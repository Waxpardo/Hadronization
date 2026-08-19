#!/usr/bin/env python3
"""Reconstruct the DEDUPLICATED MONASH decomposition from the replicated one.

WHAT THIS IS, AND WHAT IT IS NOT. This is **not** a re-extraction. The corrected
table it produces is an exact arithmetic inversion of the published (replicated)
per-species CSV. It exists because the defect (E5) was found after the merged v3
product had been produced, and that product lives on the cluster: re-running
`extraction/extract_species_decomposition.py` -- which is now fixed -- requires
the 300 merged pair files, not just the committed CSV. Until that re-run
happens, this tool makes the corrected numbers regenerable from committed inputs
rather than asserted in prose.

WHY THE INVERSION IS EXACT FOR 87 OF 95 SPECIES. The closure loop in the
analysis weights each associate by `-q_trig * q_assoc`, where the charge is
taken **in the trigger's own sector**. An associate whose charge in that sector
is zero is skipped. So:

  * a CHARM trigger's closure can only ever fill species with q_c != 0;
  * a BEAUTY trigger's closure can only ever fill species with q_b != 0.

Each charm trigger is copied into 24 pair files and each beauty trigger into 26,
so the published total for species b is

    T[b] = 24 * C[b] + 26 * B[b]

with C[b] the sum over the six charm triggers and B[b] over the six beauty
triggers. The quantity the paper needs is D[b] = C[b] + B[b]. Hence:

  * q_c != 0, q_b == 0  ->  B[b] = 0, so D[b] = T[b] / 24   EXACT
  * q_b != 0, q_c == 0  ->  C[b] = 0, so D[b] = T[b] / 26   EXACT
  * both nonzero        ->  underdetermined; D[b] lies in [T[b]/26, T[b]/24]

The third case is the eight beauty-charm species (B_c mesons and the Xi_bc /
Omega_bc baryons). Their combined published weight is 129,164 of
1,298,655,240 -- 0.0099 % -- and the resulting ambiguity on the deduplicated
total is 414 counts out of ~53.66 million, i.e. 0.00077 %. The tool reports the
bracket explicitly and never hides it inside a point estimate.

THE FINGERPRINT IS VERIFIED, NOT ASSUMED. Before inverting anything the tool
checks that every charm-only total really is divisible by 24 and every
beauty-only total by 26. If the published product were NOT replicated those
divisibilities would fail immediately, and the tool refuses to produce a
"correction" for a table that does not carry the defect.

Usage:
  tools/reconstruct_deduplicated_decomposition.py [--published CSV] [--out DIR]
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ORDINALS = REPO / "AnalysisScripts/species_ordinals_v2.json"
REGISTRY = REPO / "config/heavy_flavour_pair_registry_v1.json"
PUBLISHED = REPO / "AnalysisScripts/anchors/merged_monash_central/per_species.csv"


def replication_factors(registry: Path) -> dict[str, int]:
    """Measure the per-sector replication from the registry. Never hard-coded."""
    payload = json.loads(registry.read_text())
    seen: dict[str, set[int]] = defaultdict(set)
    counts: dict[tuple[str, int], int] = defaultdict(int)
    for row in payload["pairs"]:
        counts[(row["sector"], int(row["trigger_pdg"]))] += 1
    for (sector, _pdg), n in counts.items():
        seen[sector].add(n)
    factors = {}
    for sector, values in seen.items():
        if len(values) != 1:
            raise SystemExit(
                f"FAIL-CLOSED: {sector} triggers have unequal replication "
                f"{sorted(values)}; a single sector factor is not defined and "
                "the inversion below would be wrong. Re-extract instead."
            )
        factors[sector] = values.pop()
    return factors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--published", type=Path, default=PUBLISHED)
    ap.add_argument("--ordinals", type=Path, default=ORDINALS)
    ap.add_argument("--registry", type=Path, default=REGISTRY)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    factors = replication_factors(args.registry)
    charm, beauty = factors["charm"], factors["beauty"]
    info = {int(r["ordinal"]): r
            for r in json.loads(args.ordinals.read_text())["species"]}
    published = {int(r["ordinal"]): int(float(r["total"]))
                 for r in csv.DictReader(args.published.open())}

    # ---- verify the fingerprint before inverting ---------------------------
    violations = []
    for ordinal, value in published.items():
        rec = info[ordinal]
        if rec["q_c"] and not rec["q_b"] and value % charm:
            violations.append(("charm-only", ordinal, value, charm))
        elif rec["q_b"] and not rec["q_c"] and value % beauty:
            violations.append(("beauty-only", ordinal, value, beauty))
        elif not rec["q_c"] and not rec["q_b"] and value:
            violations.append(("sector-neutral but filled", ordinal, value, 0))
    if violations:
        raise SystemExit(
            "FAIL-CLOSED: the published table does not carry the replication "
            f"fingerprint ({len(violations)} violation(s), first "
            f"{violations[0]}). Either it was already deduplicated, or the "
            "replication is not a clean per-sector factor. Do not 'correct' it "
            "with this tool -- re-extract."
        )

    # ---- invert -------------------------------------------------------------
    rows = []
    lo_tot = hi_tot = Fraction(0)
    cat_lo: dict[int, Fraction] = defaultdict(Fraction)
    cat_hi: dict[int, Fraction] = defaultdict(Fraction)
    exact_count = bracket_count = 0
    for ordinal in sorted(published):
        value, rec = published[ordinal], info[ordinal]
        qc, qb = rec["q_c"], rec["q_b"]
        if qc and not qb:
            lo = hi = Fraction(value, charm)
            basis = f"charm-only /{charm}"
            exact_count += 1
        elif qb and not qc:
            lo = hi = Fraction(value, beauty)
            basis = f"beauty-only /{beauty}"
            exact_count += 1
        else:
            lo, hi = Fraction(value, beauty), Fraction(value, charm)
            basis = f"mixed-sector bracket /{beauty}..{charm}"
            bracket_count += 1
        lo_tot += lo
        hi_tot += hi
        cat_lo[rec["category"]] += lo
        cat_hi[rec["category"]] += hi
        rows.append((ordinal, rec["pdg"], rec["category"], rec["category_name"],
                     value, lo, hi, basis))

    out_dir = args.out or args.published.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    species_out = out_dir / "per_species_deduplicated.csv"
    with species_out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ordinal", "pdg", "category", "category_name",
                    "published_replicated", "dedup_low", "dedup_high", "basis"])
        for ordinal, pdg, cat, name, value, lo, hi, basis in rows:
            w.writerow([ordinal, pdg, cat, name, value,
                        f"{float(lo):.6f}", f"{float(hi):.6f}", basis])

    category_out = out_dir / "per_category_deduplicated.csv"
    pub_tot = sum(published.values())
    with category_out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["category", "category_name", "published_replicated",
                    "published_share_pct", "dedup_low", "dedup_high",
                    "dedup_share_pct_low", "dedup_share_pct_high", "delta_pp"])
        cat_pub: dict[int, int] = defaultdict(int)
        cat_name: dict[int, str] = {}
        for ordinal, _pdg, cat, name, value, _lo, _hi, _b in rows:
            cat_pub[cat] += value
            cat_name[cat] = name
        for cat in sorted(set(cat_lo) | set(cat_pub)):
            lo, hi = cat_lo[cat], cat_hi[cat]
            ps = 100 * Fraction(cat_pub[cat], pub_tot)
            sl = 100 * lo / hi_tot
            sh = 100 * hi / lo_tot
            mid = (sl + sh) / 2
            w.writerow([cat, cat_name.get(cat, "?"), cat_pub[cat],
                        f"{float(ps):.6f}", f"{float(lo):.6f}", f"{float(hi):.6f}",
                        f"{float(sl):.6f}", f"{float(sh):.6f}",
                        f"{float(mid - ps):+.6f}"])

    print(f"REPLICATION measured from registry: charm {charm}x, beauty {beauty}x")
    print(f"FINGERPRINT verified: {exact_count} species invert exactly, "
          f"{bracket_count} are mixed-sector and bracketed")
    print(f"PUBLISHED (replicated) total : {pub_tot:,}")
    print(f"DEDUPLICATED total           : {float(lo_tot):,.1f} .. "
          f"{float(hi_tot):,.1f}")
    print(f"  residual ambiguity         : {float(hi_tot - lo_tot):.1f} counts "
          f"({float(100 * (hi_tot - lo_tot) / lo_tot):.6f} %)")
    print(f"  inflation factor           : {float(pub_tot / hi_tot):.4f} .. "
          f"{float(pub_tot / lo_tot):.4f}")
    print(f"wrote {species_out}")
    print(f"wrote {category_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
