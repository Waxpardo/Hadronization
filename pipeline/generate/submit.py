#!/usr/bin/env python3
"""Inventory, build, reserve, submit, or execute nominal generation work."""

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime as runtime_contract  # noqa: E402


MAX_CPU_SECONDS = 3600
MAX_WALL_SECONDS = 14400
REQUEST_MEMORY = "4GB"
REQUEST_DISK = "4GB"
HANG_GUARD_MARKER = "HF_HANG_GUARD"
EVIDENCE_STATES = {"reserved", "submitted", "validated", "held", "failed", "accepted"}
RESERVATION_SCHEMA = "hf_attempt_reservation_v1"
OUTCOME_SCHEMA = "hf_attempt_outcome_v1"
RECEIPT_SCHEMA = "hf_raw_validation_receipt_v5"


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def digest_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def fsync_directory(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    failure = None
    try:
        os.fsync(descriptor)
    except BaseException as error:
        failure = error
    try:
        os.close(descriptor)
    except BaseException as error:
        if failure is not None:
            raise RuntimeError(
                "directory fsync and close both failed: {}; {}".format(
                    failure, error)) from failure
        raise
    if failure is not None:
        raise failure


def atomic_json(path, payload, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temporary = None
    created_exclusive = False
    replaced = False
    try:
        if exclusive:
            descriptor = os.open(
                str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            created_exclusive = True
        else:
            temporary = path.with_name(".{}.{}.tmp".format(path.name, os.getpid()))
            descriptor = os.open(
                str(temporary), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if temporary is not None:
            os.replace(str(temporary), str(path))
            replaced = True
        fsync_directory(path.parent)
    except BaseException as operation_error:
        cleanup_target = None
        if exclusive and created_exclusive:
            cleanup_target = path
        elif temporary is not None and not replaced:
            cleanup_target = temporary
        cleanup_failures = []
        removed = False
        if cleanup_target is not None and os.path.lexists(str(cleanup_target)):
            try:
                cleanup_target.unlink()
                removed = True
            except BaseException as cleanup_error:
                cleanup_failures.append("unlink {}: {}".format(
                    cleanup_target, cleanup_error))
        if removed:
            try:
                fsync_directory(path.parent)
            except BaseException as cleanup_error:
                cleanup_failures.append("parent durability: {}".format(
                    cleanup_error))
        if cleanup_failures:
            raise RuntimeError(
                "atomic JSON cleanup failed after {}: {}".format(
                    operation_error, "; ".join(cleanup_failures))) from operation_error
        raise


def validate_campaign_tunes(campaign, tune_rows):
    tune_order = [row.get("name") for row in tune_rows]
    if tune_order != campaign.get("tune_order"):
        raise ValueError("study and campaign tune order differ")
    expected_ordinals = {name: index for index, name in enumerate(tune_order)}
    if campaign.get("seed", {}).get("tune_ordinals") != expected_ordinals:
        raise ValueError("campaign tune ordinal map is not bijective with study tune order")
    if len({row.get("id") for row in tune_rows}) != len(tune_rows):
        raise ValueError("study tune worker IDs are not unique")


def campaign_inputs():
    campaign = load_json(ROOT / "data/campaign.json")
    study = load_json(ROOT / "config/study.json")
    if study.get("schema") != "hadronization_study_v1":
        raise ValueError("unsupported study schema")
    scope = study.get("scope", {})
    if scope.get("variation_selection") is not False:
        raise ValueError("nominal study must make variation selection impossible")
    if scope.get("systematic_uncertainty") != "disabled_and_absent":
        raise ValueError("nominal study must exclude systematic uncertainty")
    if campaign.get("systematic_uncertainties") != "disabled":
        raise ValueError("campaign does not declare systematic uncertainty disabled")
    tune_rows = study.get("tunes", [])
    validate_campaign_tunes(campaign, tune_rows)
    return campaign, study, tune_rows


def seed_for(campaign, tune, logical_id, attempt):
    seed = campaign["seed"]
    value = (100000001 + int(seed["campaign_ordinal"]) * 10000000
             + int(seed["tune_ordinals"][tune]) * 1000000
             + attempt * 100000 + logical_id)
    low, high = seed["attempt_domain"]
    if not low <= attempt <= high or not 1 <= value <= 900000000:
        raise ValueError("derived attempt or seed is outside the campaign domain")
    return value


def materialized_card(card, events):
    text = card.read_text(encoding="utf-8")
    updated, count = re.subn(
        r"(?m)^(\s*Main:numberOfEvents\s*=\s*)[0-9]+(\s*)$",
        r"\g<1>{}\g<2>".format(events), text)
    if count != 1:
        raise ValueError("{} does not define Main:numberOfEvents exactly once".format(card))
    return updated.encode("utf-8")


def accepted_manifest(path):
    rows = []
    if not path.is_file():
        return rows
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        row = json.loads(line)
        canonical = json.dumps(row, sort_keys=True, separators=(",", ":"))
        if line != canonical:
            raise ValueError("raw manifest line {} is not canonical JSON".format(number))
        rows.append(row)
    return rows


def attempt_rows(path):
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def storage_key(tune, logical_id):
    return "{}/hf_{}_job{:03d}.root".format(tune, tune, logical_id)


def evidence_directory(work_root, tune, logical_id, attempt):
    return (work_root / "evidence" / tune / "job{:03d}".format(logical_id) /
            "attempt{:02d}".format(attempt))


def require_exact_keys(payload, required, optional, label):
    keys = set(payload)
    missing = set(required) - keys
    extra = keys - set(required) - set(optional)
    if missing or extra:
        raise ValueError("{} schema keys differ: missing={} extra={}".format(
            label, sorted(missing), sorted(extra)))


def attempt_identity(payload):
    return (payload["tune"], int(payload["logical_id"]), int(payload["attempt"]))


def validate_receipt(path, reservation, campaign):
    receipt = load_json(path)
    required = {
        "schema", "state", "campaign", "tune", "logical_id", "attempt", "seed",
        "successful_events", "card_sha256", "effective_card_sha256",
        "study_definition_sha256", "producer_sha256", "validator_sha256",
        "repository_commit", "output_bytes", "output_sha256", "target",
    }
    require_exact_keys(receipt, required, set(), "validation receipt")
    if receipt["schema"] != RECEIPT_SCHEMA or receipt["state"] != "PASS":
        raise ValueError("validation receipt schema/state mismatch")
    identity_fields = ("campaign", "tune", "logical_id", "attempt", "seed")
    if any(receipt[field] != reservation[field] for field in identity_fields):
        raise ValueError("validation receipt identity/seed differs from reservation")
    if receipt["target"] != reservation["storage_key"]:
        raise ValueError("validation receipt storage key differs from reservation")
    if int(receipt["successful_events"]) != int(
            campaign["successful_events_per_logical_job"]):
        raise ValueError("validation receipt successful-event count differs from campaign")
    if int(receipt["output_bytes"]) <= 0 or not re.fullmatch(
            r"[0-9a-f]{64}", str(receipt["output_sha256"])):
        raise ValueError("validation receipt output identity is malformed")
    return receipt


def evidence_records(work_root, campaign, tune_rows):
    records = {}
    base = work_root / "evidence"
    if not base.is_dir():
        return records
    tune_names = {row["name"] for row in tune_rows}
    logical_high = int(campaign["logical_jobs_per_tune"]) - 1
    attempt_low, attempt_high = [int(value) for value in campaign["seed"]["attempt_domain"]]
    reservation_required = {
        "schema", "state", "campaign", "purpose", "tune", "logical_id",
        "attempt", "seed", "storage_key", "plan_sha256", "reserved_unix_seconds",
    }
    reservation_optional = {"state_unix_seconds", "detail"}
    outcome_common = {
        "schema", "state", "campaign", "tune", "logical_id", "attempt", "seed",
        "storage_key", "finished_unix_seconds",
    }
    for path in sorted(base.glob("*/job*/attempt*/reservation.json")):
        try:
            reservation = load_json(path)
            require_exact_keys(reservation, reservation_required,
                               reservation_optional, "attempt reservation")
            key = attempt_identity(reservation)
            if key in records:
                raise ValueError("duplicate attempt evidence identity {}".format(key))
            expected_path = evidence_directory(work_root, *key) / "reservation.json"
            if path != expected_path:
                raise ValueError("reservation payload identity does not match evidence path")
            tune, logical_id, attempt = key
            if (reservation["schema"] != RESERVATION_SCHEMA or
                    reservation["campaign"] != campaign["campaign"] or
                    reservation["purpose"] != "continuation" or
                    reservation["state"] not in {"reserved", "submitted", "failed"}):
                raise ValueError("reservation schema/campaign/state contract mismatch")
            if (tune not in tune_names or not 0 <= logical_id <= logical_high or
                    not attempt_low <= attempt <= attempt_high):
                raise ValueError("attempt evidence identity is outside campaign domain")
            if (reservation["storage_key"] != storage_key(tune, logical_id) or
                    int(reservation["seed"]) != seed_for(
                        campaign, tune, logical_id, attempt)):
                raise ValueError("reservation storage key/seed differs from campaign identity")
            if not re.fullmatch(r"[0-9a-f]{64}", str(reservation["plan_sha256"])):
                raise ValueError("reservation plan digest is malformed")
            state = reservation["state"]
            outcome = path.with_name("outcome.json")
            if outcome.is_file():
                outcome_row = load_json(outcome)
                outcome_state = outcome_row.get("state")
                if outcome_state in {"held", "failed"} and outcome_row.get(
                        "stage") == "scheduler_before_worker":
                    required = outcome_common | {"stage", "reason"}
                elif outcome_state == "failed":
                    required = outcome_common | {"stage", "exit_code"}
                elif outcome_state in {"validated", "accepted"}:
                    required = outcome_common | {"receipt_sha256", "cleanup_after_days"}
                else:
                    raise ValueError("unsupported attempt evidence state {}".format(
                        outcome_state))
                require_exact_keys(outcome_row, required, set(), "attempt outcome")
                if outcome_row["schema"] != OUTCOME_SCHEMA:
                    raise ValueError("attempt outcome schema mismatch")
                for field in ("campaign", "tune", "logical_id", "attempt", "seed",
                              "storage_key"):
                    if outcome_row[field] != reservation[field]:
                        raise ValueError("outcome identity/seed differs from reservation")
                if state not in {"reserved", "submitted"}:
                    raise ValueError("outcome transition does not start from an active reservation")
                if outcome_state in {"validated", "accepted"}:
                    receipt_path = path.with_name("validation_receipt.json")
                    if not receipt_path.is_file():
                        raise ValueError("validated/accepted outcome lacks validation receipt")
                    validate_receipt(receipt_path, reservation, campaign)
                    if digest_file(receipt_path) != outcome_row["receipt_sha256"]:
                        raise ValueError("outcome receipt digest differs from durable receipt")
                state = outcome_state
            if state not in EVIDENCE_STATES:
                raise ValueError("unsupported attempt evidence state {}".format(state))
            records[key] = state
        except (KeyError, OSError, ValueError, json.JSONDecodeError) as error:
            raise ValueError("invalid attempt evidence {}: {}".format(path, error))
    return records


def inventory(campaign, tune_rows, manifest_path, attempts_path, raw_root, work_root,
              verify_accepted_sha256=False):
    expected = [(row["name"], logical_id) for row in tune_rows
                for logical_id in range(int(campaign["logical_jobs_per_tune"]))]
    manifest = accepted_manifest(manifest_path)
    accepted = {}
    for row in manifest:
        key = (row["tune"], int(row["logical_id"]))
        if key in accepted or key not in expected:
            raise ValueError("duplicate/out-of-domain accepted identity {}".format(key))
        if row["raw_storage_key"] != storage_key(*key):
            raise ValueError("accepted storage key does not match logical identity {}".format(key))
        if (int(row["bytes"]) <= 0 or
                not re.fullmatch(r"[0-9a-f]{64}", str(row["raw_sha256"]))):
            raise ValueError("accepted byte/hash identity is malformed {}".format(key))
        accepted[key] = row
    history = {}
    for row in attempt_rows(attempts_path):
        key = (row["tune"], int(row["logical_id"]), int(row["attempt"]))
        if key in history:
            raise ValueError("duplicate historical attempt {}".format(key))
        history[key] = row["outcome"]
    evidence = evidence_records(work_root, campaign, tune_rows)
    for key in evidence:
        if key in history:
            raise ValueError("work evidence reuses immutable historical attempt {}".format(key))
    statuses = {}
    errors = []
    for key in expected:
        tune, logical_id = key
        stable = raw_root / storage_key(tune, logical_id)
        if key in accepted:
            row = accepted[key]
            if os.path.lexists(str(stable)):
                if (stable.is_symlink() or not stable.is_file() or
                        stable.stat().st_size != int(row["bytes"])):
                    statuses[key] = "accepted_size_or_type_mismatch"
                    errors.append("accepted path size/type mismatch: {}".format(stable))
                elif verify_accepted_sha256:
                    actual_sha256 = digest_file(stable)
                    if actual_sha256 != row["raw_sha256"]:
                        statuses[key] = "accepted_sha256_mismatch"
                        errors.append(
                            "accepted path SHA-256 mismatch: {} expected={} actual={}".format(
                                stable, row["raw_sha256"], actual_sha256))
                    else:
                        statuses[key] = "accepted_sha256_verified"
                else:
                    statuses[key] = "accepted_size_observed_sha256_unverified"
            else:
                statuses[key] = "accepted_missing_local"
            continue
        if os.path.lexists(str(stable)):
            statuses[key] = "occupied_mismatch"
            errors.append("occupied unregistered raw path; refusing overwrite: {}".format(stable))
            continue
        states = [(attempt, state) for (candidate_tune, candidate_id, attempt), state
                  in evidence.items() if (candidate_tune, candidate_id) == key]
        statuses[key] = max(states)[1] if states else "absent"
    return {"expected": expected, "accepted": accepted, "history": history,
            "evidence": evidence, "statuses": statuses, "errors": errors}


def plan_rows(campaign, tune_rows, inventory_result, purpose):
    if purpose not in {"inventory", "continuation", "recovery", "new"}:
        raise ValueError("unknown plan purpose")
    if purpose == "new":
        raise ValueError("HF_RUN3_V1 is frozen; a new campaign requires a new declared campaign identity")
    if inventory_result["errors"]:
        raise ValueError(inventory_result["errors"][0])
    if purpose == "recovery":
        missing = [key for key, status in inventory_result["statuses"].items()
                   if status == "accepted_missing_local"]
        if missing:
            raise ValueError("recovery cannot regenerate authoritative accepted raw bytes: {}".format(missing[0]))
        return []
    if purpose == "inventory":
        return []
    events = int(campaign["successful_events_per_logical_job"])
    tune_map = {row["name"]: row for row in tune_rows}
    planned = []
    for key in inventory_result["expected"]:
        status = inventory_result["statuses"][key]
        if status.startswith("accepted_"):
            continue
        if status in {"reserved", "submitted", "validated"}:
            continue
        if status not in {"absent", "failed", "held"}:
            raise ValueError("identity is not continuation-safe: {} status={}".format(key, status))
        tune, logical_id = key
        ordinals = [attempt for candidate_tune, candidate_id, attempt in
                    list(inventory_result["history"]) + list(inventory_result["evidence"])
                    if (candidate_tune, candidate_id) == key]
        attempt = max(ordinals, default=-1) + 1
        card = ROOT / tune_map[tune]["card"]
        planned.append({
            "tune": tune, "logical_id": logical_id, "attempt": attempt,
            "seed": seed_for(campaign, tune, logical_id, attempt),
            "block": logical_id % int(campaign["blocks"]["count"]) + 1,
            "storage_key": storage_key(tune, logical_id),
            "card_sha256": digest_file(card),
            "effective_card_sha256": digest_bytes(materialized_card(card, events)),
        })
    return planned


def command_flags(command, arguments, environment):
    result = subprocess.run([command] + list(arguments), text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=environment)
    if result.returncode:
        raise RuntimeError("{} failed: {}".format(command, result.stderr.strip()))
    return shlex.split(result.stdout.strip())


def compile_validator(runtime, output):
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    cxx = environment["CXX"]
    root_config = environment["ROOT_CONFIG"]
    flags = command_flags(root_config, ["--cflags"], environment)
    libraries = command_flags(root_config, ["--libs"], environment)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = ([cxx, "-O2", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic",
                str(ROOT / "pipeline/generate/validate_raw.cpp"),
                "-I" + str(ROOT / "pipeline/generate")] + flags + libraries +
               ["-o", str(output)])
    subprocess.run(command, env=environment, check=True)
    return command


def compile_producer(runtime, output):
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    cxx = environment["CXX"]
    root_config = environment["ROOT_CONFIG"]
    pythia_config = environment["PYTHIA8_CONFIG"]
    root_flags = command_flags(root_config, ["--cflags"], environment)
    root_libdir = command_flags(root_config, ["--libdir"], environment)
    root_aux = command_flags(root_config, ["--auxlibs"], environment)
    pythia_flags = command_flags(pythia_config, ["--cxxflags"], environment)
    pythia_libs = command_flags(pythia_config, ["--libs"], environment)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = ([cxx, "-O2", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic",
                str(ROOT / "pipeline/generate/producer.cpp"),
                "-I" + str(ROOT / "pipeline/generate")] + root_flags + pythia_flags +
               ["-L" + root_libdir[0], "-lTree", "-lHist", "-lRIO", "-lCore"] +
               root_aux + pythia_libs + ["-o", str(output)])
    subprocess.run(command, env=environment, check=True)
    return command


def generated_contract_check(python):
    result = subprocess.run([python, str(ROOT / "pipeline/generate/study_contract.py"),
                             "check"], cwd=str(ROOT))
    if result.returncode:
        raise RuntimeError("generated study contract check failed")


def build(component, producer, validator):
    root_required = component in {"validator", "producer", "all"}
    pythia_required = component in {"producer", "all"}
    runtime = runtime_contract.resolve(require_root=root_required,
                                       require_pythia=pythia_required)
    generated_contract_check(runtime["environment"]["PYTHON"])
    commands = []
    if component in {"validator", "all"}:
        commands.append(("validator", validator, compile_validator(runtime, validator)))
    if component in {"producer", "all"}:
        commands.append(("producer", producer, compile_producer(runtime, producer)))
    return commands


def condor_path(path, label):
    if not re.fullmatch(r"[A-Za-z0-9_./:@+-]+", str(path)):
        raise ValueError("{} contains unsupported Condor characters: {}".format(label, path))
    return str(path)


def render_submit(campaign, study, rows, runtime, producer, validator,
                  raw_root, work_root, purpose):
    commit = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    producer_sha = digest_file(producer) if producer.is_file() else "UNBUILT"
    validator_sha = digest_file(validator) if validator.is_file() else "UNBUILT"
    python = runtime["environment"]["PYTHON"]
    worker = ROOT / "pipeline/generate/submit.py"
    for path, label in ((python, "python"), (worker, "worker"), (raw_root, "raw root"),
                        (work_root, "work root"), (producer, "producer"),
                        (validator, "validator")):
        condor_path(path, label)
    arguments = (
        "{} worker --tune $(tune) --logical-id $(logical_id) --attempt $(attempt) "
        "--seed $(seed) --card-sha256 $(card_sha256) "
        "--effective-card-sha256 $(effective_card_sha256) --producer-sha256 {} "
        "--validator-sha256 {} --repository-commit {} --raw-root {} --work-root {} "
        "--producer-path {} --validator-path {}"
    ).format(worker, producer_sha, validator_sha, commit, raw_root, work_root,
             producer, validator)
    lines = [
        "# deterministic nominal generation plan",
        "# campaign={} purpose={} study_sha256={}".format(
            campaign["campaign"], purpose, digest_file(ROOT / "config/study.json")),
        "universe = vanilla", "executable = {}".format(python),
        "arguments = {}".format(arguments), "getenv = False",
        "initialdir = {}".format(ROOT), "should_transfer_files = NO",
        "log = {}/condor/$(tune)-$(logical_id)-$(attempt).log".format(work_root),
        "output = {}/condor/$(tune)-$(logical_id)-$(attempt).out".format(work_root),
        "error = {}/condor/$(tune)-$(logical_id)-$(attempt).err".format(work_root),
        "request_cpus = 1", "request_memory = {}".format(REQUEST_MEMORY),
        "request_disk = {}".format(REQUEST_DISK), '+UseOS = "el9"',
        "hold = True", "max_retries = 0",
        "on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)",
        ("periodic_hold = (JobStatus == 2) && ((RemoteUserCpu > {}) || "
         "((CurrentTime - EnteredCurrentStatus) > {}))").format(
             MAX_CPU_SECONDS, MAX_WALL_SECONDS),
        ('periodic_hold_reason = "{} suspected generator hang: cpu>{}s or '
         'wall>{}s"').format(HANG_GUARD_MARKER, MAX_CPU_SECONDS, MAX_WALL_SECONDS),
        '+HFCampaign = "{}"'.format(campaign["campaign"]),
        '+HFPlanPurpose = "{}"'.format(purpose),
        "queue tune,logical_id,attempt,seed,block,storage_key,card_sha256,effective_card_sha256 from (",
    ]
    for row in rows:
        lines.append("{tune} {logical_id} {attempt} {seed} {block} {storage_key} "
                     "{card_sha256} {effective_card_sha256}".format(**row))
    lines.extend([")", ""])
    rendered = "\n".join(lines).encode("utf-8")
    validate_submit_contract(rendered)
    validate_submit_executable_contract(rendered, producer, validator)
    return rendered


def validate_submit_contract(rendered):
    text = rendered.decode("utf-8") if isinstance(rendered, bytes) else rendered
    required = {
        "scrubbed environment": "getenv = False",
        "CPU hold": "RemoteUserCpu > {}".format(MAX_CPU_SECONDS),
        "wall hold": "CurrentTime - EnteredCurrentStatus) > {}".format(MAX_WALL_SECONDS),
        "hold reason": "periodic_hold_reason = \"{}".format(HANG_GUARD_MARKER),
        "exit hold": "on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)",
        "zero retry": "max_retries = 0",
        "memory": "request_memory = {}".format(REQUEST_MEMORY),
        "disk": "request_disk = {}".format(REQUEST_DISK),
        "runtime compatibility": '+UseOS = "el9"',
    }
    for label, clause in required.items():
        if clause not in text:
            raise ValueError("Condor safety contract missing {}".format(label))
    if "--systematics" in text or "card_variant" in text:
        raise ValueError("Condor plan exposes a retired variation selector")
    return True


def validate_submit_executable_contract(rendered, producer, validator):
    text = rendered.decode("utf-8") if isinstance(rendered, bytes) else rendered
    expected = ("--producer-path {}".format(producer),
                "--validator-path {}".format(validator))
    if any(token not in text for token in expected):
        raise ValueError("Condor plan/worker executable-path contract disagrees")
    return True


def submission_filesystem_preflight(work_root, producer, validator):
    for path, label in ((producer, "producer"), (validator, "validator")):
        if path.is_symlink() or not path.is_file() or not os.access(str(path), os.X_OK):
            raise RuntimeError("submission {} executable path is not a regular executable: {}".format(
                label, path))
    condor = work_root / "condor"
    condor.mkdir(parents=True, mode=0o700, exist_ok=True)
    if condor.is_symlink() or not condor.is_dir() or not os.access(str(condor), os.W_OK):
        raise RuntimeError("Condor output directory is not a writable regular directory: {}".format(
            condor))
    return condor


def reserve_rows(campaign, rows, work_root, plan_sha):
    if not re.fullmatch(r"[0-9a-f]{64}", str(plan_sha)):
        raise ValueError("reservation plan SHA-256 is malformed")
    reservations = []
    now = int(time.time())
    destinations = []
    identities = set()
    for row in rows:
        key = (row["tune"], int(row["logical_id"]), int(row["attempt"]))
        if key in identities:
            raise ValueError("duplicate reservation batch identity {}".format(key))
        identities.add(key)
        if (row["storage_key"] != storage_key(row["tune"], row["logical_id"]) or
                int(row["seed"]) != seed_for(
                    campaign, row["tune"], int(row["logical_id"]),
                    int(row["attempt"]))):
            raise ValueError("reservation batch identity/seed/storage mismatch {}".format(key))
        directory = evidence_directory(work_root, row["tune"], row["logical_id"], row["attempt"])
        reservation = directory / "reservation.json"
        if os.path.lexists(str(reservation)):
            raise FileExistsError("reservation destination collision: {}".format(reservation))
        if os.path.lexists(str(directory)) and (directory.is_symlink() or not directory.is_dir()):
            raise FileExistsError("reservation directory is occupied: {}".format(directory))
        payload = {
            "schema": RESERVATION_SCHEMA, "state": "reserved",
            "campaign": campaign["campaign"], "purpose": "continuation",
            "tune": row["tune"], "logical_id": row["logical_id"],
            "attempt": row["attempt"], "seed": row["seed"],
            "storage_key": row["storage_key"], "plan_sha256": plan_sha,
            "reserved_unix_seconds": now,
        }
        destinations.append((reservation, payload))
    try:
        for reservation, payload in destinations:
            atomic_json(reservation, payload, exclusive=True)
            reservations.append((reservation, payload))
    except Exception:
        cleanup_failures = []
        for reservation, unused in reversed(reservations):
            try:
                reservation.unlink()
            except OSError as error:
                cleanup_failures.append("{}: {}".format(reservation, error))
        if cleanup_failures:
            raise RuntimeError("reservation batch rollback failed: {}".format(
                "; ".join(cleanup_failures)))
        raise
    return reservations


def mark_reservations(reservations, state, detail=None):
    for path, payload in reservations:
        updated = dict(payload)
        updated["state"] = state
        updated["state_unix_seconds"] = int(time.time())
        if detail:
            updated["detail"] = detail
        atomic_json(path, updated)


def record_preworker_outcome(args, work_root, campaign, tune_rows):
    """Persist an operator-observed scheduler outcome for a worker that never ran."""
    directory = evidence_directory(work_root, args.tune, args.logical_id, args.attempt)
    reservation_path = directory / "reservation.json"
    if not reservation_path.is_file():
        raise RuntimeError("cannot record outcome without a durable reservation")
    evidence_records(work_root, campaign, tune_rows)
    reservation = load_json(reservation_path)
    identity = (reservation.get("tune"), reservation.get("logical_id"),
                reservation.get("attempt"))
    if identity != (args.tune, args.logical_id, args.attempt):
        raise RuntimeError("reservation identity does not match recorded outcome")
    if reservation.get("state") not in {"reserved", "submitted"}:
        raise RuntimeError("reservation is not awaiting a pre-worker outcome")
    atomic_json(directory / "outcome.json", {
        "schema": OUTCOME_SCHEMA, "state": args.state,
        "stage": "scheduler_before_worker", "reason": args.reason,
        "campaign": reservation["campaign"],
        "tune": args.tune, "logical_id": args.logical_id,
        "attempt": args.attempt, "seed": reservation.get("seed"),
        "storage_key": reservation["storage_key"],
        "finished_unix_seconds": int(time.time()),
    }, exclusive=True)
    return directory / "outcome.json"


def validator_command(validator, partial, campaign, args):
    return [str(validator), str(partial), "--campaign", campaign["campaign"],
            "--tune", args.tune, "--campaign-ordinal",
            str(campaign["seed"]["campaign_ordinal"]), "--logical-id",
            str(args.logical_id), "--attempt", str(args.attempt), "--seed",
            str(args.seed), "--events",
            str(campaign["successful_events_per_logical_job"]), "--pthat-min",
            str(campaign["physics"]["pthat_min_gev"]), "--config-sha256",
            args.effective_card_sha256, "--executable-sha256",
            args.producer_sha256, "--repository-commit", args.repository_commit,
            "--pythia-version", campaign["runtime"]["pythia_version"]]


def promote_no_overwrite(partial, stable, expected_sha):
    stable.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(str(stable)):
        raise RuntimeError("stable output already exists; refusing overwrite: {}".format(stable))
    staging = stable.parent / ".{}.{}.staging".format(stable.name, os.getpid())
    descriptor = os.open(str(staging), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with partial.open("rb") as source, os.fdopen(descriptor, "wb", closefd=False) as target:
            shutil.copyfileobj(source, target, 1024 * 1024)
            target.flush()
            os.fsync(target.fileno())
        os.close(descriptor)
        descriptor = -1
        if digest_file(staging) != expected_sha:
            raise RuntimeError("promotion staging digest mismatch")
        os.link(str(staging), str(stable))
        directory = os.open(str(stable.parent), os.O_RDONLY)
        try:
            os.fsync(directory)
        except OSError:
            stable.unlink()
            raise
        finally:
            os.close(directory)
        try:
            staging.unlink()
        except OSError as error:
            print("WARNING canonical exposure committed; staging cleanup failed: {}".format(error),
                  file=sys.stderr)
            return
    except Exception:
        if descriptor >= 0:
            os.close(descriptor)
        if os.path.lexists(str(staging)):
            staging.unlink()
        raise


def commit_validated_output(partial, stable, receipt_path, outcome_path, receipt):
    """Durably record PASS before exposing a no-overwrite canonical path."""
    atomic_json(receipt_path, receipt, exclusive=True)
    receipt_sha = digest_file(receipt_path)
    outcome_identity = {
        "campaign": receipt["campaign"], "tune": receipt["tune"],
        "logical_id": receipt["logical_id"], "attempt": receipt["attempt"],
        "seed": receipt["seed"], "storage_key": receipt["target"],
    }
    atomic_json(outcome_path, dict(outcome_identity, **{
        "schema": OUTCOME_SCHEMA, "state": "validated",
        "receipt_sha256": receipt_sha,
        "finished_unix_seconds": int(time.time()), "cleanup_after_days": 7}),
        exclusive=True)
    promote_no_overwrite(partial, stable, receipt["output_sha256"])
    try:
        atomic_json(outcome_path, dict(outcome_identity, **{
            "schema": OUTCOME_SCHEMA, "state": "accepted",
            "receipt_sha256": receipt_sha,
            "finished_unix_seconds": int(time.time()), "cleanup_after_days": 7}))
    except OSError as error:
        print("WARNING promoted output has a durable validated receipt but outcome update failed: {}".format(error),
              file=sys.stderr)


def worker(args):
    campaign, study, tune_rows = campaign_inputs()
    tune_map = {row["name"]: row for row in tune_rows}
    if args.tune not in tune_map or not 0 <= args.logical_id < int(campaign["logical_jobs_per_tune"]):
        raise ValueError("invalid tune or logical ID")
    if seed_for(campaign, args.tune, args.logical_id, args.attempt) != args.seed:
        raise ValueError("seed does not match the campaign formula")
    actual_commit = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    if actual_commit != args.repository_commit:
        raise RuntimeError("checkout moved after the plan was rendered")
    if subprocess.check_output(
            ["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=normal"],
            text=True):
        raise RuntimeError("worker refuses a checkout with tracked or untracked changes")
    resolved = runtime_contract.resolve(require_root=True, require_pythia=True)
    environment = {key: value for key, value in os.environ.items()
                   if key != "HADRONIZATION_DATASET" and not key.startswith("HADRONIZATION_")}
    environment.update(resolved["environment"])
    work_root = Path(args.work_root).resolve()
    raw_root = Path(args.raw_root).resolve()
    producer = Path(args.producer_path).resolve()
    validator = Path(args.validator_path).resolve()
    if not producer.is_file() or digest_file(producer) != args.producer_sha256:
        raise RuntimeError("producer executable digest mismatch")
    if not validator.is_file() or digest_file(validator) != args.validator_sha256:
        raise RuntimeError("validator executable digest mismatch")
    card = ROOT / tune_map[args.tune]["card"]
    if digest_file(card) != args.card_sha256:
        raise RuntimeError("tune-card digest mismatch")
    effective = materialized_card(card, int(campaign["successful_events_per_logical_job"]))
    if digest_bytes(effective) != args.effective_card_sha256:
        raise RuntimeError("materialized tune-card digest mismatch")
    directory = evidence_directory(work_root, args.tune, args.logical_id, args.attempt)
    reservation = directory / "reservation.json"
    if not reservation.is_file():
        raise RuntimeError("worker lacks durable attempt reservation")
    current_evidence = evidence_records(work_root, campaign, tune_rows)
    if current_evidence.get((args.tune, args.logical_id, args.attempt)) not in {
            "reserved", "submitted"}:
        raise RuntimeError("attempt evidence already has a terminal outcome")
    reserved = load_json(reservation)
    if (reserved.get("state") not in {"reserved", "submitted"} or
            (reserved.get("seed"), reserved.get("storage_key")) !=
            (args.seed, storage_key(args.tune, args.logical_id))):
        raise RuntimeError("attempt reservation identity/state mismatch")
    scratch = directory / "scratch"
    scratch.mkdir(parents=True, mode=0o700, exist_ok=False)
    partial = scratch / "partial.root"
    (scratch / Path(tune_map[args.tune]["card"]).name).write_bytes(effective)
    environment.update({
        "HADRONIZATION_CONFIG_SHA256": args.effective_card_sha256,
        "HADRONIZATION_EXECUTABLE_SHA256": args.producer_sha256,
        "HADRONIZATION_REPOSITORY_COMMIT": args.repository_commit,
        "HADRONIZATION_REPOSITORY_DIRTY": "false",
    })
    command = [str(producer), tune_map[args.tune]["id"], str(partial), str(args.seed),
               campaign["campaign"], str(campaign["seed"]["campaign_ordinal"]),
               str(args.logical_id), "primary", str(args.attempt)]
    result = subprocess.run(command, cwd=str(scratch), env=environment)
    if result.returncode:
        atomic_json(directory / "outcome.json", {
            "schema": OUTCOME_SCHEMA, "state": "failed",
            "campaign": campaign["campaign"], "tune": args.tune,
            "logical_id": args.logical_id, "attempt": args.attempt,
            "seed": args.seed, "storage_key": storage_key(args.tune, args.logical_id),
            "stage": "producer", "exit_code": result.returncode,
            "finished_unix_seconds": int(time.time())}, exclusive=True)
        raise RuntimeError("producer exited {}; partial retained".format(result.returncode))
    validation = subprocess.run(
        validator_command(validator, partial, campaign, args),
        cwd=str(scratch), env=environment, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if validation.returncode:
        (directory / "validator.log").write_text(validation.stdout, encoding="utf-8")
        atomic_json(directory / "outcome.json", {
            "schema": OUTCOME_SCHEMA, "state": "failed",
            "campaign": campaign["campaign"], "tune": args.tune,
            "logical_id": args.logical_id, "attempt": args.attempt,
            "seed": args.seed, "storage_key": storage_key(args.tune, args.logical_id),
            "stage": "validation", "exit_code": validation.returncode,
            "finished_unix_seconds": int(time.time())}, exclusive=True)
        raise RuntimeError("raw validator rejected partial; evidence retained")
    output_sha = digest_file(partial)
    stable = raw_root / storage_key(args.tune, args.logical_id)
    receipt = {
        "schema": RECEIPT_SCHEMA, "state": "PASS",
        "campaign": campaign["campaign"], "tune": args.tune,
        "logical_id": args.logical_id, "attempt": args.attempt, "seed": args.seed,
        "successful_events": int(campaign["successful_events_per_logical_job"]),
        "card_sha256": args.card_sha256,
        "effective_card_sha256": args.effective_card_sha256,
        "study_definition_sha256": digest_file(ROOT / "config/study.json"),
        "producer_sha256": args.producer_sha256,
        "validator_sha256": args.validator_sha256,
        "repository_commit": args.repository_commit,
        "output_bytes": partial.stat().st_size, "output_sha256": output_sha,
        "target": storage_key(args.tune, args.logical_id),
    }
    commit_validated_output(partial, stable, directory / "validation_receipt.json",
                            directory / "outcome.json", receipt)
    print("PROMOTED {} receipt={}".format(stable, directory / "validation_receipt.json"))


def parser():
    top = argparse.ArgumentParser(description=__doc__)
    sub = top.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--purpose", choices=("inventory", "continuation", "recovery", "new"),
                      default="inventory")
    plan.add_argument("--output", type=Path)
    plan.add_argument("--submit", action="store_true")
    plan.add_argument("--build", action="store_true")
    plan.add_argument("--producer", type=Path)
    plan.add_argument("--validator", type=Path)
    plan.add_argument("--raw-root", type=Path)
    plan.add_argument("--work-root", type=Path)
    plan.add_argument("--raw-manifest", type=Path)
    plan.add_argument("--attempts", type=Path)
    plan.add_argument("--verify-accepted-sha256", action="store_true",
                      help="hash locally present accepted raw bytes against the manifest")
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--component", choices=("validator", "producer", "all"),
                              default="all")
    build_parser.add_argument("--producer", type=Path)
    build_parser.add_argument("--validator", type=Path)
    run = sub.add_parser("worker")
    run.add_argument("--tune", required=True)
    run.add_argument("--logical-id", type=int, required=True)
    run.add_argument("--attempt", type=int, required=True)
    run.add_argument("--seed", type=int, required=True)
    run.add_argument("--card-sha256", required=True)
    run.add_argument("--effective-card-sha256", required=True)
    run.add_argument("--producer-sha256", required=True)
    run.add_argument("--validator-sha256", required=True)
    run.add_argument("--repository-commit", required=True)
    run.add_argument("--raw-root", required=True)
    run.add_argument("--work-root", required=True)
    run.add_argument("--producer-path", required=True)
    run.add_argument("--validator-path", required=True)
    outcome = sub.add_parser(
        "record-outcome",
        help="record a held/failed scheduler outcome when the worker never ran")
    outcome.add_argument("--tune", required=True)
    outcome.add_argument("--logical-id", type=int, required=True)
    outcome.add_argument("--attempt", type=int, required=True)
    outcome.add_argument("--state", choices=("held", "failed"), required=True)
    outcome.add_argument("--reason", required=True)
    outcome.add_argument("--work-root", type=Path)
    return top


def main():
    args = parser().parse_args()
    try:
        values = runtime_contract.site_values()
        work_root = (args.work_root if getattr(args, "work_root", None) else
                     runtime_contract.repository_path(values.get("WORK_ROOT"), ROOT / "data/work")).resolve()
        producer = (getattr(args, "producer", None) or work_root / "bin/producer").resolve()
        validator = (getattr(args, "validator", None) or work_root / "bin/validate_raw").resolve()
        if args.command == "worker":
            worker(args)
            return 0
        if args.command == "record-outcome":
            campaign, unused_study, tune_rows = campaign_inputs()
            path = record_preworker_outcome(args, work_root, campaign, tune_rows)
            print("RECORDED_OUTCOME={}".format(path))
            return 0
        if args.command == "build":
            for name, output, command in build(args.component, producer, validator):
                print("BUILT {} {}".format(name, output))
                print("BUILD_COMMAND {}".format(" ".join(shlex.quote(item) for item in command)))
            return 0
        campaign, study, tune_rows = campaign_inputs()
        generated_contract_check(sys.executable)
        raw_root = (args.raw_root or runtime_contract.repository_path(
            values.get("RAW_ROOT"), ROOT / "data/raw")).resolve()
        manifest_path = (args.raw_manifest or ROOT / "data/raw_manifest.jsonl").resolve()
        attempts_path = (args.attempts or ROOT / "data/attempts.csv").resolve()
        measured = inventory(campaign, tune_rows, manifest_path, attempts_path,
                             raw_root, work_root, args.verify_accepted_sha256)
        rows = plan_rows(campaign, tune_rows, measured, args.purpose)
        counts = {}
        for status in measured["statuses"].values():
            counts[status] = counts.get(status, 0) + 1
        print("INVENTORY campaign={} purpose={} jobs={} {}".format(
            campaign["campaign"], args.purpose, len(rows),
            " ".join("{}={}".format(key, counts[key]) for key in sorted(counts))))
        if args.submit and args.purpose != "continuation":
            raise RuntimeError("--submit requires --purpose continuation")
        if (args.build or args.submit) and rows:
            build("all", producer, validator)
        runtime = runtime_contract.resolve(require_root=False, require_pythia=False)
        rendered = render_submit(campaign, study, rows, runtime, producer, validator,
                                 raw_root, work_root, args.purpose)
        plan_sha = digest_bytes(rendered)
        print("PLAN_SHA256={}".format(plan_sha))
        if args.submit and not rows:
            print("NO_WORK accepted campaign has no continuation jobs; scheduler not contacted")
            return 0
        destination = args.output
        if args.submit and destination is None:
            destination = work_root / "plans/{}.sub".format(plan_sha)
        if destination is not None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(rendered)
            print("PLAN_FILE={}".format(destination))
        if args.submit:
            if not (ROOT / "config/site.conf").is_file():
                raise RuntimeError("--submit requires configured config/site.conf")
            submit_command = values.get("SCHEDULER_SUBMIT")
            if not submit_command:
                raise RuntimeError("--submit requires SCHEDULER_SUBMIT in config/site.conf")
            if not producer.is_file() or not validator.is_file():
                raise RuntimeError("--submit requires built producer and validator")
            submission_filesystem_preflight(work_root, producer, validator)
            reservations = reserve_rows(campaign, rows, work_root, plan_sha)
            result = subprocess.run(shlex.split(submit_command) + [str(destination)])
            if result.returncode:
                mark_reservations(reservations, "failed",
                                  "scheduler submission exited {}".format(result.returncode))
                raise RuntimeError("scheduler submit exited {}".format(result.returncode))
            mark_reservations(reservations, "submitted")
            print("SUBMITTED jobs={} plan={}".format(len(rows), destination))
        return 0
    except (KeyError, OSError, RuntimeError, ValueError, json.JSONDecodeError,
            subprocess.CalledProcessError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
