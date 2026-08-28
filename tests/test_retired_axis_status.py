#!/usr/bin/env python3
"""Retired common-axis trees are complete provenance scopes, never current roots."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_NAME = "RETIREMENT_STATUS.json"
SCHEMA = "hadronization_retired_common_axis_status_v1"
SCOPES = (
    "results/systematics/20260819",
    "results/systematics/20260820",
)


def relative_artifacts(directory: Path) -> list[str]:
    return sorted(
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file() and path.name != STATUS_NAME
    )


def check_scope(scope: str) -> int:
    directory = ROOT / scope
    record = json.loads((directory / STATUS_NAME).read_text())
    assert record["schema"] == SCHEMA, f"{scope}: schema"
    assert record["scope"] == scope, f"{scope}: scope"
    assert record["axis_contract"] == "retired_common_absolute_multiplicity_axis", (
        f"{scope}: axis_contract")
    assert record["status"] == "HISTORICAL_PROVENANCE_ONLY", f"{scope}: status"
    assert record["current_or_publication_use"] == "PROHIBITED", (
        f"{scope}: current_or_publication_use")
    assert record["current_result_root"] is False, f"{scope}: current_result_root"
    assert record["publication_result"] is False, f"{scope}: publication_result"
    assert record["successor_status"] == (
        "AWAITING_J_B_AND_J_C_TUNE_LOCAL_SUCCESSOR"), f"{scope}: successor_status"
    expected = relative_artifacts(directory)
    assert record["coverage"]["files"] == expected, (
        f"{scope}: coverage.files expected={expected!r} "
        f"actual={record['coverage']['files']!r}")
    return len(expected)


def main() -> int:
    counts = {scope: check_scope(scope) for scope in SCOPES}
    readme = (ROOT / "results/README.md").read_text()
    for scope in SCOPES:
        relative_status = f"{scope.removeprefix('results/')}/{STATUS_NAME}"
        assert relative_status in readme, f"results/README.md: missing {relative_status}"
    assert "git show" not in readme, "results/README.md: internal-history recovery"
    assert "multiplicity_percentile_classes_v2.json" in readme, (
        "results/README.md: surviving tune-local class contract")
    assert "not current\nresult roots" in readme, "results/README.md: current-root prohibition"
    print("retired common-axis status: " + ", ".join(
        f"{scope}={count} covered artifacts" for scope, count in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
