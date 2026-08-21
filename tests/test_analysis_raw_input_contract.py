#!/usr/bin/env python3
"""Adversarial checks for the raw-v5 analysis preflight contract."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_source_contract() -> None:
    macro = (
        ROOT / "analysis/status_analysis_THnSparse_qq.C"
    ).read_text()
    wrapper = (ROOT / "analysis" / "run_status_analysis.sh").read_text()
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
        "multiplicity_wide_overflow",
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
    assert "kAnalysisSchema" in wrapper
    assert 'schema_version_tags' in wrapper
    assert '"analysis_schema": analysis_schema' in wrapper
    assert '"analysis_schema": metadata["analysis_schema"]' in validator
    for stale_literal in (
        '"paul_pair_objects_primary_ground_v2"',
        '"paul_pair_objects_primary_ground_v3"',
    ):
        assert stale_literal not in wrapper


def test_root_failure_injections() -> None:
    macro = ROOT / "Validation/TestAnalysisRawInputContract.C"
    root = shutil.which("root")
    if root is None:
        raise RuntimeError("ROOT is required for the raw-input contract test")
    result = subprocess.run(
        [root, "-l", "-b", "-q", f"{macro}()"],
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


# test_immutable_receipt_binding was removed with the analysis raw-receipt
# validator: it exercised the gate layer's authorisation chain, not the
# analysis input contract. The two tests above cover that contract.



def main() -> int:
    test_source_contract()
    test_root_failure_injections()
    print("analysis raw-input contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
