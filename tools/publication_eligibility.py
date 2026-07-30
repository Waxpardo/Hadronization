#!/usr/bin/env python3
"""Validate the immutable evidence that makes a dataset publication eligible.

The checked-in selector is only a pointer.  A boolean in that selector must
never promote data by itself.  Canonical promotion requires an immutable
owner authorization that binds the sealed freeze, final origin closure,
descriptive statistical-robustness report, and an explicit scientific review
of those exact bytes.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import stat
from pathlib import Path
from typing import Any


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
AUTHORIZATION_SCHEMA = "hf_publication_dataset_eligibility_v1"
REVIEW_SCHEMA = "hf_final_scientific_review_v1"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode()
    ).hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size <= 0:
        raise ValueError(f"{label} is absent, empty, or a symlink: {path}")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not valid JSON: {path}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} is not a JSON object")
    return value


def require_single_link_read_only(path: Path, label: str) -> None:
    metadata = path.stat()
    if (
        stat.S_IMODE(metadata.st_mode) != 0o444
        or metadata.st_nlink != 1
    ):
        raise ValueError(f"{label} must be a single-link mode-0444 file")


def resolve_binding(
    checkout: Path, binding: Any, label: str
) -> tuple[Path, dict[str, Any]]:
    if (
        not isinstance(binding, dict)
        or not isinstance(binding.get("path"), str)
        or not HEX64.fullmatch(str(binding.get("sha256", "")))
    ):
        raise ValueError(f"{label} binding is malformed")
    relative = Path(binding["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"{label} path must be checkout-relative")
    root = checkout.resolve()
    path = (root / relative).resolve()
    if root not in path.parents:
        raise ValueError(f"{label} escapes the checkout")
    if (
        path.is_symlink()
        or not path.is_file()
        or sha256(path) != binding["sha256"]
    ):
        raise ValueError(f"{label} is absent, changed, or unsafe")
    return path, binding


def require_timestamp(value: Any, label: str) -> dt.datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} timestamp is absent")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{label} timestamp is invalid") from error
    if parsed.tzinfo is None:
        raise ValueError(f"{label} timestamp has no timezone")
    parsed = parsed.astimezone(dt.timezone.utc)
    if parsed > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
        raise ValueError(f"{label} timestamp is implausibly in the future")
    return parsed


def require_reviewer(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is absent")
    upper = value.upper()
    if any(token in upper for token in ("PLACEHOLDER", "UNIT TEST", "TODO")):
        raise ValueError(f"{label} is a placeholder")
    return value.strip()


def validate_payload_hash(payload: dict[str, Any], label: str) -> None:
    body = dict(payload)
    claimed = body.pop("payload_sha256", None)
    if not HEX64.fullmatch(str(claimed or "")) or claimed != canonical_digest(
        body
    ):
        raise ValueError(f"{label} payload checksum differs")


def validate_manifest(path: Path, campaign: str) -> tuple[str, int, str]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"canonical manifest JSON is invalid at line {line_number}"
            ) from error
        if not isinstance(row, dict):
            raise ValueError("canonical manifest row is not an object")
        rows.append(row)
    if not rows or len(rows) % len(TUNES):
        raise ValueError("canonical manifest has invalid equal-tune coverage")
    counts = {tune: 0 for tune in TUNES}
    identities: set[tuple[str, int]] = set()
    commits: set[str] = set()
    for row in rows:
        tune = row.get("tune")
        slot = row.get("canonical_slot")
        row_campaign = row.get("final_campaign", row.get("campaign"))
        if (
            tune not in TUNES
            or isinstance(slot, bool)
            or not isinstance(slot, int)
            or slot < 0
            or row_campaign != campaign
            or (tune, slot) in identities
            or not HEX40.fullmatch(str(row.get("repository_commit", "")))
        ):
            raise ValueError("canonical manifest identity/commit differs")
        identities.add((str(tune), slot))
        counts[str(tune)] += 1
        commits.add(str(row["repository_commit"]))
    if (
        len(set(counts.values())) != 1
        or next(iter(counts.values())) < 100
        or next(iter(counts.values())) % 10
        or len(commits) != 1
    ):
        raise ValueError(
            "canonical manifest must have one commit and equal N>=100 per "
            "tune divisible by ten"
        )
    jobs_per_tune = next(iter(counts.values()))
    expected = {
        (tune, slot)
        for tune in TUNES
        for slot in range(jobs_per_tune)
    }
    if identities != expected:
        raise ValueError("canonical manifest lacks exact tune/slot coverage")
    return sha256(path), jobs_per_tune, next(iter(commits))


def validate_authorization(
    *,
    checkout: Path,
    dataset_id: str,
    dataset_row: dict[str, Any],
    authorization_path: Path,
    expected_sha256: str,
) -> dict[str, Any]:
    checkout = checkout.resolve()
    if (
        authorization_path.is_symlink()
        or not authorization_path.is_file()
        or not HEX64.fullmatch(expected_sha256)
        or sha256(authorization_path) != expected_sha256
    ):
        raise ValueError(
            "publication eligibility authorization is absent, changed, or "
            "unsafe"
        )
    require_single_link_read_only(
        authorization_path, "publication eligibility authorization"
    )
    authorization = load_json(
        authorization_path, "publication eligibility authorization"
    )
    authorization_fields = {
        "schema",
        "state",
        "publication_eligible",
        "dataset_id",
        "campaign",
        "repository_commit",
        "approved",
        "approved_by",
        "approver_role",
        "approved_utc",
        "blocking_findings",
        "canonical_manifest",
        "freeze_summary",
        "freeze_seal",
        "canonical_validation_receipt",
        "canonical_validation_log",
        "final_origin_closure",
        "statistical_robustness",
        "final_scientific_review",
        "payload_sha256",
    }
    if set(authorization) != authorization_fields:
        raise ValueError(
            "publication eligibility authorization field set differs"
        )
    validate_payload_hash(
        authorization, "publication eligibility authorization"
    )
    campaign = dataset_row.get("campaign")
    if (
        authorization.get("schema") != AUTHORIZATION_SCHEMA
        or authorization.get("state") != "PASS"
        or authorization.get("publication_eligible") is not True
        or authorization.get("dataset_id") != dataset_id
        or authorization.get("campaign") != campaign
        or authorization.get("approved") is not True
        or authorization.get("approver_role") != "project_owner"
        or authorization.get("blocking_findings") != []
    ):
        raise ValueError(
            "publication eligibility authorization does not approve this "
            "exact dataset"
        )
    require_reviewer(
        authorization.get("approved_by"), "publication eligibility approver"
    )
    require_timestamp(
        authorization.get("approved_utc"),
        "publication eligibility approval",
    )

    bindings: dict[str, tuple[Path, dict[str, Any]]] = {}
    for key in (
        "canonical_manifest",
        "freeze_summary",
        "freeze_seal",
        "canonical_validation_receipt",
        "canonical_validation_log",
        "final_origin_closure",
        "statistical_robustness",
        "final_scientific_review",
    ):
        bindings[key] = resolve_binding(
            checkout, authorization.get(key), key.replace("_", " ")
        )

    manifest_path, manifest_binding = bindings["canonical_manifest"]
    manifest_sha, jobs_per_tune, production_commit = validate_manifest(
        manifest_path, str(campaign)
    )
    if (
        manifest_sha != manifest_binding["sha256"]
        or dataset_row.get("canonical_manifest")
        != manifest_binding["path"]
        or authorization.get("repository_commit") != production_commit
    ):
        raise ValueError(
            "publication authorization manifest/commit differs from selector"
        )

    summary = load_json(bindings["freeze_summary"][0], "freeze summary")
    seal = load_json(bindings["freeze_seal"][0], "freeze seal")
    validation_receipt = load_json(
        bindings["canonical_validation_receipt"][0],
        "canonical validation receipt",
    )
    if (
        summary.get("schema")
        not in {
            "hf_canonical_freeze_summary_v3",
            "hf_superseding_canonical_freeze_summary_v4",
        }
        or summary.get("canonical_manifest_sha256") != manifest_sha
        or summary.get("jobs_per_tune") != jobs_per_tune
        or summary.get("campaign") != campaign
        or seal.get("schema")
        not in {
            "hf_canonical_freeze_seal_v2",
            "hf_superseding_canonical_freeze_seal_v3",
        }
        or seal.get("state") != "SEALED"
        or seal.get("canonical_manifest_sha256") != manifest_sha
        or seal.get("validation_receipt_sha256")
        != bindings["canonical_validation_receipt"][1]["sha256"]
        or seal.get("validation_log_sha256")
        != bindings["canonical_validation_log"][1]["sha256"]
        or validation_receipt.get("state") != "PASS"
        or validation_receipt.get("canonical_manifest_sha256")
        != manifest_sha
        or validation_receipt.get("validation_log_sha256")
        != bindings["canonical_validation_log"][1]["sha256"]
    ):
        raise ValueError("publication freeze summary/seal is not exact")

    origin = load_json(
        bindings["final_origin_closure"][0], "final origin closure"
    )
    validate_payload_hash(origin, "final origin closure")
    if (
        origin.get("schema") != "hf_final_origin_closure_report_v1"
        or origin.get("completion_state") != "PASS"
        or origin.get("publication_readiness") != "READY"
        or origin.get("canonical_manifest_sha256") != manifest_sha
        or origin.get("freeze_seal_sha256")
        != bindings["freeze_seal"][1]["sha256"]
        or origin.get("jobs_per_tune") != jobs_per_tune
        or origin.get("audited_job_count") != jobs_per_tune * len(TUNES)
        or origin.get("unresolved_trigger_candidate_count") != 0
        or not isinstance(origin.get("origin_summary"), list)
        or not origin["origin_summary"]
        or not isinstance(origin.get("primary_all_heavy_closure"), list)
        or not origin["primary_all_heavy_closure"]
    ):
        raise ValueError("final origin closure is not publication-ready")

    robustness = load_json(
        bindings["statistical_robustness"][0],
        "statistical robustness report",
    )
    validate_payload_hash(robustness, "statistical robustness report")
    canonical_provenance = robustness.get("canonical_provenance")
    origin_binding = robustness.get("final_origin_closure_report")
    if (
        robustness.get("schema") != "hf_statistical_robustness_report_v1"
        or robustness.get("completion_state")
        != "DESCRIPTIVE_CROSS_CHECK_COMPLETE"
        or robustness.get("publication_decision")
        != "NOT_EVALUATED_NO_PREDECLARED_AGREEMENT_THRESHOLD"
        or not isinstance(canonical_provenance, dict)
        or canonical_provenance.get("canonical_manifest_sha256")
        != manifest_sha
        or canonical_provenance.get("freeze_seal_sha256")
        != bindings["freeze_seal"][1]["sha256"]
        or not isinstance(origin_binding, dict)
        or origin_binding.get("sha256")
        != bindings["final_origin_closure"][1]["sha256"]
        or not HEX64.fullmatch(
            str(robustness.get("specification_sha256", ""))
        )
        or not isinstance(robustness.get("results"), list)
        or not robustness["results"]
    ):
        raise ValueError(
            "statistical robustness report does not bind the exact final "
            "sample"
        )

    review = load_json(
        bindings["final_scientific_review"][0],
        "final scientific review",
    )
    require_single_link_read_only(
        bindings["final_scientific_review"][0],
        "final scientific review",
    )
    validate_payload_hash(review, "final scientific review")
    review_fields = {
        "schema",
        "decision",
        "approved",
        "reviewer",
        "reviewer_role",
        "decision_utc",
        "campaign",
        "canonical_manifest_sha256",
        "freeze_seal_sha256",
        "final_origin_closure_sha256",
        "statistical_robustness_sha256",
        "statistical_specification_sha256",
        "fixed_nch_definition_reviewed",
        "species_registry_disposition_reviewed",
        "paper_claim_scope_reviewed",
        "blocking_findings",
        "payload_sha256",
    }
    if set(review) != review_fields:
        raise ValueError("final scientific review field set differs")
    expected_review = {
        "schema": REVIEW_SCHEMA,
        "decision": "APPROVE_PUBLICATION_DATASET",
        "approved": True,
        "reviewer_role": "designated_physics_statistics_reviewer",
        "campaign": campaign,
        "canonical_manifest_sha256": manifest_sha,
        "freeze_seal_sha256": bindings["freeze_seal"][1]["sha256"],
        "final_origin_closure_sha256":
            bindings["final_origin_closure"][1]["sha256"],
        "statistical_robustness_sha256":
            bindings["statistical_robustness"][1]["sha256"],
        "statistical_specification_sha256":
            robustness["specification_sha256"],
        "fixed_nch_definition_reviewed": True,
        "species_registry_disposition_reviewed": True,
        "paper_claim_scope_reviewed": True,
        "blocking_findings": [],
    }
    if any(review.get(key) != value for key, value in expected_review.items()):
        raise ValueError(
            "final scientific review does not approve the exact final "
            "evidence"
        )
    require_reviewer(review.get("reviewer"), "final scientific reviewer")
    require_timestamp(review.get("decision_utc"), "final scientific review")

    return {
        "path": authorization_path.resolve().as_posix(),
        "sha256": expected_sha256,
        "schema": AUTHORIZATION_SCHEMA,
        "dataset_id": dataset_id,
        "campaign": campaign,
        "repository_commit": production_commit,
        "canonical_manifest_sha256": manifest_sha,
        "freeze_seal_sha256": bindings["freeze_seal"][1]["sha256"],
        "final_origin_closure_sha256":
            bindings["final_origin_closure"][1]["sha256"],
        "statistical_robustness_sha256":
            bindings["statistical_robustness"][1]["sha256"],
        "final_scientific_review_sha256":
            bindings["final_scientific_review"][1]["sha256"],
        "jobs_per_tune": jobs_per_tune,
    }
