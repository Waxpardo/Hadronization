#!/usr/bin/env python3
"""No source directory may be swallowed by a .gitignore rule.

THE DEFECT (2026-08-13). `.gitignore` carried a stale `/Analysis/` rule. The
restructure created a **lowercase** `analysis/` SOURCE directory, and on a
case-insensitive filesystem (`core.ignorecase=true`, the macOS default) the
capitalised rule matched it. Git applies ignore rules only to UNTRACKED paths,
so every file added there BEFORE the restructure kept working normally and the
trap stayed completely invisible -- while `analysis/a2_block_shift.py`, the
gated analyzer the entire A2 pre-registration hangs on, and
`analysis/a2_pair_yield.C` had **never been committed at all**.

Nothing failed. No command errored. `git status` was clean, because an ignored
file is not untracked in any way git reports by default. The files simply were
not there, and would not have been there for anyone who cloned the repository.

WHY THREE CHECKS AND NOT ONE. The three catch it at different stages, and the
cheapest one catches it earliest:

  A. A directory that already holds tracked files must not be ignored.
     This is the state the bug actually reached. It is the strongest check --
     tracked-and-ignored is never intentional -- but it only fires once some
     file in the directory has been committed.

  B. No ignore rule may match a real directory ONLY when case is folded.
     This is the trap itself, caught before a single file goes missing, and it
     is filesystem-independent: it fails on Linux too, where the rule would be
     harmless on Linux and unsafe on a case-folding filesystem.

  C. An ignored directory must not contain source-like files unless it is
     named here as a deliberate exception.
     This catches a directory swallowed WHOLE, where check A is blind because
     nothing in it was ever committed.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Directories that are ignored ON PURPOSE and may legitimately contain files
# with source-like extensions. Every entry needs a reason.
DELIBERATELY_IGNORED = {
    # Generated production/analysis output roots. Data, not code.
    "campaigns": "generated campaign output; the freeze dir is the tracked input",
    "Production": "generated production output",
    "AnalyzedData": "merged ROOT output, kept on Nikhef storage",
    "AnalysisOutput": "generated",
    "AnalysisResults": "generated",
    "RootFiles": "large binary ROOT output",
    "logs": "job logs",
    "Logs": "job logs",
    "Jobs": "job scratch",
    # Working paper draft, deliberately untracked so plotting/production
    # branches never overwrite it.
    "Paper/Heavy_flavour_hadronisation_model_paper": "working draft, untracked by design",
    # Local scratch/tooling.
    ".codex-tmp": "scratch",
    ".vscode": "editor state",
    "__pycache__": "bytecode",
    "graphify-out": "generated repository graph and cache output; privately preserved",
}

# Extensions that mean "this is source, losing it silently is a defect".
SOURCE_SUFFIXES = {".py", ".C", ".cpp", ".h", ".hpp", ".sh", ".json", ".md",
                   ".sub", ".mk", ".cfg", ".toml", ".yaml", ".yml"}

failures = []
checks = 0


def check(label, condition, detail=""):
    global checks
    checks += 1
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label}")
        if detail:
            for line in detail.splitlines():
                print(f"       {line}")
        failures.append(label)


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True)


def is_ignored(path):
    """git check-ignore exits 0 when the path IS ignored."""
    return git("check-ignore", "-q", "--", str(path)).returncode == 0


def ignore_rule_for(path):
    out = git("check-ignore", "-v", "--", str(path)).stdout.strip()
    return out.split("\t")[0] if out else "<none>"


def under_deliberate(rel):
    """Is `rel` one of the deliberate exceptions, or inside one?"""
    parts = Path(rel).parts
    for allowed in DELIBERATELY_IGNORED:
        a = Path(allowed).parts
        if parts[:len(a)] == a:
            return allowed
    return None


# ---------------------------------------------------------------------------
print("A. directories holding TRACKED files must not be ignored")
# ---------------------------------------------------------------------------
tracked = git("ls-files", "-z").stdout.split("\0")
tracked_dirs = set()
for f in tracked:
    if not f:
        continue
    parent = Path(f).parent
    while str(parent) != ".":
        tracked_dirs.add(parent.as_posix())
        parent = parent.parent

offenders = []
for d in sorted(tracked_dirs):
    if is_ignored(d):
        offenders.append(f"{d}  <- {ignore_rule_for(d)}")
check("no tracked-file directory is ignored",
      not offenders,
      "A directory holding tracked files is matched by an ignore rule. Files\n"
      "already committed keep working, so nothing looks wrong -- but every NEW\n"
      "file added there is silently dropped by `git add`.\n" + "\n".join(offenders))

# ---------------------------------------------------------------------------
print("B. no ignore rule may match a real directory only under case-folding")
# ---------------------------------------------------------------------------
gitignore = REPO / ".gitignore"
patterns = []
for lineno, raw in enumerate(gitignore.read_text().splitlines(), 1):
    line = raw.strip()
    if not line or line.startswith("#") or line.startswith("!"):
        continue
    # Only rules that name a path, not a glob over basenames like *.pcm.
    if re.search(r"[*?\[]", line):
        continue
    patterns.append((lineno, line, line.strip("/")))

real_dirs = {}
for dirpath, dirnames, _ in os.walk(REPO):
    dirnames[:] = [d for d in dirnames if d != ".git"]
    for d in dirnames:
        rel = Path(dirpath, d).relative_to(REPO).as_posix()
        real_dirs.setdefault(rel.lower(), []).append(rel)

collisions = []
for lineno, raw, norm in patterns:
    exact_exists = norm in {r for rs in real_dirs.values() for r in rs}
    if exact_exists:
        continue  # rule names a directory that really is spelled that way
    for real in real_dirs.get(norm.lower(), []):
        collisions.append(
            f".gitignore:{lineno}  rule {raw!r} vs real directory {real!r}\n"
            f"  differ only in case -- on a case-insensitive filesystem this "
            f"rule IGNORES {real!r}")
check("no case-only collision between an ignore rule and a real directory",
      not collisions,
      "\n".join(collisions))

# ---------------------------------------------------------------------------
print("C. an ignored directory must not hold source unless declared")
# ---------------------------------------------------------------------------
swallowed = []
for dirpath, dirnames, filenames in os.walk(REPO):
    dirnames[:] = [d for d in dirnames if d != ".git"]
    rel_dir = Path(dirpath).relative_to(REPO)
    if str(rel_dir) == ".":
        continue
    rel = rel_dir.as_posix()
    if under_deliberate(rel):
        dirnames[:] = []
        continue
    if not is_ignored(rel):
        continue
    # This directory is ignored and is not a declared exception.
    src = [f for f in filenames if Path(f).suffix in SOURCE_SUFFIXES]
    if src:
        swallowed.append(
            f"{rel}  <- {ignore_rule_for(rel)}\n"
            f"  holds {len(src)} source file(s): {', '.join(sorted(src)[:5])}")
    dirnames[:] = []
check("no undeclared ignored directory contains source files",
      not swallowed,
      "An ignored directory holds source-like files and is not listed in\n"
      "DELIBERATELY_IGNORED. Either it should be tracked (fix the rule) or it\n"
      "is a deliberate exception (add it here, with a reason).\n"
      + "\n".join(swallowed))

# ---------------------------------------------------------------------------
print("D. the specific regression: analysis/ is tracked and not ignored")
# ---------------------------------------------------------------------------
check("analysis/ is not ignored", not is_ignored("analysis"),
      f"matched by {ignore_rule_for('analysis')}")
for f in ("analysis/a2_block_shift.py", "analysis/a2_pair_yield.C"):
    check(f"{f} is tracked",
          git("ls-files", "--error-unmatch", "--", f).returncode == 0,
          "the file the /Analysis/ rule hid; it gates the A2 measurement")

print(f"\n{checks} checks, {len(failures)} failure(s)")
sys.exit(1 if failures else 0)
