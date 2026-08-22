#!/usr/bin/env python3
"""The `systematic_variation` selector status, and what it refuses.

A variation campaign must be selectable, because the selector is what the
resolver reads: on 2026-08-19 five renders loaded the right configuration and
read the CENTRAL campaign's data, and the only alternative to a selector row
was overriding HADRONIZATION_COMPLETE_ROOT_TAG by hand -- disabling the guard
instead of satisfying it.

The one thing a variation may never be is publishable, and this asserts that
the loader enforces it rather than trusting the field.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import dataset_selector  # noqa: E402

LIVE = ROOT / "config" / "dataset_selector_hf_sys_mur_up.json"


def _load(doc: dict):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "selector.json"
        path.write_text(json.dumps(doc))
        return dataset_selector.load(path, ROOT)


def test_a_live_variation_row_loads() -> None:
    active, row = dataset_selector.load(LIVE, ROOT)
    assert row["status"] == "systematic_variation", row["status"]
    assert row["publication_eligible"] is False, row
    assert row["complete_root_tag"] == "complete_root_HF_SYS_MUR_UP", row
    assert row["measurement_config"].endswith(
        "HF_SYS_MUR_UP_THREETUNE_THnSparse_complete_root.json"), row
    assert row["subsample_base"].endswith(
        "SUBSAMPLES_HF_SYS_MUR_UP/combined_root_subSamples"), row
    assert active == "hf_sys_mur_up_variation", active


def test_a_publishable_variation_is_refused() -> None:
    """THE MUTATION. Flip the one field the status exists to constrain."""
    doc = json.loads(LIVE.read_text())
    doc["datasets"][doc["active_dataset"]]["publication_eligible"] = True
    try:
        _load(doc)
    except ValueError as error:
        assert "publication dataset" in str(error), error
        return
    raise AssertionError(
        "MUTATION SURVIVED: a systematic variation declared itself "
        "publication-eligible and the loader accepted it")


def test_the_contract_fields_are_still_required() -> None:
    for key, marker in (("raw_schema", "raw schema"),
                        ("selector", "selector"),
                        ("complete_root_tag", "requires complete_root_tag")):
        doc = json.loads(LIVE.read_text())
        row = doc["datasets"][doc["active_dataset"]]
        row[key] = "" if key == "complete_root_tag" else "wrong_value"
        try:
            _load(doc)
        except ValueError as error:
            assert marker in str(error), (key, str(error))
            continue
        raise AssertionError(f"a wrong {key} must be refused")


def test_a_variation_requires_an_existing_harvest_config() -> None:
    for value, marker in (("", "requires measurement_config"),
                          ("plotting/no-such-config.json", "does not exist")):
        doc = json.loads(LIVE.read_text())
        doc["datasets"][doc["active_dataset"]]["measurement_config"] = value
        try:
            _load(doc)
        except ValueError as error:
            assert marker in str(error), str(error)
            continue
        raise AssertionError(f"measurement_config={value!r} was accepted")


def test_the_sealed_row_is_untouched_by_this_status() -> None:
    """The sealed campaign must still load as canonical and publishable."""
    active, row = dataset_selector.load(
        ROOT / "config" / "dataset_selector_hf_run3_v1.json", ROOT)
    assert active == "hf_run3_v1_candidate", active
    assert row["status"] == "canonical", row["status"]
    assert row["publication_eligible"] is True, row
    assert row["complete_root_tag"] == "complete_root_HF_RUN3_V1", row


def main() -> int:
    tests = [v for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"variation selector status: {len(tests)} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
