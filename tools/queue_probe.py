#!/usr/bin/env python3
"""Ask whether the queue is empty, and refuse to guess when the query failed.

WHY THIS EXISTS. A convergence monitor gating the post-campaign sync reported
QUEUE_EMPTY during an SSH outage. `condor_q` had failed, the monitor summed an
empty result to zero, and the loop concluded the campaign had drained. Nothing
was acted on -- the state was re-checked before proceeding and the job was still
running -- but the shape is the dangerous one: **an empty answer and an
unanswered question are not the same thing**, and the sync ends the checkout
freeze, which fails every job still in flight.

THE RULE, graduated to a standing convention: an empty queue report is evidence
of nothing until the query's success is verified. Any probe gating an
irreversible act must distinguish connection or exit failure from a genuinely
empty result, and must FAIL CLOSED on "couldn't ask".

Three outcomes, never two:

    QUEUE_EMPTY      exit 0    the schedd answered and holds nothing
    QUEUE_NONEMPTY   exit 1    the schedd answered and holds jobs
    QUEUE_UNKNOWN    exit 2    the question was not answered -- treat as
                               "not empty" for any gating decision

Emptiness is established by TWO conditions, not one: the listing command must
exit zero, AND a separate `condor_q -totals` probe must return a line naming the
schedd. A command that exits zero while printing nothing because it could not
reach the schedd satisfies the first and fails the second, which is exactly the
case that produced the false report.

Usage:
  python3 tools/queue_probe.py                     # probe the real queue
  python3 tools/queue_probe.py --cluster 5397565   # restrict to one cluster
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

EMPTY = "QUEUE_EMPTY"
NONEMPTY = "QUEUE_NONEMPTY"
UNKNOWN = "QUEUE_UNKNOWN"

EXIT_EMPTY = 0
EXIT_NONEMPTY = 1
EXIT_UNKNOWN = 2

# What a reachable schedd puts in its -totals banner. Its presence is the
# positive evidence that the question was actually answered; its absence is not
# treated as "empty" under any circumstances.
SCHEDD_MARKER = "Schedd:"


def _run(command: list[str], timeout: int) -> tuple[int, str, str]:
    """Run a command, mapping every failure mode onto a nonzero status.

    A timeout and a missing binary are indistinguishable from a crash for our
    purposes: in all three cases the question was not answered.
    """
    try:
        completed = subprocess.run(
            command, text=True, capture_output=True, timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    except FileNotFoundError:
        return 127, "", f"{command[0]} not found"
    except OSError as error:
        return 126, "", str(error)
    return completed.returncode, completed.stdout, completed.stderr


def probe(
    listing_command: list[str],
    totals_command: list[str],
    timeout: int = 60,
    runner=_run,
) -> tuple[str, int, str]:
    """Return (verdict, count, detail). `runner` is injectable so the failure
    modes can be tested without breaking a real schedd."""
    totals_rc, totals_out, totals_err = runner(totals_command, timeout)
    if totals_rc != 0:
        return UNKNOWN, -1, (
            f"totals probe exited {totals_rc}: {(totals_err or '').strip()[:200]}"
        )
    if SCHEDD_MARKER not in totals_out:
        # This is the false-QUEUE_EMPTY case. The command may exit zero and
        # print nothing when it cannot reach the schedd.
        return UNKNOWN, -1, (
            "totals probe returned no schedd banner, so the schedd did not "
            "answer; an empty listing here means 'could not ask', not 'nothing "
            "queued'"
        )

    listing_rc, listing_out, listing_err = runner(listing_command, timeout)
    if listing_rc != 0:
        return UNKNOWN, -1, (
            f"listing exited {listing_rc}: {(listing_err or '').strip()[:200]}"
        )

    jobs = [line for line in listing_out.splitlines() if line.strip()]
    if not jobs:
        return EMPTY, 0, "schedd answered and holds no matching jobs"
    return NONEMPTY, len(jobs), f"schedd answered and holds {len(jobs)} job(s)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster", help="restrict the listing to one cluster")
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    if shutil.which("condor_q") is None:
        print(f"{UNKNOWN} reason=condor_q is not on PATH on this host",
              file=sys.stderr)
        return EXIT_UNKNOWN

    listing = ["condor_q"]
    if args.cluster:
        listing.append(args.cluster)
    listing += ["-af", "ClusterId", "ProcId", "JobStatus"]

    verdict, count, detail = probe(listing, ["condor_q", "-totals"],
                                   args.timeout)
    stream = sys.stderr if verdict == UNKNOWN else sys.stdout
    print(f"{verdict} count={count} detail={detail}", file=stream)
    return {EMPTY: EXIT_EMPTY, NONEMPTY: EXIT_NONEMPTY}.get(
        verdict, EXIT_UNKNOWN)


if __name__ == "__main__":
    raise SystemExit(main())
