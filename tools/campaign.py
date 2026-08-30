#!/usr/bin/env python3
"""Minimal campaign helpers: tunes, deterministic seeds, effective cards.

This replaces the campaign-manifest layer. It keeps the three things that
layer actually protected -- reproducible per-job seeds, a check that a seed
has never been used before, and a checksum of the card the worker really
runs -- and drops the artifact-authorisation machinery around them.

Deliberately *not* a schema. Job size and job count are arguments, not
frozen constants: they carry no physics, and freezing them previously forced
the same number to be restated in seven modules, where it drifted.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import os
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Tunes
#
# The three published configurations that production compares. There is no cap
# here on how many tunes may exist -- but note that the producer's event-ID
# still packs the tune ordinal into two bits and throws above three, so a fifth
# configuration needs that widened first.
# --------------------------------------------------------------------------

PUBLISHED_TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")

# What production runs.
CAMPAIGN_TUNES = PUBLISHED_TUNES

# What the tooling accepts if asked explicitly. Ruling R32 of 2026-08-30
# removed the fourth, optional tune, so the two sets now coincide. The name
# stays: the seed arithmetic below is written on it, and a later optional tune
# re-enters the tree here and nowhere else. MAX_CAMPAIGN_ORDINAL is derived
# from len(ALL_TUNES) and is unchanged at 79 by the removal -- the tune term
# shrinks by one TUNE_STRIDE, which does not cross a CAMPAIGN_STRIDE boundary.
ALL_TUNES = PUBLISHED_TUNES

# --------------------------------------------------------------------------
# Seeds
# --------------------------------------------------------------------------

SEED_BASE = 100_000_001
# Stride between CAMPAIGNS, keyed on the campaign ordinal. Added 2026-08-09 as
# seed_derivation_v2 (B15).
#
# v1 derived seeds from (tune, job, attempt) only, with no campaign term, so
# EVERY campaign at attempt 0 drew the same sequence starting at SEED_BASE.
# HF_RUN3_V1 at ordinal 3 tried to draw the seeds HF_SMOKE burned; B2's
# assert_seeds_unused caught it at render and nothing was written. The bug was
# latent only because no two campaigns had ever been rendered at attempt 0
# against a shared ledger before.
#
# Larger than TUNE_STRIDE * len(ALL_TUNES) so campaigns cannot overlap however
# many tunes a campaign uses.
CAMPAIGN_STRIDE = 10_000_000
# Stride between tunes. Larger than any plausible job count per tune, so two
# tunes cannot overlap however many jobs each is given.
TUNE_STRIDE = 1_000_000
# Stride between attempts of the same logical job. A retry must use a FRESH
# seed: the generator is deterministic given its seed, so re-running a wedged
# job with the same seed risks wedging again in exactly the same place. Events
# are independent draws, so a different seed is statistically equivalent.
ATTEMPT_STRIDE = 100_000
MAX_ATTEMPTS = TUNE_STRIDE // ATTEMPT_STRIDE  # 10
# PYTHIA's Rndm:seed accepts 1 .. 900000000.
PYTHIA_SEED_MAX = 900_000_000

# Identifies which formula produced a campaign's seeds. Recorded in the campaign
# record so a future reader can tell which derivation a dataset was drawn under
# without inferring it from the numbers.
SEED_DERIVATION_VERSION = "seed_derivation_v2"

# Highest campaign ordinal whose largest seed still fits the PYTHIA domain.
# Derived, not hardcoded, so it tracks any stride change:
#   max seed = SEED_BASE + ordinal*CAMPAIGN_STRIDE
#            + (len(ALL_TUNES)-1)*TUNE_STRIDE
#            + (MAX_ATTEMPTS-1)*ATTEMPT_STRIDE + (ATTEMPT_STRIDE-1)
MAX_CAMPAIGN_ORDINAL = (
    PYTHIA_SEED_MAX
    - SEED_BASE
    - (len(ALL_TUNES) - 1) * TUNE_STRIDE
    - (MAX_ATTEMPTS - 1) * ATTEMPT_STRIDE
    - (ATTEMPT_STRIDE - 1)
) // CAMPAIGN_STRIDE

# Marker written into periodic_hold_reason and matched by resubmit_held.py.
# Both sides import it: a held job is only auto-resubmitted when the guard
# put it there, and a literal string duplicated in two files would silently
# stop matching the first time either was reworded.
HANG_GUARD_MARKER = "HF_HANG_GUARD"


def seed_for(
    tune: str,
    job_index: int,
    attempt: int = 0,
    tunes: tuple[str, ...] = ALL_TUNES,
    *,
    campaign_ordinal: int,
) -> int:
    """Deterministic seed for one attempt of one job of one campaign.

    Same inputs always give the same seed, and no two
    (campaign_ordinal, tune, job, attempt) tuples share one, so a retry is
    reproducible without ever reusing a seed and two campaigns cannot collide.

    seed_derivation_v2. campaign_ordinal is keyword-only and has no default on
    purpose: v1 omitted the campaign term entirely and every campaign at
    attempt 0 drew the same sequence. A default here would let a caller
    silently reproduce that bug, so every call site must state the campaign.
    """
    if tune not in tunes:
        raise ValueError(f"unknown tune {tune!r}")
    if isinstance(campaign_ordinal, bool) or not isinstance(campaign_ordinal, int):
        raise ValueError(f"campaign_ordinal must be an int, got {campaign_ordinal!r}")
    if not 0 <= campaign_ordinal <= MAX_CAMPAIGN_ORDINAL:
        raise ValueError(
            f"campaign_ordinal {campaign_ordinal} outside "
            f"[0, {MAX_CAMPAIGN_ORDINAL}]; beyond this the seed leaves the "
            f"PYTHIA domain (max {PYTHIA_SEED_MAX}). Widen CAMPAIGN_STRIDE "
            f"planning rather than truncating the ordinal."
        )
    if not 0 <= attempt < MAX_ATTEMPTS:
        raise ValueError(f"attempt {attempt} outside [0, {MAX_ATTEMPTS})")
    if job_index < 0 or job_index >= ATTEMPT_STRIDE:
        raise ValueError(f"job_index {job_index} outside [0, {ATTEMPT_STRIDE})")
    seed = (
        SEED_BASE
        + campaign_ordinal * CAMPAIGN_STRIDE
        + tunes.index(tune) * TUNE_STRIDE
        + attempt * ATTEMPT_STRIDE
        + job_index
    )
    if not 1 <= seed <= PYTHIA_SEED_MAX:
        raise ValueError(f"seed {seed} outside the PYTHIA domain")
    return seed


def read_burned_seeds(ledger: Path) -> set[int]:
    """Read a flat ledger of already-used seeds. Blank lines and # comments ok."""
    if not ledger.is_file():
        return set()
    seeds: set[int] = set()
    for raw in ledger.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            seeds.add(int(line))
    return seeds


def assert_seeds_unused(seeds: list[int], ledger: Path) -> None:
    """Fail if any seed was used before, or is duplicated within this batch.

    A real duplicate-seed collision voided two pilot campaigns. That is the
    entire reason this check exists; it does not need to be larger than this.
    """
    duplicates = {seed for seed in seeds if seeds.count(seed) > 1}
    if duplicates:
        raise ValueError(f"seeds repeat within this batch: {sorted(duplicates)}")
    collisions = sorted(set(seeds) & read_burned_seeds(ledger))
    if collisions:
        raise ValueError(f"seeds already burned in {ledger}: {collisions}")


def burn_seeds(seeds: list[int], ledger: Path, note: str = "") -> None:
    """Append seeds to the ledger. Call at RENDER time, before condor_submit.

    The contract is render-time on purpose. This docstring previously said the
    opposite -- "call once a job has actually been submitted" -- while every
    caller burned at render. B2 required resolving that rather than deepening
    it: the behaviour was right and the docstring was wrong.

    Render-time burning means a rendered-but-unsubmitted .sub has already
    reserved its seeds, so re-rendering cannot hand out the same ones. Burning
    at submit time would leave a window in which two renders draw an identical
    batch and only the second submission discovers it. The cost of the chosen
    order is that an abandoned render permanently consumes seeds, which is the
    harmless direction: the ledger is append-only and seeds are not scarce.
    """
    assert_seeds_unused(seeds, ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    suffix = f"  # {note}" if note else ""
    with ledger.open("a") as handle:
        for seed in seeds:
            handle.write(f"{seed}{suffix}\n")


# --------------------------------------------------------------------------
# Storage
# --------------------------------------------------------------------------


def resolve_production_root(project_base: Path) -> Path:
    """Where production output goes, resolved without sourcing setupEnv.sh.

    Mirrors setupEnv.sh's precedence -- environment, then
    config/dependencies.local.conf, then config/dependencies.conf, then
    <checkout>/Production -- so tools that run outside a set-up shell (make
    targets, the submit renderer) agree with the worker about where data
    lives. They previously did not: the renderer read only the environment, so
    rendering from a plain shell sent Condor logs into the checkout while the
    worker wrote its data to the configured root.
    """
    from_env = os.environ.get("HF_PRODUCTION_ROOT")
    if from_env:
        return Path(from_env)
    pattern = re.compile(
        r'^\s*:\s*"\$\{HF_PRODUCTION_ROOT:=(?P<value>[^}"]*)\}"'
    )
    for name in ("dependencies.local.conf", "dependencies.conf"):
        conf = project_base / "config" / name
        if not conf.is_file():
            continue
        for line in conf.read_text().splitlines():
            match = pattern.match(line)
            if match:
                value = match.group("value").strip()
                if value:
                    return Path(value)
    return project_base / "Production"


# --------------------------------------------------------------------------
# Effective cards
#
# The worker rewrites the card line-by-line before running it. The checksum
# must be taken over what the worker actually runs, so this rewrite stays
# byte-identical to the worker's.
# --------------------------------------------------------------------------

PTHAT_OVERRIDES = {"0.5", "1.0", "2.0"}

# --------------------------------------------------------------------------
# Card variants
#
# A systematics variation is the nominal tune card with ONE setting changed.
# The worker derived the card name from the tune alone, so a variation card was
# unreachable. This resolves both cases in one place, so the renderer (which
# computes the effective sha the job is pinned to) and the worker (which
# materialises the card and re-checks that sha) cannot disagree about which
# file was meant.
#
# NONE resolves to exactly the nominal path, so the central campaign's
# rendering is byte-unchanged by the existence of this mechanism.
# --------------------------------------------------------------------------

CARD_VARIANT_NONE = "NONE"
# Lowercase only, so a variant token can never be mistaken for a TUNE name in
# a filename that contains both.
CARD_VARIANT_TOKEN = re.compile(r"^[a-z0-9_]+$")
CARD_STEM = "pythiasettings_Hard_Low_ccbb"


def resolve_card_path(
    project_base: Path, tune: str, card_variant: str | None
) -> Path:
    """The card file for one (tune, variant). The ONE definition of the layout."""
    cards = project_base / "generation" / "cards"
    if card_variant in (None, "", CARD_VARIANT_NONE):
        return cards / f"{CARD_STEM}_{tune}.cmnd"
    if not CARD_VARIANT_TOKEN.fullmatch(card_variant):
        raise ValueError(
            f"card variant must be lowercase [a-z0-9_]: {card_variant!r}"
        )
    return cards / "systematics" / f"{CARD_STEM}_{tune}__{card_variant}.cmnd"


def _replace_card_setting(
    content: bytes, setting: bytes, value: str, *, append_if_missing: bool
) -> bytes:
    replacement = setting + b" = " + value.encode("ascii")
    output: list[bytes] = []
    found = False
    for line in content.splitlines(keepends=True):
        if line.startswith(setting):
            found = True
            if line.endswith(b"\r\n"):
                output.append(replacement + b"\r\n")
            elif line.endswith(b"\n"):
                output.append(replacement + b"\n")
            else:
                output.append(replacement)
        else:
            output.append(line)
    rewritten = b"".join(output)
    if not found:
        if not append_if_missing:
            raise ValueError(
                f"required setting {setting.decode('ascii')} is absent from card"
            )
        # Matches: printf '\nSETTING = VALUE\n' >> CARD
        rewritten += b"\n" + replacement + b"\n"
    return rewritten


def effective_card_bytes(
    card: Path, requested_successes: int, pthat_min_override: str | None
) -> bytes:
    if requested_successes < 1:
        raise ValueError("requested_successes must be positive")
    content = _replace_card_setting(
        card.read_bytes(),
        b"Main:numberOfEvents",
        str(requested_successes),
        append_if_missing=True,
    )
    if pthat_min_override not in (None, "", "NONE"):
        if pthat_min_override not in PTHAT_OVERRIDES:
            raise ValueError(
                "pthat_min_override must be NONE, " + ", ".join(sorted(PTHAT_OVERRIDES))
            )
        content = _replace_card_setting(
            content, b"PhaseSpace:pTHatMin", pthat_min_override, append_if_missing=False
        )
    return content


def effective_card_sha256(
    card: Path, requested_successes: int, pthat_min_override: str | None
) -> str:
    return hashlib.sha256(
        effective_card_bytes(card, requested_successes, pthat_min_override)
    ).hexdigest()


def effective_pthat_min(card: Path, pthat_min_override: str | None) -> float:
    if pthat_min_override not in (None, "", "NONE"):
        return float(pthat_min_override)
    pattern = re.compile(
        rb"^PhaseSpace:pTHatMin\s*=\s*"
        rb"([-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?)"
    )
    values = [
        float(match.group(1))
        for match in (pattern.match(line) for line in card.read_bytes().splitlines())
        if match
    ]
    if not values or not math.isfinite(values[-1]) or values[-1] < 0.0:
        raise ValueError("card has no finite non-negative PhaseSpace:pTHatMin")
    return values[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    seeds = sub.add_parser("seeds", help="print the seeds for one tune")
    seeds.add_argument("tune", choices=ALL_TUNES)
    seeds.add_argument("--jobs", type=int, required=True)
    # Required, not defaulted: seed_derivation_v2 keys on the campaign, and a
    # default here would reproduce the v1 collision bug from the CLI.
    seeds.add_argument("--campaign-ordinal", type=int, required=True)
    seeds.add_argument("--attempt", type=int, default=0)
    seeds.add_argument("--ledger", type=Path)

    card = sub.add_parser("card-sha256", help="checksum the effective card")
    card.add_argument("card", type=Path)
    card.add_argument("--events", type=int, required=True)
    card.add_argument("--pthat-min", default="NONE")

    materialize = sub.add_parser(
        "materialize-card", help="write the effective card the worker will run"
    )
    materialize.add_argument("card", type=Path)
    materialize.add_argument("destination", type=Path)
    materialize.add_argument("--events", type=int, required=True)
    materialize.add_argument("--pthat-min", default="NONE")
    materialize.add_argument(
        "--expect-sha256",
        help="refuse to write unless the result matches the submitted checksum",
    )

    pthat = sub.add_parser(
        "effective-pthat-min", help="resolved PhaseSpace:pTHatMin for a card"
    )
    pthat.add_argument("card", type=Path)
    pthat.add_argument("--pthat-min", default="NONE")

    # The worker calls this rather than rebuilding the path in bash: a layout
    # duplicated in two languages is a layout that drifts.
    card_path = sub.add_parser(
        "card-path", help="the card file for one (tune, variant)"
    )
    card_path.add_argument("project_base", type=Path)
    card_path.add_argument("tune")
    card_path.add_argument("--card-variant", default=CARD_VARIANT_NONE)

    args = parser.parse_args()
    if args.command == "seeds":
        values = [
            seed_for(
                args.tune, index, args.attempt,
                campaign_ordinal=args.campaign_ordinal,
            )
            for index in range(args.jobs)
        ]
        if args.ledger:
            assert_seeds_unused(values, args.ledger)
        print("\n".join(str(value) for value in values))
    elif args.command == "card-sha256":
        print(effective_card_sha256(args.card, args.events, args.pthat_min))
    elif args.command == "materialize-card":
        content = effective_card_bytes(args.card, args.events, args.pthat_min)
        digest = hashlib.sha256(content).hexdigest()
        # The submit file recorded a checksum before the job was queued. If the
        # card materialised here differs, the worker would silently run a
        # configuration nobody authorised.
        if args.expect_sha256 and digest != args.expect_sha256:
            raise SystemExit(
                f"effective card sha256 {digest} does not match the submitted "
                f"{args.expect_sha256}"
            )
        args.destination.parent.mkdir(parents=True, exist_ok=True)
        args.destination.write_bytes(content)
        print(digest)
    elif args.command == "card-path":
        print(
            resolve_card_path(
                args.project_base.resolve(), args.tune, args.card_variant
            )
        )
    else:
        print(effective_pthat_min(args.card, args.pthat_min))
    return 0


if __name__ == "__main__":
    sys.exit(main())
