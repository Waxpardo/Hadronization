#!/usr/bin/env python3
"""The pasted tables in RATIO_TREND.md must still match ratio_trend.json.

RATIO_TREND.md is hand-written prose with the generator's four tables pasted
into it. GOLDEN_OUTPUTS.md 2.16 calls the document "rendered", which invites a
reader to assume a machine keeps the tables in step with the product. No machine
did. This test is that machine.

It cannot run the generator end to end: the generator reads
`vintegrated_closure.log`, and that log is not in the repository. It therefore
renders through `write_ratio_trend.render_tables`, which the generator itself
calls, over the committed `ratio_trend.json`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extraction"))

from write_ratio_trend import render_tables  # noqa: E402

RESULTS = ROOT / "docs/systematics_results_20260819"
DOCUMENT = RESULTS / "RATIO_TREND.md"
PRODUCT = RESULTS / "ratio_trend.json"

FIRST_HEADING = "## The Λ_b/B⁻ ratio against multiplicity, per tune"
NEXT_HEADING = "## What these numbers say, and what they do not"


def committed_block() -> list[str]:
    """The pasted block: the first table heading up to the next `##` section."""
    lines = DOCUMENT.read_text().splitlines()
    try:
        start = lines.index(FIRST_HEADING)
    except ValueError:
        raise AssertionError(
            f"{DOCUMENT.name} no longer opens its tables with {FIRST_HEADING!r}; "
            "the layout moved and this guard needs its anchor updated"
        )
    try:
        end = lines.index(NEXT_HEADING, start)
    except ValueError:
        raise AssertionError(
            f"{DOCUMENT.name} no longer carries {NEXT_HEADING!r} after the "
            "tables; this guard cannot find where the pasted block ends"
        )
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def rendered_block(payload: dict) -> list[str]:
    """The generator's own lines, as the written file would carry them.

    render_tables embeds a newline in each heading entry and the generator joins
    with "\n", so the list entries are not the file's lines. Join first, then
    split, or every heading offsets the comparison by one.
    """
    lines = ("\n".join(render_tables(payload)) + "\n").splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def test_pasted_tables_match_the_product() -> None:
    rendered = rendered_block(json.loads(PRODUCT.read_text()))
    committed = committed_block()
    if committed == rendered:
        return
    report = []
    for i in range(max(len(committed), len(rendered))):
        c = committed[i] if i < len(committed) else "<absent>"
        r = rendered[i] if i < len(rendered) else "<absent>"
        if c != r:
            report.append(f"  line {i}:\n    document: {c}\n    product:  {r}")
    raise AssertionError(
        "the tables pasted into RATIO_TREND.md have drifted from "
        "ratio_trend.json. Re-paste them from the generator:\n"
        + "\n".join(report[:12])
    )


def test_the_guard_can_fail() -> None:
    """Negative control: a guard never seen to fail is not known to be a guard."""
    payload = json.loads(PRODUCT.read_text())
    payload["per_class"]["MONASH"][0]["ratio"] += 0.001
    if rendered_block(payload) == committed_block():
        raise AssertionError(
            "MUTATION SURVIVED: a changed MONASH c1 ratio left the rendered "
            "tables identical, so this test cannot detect drift"
        )


def main() -> int:
    test_pasted_tables_match_the_product()
    test_the_guard_can_fail()
    print(f"RATIO_TREND tables match ratio_trend.json: "
          f"{len(committed_block())} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
