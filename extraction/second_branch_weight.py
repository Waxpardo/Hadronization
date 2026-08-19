#!/usr/bin/env python3
"""The second-branch number: weight put at risk by dominant-only decay mapping.

The experiment-comparable convention chains each species through its DOMINANT
decay channel only, so a 60/40 species is assigned whole to its 60 % descendant.
This quantifies the weight that approximation puts at risk.

It mirrors extraction/extract_species_decomposition.py:load_decay_grouping (the chain
walk at lines 153-176) rather than importing it, because it additionally needs
the per-hop branching ratios the reader discards. Mirroring is only safe if it
is checked, so this FAIL-CLOSES unless it first reproduces the published
experiment-comparable table -- rc=0 is not evidence.

Result and interpretation: docs/SECOND_BRANCH_WEIGHT.md.
NOTE the headline figure is an UPPER BOUND: the map records only dominant
products, so a non-dominant channel that happens to terminate at the same ground
state cannot be distinguished from one that does not. See that document, §4.

Usage:
  extraction/second_branch_weight.py --per-species <per_species.csv>
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DECAY_MAP = REPO / "AnalysisScripts/decay_parent_map_v1_1.json"
ARTIFACT = REPO / "AnalysisScripts/species_ordinals_v2.json"

# The experiment-comparable table. The reimplementation must reproduce these
# before any result is printed.
#
# SUPERSEDED 2026-08-11: these were the v1 values, and v1 mapped antiparticle
# parents to particle daughters (docs/MAP_V1_CONJUGATION_BUG.md). The old
# constants are kept beside the new ones because the failure they produce is
# informative: pointing this tool at v1 now fail-closes loudly rather than
# silently agreeing with a defective table.
PUBLISHED_V1_DEFECTIVE = {"D0": 59678352.0, "D+": 13331304.0, "D-": 13310136.0,
                          "Dbar0": 13298376.0, "D_s+": 8041584.0, "B0": 5042102.0}
PUBLISHED = {"D0": 36539688.0, "D+": 13331304.0, "D-": 13310136.0,
             "Dbar0": 36437040.0, "D_s+": 5491128.0, "B0": 2986568.0}
PUBLISHED_TOTAL = 129883844.0


def build_chains(dmap: dict, art: dict):
    """Walk each species to its terminal heavy descendant.

    Returns terminal ordinal, the product of branching ratios over the hops
    ACTUALLY TAKEN, and the hop count. The BR product is the probability the
    whole chain is the one the species followed; the reader keeps only the
    terminal.
    """
    if dmap["ordinal_table_digest_fnv1a64"] != art["table_digest_fnv1a64"]:
        raise SystemExit(
            "FAIL-CLOSED: decay map was built against ordinal digest "
            f"{dmap['ordinal_table_digest_fnv1a64']}, artifact is "
            f"{art['table_digest_fnv1a64']}"
        )
    pdg_to_ord = {int(r["pdg"]): int(r["ordinal"]) for r in art["species"]}
    by_ord = {int(s["ordinal"]): s for s in dmap["species"]}

    def heavy_daughter(entry):
        for product in entry["dominant_products"]:
            if product in pdg_to_ord:
                return pdg_to_ord[product]
        return None

    terminal, brprod, hops = {}, {}, {}
    for ordinal in sorted(by_ord):
        seen, current, prod, n = set(), ordinal, 1.0, 0
        while current not in seen:
            seen.add(current)
            nxt = heavy_daughter(by_ord[current])
            if nxt is None or nxt == current:
                break
            prod *= float(by_ord[current]["dominant_branching_ratio"])
            n += 1
            current = nxt
        terminal[ordinal], brprod[ordinal], hops[ordinal] = current, prod, n
    return terminal, brprod, hops, by_ord


def species_level_residual(v2: dict, weight: dict[int, float], total: float):
    """The post-split species-level residual -- 'THE NUMBER' of §2.6.

    WHAT IT MEASURES. The experiment-comparable convention assigns a species
    whole to its dominant daughter. Map v2 removes that approximation for the
    species where it costs the most, by SPLITTING them fractionally. What is
    left at risk afterwards is the non-dominant weight of every species that was
    NOT split.

    COMPUTED FROM THE WEIGHTS, not read off the map. `species_level_branches`
    gives each species' branch fractions after species-level aggregation; the
    dominant one is the largest, so the species' exposed fraction is 1 - max(f).
    The map also carries pre-baked `species_level_nondominant_pct_of_total`
    fields, but those were computed against the anchor weights at map-build
    time. Recomputing from whatever weights are supplied is what lets this
    number be quoted on a corrected basis -- which matters here, because B_c+/-
    are the entire residual and B_c is a MIXED beauty-charm species, so its
    share of the total moves under the E5 deduplication (ERROR_RECORD.md E5).

    Returns (presplit_pct, postsplit_pct, contributors) where contributors are
    the non-split species carrying residual, largest first.
    """
    presplit = postsplit = 0.0
    contributors = []
    for entry in v2["species"]:
        branches = entry.get("species_level_branches")
        if not branches:
            continue
        ordinal = int(entry["ordinal"])
        w = weight.get(ordinal, 0.0)
        if w == 0.0:
            continue
        exposed = w * (1.0 - max(float(b["fraction"]) for b in branches))
        presplit += exposed
        if not entry.get("split"):
            postsplit += exposed
            if exposed > 0:
                contributors.append((exposed, entry["name"], ordinal))
    contributors.sort(reverse=True)
    return (100.0 * presplit / total, 100.0 * postsplit / total, contributors)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-species", type=Path, required=True,
                    help="per_species.csv emitted by extract_species_decomposition.py")
    ap.add_argument("--decay-map", type=Path, default=DECAY_MAP)
    ap.add_argument("--artifact", type=Path, default=ARTIFACT)
    ap.add_argument("--v2-map", type=Path, default=None,
                    help="decay_parent_map_v2.json. Supplying it computes the "
                         "SPECIES-LEVEL pre-split and post-split residuals -- "
                         "the latter is the number §2.6 calls THE NUMBER. "
                         "Without it this tool reports only the (A)/(B)/(C) "
                         "dominant-chain rows, which are the HISTORY rows.")
    args = ap.parse_args()

    dmap = json.loads(args.decay_map.read_text())
    art = json.loads(args.artifact.read_text())
    cat_name = {int(r["ordinal"]): r["category_name"] for r in art["species"]}
    name = {int(s["ordinal"]): s["name"] for s in dmap["species"]}

    terminal, brprod, hops, by_ord = build_chains(dmap, art)

    label = {}
    for ordinal, term in terminal.items():
        label[ordinal] = (name[term] if cat_name[term] == "kCentralGround"
                          else f"UNMAPPED/{cat_name[term]}")

    rows = list(csv.DictReader(args.per_species.open()))
    weight = {int(r["ordinal"]): float(r["total"]) for r in rows}
    total = sum(weight.values())

    # ---- POSITIVE CHECK, before any result is reported ---------------------
    regrouped: dict[str, float] = defaultdict(float)
    for ordinal, value in weight.items():
        regrouped[label[ordinal]] += value
    mismatches = [(k, PUBLISHED[k], regrouped.get(k, 0.0))
                  for k in PUBLISHED if abs(regrouped.get(k, 0.0) - PUBLISHED[k]) > 0.5]
    if total == PUBLISHED_TOTAL and mismatches:
        raise SystemExit(
            "FAIL-CLOSED: chain walk does not reproduce the published table on "
            f"the anchor weights. mismatches={mismatches}"
        )
    scope = "ANCHOR (verified against published table)" if total == PUBLISHED_TOTAL \
        else f"OTHER INPUT (total={total:.10g}, published anchor is {PUBLISHED_TOTAL:.10g})"

    # ---- the number --------------------------------------------------------
    reassigned = {o: v for o, v in weight.items() if hops.get(o, 0) > 0}
    w_re = sum(reassigned.values())
    single = sum(v * (1.0 - float(by_ord[o]["dominant_branching_ratio"]))
                 for o, v in reassigned.items())
    chained = sum(v * (1.0 - brprod[o]) for o, v in reassigned.items())
    exposed = sum(v for o, v in reassigned.items()
                  if float(by_ord[o]["dominant_branching_ratio"]) < 0.80)

    print(f"SCOPE {scope}")
    print(f"total weight                        {total:>18.10g}")
    print(f"reassigned (>=1 hop)                {w_re:>18.10g}  {100*w_re/total:8.4f} %")
    print(f"(A) single-hop  sum w*(1-BR_dom)    {single:>18.10g}  {100*single/total:8.4f} %")
    print(f"(C) chained     sum w*(1-prod BR)   {chained:>18.10g}  {100*chained/total:8.4f} %")
    print(f"(B) exposed     w with BR_dom<0.80  {exposed:>18.10g}  {100*exposed/total:8.4f} %")

    print("\nreassigned weight by chain length:")
    by_hops: dict[int, float] = defaultdict(float)
    for o, v in reassigned.items():
        by_hops[hops[o]] += v
    for h in sorted(by_hops):
        print(f"  {h} hop(s) {by_hops[h]:>16.10g}  {100*by_hops[h]/total:8.4f} %")

    print("\ncontributors to (C):")
    print(f"{'species':<16}{'hops':>5}{'prodBR':>9}{'weight':>16}{'at risk':>15}{'% tot':>8}")
    contrib = sorted(((v * (1.0 - brprod[o]), o, v) for o, v in reassigned.items()),
                     key=lambda t: -t[0])
    shown = 0.0
    for risk, o, v in contrib:
        if risk <= 0:
            break
        shown += risk
        print(f"{name[o]:<16}{hops[o]:>5}{brprod[o]:>9.4f}{v:>16.10g}"
              f"{risk:>15.10g}{100*risk/total:>8.4f}")
    print(f"\nSECOND_BRANCH_DONE at_risk_pct={100*chained/total:.4f} "
          f"concentration_top4={100*sum(c for c, _, _ in contrib[:4])/shown:.2f}%")

    # ---- the species-level v2 rows, when the v2 map is supplied ------------
    if args.v2_map is not None:
        v2 = json.loads(args.v2_map.read_text())
        if v2["ordinal_table_digest_fnv1a64"] != art["table_digest_fnv1a64"]:
            raise SystemExit(
                "FAIL-CLOSED: v2 map was built against ordinal digest "
                f"{v2['ordinal_table_digest_fnv1a64']}, artifact is "
                f"{art['table_digest_fnv1a64']}")
        n_split = sum(1 for s_ in v2["species"] if s_.get("split"))
        if n_split != int(v2["split_species_count"]):
            raise SystemExit(
                f"FAIL-CLOSED: v2 map declares split_species_count="
                f"{v2['split_species_count']} but carries {n_split}")
        if n_split == 0:
            raise SystemExit(
                "FAIL-CLOSED: --v2-map carries no split species, so it is not a "
                "v2 map and there is no post-split residual to report")
        pre, post, contributors = species_level_residual(v2, weight, total)
        print()
        print(f"=== SPECIES-LEVEL (map v2, {n_split} split species) ===")
        print(f"pre-split   sum w*(1-f_dominant) over ALL mapped species "
              f"{pre:>10.4f} %")
        print(f"post-split  same, EXCLUDING the split species     "
              f"{post:>10.4f} %   <- THE NUMBER")
        print("residual carried by:")
        for exposed, nm, o in contributors:
            print(f"   {nm:<14} ord {o:>4}  {exposed:>16.4f}  "
                  f"{100*exposed/total:.6f} %")
        print(f"SECOND_BRANCH_V2 presplit_pct={pre:.4f} "
              f"postsplit_residual_pct={post:.4f} "
              f"residual_species={len(contributors)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
