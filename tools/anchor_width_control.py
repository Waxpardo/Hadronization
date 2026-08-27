#!/usr/bin/env python3
"""Compare the quarantined anchor with genuine one-tenth MONASH blocks.

The anchor has 30 of 88 bins beyond |z|=4 and 16 deviations above 2%.
The ten canonical MONASH blocks provide the required peer distribution.

The anchor and its parent replicate charm triggers 24 times and beauty triggers 26 times.
Replication leaves fractional deviations unchanged but scales a binomial pull by sqrt(R):

    (Rk - RNf) / sqrt(RNf(1-f))  =  sqrt(R) * (k - Nf) / sqrt(Nf(1-f))

The replicated blocks are therefore the direct peer group.
The script reports both sweeps and checks the measured inflation against sqrt(R).

Run:
  tools/anchor_width_control.py
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "extraction"))
from compare_subset_parent import compare  # noqa: E402

A = REPO / "evidence"
DEDUP = A / "merged_monash_dedup"
REPL_CENTRAL = A / "merged_monash_replicated/per_species.csv"
REPL_BLOCKS = A / "merged_monash_replicated_blocks"
ANCHOR = A / "extraction_dual/per_species.csv"

MIN_EXPECTED = 10.0
Z = 4.0


def load(path: Path) -> dict[int, float]:
    return {int(r["ordinal"]): float(r["total"])
            for r in csv.DictReader(path.open())}


def fractional_profile(subset, parent):
    """Deviations as PERCENTAGES -- the quantity E4 actually argues from.

    Deliberately null-free: |k / (N f) - 1|. No variance model can influence it,
    which is what makes it the right thing to compare across sweeps.
    """
    f = sum(subset.values()) / sum(parent.values())
    devs = []
    for ordinal, n in parent.items():
        expected = n * f
        if expected < MIN_EXPECTED:
            continue
        devs.append(abs(subset.get(ordinal, 0.0) / expected - 1.0) * 100.0)
    devs.sort(reverse=True)
    return devs


def row(label, subset, parent):
    _s, _f, rows, flagged, _u, _m, diag = compare(
        subset, parent, null="mad", z_threshold=Z, expect_scale=10.0)
    _s2, _f2, _r2, flagged_b, _u2, _m2, _d2 = compare(
        subset, parent, null="binomial", z_threshold=Z, expect_scale=10.0)
    devs = fractional_profile(subset, parent)
    return {
        "label": label,
        "sigma": diag["sigma_hat"],
        "mad_flags": len(flagged),
        "binom_flags": len(flagged_b),
        "tested": len(rows),
        "over2": sum(1 for d in devs if d > 2.0),
        "max_dev": devs[0],
        "med_dev": statistics.median(devs),
    }


def sweep(name, central_path, block_dir):
    central = load(central_path)
    out = []
    for i in range(1, 11):
        out.append(row(f"block_{i}", load(block_dir / f"block_{i}/per_species.csv"),
                       central))
    print(f"\n=== {name} ===")
    print(f"{'':>9}{'sigma^':>9}{'binom':>7}{'mad':>5}{'>2%':>6}"
          f"{'maxdev%':>9}{'meddev%':>9}")
    for r in out:
        print(f"{r['label']:>9}{r['sigma']:>9.3f}{r['binom_flags']:>7}"
              f"{r['mad_flags']:>5}{r['over2']:>6}{r['max_dev']:>9.2f}"
              f"{r['med_dev']:>9.2f}")
    return out


def summarise(key, rows):
    vals = [r[key] for r in rows]
    return statistics.mean(vals), min(vals), max(vals)


def main() -> int:
    for p in (REPL_CENTRAL, ANCHOR, DEDUP, REPL_BLOCKS):
        if not p.exists():
            print(f"FAIL: missing fixture {p}")
            return 1

    dedup = sweep("DEDUPLICATED blocks vs deduplicated central",
                  DEDUP / "central/per_species.csv", DEDUP)
    repl = sweep("REPLICATED blocks vs replicated central "
                 "-- THE ANCHOR'S PEER GROUP", REPL_CENTRAL, REPL_BLOCKS)

    anchor = row("ANCHOR", load(ANCHOR), load(REPL_CENTRAL))
    print(f"\n{'ANCHOR':>9}{anchor['sigma']:>9.3f}{anchor['binom_flags']:>7}"
          f"{anchor['mad_flags']:>5}{anchor['over2']:>6}"
          f"{anchor['max_dev']:>9.2f}{anchor['med_dev']:>9.2f}")

    ds = statistics.mean([r["sigma"] for r in dedup])
    rs = statistics.mean([r["sigma"] for r in repl])
    print(f"\nreplication inflation of sigma^: {rs / ds:.2f}x measured, "
          f"sqrt(24.2) = 4.92 predicted")

    print("\n=== THE ANCHOR AGAINST ITS PEER GROUP ===")
    verdicts = []
    for key, name in (("sigma", "sigma^ (MAD width)"),
                      ("binom_flags", "binomial flags |z|>4"),
                      ("over2", "bins deviating >2%"),
                      ("max_dev", "largest deviation %")):
        mean, lo, hi = summarise(key, repl)
        val = anchor[key]
        inside = lo <= val <= hi
        verdicts.append(inside or val < lo)
        where = ("INSIDE" if inside else
                 "BELOW range" if val < lo else "ABOVE range -- anomalous")
        print(f"  {name:<24} real: mean {mean:>7.2f} range [{lo:.2f}, {hi:.2f}]"
              f"   anchor {val:>7.2f}   {where}")

    print()
    if all(verdicts):
        print("VERDICT: on every metric E4 cites, the anchor is indistinguishable")
        print("from -- or quieter than -- a genuine 1/10 subset of the same data.")
        print("The bin-level statistical case for the quarantine does not survive")
        print("this control. The quarantine's OTHER grounds (the artifact is")
        print("unprovenanced; its physics result was contradicted by two traceable")
        print("datasets) are untouched by this and are not statistical claims.")
    else:
        print("VERDICT: the anchor exceeds the real-subset range on at least one")
        print("metric -- the bin-level case survives. See the rows marked ABOVE.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
