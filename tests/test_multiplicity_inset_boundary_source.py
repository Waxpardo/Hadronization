#!/usr/bin/env python3
"""The multiplicity figures consume the tune-local percentile contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "plotting/Plot_InclusiveKinematicSpectra_Raw.C"
BOUNDARY = ROOT / "plotting/Plot_MultiplicityDistribution_PercentileBoundaries.C"
PLOTTER = ROOT / "plotting/improvedPlotting_THnSparse.C"
UTILITY = ROOT / "plotting/MultiplicityBoundaryUtils.h"
CONTRACT = ROOT / "config/multiplicity_percentile_classes_v2.json"
CLASSES_HEADER = ROOT / "plotting/GeneratedMultiplicityPercentileClasses.h"


def test_contract_is_pr13_tune_local_axis() -> None:
    """The provenance of the axis. The windows themselves are pinned once.

    Ruling R10 allows one source for the class set, so the eleven windows are
    asserted in tests/test_supervisor_decisions.py -- the executable record of
    the owner ruling -- and are not copied here. A second copy would have to be
    edited alongside the contract, which is the defect R10 removes.
    """
    document = json.loads(CONTRACT.read_text())
    assert document["schema"] == "hadronization_multiplicity_percentile_classes_v2"
    assert document["historical_contract"]["github_pr"] == 13
    assert document["classes"], "the contract declares no class"
    for row in document["classes"]:
        assert row["percentile_min"] < row["percentile_max"], row


def test_the_raw_macro_takes_its_classes_from_the_generated_header() -> None:
    """R10: the C++ side reads the contract through one generated header."""
    raw = RAW.read_text()
    assert '#include "GeneratedMultiplicityPercentileClasses.h"' in raw
    assert "HADRONIZATION_MULTIPLICITY_PERCENTILE_CLASSES" in raw

    header = CLASSES_HEADER.read_text()
    rows = json.loads(CONTRACT.read_text())["classes"]
    assert ("HADRONIZATION_MULTIPLICITY_PERCENTILE_CLASS_COUNT %d" % len(rows)
            ) in header
    for row in rows:
        entry = "{%s, %s," % (float(row["percentile_min"]),
                              float(row["percentile_max"]))
        assert entry in header, entry

    # The old second copy is gone: no percentile window is written out in the
    # macro any more.
    for row in rows:
        literal = "{%s, %s," % (float(row["percentile_min"]),
                                float(row["percentile_max"]))
        assert literal not in raw, literal


def test_plotters_derive_thresholds_from_their_tune_histogram() -> None:
    raw = RAW.read_text()
    boundary = BOUNDARY.read_text()
    plotter = PLOTTER.read_text()
    utility = UTILITY.read_text()
    for source in (raw, boundary, plotter):
        assert "MultiplicityBoundaryUtils.h" in source
        assert "CommonMultiplicityBoundaries.h" not in source
    assert "PerTuneBoundaryMarkers(insetHist)" in raw
    assert "ThresholdForPercentile" in raw
    assert "thresholds[percentile]" in boundary
    assert "ThresholdForPercentile" in boundary
    assert "MULTIPLICITY_PER_TUNE_BOUNDARIES" in plotter
    assert "per_tune_summed_multiplicity_quantiles_discrete_v2" in utility
    assert "refusing first/last-bin fallback" in utility


def test_minimum_bias_is_not_a_boundary_input() -> None:
    live_sources = "\n".join(
        path.read_text() for path in (RAW, BOUNDARY, PLOTTER, UTILITY))
    for forbidden in (
        "LoadMinimumBiasNch",
        "kCommonBoundaryArtifactPath",
        "CommonThresholdsForConfiguredClasses",
        "identical_across_tunes",
    ):
        assert forbidden not in live_sources, forbidden


def main() -> int:
    test_contract_is_pr13_tune_local_axis()
    # Ledger DA1-045: this case was defined and never called, so the only
    # assertions in this driver about the generated header -- that the raw
    # macro includes it, that the header carries the contract's class count and
    # every window, and that no percentile literal survives in the macro --
    # never ran. A stale or missing header dependency passed this gate.
    test_the_raw_macro_takes_its_classes_from_the_generated_header()
    test_plotters_derive_thresholds_from_their_tune_histogram()
    test_minimum_bias_is_not_a_boundary_input()
    print("tune-local multiplicity boundary-source tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
