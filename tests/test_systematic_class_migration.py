#!/usr/bin/env python3
"""Contract tests for S5, the decay-daughter class-migration systematic.

S5 is an exact zero, and it is exact for a structural reason: N_ch is an integer
count, the class boundaries are half-integers, and the measured 1.3272 % bias
moves no boundary across an integer. The margin is thin -- c11 at 32.5 needs
1.54 % and the bias is 1.3272 %, a factor of 1.16 -- so the null is a property of
THIS boundary set and this bias, not a general fact.

These tests exist so that changing either one fails here. A re-binning that put a
boundary above 0.5/delta = 37.7, or a re-measured bias above the tightest margin,
would silently inherit a null that no longer holds; the suite is where that must
surface, because the result document would otherwise still say "exactly zero".
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "systematic_class_migration.py"
RECORDED = ROOT / "results/systematics/20260817/s5_class_migration.json"
sys.path.insert(0, str(ROOT / "tools"))

import systematic_class_migration as migration  # noqa: E402


def test_every_boundary_clears_the_measured_bias() -> None:
    """The null's precondition, checked boundary by boundary.

    If this fails, S5 is no longer zero and must be re-measured -- the result
    document's "exactly zero" would be stale, not merely imprecise.
    """
    delta = migration.measured_bias()
    tightest = None
    for edge in migration.boundaries():
        margin = migration.crossing_margin(edge)
        assert margin > delta, (
            f"boundary {edge} needs only {100 * margin:.3f} % to cross an "
            f"integer, against a measured bias of {100 * delta:.4f} %. S5 is "
            "no longer a structural null and must be re-measured."
        )
        tightest = margin if tightest is None else min(tightest, margin)
    # Recorded so a shrinking margin is visible in the failure, not just a pass.
    assert tightest is not None
    assert tightest / delta > 1.0, tightest / delta


def test_the_integer_partition_is_unchanged_in_both_arms() -> None:
    """The mechanism, not the number: identical bin sets, identical projection."""
    delta = migration.measured_bias()
    edges = migration.boundaries()
    nominal = migration.integer_partition(edges, 200)
    for sign in (+1.0, -1.0):
        shifted = [edge / (1.0 + sign * delta) for edge in edges]
        assert migration.integer_partition(shifted, 200) == nominal, sign


def test_no_class_population_moves_in_any_tune() -> None:
    """The check on real committed data rather than on the argument."""
    delta = migration.measured_bias()
    edges = migration.boundaries()
    for tune in migration.TUNES:
        dist = migration.mb_distribution(tune)
        assert dist, tune
        nominal = migration.populations(dist, edges)
        assert sum(nominal) > 0, tune
        for sign in (+1.0, -1.0):
            shifted = [edge / (1.0 + sign * delta) for edge in edges]
            assert migration.populations(dist, shifted) == nominal, (tune, sign)


def test_the_recorded_result_reproduces() -> None:
    """The committed JSON is what the tool produces today."""
    assert RECORDED.is_file(), RECORDED
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "s5.json"
        result = subprocess.run(
            [sys.executable, str(TOOL), "--output", str(fresh)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(fresh.read_text()) == json.loads(
            RECORDED.read_text()
        ), "the recorded S5 result no longer reproduces"


def test_the_verdict_recorded_is_a_structural_null() -> None:
    payload = json.loads(RECORDED.read_text())
    assert payload["structural_null"] is True
    assert all(payload["integer_partition_identical"].values())
    assert not any(row["crosses_an_integer"] for row in payload["boundaries"])


def main() -> int:
    failures = 0
    for name, function in sorted(globals().items()):
        if not name.startswith("test_") or not callable(function):
            continue
        try:
            function()
        except Exception as error:  # noqa: BLE001
            failures += 1
            print(f"FAIL {name}: {error}")
        else:
            print(f"ok   {name}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
