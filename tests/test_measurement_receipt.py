#!/usr/bin/env python3
"""A measurement receipt is a gate, including its failure cases."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "write_measurement_receipt.py"


def run_case(lines: list[str], expected_tag: str = "complete_root_TEST"):
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        receipt = base / "receipt.json"
        log = base / "render.log"
        staged = base / "staged.json"
        facts = base / "facts.json"
        assertion = base / "assertion.json"
        identities = [
            "BEAUTY|B^{+}|MONASH|B-|hDPhiM90_100",
            "BEAUTY|B^{+}|MONASH|Lambda_b|hDPhiM90_100",
        ]
        log.write_text("\n".join(lines) + "\n")
        staged.write_text("{}\n")
        facts.write_text(json.dumps({
            "expected_uncertainty_matrix_rows": len(identities),
            "expected_uncertainty_identities": identities,
        }))
        assertion.write_text(json.dumps({"passed": True}))
        result = subprocess.run([
            sys.executable, str(TOOL),
            "--receipt", str(receipt),
            "--campaign", "TEST",
            "--render-status", "0",
            "--log", str(log),
            "--staged", str(staged),
            "--assertion-status", "0",
            "--facts", str(facts),
            "--assertion", str(assertion),
            "--window-start", "1",
            "--window-end", "2",
            "--expected-tag", expected_tag,
        ], text=True, capture_output=True, check=False)
        return result, json.loads(receipt.read_text())


def complete_lines() -> list[str]:
    return [
        "central resolver tag=complete_root_TEST",
        ("UNCERTAINTY_MATRIX flavour=BEAUTY trigger=B^{+} tune=MONASH "
         "associate=B- bin=hDPhiM90_100 status=PASS"),
        ("UNCERTAINTY_MATRIX flavour=BEAUTY trigger=B^{+} tune=MONASH "
         "associate=Lambda_b bin=hDPhiM90_100 status=PASS"),
    ]


def test_complete_receipt_passes() -> None:
    result, receipt = run_case(complete_lines())
    assert result.returncode == 0, result.stdout + result.stderr
    assert receipt["completion_status"] == "PASS", receipt
    assert receipt["uncertainty_matrix_rows"] == 2, receipt


def test_missing_class_is_recorded_and_refused() -> None:
    result, receipt = run_case(complete_lines()[:-1])
    assert result.returncode != 0, result.stdout
    assert receipt["completion_status"] == "FAIL", receipt
    assert receipt["uncertainty_matrix_rows"] == 1, receipt
    assert receipt["missing_uncertainty_identities"], receipt


def test_wrong_dataset_tag_is_recorded_and_refused() -> None:
    lines = complete_lines()
    lines[0] = "central resolver tag=complete_root_CENTRAL"
    result, receipt = run_case(lines)
    assert result.returncode != 0, result.stdout
    assert receipt["completion_status"] == "FAIL", receipt
    assert receipt["resolved_complete_root_tags"] == [
        "complete_root_CENTRAL"
    ], receipt


def main() -> int:
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"measurement receipt: {len(tests)} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
