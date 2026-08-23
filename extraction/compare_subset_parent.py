#!/usr/bin/env python3
"""Compare every per-species subset bin with its parent table.

One defective anchor passed four aggregate checks within 0.02 percentage points.
A single bin remained about 10 sigma wrong and produced a false -7.4 sigma result.

The caller must select one of two null models because they answer different questions.

  **binomial** -- if the subset is drawn from the parent with sampling fraction
  f, a bin with parent count N contributes k ~ Binomial(N, f), so

      z = (k - N f) / sqrt(N f (1 - f))

  This assumes the pair counts are independent draws. THEY ARE NOT: a pair count
  is event-clustered, one event contributing many correlated pairs, and the
  measured overdispersion is ~4.75 in variance (~2.2x in sigma) --
  the MONASH central table S3, 353 flags in 880 comparisons. So this null
  is KNOWN to be misspecified for block-vs-central integrity work. It is kept,
  and must be named explicitly, because it is the computation behind a published
  audit trail (E4's "30 of 88") and that history is pinned, not rewritten.

  **mad** -- a robust empirical null that measures the dispersion instead of
  assuming it. Form the binomial pull for every testable bin, then take the
  median as the centre and the MAD as the width:

      p_i     = (k_i - N_i f) / sqrt(N_i f (1 - f))
      sigma^  = 1.4826 * median(|p_i - median(p)|)
      z_i     = (p_i - median(p)) / sigma^

  It asks the question I2 actually needs answered: *does this bin stand out
  against the other bins of this same comparison?* -- not *is it consistent with
  an independence model we already know is wrong?* The 1.4826 makes sigma^ a
  consistent estimator of a Gaussian sigma, so a correctly-specified binomial
  case returns sigma^ ~ 1 and the two nulls agree; the factor by which it exceeds
  1 IS the measured overdispersion, and it is reported rather than assumed.

  CENTRING ON THE MEDIAN IS DELIBERATE. It makes this a test for LOCALIZED
  outliers, which is what E4 was and what I2 is looking for. A uniform offset
  common to every bin is not detectable here by construction -- that is I3's job
  (the blocks must sum to the central exactly) and `--expect-scale`'s.

f is measured from the totals rather than assumed, which is the honest choice
when the subset's provenance is unknown -- but it means a subset that is NOT a
subset will produce a scale that fits the totals and z-scores that are then
meaningful only as "inconsistent with any uniform sampling".

FAIL-CLOSED on non-integer contents: the binomial variance is a counting model,
and applying it to weighted contents would understate the variance and
manufacture significance. The MAD null is built on the same pulls, so it
inherits the same requirement.

Usage:
  extraction/compare_subset_parent.py SUBSET.csv PARENT.csv --null {binomial,mad}
      [--expect-scale N]
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from pathlib import Path

DEFAULT_Z = 4.0
DEFAULT_MIN_EXPECTED = 10.0

# The admissible nulls. There is deliberately no default anywhere in this file:
# both call sites -- I2 in decompose_with_block_sems.py and the pinned E4
# regression in tests/test_compare_subset_parent.py -- must name one.
NULL_MODELS = ("binomial", "mad")
MAD_TO_SIGMA = 1.4826


def load(path: Path) -> dict[int, float]:
    rows = list(csv.DictReader(path.open()))
    if not rows:
        raise SystemExit(f"FAIL-CLOSED: {path} is empty")
    col = "total" if "total" in rows[0] else None
    if col is None:
        raise SystemExit(f"FAIL-CLOSED: {path} has no 'total' column")
    out: dict[int, float] = {}
    for r in rows:
        out[int(r["ordinal"])] = float(r[col])
    return out


def compare(subset: dict[int, float], parent: dict[int, float],
            *,
            null: str,
            z_threshold: float = DEFAULT_Z,
            min_expected: float = DEFAULT_MIN_EXPECTED,
            expect_scale: float | None = None):
    """Pure decision, so it is testable without files.

    `null` is keyword-only and REQUIRED: see the module docstring. Returns
    (scale, f, rows, flagged, untestable, missing, diag), where `diag` carries
    the null's own parameters -- for `mad`, the measured overdispersion, which
    is the number that says whether the binomial null was defensible here.
    """
    if null not in NULL_MODELS:
        raise SystemExit(
            f"FAIL-CLOSED: null must be one of {NULL_MODELS}, got {null!r}. "
            "There is no default: the binomial null is misspecified for "
            "event-clustered pair counts, and inheriting it silently is how a "
            "misspecified null becomes a published number.")
    for name, tbl in (("subset", subset), ("parent", parent)):
        bad = [o for o, v in tbl.items() if v != int(v)]
        if bad:
            raise SystemExit(
                f"FAIL-CLOSED: {name} has non-integer contents at ordinals "
                f"{bad[:5]}; the binomial model is a counting model and would "
                f"manufacture significance on weights.")

    s_tot, p_tot = sum(subset.values()), sum(parent.values())
    if p_tot <= 0:
        raise SystemExit("FAIL-CLOSED: parent total is zero")
    f = s_tot / p_tot
    scale = (1.0 / f) if f > 0 else float("inf")
    if expect_scale is not None and abs(scale - expect_scale) > 0.05 * expect_scale:
        raise SystemExit(
            f"FAIL-CLOSED: measured scale {scale:.3f} differs from expected "
            f"{expect_scale:.3f} by more than 5 %. These may not be "
            f"subset/parent.")

    missing = sorted(set(subset) - set(parent))
    pulls, untestable = [], []
    for o in sorted(set(parent) | set(subset)):
        N = parent.get(o, 0.0)
        k = subset.get(o, 0.0)
        exp = N * f
        if exp < min_expected:
            untestable.append((o, k, N, exp))
            continue
        var = N * f * (1.0 - f)
        # The binomial pull. Under `binomial` this IS the test statistic; under
        # `mad` it is the raw residual the empirical null is then built from.
        pull = (k - exp) / math.sqrt(var) if var > 0 else 0.0
        pulls.append((o, k, N, exp, pull))

    diag: dict[str, float] = {}
    if null == "binomial":
        rows = list(pulls)
    else:
        values = [p[4] for p in pulls]
        if not values:
            rows = []
            diag = {"centre": 0.0, "sigma_hat": 0.0, "sigma_eff": 1.0,
                    "overdispersion": 0.0, "floored": True}
        else:
            centre = statistics.median(values)
            sigma_hat = MAD_TO_SIGMA * statistics.median(
                [abs(v - centre) for v in values])
            # THE COUNTING FLOOR, and why it is not a fudge. The pulls are
            # already in units of the binomial sigma, so sigma^ = 1 means "as
            # dispersed as counting statistics require". A measured width BELOW
            # 1 is not a tighter null -- for integer counts drawn from a parent
            # it is impossible unless the subset is not a sample at all, e.g. a
            # deterministic split (blocks built by exact division rather than by
            # sampling: sigma^ collapses to ~0.002 there, and dividing sub-count
            # quantization residue by it manufactures significance out of
            # rounding). This null exists to WIDEN a null that is too narrow for
            # event-clustered data; letting it narrow below the counting floor
            # would invert its purpose. So the floor is applied to the test
            # statistic while the RAW sigma^ is still reported -- the raw value
            # is the calibration diagnostic and must not be silently replaced.
            sigma_eff = max(sigma_hat, 1.0)
            diag = {"centre": centre, "sigma_hat": sigma_hat,
                    "sigma_eff": sigma_eff, "overdispersion": sigma_hat,
                    "floored": sigma_hat < 1.0}
            rows = [(o, k, N, exp, (pull - centre) / sigma_eff)
                    for o, k, N, exp, pull in pulls]
    flagged = [r for r in rows if abs(r[4]) > z_threshold]
    return scale, f, rows, flagged, untestable, missing, diag


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("subset", type=Path)
    ap.add_argument("parent", type=Path)
    ap.add_argument("--null", required=True, choices=NULL_MODELS,
                    help="REQUIRED, deliberately without a default. 'binomial' "
                         "is the historical computation behind E4's published "
                         "'30 of 88' and is known to be misspecified for "
                         "event-clustered pair counts; 'mad' is the robust "
                         "empirical null that measures the dispersion instead "
                         "of assuming it. Naming it is the point.")
    ap.add_argument("--expect-scale", type=float, default=None)
    ap.add_argument("--z", type=float, default=DEFAULT_Z)
    ap.add_argument("--min-expected", type=float, default=DEFAULT_MIN_EXPECTED)
    ap.add_argument("--names", type=Path, default=None,
                    help="decay_parent_map json, to label ordinals")
    args = ap.parse_args()

    subset, parent = load(args.subset), load(args.parent)
    scale, f, rows, flagged, untestable, missing, diag = compare(
        subset, parent, null=args.null, z_threshold=args.z,
        min_expected=args.min_expected, expect_scale=args.expect_scale)

    label = {}
    if args.names and args.names.exists():
        import json
        for s in json.loads(args.names.read_text())["species"]:
            label[int(s["ordinal"])] = s["name"]

    print(f"SUBSET {args.subset}")
    print(f"PARENT {args.parent}")
    print(f"NULL   {args.null}")
    print(f"measured scale = {scale:.4f}  (sampling fraction f = {f:.6f})")
    print(f"bins tested = {len(rows)}   untestable (expected < {args.min_expected}) "
          f"= {len(untestable)}   |z| threshold = {args.z}")
    if args.null == "mad":
        # The overdispersion is reported, not assumed. sigma^ ~ 1 would mean the
        # binomial null was defensible here after all.
        print(f"empirical null: centre = {diag['centre']:+.4f}, "
              f"sigma^ = {diag['sigma_hat']:.4f} "
              f"(= binomial sigma x {diag['sigma_hat']:.2f}; "
              f"variance overdispersion {diag['sigma_hat'] ** 2:.2f}x)")
        if diag["floored"]:
            print(f"  NOTE sigma^ < 1 is below the counting floor, so the test "
                  f"used sigma = {diag['sigma_eff']:.4f}. A sub-binomial width "
                  f"means this subset is not an independent sample of the "
                  f"parent (a deterministic split does this).")
    if missing:
        print(f"WARNING ordinals present in subset but absent from parent: {missing}")
    print()
    if flagged:
        print(f"{'ordinal':>8} {'name':<14}{'subset':>12}{'parent':>14}"
              f"{'expected':>13}{'z':>8}")
        for o, k, N, exp, z in sorted(flagged, key=lambda r: -abs(r[4])):
            print(f"{o:>8} {label.get(o,''):<14}{k:>12.0f}{N:>14.0f}"
                  f"{exp:>13.1f}{z:>8.2f}")
    print(f"SUBSET_PARENT_COMPARE null={args.null} flagged={len(flagged)} "
          f"tested={len(rows)} scale={scale:.4f}")
    return 1 if flagged else 0


if __name__ == "__main__":
    raise SystemExit(main())
