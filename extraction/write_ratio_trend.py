#!/usr/bin/env python3
"""The multiplicity trend of the Lambda_b/B- ratio, per tune, from the nominal.

THE PAPER'S CENTRAL CLAIM IS A TREND, NOT A SET OF GAPS. Per-class differences
between tunes say the tunes differ somewhere. The claim is that the baryon
fraction RISES with multiplicity under colour reconnection and does not under
MONASH. This module quantifies that rise.

It reads the sealed nominal and nothing else, so it needs no variation campaign
and quotes no systematic.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from combine_per_class import baryon_meson_ratio  # noqa: E402
from harvest_class_axis import class_names, parse_log  # noqa: E402
from ratio_trend import contrast, slope_difference, weighted_linear_fit  # noqa: E402

# Ruling R10: the class set comes from
# config/multiplicity_percentile_classes_v2.json and from nowhere else.
CLASSES = class_names()
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
RECONNECTION = ("JUNCTIONS", "CLOSEPACKING")


def series(rows: dict, tune: str) -> tuple[list[float], list[float]]:
    values, sems = [], []
    for cls in CLASSES:
        ratio = baryon_meson_ratio(rows[("BEAUTY", "B^{+}", tune, "Lambda_b", cls)])
        values.append(ratio["ratio"])
        sems.append(ratio["ratio_sem"])
    return values, sems


def render_tables(payload: dict) -> list[str]:
    """Render the four tables from the JSON payload, and only from it.

    A person pastes these tables by hand into RATIO_TREND.md. Nothing then keeps
    them in step with the product. tests/test_ratio_trend_tables.py closes that
    gap: it calls this function on the committed ratio_trend.json and compares.
    That works only because this renderer reads the payload. The repository does
    not carry the log that the generator parses.
    """
    classes = payload["classes"]
    per_class = payload["per_class"]
    enh = {t: [r["factor"] for r in payload["enhancement_over_MONASH"][t]]
           for t in RECONNECTION}
    out: list[str] = []
    add = out.append
    add("## The Λ_b/B⁻ ratio against multiplicity, per tune\n")
    add("| class | " + " | ".join(TUNES) + " | JUN/MON | CLP/MON |")
    add("|---" * (len(TUNES) + 3) + "|")
    for i, c in enumerate(classes):
        cells = " | ".join(
            f"{per_class[t][i]['ratio']:.6f} ± {per_class[t][i]['ratio_sem']:.6f}"
            for t in TUNES)
        add(f"| `{c}` | {cells} | {enh['JUNCTIONS'][i]:.3f} "
            f"| {enh['CLOSEPACKING'][i]:.3f} |")

    add("\n### The model-free trend: R(c11) − R(c1)\n")
    add("| tune | contrast | stat. σ |")
    add("|---|---|---|")
    for t in TUNES:
        e = payload["endpoint_contrast_c11_minus_c1"][t]
        add(f"| {t} | {e['difference']:+.5f} ± {e['sem']:.5f} "
            f"| {e['significance']:.1f} |")

    add("\n### The weighted straight line in class index\n")
    add("| tune | slope per class | intercept | χ²/ndf |")
    add("|---|---|---|---|")
    for t in TUNES:
        f = payload["weighted_linear_fit_vs_class_index"][t]
        add(f"| {t} | {f['slope']:+.6f} ± {f['slope_sem']:.6f} "
            f"| {f['intercept']:.5f} "
            f"| {f['chi_square']:.1f}/{f['ndf']} = {f['chi_square_per_ndf']:.2f} |")

    add("\n### The trend difference against MONASH\n")
    add("| tune | slope difference | stat. σ | endpoint-contrast difference | stat. σ |")
    add("|---|---|---|---|---|")
    for t in RECONNECTION:
        g = payload["slope_difference_vs_MONASH"][t]
        e = payload["endpoint_contrast_difference_vs_MONASH"][t]
        add(f"| {t} | {g['difference']:+.6f} ± {g['sem']:.6f} "
            f"| {g['significance']:.1f} "
            f"| {e['difference']:+.5f} ± {e['sem']:.5f} | {e['significance']:.1f} |")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--nominal", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-markdown", type=Path, required=True)
    args = ap.parse_args()

    rows = parse_log(args.nominal.read_text(errors="replace"))
    data = {t: series(rows, t) for t in TUNES}
    indices = list(range(1, len(CLASSES) + 1))

    endpoints = {t: contrast(data[t][0][-1], data[t][1][-1],
                             data[t][0][0], data[t][1][0]) for t in TUNES}
    fits = {t: weighted_linear_fit(indices, data[t][0], data[t][1])
            for t in TUNES}
    slope_gaps = {t: slope_difference(fits[t], fits["MONASH"])
                  for t in RECONNECTION}
    endpoint_gaps = {t: contrast(endpoints[t]["difference"], endpoints[t]["sem"],
                                 endpoints["MONASH"]["difference"],
                                 endpoints["MONASH"]["sem"])
                     for t in RECONNECTION}
    enhancement = {t: [(v / m) for v, m in zip(data[t][0], data["MONASH"][0])]
                   for t in RECONNECTION}

    payload = {
        "schema": "hadronization_ratio_trend_v1",
        "observable": "Lambda_b / B- balancing-yield ratio",
        "classes": CLASSES,
        "per_class": {t: [{"class": c, "ratio": v, "ratio_sem": s}
                          for c, v, s in zip(CLASSES, data[t][0], data[t][1])]
                      for t in TUNES},
        "endpoint_contrast_c11_minus_c1": endpoints,
        "weighted_linear_fit_vs_class_index": fits,
        "slope_difference_vs_MONASH": slope_gaps,
        "endpoint_contrast_difference_vs_MONASH": endpoint_gaps,
        "enhancement_over_MONASH": {
            t: [{"class": c, "factor": f} for c, f in zip(CLASSES, enhancement[t])]
            for t in RECONNECTION},
    }
    args.out_json.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")

    out = render_tables(payload)
    args.out_markdown.write_text("\n".join(out) + "\n")
    print(f"RATIO_TREND tunes={len(TUNES)} classes={len(CLASSES)} "
          f"monash_slope={fits['MONASH']['slope']:+.6f} "
          f"junctions_slope={fits['JUNCTIONS']['slope']:+.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
