"""The multiplicity trend of a per-class ratio, and the contrast between tunes.

WHY THIS EXISTS SEPARATELY FROM THE PER-CLASS GAPS. `write_tune_separation.py`
answers "do the tunes differ in class c?". The paper's claim is stronger and
different: **the ratio RISES with multiplicity under colour reconnection and
does not under MONASH**. That is a statement about the slope, not about any one
class, and a set of per-class gaps does not establish it.

TWO ESTIMATORS, AND THE MODEL-FREE ONE LEADS.

  the endpoint contrast   R(c11) - R(c1), per tune. No model, no fit, no choice
                          of x-axis. A referee recomputes it from two rows.
  the weighted slope      a straight line in the class INDEX, weighted by the
                          per-class SEM, with chi-square per degree of freedom
                          so the line can be seen to fail.

THE X-AXIS IS THE CLASS INDEX, AND THAT IS A CONVENTION, NOT A MEASUREMENT. The
classes are not equally spaced in N_ch, and every tune resolves its own N_ch
edges, so the spacing also differs between tunes. A slope "per class" is
therefore a summary of a monotone trend, not a
physical d(ratio)/dN_ch. The endpoint contrast is the number that carries no
such convention, which is why it is quoted first.

CORRELATION, STATED RATHER THAN ASSUMED. Within one tune the classes are
disjoint sets of events, so treating them as independent is right to the extent
that the ten-block resampling does not correlate them. If it does correlate
them positively, then Var(A - B) = Var(A) + Var(B) - 2Cov is SMALLER than the
quadrature sum, so every uncertainty quoted here is conservative in that
direction.
"""

from __future__ import annotations

import math


def contrast(value_a: float, sem_a: float,
             value_b: float, sem_b: float) -> dict:
    """value_a - value_b with SEMs in quadrature. The model-free trend number."""
    difference = value_a - value_b
    sem = math.sqrt(sem_a ** 2 + sem_b ** 2)
    return {
        "difference": difference,
        "sem": sem,
        "significance": abs(difference) / sem if sem else math.inf,
    }


def weighted_linear_fit(xs, ys, sigmas) -> dict:
    """Weighted least squares, y = intercept + slope * x, with w = 1/sigma^2.

    Returns the slope and intercept with their standard errors, the chi-square
    and the degrees of freedom. The chi-square is reported so a trend that is
    not a straight line says so instead of being summarised by a slope.
    """
    n = len(xs)
    if not (n == len(ys) == len(sigmas)):
        raise ValueError("xs, ys and sigmas must be the same length")
    if n < 3:
        raise ValueError(f"need at least three points for a fit with a chi-square, got {n}")
    if any(s <= 0 for s in sigmas):
        raise ValueError("every sigma must be positive")

    weights = [1.0 / s ** 2 for s in sigmas]
    s_w = sum(weights)
    s_x = sum(w * x for w, x in zip(weights, xs))
    s_y = sum(w * y for w, y in zip(weights, ys))
    s_xx = sum(w * x * x for w, x in zip(weights, xs))
    s_xy = sum(w * x * y for w, x, y in zip(weights, xs, ys))

    denominator = s_w * s_xx - s_x ** 2
    if denominator == 0:
        raise ValueError("degenerate fit: every x is the same")

    slope = (s_w * s_xy - s_x * s_y) / denominator
    intercept = (s_xx * s_y - s_x * s_xy) / denominator
    chi_square = sum(w * (y - intercept - slope * x) ** 2
                     for w, x, y in zip(weights, xs, ys))
    ndf = n - 2
    return {
        "slope": slope,
        "slope_sem": math.sqrt(s_w / denominator),
        "intercept": intercept,
        "intercept_sem": math.sqrt(s_xx / denominator),
        "chi_square": chi_square,
        "ndf": ndf,
        "chi_square_per_ndf": chi_square / ndf,
        "n_points": n,
    }


def slope_difference(fit_a: dict, fit_b: dict) -> dict:
    """slope(a) - slope(b), SEMs in quadrature.

    The two tunes are separate generation campaigns with their own raw files and
    their own seeds, so the two slopes are independent.
    """
    return contrast(fit_a["slope"], fit_a["slope_sem"],
                    fit_b["slope"], fit_b["slope_sem"])
