#!/usr/bin/env python3
"""Contract tests for Gate-D filtering and immutable certification."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_publication_gate_d.py"


def load_runner():
    specification = importlib.util.spec_from_file_location(
        "publication_gate_d_test_module", RUNNER
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
        raise AssertionError(result.stdout)
    return result.stdout


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_checkout(path: Path) -> str:
    (path / "tracked.txt").write_text("Gate-D fixture\n")
    run("git", "init", "-q", cwd=path)
    run("git", "config", "user.name", "Gate D Test", cwd=path)
    run(
        "git",
        "config",
        "user.email",
        "gate-d@example.invalid",
        cwd=path,
    )
    run(
        "git",
        "remote",
        "add",
        "origin",
        "https://github.com/Waxpardo/Hadronization.git",
        cwd=path,
    )
    run("git", "add", "tracked.txt", cwd=path)
    run("git", "commit", "-q", "-m", "fixture", cwd=path)
    return run("git", "rev-parse", "HEAD", cwd=path).strip()


def make_fixture(module, temporary: Path) -> dict[str, Path | str]:
    checkout = temporary / "checkout"
    checkout.mkdir()
    commit = prepare_checkout(checkout)
    campaign = temporary / "gate_b_campaign"
    campaign.mkdir()
    campaign_json = {
        "schema": "hf_gate_b_pilot_campaign_v1",
        "campaign": campaign.name,
        "campaign_ordinal": 71,
        "repository_implementation_commit": commit,
    }
    (campaign / "campaign.json").write_text(
        json.dumps(campaign_json) + "\n"
    )
    rows = []
    for tune in module.TUNES:
        for logical_id, purpose, successes in (
            (0, "one_million_central", 1_000_000),
            (1, "pthat_sensitivity_low", 1_000_000),
            (2, "pthat_sensitivity_high", 1_000_000),
        ):
            rows.append(
                {
                    "tune": tune,
                    "logical_id": logical_id,
                    "purpose": purpose,
                    "requested_successes": successes,
                    "attempt": 0,
                    "seed": 710000001 + len(rows) * 1000,
                    "stable_name": f"hf_{tune}_job{logical_id:03d}.root",
                }
            )
    (campaign / "candidate_manifest.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows)
    )
    (campaign / "seed_ledger.jsonl").write_text(
        "".join(
            json.dumps({"seed": row["seed"]}) + "\n" for row in rows
        )
    )

    production = temporary / "production"
    raw_evidence = []
    raw_bindings = []
    for row in rows:
        raw_evidence.append(
            {
                "tune": row["tune"],
                "logical_id": row["logical_id"],
                "entries": row["requested_successes"],
                "requested_successes": row["requested_successes"],
                "raw_sha256": "c" * 64,
                "validation_receipt_path": "unused",
                "validation_receipt_sha256": "d" * 64,
            }
        )
        if row["logical_id"] != 0:
            continue
        raw = (
            production
            / "raw"
            / row["tune"]
            / row["stable_name"]
        )
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_bytes(f"raw {row['tune']}\n".encode())
        raw_hash = sha(raw)
        Path(f"{raw}.sha256").write_text(f"{raw_hash}  {raw.name}\n")
        receipt = (
            production
            / "raw_validation"
            / row["tune"]
            / "job_000"
            / "attempt_000"
            / "receipt.json"
        )
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(
            json.dumps(
                {
                    "schema": "hf_raw_validation_receipt_v1",
                    "result": "PASS",
                    "output_sha256": raw_hash,
                }
            )
            + "\n"
        )
        raw_bindings.append(
            {
                "tune": row["tune"],
                "logical_id": 0,
                "attempt": 0,
                "seed": row["seed"],
                "raw_path": str(raw),
                "raw_sha256": raw_hash,
                "raw_validation_receipt_path": str(receipt),
                "raw_validation_receipt_sha256": sha(receipt),
            }
        )
        for evidence in raw_evidence:
            if (
                evidence["tune"] == row["tune"]
                and evidence["logical_id"] == 0
            ):
                evidence["raw_sha256"] = raw_hash
                evidence["validation_receipt_path"] = str(
                    receipt.relative_to(production)
                )
                evidence["validation_receipt_sha256"] = sha(receipt)
    gate_b = temporary / "gate_b_report.json"
    central_raw_bytes = {
        row["tune"]: Path(
            next(
                binding["raw_path"]
                for binding in raw_bindings
                if binding["tune"] == row["tune"]
            )
        ).stat().st_size
        for row in rows
        if row["logical_id"] == 0
    }
    candidate_jobs = {
        "MONASH": 100,
        "JUNCTIONS": 200,
        "CLOSEPACKING": 200,
    }
    candidate_projection_rows = [
        {
            "tune": tune,
            "candidate_jobs": candidate_jobs[tune],
            "successful_events_per_job": 1_000_000,
            "projected_successful_events":
                candidate_jobs[tune] * 1_000_000,
            "projected_raw_bytes":
                central_raw_bytes[tune] * candidate_jobs[tune],
        }
        for tune in module.TUNES
    ]
    gate_b.write_text(
        json.dumps(
            {
                "schema": "hf_publication_gate_b_report_v1",
                "state": "PASS",
                "canonical": True,
                "repository_commit": commit,
                "campaign": campaign.name,
                "campaign_ordinal": 71,
                "raw_validation_evidence": raw_evidence,
                "runtime_storage_benchmark": [
                    {
                        "tune": tune,
                        "logical_id": 0,
                        "raw_bytes": central_raw_bytes[tune],
                    }
                    for tune in module.TUNES
                ],
                "full_candidate_resource_projection": {
                    "by_tune": candidate_projection_rows,
                    "candidate_jobs": 500,
                    "projected_successful_events": 500_000_000,
                    "projected_raw_bytes": sum(
                        row["projected_raw_bytes"]
                        for row in candidate_projection_rows
                    ),
                },
            }
        )
        + "\n"
    )

    analysis = temporary / "analysis"
    analysis.mkdir()
    histogram_names = [
        "hDPhiM90_100",
        "hDPhiM80_90",
        "hDPhiM70_80",
        "hDPhiM60_70",
        "hDPhiM50_60",
        "hDPhiM40_50",
        "hDPhiM30_40",
        "hDPhiM20_30",
        "hDPhiM10_20",
        "hDPhiM1_10",
        "hDPhiM0_1",
    ]
    ignored_bins = [
        name for name in histogram_names if name != "hDPhiM1_10"
    ]
    fixture_plot_config = {
        "subsample_coverage_audit": False,
        "calculate_errors": True,
        "nSubSamples": 10,
        "subsample_error_bins_to_exclude": [],
        "PYTHIA_TUNES": list(module.TUNES),
        "histograms_to_analyse": [
            {"hDPhi": name} for name in histogram_names
        ],
        "canvases_to_be_drawn": [
            {
                "FLAVOUR": "BEAUTY",
                "TriggerToUse": "B^{+}",
                "bins_to_ignore": ignored_bins,
            },
            {
                "FLAVOUR": "CHARM",
                "TriggerToUse": "D^{+}",
                "bins_to_ignore": ignored_bins,
            },
        ],
        "beauty_correlations_to_analyse": [
            {
                "trigger": "B^{+}",
                "configs": [
                    {"associateOS": "B-"},
                    {"associateOS": "Lambda_b"},
                    {"associateOS": "Sigma_b0"},
                ],
            }
        ],
        "charm_correlations_to_analyse": [
            {
                "trigger": "D^{+}",
                "configs": [
                    {"associateOS": "D-"},
                    {"associateOS": "Lambda_c(+)-bar"},
                ],
            }
        ],
    }
    plot_config_path = analysis / "gate_d_plot_config.json"
    plot_config_path.write_text(
        json.dumps(fixture_plot_config, sort_keys=True) + "\n"
    )
    plot_scope = module.smoke_scope_contract(fixture_plot_config)
    strict_log = analysis / "logs" / "strict_coverage_and_plots.log"
    strict_log.parent.mkdir()
    exhaustive_config = {
        "base_dir": str(analysis),
        "bb_bar_complete_root_dir": "complete_root_GATE_D",
        "cc_bar_complete_root_dir": "complete_root_GATE_D",
        "bb_bar_complete_root_dir_sub_samples": str(
            analysis / "SUBSAMPLES" / "combined_root_subSamples"
        ),
        "cc_bar_complete_root_dir_sub_samples": str(
            analysis / "SUBSAMPLES" / "combined_root_subSamples"
        ),
        "nSubSamples": 10,
        "calculate_errors": True,
        "subsample_coverage_audit": True,
        "subsample_error_bins_to_exclude": [],
        "draw_correlation_plots": False,
        "PYTHIA_TUNES": list(module.TUNES),
        "histograms_to_analyse": [
            {"hDPhi": "hDPhiInclusive"},
            *[{"hDPhi": name} for name in histogram_names],
        ],
        "beauty_correlations_to_analyse": [
            {
                "trigger": "B^{+}",
                "configs": [{} for _ in range(5)],
            },
            {
                "trigger": "B^{0}",
                "configs": [{} for _ in range(5)],
            },
        ],
        "charm_correlations_to_analyse": [
            {
                "trigger": "D^{+}",
                "configs": [{} for _ in range(3)],
            },
            {
                "trigger": "D^{0}",
                "configs": [{} for _ in range(3)],
            },
        ],
        "canvases_to_be_drawn": [{"write": False}],
        "global_canvases_to_be_drawn": [{"write": False}],
    }
    exhaustive_config_path = (
        analysis / "gate_d_exhaustive_subsample_audit_config.json"
    )
    exhaustive_config_path.write_text(
        json.dumps(exhaustive_config, sort_keys=True) + "\n"
    )
    exhaustive_scope = module.validate_exhaustive_audit_config(
        exhaustive_config, analysis
    )
    exhaustive_log = (
        analysis / "logs" / "exhaustive_subsample_coverage_audit.log"
    )
    exhaustive_log.write_text(
        "SUBSAMPLE_COVERAGE_FAILURE kind=yield flavour=BEAUTY\n"
        "SUBSAMPLE_COVERAGE_FAILURE kind=ratio flavour=CHARM\n"
        "SUBSAMPLE_COVERAGE_AUDIT_SUMMARY "
        "beauty_failures=1 charm_failures=1 total_failures=2\n"
    )
    exhaustive_result = module.validate_exhaustive_audit_log(
        exhaustive_log.read_text(), 2
    )
    statistic_lines = []
    for group in plot_scope["groups"]:
        for tune in module.TUNES:
            associates = (
                ["B-", "Lambda_b", "Sigma_b0"]
                if group["flavour"] == "BEAUTY"
                else ["D-", "Lambda_c(+)-bar"]
            )
            associate_pdgs = (
                [-521, -5122, -5212]
                if group["flavour"] == "BEAUTY"
                else [-411, -4122]
            )
            reference_pdg = (
                -521 if group["flavour"] == "BEAUTY" else -411
            )
            for associate_index, (associate, associate_pdg) in enumerate(
                zip(associates, associate_pdgs)
            ):
                statistic_lines.extend(
                    [
                        (
                            "UNCERTAINTY_MATRIX "
                            f"flavour={group['flavour']} "
                            f"trigger={group['trigger']} tune={tune} "
                            f"associate={associate} bin=hDPhiM1_10 "
                            f"associate_pdg={associate_pdg} "
                            f"reference_pdg={reference_pdg} "
                            "reference_index=0 "
                            f"is_reference={'true' if associate_index == 0 else 'false'} "
                            "finite_yields=10 yield_sem=0.01 "
                            "yield_degenerate=false yield_status=PASS "
                            + (
                                "finite_ratios=NA ratio_sem=NA "
                                "ratio_degenerate=NA "
                                "ratio_status=NOT_APPLICABLE "
                                "denominator_status=NOT_APPLICABLE "
                                if associate_index == 0
                                else (
                                    "finite_ratios=10 ratio_sem=0.02 "
                                    "ratio_degenerate=false "
                                    "ratio_status=PASS "
                                    "denominator_status=valid "
                                )
                            )
                            +
                            "status=PASS"
                        ),
                        (
                            "subsample yield stats n=10 mean=0.2 "
                            "stdDev=0.03 stdError=0.01"
                        ),
                        (
                            "subsample ratio stats "
                            "status=NOT_APPLICABLE "
                            "reason=structural_reference_self_ratio"
                            if associate_index == 0
                            else (
                                "subsample ratio stats n=10 mean=1.2 "
                                "stdDev=0.06 stdError=0.02"
                            )
                        ),
                    ]
                )
    strict_log.write_text("\n".join(statistic_lines) + "\n")
    subsample_validation = module.validate_subsample_log(
        strict_log.read_text(), plot_scope
    )
    plot_inventory = analysis / "gate_d_plot_inventory.json"
    plot_inventory.write_text(
        json.dumps(
            {
                "schema": "hf_gate_d_plot_inventory_v1",
                "pdf_count": 2,
                "png_count": 2,
                "macro_count": 2,
                "output_provenance_sidecar_count": 6,
                "run_provenance_receipt_count": 1,
                "run_provenance_receipt": {
                    "path": "plots/provenance/fixture.json",
                    "bytes": 1,
                    "sha256": "8" * 64,
                },
                "multiplicity_boundary_receipt": {
                    "path":
                        "plots/multiplicity_boundary_receipt_v1.json",
                    "bytes": 1,
                    "sha256": "9" * 64,
                },
                "files": [],
            }
        )
        + "\n"
    )
    render_inventory = analysis / "gate_d_render_inventory.json"
    render_inventory.write_text(
        json.dumps(
            {
                "schema": "hf_gate_d_render_inventory_v1",
                "source_plot_inventory_sha256": sha(plot_inventory),
                "subsample_statistic_records":
                    subsample_validation["total_statistic_records"],
                "subsample_log_validation": subsample_validation,
                "rendered_page_count": 2,
                "files": [],
            }
        )
        + "\n"
    )
    fixture_capacity = 10 * 1024**4
    fixture_available = 8 * 1024**4
    fixture_required = 123456
    fixture_minimum_remaining = max(
        int(fixture_capacity * 0.05), 500 * 1024**3
    )
    preparation = {
        "schema": "hf_publication_gate_d_preparation_v1",
        "state": "PASS",
        "canonical": True,
        "repository_commit": commit,
        "analysis_root": str(analysis),
        "production_root": str(production),
        "gate_b_report": {"path": str(gate_b), "sha256": sha(gate_b)},
        "pilot_manifest": {
            "campaign_directory": str(campaign),
            "campaign_json_sha256": sha(campaign / "campaign.json"),
            "candidate_manifest_sha256": sha(
                campaign / "candidate_manifest.jsonl"
            ),
            "seed_ledger_sha256": sha(campaign / "seed_ledger.jsonl"),
            "selected_rows": 3,
        },
        "raw_inputs": raw_bindings,
        "pair_inventory": {
            "path": str(analysis / "gate_d_pair_inventory.jsonl"),
            "sha256": "pending",
            "rows": 9900,
        },
        "plot_configuration": {
            "path": str(plot_config_path),
            "sha256": sha(plot_config_path),
            "scope": plot_scope,
        },
        "plot_outputs": {
            "inventory_path": str(plot_inventory),
            "inventory_sha256": sha(plot_inventory),
            "render_inventory_path": str(render_inventory),
            "render_inventory_sha256": sha(render_inventory),
            "multiplicity_boundary_receipt_sha256": "9" * 64,
            "output_provenance_sidecars": 6,
        },
        "exhaustive_subsample_audit": {
            "configuration": {
                "path": str(exhaustive_config_path),
                "sha256": sha(exhaustive_config_path),
                "scope": exhaustive_scope,
            },
            "result": exhaustive_result,
        },
        "commands": [
            {
                "name": "strict_coverage_and_plots",
                "returncode": 0,
                "compiler_warning_found": False,
                "log_path": str(strict_log),
                "log_bytes": strict_log.stat().st_size,
                "log_sha256": sha(strict_log),
            },
            {
                "name": "exhaustive_subsample_coverage_audit",
                "returncode": 2,
                "compiler_warning_found": False,
                "log_path": str(exhaustive_log),
                "log_bytes": exhaustive_log.stat().st_size,
                "log_sha256": sha(exhaustive_log),
            }
        ],
        "storage_projection": {
            "schema": "hf_gate_d_storage_projection_v1",
            "state": "PASS",
            "gate_e_storage_authorized": True,
            "projected_components": {
                "full_100_200_200_candidate_raw_bytes": 10000,
                "simultaneous_partial_raw_bytes": 10000,
                "canonical_300_job_per_job_analysis_bytes": 20000,
                "final_merged_central_bytes": 20000,
                "final_ten_block_bytes": 50000,
                "full_plots_logs_validation_evidence_bytes": 13456,
                "raw_filesystem_required_additional_bytes": 20000,
                "analysis_filesystem_required_additional_bytes": 103456,
                "total_required_additional_bytes": fixture_required,
            },
            "capacity_policy": {
                "maximum_fraction_of_current_available": 0.70,
                "minimum_projected_free_fraction": 0.05,
                "minimum_projected_free_bytes": 500 * 1024**3,
                "simultaneous_partial_raw_multiplier": 1,
                "full_plot_scale_factor": 10,
                "minimum_full_plot_and_evidence_bytes": 10 * 1024**3,
            },
            "preparation_capacity_check": {
                "state": "PASS",
                "capacity_source": "os.statvfs f_bavail",
                "filesystems": [
                    {
                        "state": "PASS",
                        "device_id": 1,
                        "probe_paths": [str(production), str(analysis)],
                        "roles": [
                            "analysis_and_publication_outputs",
                            "candidate_raw_and_partials",
                        ],
                        "capacity_bytes": fixture_capacity,
                        "available_bytes": fixture_available,
                        "required_additional_bytes": fixture_required,
                        "maximum_allowed_from_current_available_bytes":
                            int(fixture_available * 0.70),
                        "minimum_required_remaining_bytes":
                            fixture_minimum_remaining,
                        "projected_remaining_bytes":
                            fixture_available - fixture_required,
                    }
                ],
            },
        },
    }
    pair_inventory = analysis / "gate_d_pair_inventory.jsonl"
    pair_inventory.write_text("")
    preparation["pair_inventory"]["sha256"] = sha(pair_inventory)
    preparation_path = analysis / "gate_d_preparation_report.json"
    preparation_path.write_text(
        json.dumps(preparation, indent=2, sort_keys=True) + "\n"
    )
    preparation_hash = sha(preparation_path)

    legacy_inventory = temporary / "legacy_100m_inventory.json"
    legacy_inventory.write_text(
        json.dumps(
            {
                "schema": "legacy_fixture_inventory_v1",
                "files": [
                    {
                        "path": "legacy_complete_root_fixture.root",
                        "sha256": "a" * 64,
                    }
                ],
            },
            sort_keys=True,
        )
        + "\n"
    )
    difference_categories = sorted(module.REQUIRED_DIFFERENCES)
    comparison_rows = []
    for index, (flavour, tune) in enumerate(
        (flavour, tune)
        for flavour in ("charm", "beauty")
        for tune in module.TUNES
    ):
        legacy_value = 1.0 + 0.1 * index
        gate_d_value = legacy_value + 0.2
        absolute_difference = abs(gate_d_value - legacy_value)
        comparison_rows.append(
            {
                "flavour": flavour,
                "tune": tune,
                "observable": f"{flavour}_{tune}_balancing_yield",
                "legacy_value": legacy_value,
                "gate_d_value": gate_d_value,
                "absolute_difference": absolute_difference,
                "relative_difference":
                    absolute_difference / abs(legacy_value),
                "acceptance_tolerance": 0.01,
                "status": "EXPECTED_DIFFERENCE",
                "difference_categories": [difference_categories[index]],
                "physics_interpretation":
                    "Expected selector-definition regression difference.",
            }
        )
    comparison_artifact = temporary / "legacy_comparison_values.json"
    comparison_artifact.write_text(
        json.dumps(comparison_rows, indent=2, sort_keys=True) + "\n"
    )
    legacy = temporary / "legacy.json"
    legacy.write_text(
        json.dumps(
            {
                "schema": "hf_gate_d_legacy_comparison_v1",
                "state": "PASS",
                "repository_commit": commit,
                "gate_d_preparation_sha256": preparation_hash,
                "reviewer": "Fixture Physics Reviewer",
                "reviewed_utc": "2026-07-30T12:00:00+00:00",
                "legacy_dataset": {
                    "description": "explicit 100M fixture",
                    "inventory_path": str(legacy_inventory),
                    "inventory_sha256": sha(legacy_inventory),
                    "inventory_bytes": legacy_inventory.stat().st_size,
                    "file_count": 1,
                    "events_per_tune": 100_000_000,
                    "tunes": list(module.TUNES),
                    "provenance_status":
                        "LEGACY_INCOMPLETE_NO_SEED_METADATA",
                    "provenance_limitations": [
                        "raw_files_lack_seed_metadata",
                        "seed_uniqueness_not_provable_from_outputs",
                    ],
                },
                "comparison_artifact": {
                    "path": str(comparison_artifact),
                    "sha256": sha(comparison_artifact),
                    "bytes": comparison_artifact.stat().st_size,
                    "row_count": len(comparison_rows),
                },
                "approved_difference_categories": sorted(
                    module.REQUIRED_DIFFERENCES
                ),
                "comparison_rows": comparison_rows,
            }
        )
        + "\n"
    )
    visual = temporary / "visual.json"
    visual.write_text(
        json.dumps(
            {
                "schema": "hf_gate_d_visual_review_v1",
                "state": "PASS",
                "repository_commit": commit,
                "gate_d_preparation_sha256": preparation_hash,
                "plot_inventory_sha256": sha(plot_inventory),
                "render_inventory_sha256": sha(render_inventory),
                "pdf_count_inspected": 2,
                "reviewer": "Fixture Visual Reviewer",
                "reviewed_utc": "2026-07-30T12:30:00+00:00",
                "checks": {
                    "all_pdf_pages_inspected": True,
                    "visible_finite_error_bars": True,
                    "correct_tune_ratio_styles": True,
                    "readable_legends": True,
                    "correct_multiplicity_ordering": True,
                    "no_clipping": True,
                    "no_empty_pads": True,
                },
                "findings": [],
            }
        )
        + "\n"
    )
    return {
        "checkout": checkout,
        "commit": commit,
        "campaign": campaign,
        "production": production,
        "analysis": analysis,
        "legacy": legacy,
        "legacy_inventory": legacy_inventory,
        "comparison_artifact": comparison_artifact,
        "visual": visual,
    }


def test_filter_contract_sources() -> None:
    macro = (
        ROOT / "AnalysisScripts/status_analysis_THnSparse_qq.C"
    ).read_text()
    wrapper = (ROOT / "run_status_analysis.sh").read_text()
    pair_wrapper = (
        ROOT / "Validation/validate_pair_directory.sh"
    ).read_text()
    validator = (
        ROOT / "Validation/ValidatePairDirectory.C"
    ).read_text()
    audit = (
        ROOT / "Validation/ValidateGateDPilotAnalysis.C"
    ).read_text()
    assert "unsigned_event_id_modulo_v1" in macro
    assert "eventId %" in macro
    assert "multiplicity->Fill(eventMultiplicity, eventWeight)" in macro
    assert macro.index("eventId %") < macro.index(
        "multiplicity->Fill(eventMultiplicity, eventWeight)"
    )
    assert "HistogramsExactlyCompatible" in macro
    assert "primary_all_heavy_match_valid" in macro
    assert "HADRONIZATION_EVENT_FILTER_MODULO" in wrapper
    assert "event_filter_schema" in validator
    assert "SparseBinSumw2Digest" in validator
    assert "HistogramBinSumw2Digest" in validator
    assert "shared trigger histogram bins/Sumw2 differ" in validator
    assert "trigger_histogram_identity_comparisons=288" in pair_wrapper
    assert "multiplicity_histogram_identity_comparisons=299" in pair_wrapper
    assert "blockEventSum != centralEvents" in audit
    assert "SparseEqualsBlockSum" in audit
    assert "centralTriggerCount != ssValues.centralTriggerCount" in audit
    assert "blockTriggerCount[block] !=" in audit
    assert "independent_quadrature" in audit
    assert "baryonRatioEstimates[\"MONASH\"].find(key)" in audit
    assert "matching_associate_os=" in audit
    assert "BzeroSigmabzero.root" in audit
    runner = RUNNER.read_text()
    assert "validate_pair_inventory" in runner
    assert "len(rows) != 9900" in runner
    assert "validate_preparation_commands" in runner
    assert "hf_gate_d_storage_projection_v1" in runner
    assert "gate_e_storage_authorized" in runner
    assert "MAX_CURRENT_AVAILABLE_FRACTION = 0.70" in runner
    assert "MIN_PROJECTED_FREE_FRACTION = 0.05" in runner
    assert 'config["subsample_coverage_audit"] = False' in runner
    assert 'config["subsample_coverage_audit"] = True' in runner
    assert "validate_exhaustive_audit_log" in runner
    assert "PILOT_INSUFFICIENT_FOR_FULL_PAPER" in runner
    assert '"SUBSAMPLE_COVERAGE_FAILURE" in plot_text' in runner
    assert "structural_self_ratio_records" in runner


def test_subsample_log_contract(module) -> None:
    passing = "\n".join(
        (
            (
                "subsample yield stats n=10 mean=0.2 "
                "stdDev=0.03 stdError=0.012"
            ),
            (
                "subsample ratio stats n=10 mean=1.2 "
                "stdDev=0.02 stdError=2e-3"
            ),
        )
    )
    assert (
        module.validate_subsample_log(passing)[
            "nondegenerate_positive_sem_records"
        ]
        == 2
    )
    structural_scope = {
        "tunes": ["MONASH"],
        "groups": [
            {
                "flavour": "BEAUTY",
                "trigger": "B^{+}",
                "pair_count": 2,
                "required_multiplicity_bins": ["hDPhiM1_10"],
            }
        ],
        "expected_uncertainty_matrix_records": 2,
        "expected_statistic_records": 3,
        "expected_structural_self_ratio_records": 1,
        "expected_nondegenerate_positive_sem_records": 3,
    }
    structural = "\n".join(
        (
            (
                "UNCERTAINTY_MATRIX flavour=BEAUTY trigger=B^{+} "
                "tune=MONASH associate=Lambda_b associate_pdg=-5122 "
                "bin=hDPhiM1_10 "
                "reference_pdg=-521 reference_index=1 "
                "is_reference=false finite_yields=10 yield_sem=0.01 "
                "yield_degenerate=false yield_status=PASS "
                "finite_ratios=10 ratio_sem=0.02 "
                "ratio_degenerate=false ratio_status=PASS "
                "denominator_status=valid status=PASS"
            ),
            (
                "subsample yield stats n=10 mean=0.2 "
                "stdDev=0.03 stdError=0.01"
            ),
            (
                "subsample ratio stats n=10 mean=1.2 "
                "stdDev=0.06 stdError=0.02"
            ),
            (
                "UNCERTAINTY_MATRIX flavour=BEAUTY trigger=B^{+} "
                "tune=MONASH associate=B- associate_pdg=-521 "
                "bin=hDPhiM1_10 "
                "reference_pdg=-521 reference_index=1 "
                "is_reference=true finite_yields=10 yield_sem=0.01 "
                "yield_degenerate=false yield_status=PASS "
                "finite_ratios=NA ratio_sem=NA "
                "ratio_degenerate=NA ratio_status=NOT_APPLICABLE "
                "denominator_status=NOT_APPLICABLE status=PASS"
            ),
            (
                "subsample yield stats n=10 mean=0.3 "
                "stdDev=0.03 stdError=0.01"
            ),
            (
                "subsample ratio stats status=NOT_APPLICABLE "
                "reason=structural_reference_self_ratio"
            ),
        )
    )
    structural_result = module.validate_subsample_log(
        structural, structural_scope
    )
    assert structural_result["structural_self_ratio_records"] == 1
    missing_reference_metadata = structural.replace(
        "reference_pdg=-521 reference_index=1 is_reference=true ", ""
    )
    try:
        module.validate_subsample_log(
            missing_reference_metadata, structural_scope
        )
    except module.GateDFailure:
        pass
    else:
        raise AssertionError(
            "structural zero SEM without explicit reference metadata accepted"
        )
    numeric_self_ratio = structural.replace(
        "subsample ratio stats status=NOT_APPLICABLE "
        "reason=structural_reference_self_ratio",
        "subsample ratio stats n=10 mean=1 stdDev=0 stdError=0",
    )
    try:
        module.validate_subsample_log(numeric_self_ratio, structural_scope)
    except module.GateDFailure:
        pass
    else:
        raise AssertionError("numeric structural self-ratio was accepted")
    for invalid in (
        "subsample yield stats n=9 stdError=0.1",
        "subsample yield stats n=10 stdError=0",
        "subsample ratio stats n=10 stdError=1e-10",
        "subsample ratio stats n=10 stdError=nan",
        "SUBSAMPLE_COVERAGE_FAILURE kind=yield",
    ):
        try:
            module.validate_subsample_log(invalid)
        except module.GateDFailure:
            pass
        else:
            raise AssertionError(f"invalid subsample log accepted: {invalid}")


def test_exhaustive_subsample_audit_contract(module) -> None:
    passing = (
        "SUBSAMPLE_COVERAGE_AUDIT_SUMMARY "
        "beauty_failures=0 charm_failures=0 total_failures=0\n"
        "Subsample coverage audit passed; no canvases were drawn.\n"
    )
    result = module.validate_exhaustive_audit_log(passing, 0)
    assert result["coverage_state"] == "FULL_PAPER_SCOPE_PASS"
    assert result["publication_promotion_allowed"] is True

    insufficient = (
        "SUBSAMPLE_COVERAGE_FAILURE kind=yield flavour=BEAUTY\n"
        "SUBSAMPLE_COVERAGE_FAILURE kind=ratio flavour=CHARM\n"
        "SUBSAMPLE_COVERAGE_AUDIT_SUMMARY "
        "beauty_failures=1 charm_failures=1 total_failures=2\n"
    )
    result = module.validate_exhaustive_audit_log(insufficient, 2)
    assert result["coverage_state"] == (
        "PILOT_INSUFFICIENT_FOR_FULL_PAPER"
    )
    assert result["publication_promotion_allowed"] is False

    for text, returncode in (
        (insufficient, 0),
        (insufficient.replace("total_failures=2", "total_failures=3"), 2),
        (passing, 2),
    ):
        try:
            module.validate_exhaustive_audit_log(text, returncode)
        except module.GateDFailure:
            pass
        else:
            raise AssertionError(
                "inconsistent exhaustive subsample audit was accepted"
            )


def test_preparation_command_allows_only_classified_audit_exit(
    module, temporary: Path
) -> None:
    analysis = (temporary / "analysis").resolve()
    logs = analysis / "logs"
    logs.mkdir(parents=True)
    commands = []
    for index in range(33):
        path = logs / f"command_{index:02d}.log"
        path.write_text("PASS\n")
        commands.append(
            {
                "name": f"command_{index:02d}",
                "returncode": 0,
                "compiler_warning_found": False,
                "log_path": str(path),
                "log_bytes": path.stat().st_size,
                "log_sha256": sha(path),
            }
        )
    audit_path = logs / "exhaustive_subsample_coverage_audit.log"
    audit_path.write_text(
        "SUBSAMPLE_COVERAGE_FAILURE kind=yield flavour=BEAUTY\n"
        "SUBSAMPLE_COVERAGE_AUDIT_SUMMARY "
        "beauty_failures=1 charm_failures=0 total_failures=1\n"
    )
    audit_result = module.validate_exhaustive_audit_log(
        audit_path.read_text(), 2
    )
    commands.append(
        {
            "name": "exhaustive_subsample_coverage_audit",
            "returncode": 2,
            "compiler_warning_found": False,
            "log_path": str(audit_path),
            "log_bytes": audit_path.stat().st_size,
            "log_sha256": sha(audit_path),
        }
    )
    preparation = {
        "commands": commands,
        "exhaustive_subsample_audit": {"result": audit_result},
    }
    module.validate_preparation_commands(preparation, analysis)
    preparation["exhaustive_subsample_audit"]["result"] = {
        **audit_result,
        "total_failures": 0,
    }
    try:
        module.validate_preparation_commands(preparation, analysis)
    except module.GateDFailure:
        pass
    else:
        raise AssertionError("stale exhaustive-audit result was accepted")


def test_mutable_artifact_is_rejected(module, temporary: Path) -> None:
    analysis = temporary / "analysis"
    plots = analysis / "plots"
    plots.mkdir(parents=True)
    artifact = plots / "representative.pdf"
    artifact.write_bytes(b"original")
    inventory = {
        "files": [
            {
                "path": "plots/representative.pdf",
                "bytes": artifact.stat().st_size,
                "sha256": sha(artifact),
            }
        ]
    }
    module.validate_artifact_inventory(analysis, inventory, "plots")
    artifact.write_bytes(b"mutated")
    try:
        module.validate_artifact_inventory(analysis, inventory, "plots")
    except module.GateDFailure as error:
        assert "changed" in str(error)
    else:
        raise AssertionError("mutated plot artifact was accepted")


def test_needs_signoff_does_not_advance(module, temporary: Path) -> None:
    report = temporary / "gate_b_needs_signoff.json"
    report.write_text(
        json.dumps(
            {
                "schema": "hf_publication_gate_b_report_v1",
                "state": "NEEDS_SIGNOFF",
            }
        )
        + "\n"
    )
    try:
        module.validate_gate_b(
            report,
            {"campaign": "pilot", "campaign_ordinal": 1},
            "a" * 40,
        )
    except module.GateDFailure as error:
        assert "signoff-aware superseding Gate-B PASS" in str(error)
    else:
        raise AssertionError("NEEDS_SIGNOFF Gate B advanced into Gate D")


def test_storage_capacity_gate(module) -> None:
    gib = 1024**3
    passing = module.capacity_decision(
        capacity_bytes=10_000 * gib,
        available_bytes=5_000 * gib,
        required_bytes=1_000 * gib,
    )
    assert passing["state"] == "PASS"
    low_headroom = module.capacity_decision(
        capacity_bytes=40_000 * gib,
        available_bytes=1_600 * gib,
        required_bytes=500 * gib,
    )
    assert low_headroom["state"] == "FAIL"
    assert any(
        "5% capacity" in reason
        for reason in low_headroom["failure_reasons"]
    )
    over_fraction = module.capacity_decision(
        capacity_bytes=10_000 * gib,
        available_bytes=2_000 * gib,
        required_bytes=1_500 * gib,
    )
    assert over_fraction["state"] == "FAIL"
    assert any(
        "70%" in reason for reason in over_fraction["failure_reasons"]
    )


def test_pair_storage_inventory(module, temporary: Path) -> None:
    inventory = temporary / "gate_d_pair_inventory.jsonl"
    rows = []
    for tune_index, tune in enumerate(module.TUNES, start=1):
        central = f"complete_root_GATE_D_{tune}"
        for pair in range(300):
            rows.append(
                {
                    "path": f"{central}/pair_{pair:03d}.root",
                    "bytes": tune_index * 1000,
                    "sha256": "a" * 64,
                }
            )
        for block in range(1, 11):
            directory = (
                "SUBSAMPLES/"
                f"combined_root_subSamples_{tune}/combined_root_{block}"
            )
            for pair in range(300):
                rows.append(
                    {
                        "path": f"{directory}/pair_{pair:03d}.root",
                        "bytes": tune_index * 100 + block,
                        "sha256": "b" * 64,
                    }
                )
    inventory.write_text(
        "".join(json.dumps(row) + "\n" for row in rows)
    )
    measured = module.measure_pair_storage(temporary, inventory)
    assert measured["pilot_pair_files"] == 9900
    assert len(measured["by_tune"]) == 3
    for tune_index, tune_row in enumerate(
        measured["by_tune"], start=1
    ):
        assert tune_row["central_pair_files"] == 300
        assert tune_row["ten_block_pair_files"] == 3000
        assert tune_row["central_plus_ten_blocks_pair_files"] == 3300
        assert len(tune_row["directories"]) == 11
        assert all(
            row["pair_file_count"] == 300
            for row in tune_row["directories"]
        )
        expected = 300 * tune_index * 1000 + sum(
            300 * (tune_index * 100 + block)
            for block in range(1, 11)
        )
        assert tune_row["central_plus_ten_blocks_bytes"] == expected


def test_canonical_finalize_contract(module, temporary: Path) -> None:
    fixture = make_fixture(module, temporary)
    output = temporary / "gate_d_evidence"

    def fake_run_logged(
        arguments, log_path, *, cwd, environment=None, stdin=None
    ):
        if "gate_d_analysis_audit" in log_path.name:
            text = (
                "GATE_D_ANALYSIS_SUMMARY errors=0 "
                "central_pair_files=900 block_pair_files=9000 "
                "object_closure_checks=4500 "
                "trigger_normalization_comparisons=4950 "
                "yield_rows=900 balancing_rows=450 "
                "baryon_ratio_rows=324 "
                "independent_tune_ratio_rows=300 "
                "independent_baryon_tune_double_ratio_rows=216 "
                "finite_yield_rows=900 finite_balancing_rows=450 "
                "finite_baryon_ratio_rows=324 "
                "finite_independent_tune_ratio_rows=300 "
                "finite_independent_baryon_tune_double_ratio_rows=216 "
                "zero_yield_sem_rows=0 nonfinite_yield_rows=0 "
                "zero_balancing_sem_rows=0 "
                "nonfinite_balancing_rows=0 "
                "zero_baryon_ratio_sem_rows=0 "
                "nonfinite_baryon_ratio_rows=0 "
                "zero_baryon_ratio_denominators=0 "
                "zero_tune_ratio_error_rows=0 "
                "nonfinite_tune_ratio_rows=0 "
                "zero_baryon_tune_double_ratio_error_rows=0 "
                "nonfinite_baryon_tune_double_ratio_rows=0 "
                "bzero_sigma_filename_correct=true\n"
            )
        else:
            text = "PAIR_DIRECTORY_VALIDATION errors=0\n"
        module.exclusive_text(log_path, text)
        return {
            "name": log_path.stem,
            "started_utc": module.utc_now(),
            "finished_utc": module.utc_now(),
            "cwd": str(cwd),
            "command": list(arguments),
            "command_display": "fixture",
            "returncode": 0,
            "compiler_warning_found": False,
            "log_path": str(log_path),
            "log_bytes": log_path.stat().st_size,
            "log_sha256": sha(log_path),
        }

    original = module.run_logged
    original_pair_inventory = module.validate_pair_inventory
    original_preparation_commands = module.validate_preparation_commands
    original_artifact_inventory = module.validate_artifact_inventory
    original_storage = (
        module.validate_and_recheck_storage_projection
    )
    module.run_logged = fake_run_logged
    module.validate_pair_inventory = lambda *unused: None
    module.validate_preparation_commands = lambda *unused: None
    module.validate_artifact_inventory = lambda *unused: None
    def fake_storage(**arguments):
        stored = dict(arguments["stored"])
        prepared_filesystem = dict(
            stored["preparation_capacity_check"]["filesystems"][0]
        )
        recheck = {
            "state": "PASS",
            "checked_utc": module.utc_now(),
            "capacity_source": "os.statvfs f_bavail",
            "filesystems": [prepared_filesystem],
        }
        stored["final_capacity_recheck"] = recheck
        return stored, recheck

    module.validate_and_recheck_storage_projection = fake_storage
    try:
        arguments = argparse.Namespace(
            checkout_root=fixture["checkout"],
            output_directory=output,
            analysis_root=fixture["analysis"],
            campaign_dir=fixture["campaign"],
            legacy_comparison_report=fixture["legacy"],
            visual_review_report=fixture["visual"],
            development=False,
        )
        with contextlib.redirect_stdout(io.StringIO()):
            status = module.finalize(arguments)
    finally:
        module.run_logged = original
        module.validate_pair_inventory = original_pair_inventory
        module.validate_preparation_commands = original_preparation_commands
        module.validate_artifact_inventory = original_artifact_inventory
        module.validate_and_recheck_storage_projection = original_storage
    if status != 0:
        raise AssertionError(
            (output / "gate_d_report.json").read_text()
        )
    report = json.loads((output / "gate_d_report.json").read_text())
    assert report["schema"] == "hf_publication_gate_d_report_v1"
    assert report["state"] == "PASS"
    assert report["canonical"] is True
    assert report["repository_commit"] == fixture["commit"]
    assert report["failure"] is None
    assert len(report["requirements"]) == 13
    assert all(row["state"] == "PASS" for row in report["requirements"])
    assert report["requirements"][11]["title"] == (
        "Measured full-campaign storage projection"
    )
    assert report["requirements"][12]["title"] == (
        "Fresh finalization-time storage-capacity recheck"
    )
    assert report["commands"]
    assert all(
        row["returncode"] == 0
        and row["compiler_warning_found"] is False
        for row in report["commands"]
    )
    assert len(report["pilot_inputs"]["raw_files"]) == 3
    assert report["pilot_inputs"]["manifest"]["selected_rows"] == 3
    assert report["storage_projection"]["state"] == "PASS"
    assert (
        report["storage_projection"]["gate_e_storage_authorized"]
        is True
    )
    assert (
        report["storage_projection"]["final_capacity_recheck"]["state"]
        == "PASS"
    )
    assert (
        sha(output / report["log_path"]) == report["log_sha256"]
    )
    legacy_requirement = report["requirements"][4]["evidence"]
    for binding in legacy_requirement["immutable_snapshots"].values():
        snapshot = output / binding["path"]
        assert snapshot.is_file()
        assert snapshot.stat().st_size == binding["bytes"]
        assert sha(snapshot) == binding["sha256"]
    visual_binding = report["requirements"][10]["evidence"][
        "immutable_snapshot"
    ]
    assert sha(output / visual_binding["path"]) == visual_binding["sha256"]
    assert (
        report["requirements"][11]["evidence"]["state"] == "PASS"
    )
    assert (
        report["requirements"][12]["evidence"]["state"] == "PASS"
    )
    assert not output.stat().st_mode & 0o200


def test_missing_visual_evidence_fails(module, temporary: Path) -> None:
    fixture = make_fixture(module, temporary)
    Path(fixture["visual"]).unlink()
    try:
        module.validate_visual_report(
            Path(fixture["visual"]),
            str(fixture["commit"]),
            sha(
                Path(fixture["analysis"])
                / "gate_d_preparation_report.json"
            ),
            sha(Path(fixture["analysis"]) / "gate_d_plot_inventory.json"),
            sha(
                Path(fixture["analysis"])
                / "gate_d_render_inventory.json"
            ),
            2,
        )
    except module.GateDFailure as error:
        assert "absent" in str(error)
    else:
        raise AssertionError("missing human visual review was accepted")


def test_stale_legacy_evidence_fails(module, temporary: Path) -> None:
    fixture = make_fixture(module, temporary)
    Path(fixture["legacy_inventory"]).write_text("tampered\n")
    preparation = (
        Path(fixture["analysis"]) / "gate_d_preparation_report.json"
    )
    try:
        module.validate_legacy_report(
            Path(fixture["legacy"]),
            str(fixture["commit"]),
            sha(preparation),
        )
    except module.GateDFailure as error:
        assert "absent or stale" in str(error)
    else:
        raise AssertionError("stale legacy inventory was accepted")


def main() -> None:
    module = load_runner()
    test_filter_contract_sources()
    test_subsample_log_contract(module)
    test_exhaustive_subsample_audit_contract(module)
    test_storage_capacity_gate(module)
    with tempfile.TemporaryDirectory() as directory:
        test_preparation_command_allows_only_classified_audit_exit(
            module, Path(directory)
        )
    with tempfile.TemporaryDirectory() as directory:
        test_pair_storage_inventory(module, Path(directory))
    with tempfile.TemporaryDirectory() as directory:
        test_mutable_artifact_is_rejected(module, Path(directory))
    with tempfile.TemporaryDirectory() as directory:
        test_needs_signoff_does_not_advance(module, Path(directory))
    with tempfile.TemporaryDirectory() as directory:
        test_canonical_finalize_contract(module, Path(directory))
    with tempfile.TemporaryDirectory() as directory:
        test_missing_visual_evidence_fails(module, Path(directory))
    with tempfile.TemporaryDirectory() as directory:
        test_stale_legacy_evidence_fails(module, Path(directory))
    print("publication Gate-D tests passed")


if __name__ == "__main__":
    main()
