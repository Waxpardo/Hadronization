#!/usr/bin/env python3
"""Species decomposition with block SEMs, both conventions.

THE ESTIMATOR IS FIXED BY PRE-REGISTRATION (per-tune processing, step 3) and
this implements exactly that, because the choice matters:

  * every nonlinear quantity is formed INSIDE a block before averaging. A
    fraction is computed per block from that block's own counts; the ten
    fractions are then averaged. A ratio of summed numerators to summed
    denominators is a DIFFERENT estimator with a smaller, wrong variance.
  * SEM = stdev(ten block values) / sqrt(10), sample stdev, dof = 9.
  * the pooled central value is quoted beside the block mean, never instead of
    it -- where they differ materially, that is reportable.

It also runs the integrity checks that gate the SEMs (steps I2/I3): the ten
blocks must SUM to the central exactly, bin by bin, or the ten values are not a
partition and the SEM is over the wrong thing.

Usage:
  extraction/decompose_with_block_sems.py RUNDIR --map decay_parent_map_v2.json
    where RUNDIR contains central/per_species.csv and block_1..10/per_species.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))


def load(p: Path) -> dict[int, float]:
    return {int(r["ordinal"]): float(r["total"])
            for r in csv.DictReader(p.open())}


def load_categories(p: Path) -> dict[int, str]:
    return {int(r["ordinal"]): r["category_name"]
            for r in csv.DictReader(p.open())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir", type=Path)
    ap.add_argument("--map", dest="mapfile", type=Path,
                    default=REPO / "AnalysisScripts/decay_parent_map_v2.json")
    ap.add_argument("--artifact", type=Path,
                    default=REPO / "AnalysisScripts/species_ordinals_v2.json")
    ap.add_argument("--tune", default="?")
    ap.add_argument("--i2-advisory", action="store_true",
                    help="downgrade I2 flags from a hard failure to an advisory. "
                         "Since 2026-08-13 I2 uses the robust MAD null rather "
                         "than the misspecified binomial one, so a flag now "
                         "means a bin genuinely stands out from its own "
                         "comparison and this escape hatch should be needed far "
                         "less often. It is kept so that the judgement, when "
                         "made, is EXPLICIT in the command line rather than "
                         "silent in the exit status.")
    args = ap.parse_args()

    central_csv = args.rundir / "central/per_species.csv"
    blocks = [args.rundir / f"block_{i}/per_species.csv" for i in range(1, 11)]
    for p in [central_csv] + blocks:
        if not p.exists():
            raise SystemExit(f"FAIL-CLOSED: missing {p}")

    central = load(central_csv)
    bl = [load(p) for p in blocks]
    cats = load_categories(central_csv)

    # ---- I3: the ten blocks must SUM to the central, exactly ---------------
    summed: dict[int, float] = defaultdict(float)
    for b in bl:
        for o, v in b.items():
            summed[o] += v
    ords = sorted(set(central) | set(summed))
    mism = [(o, central.get(o, 0.0), summed.get(o, 0.0))
            for o in ords if central.get(o, 0.0) != summed.get(o, 0.0)]
    print(f"TUNE {args.tune}")
    print(f"I3 block-sum == central : "
          f"{'PASS' if not mism else f'FAIL ({len(mism)} bins)'}  "
          f"central_total={sum(central.values()):.10g} "
          f"block_sum={sum(summed.values()):.10g}")
    for o, c, s in mism[:5]:
        print(f"   ordinal {o}: central={c!r} blocksum={s!r} diff={c-s!r}")

    # ---- I2: each block vs central --------------------------------------
    # THE NULL IS NAMED HERE, and it is not the binomial one. A block is a
    # tenth of the same events, and pair counts are event-clustered, so the
    # independence assumption behind the binomial variance is false by
    # construction -- measured at ~4.75x in variance. Under that null I2 flagged
    # 353 of 880 comparisons and the flags meant "the null is wrong", not "the
    # block is bad". `mad` measures the dispersion from the comparison itself
    # and asks whether any bin stands out from the rest, which is the localized
    # failure I2 exists to catch (E4 was exactly that shape).
    from compare_subset_parent import compare
    flags_total = 0
    for i, b in enumerate(bl, 1):
        try:
            scale, f, rows, flagged, unt, missing, diag = compare(
                b, central, null="mad", z_threshold=4.0, expect_scale=10.0)
        except SystemExit as e:
            print(f"I2 block_{i}: FAIL-CLOSED {e}")
            flags_total += 1
            continue
        flags_total += len(flagged)
        if flagged:
            print(f"I2 block_{i}: scale={scale:.3f} sigma^={diag['sigma_hat']:.2f} "
                  f"FLAGGED={len(flagged)} "
                  + ", ".join(f"ord{r[0]}(z={r[4]:+.1f})" for r in flagged[:4]))
    print(f"I2 block-vs-central     : "
          f"{'PASS (0 flags in 10 comparisons)' if flags_total == 0 else f'{flags_total} flags'}")

    # ---- the decomposition, both conventions -----------------------------
    dmap = json.loads(args.mapfile.read_text())
    art = json.loads(args.artifact.read_text())
    sys.path.insert(0, str(REPO / "tools"))
    from apply_decay_map import build_labels, terminal_distribution
    pdg_to_ord = {int(r["pdg"]): int(r["ordinal"]) for r in art["species"]}
    cat_name = {int(r["ordinal"]): r["category_name"] for r in art["species"]}
    name = {int(s["ordinal"]): s["name"] for s in dmap["species"]}
    by_ord = {int(s["ordinal"]): s for s in dmap["species"]}
    dist = terminal_distribution(by_ord, pdg_to_ord, split_mode=True)

    def structural(tbl):
        g = defaultdict(float)
        for o, v in tbl.items():
            g[cats.get(o, "?")] += v
        return g

    def experimental(tbl):
        g = defaultdict(float)
        for o, v in tbl.items():
            for t, fr in dist.get(o, {o: 1.0}).items():
                lab = (name[t] if cat_name.get(t) == "kCentralGround"
                       else f"UNMAPPED/{cat_name.get(t)}")
                g[lab] += v * fr
        return g

    for label, fn, top in (("DIQUARK-STRUCTURE (primary)", structural, 99),
                           ("EXPERIMENT-COMPARABLE (map v2)", experimental, 8)):
        print()
        print(f"=== {label} — tune {args.tune} ===")
        # fractions formed INSIDE each block, then averaged
        per_block = []
        for b in bl:
            g = fn(b)
            tot = sum(g.values())
            per_block.append({k: v / tot for k, v in g.items()})
        pooled = fn(central)
        ptot = sum(pooled.values())
        keys = sorted(pooled, key=lambda k: -pooled[k])[:top]
        print(f"{'group':<26}{'block mean %':>14}{'SEM':>9}{'pooled %':>11}{'diff/SEM':>10}")
        for k in keys:
            vals = [pb.get(k, 0.0) * 100 for pb in per_block]
            m = statistics.mean(vals)
            sem = statistics.stdev(vals) / (len(vals) ** 0.5)
            pv = 100 * pooled[k] / ptot
            pull = (m - pv) / sem if sem > 0 else 0.0
            print(f"{k:<26}{m:>14.4f}{sem:>9.4f}{pv:>11.4f}{pull:>10.2f}")
    print()

    # ---- exit status must report BOTH integrity checks ---------------------
    # It previously returned `0 if not mism else 3`, i.e. it depended only on
    # I3. `flags_total` was accumulated and then discarded, so this tool could
    # report hundreds of I2 failures and still exit 0 -- and an exit status is
    # exactly what a driver script reads. An integrity check whose result cannot
    # reach the caller is not a gate.
    status = 0
    if mism:
        status = 3
    if flags_total:
        if args.i2_advisory:
            print(f"I2 ADVISORY: {flags_total} flags, downgraded by "
                  f"--i2-advisory. The binomial null is misspecified for "
                  f"event-clustered counts; this is a declared judgement, not a "
                  f"pass.")
        else:
            print(f"I2 FAIL: {flags_total} flags across 10 block-vs-central "
                  f"comparisons. Pass --i2-advisory to declare this expected "
                  f"(the binomial null is known to be misspecified); do not "
                  f"ignore the exit status.")
            status = status or 4
    print(f"DECOMPOSE_DONE status={status} "
          f"(0=clean, 3=I3 block-sum mismatch, 4=I2 flags)")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
