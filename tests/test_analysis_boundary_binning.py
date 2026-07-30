#!/usr/bin/env python3
"""Regression test for inclusive eta, delta-eta, and pT histogram edges."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    root = shutil.which("root")
    if root is None:
        raise RuntimeError("ROOT is required for the analysis-boundary test")
    result = subprocess.run(
        [
            root,
            "-l",
            "-b",
            "-q",
            "-e",
            ".L AnalysisScripts/status_analysis_THnSparse_qq.C",
            "-e",
            (
                "int boundary = TestStatusAnalysisBoundaryBinning(); "
                "int single = TestStatusAnalysisRejectsInputList(); "
                "gSystem->Exit(boundary || single);"
            ),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr
    if (
        result.returncode != 0
        or "ANALYSIS_BOUNDARY_BINNING_TEST_PASS" not in output
        or "ANALYSIS_SINGLE_INPUT_TEST_PASS" not in output
    ):
        raise AssertionError(
            f"analysis boundary-binning test failed:\n{output}"
        )
    print("analysis boundary-binning test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
