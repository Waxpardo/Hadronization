#!/usr/bin/env python3
"""The output-side assertion, and the mutation the nine request-side gates missed.

WHAT THIS GUARDS. `tests/test_measurement_target.py` carries nine mutations and
every one of them gates the REQUEST -- a dataset status, a measurement root, a
target combination, a source pattern -- and every one runs BEFORE the render.
They all passed on 2026-08-19 while three canvases landed in a publication
output path. A suite that only tests refusals certifies a locked door, not an
empty room.

These tests certify the room. The anchor case is not constructed: it is the
real 2026-08-19 15:14 render, with the mtimes and the window read off the
cluster, and it MUST fail the assertion.
"""
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from assert_measurement_outputs import (  # noqa: E402
    assess, discover_publication_trees, files_in_window, missing_artifacts)

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


# --- the historical mutation ----------------------------------------------
# The defective control render of 2026-08-19, read from the cluster on
# 2026-08-19 by `find -printf "%T@ %p"` and `date -d ... +%s`:
#
#   window   15:09:45+02:00 .. 15:14:02+02:00   = 1787144985 .. 1787145242
#   canvases 15:14:02                            = 1787145242   (three files)
#   receipt  13:19:54, an earlier render         = 1787138394
#
# 1787145242 - 1787144985 = 257 s = 4 min 17 s, which is 15:09:45 to 15:14:02.
# 1787145242 - 1787138394 = 6848 s = 1 h 54 min 8 s, which is 13:19:54 to 15:14:02.
PUBLICATION = ("${HADRONIZATION_DATA_ROOT}/sys_plot_deploy/plotting/Plots"
               "/THnSparseCompleteRoot_HF_RUN3_V1")
STEM = f"{PUBLICATION}/global_balancing_plots_multiplicity_HF_RUN3_V1_THREETUNE"
HISTORICAL_ENTRIES = [
    (f"{PUBLICATION}/multiplicity_boundary_receipt_v1.json", 1787138394),
    (f"{STEM}_MACRO.C", 1787145242),
    (f"{STEM}_PDF.pdf", 1787145242),
    (f"{STEM}_PNG.png", 1787145242),
]
HISTORICAL_WINDOW = (1787144985, 1787145242)

touched = files_in_window(HISTORICAL_ENTRIES, *HISTORICAL_WINDOW)
check("the real 2026-08-19 15:14 render is caught: three files, not four",
      touched == [f"{STEM}_MACRO.C", f"{STEM}_PDF.pdf", f"{STEM}_PNG.png"],
      str(touched))
check("the 13:19 boundary receipt is NOT attributed to the 15:14 window",
      f"{PUBLICATION}/multiplicity_boundary_receipt_v1.json" not in touched)

verdict = assess(HISTORICAL_ENTRIES, *HISTORICAL_WINDOW,
                 expected=["log", "measurement_receipt.json"],
                 present=["log", "measurement_receipt.json"])
check("the historical render FAILS the assertion outright",
      verdict["passed"] is False and verdict["publication_tree_clean"] is False,
      str(verdict["passed"]))
check("it fails on the publication tree, not on missing artifacts",
      verdict["measurement_artifacts_complete"] is True
      and verdict["publication_files_touched_count"] == 3,
      str(verdict))

# THE EDGE IS THE WHOLE POINT. The three canvases carry the window's own end
# timestamp to the second. An exclusive upper bound would have called the real
# defect clean.
check("an exclusive upper bound would have MISSED the real defect",
      [p for p, m in HISTORICAL_ENTRIES
       if HISTORICAL_WINDOW[0] <= m < HISTORICAL_WINDOW[1]] == [],
      "the historical case sits exactly on the edge")

# --- constructed cases ----------------------------------------------------
check("a file written before the window is clean",
      files_in_window([("a", 100)], 200, 300) == [])
check("a file written after the window is clean",
      files_in_window([("a", 400)], 200, 300) == [])
check("the lower edge is inclusive", files_in_window([("a", 200)], 200, 300) == ["a"])
check("the upper edge is inclusive", files_in_window([("a", 300)], 200, 300) == ["a"])
check("a file inside the window is caught",
      files_in_window([("a", 250)], 200, 300) == ["a"])

try:
    files_in_window([], 300, 200)
    check("an inverted window is refused", False, "no exception")
except ValueError:
    check("an inverted window is refused", True)

check("a missing artifact is reported",
      missing_artifacts(["plots/x.pdf", "log"], ["log"]) == ["plots/x.pdf"])
check("no missing artifact reports nothing",
      missing_artifacts(["log"], ["log", "extra"]) == [])

clean = assess([("a", 100)], 200, 300, ["log"], ["log"])
check("a clean render passes", clean["passed"] is True, str(clean))

incomplete = assess([("a", 100)], 200, 300, ["log", "plots/x.pdf"], ["log"])
check("a render missing its own artifacts FAILS",
      incomplete["passed"] is False
      and incomplete["missing_measurement_artifacts"] == ["plots/x.pdf"],
      str(incomplete))

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    checkout = root / "checkout"
    external = root / "external-results"
    (checkout / "plotting").mkdir(parents=True)
    external.mkdir()
    (checkout / "plotting" / "Plots").symlink_to(
        external, target_is_directory=True
    )
    discovered = discover_publication_trees([str(checkout)])
    check(
        "the ignored publication symlink resolves to its external target",
        discovered == [str(external.resolve())],
        str(discovered),
    )

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'ALL CHECKS PASS'}")
sys.exit(1 if failures else 0)
