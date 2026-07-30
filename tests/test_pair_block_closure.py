#!/usr/bin/env python3
"""Exercise and require canonical central-versus-ten-block closure."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    macro = ROOT / "Validation/ValidatePairBlockClosure.C"
    wrapper = ROOT / "Validation/validate_pair_block_closure.sh"
    merge = ROOT / "merge_root_files.sh"
    macro_text = macro.read_text()
    wrapper_text = wrapper.read_text()
    merge_text = merge.read_text()
    assert "Hadronization::kPairDefinitions" in macro_text
    assert '"hCorrelationsByOrigin"' in macro_text
    assert '"associate_origin_category_schema"' in macro_text
    assert '"associate_origin_category_labels"' in macro_text
    assert "InvariantObjectStringMatches" in macro_text
    assert "GetBinError2" in macro_text
    assert "GetSumw2()->At" in macro_text
    assert "central_pair_files=300 block_pair_files=3000" in wrapper_text
    assert "invariant_metadata_checks=600" in wrapper_text
    assert "validate_pair_block_closure.sh" in merge_text

    root = shutil.which("root")
    if root is None:
        raise RuntimeError("ROOT is required for the pair-block closure test")
    result = subprocess.run(
        [
            root,
            "-l",
            "-b",
            "-q",
            "-e",
            ".L Validation/ValidatePairBlockClosure.C",
            "-e",
            "gSystem->Exit(TestPairBlockClosureArithmetic());",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr
    marker = (
        "PAIR_BLOCK_CLOSURE_TEST errors=0 "
        "exact_content_sumw2_sum_accepted=true "
        "histogram_mutation_rejected=true "
        "sparse_mutation_rejected=true"
    )
    if result.returncode != 0 or marker not in output:
        raise AssertionError(f"pair-block closure test failed:\n{output}")
    print("pair-block closure test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
