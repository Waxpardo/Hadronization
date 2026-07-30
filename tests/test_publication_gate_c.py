#!/usr/bin/env python3
"""Unit tests for the fail-closed immutable publication Gate-C report."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_publication_gate_c.py"


def load_runner():
    specification = importlib.util.spec_from_file_location(
        "publication_gate_c_runner_test",
        RUNNER,
    )
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def run(*arguments: str, cwd: Path) -> str:
    result = subprocess.run(
        list(arguments),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(arguments)}\n"
            f"{result.stdout}"
        )
    return result.stdout


def prepare_git_checkout(root: Path) -> str:
    (root / "tracked.txt").write_text("canonical fixture\n")
    run("git", "init", "-q", cwd=root)
    run("git", "config", "user.name", "Gate C Test", cwd=root)
    run(
        "git",
        "config",
        "user.email",
        "gate-c@example.invalid",
        cwd=root,
    )
    run(
        "git",
        "remote",
        "add",
        "origin",
        "https://github.com/Waxpardo/Hadronization.git",
        cwd=root,
    )
    run("git", "add", "tracked.txt", cwd=root)
    run("git", "commit", "-q", "-m", "canonical fixture", cwd=root)
    return run("git", "rev-parse", "HEAD", cwd=root).strip()


def fake_records(module, returncode: int = 0) -> list[dict[str, object]]:
    return [
        {
            "name": specification.name,
            "returncode": returncode,
            "process_returncode": returncode,
            "compiler_warning_found": False,
            "log_path": f"command_logs/{specification.name}.log",
            "log_sha256": hashlib.sha256(
                specification.name.encode()
            ).hexdigest(),
        }
        for specification in module.COMMAND_SPECS
    ]


def test_requirement_evaluation(module) -> None:
    results = module.evaluate_requirements(
        fake_records(module),
        canonical=True,
    )
    assert [row["number"] for row in results] == list(range(1, 11))
    assert all(row["state"] == "PASS" for row in results)
    assert all(not row["missing_evidence"] for row in results)

    command_failure = module.evaluate_requirements(
        fake_records(module, returncode=7),
        canonical=True,
    )
    assert all(row["state"] == "FAIL" for row in command_failure)
    assert any(
        "commands failed" in item
        for row in command_failure
        for item in row["missing_evidence"]
    )

    development = module.evaluate_requirements(
        fake_records(module),
        canonical=False,
    )
    assert all(row["state"] == "FAIL" for row in development)
    assert all(
        any("development-only" in item for item in row["missing_evidence"])
        for row in development
    )


def test_immutable_report(module, temporary: Path) -> None:
    checkout = temporary / "checkout"
    checkout.mkdir()
    commit = prepare_git_checkout(checkout)
    output = temporary / "gate_c_evidence"
    module.prepare_output(checkout, output)
    command = module.CommandSpec(
        "fixture_command",
        (
            sys.executable,
            "-c",
            "print('synthetic Gate-C fixture command passed')",
        ),
        ("tracked.txt",),
    )
    runner = module.GateCRunner(
        checkout,
        output,
        development=False,
        command_specs=(command,),
    )
    with contextlib.redirect_stdout(io.StringIO()):
        runner.execute()
        status, report_path = runner.finish()
    assert status == 1
    report = json.loads(report_path.read_text())
    assert report["schema"] == "hf_publication_gate_c_report_v1"
    assert report["state"] == "FAIL"
    assert report["canonical"] is True
    assert report["environment"]["repository_commit"] == commit
    assert report["environment"]["final_repository_commit"] == commit
    assert report["environment"]["initial_status"] == ""
    assert report["environment"]["final_status"] == ""
    assert report["commands"][0]["returncode"] == 0
    assert (
        report["commands"][0]["log_sha256"]
        == hashlib.sha256(
            (
                output
                / report["commands"][0]["log_path"]
            ).read_bytes()
        ).hexdigest()
    )
    assert report["commands"][0]["input_sha256"]["tracked.txt"] == (
        hashlib.sha256((checkout / "tracked.txt").read_bytes()).hexdigest()
    )
    assert all(row["state"] == "FAIL" for row in report["requirements"])
    assert not (output.stat().st_mode & stat.S_IWUSR)
    assert not (report_path.stat().st_mode & stat.S_IWUSR)
    inventory = json.loads(
        (output / "gate_c_inventory.json").read_text()
    )
    assert inventory["schema"] == "hf_publication_gate_c_inventory_v1"
    assert inventory["state"] == "FAIL"
    inventory_paths = {row["path"] for row in inventory["files"]}
    assert "gate_c_report.json" in inventory_paths
    assert "gate_c.log" in inventory_paths

    try:
        module.prepare_output(checkout, output)
    except FileExistsError:
        pass
    else:
        raise AssertionError("write-once Gate-C output was reused")


def test_canonical_pass_report_contract(module, temporary: Path) -> None:
    checkout = temporary / "pass_checkout"
    checkout.mkdir()
    commit = prepare_git_checkout(checkout)
    output = temporary / "passing_gate_c_evidence"
    module.prepare_output(checkout, output)
    command_names = tuple(
        dict.fromkeys(
            name
            for requirement in module.REQUIREMENT_SPECS
            for name in requirement.commands
        )
    )
    command_specs = tuple(
        module.CommandSpec(
            name,
            (
                sys.executable,
                "-c",
                f"print('fixture evidence {name}')",
            ),
            ("tracked.txt",),
        )
        for name in command_names
    )
    runner = module.GateCRunner(
        checkout,
        output,
        development=False,
        command_specs=command_specs,
    )
    with contextlib.redirect_stdout(io.StringIO()):
        runner.execute()
        status, report_path = runner.finish()
    assert status == 0
    report = json.loads(report_path.read_text())
    assert report["schema"] == "hf_publication_gate_c_report_v1"
    assert report["state"] == "PASS"
    assert report["canonical"] is True
    assert report["repository_commit"] == commit
    assert report["failure"] is None
    assert report["commands"]
    assert all(row["returncode"] == 0 for row in report["commands"])
    assert all(
        row["compiler_warning_found"] is False
        for row in report["commands"]
    )
    assert all(
        not Path(row["log_path"]).is_absolute()
        and ".." not in Path(row["log_path"]).parts
        and hashlib.sha256(
            (output / row["log_path"]).read_bytes()
        ).hexdigest() == row["log_sha256"]
        for row in report["commands"]
    )
    assert all(
        row["state"] == "PASS" and not row["missing_evidence"]
        for row in report["requirements"]
    )
    assert not (output.stat().st_mode & stat.S_IWUSR)
    assert not (report_path.stat().st_mode & stat.S_IWUSR)


def test_dirty_checkout_rejected(module, temporary: Path) -> None:
    checkout = temporary / "dirty_checkout"
    checkout.mkdir()
    prepare_git_checkout(checkout)
    (checkout / "untracked.txt").write_text("dirty\n")
    output = temporary / "dirty_gate_c_evidence"
    module.prepare_output(checkout, output)
    runner = module.GateCRunner(
        checkout,
        output,
        development=False,
        command_specs=(),
    )
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            runner.execute()
        except RuntimeError as error:
            assert "completely clean checkout" in str(error)
        else:
            raise AssertionError("dirty canonical Gate C was accepted")
        runner.failure = (
            "RuntimeError: canonical Gate C requires a clean checkout"
        )
        status, report_path = runner.finish()
    assert status == 1
    report = json.loads(report_path.read_text())
    assert report["state"] == "FAIL"
    assert report["environment"]["initial_status"].startswith("?? ")


def main() -> int:
    module = load_runner()
    test_requirement_evaluation(module)
    with tempfile.TemporaryDirectory(
        prefix="hadronization_publication_gate_c_"
    ) as raw:
        temporary = Path(raw)
        test_immutable_report(module, temporary)
        test_canonical_pass_report_contract(module, temporary)
        test_dirty_checkout_rejected(module, temporary)
    print("publication Gate-C report tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
