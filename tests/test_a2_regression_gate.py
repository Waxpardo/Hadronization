#!/usr/bin/env python3
"""The A2 consumption gate must actually stop the analyzer.

THE DEFECT THIS CLOSES. The pre-registration makes the regression check a gate
on consuming the permissive output. Between submitting the jobs and mechanizing
this, the gate existed only as a sentence in a document. A sentence does not
stop a script, and 300 well-formed output directories protected by prose is the
exact shape of accident this project keeps writing error-record entries about.

EXTENDED 2026-08-13 for the named variation SET. The gate used to pin one sha
in the analyzer. It now reads `config/a2_variations_v1.json` and requires the
caller to NAME the variation, so three things must agree: the sentinel passes,
its sha is registered, and the name the caller gave resolves to that same sha.

  1. no sentinel                     -> refuses;
  2. sentinel says FAIL              -> refuses;
  3. sentinel sha is UNREGISTERED    -> refuses (a pass certifies ONE macro);
  4. sentinel malformed              -> refuses;
  5. --variation names an UNREGISTERED variation -> refuses;
  6. SHA/NAME DISAGREE, both registered -> refuses;   <-- the new one
  7. valid sentinel + matching name  -> gets PAST the gate;
  8. the other registered variation also passes with ITS name.

Check 6 is the one the redesign exists for. With a set of admissible shas
rather than a single pin, a sentinel left over from the smallest-index arm is
still *registered* -- so membership alone would wave through a largest-index
measurement certified by the wrong regression, and the output would look
perfect. Checks 7 and 8 stop the rest being vacuous: a gate that refuses
everything would pass 1-6 and be useless.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "analysis/a2_block_shift.py"
REGISTRY = REPO / "config/a2_variations_v1.json"

VARIATIONS = json.loads(REGISTRY.read_text())["variations"]
SMALLEST = "permissive_smallest_index"
LARGEST = "permissive_largest_index"

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def run(sentinel: Path, tmp: Path, variation=SMALLEST, registry=REGISTRY):
    # The CSV paths and the run root deliberately do not exist: the gate must
    # fire BEFORE any input is opened, so a missing input must never be what
    # stops us first.
    return subprocess.run(
        [sys.executable, str(TOOL),
         "--baseline", str(tmp / "nope_base.csv"),
         "--permissive", str(tmp / "nope_perm.csv"),
         "--permissive-run-root", str(tmp / "nope_run_root"),
         "--tune", "TEST",
         "--variation", variation,
         "--variations-registry", str(registry),
         "--regression-sentinel", str(sentinel)],
        capture_output=True, text=True)


def write(path: Path, payload) -> Path:
    path.write_text(payload if isinstance(payload, str)
                    else json.dumps(payload, indent=2))
    return path


def sentinel_for(name):
    return {
        "schema": "a2_regression_sentinel_v1",
        "verdict": "PASS",
        "variation_sha256": VARIATIONS[name]["macro_sha256"],
        "compared": "baseline vs regression",
        "recorded": "2026-08-13T00:00:00Z",
    }


VALID = sentinel_for(SMALLEST)

# The registry itself must hold the two arms apart, or every check below is
# comparing a thing to itself.
check("the two registered variations have DIFFERENT shas",
      VARIATIONS[SMALLEST]["macro_sha256"]
      != VARIATIONS[LARGEST]["macro_sha256"])

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)

    # ---- 1. no sentinel ---------------------------------------------------
    r = run(tmp / "absent.json", tmp)
    check("missing sentinel refuses", r.returncode != 0, f"rc={r.returncode}")
    check("missing sentinel says why",
          "No regression sentinel" in (r.stdout + r.stderr),
          (r.stdout + r.stderr)[-200:])

    # ---- 2. verdict FAIL --------------------------------------------------
    bad = dict(VALID, verdict="FAIL")
    r = run(write(tmp / "fail.json", bad), tmp)
    check("FAIL verdict refuses", r.returncode != 0, f"rc={r.returncode}")
    check("FAIL verdict points at quarantine",
          "quarantine" in (r.stdout + r.stderr).lower(),
          (r.stdout + r.stderr)[-200:])

    # ---- 3. unregistered variation sha ------------------------------------
    wrong = dict(VALID, variation_sha256="0" * 64)
    r = run(write(tmp / "wrong.json", wrong), tmp)
    check("unregistered sentinel sha refuses", r.returncode != 0,
          f"rc={r.returncode}")
    check("unregistered sha is named as such",
          "UNREGISTERED" in (r.stdout + r.stderr)
          and "0000000000" in (r.stdout + r.stderr),
          (r.stdout + r.stderr)[-300:])

    # ---- 4. malformed -----------------------------------------------------
    r = run(write(tmp / "broken.json", "{not json"), tmp)
    check("malformed sentinel refuses", r.returncode != 0, f"rc={r.returncode}")
    missing_key = {k: v for k, v in VALID.items() if k != "variation_sha256"}
    r = run(write(tmp / "partial.json", missing_key), tmp)
    check("sentinel missing a required key refuses", r.returncode != 0,
          f"rc={r.returncode}")

    # ---- 5. the caller names a variation that is not registered -----------
    r = run(write(tmp / "good.json", VALID), tmp, variation="no_such_arm")
    out = r.stdout + r.stderr
    check("unregistered --variation refuses", r.returncode != 0,
          f"rc={r.returncode}")
    check("and lists what IS registered",
          SMALLEST in out and LARGEST in out, out[-300:])

    # ---- 6. THE ONE THE REDESIGN EXISTS FOR -------------------------------
    # A sentinel for the smallest-index arm, while claiming to analyse the
    # largest-index arm. Both shas are registered, so a membership-only gate
    # would wave this through and the mislabelled result would look perfect.
    r = run(write(tmp / "good.json", VALID), tmp, variation=LARGEST)
    out = r.stdout + r.stderr
    check("registered-but-WRONG variation refuses", r.returncode != 0,
          f"rc={r.returncode}")
    check("and names both the claim and the evidence",
          LARGEST in out and SMALLEST in out
          and VARIATIONS[LARGEST]["macro_sha256"] in out
          and VARIATIONS[SMALLEST]["macro_sha256"] in out,
          out[-400:])
    check("and does NOT report the gate as passed", "GATE PASSED" not in out,
          out[-200:])

    # ---- 7. the negative control: a valid, MATCHING pair gets THROUGH -----
    r = run(write(tmp / "good.json", VALID), tmp, variation=SMALLEST)
    out = r.stdout + r.stderr
    check("valid sentinel + matching name passes the gate",
          "GATE PASSED" in out, out[-300:])
    check("and then fails on the missing data, not on the gate",
          r.returncode != 0 and "GATE:" not in out, out[-300:])

    # ---- 8. the OTHER arm passes with its own sentinel --------------------
    # Without this, check 6 could be satisfied by a gate that simply always
    # rejects the largest-index name.
    r = run(write(tmp / "largest.json", sentinel_for(LARGEST)), tmp,
            variation=LARGEST)
    out = r.stdout + r.stderr
    check("the largest-index arm passes with ITS OWN sentinel",
          "GATE PASSED" in out and LARGEST in out, out[-300:])

    # ---- 9. a missing/empty registry refuses ------------------------------
    r = run(write(tmp / "good.json", VALID), tmp,
            registry=tmp / "no_registry.json")
    check("absent variations registry refuses", r.returncode != 0,
          f"rc={r.returncode}")
    r = run(write(tmp / "good.json", VALID), tmp,
            registry=write(tmp / "empty.json", {"variations": {}}))
    check("empty variations registry refuses", r.returncode != 0,
          f"rc={r.returncode}")

print()
if failures:
    for f in failures:
        print("FAIL:", f)
    sys.exit(1)
print("PASS test_a2_regression_gate.py")
