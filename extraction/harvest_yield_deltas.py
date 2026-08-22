#!/usr/bin/env python3
"""Per-class and integrated deltas on the plotter's balancing yields.

THE QUANTITY. Each `UNCERTAINTY_MATRIX` row carries `central_yield`, the OS-SS
balancing yield per trigger, and `yield_sem`, its standard error over the ten
subsample blocks. The row's identity is the five fields GOLDEN_OUTPUTS 9.9.1
requires, with the multiplicity class parsed out of the bin name by
`harvest_class_axis` (run record 18.2).

THE REGISTERED ESTIMATOR:

    Delta      = variation - nominal                       (absolute)
    SEM(Delta) = sqrt(SEM_variation^2 + SEM_nominal^2)     (independent arms)
    flagged    when |Delta| < 2 * SEM(Delta)

IT IS ABSOLUTE, NOT RELATIVE, and that is deliberate. The per-category work
(`systematics_delta`) forms a relative shift inside each block, which needs the
nominal to be non-zero and needs the blocks themselves. The log gives a mean and
a SEM per row and no block yields, and some classes hold a nominal that cannot
carry a division. An absolute difference is defined everywhere the rows are.

The relative shift is reported BESIDE it where the nominal permits one, and the
cell is NAMED rather than filled where it does not.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest_class_axis import significant_figures

K_SIGMA = 2.0


def yield_delta(variation_yield: float, variation_sem: float,
                nominal_yield: float, nominal_sem: float) -> tuple[float, float]:
    """(Delta, SEM(Delta)). Absolute, SEMs in quadrature."""
    if variation_sem < 0 or nominal_sem < 0:
        raise ValueError("a SEM cannot be negative")
    return (variation_yield - nominal_yield,
            math.sqrt(variation_sem ** 2 + nominal_sem ** 2))


def is_unresolved(delta: float, sem: float, k: float = K_SIGMA) -> bool:
    """|Delta| < k * SEM(Delta). A zero SEM makes any non-zero Delta resolved."""
    return abs(delta) < k * sem


def significance(delta: float, sem: float) -> float:
    """|Delta| / SEM(Delta). Infinite when the SEM is zero and Delta is not."""
    if sem == 0:
        return math.inf if delta != 0 else 0.0
    return abs(delta) / sem


def relative_shift(delta: float, nominal_yield: float) -> float | None:
    """Per cent of the nominal, or None when the nominal cannot carry one.

    None is a RESULT, not a failure. A class whose nominal yield is zero has no
    scale to express a shift against, and the record names the cell instead of
    quoting a number for it.
    """
    if nominal_yield == 0:
        return None
    return 100.0 * delta / nominal_yield


def printed_half_ulp(token: str) -> float:
    """Half the last recorded place of a printed number.

    THE LOG ROUNDS, AND THE CHECK HAS TO KNOW IT. A per-class trigger count
    prints as `161365` and is exact. The integrated bin's counts are larger and
    print in scientific notation at six significant figures, so `1.3646e+06` is
    a count somewhere in a window one hundred wide. Ten of those summed cannot
    reproduce an exact total, and demanding they do would report arithmetic that
    is not wrong.
    """
    value = abs(float(token))
    digits = significant_figures(token)
    if value == 0:
        return 0.5
    exponent = math.floor(math.log10(value))
    return 0.5 * 10.0 ** (exponent - digits + 1)


def trigger_consistency(central_triggers: float,
                        block_triggers: list[float],
                        block_tokens: list[str] | None = None) -> dict:
    """Do the ten block trigger counts account for the central count?

    The blocks partition the sample, so they must sum to the central count, TO
    THE PRECISION THE LOG PRINTS. Pass `block_tokens` -- the strings as written
    -- to get the rounding bound; without them the comparison is exact.
    """
    total = sum(block_triggers)
    difference = total - central_triggers
    bound = (sum(printed_half_ulp(t) for t in block_tokens)
             if block_tokens else 0.0)
    return {
        "central_triggers": central_triggers,
        "block_trigger_sum": total,
        "n_blocks": len(block_triggers),
        "difference": difference,
        "rounding_bound": bound,
        "agrees": abs(difference) <= bound,
        "agrees_exactly": total == central_triggers,
    }


def triggers_per_event(total_triggers: float, events: float) -> float:
    """The E5 plausibility ratio. The defect signature was ~13 where truth is O(1)."""
    if events <= 0:
        raise ValueError("event exposure must be positive")
    return total_triggers / events


def identical_row_sets(rows_by_campaign: dict[str, dict]) -> list[tuple[str, str]]:
    """Campaign pairs whose rows agree EXACTLY on every yield.

    THE STANDING CHECK. Two physically distinct variations that agree exactly
    are a plumbing failure until proven otherwise: it is what five renders
    reading the central campaign looked like on 2026-08-19.
    """
    names = sorted(rows_by_campaign)
    same = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ra, rb = rows_by_campaign[a], rows_by_campaign[b]
            if ra.keys() != rb.keys():
                continue
            if all(ra[k]["central_yield"] == rb[k]["central_yield"] for k in ra):
                same.append((a, b))
    return same
