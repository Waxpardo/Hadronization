#!/usr/bin/env python3
"""Render manifest-only Condor analysis for the nine Gate-B pilot files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_dir", type=Path)
    parser.add_argument("project_base", type=Path)
    parser.add_argument("production_root", type=Path)
    parser.add_argument("analysis_root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--scope", choices=("all", "central", "sensitivity"), default="all"
    )
    args = parser.parse_args()
    campaign_dir = args.campaign_dir.resolve()
    config = json.loads((campaign_dir / "campaign.json").read_text())
    rows = [
        json.loads(line)
        for line in (campaign_dir / "candidate_manifest.jsonl").read_text().splitlines()
        if line.strip()
    ]
    if config.get("schema") != "hf_gate_b_pilot_campaign_v1" or len(rows) != 9:
        raise ValueError("expected a validated nine-row Gate-B pilot campaign")
    if args.scope == "central":
        rows = [row for row in rows if row["purpose"] == "one_million_central"]
    elif args.scope == "sensitivity":
        rows = [row for row in rows if row["purpose"] != "one_million_central"]
    expected_rows = {"all": 9, "central": 3, "sensitivity": 6}[args.scope]
    if len(rows) != expected_rows:
        raise ValueError(
            f"Gate-B {args.scope} scope has {len(rows)} rows, "
            f"expected {expected_rows}"
        )
    tune_order = {tune: index for index, tune in enumerate(TUNES)}
    rows.sort(key=lambda row: (tune_order[row["tune"]], int(row["logical_id"])))

    project = args.project_base.resolve()
    production = args.production_root.resolve()
    analysis = args.analysis_root.resolve()
    lines = [
        "universe = vanilla",
        f"executable = {project}/run_status_analysis.sh",
        f"initialdir = {project}",
        "getenv = True",
        "request_cpus = 1",
        "request_memory = 8GB",
        "request_disk = 8GB",
        '+UseOS = "el9"',
        '+JobCategory = "$(CATEGORY)"',
        (
            f"log = {analysis}/condor_logs/$(TUNE)/"
            "job_$(LOGICAL_ID)_$(Cluster)_$(Process).log"
        ),
        (
            f"output = {analysis}/condor_logs/$(TUNE)/"
            "job_$(LOGICAL_ID)_$(Cluster)_$(Process).out"
        ),
        (
            f"error = {analysis}/condor_logs/$(TUNE)/"
            "job_$(LOGICAL_ID)_$(Cluster)_$(Process).err"
        ),
        "should_transfer_files = NO",
        "max_retries = 0",
        "on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)",
        'arguments = "$(RAW_PATH)" "$(OUTPUT_DIRECTORY)"',
        (
            "queue TUNE,LOGICAL_ID,CATEGORY,RAW_PATH,OUTPUT_DIRECTORY from ("
        ),
    ]
    for row in rows:
        tune = row["tune"]
        logical_id = int(row["logical_id"])
        raw = production / "raw" / tune / row["stable_name"]
        output = (
            analysis / "per_pthat" / tune / f"job_{logical_id:03d}"
        )
        lines.append(
            f"{tune},{logical_id},{row['category']},{raw},{output}"
        )
    lines.append(")")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n")
    print(
        f"GATE_B_ANALYSIS_SUBMIT_RENDERED scope={args.scope} "
        f"rows={len(rows)} output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
