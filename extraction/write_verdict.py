#!/usr/bin/env python3
"""The verdict: does the tune separation exceed its TOTAL uncertainty?

THE SYSTEMATIC IS COMPUTED ON THE SEPARATION, NOT BORROWED FROM ONE TUNE. A
variation moves MONASH and JUNCTIONS in the same direction, so part of it
cancels in their difference. Taking one tune's per-class systematic and applying
it to the difference would double-count what cancels and overstate the
uncertainty.

So for every source the separation is RECOMPUTED from that source's own render
and differenced against the nominal:

    Delta_source = [A - B](variation) - [A - B](nominal)

Whatever cancels inside the difference has already cancelled before the
combination sees it. The ruled contribution max(|Delta|, SEM) and the quadrature
over sources are `systematics_delta`'s, with its required policy flags.

Three observables: the two balancing yields, and the Lambda_b/B- ratio whose
uncertainty comes from the plotter's own `ratio_sem` because numerator and
denominator share triggers and events.

`c1` is the lowest-activity class and `c11` is the highest: the window label is
a top percentile and runs the other way. Every tune resolves its own N_ch edges,
so no absolute N_ch range applies across tunes.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from combine_derived import (combined_systematic, endpoint_contrast,  # noqa: E402
                             ratio_at, trend_difference, verdict)
from harvest_class_axis import parse_log  # noqa: E402

CLASSES = [f"c{i}" for i in range(1, 12)] + ["MB"]
PAIRS = [("MONASH", "JUNCTIONS"), ("MONASH", "CLOSEPACKING")]
OBSERVABLES = ["B+ - Lambda_b", "B+ - B-", "Lambda_b / B-"]


def quantity(rows: dict, observable: str, tune: str, cls: str) -> tuple[float, float]:
    if observable == "Lambda_b / B-":
        return ratio_at(rows, tune, cls)
    associate = "Lambda_b" if observable == "B+ - Lambda_b" else "B-"
    row = rows[("BEAUTY", "B^{+}", tune, associate, cls)]
    return float(row["central_yield"]), float(row["yield_sem"])


def separation(rows: dict, observable: str, a: str, b: str,
               cls: str) -> tuple[float, float]:
    va, sa = quantity(rows, observable, a, cls)
    vb, sb = quantity(rows, observable, b, cls)
    return va - vb, math.sqrt(sa ** 2 + sb ** 2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--nominal", type=Path, required=True)
    ap.add_argument("--variation", action="append", default=[],
                    metavar="CAMPAIGN=LOG", required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-markdown", type=Path, required=True)
    args = ap.parse_args()

    nominal = parse_log(args.nominal.read_text(errors="replace"))
    variations = {}
    for spec in args.variation:
        campaign, _, path = spec.partition("=")
        variations[campaign] = parse_log(Path(path).read_text(errors="replace"))

    payload = {
        "schema": "hadronization_verdict_v2",
        "derived_delta_sem_method":
            "independent_variation_and_nominal_quadrature_v1",
        "per_class": [],
        "trend": [],
    }
    lines, add = [], None
    out = []
    add = out.append

    # --- the per-class verdict --------------------------------------------
    for a, b in PAIRS:
        add(f"\n## {a} − {b}\n")
        for observable in OBSERVABLES:
            add(f"\n### {observable}\n")
            add("| class | separation | stat | syst | total | |sep|/total | verdict |")
            add("|---|---|---|---|---|---|---|")
            for cls in CLASSES:
                sep, stat = separation(nominal, observable, a, b, cls)
                per_campaign = {c: separation(rows, observable, a, b, cls)
                                for c, rows in variations.items()}
                combined = combined_systematic(sep, stat, per_campaign)
                syst = combined["combined_absolute"]
                v = verdict(sep, stat, syst)
                payload["per_class"].append(
                    {"pair": f"{a}-{b}", "observable": observable, "class": cls,
                     "separation": sep, "stat": stat, "syst": syst,
                     "total": v["total"], "significance": v["significance"],
                     "survives": v["survives"],
                     "terms_percent": combined["terms_percent"],
                     "quoted_arm": combined["quoted_arm"],
                     "dropped": combined["dropped"]})
                add(f"| `{cls}` | {sep:+.6g} | {stat:.3g} | {syst:.3g} "
                    f"| {v['total']:.3g} | {v['significance']:.1f} "
                    f"| {'**EXCEEDS**' if v['survives'] else 'no'} |")

    # --- the trend verdict -------------------------------------------------
    add("\n## The trend: R(c11) − R(c1) of Λ_b/B⁻\n")
    add("| quantity | value | stat | syst | total | |value|/total | verdict |")
    add("|---|---|---|---|---|---|---|")
    for tune in ("MONASH", "JUNCTIONS", "CLOSEPACKING"):
        value, stat = endpoint_contrast(nominal, tune)
        per_campaign = {c: endpoint_contrast(rows, tune)
                        for c, rows in variations.items()}
        combined = combined_systematic(value, stat, per_campaign)
        v = verdict(value, stat, combined["combined_absolute"])
        payload["trend"].append({"quantity": f"contrast {tune}", **v,
                                 "terms_percent": combined["terms_percent"]})
        add(f"| contrast {tune} | {value:+.5f} | {stat:.5f} "
            f"| {combined['combined_absolute']:.5f} | {v['total']:.5f} "
            f"| {v['significance']:.1f} | {'**EXCEEDS**' if v['survives'] else 'no'} |")

    for tune in ("JUNCTIONS", "CLOSEPACKING"):
        value, stat = trend_difference(nominal, tune)
        per_campaign = {c: trend_difference(rows, tune)
                        for c, rows in variations.items()}
        combined = combined_systematic(value, stat, per_campaign)
        v = verdict(value, stat, combined["combined_absolute"])
        payload["trend"].append({"quantity": f"trend {tune} - MONASH", **v,
                                 "terms_percent": combined["terms_percent"],
                                 "quoted_arm": combined["quoted_arm"],
                                 "dropped": combined["dropped"]})
        add(f"| **trend {tune} − MONASH** | {value:+.5f} | {stat:.5f} "
            f"| {combined['combined_absolute']:.5f} | {v['total']:.5f} "
            f"| **{v['significance']:.1f}** "
            f"| {'**EXCEEDS**' if v['survives'] else 'no'} |")

    args.out_json.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    args.out_markdown.write_text("\n".join(out) + "\n")
    survived = sum(1 for r in payload["per_class"] if r["survives"])
    print(f"VERDICT per_class_cells={len(payload['per_class'])} "
          f"exceed_total_uncertainty={survived}")
    for r in payload["trend"]:
        print(f"  {r['quantity']:28s} {r['value']:+.5f} +- stat {r['stat']:.5f} "
              f"+- syst {r['syst']:.5f}  sig={r['significance']:.1f}  "
              f"{'EXCEEDS' if r['survives'] else 'does not exceed'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
