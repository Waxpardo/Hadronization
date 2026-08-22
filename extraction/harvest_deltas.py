#!/usr/bin/env python3
"""Per-category systematic deltas for the variation campaigns.

Reads the deduplicated species-decomposition output of one variation campaign
(central + ten blocks per tune) and the committed sealed-nominal anchors, and
reports the delta per tune per diquark-structure category.

TWO ESTIMATORS, BOTH REPORTED. Pre-registration 2.2 registers the relative
shift formed INSIDE each block, averaged over ten, SEM over those ten, dof 9.
The second estimator is means-first with SEMs in quadrature. They are
different operations, so this tool prints both and never silently picks one.

LOW-STAT is the pre-registration 2.3 rule, reused verbatim: a class whose block
count falls below 1000 is reported and flagged, never dropped and never
patched. A nominal block of exactly zero makes a relative shift undefined; that
is reported as LOW-STAT-ZERO rather than given a value.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from systematics_delta import block_stats, delta_from_means, delta_per_block

CATEGORIES = ("kCentralGround", "kExcludedVector", "kExcludedExcited", "kMultiplyHeavy")
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
ANCHOR_DIR = {
    "MONASH": "merged_monash_dedup",
    "JUNCTIONS": "merged_junctions_dedup",
    "CLOSEPACKING": "merged_closepacking_dedup",
}
LOW_STAT_COUNTS = 1000.0


def read_category_counts(per_category_csv: Path) -> dict[str, float]:
    """Absolute counts per category, keyed by category name.

    `from_species` and `from_closure` are two independent routes to the same
    number and the reader fails closed if they disagree, so either column is
    the value. This takes `from_species`.
    """
    with per_category_csv.open() as handle:
        rows = list(csv.DictReader(handle))
    counts = {row["category_name"]: float(row["from_species"]) for row in rows}
    if not counts:
        raise ValueError(f"{per_category_csv} holds no category rows")
    return counts


def category_fractions(counts: dict[str, float]) -> dict[str, float]:
    """Per cent of the four-category partition. Sums to 100 by construction."""
    total = sum(counts.values())
    if total <= 0:
        raise ValueError("category total is not positive; a fraction is undefined")
    return {name: 100.0 * counts.get(name, 0.0) / total for name in CATEGORIES}


def is_low_stat(block_counts: list[float], threshold: float = LOW_STAT_COUNTS) -> bool:
    """Pre-registration 2.3: any block under the threshold flags the class."""
    return min(block_counts) < threshold


def counts_per_event(total_counts: float, events: int) -> float:
    """The E5 plausibility ratio. The defect signature was ~13 where truth is O(1)."""
    if events <= 0:
        raise ValueError("event exposure must be positive")
    return total_counts / events


def campaign_rows(sys_run: Path, anchors: Path, campaign: str) -> list[dict]:
    rows: list[dict] = []
    for tune in TUNES:
        anchor = anchors / ANCHOR_DIR[tune]
        variation_counts = [
            read_category_counts(sys_run / f"{tune}_block_{i}" / "per_category.csv")
            for i in range(1, 11)
        ]
        nominal_counts = [
            read_category_counts(anchor / f"block_{i}" / "per_category.csv")
            for i in range(1, 11)
        ]
        variation_fracs = [category_fractions(c) for c in variation_counts]
        nominal_fracs = [category_fractions(c) for c in nominal_counts]
        for category in CATEGORIES:
            v_seq = [f[category] for f in variation_fracs]
            n_seq = [f[category] for f in nominal_fracs]
            v_cnt = [c.get(category, 0.0) for c in variation_counts]
            n_cnt = [c.get(category, 0.0) for c in nominal_counts]
            flags = []
            if is_low_stat(v_cnt) or is_low_stat(n_cnt):
                flags.append("LOW-STAT")
            if any(value == 0.0 for value in n_seq):
                rows.append({
                    "campaign": campaign, "tune": tune, "category": category,
                    "delta_pct": None, "sem_pct": None,
                    "delta_means_pct": None, "sem_means_pct": None,
                    "flags": " ".join(flags + ["LOW-STAT-ZERO"]),
                })
                continue
            registered = delta_per_block(v_seq, n_seq)
            nominal_mean, nominal_sem, _ = block_stats(n_seq)
            cross_check = delta_from_means(v_seq, nominal_mean, nominal_sem)
            if not registered.resolved():
                flags.append("UNRESOLVED")
            rows.append({
                "campaign": campaign, "tune": tune, "category": category,
                "delta_pct": registered.value, "sem_pct": registered.sem,
                "delta_means_pct": cross_check.value, "sem_means_pct": cross_check.sem,
                "flags": " ".join(flags),
            })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sys-runs", type=Path, required=True)
    parser.add_argument("--anchors", type=Path, required=True)
    parser.add_argument("--campaigns", nargs="+", required=True)
    parser.add_argument("--events-per-tune", type=int, default=10_000_000)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    all_rows: list[dict] = []
    print(f"{'campaign':22s}{'tune':14s}{'total counts':>16s}{'counts/event':>14s}")
    for campaign in args.campaigns:
        for tune in TUNES:
            counts = read_category_counts(
                args.sys_runs / campaign / f"{tune}_central" / "per_category.csv")
            total = sum(counts.values())
            ratio = counts_per_event(total, args.events_per_tune)
            print(f"{campaign:22s}{tune:14s}{total:16,.0f}{ratio:14.4f}")
    print()
    for campaign in args.campaigns:
        rows = campaign_rows(args.sys_runs / campaign, args.anchors, campaign)
        all_rows.extend(rows)
        print(f"### {campaign}")
        print(f"  {'tune':14s}{'category':18s}{'D%':>11s}{'SEM':>9s}"
              f"{'D_means%':>11s}{'SEM_means':>11s}  flags")
        for row in rows:
            if row["delta_pct"] is None:
                print(f"  {row['tune']:14s}{row['category']:18s}"
                      f"{'--':>11s}{'--':>9s}{'--':>11s}{'--':>11s}  {row['flags']}")
                continue
            print(f"  {row['tune']:14s}{row['category']:18s}"
                  f"{row['delta_pct']:11.4f}{row['sem_pct']:9.4f}"
                  f"{row['delta_means_pct']:11.4f}{row['sem_means_pct']:11.4f}"
                  f"  {row['flags']}")
        print()
    if args.json_out:
        args.json_out.write_text(json.dumps(all_rows, indent=2, sort_keys=True) + "\n")
    resolved = [r for r in all_rows if r["delta_pct"] is not None]
    unresolved = [r for r in resolved if "UNRESOLVED" in r["flags"]]
    print(f"SUMMARY deltas={len(resolved)} unresolved={len(unresolved)} "
          f"low_stat_zero={len(all_rows) - len(resolved)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
