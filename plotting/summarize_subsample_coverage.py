#!/usr/bin/env python3
"""Summarize THnSparse subsample-coverage audit output."""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from campaign import PUBLISHED_TUNES  # noqa: E402

# Built from the campaign tune list rather than spelled out, so a log this
# parser cannot match is a real disagreement with the campaign definition
# rather than a stale copy of it.
TUNE_ALTERNATION = "|".join(PUBLISHED_TUNES)

FAILURE_RE = re.compile(
    r"SUBSAMPLE_COVERAGE_FAILURE kind=(?P<kind>yield|ratio) "
    r"Expected (?P<expected>\d+) finite "
    r"(?:yield subsamples|baryon/meson subsample ratios) for "
    rf"(?P<flavour>BEAUTY|CHARM)/(?P<tune>{TUNE_ALTERNATION}) "
    r"\((?P<pair>[^,]+), (?P<bin>[^)]+)\), got (?P<finite>\d+)"
)
SUMMARY_RE = re.compile(
    r"SUBSAMPLE_COVERAGE_AUDIT_SUMMARY "
    r"beauty_failures=(?P<beauty>\d+) "
    r"charm_failures=(?P<charm>\d+) "
    r"total_failures=(?P<total>\d+)"
)
STAT_RE = re.compile(r"subsample (?P<kind>yield|ratio) stats n=(?P<n>\d+)")


def nested_counts(
    records: list[dict[str, object]], fields: tuple[str, ...]
) -> dict[str, int]:
    counts: collections.Counter[str] = collections.Counter()
    for record in records:
        key = "/".join(str(record[field]) for field in fields)
        counts[key] += 1
    return dict(sorted(counts.items()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument(
        "--source-label",
        help="Stable path or provenance label to store instead of the local input path",
    )
    args = parser.parse_args()

    text = args.log.read_text(encoding="utf-8", errors="replace")
    failures: list[dict[str, object]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if match := FAILURE_RE.search(line):
            record: dict[str, object] = {
                key: match.group(key)
                for key in ("kind", "flavour", "tune", "pair", "bin")
            }
            record.update(
                line_number=line_number,
                expected=int(match.group("expected")),
                finite=int(match.group("finite")),
            )
            failures.append(record)

    summary_match = SUMMARY_RE.search(text)
    declared_summary = (
        {
            "beauty_failures": int(summary_match.group("beauty")),
            "charm_failures": int(summary_match.group("charm")),
            "total_failures": int(summary_match.group("total")),
        }
        if summary_match
        else None
    )
    stats = [
        (match.group("kind"), int(match.group("n")))
        for match in STAT_RE.finditer(text)
    ]

    consistency_errors: list[str] = []
    if not summary_match:
        consistency_errors.append("coverage audit summary line is missing")
    elif int(summary_match.group("total")) != len(failures):
        consistency_errors.append(
            "declared total does not match parsed failure count"
        )

    result = {
        "status": "coverage-deficient" if failures else "passed",
        "source_log": args.source_label or str(args.log),
        "declared_summary": declared_summary,
        "parsed_failure_count": len(failures),
        "statistics_line_count": len(stats),
        "statistics_by_kind": dict(collections.Counter(kind for kind, _ in stats)),
        "statistics_n_histogram": {
            str(key): value
            for key, value in sorted(
                collections.Counter(n for _, n in stats).items()
            )
        },
        "zero_trigger_normalisation_warning_count": len(
            re.findall(r"zero trigger normali[sz]ation", text, re.IGNORECASE)
        ),
        "failures_by_flavour": nested_counts(failures, ("flavour",)),
        "failures_by_flavour_and_tune": nested_counts(
            failures, ("flavour", "tune")
        ),
        "failures_by_kind": nested_counts(failures, ("kind",)),
        "failures_by_bin": nested_counts(failures, ("bin",)),
        "failures_by_finite_count": nested_counts(failures, ("finite",)),
        "failures_by_pair": nested_counts(
            failures, ("flavour", "pair")
        ),
        "consistency_errors": consistency_errors,
        "failures": failures,
    }

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: result[key] for key in result if key != "failures"}, indent=2))
    return 1 if consistency_errors else 0


if __name__ == "__main__":
    sys.exit(main())
