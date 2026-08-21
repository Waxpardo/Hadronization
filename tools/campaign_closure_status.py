#!/usr/bin/env python3
"""Count a variation campaign's closure markers across merge and rerun logs.

HF_SYS_MUR_UP stores its three markers only in a separate closure log.
The marker count decides closure; product counts do not substitute for it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "CANONICAL_PAIR_BLOCK_CLOSURE_PASS"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
REQUIRED_MARKERS = len(TUNES)


def candidate_logs(merge_runs: Path, campaign: str) -> list[Path]:
    """Every log that may carry this campaign's closure markers, in priority order.

    The closure re-run log comes first: when both exist it is the later and
    authoritative one, because a re-run supersedes the closure the merge driver
    performed.
    """
    return [merge_runs / f"closure_{campaign}.log",
            merge_runs / f"merge_{campaign}.log"]


def tunes_marked(text: str) -> set[str]:
    """Which tunes a log records a closure PASS for. A set, so a repeated line
    counts once -- a re-run that logged twice must not read as six of three."""
    found = set()
    for line in text.splitlines():
        if not line.startswith(MARKER):
            continue
        for token in line.split():
            if token.startswith("tune=") and token[5:] in TUNES:
                found.add(token[5:])
    return found


def closure_status(logs: dict[str, str]) -> dict:
    """`logs` maps a log's name to its text. Reports the union across them."""
    per_log = {name: tunes_marked(text) for name, text in logs.items()}
    union: set[str] = set()
    for marked in per_log.values():
        union |= marked
    answering = sorted(name for name, marked in per_log.items() if marked)
    return {
        "tunes_closed": sorted(union),
        "markers": len(union),
        "required": REQUIRED_MARKERS,
        "closed": len(union) == REQUIRED_MARKERS,
        "answering_logs": answering,
        "per_log": {name: sorted(marked) for name, marked in per_log.items()},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--merge-runs", type=Path, required=True)
    ap.add_argument("campaigns", nargs="+")
    args = ap.parse_args()

    worst = 0
    for campaign in args.campaigns:
        logs = {}
        for path in candidate_logs(args.merge_runs, campaign):
            if path.exists():
                logs[path.name] = path.read_text(errors="replace")
        status = closure_status(logs)
        verdict = "CLOSED" if status["closed"] else "NOT CLOSED"
        print(f"{campaign:22s} {status['markers']}/{status['required']} "
              f"{verdict:11s} from={','.join(status['answering_logs']) or 'no log'}")
        if not status["closed"]:
            worst = 1
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
