#!/usr/bin/env python3
"""Render a deterministic Condor submit file from the candidate manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_dir", type=Path)
    parser.add_argument("project_base", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--roles", choices=("primary", "reserve", "pilot", "all"),
        default="primary"
    )
    args = parser.parse_args()

    campaign_dir = args.campaign_dir.resolve()
    project_base = args.project_base.resolve()
    campaign = json.loads((campaign_dir / "campaign.json").read_text())
    rows = [
        json.loads(line)
        for line in (campaign_dir / "candidate_manifest.jsonl").read_text().splitlines()
        if line.strip()
    ]
    if args.roles != "all":
        rows = [row for row in rows if row["role"] == args.roles]
    if args.roles == "primary" and len(rows) != 300:
        raise ValueError(f"expected 300 primary candidates, found {len(rows)}")
    if args.roles == "all" and len(rows) != 500:
        raise ValueError(f"expected 500 declared candidates, found {len(rows)}")

    lines = [
        "universe = vanilla",
        f"executable = {project_base}/runCondorJob.sh",
        f"initialdir = {project_base}",
        "getenv = True",
        "request_cpus = 1",
        "request_memory = 4GB",
        "request_disk = 4GB",
        '+UseOS = "el9"',
        '+JobCategory = "$(CATEGORY)"',
        f"log = {project_base}/Production/{campaign['campaign']}/condor_logs/$(TUNE)/job_$(LOGICAL_ID)_$(Cluster)_$(Process).log",
        f"output = {project_base}/Production/{campaign['campaign']}/condor_logs/$(TUNE)/job_$(LOGICAL_ID)_$(Cluster)_$(Process).out",
        f"error = {project_base}/Production/{campaign['campaign']}/condor_logs/$(TUNE)/job_$(LOGICAL_ID)_$(Cluster)_$(Process).err",
        "should_transfer_files = NO",
        "max_retries = 0",
        "on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)",
        (
            'environment = "HADRONIZATION_PTHAT_MIN_OVERRIDE=$(PTHAT)'
            ' HADRONIZATION_STORE_MULTIPLICITY_AUDIT_EVENTS=$(MULT_AUDIT_EVENTS)"'
        ),
        (
            "arguments = --campaign $(CAMPAIGN) $(CAMPAIGN_ORDINAL) "
            "$(TUNE) $(LOGICAL_ID) $(ROLE) $(ATTEMPT) $(SEED) "
            "$(REQUESTED_SUCCESSES) $(Cluster) $(Process)"
        ),
        (
            "queue CAMPAIGN,CAMPAIGN_ORDINAL,TUNE,LOGICAL_ID,ROLE,ATTEMPT,"
            "SEED,REQUESTED_SUCCESSES,CATEGORY,PTHAT,MULT_AUDIT_EVENTS from ("
        ),
    ]
    for row in rows:
        category = row.get(
            "category", "medium" if row["tune"] == "MONASH" else "long"
        )
        lines.append(
            ",".join(
                [
                    row["campaign"],
                    str(campaign["campaign_ordinal"]),
                    row["tune"],
                    str(row["logical_id"]),
                    row["role"],
                    str(row["attempt"]),
                    str(row["seed"]),
                    str(row["requested_successes"]),
                    category,
                    str(row.get("pthat_min_override", "")),
                    str(row.get("multiplicity_audit_events", "")),
                ]
            )
        )
    lines.append(")")
    args.output.write_text("\n".join(lines) + "\n")
    print(
        f"PRODUCTION_SUBMIT_RENDERED rows={len(rows)} roles={args.roles} "
        f"output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
