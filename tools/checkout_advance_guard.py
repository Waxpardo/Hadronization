#!/usr/bin/env python3
"""Refuse to advance the Nikhef checkout while jobs are in flight.

WHY THIS EXISTS. The checkout freeze had been enforced by memory for weeks and
then broken within hours of being lifted. The v3 analysis submit pinned commit
61fe978f; the checkout was advanced four times while its 3000 jobs were in
flight; every job finishing after the first advance failed at its promotion
check with "analysis checkout changed after worker provenance was pinned".
Nothing was lost -- the work had already succeeded and the partial stages were
retained -- but 2702 jobs had to be re-run.

THE INVARIANT, and it is not about campaigns:

    Jobs in flight that pin a commit  =>  the checkout does not move.

Production jobs verify their pinned commit at STARTUP. Analysis jobs verify it
at PROMOTION. Either way, moving the checkout under them invalidates work that
has already been done. "The freeze is over" is only ever true of a specific
campaign, and only until the next submission -- which is exactly the reading
that failed, so this tool replaces the reading with a check.

FAIL-CLOSED, on the same principle as tools/queue_probe.py: an unanswered
question is not an empty queue. If the probe cannot reach the schedd, the
advance is refused, because "I could not ask whether jobs are in flight" is not
evidence that none are.

THE OVERRIDE EXISTS FOR ONE SHAPE OF ACTION: restoring a pin rather than
breaking one. Detaching the checkout back to the commit that in-flight jobs
already pin makes their verification succeed; it is the remedy, not the hazard.
It requires --override-reason so the justification is recorded rather than
implied.

Usage:
  python3 tools/checkout_advance_guard.py                      # may I advance?
  python3 tools/checkout_advance_guard.py --override-reason "..."
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ALLOW = "CHECKOUT_ADVANCE_ALLOWED"
REFUSE = "CHECKOUT_ADVANCE_REFUSED"
OVERRIDE = "CHECKOUT_ADVANCE_OVERRIDE"

EXIT_ALLOW = 0
EXIT_REFUSE = 1

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def find_pinfile() -> Path | None:
    """The detached-run pinfile for this checkout, if it exists.

    Lives beside the hook's log inside .git/, so it is untracked and cannot be
    removed by a checkout move -- the same reasoning that put the guard hook
    there. Returns None when git cannot be consulted at all.
    """
    try:
        git_dir = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    if git_dir.returncode != 0:
        return None
    candidate = Path(git_dir.stdout.strip()) / "checkout_pin"
    return candidate if candidate.exists() else None


def evaluate(probe_verdict: str, probe_count: int, probe_detail: str,
             override_reason: str | None,
             pinfile: Path | None = None) -> tuple[str, str]:
    """Pure decision, so every branch is testable without a schedd."""
    from queue_probe import EMPTY, NONEMPTY, UNKNOWN

    # THE PINFILE OUTRANKS EVERYTHING, INCLUDING THE OVERRIDE.
    #
    # The queue probe cannot see a detached process -- a long merge runs as a
    # nohup process, not a Condor job -- so an empty queue is not evidence that
    # nothing pins this checkout. This guard once reported ALLOWED while a 65 h
    # merge was reading the frozen tree.
    #
    # It is checked BEFORE --override-reason on purpose. The reference-
    # transaction hook, which is the actual enforcement, has no override for the
    # pinfile; a guard that answered OVERRIDE here would disagree with the hook
    # and send someone chasing a refusal the guard said would not happen.
    # The guard's job is to predict the hook, not to out-rank it.
    if pinfile is not None:
        return REFUSE, (
            f"a detached run pins this checkout ({pinfile}). The queue cannot "
            "see it, so an empty queue proves nothing here. This is NOT "
            "overridable: verify the run named in the pinfile has finished, "
            "then remove the file."
        )
    if override_reason:
        # Recorded, never silent. The override does not consult the queue at
        # all: its whole purpose is acting deliberately despite in-flight jobs.
        return OVERRIDE, f"override accepted, reason: {override_reason}"
    if probe_verdict == EMPTY:
        return ALLOW, "queue verified empty; no job can be pinning a commit"
    if probe_verdict == NONEMPTY:
        return REFUSE, (
            f"{probe_count} job(s) in flight, each pinning a commit. Advancing "
            "the checkout invalidates their provenance check -- production at "
            "startup, analysis at promotion. Wait for convergence, or pass "
            "--override-reason if this advance RESTORES a pin rather than "
            "breaking one."
        )
    if probe_verdict == UNKNOWN:
        return REFUSE, (
            f"queue state UNKNOWN ({probe_detail}). Refusing: an unanswered "
            "question is not an empty queue, and the cost of being wrong is "
            "re-running a campaign."
        )
    return REFUSE, f"unrecognised probe verdict {probe_verdict!r}; failing closed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--override-reason",
        help="advance anyway, recording why. Intended for restoring a pin.",
    )
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    from queue_probe import UNKNOWN, probe

    pinfile = find_pinfile()

    if pinfile is not None:
        # Checked before the queue is consulted at all: the answer cannot change
        # it, and asking a schedd that may be slow or absent would only delay a
        # refusal that is already decided.
        verdict, detail = evaluate(UNKNOWN, -1, "not consulted",
                                   args.override_reason, pinfile)
    elif args.override_reason:
        verdict, detail = evaluate(UNKNOWN, -1, "not consulted",
                                   args.override_reason)
    else:
        listing = ["condor_q", "-af", "ClusterId", "ProcId", "JobStatus"]
        probe_verdict, count, probe_detail = probe(
            listing, ["condor_q", "-totals"], args.timeout)
        verdict, detail = evaluate(probe_verdict, count, probe_detail, None)

    stream = sys.stdout if verdict != REFUSE else sys.stderr
    print(f"{verdict} {detail}", file=stream)
    return EXIT_ALLOW if verdict in (ALLOW, OVERRIDE) else EXIT_REFUSE


if __name__ == "__main__":
    raise SystemExit(main())
