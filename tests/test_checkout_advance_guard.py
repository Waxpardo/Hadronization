#!/usr/bin/env python3
"""The checkout guard must refuse on anything but a verified-empty queue.

The defect it replaces, verbatim: the v3 analysis submit pinned commit
61fe978f, the checkout was advanced four times while its 3000 jobs were in
flight, and every job finishing after the first advance failed its promotion
provenance check. The freeze had been enforced by memory, and memory was wrong
within hours of the previous freeze being lifted.

Every case here is exercised without a schedd, which is the point: the refusal
paths cannot be reached against a healthy cluster and are exactly the ones that
must not be assumed.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from queue_probe import EMPTY, NONEMPTY, UNKNOWN  # noqa: E402
from checkout_advance_guard import (  # noqa: E402
    ALLOW, OVERRIDE, REFUSE, evaluate,
)


def test_verified_empty_allows() -> None:
    verdict, detail = evaluate(EMPTY, 0, "schedd answered", None)
    assert verdict == ALLOW, verdict
    assert "empty" in detail


def test_jobs_in_flight_refuse() -> None:
    """THE ACTUAL DEFECT: jobs were in flight and the checkout moved."""
    verdict, detail = evaluate(NONEMPTY, 2702, "schedd answered", None)
    assert verdict == REFUSE, verdict
    assert "2702" in detail
    # The message must say WHY, since the reader's instinct will be that a
    # held or idle job is not "really" running.
    assert "pinning a commit" in detail


def test_one_job_is_enough_to_refuse() -> None:
    """No threshold. One in-flight job pins a commit exactly as 3000 do."""
    verdict, _ = evaluate(NONEMPTY, 1, "schedd answered", None)
    assert verdict == REFUSE, verdict


def test_unknown_refuses_and_is_not_treated_as_empty() -> None:
    verdict, detail = evaluate(UNKNOWN, -1, "totals probe exited 255", None)
    assert verdict == REFUSE, verdict
    assert verdict != ALLOW
    assert "UNKNOWN" in detail


def test_unrecognised_verdict_fails_closed() -> None:
    verdict, _ = evaluate("SOMETHING_NEW", 0, "", None)
    assert verdict == REFUSE, verdict


def test_override_is_allowed_and_records_its_reason() -> None:
    """The override exists for restoring a pin, not for ignoring the guard."""
    reason = "detaching to 61fe978 to restore the pin in-flight jobs verify"
    verdict, detail = evaluate(NONEMPTY, 2702, "schedd answered", reason)
    assert verdict == OVERRIDE, verdict
    assert reason in detail, "the reason must appear in the output, not be implied"


def test_override_does_not_silently_become_allow() -> None:
    """OVERRIDE and ALLOW are distinct verdicts so logs can tell them apart."""
    assert OVERRIDE != ALLOW
    reason = "restoring a pin"
    verdict, _ = evaluate(UNKNOWN, -1, "probe failed", reason)
    assert verdict == OVERRIDE
    assert verdict != ALLOW


def main() -> int:
    ran = 0
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            ran += 1
    print(f"checkout-advance-guard tests passed tests={ran}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
