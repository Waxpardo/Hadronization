#!/usr/bin/env python3
"""Validate and resolve the single publication dataset selector."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path


REQUIRED = {
    "status",
    "campaign",
    "raw_schema",
    "selector",
    "canonical_manifest",
    "production_root",
    "analysis_root",
    "raw_base",
    "analyzed_data_base",
    "complete_root_tag",
    "subsample_base",
    "block_count",
    "interpretation",
}


def load(path: Path) -> tuple[str, dict]:
    payload = json.loads(path.read_text())
    if payload.get("schema") != "hadronization_dataset_selector_v1":
        raise ValueError("unsupported dataset-selector schema")
    active = payload.get("active_dataset")
    datasets = payload.get("datasets")
    if not isinstance(active, str) or not isinstance(datasets, dict):
        raise ValueError("dataset selector requires active_dataset and datasets")
    if active not in datasets:
        raise ValueError(f"active dataset is absent: {active}")
    row = datasets[active]
    missing = REQUIRED - row.keys()
    if missing:
        raise ValueError(f"active dataset is missing fields: {sorted(missing)}")
    if int(row["block_count"]) != 10:
        raise ValueError("publication dataset must have exactly ten blocks")
    if row["status"] == "canonical":
        for key in (
            "campaign",
            "canonical_manifest",
            "production_root",
            "analysis_root",
        ):
            if not isinstance(row[key], str) or not row[key]:
                raise ValueError(f"canonical dataset requires {key}")
        if row["raw_schema"] != "hf_primary_ground_raw_v3":
            raise ValueError("canonical dataset has wrong raw schema")
        if (
            row["selector"]
            != "hard_trigger_primary_ground__primary_ground_associate_v1"
        ):
            raise ValueError("canonical dataset has wrong selector")
    return active, row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=("validate", "show", "shell")
    )
    parser.add_argument(
        "--selector",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "config/dataset_selector.json",
    )
    args = parser.parse_args()
    active, row = load(args.selector.resolve())
    if args.command == "validate":
        print(
            f"DATASET_SELECTOR_VALID active={active} "
            f"status={row['status']} blocks={row['block_count']}"
        )
    elif args.command == "show":
        print(json.dumps({"active_dataset": active, **row}, indent=2, sort_keys=True))
    else:
        values = {
            "HADRONIZATION_DATASET_ID": active,
            "HADRONIZATION_DATASET_STATUS": row["status"],
            "HADRONIZATION_RAW_BASE": row["raw_base"],
            "HADRONIZATION_ANALYZED_DATA_BASE": row["analyzed_data_base"],
            "HADRONIZATION_COMPLETE_ROOT_TAG": row["complete_root_tag"],
            "HADRONIZATION_SUBSAMPLE_BASE": row["subsample_base"],
        }
        for key, value in values.items():
            print(f"export {key}={shlex.quote(str(value))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
