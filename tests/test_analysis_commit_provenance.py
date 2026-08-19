#!/usr/bin/env python3
"""The analysis wrapper must state its commit, never guess it.

THE DEFECT THIS CLOSES. All 301 A2 jobs died on ExitCode 128 because
`run_status_analysis.sh` discovered its provenance with `git rev-parse HEAD`
in a tree deployed by `git archive`, which extracts no `.git`. Under
`set -euo pipefail` that is an instant, total failure with a 143-byte stderr.

The corollary to the deploy-from-a-tracked-commit rule is that an archived tree
carries its commit in the ENVIRONMENT. This test holds the three branches apart:

  1. injected sha, no .git      -> accepted, and reported as injected;
  2. no .git and no injection   -> HARD ERROR, never a guess;
  3. malformed injected sha     -> HARD ERROR;
  4. real checkout, no injection-> still discovers from git (the default is
                                   not broken by adding the new path).

Check 4 is what stops the others being vacuous: a wrapper that took the
injected path always would pass 1-3 and would have silently changed how every
existing checkout-based run records its provenance.

The wrapper exits long before it runs any analysis, so each case is judged on
the provenance message alone -- reaching the NEXT failure is the pass signal.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "analysis/run_status_analysis.sh"

failures = []


def check(name, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        failures.append(f"{name}: {detail}")


def make_tree(tmp: Path, git: bool) -> Path:
    """A tree with the components the wrapper requires present, nothing more."""
    base = tmp / ("checkout" if git else "archived")
    (base / "Validation").mkdir(parents=True)
    (base / "analysis").mkdir(parents=True)
    (base / "Validation/validate_pair_directory.sh").write_text("#!/bin/bash\n")
    (base / "analysis/status_analysis_THnSparse_qq.C").write_text("// stub\n")
    (base / "setupEnv.sh").write_text("# stub\n")
    if git:
        env = dict(os.environ,
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        for args in (["init", "-q"], ["add", "-A"],
                     ["commit", "-qm", "stub", "--no-gpg-sign"]):
            subprocess.run(["git", "-C", str(base)] + args, check=True, env=env,
                           capture_output=True)
    return base


def run(base: Path, raw: Path, injected=None):
    env = dict(os.environ, HADRONIZATION_BASE=str(base))
    env.pop("HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT", None)
    if injected is not None:
        env["HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT"] = injected
    return subprocess.run(
        ["bash", str(WRAPPER), str(raw), str(base / "out")],
        capture_output=True, text=True, env=env)


SHA = "61fe978f66c00e8467f88c00d677462292dd5a1c"

with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    raw = tmp / "raw.root"
    raw.write_text("not really a root file\n")

    # ---- 1. injected sha in an archived tree is accepted -------------------
    archived = make_tree(tmp, git=False)
    r = run(archived, raw, injected=SHA)
    out = r.stdout + r.stderr
    check("archived tree with an injected sha gets past provenance",
          "not a git repository" not in out and "no deploy commit" not in out,
          out[-400:])
    check("and records that the sha was injected, not discovered",
          f"A2_PROVENANCE_SOURCE source=injected_deploy_commit_v1 commit={SHA}"
          in out, out[-400:])

    # ---- 2. archived tree with NO injection is a hard error ----------------
    r = run(archived, raw)
    out = r.stdout + r.stderr
    check("archived tree without an injected sha refuses",
          r.returncode != 0 and "no deploy commit was injected" in out,
          f"rc={r.returncode} {out[-400:]}")
    check("and names the variable that fixes it",
          "HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT" in out, out[-400:])

    # ---- 3. a malformed injected sha is a hard error -----------------------
    for bad, label in ((SHA[:-1], "too short"),
                       (SHA.upper(), "uppercase"),
                       ("not-a-sha" + "0" * 31, "non-hex")):
        r = run(archived, raw, injected=bad)
        out = r.stdout + r.stderr
        check(f"malformed injected sha refuses ({label})",
              r.returncode != 0 and "not a 40-character lowercase sha" in out,
              f"rc={r.returncode} {out[-300:]}")

    # ---- 4. the negative control: a real checkout still DISCOVERS ----------
    checkout = make_tree(tmp, git=True)
    r = run(checkout, raw)
    out = r.stdout + r.stderr
    check("a real checkout still discovers its commit from git",
          "A2_PROVENANCE_SOURCE source=git_checkout_v1" in out, out[-400:])
    check("and the discovered sha is a real 40-character sha",
          any(len(tok) == 40 and all(c in "0123456789abcdef" for c in tok)
              for line in out.splitlines()
              if line.startswith("A2_PROVENANCE_SOURCE")
              for tok in [line.split("commit=")[-1].strip()]),
          out[-400:])

print()
if failures:
    for f in failures:
        print("FAIL:", f)
    sys.exit(1)
print("PASS test_analysis_commit_provenance.py")
