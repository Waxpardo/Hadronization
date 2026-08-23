#!/usr/bin/env python3
"""The three-tune table and the b-baryon advisory, pinned against MONASH.

A TOOL THAT PRODUCES A PUBLISHED NUMBER MUST REPRODUCE A KNOWN ONE. Both tools
here fed the published central tables, so both are run against the committed
MONASH anchor (`AnalysisScripts/anchors/merged_monash_dedup`) and required to
return the values those tables record. The tables are held in the internal
repository.
That is the same discipline test_harvest_tune.py applies to the harvest driver.

TWO PROPERTIES ARE PINNED THAT ARE EASY TO "FIX" INTO ERRORS.

  * The structural table is a PARTITION and must sum to 100 %. The
    experiment-comparable table is a SELECTION and must NOT -- it is the largest
    observables a detector reconstructs, not a decomposition. A future reader
    who notices the second column summing to ~93 % and normalises it would turn
    a correct table into a wrong one, so the non-sum is asserted here as a
    requirement rather than tolerated as a quirk.
  * The advisory NEVER fails. It reports ratios and a direction; a hard gate at
    1.00 would be refusing real physics (apply_decay_map.py says so in terms).
    Its exit status is pinned at 0 even though MONASH's own Sigma_b ratios sit
    at 1.59, far outside any plausible threshold.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ANCHOR = REPO / "AnalysisScripts/anchors/merged_monash_dedup"
TABLE = REPO / "extraction/three_tune_table.py"
ADVISORY = REPO / "extraction/bbaryon_tune_advisory.py"

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def run(script):
    return subprocess.run([sys.executable, str(script), f"MONASH={ANCHOR}"],
                          capture_output=True, text=True)


# ---- the three-tune table on the known tune ------------------------------
r = run(TABLE)
out = r.stdout
check("three_tune_table exits 0 on the committed MONASH anchor",
      r.returncode == 0, r.stderr[-300:])

# MONASH central table section 0, structural.
for group, value, sem in (("kCentralGround", "52.4959", "0.0074"),
                          ("kExcludedVector", "46.4946", "0.0079"),
                          ("kExcludedExcited", "1.0095", "0.0012")):
    check(f"structural {group} reproduces {value} +/- {sem}",
          any(group in ln and value in ln and sem in ln
              for ln in out.splitlines()),
          out[:200])

# MONASH central table section 0, experiment-comparable (map v2, split).
for species, value in (("D0", "25.4543"), ("Dbar0", "25.3809"),
                       ("D+", "13.2505"), ("D-", "13.2225"),
                       ("D_s+", "4.2720"), ("D_s-", "4.2684"),
                       ("B+", "2.1441"), ("B-", "2.1431")):
    check(f"experiment-comparable {species} reproduces {value}",
          any(ln.strip().startswith(f"| {species} ") and value in ln
              for ln in out.splitlines()),
          out[:200])

# ---- the partition / selection distinction, both directions --------------
check("the structural table sums to 100.0000 %",
      "MONASH sum = 100.0000 %" in out, out[:300])
sel = [ln for ln in out.splitlines() if "selection sums to" in ln]
check("the experiment-comparable table reports its own non-100 total",
      len(sel) == 1, str(sel))
if sel:
    total = float(sel[0].split("selection sums to")[1].split("%")[0])
    check("and that total is NOT 100 % -- it is a selection, not a partition",
          abs(total - 100.0) > 1.0, f"got {total}")
check("the selection caveat is printed above the table, not after it",
      out.index("NOT a partition") < out.index("| D0"), "caveat is misplaced")

# ---- the advisory ---------------------------------------------------------
r = run(ADVISORY)
out = r.stdout
check("bbaryon_tune_advisory exits 0", r.returncode == 0, r.stderr[-300:])
check("it never fails on a large asymmetry: MONASH Sigma_b0 is 1.5858",
      "1.5858" in out and r.returncode == 0, out[:200])
for species, value in (("Sigma_b+", "1.6377"), ("Sigma_b-", "1.5950"),
                       ("Xi'_b0", "1.7572"), ("Lambda_b0", "1.0124")):
    check(f"advisory {species} reproduces {value}",
          any(ln.startswith(species) and value in ln for ln in out.splitlines()),
          out[:200])
check("the advisory names itself advisory-only",
      "advisory only" in out, out[:200])
check("ratios are raw -- the advisory says it applies no map",
      "no map" in out, out[:200])

# ---- all three tunes, and the digest GOLDEN_OUTPUTS 2.9c pins ------------
# Since 2026-08-16 the JUNCTIONS and CLOSEPACKING anchors are committed, so the
# FINAL table regenerates from the repository alone -- it no longer depends on
# run directories that live only on stbc-i3. That is what makes the digest below
# meaningful as a gate rather than as a note.
import hashlib  # noqa: E402

THREE = {t: ANCHOR_DIR for t, ANCHOR_DIR in (
    ("MONASH", ANCHOR),
    ("JUNCTIONS", REPO / "AnalysisScripts/anchors/merged_junctions_dedup"),
    ("CLOSEPACKING", REPO / "AnalysisScripts/anchors/merged_closepacking_dedup"),
)}
for tune, path in THREE.items():
    check(f"{tune} anchor is committed", path.is_dir(), str(path))

r = subprocess.run([sys.executable, str(TABLE)]
                   + [f"{t}={p}" for t, p in THREE.items()],
                   capture_output=True, text=True)
check("three-tune table exits 0 on the committed anchors", r.returncode == 0,
      r.stderr[-300:])
out = r.stdout

# Three-tune central table section 1, every structural cell.
FINAL = {
    "kCentralGround":   [("52.4959", "0.0074"), ("58.2318", "0.0078"), ("54.1697", "0.0112")],
    "kExcludedVector":  [("46.4946", "0.0079"), ("39.9409", "0.0083"), ("39.9976", "0.0105")],
    "kExcludedExcited": [("1.0095", "0.0012"), ("1.7821", "0.0015"), ("5.7745", "0.0050")],
    "kMultiplyHeavy":   [("0.0000", "0.0000"), ("0.0452", "0.0004"), ("0.0583", "0.0007")],
}
for group, cells in FINAL.items():
    line = next((ln for ln in out.splitlines()
                 if ln.strip().startswith(f"| {group} ")), "")
    for value, sem in cells:
        check(f"three-tune {group} carries {value} ± {sem}",
              value in line and sem in line, line.strip())

check("the structural table sums to 100 % for every tune",
      sum("sum = 100.0000 %" in ln for ln in out.splitlines()) == 3, out[-400:])

# The digest recorded in docs/GOLDEN_OUTPUTS.md 2.9c and in the three-tune
# central table's section 7 regeneration recipe.
PINNED = "a46a7f6b96f668177ee600746e51eadf1dfaabdaceac07c1265ef5d7d0fc930d"
digest = hashlib.sha256(out.encode()).hexdigest()
check("the table's stdout matches the digest pinned in GOLDEN_OUTPUTS 2.9c",
      digest == PINNED, f"got {digest}")

# The advisory over three tunes reverses its own loose pre-registration; the
# direction is the finding, so pin that it is still reported and still 0 of 13.
r = subprocess.run([sys.executable, str(ADVISORY)]
                   + [f"{t}={p}" for t, p in THREE.items()],
                   capture_output=True, text=True)
check("advisory exits 0 over three tunes", r.returncode == 0, r.stderr[-300:])
for tune in ("JUNCTIONS", "CLOSEPACKING"):
    check(f"advisory reports {tune} against MONASH",
          any(tune in ln and ">= MONASH in" in ln
              for ln in r.stdout.splitlines()), r.stdout[-300:])

print()
if failures:
    for f in failures:
        print("FAIL:", f)
    sys.exit(1)
print("PASS test_three_tune_tables.py")
