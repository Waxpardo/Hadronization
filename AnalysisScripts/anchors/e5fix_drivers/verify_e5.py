#!/usr/bin/env python3
"""Verify a re-extracted MONASH central against E5's predicted values."""
import csv, json, sys
from collections import defaultdict

run = sys.argv[1] if len(sys.argv) > 1 else "/data/alice/ipardoza/tune_runs_e5fix/MONASH/central"
art_path = "/data/alice/ipardoza/extractor_e5fix/AnalysisScripts/species_ordinals_v2.json"

rows = list(csv.DictReader(open(f"{run}/per_species.csv")))
tot = sum(float(r["total"]) for r in rows)
LO, HI = 53662414, 53662828
verdict = "IN RANGE" if LO <= tot <= HI else "OUT OF RANGE -- STOP AND REPORT"

print("=== E5 VERIFICATION: MONASH central, fixed (deduplicating) extractor ===")
print(f"TOTAL = {tot:,.0f}")
print(f"E5 predicted bracket [{LO:,} .. {HI:,}]  ->  {verdict}")
print(f"  {tot - LO:.0f} counts above the bracket floor (bracket width {HI - LO})")

cat = defaultdict(float)
for r in rows:
    cat[r["category_name"]] += float(r["total"])
pred = {"kCentralGround": 52.4958, "kExcludedVector": 46.4946, "kExcludedExcited": 1.0095}
print()
print(f"{'category':<20}{'counts':>14}{'measured %':>13}{'E5 pred':>10}{'delta pp':>11}")
for k, v in sorted(cat.items(), key=lambda x: -x[1]):
    pct = 100 * v / tot
    p = pred.get(k)
    ptxt = f"{p:.4f}" if p else "-"
    dtxt = f"{pct - p:+.4f}" if p else "-"
    print(f"{k:<20}{v:>14,.0f}{pct:>13.4f}{ptxt:>10}{dtxt:>11}")

art = json.load(open(art_path))
qq = {int(s["ordinal"]): (int(s.get("q_c", 0)), int(s.get("q_b", 0))) for s in art["species"]}
charm = beauty = mixed = 0.0
for r in rows:
    o, v = int(r["ordinal"]), float(r["total"])
    a, b = qq.get(o, (0, 0))
    if a and b:
        mixed += v
    elif a:
        charm += v
    elif b:
        beauty += v
print()
print(f"charm-only  {charm:>14,.0f}   {100*charm/tot:8.4f} %")
print(f"beauty-only {beauty:>14,.0f}   {100*beauty/tot:8.4f} %")
print(f"mixed (bc)  {mixed:>14,.0f}   {100*mixed/tot:8.4f} %")
cb = charm + beauty
print(f"charm:beauty (excl. mixed) = {100*charm/cb:.4f} : {100*beauty/cb:.4f}"
      f"   [E5 predicted 89.9852 : 10.0148]")

EV = 100_000_000
print()
print("=== PER-EVENT PLAUSIBILITY (standing check) ===")
print(f"events in campaign       = {EV:,}")
print(f"re-extracted, per event  = {tot/EV:.4f}")
print(f"OLD replicated, per event= {1298655240/EV:.4f}  <- the ~13/event nobody divided (E5)")
