#!/usr/bin/env python3
"""Freeze and validate the exact equal-event canonical and block manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
CANONICAL_SLOTS = 100
BLOCKS = 10
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


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


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def freeze(args: argparse.Namespace) -> int:
    campaign_dir = args.campaign_dir.resolve()
    production_root = args.production_root.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"refusing to alter nonempty freeze directory: {output_dir}")

    campaign = json.loads((campaign_dir / "campaign.json").read_text())
    current_commit = subprocess.check_output(
        ["git", "-C", str(REPOSITORY_ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    tracked_dirty = bool(
        subprocess.check_output(
            [
                "git",
                "-C",
                str(REPOSITORY_ROOT),
                "status",
                "--porcelain",
                "--untracked-files=no",
            ],
            text=True,
        ).strip()
    )
    if tracked_dirty:
        raise SystemExit("refusing to freeze from a tracked-dirty repository")
    if campaign.get("repository_dirty_at_generation") is not False:
        raise ValueError("campaign was not generated from a clean repository")
    ancestry = subprocess.run(
        [
            "git",
            "-C",
            str(REPOSITORY_ROOT),
            "merge-base",
            "--is-ancestor",
            campaign["repository_commit"],
            current_commit,
        ]
    )
    if ancestry.returncode != 0:
        raise ValueError(
            "campaign implementation commit is not an ancestor of freeze checkout"
        )
    candidates = read_jsonl(campaign_dir / "candidate_manifest.jsonl")
    ledger = read_jsonl(campaign_dir / "seed_ledger.jsonl")
    candidate_lookup = {
        (row["tune"], int(row["logical_id"])): row for row in candidates
    }
    ledger_lookup = {
        (row["tune"], int(row["logical_id"]), int(row["attempt"])): row
        for row in ledger
    }
    choices: dict[tuple[str, int], dict] = {}
    if args.selection:
        for row in json.loads(args.selection.read_text()):
            key = (row["tune"], int(row["canonical_slot"]))
            if key in choices:
                raise ValueError(f"duplicate explicit selection {key}")
            choices[key] = row

    rows: list[dict] = []
    for tune in TUNES:
        for slot in range(CANONICAL_SLOTS):
            choice = choices.get(
                (tune, slot),
                {
                    "tune": tune,
                    "canonical_slot": slot,
                    "logical_id": slot,
                    "attempt": 0,
                    "reason": "primary_initial_allocation",
                    "approval": "predeclared_primary",
                },
            )
            logical_id = int(choice["logical_id"])
            attempt = int(choice["attempt"])
            candidate = candidate_lookup.get((tune, logical_id))
            allocation = ledger_lookup.get((tune, logical_id, attempt))
            if candidate is None or allocation is None:
                raise ValueError(f"selection is not ledger-authorized: {choice}")
            role = candidate["role"]
            if logical_id >= CANONICAL_SLOTS and role != "reserve":
                raise ValueError(f"replacement is not a declared reserve: {choice}")
            raw_relative = Path("raw") / tune / f"hf_{tune}_job{logical_id:03d}.root"
            raw_path = production_root / raw_relative
            if not raw_path.is_file() or raw_path.stat().st_size == 0:
                raise FileNotFoundError(f"missing canonical raw output: {raw_path}")
            checksum_path = Path(f"{raw_path}.sha256")
            if not checksum_path.is_file():
                raise FileNotFoundError(f"missing output checksum: {checksum_path}")
            recorded_sha = checksum_path.read_text().split()[0]
            if args.verify_checksums:
                actual_sha = digest(raw_path)
                if actual_sha != recorded_sha:
                    raise ValueError(f"checksum mismatch for {raw_path}")
            row = {
                "schema": "hf_canonical_raw_manifest_v1",
                "campaign": campaign["campaign"],
                "campaign_ordinal": campaign["campaign_ordinal"],
                "tune": tune,
                "canonical_slot": slot,
                "block": slot % BLOCKS,
                "logical_id": logical_id,
                "role": role,
                "attempt": attempt,
                "seed": int(allocation["seed"]),
                "requested_successes": campaign["requested_successes_per_job"],
                "raw_path": raw_relative.as_posix(),
                "raw_sha256": recorded_sha,
                "selection_reason": choice["reason"],
                "selection_approval": choice["approval"],
            }
            rows.append(row)

    output_dir.mkdir(parents=True, exist_ok=True)
    canonical_text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    atomic_write(output_dir / "canonical_manifest.jsonl", canonical_text)
    canonical_sha = hashlib.sha256(canonical_text.encode()).hexdigest()
    for block in range(BLOCKS):
        block_rows = [row for row in rows if row["block"] == block]
        block_text = "".join(
            json.dumps(row, sort_keys=True) + "\n" for row in block_rows
        )
        atomic_write(output_dir / f"block_{block + 1:02d}.jsonl", block_text)
    summary = {
        "schema": "hf_canonical_freeze_summary_v1",
        "campaign": campaign["campaign"],
        "canonical_manifest_sha256": canonical_sha,
        "jobs_per_tune": CANONICAL_SLOTS,
        "successful_events_per_job": campaign["requested_successes_per_job"],
        "successful_events_per_tune": (
            CANONICAL_SLOTS * campaign["requested_successes_per_job"]
        ),
        "block_count": BLOCKS,
        "jobs_per_tune_per_block": CANONICAL_SLOTS // BLOCKS,
        "selection_file": str(args.selection.resolve()) if args.selection else None,
        "repository_commit_at_freeze": current_commit,
        "repository_implementation_commit": campaign["repository_commit"],
        "raw_schema": campaign["raw_schema"],
        "selector": campaign["selector"],
        "species_registry_sha256": campaign["species_registry_sha256"],
        "pair_registry_sha256": campaign["pair_registry_sha256"],
        "card_sha256": campaign["card_sha256"],
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write(
        output_dir / "freeze_summary.json",
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
    )
    return validate_directory(output_dir)


def validate_directory(directory: Path) -> int:
    rows = read_jsonl(directory / "canonical_manifest.jsonl")
    if len(rows) != len(TUNES) * CANONICAL_SLOTS:
        raise ValueError(f"canonical row count {len(rows)} is not 300")
    identities = {
        (row["tune"], int(row["canonical_slot"])) for row in rows
    }
    if len(identities) != len(rows):
        raise ValueError("duplicate canonical tune/slot")
    paths = [row["raw_path"] for row in rows]
    seeds = [int(row["seed"]) for row in rows]
    if len(paths) != len(set(paths)):
        raise ValueError("duplicate canonical raw path")
    if len(seeds) != len(set(seeds)):
        raise ValueError("duplicate canonical seed")
    union: list[dict] = []
    for block in range(BLOCKS):
        block_rows = read_jsonl(directory / f"block_{block + 1:02d}.jsonl")
        for tune in TUNES:
            tune_rows = [row for row in block_rows if row["tune"] == tune]
            if len(tune_rows) != CANONICAL_SLOTS // BLOCKS:
                raise ValueError(f"block {block + 1} has wrong {tune} count")
        if any(int(row["block"]) != block for row in block_rows):
            raise ValueError(f"block label mismatch in block {block + 1}")
        union.extend(block_rows)
    canonical_keys = {
        (row["tune"], int(row["canonical_slot"]), row["raw_sha256"])
        for row in rows
    }
    union_keys = {
        (row["tune"], int(row["canonical_slot"]), row["raw_sha256"])
        for row in union
    }
    if canonical_keys != union_keys or len(union) != len(rows):
        raise ValueError("block union is not exactly the canonical manifest")
    for tune in TUNES:
        tune_rows = [row for row in rows if row["tune"] == tune]
        if len(tune_rows) != CANONICAL_SLOTS:
            raise ValueError(f"wrong canonical job count for {tune}")
        events = sum(int(row["requested_successes"]) for row in tune_rows)
        if events < 100_000_000:
            raise ValueError(f"{tune} has fewer than 100M successful events")
    print(
        "CANONICAL_MANIFEST_VALID "
        f"rows={len(rows)} unique_seeds={len(set(seeds))} blocks={BLOCKS}"
    )
    return 0


def validate(args: argparse.Namespace) -> int:
    return validate_directory(args.directory.resolve())


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    freeze_parser = subparsers.add_parser("freeze")
    freeze_parser.add_argument("campaign_dir", type=Path)
    freeze_parser.add_argument("production_root", type=Path)
    freeze_parser.add_argument("output_dir", type=Path)
    freeze_parser.add_argument("--selection", type=Path)
    freeze_parser.add_argument(
        "--verify-checksums", action=argparse.BooleanOptionalAction, default=True
    )
    freeze_parser.set_defaults(function=freeze)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("directory", type=Path)
    validate_parser.set_defaults(function=validate)
    args = parser.parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
