#!/usr/bin/env python3
"""Whether a variation campaign has closed, counted from every log that can say so.

THE TRAP THIS CLOSES. The handoff probe counts closure markers in
`merge_runs/merge_<CAMPAIGN>.log`. That is where they land when the merge driver
runs the closure itself, which it did for six of the seven campaigns. It is not
where they land when a closure is RE-RUN separately: `HF_SYS_MUR_UP`'s closure
was re-run on 2026-08-19 after a schema correction, so its three markers are in
`merge_runs/closure_HF_SYS_MUR_UP.log` and its merge log holds none.

Reading only the merge log therefore reports `HF_SYS_MUR_UP` as **0/3** — a
campaign that closed first, and closed cleanly, looks like one that never
started. A false negative on closure is the dangerous direction: it says "not
ready" about data that is ready, and the natural response is to wait for a merge
that already finished.

THE MARKER IS STILL THE ANSWER. This does not soften the rule that the marker
count decides and the product count does not. It widens where the marker is
looked for, and it reports which log answered so the provenance stays visible.
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
