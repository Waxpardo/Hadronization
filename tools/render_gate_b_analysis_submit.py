#!/usr/bin/env python3
"""Render manifest-only Condor analysis for the nine Gate-B pilot files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
RAW_SCHEMA = "hf_primary_ground_raw_v7"
ORIGIN_ALGORITHM = "signed_heavy_constituent_complete_mothers_unique_v4"
SAFE_TOKEN = re.compile(r"[A-Za-z0-9._-]+")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_pinned_checksum(raw: Path) -> str:
    sidecar = Path(f"{raw}.sha256")
    if not raw.is_file() or not sidecar.is_file():
        raise FileNotFoundError(f"missing raw input or checksum sidecar: {raw}")
    fields = sidecar.read_text().strip().split()
    if len(fields) != 2 or not re.fullmatch(r"[0-9a-f]{64}", fields[0]):
        raise ValueError(f"invalid raw checksum sidecar: {sidecar}")
    if Path(fields[1]).name != raw.name:
        raise ValueError(f"raw checksum sidecar names another file: {sidecar}")
    actual = sha256(raw)
    if actual != fields[0]:
        raise ValueError(f"raw checksum differs from sidecar: {raw}")
    return actual


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
    if (
        config.get("schema") != "hf_gate_b_pilot_campaign_v1"
        or config.get("raw_schema") != RAW_SCHEMA
        or config.get("origin_algorithm") != ORIGIN_ALGORITHM
        or len(rows) != 9
    ):
        raise ValueError("expected a validated nine-row Gate-B pilot campaign")
    if (
        not isinstance(config.get("campaign"), str)
        or not SAFE_TOKEN.fullmatch(config["campaign"])
        or campaign_dir.name != config["campaign"]
    ):
        raise ValueError("campaign name and campaign-directory basename differ")
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
    for name, path in {
        "project_base": project,
        "production_root": production,
        "analysis_root": analysis,
    }.items():
        if any(character.isspace() for character in str(path)) or any(
            character in str(path) for character in (",", '"', "'", ";")
        ):
            raise ValueError(f"{name} contains an unsafe submit character: {path}")
    analysis_commit = subprocess.check_output(
        ["git", "-C", str(project), "rev-parse", "HEAD"], text=True
    ).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", analysis_commit):
        raise ValueError("analysis checkout did not resolve to a full commit")
    macro_sha256 = sha256(project / "AnalysisScripts/status_analysis_THnSparse_qq.C")
    lines = [
        "universe = vanilla",
        f"executable = {project}/run_status_analysis.sh",
        f"initialdir = {project}",
        "getenv = False",
        f'environment = "HADRONIZATION_BASE={project}"',
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
        (
            "arguments = $(RAW_PATH) $(OUTPUT_DIRECTORY) $(CAMPAIGN) $(TUNE) "
            "$(LOGICAL_ID) $(RAW_SHA256) "
            f"{analysis_commit} {macro_sha256} $(PURPOSE)"
        ),
        (
            "queue CAMPAIGN,TUNE,LOGICAL_ID,CATEGORY,PURPOSE,RAW_SHA256,"
            "RAW_PATH,OUTPUT_DIRECTORY from ("
        ),
    ]
    for row in rows:
        tune = row["tune"]
        logical_id = int(row["logical_id"])
        if (
            tune not in TUNES
            or logical_id not in (0, 1, 2)
            or any(
                not isinstance(row.get(field), str)
                or not SAFE_TOKEN.fullmatch(row[field])
                for field in ("category", "purpose", "stable_name")
            )
        ):
            raise ValueError(f"unsafe or invalid Gate-B analysis row: {row}")
        raw = production / "raw" / tune / row["stable_name"]
        raw_sha256 = read_pinned_checksum(raw)
        output = (
            analysis / "per_pthat" / tune / f"job_{logical_id:03d}"
        )
        lines.append(
            ",".join(
                (
                    config["campaign"],
                    tune,
                    str(logical_id),
                    row["category"],
                    row["purpose"],
                    raw_sha256,
                    str(raw),
                    str(output),
                )
            )
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
