#!/usr/bin/env python3
"""Synthetic fail-closed tests for final-plot provenance receipts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "final_plot_provenance.py"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


def load_tool_module():
    specification = importlib.util.spec_from_file_location(
        "final_plot_provenance_under_test", TOOL
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*arguments: str, expected: int = 0) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [sys.executable, str(TOOL), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != expected:
        raise AssertionError(
            f"status={result.returncode}, expected={expected}\n{result.stdout}"
        )
    return result


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def seal_boundary_receipt(receipt: dict) -> None:
    receipt.pop("payload_sha256", None)
    payload = json.dumps(
        receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    receipt["payload_sha256"] = hashlib.sha256(payload).hexdigest()


def initialize_checkout(path: Path) -> str:
    for relative in (
        "PlottingScripts/TunePlotStyle.h",
        "PlottingScripts/improvedPlotting_THnSparse.C",
        "PlottingScripts/MultiplicityBoundaryUtils.h",
        "PlottingScripts/PairInputSelectionUtils.h",
    ):
        target = path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"// {relative}\n")
    (path / ".gitignore").write_text("plots/\n")
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Plot Provenance Test"],
        cwd=path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "plot@example.invalid"],
        cwd=path,
        check=True,
    )
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "fixture"], cwd=path, check=True
    )
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=path, text=True
    ).strip()


def canonical_rows(commit: str) -> list[dict]:
    rows = []
    for tune in TUNES:
        for slot in range(100):
            rows.append(
                {
                    "schema": "hf_canonical_raw_manifest_v2",
                    "campaign": "fixture",
                    "tune": tune,
                    "canonical_slot": slot,
                    "block": slot % 10,
                    "repository_commit": commit,
                }
            )
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )


def make_merge(
    directory: Path,
    tune: str,
    source_manifest: Path,
    analysis_commit: str,
    input_count: int,
) -> None:
    directory.mkdir(parents=True)
    root_rows = []
    for name in ("beauty.root", "charm.root"):
        path = directory / name
        path.write_text(f"{tune}:{directory.name}:{name}\n")
        root_rows.append(
            {
                "path": name,
                "bytes": path.stat().st_size,
                "sha256": sha(path),
            }
        )
    (directory / "source_manifest.jsonl").write_bytes(
        source_manifest.read_bytes()
    )
    write_json(
        directory / "merge_provenance.json",
        {
            "schema": "hf_merged_pair_directory_provenance_v2",
            "status": "PASS",
            "tune": tune,
            "source_manifest_sha256": sha(source_manifest),
            "merge_input_file_count": input_count,
            "analysis_commit": analysis_commit,
            "repository_commit": analysis_commit,
        },
    )
    write_json(
        directory / "merged_pair_checksums.json",
        {
            "schema": "hf_merged_pair_checksum_inventory_v1",
            "pair_file_count": 2,
            "files": root_rows,
        },
    )


def fixture(base: Path) -> dict[str, Path | str]:
    checkout = base / "checkout"
    checkout.mkdir()
    commit = initialize_checkout(checkout)
    freeze = checkout / "Production/fixture/freeze"
    rows = canonical_rows(commit)
    manifest = freeze / "canonical_manifest.jsonl"
    write_jsonl(manifest, rows)
    blocks = []
    for block in range(10):
        path = freeze / f"block_{block + 1:02d}.jsonl"
        write_jsonl(path, [row for row in rows if row["block"] == block])
        blocks.append(path)
    validation_log = freeze / "canonical_raw_validation.log"
    validation_log.write_text(
        "CANONICAL_RAW_VALIDATION errors=0 files=300\n"
    )
    validation_receipt = freeze / "canonical_raw_validation_receipt.json"
    write_json(
        validation_receipt,
        {
            "schema": "hf_canonical_raw_validation_receipt_v2",
            "state": "PASS",
            "canonical_manifest_sha256": sha(manifest),
            "validation_log_sha256": sha(validation_log),
        },
    )
    summary = freeze / "freeze_summary.json"
    write_json(
        summary,
        {
            "schema": "hf_canonical_freeze_summary_v3",
            "campaign": "fixture",
            "campaign_ordinal": 1,
            "canonical_manifest_sha256": sha(manifest),
            "jobs_per_tune": 100,
        },
    )
    seal = freeze / "freeze_seal.json"
    write_json(
        seal,
        {
            "schema": "hf_canonical_freeze_seal_v2",
            "state": "SEALED",
            "canonical_manifest_sha256": sha(manifest),
            "validation_receipt_path":
                "canonical_raw_validation_receipt.json",
            "validation_receipt_sha256": sha(validation_receipt),
            "validation_log_path": "canonical_raw_validation.log",
            "validation_log_sha256": sha(validation_log),
        },
    )

    analyzed = base / "analyzed"
    block_base = analyzed / "SUBSAMPLES" / "combined_root_subSamples"
    for tune in TUNES:
        make_merge(
            analyzed / f"complete_root_FINAL_{tune}",
            tune,
            manifest,
            commit,
            100,
        )
        for block, block_manifest in enumerate(blocks, start=1):
            make_merge(
                Path(f"{block_base}_{tune}") / f"combined_root_{block}",
                tune,
                block_manifest,
                commit,
                10,
            )

    plots = checkout / "plots"
    config = base / "plot.json"
    write_json(
        config,
        {
            "base_dir": str(analyzed),
            "bb_bar_complete_root_dir": "complete_root_FINAL",
            "cc_bar_complete_root_dir": "complete_root_FINAL",
            "bb_bar_complete_root_dir_sub_samples": str(block_base),
            "cc_bar_complete_root_dir_sub_samples": str(block_base),
            "nSubSamples": 10,
            "calculate_errors": True,
            "pair_combinatorics_mode": "ordered_conditional_v1",
            "same_sign_pair_factor": 1.0,
            "pair_input_selection_contract": {
                "mode": "v2_metadata_only_v1",
                "v2_analysis_schema": "paul_pair_objects_primary_ground_v2",
                "v2_selector_version":
                    "hard_trigger_primary_ground__primary_ground_associate_v1",
                "v2_trigger_pt_min_exclusive": 1.0,
                "v2_associate_pt_min_exclusive": 0.15,
                "v2_eta_abs_max_inclusive": 4.0,
            },
            "PYTHIA_TUNES": list(TUNES),
            "histograms_to_analyse": [
                {
                    "hDPhi": "hDPhiM1_10",
                    "multiplicityMin": 1,
                    "multiplicityMax": 10,
                }
            ],
            "beauty_correlations_to_analyse": [
                {
                    "trigger": "B+",
                    "configs": [
                        {"OS": "beauty.root", "SS": "beauty.root"}
                    ],
                }
            ],
            "charm_correlations_to_analyse": [
                {
                    "trigger": "D+",
                    "configs": [
                        {"OS": "charm.root", "SS": "charm.root"}
                    ],
                }
            ],
            "draw_correlation_plots": False,
            "canvases_to_be_drawn": [],
            "global_canvases_to_be_drawn": [
                {
                    "write": True,
                    "write_path": str(plots),
                    "write_name": "global",
                }
            ],
        },
    )
    evidence = checkout / "AnalysisResults/fixture"
    origin = evidence / "final_origin_closure_report_v1.json"
    origin_payload = {
        "schema": "hf_final_origin_closure_report_v1",
        "completion_state": "PASS",
        "publication_readiness": "READY",
        "canonical_manifest_sha256": sha(manifest),
        "freeze_seal_sha256": sha(seal),
        "jobs_per_tune": 100,
        "audited_job_count": 300,
        "unresolved_trigger_candidate_count": 0,
        "origin_summary": [{"role": 1, "candidates": 1}],
        "primary_all_heavy_closure": [
            {"denominator_count": 1, "count": 1}
        ],
    }
    origin_payload["payload_sha256"] = hashlib.sha256(
        json.dumps(
            origin_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()
    write_json(origin, origin_payload)
    robustness = evidence / "statistical_robustness_report_v1.json"
    robustness_payload = {
        "schema": "hf_statistical_robustness_report_v1",
        "completion_state": "DESCRIPTIVE_CROSS_CHECK_COMPLETE",
        "publication_decision":
            "NOT_EVALUATED_NO_PREDECLARED_AGREEMENT_THRESHOLD",
        "specification_sha256": "f" * 64,
        "canonical_provenance": {
            "canonical_manifest_sha256": sha(manifest),
            "freeze_seal_sha256": sha(seal),
        },
        "final_origin_closure_report": {"sha256": sha(origin)},
        "results": [{"quantity": "fixture"}],
    }
    robustness_payload["payload_sha256"] = hashlib.sha256(
        json.dumps(
            robustness_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()
    write_json(robustness, robustness_payload)
    review = evidence / "FINAL_SCIENTIFIC_REVIEW.json"
    review_payload = {
        "schema": "hf_final_scientific_review_v1",
        "decision": "APPROVE_PUBLICATION_DATASET",
        "approved": True,
        "reviewer": "Fixture Scientific Reviewer",
        "reviewer_role": "designated_physics_statistics_reviewer",
        "decision_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": "fixture",
        "canonical_manifest_sha256": sha(manifest),
        "freeze_seal_sha256": sha(seal),
        "final_origin_closure_sha256": sha(origin),
        "statistical_robustness_sha256": sha(robustness),
        "statistical_specification_sha256": "f" * 64,
        "fixed_nch_definition_reviewed": True,
        "species_registry_disposition_reviewed": True,
        "paper_claim_scope_reviewed": True,
        "blocking_findings": [],
    }
    review_payload["payload_sha256"] = hashlib.sha256(
        json.dumps(
            review_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()
    write_json(review, review_payload)
    os.chmod(review, 0o444)
    authorization = (
        checkout / "campaigns/fixture/"
        "PUBLICATION_DATASET_AUTHORIZATION.json"
    )
    bound_paths = {
        "canonical_manifest": manifest,
        "freeze_summary": summary,
        "freeze_seal": seal,
        "canonical_validation_receipt": validation_receipt,
        "canonical_validation_log": validation_log,
        "final_origin_closure": origin,
        "statistical_robustness": robustness,
        "final_scientific_review": review,
    }
    authorization_payload = {
        "schema": "hf_publication_dataset_eligibility_v1",
        "state": "PASS",
        "publication_eligible": True,
        "dataset_id": "final",
        "campaign": "fixture",
        "repository_commit": commit,
        "approved": True,
        "approved_by": "Fixture Project Owner",
        "approver_role": "project_owner",
        "approved_utc": datetime.now(timezone.utc).isoformat(),
        "blocking_findings": [],
        **{
            name: {
                "path": path.relative_to(checkout).as_posix(),
                "sha256": sha(path),
            }
            for name, path in bound_paths.items()
        },
    }
    authorization_payload["payload_sha256"] = hashlib.sha256(
        json.dumps(
            authorization_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()
    write_json(authorization, authorization_payload)
    os.chmod(authorization, 0o444)

    selector = base / "selector.json"
    write_json(
        selector,
        {
            "schema": "hadronization_dataset_selector_v1",
            "active_dataset": "final",
            "datasets": {
                "final": {
                    "status": "canonical",
                    "publication_eligible": True,
                    "raw_schema": "hf_primary_ground_raw_v5",
                    "selector":
                        "hard_trigger_primary_ground__primary_ground_associate_v1",
                    "campaign": "fixture",
                    "canonical_manifest":
                        manifest.relative_to(checkout).as_posix(),
                    "production_root": "Production/fixture",
                    "analysis_root": "AnalysisOutput/fixture",
                    "raw_base": "Production/fixture",
                    "analyzed_data_base": str(analyzed),
                    "complete_root_tag": "complete_root_FINAL",
                    "subsample_base": str(block_base),
                    "block_count": 10,
                    "publication_authorization":
                        authorization.relative_to(checkout).as_posix(),
                    "publication_authorization_sha256":
                        sha(authorization),
                    "interpretation": "fixture",
                }
            },
        },
    )
    source_by_tune = {
        tune: analyzed / f"complete_root_FINAL_{tune}" / "beauty.root"
        for tune in TUNES
    }
    receipt = {
        "schema": "hadronization_multiplicity_boundary_receipt_v1",
        "schema_version": 1,
        "algorithm": "ascending_discrete_weighted_quantile_v1",
        "completion_status": "PASS",
        "configuration_path": str(config.resolve()),
        "configuration_sha256": sha(config),
        "plotter_source_sha256": sha(
            checkout / "PlottingScripts/improvedPlotting_THnSparse.C"
        ),
        "boundary_utility_sha256": sha(
            checkout / "PlottingScripts/MultiplicityBoundaryUtils.h"
        ),
        "tunes": {
            tune: {
                "central_reference_path": str(path),
                "central_source_file_sha256": sha(path),
            }
            for tune, path in source_by_tune.items()
        },
    }
    seal_boundary_receipt(receipt)
    plots.mkdir(parents=True)
    write_json(plots / "multiplicity_boundary_receipt_v1.json", receipt)
    return {
        "checkout": checkout,
        "config": config,
        "selector": selector,
        "plots": plots,
        "manifest": manifest,
    }


def write_triplet(directory: Path, stem: str, *, omit_macro: bool = False) -> None:
    (directory / f"{stem}_PDF.pdf").write_bytes(b"%PDF fixture\n")
    (directory / f"{stem}_PNG.png").write_bytes(b"\x89PNG fixture\n")
    if not omit_macro:
        (directory / f"{stem}_MACRO.C").write_text("// ROOT macro\n")


def canonical_record(
    fix: dict[str, Path | str],
    state: Path,
    *,
    mode: str = "canonical-pair",
    expected: int = 0,
) -> subprocess.CompletedProcess:
    return run(
        "record",
        "--checkout",
        str(fix["checkout"]),
        "--state",
        str(state),
        "--target",
        "thnsparse",
        "--command",
        "./PlottingScripts/run_paper_plots.sh thnsparse",
        "--mode",
        mode,
        "--selector",
        str(fix["selector"]),
        "--config",
        str(fix["config"]),
        "--require-boundary-receipt",
        expected=expected,
    )


def test_success_and_tamper(base: Path) -> None:
    fix = fixture(base)
    state = base / "snapshot.json"
    run(
        "snapshot",
        "--checkout",
        str(fix["checkout"]),
        "--state",
        str(state),
        "--config",
        str(fix["config"]),
    )
    write_triplet(fix["plots"], "global")
    result = canonical_record(fix, state)
    assert "publication_eligible=true" in result.stdout
    sidecar = Path(f"{fix['plots'] / 'global_PDF.pdf'}.provenance.json")
    payload = json.loads(sidecar.read_text())
    assert payload["schema"] == "hf_final_plot_provenance_v1"
    assert len(payload["block_manifests"]) == 10
    assert payload["multiplicity_boundary_receipt"]["sha256"]
    assert payload["selection_cut_schema_versions"][
        "multiplicity_classes"
    ] == [
        {
            "name": "hDPhiM1_10",
            "minimum": 1,
            "maximum": 10,
        }
    ]
    run(
        "verify",
        "--checkout",
        str(fix["checkout"]),
        "--sidecar",
        str(sidecar),
    )
    (fix["plots"] / "global_PDF.pdf").write_bytes(b"tampered\n")
    result = run(
        "verify",
        "--checkout",
        str(fix["checkout"]),
        "--sidecar",
        str(sidecar),
        expected=2,
    )
    assert "checksum/size differs" in result.stdout


def test_multiplicity_key_compatibility() -> None:
    tool = load_tool_module()
    dataset = {
        "raw_schema": "hf_primary_ground_raw_v5",
        "selector": (
            "hard_trigger_primary_ground__primary_ground_associate_v1"
        ),
    }
    common = {
        "histograms_to_analyse": [
            {
                "hDPhi": "hDPhiM90_100",
                "multiplicity_min": 90,
                "multiplicity_max": 100,
            }
        ]
    }
    legacy_contract = tool.contract_binding(
        "canonical-pair", dataset, common
    )
    assert legacy_contract["multiplicity_classes"] == [
        {
            "name": "hDPhiM90_100",
            "minimum": 90,
            "maximum": 100,
        }
    ]

    common["histograms_to_analyse"][0].update(
        {"multiplicityMin": 80, "multiplicityMax": 100}
    )
    try:
        tool.contract_binding("canonical-pair", dataset, common)
    except tool.ProvenanceFailure as error:
        assert "conflicting multiplicity range values" in str(error)
    else:
        raise AssertionError(
            "conflicting canonical/compatibility multiplicity keys passed"
        )


def test_canonical_candidate_is_ineligible(base: Path) -> None:
    fix = fixture(base)
    selector_path = Path(fix["selector"])
    selector = json.loads(selector_path.read_text())
    row = selector["datasets"]["final"]
    row["status"] = "canonical_candidate"
    row["publication_eligible"] = False
    row["publication_authorization"] = None
    row["publication_authorization_sha256"] = None
    write_json(selector_path, selector)
    state = base / "candidate_snapshot.json"
    run(
        "snapshot",
        "--checkout",
        str(fix["checkout"]),
        "--state",
        str(state),
        "--config",
        str(fix["config"]),
    )
    write_triplet(fix["plots"], "candidate")
    result = canonical_record(
        fix, state, mode="canonical-validation-pair"
    )
    assert "publication_eligible=false" in result.stdout
    sidecar = Path(
        f"{fix['plots'] / 'candidate_PDF.pdf'}.provenance.json"
    )
    payload = json.loads(sidecar.read_text())
    assert payload["publication_eligible"] is False
    receipt_path = Path(payload["run_receipt"]["path"])
    if not receipt_path.is_absolute():
        receipt_path = Path(fix["checkout"]) / receipt_path
    receipt = json.loads(receipt_path.read_text())
    assert "Prepublication canonical validation" in (
        receipt["inputs"]["publication_limitation"]
    )
    run(
        "verify",
        "--checkout",
        str(fix["checkout"]),
        "--sidecar",
        str(sidecar),
    )


def test_missing_triplet(base: Path) -> None:
    fix = fixture(base)
    state = base / "snapshot.json"
    run(
        "snapshot",
        "--checkout",
        str(fix["checkout"]),
        "--state",
        str(state),
        "--config",
        str(fix["config"]),
    )
    write_triplet(fix["plots"], "incomplete", omit_macro=True)
    result = run(
        "record",
        "--checkout",
        str(fix["checkout"]),
        "--state",
        str(state),
        "--target",
        "thnsparse",
        "--command",
        "fixture",
        "--mode",
        "canonical-pair",
        "--selector",
        str(fix["selector"]),
        "--config",
        str(fix["config"]),
        "--require-boundary-receipt",
        expected=2,
    )
    assert "representations are incomplete" in result.stdout


def test_missing_manifest(base: Path) -> None:
    fix = fixture(base)
    state = base / "snapshot.json"
    run(
        "snapshot",
        "--checkout",
        str(fix["checkout"]),
        "--state",
        str(state),
        "--config",
        str(fix["config"]),
    )
    write_triplet(fix["plots"], "global")
    Path(fix["manifest"]).with_name("block_04.jsonl").unlink()
    result = run(
        "record",
        "--checkout",
        str(fix["checkout"]),
        "--state",
        str(state),
        "--target",
        "thnsparse",
        "--command",
        "fixture",
        "--mode",
        "canonical-pair",
        "--selector",
        str(fix["selector"]),
        "--config",
        str(fix["config"]),
        "--require-boundary-receipt",
        expected=2,
    )
    assert "block_04" in result.stdout and "absent/not regular" in result.stdout


def test_boundary_payload_tamper(base: Path) -> None:
    fix = fixture(base)
    receipt_path = (
        Path(fix["plots"]) / "multiplicity_boundary_receipt_v1.json"
    )
    receipt = json.loads(receipt_path.read_text())
    receipt["tunes"]["MONASH"]["central_source_file_sha256"] = "0" * 64
    write_json(receipt_path, receipt)
    state = base / "snapshot.json"
    run(
        "snapshot",
        "--checkout",
        str(fix["checkout"]),
        "--state",
        str(state),
        "--config",
        str(fix["config"]),
    )
    write_triplet(Path(fix["plots"]), "global")
    result = canonical_record(fix, state, expected=2)
    assert "receipt is incomplete/stale" in result.stdout


def test_legacy_is_honestly_ineligible(base: Path) -> None:
    fix = fixture(base)
    selector = json.loads(Path(fix["selector"]).read_text())
    row = selector["datasets"]["final"]
    row.update(
        {
            "status": "legacy_regression_default",
            "publication_eligible": False,
            "raw_schema": "legacy_status_unknown",
            "selector": "legacy_status",
            "campaign": None,
            "canonical_manifest": None,
            "production_root": None,
            "analysis_root": None,
            "publication_authorization": None,
            "publication_authorization_sha256": None,
        }
    )
    write_json(Path(fix["selector"]), selector)
    config = json.loads(Path(fix["config"]).read_text())
    config["pair_combinatorics_mode"] = "legacy_identical_ss_half_v1"
    config["same_sign_pair_factor"] = 0.5
    config["pair_input_selection_contract"]["mode"] = (
        "tagged_legacy_recuts_only_v1"
    )
    write_json(Path(fix["config"]), config)
    receipt_path = (
        Path(fix["plots"]) / "multiplicity_boundary_receipt_v1.json"
    )
    receipt = json.loads(receipt_path.read_text())
    receipt["configuration_sha256"] = sha(Path(fix["config"]))
    seal_boundary_receipt(receipt)
    write_json(receipt_path, receipt)

    state = base / "snapshot.json"
    run(
        "snapshot",
        "--checkout",
        str(fix["checkout"]),
        "--state",
        str(state),
        "--config",
        str(fix["config"]),
    )
    write_triplet(Path(fix["plots"]), "legacy")
    run(
        "record",
        "--checkout",
        str(fix["checkout"]),
        "--state",
        str(state),
        "--target",
        "legacy-regression",
        "--command",
        "./PlottingScripts/run_paper_plots.sh legacy-regression",
        "--mode",
        "legacy-pair",
        "--selector",
        str(fix["selector"]),
        "--config",
        str(fix["config"]),
        "--require-boundary-receipt",
    )
    sidecar = Path(f"{fix['plots'] / 'legacy_PDF.pdf'}.provenance.json")
    payload = json.loads(sidecar.read_text())
    assert payload["publication_eligible"] is False
    assert (
        payload["canonical_manifest"]["status"]
        == "NOT_AVAILABLE_FOR_LEGACY_INPUT"
    )
    assert all(
        row["status"] == "NOT_AVAILABLE_FOR_LEGACY_INPUT"
        for row in payload["block_manifests"]
    )


def test_runner_and_gate_d_are_wrapped() -> None:
    runner = (ROOT / "PlottingScripts" / "run_paper_plots.sh").read_text()
    gate_d = (ROOT / "tools" / "run_publication_gate_d.py").read_text()
    required_runner = (
        'plot_provenance_tool="${project_base}/tools/final_plot_provenance.py"',
        "snapshot_arguments=(",
        "record_arguments=(",
        'canonical_pair_provenance_mode="canonical-pair"',
        'canonical_pair_provenance_mode="canonical-validation-pair"',
        'canonical_raw_provenance_mode="canonical-raw"',
        'canonical_raw_provenance_mode="canonical-validation-raw"',
        'provenance_mode="legacy-pair"',
        "--require-boundary-receipt",
    )
    for fragment in required_runner:
        assert fragment in runner, fragment
    required_gate_d = (
        '"plot_provenance_snapshot"',
        '"final_plot_provenance"',
        '"--pair-inventory"',
        '"--pilot-manifest"',
        '"--require-boundary-receipt"',
        '"output_provenance_sidecar_count"',
        '"multiplicity_boundary_receipt"',
    )
    for fragment in required_gate_d:
        assert fragment in gate_d, fragment


def main() -> int:
    test_runner_and_gate_d_are_wrapped()
    test_multiplicity_key_compatibility()
    with tempfile.TemporaryDirectory(prefix="plot_provenance_success_") as tmp:
        test_success_and_tamper(Path(tmp))
    with tempfile.TemporaryDirectory(
        prefix="plot_provenance_candidate_"
    ) as tmp:
        test_canonical_candidate_is_ineligible(Path(tmp))
    with tempfile.TemporaryDirectory(prefix="plot_provenance_missing_output_") as tmp:
        test_missing_triplet(Path(tmp))
    with tempfile.TemporaryDirectory(prefix="plot_provenance_missing_manifest_") as tmp:
        test_missing_manifest(Path(tmp))
    with tempfile.TemporaryDirectory(prefix="plot_provenance_boundary_tamper_") as tmp:
        test_boundary_payload_tamper(Path(tmp))
    with tempfile.TemporaryDirectory(prefix="plot_provenance_legacy_") as tmp:
        test_legacy_is_honestly_ineligible(Path(tmp))
    print("final plot provenance tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
