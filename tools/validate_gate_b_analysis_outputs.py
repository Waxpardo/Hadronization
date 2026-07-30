#!/usr/bin/env python3
"""Validate exact analysis-output coverage for a Gate-B pilot manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
SELECTOR = "hard_trigger_primary_ground__primary_ground_associate_v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_dir", type=Path)
    parser.add_argument("production_root", type=Path)
    parser.add_argument("analysis_root", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    campaign_dir = args.campaign_dir.resolve()
    production = args.production_root.resolve()
    analysis = args.analysis_root.resolve()
    config = json.loads((campaign_dir / "campaign.json").read_text())
    rows = [
        json.loads(line)
        for line in (campaign_dir / "candidate_manifest.jsonl").read_text().splitlines()
        if line.strip()
    ]
    if config.get("schema") != "hf_gate_b_pilot_campaign_v1" or len(rows) != 9:
        raise ValueError("expected a nine-row Gate-B campaign")

    expected: set[Path] = set()
    validated = []
    analysis_commits: set[str] = set()
    for row in rows:
        tune = row["tune"]
        logical_id = int(row["logical_id"])
        raw = production / "raw" / tune / row["stable_name"]
        directory = analysis / "per_pthat" / tune / f"job_{logical_id:03d}"
        expected.add(directory)
        metadata_path = directory / "analysis_job_metadata.json"
        if not raw.is_file() or not metadata_path.is_file():
            raise FileNotFoundError(f"missing raw or analysis metadata for {directory}")
        metadata = json.loads(metadata_path.read_text())
        if metadata.get("raw_sha256") != sha256(raw):
            raise ValueError(f"raw checksum mismatch for {directory}")
        if metadata.get("selector") != SELECTOR:
            raise ValueError(f"selector mismatch for {directory}")
        if metadata.get("repository_dirty") is not False:
            raise ValueError(f"tracked-dirty analysis checkout for {directory}")
        commit = metadata.get("repository_commit")
        if not isinstance(commit, str) or len(commit) != 40:
            raise ValueError(f"invalid analysis commit for {directory}")
        analysis_commits.add(commit)
        root_files = list(directory.glob("*.root"))
        if len(root_files) != 300:
            raise ValueError(f"expected 300 pair files in {directory}")
        validated.append(
            {
                "tune": tune,
                "logical_id": logical_id,
                "purpose": row["purpose"],
                "raw_sha256": metadata["raw_sha256"],
                "analysis_commit": commit,
            }
        )

    discovered = {
        path.resolve()
        for tune in TUNES
        for path in (analysis / "per_pthat" / tune).glob("job_*")
        if path.is_dir()
    }
    if discovered != expected:
        raise ValueError(
            f"Gate-B analysis coverage mismatch extras={sorted(discovered - expected)} "
            f"missing={sorted(expected - discovered)}"
        )
    if len(analysis_commits) != 1:
        raise ValueError(f"multiple analysis commits: {sorted(analysis_commits)}")
    report = {
        "schema": "hf_gate_b_analysis_validation_v1",
        "campaign": config["campaign"],
        "production_implementation_commit":
            config["repository_implementation_commit"],
        "analysis_commit": next(iter(analysis_commits)),
        "validated_outputs": validated,
        "status": "PASS",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        f"GATE_B_ANALYSIS_OUTPUTS_VALID directories={len(validated)} "
        f"commit={next(iter(analysis_commits))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
