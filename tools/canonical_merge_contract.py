#!/usr/bin/env python3
"""Validate the count/exposure contract consumed by canonical merging.

The first publication freeze contains 100 jobs per tune.  A later,
explicitly authorised superseding freeze may contain more.  This validator
therefore fixes the physics tune set and ten deterministic blocks, but derives
the equal per-tune count and exposure from the manifest instead of silently
assuming the first-stage 100-job size.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
BLOCK_COUNT = 10
MINIMUM_JOBS_PER_TUNE = 100
FIRST_STAGE_ROW_SCHEMA = "hf_canonical_raw_manifest_v2"
SUPERSEDING_ROW_SCHEMA = "hf_superseding_canonical_raw_manifest_v3"
HEX64 = frozenset("0123456789abcdef")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"manifest is absent or a symlink: {path}")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON at {path}:{number}") from error
        if not isinstance(row, dict):
            raise ValueError(f"manifest row is not an object at {path}:{number}")
        rows.append(row)
    return rows


def canonical_row(row: dict[str, Any]) -> str:
    return json.dumps(row, sort_keys=True, separators=(",", ":"))


def require_sha256(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in HEX64 for character in value)
    ):
        raise ValueError(f"{label} is not a lowercase SHA-256 digest")
    return value


def merge_campaign_identity(
    rows: list[dict[str, Any]], schema: str
) -> tuple[str, list[str]]:
    """Return the final campaign while preserving v3 leaf provenance.

    First-stage rows all belong to one campaign.  Superseding rows deliberately
    retain the campaign that produced each raw file and bind the union through
    ``final_campaign``.  Treating ``campaign`` as the union identity would
    either reject every valid expansion or erase the source provenance that
    makes an expansion auditable.
    """
    if schema == FIRST_STAGE_ROW_SCHEMA:
        campaigns = {row.get("campaign") for row in rows}
        if (
            len(campaigns) != 1
            or not isinstance(next(iter(campaigns)), str)
            or not next(iter(campaigns))
        ):
            raise ValueError("first-stage merge rows mix/omit campaign")
        return str(next(iter(campaigns))), [str(next(iter(campaigns)))]

    if schema != SUPERSEDING_ROW_SCHEMA:
        raise ValueError(f"unsupported canonical merge row schema: {schema!r}")

    final_campaigns = {row.get("final_campaign") for row in rows}
    final_ordinals = {row.get("final_campaign_ordinal") for row in rows}
    if (
        len(final_campaigns) != 1
        or not isinstance(next(iter(final_campaigns)), str)
        or not next(iter(final_campaigns))
        or len(final_ordinals) != 1
        or isinstance(next(iter(final_ordinals)), bool)
        or not isinstance(next(iter(final_ordinals)), int)
        or next(iter(final_ordinals)) < 1
    ):
        raise ValueError(
            "superseding merge rows mix/omit final campaign identity"
        )

    source_contracts: dict[str, tuple[Any, ...]] = {}
    source_tune_counts: dict[str, dict[str, int]] = {}
    for row in rows:
        source_campaign = row.get("campaign")
        source_prefix = row.get("source_production_prefix")
        source_slot = row.get("source_canonical_slot")
        if (
            not isinstance(source_campaign, str)
            or not source_campaign
            or source_prefix != source_campaign
            or isinstance(source_slot, bool)
            or not isinstance(source_slot, int)
            or source_slot < 0
        ):
            raise ValueError(
                "superseding merge row has invalid source campaign/slot"
            )
        contract = (
            require_sha256(
                row.get("source_manifest_sha256"),
                "source manifest checksum",
            ),
            require_sha256(
                row.get("source_freeze_summary_sha256"),
                "source freeze-summary checksum",
            ),
            require_sha256(
                row.get("source_freeze_seal_sha256"),
                "source freeze-seal checksum",
            ),
        )
        known = source_contracts.setdefault(source_campaign, contract)
        if known != contract:
            raise ValueError(
                "superseding rows disagree on a source-freeze identity"
            )
        tune = row.get("tune")
        if tune not in TUNES:
            raise ValueError("superseding source row has an unknown tune")
        counts = source_tune_counts.setdefault(
            source_campaign, {candidate: 0 for candidate in TUNES}
        )
        counts[str(tune)] += 1
    if len(source_contracts) < 2:
        raise ValueError(
            "superseding merge requires at least two sealed source freezes"
        )
    for source_campaign, counts in source_tune_counts.items():
        if min(counts.values()) < 1 or len(set(counts.values())) != 1:
            raise ValueError(
                "superseding source freeze has unequal tune exposure: "
                f"{source_campaign}={counts}"
            )
    return (
        str(next(iter(final_campaigns))),
        sorted(source_contracts),
    )


def validate(freeze_dir: Path) -> dict[str, Any]:
    if freeze_dir.is_symlink() or not freeze_dir.is_dir():
        raise ValueError(
            f"canonical freeze is absent or a symbolic link: {freeze_dir}"
        )
    freeze_dir = freeze_dir.resolve()
    central_path = freeze_dir / "canonical_manifest.jsonl"
    central = read_jsonl(central_path)
    if not central:
        raise ValueError("canonical merge manifest is empty")
    schemas = {row.get("schema") for row in central}
    if (
        len(schemas) != 1
        or not isinstance(next(iter(schemas)), str)
        or not next(iter(schemas))
    ):
        raise ValueError("canonical merge rows mix/omit schema")
    source_schema = str(next(iter(schemas)))
    campaign, source_campaigns = merge_campaign_identity(
        central, source_schema
    )

    by_tune: dict[str, list[dict[str, Any]]] = {tune: [] for tune in TUNES}
    for row in central:
        tune = row.get("tune")
        slot = row.get("canonical_slot")
        block = row.get("block")
        block_position = row.get("block_position")
        requested = row.get("requested_successes")
        if (
            tune not in by_tune
            or isinstance(slot, bool)
            or not isinstance(slot, int)
            or slot < 0
            or isinstance(block, bool)
            or not isinstance(block, int)
            or not 0 <= block < BLOCK_COUNT
            or isinstance(block_position, bool)
            or not isinstance(block_position, int)
            or block_position < 0
            or isinstance(requested, bool)
            or not isinstance(requested, int)
            or requested <= 0
        ):
            raise ValueError("canonical merge row has invalid tune/partition")
        by_tune[tune].append(row)

    tune_counts = {tune: len(rows) for tune, rows in by_tune.items()}
    if (
        len(set(tune_counts.values())) != 1
        or next(iter(tune_counts.values())) < MINIMUM_JOBS_PER_TUNE
    ):
        raise ValueError(
            "canonical merge requires equal N>=100 jobs for all tunes"
        )
    jobs_per_tune = next(iter(tune_counts.values()))
    if jobs_per_tune % BLOCK_COUNT != 0:
        raise ValueError("per-tune job count is not divisible by ten blocks")
    jobs_per_tune_per_block = jobs_per_tune // BLOCK_COUNT

    requested_values = {row["requested_successes"] for row in central}
    if len(requested_values) != 1:
        raise ValueError("canonical merge rows do not have equal exposure")
    successful_events_per_job = next(iter(requested_values))
    successful_events_per_tune = (
        jobs_per_tune * successful_events_per_job
    )

    central_identities: dict[tuple[str, int], str] = {}
    for tune, rows in by_tune.items():
        slots = {row["canonical_slot"] for row in rows}
        if slots != set(range(jobs_per_tune)):
            raise ValueError(f"canonical slots are not contiguous for {tune}")
        for row in rows:
            slot = row["canonical_slot"]
            if (
                row["block"] != slot % BLOCK_COUNT
                or row["block_position"] != slot // BLOCK_COUNT
            ):
                raise ValueError("canonical row partition arithmetic differs")
            identity = (tune, slot)
            if identity in central_identities:
                raise ValueError("duplicate canonical tune/slot identity")
            central_identities[identity] = canonical_row(row)

    observed_identities: set[tuple[str, int]] = set()
    block_hashes: dict[str, str] = {}
    for block in range(BLOCK_COUNT):
        path = freeze_dir / f"block_{block + 1:02d}.jsonl"
        rows = read_jsonl(path)
        block_hashes[path.name] = sha256(path)
        if len(rows) != len(TUNES) * jobs_per_tune_per_block:
            raise ValueError(f"block {block + 1} has the wrong row count")
        for tune in TUNES:
            tune_rows = [row for row in rows if row.get("tune") == tune]
            if len(tune_rows) != jobs_per_tune_per_block:
                raise ValueError(
                    f"block {block + 1} has unequal {tune} exposure"
                )
            if (
                sum(row["requested_successes"] for row in tune_rows)
                != successful_events_per_tune // BLOCK_COUNT
            ):
                raise ValueError(
                    f"block {block + 1} has unequal {tune} event exposure"
                )
        for row in rows:
            slot = row.get("canonical_slot")
            identity = (row.get("tune"), slot)
            if (
                row.get("block") != block
                or identity not in central_identities
                or canonical_row(row) != central_identities[identity]
                or identity in observed_identities
            ):
                raise ValueError(
                    f"block {block + 1} is not an exact disjoint partition"
                )
            observed_identities.add(identity)
    if observed_identities != set(central_identities):
        raise ValueError("ten-block union differs from canonical manifest")

    return {
        "schema": "hf_canonical_merge_contract_v1",
        "state": "PASS",
        "source_manifest_schema": source_schema,
        "campaign": campaign,
        "source_campaigns": source_campaigns,
        "tunes": list(TUNES),
        "block_count": BLOCK_COUNT,
        "jobs_per_tune": jobs_per_tune,
        "jobs_per_tune_per_block": jobs_per_tune_per_block,
        "successful_events_per_job": successful_events_per_job,
        "successful_events_per_tune": successful_events_per_tune,
        "canonical_manifest_sha256": sha256(central_path),
        "block_manifest_sha256": block_hashes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("freeze_dir", type=Path)
    parser.add_argument(
        "--shell-values",
        action="store_true",
        help="print N, N/10, and expected events as tab-separated integers",
    )
    args = parser.parse_args()
    report = validate(args.freeze_dir)
    if args.shell_values:
        print(
            report["jobs_per_tune"],
            report["jobs_per_tune_per_block"],
            report["successful_events_per_tune"],
            sep="\t",
        )
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
