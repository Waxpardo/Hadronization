#!/usr/bin/env python3
"""Harvest configurations share one axis and use selector-authoritative routes."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from class_label_format import format_percentile_range  # noqa: E402

CONTRACT = ROOT / "config/multiplicity_percentile_classes_v2.json"
SOURCE = ROOT / "tools/make_harvest_configs.py"
SPEC = importlib.util.spec_from_file_location("make_harvest_configs", SOURCE)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def labels(document: dict) -> list[str]:
    found: list[str] = []

    def visit(value: object) -> None:
        if isinstance(value, dict):
            if isinstance(value.get("display_name"), str):
                found.append(value["display_name"])
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(document)
    return found


def main() -> int:
    central = json.loads(MODULE.CENTRAL.read_text())
    MODULE.validate_route(central, MODULE.NOMINAL)

    central_labels = labels(central)
    # Ruling R10: every class label the contract defines must be present, and
    # the labels come from the contract rather than from a copy of them here.
    for row in json.loads(CONTRACT.read_text())["classes"]:
        expected = format_percentile_range(row["percentile_min"],
                                           row["percentile_max"])
        assert expected in central_labels, expected

    for campaign in MODULE.CAMPAIGNS:
        derived = json.loads(MODULE.output_path(campaign).read_text())
        MODULE.validate_route(derived, campaign)
        assert labels(derived) == central_labels

    bad = json.loads(json.dumps(central))
    bad["base_dir"] = "/stale/storage/root"
    try:
        MODULE.validate_route(bad, MODULE.NOMINAL)
    except ValueError as error:
        assert "differs from its active dataset selector" in str(error)
    else:
        raise AssertionError("a stale nominal storage root was accepted")

    result = subprocess.run(
        [sys.executable, str(SOURCE), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "HARVEST_CONFIGS_CURRENT files=7" in result.stdout
    print("harvest configs: 7 current, routes selector-bound, tune-local windows shared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
