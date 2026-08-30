#!/usr/bin/env python3
"""Validate verbose improvedPlotting_THnSparse subsample-statistics output.

PRODUCTION INPUT ONLY (ledger D14). This reads a render log written with
SUBSAMPLE_COVERAGE_AUDIT = 1. The measurement configurations set it to 0, so a
measurement render log carries no subsample-statistics line and this script
exits 1 on it. That exit is the correct refusal for the wrong input, not a
defect: run it against a subsample-audit render.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from campaign import PUBLISHED_TUNES  # noqa: E402

# The tune alternation is built from the campaign tune list rather than spelled
# out, so a log this parser cannot match is a real disagreement with the
# campaign definition rather than a stale copy of it.
TUNE_ALTERNATION = "|".join(PUBLISHED_TUNES)

STAT_RE = re.compile(
    r"subsample (?P<kind>yield|ratio) stats "
    r"n=(?P<n>\d+) mean=(?P<mean>\S+) stdDev=(?P<stddev>\S+) stdError=(?P<stderr>\S+)"
)
FLAVOUR_RE = re.compile(r"\*\*\* Calculating yields for (BEAUTY|CHARM) \*\*\*")
TUNE_RE = re.compile(rf"starting loop over ({TUNE_ALTERNATION})$")
PAIR_RE = re.compile(r"starting loop over OS file: (\S+) and SS file: (\S+)")
BIN_RE = re.compile(r"Analysing bin (\d+)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--expected-n", type=int, default=10)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    text = args.log.read_text(encoding="utf-8", errors="replace")
    records: list[dict[str, object]] = []
    context: dict[str, object] = {
        "flavour": None,
        "tune": None,
        "os_file": None,
        "ss_file": None,
        "bin_index": None,
    }

    for line_number, line in enumerate(text.splitlines(), start=1):
        if match := FLAVOUR_RE.search(line):
            context["flavour"] = match.group(1)
        if match := TUNE_RE.search(line):
            context["tune"] = match.group(1)
        if match := PAIR_RE.search(line):
            context["os_file"], context["ss_file"] = match.groups()
        if match := BIN_RE.search(line):
            context["bin_index"] = int(match.group(1))
        if match := STAT_RE.search(line):
            record = dict(context)
            record.update(
                line_number=line_number,
                kind=match.group("kind"),
                n=int(match.group("n")),
                mean=float(match.group("mean")),
                stddev=float(match.group("stddev")),
                stderr=float(match.group("stderr")),
                source_line=line,
            )
            records.append(record)

    failures: list[str] = []
    if not records:
        failures.append("no subsample statistics lines found")

    for record in records:
        label = (
            f"line {record['line_number']} {record['flavour']}/{record['tune']} "
            f"{record['os_file']} bin={record['bin_index']} {record['kind']}"
        )
        if record["n"] != args.expected_n:
            failures.append(f"{label}: n={record['n']}, expected {args.expected_n}")
        for field in ("mean", "stddev", "stderr"):
            if not math.isfinite(float(record[field])):
                failures.append(f"{label}: non-finite {field}={record[field]}")
        stderr = float(record["stderr"])
        mean = float(record["mean"])
        expected_degenerate_ratio = (
            record["kind"] == "ratio"
            and math.isclose(mean, 1.0, rel_tol=0.0, abs_tol=1e-12)
            and math.isclose(stderr, 0.0, rel_tol=0.0, abs_tol=1e-15)
        )
        if stderr <= 0.0 and not expected_degenerate_ratio:
            failures.append(f"{label}: non-positive stdError={stderr}")

    forbidden_patterns = {
        "ROOT/input error": re.compile(
            r"(Could not find input ROOT file|Missing or wrong-type object|"
            r"zero trigger normali[sz]ation|ERROR:)",
            re.IGNORECASE,
        ),
        "placeholder error": re.compile(r"(?<![\w.])1e-10(?![\w.])", re.IGNORECASE),
        "non-finite token": re.compile(
            r"(?<![A-Za-z])(nan|[-+]?inf(?:inity)?)(?![A-Za-z])", re.IGNORECASE
        ),
    }
    for label, pattern in forbidden_patterns.items():
        if match := pattern.search(text):
            failures.append(f"{label} found near log offset {match.start()}: {match.group(0)}")

    representatives: list[dict[str, object]] = []
    for flavour in ("BEAUTY", "CHARM"):
        for tune in PUBLISHED_TUNES:
            for kind in ("yield", "ratio"):
                found = next(
                    (
                        record
                        for record in records
                        if record["flavour"] == flavour
                        and record["tune"] == tune
                        and record["kind"] == kind
                        and float(record["stderr"]) > 0.0
                    ),
                    None,
                )
                if found:
                    representatives.append(found)
                else:
                    failures.append(
                        f"no nonzero representative for {flavour}/{tune}/{kind}"
                    )

    summary = {
        "status": "passed" if not failures else "failed",
        "log": str(args.log),
        "expected_n": args.expected_n,
        "record_count": len(records),
        "yield_record_count": sum(record["kind"] == "yield" for record in records),
        "ratio_record_count": sum(record["kind"] == "ratio" for record in records),
        "min_positive_stderr": min(
            (float(record["stderr"]) for record in records if float(record["stderr"]) > 0.0),
            default=None,
        ),
        "max_stderr": max((float(record["stderr"]) for record in records), default=None),
        "representatives": representatives,
        "failures": failures,
    }

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
