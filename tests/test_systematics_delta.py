#!/usr/bin/env python3
"""Contract tests for extraction/systematics_delta.py.

Every expected value below is HAND-COMPUTED and written out longhand in the
docstring or comment beside it. Comparing a tool against its own output proves
agreement, not correctness (E1), so nothing here is a golden value captured
from a previous run.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extraction"))

from systematics_delta import (  # noqa: E402
    CombinationPolicyRequired,
    Delta,
    S6_TERM_NAMES,
    UNRESOLVED_MAX_ABS_OR_SEM,
    block_stats,
    combine_quadrature,
    contribution_of,
    correlated_pair_choice,
    delta_from_means,
    delta_per_block,
    larger_arm,
)

RULED = dict(unresolved_policy=UNRESOLVED_MAX_ABS_OR_SEM, s6_policy="separate")

TOL = 1e-12


def close(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def test_block_stats_against_longhand() -> None:
    """values 1..10.

    mean = 55/10 = 5.5
    sample variance = sum((x-5.5)^2)/9 = 82.5/9 = 9.1666...
    stdev = sqrt(9.1666...) = 3.0276503540974917
    SEM = stdev/sqrt(10) = 0.9574271077563381
    """
    mean, sem, n = block_stats([float(x) for x in range(1, 11)])
    assert n == 10, n
    assert close(mean, 5.5), mean
    assert close(sem, 3.0276503540974917 / math.sqrt(10)), sem
    assert close(sem, 0.9574271077563381), sem


def test_block_stats_refuses_a_single_block() -> None:
    """dof 0 has no SEM; the tool must refuse rather than return 0."""
    try:
        block_stats([1.0])
    except ValueError:
        return
    raise AssertionError("a single block must not yield a SEM")


def test_delta_per_block_is_the_registered_estimator() -> None:
    """Ratio INSIDE each block, then averaged -- not means-first.

    variation = [11, 12, 13, 14], nominal = [10, 10, 10, 10]
    per-block relative shift, per cent:
        (11-10)/10 = 10 %, (12-10)/10 = 20 %, 30 %, 40 %
    mean = 25 %
    sample stdev of [10,20,30,40] = sqrt(((15^2)+(5^2)+(5^2)+(15^2))/3)
                                  = sqrt(500/3) = 12.909944487358056
    SEM = 12.909944487358056/sqrt(4) = 6.454972243679028
    """
    d = delta_per_block([11.0, 12.0, 13.0, 14.0], [10.0, 10.0, 10.0, 10.0])
    assert d.estimator == "per_block_relative"
    assert close(d.value, 25.0), d.value
    assert close(d.sem, 6.454972243679028), d.sem
    assert d.n_blocks == 4


def test_per_block_differs_from_means_first_when_nominal_varies() -> None:
    """The two estimators are not the same operation, and this proves it.

    variation = [10, 20], nominal = [10, 40]
    inside-block:   (10-10)/10 = 0 %, (20-40)/40 = -50 %  -> mean -25 %
    means-first:    (15 - 25)/25 = -40 %
    -25 != -40, so forming the ratio inside the block is a real choice, which
    is why the pre-registration names it.
    """
    inside = delta_per_block([10.0, 20.0], [10.0, 40.0])
    assert close(inside.value, -25.0), inside.value
    mean_n, sem_n, _ = block_stats([10.0, 40.0])
    outside = delta_from_means([10.0, 20.0], mean_n, sem_n)
    assert close(outside.value, -40.0), outside.value
    assert not close(inside.value, outside.value)


def test_delta_per_block_refuses_mismatched_block_counts() -> None:
    try:
        delta_per_block([1.0, 2.0, 3.0], [1.0, 2.0])
    except ValueError:
        return
    raise AssertionError("mismatched block counts must be refused")


def test_delta_per_block_refuses_a_zero_nominal_block() -> None:
    """A relative shift on a zero nominal is undefined, not infinite."""
    try:
        delta_per_block([1.0, 2.0], [0.0, 2.0])
    except ZeroDivisionError:
        return
    raise AssertionError("a zero nominal block must be refused")


def test_delta_from_means_propagation_longhand() -> None:
    """variation blocks [9, 11] -> mean 10, stdev sqrt(2), SEM sqrt(2)/sqrt(2)=1
    nominal mean 20, nominal SEM 2.

    value = 100*(10-20)/20 = -50 %
    rel_v = SEM_v/|mean_n|      = 1/20   = 0.05
    rel_n = |mean_v|*SEM_n/mean_n^2 = 10*2/400 = 0.05
    sem   = 100*sqrt(0.05^2 + 0.05^2) = 100*0.0707106781186547 = 7.07106781186547
    """
    d = delta_from_means([9.0, 11.0], 20.0, 2.0)
    assert close(d.value, -50.0), d.value
    assert close(d.sem, 100.0 * math.sqrt(0.05 ** 2 + 0.05 ** 2)), d.sem
    assert close(d.sem, 7.0710678118654755), d.sem


def test_resolved_boundary_is_exactly_two_sem() -> None:
    """|D| = 2*SEM counts as resolved; strictly below does not."""
    assert Delta(2.0, 1.0, 10, "x").resolved()
    assert not Delta(1.999, 1.0, 10, "x").resolved()
    assert Delta(-2.0, 1.0, 10, "x").resolved()


def test_larger_arm_picks_by_absolute_value_not_sign() -> None:
    up = Delta(1.0, 0.1, 10, "x")
    down = Delta(-3.0, 0.1, 10, "x")
    quoted, cross = larger_arm(up, down)
    assert quoted is down and cross is up
    # ties go to the up arm, deterministically
    a, b = Delta(2.0, 0.1, 10, "x"), Delta(-2.0, 0.1, 10, "x")
    q, _ = larger_arm(a, b)
    assert q is a


def test_combination_refuses_without_an_explicit_policy() -> None:
    """Ruled on 2026-08-18, but still required rather than defaulted: a caller
    must name the policy so a future change is visible at the call site."""
    terms = {"S1a": Delta(1.0, 0.1, 10, "x")}
    for bad in ("", "default", None):
        try:
            combine_quadrature(terms, unresolved_policy=bad,  # type: ignore[arg-type]
                               s6_policy="separate")
        except CombinationPolicyRequired:
            continue
        raise AssertionError(f"policy {bad!r} must be refused")
    try:
        combine_quadrature(terms, unresolved_policy=UNRESOLVED_MAX_ABS_OR_SEM,
                           s6_policy="quadrature")
    except CombinationPolicyRequired:
        return
    raise AssertionError("s6_policy other than 'separate' must be refused")


# ---- OWNER AMENDMENT A1: contribution is max(|D|, SEM), continuous ----------

def test_ruling_a1_contribution_is_max_abs_or_sem() -> None:
    """resolved 3.0 +- 0.1 -> max(3.0, 0.1) = 3.0
       unresolved 1.0 +- 2.0 -> max(1.0, 2.0) = 2.0   (the SEM floor binds)
       zero-valued 0.0 +- 0.5 -> max(0.0, 0.5) = 0.5
    """
    assert close(contribution_of(Delta(3.0, 0.1, 10, "x"), UNRESOLVED_MAX_ABS_OR_SEM), 3.0)
    assert close(contribution_of(Delta(1.0, 2.0, 10, "x"), UNRESOLVED_MAX_ABS_OR_SEM), 2.0)
    assert close(contribution_of(Delta(0.0, 0.5, 10, "x"), UNRESOLVED_MAX_ABS_OR_SEM), 0.5)
    # sign is irrelevant: the magnitude is what is squared
    assert close(contribution_of(Delta(-3.0, 0.1, 10, "x"), UNRESOLVED_MAX_ABS_OR_SEM), 3.0)


def test_ruling_a1_the_worked_example_from_the_brief() -> None:
    """resolved 3.0 +- 0.1 and unresolved 1.0 +- 2.0.

    contributions: max(3.0, 0.1) = 3.0 ; max(1.0, 2.0) = 2.0
    total = sqrt(3^2 + 2^2) = sqrt(13) = 3.605551275463989
    """
    terms = {"res": Delta(3.0, 0.1, 10, "x"), "unres": Delta(1.0, 2.0, 10, "x")}
    assert close(combine_quadrature(terms, **RULED), math.sqrt(13.0))
    assert close(combine_quadrature(terms, **RULED), 3.605551275463989)


def test_ruling_a1_is_continuous_across_the_two_sigma_boundary() -> None:
    """The point of max(|D|, SEM): no cliff.

    Hold SEM = 1.0 and walk |D| through 2.0. Contribution is 1.0 while |D| < 1,
    then |D| once |D| > 1 -- and nothing special happens at |D| = 2 (the 2-sigma
    flag), which is exactly what a threshold rule would have made discontinuous.
    """
    sem = 1.0
    prev = None
    for tenths in range(0, 41):
        d = Delta(tenths / 10.0, sem, 10, "x")
        c = contribution_of(d, UNRESOLVED_MAX_ABS_OR_SEM)
        assert close(c, max(tenths / 10.0, sem))
        if prev is not None:
            assert c - prev <= 0.1 + 1e-12, (tenths, prev, c)
        prev = c
    # explicit: no jump straddling |D| = 2*SEM
    below = contribution_of(Delta(1.999, sem, 10, "x"), UNRESOLVED_MAX_ABS_OR_SEM)
    above = contribution_of(Delta(2.001, sem, 10, "x"), UNRESOLVED_MAX_ABS_OR_SEM)
    assert abs(above - below) < 0.01, (below, above)


def test_ruling_a1_never_zeroes_and_never_claims_below_resolution() -> None:
    """The two halves of the recorded rationale, as assertions."""
    # a potentially real shift is never zeroed
    assert contribution_of(Delta(0.9, 1.0, 10, "x"), UNRESOLVED_MAX_ABS_OR_SEM) > 0.0
    # a systematic is never claimed below the resolution of the measurement
    d = Delta(0.2, 1.5, 10, "x")
    assert contribution_of(d, UNRESOLVED_MAX_ABS_OR_SEM) >= d.sem


# ---- OWNER AMENDMENT A2: S6 is never summed across partitions --------------

def test_ruling_a2_refuses_an_s6_term_in_the_per_class_sum() -> None:
    """Summing across the M1..M5 and c1..c11 partitions is the specific thing
    the ruling forbids, so it is refused rather than silently included."""
    for name in sorted(S6_TERM_NAMES):
        terms = {"S1a": Delta(3.0, 0.1, 10, "x"), name: Delta(0.15, 0.02, 10, "x")}
        try:
            combine_quadrature(terms, **RULED)
        except CombinationPolicyRequired:
            continue
        raise AssertionError(f"an S6 term named {name!r} must be refused")


def test_ruling_a2_an_s6_term_may_be_explicitly_dropped() -> None:
    """Dropping is how a caller says 'I know, it is quoted separately'."""
    terms = {"S1a": Delta(3.0, 0.1, 10, "x"), "S6": Delta(0.15, 0.02, 10, "x")}
    got = combine_quadrature(terms, **RULED, drop=frozenset({"S6"}))
    assert close(got, 3.0), got


def test_combination_quadrature_longhand() -> None:
    """Three resolved terms 3, 4, 12 -> sqrt(9+16+144) = sqrt(169) = 13.

    All three have SEM 0.1, so the ruled max(|D|, SEM) picks |D| for each and
    the answer is the same as a plain quadrature sum.
    """
    terms = {
        "a": Delta(3.0, 0.1, 10, "x"),
        "b": Delta(4.0, 0.1, 10, "x"),
        "c": Delta(12.0, 0.1, 10, "x"),
    }
    assert close(combine_quadrature(terms, **RULED), 13.0)


def test_the_superseded_policies_remain_nameable_and_distinct() -> None:
    """The three options the gap generated, kept testable so the superseded
    alternatives stay nameable rather than becoming folklore.

    resolved term 3.0 +- 0.1 ; unresolved term 1.0 +- 2.0 (|D| = 0.5 SEM)
      as_is : sqrt(3^2 + 1^2)   = sqrt(10) = 3.1622776601683795
      zero  : sqrt(3^2 + 0)     = 3.0
      sem   : sqrt(3^2 + 2^2)   = sqrt(13) = 3.605551275463989
    RULED  : max(3,0.1)=3, max(1,2)=2 -> sqrt(13), which coincides with "sem"
             HERE only because |D| < SEM for the unresolved term; the two rules
             differ whenever |D| > SEM but |D| < 2*SEM.
    """
    terms = {"res": Delta(3.0, 0.1, 10, "x"), "unres": Delta(1.0, 2.0, 10, "x")}
    sep = dict(s6_policy="separate")
    assert close(combine_quadrature(terms, unresolved_policy="as_is", **sep), math.sqrt(10.0))
    assert close(combine_quadrature(terms, unresolved_policy="zero", **sep), 3.0)
    assert close(combine_quadrature(terms, unresolved_policy="sem", **sep), math.sqrt(13.0))
    # where the ruled rule genuinely differs from "sem": |D| between SEM and 2*SEM
    mixed = {"res": Delta(3.0, 0.1, 10, "x"), "unres": Delta(1.5, 1.0, 10, "x")}
    assert close(combine_quadrature(mixed, unresolved_policy="sem", **sep), math.sqrt(10.0))
    assert close(combine_quadrature(mixed, **RULED), math.sqrt(3.0 ** 2 + 1.5 ** 2))


def test_drop_excludes_a_source_from_the_sum() -> None:
    terms = {"a": Delta(3.0, 0.1, 10, "x"), "b": Delta(4.0, 0.1, 10, "x")}
    got = combine_quadrature(terms, **RULED, drop=frozenset({"b"}))
    assert close(got, 3.0), got


def test_correlated_pair_drops_the_smaller_only_when_both_are_big() -> None:
    """Section 9.1: mu_F and PDF act on the same object.

    both big   -> drop the smaller of the two
    one small  -> drop nothing, the other enters alone
    """
    big_muf = Delta(0.5, 0.01, 10, "x")
    big_pdf = Delta(0.3, 0.01, 10, "x")
    assert correlated_pair_choice(big_muf, big_pdf) == frozenset({"S2_pdf"})
    assert correlated_pair_choice(big_pdf, big_muf) == frozenset({"S1b_muf"})
    small = Delta(0.01, 0.01, 10, "x")
    assert correlated_pair_choice(big_muf, small) == frozenset()
    assert correlated_pair_choice(small, small) == frozenset()


def main() -> int:
    failures = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
        except Exception as error:  # noqa: BLE001
            failures += 1
            print(f"FAIL {name}: {error}")
        else:
            print(f"ok   {name}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
