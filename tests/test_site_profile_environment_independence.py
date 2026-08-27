#!/usr/bin/env python3
"""A site profile must resolve the data plane without reading the environment.

Origin. `config/sites/nikhef.conf` built every data root from
`/data/alice/${USER}/hf`. `tools/render_production_submit.py` emits
`getenv = False` and no `environment =` line, so an HTCondor job starts with an
empty environment: `${USER}` expanded to nothing on the execute node,
`/data/alice//hf` collapsed to the shared `/data/alice/hf`, and the first
HF_SMOKE3 pilot resolved that path, failed to find PYTHIA below it, and wrote
outside the account. Nothing refused, because the path was valid.

Checks:
  1. each tracked profile resolves under `env -i bash`, with no USER, to an
     absolute root whose segments are all non-empty;
  2. the Nikhef profile puts the account in the root as its own path segment,
     and the name equals `id -un`;
  2b. the Nikhef profile refuses an account whose data directory does not
     exist -- the pool-account guard: `id -un` answers which account the
     process runs as, so a pool or glidein account resolves a well-formed root
     that no shape rule can reject;
  3. an empty account name makes the Nikhef profile refuse, loudly, naming the
     file to edit;
  4. an empty HADRONIZATION_BASE makes the local profile refuse the same way;
  5. a malformed HADRONIZATION_DATA_ROOT is refused whoever supplied it;
  6. no tracked file under config/sites reads USER or LOGNAME, including the
     shared guard, which is where the account derivation now lives;
  7. setupEnv.sh refuses on its own account: it stops a caller that runs with
     `set -e`, it catches a root supplied by an untracked config/site.local.conf
     that no tracked profile ever saw, it catches a malformed sibling root, and
     it names the file that supplied the value;
  8. the environment verdict blocks on a malformed data root, reports the site
     and the account it resolved without the environment, and does not let
     HF_ALLOW_UNPINNED_ENV suppress it;
  9. the account guard in the shared file accepts an account that has a data
     directory and refuses one that does not, both branches driven against a
     sandbox parent.

Every check must mean the same thing on every host. Two did not: check 7a
named `config/sites/local.conf`, which hf_site_detect answers only off the
cluster, and check 7c's well-formed case required the whole of setupEnv.sh to
succeed, which reads the dependency plane the sandbox deliberately replaces.
Both are derived from the guard now. A check whose subject is the site plane
asserts on the site plane, and says which plane refused when one does.

Run against another directory of profiles to check a copy:
    python3 tests/test_site_profile_environment_independence.py --sites-dir DIR
Checks 1 to 6 then read DIR. Checks 7 and 8 read setupEnv.sh and the verdict in
this checkout and are skipped, which the run says. That is how this test was
seen to fail against the pre-fix profile.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERDICT = ROOT / "tools/environment_verdict.sh"
SETUP_ENV = ROOT / "setupEnv.sh"
GUARD = ROOT / "config/sites/site_guard.sh"

# Read the root and the account the profile resolved, and nothing else.
REPORT = (
    'source "$1" || exit 3\n'
    'printf "%s\\n%s\\n" "${HADRONIZATION_DATA_ROOT:-}" '
    '"${HADRONIZATION_SITE_ACCOUNT:-}"\n'
)

# The same, but reporting what the profile derived even when it refuses.
# config/sites/nikhef.conf assigns HADRONIZATION_DATA_ROOT before it asserts
# that the account's data directory exists, so the derived root is readable on a
# host that carries no /data/alice -- which is every host except the cluster.
# Without this probe the environment-independence property of the Nikhef profile
# could only be checked on Nikhef, and that is the one host where an
# environment-dependent path would still have resolved.
DERIVE = (
    'source "$1"\n'
    'hf_probe_status=$?\n'
    'printf "%s\\n%s\\n%s\\n" "${hf_probe_status}" '
    '"${HADRONIZATION_DATA_ROOT:-}" "${HADRONIZATION_SITE_ACCOUNT:-}"\n'
)

# The refusal the pool-account guard prints, and the directory it names.
ACCOUNT_DIR_REFUSAL = re.compile(
    r"the data directory of account '([^']*)' does not exist: ([^;]+);")

# Every shape config/sites/site_guard.sh refuses, and why it still names a real
# directory. A shape that resolves to nothing would not need a rule.
MALFORMED = {
    "an empty path segment": "/data/alice//hf",
    "a relative path": "data/alice/x/hf",
    "a trailing separator": "/data/alice/x/hf/",
    "a .. segment": "/data/alice/x/hf/..",
    "a . segment": "/data/alice/./x/hf",
}

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def source_profile(profile, keep=None, path=None, script=REPORT):
    """Source one profile with an empty environment and report what it did."""
    command = ["env", "-i"]
    if path is not None:
        command.append(f"PATH={path}")
    for name, value in (keep or {}).items():
        command.append(f"{name}={value}")
    command += ["bash", "-c", script, "_", str(profile)]
    return subprocess.run(command, capture_output=True, text=True)


def source_setup_env(base, environment=None, report=None):
    """Source a checkout's setupEnv.sh from a caller that runs with set -e.

    With `report`, the caller drops errexit and runs `report` afterwards, so a
    check can read what the site plane resolved even on a host whose dependency
    plane refuses for its own reasons. Only a probe may do that. A job must
    stop, which is what the default form measures.
    """
    inherited = dict(os.environ)
    inherited["SETUPENV_QUIET"] = "1"
    inherited.update(environment or {})
    if report is None:
        script = (f'set -euo pipefail\nsource "{base}/setupEnv.sh"\n'
                  f'echo JOB-LOGIC-RAN\n')
    else:
        script = f'source "{base}/setupEnv.sh"\n{report}'
    return subprocess.run(["bash", "-c", script],
                          capture_output=True, text=True, env=inherited)


def site_profile_source(base=ROOT):
    """Name the file setupEnv.sh reads for its site plane on THIS host.

    setupEnv.sh reads config/site.local.conf when that file exists and
    config/sites/<site>.conf otherwise, and hf_site_detect answers `nikhef`
    only where /data/alice and /cvmfs/alice.cern.ch both exist. Ask the guard
    for both answers rather than naming a profile: this check hardcoded
    `config/sites/local.conf`, which is correct on every development host and
    wrong on the cluster -- the one host the Nikhef profile exists for. Return
    an empty string when the guard cannot answer, so the caller fails loudly.
    """
    script = ('source "$1/config/sites/site_guard.sh"\n'
              'hf_site_profile_path "$1" "$(hf_site_detect)"\n')
    got = subprocess.run(["bash", "-c", script, "_", str(base)],
                         capture_output=True, text=True)
    resolved = got.stdout.strip()
    if got.returncode != 0 or not resolved:
        return ""
    return os.path.relpath(resolved, str(base))


def malformed(value):
    """Say why a resolved root is unusable, or return an empty string."""
    if not value:
        return "empty"
    if not value.startswith("/"):
        return "relative"
    segments = value.split("/")[1:]
    if not all(segments):
        return "empty path segment"
    if any(segment in (".", "..") for segment in segments):
        return "a . or .. segment"
    if "\n" in value:
        return "a newline"
    return ""


def refuses(result, source):
    """A refusal is a non-zero status AND a named error naming the file to edit.

    The message must carry the refusal wording, not merely the file name: the
    profiles also bail out when the shared guard is missing, and that is a
    different failure with no rule behind it.
    """
    return (result.returncode != 0
            and f"cannot resolve the data plane from {source}" in result.stderr)


def check_profiles(sites_dir):
    account = subprocess.run(["id", "-un"], capture_output=True,
                             text=True).stdout.strip()
    nikhef = sites_dir / "nikhef.conf"
    nikhef_name = f"config/sites/{nikhef.name}"
    local = sites_dir / "local.conf"
    local_name = f"config/sites/{local.name}"

    # --- 1, 2. the profiles resolve with no environment at all ---------------
    check("the Nikhef profile exists", nikhef.is_file(), str(nikhef))
    if nikhef.is_file():
        # Nothing is passed. No USER, no LOGNAME, no HOME, not even PATH: the
        # account must come from the process credential.
        #
        # Two outcomes are correct here, and which one appears depends on the
        # host rather than on the profile. On Nikhef the account has a data
        # directory and the profile resolves. Everywhere else /data/alice does
        # not exist, so the pool-account guard refuses -- and the derived root
        # is still readable, because the profile assigns it before it asserts
        # the directory. The derivation is what this check is about, so it runs
        # either way; a third outcome, any other refusal, is a defect.
        got = source_profile(nikhef, script=DERIVE)
        status, root, resolved_account = (got.stdout.split("\n") + ["", "", ""])[:3]
        refusal = ACCOUNT_DIR_REFUSAL.search(got.stderr)
        check("the Nikhef profile derives a root under `env -i`, with no USER",
              status in ("0", "1") and bool(root),
              f"status={status!r} root={root!r} {got.stderr[:300]}")
        check("...whose segments are all usable",
              malformed(root) == "", f"{root!r} has {malformed(root)}")
        # A path component, not a substring: /data/alice/hf -- the shared
        # directory the pilot wrote into -- contains "/alice/" already.
        check("...and carries the account as its own path segment",
              bool(account) and account in root.split("/")[1:],
              f"{root!r} has no segment {account!r}")
        if status == "0":
            check("...and reports the account it used",
                  resolved_account == account,
                  f"{resolved_account!r} != {account!r} from `id -un`")
        else:
            check("...and, off the storage plane, refuses for the account "
                  "directory and nothing else",
                  refusal is not None, got.stderr[:400])
            if refusal is not None:
                named_account, named_dir = refusal.group(1), refusal.group(2)
                check("...naming the account `id -un` gave",
                      named_account == account,
                      f"{named_account!r} != {account!r} from `id -un`")
                check("...and the directory the derived root sits below",
                      root.startswith(f"{named_dir}/")
                      and named_dir.split("/")[-1] == account,
                      f"{named_dir!r} is not the account parent of {root!r}")

    check("the local profile exists", local.is_file(), str(local))
    if local.is_file():
        # HADRONIZATION_BASE is passed because setupEnv.sh derives it from the
        # location of setupEnv.sh, not from the environment. USER is not.
        got = source_profile(local, keep={"HADRONIZATION_BASE": str(ROOT)})
        check("the local profile resolves under `env -i`, with no USER",
              got.returncode == 0, f"rc={got.returncode} {got.stderr[:300]}")
        if got.returncode == 0:
            root = got.stdout.split("\n")[0]
            check("...to a root whose segments are all usable",
                  malformed(root) == "", f"{root!r} has {malformed(root)}")

    # --- 3. an empty account name is refused, not substituted ---------------
    if nikhef.is_file():
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "id-ran"
            stub = Path(tmp) / "id"
            stub.write_text(f"#!/bin/sh\n: > '{marker}'\nexit 0\n")
            stub.chmod(0o755)
            got = source_profile(nikhef, path=f"{tmp}:/usr/bin:/bin")
            # Without this, the next check reads as a defect in the profile
            # when the cause is elsewhere: either the profile never calls `id`,
            # or the temporary directory is mounted noexec and the real `id`
            # answered.
            check("the stubbed `id` is the one that ran", marker.exists(),
                  f"the profile did not call `id`, or {tmp} is noexec")
            check("an empty account name makes the Nikhef profile refuse",
                  refuses(got, nikhef_name),
                  f"rc={got.returncode} out={got.stdout!r} err={got.stderr[:300]}")
            check("...and the refusal says the account name is empty",
                  "account name is empty" in got.stderr, got.stderr[:300])
            check("...and resolves no data root at all",
                  got.stdout.strip() == "", got.stdout[:200])

    # --- 4. an empty base is refused the same way ---------------------------
    if local.is_file():
        got = source_profile(local)
        check("an empty HADRONIZATION_BASE makes the local profile refuse",
              refuses(got, local_name),
              f"rc={got.returncode} out={got.stdout!r} err={got.stderr[:300]}")

    # --- 5. a malformed root is refused whoever supplied it -----------------
    for profile, source in ((nikhef, nikhef_name), (local, local_name)):
        if not profile.is_file():
            continue
        for label, value in MALFORMED.items():
            got = source_profile(profile, keep={
                "HADRONIZATION_DATA_ROOT": value,
                "HADRONIZATION_BASE": str(ROOT),
            })
            check(f"{source} refuses {label} in an exported "
                  f"HADRONIZATION_DATA_ROOT",
                  refuses(got, source),
                  f"rc={got.returncode} err={got.stderr[:300]}")

    # --- 6. nothing under config/sites reads the environment for an account --
    # The account derivation lives in the shared guard now, so a *.conf glob
    # would miss the one file that performs it. Comments describe the failure,
    # so read the code lines only.
    scanned = sorted(list(sites_dir.glob("*.conf")) + list(sites_dir.glob("*.sh")))
    check("config/sites holds the guard as well as the profiles",
          any(path.suffix == ".sh" for path in scanned),
          f"{[p.name for p in scanned]} -- nothing scanned derives the account")
    for path in scanned:
        code = [line for line in path.read_text().splitlines()
                if line.strip() and not line.lstrip().startswith("#")]
        reads = [line for line in code if "USER" in line or "LOGNAME" in line]
        check(f"{path.name} reads no USER or LOGNAME", not reads,
              f"{reads} -- an account segment taken from the environment is "
              f"empty in a Condor job")

    # --- 9. the account guard, both branches, against a sandbox parent -------
    # /data/alice cannot be created on a development host, so the guard is
    # driven as a function with a parent this test owns. That is what makes the
    # pool-account case reproducible off the cluster: the guard has to refuse an
    # account name that is perfectly well formed by every shape rule and simply
    # has no directory, which is exactly what a pool, glidein or uid-mapped
    # account looks like.
    guard = sites_dir / "site_guard.sh"
    has_rule = guard.is_file() and "hf_site_require_account_dir" in guard.read_text()
    check("the shared guard carries the account-directory rule", has_rule,
          f"{guard} defines no hf_site_require_account_dir")
    if has_rule:
        drive = ('source "$1"\n'
                 'hf_site_require_account_dir "config/sites/nikhef.conf" "$2" "$3"\n')
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "has-storage").mkdir()
            got = subprocess.run(
                ["bash", "-c", drive, "_", str(guard), tmp, "has-storage"],
                capture_output=True, text=True)
            check("the account guard accepts an account that has a data "
                  "directory", got.returncode == 0,
                  f"rc={got.returncode} err={got.stderr[:300]}")
            got = subprocess.run(
                ["bash", "-c", drive, "_", str(guard), tmp, "pool-account"],
                capture_output=True, text=True)
            check("...and refuses a well-formed account that has none",
                  refuses(got, "config/sites/nikhef.conf"),
                  f"rc={got.returncode} err={got.stderr[:300]}")
            check("...naming the directory it required",
                  f"{tmp}/pool-account" in got.stderr, got.stderr[:300])


def check_setup_env():
    # Which file setupEnv.sh reads for its site plane depends on the host, and
    # every refusal below names that file rather than the site. Derive it once,
    # from the guard that setupEnv.sh itself uses, so this test cannot drift
    # from the selection rule it is checking.
    site_source = site_profile_source()
    check("the guard names the site profile setupEnv.sh would read",
          bool(site_source),
          "hf_site_detect or hf_site_profile_path did not answer")

    # --- 7a. a refusal reaches a caller that runs with `set -e` -------------
    # A sourced script cannot force its caller to stop; it can only return a
    # status. setupEnv.sh turns the caller's errexit off, so it must put the
    # flag back before it refuses. Without that, the caller runs on -- which is
    # what let the HF_SMOKE3 pilot run the producer after a refusal.
    got = source_setup_env(ROOT, {"HADRONIZATION_DATA_ROOT": "/data/alice//hf"})
    check("a site-profile refusal stops a caller that runs with `set -e`",
          got.returncode != 0 and "JOB-LOGIC-RAN" not in got.stdout,
          f"rc={got.returncode} out={got.stdout[:200]}")
    check("...and the refusal names the file that supplied the value",
          f"cannot resolve the data plane from {site_source}" in got.stderr,
          f"expected {site_source}: {got.stderr[-300:]}")

    # --- 7b. a malformed sibling root stops the run too ---------------------
    # HF_PRODUCTION_ROOT decides where hundreds of gigabytes of raw campaign
    # output land, and config/site.local.conf.example invites setting it alone.
    got = source_setup_env(
        ROOT, {"HF_PRODUCTION_ROOT": "/data/alice//hadronization_production"})
    check("a malformed HF_PRODUCTION_ROOT stops the run",
          got.returncode != 0 and "JOB-LOGIC-RAN" not in got.stdout,
          f"rc={got.returncode} out={got.stdout[:200]} err={got.stderr[:300]}")
    # A non-zero status alone proves nothing on a host that carries
    # /cvmfs/alice.cern.ch: the dependency plane below refuses there for its own
    # reasons, so this check would pass with the sibling rule deleted. Name the
    # plane that stopped the run and the variable it read.
    check("...and the site plane is what stopped it, naming the variable",
          refuses(got, site_source) and "HF_PRODUCTION_ROOT" in got.stderr,
          f"rc={got.returncode} err={got.stderr[:400]}")

    # --- 7c. setupEnv.sh catches what no tracked profile ever sees ----------
    # config/site.local.conf is sourced INSTEAD of config/sites/<site>.conf, so
    # none of the tracked refusals run. setupEnv.sh has to check the surviving
    # value itself. Build a checkout that carries only the files the site block
    # reads, so nothing is written into this working tree.
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "checkout"
        (base / "config/sites").mkdir(parents=True)
        shutil.copy(SETUP_ENV, base / "setupEnv.sh")
        shutil.copy(GUARD, base / "config/sites/site_guard.sh")
        shutil.copy(ROOT / "config/sites/local.conf",
                    base / "config/sites/local.conf")
        # The sandbox carries the tracked dependency defaults so that it reads
        # as a real checkout. It is not what makes the well-formed case below
        # meaningful; that case asserts on the site plane directly.
        shutil.copy(ROOT / "config/dependencies.conf",
                    base / "config/dependencies.conf")
        override = base / "config/site.local.conf"
        override.write_text('HADRONIZATION_DATA_ROOT=/data/alice//hf\n')
        got = source_setup_env(base)
        check("setupEnv.sh refuses a root that only config/site.local.conf set",
              got.returncode != 0 and "JOB-LOGIC-RAN" not in got.stdout,
              f"rc={got.returncode} out={got.stdout[:200]} err={got.stderr[:400]}")
        check("...and blames config/site.local.conf, not the tracked profile",
              "cannot resolve the data plane from config/site.local.conf"
              in got.stderr, got.stderr[-400:])

        # The same file, well formed, must not be refused.
        #
        # Only the site plane is under test. Requiring the whole of setupEnv.sh
        # to succeed made this case read the host's dependency plane as well:
        # config/site.local.conf replaces the tracked profile entirely, and on
        # Nikhef config/sites/nikhef.conf is also the file that supplies
        # HF_PYTHIA8_PREFIX. On a host that carries /cvmfs/alice.cern.ch the
        # sandbox therefore reached the PYTHIA pin with an empty prefix and
        # refused there, with rc=1 and no site refusal at all. Measure what the
        # site plane did, which is the same answer on every host.
        override.write_text('HADRONIZATION_DATA_ROOT=/data/alice/someone/hf\n')
        got = source_setup_env(base, report=(
            'printf "SITE-PLANE-ROOT=%s\\n" "${HADRONIZATION_DATA_ROOT:-}"\n'))
        check("...and accepts the same file when the root is well formed",
              "cannot resolve the data plane from" not in got.stderr
              and "config/site.local.conf refused" not in got.stderr,
              f"rc={got.returncode} err={got.stderr[:400]}")
        # Without this the check above would also pass on a sandbox that failed
        # before the site plane ran at all, which prints no refusal either.
        check("...keeping the root that file supplied",
              "SITE-PLANE-ROOT=/data/alice/someone/hf" in got.stdout,
              f"out={got.stdout[:200]} err={got.stderr[:300]}")


def check_pin_refusal():
    """--- 7d. the PYTHIA pin refusal names the plane, not one candidate file --

    WHAT THIS MACHINE CANNOT DO. The block that carries this refusal is gated
    on /cvmfs/alice.cern.ch/etc/login.sh (setupEnv.sh:172), which exists on the
    cluster and on no development host, so these assertions read the source
    rather than run it. That boundary is the same one check 7c records: the
    site plane resolves everywhere, the dependency plane does not.

    WHY THE MESSAGE CHANGED. config/sites/nikhef.conf sets HF_PYTHIA8_PREFIX on
    its last line, and an untracked config/site.local.conf replaces the tracked
    profile entirely, including that assignment. The refusal used to answer
    that case with "Set HF_PYTHIA8_PREFIX in config/dependencies.local.conf",
    which is the one file that had nothing to do with it.
    """
    text = SETUP_ENV.read_text()
    start = text.index("pinned PYTHIA package is unavailable")
    refusal = text[start:text.index("pinned PYTHIA compiler runtime")]

    check("the pin refusal names the site plane in effect",
          "${setupenv_site_source" in refusal, refusal[:400])
    check("...and says that plane does not set the variable",
          "does not set that variable" in refusal, refusal[:400])
    check("...naming the tracked profile that does set it",
          "config/sites/nikhef.conf" in refusal, refusal[:400])
    check("...and the untracked file that replaces it",
          "config/site.local.conf" in refusal, refusal[:400])
    check("...and it no longer sends the reader to one file alone",
          "Set HF_PYTHIA8_PREFIX in config/dependencies.local.conf."
          not in refusal, refusal[:400])
    check("...while still naming where the pin may be supplied",
          "config/dependencies.local.conf" in refusal, refusal[:400])
    # Fail-closed is the part that must NOT change.
    check("...and the refusal still stops the run",
          "setupenv_restore_shell_flags" in refusal
          and "return 1 2>/dev/null || exit 1" in refusal, refusal[-200:])


def check_verdict():
    account = subprocess.run(["id", "-un"], capture_output=True,
                             text=True).stdout.strip()
    environment = dict(os.environ)
    environment["HADRONIZATION_DATA_ROOT"] = "/data/alice//hf"
    environment["HF_ALLOW_UNPINNED_ENV"] = "1"
    got = subprocess.run(["bash", str(VERDICT), str(ROOT)],
                         capture_output=True, text=True, env=environment)
    output = got.stdout + got.stderr
    reported = {}
    for line in output.splitlines():
        if ":" in line and line.startswith("  "):
            key, _, value = line.strip().partition(":")
            reported.setdefault(key.strip(), value.strip())

    check("the environment verdict blocks on a malformed data root",
          got.returncode != 0, f"rc={got.returncode}")
    check("...and calls it a site profile defect",
          "SITE PROFILE DEFECT" in output, output[-400:])
    check("...and HF_ALLOW_UNPINNED_ENV does not suppress it",
          "does not apply" in output, output[-400:])
    # Assert the values, not the labels: the labels are printed unconditionally,
    # so a verdict that stopped resolving anything would still carry them.
    check("...and names the site it resolved",
          reported.get("site") in ("local", "nikhef"), str(reported)[:400])
    check("...and reports the account it resolved without the environment",
          bool(account) and reported.get("account, env -i") == account,
          f"{reported.get('account, env -i')!r} != {account!r}")
    check("...and reports the root it resolved without the environment",
          malformed(reported.get("data root, env -i", "")) == "",
          f"{reported.get('data root, env -i')!r}")


def main(argv):
    sites_dir = ROOT / "config/sites"
    repository = True
    if len(argv) == 3 and argv[1] == "--sites-dir":
        sites_dir = Path(argv[2]).resolve()
        repository = False
    elif len(argv) != 1:
        print(f"usage: {argv[0]} [--sites-dir DIR]")
        return 2

    print(f"site profiles under {sites_dir}")
    check_profiles(sites_dir)
    if repository:
        check_setup_env()
        check_pin_refusal()
        check_verdict()
    else:
        print("  SKIP checks 7 and 8: they read setupEnv.sh and the "
              "environment verdict in this checkout, not --sites-dir")

    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
