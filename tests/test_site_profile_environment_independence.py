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
     HF_ALLOW_UNPINNED_ENV suppress it.

Run against another directory of profiles to check a copy:
    python3 tests/test_site_profile_environment_independence.py --sites-dir DIR
Checks 1 to 6 then read DIR. Checks 7 and 8 read setupEnv.sh and the verdict in
this checkout and are skipped, which the run says. That is how this test was
seen to fail against the pre-fix profile.
"""

from __future__ import annotations

import os
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


def source_profile(profile, keep=None, path=None):
    """Source one profile with an empty environment and report what it did."""
    command = ["env", "-i"]
    if path is not None:
        command.append(f"PATH={path}")
    for name, value in (keep or {}).items():
        command.append(f"{name}={value}")
    command += ["bash", "-c", REPORT, "_", str(profile)]
    return subprocess.run(command, capture_output=True, text=True)


def source_setup_env(base, environment=None):
    """Source a checkout's setupEnv.sh from a caller that runs with set -e."""
    inherited = dict(os.environ)
    inherited["SETUPENV_QUIET"] = "1"
    inherited.update(environment or {})
    script = f'set -euo pipefail\nsource "{base}/setupEnv.sh"\necho JOB-LOGIC-RAN\n'
    return subprocess.run(["bash", "-c", script],
                          capture_output=True, text=True, env=inherited)


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
        got = source_profile(nikhef)
        check("the Nikhef profile resolves under `env -i`, with no USER",
              got.returncode == 0, f"rc={got.returncode} {got.stderr[:300]}")
        if got.returncode == 0:
            root, resolved_account = (got.stdout.split("\n") + ["", ""])[:2]
            check("...to a root whose segments are all usable",
                  malformed(root) == "", f"{root!r} has {malformed(root)}")
            # A path component, not a substring: /data/alice/hf -- the shared
            # directory the pilot wrote into -- contains "/alice/" already.
            check("...that carries the account as its own path segment",
                  bool(account) and account in root.split("/")[1:],
                  f"{root!r} has no segment {account!r}")
            check("...and reports the account it used",
                  resolved_account == account,
                  f"{resolved_account!r} != {account!r} from `id -un`")

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


def check_setup_env():
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
          "cannot resolve the data plane from config/sites/local.conf"
          in got.stderr, got.stderr[-300:])

    # --- 7b. a malformed sibling root stops the run too ---------------------
    # HF_PRODUCTION_ROOT decides where hundreds of gigabytes of raw campaign
    # output land, and config/site.local.conf.example invites setting it alone.
    got = source_setup_env(
        ROOT, {"HF_PRODUCTION_ROOT": "/data/alice//hadronization_production"})
    check("a malformed HF_PRODUCTION_ROOT stops the run",
          got.returncode != 0 and "JOB-LOGIC-RAN" not in got.stdout,
          f"rc={got.returncode} out={got.stdout[:200]} err={got.stderr[:300]}")

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
        # Without this, setupEnv.sh refuses further down for a different reason
        # and the well-formed case below would pass without accepting anything.
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
        override.write_text('HADRONIZATION_DATA_ROOT=/data/alice/someone/hf\n')
        got = source_setup_env(base)
        check("...and accepts the same file when the root is well formed",
              got.returncode == 0 and "JOB-LOGIC-RAN" in got.stdout,
              f"rc={got.returncode} err={got.stderr[:400]}")


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
        check_verdict()
    else:
        print("  SKIP checks 7 and 8: they read setupEnv.sh and the "
              "environment verdict in this checkout, not --sites-dir")

    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
