#!/usr/bin/env python3
"""Every refusal in setupEnv.sh must stop the job that sourced it.

Origin. `setupEnv.sh` is sourced, so it cannot force its caller to stop; it can
only return a status, and a caller with `set -e` acts on that status only while
errexit is on. The file turns the caller's errexit and nounset off on entry, so
a refusal that returns without putting them back leaves the caller running AND
leaves it running with both flags cleared for the rest of the job. That is worse
than no refusal at all.

It is not hypothetical. On the first HF_SMOKE3 pilot the PYTHIA refusal printed
its error on line 1 of the job's `.err` and
`generation/submit/runCondorJob.sh` reported a promotion error 109 lines
further in: the worker ran the producer after the environment had refused to
set up. `generation/submit/runCondorJob.sh` opens with `set -euo pipefail` and
sources this file bare, which is the correct caller shape; the defect was
entirely on this side.

Two things are checked for every refusal site in the file:

  1. the file -- the refusal calls `setupenv_restore_shell_flags` before it
     returns, with no exception, and every site is accounted for by exactly one
     row of SITES below, so a refusal added later cannot pass unnoticed;
  2. the run -- for every site that can be reached on a development host, a
     caller running `set -euo pipefail` stops with a non-zero status and never
     reaches the statement after the `source`.

Each driven site is also shown to be load-bearing on its own. The same case is
run against a copy of setupEnv.sh with that one call deleted -- the pre-fix
shape, reproduced one site at a time -- and the caller must then run on. A guard
that no case can kill is a guard nothing depends on.

Nothing is written into the working tree. Every case builds a sandbox checkout
holding only the files the sourced code reads.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETUP_ENV = ROOT / "setupEnv.sh"

# The line that hands a refusal back to the caller, and the call that has to
# stand above it.
REFUSAL = "return 1 2>/dev/null || exit 1"
RESTORE = "setupenv_restore_shell_flags"

# The CVMFS entry test. Nine refusals sit below it, /cvmfs cannot be created on
# a development host, and the root filesystem is read-only on this one, so the
# only way to reach those nine is to redirect the entry path into the sandbox.
# The redirect is asserted to change these two lines and nothing else.
CVMFS_LOGIN = "/cvmfs/alice.cern.ch/etc/login.sh"

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


# --------------------------------------------------------------------------
# The sandbox checkout
# --------------------------------------------------------------------------

def redirect_cvmfs(text, login):
    """Point the CVMFS entry test and its source at a file the sandbox owns."""
    out, changed = [], 0
    for line in text.splitlines(keepends=True):
        if CVMFS_LOGIN in line:
            line = line.replace(CVMFS_LOGIN, str(login))
            changed += 1
        out.append(line)
    return "".join(out), changed


def drop_restore(text, anchor):
    """Delete the one `setupenv_restore_shell_flags` that guards `anchor`.

    This reproduces the pre-fix shape for a single site. Everything else in the
    file is left byte-identical, so a caller that runs on can only have run on
    because of this site.
    """
    lines = text.splitlines(keepends=True)
    start = next(i for i, line in enumerate(lines) if anchor in line)
    site = next(i for i in range(start, len(lines)) if REFUSAL in lines[i])
    guard = site - 1
    while guard >= 0 and not lines[guard].strip():
        guard -= 1
    if lines[guard].strip() != RESTORE:
        return None
    return "".join(lines[:guard] + lines[guard + 1:])


def build_checkout(tmp, *, cvmfs=False, omit=(), text=None):
    """Copy the files the site and dependency blocks read into a sandbox."""
    base = Path(tmp) / "checkout"
    (base / "config/sites").mkdir(parents=True)
    (base / "bin").mkdir()
    body = SETUP_ENV.read_text() if text is None else text
    if cvmfs:
        login = base / "cvmfs/alice.cern.ch/etc/login.sh"
        login.parent.mkdir(parents=True)
        login.write_text("# the sandbox stands in for CVMFS; it loads nothing\n")
        body, changed = redirect_cvmfs(body, login)
        if changed != 2:
            raise AssertionError(
                f"the CVMFS redirect changed {changed} lines, expected 2 "
                f"(the entry test and the source)")
        stub(base, "alienv", "exit 0")
    (base / "setupEnv.sh").write_text(body)
    for name in ("config/sites/site_guard.sh", "config/sites/local.conf",
                 "config/sites/nikhef.conf", "config/dependencies.conf"):
        if name in omit:
            continue
        shutil.copy(ROOT / name, base / name)
    return base


def stub(base, name, body):
    """Put an executable of our own on the sandbox PATH."""
    path = base / "bin" / name
    path.write_text(f"#!/bin/sh\n{body}\n")
    path.chmod(0o755)
    return path


def prefix(base, name, *files):
    """Build a dependency prefix holding exactly the files named."""
    root = base / name
    for relative in files:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")
        if "/bin/" in f"/{relative}":
            path.chmod(0o755)
    root.mkdir(parents=True, exist_ok=True)
    return root


def source_it(base, environment):
    """Source the sandbox checkout from a caller that runs `set -euo pipefail`.

    The environment is built from nothing rather than inherited, so a value on
    the developer's shell cannot decide the result. PATH carries the sandbox
    stubs first; /opt/homebrew is deliberately absent, so `root` and
    `root-config` are the ones this test put there or are absent entirely.
    """
    env = {
        "PATH": f"{base}/bin:/usr/bin:/bin",
        "HOME": str(base),
        "SETUPENV_QUIET": "1",
    }
    env.update(environment)
    script = (f"set -euo pipefail\n"
              f'source "{base}/setupEnv.sh"\n'
              f"echo JOB-LOGIC-RAN\n")
    return subprocess.run(["bash", "-c", script],
                          capture_output=True, text=True, env=env)


# --------------------------------------------------------------------------
# One case per reachable refusal site
#
# Each builder receives the sandbox base and returns the environment to source
# it with. Builders that need a CVMFS-gated site are marked cvmfs=True in SITES,
# which is what puts the entry file in the sandbox.
# --------------------------------------------------------------------------

def case_unknown_site(base):
    return {"HADRONIZATION_SITE": "nosuchsite"}


def case_profile_refuses(base):
    # config/sites/local.conf checks an exported root by its own rules and
    # returns non-zero; this site is setupEnv.sh reading that status.
    return {"HADRONIZATION_DATA_ROOT": "/data/alice//hf"}


def case_data_root(base):
    # config/site.local.conf replaces the tracked profile, so no tracked
    # refusal runs and setupEnv.sh has to catch the value itself.
    (base / "config/site.local.conf").write_text(
        "HADRONIZATION_DATA_ROOT=/data/alice//hf\n")
    return {}


def case_sibling_root(base):
    return {"HADRONIZATION_MERGED_ROOT": "/data/alice//hadronization_merged"}


def case_deps_override(base):
    return {"HADRONIZATION_DEPENDENCIES_CONF": str(base / "absent.conf")}


def case_root_package(base):
    # No `root` on PATH, so setupEnv.sh takes the raw-CVMFS route and asserts
    # the pinned package first.
    return {"HF_ROOT_PREFIX": str(base / "absent-root")}


def case_pythia_package(base):
    # A `root` on PATH skips the ROOT block, which is what puts the PYTHIA
    # assertions in reach.
    stub(base, "root", "exit 0")
    return {"HF_PYTHIA8_PREFIX": str(base / "absent-pythia")}


def case_pythia_gcc(base):
    stub(base, "root", "exit 0")
    pythia = prefix(base, "pythia", "bin/pythia8-config")
    return {"HF_PYTHIA8_PREFIX": str(pythia),
            "HF_PYTHIA8_GCC_PREFIX": str(base / "absent-gcc")}


def case_pythia_data(base):
    stub(base, "root", "exit 0")
    pythia = prefix(base, "pythia", "bin/pythia8-config")
    gcc = prefix(base, "gcc", "bin/g++")
    return {"HF_PYTHIA8_PREFIX": str(pythia), "HF_PYTHIA8_GCC_PREFIX": str(gcc)}


def case_pythia_lib(base):
    stub(base, "root", "exit 0")
    pythia = prefix(base, "pythia", "bin/pythia8-config",
                    "share/Pythia8/xmldoc/Index.xml")
    gcc = prefix(base, "gcc", "bin/g++")
    return {"HF_PYTHIA8_PREFIX": str(pythia), "HF_PYTHIA8_GCC_PREFIX": str(gcc)}


def _pythia_complete(base, version):
    """A PYTHIA prefix that passes every availability assertion."""
    stub(base, "root", "exit 0")
    pythia = prefix(base, "pythia", "share/Pythia8/xmldoc/Index.xml",
                    "lib/libpythia8.so")
    config = pythia / "bin/pythia8-config"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(f"#!/bin/sh\necho {version}\n")
    config.chmod(0o755)
    gcc = prefix(base, "gcc", "bin/g++")
    return {"HF_PYTHIA8_PREFIX": str(pythia), "HF_PYTHIA8_GCC_PREFIX": str(gcc)}


def case_pythia_version(base):
    # The prefix is complete and the interpreter reports a version nobody
    # configured. A rebuild in place changes the generator while every recorded
    # path stays identical, which is the failure this assertion exists for.
    return _pythia_complete(base, "0.000")


def case_root_version(base):
    environment = _pythia_complete(base, "8.317")
    stub(base, "root-config", "echo 0.00.00")
    return environment


def case_production_root(base):
    # config/dependencies.local.conf is sourced after the sibling-root loop, so
    # a root set there reaches the last assertion in the file and no earlier
    # one. HF_PRODUCTION_ROOT decides where the raw campaign output lands.
    (base / "config/dependencies.local.conf").write_text(
        "HF_PRODUCTION_ROOT=/data/alice//hadronization_production\n")
    return {}


# anchor: a line that appears once in setupEnv.sh; the site is the first
# refusal at or after it. name: what the site refuses. expect: text the refusal
# must print. case: builds the sandbox that reaches it, or None when no case on
# a development host can, with the reason recorded in `unreachable`.
SITES = [
    {"anchor": "ERROR: the shared site guard is missing",
     "name": "the shared site guard is missing",
     "expect": "the shared site guard is missing",
     "omit": ("config/sites/site_guard.sh",), "case": lambda base: {}},
    {"anchor": "ERROR: unknown HADRONIZATION_SITE=",
     "name": "the site has no profile",
     "expect": "unknown HADRONIZATION_SITE=nosuchsite",
     "case": case_unknown_site},
    {"anchor": "refused; no dependency, dataset or output path is set up.",
     "name": "the site profile refused",
     "expect": "refused; no dependency, dataset or output path is set up",
     "case": case_profile_refuses},
    {"anchor": 'if ! hf_site_check_root "${setupenv_site_source}" HADRONIZATION_DATA_ROOT',
     "name": "the surviving data root is malformed",
     "expect": "cannot resolve the data plane from config/site.local.conf",
     "case": case_data_root},
    {"anchor": 'if ! hf_site_check_root "${setupenv_site_source}" "${setupenv_root_name}"',
     "name": "a sibling root is malformed",
     "expect": "HADRONIZATION_MERGED_ROOT carries an empty path segment",
     "case": case_sibling_root},
    {"anchor": "ERROR: HADRONIZATION_DEPENDENCIES_CONF does not exist",
     "name": "the dependency override does not exist",
     "expect": "HADRONIZATION_DEPENDENCIES_CONF does not exist",
     "case": case_deps_override},
    {"anchor": "ERROR: dependency configuration is missing",
     "name": "the dependency configuration is missing",
     "expect": "dependency configuration is missing",
     "omit": ("config/dependencies.conf",), "case": lambda base: {}},
    {"anchor": "ERROR: pinned ROOT package is unavailable",
     "name": "the pinned ROOT package is unavailable",
     "expect": "pinned ROOT package is unavailable",
     "cvmfs": True, "case": case_root_package},
    {"anchor": "ERROR: pinned PYTHIA package is unavailable",
     "name": "the pinned PYTHIA package is unavailable",
     "expect": "pinned PYTHIA package is unavailable",
     "cvmfs": True, "case": case_pythia_package},
    {"anchor": "ERROR: pinned PYTHIA compiler runtime is unavailable",
     "name": "the PYTHIA compiler runtime is unavailable",
     "expect": "pinned PYTHIA compiler runtime is unavailable",
     "cvmfs": True, "case": case_pythia_gcc},
    {"anchor": "ERROR: pinned PYTHIA data are unavailable",
     "name": "the PYTHIA runtime data are unavailable",
     "expect": "pinned PYTHIA data are unavailable",
     "cvmfs": True, "case": case_pythia_data},
    {"anchor": "ERROR: pinned PYTHIA shared library is unavailable",
     "name": "the PYTHIA shared library is unavailable",
     "expect": "pinned PYTHIA shared library is unavailable",
     "cvmfs": True, "case": case_pythia_lib},
    {"anchor": "ERROR: PYTHIA8DATA is unset and no runtime XML data exist",
     "name": "PYTHIA8DATA is unset and carries no data",
     "case": None,
     "unreachable":
         "the line above it exports PYTHIA8DATA unconditionally, so the "
         "`-z PYTHIA8DATA` test that guards this branch is never true"},
    {"anchor": "ERROR: PYTHIA8DATA does not contain Index.xml",
     "name": "PYTHIA8DATA holds no Index.xml",
     "case": None,
     "unreachable":
         "PYTHIA8DATA is exported from the prefix whose Index.xml an earlier "
         "assertion already required, so this test reads the same file twice"},
    {"anchor": "ERROR: PYTHIA version mismatch under",
     "name": "PYTHIA reports an unconfigured version",
     "expect": "PYTHIA version mismatch",
     "cvmfs": True, "case": case_pythia_version},
    {"anchor": 'ERROR: ROOT version mismatch"',
     "name": "ROOT reports an unconfigured version",
     "expect": "ROOT version mismatch",
     "cvmfs": True, "case": case_root_version},
    {"anchor": "if ! hf_site_check_root \\",
     "name": "the production root is malformed after its last default",
     "expect": "HF_PRODUCTION_ROOT carries an empty path segment",
     "case": case_production_root},
]


# --------------------------------------------------------------------------
# 1. the file
# --------------------------------------------------------------------------

def check_census(text):
    lines = text.splitlines()
    sites = [i for i, line in enumerate(lines) if REFUSAL in line]
    print(f"  {len(sites)} refusal site(s) in setupEnv.sh")

    unguarded = []
    for site in sites:
        guard = site - 1
        while guard >= 0 and not lines[guard].strip():
            guard -= 1
        if guard < 0 or lines[guard].strip() != RESTORE:
            unguarded.append(site + 1)
    check("every refusal restores the caller's shell flags before it returns",
          not unguarded,
          f"lines {unguarded} return without {RESTORE}; a caller with `set -e` "
          f"runs on, with errexit and nounset cleared")

    # A refusal added later must be classified here before it can pass. Without
    # this the census above would still be green while a new site sat untested.
    mapped, ambiguous = {}, []
    for row in SITES:
        hits = [i for i, line in enumerate(lines) if row["anchor"] in line]
        if len(hits) != 1:
            ambiguous.append((row["name"], len(hits)))
            continue
        site = next((i for i in sites if i >= hits[0]), None)
        mapped.setdefault(site, []).append(row["name"])
    check("every row of SITES names one line of setupEnv.sh", not ambiguous,
          f"{ambiguous} -- each anchor must match exactly one line")
    check("no two rows claim the same refusal site",
          all(len(names) == 1 for names in mapped.values()),
          str({site: names for site, names in mapped.items()
               if len(names) > 1}))
    missing = [i + 1 for i in sites if i not in mapped]
    check("every refusal site is claimed by a row of SITES", not missing,
          f"lines {missing} are refusals no case covers; add a row saying how "
          f"it is reached, or why it cannot be")
    return sites


# --------------------------------------------------------------------------
# 2. the run, and the same run against the pre-fix shape
# --------------------------------------------------------------------------

def run_case(row, text=None):
    with tempfile.TemporaryDirectory() as tmp:
        base = build_checkout(tmp, cvmfs=row.get("cvmfs", False),
                              omit=row.get("omit", ()), text=text)
        environment = row["case"](base)
        return source_it(base, environment)


def check_site(row):
    name = row["name"]
    got = run_case(row)
    stopped = got.returncode != 0 and "JOB-LOGIC-RAN" not in got.stdout
    check(f"{name}: the refusal stops the sourcing shell", stopped,
          f"rc={got.returncode} out={got.stdout[:120]!r} "
          f"err={got.stderr[-300:]!r}")
    check(f"{name}: ...and it is this refusal that fired",
          row["expect"] in got.stderr, got.stderr[-300:])

    # Seen to fail: the same case against the file with this one call deleted.
    mutant = drop_restore(SETUP_ENV.read_text(), row["anchor"])
    if mutant is None:
        check(f"{name}: ...and the guard above it can be deleted", False,
              "no setupenv_restore_shell_flags stands above this refusal")
        return
    got = run_case(row, text=mutant)
    check(f"{name}: ...and without that one call the caller runs on",
          got.returncode == 0 and "JOB-LOGIC-RAN" in got.stdout,
          f"rc={got.returncode} out={got.stdout[:120]!r} -- the guard is not "
          f"what stops the caller here, so this case proves nothing")


def check_normal_exit():
    """A run that refuses nothing must hand the caller its flags back too."""
    with tempfile.TemporaryDirectory() as tmp:
        base = build_checkout(tmp)
        env = {
            "PATH": f"{base}/bin:/usr/bin:/bin",
            "HOME": str(base),
            "SETUPENV_QUIET": "1",
        }
        script = (f"set -euo pipefail\n"
                  f'source "{base}/setupEnv.sh"\n'
                  f'case "$-" in *e*) echo ERREXIT-ON ;; esac\n'
                  f'case "$-" in *u*) echo NOUNSET-ON ;; esac\n')
        got = subprocess.run(["bash", "-c", script], capture_output=True,
                             text=True, env=env)
        check("a run that refuses nothing leaves errexit on",
              got.returncode == 0 and "ERREXIT-ON" in got.stdout,
              f"rc={got.returncode} out={got.stdout[:200]!r} "
              f"err={got.stderr[-200:]!r}")
        check("...and leaves nounset on", "NOUNSET-ON" in got.stdout,
              got.stdout[:200])


def main(argv):
    if len(argv) != 1:
        print(f"usage: {argv[0]}")
        return 2
    if os.name != "posix":
        print("  SKIP: this test sources a shell script")
        return 0

    print(f"refusal propagation in {SETUP_ENV}")
    check_census(SETUP_ENV.read_text())

    driven = [row for row in SITES if row["case"] is not None]
    for row in driven:
        check_site(row)
    check_normal_exit()

    for row in SITES:
        if row["case"] is None:
            print(f"  NOTE {row['name']}: no case reaches it -- "
                  f"{row['unreachable']}")

    print(f"\n{len(driven)} of {len(SITES)} refusal sites driven end to end")
    print(f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
