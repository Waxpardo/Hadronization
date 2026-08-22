#!/usr/bin/env python3
"""Hand-computed anchors for extraction/harvest_deltas.py.

Every expected value below is worked out longhand beside the assertion.
Comparing the tool against its own output would prove agreement, not
correctness, so no anchor here is a captured value.
"""

from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extraction"))

from harvest_deltas import (  # noqa: E402
    CATEGORIES,
    category_fractions,
    counts_per_event,
    is_low_stat,
    read_category_counts,
)


def _write(path: Path, rows: list[tuple[str, float]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["category", "category_name", "from_species",
                         "from_closure", "difference", "relative"])
        for index, (name, value) in enumerate(rows):
            writer.writerow([index, name, value, value, 0.0, 0.0])


def test_category_fractions() -> None:
    # 25 + 50 + 20 + 5 = 100 exactly, so the percentages are the counts.
    counts = {"kCentralGround": 25.0, "kExcludedVector": 50.0,
              "kExcludedExcited": 20.0, "kMultiplyHeavy": 5.0}
    fracs = category_fractions(counts)
    assert fracs["kCentralGround"] == 25.0, fracs
    assert fracs["kExcludedVector"] == 50.0, fracs
    assert abs(sum(fracs.values()) - 100.0) < 1e-12, fracs

    # A total of 8: 3/8 = 37.5 %, 4/8 = 50 %, 1/8 = 12.5 %, absent = 0 %.
    counts = {"kCentralGround": 3.0, "kExcludedVector": 4.0, "kExcludedExcited": 1.0}
    fracs = category_fractions(counts)
    assert fracs["kCentralGround"] == 37.5, fracs
    assert fracs["kExcludedVector"] == 50.0, fracs
    assert fracs["kExcludedExcited"] == 12.5, fracs
    assert fracs["kMultiplyHeavy"] == 0.0, "an absent category is zero, not missing"

    try:
        category_fractions({"kCentralGround": 0.0})
    except ValueError:
        pass
    else:
        raise AssertionError("a zero total must refuse, not divide")


def test_is_low_stat() -> None:
    # The rule is "below 1000", so exactly 1000 is NOT low-stat.
    assert is_low_stat([999.0, 5000.0]) is True
    assert is_low_stat([1000.0, 5000.0]) is False
    assert is_low_stat([1000.0, 1000.0]) is False
    assert is_low_stat([0.0]) is True
    # The threshold is a parameter, and the comparison is on the minimum.
    assert is_low_stat([1500.0, 2000.0], threshold=1800.0) is True


def test_counts_per_event() -> None:
    # 5,376,793 counts over 10,000,000 events = 0.5376793 per event.
    assert abs(counts_per_event(5_376_793.0, 10_000_000) - 0.5376793) < 1e-12
    # The E5 defect signature: 130,000,000 over 10,000,000 is 13 per event.
    assert counts_per_event(130_000_000.0, 10_000_000) == 13.0
    try:
        counts_per_event(1.0, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero exposure must refuse")


def test_read_category_counts() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "per_category.csv"
        _write(path, [("kCentralGround", 7.0), ("kExcludedVector", 3.0)])
        counts = read_category_counts(path)
        assert counts == {"kCentralGround": 7.0, "kExcludedVector": 3.0}, counts


def test_reproduces_the_sealed_central_table() -> None:
    """The strongest anchor: the committed nominal must come back exactly.

    THREE_TUNE_CENTRAL_TABLE.md section 1 quotes MONASH at kCentralGround
    52.4959, kExcludedVector 46.4946, kExcludedExcited 1.0095, kMultiplyHeavy
    0.0000, and the I3 total at 53,662,416. Those are published numbers this
    file does not produce, so agreeing with them is a real check on the
    fraction arithmetic used for every delta.
    """
    anchor = ROOT / "AnalysisScripts/anchors/merged_monash_dedup/central/per_category.csv"
    counts = read_category_counts(anchor)
    assert sum(counts.values()) == 53_662_416.0, sum(counts.values())
    fracs = category_fractions(counts)
    assert round(fracs["kCentralGround"], 4) == 52.4959, fracs
    assert round(fracs["kExcludedVector"], 4) == 46.4946, fracs
    assert round(fracs["kExcludedExcited"], 4) == 1.0095, fracs
    assert round(fracs["kMultiplyHeavy"], 4) == 0.0000, fracs
    assert set(CATEGORIES) >= set(counts), counts


def main() -> int:
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"harvest deltas: {len(tests)} hand-anchored checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
