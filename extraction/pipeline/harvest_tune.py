#!/usr/bin/env python3
"""Per-tune harvest driver: closure verdict, extraction, integrity, decomposition.

WHY THIS EXISTS. The three-tune harvest is the resubmission's central number and
the session that does it should be short and mechanical. Every step below has
been done by hand at least once for MONASH; doing them by hand again for
JUNCTIONS and CLOSEPACKING is how a step gets skipped or a threshold gets
eyeballed.

THE VERDICT IS THE POINT. `closure_verdict()` is a pure function of the closure
log text, checked against the counts registered in
`docs/CLOSURE_V3_PREREGISTRATION.md` and quoted in `MONASH_CENTRAL_TABLE.md` §1:

    2100 content comparisons, 1500 invariant comparisons,
    schema paul_pair_objects_primary_ground_v3, errors 0

**1800/600 is the specific failure mode this guards.** If the closure resolves a
v2 sidecar instead of the v3 schema it emits 1800/600 and still says `errors=0`,
which reads as a pass to anything that only greps for the error count. Review
finding A4 added a required expected-schema argument to the wrapper for exactly
this -- but that fix lives only in the local checkout, NOT on the frozen Nikhef
tree the merge is reading, so until the checkout can advance the enforcement has
to happen here, on the emitted text.

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

    Returns every measured field so a FAIL can be reported verbatim rather than
    summarised -- the brief for every harvest says a failing closure is reported
    as-is and the tune stops.
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
            "1800/600 is the v2-sidecar resolution failure mode (review finding "
            "A4): the closure ran against the wrong schema and still reports "
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
