#!/usr/bin/env python3
"""Build the immutable aggregate publication Gate-B decision.

Gate B is intentionally an evidence aggregator, not an approval mechanism.
It validates the exact nine-row pilot campaign, the scheduler submission
claim/record, every raw file and immutable PASS validation receipt, and the
predeclared pTHat decision.  It also runs the independent cross-tune settings,
origin-resolution, and unresolved-origin audits on the three million-event
central pilots.

The output directory is write-once.  It is assembled under a private staging
directory, sealed read-only, and atomically renamed into place.  A nonzero
publication-trigger unresolved count produces NEEDS_SIGNOFF; this program
never creates or accepts a physics sign-off.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import math
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


REPORT_SCHEMA = "hf_publication_gate_b_report_v1"
CAMPAIGN_SCHEMA = "hf_gate_b_pilot_campaign_v1"
RAW_RECEIPT_SCHEMA = "hf_raw_validation_receipt_v1"
PTHAT_REPORT_SCHEMA = "hf_gate_b_pthat_sensitivity_report_v1"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
PROFILES = {
    0: ("1.0", 1_000_000, "long", "one_million_central"),
    1: ("0.5", 100_000, "medium", "pthat_sensitivity_low"),
    2: ("2.0", 100_000, "medium", "pthat_sensitivity_high"),
}
RAW_SCHEMA = "hf_primary_ground_raw_v6"
SELECTOR = "hard_trigger_primary_ground__primary_ground_associate_v1"
ORIGIN_ALGORITHM = "signed_heavy_constituent_complete_mothers_unique_v4"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SAFE_TOKEN = re.compile(r"^[A-Za-z0-9._-]+$")
CONDOR_SUBMISSION_ATTRIBUTES = (
    "ClusterId",
    "ProcId",
    "JobStatus",
    "Cmd",
    "Iwd",
    "Args",
    "HFCampaign",
    "HFCampaignOrdinal",
    "HFTune",
    "HFLogicalId",
    "HFRole",
    "HFAttempt",
    "HFSeed",
    "HFRequestedSuccesses",
    "HFPTHat",
    "HFMultiplicityAuditEvents",
    "HFRepositoryCommit",
    "HFEffectiveCardSHA256",
    "HFProducerExecutableSHA256",
)
RAW_SUMMARY = re.compile(
    r"^RAW_VALIDATION_SUMMARY errors=0 entries=(\d+) "
    r"process_codes=(\d+) stability_rows=(\d+)\s*$",
    flags=re.MULTILINE,
)
RAW_ORIGIN = re.compile(
    r"^RAW_ORIGIN_AUDIT "
    r"unresolved_charm_trigger_candidates=(\d+) "
    r"unresolved_beauty_trigger_candidates=(\d+) "
    r"resolved_nonhard_charm_trigger_candidates=(\d+) "
    r"resolved_nonhard_beauty_trigger_candidates=(\d+) "
    r"duplicate_hard_carrier_groups_charm=(\d+) "
    r"duplicate_hard_carrier_groups_beauty=(\d+) "
    r"duplicate_hard_carrier_demotions_charm=(\d+) "
    r"duplicate_hard_carrier_demotions_beauty=(\d+) "
    r"multi_heavy_rejections_charm=(\d+) "
    r"multi_heavy_rejections_beauty=(\d+)\s*$",
    flags=re.MULTILINE,
)
ORIGIN_SUMMARY = re.compile(
    r"^ORIGIN_RESOLUTION_SUMMARY tune=(\S+) role=(\S+) sector=(\S+) "
    r"candidates=(\d+) unresolved=(\d+) "
    r"unresolved_fraction=(\S+) unresolved_fraction_defined=([01]) "
    r"sum_weights=(\S+) "
    r"unresolved_sum_weights=(\S+) "
    r"weighted_unresolved_fraction=(\S+) "
    r"weighted_unresolved_fraction_defined=([01])\s*$",
    flags=re.MULTILINE,
)
UNRESOLVED_SUMMARY = re.compile(
    r"^UNRESOLVED_SUMMARY tune=(\S+) role_sector=(\S+) "
    r"candidates=(\d+) sum_weights=(\S+) sum_weights2=(\S+) "
    r"effective_entries=(\S+) effective_entries_defined=([01])\s*$",
    flags=re.MULTILINE,
)
RESOURCE_SUMMARY = re.compile(
    r"^GATE_B_RESOURCE tune=(\S+) logical_id=(\d+) "
    r"successful_events=(\d+) peak_rss_kib=(\d+) file_bytes=(\d+) "
    r"compression_settings=(-?\d+) compression_algorithm=(-?\d+) "
    r"compression_level=(-?\d+) compression_factor=(\S+) "
    r"stability_schema=(\S+) stability_sha256=([0-9a-f]{64}) "
    r"stability_rows=(\d+) settings_schema=(\S+) "
    r"settings_sha256=([0-9a-f]{64})\s*$",
    flags=re.MULTILINE,
)


class GateFailure(ValueError):
    """A fail-closed validation failure."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    require_regular(path, label)
    try:
        payload = json.loads(path.read_text())
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise GateFailure(f"{label} is not valid JSON: {path}") from error
    if not isinstance(payload, dict):
        raise GateFailure(f"{label} is not a JSON object: {path}")
    require_finite_json(payload, label)
    return payload


def load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    require_regular(path, label)
    rows: list[dict[str, Any]] = []
    try:
        for number, line in enumerate(path.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise GateFailure(f"{label} line {number} is not an object")
            require_finite_json(value, f"{label} line {number}")
            rows.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise GateFailure(f"{label} is not valid JSON Lines: {path}") from error
    return rows


def require_finite_json(value: Any, label: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise GateFailure(f"{label} contains a non-finite number")
    if isinstance(value, list):
        for item in value:
            require_finite_json(item, label)
    elif isinstance(value, dict):
        for item in value.values():
            require_finite_json(item, label)


def require_regular(path: Path, label: str) -> Path:
    if path.is_symlink() or not path.is_file():
        raise GateFailure(f"{label} is absent, non-regular, or a symlink: {path}")
    return path


def require_read_only_regular(path: Path, label: str) -> Path:
    require_regular(path, label)
    details = path.stat()
    if details.st_nlink != 1 or stat.S_IMODE(details.st_mode) & 0o222:
        raise GateFailure(
            f"{label} is not a single-link read-only immutable file: {path}"
        )
    return path


def require_directory(path: Path, label: str) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise GateFailure(f"{label} is absent, non-directory, or a symlink: {path}")
    return path


def require_exact(
    payload: dict[str, Any], expected: dict[str, Any], label: str
) -> None:
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            raise GateFailure(
                f"{label} {key}={payload.get(key)!r}, "
                f"expected {expected_value!r}"
            )


def require_utc_timestamp(value: Any, label: str) -> datetime.datetime:
    if not isinstance(value, str) or not value:
        raise GateFailure(f"{label} timestamp is absent")
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except ValueError as error:
        raise GateFailure(f"{label} timestamp is not ISO-8601") from error
    if (
        parsed.tzinfo is None
        or parsed.utcoffset() != datetime.timedelta(0)
    ):
        raise GateFailure(f"{label} timestamp is not explicitly UTC")
    return parsed


def git_output(checkout: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(checkout), *arguments],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except subprocess.CalledProcessError as error:
        raise GateFailure(
            f"git {' '.join(arguments)} failed: {error.stdout.strip()}"
        ) from error


def validate_checkout(
    checkout: Path, allowed_untracked_roots: Iterable[Path]
) -> tuple[str, list[str]]:
    checkout = checkout.resolve()
    git_control = checkout / ".git"
    if git_control.is_symlink() or not (
        git_control.is_dir() or git_control.is_file()
    ):
        raise GateFailure("checkout .git control path is absent or a symlink")
    commit = git_output(checkout, "rev-parse", "HEAD")
    if not HEX40.fullmatch(commit):
        raise GateFailure("checkout HEAD is not a lowercase 40-hex commit")
    changed = git_output(checkout, "diff", "--name-only", "HEAD", "--")
    if changed:
        raise GateFailure(
            "Gate-B aggregate requires a tracked-clean checkout; "
            f"first changed tracked path: {changed.splitlines()[0]}"
        )
    allowed: list[Path] = []
    for root in allowed_untracked_roots:
        resolved = root.resolve()
        try:
            resolved.relative_to(checkout)
        except ValueError as error:
            raise GateFailure(
                f"allowed operational path is outside checkout: {resolved}"
            ) from error
        allowed.append(resolved)
    raw_untracked = subprocess.check_output(
        [
            "git",
            "-C",
            str(checkout),
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
        ]
    )
    untracked = sorted(
        entry.decode("utf-8", errors="strict")
        for entry in raw_untracked.split(b"\0")
        if entry
    )
    for relative in untracked:
        candidate = (checkout / relative).resolve()
        if not any(
            candidate == root or candidate.is_relative_to(root)
            for root in allowed
        ):
            raise GateFailure(
                "untracked path is not whitelisted Gate-B operational "
                f"evidence: {relative}"
            )
    return commit, untracked


def canonical_paths(
    checkout: Path, campaign_dir: Path, production: Path, campaign: dict[str, Any]
) -> None:
    name = campaign.get("campaign")
    if not isinstance(name, str) or not SAFE_TOKEN.fullmatch(name):
        raise GateFailure("campaign name is absent or unsafe")
    expected_campaign = (checkout / "campaigns" / name).resolve()
    expected_production = (checkout / "Production" / name).resolve()
    if campaign_dir.resolve() != expected_campaign:
        raise GateFailure(
            f"campaign directory is noncanonical: {campaign_dir} != "
            f"{expected_campaign}"
        )
    if production.resolve() != expected_production:
        raise GateFailure(
            f"production directory is noncanonical: {production} != "
            f"{expected_production}"
        )


def validate_campaign(
    checkout: Path, campaign_dir: Path, production: Path, commit: str
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[tuple[str, int], dict[str, Any]]]:
    campaign_path = campaign_dir / "campaign.json"
    candidates_path = campaign_dir / "candidate_manifest.jsonl"
    ledger_path = campaign_dir / "seed_ledger.jsonl"
    campaign = load_json(campaign_path, "Gate-B campaign manifest")
    canonical_paths(checkout, campaign_dir, production, campaign)
    require_exact(
        campaign,
        {
            "schema": CAMPAIGN_SCHEMA,
            "repository_commit": commit,
            "repository_implementation_commit": commit,
            "repository_dirty_at_generation": False,
            "raw_schema": RAW_SCHEMA,
            "selector": SELECTOR,
            "origin_algorithm": ORIGIN_ALGORITHM,
            "pilot_jobs": 9,
        },
        "Gate-B campaign",
    )
    ordinal = campaign.get("campaign_ordinal")
    seed_base = campaign.get("seed_base")
    if (
        isinstance(ordinal, bool)
        or not isinstance(ordinal, int)
        or not 1 <= ordinal <= 65_535
        or isinstance(seed_base, bool)
        or not isinstance(seed_base, int)
        or seed_base < 1
    ):
        raise GateFailure("campaign ordinal or seed base is invalid")

    hash_contract = {
        "pthat_sensitivity_spec_sha256": "config/pthat_sensitivity_v1.json",
        "species_registry_sha256": "config/heavy_flavour_species_v1.json",
        "pair_registry_sha256": "config/heavy_flavour_pair_registry_v1.json",
        "tune_allowlist_sha256": "config/tune_difference_allowlist_v1.json",
    }
    for field, relative in hash_contract.items():
        path = require_regular(checkout / relative, relative)
        if campaign.get(field) != sha256(path):
            raise GateFailure(f"campaign {field} differs from clean checkout")
    for tune in TUNES:
        card = require_regular(
            checkout
            / "SimulationScripts"
            / f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd",
            f"{tune} tune card",
        )
        if campaign.get("card_sha256", {}).get(tune) != sha256(card):
            raise GateFailure(f"campaign card checksum differs for {tune}")

    rows = load_jsonl(candidates_path, "Gate-B candidate manifest")
    ledger = load_jsonl(ledger_path, "Gate-B seed ledger")
    if len(rows) != 9 or len(ledger) != 9:
        raise GateFailure("Gate-B campaign must contain exactly nine rows")
    selected: dict[tuple[str, int], dict[str, Any]] = {}
    seeds: set[int] = set()
    for tune_index, tune in enumerate(TUNES):
        for logical_id, (pthat, events, category, purpose) in PROFILES.items():
            matching = [
                row
                for row in rows
                if row.get("tune") == tune
                and row.get("logical_id") == logical_id
            ]
            if len(matching) != 1:
                raise GateFailure(
                    f"Gate-B manifest identity {tune}/{logical_id} is "
                    "missing or duplicated"
                )
            row = matching[0]
            expected_seed = seed_base + tune_index * 10_000 + logical_id * 1_000
            require_exact(
                row,
                {
                    "campaign": campaign["campaign"],
                    "campaign_ordinal": ordinal,
                    "tune": tune,
                    "logical_id": logical_id,
                    "role": "pilot",
                    "attempt": 0,
                    "seed": expected_seed,
                    "requested_successes": events,
                    "pthat_min_override": pthat,
                    "category": category,
                    "purpose": purpose,
                    "multiplicity_audit_events": 100,
                    "stable_name": f"hf_{tune}_job{logical_id:03d}.root",
                    "repository_commit": commit,
                },
                f"Gate-B row {tune}/{logical_id}",
            )
            effective_sha = row.get("effective_card_sha256")
            if not isinstance(effective_sha, str) or not HEX64.fullmatch(effective_sha):
                raise GateFailure(
                    f"Gate-B row {tune}/{logical_id} effective-card SHA is invalid"
                )
            if expected_seed in seeds or not 1 <= expected_seed <= 900_000_000:
                raise GateFailure("Gate-B seeds are duplicated or outside PYTHIA range")
            seeds.add(expected_seed)
            selected[(tune, logical_id)] = row
    if len(selected) != len(rows):
        raise GateFailure("Gate-B manifest contains unexpected rows")
    expected_ledger = {
        (
            row["campaign"],
            row["tune"],
            int(row["logical_id"]),
            int(row["attempt"]),
            int(row["seed"]),
        )
        for row in rows
    }
    actual_ledger = {
        (
            row.get("campaign"),
            row.get("tune"),
            int(row.get("logical_id", -1)),
            int(row.get("attempt", -1)),
            int(row.get("seed", -1)),
        )
        for row in ledger
    }
    if len(actual_ledger) != 9 or actual_ledger != expected_ledger:
        raise GateFailure("Gate-B seed ledger does not exactly cover candidates")
    if any(row.get("allocation") != "gate_b_pilot" for row in ledger):
        raise GateFailure("Gate-B seed ledger has an unexpected allocation class")
    return campaign, rows, selected


def validate_submission(
    campaign_dir: Path,
    production: Path,
    campaign: dict[str, Any],
    rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    checkout = campaign_dir.parents[1].resolve()
    receipts = production / "submission_receipts"
    claim_path = receipts / "gate_b_attempt0_submission_claim.json"
    record_path = receipts / "gate_b_attempt0_submitted.json"
    require_read_only_regular(claim_path, "Gate-B submission claim")
    require_read_only_regular(record_path, "Gate-B submission record")
    claim = load_json(claim_path, "Gate-B submission claim")
    record = load_json(record_path, "Gate-B submission record")
    submit_path = require_regular(
        production / "submit_gate_b.sub", "Gate-B Condor submit file"
    )
    require_exact(
        claim,
        {
            "schema": "hf_gate_b_submission_claim_v1",
            "state": "claimed_before_condor_submit",
            "submission_kind": "gate_b",
            "campaign": campaign["campaign"],
            "campaign_ordinal": campaign["campaign_ordinal"],
            "repository_commit": campaign["repository_commit"],
            "campaign_json_sha256": sha256(campaign_dir / "campaign.json"),
            "candidate_manifest_sha256": sha256(
                campaign_dir / "candidate_manifest.jsonl"
            ),
            "seed_ledger_sha256": sha256(campaign_dir / "seed_ledger.jsonl"),
            "submit_file_sha256": sha256(submit_path),
        },
        "Gate-B submission claim",
    )
    claim_time = require_utc_timestamp(
        claim.get("created_utc"), "Gate-B submission claim"
    )
    producer_sha = claim.get("producer_executable_sha256")
    if not isinstance(producer_sha, str) or not HEX64.fullmatch(producer_sha):
        raise GateFailure("submission claim producer checksum is invalid")
    expected_allocations = [
        {
            "tune": row["tune"],
            "logical_id": int(row["logical_id"]),
            "role": row["role"],
            "attempt": int(row["attempt"]),
            "seed": int(row["seed"]),
            "requested_successes": int(row["requested_successes"]),
            "campaign_ordinal": int(row["campaign_ordinal"]),
            "pthat_min_override": str(row["pthat_min_override"]),
            "multiplicity_audit_events": int(row["multiplicity_audit_events"]),
            "repository_commit": row["repository_commit"],
            "effective_card_sha256": row["effective_card_sha256"],
            "producer_executable_sha256": producer_sha,
        }
        for row in rows
    ]
    if claim.get("allocations") != expected_allocations:
        raise GateFailure("submission claim does not bind the exact nine rows")
    reserved = claim.get("reserved_seeds")
    if reserved != sorted(row["seed"] for row in rows):
        raise GateFailure("submission claim reserved seeds differ from manifest")
    if claim.get("reserved_seed_intervals") != [
        [seed, seed] for seed in reserved
    ]:
        raise GateFailure(
            "submission claim seed intervals do not exactly reserve nine seeds"
        )
    prefix_bytes = claim.get("seed_ledger_prefix_bytes")
    if (
        isinstance(prefix_bytes, bool)
        or not isinstance(prefix_bytes, int)
        or prefix_bytes != (campaign_dir / "seed_ledger.jsonl").stat().st_size
    ):
        raise GateFailure("submission claim ledger prefix length is not exact")
    for key in ("repository_identity", "global_submission_registry"):
        if not isinstance(claim.get(key), str) or not claim[key]:
            raise GateFailure(f"submission claim {key} is absent")
    if not HEX64.fullmatch(str(claim.get("registry_baseline_sha256", ""))):
        raise GateFailure("submission claim registry baseline checksum is invalid")
    identity = claim["repository_identity"]
    registry = Path(claim["global_submission_registry"])
    if (
        not registry.is_absolute()
        or registry.name != hashlib.sha256(identity.encode()).hexdigest()
        or registry.resolve() != registry
        or registry.is_symlink()
        or not registry.is_dir()
    ):
        raise GateFailure("submission claim global registry path is invalid")
    baseline_path = require_regular(
        registry / "reservation_baseline.json",
        "shared submission reservation baseline",
    )
    baseline_stat = baseline_path.stat()
    if (
        baseline_stat.st_nlink != 1
        or stat.S_IMODE(baseline_stat.st_mode) & 0o222
        or sha256(baseline_path) != claim["registry_baseline_sha256"]
    ):
        raise GateFailure(
            "shared submission reservation baseline is mutable or differs"
        )
    baseline = load_json(
        baseline_path, "shared submission reservation baseline"
    )
    require_exact(
        baseline,
        {
            "schema": "hf_submission_registry_baseline_v1",
            "repository_identity": identity,
        },
        "shared submission reservation baseline",
    )
    if (
        not isinstance(baseline.get("reviewer"), str)
        or not baseline["reviewer"].strip()
        or not isinstance(baseline.get("historical_reservations"), list)
    ):
        raise GateFailure("shared submission reservation baseline is incomplete")
    global_claim_path = registry / "claims" / f"{campaign['campaign']}.json"
    require_read_only_regular(
        global_claim_path, "shared Gate-B submission reservation"
    )
    global_claim = load_json(
        global_claim_path, "shared Gate-B submission reservation"
    )
    require_exact(
        global_claim,
        {
            "schema": "hf_global_submission_claim_v1",
            "state": "reserved_before_condor_submit",
            "repository_identity": identity,
            "global_submission_registry": str(registry),
            "registry_baseline_sha256": claim["registry_baseline_sha256"],
            "campaign": campaign["campaign"],
            "campaign_ordinal": campaign["campaign_ordinal"],
            "submission_kind": "gate_b",
            "repository_commit": campaign["repository_commit"],
            "reserved_seeds": claim["reserved_seeds"],
            "reserved_seed_intervals": claim["reserved_seed_intervals"],
            "local_receipt_sha256": sha256(claim_path),
        },
        "shared Gate-B submission reservation",
    )
    if require_utc_timestamp(
        global_claim.get("created_utc"),
        "shared Gate-B submission reservation",
    ) != claim_time:
        raise GateFailure(
            "shared/local Gate-B reservation timestamps do not match"
        )
    require_exact(
        record,
        {
            "schema": "hf_gate_b_submission_record_v1",
            "state": "condor_submit_succeeded",
            "submission_kind": "gate_b",
            "claim_sha256": sha256(claim_path),
            "campaign": campaign["campaign"],
            "campaign_ordinal": campaign["campaign_ordinal"],
            "condor_first_process": 0,
            "condor_last_process": 8,
            "condor_process_count": 9,
            "submitted_held": True,
        },
        "Gate-B submission record",
    )
    submitted_time = require_utc_timestamp(
        record.get("submitted_utc"), "Gate-B submission record"
    )
    if submitted_time < claim_time:
        raise GateFailure("Gate-B submission record predates its claim")
    cluster = record.get("condor_cluster_id")
    if isinstance(cluster, bool) or not isinstance(cluster, int) or cluster < 0:
        raise GateFailure("submission record Condor cluster ID is invalid")
    classad_relative_text = record.get("classad_evidence_path")
    classad_relative = (
        Path(classad_relative_text)
        if isinstance(classad_relative_text, str)
        else Path()
    )
    classad_path = (
        receipts / "gate_b_attempt0_submitted_classads.json"
    )
    if (
        not classad_relative_text
        or classad_relative.is_absolute()
        or ".." in classad_relative.parts
        or checkout / classad_relative != classad_path
        or not HEX64.fullmatch(
            str(record.get("classad_evidence_sha256", ""))
        )
    ):
        raise GateFailure("Gate-B ClassAd evidence path is not canonical")
    require_read_only_regular(classad_path, "Gate-B ClassAd evidence")
    if sha256(classad_path) != record["classad_evidence_sha256"]:
        raise GateFailure("Gate-B ClassAd evidence checksum differs")
    classad_evidence = load_json(classad_path, "Gate-B ClassAd evidence")
    captured_time = require_utc_timestamp(
        classad_evidence.get("captured_utc"),
        "Gate-B ClassAd evidence",
    )
    if captured_time < claim_time or captured_time > submitted_time:
        raise GateFailure(
            "Gate-B ClassAd capture is outside the claim/submission interval"
        )
    condor_q_text = classad_evidence.get("condor_q_executable")
    condor_q_path = (
        Path(condor_q_text) if isinstance(condor_q_text, str) else Path()
    )
    condor_q_sha = classad_evidence.get("condor_q_executable_sha256")
    expected_command = [
        str(condor_q_path),
        str(cluster),
        "-json",
        "-attributes",
        ",".join(CONDOR_SUBMISSION_ATTRIBUTES),
    ]
    expected_classad_metadata = {
        "schema": "hf_condor_submission_classads_v1",
        "state": "PASS",
        "claim_path": str(claim_path.relative_to(checkout)),
        "claim_sha256": sha256(claim_path),
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
        "condor_cluster_id": cluster,
        "condor_first_process": 0,
        "condor_last_process": 8,
        "condor_process_count": 9,
        "attributes": list(CONDOR_SUBMISSION_ATTRIBUTES),
        "command": expected_command,
    }
    for key, expected in expected_classad_metadata.items():
        if classad_evidence.get(key) != expected:
            raise GateFailure(f"Gate-B ClassAd evidence {key} differs")
    if (
        not condor_q_text
        or not condor_q_path.is_absolute()
        or condor_q_path.name != "condor_q"
        or not isinstance(condor_q_sha, str)
        or not HEX64.fullmatch(condor_q_sha)
        or record.get("condor_q_executable") != condor_q_text
        or record.get("condor_q_executable_sha256") != condor_q_sha
    ):
        raise GateFailure("Gate-B condor_q provenance is invalid")
    raw_stdout = classad_evidence.get("raw_stdout")
    if (
        not isinstance(raw_stdout, str)
        or hashlib.sha256(raw_stdout.encode()).hexdigest()
        != classad_evidence.get("raw_stdout_sha256")
    ):
        raise GateFailure("Gate-B ClassAd raw output checksum differs")
    try:
        raw_classads = json.loads(raw_stdout)
    except json.JSONDecodeError as error:
        raise GateFailure("Gate-B ClassAd raw output is not JSON") from error
    if (
        not isinstance(raw_classads, list)
        or raw_classads != classad_evidence.get("classads")
        or len(raw_classads) != len(expected_allocations)
    ):
        raise GateFailure("Gate-B ClassAd raw/evaluated rows differ")
    by_process: dict[int, dict[str, Any]] = {}
    for row in raw_classads:
        process_id = row.get("ProcId") if isinstance(row, dict) else None
        if (
            not isinstance(row, dict)
            or isinstance(process_id, bool)
            or not isinstance(process_id, int)
            or process_id in by_process
            or process_id < 0
            or process_id >= len(expected_allocations)
        ):
            raise GateFailure("Gate-B ClassAd process coverage differs")
        by_process[process_id] = row
    if set(by_process) != set(range(len(expected_allocations))):
        raise GateFailure("Gate-B ClassAd process coverage is incomplete")
    worker = checkout / "runCondorJob.sh"
    for process_id, allocation in enumerate(expected_allocations):
        row = by_process[process_id]
        expected_args = " ".join(
            (
                "--campaign",
                campaign["campaign"],
                str(allocation["campaign_ordinal"]),
                allocation["tune"],
                str(allocation["logical_id"]),
                allocation["role"],
                str(allocation["attempt"]),
                str(allocation["seed"]),
                str(allocation["requested_successes"]),
                allocation["pthat_min_override"],
                str(allocation["multiplicity_audit_events"]),
                allocation["repository_commit"],
                allocation["effective_card_sha256"],
                allocation["producer_executable_sha256"],
                str(cluster),
                str(process_id),
            )
        )
        expected_strings = {
            "Cmd": str(worker),
            "Iwd": str(checkout),
            "Args": expected_args,
            "HFCampaign": campaign["campaign"],
            "HFTune": allocation["tune"],
            "HFRole": allocation["role"],
            "HFPTHat": allocation["pthat_min_override"],
            "HFRepositoryCommit": allocation["repository_commit"],
            "HFEffectiveCardSHA256":
                allocation["effective_card_sha256"],
            "HFProducerExecutableSHA256":
                allocation["producer_executable_sha256"],
        }
        expected_integers = {
            "ClusterId": cluster,
            "ProcId": process_id,
            "JobStatus": 5,
            "HFCampaignOrdinal": allocation["campaign_ordinal"],
            "HFLogicalId": allocation["logical_id"],
            "HFAttempt": allocation["attempt"],
            "HFSeed": allocation["seed"],
            "HFRequestedSuccesses": allocation["requested_successes"],
            "HFMultiplicityAuditEvents":
                allocation["multiplicity_audit_events"],
        }
        if any(row.get(key) != value for key, value in expected_strings.items()):
            raise GateFailure(
                f"Gate-B ClassAd strings differ for process {process_id}"
            )
        if any(
            isinstance(row.get(key), bool)
            or not isinstance(row.get(key), int)
            or row.get(key) != value
            for key, value in expected_integers.items()
        ):
            raise GateFailure(
                f"Gate-B ClassAd integers differ for process {process_id}"
            )
    return (
        claim,
        record,
        {
            "claim_path": str(claim_path.relative_to(production)),
            "claim_sha256": sha256(claim_path),
            "record_path": str(record_path.relative_to(production)),
            "record_sha256": sha256(record_path),
            "submit_path": str(submit_path.relative_to(production)),
            "submit_sha256": sha256(submit_path),
            "producer_executable_sha256": producer_sha,
            "condor_cluster_id": cluster,
            "classad_evidence_path": str(
                classad_path.relative_to(production)
            ),
            "classad_evidence_sha256": sha256(classad_path),
            "condor_q_executable": condor_q_text,
            "condor_q_executable_sha256": condor_q_sha,
            "registry_baseline_path": str(baseline_path),
            "registry_baseline_sha256": sha256(baseline_path),
            "global_claim_path": str(global_claim_path),
            "global_claim_sha256": sha256(global_claim_path),
        },
    )


def validator_dependency_hashes(checkout: Path) -> dict[str, str]:
    paths = (
        "setupEnv.sh",
        "SimulationScripts/HeavyFlavourUtils.h",
        "SimulationScripts/GeneratedHeavyFlavourRegistry.h",
        "SimulationScripts/GeneratedTuneSettingRegistry.h",
        "SimulationScripts/Sha256.h",
        "AnalysisScripts/GeneratedPairRegistry.h",
    )
    result: dict[str, str] = {}
    for relative in paths:
        path = require_regular(checkout / relative, f"validator dependency {relative}")
        key = (
            relative
            if Path(relative).parent.name
            in {"Validation", "SimulationScripts", "AnalysisScripts"}
            else Path(relative).name
        )
        result[key] = sha256(path)
    return dict(sorted(result.items()))


def parse_raw_log(log_text: str, expected_events: int, label: str) -> dict[str, Any]:
    if (
        "RAW_VALIDATION_ERROR" in log_text
        or "segmentation violation" in log_text.lower()
        or "segmentation fault" in log_text.lower()
    ):
        raise GateFailure(f"{label} contains a validator/crash error marker")
    summaries = RAW_SUMMARY.findall(log_text)
    origins = RAW_ORIGIN.findall(log_text)
    if len(summaries) != 1 or len(origins) != 1:
        raise GateFailure(
            f"{label} lacks exactly one complete validation/origin summary"
        )
    entries, process_codes, stability_rows = map(int, summaries[0])
    if entries != expected_events or process_codes < 2 or stability_rows <= 0:
        raise GateFailure(
            f"{label} event/process/stability accounting is incomplete"
        )
    origin_values = tuple(map(int, origins[0]))
    return {
        "entries": entries,
        "process_codes": process_codes,
        "stability_rows": stability_rows,
        "unresolved_charm_trigger_candidates": origin_values[0],
        "unresolved_beauty_trigger_candidates": origin_values[1],
        "resolved_nonhard_charm_trigger_candidates": origin_values[2],
        "resolved_nonhard_beauty_trigger_candidates": origin_values[3],
        "duplicate_hard_carrier_groups_charm": origin_values[4],
        "duplicate_hard_carrier_groups_beauty": origin_values[5],
        "duplicate_hard_carrier_demotions_charm": origin_values[6],
        "duplicate_hard_carrier_demotions_beauty": origin_values[7],
        "multi_heavy_rejections_charm": origin_values[8],
        "multi_heavy_rejections_beauty": origin_values[9],
    }


def validate_raw_outputs(
    checkout: Path,
    production: Path,
    campaign: dict[str, Any],
    selected: dict[tuple[str, int], dict[str, Any]],
    claim: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    wrapper_sha = sha256(
        require_regular(
            checkout / "Validation/validate_raw_output.sh",
            "raw validator wrapper",
        )
    )
    macro_sha = sha256(
        require_regular(
            checkout / "Validation/ValidateRawOutput.C", "raw validator macro"
        )
    )
    dependencies = validator_dependency_hashes(checkout)
    producer_sha = claim["producer_executable_sha256"]
    evidence: list[dict[str, Any]] = []
    central_origins: dict[str, dict[str, int]] = {}
    stability_rows: set[int] = set()
    for tune in TUNES:
        for logical_id in sorted(PROFILES):
            row = selected[(tune, logical_id)]
            raw = require_read_only_regular(
                production / "raw" / tune / row["stable_name"],
                f"raw output {tune}/{logical_id}",
            )
            raw_sha = sha256(raw)
            sidecar = require_read_only_regular(
                Path(f"{raw}.sha256"), f"raw checksum sidecar {tune}/{logical_id}"
            )
            if sidecar.read_text() != f"{raw_sha}  {raw.name}\n":
                raise GateFailure(f"raw checksum sidecar differs for {raw}")
            attempt_relative = (
                f"attempt_starts/{tune}/job_{logical_id:03d}/attempt_000.json"
            )
            attempt_path = production / attempt_relative
            require_read_only_regular(
                attempt_path, f"attempt-start claim {tune}/{logical_id}"
            )
            attempt = load_json(
                attempt_path, f"attempt-start claim {tune}/{logical_id}"
            )
            require_exact(
                attempt,
                {
                    "schema": "hf_attempt_start_claim_v1",
                    "state": "claimed_before_producer_execution",
                    "campaign": campaign["campaign"],
                    "campaign_ordinal": campaign["campaign_ordinal"],
                    "tune": tune,
                    "logical_id": logical_id,
                    "role": "pilot",
                    "attempt": 0,
                    "seed": row["seed"],
                    "requested_successes": row["requested_successes"],
                    "repository_commit": campaign["repository_commit"],
                    "effective_card_sha256": row["effective_card_sha256"],
                    "producer_executable_sha256": producer_sha,
                },
                f"attempt-start claim {tune}/{logical_id}",
            )
            attempt_time = require_utc_timestamp(
                attempt.get("claimed_utc"),
                f"attempt-start claim {tune}/{logical_id}",
            )
            for scheduler_key in ("cluster_id", "process_id"):
                token = attempt.get(scheduler_key)
                if not isinstance(token, str) or not SAFE_TOKEN.fullmatch(token):
                    raise GateFailure(
                        f"attempt-start {tune}/{logical_id} has invalid "
                        f"{scheduler_key}"
                    )
            attempt_sha = sha256(attempt_path)
            validation_dir = (
                production
                / "raw_validation"
                / tune
                / f"job_{logical_id:03d}"
                / "attempt_000"
            )
            receipt_path = validation_dir / "receipt.json"
            require_read_only_regular(
                receipt_path, f"raw-validation receipt {tune}/{logical_id}"
            )
            receipt = load_json(
                receipt_path, f"raw-validation receipt {tune}/{logical_id}"
            )
            log_name = receipt.get("validation_log_name")
            if (
                not isinstance(log_name, str)
                or not log_name
                or Path(log_name).name != log_name
            ):
                raise GateFailure(
                    f"raw-validation receipt {tune}/{logical_id} has unsafe log"
                )
            log_path = require_read_only_regular(
                validation_dir / log_name,
                f"raw-validation log {tune}/{logical_id}",
            )
            expected_provenance = {
                "campaign": campaign["campaign"],
                "campaign_ordinal": campaign["campaign_ordinal"],
                "tune": tune,
                "logical_id": logical_id,
                "role": "pilot",
                "attempt": 0,
                "seed": row["seed"],
                "requested_successes": row["requested_successes"],
                "phase_space_pthat_min": float(row["pthat_min_override"]),
                "multiplicity_audit_events": 100,
                "repository_commit": campaign["repository_commit"],
                "effective_card_sha256": row["effective_card_sha256"],
                "producer_executable_sha256": producer_sha,
                "attempt_start_claim_sha256": attempt_sha,
                "cluster_id": attempt["cluster_id"],
                "process_id": attempt["process_id"],
            }
            require_exact(
                receipt,
                {
                    "schema": RAW_RECEIPT_SCHEMA,
                    "result": "PASS",
                    "validator_exit_status": 0,
                    "validator_wrapper_sha256": wrapper_sha,
                    "validator_macro_sha256": macro_sha,
                    "validator_dependency_sha256": dependencies,
                    "validation_log_name": log_name,
                    "validation_log_sha256": sha256(log_path),
                    "output_sha256": raw_sha,
                    "output_bytes": raw.stat().st_size,
                    "expected_provenance": expected_provenance,
                },
                f"raw-validation receipt {tune}/{logical_id}",
            )
            validation_time = require_utc_timestamp(
                receipt.get("validated_utc"),
                f"raw-validation receipt {tune}/{logical_id}",
            )
            if validation_time < attempt_time:
                raise GateFailure(
                    f"raw validation predates attempt claim for "
                    f"{tune}/{logical_id}"
                )
            summary = parse_raw_log(
                log_path.read_text(errors="replace"),
                row["requested_successes"],
                f"raw-validation log {tune}/{logical_id}",
            )
            stability_rows.add(summary["stability_rows"])
            if logical_id == 0:
                central_origins[tune] = {
                    "charm": summary[
                        "unresolved_charm_trigger_candidates"
                    ],
                    "beauty": summary[
                        "unresolved_beauty_trigger_candidates"
                    ],
                }
            sidecar_name = (
                f"hf_{tune}_job{logical_id:03d}_attempt000_"
                f"{attempt['cluster_id']}_{attempt['process_id']}.json"
            )
            metadata_path = require_read_only_regular(
                production / "attempt_metadata" / tune / sidecar_name,
                f"attempt metadata {tune}/{logical_id}",
            )
            metadata = load_json(
                metadata_path, f"attempt metadata {tune}/{logical_id}"
            )
            require_exact(
                metadata,
                {
                    "campaign": campaign["campaign"],
                    "campaign_ordinal": campaign["campaign_ordinal"],
                    "tune": tune,
                    "logical_id": logical_id,
                    "role": "pilot",
                    "attempt": 0,
                    "seed": row["seed"],
                    "requested_successes": row["requested_successes"],
                    "pthat_min_override": row["pthat_min_override"],
                    "multiplicity_audit_events": 100,
                    "repository_commit": campaign["repository_commit"],
                    "effective_card_sha256": row["effective_card_sha256"],
                    "producer_executable_sha256": producer_sha,
                    "attempt_start_claim_sha256": attempt_sha,
                    "cluster_id": attempt["cluster_id"],
                    "process_id": attempt["process_id"],
                    "producer_exit": 0,
                    "partial_bytes": raw.stat().st_size,
                    "partial_sha256": raw_sha,
                },
                f"attempt metadata {tune}/{logical_id}",
            )
            elapsed = metadata.get("elapsed_seconds")
            if isinstance(elapsed, bool) or not isinstance(elapsed, int) or elapsed <= 0:
                raise GateFailure(
                    f"attempt metadata {tune}/{logical_id} runtime is invalid"
                )
            start_time = require_utc_timestamp(
                metadata.get("start_utc"),
                f"attempt metadata start {tune}/{logical_id}",
            )
            end_time = require_utc_timestamp(
                metadata.get("end_utc"),
                f"attempt metadata end {tune}/{logical_id}",
            )
            if (
                end_time < start_time
                or abs((end_time - start_time).total_seconds() - elapsed) > 1
            ):
                raise GateFailure(
                    f"attempt metadata wall-time accounting differs for "
                    f"{tune}/{logical_id}"
                )
            evidence.append(
                {
                    "tune": tune,
                    "logical_id": logical_id,
                    "purpose": row["purpose"],
                    "pthat_min": row["pthat_min_override"],
                    "requested_successes": row["requested_successes"],
                    "raw_path": str(raw.relative_to(production)),
                    "raw_bytes": raw.stat().st_size,
                    "raw_sha256": raw_sha,
                    "attempt_start_path": attempt_relative,
                    "attempt_start_sha256": attempt_sha,
                    "attempt_metadata_path": str(
                        metadata_path.relative_to(production)
                    ),
                    "attempt_metadata_sha256": sha256(metadata_path),
                    "validation_receipt_path": str(
                        receipt_path.relative_to(production)
                    ),
                    "validation_receipt_sha256": sha256(receipt_path),
                    "validation_log_path": str(log_path.relative_to(production)),
                    "validation_log_sha256": sha256(log_path),
                    "elapsed_seconds": elapsed,
                    **summary,
                }
            )
    if len(evidence) != 9 or len(central_origins) != 3:
        raise GateFailure("raw-output evidence is incomplete")
    if len(stability_rows) != 1:
        raise GateFailure(
            f"heavy-stability audit row counts differ: {sorted(stability_rows)}"
        )
    return evidence, central_origins


def validate_pthat_report(
    checkout: Path,
    campaign_dir: Path,
    campaign: dict[str, Any],
    rows: list[dict[str, Any]],
    pthat_path: Path,
) -> tuple[
    dict[str, Any],
    dict[str, dict[str, int]],
    list[str],
    list[str],
]:
    report = load_json(pthat_path, "pTHat sensitivity decision")
    require_exact(
        report,
        {
            "schema": PTHAT_REPORT_SCHEMA,
            "campaign": campaign["campaign"],
            "campaign_ordinal": campaign["campaign_ordinal"],
            "repository_commit": campaign["repository_commit"],
            "spec_sha256": sha256(
                checkout / "config/pthat_sensitivity_v1.json"
            ),
            "campaign_sha256": sha256(campaign_dir / "campaign.json"),
            "manifest_sha256": json_digest(rows),
        },
        "pTHat sensitivity decision",
    )
    outcome = report.get("outcome")
    if outcome not in {
        "PASS",
        "TECHNICAL_FAIL",
        "INCONCLUSIVE",
        "SCIENTIFIC_REVIEW_REQUIRED",
    }:
        raise GateFailure("pTHat sensitivity decision outcome is invalid")
    for key in (
        "technical_failures",
        "scientific_review_findings",
        "inconclusive_findings",
        "diagnostics",
        "comparisons",
        "sigma_nested_closure",
        "input_provenance_evidence",
    ):
        if not isinstance(report.get(key), list):
            raise GateFailure(f"pTHat decision {key} is absent or not a list")
    expected_comparisons = 192
    if len(report["comparisons"]) != expected_comparisons:
        raise GateFailure(
            f"pTHat decision has {len(report['comparisons'])}/"
            f"{expected_comparisons} comparisons"
        )
    if len(report["sigma_nested_closure"]) != 6 or any(
        row.get("passed") is not True
        for row in report["sigma_nested_closure"]
    ):
        raise GateFailure("pTHat structured cross-section closure did not pass")
    extraction_hashes = report.get("extraction_sha256")
    if (
        not isinstance(extraction_hashes, dict)
        or set(extraction_hashes)
        != {
            f"{tune}:{threshold}"
            for tune in TUNES
            for threshold in ("0.5", "1.0", "2.0")
        }
        or any(
            not isinstance(value, str) or not HEX64.fullmatch(value)
            for value in extraction_hashes.values()
        )
    ):
        raise GateFailure("pTHat extraction checksum coverage is incomplete")
    diagnostics: dict[tuple[str, str], dict[str, Any]] = {}
    for row in report["diagnostics"]:
        identity = row.get("identity", {})
        key = (identity.get("tune"), str(identity.get("pthat_min")))
        if key in diagnostics:
            raise GateFailure("pTHat diagnostics contain a duplicate identity")
        diagnostics[key] = row
    expected_identities = {
        (tune, threshold)
        for tune in TUNES
        for threshold in ("0.5", "1.0", "2.0")
    }
    if set(diagnostics) != expected_identities:
        raise GateFailure("pTHat diagnostics do not cover exact nine samples")
    unresolved_by_sample: dict[str, dict[str, int]] = {}
    for tune in TUNES:
        unresolved_by_sample[tune] = {}
        for logical_id, (threshold, events, _, _) in PROFILES.items():
            diagnostic = diagnostics[(tune, threshold)]
            if diagnostic.get("events") != events:
                raise GateFailure(
                    f"pTHat diagnostic event count differs for "
                    f"{tune}/{threshold}"
                )
            unresolved = diagnostic.get("unresolved_trigger_candidates")
            if (
                isinstance(unresolved, bool)
                or not isinstance(unresolved, int)
                or unresolved < 0
            ):
                raise GateFailure(
                    f"pTHat unresolved count is invalid for {tune}/{threshold}"
                )
            unresolved_by_sample[tune][threshold] = unresolved
    nonpass_reasons: list[str] = []
    if outcome != "PASS":
        nonpass_reasons.append(f"pTHat outcome is {outcome}, not PASS")
    blockers: list[str] = []
    blockers.extend(
        f"technical: {finding}" for finding in report["technical_failures"]
    )
    blockers.extend(
        f"inconclusive: {finding}" for finding in report["inconclusive_findings"]
    )
    for comparison in report["comparisons"]:
        if comparison.get("status") != "EQUIVALENT_NO_RESOLVED_SHIFT":
            blockers.append(
                "pTHat comparison is not equivalent/no-resolved-shift: "
                f"{comparison.get('tune')}/"
                f"{comparison.get('alternate_threshold')}/"
                f"{comparison.get('observable')}="
                f"{comparison.get('status')}"
            )
    for finding in report["scientific_review_findings"]:
        if "unresolved publication-trigger candidates" not in str(finding):
            blockers.append(f"scientific review: {finding}")
    if outcome == "PASS":
        if (
            report["technical_failures"]
            or report["scientific_review_findings"]
            or report["inconclusive_findings"]
            or any(
                row.get("status") != "EQUIVALENT_NO_RESOLVED_SHIFT"
                for row in report["comparisons"]
            )
        ):
            raise GateFailure("pTHat PASS retains non-PASS findings/comparisons")
    return report, unresolved_by_sample, nonpass_reasons, blockers


def recheck_pthat_decision(
    checkout: Path,
    campaign_dir: Path,
    production: Path,
    pthat_path: Path,
    staging: Path,
    commands: list[dict[str, Any]],
) -> dict[str, Any]:
    if pthat_path.name != "pthat_sensitivity_decision.json":
        raise GateFailure(
            "pTHat input must be the canonical pthat_sensitivity_decision.json"
        )
    supplied = load_json(pthat_path, "supplied pTHat decision")
    extraction_hashes = supplied.get("extraction_sha256")
    extraction_dir = pthat_path.parent / "extractions"
    require_directory(extraction_dir, "pTHat extraction directory")
    if not isinstance(extraction_hashes, dict):
        raise GateFailure("pTHat decision lacks extraction checksums")
    expected_files: set[str] = set()
    for identity, expected_sha in extraction_hashes.items():
        try:
            tune, threshold = identity.split(":", 1)
        except ValueError as error:
            raise GateFailure(f"unsafe pTHat extraction identity {identity!r}") from error
        if tune not in TUNES or threshold not in {"0.5", "1.0", "2.0"}:
            raise GateFailure(f"unexpected pTHat extraction identity {identity}")
        name = f"{tune}_pthat_{threshold}.json"
        expected_files.add(name)
        path = require_regular(
            extraction_dir / name, f"pTHat extraction {identity}"
        )
        if sha256(path) != expected_sha:
            raise GateFailure(f"pTHat extraction checksum differs for {identity}")
    discovered = {
        path.name
        for path in extraction_dir.iterdir()
        if path.is_file() and path.name.endswith(".json")
    }
    if discovered != expected_files:
        raise GateFailure(
            f"pTHat extraction file set differs: "
            f"missing={sorted(expected_files - discovered)} "
            f"extra={sorted(discovered - expected_files)}"
        )
    recheck_dir = staging / "pthat_recheck"
    log = staging / "pthat_recheck.log"
    command = run_command(
        [
            sys.executable,
            str(checkout / "tools/evaluate_pthat_sensitivity.py"),
            str(campaign_dir),
            str(production),
            str(recheck_dir),
            "--checkout-root",
            str(checkout),
        ],
        log,
    )
    command["purpose"] = "fresh_raw_to_frozen_pthat_decision_recheck"
    commands.append(command)
    expected_exit = {
        "PASS": 0,
        "TECHNICAL_FAIL": 2,
        "INCONCLUSIVE": 3,
        "SCIENTIFIC_REVIEW_REQUIRED": 4,
    }.get(supplied.get("outcome"))
    if expected_exit is None or command["returncode"] != expected_exit:
        raise GateFailure(
            "frozen pTHat evaluator exit status differs from supplied outcome"
        )
    extraction_log = require_regular(
        recheck_dir / "extractions" / "pthat_extraction_root.log",
        "fresh pTHat ROOT extraction log",
    )
    command["additional_log_path"] = str(extraction_log.relative_to(staging))
    command["additional_log_sha256"] = sha256(extraction_log)
    extraction_log_text = extraction_log.read_text(errors="replace").lower()
    if (
        re.search(r"(^|\n)[^\n]*\bwarning:", extraction_log_text)
        or "error in <aclic>" in extraction_log_text
        or "fatal error:" in extraction_log_text
        or "segmentation violation" in extraction_log_text
        or "segmentation fault" in extraction_log_text
    ):
        command["compiler_warning_found"] = True
        raise GateFailure(
            "fresh pTHat ROOT extraction log contains a compiler/crash marker"
        )
    recomputed_path = require_regular(
        recheck_dir / "pthat_sensitivity_decision.json",
        "recomputed pTHat decision",
    )
    recomputed = load_json(recomputed_path, "recomputed pTHat decision")
    if recomputed != supplied:
        raise GateFailure(
            "supplied pTHat decision is not semantically identical to the "
            "reuse-only frozen evaluator result"
        )
    return {
        "recomputed_path": str(recomputed_path.relative_to(staging)),
        "recomputed_sha256": sha256(recomputed_path),
        "supplied_extraction_directory": str(extraction_dir),
        "supplied_extraction_count": len(expected_files),
        "fresh_extraction_directory": str(
            (recheck_dir / "extractions").relative_to(staging)
        ),
        "fresh_extraction_log_sha256": sha256(extraction_log),
        "semantic_identity_confirmed": True,
    }


def central_associate_origin_evidence(
    pthat_report: dict[str, Any],
) -> list[dict[str, Any]]:
    labels = {
        "0": "unresolved",
        "1": "selected_hard",
        "2": "shower",
        "3": "mpi",
        "4": "other_resolved",
    }
    result: list[dict[str, Any]] = []
    for tune in TUNES:
        matches = [
            row
            for row in pthat_report["diagnostics"]
            if row.get("identity") == {"tune": tune, "pthat_min": "1.0"}
        ]
        if len(matches) != 1:
            raise GateFailure(
                f"central associate-origin diagnostics missing for {tune}"
            )
        diagnostic = matches[0]
        counts = diagnostic.get("associate_origin_counts")
        weights = diagnostic.get("associate_origin_weight_sums")
        if (
            not isinstance(counts, dict)
            or not isinstance(weights, dict)
            or set(counts) != {"charm", "beauty"}
            or set(weights) != {"charm", "beauty"}
        ):
            raise GateFailure(
                f"associate-origin sector diagnostics differ for {tune}"
            )
        for sector in ("charm", "beauty"):
            if (
                not isinstance(counts[sector], dict)
                or not isinstance(weights[sector], dict)
                or set(counts[sector]) - set(labels)
                or set(weights[sector]) - set(labels)
            ):
                raise GateFailure(
                    f"associate-origin category diagnostics differ for "
                    f"{tune}/{sector}"
                )
            normalized_counts = {
                labels[key]: int(value)
                for key, value in counts[sector].items()
            }
            normalized_weights = {
                labels[key]: float(value)
                for key, value in weights[sector].items()
            }
            if (
                any(value < 0 for value in normalized_counts.values())
                or any(
                    not math.isfinite(value) or value < 0.0
                    for value in normalized_weights.values()
                )
            ):
                raise GateFailure(
                    f"associate-origin diagnostics are negative/non-finite "
                    f"for {tune}/{sector}"
                )
            total_count = sum(normalized_counts.values())
            total_weight = sum(normalized_weights.values())
            if total_count <= 0 or total_weight <= 0.0:
                raise GateFailure(
                    f"associate-origin denominator is empty for {tune}/{sector}"
                )
            result.append(
                {
                    "tune": tune,
                    "sector": sector,
                    "counts": normalized_counts,
                    "count_fractions": {
                        label: value / total_count
                        for label, value in normalized_counts.items()
                    },
                    "weight_sums": normalized_weights,
                    "weight_fractions": {
                        label: value / total_weight
                        for label, value in normalized_weights.items()
                    },
                    "total_count": total_count,
                    "total_weight": total_weight,
                }
            )
    return result


def cpp_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def run_command(
    argv: list[str],
    log_path: Path,
    *,
    stdin: str | None = None,
    stdin_evidence_path: Path | None = None,
) -> dict[str, Any]:
    if stdin is not None:
        if stdin_evidence_path is None:
            raise GateFailure("command stdin was not assigned an evidence path")
        stdin_evidence_path.write_text(stdin)
    elif stdin_evidence_path is not None:
        raise GateFailure("stdin evidence path was supplied without stdin")
    started = datetime.datetime.now(datetime.timezone.utc)
    process = subprocess.run(
        argv,
        input=stdin,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    ended = datetime.datetime.now(datetime.timezone.utc)
    log_path.write_text(process.stdout)
    lowered = process.stdout.lower()
    compiler_warning = bool(
        re.search(r"(^|\n)[^\n]*\bwarning:", lowered)
        or "error in <aclic>" in lowered
        or "fatal error:" in lowered
    )
    evidence = {
        "argv": argv,
        "started_utc": started.isoformat(timespec="seconds"),
        "ended_utc": ended.isoformat(timespec="seconds"),
        "returncode": process.returncode,
        "log_path": log_path.name,
        "log_sha256": sha256(log_path),
        "compiler_warning_found": compiler_warning,
    }
    if stdin_evidence_path is not None:
        evidence["stdin_path"] = stdin_evidence_path.name
        evidence["stdin_sha256"] = sha256(stdin_evidence_path)
    return evidence


def root_script(body: Iterable[str]) -> str:
    return "\n".join(
        [
            *body,
            "",
        ]
    )


def audit_tune_settings(
    checkout: Path,
    production: Path,
    staging: Path,
    commands: list[dict[str, Any]],
) -> dict[str, Any]:
    output = staging / "effective_tune_differences.csv"
    log = staging / "audit_tune_settings.log"
    macro = checkout / "Validation/AuditTuneSettings.C"
    raw = {
        tune: production / "raw" / tune / f"hf_{tune}_job000.root"
        for tune in TUNES
    }
    script = root_script(
        [
            f'gROOT->ProcessLine({cpp_string(f".L {macro}")});',
            "int gate_b_status = AuditTuneSettings("
            + ",".join(
                cpp_string(str(raw[tune])) for tune in TUNES
            )
            + f",{cpp_string(str(checkout / 'config/tune_difference_allowlist_v1.json'))}"
            + f",{cpp_string(str(output))});",
            "gSystem->Exit(gate_b_status);",
        ]
    )
    command = run_command(
        ["root", "-l", "-b"],
        log,
        stdin=script,
        stdin_evidence_path=staging / "audit_tune_settings.stdin.C",
    )
    command["purpose"] = "cross_tune_effective_settings_audit"
    commands.append(command)
    if command["returncode"] != 0 or command["compiler_warning_found"]:
        raise GateFailure("cross-tune effective-settings audit command failed")
    require_regular(output, "effective tune-difference CSV")
    text = log.read_text(errors="replace")
    matches = re.findall(
        r"^EFFECTIVE_TUNE_AUDIT errors=(\d+) settings=(\d+) "
        r"differences=(\d+) csv=(.+)\s*$",
        text,
        flags=re.MULTILINE,
    )
    if (
        len(matches) != 1
        or int(matches[0][0]) != 0
        or int(matches[0][1]) <= 0
        or "TUNE_AUDIT_ERROR" in text
        or "FORBIDDEN_DIFFERENCE" in output.read_text()
    ):
        raise GateFailure("cross-tune effective-settings audit did not certify PASS")
    with output.open(newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    expected_columns = {
        "setting",
        "MONASH",
        "JUNCTIONS",
        "CLOSEPACKING",
        "classification",
    }
    if (
        not csv_rows
        or set(csv_rows[0]) != expected_columns
        or len(csv_rows) != int(matches[0][1])
        or len({row["setting"] for row in csv_rows}) != len(csv_rows)
        or any(
            row["classification"]
            not in {
                "common",
                "allowed_tune_difference",
                "allowed_per_job_difference",
            }
            for row in csv_rows
        )
        or sum(row["classification"] != "common" for row in csv_rows)
        != int(matches[0][2])
    ):
        raise GateFailure("effective-settings CSV accounting is inconsistent")
    return {
        "schema": "effective_settings_audit_exhaustive_v2",
        "settings": int(matches[0][1]),
        "differences": int(matches[0][2]),
        "csv_path": output.name,
        "csv_sha256": sha256(output),
        "log_path": log.name,
        "log_sha256": sha256(log),
    }


def audit_resource_metadata(
    production: Path,
    selected: dict[tuple[str, int], dict[str, Any]],
    staging: Path,
    commands: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    macro = staging / "gate_b_resource_audit.C"
    log = staging / "gate_b_resource_audit.log"
    lines = [
        "#include <TFile.h>",
        "#include <TLeaf.h>",
        "#include <TObjString.h>",
        "#include <TTree.h>",
        "#include <cmath>",
        "#include <iomanip>",
        "#include <iostream>",
        "#include <stdexcept>",
        "#include <string>",
        "",
        "namespace {",
        "void InspectGateBResource(const char* path, const char* tune,",
        "                          int logicalId) {",
        '  TFile input(path, "READ");',
        "  if (input.IsZombie()) throw std::runtime_error(\"cannot open raw\");",
        '  auto* metadata = dynamic_cast<TTree*>(input.Get("job_metadata"));',
        "  auto* stability =",
        '      dynamic_cast<TTree*>(input.Get("heavy_stability_audit"));',
        "  auto* stabilityShaObject = dynamic_cast<TObjString*>(",
        '      input.Get("heavy_stability_audit_sha256"));',
        "  auto* settingsShaObject = dynamic_cast<TObjString*>(",
        '      input.Get("effective_settings_sha256"));',
        "  if (!metadata || metadata->GetEntries() != 1 || !stability ||",
        "      !stabilityShaObject || !settingsShaObject) {",
        '    throw std::runtime_error("missing resource/stability metadata");',
        "  }",
        "  std::string* storedTune = nullptr;",
        "  std::string* stabilitySchema = nullptr;",
        "  std::string* settingsSchema = nullptr;",
        '  metadata->SetBranchAddress("tune", &storedTune);',
        '  metadata->SetBranchAddress("heavy_stability_audit_schema",',
        "                             &stabilitySchema);",
        '  metadata->SetBranchAddress("effective_settings_schema",',
        "                             &settingsSchema);",
        "  metadata->GetEntry(0);",
        '  auto* successes = metadata->GetLeaf("successful_events");',
        '  auto* peakRss = metadata->GetLeaf("peak_rss_kib");',
        "  if (!storedTune || *storedTune != tune || !stabilitySchema ||",
        "      !settingsSchema || !successes || !peakRss) {",
        '    throw std::runtime_error("invalid/missing resource branches");',
        "  }",
        "  const auto successfulEvents = successes->GetValueLong64();",
        "  const auto peakRssKib = peakRss->GetValueLong64();",
        "  const auto fileBytes = input.GetSize();",
        '  auto* storedCompressionSettings = metadata->GetLeaf("root_compression_settings");',
        '  auto* storedCompressionAlgorithm = metadata->GetLeaf("root_compression_algorithm");',
        '  auto* storedCompressionLevel = metadata->GetLeaf("root_compression_level");',
        "  if (!storedCompressionSettings || !storedCompressionAlgorithm ||",
        "      !storedCompressionLevel) {",
        '    throw std::runtime_error("missing stored compression metadata");',
        "  }",
        "  const int compressionSettings = input.GetCompressionSettings();",
        "  const int compressionAlgorithm = input.GetCompressionAlgorithm();",
        "  const int compressionLevel = input.GetCompressionLevel();",
        "  const double compressionFactor = input.GetCompressionFactor();",
        "  if (successfulEvents <= 0 || peakRssKib <= 0 || fileBytes <= 0 ||",
        "      compressionSettings < 0 || compressionAlgorithm < 0 ||",
        "      compressionLevel < 0 ||",
        "      storedCompressionSettings->GetValueLong64() !=",
        "          compressionSettings ||",
        "      storedCompressionAlgorithm->GetValueLong64() !=",
        "          compressionAlgorithm ||",
        "      storedCompressionLevel->GetValueLong64() != compressionLevel ||",
        "      !std::isfinite(compressionFactor) ||",
        "      compressionFactor <= 0.0) {",
        '    throw std::runtime_error("invalid resource/compression values");',
        "  }",
        '  std::cout << "GATE_B_RESOURCE"',
        '            << " tune=" << tune',
        '            << " logical_id=" << logicalId',
        '            << " successful_events=" << successfulEvents',
        '            << " peak_rss_kib=" << peakRssKib',
        '            << " file_bytes=" << fileBytes',
        '            << " compression_settings=" << compressionSettings',
        '            << " compression_algorithm=" << compressionAlgorithm',
        '            << " compression_level=" << compressionLevel',
        "            << std::setprecision(17)",
        '            << " compression_factor=" << compressionFactor',
        '            << " stability_schema=" << *stabilitySchema',
        '            << " stability_sha256="',
        "            << stabilityShaObject->GetString().Data()",
        '            << " stability_rows=" << stability->GetEntries()',
        '            << " settings_schema=" << *settingsSchema',
        '            << " settings_sha256="',
        "            << settingsShaObject->GetString().Data() << \"\\n\";",
        "  metadata->ResetBranchAddresses();",
        "}",
        "}  // namespace",
        "",
        "void gate_b_resource_audit() {",
    ]
    for tune in TUNES:
        for logical_id in sorted(PROFILES):
            raw = production / "raw" / tune / selected[(tune, logical_id)][
                "stable_name"
            ]
            lines.append(
                "  InspectGateBResource("
                f"{cpp_string(str(raw))},{cpp_string(tune)},{logical_id});"
            )
    lines.extend(["}", ""])
    macro.write_text("\n".join(lines))
    command = run_command(["root", "-l", "-b", "-q", str(macro)], log)
    command["purpose"] = "raw_resource_stability_compression_audit"
    command["input_macro_path"] = macro.name
    command["input_macro_sha256"] = sha256(macro)
    commands.append(command)
    if command["returncode"] != 0 or command["compiler_warning_found"]:
        raise GateFailure("raw resource/stability/compression audit command failed")
    text = log.read_text(errors="replace")
    matches = RESOURCE_SUMMARY.findall(text)
    if len(matches) != 9:
        raise GateFailure(
            f"resource/stability audit has {len(matches)}/9 summaries"
        )
    evidence: list[dict[str, Any]] = []
    identities: set[tuple[str, int]] = set()
    stability_hashes: set[str] = set()
    for match in matches:
        tune = match[0]
        logical_id = int(match[1])
        identity = (tune, logical_id)
        if identity not in selected or identity in identities:
            raise GateFailure("resource audit identity is invalid or duplicated")
        identities.add(identity)
        successful_events = int(match[2])
        peak_rss_kib = int(match[3])
        file_bytes = int(match[4])
        compression_settings = int(match[5])
        compression_algorithm = int(match[6])
        compression_level = int(match[7])
        compression_factor = float(match[8])
        stability_schema = match[9]
        stability_sha = match[10]
        stability_rows = int(match[11])
        settings_schema = match[12]
        settings_sha = match[13]
        row = selected[identity]
        raw = production / "raw" / tune / row["stable_name"]
        if (
            successful_events != row["requested_successes"]
            or peak_rss_kib <= 0
            or file_bytes != raw.stat().st_size
            or compression_settings < 0
            or compression_algorithm < 0
            or compression_level < 0
            or not math.isfinite(compression_factor)
            or compression_factor <= 0.0
            or stability_schema != "heavy_stability_audit_v2"
            or stability_rows <= 0
            or settings_schema != "effective_pythia_settings_exhaustive_v2"
        ):
            raise GateFailure(
                f"resource/stability metadata contract differs for "
                f"{tune}/{logical_id}"
            )
        stability_hashes.add(stability_sha)
        evidence.append(
            {
                "tune": tune,
                "logical_id": logical_id,
                "purpose": row["purpose"],
                "successful_events": successful_events,
                "peak_rss_kib": peak_rss_kib,
                "file_bytes": file_bytes,
                "compression_settings": compression_settings,
                "compression_algorithm": compression_algorithm,
                "compression_level": compression_level,
                "compression_factor": compression_factor,
                "heavy_stability_audit_schema": stability_schema,
                "heavy_stability_audit_sha256": stability_sha,
                "heavy_stability_rows": stability_rows,
                "effective_settings_schema": settings_schema,
                "effective_settings_sha256": settings_sha,
            }
        )
    if len(identities) != 9 or len(stability_hashes) != 1:
        raise GateFailure(
            "resource evidence is incomplete or heavy-stability digests differ"
        )
    return sorted(evidence, key=lambda row: (row["tune"], row["logical_id"]))


def audit_origins(
    checkout: Path,
    production: Path,
    staging: Path,
    commands: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    evidence: list[dict[str, Any]] = []
    unresolved_by_tune: dict[str, dict[str, int]] = {}
    origin_macro = checkout / "Validation/AuditOriginResolution.C"
    unresolved_macro = checkout / "Validation/ListUnresolvedOrigins.C"
    for tune in TUNES:
        raw = production / "raw" / tune / f"hf_{tune}_job000.root"
        validation_receipt = (
            production
            / "raw_validation"
            / tune
            / "job_000"
            / "attempt_000"
            / "receipt.json"
        )
        audit_output = staging / f"origin_resolution_{tune}.root"
        audit_log = staging / f"audit_origin_{tune}.log"
        audit_script = root_script(
            [
                f'gROOT->ProcessLine({cpp_string(f".L {origin_macro}")});',
                "int gate_b_status = AuditOriginResolution("
                f"{cpp_string(str(raw))},{cpp_string(str(audit_output))},"
                f"{cpp_string(str(validation_receipt))});",
                "gSystem->Exit(gate_b_status);",
            ]
        )
        audit_command = run_command(
            ["root", "-l", "-b"],
            audit_log,
            stdin=audit_script,
            stdin_evidence_path=staging / f"audit_origin_{tune}.stdin.C",
        )
        audit_command["purpose"] = f"origin_resolution_audit_{tune}"
        commands.append(audit_command)
        if audit_command["returncode"] != 0 or audit_command["compiler_warning_found"]:
            raise GateFailure(f"origin-resolution audit failed for {tune}")
        require_regular(audit_output, f"origin-resolution output {tune}")
        audit_text = audit_log.read_text(errors="replace")
        header = re.findall(
            rf"^ORIGIN_RESOLUTION_AUDIT schema=(\S+) tune={tune} "
            r"summary_rows=(\d+) output=(.+)\s*$",
            audit_text,
            flags=re.MULTILINE,
        )
        if (
            len(header) != 1
            or int(header[0][1]) <= 0
            or "ORIGIN_AUDIT_ERROR" in audit_text
        ):
            raise GateFailure(f"origin-resolution audit is incomplete for {tune}")
        summaries: dict[tuple[str, str], dict[str, Any]] = {}
        for match in ORIGIN_SUMMARY.findall(audit_text):
            parsed_tune, role, sector = match[0], match[1], match[2]
            if parsed_tune != tune or (role, sector) in summaries:
                raise GateFailure(f"invalid origin summary identity for {tune}")
            numeric = [
                float(match[5]),
                float(match[7]),
                float(match[8]),
                float(match[9]),
            ]
            if (
                match[6] != "1"
                or match[10] != "1"
                or any(not math.isfinite(value) for value in numeric)
            ):
                raise GateFailure(f"non-finite origin audit summary for {tune}")
            summaries[(role, sector)] = {
                "candidates": int(match[3]),
                "unresolved": int(match[4]),
                "unresolved_fraction": float(match[5]),
                "unresolved_fraction_defined": True,
                "sum_weights": float(match[7]),
                "unresolved_sum_weights": float(match[8]),
                "weighted_unresolved_fraction": float(match[9]),
                "weighted_unresolved_fraction_defined": True,
            }
        required = {
            ("associate", "charm"),
            ("associate", "beauty"),
            ("trigger_candidate", "charm"),
            ("trigger_candidate", "beauty"),
        }
        if not required.issubset(summaries):
            raise GateFailure(
                f"origin-resolution audit lacks role/sector coverage for {tune}"
            )

        unresolved_log = staging / f"list_unresolved_{tune}.log"
        unresolved_script = root_script(
            [
                f'gROOT->ProcessLine({cpp_string(f".L {unresolved_macro}")});',
                "int gate_b_status = ListUnresolvedOrigins("
                f"{cpp_string(str(raw))},"
                f"{cpp_string(str(validation_receipt))},100);",
                "gSystem->Exit(gate_b_status);",
            ]
        )
        unresolved_command = run_command(
            ["root", "-l", "-b"],
            unresolved_log,
            stdin=unresolved_script,
            stdin_evidence_path=staging / f"list_unresolved_{tune}.stdin.C",
        )
        unresolved_command["purpose"] = f"unresolved_origin_listing_{tune}"
        commands.append(unresolved_command)
        if (
            unresolved_command["returncode"] != 0
            or unresolved_command["compiler_warning_found"]
        ):
            raise GateFailure(f"unresolved-origin listing failed for {tune}")
        unresolved_text = unresolved_log.read_text(errors="replace")
        if (
            "UNRESOLVED_LIST_ERROR" in unresolved_text
            or len(
                re.findall(
                    rf"^UNRESOLVED_LIST tune={tune} printed_rows=\d+ "
                    r"maximum_rows=100\s*$",
                    unresolved_text,
                    flags=re.MULTILINE,
                )
            )
            != 1
        ):
            raise GateFailure(f"unresolved-origin listing is incomplete for {tune}")
        listed: dict[str, int] = {}
        for match in UNRESOLVED_SUMMARY.findall(unresolved_text):
            parsed_tune, role_sector = match[0], match[1]
            if parsed_tune != tune or role_sector in listed:
                raise GateFailure(f"invalid unresolved summary identity for {tune}")
            values = [float(value) for value in match[3:6]]
            if (
                match[6] != "1"
                or any(not math.isfinite(value) for value in values)
            ):
                raise GateFailure(f"non-finite unresolved summary for {tune}")
            listed[role_sector] = int(match[2])
        sector_counts: dict[str, int] = {}
        for sector in ("charm", "beauty"):
            expected = summaries[("trigger_candidate", sector)]["unresolved"]
            listed_count = listed.get(f"trigger_candidate:{sector}", 0)
            if listed_count != expected:
                raise GateFailure(
                    f"unresolved listing/origin audit mismatch for {tune}/{sector}"
                )
            sector_counts[sector] = expected
        unresolved_by_tune[tune] = sector_counts
        evidence.append(
            {
                "tune": tune,
                "audit_schema": header[0][0],
                "summary_rows": int(header[0][1]),
                "output_path": audit_output.name,
                "output_sha256": sha256(audit_output),
                "audit_log_path": audit_log.name,
                "audit_log_sha256": sha256(audit_log),
                "unresolved_log_path": unresolved_log.name,
                "unresolved_log_sha256": sha256(unresolved_log),
                "summaries": {
                    f"{role}:{sector}": value
                    for (role, sector), value in sorted(summaries.items())
                },
            }
        )
    return evidence, unresolved_by_tune


def combine_log(staging: Path, commands: list[dict[str, Any]]) -> tuple[str, str]:
    path = staging / "gate_b.log"
    sections: list[str] = []
    for command in commands:
        command_log = staging / command["log_path"]
        sections.extend(
            [
                f"COMMAND purpose={command.get('purpose', '')}",
                "ARGV " + json.dumps(command["argv"]),
                f"RETURNCODE {command['returncode']}",
                command_log.read_text(errors="replace"),
                "",
            ]
        )
        if "additional_log_path" in command:
            additional = staging / command["additional_log_path"]
            sections.extend(
                [
                    "ADDITIONAL_LOG "
                    + str(command["additional_log_path"]),
                    additional.read_text(errors="replace"),
                    "",
                ]
            )
    path.write_text("\n".join(sections))
    return path.name, sha256(path)


def reconcile_unresolved(
    raw_evidence: list[dict[str, Any]],
    raw_central_counts: dict[str, dict[str, int]],
    origin_counts: dict[str, dict[str, int]],
    pthat_counts: dict[str, dict[str, int]],
) -> int:
    total = 0
    for tune in TUNES:
        if raw_central_counts.get(tune) != origin_counts.get(tune):
            raise GateFailure(
                f"raw validator/origin audit unresolved counts differ for {tune}"
            )
        for logical_id, (threshold, _, _, _) in PROFILES.items():
            rows = [
                row
                for row in raw_evidence
                if row["tune"] == tune and row["logical_id"] == logical_id
            ]
            if len(rows) != 1:
                raise GateFailure(
                    f"raw unresolved evidence missing for {tune}/{logical_id}"
                )
            combined = (
                rows[0]["unresolved_charm_trigger_candidates"]
                + rows[0]["unresolved_beauty_trigger_candidates"]
            )
            if pthat_counts.get(tune, {}).get(threshold) != combined:
                raise GateFailure(
                    f"pTHat/raw unresolved counts differ for {tune}/{threshold}"
                )
            if logical_id == 0 and combined != sum(origin_counts[tune].values()):
                raise GateFailure(
                    f"pTHat/origin audit unresolved counts differ for {tune}"
                )
            total += combined
    return total


def decide_state(
    unresolved_total: int,
    pthat_outcome: str,
    pthat_blockers: list[str],
) -> tuple[str, str | None, int]:
    if pthat_blockers:
        return (
            "FAIL",
            "predeclared pTHat decision retains blocking evidence: "
            + "; ".join(pthat_blockers[:10]),
            2,
        )
    if unresolved_total:
        return (
            "NEEDS_SIGNOFF",
            f"{unresolved_total} unresolved publication-trigger candidates "
            "require explicit project-owner physics review; no sign-off was "
            "created or inferred",
            3,
        )
    if pthat_outcome != "PASS":
        return (
            "FAIL",
            f"predeclared pTHat sensitivity outcome is {pthat_outcome}, not PASS",
            2,
        )
    return "PASS", None, 0


def seal_tree(path: Path, *, seal_root: bool = True) -> None:
    files = sorted(
        (candidate for candidate in path.rglob("*") if candidate.is_file()),
        key=lambda candidate: len(candidate.parts),
        reverse=True,
    )
    directories = sorted(
        (candidate for candidate in path.rglob("*") if candidate.is_dir()),
        key=lambda candidate: len(candidate.parts),
        reverse=True,
    )
    for candidate in files:
        if candidate.is_symlink():
            raise GateFailure(f"refusing to seal symlink output: {candidate}")
        os.chmod(candidate, 0o444)
    for candidate in directories:
        if candidate.is_symlink():
            raise GateFailure(f"refusing to seal symlink directory: {candidate}")
        os.chmod(candidate, 0o555)
    if seal_root:
        os.chmod(path, 0o555)


def execute(
    campaign_dir: Path,
    production: Path,
    pthat_path: Path,
    output_dir: Path,
    checkout: Path,
) -> tuple[int, Path]:
    campaign_dir = campaign_dir.resolve()
    production = production.resolve()
    pthat_path = pthat_path.resolve()
    checkout = checkout.resolve()
    output_dir = output_dir.absolute()
    output_dir = output_dir.parent.resolve() / output_dir.name
    try:
        output_dir.relative_to(checkout)
    except ValueError as error:
        raise GateFailure(
            "canonical Gate-B output directory must be inside the checkout"
        ) from error
    if output_dir.exists() or output_dir.is_symlink():
        raise GateFailure(f"refusing to alter existing Gate-B output: {output_dir}")
    commit, allowed_untracked = validate_checkout(
        checkout, (campaign_dir, production, pthat_path.parent)
    )
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = output_dir.parent / f".{output_dir.name}.partial.{os.getpid()}"
    if staging.exists() or staging.is_symlink():
        raise GateFailure(f"Gate-B staging path already exists: {staging}")
    staging.mkdir(mode=0o700)

    commands: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "schema": REPORT_SCHEMA,
        "state": "FAIL",
        "canonical": False,
        "failure": None,
        "repository_commit": None,
        "campaign": None,
        "campaign_ordinal": None,
        "created_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "commands": commands,
        "checkout_state": {
            "tracked_clean": True,
            "allowed_untracked_operational_paths": allowed_untracked,
        },
    }
    exit_code = 2
    try:
        report["repository_commit"] = commit
        campaign, rows, selected = validate_campaign(
            checkout, campaign_dir, production, commit
        )
        report["campaign"] = campaign["campaign"]
        report["campaign_ordinal"] = campaign["campaign_ordinal"]
        campaign_log = staging / "campaign_validation.log"
        campaign_command = run_command(
            [
                sys.executable,
                str(checkout / "tools/campaign_manifest.py"),
                "validate",
                str(campaign_dir),
                "--implementation-policy",
                "exact",
                "--checkout-root",
                str(checkout),
            ],
            campaign_log,
        )
        campaign_command["purpose"] = "canonical_gate_b_campaign_validation"
        commands.append(campaign_command)
        if (
            campaign_command["returncode"] != 0
            or campaign_command["compiler_warning_found"]
        ):
            raise GateFailure("canonical Gate-B campaign validator failed")
        claim, record, submission_evidence = validate_submission(
            campaign_dir, production, campaign, rows
        )
        raw_evidence, raw_unresolved = validate_raw_outputs(
            checkout, production, campaign, selected, claim
        )
        pthat_recheck = recheck_pthat_decision(
            checkout,
            campaign_dir,
            production,
            pthat_path,
            staging,
            commands,
        )
        (
            pthat_report,
            pthat_unresolved,
            pthat_nonpass,
            pthat_blockers,
        ) = validate_pthat_report(checkout, campaign_dir, campaign, rows, pthat_path)
        associate_origin_evidence = central_associate_origin_evidence(
            pthat_report
        )
        resource_evidence = audit_resource_metadata(
            production, selected, staging, commands
        )
        raw_by_identity = {
            (row["tune"], row["logical_id"]): row for row in raw_evidence
        }
        if any(
            resource["heavy_stability_rows"]
            != raw_by_identity[(resource["tune"], resource["logical_id"])][
                "stability_rows"
            ]
            for resource in resource_evidence
        ):
            raise GateFailure(
                "ROOT resource audit and immutable raw-validation logs "
                "disagree on heavy-stability row counts"
            )
        tune_evidence = audit_tune_settings(
            checkout, production, staging, commands
        )
        origin_evidence, origin_unresolved = audit_origins(
            checkout, production, staging, commands
        )
        unresolved_total = reconcile_unresolved(
            raw_evidence,
            raw_unresolved,
            origin_unresolved,
            pthat_unresolved,
        )
        log_path, log_sha = combine_log(staging, commands)
        report.update(
            {
                "canonical": True,
                "failure": None,
                "campaign_manifest": {
                    "path": str(
                        (campaign_dir / "campaign.json").relative_to(checkout)
                    ),
                    "sha256": sha256(campaign_dir / "campaign.json"),
                    "candidate_manifest_path": str(
                        (campaign_dir / "candidate_manifest.jsonl").relative_to(
                            checkout
                        )
                    ),
                    "candidate_manifest_sha256": sha256(
                        campaign_dir / "candidate_manifest.jsonl"
                    ),
                    "seed_ledger_path": str(
                        (campaign_dir / "seed_ledger.jsonl").relative_to(checkout)
                    ),
                    "seed_ledger_sha256": sha256(
                        campaign_dir / "seed_ledger.jsonl"
                    ),
                    "jobs": 9,
                    "central_successes_per_tune": 1_000_000,
                    "pthat_thresholds": ["0.5", "1.0", "2.0"],
                },
                "submission_evidence": submission_evidence,
                "raw_validation_evidence": raw_evidence,
                "raw_validation_count": len(raw_evidence),
                "resource_metadata_evidence": resource_evidence,
                "heavy_stability_audit": {
                    "validation": (
                        "Every raw PASS receipt binds the exhaustive validator; "
                        "the validator independently reconstructs the complete "
                        "heavy-stability tree and digest, requires every heavy "
                        "hadron final_may_decay=0, and checks antiparticle and "
                        "heavy-content closure."
                    ),
                    "row_count": raw_evidence[0]["stability_rows"],
                    "consistent_across_nine_jobs": True,
                    "schema": resource_evidence[0][
                        "heavy_stability_audit_schema"
                    ],
                    "sha256": resource_evidence[0][
                        "heavy_stability_audit_sha256"
                    ],
                    "validator_macro_sha256": sha256(
                        checkout / "Validation/ValidateRawOutput.C"
                    ),
                },
                "tune_settings_audit": tune_evidence,
                "origin_resolution_audits": origin_evidence,
                "central_associate_origin_composition": (
                    associate_origin_evidence
                ),
                "unresolved_trigger_candidates": {
                    "central_by_tune_and_sector": origin_unresolved,
                    "all_samples_by_tune_threshold_and_sector": {
                        f"{row['tune']}:{row['pthat_min']}": {
                            "charm": row[
                                "unresolved_charm_trigger_candidates"
                            ],
                            "beauty": row[
                                "unresolved_beauty_trigger_candidates"
                            ],
                        }
                        for row in raw_evidence
                    },
                    "all_nine_samples_total": unresolved_total,
                    "policy": (
                        "zero is required for autonomous PASS; any nonzero "
                        "count requires explicit project-owner physics sign-off"
                    ),
                },
                "pthat_sensitivity": {
                    "path": str(pthat_path),
                    "sha256": sha256(pthat_path),
                    "schema": pthat_report["schema"],
                    "outcome": pthat_report["outcome"],
                    "comparison_count": len(pthat_report["comparisons"]),
                    "nonpass_reasons": pthat_nonpass,
                    "blocking_reasons": pthat_blockers,
                    "reuse_only_recheck": pthat_recheck,
                },
                "runtime_storage_benchmark": [],
                "log_path": log_path,
                "log_sha256": log_sha,
            }
        )
        resources = {
            (row["tune"], row["logical_id"]): row
            for row in resource_evidence
        }
        for row in raw_evidence:
            resource = resources[(row["tune"], row["logical_id"])]
            report["runtime_storage_benchmark"].append(
                {
                    "tune": row["tune"],
                    "logical_id": row["logical_id"],
                    "purpose": row["purpose"],
                    "requested_successes": row["requested_successes"],
                    "elapsed_seconds": row["elapsed_seconds"],
                    "peak_rss_kib": resource["peak_rss_kib"],
                    "raw_bytes": row["raw_bytes"],
                    "bytes_per_successful_event": (
                        row["raw_bytes"] / row["requested_successes"]
                    ),
                    "root_compression_settings": resource[
                        "compression_settings"
                    ],
                    "root_compression_algorithm": resource[
                        "compression_algorithm"
                    ],
                    "root_compression_level": resource[
                        "compression_level"
                    ],
                    "root_compression_factor": resource[
                        "compression_factor"
                    ],
                }
            )
        candidate_slots = {
            "MONASH": 100,
            "JUNCTIONS": 200,
            "CLOSEPACKING": 200,
        }
        projection_rows: list[dict[str, Any]] = []
        for tune in TUNES:
            observed = next(
                row
                for row in report["runtime_storage_benchmark"]
                if row["tune"] == tune and row["logical_id"] == 0
            )
            slots = candidate_slots[tune]
            projection_rows.append(
                {
                    "tune": tune,
                    "candidate_jobs": slots,
                    "successful_events_per_job": 1_000_000,
                    "projected_successful_events": slots * 1_000_000,
                    "observed_central_pilot_elapsed_seconds": observed[
                        "elapsed_seconds"
                    ],
                    "projected_aggregate_cpu_hours": (
                        observed["elapsed_seconds"] * slots / 3600.0
                    ),
                    "observed_central_pilot_raw_bytes": observed["raw_bytes"],
                    "projected_raw_bytes": observed["raw_bytes"] * slots,
                    "observed_peak_rss_kib_per_job": observed["peak_rss_kib"],
                    "observed_root_compression_factor": observed[
                        "root_compression_factor"
                    ],
                }
            )
        report["full_candidate_resource_projection"] = {
            "basis": (
                "Linear projection from each tune's validated one-million-"
                "success central pilot to the declared 100/200/200 candidate "
                "launch. CPU time is aggregate, not Condor wall-clock; peak "
                "RSS is per concurrent job."
            ),
            "by_tune": projection_rows,
            "candidate_jobs": sum(candidate_slots.values()),
            "projected_successful_events": sum(
                row["projected_successful_events"] for row in projection_rows
            ),
            "projected_aggregate_cpu_hours": sum(
                row["projected_aggregate_cpu_hours"] for row in projection_rows
            ),
            "projected_raw_bytes": sum(
                row["projected_raw_bytes"] for row in projection_rows
            ),
        }
        report["canonical_300m_resource_projection"] = {
            "basis": (
                "Linear storage/CPU projection for the eventual exact "
                "100-job-per-tune canonical freeze; reserve selection is not "
                "a license to combine more than 100 logical jobs per tune."
            ),
            "canonical_jobs": 300,
            "projected_successful_events": 300_000_000,
            "projected_aggregate_cpu_hours": sum(
                next(
                    row["elapsed_seconds"]
                    for row in report["runtime_storage_benchmark"]
                    if row["tune"] == tune and row["logical_id"] == 0
                )
                * 100
                / 3600.0
                for tune in TUNES
            ),
            "projected_raw_bytes": sum(
                next(
                    row["raw_bytes"]
                    for row in report["runtime_storage_benchmark"]
                    if row["tune"] == tune and row["logical_id"] == 0
                )
                * 100
                for tune in TUNES
            ),
        }
        report["state"], report["failure"], exit_code = decide_state(
            unresolved_total,
            pthat_report["outcome"],
            pthat_blockers,
        )
        if report["state"] == "PASS" and (
            not commands
            or any(
                type(command.get("returncode")) is not int
                or command["returncode"] != 0
                or command.get("compiler_warning_found") is not False
                for command in commands
            )
        ):
            raise GateFailure(
                "PASS is forbidden without all-zero integer command evidence "
                "and compiler_warning_found=false"
            )
        aggregate_log = staging / report["log_path"]
        with aggregate_log.open("a") as stream:
            stream.write(
                "GATE_B_AGGREGATE "
                f"state={report['state']} canonical=true "
                f"repository_commit={commit} raw_files={len(raw_evidence)} "
                f"central_million_event_pilots=3 "
                f"pthat_sensitivity_pilots=6 "
                f"pthat_outcome={pthat_report['outcome']} "
                f"unresolved_trigger_candidates={unresolved_total}\n"
            )
        report["log_sha256"] = sha256(aggregate_log)
    except Exception as error:
        report["state"] = "FAIL"
        report["canonical"] = False
        report["failure"] = str(error)
        if commands:
            log_path, log_sha = combine_log(staging, commands)
            failure_log = staging / log_path
            with failure_log.open("a") as stream:
                stream.write(f"GATE_B_FAIL {error}\n")
            log_sha = sha256(failure_log)
        else:
            failure_log = staging / "gate_b.log"
            failure_log.write_text(f"GATE_B_FAIL {error}\n")
            log_path, log_sha = failure_log.name, sha256(failure_log)
        report["log_path"] = log_path
        report["log_sha256"] = log_sha
        exit_code = 2

    report_path = staging / "gate_b_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    inventory = []
    for path in sorted(candidate for candidate in staging.rglob("*") if candidate.is_file()):
        inventory.append(
            {
                "path": str(path.relative_to(staging)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    (staging / "evidence_inventory.json").write_text(
        json.dumps(
            {
                "schema": "hf_publication_gate_b_evidence_inventory_v1",
                "files": inventory,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    # macOS refuses to rename a non-writable directory even when its parent is
    # writable.  Seal every child first, promote atomically, then remove the
    # root directory's write bits immediately after the rename.
    seal_tree(staging, seal_root=False)
    os.rename(staging, output_dir)
    os.chmod(output_dir, 0o555)
    print(
        f"PUBLICATION_GATE_B state={report['state']} "
        f"canonical={str(report['canonical']).lower()} "
        f"report={output_dir / 'gate_b_report.json'}"
    )
    return exit_code, output_dir / "gate_b_report.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and seal the exact nine-job publication Gate-B evidence. "
            "Exit codes: 0 PASS, 2 FAIL, 3 NEEDS_SIGNOFF."
        )
    )
    parser.add_argument("campaign_dir", type=Path)
    parser.add_argument("production_root", type=Path)
    parser.add_argument("pthat_decision_json", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument(
        "--checkout-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    try:
        status, _ = execute(
            args.campaign_dir,
            args.production_root,
            args.pthat_decision_json,
            args.output_dir,
            args.checkout_root,
        )
        return status
    except Exception as error:
        print(f"PUBLICATION_GATE_B_SETUP_FAIL {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
