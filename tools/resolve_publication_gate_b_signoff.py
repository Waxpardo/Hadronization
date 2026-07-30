#!/usr/bin/env python3
"""Resolve an immutable Gate-B NEEDS_SIGNOFF report after owner review.

This is deliberately a separate workflow from run_publication_gate_b.py.
The original NEEDS_SIGNOFF report is never changed or hidden.  A project
owner must create the canonical sign-off file, bind it to the original report
SHA-256 and exact unresolved-count table, and choose the declared treatment.
This tool then revalidates that evidence and emits a distinct, immutable
superseding Gate-B PASS report suitable for Gate-D/full-production binding.

The tool never creates, edits, or guesses the physics sign-off.
"""

from __future__ import annotations

import argparse
import copy
import datetime
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

import run_publication_gate_b as gate_b


SIGNOFF_SCHEMA = "hf_gate_b_physics_signoff_v1"
RESOLUTION_SCHEMA = gate_b.REPORT_SCHEMA
ALLOWED_TREATMENT = (
    "Exclude unresolved triggers centrally; retain unresolved associates "
    "as a reported origin category"
)
PRESERVED_EVIDENCE_FIELDS = (
    "checkout_state",
    "campaign_manifest",
    "submission_evidence",
    "raw_validation_evidence",
    "raw_validation_count",
    "resource_metadata_evidence",
    "heavy_stability_audit",
    "tune_settings_audit",
    "origin_resolution_audits",
    "central_associate_origin_composition",
    "runtime_storage_benchmark",
    "full_candidate_resource_projection",
    "canonical_300m_resource_projection",
    "unresolved_trigger_candidates",
    "pthat_sensitivity",
)
PLACEHOLDER = re.compile(
    r"(PROJECT\s*OWNER|UNIT\s*TEST|PLACEHOLDER|TO\s*BE\s*DECIDED|\bTBD\b)",
    flags=re.IGNORECASE,
)


class ResolutionFailure(ValueError):
    """Fail-closed sign-off resolution error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ResolutionFailure(message)


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        gate_b.require_read_only_regular(path, label)
        value = json.loads(path.read_text())
        gate_b.require_finite_json(value, label)
    except Exception as error:
        if isinstance(error, ResolutionFailure):
            raise
        raise ResolutionFailure(str(error)) from error
    if not isinstance(value, dict):
        raise ResolutionFailure(f"{label} is not a JSON object")
    return value


def absolute_without_resolving(path: Path) -> Path:
    """Return an absolute lexical path without hiding a symlink leaf."""

    return Path(os.path.abspath(path))


def canonical_parent_preserving_leaf(path: Path) -> Path:
    """Resolve directory aliases while retaining the leaf for link checks."""

    absolute = absolute_without_resolving(path)
    return absolute.parent.resolve() / absolute.name


def require_no_symlink_components(
    checkout: Path, path: Path, label: str
) -> Path:
    """Require an in-checkout path whose existing components are not links."""

    checkout = checkout.resolve()
    absolute = canonical_parent_preserving_leaf(path)
    try:
        relative = absolute.relative_to(checkout)
    except ValueError as error:
        raise ResolutionFailure(f"{label} is outside canonical checkout") from error
    candidate = checkout
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ResolutionFailure(f"{label} traverses a symlink: {candidate}")
    return absolute


def safe_relative(checkout: Path, path: Path, label: str) -> str:
    absolute = require_no_symlink_components(checkout, path, label)
    return str(absolute.relative_to(checkout.resolve()))


def require_sealed_directory_tree(path: Path, label: str) -> None:
    """Require the immutable aggregate tree, including directories, to be sealed."""

    candidates = [path, *(item for item in path.rglob("*") if item.is_dir())]
    for candidate in candidates:
        if candidate.is_symlink() or not candidate.is_dir():
            raise ResolutionFailure(
                f"{label} contains an invalid directory: {candidate}"
            )
        if stat.S_IMODE(candidate.stat().st_mode) & 0o222:
            raise ResolutionFailure(
                f"{label} contains a writable directory: {candidate}"
            )


def validate_original_report(
    checkout: Path, report_path: Path
) -> dict[str, Any]:
    report = load_json(report_path, "original Gate-B NEEDS_SIGNOFF report")
    require(
        report.get("schema") == gate_b.REPORT_SCHEMA,
        "original Gate-B report schema differs",
    )
    require(
        report.get("state") == "NEEDS_SIGNOFF",
        "original Gate-B report is not NEEDS_SIGNOFF",
    )
    require(
        report.get("canonical") is True,
        "original Gate-B report is noncanonical",
    )
    missing_evidence = [
        key for key in PRESERVED_EVIDENCE_FIELDS if key not in report
    ]
    require(
        not missing_evidence,
        "original Gate-B report lacks evidence required by downstream "
        f"consumers: {missing_evidence}",
    )
    commit = report.get("repository_commit")
    require(
        isinstance(commit, str) and gate_b.HEX40.fullmatch(commit) is not None,
        "original Gate-B report commit is invalid",
    )
    head = gate_b.git_output(checkout, "rev-parse", "HEAD")
    require(commit == head, "original Gate-B report commit differs from HEAD")
    campaign = report.get("campaign")
    ordinal = report.get("campaign_ordinal")
    require(
        isinstance(campaign, str)
        and gate_b.SAFE_TOKEN.fullmatch(campaign) is not None,
        "original Gate-B campaign identity is invalid",
    )
    require(
        type(ordinal) is int and 1 <= ordinal <= 65_535,
        "original Gate-B campaign ordinal is invalid",
    )
    failure = report.get("failure")
    require(
        isinstance(failure, str)
        and "no sign-off was created or inferred" in failure,
        "original Gate-B report does not preserve the sign-off blocker",
    )
    unresolved = report.get("unresolved_trigger_candidates")
    require(
        isinstance(unresolved, dict),
        "original unresolved-trigger evidence is absent",
    )
    sample_counts = unresolved.get("all_samples_by_tune_threshold_and_sector")
    total = unresolved.get("all_nine_samples_total")
    require(
        isinstance(sample_counts, dict) and len(sample_counts) == 9,
        "original unresolved-trigger table does not cover nine samples",
    )
    expected_keys = {
        f"{tune}:{threshold}"
        for tune in gate_b.TUNES
        for threshold in ("0.5", "1.0", "2.0")
    }
    require(
        set(sample_counts) == expected_keys,
        "original unresolved-trigger sample identities differ",
    )
    recomputed_total = 0
    for identity, sectors in sample_counts.items():
        require(
            isinstance(sectors, dict) and set(sectors) == {"charm", "beauty"},
            f"unresolved-trigger sector split differs for {identity}",
        )
        for value in sectors.values():
            require(
                type(value) is int and value >= 0,
                f"unresolved-trigger count is invalid for {identity}",
            )
            recomputed_total += value
    require(
        type(total) is int and total > 0 and total == recomputed_total,
        "original unresolved-trigger total is zero or inconsistent",
    )
    pthat = report.get("pthat_sensitivity")
    require(
        isinstance(pthat, dict)
        and pthat.get("outcome") == "SCIENTIFIC_REVIEW_REQUIRED"
        and pthat.get("blocking_reasons") == [],
        "original pTHat outcome has a blocker beyond unresolved origins",
    )

    commands = report.get("commands")
    require(
        isinstance(commands, list) and commands,
        "original Gate-B command evidence is absent",
    )
    nonzero = []
    for command in commands:
        require(isinstance(command, dict), "original command evidence is malformed")
        returncode = command.get("returncode")
        require(
            type(returncode) is int,
            "original command returncode is not an integer",
        )
        require(
            command.get("compiler_warning_found") is False,
            "original command evidence contains a compiler warning",
        )
        if returncode != 0:
            nonzero.append(command)
    require(
        len(nonzero) == 1
        and nonzero[0].get("purpose")
        == "fresh_raw_to_frozen_pthat_decision_recheck"
        and nonzero[0].get("returncode") == 4,
        "original nonzero command is not the expected scientific-review pTHat exit",
    )
    return report


def verify_report_evidence_files(
    checkout: Path, report_path: Path, report: dict[str, Any]
) -> dict[str, Any]:
    report_dir = report_path.parent
    require_sealed_directory_tree(
        report_dir, "original Gate-B aggregate evidence tree"
    )
    log_relative = report.get("log_path")
    log_sha = report.get("log_sha256")
    require(
        isinstance(log_relative, str)
        and gate_b.HEX64.fullmatch(str(log_sha or "")) is not None,
        "original aggregate log binding is absent",
    )
    log_path = report_dir / log_relative
    gate_b.require_read_only_regular(log_path, "original aggregate Gate-B log")
    require(
        gate_b.sha256(log_path) == log_sha,
        "original aggregate Gate-B log checksum differs",
    )

    for command in report["commands"]:
        for path_key, sha_key in (
            ("log_path", "log_sha256"),
            ("stdin_path", "stdin_sha256"),
            ("additional_log_path", "additional_log_sha256"),
            ("input_macro_path", "input_macro_sha256"),
        ):
            if path_key not in command:
                continue
            relative = Path(str(command[path_key]))
            require(
                not relative.is_absolute() and ".." not in relative.parts,
                f"original command {path_key} is unsafe",
            )
            evidence = report_dir / relative
            gate_b.require_read_only_regular(
                evidence, f"original command {path_key}"
            )
            require(
                gate_b.HEX64.fullmatch(str(command.get(sha_key, ""))) is not None
                and gate_b.sha256(evidence) == command[sha_key],
                f"original command {path_key} checksum differs",
            )

    inventory_path = report_dir / "evidence_inventory.json"
    inventory = load_json(
        inventory_path, "original Gate-B evidence inventory"
    )
    require(
        inventory.get("schema")
        == "hf_publication_gate_b_evidence_inventory_v1"
        and isinstance(inventory.get("files"), list),
        "original Gate-B evidence inventory schema differs",
    )
    inventory_paths: set[str] = set()
    for row in inventory["files"]:
        require(isinstance(row, dict), "evidence inventory row is malformed")
        relative = Path(str(row.get("path", "")))
        require(
            str(relative)
            and not relative.is_absolute()
            and ".." not in relative.parts
            and str(relative) not in inventory_paths,
            "evidence inventory path is unsafe or duplicated",
        )
        evidence = report_dir / relative
        gate_b.require_read_only_regular(evidence, "inventoried Gate-B evidence")
        require(
            type(row.get("bytes")) is int
            and row["bytes"] == evidence.stat().st_size
            and gate_b.HEX64.fullmatch(str(row.get("sha256", ""))) is not None
            and row["sha256"] == gate_b.sha256(evidence),
            f"evidence inventory checksum/size differs for {relative}",
        )
        inventory_paths.add(str(relative))
    discovered = {
        str(path.relative_to(report_dir))
        for path in report_dir.rglob("*")
        if path.is_file() and path != inventory_path
    }
    require(
        inventory_paths == discovered,
        "original evidence inventory does not exactly cover report files",
    )

    campaign_evidence = report.get("campaign_manifest")
    require(
        isinstance(campaign_evidence, dict),
        "original campaign-manifest evidence is absent",
    )
    for path_key, sha_key in (
        ("path", "sha256"),
        ("candidate_manifest_path", "candidate_manifest_sha256"),
        ("seed_ledger_path", "seed_ledger_sha256"),
    ):
        relative = Path(str(campaign_evidence.get(path_key, "")))
        require(
            not relative.is_absolute() and ".." not in relative.parts,
            f"campaign evidence {path_key} is unsafe",
        )
        evidence = checkout / relative
        gate_b.require_regular(evidence, f"campaign evidence {path_key}")
        require(
            gate_b.sha256(evidence) == campaign_evidence.get(sha_key),
            f"campaign evidence {path_key} checksum differs",
        )

    production = checkout / "Production" / report["campaign"]
    raw_evidence = report.get("raw_validation_evidence")
    require(
        isinstance(raw_evidence, list) and len(raw_evidence) == 9,
        "original raw-validation evidence does not contain nine samples",
    )
    identities: set[tuple[str, int]] = set()
    for row in raw_evidence:
        require(isinstance(row, dict), "raw-validation evidence row is malformed")
        tune = row.get("tune")
        logical_id = row.get("logical_id")
        require(
            tune in gate_b.TUNES
            and type(logical_id) is int
            and logical_id in gate_b.PROFILES
            and (tune, logical_id) not in identities,
            "raw-validation identity is invalid or duplicated",
        )
        identities.add((tune, logical_id))
        threshold, requested, _, purpose = gate_b.PROFILES[logical_id]
        require(
            row.get("pthat_min") == threshold
            and row.get("requested_successes") == requested
            and row.get("entries") == requested
            and row.get("purpose") == purpose,
            f"raw-validation profile differs for {tune}/{logical_id}",
        )
        for path_key, sha_key, immutable in (
            ("raw_path", "raw_sha256", True),
            ("attempt_start_path", "attempt_start_sha256", True),
            ("attempt_metadata_path", "attempt_metadata_sha256", True),
            (
                "validation_receipt_path",
                "validation_receipt_sha256",
                True,
            ),
            ("validation_log_path", "validation_log_sha256", True),
        ):
            relative = Path(str(row.get(path_key, "")))
            require(
                not relative.is_absolute() and ".." not in relative.parts,
                f"raw evidence {path_key} is unsafe",
            )
            evidence = production / relative
            if immutable:
                gate_b.require_read_only_regular(
                    evidence, f"raw evidence {path_key}"
                )
            else:
                gate_b.require_regular(evidence, f"raw evidence {path_key}")
            require(
                gate_b.sha256(evidence) == row.get(sha_key),
                f"raw evidence {path_key} checksum differs",
            )
        raw_path = production / row["raw_path"]
        require(
            raw_path.stat().st_size == row.get("raw_bytes")
            and row.get("entries") == row.get("requested_successes"),
            "raw evidence size/event accounting differs",
        )
    require(
        identities
        == {
            (tune, logical_id)
            for tune in gate_b.TUNES
            for logical_id in gate_b.PROFILES
        },
        "raw-validation identities do not exactly cover the Gate-B campaign",
    )

    pthat = report["pthat_sensitivity"]
    pthat_path = Path(str(pthat.get("path", "")))
    safe_relative(checkout, pthat_path, "original pTHat decision")
    gate_b.require_regular(pthat_path, "original pTHat decision")
    require(
        gate_b.sha256(pthat_path) == pthat.get("sha256"),
        "original pTHat decision checksum differs",
    )
    return {
        "aggregate_log_path": safe_relative(
            checkout, log_path, "original aggregate Gate-B log"
        ),
        "aggregate_log_sha256": gate_b.sha256(log_path),
        "inventory_path": safe_relative(
            checkout, inventory_path, "original Gate-B evidence inventory"
        ),
        "inventory_sha256": gate_b.sha256(inventory_path),
        "raw_files_revalidated": len(raw_evidence),
        "campaign_evidence_revalidated": 3,
        "pthat_decision_sha256": gate_b.sha256(pthat_path),
    }


def validate_signoff(
    campaign_dir: Path,
    signoff_path: Path,
    original_path: Path,
    original: dict[str, Any],
) -> dict[str, Any]:
    expected_path = campaign_dir / "GATE_B_PHYSICS_SIGNOFF.json"
    require(
        canonical_parent_preserving_leaf(signoff_path)
        == canonical_parent_preserving_leaf(expected_path),
        "physics sign-off path is not canonical",
    )
    signoff = load_json(signoff_path, "project-owner physics sign-off")
    original_sha = gate_b.sha256(original_path)
    expected = {
        "schema": SIGNOFF_SCHEMA,
        "approved": True,
        "campaign": original["campaign"],
        "campaign_ordinal": original["campaign_ordinal"],
        "repository_commit": original["repository_commit"],
        "gate_b_needs_signoff_report_sha256": original_sha,
        "reviewed_unresolved_trigger_candidates": original[
            "unresolved_trigger_candidates"
        ]["all_samples_by_tune_threshold_and_sector"],
        "reviewed_unresolved_trigger_candidates_total": original[
            "unresolved_trigger_candidates"
        ]["all_nine_samples_total"],
        "allowed_unresolved_treatment": ALLOWED_TREATMENT,
    }
    for key, value in expected.items():
        require(
            signoff.get(key) == value,
            f"physics sign-off {key} differs from original evidence",
        )
    reviewer = signoff.get("reviewer")
    reviewer_role = signoff.get("reviewer_role")
    finding = signoff.get("finding")
    require(
        isinstance(reviewer, str)
        and reviewer.strip()
        and PLACEHOLDER.search(reviewer) is None,
        "physics sign-off reviewer is absent or a placeholder",
    )
    require(
        isinstance(reviewer_role, str)
        and reviewer_role.strip().lower() == "project owner",
        "physics sign-off reviewer_role must explicitly be project owner",
    )
    require(
        isinstance(finding, str)
        and len(finding.strip()) >= 20
        and PLACEHOLDER.search(finding) is None,
        "physics sign-off finding is absent, placeholder, or too short",
    )
    decision_utc = signoff.get("decision_utc")
    require(
        isinstance(decision_utc, str) and decision_utc,
        "physics sign-off decision_utc is absent",
    )
    try:
        decision_time = datetime.datetime.fromisoformat(decision_utc)
    except ValueError as error:
        raise ResolutionFailure(
            "physics sign-off decision_utc is not ISO-8601"
        ) from error
    require(
        decision_time.tzinfo is not None
        and decision_time.utcoffset() == datetime.timedelta(0),
        "physics sign-off decision_utc is not explicitly UTC",
    )
    require(
        decision_time
        <= datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=5),
        "physics sign-off decision_utc is implausibly in the future",
    )
    require(
        signoff.get("supersedes_state") == "NEEDS_SIGNOFF",
        "physics sign-off does not explicitly supersede NEEDS_SIGNOFF",
    )
    return signoff


def validate_inputs(
    checkout: Path,
    original_path: Path,
    signoff_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    checkout = checkout.resolve()
    original_path = absolute_without_resolving(original_path)
    signoff_path = absolute_without_resolving(signoff_path)
    safe_relative(checkout, original_path, "original Gate-B report")
    safe_relative(checkout, signoff_path, "Gate-B physics sign-off")
    original = validate_original_report(checkout, original_path)
    campaign_dir = checkout / "campaigns" / original["campaign"]
    production = checkout / "Production" / original["campaign"]
    pthat_path = Path(str(original["pthat_sensitivity"].get("path", "")))
    safe_relative(checkout, pthat_path, "original pTHat decision")
    commit, _ = gate_b.validate_checkout(
        checkout,
        (
            campaign_dir,
            production,
            original_path.parent,
            pthat_path.parent,
        ),
    )
    require(
        original["repository_commit"] == commit,
        "original Gate-B report differs from tracked-clean HEAD",
    )
    signoff = validate_signoff(
        campaign_dir, signoff_path, original_path, original
    )
    evidence = verify_report_evidence_files(
        checkout, original_path, original
    )
    evidence["original_report_sha256"] = gate_b.sha256(original_path)
    evidence["gate_b_physics_signoff_sha256"] = gate_b.sha256(signoff_path)
    return original, signoff, evidence


def run_verification_command(
    checkout: Path,
    original_path: Path,
    signoff_path: Path,
    staging: Path,
) -> dict[str, Any]:
    log = staging / "gate_b_signoff_resolution.log"
    command = gate_b.run_command(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "--verify-only",
            str(original_path),
            str(signoff_path),
            "--checkout-root",
            str(checkout),
        ],
        log,
    )
    command["purpose"] = "gate_b_needs_signoff_evidence_revalidation"
    if command["returncode"] != 0 or command["compiler_warning_found"]:
        raise ResolutionFailure("sign-off evidence verification command failed")
    return command


def preserved_downstream_evidence(
    original: dict[str, Any],
) -> dict[str, Any]:
    """Copy the original evidence needed by Gate D without reinterpretation."""

    missing = [key for key in PRESERVED_EVIDENCE_FIELDS if key not in original]
    require(
        not missing,
        f"original Gate-B report lacks downstream evidence: {missing}",
    )
    raw = original["raw_validation_evidence"]
    require(
        isinstance(raw, list) and len(raw) == 9,
        "original Gate-B report lacks nine raw records for Gate D",
    )
    for row in raw:
        require(
            isinstance(row, dict)
            and gate_b.HEX64.fullmatch(str(row.get("raw_sha256", "")))
            is not None
            and type(row.get("entries")) is int
            and type(row.get("requested_successes")) is int
            and row["entries"] == row["requested_successes"]
            and isinstance(row.get("validation_receipt_path"), str)
            and gate_b.HEX64.fullmatch(
                str(row.get("validation_receipt_sha256", ""))
            )
            is not None,
            "raw record lacks the immutable fields consumed by Gate D",
        )
    return {
        key: copy.deepcopy(original[key])
        for key in PRESERVED_EVIDENCE_FIELDS
    }


def create_resolution(
    checkout: Path,
    original_path: Path,
    signoff_path: Path,
    output_dir: Path,
) -> tuple[int, Path]:
    checkout = checkout.resolve()
    original_path = absolute_without_resolving(original_path)
    signoff_path = absolute_without_resolving(signoff_path)
    output_dir = absolute_without_resolving(output_dir)
    safe_relative(checkout, output_dir, "superseding Gate-B output")
    require(
        output_dir != original_path.parent
        and original_path.parent not in output_dir.parents,
        "superseding Gate-B output must not alter or nest inside the "
        "immutable original report tree",
    )
    require(
        not output_dir.exists() and not output_dir.is_symlink(),
        f"refusing to alter existing sign-off resolution output: {output_dir}",
    )
    original, signoff, evidence = validate_inputs(
        checkout, original_path, signoff_path
    )
    original_sha = evidence["original_report_sha256"]
    signoff_sha = evidence["gate_b_physics_signoff_sha256"]
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = output_dir.parent / f".{output_dir.name}.partial.{os.getpid()}"
    require(
        not staging.exists() and not staging.is_symlink(),
        f"sign-off resolution staging path exists: {staging}",
    )
    staging.mkdir(mode=0o700)
    command = run_verification_command(
        checkout, original_path, signoff_path, staging
    )
    require(
        gate_b.sha256(original_path) == original_sha
        and gate_b.sha256(signoff_path) == signoff_sha,
        "original report or Gate-B physics sign-off changed during validation",
    )
    log_path = staging / command["log_path"]
    with log_path.open("a") as stream:
        stream.write(
            "GATE_B_SIGNOFF_RESOLUTION "
            f"state=PASS campaign={original['campaign']} "
            f"repository_commit={original['repository_commit']} "
            f"original_report_sha256={original_sha} "
            f"signoff_sha256={signoff_sha}\n"
        )
    command["log_sha256"] = gate_b.sha256(log_path)
    report = {
        "schema": RESOLUTION_SCHEMA,
        "state": "PASS",
        "canonical": True,
        "failure": None,
        "repository_commit": original["repository_commit"],
        "campaign": original["campaign"],
        "campaign_ordinal": original["campaign_ordinal"],
        "created_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "resolution_kind": "owner_physics_signoff_supersession_v1",
        "commands": [command],
        "log_path": log_path.name,
        "log_sha256": gate_b.sha256(log_path),
        "supersedes": {
            "path": safe_relative(
                checkout, original_path, "original Gate-B report"
            ),
            "sha256": original_sha,
            "state": "NEEDS_SIGNOFF",
            "schema": original["schema"],
        },
        "gate_b_physics_signoff": {
            "path": safe_relative(
                checkout, signoff_path, "Gate-B physics sign-off"
            ),
            "sha256": signoff_sha,
            "schema": signoff["schema"],
            "reviewer": signoff["reviewer"],
            "reviewer_role": signoff["reviewer_role"],
            "decision_utc": signoff["decision_utc"],
            "finding": signoff["finding"],
            "allowed_unresolved_treatment": signoff[
                "allowed_unresolved_treatment"
            ],
            "reviewed_unresolved_trigger_candidates": signoff[
                "reviewed_unresolved_trigger_candidates"
            ],
            "reviewed_unresolved_trigger_candidates_total": signoff[
                "reviewed_unresolved_trigger_candidates_total"
            ],
        },
        "revalidated_original_evidence": evidence,
        "scientific_scope": (
            "The owner-approved treatment resolves only the explicitly bound "
            "unresolved-origin policy. It does not waive technical failures, "
            "pTHat shifts, incomplete evidence, or later Gate-D checks."
        ),
    }
    report.update(preserved_downstream_evidence(original))
    report_path = staging / "gate_b_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    inventory = []
    for path in sorted(
        candidate for candidate in staging.rglob("*") if candidate.is_file()
    ):
        inventory.append(
            {
                "path": str(path.relative_to(staging)),
                "bytes": path.stat().st_size,
                "sha256": gate_b.sha256(path),
            }
        )
    (staging / "evidence_inventory.json").write_text(
        json.dumps(
            {
                "schema":
                    "hf_publication_gate_b_signoff_evidence_inventory_v1",
                "files": inventory,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    gate_b.seal_tree(staging, seal_root=False)
    os.rename(staging, output_dir)
    os.chmod(output_dir, 0o555)
    print(
        "PUBLICATION_GATE_B_SIGNOFF_RESOLUTION state=PASS "
        f"report={output_dir / 'gate_b_report.json'}"
    )
    return 0, output_dir / "gate_b_report.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Revalidate an immutable Gate-B NEEDS_SIGNOFF report and an "
            "owner-created, report-bound physics sign-off, then emit a "
            "separate immutable superseding PASS report."
        )
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="read-only validation; do not create a superseding report",
    )
    parser.add_argument("original_gate_b_report", type=Path)
    parser.add_argument("physics_signoff", type=Path)
    parser.add_argument("output_dir", nargs="?", type=Path)
    parser.add_argument(
        "--checkout-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    try:
        if args.verify_only:
            if args.output_dir is not None:
                raise ResolutionFailure(
                    "--verify-only does not accept an output directory"
                )
            original, signoff, evidence = validate_inputs(
                args.checkout_root,
                args.original_gate_b_report,
                args.physics_signoff,
            )
            print(
                "GATE_B_SIGNOFF_INPUTS_VALID "
                f"campaign={original['campaign']} "
                f"repository_commit={original['repository_commit']} "
                f"report_sha256={gate_b.sha256(args.original_gate_b_report)} "
                f"signoff_sha256={gate_b.sha256(args.physics_signoff)} "
                f"raw_files={evidence['raw_files_revalidated']} "
                f"reviewer={json.dumps(signoff['reviewer'])}"
            )
            return 0
        if args.output_dir is None:
            raise ResolutionFailure(
                "output_dir is required unless --verify-only is used"
            )
        status, _ = create_resolution(
            args.checkout_root,
            args.original_gate_b_report,
            args.physics_signoff,
            args.output_dir,
        )
        return status
    except Exception as error:
        print(f"GATE_B_SIGNOFF_RESOLUTION_FAIL {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
