#!/usr/bin/env python3
"""Render manifest-only Condor submission for canonical one-pass analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("canonical_manifest", type=Path)
    parser.add_argument("project_base", type=Path)
    parser.add_argument("production_root", type=Path)
    parser.add_argument("analysis_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = [
        json.loads(line)
        for line in args.canonical_manifest.read_text().splitlines()
        if line.strip()
    ]
    if len(rows) != 300:
        raise ValueError(f"expected 300 canonical rows, found {len(rows)}")
    project = args.project_base.resolve()
    production = args.production_root.resolve()
    analysis = args.analysis_root.resolve()
    for name, path in {
        "project_base": project,
        "production_root": production,
        "analysis_root": analysis,
    }.items():
        if any(character.isspace() for character in str(path)) or "," in str(path):
            raise ValueError(f"{name} contains whitespace or comma: {path}")
    lines = [
        "universe = vanilla",
        f"executable = {project}/run_status_analysis.sh",
        f"initialdir = {project}",
        "getenv = True",
        "request_cpus = 1",
        "request_memory = 8GB",
        "request_disk = 8GB",
        '+UseOS = "el9"',
        '+JobCategory = "long"',
        f"log = {analysis}/condor_logs/$(TUNE)/slot_$(CANONICAL_SLOT)_$(Cluster)_$(Process).log",
        f"output = {analysis}/condor_logs/$(TUNE)/slot_$(CANONICAL_SLOT)_$(Cluster)_$(Process).out",
        f"error = {analysis}/condor_logs/$(TUNE)/slot_$(CANONICAL_SLOT)_$(Cluster)_$(Process).err",
        "should_transfer_files = NO",
        "max_retries = 0",
        "on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)",
        "arguments = $(RAW_PATH) $(OUTPUT_DIRECTORY)",
        "queue TUNE,CANONICAL_SLOT,RAW_PATH,OUTPUT_DIRECTORY from (",
    ]
    for row in rows:
        raw = production / row["raw_path"]
        output = analysis / "per_job" / row["tune"] / f"slot_{int(row['canonical_slot']):03d}"
        lines.append(f"{row['tune']},{row['canonical_slot']},{raw},{output}")
    lines.append(")")
    args.output.write_text("\n".join(lines) + "\n")
    print(f"ANALYSIS_SUBMIT_RENDERED rows={len(rows)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
