#!/usr/bin/env python3
"""Exercise and require canonical central-versus-ten-block closure."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    macro = ROOT / "Validation/ValidatePairBlockClosure.C"
    wrapper = ROOT / "Validation/validate_pair_block_closure.sh"
    merge = ROOT / "merging" / "merge_root_files.sh"
    macro_text = macro.read_text()
    wrapper_text = wrapper.read_text()
    merge_text = merge.read_text()
    assert "Hadronization::kPairDefinitions" in macro_text
    # This used to assert the literal '"hCorrelationsByOrigin"' appeared in the
    # macro. That pinned the implementation -- a hand-written list -- rather
    # than the behaviour, so it went red the moment the list was replaced by
    # the generated contract in b01536b, even though the closure's coverage had
    # strictly increased. It is the same failure mode as a fixture derived from
    # the code under test: assert what must be true of the product, not how the
    # source happens to spell it.
    contract = json.loads(
        (ROOT / "config/pair_file_object_contract_v1.json").read_text()
    )
    closure_checked = {
        row["name"] for row in contract["objects"]
        if row["closure"] == "checked"
        and row["merge_semantics"] == "additive_content"
    }
    assert "hCorrelationsByOrigin" in closure_checked
    assert "hFlavourClosure" in closure_checked, (
        "hFlavourClosure must stay closure-checked; it was silently skipped "
        "until b01536b"
    )
    assert "Hadronization::ClosureCheckedObjects" in macro_text, (
        "the closure must filter the generated contract, not restate names"
    )
    assert '"associate_origin_category_schema"' in macro_text
    assert '"associate_origin_category_labels"' in macro_text
    assert "InvariantObjectStringMatches" in macro_text
    assert "GetBinError2" in macro_text
    assert "GetSumw2()->At" in macro_text
    assert "central_pair_files=300 block_pair_files=3000" in wrapper_text
    # NOT `invariant_metadata_checks=600`. That literal was this test's own
    # copy of a number that is a function of the contract -- two hand-listed
    # objects x 300 -- and it went stale the moment v3 added the three
    # species-axis legibility objects, taking the real count to 1500. It is
    # the same defect as B12's pinned 1500, in the test rather than the
    # wrapper. The wrapper must DERIVE the count from the contract's
    # identity_checked axis, so that is what is asserted.
    assert "invariant_metadata_checks=$(( identity_objects * 300 ))" in (
        wrapper_text), (
        "validate_pair_block_closure.sh must derive invariant_metadata_checks "
        "from the contract's identity_checked axis rather than pinning it; a "
        "pinned count goes stale at the next contract change"
    )
    assert "identity_checked" in wrapper_text, (
        "the wrapper must read the identity_checked axis, not a hand-listed "
        "pair of object names"
    )
    assert "Hadronization::IdentityCheckedObjects" in macro_text, (
        "the closure must derive WHICH objects are identity-checked from the "
        "contract; a hand-written list is how an object gets added and "
        "silently never checked"
    )
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
