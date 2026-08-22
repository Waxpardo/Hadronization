#!/usr/bin/env python3
"""Run the per-tune closure, extraction, integrity, and decomposition harvest.

`closure_verdict()` checks the closure log against these registered values:

    2100 content comparisons, 1500 invariant comparisons,
    schema paul_pair_objects_primary_ground_v3, errors 0

The 1800/600 counts identify a v2 sidecar even when the log reports zero errors.

STAGES. Each may be run alone; each refuses to run if its predecessor's evidence
is missing. Extraction and decomposition shell out to the already-proven
scripts rather than reimplementing them.

Usage:
  extraction/pipeline/harvest_tune.py TUNE --stage closure   --closure-log FILE
  extraction/pipeline/harvest_tune.py TUNE --stage decompose --rundir DIR
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# The pre-registered closure contract. These are counts, not tolerances.
EXPECTED_SCHEMA = "paul_pair_objects_primary_ground_v3"
EXPECTED_CONTENT_CHECKS = 2100
EXPECTED_INVARIANT_CHECKS = 1500
EXPECTED_CENTRAL_PAIR_FILES = 300
EXPECTED_BLOCK_PAIR_FILES = 3000


def closure_verdict(text: str) -> dict:
    """PASS/FAIL against the standing pre-registration, from the log text alone.

    Return every measured field so a failure preserves the emitted evidence.
    """
    line = None
    for candidate in text.splitlines():
        if candidate.startswith("PAIR_BLOCK_CLOSURE "):
            line = candidate.strip()
            break
    if line is None:
        return {"verdict": "FAIL", "measured": {},
                "failures": ["no PAIR_BLOCK_CLOSURE line in the closure output"],
                "line": None}

    measured: dict[str, str] = {}
    for key, value in re.findall(r"(\w+)=(\S+)", line):
        measured[key] = value

    failures: list[str] = []

    def want_int(key: str, expected: int) -> None:
        raw = measured.get(key)
        if raw is None:
            failures.append(f"{key} missing from the closure line")
            return
        try:
            got = int(raw)
        except ValueError:
            failures.append(f"{key}={raw!r} is not an integer")
            return
        if got != expected:
            failures.append(f"{key}={got}, pre-registered {expected}")

    want_int("errors", 0)
    want_int("object_content_sumw2_closure_checks", EXPECTED_CONTENT_CHECKS)
    want_int("invariant_metadata_checks", EXPECTED_INVARIANT_CHECKS)
    want_int("central_pair_files", EXPECTED_CENTRAL_PAIR_FILES)
    want_int("block_pair_files", EXPECTED_BLOCK_PAIR_FILES)

    schema = measured.get("analysis_schema")
    if schema != EXPECTED_SCHEMA:
        failures.append(
            f"analysis_schema={schema!r}, pre-registered {EXPECTED_SCHEMA!r}")

    # Name the known failure mode explicitly when it appears, because "1800/600
    # with errors=0" is the case that reads as a pass to a careless reader.
    if (measured.get("object_content_sumw2_closure_checks") == "1800"
            and measured.get("invariant_metadata_checks") == "600"):
        failures.append(
            "1800/600 is the v2-sidecar resolution failure mode: the closure "
            "ran against the wrong schema and still reports "
            "errors=0. This is NOT a pass.")

    return {"verdict": "PASS" if not failures else "FAIL",
            "measured": measured, "failures": failures, "line": line}


def stage_closure(tune: str, closure_log: Path) -> int:
    if not closure_log.exists():
        raise SystemExit(f"FAIL-CLOSED: no closure log at {closure_log}")
    result = closure_verdict(closure_log.read_text())
    print(f"TUNE {tune}  CLOSURE {result['verdict']}")
    print(f"  {result['line']}")
    for key in ("errors", "analysis_schema",
                "object_content_sumw2_closure_checks",
                "invariant_metadata_checks"):
        print(f"    {key} = {result['measured'].get(key)}")
    if result["verdict"] != "PASS":
        print("\n  FAILURES (reported verbatim; this tune stops here):")
        for failure in result["failures"]:
            print(f"    - {failure}")
        return 2
    print("  matches the pre-registration: 2100 content / 1500 invariant, "
          "schema v3, errors 0")
    return 0


def stage_decompose(tune: str, rundir: Path) -> int:
    """Integrity + block SEMs, via the committed tool. No reimplementation."""
    tool = REPO / "extraction/decompose_with_block_sems.py"
    result = subprocess.run(
        [sys.executable, str(tool), str(rundir), "--tune", tune],
        capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        print(f"DECOMPOSE FAILED rc={result.returncode}")
    return result.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tune")
    ap.add_argument("--stage", required=True,
                    choices=("closure", "decompose"))
    ap.add_argument("--closure-log", type=Path)
    ap.add_argument("--rundir", type=Path)
    args = ap.parse_args()

    if args.stage == "closure":
        if args.closure_log is None:
            raise SystemExit("--closure-log is required for --stage closure")
        return stage_closure(args.tune, args.closure_log)
    if args.rundir is None:
        raise SystemExit("--rundir is required for --stage decompose")
    return stage_decompose(args.tune, args.rundir)


if __name__ == "__main__":
    raise SystemExit(main())
