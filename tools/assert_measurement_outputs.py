#!/usr/bin/env python3
"""The output-side assertion for a measurement render.

WHY THIS EXISTS. The measurement target already refuses a measurement root
inside the publication tree, refuses a publication target in the same run, and
stamps `purpose=measurement` on its receipt. Every one of those gates reads the
REQUEST. On 2026-08-19 the request was correct and three canvases still landed
in `plotting/Plots/THnSparseCompleteRoot_HF_RUN3_V1`, because the plotter takes
`writePath` from a nested configuration field and the staged copy set a
top-level key the plotter never reads (run record 19.1).

A GATE ON THE REQUEST CANNOT CERTIFY THE RESULT. This module asks the other
question: after the render, WHERE ARE THE FILES?

Two requirements, both checked against the filesystem rather than the
configuration:

1. No file under any publication `Plots` path carries an mtime inside the
   render window.
2. Every expected artifact exists under the measurement root.

FAIL CLOSED AT THE EDGES. The window is inclusive at both ends: a file stamped
exactly at the start or the end is a violation, not a pass. A render window
recorded to the second cannot distinguish "at 15:14:02" from "during the second
that began at 15:14:02", so the benefit of the doubt goes to the assertion.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PUBLICATION_DIRECTORY_NAME = "Plots"


# --- the pure core --------------------------------------------------------
# These three functions take values, not paths, so the tests can hand them
# constructed and historical inputs without a filesystem.

def files_in_window(entries, window_start: float, window_end: float) -> list[str]:
    """Paths whose mtime falls inside [window_start, window_end], INCLUSIVE.

    `entries` is an iterable of (path, mtime) pairs. Inclusive at both ends:
    see the module docstring on failing closed at the edges.
    """
    if window_end < window_start:
        raise ValueError(
            f"render window ends before it starts: {window_start} > {window_end}")
    return sorted(str(path) for path, mtime in entries
                  if window_start <= mtime <= window_end)


def missing_artifacts(expected, present) -> list[str]:
    """Expected artifacts that are not present. Order-independent."""
    return sorted(set(map(str, expected)) - set(map(str, present)))


def assess(publication_entries, window_start: float, window_end: float,
           expected, present) -> dict:
    """The verdict. `passed` is true only when both requirements hold."""
    touched = files_in_window(publication_entries, window_start, window_end)
    missing = missing_artifacts(expected, present)
    return {
        "schema": "hadronization_measurement_output_assertion_v1",
        "window_start": window_start,
        "window_end": window_end,
        "publication_files_touched": touched,
        "publication_files_touched_count": len(touched),
        "missing_measurement_artifacts": missing,
        "publication_tree_clean": not touched,
        "measurement_artifacts_complete": not missing,
        "passed": not touched and not missing,
    }


# --- the filesystem side --------------------------------------------------

def discover_publication_trees(scan_bases) -> list[str]:
    """Every directory named `Plots` under each scan base.

    Discovery rather than a list: the assertion must cover publication paths
    this driver was never told about.
    """
    found: set[str] = set()
    for base in scan_bases:
        for dirpath, dirnames, _ in os.walk(base):
            if os.path.basename(dirpath) == PUBLICATION_DIRECTORY_NAME:
                found.add(dirpath)
            if ".git" in dirnames:
                dirnames.remove(".git")
    return sorted(found)


def walk_entries(trees):
    """(path, mtime) for every regular file under each tree."""
    entries = []
    for tree in trees:
        for dirpath, _, filenames in os.walk(tree):
            for name in filenames:
                path = os.path.join(dirpath, name)
                try:
                    entries.append((path, os.stat(path).st_mtime))
                except FileNotFoundError:
                    continue
    return entries


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--measurement-root", required=True)
    ap.add_argument("--window-start", type=float, required=True)
    ap.add_argument("--window-end", type=float, required=True)
    ap.add_argument("--scan-base", action="append", default=[],
                    help="search this tree for directories named Plots")
    ap.add_argument("--publication-tree", action="append", default=[],
                    help="treat this exact directory as a publication tree")
    ap.add_argument("--expect", action="append", default=[],
                    help="path required to exist, relative to the "
                         "measurement root")
    ap.add_argument("--out", help="write the verdict here as JSON")
    args = ap.parse_args()

    trees = sorted(set(discover_publication_trees(args.scan_base))
                   | set(args.publication_tree))
    root = Path(args.measurement_root)
    expected = list(args.expect)
    present = [rel for rel in expected if (root / rel).exists()]

    verdict = assess(walk_entries(trees), args.window_start, args.window_end,
                     expected, present)
    verdict["publication_trees_scanned"] = trees
    verdict["measurement_root"] = str(root)

    if args.out:
        Path(args.out).write_text(json.dumps(verdict, indent=2,
                                             sort_keys=True) + "\n")

    if verdict["passed"]:
        print(f"OUTPUT_ASSERTION_PASS trees={len(trees)} "
              f"touched=0 artifacts={len(expected)}/{len(expected)}")
        return 0

    print("OUTPUT_ASSERTION_FAIL", file=sys.stderr)
    for path in verdict["publication_files_touched"]:
        print(f"  WROTE INTO A PUBLICATION PATH: {path}", file=sys.stderr)
    for rel in verdict["missing_measurement_artifacts"]:
        print(f"  MISSING UNDER THE MEASUREMENT ROOT: {rel}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
