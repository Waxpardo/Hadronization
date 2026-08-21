#!/usr/bin/env python3
"""Render the per-class combined systematics, and the per-source terms behind them.

Every cell's |Delta| and SEM(Delta) for every source is in the JSON this reads and
in the CSV it writes. The markdown carries the combined value per class per tune
and, beneath it, the source breakdown for the integrated bin, which is where the
budget is easiest to read.

THE 2 SEM FLAG IS PRESENTATIONAL. It marks a cell for the reader and gates
nothing: ruling A1 contributes max(|Delta|, SEM) continuously, with no branch on
resolution anywhere in the arithmetic.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest_class_axis import class_order  # noqa: E402

TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
SHORT = {"MONASH": "MON", "JUNCTIONS": "JUN", "CLOSEPACKING": "CLP"}
SERIES = [("BEAUTY", "B^{+}", "B-"), ("BEAUTY", "B^{+}", "Lambda_b"),
          ("CHARM", "D^{+}", "D-"), ("CHARM", "D^{+}", "Lambda_c(+)-bar")]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--combination", type=Path, required=True)
    ap.add_argument("--out-markdown", type=Path, required=True)
    ap.add_argument("--out-csv", type=Path, required=True)
    args = ap.parse_args()

    cells = json.loads(args.combination.read_text())["cells"]
    index = {(c["flavour"], c["trigger"], c["associate"], c["tune"],
              c["class"]): c for c in cells}

    with args.out_csv.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["flavour", "trigger", "associate", "tune", "class",
                         "nominal_yield", "combined_percent",
                         "combined_absolute", "source", "abs_delta_percent",
                         "sem_percent", "contribution_percent", "quoted_arm",
                         "dropped"])
        for cell in sorted(cells, key=lambda c: (c["flavour"], c["trigger"],
                                                 c["associate"], c["tune"],
                                                 class_order(c["class"]))):
            for source, term in sorted(cell["terms_percent"].items()):
                writer.writerow([
                    cell["flavour"], cell["trigger"], cell["associate"],
                    cell["tune"], cell["class"], f"{cell['nominal_yield']:.17g}",
                    f"{cell['combined_percent']:.17g}",
                    f"{cell['combined_absolute']:.17g}", source,
                    f"{abs(term['delta']):.17g}", f"{term['sem']:.17g}",
                    f"{term['contribution']:.17g}",
                    cell["quoted_arm"].get(source, ""),
                    "yes" if source in cell["dropped"] else "no"])

    out, add = [], None
    out = []
    add = out.append
    add("## The combined systematic, per class per tune\n")
    add("Per cent of the nominal yield in that cell. Every source contributes "
        "`max(|Δ|, SEM(Δ))`, continuously; S5 is a measured zero; A2/S6 is not "
        "in this sum.\n")
    for flavour, trigger, associate in SERIES:
        add(f"\n### {flavour} {trigger} — {associate}\n")
        add("| class | " + " | ".join(SHORT[t] for t in TUNES) + " |")
        add("|---" * (len(TUNES) + 1) + "|")
        for cls in [f"c{i}" for i in range(1, 12)] + ["MB"]:
            cols = []
            for tune in TUNES:
                cell = index[(flavour, trigger, associate, tune, cls)]
                cols.append(f"{cell['combined_percent']:.3g}%")
            add(f"| `{cls}` | " + " | ".join(cols) + " |")

    add("\n## The source breakdown, integrated bin\n")
    add("|Δ| and SEM(Δ) per source, per cent of the nominal. `contribution` is "
        "the ruled `max` of the two; a dropped source is section 9.1's "
        "μ_F-against-PDF choice.\n")
    for flavour, trigger, associate in SERIES:
        for tune in TUNES:
            cell = index[(flavour, trigger, associate, tune, "MB")]
            add(f"\n**{trigger}–{associate}, {tune}** — combined "
                f"**{cell['combined_percent']:.3g}%**"
                + (f", dropped {', '.join(cell['dropped'])}"
                   if cell["dropped"] else ""))
            add("")
            add("| source | \\|Δ\\| | SEM(Δ) | contribution | arm |")
            add("|---|---|---|---|---|")
            for source, term in sorted(cell["terms_percent"].items()):
                add(f"| {source} | {abs(term['delta']):.4g} "
                    f"| {term['sem']:.4g} | {term['contribution']:.4g} "
                    f"| {cell['quoted_arm'].get(source, '—')} |")

    args.out_markdown.write_text("\n".join(out) + "\n")
    print(f"COMBINATION_REPORT cells={len(cells)} rows_csv={len(cells) * 5}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
