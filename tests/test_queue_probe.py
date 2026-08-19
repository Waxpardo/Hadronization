#!/usr/bin/env python3
"""UNKNOWN must never be reported as EMPTY.

The defect being prevented, verbatim from the session that produced it: a
convergence monitor gating the post-campaign sync reported QUEUE_EMPTY during an
SSH outage, because condor_q failed and the sum of an empty result is zero. The
sync ends the checkout freeze and fails every job still in flight, so a probe
that cannot tell "nothing queued" from "could not ask" must not gate it.

Every test here simulates a failure mode WITHOUT a schedd, which is the point:
these paths cannot be exercised against a healthy cluster, and they are exactly
the paths that were wrong.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from queue_probe import EMPTY, NONEMPTY, UNKNOWN, probe  # noqa: E402

LISTING = ["condor_q", "-af", "ClusterId"]
TOTALS = ["condor_q", "-totals"]
BANNER = "\n-- Schedd: taai-007.nikhef.nl : <145.107.7.246:9618?...\n"


def fake(responses):
    """Runner returning queued (rc, stdout, stderr) tuples by command."""
    def runner(command, timeout):
        key = "totals" if "-totals" in command else "listing"
        return responses[key]
    return runner


def test_empty_requires_the_schedd_to_have_answered() -> None:
    verdict, count, _ = probe(
        LISTING, TOTALS,
        runner=fake({"totals": (0, BANNER, ""), "listing": (0, "", "")}),
    )
    assert verdict == EMPTY, verdict
    assert count == 0


def test_nonempty_counts_jobs() -> None:
    verdict, count, _ = probe(
        LISTING, TOTALS,
        runner=fake({"totals": (0, BANNER, ""),
                     "listing": (0, "5397565 0 2\n5397565 1 1\n", "")}),
    )
    assert verdict == NONEMPTY, verdict
    assert count == 2, count


def test_silent_success_is_UNKNOWN_not_EMPTY() -> None:
    """THE ACTUAL DEFECT.

    condor_q exits zero and prints nothing because it never reached the schedd.
    The old monitor called that empty. It must be UNKNOWN.
    """
    verdict, count, detail = probe(
        LISTING, TOTALS,
        runner=fake({"totals": (0, "", ""), "listing": (0, "", "")}),
    )
    assert verdict == UNKNOWN, (
        f"a zero-exit, no-banner response was reported as {verdict}; this is "
        "the false-QUEUE_EMPTY shape that gated a sync"
    )
    assert verdict != EMPTY
    assert count == -1
    assert "could not ask" in detail or "did not answer" in detail


def test_totals_failure_is_UNKNOWN() -> None:
    for rc, err in ((1, "Failed to connect"), (124, "timeout after 60s"),
                    (127, "condor_q not found"), (255, "ssh died")):
        verdict, _, _ = probe(
            LISTING, TOTALS,
            runner=fake({"totals": (rc, "", err), "listing": (0, "", "")}),
        )
        assert verdict == UNKNOWN, f"rc={rc} gave {verdict}, expected UNKNOWN"


def test_listing_failure_is_UNKNOWN_even_when_schedd_answered() -> None:
    """A reachable schedd does not make a failed listing an empty one."""
    verdict, _, _ = probe(
        LISTING, TOTALS,
        runner=fake({"totals": (0, BANNER, ""),
                     "listing": (1, "", "Error: bad constraint")}),
    )
    assert verdict == UNKNOWN, verdict


def test_unknown_is_never_the_empty_exit_code() -> None:
    """Fail closed: a caller that only checks the exit status must not read
    UNKNOWN as EMPTY."""
    from queue_probe import EXIT_EMPTY, EXIT_NONEMPTY, EXIT_UNKNOWN
    assert EXIT_UNKNOWN != EXIT_EMPTY
    assert EXIT_UNKNOWN != EXIT_NONEMPTY
    # Non-zero, so `if probe; then treat_as_empty; fi` cannot misfire.
    assert EXIT_UNKNOWN != 0


def main() -> int:
    ran = 0
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            ran += 1
    print(f"queue-probe tests passed tests={ran}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
