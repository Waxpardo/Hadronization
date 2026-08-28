"""The multiplicity trend of a per-class ratio, and the contrast between tunes.

WHY THIS EXISTS SEPARATELY FROM THE PER-CLASS GAPS. `write_tune_separation.py`
answers "do the bundles differ in class c?". This module instead measures how
the ratio changes with multiplicity inside each complete configuration.
JUNCTIONS and CLOSEPACKING are full configuration bundles, and MONASH is the
reference bundle. Their differences cannot be attributed causally to one
switch; in particular, CLOSEPACKING is not a junction-off control. A trend is
a statement about the slope, not about any one class, and a set of per-class
gaps does not establish it.

TWO ESTIMATORS, AND THE MODEL-FREE ONE LEADS.

  the endpoint contrast   R(c11) - R(c1), per tune. No model, no fit, no choice
                          of x-axis. A referee recomputes it from two rows.
  legacy weighted slope  a straight line in the class INDEX, weighted by the
                         per-class SEM, with chi-square per degree of freedom
                         so the line can be seen to fail.

THE X-AXIS IS THE CLASS INDEX, AND THAT IS A CONVENTION, NOT A MEASUREMENT. The
classes are not equally spaced in N_ch, and every tune resolves its own N_ch
edges, so the spacing also differs between tunes. A slope "per class" is
therefore a summary of a monotone trend, not a
physical d(ratio)/dN_ch. The endpoint contrast is the number that carries no
such convention, which is why it is quoted first.

CORRELATION, STATED RATHER THAN ASSUMED. Within one tune the classes are
aligned by canonical file-block index. Endpoint differences are formed inside
those blocks, so their SEM retains the measured covariance between classes.
The class-index fit below remains a legacy summary until the physical-coordinate,
covariance-aware successor is implemented.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence


def sample_sem(values: Sequence[float]) -> float:
    """Sample SEM over aligned blocks, with n - 1 sample-variance divisor."""
    if len(values) < 2:
        raise ValueError(f"need at least two aligned blocks, got {len(values)}")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("block vector contains a non-finite value")
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values)
                     / (len(values) * (len(values) - 1)))


def independent_difference(value_a: float, sem_a: float,
                           value_b: float, sem_b: float) -> dict:
    """Difference between statistically independent generation campaigns."""
    difference = value_a - value_b
    sem = math.sqrt(sem_a ** 2 + sem_b ** 2)
    return {
        "difference": difference,
        "sem": sem,
        "significance": abs(difference) / sem if sem else math.inf,
        "statistical_method": "independent_campaign_sem_quadrature",
    }


def endpoint_contrast(value_high: float, blocks_high: Sequence[float],
                      value_low: float, blocks_low: Sequence[float]) -> dict:
    """Full-sample endpoint difference with its aligned-block sample SEM."""
    if len(blocks_high) != len(blocks_low):
        raise ValueError(
            "endpoint block vectors must have the same length: "
            f"{len(blocks_high)} != {len(blocks_low)}")
    contrasts = [high - low for high, low in zip(blocks_high, blocks_low)]
    difference = value_high - value_low
    sem = sample_sem(contrasts)
    return {
        "difference": difference,
        "sem": sem,
        "significance": abs(difference) / sem if sem else math.inf,
        "block_contrasts": contrasts,
        "block_count": len(contrasts),
        "statistical_method": "aligned_block_endpoint_sample_sem_v1",
    }


def block_covariance(
    blocks_by_class: Mapping[str, Sequence[float]],
    expected_sems: Mapping[str, float] | None = None,
) -> dict:
    """Covariance of class means from canonically aligned block vectors.

    Cov_mean(i,j) = sum_k[(R_ik-mean_i)(R_jk-mean_j)] / [n(n-1)].
    """
    classes = list(blocks_by_class)
    if not classes:
        raise ValueError("the class-vector covariance needs at least one class")
    lengths = {len(blocks_by_class[cls]) for cls in classes}
    if len(lengths) != 1:
        detail = ", ".join(f"{cls}={len(blocks_by_class[cls])}" for cls in classes)
        raise ValueError(f"class block vectors are mis-sized: {detail}")
    block_count = lengths.pop()
    if block_count < 2:
        raise ValueError(f"need at least two aligned blocks, got {block_count}")
    vectors = {cls: [float(value) for value in blocks_by_class[cls]]
               for cls in classes}
    for cls, values in vectors.items():
        if any(not math.isfinite(value) for value in values):
            raise ValueError(f"{cls} block vector contains a non-finite value")
    means = {cls: sum(vectors[cls]) / block_count for cls in classes}
    covariance = []
    for class_i in classes:
        row = []
        for class_j in classes:
            row.append(sum(
                (value_i - means[class_i]) * (value_j - means[class_j])
                for value_i, value_j in zip(vectors[class_i], vectors[class_j])
            ) / (block_count * (block_count - 1)))
        covariance.append(row)
    block_sems = {cls: sample_sem(vectors[cls]) for cls in classes}
    for index, cls in enumerate(classes):
        if not math.isclose(covariance[index][index], block_sems[cls] ** 2,
                            rel_tol=5e-15, abs_tol=1e-30):
            raise ArithmeticError(
                f"{cls} covariance diagonal disagrees with squared block SEM")
        if expected_sems is not None:
            if cls not in expected_sems:
                raise ValueError(f"{cls} has no declared ratio SEM")
            if not math.isclose(block_sems[cls], expected_sems[cls],
                                rel_tol=5e-15, abs_tol=0.0):
                raise ValueError(
                    f"{cls} block SEM {block_sems[cls]:.17g} disagrees with "
                    f"declared ratio SEM {expected_sems[cls]:.17g}")
    return {
        "classes": classes,
        "block_count": block_count,
        "block_means": means,
        "block_sems": block_sems,
        "covariance_of_means": covariance,
        "formula": "sum((R_ik-mean_i)*(R_jk-mean_j))/(n*(n-1))",
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
    return independent_difference(fit_a["slope"], fit_a["slope_sem"],
                                  fit_b["slope"], fit_b["slope_sem"])
