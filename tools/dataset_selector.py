#!/usr/bin/env python3
"""Validate and resolve the single publication dataset selector."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import publication_eligibility  # noqa: E402


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
    "publication_eligible",
    "publication_authorization",
    "publication_authorization_sha256",
    "interpretation",
}


def load(path: Path, checkout: Path | None = None) -> tuple[str, dict]:
    checkout = (
        checkout.resolve()
        if checkout is not None
        else Path(__file__).resolve().parents[1]
    )
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
    if not isinstance(row["publication_eligible"], bool):
        raise ValueError("publication_eligible must be a boolean")
    if not isinstance(row["interpretation"], str) or not row["interpretation"]:
        raise ValueError("dataset interpretation must be nonempty")

    status = row["status"]
    if status in {"canonical", "canonical_candidate"}:
        for key in (
            "campaign",
            "canonical_manifest",
            "production_root",
            "analysis_root",
            "raw_base",
            "analyzed_data_base",
            "complete_root_tag",
            "subsample_base",
        ):
            if not isinstance(row[key], str) or not row[key]:
                raise ValueError(f"canonical dataset requires {key}")
        if row["raw_schema"] != "hf_primary_ground_raw_v6":
            raise ValueError("canonical dataset has wrong raw schema")
        if (
            row["selector"]
            != "hard_trigger_primary_ground__primary_ground_associate_v1"
        ):
            raise ValueError("canonical dataset has wrong selector")
        if status == "canonical":
            if not row["publication_eligible"]:
                raise ValueError(
                    "canonical dataset must set publication_eligible=true"
                )
            authorization_value = row["publication_authorization"]
            authorization_relative = (
                Path(authorization_value)
                if isinstance(authorization_value, str)
                else Path()
            )
            if (
                not authorization_value
                or authorization_relative.is_absolute()
                or ".." in authorization_relative.parts
                or not isinstance(
                    row["publication_authorization_sha256"], str
                )
            ):
                raise ValueError(
                    "canonical dataset publication authorization is malformed"
                )
            evidence = publication_eligibility.validate_authorization(
                checkout=checkout,
                dataset_id=active,
                dataset_row=row,
                authorization_path=checkout / authorization_relative,
                expected_sha256=row["publication_authorization_sha256"],
            )
            row = {**row, "publication_eligibility_evidence": evidence}
        else:
            if row["publication_eligible"]:
                raise ValueError(
                    "canonical candidate cannot be publication eligible"
                )
            for key in (
                "publication_authorization",
                "publication_authorization_sha256",
            ):
                if row[key] is not None:
                    raise ValueError(
                        f"canonical candidate must leave {key} null"
                    )
    elif status == "legacy_regression_default":
        if row["publication_eligible"]:
            raise ValueError(
                "legacy regression dataset cannot be publication eligible"
            )
        for key in (
            "campaign",
            "canonical_manifest",
            "production_root",
            "analysis_root",
            "publication_authorization",
            "publication_authorization_sha256",
        ):
            if row[key] is not None:
                raise ValueError(
                    f"legacy regression dataset must leave {key} null"
                )
        for key in (
            "raw_base",
            "analyzed_data_base",
            "complete_root_tag",
            "subsample_base",
        ):
            if not isinstance(row[key], str) or not row[key]:
                raise ValueError(f"legacy regression dataset requires {key}")
        if row["raw_schema"] != "legacy_status_unknown":
            raise ValueError("legacy regression dataset has wrong raw schema")
        if row["selector"] != "legacy_status":
            raise ValueError("legacy regression dataset has wrong selector")
    else:
        raise ValueError(f"unsupported dataset status: {status!r}")
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
    parser.add_argument(
        "--checkout",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    active, row = load(args.selector.resolve(), args.checkout.resolve())
    if args.command == "validate":
        print(
            f"DATASET_SELECTOR_VALID active={active} "
            f"status={row['status']} blocks={row['block_count']}"
        )
    elif args.command == "show":
        print(json.dumps({"active_dataset": active, **row}, indent=2, sort_keys=True))
    else:
        def shell_value(key: str) -> str:
            value = row[key]
            return "" if value is None else str(value)

        values = {
            "HADRONIZATION_DATASET_ID": active,
            "HADRONIZATION_DATASET_STATUS": row["status"],
            "HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE":
                "true" if row["publication_eligible"] else "false",
            "HADRONIZATION_CANONICAL_MANIFEST":
                shell_value("canonical_manifest"),
            "HADRONIZATION_PRODUCTION_ROOT":
                shell_value("production_root"),
            "HADRONIZATION_ANALYSIS_ROOT":
                shell_value("analysis_root"),
            "HADRONIZATION_RAW_BASE": shell_value("raw_base"),
            "HADRONIZATION_ANALYZED_DATA_BASE":
                shell_value("analyzed_data_base"),
            "HADRONIZATION_COMPLETE_ROOT_TAG":
                shell_value("complete_root_tag"),
            "HADRONIZATION_SUBSAMPLE_BASE":
                shell_value("subsample_base"),
        }
        for key, value in values.items():
            print(f"export {key}={shlex.quote(str(value))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
