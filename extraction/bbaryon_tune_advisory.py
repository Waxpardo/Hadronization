#!/usr/bin/env python3
"""Per-tune b-baryon particle/antiparticle advisory — step 2 of the advisory
ladder, which is blocked on the merged three-tune output.

RAW WEIGHTS, NO MAP. Step 1 of that ladder computed its ratios "directly from
per_species.csv, with no map applied at all", and exonerated the map. Step 2 is
the same measurement across tunes, so it uses the same basis; applying the map
here would re-introduce the chaining (Sigma_b -> Lambda_b) that step 1 was
designed to look underneath.

THE PRE-REGISTRATION IS LOOSE AND IS NOT A GATE. Junction baryon-number
transport predicts the CR tunes carry at least MONASH's asymmetry. That is a
direction, not a threshold, and this prints it as an advisory exactly as
apply_decay_map.py's advisory does -- it never fails.

Ratios are formed INSIDE each block and then averaged, per the registered
per-tune processing, step 3: a ratio of summed
numerators to summed denominators is a different estimator with a smaller,
wrong variance.
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = json.loads((REPO / "contracts/species_ordinals_v2.json").read_text())
DMAP = json.loads((REPO / "contracts/decay_parent_map_v2.json").read_text())

NAME = {int(s["ordinal"]): s["name"] for s in DMAP["species"]}
ORD_PDG = {int(r["ordinal"]): int(r["pdg"]) for r in ART["species"]}
PDG_ORD = {int(r["pdg"]): int(r["ordinal"]) for r in ART["species"]}
IS_BBARYON = {int(r["ordinal"]): (r["is_baryon"] == 1 and r["n_beauty"] >= 1)
              for r in ART["species"]}


def load(p: Path) -> dict[int, float]:
    return {int(r["ordinal"]): float(r["total"]) for r in csv.DictReader(p.open())}


def ratios(weights: dict[int, float]) -> dict[int, float | None]:
    """particle/antiparticle ratio keyed by the POSITIVE pdg."""
    out: dict[int, float | None] = {}
    for o, pdg in ORD_PDG.items():
        if pdg <= 0 or not IS_BBARYON.get(o):
            continue
        anti_ord = PDG_ORD.get(-pdg)
        w_p = weights.get(o, 0.0)
        w_a = weights.get(anti_ord, 0.0) if anti_ord is not None else 0.0
        out[pdg] = (w_p / w_a) if w_a > 0 else None
    return out


def main() -> int:
    rundirs = {t: Path(d) for t, d in (a.split("=", 1) for a in sys.argv[1:])}
    per_tune = {}
    for tune, rd in rundirs.items():
        central = load(rd / "central/per_species.csv")
        blocks = [load(rd / f"block_{i}/per_species.csv") for i in range(1, 11)]
        per_tune[tune] = (central, blocks, ratios(central),
                          [ratios(b) for b in blocks])

    tunes = list(per_tune)
    # Order by MONASH central weight so the table leads with what carries weight.
    ref_central = per_tune.get("MONASH", per_tune[tunes[0]])[0]

    def wt(pdg):
        o = PDG_ORD.get(pdg)
        return ref_central.get(o, 0.0) if o is not None else 0.0

    pdgs = sorted({p for _, _, r, _ in per_tune.values() for p in r}, key=lambda p: -wt(p))

    print("PER-TUNE b-BARYON PARTICLE/ANTIPARTICLE ADVISORY — raw weights, no map")
    print("ratio = w(particle)/w(antiparticle); block mean +/- SEM over ten blocks, dof=9")
    print()
    hdr = f"{'species':<14}{'pdg':>7}"
    for t in tunes:
        hdr += f"{t:>28}"
    print(hdr)
    sub = f"{'':<14}{'':>7}" + "".join(f"{'ratio':>10}{'SEM':>8}{'n(particle)':>10}" for _ in tunes)
    print(sub)
    for pdg in pdgs:
        o = PDG_ORD[pdg]
        if wt(pdg) < 1000:          # keep the table to species with real weight
            continue
        line = f"{NAME.get(o, '?'):<14}{pdg:>7}"
        for t in tunes:
            central, blocks, rc, rb = per_tune[t]
            vals = [rb[i].get(pdg) for i in range(len(rb))]
            vals = [v for v in vals if v is not None]
            if len(vals) < 2:
                line += f"{'n/a':>10}{'':>8}{'':>10}"
                continue
            m = statistics.mean(vals)
            sem = statistics.stdev(vals) / (len(vals) ** 0.5)
            line += f"{m:>10.4f}{sem:>8.4f}{central.get(o, 0):>10,.0f}"
        print(line)

    # ---- the loose pre-registration, stated as a direction ------------------
    print()
    print("PRE-REGISTRATION (loose, advisory only): CR tunes >= MONASH")
    if "MONASH" in per_tune:
        for t in tunes:
            if t == "MONASH":
                continue
            ge = lt = 0
            for pdg in pdgs:
                if wt(pdg) < 1000:
                    continue
                mv = [r.get(pdg) for r in per_tune["MONASH"][3]]
                tv = [r.get(pdg) for r in per_tune[t][3]]
                mv = [v for v in mv if v is not None]
                tv = [v for v in tv if v is not None]
                if len(mv) < 2 or len(tv) < 2:
                    continue
                if statistics.mean(tv) >= statistics.mean(mv):
                    ge += 1
                else:
                    lt += 1
            print(f"  {t:<14} >= MONASH in {ge} of {ge + lt} weighted b-baryon species")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
