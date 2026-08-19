#!/usr/bin/env python3
"""`make check` must not report success on a runtime that cannot run anything.

THE DEFECT (review finding A7). On the reviewed commit `make check` reported
30/30 and exited 0 on a host with Homebrew ROOT 6.38.04 against a pinned
6.30.01, no PYTHIA and no CVMFS -- while `doctor`, inside the same run,
reported two BLOCKING findings. Every component behaved as designed: doctor is
deliberately non-fatal, run_tests.sh accepts any `root` on PATH, and
test_pythia_runtime_contract.py returns success when PYTHIA is absent. The
EMERGENT behaviour was a fully green certification of a machine that cannot run
the pipeline.

THE FIX IS NOT "REFUSE TO RUN OFF-CLUSTER". Most of the suite is
standard-library Python and is genuinely useful on a laptop. What must not
happen is a green run that reads as a pipeline certification. So the verdict is
printed last, an off-pin runtime fails, and HF_ALLOW_UNPINNED_ENV=1 is the
explicit, transcript-visible way to proceed anyway.

Checks:
  1. `check` depends on the verdict, and the verdict runs LAST;
  2. an off-pin runtime fails;
  3. HF_ALLOW_UNPINNED_ENV=1 turns that into success, and SAYS it is not a
     certification -- an escape hatch that hides itself is the original bug;
  4. a fabricated on-pin environment passes without the escape hatch, so
     check 2 is about the pin and not merely about the script always failing;
  5. the verdict names what a green suite does not certify;
  6. README states what `make check` does not certify.
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERDICT = REPO / "tools/environment_verdict.sh"
MAKEFILE = REPO / "Makefile"
README = REPO / "README.md"

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def run_verdict(env_extra=None, path_prefix=None):
    env = dict(os.environ)
    env.pop("HF_ALLOW_UNPINNED_ENV", None)
    if path_prefix:
        env["PATH"] = f"{path_prefix}:{env['PATH']}"
    env.update(env_extra or {})
    return subprocess.run(["bash", str(VERDICT), str(REPO)],
                          capture_output=True, text=True, env=env)


# --- 1. wiring ---------------------------------------------------------------
makefile = MAKEFILE.read_text()
check_line = next((l for l in makefile.splitlines()
                   if l.startswith("check:")), "")
check("`make check` depends on env-verdict", "env-verdict" in check_line,
      check_line)
check("the verdict runs LAST in `check`", check_line.strip().endswith("env-verdict"),
      f"{check_line!r} -- a verdict printed mid-run scrolls away")
check("env-verdict is a real target",
      re.search(r"^env-verdict:", makefile, re.M) is not None, "")

# --- 2. an off-pin runtime fails ---------------------------------------------
r = run_verdict()
out = r.stdout + r.stderr
check("the verdict reports the pinned and found ROOT versions",
      "ROOT pinned:" in out and "ROOT found:" in out, out[:200])
off_pin = "OFF-PIN RUNTIME" in out
if off_pin:
    check("an off-pin runtime FAILS without a declaration", r.returncode != 0,
          f"rc={r.returncode}")
else:
    check("an on-pin runtime passes", r.returncode == 0, f"rc={r.returncode}")

# --- 3. the escape hatch works and announces itself --------------------------
if off_pin:
    r = run_verdict({"HF_ALLOW_UNPINNED_ENV": "1"})
    out = r.stdout + r.stderr
    check("HF_ALLOW_UNPINNED_ENV=1 permits the run", r.returncode == 0,
          f"rc={r.returncode}")
    check("...and says the run is NOT a certification",
          "NOT a pinned-runtime certification" in out, out[-200:])

# --- 4. a fabricated on-pin environment passes -------------------------------
# Without this the failure in check 2 could just mean "this script always
# fails". Stub a `root`/`root-config`/`pythia8-config` matching the pin.
want = re.search(r'HF_ROOT_VERSION:=([^}]*)\}',
                 (REPO / "config/dependencies.conf").read_text())
if want:
    version = want.group(1)
    with tempfile.TemporaryDirectory() as tmp:
        stub = Path(tmp)
        (stub / "root").write_text("#!/bin/sh\nexit 0\n")
        (stub / "root-config").write_text(f"#!/bin/sh\necho {version}\n")
        (stub / "pythia8-config").write_text("#!/bin/sh\necho 8.317\n")
        for name in ("root", "root-config", "pythia8-config"):
            (stub / name).chmod(0o755)
        r = run_verdict(path_prefix=str(stub))
        out = r.stdout + r.stderr
        check("a pinned runtime passes with NO escape hatch",
              r.returncode == 0 and "PINNED RUNTIME" in out,
              f"rc={r.returncode} {out[-300:]}")

# --- 5/6. it says what it does not certify -----------------------------------
text = VERDICT.read_text()
check("the verdict names what a green suite does not certify",
      "does not run" in text.lower() or "NOT certify" in text, "")
readme = README.read_text()
check("README states what `make check` does not certify",
      "does NOT certify" in readme or "does not certify" in readme.lower(), "")
check("README no longer calls the repo-only path the entire extraction chain",
      "This is the entire extraction chain." not in readme,
      "the overstatement is back")

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
