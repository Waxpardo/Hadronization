#!/usr/bin/env python3
"""Resubmit jobs that produced no output, at the next attempt with fresh seeds.

Why fresh seeds. PYTHIA is deterministic given its seed, so re-running a wedged
job with the same seed risks wedging in exactly the same place. Events are
independent draws, so a different seed is statistically equivalent -- and
tools/campaign.py derives attempt seeds deterministically, so a retry is still
reproducible and can never collide with an earlier attempt.

Why this is not `periodic_release`. Releasing a held job re-runs it unchanged;
a hung job would simply hang again and burn the guard budget a second time.

Why it is needed at all. merge_root_files.sh requires equal exposure per tune,
so a campaign with any job missing cannot be merged. Held jobs must be replaced
before the campaign is analysable.

Held jobs are also removed from the queue (they hold a slot indefinitely
otherwise), which is the one irreversible action here and is why --dry-run is
the default.

Why the ledger is not optional. The derivation makes a collision unlikely; the
ledger is what makes it *detectable*. Exactly one of --seed-ledger and
--no-ledger REASON must be given, in dry runs too, so the dry run previews the
same guard state the apply will use.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import campaign_status  # noqa: E402
from campaign import (  # noqa: E402
    CAMPAIGN_TUNES,
    CARD_VARIANT_NONE,
    HANG_GUARD_MARKER,
)


def condor_held(cluster: str | None) -> list[tuple[str, str]]:
    """Return (jobid, hold reason) for held jobs.

    Hard-fails when condor is absent rather than reporting an empty queue.
    condor_* is not installed on the Nikhef LOGIN node at all -- only on stbc
    -- so the previous "empty if condor is absent" behaviour meant that
    `make resubmit APPLY=1` run from the login node rendered the retry submit
    and SILENTLY SKIPPED the condor_rm, leaving the hung job in the queue
    while its replacement ran. A wrong answer presented as a clean one.
    """
    command = ["condor_q", "-held", "-af:j", "HoldReason"]
    if cluster:
        command.insert(1, cluster)
    try:
        output = subprocess.run(
            command, text=True, capture_output=True, check=False
        ).stdout
    except FileNotFoundError:
        raise SystemExit(
            "ERROR: condor_q is not available on this host, so held jobs "
            "cannot be seen or removed.\n"
            "       Run this from the batch node, where condor lives:\n"
            "         ssh -o BatchMode=yes -o RemoteCommand=none "
            "-o RequestTTY=no stbc\n"
            "       The login node has no condor_q, condor_rm or "
            "condor_submit."
        ) from None
    held = []
    for line in output.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            held.append((parts[0], parts[1]))
    return held


def campaign_ordinal_on_disk(campaign_root: Path) -> tuple[int | None, set[int]]:
    """Return the campaign ordinal this campaign's own jobs already carry.

    The ordinal is packed into every event ID, so a retry rendered with a
    different one produces events attributed to a different campaign from the
    292 it is completing -- inside a single merge, where no downstream
    validator would trace the mismatch back to the retry. Reading it off the
    jobs already on disk makes that disagreement unrepresentable rather than
    merely unlikely, which is why this is preferred over an argument the
    caller has to remember to pass correctly.

    Returns (ordinal, observed). ordinal is None when nothing is on disk yet
    or when the values disagree; observed lets the caller tell those apart.
    """
    observed: set[int] = set()
    for sidecar in sorted((campaign_root / "attempt_metadata").glob("*/*.json")):
        ordinal = (campaign_status.load_json(sidecar) or {}).get("campaign_ordinal")
        if isinstance(ordinal, int) and not isinstance(ordinal, bool):
            observed.add(ordinal)
    if len(observed) == 1:
        return next(iter(observed)), observed
    return None, observed


def card_variant_on_disk(campaign_root: Path) -> tuple[str | None, set[str]]:
    """Return the card variant this campaign's own jobs already carry.

    Same argument as the ordinal above, and the failure is worse because it is
    invisible: a retry rendered without --card-variant would draw the NOMINAL
    card, so a systematics campaign would finish with a handful of jobs that
    are not the variation at all. Nothing downstream would flag it -- each such
    job is internally consistent, its effective_card_sha256 matches the card it
    actually ran -- and the resulting Delta would be diluted by however many
    jobs were retried, in the direction of "no systematic".

    Sidecars written before 2026-08-17 have no card_variant key. Those are
    nominal campaigns by construction, so a missing key reads as NONE rather
    than as unknown.
    """
    observed: set[str] = set()
    for sidecar in sorted((campaign_root / "attempt_metadata").glob("*/*.json")):
        payload = campaign_status.load_json(sidecar) or {}
        if not payload:
            continue
        variant = payload.get("card_variant", CARD_VARIANT_NONE)
        if isinstance(variant, str) and variant:
            observed.add(variant)
    if len(observed) == 1:
        return next(iter(observed)), observed
    return None, observed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign")
    parser.add_argument(
        "--campaign-ordinal", type=int, default=None,
        help="ordinal to render the retry with. Defaults to the ordinal this "
             "campaign's existing jobs already carry, and refuses to override "
             "it with a conflicting value. Needed explicitly only when no "
             "attempt metadata exists yet.",
    )
    parser.add_argument("--jobs", type=int, required=True, help="jobs per tune")
    parser.add_argument("--events", type=int, required=True)
    parser.add_argument("--attempt", type=int, required=True,
                        help="attempt number to render (previous + 1)")
    parser.add_argument("--checkout", type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--production-root", type=Path,
        default=Path(os.environ.get("HF_PRODUCTION_ROOT", "Production")),
    )
    parser.add_argument("--cluster", help="restrict condor_rm to this cluster")
    # Exactly one of these is required. The ledger is the ONLY thing that can
    # refuse a seed already burned by an earlier attempt, and it was previously
    # optional with no default: omitting it rendered a retry with the guard
    # silently off, and a collision it would have caught is invisible
    # afterwards -- the duplicate events are internally consistent and no
    # downstream validator distinguishes them from independent draws. A default
    # path would be worse than requiring the flag, because it would make a
    # wrong-ledger retry look served. Opting out must therefore be stated, and
    # stated with a reason, so it appears in the operator's own log.
    ledger = parser.add_mutually_exclusive_group(required=True)
    ledger.add_argument(
        "--seed-ledger", type=Path,
        help="authoritative burned-seed ledger; the retry's seeds are burned "
             "into it and a collision with any earlier attempt is refused",
    )
    ledger.add_argument(
        "--no-ledger", metavar="REASON",
        help="render WITHOUT the collision guard, for the stated reason. Use "
             "only where a collision is impossible or irrelevant -- a scratch "
             "campaign, a test render -- never for production output",
    )
    parser.add_argument("--producer-executable-sha256")
    parser.add_argument(
        "--tunes", default=",".join(CAMPAIGN_TUNES),
        help="tunes that SHOULD be present; a tune that never started still "
             "needs its jobs rendered, so this cannot be inferred from disk",
    )
    parser.add_argument("--max-runtime-seconds", type=int)
    parser.add_argument("--max-cpu-seconds", type=int)
    parser.add_argument(
        "--apply", action="store_true",
        help="actually remove held jobs and write the retry submit file",
    )
    args = parser.parse_args()

    # argparse accepts --no-ledger "" and --no-ledger "   ". An empty reason is
    # not a stated one, so it is refused rather than recorded as a blank.
    if args.no_ledger is not None and not args.no_ledger.strip():
        parser.error("--no-ledger needs a non-empty reason")

    campaign_root = (args.production_root / args.campaign).resolve()
    if not campaign_root.is_dir():
        print(f"no such campaign directory: {campaign_root}", file=sys.stderr)
        return 1

    observed_ordinal, observed = campaign_ordinal_on_disk(campaign_root)
    if len(observed) > 1:
        print(
            f"campaign {args.campaign} carries more than one campaign ordinal "
            f"on disk: {sorted(observed)}. Refusing to guess which one a retry "
            "should complete.",
            file=sys.stderr,
        )
        return 1
    if args.campaign_ordinal is None:
        if observed_ordinal is None:
            print(
                "no attempt metadata under "
                f"{campaign_root / 'attempt_metadata'}, so the campaign ordinal "
                "cannot be derived. Pass --campaign-ordinal explicitly.",
                file=sys.stderr,
            )
            return 1
        campaign_ordinal = observed_ordinal
    else:
        campaign_ordinal = args.campaign_ordinal
        if observed_ordinal is not None and observed_ordinal != campaign_ordinal:
            print(
                f"--campaign-ordinal {campaign_ordinal} disagrees with ordinal "
                f"{observed_ordinal}, which this campaign's jobs already carry. "
                "The retry would be attributed to a different campaign from the "
                "jobs it completes.",
                file=sys.stderr,
            )
            return 1

    # Derived, never passed. A retry that silently drew the nominal card would
    # dilute the variation toward "no systematic" and nothing downstream would
    # flag it.
    card_variant, observed_variants = card_variant_on_disk(campaign_root)
    if len(observed_variants) > 1:
        print(
            f"campaign {args.campaign} carries more than one card variant on "
            f"disk: {sorted(observed_variants)}. Refusing to guess which card a "
            "retry should run.",
            file=sys.stderr,
        )
        return 1
    if card_variant is None:
        # No metadata at all. The ordinal check above has already returned in
        # that case unless --campaign-ordinal was passed explicitly, so this is
        # a first render of a campaign with nothing on disk: nominal.
        card_variant = CARD_VARIANT_NONE

    data = campaign_status.collect(campaign_root)
    done = {(tune, job) for tune, job in data["promoted_jobs"]}

    tunes = [name.strip() for name in args.tunes.split(",") if name.strip()]
    if not tunes:
        print("no tunes given", file=sys.stderr)
        return 1
    started = sorted({record["tune"] for record in data["attempts"].values()})
    never_started = [tune for tune in tunes if tune not in started]
    if never_started:
        print(f"  tunes with no attempts at all: {', '.join(never_started)}")

    missing = [
        f"{tune}:{job}"
        for tune in tunes
        for job in range(args.jobs)
        if (tune, job) not in done
    ]

    held = condor_held(args.cluster)
    # Only jobs the hang guard held are auto-resubmitted. A job held for any
    # other reason -- operator action, a site policy, an unexpected fault --
    # is left alone and reported, because resubmitting it blindly would hide
    # whatever actually went wrong.
    guard_held = [jobid for jobid, reason in held if HANG_GUARD_MARKER in reason]
    other_held = [
        (jobid, reason) for jobid, reason in held
        if HANG_GUARD_MARKER not in reason
    ]

    print(f"Campaign {args.campaign}")
    print(f"  campaign ordinal: {campaign_ordinal}"
          + (" (derived from attempt metadata)" if args.campaign_ordinal is None
             else " (from --campaign-ordinal, agrees with disk)"))
    print(f"  card variant: {card_variant} (derived from attempt metadata)")
    if args.seed_ledger:
        print(f"  seed ledger: {args.seed_ledger} (collision guard ON)")
    else:
        print(f"  seed ledger: NONE -- collision guard OFF, stated reason: "
              f"{args.no_ledger.strip()}")
    print(f"  jobs per tune expected: {args.jobs}")
    print(f"  tunes: {', '.join(tunes)}")
    print(f"  job slots with no promoted output: {len(missing)}")
    if held:
        print(f"  held in queue: {len(held)} "
              f"({len(guard_held)} by the hang guard)")
        for jobid, reason in other_held[:5]:
            print(f"    NOT a guard hold, left alone: {jobid} {reason[:70]}")
    if not missing:
        print("  nothing to resubmit")
        return 0

    print(f"  would render attempt {args.attempt} for {len(missing)} jobs")
    if not args.apply:
        print()
        print("  dry run. Re-run with --apply to remove held jobs and render.")
        print(f"  jobs: {','.join(missing[:20])}"
              + (" ..." if len(missing) > 20 else ""))
        return 0

    if guard_held:
        print(f"  removing {len(guard_held)} guard-held jobs from the queue")
        subprocess.run(["condor_rm", *guard_held], check=False)
    if other_held:
        print(
            f"  leaving {len(other_held)} job(s) held for other reasons; "
            "investigate them before assuming the campaign is sound"
        )

    output = args.checkout / f"submit_{args.campaign}_retry{args.attempt}.sub"
    command = [
        sys.executable,
        str(args.checkout / "tools/render_production_submit.py"),
        str(args.checkout), str(output),
        "--campaign", args.campaign,
        "--campaign-ordinal", str(campaign_ordinal),
        "--jobs", str(args.jobs),
        "--events", str(args.events),
        "--attempt", str(args.attempt),
        "--only-jobs", ",".join(missing),
        "--card-variant", card_variant,
    ]
    # Only override the guard when asked; otherwise the retry inherits the
    # renderer's calibrated defaults rather than a stale copy kept here.
    if args.max_runtime_seconds is not None:
        command.extend(["--max-runtime-seconds", str(args.max_runtime_seconds)])
    if args.max_cpu_seconds is not None:
        command.extend(["--max-cpu-seconds", str(args.max_cpu_seconds)])
    for tune in tunes:
        command.extend(["--tune", tune])
    if args.seed_ledger:
        command.extend(["--seed-ledger", str(args.seed_ledger), "--burn-seeds"])
    if args.producer_executable_sha256:
        command.extend(
            ["--producer-executable-sha256", args.producer_executable_sha256]
        )
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        return result.returncode
    print(f"  submit with: condor_submit {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
