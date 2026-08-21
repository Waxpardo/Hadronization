#!/usr/bin/env python3
"""Quarantine the A2 permissive outputs when the regression has FAILED.

Owner ruling, 2026-08-13: do not leave well-formed outputs on disk protected
only by a paragraph. If the variation cannot reproduce the baseline, its 300
output directories are not a measurement -- they are 300 plausible-looking
directories that will eventually be read by someone who did not read the prose.

WHAT IT DOES. Moves each permissive slot directory into a dated quarantine tree
and writes a manifest recording what moved, why, and what the regression
actually reported. **It moves, never deletes** -- the outputs are the evidence
for whatever went wrong, exactly as the retired replicating extractor is the
evidence for E5.

IT REFUSES TO RUN IF THE REGRESSION PASSED. Quarantining good output would be
its own kind of damage, so the sentinel is read and a PASS aborts.

Usage:
  tools/a2_quarantine_outputs.py --permissive-root /data/.../a2_runs/permissive
      [--sentinel docs/a2_regression_pass.json] [--apply]

Without --apply it prints what it would move and exits 0, changing nothing.
"""
from __future__ import annotations

import argparse
import datetime
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--permissive-root", type=Path, required=True)
    ap.add_argument("--sentinel", type=Path,
                    default=REPO / "docs/a2_regression_pass.json")
    ap.add_argument("--apply", action="store_true",
                    help="actually move. Without it this is a dry run.")
    args = ap.parse_args()

    if not args.sentinel.exists():
        raise SystemExit(
            f"FAIL-CLOSED: no sentinel at {args.sentinel}. Run the regression "
            "comparison first (tools/a2_record_regression.py) -- quarantining "
            "on a guess is not better than leaving the output alone.")
    payload = json.loads(args.sentinel.read_text())
    verdict = payload.get("verdict")
    if verdict == "PASS":
        raise SystemExit(
            "REFUSING: the regression PASSED, so this output is usable and "
            "quarantining it would destroy a valid measurement.")
    if verdict != "FAIL":
        raise SystemExit(f"FAIL-CLOSED: unrecognised verdict {verdict!r}")

    if not args.permissive_root.is_dir():
        raise SystemExit(f"FAIL-CLOSED: {args.permissive_root} is not a directory")

    slots = sorted(
        p for p in args.permissive_root.glob("*/slot_*") if p.is_dir())
    if not slots:
        print("nothing to quarantine: no slot directories found")
        return 0

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
    dest_root = args.permissive_root.parent / f"quarantine_regression_fail_{stamp}"

    print(f"regression verdict : {verdict}")
    print(f"unexpected diffs   : {payload.get('unexpected_difference_count')}")
    print(f"slot directories   : {len(slots)}")
    print(f"destination        : {dest_root}")
    if not args.apply:
        print("\nDRY RUN -- nothing moved. Re-run with --apply.")
        for p in slots[:5]:
            print("   would move", p)
        return 0

    dest_root.mkdir(parents=True, exist_ok=True)
    moved = []
    for src in slots:
        dst = dest_root / src.parent.name / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            raise SystemExit(f"FAIL-CLOSED: {dst} already exists; refusing to "
                             "overwrite a previous quarantine")
        shutil.move(str(src), str(dst))
        moved.append({"from": str(src), "to": str(dst)})

    manifest = dest_root / "MANIFEST.json"
    manifest.write_text(json.dumps({
        "schema": "a2_quarantine_manifest_v1",
        "reason": "A2 regression FAILED -- the variation did not reproduce the "
                  "baseline with its permissive rule disabled, so these outputs "
                  "are not a measurement of anything.",
        "quarantined": datetime.datetime.now(datetime.timezone.utc)
                       .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sentinel": json.loads(args.sentinel.read_text()),
        "directories_moved": len(moved),
        "moves": moved,
        "note": "MOVED, NEVER DELETED. These are the evidence for whatever the "
                "variation got wrong.",
    }, indent=2) + "\n")
    print(f"moved {len(moved)} directories; manifest at {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
