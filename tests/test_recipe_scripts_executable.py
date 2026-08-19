#!/usr/bin/env python3
"""Every script a Golden Output recipe invokes directly must be executable.

THE DEFECT (review finding A8). `GOLDEN_OUTPUTS.md` §4 documents recipes as
bare invocations -- `tools/build_decay_parent_map_v2.py ...` -- but four of the
scripts did not have the executable bit set. R6, R7 and R10 exited **126,
permission denied**. The documented end-to-end path stopped at its second
command.

WHY A TEST AND NOT JUST A CHMOD. The mode bit is a property of the file that
nothing else in the suite reads, so it can be lost by a copy, a patch applied
with the wrong tool, or a `git checkout` from a tree where it was never set.
The chmod fixes today; this fixes tomorrow.

It also checks the shebang, because the executable bit alone is not enough: a
file with `+x` and no `#!` line is executed by the invoking shell, which for a
Python script fails in a far more confusing way than 126 does.

Two further checks guard the OTHER half of A8: that R7 carries `--mode split`
(without it the recipe silently produced v1.1 dominant shares, not the v2 split
shares it claimed) and that R8 is labelled as the history row rather than as
"THE NUMBER" it does not compute.
"""
import os
import re
import stat
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GOLDEN = REPO / "docs/GOLDEN_OUTPUTS.md"

# Every script invoked bare by a recipe in GOLDEN_OUTPUTS.md S4.
RECIPE_SCRIPTS = [
    "tools/build_decay_parent_map.py",
    "tools/build_decay_parent_map_v2.py",
    "tools/reconstruct_deduplicated_decomposition.py",
    "extraction/apply_decay_map.py",
    "extraction/second_branch_weight.py",
    "extraction/aggregate_m7.py",
    "extraction/compare_subset_parent.py",
    "extraction/extract_species_decomposition.py",
    "extraction/decompose_with_block_sems.py",
]

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


for rel in RECIPE_SCRIPTS:
    path = REPO / rel
    if not path.exists():
        check(f"{rel} exists", False, "missing")
        continue
    mode = path.stat().st_mode
    check(f"{rel} is executable",
          bool(mode & stat.S_IXUSR) and os.access(path, os.X_OK),
          f"mode={stat.filemode(mode)} -- a bare recipe invocation exits 126")
    check(f"{rel} has a shebang",
          path.read_bytes().startswith(b"#!"),
          "executable without #! is run by the calling shell")

# --- the R7 / R8 corrections -------------------------------------------------
golden = GOLDEN.read_text()

r7 = [l for l in golden.splitlines() if re.match(r"\|\s*\*{0,2}R7\*{0,2}\s*\|", l)]
check("R7 is documented in the recipe table", len(r7) == 1, f"found {len(r7)}")
if r7:
    check("R7 carries --mode split",
          "--mode split" in r7[0],
          "without it the recipe reproduces v1.1 dominant shares (28.1301), "
          "not the v2 split shares (25.2435) it claims")

r8 = [l for l in golden.splitlines() if re.match(r"\|\s*\*{0,2}R8\*{0,2}\s*\|", l)]
check("R8 is documented in the recipe table", len(r8) == 1, f"found {len(r8)}")
if r8:
    check("R8 states which row it actually reproduces",
          "12.8396" in r8[0] and "chained" in r8[0].lower(),
          "R8 prints the (C) chained history value, not the 0.0018% "
          "post-split figure declared as THE NUMBER")
    check("R8 does not claim to produce THE NUMBER",
          "0.0018" not in r8[0], r8[0][:120])

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
