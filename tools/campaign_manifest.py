#!/usr/bin/env python3
"""Create and validate immutable heavy-flavour campaign/seed manifests."""

from __future__ import annotations

import argparse
import ast
import contextlib
import datetime
import fcntl
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
GLOBAL_OFFSETS = {"MONASH": 0, "JUNCTIONS": 100, "CLOSEPACKING": 300}
SLOTS = {"MONASH": 100, "JUNCTIONS": 200, "CLOSEPACKING": 200}
EQUAL_TUNE_EXPANSION_KIND = "equal_tune_canonical_expansion_v1"
EXPANSION_AUTHORIZATION_SCHEMA = (
    "hf_equal_tune_expansion_authorization_v1"
)
EXPANSION_STORAGE_SCHEMA = (
    "hf_equal_tune_expansion_storage_projection_v1"
)
EXPANSION_COVERAGE_SCHEMA = "hf_final_coverage_precision_report_v1"
EXPANSION_COVERAGE_SPEC_SCHEMA = (
    "hf_expansion_coverage_precision_spec_v1"
)
EXPANSION_COVERAGE_MATRIX_SCHEMA = (
    "hf_final_coverage_precision_matrix_v1"
)
EXPANSION_SELECTION_RULE = (
    "predeclared_coverage_and_precision_only_v1"
)
EXPANSION_CAPACITY_POLICY = (
    "live_statvfs_available_after_full_projection_ge_5_percent_capacity_v1"
)
EXPANSION_STORAGE_MAX_RECHECK_AGE = datetime.timedelta(minutes=15)
EXPANSION_LIVE_STORAGE_SCHEMA = (
    "hf_equal_tune_expansion_live_storage_recheck_v1"
)
GATE_B_PROFILES = {
    0: ("1.0", 1_000_000, "long", "one_million_central"),
    1: ("0.5", 100_000, "medium", "pthat_sensitivity_low"),
    2: ("2.0", 100_000, "medium", "pthat_sensitivity_high"),
}
SAFE_CAMPAIGN = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,126}[A-Za-z0-9])?$"
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_COMMIT = re.compile(r"^[0-9a-f]{40}$")
GATE_D_STORAGE_MAX_RECHECK_AGE = datetime.timedelta(minutes=15)
CONDOR_SUBMISSION_CLASSAD_SCHEMA = "hf_condor_submission_classads_v1"
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
FULL_ORIGIN_SIGNOFF_SCHEMA = "hf_full_production_origin_signoff_v1"
FULL_ORIGIN_APPROVAL_DECISION = "APPROVE_FULL_PRODUCTION"
ZERO_UNRESOLVED_TREATMENT = (
    "No unresolved trigger candidates were observed; no special treatment "
    "is required."
)
NONZERO_UNRESOLVED_TREATMENT = (
    "Exclude unresolved triggers centrally; retain unresolved associates "
    "as a reported origin category"
)
GATE_D_STORAGE_SCHEMA = "hf_gate_d_storage_projection_v1"
GATE_D_STORAGE_COMPONENT_KEYS = {
    "full_100_200_200_candidate_raw_bytes",
    "simultaneous_partial_raw_bytes",
    "canonical_300_job_per_job_analysis_bytes",
    "final_merged_central_bytes",
    "final_ten_block_bytes",
    "full_plots_logs_validation_evidence_bytes",
    "raw_filesystem_required_additional_bytes",
    "analysis_filesystem_required_additional_bytes",
    "total_required_additional_bytes",
}
GATE_D_STORAGE_POLICY = {
    "maximum_fraction_of_current_available": 0.70,
    "minimum_projected_free_fraction": 0.05,
    "minimum_projected_free_bytes": 500 * 1024**3,
    "simultaneous_partial_raw_multiplier": 1,
    "full_plot_scale_factor": 10,
    "minimum_full_plot_and_evidence_bytes": 10 * 1024**3,
}
SUBMISSION_KINDS = {
    "gate_b": {
        "campaign_schema": "hf_gate_b_pilot_campaign_v1",
        "roles": ("pilot",),
        "expected_rows": 9,
        "submit_file": "submit_gate_b.sub",
        "claim_file": "gate_b_attempt0_submission_claim.json",
        "claim_schema": "hf_gate_b_submission_claim_v1",
        "record_file": "gate_b_attempt0_submitted.json",
        "record_schema": "hf_gate_b_submission_record_v1",
    },
    "full": {
        "campaign_schema": "hf_campaign_v1",
        "roles": ("primary", "reserve"),
        "expected_rows": 500,
        "submit_file": "submit_candidates.sub",
        "claim_file": "full_candidates_attempt0_submission_claim.json",
        "claim_schema": "hf_full_submission_claim_v1",
        "record_file": "full_candidates_attempt0_submitted.json",
        "record_schema": "hf_full_submission_record_v1",
    },
}
MAX_ATTEMPTS_PER_LOGICAL_ID = 4096
GATE_B_COMMAND_PURPOSES = {
    "canonical_gate_b_campaign_validation",
    "fresh_raw_to_frozen_pthat_decision_recheck",
    "raw_resource_stability_compression_audit",
    "cross_tune_effective_settings_audit",
    *{
        f"origin_resolution_audit_{tune}"
        for tune in TUNES
    },
    *{
        f"unresolved_origin_listing_{tune}"
        for tune in TUNES
    },
}
GATE_C_COMMAND_NAMES = {
    "git_diff_check",
    "worker_provenance_contract",
    "full_submission_contract",
    "gate_b_submission_contract",
    "submit_rendering_contract",
    "canonical_postproduction_contract",
    "gate_b_analysis_validation_contract",
    "statistical_robustness_contract",
    "publication_gate_c_report_contract",
    "gate_c_missing_evidence_contract",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def changed_tracked_paths(checkout_root: Path) -> set[str]:
    """Return tracked paths whose index/worktree bytes differ from HEAD."""
    output = subprocess.check_output(
        [
            "git",
            "-C",
            str(checkout_root),
            "diff",
            "--name-only",
            "-z",
            "HEAD",
            "--",
        ]
    )
    return {
        entry.decode("utf-8", errors="strict")
        for entry in output.split(b"\0")
        if entry
    }


def require_tracked_clean(
    checkout_root: Path, allowed_paths: set[str] | None = None
) -> None:
    allowed = allowed_paths or set()
    unexpected = changed_tracked_paths(checkout_root) - allowed
    if unexpected:
        raise ValueError(
            "tracked checkout changes are not authorized: "
            + ", ".join(sorted(unexpected))
        )


def git_file_sha256(
    checkout_root: Path, repository_commit: str, relative_path: str
) -> str:
    if not GIT_COMMIT.fullmatch(repository_commit):
        raise ValueError("repository commit is not a lowercase 40-hex SHA")
    if (
        not relative_path
        or relative_path.startswith("/")
        or ".." in Path(relative_path).parts
    ):
        raise ValueError("tracked-file path is unsafe")
    content = subprocess.check_output(
        [
            "git",
            "-C",
            str(checkout_root),
            "show",
            f"{repository_commit}:{relative_path}",
        ]
    )
    return hashlib.sha256(content).hexdigest()


def ensure_directory_chain_no_symlinks(anchor: Path, directory: Path) -> None:
    anchor = Path(os.path.abspath(anchor))
    directory = Path(os.path.abspath(directory))
    anchor_metadata = os.lstat(anchor)
    if (
        stat.S_ISLNK(anchor_metadata.st_mode)
        or not stat.S_ISDIR(anchor_metadata.st_mode)
    ):
        raise ValueError(f"canonical anchor is not a real directory: {anchor}")
    try:
        relative = directory.relative_to(anchor)
    except ValueError as error:
        raise ValueError(f"path is outside canonical anchor: {directory}") from error
    current = anchor
    for component in relative.parts:
        current = current / component
        try:
            os.mkdir(current, 0o755)
        except FileExistsError:
            pass
        metadata = os.lstat(current)
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(
                f"production path component is not a real directory: {current}"
            )


def require_existing_directory_chain_no_symlinks(directory: Path) -> Path:
    """Require an absolute, existing directory whose path contains no symlink."""
    directory = Path(os.path.abspath(directory))
    if not directory.is_absolute():
        raise ValueError("directory path must be absolute")
    current = Path(directory.anchor)
    for component in directory.parts[1:]:
        current /= component
        try:
            metadata = os.lstat(current)
        except FileNotFoundError as error:
            raise ValueError(
                f"required directory path is absent: {current}"
            ) from error
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(
                f"directory path component is not a real directory: {current}"
            )
    return directory


@contextlib.contextmanager
def locked_regular_file(path: Path):
    """Open and exclusively lock a single-link regular file without symlinks."""
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise ValueError(
            f"lock cannot be opened without following links: {path}"
        ) from error
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ValueError(f"lock is not a single-link regular file: {path}")
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ValueError(f"lock permissions are not private: {path}")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        with os.fdopen(descriptor, "r+") as stream:
            descriptor = -1
            yield stream
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def repository_identity(checkout_root: Path) -> str:
    remote = subprocess.check_output(
        ["git", "-C", str(checkout_root), "remote", "get-url", "origin"],
        text=True,
    ).strip()
    if not remote:
        raise ValueError("origin remote URL is empty")
    scp_match = re.fullmatch(r"git@([^:]+):(.+)", remote)
    if scp_match:
        host, path = scp_match.groups()
    else:
        url_match = re.fullmatch(
            r"(?:https?|ssh|git)://(?:[^@/]+@)?([^/]+)/(.+)", remote
        )
        if not url_match:
            raise ValueError(
                "origin must be an SSH/HTTP(S)/git repository URL for "
                "cross-checkout submission identity"
            )
        host, path = url_match.groups()
    path = path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    if not path or ".." in Path(path).parts:
        raise ValueError("origin repository path is unsafe")
    host = host.lower()
    if host == "github.com":
        path = path.lower()
    return f"{host}/{path}"


def global_submission_registry(checkout_root: Path) -> tuple[Path, str]:
    identity = repository_identity(checkout_root)
    identity_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    configured_root = os.environ.get(
        "HADRONIZATION_SUBMISSION_REGISTRY_ROOT"
    )
    if configured_root:
        registry_root = Path(configured_root)
        if not registry_root.is_absolute():
            raise ValueError(
                "HADRONIZATION_SUBMISSION_REGISTRY_ROOT must be absolute"
            )
        registry_root = require_existing_directory_chain_no_symlinks(
            registry_root
        )
    else:
        registry_root = (
            Path.home()
            / ".local"
            / "state"
            / "hadronization"
            / "submission_registry"
        )
        registry_root = require_existing_directory_chain_no_symlinks(
            registry_root
        )
    registry = registry_root / identity_hash
    require_existing_directory_chain_no_symlinks(registry)
    return registry, identity


def claimed_global_registry(
    claim: dict, checkout_root: Path, identity: str
) -> Path:
    value = claim.get("global_submission_registry")
    if not isinstance(value, str) or not value:
        raise ValueError("submission claim has no global registry path")
    registry = Path(value)
    canonical, canonical_identity = global_submission_registry(checkout_root)
    if (
        canonical_identity != identity
        or not registry.is_absolute()
        or Path(os.path.abspath(registry)) != canonical
    ):
        raise ValueError("submission claim global registry path is invalid")
    require_existing_directory_chain_no_symlinks(registry)
    return registry


def load_registry_baseline(registry: Path, identity: str) -> tuple[dict, Path]:
    require_existing_directory_chain_no_symlinks(registry)
    path = registry / "reservation_baseline.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError(
            "shared submission registry lacks reviewed "
            f"reservation baseline: {path}"
        )
    baseline_stat = path.stat()
    if baseline_stat.st_nlink != 1 or stat.S_IMODE(
        baseline_stat.st_mode
    ) & 0o222:
        raise ValueError(
            "shared reservation baseline must be single-link and read-only"
        )
    baseline = json.loads(path.read_text())
    if (
        baseline.get("schema") != "hf_submission_registry_baseline_v1"
        or baseline.get("repository_identity") != identity
        or not isinstance(baseline.get("reviewer"), str)
        or not baseline["reviewer"].strip()
        or not isinstance(baseline.get("historical_reservations"), list)
    ):
        raise ValueError("shared submission registry baseline is malformed")
    campaign_names: set[str] = set()
    ordinals: set[int] = set()
    historical_intervals: list[tuple[str, list[list[int]]]] = []
    for reservation in baseline["historical_reservations"]:
        if (
            not isinstance(reservation, dict)
            or not isinstance(reservation.get("campaign"), str)
            or not SAFE_CAMPAIGN.fullmatch(reservation["campaign"])
            or isinstance(reservation.get("campaign_ordinal"), bool)
            or not isinstance(reservation.get("campaign_ordinal"), int)
            or not 1 <= reservation["campaign_ordinal"] <= 65_535
            or not isinstance(reservation.get("reserved_seed_intervals"), list)
        ):
            raise ValueError("historical reservation baseline row is malformed")
        campaign_name = reservation["campaign"]
        campaign_ordinal = reservation["campaign_ordinal"]
        if campaign_name in campaign_names or campaign_ordinal in ordinals:
            raise ValueError(
                "historical reservation baseline reuses a campaign or ordinal"
            )
        campaign_names.add(campaign_name)
        ordinals.add(campaign_ordinal)
        normalized_intervals: list[list[int]] = []
        for interval in reservation["reserved_seed_intervals"]:
            if (
                not isinstance(interval, list)
                or len(interval) != 2
                or any(isinstance(value, bool) for value in interval)
                or any(not isinstance(value, int) for value in interval)
                or not 1 <= interval[0] <= interval[1] <= 900_000_000
            ):
                raise ValueError(
                    "historical reservation seed interval is malformed"
                )
            normalized_intervals.append([int(interval[0]), int(interval[1])])
        for prior_campaign, prior_intervals in historical_intervals:
            if overlapping_seed_intervals(normalized_intervals, prior_intervals):
                raise ValueError(
                    "historical reservation baseline contains overlapping seed "
                    f"intervals for {prior_campaign} and {campaign_name}"
                )
        historical_intervals.append((campaign_name, normalized_intervals))
    return baseline, path


def reserved_seed_intervals(config: dict, ledger: list[dict]) -> list[list[int]]:
    if config.get("schema") == "hf_campaign_v1":
        first = int(config["seed_base"])
        slots, _, _ = campaign_slot_contract(config)
        maximum = int(config["max_attempts_per_logical_id"])
        if not 1 <= maximum <= MAX_ATTEMPTS_PER_LOGICAL_ID:
            raise ValueError(
                "max_attempts_per_logical_id exceeds the 12-bit event-ID domain"
            )
        count = sum(slots.values()) * maximum
        last = first + count - 1
        if first < 1 or last > 900_000_000:
            raise ValueError("full-campaign seed reservation exceeds PYTHIA domain")
        return [[first, last]]
    seeds = sorted({int(row["seed"]) for row in ledger})
    if len(seeds) != len(ledger):
        raise ValueError("submission seed ledger contains duplicate seeds")
    return [[seed, seed] for seed in seeds]


def overlapping_seed_intervals(
    left: list[list[int]], right: list[list[int]]
) -> list[list[int]]:
    overlaps: list[list[int]] = []
    for left_first, left_last in left:
        for right_first, right_last in right:
            first = max(int(left_first), int(right_first))
            last = min(int(left_last), int(right_last))
            if first <= last:
                overlaps.append([first, last])
    return overlaps


def _require_utc_timestamp(
    value: object, description: str
) -> datetime.datetime:
    if not isinstance(value, str):
        raise ValueError(f"{description} timestamp is absent")
    try:
        timestamp = datetime.datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            f"{description} timestamp is not ISO-8601"
        ) from error
    if timestamp.tzinfo is None or timestamp.utcoffset() != datetime.timedelta(0):
        raise ValueError(f"{description} timestamp is not UTC")
    return timestamp


def validate_pthat_spec_preapproval(
    checkout_root: Path, repository_commit: str | None = None
) -> dict:
    """Require the exact frozen pTHat contract to have pre-pilot approval."""
    checkout_root = checkout_root.resolve()
    specification_path = checkout_root / "config/pthat_sensitivity_v1.json"
    if specification_path.is_symlink() or not specification_path.is_file():
        raise ValueError("pTHat sensitivity specification is absent")
    try:
        payload = json.loads(specification_path.read_text())
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(
            "pTHat sensitivity specification is not valid JSON"
        ) from error
    if not isinstance(payload, dict):
        raise ValueError("pTHat sensitivity specification is not an object")
    evaluator_path = (
        checkout_root / "tools/evaluate_pthat_sensitivity.py"
    )
    if evaluator_path.is_symlink() or not evaluator_path.is_file():
        raise ValueError(
            "checkout lacks the exact pTHat sensitivity review contract"
        )
    if repository_commit is not None:
        try:
            expected_evaluator_sha = (
                git_file_sha256(
                    checkout_root,
                    repository_commit,
                    "tools/evaluate_pthat_sensitivity.py",
                )
                if GIT_COMMIT.fullmatch(repository_commit)
                else None
            )
        except subprocess.CalledProcessError as error:
            raise ValueError(
                "pTHat sensitivity review contract campaign commit "
                "cannot be verified"
            ) from error
        if (
            expected_evaluator_sha is None
            or sha256(evaluator_path) != expected_evaluator_sha
        ):
            raise ValueError(
                "pTHat sensitivity review contract differs from campaign commit"
            )
    specification = importlib.util.spec_from_file_location(
        "campaign_pthat_preapproval_contract",
        evaluator_path,
    )
    if specification is None or specification.loader is None:
        raise ValueError("cannot load pTHat sensitivity review contract")
    evaluator = importlib.util.module_from_spec(specification)
    prior_bytecode_setting = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        specification.loader.exec_module(evaluator)
    finally:
        sys.dont_write_bytecode = prior_bytecode_setting
    try:
        evaluator.validate_spec(payload)
    except ValueError as error:
        raise ValueError(
            "campaign blocked: pTHat sensitivity specification lacks exact "
            "pre-pilot scientific approval"
        ) from error
    return payload


def _gate_b_unresolved_evidence(report: dict) -> tuple[dict, int]:
    unresolved = report.get("unresolved_trigger_candidates")
    if not isinstance(unresolved, dict):
        raise ValueError(
            "Gate-B report has no unresolved-trigger evidence"
        )
    samples = unresolved.get("all_samples_by_tune_threshold_and_sector")
    total = unresolved.get("all_nine_samples_total")
    expected_identities = {
        f"{tune}:{threshold}"
        for tune in TUNES
        for threshold in ("0.5", "1.0", "2.0")
    }
    if not isinstance(samples, dict) or set(samples) != expected_identities:
        raise ValueError(
            "Gate-B unresolved-trigger table does not cover the exact nine "
            "tune/threshold samples"
        )
    recomputed = 0
    for identity, sectors in samples.items():
        if not isinstance(sectors, dict) or set(sectors) != {"charm", "beauty"}:
            raise ValueError(
                f"Gate-B unresolved-trigger sector table differs for {identity}"
            )
        for sector, count in sectors.items():
            if (
                isinstance(count, bool)
                or not isinstance(count, int)
                or count < 0
            ):
                raise ValueError(
                    "Gate-B unresolved-trigger count is invalid for "
                    f"{identity}/{sector}"
                )
            recomputed += count
    if isinstance(total, bool) or not isinstance(total, int) or total != recomputed:
        raise ValueError(
            "Gate-B unresolved-trigger total is absent or inconsistent"
        )
    return samples, total


def validate_physics_signoff(
    path: Path,
    config: dict,
    *,
    gate_b_report_path: Path | None = None,
    gate_b_report_relative: str | None = None,
    gate_b_report_sha256: str | None = None,
) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError("physics sign-off is not a regular file")
    row = json.loads(path.read_text())
    if not isinstance(row, dict):
        raise ValueError("physics sign-off is not a JSON object")
    expected = {
        "schema": FULL_ORIGIN_SIGNOFF_SCHEMA,
        "decision": FULL_ORIGIN_APPROVAL_DECISION,
        "campaign": config["campaign"],
        "campaign_ordinal": config["campaign_ordinal"],
        "repository_commit": config["repository_commit"],
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise ValueError(f"physics sign-off {key} differs from campaign")
    if row.get("approved") is not True:
        raise ValueError("physics sign-off is not explicitly approved")
    for key in ("reviewer", "finding", "allowed_unresolved_treatment"):
        value = row.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"physics sign-off {key} is missing or empty")
    reviewer_role = row.get("reviewer_role")
    if reviewer_role != "project_owner":
        raise ValueError(
            "physics sign-off reviewer_role must be project_owner"
        )
    if any(
        placeholder in row["reviewer"].upper()
        for placeholder in ("PROJECT OWNER", "UNIT TEST", "PLACEHOLDER")
    ):
        raise ValueError("physics sign-off reviewer is still a placeholder")
    decision_time = _require_utc_timestamp(
        row.get("decision_utc"), "physics sign-off"
    )
    if (
        decision_time
        > datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=5)
    ):
        raise ValueError("physics sign-off timestamp is implausibly in the future")
    signoff_stat = path.stat()
    if stat.S_IMODE(signoff_stat.st_mode) != 0o444 or signoff_stat.st_nlink != 1:
        raise ValueError(
            "physics sign-off is not sealed as a single-link 0444 file"
        )

    if gate_b_report_path is None:
        return
    if gate_b_report_relative is None or gate_b_report_sha256 is None:
        raise ValueError("Gate-B report binding context is incomplete")
    if sha256(gate_b_report_path) != gate_b_report_sha256:
        raise ValueError(
            "Gate-B report changed while validating physics sign-off"
        )
    try:
        gate_b_report = json.loads(gate_b_report_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            "physics sign-off Gate-B report is not valid JSON"
        ) from error
    if not isinstance(gate_b_report, dict):
        raise ValueError("physics sign-off Gate-B report is not a JSON object")
    unresolved_samples, unresolved_total = _gate_b_unresolved_evidence(
        gate_b_report
    )
    expected_binding = {
        "gate_b_report_path": gate_b_report_relative,
        "gate_b_report_sha256": gate_b_report_sha256,
        "gate_b_campaign": gate_b_report.get("campaign"),
        "gate_b_campaign_ordinal": gate_b_report.get("campaign_ordinal"),
        "reviewed_unresolved_trigger_candidates": unresolved_samples,
        "reviewed_unresolved_trigger_candidates_total": unresolved_total,
    }
    for key, value in expected_binding.items():
        if row.get(key) != value:
            raise ValueError(
                f"physics sign-off {key} differs from the authorized Gate-B "
                "report"
            )
    unresolved_total = expected_binding[
        "reviewed_unresolved_trigger_candidates_total"
    ]
    expected_treatment = (
        ZERO_UNRESOLVED_TREATMENT
        if unresolved_total == 0
        else NONZERO_UNRESOLVED_TREATMENT
    )
    if row["allowed_unresolved_treatment"] != expected_treatment:
        raise ValueError(
            "physics sign-off unresolved treatment differs from the "
            "predeclared policy"
        )


def _sealed_gate_inventory(
    report_path: Path,
    *,
    inventory_name: str,
    inventory_schema: str,
    expected_state: str,
) -> dict[str, dict]:
    """Validate the complete immutable file inventory beside a gate report."""
    evidence_root = report_path.parent
    if evidence_root.is_symlink() or not evidence_root.is_dir():
        raise ValueError("gate evidence root is not a regular directory")
    root_mode = stat.S_IMODE(evidence_root.stat().st_mode)
    if root_mode & 0o222:
        raise ValueError("gate evidence root is not sealed read-only")
    inventory_path = evidence_root / inventory_name
    if inventory_path.is_symlink() or not inventory_path.is_file():
        raise ValueError("gate evidence inventory is absent")
    inventory_stat = inventory_path.stat()
    if (
        inventory_stat.st_nlink != 1
        or stat.S_IMODE(inventory_stat.st_mode) & 0o222
    ):
        raise ValueError("gate evidence inventory is not sealed")
    try:
        inventory = json.loads(inventory_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("gate evidence inventory is not valid JSON") from error
    if (
        not isinstance(inventory, dict)
        or inventory.get("schema") != inventory_schema
        or (
            "state" in inventory
            and inventory.get("state") != expected_state
        )
    ):
        raise ValueError("gate evidence inventory metadata differs")
    rows = inventory.get("files")
    if not isinstance(rows, list) or not rows:
        raise ValueError("gate evidence inventory has no files")
    indexed: dict[str, dict] = {}
    for row in rows:
        relative_text = row.get("path") if isinstance(row, dict) else None
        relative = Path(relative_text) if isinstance(relative_text, str) else Path()
        if (
            not isinstance(row, dict)
            or not relative_text
            or relative.is_absolute()
            or ".." in relative.parts
            or relative_text in indexed
            or isinstance(row.get("bytes"), bool)
            or not isinstance(row.get("bytes"), int)
            or row["bytes"] < 0
            or not SHA256.fullmatch(str(row.get("sha256", "")))
        ):
            raise ValueError("gate evidence inventory row is malformed")
        path = evidence_root / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(
                f"gate evidence inventory file is absent: {relative_text}"
            )
        metadata = path.stat()
        if (
            metadata.st_nlink != 1
            or stat.S_IMODE(metadata.st_mode) & 0o222
            or metadata.st_size != row["bytes"]
            or sha256(path) != row["sha256"]
        ):
            raise ValueError(
                f"gate evidence inventory binding differs: {relative_text}"
            )
        indexed[relative_text] = row
    discovered = {
        path.relative_to(evidence_root).as_posix()
        for path in evidence_root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    expected = set(indexed) | {inventory_name}
    if discovered != expected:
        raise ValueError(
            "gate evidence inventory file set differs: "
            f"missing={sorted(expected - discovered)} "
            f"extra={sorted(discovered - expected)}"
        )
    report_relative = report_path.relative_to(evidence_root).as_posix()
    if report_relative not in indexed:
        raise ValueError("gate report is absent from its evidence inventory")
    return indexed


def _literal_assignment(source: Path, name: str):
    try:
        tree = ast.parse(source.read_text(), filename=str(source))
    except (OSError, SyntaxError) as error:
        raise ValueError(f"cannot parse gate implementation {source}") from error
    for statement in tree.body:
        if (
            isinstance(statement, (ast.Assign, ast.AnnAssign))
            and (
                (
                    isinstance(statement, ast.Assign)
                    and any(
                        isinstance(target, ast.Name) and target.id == name
                        for target in statement.targets
                    )
                )
                or (
                    isinstance(statement, ast.AnnAssign)
                    and isinstance(statement.target, ast.Name)
                    and statement.target.id == name
                )
            )
        ):
            try:
                return ast.literal_eval(statement.value)
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"gate implementation {name} is not literal"
                ) from error
    raise ValueError(f"gate implementation has no {name} assignment")


def _gate_a_expected_command_names(
    checkout_root: Path, repository_commit: str
) -> set[str]:
    gate_script = checkout_root / "tools/run_publication_gate_a.py"
    active_macros = _literal_assignment(gate_script, "ACTIVE_ROOT_MACROS")
    root_tests = _literal_assignment(gate_script, "ROOT_TESTS")
    tree_paths = subprocess.check_output(
        [
            "git",
            "-C",
            str(checkout_root),
            "ls-tree",
            "-r",
            "--name-only",
            repository_commit,
            "--",
            "tests",
            "REPOSITORY_FILE_CATALOG.md",
        ],
        text=True,
    ).splitlines()
    python_tests = {
        Path(path).name
        for path in tree_paths
        if re.fullmatch(r"tests/test_[^/]+\.py", path)
    }
    names = {
        *{f"version:{name}" for name in ("python3", "git", "root", "root-config", "g++", "jq")},
        "git-diff-check",
        "origin-fetch",
        "origin-reachability",
        "branch-diff-check",
        "registry-generation-check",
        "tune-card-allowlist-check",
        "json-syntax",
        "shell-syntax",
        "python-bytecode",
        "producer-build",
        "heavy-flavour-utils-build",
        "heavy-flavour-utils-test",
        *{f"python-test:{name}" for name in python_tests},
        *{f"aclic:{path}" for path in active_macros},
        *{f"root-test:{row[0]}" for row in root_tests},
        "species-registry-pythia-audit",
        "species-registry-official-pdg-audit",
    }
    if "REPOSITORY_FILE_CATALOG.md" in tree_paths:
        names.add("repository-file-catalog-check")
    return names


def _is_named_executable(token: object, name: str) -> bool:
    return (
        isinstance(token, str)
        and bool(token)
        and Path(token).name == name
    )


def _is_python_executable(token: object) -> bool:
    return (
        isinstance(token, str)
        and bool(re.fullmatch(r"python(?:3(?:\.[0-9]+)?)?", Path(token).name))
    )


def _gate_a_tracked_paths(
    checkout_root: Path, repository_commit: str, pattern: str
) -> list[str]:
    return [
        path
        for path in subprocess.check_output(
            [
                "git",
                "-C",
                str(checkout_root),
                "ls-tree",
                "-r",
                "--name-only",
                repository_commit,
                "--",
            ],
            text=True,
        ).splitlines()
        if Path(path).match(pattern)
    ]


def _validate_gate_a_command_semantics(
    *,
    command: dict,
    checkout_root: Path,
    repository_commit: str,
    evidence_root: Path,
    aggregate_log: str,
) -> None:
    """Validate the canonical Gate-A argv, not merely its display name."""
    name = command["name"]
    argv = command.get("command")
    if not isinstance(argv, list) or not argv or not all(
        isinstance(token, str) and token for token in argv
    ):
        raise ValueError(f"Gate-A command {name} argv is incomplete")
    start_marker = f"GATE_A_COMMAND_START name={name}"
    command_marker = "command=" + shlex.join(argv)
    end_marker = (
        f"GATE_A_COMMAND_END name={name} returncode=0 "
        "compiler_warning_found=false"
    )
    log_lines = aggregate_log.splitlines()
    if (
        log_lines.count(start_marker) != 1
        or log_lines.count(command_marker) != 1
        or log_lines.count(end_marker) != 1
    ):
        raise ValueError(
            f"Gate-A command {name} is not bound to its aggregate execution log"
        )

    exact: list[str] | None = None
    executable_name: str | None = None
    if name.startswith("version:"):
        executable_name = name.split(":", 1)[1]
        exact = [argv[0], "--version"]
    elif name == "git-diff-check":
        executable_name, exact = "git", ["git", "diff", "--check"]
    elif name == "origin-fetch":
        executable_name, exact = "git", [
            "git", "fetch", "--prune", "origin"
        ]
    elif name == "origin-reachability":
        executable_name, exact = "git", [
            "git", "branch", "-r", "--contains", repository_commit
        ]
    elif name == "branch-diff-check":
        executable_name, exact = "git", [
            "git", "diff", "--check", "origin/main...HEAD"
        ]
    elif name == "registry-generation-check":
        if not _is_python_executable(argv[0]):
            raise ValueError("Gate-A registry generator is not Python")
        exact = [
            argv[0],
            "tools/generate_registry_artifacts.py",
            "--check",
        ]
    elif name == "tune-card-allowlist-check":
        if not _is_python_executable(argv[0]):
            raise ValueError("Gate-A tune-card validator is not Python")
        exact = [
            argv[0],
            "tools/validate_tune_cards.py",
            "--root",
            str(checkout_root),
        ]
    elif name == "json-syntax":
        executable_name = "jq"
        expected = set(_gate_a_tracked_paths(
            checkout_root, repository_commit, "*.json"
        ))
        if argv[:2] != ["jq", "empty"] or set(argv[2:]) != expected:
            raise ValueError("Gate-A JSON syntax command differs")
    elif name == "shell-syntax":
        executable_name = "bash"
        expected = set(_gate_a_tracked_paths(
            checkout_root, repository_commit, "*.sh"
        ))
        if argv[:2] != ["bash", "-n"] or set(argv[2:]) != expected:
            raise ValueError("Gate-A shell syntax command differs")
    elif name == "python-bytecode":
        if not _is_python_executable(argv[0]):
            raise ValueError("Gate-A bytecode command is not Python")
        expected = set(_gate_a_tracked_paths(
            checkout_root, repository_commit, "*.py"
        ))
        if argv[1:3] != ["-m", "py_compile"] or set(argv[3:]) != expected:
            raise ValueError("Gate-A Python bytecode command differs")
    elif name == "producer-build":
        executable_name = "make"
        if (
            argv[:4] != ["make", "-B", "-C", "SimulationScripts"]
            or argv[-1] != "heavyflavourcorrelations_status"
            or len(argv) != 6
            or not argv[4].startswith("PRODUCER_OUTPUT=")
        ):
            raise ValueError("Gate-A producer-build argv differs")
        output = Path(argv[4].split("=", 1)[1])
        try:
            output.relative_to(evidence_root / "build")
        except ValueError as error:
            raise ValueError(
                "Gate-A producer build output is outside evidence"
            ) from error
    elif name == "heavy-flavour-utils-build":
        executable_name = "g++"
        required = [
            "g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic",
            "-Wconversion", "-Wshadow", "-Werror", "-I",
            "SimulationScripts", "tests/test_heavy_flavour_utils.cpp", "-o",
        ]
        if argv[:len(required)] != required or len(argv) != len(required) + 1:
            raise ValueError("Gate-A heavy-flavour utility build argv differs")
        try:
            Path(argv[-1]).relative_to(evidence_root / "build")
        except ValueError as error:
            raise ValueError(
                "Gate-A utility test binary is outside evidence"
            ) from error
    elif name == "heavy-flavour-utils-test":
        if len(argv) != 1 or Path(argv[0]).name != "test_heavy_flavour_utils":
            raise ValueError("Gate-A utility test argv differs")
        try:
            Path(argv[0]).relative_to(evidence_root / "build")
        except ValueError as error:
            raise ValueError("Gate-A utility test is outside evidence") from error
    elif name.startswith("python-test:"):
        test_name = name.split(":", 1)[1]
        if (
            len(argv) != 2
            or not _is_python_executable(argv[0])
            or Path(argv[1]).resolve() != checkout_root / "tests" / test_name
        ):
            raise ValueError(f"Gate-A Python test argv differs: {test_name}")
    elif name.startswith(("aclic:", "root-test:")):
        macro = name.split(":", 1)[1]
        if (
            len(argv) != 6
            or argv[:5] != ["root", "-l", "-b", "-q", "-e"]
            or str(checkout_root / macro) not in argv[5]
            or "gROOT->LoadMacro" not in argv[5]
            or "gSystem->SetBuildDir" not in argv[5]
        ):
            raise ValueError(f"Gate-A ROOT command argv differs: {name}")
        executable_name = "root"
    elif name == "species-registry-pythia-audit":
        if (
            len(argv) != 6
            or argv[:5] != ["root", "-l", "-b", "-q", "-e"]
            or str(
                checkout_root / "Validation/AuditSpeciesRegistry.C"
            ) not in argv[5]
            or "AuditSpeciesRegistry" not in argv[5]
        ):
            raise ValueError("Gate-A PYTHIA species-audit argv differs")
        executable_name = "root"
    elif name == "species-registry-official-pdg-audit":
        if (
            len(argv) != 8
            or not _is_python_executable(argv[0])
            or argv[1:3] != ["tools/pdg_2025_species_audit.py", "check"]
            or argv[3] != "--pythia-csv"
            or argv[5] != "--require-pythia"
            or argv[6] != "--output"
        ):
            raise ValueError("Gate-A official-PDG audit argv differs")
        for path_text in (argv[4], argv[7]):
            try:
                Path(path_text).relative_to(evidence_root)
            except ValueError as error:
                raise ValueError(
                    "Gate-A official-PDG evidence path is outside evidence"
                ) from error
    elif name == "repository-file-catalog-check":
        if not _is_python_executable(argv[0]):
            raise ValueError("Gate-A catalog command is not Python")
        exact = [
            argv[0],
            "tools/generate_file_catalog.py",
            "--root",
            str(checkout_root),
            "--check",
        ]
    else:
        raise ValueError(f"Gate-A command has no semantic contract: {name}")

    if executable_name is not None and not _is_named_executable(
        argv[0], executable_name
    ):
        raise ValueError(
            f"Gate-A command {name} executable is not {executable_name}"
        )
    if exact is not None and argv != exact:
        raise ValueError(f"Gate-A command {name} argv differs")


def _validate_gate_b_command_semantics(command: dict) -> None:
    purpose = command["purpose"]
    argv = command.get("argv")
    if not isinstance(argv, list) or not argv or not all(
        isinstance(token, str) and token for token in argv
    ):
        raise ValueError(f"Gate-B command {purpose} argv is incomplete")
    if purpose == "canonical_gate_b_campaign_validation":
        if (
            len(argv) != 8
            or not _is_python_executable(argv[0])
            or Path(argv[1]).name != "campaign_manifest.py"
            or argv[2] != "validate"
            or argv[4:6] != ["--implementation-policy", "exact"]
            or argv[6] != "--checkout-root"
        ):
            raise ValueError("Gate-B campaign validation argv differs")
    elif purpose == "fresh_raw_to_frozen_pthat_decision_recheck":
        if (
            not _is_python_executable(argv[0])
            or "pthat" not in " ".join(argv[1:]).lower()
        ):
            raise ValueError("Gate-B pTHat recheck argv differs")
    elif purpose == "raw_resource_stability_compression_audit":
        if (
            len(argv) != 5
            or argv[:4] != ["root", "-l", "-b", "-q"]
            or Path(argv[4]).name != "gate_b_resource_audit.C"
        ):
            raise ValueError("Gate-B resource audit argv differs")
    elif (
        purpose == "cross_tune_effective_settings_audit"
        or purpose.startswith("origin_resolution_audit_")
        or purpose.startswith("unresolved_origin_listing_")
    ):
        if argv != ["root", "-l", "-b"]:
            raise ValueError(f"Gate-B ROOT audit argv differs: {purpose}")
        if (
            not isinstance(command.get("stdin_path"), str)
            or not SHA256.fullmatch(str(command.get("stdin_sha256", "")))
        ):
            raise ValueError(f"Gate-B ROOT audit stdin binding is absent: {purpose}")
    elif purpose == "gate_b_needs_signoff_evidence_revalidation":
        if (
            not _is_python_executable(argv[0])
            or Path(argv[1]).name != "run_publication_gate_b.py"
        ):
            raise ValueError("Gate-B supersession revalidation argv differs")
    else:
        raise ValueError(f"Gate-B command has no semantic contract: {purpose}")


def _validate_gate_d_command_semantics(
    commands: list[dict], checkout_root: Path, report_path: Path
) -> None:
    expected_names = {
        *{
            f"pair_contract_{tune}_{label}"
            for tune in TUNES
            for label in ("central", *(
                f"block_{index:02d}" for index in range(1, 11)
            ))
        },
        "gate_d_analysis_audit",
    }
    observed_names = {
        row.get("name") for row in commands if isinstance(row, dict)
    }
    if len(commands) != len(expected_names) or observed_names != expected_names:
        raise ValueError(
            "Gate-D command inventory differs from the canonical 33-directory "
            "validation plus analysis audit"
        )
    _validate_gate_command_logs(report_path, commands, name_key="name")
    for command in commands:
        argv = command.get("command")
        name = command["name"]
        if (
            Path(str(command.get("cwd", ""))).resolve() != checkout_root
            or not isinstance(argv, list)
            or not argv
        ):
            raise ValueError(f"Gate-D command {name} execution context differs")
        _require_utc_timestamp(
            command.get("started_utc"), f"Gate-D command {name} start"
        )
        _require_utc_timestamp(
            command.get("finished_utc"), f"Gate-D command {name} finish"
        )
        log = report_path.parent / command["log_path"]
        text = log.read_text(errors="replace")
        if name == "gate_d_analysis_audit":
            if (
                argv != ["root", "-l", "-b"]
                or "GATE_D_ANALYSIS_SUMMARY errors=0" not in text
                or "GATE_D_ANALYSIS_ERROR" in text
            ):
                raise ValueError("Gate-D analysis-audit command differs")
            continue
        match = re.fullmatch(
            r"pair_contract_(MONASH|JUNCTIONS|CLOSEPACKING)_"
            r"(central|block_(?:0[1-9]|10))",
            name,
        )
        if match is None:
            raise ValueError(f"Gate-D pair command name is invalid: {name}")
        tune, label = match.groups()
        if (
            len(argv) != 2
            or Path(argv[0]).resolve()
            != checkout_root / "Validation/validate_pair_directory.sh"
            or tune not in argv[1]
            or (
                label == "central"
                and "complete_root_GATE_D_" not in argv[1]
            )
            or (
                label.startswith("block_")
                and f"combined_root_{int(label[-2:])}" not in argv[1]
            )
            or "PAIR_DIRECTORY_SUMMARY errors=0" not in text
        ):
            raise ValueError(f"Gate-D pair validation argv/log differs: {name}")


def _gate_c_expected_specs(checkout_root: Path) -> dict[str, dict]:
    source = checkout_root / "tools/run_publication_gate_c.py"
    try:
        tree = ast.parse(source.read_text(), filename=str(source))
    except (OSError, SyntaxError) as error:
        raise ValueError("cannot parse Gate-C implementation") from error
    assignment = next(
        (
            statement
            for statement in tree.body
            if isinstance(statement, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "COMMAND_SPECS"
                for target in statement.targets
            )
        ),
        None,
    )
    if assignment is None or not isinstance(assignment.value, ast.Tuple):
        raise ValueError("Gate-C COMMAND_SPECS is not a literal tuple")

    def sequence(node: ast.AST) -> list[str]:
        if not isinstance(node, (ast.Tuple, ast.List)):
            raise ValueError("Gate-C command sequence is not literal")
        values: list[str] = []
        for element in node.elts:
            if isinstance(element, ast.Constant) and isinstance(
                element.value, str
            ):
                values.append(element.value)
            elif (
                isinstance(element, ast.Attribute)
                and isinstance(element.value, ast.Name)
                and element.value.id == "sys"
                and element.attr == "executable"
            ):
                values.append("<PYTHON_EXECUTABLE>")
            else:
                raise ValueError("Gate-C command sequence is not canonical")
        return values

    result: dict[str, dict] = {}
    for element in assignment.value.elts:
        if (
            not isinstance(element, ast.Call)
            or not isinstance(element.func, ast.Name)
            or element.func.id != "CommandSpec"
            or len(element.args) < 3
        ):
            raise ValueError("Gate-C command specification is not canonical")
        name = ast.literal_eval(element.args[0])
        arguments = sequence(element.args[1])
        inputs = sequence(element.args[2])
        markers = (
            sequence(element.args[3])
            if len(element.args) > 3
            else []
        )
        if name in result:
            raise ValueError("Gate-C command specification is duplicated")
        result[name] = {
            "command": list(arguments),
            "inputs": tuple(inputs),
            "markers": list(markers),
        }
    if set(result) != GATE_C_COMMAND_NAMES:
        raise ValueError("Gate-C implementation command inventory differs")
    return result


def _validate_gate_command_logs(
    report_path: Path, commands: list[dict], *, name_key: str
) -> None:
    for command in commands:
        if (
            not isinstance(command, dict)
            or command.get("returncode") != 0
            or command.get("compiler_warning_found") is not False
        ):
            raise ValueError("gate report has failed command evidence")
        command_name = command.get(name_key)
        if not isinstance(command_name, str) or not command_name:
            raise ValueError("gate report command identity is absent")
        log_relative = command.get("log_path")
        log_sha = command.get("log_sha256")
        if log_relative is None and name_key == "name":
            # Gate A records all output in its authenticated aggregate log.
            continue
        if (
            not isinstance(log_relative, str)
            or not SHA256.fullmatch(str(log_sha or ""))
        ):
            raise ValueError(
                f"gate command {command_name} log binding is absent"
            )
        relative = Path(log_relative)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"gate command {command_name} log path is unsafe")
        log_path = report_path.parent / relative
        if (
            log_path.is_symlink()
            or not log_path.is_file()
            or sha256(log_path) != log_sha
        ):
            raise ValueError(
                f"gate command {command_name} log binding differs"
            )


def validate_gate_report_semantics(
    name: str,
    report_path: Path,
    checkout_root: Path,
    config: dict,
    *,
    allow_pthat_unresolved_review: bool = False,
) -> dict:
    """Require the checksummed gate artifact to be a real canonical PASS.

    A checksum proves only that bytes did not change.  It does not prove that
    those bytes are a gate report, that the gate passed, or that it tested the
    production implementation.  Full-production authorization therefore
    validates both the immutable byte identity and this minimal semantic
    contract.
    """
    checkout_root = checkout_root.resolve()
    report_path = report_path.resolve()
    try:
        report = json.loads(report_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            f"gate authorization report {name} is not valid JSON"
        ) from error
    if not isinstance(report, dict):
        raise ValueError(
            f"gate authorization report {name} is not a JSON object"
        )

    schema_by_name = {
        "gate_a": "hf_publication_gate_a_report_v1",
        "gate_b": "hf_publication_gate_b_report_v1",
        "pthat_sensitivity": "hf_gate_b_pthat_sensitivity_report_v1",
        "gate_c": "hf_publication_gate_c_report_v1",
        "gate_d": "hf_publication_gate_d_report_v1",
    }
    if report.get("schema") != schema_by_name[name]:
        raise ValueError(
            f"gate authorization report {name} schema differs"
        )

    if name == "pthat_sensitivity":
        outcome = report.get("outcome")
        allowed_outcomes = {"PASS"}
        if allow_pthat_unresolved_review:
            allowed_outcomes.add("SCIENTIFIC_REVIEW_REQUIRED")
        if outcome not in allowed_outcomes:
            raise ValueError(
                "pTHat sensitivity report did not reach an authorized "
                "outcome"
            )
        for key in ("technical_failures", "inconclusive_findings"):
            if report.get(key) != []:
                raise ValueError(
                    f"pTHat sensitivity report retains {key}"
                )
        scientific_findings = report.get("scientific_review_findings")
        if outcome == "PASS" and scientific_findings != []:
            raise ValueError(
                "pTHat sensitivity PASS retains scientific-review findings"
            )
        if (
            outcome == "SCIENTIFIC_REVIEW_REQUIRED"
            and (
                not isinstance(scientific_findings, list)
                or not scientific_findings
            )
        ):
            raise ValueError(
                "pTHat sensitivity review outcome has no review findings"
            )
        comparisons = report.get("comparisons")
        if (
            not isinstance(comparisons, list)
            or len(comparisons) != 192
        ):
            raise ValueError(
                "pTHat sensitivity report does not contain the exact 192 "
                "predeclared comparisons"
            )
        comparison_identities: set[tuple[object, ...]] = set()
        for comparison in comparisons:
            if (
                not isinstance(comparison, dict)
                or comparison.get("status")
                != "EQUIVALENT_NO_RESOLVED_SHIFT"
                or comparison.get("family_comparisons") != 192
            ):
                raise ValueError(
                    "pTHat sensitivity comparison is not an equivalent "
                    "member of the frozen 192-comparison family"
                )
            identity = (
                comparison.get("tune"),
                comparison.get("alternate_threshold"),
                comparison.get("reference_threshold"),
                comparison.get("observable"),
            )
            if (
                identity in comparison_identities
                or identity[0] not in TUNES
                or identity[1] not in {"0.5", "2.0"}
                or identity[2] != "1.0"
                or not isinstance(identity[3], str)
                or not identity[3]
            ):
                raise ValueError(
                    "pTHat sensitivity comparison identity is invalid or "
                    "duplicated"
                )
            comparison_identities.add(identity)
        diagnostics = report.get("diagnostics")
        expected_diagnostics = {
            (tune, threshold)
            for tune in TUNES
            for threshold in ("0.5", "1.0", "2.0")
        }
        diagnostic_identities: set[tuple[object, object]] = set()
        if not isinstance(diagnostics, list) or len(diagnostics) != 9:
            raise ValueError(
                "pTHat sensitivity diagnostics do not cover nine samples"
            )
        for diagnostic in diagnostics:
            identity = (
                diagnostic.get("identity", {}).get("tune"),
                diagnostic.get("identity", {}).get("pthat_min"),
            ) if isinstance(diagnostic, dict) else (None, None)
            unresolved = (
                diagnostic.get("unresolved_trigger_candidates")
                if isinstance(diagnostic, dict)
                else None
            )
            if (
                identity in diagnostic_identities
                or identity not in expected_diagnostics
                or isinstance(unresolved, bool)
                or not isinstance(unresolved, int)
                or unresolved < 0
            ):
                raise ValueError(
                    "pTHat sensitivity diagnostic identity/count is invalid"
                )
            diagnostic_identities.add(identity)
        if diagnostic_identities != expected_diagnostics:
            raise ValueError(
                "pTHat sensitivity diagnostic identities differ"
            )
        if (
            report.get("spec_sha256")
            != config.get("pthat_sensitivity_spec_sha256")
        ):
            raise ValueError(
                "pTHat sensitivity report specification checksum differs"
            )
        commit = report.get("repository_commit")
    else:
        if report.get("state") != "PASS":
            raise ValueError(
                f"gate authorization report {name} did not reach PASS"
            )
        if report.get("canonical") is not True:
            raise ValueError(
                f"gate authorization report {name} is noncanonical"
            )
        if report.get("failure") is not None:
            raise ValueError(
                f"gate authorization report {name} retains a failure"
            )
        commands = report.get("commands")
        if not isinstance(commands, list) or not commands:
            raise ValueError(
                f"gate authorization report {name} has no command evidence"
            )
        if name == "gate_a":
            environment = report.get("environment")
            aggregate_log_path = report_path.parent / str(
                report.get("log_path", "")
            )
            if (
                not isinstance(environment, dict)
                or Path(
                    str(environment.get("repository_root", ""))
                ).resolve() != checkout_root
                or environment.get("origin")
                != subprocess.check_output(
                    ["git", "-C", str(checkout_root), "remote", "get-url", "origin"],
                    text=True,
                ).strip()
                or environment.get("development_mode") != "false"
                or environment.get("initial_status") != ""
                or environment.get("initial_tracked_status") != ""
                or not isinstance(
                    environment.get("origin_refs_containing_commit"), list
                )
                or not environment["origin_refs_containing_commit"]
                or not SHA256.fullmatch(
                    str(environment.get("producer_executable_sha256", ""))
                )
                or aggregate_log_path.is_symlink()
                or not aggregate_log_path.is_file()
                or sha256(aggregate_log_path) != report.get("log_sha256")
                or report.get("publication_gate_a_pass") is not True
                or report.get("physics_review_required") is not None
            ):
                raise ValueError("Gate-A environment evidence is absent")
            commit = environment.get("repository_commit")
            current_origin_refs = {
                line.strip()
                for line in subprocess.check_output(
                    [
                        "git",
                        "-C",
                        str(checkout_root),
                        "branch",
                        "-r",
                        "--contains",
                        str(commit),
                    ],
                    text=True,
                ).splitlines()
                if line.strip().startswith("origin/") and " -> " not in line
            }
            if not current_origin_refs or not set(
                environment["origin_refs_containing_commit"]
            ).intersection(current_origin_refs):
                raise ValueError(
                    "Gate-A commit is no longer reachable from a recorded origin ref"
                )
            expected_names = _gate_a_expected_command_names(
                checkout_root, config["repository_commit"]
            )
            command_names = [
                command.get("name") if isinstance(command, dict) else None
                for command in commands
            ]
            if (
                len(command_names) != len(set(command_names))
                or set(command_names) != expected_names
            ):
                raise ValueError(
                    "Gate-A command inventory differs from the canonical suite"
                )
            _validate_gate_command_logs(
                report_path, commands, name_key="name"
            )
            aggregate_log = aggregate_log_path.read_text(errors="replace")
            for command in commands:
                if (
                    not isinstance(command.get("command"), list)
                    or not command["command"]
                    or not all(
                        isinstance(token, str) and token
                        for token in command["command"]
                    )
                    or Path(str(command.get("cwd", ""))).resolve()
                    != checkout_root
                ):
                    raise ValueError(
                        f"Gate-A command {command.get('name')} is incomplete"
                    )
                _require_utc_timestamp(
                    command.get("started_utc"), "Gate-A command start"
                )
                _require_utc_timestamp(
                    command.get("finished_utc"), "Gate-A command finish"
                )
                _validate_gate_a_command_semantics(
                    command=command,
                    checkout_root=checkout_root,
                    repository_commit=config["repository_commit"],
                    evidence_root=report_path.parent,
                    aggregate_log=aggregate_log,
                )
            _sealed_gate_inventory(
                report_path,
                inventory_name="gate_a_inventory.json",
                inventory_schema="hf_publication_gate_a_inventory_v1",
                expected_state="PASS",
            )
        elif name == "gate_b":
            commit = report.get("repository_commit")
            resolution = (
                report.get("resolution_kind")
                == "owner_physics_signoff_supersession_v1"
            )
            expected_purposes = (
                {"gate_b_needs_signoff_evidence_revalidation"}
                if resolution
                else GATE_B_COMMAND_PURPOSES
            )
            purposes = [
                command.get("purpose") if isinstance(command, dict) else None
                for command in commands
            ]
            if (
                len(purposes) != len(set(purposes))
                or set(purposes) != expected_purposes
            ):
                raise ValueError(
                    "Gate-B command inventory differs from the canonical suite"
                )
            _validate_gate_command_logs(
                report_path, commands, name_key="purpose"
            )
            for command in commands:
                _validate_gate_b_command_semantics(command)
                _require_utc_timestamp(
                    command.get("started_utc"), "Gate-B command start"
                )
                _require_utc_timestamp(
                    command.get("ended_utc"), "Gate-B command finish"
                )
                if "stdin_path" in command:
                    stdin_path = report_path.parent / str(
                        command["stdin_path"]
                    )
                    if (
                        stdin_path.is_symlink()
                        or not stdin_path.is_file()
                        or sha256(stdin_path) != command["stdin_sha256"]
                    ):
                        raise ValueError(
                            f"Gate-B command {command['purpose']} stdin differs"
                        )
            manifest = report.get("campaign_manifest")
            if not isinstance(manifest, dict):
                raise ValueError("Gate-B campaign-manifest evidence is absent")
            for path_key, hash_key in (
                ("path", "sha256"),
                ("candidate_manifest_path", "candidate_manifest_sha256"),
                ("seed_ledger_path", "seed_ledger_sha256"),
            ):
                relative_text = manifest.get(path_key)
                relative = (
                    Path(relative_text)
                    if isinstance(relative_text, str)
                    else Path()
                )
                if (
                    not relative_text
                    or relative.is_absolute()
                    or ".." in relative.parts
                    or not SHA256.fullmatch(str(manifest.get(hash_key, "")))
                ):
                    raise ValueError(
                        f"Gate-B campaign-manifest {path_key} is malformed"
                    )
                artifact = checkout_root / relative
                if (
                    artifact.is_symlink()
                    or not artifact.is_file()
                    or sha256(artifact) != manifest[hash_key]
                ):
                    raise ValueError(
                        f"Gate-B campaign-manifest {path_key} differs"
                    )
            gate_b_campaign = json.loads(
                (checkout_root / manifest["path"]).read_text()
            )
            if (
                gate_b_campaign.get("schema")
                != "hf_gate_b_pilot_campaign_v1"
                or gate_b_campaign.get("repository_commit") != commit
                or gate_b_campaign.get("campaign") != report.get("campaign")
                or gate_b_campaign.get("campaign_ordinal")
                != report.get("campaign_ordinal")
                or manifest.get("jobs") != 9
                or manifest.get("central_successes_per_tune") != 1_000_000
                or manifest.get("pthat_thresholds") != ["0.5", "1.0", "2.0"]
            ):
                raise ValueError("Gate-B campaign definition differs")
            expected_identities = {
                (tune, logical_id)
                for tune in TUNES
                for logical_id in GATE_B_PROFILES
            }
            for evidence_key in (
                "raw_validation_evidence",
                "resource_metadata_evidence",
            ):
                rows = report.get(evidence_key)
                if not isinstance(rows, list) or len(rows) != 9:
                    raise ValueError(
                        f"Gate-B {evidence_key} does not contain nine jobs"
                    )
                identities = {
                    (
                        row.get("tune"),
                        row.get("logical_id"),
                    )
                    for row in rows
                    if isinstance(row, dict)
                }
                if identities != expected_identities:
                    raise ValueError(
                        f"Gate-B {evidence_key} identities differ"
                    )
                for row in rows:
                    profile = GATE_B_PROFILES[int(row["logical_id"])]
                    event_key = (
                        "requested_successes"
                        if evidence_key == "raw_validation_evidence"
                        else "successful_events"
                    )
                    if (
                        row.get("purpose") != profile[3]
                        or row.get(event_key) != profile[1]
                    ):
                        raise ValueError(
                            f"Gate-B {evidence_key} production profile differs"
                        )
            if (
                report.get("raw_validation_count") != 9
                or not isinstance(report.get("submission_evidence"), dict)
                or not SHA256.fullmatch(
                    str(
                        report["submission_evidence"].get(
                            "producer_executable_sha256", ""
                        )
                    )
                )
            ):
                raise ValueError("Gate-B submission/raw evidence is incomplete")
            _sealed_gate_inventory(
                report_path,
                inventory_name="evidence_inventory.json",
                inventory_schema=(
                    "hf_publication_gate_b_signoff_evidence_inventory_v1"
                    if resolution
                    else "hf_publication_gate_b_evidence_inventory_v1"
                ),
                expected_state="PASS",
            )
        elif name == "gate_c":
            commit = report.get("repository_commit")
            specs = _gate_c_expected_specs(checkout_root)
            command_names = [
                command.get("name") if isinstance(command, dict) else None
                for command in commands
            ]
            if (
                len(command_names) != len(set(command_names))
                or set(command_names) != set(specs)
            ):
                raise ValueError(
                    "Gate-C command inventory differs from the canonical suite"
                )
            _validate_gate_command_logs(
                report_path, commands, name_key="name"
            )
            for command in commands:
                specification = specs[command["name"]]
                actual_command = command.get("command")
                expected_command = specification["command"]
                command_matches = (
                    isinstance(actual_command, list)
                    and len(actual_command) == len(expected_command)
                    and (
                        actual_command == expected_command
                        or (
                            expected_command
                            and expected_command[0] == "<PYTHON_EXECUTABLE>"
                            and isinstance(actual_command[0], str)
                            and Path(actual_command[0]).name.startswith("python")
                            and actual_command[1:] == expected_command[1:]
                        )
                    )
                )
                if (
                    not command_matches
                    or command.get("process_returncode") != 0
                    or command.get("required_markers")
                    != specification["markers"]
                    or command.get("missing_markers") != []
                    or set(command.get("input_sha256", {}))
                    != set(specification["inputs"])
                ):
                    raise ValueError(
                        f"Gate-C command {command['name']} evidence differs"
                    )
                for relative, digest in command["input_sha256"].items():
                    if (
                        not SHA256.fullmatch(str(digest))
                        or digest
                        != git_file_sha256(
                            checkout_root,
                            config["repository_commit"],
                            relative,
                        )
                    ):
                        raise ValueError(
                            f"Gate-C command input differs: {relative}"
                        )
            requirements = report.get("requirements")
            if not isinstance(requirements, list) or len(requirements) != 10:
                raise ValueError("Gate-C requirement inventory differs")
            numbers = {
                row.get("number")
                for row in requirements
                if isinstance(row, dict)
                and row.get("state") == "PASS"
                and row.get("missing_evidence") == []
                and isinstance(row.get("evidenced_claims"), list)
                and row["evidenced_claims"]
            }
            if numbers != set(range(1, 11)):
                raise ValueError("Gate-C requirements are not exact PASS evidence")
            environment = report.get("environment")
            if (
                not isinstance(environment, dict)
                or environment.get("canonical") is not True
                or environment.get("initial_status") != ""
                or environment.get("initial_tracked_status") != ""
                or environment.get("final_status") != ""
                or environment.get("final_tracked_status") != ""
                or environment.get("final_repository_commit") != commit
                or environment.get("repository_commit") != commit
            ):
                raise ValueError("Gate-C clean-checkout evidence differs")
            _sealed_gate_inventory(
                report_path,
                inventory_name="gate_c_inventory.json",
                inventory_schema="hf_publication_gate_c_inventory_v1",
                expected_state="PASS",
            )
        elif name == "gate_d":
            commit = report.get("repository_commit")
            _validate_gate_d_command_semantics(
                commands, checkout_root, report_path
            )
            requirements = report.get("requirements")
            if (
                not isinstance(requirements, list)
                or len(requirements) != 13
                or {
                    row.get("number")
                    for row in requirements
                    if isinstance(row, dict) and row.get("state") == "PASS"
                }
                != set(range(1, 14))
            ):
                raise ValueError("Gate-D requirements are not exact PASS evidence")
            validate_gate_d_storage_projection(report)
            _sealed_gate_inventory(
                report_path,
                inventory_name="gate_d_inventory.json",
                inventory_schema="hf_publication_gate_d_inventory_v1",
                expected_state="PASS",
            )
        else:
            raise ValueError(f"unsupported gate report {name}")

        log_relative = report.get("log_path")
        log_sha = report.get("log_sha256")
        if (
            not isinstance(log_relative, str)
            or not SHA256.fullmatch(str(log_sha or ""))
        ):
            raise ValueError(
                f"gate authorization report {name} log binding is absent"
            )
        relative_log = Path(log_relative)
        if relative_log.is_absolute() or ".." in relative_log.parts:
            raise ValueError(
                f"gate authorization report {name} log path is unsafe"
            )
        log_path = report_path.parent / relative_log
        if log_path.is_symlink() or not log_path.is_file():
            raise ValueError(
                f"gate authorization report {name} log is absent"
            )
        if sha256(log_path) != log_sha:
            raise ValueError(
                f"gate authorization report {name} log checksum differs"
            )
    if commit != config["repository_commit"]:
        raise ValueError(
            f"gate authorization report {name} repository commit differs"
        )
    return report


def validate_gate_b_pthat_resolution(
    *,
    checkout_root: Path,
    gate_b_report: dict,
    pthat_report: dict,
    pthat_report_sha256: str,
) -> None:
    """Cross-bind a pTHat decision to the exact Gate-B scientific resolution.

    A normal pTHat PASS remains the default.  The sole accepted non-PASS
    route is the immutable Gate-B owner-signoff supersession for nonzero
    unresolved trigger candidates.  It may not waive a technical failure,
    inconclusive estimator, or resolved/material pTHat shift.
    """
    pthat_evidence = gate_b_report.get("pthat_sensitivity")
    if (
        not isinstance(pthat_evidence, dict)
        or pthat_evidence.get("sha256") != pthat_report_sha256
        or pthat_evidence.get("schema")
        != "hf_gate_b_pthat_sensitivity_report_v1"
        or pthat_evidence.get("outcome") != pthat_report.get("outcome")
    ):
        raise ValueError(
            "Gate-B report does not bind the authorized pTHat decision"
        )

    unresolved_samples, unresolved_total = _gate_b_unresolved_evidence(
        gate_b_report
    )
    diagnostic_counts: dict[str, int] = {}
    for diagnostic in pthat_report["diagnostics"]:
        identity = diagnostic["identity"]
        key = f"{identity['tune']}:{identity['pthat_min']}"
        diagnostic_counts[key] = diagnostic[
            "unresolved_trigger_candidates"
        ]
    expected_counts = {
        identity: sectors["charm"] + sectors["beauty"]
        for identity, sectors in unresolved_samples.items()
    }
    if diagnostic_counts != expected_counts:
        raise ValueError(
            "pTHat and Gate-B unresolved-trigger sample counts differ"
        )
    if pthat_report.get("outcome") == "PASS":
        if unresolved_total != 0:
            raise ValueError(
                "pTHat PASS contains unresolved trigger candidates"
            )
        return
    if pthat_report.get("outcome") != "SCIENTIFIC_REVIEW_REQUIRED":
        raise ValueError("unsupported non-PASS pTHat authorization route")
    if (
        gate_b_report.get("resolution_kind")
        != "owner_physics_signoff_supersession_v1"
        or gate_b_report.get("supersedes", {}).get("state")
        != "NEEDS_SIGNOFF"
        or pthat_evidence.get("blocking_reasons") != []
    ):
        raise ValueError(
            "pTHat review outcome lacks the exact Gate-B owner-signoff "
            "supersession"
        )

    if pthat_report.get("technical_failures") != []:
        raise ValueError("owner sign-off cannot waive pTHat technical failures")
    if pthat_report.get("inconclusive_findings") != []:
        raise ValueError("owner sign-off cannot waive inconclusive pTHat evidence")
    comparisons = pthat_report.get("comparisons")
    if (
        not isinstance(comparisons, list)
        or not comparisons
        or any(
            not isinstance(row, dict)
            or row.get("status") != "EQUIVALENT_NO_RESOLVED_SHIFT"
            for row in comparisons
        )
    ):
        raise ValueError(
            "owner sign-off cannot waive a resolved or material pTHat shift"
        )

    if unresolved_total <= 0:
        raise ValueError(
            "Gate-B signoff supersession has no unresolved candidates"
        )
    expected_findings = sorted(
        f"{(identity.split(':', 1)[0], identity.split(':', 1)[1])} has "
        f"{count} unresolved publication-trigger candidates"
        for identity, count in expected_counts.items()
        if count
    )
    if pthat_report.get("scientific_review_findings") != expected_findings:
        raise ValueError(
            "pTHat scientific-review findings are not limited to the exact "
            "unresolved-trigger evidence"
        )

    signoff = gate_b_report.get("gate_b_physics_signoff")
    if (
        not isinstance(signoff, dict)
        or signoff.get("schema") != "hf_gate_b_physics_signoff_v1"
        or signoff.get("reviewer_role") != "project owner"
        or signoff.get("allowed_unresolved_treatment")
        != NONZERO_UNRESOLVED_TREATMENT
        or signoff.get("reviewed_unresolved_trigger_candidates")
        != unresolved_samples
        or signoff.get("reviewed_unresolved_trigger_candidates_total")
        != unresolved_total
    ):
        raise ValueError(
            "Gate-B owner sign-off does not bind the unresolved-trigger "
            "evidence and approved treatment"
        )
    signoff_relative = Path(str(signoff.get("path", "")))
    signoff_sha = str(signoff.get("sha256", ""))
    expected_signoff_relative = (
        Path("campaigns")
        / str(gate_b_report.get("campaign", ""))
        / "GATE_B_PHYSICS_SIGNOFF.json"
    )
    if (
        signoff_relative != expected_signoff_relative
        or signoff_relative.is_absolute()
        or ".." in signoff_relative.parts
        or not SHA256.fullmatch(signoff_sha)
    ):
        raise ValueError("Gate-B owner sign-off path or checksum is unsafe")
    signoff_path = checkout_root / signoff_relative
    if (
        signoff_path.is_symlink()
        or not signoff_path.is_file()
        or signoff_path.stat().st_mode & 0o222
        or sha256(signoff_path) != signoff_sha
    ):
        raise ValueError(
            "Gate-B owner sign-off is absent, mutable, or checksum-mismatched"
        )
    try:
        signoff_source = json.loads(signoff_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("Gate-B owner sign-off is not valid JSON") from error
    if not isinstance(signoff_source, dict):
        raise ValueError("Gate-B owner sign-off is not a JSON object")
    supersedes = gate_b_report.get("supersedes")
    expected_source_fields = {
        "schema": "hf_gate_b_physics_signoff_v1",
        "approved": True,
        "campaign": gate_b_report.get("campaign"),
        "campaign_ordinal": gate_b_report.get("campaign_ordinal"),
        "repository_commit": gate_b_report.get("repository_commit"),
        "gate_b_needs_signoff_report_sha256": (
            supersedes.get("sha256")
            if isinstance(supersedes, dict)
            else None
        ),
        "reviewed_unresolved_trigger_candidates": unresolved_samples,
        "reviewed_unresolved_trigger_candidates_total": unresolved_total,
        "allowed_unresolved_treatment": NONZERO_UNRESOLVED_TREATMENT,
        "supersedes_state": "NEEDS_SIGNOFF",
        "reviewer": signoff.get("reviewer"),
        "decision_utc": signoff.get("decision_utc"),
        "finding": signoff.get("finding"),
    }
    for key, value in expected_source_fields.items():
        if signoff_source.get(key) != value:
            raise ValueError(
                f"Gate-B owner sign-off source {key} differs from the "
                "superseding report"
            )
    if (
        not isinstance(signoff_source.get("reviewer_role"), str)
        or signoff_source["reviewer_role"].strip().lower() != "project owner"
    ):
        raise ValueError(
            "Gate-B owner sign-off source reviewer_role differs"
        )
    gate_b_decision_time = _require_utc_timestamp(
        signoff_source.get("decision_utc"), "Gate-B owner sign-off"
    )
    if (
        gate_b_decision_time
        > datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=5)
    ):
        raise ValueError(
            "Gate-B owner sign-off timestamp is implausibly in the future"
        )
    revalidated = gate_b_report.get("revalidated_original_evidence")
    if (
        not isinstance(revalidated, dict)
        or revalidated.get("pthat_decision_sha256")
        != pthat_report_sha256
    ):
        raise ValueError(
            "superseding Gate-B report did not revalidate the pTHat artifact"
        )


def _validate_gate_d_capacity_check(
    check: object,
    *,
    label: str,
    expected_total_required_bytes: int,
) -> datetime.datetime:
    if not isinstance(check, dict):
        raise ValueError(f"Gate-D {label} capacity check is absent")
    if (
        check.get("capacity_source") != "os.statvfs f_bavail"
        or check.get("state") != "PASS"
    ):
        raise ValueError(f"Gate-D {label} capacity check did not pass")
    checked = _require_utc_timestamp(
        check.get("checked_utc"), f"Gate-D {label} capacity check"
    )
    if (
        checked
        > datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=5)
    ):
        raise ValueError(f"Gate-D {label} capacity check is in the future")
    filesystems = check.get("filesystems")
    if not isinstance(filesystems, list) or not filesystems:
        raise ValueError(
            f"Gate-D {label} capacity check has no filesystem evidence"
        )
    required_sum = 0
    roles: set[str] = set()
    for index, filesystem in enumerate(filesystems):
        if not isinstance(filesystem, dict):
            raise ValueError(
                f"Gate-D {label} filesystem row {index} is malformed"
            )
        integer_fields = (
            "device_id",
            "statvfs_frsize",
            "statvfs_blocks",
            "statvfs_bavail",
            "capacity_bytes",
            "available_bytes",
            "required_additional_bytes",
            "maximum_allowed_from_current_available_bytes",
            "minimum_required_remaining_bytes",
            "projected_remaining_bytes",
        )
        values: dict[str, int] = {}
        for field in integer_fields:
            value = filesystem.get(field)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(
                    f"Gate-D {label} filesystem {field} is not an integer"
                )
            values[field] = value
        if (
            values["device_id"] < 0
            or values["statvfs_frsize"] <= 0
            or values["statvfs_blocks"] <= 0
            or values["statvfs_bavail"] < 0
            or values["statvfs_bavail"] > values["statvfs_blocks"]
            or values["capacity_bytes"]
            != values["statvfs_frsize"] * values["statvfs_blocks"]
            or values["available_bytes"]
            != values["statvfs_frsize"] * values["statvfs_bavail"]
            or values["capacity_bytes"] <= 0
            or values["available_bytes"] < 0
            or values["available_bytes"] > values["capacity_bytes"]
            or values["required_additional_bytes"] <= 0
        ):
            raise ValueError(
                f"Gate-D {label} filesystem capacity values are invalid"
            )
        expected_maximum = int(
            values["available_bytes"]
            * GATE_D_STORAGE_POLICY[
                "maximum_fraction_of_current_available"
            ]
        )
        expected_minimum_remaining = max(
            int(
                values["capacity_bytes"]
                * GATE_D_STORAGE_POLICY[
                    "minimum_projected_free_fraction"
                ]
            ),
            GATE_D_STORAGE_POLICY["minimum_projected_free_bytes"],
        )
        expected_projected = (
            values["available_bytes"]
            - values["required_additional_bytes"]
        )
        if (
            values["maximum_allowed_from_current_available_bytes"]
            != expected_maximum
            or values["minimum_required_remaining_bytes"]
            != expected_minimum_remaining
            or values["projected_remaining_bytes"] != expected_projected
            or values["required_additional_bytes"] > expected_maximum
            or expected_projected < expected_minimum_remaining
            or filesystem.get("state") != "PASS"
            or filesystem.get("failure_reasons") != []
        ):
            raise ValueError(
                f"Gate-D {label} filesystem PASS arithmetic is inconsistent"
            )
        row_roles = filesystem.get("roles")
        probe_paths = filesystem.get("probe_paths")
        if (
            not isinstance(row_roles, list)
            or any(not isinstance(role, str) for role in row_roles)
            or not isinstance(probe_paths, list)
            or not probe_paths
            or any(
                not isinstance(path, str) or not Path(path).is_absolute()
                for path in probe_paths
            )
        ):
            raise ValueError(
                f"Gate-D {label} filesystem roles/probes are malformed"
            )
        roles.update(row_roles)
        required_sum += values["required_additional_bytes"]
    if required_sum != expected_total_required_bytes:
        raise ValueError(
            f"Gate-D {label} capacity total differs from the projection"
        )
    if roles != {
        "candidate_raw_and_partials",
        "analysis_and_publication_outputs",
    }:
        raise ValueError(
            f"Gate-D {label} capacity roles do not cover raw and analysis"
        )
    return checked


def validate_gate_d_storage_projection(report: dict) -> None:
    projection = report.get("storage_projection")
    if (
        not isinstance(projection, dict)
        or projection.get("schema") != GATE_D_STORAGE_SCHEMA
        or projection.get("state") != "PASS"
        or projection.get("gate_e_storage_authorized") is not True
    ):
        raise ValueError(
            "Gate-D report lacks passing Gate-E storage authorization"
        )
    components = projection.get("projected_components")
    if (
        not isinstance(components, dict)
        or set(components) != GATE_D_STORAGE_COMPONENT_KEYS
    ):
        raise ValueError("Gate-D storage component projection is incomplete")
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in components.values()
    ):
        raise ValueError(
            "Gate-D storage component projection is not positive integer bytes"
        )
    if (
        components["simultaneous_partial_raw_bytes"]
        != components["full_100_200_200_candidate_raw_bytes"]
        or components["full_plots_logs_validation_evidence_bytes"]
        < GATE_D_STORAGE_POLICY[
            "minimum_full_plot_and_evidence_bytes"
        ]
        or components["raw_filesystem_required_additional_bytes"]
        != components["full_100_200_200_candidate_raw_bytes"]
        + components["simultaneous_partial_raw_bytes"]
        or components["analysis_filesystem_required_additional_bytes"]
        != (
            components["canonical_300_job_per_job_analysis_bytes"]
            + components["final_merged_central_bytes"]
            + components["final_ten_block_bytes"]
            + components["full_plots_logs_validation_evidence_bytes"]
        )
        or components["total_required_additional_bytes"]
        != (
            components["raw_filesystem_required_additional_bytes"]
            + components["analysis_filesystem_required_additional_bytes"]
        )
    ):
        raise ValueError("Gate-D storage component arithmetic is inconsistent")
    if projection.get("capacity_policy") != GATE_D_STORAGE_POLICY:
        raise ValueError("Gate-D storage safety policy differs")
    total = components["total_required_additional_bytes"]
    preparation_time = _validate_gate_d_capacity_check(
        projection.get("preparation_capacity_check"),
        label="preparation",
        expected_total_required_bytes=total,
    )
    final_time = _validate_gate_d_capacity_check(
        projection.get("final_capacity_recheck"),
        label="final",
        expected_total_required_bytes=total,
    )
    if final_time < preparation_time:
        raise ValueError("Gate-D final capacity recheck predates preparation")


def retained_partial_bytes(campaign_root: Path) -> int:
    """Count every retained partial/quarantine byte in the campaign."""
    total = 0
    for directory_name in ("partial", "quarantine"):
        directory = campaign_root / directory_name
        if not directory.exists():
            continue
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(
                f"campaign retained-output path is unsafe: {directory}"
            )
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise ValueError(
                    f"campaign retained-output tree contains a symlink: {path}"
                )
            if path.is_file():
                metadata = path.stat()
                if metadata.st_nlink != 1:
                    raise ValueError(
                        f"retained output is hard-linked: {path}"
                    )
                total += metadata.st_size
    return total


def live_recheck_gate_d_storage(
    report: dict, campaign_root: Path
) -> dict:
    """Reprobe every Gate-D filesystem and re-evaluate the frozen policy."""
    validate_gate_d_storage_projection(report)
    projection = report["storage_projection"]
    final_check = projection["final_capacity_recheck"]
    checked = _require_utc_timestamp(
        final_check.get("checked_utc"), "Gate-D final capacity check"
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for stored in final_check["filesystems"]:
        snapshots = []
        for path_text in stored["probe_paths"]:
            path = Path(path_text)
            require_existing_directory_chain_no_symlinks(path)
            metadata = path.stat()
            values = os.statvfs(path)
            fragment = int(values.f_frsize or values.f_bsize)
            snapshots.append(
                {
                    "path": str(path),
                    "device_id": int(metadata.st_dev),
                    "statvfs_frsize": fragment,
                    "statvfs_blocks": int(values.f_blocks),
                    "statvfs_bavail": int(values.f_bavail),
                    "capacity_bytes": int(values.f_blocks * fragment),
                    "available_bytes": int(values.f_bavail * fragment),
                }
            )
        if (
            any(row["device_id"] != stored["device_id"] for row in snapshots)
            or any(
                row["statvfs_frsize"] != stored["statvfs_frsize"]
                or row["statvfs_blocks"] != stored["statvfs_blocks"]
                for row in snapshots
            )
        ):
            raise ValueError(
                "Gate-D storage filesystem identity/geometry changed"
            )
        capacity = snapshots[0]["capacity_bytes"]
        available = min(row["available_bytes"] for row in snapshots)
        required = int(stored["required_additional_bytes"])
        maximum = int(
            available
            * GATE_D_STORAGE_POLICY[
                "maximum_fraction_of_current_available"
            ]
        )
        minimum_remaining = max(
            int(
                capacity
                * GATE_D_STORAGE_POLICY[
                    "minimum_projected_free_fraction"
                ]
            ),
            GATE_D_STORAGE_POLICY["minimum_projected_free_bytes"],
        )
        projected = available - required
        if required > maximum or projected < minimum_remaining:
            raise ValueError(
                "live Gate-D storage headroom no longer satisfies policy"
            )
        rows.append(
            {
                "device_id": stored["device_id"],
                "probe_paths": stored["probe_paths"],
                "roles": stored["roles"],
                "statvfs_frsize": snapshots[0]["statvfs_frsize"],
                "statvfs_blocks": snapshots[0]["statvfs_blocks"],
                "statvfs_bavail": min(
                    row["statvfs_bavail"] for row in snapshots
                ),
                "capacity_bytes": capacity,
                "available_bytes": available,
                "required_additional_bytes": required,
                "maximum_allowed_from_current_available_bytes": maximum,
                "minimum_required_remaining_bytes": minimum_remaining,
                "projected_remaining_bytes": projected,
                "state": "PASS",
                "failure_reasons": [],
            }
        )
    retained = retained_partial_bytes(campaign_root)
    retained_budget = projection["projected_components"][
        "simultaneous_partial_raw_bytes"
    ]
    if retained > retained_budget:
        raise ValueError(
            "retained partial/quarantine bytes exceed the Gate-D partial budget"
        )
    return {
        "schema": "hf_live_storage_recheck_v1",
        "state": "PASS",
        "checked_utc": now.isoformat(timespec="seconds"),
        "source_final_check_utc": checked.isoformat(timespec="seconds"),
        "source_storage_projection_sha256": hashlib.sha256(
            json.dumps(
                projection, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest(),
        "retained_partial_and_quarantine_bytes": retained,
        "retained_partial_budget_bytes": retained_budget,
        "filesystems": rows,
    }


def recheck_storage_from_claim(
    claim: dict, checkout_root: Path, *, require_recent_claim: bool = True
) -> dict:
    """Require a recent claim-time check and perform a new live storage probe."""
    prior = claim.get("live_storage_recheck")
    relative_text = claim.get("gate_d_report_path")
    relative = Path(relative_text) if isinstance(relative_text, str) else Path()
    expected_sha = claim.get("gate_d_report_sha256")
    if (
        not isinstance(prior, dict)
        or prior.get("schema") != "hf_live_storage_recheck_v1"
        or prior.get("state") != "PASS"
        or not relative_text
        or relative.is_absolute()
        or ".." in relative.parts
        or not SHA256.fullmatch(str(expected_sha or ""))
    ):
        raise ValueError("submission claim lacks canonical live storage evidence")
    prior_time = _require_utc_timestamp(
        prior.get("checked_utc"), "submission claim live-storage check"
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    if require_recent_claim and (
        prior_time > now + datetime.timedelta(minutes=5)
        or now - prior_time > GATE_D_STORAGE_MAX_RECHECK_AGE
    ):
        raise ValueError("submission claim live-storage check is stale")
    report_path = checkout_root / relative
    if (
        report_path.is_symlink()
        or not report_path.is_file()
        or sha256(report_path) != expected_sha
    ):
        raise ValueError("submission claim Gate-D report changed")
    report = json.loads(report_path.read_text())
    campaign_root = (
        checkout_root / "Production" / str(claim.get("campaign", ""))
    )
    return live_recheck_gate_d_storage(report, campaign_root)


def validate_gate_authorization(
    path: Path, checkout_root: Path, config: dict, physics_signoff: Path
) -> dict[str, dict]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(
            "full-production gate authorization is not a regular file"
        )
    authorization_stat = path.stat()
    if (
        stat.S_IMODE(authorization_stat.st_mode) != 0o444
        or authorization_stat.st_nlink != 1
    ):
        raise ValueError(
            "full-production gate authorization is not sealed as a "
            "single-link 0444 file"
        )
    authorization = json.loads(path.read_text())
    if not isinstance(authorization, dict):
        raise ValueError(
            "full-production gate authorization is not a JSON object"
        )
    expected = {
        "schema": "hf_full_production_gate_authorization_v1",
        "approved": True,
        "campaign": config["campaign"],
        "campaign_ordinal": config["campaign_ordinal"],
        "repository_commit": config["repository_commit"],
        "physics_origin_signoff_sha256": sha256(physics_signoff),
    }
    for key, value in expected.items():
        if authorization.get(key) != value:
            raise ValueError(f"full-production gate authorization {key} differs")
    owner = authorization.get("project_owner")
    if (
        not isinstance(owner, str)
        or not owner.strip()
        or "PROJECT OWNER" in owner.upper()
        or "UNIT TEST" in owner.upper()
    ):
        raise ValueError("full-production owner approval is absent or placeholder")
    timestamp = _require_utc_timestamp(
        authorization.get("approved_utc"),
        "full-production owner approval",
    )
    if (
        timestamp
        > datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=5)
    ):
        raise ValueError(
            "full-production owner approval timestamp is implausibly in the "
            "future"
        )
    reports = authorization.get("reports")
    required_reports = {
        "gate_a",
        "gate_b",
        "pthat_sensitivity",
        "gate_c",
        "gate_d",
    }
    if not isinstance(reports, dict) or set(reports) != required_reports:
        raise ValueError(
            "full-production authorization must bind exact Gates A-D and "
            "pTHat reports"
        )
    report_paths: dict[str, Path] = {}
    loaded_reports: dict[str, dict] = {}
    for name in sorted(required_reports):
        report = reports[name]
        if (
            not isinstance(report, dict)
            or not isinstance(report.get("path"), str)
            or not SHA256.fullmatch(str(report.get("sha256", "")))
        ):
            raise ValueError(f"gate authorization report {name} is malformed")
        relative = Path(report["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"gate authorization report {name} path is unsafe")
        report_path = checkout_root / relative
        if report_path.is_symlink() or not report_path.is_file():
            raise ValueError(f"gate authorization report {name} is absent")
        if sha256(report_path) != report["sha256"]:
            raise ValueError(f"gate authorization report {name} checksum differs")
        report_paths[name] = report_path
        if name != "pthat_sensitivity":
            loaded_reports[name] = validate_gate_report_semantics(
                name, report_path, checkout_root, config
            )

    gate_b_report = loaded_reports["gate_b"]
    allow_pthat_unresolved_review = (
        gate_b_report.get("resolution_kind")
        == "owner_physics_signoff_supersession_v1"
    )
    loaded_reports["pthat_sensitivity"] = validate_gate_report_semantics(
        "pthat_sensitivity",
        report_paths["pthat_sensitivity"],
        checkout_root,
        config,
        allow_pthat_unresolved_review=allow_pthat_unresolved_review,
    )
    validate_gate_b_pthat_resolution(
        checkout_root=checkout_root,
        gate_b_report=gate_b_report,
        pthat_report=loaded_reports["pthat_sensitivity"],
        pthat_report_sha256=reports["pthat_sensitivity"]["sha256"],
    )
    validate_physics_signoff(
        physics_signoff,
        config,
        gate_b_report_path=report_paths["gate_b"],
        gate_b_report_relative=reports["gate_b"]["path"],
        gate_b_report_sha256=reports["gate_b"]["sha256"],
    )
    return loaded_reports


def _require_exact_object_keys(
    value: object, expected: set[str], label: str
) -> dict:
    if not isinstance(value, dict) or set(value) != expected:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        raise ValueError(
            f"{label} fields differ: expected={sorted(expected)} actual={actual}"
        )
    return value


def _require_nonnegative_number(value: object, label: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) < 0.0
    ):
        raise ValueError(f"{label} is not a finite nonnegative number")
    return float(value)


def _require_nonnegative_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} is not a nonnegative integer")
    return value


def _sealed_expansion_json(path: Path, label: str) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} is absent or a symbolic link")
    metadata = path.stat()
    if metadata.st_nlink != 1 or stat.S_IMODE(metadata.st_mode) != 0o444:
        raise ValueError(f"{label} is not single-link mode 0444")
    try:
        payload = json.loads(path.read_text())
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not valid JSON") from error
    if not isinstance(payload, dict):
        raise ValueError(f"{label} is not a JSON object")
    return payload


def _expansion_parent_evidence(
    checkout_root: Path, config: dict
) -> tuple[Path, dict, list[dict], str]:
    parent = config.get("supersedes")
    if not isinstance(parent, dict):
        raise ValueError("equal-tune expansion parent binding is absent")
    relative_text = parent.get("freeze_path")
    relative = (
        Path(relative_text) if isinstance(relative_text, str) else Path()
    )
    if (
        not relative_text
        or relative.is_absolute()
        or ".." in relative.parts
    ):
        raise ValueError("equal-tune expansion parent path is unsafe")
    parent_freeze = checkout_root / relative
    if (
        parent_freeze.is_symlink()
        or not parent_freeze.is_dir()
        or parent_freeze.name != "freeze"
    ):
        raise ValueError("equal-tune expansion sealed parent is absent")
    require_existing_directory_chain_no_symlinks(parent_freeze)
    canonical_path = checkout_root / "tools/canonical_manifest.py"
    if canonical_path.is_symlink() or not canonical_path.is_file():
        raise ValueError("checkout lacks the canonical parent contract")
    if sha256(canonical_path) != git_file_sha256(
        checkout_root,
        config["repository_commit"],
        "tools/canonical_manifest.py",
    ):
        raise ValueError(
            "canonical parent contract differs from expansion campaign commit"
        )
    specification = importlib.util.spec_from_file_location(
        "expansion_authorization_parent_contract",
        canonical_path,
    )
    if specification is None or specification.loader is None:
        raise ValueError("cannot load canonical parent contract")
    canonical_contract = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(canonical_contract)
    with contextlib.redirect_stdout(io.StringIO()):
        canonical_contract.validate_directory(
            parent_freeze, require_seal=True
        )
    summary_path = parent_freeze / "freeze_summary.json"
    manifest_path = parent_freeze / "canonical_manifest.jsonl"
    seal_path = parent_freeze / canonical_contract.SEAL_NAME
    summary = json.loads(summary_path.read_text())
    rows = load_jsonl(manifest_path)
    manifest_sha = sha256(manifest_path)
    expected_parent = {
        "campaign": summary.get("campaign"),
        "campaign_ordinal": summary.get("campaign_ordinal"),
        "jobs_per_tune": summary.get("jobs_per_tune"),
        "canonical_manifest_sha256": manifest_sha,
        "freeze_summary_sha256": sha256(summary_path),
        "freeze_seal_sha256": sha256(seal_path),
        "freeze_path": relative_text,
    }
    if set(parent) != set(expected_parent):
        raise ValueError("equal-tune expansion parent fields differ")
    for key, expected in expected_parent.items():
        if parent.get(key) != expected:
            raise ValueError(f"equal-tune expansion parent {key} differs")
    return parent_freeze, summary, rows, manifest_sha


def _expansion_directory_inventory(path: Path, label: str) -> dict:
    require_existing_directory_chain_no_symlinks(path)
    files = 0
    total_bytes = 0
    digest = hashlib.sha256()
    for candidate in sorted(path.rglob("*")):
        metadata = candidate.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"{label} contains a symbolic link")
        if stat.S_ISDIR(metadata.st_mode):
            continue
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ValueError(f"{label} contains a non-single-link file")
        relative = candidate.relative_to(path).as_posix()
        files += 1
        total_bytes += metadata.st_size
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(str(metadata.st_size).encode())
        digest.update(b"\0")
        digest.update(sha256(candidate).encode())
        digest.update(b"\n")
    if files < 1 or total_bytes < 1:
        raise ValueError(f"{label} inventory is empty")
    return {
        "path": str(path),
        "file_count": files,
        "bytes": total_bytes,
        "inventory_sha256": digest.hexdigest(),
    }


def _expansion_coverage_evaluations(
    specification: dict, matrix: dict
) -> tuple[list[dict], list[str]]:
    _require_exact_object_keys(
        specification,
        {"schema", "frozen", "selection_rule", "observables"},
        "expansion coverage specification",
    )
    if (
        specification["schema"] != EXPANSION_COVERAGE_SPEC_SCHEMA
        or specification["frozen"] is not True
        or specification["selection_rule"] != EXPANSION_SELECTION_RULE
    ):
        raise ValueError("expansion coverage specification contract differs")
    _require_exact_object_keys(
        matrix,
        {
            "schema",
            "state",
            "canonical_manifest_sha256",
            "jobs_per_tune",
            "observations",
        },
        "expansion coverage matrix",
    )
    if (
        matrix["schema"] != EXPANSION_COVERAGE_MATRIX_SCHEMA
        or matrix["state"] != "COMPLETE"
    ):
        raise ValueError("expansion coverage matrix contract differs")
    criteria = specification["observables"]
    observations = matrix["observations"]
    if (
        not isinstance(criteria, list)
        or not criteria
        or not isinstance(observations, list)
        or not observations
    ):
        raise ValueError("expansion coverage specification/matrix is empty")
    criteria_by_name: dict[str, dict] = {}
    for criterion in criteria:
        _require_exact_object_keys(
            criterion,
            {
                "name",
                "minimum_finite_subsamples",
                "minimum_effective_entries",
                "maximum_relative_sem",
            },
            "expansion coverage criterion",
        )
        name = criterion["name"]
        if (
            not isinstance(name, str)
            or not name
            or name in criteria_by_name
            or _require_nonnegative_integer(
                criterion["minimum_finite_subsamples"],
                f"{name} minimum finite subsamples",
            )
            < 2
            or _require_nonnegative_integer(
                criterion["minimum_effective_entries"],
                f"{name} minimum effective entries",
            )
            < 1
        ):
            raise ValueError("expansion coverage criterion is invalid")
        _require_nonnegative_number(
            criterion["maximum_relative_sem"],
            f"{name} maximum relative SEM",
        )
        criteria_by_name[name] = criterion
    observations_by_name: dict[str, dict] = {}
    for observation in observations:
        _require_exact_object_keys(
            observation,
            {
                "name",
                "central_value",
                "std_error",
                "finite_subsamples",
                "effective_entries",
            },
            "expansion coverage observation",
        )
        name = observation["name"]
        if (
            not isinstance(name, str)
            or not name
            or name in observations_by_name
        ):
            raise ValueError("expansion coverage observation is invalid")
        observations_by_name[name] = observation
    if set(criteria_by_name) != set(observations_by_name):
        raise ValueError(
            "expansion matrix does not cover the exact frozen observables"
        )
    evaluations: list[dict] = []
    failing: list[str] = []
    for name in sorted(criteria_by_name):
        criterion = criteria_by_name[name]
        observation = observations_by_name[name]
        central = _require_nonnegative_number(
            observation["central_value"], f"{name} central magnitude"
        )
        error = _require_nonnegative_number(
            observation["std_error"], f"{name} standard error"
        )
        finite = _require_nonnegative_integer(
            observation["finite_subsamples"],
            f"{name} finite subsamples",
        )
        effective = _require_nonnegative_integer(
            observation["effective_entries"],
            f"{name} effective entries",
        )
        relative = error / central if central > 0.0 else math.inf
        reasons: list[str] = []
        if finite < criterion["minimum_finite_subsamples"]:
            reasons.append("insufficient_finite_subsamples")
        if effective < criterion["minimum_effective_entries"]:
            reasons.append("insufficient_effective_entries")
        if not math.isfinite(relative):
            reasons.append("zero_central_magnitude")
        elif relative > criterion["maximum_relative_sem"]:
            reasons.append("relative_sem_above_predeclared_limit")
        if reasons:
            failing.append(name)
        evaluations.append(
            {
                "name": name,
                "central_magnitude": central,
                "std_error": error,
                "finite_subsamples": finite,
                "effective_entries": effective,
                "relative_sem": (
                    relative if math.isfinite(relative) else None
                ),
                "criterion": criterion,
                "state": "FAIL" if reasons else "PASS",
                "failure_reasons": reasons,
            }
        )
    return evaluations, failing


def _validate_expansion_coverage_report(
    report: dict,
    checkout_root: Path,
    config: dict,
    summary: dict,
    manifest_sha: str,
    generator_sha: str,
) -> None:
    _require_exact_object_keys(
        report,
        {
            "schema",
            "state",
            "publication_promotion_allowed",
            "selection_rule",
            "canonical_manifest_sha256",
            "parent_campaign",
            "parent_campaign_ordinal",
            "jobs_per_tune",
            "specification_path",
            "specification_sha256",
            "matrix_path",
            "matrix_sha256",
            "generator_sha256",
            "evaluations",
            "failing_predeclared_observables",
        },
        "expansion coverage report",
    )
    if (
        report["schema"] != EXPANSION_COVERAGE_SCHEMA
        or report["selection_rule"] != EXPANSION_SELECTION_RULE
        or report["canonical_manifest_sha256"] != manifest_sha
        or report["parent_campaign"] != summary["campaign"]
        or report["parent_campaign_ordinal"]
        != summary["campaign_ordinal"]
        or report["jobs_per_tune"] != summary["jobs_per_tune"]
        or report["generator_sha256"] != generator_sha
    ):
        raise ValueError("expansion coverage report parent/generator differs")
    inputs: dict[str, tuple[Path, dict]] = {}
    for label in ("specification", "matrix"):
        path_text = report[f"{label}_path"]
        source = Path(path_text) if isinstance(path_text, str) else Path()
        if (
            not path_text
            or not source.is_absolute()
            or source.is_symlink()
            or not source.is_file()
        ):
            raise ValueError(f"expansion coverage {label} path is invalid")
        try:
            source.relative_to(checkout_root)
        except ValueError as error:
            raise ValueError(
                f"expansion coverage {label} is outside the checkout"
            ) from error
        require_existing_directory_chain_no_symlinks(source.parent)
        metadata = source.stat()
        if metadata.st_nlink != 1 or stat.S_IMODE(metadata.st_mode) != 0o444:
            raise ValueError(
                f"expansion coverage {label} is not frozen mode 0444"
            )
        if sha256(source) != report[f"{label}_sha256"]:
            raise ValueError(f"expansion coverage {label} checksum differs")
        payload = json.loads(source.read_text())
        if not isinstance(payload, dict):
            raise ValueError(f"expansion coverage {label} is not an object")
        inputs[label] = (source, payload)
    specification = inputs["specification"][1]
    matrix = inputs["matrix"][1]
    if (
        matrix.get("canonical_manifest_sha256") != manifest_sha
        or matrix.get("jobs_per_tune") != summary["jobs_per_tune"]
    ):
        raise ValueError("expansion coverage matrix is not parent-bound")
    evaluations, failing = _expansion_coverage_evaluations(
        specification, matrix
    )
    if (
        report["evaluations"] != evaluations
        or report["failing_predeclared_observables"] != failing
        or report["state"]
        != ("EXPANSION_REQUIRED" if failing else "SUFFICIENT")
        or report["publication_promotion_allowed"] is not (not failing)
        or not failing
    ):
        raise ValueError(
            "expansion coverage evaluations were not machine-reproduced"
        )


def _ceil_ratio(value: int, numerator: int, denominator: int) -> int:
    return (value * numerator + denominator - 1) // denominator


def _validate_expansion_storage_report(
    report: dict,
    checkout_root: Path,
    config: dict,
    summary: dict,
    parent_rows: list[dict],
    manifest_sha: str,
    generator_sha: str,
    decision_time: datetime.datetime,
) -> None:
    _require_exact_object_keys(
        report,
        {
            "schema",
            "state",
            "gate_e_storage_authorized",
            "campaign",
            "campaign_ordinal",
            "campaign_json_sha256",
            "parent_campaign",
            "parent_canonical_manifest_sha256",
            "parent_jobs_per_tune",
            "additional_jobs_per_tune",
            "final_jobs_per_tune",
            "candidate_slots",
            "parent_raw_inventory_sha256",
            "maximum_parent_raw_bytes_by_tune",
            "parent_analysis_inventory",
            "parent_analyzed_data_inventory",
            "projection_components",
            "projected_required_additional_bytes",
            "capacity_policy",
            "final_capacity_recheck",
            "generator_sha256",
        },
        "expansion storage report",
    )
    campaign_dir = checkout_root / "campaigns" / config["campaign"]
    parent_jobs = int(summary["jobs_per_tune"])
    additional = int(config["planned_additional_jobs_per_tune"])
    final_jobs = parent_jobs + additional
    if (
        report["schema"] != EXPANSION_STORAGE_SCHEMA
        or report["state"] != "PASS"
        or report["gate_e_storage_authorized"] is not True
        or report["campaign"] != config["campaign"]
        or report["campaign_ordinal"] != config["campaign_ordinal"]
        or report["campaign_json_sha256"]
        != sha256(campaign_dir / "campaign.json")
        or report["parent_campaign"] != summary["campaign"]
        or report["parent_canonical_manifest_sha256"] != manifest_sha
        or report["parent_jobs_per_tune"] != parent_jobs
        or report["additional_jobs_per_tune"] != additional
        or report["final_jobs_per_tune"] != final_jobs
        or report["candidate_slots"] != config["candidate_slots"]
        or report["capacity_policy"] != EXPANSION_CAPACITY_POLICY
        or report["generator_sha256"] != generator_sha
    ):
        raise ValueError("expansion storage report campaign contract differs")

    production_collection = checkout_root / "Production"
    maximum_raw = {tune: 0 for tune in TUNES}
    raw_digest = hashlib.sha256()
    for row in parent_rows:
        tune = row.get("tune")
        if tune not in maximum_raw:
            raise ValueError("expansion parent raw inventory has unknown tune")
        relative_text = row.get("raw_path")
        relative = (
            Path(relative_text)
            if isinstance(relative_text, str)
            else Path()
        )
        if (
            not relative_text
            or relative.is_absolute()
            or ".." in relative.parts
        ):
            raise ValueError("expansion parent raw path is unsafe")
        source = (
            production_collection / relative
            if summary.get("schema")
            == "hf_superseding_canonical_freeze_summary_v1"
            else production_collection / summary["campaign"] / relative
        )
        require_existing_directory_chain_no_symlinks(source.parent)
        if source.is_symlink() or not source.is_file():
            raise ValueError("expansion parent raw file is absent")
        metadata = source.stat()
        if (
            metadata.st_nlink != 1
            or metadata.st_size != row.get("raw_bytes")
            or sha256(source) != row.get("raw_sha256")
        ):
            raise ValueError("expansion parent raw inventory changed")
        maximum_raw[tune] = max(maximum_raw[tune], metadata.st_size)
        raw_digest.update(relative.as_posix().encode())
        raw_digest.update(b"\0")
        raw_digest.update(str(metadata.st_size).encode())
        raw_digest.update(b"\0")
        raw_digest.update(row["raw_sha256"].encode())
        raw_digest.update(b"\n")
    if (
        any(value <= 0 for value in maximum_raw.values())
        or report["maximum_parent_raw_bytes_by_tune"] != maximum_raw
        or report["parent_raw_inventory_sha256"]
        != raw_digest.hexdigest()
    ):
        raise ValueError("expansion parent raw inventory digest differs")

    inventory_fields = {"path", "file_count", "bytes", "inventory_sha256"}
    inventories: dict[str, dict] = {}
    for report_key, label, output_root_name in (
        (
            "parent_analysis_inventory",
            "parent analysis inventory",
            "AnalysisOutput",
        ),
        (
            "parent_analyzed_data_inventory",
            "parent analyzed-data inventory",
            "AnalyzedData",
        ),
    ):
        stored = _require_exact_object_keys(
            report[report_key], inventory_fields, label
        )
        path_text = stored["path"]
        source = Path(path_text) if isinstance(path_text, str) else Path()
        if not path_text or not source.is_absolute():
            raise ValueError(f"{label} path is invalid")
        expected_root = checkout_root / output_root_name
        try:
            source_relative = source.relative_to(expected_root)
        except ValueError as error:
            raise ValueError(
                f"{label} is outside its canonical output root"
            ) from error
        if summary["campaign"] not in source_relative.parts:
            raise ValueError(f"{label} is not bound to the parent campaign")
        current = _expansion_directory_inventory(source, label)
        if stored != current:
            raise ValueError(f"{label} changed after projection")
        inventories[report_key] = current

    component_keys = {
        "all_candidate_raw_outputs_bytes",
        "additional_per_job_analysis_outputs_bytes",
        "new_full_superseding_analyzed_outputs_bytes",
        "one_full_candidate_batch_retry_partial_contingency_bytes",
        "one_full_derived_output_staging_contingency_bytes",
        "ten_percent_filesystem_overhead_bytes",
    }
    components = _require_exact_object_keys(
        report["projection_components"],
        component_keys,
        "expansion storage projection components",
    )
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in components.values()
    ):
        raise ValueError("expansion storage components are not positive bytes")
    projected_raw = sum(
        config["candidate_slots"][tune] * maximum_raw[tune]
        for tune in TUNES
    )
    projected_analysis = _ceil_ratio(
        inventories["parent_analysis_inventory"]["bytes"],
        additional,
        parent_jobs,
    )
    projected_analyzed = _ceil_ratio(
        inventories["parent_analyzed_data_inventory"]["bytes"],
        final_jobs,
        parent_jobs,
    )
    subtotal = (
        projected_raw
        + projected_analysis
        + projected_analyzed
        + projected_raw
        + projected_analyzed
    )
    overhead = _ceil_ratio(subtotal, 1, 10)
    expected_components = {
        "all_candidate_raw_outputs_bytes": projected_raw,
        "additional_per_job_analysis_outputs_bytes": projected_analysis,
        "new_full_superseding_analyzed_outputs_bytes": projected_analyzed,
        "one_full_candidate_batch_retry_partial_contingency_bytes":
            projected_raw,
        "one_full_derived_output_staging_contingency_bytes":
            projected_analyzed,
        "ten_percent_filesystem_overhead_bytes": overhead,
    }
    required = subtotal + overhead
    if (
        components != expected_components
        or report["projected_required_additional_bytes"] != required
    ):
        raise ValueError("expansion storage projection arithmetic differs")

    capacity = _require_exact_object_keys(
        report["final_capacity_recheck"],
        {
            "state",
            "checked_utc",
            "path",
            "device",
            "capacity_bytes",
            "available_bytes",
            "required_additional_bytes",
            "reserve_fraction",
            "reserve_bytes",
            "projected_available_bytes",
            "capacity_policy",
        },
        "expansion final capacity check",
    )
    checked = _require_utc_timestamp(
        capacity["checked_utc"], "expansion final capacity check"
    )
    if (
        checked > decision_time + datetime.timedelta(minutes=5)
        or decision_time - checked > EXPANSION_STORAGE_MAX_RECHECK_AGE
    ):
        raise ValueError(
            "expansion capacity evidence was stale at owner authorization"
        )
    capacity_path = (
        Path(capacity["path"])
        if isinstance(capacity["path"], str)
        else Path()
    )
    if (
        not capacity_path.is_absolute()
        or capacity_path.is_symlink()
        or capacity["state"] != "PASS"
        or capacity["required_additional_bytes"] != required
        or capacity["reserve_fraction"] != 0.05
        or capacity["capacity_policy"] != EXPANSION_CAPACITY_POLICY
        or isinstance(capacity["device"], bool)
        or not isinstance(capacity["device"], int)
    ):
        raise ValueError("expansion final capacity check contract differs")
    require_existing_directory_chain_no_symlinks(capacity_path)
    for field in (
        "capacity_bytes",
        "available_bytes",
        "reserve_bytes",
        "projected_available_bytes",
    ):
        _require_nonnegative_integer(
            capacity[field], f"expansion capacity {field}"
        )
    expected_reserve = _ceil_ratio(capacity["capacity_bytes"], 5, 100)
    expected_projected = capacity["available_bytes"] - required
    if (
        capacity["reserve_bytes"] != expected_reserve
        or capacity["projected_available_bytes"] != expected_projected
        or expected_projected < expected_reserve
    ):
        raise ValueError("expansion final capacity arithmetic differs")


def _count_retained_tree(path: Path, label: str) -> int:
    if not path.exists():
        return 0
    require_existing_directory_chain_no_symlinks(path)
    total = 0
    for candidate in path.rglob("*"):
        metadata = candidate.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"{label} contains a symbolic link")
        if stat.S_ISDIR(metadata.st_mode):
            continue
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ValueError(f"{label} contains a non-single-link file")
        total += metadata.st_size
    return total


def _expansion_retained_staging_bytes(
    checkout_root: Path, campaign: str
) -> int:
    total = 0
    for output_root_name in ("Production", "AnalysisOutput", "AnalyzedData"):
        output_root = checkout_root / output_root_name
        if not output_root.exists():
            continue
        require_existing_directory_chain_no_symlinks(output_root)
        candidate_roots = [
            child
            for child in output_root.iterdir()
            if campaign in child.name
        ]
        for candidate_root in candidate_roots:
            metadata = candidate_root.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                raise ValueError("expansion staging root is a symbolic link")
            discovered = (
                [candidate_root]
                if stat.S_ISREG(metadata.st_mode)
                else candidate_root.rglob("*")
            )
            for candidate in discovered:
                relative = candidate.relative_to(output_root)
                if (
                    output_root_name == "Production"
                    and len(relative.parts) >= 2
                    and relative.parts[0] == campaign
                    and relative.parts[1] in {"partial", "quarantine"}
                ):
                    continue
                if not any(
                    ".partial." in component
                    or ".staging." in component
                    or component in {"staging", "merge_staging"}
                    for component in relative.parts
                ):
                    continue
                metadata = candidate.lstat()
                if stat.S_ISLNK(metadata.st_mode):
                    raise ValueError("expansion staging output is unsafe")
                if stat.S_ISDIR(metadata.st_mode):
                    continue
                if (
                    not stat.S_ISREG(metadata.st_mode)
                    or metadata.st_nlink != 1
                ):
                    raise ValueError("expansion staging output is unsafe")
                total += metadata.st_size
    return total


def live_recheck_expansion_storage(
    authorization: dict, checkout_root: Path, config: dict
) -> dict:
    binding = authorization.get("storage_projection")
    if not isinstance(binding, dict):
        raise ValueError("expansion storage binding is absent")
    relative = Path(str(binding.get("path", "")))
    if (
        not binding.get("path")
        or relative.is_absolute()
        or ".." in relative.parts
    ):
        raise ValueError("expansion storage binding path is unsafe")
    storage_path = checkout_root / relative
    storage = _sealed_expansion_json(
        storage_path, "equal-tune expansion storage projection"
    )
    if sha256(storage_path) != binding.get("sha256"):
        raise ValueError("equal-tune expansion storage projection changed")
    capacity = storage["final_capacity_recheck"]
    capacity_path = Path(capacity["path"])
    require_existing_directory_chain_no_symlinks(capacity_path)
    metadata = capacity_path.stat()
    filesystem = os.statvfs(capacity_path)
    fragment = int(filesystem.f_frsize or filesystem.f_bsize)
    current_capacity = int(filesystem.f_blocks * fragment)
    current_available = int(filesystem.f_bavail * fragment)
    required = int(storage["projected_required_additional_bytes"])
    reserve = _ceil_ratio(current_capacity, 5, 100)
    if (
        int(metadata.st_dev) != capacity["device"]
        or current_capacity != capacity["capacity_bytes"]
        or current_available - required < reserve
    ):
        raise ValueError(
            "live equal-tune expansion storage headroom no longer passes"
        )
    campaign_root = checkout_root / "Production" / config["campaign"]
    retained_partial = (
        _count_retained_tree(
            campaign_root / "partial",
            "expansion retained partial output",
        )
        + _count_retained_tree(
            campaign_root / "quarantine",
            "expansion retained quarantine output",
        )
    )
    components = storage["projection_components"]
    partial_budget = components[
        "one_full_candidate_batch_retry_partial_contingency_bytes"
    ]
    retained_staging = _expansion_retained_staging_bytes(
        checkout_root, config["campaign"]
    )
    staging_budget = components[
        "one_full_derived_output_staging_contingency_bytes"
    ]
    if (
        retained_partial > partial_budget
        or retained_staging > staging_budget
    ):
        raise ValueError(
            "retained expansion partial/staging data exceed frozen budgets"
        )
    return {
        "schema": EXPANSION_LIVE_STORAGE_SCHEMA,
        "state": "PASS",
        "checked_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "source_storage_projection_path": str(relative),
        "source_storage_projection_sha256": sha256(storage_path),
        "capacity_path": str(capacity_path),
        "device": int(metadata.st_dev),
        "capacity_bytes": current_capacity,
        "available_bytes": current_available,
        "required_additional_bytes": required,
        "reserve_bytes": reserve,
        "projected_available_bytes": current_available - required,
        "retained_partial_and_quarantine_bytes": retained_partial,
        "retained_partial_budget_bytes": partial_budget,
        "retained_staging_bytes": retained_staging,
        "retained_staging_budget_bytes": staging_budget,
    }


def _parse_jsonl_bytes(content: bytes, label: str) -> list[dict]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} is not UTF-8") from error
    rows: list[dict] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{label} line {number} is not JSON") from error
        if not isinstance(row, dict):
            raise ValueError(f"{label} line {number} is not an object")
        rows.append(row)
    return rows


def _validate_expansion_ledger_prefix(
    authorization: dict, campaign_dir: Path, config: dict
) -> list[dict]:
    ledger_path = campaign_dir / "seed_ledger.jsonl"
    ledger_bytes = ledger_path.read_bytes()
    prefix_bytes = authorization.get("initial_seed_ledger_prefix_bytes")
    prefix_sha = authorization.get("initial_seed_ledger_prefix_sha256")
    if (
        isinstance(prefix_bytes, bool)
        or not isinstance(prefix_bytes, int)
        or prefix_bytes < 1
        or prefix_bytes > len(ledger_bytes)
        or not SHA256.fullmatch(str(prefix_sha or ""))
        or hashlib.sha256(ledger_bytes[:prefix_bytes]).hexdigest()
        != prefix_sha
        or not ledger_bytes[:prefix_bytes].endswith(b"\n")
    ):
        raise ValueError(
            "equal-tune expansion initial seed-ledger prefix differs"
        )
    initial = _parse_jsonl_bytes(
        ledger_bytes[:prefix_bytes],
        "equal-tune expansion initial seed-ledger prefix",
    )
    suffix = _parse_jsonl_bytes(
        ledger_bytes[prefix_bytes:],
        "equal-tune expansion retry seed-ledger suffix",
    )
    candidates = load_jsonl(campaign_dir / "candidate_manifest.jsonl")
    slots, _, _ = campaign_slot_contract(config)
    expected_count = sum(slots.values())
    if len(initial) != expected_count or len(candidates) != expected_count:
        raise ValueError(
            "equal-tune expansion initial allocation cardinality differs"
        )
    candidate_by_identity: dict[tuple[str, int], dict] = {}
    for candidate in candidates:
        identity = (candidate.get("tune"), candidate.get("logical_id"))
        if (
            identity[0] not in TUNES
            or isinstance(identity[1], bool)
            or not isinstance(identity[1], int)
            or not 0 <= identity[1] < slots[identity[0]]
            or identity in candidate_by_identity
            or candidate.get("campaign") != config["campaign"]
            or isinstance(candidate.get("attempt"), bool)
            or not isinstance(candidate.get("attempt"), int)
            or candidate.get("attempt") != 0
            or isinstance(candidate.get("seed"), bool)
            or not isinstance(candidate.get("seed"), int)
            or candidate.get("seed")
            != campaign_logical_seed(
                config, identity[0], identity[1], 0
            )
        ):
            raise ValueError(
                "equal-tune expansion initial candidate identity differs"
            )
        candidate_by_identity[identity] = candidate
    initial_keys = {
        "campaign",
        "tune",
        "logical_id",
        "attempt",
        "seed",
        "allocation",
    }
    attempts: dict[tuple[str, int], set[int]] = {}
    all_seeds: set[int] = set()
    for row in initial:
        _require_exact_object_keys(
            row, initial_keys, "equal-tune expansion initial allocation"
        )
        identity = (row["tune"], row["logical_id"])
        candidate = candidate_by_identity.get(identity)
        if (
            row["tune"] not in TUNES
            or isinstance(row["logical_id"], bool)
            or not isinstance(row["logical_id"], int)
            or isinstance(row["attempt"], bool)
            or not isinstance(row["attempt"], int)
            or isinstance(row["seed"], bool)
            or not isinstance(row["seed"], int)
            or candidate is None
            or row["campaign"] != config["campaign"]
            or row["attempt"] != 0
            or row["allocation"] != "initial"
            or row["seed"] != candidate["seed"]
            or row["seed"] in all_seeds
        ):
            raise ValueError(
                "equal-tune expansion initial ledger allocation differs"
            )
        all_seeds.add(row["seed"])
        attempts[identity] = {0}
    if set(attempts) != set(candidate_by_identity):
        raise ValueError(
            "equal-tune expansion initial ledger coverage differs"
        )
    retry_keys = initial_keys | {
        "reason",
        "prior_attempt_evidence",
    }
    reserved = authorization.get("reserved_seed_intervals")
    for row in suffix:
        _require_exact_object_keys(
            row, retry_keys, "equal-tune expansion retry allocation"
        )
        tune = row.get("tune")
        logical_id = row.get("logical_id")
        attempt = row.get("attempt")
        seed = row.get("seed")
        reason = row.get("reason")
        evidence = row.get("prior_attempt_evidence")
        if (
            tune not in TUNES
            or isinstance(logical_id, bool)
            or not isinstance(logical_id, int)
            or not 0 <= logical_id < slots[tune]
            or isinstance(attempt, bool)
            or not isinstance(attempt, int)
            or not 1 <= attempt < int(config["max_attempts_per_logical_id"])
            or isinstance(seed, bool)
            or not isinstance(seed, int)
            or seed != campaign_logical_seed(
                config, tune, logical_id, attempt
            )
            or seed in all_seeds
            or row.get("campaign") != config["campaign"]
            or row.get("allocation") != "retry"
            or not isinstance(reason, str)
            or not reason.strip()
            or len(reason) > 500
            or not isinstance(evidence, dict)
            or set(evidence) != {"kind", "path", "sha256"}
            or evidence.get("kind")
            not in {
                "producer_failure",
                "raw_validation_fail",
                "scheduler_loss_approval",
            }
            or not isinstance(evidence.get("path"), str)
            or Path(evidence["path"]).is_absolute()
            or ".." in Path(evidence["path"]).parts
            or not SHA256.fullmatch(str(evidence.get("sha256", "")))
        ):
            raise ValueError(
                "equal-tune expansion retry allocation is invalid"
            )
        if not any(first <= seed <= last for first, last in reserved):
            raise ValueError(
                "equal-tune expansion retry seed is outside reservation"
            )
        evidence_path = campaign_dir.parents[1] / evidence["path"]
        if (
            evidence_path.is_symlink()
            or not evidence_path.is_file()
            or evidence_path.stat().st_nlink != 1
            or stat.S_IMODE(evidence_path.stat().st_mode) & 0o222
            or sha256(evidence_path) != evidence["sha256"]
        ):
            raise ValueError(
                "equal-tune expansion retry evidence is absent or changed"
            )
        identity = (tune, logical_id)
        prior_attempts = attempts.setdefault(identity, {0})
        if attempt != max(prior_attempts) + 1:
            raise ValueError(
                "equal-tune expansion retry suffix is not append-ordered"
            )
        prior_attempts.add(attempt)
        all_seeds.add(seed)
    if any(values != set(range(max(values) + 1)) for values in attempts.values()):
        raise ValueError(
            "equal-tune expansion retry attempts are not contiguous"
        )
    return initial + suffix


def recheck_expansion_storage_from_claim(
    claim: dict,
    checkout_root: Path,
    config: dict,
    *,
    require_recent_claim: bool = True,
) -> dict:
    prior = claim.get("expansion_live_storage_recheck")
    authorization_path = (
        checkout_root
        / "campaigns"
        / config["campaign"]
        / "EQUAL_TUNE_EXPANSION_AUTHORIZATION.json"
    )
    if (
        not isinstance(prior, dict)
        or prior.get("schema") != EXPANSION_LIVE_STORAGE_SCHEMA
        or prior.get("state") != "PASS"
        or claim.get("equal_tune_expansion_authorization_sha256")
        != sha256(authorization_path)
    ):
        raise ValueError(
            "submission claim lacks canonical live expansion storage evidence"
        )
    captured = _require_utc_timestamp(
        prior.get("checked_utc"),
        "submission claim expansion live-storage check",
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    if captured > now + datetime.timedelta(minutes=5) or (
        require_recent_claim
        and now - captured > EXPANSION_STORAGE_MAX_RECHECK_AGE
    ):
        raise ValueError("submission claim expansion storage check is stale")
    authorization = validate_expansion_authorization(
        authorization_path, checkout_root, config
    )
    return live_recheck_expansion_storage(
        authorization, checkout_root, config
    )


def validate_expansion_authorization(
    path: Path, checkout_root: Path, config: dict
) -> dict:
    """Validate the distinct owner decision required for later expansion."""
    checkout_root = checkout_root.resolve()
    if config.get("campaign_kind") != EQUAL_TUNE_EXPANSION_KIND:
        raise ValueError(
            "equal-tune expansion authorization used for a non-expansion campaign"
        )
    expected_path = (
        checkout_root
        / "campaigns"
        / config["campaign"]
        / "EQUAL_TUNE_EXPANSION_AUTHORIZATION.json"
    )
    path = Path(os.path.abspath(path))
    if path != expected_path:
        raise ValueError(
            "equal-tune expansion authorization path is not canonical"
        )
    authorization = _sealed_expansion_json(
        path, "equal-tune expansion authorization"
    )
    campaign_dir = checkout_root / "campaigns" / config["campaign"]
    campaign_json = campaign_dir / "campaign.json"
    candidate_manifest = campaign_dir / "candidate_manifest.jsonl"
    seed_ledger = campaign_dir / "seed_ledger.jsonl"
    initial_ledger_bytes = authorization.get(
        "initial_seed_ledger_prefix_bytes"
    )
    generator_path = checkout_root / "tools/generate_expansion_evidence.py"
    if generator_path.is_symlink() or not generator_path.is_file():
        raise ValueError("checkout lacks the expansion evidence generator")
    generator_sha = sha256(generator_path)
    if generator_sha != git_file_sha256(
        checkout_root,
        config["repository_commit"],
        "tools/generate_expansion_evidence.py",
    ):
        raise ValueError(
            "expansion evidence generator differs from campaign commit"
        )
    authorization_fields = {
        "schema",
        "decision",
        "approved",
        "reviewer",
        "reviewer_role",
        "decision_utc",
        "rationale",
        "campaign",
        "campaign_ordinal",
        "repository_commit",
        "equal_tune_scope",
        "additional_jobs_per_tune",
        "final_jobs_per_tune",
        "candidate_slots",
        "campaign_json_sha256",
        "candidate_manifest_sha256",
        "initial_seed_ledger_prefix_bytes",
        "initial_seed_ledger_prefix_sha256",
        "reserved_seed_intervals",
        "parent",
        "evidence_generator_sha256",
        "coverage_precision_report",
        "storage_projection",
    }
    _require_exact_object_keys(
        authorization,
        authorization_fields,
        "equal-tune expansion authorization",
    )
    expected = {
        "schema": EXPANSION_AUTHORIZATION_SCHEMA,
        "decision": "APPROVE_EQUAL_TUNE_EXPANSION",
        "approved": True,
        "reviewer_role": "project_owner",
        "campaign": config["campaign"],
        "campaign_ordinal": config["campaign_ordinal"],
        "repository_commit": config["repository_commit"],
        "equal_tune_scope": list(TUNES),
        "additional_jobs_per_tune":
            config["planned_additional_jobs_per_tune"],
        "final_jobs_per_tune": config["planned_final_jobs_per_tune"],
        "candidate_slots": config["candidate_slots"],
        "campaign_json_sha256": sha256(campaign_json),
        "candidate_manifest_sha256": sha256(candidate_manifest),
        "reserved_seed_intervals":
            reserved_seed_intervals(config, []),
        "parent": config["supersedes"],
        "evidence_generator_sha256": generator_sha,
    }
    for key, value in expected.items():
        if authorization.get(key) != value:
            raise ValueError(
                f"equal-tune expansion authorization {key} differs"
            )
    reviewer = authorization.get("reviewer")
    if (
        not isinstance(reviewer, str)
        or not reviewer.strip()
        or "PROJECT OWNER" in reviewer.upper()
        or "UNIT TEST" in reviewer.upper()
    ):
        raise ValueError("equal-tune expansion reviewer is absent or placeholder")
    decision_time = _require_utc_timestamp(
        authorization.get("decision_utc"),
        "equal-tune expansion authorization",
    )
    if (
        decision_time
        > datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=5)
    ):
        raise ValueError(
            "equal-tune expansion authorization is implausibly in the future"
        )
    rationale = authorization.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError("equal-tune expansion rationale is absent")
    if (
        isinstance(initial_ledger_bytes, bool)
        or not isinstance(initial_ledger_bytes, int)
    ):
        raise ValueError(
            "equal-tune expansion initial ledger prefix length is invalid"
        )

    parent_freeze, summary, parent_rows, parent_manifest_sha = (
        _expansion_parent_evidence(checkout_root, config)
    )
    if parent_freeze != checkout_root / config["supersedes"]["freeze_path"]:
        raise ValueError("equal-tune expansion parent path differs")
    _validate_expansion_ledger_prefix(
        authorization, campaign_dir, config
    )

    bindings = ("coverage_precision_report", "storage_projection")
    loaded: dict[str, dict] = {}
    for label in bindings:
        binding = authorization.get(label)
        _require_exact_object_keys(
            binding, {"path", "sha256"}, f"equal-tune expansion {label} binding"
        )
        if (
            not isinstance(binding["path"], str)
            or not SHA256.fullmatch(str(binding["sha256"]))
        ):
            raise ValueError(f"equal-tune expansion {label} binding is malformed")
        relative = Path(binding["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"equal-tune expansion {label} path is unsafe")
        artifact = checkout_root / relative
        require_existing_directory_chain_no_symlinks(artifact.parent)
        payload = _sealed_expansion_json(
            artifact, f"equal-tune expansion {label}"
        )
        if sha256(artifact) != binding["sha256"]:
            raise ValueError(
                f"equal-tune expansion {label} is absent or changed"
            )
        loaded[label] = payload

    _validate_expansion_coverage_report(
        loaded["coverage_precision_report"],
        checkout_root,
        config,
        summary,
        parent_manifest_sha,
        generator_sha,
    )
    _validate_expansion_storage_report(
        loaded["storage_projection"],
        checkout_root,
        config,
        summary,
        parent_rows,
        parent_manifest_sha,
        generator_sha,
        decision_time,
    )
    live_recheck_expansion_storage(
        authorization, checkout_root, config
    )
    return authorization


def _replace_card_setting(
    content: bytes,
    setting: bytes,
    value: str,
    *,
    append_if_missing: bool,
) -> bytes:
    """Mirror the canonical worker's exact line-oriented card rewrite."""
    replacement = setting + b" = " + value.encode("ascii")
    output: list[bytes] = []
    found = False
    for line in content.splitlines(keepends=True):
        if line.startswith(setting):
            found = True
            if line.endswith(b"\r\n"):
                output.append(replacement + b"\r\n")
            elif line.endswith(b"\n"):
                output.append(replacement + b"\n")
            else:
                output.append(replacement)
        else:
            output.append(line)
    rewritten = b"".join(output)
    if not found:
        if not append_if_missing:
            raise ValueError(
                f"required setting {setting.decode('ascii')} is absent from card"
            )
        # This deliberately matches: printf '\nSETTING = VALUE\n' >> CARD
        rewritten += b"\n" + replacement + b"\n"
    return rewritten


def effective_card_bytes(
    card: Path, requested_successes: int, pthat_min_override: str | None
) -> bytes:
    if requested_successes < 1:
        raise ValueError("requested_successes must be positive")
    content = _replace_card_setting(
        card.read_bytes(),
        b"Main:numberOfEvents",
        str(requested_successes),
        append_if_missing=True,
    )
    if pthat_min_override not in (None, "", "NONE"):
        if pthat_min_override not in {"0.5", "1.0", "2.0"}:
            raise ValueError(
                "pthat_min_override must be NONE, 0.5, 1.0, or 2.0"
            )
        content = _replace_card_setting(
            content,
            b"PhaseSpace:pTHatMin",
            pthat_min_override,
            append_if_missing=False,
        )
    return content


def effective_card_sha256(
    card: Path, requested_successes: int, pthat_min_override: str | None
) -> str:
    return hashlib.sha256(
        effective_card_bytes(card, requested_successes, pthat_min_override)
    ).hexdigest()


def effective_pthat_min(card: Path, pthat_min_override: str | None) -> float:
    if pthat_min_override not in (None, "", "NONE"):
        return float(pthat_min_override)
    values: list[float] = []
    pattern = re.compile(
        rb"^PhaseSpace:pTHatMin\s*=\s*"
        rb"([-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?)"
    )
    for line in card.read_bytes().splitlines():
        match = pattern.match(line)
        if match:
            values.append(float(match.group(1)))
    if not values or not math.isfinite(values[-1]) or values[-1] < 0.0:
        raise ValueError("card has no finite non-negative PhaseSpace:pTHatMin")
    return values[-1]


def validate_campaign_identity(
    campaign_dir: Path, config: dict, candidates: list[dict], ledger: list[dict]
) -> tuple[str, int]:
    campaign = config.get("campaign")
    if not isinstance(campaign, str) or not SAFE_CAMPAIGN.fullmatch(campaign):
        raise ValueError("campaign name is missing or contains unsafe characters")
    if campaign_dir.name != campaign:
        raise ValueError(
            f"campaign directory basename {campaign_dir.name!r} != {campaign!r}"
        )
    ordinal = config.get("campaign_ordinal")
    if (
        isinstance(ordinal, bool)
        or not isinstance(ordinal, int)
        or not 1 <= ordinal <= 65_535
    ):
        raise ValueError("campaign_ordinal must be an integer in [1,65535]")
    for row in candidates:
        if row.get("campaign") != campaign:
            raise ValueError("candidate campaign differs from campaign.json")
        row_ordinal = row.get("campaign_ordinal")
        if (
            isinstance(row_ordinal, bool)
            or not isinstance(row_ordinal, int)
            or row_ordinal != ordinal
        ):
            raise ValueError("candidate campaign_ordinal differs from campaign.json")
    for row in ledger:
        if row.get("campaign") != campaign:
            raise ValueError("seed-ledger campaign differs from campaign.json")
    return campaign, ordinal


def logical_seed(seed_base: int, max_attempts: int, tune: str, logical_id: int, attempt: int) -> int:
    if tune not in TUNES:
        raise ValueError(f"unknown tune {tune}")
    if logical_id < 0 or logical_id >= SLOTS[tune]:
        raise ValueError(f"logical ID {logical_id} outside {tune} candidate range")
    if not 1 <= max_attempts <= MAX_ATTEMPTS_PER_LOGICAL_ID:
        raise ValueError("max_attempts exceeds the 12-bit event-ID domain")
    if attempt < 0 or attempt >= max_attempts:
        raise ValueError(f"attempt {attempt} outside [0,{max_attempts})")
    seed = seed_base + (GLOBAL_OFFSETS[tune] + logical_id) * max_attempts + attempt
    if not 1 <= seed <= 900_000_000:
        raise ValueError(f"seed {seed} outside PYTHIA domain")
    return seed


def campaign_slot_contract(config: dict) -> tuple[dict[str, int], dict[str, int], int]:
    """Return immutable candidate counts/offsets and the primary-ID limit."""
    kind = config.get("campaign_kind")
    if kind == EQUAL_TUNE_EXPANSION_KIND:
        additional = config.get("planned_additional_jobs_per_tune")
        if (
            isinstance(additional, bool)
            or not isinstance(additional, int)
            or not 10 <= additional <= 100
            or additional % 10
        ):
            raise ValueError("invalid equal-tune expansion size")
        expected_slots = {
            "MONASH": additional,
            "JUNCTIONS": 2 * additional,
            "CLOSEPACKING": 2 * additional,
        }
        expected_offsets = {
            "MONASH": 0,
            "JUNCTIONS": additional,
            "CLOSEPACKING": 3 * additional,
        }
        primary_limit = additional
    else:
        expected_slots = dict(SLOTS)
        expected_offsets = dict(GLOBAL_OFFSETS)
        primary_limit = 100
    if config.get("candidate_slots") != expected_slots:
        raise ValueError("campaign candidate-slot contract differs")
    if config.get("global_offsets") != expected_offsets:
        raise ValueError("campaign global-offset contract differs")
    return expected_slots, expected_offsets, primary_limit


def campaign_logical_seed(
    config: dict, tune: str, logical_id: int, attempt: int
) -> int:
    slots, offsets, _ = campaign_slot_contract(config)
    if tune not in TUNES:
        raise ValueError(f"unknown tune {tune}")
    if logical_id < 0 or logical_id >= slots[tune]:
        raise ValueError(f"logical ID {logical_id} outside {tune} candidate range")
    maximum = int(config["max_attempts_per_logical_id"])
    if not 1 <= maximum <= MAX_ATTEMPTS_PER_LOGICAL_ID:
        raise ValueError(
            "max_attempts_per_logical_id exceeds the 12-bit event-ID domain"
        )
    if attempt < 0 or attempt >= maximum:
        raise ValueError(f"attempt {attempt} outside [0,{maximum})")
    seed = (
        int(config["seed_base"])
        + (offsets[tune] + logical_id) * maximum
        + attempt
    )
    if not 1 <= seed <= 900_000_000:
        raise ValueError(f"seed {seed} outside PYTHIA domain")
    return seed


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


def generate(args: argparse.Namespace) -> int:
    if not SAFE_CAMPAIGN.fullmatch(args.campaign):
        raise SystemExit(
            "campaign may contain only letters, digits, dot, underscore, and hyphen"
        )
    if not 1 <= args.campaign_ordinal <= 65_535:
        raise SystemExit("campaign-ordinal must be in [1,65535]")
    if not 1 <= args.events <= 1_048_575:
        raise SystemExit("events must be in [1,1048575]")
    if not 1 <= args.max_attempts <= MAX_ATTEMPTS_PER_LOGICAL_ID:
        raise SystemExit(
            "max-attempts must be in [1,4096] for the 12-bit event-ID field"
        )
    root = args.root.resolve()
    campaign_dir = root / "campaigns" / args.campaign
    if campaign_dir.exists() and any(campaign_dir.iterdir()):
        raise SystemExit(f"refusing to alter nonempty campaign directory: {campaign_dir}")
    species = root / "config/heavy_flavour_species_v1.json"
    pairs = root / "config/heavy_flavour_pair_registry_v1.json"
    tune_allowlist = root / "config/tune_difference_allowlist_v1.json"
    pthat_spec = root / "config/pthat_sensitivity_v1.json"
    validate_pthat_spec_preapproval(root)
    cards = {
        tune: root / "SimulationScripts" / f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
        for tune in TUNES
    }
    repository_commit = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    repository_dirty = bool(
        subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain"], text=True
        ).strip()
    )
    if repository_dirty and not args.allow_dirty:
        raise SystemExit("refusing to generate canonical campaign from dirty repository")
    expansion_fields: dict = {}
    candidate_slots = dict(SLOTS)
    global_offsets = dict(GLOBAL_OFFSETS)
    primary_limit = 100
    parent_freeze_arg = getattr(args, "parent_freeze", None)
    if parent_freeze_arg is not None:
        additional_jobs = int(args.additional_jobs_per_tune)
        if (
            additional_jobs < 10
            or additional_jobs > 100
            or additional_jobs % 10
        ):
            raise SystemExit(
                "additional-jobs-per-tune must be a multiple of ten in [10,100]"
            )
        parent_freeze = parent_freeze_arg.resolve()
        try:
            parent_relative = parent_freeze.relative_to(root)
        except ValueError as error:
            raise SystemExit(
                "parent freeze must be inside the generating checkout"
            ) from error
        if (
            len(parent_relative.parts) < 3
            or parent_relative.parts[0] != "Production"
            or parent_relative.parts[-1] != "freeze"
        ):
            raise SystemExit(
                "parent freeze must use Production/<CAMPAIGN>/freeze"
            )
        canonical_path = root / "tools/canonical_manifest.py"
        specification = importlib.util.spec_from_file_location(
            "expansion_parent_canonical_contract", canonical_path
        )
        if specification is None or specification.loader is None:
            raise SystemExit("cannot load canonical parent contract")
        canonical_contract = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(canonical_contract)
        with contextlib.redirect_stdout(io.StringIO()):
            canonical_contract.validate_directory(
                parent_freeze, require_seal=True
            )
        parent_summary_path = parent_freeze / "freeze_summary.json"
        parent_manifest_path = parent_freeze / "canonical_manifest.jsonl"
        parent_seal_path = parent_freeze / "freeze_seal.json"
        parent_summary = json.loads(parent_summary_path.read_text())
        parent_jobs = int(parent_summary["jobs_per_tune"])
        if parent_jobs < 100 or parent_jobs % 10:
            raise SystemExit("parent freeze is not an equal-tune ten-block sample")
        if args.campaign == parent_summary["campaign"]:
            raise SystemExit(
                "expansion campaign name must differ from its immutable parent"
            )
        if args.campaign_ordinal == int(parent_summary["campaign_ordinal"]):
            raise SystemExit(
                "expansion campaign ordinal must differ from its parent"
            )
        parent_rows = [
            json.loads(line)
            for line in parent_manifest_path.read_text().splitlines()
            if line.strip()
        ]
        candidate_slots = {
            "MONASH": additional_jobs,
            "JUNCTIONS": 2 * additional_jobs,
            "CLOSEPACKING": 2 * additional_jobs,
        }
        global_offsets = {
            "MONASH": 0,
            "JUNCTIONS": additional_jobs,
            "CLOSEPACKING": 3 * additional_jobs,
        }
        primary_limit = additional_jobs
        parent_seeds = {int(row["seed"]) for row in parent_rows}
        initial_expansion_seeds = {
            args.seed_base
            + (global_offsets[tune] + logical_id) * args.max_attempts
            for tune in TUNES
            for logical_id in range(candidate_slots[tune])
        }
        if parent_seeds & initial_expansion_seeds:
            raise SystemExit(
                "expansion attempt-zero seeds overlap the canonical parent"
            )
        expansion_fields = {
            "campaign_kind": EQUAL_TUNE_EXPANSION_KIND,
            "planned_additional_jobs_per_tune": additional_jobs,
            "planned_final_jobs_per_tune": parent_jobs + additional_jobs,
            "supersedes": {
                "campaign": parent_summary["campaign"],
                "campaign_ordinal": int(parent_summary["campaign_ordinal"]),
                "jobs_per_tune": parent_jobs,
                "canonical_manifest_sha256": sha256(parent_manifest_path),
                "freeze_summary_sha256": sha256(parent_summary_path),
                "freeze_seal_sha256": sha256(parent_seal_path),
                "freeze_path": parent_relative.as_posix(),
            },
            "final_block_contract":
                "canonical_slot_modulo_10_over_complete_union_v1",
            "extension_selection_rule":
                "lowest_canonical_slots_after_technical_freeze_v1",
        }
    campaign = {
        "schema": "hf_campaign_v1",
        "campaign": args.campaign,
        "campaign_ordinal": args.campaign_ordinal,
        "requested_successes_per_job": args.events,
        "seed_base": args.seed_base,
        "max_attempts_per_logical_id": args.max_attempts,
        "pythia_seed_domain": [1, 900_000_000],
        "candidate_slots": candidate_slots,
        "global_offsets": global_offsets,
        "canonical_first_stage_jobs_per_tune": 100,
        "canonical_first_stage_successes_per_tune": 100 * args.events,
        "species_registry_sha256": sha256(species),
        "pair_registry_sha256": sha256(pairs),
        "tune_allowlist_sha256": sha256(tune_allowlist),
        "pthat_sensitivity_spec_sha256": sha256(pthat_spec),
        "card_sha256": {tune: sha256(path) for tune, path in cards.items()},
        "selector": "hard_trigger_primary_ground__primary_ground_associate_v1",
        "raw_schema": "hf_primary_ground_raw_v6",
        "origin_algorithm":
            "signed_heavy_constituent_complete_mothers_unique_v4",
        "block_count": 10,
        "repository_commit": repository_commit,
        "repository_dirty_at_generation": repository_dirty,
        **expansion_fields,
    }
    candidates = []
    seeds = set()
    for tune in TUNES:
        for logical_id in range(candidate_slots[tune]):
            role = "primary" if logical_id < primary_limit else "reserve"
            seed = (
                args.seed_base
                + (global_offsets[tune] + logical_id) * args.max_attempts
            )
            if not 1 <= seed <= 900_000_000:
                raise ValueError(f"seed {seed} outside PYTHIA domain")
            if seed in seeds:
                raise AssertionError(f"seed collision {seed}")
            seeds.add(seed)
            candidates.append(
                {
                    "campaign": args.campaign,
                    "campaign_ordinal": args.campaign_ordinal,
                    "tune": tune,
                    "logical_id": logical_id,
                    "global_candidate_ordinal": (
                        global_offsets[tune] + logical_id
                    ),
                    "role": role,
                    "attempt": 0,
                    "seed": seed,
                    "requested_successes": args.events,
                    "pthat_min_override": "NONE",
                    "multiplicity_audit_events": 0,
                    "repository_commit": repository_commit,
                    "effective_card_sha256": effective_card_sha256(
                        cards[tune], args.events, "NONE"
                    ),
                    "stable_name": f"hf_{tune}_job{logical_id:03d}.root",
                }
            )
    campaign_text = json.dumps(campaign, indent=2, sort_keys=True) + "\n"
    candidate_text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in candidates)
    ledger_text = "".join(
        json.dumps(
            {
                "campaign": row["campaign"],
                "tune": row["tune"],
                "logical_id": row["logical_id"],
                "attempt": row["attempt"],
                "seed": row["seed"],
                "allocation": "initial",
            },
            sort_keys=True,
        )
        + "\n"
        for row in candidates
    )
    atomic_write(campaign_dir / "campaign.json", campaign_text)
    atomic_write(campaign_dir / "candidate_manifest.jsonl", candidate_text)
    atomic_write(campaign_dir / "seed_ledger.jsonl", ledger_text)
    print(f"generated {len(candidates)} candidates and {len(seeds)} unique seeds in {campaign_dir}")
    return validate_campaign(campaign_dir)


def generate_expansion(args: argparse.Namespace) -> int:
    if args.parent_freeze is None:
        raise SystemExit("generate-expansion requires --parent-freeze")
    return generate(args)


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def validate_seed_ledger(candidates: list[dict], ledger: list[dict]) -> set[int]:
    candidate_allocations = {
        (
            row["campaign"],
            row["tune"],
            int(row["logical_id"]),
            int(row["attempt"]),
            int(row["seed"]),
        )
        for row in candidates
    }
    ledger_allocations = {
        (
            row["campaign"],
            row["tune"],
            int(row["logical_id"]),
            int(row["attempt"]),
            int(row["seed"]),
        )
        for row in ledger
    }
    if len(ledger_allocations) != len(ledger):
        raise ValueError("duplicate seed-ledger allocation")
    if candidate_allocations - ledger_allocations:
        raise ValueError("candidate without matching seed-ledger allocation")
    seeds = {int(row["seed"]) for row in ledger}
    if len(seeds) != len(ledger):
        raise ValueError("duplicate allocated seed")
    if any(seed < 1 or seed > 900_000_000 for seed in seeds):
        raise ValueError("seed outside PYTHIA domain")
    return seeds


def validate_gate_b_campaign(
    campaign_dir: Path,
    checkout_root: Path,
    config: dict,
    candidates: list[dict],
    ledger: list[dict],
    implementation_policy: str,
) -> int:
    root = checkout_root.resolve()
    expected_campaign_dir = root / "campaigns" / config["campaign"]
    if campaign_dir.resolve() != expected_campaign_dir:
        raise ValueError(
            "Gate-B campaign must be read from the validated checkout: "
            f"{campaign_dir.resolve()} != {expected_campaign_dir}"
        )
    expected_contract = {
        "raw_schema": "hf_primary_ground_raw_v6",
        "selector": "hard_trigger_primary_ground__primary_ground_associate_v1",
        "origin_algorithm":
            "signed_heavy_constituent_complete_mothers_unique_v4",
    }
    for key, expected_value in expected_contract.items():
        if config.get(key) != expected_value:
            raise ValueError(
                f"Gate-B contract mismatch {key}: "
                f"{config.get(key)!r} != {expected_value!r}"
            )
    expected_hashes = {
        "species_registry_sha256":
            sha256(root / "config/heavy_flavour_species_v1.json"),
        "pair_registry_sha256":
            sha256(root / "config/heavy_flavour_pair_registry_v1.json"),
        "tune_allowlist_sha256":
            sha256(root / "config/tune_difference_allowlist_v1.json"),
        "pthat_sensitivity_spec_sha256":
            sha256(root / "config/pthat_sensitivity_v1.json"),
    }
    for key, expected_value in expected_hashes.items():
        if config.get(key) != expected_value:
            raise ValueError(f"Gate-B {key} differs from checkout")
    for tune in TUNES:
        card = root / "SimulationScripts" / (
            f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
        )
        if config.get("card_sha256", {}).get(tune) != sha256(card):
            raise ValueError(f"Gate-B card checksum differs for {tune}")
    if config.get("repository_dirty_at_generation") is not False:
        raise ValueError("Gate-B campaign was not generated from a clean checkout")
    current_commit = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    implementation_commit = config.get(
        "repository_commit", config.get("repository_implementation_commit")
    )
    legacy_implementation_commit = config.get("repository_implementation_commit")
    if (
        legacy_implementation_commit is not None
        and legacy_implementation_commit != implementation_commit
    ):
        raise ValueError(
            "Gate-B repository_commit and repository_implementation_commit differ"
        )
    if not isinstance(implementation_commit, str) or not GIT_COMMIT.fullmatch(
        implementation_commit
    ):
        raise ValueError("Gate-B repository commit is not a lowercase 40-hex SHA")
    if implementation_policy == "exact" and implementation_commit != current_commit:
        raise ValueError("Gate-B implementation commit differs from current checkout")
    if implementation_policy == "ancestor":
        ancestry = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "merge-base",
                "--is-ancestor",
                str(implementation_commit),
                current_commit,
            ],
            check=False,
        )
        if ancestry.returncode != 0:
            raise ValueError(
                "Gate-B implementation commit is not an ancestor of checkout"
            )
    expected = int(config.get("pilot_jobs", -1))
    if expected != len(TUNES) * len(GATE_B_PROFILES) or len(candidates) != expected:
        raise ValueError(
            f"Gate-B candidate count {len(candidates)} != expected {len(TUNES) * len(GATE_B_PROFILES)}"
        )
    if len(ledger) != expected:
        raise ValueError(f"Gate-B ledger count {len(ledger)} != {expected}")
    identities = {
        (row["tune"], int(row["logical_id"]), int(row["attempt"]))
        for row in candidates
    }
    if len(identities) != expected:
        raise ValueError("duplicate Gate-B candidate identity")
    seeds = validate_seed_ledger(candidates, ledger)
    for tune_index, tune in enumerate(TUNES):
        rows = {
            int(row["logical_id"]): row
            for row in candidates
            if row["tune"] == tune
        }
        if set(rows) != set(GATE_B_PROFILES):
            raise ValueError(f"wrong Gate-B profiles for {tune}")
        for logical_id, (pthat, events, category, purpose) in GATE_B_PROFILES.items():
            row = rows[logical_id]
            expected_seed = (
                int(config["seed_base"]) + tune_index * 10_000 + logical_id * 1_000
            )
            expected_fields = {
                "campaign": config["campaign"],
                "campaign_ordinal": int(config["campaign_ordinal"]),
                "role": "pilot",
                "attempt": 0,
                "seed": expected_seed,
                "requested_successes": events,
                "pthat_min_override": pthat,
                "category": category,
                "purpose": purpose,
                "multiplicity_audit_events": 100,
                "stable_name": f"hf_{tune}_job{logical_id:03d}.root",
                "repository_commit": implementation_commit,
                "effective_card_sha256": effective_card_sha256(
                    root
                    / "SimulationScripts"
                    / f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd",
                    events,
                    pthat,
                ),
            }
            for key, expected_value in expected_fields.items():
                if row.get(key) != expected_value:
                    raise ValueError(
                        f"Gate-B field mismatch {tune}/{logical_id} {key}: "
                        f"{row.get(key)!r} != {expected_value!r}"
                    )
    print(
        f"Gate-B campaign valid: candidates={len(candidates)} "
        f"allocations={len(ledger)} unique_seeds={len(seeds)}"
    )
    return 0


def validate_full_campaign(
    campaign_dir: Path,
    checkout_root: Path,
    config: dict,
    candidates: list[dict],
    ledger: list[dict],
    implementation_policy: str,
) -> int:
    root = checkout_root.resolve()
    expected_campaign_dir = root / "campaigns" / config["campaign"]
    if campaign_dir.resolve() != expected_campaign_dir:
        raise ValueError(
            "full campaign must be read from the validated checkout: "
            f"{campaign_dir.resolve()} != {expected_campaign_dir}"
        )
    expected_contract = {
        "raw_schema": "hf_primary_ground_raw_v6",
        "selector": "hard_trigger_primary_ground__primary_ground_associate_v1",
        "origin_algorithm":
            "signed_heavy_constituent_complete_mothers_unique_v4",
    }
    for key, expected_value in expected_contract.items():
        if config.get(key) != expected_value:
            raise ValueError(
                f"full-campaign contract mismatch {key}: "
                f"{config.get(key)!r} != {expected_value!r}"
            )
    maximum_attempts = config.get("max_attempts_per_logical_id")
    if (
        isinstance(maximum_attempts, bool)
        or not isinstance(maximum_attempts, int)
        or not 1 <= maximum_attempts <= MAX_ATTEMPTS_PER_LOGICAL_ID
    ):
        raise ValueError(
            "full-campaign max_attempts_per_logical_id must be in "
            "[1,4096] for the 12-bit event-ID field"
        )
    expected_hashes = {
        "species_registry_sha256":
            sha256(root / "config/heavy_flavour_species_v1.json"),
        "pair_registry_sha256":
            sha256(root / "config/heavy_flavour_pair_registry_v1.json"),
        "tune_allowlist_sha256":
            sha256(root / "config/tune_difference_allowlist_v1.json"),
        "pthat_sensitivity_spec_sha256":
            sha256(root / "config/pthat_sensitivity_v1.json"),
    }
    for key, expected_value in expected_hashes.items():
        if config.get(key) != expected_value:
            raise ValueError(f"full-campaign {key} differs from checkout")
    cards = {
        tune: root
        / "SimulationScripts"
        / f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
        for tune in TUNES
    }
    for tune, card in cards.items():
        if config.get("card_sha256", {}).get(tune) != sha256(card):
            raise ValueError(f"full-campaign card checksum differs for {tune}")

    implementation_commit = config.get("repository_commit")
    current_commit = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    if (
        not isinstance(implementation_commit, str)
        or not GIT_COMMIT.fullmatch(implementation_commit)
    ):
        raise ValueError("full-campaign repository commit is invalid")
    if implementation_policy == "exact" and implementation_commit != current_commit:
        raise ValueError(
            "full-campaign implementation commit differs from current checkout"
        )
    if implementation_policy == "ancestor":
        ancestry = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "merge-base",
                "--is-ancestor",
                implementation_commit,
                current_commit,
            ],
            check=False,
        )
        if ancestry.returncode != 0:
            raise ValueError(
                "full-campaign implementation commit is not an ancestor of checkout"
            )
    if config.get("repository_dirty_at_generation") is not False:
        raise ValueError("full campaign was not generated from a clean checkout")
    campaign_kind = config.get("campaign_kind")
    expansion_keys = {
        "planned_additional_jobs_per_tune",
        "planned_final_jobs_per_tune",
        "supersedes",
        "final_block_contract",
        "extension_selection_rule",
    }
    if campaign_kind is None:
        unexpected = expansion_keys & set(config)
        if unexpected:
            raise ValueError(
                "first-stage campaign contains partial expansion metadata"
            )
    elif campaign_kind == EQUAL_TUNE_EXPANSION_KIND:
        additional_jobs = config.get("planned_additional_jobs_per_tune")
        parent = config.get("supersedes")
        if (
            isinstance(additional_jobs, bool)
            or not isinstance(additional_jobs, int)
            or not 10 <= additional_jobs <= 100
            or additional_jobs % 10
            or not isinstance(parent, dict)
            or config.get("final_block_contract")
            != "canonical_slot_modulo_10_over_complete_union_v1"
            or config.get("extension_selection_rule")
            != "lowest_canonical_slots_after_technical_freeze_v1"
        ):
            raise ValueError("equal-tune expansion metadata is malformed")
        parent_path_value = parent.get("freeze_path")
        if (
            not isinstance(parent_path_value, str)
            or Path(parent_path_value).is_absolute()
            or ".." in Path(parent_path_value).parts
        ):
            raise ValueError("expansion parent freeze path is unsafe")
        parent_freeze = root / parent_path_value
        if (
            parent_freeze.is_symlink()
            or not parent_freeze.is_dir()
            or parent_freeze.name != "freeze"
        ):
            raise ValueError("expansion parent freeze is absent")
        canonical_path = root / "tools/canonical_manifest.py"
        specification = importlib.util.spec_from_file_location(
            "validated_expansion_parent_contract", canonical_path
        )
        if specification is None or specification.loader is None:
            raise ValueError("cannot load canonical parent contract")
        canonical_contract = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(canonical_contract)
        with contextlib.redirect_stdout(io.StringIO()):
            canonical_contract.validate_directory(
                parent_freeze, require_seal=True
            )
        parent_summary_path = parent_freeze / "freeze_summary.json"
        parent_manifest_path = parent_freeze / "canonical_manifest.jsonl"
        parent_seal_path = parent_freeze / "freeze_seal.json"
        parent_summary = json.loads(parent_summary_path.read_text())
        parent_jobs = int(parent_summary["jobs_per_tune"])
        expected_parent = {
            "campaign": parent_summary["campaign"],
            "campaign_ordinal": int(parent_summary["campaign_ordinal"]),
            "jobs_per_tune": parent_jobs,
            "canonical_manifest_sha256": sha256(parent_manifest_path),
            "freeze_summary_sha256": sha256(parent_summary_path),
            "freeze_seal_sha256": sha256(parent_seal_path),
            "freeze_path": str(Path(parent_path_value)),
        }
        for key, value in expected_parent.items():
            if parent.get(key) != value:
                raise ValueError(
                    f"expansion parent binding differs: {key}"
                )
        if (
            parent_summary["campaign"] == config["campaign"]
            or int(parent_summary["campaign_ordinal"])
            == int(config["campaign_ordinal"])
            or parent_jobs < 100
            or parent_jobs % 10
            or config.get("planned_final_jobs_per_tune")
            != parent_jobs + additional_jobs
        ):
            raise ValueError("expansion campaign/final exposure differs")
    else:
        raise ValueError(f"unsupported full campaign kind {campaign_kind!r}")
    requested_successes = config.get("requested_successes_per_job")
    if (
        isinstance(requested_successes, bool)
        or not isinstance(requested_successes, int)
        or not 1 <= requested_successes <= 1_048_575
    ):
        raise ValueError("invalid requested_successes_per_job")

    campaign_slots, campaign_offsets, primary_limit = campaign_slot_contract(
        config
    )
    expected = sum(campaign_slots.values())
    if len(candidates) != expected:
        raise ValueError(f"candidate count {len(candidates)} != {expected}")
    identities = {
        (row["tune"], int(row["logical_id"]), int(row["attempt"]))
        for row in candidates
    }
    if len(identities) != expected:
        raise ValueError("duplicate candidate identity")
    seeds = validate_seed_ledger(candidates, ledger)
    if campaign_kind == EQUAL_TUNE_EXPANSION_KIND:
        parent_freeze = root / config["supersedes"]["freeze_path"]
        parent_rows = load_jsonl(parent_freeze / "canonical_manifest.jsonl")
        parent_seeds = {int(row["seed"]) for row in parent_rows}
        if seeds & parent_seeds:
            raise ValueError(
                "equal-tune expansion seed ledger overlaps its canonical parent"
            )
    attempts_by_logical: dict[tuple[str, int], set[int]] = {}
    if any(int(row.get("attempt", -1)) > 0 for row in ledger):
        verify_full_initial_reservation(root, campaign_dir, config)
    for allocation in ledger:
        tune = allocation.get("tune")
        logical_id = allocation.get("logical_id")
        attempt = allocation.get("attempt")
        seed = allocation.get("seed")
        if (
            tune not in TUNES
            or isinstance(logical_id, bool)
            or not isinstance(logical_id, int)
            or not 0 <= logical_id < campaign_slots[tune]
            or isinstance(attempt, bool)
            or not isinstance(attempt, int)
            or not 0 <= attempt < int(config["max_attempts_per_logical_id"])
            or isinstance(seed, bool)
            or not isinstance(seed, int)
        ):
            raise ValueError("full seed-ledger allocation fields are invalid")
        expected_allocation_seed = campaign_logical_seed(
            config, tune, logical_id, attempt
        )
        if seed != expected_allocation_seed:
            raise ValueError(
                f"full retry seed mapping differs for "
                f"{tune}/{logical_id}/attempt{attempt}"
            )
        if attempt == 0:
            if allocation.get("allocation") != "initial":
                raise ValueError("attempt-zero allocation is not marked initial")
        else:
            reason = allocation.get("reason")
            prior_evidence = allocation.get("prior_attempt_evidence")
            if (
                allocation.get("allocation") != "retry"
                or not isinstance(reason, str)
                or not reason.strip()
                or len(reason) > 500
                or not isinstance(prior_evidence, dict)
                or prior_evidence.get("kind")
                not in {
                    "producer_failure",
                    "raw_validation_fail",
                    "scheduler_loss_approval",
                }
                or not isinstance(prior_evidence.get("path"), str)
                or not SHA256.fullmatch(
                    str(prior_evidence.get("sha256", ""))
                )
            ):
                raise ValueError(
                    "retry allocation lacks marker, reason, or prior evidence"
                )
            verify_retry_eligibility(
                root,
                config,
                tune,
                logical_id,
                attempt,
                recorded_evidence=prior_evidence,
            )
        attempts_by_logical.setdefault((tune, logical_id), set()).add(attempt)
    for (tune, logical_id), attempts in attempts_by_logical.items():
        if attempts != set(range(max(attempts) + 1)):
            raise ValueError(
                f"non-contiguous retry attempts for {tune}/{logical_id}: "
                f"{sorted(attempts)}"
            )
    for tune in TUNES:
        rows = [row for row in candidates if row["tune"] == tune]
        if len(rows) != campaign_slots[tune]:
            raise ValueError(f"wrong slot count for {tune}")
        logical_ids = {int(row["logical_id"]) for row in rows}
        if logical_ids != set(range(campaign_slots[tune])):
            raise ValueError(f"full-campaign logical-ID coverage differs for {tune}")
        for row in rows:
            logical_id = int(row["logical_id"])
            expected_seed = campaign_logical_seed(
                config, tune, logical_id, int(row["attempt"])
            )
            expected_fields = {
                "global_candidate_ordinal":
                    campaign_offsets[tune] + logical_id,
                "role": (
                    "primary" if logical_id < primary_limit else "reserve"
                ),
                "attempt": 0,
                "seed": expected_seed,
                "requested_successes": requested_successes,
                "pthat_min_override": "NONE",
                "multiplicity_audit_events": 0,
                "repository_commit": implementation_commit,
                "effective_card_sha256": effective_card_sha256(
                    cards[tune], requested_successes, "NONE"
                ),
                "stable_name": f"hf_{tune}_job{logical_id:03d}.root",
            }
            for key, expected_value in expected_fields.items():
                if row.get(key) != expected_value:
                    raise ValueError(
                        f"full-campaign field mismatch {tune}/{logical_id} "
                        f"{key}: {row.get(key)!r} != {expected_value!r}"
                    )
            if int(row["seed"]) != expected_seed:
                raise ValueError(f"seed mapping mismatch: {row}")
    print(
        f"campaign valid: candidates={len(candidates)} allocations={len(ledger)} "
        f"unique_seeds={len(seeds)}"
    )
    return 0


def validate_campaign(
    campaign_dir: Path,
    implementation_policy: str = "exact",
    checkout_root: Path | None = None,
) -> int:
    checkout = (
        checkout_root.resolve()
        if checkout_root is not None
        else campaign_dir.parents[1]
    )
    config = json.loads((campaign_dir / "campaign.json").read_text())
    candidates = load_jsonl(campaign_dir / "candidate_manifest.jsonl")
    ledger = load_jsonl(campaign_dir / "seed_ledger.jsonl")
    validate_pthat_spec_preapproval(
        checkout,
        config.get(
            "repository_commit",
            config.get("repository_implementation_commit"),
        ),
    )
    validate_campaign_identity(campaign_dir, config, candidates, ledger)
    schema = config.get("schema")
    if schema == "hf_gate_b_pilot_campaign_v1":
        return validate_gate_b_campaign(
            campaign_dir,
            checkout,
            config,
            candidates,
            ledger,
            implementation_policy,
        )
    if schema == "hf_campaign_v1":
        return validate_full_campaign(
            campaign_dir,
            checkout,
            config,
            candidates,
            ledger,
            implementation_policy,
        )
    raise ValueError(f"unsupported campaign schema {schema!r}")


def validate(args: argparse.Namespace) -> int:
    return validate_campaign(
        args.campaign_dir.resolve(),
        args.implementation_policy,
        args.checkout_root,
    )


def allocate_retry(args: argparse.Namespace) -> int:
    campaign_dir = args.campaign_dir.resolve()
    checkout_root = campaign_dir.parents[1]
    with contextlib.redirect_stdout(io.StringIO()):
        validate_campaign(
            campaign_dir,
            implementation_policy="exact",
            checkout_root=checkout_root,
        )
    config = json.loads((campaign_dir / "campaign.json").read_text())
    if config.get("schema") != "hf_campaign_v1":
        raise ValueError("retry allocation requires a full campaign")
    if not isinstance(args.reason, str) or not args.reason.strip():
        raise ValueError("retry reason must be nonempty")
    if len(args.reason) > 500:
        raise ValueError("retry reason exceeds 500 characters")
    allowed_ledger = str(
        (campaign_dir / "seed_ledger.jsonl").relative_to(checkout_root)
    )
    require_tracked_clean(checkout_root, {allowed_ledger})
    verify_full_initial_reservation(checkout_root, campaign_dir, config)
    ledger_path = campaign_dir / "seed_ledger.jsonl"
    lock_path = campaign_dir / ".seed_ledger.lock"
    with locked_regular_file(lock_path):
        ledger = load_jsonl(ledger_path)
        attempts = [
            int(row["attempt"]) for row in ledger
            if row["tune"] == args.tune and int(row["logical_id"]) == args.logical_id
        ]
        attempt = max(attempts, default=-1) + 1
        seed = campaign_logical_seed(
            config, args.tune, args.logical_id, attempt
        )
        prior_evidence = verify_retry_eligibility(
            checkout_root,
            config,
            args.tune,
            args.logical_id,
            attempt,
            scheduler_loss_approval=args.scheduler_loss_approval,
        )
        if any(int(row["seed"]) == seed for row in ledger):
            raise ValueError(f"seed collision for {seed}")
        row = {
            "campaign": config["campaign"],
            "tune": args.tune,
            "logical_id": args.logical_id,
            "attempt": attempt,
            "seed": seed,
            "allocation": "retry",
            "reason": args.reason.strip(),
            "prior_attempt_evidence": prior_evidence,
        }
        with ledger_path.open("a") as stream:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        with contextlib.redirect_stdout(io.StringIO()):
            validate_campaign(
                campaign_dir,
                implementation_policy="exact",
                checkout_root=checkout_root,
            )
    print(json.dumps(row, sort_keys=True))
    return 0


def authorize(args: argparse.Namespace) -> int:
    campaign_dir = args.campaign_dir.resolve()
    checkout_root = args.checkout_root.resolve()
    with contextlib.redirect_stdout(io.StringIO()):
        validate_campaign(
            campaign_dir,
            implementation_policy="exact",
            checkout_root=checkout_root,
        )
    config = json.loads((campaign_dir / "campaign.json").read_text())
    candidates = load_jsonl(campaign_dir / "candidate_manifest.jsonl")
    ledger = load_jsonl(campaign_dir / "seed_ledger.jsonl")
    candidate = next(
        (
            row
            for row in candidates
            if row["tune"] == args.tune
            and int(row["logical_id"]) == args.logical_id
        ),
        None,
    )
    allocation = next(
        (
            row
            for row in ledger
            if row["tune"] == args.tune
            and int(row["logical_id"]) == args.logical_id
            and int(row["attempt"]) == args.attempt
            and int(row["seed"]) == args.seed
        ),
        None,
    )
    if candidate is None or allocation is None:
        raise ValueError("logical attempt/seed is not manifest and ledger authorized")
    if (
        config["campaign"] != args.campaign
        or campaign_dir.name != args.campaign
        or candidate["campaign"] != args.campaign
        or candidate["role"] != args.role
    ):
        raise ValueError("campaign or role differs from candidate manifest")
    if (
        int(config["campaign_ordinal"]) != args.campaign_ordinal
        or int(candidate["campaign_ordinal"]) != args.campaign_ordinal
    ):
        raise ValueError("campaign ordinal differs from manifest")
    if int(candidate["requested_successes"]) != args.requested_successes:
        raise ValueError("requested success count differs from candidate manifest")
    manifest_pthat = str(candidate.get("pthat_min_override", "NONE"))
    if manifest_pthat in {"", "None"}:
        manifest_pthat = "NONE"
    if manifest_pthat != args.pthat_min_override:
        raise ValueError("pTHat override differs from candidate manifest")
    manifest_audit = int(candidate.get("multiplicity_audit_events", 0))
    if manifest_audit != args.multiplicity_audit_events:
        raise ValueError(
            "multiplicity audit event count differs from candidate manifest"
        )

    current_commit = subprocess.check_output(
        ["git", "-C", str(checkout_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if (
        args.repository_commit != current_commit
        or (
            candidate.get("repository_commit") is not None
            and candidate["repository_commit"] != current_commit
        )
    ):
        raise ValueError("runtime repository commit differs from authorized commit")
    allowed_tracked_changes: set[str] = set()
    if config.get("schema") == "hf_campaign_v1":
        allowed_tracked_changes.add(
            str(
                (campaign_dir / "seed_ledger.jsonl").relative_to(
                    checkout_root
                )
            )
        )
    require_tracked_clean(checkout_root, allowed_tracked_changes)

    card = checkout_root / "SimulationScripts" / (
        f"pythiasettings_Hard_Low_ccbb_{args.tune}.cmnd"
    )
    computed_effective_sha = effective_card_sha256(
        card,
        args.requested_successes,
        args.pthat_min_override,
    )
    if (
        args.effective_card_sha256 != computed_effective_sha
        or (
            candidate.get("effective_card_sha256") is not None
            and candidate["effective_card_sha256"] != computed_effective_sha
        )
    ):
        raise ValueError("effective card SHA-256 differs from authorized bytes")

    producer = (
        checkout_root / "SimulationScripts" / "heavyflavourcorrelations_status"
    )
    if not producer.is_file() or not os.access(producer, os.X_OK):
        raise ValueError(f"producer executable is absent or not executable: {producer}")
    if (
        not SHA256.fullmatch(args.producer_executable_sha256)
        or sha256(producer) != args.producer_executable_sha256
    ):
        raise ValueError("producer executable SHA-256 differs from runtime binary")
    if args.require_submission_claim:
        submission_kind = next(
            (
                name
                for name, row in SUBMISSION_KINDS.items()
                if row["campaign_schema"] == config.get("schema")
            ),
            None,
        )
        if submission_kind is None:
            raise ValueError("campaign schema has no submission-claim contract")
        submission = SUBMISSION_KINDS[submission_kind]
        retry_mode = submission_kind == "full" and args.attempt > 0
        if retry_mode:
            retry_stem = (
                f"{args.tune}_job{args.logical_id:03d}_"
                f"attempt{args.attempt:03d}"
            )
            claim_path = (
                checkout_root
                / "Production"
                / args.campaign
                / "submission_receipts"
                / "retries"
                / f"{retry_stem}_claim.json"
            )
        else:
            claim_path = (
                checkout_root
                / "Production"
                / args.campaign
                / "submission_receipts"
                / submission["claim_file"]
            )
        if claim_path.is_symlink() or not claim_path.is_file():
            raise ValueError(f"required submission claim is absent: {claim_path}")
        claim = json.loads(claim_path.read_text())
        expected_claim_fields = {
            "schema": (
                "hf_full_retry_submission_claim_v1"
                if retry_mode
                else submission["claim_schema"]
            ),
            "state": "claimed_before_condor_submit",
            "submission_kind": (
                "full_retry" if retry_mode else submission_kind
            ),
            "campaign": args.campaign,
            "campaign_ordinal": args.campaign_ordinal,
            "repository_commit": args.repository_commit,
            "producer_executable_sha256": args.producer_executable_sha256,
            "repository_identity": repository_identity(checkout_root),
            "campaign_json_sha256": sha256(campaign_dir / "campaign.json"),
            "candidate_manifest_sha256": sha256(
                campaign_dir / "candidate_manifest.jsonl"
            ),
        }
        if submission_kind == "full" and not retry_mode:
            signoff = campaign_dir / "PHYSICS_ORIGIN_SIGNOFF.json"
            if signoff.is_symlink() or not signoff.is_file():
                raise ValueError("full-production physics sign-off is absent")
            expected_claim_fields["physics_origin_signoff_sha256"] = sha256(
                signoff
            )
            gate_authorization = (
                campaign_dir / "FULL_PRODUCTION_GATE_AUTHORIZATION.json"
            )
            if (
                gate_authorization.is_symlink()
                or not gate_authorization.is_file()
            ):
                raise ValueError(
                    "full-production gate authorization is absent"
                )
            gate_reports = validate_gate_authorization(
                gate_authorization, checkout_root, config, signoff
            )
            if (
                gate_reports["gate_a"]["environment"][
                    "producer_executable_sha256"
                ]
                != args.producer_executable_sha256
            ):
                raise ValueError(
                    "submission producer differs from the Gate-A rebuilt binary"
                )
            expected_claim_fields[
                "full_production_gate_authorization_sha256"
            ] = sha256(gate_authorization)
            if config.get("campaign_kind") == EQUAL_TUNE_EXPANSION_KIND:
                expansion_authorization = (
                    campaign_dir
                    / "EQUAL_TUNE_EXPANSION_AUTHORIZATION.json"
                )
                validate_expansion_authorization(
                    expansion_authorization, checkout_root, config
                )
                expected_claim_fields[
                    "equal_tune_expansion_authorization_sha256"
                ] = sha256(expansion_authorization)
        for key, expected_value in expected_claim_fields.items():
            if claim.get(key) != expected_value:
                raise ValueError(f"submission claim {key} differs")
        ledger_path = campaign_dir / "seed_ledger.jsonl"
        if submission_kind == "full":
            claimed_prefix_bytes = claim.get("seed_ledger_prefix_bytes")
            if (
                isinstance(claimed_prefix_bytes, bool)
                or not isinstance(claimed_prefix_bytes, int)
                or claimed_prefix_bytes < 1
            ):
                raise ValueError(
                    "full submission claim seed-ledger prefix length is invalid"
                )
            current_ledger = ledger_path.read_bytes()
            if len(current_ledger) < claimed_prefix_bytes:
                raise ValueError(
                    "full seed ledger is shorter than the claimed immutable prefix"
                )
            claimed_prefix_sha = hashlib.sha256(
                current_ledger[:claimed_prefix_bytes]
            ).hexdigest()
            if claim.get("seed_ledger_sha256") != claimed_prefix_sha:
                raise ValueError(
                    "full seed-ledger immutable prefix differs from submission claim"
                )
        elif claim.get("seed_ledger_sha256") != sha256(ledger_path):
            raise ValueError("Gate-B seed ledger differs from submission claim")
        if retry_mode:
            initial_claim = verify_full_initial_reservation(
                checkout_root, campaign_dir, config
            )
            if claim.get("initial_submission_claim_sha256") != sha256(
                checkout_root
                / "Production"
                / args.campaign
                / "submission_receipts"
                / submission["claim_file"]
            ):
                raise ValueError(
                    "retry claim does not bind the initial full reservation"
                )
            if (
                claim.get("producer_executable_sha256")
                != initial_claim.get("producer_executable_sha256")
            ):
                raise ValueError(
                    "retry producer differs from initial full reservation"
                )
            submit_file = (
                checkout_root
                / "Production"
                / args.campaign
                / "retry_submissions"
                / f"submit_{retry_stem}.sub"
            )
        else:
            submit_file = (
                checkout_root
                / "Production"
                / args.campaign
                / submission["submit_file"]
            )
        if (
            submit_file.is_symlink()
            or not submit_file.is_file()
            or claim.get("submit_file_sha256") != sha256(submit_file)
        ):
            raise ValueError("submission claim submit-file checksum differs")
        if retry_mode:
            allocation = claim.get("allocation")
            if (
                not isinstance(allocation, dict)
                or allocation.get("tune") != args.tune
                or int(allocation.get("logical_id", -1)) != args.logical_id
                or int(allocation.get("attempt", -1)) != args.attempt
                or int(allocation.get("seed", -1)) != args.seed
            ):
                allocation = None
        else:
            allocation = next(
                (
                    row
                    for row in claim.get("allocations", [])
                    if row.get("tune") == args.tune
                    and int(row.get("logical_id", -1)) == args.logical_id
                    and int(row.get("attempt", -1)) == args.attempt
                    and int(row.get("seed", -1)) == args.seed
                ),
                None,
            )
        if allocation is None:
            raise ValueError("runtime allocation is absent from submission claim")
        expected_allocation = {
            "campaign_ordinal": args.campaign_ordinal,
            "pthat_min_override": args.pthat_min_override,
            "multiplicity_audit_events": args.multiplicity_audit_events,
            "repository_commit": args.repository_commit,
            "effective_card_sha256": args.effective_card_sha256,
        }
        if retry_mode:
            expected_allocation.update(
                {
                    "role": args.role,
                    "requested_successes": args.requested_successes,
                }
            )
        for key, expected_value in expected_allocation.items():
            if allocation.get(key) != expected_value:
                raise ValueError(
                    f"submission allocation {key} differs"
                )
        if args.cluster_id is None or args.process_id is None:
            raise ValueError(
                "submission-bound authorization requires ClusterId and ProcId"
            )
        verify_scheduler_submission_binding(
            checkout_root,
            config,
            tune=args.tune,
            logical_id=args.logical_id,
            attempt=args.attempt,
            seed=args.seed,
            cluster_id=args.cluster_id,
            process_id=args.process_id,
        )
    elif args.cluster_id is not None or args.process_id is not None:
        raise ValueError(
            "scheduler identity is accepted only with --require-submission-claim"
        )
    print(
        "CAMPAIGN_ALLOCATION_AUTHORIZED "
        f"campaign={args.campaign} tune={args.tune} logical_id={args.logical_id} "
        f"attempt={args.attempt} seed={args.seed} "
        f"campaign_ordinal={args.campaign_ordinal} "
        f"pthat_min_override={args.pthat_min_override} "
        f"multiplicity_audit_events={args.multiplicity_audit_events} "
        f"repository_commit={args.repository_commit} "
        f"effective_card_sha256={args.effective_card_sha256} "
        f"producer_executable_sha256={args.producer_executable_sha256}"
    )
    return 0


def exclusive_write(path: Path, text: str, mode: int = 0o444) -> None:
    """Create a write-once record; an existing path is always an error."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        # A partial file intentionally remains as a fail-closed guard.
        raise


def parse_condor_terse_range(value: str, expected_count: int) -> dict:
    text = value.strip()
    match = re.fullmatch(
        r"([0-9]+)\.([0-9]+)(?:\s*-\s*([0-9]+)\.([0-9]+))?",
        text,
    )
    if match is None:
        raise ValueError("unexpected condor_submit -terse result")
    first_cluster = int(match.group(1))
    first_process = int(match.group(2))
    last_cluster = (
        int(match.group(3)) if match.group(3) is not None else first_cluster
    )
    last_process = (
        int(match.group(4)) if match.group(4) is not None else first_process
    )
    count = last_process - first_process + 1
    if (
        first_cluster != last_cluster
        or first_process != 0
        or count != expected_count
    ):
        raise ValueError(
            "condor_submit range does not cover the exact claimed queue: "
            f"expected={expected_count} got={text!r}"
        )
    return {
        "cluster_id": first_cluster,
        "first_process": first_process,
        "last_process": last_process,
        "process_count": count,
        "terse": text,
    }


def _classad_integer(row: dict, key: str) -> int:
    value = row.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Condor ClassAd {key} is not an integer")
    return value


def _expected_condor_args(
    allocation: dict, cluster_id: int, process_id: int, campaign: str
) -> str:
    return " ".join(
        (
            "--campaign",
            campaign,
            str(allocation["campaign_ordinal"]),
            str(allocation["tune"]),
            str(allocation["logical_id"]),
            str(allocation["role"]),
            str(allocation["attempt"]),
            str(allocation["seed"]),
            str(allocation["requested_successes"]),
            str(allocation["pthat_min_override"]),
            str(allocation["multiplicity_audit_events"]),
            str(allocation["repository_commit"]),
            str(allocation["effective_card_sha256"]),
            str(allocation["producer_executable_sha256"]),
            str(cluster_id),
            str(process_id),
        )
    )


def _validate_submission_classads(
    payload: dict,
    *,
    claim: dict,
    checkout_root: Path,
    condor_range: dict,
) -> None:
    executable_text = payload.get("condor_q_executable")
    executable = (
        Path(executable_text)
        if isinstance(executable_text, str)
        else Path()
    )
    executable_sha = payload.get("condor_q_executable_sha256")
    expected_command = [
        str(executable),
        str(condor_range["cluster_id"]),
        "-json",
        "-attributes",
        ",".join(CONDOR_SUBMISSION_ATTRIBUTES),
    ]
    if (
        payload.get("schema") != CONDOR_SUBMISSION_CLASSAD_SCHEMA
        or payload.get("state") != "PASS"
        or not SHA256.fullmatch(str(payload.get("claim_sha256", "")))
        or payload.get("campaign") != claim.get("campaign")
        or payload.get("campaign_ordinal")
        != claim.get("campaign_ordinal")
        or payload.get("condor_cluster_id") != condor_range["cluster_id"]
        or payload.get("condor_first_process") != condor_range["first_process"]
        or payload.get("condor_last_process") != condor_range["last_process"]
        or payload.get("condor_process_count") != condor_range["process_count"]
        or payload.get("attributes") != list(CONDOR_SUBMISSION_ATTRIBUTES)
        or not executable_text
        or not executable.is_absolute()
        or executable.name != "condor_q"
        or not SHA256.fullmatch(str(executable_sha or ""))
        or payload.get("command") != expected_command
    ):
        raise ValueError("Condor submission ClassAd evidence metadata differs")
    captured = _require_utc_timestamp(
        payload.get("captured_utc"), "Condor submission ClassAd capture"
    )
    if captured > (
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=5)
    ):
        raise ValueError("Condor submission ClassAd capture is in the future")
    raw_stdout = payload.get("raw_stdout")
    if (
        not isinstance(raw_stdout, str)
        or hashlib.sha256(raw_stdout.encode()).hexdigest()
        != payload.get("raw_stdout_sha256")
    ):
        raise ValueError("Condor submission ClassAd raw output binding differs")
    try:
        raw_rows = json.loads(raw_stdout)
    except json.JSONDecodeError as error:
        raise ValueError("Condor submission ClassAd output is not JSON") from error
    if raw_rows != payload.get("classads"):
        raise ValueError("Condor submission ClassAds differ from raw output")
    allocations = claim.get("allocations")
    if allocations is None:
        allocations = [claim.get("allocation")]
    if (
        not isinstance(allocations, list)
        or len(allocations) != condor_range["process_count"]
        or not all(isinstance(row, dict) for row in allocations)
        or not isinstance(raw_rows, list)
        or len(raw_rows) != len(allocations)
    ):
        raise ValueError("Condor ClassAd/allocation cardinality differs")
    by_process: dict[int, dict] = {}
    for row in raw_rows:
        if not isinstance(row, dict):
            raise ValueError("Condor ClassAd row is not an object")
        cluster_id = _classad_integer(row, "ClusterId")
        process_id = _classad_integer(row, "ProcId")
        if (
            cluster_id != condor_range["cluster_id"]
            or process_id in by_process
            or not condor_range["first_process"]
            <= process_id
            <= condor_range["last_process"]
        ):
            raise ValueError("Condor ClassAd scheduler identity differs")
        by_process[process_id] = row
    expected_processes = set(
        range(
            condor_range["first_process"],
            condor_range["last_process"] + 1,
        )
    )
    if set(by_process) != expected_processes:
        raise ValueError("Condor ClassAd process coverage differs")
    worker = checkout_root / "runCondorJob.sh"
    for process_id, allocation in enumerate(allocations):
        row = by_process[process_id]
        expected_strings = {
            "Cmd": str(worker),
            "Iwd": str(checkout_root),
            "Args": _expected_condor_args(
                allocation,
                condor_range["cluster_id"],
                process_id,
                claim["campaign"],
            ),
            "HFCampaign": claim["campaign"],
            "HFTune": allocation["tune"],
            "HFRole": allocation["role"],
            "HFPTHat": allocation["pthat_min_override"],
            "HFRepositoryCommit": allocation["repository_commit"],
            "HFEffectiveCardSHA256": allocation["effective_card_sha256"],
            "HFProducerExecutableSHA256":
                allocation["producer_executable_sha256"],
        }
        expected_integers = {
            "ClusterId": condor_range["cluster_id"],
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
        for key, expected in expected_strings.items():
            if row.get(key) != expected:
                raise ValueError(
                    f"Condor ClassAd {process_id} {key} differs"
                )
        for key, expected in expected_integers.items():
            if _classad_integer(row, key) != expected:
                raise ValueError(
                    f"Condor ClassAd {process_id} {key} differs"
                )


def capture_submission_classads(
    *,
    claim: dict,
    claim_path: Path,
    checkout_root: Path,
    condor_range: dict,
    output: Path,
) -> dict:
    executable = shutil.which("condor_q")
    if executable is None:
        raise ValueError("condor_q is unavailable for held-job verification")
    executable_path = Path(executable).resolve()
    if (
        executable_path.is_symlink()
        or not executable_path.is_file()
        or not os.access(executable_path, os.X_OK)
    ):
        raise ValueError("condor_q does not resolve to a regular executable")
    argv = [
        str(executable_path),
        str(condor_range["cluster_id"]),
        "-json",
        "-attributes",
        ",".join(CONDOR_SUBMISSION_ATTRIBUTES),
    ]
    result = subprocess.run(
        argv,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0 or result.stderr.strip():
        raise ValueError("condor_q failed while verifying held submission")
    try:
        rows = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError("condor_q held-submission output is not JSON") from error
    payload = {
        "schema": CONDOR_SUBMISSION_CLASSAD_SCHEMA,
        "state": "PASS",
        "captured_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "claim_path": str(claim_path.relative_to(checkout_root)),
        "claim_sha256": sha256(claim_path),
        "campaign": claim["campaign"],
        "campaign_ordinal": claim["campaign_ordinal"],
        "condor_cluster_id": condor_range["cluster_id"],
        "condor_first_process": condor_range["first_process"],
        "condor_last_process": condor_range["last_process"],
        "condor_process_count": condor_range["process_count"],
        "condor_q_executable": str(executable_path),
        "condor_q_executable_sha256": sha256(executable_path),
        "command": argv,
        "attributes": list(CONDOR_SUBMISSION_ATTRIBUTES),
        "raw_stdout": result.stdout,
        "raw_stdout_sha256": hashlib.sha256(
            result.stdout.encode()
        ).hexdigest(),
        "classads": rows,
    }
    _validate_submission_classads(
        payload,
        claim=claim,
        checkout_root=checkout_root,
        condor_range=condor_range,
    )
    exclusive_write(
        output, json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    return payload


def verify_scheduler_submission_binding(
    checkout_root: Path,
    config: dict,
    *,
    tune: str,
    logical_id: int,
    attempt: int,
    seed: int,
    cluster_id: str,
    process_id: str,
) -> dict:
    """Bind a worker allocation to the immutable successful submit receipt."""
    if (
        not re.fullmatch(r"[0-9]+", cluster_id)
        or not re.fullmatch(r"[0-9]+", process_id)
    ):
        raise ValueError("scheduler identity must be numeric ClusterId/ProcId")
    cluster = int(cluster_id)
    process = int(process_id)
    if cluster < 0 or process < 0:
        raise ValueError("scheduler identity is negative")
    submission_kind = next(
        (
            kind
            for kind, contract in SUBMISSION_KINDS.items()
            if contract["campaign_schema"] == config.get("schema")
        ),
        None,
    )
    if submission_kind is None:
        raise ValueError("campaign schema has no scheduler binding contract")
    production = checkout_root / "Production" / config["campaign"]
    retry_mode = submission_kind == "full" and attempt > 0
    if retry_mode:
        stem = f"{tune}_job{logical_id:03d}_attempt{attempt:03d}"
        claim_path = (
            production
            / "submission_receipts"
            / "retries"
            / f"{stem}_claim.json"
        )
        record_path = claim_path.with_name(f"{stem}_submitted.json")
        expected_claim_schema = "hf_full_retry_submission_claim_v1"
        expected_record_schema = "hf_full_retry_submission_record_v1"
        expected_submission_kind = "full_retry"
    else:
        contract = SUBMISSION_KINDS[submission_kind]
        claim_path = (
            production / "submission_receipts" / contract["claim_file"]
        )
        record_path = (
            production / "submission_receipts" / contract["record_file"]
        )
        expected_claim_schema = contract["claim_schema"]
        expected_record_schema = contract["record_schema"]
        expected_submission_kind = submission_kind
    for label, path in (("claim", claim_path), ("record", record_path)):
        if path.is_symlink() or not path.is_file():
            raise ValueError(
                f"immutable scheduler submission {label} is absent: {path}"
            )
        metadata = path.stat()
        if metadata.st_nlink != 1 or stat.S_IMODE(metadata.st_mode) & 0o222:
            raise ValueError(
                f"scheduler submission {label} is not sealed read-only"
            )
    claim = json.loads(claim_path.read_text())
    record = json.loads(record_path.read_text())
    if (
        claim.get("schema") != expected_claim_schema
        or claim.get("state") != "claimed_before_condor_submit"
        or claim.get("submission_kind") != expected_submission_kind
        or claim.get("campaign") != config["campaign"]
        or claim.get("campaign_ordinal") != config["campaign_ordinal"]
        or record.get("schema") != expected_record_schema
        or record.get("state") != "condor_submit_succeeded"
        or record.get("submission_kind") != expected_submission_kind
        or record.get("claim_sha256") != sha256(claim_path)
        or record.get("campaign") != config["campaign"]
        or record.get("campaign_ordinal") != config["campaign_ordinal"]
        or record.get("submitted_held") is not True
    ):
        raise ValueError("scheduler submission claim/record contract differs")
    classad_relative_text = record.get("classad_evidence_path")
    classad_relative = (
        Path(classad_relative_text)
        if isinstance(classad_relative_text, str)
        else Path()
    )
    classad_path = checkout_root / classad_relative
    expected_classad_path = (
        claim_path.with_name(
            claim_path.name.removesuffix("_claim.json")
            + "_classads.json"
        )
        if retry_mode
        else record_path.with_name(
            record_path.name.removesuffix(".json") + "_classads.json"
        )
    )
    if (
        not classad_relative_text
        or classad_relative.is_absolute()
        or ".." in classad_relative.parts
        or classad_path != expected_classad_path
        or classad_path.is_symlink()
        or not classad_path.is_file()
        or classad_path.stat().st_nlink != 1
        or stat.S_IMODE(classad_path.stat().st_mode) & 0o222
        or sha256(classad_path) != record.get("classad_evidence_sha256")
    ):
        raise ValueError("scheduler submission ClassAd evidence differs")
    classad_payload = json.loads(classad_path.read_text())
    if classad_payload.get("claim_sha256") != sha256(claim_path):
        raise ValueError("scheduler ClassAd evidence claim binding differs")
    claim_time = _require_utc_timestamp(
        claim.get("created_utc"), "scheduler submission claim"
    )
    captured_time = _require_utc_timestamp(
        classad_payload.get("captured_utc"),
        "scheduler submission ClassAd capture",
    )
    submitted_time = _require_utc_timestamp(
        record.get("submitted_utc"), "scheduler submission record"
    )
    if not claim_time <= captured_time <= submitted_time:
        raise ValueError(
            "scheduler ClassAd capture is outside claim/submission interval"
        )
    if (
        record.get("condor_q_executable")
        != classad_payload.get("condor_q_executable")
        or record.get("condor_q_executable_sha256")
        != classad_payload.get("condor_q_executable_sha256")
    ):
        raise ValueError("scheduler condor_q provenance differs")
    _validate_submission_classads(
        classad_payload,
        claim=claim,
        checkout_root=checkout_root,
        condor_range={
            "cluster_id": record["condor_cluster_id"],
            "first_process": record["condor_first_process"],
            "last_process": record["condor_last_process"],
            "process_count": record["condor_process_count"],
        },
    )
    if record.get("condor_cluster_id") != cluster:
        raise ValueError(
            "runtime ClusterId differs from immutable submission record"
        )
    if retry_mode:
        allocation = claim.get("allocation")
        expected_process = 0
        record_allocation = record.get("allocation")
        if record_allocation != allocation:
            raise ValueError("retry submission record allocation differs")
    else:
        allocations = claim.get("allocations")
        if not isinstance(allocations, list):
            raise ValueError("initial submission claim allocations are absent")
        matching_indices = [
            index
            for index, row in enumerate(allocations)
            if isinstance(row, dict)
            and row.get("tune") == tune
            and row.get("logical_id") == logical_id
            and row.get("attempt") == attempt
            and row.get("seed") == seed
        ]
        if len(matching_indices) != 1:
            raise ValueError(
                "runtime allocation is absent or duplicated in submission claim"
            )
        expected_process = matching_indices[0]
        allocation = allocations[expected_process]
    if (
        not isinstance(allocation, dict)
        or allocation.get("tune") != tune
        or allocation.get("logical_id") != logical_id
        or allocation.get("attempt") != attempt
        or allocation.get("seed") != seed
        or process != expected_process
        or record.get("condor_first_process") != 0
        or record.get("condor_last_process")
        != record.get("condor_process_count", 0) - 1
        or not 0 <= process < record.get("condor_process_count", 0)
    ):
        raise ValueError(
            "runtime ProcId does not map to the claimed scheduler allocation"
        )
    return {
        "claim_path": claim_path,
        "record_path": record_path,
        "claim": claim,
        "record": record,
        "allocation": allocation,
        "cluster_id": cluster,
        "process_id": process,
    }


def verify_full_initial_reservation(
    checkout_root: Path, campaign_dir: Path, config: dict
) -> dict:
    """Verify the immutable local and cross-checkout reservation receipts."""
    submission = SUBMISSION_KINDS["full"]
    campaign_root = checkout_root / "Production" / config["campaign"]
    claim_path = (
        campaign_root
        / "submission_receipts"
        / submission["claim_file"]
    )
    if claim_path.is_symlink() or not claim_path.is_file():
        raise ValueError("initial full-candidate submission claim is absent")
    claim = json.loads(claim_path.read_text())
    identity = repository_identity(checkout_root)
    signoff = campaign_dir / "PHYSICS_ORIGIN_SIGNOFF.json"
    if signoff.is_symlink() or not signoff.is_file():
        raise ValueError("full-production physics sign-off is absent")
    validate_physics_signoff(signoff, config)
    gate_authorization = (
        campaign_dir / "FULL_PRODUCTION_GATE_AUTHORIZATION.json"
    )
    if gate_authorization.is_symlink() or not gate_authorization.is_file():
        raise ValueError("full-production gate authorization is absent")
    gate_reports = validate_gate_authorization(
        gate_authorization, checkout_root, config, signoff
    )
    expansion_authorization_sha256 = None
    if config.get("campaign_kind") == EQUAL_TUNE_EXPANSION_KIND:
        expansion_authorization = (
            campaign_dir / "EQUAL_TUNE_EXPANSION_AUTHORIZATION.json"
        )
        validate_expansion_authorization(
            expansion_authorization, checkout_root, config
        )
        expansion_authorization_sha256 = sha256(expansion_authorization)
    expected = {
        "schema": submission["claim_schema"],
        "state": "claimed_before_condor_submit",
        "submission_kind": "full",
        "campaign": config["campaign"],
        "campaign_ordinal": int(config["campaign_ordinal"]),
        "repository_identity": identity,
        "repository_commit": config["repository_commit"],
        "campaign_json_sha256": sha256(campaign_dir / "campaign.json"),
        "candidate_manifest_sha256": sha256(
            campaign_dir / "candidate_manifest.jsonl"
        ),
        "physics_origin_signoff_sha256": sha256(signoff),
        "full_production_gate_authorization_sha256":
            sha256(gate_authorization),
    }
    if expansion_authorization_sha256 is not None:
        expected["equal_tune_expansion_authorization_sha256"] = (
            expansion_authorization_sha256
        )
    for key, value in expected.items():
        if claim.get(key) != value:
            raise ValueError(f"initial full submission claim {key} differs")
    if expansion_authorization_sha256 is not None:
        recheck_expansion_storage_from_claim(
            claim,
            checkout_root,
            config,
            require_recent_claim=False,
        )
    if (
        claim.get("producer_executable_sha256")
        != gate_reports["gate_a"]["environment"][
            "producer_executable_sha256"
        ]
    ):
        raise ValueError(
            "initial full producer differs from the Gate-A rebuilt binary"
        )
    prefix_bytes = claim.get("seed_ledger_prefix_bytes")
    if (
        isinstance(prefix_bytes, bool)
        or not isinstance(prefix_bytes, int)
        or prefix_bytes < 1
    ):
        raise ValueError("initial full seed-ledger prefix length is invalid")
    ledger_bytes = (campaign_dir / "seed_ledger.jsonl").read_bytes()
    if len(ledger_bytes) < prefix_bytes:
        raise ValueError("full seed ledger is shorter than its initial claim")
    if hashlib.sha256(ledger_bytes[:prefix_bytes]).hexdigest() != claim.get(
        "seed_ledger_sha256"
    ):
        raise ValueError("initial full seed-ledger prefix checksum differs")
    slots, _, _ = campaign_slot_contract(config)
    expected_candidates = sum(slots.values())
    if len(claim.get("allocations", [])) != expected_candidates:
        raise ValueError(
            "initial full claim does not bind every declared candidate"
        )

    initial_submit = campaign_root / submission["submit_file"]
    if (
        initial_submit.is_symlink()
        or not initial_submit.is_file()
        or sha256(initial_submit) != claim.get("submit_file_sha256")
    ):
        raise ValueError("initial full submit file differs from its claim")

    registry = claimed_global_registry(claim, checkout_root, identity)
    _, baseline_path = load_registry_baseline(registry, identity)
    if claim.get("registry_baseline_sha256") != sha256(baseline_path):
        raise ValueError("submission registry baseline differs from claim")
    global_claim_path = registry / "claims" / f"{config['campaign']}.json"
    if global_claim_path.is_symlink() or not global_claim_path.is_file():
        raise ValueError("global full-campaign reservation claim is absent")
    global_claim = json.loads(global_claim_path.read_text())
    global_expected = {
        "schema": "hf_global_submission_claim_v1",
        "state": "reserved_before_condor_submit",
        "repository_identity": identity,
        "global_submission_registry": str(registry),
        "registry_baseline_sha256": sha256(baseline_path),
        "campaign": config["campaign"],
        "campaign_ordinal": int(config["campaign_ordinal"]),
        "submission_kind": "full",
        "repository_commit": config["repository_commit"],
        "physics_origin_signoff_sha256": sha256(signoff),
        "full_production_gate_authorization_sha256":
            sha256(gate_authorization),
        "reserved_seed_intervals": claim["reserved_seed_intervals"],
        "local_receipt_sha256": sha256(claim_path),
    }
    if expansion_authorization_sha256 is not None:
        global_expected["equal_tune_expansion_authorization_sha256"] = (
            expansion_authorization_sha256
        )
    for key, value in global_expected.items():
        if global_claim.get(key) != value:
            raise ValueError(f"global full reservation {key} differs")
    submitted_path = claim_path.with_name(submission["record_file"])
    if submitted_path.is_symlink() or not submitted_path.is_file():
        raise ValueError("initial full-candidate submission record is absent")
    submitted = json.loads(submitted_path.read_text())
    submitted_expected = {
        "schema": submission["record_schema"],
        "state": "condor_submit_succeeded",
        "submission_kind": "full",
        "claim_sha256": sha256(claim_path),
        "campaign": config["campaign"],
        "campaign_ordinal": int(config["campaign_ordinal"]),
        "condor_first_process": 0,
        "condor_last_process": expected_candidates - 1,
        "condor_process_count": expected_candidates,
        "submitted_held": True,
    }
    for key, value in submitted_expected.items():
        if submitted.get(key) != value:
            raise ValueError(f"initial full submission record {key} differs")
    classad_relative = Path(
        str(submitted.get("classad_evidence_path", ""))
    )
    classad_path = checkout_root / classad_relative
    expected_classad_path = submitted_path.with_name(
        submitted_path.name.removesuffix(".json") + "_classads.json"
    )
    if (
        not str(submitted.get("classad_evidence_path", ""))
        or classad_relative.is_absolute()
        or ".." in classad_relative.parts
        or classad_path != expected_classad_path
        or classad_path.is_symlink()
        or not classad_path.is_file()
        or classad_path.stat().st_nlink != 1
        or stat.S_IMODE(classad_path.stat().st_mode) & 0o222
        or sha256(classad_path)
        != submitted.get("classad_evidence_sha256")
    ):
        raise ValueError("initial submission ClassAd evidence differs")
    classad_payload = json.loads(classad_path.read_text())
    if classad_payload.get("claim_sha256") != sha256(claim_path):
        raise ValueError("initial submission ClassAd claim binding differs")
    claim_time = _require_utc_timestamp(
        claim.get("created_utc"), "initial submission claim"
    )
    captured_time = _require_utc_timestamp(
        classad_payload.get("captured_utc"),
        "initial submission ClassAd capture",
    )
    submitted_time = _require_utc_timestamp(
        submitted.get("submitted_utc"), "initial submission record"
    )
    if not claim_time <= captured_time <= submitted_time:
        raise ValueError(
            "initial ClassAd capture is outside claim/submission interval"
        )
    if (
        submitted.get("condor_q_executable")
        != classad_payload.get("condor_q_executable")
        or submitted.get("condor_q_executable_sha256")
        != classad_payload.get("condor_q_executable_sha256")
    ):
        raise ValueError("initial condor_q provenance differs")
    _validate_submission_classads(
        classad_payload,
        claim=claim,
        checkout_root=checkout_root,
        condor_range={
            "cluster_id": submitted["condor_cluster_id"],
            "first_process": submitted["condor_first_process"],
            "last_process": submitted["condor_last_process"],
            "process_count": submitted["condor_process_count"],
        },
    )
    return claim


def _sealed_regular_json(path: Path, label: str) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} is absent or not regular")
    metadata = path.stat()
    if metadata.st_nlink != 1 or stat.S_IMODE(metadata.st_mode) & 0o222:
        raise ValueError(f"{label} is not single-link and read-only")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not valid JSON") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} is not a JSON object")
    return value


def _scheduler_identity_for_attempt(
    checkout_root: Path,
    config: dict,
    tune: str,
    logical_id: int,
    attempt: int,
    seed: int,
) -> dict:
    production = checkout_root / "Production" / config["campaign"]
    if attempt == 0:
        contract = SUBMISSION_KINDS["full"]
        claim_path = (
            production / "submission_receipts" / contract["claim_file"]
        )
        record_path = (
            production / "submission_receipts" / contract["record_file"]
        )
        claim = _sealed_regular_json(
            claim_path, "initial submission claim"
        )
        matches = [
            index
            for index, row in enumerate(claim.get("allocations", []))
            if isinstance(row, dict)
            and row.get("tune") == tune
            and row.get("logical_id") == logical_id
            and row.get("attempt") == attempt
            and row.get("seed") == seed
        ]
        if len(matches) != 1:
            raise ValueError(
                "scheduler-evidence allocation is absent or duplicated"
            )
        process_id = matches[0]
    else:
        stem = f"{tune}_job{logical_id:03d}_attempt{attempt:03d}"
        claim_path = (
            production
            / "submission_receipts"
            / "retries"
            / f"{stem}_claim.json"
        )
        record_path = claim_path.with_name(f"{stem}_submitted.json")
        process_id = 0
    record = _sealed_regular_json(
        record_path, "scheduler submission record"
    )
    cluster_id = record.get("condor_cluster_id")
    if (
        isinstance(cluster_id, bool)
        or not isinstance(cluster_id, int)
        or cluster_id < 0
    ):
        raise ValueError("scheduler submission record ClusterId is invalid")
    verified = verify_scheduler_submission_binding(
        checkout_root,
        config,
        tune=tune,
        logical_id=logical_id,
        attempt=attempt,
        seed=seed,
        cluster_id=str(cluster_id),
        process_id=str(process_id),
    )
    return {
        **verified,
        "cluster_id": cluster_id,
        "process_id": process_id,
    }


def capture_scheduler_terminal_evidence(args: argparse.Namespace) -> int:
    """Capture immutable Condor q/history proof for one prior attempt."""
    checkout_root = args.checkout_root.resolve()
    campaign_dir = args.campaign_dir.resolve()
    config = json.loads((campaign_dir / "campaign.json").read_text())
    if (
        config.get("schema") != "hf_campaign_v1"
        or campaign_dir
        != checkout_root / "campaigns" / config.get("campaign", "")
    ):
        raise ValueError(
            "scheduler evidence requires the canonical full campaign"
        )
    with contextlib.redirect_stdout(io.StringIO()):
        validate_campaign(
            campaign_dir,
            implementation_policy="exact",
            checkout_root=checkout_root,
        )
    slots = campaign_slot_contract(config)[0]
    if (
        args.tune not in TUNES
        or not 0 <= args.logical_id < slots[args.tune]
        or not 0 <= args.attempt <= 4095
    ):
        raise ValueError("scheduler-evidence attempt identity is invalid")
    ledger = load_jsonl(campaign_dir / "seed_ledger.jsonl")
    allocations = [
        row
        for row in ledger
        if row.get("tune") == args.tune
        and row.get("logical_id") == args.logical_id
        and row.get("attempt") == args.attempt
    ]
    if len(allocations) != 1:
        raise ValueError(
            "scheduler-evidence attempt allocation is absent or duplicated"
        )
    seed = int(allocations[0]["seed"])
    scheduler = _scheduler_identity_for_attempt(
        checkout_root,
        config,
        args.tune,
        args.logical_id,
        args.attempt,
        seed,
    )
    cluster_id = scheduler["cluster_id"]
    process_id = scheduler["process_id"]
    job_id = f"{cluster_id}.{process_id}"
    attributes = (
        "ClusterId,ProcId,JobStatus,EnteredCurrentStatus,"
        "CompletionDate,ExitCode,ExitBySignal,RemoveReason"
    )
    def scheduler_tool(requested: str, expected_name: str) -> Path:
        if Path(requested).name != expected_name:
            raise ValueError(
                f"scheduler evidence tool must be named {expected_name}"
            )
        located = (
            requested
            if os.path.sep in requested
            else shutil.which(requested)
        )
        if located is None:
            raise ValueError(f"scheduler evidence tool is absent: {expected_name}")
        resolved = Path(located).resolve()
        if not resolved.is_file() or not os.access(resolved, os.X_OK):
            raise ValueError(
                f"scheduler evidence tool is not executable: {resolved}"
            )
        return resolved

    q_executable = scheduler_tool(args.condor_q, "condor_q")
    history_executable = scheduler_tool(
        args.condor_history, "condor_history"
    )
    q_argv = [
        str(q_executable),
        job_id,
        "-json",
        "-attributes",
        attributes,
    ]
    history_argv = [
        str(history_executable),
        job_id,
        "-json",
        "-limit",
        "1",
        "-attributes",
        attributes,
    ]
    query = subprocess.run(
        q_argv,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    history = subprocess.run(
        history_argv,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if query.returncode != 0 or history.returncode != 0:
        raise ValueError("Condor q/history evidence command failed")
    if query.stderr.strip() or history.stderr.strip():
        raise ValueError("Condor q/history emitted unexpected stderr")
    try:
        live_rows = json.loads(query.stdout)
        history_rows = json.loads(history.stdout)
    except json.JSONDecodeError as error:
        raise ValueError("Condor q/history output is not valid JSON") from error
    if not isinstance(live_rows, list) or live_rows:
        raise ValueError(
            "scheduler evidence found a live job; retry is forbidden"
        )
    if not isinstance(history_rows, list) or len(history_rows) != 1:
        raise ValueError(
            "scheduler history does not contain exactly one terminal job"
        )
    terminal = history_rows[0]
    if (
        not isinstance(terminal, dict)
        or terminal.get("ClusterId") != cluster_id
        or terminal.get("ProcId") != process_id
        or terminal.get("JobStatus") not in {3, 4}
    ):
        raise ValueError(
            "scheduler history identity/status is not terminal and exact"
        )
    production = checkout_root / "Production" / config["campaign"]
    evidence_dir = (
        production
        / "scheduler_evidence"
        / args.tune
        / f"job_{args.logical_id:03d}"
        / f"attempt_{args.attempt:03d}"
    )
    ensure_directory_chain_no_symlinks(checkout_root, evidence_dir)
    q_stdout = evidence_dir / "condor_q.stdout.json"
    q_stderr = evidence_dir / "condor_q.stderr.log"
    history_stdout = evidence_dir / "condor_history.stdout.json"
    history_stderr = evidence_dir / "condor_history.stderr.log"
    for path, text_value in (
        (q_stdout, query.stdout),
        (q_stderr, query.stderr),
        (history_stdout, history.stdout),
        (history_stderr, history.stderr),
    ):
        exclusive_write(path, text_value)
    start_path = (
        production
        / "attempt_starts"
        / args.tune
        / f"job_{args.logical_id:03d}"
        / f"attempt_{args.attempt:03d}.json"
    )
    start_sha = None
    start_relative = None
    if start_path.exists() or start_path.is_symlink():
        _sealed_regular_json(start_path, "scheduler attempt-start claim")
        start_sha = sha256(start_path)
        start_relative = str(start_path.relative_to(checkout_root))
    captured = datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="seconds"
    )
    evidence = {
        "schema": "hf_condor_terminal_evidence_v1",
        "state": "PASS",
        "captured_utc": captured,
        "campaign": config["campaign"],
        "campaign_ordinal": int(config["campaign_ordinal"]),
        "repository_commit": config["repository_commit"],
        "tune": args.tune,
        "logical_id": args.logical_id,
        "attempt": args.attempt,
        "seed": seed,
        "cluster_id": cluster_id,
        "process_id": process_id,
        "submission_record_path": str(
            scheduler["record_path"].relative_to(checkout_root)
        ),
        "submission_record_sha256": sha256(scheduler["record_path"]),
        "attempt_start_path": start_relative,
        "attempt_start_claim_sha256": start_sha,
        "condor_q": {
            "argv": q_argv,
            "executable_path": str(q_executable),
            "executable_sha256": sha256(q_executable),
            "attributes": attributes,
            "returncode": query.returncode,
            "stdout_path": q_stdout.name,
            "stdout_sha256": sha256(q_stdout),
            "stderr_path": q_stderr.name,
            "stderr_sha256": sha256(q_stderr),
            "live_matches": 0,
        },
        "condor_history": {
            "argv": history_argv,
            "executable_path": str(history_executable),
            "executable_sha256": sha256(history_executable),
            "attributes": attributes,
            "returncode": history.returncode,
            "stdout_path": history_stdout.name,
            "stdout_sha256": sha256(history_stdout),
            "stderr_path": history_stderr.name,
            "stderr_sha256": sha256(history_stderr),
            "terminal_matches": 1,
            "job_status": terminal["JobStatus"],
        },
    }
    output = evidence_dir / "evidence.json"
    exclusive_write(output, json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(output)
    return 0


def _validate_scheduler_loss_evidence(
    checkout_root: Path,
    config: dict,
    *,
    tune: str,
    logical_id: int,
    prior_attempt: int,
    prior_seed: int,
    start_path: Path,
    start_sha: str | None,
    approval: dict,
) -> dict:
    relative_text = approval.get("machine_evidence_path")
    relative = Path(relative_text) if isinstance(relative_text, str) else Path()
    if (
        not relative_text
        or relative.is_absolute()
        or ".." in relative.parts
        or not SHA256.fullmatch(
            str(approval.get("machine_evidence_sha256", ""))
        )
    ):
        raise ValueError("scheduler-loss machine-evidence binding is malformed")
    expected = (
        checkout_root
        / "Production"
        / config["campaign"]
        / "scheduler_evidence"
        / tune
        / f"job_{logical_id:03d}"
        / f"attempt_{prior_attempt:03d}"
        / "evidence.json"
    )
    evidence_path = checkout_root / relative
    if evidence_path != expected:
        raise ValueError("scheduler-loss machine-evidence path is noncanonical")
    evidence = _sealed_regular_json(
        evidence_path, "scheduler-loss machine evidence"
    )
    if sha256(evidence_path) != approval["machine_evidence_sha256"]:
        raise ValueError("scheduler-loss machine-evidence checksum differs")
    scheduler = _scheduler_identity_for_attempt(
        checkout_root,
        config,
        tune,
        logical_id,
        prior_attempt,
        prior_seed,
    )
    expected_fields = {
        "schema": "hf_condor_terminal_evidence_v1",
        "state": "PASS",
        "campaign": config["campaign"],
        "campaign_ordinal": int(config["campaign_ordinal"]),
        "repository_commit": config["repository_commit"],
        "tune": tune,
        "logical_id": logical_id,
        "attempt": prior_attempt,
        "seed": prior_seed,
        "cluster_id": scheduler["cluster_id"],
        "process_id": scheduler["process_id"],
        "submission_record_path": str(
            scheduler["record_path"].relative_to(checkout_root)
        ),
        "submission_record_sha256": sha256(scheduler["record_path"]),
        "attempt_start_path": (
            str(start_path.relative_to(checkout_root))
            if start_sha is not None
            else None
        ),
        "attempt_start_claim_sha256": start_sha,
    }
    for key, value in expected_fields.items():
        if evidence.get(key) != value:
            raise ValueError(f"scheduler-loss machine evidence {key} differs")
    captured = _require_utc_timestamp(
        evidence.get("captured_utc"), "scheduler-loss evidence capture"
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    if captured > now + datetime.timedelta(minutes=5):
        raise ValueError("scheduler-loss evidence timestamp is in the future")
    for section_name, count_key, expected_count in (
        ("condor_q", "live_matches", 0),
        ("condor_history", "terminal_matches", 1),
    ):
        section = evidence.get(section_name)
        if (
            not isinstance(section, dict)
            or section.get("returncode") != 0
            or section.get(count_key) != expected_count
        ):
            raise ValueError(
                f"scheduler-loss {section_name} result is not exact"
            )
        expected_executable_name = (
            "condor_q" if section_name == "condor_q" else "condor_history"
        )
        executable_text = section.get("executable_path")
        executable = (
            Path(executable_text)
            if isinstance(executable_text, str)
            else Path()
        )
        if (
            not executable_text
            or not executable.is_absolute()
            or executable.name != expected_executable_name
            or not executable.is_file()
            or not os.access(executable, os.X_OK)
            or not SHA256.fullmatch(
                str(section.get("executable_sha256", ""))
            )
            or sha256(executable) != section["executable_sha256"]
        ):
            raise ValueError(
                f"scheduler-loss {section_name} executable binding differs"
            )
        attributes = (
            "ClusterId,ProcId,JobStatus,EnteredCurrentStatus,"
            "CompletionDate,ExitCode,ExitBySignal,RemoveReason"
        )
        expected_argv = [
            str(executable),
            f"{scheduler['cluster_id']}.{scheduler['process_id']}",
            "-json",
        ]
        if section_name == "condor_history":
            expected_argv.extend(["-limit", "1"])
        expected_argv.extend(["-attributes", attributes])
        if (
            section.get("argv") != expected_argv
            or section.get("attributes") != attributes
        ):
            raise ValueError(
                f"scheduler-loss {section_name} argv differs"
            )
        for path_key, hash_key in (
            ("stdout_path", "stdout_sha256"),
            ("stderr_path", "stderr_sha256"),
        ):
            basename = section.get(path_key)
            if (
                not isinstance(basename, str)
                or Path(basename).name != basename
                or not SHA256.fullmatch(str(section.get(hash_key, "")))
            ):
                raise ValueError(
                    f"scheduler-loss {section_name} log binding is malformed"
                )
            log = evidence_path.parent / basename
            if (
                log.is_symlink()
                or not log.is_file()
                or log.stat().st_nlink != 1
                or stat.S_IMODE(log.stat().st_mode) & 0o222
                or sha256(log) != section[hash_key]
            ):
                raise ValueError(
                    f"scheduler-loss {section_name} log binding differs"
                )
    q_stdout = (
        evidence_path.parent / evidence["condor_q"]["stdout_path"]
    )
    history_stdout = (
        evidence_path.parent / evidence["condor_history"]["stdout_path"]
    )
    q_stderr = evidence_path.parent / evidence["condor_q"]["stderr_path"]
    history_stderr = (
        evidence_path.parent / evidence["condor_history"]["stderr_path"]
    )
    try:
        live_rows = json.loads(q_stdout.read_text())
        history_rows = json.loads(history_stdout.read_text())
    except json.JSONDecodeError as error:
        raise ValueError(
            "scheduler-loss raw q/history evidence is not JSON"
        ) from error
    if (
        live_rows != []
        or q_stderr.read_text().strip()
        or history_stderr.read_text().strip()
        or not isinstance(history_rows, list)
        or len(history_rows) != 1
        or not isinstance(history_rows[0], dict)
        or history_rows[0].get("ClusterId") != scheduler["cluster_id"]
        or history_rows[0].get("ProcId") != scheduler["process_id"]
        or history_rows[0].get("JobStatus") not in {3, 4}
        or evidence["condor_history"].get("job_status")
        != history_rows[0].get("JobStatus")
    ):
        raise ValueError(
            "scheduler-loss raw q/history semantics differ"
        )
    if evidence["condor_history"].get("job_status") not in {3, 4}:
        raise ValueError("scheduler-loss history status is not terminal")
    return {"path": evidence_path, "captured": captured}


def verify_retry_eligibility(
    checkout_root: Path,
    config: dict,
    tune: str,
    logical_id: int,
    next_attempt: int,
    *,
    scheduler_loss_approval: Path | None = None,
    recorded_evidence: dict | None = None,
) -> dict:
    """Require terminal technical evidence before burning a retry seed."""
    if next_attempt < 1:
        raise ValueError("retry eligibility requires a positive next attempt")
    campaign = config["campaign"]
    initial_claim = verify_full_initial_reservation(
        checkout_root,
        checkout_root / "campaigns" / campaign,
        config,
    )
    production = checkout_root / "Production" / campaign
    stable = (
        production
        / "raw"
        / tune
        / f"hf_{tune}_job{logical_id:03d}.root"
    )
    if stable.exists() or stable.is_symlink():
        raise ValueError(
            "retry forbidden because a stable logical output already exists"
        )
    prior_attempt = next_attempt - 1
    start_path = (
        production
        / "attempt_starts"
        / tune
        / f"job_{logical_id:03d}"
        / f"attempt_{prior_attempt:03d}.json"
    )
    start_sha: str | None = None
    start: dict | None = None
    if start_path.exists() or start_path.is_symlink():
        if start_path.is_symlink() or not start_path.is_file():
            raise ValueError("prior attempt-start claim is not regular")
        start = json.loads(start_path.read_text())
        start_expected = {
            "schema": "hf_attempt_start_claim_v1",
            "state": "claimed_before_producer_execution",
            "campaign": campaign,
            "campaign_ordinal": int(config["campaign_ordinal"]),
            "tune": tune,
            "logical_id": logical_id,
            "attempt": prior_attempt,
            "repository_commit": config["repository_commit"],
        }
        for key, value in start_expected.items():
            if start.get(key) != value:
                raise ValueError(f"prior attempt-start claim {key} differs")
        start_sha = sha256(start_path)

    candidates = load_jsonl(
        checkout_root / "campaigns" / campaign / "candidate_manifest.jsonl"
    )
    candidate = next(
        (
            row
            for row in candidates
            if row["tune"] == tune
            and int(row["logical_id"]) == logical_id
        ),
        None,
    )
    if candidate is None:
        raise ValueError("retry candidate is absent")
    ledger = load_jsonl(
        checkout_root / "campaigns" / campaign / "seed_ledger.jsonl"
    )
    prior_allocations = [
        row
        for row in ledger
        if row["tune"] == tune
        and int(row["logical_id"]) == logical_id
        and int(row["attempt"]) == prior_attempt
    ]
    if len(prior_allocations) != 1:
        raise ValueError("prior retry allocation is absent or duplicated")
    if start is not None:
        complete_start_expected = {
            "role": candidate["role"],
            "seed": int(prior_allocations[0]["seed"]),
            "requested_successes": int(candidate["requested_successes"]),
            "effective_card_sha256": candidate["effective_card_sha256"],
            "producer_executable_sha256":
                initial_claim["producer_executable_sha256"],
        }
        for key, value in complete_start_expected.items():
            if start.get(key) != value:
                raise ValueError(f"prior attempt-start claim {key} differs")
        for scheduler_key in ("cluster_id", "process_id"):
            scheduler_token = start.get(scheduler_key)
            if (
                not isinstance(scheduler_token, str)
                or not SAFE_CAMPAIGN.fullmatch(scheduler_token)
            ):
                raise ValueError(
                    f"prior attempt-start {scheduler_key} is invalid"
                )
    if prior_attempt == 0:
        # The initial record is verified by verify_full_initial_reservation().
        pass
    else:
        retry_stem = (
            f"{tune}_job{logical_id:03d}_attempt{prior_attempt:03d}"
        )
        prior_record_path = (
            production
            / "submission_receipts"
            / "retries"
            / f"{retry_stem}_submitted.json"
        )
        if (
            prior_record_path.is_symlink()
            or not prior_record_path.is_file()
        ):
            raise ValueError("prior retry submission record is absent")
        prior_claim_path = prior_record_path.with_name(
            f"{retry_stem}_claim.json"
        )
        if prior_claim_path.is_symlink() or not prior_claim_path.is_file():
            raise ValueError("prior retry submission claim is absent")
        prior_record = json.loads(prior_record_path.read_text())
        if (
            prior_record.get("schema")
            != "hf_full_retry_submission_record_v1"
            or prior_record.get("state") != "condor_submit_succeeded"
            or prior_record.get("submission_kind") != "full_retry"
            or prior_record.get("campaign") != campaign
            or prior_record.get("claim_sha256") != sha256(prior_claim_path)
            or prior_record.get("condor_first_process") != 0
            or prior_record.get("condor_last_process") != 0
            or prior_record.get("condor_process_count") != 1
            or prior_record.get("submitted_held") is not True
            or prior_record.get("allocation", {}).get("tune") != tune
            or int(
                prior_record.get("allocation", {}).get("logical_id", -1)
            )
            != logical_id
            or int(
                prior_record.get("allocation", {}).get("attempt", -1)
            )
            != prior_attempt
        ):
            raise ValueError("prior retry submission record differs")

    validation_receipt = (
        production
        / "raw_validation"
        / tune
        / f"job_{logical_id:03d}"
        / f"attempt_{prior_attempt:03d}"
        / "receipt.json"
    )
    discovered: list[dict] = []
    if validation_receipt.exists() or validation_receipt.is_symlink():
        if start_sha is None:
            raise ValueError(
                "machine raw-validation failure lacks an attempt-start claim"
            )
        if validation_receipt.is_symlink() or not validation_receipt.is_file():
            raise ValueError("prior raw-validation receipt is not regular")
        validation = json.loads(validation_receipt.read_text())
        expected_provenance = validation.get("expected_provenance", {})
        if (
            validation.get("schema") != "hf_raw_validation_receipt_v1"
            or validation.get("result") != "FAIL"
            or expected_provenance.get("campaign") != campaign
            or expected_provenance.get("tune") != tune
            or int(expected_provenance.get("logical_id", -1)) != logical_id
            or int(expected_provenance.get("attempt", -1)) != prior_attempt
            or expected_provenance.get("attempt_start_claim_sha256")
            != start_sha
            or expected_provenance.get("seed")
            != int(prior_allocations[0]["seed"])
            or expected_provenance.get("role") != candidate["role"]
            or expected_provenance.get("requested_successes")
            != int(candidate["requested_successes"])
            or expected_provenance.get("cluster_id")
            != start["cluster_id"]
            or expected_provenance.get("process_id")
            != start["process_id"]
        ):
            raise ValueError("prior raw-validation FAIL receipt differs")
        discovered.append(
            {
                "kind": "raw_validation_fail",
                "path": str(validation_receipt.relative_to(checkout_root)),
                "sha256": sha256(validation_receipt),
            }
        )

    metadata_glob = (
        production
        / "attempt_metadata"
        / tune
    ).glob(
        f"hf_{tune}_job{logical_id:03d}_attempt"
        f"{prior_attempt:03d}_*.json"
    )
    for metadata_path in sorted(metadata_glob):
        if start_sha is None:
            raise ValueError(
                "machine producer failure lacks an attempt-start claim"
            )
        if metadata_path.is_symlink() or not metadata_path.is_file():
            raise ValueError("prior producer sidecar is not regular")
        metadata = json.loads(metadata_path.read_text())
        if (
            metadata.get("campaign") == campaign
            and metadata.get("tune") == tune
            and int(metadata.get("logical_id", -1)) == logical_id
            and int(metadata.get("attempt", -1)) == prior_attempt
            and int(metadata.get("producer_exit", 0)) != 0
            and metadata.get("attempt_start_claim_sha256") == start_sha
            and int(metadata.get("seed", -1))
            == int(prior_allocations[0]["seed"])
            and metadata.get("role") == candidate["role"]
            and int(metadata.get("requested_successes", -1))
            == int(candidate["requested_successes"])
            and metadata.get("cluster_id") == start["cluster_id"]
            and metadata.get("process_id") == start["process_id"]
        ):
            discovered.append(
                {
                    "kind": "producer_failure",
                    "path": str(metadata_path.relative_to(checkout_root)),
                    "sha256": sha256(metadata_path),
                }
            )

    if (
        scheduler_loss_approval is None
        and isinstance(recorded_evidence, dict)
        and recorded_evidence.get("kind") == "scheduler_loss_approval"
        and isinstance(recorded_evidence.get("path"), str)
    ):
        recorded_relative = Path(recorded_evidence["path"])
        if recorded_relative.is_absolute() or ".." in recorded_relative.parts:
            raise ValueError("recorded scheduler-loss approval path is unsafe")
        scheduler_loss_approval = checkout_root / recorded_relative

    if scheduler_loss_approval is not None:
        approval = scheduler_loss_approval.resolve()
        expected_approval = (
            production
            / "retry_authorizations"
            / (
                f"{tune}_job{logical_id:03d}_attempt"
                f"{prior_attempt:03d}_scheduler_loss.json"
            )
        )
        if (
            approval != expected_approval
            or approval.is_symlink()
            or not approval.is_file()
        ):
            raise ValueError("scheduler-loss approval path is not canonical")
        approval_metadata = approval.stat()
        if (
            approval_metadata.st_nlink != 1
            or stat.S_IMODE(approval_metadata.st_mode) != 0o444
        ):
            raise ValueError(
                "scheduler-loss approval is not single-link mode 0444"
            )
        row = json.loads(approval.read_text())
        approval_expected = {
            "schema": "hf_scheduler_loss_retry_authorization_v1",
            "approved": True,
            "reviewer_role": "project_owner",
            "campaign": campaign,
            "campaign_ordinal": int(config["campaign_ordinal"]),
            "tune": tune,
            "logical_id": logical_id,
            "prior_attempt": prior_attempt,
            "repository_commit": config["repository_commit"],
            "attempt_start_claim_sha256": start_sha,
        }
        for key, value in approval_expected.items():
            if row.get(key) != value:
                raise ValueError(f"scheduler-loss approval {key} differs")
        for key in ("reviewer", "reason", "scheduler_state"):
            value = row.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"scheduler-loss approval {key} is empty")
        if (
            "UNIT TEST" in row["reviewer"].upper()
            or "PROJECT OWNER" in row["reviewer"].upper()
            or len(row["reason"]) > 500
        ):
            raise ValueError(
                "scheduler-loss reviewer/reason is placeholder or invalid"
            )
        decision_time = _require_utc_timestamp(
            row.get("decision_utc"), "scheduler-loss approval"
        )
        now = datetime.datetime.now(datetime.timezone.utc)
        if decision_time > now + datetime.timedelta(minutes=5):
            raise ValueError(
                "scheduler-loss approval timestamp is in the future"
            )
        if row["scheduler_state"] not in {
            "never_started",
            "evicted_or_lost_after_start",
        }:
            raise ValueError("scheduler-loss state is unsupported")
        if (
            row["scheduler_state"] == "never_started"
            and start_sha is not None
        ) or (
            row["scheduler_state"] == "evicted_or_lost_after_start"
            and start_sha is None
        ):
            raise ValueError(
                "scheduler-loss state contradicts attempt-start evidence"
            )
        machine_evidence = _validate_scheduler_loss_evidence(
            checkout_root,
            config,
            tune=tune,
            logical_id=logical_id,
            prior_attempt=prior_attempt,
            prior_seed=int(prior_allocations[0]["seed"]),
            start_path=start_path,
            start_sha=start_sha,
            approval=row,
        )
        if (
            machine_evidence["captured"] > decision_time
            or decision_time - machine_evidence["captured"]
            > datetime.timedelta(hours=24)
        ):
            raise ValueError(
                "scheduler-loss approval is not within 24 hours after "
                "machine evidence capture"
            )
        discovered.append(
            {
                "kind": "scheduler_loss_approval",
                "path": str(approval.relative_to(checkout_root)),
                "sha256": sha256(approval),
            }
        )

    if recorded_evidence is not None:
        if not isinstance(recorded_evidence, dict):
            raise ValueError("retry ledger prior-attempt evidence is malformed")
        evidence_path = checkout_root / str(recorded_evidence.get("path", ""))
        if (
            evidence_path.is_symlink()
            or not evidence_path.is_file()
            or sha256(evidence_path) != recorded_evidence.get("sha256")
            or recorded_evidence not in discovered
        ):
            raise ValueError("recorded retry evidence is absent or changed")
        return recorded_evidence
    if not discovered:
        raise ValueError(
            "retry requires a producer failure, raw-validation FAIL, or "
            "reviewed scheduler-loss authorization"
        )
    # Prefer machine-generated evidence. Multiple matching producer sidecars
    # are forbidden because one allocation may start only once.
    machine = [
        row
        for row in discovered
        if row["kind"] in {"raw_validation_fail", "producer_failure"}
    ]
    if len(machine) > 1:
        raise ValueError("multiple terminal machine receipts found for one attempt")
    return machine[0] if machine else discovered[0]


def claim_submission(args: argparse.Namespace) -> int:
    campaign_dir = args.campaign_dir.resolve()
    checkout_root = args.checkout_root.resolve()
    production_root = args.production_root.resolve()
    if production_root != checkout_root / "Production":
        raise ValueError(
            "submission receipt root must be the checkout's Production directory"
        )
    if not os.environ.get("HADRONIZATION_SUBMISSION_REGISTRY_ROOT"):
        raise ValueError(
            "canonical submission requires the absolute shared "
            "HADRONIZATION_SUBMISSION_REGISTRY_ROOT; a per-HOME registry "
            "cannot prove cross-host seed uniqueness"
        )
    with contextlib.redirect_stdout(io.StringIO()):
        validate_campaign(
            campaign_dir,
            implementation_policy="exact",
            checkout_root=checkout_root,
        )
    config = json.loads((campaign_dir / "campaign.json").read_text())
    submission = SUBMISSION_KINDS[args.submission_kind]
    if config.get("schema") != submission["campaign_schema"]:
        raise ValueError(
            f"{args.submission_kind} submission kind does not match campaign schema"
        )
    candidates = load_jsonl(campaign_dir / "candidate_manifest.jsonl")
    ledger = load_jsonl(campaign_dir / "seed_ledger.jsonl")
    selected = [
        row for row in candidates if row["role"] in submission["roles"]
    ]
    if (
        len(selected)
        != (
            sum(campaign_slot_contract(config)[0].values())
            if args.submission_kind == "full"
            else submission["expected_rows"]
        )
        or any(int(row["attempt"]) != 0 for row in selected)
    ):
        raise ValueError(
            f"{args.submission_kind} initial submission selection is not exact"
        )
    if args.submission_kind == "full" and (
        len(ledger) != sum(campaign_slot_contract(config)[0].values())
        or any(
            int(row["attempt"]) != 0 or row.get("allocation") != "initial"
            for row in ledger
        )
    ):
        raise ValueError(
            "full primary submission must precede every retry allocation"
        )

    current_commit = subprocess.check_output(
        ["git", "-C", str(checkout_root), "rev-parse", "HEAD"], text=True
    ).strip()
    require_tracked_clean(checkout_root)
    producer = args.producer.resolve()
    expected_producer = (
        checkout_root / "SimulationScripts" / "heavyflavourcorrelations_status"
    )
    if (
        producer != expected_producer
        or not producer.is_file()
        or not os.access(producer, os.X_OK)
    ):
        raise ValueError("submission producer is not the checkout's canonical binary")
    producer_sha = sha256(producer)
    if producer_sha != args.producer_executable_sha256:
        raise ValueError("submission producer checksum changed after rendering")
    if current_commit != config.get(
        "repository_commit", config.get("repository_implementation_commit")
    ):
        raise ValueError("submission checkout no longer matches campaign manifest")

    submit_file = args.submit_file.resolve()
    campaign_root = production_root / config["campaign"]
    if (
        submit_file.parent != campaign_root
        or submit_file.name != submission["submit_file"]
    ):
        raise ValueError("submit file is outside its canonical campaign path")
    approval_sha256 = None
    gate_authorization_sha256 = None
    expansion_authorization_sha256 = None
    expansion_live_storage_recheck: dict | None = None
    gate_d_report_path: Path | None = None
    gate_d_report_sha256: str | None = None
    live_storage_recheck: dict | None = None
    if args.submission_kind == "full":
        if args.approval_file is None:
            raise ValueError("full submission requires an approval file")
        approval_file = args.approval_file.resolve()
        expected_approval = campaign_dir / "PHYSICS_ORIGIN_SIGNOFF.json"
        if (
            approval_file != expected_approval
            or approval_file.is_symlink()
            or not approval_file.is_file()
        ):
            raise ValueError("full submission approval file is not canonical")
        validate_physics_signoff(approval_file, config)
        approval_sha256 = sha256(approval_file)
        if args.gate_authorization_file is None:
            raise ValueError(
                "full submission requires Gates A-D owner authorization"
            )
        gate_authorization_file = args.gate_authorization_file.resolve()
        expected_gate_authorization = (
            campaign_dir / "FULL_PRODUCTION_GATE_AUTHORIZATION.json"
        )
        if (
            gate_authorization_file != expected_gate_authorization
            or gate_authorization_file.is_symlink()
            or not gate_authorization_file.is_file()
        ):
            raise ValueError(
                "full-production gate authorization file is not canonical"
            )
        gate_reports = validate_gate_authorization(
            gate_authorization_file,
            checkout_root,
            config,
            approval_file,
        )
        authorization_payload = json.loads(
            gate_authorization_file.read_text()
        )
        gate_d_binding = authorization_payload.get("reports", {}).get("gate_d")
        gate_d_relative = (
            Path(gate_d_binding.get("path", ""))
            if isinstance(gate_d_binding, dict)
            else Path()
        )
        if (
            not isinstance(gate_d_binding, dict)
            or not gate_d_binding.get("path")
            or gate_d_relative.is_absolute()
            or ".." in gate_d_relative.parts
            or not SHA256.fullmatch(
                str(gate_d_binding.get("sha256", ""))
            )
        ):
            raise ValueError("full submission Gate-D report binding is unsafe")
        gate_d_report_path = checkout_root / gate_d_relative
        gate_d_report_sha256 = gate_d_binding["sha256"]
        live_storage_recheck = live_recheck_gate_d_storage(
            gate_reports["gate_d"], campaign_root
        )
        if (
            gate_reports["gate_a"]["environment"][
                "producer_executable_sha256"
            ]
            != producer_sha
        ):
            raise ValueError(
                "submission producer differs from the Gate-A rebuilt binary"
            )
        gate_authorization_sha256 = sha256(gate_authorization_file)
        if config.get("campaign_kind") == EQUAL_TUNE_EXPANSION_KIND:
            if args.expansion_authorization_file is None:
                raise ValueError(
                    "expansion submission requires its distinct owner authorization"
                )
            expansion_authorization_file = (
                args.expansion_authorization_file.resolve()
            )
            expected_expansion_authorization = (
                campaign_dir / "EQUAL_TUNE_EXPANSION_AUTHORIZATION.json"
            )
            if expansion_authorization_file != expected_expansion_authorization:
                raise ValueError(
                    "equal-tune expansion authorization path is not canonical"
                )
            expansion_authorization = validate_expansion_authorization(
                expansion_authorization_file, checkout_root, config
            )
            expansion_authorization_sha256 = sha256(
                expansion_authorization_file
            )
            expansion_live_storage_recheck = (
                live_recheck_expansion_storage(
                    expansion_authorization, checkout_root, config
                )
            )
        elif args.expansion_authorization_file is not None:
            raise ValueError(
                "first-stage submission does not accept expansion authorization"
            )
    elif args.approval_file is not None:
        raise ValueError("Gate-B submission does not accept an approval file")
    elif args.gate_authorization_file is not None:
        raise ValueError(
            "Gate-B submission does not accept a gate authorization file"
        )
    elif args.expansion_authorization_file is not None:
        raise ValueError(
            "Gate-B submission does not accept expansion authorization"
        )

    allocations = [
        {
            "tune": row["tune"],
            "logical_id": int(row["logical_id"]),
            "role": row["role"],
            "attempt": int(row["attempt"]),
            "seed": int(row["seed"]),
            "campaign_ordinal": int(row["campaign_ordinal"]),
            "requested_successes": int(row["requested_successes"]),
            "pthat_min_override": str(row["pthat_min_override"]),
            "multiplicity_audit_events": int(row["multiplicity_audit_events"]),
            "repository_commit": row["repository_commit"],
            "effective_card_sha256": row["effective_card_sha256"],
            "producer_executable_sha256": producer_sha,
        }
        for row in selected
    ]
    reserved_seeds = sorted({int(row["seed"]) for row in ledger})
    if len(reserved_seeds) != len(ledger):
        raise ValueError("submission seed ledger contains duplicate seeds")
    seed_intervals = reserved_seed_intervals(config, ledger)
    registry, identity = global_submission_registry(checkout_root)
    baseline, baseline_path = load_registry_baseline(registry, identity)
    baseline_sha256 = sha256(baseline_path)
    receipt = {
        "schema": submission["claim_schema"],
        "state": "claimed_before_condor_submit",
        "submission_kind": args.submission_kind,
        "created_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "campaign": config["campaign"],
        "campaign_ordinal": int(config["campaign_ordinal"]),
        "repository_identity": identity,
        "global_submission_registry": str(registry),
        "registry_baseline_sha256": baseline_sha256,
        "repository_commit": current_commit,
        "producer_executable_sha256": producer_sha,
        "campaign_json_sha256": sha256(campaign_dir / "campaign.json"),
        "candidate_manifest_sha256": sha256(
            campaign_dir / "candidate_manifest.jsonl"
        ),
        "seed_ledger_sha256": sha256(campaign_dir / "seed_ledger.jsonl"),
        "seed_ledger_prefix_bytes": (
            campaign_dir / "seed_ledger.jsonl"
        ).stat().st_size,
        "submit_file_sha256": sha256(submit_file),
        "reserved_seeds": reserved_seeds,
        "reserved_seed_intervals": seed_intervals,
        "allocations": allocations,
    }
    if approval_sha256 is not None:
        receipt["physics_origin_signoff_sha256"] = approval_sha256
        receipt["full_production_gate_authorization_sha256"] = (
            gate_authorization_sha256
        )
        if expansion_authorization_sha256 is not None:
            receipt["equal_tune_expansion_authorization_sha256"] = (
                expansion_authorization_sha256
            )
            if expansion_live_storage_recheck is None:
                raise ValueError(
                    "expansion submission lacks live storage evidence"
                )
            receipt["expansion_live_storage_recheck"] = (
                expansion_live_storage_recheck
            )
        if (
            gate_d_report_path is None
            or gate_d_report_sha256 is None
            or live_storage_recheck is None
        ):
            raise ValueError("full submission lacks live Gate-D storage evidence")
        receipt["gate_d_report_path"] = str(
            gate_d_report_path.relative_to(checkout_root)
        )
        receipt["gate_d_report_sha256"] = gate_d_report_sha256
        receipt["live_storage_recheck"] = live_storage_recheck
    receipt_text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    receipt_path = (
        campaign_root
        / "submission_receipts"
        / submission["claim_file"]
    )
    ensure_directory_chain_no_symlinks(
        checkout_root, receipt_path.parent
    )
    global_claim = {
        "schema": "hf_global_submission_claim_v1",
        "state": "reserved_before_condor_submit",
        "created_utc": receipt["created_utc"],
        "repository_identity": identity,
        "global_submission_registry": str(registry),
        "registry_baseline_sha256": baseline_sha256,
        "campaign": config["campaign"],
        "campaign_ordinal": int(config["campaign_ordinal"]),
        "submission_kind": args.submission_kind,
        "repository_commit": current_commit,
        "reserved_seeds": reserved_seeds,
        "reserved_seed_intervals": seed_intervals,
        "local_receipt_sha256": hashlib.sha256(
            receipt_text.encode("utf-8")
        ).hexdigest(),
    }
    if approval_sha256 is not None:
        global_claim["physics_origin_signoff_sha256"] = approval_sha256
        global_claim["full_production_gate_authorization_sha256"] = (
            gate_authorization_sha256
        )
        if expansion_authorization_sha256 is not None:
            global_claim["equal_tune_expansion_authorization_sha256"] = (
                expansion_authorization_sha256
            )
    global_claim_text = json.dumps(
        global_claim, indent=2, sort_keys=True
    ) + "\n"
    if registry.is_symlink() or not registry.is_dir():
        raise ValueError("shared submission registry is not a real directory")
    claims_dir = registry / "claims"
    try:
        claims_dir.mkdir(mode=0o700)
    except FileExistsError:
        pass
    if claims_dir.is_symlink() or not claims_dir.is_dir():
        raise ValueError("shared submission claims path is not a real directory")
    global_claim_path = claims_dir / f"{config['campaign']}.json"
    lock_path = registry / ".submission.lock"
    with locked_regular_file(lock_path):
        if receipt_path.exists() or global_claim_path.exists():
            raise ValueError(
                "attempt-0 submission is already claimed locally or globally: "
                f"{receipt_path}"
            )
        requested_intervals = seed_intervals
        for prior in baseline["historical_reservations"]:
            if prior["campaign"] == config["campaign"]:
                raise ValueError(
                    "campaign-name reuse blocked by reviewed historical "
                    f"baseline: {config['campaign']}"
                )
            if int(prior["campaign_ordinal"]) == int(
                config["campaign_ordinal"]
            ):
                raise ValueError(
                    "campaign ordinal reuse blocked by reviewed historical "
                    f"baseline: {config['campaign_ordinal']}"
                )
            overlap = overlapping_seed_intervals(
                requested_intervals,
                prior["reserved_seed_intervals"],
            )
            if overlap:
                raise ValueError(
                    "seed reuse blocked by reviewed historical baseline "
                    f"{prior['campaign']}: {sorted(overlap)}"
                )
        for prior in claims_dir.glob("*.json"):
            try:
                prior_metadata = os.lstat(prior)
                if (
                    stat.S_ISLNK(prior_metadata.st_mode)
                    or not stat.S_ISREG(prior_metadata.st_mode)
                    or prior_metadata.st_nlink != 1
                    or stat.S_IMODE(prior_metadata.st_mode) & 0o222
                ):
                    raise ValueError(
                        "global claim is not single-link and read-only"
                    )
                prior_receipt = json.loads(prior.read_text())
                if (
                    prior_receipt.get("schema")
                    != "hf_global_submission_claim_v1"
                    or prior_receipt.get("repository_identity") != identity
                ):
                    raise ValueError("global claim schema/repository differs")
                prior_intervals = [
                    [int(interval[0]), int(interval[1])]
                    for interval in prior_receipt["reserved_seed_intervals"]
                ]
            except Exception as error:
                raise ValueError(
                    f"cannot audit existing global submission claim {prior}: {error}"
                ) from error
            if prior_receipt.get("campaign") == config["campaign"]:
                raise ValueError(
                    f"campaign-name reuse blocked by {prior}: "
                    f"{config['campaign']}"
                )
            if int(prior_receipt.get("campaign_ordinal", -1)) == int(
                config["campaign_ordinal"]
            ):
                raise ValueError(
                    "campaign ordinal reuse blocked by "
                    f"{prior}: {config['campaign_ordinal']}"
                )
            overlap = overlapping_seed_intervals(
                requested_intervals, prior_intervals
            )
            if overlap:
                raise ValueError(
                    f"seed reuse blocked by {prior}: {sorted(overlap)}"
                )
        # Reserve globally first. A crash can burn an allocation but can never
        # leave it reusable from a second clean clone.
        exclusive_write(global_claim_path, global_claim_text)
        exclusive_write(receipt_path, receipt_text)
    print(receipt_path)
    return 0


def claim_retry_submission(args: argparse.Namespace) -> int:
    campaign_dir = args.campaign_dir.resolve()
    checkout_root = args.checkout_root.resolve()
    production_root = args.production_root.resolve()
    if production_root != checkout_root / "Production":
        raise ValueError(
            "retry receipt root must be the checkout's Production directory"
        )
    with contextlib.redirect_stdout(io.StringIO()):
        validate_campaign(
            campaign_dir,
            implementation_policy="exact",
            checkout_root=checkout_root,
        )
    config = json.loads((campaign_dir / "campaign.json").read_text())
    if config.get("schema") != "hf_campaign_v1":
        raise ValueError("retry submission requires a full campaign")
    allowed_ledger = str(
        (campaign_dir / "seed_ledger.jsonl").relative_to(checkout_root)
    )
    require_tracked_clean(checkout_root, {allowed_ledger})
    initial_claim = verify_full_initial_reservation(
        checkout_root, campaign_dir, config
    )
    retry_storage_recheck = recheck_storage_from_claim(
        initial_claim, checkout_root, require_recent_claim=False
    )
    retry_expansion_storage_recheck = None
    if config.get("campaign_kind") == EQUAL_TUNE_EXPANSION_KIND:
        retry_expansion_storage_recheck = (
            recheck_expansion_storage_from_claim(
                initial_claim,
                checkout_root,
                config,
                require_recent_claim=False,
            )
        )

    producer = args.producer.resolve()
    expected_producer = (
        checkout_root / "SimulationScripts" / "heavyflavourcorrelations_status"
    )
    if (
        producer != expected_producer
        or producer.is_symlink()
        or not producer.is_file()
        or not os.access(producer, os.X_OK)
    ):
        raise ValueError("retry producer is not the canonical executable")
    producer_sha = sha256(producer)
    if (
        producer_sha != args.producer_executable_sha256
        or producer_sha != initial_claim.get("producer_executable_sha256")
    ):
        raise ValueError("retry producer checksum differs from initial claim")

    candidates = load_jsonl(campaign_dir / "candidate_manifest.jsonl")
    candidate_rows = [
        row
        for row in candidates
        if row["tune"] == args.tune
        and int(row["logical_id"]) == args.logical_id
    ]
    if len(candidate_rows) != 1:
        raise ValueError("retry logical candidate is absent or duplicated")
    candidate = candidate_rows[0]
    ledger = load_jsonl(campaign_dir / "seed_ledger.jsonl")
    allocations = [
        row
        for row in ledger
        if row["tune"] == args.tune
        and int(row["logical_id"]) == args.logical_id
        and int(row["attempt"]) == args.attempt
        and int(row["seed"]) == args.seed
        and row.get("allocation") == "retry"
    ]
    if args.attempt < 1 or len(allocations) != 1:
        raise ValueError("retry allocation is absent, duplicated, or attempt zero")
    verify_retry_eligibility(
        checkout_root,
        config,
        args.tune,
        args.logical_id,
        args.attempt,
        recorded_evidence=allocations[0].get("prior_attempt_evidence"),
    )
    expected_seed = campaign_logical_seed(
        config, args.tune, args.logical_id, args.attempt
    )
    if args.seed != expected_seed:
        raise ValueError("retry seed differs from deterministic allocation")
    seed_intervals = initial_claim.get("reserved_seed_intervals", [])
    if not any(
        int(first) <= args.seed <= int(last)
        for first, last in seed_intervals
    ):
        raise ValueError("retry seed is outside the globally reserved interval")

    campaign_root = production_root / config["campaign"]
    retry_stem = (
        f"{args.tune}_job{args.logical_id:03d}_attempt{args.attempt:03d}"
    )
    submit_file = args.submit_file.resolve()
    expected_submit = (
        campaign_root / "retry_submissions" / f"submit_{retry_stem}.sub"
    )
    if (
        submit_file != expected_submit
        or submit_file.is_symlink()
        or not submit_file.is_file()
    ):
        raise ValueError("retry submit file is not the canonical regular file")
    ledger_path = campaign_dir / "seed_ledger.jsonl"
    ledger_bytes = ledger_path.read_bytes()
    allocation = {
        "tune": args.tune,
        "logical_id": args.logical_id,
        "role": candidate["role"],
        "attempt": args.attempt,
        "seed": args.seed,
        "campaign_ordinal": int(config["campaign_ordinal"]),
        "requested_successes": int(candidate["requested_successes"]),
        "pthat_min_override": str(candidate["pthat_min_override"]),
        "multiplicity_audit_events": int(
            candidate["multiplicity_audit_events"]
        ),
        "repository_commit": candidate["repository_commit"],
        "effective_card_sha256": candidate["effective_card_sha256"],
        "producer_executable_sha256": producer_sha,
    }
    receipt = {
        "schema": "hf_full_retry_submission_claim_v1",
        "state": "claimed_before_condor_submit",
        "submission_kind": "full_retry",
        "created_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "campaign": config["campaign"],
        "campaign_ordinal": int(config["campaign_ordinal"]),
        "repository_identity": repository_identity(checkout_root),
        "global_submission_registry":
            initial_claim["global_submission_registry"],
        "repository_commit": config["repository_commit"],
        "producer_executable_sha256": producer_sha,
        "campaign_json_sha256": sha256(campaign_dir / "campaign.json"),
        "candidate_manifest_sha256": sha256(
            campaign_dir / "candidate_manifest.jsonl"
        ),
        "seed_ledger_prefix_bytes": len(ledger_bytes),
        "seed_ledger_sha256": hashlib.sha256(ledger_bytes).hexdigest(),
        "initial_submission_claim_sha256": sha256(
            checkout_root
            / "Production"
            / config["campaign"]
            / "submission_receipts"
            / SUBMISSION_KINDS["full"]["claim_file"]
        ),
        "gate_d_report_path": initial_claim["gate_d_report_path"],
        "gate_d_report_sha256": initial_claim["gate_d_report_sha256"],
        "live_storage_recheck": retry_storage_recheck,
        "submit_file_sha256": sha256(submit_file),
        "allocation": allocation,
    }
    if retry_expansion_storage_recheck is not None:
        receipt["equal_tune_expansion_authorization_sha256"] = (
            initial_claim["equal_tune_expansion_authorization_sha256"]
        )
        receipt["expansion_live_storage_recheck"] = (
            retry_expansion_storage_recheck
        )
    receipt_path = (
        campaign_root
        / "submission_receipts"
        / "retries"
        / f"{retry_stem}_claim.json"
    )
    ensure_directory_chain_no_symlinks(
        checkout_root, receipt_path.parent
    )
    exclusive_write(
        receipt_path, json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(receipt_path)
    return 0


def record_submission(args: argparse.Namespace) -> int:
    claim_path = args.claim.resolve()
    checkout_root = args.checkout_root.resolve()
    claim = json.loads(claim_path.read_text())
    submission_kind = claim.get("submission_kind")
    submission = SUBMISSION_KINDS.get(submission_kind)
    if (
        submission is None
        or claim_path.name != submission["claim_file"]
        or claim.get("schema") != submission["claim_schema"]
        or claim.get("state") != "claimed_before_condor_submit"
        or claim_path.parents[1].name != claim.get("campaign")
        or claim_path
        != (
            checkout_root
            / "Production"
            / claim.get("campaign", "")
            / "submission_receipts"
            / submission["claim_file"]
        )
    ):
        raise ValueError("submission claim has an unsupported schema")
    expected_count = len(claim.get("allocations", []))
    if submission_kind == "full":
        campaign_config = json.loads(
            (
                checkout_root
                / "campaigns"
                / str(claim["campaign"])
                / "campaign.json"
            ).read_text()
        )
        contracted_count = sum(
            campaign_slot_contract(campaign_config)[0].values()
        )
    else:
        contracted_count = submission["expected_rows"]
    if expected_count != contracted_count:
        raise ValueError("submission claim allocation count differs")
    record_storage_recheck = (
        recheck_storage_from_claim(claim, checkout_root)
        if submission_kind == "full"
        else None
    )
    record_expansion_storage_recheck = None
    if (
        submission_kind == "full"
        and campaign_config.get("campaign_kind")
        == EQUAL_TUNE_EXPANSION_KIND
    ):
        record_expansion_storage_recheck = (
            recheck_expansion_storage_from_claim(
                claim, checkout_root, campaign_config
            )
        )
    submit_file = (
        checkout_root
        / "Production"
        / claim["campaign"]
        / submission["submit_file"]
    )
    if (
        submit_file.is_symlink()
        or not submit_file.is_file()
        or claim.get("submit_file_sha256") != sha256(submit_file)
        or "hold = True" not in submit_file.read_text().splitlines()
    ):
        raise ValueError(
            "submission record requires the exact claimed held submit file"
        )
    condor_range = parse_condor_terse_range(
        args.condor_result, expected_count
    )
    classad_path = claim_path.with_name(
        submission["record_file"].removesuffix(".json") + "_classads.json"
    )
    classad_payload = capture_submission_classads(
        claim=claim,
        claim_path=claim_path,
        checkout_root=checkout_root,
        condor_range=condor_range,
        output=classad_path,
    )
    identity = repository_identity(checkout_root)
    registry = claimed_global_registry(claim, checkout_root, identity)
    _, baseline_path = load_registry_baseline(registry, identity)
    if claim.get("registry_baseline_sha256") != sha256(baseline_path):
        raise ValueError("submission registry baseline changed after claim")
    global_claim_path = (
        registry / "claims" / f"{claim['campaign']}.json"
    )
    if global_claim_path.is_symlink() or not global_claim_path.is_file():
        raise ValueError("global reservation claim is absent")
    global_claim = json.loads(global_claim_path.read_text())
    if (
        claim.get("repository_identity") != identity
        or global_claim.get("repository_identity") != identity
        or global_claim.get("local_receipt_sha256") != sha256(claim_path)
    ):
        raise ValueError("global reservation does not bind submission claim")
    record = {
        "schema": submission["record_schema"],
        "state": "condor_submit_succeeded",
        "submission_kind": submission_kind,
        "submitted_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "claim_sha256": sha256(claim_path),
        "campaign": claim["campaign"],
        "campaign_ordinal": claim["campaign_ordinal"],
        "condor_submit_terse": condor_range["terse"],
        "condor_cluster_id": condor_range["cluster_id"],
        "condor_first_process": condor_range["first_process"],
        "condor_last_process": condor_range["last_process"],
        "condor_process_count": condor_range["process_count"],
        "submitted_held": True,
        "classad_evidence_path": str(
            classad_path.relative_to(checkout_root)
        ),
        "classad_evidence_sha256": sha256(classad_path),
        "condor_q_executable": classad_payload["condor_q_executable"],
        "condor_q_executable_sha256":
            classad_payload["condor_q_executable_sha256"],
    }
    if record_storage_recheck is not None:
        record["live_storage_recheck"] = record_storage_recheck
    if record_expansion_storage_recheck is not None:
        record["expansion_live_storage_recheck"] = (
            record_expansion_storage_recheck
        )
    output = claim_path.with_name(submission["record_file"])
    exclusive_write(output, json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(output)
    return 0


def record_retry_submission(args: argparse.Namespace) -> int:
    claim_path = Path(os.path.abspath(args.claim))
    checkout_root = args.checkout_root.resolve()
    if claim_path.is_symlink() or not claim_path.is_file():
        raise ValueError("retry submission claim is absent or not regular")
    claim = json.loads(claim_path.read_text())
    if (
        claim.get("schema") != "hf_full_retry_submission_claim_v1"
        or claim.get("state") != "claimed_before_condor_submit"
        or claim.get("submission_kind") != "full_retry"
        or claim_path
        != (
            checkout_root
            / "Production"
            / claim.get("campaign", "")
            / "submission_receipts"
            / "retries"
            / claim_path.name
        )
        or claim_path.name
        != (
            f"{claim['allocation']['tune']}_job"
            f"{int(claim['allocation']['logical_id']):03d}_attempt"
            f"{int(claim['allocation']['attempt']):03d}_claim.json"
        )
    ):
        raise ValueError("retry submission claim has an unsupported contract")
    allocation = claim["allocation"]
    retry_stem = (
        f"{allocation['tune']}_job{int(allocation['logical_id']):03d}_"
        f"attempt{int(allocation['attempt']):03d}"
    )
    submit_file = (
        checkout_root
        / "Production"
        / claim["campaign"]
        / "retry_submissions"
        / f"submit_{retry_stem}.sub"
    )
    if (
        submit_file.is_symlink()
        or not submit_file.is_file()
        or claim.get("submit_file_sha256") != sha256(submit_file)
        or "hold = True" not in submit_file.read_text().splitlines()
    ):
        raise ValueError(
            "retry record requires the exact claimed held submit file"
        )
    record_storage_recheck = recheck_storage_from_claim(
        claim, checkout_root
    )
    campaign_config = json.loads(
        (
            checkout_root
            / "campaigns"
            / claim["campaign"]
            / "campaign.json"
        ).read_text()
    )
    record_expansion_storage_recheck = None
    if (
        campaign_config.get("campaign_kind")
        == EQUAL_TUNE_EXPANSION_KIND
    ):
        record_expansion_storage_recheck = (
            recheck_expansion_storage_from_claim(
                claim, checkout_root, campaign_config
            )
        )
    condor_range = parse_condor_terse_range(args.condor_result, 1)
    classad_path = claim_path.with_name(
        claim_path.name.removesuffix("_claim.json") + "_classads.json"
    )
    classad_payload = capture_submission_classads(
        claim=claim,
        claim_path=claim_path,
        checkout_root=checkout_root,
        condor_range=condor_range,
        output=classad_path,
    )
    record = {
        "schema": "hf_full_retry_submission_record_v1",
        "state": "condor_submit_succeeded",
        "submission_kind": "full_retry",
        "submitted_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "claim_sha256": sha256(claim_path),
        "campaign": claim["campaign"],
        "campaign_ordinal": claim["campaign_ordinal"],
        "allocation": claim["allocation"],
        "condor_submit_terse": condor_range["terse"],
        "condor_cluster_id": condor_range["cluster_id"],
        "condor_first_process": condor_range["first_process"],
        "condor_last_process": condor_range["last_process"],
        "condor_process_count": condor_range["process_count"],
        "submitted_held": True,
        "classad_evidence_path": str(
            classad_path.relative_to(checkout_root)
        ),
        "classad_evidence_sha256": sha256(classad_path),
        "condor_q_executable": classad_payload["condor_q_executable"],
        "condor_q_executable_sha256":
            classad_payload["condor_q_executable_sha256"],
        "live_storage_recheck": record_storage_recheck,
    }
    if record_expansion_storage_recheck is not None:
        record["expansion_live_storage_recheck"] = (
            record_expansion_storage_recheck
        )
    output = claim_path.with_name(
        claim_path.name.removesuffix("_claim.json") + "_submitted.json"
    )
    exclusive_write(output, json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(output)
    return 0


def claim_attempt_start(args: argparse.Namespace) -> int:
    checkout_root = args.checkout_root.resolve()
    campaign_dir = args.campaign_dir.resolve()
    expected_campaign_dir = (
        checkout_root / "campaigns" / args.campaign
    )
    if campaign_dir != expected_campaign_dir:
        raise ValueError("attempt-start campaign path is not canonical")
    if not SAFE_CAMPAIGN.fullmatch(args.campaign):
        raise ValueError("attempt-start campaign name is unsafe")
    config = json.loads((campaign_dir / "campaign.json").read_text())
    slots = (
        campaign_slot_contract(config)[0]
        if config.get("schema") == "hf_campaign_v1"
        else {tune: 1_000_000 for tune in TUNES}
    )
    if (
        not 1 <= args.campaign_ordinal <= 65_535
        or not 0 <= args.logical_id < slots[args.tune]
        or not 0 <= args.attempt <= 4095
        or not 1 <= args.seed <= 900_000_000
        or not 1 <= args.requested_successes <= 1_048_575
    ):
        raise ValueError("attempt-start numeric allocation is outside bounds")
    for token_name in ("cluster_id", "process_id"):
        token = getattr(args, token_name)
        if not SAFE_CAMPAIGN.fullmatch(token):
            raise ValueError(f"attempt-start {token_name} is unsafe")
    if (
        not GIT_COMMIT.fullmatch(args.repository_commit)
        or not SHA256.fullmatch(args.effective_card_sha256)
        or not SHA256.fullmatch(args.producer_executable_sha256)
    ):
        raise ValueError("attempt-start commit or checksum is malformed")
    with contextlib.redirect_stdout(io.StringIO()):
        validate_campaign(
            campaign_dir,
            implementation_policy="exact",
            checkout_root=checkout_root,
        )
    candidates = load_jsonl(campaign_dir / "candidate_manifest.jsonl")
    ledger = load_jsonl(campaign_dir / "seed_ledger.jsonl")
    candidate = next(
        (
            row
            for row in candidates
            if row["tune"] == args.tune
            and int(row["logical_id"]) == args.logical_id
        ),
        None,
    )
    allocation = next(
        (
            row
            for row in ledger
            if row["tune"] == args.tune
            and int(row["logical_id"]) == args.logical_id
            and int(row["attempt"]) == args.attempt
            and int(row["seed"]) == args.seed
        ),
        None,
    )
    if candidate is None or allocation is None:
        raise ValueError("attempt-start allocation is not in campaign ledger")
    start_expected = {
        "campaign": args.campaign,
        "campaign_ordinal": args.campaign_ordinal,
        "role": args.role,
        "requested_successes": args.requested_successes,
        "repository_commit": args.repository_commit,
        "effective_card_sha256": args.effective_card_sha256,
    }
    candidate_values = {
        "campaign": candidate.get("campaign"),
        "campaign_ordinal": candidate.get("campaign_ordinal"),
        "role": candidate.get("role"),
        "requested_successes": candidate.get("requested_successes"),
        "repository_commit": candidate.get("repository_commit"),
        "effective_card_sha256": candidate.get("effective_card_sha256"),
    }
    for key, value in start_expected.items():
        if candidate_values.get(key) != value:
            raise ValueError(f"attempt-start candidate {key} differs")
    allowed_changes: set[str] = set()
    if config.get("schema") == "hf_campaign_v1":
        allowed_changes.add(
            str(
                (campaign_dir / "seed_ledger.jsonl").relative_to(
                    checkout_root
                )
            )
        )
    require_tracked_clean(checkout_root, allowed_changes)
    verify_scheduler_submission_binding(
        checkout_root,
        config,
        tune=args.tune,
        logical_id=args.logical_id,
        attempt=args.attempt,
        seed=args.seed,
        cluster_id=args.cluster_id,
        process_id=args.process_id,
    )
    private_card_input = Path(os.path.abspath(args.private_card))
    private_producer_input = Path(os.path.abspath(args.private_producer))
    if private_card_input.is_symlink() or private_producer_input.is_symlink():
        raise ValueError("attempt-start private inputs may not be symlinks")
    private_card = private_card_input.resolve(strict=True)
    private_producer = private_producer_input.resolve(strict=True)
    for label, path, expected_sha in (
        ("effective card", private_card, args.effective_card_sha256),
        (
            "producer",
            private_producer,
            args.producer_executable_sha256,
        ),
    ):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"attempt-start private {label} is not regular")
        if path.stat().st_nlink != 1:
            raise ValueError(
                f"attempt-start private {label} has unexpected hard links"
            )
        if label == "producer" and not os.access(path, os.X_OK):
            raise ValueError("attempt-start private producer is not executable")
        if sha256(path) != expected_sha:
            raise ValueError(f"attempt-start private {label} checksum differs")
    work_root = (
        checkout_root
        / "Production"
        / args.campaign
        / "work"
        / args.tune
        / f"job_{args.logical_id:03d}"
        / f"attempt_{args.attempt:03d}"
        / f"{args.cluster_id}_{args.process_id}"
    )
    for path in (private_card, private_producer):
        try:
            path.relative_to(work_root)
        except ValueError as error:
            raise ValueError(
                "attempt-start private inputs are outside the scheduler work tree"
            ) from error
    receipt = {
        "schema": "hf_attempt_start_claim_v1",
        "state": "claimed_before_producer_execution",
        "claimed_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "campaign": args.campaign,
        "campaign_ordinal": args.campaign_ordinal,
        "tune": args.tune,
        "logical_id": args.logical_id,
        "role": args.role,
        "attempt": args.attempt,
        "seed": args.seed,
        "requested_successes": args.requested_successes,
        "repository_commit": args.repository_commit,
        "effective_card_sha256": args.effective_card_sha256,
        "producer_executable_sha256": args.producer_executable_sha256,
        "cluster_id": args.cluster_id,
        "process_id": args.process_id,
    }
    output = (
        checkout_root
        / "Production"
        / args.campaign
        / "attempt_starts"
        / args.tune
        / f"job_{args.logical_id:03d}"
        / f"attempt_{args.attempt:03d}.json"
    )
    ensure_directory_chain_no_symlinks(checkout_root, output.parent)
    exclusive_write(output, json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(output)
    return 0


def write_checksum_sidecar(args: argparse.Namespace) -> int:
    target = args.file.resolve()
    if not target.is_file():
        raise ValueError(f"checksum target is not a regular file: {target}")
    digest = sha256(target)
    output = target.with_name(target.name + ".sha256")
    text = f"{digest}  {target.name}\n"
    if output.exists():
        if output.is_symlink() or not output.is_file():
            raise ValueError(f"checksum sidecar is not a regular file: {output}")
        if output.read_text() != text:
            raise ValueError(f"existing checksum sidecar disagrees: {output}")
    else:
        exclusive_write(output, text)
    print(f"CHECKSUM_SIDECAR_OK path={output} sha256={digest}")
    return 0


def materialize_effective_card(args: argparse.Namespace) -> int:
    source = args.source.resolve()
    output = Path(os.path.abspath(args.output))
    if output.exists() or output.is_symlink():
        raise ValueError(
            f"effective card snapshot destination already exists: {output}"
        )
    content = effective_card_bytes(
        source, args.requested_successes, args.pthat_min_override
    )
    digest = hashlib.sha256(content).hexdigest()
    if digest != args.effective_card_sha256:
        raise ValueError(
            f"effective card checksum {digest} != {args.effective_card_sha256}"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444
    )
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    if output.stat().st_nlink != 1:
        raise ValueError("effective card snapshot has unexpected hard links")
    print(f"EFFECTIVE_CARD_READY path={output} sha256={digest}")
    return 0


def print_effective_pthat_min(args: argparse.Namespace) -> int:
    value = effective_pthat_min(
        args.card.resolve(), args.pthat_min_override
    )
    print(format(value, ".17g"))
    return 0


def promote_output(args: argparse.Namespace) -> int:
    """Atomically publish a validated file without ever replacing a target."""
    source = Path(os.path.abspath(args.source))
    destination = Path(os.path.abspath(args.destination))
    if not source.is_file():
        raise ValueError(f"promotion source is not a regular file: {source}")
    if source.is_symlink() or destination.is_symlink():
        raise ValueError("promotion source/destination may not be symlinks")
    if args.expected_sha256 is not None:
        if (
            not SHA256.fullmatch(args.expected_sha256)
            or sha256(source) != args.expected_sha256
        ):
            raise ValueError("promotion source differs from expected checksum")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, destination)
    except FileExistsError as error:
        raise ValueError(
            f"promotion destination already exists: {destination}"
        ) from error
    source_stat = source.stat()
    destination_stat = destination.stat()
    if (
        source_stat.st_dev != destination_stat.st_dev
        or source_stat.st_ino != destination_stat.st_ino
        or (
            args.expected_sha256 is not None
            and sha256(destination) != args.expected_sha256
        )
    ):
        raise ValueError("published destination differs from promotion source")
    try:
        source.unlink()
    except BaseException:
        # Both names reference the same immutable validated bytes. Leaving the
        # partial link is safer than rolling back the published destination.
        raise
    print(f"OUTPUT_PROMOTED source={source} destination={destination}")
    return 0


def snapshot_executable(args: argparse.Namespace) -> int:
    """Seal exact executable bytes into a private, non-overwritten path."""
    source = Path(os.path.abspath(args.source))
    destination = Path(os.path.abspath(args.destination))
    if source == destination:
        raise ValueError("snapshot source and destination must differ")
    if (
        source.is_symlink()
        or not source.is_file()
        or not os.access(source, os.X_OK)
    ):
        raise ValueError(f"snapshot source is not a regular executable: {source}")
    if sha256(source) != args.producer_executable_sha256:
        raise ValueError("snapshot source checksum differs from authorized producer")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise ValueError(
            f"executable snapshot destination already exists: {destination}"
        )
    descriptor = os.open(
        destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o555
    )
    digest = hashlib.sha256()
    with source.open("rb") as input_stream, os.fdopen(
        descriptor, "wb"
    ) as output_stream:
        for chunk in iter(
            lambda: input_stream.read(1024 * 1024), b""
        ):
            digest.update(chunk)
            output_stream.write(chunk)
        output_stream.flush()
        os.fsync(output_stream.fileno())
    if digest.hexdigest() != args.producer_executable_sha256:
        raise ValueError(
            "producer changed while its private snapshot was being sealed"
        )
    if destination.stat().st_nlink != 1:
        raise ValueError("private producer snapshot has unexpected hard links")
    if not os.access(destination, os.X_OK):
        raise ValueError(f"private producer snapshot is not executable: {destination}")
    print(
        f"EXECUTABLE_SNAPSHOT_READY path={destination} "
        f"sha256={args.producer_executable_sha256}"
    )
    return 0


def snapshot_file(args: argparse.Namespace) -> int:
    """Seal exact non-executable bytes into a private, non-overwritten path."""
    source = Path(os.path.abspath(args.source))
    destination = Path(os.path.abspath(args.destination))
    if source == destination or source.is_symlink() or not source.is_file():
        raise ValueError("snapshot source must be a distinct regular file")
    if sha256(source) != args.expected_sha256:
        raise ValueError("snapshot source checksum differs from expected bytes")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"file snapshot destination already exists: {destination}")
    descriptor = os.open(
        destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444
    )
    digest = hashlib.sha256()
    with source.open("rb") as input_stream, os.fdopen(
        descriptor, "wb"
    ) as output_stream:
        for chunk in iter(
            lambda: input_stream.read(1024 * 1024), b""
        ):
            digest.update(chunk)
            output_stream.write(chunk)
        output_stream.flush()
        os.fsync(output_stream.fileno())
    if digest.hexdigest() != args.expected_sha256:
        raise ValueError("source changed while its snapshot was being sealed")
    if destination.stat().st_nlink != 1:
        raise ValueError("private file snapshot has unexpected hard links")
    print(
        f"FILE_SNAPSHOT_READY path={destination} "
        f"sha256={args.expected_sha256}"
    )
    return 0


def print_tracked_file_sha256(args: argparse.Namespace) -> int:
    checkout_root = args.checkout_root.resolve()
    print(
        git_file_sha256(
            checkout_root, args.repository_commit, args.relative_path
        )
    )
    return 0


def verify_production_directories(args: argparse.Namespace) -> int:
    checkout_root = args.checkout_root.resolve()
    production_root = checkout_root / "Production" / args.campaign
    if not SAFE_CAMPAIGN.fullmatch(args.campaign):
        raise ValueError("production-directory campaign is unsafe")
    ensure_directory_chain_no_symlinks(
        checkout_root, checkout_root / "Production"
    )
    ensure_directory_chain_no_symlinks(checkout_root, production_root)
    checked: list[Path] = []
    for argument in args.directory:
        directory = Path(os.path.abspath(argument)).resolve()
        try:
            directory.relative_to(production_root)
        except ValueError as error:
            raise ValueError(
                f"production directory is outside campaign root: {directory}"
            ) from error
        ensure_directory_chain_no_symlinks(checkout_root, directory)
        checked.append(directory)
    private_directory = Path(
        os.path.abspath(args.private_directory)
    ).resolve()
    if private_directory not in checked:
        raise ValueError("private work directory is not in checked directories")
    os.chmod(private_directory, 0o700)
    if stat.S_IMODE(os.lstat(private_directory).st_mode) != 0o700:
        raise ValueError("private work directory mode is not 0700")
    print(
        f"PRODUCTION_DIRECTORIES_VERIFIED count={len(checked)} "
        f"private={private_directory}"
    )
    return 0


def raw_validation_expected(args: argparse.Namespace) -> dict:
    return {
        "campaign": args.campaign,
        "campaign_ordinal": args.campaign_ordinal,
        "tune": args.tune,
        "logical_id": args.logical_id,
        "role": args.role,
        "attempt": args.attempt,
        "seed": args.seed,
        "requested_successes": args.requested_successes,
        "phase_space_pthat_min": args.phase_space_pthat_min,
        "multiplicity_audit_events": args.multiplicity_audit_events,
        "repository_commit": args.repository_commit,
        "effective_card_sha256": args.effective_card_sha256,
        "producer_executable_sha256": args.producer_executable_sha256,
        "attempt_start_claim_sha256": args.attempt_start_claim_sha256,
        "cluster_id": args.cluster_id,
        "process_id": args.process_id,
    }


def raw_validation_dependency_hashes(paths: list[Path]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path_argument in paths:
        path = Path(os.path.abspath(path_argument))
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"validator dependency is not regular: {path}")
        if path.parent.name in {
            "Validation",
            "SimulationScripts",
            "AnalysisScripts",
        }:
            key = f"{path.parent.name}/{path.name}"
        else:
            key = path.name
        if key in hashes:
            raise ValueError(f"duplicate validator dependency key: {key}")
        hashes[key] = sha256(path)
    return dict(sorted(hashes.items()))


def record_raw_validation(args: argparse.Namespace) -> int:
    receipt = Path(os.path.abspath(args.receipt))
    output = Path(os.path.abspath(args.output))
    log = Path(os.path.abspath(args.log))
    wrapper = Path(os.path.abspath(args.validator_wrapper))
    macro = Path(os.path.abspath(args.validator_macro))
    for label, path in (
        ("validation log", log),
        ("validator wrapper", wrapper),
        ("validator macro", macro),
    ):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"{label} is not a regular file: {path}")
    output_regular = not output.is_symlink() and output.is_file()
    if not output_regular and args.validator_status == 0:
        raise ValueError(
            "validator reported success without a regular output file"
        )
    log_text = log.read_text(errors="replace")
    success_markers = re.findall(
        r"^RAW_VALIDATION_SUMMARY errors=0(?:\s|$)",
        log_text,
        flags=re.MULTILINE,
    )
    lowered_log = log_text.lower()
    passed = (
        args.validator_status == 0
        and len(success_markers) == 1
        and "RAW_VALIDATION_ERROR" not in log_text
        and "segmentation violation" not in lowered_log
        and "segmentation fault" not in lowered_log
    )
    payload = {
        "schema": "hf_raw_validation_receipt_v1",
        "result": "PASS" if passed else "FAIL",
        "validated_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "validator_exit_status": args.validator_status,
        "validator_wrapper_sha256": sha256(wrapper),
        "validator_macro_sha256": sha256(macro),
        "validator_dependency_sha256":
            raw_validation_dependency_hashes(args.dependency),
        "validation_log_name": log.name,
        "validation_log_sha256": sha256(log),
        "output_sha256": sha256(output) if output_regular else None,
        "output_bytes": output.stat().st_size if output_regular else 0,
        "expected_provenance": raw_validation_expected(args),
    }
    exclusive_write(receipt, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        f"RAW_VALIDATION_RECEIPT result={payload['result']} "
        f"path={receipt} output_sha256={payload['output_sha256']}"
    )
    return 0


def verify_raw_validation(args: argparse.Namespace) -> int:
    receipt_path = Path(os.path.abspath(args.receipt))
    output = Path(os.path.abspath(args.output))
    log = Path(os.path.abspath(args.log))
    wrapper = Path(os.path.abspath(args.validator_wrapper))
    macro = Path(os.path.abspath(args.validator_macro))
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise ValueError("raw-validation receipt is absent or not regular")
    for label, path in (
        ("output", output),
        ("validation log", log),
        ("validator wrapper", wrapper),
        ("validator macro", macro),
    ):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"{label} is not a regular file: {path}")
    payload = json.loads(receipt_path.read_text())
    validated_utc = payload.get("validated_utc")
    if not isinstance(validated_utc, str):
        raise ValueError("raw-validation receipt timestamp is absent")
    try:
        parsed_timestamp = datetime.datetime.fromisoformat(validated_utc)
    except ValueError as error:
        raise ValueError(
            "raw-validation receipt timestamp is not ISO-8601"
        ) from error
    if (
        parsed_timestamp.tzinfo is None
        or parsed_timestamp.utcoffset() != datetime.timedelta(0)
    ):
        raise ValueError("raw-validation receipt timestamp is not UTC")
    expected = {
        "schema": "hf_raw_validation_receipt_v1",
        "result": "PASS",
        "validator_exit_status": 0,
        "validator_wrapper_sha256": sha256(wrapper),
        "validator_macro_sha256": sha256(macro),
        "validator_dependency_sha256":
            raw_validation_dependency_hashes(args.dependency),
        "validation_log_name": log.name,
        "validation_log_sha256": sha256(log),
        "output_sha256": sha256(output),
        "output_bytes": output.stat().st_size,
        "expected_provenance": raw_validation_expected(args),
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise ValueError(
                f"raw-validation receipt mismatch {key}: "
                f"{payload.get(key)!r} != {value!r}"
            )
    print(
        f"RAW_VALIDATION_RECEIPT_VERIFIED path={receipt_path} "
        f"output_sha256={payload['output_sha256']}"
    )
    return 0


def add_raw_validation_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("receipt", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("log", type=Path)
    parser.add_argument("validator_wrapper", type=Path)
    parser.add_argument("validator_macro", type=Path)
    parser.add_argument("--dependency", type=Path, action="append", default=[])
    parser.add_argument("--campaign", required=True)
    parser.add_argument("--campaign-ordinal", type=int, required=True)
    parser.add_argument("--tune", choices=TUNES, required=True)
    parser.add_argument("--logical-id", type=int, required=True)
    parser.add_argument(
        "--role", choices=("primary", "reserve", "pilot"), required=True
    )
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--requested-successes", type=int, required=True)
    parser.add_argument("--phase-space-pthat-min", type=float, required=True)
    parser.add_argument("--multiplicity-audit-events", type=int, required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--effective-card-sha256", required=True)
    parser.add_argument("--producer-executable-sha256", required=True)
    parser.add_argument("--attempt-start-claim-sha256", required=True)
    parser.add_argument("--cluster-id", required=True)
    parser.add_argument("--process-id", required=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.set_defaults(root=Path(__file__).resolve().parents[1])
    subparsers = parser.add_subparsers(required=True)
    create = subparsers.add_parser("generate")
    create.add_argument("--root", type=Path, default=parser.get_default("root"))
    create.add_argument(
        "--campaign",
        required=True,
        help=(
            "explicit new campaign tag; no default is provided because the "
            "historical HF_100M_primaryGround_ccbb_v1 seed range is reserved"
        ),
    )
    create.add_argument("--campaign-ordinal", type=int, default=1)
    create.add_argument("--events", type=int, default=1_000_000)
    create.add_argument("--seed-base", type=int, default=100_000_001)
    create.add_argument("--max-attempts", type=int, default=1000)
    create.add_argument("--allow-dirty", action="store_true")
    create.set_defaults(
        parent_freeze=None, additional_jobs_per_tune=None
    )
    create.set_defaults(function=generate)
    expand = subparsers.add_parser(
        "generate-expansion",
        help=(
            "create a parent-bound A/2A/2A technical candidate campaign "
            "whose accepted equal-tune subset supersedes a sealed parent"
        ),
    )
    expand.add_argument("--root", type=Path, default=parser.get_default("root"))
    expand.add_argument("--campaign", required=True)
    expand.add_argument("--campaign-ordinal", type=int, required=True)
    expand.add_argument("--events", type=int, default=1_000_000)
    expand.add_argument("--seed-base", type=int, required=True)
    expand.add_argument("--max-attempts", type=int, default=1000)
    expand.add_argument("--parent-freeze", type=Path, required=True)
    expand.add_argument(
        "--additional-jobs-per-tune", type=int, required=True
    )
    expand.add_argument("--allow-dirty", action="store_true")
    expand.set_defaults(function=generate_expansion)
    check = subparsers.add_parser("validate")
    check.add_argument("campaign_dir", type=Path)
    check.add_argument(
        "--implementation-policy",
        choices=("exact", "ancestor"),
        default="exact",
        help=(
            "Gate-B only: require the production implementation to equal "
            "HEAD, or allow it to be an ancestor for later analysis tooling"
        ),
    )
    check.add_argument(
        "--checkout-root",
        type=Path,
        help=(
            "checkout whose contracts and commit are validated; defaults to "
            "the campaign directory's repository"
        ),
    )
    check.set_defaults(function=validate)
    retry = subparsers.add_parser("allocate-retry")
    retry.add_argument("campaign_dir", type=Path)
    retry.add_argument("tune", choices=TUNES)
    retry.add_argument("logical_id", type=int)
    retry.add_argument("--reason", required=True)
    retry.add_argument("--scheduler-loss-approval", type=Path)
    retry.set_defaults(function=allocate_retry)
    scheduler_evidence = subparsers.add_parser(
        "capture-scheduler-terminal-evidence",
        help=(
            "capture immutable condor_q/condor_history proof before a "
            "reviewed scheduler-loss retry authorization"
        ),
    )
    scheduler_evidence.add_argument("campaign_dir", type=Path)
    scheduler_evidence.add_argument("--checkout-root", type=Path, required=True)
    scheduler_evidence.add_argument("--tune", choices=TUNES, required=True)
    scheduler_evidence.add_argument("--logical-id", type=int, required=True)
    scheduler_evidence.add_argument("--attempt", type=int, required=True)
    scheduler_evidence.add_argument("--condor-q", default="condor_q")
    scheduler_evidence.add_argument(
        "--condor-history", default="condor_history"
    )
    scheduler_evidence.set_defaults(
        function=capture_scheduler_terminal_evidence
    )
    authorization = subparsers.add_parser("authorize")
    authorization.add_argument("campaign_dir", type=Path)
    authorization.add_argument("campaign")
    authorization.add_argument("tune", choices=TUNES)
    authorization.add_argument("logical_id", type=int)
    authorization.add_argument("role", choices=("primary", "reserve", "pilot"))
    authorization.add_argument("attempt", type=int)
    authorization.add_argument("seed", type=int)
    authorization.add_argument("requested_successes", type=int)
    authorization.add_argument("--campaign-ordinal", type=int, required=True)
    authorization.add_argument(
        "--pthat-min-override",
        choices=("NONE", "0.5", "1.0", "2.0"),
        required=True,
    )
    authorization.add_argument(
        "--multiplicity-audit-events", type=int, required=True
    )
    authorization.add_argument("--repository-commit", required=True)
    authorization.add_argument("--effective-card-sha256", required=True)
    authorization.add_argument("--producer-executable-sha256", required=True)
    authorization.add_argument("--checkout-root", type=Path, required=True)
    authorization.add_argument(
        "--require-submission-claim", action="store_true"
    )
    authorization.add_argument("--cluster-id")
    authorization.add_argument("--process-id")
    authorization.set_defaults(function=authorize)
    claim = subparsers.add_parser("claim-submission")
    claim.add_argument("campaign_dir", type=Path)
    claim.add_argument("--checkout-root", type=Path, required=True)
    claim.add_argument("--production-root", type=Path, required=True)
    claim.add_argument("--submit-file", type=Path, required=True)
    claim.add_argument("--producer", type=Path, required=True)
    claim.add_argument("--producer-executable-sha256", required=True)
    claim.add_argument("--approval-file", type=Path)
    claim.add_argument("--gate-authorization-file", type=Path)
    claim.add_argument("--expansion-authorization-file", type=Path)
    claim.add_argument(
        "--submission-kind",
        choices=tuple(SUBMISSION_KINDS),
        required=True,
    )
    claim.set_defaults(function=claim_submission)
    retry_claim = subparsers.add_parser("claim-retry-submission")
    retry_claim.add_argument("campaign_dir", type=Path)
    retry_claim.add_argument("--checkout-root", type=Path, required=True)
    retry_claim.add_argument("--production-root", type=Path, required=True)
    retry_claim.add_argument("--submit-file", type=Path, required=True)
    retry_claim.add_argument("--producer", type=Path, required=True)
    retry_claim.add_argument("--producer-executable-sha256", required=True)
    retry_claim.add_argument("--tune", choices=TUNES, required=True)
    retry_claim.add_argument("--logical-id", type=int, required=True)
    retry_claim.add_argument("--attempt", type=int, required=True)
    retry_claim.add_argument("--seed", type=int, required=True)
    retry_claim.set_defaults(function=claim_retry_submission)
    record = subparsers.add_parser("record-submission")
    record.add_argument("claim", type=Path)
    record.add_argument("condor_result")
    record.add_argument("--checkout-root", type=Path, required=True)
    record.set_defaults(function=record_submission)
    retry_record = subparsers.add_parser("record-retry-submission")
    retry_record.add_argument("claim", type=Path)
    retry_record.add_argument("condor_result")
    retry_record.add_argument("--checkout-root", type=Path, required=True)
    retry_record.set_defaults(function=record_retry_submission)
    attempt_start = subparsers.add_parser("claim-attempt-start")
    attempt_start.add_argument("campaign_dir", type=Path)
    attempt_start.add_argument("--checkout-root", type=Path, required=True)
    attempt_start.add_argument("--campaign", required=True)
    attempt_start.add_argument("--campaign-ordinal", type=int, required=True)
    attempt_start.add_argument("--tune", choices=TUNES, required=True)
    attempt_start.add_argument("--logical-id", type=int, required=True)
    attempt_start.add_argument(
        "--role", choices=("primary", "reserve", "pilot"), required=True
    )
    attempt_start.add_argument("--attempt", type=int, required=True)
    attempt_start.add_argument("--seed", type=int, required=True)
    attempt_start.add_argument("--requested-successes", type=int, required=True)
    attempt_start.add_argument("--repository-commit", required=True)
    attempt_start.add_argument("--effective-card-sha256", required=True)
    attempt_start.add_argument("--producer-executable-sha256", required=True)
    attempt_start.add_argument("--cluster-id", required=True)
    attempt_start.add_argument("--process-id", required=True)
    attempt_start.add_argument("--private-card", type=Path, required=True)
    attempt_start.add_argument("--private-producer", type=Path, required=True)
    attempt_start.set_defaults(function=claim_attempt_start)
    checksum = subparsers.add_parser("write-checksum-sidecar")
    checksum.add_argument("file", type=Path)
    checksum.set_defaults(function=write_checksum_sidecar)
    materialize = subparsers.add_parser("materialize-effective-card")
    materialize.add_argument("source", type=Path)
    materialize.add_argument("output", type=Path)
    materialize.add_argument("requested_successes", type=int)
    materialize.add_argument(
        "pthat_min_override", choices=("NONE", "0.5", "1.0", "2.0")
    )
    materialize.add_argument("effective_card_sha256")
    materialize.set_defaults(function=materialize_effective_card)
    pthat = subparsers.add_parser("effective-pthat-min")
    pthat.add_argument("card", type=Path)
    pthat.add_argument(
        "pthat_min_override", choices=("NONE", "0.5", "1.0", "2.0")
    )
    pthat.set_defaults(function=print_effective_pthat_min)
    promote = subparsers.add_parser("promote-output")
    promote.add_argument("source", type=Path)
    promote.add_argument("destination", type=Path)
    promote.add_argument("--expected-sha256")
    promote.set_defaults(function=promote_output)
    snapshot = subparsers.add_parser("snapshot-executable")
    snapshot.add_argument("source", type=Path)
    snapshot.add_argument("destination", type=Path)
    snapshot.add_argument("producer_executable_sha256")
    snapshot.set_defaults(function=snapshot_executable)
    snapshot_regular = subparsers.add_parser("snapshot-file")
    snapshot_regular.add_argument("source", type=Path)
    snapshot_regular.add_argument("destination", type=Path)
    snapshot_regular.add_argument("expected_sha256")
    snapshot_regular.set_defaults(function=snapshot_file)
    tracked_hash = subparsers.add_parser("tracked-file-sha256")
    tracked_hash.add_argument("checkout_root", type=Path)
    tracked_hash.add_argument("repository_commit")
    tracked_hash.add_argument("relative_path")
    tracked_hash.set_defaults(function=print_tracked_file_sha256)
    directory_check = subparsers.add_parser("verify-production-directories")
    directory_check.add_argument("checkout_root", type=Path)
    directory_check.add_argument("campaign")
    directory_check.add_argument(
        "--directory", type=Path, action="append", required=True
    )
    directory_check.add_argument(
        "--private-directory", type=Path, required=True
    )
    directory_check.set_defaults(function=verify_production_directories)
    record_validation = subparsers.add_parser("record-raw-validation")
    add_raw_validation_arguments(record_validation)
    record_validation.add_argument("--validator-status", type=int, required=True)
    record_validation.set_defaults(function=record_raw_validation)
    verify_validation = subparsers.add_parser("verify-raw-validation")
    add_raw_validation_arguments(verify_validation)
    verify_validation.set_defaults(function=verify_raw_validation)
    args = parser.parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
