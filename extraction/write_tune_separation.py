#!/usr/bin/env python3
"""The MONASH-to-JUNCTIONS separation per class, from the sealed nominal alone.

THIS IS HALF OF THE HEADLINE COMPARISON, AND IT IS THE HALF THAT NEEDS NO
VARIATION. The separation between two tunes is a property of the nominal
campaign: three tunes, three sets of raw files, three sets of seeds. The other
half, the combined systematic, needs every included variation arm and
`combine_per_class.py` refuses without them.

THE THREE TUNES ARE INDEPENDENT SAMPLES, so the SEM of a difference is the two
SEMs in quadrature. They are separate generation campaigns with their own raw
files under `hf_<TUNE>_job*.root` and their own seeds, not three analyses of one
sample.

THE RATIO IS TAKEN FROM THE PLOTTER, NOT PROPAGATED. Lambda_b and B- share their
triggers and their events, so a quadrature sum of the two yield SEMs would be
wrong. The plotter forms the ratio inside each block and reports `ratio_sem`
over the ten.

THE CLASS AXIS RUNS OPPOSITE TO ITS LABEL: `c1` is the lowest-activity class
and the last class is the highest. Every tune resolves its own N_ch edges, and
the class set is read from the contract. See `harvest_class_axis`.

JUNCTIONS and CLOSEPACKING are full configuration bundles and MONASH is the
reference bundle. This comparison does not attribute a difference to one
switch, and CLOSEPACKING is not a junction-off control.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from combine_per_class import baryon_meson_ratio  # noqa: E402
from harvest_class_axis import (INTEGRATED, class_names,  # noqa: E402
                                class_order, parse_log)

# Ruling R10: the class set comes from
# config/multiplicity_percentile_classes_v2.json and from nowhere else.
CLASSES = class_names() + [INTEGRATED]
OBSERVABLES = [
    ("B+ - B- balancing yield", "B-", "yield"),
    ("B+ - Lambda_b balancing yield", "Lambda_b", "yield"),
    ("Lambda_b / B- balancing-yield ratio", "Lambda_b", "ratio"),
]


def value_of(row: dict, kind: str) -> tuple[float, float]:
    if kind == "yield":
        return float(row["central_yield"]), float(row["yield_sem"])
    ratio = baryon_meson_ratio(row)
    return ratio["ratio"], ratio["ratio_sem"]


def separation(rows: dict, associate: str, cls: str, kind: str,
               a: str = "MONASH", b: str = "JUNCTIONS") -> dict:
    va, sa = value_of(rows[("BEAUTY", "B^{+}", a, associate, cls)], kind)
    vb, sb = value_of(rows[("BEAUTY", "B^{+}", b, associate, cls)], kind)
    difference = va - vb
    sem = math.sqrt(sa ** 2 + sb ** 2)
    return {
        "class": cls, "tune_a": a, "tune_b": b,
        "value_a": va, "sem_a": sa, "value_b": vb, "sem_b": sb,
        "difference": difference, "difference_sem": sem,
        "statistical_significance": abs(difference) / sem if sem else math.inf,
        # The size a combined systematic would have to reach, as a per cent of
        # the MONASH value, to erase this separation. It is a property of the
        # nominal alone and quotes no systematic.
        "percent_of_monash_to_erase":
            abs(difference) / abs(va) * 100.0 if va else math.inf,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--nominal", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-markdown", type=Path, required=True)
    args = ap.parse_args()

    rows = parse_log(args.nominal.read_text(errors="replace"))
    payload = {"schema": "hadronization_tune_separation_v2", "observables": {}}
    lines = []
    add = lines.append
    add("## The configuration bundles against MONASH, the sealed nominal\n")
    add("**Statistical uncertainty only.** The combined systematic is not in "
        "these tables, so no column here is a verdict on whether the tunes "
        "separate. `c1` is N_ch 0 to 2 and `c11` is N_ch 33 and above.\n")

    for other in ("JUNCTIONS", "CLOSEPACKING"):
      for label, associate, kind in OBSERVABLES:
        entries = [separation(rows, associate, cls, kind, b=other)
                   for cls in CLASSES]
        payload["observables"][f"MONASH - {other}: {label}"] = entries
        add(f"\n### MONASH − {other} — {label}\n")
        add(f"| class | MONASH | {other} | difference | stat. σ | "
            "% of MONASH to erase |")
        add("|---|---|---|---|---|---|")
        for e in sorted(entries, key=lambda x: class_order(x["class"])):
            add(f"| `{e['class']}` | {e['value_a']:.6g} ± {e['sem_a']:.3g} "
                f"| {e['value_b']:.6g} ± {e['sem_b']:.3g} "
                f"| {e['difference']:+.6g} ± {e['difference_sem']:.3g} "
                f"| {e['statistical_significance']:.1f} "
                f"| {e['percent_of_monash_to_erase']:.1f} |")

    args.out_json.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    args.out_markdown.write_text("\n".join(lines) + "\n")
    worst = min(e["statistical_significance"]
                for v in payload["observables"].values() for e in v)
    best = max(e["statistical_significance"]
               for v in payload["observables"].values() for e in v)
    print(f"TUNE_SEPARATION observables={len(OBSERVABLES)} "
          f"classes={len(CLASSES)} stat_sigma_range={worst:.1f}..{best:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
