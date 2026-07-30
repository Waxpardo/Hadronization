#!/usr/bin/env python3
"""Adversarial checks for the raw-v5 analysis preflight contract."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_source_contract() -> None:
    macro = (
        ROOT / "AnalysisScripts/status_analysis_THnSparse_qq.C"
    ).read_text()
    wrapper = (ROOT / "run_status_analysis.sh").read_text()
    renderer = (ROOT / "tools/render_analysis_submit.py").read_text()
    validator = (ROOT / "tools/validate_analysis_outputs.py").read_text()
    for field in (
        "complete",
        "requested_successes",
        "attempts",
        "successful_events",
        "failed_attempts",
        "tree_entries",
        "content_decode_failures",
        "heavy_flavour_conservation_failures",
        "origin_classification_failures",
        "primary_all_heavy_match_failures",
        "multiplicity_overflow",
        "multiplicity_strong_em_overflow",
    ):
        assert f'"{field}"' in macro
    assert "current.attempts !=" in macro
    assert "current.successfulEvents + current.failedAttempts" in macro
    assert "non-finite raw event weight" in macro
    assert "analysis_raw_input_fail_closed_v1" in macro
    assert "immutable_receipt_plus_direct_preflight_v1" in wrapper
    assert (
        "canonical analysis requires its immutable raw-validation receipt"
        in wrapper
    )
    assert "RAW_VALIDATION_RECEIPT_SHA256" in renderer
    assert 'ANALYSIS_JOB_SCHEMA = "hf_analysis_job_metadata_v3"' in validator


def test_root_failure_injections() -> None:
    macro = ROOT / "Validation/TestAnalysisRawInputContract.C"
    result = subprocess.run(
        ["root", "-l", "-b", "-q", f"{macro}()"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    combined = result.stdout + result.stderr
    if (
        result.returncode != 0
        or "ANALYSIS_RAW_CONTRACT_TEST_SUMMARY failures=0"
        not in combined
    ):
        raise AssertionError(
            "analysis raw contract ROOT test failed:\n"
            + "\n".join(combined.splitlines()[-80:])
        )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_immutable_receipt_binding() -> None:
    validator = ROOT / "tools/validate_analysis_raw_receipt.py"
    with tempfile.TemporaryDirectory(
        prefix="hadronization_analysis_receipt_"
    ) as raw_directory:
        directory = Path(raw_directory)
        raw = directory / "input.root"
        raw.write_bytes(b"raw fixture")
        log = directory / "validate_raw_output.log"
        log.write_text(
            "RAW_VALIDATION_SUMMARY errors=0 entries=1\n"
        )
        receipt = directory / "receipt.json"
        payload = {
            "schema": "hf_raw_validation_receipt_v1",
            "result": "PASS",
            "validated_utc": "2026-07-30T00:00:00+00:00",
            "validator_exit_status": 0,
            "validator_wrapper_sha256": "1" * 64,
            "validator_macro_sha256": "2" * 64,
            "validator_dependency_sha256": {"fixture.h": "3" * 64},
            "validation_log_name": log.name,
            "validation_log_sha256": digest(log),
            "output_sha256": digest(raw),
            "output_bytes": raw.stat().st_size,
            "expected_provenance": {
                "campaign": "RAW_CONTRACT_TEST",
                "tune": "MONASH",
                "logical_id": 0,
            },
        }
        receipt.write_text(json.dumps(payload, sort_keys=True) + "\n")

        def run(receipt_sha: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [
                    sys.executable,
                    str(validator),
                    str(receipt),
                    str(raw),
                    digest(raw),
                    receipt_sha,
                    "RAW_CONTRACT_TEST",
                    "MONASH",
                    "0",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

        assert run(digest(receipt)).returncode == 0
        log.write_text(
            "RAW_VALIDATION_SUMMARY errors=0 entries=1\n"
            "RAW_VALIDATION_ERROR injected after receipt\n"
        )
        stale_log = run(digest(receipt))
        assert stale_log.returncode != 0
        log.write_text(
            "RAW_VALIDATION_SUMMARY errors=0 entries=1\n"
        )
        payload["result"] = "FAIL"
        payload["validation_log_sha256"] = digest(log)
        receipt.write_text(json.dumps(payload, sort_keys=True) + "\n")
        semantic_tamper = run(digest(receipt))
        assert semantic_tamper.returncode != 0


def main() -> int:
    test_source_contract()
    test_root_failure_injections()
    test_immutable_receipt_binding()
    print("analysis raw-input contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
