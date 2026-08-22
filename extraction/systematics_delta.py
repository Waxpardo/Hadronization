#!/usr/bin/env python3
"""Per-class systematics deltas and their combination — the pure arithmetic.

Separated from any I/O so it can be tested against hand-computed anchors, which
is the only way to check a statistical estimator: comparing a tool against
itself proves agreement, not correctness (ERROR_RECORD E1).

THE REGISTERED ESTIMATOR is docs/SYSTEMATICS_PREREGISTRATION.md 2.2:

    Delta_v(c) = [ Y_v(c) - Y_nom(c) ] / Y_nom(c)

formed INSIDE each block, averaged over the ten blocks, SEM over those ten
values, dof 9, reported in PER CENT. Forming the ratio inside the block before
averaging is the project's standing rule for nonlinear quantities.

The variation and the nominal are independent generations, so block k of one is
not the same events as block k of the other; the pairing is by block INDEX and
the pre-registration says so explicitly. Pairing by index does not reduce the
variance -- it is a labelling, not a match -- and the SEM over the ten paired
values is still the SEM of a difference of two independent means.

A SECOND FORM is provided, `delta_from_means`, which is what a caller would
reach for if it only had the sealed table's mean and SEM rather than the
nominal's ten blocks: Delta = (mean_v - mean_n)/mean_n with the SEMs added in
quadrature. It is a CROSS-CHECK, not the registered estimator. Both are
computed and reported so the two can be compared; where they disagree the
registered one governs.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass


# --------------------------------------------------------------------------
# Block statistics
# --------------------------------------------------------------------------

def block_stats(values: list[float]) -> tuple[float, float, int]:
    """(mean, SEM, n) over blocks. Sample stdev, so dof = n - 1.

    Ten blocks give dof 9, which is what every SEM in this project quotes.
    """
    n = len(values)
    if n < 2:
        raise ValueError(f"need at least two blocks for a SEM, got {n}")
    mean = statistics.fmean(values)
    sem = statistics.stdev(values) / math.sqrt(n)
    return mean, sem, n


# --------------------------------------------------------------------------
# Deltas
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Delta:
    """One per-class, per-tune, per-source delta, in per cent."""
    value: float          # per cent
    sem: float            # per cent
    n_blocks: int
    estimator: str

    def resolved(self, k: float = 2.0) -> bool:
        """Is the delta distinguishable from zero at k SEM?"""
        return abs(self.value) >= k * self.sem

    def significance(self) -> float:
        return abs(self.value) / self.sem if self.sem > 0 else math.inf


def delta_per_block(variation_blocks: list[float],
                    nominal_blocks: list[float]) -> Delta:
    """THE REGISTERED ESTIMATOR (pre-registration 2.2).

    Relative shift formed inside each block, then averaged. Per cent.
    """
    if len(variation_blocks) != len(nominal_blocks):
        raise ValueError(
            "block counts differ: %d vs %d -- the pairing is by block index, "
            "so the two arms must have the same number of blocks"
            % (len(variation_blocks), len(nominal_blocks))
        )
    per_block = []
    for k, (v, n) in enumerate(zip(variation_blocks, nominal_blocks)):
        if n == 0:
            raise ZeroDivisionError(
                f"nominal block {k} is zero; a relative shift is undefined. "
                "This is a LOW-STAT class, not a number to be patched."
            )
        per_block.append(100.0 * (v - n) / n)
    mean, sem, count = block_stats(per_block)
    return Delta(mean, sem, count, "per_block_relative")


def delta_from_means(variation_blocks: list[float],
                     nominal_mean: float,
                     nominal_sem: float) -> Delta:
    """CROSS-CHECK form: means first, SEMs in quadrature. Per cent.

    Used when the nominal is available only as the sealed table's mean and SEM.
    Not the registered estimator; reported beside it.
    """
    if nominal_mean == 0:
        raise ZeroDivisionError("nominal mean is zero; relative shift undefined")
    mean_v, sem_v, n = block_stats(variation_blocks)
    value = 100.0 * (mean_v - nominal_mean) / nominal_mean
    # Relative-error propagation on a ratio of two independent measurements.
    rel_v = sem_v / abs(nominal_mean)
    rel_n = abs(mean_v) * nominal_sem / (nominal_mean ** 2)
    sem = 100.0 * math.sqrt(rel_v ** 2 + rel_n ** 2)
    return Delta(value, sem, n, "from_means_quadrature")


# --------------------------------------------------------------------------
# Arm selection (pre-registration 2.5)
# --------------------------------------------------------------------------

def larger_arm(up: Delta, down: Delta) -> tuple[Delta, Delta]:
    """(quoted, cross_check) — the arm with the larger |Delta|, per class.

    NOT half the spread, and NOT an envelope: the pre-registration forbids both
    words and both operations. Half-spread understates a one-sided response;
    "envelope" would claim the pair bounds the space of scale choices, and a
    7- or 9-point variation reaches further.
    """
    return (up, down) if abs(up.value) >= abs(down.value) else (down, up)


# --------------------------------------------------------------------------
# Combination (pre-registration 9)
# --------------------------------------------------------------------------

class CombinationPolicyRequired(Exception):
    """Reject a combination whose caller did not select a registered policy."""


# Each source contributes max(|D|, SEM(D)) without a threshold discontinuity.
UNRESOLVED_MAX_ABS_OR_SEM = "max_abs_or_sem"
# The three options the gap generated, kept so the superseded alternatives stay
# nameable and testable rather than becoming folklore. NOT the ruled policy.
UNRESOLVED_SUPERSEDED = ("as_is", "zero", "sem")

# S6 uses the M1..M5 partition and cannot enter c1..c11 totals.
# Named terms make that exclusion resistant to a caller's spelling error.
S6_TERM_NAMES = frozenset({"S6", "S6_a2", "A2", "S6_unresolved_origin"})


def contribution_of(d: Delta, unresolved_policy: str) -> float:
    """The signed-magnitude a single term contributes before squaring.

    Ruling A1 is deliberately CONTINUOUS: max(|D|, SEM) has no branch on
    resolution, so the quoted systematic cannot jump as a delta drifts across
    2 sigma. The `resolved()` flag is presentational and is not consulted here.
    """
    if unresolved_policy == UNRESOLVED_MAX_ABS_OR_SEM:
        return max(abs(d.value), d.sem)
    # Superseded policies, retained for comparison and for the record.
    if unresolved_policy == "as_is":
        return abs(d.value)
    if d.resolved():
        return abs(d.value)
    if unresolved_policy == "zero":
        return 0.0
    if unresolved_policy == "sem":
        return d.sem
    raise CombinationPolicyRequired(f"unknown policy {unresolved_policy!r}")


def combine_quadrature(terms: dict[str, Delta],
                       *,
                       unresolved_policy: str,
                       s6_policy: str,
                       drop: frozenset[str] = frozenset()) -> float:
    """Quadrature sum over sources, per class per tune. Per cent.

    `unresolved_policy` — use UNRESOLVED_MAX_ABS_OR_SEM (ruling A1). The three
    superseded options remain callable so they can be compared, but they are not
    the registered rule.

    `s6_policy` must be "separate" (ruling A2): S6/A2 lives on the M1..M5
    partition and is NEVER summed into a c1..c11 total. Passing a term whose
    name is in S6_TERM_NAMES is refused, because summing across incompatible
    partitions is the specific thing the ruling forbids.

    `drop` names sources excluded by a registered rule -- section 9.1 (mu_F vs
    PDF, quote the larger and drop the other).
    """
    if unresolved_policy not in (UNRESOLVED_MAX_ABS_OR_SEM,) + UNRESOLVED_SUPERSEDED:
        raise CombinationPolicyRequired(
            f"unresolved_policy must be {UNRESOLVED_MAX_ABS_OR_SEM!r} (ruled) or "
            f"one of the superseded {UNRESOLVED_SUPERSEDED}, got "
            f"{unresolved_policy!r}"
        )
    if s6_policy != "separate":
        raise CombinationPolicyRequired(
            "s6_policy must be 'separate' -- pre-registration 9.6 stands "
            "(AMENDMENT A2). A2 is on the M1..M5 partition and is not "
            "summed into per-class c1..c11 totals."
        )
    offenders = S6_TERM_NAMES & set(terms) - drop
    if offenders:
        raise CombinationPolicyRequired(
            "refusing to sum across incompatible partitions: "
            + ", ".join(sorted(offenders))
            + " is on the M1..M5 axis. Quote it as a separate line."
        )
    total = 0.0
    for name, d in sorted(terms.items()):
        if name in drop:
            continue
        total += contribution_of(d, unresolved_policy) ** 2
    return math.sqrt(total)


def correlated_pair_choice(muf: Delta, pdf: Delta,
                           negligible_pct: float = 0.1) -> frozenset[str]:
    """Section 9.1: mu_F and PDF act on the same object (the parton flux).

    If BOTH are non-negligible, quote the larger and drop the other. If one is
    negligible the other enters alone and the question does not arise.
    Returns the set of names to drop.
    """
    muf_big = abs(muf.value) >= negligible_pct
    pdf_big = abs(pdf.value) >= negligible_pct
    if muf_big and pdf_big:
        return frozenset({"S2_pdf"} if abs(muf.value) >= abs(pdf.value)
                         else {"S1b_muf"})
    return frozenset()
