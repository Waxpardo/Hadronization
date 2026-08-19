#!/usr/bin/env python3
"""Render a Condor submit file for a production run.

Jobs are described directly by (tune, jobs, events) rather than read from a
sealed manifest. Seeds are derived deterministically in tools/campaign.py, so
the same command always produces the same submit file, and the seed ledger
still refuses a seed that has been used before.

Job size and job count are arguments. They carry no physics -- they only say
how CPU is sliced -- and the previous design, which froze them into a schema
replicated across seven modules, drifted.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from campaign import (  # noqa: E402
    ALL_TUNES,
    CARD_VARIANT_NONE,
    CARD_VARIANT_TOKEN,
    HANG_GUARD_MARKER,
    CAMPAIGN_TUNES,
    MAX_ATTEMPTS,
    assert_seeds_unused,
    burn_seeds,
    effective_card_sha256,
    resolve_card_path,
    resolve_production_root,
    seed_for,
)

SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_TOKEN = re.compile(r"^[A-Za-z0-9._-]+$")

# A hung generator never exits, so on_exit_hold cannot catch it. The PYTHIA
# junction-splitting hang burned 34 CPU-hours across four jobs unnoticed.
#
# CPU TIME IS THE RIGHT VARIABLE, NOT WALL TIME.
#
# The hang burns CPU continuously -- the four wedged jobs ran at CPU/wall =
# 0.97. A legitimate job on a contended node looks nothing like that: one in
# the smoke test sat at CPU/wall = 0.33, 1787s of wall clock for 598s of work,
# and was heading toward a wall-clock limit while behaving perfectly.
#
# A wall-clock guard therefore cannot separate "wedged" from "sharing a slot",
# and tightening it to catch hangs sooner buys false positives that discard
# good jobs -- biased toward whichever nodes happen to be busy, which has
# nothing to do with physics. CPU time stays bounded for a healthy job however
# contended its node is.
#
# WHY THE THRESHOLD IS GENEROUS RATHER THAN TIGHT.
#
# The hang is UNBOUNDED, so any finite threshold catches it eventually; the
# only cost of a high threshold is wasted CPU per hang. A threshold set close
# to the typical job, by contrast, also cuts the tail of legitimate slow jobs
# -- and that tail is not random. Events with dense junction topologies take
# longer to fragment AND are exactly the events that produce the baryons this
# analysis measures. Cutting them would bias the observable directly, which is
# far worse than burning an extra hour of CPU on a job that was doomed anyway.
#
# So the threshold is set above anything plausibly legitimate, not just above
# the median. Measured CPU per 100k-event job: MONASH 247s median / 321s max,
# JUNCTIONS 480s / 632s, CLOSEPACKING 677s / 762s. One smoke-test job reached
# 2398s of CPU without being a classic hang (its CPU then froze -- it was
# blocked on I/O, not looping), which is the kind of legitimate-looking outlier
# a tight cut would have discarded.
DEFAULT_MAX_CPU_SECONDS = 3_600  # ~4.7x the slowest normal job, above the outlier
# Backstop for a job stuck without burning CPU (dead mount, hung I/O), which
# the CPU guard cannot see. Deliberately generous.
DEFAULT_MAX_RUNTIME_SECONDS = 14_400


def reject_condor_unsafe_path(path: Path, label: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_./:+-]+", str(path)):
        raise ValueError(f"{label} contains unsupported characters: {path}")


def write_once_or_identical(path: Path, content: str) -> None:
    """Never replace a submit artifact that may already be queued."""
    encoded = content.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError(f"submit output may not be a symlink: {path}")
    if path.exists():
        if not path.is_file() or path.read_bytes() != encoded:
            raise ValueError(
                f"existing submit artifact differs; refusing overwrite: {path}"
            )
        return
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def git_head(project_base: Path) -> str:
    commit = subprocess.check_output(
        ["git", "-C", str(project_base), "rev-parse", "HEAD"], text=True
    ).strip()
    # Tracked changes only. Untracked files must not count: the rendered submit
    # file itself lands in the checkout, so counting them would make rendering
    # one submit block the next. This matches the check runCondorJob.sh applies
    # at run time, which is the one that actually protects the output.
    dirty = subprocess.check_output(
        ["git", "-C", str(project_base), "diff", "--name-only", "HEAD", "--"],
        text=True,
    ).strip()
    if dirty:
        raise ValueError(
            "refusing to submit from a checkout with tracked modifications; "
            f"commit or stash first:\n{dirty}"
        )
    return commit


def card_for(project_base: Path, tune: str, card_variant: str) -> Path:
    card = resolve_card_path(project_base, tune, card_variant)
    if not card.is_file():
        raise ValueError(f"no tune card for {tune} variant {card_variant}: {card}")
    return card


def producer_sha256(project_base: Path) -> str:
    producer = project_base / "generation" / "producer" / "heavyflavourcorrelations_status"
    if not producer.is_file():
        raise ValueError(f"producer binary is absent: {producer}")
    return hashlib.sha256(producer.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_base", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--campaign", required=True)
    parser.add_argument("--campaign-ordinal", type=int, required=True)
    parser.add_argument(
        "--tune", action="append", choices=ALL_TUNES, dest="tunes",
        help="repeatable; defaults to the three published tunes",
    )
    parser.add_argument(
        "--attempt", type=int, default=0,
        help="retry generation; each attempt uses a fresh deterministic seed",
    )
    parser.add_argument(
        "--only-jobs",
        help="comma-separated TUNE:LOGICAL_ID pairs to render (for retries)",
    )
    parser.add_argument(
        "--burn-seeds", action="store_true",
        help="append the rendered seeds to the ledger",
    )
    parser.add_argument("--jobs", type=int, required=True, help="jobs per tune")
    parser.add_argument(
        "--events", type=int, required=True, help="requested successes per job"
    )
    parser.add_argument("--pthat-min", default="NONE")
    parser.add_argument(
        "--card-variant", default=CARD_VARIANT_NONE,
        help="systematics variation card token; NONE is the nominal tune card",
    )
    parser.add_argument("--multiplicity-audit-events", type=int, default=0)
    parser.add_argument("--seed-ledger", type=Path)
    parser.add_argument("--producer-executable-sha256")
    parser.add_argument(
        "--max-runtime-seconds", type=int, default=DEFAULT_MAX_RUNTIME_SECONDS,
        help="wall-clock backstop for a job stuck without burning CPU",
    )
    parser.add_argument(
        "--max-cpu-seconds", type=int, default=DEFAULT_MAX_CPU_SECONDS,
        help="primary hang guard; a wedged generator burns CPU continuously",
    )
    args = parser.parse_args()

    project_base = args.project_base.resolve()
    output_path = args.output.resolve()
    reject_condor_unsafe_path(project_base, "project_base")
    reject_condor_unsafe_path(output_path, "output")

    if not SAFE_TOKEN.fullmatch(args.campaign):
        raise ValueError("campaign name contains unsafe characters")
    if args.card_variant != CARD_VARIANT_NONE and not CARD_VARIANT_TOKEN.fullmatch(
        args.card_variant
    ):
        raise ValueError(
            "--card-variant must be NONE or a lowercase [a-z0-9_] token"
        )
    if not 1 <= args.campaign_ordinal <= 65_535:
        raise ValueError("campaign_ordinal must be in [1,65535]")
    if args.jobs < 1 or args.events < 1:
        raise ValueError("--jobs and --events must be positive")
    if args.multiplicity_audit_events < 0:
        raise ValueError("--multiplicity-audit-events must not be negative")
    if args.max_runtime_seconds < 60:
        raise ValueError("--max-runtime-seconds must be at least 60")
    if args.max_cpu_seconds < 60:
        raise ValueError("--max-cpu-seconds must be at least 60")
    if args.max_cpu_seconds > args.max_runtime_seconds:
        raise ValueError(
            "--max-cpu-seconds above --max-runtime-seconds makes the CPU guard "
            "unreachable; the wall backstop would always fire first"
        )

    tunes = tuple(args.tunes) if args.tunes else CAMPAIGN_TUNES
    if not 0 <= args.attempt < MAX_ATTEMPTS:
        raise ValueError(f"--attempt must be in [0,{MAX_ATTEMPTS})")
    commit = git_head(project_base)
    producer = args.producer_executable_sha256 or producer_sha256(project_base)
    if not SHA256.fullmatch(producer):
        raise ValueError("producer executable SHA-256 is malformed")

    # A retry renders only the jobs that failed, at the next attempt number.
    selected: set[tuple[str, int]] | None = None
    if args.only_jobs:
        selected = set()
        for token in args.only_jobs.split(","):
            token = token.strip()
            if not token:
                continue
            tune_name, _, index = token.partition(":")
            if tune_name not in tunes or not index.isdigit():
                raise ValueError(f"--only-jobs entry is malformed: {token!r}")
            selected.add((tune_name, int(index)))
        if not selected:
            raise ValueError("--only-jobs selected nothing")

    seeds: list[int] = []
    rows: list[str] = []
    for tune in tunes:
        card_sha = effective_card_sha256(
            card_for(project_base, tune, args.card_variant),
            args.events,
            args.pthat_min,
        )
        category = "medium" if tune == "MONASH" else "long"
        for logical_id in range(args.jobs):
            if selected is not None and (tune, logical_id) not in selected:
                continue
            seed = seed_for(
                tune, logical_id, args.attempt,
                campaign_ordinal=args.campaign_ordinal,
            )
            seeds.append(seed)
            rows.append(
                f"  {args.campaign},{args.campaign_ordinal},{tune},{logical_id},"
                f"primary,{args.attempt},{seed},{args.events},{category},"
                f"{args.pthat_min},{args.multiplicity_audit_events},{commit},"
                f"{card_sha},{producer},{args.card_variant}"
            )
    if not rows:
        raise ValueError("no jobs selected; nothing to render")

    if args.seed_ledger:
        ledger = args.seed_ledger.resolve()
        assert_seeds_unused(seeds, ledger)
        if args.burn_seeds:
            burn_seeds(
                seeds, ledger, f"{args.campaign} attempt{args.attempt}"
            )

    production_root = resolve_production_root(project_base)
    if str(production_root).startswith(str(project_base)):
        print(
            f"WARNING: production root is inside the checkout: "
            f"{production_root}",
            file=sys.stderr,
        )
        print(
            "         set HF_PRODUCTION_ROOT in "
            "config/dependencies.local.conf",
            file=sys.stderr,
        )
    logs = f"{production_root}/{args.campaign}/condor_logs"
    lines = [
        "universe = vanilla",
        f"executable = {project_base}/generation/submit/runCondorJob.sh",
        f"initialdir = {project_base}",
        "getenv = False",
        "request_cpus = 1",
        "request_memory = 4GB",
        "request_disk = 4GB",
        '+UseOS = "el9"',
        '+JobCategory = "$(CATEGORY)"',
        f"log = {logs}/$(TUNE)/job_$(LOGICAL_ID)_$(Cluster)_$(Process).log",
        f"output = {logs}/$(TUNE)/job_$(LOGICAL_ID)_$(Cluster)_$(Process).out",
        f"error = {logs}/$(TUNE)/job_$(LOGICAL_ID)_$(Cluster)_$(Process).err",
        "should_transfer_files = NO",
        "hold = True",
        "max_retries = 0",
        "on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)",
        # Liveness guard. on_exit_hold only fires when a job exits; the PYTHIA
        # junction-splitting hang never exits, so without this a wedged job
        # holds a slot indefinitely and is invisible to the failure path.
        (
            "periodic_hold = (JobStatus == 2) && "
            f"((RemoteUserCpu > {args.max_cpu_seconds}) || "
            f"((CurrentTime - EnteredCurrentStatus) > {args.max_runtime_seconds}))"
        ),
        (
            f'periodic_hold_reason = "{HANG_GUARD_MARKER} suspected generator '
            f'hang: cpu>{args.max_cpu_seconds}s or wall>'
            f'{args.max_runtime_seconds}s"'
        ),
        '+HFCampaign = "$(CAMPAIGN)"',
        "+HFCampaignOrdinal = $(CAMPAIGN_ORDINAL)",
        '+HFTune = "$(TUNE)"',
        "+HFLogicalId = $(LOGICAL_ID)",
        '+HFRole = "$(ROLE)"',
        "+HFAttempt = $(ATTEMPT)",
        "+HFSeed = $(SEED)",
        "+HFRequestedSuccesses = $(REQUESTED_SUCCESSES)",
        '+HFPTHat = "$(PTHAT)"',
        "+HFMultiplicityAuditEvents = $(MULT_AUDIT_EVENTS)",
        '+HFRepositoryCommit = "$(REPOSITORY_COMMIT)"',
        '+HFEffectiveCardSHA256 = "$(EFFECTIVE_CARD_SHA256)"',
        '+HFProducerExecutableSHA256 = "$(PRODUCER_EXECUTABLE_SHA256)"',
        '+HFCardVariant = "$(CARD_VARIANT)"',
        (
            "arguments = --campaign $(CAMPAIGN) $(CAMPAIGN_ORDINAL) "
            "$(TUNE) $(LOGICAL_ID) $(ROLE) $(ATTEMPT) $(SEED) "
            "$(REQUESTED_SUCCESSES) $(PTHAT) $(MULT_AUDIT_EVENTS) "
            "$(REPOSITORY_COMMIT) $(EFFECTIVE_CARD_SHA256) "
            "$(PRODUCER_EXECUTABLE_SHA256) $(CARD_VARIANT) "
            "$(Cluster) $(Process)"
        ),
        (
            "queue CAMPAIGN,CAMPAIGN_ORDINAL,TUNE,LOGICAL_ID,ROLE,ATTEMPT,"
            "SEED,REQUESTED_SUCCESSES,CATEGORY,PTHAT,MULT_AUDIT_EVENTS,"
            "REPOSITORY_COMMIT,EFFECTIVE_CARD_SHA256,"
            "PRODUCER_EXECUTABLE_SHA256,CARD_VARIANT from ("
        ),
        *rows,
        ")",
        "",
    ]
    write_once_or_identical(output_path, "\n".join(lines))
    print(
        f"PRODUCTION_SUBMIT_RENDERED rows={len(rows)} "
        f"attempt={args.attempt} output={output_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
