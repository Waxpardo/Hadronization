#!/usr/bin/env python3
"""Run the immutable publication Gate-A validation suite.

The output directory is write-once.  Every command, version, result, and
checksum is captured before the directory is made read-only.  A failed run is
also retained as evidence and can never be mistaken for a PASS receipt.
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
import tempfile
import traceback
from pathlib import Path
from typing import Sequence


SCHEMA = "hf_publication_gate_a_report_v1"
ROOT = Path(__file__).resolve().parents[1]

ACTIVE_ROOT_MACROS = (
    "AnalysisScripts/status_analysis_THnSparse_qq.C",
    "AnalysisScripts/MergeAnalysisObjects.C",
    "AnalysisScripts/MergeCanonicalAnalysis.C",
    "Validation/ValidateRawOutput.C",
    "Validation/ValidateCanonicalRawManifest.C",
    "Validation/ValidatePairDirectory.C",
    "Validation/ValidatePairBlockClosure.C",
    "Validation/AuditSpeciesRegistry.C",
    "Validation/AuditTuneSettings.C",
    "Validation/AuditOriginResolution.C",
    "Validation/ListUnresolvedOrigins.C",
    "Validation/PTHatSensitivity.C",
    "Validation/ValidateGateDPilotAnalysis.C",
    "PlottingScripts/improvedPlotting_THnSparse.C",
    "PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C",
    "PlottingScripts/Plot_KinematicSpectra_THnSparse.C",
    "PlottingScripts/Plot_MultiplicityDistribution_PercentileBoundaries.C",
)

ROOT_TESTS = (
    ("Validation/TestHardCarrierUniqueness.C", "TestHardCarrierUniqueness()"),
    ("Validation/TestInclusiveRawKinematics.C", "TestInclusiveRawKinematics()"),
    ("Validation/TestPlotProjectionCuts.C", "TestPlotProjectionCuts()"),
    (
        "Validation/TestPlotReferenceMultiplicityContracts.C",
        "TestPlotReferenceMultiplicityContracts()",
    ),
)


class PhysicsReviewRequired(RuntimeError):
    """A technical check passed but an unresolved physics decision remains."""


def validate_species_pdg_report(path: Path, review_required: bool) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(
            "official-PDG species audit did not create its JSON report"
        )
    try:
        report = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(
            "official-PDG species audit report is not valid JSON"
        ) from error
    expected_state = "NEEDS_PHYSICS_REVIEW" if review_required else "PASS"
    expected_pass = not review_required
    if (
        report.get("schema") != "hf_species_registry_pdg_audit_v1"
        or report.get("state") != expected_state
        or report.get("publication_gate_a_pass") is not expected_pass
        or report.get("physics_review_required") is not review_required
        or report.get("owner_signoff_present") is not False
        or report.get("owner_signoff_authored_or_inferred") is not False
        or report.get("technical_failures") != []
    ):
        raise RuntimeError(
            "official-PDG command lacks an exact "
            f"{expected_state} report"
        )


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="seconds"
    )


def git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *arguments], text=True
    ).strip()


class GateRunner:
    def __init__(self, output: Path, development: bool) -> None:
        self.output = output
        self.development = development
        self.log_path = output / "gate_a.log"
        self.log = self.log_path.open("w", buffering=1)
        self.commands: list[dict[str, object]] = []
        self.failure: str | None = None
        self.physics_review_required: str | None = None
        self.environment: dict[str, str] = {}
        self.started = utc_now()
        self.build = output / "build"
        self.build.mkdir(mode=0o700)
        self.pycache = self.build / "pycache"
        self.pycache.mkdir(mode=0o700)

    def write(self, text: str) -> None:
        self.log.write(text)
        if not text.endswith("\n"):
            self.log.write("\n")
        self.log.flush()
        print(text, flush=True)

    def run(
        self,
        name: str,
        arguments: Sequence[str],
        *,
        cwd: Path = ROOT,
        forbid_compiler_warning: bool = False,
        extra_environment: dict[str, str] | None = None,
        review_returncode: int | None = None,
    ) -> str:
        command = [str(argument) for argument in arguments]
        self.write(f"\nGATE_A_COMMAND_START name={name}")
        self.write(f"cwd={cwd}")
        self.write("command=" + shlex.join(command))
        environment = os.environ.copy()
        environment["PYTHONPYCACHEPREFIX"] = str(self.pycache)
        if extra_environment:
            environment.update(extra_environment)
        started = utc_now()
        result = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        output = result.stdout or ""
        self.log.write(output)
        self.log.flush()
        if output:
            print(output, end="" if output.endswith("\n") else "\n", flush=True)
        warning_found = forbid_compiler_warning and "warning:" in output.lower()
        record = {
            "name": name,
            "started_utc": started,
            "finished_utc": utc_now(),
            "cwd": str(cwd),
            "command": command,
            "returncode": result.returncode,
            "compiler_warning_found": warning_found,
        }
        self.commands.append(record)
        self.write(
            "GATE_A_COMMAND_END "
            f"name={name} returncode={result.returncode} "
            f"compiler_warning_found={str(warning_found).lower()}"
        )
        if (
            review_returncode is not None
            and result.returncode == review_returncode
        ):
            raise PhysicsReviewRequired(
                f"Gate-A command {name} requires physics review"
            )
        if result.returncode != 0:
            raise RuntimeError(
                f"Gate-A command {name} returned {result.returncode}"
            )
        if warning_found:
            raise RuntimeError(
                f"Gate-A command {name} emitted a compiler warning"
            )
        return output.strip()

    def root_compile(self, relative: str, index: int) -> None:
        macro = ROOT / relative
        build = self.build / f"aclic_{index:02d}"
        build.mkdir(mode=0o700)
        expression = (
            f'gSystem->SetBuildDir("{build}", kTRUE); '
            f'int loadStatus = gROOT->LoadMacro("{macro}+"); '
            "gSystem->Exit(loadStatus < 0 ? 1 : 0);"
        )
        self.run(
            f"aclic:{relative}",
            ["root", "-l", "-b", "-q", "-e", expression],
            forbid_compiler_warning=True,
        )

    def root_test(self, relative: str, invocation: str, index: int) -> None:
        macro = ROOT / relative
        build = self.build / f"root_test_{index:02d}"
        build.mkdir(mode=0o700)
        expression = (
            f'gSystem->SetBuildDir("{build}", kTRUE); '
            f'int loadStatus = gROOT->LoadMacro("{macro}+"); '
            "if (loadStatus < 0) { gSystem->Exit(100); } "
            f"Long_t testStatus = gROOT->ProcessLine(\"{invocation}\"); "
            "gSystem->Exit(static_cast<int>(testStatus));"
        )
        self.run(
            f"root-test:{relative}",
            ["root", "-l", "-b", "-q", "-e", expression],
            forbid_compiler_warning=True,
        )

    def execute(self) -> None:
        commit = git("rev-parse", "HEAD")
        branch = git("branch", "--show-current")
        origin = git("remote", "get-url", "origin")
        status = git("status", "--porcelain=v1", "--untracked-files=all")
        tracked_status = git(
            "status", "--porcelain=v1", "--untracked-files=no"
        )
        ignored_sensitive = {
            item
            for item in git(
                "ls-files",
                "--others",
                "--ignored",
                "--exclude-standard",
                "SimulationScripts",
                "tools",
                "Validation",
                "AnalysisScripts",
                "config",
            ).splitlines()
            if item
        }
        allowed_ignored = {
            "SimulationScripts/heavyflavourcorrelations_status"
        }
        unexpected_ignored = ignored_sensitive - allowed_ignored
        self.environment = {
            "repository_root": str(ROOT),
            "repository_commit": commit,
            "branch": branch,
            "origin": origin,
            "development_mode": str(self.development).lower(),
            "initial_status": status,
            "initial_tracked_status": tracked_status,
            "initial_ignored_sensitive_paths": sorted(ignored_sensitive),
        }
        if not self.development and status:
            raise RuntimeError(
                "canonical Gate A requires a completely clean checkout"
            )
        if not self.development and unexpected_ignored:
            raise RuntimeError(
                "canonical Gate A found unauthorized ignored files in "
                "production-sensitive paths: "
                + ", ".join(sorted(unexpected_ignored))
            )

        for executable, version_args in (
            ("python3", ("--version",)),
            ("git", ("--version",)),
            ("root", ("--version",)),
            ("root-config", ("--version",)),
            ("g++", ("--version",)),
            ("jq", ("--version",)),
        ):
            self.run(
                f"version:{executable}", [executable, *version_args]
            )
        self.run("git-diff-check", ["git", "diff", "--check"])
        self.run("origin-fetch", ["git", "fetch", "--prune", "origin"])
        containing_refs = self.run(
            "origin-reachability",
            ["git", "branch", "-r", "--contains", commit],
        )
        origin_refs = sorted(
            line.strip()
            for line in containing_refs.splitlines()
            if line.strip().startswith("origin/")
            and " -> " not in line
        )
        if not origin_refs:
            raise RuntimeError(
                "Gate-A commit is not reachable from any fetched origin ref"
            )
        self.environment["origin_refs_containing_commit"] = origin_refs
        self.run(
            "branch-diff-check",
            ["git", "diff", "--check", "origin/main...HEAD"],
        )
        self.run(
            "registry-generation-check",
            [
                sys.executable,
                "tools/generate_registry_artifacts.py",
                "--check",
            ],
        )
        self.run(
            "tune-card-allowlist-check",
            [sys.executable, "tools/validate_tune_cards.py", "--root", str(ROOT)],
        )

        json_paths = [
            item for item in git("ls-files", "*.json").splitlines() if item
        ]
        self.run("json-syntax", ["jq", "empty", *json_paths])
        shell_paths = [
            item for item in git("ls-files", "*.sh").splitlines() if item
        ]
        self.run("shell-syntax", ["bash", "-n", *shell_paths])
        python_paths = [
            item for item in git("ls-files", "*.py").splitlines() if item
        ]
        self.run(
            "python-bytecode",
            [sys.executable, "-m", "py_compile", *python_paths],
        )

        producer = self.build / "heavyflavourcorrelations_status"
        self.run(
            "producer-build",
            [
                "make",
                "-B",
                "-C",
                "SimulationScripts",
                f"PRODUCER_OUTPUT={producer}",
                "heavyflavourcorrelations_status",
            ],
            forbid_compiler_warning=True,
        )
        if not producer.is_file() or not os.access(producer, os.X_OK):
            raise RuntimeError("producer build did not create an executable")
        self.environment["producer_executable_sha256"] = sha256(producer)
        canonical_producer = (
            ROOT / "SimulationScripts/heavyflavourcorrelations_status"
        )
        if (
            canonical_producer.is_symlink()
            or not canonical_producer.is_file()
            or not os.access(canonical_producer, os.X_OK)
            or sha256(canonical_producer)
            != self.environment["producer_executable_sha256"]
        ):
            raise RuntimeError(
                "canonical producer does not match the forced clean Gate-A "
                "rebuild; run tools/build_producer.sh before Gate A"
            )

        cpp_test = self.build / "test_heavy_flavour_utils"
        self.run(
            "heavy-flavour-utils-build",
            [
                "g++",
                "-std=c++17",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Wconversion",
                "-Wshadow",
                "-Werror",
                "-I",
                "SimulationScripts",
                "tests/test_heavy_flavour_utils.cpp",
                "-o",
                str(cpp_test),
            ],
            forbid_compiler_warning=True,
        )
        self.run("heavy-flavour-utils-test", [str(cpp_test)])

        for test in sorted((ROOT / "tests").glob("test_*.py")):
            self.run(f"python-test:{test.name}", [sys.executable, str(test)])

        for index, macro in enumerate(ACTIVE_ROOT_MACROS):
            self.root_compile(macro, index)
        for index, (macro, invocation) in enumerate(ROOT_TESTS):
            self.root_test(macro, invocation, index)

        species_csv = self.output / "species_registry_pythia_audit.csv"
        species_build = self.build / "species_audit"
        species_build.mkdir(mode=0o700)
        species_macro = ROOT / "Validation/AuditSpeciesRegistry.C"
        species_expression = (
            f'gSystem->SetBuildDir("{species_build}", kTRUE); '
            f'int loadStatus = gROOT->LoadMacro("{species_macro}+"); '
            "if (loadStatus < 0) { gSystem->Exit(100); } "
            "Long_t auditStatus = gROOT->ProcessLine("
            f'"AuditSpeciesRegistry(\\"{species_csv}\\")"); '
            "gSystem->Exit(static_cast<int>(auditStatus));"
        )
        self.run(
            "species-registry-pythia-audit",
            ["root", "-l", "-b", "-q", "-e", species_expression],
            forbid_compiler_warning=True,
        )
        if not species_csv.is_file() or species_csv.stat().st_size == 0:
            raise RuntimeError("species registry audit did not create its CSV")

        catalog = ROOT / "REPOSITORY_FILE_CATALOG.md"
        if catalog.is_file() and "REPOSITORY_FILE_CATALOG.md" in git(
            "ls-files", "REPOSITORY_FILE_CATALOG.md"
        ).splitlines():
            self.run(
                "repository-file-catalog-check",
                [
                    sys.executable,
                    "tools/generate_file_catalog.py",
                    "--root",
                    str(ROOT),
                    "--check",
                ],
            )

        final_tracked_status = git(
            "status", "--porcelain=v1", "--untracked-files=no"
        )
        if final_tracked_status != tracked_status:
            raise RuntimeError(
                "Gate A changed tracked checkout state while validating"
            )

        # This is the final deliberate gate.  A review-blocked report therefore
        # proves that every mechanical build, test, catalog, and checkout-state
        # check above completed first.
        species_pdg_report = self.output / "species_registry_pdg_audit.json"
        review_required: PhysicsReviewRequired | None = None
        try:
            self.run(
                "species-registry-official-pdg-audit",
                [
                    sys.executable,
                    "tools/pdg_2025_species_audit.py",
                    "check",
                    "--pythia-csv",
                    str(species_csv),
                    "--require-pythia",
                    "--output",
                    str(species_pdg_report),
                ],
                review_returncode=2,
            )
        except PhysicsReviewRequired as error:
            review_required = error
        validate_species_pdg_report(
            species_pdg_report, review_required is not None
        )
        if review_required is not None:
            raise review_required

    def finish(self) -> int:
        symlinks = [
            path.relative_to(self.output).as_posix()
            for path in self.output.rglob("*")
            if path.is_symlink()
        ]
        if symlinks and self.failure is None:
            self.failure = (
                "Gate-A evidence contains symbolic links: "
                + ", ".join(sorted(symlinks))
            )
        state = (
            "FAIL"
            if self.failure is not None
            else "NEEDS_PHYSICS_REVIEW"
            if self.physics_review_required is not None
            else "PASS"
        )
        self.write(
            f"\nPUBLICATION_GATE_A_{state} commands={len(self.commands)}"
        )
        self.log.close()
        report = {
            "schema": SCHEMA,
            "state": state,
            "canonical": not self.development,
            "started_utc": self.started,
            "finished_utc": utc_now(),
            "environment": self.environment,
            "commands": self.commands,
            "failure": self.failure,
            "physics_review_required": self.physics_review_required,
            "publication_gate_a_pass": state == "PASS",
            "log_path": self.log_path.name,
            "log_sha256": sha256(self.log_path),
        }
        report_path = self.output / "gate_a_report.json"
        report_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        inventory = []
        for path in sorted(
            item
            for item in self.output.rglob("*")
            if not item.is_symlink() and item.is_file()
        ):
            if path.name == "gate_a_inventory.json":
                continue
            inventory.append(
                {
                    "path": path.relative_to(self.output).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
        inventory_path = self.output / "gate_a_inventory.json"
        inventory_path.write_text(
            json.dumps(
                {
                    "schema": "hf_publication_gate_a_inventory_v1",
                    "state": state,
                    "files": inventory,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        for path in sorted(
            self.output.rglob("*"), key=lambda item: len(item.parts), reverse=True
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
        return {"PASS": 0, "FAIL": 1, "NEEDS_PHYSICS_REVIEW": 2}[state]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run immutable Gate A. OUTPUT_DIRECTORY must not already exist "
            "and must be outside the checkout or below its ignored "
            "Production/ campaign tree."
        )
    )
    parser.add_argument("output_directory", type=Path)
    parser.add_argument(
        "--development",
        action="store_true",
        help=(
            "allow a dirty checkout for iterative diagnostics; the report is "
            "permanently marked noncanonical and cannot authorize production"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    output = args.output_directory.expanduser().resolve()
    try:
        relative_output = output.relative_to(ROOT)
    except ValueError:
        pass
    else:
        ignored = subprocess.run(
            ["git", "-C", str(ROOT), "check-ignore", "-q", "--",
             relative_output.as_posix()],
            check=False,
        ).returncode == 0
        if (
            not relative_output.parts
            or relative_output.parts[0] != "Production"
            or not ignored
        ):
            raise ValueError(
                "Gate-A output inside the checkout is allowed only below the "
                "ignored Production/ campaign tree"
            )
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    runner = GateRunner(output, args.development)
    try:
        runner.execute()
    except PhysicsReviewRequired as error:
        runner.physics_review_required = str(error)
        runner.write(
            "\nGATE_A_NEEDS_PHYSICS_REVIEW "
            f"{runner.physics_review_required}"
        )
    except BaseException as error:
        runner.failure = f"{type(error).__name__}: {error}"
        runner.write("\nGATE_A_FAILURE_TRACEBACK")
        runner.write(traceback.format_exc())
    return runner.finish()


if __name__ == "__main__":
    raise SystemExit(main())
