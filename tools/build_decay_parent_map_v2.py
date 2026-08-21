#!/usr/bin/env python3
"""Build decay_parent_map_v2.json -- species-level, with fractional splits.

WHY v2 EXISTS. v1 chains each species through its DOMINANT CHANNEL only, so a
species is assigned WHOLE to one descendant. That put 12.84 % of total weight at
risk (docs/SECOND_BRANCH_WEIGHT.md). The owner ruled: build v2 with fractional
splits, do not switch conventions.

THE KEY CORRECTION IS SPECIES-LEVEL AGGREGATION, NOT THE SPLIT ITSELF. The
12.84 % is CHANNEL-level, but the convention assigns to a SPECIES, so two
channels landing on the same ground state were never a misassignment. D*0 ->
D0 pi0 and D0 gamma are both D0. Most of the 12.84 % evaporates on that
observation alone, before a single split is made.

SCOPE, AND WHY IT IS BOUNDED. Species-level aggregation is applied ONLY to
species v1 already reassigns (>= 1 hop). It is deliberately NOT applied to
terminals: B0 carries 890 channels whose branching ratios sum to 1.32 and whose
dominant channel is quark-level, which is exactly why v1 terminates it at
itself and treats it as an observable. Aggregating its channels would move
beauty weight into charm bins -- a convention change, which is not what was
ruled. The terminal set is therefore identical to v1's by construction.

BR SOURCE: PYTHIA 8.317 particleData, the pinned install, via the extended
probe (all channels). Same source as v1, so v2 is comparable to v1 by
construction. This is NOT the PDG; see docs/MAP_V2_PREREGISTRATION.md §4, an
open provenance question for the owner.

Usage:
  tools/build_decay_parent_map_v2.py PROBE_OUT --ordinals ... --v1 ... --out ...
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

# Conjugation lives in one place. PYTHIA reports one decay table per particle,
# so EVERY channel of an antiparticle parent needs conjugating, not just the
# dominant one -- v1.1 fixed the dominant channel, and v2 reads all of them.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_decay_parent_map import conjugate_products, heavy_flavour_sign  # noqa: E402

# Split a species when its non-dominant weight exceeds this total-weight fraction.
DEFAULT_THRESHOLD_PCT = 0.1


def parse_channels(text: str) -> dict[int, list[tuple[Fraction, list[int]]]]:
    out: dict[int, list[tuple[Fraction, list[int]]]] = defaultdict(list)
    for line in text.splitlines():
        if not line.startswith("F4_CHANNEL"):
            continue
        kv = dict(t.split("=", 1) for t in line.split()[1:] if "=" in t)
        prods = [int(x) for x in kv["products"].split(":")] if kv["products"] != "-" else []
        out[int(kv["pdg"])].append((Fraction(kv["br"]), prods))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("probe_out", type=Path)
    ap.add_argument("--ordinals", type=Path, required=True)
    ap.add_argument("--v1", type=Path, required=True,
                    help="the BASE map: must be v1.1 or later. v1 is defective "
                         "(docs/MAP_V1_CONJUGATION_BUG.md)")
    ap.add_argument("--weights", type=Path, required=True,
                    help="per_species.csv, for the threshold decision")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--threshold-pct", type=float, default=DEFAULT_THRESHOLD_PCT)
    args = ap.parse_args()

    art = json.loads(args.ordinals.read_text())
    v1 = json.loads(args.v1.read_text())
    chans = parse_channels(args.probe_out.read_text())

    pdg2ord = {int(r["pdg"]): int(r["ordinal"]) for r in art["species"]}
    ord2pdg = {v: k for k, v in pdg2ord.items()}
    name = {int(s["ordinal"]): s["name"] for s in v1["species"]}
    by_ord = {int(s["ordinal"]): s for s in v1["species"]}

    if v1["ordinal_table_digest_fnv1a64"] != art["table_digest_fnv1a64"]:
        raise SystemExit("FAIL-CLOSED: v1 map / ordinal table digest mismatch")

    # The base map must already carry the conjugation fix. Building v2 on the
    # defective v1 would silently inherit a 17.8 pp error in D0.
    if v1.get("schema") == "hf_decay_parent_map_v1":
        raise SystemExit(
            "FAIL-CLOSED: base map is v1, which does not conjugate antiparticle "
            "decays (docs/MAP_V1_CONJUGATION_BUG.md). Build on v1.1 or later.")

    def daughter_of(prods):
        for p in prods:
            if p in pdg2ord:
                return pdg2ord[p]
        return None

    # ---- v1's walk, to identify which species are REASSIGNED ----------------
    def v1_daughter(o):
        return daughter_of(by_ord[o]["dominant_products"])

    nhops = {}
    for o in sorted(by_ord):
        seen, cur, n = set(), o, 0
        while cur not in seen:
            seen.add(cur)
            nxt = v1_daughter(cur)
            if nxt is None or nxt == cur:
                break
            n += 1
            cur = nxt
        nhops[o] = n

    # ---- weights, for the threshold ----------------------------------------
    import csv
    weight = {int(r["ordinal"]): float(r["total"])
              for r in csv.DictReader(args.weights.open())}
    total_weight = sum(weight.values())

    # ---- species-level branches for the reassigned set ----------------------
    species_out, split_count, notes = [], 0, []
    for o in sorted(by_ord):
        pdg = ord2pdg[o]
        entry = by_ord[o]
        rec = {
            "ordinal": o, "pdg": pdg, "name": entry["name"],
            "channels": entry["channels"],
            "dominant_branching_ratio": entry["dominant_branching_ratio"],
            "dominant_products": entry["dominant_products"],
            "status": entry["status"],
            "reassigned_by_v1": nhops[o] > 0,
            "split": False,
        }
        if nhops[o] > 0 and pdg in chans:
            agg: dict[int, Fraction] = defaultdict(Fraction)
            br_total = Fraction(0)
            no_daughter = Fraction(0)
            for br, prods_raw in chans[pdg]:
                br_total += br
                # EVERY channel of an antiparticle parent is conjugated, for
                # the same reason the dominant one was in v1.1.
                prods = conjugate_products(prods_raw) if pdg < 0 else prods_raw
                d = daughter_of(prods)
                if d is None:
                    no_daughter += br
                else:
                    agg[d] += br
            # Renormalise over channels that HAVE an in-table daughter. For 58
            # of the 60 reassigned species this is a no-op (br_total == 1 and
            # no_daughter == 0); it exists for B_c+-, whose table sums to 1.021
            # with 23 daughterless channels. Those sit far below threshold and
            # stay dominant-only, so the renormalisation never reaches a
            # published number -- but it is recorded rather than hidden.
            denom = sum(agg.values())
            if denom > 0:
                branches = sorted(
                    ((d, f / denom) for d, f in agg.items()),
                    key=lambda t: (-t[1], t[0]))
                rec["species_level_branches"] = [
                    {"daughter_ordinal": d,
                     "daughter_pdg": ord2pdg[d],
                     "daughter_name": name[d],
                     "fraction": float(f),
                     "fraction_exact": f"{f.numerator}/{f.denominator}"}
                    for d, f in branches
                ]
                rec["br_sum_raw"] = float(br_total)
                rec["br_weight_without_in_table_daughter"] = float(no_daughter)
                dominant_fraction = branches[0][1]
                nondom_weight = weight.get(o, 0.0) * float(1 - dominant_fraction)
                rec["species_level_nondominant_weight"] = nondom_weight
                rec["species_level_nondominant_pct_of_total"] = (
                    100.0 * nondom_weight / total_weight)
                if rec["species_level_nondominant_pct_of_total"] > args.threshold_pct:
                    rec["split"] = True
                    split_count += 1
                    # C2: a split may not cross heavy flavour or flip its sign.
                    ph, ps = heavy_flavour_sign(pdg)
                    for b in rec["species_level_branches"]:
                        dh, ds = heavy_flavour_sign(b["daughter_pdg"])
                        if (dh, ds) != (ph, ps):
                            raise SystemExit(
                                f"FAIL-CLOSED C2: split of {entry['name']} "
                                f"({pdg}, flavour={ph} sign={ps}) sends weight to "
                                f"{b['daughter_name']} ({b['daughter_pdg']}, "
                                f"flavour={dh} sign={ds})")
        species_out.append(rec)

    payload = {
        "schema": "hf_decay_parent_map_v2",
        "supersedes": "hf_decay_parent_map_v1",
        "derived_from": ("PYTHIA particleData, pinned install, via the extended "
                         "f4 probe emitting ALL channels"),
        "br_source": {
            "generator": "PYTHIA",
            "version": v1["pythia_version"],
            "table": "particleData, channels read after mayDecay(id,false)",
            "is_pdg": False,
            "note": ("NOT the PDG. Same source as v1 so the two are comparable; "
                     "switching to PDG values is an open owner decision recorded "
                     "in docs/MAP_V2_PREREGISTRATION.md section 4."),
        },
        "pythia_version": v1["pythia_version"],
        "ordinal_table_digest_fnv1a64": v1["ordinal_table_digest_fnv1a64"],
        "gate": v1["gate"],
        "species_count": len(species_out),
        "split_threshold_pct_of_total_weight": args.threshold_pct,
        "split_species_count": split_count,
        "scope_note": ("Species-level aggregation is applied ONLY to species v1 "
                       "reassigns. Terminals keep v1 semantics, so the terminal "
                       "set is identical to v1's by construction."),
        "unmapped_policy": v1["unmapped_policy"],
        "species": species_out,
    }
    body = json.dumps(payload, indent=2, sort_keys=True)
    payload["map_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print(f"MAP_V2_BUILT species={len(species_out)} split={split_count} "
          f"threshold={args.threshold_pct}% sha256={payload['map_sha256'][:16]}")
    for r in species_out:
        if r["split"]:
            frs = " ".join(f"{b['daughter_name']}={b['fraction']:.4f}"
                           for b in r["species_level_branches"])
            print(f"  SPLIT {r['name']:<10} {frs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
