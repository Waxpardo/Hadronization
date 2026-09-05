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
import re
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
BUILD_SCHEMA = "hadronization_analysis_tool_build_v1"
DEPENDENCY_SCHEMA = "hadronization_lossless_dependency_v1"
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


def fsync_directory(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def fsync_file(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_json(path, value, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    target = path
    if not exclusive:
        temporary = path.with_name(".{}.{}-{}.tmp".format(
            path.name, os.getpid(), time.time_ns()))
        target = temporary
    descriptor = os.open(str(target), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(canonical(value) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        if temporary is not None:
            os.replace(str(temporary), str(path))
        fsync_directory(path.parent)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        if temporary is not None and os.path.lexists(str(temporary)):
            temporary.unlink()
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


def lower_sha256(value, label):
    if (not isinstance(value, str) or
            re.fullmatch(r"[0-9a-f]{64}", value) is None):
        raise ValueError("{} is not lowercase SHA-256".format(label))


def bounded_int(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("{} is outside [{} ,{}]".format(label, low, high))
    return value


def seed_for(campaign, tune, logical_id, attempt):
    seed = campaign["seed"]
    value = (100000001 + seed["campaign_ordinal"] * 10000000 +
             seed["tune_ordinals"][tune] * 1000000 +
             attempt * 100000 + logical_id)
    if not 1 <= value <= 900000000:
        raise ValueError("derived seed is outside the supported PYTHIA domain")
    return value


def campaign_adapter(campaign):
    top_fields = {
        "accepted_source", "attempt_evidence_inventory", "blocks", "campaign",
        "current_interpretation_definitions", "held_attempt_policy",
        "logical_jobs_per_tune", "physics", "runtime", "schema", "seed",
        "successful_events_per_logical_job", "successful_events_per_tune",
        "systematic_uncertainties", "tune_order", "version",
    }
    exact_keys(campaign, top_fields, "campaign descriptor")
    if campaign["schema"] != "hadronization_campaign_record_v1" or campaign["version"] != 1:
        raise ValueError("campaign descriptor schema/version differs")
    if (not isinstance(campaign["campaign"], str) or
            re.fullmatch(r"[A-Z0-9][A-Z0-9_-]{0,63}", campaign["campaign"]) is None):
        raise ValueError("campaign namespace is unsupported")

    tunes = campaign["tune_order"]
    if (not isinstance(tunes, list) or not tunes or len(tunes) > 4 or
            any(not isinstance(tune, str) or not tune for tune in tunes) or
            len(set(tunes)) != len(tunes)):
        raise ValueError("campaign tune order is not a unique supported list")
    jobs = bounded_int(campaign["logical_jobs_per_tune"], 1, 16384,
                       "logical jobs per tune")
    events = bounded_int(campaign["successful_events_per_logical_job"], 1,
                         (1 << 20) - 1, "successful events per logical job")
    bounded_int(campaign["successful_events_per_tune"], 1, (1 << 63) - 1,
                "successful events per tune")
    if campaign["successful_events_per_tune"] != jobs * events:
        raise ValueError("campaign successful-event exposure is incoherent")

    blocks = campaign["blocks"]
    exact_keys(blocks, {"count", "logical_id_domain", "logical_id_rule"},
               "campaign block descriptor")
    count = bounded_int(blocks["count"], 1, jobs, "campaign block count")
    if jobs % count:
        raise ValueError("campaign block exposure is not equal across blocks")
    if blocks["logical_id_domain"] != [0, jobs - 1]:
        raise ValueError("campaign logical-ID domain differs from declared jobs")
    expected_rule = "block=(logical_id%{})+1".format(count)
    if blocks["logical_id_rule"] != expected_rule:
        raise ValueError("campaign block assignment rule differs")

    seed = campaign["seed"]
    exact_keys(seed, {"schema", "formula", "campaign_ordinal", "tune_ordinals",
                      "attempt_domain"}, "campaign seed descriptor")
    if seed["schema"] != "seed_derivation_v2" or seed["formula"] != (
            "100000001+campaign_ordinal*10000000+tune_ordinal*1000000+"
            "attempt*100000+logical_id"):
        raise ValueError("campaign seed schema/formula differs")
    bounded_int(seed["campaign_ordinal"], 1, 65535, "campaign ordinal")
    expected_ordinals = {tune: ordinal for ordinal, tune in enumerate(tunes)}
    if seed["tune_ordinals"] != expected_ordinals:
        raise ValueError("campaign tune ordinals do not exactly match tune order")
    if (not isinstance(seed["attempt_domain"], list) or
            len(seed["attempt_domain"]) != 2):
        raise ValueError("campaign attempt domain differs")
    attempt_low = bounded_int(seed["attempt_domain"][0], 0, 4095,
                              "campaign attempt-domain lower bound")
    attempt_high = bounded_int(seed["attempt_domain"][1], 0, 4095,
                               "campaign attempt-domain upper bound")
    if attempt_low > attempt_high or attempt_high - attempt_low > 9:
        raise ValueError("campaign attempt domain is non-injective for seed strides")

    accepted = campaign["accepted_source"]
    exact_keys(accepted, {"origin_algorithm", "producer_executable_sha256",
                          "producer_repository_commit", "raw_manifest_schema",
                          "raw_manifest_sha256", "raw_schema", "selector",
                          "tune_cards", "tune_difference_allowlist"},
               "accepted raw definition")
    if (accepted["raw_schema"] != "hf_primary_ground_raw_v7" or
            accepted["raw_manifest_schema"] != "hf_canonical_raw_manifest_v2" or
            not isinstance(accepted["origin_algorithm"], str) or
            not accepted["origin_algorithm"] or
            not isinstance(accepted["selector"], str) or not accepted["selector"]):
        raise ValueError("accepted raw schema/mapping definition differs")
    lower_sha256(accepted["producer_executable_sha256"],
                 "accepted producer executable")
    lower_sha256(accepted["raw_manifest_sha256"], "accepted raw-manifest identity")
    if (not isinstance(accepted["producer_repository_commit"], str) or
            re.fullmatch(r"[0-9a-f]{40}", accepted["producer_repository_commit"]) is None):
        raise ValueError("accepted producer commit is malformed")
    if not isinstance(accepted["tune_cards"], dict) or set(accepted["tune_cards"]) != set(tunes):
        raise ValueError("accepted tune-card identities do not cover tune order")
    for tune, card in accepted["tune_cards"].items():
        exact_keys(card, {"accepted_effective_sha256", "current_definition_sha256"},
                   "accepted tune card {}".format(tune))
        lower_sha256(card["accepted_effective_sha256"],
                     "accepted effective tune card {}".format(tune))
        lower_sha256(card["current_definition_sha256"],
                     "current tune card {}".format(tune))
    allowlist = accepted["tune_difference_allowlist"]
    exact_keys(allowlist, {"schema", "sha256"}, "tune difference allowlist")
    if not isinstance(allowlist["schema"], str) or not allowlist["schema"]:
        raise ValueError("tune difference allowlist schema differs")
    lower_sha256(allowlist["sha256"], "tune difference allowlist")

    physics = campaign["physics"]
    exact_keys(physics, {"beam", "hard_processes", "heavy_hadron_decays",
                         "pthat_min_gev", "sqrt_s_gev"}, "campaign physics")
    if (physics != {"beam": "pp", "hard_processes": ["ccbar", "bbbar"],
                    "heavy_hadron_decays": "disabled", "pthat_min_gev": 2.0,
                    "sqrt_s_gev": 13600}):
        raise ValueError("campaign physics differs from the supported raw-v7 definition")
    exact_keys(campaign["runtime"], {"pythia_version"}, "campaign runtime")
    if campaign["runtime"]["pythia_version"] != "8.317":
        raise ValueError("campaign PYTHIA version differs")
    if (campaign["systematic_uncertainties"] != "disabled" or
            campaign["held_attempt_policy"] != "record_and_disclose_no_correction"):
        raise ValueError("campaign nominal/held-attempt policy differs")

    inventory = campaign["attempt_evidence_inventory"]
    exact_keys(inventory, {"file_count", "sha256"}, "attempt evidence inventory")
    bounded_int(inventory["file_count"], 1, (1 << 31) - 1,
                "attempt evidence file count")
    lower_sha256(inventory["sha256"], "attempt evidence inventory")
    definitions = campaign["current_interpretation_definitions"]
    exact_keys(definitions, {"files", "role"}, "current interpretation definitions")
    if (definitions["role"] != "interpretation_only_not_claimed_as_accepted_producer" or
            not isinstance(definitions["files"], list)):
        raise ValueError("current interpretation definition role differs")
    for entry in definitions["files"]:
        exact_keys(entry, {"bytes", "path", "sha256"},
                   "current interpretation definition")
        bounded_int(entry["bytes"], 1, (1 << 63) - 1,
                    "current interpretation definition bytes")
        if not isinstance(entry["path"], str) or not entry["path"]:
            raise ValueError("current interpretation definition path differs")
        lower_sha256(entry["sha256"], "current interpretation definition")

    seeds = set()
    for tune in tunes:
        for attempt in range(attempt_low, attempt_high + 1):
            for logical_id in range(jobs):
                derived = seed_for(campaign, tune, logical_id, attempt)
                if derived in seeds:
                    raise ValueError("campaign seed domains collide")
                seeds.add(derived)

    lossless_campaign = {
        "accepted_source": accepted,
        "campaign": campaign["campaign"],
        "logical_jobs_per_tune": jobs,
        "physics": physics,
        "runtime": campaign["runtime"],
        "schema": campaign["schema"],
        "seed": seed,
        "successful_events_per_logical_job": events,
        "successful_events_per_tune": campaign["successful_events_per_tune"],
        "tune_order": tunes,
        "version": campaign["version"],
    }
    return {
        "attempt_high": attempt_high, "attempt_low": attempt_low,
        "block_count": count, "events_per_job": events, "jobs": jobs,
        "lossless_campaign_identity": lossless_campaign,
        "lossless_campaign_identity_sha256": sha_bytes(
            canonical(lossless_campaign).encode("utf-8")),
        "tune_ordinals": expected_ordinals,
    }


MANIFEST_FIELDS = {
    "accepted_attempt", "accepted_seed", "block", "bytes", "logical_id",
    "raw_sha256", "raw_storage_key", "successful_events", "tune",
    "validation_log_sha256", "validation_receipt_sha256",
}


def load_manifest(path, campaign, adapter):
    regular_file(path, "manifest")
    rows = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError("manifest line {} is invalid JSON".format(number)) from error
        if line != canonical(row):
            raise ValueError("manifest line {} is not canonical JSON".format(number))
        exact_keys(row, MANIFEST_FIELDS, "manifest line {}".format(number))
        for key in ("logical_id", "accepted_attempt", "accepted_seed", "block",
                    "bytes", "successful_events"):
            if type(row[key]) is not int or row[key] < 0:
                raise ValueError("manifest {} is not a nonnegative integer".format(key))
        if row["bytes"] <= 0 or row["successful_events"] <= 0:
            raise ValueError("manifest size/event exposure must be positive")
        logical_id = row["logical_id"]
        attempt = row["accepted_attempt"]
        if logical_id >= adapter["jobs"] or logical_id > 16383:
            raise ValueError("manifest logical ID is outside the campaign/event-ID domain")
        if not adapter["attempt_low"] <= attempt <= adapter["attempt_high"] or attempt > 4095:
            raise ValueError("manifest attempt is outside the campaign/event-ID domain")
        if row["successful_events"] != adapter["events_per_job"]:
            raise ValueError("manifest successful-event exposure differs from campaign")
        if row["successful_events"] >= (1 << 20):
            raise ValueError("manifest successful events exceed the event-ID local field")
        if row["block"] != (logical_id % adapter["block_count"]) + 1:
            raise ValueError("manifest source block does not match the descriptor rule")
        if row["tune"] not in campaign["tune_order"]:
            raise ValueError("manifest contains an unknown tune")
        if row["accepted_seed"] != seed_for(campaign, row["tune"], logical_id, attempt):
            raise ValueError("manifest accepted seed differs from the campaign formula")
        for key in ("raw_sha256", "validation_log_sha256",
                    "validation_receipt_sha256"):
            if (not isinstance(row[key], str) or len(row[key]) != 64 or
                    any(character not in "0123456789abcdef" for character in row[key])):
                raise ValueError("manifest {} is not lowercase SHA-256".format(key))
        storage = PurePosixPath(row["raw_storage_key"])
        if (not isinstance(row["raw_storage_key"], str) or storage.is_absolute() or
                not storage.parts or any(part in {"", ".", ".."} for part in storage.parts)):
            raise ValueError("manifest raw_storage_key is not a portable relative key")
        if storage.parts[0] != row["tune"]:
            raise ValueError("manifest raw_storage_key tune namespace differs")
        rows.append(row)
    tune_index = {name: index for index, name in enumerate(campaign["tune_order"])}
    ordered = sorted(rows, key=lambda row: (
        tune_index[row["tune"]], row["logical_id"], row["accepted_attempt"],
        row["raw_storage_key"]))
    if rows != ordered:
        raise ValueError("manifest is not in canonical source order")
    identities = [(row["tune"], row["logical_id"]) for row in rows]
    expected = [(tune, logical_id) for tune in campaign["tune_order"]
                for logical_id in range(adapter["jobs"])]
    if identities != expected:
        raise ValueError("manifest coverage is not exactly the declared campaign domain")
    storage_keys = [row["raw_storage_key"] for row in rows]
    accepted_seeds = [row["accepted_seed"] for row in rows]
    if len(set(storage_keys)) != len(storage_keys):
        raise ValueError("manifest repeats a raw storage identity")
    if len(set(accepted_seeds)) != len(accepted_seeds):
        raise ValueError("manifest accepted seeds collide")
    for tune in campaign["tune_order"]:
        exposure = sum(row["successful_events"] for row in rows
                       if row["tune"] == tune)
        if exposure != campaign["successful_events_per_tune"]:
            raise ValueError("manifest tune exposure is incoherent")
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


def validate_attempts(campaign, adapter, manifest, attempts):
    if len(attempts) != campaign["attempt_evidence_inventory"]["file_count"]:
        raise ValueError("attempt ledger count differs from campaign inventory")
    allowed_evidence = {
        "accepted_manifest_and_scheduler_log_confirmed",
        "accepted_manifest_confirmed", "scheduler_log_confirmed",
        "inferred_from_accepted_attempt_ordinal",
    }
    parsed = []
    seen = set()
    for number, row in enumerate(attempts, 2):
        try:
            logical_id = int(row["logical_id"])
            attempt = int(row["attempt"])
            seed = int(row["seed"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("attempt ledger line {} has invalid integers".format(number)) from error
        identity = (row.get("tune"), logical_id, attempt)
        if identity in seen:
            raise ValueError("attempt ledger repeats an attempt identity")
        seen.add(identity)
        if (row.get("tune") not in campaign["tune_order"] or
                not 0 <= logical_id < adapter["jobs"] or
                not adapter["attempt_low"] <= attempt <= adapter["attempt_high"]):
            raise ValueError("attempt ledger identity is outside the campaign domain")
        if seed != seed_for(campaign, row["tune"], logical_id, attempt):
            raise ValueError("attempt ledger seed differs from campaign formula")
        if (row.get("outcome") not in {"accepted", "discarded"} or
                row.get("evidence_status") not in allowed_evidence):
            raise ValueError("attempt ledger outcome/evidence status differs")
        if row["outcome"] == "discarded" and row.get("raw_storage_key"):
            raise ValueError("discarded attempt carries a raw storage key")
        parsed.append((identity, row))
    groups = {}
    for (tune, logical_id, unused_attempt), row in parsed:
        del unused_attempt
        groups.setdefault((tune, logical_id), []).append(row)
    manifest_by_source = {(row["tune"], row["logical_id"]): row for row in manifest}
    if set(groups) != set(manifest_by_source):
        raise ValueError("attempt ledger coverage differs from manifest")
    for identity, manifest_row in manifest_by_source.items():
        group = groups[identity]
        ordinals = [int(row["attempt"]) for row in group]
        if ordinals != list(range(manifest_row["accepted_attempt"] + 1)):
            raise ValueError("attempt ledger sequence is not 0..accepted attempt")
        accepted = [row for row in group if row["outcome"] == "accepted"]
        if len(accepted) != 1 or accepted[0] is not group[-1]:
            raise ValueError("attempt ledger accepted attempt is not unique and final")
        final = accepted[0]
        if (int(final["seed"]) != manifest_row["accepted_seed"] or
                final["raw_storage_key"] != manifest_row["raw_storage_key"]):
            raise ValueError("attempt ledger accepted source differs from manifest")


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


def raw_source_identity_rows(rows):
    return [{key: value for key, value in row.items() if key != "block"}
            for row in rows]


def lossless_dependency_identity(campaign, adapter, rows):
    raw_sources = raw_source_identity_rows(rows)
    return {
        "accepted_raw_definition": campaign["accepted_source"],
        "campaign_lossless_identity_sha256":
            adapter["lossless_campaign_identity_sha256"],
        "campaign_namespace": campaign["campaign"],
        "raw_mapping_digest": RAW_MAPPING_DIGEST,
        "raw_schema": campaign["accepted_source"]["raw_schema"],
        "raw_source_subset_digest": sha_bytes(
            canonical(raw_sources).encode("utf-8")),
        "registries_digest": REGISTRIES_DIGEST,
        "schema": DEPENDENCY_SCHEMA,
        "schema_digest": SCHEMA_DIGEST,
    }


def make_plan(args):
    campaign_path = args.campaign.resolve()
    manifest_path = args.manifest.resolve()
    attempts_path = args.attempts.resolve()
    regular_file(campaign_path, "campaign descriptor")
    campaign = json_file(campaign_path)
    adapter = campaign_adapter(campaign)
    manifest_rows = load_manifest(manifest_path, campaign, adapter)
    attempts, attempts_digest = load_attempts(attempts_path)
    validate_attempts(campaign, adapter, manifest_rows, attempts)
    rows = selected_rows(manifest_rows, args)
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
    dependency = lossless_dependency_identity(campaign, adapter, rows)
    map_payload = {"target_bytes": args.target_bytes,
                   "shards": [{"ordinal": shard["ordinal"],
                               "source_ids": shard["source_ids"]} for shard in shards]}
    plan = {
        "schema": PLAN_SCHEMA,
        "campaign": campaign["campaign"],
        "campaign_descriptor_sha256": sha_file(campaign_path),
        "campaign_lossless_identity_sha256":
            adapter["lossless_campaign_identity_sha256"],
        "manifest_sha256": sha_file(manifest_path),
        "attempt_ledger_sha256": attempts_digest,
        "block_assignment": campaign["blocks"],
        "tune_ordinals": campaign["seed"]["tune_ordinals"],
        "schema_digest": SCHEMA_DIGEST,
        "registries_digest": REGISTRIES_DIGEST,
        "raw_mapping_digest": RAW_MAPPING_DIGEST,
        "source_subset_digest": source_subset_digest,
        "lossless_dependency_identity": dependency,
        "lossless_dependency_identity_sha256": sha_bytes(
            canonical(dependency).encode("utf-8")),
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
        "campaign_lossless_identity_sha256", "attempt_ledger_sha256",
        "block_assignment", "tune_ordinals", "schema_digest", "registries_digest",
        "raw_mapping_digest", "source_subset_digest", "target_bytes",
        "lossless_dependency_identity", "lossless_dependency_identity_sha256",
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
    dependency = plan["lossless_dependency_identity"]
    if (not isinstance(dependency, dict) or
            plan["lossless_dependency_identity_sha256"] != sha_bytes(
                canonical(dependency).encode("utf-8"))):
        raise ValueError("analysis plan lossless dependency digest differs")
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

    campaign_path = Path(plan["campaign_descriptor"])
    manifest_path = Path(plan["manifest"])
    attempts_path = Path(plan["attempts"])
    for path, expected_sha, label in (
            (campaign_path, plan["campaign_descriptor_sha256"], "campaign descriptor"),
            (manifest_path, plan["manifest_sha256"], "manifest"),
            (attempts_path, plan["attempt_ledger_sha256"], "attempt ledger")):
        regular_file(path, label)
        if sha_file(path) != expected_sha:
            raise ValueError("{} changed since planning".format(label))
    campaign = json_file(campaign_path)
    adapter = campaign_adapter(campaign)
    manifest = load_manifest(manifest_path, campaign, adapter)
    attempts, unused_digest = load_attempts(attempts_path)
    del unused_digest
    validate_attempts(campaign, adapter, manifest, attempts)
    if (plan["campaign"] != campaign["campaign"] or
            plan["campaign_lossless_identity_sha256"] !=
            adapter["lossless_campaign_identity_sha256"] or
            plan["block_assignment"] != campaign["blocks"] or
            plan["tune_ordinals"] != campaign["seed"]["tune_ordinals"]):
        raise ValueError("analysis plan campaign binding differs")
    authorized = {canonical(row) for row in manifest}
    if any(canonical(row) not in authorized for row in manifest_rows):
        raise ValueError("analysis plan source subset is not manifest-authorized")
    expected_dependency = lossless_dependency_identity(campaign, adapter, manifest_rows)
    if dependency != expected_dependency:
        raise ValueError("analysis plan lossless dependency identity differs")
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


def compile_cpp(runtime, source, output, flags=None, libraries=None):
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    root_config = environment["ROOT_CONFIG"]
    flags = flags or command_tokens(root_config, ["--cflags"], environment,
                                    "ROOT cflags")
    libraries = libraries or command_tokens(root_config, ["--libs"], environment,
                                             "ROOT libs")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp-{}-{}".format(
        os.getpid(), time.time_ns()))
    command = ([environment["CXX"], "-O2", "-std=c++17", "-Wall", "-Wextra",
                "-Wpedantic", str(source), "-I" + str(ROOT / "pipeline/generate")]
               + flags + libraries + ["-o", str(temporary)])
    try:
        subprocess.run(command, env=environment, check=True)
        temporary.chmod(0o700)
        fsync_file(temporary)
        os.replace(str(temporary), str(output))
        fsync_directory(output.parent)
    finally:
        if os.path.lexists(str(temporary)):
            temporary.unlink()
    return command


def build_spec(runtime, source, role):
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    flags = command_tokens(environment["ROOT_CONFIG"], ["--cflags"], environment,
                           "ROOT cflags")
    libraries = command_tokens(environment["ROOT_CONFIG"], ["--libs"], environment,
                               "ROOT libs")
    compiler = Path(shutil.which(environment["CXX"]) or environment["CXX"]).resolve()
    root_config = Path(environment["ROOT_CONFIG"]).resolve()
    regular_file(compiler, "C++ compiler")
    regular_file(root_config, "root-config")
    version = subprocess.run(
        [str(compiler), "--version"], env=environment, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True).stdout.splitlines()
    inputs = [source, ROOT / "pipeline/generate/physics.hpp",
              ROOT / "pipeline/generate/sha256.hpp",
              ROOT / "pipeline/generate/study_contract.hpp"]
    specification = {
        "compiler": {"path": str(compiler), "sha256": sha_file(compiler),
                     "version": version[0] if version else "unknown"},
        "inputs": {str(path.relative_to(ROOT)): sha_file(path) for path in inputs},
        "root": {"cflags": flags, "config_path": str(root_config),
                 "config_sha256": sha_file(root_config), "libs": libraries,
                 "version": next((item.split("=", 1)[1]
                                  for item in runtime["diagnostics"]
                                  if item.startswith("ROOT=")), "unknown")},
        "role": role,
    }
    return specification, flags, libraries


def build_tool(runtime, binary_root, source, role):
    specification, flags, libraries = build_spec(runtime, source, role)
    build_identity = sha_bytes(canonical(specification).encode("utf-8"))
    binary = binary_root / (role + "-" + build_identity[:16])
    receipt_path = binary.with_suffix(".build.json")
    valid = False
    if binary.is_file() and receipt_path.is_file():
        try:
            receipt = json_file(receipt_path)
            exact_keys(receipt, {"binary_sha256", "build_identity", "build_spec",
                                 "schema"}, "tool build receipt")
            valid = (receipt["schema"] == BUILD_SCHEMA and
                     receipt["build_identity"] == build_identity and
                     receipt["build_spec"] == specification and
                     receipt["binary_sha256"] == sha_file(binary))
        except (OSError, ValueError, json.JSONDecodeError):
            valid = False
    if not valid:
        compile_cpp(runtime, source, binary, flags, libraries)
        receipt = {
            "binary_sha256": sha_file(binary),
            "build_identity": build_identity,
            "build_spec": specification,
            "schema": BUILD_SCHEMA,
        }
        atomic_json(receipt_path, receipt)
    else:
        receipt = json_file(receipt_path)
    return binary, {
        "binary_sha256": receipt["binary_sha256"],
        "build_identity": build_identity,
        "build_receipt_sha256": sha_file(receipt_path),
        "source_sha256": sha_file(source),
    }


def build_tools(work_root):
    runtime = runtime_contract.resolve(require_root=True)
    binary_root = work_root / "bin"
    analyzer, analyzer_build = build_tool(
        runtime, binary_root, ANALYSIS_SOURCE, "analyze")
    validator, validator_build = build_tool(
        runtime, binary_root, RAW_VALIDATOR_SOURCE, "validate-raw")
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    return (runtime, environment, analyzer, validator, analyzer_build,
            validator_build)


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
    accepted = campaign["accepted_source"]
    for local_source_id, (entry, raw_path, metadata) in enumerate(
            zip(source_entries, source_paths, source_metadata)):
        row = entry["manifest_row"]
        values = [
            str(local_source_id), str(campaign["seed"]["tune_ordinals"][row["tune"]]),
            str(campaign["seed"]["campaign_ordinal"]),
            str(row["logical_id"]), str(row["accepted_attempt"]),
            str(row["accepted_seed"]), str(row["successful_events"]),
            str(row["bytes"]), str(row["block"]), row["raw_sha256"],
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


def shard_binding(plan, shard, dependency_sha256):
    return {
        "attempt_ledger_sha256": plan["attempt_ledger_sha256"],
        "block_assignment": plan["block_assignment"],
        "campaign": plan["campaign"],
        "campaign_descriptor_sha256": plan["campaign_descriptor_sha256"],
        "lossless_dependency_identity_sha256": dependency_sha256,
        "manifest_sha256": plan["manifest_sha256"],
        "map_digest": plan["map_digest"],
        "plan_digest": plan["plan_digest"],
        "plan_lossless_dependency_identity_sha256":
            plan["lossless_dependency_identity_sha256"],
        "shard_ordinal": shard["ordinal"],
        "source_ids": shard["source_ids"],
        "source_subset_digest": sha_bytes(canonical(
            [plan["sources"][item]["manifest_row"]
             for item in shard["source_ids"]]).encode("utf-8")),
        "target_bytes": plan["target_bytes"],
        "tune_ordinals": plan["tune_ordinals"],
    }


def producer_identity(runtime, analyzer_build, validator_build, pre_hashes):
    return {
        "analyzer": analyzer_build,
        "compiler": next((item.split("=", 1)[1] for item in runtime["diagnostics"]
                          if item.startswith("CXX=")), "unknown"),
        "raw_pre_sha256": pre_hashes,
        "root": next((item.split("=", 1)[1] for item in runtime["diagnostics"]
                      if item.startswith("ROOT=")), "unknown"),
        "validator": validator_build,
    }


def contract_template(plan, shard, campaign, source_entries, runtime,
                      producer, dependency):
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
        "assignment": {"assignment_id": 0,
                       "descriptor": plan["block_assignment"]},
        "axes": "DOWNSTREAM_QUERY_TIME_NOT_SHARD_VALIDITY",
        "binding": shard_binding(plan, shard, sha_bytes(
            canonical(dependency).encode("utf-8"))),
        "campaign_descriptor_digest": plan["campaign_descriptor_sha256"],
        "completion": "COMPLETE_INDEPENDENT_SHARD",
        "compression": {"algorithm": "ZSTD", "level": 5},
        "estimator_slot": "UNCOMPUTED_ANALYZE1",
        "parent_shard_set_digest": "NOT_APPLICABLE_LOSSLESS_SOURCE",
        "profiles": "DOWNSTREAM_QUERY_TIME_NOT_SHARD_VALIDITY",
        "producer_identity": producer,
        "projection_domains": "ALL_DECLARED_LOSSLESS_ROWS",
        "raw_manifest_digest": plan["manifest_sha256"],
        "raw_runtime": "EXACT_PER_SOURCE_METADATA",
        "registries_digest": REGISTRIES_DIGEST,
        "runtime": {"root": next((item.split("=", 1)[1] for item in runtime["diagnostics"]
                                   if item.startswith("ROOT=")), "unknown"),
                    "platform": platform.platform(), "python": platform.python_version()},
        "schema_digest": SCHEMA_DIGEST,
        "schema": WORKER_SCHEMA,
        "scientific_content_digest": "X" * 64,
        "source_scientific_digests": "__SOURCE_DIGESTS__",
        "shard_map": {"map_digest": plan["map_digest"],
                      "ordinal": shard["ordinal"],
                      "source_ids": shard["source_ids"],
                      "target_bytes": plan["target_bytes"]},
        "source_metadata": "__SOURCE_METADATA__",
        "source_subset_digest": sha_bytes(canonical(
            [entry["manifest_row"] for entry in source_entries]).encode("utf-8")),
        "lossless_dependency_identity": dependency,
        "lossless_dependency_identity_sha256": sha_bytes(
            canonical(dependency).encode("utf-8")),
        "streaming": {"aggregate_autoflush_bytes": 67108864,
                      "basket_bytes": 32768, "event_flush_interval": 8192,
                      "per_tree_autoflush_bytes": 4194304},
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


def receipt_for(plan, shard, entries, output, digest, rows, source_digests,
                dependency, producer, elapsed, publication_mode):
    dependency_sha256 = sha_bytes(canonical(dependency).encode("utf-8"))
    scientific = {
        "lossless_dependency_identity": dependency,
        "lossless_dependency_identity_sha256": dependency_sha256,
        "raw_mapping_digest": RAW_MAPPING_DIGEST,
        "raw_schema": dependency["raw_schema"],
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
        "producer_identity": producer,
        "publication": {"elapsed_seconds": elapsed, "host": platform.node(),
                        "mode": publication_mode},
    }
    return {
        "schema": RECEIPT_SCHEMA, "state": "PASS",
        "campaign": plan["campaign"], "plan_digest": plan["plan_digest"],
        "map_digest": plan["map_digest"], "shard_ordinal": shard["ordinal"],
        "binding": shard_binding(plan, shard, dependency_sha256),
        "sources": entries, "rows": rows,
        "scientific_identity": scientific,
        "scientific_identity_sha256": sha_bytes(canonical(scientific).encode("utf-8")),
        "storage_identity": storage,
        "storage_identity_sha256": sha_bytes(canonical(storage).encode("utf-8")),
        "producer_provenance": provenance,
        "producer_provenance_sha256": sha_bytes(
            canonical(provenance).encode("utf-8")),
    }


def inspect_root_binding(analyzer, environment, root_path):
    completed = subprocess.run([str(analyzer), "binding", str(root_path)],
                               env=environment, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode:
        raise ValueError("ROOT contract inspection failed: {}".format(
            completed.stderr.strip()))
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ValueError("ROOT contract is not structural JSON") from error
    exact_keys(value, {"contract", "event_ranges", "source_blocks", "sources"},
               "ROOT binding inspection")
    return value


def event_id(campaign_ordinal, tune_ordinal, logical_id, attempt, local_success):
    for value, low, high, label in (
            (campaign_ordinal, 0, 65535, "campaign ordinal"),
            (tune_ordinal, 0, 3, "tune ordinal"),
            (logical_id, 0, 16383, "logical ID"),
            (attempt, 0, 4095, "attempt"),
            (local_success, 0, (1 << 20) - 1, "local success")):
        bounded_int(value, low, high, label)
    return ((campaign_ordinal << 48) | (tune_ordinal << 46) |
            (logical_id << 32) | (attempt << 20) | local_success)


def validate_dictionary(dictionary, kind):
    if not isinstance(dictionary, dict):
        raise ValueError("ROOT {} dictionary differs".format(kind))
    for identity, payload in dictionary.items():
        lower_sha256(identity, "ROOT {} dictionary key".format(kind))
        if kind == "effective_settings":
            exact_keys(payload, {"canonical", "changed"},
                       "ROOT effective-settings dictionary payload")
            content = payload["canonical"]
            if not isinstance(payload["changed"], str):
                raise ValueError("ROOT effective-settings changed payload differs")
        elif kind == "heavy_stability":
            exact_keys(payload, {"canonical"},
                       "ROOT heavy-stability dictionary payload")
            content = payload["canonical"]
        else:
            content = payload
        if not isinstance(content, str) or sha_bytes(content.encode("utf-8")) != identity:
            raise ValueError("ROOT {} dictionary key/payload collision".format(kind))


def metadata_value(metadata, name):
    value = metadata.get(name)
    if not isinstance(value, dict) or set(value) != {"type", "value"}:
        raise ValueError("ROOT original raw metadata field differs: {}".format(name))
    return value["value"]


def validate_root_contract(binding_view, receipt, root_summary, plan=None, shard=None):
    contract = binding_view["contract"]
    expected_contract_fields = {
        "accepted_study_digest", "activity_definitions", "assignment", "axes",
        "binding", "campaign_descriptor_digest", "completion", "compression",
        "estimator_slot", "lossless_dependency_identity",
        "lossless_dependency_identity_sha256", "parent_shard_set_digest", "profiles",
        "producer_identity", "projection_domains", "raw_manifest_digest",
        "raw_runtime", "registries_digest", "runtime", "schema", "schema_digest",
        "scientific_content_digest", "shard_map", "source_metadata",
        "source_scientific_digests", "source_subset_digest", "streaming",
        "study_interpretation_digest",
    }
    exact_keys(contract, expected_contract_fields, "ROOT contract")
    if (contract["schema"] != WORKER_SCHEMA or
            contract["completion"] != "COMPLETE_INDEPENDENT_SHARD" or
            contract["schema_digest"] != SCHEMA_DIGEST or
            contract["registries_digest"] != REGISTRIES_DIGEST or
            contract["compression"] != {"algorithm": "ZSTD", "level": 5}):
        raise ValueError("ROOT contract static identity/completion differs")
    if contract["streaming"] != {
            "aggregate_autoflush_bytes": 67108864, "basket_bytes": 32768,
            "event_flush_interval": 8192, "per_tree_autoflush_bytes": 4194304}:
        raise ValueError("ROOT streaming policy differs")
    dependency = contract["lossless_dependency_identity"]
    exact_keys(dependency, {"accepted_raw_definition",
                            "campaign_lossless_identity_sha256",
                            "campaign_namespace", "raw_mapping_digest", "raw_schema",
                            "raw_source_subset_digest", "registries_digest", "schema",
                            "schema_digest"}, "ROOT lossless dependency identity")
    dependency_sha256 = sha_bytes(canonical(dependency).encode("utf-8"))
    if (contract["lossless_dependency_identity_sha256"] != dependency_sha256 or
            dependency["schema"] != DEPENDENCY_SCHEMA or
            dependency["schema_digest"] != SCHEMA_DIGEST or
            dependency["registries_digest"] != REGISTRIES_DIGEST or
            dependency["raw_mapping_digest"] != RAW_MAPPING_DIGEST or
            dependency["raw_schema"] != "hf_primary_ground_raw_v7"):
        raise ValueError("ROOT lossless dependency identity differs")

    scientific = receipt["scientific_identity"]
    digest, rows, source_digests = root_summary
    if (contract["scientific_content_digest"] != digest or
            contract["source_scientific_digests"] != source_digests or
            contract["lossless_dependency_identity"] !=
            scientific["lossless_dependency_identity"] or
            contract["lossless_dependency_identity_sha256"] !=
            scientific["lossless_dependency_identity_sha256"]):
        raise ValueError("ROOT contract scientific/dependency binding differs")
    if rows != receipt["rows"]:
        raise ValueError("ROOT row counts differ from receipt")
    if contract["binding"] != receipt["binding"]:
        raise ValueError("ROOT contract binding differs from receipt")
    receipt_binding = receipt["binding"]
    if (contract["campaign_descriptor_digest"] !=
            receipt_binding["campaign_descriptor_sha256"] or
            contract["raw_manifest_digest"] != receipt_binding["manifest_sha256"] or
            contract["source_subset_digest"] != receipt_binding["source_subset_digest"] or
            contract["assignment"] != {"assignment_id": 0,
                                       "descriptor": receipt_binding["block_assignment"]}):
        raise ValueError("ROOT contract duplicated campaign/source fields differ")
    if contract["shard_map"] != {
            "map_digest": receipt_binding["map_digest"],
            "ordinal": receipt_binding["shard_ordinal"],
            "source_ids": receipt_binding["source_ids"],
            "target_bytes": receipt_binding["target_bytes"]}:
        raise ValueError("ROOT contract shard-map binding differs")
    if contract["producer_identity"] != receipt["producer_provenance"]["producer_identity"]:
        raise ValueError("ROOT executable provenance differs from receipt")
    if plan is not None:
        expected_binding = shard_binding(
            plan, shard, scientific["lossless_dependency_identity_sha256"])
        if receipt_binding != expected_binding:
            raise ValueError("ROOT/receipt binding differs from plan")

    source_metadata = contract["source_metadata"]
    exact_keys(source_metadata, {"dictionaries", "sources"}, "ROOT source metadata")
    dictionaries = source_metadata["dictionaries"]
    exact_keys(dictionaries, {"effective_settings", "heavy_stability",
                              "pythia_statistics"}, "ROOT source dictionaries")
    for kind, dictionary in dictionaries.items():
        validate_dictionary(dictionary, kind)
    metadata_sources = source_metadata["sources"]
    root_sources = binding_view["sources"]
    root_blocks = binding_view["source_blocks"]
    root_ranges = binding_view["event_ranges"]
    if not all(isinstance(value, list) for value in
               (metadata_sources, root_sources, root_blocks, root_ranges)):
        raise ValueError("ROOT source binding rows differ")
    if not (len(metadata_sources) == len(receipt["sources"]) == len(root_sources) ==
            len(root_blocks) == len(root_ranges)):
        raise ValueError("ROOT source binding cardinality differs")
    raw_identity_rows = []
    metadata_fields = {
        "accepted_attempt", "accepted_seed", "attempt_ledger_identity",
        "attempted_exposure_availability", "campaign_identity",
        "effective_settings_identity", "logical_id", "manifest_row",
        "original_raw_metadata", "pythia_statistics_identity", "raw_bytes",
        "raw_object_cycles", "raw_sha256", "raw_storage_key", "source_id",
        "stability_identity", "tune", "validation_log_sha256",
        "validation_receipt_sha256",
    }
    for local_id, (entry, metadata, root_source, root_block, root_range) in enumerate(
            zip(receipt["sources"], metadata_sources, root_sources, root_blocks,
                root_ranges)):
        row = entry["manifest_row"]
        exact_keys(metadata, metadata_fields, "ROOT source metadata row")
        if (metadata["source_id"] != local_id or metadata["manifest_row"] != row or
                metadata["campaign_identity"] != receipt["campaign"] or
                metadata["tune"] != row["tune"] or
                metadata["logical_id"] != row["logical_id"] or
                metadata["accepted_attempt"] != row["accepted_attempt"] or
                metadata["accepted_seed"] != row["accepted_seed"] or
                metadata["raw_bytes"] != row["bytes"] or
                metadata["raw_sha256"] != row["raw_sha256"] or
                metadata["raw_storage_key"] != row["raw_storage_key"] or
                metadata["validation_log_sha256"] != row["validation_log_sha256"] or
                metadata["validation_receipt_sha256"] !=
                row["validation_receipt_sha256"] or
                metadata["attempt_ledger_identity"] !=
                receipt_binding["attempt_ledger_sha256"]):
            raise ValueError("ROOT source metadata/receipt cross-binding differs")
        for identity_name, dictionary_name in (
                ("effective_settings_identity", "effective_settings"),
                ("stability_identity", "heavy_stability"),
                ("pythia_statistics_identity", "pythia_statistics")):
            if metadata[identity_name] not in dictionaries[dictionary_name]:
                raise ValueError("ROOT source dictionary reference is unresolved")
        original = metadata["original_raw_metadata"]
        if (metadata_value(original, "campaign") != receipt["campaign"] or
                metadata_value(original, "tune") != row["tune"] or
                int(metadata_value(original, "logical_id")) != row["logical_id"] or
                int(metadata_value(original, "attempt")) != row["accepted_attempt"] or
                int(metadata_value(original, "seed")) != row["accepted_seed"] or
                int(metadata_value(original, "successful_events")) !=
                row["successful_events"] or
                metadata_value(original, "raw_schema") != dependency["raw_schema"] or
                metadata_value(original, "effective_settings_sha256") !=
                metadata["effective_settings_identity"]):
            raise ValueError("ROOT original raw metadata cross-binding differs")
        expected_tune_ordinal = receipt_binding["tune_ordinals"][row["tune"]]
        exact_keys(root_source, {"attempt", "events", "logical_id", "source_id", "tune"},
                   "ROOT sources binding row")
        exact_keys(root_block, {"assignment_id", "block", "source_id"},
                   "ROOT source_blocks binding row")
        exact_keys(root_range, {"count", "first_id", "source_id"},
                   "ROOT event_ranges binding row")
        campaign_ordinal = int(metadata_value(original, "campaign_ordinal"))
        if (root_source != {"attempt": row["accepted_attempt"],
                            "events": row["successful_events"],
                            "logical_id": row["logical_id"], "source_id": local_id,
                            "tune": expected_tune_ordinal} or
                root_block != {"assignment_id": 0, "block": row["block"],
                               "source_id": local_id} or
                root_range != {"count": row["successful_events"],
                               "first_id": event_id(campaign_ordinal,
                                                    expected_tune_ordinal,
                                                    row["logical_id"],
                                                    row["accepted_attempt"], 0),
                               "source_id": local_id}):
            raise ValueError("ROOT source/block/event-range rows differ from contract sources")
        raw_identity_rows.append({key: value for key, value in row.items()
                                  if key != "block"})
    if dependency["raw_source_subset_digest"] != sha_bytes(
            canonical(raw_identity_rows).encode("utf-8")):
        raise ValueError("ROOT lossless raw-source subset differs")


def verify_receipt(receipt_path, root_path, plan=None, shard=None,
                   analyzer=None, environment=None, root_summary=None,
                   binding_view=None):
    regular_file(receipt_path, "shard receipt")
    regular_file(root_path, "analysis shard")
    receipt = json_file(receipt_path)
    exact_keys(receipt, {"schema", "state", "campaign", "plan_digest",
                         "map_digest", "shard_ordinal", "binding", "sources", "rows",
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
    exact_keys(scientific, {"lossless_dependency_identity",
                            "lossless_dependency_identity_sha256",
                            "raw_mapping_digest", "raw_schema", "schema_digest",
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
            scientific["lossless_dependency_identity_sha256"] != sha_bytes(
                canonical(scientific["lossless_dependency_identity"]).encode("utf-8")) or
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
    binding = receipt["binding"]
    exact_keys(binding, {"attempt_ledger_sha256", "block_assignment", "campaign",
                         "campaign_descriptor_sha256",
                         "lossless_dependency_identity_sha256", "manifest_sha256",
                         "map_digest", "plan_digest",
                         "plan_lossless_dependency_identity_sha256", "shard_ordinal",
                         "source_ids", "source_subset_digest", "target_bytes",
                         "tune_ordinals"}, "receipt binding")
    if (binding["campaign"] != receipt["campaign"] or
            binding["plan_digest"] != receipt["plan_digest"] or
            binding["map_digest"] != receipt["map_digest"] or
            binding["shard_ordinal"] != receipt["shard_ordinal"] or
            binding["source_ids"] != source_ids or
            binding["source_subset_digest"] != scientific["source_subset_digest"] or
            binding["lossless_dependency_identity_sha256"] !=
            scientific["lossless_dependency_identity_sha256"] or
            storage["map_digest"] != binding["map_digest"] or
            storage["shard_ordinal"] != binding["shard_ordinal"] or
            storage["target_bytes"] != binding["target_bytes"]):
        raise ValueError("receipt duplicated binding fields differ")
    provenance = receipt["producer_provenance"]
    exact_keys(provenance, {"producer_identity", "publication"},
               "producer provenance")
    if receipt["producer_provenance_sha256"] != sha_bytes(
            canonical(provenance).encode("utf-8")):
        raise ValueError("producer provenance digest mismatch")
    producer = provenance["producer_identity"]
    exact_keys(producer, {"analyzer", "compiler", "raw_pre_sha256", "root",
                          "validator"}, "producer identity")
    for role in ("analyzer", "validator"):
        exact_keys(producer[role], {"binary_sha256", "build_identity",
                                    "build_receipt_sha256", "source_sha256"},
                   "producer {} identity".format(role))
        for key in ("binary_sha256", "build_identity", "build_receipt_sha256",
                    "source_sha256"):
            lower_sha256(producer[role][key], "producer {} {}".format(role, key))
    publication = provenance["publication"]
    exact_keys(publication, {"elapsed_seconds", "host", "mode"},
               "receipt publication provenance")
    if (not isinstance(publication["elapsed_seconds"], (int, float)) or
            publication["elapsed_seconds"] < 0 or
            not isinstance(publication["host"], str) or
            publication["mode"] not in {"normal", "root_only_recovery"}):
        raise ValueError("receipt publication provenance differs")
    expected_raw = {row["raw_storage_key"]: row["raw_sha256"]
                    for row in source_rows}
    if producer["raw_pre_sha256"] != expected_raw:
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
    if root_summary is None:
        if analyzer is None or environment is None:
            raise ValueError("ROOT semantic verifier is required")
        completed = subprocess.run([str(analyzer), "verify", str(root_path)],
                                   env=environment, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.returncode:
            raise ValueError("ROOT shard verification failed: {}".format(
                completed.stderr.strip()))
        root_summary = worker_summary(completed.stdout)
    digest, rows, source_digests = root_summary
    if digest != scientific.get("scientific_content_digest"):
        raise ValueError("ROOT scientific digest differs from receipt")
    if rows != receipt.get("rows"):
        raise ValueError("ROOT row counts differ from receipt")
    if source_digests != scientific.get("source_scientific_digests"):
        raise ValueError("ROOT source scientific digests differ from receipt")
    if binding_view is None:
        if analyzer is None or environment is None:
            raise ValueError("ROOT contract inspector is required")
        binding_view = inspect_root_binding(analyzer, environment, root_path)
    validate_root_contract(binding_view, receipt, root_summary, plan, shard)
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


def recover_root_only(plan, shard, final_root, final_receipt, campaign,
                      analyzer, environment, work_root):
    entries = [plan["sources"][source_id] for source_id in shard["source_ids"]]
    completed = subprocess.run([str(analyzer), "verify", str(final_root)],
                               env=environment, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode:
        raise RuntimeError("root-only promotion recovery rejected: {}".format(
            completed.stderr.strip()))
    summary = worker_summary(completed.stdout)
    binding_view = inspect_root_binding(analyzer, environment, final_root)
    dependency = binding_view["contract"].get("lossless_dependency_identity")
    producer = binding_view["contract"].get("producer_identity")
    if not isinstance(dependency, dict) or not isinstance(producer, dict):
        raise RuntimeError("root-only promotion recovery lacks bound provenance")
    fsync_file(final_root)
    receipt = receipt_for(plan, shard, entries, final_root, summary[0], summary[1],
                          summary[2], dependency, producer, 0.0,
                          "root_only_recovery")
    stage = work_root / "staging" / "recovery-{:04d}-{}-{}".format(
        shard["ordinal"], os.getpid(), time.time_ns())
    stage.mkdir(parents=True, mode=0o700)
    try:
        staged_receipt = stage / "shard.json"
        atomic_json(staged_receipt, receipt, exclusive=True)
        verify_receipt(staged_receipt, final_root, plan, shard, analyzer,
                       environment, root_summary=summary,
                       binding_view=binding_view)
        link_no_overwrite(staged_receipt, final_receipt)
        fsync_directory(final_receipt.parent)
        staged_receipt.unlink()
    finally:
        shutil.rmtree(str(stage), ignore_errors=True)
    return "RECOVERED shard={} root={} receipt={}".format(
        shard["ordinal"], final_root, final_receipt)


def produce_one(plan, shard, campaign, attempts, attempt_digest, runtime,
                environment, analyzer, validator, raw_root, work_root,
                campaign_output, resume, analyzer_build, validator_build):
    ordinal = shard["ordinal"]
    final_root = campaign_output / "shard-{:04d}.root".format(ordinal)
    final_receipt = campaign_output / "shard-{:04d}.json".format(ordinal)
    root_exists = final_root.exists()
    receipt_exists = final_receipt.exists()
    if root_exists and not receipt_exists:
        if not resume or not final_root.is_file():
            raise FileExistsError("foreign or partial final collision for shard {}".format(ordinal))
        return recover_root_only(plan, shard, final_root, final_receipt, campaign,
                                 analyzer, environment, work_root)
    if root_exists or receipt_exists:
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
        adapter = campaign_adapter(campaign)
        dependency = lossless_dependency_identity(
            campaign, adapter, [entry["manifest_row"] for entry in entries])
        producer = producer_identity(runtime, analyzer_build, validator_build,
                                     pre_hashes)
        atomic_json(contract, contract_template(
            plan, shard, campaign, entries, runtime, producer, dependency),
            exclusive=True)
        started = time.monotonic()
        completed = subprocess.run([str(analyzer), "write", str(spec),
                                    str(staged_root), str(contract)],
                                   env=environment, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.returncode:
            raise RuntimeError("analysis worker rejected shard {}: {}".format(
                ordinal, completed.stderr.strip()))
        digest, rows, source_digests = worker_summary(completed.stdout)
        root_summary = (digest, rows, source_digests)
        binding_view = inspect_root_binding(analyzer, environment, staged_root)
        receipt = receipt_for(plan, shard, entries, staged_root, digest,
                              rows, source_digests, dependency, producer,
                              time.monotonic() - started, "normal")
        for entry, path in zip(entries, paths):
            row = entry["manifest_row"]
            if path.stat().st_size != row["bytes"] or sha_file(path) != row["raw_sha256"]:
                raise RuntimeError("raw source changed during analysis: {}".format(path))
        fsync_file(staged_root)
        atomic_json(staged_receipt, receipt, exclusive=True)
        verify_receipt(staged_receipt, staged_root, plan, shard, analyzer,
                       environment, root_summary=root_summary,
                       binding_view=binding_view)
        campaign_output_preexisted = campaign_output.exists()
        campaign_output.mkdir(parents=True, exist_ok=True)
        if not campaign_output_preexisted:
            fsync_directory(campaign_output.parent)
        link_no_overwrite(staged_root, final_root)
        fsync_directory(campaign_output)
        if os.environ.get("HADRONIZATION_ANALYZE_FAIL_AFTER_ROOT_PROMOTION") == "1":
            raise RuntimeError("injected interruption after ROOT promotion")
        link_no_overwrite(staged_receipt, final_receipt)
        fsync_directory(campaign_output)
        staged_root.unlink()
        staged_receipt.unlink()
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
    adapter = campaign_adapter(campaign)
    manifest = load_manifest(Path(plan["manifest"]), campaign, adapter)
    manifest_encodings = {canonical(row) for row in manifest}
    if (len(plan["sources"]) != len({canonical(source["manifest_row"])
                                     for source in plan["sources"]}) or
            any(canonical(source["manifest_row"]) not in manifest_encodings
                for source in plan["sources"])):
        raise ValueError("planned source subset is not authorized by the manifest")
    attempts, attempt_digest = load_attempts(Path(plan["attempts"]))
    validate_attempts(campaign, adapter, manifest, attempts)
    (runtime, environment, analyzer, validator, analyzer_build,
     validator_build) = build_tools(work_root)
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
            args.resume, analyzer_build, validator_build) for shard in shards]
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
        (runtime, environment, analyzer, unused, analyzer_build,
         validator_build) = build_tools(work_root)
        del runtime, unused, analyzer_build, validator_build
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
    (runtime, environment, analyzer, unused, analyzer_build,
     validator_build) = build_tools(work_root)
    del runtime, unused, analyzer_build, validator_build
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
    work_root = Path(args.work_root or ROOT / "data/work/analyze").resolve(strict=False)
    raw_root = Path(args.raw_root or ROOT / "data/raw").resolve(strict=False)
    output_root = receipt_path.parent.parent.resolve(strict=False)
    unused_raw, work_root, unused_output = safe_roots(raw_root, work_root, output_root)
    del unused_raw, unused_output
    (runtime, environment, analyzer, unused, analyzer_build,
     validator_build) = build_tools(work_root)
    del runtime, unused, analyzer_build, validator_build
    receipt = verify_receipt(receipt_path, receipt_path.with_suffix(".root"),
                             analyzer=analyzer, environment=environment)
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
    explain_parser.add_argument("--raw-root", type=Path)
    explain_parser.add_argument("--work-root", type=Path)
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
