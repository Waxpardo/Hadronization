#!/usr/bin/env python3
"""The species-ordinal table: header currency, and fail-closed lookup.

The table is the species axis's index space. It is DERIVED from a raw file's
heavy_stability_audit tree rather than hand-written, on F4's rule that mapping
tables come from PYTHIA's own state; these tests pin the properties the axis
depends on.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "AnalysisScripts/species_ordinals_v2.json"
HEADER = ROOT / "AnalysisScripts/GeneratedSpeciesOrdinals.h"
GENERATOR = ROOT / "tools/generate_species_ordinals_header.py"


def artifact() -> dict:
    return json.loads(ARTIFACT.read_text())


def test_header_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        text=True, capture_output=True,
    )
    assert result.returncode == 0, (
        "AnalysisScripts/GeneratedSpeciesOrdinals.h is stale; regenerate with "
        f"tools/generate_species_ordinals_header.py\n{result.stderr}"
    )


def test_artifact_is_the_ratified_table() -> None:
    """202 species, and the digest that identifies the axis.

    Pin both literals independently of the artifact under test.
    Deriving either value from the artifact would make the check self-referential.
    """
    payload = artifact()
    assert payload["species_count"] == 202, payload["species_count"]
    assert payload["table_digest_fnv1a64"] == "646f310f78126267", (
        payload["table_digest_fnv1a64"]
    )
    # 219 audit rows minus 17 hidden-heavy states that carry q_c = q_b = 0 and
    # therefore cannot compensate.
    assert payload["audit_rows_total"] == 219
    assert payload["hidden_heavy_excluded"] == 17
    assert (payload["audit_rows_total"] - payload["hidden_heavy_excluded"]
            == payload["species_count"])


def test_digest_covers_the_index_space_only() -> None:
    """The digest identifies the AXIS, so annotation must not move it.

    v1 of the artifact carried no category column and the same 202 ordinals.
    Its digest was identical. If adding a column ever changes the digest, two
    tables that index identically would look different and a reader comparing
    files would draw the wrong conclusion.
    """
    header = HEADER.read_text()
    assert '"646f310f78126267"' in header, (
        "the header does not carry the ratified digest"
    )


def test_every_species_carries_a_category() -> None:
    for row in artifact()["species"]:
        assert "category" in row and "category_name" in row, row
        assert 0 <= row["category"] <= 5, row
    counts = artifact()["category_counts"]
    assert counts["kOtherNoncentral"] == 0, (
        "kOtherNoncentral is unreachable for an open-heavy table: every row "
        "has n_charm + n_beauty > 0, so hasCharm||hasBeauty fires first"
    )
    assert sum(counts.values()) == 202, counts


def test_lookup_semantics() -> None:
    compiler = shutil.which("c++")
    if compiler is None:
        raise RuntimeError("a C++17 compiler is required")
    with tempfile.TemporaryDirectory() as temporary:
        executable = Path(temporary) / "test_species_ordinals"
        subprocess.run(
            [
                compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                str(ROOT / "tests/test_species_ordinals.cpp"),
                "-o", str(executable),
            ],
            cwd=ROOT, check=True,
        )
        result = subprocess.run(
            [str(executable)], check=False, text=True, capture_output=True)
    output = result.stdout + result.stderr
    if result.returncode != 0 or "errors=0" not in output:
        raise AssertionError(f"species-ordinal lookup test failed:\n{output}")
    if "species=202" not in output:
        raise AssertionError(
            f"the harness did not see 202 species:\n{output}")


def main() -> int:
    ran = 0
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            ran += 1
    print(f"species-ordinal tests passed tests={ran} "
          f"species={artifact()['species_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
