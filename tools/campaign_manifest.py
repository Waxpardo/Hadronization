#!/usr/bin/env python3
"""Create and validate immutable heavy-flavour campaign/seed manifests."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
GLOBAL_OFFSETS = {"MONASH": 0, "JUNCTIONS": 100, "CLOSEPACKING": 300}
SLOTS = {"MONASH": 100, "JUNCTIONS": 200, "CLOSEPACKING": 200}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def logical_seed(seed_base: int, max_attempts: int, tune: str, logical_id: int, attempt: int) -> int:
    if tune not in TUNES:
        raise ValueError(f"unknown tune {tune}")
    if logical_id < 0 or logical_id >= SLOTS[tune]:
        raise ValueError(f"logical ID {logical_id} outside {tune} candidate range")
    if attempt < 0 or attempt >= max_attempts:
        raise ValueError(f"attempt {attempt} outside [0,{max_attempts})")
    seed = seed_base + (GLOBAL_OFFSETS[tune] + logical_id) * max_attempts + attempt
    if not 1 <= seed <= 900_000_000:
        raise ValueError(f"seed {seed} outside PYTHIA domain")
    return seed


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def generate(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    campaign_dir = root / "campaigns" / args.campaign
    if campaign_dir.exists() and any(campaign_dir.iterdir()):
        raise SystemExit(f"refusing to alter nonempty campaign directory: {campaign_dir}")
    species = root / "config/heavy_flavour_species_v1.json"
    pairs = root / "config/heavy_flavour_pair_registry_v1.json"
    cards = {
        tune: root / "SimulationScripts" / f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
        for tune in TUNES
    }
    repository_commit = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    repository_dirty = bool(
        subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain"], text=True
        ).strip()
    )
    if repository_dirty and not args.allow_dirty:
        raise SystemExit("refusing to generate canonical campaign from dirty repository")
    campaign = {
        "schema": "hf_campaign_v1",
        "campaign": args.campaign,
        "campaign_ordinal": args.campaign_ordinal,
        "requested_successes_per_job": args.events,
        "seed_base": args.seed_base,
        "max_attempts_per_logical_id": args.max_attempts,
        "pythia_seed_domain": [1, 900_000_000],
        "candidate_slots": SLOTS,
        "global_offsets": GLOBAL_OFFSETS,
        "canonical_first_stage_jobs_per_tune": 100,
        "canonical_first_stage_successes_per_tune": 100 * args.events,
        "species_registry_sha256": sha256(species),
        "pair_registry_sha256": sha256(pairs),
        "card_sha256": {tune: sha256(path) for tune, path in cards.items()},
        "selector": "hard_trigger_primary_ground__primary_ground_associate_v1",
        "raw_schema": "hf_primary_ground_raw_v3",
        "block_count": 10,
        "repository_commit": repository_commit,
        "repository_dirty_at_generation": repository_dirty,
    }
    candidates = []
    seeds = set()
    for tune in TUNES:
        for logical_id in range(SLOTS[tune]):
            role = "primary" if logical_id < 100 else "reserve"
            seed = logical_seed(args.seed_base, args.max_attempts, tune, logical_id, 0)
            if seed in seeds:
                raise AssertionError(f"seed collision {seed}")
            seeds.add(seed)
            candidates.append(
                {
                    "campaign": args.campaign,
                    "campaign_ordinal": args.campaign_ordinal,
                    "tune": tune,
                    "logical_id": logical_id,
                    "global_candidate_ordinal": GLOBAL_OFFSETS[tune] + logical_id,
                    "role": role,
                    "attempt": 0,
                    "seed": seed,
                    "requested_successes": args.events,
                    "stable_name": f"hf_{tune}_job{logical_id:03d}.root",
                }
            )
    campaign_text = json.dumps(campaign, indent=2, sort_keys=True) + "\n"
    candidate_text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in candidates)
    ledger_text = "".join(
        json.dumps(
            {
                "campaign": row["campaign"],
                "tune": row["tune"],
                "logical_id": row["logical_id"],
                "attempt": row["attempt"],
                "seed": row["seed"],
                "allocation": "initial",
            },
            sort_keys=True,
        )
        + "\n"
        for row in candidates
    )
    atomic_write(campaign_dir / "campaign.json", campaign_text)
    atomic_write(campaign_dir / "candidate_manifest.jsonl", candidate_text)
    atomic_write(campaign_dir / "seed_ledger.jsonl", ledger_text)
    print(f"generated {len(candidates)} candidates and {len(seeds)} unique seeds in {campaign_dir}")
    return validate_campaign(campaign_dir)


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def validate_campaign(campaign_dir: Path) -> int:
    config = json.loads((campaign_dir / "campaign.json").read_text())
    candidates = load_jsonl(campaign_dir / "candidate_manifest.jsonl")
    ledger = load_jsonl(campaign_dir / "seed_ledger.jsonl")
    expected = sum(SLOTS.values())
    if len(candidates) != expected:
        raise ValueError(f"candidate count {len(candidates)} != {expected}")
    identities = {(row["tune"], row["logical_id"], row["attempt"]) for row in candidates}
    if len(identities) != expected:
        raise ValueError("duplicate candidate identity")
    seeds = [int(row["seed"]) for row in ledger]
    if len(seeds) != len(set(seeds)):
        raise ValueError("duplicate allocated seed")
    if any(seed < 1 or seed > 900_000_000 for seed in seeds):
        raise ValueError("seed outside PYTHIA domain")
    for tune in TUNES:
        rows = [row for row in candidates if row["tune"] == tune]
        if len(rows) != SLOTS[tune]:
            raise ValueError(f"wrong slot count for {tune}")
        for row in rows:
            expected_seed = logical_seed(
                config["seed_base"], config["max_attempts_per_logical_id"],
                tune, row["logical_id"], row["attempt"]
            )
            if row["seed"] != expected_seed:
                raise ValueError(f"seed mapping mismatch: {row}")
    print(
        f"campaign valid: candidates={len(candidates)} allocations={len(ledger)} "
        f"unique_seeds={len(set(seeds))}"
    )
    return 0


def validate(args: argparse.Namespace) -> int:
    return validate_campaign(args.campaign_dir.resolve())


def allocate_retry(args: argparse.Namespace) -> int:
    campaign_dir = args.campaign_dir.resolve()
    config = json.loads((campaign_dir / "campaign.json").read_text())
    ledger_path = campaign_dir / "seed_ledger.jsonl"
    lock_path = campaign_dir / ".seed_ledger.lock"
    lock_path.touch(exist_ok=True)
    with lock_path.open("r+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        ledger = load_jsonl(ledger_path)
        attempts = [
            int(row["attempt"]) for row in ledger
            if row["tune"] == args.tune and int(row["logical_id"]) == args.logical_id
        ]
        attempt = max(attempts, default=-1) + 1
        seed = logical_seed(
            config["seed_base"], config["max_attempts_per_logical_id"],
            args.tune, args.logical_id, attempt
        )
        if any(int(row["seed"]) == seed for row in ledger):
            raise ValueError(f"seed collision for {seed}")
        row = {
            "campaign": config["campaign"],
            "tune": args.tune,
            "logical_id": args.logical_id,
            "attempt": attempt,
            "seed": seed,
            "allocation": "retry",
            "reason": args.reason,
        }
        with ledger_path.open("a") as stream:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    print(json.dumps(row, sort_keys=True))
    return 0


def authorize(args: argparse.Namespace) -> int:
    campaign_dir = args.campaign_dir.resolve()
    candidates = load_jsonl(campaign_dir / "candidate_manifest.jsonl")
    ledger = load_jsonl(campaign_dir / "seed_ledger.jsonl")
    candidate = next(
        (
            row
            for row in candidates
            if row["tune"] == args.tune
            and int(row["logical_id"]) == args.logical_id
        ),
        None,
    )
    allocation = next(
        (
            row
            for row in ledger
            if row["tune"] == args.tune
            and int(row["logical_id"]) == args.logical_id
            and int(row["attempt"]) == args.attempt
            and int(row["seed"]) == args.seed
        ),
        None,
    )
    if candidate is None or allocation is None:
        raise ValueError("logical attempt/seed is not manifest and ledger authorized")
    if candidate["campaign"] != args.campaign or candidate["role"] != args.role:
        raise ValueError("campaign or role differs from candidate manifest")
    if int(candidate["requested_successes"]) != args.requested_successes:
        raise ValueError("requested success count differs from candidate manifest")
    print(
        "CAMPAIGN_ALLOCATION_AUTHORIZED "
        f"campaign={args.campaign} tune={args.tune} logical_id={args.logical_id} "
        f"attempt={args.attempt} seed={args.seed}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.set_defaults(root=Path(__file__).resolve().parents[1])
    subparsers = parser.add_subparsers(required=True)
    create = subparsers.add_parser("generate")
    create.add_argument("--root", type=Path, default=parser.get_default("root"))
    create.add_argument("--campaign", default="HF_100M_primaryGround_ccbb_v1")
    create.add_argument("--campaign-ordinal", type=int, default=1)
    create.add_argument("--events", type=int, default=1_000_000)
    create.add_argument("--seed-base", type=int, default=100_000_001)
    create.add_argument("--max-attempts", type=int, default=1000)
    create.add_argument("--allow-dirty", action="store_true")
    create.set_defaults(function=generate)
    check = subparsers.add_parser("validate")
    check.add_argument("campaign_dir", type=Path)
    check.set_defaults(function=validate)
    retry = subparsers.add_parser("allocate-retry")
    retry.add_argument("campaign_dir", type=Path)
    retry.add_argument("tune", choices=TUNES)
    retry.add_argument("logical_id", type=int)
    retry.add_argument("--reason", required=True)
    retry.set_defaults(function=allocate_retry)
    authorization = subparsers.add_parser("authorize")
    authorization.add_argument("campaign_dir", type=Path)
    authorization.add_argument("campaign")
    authorization.add_argument("tune", choices=TUNES)
    authorization.add_argument("logical_id", type=int)
    authorization.add_argument("role", choices=("primary", "reserve", "pilot"))
    authorization.add_argument("attempt", type=int)
    authorization.add_argument("seed", type=int)
    authorization.add_argument("requested_successes", type=int)
    authorization.set_defaults(function=authorize)
    args = parser.parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
