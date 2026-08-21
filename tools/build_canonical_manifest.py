#!/usr/bin/env python3
"""Build the canonical manifest the analysis stage consumes.

Seven components read canonical_manifest.jsonl -- the merge, the analysis
submit, the statistics, the raw-manifest validator -- and until now nothing
wrote it. This walks a completed campaign and emits one row per promoted raw
file, in tune-major order with a contiguous canonical_slot per tune, which is
the order render_analysis_submit.py assumes.

It refuses to emit a partial manifest: every tune must have the same number of
promoted jobs and that number must divide into the ten analysis blocks, because
ratios are formed within block and the tunes are compared at matched
statistics. Use tools/campaign_status.py to see what is missing, and
tools/resubmit_held.py to fill it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from campaign import CAMPAIGN_TUNES, effective_pthat_min  # noqa: E402

RAW_NAME = re.compile(r"^hf_(?P<tune>[A-Za-z0-9_]+)_job(?P<job>\d+)\.root$")
BLOCKS = 10

# Validation/ValidateCanonicalRawManifest.C checks these against every row, so
# they are emitted rather than assumed. They are the same contract strings the
# producer embeds, which is what makes the check meaningful.
# Paths in the manifest are relative to the CAMPAIGN directory, not its
# parent: render_analysis_submit.py expects "raw/<TUNE>/hf_<TUNE>_jobNNN.root"
# for schema v2 and resolves it against the production root it is given, which
# is therefore <root>/<CAMPAIGN>.
RAW_SCHEMA = "hf_primary_ground_raw_v7"
ORIGIN_ALGORITHM = "signed_heavy_constituent_complete_mothers_unique_v4"
SELECTOR = "hard_trigger_primary_ground__primary_ground_associate_v1"
TUNE_ALLOWLIST_SCHEMA = "pythia_tune_difference_allowlist_v2"


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def sidecar_checksum(raw: Path) -> str | None:
    """Use the .sha256 the worker wrote rather than re-hashing hundreds of GB."""
    sidecar = raw.with_suffix(raw.suffix + ".sha256")
    if not sidecar.is_file():
        return None
    first = sidecar.read_text().split()
    return first[0] if first else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign")
    parser.add_argument("freeze_dir", type=Path)
    parser.add_argument(
        "--production-root", type=Path,
        default=Path(os.environ.get("HF_PRODUCTION_ROOT", "Production")),
    )
    parser.add_argument(
        "--tune", action="append", dest="tunes",
        help="repeatable; defaults to the canonical campaign order",
    )
    parser.add_argument(
        "--rehash", action="store_true",
        help="recompute checksums instead of trusting the .sha256 sidecars",
    )
    parser.add_argument(
        "--allow-partial", action="store_true",
        help="emit even if tunes are unequal (diagnostics only, not analysable)",
    )
    args = parser.parse_args()

    project_base = Path(__file__).resolve().parents[1]
    campaign_root = (args.production_root / args.campaign).resolve()
    raw_root = campaign_root / "raw"
    if not raw_root.is_dir():
        print(f"no raw directory: {raw_root}", file=sys.stderr)
        return 1

    found: dict[str, dict[int, Path]] = {}
    for raw in sorted(raw_root.glob("*/hf_*_job*.root")):
        match = RAW_NAME.match(raw.name)
        if not match:
            continue
        found.setdefault(match["tune"], {})[int(match["job"])] = raw

    # Canonical order, not alphabetical. tune_ordinal must agree with kTunes in
    # Validation/ValidateCanonicalRawManifest.C, and render_analysis_submit.py
    # reads tunes in first-appearance order, so the row order matters too.
    # Sorting alphabetically silently put CLOSEPACKING at ordinal 0 and every
    # row but JUNCTIONS was rejected.
    if args.tunes:
        tunes = tuple(args.tunes)
    else:
        tunes = tuple(t for t in CAMPAIGN_TUNES if t in found) + tuple(
            sorted(t for t in found if t not in CAMPAIGN_TUNES)
        )
    missing_tunes = [tune for tune in tunes if tune not in found]
    if missing_tunes:
        print(f"no promoted output for: {', '.join(missing_tunes)}", file=sys.stderr)
        return 1

    counts = {tune: len(found[tune]) for tune in tunes}
    per_tune = set(counts.values())
    if not args.allow_partial:
        if len(per_tune) != 1:
            print(f"tunes have unequal exposure: {counts}", file=sys.stderr)
            print(
                "the merge requires matched statistics; "
                "run tools/resubmit_held.py to fill the gaps",
                file=sys.stderr,
            )
            return 1
        jobs_per_tune = per_tune.pop()
        if jobs_per_tune % BLOCKS:
            print(
                f"jobs per tune ({jobs_per_tune}) must divide into "
                f"{BLOCKS} analysis blocks",
                file=sys.stderr,
            )
            return 1

    allowlist = project_base / "config/tune_difference_allowlist_v1.json"
    allowlist_sha = sha256(allowlist) if allowlist.is_file() else ""

    rows = []
    for tune in tunes:
        for slot, job in enumerate(sorted(found[tune])):
            raw = found[tune][job]
            digest = sha256(raw) if args.rehash else sidecar_checksum(raw)
            if not digest:
                print(
                    f"no checksum for {raw}; re-run with --rehash",
                    file=sys.stderr,
                )
                return 1
            validation = (
                campaign_root / "raw_validation" / tune
                / f"job{job:03d}"
            )
            attempts = sorted(validation.glob("attempt*")) if validation.is_dir() else []
            receipt = attempts[-1] / "receipt.json" if attempts else None
            log = attempts[-1] / "validate_raw_output.log" if attempts else None
            rows.append(
                {
                    "schema": "hf_canonical_raw_manifest_v2",
                    "campaign": args.campaign,
                    "campaign_ordinal": None,
                    "tune": tune,
                    "tune_ordinal": tunes.index(tune),
                    "logical_id": job,
                    "canonical_slot": slot,
                    "block": slot % BLOCKS,
                    "block_position": slot // BLOCKS,
                    "attempt": None,
                    "role": "primary",
                    "requested_successes": None,
                    "seed": None,
                    "raw_schema": RAW_SCHEMA,
                    "origin_algorithm": ORIGIN_ALGORITHM,
                    "selector": SELECTOR,
                    "tune_difference_allowlist_schema": TUNE_ALLOWLIST_SCHEMA,
                    "tune_difference_allowlist_sha256": allowlist_sha,
                    "effective_card_sha256": None,
                    "producer_executable_sha256": None,
                    "repository_commit": None,
                    "effective_pthat_min": None,
                    "multiplicity_audit_events": 0,
                    "attempt_receipt_path": None,
                    "raw_path": str(raw.relative_to(campaign_root)),
                    "raw_sha256": digest,
                    "raw_bytes": raw.stat().st_size,
                    "raw_validation_receipt_path": (
                        str(receipt.relative_to(campaign_root))
                        if receipt and receipt.is_file() else None
                    ),
                    "raw_validation_receipt_sha256": (
                        sha256(receipt) if receipt and receipt.is_file() else None
                    ),
                    "raw_validation_log_path": (
                        str(log.relative_to(campaign_root))
                        if log and log.is_file() else None
                    ),
                    "raw_validation_log_sha256": (
                        sha256(log) if log and log.is_file() else None
                    ),
                }
            )

    # requested_successes and seed come from the attempt metadata of whichever
    # attempt was promoted.
    metadata_root = campaign_root / "attempt_metadata"
    by_job: dict[tuple[str, int], dict] = {}
    for sidecar in sorted(metadata_root.glob("*/*.json")):
        try:
            payload = json.loads(sidecar.read_text())
        except (OSError, ValueError):
            continue
        if payload.get("producer_exit") != 0:
            continue
        payload["_sidecar_path"] = str(sidecar.relative_to(campaign_root))
        key = (str(payload.get("tune")), int(payload.get("logical_id", -1)))
        by_job[key] = payload
    for row in rows:
        payload = by_job.get((row["tune"], row["logical_id"]))
        if not payload:
            continue
        row["requested_successes"] = payload.get("requested_successes")
        row["seed"] = payload.get("seed")
        row["attempt"] = payload.get("attempt")
        row["campaign_ordinal"] = payload.get("campaign_ordinal")
        row["role"] = payload.get("role", "primary")
        row["effective_card_sha256"] = payload.get("effective_card_sha256")
        row["producer_executable_sha256"] = payload.get(
            "producer_executable_sha256"
        )
        row["repository_commit"] = payload.get("repository_commit")
        row["multiplicity_audit_events"] = payload.get(
            "multiplicity_audit_events", 0
        )
        override = str(payload.get("pthat_min_override", "NONE"))
        card = (
            project_base / "generation" / "cards"
            / f"pythiasettings_Hard_Low_ccbb_{row['tune']}.cmnd"
        )
        row["effective_pthat_min"] = (
            float(override) if override not in ("NONE", "", "None")
            else effective_pthat_min(card, None)
        )
        sidecar_path = payload.get("_sidecar_path")
        if sidecar_path:
            row["attempt_receipt_path"] = sidecar_path

    incomplete = [row for row in rows if row["requested_successes"] is None]
    if incomplete and not args.allow_partial:
        print(
            f"{len(incomplete)} rows have no matching attempt metadata",
            file=sys.stderr,
        )
        return 1

    args.freeze_dir.mkdir(parents=True, exist_ok=True)
    manifest = args.freeze_dir / "canonical_manifest.jsonl"
    block_paths = [
        args.freeze_dir / f"block_{block + 1:02d}.jsonl" for block in range(BLOCKS)
    ]
    # The freeze is write-once as a whole, so check every artifact before
    # writing any of them; a half-written freeze is worse than none.
    for artifact in (manifest, *block_paths):
        if artifact.exists():
            print(
                f"refusing to overwrite existing freeze artifact: {artifact}",
                file=sys.stderr,
            )
            return 1
    manifest.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n"
    )

    # The ten disjoint blocks every nonlinear quantity is formed inside before
    # the SEM across blocks is taken. Two components read these and nothing
    # wrote them:
    #
    #   merge_root_files.sh:191-192              one merge_one() per block
    #   tools/statistical_robustness.py:602-610  revalidates each block against
    #                                            the canonical rows
    #
    # The partition is canonical_slot % BLOCKS -- the same value already stored
    # per row as "block" above -- so the ten blocks are disjoint and exhaust the
    # manifest by construction. Each file carries the FULL manifest rows for its
    # block, in manifest order, serialised exactly as canonical_manifest.jsonl,
    # because statistical_robustness.py:609-610 compares the parsed file to
    #
    #   [row for row in rows if row["canonical_slot"] % 10 == block]
    #
    # by dict equality: any dropped field or reordering fails it. The trailing
    # -newline-per-row form is used rather than "\n".join(...) + "\n" so an
    # empty block yields an empty file rather than a stray blank line; for a
    # non-empty block the two are byte-identical.
    for block, path in enumerate(block_paths):
        path.write_text(
            "".join(
                json.dumps(row, sort_keys=True) + "\n"
                for row in rows
                if row["canonical_slot"] % BLOCKS == block
            )
        )
    # A freeze seal: one checksum that identifies the exact input set the
    # analysis ran on. The gate layer wrote this and the analysis still records
    # it, which is worth keeping -- it is how a plot is traced back to the
    # precise set of raw files behind it.
    manifest_sha = sha256(manifest)
    events = sum(int(row["requested_successes"] or 0) for row in rows)
    seal = args.freeze_dir / "freeze_seal.json"
    seal.write_text(
        json.dumps(
            {
                "schema": "hf_canonical_freeze_seal_v2",
                "campaign": args.campaign,
                "canonical_manifest_sha256": manifest_sha,
                "rows": len(rows),
                "tunes": list(tunes),
                "jobs_per_tune": len(rows) // len(tunes),
                "blocks": BLOCKS,
                "total_requested_successes": events,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print(
        f"CANONICAL_MANIFEST_WRITTEN {manifest} rows={len(rows)} "
        f"tunes={len(tunes)} events={events} sha256={manifest_sha}"
    )
    print(
        f"CANONICAL_BLOCKS_WRITTEN {args.freeze_dir} blocks={BLOCKS} "
        + " ".join(
            f"{path.name}={sum(1 for _ in path.read_text().splitlines() if _.strip())}"
            for path in block_paths
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
