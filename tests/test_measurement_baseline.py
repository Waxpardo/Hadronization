#!/usr/bin/env python3
"""Independent arithmetic and topology checks for migration measurements."""

from __future__ import annotations

import csv
import math
import os
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(os.environ.get("RESULTS1_ROOT", Path(__file__).resolve().parents[1]))
MEASUREMENT = ROOT / "results/measurement"


def rows(name: str) -> list[dict[str, str]]:
    with (MEASUREMENT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=2e-13, abs_tol=2e-15)


def finite_cells(table: list[dict[str, str]], numeric: set[str]) -> None:
    for row in table:
        if not row.get("status"):
            raise AssertionError("measurement row lacks explicit status")
        for field in numeric:
            if row.get(field) and not math.isfinite(float(row[field])):
                raise AssertionError(f"nonfinite {field}: {row}")


balancing = rows("balancing.csv")
expected_balancing = ("tune", "flavour", "trigger", "os_associate", "ss_associate", "quantity",
                      "activity_id", "percentile_low", "percentile_high", "nch_low", "nch_high",
                      "estimator", "n_os", "n_ss", "n_trigger", "value", "status")
assert tuple(balancing[0]) == expected_balancing
finite_cells(balancing, {"percentile_low", "percentile_high", "nch_low", "nch_high", "n_os", "n_ss",
                         "n_trigger", "value"})
balance_ids = [(r["tune"], r["flavour"], r["trigger"], r["os_associate"], r["ss_associate"],
                r["quantity"], r["activity_id"], r["estimator"]) for r in balancing]
if len(balance_ids) != len(set(balance_ids)):
    raise AssertionError("balancing scientific identity is not unique")

base_fields = ("tune", "flavour", "trigger", "os_associate", "activity_id")
grouped: dict[tuple[str, ...], dict[tuple[str, str], dict[str, str]]] = defaultdict(dict)
for row in balancing:
    base = tuple(row[field] for field in base_fields)
    grouped[base][(row["quantity"], row["estimator"])] = row

for base, group in grouped.items():
    central = group[("balancing_yield", "central")]
    if central["status"] == "available_count_backed":
        expected = (int(central["n_os"]) - int(central["n_ss"])) / int(central["n_trigger"])
        if not close(float(central["value"]), expected):
            raise AssertionError(f"central balancing arithmetic failed: {base}")
    if ("balancing_yield_sem", "central") in group:
        blocks = [float(group[("balancing_yield", f"block_{index:02d}")]["value"])
                  for index in range(1, 11)]
        expected_sem = statistics.stdev(blocks) / math.sqrt(10.0)
        if not close(float(group[("balancing_yield_sem", "central")]["value"]), expected_sem):
            raise AssertionError(f"ten-block yield SEM failed: {base}")
    elif set(group) != {("balancing_yield", "central")}:
        raise AssertionError(f"count-only identity carries incomplete estimator rows: {base}")
    if ("balancing_ratio_to_reference", "central") in group:
        ratios = [float(group[("balancing_ratio_to_reference", f"block_{index:02d}")]["value"])
                  for index in range(1, 11)]
        expected_ratio_sem = statistics.stdev(ratios) / math.sqrt(10.0)
        if not close(float(group[("balancing_ratio_sem", "central")]["value"]), expected_ratio_sem):
            raise AssertionError(f"ten-block ratio SEM failed: {base}")
        prefix = (base[0], base[1], base[2], base[4])
        references = [candidate for candidate, candidate_group in grouped.items()
                      if (candidate[0], candidate[1], candidate[2], candidate[4]) == prefix
                      and ("balancing_yield_sem", "central") in candidate_group
                      and ("balancing_ratio_to_reference", "central") not in candidate_group]
        if len(references) != 1:
            raise AssertionError(f"ratio reference is not unique: {base}")
        reference_group = grouped[references[0]]
        for index, ratio in enumerate(ratios, 1):
            numerator = float(group[("balancing_yield", f"block_{index:02d}")]["value"])
            denominator = float(reference_group[("balancing_yield", f"block_{index:02d}")]["value"])
            if not close(ratio, numerator / denominator):
                raise AssertionError(f"ratio-inside-block arithmetic failed: {base}/block_{index:02d}")

closure_groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
for group in grouped.values():
    central = group[("balancing_yield", "central")]
    if central["status"] == "available_count_backed":
        closure_groups[(central["tune"], central["flavour"], central["trigger"], central["os_associate"])].append(central)
for identity, group in closure_groups.items():
    integrated = [row for row in group if row["activity_id"] == "integrated_0_100"]
    classes = [row for row in group if row["activity_id"] != "integrated_0_100"]
    if len(integrated) != 1 or len(classes) != 11:
        raise AssertionError(f"activity topology failed: {identity}")
    total_trigger = sum(int(row["n_trigger"]) for row in classes)
    total_os = sum(int(row["n_os"]) for row in classes)
    total_ss = sum(int(row["n_ss"]) for row in classes)
    central = integrated[0]
    if (total_trigger, total_os, total_ss) != (int(central["n_trigger"]), int(central["n_os"]), int(central["n_ss"])):
        raise AssertionError(f"activity-class count closure failed: {identity}")
    weighted = sum(float(row["value"]) * int(row["n_trigger"]) for row in classes) / total_trigger
    if not close(weighted, float(central["value"])):
        raise AssertionError(f"weighted class-yield closure failed: {identity}")

correlations = rows("correlations.csv")
assert tuple(correlations[0]) == ("tune", "flavour", "trigger", "associate", "context", "activity_id",
                                  "bin_index", "dphi_low", "dphi_high", "value", "stat_error", "status")
if len(correlations) != 1200:
    raise AssertionError(f"correlation row count: {len(correlations)} != 1200")
finite_cells(correlations, {"bin_index", "dphi_low", "dphi_high", "value", "stat_error"})
correlation_ids = [(r["tune"], r["flavour"], r["trigger"], r["associate"], r["context"],
                    r["activity_id"], r["bin_index"]) for r in correlations]
if len(correlation_ids) != len(set(correlation_ids)):
    raise AssertionError("correlation identity is not unique")
correlation_groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
for row in correlations:
    correlation_groups[tuple(row[key] for key in ("tune", "flavour", "trigger", "associate", "context", "activity_id"))].append(row)
if len(correlation_groups) != 12:
    raise AssertionError("correlation context count differs from 12")
for identity, group in correlation_groups.items():
    group.sort(key=lambda row: int(row["bin_index"]))
    if [int(row["bin_index"]) for row in group] != list(range(1, 101)):
        raise AssertionError(f"correlation bin indexes are incomplete: {identity}")
    for left, right in zip(group, group[1:]):
        if not close(float(left["dphi_high"]), float(right["dphi_low"])):
            raise AssertionError(f"correlation axis does not close: {identity}")


def check_axis_table(name: str, group_fields: tuple[str, ...], index_field: str,
                     low_field: str, high_field: str, expected_groups: int) -> None:
    table = rows(name)
    finite_cells(table, {index_field, low_field, high_field, "normalized_value", "normalized_error"})
    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in table:
        groups[tuple(row[field] for field in group_fields)].append(row)
    if len(groups) != expected_groups:
        raise AssertionError(f"{name} group count: {len(groups)} != {expected_groups}")
    for identity, group in groups.items():
        group.sort(key=lambda row: int(row[index_field]))
        if [int(row[index_field]) for row in group] != list(range(1, len(group) + 1)):
            raise AssertionError(f"{name} bin indexes are not consecutive: {identity}")
        for row in group:
            if not float(row[low_field]) < float(row[high_field]):
                raise AssertionError(f"{name} bin is not strictly ordered: {identity}")
        for left, right in zip(group, group[1:]):
            if not close(float(left[high_field]), float(right[low_field])):
                raise AssertionError(f"{name} bins overlap or leave a gap: {identity}")


check_axis_table("multiplicity.csv", ("tune",), "bin_index", "nch_low", "nch_high", 3)
check_axis_table("kinematics.csv", ("tune", "species", "pdg", "observable"),
                 "bin_index", "bin_low", "bin_high", 90)

sample_counts = rows("sample_counts.csv")
if len(sample_counts) != 36:
    raise AssertionError("sample-count CSV does not contain 12 quantities per tune")
sample_ids = {(row["tune"], row["quantity"]) for row in sample_counts}
if len(sample_ids) != 36:
    raise AssertionError("sample-count identity is not unique")
finite_cells(sample_counts, {"pdg", "value"})
tex = (ROOT / "results/tables/sample_counts.tex").read_text(encoding="utf-8")
for quantity in {row["quantity"] for row in sample_counts}:
    selected = {row["tune"]: row for row in sample_counts if row["quantity"] == quantity}
    expected = " & ".join(selected[tune]["value"] for tune in ("MONASH", "JUNCTIONS", "CLOSEPACKING"))
    if expected not in tex:
        raise AssertionError(f"sample table does not exactly reproduce canonical CSV: {quantity}")

print("PASS test_measurement_baseline.py")
