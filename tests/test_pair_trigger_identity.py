#!/usr/bin/env python3
"""Reject pair directories whose shared event/trigger histograms differ."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    root = shutil.which("root")
    if root is None:
        raise RuntimeError("ROOT is required for the trigger-identity test")
    result = subprocess.run(
        [
            root,
            "-l",
            "-b",
            "-q",
            "-e",
            ".L Validation/ValidatePairDirectory.C",
            "-e",
            "gSystem->Exit(TestPairHistogramIdentity());",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr
    marker = (
        "PAIR_HISTOGRAM_IDENTITY_TEST errors=0 "
        "trigger_equal_count_weight_redistribution_rejected=true "
        "multiplicity_equal_integral_entries_redistribution_rejected=true"
    )
    if result.returncode != 0 or marker not in output:
        raise AssertionError(
            f"pair trigger-histogram identity test failed:\n{output}"
        )
    print("pair histogram-identity test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
