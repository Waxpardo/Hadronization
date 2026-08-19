#!/usr/bin/env python3
"""Three-tune table on a COMMON row set, both conventions.

WHY THIS EXISTS RATHER THAN THREE RUNS OF decompose_with_block_sems.py. That
tool prints each tune's own top-8 experiment-comparable rows, and the top-8
differs between tunes -- MONASH's carries B+/B-, the CR tunes' carries
Lambda_c+/Lambda_cbar-. A three-tune table needs the same rows in every column
or the columns are not comparable.

The estimator is unchanged and is re-derived here from the same CSVs the tool
reads: fractions are formed INSIDE each block and then averaged, SEM =
stdev(ten)/sqrt(10) with dof = 9, per docs/PER_TUNE_PROCESSING_PREREGISTRATION.md
step 3. The structural numbers this prints are checked against that tool's
output for all three tunes before use.
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "extraction"))
from apply_decay_map import terminal_distribution  # noqa: E402

ART = json.loads((REPO / "AnalysisScripts/species_ordinals_v2.json").read_text())
DMAP = json.loads((REPO / "AnalysisScripts/decay_parent_map_v2.json").read_text())
PDG_ORD = {int(r["pdg"]): int(r["ordinal"]) for r in ART["species"]}
CAT = {int(r["ordinal"]): r["category_name"] for r in ART["species"]}
NAME = {int(s["ordinal"]): s["name"] for s in DMAP["species"]}
BY_ORD = {int(s["ordinal"]): s for s in DMAP["species"]}
DIST = terminal_distribution(BY_ORD, PDG_ORD, split_mode=True)

STRUCT = ["kCentralGround", "kExcludedVector", "kExcludedExcited", "kMultiplyHeavy"]
EXPT = ["D0", "Dbar0", "D+", "D-", "D_s+", "D_s-",
        "Lambda_c+", "Lambda_cbar-", "B+", "B-"]


def load(p: Path) -> dict[int, float]:
    return {int(r["ordinal"]): float(r["total"]) for r in csv.DictReader(p.open())}


def structural(tbl):
    g = defaultdict(float)
    for o, v in tbl.items():
        g[CAT.get(o, "?")] += v
    return g


def experimental(tbl):
    g = defaultdict(float)
    for o, v in tbl.items():
        for t, fr in DIST.get(o, {o: 1.0}).items():
            lab = (NAME[t] if CAT.get(t) == "kCentralGround"
                   else f"UNMAPPED/{CAT.get(t)}")
            g[lab] += v * fr
    return g


def stats(rundirs, fn, keys):
    out = {}
    for tune, rd in rundirs.items():
        bl = [load(rd / f"block_{i}/per_species.csv") for i in range(1, 11)]
        per = []
        for b in bl:
            g = fn(b)
            tot = sum(g.values())
            per.append({k: 100 * v / tot for k, v in g.items()})
        pooled = fn(load(rd / "central/per_species.csv"))
        ptot = sum(pooled.values())
        out[tune] = {k: (statistics.mean([p.get(k, 0.0) for p in per]),
                         statistics.stdev([p.get(k, 0.0) for p in per]) / 10 ** 0.5,
                         100 * pooled.get(k, 0.0) / ptot) for k in keys}
    return out


def emit(title, table, keys, tunes, note=""):
    print(f"\n=== {title} ===")
    if note:
        print(note)
    print(f"| {'row':<16} | " + " | ".join(f"{t:^22}" for t in tunes) + " |")
    print(f"|{'-'*18}|" + "|".join("-" * 24 for _ in tunes) + "|")
    for k in keys:
        cells = []
        for t in tunes:
            m, s, p = table[t][k]
            cells.append(f"{m:>10.4f} ± {s:<7.4f}")
        print(f"| {k:<16} | " + " | ".join(f"{c:<22}" for c in cells) + " |")


def main() -> int:
    rundirs = {t: Path(d) for t, d in (a.split("=", 1) for a in sys.argv[1:])}
    tunes = list(rundirs)
    st = stats(rundirs, structural, STRUCT)
    ex = stats(rundirs, experimental, EXPT)
    emit("DIQUARK-STRUCTURE (primary) — a PARTITION, sums to 100 %", st, STRUCT, tunes)
    for t in tunes:
        print(f"  {t} sum = {sum(st[t][k][0] for k in STRUCT):.4f} %")
    emit("EXPERIMENT-COMPARABLE (decay map v2, split) — a SELECTION, NOT a partition",
         ex, EXPT, tunes,
         note="These rows do NOT sum to 100 % and are not meant to.")
    for t in tunes:
        print(f"  {t} selection sums to {sum(ex[t][k][0] for k in EXPT):.4f} % "
              f"(not 100 % by construction)")
    print("\n--- pooled-vs-block-mean agreement (diff/SEM, both conventions) ---")
    worst = 0.0
    for tab, keys in ((st, STRUCT), (ex, EXPT)):
        for t in tunes:
            for k in keys:
                m, s, p = tab[t][k]
                if s > 0:
                    worst = max(worst, abs(m - p) / s)
    print(f"  worst |block mean - pooled| / SEM over all rows and tunes: {worst:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
