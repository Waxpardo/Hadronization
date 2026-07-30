#!/usr/bin/env python3
"""Regression tests for sealed full-production submission provenance."""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from test_gate_b_submission_contract import prepare_checkout, run


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools/campaign_manifest.py"
RENDERER = ROOT / "tools/render_production_submit.py"
sys.path.insert(0, str(ROOT / "tools"))
import campaign_manifest as contract  # noqa: E402


def unresolved_fixture(count: int = 0) -> dict[str, dict[str, int]]:
    return {
        f"{tune}:{threshold}": {"charm": count, "beauty": 0}
        for tune in ("MONASH", "JUNCTIONS", "CLOSEPACKING")
        for threshold in ("0.5", "1.0", "2.0")
    }


def passing_pthat_comparisons() -> list[dict]:
    return [
        {
            "tune": tune,
            "alternate_threshold": alternate,
            "reference_threshold": "1.0",
            "observable": f"synthetic_observable_{index:02d}",
            "family_comparisons": 192,
            "status": "EQUIVALENT_NO_RESOLVED_SHIFT",
        }
        for tune in ("MONASH", "JUNCTIONS", "CLOSEPACKING")
        for alternate in ("0.5", "2.0")
        for index in range(32)
    ]


def pthat_diagnostics(
    samples: dict[str, dict[str, int]]
) -> list[dict]:
    return [
        {
            "identity": {
                "tune": identity.split(":", 1)[0],
                "pthat_min": identity.split(":", 1)[1],
            },
            "unresolved_trigger_candidates":
                sectors["charm"] + sectors["beauty"],
        }
        for identity, sectors in sorted(samples.items())
    ]


def passing_storage_projection(
    probe_paths: list[Path], device_id: int
) -> dict:
    gib = 1024**3
    candidate_raw = 100_000_000
    canonical_analysis = 100_000_000
    merged = 100_000_000
    blocks = 100_000_000
    plot_evidence = 10 * gib
    raw_required = 2 * candidate_raw
    analysis_required = (
        canonical_analysis + merged + blocks + plot_evidence
    )
    total = raw_required + analysis_required
    capacity = 10 * 1024**4
    available = 8 * 1024**4
    maximum = int(available * 0.70)
    minimum_remaining = max(int(capacity * 0.05), 500 * gib)
    projected = available - total
    checked = datetime.now(timezone.utc).isoformat(timespec="seconds")
    fragment = 4096
    capacity_check = {
        "checked_utc": checked,
        "capacity_source": "os.statvfs f_bavail",
        "state": "PASS",
        "filesystems": [
            {
                "device_id": device_id,
                "probe_paths": [str(path) for path in probe_paths],
                "statvfs_frsize": fragment,
                "statvfs_blocks": capacity // fragment,
                "statvfs_bavail": available // fragment,
                "capacity_bytes": capacity,
                "available_bytes": available,
                "required_additional_bytes": total,
                "maximum_allowed_from_current_available_bytes": maximum,
                "minimum_required_remaining_bytes": minimum_remaining,
                "projected_remaining_bytes": projected,
                "state": "PASS",
                "failure_reasons": [],
                "roles": [
                    "analysis_and_publication_outputs",
                    "candidate_raw_and_partials",
                ],
            }
        ],
    }
    return {
        "schema": "hf_gate_d_storage_projection_v1",
        "state": "PASS",
        "gate_e_storage_authorized": True,
        "projected_components": {
            "full_100_200_200_candidate_raw_bytes": candidate_raw,
            "simultaneous_partial_raw_bytes": candidate_raw,
            "canonical_300_job_per_job_analysis_bytes":
                canonical_analysis,
            "final_merged_central_bytes": merged,
            "final_ten_block_bytes": blocks,
            "full_plots_logs_validation_evidence_bytes": plot_evidence,
            "raw_filesystem_required_additional_bytes": raw_required,
            "analysis_filesystem_required_additional_bytes":
                analysis_required,
            "total_required_additional_bytes": total,
        },
        "capacity_policy": {
            "maximum_fraction_of_current_available": 0.70,
            "minimum_projected_free_fraction": 0.05,
            "minimum_projected_free_bytes": 500 * gib,
            "simultaneous_partial_raw_multiplier": 1,
            "full_plot_scale_factor": 10,
            "minimum_full_plot_and_evidence_bytes": 10 * gib,
        },
        "preparation_capacity_check": capacity_check,
        "final_capacity_recheck": capacity_check,
    }


def overwrite_sealed(path: Path, content: bytes) -> None:
    path.chmod(0o644)
    path.write_bytes(content)
    path.chmod(0o444)


def write_submission_classads(
    output: Path,
    claim_path: Path,
    checkout: Path,
    cluster_id: int,
    *,
    corrupt_process: int | None = None,
) -> None:
    checkout = checkout.resolve()
    claim = json.loads(claim_path.read_text())
    allocations = claim.get("allocations")
    if allocations is None:
        allocations = [claim["allocation"]]
    rows = []
    for process_id, allocation in enumerate(allocations):
        row = {
            "ClusterId": cluster_id,
            "ProcId": process_id,
            "JobStatus": 5,
            "Cmd": str(checkout / "runCondorJob.sh"),
            "Iwd": str(checkout),
            "Args": contract._expected_condor_args(
                allocation, cluster_id, process_id, claim["campaign"]
            ),
            "HFCampaign": claim["campaign"],
            "HFCampaignOrdinal": allocation["campaign_ordinal"],
            "HFTune": allocation["tune"],
            "HFLogicalId": allocation["logical_id"],
            "HFRole": allocation["role"],
            "HFAttempt": allocation["attempt"],
            "HFSeed": allocation["seed"],
            "HFRequestedSuccesses": allocation["requested_successes"],
            "HFPTHat": allocation["pthat_min_override"],
            "HFMultiplicityAuditEvents":
                allocation["multiplicity_audit_events"],
            "HFRepositoryCommit": allocation["repository_commit"],
            "HFEffectiveCardSHA256":
                allocation["effective_card_sha256"],
            "HFProducerExecutableSHA256":
                allocation["producer_executable_sha256"],
        }
        if corrupt_process == process_id:
            row["HFSeed"] += 1
        rows.append(row)
    output.write_text(json.dumps(rows, sort_keys=True) + "\n")


def write_signoff(
    campaign_dir: Path, gate_b_report: dict[str, str]
) -> Path:
    config = json.loads((campaign_dir / "campaign.json").read_text())
    checkout = campaign_dir.parents[1].resolve()
    gate_b_payload = json.loads(
        (checkout / gate_b_report["path"]).read_text()
    )
    path = campaign_dir / "PHYSICS_ORIGIN_SIGNOFF.json"
    path.write_text(
        json.dumps(
            {
                "schema": "hf_full_production_origin_signoff_v1",
                "decision": "APPROVE_FULL_PRODUCTION",
                "approved": True,
                "reviewer": "Synthetic Fixture Approver",
                "reviewer_role": "project_owner",
                "decision_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "finding": "Synthetic fixture approval for workflow testing only",
                "allowed_unresolved_treatment":
                    "No unresolved trigger candidates were observed; no "
                    "special treatment is required.",
                "campaign": config["campaign"],
                "campaign_ordinal": config["campaign_ordinal"],
                "repository_commit": config["repository_commit"],
                "gate_b_report_path": gate_b_report["path"],
                "gate_b_report_sha256": gate_b_report["sha256"],
                "gate_b_campaign": gate_b_payload["campaign"],
                "gate_b_campaign_ordinal":
                    gate_b_payload["campaign_ordinal"],
                "reviewed_unresolved_trigger_candidates":
                    unresolved_fixture(),
                "reviewed_unresolved_trigger_candidates_total": 0,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    path.chmod(0o444)
    return path


def write_gate_reports(campaign_dir: Path) -> dict[str, dict[str, str]]:
    campaign_dir = campaign_dir.resolve()
    config = json.loads((campaign_dir / "campaign.json").read_text())
    checkout = campaign_dir.parents[1].resolve()
    reports: dict[str, dict[str, str]] = {}
    report_dir = campaign_dir / "gate_reports"
    report_dir.mkdir()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    producer_sha = hashlib.sha256(
        (
            checkout
            / "SimulationScripts/heavyflavourcorrelations_status"
        ).read_bytes()
    ).hexdigest()

    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def seal_evidence(
        evidence_dir: Path,
        inventory_name: str,
        inventory_schema: str,
        *,
        state: str | None = None,
        commit: str | None = None,
    ) -> None:
        inventory = []
        for path in sorted(
            candidate
            for candidate in evidence_dir.rglob("*")
            if candidate.is_file()
        ):
            inventory.append(
                {
                    "path": path.relative_to(evidence_dir).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": digest(path),
                }
            )
        payload: dict[str, object] = {
            "schema": inventory_schema,
            "files": inventory,
        }
        if state is not None:
            payload["state"] = state
        if commit is not None:
            payload["repository_commit"] = commit
        inventory_path = evidence_dir / inventory_name
        inventory_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )
        for path in sorted(
            evidence_dir.rglob("*"),
            key=lambda candidate: len(candidate.parts),
            reverse=True,
        ):
            if path.is_file():
                path.chmod(0o444)
            elif path.is_dir():
                path.chmod(0o500)
        evidence_dir.chmod(0o500)

    pthat_report = report_dir / "pthat_sensitivity.json"
    pthat_report.write_text(
        json.dumps(
            {
                "schema": "hf_gate_b_pthat_sensitivity_report_v1",
                "outcome": "PASS",
                "repository_commit": config["repository_commit"],
                "spec_sha256": config["pthat_sensitivity_spec_sha256"],
                "technical_failures": [],
                "scientific_review_findings": [],
                "inconclusive_findings": [],
                "comparisons": passing_pthat_comparisons(),
                "diagnostics": pthat_diagnostics(unresolved_fixture()),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    pthat_report.chmod(0o444)
    reports["pthat_sensitivity"] = {
        "path": str(pthat_report.relative_to(checkout)),
        "sha256": digest(pthat_report),
    }

    gate_a_dir = report_dir / "gate_a"
    gate_a_dir.mkdir()
    gate_a_log = gate_a_dir / "gate_a.log"

    def gate_a_fixture_argv(name: str) -> list[str]:
        python = sys.executable
        if name.startswith("version:"):
            return [name.split(":", 1)[1], "--version"]
        exact = {
            "git-diff-check": ["git", "diff", "--check"],
            "origin-fetch": ["git", "fetch", "--prune", "origin"],
            "origin-reachability": [
                "git", "branch", "-r", "--contains",
                config["repository_commit"],
            ],
            "branch-diff-check": [
                "git", "diff", "--check", "origin/main...HEAD",
            ],
            "registry-generation-check": [
                python, "tools/generate_registry_artifacts.py", "--check",
            ],
            "tune-card-allowlist-check": [
                python, "tools/validate_tune_cards.py", "--root", str(checkout),
            ],
            "producer-build": [
                "make", "-B", "-C", "SimulationScripts",
                "PRODUCER_OUTPUT="
                + str(gate_a_dir / "build/heavyflavourcorrelations_status"),
                "heavyflavourcorrelations_status",
            ],
            "heavy-flavour-utils-build": [
                "g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic",
                "-Wconversion", "-Wshadow", "-Werror", "-I",
                "SimulationScripts", "tests/test_heavy_flavour_utils.cpp",
                "-o", str(gate_a_dir / "build/test_heavy_flavour_utils"),
            ],
            "heavy-flavour-utils-test": [
                str(gate_a_dir / "build/test_heavy_flavour_utils")
            ],
            "repository-file-catalog-check": [
                python, "tools/generate_file_catalog.py", "--root",
                str(checkout), "--check",
            ],
        }
        if name in exact:
            return exact[name]
        if name == "json-syntax":
            return [
                "jq", "empty",
                *contract._gate_a_tracked_paths(
                    checkout, config["repository_commit"], "*.json"
                ),
            ]
        if name == "shell-syntax":
            return [
                "bash", "-n",
                *contract._gate_a_tracked_paths(
                    checkout, config["repository_commit"], "*.sh"
                ),
            ]
        if name == "python-bytecode":
            return [
                python, "-m", "py_compile",
                *contract._gate_a_tracked_paths(
                    checkout, config["repository_commit"], "*.py"
                ),
            ]
        if name.startswith("python-test:"):
            return [
                python,
                str(checkout / "tests" / name.split(":", 1)[1]),
            ]
        if name.startswith(("aclic:", "root-test:")):
            macro = name.split(":", 1)[1]
            expression = (
                f'gSystem->SetBuildDir("{gate_a_dir}/build/aclic", kTRUE); '
                f'int loadStatus = gROOT->LoadMacro("{checkout / macro}+");'
            )
            return ["root", "-l", "-b", "-q", "-e", expression]
        if name == "species-registry-pythia-audit":
            expression = (
                f'gSystem->SetBuildDir("{gate_a_dir}/build/species", kTRUE); '
                "int loadStatus = gROOT->LoadMacro("
                f'"{checkout / "Validation/AuditSpeciesRegistry.C"}+"); '
                "AuditSpeciesRegistry();"
            )
            return ["root", "-l", "-b", "-q", "-e", expression]
        if name == "species-registry-official-pdg-audit":
            return [
                python, "tools/pdg_2025_species_audit.py", "check",
                "--pythia-csv", str(gate_a_dir / "species.csv"),
                "--require-pythia", "--output",
                str(gate_a_dir / "species.json"),
            ]
        raise AssertionError(f"no Gate-A fixture argv for {name}")

    gate_a_commands = []
    gate_a_log_lines = []
    for name in sorted(
        contract._gate_a_expected_command_names(
            checkout, config["repository_commit"]
        )
    ):
        argv = gate_a_fixture_argv(name)
        gate_a_commands.append(
            {
                "name": name,
                "started_utc": now,
                "finished_utc": now,
                "cwd": str(checkout.resolve()),
                "command": argv,
                "returncode": 0,
                "compiler_warning_found": False,
            }
        )
        gate_a_log_lines.extend(
            (
                f"GATE_A_COMMAND_START name={name}",
                f"cwd={checkout.resolve()}",
                "command=" + shlex.join(argv),
                f"GATE_A_COMMAND_END name={name} returncode=0 "
                "compiler_warning_found=false",
            )
        )
    gate_a_log.write_text("\n".join(gate_a_log_lines) + "\n")
    gate_a_report = gate_a_dir / "gate_a_report.json"
    gate_a_report.write_text(
        json.dumps(
            {
                "schema": "hf_publication_gate_a_report_v1",
                "state": "PASS",
                "canonical": True,
                "started_utc": now,
                "finished_utc": now,
                "environment": {
                    "repository_root": str(checkout),
                    "repository_commit": config["repository_commit"],
                    "branch": "main",
                    "origin": "https://github.com/Waxpardo/Hadronization.git",
                    "development_mode": "false",
                    "initial_status": "",
                    "initial_tracked_status": "",
                    "initial_ignored_sensitive_paths": [
                        "SimulationScripts/heavyflavourcorrelations_status"
                    ],
                    "origin_refs_containing_commit": ["origin/main"],
                    "producer_executable_sha256": producer_sha,
                },
                "commands": gate_a_commands,
                "failure": None,
                "physics_review_required": None,
                "publication_gate_a_pass": True,
                "log_path": gate_a_log.name,
                "log_sha256": digest(gate_a_log),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    seal_evidence(
        gate_a_dir,
        "gate_a_inventory.json",
        "hf_publication_gate_a_inventory_v1",
        state="PASS",
    )
    reports["gate_a"] = {
        "path": str(gate_a_report.relative_to(checkout)),
        "sha256": digest(gate_a_report),
    }

    gate_b_campaign_dir = campaign_dir / "gate_b_fixture_campaign"
    gate_b_campaign_dir.mkdir()
    gate_b_campaign_json = gate_b_campaign_dir / "campaign.json"
    gate_b_candidates = gate_b_campaign_dir / "candidate_manifest.jsonl"
    gate_b_ledger = gate_b_campaign_dir / "seed_ledger.jsonl"
    gate_b_name = f"{config['campaign']}_gate_b_fixture"
    gate_b_ordinal = int(config["campaign_ordinal"]) + 1
    gate_b_campaign_json.write_text(
        json.dumps(
            {
                "schema": "hf_gate_b_pilot_campaign_v1",
                "campaign": gate_b_name,
                "campaign_ordinal": gate_b_ordinal,
                "repository_commit": config["repository_commit"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    gate_b_candidates.write_text("fixture\n")
    gate_b_ledger.write_text("fixture\n")
    gate_b_dir = report_dir / "gate_b"
    gate_b_dir.mkdir()
    gate_b_commands = []
    for index, purpose in enumerate(sorted(contract.GATE_B_COMMAND_PURPOSES)):
        command_log = gate_b_dir / f"command_{index:02d}.log"
        command_log.write_text(f"{purpose} exact-shape fixture\n")
        if purpose == "canonical_gate_b_campaign_validation":
            argv = [
                sys.executable,
                str(checkout / "tools/campaign_manifest.py"),
                "validate",
                str(gate_b_campaign_dir),
                "--implementation-policy",
                "exact",
                "--checkout-root",
                str(checkout),
            ]
        elif purpose == "fresh_raw_to_frozen_pthat_decision_recheck":
            argv = [
                sys.executable,
                str(checkout / "tools/evaluate_pthat_sensitivity.py"),
                str(gate_b_campaign_dir),
                str(checkout / "Production" / gate_b_name),
                str(gate_b_dir / "pthat_recheck"),
                "--checkout-root",
                str(checkout),
            ]
        elif purpose == "raw_resource_stability_compression_audit":
            argv = [
                "root", "-l", "-b", "-q",
                str(gate_b_dir / "gate_b_resource_audit.C"),
            ]
        else:
            argv = ["root", "-l", "-b"]
        stdin_path = None
        if argv == ["root", "-l", "-b"]:
            stdin_path = gate_b_dir / f"command_{index:02d}.stdin.C"
            stdin_path.write_text(f"// {purpose} fixture\n")
        gate_b_commands.append(
            {
                "purpose": purpose,
                "argv": argv,
                "started_utc": now,
                "ended_utc": now,
                "returncode": 0,
                "log_path": command_log.name,
                "log_sha256": digest(command_log),
                "compiler_warning_found": False,
                **(
                    {
                        "stdin_path": stdin_path.name,
                        "stdin_sha256": digest(stdin_path),
                    }
                    if stdin_path is not None
                    else {}
                ),
            }
        )
    gate_b_log = gate_b_dir / "gate_b.log"
    gate_b_log.write_text("synthetic exact-shape Gate-B contract fixture\n")
    profiles = {
        logical_id: profile
        for logical_id, profile in contract.GATE_B_PROFILES.items()
    }
    raw_rows = []
    resource_rows = []
    for tune in contract.TUNES:
        for logical_id, profile in sorted(profiles.items()):
            raw_rows.append(
                {
                    "tune": tune,
                    "logical_id": logical_id,
                    "purpose": profile[3],
                    "pthat_min": profile[0],
                    "requested_successes": profile[1],
                    "raw_sha256": "1" * 64,
                }
            )
            resource_rows.append(
                {
                    "tune": tune,
                    "logical_id": logical_id,
                    "purpose": profile[3],
                    "successful_events": profile[1],
                }
            )
    gate_b_report = gate_b_dir / "gate_b_report.json"
    gate_b_report.write_text(
        json.dumps(
            {
                "schema": "hf_publication_gate_b_report_v1",
                "state": "PASS",
                "canonical": True,
                "failure": None,
                "repository_commit": config["repository_commit"],
                "campaign": gate_b_name,
                "campaign_ordinal": gate_b_ordinal,
                "created_utc": now,
                "commands": gate_b_commands,
                "campaign_manifest": {
                    "path": str(gate_b_campaign_json.relative_to(checkout)),
                    "sha256": digest(gate_b_campaign_json),
                    "candidate_manifest_path": str(
                        gate_b_candidates.relative_to(checkout)
                    ),
                    "candidate_manifest_sha256": digest(gate_b_candidates),
                    "seed_ledger_path": str(gate_b_ledger.relative_to(checkout)),
                    "seed_ledger_sha256": digest(gate_b_ledger),
                    "jobs": 9,
                    "central_successes_per_tune": 1_000_000,
                    "pthat_thresholds": ["0.5", "1.0", "2.0"],
                },
                "submission_evidence": {
                    "producer_executable_sha256": producer_sha
                },
                "raw_validation_evidence": raw_rows,
                "raw_validation_count": 9,
                "resource_metadata_evidence": resource_rows,
                "unresolved_trigger_candidates": {
                    "all_samples_by_tune_threshold_and_sector":
                        unresolved_fixture(),
                    "all_nine_samples_total": 0,
                },
                "pthat_sensitivity": {
                    "schema": "hf_gate_b_pthat_sensitivity_report_v1",
                    "outcome": "PASS",
                    "sha256": reports["pthat_sensitivity"]["sha256"],
                    "blocking_reasons": [],
                },
                "log_path": gate_b_log.name,
                "log_sha256": digest(gate_b_log),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    seal_evidence(
        gate_b_dir,
        "evidence_inventory.json",
        "hf_publication_gate_b_evidence_inventory_v1",
    )
    reports["gate_b"] = {
        "path": str(gate_b_report.relative_to(checkout)),
        "sha256": digest(gate_b_report),
    }

    gate_c_dir = report_dir / "gate_c"
    gate_c_dir.mkdir()
    gate_c_commands = []
    gate_c_specs = contract._gate_c_expected_specs(checkout)
    for index, (name, specification) in enumerate(gate_c_specs.items()):
        command_log_dir = gate_c_dir / "command_logs"
        command_log_dir.mkdir(exist_ok=True)
        command_log = command_log_dir / f"{index:02d}_{name}.log"
        command_log.write_text(f"{name} exact-shape fixture\n")
        command = list(specification["command"])
        if command[0] == "<PYTHON_EXECUTABLE>":
            command[0] = sys.executable
        gate_c_commands.append(
            {
                "name": name,
                "started_utc": now,
                "finished_utc": now,
                "cwd": str(checkout.resolve()),
                "command": command,
                "returncode": 0,
                "process_returncode": 0,
                "compiler_warning_found": False,
                "input_sha256": {
                    relative: contract.git_file_sha256(
                        checkout,
                        config["repository_commit"],
                        relative,
                    )
                    for relative in specification["inputs"]
                },
                "required_markers": specification["markers"],
                "missing_markers": [],
                "log_path": command_log.relative_to(gate_c_dir).as_posix(),
                "log_bytes": command_log.stat().st_size,
                "log_sha256": digest(command_log),
            }
        )
    gate_c_log = gate_c_dir / "gate_c.log"
    gate_c_log.write_text("synthetic exact-shape Gate-C contract fixture\n")
    gate_c_report = gate_c_dir / "gate_c_report.json"
    gate_c_report.write_text(
        json.dumps(
            {
                "schema": "hf_publication_gate_c_report_v1",
                "state": "PASS",
                "canonical": True,
                "repository_commit": config["repository_commit"],
                "started_utc": now,
                "finished_utc": now,
                "environment": {
                    "repository_commit": config["repository_commit"],
                    "final_repository_commit": config["repository_commit"],
                    "canonical": True,
                    "initial_status": "",
                    "initial_tracked_status": "",
                    "final_status": "",
                    "final_tracked_status": "",
                },
                "requirements": [
                    {
                        "number": number,
                        "title": f"fixture requirement {number}",
                        "state": "PASS",
                        "evidenced_claims": ["exact-shape fixture"],
                        "missing_evidence": [],
                        "commands": [],
                    }
                    for number in range(1, 11)
                ],
                "commands": gate_c_commands,
                "failure": None,
                "log_path": gate_c_log.name,
                "log_sha256": digest(gate_c_log),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    seal_evidence(
        gate_c_dir,
        "gate_c_inventory.json",
        "hf_publication_gate_c_inventory_v1",
        state="PASS",
        commit=config["repository_commit"],
    )
    reports["gate_c"] = {
        "path": str(gate_c_report.relative_to(checkout)),
        "sha256": digest(gate_c_report),
    }

    gate_d_dir = report_dir / "gate_d"
    gate_d_dir.mkdir()
    gate_d_command_logs = gate_d_dir / "command_logs"
    gate_d_command_logs.mkdir()
    gate_d_commands = []
    for tune in contract.TUNES:
        for index in range(0, 11):
            label = "central" if index == 0 else f"block_{index:02d}"
            name = f"pair_contract_{tune}_{label}"
            command_log = gate_d_command_logs / f"{name}.log"
            command_log.write_text(
                "PAIR_DIRECTORY_SUMMARY errors=0 files=300\n"
            )
            directory = (
                gate_d_dir / f"complete_root_GATE_D_{tune}"
                if index == 0
                else gate_d_dir
                / "SUBSAMPLES"
                / f"combined_root_subSamples_{tune}"
                / f"combined_root_{index}"
            )
            gate_d_commands.append(
                {
                    "name": name,
                    "started_utc": now,
                    "finished_utc": now,
                    "cwd": str(checkout.resolve()),
                    "command": [
                        str(
                            checkout
                            / "Validation/validate_pair_directory.sh"
                        ),
                        str(directory),
                    ],
                    "returncode": 0,
                    "compiler_warning_found": False,
                    "log_path": command_log.relative_to(
                        gate_d_dir
                    ).as_posix(),
                    "log_bytes": command_log.stat().st_size,
                    "log_sha256": digest(command_log),
                }
            )
    audit_log = gate_d_command_logs / "gate_d_analysis_audit.log"
    audit_log.write_text(
        "GATE_D_ANALYSIS_SUMMARY errors=0 fixture=true\n"
    )
    gate_d_commands.append(
        {
            "name": "gate_d_analysis_audit",
            "started_utc": now,
            "finished_utc": now,
            "cwd": str(checkout.resolve()),
            "command": ["root", "-l", "-b"],
            "returncode": 0,
            "compiler_warning_found": False,
            "log_path": audit_log.relative_to(gate_d_dir).as_posix(),
            "log_bytes": audit_log.stat().st_size,
            "log_sha256": digest(audit_log),
        }
    )
    gate_d_log = gate_d_dir / "gate_d.log"
    gate_d_log.write_text(
        "\n".join(
            f"COMMAND name={row['name']}\nRETURN_CODE 0"
            for row in gate_d_commands
        )
        + "\nPUBLICATION_GATE_D_PASS requirements=13/13\n"
    )
    gate_d_report = gate_d_dir / "gate_d_report.json"
    storage_campaign_root = (
        checkout / "Production" / config["campaign"]
    )
    storage_campaign_root.mkdir(parents=True, exist_ok=True)
    gate_d_report.write_text(
        json.dumps(
            {
                "schema": "hf_publication_gate_d_report_v1",
                "state": "PASS",
                "canonical": True,
                "repository_commit": config["repository_commit"],
                "commands": gate_d_commands,
                "requirements": [
                    {
                        "number": number,
                        "title": f"fixture requirement {number}",
                        "state": "PASS",
                        "evidence": {"fixture": True},
                        "failure": None,
                    }
                    for number in range(1, 14)
                ],
                "failure": None,
                "log_path": gate_d_log.name,
                "log_sha256": digest(gate_d_log),
                "storage_projection": passing_storage_projection(
                    [checkout.resolve(), storage_campaign_root.resolve()],
                    checkout.stat().st_dev,
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    seal_evidence(
        gate_d_dir,
        "gate_d_inventory.json",
        "hf_publication_gate_d_inventory_v1",
        state="PASS",
        commit=config["repository_commit"],
    )
    reports["gate_d"] = {
        "path": str(gate_d_report.relative_to(checkout)),
        "sha256": digest(gate_d_report),
    }
    return reports


def write_gate_authorization(
    campaign_dir: Path,
    signoff: Path,
    reports: dict[str, dict[str, str]],
) -> Path:
    config = json.loads((campaign_dir / "campaign.json").read_text())
    path = campaign_dir / "FULL_PRODUCTION_GATE_AUTHORIZATION.json"
    path.write_text(
        json.dumps(
            {
                "schema": "hf_full_production_gate_authorization_v1",
                "approved": True,
                "project_owner": "Synthetic Fixture Approver",
                "approved_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "campaign": config["campaign"],
                "campaign_ordinal": config["campaign_ordinal"],
                "repository_commit": config["repository_commit"],
                "physics_origin_signoff_sha256": hashlib.sha256(
                    signoff.read_bytes()
                ).hexdigest(),
                "reports": reports,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    path.chmod(0o444)
    return path


def generate_full(
    checkout: Path, campaign: str, ordinal: int, seed_base: int
) -> Path:
    run(
        sys.executable,
        str(MANIFEST),
        "generate",
        "--root",
        str(checkout),
        "--campaign",
        campaign,
        "--campaign-ordinal",
        str(ordinal),
        "--events",
        "10",
        "--seed-base",
        str(seed_base),
        "--max-attempts",
        "1000",
    )
    return checkout / "campaigns" / campaign


def test_resolved_pthat_authorization_route() -> None:
    with tempfile.TemporaryDirectory(
        prefix="hadronization_pthat_authorization_test_"
    ) as temporary:
        checkout = Path(temporary)
        campaign = "HF_GATEB_resolved_fixture"
        ordinal = 26
        commit = "5" * 40
        samples = unresolved_fixture()
        samples["JUNCTIONS:1.0"]["charm"] = 2
        total = 2
        decision_utc = datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )
        signoff_source = {
            "schema": "hf_gate_b_physics_signoff_v1",
            "approved": True,
            "campaign": campaign,
            "campaign_ordinal": ordinal,
            "repository_commit": commit,
            "gate_b_needs_signoff_report_sha256": "a" * 64,
            "reviewed_unresolved_trigger_candidates": samples,
            "reviewed_unresolved_trigger_candidates_total": total,
            "allowed_unresolved_treatment":
                contract.NONZERO_UNRESOLVED_TREATMENT,
            "reviewer": "Synthetic Physics Approver",
            "reviewer_role": "project owner",
            "decision_utc": decision_utc,
            "finding": (
                "Synthetic nonzero-origin approval used only to exercise "
                "the fail-closed authorization contract."
            ),
            "supersedes_state": "NEEDS_SIGNOFF",
        }
        signoff_path = (
            checkout
            / "campaigns"
            / campaign
            / "GATE_B_PHYSICS_SIGNOFF.json"
        )
        signoff_path.parent.mkdir(parents=True)
        signoff_path.write_text(
            json.dumps(signoff_source, indent=2, sort_keys=True) + "\n"
        )
        signoff_path.chmod(0o444)
        signoff_sha = hashlib.sha256(signoff_path.read_bytes()).hexdigest()
        pthat_sha = "b" * 64
        pthat = {
            "outcome": "SCIENTIFIC_REVIEW_REQUIRED",
            "technical_failures": [],
            "inconclusive_findings": [],
            "scientific_review_findings": [
                "('JUNCTIONS', '1.0') has 2 unresolved "
                "publication-trigger candidates"
            ],
            "diagnostics": pthat_diagnostics(samples),
            "comparisons": passing_pthat_comparisons(),
        }
        gate_b = {
            "campaign": campaign,
            "campaign_ordinal": ordinal,
            "repository_commit": commit,
            "resolution_kind":
                "owner_physics_signoff_supersession_v1",
            "supersedes": {
                "state": "NEEDS_SIGNOFF",
                "sha256": "a" * 64,
            },
            "unresolved_trigger_candidates": {
                "all_samples_by_tune_threshold_and_sector": samples,
                "all_nine_samples_total": total,
            },
            "pthat_sensitivity": {
                "schema": "hf_gate_b_pthat_sensitivity_report_v1",
                "sha256": pthat_sha,
                "outcome": "SCIENTIFIC_REVIEW_REQUIRED",
                "blocking_reasons": [],
            },
            "gate_b_physics_signoff": {
                "path": str(signoff_path.relative_to(checkout)),
                "sha256": signoff_sha,
                "schema": "hf_gate_b_physics_signoff_v1",
                "reviewer": signoff_source["reviewer"],
                "reviewer_role": signoff_source["reviewer_role"],
                "decision_utc": decision_utc,
                "finding": signoff_source["finding"],
                "allowed_unresolved_treatment":
                    contract.NONZERO_UNRESOLVED_TREATMENT,
                "reviewed_unresolved_trigger_candidates": samples,
                "reviewed_unresolved_trigger_candidates_total": total,
            },
            "revalidated_original_evidence": {
                "pthat_decision_sha256": pthat_sha,
            },
        }
        contract.validate_gate_b_pthat_resolution(
            checkout_root=checkout,
            gate_b_report=gate_b,
            pthat_report=pthat,
            pthat_report_sha256=pthat_sha,
        )
        pthat["comparisons"][0]["status"] = "MATERIAL_SHIFT"
        try:
            contract.validate_gate_b_pthat_resolution(
                checkout_root=checkout,
                gate_b_report=gate_b,
                pthat_report=pthat,
                pthat_report_sha256=pthat_sha,
            )
        except ValueError as error:
            assert "cannot waive a resolved or material pTHat shift" in str(
                error
            )
        else:
            raise AssertionError(
                "owner origin sign-off waived a material pTHat shift"
            )


def main() -> int:
    test_resolved_pthat_authorization_route()
    with tempfile.TemporaryDirectory(
        prefix="hadronization_full_submission_test_"
    ) as temporary:
        test_root = Path(temporary)
        checkout = test_root / "checkout"
        checkout.mkdir()
        prepare_checkout(checkout)
        test_home = test_root / "home"
        test_home.mkdir()
        os.environ["HOME"] = str(test_home)
        shared_registry_root = test_root / "shared_submission_registry"
        shared_registry_root.mkdir()
        os.environ["HADRONIZATION_SUBMISSION_REGISTRY_ROOT"] = str(
            shared_registry_root.resolve()
        )
        fake_python = test_root / "fake_python"
        fake_python.mkdir()
        (fake_python / "sitecustomize.py").write_text(
            "import os\n"
            "_real_statvfs = os.statvfs\n"
            "_blocks = (10 * 1024**4) // 4096\n"
            "_bavail = (8 * 1024**4) // 4096\n"
            "def _fixture_statvfs(path):\n"
            "    return os.statvfs_result((4096,4096,_blocks,_bavail,"
            "_bavail,1000000,900000,900000,0,255))\n"
            "os.statvfs = _fixture_statvfs\n"
        )
        os.environ["PYTHONPATH"] = str(fake_python) + os.pathsep + (
            os.environ.get("PYTHONPATH", "")
        )
        fake_scheduler = test_root / "fake_scheduler"
        fake_scheduler.mkdir()
        classad_fixture = test_root / "submission_classads.json"
        condor_q_submit = fake_scheduler / "condor_q"
        condor_q_submit.write_text(
            "#!/usr/bin/env python3\n"
            "import os\n"
            "print(open(os.environ['HF_TEST_CLASSADS_PATH']).read(), end='')\n"
        )
        condor_q_submit.chmod(0o755)
        os.environ["HF_TEST_CLASSADS_PATH"] = str(classad_fixture)
        os.environ["PATH"] = (
            str(fake_scheduler)
            + os.pathsep
            + os.environ.get("PATH", "")
        )
        registry = (
            Path(os.environ["HADRONIZATION_SUBMISSION_REGISTRY_ROOT"])
            / hashlib.sha256(
                b"github.com/waxpardo/hadronization"
            ).hexdigest()
        )
        registry.mkdir(parents=True)
        baseline = registry / "reservation_baseline.json"
        baseline.write_text(
            json.dumps(
                {
                    "schema": "hf_submission_registry_baseline_v1",
                    "repository_identity":
                        "github.com/waxpardo/hadronization",
                    "reviewer": "Submission Contract Unit Test",
                    "historical_reservations": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        baseline.chmod(0o444)
        for unsafe_campaign in (".", "..", "-leading", "trailing_"):
            assert contract.SAFE_CAMPAIGN.fullmatch(unsafe_campaign) is None
        lock_target = test_root / "lock_target"
        lock_target.write_text("do not lock through this file\n")
        lock_symlink = test_root / "unsafe.lock"
        lock_symlink.symlink_to(lock_target)
        try:
            with contract.locked_regular_file(lock_symlink):
                pass
        except ValueError as error:
            assert "without following links" in str(error)
        else:
            raise AssertionError("symlinked lock was accepted")
        registry_link_target = test_root / "registry_link_target"
        registry_link_target.mkdir()
        registry_link = test_root / "registry_link"
        registry_link.symlink_to(registry_link_target, target_is_directory=True)
        canonical_registry_root = os.environ[
            "HADRONIZATION_SUBMISSION_REGISTRY_ROOT"
        ]
        os.environ["HADRONIZATION_SUBMISSION_REGISTRY_ROOT"] = str(
            registry_link
        )
        try:
            contract.global_submission_registry(checkout)
        except ValueError as error:
            assert "not a real directory" in str(error)
        else:
            raise AssertionError("symlinked submission registry was accepted")
        finally:
            os.environ["HADRONIZATION_SUBMISSION_REGISTRY_ROOT"] = (
                canonical_registry_root
            )

        campaign = "HF_full_submission_contract_test"
        campaign_dir = generate_full(checkout, campaign, 880, 100_000_001)
        validation = run(
            sys.executable,
            str(MANIFEST),
            "validate",
            str(campaign_dir),
            "--checkout-root",
            str(checkout),
        )
        assert "campaign valid: candidates=500" in validation.stdout
        rows = [
            json.loads(line)
            for line in (
                campaign_dir / "candidate_manifest.jsonl"
            ).read_text().splitlines()
        ]
        assert len(rows) == 500
        assert sum(row["role"] == "primary" for row in rows) == 300
        assert all(row["pthat_min_override"] == "NONE" for row in rows)
        assert all(row["multiplicity_audit_events"] == 0 for row in rows)
        assert all(len(row["effective_card_sha256"]) == 64 for row in rows)

        reports = write_gate_reports(campaign_dir)
        campaign_config = json.loads(
            (campaign_dir / "campaign.json").read_text()
        )
        gate_d_payload = json.loads(
            (checkout / reports["gate_d"]["path"]).read_text()
        )
        fabricated_storage = json.loads(json.dumps(gate_d_payload))
        del fabricated_storage["storage_projection"][
            "final_capacity_recheck"
        ]["filesystems"][0]["statvfs_blocks"]
        try:
            contract.validate_gate_d_storage_projection(fabricated_storage)
        except ValueError as error:
            assert "statvfs_blocks is not an integer" in str(error)
        else:
            raise AssertionError("fabricated storage geometry was accepted")
        for gate_name, command_key in (
            ("gate_a", "command"),
            ("gate_b", "argv"),
            ("gate_d", "command"),
        ):
            report_path = checkout / reports[gate_name]["path"]
            original = report_path.read_bytes()
            synthetic = json.loads(original)
            synthetic["commands"][0][command_key] = ["/usr/bin/true"]
            overwrite_sealed(
                report_path,
                (
                    json.dumps(synthetic, indent=2, sort_keys=True) + "\n"
                ).encode(),
            )
            try:
                contract.validate_gate_report_semantics(
                    gate_name,
                    report_path,
                    checkout,
                    campaign_config,
                )
            except ValueError as error:
                assert (
                    "command" in str(error).lower()
                    or "argv" in str(error).lower()
                ), str(error)
            else:
                raise AssertionError(
                    f"{gate_name} accepted /usr/bin/true evidence"
                )
            overwrite_sealed(report_path, original)
        signoff = write_signoff(campaign_dir, reports["gate_b"])
        gate_authorization = write_gate_authorization(
            campaign_dir, signoff, reports
        )
        producer = checkout / "SimulationScripts/heavyflavourcorrelations_status"
        producer_sha = hashlib.sha256(producer.read_bytes()).hexdigest()
        campaign_root = checkout / "Production" / campaign
        campaign_root.mkdir(parents=True, exist_ok=True)
        submit_file = campaign_root / "submit_candidates.sub"
        run(
            sys.executable,
            str(RENDERER),
            str(campaign_dir),
            str(checkout),
            str(submit_file),
            "--roles",
            "all",
            "--producer-executable-sha256",
            producer_sha,
        )
        claim_arguments = [
            sys.executable,
            str(MANIFEST),
            "claim-submission",
            str(campaign_dir),
            "--checkout-root",
            str(checkout),
            "--production-root",
            str(checkout / "Production"),
            "--submit-file",
            str(submit_file),
            "--producer",
            str(producer),
            "--producer-executable-sha256",
            producer_sha,
            "--submission-kind",
            "full",
            "--approval-file",
            str(signoff),
        ]
        missing_authorization = run(*claim_arguments, expect=1)
        assert (
            "full submission requires Gates A-D owner authorization"
            in missing_authorization.stderr
        )

        authorization_bytes = gate_authorization.read_bytes()
        authorization_json = json.loads(authorization_bytes)
        gate_d_report = (
            checkout / authorization_json["reports"]["gate_d"]["path"]
        )
        gate_d_report_bytes = gate_d_report.read_bytes()
        overwrite_sealed(
            gate_d_report, gate_d_report_bytes + b"tampered\n"
        )
        mismatched_authorization = run(
            *claim_arguments,
            "--gate-authorization-file",
            str(gate_authorization),
            expect=1,
        )
        assert (
            "gate authorization report gate_d checksum differs"
            in mismatched_authorization.stderr
        ), mismatched_authorization.stderr
        overwrite_sealed(gate_d_report, gate_d_report_bytes)

        failed_gate_d = json.loads(gate_d_report_bytes)
        failed_gate_d["state"] = "FAIL"
        failed_gate_d["failure"] = "synthetic negative test"
        overwrite_sealed(
            gate_d_report,
            (
                json.dumps(failed_gate_d, indent=2, sort_keys=True) + "\n"
            ).encode(),
        )
        authorization_json["reports"]["gate_d"]["sha256"] = (
            hashlib.sha256(gate_d_report.read_bytes()).hexdigest()
        )
        overwrite_sealed(
            gate_authorization,
            (
                json.dumps(authorization_json, indent=2, sort_keys=True)
                + "\n"
            ).encode(),
        )
        semantic_failure = run(
            *claim_arguments,
            "--gate-authorization-file",
            str(gate_authorization),
            expect=1,
        )
        assert (
            "gate authorization report gate_d did not reach PASS"
            in semantic_failure.stderr
        )
        overwrite_sealed(gate_d_report, gate_d_report_bytes)
        overwrite_sealed(gate_authorization, authorization_bytes)
        authorization_json = json.loads(authorization_bytes)

        failed_storage = json.loads(gate_d_report_bytes)
        del failed_storage["storage_projection"]["final_capacity_recheck"]
        overwrite_sealed(
            gate_d_report,
            (
                json.dumps(failed_storage, indent=2, sort_keys=True) + "\n"
            ).encode(),
        )
        authorization_json["reports"]["gate_d"]["sha256"] = (
            hashlib.sha256(gate_d_report.read_bytes()).hexdigest()
        )
        overwrite_sealed(
            gate_authorization,
            (
                json.dumps(authorization_json, indent=2, sort_keys=True)
                + "\n"
            ).encode(),
        )
        storage_failure = run(
            *claim_arguments,
            "--gate-authorization-file",
            str(gate_authorization),
            expect=1,
        )
        assert "Gate-D final capacity check is absent" in (
            storage_failure.stderr
        )
        overwrite_sealed(gate_d_report, gate_d_report_bytes)
        overwrite_sealed(gate_authorization, authorization_bytes)
        authorization_json = json.loads(authorization_bytes)

        authorization_json["repository_commit"] = "0" * 40
        overwrite_sealed(
            gate_authorization,
            (
                json.dumps(authorization_json, indent=2, sort_keys=True)
                + "\n"
            ).encode(),
        )
        stale_authorization = run(
            *claim_arguments,
            "--gate-authorization-file",
            str(gate_authorization),
            expect=1,
        )
        assert (
            "full-production gate authorization repository_commit differs"
            in stale_authorization.stderr
        )
        overwrite_sealed(gate_authorization, authorization_bytes)

        signoff_bytes = signoff.read_bytes()
        signoff.chmod(0o644)
        mutable_signoff = run(
            *claim_arguments,
            "--gate-authorization-file",
            str(gate_authorization),
            expect=1,
        )
        assert "not sealed as a single-link 0444 file" in (
            mutable_signoff.stderr
        )
        signoff.chmod(0o444)

        signoff_json = json.loads(signoff_bytes)
        signoff_json[
            "reviewed_unresolved_trigger_candidates_total"
        ] = 1
        signoff.chmod(0o644)
        signoff.write_text(
            json.dumps(signoff_json, indent=2, sort_keys=True) + "\n"
        )
        signoff.chmod(0o444)
        authorization_json = json.loads(authorization_bytes)
        authorization_json["physics_origin_signoff_sha256"] = (
            hashlib.sha256(signoff.read_bytes()).hexdigest()
        )
        overwrite_sealed(
            gate_authorization,
            (
                json.dumps(authorization_json, indent=2, sort_keys=True)
                + "\n"
            ).encode(),
        )
        mismatched_signoff = run(
            *claim_arguments,
            "--gate-authorization-file",
            str(gate_authorization),
            expect=1,
        )
        assert (
            "reviewed_unresolved_trigger_candidates_total differs from the "
            "authorized Gate-B report"
            in mismatched_signoff.stderr
        )
        signoff.chmod(0o644)
        signoff.write_bytes(signoff_bytes)
        signoff.chmod(0o444)
        overwrite_sealed(gate_authorization, authorization_bytes)

        claim_result = run(
            *claim_arguments,
            "--gate-authorization-file",
            str(gate_authorization),
        )
        claim_path = Path(claim_result.stdout.strip())
        claim = json.loads(claim_path.read_text())
        assert claim["schema"] == "hf_full_submission_claim_v1"
        assert claim["submission_kind"] == "full"
        assert len(claim["allocations"]) == 500
        assert claim["reserved_seed_intervals"] == [
            [100_000_001, 100_500_000]
        ]
        stale_claim = json.loads(claim_path.read_text())
        stale_claim["live_storage_recheck"]["checked_utc"] = (
            "2000-01-01T00:00:00+00:00"
        )
        try:
            contract.recheck_storage_from_claim(
                stale_claim, checkout.resolve()
            )
        except ValueError as error:
            assert "live-storage check is stale" in str(error)
        else:
            raise AssertionError("stale live-storage claim was accepted")

        row = rows[0]
        authorization_arguments = [
            sys.executable,
            str(MANIFEST),
            "authorize",
            str(campaign_dir),
            campaign,
            row["tune"],
            str(row["logical_id"]),
            row["role"],
            str(row["attempt"]),
            str(row["seed"]),
            str(row["requested_successes"]),
            "--campaign-ordinal",
            str(row["campaign_ordinal"]),
            "--pthat-min-override",
            row["pthat_min_override"],
            "--multiplicity-audit-events",
            str(row["multiplicity_audit_events"]),
            "--repository-commit",
            row["repository_commit"],
            "--effective-card-sha256",
            row["effective_card_sha256"],
            "--producer-executable-sha256",
            producer_sha,
            "--checkout-root",
            str(checkout),
            "--require-submission-claim",
            "--cluster-id",
            "23456",
            "--process-id",
            "0",
        ]
        unrecorded_authorization = run(
            *authorization_arguments, expect=1
        )
        assert "submission record is absent" in (
            unrecorded_authorization.stderr
        )
        short_submission = run(
            sys.executable,
            str(MANIFEST),
            "record-submission",
            str(claim_path),
            "23456.0 - 23456.299",
            "--checkout-root",
            str(checkout),
            expect=1,
        )
        assert "does not cover the exact claimed queue" in (
            short_submission.stderr
        )
        write_submission_classads(
            classad_fixture,
            claim_path,
            checkout,
            23456,
            corrupt_process=7,
        )
        mismatched_classad = run(
            sys.executable,
            str(MANIFEST),
            "record-submission",
            str(claim_path),
            "23456.0 - 23456.499",
            "--checkout-root",
            str(checkout),
            expect=1,
        )
        assert "ClassAd 7 HFSeed differs" in mismatched_classad.stderr, (
            mismatched_classad.stderr
        )
        write_submission_classads(
            classad_fixture, claim_path, checkout, 23456
        )
        record = run(
            sys.executable,
            str(MANIFEST),
            "record-submission",
            str(claim_path),
            "23456.0 - 23456.499",
            "--checkout-root",
            str(checkout),
        )
        assert Path(record.stdout.strip()).name == (
            "full_candidates_attempt0_submitted.json"
        )
        mismatched_scheduler = list(authorization_arguments)
        mismatched_scheduler[
            mismatched_scheduler.index("--cluster-id") + 1
        ] = "99999"
        rejected_scheduler = run(
            *mismatched_scheduler, expect=1
        )
        assert "ClusterId differs" in rejected_scheduler.stderr
        authorization = run(*authorization_arguments)
        assert "CAMPAIGN_ALLOCATION_AUTHORIZED" in authorization.stdout

        fake_condor = test_root / "fake_condor"
        fake_condor.mkdir()
        condor_q = fake_condor / "condor_q"
        condor_history = fake_condor / "condor_history"
        condor_q.write_text("#!/bin/sh\nprintf '[]\\n'\n")
        condor_history.write_text(
            "#!/bin/sh\n"
            "printf '[{\"ClusterId\":23456,\"ProcId\":4,"
            "\"JobStatus\":3}]\\n'\n"
        )
        condor_q.chmod(0o755)
        condor_history.chmod(0o755)
        scheduler_evidence_result = run(
            sys.executable,
            str(MANIFEST),
            "capture-scheduler-terminal-evidence",
            str(campaign_dir),
            "--checkout-root",
            str(checkout),
            "--tune",
            "MONASH",
            "--logical-id",
            "4",
            "--attempt",
            "0",
            "--condor-q",
            str(condor_q),
            "--condor-history",
            str(condor_history),
        )
        scheduler_evidence = Path(
            scheduler_evidence_result.stdout.strip()
        )
        scheduler_payload = json.loads(scheduler_evidence.read_text())
        assert scheduler_payload["condor_q"]["live_matches"] == 0
        assert scheduler_payload["condor_history"]["job_status"] == 3

        live_q_dir = fake_condor / "live"
        live_q_dir.mkdir()
        live_q = live_q_dir / "condor_q"
        live_q.write_text(
            "#!/bin/sh\n"
            "printf '[{\"ClusterId\":23456,\"ProcId\":6,"
            "\"JobStatus\":2}]\\n'\n"
        )
        live_q.chmod(0o755)
        live_rejected = run(
            sys.executable,
            str(MANIFEST),
            "capture-scheduler-terminal-evidence",
            str(campaign_dir),
            "--checkout-root",
            str(checkout),
            "--tune",
            "MONASH",
            "--logical-id",
            "6",
            "--attempt",
            "0",
            "--condor-q",
            str(live_q),
            "--condor-history",
            str(condor_history),
            expect=1,
        )
        assert "found a live job" in live_rejected.stderr

        authorization_dir = campaign_root / "retry_authorizations"
        authorization_dir.mkdir()
        missing_machine_approval = (
            authorization_dir
            / "MONASH_job005_attempt000_scheduler_loss.json"
        )
        missing_machine_approval.write_text(
            json.dumps(
                {
                    "schema":
                        "hf_scheduler_loss_retry_authorization_v1",
                    "approved": True,
                    "reviewer": "Synthetic Fixture Reviewer",
                    "reviewer_role": "project_owner",
                    "decision_utc": datetime.now(timezone.utc).isoformat(
                        timespec="seconds"
                    ),
                    "reason": "Scheduler terminal state reviewed.",
                    "scheduler_state": "never_started",
                    "campaign": campaign,
                    "campaign_ordinal": 880,
                    "tune": "MONASH",
                    "logical_id": 5,
                    "prior_attempt": 0,
                    "repository_commit": row["repository_commit"],
                    "attempt_start_claim_sha256": None,
                    "machine_evidence_path":
                        "Production/"
                        f"{campaign}/scheduler_evidence/MONASH/"
                        "job_005/attempt_000/evidence.json",
                    "machine_evidence_sha256": "0" * 64,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        missing_machine_approval.chmod(0o444)
        missing_machine_rejected = run(
            sys.executable,
            str(MANIFEST),
            "allocate-retry",
            str(campaign_dir),
            "MONASH",
            "5",
            "--reason",
            "scheduler loss without evidence",
            "--scheduler-loss-approval",
            str(missing_machine_approval),
            expect=1,
        )
        assert "machine evidence is absent" in missing_machine_rejected.stderr

        scheduler_approval = (
            authorization_dir
            / "MONASH_job004_attempt000_scheduler_loss.json"
        )
        scheduler_approval.write_text(
            json.dumps(
                {
                    "schema":
                        "hf_scheduler_loss_retry_authorization_v1",
                    "approved": True,
                    "reviewer": "Synthetic Fixture Reviewer",
                    "reviewer_role": "project_owner",
                    "decision_utc": datetime.now(timezone.utc).isoformat(
                        timespec="seconds"
                    ),
                    "reason":
                        "Condor history is terminal and condor_q has no "
                        "matching live job.",
                    "scheduler_state": "never_started",
                    "campaign": campaign,
                    "campaign_ordinal": 880,
                    "tune": "MONASH",
                    "logical_id": 4,
                    "prior_attempt": 0,
                    "repository_commit": row["repository_commit"],
                    "attempt_start_claim_sha256": None,
                    "machine_evidence_path": str(
                        scheduler_evidence.relative_to(checkout.resolve())
                    ),
                    "machine_evidence_sha256": hashlib.sha256(
                        scheduler_evidence.read_bytes()
                    ).hexdigest(),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        scheduler_approval.chmod(0o444)
        scheduler_evidence_bytes = scheduler_evidence.read_bytes()
        scheduler_approval_bytes = scheduler_approval.read_bytes()
        mismatched_history = json.loads(scheduler_evidence_bytes)
        mismatched_history["condor_history"]["job_status"] = 4
        overwrite_sealed(
            scheduler_evidence,
            (
                json.dumps(mismatched_history, indent=2, sort_keys=True) + "\n"
            ).encode(),
        )
        mismatched_approval = json.loads(scheduler_approval_bytes)
        mismatched_approval["machine_evidence_sha256"] = hashlib.sha256(
            scheduler_evidence.read_bytes()
        ).hexdigest()
        overwrite_sealed(
            scheduler_approval,
            (
                json.dumps(mismatched_approval, indent=2, sort_keys=True) + "\n"
            ).encode(),
        )
        raw_scheduler_mismatch = run(
            sys.executable,
            str(MANIFEST),
            "allocate-retry",
            str(campaign_dir),
            "MONASH",
            "4",
            "--reason",
            "mismatched scheduler summary",
            "--scheduler-loss-approval",
            str(scheduler_approval),
            expect=1,
        )
        assert "raw q/history semantics differ" in (
            raw_scheduler_mismatch.stderr
        )
        overwrite_sealed(scheduler_evidence, scheduler_evidence_bytes)
        overwrite_sealed(scheduler_approval, scheduler_approval_bytes)
        scheduler_retry = run(
            sys.executable,
            str(MANIFEST),
            "allocate-retry",
            str(campaign_dir),
            "MONASH",
            "4",
            "--reason",
            "reviewed terminal scheduler loss",
            "--scheduler-loss-approval",
            str(scheduler_approval),
        )
        scheduler_retry_row = json.loads(scheduler_retry.stdout)
        assert scheduler_retry_row["attempt"] == 1
        assert (
            scheduler_retry_row["prior_attempt_evidence"]["kind"]
            == "scheduler_loss_approval"
        )

        attempt_work = (
            campaign_root
            / "work"
            / "MONASH"
            / "job_000"
            / "attempt_000"
            / "23456_0"
        )
        attempt_work.mkdir(parents=True)
        attempt_card = attempt_work / "effective.cmnd"
        attempt_producer = attempt_work / "heavyflavourcorrelations_status"
        run(
            sys.executable,
            str(MANIFEST),
            "materialize-effective-card",
            str(
                checkout
                / "SimulationScripts"
                / "pythiasettings_Hard_Low_ccbb_MONASH.cmnd"
            ),
            str(attempt_card),
            "10",
            "NONE",
            row["effective_card_sha256"],
        )
        attempt_producer.write_bytes(producer.read_bytes())
        attempt_producer.chmod(0o555)
        attempt_args = [
            sys.executable,
            str(MANIFEST),
            "claim-attempt-start",
            str(campaign_dir),
            "--checkout-root",
            str(checkout),
            "--campaign",
            campaign,
            "--campaign-ordinal",
            "880",
            "--tune",
            "MONASH",
            "--logical-id",
            "0",
            "--role",
            "primary",
            "--attempt",
            "0",
            "--seed",
            "100000001",
            "--requested-successes",
            "10",
            "--repository-commit",
            row["repository_commit"],
            "--effective-card-sha256",
            row["effective_card_sha256"],
            "--producer-executable-sha256",
            producer_sha,
            "--cluster-id",
            "23456",
            "--process-id",
            "0",
            "--private-card",
            str(attempt_card),
            "--private-producer",
            str(attempt_producer),
        ]
        start_result = run(*attempt_args)
        start_path = Path(start_result.stdout.strip())
        assert json.loads(start_path.read_text())["seed"] == 100_000_001
        duplicate_start = run(*attempt_args, expect=1)
        assert "File exists" in duplicate_start.stderr
        failed_metadata_dir = (
            campaign_root / "attempt_metadata" / "MONASH"
        )
        failed_metadata_dir.mkdir(parents=True)
        failed_metadata = (
            failed_metadata_dir
            / "hf_MONASH_job000_attempt000_23456_0.json"
        )
        failed_metadata.write_text(
            json.dumps(
                {
                    "campaign": campaign,
                    "tune": "MONASH",
                    "logical_id": 0,
                    "attempt": 0,
                    "seed": 100_000_001,
                    "role": "primary",
                    "requested_successes": 10,
                    "producer_exit": 9,
                    "cluster_id": "23456",
                    "process_id": "0",
                    "attempt_start_claim_sha256": hashlib.sha256(
                        start_path.read_bytes()
                    ).hexdigest(),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        retry_allocation_result = run(
            sys.executable,
            str(MANIFEST),
            "allocate-retry",
            str(campaign_dir),
            "MONASH",
            "0",
            "--reason",
            "synthetic producer failure",
        )
        retry_allocation = json.loads(retry_allocation_result.stdout)
        assert retry_allocation["attempt"] == 1
        assert retry_allocation["seed"] == 100_000_002
        assert (
            retry_allocation["prior_attempt_evidence"]["kind"]
            == "producer_failure"
        )
        retry_submit = (
            campaign_root
            / "retry_submissions"
            / "submit_MONASH_job000_attempt001.sub"
        )
        run(
            sys.executable,
            str(RENDERER),
            str(campaign_dir),
            str(checkout),
            str(retry_submit),
            "--producer-executable-sha256",
            producer_sha,
            "--retry-tune",
            "MONASH",
            "--retry-logical-id",
            "0",
            "--retry-attempt",
            "1",
        )
        retry_claim_result = run(
            sys.executable,
            str(MANIFEST),
            "claim-retry-submission",
            str(campaign_dir),
            "--checkout-root",
            str(checkout),
            "--production-root",
            str(checkout / "Production"),
            "--submit-file",
            str(retry_submit),
            "--producer",
            str(producer),
            "--producer-executable-sha256",
            producer_sha,
            "--tune",
            "MONASH",
            "--logical-id",
            "0",
            "--attempt",
            "1",
            "--seed",
            "100000002",
        )
        retry_claim_path = Path(retry_claim_result.stdout.strip())
        retry_row = dict(row)
        retry_row["attempt"] = 1
        retry_row["seed"] = 100_000_002
        retry_authorization_arguments = [
            sys.executable,
            str(MANIFEST),
            "authorize",
            str(campaign_dir),
            campaign,
            "MONASH",
            "0",
            "primary",
            "1",
            "100000002",
            "10",
            "--campaign-ordinal",
            "880",
            "--pthat-min-override",
            "NONE",
            "--multiplicity-audit-events",
            "0",
            "--repository-commit",
            retry_row["repository_commit"],
            "--effective-card-sha256",
            retry_row["effective_card_sha256"],
            "--producer-executable-sha256",
            producer_sha,
            "--checkout-root",
            str(checkout),
            "--require-submission-claim",
            "--cluster-id",
            "34567",
            "--process-id",
            "0",
        ]
        unrecorded_retry = run(
            *retry_authorization_arguments, expect=1
        )
        assert "submission record is absent" in unrecorded_retry.stderr
        write_submission_classads(
            classad_fixture, retry_claim_path, checkout, 34567
        )
        retry_record_result = run(
            sys.executable,
            str(MANIFEST),
            "record-retry-submission",
            str(retry_claim_path),
            "34567.0",
            "--checkout-root",
            str(checkout),
        )
        assert Path(retry_record_result.stdout.strip()).name.endswith(
            "_submitted.json"
        )
        retry_authorization = run(*retry_authorization_arguments)
        assert "attempt=1 seed=100000002" in retry_authorization.stdout
        no_start_metadata = (
            failed_metadata_dir
            / "hf_MONASH_job003_attempt000_99999_0.json"
        )
        no_start_metadata.write_text(
            json.dumps(
                {
                    "campaign": campaign,
                    "tune": "MONASH",
                    "logical_id": 3,
                    "attempt": 0,
                    "seed": 100_003_001,
                    "role": "primary",
                    "requested_successes": 10,
                    "producer_exit": 9,
                    "cluster_id": "99999",
                    "process_id": "0",
                    "attempt_start_claim_sha256": "0" * 64,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        no_start_retry = run(
            sys.executable,
            str(MANIFEST),
            "allocate-retry",
            str(campaign_dir),
            "MONASH",
            "3",
            "--reason",
            "synthetic sidecar without start claim",
            expect=1,
        )
        assert "lacks an attempt-start claim" in no_start_retry.stderr

        private_source = test_root / "producer_source"
        private_source.write_text("#!/bin/sh\necho sealed\n")
        private_source.chmod(0o755)
        private_sha = hashlib.sha256(private_source.read_bytes()).hexdigest()
        private_snapshot = test_root / "private_job" / "producer"
        run(
            sys.executable,
            str(MANIFEST),
            "snapshot-executable",
            str(private_source),
            str(private_snapshot),
            private_sha,
        )
        private_source.write_text("#!/bin/sh\necho changed\n")
        assert hashlib.sha256(private_snapshot.read_bytes()).hexdigest() == private_sha

        validation_fixture = test_root / "raw_validation_fixture"
        fixture_validation_dir = validation_fixture / "Validation"
        fixture_simulation_dir = validation_fixture / "SimulationScripts"
        fixture_analysis_dir = validation_fixture / "AnalysisScripts"
        fixture_validation_dir.mkdir(parents=True)
        fixture_simulation_dir.mkdir()
        fixture_analysis_dir.mkdir()
        fixture_wrapper = fixture_validation_dir / "validate_raw_output.sh"
        fixture_macro = fixture_validation_dir / "ValidateRawOutput.C"
        fixture_setup = validation_fixture / "setupEnv.sh"
        fixture_heavy = fixture_simulation_dir / "HeavyFlavourUtils.h"
        fixture_pairs = fixture_analysis_dir / "GeneratedPairRegistry.h"
        fixture_wrapper.write_text("#!/bin/sh\nexit 0\n")
        fixture_wrapper.chmod(0o755)
        fixture_macro.write_text("int ValidateRawOutput() { return 0; }\n")
        fixture_setup.write_text("#!/bin/sh\n")
        fixture_heavy.write_text("#pragma once\n")
        fixture_pairs.write_text("#pragma once\n")
        fixture_output = validation_fixture / "candidate.partial.root"
        fixture_output.write_bytes(b"synthetic ROOT output bytes")
        fixture_log = validation_fixture / "validate_raw_output.log"
        fixture_log.write_text(
            "RAW_VALIDATION_SUMMARY errors=0 entries=10 successes=10\n"
        )
        fixture_receipt = validation_fixture / "receipt.json"
        receipt_common = [
            str(fixture_receipt),
            str(fixture_output),
            str(fixture_log),
            str(fixture_wrapper),
            str(fixture_macro),
            "--dependency",
            str(fixture_setup),
            "--dependency",
            str(fixture_heavy),
            "--dependency",
            str(fixture_pairs),
            "--campaign",
            campaign,
            "--campaign-ordinal",
            "880",
            "--tune",
            "MONASH",
            "--logical-id",
            "0",
            "--role",
            "primary",
            "--attempt",
            "0",
            "--seed",
            "100000001",
            "--requested-successes",
            "10",
            "--phase-space-pthat-min",
            "0.5",
            "--multiplicity-audit-events",
            "0",
            "--repository-commit",
            row["repository_commit"],
            "--effective-card-sha256",
            row["effective_card_sha256"],
            "--producer-executable-sha256",
            producer_sha,
            "--attempt-start-claim-sha256",
            hashlib.sha256(b"synthetic attempt start").hexdigest(),
            "--cluster-id",
            "12345",
            "--process-id",
            "0",
        ]
        run(
            sys.executable,
            str(MANIFEST),
            "record-raw-validation",
            *receipt_common,
            "--validator-status",
            "0",
        )
        receipt_payload = json.loads(fixture_receipt.read_text())
        assert receipt_payload["result"] == "PASS"
        assert receipt_payload["output_bytes"] == fixture_output.stat().st_size
        run(
            sys.executable,
            str(MANIFEST),
            "verify-raw-validation",
            *receipt_common,
        )
        fixture_output.write_bytes(b"mutated after validation")
        changed_output = run(
            sys.executable,
            str(MANIFEST),
            "verify-raw-validation",
            *receipt_common,
            expect=1,
        )
        assert "raw-validation receipt mismatch output_sha256" in (
            changed_output.stderr
        )

        failed_output = validation_fixture / "failed.partial.root"
        failed_output.write_bytes(b"invalid output")
        failed_log = validation_fixture / "failed_validation.log"
        failed_log.write_text("RAW_VALIDATION_ERROR missing provenance\n")
        failed_receipt = validation_fixture / "failed_receipt.json"
        failed_receipt_args = receipt_common.copy()
        failed_receipt_args[0] = str(failed_receipt)
        failed_receipt_args[1] = str(failed_output)
        failed_receipt_args[2] = str(failed_log)
        run(
            sys.executable,
            str(MANIFEST),
            "record-raw-validation",
            *failed_receipt_args,
            "--validator-status",
            "90",
        )
        assert json.loads(failed_receipt.read_text())["result"] == "FAIL"
        failed_verification = run(
            sys.executable,
            str(MANIFEST),
            "verify-raw-validation",
            *failed_receipt_args,
            expect=1,
        )
        assert "raw-validation receipt mismatch result" in (
            failed_verification.stderr
        )

        run("git", "add", "campaigns", cwd=checkout)
        run("git", "commit", "-q", "-m", "archive first full campaign", cwd=checkout)
        second_checkout = test_root / "second_checkout"
        run("git", "clone", "-q", str(checkout), str(second_checkout))
        run(
            "git",
            "remote",
            "set-url",
            "origin",
            "https://github.com/Waxpardo/Hadronization.git",
            cwd=second_checkout,
        )
        second_campaign = "HF_full_overlapping_seed_interval_test"
        second_dir = generate_full(
            second_checkout, second_campaign, 881, 100_400_000
        )
        second_reports = write_gate_reports(second_dir)
        second_signoff = write_signoff(
            second_dir, second_reports["gate_b"]
        )
        second_gate_authorization = write_gate_authorization(
            second_dir, second_signoff, second_reports
        )
        second_root = second_checkout / "Production" / second_campaign
        second_root.mkdir(parents=True, exist_ok=True)
        second_submit = second_root / "submit_candidates.sub"
        run(
            sys.executable,
            str(RENDERER),
            str(second_dir),
            str(second_checkout),
            str(second_submit),
            "--roles",
            "all",
            "--producer-executable-sha256",
            producer_sha,
        )
        overlap = run(
            sys.executable,
            str(MANIFEST),
            "claim-submission",
            str(second_dir),
            "--checkout-root",
            str(second_checkout),
            "--production-root",
            str(second_checkout / "Production"),
            "--submit-file",
            str(second_submit),
            "--producer",
            str(
                second_checkout
                / "SimulationScripts"
                / "heavyflavourcorrelations_status"
            ),
            "--producer-executable-sha256",
            producer_sha,
            "--submission-kind",
            "full",
            "--approval-file",
            str(second_signoff),
            "--gate-authorization-file",
            str(second_gate_authorization),
            expect=1,
        )
        assert "seed reuse blocked" in overlap.stderr

    print("full-production submission-contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
