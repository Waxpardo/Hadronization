#!/usr/bin/env python3
"""Exercise final and interim Gate-B analysis validation contracts."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/validate_gate_b_analysis_outputs.py"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
CAMPAIGN = "HF_GATEB_analysis_validation_test"
ORDINAL = 812
PRODUCER_SHA = "b" * 64
STABILITY_SHA = "e" * 64
SETTINGS_SHA = "f" * 64
ALLOWLIST_SHA = "a" * 64


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    result = subprocess.run(
        list(arguments),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(arguments)}\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(
        prefix="hadronization_gate_b_analysis_validation_"
    ) as raw_temporary:
        temporary = Path(raw_temporary)
        checkout = temporary / "checkout"
        (checkout / "config").mkdir(parents=True)
        (checkout / "AnalysisScripts").mkdir()
        (checkout / "Validation").mkdir()
        shutil.copy2(
            ROOT / "config/heavy_flavour_pair_registry_v1.json",
            checkout / "config/heavy_flavour_pair_registry_v1.json",
        )
        shutil.copy2(
            ROOT / "AnalysisScripts/status_analysis_THnSparse_qq.C",
            checkout / "AnalysisScripts/status_analysis_THnSparse_qq.C",
        )
        raw_validator = checkout / "Validation/validate_raw_output.sh"
        raw_validator.write_text(
            "#!/bin/sh\n"
            "echo 'RAW_VALIDATION_SUMMARY errors=0 exhaustive=1'\n"
        )
        raw_validator.chmod(0o755)
        run("git", "init", "-q", cwd=checkout)
        run("git", "config", "user.name", "Analysis Validation Test", cwd=checkout)
        run(
            "git",
            "config",
            "user.email",
            "analysis-validation@example.invalid",
            cwd=checkout,
        )
        run("git", "add", ".", cwd=checkout)
        run("git", "commit", "-q", "-m", "analysis validation fixture", cwd=checkout)
        commit = run("git", "rev-parse", "HEAD", cwd=checkout).stdout.strip()
        macro_sha = digest(
            checkout / "AnalysisScripts/status_analysis_THnSparse_qq.C"
        )

        pair_validator = checkout / "Validation/validate_pair_directory.sh"
        pair_validator.write_text(
            "#!/bin/sh\n"
            'tune="$(basename "$(dirname "$1")")"\n'
            'echo "PAIR_DIRECTORY_VALIDATION errors=0 expected_files=300 '
            "found_root_files=300 "
            f"analysis_commit={commit} analysis_macro_sha256={macro_sha} "
            f"raw_campaign={CAMPAIGN} raw_tune=${{tune}} "
            "upstream_raw_sha256=${HADRONIZATION_EXPECTED_RAW_SHA256} "
            f"upstream_commit={commit} "
            f"upstream_executable_sha256={PRODUCER_SHA} "
            f"upstream_tune_allowlist_sha256={ALLOWLIST_SHA} "
            f"upstream_stability_sha256={STABILITY_SHA} "
            f"upstream_settings_sha256={SETTINGS_SHA} "
            "pair_combinatorics_mode=ordered_conditional_v1 "
            'same_sign_pair_factor=1"\n'
        )
        pair_validator.chmod(0o755)

        campaign_dir = temporary / CAMPAIGN
        campaign_dir.mkdir()
        profiles = {
            0: ("1.0", 1_000_000, "long", "one_million_central"),
            1: ("0.5", 100_000, "medium", "pthat_sensitivity_low"),
            2: ("2.0", 100_000, "medium", "pthat_sensitivity_high"),
        }
        rows = []
        for tune_index, tune in enumerate(TUNES):
            for logical_id, (
                pthat,
                successes,
                category,
                purpose,
            ) in profiles.items():
                rows.append(
                    {
                        "campaign": CAMPAIGN,
                        "campaign_ordinal": ORDINAL,
                        "tune": tune,
                        "logical_id": logical_id,
                        "role": "pilot",
                        "attempt": 0,
                        "seed": 600_000_001 + tune_index * 10_000
                        + logical_id * 1_000,
                        "requested_successes": successes,
                        "pthat_min_override": pthat,
                        "category": category,
                        "purpose": purpose,
                        "multiplicity_audit_events": 100,
                        "stable_name": f"hf_{tune}_job{logical_id:03d}.root",
                        "repository_commit": commit,
                        "effective_card_sha256":
                            f"{tune_index}{logical_id}" * 32,
                    }
                )
        config = {
            "schema": "hf_gate_b_pilot_campaign_v1",
            "campaign": CAMPAIGN,
            "campaign_ordinal": ORDINAL,
            "repository_implementation_commit": commit,
            "raw_schema": "hf_primary_ground_raw_v6",
            "origin_algorithm":
                "signed_heavy_constituent_complete_mothers_unique_v4",
            "selector":
                "hard_trigger_primary_ground__primary_ground_associate_v1",
            "pair_registry_sha256": digest(
                checkout / "config/heavy_flavour_pair_registry_v1.json"
            ),
            "tune_allowlist_sha256": ALLOWLIST_SHA,
        }
        (campaign_dir / "campaign.json").write_text(
            json.dumps(config, sort_keys=True) + "\n"
        )
        (campaign_dir / "candidate_manifest.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
        )
        (campaign_dir / "seed_ledger.jsonl").write_text(
            "".join(
                json.dumps(
                    {
                        "tune": row["tune"],
                        "logical_id": row["logical_id"],
                        "attempt": row["attempt"],
                        "seed": row["seed"],
                    },
                    sort_keys=True,
                )
                + "\n"
                for row in rows
            )
        )

        production = temporary / "production"
        analysis = temporary / "analysis"
        pair_registry = json.loads(
            (checkout / "config/heavy_flavour_pair_registry_v1.json").read_text()
        )
        filenames = sorted(row["filename"] for row in pair_registry["pairs"])
        for row in rows:
            raw_file = (
                production
                / "raw"
                / row["tune"]
                / row["stable_name"]
            )
            raw_file.parent.mkdir(parents=True, exist_ok=True)
            raw_file.write_bytes(
                f"{row['tune']}:{row['logical_id']}\n".encode()
            )
            Path(f"{raw_file}.sha256").write_text(
                f"{digest(raw_file)}  {raw_file.name}\n"
            )
            directory = (
                analysis
                / "per_pthat"
                / row["tune"]
                / f"job_{row['logical_id']:03d}"
            )
            directory.mkdir(parents=True)
            metadata = {
                "schema": "hf_analysis_job_metadata_v3",
                "analysis_schema": "paul_pair_objects_primary_ground_v2",
                "analysis_implementation":
                    "one_pass_primary_ground_pair_analysis_v2",
                "analysis_version": "status_analysis_THnSparse_qq_v2",
                "analysis_profile": "central_primary_ground_v1",
                "pair_combinatorics_mode": "ordered_conditional_v1",
                "event_filter_schema": "all_events_v1",
                "event_filter_modulo": 0,
                "event_filter_remainder": -1,
                "same_sign_pair_factor": 1.0,
                "analysis_macro_sha256": macro_sha,
                "raw_input": row["stable_name"],
                "raw_sha256": digest(raw_file),
                "raw_schema": "hf_primary_ground_raw_v6",
                "raw_input_validation_contract":
                    "analysis_raw_input_fail_closed_v1",
                "raw_validation_evidence_mode":
                    "direct_preflight_only_v1",
                "raw_validation_receipt": None,
                "raw_validation_receipt_schema": None,
                "raw_validation_receipt_sha256": None,
                "origin_algorithm":
                    "signed_heavy_constituent_complete_mothers_unique_v4",
                "repository_commit": commit,
                "repository_dirty": False,
                "selector":
                    "hard_trigger_primary_ground__primary_ground_associate_v1",
                "campaign": CAMPAIGN,
                "tune": row["tune"],
                "logical_id": row["logical_id"],
                "purpose": row["purpose"],
            }
            (directory / "analysis_job_metadata.json").write_text(
                json.dumps(metadata, sort_keys=True) + "\n"
            )
            for filename in filenames:
                (directory / filename).write_bytes(
                    f"{row['tune']}:{row['logical_id']}:{filename}\n".encode()
                )

        production.mkdir(exist_ok=True)
        submit_file = production / "submit_gate_b.sub"
        submit_file.write_text("fixture submit\n")
        allocations = [
            {
                "tune": row["tune"],
                "logical_id": row["logical_id"],
                "attempt": row["attempt"],
                "seed": row["seed"],
                "campaign_ordinal": row["campaign_ordinal"],
                "pthat_min_override": row["pthat_min_override"],
                "multiplicity_audit_events": row["multiplicity_audit_events"],
                "repository_commit": row["repository_commit"],
                "effective_card_sha256": row["effective_card_sha256"],
            }
            for row in rows
        ]
        claim = {
            "schema": "hf_gate_b_submission_claim_v1",
            "state": "claimed_before_condor_submit",
            "campaign": CAMPAIGN,
            "campaign_ordinal": ORDINAL,
            "repository_commit": commit,
            "producer_executable_sha256": PRODUCER_SHA,
            "campaign_json_sha256": digest(campaign_dir / "campaign.json"),
            "candidate_manifest_sha256": digest(
                campaign_dir / "candidate_manifest.jsonl"
            ),
            "seed_ledger_sha256": digest(campaign_dir / "seed_ledger.jsonl"),
            "submit_file_sha256": digest(submit_file),
            "allocations": allocations,
        }
        receipt_dir = production / "submission_receipts"
        receipt_dir.mkdir()
        claim_path = receipt_dir / "gate_b_attempt0_submission_claim.json"
        claim_path.write_text(json.dumps(claim, sort_keys=True) + "\n")
        record = {
            "schema": "hf_gate_b_submission_record_v1",
            "state": "condor_submit_succeeded",
            "claim_sha256": digest(claim_path),
            "campaign": CAMPAIGN,
            "campaign_ordinal": ORDINAL,
        }
        (receipt_dir / "gate_b_attempt0_submitted.json").write_text(
            json.dumps(record, sort_keys=True) + "\n"
        )

        report = temporary / "all_report.json"
        inventory = temporary / "all_checksums.jsonl"
        output = run(
            sys.executable,
            str(VALIDATOR),
            str(campaign_dir),
            str(production),
            str(analysis),
            "--checkout-root",
            str(checkout),
            "--report",
            str(report),
            "--checksum-inventory",
            str(inventory),
        )
        assert "GATE_B_ANALYSIS_OUTPUTS_VALID" in output.stdout
        payload = json.loads(report.read_text())
        assert payload["status"] == "PASS"
        assert payload["pair_checksum_count"] == 2700
        assert len(inventory.read_text().splitlines()) == 2700

        central_staging = (
            analysis
            / "per_pthat"
            / "MONASH"
            / "job_000.partial.RUNNING"
        )
        central_staging.mkdir()
        interim_report = temporary / "interim_report.json"
        output = run(
            sys.executable,
            str(VALIDATOR),
            str(campaign_dir),
            str(production),
            str(analysis),
            "--checkout-root",
            str(checkout),
            "--scope",
            "sensitivity",
            "--report",
            str(interim_report),
        )
        assert "GATE_B_ANALYSIS_OUTPUTS_INTERIM_VALID" in output.stdout
        interim = json.loads(interim_report.read_text())
        assert interim["status"] == "INTERIM_PASS"
        assert interim["pair_checksum_count"] == 1800
        assert interim["out_of_scope_staging_directories"] == [
            "per_pthat/MONASH/job_000.partial.RUNNING"
        ]

    print("Gate-B analysis-validation tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
