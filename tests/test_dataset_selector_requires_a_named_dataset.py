"""The resolver must refuse to pick a dataset nobody named.

`docs/NIKHEF_CLEANUP_PLAN.md` §11.2 specifies this change and its two cases.
The defect it closes is not hypothetical: a silent `active_dataset` default is
what let five variation renders read the central campaign. A resolver that
answers a question nobody asked will answer it wrongly, and the wrong answer
looks exactly like a right one -- the render succeeds, emits all its rows, and
reports the wrong dataset.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import dataset_selector  # noqa: E402

COMBINED = ROOT / "config" / "dataset_selector.json"
LEGACY_ROW = "legacy_21_06_2026"


def test_resolving_with_no_dataset_named_raises_and_lists_the_valid_keys() -> None:
    """Case 1 of §11.2. The message must be actionable, not just a refusal."""
    try:
        dataset_selector.load(COMBINED, ROOT)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("the resolver picked a dataset nobody named")
    assert "no dataset named" in message, message
    keys = set(json.loads(COMBINED.read_text())["datasets"])
    assert keys, "the combined selector defines no datasets"
    for key in keys:
        assert key in message, f"the refusal does not name {key}: {message}"


def test_the_legacy_row_is_still_selectable_by_name() -> None:
    """Case 2 of §11.2. Only the silent fallback goes; the row stays usable.

    The regression path must stay open -- `RootFiles/HF/`'s 326.6 G is
    protected by this row, and removing the row rather than the default would
    have made the largest directory on the Nikhef volume look unreferenced.
    """
    active, row = dataset_selector.load(COMBINED, ROOT, LEGACY_ROW)
    assert active == LEGACY_ROW
    assert row["status"] == "legacy_regression_default"
    assert row["publication_eligible"] is False


def test_the_combined_selector_declares_no_default() -> None:
    """The mutation guard: restoring the default must fail this test.

    Without this, a later edit could put `active_dataset` back and the two
    tests above would keep passing -- the first only asserts that SOME refusal
    happens when no dataset is named, and a restored default would stop it
    being reached at all.
    """
    assert json.loads(COMBINED.read_text())["active_dataset"] is None


def test_a_per_campaign_selector_still_resolves_from_its_own_default() -> None:
    """The change is scoped. A one-row file naming itself is not a silent default."""
    active, row = dataset_selector.load(
        ROOT / "config" / "dataset_selector_hf_run3_v1.json", ROOT
    )
    assert active == "hf_run3_v1_candidate"
    assert row["status"] == "canonical"


def test_naming_a_dataset_the_file_does_not_define_raises_with_the_keys() -> None:
    try:
        dataset_selector.load(COMBINED, ROOT, "no_such_dataset")
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("an undefined dataset key resolved")
    assert "no_such_dataset" in message
    assert LEGACY_ROW in message, message


def main() -> int:
    test_resolving_with_no_dataset_named_raises_and_lists_the_valid_keys()
    test_the_legacy_row_is_still_selectable_by_name()
    test_the_combined_selector_declares_no_default()
    test_a_per_campaign_selector_still_resolves_from_its_own_default()
    test_naming_a_dataset_the_file_does_not_define_raises_with_the_keys()
    print("dataset selector named-dataset tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
