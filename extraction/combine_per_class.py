#!/usr/bin/env python3
"""Per-class combination of the variation sources, and the tune-separation test.

WHAT THIS DOES, AND WHAT IT REFUSES TO DO. It turns the per-class deltas of
`harvest_class_report.py` into one combined systematic per class, per tune, per
series, and compares that against the MONASH-to-JUNCTIONS separation in the same
class. **It refuses to run while any registered source is missing a campaign**,
because pre-registration section 9 closes with the rule that a partial
quadrature sum understates, and an understated systematic is worse than an
absent one.

THE RULES IT APPLIES, none of them chosen here:

    A1 (recorded 2026-08-18) each source contributes max(|D|, SEM(D)) per class,
                             continuously, with no threshold cliff. The 2 SEM
                             flag is presentational and is never a branch.
    A2 (recorded 2026-08-18) S6/A2 is on the M1..M5 partition and is NEVER
                             summed into a c1..c11 total.
    section 9.1              mu_F and PDF act on the same object. If both are
                             non-negligible, quote the larger and drop the other.
    section 9.5              S5 contributed exactly zero, measured -- on the
                             RETIRED absolute axis. Ruling R11 (2026-08-23)
                             holds S5 unresolved on the v2 percentile axis, so
                             it enters no per-class sum and no term is written.
    ruling R9 (2026-08-23)   HF_SYS_PTHAT_1 is excluded. S3 is quoted one-sided
                             as measured, from HF_SYS_PTHAT_4 alone.
    section 2.5              a two-sided source quotes the arm with the larger
                             |D|. Not half the spread, not an envelope.

All of the arithmetic lives in `systematics_delta`, which already carries the
rulings as required policy flags. This module supplies the per-class wiring and
the source-to-campaign map, and nothing else.

UNITS. The combination runs in PER CENT, which is the unit the pre-registration
reports and the unit `systematics_delta`'s negligibility threshold is written
in. The headline comparison needs absolute yields, so the combined per-cent
value is multiplied back by the nominal. The two routes are identical
arithmetic: every source in one cell shares one nominal, so it is a common
positive factor, and max() and quadrature both commute with it.
`tests/test_combine_per_class.py` asserts that agreement rather than asserting
the reasoning.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest_class_axis import class_order  # noqa: E402
from systematics_delta import (UNRESOLVED_MAX_ABS_OR_SEM, Delta,  # noqa: E402
                               combine_quadrature, correlated_pair_choice,
                               larger_arm)

# Source name -> the INCLUDED arms, (up campaign, down campaign). A one-element
# tuple is one-sided. `config/systematics_sources_v1.json` is the declaration
# and carries the excluded arms with their reasons; this map is what the
# arithmetic applies. `tools/systematics_envelope.py` refuses when the two
# disagree, so neither can drift without the envelope saying so.
#
# S3 is one-sided under ruling R9 of 2026-08-23. HF_SYS_PTHAT_1 is excluded: on
# the v2 percentile axis its MONASH p80 and p90 quantiles both resolve to
# N_ch = 2, so the 80-90 per cent class needs the empty range [3,2]. R9 quotes
# S3 one-sided AS MEASURED and does not symmetrise it.
SOURCES: dict[str, tuple[str, ...]] = {
    "S1a_mur": ("HF_SYS_MUR_UP", "HF_SYS_MUR_DOWN"),
    "S1b_muf": ("HF_SYS_MUF_UP", "HF_SYS_MUF_DOWN"),
    "S2_pdf": ("HF_SYS_PDF_CTEQ6L1",),
    "S3_pthat": ("HF_SYS_PTHAT_4",),
}
# Sources that contribute a per-class term without a variation campaign of their
# own. Ruling R11 of 2026-08-23 excludes S5_class_migration -- its structural
# zero was measured on the retired absolute axis and does not carry to the v2
# percentile axis -- so this set is empty and `combine_cell` adds no such term.
# No source name appears here as a constant: ruling R16 put both combination
# routes on the contract below, which is where the names live.
CAMPAIGNLESS_TERMS: tuple[str, ...] = ()

# The declared sources. Ruling R16 of 2026-08-23 makes BOTH combination routes
# read this file: `combine_cell` here and `combined_systematic` in
# `combine_derived`. Before R16 the derived route synthesised an S5 term from a
# constant whatever the contract said.
SOURCES_CONTRACT = (Path(__file__).resolve().parents[1]
                    / "config" / "systematics_sources_v1.json")


def load_source_contract(path: Path | None = None) -> dict:
    """The declared sources, read from the contract."""
    return json.loads((path or SOURCES_CONTRACT).read_text())


def source_arms(row: dict) -> list[dict]:
    """The campaign entries of one source, as objects."""
    return list(row.get("campaigns") or [])


def included_campaignless_sources(sources: dict) -> list[str]:
    """Included sources that declare no campaign at all.

    Such a source was MEASURED without a variation campaign, so it carries a
    term with no variation of its own. S5_class_migration is the only one this
    project has, and R11 currently excludes it, so today this list is empty.
    """
    return [row["source"] for row in sources["sources"]
            if row.get("included", False) and not source_arms(row)]


def source_exclusions(sources: dict) -> tuple[list[dict], list[str]]:
    """(the recorded exclusions, the entries that record no reason).

    An exclusion with no reason is the failure this prevents: a source could
    leave a budget with no record of who removed it or why. So a missing reason
    is a refusal, not a warning. Both combination routes and the envelope
    builder use this one implementation, so the shape cannot drift between
    them.
    """
    recorded: list[dict] = []
    unreasoned: list[str] = []
    for row in sources["sources"]:
        source = row["source"]
        if not row.get("included", False):
            reason = (row.get("exclusion_reason") or "").strip()
            recorded.append(
                {"source": source, "campaign": None, "reason": reason})
            if not reason:
                unreasoned.append(
                    f"source {source} is excluded and records no "
                    "exclusion_reason")
            continue
        for arm in source_arms(row):
            if arm.get("included", False):
                continue
            reason = (arm.get("exclusion_reason") or "").strip()
            recorded.append({"source": source, "campaign": arm["campaign"],
                             "reason": reason})
            if not reason:
                unreasoned.append(
                    f"arm {arm['campaign']} of source {source} is excluded "
                    "and records no exclusion_reason")
    return recorded, unreasoned

TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


class SourcesIncomplete(Exception):
    """A registered source has no campaign. Section 9 forbids a partial sum."""


def required_campaigns() -> set[str]:
    return {c for arms in SOURCES.values() for c in arms}


def missing_campaigns(available: set[str]) -> list[str]:
    return sorted(required_campaigns() - set(available))


def as_percent(row: dict) -> Delta:
    """One delta cell in per cent of its own nominal.

    The nominal is the sealed central and is shared by every source in the cell,
    so this rescaling cannot change which arm is larger or which of |D| and SEM
    binds.
    """
    nominal = row["nominal_yield"]
    if nominal == 0:
        raise ZeroDivisionError(
            f"nominal is zero for {row['campaign']} {row['class']}; a per-cent "
            "delta is undefined and the cell must be named, not filled")
    scale = 100.0 / nominal
    return Delta(row["delta"] * scale, row["delta_sem"] * scale, 10,
                 "absolute_rescaled_to_percent")


def combine_cell(cells: dict[str, dict]) -> dict:
    """One combined systematic for one (series, tune, class).

    `cells` maps campaign name to its delta row for this cell.
    """
    missing = missing_campaigns(set(cells))
    if missing:
        raise SourcesIncomplete(
            "refusing to combine: no campaign for " + ", ".join(missing)
            + ". Pre-registration section 9 -- a partial quadrature sum "
            "understates, and an understated systematic is worse than an "
            "absent one.")

    quoted: dict[str, Delta] = {}
    arms: dict[str, str] = {}
    for source, campaigns in SOURCES.items():
        deltas = {c: as_percent(cells[c]) for c in campaigns}
        if len(campaigns) == 1:
            name = campaigns[0]
        else:
            up, down = campaigns
            chosen, _ = larger_arm(deltas[up], deltas[down])
            name = up if chosen is deltas[up] else down
        quoted[source] = deltas[name]
        arms[source] = name
    # R11 removed the S5 term from this sum. Its per-class contribution was
    # max(|0|, 0) = 0, so no combined value changes; what changes is that the
    # envelope no longer prints a number for an unresolved source.

    drop = correlated_pair_choice(quoted["S1b_muf"], quoted["S2_pdf"])
    total_pct = combine_quadrature(
        quoted,
        unresolved_policy=UNRESOLVED_MAX_ABS_OR_SEM,
        s6_policy="separate",
        drop=drop)

    nominal = next(iter(cells.values()))["nominal_yield"]
    return {
        "combined_percent": total_pct,
        "combined_absolute": total_pct * nominal / 100.0,
        "nominal_yield": nominal,
        "quoted_arm": arms,
        "dropped": sorted(drop),
        "terms_percent": {
            name: {"delta": d.value, "sem": d.sem,
                   "contribution": max(abs(d.value), d.sem)}
            for name, d in sorted(quoted.items())},
    }


def tune_separation(rows_by_tune: dict[str, dict], a: str = "MONASH",
                    b: str = "JUNCTIONS") -> dict:
    """The nominal separation between two tunes in one class, absolute.

    The three tunes are separate generation campaigns with their own raw files
    and their own seeds, so the two means are independent and their SEMs add in
    quadrature. This is the same form as a variation delta and for the same
    reason.
    """
    ya, sa = rows_by_tune[a]["nominal_yield"], rows_by_tune[a]["nominal_sem"]
    yb, sb = rows_by_tune[b]["nominal_yield"], rows_by_tune[b]["nominal_sem"]
    return {
        "tune_a": a, "tune_b": b,
        "yield_a": ya, "yield_b": yb,
        "difference": ya - yb,
        "difference_sem": math.sqrt(sa ** 2 + sb ** 2),
    }


def baryon_meson_ratio(row: dict) -> dict:
    """The Lambda_b / B- balancing-yield ratio from one UNCERTAINTY_MATRIX row.

    The plotter already forms this. A non-reference row carries
    `reference_yield`, the reference associate's yield in the same class and
    tune, and `ratio_sem`, the standard error of the ratio over the ten blocks.
    Taking the plotter's `ratio_sem` rather than propagating the two yield SEMs
    is the point: the numerator and the denominator share their triggers and
    their events, so a quadrature sum of the two would be wrong.
    """
    if row.get("is_reference") == "true":
        raise ValueError("the reference associate has no ratio against itself")
    if row.get("ratio_status") != "PASS":
        raise ValueError(f"ratio_status is {row.get('ratio_status')!r}, not PASS")
    numerator = float(row["central_yield"])
    denominator = float(row["reference_yield"])
    if denominator == 0:
        raise ZeroDivisionError("reference yield is zero; the ratio is undefined")
    return {"ratio": numerator / denominator,
            "ratio_sem": float(row["ratio_sem"])}


def headline_ratio(separation: float, combined_absolute: float) -> float:
    """|tune separation| / combined systematic. Infinite when the systematic is
    zero and the separation is not."""
    if combined_absolute == 0:
        return math.inf if separation != 0 else 0.0
    return abs(separation) / combined_absolute


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", type=Path, required=True,
                    help="per_class_deltas.json from harvest_class_report.py")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    data = json.loads(args.report.read_text())
    available = set(data["campaigns"])
    missing = missing_campaigns(available)
    if missing:
        print("COMBINATION_REFUSED missing=" + ",".join(missing), file=sys.stderr)
        print("Pre-registration section 9: a partial quadrature sum "
              "understates.", file=sys.stderr)
        return 2

    by_cell: dict[tuple, dict[str, dict]] = {}
    for row in data["deltas"]:
        key = (row["flavour"], row["trigger"], row["associate"], row["tune"],
               row["class"])
        by_cell.setdefault(key, {})[row["campaign"]] = row

    nominal_by_series_class: dict[tuple, dict[str, dict]] = {}
    for (flavour, trigger, associate, tune, cls), cells in by_cell.items():
        any_row = next(iter(cells.values()))
        nominal_by_series_class.setdefault(
            (flavour, trigger, associate, cls), {})[tune] = any_row

    out = []
    for key in sorted(by_cell, key=lambda k: (k[:4], class_order(k[4]))):
        flavour, trigger, associate, tune, cls = key
        combined = combine_cell(by_cell[key])
        separation = tune_separation(
            nominal_by_series_class[(flavour, trigger, associate, cls)])
        out.append({
            "flavour": flavour, "trigger": trigger, "associate": associate,
            "tune": tune, "class": cls,
            **combined,
            "tune_separation": separation,
            "separation_over_systematic": headline_ratio(
                separation["difference"], combined["combined_absolute"]),
        })

    args.out.write_text(json.dumps(
        {"schema": "hadronization_per_class_combination_v1",
         "campaigns": sorted(available), "cells": out},
        indent=1, sort_keys=True) + "\n")
    exceed = sum(1 for c in out if c["separation_over_systematic"] > 1.0)
    print(f"COMBINED cells={len(out)} "
          f"separation_exceeds_systematic={exceed}/{len(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
