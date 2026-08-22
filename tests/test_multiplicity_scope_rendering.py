#!/usr/bin/env python3
"""Pair-level multiplicity scopes must constrain calculation and rendering."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIGURATION = (
    ROOT / "plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json"
)
PLOTTER = ROOT / "plotting/improvedPlotting_THnSparse.C"


def function_body(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish]


def main() -> int:
    configuration = json.loads(CONFIGURATION.read_text())
    declared_bins = {
        row["binLabel"] for row in configuration["histograms_to_analyse"]
    }
    scoped = []
    for section in (
        "beauty_correlations_to_analyse",
        "charm_correlations_to_analyse",
    ):
        for trigger_group in configuration[section]:
            for pair in trigger_group["configs"]:
                if "multiplicity_scope" in pair:
                    scoped.append(pair)
                    scope = pair["multiplicity_scope"]
                    assert scope, pair
                    assert len(scope) == len(set(scope)), pair
                    assert set(scope) <= declared_bins, pair

    assert scoped, "fixture has no scoped pairs"
    assert {pair["associateOS"] for pair in scoped} == {"Bc-"}
    assert all(
        set(pair["multiplicity_scope"]) == {"M00_100", "M0_1"}
        for pair in scoped
    )

    source = PLOTTER.read_text()
    calculation = function_body(
        source,
        "YieldsAndErrorsMap calculateYieldsVector(",
        "} // calculateYieldsVector()",
    )
    yields = function_body(
        source, "TPad* drawBalancingPlots(", "} // drawBalancingPlots()"
    )
    tune_ratios = function_body(
        source,
        "TPad* drawBalancingPlotsTUNERatios(",
        "} // drawBalancingPlotsTUNERatios()",
    )
    guard = "IsOutsideDeclaredScope("
    assert guard in calculation
    assert guard in yields
    assert guard in tune_ratios
    assert yields.index(guard) < yields.index("SetPlotPointOrThrow(")
    assert tune_ratios.index(guard) < tune_ratios.index("SetPlotPointOrThrow(")
    assert "not drawing this point" in yields
    assert "not drawing this tune ratio" in tune_ratios

    print(
        "multiplicity scope rendering contract passed: "
        f"{len(scoped)} scoped pairs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
