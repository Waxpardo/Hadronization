#!/usr/bin/env python3
"""Aggregate the M7 unresolved-origin systematic across the ten canonical blocks.

WHAT M7 IS. Heavy-flavour origin is never tie-broken: a hadron whose heavy quark
cannot be traced unambiguously to the selected hard subprocess is classified
`kUnresolved` and dropped. Dropping is only safe if the dropped sample looks like
the kept one, and it does not -- the unresolved sample is baryon-enriched, and
the unresolved *rate* is tune-dependent. Since the observable is whether a heavy
baryon's balancing partner is a baryon, a baryon-enriched loss of tune-dependent
size acts directly on the measurement. `Validation/MeasureUnresolvedSystematic.C`
quantifies it per file; this aggregates to the number the paper quotes.

CENTRAL VALUE FROM POOLED COUNTS, UNCERTAINTY FROM BLOCK SPREAD. The two are
different questions and must not be conflated:

  - the central value is computed from the SUMMED counts over all ten blocks, so
    it is the whole-campaign ratio and carries no block-averaging bias (a mean of
    per-block ratios is not the ratio of the sums when block sizes differ);
  - the uncertainty is the standard error of the ten per-block values,
    `stdev / sqrt(10)`, which is the project's standard machinery and the same
    n=10 the species decomposition will use.

Reporting the pooled ratio with a block SEM is deliberate: the SEM measures how
much the answer moves between statistically independent thirds of the campaign,
which is the uncertainty a reader cares about.

Usage:
  extraction/aggregate_m7.py BLOCK_LOG [BLOCK_LOG ...]
"""

from __future__ import annotations

import argparse
import collections
import statistics
import sys
from pathlib import Path


def parse(paths: list[Path]) -> tuple[dict[str, dict[int, dict[str, float]]], set[str]]:
    out: dict[str, dict[int, dict[str, float]]] = collections.defaultdict(dict)
    sectors: set[str] = set()
    for path in paths:
        for line in path.read_text().splitlines():
            if not line.startswith("M7_BLOCK "):
                continue
            kv = dict(t.split("=", 1) for t in line.split()[1:] if "=" in t)
            if "ERROR" in line or "tune" not in kv:
                sys.stderr.write(f"skipping malformed/error line: {line}\n")
                continue
            # `sector` is a label, not a measurement, and must be excluded from
            # the float conversion -- float("b") would abort the whole run.
            # Absent means charm, so pre-existing charm logs parse unchanged.
            sectors.add(kv.get("sector", "c"))
            out[kv["tune"]][int(kv["block"])] = {
                k: float(v) for k, v in kv.items()
                if k not in ("block", "tune", "sector")
            }
    return out, sectors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+", type=Path)
    ap.add_argument("--expect-blocks", type=int, default=10)
    args = ap.parse_args()

    data, sectors = parse(args.logs)
    if not data:
        raise SystemExit("FAIL-CLOSED: no M7_BLOCK lines found")
    # Charm and beauty are different measurements; pooling them would produce a
    # number that is neither.
    if len(sectors) != 1:
        raise SystemExit(
            f"FAIL-CLOSED: logs mix sectors {sorted(sectors)}. Aggregate one "
            f"sector at a time."
        )
    sector = sectors.pop()
    print(f"SECTOR {'charm' if sector == 'c' else 'beauty'} (sector={sector})")

    print(f"{'tune':<14} {'blocks':>6} {'unres rate %':>22} "
          f"{'baryon % (measured)':>26} {'baryon % (inclusive)':>26} "
          f"{'relative shift %':>22}")

    rows = []
    for tune in sorted(data):
        blocks = data[tune]
        if len(blocks) != args.expect_blocks:
            raise SystemExit(
                f"FAIL-CLOSED: {tune} has {len(blocks)} blocks, expected "
                f"{args.expect_blocks}. A partial set would give a SEM over the "
                f"wrong n."
            )
        ub = sum(b["ub"] for b in blocks.values())
        um = sum(b["um"] for b in blocks.values())
        rb = sum(b["rb"] for b in blocks.values())
        rm = sum(b["rm"] for b in blocks.values())
        unres, res = ub + um, rb + rm

        pooled_rate = 100.0 * unres / (res + unres)
        pooled_measured = 100.0 * rb / res
        pooled_inclusive = 100.0 * (rb + ub) / (res + unres)
        pooled_shift = 100.0 * (pooled_inclusive - pooled_measured) / pooled_measured

        def sem(key: str) -> float:
            vals = [b[key] for b in blocks.values()]
            return statistics.stdev(vals) / (len(vals) ** 0.5)

        r = {
            "tune": tune, "blocks": len(blocks),
            "unresolved_n": int(unres), "resolved_n": int(res),
            "rate": pooled_rate, "rate_sem": sem("unresolved_rate_pct"),
            "measured": pooled_measured, "measured_sem": sem("measured_baryon_pct"),
            "inclusive": pooled_inclusive, "inclusive_sem": sem("inclusive_baryon_pct"),
            "shift": pooled_shift, "shift_sem": sem("relative_shift_pct"),
            "unres_baryon_pct": 100.0 * ub / unres if unres else 0.0,
        }
        rows.append(r)
        print(f"{tune:<14} {len(blocks):>6} "
              f"{r['rate']:>13.4f} ± {r['rate_sem']:<6.4f} "
              f"{r['measured']:>17.4f} ± {r['measured_sem']:<6.4f} "
              f"{r['inclusive']:>17.4f} ± {r['inclusive_sem']:<6.4f} "
              f"{r['shift']:>13.4f} ± {r['shift_sem']:<6.4f}")

    print()
    print("counts and baryon enrichment of the dropped sample:")
    for r in rows:
        enrich = r["unres_baryon_pct"] / r["measured"] if r["measured"] else 0.0
        print(f"  {r['tune']:<14} unresolved_n={r['unresolved_n']:>9}  "
              f"resolved_n={r['resolved_n']:>10}  "
              f"unresolved_baryon%={r['unres_baryon_pct']:>7.3f}  "
              f"enrichment={enrich:>5.2f}x")
    print()
    print("SEM is over the ten canonical blocks (n=10); central values are from "
          "pooled counts, not averaged ratios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
