#!/usr/bin/env python3
"""Sandbox the blocking merge supervisor and the unified-CLI route into it."""

from __future__ import annotations

import hashlib
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR = ROOT / "tools/merge_supervisor.sh"
WATCHER = ROOT / "tools/supervisor_eol_watch.sh"
SESSION_LAUNCHER = ROOT / "tools/launch_in_new_session.py"
CLI = ROOT / "hadronization"
SMOKE_SELECTOR = ROOT / "config/dataset_selector_hf_smoke3.json"

sys.path.insert(0, str(ROOT / "tests"))
from test_cli_surface import run_cli, sandbox  # noqa: E402


MERGE_STUB = r'''#!/bin/bash
set -uo pipefail
{
  echo BEGIN
  echo "PAIR=${HADRONIZATION_EXPECTED_PAIR_SCHEMA:-}"
  for argument in "$@"; do echo "ARG=${argument}"; done
  echo END
} >> "${STUB_CALLS}"
attempts="$(grep -c '^BEGIN$' "${STUB_CALLS}")"
case "${STUB_BEHAVIOR}" in
  clean)
    echo "CANONICAL_SUPERVISED_MERGE_COMPLETE output_tag=$5 pair_schema=test"
    exit 0
    ;;
  zero_without_marker) exit 0 ;;
  nonzero) exit 7 ;;
  interrupt_then_clean)
    if [[ "${attempts}" -eq 1 ]]; then kill -TERM "$$"; fi
    echo "CANONICAL_SUPERVISED_MERGE_COMPLETE output_tag=$5 pair_schema=test"
    exit 0
    ;;
  always_interrupt) kill -TERM "$$" ;;
  advance_head_then_interrupt)
    git -C "${MUTATE_CHECKOUT}" -c user.name=t -c user.email=t@t \
      commit -q --allow-empty -m advanced
    kill -TERM "$$"
    ;;
  replace_manifest_then_interrupt)
    echo replaced >> "${MUTATE_MANIFEST}"
    kill -TERM "$$"
    ;;
  *) exit 91 ;;
esac
'''

PRECHECK_STUB = r'''#!/bin/bash
echo PRECHECK >> "${PRECHECK_CALLS}"
[[ "${PRECHECK_FAIL:-0}" != 1 ]]
'''

PROCESS_TREE_STUB = r'''#!/bin/bash
set -uo pipefail
trap '' HUP INT TERM
(
  trap '' HUP INT TERM
  sleep 300
) &
grandchild=$!
printf '%s %s\n' "$$" "${grandchild}" > "${DESCENDANT_PIDS}"
wait "${grandchild}"
'''


def executable(path: Path, text: str) -> None:
    path.write_text(text)
    path.chmod(0o755)


def git_output(checkout: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(checkout), *arguments], text=True).strip()


def case_tree(base: Path) -> dict:
    checkout = base / "checkout"
    checkout.mkdir()
    subprocess.run(["git", "-C", str(checkout), "init", "-q"], check=True)
    (checkout / "tracked.txt").write_text("tracked\n")
    subprocess.run(["git", "-C", str(checkout), "add", "tracked.txt"], check=True)
    subprocess.run([
        "git", "-C", str(checkout), "-c", "user.name=t", "-c",
        "user.email=t@t", "commit", "-q", "-m", "base"], check=True)
    freeze = base / "freeze"
    freeze.mkdir()
    manifest = freeze / "canonical_manifest.jsonl"
    manifest.write_text('{"schema":"synthetic"}\n')
    production = base / "production"
    analysis = base / "analysis"
    merged = base / "merged"
    for path in (production, analysis, merged):
        path.mkdir()
    merge_stub = base / "merge_stub.sh"
    precheck_stub = base / "precheck_stub.sh"
    executable(merge_stub, MERGE_STUB)
    executable(precheck_stub, PRECHECK_STUB)
    return {
        "checkout": checkout,
        "freeze": freeze,
        "manifest": manifest,
        "production": production,
        "analysis": analysis,
        "merged": merged,
        "merge_stub": merge_stub,
        "precheck_stub": precheck_stub,
        "calls": base / "calls.log",
        "prechecks": base / "prechecks.log",
        "run_root": base / "run",
    }


def supervisor_environment(box: dict, behavior: str, *, restarts: int = 2,
                           extra: dict[str, str] | None = None
                           ) -> dict[str, str]:
    environment = dict(os.environ)
    environment.update({
        "HADRONIZATION_BASE": str(box["checkout"]),
        "HADRONIZATION_MERGE_RUN_ROOT": str(box["run_root"]),
        "HADRONIZATION_SUPERVISOR_MERGE_CMD": str(box["merge_stub"]),
        "HADRONIZATION_SUPERVISOR_WATCH_CMD": str(WATCHER),
        "HADRONIZATION_SUPERVISOR_SESSION_LAUNCHER": str(SESSION_LAUNCHER),
        "HADRONIZATION_SUPERVISOR_PRECHECK_CMD": str(box["precheck_stub"]),
        "HADRONIZATION_SUPERVISOR_PYTHON": sys.executable,
        "HADRONIZATION_SUPERVISOR_POLL_SECONDS": "0.01",
        "HADRONIZATION_SUPERVISOR_WATCH_MAX_POLLS": "1000",
        "HADRONIZATION_MERGE_MAX_RESTARTS": str(restarts),
        "HADRONIZATION_MERGE_TERM_GRACE_POLL_SECONDS": "0.01",
        "HADRONIZATION_MERGE_TERM_GRACE_MAX_POLLS": "5",
        "STUB_CALLS": str(box["calls"]),
        "PRECHECK_CALLS": str(box["prechecks"]),
        "STUB_BEHAVIOR": behavior,
        "MUTATE_CHECKOUT": str(box["checkout"]),
        "MUTATE_MANIFEST": str(box["manifest"]),
    })
    environment.update(extra or {})
    return environment


def supervisor_arguments(box: dict, supervisor: Path = SUPERVISOR) -> list[str]:
    head = git_output(box["checkout"], "rev-parse", "HEAD")
    manifest_sha = hashlib.sha256(box["manifest"].read_bytes()).hexdigest()
    return [
        "bash", str(supervisor), str(box["freeze"]),
        str(box["production"]), str(box["analysis"]), str(box["merged"]),
        "CAMPAIGN_X", "pair_schema_x", head, manifest_sha,
    ]


def assert_watchers_reaped(output: str) -> None:
    time.sleep(0.01)
    for text_pid in re.findall(r"watcher_pid=([0-9]+)", output):
        try:
            os.kill(int(text_pid), 0)
        except ProcessLookupError:
            continue
        raise AssertionError(f"watcher PID {text_pid} survived supervisor exit")


def run_supervisor(box: dict, behavior: str, *, restarts: int = 2,
                   extra: dict[str, str] | None = None,
                   supervisor: Path = SUPERVISOR,
                   ) -> subprocess.CompletedProcess:
    environment = supervisor_environment(
        box, behavior, restarts=restarts, extra=extra)
    result = subprocess.run([
        *supervisor_arguments(box, supervisor),
    ], env=environment, text=True, capture_output=True, timeout=15)
    # Every watcher PID the supervisor reported must have been reaped.
    assert_watchers_reaped(result.stdout)
    return result


def launch_count(box: dict) -> int:
    return box["calls"].read_text().count("BEGIN\n") if box["calls"].exists() else 0


def precheck_count(box: dict) -> int:
    return (box["prechecks"].read_text().count("PRECHECK\n")
            if box["prechecks"].exists() else 0)


def pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


LINUX_PROCFS = Path("/proc/self/stat").is_file()


def linux_process_state(pid: int) -> str | None:
    if not LINUX_PROCFS:
        return None
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except FileNotFoundError:
        return None
    closing_parenthesis = stat.rfind(")")
    if closing_parenthesis < 0:
        raise AssertionError(f"malformed /proc stat for PID {pid}")
    fields = stat[closing_parenthesis + 2:].split()
    if not fields:
        raise AssertionError(f"missing process state for PID {pid}")
    return fields[0]


def pid_is_running(pid: int) -> bool:
    if not pid_exists(pid):
        return False
    if not LINUX_PROCFS:
        return True
    state = linux_process_state(pid)
    return state is not None and state not in {"X", "Z"}


def wait_pid_not_running(pid: int, timeout: float = 3.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not pid_is_running(pid):
            return True
        time.sleep(0.01)
    return not pid_is_running(pid)


def assert_linux_zombie_is_not_running() -> None:
    if not LINUX_PROCFS:
        return
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    try:
        deadline = time.monotonic() + 2
        state = linux_process_state(child.pid)
        while state != "Z" and time.monotonic() < deadline:
            time.sleep(0.01)
            state = linux_process_state(child.pid)
        assert state == "Z", f"child {child.pid} did not enter zombie state"
        assert pid_exists(child.pid), "kill(pid, 0) did not see the zombie"
        assert not pid_is_running(child.pid), "zombie reported as running"
        print("  Linux zombie: kill0-present state=Z not-running")
    finally:
        child.wait(timeout=2)


def test_all_resolved_arguments_and_pair_schema_arrive_unchanged() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        result = run_supervisor(box, "clean")
        lines = box["calls"].read_text().splitlines()
    assert result.returncode == 0, result.stdout + result.stderr
    assert lines == [
        "BEGIN", "PAIR=pair_schema_x",
        f"ARG={box['freeze']}", f"ARG={box['production']}",
        f"ARG={box['analysis']}", f"ARG={box['merged']}",
        "ARG=CAMPAIGN_X", "END",
    ], lines


def test_clean_exit_plus_marker_succeeds_without_restart() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        result = run_supervisor(box, "clean")
        launches = launch_count(box)
    assert result.returncode == 0, result.stdout + result.stderr
    assert launches == 1
    assert "PASS clean_exit_and_final_marker" in result.stdout


def test_preserved_untracked_artifact_is_ignored_and_untouched() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        artifact = box["checkout"] / "preserved.move-aside"
        payload = b"nikhef-preserved\x00bytes\n"
        artifact.write_bytes(payload)
        original_path = artifact.resolve()
        result = run_supervisor(box, "clean")
        launches = launch_count(box)
        assert artifact.resolve() == original_path
        assert artifact.read_bytes() == payload
        assert "preserved.move-aside" not in box["calls"].read_text()
    assert result.returncode == 0, result.stdout + result.stderr
    assert launches == 1
    print("  untracked artifact: exit=0 launches=1 byte-identical and unmoved")


def test_tracked_modification_refuses_before_launch() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        (box["checkout"] / "tracked.txt").write_text("modified\n")
        result = run_supervisor(box, "clean")
        launches = launch_count(box)
    assert result.returncode == 64, result.stdout + result.stderr
    assert launches == 0
    assert "REFUSAL_CHECKOUT_DIRTY" in result.stdout
    print("  tracked dirty: exit=64 launches=0 named refusal")


def test_failed_git_status_is_a_named_refusal_and_launches_nothing() -> None:
    real_git = shutil.which("git")
    assert real_git is not None
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        git_stub = Path(temporary) / "git_status_failure.sh"
        executable(git_stub, r'''#!/bin/bash
if [[ " $* " == *" status "* ]]; then exit 71; fi
exec "${REAL_GIT}" "$@"
''')
        result = run_supervisor(
            box, "clean",
            extra={"HADRONIZATION_SUPERVISOR_GIT": str(git_stub),
                   "REAL_GIT": real_git})
        launches = launch_count(box)
    assert result.returncode == 64, result.stdout + result.stderr
    assert launches == 0
    assert "REFUSAL_CHECKOUT_STATUS_FAILED" in result.stdout
    print("  failed git status: exit=64 launches=0 named refusal")


def test_seen_to_fail_untracked_files_all_mutation_rejects_preserved_artifact() -> None:
    text = SUPERVISOR.read_text()
    assert "--untracked-files=no" in text
    mutated_text = text.replace("--untracked-files=no", "--untracked-files=all", 1)
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        artifact = box["checkout"] / "preserved.move-aside"
        payload = b"preserved mutation anchor\n"
        artifact.write_bytes(payload)
        mutated = Path(temporary) / "merge_supervisor_untracked_all.sh"
        executable(mutated, mutated_text)
        result = run_supervisor(box, "clean", supervisor=mutated)
        launches = launch_count(box)
        remained = artifact.is_file() and artifact.read_bytes() == payload
    assert result.returncode == 64, result.stdout + result.stderr
    assert launches == 0
    assert remained
    assert "REFUSAL_CHECKOUT_DIRTY" in result.stdout
    print("  seen to fail: --untracked-files=all rejects preserved artifact")


def test_exit_zero_without_marker_fails() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        result = run_supervisor(box, "zero_without_marker")
        launches = launch_count(box)
    assert result.returncode != 0
    assert launches == 1
    assert "FAIL missing_final_marker" in result.stdout


def test_deterministic_nonzero_fails_without_restart() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        result = run_supervisor(box, "nonzero")
        launches = launch_count(box)
    assert result.returncode == 7, result.stdout + result.stderr
    assert launches == 1
    assert "deterministic_child_exit=7 no_restart" in result.stdout


def test_one_interrupted_attempt_rechecks_and_can_succeed() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        result = run_supervisor(box, "interrupt_then_clean")
        launches = launch_count(box)
        checks = precheck_count(box)
    assert result.returncode == 0, result.stdout + result.stderr
    assert launches == 2 and checks == 2
    assert "RESTART_ALLOWED restart=1" in result.stdout


def test_failed_precheck_launches_nothing() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        result = run_supervisor(box, "clean", extra={"PRECHECK_FAIL": "1"})
        launches = launch_count(box)
    assert result.returncode != 0
    assert launches == 0
    assert "REFUSAL_PRECHECK_COMMAND_FAILED" in result.stdout


def test_changed_head_or_manifest_refuses_restart() -> None:
    for behavior, refusal in (
            ("advance_head_then_interrupt", "REFUSAL_HEAD_CHANGED"),
            ("replace_manifest_then_interrupt", "REFUSAL_MANIFEST_CHANGED")):
        with tempfile.TemporaryDirectory() as temporary:
            box = case_tree(Path(temporary))
            result = run_supervisor(box, behavior)
            launches = launch_count(box)
        assert result.returncode != 0, behavior
        assert launches == 1, behavior
        assert refusal in result.stdout, result.stdout


def test_unavailable_interpreter_is_a_named_refusal() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        result = run_supervisor(
            box, "clean", extra={"HADRONIZATION_SUPERVISOR_PYTHON":
                                  str(Path(temporary) / "missing-python")})
        launches = launch_count(box)
    assert result.returncode != 0
    assert launches == 0
    assert "REFUSAL_INTERPRETER_UNAVAILABLE" in result.stdout


def test_exhausted_restart_budget_fails() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        box = case_tree(Path(temporary))
        result = run_supervisor(box, "always_interrupt", restarts=1)
        launches = launch_count(box)
    assert result.returncode == 75, result.stdout + result.stderr
    assert launches == 2
    assert "restart_budget_exhausted" in result.stdout


def test_term_and_int_end_exact_merge_group_but_not_caller() -> None:
    assert_linux_zombie_is_not_running()
    for sent_signal in (signal.SIGTERM, signal.SIGINT):
        supervisor = None
        shell_pid = None
        grandchild_pid = None
        output = ""
        try:
            with tempfile.TemporaryDirectory() as temporary:
                box = case_tree(Path(temporary))
                executable(box["merge_stub"], PROCESS_TREE_STUB)
                identities = Path(temporary) / "descendant_pids"
                environment = supervisor_environment(
                    box, "unused", restarts=0,
                    extra={"DESCENDANT_PIDS": str(identities)})
                supervisor = subprocess.Popen(
                    supervisor_arguments(box),
                    env=environment, text=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                deadline = time.monotonic() + 5
                while not identities.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                assert identities.exists(), "merge descendants did not start"
                shell_pid, grandchild_pid = map(
                    int, identities.read_text().split())
                merge_pgid = os.getpgid(shell_pid)
                assert merge_pgid == shell_pid
                assert os.getpgid(grandchild_pid) == merge_pgid
                assert os.getpgid(supervisor.pid) != merge_pgid
                caller_pid = os.getpid()
                caller_pgid = os.getpgrp()
                assert caller_pgid != merge_pgid

                supervisor.send_signal(sent_signal)
                output, _ = supervisor.communicate(timeout=5)
                assert supervisor.returncode == 130, output
                assert wait_pid_not_running(shell_pid), (
                    f"shell {shell_pid} remained running "
                    f"state={linux_process_state(shell_pid)}")
                assert wait_pid_not_running(grandchild_pid), (
                    f"grandchild {grandchild_pid} remained running "
                    f"state={linux_process_state(grandchild_pid)}")
                assert pid_exists(caller_pid), "test caller was signalled"
                assert_watchers_reaped(output)
                print(
                    f"  {signal.Signals(sent_signal).name}: supervisor=130 "
                    "shell-not-running grandchild-not-running "
                    "caller-alive watcher-reaped")
        finally:
            if supervisor is not None and supervisor.poll() is None:
                supervisor.kill()
                supervisor.wait(timeout=2)
            if shell_pid is not None:
                try:
                    os.killpg(shell_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            for diagnostic_pid in (grandchild_pid, shell_pid):
                if diagnostic_pid is not None and pid_exists(diagnostic_pid):
                    try:
                        os.kill(diagnostic_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass


def test_supervisor_pair_has_no_stale_discovery_or_campaign_pins() -> None:
    combined = SUPERVISOR.read_text() + WATCHER.read_text()
    for forbidden in (
            "pgrep", "newest_log", "ls -t", "HF_RUN3_V1",
            "43e35be876dd5d881a931cb845ab490ab9b97509",
            "fcd96eaebd4dc11f071a2c8db8849f6a4cc19b764622a796664e524b27d0fc80",
            "/cvmfs/", "2026-08-10"):
        assert forbidden not in combined, forbidden
    watcher = WATCHER.read_text()
    assert re.search(r"\bkill\s+(?!-0\b)", watcher) is None, (
        "the EOL watcher must observe the exact PID, never signal it")


def supervised_merge_branch(text: str) -> str:
    start = text.index("\n  merge)")
    end = text.index("\n  systematics)", start)
    branch = text[start:end]
    if "tools/merge_supervisor.sh" not in branch:
        raise AssertionError("merge branch does not invoke merge_supervisor.sh")
    if "merging/merge_root_files.sh" in branch:
        raise AssertionError("merge branch contains a direct merge-driver bypass")
    return branch


def test_cli_reaches_supervisor_and_has_no_direct_bypass() -> None:
    supervised_merge_branch(CLI.read_text())
    supervisor_stub = r'''#!/bin/bash
printf '%s\n' "$@" > "${CLI_CAPTURE}"
exit "${CLI_SUPERVISOR_EXIT:-0}"
'''
    with tempfile.TemporaryDirectory() as temporary:
        base = sandbox(
            temporary,
            replace={"tools/merge_supervisor.sh": supervisor_stub},
            git=True)
        data = Path(temporary) / "data"
        manifest = data / "project/runs/HF_SMOKE3/freeze/canonical_manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text('{"schema":"synthetic"}\n')
        capture = Path(temporary) / "cli_capture"
        result = run_cli(
            base, data, ["merge", "hf_smoke3", "v2"],
            {"HADRONIZATION_DATASET_SELECTOR": str(SMOKE_SELECTOR),
             "CLI_CAPTURE": str(capture), "CLI_SUPERVISOR_EXIT": "23"})
        arguments = capture.read_text().splitlines()
        head = git_output(base, "rev-parse", "HEAD")
        digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert result.returncode == 23, result.stdout + result.stderr
    assert arguments == [
        str(manifest.parent),
        str(data / "hadronization_production/HF_SMOKE3"),
        str(data / "hadronization_analysis/HF_SMOKE3"),
        str(data / "hadronization_merged"),
        "HF_SMOKE3", "v2", head, digest,
    ], arguments


def test_seen_to_fail_former_direct_merge_routing_mutation() -> None:
    mutated = CLI.read_text().replace(
        "tools/merge_supervisor.sh", "merging/merge_root_files.sh", 1)
    try:
        supervised_merge_branch(mutated)
    except AssertionError as error:
        assert "merge_supervisor" in str(error) or "bypass" in str(error)
        return
    raise AssertionError("former direct merge routing mutation survived")


def main() -> int:
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"merge supervisor: {len(tests)} sandbox checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
