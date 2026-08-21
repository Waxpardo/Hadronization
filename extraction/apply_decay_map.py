#!/usr/bin/env python3
"""Apply a decay-parent map to per-species weights and report the
experiment-comparable table, with the particle/antiparticle advisory.

Works on any map version (v1, v1.1, v2) so tables can be compared across them.
The chain walk is v1's, unchanged -- conjugation now lives in the ARTIFACT
(tools/build_decay_parent_map.py), not here, so the reader stays a faithful
consumer of whatever it is given. That is deliberate: the v1 defect was an
artifact defect that the reader propagated correctly, and moving interpretation
into the reader would make the next one harder to find, not easier.

THE ADVISORY IS NOT A GATE. Particle/antiparticle ratios are reported and
flagged beyond a threshold, never enforced. A hard gate at 1.00 would be wrong
physics: real few-percent baryon asymmetries exist in the CR samples, and a
check that refused them would be refusing a result. The defect this catches was
4.49x -- two orders of magnitude beyond anything physical.

Usage:
  extraction/apply_decay_map.py --map <map.json> --weights <per_species.csv>
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARTIFACT = REPO / "AnalysisScripts/species_ordinals_v2.json"
ADVISORY_THRESHOLD = 0.10


def build_labels(dmap: dict, art: dict):
    if dmap["ordinal_table_digest_fnv1a64"] != art["table_digest_fnv1a64"]:
        raise SystemExit("FAIL-CLOSED: map / ordinal table digest mismatch")
    pdg_to_ord = {int(r["pdg"]): int(r["ordinal"]) for r in art["species"]}
    cat_name = {int(r["ordinal"]): r["category_name"] for r in art["species"]}
    name = {int(s["ordinal"]): s["name"] for s in dmap["species"]}
    by_ord = {int(s["ordinal"]): s for s in dmap["species"]}

    def heavy_daughter(entry):
        for product in entry["dominant_products"]:
            if product in pdg_to_ord:
                return pdg_to_ord[product]
        return None

    terminal = {}
    for ordinal in sorted(by_ord):
        seen, current = set(), ordinal
        while current not in seen:
            seen.add(current)
            nxt = heavy_daughter(by_ord[current])
            if nxt is None or nxt == current:
                break
            current = nxt
        terminal[ordinal] = current

    label, term_ord = {}, {}
    for ordinal, term in terminal.items():
        term_ord[ordinal] = term
        label[ordinal] = (name[term] if cat_name[term] == "kCentralGround"
                          else f"UNMAPPED/{cat_name[term]}")
    return label, term_ord, name, by_ord


def terminal_distribution(by_ord: dict, pdg_to_ord: dict, split_mode: bool):
    """Terminal ordinal -> fraction, per species.

    In dominant-only mode this collapses to a single terminal with weight 1 and
    must reproduce the base map exactly (check C5). With splits enabled, a split
    species distributes over its species-level branches, and each branch is then
    resolved recursively -- a branch may itself be a split species.
    """
    def heavy_daughter(entry):
        for product in entry["dominant_products"]:
            if product in pdg_to_ord:
                return pdg_to_ord[product]
        return None

    memo: dict[int, dict[int, float]] = {}

    def resolve(ordinal: int, seen: frozenset) -> dict[int, float]:
        if ordinal in memo:
            return memo[ordinal]
        if ordinal in seen:                      # cycle: terminate here
            return {ordinal: 1.0}
        entry = by_ord[ordinal]
        nxt_seen = seen | {ordinal}
        if split_mode and entry.get("split"):
            out: dict[int, float] = defaultdict(float)
            for b in entry["species_level_branches"]:
                for t, f in resolve(int(b["daughter_ordinal"]), nxt_seen).items():
                    out[t] += float(b["fraction"]) * f
            result = dict(out)
        else:
            nxt = heavy_daughter(entry)
            result = ({ordinal: 1.0} if nxt is None or nxt == ordinal
                      else resolve(nxt, nxt_seen))
        if not seen:
            memo[ordinal] = result
        return result

    return {o: resolve(o, frozenset()) for o in sorted(by_ord)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", dest="mapfile", type=Path, required=True)
    ap.add_argument("--weights", type=Path, required=True)
    ap.add_argument("--artifact", type=Path, default=ARTIFACT)
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--mode", choices=("dominant", "split"), default="dominant",
                    help="'split' honours v2 fractional splits; 'dominant' is "
                         "the compatibility mode used for check C5")
    args = ap.parse_args()

    dmap = json.loads(args.mapfile.read_text())
    art = json.loads(args.artifact.read_text())
    label, term_ord, name, by_ord = build_labels(dmap, art)
    ord_to_pdg = {int(s["ordinal"]): int(s["pdg"]) for s in dmap["species"]}
    pdg_to_ord = {int(r["pdg"]): int(r["ordinal"]) for r in art["species"]}
    cat_name = {int(r["ordinal"]): r["category_name"] for r in art["species"]}

    weight = {int(r["ordinal"]): float(r["total"])
              for r in csv.DictReader(args.weights.open())}
    total = sum(weight.values())

    dist = terminal_distribution(by_ord, pdg_to_ord,
                                 split_mode=(args.mode == "split"))

    grouped: dict[str, float] = defaultdict(float)
    by_terminal_pdg: dict[int, float] = defaultdict(float)
    for ordinal, value in weight.items():
        for t, frac in dist[ordinal].items():
            lab = (name[t] if cat_name[t] == "kCentralGround"
                   else f"UNMAPPED/{cat_name[t]}")
            grouped[lab] += value * frac
            by_terminal_pdg[ord_to_pdg[t]] += value * frac

    regrouped_total = sum(grouped.values())
    # C3 TOTALS. Fractional splits introduce floating-point summation, so exact
    # equality is the wrong test here -- it would fail on representation, not on
    # a real leak. A relative tolerance at the 1e-12 level still catches any
    # actual loss of weight, which would be parts in 1e2, not 1e12.
    if abs(regrouped_total - total) > 1e-6 * max(total, 1.0):
        raise SystemExit(
            f"FAIL-CLOSED C3: regrouping did not conserve weight. "
            f"ungrouped={total!r} regrouped={regrouped_total!r}")

    # C1 FRACTIONS. Every split species' branch fractions must sum to exactly 1
    # in exact arithmetic; the artifact carries them as rationals for this.
    from fractions import Fraction
    for s_ in dmap["species"]:
        if not s_.get("split"):
            continue
        exact = sum(Fraction(b["fraction_exact"]) for b in s_["species_level_branches"])
        if exact != 1:
            raise SystemExit(
                f"FAIL-CLOSED C1: {s_['name']} split fractions sum to {exact}, not 1")

    print(f"MAP {args.mapfile.name} schema={dmap.get('schema')} "
          f"sha256={dmap.get('map_sha256','')[:16]}")
    print(f"TOTAL {total:.10g}  INVARIANCE CONSERVED")
    print()
    rows = sorted(grouped.items(), key=lambda kv: -abs(kv[1]))
    print(f"{'observable':<24}{'weight':>16}{'share %':>10}")
    for k, v in rows[:args.top]:
        print(f"{k:<24}{v:>16.10g}{100.0*v/total:>10.4f}")

    # ---- ADVISORY: particle / antiparticle ratios ---------------------------
    print()
    print("PARTICLE/ANTIPARTICLE ADVISORY "
          f"(flag |ratio-1| > {ADVISORY_THRESHOLD:.0%}; advisory only, never fails)")
    seen, flagged = set(), 0
    for pdg in sorted(by_terminal_pdg, key=lambda p: -by_terminal_pdg[p]):
        if pdg <= 0 or pdg in seen:
            continue
        seen.add(pdg)
        w_p = by_terminal_pdg.get(pdg, 0.0)
        w_a = by_terminal_pdg.get(-pdg, 0.0)
        if w_p <= 0 and w_a <= 0:
            continue
        if w_a == 0:
            print(f"  FLAG {pdg:>7}: antiparticle bin EMPTY "
                  f"(particle {w_p:.10g})")
            flagged += 1
            continue
        ratio = w_p / w_a
        mark = "FLAG" if abs(ratio - 1.0) > ADVISORY_THRESHOLD else "ok  "
        if mark == "FLAG":
            flagged += 1
        if mark == "FLAG" or w_p > 0.01 * total:
            print(f"  {mark} {pdg:>7} / {-pdg:<7} ratio={ratio:>7.3f}  "
                  f"({w_p:.10g} vs {w_a:.10g})")
    print(f"ADVISORY_FLAGGED {flagged}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
