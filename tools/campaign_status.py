#!/usr/bin/env python3
"""Count what a campaign started, what succeeded, and what did not.

Everything is read from what the worker already writes on disk -- there is no
separate bookkeeping database to fall out of step with reality:

  attempt_metadata/<TUNE>/*.json    one per attempt STARTED
  raw_validation/<TUNE>/.../receipt.json  one per attempt that finished
                                          producing, PASS or FAIL
  raw/<TUNE>/hf_<TUNE>_jobNNN.root  one per attempt that SUCCEEDED

An attempt that started and left no receipt neither succeeded nor failed
cleanly: it was killed. The CPU-time arm targets suspected generator hangs; the
wall-time arm is its backstop (`tools/render_production_submit.py:84-92`). Both
arms use one static hold-reason string, so the reason alone does not show which
arm fired (`tools/render_production_submit.py:333-341`).

The campaign record attributes the loss to a hang that hits dense-junction
topologies -- the configurations under study (`docs/GOLDEN_OUTPUTS.md:1067`).
Per-attempt termination metadata is absent (`docs/REPRODUCIBILITY.md:145-147`),
and the mechanism study used PYTHIA 8.315 while production used 8.317
(`docs2/physics/DISCARD_BIAS.md:117-124`). The discard rate must be reported,
not corrected away. See `docs2/physics/DISCARD_BIAS.md` for the full argument.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from campaign import CAMPAIGN_TUNES  # noqa: E402

ATTEMPT_STEM = re.compile(
    r"^hf_(?P<tune>[A-Za-z0-9_]+)_job(?P<job>\d+)_attempt(?P<attempt>\d+)_"
    r"(?P<cluster>[^_]+)_(?P<process>[^.]+)\.json$"
)
# A killed attempt leaves no sidecar -- the sidecar is written only after the
# producer exits -- but it does leave its partial output behind. Without this,
# the attempts that matter most are invisible and the discard rate reads zero.
PARTIAL_STEM = re.compile(
    r"^hf_(?P<tune>[A-Za-z0-9_]+)_job(?P<job>\d+)_attempt(?P<attempt>\d+)_"
    r"(?P<cluster>[^_]+)_(?P<process>[^.]+)\.partial\.root$"
)


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def collect(campaign_root: Path) -> dict:
    """Walk one campaign directory and classify every attempt."""
    attempts: dict[tuple[str, int, int], dict] = {}

    metadata_root = campaign_root / "attempt_metadata"
    for sidecar in sorted(metadata_root.glob("*/*.json")):
        match = ATTEMPT_STEM.match(sidecar.name)
        if not match:
            continue
        payload = load_json(sidecar) or {}
        key = (
            match["tune"],
            int(match["job"]),
            int(match["attempt"]),
        )
        attempts[key] = {
            "tune": match["tune"],
            "logical_id": int(match["job"]),
            "attempt": int(match["attempt"]),
            "seed": payload.get("seed"),
            "producer_exit": payload.get("producer_exit"),
            "elapsed_seconds": payload.get("elapsed_seconds"),
            "validator_status": None,
            "promoted": False,
            "partial_bytes": None,
        }

    # Attempts that were killed before the producer exited: a partial file with
    # no matching sidecar. These are precisely the suspected hangs, so leaving
    # them out would report a discard rate of zero however many jobs wedged.
    for partial in sorted((campaign_root / "partial").glob("*/*.partial.root")):
        match = PARTIAL_STEM.match(partial.name)
        if not match:
            continue
        key = (match["tune"], int(match["job"]), int(match["attempt"]))
        if key in attempts:
            continue
        attempts[key] = {
            "tune": match["tune"],
            "logical_id": int(match["job"]),
            "attempt": int(match["attempt"]),
            "seed": None,
            "producer_exit": None,
            "elapsed_seconds": None,
            "validator_status": None,
            "promoted": False,
            "partial_bytes": partial.stat().st_size,
        }

    validation_root = campaign_root / "raw_validation"
    for receipt_path in sorted(validation_root.glob("*/job*/attempt*/receipt.json")):
        payload = load_json(receipt_path)
        if not payload:
            continue
        key = (
            str(payload.get("tune")),
            int(payload.get("logical_id", -1)),
            int(payload.get("attempt", -1)),
        )
        if key in attempts:
            attempts[key]["validator_status"] = payload.get("validator_status")

    promoted: set[tuple[str, int]] = set()
    for raw in sorted((campaign_root / "raw").glob("*/hf_*_job*.root")):
        stem = re.match(r"^hf_(?P<tune>[A-Za-z0-9_]+)_job(?P<job>\d+)\.root$", raw.name)
        if stem:
            promoted.add((stem["tune"], int(stem["job"])))

    # A promoted file belongs to whichever attempt of that job produced cleanly.
    for key, record in attempts.items():
        tune, job, _ = key
        if (tune, job) in promoted and record["producer_exit"] == 0 and (
            record["validator_status"] == 0
        ):
            record["promoted"] = True

    return {"attempts": attempts, "promoted_jobs": promoted}


def classify(record: dict) -> str:
    """Classify one attempt.

    "no_verdict" means the attempt left no outcome: it is either still in
    flight (producing, or validating) or it was killed. On-disk evidence alone
    cannot tell those apart -- the sidecar is written when the producer exits,
    so a job that is midway through validation looks exactly like one the
    wall-time guard killed. Once the queue has drained, no_verdict IS the
    killed count, and that is when the hang rate can be read off. Reporting it
    as "killed" while jobs are still running would inflate the hang rate with
    jobs that are about to succeed.
    """
    if record["promoted"]:
        return "succeeded"
    if record["producer_exit"] is None:
        return "no_verdict"
    if record["producer_exit"] != 0:
        return "producer_failed"
    if record["validator_status"] is None:
        return "no_verdict"
    if record["validator_status"] != 0:
        return "validation_failed"
    return "produced_not_promoted"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign")
    parser.add_argument(
        "--production-root", type=Path,
        default=Path(os.environ.get("HF_PRODUCTION_ROOT", "Production")),
    )
    parser.add_argument("--expected-jobs", type=int, help="jobs per tune")
    parser.add_argument(
        "--expected-tunes", default=",".join(CAMPAIGN_TUNES),
        help="comma-separated tunes that SHOULD be present; completeness is "
             "judged against these, not against whatever happens to exist",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable")
    parser.add_argument(
        "--list-incomplete", action="store_true",
        help="print TUNE:LOGICAL_ID for jobs with no promoted output",
    )
    args = parser.parse_args()

    campaign_root = (args.production_root / args.campaign).resolve()
    if not campaign_root.is_dir():
        print(f"no such campaign directory: {campaign_root}", file=sys.stderr)
        return 1

    data = collect(campaign_root)
    attempts = data["attempts"]

    per_tune: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for record in attempts.values():
        per_tune[record["tune"]][classify(record)] += 1

    tunes = sorted(per_tune)
    jobs_done: dict[str, set[int]] = collections.defaultdict(set)
    for tune, job in data["promoted_jobs"]:
        jobs_done[tune].add(job)

    # Completeness is judged against the tunes that SHOULD be there. Deriving
    # it from the tunes found would report a campaign that never started, or
    # one where a whole tune is missing, as complete.
    expected_tunes = [
        name.strip() for name in args.expected_tunes.split(",") if name.strip()
    ]
    incomplete: list[str] = []
    if args.expected_jobs:
        for tune in expected_tunes:
            for job in range(args.expected_jobs):
                if job not in jobs_done[tune]:
                    incomplete.append(f"{tune}:{job}")

    if args.list_incomplete:
        print(",".join(incomplete))
        return 0

    total = collections.Counter()
    for counter in per_tune.values():
        total.update(counter)

    if args.json:
        json.dump(
            {
                "campaign": args.campaign,
                "campaign_root": str(campaign_root),
                "per_tune": {tune: dict(per_tune[tune]) for tune in tunes},
                "totals": dict(total),
                "attempts_started": sum(total.values()),
                "jobs_promoted": {tune: len(jobs_done[tune]) for tune in tunes},
                "incomplete": incomplete,
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        print()
        return 0

    started = sum(total.values())
    print(f"Campaign {args.campaign}")
    print(f"  {campaign_root}")
    print()
    header = (
        f"  {'tune':<20}{'started':>9}{'success':>9}{'noverdict':>11}"
        f"{'prodfail':>10}{'valfail':>9}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))
    for tune in tunes:
        counter = per_tune[tune]
        print(
            f"  {tune:<20}{sum(counter.values()):>9}"
            f"{counter['succeeded']:>9}{counter['no_verdict']:>11}"
            f"{counter['producer_failed']:>10}{counter['validation_failed']:>9}"
        )
    print("  " + "-" * (len(header) - 2))
    print(
        f"  {'TOTAL':<20}{started:>9}{total['succeeded']:>9}"
        f"{total['no_verdict']:>11}{total['producer_failed']:>10}"
        f"{total['validation_failed']:>9}"
    )
    print()
    for tune in tunes:
        print(f"  {tune}: {len(jobs_done[tune])} distinct jobs with promoted output")

    if started:
        killed_rate = total["no_verdict"] / started
        print()
        print(
            f"  attempts started {started}, succeeded {total['succeeded']}, "
            f"unsuccessful {started - total['succeeded']}"
        )
        if total["no_verdict"]:
            print(
                f"  no verdict {total['no_verdict']} = "
                f"{100 * killed_rate:.2f}% of attempts"
            )
            print(
                "  these are STILL RUNNING, were killed by the guard, or were "
                "removed by an operator -- on-disk evidence cannot tell them"
            )
            print(
                "  apart. Once the queue has drained, subtract any jobs you "
                "removed yourself; the remainder is the hang rate, a"
            )
            print(
                "  non-random loss (hangs occur on dense-junction topologies) "
                "that must be reported with the results."
            )
    if args.expected_jobs:
        print()
        if incomplete:
            print(
                f"  {len(incomplete)} of "
                f"{args.expected_jobs * len(expected_tunes)} job slots have no "
                f"promoted output"
            )
            if started:
                print(f"  resubmit with: make resubmit CAMPAIGN={args.campaign}")
            else:
                print("  nothing has run yet")
        else:
            print(
                f"  complete: each of {', '.join(expected_tunes)} has "
                f"{args.expected_jobs} promoted jobs"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
