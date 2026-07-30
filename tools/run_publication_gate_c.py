#!/usr/bin/env python3
"""Run the immutable publication Gate-C workflow/failure audit.

This gate is intentionally evidence driven.  A successful regression command
is not treated as evidence for a claim that the regression does not actually
exercise.  Requirements with known evidence gaps remain ``FAIL`` until a
targeted test is added and the requirement table below is updated.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import shlex
import stat
import subprocess
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


SCHEMA = "hf_publication_gate_c_report_v1"
INVENTORY_SCHEMA = "hf_publication_gate_c_inventory_v1"
ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CommandSpec:
    """One independently logged Gate-C regression command."""

    name: str
    arguments: tuple[str, ...]
    inputs: tuple[str, ...]
    required_markers: tuple[str, ...] = ()


@dataclass(frozen=True)
class RequirementSpec:
    """Evidence contract for one numbered Section-16 Gate-C requirement."""

    number: int
    title: str
    commands: tuple[str, ...]
    confirmed_claims: tuple[str, ...]
    missing_evidence: tuple[str, ...] = ()


COMMAND_SPECS = (
    CommandSpec(
        "git_diff_check",
        ("git", "diff", "--check", "origin/main...HEAD"),
        (),
    ),
    CommandSpec(
        "worker_provenance_contract",
        (sys.executable, "tests/test_worker_provenance_contract.py"),
        (
            "tests/test_worker_provenance_contract.py",
            "runCondorJob.sh",
            "tools/campaign_manifest.py",
        ),
    ),
    CommandSpec(
        "full_submission_contract",
        (sys.executable, "tests/test_full_submission_contract.py"),
        (
            "tests/test_full_submission_contract.py",
            "submit_full_production.sh",
            "submit_full_retry.sh",
            "tools/campaign_manifest.py",
            "tools/render_production_submit.py",
        ),
    ),
    CommandSpec(
        "gate_b_submission_contract",
        (sys.executable, "tests/test_gate_b_submission_contract.py"),
        (
            "tests/test_gate_b_submission_contract.py",
            "submit_gate_b_pilots.sh",
            "tools/campaign_manifest.py",
            "tools/render_production_submit.py",
        ),
    ),
    CommandSpec(
        "submit_rendering_contract",
        (sys.executable, "tests/test_submit_rendering.py"),
        (
            "tests/test_submit_rendering.py",
            "tools/render_production_submit.py",
            "tools/render_analysis_submit.py",
        ),
    ),
    CommandSpec(
        "canonical_postproduction_contract",
        (
            sys.executable,
            "tests/test_canonical_postproduction_contract.py",
        ),
        (
            "tests/test_canonical_postproduction_contract.py",
            "tools/canonical_manifest.py",
            "tools/render_analysis_submit.py",
            "submit_status_analysis.sh",
            "merge_root_files.sh",
            "make_subsamples.sh",
            "tools/validate_analysis_outputs.py",
        ),
    ),
    CommandSpec(
        "gate_b_analysis_validation_contract",
        (
            sys.executable,
            "tests/test_gate_b_analysis_validation.py",
        ),
        (
            "tests/test_gate_b_analysis_validation.py",
            "tools/validate_gate_b_analysis_outputs.py",
            "AnalysisScripts/status_analysis_THnSparse_qq.C",
        ),
    ),
    CommandSpec(
        "statistical_robustness_contract",
        (sys.executable, "tests/test_statistical_robustness.py"),
        (
            "tests/test_statistical_robustness.py",
            "tools/statistical_robustness.py",
            "config/statistical_robustness_v1.json",
        ),
    ),
    CommandSpec(
        "publication_gate_c_report_contract",
        (
            sys.executable,
            "tests/test_publication_gate_c.py",
        ),
        (
            "tests/test_publication_gate_c.py",
            "tools/run_publication_gate_c.py",
            "run_publication_gate_c.sh",
        ),
    ),
    CommandSpec(
        "gate_c_missing_evidence_contract",
        (
            sys.executable,
            "tests/test_gate_c_missing_evidence.py",
        ),
        (
            "tests/test_gate_c_missing_evidence.py",
            "tools/gate_c_workflow_audit.py",
            "runCondorJob.sh",
            "tools/campaign_manifest.py",
            "tools/render_production_submit.py",
            "tools/render_analysis_submit.py",
            "submit_status_analysis.sh",
            "merge_root_files.sh",
            "make_subsamples.sh",
            "PlottingScripts/improvedPlotting_THnSparse.C",
        ),
        (
            "GATE_C_EVIDENCE requirement=2 state=PASS "
            "started_then_evicted_partial_not_promoted=true",
            "GATE_C_EVIDENCE requirement=7 state=PASS "
            "lowest_valid_reserve_deterministic=true",
            "GATE_C_EVIDENCE requirement=8 state=PASS "
            "duplicate_global_event_id_rejected=true",
            "GATE_C_EVIDENCE requirement=9 state=PASS "
            "synthetic_and_pilot_metadata_bias_diagnostic=true",
            "GATE_C_EVIDENCE requirement=10 state=PASS "
            "same_manifest_all_stages_extra_reserve_rejected=true",
        ),
    ),
)


# Every requirement below names executable evidence. Do not turn an adjacent
# test into evidence for a new claim: add a targeted assertion and marker.
REQUIREMENT_SPECS = (
    RequirementSpec(
        1,
        "Force a generation failure",
        ("worker_provenance_contract",),
        (
            "A synthetic producer exits nonzero and the worker records the "
            "failure.",
        ),
    ),
    RequirementSpec(
        2,
        "Emulate eviction or wall-time termination",
        ("gate_c_missing_evidence_contract",),
        (
            "A worker that has created an attempt-start claim and partial "
            "output is terminated as a process group; the partial remains "
            "unpromoted and no validation PASS receipt exists.",
        ),
    ),
    RequirementSpec(
        3,
        "Prove partial files are not promoted",
        ("worker_provenance_contract",),
        (
            "Producer-failed and validator-failed partial outputs do not "
            "appear at the stable logical path.",
        ),
    ),
    RequirementSpec(
        4,
        "Retry the same logical ID with a new attempt and seed",
        ("full_submission_contract",),
        (
            "The synthetic full campaign allocates attempt 1 for the same "
            "logical ID with a distinct deterministic seed and binds its "
            "retry submission.",
        ),
    ),
    RequirementSpec(
        5,
        "Reject a corrupt or merely nonempty file",
        (
            "worker_provenance_contract",
            "full_submission_contract",
            "gate_b_submission_contract",
        ),
        (
            "A nonempty invalid producer output receives a FAIL validation "
            "receipt and is not promoted.",
            "Mutation after a PASS receipt invalidates the receipt instead "
            "of being skipped.",
        ),
    ),
    RequirementSpec(
        6,
        "Dry-run exactly 100/200/200 candidate slots",
        ("full_submission_contract", "submit_rendering_contract"),
        (
            "The synthetic full manifest contains exactly 500 candidates: "
            "100 MONASH, 200 JUNCTIONS, and 200 CLOSEPACKING.",
            "The deterministic renderer is exercised from the manifest.",
        ),
    ),
    RequirementSpec(
        7,
        "Demonstrate deterministic canonical selection and reserve substitution",
        (
            "canonical_postproduction_contract",
            "gate_c_missing_evidence_contract",
        ),
        (
            "The structural canonical contract checks 300 ordered rows and "
            "ten deterministic blocks.",
            "Two independently ordered synthetic inventories produce the "
            "same selection digest, missing primaries are replaced by the "
            "lowest valid reserve, and physics-sensitive selection fields "
            "are rejected.",
        ),
    ),
    RequirementSpec(
        8,
        "Run global seed and event-ID collision checks",
        (
            "full_submission_contract",
            "gate_b_submission_contract",
            "gate_c_missing_evidence_contract",
        ),
        (
            "Cross-checkout seed-range reuse is rejected by the shared "
            "submission registry.",
            "The C++ event-ID layout is mirrored as disjoint manifest ranges; "
            "an injected duplicate event ID and duplicate provenance prefix "
            "are both rejected.",
        ),
    ),
    RequirementSpec(
        9,
        "Demonstrate primary/reserve and failure-bias diagnostics",
        ("gate_c_missing_evidence_contract",),
        (
            "The diagnostic reports valid primary/reserve and valid/failed "
            "cohorts for technical and physics-sensitive monitoring fields, "
            "detects an injected association, rejects non-finite metadata, "
            "and explicitly requires human review.",
        ),
    ),
    RequirementSpec(
        10,
        "Prove every downstream stage consumes one canonical manifest",
        (
            "canonical_postproduction_contract",
            "gate_b_analysis_validation_contract",
            "statistical_robustness_contract",
            "gate_c_missing_evidence_contract",
        ),
        (
            "Submission rendering and merge/statistics source contracts bind "
            "canonical-manifest hashes.",
            "One 300-row manifest drives the synthetic status, central merge, "
            "ten block/subsample, and plot-selection contracts; an extra "
            "reserve is rejected independently at every transition.",
        ),
    ),
)


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="seconds"
    )


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def exclusive_text(path: Path, text: str, mode: int = 0o444) -> None:
    """Create a regular file once and fsync it before returning."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        mode,
    )
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        # Retain a partial write as a fail-closed marker.
        raise


def git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *arguments],
        text=True,
    ).strip()


def input_hashes(root: Path, relative_paths: Sequence[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in relative_paths:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(
                f"Gate-C command input is absent or non-regular: {relative}"
            )
        result[relative] = sha256(path)
    return result


def evaluate_requirements(
    command_records: Sequence[dict[str, object]],
    *,
    canonical: bool,
) -> list[dict[str, object]]:
    """Evaluate numbered requirements without inferring untested claims."""

    by_name = {
        str(record["name"]): record
        for record in command_records
    }
    results: list[dict[str, object]] = []
    for specification in REQUIREMENT_SPECS:
        absent = [
            name for name in specification.commands if name not in by_name
        ]
        failed = [
            name
            for name in specification.commands
            if name in by_name and int(by_name[name]["returncode"]) != 0
        ]
        missing = list(specification.missing_evidence)
        if absent:
            missing.append(
                "Required evidence commands were not executed: "
                + ", ".join(absent)
            )
        if failed:
            missing.append(
                "Required evidence commands failed: " + ", ".join(failed)
            )
        if not canonical:
            missing.append(
                "The run is development-only and is not bound to a clean "
                "canonical checkout."
            )
        state = "PASS" if not missing else "FAIL"
        command_evidence = []
        for name in specification.commands:
            if name not in by_name:
                continue
            record = by_name[name]
            command_evidence.append(
                {
                    "name": name,
                    "returncode": record["returncode"],
                    "log_path": record["log_path"],
                    "log_sha256": record["log_sha256"],
                }
            )
        evidence_commands_passed = not absent and not failed
        results.append(
            {
                "number": specification.number,
                "title": specification.title,
                "state": state,
                "evidenced_claims": (
                    list(specification.confirmed_claims)
                    if evidence_commands_passed
                    else []
                ),
                "missing_evidence": missing,
                "commands": command_evidence,
            }
        )
    return results


class GateCRunner:
    def __init__(
        self,
        root: Path,
        output: Path,
        *,
        development: bool,
        command_specs: Sequence[CommandSpec] = COMMAND_SPECS,
    ) -> None:
        self.root = root
        self.output = output
        self.development = development
        self.command_specs = tuple(command_specs)
        self.started = utc_now()
        self.commands: list[dict[str, object]] = []
        self.environment: dict[str, object] = {}
        self.failure: str | None = None
        self.requirements: list[dict[str, object]] = []
        self.log_path = output / "gate_c.log"
        self.log = self.log_path.open("x", buffering=1)
        self.command_log_dir = output / "command_logs"
        self.command_log_dir.mkdir(mode=0o700)

    def write(self, value: str) -> None:
        self.log.write(value)
        if not value.endswith("\n"):
            self.log.write("\n")
        self.log.flush()
        print(value, flush=True)

    def establish_environment(self) -> None:
        commit = git(self.root, "rev-parse", "HEAD")
        branch = git(self.root, "branch", "--show-current")
        origin = git(self.root, "remote", "get-url", "origin")
        tree = git(self.root, "rev-parse", "HEAD^{tree}")
        status = git(
            self.root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
        tracked_status = git(
            self.root,
            "status",
            "--porcelain=v1",
            "--untracked-files=no",
        )
        self.environment = {
            "repository_root": str(self.root),
            "repository_commit": commit,
            "repository_tree": tree,
            "branch": branch,
            "origin": origin,
            "canonical": not self.development,
            "initial_status": status,
            "initial_tracked_status": tracked_status,
            "python_version": sys.version,
        }
        if not self.development and status:
            raise RuntimeError(
                "canonical Gate C requires a completely clean checkout"
            )

    def run_command(self, index: int, specification: CommandSpec) -> None:
        log_relative = (
            Path("command_logs")
            / f"{index:02d}_{specification.name}.log"
        )
        log_path = self.output / log_relative
        arguments = [str(value) for value in specification.arguments]
        started = utc_now()
        self.write(
            "\nGATE_C_COMMAND_START "
            f"name={specification.name} command={shlex.join(arguments)}"
        )
        result = subprocess.run(
            arguments,
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        command_output = result.stdout or ""
        exclusive_text(log_path, command_output)
        missing_markers = [
            marker
            for marker in specification.required_markers
            if marker not in command_output
        ]
        effective_returncode = (
            result.returncode
            if result.returncode != 0 or not missing_markers
            else 97
        )
        record = {
            "name": specification.name,
            "started_utc": started,
            "finished_utc": utc_now(),
            "cwd": str(self.root),
            "command": arguments,
            "returncode": effective_returncode,
            "process_returncode": result.returncode,
            "compiler_warning_found": False,
            "input_sha256": input_hashes(
                self.root, specification.inputs
            ),
            "required_markers": list(specification.required_markers),
            "missing_markers": missing_markers,
            "log_path": log_relative.as_posix(),
            "log_bytes": log_path.stat().st_size,
            "log_sha256": sha256(log_path),
        }
        self.commands.append(record)
        if command_output:
            self.log.write(command_output)
            if not command_output.endswith("\n"):
                self.log.write("\n")
            self.log.flush()
        self.write(
            "GATE_C_COMMAND_END "
            f"name={specification.name} "
            f"returncode={effective_returncode} "
            f"process_returncode={result.returncode} "
            f"log_sha256={record['log_sha256']}"
        )

    def execute(self) -> None:
        self.establish_environment()
        for index, specification in enumerate(self.command_specs, start=1):
            try:
                self.run_command(index, specification)
            except BaseException as error:
                self.failure = (
                    f"{type(error).__name__} while running "
                    f"{specification.name}: {error}"
                )
                self.write(traceback.format_exc())
                break

        final_commit = git(self.root, "rev-parse", "HEAD")
        final_tree = git(self.root, "rev-parse", "HEAD^{tree}")
        final_branch = git(self.root, "branch", "--show-current")
        final_status = git(
            self.root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
        final_tracked_status = git(
            self.root,
            "status",
            "--porcelain=v1",
            "--untracked-files=no",
        )
        self.environment["final_repository_commit"] = final_commit
        self.environment["final_repository_tree"] = final_tree
        self.environment["final_branch"] = final_branch
        self.environment["final_status"] = final_status
        self.environment["final_tracked_status"] = final_tracked_status
        if (
            final_commit != self.environment["repository_commit"]
            or final_tree != self.environment["repository_tree"]
            or final_branch != self.environment["branch"]
            or final_status != self.environment["initial_status"]
            or final_tracked_status
            != self.environment["initial_tracked_status"]
        ):
            self.failure = (
                self.failure
                or "Gate-C validation changed repository worktree state"
            )
        self.requirements = evaluate_requirements(
            self.commands,
            canonical=not self.development,
        )

    def finish(self) -> tuple[int, Path]:
        if not self.requirements:
            self.requirements = evaluate_requirements(
                self.commands,
                canonical=not self.development,
            )
        command_failures = [
            str(record["name"])
            for record in self.commands
            if int(record["returncode"]) != 0
        ]
        if command_failures and self.failure is None:
            self.failure = (
                "Gate-C regression commands failed: "
                + ", ".join(command_failures)
            )
        if self.development and self.failure is None:
            self.failure = (
                "development mode cannot produce a canonical Gate-C PASS"
            )
        failed_requirements = [
            int(row["number"])
            for row in self.requirements
            if row["state"] != "PASS"
        ]
        if failed_requirements and self.failure is None:
            self.failure = (
                "Gate-C requirements lack complete executable evidence: "
                + ", ".join(str(value) for value in failed_requirements)
            )

        symlinks = sorted(
            path.relative_to(self.output).as_posix()
            for path in self.output.rglob("*")
            if path.is_symlink()
        )
        if symlinks and self.failure is None:
            self.failure = (
                "Gate-C evidence contains symbolic links: "
                + ", ".join(symlinks)
            )

        state = "PASS" if self.failure is None else "FAIL"
        self.write(
            f"\nPUBLICATION_GATE_C_{state} "
            f"requirements_passed="
            f"{sum(row['state'] == 'PASS' for row in self.requirements)}/10"
        )
        self.log.close()
        report = {
            "schema": SCHEMA,
            "state": state,
            "canonical": not self.development,
            "repository_commit":
                self.environment.get("repository_commit"),
            "started_utc": self.started,
            "finished_utc": utc_now(),
            "environment": self.environment,
            "requirements": self.requirements,
            "commands": self.commands,
            "failure": self.failure,
            "log_path": self.log_path.name,
            "log_sha256": sha256(self.log_path),
        }
        report_path = self.output / "gate_c_report.json"
        exclusive_text(
            report_path,
            json.dumps(report, indent=2, sort_keys=True) + "\n",
        )

        files = []
        for path in sorted(
            item
            for item in self.output.rglob("*")
            if not item.is_symlink() and item.is_file()
        ):
            if path.name == "gate_c_inventory.json":
                continue
            files.append(
                {
                    "path": path.relative_to(self.output).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
        inventory_path = self.output / "gate_c_inventory.json"
        exclusive_text(
            inventory_path,
            json.dumps(
                {
                    "schema": INVENTORY_SCHEMA,
                    "state": state,
                    "repository_commit":
                        self.environment.get("repository_commit"),
                    "files": files,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

        for path in sorted(
            self.output.rglob("*"),
            key=lambda item: len(item.parts),
            reverse=True,
        ):
            if path.is_symlink():
                continue
            mode = path.stat().st_mode
            if path.is_dir():
                path.chmod((mode & ~0o222) | stat.S_IXUSR)
            else:
                path.chmod(mode & ~0o222)
        self.output.chmod(0o500)
        print(report_path.read_text(), end="")
        return (0 if state == "PASS" else 1), report_path


def prepare_output(root: Path, output: Path) -> None:
    try:
        relative = output.relative_to(root)
    except ValueError:
        pass
    else:
        ignored = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "check-ignore",
                "-q",
                "--",
                relative.as_posix(),
            ],
            check=False,
        ).returncode == 0
        if (
            not relative.parts
            or relative.parts[0] != "Production"
            or not ignored
        ):
            raise ValueError(
                "Gate-C output inside the checkout is allowed only below "
                "the ignored Production/ campaign tree"
            )
    output.mkdir(mode=0o700, parents=False, exist_ok=False)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the immutable Section-16 Gate-C audit. OUTPUT_DIRECTORY "
            "must not already exist and must be outside the checkout or "
            "below its ignored Production/ campaign tree."
        )
    )
    parser.add_argument("output_directory", type=Path)
    parser.add_argument(
        "--development",
        action="store_true",
        help=(
            "allow a dirty checkout for diagnostic execution; the retained "
            "report is always FAIL and cannot authorize production"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    output = args.output_directory.expanduser().resolve()
    prepare_output(ROOT, output)
    runner = GateCRunner(
        ROOT,
        output,
        development=args.development,
    )
    try:
        runner.execute()
    except BaseException as error:
        runner.failure = f"{type(error).__name__}: {error}"
        runner.write("\nGATE_C_FAILURE_TRACEBACK")
        runner.write(traceback.format_exc())
    status, _ = runner.finish()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
