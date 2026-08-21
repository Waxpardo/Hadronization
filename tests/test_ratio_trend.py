#!/usr/bin/env python3
"""The trend arithmetic, on hand-computed anchors.

The fit anchors use the three points (1,1), (2,2), (3,3), which lie exactly on
y = x. With unit sigmas the weighted least-squares algebra is small enough to do
by hand:

    w = 1,  S = 3,  Sx = 6,  Sxx = 14
    D = S*Sxx - Sx^2 = 3*14 - 36 = 6
    slope     = 1,   slope_sem     = sqrt(S/D)   = sqrt(3/6)  = sqrt(0.5)
    intercept = 0,   intercept_sem = sqrt(Sxx/D) = sqrt(14/6)
    chi-square = 0 on ndf = 1

Halving every sigma quadruples every weight, which leaves D scaled by 16 and S
by 4, so each standard error halves. That is asserted rather than assumed.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extraction"))

from ratio_trend import (contrast, slope_difference,  # noqa: E402
                         weighted_linear_fit)

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


# --- the fit --------------------------------------------------------------
fit = weighted_linear_fit([1, 2, 3], [1, 2, 3], [1, 1, 1])
check("a perfect line gives slope 1", fit["slope"] == 1.0, "%.17g" % fit["slope"])
check("and intercept 0", fit["intercept"] == 0.0, "%.17g" % fit["intercept"])
check("its slope error is sqrt(1/2)",
      fit["slope_sem"] == math.sqrt(0.5), "%.17g" % fit["slope_sem"])
check("its intercept error is sqrt(14/6)",
      fit["intercept_sem"] == math.sqrt(14.0 / 6.0),
      "%.17g" % fit["intercept_sem"])
check("a perfect line has chi-square 0 on ndf 1",
      fit["chi_square"] == 0.0 and fit["ndf"] == 1, str(fit))

half = weighted_linear_fit([1, 2, 3], [1, 2, 3], [0.5, 0.5, 0.5])
check("halving every sigma halves the slope error",
      abs(half["slope_sem"] - fit["slope_sem"] / 2) < 1e-15,
      "%.17g" % half["slope_sem"])
check("and leaves the slope itself alone", half["slope"] == fit["slope"])

# A point off the line makes the chi-square say so. Points (1,1),(2,2),(3,4)
# with unit sigmas: the fitted slope is 1.5, intercept -2/3, and the residuals
# are +1/6, -1/3, +1/6, so chi-square = 1/36 + 1/9 + 1/36 = 1/6.
off = weighted_linear_fit([1, 2, 3], [1, 2, 4], [1, 1, 1])
check("a point off the line gives slope 1.5",
      abs(off["slope"] - 1.5) < 1e-15, "%.17g" % off["slope"])
check("and a chi-square of 1/6",
      abs(off["chi_square"] - 1.0 / 6.0) < 1e-15, "%.17g" % off["chi_square"])
check("chi-square per ndf is reported",
      abs(off["chi_square_per_ndf"] - 1.0 / 6.0) < 1e-15,
      str(off["chi_square_per_ndf"]))

# A steeply weighted point pulls the line towards itself, and the limit is
# exact. As sigma_3 -> 0 the line is forced through (3, 4), so a = 4 - 3b, and
# minimising (1 - a - b)^2 + (2 - a - 2b)^2 = 5b^2 - 16b + 13 gives b = 1.6.
weighted = weighted_linear_fit([1, 2, 3], [1, 2, 4], [1, 1, 0.01])
check("a tightly measured point pulls the slope from 1.5 towards 1.6",
      1.5 < weighted["slope"] < 1.6, "%.17g" % weighted["slope"])
check("and with sigma 0.01 it is within 1e-4 of the limit",
      abs(weighted["slope"] - 1.6) < 1e-4, "%.17g" % weighted["slope"])
tighter = weighted_linear_fit([1, 2, 3], [1, 2, 4], [1, 1, 0.0001])
check("a tighter sigma moves it closer to the 1.6 limit still",
      abs(tighter["slope"] - 1.6) < abs(weighted["slope"] - 1.6),
      "%.17g" % tighter["slope"])

for bad, why in (
        (([1, 2], [1, 2], [1, 1]), "two points leave no degrees of freedom"),
        (([1, 2, 3], [1, 2, 3], [1, 0, 1]), "a zero sigma is not a weight"),
        (([1, 1, 1], [1, 2, 3], [1, 1, 1]), "every x the same is degenerate"),
        (([1, 2, 3], [1, 2], [1, 1, 1]), "mismatched lengths")):
    try:
        weighted_linear_fit(*bad)
        check(f"refused: {why}", False, "no exception")
    except ValueError:
        check(f"refused: {why}", True)

# --- the model-free contrast ---------------------------------------------
# 0.54317 - 0.21408 = 0.32909;  sqrt(0.0059^2 + 0.00873^2) = 0.010535...
c = contrast(0.54317, 0.0059, 0.21408, 0.00873)
check("the endpoint contrast subtracts",
      "%.6g" % c["difference"] == "0.32909", "%.17g" % c["difference"])
check("its SEM is the two SEMs in quadrature",
      abs(c["sem"] - math.sqrt(0.0059 ** 2 + 0.00873 ** 2)) < 1e-18,
      "%.17g" % c["sem"])
check("and the significance divides",
      abs(c["significance"] - c["difference"] / c["sem"]) < 1e-12)

# 3-4-5, so this one is exact.
clean = contrast(5.0, 3.0, 2.0, 4.0)
check("a 3-4-5 contrast gives 3 +/- 5",
      clean["difference"] == 3.0 and clean["sem"] == 5.0, str(clean))
check("a zero SEM with a real difference is infinitely significant",
      contrast(1.0, 0.0, 0.0, 0.0)["significance"] == math.inf)

# --- the slope difference -------------------------------------------------
diff = slope_difference({"slope": 5.0, "slope_sem": 3.0},
                        {"slope": 2.0, "slope_sem": 4.0})
check("the slope difference is also a 3-4-5 contrast",
      diff["difference"] == 3.0 and diff["sem"] == 5.0, str(diff))
check("a tune with no trend against one with a trend is resolved",
      slope_difference({"slope": 0.04, "slope_sem": 0.001},
                       {"slope": 0.0, "slope_sem": 0.001}
                       )["significance"] > 2.0)

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'ALL CHECKS PASS'}")
sys.exit(1 if failures else 0)
