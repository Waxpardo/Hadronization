#!/usr/bin/env python3
"""The closure probe, including the false negative it exists to prevent.

THE ANCHOR IS THE REAL CASE. `HF_SYS_MUR_UP` closed first and closed cleanly,
and its merge log holds NO markers, because its closure was re-run separately on
2026-08-19 after a schema correction. A probe reading only the merge log calls
it 0/3. The last line of `closure_HF_SYS_MUR_UP.log` is its CLOSEPACKING PASS.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from campaign_closure_status import (  # noqa: E402
    REQUIRED_MARKERS, candidate_logs, closure_status, tunes_marked)

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def marker(tune: str) -> str:
    return (f"CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune={tune} "
            f"report=/data/alice/ipardoza/hadronization_analysis/X/validation/y.log")


ALL_THREE = "\n".join(marker(t) for t in ("MONASH", "JUNCTIONS", "CLOSEPACKING"))

# --- THE FALSE NEGATIVE ---------------------------------------------------
# The merge log is silent; the closure re-run log carries all three.
mur_up = closure_status({"merge_HF_SYS_MUR_UP.log": "PROMOTED_MERGE ...\n",
                         "closure_HF_SYS_MUR_UP.log": ALL_THREE})
check("a campaign closed by a RE-RUN reads 3/3, not 0/3",
      mur_up["markers"] == 3 and mur_up["closed"] is True, str(mur_up["markers"]))
check("and the answering log is named, so the provenance is visible",
      mur_up["answering_logs"] == ["closure_HF_SYS_MUR_UP.log"],
      str(mur_up["answering_logs"]))
check("reading the merge log ALONE is the false negative this closes",
      closure_status({"merge_HF_SYS_MUR_UP.log": "PROMOTED_MERGE ...\n"}
                     )["markers"] == 0)

# --- the ordinary case ----------------------------------------------------
ordinary = closure_status({"merge_HF_SYS_MUF_UP.log": ALL_THREE})
check("a campaign closed by the merge driver reads 3/3",
      ordinary["markers"] == 3 and ordinary["closed"] is True)
check("its answering log is the merge log",
      ordinary["answering_logs"] == ["merge_HF_SYS_MUF_UP.log"])

# --- partial and absent ---------------------------------------------------
partial = closure_status({"merge_X.log": marker("MONASH")})
check("one marker of three is NOT closed",
      partial["markers"] == 1 and partial["closed"] is False)
check("and it names which tune closed",
      partial["tunes_closed"] == ["MONASH"], str(partial["tunes_closed"]))
check("no log at all is 0/3, not an error",
      closure_status({})["markers"] == 0)
check("a log with products but no markers is 0/3",
      closure_status({"merge_X.log": "PROMOTED_MERGE a\nPROMOTED_MERGE b\n"}
                     )["markers"] == 0)

# --- a repeated line must not inflate the count ---------------------------
doubled = closure_status({"closure_X.log": ALL_THREE + "\n" + ALL_THREE})
check("a re-run that logged every marker twice still reads 3/3",
      doubled["markers"] == 3, str(doubled["markers"]))

# --- the union across both logs -------------------------------------------
split = closure_status({"merge_X.log": marker("MONASH"),
                        "closure_X.log": marker("JUNCTIONS") + "\n"
                                         + marker("CLOSEPACKING")})
check("markers split across the two logs are unioned to 3/3",
      split["markers"] == 3 and split["closed"] is True, str(split))
check("and both answering logs are named",
      split["answering_logs"] == ["closure_X.log", "merge_X.log"],
      str(split["answering_logs"]))

# --- parsing details ------------------------------------------------------
check("an unknown tune name is not counted",
      tunes_marked(marker("SOMETHING_ELSE")) == set())
check("a marker mentioned in prose is not counted",
      tunes_marked("we saw CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=MONASH once")
      == set(), "the line must START with the marker")
check("three tunes are required", REQUIRED_MARKERS == 3)

# --- the candidate order --------------------------------------------------
names = [p.name for p in candidate_logs(Path("/m"), "HF_SYS_MUR_UP")]
check("the closure re-run log is looked at first",
      names == ["closure_HF_SYS_MUR_UP.log", "merge_HF_SYS_MUR_UP.log"],
      str(names))

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'ALL CHECKS PASS'}")
sys.exit(1 if failures else 0)
