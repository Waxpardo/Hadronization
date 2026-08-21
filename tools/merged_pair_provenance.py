#!/usr/bin/env python3
"""Write and validate immutable provenance for a canonical merged pair set."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from campaign import PUBLISHED_TUNES  # noqa: E402

TUNES = PUBLISHED_TUNES
HEX40 = re.compile(r"[0-9a-f]{40}")
ROOT_INVENTORY = "merged_pair_checksums.json"
PROVENANCE = "merge_provenance.json"
SOURCE_MANIFEST = "source_manifest.jsonl"
EXPECTED_AUXILIARY = {
    "merge.log",
    ROOT_INVENTORY,
    PROVENANCE,
    SOURCE_MANIFEST,
}


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def optional_sha256(path: Path) -> str | None:
    """Digest optional recorded provenance without weakening the required seal.

    No current producer writes canonical_raw_validation_receipt.json.
    build_canonical_manifest.py writes freeze_seal.json, so its absence remains fatal.
    """
    return sha256(path) if path.is_file() else None


def expected_pair_filenames(checkout: Path) -> set[str]:
    header = (
        checkout / "AnalysisScripts" / "GeneratedPairRegistry.h"
    ).read_text()
    names = set(re.findall(r'"([^"]+\.root)"', header))
    declared = re.search(
        r"std::array<PairDefinition,\s*([0-9]+)>", header
    )
    if not declared or int(declared.group(1)) != len(names):
        raise ValueError("cannot establish pair registry file set")
    return names


def root_inventory(directory: Path, expected: set[str]) -> list[dict]:
    values = []
    for name in sorted(expected):
        path = directory / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size <= 0:
            raise ValueError(f"merged pair file is absent/invalid: {path}")
        values.append(
            {
                "path": name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return values


def source_manifest_scope(
    manifest: Path, tune: str, input_count: int
) -> dict:
    rows = [
        json.loads(line)
        for line in manifest.read_text().splitlines()
        if line.strip()
    ]
    tune_counts = {
        candidate: sum(row.get("tune") == candidate for row in rows)
        for candidate in TUNES
    }
    if (
        len(rows) != len(TUNES) * input_count
        or set(row.get("tune") for row in rows) != set(TUNES)
        or any(count != input_count for count in tune_counts.values())
    ):
        raise ValueError(
            "all-tune source manifest does not contain equal selected "
            "subsets"
        )
    return {
        "source_manifest_scope":
            "all_tunes_with_explicit_tune_filter_v1",
        "source_manifest_total_rows": len(rows),
        "source_manifest_tune_counts": tune_counts,
        "selected_tune": tune,
        "selected_tune_input_file_count": input_count,
    }


def expected_provenance(
    directory: Path,
    manifest: Path,
    tune: str,
    input_count: int,
    checkout: Path,
    analysis_report: Path,
    freeze_dir: Path,
) -> dict:
    report = json.loads(analysis_report.read_text())
    canonical_manifest = freeze_dir / "canonical_manifest.jsonl"
    if (
        report.get("schema") != "hf_analysis_output_validation_v3"
        or report.get("status") != "PASS"
        or report.get("canonical_manifest_sha256")
        != sha256(canonical_manifest)
        or report.get("validated_output_count")
        != report.get("canonical_manifest_rows")
        or report.get("missing_output_count") != 0
    ):
        raise ValueError("canonical analysis validation report is not final PASS")
    provenance = {
        "schema": "hf_merged_pair_directory_provenance_v2",
        "status": "PASS",
        "tune": tune,
        "source_manifest": SOURCE_MANIFEST,
        "source_manifest_sha256": sha256(manifest),
        "merge_input_file_count": input_count,
        "pair_file_count": len(expected_pair_filenames(checkout)),
        "analysis_output_validation_sha256": sha256(analysis_report),
        "analysis_commit": report["analysis_commit"],
        "analysis_macro_sha256": report["analysis_macro_sha256"],
        "canonical_freeze_seal_sha256": sha256(
            freeze_dir / "freeze_seal.json"
        ),
        "canonical_raw_validation_receipt_sha256": optional_sha256(
            freeze_dir / "canonical_raw_validation_receipt.json"
        ),
    }
    provenance.update(source_manifest_scope(manifest, tune, input_count))
    return provenance


def validate_common(
    directory: Path,
    manifest: Path,
    tune: str,
    input_count: int,
    checkout: Path,
    analysis_report: Path,
    freeze_dir: Path,
) -> tuple[dict, list[dict]]:
    if tune not in TUNES or isinstance(input_count, bool) or input_count <= 0:
        raise ValueError("invalid merged tune/input-count contract")
    source_manifest_scope(manifest, tune, input_count)
    expected_roots = expected_pair_filenames(checkout)
    actual_entries = {path.name for path in directory.iterdir()}
    expected_entries = expected_roots | EXPECTED_AUXILIARY
    if actual_entries != expected_entries:
        raise ValueError(
            f"merged directory file set differs: "
            f"missing={sorted(expected_entries - actual_entries)} "
            f"extra={sorted(actual_entries - expected_entries)}"
        )
    if any(path.is_symlink() for path in directory.iterdir()):
        raise ValueError(f"merged directory contains a symlink: {directory}")
    if (directory / SOURCE_MANIFEST).read_bytes() != manifest.read_bytes():
        raise ValueError("copied source manifest bytes differ")
    merge_log = (directory / "merge.log").read_text()
    if (
        merge_log.count("CANONICAL_MERGE_SUMMARY") != 1
        or "CANONICAL_MERGE_ERROR" in merge_log
        or re.search(
            r"segmentation violation|Break +segmentation|cling JIT session error",
            merge_log,
        )
    ):
        raise ValueError("merge log does not contain one clean completion marker")
    expected_prov = expected_provenance(
        directory,
        manifest,
        tune,
        input_count,
        checkout,
        analysis_report,
        freeze_dir,
    )
    provenance = json.loads((directory / PROVENANCE).read_text())
    for key, value in expected_prov.items():
        if provenance.get(key) != value:
            raise ValueError(
                f"merged provenance {key} differs: "
                f"{provenance.get(key)!r} != {value!r}"
            )
    merge_commit = provenance.get("repository_commit")
    if not isinstance(merge_commit, str) or not HEX40.fullmatch(merge_commit):
        raise ValueError("merged provenance repository commit is invalid")
    current_commit = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    ancestry = subprocess.run(
        [
            "git",
            "-C",
            str(checkout),
            "merge-base",
            "--is-ancestor",
            merge_commit,
            current_commit,
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if ancestry.returncode != 0:
        raise ValueError("merge implementation commit is absent/not an ancestor")
    for relative, field in (
        (
            "merging/MergeCanonicalAnalysis.C",
            "merge_canonical_macro_sha256",
        ),
        (
            "merging/MergeAnalysisObjects.C",
            "merge_objects_macro_sha256",
        ),
    ):
        committed = subprocess.check_output(
            ["git", "-C", str(checkout), "show", f"{merge_commit}:{relative}"]
        )
        if hashlib.sha256(committed).hexdigest() != provenance.get(field):
            raise ValueError(f"merged provenance checksum differs for {relative}")
    inventory_document = json.loads((directory / ROOT_INVENTORY).read_text())
    inventory = root_inventory(directory, expected_roots)
    expected_inventory = {
        "schema": "hf_merged_pair_checksum_inventory_v1",
        "pair_file_count": len(expected_roots),
        "files": inventory,
    }
    if inventory_document != expected_inventory:
        raise ValueError("merged ROOT checksum inventory is stale")
    return provenance, inventory


def write(args: argparse.Namespace) -> int:
    directory = args.directory.resolve()
    manifest = args.manifest.resolve()
    checkout = args.checkout.resolve()
    analysis_report = args.analysis_report.resolve()
    freeze_dir = args.freeze_dir.resolve()
    expected_roots = expected_pair_filenames(checkout)
    actual_roots = {
        path.name
        for path in directory.iterdir()
        if path.is_file() and path.suffix == ".root"
    }
    if actual_roots != expected_roots:
        raise ValueError("cannot provenance an incomplete/extra merged ROOT set")
    for name in (SOURCE_MANIFEST, PROVENANCE, ROOT_INVENTORY):
        if (directory / name).exists():
            raise ValueError(f"refusing to overwrite merged provenance {name}")
    (directory / SOURCE_MANIFEST).write_bytes(manifest.read_bytes())
    provenance = expected_provenance(
        directory,
        manifest,
        args.tune,
        args.input_count,
        checkout,
        analysis_report,
        freeze_dir,
    )
    provenance["repository_commit"] = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    provenance["merge_canonical_macro_sha256"] = sha256(
        checkout / "merging/MergeCanonicalAnalysis.C"
    )
    provenance["merge_objects_macro_sha256"] = sha256(
        checkout / "merging/MergeAnalysisObjects.C"
    )
    provenance["created_utc"] = datetime.now(timezone.utc).isoformat()
    (directory / PROVENANCE).write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n"
    )
    inventory = {
        "schema": "hf_merged_pair_checksum_inventory_v1",
        "pair_file_count": len(expected_roots),
        "files": root_inventory(directory, expected_roots),
    }
    (directory / ROOT_INVENTORY).write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n"
    )
    validate_common(
        directory,
        manifest,
        args.tune,
        args.input_count,
        checkout,
        analysis_report,
        freeze_dir,
    )
    print(
        "MERGED_PAIR_PROVENANCE_WRITTEN "
        f"tune={args.tune} inputs={args.input_count} files={len(expected_roots)}"
    )
    return 0


def validate(args: argparse.Namespace) -> int:
    directory = args.directory.resolve()
    provenance, inventory = validate_common(
        directory,
        args.manifest.resolve(),
        args.tune,
        args.input_count,
        args.checkout.resolve(),
        args.analysis_report.resolve(),
        args.freeze_dir.resolve(),
    )
    print(
        "MERGED_PAIR_DIRECTORY_VALID "
        f"tune={provenance['tune']} inputs={provenance['merge_input_file_count']} "
        f"files={len(inventory)}"
    )
    return 0


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("directory", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("tune", choices=TUNES)
    parser.add_argument("input_count", type=int)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("analysis_report", type=Path)
    parser.add_argument("freeze_dir", type=Path)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    write_parser = subparsers.add_parser("write")
    add_common(write_parser)
    write_parser.set_defaults(function=write)
    validate_parser = subparsers.add_parser("validate")
    add_common(validate_parser)
    validate_parser.set_defaults(function=validate)
    args = parser.parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
