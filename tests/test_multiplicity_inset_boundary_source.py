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


def test_contract_is_pr13_tune_local_axis() -> None:
    document = json.loads(CONTRACT.read_text())
    assert document["schema"] == "hadronization_multiplicity_percentile_classes_v2"
    assert document["historical_contract"]["github_pr"] == 13
    assert [(row["percentile_min"], row["percentile_max"])
            for row in document["classes"]] == [
        (90.0, 100.0), (80.0, 90.0), (70.0, 80.0),
        (60.0, 70.0), (50.0, 60.0), (40.0, 50.0),
        (30.0, 40.0), (20.0, 30.0), (10.0, 20.0),
        (1.0, 10.0), (0.0, 1.0),
    ]


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
    test_plotters_derive_thresholds_from_their_tune_histogram()
    test_minimum_bias_is_not_a_boundary_input()
    print("tune-local multiplicity boundary-source tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
