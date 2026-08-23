#!/usr/bin/env python3
"""Validate and resolve the single publication dataset selector."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))



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

PATH_FIELDS = {
    "canonical_manifest",
    "production_root",
    "analysis_root",
    "raw_base",
    "analyzed_data_base",
    "subsample_base",
    "publication_authorization",
}


def expand_site_paths(row: dict) -> dict:
    """Expand tracked ${VARIABLE} routes after setupEnv selected a site."""
    resolved = dict(row)
    for key in PATH_FIELDS:
        value = resolved.get(key)
        if value is None:
            continue
        if not isinstance(value, str):
            raise ValueError(f"dataset field {key} must be a string or null")
        expanded = os.path.expandvars(value)
        if "$" in expanded:
            raise ValueError(
                f"dataset field {key} contains an unresolved site variable: "
                f"{value!r}; source setupEnv.sh first"
            )
        resolved[key] = expanded
    return resolved


def load(
    path: Path,
    checkout: Path | None = None,
    dataset: str | None = None,
) -> tuple[str, dict]:
    """Resolve one dataset row. A dataset must be NAMED, not defaulted.

    A resolver that answers a question nobody asked will answer it wrongly, and
    the wrong answer looks exactly like a right one: the render succeeds, emits
    all its rows, and reports the wrong dataset. That is not hypothetical -- a
    silent `active_dataset` default is what let five variation renders read the
    central campaign.

    So `active_dataset: null` means REFUSE, and the refusal names every key it
    would have accepted. Per-campaign selector files carry exactly one row and
    keep their own `active_dataset`, so naming the file names the dataset and
    those callers are unaffected.
    """
    checkout = (
        checkout.resolve()
        if checkout is not None
        else Path(__file__).resolve().parents[1]
    )
    payload = json.loads(path.read_text())
    if payload.get("schema") != "hadronization_dataset_selector_v1":
        raise ValueError("unsupported dataset-selector schema")
    datasets = payload.get("datasets")
    if not isinstance(datasets, dict) or not datasets:
        raise ValueError("dataset selector requires a nonempty datasets map")

    declared = payload.get("active_dataset")
    if dataset is not None:
        active = dataset
    elif isinstance(declared, str) and declared:
        active = declared
    else:
        raise ValueError(
            "no dataset named and this selector declares no default; "
            "name one with --dataset or HADRONIZATION_DATASET. "
            f"accepted keys: {sorted(datasets)}"
        )
    if active not in datasets:
        raise ValueError(
            f"dataset is absent: {active}. "
            f"accepted keys: {sorted(datasets)}"
        )
    row = expand_site_paths(datasets[active])
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
        if row["raw_schema"] != "hf_primary_ground_raw_v7":
            raise ValueError("canonical dataset has wrong raw schema")
        if (
            row["selector"]
            != "hard_trigger_primary_ground__primary_ground_associate_v1"
        ):
            raise ValueError("canonical dataset has wrong selector")
        # The publication-authorization fields that used to be validated here
        # belonged to the gate layer. What matters for correctness is above:
        # the raw schema and the selector contract.
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
    elif status == "systematic_variation":
        # ADDED 2026-08-19. A variation campaign is a real dataset the resolver
        # must be able to point at, and the selector is the only thing that can
        # point it: the plotting configuration is a request, and the selector's
        # exported tag is what the macro actually reads. Before this arm
        # existed, the only way to render a variation was to override
        # HADRONIZATION_COMPLETE_ROOT_TAG by hand, which is disabling the guard
        # rather than satisfying it.
        #
        # It carries the same contract as a canonical dataset -- same raw
        # schema, same selector, same eight paths -- because it is the same
        # instrument at one tenth the exposure. The one thing it may NOT be is
        # publishable, and that is enforced here rather than left to a field
        # nobody checks.
        if row["publication_eligible"]:
            raise ValueError(
                "a systematic variation is an input to an uncertainty, not a "
                "publication dataset; publication_eligible must be false"
            )
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
                raise ValueError(f"systematic variation requires {key}")
        if row["raw_schema"] != "hf_primary_ground_raw_v7":
            raise ValueError("systematic variation has wrong raw schema")
        if (
            row["selector"]
            != "hard_trigger_primary_ground__primary_ground_associate_v1"
        ):
            raise ValueError("systematic variation has wrong selector")
        measurement_config = row.get("measurement_config")
        if not isinstance(measurement_config, str) or not measurement_config:
            raise ValueError(
                "systematic variation requires measurement_config"
            )
        config_path = (checkout / measurement_config).resolve()
        try:
            config_path.relative_to(checkout)
        except ValueError as error:
            raise ValueError(
                "measurement_config must remain inside the checkout"
            ) from error
        if not config_path.is_file():
            raise ValueError(
                f"measurement_config does not exist: {measurement_config}"
            )
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
    parser.add_argument(
        "--dataset",
        default=os.environ.get("HADRONIZATION_DATASET") or None,
        help=(
            "the dataset key to resolve. Required when the selector declares "
            "no active_dataset. Defaults to $HADRONIZATION_DATASET."
        ),
    )
    args = parser.parse_args()
    # A refusal is a named exit, not a traceback. `./hadronization` reads this
    # tool's status, and a traceback carries the reason to a human while
    # telling the caller nothing it can act on.
    try:
        active, row = load(
            args.selector.resolve(), args.checkout.resolve(), args.dataset
        )
    except ValueError as error:
        print(
            f"DATASET_SELECTOR_REFUSED dataset={args.dataset!r} "
            f"selector={args.selector}: {error}",
            file=sys.stderr,
        )
        return 2
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
            # The campaign this row promotes. Exported so a consumer can check
            # that the freeze it was handed is the one the selector named: the
            # manifest path is just a path, and any other campaign's valid
            # sealed freeze would otherwise satisfy every internal check.
            "HADRONIZATION_CAMPAIGN": row["campaign"] or "",
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
            "HADRONIZATION_MEASUREMENT_CONFIG":
                str(row.get("measurement_config") or ""),
            "HADRONIZATION_SUBSAMPLE_BASE":
                shell_value("subsample_base"),
        }
        for key, value in values.items():
            print(f"export {key}={shlex.quote(str(value))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
