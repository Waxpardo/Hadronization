#!/usr/bin/env python3
"""An unknown dataset key is refused by name, before anything is arranged.

THE DEFECT THIS CLOSES. `./hadronization plot <unknown-dataset>` died with

    ./hadronization: line 71: HADRONIZATION_CAMPAIGN: unbound variable

The dataset resolution was one `eval "$(...)"`. A command substitution's exit
status is discarded, so the selector's refusal reached the caller as an EMPTY
environment and `eval ""` succeeded. The run continued into
`prepare_plot_output_plane` and failed there, on a message that names neither
the key the user typed nor the file that rejected it. Session D found it.

WHAT MUST HOLD NOW. Exit 2, the key named, the selector named, no traceback,
and nothing written under the results root. Every command that resolves a
dataset shares one resolver, so each is checked here.

WHAT MUST NOT CHANGE. A valid dataset key still resolves and the command
continues exactly as before. `test_a_valid_dataset_still_resolves` requires
the refusal to be absent and the campaign to be exported.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "hadronization"
SELECTOR = ROOT / "config" / "dataset_selector.json"
UNKNOWN = "no_such_dataset_key_20260823"
VALID = "hf_run3_v1_candidate"
# Every subcommand that names a dataset goes through the one resolver.
RESOLVING_COMMANDS = ("plot", "dataset", "freeze", "merge", "systematics")


def cli(*args: str, env_extra: dict | None = None
        ) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["HADRONIZATION_REQUEST_PREFLIGHT_ONLY"] = "1"
    env.pop("HADRONIZATION_DATASET", None)
    env.update(env_extra or {})
    return subprocess.run(["bash", str(CLI), *args], cwd=str(ROOT), env=env,
                          text=True, capture_output=True, check=False)


def test_plot_refuses_an_unknown_dataset_by_name() -> None:
    result = cli("plot", UNKNOWN)
    assert result.returncode == 2, (result.returncode, result.stderr)
    assert UNKNOWN in result.stderr, result.stderr
    assert str(SELECTOR) in result.stderr, result.stderr
    assert "dataset key rejected" in result.stderr, result.stderr


def test_the_refusal_is_not_a_traceback() -> None:
    """A traceback tells a human the reason and the caller nothing."""
    result = cli("plot", UNKNOWN)
    assert "Traceback (most recent call last)" not in result.stderr, \
        result.stderr
    assert "unbound variable" not in result.stderr, result.stderr
    assert "DATASET_SELECTOR_REFUSED" in result.stderr, result.stderr


def test_nothing_is_arranged_before_the_refusal() -> None:
    """No output plane, no directory, no symlink: the refusal comes first."""
    with tempfile.TemporaryDirectory() as tmp:
        results = Path(tmp) / "results"
        results.mkdir()
        result = cli("plot", UNKNOWN,
                     env_extra={"HADRONIZATION_RESULTS_ROOT": str(results)})
        written = sorted(p.name for p in results.rglob("*"))
    assert result.returncode == 2, result.stderr
    assert written == [], written


def test_every_dataset_command_shares_the_refusal() -> None:
    """One resolver, so one refusal. A second route would drift from it."""
    for command in RESOLVING_COMMANDS:
        result = cli(command, UNKNOWN)
        assert result.returncode == 2, (command, result.returncode,
                                        result.stderr)
        assert UNKNOWN in result.stderr, (command, result.stderr)
        assert str(SELECTOR) in result.stderr, (command, result.stderr)


def test_a_valid_dataset_still_resolves() -> None:
    """The guarantee: a known key is unaffected by the refusal."""
    result = cli("dataset", VALID)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "dataset key rejected" not in result.stderr, result.stderr
    assert "DATASET_SELECTOR_REFUSED" not in result.stderr, result.stderr
    assert "HF_RUN3_V1" in result.stdout, result.stdout


def test_the_selector_tool_itself_exits_two() -> None:
    """The bash layer reads this status; it must be a refusal, not a crash."""
    import sys
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "dataset_selector.py"), "shell",
         "--selector", str(SELECTOR), "--checkout", str(ROOT),
         "--dataset", UNKNOWN],
        cwd=str(ROOT), text=True, capture_output=True, check=False)
    assert result.returncode == 2, (result.returncode, result.stderr)
    assert result.stdout == "", result.stdout
    assert "Traceback" not in result.stderr, result.stderr
    assert UNKNOWN in result.stderr and str(SELECTOR) in result.stderr, \
        result.stderr


def main() -> int:
    tests = [v for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"unknown dataset refusal: {len(tests)} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
