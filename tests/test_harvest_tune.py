#!/usr/bin/env python3
"""Require the harvest driver to reproduce MONASH and reject closure failures.

The positive case uses the recorded MONASH closure line and committed anchors.

The negative cases matter more than usual. `1800/600` is the v2-sidecar
resolution failure: the closure runs against the wrong schema, produces fewer
comparisons, and STILL REPORTS errors=0. Anything that greps for the error count
calls that a pass. This function must reject that count pair.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "extraction/pipeline"))
from harvest_tune import closure_verdict  # noqa: E402

DRIVER = REPO / "extraction/pipeline/harvest_tune.py"
DEDUP = REPO / "AnalysisScripts/anchors/merged_monash_dedup"

# MONASH's real closure output, as recorded in the MONASH central table §1.
MONASH_CLOSURE = (
    "PAIR_BLOCK_CLOSURE errors=0 "
    "analysis_schema=paul_pair_objects_primary_ground_v3 "
    "central_pair_files=300 block_pair_files=3000 "
    "object_content_sumw2_closure_checks=2100 "
    "additive_metadata_closure_checks=3600 "
    "invariant_metadata_checks=1500 source_filter_contract_checks=300 "
    "expected_central_events=-1 relative_tolerance=2e-10"
)

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


# ---- the known tune ------------------------------------------------------
v = closure_verdict(MONASH_CLOSURE)
check("MONASH's recorded closure line is a PASS", v["verdict"] == "PASS",
      str(v["failures"]))

# ---- the failure modes, each independently ------------------------------
sidecar = (MONASH_CLOSURE
           .replace("object_content_sumw2_closure_checks=2100",
                    "object_content_sumw2_closure_checks=1800")
           .replace("invariant_metadata_checks=1500",
                    "invariant_metadata_checks=600"))
v = closure_verdict(sidecar)
check("1800/600 with errors=0 is a FAIL", v["verdict"] == "FAIL")
check("and it is named as the v2-sidecar failure mode",
      any("sidecar" in f for f in v["failures"]), str(v["failures"]))

v = closure_verdict(MONASH_CLOSURE.replace(
    "paul_pair_objects_primary_ground_v3", "paul_pair_objects_primary_ground_v2"))
check("the v2 schema is a FAIL", v["verdict"] == "FAIL")

v = closure_verdict(MONASH_CLOSURE.replace("errors=0", "errors=1"))
check("errors=1 is a FAIL", v["verdict"] == "FAIL")

v = closure_verdict(MONASH_CLOSURE.replace("central_pair_files=300",
                                           "central_pair_files=299"))
check("a short central file count is a FAIL", v["verdict"] == "FAIL")

v = closure_verdict("some log with no closure line at all\n")
check("a missing closure line is a FAIL, not a crash", v["verdict"] == "FAIL")

# A truncated line that happens to contain errors=0 must not sneak through on
# the strength of the one field a careless reader checks.
v = closure_verdict("PAIR_BLOCK_CLOSURE errors=0\n")
check("errors=0 alone is not sufficient", v["verdict"] == "FAIL",
      str(v["failures"]))

# ---- the driver's exit status, end to end -------------------------------
with tempfile.TemporaryDirectory() as td:
    good = Path(td) / "good.log"
    good.write_text(MONASH_CLOSURE + "\n")
    r = subprocess.run([sys.executable, str(DRIVER), "MONASH",
                        "--stage", "closure", "--closure-log", str(good)],
                       capture_output=True, text=True)
    check("driver exits 0 on MONASH's closure", r.returncode == 0,
          r.stdout[-300:])

    bad = Path(td) / "bad.log"
    bad.write_text(sidecar + "\n")
    r = subprocess.run([sys.executable, str(DRIVER), "MONASH",
                        "--stage", "closure", "--closure-log", str(bad)],
                       capture_output=True, text=True)
    check("driver exits non-zero on 1800/600", r.returncode != 0)
    check("and prints the failing line verbatim",
          "PAIR_BLOCK_CLOSURE" in r.stdout and "1800" in r.stdout,
          r.stdout[-300:])

# ---- the decomposition stage must reproduce the recorded MONASH values ---
r = subprocess.run([sys.executable, str(DRIVER), "MONASH",
                    "--stage", "decompose", "--rundir", str(DEDUP)],
                   capture_output=True, text=True)
out = r.stdout
check("decompose stage exits 0 on the committed MONASH anchors",
      r.returncode == 0, out[-400:])
check("I3 is exact at the recorded total",
      "I3 block-sum == central : PASS" in out and "53662416" in out,
      out[:300])
check("I2 is clean under the MAD null",
      "I2 block-vs-central     : PASS (0 flags in 10 comparisons)" in out,
      out[:400])
for group, value in (("kCentralGround", "52.4959"),
                     ("kExcludedVector", "46.4946"),
                     ("kExcludedExcited", "1.0095")):
    check(f"reproduces {group} = {value}",
          any(group in line and value in line for line in out.splitlines()),
          "")

print()
if failures:
    for f in failures:
        print("FAIL:", f)
    sys.exit(1)
print("PASS test_harvest_tune.py")
