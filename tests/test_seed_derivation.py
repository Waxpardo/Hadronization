#!/usr/bin/env python3
"""seed_derivation_v2 regressions (B15).

v1 derived seeds from (tune, job, attempt) only, so every campaign at attempt 0
drew the same sequence from SEED_BASE. HF_RUN3_V1 at ordinal 3 tried to draw
the seeds HF_SMOKE had burned; B2's assert_seeds_unused caught it at render.

These tests pin the PROPERTY that fix establishes -- distinct campaigns get
disjoint seed ranges -- rather than a table of literals, so they keep meaning
if the strides are ever retuned.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from campaign import (  # noqa: E402
    ALL_TUNES,
    ATTEMPT_STRIDE,
    CAMPAIGN_STRIDE,
    MAX_ATTEMPTS,
    MAX_CAMPAIGN_ORDINAL,
    PYTHIA_SEED_MAX,
    SEED_BASE,
    SEED_DERIVATION_VERSION,
    TUNE_STRIDE,
    seed_for,
)


def seeds_for_campaign(ordinal: int, jobs: int = 200) -> set[int]:
    return {
        seed_for(tune, job, attempt, campaign_ordinal=ordinal)
        for tune in ALL_TUNES
        for attempt in range(MAX_ATTEMPTS)
        for job in range(jobs)
    }


def test_distinct_campaigns_are_disjoint() -> None:
    """The property v1 lacked: no two campaigns share a seed."""
    ranges = {ordinal: seeds_for_campaign(ordinal) for ordinal in range(6)}
    for left in ranges:
        for right in ranges:
            if left >= right:
                continue
            overlap = ranges[left] & ranges[right]
            assert not overlap, (
                f"campaigns {left} and {right} share {len(overlap)} seeds; "
                f"first few {sorted(overlap)[:5]}"
            )


def test_v1_collision_would_have_been_caught() -> None:
    """Ordinals 1 and 3 must not both start at SEED_BASE, as they did in v1."""
    first_one = seed_for(ALL_TUNES[0], 0, 0, campaign_ordinal=1)
    first_three = seed_for(ALL_TUNES[0], 0, 0, campaign_ordinal=3)
    assert first_one != first_three
    assert first_one == SEED_BASE + 1 * CAMPAIGN_STRIDE
    assert first_three == SEED_BASE + 3 * CAMPAIGN_STRIDE


def test_within_campaign_uniqueness_preserved() -> None:
    """v1's own guarantee still holds inside one campaign."""
    seeds = [
        seed_for(tune, job, attempt, campaign_ordinal=3)
        for tune in ALL_TUNES
        for attempt in range(MAX_ATTEMPTS)
        for job in range(50)
    ]
    assert len(seeds) == len(set(seeds))


def test_campaign_stride_exceeds_tune_span() -> None:
    """A campaign's whole span must fit inside one stride."""
    span = (
        (len(ALL_TUNES) - 1) * TUNE_STRIDE
        + (MAX_ATTEMPTS - 1) * ATTEMPT_STRIDE
        + (ATTEMPT_STRIDE - 1)
    )
    assert span < CAMPAIGN_STRIDE, (
        f"campaign span {span} >= CAMPAIGN_STRIDE {CAMPAIGN_STRIDE}; "
        "campaigns would overlap"
    )


def test_ordinal_cap_fails_closed() -> None:
    """Beyond the cap the seed leaves the PYTHIA domain. Refuse, never truncate."""
    top = seed_for(
        ALL_TUNES[-1], ATTEMPT_STRIDE - 1, MAX_ATTEMPTS - 1,
        campaign_ordinal=MAX_CAMPAIGN_ORDINAL,
    )
    assert top <= PYTHIA_SEED_MAX, f"cap admits an out-of-domain seed {top}"

    for bad in (MAX_CAMPAIGN_ORDINAL + 1, -1):
        try:
            seed_for(ALL_TUNES[0], 0, 0, campaign_ordinal=bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"ordinal {bad} was accepted; must refuse")


def test_campaign_ordinal_is_mandatory() -> None:
    """No default: a defaulted campaign term is how v1's bug would return."""
    try:
        seed_for(ALL_TUNES[0], 0, 0)  # type: ignore[call-arg]
    except TypeError:
        pass
    else:
        raise AssertionError("campaign_ordinal must be required, not defaulted")

    for bad in (True, 1.0, "3", None):
        try:
            seed_for(ALL_TUNES[0], 0, 0, campaign_ordinal=bad)  # type: ignore[arg-type]
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError(f"campaign_ordinal={bad!r} was accepted")


def test_derivation_version_is_declared() -> None:
    assert SEED_DERIVATION_VERSION == "seed_derivation_v2"


def main() -> int:
    test_distinct_campaigns_are_disjoint()
    test_v1_collision_would_have_been_caught()
    test_within_campaign_uniqueness_preserved()
    test_campaign_stride_exceeds_tune_span()
    test_ordinal_cap_fails_closed()
    test_campaign_ordinal_is_mandatory()
    test_derivation_version_is_declared()
    print("seed derivation tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
