#!/usr/bin/env python3
"""Create, supersede, seal, and validate publication input manifests.

The canonical manifest is the only allowed bridge from raw production to the
paper analysis.  A freeze is deliberately two phase:

1. ``freeze`` records the exact selected raw bytes and all authorising
   production provenance in a new, empty directory.
2. ``Validation/validate_canonical_manifest.sh`` performs exhaustive ROOT
   validation and calls ``seal``.  Downstream commands accept sealed freezes
   only.

The first stage remains the exact 100-file-per-tune v2/v3 contract.  A
coverage-driven expansion is represented by a new v3/v4 canonical manifest
which records and revalidates its sealed parent and a separately authorised
extension campaign.  It never edits either source freeze.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
TUNE_ORDINAL = {tune: index for index, tune in enumerate(TUNES)}
CANONICAL_SLOTS = 100
BLOCKS = 10
ROWS = len(TUNES) * CANONICAL_SLOTS
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

RAW_SCHEMA = "hf_primary_ground_raw_v6"
ORIGIN_ALGORITHM = "signed_heavy_constituent_complete_mothers_unique_v4"
SELECTOR = "hard_trigger_primary_ground__primary_ground_associate_v1"
TUNE_ALLOWLIST_SCHEMA = "pythia_tune_difference_allowlist_v2"
ROW_SCHEMA = "hf_canonical_raw_manifest_v2"
SUMMARY_SCHEMA = "hf_canonical_freeze_summary_v3"
VALIDATION_RECEIPT_SCHEMA = "hf_canonical_raw_validation_receipt_v2"
SEAL_SCHEMA = "hf_canonical_freeze_seal_v2"
SUPERSEDING_ROW_SCHEMA = "hf_superseding_canonical_raw_manifest_v3"
SUPERSEDING_SUMMARY_SCHEMA = "hf_superseding_canonical_freeze_summary_v4"
SUPERSEDING_VALIDATION_RECEIPT_SCHEMA = (
    "hf_superseding_canonical_raw_validation_receipt_v3"
)
SUPERSEDING_SEAL_SCHEMA = "hf_superseding_canonical_freeze_seal_v3"
EXTENSION_ROW_SCHEMA = "hf_equal_tune_extension_raw_manifest_v1"
EXTENSION_SUMMARY_SCHEMA = "hf_equal_tune_extension_freeze_summary_v1"
EXTENSION_VALIDATION_RECEIPT_SCHEMA = (
    "hf_equal_tune_extension_raw_validation_receipt_v1"
)
EXTENSION_SEAL_SCHEMA = "hf_equal_tune_extension_freeze_seal_v1"
EXPANSION_CAMPAIGN_KIND = "equal_tune_canonical_expansion_v1"
VALIDATION_RECEIPT_NAME = "canonical_raw_validation_receipt.json"
VALIDATION_LOG_NAME = "canonical_raw_validation.log"
SEAL_NAME = "freeze_seal.json"
FULL_CLAIM = (
    Path("submission_receipts")
    / "full_candidates_attempt0_submission_claim.json"
)
FULL_RECORD = (
    Path("submission_receipts") / "full_candidates_attempt0_submitted.json"
)
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")

ROW_KEYS = {
    "schema",
    "campaign",
    "campaign_ordinal",
    "tune",
    "tune_ordinal",
    "canonical_slot",
    "block",
    "block_position",
    "logical_id",
    "role",
    "attempt",
    "seed",
    "requested_successes",
    "pthat_min_override",
    "effective_pthat_min",
    "multiplicity_audit_events",
    "effective_card_sha256",
    "producer_executable_sha256",
    "repository_commit",
    "raw_schema",
    "origin_algorithm",
    "selector",
    "species_registry_sha256",
    "pair_registry_sha256",
    "tune_difference_allowlist_schema",
    "tune_difference_allowlist_sha256",
    "raw_path",
    "raw_bytes",
    "raw_sha256",
    "attempt_start_claim_path",
    "attempt_start_claim_sha256",
    "producing_cluster_id",
    "producing_process_id",
    "attempt_receipt_path",
    "attempt_receipt_sha256",
    "raw_validation_receipt_path",
    "raw_validation_receipt_sha256",
    "raw_validation_log_path",
    "raw_validation_log_sha256",
    "allocation_authorization_path",
    "allocation_authorization_sha256",
    "submission_record_path",
    "submission_record_sha256",
    "validation_receipt_path",
    "selection_reason",
    "selection_approval",
    "production_definition_sha256",
}
SUPERSEDING_ROW_EXTRA_KEYS = {
    "final_campaign",
    "final_campaign_ordinal",
    "source_canonical_slot",
    "source_manifest_sha256",
    "source_freeze_summary_sha256",
    "source_freeze_seal_sha256",
    "source_production_prefix",
    "source_production_definition_sha256",
}
SUPERSEDING_ROW_KEYS = ROW_KEYS | SUPERSEDING_ROW_EXTRA_KEYS


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return value


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    try:
        lines = path.read_text().splitlines()
    except OSError as error:
        raise ValueError(f"cannot read JSONL {path}: {error}") from error
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON {path}:{number}: {error}") from error
        if not isinstance(row, dict):
            raise ValueError(f"expected object at {path}:{number}")
        rows.append(row)
    return rows


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def jsonl_text(rows: list[dict]) -> str:
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def exclusive_write(path: Path, text: str) -> None:
    """Create a write-once record; an existing path is never overwritten."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        # Leave a partial file as a fail-closed marker.
        raise


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def relative_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a nonempty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label} escapes its declared root: {value!r}")
    return path


def require_hex(value: object, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValueError(f"invalid {label}: {value!r}")
    return value


def require_int(value: object, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"invalid {label}: {value!r}")
    return value


def manifest_shape(summary: dict) -> tuple[int, int, str, str, str, str]:
    """Return dynamic shape and schema contracts without weakening v2."""
    schema = summary.get("schema")
    if schema == SUMMARY_SCHEMA:
        jobs_per_tune = CANONICAL_SLOTS
        row_schema = ROW_SCHEMA
        receipt_schema = VALIDATION_RECEIPT_SCHEMA
        seal_schema = SEAL_SCHEMA
    elif schema in {
        SUPERSEDING_SUMMARY_SCHEMA,
        EXTENSION_SUMMARY_SCHEMA,
    }:
        minimum = 100 if schema == SUPERSEDING_SUMMARY_SCHEMA else 10
        jobs_per_tune = require_int(
            summary.get("jobs_per_tune"), "dynamic jobs per tune", minimum
        )
        if jobs_per_tune % BLOCKS:
            raise ValueError(
                "superseding jobs per tune must be divisible by ten"
            )
        if schema == SUPERSEDING_SUMMARY_SCHEMA:
            row_schema = SUPERSEDING_ROW_SCHEMA
            receipt_schema = SUPERSEDING_VALIDATION_RECEIPT_SCHEMA
            seal_schema = SUPERSEDING_SEAL_SCHEMA
        else:
            row_schema = EXTENSION_ROW_SCHEMA
            receipt_schema = EXTENSION_VALIDATION_RECEIPT_SCHEMA
            seal_schema = EXTENSION_SEAL_SCHEMA
    else:
        raise ValueError("canonical freeze summary schema differs")
    rows = len(TUNES) * jobs_per_tune
    return (
        jobs_per_tune,
        rows,
        row_schema,
        schema,
        receipt_schema,
        seal_schema,
    )


def source_freeze_identity(directory: Path) -> dict:
    """Read and checksum a sealed source freeze after strict validation."""
    validate_directory(directory, require_seal=True)
    summary_path = directory / "freeze_summary.json"
    manifest_path = directory / "canonical_manifest.jsonl"
    seal_path = directory / SEAL_NAME
    summary = read_json(summary_path)
    jobs_per_tune, _, _, _, _, _ = manifest_shape(summary)
    identity = {
        "campaign": summary["campaign"],
        "campaign_ordinal": summary["campaign_ordinal"],
        "jobs_per_tune": jobs_per_tune,
        "successful_events_per_job": summary["successful_events_per_job"],
        "successful_events_per_tune": summary[
            "successful_events_per_tune"
        ],
        "canonical_manifest_sha256": digest(manifest_path),
        "freeze_summary_sha256": digest(summary_path),
        "freeze_seal_sha256": digest(seal_path),
        "physics_origin_signoff_sha256": summary[
            "physics_origin_signoff_sha256"
        ],
        "full_production_gate_authorization_sha256": summary[
            "full_production_gate_authorization_sha256"
        ],
        "registry_baseline_sha256": summary[
            "registry_baseline_sha256"
        ],
        "global_submission_claim_sha256": summary[
            "global_submission_claim_sha256"
        ],
    }
    if "equal_tune_expansion_authorization_sha256" in summary:
        identity["equal_tune_expansion_authorization_sha256"] = summary[
            "equal_tune_expansion_authorization_sha256"
        ]
    return identity


def git_output(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPOSITORY_ROOT), *arguments], text=True
    ).strip()


def require_clean_checkout() -> str:
    current_commit = git_output("rev-parse", "HEAD")
    require_hex(current_commit, HEX40, "freeze checkout commit")
    tracked_dirty = git_output(
        "status", "--porcelain", "--untracked-files=no"
    )
    if tracked_dirty:
        raise ValueError("refusing to freeze from a tracked-dirty repository")
    return current_commit


def require_ancestor(ancestor: str, descendant: str) -> None:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(REPOSITORY_ROOT),
            "merge-base",
            "--is-ancestor",
            ancestor,
            descendant,
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        raise ValueError(
            f"production commit {ancestor} is not an ancestor of "
            f"freeze commit {descendant}"
        )


def parse_card_pthat_min(card: Path) -> float:
    result: float | None = None
    for source_line in card.read_text().splitlines():
        line = source_line.split("!", 1)[0].split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if key == "PhaseSpace:pTHatMin":
            result = float(value)
    if result is None or not math.isfinite(result) or result < 0:
        raise ValueError(f"cannot establish PhaseSpace:pTHatMin from {card}")
    return result


def production_definition(row: dict) -> str:
    fields = {
        key: row[key]
        for key in (
            "campaign",
            "campaign_ordinal",
            "tune",
            "canonical_slot",
            "logical_id",
            "role",
            "attempt",
            "seed",
            "requested_successes",
            "pthat_min_override",
            "effective_pthat_min",
            "multiplicity_audit_events",
            "effective_card_sha256",
            "producer_executable_sha256",
            "repository_commit",
            "raw_schema",
            "origin_algorithm",
            "selector",
            "species_registry_sha256",
            "pair_registry_sha256",
            "tune_difference_allowlist_schema",
            "tune_difference_allowlist_sha256",
            "raw_path",
            "raw_bytes",
            "raw_sha256",
            "attempt_start_claim_sha256",
            "producing_cluster_id",
            "producing_process_id",
            "attempt_receipt_sha256",
            "raw_validation_receipt_sha256",
            "raw_validation_log_sha256",
            "allocation_authorization_sha256",
            "submission_record_sha256",
        )
    }
    return text_digest(canonical_json(fields))


def scientific_production_definition(row: dict) -> str:
    """Hash fields that must match when independent campaigns are pooled."""
    fields = {
        key: row[key]
        for key in (
            "tune",
            "requested_successes",
            "pthat_min_override",
            "effective_pthat_min",
            "multiplicity_audit_events",
            "effective_card_sha256",
            "producer_executable_sha256",
            "raw_schema",
            "origin_algorithm",
            "selector",
            "species_registry_sha256",
            "pair_registry_sha256",
            "tune_difference_allowlist_schema",
            "tune_difference_allowlist_sha256",
        )
    }
    return text_digest(canonical_json(fields))


def validate_submission_receipts(
    campaign_dir: Path, production_root: Path, campaign: dict
) -> tuple[dict, str, str, dict[str, str]]:
    claim_path = production_root / FULL_CLAIM
    record_path = production_root / FULL_RECORD
    if (
        claim_path.is_symlink()
        or record_path.is_symlink()
        or not claim_path.is_file()
        or not record_path.is_file()
    ):
        raise FileNotFoundError(
            "immutable full-production submission claim/record is absent"
        )
    claim = read_json(claim_path)
    record = read_json(record_path)
    campaign_commit = campaign.get("repository_commit")
    expected_claim = {
        "schema": "hf_full_submission_claim_v1",
        "state": "claimed_before_condor_submit",
        "submission_kind": "full",
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
        "repository_commit": campaign_commit,
        "campaign_json_sha256": digest(campaign_dir / "campaign.json"),
        "candidate_manifest_sha256": digest(
            campaign_dir / "candidate_manifest.jsonl"
        ),
    }
    for key, expected in expected_claim.items():
        if claim.get(key) != expected:
            raise ValueError(
                f"full-production submission claim {key} differs: "
                f"{claim.get(key)!r} != {expected!r}"
            )
    producer_sha = require_hex(
        claim.get("producer_executable_sha256"),
        HEX64,
        "producer executable SHA-256",
    )
    prefix_bytes = require_int(
        claim.get("seed_ledger_prefix_bytes"),
        "claimed seed-ledger prefix length",
        1,
    )
    ledger_bytes = (campaign_dir / "seed_ledger.jsonl").read_bytes()
    if len(ledger_bytes) < prefix_bytes:
        raise ValueError("seed ledger is shorter than its immutable claim prefix")
    if (
        hashlib.sha256(ledger_bytes[:prefix_bytes]).hexdigest()
        != claim.get("seed_ledger_sha256")
    ):
        raise ValueError("claimed seed-ledger prefix checksum differs")
    expected_candidates = sum(
        int(value) for value in campaign["candidate_slots"].values()
    )
    if len(claim.get("allocations", [])) != expected_candidates:
        raise ValueError(
            f"full submission claim does not bind all {expected_candidates} candidates"
        )
    submit_file = production_root / "submit_candidates.sub"
    if (
        submit_file.is_symlink()
        or not submit_file.is_file()
        or digest(submit_file) != claim.get("submit_file_sha256")
    ):
        raise ValueError("full-candidate submit file differs from its claim")
    expected_record = {
        "schema": "hf_full_submission_record_v1",
        "state": "condor_submit_succeeded",
        "submission_kind": "full",
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
        "claim_sha256": digest(claim_path),
        "condor_first_process": 0,
        "condor_last_process": expected_candidates - 1,
        "condor_process_count": expected_candidates,
    }
    for key, expected in expected_record.items():
        if record.get(key) != expected:
            raise ValueError(
                f"full-production submission record {key} differs"
            )

    signoff_path = campaign_dir / "PHYSICS_ORIGIN_SIGNOFF.json"
    gate_authorization_path = (
        campaign_dir / "FULL_PRODUCTION_GATE_AUTHORIZATION.json"
    )
    required_authorizations = [
        ("physics-origin sign-off", signoff_path),
        ("full-production gate authorization", gate_authorization_path),
    ]
    expansion_authorization_path = (
        campaign_dir / "EQUAL_TUNE_EXPANSION_AUTHORIZATION.json"
    )
    if campaign.get("campaign_kind") == EXPANSION_CAMPAIGN_KIND:
        required_authorizations.append(
            (
                "equal-tune expansion authorization",
                expansion_authorization_path,
            )
        )
    for label, source in required_authorizations:
        if source.is_symlink() or not source.is_file():
            raise FileNotFoundError(f"{label} is absent: {source}")
    signoff_sha = digest(signoff_path)
    gate_authorization_sha = digest(gate_authorization_path)
    expansion_authorization_sha = (
        digest(expansion_authorization_path)
        if campaign.get("campaign_kind") == EXPANSION_CAMPAIGN_KIND
        else None
    )
    if claim.get("physics_origin_signoff_sha256") != signoff_sha:
        raise ValueError(
            "full-production claim physics-origin sign-off checksum differs"
        )
    if (
        claim.get("full_production_gate_authorization_sha256")
        != gate_authorization_sha
    ):
        raise ValueError(
            "full-production claim gate-authorization checksum differs"
        )
    if (
        expansion_authorization_sha is not None
        and claim.get("equal_tune_expansion_authorization_sha256")
        != expansion_authorization_sha
    ):
        raise ValueError(
            "full-production claim equal-tune expansion authorization differs"
        )
    gate_authorization = read_json(gate_authorization_path)
    gate_expected = {
        "schema": "hf_full_production_gate_authorization_v1",
        "approved": True,
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
        "repository_commit": campaign_commit,
        "physics_origin_signoff_sha256": signoff_sha,
    }
    for key, expected in gate_expected.items():
        if gate_authorization.get(key) != expected:
            raise ValueError(
                f"full-production gate authorization {key} differs at freeze"
            )

    repository_identity = claim.get("repository_identity")
    registry_value = claim.get("global_submission_registry")
    if (
        not isinstance(repository_identity, str)
        or not repository_identity
        or not isinstance(registry_value, str)
    ):
        raise ValueError("full-production claim lacks global registry identity")
    registry = Path(registry_value)
    if not registry.is_absolute() or registry.is_symlink() or not registry.is_dir():
        raise ValueError("full-production global registry path is invalid")
    baseline_path = registry / "reservation_baseline.json"
    if baseline_path.is_symlink() or not baseline_path.is_file():
        raise FileNotFoundError(
            "reviewed global seed-reservation baseline is absent"
        )
    baseline_sha = digest(baseline_path)
    if claim.get("registry_baseline_sha256") != baseline_sha:
        raise ValueError(
            "full-production claim registry-baseline checksum differs"
        )
    baseline = read_json(baseline_path)
    if (
        baseline.get("schema") != "hf_submission_registry_baseline_v1"
        or baseline.get("repository_identity") != repository_identity
        or not isinstance(baseline.get("reviewer"), str)
        or not baseline["reviewer"].strip()
    ):
        raise ValueError("global seed-reservation baseline is malformed")

    global_claim_path = (
        registry / "claims" / f"{campaign['campaign']}.json"
    )
    if global_claim_path.is_symlink() or not global_claim_path.is_file():
        raise FileNotFoundError("global full-production reservation is absent")
    global_claim = read_json(global_claim_path)
    global_expected = {
        "schema": "hf_global_submission_claim_v1",
        "state": "reserved_before_condor_submit",
        "repository_identity": repository_identity,
        "global_submission_registry": str(registry),
        "registry_baseline_sha256": baseline_sha,
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
        "submission_kind": "full",
        "repository_commit": campaign_commit,
        "physics_origin_signoff_sha256": signoff_sha,
        "full_production_gate_authorization_sha256":
            gate_authorization_sha,
        "reserved_seed_intervals": claim.get("reserved_seed_intervals"),
        "local_receipt_sha256": digest(claim_path),
    }
    if expansion_authorization_sha is not None:
        global_expected[
            "equal_tune_expansion_authorization_sha256"
        ] = expansion_authorization_sha
    for key, expected in global_expected.items():
        if global_claim.get(key) != expected:
            raise ValueError(
                f"global full-production reservation {key} differs at freeze"
            )
    provenance = {
        "physics_origin_signoff_sha256": signoff_sha,
        "full_production_gate_authorization_sha256":
            gate_authorization_sha,
        "registry_baseline_sha256": baseline_sha,
        "global_submission_claim_sha256": digest(global_claim_path),
    }
    if expansion_authorization_sha is not None:
        provenance[
            "equal_tune_expansion_authorization_sha256"
        ] = expansion_authorization_sha
    return claim, producer_sha, digest(record_path), provenance


def validate_attempt_start_claim(
    production_root: Path, expected: dict
) -> tuple[Path, str, str, str]:
    relative = (
        Path("attempt_starts")
        / expected["tune"]
        / f"job_{expected['logical_id']:03d}"
        / f"attempt_{expected['attempt']:03d}.json"
    )
    path = production_root / relative
    if path.is_symlink() or not path.is_file():
        raise FileNotFoundError(f"attempt-start claim is absent: {path}")
    claim = read_json(path)
    exact = {
        "schema": "hf_attempt_start_claim_v1",
        "state": "claimed_before_producer_execution",
        "campaign": expected["campaign"],
        "campaign_ordinal": expected["campaign_ordinal"],
        "tune": expected["tune"],
        "logical_id": expected["logical_id"],
        "role": expected["role"],
        "attempt": expected["attempt"],
        "seed": expected["seed"],
        "requested_successes": expected["requested_successes"],
        "repository_commit": expected["repository_commit"],
        "effective_card_sha256": expected["effective_card_sha256"],
        "producer_executable_sha256": expected[
            "producer_executable_sha256"
        ],
    }
    for key, value in exact.items():
        if claim.get(key) != value:
            raise ValueError(f"attempt-start claim {key} differs")
    cluster = claim.get("cluster_id")
    process = claim.get("process_id")
    for label, value in (("cluster_id", cluster), ("process_id", process)):
        if not isinstance(value, str) or not re.fullmatch(
            r"[A-Za-z0-9._-]+", value
        ):
            raise ValueError(f"attempt-start {label} is invalid")
    return relative, digest(path), cluster, process


def find_attempt_receipt(
    production_root: Path,
    expected: dict,
    raw_sha256: str,
    raw_bytes: int,
) -> tuple[Path, str]:
    directory = production_root / "attempt_metadata" / expected["tune"]
    pattern = (
        f"hf_{expected['tune']}_job{expected['logical_id']:03d}_"
        f"attempt{expected['attempt']:03d}_*.json"
    )
    matches: list[tuple[Path, dict]] = []
    for path in sorted(directory.glob(pattern)):
        if path.is_symlink() or not path.is_file():
            continue
        receipt = read_json(path)
        exact = {
            "campaign": expected["campaign"],
            "campaign_ordinal": expected["campaign_ordinal"],
            "tune": expected["tune"],
            "logical_id": expected["logical_id"],
            "role": expected["role"],
            "attempt": expected["attempt"],
            "seed": expected["seed"],
            "requested_successes": expected["requested_successes"],
            "pthat_min_override": expected["pthat_min_override"],
            "multiplicity_audit_events": expected[
                "multiplicity_audit_events"
            ],
            "repository_commit": expected["repository_commit"],
            "effective_card_sha256": expected["effective_card_sha256"],
            "producer_executable_sha256": expected[
                "producer_executable_sha256"
            ],
            "attempt_start_claim_sha256": expected[
                "attempt_start_claim_sha256"
            ],
            "cluster_id": expected["producing_cluster_id"],
            "process_id": expected["producing_process_id"],
            "producer_exit": 0,
            "partial_sha256": raw_sha256,
            "partial_bytes": raw_bytes,
        }
        start_path = receipt.get("attempt_start_claim_path")
        start_matches = (
            isinstance(start_path, str)
            and Path(start_path).resolve()
            == (
                production_root / expected["attempt_start_claim_path"]
            ).resolve()
        )
        if start_matches and all(
            receipt.get(key) == value for key, value in exact.items()
        ):
            matches.append((path, receipt))
    if len(matches) != 1:
        raise ValueError(
            "expected exactly one successful attempt receipt for "
            f"{expected['tune']}/{expected['logical_id']}/"
            f"{expected['attempt']}, found {len(matches)}"
        )
    path = matches[0][0]
    return path.relative_to(production_root), digest(path)


def validate_raw_validation_receipt(
    production_root: Path,
    expected: dict,
    raw_sha256: str,
    raw_bytes: int,
) -> tuple[Path, str, Path, str]:
    base = (
        Path("raw_validation")
        / expected["tune"]
        / f"job_{expected['logical_id']:03d}"
        / f"attempt_{expected['attempt']:03d}"
    )
    receipt_path = base / "receipt.json"
    log_path = base / "validate_raw_output.log"
    full_receipt = production_root / receipt_path
    full_log = production_root / log_path
    for label, path in (
        ("raw-validation receipt", full_receipt),
        ("raw-validation log", full_log),
    ):
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(f"{label} is absent: {path}")
    receipt = read_json(full_receipt)
    exact = {
        "schema": "hf_raw_validation_receipt_v1",
        "result": "PASS",
        "validator_exit_status": 0,
        "output_sha256": raw_sha256,
        "output_bytes": raw_bytes,
        "validation_log_name": full_log.name,
        "validation_log_sha256": digest(full_log),
    }
    for key, value in exact.items():
        if receipt.get(key) != value:
            raise ValueError(
                f"raw-validation receipt {key} differs for "
                f"{expected['tune']}/{expected['logical_id']}/"
                f"{expected['attempt']}"
            )
    expected_provenance = {
        "campaign": expected["campaign"],
        "campaign_ordinal": expected["campaign_ordinal"],
        "tune": expected["tune"],
        "logical_id": expected["logical_id"],
        "role": expected["role"],
        "attempt": expected["attempt"],
        "seed": expected["seed"],
        "requested_successes": expected["requested_successes"],
        "phase_space_pthat_min": expected["effective_pthat_min"],
        "multiplicity_audit_events": expected[
            "multiplicity_audit_events"
        ],
        "repository_commit": expected["repository_commit"],
        "effective_card_sha256": expected["effective_card_sha256"],
        "producer_executable_sha256": expected[
            "producer_executable_sha256"
        ],
        "attempt_start_claim_sha256": expected[
            "attempt_start_claim_sha256"
        ],
        "cluster_id": expected["producing_cluster_id"],
        "process_id": expected["producing_process_id"],
    }
    if receipt.get("expected_provenance") != expected_provenance:
        raise ValueError("raw-validation receipt expected provenance differs")
    for key in ("validator_wrapper_sha256", "validator_macro_sha256"):
        require_hex(receipt.get(key), HEX64, f"raw-validation {key}")
    dependencies = receipt.get("validator_dependency_sha256")
    if not isinstance(dependencies, dict) or not dependencies:
        raise ValueError("raw-validation dependency checksum map is absent")
    for key, value in dependencies.items():
        if not isinstance(key, str) or not key:
            raise ValueError("raw-validation dependency name is invalid")
        require_hex(value, HEX64, f"raw-validation dependency {key}")
    log_text = full_log.read_text(errors="replace")
    if (
        "RAW_VALIDATION_SUMMARY errors=0 " not in log_text
        or "RAW_VALIDATION_ERROR" in log_text
        or re.search(
            r"segmentation violation|Break +segmentation|cling JIT session error",
            log_text,
        )
    ):
        raise ValueError("raw-validation log does not certify PASS")
    return receipt_path, digest(full_receipt), log_path, digest(full_log)


def authorization_for(
    production_root: Path,
    campaign_dir: Path,
    claim: dict,
    choice: dict,
    expected: dict,
    initial_producer_sha: str,
    full_record_sha: str,
) -> tuple[Path, str, Path, str]:
    allocation = next(
        (
            row
            for row in claim.get("allocations", [])
            if row.get("tune") == expected["tune"]
            and row.get("logical_id") == expected["logical_id"]
            and row.get("attempt") == expected["attempt"]
            and row.get("seed") == expected["seed"]
        ),
        None,
    )
    if allocation is not None:
        allocation_exact = {
            "campaign_ordinal": expected["campaign_ordinal"],
            "pthat_min_override": expected["pthat_min_override"],
            "multiplicity_audit_events": expected[
                "multiplicity_audit_events"
            ],
            "repository_commit": expected["repository_commit"],
            "effective_card_sha256": expected["effective_card_sha256"],
        }
        for key, value in allocation_exact.items():
            if allocation.get(key) != value:
                raise ValueError(
                    f"submission allocation {key} differs for "
                    f"{expected['tune']}/{expected['logical_id']}"
                )
        path = FULL_CLAIM
        return path, digest(production_root / path), FULL_RECORD, full_record_sha

    retry_stem = (
        f"{expected['tune']}_job{expected['logical_id']:03d}_"
        f"attempt{expected['attempt']:03d}"
    )
    path = (
        Path("submission_receipts") / "retries" / f"{retry_stem}_claim.json"
    )
    record_path = (
        Path("submission_receipts")
        / "retries"
        / f"{retry_stem}_submitted.json"
    )
    full_path = production_root / path
    full_record = production_root / record_path
    for label, source in (
        ("retry submission claim", full_path),
        ("retry submission record", full_record),
    ):
        if source.is_symlink() or not source.is_file():
            raise FileNotFoundError(f"{label} is absent: {source}")
    retry_claim = read_json(full_path)
    retry_record = read_json(full_record)
    expected_claim = {
        "schema": "hf_full_retry_submission_claim_v1",
        "state": "claimed_before_condor_submit",
        "submission_kind": "full_retry",
        "campaign": expected["campaign"],
        "campaign_ordinal": expected["campaign_ordinal"],
        "repository_commit": expected["repository_commit"],
        "producer_executable_sha256": initial_producer_sha,
        "initial_submission_claim_sha256": digest(
            production_root / FULL_CLAIM
        ),
    }
    for key, value in expected_claim.items():
        if retry_claim.get(key) != value:
            raise ValueError(f"retry submission claim {key} differs")
    expected_allocation = {
        "tune": expected["tune"],
        "logical_id": expected["logical_id"],
        "role": expected["role"],
        "attempt": expected["attempt"],
        "seed": expected["seed"],
        "campaign_ordinal": expected["campaign_ordinal"],
        "requested_successes": expected["requested_successes"],
        "pthat_min_override": expected["pthat_min_override"],
        "multiplicity_audit_events": expected[
            "multiplicity_audit_events"
        ],
        "repository_commit": expected["repository_commit"],
        "effective_card_sha256": expected["effective_card_sha256"],
    }
    if retry_claim.get("allocation") != expected_allocation:
        raise ValueError("retry submission allocation differs")
    prefix_bytes = require_int(
        retry_claim.get("seed_ledger_prefix_bytes"),
        "retry seed-ledger prefix bytes",
        1,
    )
    ledger = (campaign_dir / "seed_ledger.jsonl").read_bytes()
    if (
        len(ledger) < prefix_bytes
        or hashlib.sha256(ledger[:prefix_bytes]).hexdigest()
        != retry_claim.get("seed_ledger_sha256")
    ):
        raise ValueError("retry seed-ledger prefix checksum differs")
    expected_record = {
        "schema": "hf_full_retry_submission_record_v1",
        "state": "condor_submit_succeeded",
        "submission_kind": "full_retry",
        "claim_sha256": digest(full_path),
        "campaign": expected["campaign"],
        "campaign_ordinal": expected["campaign_ordinal"],
        "allocation": expected_allocation,
    }
    for key, value in expected_record.items():
        if retry_record.get(key) != value:
            raise ValueError(f"retry submission record {key} differs")
    return path, digest(full_path), record_path, digest(full_record)


def validate_lowest_valid_selection(
    rows: list[dict],
    technically_valid_ids: dict[str, set[int]],
    primary_limit: int,
    canonical_slots: int,
) -> None:
    """Enforce the predeclared, physics-blind primary/reserve policy."""
    for tune in TUNES:
        tune_rows = [row for row in rows if row["tune"] == tune]
        selected_primary = sorted(
            int(row["logical_id"])
            for row in tune_rows
            if row["role"] == "primary"
        )
        selected_reserve = sorted(
            int(row["logical_id"])
            for row in tune_rows
            if row["role"] == "reserve"
        )
        available_primary = sorted(
            logical_id
            for logical_id in technically_valid_ids[tune]
            if logical_id < primary_limit
        )
        available_reserve = sorted(
            logical_id
            for logical_id in technically_valid_ids[tune]
            if logical_id >= primary_limit
        )
        if selected_primary != available_primary:
            raise ValueError(
                f"canonical selection does not preserve every valid primary "
                f"for {tune}: selected={selected_primary} "
                f"available={available_primary}"
            )
        missing_slots = sorted(
            set(range(primary_limit)) - set(available_primary)
        )
        expected_reserve = available_reserve[: len(missing_slots)]
        if (
            len(available_primary) > canonical_slots
            or len(missing_slots) != canonical_slots - len(available_primary)
            or len(expected_reserve) != len(missing_slots)
            or selected_reserve != expected_reserve
        ):
            raise ValueError(
                f"canonical selection is not the lowest-valid equal-tune "
                f"subset for {tune}: missing_slots={missing_slots} "
                f"selected_reserves={selected_reserve} "
                f"lowest_valid_reserves={expected_reserve}"
            )
        primary_slot_pairs = sorted(
            (int(row["canonical_slot"]), int(row["logical_id"]))
            for row in tune_rows
            if row["role"] == "primary"
        )
        if any(slot != logical_id for slot, logical_id in primary_slot_pairs):
            raise ValueError(
                f"valid primary IDs were reordered for {tune}"
            )
        reserve_slot_pairs = sorted(
            (int(row["canonical_slot"]), int(row["logical_id"]))
            for row in tune_rows
            if row["role"] == "reserve"
        )
        if reserve_slot_pairs != list(zip(missing_slots, expected_reserve)):
            raise ValueError(
                f"lowest valid reserves are not assigned to missing primary "
                f"slots in order for {tune}"
            )


def freeze(args: argparse.Namespace) -> int:
    campaign_dir = args.campaign_dir.resolve()
    production_root = args.production_root.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(
            f"refusing to alter nonempty freeze directory: {output_dir}"
        )
    current_commit = require_clean_checkout()

    campaign_path = campaign_dir / "campaign.json"
    campaign = read_json(campaign_path)
    expected_campaign_fields = {
        "schema": "hf_campaign_v1",
        "raw_schema": RAW_SCHEMA,
        "origin_algorithm": ORIGIN_ALGORITHM,
        "selector": SELECTOR,
        "block_count": BLOCKS,
        "repository_dirty_at_generation": False,
    }
    for key, expected in expected_campaign_fields.items():
        if campaign.get(key) != expected:
            raise ValueError(
                f"campaign {key} differs: {campaign.get(key)!r} != {expected!r}"
            )
    expansion_campaign = (
        campaign.get("campaign_kind") == EXPANSION_CAMPAIGN_KIND
    )
    if expansion_campaign:
        canonical_slots = require_int(
            campaign.get("planned_additional_jobs_per_tune"),
            "expansion jobs per tune",
            10,
        )
        if canonical_slots > 100 or canonical_slots % BLOCKS:
            raise ValueError("expansion jobs per tune must be 10..100 by ten")
        row_schema = EXTENSION_ROW_SCHEMA
        summary_schema = EXTENSION_SUMMARY_SCHEMA
        primary_limit = canonical_slots
    else:
        if campaign.get("campaign_kind") is not None:
            raise ValueError("unsupported canonical campaign kind")
        canonical_slots = CANONICAL_SLOTS
        row_schema = ROW_SCHEMA
        summary_schema = SUMMARY_SCHEMA
        primary_limit = CANONICAL_SLOTS
    campaign_commit = require_hex(
        campaign.get("repository_commit"), HEX40, "campaign repository commit"
    )
    require_ancestor(campaign_commit, current_commit)
    campaign_ordinal = require_int(
        campaign.get("campaign_ordinal"), "campaign ordinal", 1
    )
    requested = require_int(
        campaign.get("requested_successes_per_job"),
        "requested successes per job",
        1,
    )
    species_sha = require_hex(
        campaign.get("species_registry_sha256"),
        HEX64,
        "species registry SHA-256",
    )
    pair_sha = require_hex(
        campaign.get("pair_registry_sha256"),
        HEX64,
        "pair registry SHA-256",
    )
    tune_allowlist_sha = require_hex(
        campaign.get("tune_allowlist_sha256"),
        HEX64,
        "tune-difference allowlist SHA-256",
    )

    candidates = read_jsonl(campaign_dir / "candidate_manifest.jsonl")
    ledger = read_jsonl(campaign_dir / "seed_ledger.jsonl")
    candidate_lookup: dict[tuple[str, int], dict] = {}
    for candidate in candidates:
        key = (candidate.get("tune"), candidate.get("logical_id"))
        if key in candidate_lookup:
            raise ValueError(f"duplicate candidate allocation {key}")
        candidate_lookup[key] = candidate
    ledger_lookup: dict[tuple[str, int, int], dict] = {}
    for allocation in ledger:
        key = (
            allocation.get("tune"),
            allocation.get("logical_id"),
            allocation.get("attempt"),
        )
        if key in ledger_lookup:
            raise ValueError(f"duplicate seed allocation {key}")
        ledger_lookup[key] = allocation

    (
        claim,
        producer_sha,
        submission_record_sha,
        launch_provenance,
    ) = validate_submission_receipts(campaign_dir, production_root, campaign)
    campaign_contract_path = (
        REPOSITORY_ROOT / "tools" / "campaign_manifest.py"
    )
    specification = importlib.util.spec_from_file_location(
        "canonical_freeze_campaign_contract", campaign_contract_path
    )
    if specification is None or specification.loader is None:
        raise ValueError("cannot load the campaign launch contract")
    campaign_contract = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(campaign_contract)
    physics_signoff = campaign_dir / "PHYSICS_ORIGIN_SIGNOFF.json"
    gate_authorization = (
        campaign_dir / "FULL_PRODUCTION_GATE_AUTHORIZATION.json"
    )
    campaign_contract.validate_physics_signoff(
        physics_signoff, campaign
    )
    campaign_contract.validate_gate_authorization(
        gate_authorization,
        REPOSITORY_ROOT,
        campaign,
        physics_signoff,
    )
    if expansion_campaign:
        campaign_contract.validate_expansion_authorization(
            campaign_dir / "EQUAL_TUNE_EXPANSION_AUTHORIZATION.json",
            REPOSITORY_ROOT,
            campaign,
        )
    choices: dict[tuple[str, int], dict] = {}
    selection_sha: str | None = None
    if args.selection:
        selection_path = args.selection.resolve()
        selection_sha = digest(selection_path)
        values = json.loads(selection_path.read_text())
        if not isinstance(values, list):
            raise ValueError("selection override must be a JSON array")
        for choice in values:
            if not isinstance(choice, dict):
                raise ValueError("selection override entries must be objects")
            key = (choice.get("tune"), choice.get("canonical_slot"))
            if key in choices:
                raise ValueError(f"duplicate explicit selection {key}")
            choices[key] = choice

    cards: dict[str, tuple[Path, float]] = {}
    for tune in TUNES:
        card = (
            REPOSITORY_ROOT
            / "SimulationScripts"
            / f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
        )
        expected_card_sha = campaign.get("card_sha256", {}).get(tune)
        if expected_card_sha != digest(card):
            raise ValueError(f"campaign card checksum differs for {tune}")
        cards[tune] = (card, parse_card_pthat_min(card))

    rows: list[dict] = []
    selected_raw: set[Path] = set()
    technically_valid_ids: dict[str, set[int]] = {
        tune: set() for tune in TUNES
    }
    for tune in TUNES:
        for slot in range(canonical_slots):
            choice = choices.get(
                (tune, slot),
                {
                    "tune": tune,
                    "canonical_slot": slot,
                    "logical_id": slot,
                    "attempt": 0,
                    "reason": "primary_initial_allocation",
                    "approval": "full_candidates_attempt0_submission_claim",
                },
            )
            if choice.get("tune") != tune or choice.get("canonical_slot") != slot:
                raise ValueError(f"selection identity differs: {choice}")
            logical_id = require_int(
                choice.get("logical_id"), "selected logical ID"
            )
            attempt = require_int(choice.get("attempt"), "selected attempt")
            candidate = candidate_lookup.get((tune, logical_id))
            allocation = ledger_lookup.get((tune, logical_id, attempt))
            if candidate is None or allocation is None:
                raise ValueError(f"selection is not ledger-authorized: {choice}")
            role = candidate.get("role")
            if role not in {"primary", "reserve"}:
                raise ValueError(f"invalid selected role: {role!r}")
            if logical_id >= primary_limit and role != "reserve":
                raise ValueError(f"replacement is not a declared reserve: {choice}")
            if logical_id < primary_limit and role != "primary":
                raise ValueError(f"primary logical ID has non-primary role: {choice}")
            seed = require_int(allocation.get("seed"), "selected seed", 1)
            candidate_exact = {
                "campaign": campaign["campaign"],
                "campaign_ordinal": campaign_ordinal,
                "tune": tune,
                "logical_id": logical_id,
                "role": role,
                "requested_successes": requested,
                "repository_commit": campaign_commit,
            }
            for key, value in candidate_exact.items():
                if candidate.get(key) != value:
                    raise ValueError(
                        f"candidate {key} differs for {tune}/{logical_id}"
                    )
            if allocation.get("seed") != seed:
                raise ValueError("seed ledger mismatch")
            pthat_override = str(candidate.get("pthat_min_override"))
            if pthat_override not in {"NONE", "0.5", "1.0", "2.0"}:
                raise ValueError(f"invalid pTHat override {pthat_override!r}")
            effective_pthat = (
                cards[tune][1]
                if pthat_override == "NONE"
                else float(pthat_override)
            )
            audit_events = require_int(
                candidate.get("multiplicity_audit_events"),
                "multiplicity audit event count",
            )
            effective_card_sha = require_hex(
                candidate.get("effective_card_sha256"),
                HEX64,
                "effective card SHA-256",
            )
            stable_name = candidate.get("stable_name")
            expected_name = f"hf_{tune}_job{logical_id:03d}.root"
            if stable_name != expected_name:
                raise ValueError(
                    f"candidate stable name differs: {stable_name!r}"
                )
            raw_relative = Path("raw") / tune / expected_name
            raw_path = production_root / raw_relative
            if (
                raw_path.is_symlink()
                or not raw_path.is_file()
                or raw_path.stat().st_size <= 0
            ):
                raise FileNotFoundError(f"missing canonical raw output: {raw_path}")
            raw_bytes = raw_path.stat().st_size
            checksum_path = Path(f"{raw_path}.sha256")
            if checksum_path.is_symlink() or not checksum_path.is_file():
                raise FileNotFoundError(f"missing raw checksum: {checksum_path}")
            fields = checksum_path.read_text().split()
            if (
                len(fields) != 2
                or not HEX64.fullmatch(fields[0])
                or Path(fields[1]).name != raw_path.name
            ):
                raise ValueError(f"invalid raw checksum sidecar: {checksum_path}")
            raw_sha = fields[0]
            if args.verify_checksums and digest(raw_path) != raw_sha:
                raise ValueError(f"raw checksum mismatch: {raw_path}")

            expected = {
                **candidate_exact,
                "canonical_slot": slot,
                "attempt": attempt,
                "seed": seed,
                "pthat_min_override": pthat_override,
                "effective_pthat_min": effective_pthat,
                "multiplicity_audit_events": audit_events,
                "effective_card_sha256": effective_card_sha,
                "producer_executable_sha256": producer_sha,
                "raw_sha256": raw_sha,
            }
            (
                attempt_start_claim,
                attempt_start_claim_sha,
                producing_cluster_id,
                producing_process_id,
            ) = validate_attempt_start_claim(production_root, expected)
            expected.update(
                {
                    "attempt_start_claim_path":
                        attempt_start_claim.as_posix(),
                    "attempt_start_claim_sha256":
                        attempt_start_claim_sha,
                    "producing_cluster_id": producing_cluster_id,
                    "producing_process_id": producing_process_id,
                }
            )
            attempt_receipt, attempt_receipt_sha = find_attempt_receipt(
                production_root, expected, raw_sha, raw_bytes
            )
            (
                raw_validation_receipt,
                raw_validation_receipt_sha,
                raw_validation_log,
                raw_validation_log_sha,
            ) = validate_raw_validation_receipt(
                production_root, expected, raw_sha, raw_bytes
            )
            (
                authorization,
                authorization_sha,
                submission_record,
                selected_submission_record_sha,
            ) = authorization_for(
                production_root,
                campaign_dir,
                claim,
                choice,
                expected,
                producer_sha,
                submission_record_sha,
            )
            reason = choice.get("reason")
            approval = choice.get("approval")
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError("selection reason is absent")
            if not isinstance(approval, str) or not approval.strip():
                raise ValueError("selection approval is absent")
            row = {
                "schema": row_schema,
                "campaign": campaign["campaign"],
                "campaign_ordinal": campaign_ordinal,
                "tune": tune,
                "tune_ordinal": TUNE_ORDINAL[tune],
                "canonical_slot": slot,
                "block": slot % BLOCKS,
                "block_position": slot // BLOCKS,
                "logical_id": logical_id,
                "role": role,
                "attempt": attempt,
                "seed": seed,
                "requested_successes": requested,
                "pthat_min_override": pthat_override,
                "effective_pthat_min": effective_pthat,
                "multiplicity_audit_events": audit_events,
                "effective_card_sha256": effective_card_sha,
                "producer_executable_sha256": producer_sha,
                "repository_commit": campaign_commit,
                "raw_schema": RAW_SCHEMA,
                "origin_algorithm": ORIGIN_ALGORITHM,
                "selector": SELECTOR,
                "species_registry_sha256": species_sha,
                "pair_registry_sha256": pair_sha,
                "tune_difference_allowlist_schema": TUNE_ALLOWLIST_SCHEMA,
                "tune_difference_allowlist_sha256": tune_allowlist_sha,
                "raw_path": raw_relative.as_posix(),
                "raw_bytes": raw_bytes,
                "raw_sha256": raw_sha,
                "attempt_start_claim_path":
                    attempt_start_claim.as_posix(),
                "attempt_start_claim_sha256": attempt_start_claim_sha,
                "producing_cluster_id": producing_cluster_id,
                "producing_process_id": producing_process_id,
                "attempt_receipt_path": attempt_receipt.as_posix(),
                "attempt_receipt_sha256": attempt_receipt_sha,
                "raw_validation_receipt_path":
                    raw_validation_receipt.as_posix(),
                "raw_validation_receipt_sha256":
                    raw_validation_receipt_sha,
                "raw_validation_log_path": raw_validation_log.as_posix(),
                "raw_validation_log_sha256": raw_validation_log_sha,
                "allocation_authorization_path": authorization.as_posix(),
                "allocation_authorization_sha256": authorization_sha,
                "submission_record_path": submission_record.as_posix(),
                "submission_record_sha256":
                    selected_submission_record_sha,
                "validation_receipt_path": VALIDATION_RECEIPT_NAME,
                "selection_reason": reason,
                "selection_approval": approval,
            }
            row["production_definition_sha256"] = production_definition(row)
            rows.append(row)
            selected_raw.add(raw_path.resolve())
            technically_valid_ids[tune].add(logical_id)

    unused_choices = set(choices) - {
        (row["tune"], row["canonical_slot"]) for row in rows
    }
    if unused_choices:
        raise ValueError(f"selection contains unknown tune/slot: {unused_choices}")
    selected_logical_ids = [
        (row["tune"], row["logical_id"]) for row in rows
    ]
    if len(selected_logical_ids) != len(set(selected_logical_ids)):
        raise ValueError("canonical selection reuses a logical ID")
    discovered_raw = {
        path.resolve()
        for tune in TUNES
        for path in (production_root / "raw" / tune).glob("*.root")
        if path.is_file()
    }
    authorized_candidate_raw = {
        (
            production_root
            / "raw"
            / str(candidate["tune"])
            / str(candidate["stable_name"])
        ).resolve()
        for candidate in candidates
    }
    if not selected_raw.issubset(discovered_raw) or not discovered_raw.issubset(
        authorized_candidate_raw
    ):
        raise ValueError(
            "production raw-file set is missing selected or contains "
            "undeclared files: "
            f"missing={sorted(str(path) for path in selected_raw - discovered_raw)} "
            f"undeclared={sorted(str(path) for path in discovered_raw - authorized_candidate_raw)}"
        )
    candidate_by_raw = {
        (
            production_root
            / "raw"
            / str(candidate["tune"])
            / str(candidate["stable_name"])
        ).resolve(): candidate
        for candidate in candidates
    }
    for raw_path in sorted(discovered_raw - selected_raw):
        candidate = candidate_by_raw[raw_path]
        raw_sha = digest(raw_path)
        raw_bytes = raw_path.stat().st_size
        checksum = Path(f"{raw_path}.sha256")
        fields = checksum.read_text().split() if checksum.is_file() else []
        if (
            checksum.is_symlink()
            or len(fields) != 2
            or fields[0] != raw_sha
            or Path(fields[1]).name != raw_path.name
        ):
            raise ValueError(
                f"unselected declared reserve checksum differs: {raw_path}"
            )
        matching_attempts = 0
        for allocation in ledger:
            if (
                allocation.get("tune") != candidate["tune"]
                or allocation.get("logical_id") != candidate["logical_id"]
            ):
                continue
            attempt = require_int(
                allocation.get("attempt"), "reserve attempt"
            )
            expected = {
                "campaign": campaign["campaign"],
                "campaign_ordinal": campaign_ordinal,
                "tune": candidate["tune"],
                "canonical_slot": -1,
                "logical_id": candidate["logical_id"],
                "role": candidate["role"],
                "attempt": attempt,
                "seed": require_int(allocation.get("seed"), "reserve seed", 1),
                "requested_successes": requested,
                "pthat_min_override": str(candidate["pthat_min_override"]),
                "effective_pthat_min": (
                    cards[candidate["tune"]][1]
                    if candidate["pthat_min_override"] == "NONE"
                    else float(candidate["pthat_min_override"])
                ),
                "multiplicity_audit_events": int(
                    candidate["multiplicity_audit_events"]
                ),
                "repository_commit": campaign_commit,
                "effective_card_sha256": candidate[
                    "effective_card_sha256"
                ],
                "producer_executable_sha256": producer_sha,
                "raw_sha256": raw_sha,
            }
            try:
                (
                    start_path,
                    start_sha,
                    cluster,
                    process,
                ) = validate_attempt_start_claim(production_root, expected)
                expected.update(
                    {
                        "attempt_start_claim_path": start_path.as_posix(),
                        "attempt_start_claim_sha256": start_sha,
                        "producing_cluster_id": cluster,
                        "producing_process_id": process,
                    }
                )
                find_attempt_receipt(
                    production_root, expected, raw_sha, raw_bytes
                )
                validate_raw_validation_receipt(
                    production_root, expected, raw_sha, raw_bytes
                )
                authorization_for(
                    production_root,
                    campaign_dir,
                    claim,
                    {},
                    expected,
                    producer_sha,
                    submission_record_sha,
                )
            except (
                FileNotFoundError,
                KeyError,
                TypeError,
                ValueError,
            ):
                continue
            matching_attempts += 1
        if matching_attempts != 1:
            raise ValueError(
                "unselected declared reserve lacks one unambiguous validated "
                f"attempt: {raw_path} matches={matching_attempts}"
            )
        technically_valid_ids[str(candidate["tune"])].add(
            int(candidate["logical_id"])
        )

    # Technical validity determines the subset before any physics observable
    # is inspected.
    validate_lowest_valid_selection(
        rows, technically_valid_ids, primary_limit, canonical_slots
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    canonical_text = jsonl_text(rows)
    atomic_write(output_dir / "canonical_manifest.jsonl", canonical_text)
    block_hashes: dict[str, str] = {}
    for block in range(BLOCKS):
        block_rows = [row for row in rows if row["block"] == block]
        block_text = jsonl_text(block_rows)
        name = f"block_{block + 1:02d}.jsonl"
        atomic_write(output_dir / name, block_text)
        block_hashes[name] = text_digest(block_text)
    summary = {
        "schema": summary_schema,
        "state": "AWAITING_EXHAUSTIVE_RAW_VALIDATION",
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign_ordinal,
        "canonical_manifest_sha256": text_digest(canonical_text),
        "block_manifest_sha256": block_hashes,
        "jobs_per_tune": canonical_slots,
        "successful_events_per_job": requested,
        "successful_events_per_tune": canonical_slots * requested,
        "block_count": BLOCKS,
        "jobs_per_tune_per_block": canonical_slots // BLOCKS,
        "selection_file_sha256": selection_sha,
        "repository_commit_at_freeze": current_commit,
        "repository_implementation_commit": campaign_commit,
        "campaign_json_sha256": digest(campaign_path),
        "candidate_manifest_sha256": digest(
            campaign_dir / "candidate_manifest.jsonl"
        ),
        "seed_ledger_sha256": digest(campaign_dir / "seed_ledger.jsonl"),
        "submission_claim_path": FULL_CLAIM.as_posix(),
        "submission_claim_sha256": digest(production_root / FULL_CLAIM),
        "submission_record_path": FULL_RECORD.as_posix(),
        "submission_record_sha256": submission_record_sha,
        **launch_provenance,
        "raw_schema": RAW_SCHEMA,
        "origin_algorithm": ORIGIN_ALGORITHM,
        "selector": SELECTOR,
        "species_registry_sha256": species_sha,
        "pair_registry_sha256": pair_sha,
        "tune_difference_allowlist_schema": TUNE_ALLOWLIST_SCHEMA,
        "tune_difference_allowlist_sha256": tune_allowlist_sha,
        "validation_receipt_path": VALIDATION_RECEIPT_NAME,
        "seal_path": SEAL_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    if expansion_campaign:
        summary.update(
            {
                "campaign_kind": EXPANSION_CAMPAIGN_KIND,
                "primary_logical_ids_per_tune": primary_limit,
                "supersedes": campaign["supersedes"],
                "planned_final_jobs_per_tune": campaign[
                    "planned_final_jobs_per_tune"
                ],
            }
        )
    atomic_write(
        output_dir / "freeze_summary.json",
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
    )
    validate_directory(output_dir, require_seal=False)
    print(
        "CANONICAL_FREEZE_AWAITING_VALIDATION "
        f"rows={len(rows)} directory={output_dir}"
    )
    return 0


def validate_row(
    row: dict,
    index: int,
    summary: dict,
    jobs_per_tune: int,
    row_schema: str,
) -> None:
    expected_keys = (
        ROW_KEYS
        if row_schema in {ROW_SCHEMA, EXTENSION_ROW_SCHEMA}
        else SUPERSEDING_ROW_KEYS
    )
    if set(row) != expected_keys:
        raise ValueError(
            f"canonical row {index} field set differs: "
            f"missing={sorted(expected_keys - set(row))} "
            f"extra={sorted(set(row) - expected_keys)}"
        )
    tune_index, slot = divmod(index, jobs_per_tune)
    tune = TUNES[tune_index]
    exact = {
        "schema": row_schema,
        "tune": tune,
        "tune_ordinal": tune_index,
        "canonical_slot": slot,
        "block": slot % BLOCKS,
        "block_position": slot // BLOCKS,
        "requested_successes": summary["successful_events_per_job"],
        "raw_schema": RAW_SCHEMA,
        "origin_algorithm": ORIGIN_ALGORITHM,
        "selector": SELECTOR,
        "species_registry_sha256": summary["species_registry_sha256"],
        "pair_registry_sha256": summary["pair_registry_sha256"],
        "tune_difference_allowlist_schema": TUNE_ALLOWLIST_SCHEMA,
        "tune_difference_allowlist_sha256": summary[
            "tune_difference_allowlist_sha256"
        ],
        "validation_receipt_path": VALIDATION_RECEIPT_NAME,
    }
    if row_schema in {ROW_SCHEMA, EXTENSION_ROW_SCHEMA}:
        exact.update(
            {
                "campaign": summary["campaign"],
                "campaign_ordinal": summary["campaign_ordinal"],
            }
        )
    else:
        exact.update(
            {
                "final_campaign": summary["campaign"],
                "final_campaign_ordinal": summary["campaign_ordinal"],
            }
        )
    for key, value in exact.items():
        if row.get(key) != value:
            raise ValueError(
                f"canonical row {index} {key} differs: "
                f"{row.get(key)!r} != {value!r}"
            )
    logical_id = require_int(row["logical_id"], "logical ID")
    role = row["role"]
    if role not in {"primary", "reserve"}:
        raise ValueError(f"invalid canonical role at row {index}")
    primary_limit = (
        CANONICAL_SLOTS
        if row_schema == ROW_SCHEMA
        else int(summary.get("primary_logical_ids_per_tune", CANONICAL_SLOTS))
    )
    if row_schema == SUPERSEDING_ROW_SCHEMA:
        # The source campaign can be first-stage or expansion. Source role
        # validity was sealed there and is bound by source hashes.
        primary_limit = -1
    if primary_limit >= 0 and (logical_id < primary_limit) != (role == "primary"):
        raise ValueError(f"logical-ID/role mismatch at row {index}")
    require_int(row["attempt"], "attempt")
    require_int(row["seed"], "seed", 1)
    require_int(row["multiplicity_audit_events"], "audit event count")
    require_int(row["raw_bytes"], "raw byte count", 1)
    if row["pthat_min_override"] not in {"NONE", "0.5", "1.0", "2.0"}:
        raise ValueError(f"invalid pTHat override at row {index}")
    effective_pthat = row["effective_pthat_min"]
    if (
        isinstance(effective_pthat, bool)
        or not isinstance(effective_pthat, (int, float))
        or not math.isfinite(effective_pthat)
        or effective_pthat < 0
    ):
        raise ValueError(f"invalid effective pTHat at row {index}")
    for key in (
        "effective_card_sha256",
        "producer_executable_sha256",
        "raw_sha256",
        "attempt_start_claim_sha256",
        "attempt_receipt_sha256",
        "raw_validation_receipt_sha256",
        "raw_validation_log_sha256",
        "allocation_authorization_sha256",
        "submission_record_sha256",
        "production_definition_sha256",
    ):
        require_hex(row[key], HEX64, f"row {index} {key}")
    require_hex(row["repository_commit"], HEX40, "production repository commit")
    for key in (
        "raw_path",
        "attempt_start_claim_path",
        "attempt_receipt_path",
        "raw_validation_receipt_path",
        "raw_validation_log_path",
        "allocation_authorization_path",
        "submission_record_path",
        "validation_receipt_path",
    ):
        relative_path(row[key], f"row {index} {key}")
    expected_raw = Path("raw") / tune / f"hf_{tune}_job{logical_id:03d}.root"
    if row_schema == SUPERSEDING_ROW_SCHEMA:
        source_prefix = relative_path(
            row["source_production_prefix"],
            f"row {index} source production prefix",
        )
        if len(source_prefix.parts) != 1:
            raise ValueError(
                f"source production prefix must be one campaign component at row {index}"
            )
        source_campaign = row.get("campaign")
        if (
            not isinstance(source_campaign, str)
            or source_campaign != source_prefix.name
        ):
            raise ValueError(
                f"source campaign/prefix mismatch at row {index}"
            )
        require_int(
            row["source_canonical_slot"],
            f"row {index} source canonical slot",
        )
        for key in (
            "source_manifest_sha256",
            "source_freeze_summary_sha256",
            "source_freeze_seal_sha256",
            "source_production_definition_sha256",
        ):
            require_hex(row[key], HEX64, f"row {index} {key}")
        expected_raw = source_prefix / expected_raw
        for key in (
            "attempt_start_claim_path",
            "attempt_receipt_path",
            "raw_validation_receipt_path",
            "raw_validation_log_path",
            "allocation_authorization_path",
            "submission_record_path",
        ):
            if Path(row[key]).parts[:1] != source_prefix.parts:
                raise ValueError(
                    f"source evidence path prefix differs at row {index}: {key}"
                )
    expected_raw = expected_raw.as_posix()
    if row["raw_path"] != expected_raw:
        raise ValueError(f"raw path naming mismatch at row {index}")
    for key in ("producing_cluster_id", "producing_process_id"):
        if not isinstance(row[key], str) or not re.fullmatch(
            r"[A-Za-z0-9._-]+", row[key]
        ):
            raise ValueError(f"invalid {key} at row {index}")
    if row["production_definition_sha256"] != production_definition(row):
        raise ValueError(f"production-definition checksum differs at row {index}")
    for key in ("selection_reason", "selection_approval"):
        if not isinstance(row[key], str) or not row[key].strip():
            raise ValueError(f"{key} absent at row {index}")


def validate_directory(directory: Path, require_seal: bool = True) -> int:
    manifest_path = directory / "canonical_manifest.jsonl"
    summary_path = directory / "freeze_summary.json"
    rows = read_jsonl(manifest_path)
    summary = read_json(summary_path)
    (
        jobs_per_tune,
        expected_row_count,
        row_schema,
        summary_schema,
        receipt_schema,
        seal_schema,
    ) = manifest_shape(summary)
    exact_summary = {
        "state": "AWAITING_EXHAUSTIVE_RAW_VALIDATION",
        "block_count": BLOCKS,
        "jobs_per_tune": jobs_per_tune,
        "jobs_per_tune_per_block": jobs_per_tune // BLOCKS,
        "raw_schema": RAW_SCHEMA,
        "origin_algorithm": ORIGIN_ALGORITHM,
        "selector": SELECTOR,
        "tune_difference_allowlist_schema": TUNE_ALLOWLIST_SCHEMA,
        "validation_receipt_path": VALIDATION_RECEIPT_NAME,
        "seal_path": SEAL_NAME,
    }
    for key, value in exact_summary.items():
        if summary.get(key) != value:
            raise ValueError(f"freeze summary {key} differs")
    successes_per_job = require_int(
        summary.get("successful_events_per_job"),
        "freeze successful events per job",
        1,
    )
    if (
        summary.get("successful_events_per_tune")
        != jobs_per_tune * successes_per_job
    ):
        raise ValueError("freeze successful events per tune differs")
    if summary_schema == EXTENSION_SUMMARY_SCHEMA:
        if (
            summary.get("campaign_kind") != EXPANSION_CAMPAIGN_KIND
            or summary.get("primary_logical_ids_per_tune")
            != jobs_per_tune
            or not isinstance(summary.get("supersedes"), dict)
            or summary.get("planned_final_jobs_per_tune", 0)
            < jobs_per_tune + 100
        ):
            raise ValueError("equal-tune extension freeze metadata differs")
    if summary_schema == SUPERSEDING_SUMMARY_SCHEMA:
        supersedes = summary.get("supersedes")
        sources = summary.get("source_freezes")
        if (
            not isinstance(supersedes, dict)
            or supersedes.get("contract")
            != "immutable_equal_tune_union_v1"
            or not isinstance(sources, list)
            or len(sources) < 2
        ):
            raise ValueError(
                "superseding freeze lacks its immutable parent/source contract"
            )
        parent_jobs = require_int(
            supersedes.get("parent_jobs_per_tune"),
            "superseding parent jobs per tune",
            100,
        )
        additional_jobs = require_int(
            supersedes.get("additional_jobs_per_tune"),
            "superseding additional jobs per tune",
            1,
        )
        if (
            parent_jobs % BLOCKS
            or additional_jobs % BLOCKS
            or parent_jobs + additional_jobs != jobs_per_tune
        ):
            raise ValueError("superseding parent/extension exposure differs")
        source_campaigns: set[str] = set()
        for source_index, source in enumerate(sources):
            if not isinstance(source, dict):
                raise ValueError("superseding source-freeze entry is malformed")
            campaign = source.get("campaign")
            prefix = source.get("production_prefix")
            if (
                not isinstance(campaign, str)
                or not campaign
                or prefix != campaign
                or campaign in source_campaigns
            ):
                raise ValueError(
                    "superseding source campaign/prefix is invalid or duplicated"
                )
            source_campaigns.add(campaign)
            require_int(
                source.get("campaign_ordinal"),
                f"source {source_index} campaign ordinal",
                1,
            )
            require_int(
                source.get("jobs_in_final_union_per_tune"),
                f"source {source_index} final-union jobs",
                1,
            )
            for key in (
                "canonical_manifest_sha256",
                "freeze_summary_sha256",
                "freeze_seal_sha256",
                "physics_origin_signoff_sha256",
                "full_production_gate_authorization_sha256",
                "registry_baseline_sha256",
                "global_submission_claim_sha256",
            ):
                require_hex(
                    source.get(key),
                    HEX64,
                    f"source {source_index} {key}",
                )
            if "equal_tune_expansion_authorization_sha256" in source:
                require_hex(
                    source[
                        "equal_tune_expansion_authorization_sha256"
                    ],
                    HEX64,
                    f"source {source_index} expansion authorization",
                )
        if (
            sum(
                int(source["jobs_in_final_union_per_tune"])
                for source in sources
            )
            != jobs_per_tune
            or supersedes.get("parent_campaign")
            != sources[-2]["campaign"]
            or parent_jobs
            != sum(
                int(source["jobs_in_final_union_per_tune"])
                for source in sources[:-1]
            )
            or supersedes.get("extension_campaign")
            != sources[-1]["campaign"]
            or summary["campaign"] != sources[-1]["campaign"]
            or sources[-1].get(
                "equal_tune_expansion_authorization_sha256"
            )
            != summary.get(
                "equal_tune_expansion_authorization_sha256"
            )
        ):
            raise ValueError("superseding source-freeze accounting differs")
        require_hex(
            summary.get("source_freezes_sha256"),
            HEX64,
            "superseding source-freeze inventory SHA-256",
        )
        if summary["source_freezes_sha256"] != text_digest(
            canonical_json(sources)
        ):
            raise ValueError("superseding source-freeze inventory checksum differs")
    for key in (
        "species_registry_sha256",
        "pair_registry_sha256",
        "tune_difference_allowlist_sha256",
        "submission_claim_sha256",
        "submission_record_sha256",
        "physics_origin_signoff_sha256",
        "full_production_gate_authorization_sha256",
        "registry_baseline_sha256",
        "global_submission_claim_sha256",
        "campaign_json_sha256",
        "candidate_manifest_sha256",
        "seed_ledger_sha256",
    ):
        require_hex(summary.get(key), HEX64, f"freeze summary {key}")
    if summary_schema in {
        EXTENSION_SUMMARY_SCHEMA,
        SUPERSEDING_SUMMARY_SCHEMA,
    }:
        require_hex(
            summary.get("equal_tune_expansion_authorization_sha256"),
            HEX64,
            "freeze expansion authorization SHA-256",
        )
    if len(rows) != expected_row_count:
        raise ValueError(
            f"canonical row count {len(rows)} is not {expected_row_count}"
        )
    if summary.get("canonical_manifest_sha256") != digest(manifest_path):
        raise ValueError("canonical manifest checksum differs from summary")
    for index, row in enumerate(rows):
        validate_row(row, index, summary, jobs_per_tune, row_schema)
    identities = [(row["tune"], row["canonical_slot"]) for row in rows]
    paths = [row["raw_path"] for row in rows]
    seeds = [row["seed"] for row in rows]
    receipts = [row["attempt_receipt_path"] for row in rows]
    attempt_starts = [row["attempt_start_claim_path"] for row in rows]
    raw_validation_receipts = [
        row["raw_validation_receipt_path"] for row in rows
    ]
    raw_validation_logs = [
        row["raw_validation_log_path"] for row in rows
    ]
    if len(set(identities)) != expected_row_count:
        raise ValueError("duplicate canonical tune/slot")
    if len(set(paths)) != expected_row_count:
        raise ValueError("duplicate canonical raw path")
    if len(set(seeds)) != expected_row_count:
        raise ValueError("duplicate canonical seed")
    if len(set(receipts)) != expected_row_count:
        raise ValueError("duplicate successful-attempt receipt")
    if len(set(attempt_starts)) != expected_row_count:
        raise ValueError("duplicate attempt-start claim")
    if len(set(raw_validation_receipts)) != expected_row_count:
        raise ValueError("duplicate raw-validation receipt")
    if len(set(raw_validation_logs)) != expected_row_count:
        raise ValueError("duplicate raw-validation log")
    if row_schema == SUPERSEDING_ROW_SCHEMA:
        source_by_campaign = {
            source["campaign"]: source
            for source in summary["source_freezes"]
        }
        source_counts = {
            campaign: {tune: 0 for tune in TUNES}
            for campaign in source_by_campaign
        }
        source_slots: set[tuple[str, str, int]] = set()
        for index, row in enumerate(rows):
            source = source_by_campaign.get(row["campaign"])
            if source is None:
                raise ValueError(
                    f"canonical row {index} has an undeclared source campaign"
                )
            expected_source = {
                "source_production_prefix": source["production_prefix"],
                "source_manifest_sha256": source[
                    "canonical_manifest_sha256"
                ],
                "source_freeze_summary_sha256": source[
                    "freeze_summary_sha256"
                ],
                "source_freeze_seal_sha256": source[
                    "freeze_seal_sha256"
                ],
            }
            for key, value in expected_source.items():
                if row.get(key) != value:
                    raise ValueError(
                        f"canonical row {index} {key} differs from source freeze"
                    )
            source_identity = (
                row["campaign"],
                row["tune"],
                row["source_canonical_slot"],
            )
            if source_identity in source_slots:
                raise ValueError("duplicate source tune/canonical-slot identity")
            source_slots.add(source_identity)
            source_counts[row["campaign"]][row["tune"]] += 1
        for campaign, tune_counts in source_counts.items():
            expected_source_jobs = source_by_campaign[campaign][
                "jobs_in_final_union_per_tune"
            ]
            if set(tune_counts.values()) != {expected_source_jobs}:
                raise ValueError(
                    f"source {campaign} contributes unequal tune exposure: "
                    f"{tune_counts}"
                )

    discovered_blocks = {path.name for path in directory.glob("block_*.jsonl")}
    expected_blocks = {f"block_{block + 1:02d}.jsonl" for block in range(BLOCKS)}
    if discovered_blocks != expected_blocks:
        raise ValueError(
            f"block file set differs: missing={expected_blocks - discovered_blocks} "
            f"extra={discovered_blocks - expected_blocks}"
        )
    union: list[dict] = []
    summary_block_hashes = summary.get("block_manifest_sha256")
    if not isinstance(summary_block_hashes, dict):
        raise ValueError("block checksum map is absent")
    for block in range(BLOCKS):
        name = f"block_{block + 1:02d}.jsonl"
        path = directory / name
        if summary_block_hashes.get(name) != digest(path):
            raise ValueError(f"block checksum differs for {name}")
        block_rows = read_jsonl(path)
        expected_rows = [row for row in rows if row["block"] == block]
        if block_rows != expected_rows:
            raise ValueError(f"{name} is not the exact canonical subset")
        for tune in TUNES:
            if (
                sum(row["tune"] == tune for row in block_rows)
                != jobs_per_tune // BLOCKS
            ):
                raise ValueError(
                    f"{name} does not contain "
                    f"{jobs_per_tune // BLOCKS} {tune} jobs"
                )
        union.extend(block_rows)
    union_identities = {
        (row["tune"], row["canonical_slot"]) for row in union
    }
    if (
        len(union) != expected_row_count
        or union_identities != set(identities)
    ):
        raise ValueError("ten-block union is not exactly the canonical manifest")
    for tune in TUNES:
        tune_rows = [row for row in rows if row["tune"] == tune]
        if len(tune_rows) != jobs_per_tune:
            raise ValueError(f"wrong canonical job count for {tune}")
        events = sum(row["requested_successes"] for row in tune_rows)
        if events != summary["successful_events_per_tune"]:
            raise ValueError(f"successful-event total differs for {tune}")

    seal_path = directory / SEAL_NAME
    receipt_path = directory / VALIDATION_RECEIPT_NAME
    validation_log = directory / VALIDATION_LOG_NAME
    if require_seal:
        for path in (seal_path, receipt_path, validation_log):
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"canonical freeze is not sealed: missing {path}")
        receipt = read_json(receipt_path)
        seal = read_json(seal_path)
        receipt_expected = {
            "schema": receipt_schema,
            "state": "PASS",
            "canonical_manifest_sha256": digest(manifest_path),
            "canonical_manifest_rows": expected_row_count,
            "validation_log_sha256": digest(validation_log),
            "submission_claim_sha256": summary["submission_claim_sha256"],
            "submission_record_sha256": summary["submission_record_sha256"],
            "physics_origin_signoff_sha256":
                summary["physics_origin_signoff_sha256"],
            "full_production_gate_authorization_sha256":
                summary["full_production_gate_authorization_sha256"],
            "registry_baseline_sha256":
                summary["registry_baseline_sha256"],
            "global_submission_claim_sha256":
                summary["global_submission_claim_sha256"],
        }
        if summary_schema in {
            EXTENSION_SUMMARY_SCHEMA,
            SUPERSEDING_SUMMARY_SCHEMA,
        }:
            receipt_expected[
                "equal_tune_expansion_authorization_sha256"
            ] = summary[
                "equal_tune_expansion_authorization_sha256"
            ]
        if summary_schema == SUPERSEDING_SUMMARY_SCHEMA:
            receipt_expected.update(
                {
                    "jobs_per_tune": jobs_per_tune,
                    "source_freezes_sha256": summary[
                        "source_freezes_sha256"
                    ],
                    "supersedes": summary["supersedes"],
                }
            )
        for key, value in receipt_expected.items():
            if receipt.get(key) != value:
                raise ValueError(f"canonical validation receipt {key} differs")
        seal_expected = {
            "schema": seal_schema,
            "state": "SEALED",
            "canonical_manifest_sha256": digest(manifest_path),
            "validation_receipt_path": VALIDATION_RECEIPT_NAME,
            "validation_receipt_sha256": digest(receipt_path),
            "validation_log_path": VALIDATION_LOG_NAME,
            "validation_log_sha256": digest(validation_log),
            "physics_origin_signoff_sha256":
                summary["physics_origin_signoff_sha256"],
            "full_production_gate_authorization_sha256":
                summary["full_production_gate_authorization_sha256"],
            "registry_baseline_sha256":
                summary["registry_baseline_sha256"],
            "global_submission_claim_sha256":
                summary["global_submission_claim_sha256"],
        }
        if summary_schema in {
            EXTENSION_SUMMARY_SCHEMA,
            SUPERSEDING_SUMMARY_SCHEMA,
        }:
            seal_expected[
                "equal_tune_expansion_authorization_sha256"
            ] = summary[
                "equal_tune_expansion_authorization_sha256"
            ]
        if summary_schema == SUPERSEDING_SUMMARY_SCHEMA:
            seal_expected.update(
                {
                    "jobs_per_tune": jobs_per_tune,
                    "source_freezes_sha256": summary[
                        "source_freezes_sha256"
                    ],
                    "supersedes": summary["supersedes"],
                }
            )
        for key, value in seal_expected.items():
            if seal.get(key) != value:
                raise ValueError(f"canonical freeze seal {key} differs")
    elif seal_path.exists() or receipt_path.exists() or validation_log.exists():
        # A partially sealed directory is unsafe even for the validation stage.
        present = [
            path.name
            for path in (seal_path, receipt_path, validation_log)
            if path.exists()
        ]
        if len(present) != 3:
            raise ValueError(f"partial canonical seal detected: {present}")

    print(
        "CANONICAL_MANIFEST_VALID "
        f"rows={len(rows)} unique_seeds={len(set(seeds))} blocks={BLOCKS} "
        f"jobs_per_tune={jobs_per_tune} schema={row_schema} "
        f"sealed={'true' if require_seal else 'false'}"
    )
    return 0


def raw_inventory_digest(rows: list[dict]) -> str:
    text = "".join(
        f"{row['raw_path']}\0{row['raw_sha256']}\0{row['raw_bytes']}\n"
        for row in rows
    )
    return text_digest(text)


def promote_freeze_artifacts(
    output_dir: Path, artifacts: dict[str, str]
) -> None:
    """Validate a complete freeze in a sibling stage, then rename atomically."""
    if output_dir.exists():
        raise ValueError(
            f"refusing to alter an existing superseding freeze: {output_dir}"
        )
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging_dir = Path(
        tempfile.mkdtemp(
            prefix=f".{output_dir.name}.partial.",
            dir=output_dir.parent,
        )
    )
    os.chmod(
        staging_dir,
        output_dir.parent.stat().st_mode & 0o7777,
    )
    try:
        for name, content in artifacts.items():
            atomic_write(staging_dir / name, content)
        validate_directory(staging_dir, require_seal=False)
        os.replace(staging_dir, output_dir)
    except BaseException:
        if staging_dir.is_dir() and not staging_dir.is_symlink():
            for child in staging_dir.iterdir():
                if child.is_file() and not child.is_symlink():
                    child.unlink()
            staging_dir.rmdir()
        raise


def verify_source_row_files(
    row: dict, source_root: Path, verify_checksums: bool = True
) -> None:
    """Revalidate every raw/evidence byte carried into a superseding union."""
    raw_relative = relative_path(row["raw_path"], "source raw path")
    raw = source_root / raw_relative
    if (
        raw.is_symlink()
        or not raw.is_file()
        or raw.stat().st_size != row["raw_bytes"]
    ):
        raise ValueError(f"source raw bytes are absent or changed: {raw}")
    if verify_checksums and digest(raw) != row["raw_sha256"]:
        raise ValueError(f"source raw checksum differs: {raw}")
    sidecar = Path(f"{raw}.sha256")
    fields = sidecar.read_text().split() if sidecar.is_file() else []
    if (
        sidecar.is_symlink()
        or len(fields) != 2
        or fields[0] != row["raw_sha256"]
        or Path(fields[1]).name != raw.name
    ):
        raise ValueError(f"source raw checksum sidecar differs: {sidecar}")
    for path_key, sha_key in (
        ("attempt_start_claim_path", "attempt_start_claim_sha256"),
        ("attempt_receipt_path", "attempt_receipt_sha256"),
        (
            "raw_validation_receipt_path",
            "raw_validation_receipt_sha256",
        ),
        ("raw_validation_log_path", "raw_validation_log_sha256"),
        (
            "allocation_authorization_path",
            "allocation_authorization_sha256",
        ),
        ("submission_record_path", "submission_record_sha256"),
    ):
        source = source_root / relative_path(row[path_key], path_key)
        if (
            source.is_symlink()
            or not source.is_file()
            or digest(source) != row[sha_key]
        ):
            raise ValueError(
                f"source production evidence is absent or changed: {source}"
            )


def prefixed_source_path(prefix: str, value: object, label: str) -> str:
    relative = relative_path(value, label)
    return (Path(prefix) / relative).as_posix()


def source_entries_for_parent(
    parent_summary: dict, parent_identity: dict
) -> list[dict]:
    if parent_summary["schema"] == SUMMARY_SCHEMA:
        source = {
                "campaign": parent_identity["campaign"],
                "campaign_ordinal": parent_identity["campaign_ordinal"],
                "production_prefix": parent_identity["campaign"],
                "jobs_in_final_union_per_tune": parent_identity[
                    "jobs_per_tune"
                ],
                **{
                    key: parent_identity[key]
                    for key in (
                        "canonical_manifest_sha256",
                        "freeze_summary_sha256",
                        "freeze_seal_sha256",
                        "physics_origin_signoff_sha256",
                        "full_production_gate_authorization_sha256",
                        "registry_baseline_sha256",
                        "global_submission_claim_sha256",
                    )
                },
            }
        if "equal_tune_expansion_authorization_sha256" in parent_identity:
            source["equal_tune_expansion_authorization_sha256"] = (
                parent_identity[
                    "equal_tune_expansion_authorization_sha256"
                ]
            )
        return [source]
    entries = parent_summary.get("source_freezes")
    if not isinstance(entries, list):
        raise ValueError("superseding parent source-freeze inventory is absent")
    return [dict(entry) for entry in entries]


def transform_source_row(
    row: dict,
    *,
    final_campaign: str,
    final_campaign_ordinal: int,
    final_slot: int,
    source_entry: dict,
    add_prefix: bool,
) -> dict:
    transformed = dict(row)
    original_definition = transformed["production_definition_sha256"]
    if add_prefix:
        prefix = source_entry["production_prefix"]
        for key in (
            "raw_path",
            "attempt_start_claim_path",
            "attempt_receipt_path",
            "raw_validation_receipt_path",
            "raw_validation_log_path",
            "allocation_authorization_path",
            "submission_record_path",
        ):
            transformed[key] = prefixed_source_path(
                prefix, transformed[key], key
            )
        transformed.update(
            {
                "source_canonical_slot": row["canonical_slot"],
                "source_manifest_sha256": source_entry[
                    "canonical_manifest_sha256"
                ],
                "source_freeze_summary_sha256": source_entry[
                    "freeze_summary_sha256"
                ],
                "source_freeze_seal_sha256": source_entry[
                    "freeze_seal_sha256"
                ],
                "source_production_prefix": prefix,
                "source_production_definition_sha256": original_definition,
            }
        )
    else:
        if transformed.get("schema") != SUPERSEDING_ROW_SCHEMA:
            raise ValueError("unprefixed source row is not superseding v3")
    transformed.update(
        {
            "schema": SUPERSEDING_ROW_SCHEMA,
            "final_campaign": final_campaign,
            "final_campaign_ordinal": final_campaign_ordinal,
            "canonical_slot": final_slot,
            "block": final_slot % BLOCKS,
            "block_position": final_slot // BLOCKS,
        }
    )
    transformed["production_definition_sha256"] = production_definition(
        transformed
    )
    return transformed


def supersede(args: argparse.Namespace) -> int:
    """Create an immutable equal-tune union from two sealed freezes."""
    for label, path in (
        ("parent freeze", args.parent_freeze),
        ("extension freeze", args.extension_freeze),
        ("production collection root", args.production_collection_root),
        ("superseding output", args.output_dir),
    ):
        if path.is_symlink():
            raise ValueError(f"{label} must not be a symbolic link: {path}")
    parent_dir = args.parent_freeze.resolve()
    extension_dir = args.extension_freeze.resolve()
    collection_root = args.production_collection_root.resolve()
    output_dir = args.output_dir.resolve()
    if collection_root.is_symlink() or not collection_root.is_dir():
        raise ValueError("production collection root is not a real directory")
    if output_dir.exists():
        raise ValueError(
            f"refusing to alter an existing superseding freeze: {output_dir}"
        )
    current_commit = require_clean_checkout()

    parent_identity = source_freeze_identity(parent_dir)
    extension_identity = source_freeze_identity(extension_dir)
    parent_summary = read_json(parent_dir / "freeze_summary.json")
    extension_summary = read_json(extension_dir / "freeze_summary.json")
    if extension_summary.get("schema") != EXTENSION_SUMMARY_SCHEMA:
        raise ValueError(
            "extension source is not a separately sealed equal-tune extension"
        )
    if parent_identity["campaign"] == extension_identity["campaign"]:
        raise ValueError("superseding extension must use a new campaign name")
    parent_production = collection_root / parent_identity["campaign"]
    extension_production = collection_root / extension_identity["campaign"]
    if parent_summary["schema"] == SUMMARY_SCHEMA:
        expected_parent_dir = parent_production / "freeze"
        parent_row_root = parent_production
    else:
        expected_parent_dir = parent_production / "freeze"
        parent_row_root = collection_root
    expected_extension_dir = extension_production / "extension_freeze"
    if (
        parent_dir != expected_parent_dir.resolve()
        or extension_dir != expected_extension_dir.resolve()
        or output_dir != (extension_production / "freeze").resolve()
    ):
        raise ValueError(
            "parent must be PRODUCTION_COLLECTION/PARENT/freeze and "
            "extension/final outputs must be CHILD/extension_freeze and "
            "CHILD/freeze"
        )

    campaign_dir = (
        REPOSITORY_ROOT
        / "campaigns"
        / str(extension_identity["campaign"])
    )
    campaign_path = campaign_dir / "campaign.json"
    campaign = read_json(campaign_path)
    additional_jobs = require_int(
        campaign.get("planned_additional_jobs_per_tune"),
        "planned additional jobs per tune",
        1,
    )
    if (
        campaign.get("campaign_kind") != EXPANSION_CAMPAIGN_KIND
        or additional_jobs % BLOCKS
        or additional_jobs != extension_identity["jobs_per_tune"]
    ):
        raise ValueError(
            "extension campaign is not an equal-tune multiple-of-ten expansion"
        )
    parent_binding = campaign.get("supersedes")
    expected_parent_binding = {
        "campaign": parent_identity["campaign"],
        "campaign_ordinal": parent_identity["campaign_ordinal"],
        "jobs_per_tune": parent_identity["jobs_per_tune"],
        "canonical_manifest_sha256": parent_identity[
            "canonical_manifest_sha256"
        ],
        "freeze_summary_sha256": parent_identity["freeze_summary_sha256"],
        "freeze_seal_sha256": parent_identity["freeze_seal_sha256"],
    }
    if not isinstance(parent_binding, dict) or any(
        parent_binding.get(key) != value
        for key, value in expected_parent_binding.items()
    ):
        raise ValueError("extension campaign parent binding differs")
    final_jobs = parent_identity["jobs_per_tune"] + additional_jobs
    if (
        campaign.get("planned_final_jobs_per_tune") != final_jobs
        or final_jobs < 100
        or final_jobs % BLOCKS
    ):
        raise ValueError("extension campaign final equal-tune exposure differs")
    if (
        campaign.get("campaign") != extension_identity["campaign"]
        or campaign.get("campaign_ordinal")
        != extension_identity["campaign_ordinal"]
        or campaign.get("repository_commit")
        != extension_summary["repository_implementation_commit"]
    ):
        raise ValueError("extension campaign/freeze identity differs")
    require_ancestor(campaign["repository_commit"], current_commit)

    contract_keys = (
        "successful_events_per_job",
        "raw_schema",
        "origin_algorithm",
        "selector",
        "species_registry_sha256",
        "pair_registry_sha256",
        "tune_difference_allowlist_schema",
        "tune_difference_allowlist_sha256",
    )
    for key in contract_keys:
        if parent_summary.get(key) != extension_summary.get(key):
            raise ValueError(
                f"parent and extension production contract differs: {key}"
            )

    parent_rows = read_jsonl(parent_dir / "canonical_manifest.jsonl")
    extension_rows = read_jsonl(extension_dir / "canonical_manifest.jsonl")
    for tune in TUNES:
        definitions = {
            scientific_production_definition(row)
            for row in (*parent_rows, *extension_rows)
            if row.get("tune") == tune
        }
        if len(definitions) != 1:
            raise ValueError(
                "parent and extension scientific production definitions "
                f"differ for {tune}"
            )
    parent_sources = source_entries_for_parent(
        parent_summary, parent_identity
    )
    parent_source_by_campaign = {
        source["campaign"]: source for source in parent_sources
    }
    if len(parent_source_by_campaign) != len(parent_sources):
        raise ValueError("parent source campaign inventory is duplicated")
    extension_source = {
        "campaign": extension_identity["campaign"],
        "campaign_ordinal": extension_identity["campaign_ordinal"],
        "production_prefix": extension_identity["campaign"],
        "jobs_in_final_union_per_tune": additional_jobs,
        **{
            key: extension_identity[key]
            for key in (
                "canonical_manifest_sha256",
                "freeze_summary_sha256",
                "freeze_seal_sha256",
                "physics_origin_signoff_sha256",
                "full_production_gate_authorization_sha256",
                "registry_baseline_sha256",
                "global_submission_claim_sha256",
            )
        },
    }
    extension_source[
        "equal_tune_expansion_authorization_sha256"
    ] = extension_identity[
        "equal_tune_expansion_authorization_sha256"
    ]
    if extension_source["campaign"] in parent_source_by_campaign:
        raise ValueError("extension campaign already appears in parent union")
    source_entries = [*parent_sources, extension_source]
    source_ordinals = [
        int(source["campaign_ordinal"]) for source in source_entries
    ]
    if len(source_ordinals) != len(set(source_ordinals)):
        raise ValueError(
            "superseding source campaigns reuse a campaign ordinal"
        )

    rows: list[dict] = []
    for tune in TUNES:
        selected_parent = [
            row for row in parent_rows if row.get("tune") == tune
        ]
        selected_extension = [
            row
            for row in extension_rows
            if row.get("tune") == tune
            and 0 <= int(row.get("canonical_slot", -1)) < additional_jobs
        ]
        if (
            len(selected_parent) != parent_identity["jobs_per_tune"]
            or len(selected_extension) != additional_jobs
        ):
            raise ValueError(
                f"source exposure differs for {tune}: "
                f"parent={len(selected_parent)} extension={len(selected_extension)}"
            )
        selected_parent.sort(key=lambda row: int(row["canonical_slot"]))
        selected_extension.sort(key=lambda row: int(row["canonical_slot"]))
        for slot, row in enumerate(selected_parent):
            source = parent_source_by_campaign.get(row["campaign"])
            if source is None:
                raise ValueError("parent row source is absent from provenance")
            verify_source_row_files(row, parent_row_root)
            rows.append(
                transform_source_row(
                    row,
                    final_campaign=extension_identity["campaign"],
                    final_campaign_ordinal=extension_identity[
                        "campaign_ordinal"
                    ],
                    final_slot=slot,
                    source_entry=source,
                    add_prefix=parent_summary["schema"] == SUMMARY_SCHEMA,
                )
            )
        for offset, row in enumerate(selected_extension):
            verify_source_row_files(row, extension_production)
            rows.append(
                transform_source_row(
                    row,
                    final_campaign=extension_identity["campaign"],
                    final_campaign_ordinal=extension_identity[
                        "campaign_ordinal"
                    ],
                    final_slot=parent_identity["jobs_per_tune"] + offset,
                    source_entry=extension_source,
                    add_prefix=True,
                )
            )

    seeds = [row["seed"] for row in rows]
    raw_paths = [row["raw_path"] for row in rows]
    receipts = [row["attempt_receipt_path"] for row in rows]
    event_namespaces = [
        (
            row["campaign_ordinal"],
            row["tune"],
            row["logical_id"],
            row["attempt"],
        )
        for row in rows
    ]
    for label, values in (
        ("seed", seeds),
        ("raw path", raw_paths),
        ("attempt receipt", receipts),
        ("event-ID namespace", event_namespaces),
    ):
        if len(values) != len(set(values)):
            raise ValueError(f"superseding union reuses a {label}")

    canonical_text = jsonl_text(rows)
    artifacts = {"canonical_manifest.jsonl": canonical_text}
    block_hashes: dict[str, str] = {}
    for block in range(BLOCKS):
        block_rows = [row for row in rows if row["block"] == block]
        block_text = jsonl_text(block_rows)
        name = f"block_{block + 1:02d}.jsonl"
        artifacts[name] = block_text
        block_hashes[name] = text_digest(block_text)

    child_prefix = extension_identity["campaign"]
    source_freezes_sha = text_digest(canonical_json(source_entries))
    summary = {
        "schema": SUPERSEDING_SUMMARY_SCHEMA,
        "state": "AWAITING_EXHAUSTIVE_RAW_VALIDATION",
        "campaign": extension_identity["campaign"],
        "campaign_ordinal": extension_identity["campaign_ordinal"],
        "canonical_manifest_sha256": text_digest(canonical_text),
        "block_manifest_sha256": block_hashes,
        "jobs_per_tune": final_jobs,
        "successful_events_per_job": extension_summary[
            "successful_events_per_job"
        ],
        "successful_events_per_tune": final_jobs
        * extension_summary["successful_events_per_job"],
        "block_count": BLOCKS,
        "jobs_per_tune_per_block": final_jobs // BLOCKS,
        "selection_file_sha256": None,
        "repository_commit_at_freeze": current_commit,
        "repository_implementation_commit": campaign[
            "repository_commit"
        ],
        "campaign_json_sha256": digest(campaign_path),
        "candidate_manifest_sha256": digest(
            campaign_dir / "candidate_manifest.jsonl"
        ),
        "seed_ledger_sha256": digest(campaign_dir / "seed_ledger.jsonl"),
        "submission_claim_path": prefixed_source_path(
            child_prefix,
            extension_summary["submission_claim_path"],
            "extension submission claim",
        ),
        "submission_claim_sha256": extension_summary[
            "submission_claim_sha256"
        ],
        "submission_record_path": prefixed_source_path(
            child_prefix,
            extension_summary["submission_record_path"],
            "extension submission record",
        ),
        "submission_record_sha256": extension_summary[
            "submission_record_sha256"
        ],
        "physics_origin_signoff_sha256": extension_summary[
            "physics_origin_signoff_sha256"
        ],
        "full_production_gate_authorization_sha256": extension_summary[
            "full_production_gate_authorization_sha256"
        ],
        "equal_tune_expansion_authorization_sha256": extension_summary[
            "equal_tune_expansion_authorization_sha256"
        ],
        "registry_baseline_sha256": extension_summary[
            "registry_baseline_sha256"
        ],
        "global_submission_claim_sha256": extension_summary[
            "global_submission_claim_sha256"
        ],
        "raw_schema": extension_summary["raw_schema"],
        "origin_algorithm": extension_summary["origin_algorithm"],
        "selector": extension_summary["selector"],
        "species_registry_sha256": extension_summary[
            "species_registry_sha256"
        ],
        "pair_registry_sha256": extension_summary[
            "pair_registry_sha256"
        ],
        "tune_difference_allowlist_schema": extension_summary[
            "tune_difference_allowlist_schema"
        ],
        "tune_difference_allowlist_sha256": extension_summary[
            "tune_difference_allowlist_sha256"
        ],
        "supersedes": {
            "contract": "immutable_equal_tune_union_v1",
            "parent_campaign": parent_identity["campaign"],
            "parent_campaign_ordinal": parent_identity["campaign_ordinal"],
            "parent_jobs_per_tune": parent_identity["jobs_per_tune"],
            "parent_canonical_manifest_sha256": parent_identity[
                "canonical_manifest_sha256"
            ],
            "parent_freeze_summary_sha256": parent_identity[
                "freeze_summary_sha256"
            ],
            "parent_freeze_seal_sha256": parent_identity[
                "freeze_seal_sha256"
            ],
            "extension_campaign": extension_identity["campaign"],
            "extension_campaign_ordinal": extension_identity[
                "campaign_ordinal"
            ],
            "extension_canonical_manifest_sha256": extension_identity[
                "canonical_manifest_sha256"
            ],
            "extension_freeze_summary_sha256": extension_identity[
                "freeze_summary_sha256"
            ],
            "extension_freeze_seal_sha256": extension_identity[
                "freeze_seal_sha256"
            ],
            "additional_jobs_per_tune": additional_jobs,
            "final_jobs_per_tune": final_jobs,
            "block_assignment":
                "canonical_slot_modulo_10_over_complete_union_v1",
        },
        "source_freezes": source_entries,
        "source_freezes_sha256": source_freezes_sha,
        "validation_receipt_path": VALIDATION_RECEIPT_NAME,
        "seal_path": SEAL_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    artifacts["freeze_summary.json"] = (
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    promote_freeze_artifacts(output_dir, artifacts)
    print(
        "CANONICAL_SUPERSEDING_FREEZE_AWAITING_VALIDATION "
        f"parent_jobs_per_tune={parent_identity['jobs_per_tune']} "
        f"additional_jobs_per_tune={additional_jobs} "
        f"final_jobs_per_tune={final_jobs} rows={len(rows)} "
        f"directory={output_dir}"
    )
    return 0


def seal(args: argparse.Namespace) -> int:
    directory = args.directory.resolve()
    production_root = args.production_root.resolve()
    source_log = args.validation_log.resolve()
    validate_directory(directory, require_seal=False)
    rows = read_jsonl(directory / "canonical_manifest.jsonl")
    summary = read_json(directory / "freeze_summary.json")
    (
        jobs_per_tune,
        expected_rows,
        _,
        summary_schema,
        receipt_schema,
        seal_schema,
    ) = manifest_shape(summary)

    for row in rows:
        raw = production_root / relative_path(row["raw_path"], "raw path")
        if (
            raw.is_symlink()
            or not raw.is_file()
            or raw.stat().st_size != row["raw_bytes"]
            or digest(raw) != row["raw_sha256"]
        ):
            raise ValueError(f"raw bytes changed before seal: {raw}")
        for path_key, sha_key in (
            (
                "attempt_start_claim_path",
                "attempt_start_claim_sha256",
            ),
            ("attempt_receipt_path", "attempt_receipt_sha256"),
            (
                "raw_validation_receipt_path",
                "raw_validation_receipt_sha256",
            ),
            ("raw_validation_log_path", "raw_validation_log_sha256"),
            (
                "allocation_authorization_path",
                "allocation_authorization_sha256",
            ),
            ("submission_record_path", "submission_record_sha256"),
        ):
            source = production_root / relative_path(row[path_key], path_key)
            if source.is_symlink() or not source.is_file():
                raise ValueError(f"bound production receipt is absent: {source}")
            if digest(source) != row[sha_key]:
                raise ValueError(f"bound production receipt changed: {source}")
    claim = production_root / relative_path(
        summary["submission_claim_path"], "submission claim path"
    )
    if digest(claim) != summary["submission_claim_sha256"]:
        raise ValueError("full-production submission claim changed before seal")
    claim_value = read_json(claim)
    launch_hash_fields = (
        "physics_origin_signoff_sha256",
        "full_production_gate_authorization_sha256",
        "registry_baseline_sha256",
    )
    if summary_schema in {
        EXTENSION_SUMMARY_SCHEMA,
        SUPERSEDING_SUMMARY_SCHEMA,
    }:
        launch_hash_fields = (
            *launch_hash_fields,
            "equal_tune_expansion_authorization_sha256",
        )
    for key in launch_hash_fields:
        if claim_value.get(key) != summary[key]:
            raise ValueError(
                f"full-production launch provenance {key} changed before seal"
            )
    campaign_dir = (
        REPOSITORY_ROOT / "campaigns" / str(summary["campaign"])
    )
    campaign_authorizations = [
        (
            campaign_dir / "PHYSICS_ORIGIN_SIGNOFF.json",
            "physics_origin_signoff_sha256",
        ),
        (
            campaign_dir / "FULL_PRODUCTION_GATE_AUTHORIZATION.json",
            "full_production_gate_authorization_sha256",
        ),
    ]
    if summary_schema in {
        EXTENSION_SUMMARY_SCHEMA,
        SUPERSEDING_SUMMARY_SCHEMA,
    }:
        campaign_authorizations.append(
            (
                campaign_dir
                / "EQUAL_TUNE_EXPANSION_AUTHORIZATION.json",
                "equal_tune_expansion_authorization_sha256",
            )
        )
    for source, key in campaign_authorizations:
        if (
            source.is_symlink()
            or not source.is_file()
            or digest(source) != summary[key]
        ):
            raise ValueError(
                f"full-production launch provenance changed: {source}"
            )
    if summary_schema == SUPERSEDING_SUMMARY_SCHEMA:
        for source_entry in summary["source_freezes"]:
            source_production = (
                production_root / str(source_entry["campaign"])
            )
            matching_freezes: list[Path] = []
            for source_freeze in (
                source_production / "freeze",
                source_production / "extension_freeze",
            ):
                source_manifest = (
                    source_freeze / "canonical_manifest.jsonl"
                )
                source_summary = source_freeze / "freeze_summary.json"
                source_seal = source_freeze / SEAL_NAME
                if (
                    source_manifest.is_file()
                    and not source_manifest.is_symlink()
                    and source_summary.is_file()
                    and not source_summary.is_symlink()
                    and source_seal.is_file()
                    and not source_seal.is_symlink()
                    and digest(source_manifest)
                    == source_entry["canonical_manifest_sha256"]
                    and digest(source_summary)
                    == source_entry["freeze_summary_sha256"]
                    and digest(source_seal)
                    == source_entry["freeze_seal_sha256"]
                ):
                    matching_freezes.append(source_freeze)
            if len(matching_freezes) != 1:
                raise ValueError(
                    "superseding source freeze is absent, changed, or "
                    f"ambiguous: {source_entry['campaign']}"
                )
            validate_directory(
                matching_freezes[0], require_seal=True
            )
            source_campaign_dir = (
                REPOSITORY_ROOT
                / "campaigns"
                / str(source_entry["campaign"])
            )
            for source_name, key in (
                (
                    "PHYSICS_ORIGIN_SIGNOFF.json",
                    "physics_origin_signoff_sha256",
                ),
                (
                    "FULL_PRODUCTION_GATE_AUTHORIZATION.json",
                    "full_production_gate_authorization_sha256",
                ),
            ):
                source = source_campaign_dir / source_name
                if (
                    source.is_symlink()
                    or not source.is_file()
                    or digest(source) != source_entry[key]
                ):
                    raise ValueError(
                        "superseding source launch provenance changed: "
                        f"{source}"
                    )
            expansion_sha = source_entry.get(
                "equal_tune_expansion_authorization_sha256"
            )
            if expansion_sha is not None:
                source = (
                    source_campaign_dir
                    / "EQUAL_TUNE_EXPANSION_AUTHORIZATION.json"
                )
                if (
                    source.is_symlink()
                    or not source.is_file()
                    or digest(source) != expansion_sha
                ):
                    raise ValueError(
                        "superseding source expansion authorization changed: "
                        f"{source}"
                    )
    registry_value = claim_value.get("global_submission_registry")
    if not isinstance(registry_value, str):
        raise ValueError("full-production claim global registry is absent")
    registry = Path(registry_value)
    baseline = registry / "reservation_baseline.json"
    global_claim = (
        registry / "claims" / f"{summary['campaign']}.json"
    )
    if (
        not registry.is_absolute()
        or baseline.is_symlink()
        or not baseline.is_file()
        or digest(baseline) != summary["registry_baseline_sha256"]
    ):
        raise ValueError(
            "reviewed global seed-reservation baseline changed before seal"
        )
    if (
        global_claim.is_symlink()
        or not global_claim.is_file()
        or digest(global_claim)
        != summary["global_submission_claim_sha256"]
    ):
        raise ValueError(
            "global full-production reservation changed before seal"
        )
    if not source_log.is_file():
        raise FileNotFoundError(f"canonical ROOT validation log absent: {source_log}")
    log_text = source_log.read_text()
    marker = re.findall(
        rf"^CANONICAL_RAW_VALIDATION errors=0 files={expected_rows} "
        rf"unique_seeds={expected_rows} total_events=([0-9]+)$",
        log_text,
        flags=re.MULTILINE,
    )
    expected_events = expected_rows * summary["successful_events_per_job"]
    if len(marker) != 1 or int(marker[0]) != expected_events:
        raise ValueError(
            "ROOT validation log lacks one exact successful canonical summary"
        )
    if "CANONICAL_RAW_ERROR" in log_text or "RAW_VALIDATION_ERROR" in log_text:
        raise ValueError("ROOT validation log contains an error marker")

    destination_log = directory / VALIDATION_LOG_NAME
    receipt_path = directory / VALIDATION_RECEIPT_NAME
    seal_path = directory / SEAL_NAME
    if any(path.exists() for path in (destination_log, receipt_path, seal_path)):
        return validate_directory(directory, require_seal=True)
    exclusive_write(destination_log, log_text)
    receipt = {
        "schema": receipt_schema,
        "state": "PASS",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": summary["campaign"],
        "campaign_ordinal": summary["campaign_ordinal"],
        "canonical_manifest_sha256": digest(
            directory / "canonical_manifest.jsonl"
        ),
        "canonical_manifest_rows": expected_rows,
        "raw_inventory_sha256": raw_inventory_digest(rows),
        "validated_raw_files": expected_rows,
        "validated_successful_events": expected_events,
        "validation_log_sha256": digest(destination_log),
        "submission_claim_sha256": summary["submission_claim_sha256"],
        "submission_record_sha256": summary["submission_record_sha256"],
        "physics_origin_signoff_sha256":
            summary["physics_origin_signoff_sha256"],
        "full_production_gate_authorization_sha256":
            summary["full_production_gate_authorization_sha256"],
        "registry_baseline_sha256":
            summary["registry_baseline_sha256"],
        "global_submission_claim_sha256":
            summary["global_submission_claim_sha256"],
        "validator_sha256": {
            "Validation/ValidateCanonicalRawManifest.C": digest(
                REPOSITORY_ROOT / "Validation/ValidateCanonicalRawManifest.C"
            ),
            "Validation/ValidateRawOutput.C": digest(
                REPOSITORY_ROOT / "Validation/ValidateRawOutput.C"
            ),
            "tools/canonical_manifest.py": digest(Path(__file__).resolve()),
        },
    }
    if summary_schema in {
        EXTENSION_SUMMARY_SCHEMA,
        SUPERSEDING_SUMMARY_SCHEMA,
    }:
        receipt[
            "equal_tune_expansion_authorization_sha256"
        ] = summary["equal_tune_expansion_authorization_sha256"]
    if summary_schema == SUPERSEDING_SUMMARY_SCHEMA:
        receipt.update(
            {
                "jobs_per_tune": jobs_per_tune,
                "source_freezes_sha256": summary[
                    "source_freezes_sha256"
                ],
                "supersedes": summary["supersedes"],
            }
        )
    exclusive_write(
        receipt_path, json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    seal_value = {
        "schema": seal_schema,
        "state": "SEALED",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "canonical_manifest_sha256": digest(
            directory / "canonical_manifest.jsonl"
        ),
        "validation_receipt_path": VALIDATION_RECEIPT_NAME,
        "validation_receipt_sha256": digest(receipt_path),
        "validation_log_path": VALIDATION_LOG_NAME,
        "validation_log_sha256": digest(destination_log),
        "physics_origin_signoff_sha256":
            summary["physics_origin_signoff_sha256"],
        "full_production_gate_authorization_sha256":
            summary["full_production_gate_authorization_sha256"],
        "registry_baseline_sha256":
            summary["registry_baseline_sha256"],
        "global_submission_claim_sha256":
            summary["global_submission_claim_sha256"],
    }
    if summary_schema in {
        EXTENSION_SUMMARY_SCHEMA,
        SUPERSEDING_SUMMARY_SCHEMA,
    }:
        seal_value[
            "equal_tune_expansion_authorization_sha256"
        ] = summary["equal_tune_expansion_authorization_sha256"]
    if summary_schema == SUPERSEDING_SUMMARY_SCHEMA:
        seal_value.update(
            {
                "jobs_per_tune": jobs_per_tune,
                "source_freezes_sha256": summary[
                    "source_freezes_sha256"
                ],
                "supersedes": summary["supersedes"],
            }
        )
    exclusive_write(
        seal_path, json.dumps(seal_value, indent=2, sort_keys=True) + "\n"
    )
    return validate_directory(directory, require_seal=True)


def validate(args: argparse.Namespace) -> int:
    if (
        args.allow_unsealed
        and os.environ.get("HADRONIZATION_CANONICAL_SEALING") != "1"
    ):
        raise ValueError(
            "--allow-unsealed is restricted to the internal sealing workflow"
        )
    return validate_directory(
        args.directory.resolve(), require_seal=not args.allow_unsealed
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    freeze_parser = subparsers.add_parser("freeze")
    freeze_parser.add_argument("campaign_dir", type=Path)
    freeze_parser.add_argument("production_root", type=Path)
    freeze_parser.add_argument("output_dir", type=Path)
    freeze_parser.add_argument("--selection", type=Path)
    freeze_parser.add_argument(
        "--verify-checksums", action=argparse.BooleanOptionalAction, default=True
    )
    freeze_parser.set_defaults(function=freeze)

    supersede_parser = subparsers.add_parser(
        "supersede",
        help=(
            "create a new equal-tune final union from a sealed parent and "
            "a separately authorised sealed expansion campaign"
        ),
    )
    supersede_parser.add_argument("parent_freeze", type=Path)
    supersede_parser.add_argument("extension_freeze", type=Path)
    supersede_parser.add_argument("production_collection_root", type=Path)
    supersede_parser.add_argument("output_dir", type=Path)
    supersede_parser.set_defaults(function=supersede)

    seal_parser = subparsers.add_parser("seal")
    seal_parser.add_argument("directory", type=Path)
    seal_parser.add_argument("production_root", type=Path)
    seal_parser.add_argument("validation_log", type=Path)
    seal_parser.set_defaults(function=seal)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("directory", type=Path)
    validate_parser.add_argument("--allow-unsealed", action="store_true")
    validate_parser.set_defaults(function=validate)

    args = parser.parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
