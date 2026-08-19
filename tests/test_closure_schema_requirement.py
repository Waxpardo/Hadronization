#!/usr/bin/env python3
"""The v3 closure gate must REJECT a complete v2 dataset.

THE DEFECT (review finding A4). `validate_pair_block_closure.sh` read the schema
out of its input and then derived every expected count FOR THAT SCHEMA, and
`ValidatePairBlockClosure.C` adopted whatever the first central file declared.
So a complete, internally consistent v2 directory passed at 1800/600 -- the
exact state README says must be treated as failure -- because nothing anywhere
compared the schema FOUND against the schema WANTED.

**A gate whose expectations are supplied by the thing under test cannot fail
it.** The recorded MONASH transcript really was v3/2100/1500; the defect is that
the reusable gate could not stop the next campaign silently reverting to v2.

The fix is a REQUIRED third argument naming the campaign's schema, enforced in
two independent places: the wrapper (which survives a caller that bypasses the
macro) and the macro (which survives a caller that bypasses the wrapper).

Checks:
  1. the wrapper refuses to run with the schema argument omitted;
  2. it refuses an unknown schema name;
  3. it gives a specific message for the OLD signature (a number in slot 3),
     rather than a confusing "unknown schema";
  4. it accepts both `v3` and the full tag;
  5. the wrapper compares declared against required and says so;
  6. the macro takes the argument, refuses an empty one, and carries the
     mismatch check -- asserted on the source, since running it needs a
     300-file ROOT dataset this repository does not commit.

Check 1 is the regression: pre-fix, two arguments were a valid invocation.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WRAPPER = REPO / "Validation/validate_pair_block_closure.sh"
MACRO = REPO / "Validation/ValidatePairBlockClosure.C"

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def run(*args):
    return subprocess.run(["bash", str(WRAPPER), *args],
                          capture_output=True, text=True)


# --- 1. the schema argument is required --------------------------------------
r = run("/nonexistent/central", "/nonexistent/blocks")
out = r.stdout + r.stderr
check("two arguments are refused (pre-fix this was a valid invocation)",
      r.returncode == 2 and "EXPECTED_SCHEMA" in out,
      f"rc={r.returncode} {out[:200]}")
check("the usage text explains why the schema is required",
      "not derived from the data" in out.lower()
      or "deliberately NOT derived" in out, out[:300])

# --- 2. an unknown schema is refused -----------------------------------------
r = run("/nonexistent/central", "/nonexistent/blocks", "v9")
out = r.stdout + r.stderr
check("an unknown schema name is refused", r.returncode == 2 and "v9" in out,
      f"rc={r.returncode} {out[:200]}")

# --- 3. the old signature gets a specific message ----------------------------
r = run("/nonexistent/central", "/nonexistent/blocks", "1000000")
out = r.stdout + r.stderr
check("a numeric third argument is diagnosed as the old signature",
      r.returncode == 2 and "fourth position" in out,
      f"rc={r.returncode} {out[:200]}")

# --- 4. v3 and the full tag are both accepted past validation ----------------
# These proceed past argument parsing and then fail for a real reason (the
# directories do not exist / ROOT). What must NOT happen is a rejection at the
# schema-argument stage.
for accepted in ("v3", "paul_pair_objects_primary_ground_v3"):
    r = run("/nonexistent/central", "/nonexistent/blocks", accepted)
    out = r.stdout + r.stderr
    check(f"{accepted!r} passes schema-argument validation",
          "is not a known schema" not in out and "unknown EXPECTED_SCHEMA" not in out,
          out[:200])

# --- 5. the wrapper enforces declared == required ----------------------------
text = WRAPPER.read_text()
check("the wrapper compares the declared schema against the required one",
      re.search(r'\$\{declared_schema\}"?\s*!=\s*"?\$\{expected_schema\}', text)
      is not None,
      "no declared-vs-expected comparison found")
check("the wrapper names the 1800/600 failure mode in its error",
      "1800/600" in text, "")
check("the wrapper passes the expected schema to the macro",
      "expected_schema}\\\"" in text or "${expected_schema}" in
      text.split("root -l -b -q")[1][:400],
      "not forwarded to ValidatePairBlockClosure.C")

# --- 6. the macro carries the requirement too --------------------------------
macro = MACRO.read_text()
check("the macro takes an expectedSchema parameter",
      "const char* expectedSchema" in macro, "")
check("the macro refuses an empty expected schema",
      "requiredSchema.empty()" in macro
      and "EXPECTED_SCHEMA is required" in macro, "")
check("the macro fails when the declared schema differs from the required one",
      "declared != requiredSchema" in macro, "")
check("the macro's mismatch error names the failure mode",
      "1800/600" in macro, "")

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
