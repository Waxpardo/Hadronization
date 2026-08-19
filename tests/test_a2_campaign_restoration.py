#!/usr/bin/env python3
"""The did-it-work assertion must be campaign-level, and must tolerate a zero job.

THE DEFECT THIS CLOSES (ERROR_RECORD E7). The variation used to throw when a
single job restored nothing. At MONASH's measured ~6 restorations per million
events a 100k-event job restores 0.62 on average, so zero was the MODAL outcome:
49 of 100 MONASH jobs were discarded and none of JUNCTIONS or CLOSEPACKING.
That is selection on the outcome variable, in one arm of the comparison, in the
direction that inflates the measured shift.

The replacement asserts the same thing where it is still true -- across the
whole campaign -- so this test holds four cases apart:

  1. some jobs zero, campaign non-zero -> PASSES, and the zero jobs are COUNTED
     (this is the MONASH shape, and the case the old guard got wrong);
  2. every job zero                    -> REFUSES (the real defect survives);
  3. a job with no A2_PERMISSIVE line  -> REFUSES (silence is not a zero);
  4. no jobs at all                    -> REFUSES.

Case 1 is what stops the others being vacuous: a check that refused whenever it
saw a zero job would pass 2-4 and would reproduce the bias it replaced.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
from a2_block_shift import check_campaign_restoration  # noqa: E402

failures = []


def check(name, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        failures.append(f"{name}: {detail}")


def make_run(root: Path, lines):
    """One slot directory per entry; None means a log with no A2_PERMISSIVE line."""
    for index, line in enumerate(lines):
        slot = root / f"slot_{index:03d}"
        slot.mkdir(parents=True)
        body = "Environment set:\n" + ("" if line is None else line + "\n")
        (slot / "analysis.log").write_text(body)
    return root


def line(charm, beauty, contested=0):
    return (f"A2_PERMISSIVE restored_charm={charm} restored_beauty={beauty} "
            f"contested_seen_charm={contested} contested_seen_beauty=0 "
            f"events_touched={1 if charm + beauty else 0} "
            f"selected_events=100000")


with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)

    # ---- 1. the MONASH shape: half the jobs zero, campaign non-zero --------
    mixed = make_run(tmp / "mixed",
                     [line(0, 0, 3), line(1, 0, 5), line(0, 0, 0), line(0, 1, 2)])
    try:
        summary = check_campaign_restoration(mixed, "MIXED")
        ok = True
    except SystemExit as exc:
        summary, ok = {}, False
        detail = str(exc)
    check("a campaign with zero-restoration jobs still PASSES", ok,
          locals().get("detail", ""))
    if ok:
        check("and the zero jobs are counted, not hidden",
              summary["zero_restoration_jobs"] == 2, str(summary))
        check("and the restored totals are summed across jobs",
              summary["charm"] == 1 and summary["beauty"] == 1, str(summary))
        check("and contested_seen is carried through",
              summary["contested_seen"] == 10, str(summary))

    # ---- 2. the real defect still refuses ----------------------------------
    allzero = make_run(tmp / "allzero", [line(0, 0), line(0, 0), line(0, 0)])
    try:
        check_campaign_restoration(allzero, "ALLZERO")
        check("a campaign that restored NOTHING refuses", False, "no SystemExit")
    except SystemExit as exc:
        check("a campaign that restored NOTHING refuses",
              "restored NOTHING" in str(exc), str(exc))

    # ---- 3. silence is not a zero ------------------------------------------
    silent = make_run(tmp / "silent", [line(5, 0), None])
    try:
        check_campaign_restoration(silent, "SILENT")
        check("a job with no A2_PERMISSIVE line refuses", False, "no SystemExit")
    except SystemExit as exc:
        check("a job with no A2_PERMISSIVE line refuses",
              "carries no A2_PERMISSIVE line" in str(exc), str(exc))

    # ---- 4. an empty run root refuses --------------------------------------
    empty = tmp / "empty"
    empty.mkdir()
    try:
        check_campaign_restoration(empty, "EMPTY")
        check("an empty run root refuses", False, "no SystemExit")
    except SystemExit as exc:
        check("an empty run root refuses", "no permissive job logs" in str(exc),
              str(exc))

    # ---- 5. the pre-guard-removal log format is still readable -------------
    legacy = tmp / "legacy"
    legacy.mkdir()
    (legacy / "slot_000").mkdir()
    (legacy / "slot_000/analysis.log").write_text(
        "A2_PERMISSIVE restored_charm=7 restored_beauty=0 events_touched=7 "
        "selected_events=100000\n")
    try:
        summary = check_campaign_restoration(legacy, "LEGACY")
        check("logs written before contested_seen existed still parse",
              summary["charm"] == 7 and summary["contested_seen"] == 0,
              str(summary))
    except SystemExit as exc:
        check("logs written before contested_seen existed still parse", False,
              str(exc))

print()
if failures:
    for f in failures:
        print("FAIL:", f)
    sys.exit(1)
print("PASS test_a2_campaign_restoration.py")
