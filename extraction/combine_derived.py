#!/usr/bin/env python3
"""Combined systematics on DERIVED quantities: the ratio, the contrast, the trend.

WHY A DERIVED QUANTITY NEEDS ITS OWN COMBINATION, AND CANNOT BORROW ONE. The
per-class combination in `combine_per_class` works on yields, one class at a
time. The paper's claim is about none of those. It is about the TREND: how much
the Lambda_b/B- ratio rises from the lowest multiplicity class to the highest,
and whether that rise differs between tunes.

Three reasons the per-class systematic cannot simply be propagated into it:

  the ratio      Lambda_b and B- share their triggers and their events, so
                 adding the two yield systematics in quadrature would be wrong.
                 The plotter forms the ratio inside each block and reports its
                 SEM; the ratio is taken from there.
  the contrast   R(c11) - R(c1) is a difference of two classes measured in ONE
                 render. A scale variation moves both ends, largely together.
                 Adding the two per-class systematics would double-count the
                 part that cancels.
  the trend      the difference between two tunes cancels again, because a
                 variation moves MONASH and JUNCTIONS in the same direction.

THE METHOD AVOIDS ALL THREE BY NEVER PROPAGATING. For each source, the derived
quantity is recomputed from THAT SOURCE'S OWN RENDER and differenced against the
nominal:

    Delta_source = Q(variation) - Q(nominal)

Whatever cancels inside Q cancels in that subtraction, because it is one number
computed twice. The ruled contribution max(|Delta|, SEM) and the quadrature over
sources are then exactly as `systematics_delta` defines them, with the same
required policy flags.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from combine_per_class import SOURCES, S5_TERM, missing_campaigns  # noqa: E402
from systematics_delta import (UNRESOLVED_MAX_ABS_OR_SEM, Delta,  # noqa: E402
                               combine_quadrature, correlated_pair_choice,
                               larger_arm)

LOW, HIGH = "c1", "c11"


def ratio_at(rows: dict, tune: str, cls: str) -> tuple[float, float]:
    """The Lambda_b/B- balancing-yield ratio and its SEM, from the plotter."""
    row = rows[("BEAUTY", "B^{+}", tune, "Lambda_b", cls)]
    if row.get("ratio_status") != "PASS":
        raise ValueError(f"ratio_status={row.get('ratio_status')!r} for {tune} {cls}")
    denominator = float(row["reference_yield"])
    if denominator == 0:
        raise ZeroDivisionError(f"reference yield is zero for {tune} {cls}")
    return float(row["central_yield"]) / denominator, float(row["ratio_sem"])


def endpoint_contrast(rows: dict, tune: str) -> tuple[float, float]:
    """R(c11) - R(c1) for one tune, SEMs in quadrature.

    The two classes are disjoint sets of events, so treating them as independent
    is right to the extent the block resampling does not correlate them. A
    positive correlation would make this SEM conservative.
    """
    high, high_sem = ratio_at(rows, tune, HIGH)
    low, low_sem = ratio_at(rows, tune, LOW)
    return high - low, math.sqrt(high_sem ** 2 + low_sem ** 2)


def trend_difference(rows: dict, tune: str, reference: str = "MONASH"
                     ) -> tuple[float, float]:
    """contrast(tune) - contrast(reference). The paper's central quantity."""
    a, a_sem = endpoint_contrast(rows, tune)
    b, b_sem = endpoint_contrast(rows, reference)
    return a - b, math.sqrt(a_sem ** 2 + b_sem ** 2)


def combined_systematic(nominal_value: float, nominal_sem: float,
                        per_campaign: dict) -> dict:
    """Combined systematic on ONE derived scalar, over all seven campaigns.

    `per_campaign` maps campaign -> (value, sem) of the SAME derived quantity,
    recomputed from that campaign's own render. `nominal_sem` is the SEM of the
    nominal derived quantity. The generations are independent, so every
    derived delta uses

        SEM(delta) = sqrt(SEM(variation)^2 + SEM(nominal)^2).

    Everything that cancels inside the quantity has already cancelled before
    this function sees it.

    Runs in per cent of the nominal, which is the unit the pre-registration
    reports and the unit section 9.1's negligibility threshold is written in.
    The nominal is a common positive factor, so max() and quadrature commute
    with the rescaling and the absolute answer is recovered exactly.
    """
    missing = missing_campaigns(set(per_campaign))
    if missing:
        raise ValueError("refusing to combine: no campaign for "
                         + ", ".join(missing))
    if nominal_value == 0:
        raise ZeroDivisionError(
            "the nominal derived quantity is zero; a per-cent contribution is "
            "undefined and the cell must be named, not filled")
    if not math.isfinite(nominal_sem) or nominal_sem < 0:
        raise ValueError("nominal SEM must be finite and non-negative")

    scale = 100.0 / abs(nominal_value)
    quoted: dict[str, Delta] = {}
    arms: dict[str, str] = {}
    variation_sems: dict[str, float] = {}
    for source, campaigns in SOURCES.items():
        deltas = {}
        for campaign in campaigns:
            value, sem = per_campaign[campaign]
            if not math.isfinite(sem) or sem < 0:
                raise ValueError(
                    f"variation SEM for {campaign} must be finite and non-negative")
            deltas[campaign] = Delta((value - nominal_value) * scale,
                                     math.hypot(sem, nominal_sem) * scale,
                                     10, "derived_percent_two_sem")
        if len(campaigns) == 1:
            name = campaigns[0]
        else:
            up, down = campaigns
            chosen, _ = larger_arm(deltas[up], deltas[down])
            name = up if chosen is deltas[up] else down
        quoted[source] = deltas[name]
        arms[source] = name
        variation_sems[source] = per_campaign[name][1] * scale
    # S5's measured class migration is an exact zero shift, not an absent
    # source. Its variation SEM is therefore zero; the nominal derived
    # quantity still has finite sampling uncertainty and the same two-SEM rule
    # gives SEM(delta)=nominal_sem. Omitting this term is one of the four
    # two-sigma classification changes recorded on 2026-08-21.
    quoted[S5_TERM] = Delta(0.0, nominal_sem * scale, 10,
                            "measured_structural_zero_two_sem")
    variation_sems[S5_TERM] = 0.0

    drop = correlated_pair_choice(quoted["S1b_muf"], quoted["S2_pdf"])
    total_pct = combine_quadrature(
        quoted, unresolved_policy=UNRESOLVED_MAX_ABS_OR_SEM,
        s6_policy="separate", drop=drop)
    return {
        "nominal": nominal_value,
        "nominal_sem": nominal_sem,
        "delta_sem_method": "independent_variation_and_nominal_quadrature_v1",
        "combined_percent": total_pct,
        "combined_absolute": total_pct * abs(nominal_value) / 100.0,
        "quoted_arm": arms,
        "dropped": sorted(drop),
        "terms_percent": {
            name: {"delta": d.value, "sem": d.sem,
                   "nominal_sem": nominal_sem * scale,
                   "variation_sem": variation_sems[name],
                   "contribution": max(abs(d.value), d.sem)}
            for name, d in sorted(quoted.items())},
    }


def verdict(value: float, stat_sem: float, syst: float) -> dict:
    """Does the measured quantity exceed its TOTAL uncertainty?"""
    total = math.sqrt(stat_sem ** 2 + syst ** 2)
    return {
        "value": value, "stat": stat_sem, "syst": syst, "total": total,
        "significance": abs(value) / total if total else math.inf,
        "survives": abs(value) > total,
    }
