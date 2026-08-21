#!/usr/bin/env python3
"""Render the per-class and integrated delta tables from the report JSON.

Separated from `harvest_class_report.py` so the numbers are computed once and
formatted once, and so a change to a table cannot change a value.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest_class_axis import class_order  # noqa: E402

SERIES = [("BEAUTY", "B^{+}", "B-"), ("BEAUTY", "B^{+}", "Lambda_b"),
          ("CHARM", "D^{+}", "D-"), ("CHARM", "D^{+}", "Lambda_c(+)-bar")]
TUNES = ["MONASH", "JUNCTIONS", "CLOSEPACKING"]
SHORT = {"MONASH": "MON", "JUNCTIONS": "JUN", "CLOSEPACKING": "CLP"}


def cell(row: dict) -> str:
    """Delta +/- SEM, with a flag when it falls short of 2 SEM."""
    text = f"{row['delta']:+.6g} ± {row['delta_sem']:.3g}"
    return f"*{text}*" if row["flagged_below_2sem"] else f"**{text}**"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--out-markdown", type=Path, required=True)
    ap.add_argument("--out-csv", type=Path, required=True)
    args = ap.parse_args()

    data = json.loads(args.report.read_text())
    rows = data["deltas"]
    campaigns = data["campaigns"]
    index = {(r["campaign"], r["flavour"], r["trigger"], r["associate"],
              r["tune"], r["class"]): r for r in rows}

    with args.out_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (
            r["campaign"], r["flavour"], r["trigger"], r["associate"],
            r["tune"], class_order(r["class"]))))

    out = []
    add = out.append

    # --- the integrated arm ------------------------------------------------
    add("## The integrated deltas\n")
    add("Multiplicity-integrated bin `M00_100`, 12 series per campaign, "
        "60 cells. **Bold** is resolved at 2 SEM; *italic* falls short of it.\n")
    for flavour, trigger, associate in SERIES:
        add(f"\n### {flavour} {trigger} — {associate}\n")
        add("| campaign | " + " | ".join(SHORT[t] for t in TUNES) + " |")
        add("|---|" + "---|" * len(TUNES))
        for campaign in campaigns:
            cells = []
            for tune in TUNES:
                row = index[(campaign, flavour, trigger, associate, tune, "MB")]
                cells.append(cell(row))
            add(f"| `{campaign}` | " + " | ".join(cells) + " |")
        add("")
        add("| campaign | " + " | ".join(f"{SHORT[t]} rel. %" for t in TUNES) + " |")
        add("|---|" + "---|" * len(TUNES))
        for campaign in campaigns:
            cells = []
            for tune in TUNES:
                row = index[(campaign, flavour, trigger, associate, tune, "MB")]
                rel = row["relative_shift_percent"]
                cells.append("no scale" if rel is None else f"{rel:+.4g}")
            add(f"| `{campaign}` | " + " | ".join(cells) + " |")

    # --- the per-class arm -------------------------------------------------
    add("\n## The per-class deltas, resolved counts\n")
    add("132 cells per campaign: eleven classes by twelve series. "
        "The count is how many are resolved at 2 SEM.\n")
    add("| campaign | resolved / 132 | " + " | ".join(f"c{i}" for i in range(1, 12)) + " |")
    add("|---|---|" + "---|" * 11)
    for campaign in campaigns:
        per_class = []
        total = 0
        for i in range(1, 12):
            got = [r for r in rows
                   if r["campaign"] == campaign and r["class"] == f"c{i}"]
            n = sum(1 for r in got if not r["flagged_below_2sem"])
            per_class.append(f"{n}/12")
            total += n
        add(f"| `{campaign}` | **{total}/132** | " + " | ".join(per_class) + " |")

    # --- the largest effects ----------------------------------------------
    add("\n## The ten largest per-class effects, by significance\n")
    per_class_rows = [r for r in rows if r["class"] != "MB"]
    top = sorted(per_class_rows, key=lambda r: -r["significance"])[:10]
    add("| campaign | series | tune | class | Δ ± SEM(Δ) | Δ/SEM | rel. % |")
    add("|---|---|---|---|---|---|---|")
    for r in top:
        rel = r["relative_shift_percent"]
        add(f"| `{r['campaign']}` | {r['trigger']}–{r['associate']} | "
            f"{SHORT[r['tune']]} | {r['class']} | "
            f"{r['delta']:+.6g} ± {r['delta_sem']:.3g} | "
            f"{r['significance']:.1f} | "
            f"{'no scale' if rel is None else f'{rel:+.4g}'} |")

    args.out_markdown.write_text("\n".join(out) + "\n")
    print(f"WROTE {args.out_markdown} and {args.out_csv} "
          f"rows={len(rows)} campaigns={len(campaigns)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
