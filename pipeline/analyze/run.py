#!/usr/bin/env python3
"""Plan, produce, verify, and explain lossless ROOT analysis shards."""

import argparse
import concurrent.futures
import csv
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline/generate"))
import runtime as runtime_contract


PLAN_SCHEMA = "hadronization_analysis_shard_plan_v1"
RECEIPT_SCHEMA = "hadronization_analysis_shard_receipt_v1"
WORKER_SCHEMA = "hadronization_lossless_analysis_v1"
SCHEMA_DIGEST = "3a83a7550c27c3f59989b84eea0204bce45bd9c401744f321758e56f3bf422c9"
REGISTRIES_DIGEST = "5462be4f9fed821f6a0c09cda4b461343d1720112f8c76a3afd14ce8130895f3"
RAW_MAPPING_DIGEST = "bdd6846d981d27b8efe02e8538c6fd43884c4bed6ae3bfbf2439610afd2f7898"
ANALYSIS_SOURCE = ROOT / "pipeline/analyze/analyze.cpp"
RAW_VALIDATOR_SOURCE = ROOT / "pipeline/generate/validate_raw.cpp"
TABLES = (
    "ancestry", "ancestry_mothers", "closure", "constituents",
    "event_compatibility", "event_ranges", "events", "hard", "heavy",
    "heavy_mothers", "origins", "pairs", "source_blocks", "source_counts",
    "sources", "triggers",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_file(path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path, value, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | (os.O_EXCL if exclusive else os.O_TRUNC)
    descriptor = os.open(str(path), flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(canonical(value) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def is_within(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def reject_symlink_components(path, label):
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ValueError("{} contains symlink component: {}".format(label, current))
        if not current.exists():
            break


def safe_roots(raw_root, work_root, output_root):
    for path, label in ((raw_root, "raw root"), (work_root, "work root"),
                        (output_root, "output root")):
        reject_symlink_components(path, label)
    raw = raw_root.resolve(strict=False)
    work = work_root.resolve(strict=False)
    output = output_root.resolve(strict=False)
    if raw == work or raw == output or is_within(work, raw) or is_within(output, raw):
        raise ValueError("work/output roots must not be inside the protected raw root")
    if is_within(raw, work) or is_within(raw, output):
        raise ValueError("protected raw root must not be inside work/output roots")
    if work == output or is_within(work, output) or is_within(output, work):
        raise ValueError("work and output roots must not overlap")
    return raw, work, output


def safe_child(root, child, label, must_exist=False):
    root = root.resolve(strict=False)
    reject_symlink_components(child, label)
    resolved = child.resolve(strict=must_exist)
    if not is_within(resolved, root):
        raise ValueError("{} resolves outside its declared root: {}".format(label, child))
    return resolved


def regular_file(path, label):
    try:
        mode = path.lstat().st_mode
    except OSError as error:
        raise ValueError("{} is unavailable: {}".format(label, path)) from error
    if not stat.S_ISREG(mode) or path.is_symlink():
        raise ValueError("{} is not a regular non-symlink file: {}".format(label, path))


def exact_keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError("{} has an unsupported or missing field set".format(label))


MANIFEST_FIELDS = {
    "accepted_attempt", "accepted_seed", "block", "bytes", "logical_id",
    "raw_sha256", "raw_storage_key", "successful_events", "tune",
    "validation_log_sha256", "validation_receipt_sha256",
}


def load_manifest(path, campaign):
    regular_file(path, "manifest")
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError("manifest line {} is invalid JSON".format(number)) from error
        exact_keys(row, MANIFEST_FIELDS, "manifest line {}".format(number))
        for key in ("logical_id", "accepted_attempt", "accepted_seed", "block",
                    "bytes", "successful_events"):
            if type(row[key]) is not int or row[key] < 0:
                raise ValueError("manifest {} is not a nonnegative integer".format(key))
        if row["bytes"] <= 0 or row["successful_events"] <= 0:
            raise ValueError("manifest size/event exposure must be positive")
        if row["block"] != (row["logical_id"] % 10) + 1:
            raise ValueError("manifest source block does not match the accepted +1 rule")
        if row["tune"] not in campaign["tune_order"]:
            raise ValueError("manifest contains an unknown tune")
        for key in ("raw_sha256", "validation_log_sha256",
                    "validation_receipt_sha256"):
            if (not isinstance(row[key], str) or len(row[key]) != 64 or
                    any(character not in "0123456789abcdef" for character in row[key])):
                raise ValueError("manifest {} is not lowercase SHA-256".format(key))
        storage = PurePosixPath(row["raw_storage_key"])
        if (not isinstance(row["raw_storage_key"], str) or storage.is_absolute() or
                not storage.parts or any(part in {"", ".", ".."} for part in storage.parts)):
            raise ValueError("manifest raw_storage_key is not a portable relative key")
        rows.append(row)
    tune_index = {name: index for index, name in enumerate(campaign["tune_order"])}
    ordered = sorted(rows, key=lambda row: (
        tune_index[row["tune"]], row["logical_id"], row["accepted_attempt"],
        row["raw_storage_key"]))
    if rows != ordered:
        raise ValueError("manifest is not in canonical source order")
    identities = [(row["tune"], row["logical_id"], row["accepted_attempt"])
                  for row in rows]
    if len(set(identities)) != len(identities):
        raise ValueError("manifest repeats a scientific source identity")
    return rows


def load_attempts(path):
    regular_file(path, "attempt ledger")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expected = ["tune", "logical_id", "attempt", "seed", "outcome",
                    "evidence_status", "raw_storage_key"]
        if reader.fieldnames != expected:
            raise ValueError("attempt ledger field contract differs")
        rows = list(reader)
    return rows, sha_file(path)


def verify_attempt(row, attempts):
    matches = [item for item in attempts
               if item["tune"] == row["tune"] and
               item["logical_id"] == str(row["logical_id"]) and
               item["attempt"] == str(row["accepted_attempt"])]
    if len(matches) != 1:
        raise ValueError("attempt ledger does not uniquely authorize {}/{}".format(
            row["tune"], row["logical_id"]))
    item = matches[0]
    if (item["seed"] != str(row["accepted_seed"]) or
            item["outcome"] != "accepted" or
            item["raw_storage_key"] != row["raw_storage_key"] or
            not item["evidence_status"].startswith("accepted_manifest")):
        raise ValueError("attempt ledger authorization mismatch for {}/{}".format(
            row["tune"], row["logical_id"]))


def selected_rows(rows, args):
    sources = set(args.source or [])
    parsed_sources = set()
    for token in sources:
        if token.count(":") != 1:
            raise ValueError("--source must be TUNE:LOGICAL_ID")
        tune, logical = token.split(":")
        parsed_sources.add((tune, int(logical)))
    tunes = set(args.tune or [])
    logicals = set(args.logical_id or [])
    result = []
    for row in rows:
        identity = (row["tune"], row["logical_id"])
        if parsed_sources and identity not in parsed_sources:
            continue
        if tunes and row["tune"] not in tunes:
            continue
        if logicals and row["logical_id"] not in logicals:
            continue
        result.append(row)
    if parsed_sources - {(row["tune"], row["logical_id"]) for row in result}:
        raise ValueError("one or more requested --source identities are absent")
    if not result:
        raise ValueError("source selection is empty")
    return result


def load_rates(path):
    if path is None:
        return None
    regular_file(path, "rate receipt")
    value = json_file(path)
    if (not isinstance(value, dict) or set(value) != {"schema", "bytes_per_raw_byte"} or
            value["schema"] != "hadronization_analysis_size_rate_v1" or
            not isinstance(value["bytes_per_raw_byte"], (int, float)) or
            value["bytes_per_raw_byte"] <= 0):
        raise ValueError("rate receipt contract differs")
    return float(value["bytes_per_raw_byte"])


def make_plan(args):
    campaign_path = args.campaign.resolve()
    manifest_path = args.manifest.resolve()
    attempts_path = args.attempts.resolve()
    regular_file(campaign_path, "campaign descriptor")
    campaign = json_file(campaign_path)
    rows = load_manifest(manifest_path, campaign)
    attempts, attempts_digest = load_attempts(attempts_path)
    rows = selected_rows(rows, args)
    for row in rows:
        verify_attempt(row, attempts)
    if args.target_bytes <= 0:
        raise ValueError("--target-bytes must be positive")
    rate = load_rates(args.rates)
    estimates = [max(1, int(round(row["bytes"] * (rate if rate else 1.0))))
                 for row in rows]
    shards = []
    current = []
    current_bytes = 0
    source_rows = []
    for source_id, (row, estimate) in enumerate(zip(rows, estimates)):
        entry = {"source_id": source_id, "estimated_output_bytes": estimate,
                 "manifest_row": row}
        source_rows.append(entry)
        if current and current_bytes + estimate > args.target_bytes:
            shards.append({"ordinal": len(shards), "estimated_output_bytes": current_bytes,
                           "source_ids": current})
            current = []
            current_bytes = 0
        current.append(source_id)
        current_bytes += estimate
    shards.append({"ordinal": len(shards), "estimated_output_bytes": current_bytes,
                   "source_ids": current})
    source_subset_digest = sha_bytes(canonical([row for row in rows]).encode("utf-8"))
    map_payload = {"target_bytes": args.target_bytes,
                   "shards": [{"ordinal": shard["ordinal"],
                               "source_ids": shard["source_ids"]} for shard in shards]}
    plan = {
        "schema": PLAN_SCHEMA,
        "campaign": campaign["campaign"],
        "campaign_descriptor_sha256": sha_file(campaign_path),
        "manifest_sha256": sha_file(manifest_path),
        "attempt_ledger_sha256": attempts_digest,
        "schema_digest": SCHEMA_DIGEST,
        "registries_digest": REGISTRIES_DIGEST,
        "raw_mapping_digest": RAW_MAPPING_DIGEST,
        "source_subset_digest": source_subset_digest,
        "target_bytes": args.target_bytes,
        "estimate_basis": ({"schema": "hadronization_analysis_size_rate_v1",
                            "sha256": sha_file(args.rates.resolve()),
                            "bytes_per_raw_byte": rate} if rate else
                           {"schema": "raw_bytes_conservative_fallback_v1"}),
        "raw_root": str(args.raw_root.resolve(strict=False)),
        "output_root": str(args.output_root.resolve(strict=False)),
        "work_root": str(args.work_root.resolve(strict=False)),
        "manifest": str(manifest_path),
        "attempts": str(attempts_path),
        "campaign_descriptor": str(campaign_path),
        "sources": source_rows,
        "shards": shards,
        "map_digest": sha_bytes(canonical(map_payload).encode("utf-8")),
    }
    plan["plan_digest"] = sha_bytes(canonical(plan).encode("utf-8"))
    raw, work, output = safe_roots(args.raw_root, args.work_root, args.output_root)
    del raw, output
    plan_path = args.plan.resolve(strict=False)
    safe_child(work, plan_path, "plan output")
    atomic_json(plan_path, plan, exclusive=not args.replace_plan)
    print("ANALYSIS_PLAN={} SHARDS={} SOURCES={} MAP_DIGEST={}".format(
        plan_path, len(shards), len(rows), plan["map_digest"]))


def checked_plan(path):
    regular_file(path, "analysis plan")
    plan = json_file(path)
    expected = {
        "schema", "campaign", "campaign_descriptor_sha256", "manifest_sha256",
        "attempt_ledger_sha256", "schema_digest", "registries_digest",
        "raw_mapping_digest", "source_subset_digest", "target_bytes",
        "estimate_basis", "raw_root", "output_root", "work_root", "manifest",
        "attempts", "campaign_descriptor", "sources", "shards", "map_digest",
        "plan_digest",
    }
    exact_keys(plan, expected, "analysis plan")
    if plan["schema"] != PLAN_SCHEMA:
        raise ValueError("analysis plan schema differs")
    digest = plan.pop("plan_digest")
    calculated = sha_bytes(canonical(plan).encode("utf-8"))
    plan["plan_digest"] = digest
    if digest != calculated:
        raise ValueError("analysis plan digest mismatch")
    if (plan["schema_digest"] != SCHEMA_DIGEST or
            plan["registries_digest"] != REGISTRIES_DIGEST or
            plan["raw_mapping_digest"] != RAW_MAPPING_DIGEST):
        raise ValueError("analysis plan contract identity differs")
    if type(plan["target_bytes"]) is not int or plan["target_bytes"] <= 0:
        raise ValueError("analysis plan target bytes differ")
    if (not isinstance(plan["sources"], list) or not plan["sources"] or
            not isinstance(plan["shards"], list) or not plan["shards"]):
        raise ValueError("analysis plan source/shard map is empty")
    manifest_rows = []
    for source_id, source in enumerate(plan["sources"]):
        exact_keys(source, {"source_id", "estimated_output_bytes", "manifest_row"},
                   "analysis plan source")
        if (source["source_id"] != source_id or
                type(source["estimated_output_bytes"]) is not int or
                source["estimated_output_bytes"] <= 0):
            raise ValueError("analysis plan source identity/estimate differs")
        exact_keys(source["manifest_row"], MANIFEST_FIELDS,
                   "analysis plan manifest row")
        manifest_rows.append(source["manifest_row"])
    if plan["source_subset_digest"] != sha_bytes(
            canonical(manifest_rows).encode("utf-8")):
        raise ValueError("analysis plan source subset digest differs")
    assigned = []
    map_shards = []
    for ordinal, shard in enumerate(plan["shards"]):
        exact_keys(shard, {"ordinal", "estimated_output_bytes", "source_ids"},
                   "analysis plan shard")
        if (shard["ordinal"] != ordinal or
                type(shard["estimated_output_bytes"]) is not int or
                shard["estimated_output_bytes"] <= 0 or
                not isinstance(shard["source_ids"], list) or
                not shard["source_ids"] or
                any(type(item) is not int for item in shard["source_ids"])):
            raise ValueError("analysis plan shard identity/estimate differs")
        if shard["estimated_output_bytes"] != sum(
                plan["sources"][item]["estimated_output_bytes"]
                for item in shard["source_ids"] if 0 <= item < len(plan["sources"])):
            raise ValueError("analysis plan shard estimate differs")
        assigned.extend(shard["source_ids"])
        map_shards.append({"ordinal": ordinal, "source_ids": shard["source_ids"]})
    if assigned != list(range(len(plan["sources"]))):
        raise ValueError("analysis plan does not partition sources canonically")
    map_payload = {"target_bytes": plan["target_bytes"], "shards": map_shards}
    if plan["map_digest"] != sha_bytes(canonical(map_payload).encode("utf-8")):
        raise ValueError("analysis plan map digest differs")
    return plan


def command_tokens(command, arguments, environment, label):
    completed = subprocess.run([command] + list(arguments), env=environment,
                               text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    if completed.returncode:
        raise ValueError("{} failed: {}".format(label, completed.stderr.strip()))
    if completed.stderr.strip():
        raise ValueError("{} wrote a diagnostic: {}".format(
            label, completed.stderr.strip()))
    return shlex.split(completed.stdout.strip())


def compile_cpp(runtime, source, output):
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    root_config = environment["ROOT_CONFIG"]
    flags = command_tokens(root_config, ["--cflags"], environment, "ROOT cflags")
    libraries = command_tokens(root_config, ["--libs"], environment, "ROOT libs")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp-{}".format(os.getpid()))
    command = ([environment["CXX"], "-O2", "-std=c++17", "-Wall", "-Wextra",
                "-Wpedantic", str(source), "-I" + str(ROOT / "pipeline/generate")]
               + flags + libraries + ["-o", str(temporary)])
    subprocess.run(command, env=environment, check=True)
    os.replace(str(temporary), str(output))
    output.chmod(0o700)
    return command


def build_tools(work_root):
    runtime = runtime_contract.resolve(require_root=True)
    source_identity = sha_bytes(
        ANALYSIS_SOURCE.read_bytes() +
        (ROOT / "pipeline/generate/physics.hpp").read_bytes() +
        (ROOT / "pipeline/generate/sha256.hpp").read_bytes() +
        (ROOT / "pipeline/generate/study_contract.hpp").read_bytes())
    validator_identity = sha_bytes(
        RAW_VALIDATOR_SOURCE.read_bytes() +
        (ROOT / "pipeline/generate/physics.hpp").read_bytes() +
        (ROOT / "pipeline/generate/sha256.hpp").read_bytes() +
        (ROOT / "pipeline/generate/study_contract.hpp").read_bytes())
    binary_root = work_root / "bin"
    analyzer = binary_root / ("analyze-" + source_identity[:16])
    validator = binary_root / ("validate-raw-" + validator_identity[:16])
    if not analyzer.is_file():
        compile_cpp(runtime, ANALYSIS_SOURCE, analyzer)
    if not validator.is_file():
        compile_cpp(runtime, RAW_VALIDATOR_SOURCE, validator)
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    return runtime, environment, analyzer, validator


def source_path(raw_root, row):
    candidate = raw_root.joinpath(*PurePosixPath(row["raw_storage_key"]).parts)
    path = safe_child(raw_root, candidate, "raw source", must_exist=True)
    regular_file(path, "raw source")
    return path


def inspect_raw(analyzer, environment, path):
    completed = subprocess.run([str(analyzer), "inspect-raw", str(path)],
                               env=environment, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode:
        raise RuntimeError("raw metadata inspection failed: {}".format(
            completed.stderr.strip()))
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("raw metadata inspection returned invalid JSON") from error


def validate_raw(validator, environment, path, row, campaign, metadata):
    command = [
        str(validator), str(path), "--campaign", campaign["campaign"],
        "--tune", row["tune"], "--campaign-ordinal", str(campaign["seed"]["campaign_ordinal"]),
        "--logical-id", str(row["logical_id"]), "--attempt", str(row["accepted_attempt"]),
        "--seed", str(row["accepted_seed"]), "--events", str(row["successful_events"]),
        "--pthat-min", str(campaign["physics"]["pthat_min_gev"]),
        "--config-sha256", metadata["config_sha256"],
        "--executable-sha256", campaign["accepted_source"]["producer_executable_sha256"],
        "--repository-commit", campaign["accepted_source"]["producer_repository_commit"],
        "--pythia-version", campaign["runtime"]["pythia_version"],
    ]
    completed = subprocess.run(command, env=environment, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if completed.returncode:
        raise RuntimeError("raw validator rejected {}:\n{}".format(path, completed.stdout))
    return completed.stdout.strip()


def hexadecimal(value):
    return value.encode("utf-8").hex()


def write_spec(path, source_entries, source_paths, source_metadata, campaign,
               attempt_digest):
    lines = ["hadronization_analysis_source_spec_v1"]
    tune_index = {name: index for index, name in enumerate(campaign["tune_order"])}
    accepted = campaign["accepted_source"]
    for local_source_id, (entry, raw_path, metadata) in enumerate(
            zip(source_entries, source_paths, source_metadata)):
        row = entry["manifest_row"]
        values = [
            str(local_source_id), str(tune_index[row["tune"]]),
            str(campaign["seed"]["campaign_ordinal"]),
            str(row["logical_id"]), str(row["accepted_attempt"]),
            str(row["accepted_seed"]), str(row["successful_events"]),
            str(row["bytes"]), row["raw_sha256"],
            row["validation_receipt_sha256"], row["validation_log_sha256"],
            hexadecimal(row["tune"]), hexadecimal(row["raw_storage_key"]),
            hexadecimal(str(raw_path)), hexadecimal(canonical(row)),
            accepted["producer_executable_sha256"],
            accepted["producer_repository_commit"],
            metadata["effective_settings_sha256"], attempt_digest,
            hexadecimal(campaign["campaign"]),
        ]
        lines.append("\t".join(values))
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def contract_template(plan, shard, campaign, source_entries, runtime, analyzer):
    study_path = Path(plan["campaign_descriptor"]).parent.parent / "config/study.json"
    study_digest = sha_file(study_path) if study_path.is_file() else "UNAVAILABLE"
    interpretation = {
        "schema_digest": SCHEMA_DIGEST,
        "raw_schema": campaign["accepted_source"]["raw_schema"],
        "raw_mapping_digest": RAW_MAPPING_DIGEST,
        "structural_registries_digest": REGISTRIES_DIGEST,
    }
    return {
        "accepted_study_digest": study_digest,
        "activity_definitions": "DOWNSTREAM_QUERY_TIME_NOT_SHARD_VALIDITY",
        "analyzer_binary_digest": sha_file(analyzer),
        "analyzer_source_digest": sha_file(ANALYSIS_SOURCE),
        "assignment": {"assignment_id": 0, "blocks": 10,
                       "rule": "block=(logical_id%10)+1"},
        "axes": "DOWNSTREAM_QUERY_TIME_NOT_SHARD_VALIDITY",
        "campaign_descriptor_digest": plan["campaign_descriptor_sha256"],
        "completion": "COMPLETE_INDEPENDENT_SHARD",
        "compression": {"algorithm": "ZSTD", "level": 5},
        "estimator_slot": "UNCOMPUTED_ANALYZE1",
        "parent_shard_set_digest": "NOT_APPLICABLE_LOSSLESS_SOURCE",
        "profiles": "DOWNSTREAM_QUERY_TIME_NOT_SHARD_VALIDITY",
        "projection_domains": "ALL_DECLARED_LOSSLESS_ROWS",
        "raw_manifest_digest": plan["manifest_sha256"],
        "raw_runtime": "EXACT_PER_SOURCE_METADATA",
        "registries_digest": REGISTRIES_DIGEST,
        "runtime": {"root": next((item.split("=", 1)[1] for item in runtime["diagnostics"]
                                   if item.startswith("ROOT=")), "unknown"),
                    "platform": platform.platform(), "python": platform.python_version()},
        "schema_digest": SCHEMA_DIGEST,
        "scientific_content_digest": "X" * 64,
        "source_scientific_digests": "__SOURCE_DIGESTS__",
        "shard_map": {"map_digest": plan["map_digest"],
                      "ordinal": shard["ordinal"],
                      "source_ids": shard["source_ids"],
                      "target_bytes": plan["target_bytes"]},
        "source_metadata": "__SOURCE_METADATA__",
        "source_subset_digest": sha_bytes(canonical(
            [entry["manifest_row"] for entry in source_entries]).encode("utf-8")),
        "study_interpretation_digest": sha_bytes(canonical(interpretation).encode("utf-8")),
    }


def worker_summary(stdout):
    lines = [line for line in stdout.splitlines() if line.startswith("ANALYSIS_SUMMARY ")]
    if len(lines) != 1:
        raise RuntimeError("analysis worker did not emit one summary")
    values = {}
    for token in lines[0].split()[1:]:
        key, value = token.split("=", 1)
        values[key] = value
    rows = {}
    for name in TABLES:
        rows[name] = int(values.pop("rows_" + name))
    digest = values.pop("scientific_digest")
    source_digests = values.pop("source_digests").split(",")
    lower_hex = set("0123456789abcdef")
    if (values or len(digest) != 64 or not set(digest) <= lower_hex or
            not source_digests or any(len(item) != 64 or not set(item) <= lower_hex
                                      for item in source_digests)):
        raise RuntimeError("analysis worker summary contract differs")
    return digest, rows, source_digests


def receipt_for(plan, shard, campaign, entries, output, digest, rows,
                source_digests, analyzer, runtime, pre_hashes, elapsed):
    scientific = {
        "raw_mapping_digest": RAW_MAPPING_DIGEST,
        "raw_schema": campaign["accepted_source"]["raw_schema"],
        "schema_digest": SCHEMA_DIGEST,
        "scientific_content_digest": digest,
        "source_scientific_digests": source_digests,
        "source_subset_digest": sha_bytes(canonical(
            [entry["manifest_row"] for entry in entries]).encode("utf-8")),
        "structural_registries_digest": REGISTRIES_DIGEST,
    }
    storage = {
        "compression": {"algorithm": "ZSTD", "level": 5},
        "map_digest": plan["map_digest"], "ordering": "canonical_natural_key_v1",
        "root_bytes": output.stat().st_size, "root_sha256": sha_file(output),
        "shard_ordinal": shard["ordinal"], "source_ids": shard["source_ids"],
        "target_bytes": plan["target_bytes"],
    }
    provenance = {
        "analyzer_binary_sha256": sha_file(analyzer),
        "analyzer_source_sha256": sha_file(ANALYSIS_SOURCE),
        "compiler": next((item.split("=", 1)[1] for item in runtime["diagnostics"]
                          if item.startswith("CXX=")), "unknown"),
        "elapsed_seconds": elapsed, "host": platform.node(),
        "raw_pre_sha256": pre_hashes,
        "root": next((item.split("=", 1)[1] for item in runtime["diagnostics"]
                      if item.startswith("ROOT=")), "unknown"),
    }
    return {
        "schema": RECEIPT_SCHEMA, "state": "PASS",
        "campaign": plan["campaign"], "plan_digest": plan["plan_digest"],
        "map_digest": plan["map_digest"], "shard_ordinal": shard["ordinal"],
        "sources": entries, "rows": rows,
        "scientific_identity": scientific,
        "scientific_identity_sha256": sha_bytes(canonical(scientific).encode("utf-8")),
        "storage_identity": storage,
        "storage_identity_sha256": sha_bytes(canonical(storage).encode("utf-8")),
        "producer_provenance": provenance,
        "producer_provenance_sha256": sha_bytes(
            canonical(provenance).encode("utf-8")),
    }


def verify_receipt(receipt_path, root_path, plan=None, shard=None,
                   analyzer=None, environment=None):
    regular_file(receipt_path, "shard receipt")
    regular_file(root_path, "analysis shard")
    receipt = json_file(receipt_path)
    exact_keys(receipt, {"schema", "state", "campaign", "plan_digest",
                         "map_digest", "shard_ordinal", "sources", "rows",
                         "scientific_identity", "scientific_identity_sha256",
                         "storage_identity", "storage_identity_sha256",
                         "producer_provenance", "producer_provenance_sha256"},
               "shard receipt")
    if receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("state") != "PASS":
        raise ValueError("shard receipt is not a PASS receipt")
    storage = receipt.get("storage_identity")
    exact_keys(storage, {"compression", "map_digest", "ordering", "root_bytes",
                         "root_sha256", "shard_ordinal", "source_ids",
                         "target_bytes"}, "storage identity")
    if (not isinstance(storage, dict) or
            receipt.get("storage_identity_sha256") !=
            sha_bytes(canonical(storage).encode("utf-8"))):
        raise ValueError("storage identity digest mismatch")
    if root_path.stat().st_size != storage.get("root_bytes"):
        raise ValueError("analysis shard byte count differs from receipt")
    if sha_file(root_path) != storage.get("root_sha256"):
        raise ValueError("analysis shard SHA-256 differs from receipt")
    scientific = receipt.get("scientific_identity")
    exact_keys(scientific, {"raw_mapping_digest", "raw_schema", "schema_digest",
                            "scientific_content_digest", "source_scientific_digests",
                            "source_subset_digest", "structural_registries_digest"},
               "scientific identity")
    if (not isinstance(scientific, dict) or
            receipt.get("scientific_identity_sha256") !=
            sha_bytes(canonical(scientific).encode("utf-8"))):
        raise ValueError("scientific identity digest mismatch")
    if (scientific["schema_digest"] != SCHEMA_DIGEST or
            scientific["raw_mapping_digest"] != RAW_MAPPING_DIGEST or
            scientific["structural_registries_digest"] != REGISTRIES_DIGEST or
            not isinstance(scientific["source_scientific_digests"], list) or
            len(scientific["source_scientific_digests"]) != len(receipt["sources"])):
        raise ValueError("scientific identity contract differs")
    if not isinstance(receipt["sources"], list) or not receipt["sources"]:
        raise ValueError("receipt source membership is empty")
    source_rows = []
    source_ids = []
    for source in receipt["sources"]:
        exact_keys(source, {"source_id", "estimated_output_bytes", "manifest_row"},
                   "receipt source")
        if (type(source["source_id"]) is not int or source["source_id"] < 0 or
                type(source["estimated_output_bytes"]) is not int or
                source["estimated_output_bytes"] <= 0):
            raise ValueError("receipt source identity/estimate differs")
        exact_keys(source["manifest_row"], MANIFEST_FIELDS,
                   "receipt manifest row")
        source_ids.append(source["source_id"])
        source_rows.append(source["manifest_row"])
    if (storage["source_ids"] != source_ids or
            scientific["source_subset_digest"] != sha_bytes(
                canonical(source_rows).encode("utf-8"))):
        raise ValueError("receipt source subset identity differs")
    provenance = receipt["producer_provenance"]
    exact_keys(provenance,
               {"analyzer_binary_sha256", "analyzer_source_sha256", "compiler",
                "elapsed_seconds", "host", "raw_pre_sha256", "root"},
               "producer provenance")
    if receipt["producer_provenance_sha256"] != sha_bytes(
            canonical(provenance).encode("utf-8")):
        raise ValueError("producer provenance digest mismatch")
    expected_raw = {row["raw_storage_key"]: row["raw_sha256"]
                    for row in source_rows}
    if provenance["raw_pre_sha256"] != expected_raw:
        raise ValueError("producer raw-input provenance differs")
    if (not isinstance(receipt["rows"], dict) or
            set(receipt["rows"]) != set(TABLES) or
            any(type(value) is not int or value < 0
                for value in receipt["rows"].values())):
        raise ValueError("receipt row accounting differs")
    if plan is not None:
        if (receipt.get("plan_digest") != plan["plan_digest"] or
                receipt.get("map_digest") != plan["map_digest"]):
            raise ValueError("shard receipt belongs to a different plan")
    if shard is not None and receipt.get("shard_ordinal") != shard["ordinal"]:
        raise ValueError("shard receipt ordinal differs")
    if shard is not None:
        expected_sources = [plan["sources"][item] for item in shard["source_ids"]]
        if (receipt["sources"] != expected_sources or
                storage["source_ids"] != shard["source_ids"] or
                storage["shard_ordinal"] != shard["ordinal"] or
                storage["map_digest"] != plan["map_digest"] or
                storage["target_bytes"] != plan["target_bytes"]):
            raise ValueError("receipt storage/source membership differs from plan")
    if analyzer is not None:
        completed = subprocess.run([str(analyzer), "verify", str(root_path)],
                                   env=environment, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.returncode:
            raise ValueError("ROOT shard verification failed: {}".format(
                completed.stderr.strip()))
        digest, rows, source_digests = worker_summary(completed.stdout)
        if digest != scientific.get("scientific_content_digest"):
            raise ValueError("ROOT scientific digest differs from receipt")
        if rows != receipt.get("rows"):
            raise ValueError("ROOT row counts differ from receipt")
        if source_digests != scientific.get("source_scientific_digests"):
            raise ValueError("ROOT source scientific digests differ from receipt")
    return receipt


def link_no_overwrite(staged, final):
    try:
        os.link(str(staged), str(final))
    except OSError as error:
        if error.errno == errno.EXDEV:
            raise RuntimeError("staging and final roots must share a filesystem") from error
        if error.errno == errno.EEXIST:
            raise FileExistsError("no-overwrite promotion collision: {}".format(final)) from error
        raise


def produce_one(plan, shard, campaign, attempts, attempt_digest, runtime,
                environment, analyzer, validator, raw_root, work_root,
                campaign_output, resume):
    ordinal = shard["ordinal"]
    final_root = campaign_output / "shard-{:04d}.root".format(ordinal)
    final_receipt = campaign_output / "shard-{:04d}.json".format(ordinal)
    if final_root.exists() or final_receipt.exists():
        if not resume or not final_root.is_file() or not final_receipt.is_file():
            raise FileExistsError("foreign or partial final collision for shard {}".format(ordinal))
        verify_receipt(final_receipt, final_root, plan, shard, analyzer, environment)
        return "REUSED shard={} root={}".format(ordinal, final_root)
    entries = [plan["sources"][source_id] for source_id in shard["source_ids"]]
    paths = []
    inspections = []
    pre_hashes = {}
    for entry in entries:
        row = entry["manifest_row"]
        verify_attempt(row, attempts)
        path = source_path(raw_root, row)
        if path.stat().st_size != row["bytes"]:
            raise ValueError("raw source byte count differs: {}".format(path))
        digest = sha_file(path)
        if digest != row["raw_sha256"]:
            raise ValueError("raw source SHA-256 differs: {}".format(path))
        pre_hashes[row["raw_storage_key"]] = digest
        metadata = inspect_raw(analyzer, environment, path)
        validate_raw(validator, environment, path, row, campaign, metadata)
        paths.append(path)
        inspections.append(metadata)
    stage = work_root / "staging" / "shard-{:04d}-{}-{}".format(
        ordinal, os.getpid(), time.time_ns())
    stage.mkdir(parents=True, mode=0o700)
    try:
        spec = stage / "sources.tsv"
        contract = stage / "contract.json"
        staged_root = stage / "shard.root"
        staged_receipt = stage / "shard.json"
        write_spec(spec, entries, paths, inspections, campaign, attempt_digest)
        atomic_json(contract, contract_template(
            plan, shard, campaign, entries, runtime, analyzer), exclusive=True)
        started = time.monotonic()
        completed = subprocess.run([str(analyzer), "write", str(spec),
                                    str(staged_root), str(contract)],
                                   env=environment, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.returncode:
            raise RuntimeError("analysis worker rejected shard {}: {}".format(
                ordinal, completed.stderr.strip()))
        digest, rows, source_digests = worker_summary(completed.stdout)
        verify_completed = subprocess.run([str(analyzer), "verify", str(staged_root)],
                                          env=environment, text=True,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if verify_completed.returncode:
            raise RuntimeError("staged shard reopen failed: {}".format(
                verify_completed.stderr.strip()))
        verify_digest, verify_rows, verify_source_digests = worker_summary(
            verify_completed.stdout)
        if ((verify_digest, verify_rows, verify_source_digests) !=
                (digest, rows, source_digests)):
            raise RuntimeError("staged shard readback summary changed")
        receipt = receipt_for(plan, shard, campaign, entries, staged_root, digest,
                              rows, source_digests, analyzer, runtime, pre_hashes,
                              time.monotonic() - started)
        for entry, path in zip(entries, paths):
            row = entry["manifest_row"]
            if path.stat().st_size != row["bytes"] or sha_file(path) != row["raw_sha256"]:
                raise RuntimeError("raw source changed during analysis: {}".format(path))
        atomic_json(staged_receipt, receipt, exclusive=True)
        verify_receipt(staged_receipt, staged_root, plan, shard, analyzer, environment)
        campaign_output.mkdir(parents=True, exist_ok=True)
        link_no_overwrite(staged_receipt, final_receipt)
        try:
            link_no_overwrite(staged_root, final_root)
        except BaseException:
            if final_receipt.is_file() and os.path.samefile(
                    str(staged_receipt), str(final_receipt)):
                final_receipt.unlink()
            raise
        staged_receipt.unlink()
        staged_root.unlink()
        return "PROMOTED shard={} root={} receipt={}".format(
            ordinal, final_root, final_receipt)
    finally:
        shutil.rmtree(str(stage), ignore_errors=True)


def run_plan(args):
    plan = checked_plan(args.plan.resolve())
    raw_root, work_root, output_root = safe_roots(
        Path(args.raw_root or plan["raw_root"]), Path(args.work_root or plan["work_root"]),
        Path(args.output_root or plan["output_root"]))
    if sha_file(Path(plan["manifest"])) != plan["manifest_sha256"]:
        raise ValueError("manifest changed since planning")
    if sha_file(Path(plan["attempts"])) != plan["attempt_ledger_sha256"]:
        raise ValueError("attempt ledger changed since planning")
    if sha_file(Path(plan["campaign_descriptor"])) != plan["campaign_descriptor_sha256"]:
        raise ValueError("campaign descriptor changed since planning")
    campaign = json_file(Path(plan["campaign_descriptor"]))
    manifest = load_manifest(Path(plan["manifest"]), campaign)
    manifest_encodings = {canonical(row) for row in manifest}
    if (len(plan["sources"]) != len({canonical(source["manifest_row"])
                                     for source in plan["sources"]}) or
            any(canonical(source["manifest_row"]) not in manifest_encodings
                for source in plan["sources"])):
        raise ValueError("planned source subset is not authorized by the manifest")
    attempts, attempt_digest = load_attempts(Path(plan["attempts"]))
    runtime, environment, analyzer, validator = build_tools(work_root)
    selected = set(args.shard or [shard["ordinal"] for shard in plan["shards"]])
    shards = [shard for shard in plan["shards"] if shard["ordinal"] in selected]
    if selected != {shard["ordinal"] for shard in shards}:
        raise ValueError("one or more requested shard ordinals are absent")
    if args.jobs < 1 or args.jobs > 32:
        raise ValueError("--jobs must be in [1,32]")
    campaign_output = safe_child(output_root, output_root / plan["campaign"],
                                 "campaign output")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(
            produce_one, plan, shard, campaign, attempts, attempt_digest, runtime,
            environment, analyzer, validator, raw_root, work_root, campaign_output,
            args.resume) for shard in shards]
        for future in futures:
            results.append(future.result())
    for result in sorted(results):
        print(result)


def verify_command(args):
    plan = checked_plan(args.plan.resolve()) if args.plan else None
    if plan:
        raw_root, work_root, output_root = safe_roots(
            Path(args.raw_root or plan["raw_root"]), Path(args.work_root or plan["work_root"]),
            Path(args.output_root or plan["output_root"]))
        del raw_root
        runtime, environment, analyzer, unused = build_tools(work_root)
        del runtime, unused
        selected = set(args.shard or [shard["ordinal"] for shard in plan["shards"]])
        if selected - {shard["ordinal"] for shard in plan["shards"]}:
            raise ValueError("one or more requested shard ordinals are absent")
        for shard in plan["shards"]:
            if shard["ordinal"] not in selected:
                continue
            root_path = output_root / plan["campaign"] / "shard-{:04d}.root".format(shard["ordinal"])
            receipt = root_path.with_suffix(".json")
            verify_receipt(receipt, root_path, plan, shard, analyzer, environment)
            print("VERIFIED shard={} root={}".format(shard["ordinal"], root_path))
        return
    if not args.root:
        raise ValueError("verify requires --plan or --root")
    reject_symlink_components(args.root, "analysis shard")
    root_path = args.root.resolve()
    if args.receipt:
        reject_symlink_components(args.receipt, "shard receipt")
    receipt = (args.receipt.resolve() if args.receipt else root_path.with_suffix(".json"))
    work_root = Path(args.work_root or ROOT / "data/work/analyze").resolve(strict=False)
    output_root = root_path.parent.parent.resolve(strict=False)
    raw_root = Path(args.raw_root or ROOT / "data/raw").resolve(strict=False)
    unused_raw, work_root, unused_output = safe_roots(raw_root, work_root, output_root)
    del unused_raw, unused_output
    runtime, environment, analyzer, unused = build_tools(work_root)
    del runtime, unused
    verify_receipt(receipt, root_path, analyzer=analyzer, environment=environment)
    print("VERIFIED root={}".format(root_path))


def explain(args):
    if args.plan:
        plan = checked_plan(args.plan.resolve())
        selected = args.shard
        payload = dict(plan)
        if selected:
            if set(selected) - {item["ordinal"] for item in plan["shards"]}:
                raise ValueError("one or more requested shard ordinals are absent")
            payload["shards"] = [item for item in plan["shards"]
                                  if item["ordinal"] in set(selected)]
        print(json.dumps(payload, sort_keys=True, indent=2))
        return
    if not args.receipt:
        raise ValueError("explain requires --plan or --receipt")
    reject_symlink_components(args.receipt, "shard receipt")
    receipt_path = args.receipt.resolve()
    receipt = verify_receipt(receipt_path, receipt_path.with_suffix(".root"))
    print(json.dumps(receipt, sort_keys=True, indent=2))


def parser():
    top = argparse.ArgumentParser(prog="hadronization analyze", description=__doc__)
    sub = top.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan", help="emit an exact deterministic source-to-shard map")
    plan.add_argument("--campaign", type=Path, default=ROOT / "data/campaign.json")
    plan.add_argument("--manifest", type=Path, default=ROOT / "data/raw_manifest.jsonl")
    plan.add_argument("--attempts", type=Path, default=ROOT / "data/attempts.csv")
    plan.add_argument("--raw-root", type=Path, default=ROOT / "data/raw")
    plan.add_argument("--work-root", type=Path, default=ROOT / "data/work/analyze")
    plan.add_argument("--output-root", type=Path, default=ROOT / "data/analyzed")
    plan.add_argument("--plan", type=Path, default=ROOT / "data/work/analyze/plan.json")
    plan.add_argument("--target-bytes", type=int, required=True)
    plan.add_argument("--rates", type=Path)
    plan.add_argument("--tune", action="append")
    plan.add_argument("--logical-id", action="append", type=int)
    plan.add_argument("--source", action="append")
    plan.add_argument("--replace-plan", action="store_true")

    run = sub.add_parser("run", help="produce selected independently promoted shards")
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--raw-root", type=Path)
    run.add_argument("--work-root", type=Path)
    run.add_argument("--output-root", type=Path)
    run.add_argument("--shard", action="append", type=int)
    run.add_argument("--jobs", type=int, default=1)
    resume = run.add_mutually_exclusive_group()
    resume.add_argument("--resume", action="store_true", default=True)
    resume.add_argument("--no-resume", action="store_false", dest="resume")

    verify = sub.add_parser("verify", help="independently verify shards and receipts")
    verify.add_argument("--plan", type=Path)
    verify.add_argument("--root", type=Path)
    verify.add_argument("--receipt", type=Path)
    verify.add_argument("--raw-root", type=Path)
    verify.add_argument("--work-root", type=Path)
    verify.add_argument("--output-root", type=Path)
    verify.add_argument("--shard", action="append", type=int)

    explain_parser = sub.add_parser("explain", help="show exact source and identity receipts")
    explain_parser.add_argument("--plan", type=Path)
    explain_parser.add_argument("--receipt", type=Path)
    explain_parser.add_argument("--shard", action="append", type=int)
    return top


def main():
    args = parser().parse_args()
    try:
        if args.command == "plan":
            make_plan(args)
        elif args.command == "run":
            run_plan(args)
        elif args.command == "verify":
            verify_command(args)
        else:
            explain(args)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
