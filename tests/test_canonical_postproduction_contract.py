#!/usr/bin/env python3
"""Regression tests for the sealed canonical and manifest-only analysis path."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PATH = ROOT / "tools/canonical_manifest.py"
RENDERER = ROOT / "tools/render_analysis_submit.py"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_canonical():
    specification = importlib.util.spec_from_file_location(
        "canonical_manifest_contract", CANONICAL_PATH
    )
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def load_module(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def write_freeze(directory: Path, module) -> list[dict]:
    rows = []
    for tune_index, tune in enumerate(TUNES):
        for slot in range(100):
            logical_id = slot
            row = {
                "schema": module.ROW_SCHEMA,
                "campaign": "canonical_test",
                "campaign_ordinal": 19,
                "tune": tune,
                "tune_ordinal": tune_index,
                "canonical_slot": slot,
                "block": slot % 10,
                "block_position": slot // 10,
                "logical_id": logical_id,
                "role": "primary",
                "attempt": 0,
                "seed": 1 + tune_index * 1000 + slot,
                "requested_successes": 1_000_000,
                "pthat_min_override": "NONE",
                "effective_pthat_min": 1.0,
                "multiplicity_audit_events": 0,
                "effective_card_sha256": f"{tune_index + 1:x}" * 64,
                "producer_executable_sha256": "4" * 64,
                "repository_commit": "5" * 40,
                "raw_schema": module.RAW_SCHEMA,
                "origin_algorithm": module.ORIGIN_ALGORITHM,
                "selector": module.SELECTOR,
                "species_registry_sha256": "6" * 64,
                "pair_registry_sha256": "7" * 64,
                "tune_difference_allowlist_schema":
                    module.TUNE_ALLOWLIST_SCHEMA,
                "tune_difference_allowlist_sha256": "8" * 64,
                "raw_path": f"raw/{tune}/hf_{tune}_job{slot:03d}.root",
                "raw_bytes": 1000 + slot,
                "raw_sha256": hashlib.sha256(
                    f"{tune}:{slot}".encode()
                ).hexdigest(),
                "attempt_start_claim_path":
                    f"attempt_starts/{tune}/job_{slot:03d}/attempt_000.json",
                "attempt_start_claim_sha256": hashlib.sha256(
                    f"start:{tune}:{slot}".encode()
                ).hexdigest(),
                "producing_cluster_id": f"cluster{tune_index}",
                "producing_process_id": str(slot),
                "attempt_receipt_path":
                    f"attempt_metadata/{tune}/job_{slot:03d}.json",
                "attempt_receipt_sha256": hashlib.sha256(
                    f"attempt:{tune}:{slot}".encode()
                ).hexdigest(),
                "raw_validation_receipt_path":
                    f"raw_validation/{tune}/job_{slot:03d}/"
                    "attempt_000/receipt.json",
                "raw_validation_receipt_sha256": hashlib.sha256(
                    f"validation:{tune}:{slot}".encode()
                ).hexdigest(),
                "raw_validation_log_path":
                    f"raw_validation/{tune}/job_{slot:03d}/"
                    "attempt_000/validate_raw_output.log",
                "raw_validation_log_sha256": hashlib.sha256(
                    f"log:{tune}:{slot}".encode()
                ).hexdigest(),
                "allocation_authorization_path":
                    "submission_receipts/"
                    "full_candidates_attempt0_submission_claim.json",
                "allocation_authorization_sha256": "9" * 64,
                "submission_record_path":
                    "submission_receipts/"
                    "full_candidates_attempt0_submitted.json",
                "submission_record_sha256": "a" * 64,
                "validation_receipt_path": module.VALIDATION_RECEIPT_NAME,
                "selection_reason": "primary_initial_allocation",
                "selection_approval": "full_candidates_attempt0_claim",
            }
            row["production_definition_sha256"] = (
                module.production_definition(row)
            )
            rows.append(row)
    manifest = directory / "canonical_manifest.jsonl"
    manifest.write_text(module.jsonl_text(rows))
    block_hashes = {}
    for block in range(10):
        path = directory / f"block_{block + 1:02d}.jsonl"
        path.write_text(
            module.jsonl_text([row for row in rows if row["block"] == block])
        )
        block_hashes[path.name] = sha(path)
    summary = {
        "schema": module.SUMMARY_SCHEMA,
        "state": "AWAITING_EXHAUSTIVE_RAW_VALIDATION",
        "campaign": "canonical_test",
        "campaign_ordinal": 19,
        "canonical_manifest_sha256": sha(manifest),
        "block_manifest_sha256": block_hashes,
        "jobs_per_tune": 100,
        "successful_events_per_job": 1_000_000,
        "successful_events_per_tune": 100_000_000,
        "block_count": 10,
        "jobs_per_tune_per_block": 10,
        "raw_schema": module.RAW_SCHEMA,
        "origin_algorithm": module.ORIGIN_ALGORITHM,
        "selector": module.SELECTOR,
        "species_registry_sha256": "6" * 64,
        "pair_registry_sha256": "7" * 64,
        "tune_difference_allowlist_schema":
            module.TUNE_ALLOWLIST_SCHEMA,
        "tune_difference_allowlist_sha256": "8" * 64,
        "submission_claim_sha256": "9" * 64,
        "submission_record_sha256": "a" * 64,
        "physics_origin_signoff_sha256": "e" * 64,
        "full_production_gate_authorization_sha256": "f" * 64,
        "registry_baseline_sha256": "1" * 64,
        "global_submission_claim_sha256": "2" * 64,
        "campaign_json_sha256": "b" * 64,
        "candidate_manifest_sha256": "c" * 64,
        "seed_ledger_sha256": "d" * 64,
        "validation_receipt_path": module.VALIDATION_RECEIPT_NAME,
        "seal_path": module.SEAL_NAME,
    }
    (directory / "freeze_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return rows


def test_structural_freeze(module, temporary: Path) -> None:
    freeze = temporary / "freeze"
    freeze.mkdir()
    rows = write_freeze(freeze, module)
    module.validate_directory(freeze, require_seal=False)
    for block in range(10):
        selected = [row for row in rows if row["block"] == block]
        assert len(selected) == 30
        assert all(
            sum(row["tune"] == tune for row in selected) == 10
            for tune in TUNES
        )

    block = freeze / "block_01.jsonl"
    original = block.read_text()
    block.write_text(original.replace('"canonical_slot": 0', '"canonical_slot": 1', 1))
    try:
        module.validate_directory(freeze, require_seal=False)
    except ValueError:
        pass
    else:
        raise AssertionError("tampered deterministic block was accepted")
    block.write_text(original)


def test_launch_provenance_is_preserved(module, temporary: Path) -> None:
    campaign_dir = temporary / "campaigns" / "launch_provenance_test"
    production = temporary / "Production" / "launch_provenance_test"
    receipts = production / "submission_receipts"
    registry = temporary / "shared_registry"
    claims = registry / "claims"
    campaign_dir.mkdir(parents=True)
    receipts.mkdir(parents=True)
    claims.mkdir(parents=True)

    campaign = {
        "campaign": "launch_provenance_test",
        "campaign_ordinal": 81,
        "repository_commit": "5" * 40,
        "candidate_slots": {"MONASH": 1},
    }
    (campaign_dir / "campaign.json").write_text(
        json.dumps(campaign, indent=2, sort_keys=True) + "\n"
    )
    (campaign_dir / "candidate_manifest.jsonl").write_text("{}\n")
    ledger = campaign_dir / "seed_ledger.jsonl"
    ledger.write_text('{"seed": 123456789}\n')
    signoff = campaign_dir / "PHYSICS_ORIGIN_SIGNOFF.json"
    signoff.write_text('{"approved":true}\n')
    signoff_sha = sha(signoff)
    gate_authorization = (
        campaign_dir / "FULL_PRODUCTION_GATE_AUTHORIZATION.json"
    )
    gate_authorization.write_text(
        json.dumps(
            {
                "schema": "hf_full_production_gate_authorization_v1",
                "approved": True,
                "campaign": campaign["campaign"],
                "campaign_ordinal": campaign["campaign_ordinal"],
                "repository_commit": campaign["repository_commit"],
                "physics_origin_signoff_sha256": signoff_sha,
            },
            sort_keys=True,
        )
        + "\n"
    )
    gate_authorization_sha = sha(gate_authorization)
    baseline = registry / "reservation_baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "schema": "hf_submission_registry_baseline_v1",
                "repository_identity": "github.com/waxpardo/hadronization",
                "reviewer": "Canonical contract test",
                "historical_reservations": [],
            },
            sort_keys=True,
        )
        + "\n"
    )
    baseline_sha = sha(baseline)
    submit = production / "submit_candidates.sub"
    submit.write_text("queue 1\n")
    claim_path = receipts / module.FULL_CLAIM.name
    claim = {
        "schema": "hf_full_submission_claim_v1",
        "state": "claimed_before_condor_submit",
        "submission_kind": "full",
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
        "repository_commit": campaign["repository_commit"],
        "campaign_json_sha256": sha(campaign_dir / "campaign.json"),
        "candidate_manifest_sha256":
            sha(campaign_dir / "candidate_manifest.jsonl"),
        "producer_executable_sha256": "4" * 64,
        "seed_ledger_prefix_bytes": ledger.stat().st_size,
        "seed_ledger_sha256": sha(ledger),
        "allocations": [{"seed": 123456789}],
        "submit_file_sha256": sha(submit),
        "physics_origin_signoff_sha256": signoff_sha,
        "full_production_gate_authorization_sha256":
            gate_authorization_sha,
        "repository_identity": "github.com/waxpardo/hadronization",
        "global_submission_registry": str(registry),
        "registry_baseline_sha256": baseline_sha,
        "reserved_seed_intervals": [[123456789, 123456789]],
    }
    claim_path.write_text(
        json.dumps(claim, indent=2, sort_keys=True) + "\n"
    )
    global_claim = claims / f"{campaign['campaign']}.json"
    global_claim.write_text(
        json.dumps(
            {
                "schema": "hf_global_submission_claim_v1",
                "state": "reserved_before_condor_submit",
                "repository_identity": claim["repository_identity"],
                "global_submission_registry": str(registry),
                "registry_baseline_sha256": baseline_sha,
                "campaign": campaign["campaign"],
                "campaign_ordinal": campaign["campaign_ordinal"],
                "submission_kind": "full",
                "repository_commit": campaign["repository_commit"],
                "physics_origin_signoff_sha256": signoff_sha,
                "full_production_gate_authorization_sha256":
                    gate_authorization_sha,
                "reserved_seed_intervals": claim["reserved_seed_intervals"],
                "local_receipt_sha256": sha(claim_path),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    record = receipts / module.FULL_RECORD.name
    record.write_text(
        json.dumps(
            {
                "schema": "hf_full_submission_record_v1",
                "state": "condor_submit_succeeded",
                "submission_kind": "full",
                "campaign": campaign["campaign"],
                "campaign_ordinal": campaign["campaign_ordinal"],
                "claim_sha256": sha(claim_path),
                "condor_first_process": 0,
                "condor_last_process": 0,
                "condor_process_count": 1,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    _, _, _, provenance = module.validate_submission_receipts(
        campaign_dir, production, campaign
    )
    assert provenance == {
        "physics_origin_signoff_sha256": signoff_sha,
        "full_production_gate_authorization_sha256":
            gate_authorization_sha,
        "registry_baseline_sha256": baseline_sha,
        "global_submission_claim_sha256": sha(global_claim),
    }

    gate_authorization.write_text('{"approved":false}\n')
    try:
        module.validate_submission_receipts(
            campaign_dir, production, campaign
        )
    except ValueError as error:
        assert "gate-authorization checksum differs" in str(error)
    else:
        raise AssertionError("changed gate authorization was accepted")


def test_renderer(temporary: Path) -> None:
    checkout = temporary / "checkout"
    (checkout / "AnalysisScripts").mkdir(parents=True)
    (checkout / "AnalysisScripts/status_analysis_THnSparse_qq.C").write_text(
        "// fixture\n"
    )
    (checkout / "run_status_analysis.sh").write_text("#!/bin/sh\n")
    subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Canonical Test"],
        cwd=checkout,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "canonical@example.invalid"],
        cwd=checkout,
        check=True,
    )
    subprocess.run(["git", "add", "."], cwd=checkout, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "fixture"], cwd=checkout, check=True
    )
    production = temporary / "production"
    analysis = temporary / "analysis"
    rows = []
    for tune_index, tune in enumerate(TUNES):
        for slot in range(100):
            raw = production / "raw" / tune / f"hf_{tune}_job{slot:03d}.root"
            raw.parent.mkdir(parents=True, exist_ok=True)
            raw.write_bytes(f"{tune}:{slot}".encode())
            evidence = (
                production
                / "raw_validation"
                / tune
                / f"job_{slot:03d}"
                / "attempt_000"
            )
            evidence.mkdir(parents=True)
            log = evidence / "validate_raw_output.log"
            log.write_text(
                "RAW_VALIDATION_SUMMARY errors=0 entries=1\n"
            )
            receipt = evidence / "receipt.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schema": "hf_raw_validation_receipt_v1",
                        "result": "PASS",
                        "validated_utc": "2026-07-30T00:00:00+00:00",
                        "validator_exit_status": 0,
                        "validator_wrapper_sha256": "1" * 64,
                        "validator_macro_sha256": "2" * 64,
                        "validator_dependency_sha256": {
                            "fixture.h": "3" * 64,
                        },
                        "validation_log_name": log.name,
                        "validation_log_sha256": sha(log),
                        "output_sha256": sha(raw),
                        "output_bytes": raw.stat().st_size,
                        "expected_provenance": {
                            "campaign": "render_test",
                            "tune": tune,
                            "logical_id": slot,
                        },
                    },
                    sort_keys=True,
                )
                + "\n"
            )
            rows.append(
                {
                    "schema": "hf_canonical_raw_manifest_v2",
                    "campaign": "render_test",
                    "tune": tune,
                    "canonical_slot": slot,
                    "logical_id": slot,
                    "raw_path": str(raw.relative_to(production)),
                    "raw_sha256": sha(raw),
                    "raw_validation_receipt_path": str(
                        receipt.relative_to(production)
                    ),
                    "raw_validation_receipt_sha256": sha(receipt),
                    "raw_validation_log_path": str(
                        log.relative_to(production)
                    ),
                    "raw_validation_log_sha256": sha(log),
                }
            )
    manifest = temporary / "canonical.jsonl"
    manifest.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )
    output = temporary / "canonical.sub"
    subprocess.run(
        [
            sys.executable,
            str(RENDERER),
            str(manifest),
            str(checkout),
            str(production),
            str(analysis),
            str(output),
        ],
        check=True,
    )
    text = output.read_text()
    assert "getenv = False" in text
    assert "getenv = True" not in text
    assert "$(MANIFEST_SHA256)" in text
    assert "$(RAW_VALIDATION_RECEIPT_SHA256)" in text
    assert text.count("\nrender_test,MONASH,") == 100
    assert text.count("\nrender_test,JUNCTIONS,") == 100
    assert text.count("\nrender_test,CLOSEPACKING,") == 100
    receipt = production / rows[0]["raw_validation_receipt_path"]
    payload = json.loads(receipt.read_text())
    payload["result"] = "FAIL"
    receipt.write_text(json.dumps(payload, sort_keys=True) + "\n")
    rejected = subprocess.run(
        [
            sys.executable,
            str(RENDERER),
            str(manifest),
            str(checkout),
            str(production),
            str(analysis),
            str(temporary / "tampered_receipt.sub"),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected.returncode != 0


def test_merge_contract_source() -> None:
    source = (ROOT / "AnalysisScripts/MergeAnalysisObjects.C").read_text()
    assert 'objectName == "input_file_count"' in source
    assert 'keyName == "upstream_raw_sha256"' in source
    assert 'keyName == "upstream_effective_settings_sha256"' in source
    assert "HistogramsCompatible" in source
    assert "SparseHistogramsCompatible" in source
    assert "!targetHist->Add(sourceHist)" in source
    assert "targetSparse->Add(sourceSparse)" in source
    assert "TestMergeAnalysisAxisCompatibility" in source
    canonical = (
        ROOT / "AnalysisScripts/MergeCanonicalAnalysis.C"
    ).read_text()
    assert "expectedSlotCount <= 0" in canonical
    subsamples = (ROOT / "make_subsamples.sh").read_text()
    assert 'exec "${script_dir}/merge_root_files.sh" "$@"' in subsamples
    assert "random" not in subsamples.lower().replace("no random", "")
    merge = (ROOT / "merge_root_files.sh").read_text()
    assert "validate_pair_block_closure.sh" in merge
    assert "canonical_merge_contract.py" in merge
    closure = (
        ROOT / "Validation/ValidatePairBlockClosure.C"
    ).read_text()
    assert "Hadronization::kPairDefinitions" in closure
    assert "SparseEqualsBlockSum" in closure
    assert "HistogramEqualsBlockSum" in closure
    merged = load_module(
        "merged_pair_provenance_contract",
        ROOT / "tools/merged_pair_provenance.py",
    )
    analysis = load_module(
        "analysis_output_validation_contract",
        ROOT / "tools/validate_analysis_outputs.py",
    )
    assert len(merged.expected_pair_filenames(ROOT)) == 300
    assert len(analysis.expected_pair_filenames(ROOT)) == 300
    assert analysis.ANALYSIS_JOB_SCHEMA == "hf_analysis_job_metadata_v3"
    assert "raw_validation_receipt_sha256" in analysis.METADATA_KEYS
    assert (
        'report.get("schema") != "hf_analysis_output_validation_v3"'
        in (ROOT / "tools/merged_pair_provenance.py").read_text()
    )


def main() -> int:
    module = load_canonical()
    with tempfile.TemporaryDirectory(
        prefix="hadronization_canonical_contract_"
    ) as raw:
        temporary = Path(raw)
        test_structural_freeze(module, temporary)
        test_launch_provenance_is_preserved(module, temporary)
        test_renderer(temporary)
    test_merge_contract_source()
    print("canonical post-production contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
