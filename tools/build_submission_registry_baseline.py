#!/usr/bin/env python3
"""Build a reviewed, immutable baseline of historical seed reservations.

The cross-checkout registry cannot infer campaigns created before the shared
registry existed.  This helper derives their burned seed domains from the
immutable campaign and seed-ledger bytes.  Historical overlaps are retained
and reported explicitly; they are evidence of past reuse, not permission to
reuse either interval again.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
from pathlib import Path


SAFE_CAMPAIGN = re.compile(r"^[A-Za-z0-9._-]+$")
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{number} is not an object")
        rows.append(value)
    return rows


def singleton_intervals(seeds: list[int]) -> list[list[int]]:
    return [[seed, seed] for seed in sorted(seeds)]


def campaign_reservation(directory: Path) -> dict:
    directory = directory.resolve()
    config_path = directory / "campaign.json"
    candidates_path = directory / "candidate_manifest.jsonl"
    ledger_path = directory / "seed_ledger.jsonl"
    for path in (config_path, candidates_path, ledger_path):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"campaign evidence is absent or a symlink: {path}")
    config = json.loads(config_path.read_text())
    candidates = load_jsonl(candidates_path)
    ledger = load_jsonl(ledger_path)
    campaign = config.get("campaign")
    ordinal = config.get("campaign_ordinal")
    if (
        not isinstance(campaign, str)
        or not SAFE_CAMPAIGN.fullmatch(campaign)
        or directory.name != campaign
        or isinstance(ordinal, bool)
        or not isinstance(ordinal, int)
        or not 1 <= ordinal <= 65_535
    ):
        raise ValueError(f"invalid campaign identity in {directory}")
    if any(row.get("campaign") != campaign for row in candidates + ledger):
        raise ValueError(f"mixed campaign identity in {directory}")
    seeds = [row.get("seed") for row in ledger]
    if any(
        isinstance(seed, bool)
        or not isinstance(seed, int)
        or not 1 <= seed <= 900_000_000
        for seed in seeds
    ):
        raise ValueError(f"invalid ledger seed in {directory}")
    if len(seeds) != len(set(seeds)):
        raise ValueError(f"duplicate seed inside historical ledger {directory}")
    candidate_allocations = {
        (
            row.get("tune"),
            row.get("logical_id"),
            row.get("attempt"),
            row.get("seed"),
        )
        for row in candidates
    }
    ledger_allocations = {
        (
            row.get("tune"),
            row.get("logical_id"),
            row.get("attempt"),
            row.get("seed"),
        )
        for row in ledger
    }
    if not candidate_allocations.issubset(ledger_allocations):
        raise ValueError(
            f"candidate allocation missing from historical ledger {directory}"
        )

    schema = config.get("schema")
    if schema == "hf_campaign_v1":
        slots = config.get(
            "candidate_slots",
            {"MONASH": 100, "JUNCTIONS": 200, "CLOSEPACKING": 200},
        )
        if (
            not isinstance(slots, dict)
            or set(slots) != set(TUNES)
            or any(
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 1
                for value in slots.values()
            )
        ):
            raise ValueError(f"invalid full-campaign slots in {directory}")
        attempts = config.get("max_attempts_per_logical_id")
        seed_base = config.get("seed_base")
        if (
            isinstance(attempts, bool)
            or not isinstance(attempts, int)
            or attempts < 1
            or isinstance(seed_base, bool)
            or not isinstance(seed_base, int)
        ):
            raise ValueError(f"invalid full seed reservation in {directory}")
        reserved_count = sum(slots.values()) * attempts
        last = seed_base + reserved_count - 1
        if seed_base < 1 or last > 900_000_000:
            raise ValueError(f"full seed reservation exceeds PYTHIA domain")
        intervals = [[seed_base, last]]
        policy = "contiguous_full_attempt_domain"
    elif schema == "hf_gate_b_pilot_campaign_v1":
        if len(candidates) != 9 or len(ledger) != 9:
            raise ValueError(
                f"Gate-B historical reservation is not exactly nine rows"
            )
        intervals = singleton_intervals(seeds)
        policy = "exact_manifest_seed_singletons"
    else:
        raise ValueError(f"unsupported historical campaign schema {schema!r}")

    return {
        "campaign": campaign,
        "campaign_ordinal": ordinal,
        "schema": schema,
        "reservation_policy": policy,
        "reserved_seed_intervals": intervals,
        "source": {
            "campaign_directory": str(directory),
            "campaign_json_sha256": sha256(config_path),
            "candidate_manifest_sha256": sha256(candidates_path),
            "seed_ledger_sha256": sha256(ledger_path),
            "ledger_rows": len(ledger),
        },
    }


def interval_overlaps(
    left: list[list[int]], right: list[list[int]]
) -> list[list[int]]:
    overlaps = []
    for left_first, left_last in left:
        for right_first, right_last in right:
            first = max(left_first, right_first)
            last = min(left_last, right_last)
            if first <= last:
                overlaps.append([first, last])
    return overlaps


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-identity", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--campaign-dir",
        type=Path,
        action="append",
        required=True,
        help="repeat once for every historical full or Gate-B campaign",
    )
    args = parser.parse_args()
    reviewer = args.reviewer.strip()
    if not reviewer or "PROJECT OWNER" in reviewer.upper():
        raise ValueError("reviewer is absent or a placeholder")
    reservations = [
        campaign_reservation(path) for path in args.campaign_dir
    ]
    reservations.sort(
        key=lambda row: (row["campaign_ordinal"], row["campaign"])
    )
    names = [row["campaign"] for row in reservations]
    ordinals = [row["campaign_ordinal"] for row in reservations]
    if len(names) != len(set(names)) or len(ordinals) != len(set(ordinals)):
        raise ValueError("historical campaign names and ordinals must be unique")

    overlaps = []
    for left_index, left in enumerate(reservations):
        for right in reservations[left_index + 1 :]:
            common = interval_overlaps(
                left["reserved_seed_intervals"],
                right["reserved_seed_intervals"],
            )
            if common:
                overlaps.append(
                    {
                        "campaign_a": left["campaign"],
                        "campaign_b": right["campaign"],
                        "overlap_intervals": common,
                        "disposition":
                            "historical_collision_burn_all_overlapping_seeds",
                    }
                )
    baseline = {
        "schema": "hf_submission_registry_baseline_v1",
        "repository_identity": args.repository_identity,
        "reviewer": reviewer,
        "created_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "policy": (
            "Every listed seed is permanently burned. Historical collisions "
            "are retained explicitly and never make a seed reusable."
        ),
        "historical_reservations": reservations,
        "documented_historical_overlaps": overlaps,
    }
    output = args.output.expanduser().resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"refusing to replace baseline: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(baseline, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    print(
        "SUBMISSION_REGISTRY_BASELINE_CREATED "
        f"campaigns={len(reservations)} overlaps={len(overlaps)} "
        f"sha256={sha256(output)} path={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
