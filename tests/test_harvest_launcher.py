#!/usr/bin/env python3
"""Exercise every refusal in tools/harvest_launch_merge.sh, and the lock.

WHY THIS TEST EXISTS. The launcher lived only in the Nikhef workspace until
2026-08-18. A second executor overwrote it that day, dropped the fix-presence
guard and the disk floor, and added the schema default the owner had
forbidden. Nothing failed, because nothing checked. Each refusal below is RUN,
and each is then re-run against a mutated launcher that must NOT refuse -- a
guard never seen to fail is not known to be a guard.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "tools" / "harvest_launch_merge.sh"
CAMPAIGN = "HF_SYS_TESTCAMPAIGN"

DRIVER_STUB = """#!/bin/bash
# Stub driver. Carries the HADRONIZATION_EXPECTED_PAIR_SCHEMA string because the
# launcher's fix-presence guard looks for exactly that.
echo "CLOSURE_EXPECTED_SCHEMA requested=${HADRONIZATION_EXPECTED_PAIR_SCHEMA} resolved=stub"
sleep 30
"""

DRIVER_PREFIX = """#!/bin/bash
# Stub driver WITHOUT the guard string: stands in for a checkout that predates
# the closure-gate fix.
sleep 30
"""


def _run(launcher: Path, sandbox: dict, env_extra: dict) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(
        HADRONIZATION_BASE=str(sandbox["checkout"]),
        HARVEST_WORKSPACE=str(sandbox["workspace"]),
        HARVEST_PRODUCTION_ROOT=str(sandbox["root"] / "production"),
        HARVEST_ANALYSIS_ROOT=str(sandbox["root"] / "analysis"),
        HARVEST_MERGED_ROOT=str(sandbox["root"] / "merged"),
        HARVEST_DISK_PATH=str(sandbox["root"]),
        HARVEST_DISK_FLOOR_GB="0",
        HARVEST_SETTLE_SECONDS="1",
    )
    env.pop("HADRONIZATION_EXPECTED_PAIR_SCHEMA", None)
    env.update(env_extra)
    return subprocess.run(
        ["bash", str(launcher), CAMPAIGN],
        env=env, text=True, capture_output=True, check=False,
    )


def _sandbox(stack: list, driver_text: str = DRIVER_STUB) -> dict:
    root = Path(tempfile.mkdtemp())
    stack.append(root)
    checkout = root / "checkout"
    (checkout / "merging").mkdir(parents=True)
    (checkout / "merging" / "merge_root_files.sh").write_text(driver_text)
    subprocess.run(["git", "init", "-q", str(checkout)], check=True)
    subprocess.run(["git", "-C", str(checkout), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(checkout), "-c", "user.email=t@t", "-c", "user.name=t",
         "commit", "-qm", "stub"], check=True,
    )
    workspace = root / "workspace"
    (workspace / "manifests" / CAMPAIGN).mkdir(parents=True)
    return {"root": root, "checkout": checkout, "workspace": workspace}


def _mutate(stack: list, old: str, new: str) -> Path:
    text = LAUNCHER.read_text()
    assert text.count(old) == 1, f"mutation anchor not unique: {old[:50]!r}"
    path = Path(tempfile.mkdtemp())
    stack.append(path)
    mutant = path / "mutant.sh"
    mutant.write_text(text.replace(old, new, 1))
    return mutant


def main() -> int:  # noqa: C901
    stack: list = []
    checks = 0
    try:
        # ---- 1. the schema is required, and refusing must not consume the log
        box = _sandbox(stack)
        r = _run(LAUNCHER, box, {})
        assert r.returncode == 2, r
        assert "is required and has no default" in r.stderr, r.stderr
        assert not (box["workspace"] / "merge_runs" / f"merge_{CAMPAIGN}.log").exists(), (
            "a refused launch consumed the campaign's one-shot log")
        checks += 1

        # ---- 2. an unrelated existing log refuses
        box = _sandbox(stack)
        logs = box["workspace"] / "merge_runs"
        logs.mkdir(parents=True, exist_ok=True)
        (logs / f"merge_{CAMPAIGN}.log").write_text("earlier run\n")
        r = _run(LAUNCHER, box, {"HADRONIZATION_EXPECTED_PAIR_SCHEMA": "v3"})
        assert r.returncode == 3 and "already started" in r.stderr, r
        checks += 1

        # ---- 3. a dirty checkout refuses
        box = _sandbox(stack)
        (box["checkout"] / "merging" / "merge_root_files.sh").write_text(
            DRIVER_STUB + "# tracked edit\n")
        r = _run(LAUNCHER, box, {"HADRONIZATION_EXPECTED_PAIR_SCHEMA": "v3"})
        assert r.returncode == 3 and "not tracked-clean" in r.stderr, r
        checks += 1

        # ---- 4. a checkout without the closure-gate fix refuses
        box = _sandbox(stack, DRIVER_PREFIX)
        r = _run(LAUNCHER, box, {"HADRONIZATION_EXPECTED_PAIR_SCHEMA": "v3"})
        assert r.returncode == 3 and "predates the closure-gate fix" in r.stderr, r
        checks += 1

        # ---- 5. the disk floor refuses
        box = _sandbox(stack)
        r = _run(LAUNCHER, box, {"HADRONIZATION_EXPECTED_PAIR_SCHEMA": "v3",
                                 "HARVEST_DISK_FLOOR_GB": "99999999"})
        assert r.returncode == 3 and "below the" in r.stderr, r
        checks += 1

        # ---- 6. a LIVE lock refuses and prints its contents
        box = _sandbox(stack)
        lock = box["workspace"] / "pipeline.lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(
            f"pid={os.getpid()}\npgid=1\nhost={os.uname().nodename}\n"
            f"started_utc=2026-08-18T00:00:00Z\ncampaign=OTHER\n")
        r = _run(LAUNCHER, box, {"HADRONIZATION_EXPECTED_PAIR_SCHEMA": "v3"})
        assert r.returncode == 3, r
        assert "live pipeline lock" in r.stderr, r.stderr
        assert "campaign=OTHER" in r.stderr, "the refusal must print the lock"
        checks += 1

        # ---- 7. a STALE lock refuses and says so, and does not self-clear
        box = _sandbox(stack)
        lock = box["workspace"] / "pipeline.lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        dead = subprocess.run(["bash", "-c", "echo $$"], text=True, capture_output=True)
        dead_pid = dead.stdout.strip()
        lock.write_text(
            f"pid={dead_pid}\npgid={dead_pid}\nhost={os.uname().nodename}\n"
            f"started_utc=2026-08-18T00:00:00Z\ncampaign=OTHER\n")
        r = _run(LAUNCHER, box, {"HADRONIZATION_EXPECTED_PAIR_SCHEMA": "v3"})
        assert r.returncode == 3, r
        assert "STALE pipeline lock" in r.stderr, r.stderr
        assert lock.exists(), "a stale lock must survive; only a human removes it"
        checks += 1

        # ---- 8. a lock from ANOTHER HOST refuses -- E8, we cannot ask
        box = _sandbox(stack)
        lock = box["workspace"] / "pipeline.lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(
            "pid=1\npgid=1\nhost=some-other-node.example\n"
            "started_utc=2026-08-18T00:00:00Z\ncampaign=OTHER\n")
        r = _run(LAUNCHER, box, {"HADRONIZATION_EXPECTED_PAIR_SCHEMA": "v3"})
        assert r.returncode == 3, r
        assert "cannot ask whether" in r.stderr, r.stderr
        checks += 1

        # ---- 9. the success path launches, records identity, releases the lock
        box = _sandbox(stack)
        r = _run(LAUNCHER, box, {"HADRONIZATION_EXPECTED_PAIR_SCHEMA": "v3"})
        assert r.returncode == 0, r.stderr
        identity = (box["workspace"] / "merge_runs" / f"identity_{CAMPAIGN}.txt").read_text()
        for field in ("campaign", "pid", "pgid", "host", "checkout_commit",
                      "expected_schema", "disk_free_gb", "loadavg", "launched_utc",
                      "completion_marker", "death_rule", "kill_rule"):
            assert field in identity, f"identity record lost {field}:\n{identity}"
        assert "expected_schema   = v3" in identity, identity
        assert not (box["workspace"] / "pipeline.lock").exists(), (
            "the lock must be released when the launcher exits")
        pid = [l for l in identity.splitlines() if l.startswith("pid")][0].split("=")[1]
        subprocess.run(["kill", pid.strip()], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        checks += 1

        # ---- MUTATIONS. Each must make the matching check FAIL.
        box = _sandbox(stack)
        mutant = _mutate(stack,
                         'if [ -z "${HADRONIZATION_EXPECTED_PAIR_SCHEMA:-}" ]; then',
                         'HADRONIZATION_EXPECTED_PAIR_SCHEMA="${HADRONIZATION_EXPECTED_PAIR_SCHEMA:-v3}"\n'
                         'if [ -z "${HADRONIZATION_EXPECTED_PAIR_SCHEMA:-}" ]; then')
        r = _run(mutant, box, {})
        assert r.returncode != 2, (
            "MUTATION SURVIVED: a v3 default made the schema refusal unreachable, "
            "and the test did not notice")
        checks += 1

        box = _sandbox(stack)
        lock = box["workspace"] / "pipeline.lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(f"pid={os.getpid()}\npgid=1\nhost={os.uname().nodename}\n"
                        "started_utc=x\ncampaign=OTHER\n")
        mutant = _mutate(stack, "if ! ( set -o noclobber", "if false && ( set -o noclobber")
        r = _run(mutant, box, {"HADRONIZATION_EXPECTED_PAIR_SCHEMA": "v3"})
        assert "live pipeline lock" not in r.stderr, (
            "MUTATION SURVIVED: the lock check was disabled and the test stayed green")
        checks += 1

        box = _sandbox(stack, DRIVER_PREFIX)
        mutant = _mutate(stack,
                         'if ! grep -q "HADRONIZATION_EXPECTED_PAIR_SCHEMA" "$H/merging/merge_root_files.sh"; then',
                         'if false; then')
        r = _run(mutant, box, {"HADRONIZATION_EXPECTED_PAIR_SCHEMA": "v3"})
        assert "predates the closure-gate fix" not in r.stderr, (
            "MUTATION SURVIVED: the fix-presence guard was removed unnoticed")
        subprocess.run(["bash", "-c",
                        "pkill -P $$ 2>/dev/null; true"], check=False)
        checks += 1

    finally:
        for path in stack:
            shutil.rmtree(path, ignore_errors=True)
    print(f"harvest launcher: {checks} checks passed (9 refusal/success, 3 mutations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
