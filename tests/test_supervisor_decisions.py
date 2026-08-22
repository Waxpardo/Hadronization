#!/usr/bin/env python3
"""Executable contracts for the 2026-08-22 supervisor decisions."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_per_tune_class_contract() -> None:
    contract = json.loads(
        (ROOT / "config/multiplicity_percentile_classes_v2.json").read_text())
    classes = contract["classes"]
    assert [(row["percentile_min"], row["percentile_max"])
            for row in classes] == [
        (90.0, 100.0), (80.0, 90.0), (70.0, 80.0),
        (60.0, 70.0), (50.0, 60.0), (40.0, 50.0),
        (30.0, 40.0), (20.0, 30.0), (10.0, 20.0),
        (1.0, 10.0), (0.0, 1.0),
    ]
    plotter = (ROOT / "plotting/improvedPlotting_THnSparse.C").read_text()
    assert "ThresholdForPercentile(\n                                        centralIdentity" in plotter
    assert "MULTIPLICITY_PER_TUNE_BOUNDARIES" in plotter
    assert "identical_across_tunes" not in plotter
    assert "CommonMultiplicityBoundaries.h" not in plotter


def test_all_current_configs_use_the_contract() -> None:
    expected = json.loads(
        (ROOT / "config/multiplicity_percentile_classes_v2.json").read_text())[
            "classes"]
    expected_windows = [
        (row["bin"], row["percentile_min"], row["percentile_max"])
        for row in expected
    ]
    paths = sorted((ROOT / "plotting").glob("configuration_HF*.json"))
    paths += sorted((ROOT / "plotting").glob("configuration_multiplicity_HF*.json"))
    paths += sorted((ROOT / "plotting/harvest_configs").glob("*.json"))
    for path in set(paths):
        document = json.loads(path.read_text())
        rows = [row for row in document.get("histograms_to_analyse", [])
                if row.get("hDPhi") != "hDPhiM00_100"]
        if not rows:
            continue
        assert [(row["binLabel"], row["multiplicityMin"],
                 row["multiplicityMax"]) for row in rows] == expected_windows, path
        comment = document.get("_comment_axis", "")
        assert "COMMON ABSOLUTE" not in comment, path
        assert "Each tune resolves" in comment, path


def test_cr_holdout_decision_is_exact_and_scoped() -> None:
    policy = json.loads(
        (ROOT / "config/cr_holdout_policy_v1.json").read_text())
    rows = {row["tune"]: row for row in policy["observations"]}
    assert (rows["JUNCTIONS"]["discarded_attempts"],
            rows["JUNCTIONS"]["total_attempts"]) == (63, 1063)
    assert (rows["CLOSEPACKING"]["discarded_attempts"],
            rows["CLOSEPACKING"]["total_attempts"]) == (64, 1064)
    assert policy["decision"] == "accepted_by_supervisors"
    assert "not a universal tolerance" in policy["interpretation"]


def test_tracked_routes_are_account_independent() -> None:
    for path in list((ROOT / "config").glob("*.json")) + list(
            (ROOT / "plotting").glob("configuration_*.json")):
        assert "/data/alice/ipardoza" not in path.read_text(), path


if __name__ == "__main__":
    test_per_tune_class_contract()
    test_all_current_configs_use_the_contract()
    test_cr_holdout_decision_is_exact_and_scoped()
    test_tracked_routes_are_account_independent()
    print("supervisor decision contracts passed")
