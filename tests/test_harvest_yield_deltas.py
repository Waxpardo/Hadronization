#!/usr/bin/env python3
"""The per-class yield delta arithmetic, on hand-computed anchors.

Every anchor below is chosen so the answer is exact in decimal and can be
checked without running the code. The SEM pairs are 3-4-5 triangles for that
reason: sqrt(3^2 + 4^2) = 5, with no rounding to argue about.
"""
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "extraction"))

from harvest_yield_deltas import (  # noqa: E402
    K_SIGMA, identical_row_sets, is_unresolved, relative_shift, significance,
    printed_half_ulp, trigger_consistency, triggers_per_event,
    yield_delta)

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


# --- the delta and its SEM ------------------------------------------------
# 5 - 2 = 3.  sqrt(3^2 + 4^2) = 5.  Both exact in binary floating point.
delta, sem = yield_delta(5.0, 3.0, 2.0, 4.0)
check("Delta is variation minus nominal", delta == 3.0, str(delta))
check("SEM(Delta) adds the two SEMs in quadrature", sem == 5.0, str(sem))

# A realistic-scale anchor, checked at the six figures the report prints.
# 0.12 - 0.10 = 0.02;  sqrt(0.003^2 + 0.004^2) = sqrt(2.5e-5) = 0.005.
d2, s2 = yield_delta(0.12, 0.003, 0.10, 0.004)
check("a yield-scale Delta prints 0.02 at six figures", "%.6g" % d2 == "0.02", "%.17g" % d2)
check("a yield-scale SEM prints 0.005 at six figures", "%.6g" % s2 == "0.005", "%.17g" % s2)

try:
    yield_delta(1.0, -1.0, 1.0, 1.0)
    check("a negative SEM is refused", False, "no exception")
except ValueError:
    check("a negative SEM is refused", True)

# --- the 2-sigma flag -----------------------------------------------------
check("the default k is 2", K_SIGMA == 2.0, str(K_SIGMA))
check("|Delta| = 3 against SEM 5 is flagged", is_unresolved(3.0, 5.0) is True)
check("|Delta| = 11 against SEM 5 is not flagged", is_unresolved(11.0, 5.0) is False)
# THE BOUNDARY. The rule is |Delta| < 2*SEM, so a Delta at exactly 2 SEM is
# resolved, not flagged.
check("a Delta at exactly 2 SEM is resolved, not flagged",
      is_unresolved(10.0, 5.0) is False)
check("a negative Delta is flagged on its magnitude",
      is_unresolved(-3.0, 5.0) is True)

check("significance is |Delta| / SEM", significance(3.0, 5.0) == 0.6)
check("a zero SEM with a non-zero Delta is infinitely significant",
      significance(1.0, 0.0) == math.inf)
check("a zero SEM with a zero Delta is not significant",
      significance(0.0, 0.0) == 0.0)

# --- the relative shift, and the cell that cannot carry one ---------------
check("the relative shift is per cent of the nominal",
      relative_shift(3.0, 2.0) == 150.0, str(relative_shift(3.0, 2.0)))
check("a zero nominal returns None rather than a number",
      relative_shift(0.5, 0.0) is None)
check("a zero Delta on a live nominal is a real zero, not None",
      relative_shift(0.0, 2.0) == 0.0)

# --- the absolute counts --------------------------------------------------
agree = trigger_consistency(100.0, [10.0] * 10)
check("ten blocks of ten account for a central hundred",
      agree["agrees"] is True and agree["difference"] == 0.0, str(agree))
disagree = trigger_consistency(100.0, [10.0] * 9 + [11.0])
check("a block sum over the central count is caught",
      disagree["agrees"] is False and disagree["difference"] == 1.0, str(disagree))
check("the block count is reported", agree["n_blocks"] == 10)

# THE LOG'S OWN ROUNDING. `1.3646e+06` records five significant figures, so the
# count it stands for lies in a window 100 wide and the half-ulp is 50.
# `1.36637e+06` records six, so 10 wide and the half-ulp is 5. `161365` prints
# every digit, so 1 wide and the half-ulp is 0.5.
check("a five-figure scientific count has a half-ulp of 50",
      printed_half_ulp("1.3646e+06") == 50.0, str(printed_half_ulp("1.3646e+06")))
check("a six-figure scientific count has a half-ulp of 5",
      printed_half_ulp("1.36637e+06") == 5.0, str(printed_half_ulp("1.36637e+06")))
check("a six-digit integer count has a half-ulp of a half",
      printed_half_ulp("161365") == 0.5, str(printed_half_ulp("161365")))

# The real 2026-08-18 nominal row: CHARM D^{+} MONASH D- in the integrated bin,
# read off vintegrated_closure.log. TWO of the ten blocks print five significant
# figures rather than six -- `1.3646e+06` and `1.3635e+06`, whose sixth digit is
# a zero ROOT does not print -- so the bound is 2*50 + 8*5 = 140, not 95. The
# observed shortfall is 17.
REAL_TOKENS = ["1.3646e+06", "1.36637e+06", "1.36666e+06", "1.36644e+06",
               "1.36485e+06", "1.36538e+06", "1.3635e+06", "1.36503e+06",
               "1.36658e+06", "1.36709e+06"]
real = trigger_consistency(13656517.0, [float(t) for t in REAL_TOKENS],
                           REAL_TOKENS)
check("the real integrated CHARM row is short by 17",
      round(real["difference"]) == -17, str(real["difference"]))
check("its rounding bound is 140, so 17 is inside it",
      real["rounding_bound"] == 140.0, str(real["rounding_bound"]))
check("it agrees at the recorded precision but NOT exactly",
      real["agrees"] is True and real["agrees_exactly"] is False, str(real))

# A shortfall past the bound is still a real failure.
check("a difference past the rounding bound still fails",
      trigger_consistency(13656517.0 + 200, [float(t) for t in REAL_TOKENS],
                          REAL_TOKENS)["agrees"] is False)

check("triggers per event divides", triggers_per_event(5.0, 2.0) == 2.5)
try:
    triggers_per_event(5.0, 0)
    check("a zero exposure is refused", False, "no exception")
except ValueError:
    check("a zero exposure is refused", True)

# --- the standing check ---------------------------------------------------
rows = {
    "A": {("k",): {"central_yield": "0.5"}},
    "B": {("k",): {"central_yield": "0.5"}},
    "C": {("k",): {"central_yield": "0.6"}},
}
check("two campaigns agreeing exactly are named as a pair",
      identical_row_sets(rows) == [("A", "B")], str(identical_row_sets(rows)))
check("a campaign that differs is not named",
      identical_row_sets({"A": rows["A"], "C": rows["C"]}) == [])

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'ALL CHECKS PASS'}")
sys.exit(1 if failures else 0)
