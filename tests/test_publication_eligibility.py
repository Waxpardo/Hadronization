#!/usr/bin/env python3
"""Fail-closed tests for publication-dataset promotion evidence."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/dataset_selector.py"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_digest(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode()
    ).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def seal_payload(value: dict) -> dict:
    value = dict(value)
    value["payload_sha256"] = payload_digest(value)
    return value


def binding(checkout: Path, path: Path) -> dict:
    return {
        "path": path.relative_to(checkout).as_posix(),
        "sha256": digest(path),
    }


def fixture(checkout: Path) -> tuple[Path, Path]:
    campaign = "HF_PUBLICATION_FIXTURE"
    commit = "a" * 40
    freeze = checkout / "Production" / campaign / "freeze"
    freeze.mkdir(parents=True)
    manifest = freeze / "canonical_manifest.jsonl"
    manifest.write_text(
        "".join(
            json.dumps(
                {
                    "schema": "hf_canonical_raw_manifest_v2",
                    "campaign": campaign,
                    "tune": tune,
                    "canonical_slot": slot,
                    "repository_commit": commit,
                },
                sort_keys=True,
            )
            + "\n"
            for tune in TUNES
            for slot in range(100)
        )
    )
    manifest_sha = digest(manifest)
    summary = freeze / "freeze_summary.json"
    write_json(
        summary,
        {
            "schema": "hf_canonical_freeze_summary_v3",
            "campaign": campaign,
            "canonical_manifest_sha256": manifest_sha,
            "jobs_per_tune": 100,
        },
    )
    validation_log = freeze / "canonical_raw_validation.log"
    validation_log.write_text(
        "CANONICAL_RAW_VALIDATION errors=0 files=300\n"
    )
    validation_receipt = freeze / "canonical_raw_validation_receipt.json"
    write_json(
        validation_receipt,
        {
            "schema": "hf_canonical_raw_validation_receipt_v2",
            "state": "PASS",
            "canonical_manifest_sha256": manifest_sha,
            "validation_log_sha256": digest(validation_log),
        },
    )
    seal = freeze / "freeze_seal.json"
    write_json(
        seal,
        {
            "schema": "hf_canonical_freeze_seal_v2",
            "state": "SEALED",
            "canonical_manifest_sha256": manifest_sha,
            "validation_receipt_path":
                "canonical_raw_validation_receipt.json",
            "validation_receipt_sha256": digest(validation_receipt),
            "validation_log_path": "canonical_raw_validation.log",
            "validation_log_sha256": digest(validation_log),
        },
    )

    evidence = checkout / "AnalysisResults" / campaign
    origin = evidence / "final_origin_closure_report_v1.json"
    write_json(
        origin,
        seal_payload(
            {
                "schema": "hf_final_origin_closure_report_v1",
                "completion_state": "PASS",
                "publication_readiness": "READY",
                "canonical_manifest_sha256": manifest_sha,
                "freeze_seal_sha256": digest(seal),
                "jobs_per_tune": 100,
                "audited_job_count": 300,
                "unresolved_trigger_candidate_count": 0,
                "origin_summary": [{"role": 1, "candidates": 1}],
                "primary_all_heavy_closure": [
                    {"denominator_count": 1, "count": 1}
                ],
            }
        ),
    )
    robustness = evidence / "statistical_robustness_report_v1.json"
    write_json(
        robustness,
        seal_payload(
            {
                "schema": "hf_statistical_robustness_report_v1",
                "completion_state": "DESCRIPTIVE_CROSS_CHECK_COMPLETE",
                "publication_decision":
                    "NOT_EVALUATED_NO_PREDECLARED_AGREEMENT_THRESHOLD",
                "specification_sha256": "f" * 64,
                "canonical_provenance": {
                    "canonical_manifest_sha256": manifest_sha,
                    "freeze_seal_sha256": digest(seal),
                },
                "final_origin_closure_report": {
                    "sha256": digest(origin)
                },
                "results": [{"quantity": "fixture"}],
            }
        ),
    )
    review = evidence / "FINAL_SCIENTIFIC_REVIEW.json"
    write_json(
        review,
        seal_payload(
            {
                "schema": "hf_final_scientific_review_v1",
                "decision": "APPROVE_PUBLICATION_DATASET",
                "approved": True,
                "reviewer": "Fixture Scientific Reviewer",
                "reviewer_role":
                    "designated_physics_statistics_reviewer",
                "decision_utc": datetime.now(timezone.utc).isoformat(),
                "campaign": campaign,
                "canonical_manifest_sha256": manifest_sha,
                "freeze_seal_sha256": digest(seal),
                "final_origin_closure_sha256": digest(origin),
                "statistical_robustness_sha256": digest(robustness),
                "statistical_specification_sha256": "f" * 64,
                "fixed_nch_definition_reviewed": True,
                "species_registry_disposition_reviewed": True,
                "paper_claim_scope_reviewed": True,
                "blocking_findings": [],
            }
        ),
    )
    os.chmod(review, 0o444)

    authorization = (
        checkout / "campaigns" / campaign
        / "PUBLICATION_DATASET_AUTHORIZATION.json"
    )
    bindings = {
        "canonical_manifest": binding(checkout, manifest),
        "freeze_summary": binding(checkout, summary),
        "freeze_seal": binding(checkout, seal),
        "canonical_validation_receipt":
            binding(checkout, validation_receipt),
        "canonical_validation_log": binding(checkout, validation_log),
        "final_origin_closure": binding(checkout, origin),
        "statistical_robustness": binding(checkout, robustness),
        "final_scientific_review": binding(checkout, review),
    }
    write_json(
        authorization,
        seal_payload(
            {
                "schema": "hf_publication_dataset_eligibility_v1",
                "state": "PASS",
                "publication_eligible": True,
                "dataset_id": "canonical_fixture",
                "campaign": campaign,
                "repository_commit": commit,
                "approved": True,
                "approved_by": "Fixture Project Owner",
                "approver_role": "project_owner",
                "approved_utc": datetime.now(timezone.utc).isoformat(),
                "blocking_findings": [],
                **bindings,
            }
        ),
    )
    os.chmod(authorization, 0o444)

    selector = checkout / "config/dataset_selector.json"
    write_json(
        selector,
        {
            "schema": "hadronization_dataset_selector_v1",
            "active_dataset": "canonical_fixture",
            "datasets": {
                "canonical_fixture": {
                    "status": "canonical",
                    "campaign": campaign,
                    "raw_schema": "hf_primary_ground_raw_v5",
                    "selector":
                        "hard_trigger_primary_ground__primary_ground_associate_v1",
                    "canonical_manifest":
                        manifest.relative_to(checkout).as_posix(),
                    "production_root": f"Production/{campaign}",
                    "analysis_root": f"AnalysisOutput/{campaign}",
                    "raw_base": f"Production/{campaign}",
                    "analyzed_data_base": "AnalyzedData",
                    "complete_root_tag": campaign,
                    "subsample_base":
                        f"AnalyzedData/SUBSAMPLES_{campaign}/"
                        "combined_root_subSamples",
                    "block_count": 10,
                    "publication_eligible": True,
                    "publication_authorization":
                        authorization.relative_to(checkout).as_posix(),
                    "publication_authorization_sha256":
                        digest(authorization),
                    "interpretation": "synthetic contract fixture",
                }
            },
        },
    )
    return selector, robustness, review


def run(selector: Path, checkout: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "validate",
            "--selector",
            str(selector),
            "--checkout",
            str(checkout),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(
        prefix="publication_eligibility_"
    ) as temporary:
        checkout = Path(temporary)
        selector, robustness, review = fixture(checkout)
        passed = run(selector, checkout)
        assert passed.returncode == 0, passed.stderr
        assert "status=canonical" in passed.stdout

        review.chmod(0o644)
        writable_review = run(selector, checkout)
        assert writable_review.returncode != 0
        assert "final scientific review must be" in writable_review.stderr
        review.chmod(0o444)

        robustness.write_text(robustness.read_text() + "\n")
        failed = run(selector, checkout)
        assert failed.returncode != 0
        assert "statistical robustness is absent, changed" in failed.stderr

    print("publication-eligibility tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
