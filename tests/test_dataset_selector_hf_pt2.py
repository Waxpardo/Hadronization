#!/usr/bin/env python3
"""The HF_PT2 canonical-candidate override selector.

The HF_PT2 row is carried in two committed files: the main selector, which
records it but does not activate it, and the override selector, which activates
it for the merge-consuming plotting targets. That duplication is deliberate --
activating HF_PT2 in the main selector would disable the legacy-regression
target, which requires the *active* status to be legacy_regression_default
(plotting/run_paper_plots.sh:243-247). The cost of the duplication is
drift, so it is tested here.
"""
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/dataset_selector.py"
MAIN = ROOT / "config/dataset_selector.json"
OVERRIDE = ROOT / "config/dataset_selector_hf_pt2.json"
ROW = "hf_pt2_candidate"


def main() -> int:
    main_payload = json.loads(MAIN.read_text())
    override_payload = json.loads(OVERRIDE.read_text())

    # The main selector must keep the legacy regression default active, or the
    # legacy-regression diagnostic stops being runnable.
    assert main_payload["active_dataset"] == "legacy_21_06_2026", (
        "the main selector must keep legacy_21_06_2026 active"
    )
    assert override_payload["active_dataset"] == ROW

    # The duplicated row must stay identical in both files.
    assert ROW in main_payload["datasets"], f"{ROW} absent from {MAIN.name}"
    assert main_payload["datasets"][ROW] == override_payload["datasets"][ROW], (
        f"the {ROW} row has drifted between "
        f"{MAIN.name} and {OVERRIDE.name}"
    )

    row = override_payload["datasets"][ROW]
    assert row["status"] == "canonical_candidate"
    assert row["publication_eligible"] is False, (
        "HF_PT2 is a validation campaign and must never be publication eligible"
    )
    assert row["campaign"] == "HF_PT2"

    result = subprocess.run(
        [sys.executable, str(TOOL), "validate", "--selector", str(OVERRIDE)],
        check=True,
        text=True,
        capture_output=True,
    )
    assert f"active={ROW}" in result.stdout
    assert "status=canonical_candidate" in result.stdout
    assert "blocks=10" in result.stdout

    shell = subprocess.run(
        [sys.executable, str(TOOL), "shell", "--selector", str(OVERRIDE)],
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    assert "HADRONIZATION_DATASET_STATUS=canonical_candidate" in shell
    assert "HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE=false" in shell
    assert "HADRONIZATION_COMPLETE_ROOT_TAG=complete_root_HF_PT2" in shell

    print("hf_pt2 dataset-selector override tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
