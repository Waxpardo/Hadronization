#!/usr/bin/env python3
"""Validate that per-job analysis outputs are exactly the frozen raw manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
SELECTOR = "hard_trigger_primary_ground__primary_ground_associate_v1"


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("canonical_manifest", type=Path)
    parser.add_argument("analysis_root", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    rows = read_jsonl(args.canonical_manifest.resolve())
    if len(rows) != 300:
        raise ValueError(f"expected 300 canonical rows, found {len(rows)}")
    analysis_root = args.analysis_root.resolve()
    expected_directories: set[Path] = set()
    commits: set[str] = set()
    validated = []
    for row in rows:
        tune = row["tune"]
        slot = int(row["canonical_slot"])
        directory = (
            analysis_root / "per_job" / tune / f"slot_{slot:03d}"
        )
        expected_directories.add(directory)
        metadata_path = directory / "analysis_job_metadata.json"
        if not metadata_path.is_file():
            raise FileNotFoundError(f"missing analysis metadata: {metadata_path}")
        metadata = json.loads(metadata_path.read_text())
        if metadata.get("raw_sha256") != row["raw_sha256"]:
            raise ValueError(f"raw checksum mismatch for {directory}")
        if metadata.get("selector") != SELECTOR:
            raise ValueError(f"selector mismatch for {directory}")
        if metadata.get("repository_dirty") is not False:
            raise ValueError(f"analysis ran from tracked-dirty checkout: {directory}")
        commit = metadata.get("repository_commit")
        if not isinstance(commit, str) or len(commit) != 40:
            raise ValueError(f"invalid analysis commit in {metadata_path}")
        commits.add(commit)
        root_files = {path.name for path in directory.glob("*.root")}
        if len(root_files) != 300:
            raise ValueError(
                f"expected 300 pair ROOT files in {directory}, "
                f"found {len(root_files)}"
            )
        validated.append(
            {
                "tune": tune,
                "canonical_slot": slot,
                "raw_sha256": row["raw_sha256"],
                "analysis_commit": commit,
            }
        )

    discovered = {
        path.resolve()
        for tune in TUNES
        for path in (analysis_root / "per_job" / tune).glob("slot_*")
        if path.is_dir()
    }
    extras = sorted(str(path) for path in discovered - expected_directories)
    missing = sorted(str(path) for path in expected_directories - discovered)
    if extras or missing:
        raise ValueError(
            f"analysis-directory manifest mismatch extras={extras} missing={missing}"
        )
    if len(commits) != 1:
        raise ValueError(f"analysis outputs use multiple commits: {sorted(commits)}")

    report = {
        "schema": "hf_analysis_output_validation_v1",
        "canonical_manifest": str(args.canonical_manifest.resolve()),
        "canonical_manifest_rows": len(rows),
        "analysis_root": str(analysis_root),
        "analysis_commit": next(iter(commits)),
        "validated_outputs": validated,
        "status": "PASS",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        "ANALYSIS_OUTPUT_MANIFEST_VALID "
        f"directories={len(validated)} commit={next(iter(commits))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
