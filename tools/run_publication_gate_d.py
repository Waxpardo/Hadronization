#!/usr/bin/env python3
"""Prepare and certify the Section-16 Gate-D analysis smoke test.

``prepare`` creates the central and ten deterministic event-ID-modulo
analyses for each one-million-event Gate-B central pilot, runs strict plotting
coverage, executes the full-paper exhaustive coverage audit as a fail-closed
production-sizing diagnostic, and renders the generated PDFs.  It never
claims human visual inspection or legacy agreement.

``finalize`` revalidates those artifacts and requires explicit, checksum-bound
legacy-comparison and human visual-review reports.  Only finalize can emit the
immutable ``hf_publication_gate_d_report_v1`` accepted by the full-production
authorization contract.  Both stages fail closed on a measured, conservative
storage projection covering the 100/200/200 raw campaign, simultaneous
partials, all canonical per-job analyses, merged central/block outputs, and
publication artifacts.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import re
import shlex
import stat
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
PREPARATION_SCHEMA = "hf_publication_gate_d_preparation_v1"
REPORT_SCHEMA = "hf_publication_gate_d_report_v1"
INVENTORY_SCHEMA = "hf_publication_gate_d_inventory_v1"
STORAGE_SCHEMA = "hf_gate_d_storage_projection_v1"
VISUAL_SCHEMA = "hf_gate_d_visual_review_v1"
LEGACY_SCHEMA = "hf_gate_d_legacy_comparison_v1"
EXHAUSTIVE_AUDIT_SCHEMA = "hf_gate_d_exhaustive_subsample_audit_v1"
GATE_B_SCHEMA = "hf_publication_gate_b_report_v1"
CAMPAIGN_SCHEMA = "hf_gate_b_pilot_campaign_v1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ANALYSIS_SUMMARY = re.compile(
    r"^GATE_D_ANALYSIS_SUMMARY errors=0 "
    r"central_pair_files=900 block_pair_files=9000 "
    r"object_closure_checks=4500 "
    r"trigger_normalization_comparisons=4950 "
    r"yield_rows=900 balancing_rows=450 baryon_ratio_rows=324 "
    r"independent_tune_ratio_rows=300 "
    r"independent_baryon_tune_double_ratio_rows=216 "
    r"finite_yield_rows=(\d+) finite_balancing_rows=(\d+) "
    r"finite_baryon_ratio_rows=(\d+) "
    r"finite_independent_tune_ratio_rows=(\d+) "
    r"finite_independent_baryon_tune_double_ratio_rows=(\d+) "
    r"zero_yield_sem_rows=(\d+) nonfinite_yield_rows=(\d+) "
    r"zero_balancing_sem_rows=(\d+) nonfinite_balancing_rows=(\d+) "
    r"zero_baryon_ratio_sem_rows=(\d+) "
    r"nonfinite_baryon_ratio_rows=(\d+) "
    r"zero_baryon_ratio_denominators=(\d+) "
    r"zero_tune_ratio_error_rows=(\d+) "
    r"nonfinite_tune_ratio_rows=(\d+) "
    r"zero_baryon_tune_double_ratio_error_rows=(\d+) "
    r"nonfinite_baryon_tune_double_ratio_rows=(\d+) "
    r"bzero_sigma_filename_correct=true\s*$",
    flags=re.MULTILINE,
)
EXHAUSTIVE_AUDIT_SUMMARY = re.compile(
    r"^SUBSAMPLE_COVERAGE_AUDIT_SUMMARY "
    r"beauty_failures=(\d+) charm_failures=(\d+) "
    r"total_failures=(\d+)\s*$",
    flags=re.MULTILINE,
)
REQUIRED_DIFFERENCES = {
    "heavy_stabilization",
    "hard_origin_matching",
    "signed_species_registry",
    "role_dependent_thresholds",
    "charge_resolved_ordered_pairs",
    "same_sign_factor_removed",
}
MAX_CURRENT_AVAILABLE_FRACTION = 0.70
MIN_PROJECTED_FREE_FRACTION = 0.05
MIN_PROJECTED_FREE_BYTES = 500 * 1024**3
CONCURRENT_PARTIAL_RAW_MULTIPLIER = 1
FULL_PLOT_SCALE_FACTOR = 10
MIN_FULL_PLOT_AND_EVIDENCE_BYTES = 10 * 1024**3


class GateDFailure(ValueError):
    """Fail-closed Gate-D validation failure."""


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="seconds"
    )


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise GateDFailure(f"{label} is absent or not a regular file: {path}")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise GateDFailure(f"{label} is not valid JSON: {path}") from error
    if not isinstance(value, dict):
        raise GateDFailure(f"{label} must contain one JSON object")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if path.is_symlink() or not path.is_file():
        raise GateDFailure(f"manifest is absent or not regular: {path}")
    rows = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise GateDFailure(
                f"invalid JSON manifest row {number}: {path}"
            ) from error
        if not isinstance(row, dict):
            raise GateDFailure(f"manifest row {number} is not an object")
        rows.append(row)
    return rows


def git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *arguments], text=True
    ).strip()


def validate_checkout(root: Path, development: bool) -> dict[str, Any]:
    commit = git(root, "rev-parse", "HEAD")
    if not HEX40.fullmatch(commit):
        raise GateDFailure("checkout does not resolve to a full commit")
    status = git(
        root, "status", "--porcelain=v1", "--untracked-files=all"
    )
    if not development and status:
        raise GateDFailure(
            "canonical Gate D requires a completely clean checkout"
        )
    return {
        "repository_root": str(root),
        "repository_commit": commit,
        "repository_tree": git(root, "rev-parse", "HEAD^{tree}"),
        "branch": git(root, "branch", "--show-current"),
        "origin": git(root, "remote", "get-url", "origin"),
        "initial_status": status,
        "canonical": not development,
    }


def exclusive_text(path: Path, text: str, mode: int = 0o444) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        raise


def exclusive_bytes(path: Path, payload: bytes, mode: int = 0o444) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def run_logged(
    arguments: Sequence[str],
    log_path: Path,
    *,
    cwd: Path,
    environment: dict[str, str] | None = None,
    stdin: str | None = None,
) -> dict[str, Any]:
    started = utc_now()
    result = subprocess.run(
        list(arguments),
        cwd=cwd,
        env=environment,
        input=stdin,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = result.stdout or ""
    exclusive_text(log_path, output)
    lowered = output.lower()
    warning = bool(
        re.search(r"(^|\s)warning:", output, flags=re.IGNORECASE)
        or "cling jit session error" in lowered
    )
    return {
        "name": log_path.stem,
        "started_utc": started,
        "finished_utc": utc_now(),
        "cwd": str(cwd),
        "command": list(arguments),
        "command_display": shlex.join(arguments),
        "returncode": result.returncode,
        "compiler_warning_found": warning,
        "log_path": str(log_path),
        "log_bytes": log_path.stat().st_size,
        "log_sha256": sha256(log_path),
    }


def validate_gate_b(
    report_path: Path, campaign: dict[str, Any], commit: str
) -> dict[str, Any]:
    report = load_json(report_path, "Gate-B report")
    if report.get("state") == "NEEDS_SIGNOFF":
        raise GateDFailure(
            "Gate B is NEEDS_SIGNOFF because unresolved trigger candidates "
            "were observed. Gate D will not infer approval from a separate "
            "file or mutate that decision; a project-owner-reviewed, "
            "signoff-aware superseding Gate-B PASS artifact is required."
        )
    expected = {
        "schema": GATE_B_SCHEMA,
        "state": "PASS",
        "canonical": True,
        "repository_commit": commit,
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
    }
    for key, value in expected.items():
        if report.get(key) != value:
            raise GateDFailure(
                f"Gate-B report {key} differs: "
                f"{report.get(key)!r} != {value!r}"
            )
    raw = report.get("raw_validation_evidence")
    if not isinstance(raw, list) or len(raw) != 9:
        raise GateDFailure("Gate-B report lacks nine raw validation records")
    return report


def validate_campaign(
    campaign_dir: Path,
    gate_b_report: Path,
    commit: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    campaign = load_json(campaign_dir / "campaign.json", "Gate-B campaign")
    rows = load_jsonl(campaign_dir / "candidate_manifest.jsonl")
    if (
        campaign.get("schema") != CAMPAIGN_SCHEMA
        or campaign.get("repository_implementation_commit") != commit
        or len(rows) != 9
    ):
        raise GateDFailure(
            "Gate-D preparation requires an exact current-commit "
            "nine-row Gate-B campaign"
        )
    selected = [
        row
        for row in rows
        if row.get("purpose") == "one_million_central"
        and int(row.get("logical_id", -1)) == 0
    ]
    if (
        len(selected) != 3
        or {row.get("tune") for row in selected} != set(TUNES)
        or any(int(row.get("requested_successes", -1)) != 1_000_000
               for row in selected)
    ):
        raise GateDFailure(
            "Gate-B manifest lacks one one-million central pilot per tune"
        )
    report = validate_gate_b(gate_b_report, campaign, commit)
    return campaign, selected, report


def validate_raw_binding(
    production: Path,
    row: dict[str, Any],
    gate_b_report: dict[str, Any],
) -> tuple[Path, str]:
    raw = production / "raw" / row["tune"] / row["stable_name"]
    sidecar = Path(f"{raw}.sha256")
    if raw.is_symlink() or not raw.is_file() or not sidecar.is_file():
        raise GateDFailure(f"pilot raw file/checksum is absent: {raw}")
    fields = sidecar.read_text().split()
    actual = sha256(raw)
    if (
        len(fields) != 2
        or fields[0] != actual
        or Path(fields[1]).name != raw.name
    ):
        raise GateDFailure(f"pilot raw checksum sidecar differs: {raw}")
    evidence = [
        record
        for record in gate_b_report["raw_validation_evidence"]
        if record.get("tune") == row["tune"]
        and int(record.get("logical_id", -1)) == 0
    ]
    if (
        len(evidence) != 1
        or evidence[0].get("raw_sha256") != actual
        or int(evidence[0].get("entries", -1)) != 1_000_000
        or int(evidence[0].get("requested_successes", -1)) != 1_000_000
    ):
        raise GateDFailure(
            f"Gate-B report does not bind central pilot {row['tune']}"
        )
    receipt = (
        production
        / "raw_validation"
        / row["tune"]
        / "job_000"
        / f"attempt_{int(row['attempt']):03d}"
        / "receipt.json"
    )
    payload = load_json(receipt, "raw PASS receipt")
    if (
        payload.get("schema") != "hf_raw_validation_receipt_v1"
        or payload.get("result") != "PASS"
        or payload.get("output_sha256") != actual
        or evidence[0].get("validation_receipt_path")
        != str(receipt.relative_to(production))
        or evidence[0].get("validation_receipt_sha256")
        != sha256(receipt)
    ):
        raise GateDFailure(f"raw PASS receipt differs for {row['tune']}")
    return raw, actual


def central_directory(root: Path, tune: str) -> Path:
    return root / f"complete_root_GATE_D_{tune}"


def block_directory(root: Path, tune: str, block: int) -> Path:
    return (
        root
        / "SUBSAMPLES"
        / f"combined_root_subSamples_{tune}"
        / f"combined_root_{block}"
    )


def prepare_plot_config(checkout: Path, analysis: Path) -> Path:
    source = (
        checkout
        / "PlottingScripts"
        / "configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json"
    )
    config = load_json(source, "reduced THnSparse configuration")
    config["base_dir"] = str(analysis)
    config["bb_bar_complete_root_dir"] = "complete_root_GATE_D"
    config["cc_bar_complete_root_dir"] = "complete_root_GATE_D"
    block_base = str(
        analysis / "SUBSAMPLES" / "combined_root_subSamples"
    )
    config["bb_bar_complete_root_dir_sub_samples"] = block_base
    config["cc_bar_complete_root_dir_sub_samples"] = block_base
    config["nSubSamples"] = 10
    config["calculate_errors"] = True
    # Gate D is a reduced end-to-end smoke test. With this false, Paul's
    # plotting code skips bins unused by every configured smoke canvas but
    # throws immediately if any smoke-reachable point lacks all ten blocks.
    # The checked-in full paper configuration remains untouched and its
    # exhaustive final coverage is a Gate-E requirement.
    config["subsample_coverage_audit"] = False
    config["subsample_error_bins_to_exclude"] = []
    config["VERBOSE"] = True
    config["draw_correlation_plots"] = False
    plots = analysis / "plots"
    plots.mkdir(mode=0o700)
    for canvas in config.get("canvases_to_be_drawn", []):
        canvas["write_path"] = str(plots)
    for canvas in config.get("global_canvases_to_be_drawn", []):
        canvas["write"] = True
        canvas["write_path"] = str(plots)
    output = analysis / "gate_d_plot_config.json"
    exclusive_text(
        output,
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        mode=0o444,
    )
    return output


def prepare_exhaustive_audit_config(
    checkout: Path, analysis: Path
) -> Path:
    source = (
        checkout
        / "PlottingScripts"
        / "configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json"
    )
    config = load_json(source, "full THnSparse configuration")
    config["base_dir"] = str(analysis)
    config["bb_bar_complete_root_dir"] = "complete_root_GATE_D"
    config["cc_bar_complete_root_dir"] = "complete_root_GATE_D"
    block_base = str(
        analysis / "SUBSAMPLES" / "combined_root_subSamples"
    )
    config["bb_bar_complete_root_dir_sub_samples"] = block_base
    config["cc_bar_complete_root_dir_sub_samples"] = block_base
    config["nSubSamples"] = 10
    config["calculate_errors"] = True
    config["subsample_coverage_audit"] = True
    config["subsample_error_bins_to_exclude"] = []
    config["VERBOSE"] = False
    config["draw_correlation_plots"] = False
    for canvas in config.get("canvases_to_be_drawn", []):
        canvas["write"] = False
    for canvas in config.get("global_canvases_to_be_drawn", []):
        canvas["write"] = False
    output = analysis / "gate_d_exhaustive_subsample_audit_config.json"
    exclusive_text(
        output,
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        mode=0o444,
    )
    return output


def validate_exhaustive_audit_config(
    config: dict[str, Any], analysis: Path
) -> dict[str, Any]:
    expected_block_base = (
        analysis / "SUBSAMPLES" / "combined_root_subSamples"
    ).resolve()
    path_fields = {
        "base_dir": analysis.resolve(),
        "bb_bar_complete_root_dir_sub_samples": expected_block_base,
        "cc_bar_complete_root_dir_sub_samples": expected_block_base,
    }
    for key, value in path_fields.items():
        configured = config.get(key)
        if (
            not isinstance(configured, str)
            or Path(configured).expanduser().resolve() != value
        ):
            raise GateDFailure(
                f"Gate-D exhaustive-audit configuration differs: {key}"
            )
    expected = {
        "bb_bar_complete_root_dir": "complete_root_GATE_D",
        "cc_bar_complete_root_dir": "complete_root_GATE_D",
        "nSubSamples": 10,
        "calculate_errors": True,
        "subsample_coverage_audit": True,
        "subsample_error_bins_to_exclude": [],
        "draw_correlation_plots": False,
        "PYTHIA_TUNES": list(TUNES),
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise GateDFailure(
                f"Gate-D exhaustive-audit configuration differs: {key}"
            )
    bins = config.get("histograms_to_analyse")
    beauty = config.get("beauty_correlations_to_analyse")
    charm = config.get("charm_correlations_to_analyse")
    if (
        not isinstance(bins, list)
        or len(bins) != 12
        or len(
            {
                row.get("hDPhi")
                for row in bins
                if isinstance(row, dict)
            }
        ) != 12
        or not isinstance(beauty, list)
        or len(beauty) != 2
        or sum(
            len(row.get("configs", []))
            for row in beauty
            if isinstance(row, dict)
        ) != 10
        or not isinstance(charm, list)
        or len(charm) != 2
        or sum(
            len(row.get("configs", []))
            for row in charm
            if isinstance(row, dict)
        ) != 6
    ):
        raise GateDFailure(
            "Gate-D exhaustive-audit configuration is not the full "
            "12-bin, 16-pair paper scope"
        )
    if any(
        isinstance(row, dict) and row.get("write") is not False
        for key in ("canvases_to_be_drawn", "global_canvases_to_be_drawn")
        for row in config.get(key, [])
    ):
        raise GateDFailure(
            "Gate-D exhaustive audit must not write plot artifacts"
        )
    return {
        "scope": "full_paper_configuration",
        "multiplicity_bins": 12,
        "beauty_trigger_groups": 2,
        "beauty_pair_configurations": 10,
        "charm_trigger_groups": 2,
        "charm_pair_configurations": 6,
        "tunes": list(TUNES),
        "subsamples": 10,
    }


def validate_exhaustive_audit_log(
    text: str, returncode: int
) -> dict[str, Any]:
    matches = EXHAUSTIVE_AUDIT_SUMMARY.findall(text)
    if len(matches) != 1:
        raise GateDFailure(
            "exhaustive subsample audit lacks one machine-readable summary"
        )
    beauty, charm, total = (int(value) for value in matches[0])
    failure_records = len(
        re.findall(
            r"^SUBSAMPLE_COVERAGE_FAILURE\b", text, flags=re.MULTILINE
        )
    )
    if (
        total != beauty + charm
        or failure_records != total
        or "SUBSAMPLE_COVERAGE_ERROR" in text
    ):
        raise GateDFailure(
            "exhaustive subsample-audit failure accounting is inconsistent"
        )
    if total == 0:
        if (
            returncode != 0
            or "Subsample coverage audit passed" not in text
        ):
            raise GateDFailure(
                "passing exhaustive subsample audit returned nonzero"
            )
        coverage_state = "FULL_PAPER_SCOPE_PASS"
    else:
        if returncode != 2:
            raise GateDFailure(
                "coverage-only exhaustive audit must fail closed with code 2"
            )
        coverage_state = "PILOT_INSUFFICIENT_FOR_FULL_PAPER"
    return {
        "schema": EXHAUSTIVE_AUDIT_SCHEMA,
        "audit_execution_state": "PASS",
        "coverage_state": coverage_state,
        "publication_promotion_allowed": total == 0,
        "beauty_failures": beauty,
        "charm_failures": charm,
        "total_failures": total,
        "failure_records": failure_records,
        "returncode": returncode,
    }


def smoke_scope_contract(config: dict[str, Any]) -> dict[str, Any]:
    if (
        config.get("subsample_coverage_audit") is not False
        or config.get("calculate_errors") is not True
        or config.get("nSubSamples") != 10
        or config.get("subsample_error_bins_to_exclude") != []
        or config.get("PYTHIA_TUNES") != list(TUNES)
    ):
        raise GateDFailure(
            "Gate-D plot configuration is not a ten-block, "
            "canvas-scoped smoke configuration"
        )
    histogram_names = [
        row.get("hDPhi")
        for row in config.get("histograms_to_analyse", [])
        if isinstance(row, dict)
    ]
    if len(histogram_names) != 11 or len(set(histogram_names)) != 11:
        raise GateDFailure(
            "Gate-D plot configuration lacks eleven unique multiplicity bins"
        )
    canvases = config.get("canvases_to_be_drawn")
    if not isinstance(canvases, list) or not canvases:
        raise GateDFailure("Gate-D plot configuration has no smoke canvases")

    group_rows = []
    expected_matrices = 0
    expected_structural = 0
    for flavour, key in (
        ("BEAUTY", "beauty_correlations_to_analyse"),
        ("CHARM", "charm_correlations_to_analyse"),
    ):
        groups = config.get(key)
        if not isinstance(groups, list) or not groups:
            raise GateDFailure(
                f"Gate-D plot configuration has no {flavour} trigger group"
            )
        for group in groups:
            if not isinstance(group, dict):
                raise GateDFailure("Gate-D trigger group is malformed")
            trigger = group.get("trigger")
            pairs = group.get("configs")
            if (
                not isinstance(trigger, str)
                or not isinstance(pairs, list)
                or not pairs
                or any(not isinstance(pair, dict) for pair in pairs)
            ):
                raise GateDFailure("Gate-D trigger group has no pair configs")
            matching_canvases = [
                canvas
                for canvas in canvases
                if isinstance(canvas, dict)
                and canvas.get("FLAVOUR") in ("", flavour)
                and canvas.get("TriggerToUse") in ("", trigger)
            ]
            if not matching_canvases:
                raise GateDFailure(
                    f"Gate-D trigger is unreachable from a canvas: {trigger}"
                )
            required_bins = sorted(
                histogram
                for histogram in histogram_names
                if any(
                    histogram not in canvas.get("bins_to_ignore", [])
                    for canvas in matching_canvases
                )
            )
            if required_bins != ["hDPhiM1_10"]:
                raise GateDFailure(
                    "Gate-D reduced smoke scope must cover exactly the "
                    f"1-10% bin for {flavour}/{trigger}, got {required_bins}"
                )
            matrices = len(TUNES) * len(pairs) * len(required_bins)
            structural = len(TUNES) * len(required_bins)
            expected_matrices += matrices
            expected_structural += structural
            group_rows.append(
                {
                    "flavour": flavour,
                    "trigger": trigger,
                    "pair_count": len(pairs),
                    "required_multiplicity_bins": required_bins,
                    "expected_uncertainty_matrix_records": matrices,
                    "expected_structural_self_ratio_records": structural,
                    "expected_reference_records": structural,
                }
            )
    return {
        "schema": "hf_gate_d_plot_smoke_scope_v1",
        "coverage_mode": "configured_canvas_scope_fail_closed_v1",
        "required_multiplicity_bins": ["hDPhiM1_10"],
        "tunes": list(TUNES),
        "groups": group_rows,
        "expected_uncertainty_matrix_records": expected_matrices,
        "expected_statistic_records":
            2 * expected_matrices - expected_structural,
        "expected_structural_self_ratio_records": expected_structural,
        "expected_nondegenerate_positive_sem_records":
            2 * expected_matrices - expected_structural,
    }


def plot_inventory(
    analysis: Path, checkout: Path = ROOT
) -> dict[str, Any]:
    plots = analysis / "plots"
    files = []
    for path in sorted(plots.rglob("*")):
        if path.is_symlink():
            raise GateDFailure(f"plot artifact is a symbolic link: {path}")
        if path.is_file():
            files.append(
                {
                    "path": path.relative_to(analysis).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    pdfs = [row for row in files if row["path"].endswith(".pdf")]
    pngs = [row for row in files if row["path"].endswith(".png")]
    macros = [row for row in files if row["path"].endswith(".C")]
    if not pdfs or len(pdfs) != len(pngs) or len(pdfs) != len(macros):
        raise GateDFailure(
            "representative plots lack matching PDF/PNG/ROOT-macro outputs"
        )
    output_rows = pdfs + pngs + macros
    expected_sidecars = {
        f"{row['path']}.provenance.json" for row in output_rows
    }
    sidecar_rows = {
        row["path"]: row
        for row in files
        if row["path"].endswith(".provenance.json")
    }
    if set(sidecar_rows) != expected_sidecars:
        raise GateDFailure(
            "Gate-D plot outputs do not have exactly one adjacent provenance "
            "sidecar each"
        )
    run_rows = [
        row
        for row in files
        if row["path"].startswith("plots/provenance/")
        and row["path"].endswith(".json")
    ]
    if len(run_rows) != 1:
        raise GateDFailure(
            "Gate-D plot inventory requires exactly one run-provenance receipt"
        )
    run_receipt = load_json(
        analysis / run_rows[0]["path"], "Gate-D plot run provenance"
    )
    run_inputs = run_receipt.get("inputs", {})
    block_bindings = run_inputs.get("block_manifests", [])
    if (
        run_receipt.get("schema")
        != "hf_final_plot_run_provenance_v1"
        or run_receipt.get("state") != "PASS"
        or run_receipt.get("publication_eligible") is not False
        or run_receipt.get("target") != "gate-d-smoke"
        or not isinstance(run_inputs, dict)
        or run_inputs.get("input_mode")
        != "gate_d_one_million_pilot_pairs"
        or run_inputs.get("exact_input_count") != 9900
        or not HEX64.fullmatch(
            str(run_inputs.get("exact_input_inventory_sha256", ""))
        )
        or len(block_bindings) != 10
        or {
            row.get("block")
            for row in block_bindings
            if isinstance(row, dict)
            and row.get("input_count") == 900
            and row.get("status")
            == "PILOT_PAIR_INVENTORY_DIGEST_NOT_MANIFEST"
            and HEX64.fullmatch(str(row.get("sha256", "")))
        }
        != set(range(1, 11))
        or run_inputs.get("pair_inventory", {}).get("sha256")
        != sha256(analysis / "gate_d_pair_inventory.jsonl")
    ):
        raise GateDFailure("Gate-D plot run provenance is invalid")
    for output in output_rows:
        sidecar = load_json(
            analysis / f"{output['path']}.provenance.json",
            "Gate-D output provenance sidecar",
        )
        sidecar_output = sidecar.get("output", {})
        sidecar_output_path = Path(
            str(sidecar_output.get("path", ""))
        )
        if not sidecar_output_path.is_absolute():
            sidecar_output_path = checkout / sidecar_output_path
        if (
            sidecar.get("schema") != "hf_final_plot_provenance_v1"
            or sidecar.get("state") != "PASS"
            or sidecar.get("publication_eligible") is not False
            or sidecar_output_path.resolve()
            != (analysis / output["path"]).resolve()
            or sidecar_output.get("bytes") != output["bytes"]
            or sidecar_output.get("sha256") != output["sha256"]
            or sidecar.get("run_receipt", {}).get("sha256")
            != run_rows[0]["sha256"]
        ):
            raise GateDFailure(
                f"Gate-D output provenance differs: {output['path']}"
            )
    boundary_path = plots / "multiplicity_boundary_receipt_v1.json"
    boundary = load_json(
        boundary_path, "Gate-D multiplicity-boundary receipt"
    )
    if (
        boundary.get("schema")
        != "hadronization_multiplicity_boundary_receipt_v1"
        or boundary.get("completion_status") != "PASS"
        or not HEX64.fullmatch(str(boundary.get("payload_sha256", "")))
    ):
        raise GateDFailure(
            "Gate-D multiplicity-boundary receipt is invalid"
        )
    boundary_row = [
        row
        for row in files
        if row["path"] == "plots/multiplicity_boundary_receipt_v1.json"
    ]
    if len(boundary_row) != 1:
        raise GateDFailure(
            "Gate-D plot inventory omits the multiplicity-boundary receipt"
        )
    if (
        run_receipt.get("multiplicity_boundary_receipt", {}).get("sha256")
        != boundary_row[0]["sha256"]
    ):
        raise GateDFailure(
            "Gate-D plot run provenance does not bind the inventoried "
            "multiplicity-boundary receipt"
        )
    return {
        "schema": "hf_gate_d_plot_inventory_v1",
        "analysis_root": str(analysis),
        "pdf_count": len(pdfs),
        "png_count": len(pngs),
        "macro_count": len(macros),
        "output_provenance_sidecar_count": len(sidecar_rows),
        "run_provenance_receipt_count": len(run_rows),
        "run_provenance_receipt": run_rows[0],
        "multiplicity_boundary_receipt": boundary_row[0],
        "files": files,
    }


def expected_pair_paths(checkout: Path, analysis: Path) -> set[str]:
    registry = load_json(
        checkout / "config/heavy_flavour_pair_registry_v1.json",
        "pair registry",
    )
    filenames = {
        row.get("filename") for row in registry.get("pairs", [])
    }
    if registry.get("pair_count") != 300 or len(filenames) != 300 or (
        not all(isinstance(name, str) and name.endswith(".root")
                for name in filenames)
    ):
        raise GateDFailure("pair registry does not define 300 unique files")
    paths = set()
    for tune in TUNES:
        for filename in filenames:
            paths.add(
                (
                    central_directory(analysis, tune) / filename
                ).relative_to(analysis).as_posix()
            )
            for block in range(1, 11):
                paths.add(
                    (
                        block_directory(analysis, tune, block)
                        / filename
                    ).relative_to(analysis).as_posix()
                )
    if len(paths) != 9900:
        raise AssertionError("Gate-D pair inventory is not 9,900 files")
    return paths


def write_pair_inventory(checkout: Path, analysis: Path) -> Path:
    rows = []
    expected = expected_pair_paths(checkout, analysis)
    for relative in sorted(expected):
        path = analysis / relative
        if path.is_symlink() or not path.is_file():
            raise GateDFailure(f"pair artifact is absent: {path}")
        rows.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    discovered = {
        path.relative_to(analysis).as_posix()
        for tune in TUNES
        for directory in (
            [central_directory(analysis, tune)]
            + [
                block_directory(analysis, tune, block)
                for block in range(1, 11)
            ]
        )
        for path in directory.glob("*.root")
        if path.is_file()
    }
    if discovered != expected:
        raise GateDFailure(
            "Gate-D analysis has missing or extra pair ROOT files"
        )
    inventory = analysis / "gate_d_pair_inventory.jsonl"
    exclusive_text(
        inventory,
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
    )
    return inventory


def validate_pair_inventory(
    checkout: Path, analysis: Path, inventory: Path
) -> None:
    expected = expected_pair_paths(checkout, analysis)
    rows = load_jsonl(inventory)
    if len(rows) != 9900:
        raise GateDFailure("pair checksum inventory does not have 9,900 rows")
    observed: set[str] = set()
    for row in rows:
        relative = row.get("path")
        if (
            not isinstance(relative, str)
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or relative in observed
        ):
            raise GateDFailure("pair checksum inventory path is unsafe/duplicate")
        observed.add(relative)
        path = analysis / relative
        if (
            path.is_symlink()
            or not path.is_file()
            or path.stat().st_size != row.get("bytes")
            or sha256(path) != row.get("sha256")
        ):
            raise GateDFailure(f"prepared pair artifact changed: {relative}")
    if observed != expected:
        raise GateDFailure("pair checksum inventory coverage differs")


def summarize_file_sizes(rows: list[dict[str, Any]]) -> dict[str, int]:
    sizes = sorted(int(row["bytes"]) for row in rows)
    if len(sizes) != 300 or any(size <= 0 for size in sizes):
        raise GateDFailure(
            "Gate-D storage measurement requires 300 nonempty pair files "
            "per directory"
        )
    middle = len(sizes) // 2
    return {
        "pair_file_count": len(sizes),
        "total_bytes": sum(sizes),
        "minimum_pair_file_bytes": sizes[0],
        "median_pair_file_bytes": (
            sizes[middle - 1] + sizes[middle]
        ) // 2,
        "maximum_pair_file_bytes": sizes[-1],
    }


def measure_pair_storage(
    analysis: Path, inventory_path: Path
) -> dict[str, Any]:
    rows = load_jsonl(inventory_path)
    if len(rows) != 9900:
        raise GateDFailure(
            "Gate-D storage measurement requires the complete 9,900-file "
            "pair inventory"
        )
    by_tune = []
    for tune in TUNES:
        directories = []
        central_relative = f"complete_root_GATE_D_{tune}"
        central_rows = [
            row
            for row in rows
            if Path(str(row["path"])).parent.as_posix()
            == central_relative
        ]
        central = {
            "kind": "central",
            "block": None,
            "directory": central_relative,
            **summarize_file_sizes(central_rows),
        }
        directories.append(central)
        for block in range(1, 11):
            relative = (
                "SUBSAMPLES/"
                f"combined_root_subSamples_{tune}/combined_root_{block}"
            )
            block_rows = [
                row
                for row in rows
                if Path(str(row["path"])).parent.as_posix() == relative
            ]
            directories.append(
                {
                    "kind": "event_id_block",
                    "block": block,
                    "directory": relative,
                    **summarize_file_sizes(block_rows),
                }
            )
        central_bytes = central["total_bytes"]
        block_bytes = sum(
            row["total_bytes"]
            for row in directories
            if row["kind"] == "event_id_block"
        )
        by_tune.append(
            {
                "tune": tune,
                "central_pair_files": 300,
                "central_bytes": central_bytes,
                "ten_block_pair_files": 3000,
                "ten_block_bytes": block_bytes,
                "central_plus_ten_blocks_pair_files": 3300,
                "central_plus_ten_blocks_bytes":
                    central_bytes + block_bytes,
                "directories": directories,
            }
        )
    return {
        "analysis_root": str(analysis),
        "pair_inventory_path": str(inventory_path),
        "pair_inventory_sha256": sha256(inventory_path),
        "pilot_pair_files": 9900,
        "pilot_pair_bytes": sum(
            row["central_plus_ten_blocks_bytes"] for row in by_tune
        ),
        "by_tune": by_tune,
    }


def candidate_raw_projection(gate_b: dict[str, Any]) -> dict[str, Any]:
    projection = gate_b.get("full_candidate_resource_projection")
    benchmark = gate_b.get("runtime_storage_benchmark")
    if not isinstance(projection, dict) or not isinstance(benchmark, list):
        raise GateDFailure(
            "Gate-B report lacks measured candidate raw-storage projection"
        )
    expected_jobs = {
        "MONASH": 100,
        "JUNCTIONS": 200,
        "CLOSEPACKING": 200,
    }
    rows = projection.get("by_tune")
    if (
        projection.get("candidate_jobs") != 500
        or projection.get("projected_successful_events") != 500_000_000
        or not isinstance(rows, list)
        or len(rows) != 3
    ):
        raise GateDFailure(
            "Gate-B full-candidate storage projection has wrong scope"
        )
    result = []
    for tune in TUNES:
        projected = [
            row
            for row in rows
            if isinstance(row, dict) and row.get("tune") == tune
        ]
        observed = [
            row
            for row in benchmark
            if isinstance(row, dict)
            and row.get("tune") == tune
            and row.get("logical_id") == 0
        ]
        if len(projected) != 1 or len(observed) != 1:
            raise GateDFailure(
                f"Gate-B storage basis is not unique for {tune}"
            )
        raw_bytes = observed[0].get("raw_bytes")
        jobs = expected_jobs[tune]
        projected_bytes = projected[0].get("projected_raw_bytes")
        if (
            isinstance(raw_bytes, bool)
            or not isinstance(raw_bytes, int)
            or raw_bytes <= 0
            or projected[0].get("candidate_jobs") != jobs
            or projected[0].get("successful_events_per_job") != 1_000_000
            or projected_bytes != raw_bytes * jobs
        ):
            raise GateDFailure(
                f"Gate-B raw-storage arithmetic differs for {tune}"
            )
        result.append(
            {
                "tune": tune,
                "candidate_jobs": jobs,
                "observed_one_million_pilot_raw_bytes": raw_bytes,
                "projected_candidate_raw_bytes": projected_bytes,
            }
        )
    total = sum(row["projected_candidate_raw_bytes"] for row in result)
    if projection.get("projected_raw_bytes") != total:
        raise GateDFailure(
            "Gate-B total candidate raw-storage projection differs"
        )
    return {
        "source_schema": gate_b.get("schema"),
        "candidate_jobs": 500,
        "projected_successful_events": 500_000_000,
        "projected_candidate_raw_bytes": total,
        "by_tune": result,
    }


def inventory_bytes(inventory: dict[str, Any], label: str) -> int:
    rows = inventory.get("files")
    if not isinstance(rows, list):
        raise GateDFailure(f"{label} has no file rows")
    total = 0
    for row in rows:
        if (
            not isinstance(row, dict)
            or isinstance(row.get("bytes"), bool)
            or not isinstance(row.get("bytes"), int)
            or row["bytes"] < 0
        ):
            raise GateDFailure(f"{label} contains an invalid byte count")
        total += row["bytes"]
    return total


def capacity_decision(
    capacity_bytes: int, available_bytes: int, required_bytes: int
) -> dict[str, Any]:
    if (
        capacity_bytes <= 0
        or available_bytes < 0
        or available_bytes > capacity_bytes
        or required_bytes < 0
    ):
        raise GateDFailure("filesystem capacity values are invalid")
    maximum_from_available = int(
        available_bytes * MAX_CURRENT_AVAILABLE_FRACTION
    )
    minimum_remaining = max(
        int(capacity_bytes * MIN_PROJECTED_FREE_FRACTION),
        MIN_PROJECTED_FREE_BYTES,
    )
    projected_remaining = available_bytes - required_bytes
    reasons = []
    if required_bytes > maximum_from_available:
        reasons.append(
            "projection exceeds 70% of currently available bytes"
        )
    if projected_remaining < minimum_remaining:
        reasons.append(
            "projection would leave less than max(5% capacity, 500 GiB)"
        )
    return {
        "capacity_bytes": capacity_bytes,
        "available_bytes": available_bytes,
        "required_additional_bytes": required_bytes,
        "maximum_allowed_from_current_available_bytes":
            maximum_from_available,
        "minimum_required_remaining_bytes": minimum_remaining,
        "projected_remaining_bytes": projected_remaining,
        "current_available_fraction": available_bytes / capacity_bytes,
        "projected_remaining_fraction":
            projected_remaining / capacity_bytes,
        "fraction_of_current_available_required": (
            required_bytes / available_bytes
            if available_bytes > 0
            else None
        ),
        "state": "PASS" if not reasons else "FAIL",
        "failure_reasons": reasons,
    }


def capacity_check(
    production: Path,
    analysis: Path,
    raw_required_bytes: int,
    analysis_required_bytes: int,
) -> dict[str, Any]:
    role_rows = [
        ("candidate_raw_and_partials", production, raw_required_bytes),
        ("analysis_and_publication_outputs", analysis,
         analysis_required_bytes),
    ]
    groups: dict[int, dict[str, Any]] = {}
    for role, probe, required in role_rows:
        if not probe.exists():
            raise GateDFailure(f"storage probe path is absent: {probe}")
        device = int(probe.stat().st_dev)
        group = groups.setdefault(
            device,
            {
                "device_id": device,
                "probe_paths": [],
                "roles": [],
                "required_additional_bytes": 0,
            },
        )
        group["probe_paths"].append(str(probe))
        group["roles"].append(role)
        group["required_additional_bytes"] += required

    filesystems = []
    for device in sorted(groups):
        group = groups[device]
        snapshots = []
        for probe_text in group["probe_paths"]:
            values = os.statvfs(probe_text)
            fragment = values.f_frsize or values.f_bsize
            snapshots.append(
                {
                    "capacity_bytes": int(values.f_blocks * fragment),
                    "available_bytes": int(values.f_bavail * fragment),
                    "statvfs_frsize": int(fragment),
                    "statvfs_blocks": int(values.f_blocks),
                    "statvfs_bavail": int(values.f_bavail),
                }
            )
        geometries = {
            (row["capacity_bytes"], row["statvfs_frsize"], row["statvfs_blocks"])
            for row in snapshots
        }
        if len(geometries) != 1:
            raise GateDFailure(
                "paths on one storage device report inconsistent capacity"
            )
        decision = capacity_decision(
            snapshots[0]["capacity_bytes"],
            min(row["available_bytes"] for row in snapshots),
            group["required_additional_bytes"],
        )
        filesystems.append(
            {
                "device_id": device,
                "probe_paths": sorted(group["probe_paths"]),
                "roles": sorted(group["roles"]),
                "statvfs_frsize": snapshots[0]["statvfs_frsize"],
                "statvfs_blocks": snapshots[0]["statvfs_blocks"],
                "statvfs_bavail": min(
                    row["statvfs_bavail"] for row in snapshots
                ),
                **decision,
            }
        )
    return {
        "checked_utc": utc_now(),
        "capacity_source": "os.statvfs f_bavail",
        "state": (
            "PASS"
            if filesystems
            and all(row["state"] == "PASS" for row in filesystems)
            else "FAIL"
        ),
        "filesystems": filesystems,
    }


def build_storage_projection(
    *,
    analysis: Path,
    production: Path,
    pair_inventory_path: Path,
    gate_b: dict[str, Any],
    plot_inventory: dict[str, Any],
    render_inventory: dict[str, Any],
) -> dict[str, Any]:
    pair_measurement = measure_pair_storage(
        analysis, pair_inventory_path
    )
    raw_projection = candidate_raw_projection(gate_b)
    tune_measurements = {
        row["tune"]: row for row in pair_measurement["by_tune"]
    }
    canonical_per_job_analysis = sum(
        tune_measurements[tune]["central_bytes"] * 100
        for tune in TUNES
    )
    final_merged_central = canonical_per_job_analysis
    final_ten_blocks = sum(
        tune_measurements[tune]["ten_block_bytes"] * 100
        for tune in TUNES
    )
    measured_plot_bytes = (
        inventory_bytes(plot_inventory, "plot inventory")
        + inventory_bytes(render_inventory, "render inventory")
    )
    final_plot_evidence = max(
        measured_plot_bytes * FULL_PLOT_SCALE_FACTOR,
        MIN_FULL_PLOT_AND_EVIDENCE_BYTES,
    )
    candidate_raw = raw_projection["projected_candidate_raw_bytes"]
    simultaneous_partials = (
        candidate_raw * CONCURRENT_PARTIAL_RAW_MULTIPLIER
    )
    raw_required = candidate_raw + simultaneous_partials
    analysis_required = (
        canonical_per_job_analysis
        + final_merged_central
        + final_ten_blocks
        + final_plot_evidence
    )
    components = {
        "full_100_200_200_candidate_raw_bytes": candidate_raw,
        "simultaneous_partial_raw_bytes": simultaneous_partials,
        "canonical_300_job_per_job_analysis_bytes":
            canonical_per_job_analysis,
        "final_merged_central_bytes": final_merged_central,
        "final_ten_block_bytes": final_ten_blocks,
        "full_plots_logs_validation_evidence_bytes":
            final_plot_evidence,
        "raw_filesystem_required_additional_bytes": raw_required,
        "analysis_filesystem_required_additional_bytes":
            analysis_required,
        "total_required_additional_bytes":
            raw_required + analysis_required,
    }
    check = capacity_check(
        production, analysis, raw_required, analysis_required
    )
    passed = check["state"] == "PASS"
    return {
        "schema": STORAGE_SCHEMA,
        "state": "PASS" if passed else "FAIL",
        "gate_e_storage_authorized": passed,
        "strategy": {
            "candidate_slots": {
                "MONASH": 100,
                "JUNCTIONS": 200,
                "CLOSEPACKING": 200,
            },
            "canonical_analysis_jobs": 300,
            "successful_events_per_job": 1_000_000,
        },
        "basis": (
            "Raw bytes are the Gate-B measured one-million-event tune "
            "pilots scaled to all 100/200/200 candidates. A second complete "
            "raw footprint is reserved for simultaneous partial files. "
            "Canonical per-job analysis and merged central outputs each use "
            "100 times the measured one-tune central pair footprint. Final "
            "blocks conservatively use 100 times the measured ten-block "
            "pilot footprint. Full plots, logs, validation, and evidence "
            "use the larger of ten times the measured reduced outputs or "
            "10 GiB. Existing Gate-D and legacy data are already charged "
            "against live available space."
        ),
        "pilot_pair_storage": pair_measurement,
        "gate_b_candidate_raw_projection": raw_projection,
        "measured_reduced_plot_and_render_bytes": measured_plot_bytes,
        "projected_components": components,
        "capacity_policy": {
            "maximum_fraction_of_current_available":
                MAX_CURRENT_AVAILABLE_FRACTION,
            "minimum_projected_free_fraction":
                MIN_PROJECTED_FREE_FRACTION,
            "minimum_projected_free_bytes": MIN_PROJECTED_FREE_BYTES,
            "simultaneous_partial_raw_multiplier":
                CONCURRENT_PARTIAL_RAW_MULTIPLIER,
            "full_plot_scale_factor": FULL_PLOT_SCALE_FACTOR,
            "minimum_full_plot_and_evidence_bytes":
                MIN_FULL_PLOT_AND_EVIDENCE_BYTES,
        },
        "preparation_capacity_check": check,
    }


def validate_and_recheck_storage_projection(
    *,
    stored: dict[str, Any],
    analysis: Path,
    production: Path,
    pair_inventory_path: Path,
    gate_b: dict[str, Any],
    plot_inventory: dict[str, Any],
    render_inventory: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    if (
        not isinstance(stored, dict)
        or stored.get("schema") != STORAGE_SCHEMA
        or stored.get("state") != "PASS"
        or stored.get("gate_e_storage_authorized") is not True
    ):
        raise GateDFailure(
            "preparation lacks a passing Gate-E storage projection"
        )
    fresh = build_storage_projection(
        analysis=analysis,
        production=production,
        pair_inventory_path=pair_inventory_path,
        gate_b=gate_b,
        plot_inventory=plot_inventory,
        render_inventory=render_inventory,
    )
    immutable_keys = (
        "schema",
        "strategy",
        "basis",
        "pilot_pair_storage",
        "gate_b_candidate_raw_projection",
        "measured_reduced_plot_and_render_bytes",
        "projected_components",
        "capacity_policy",
    )
    for key in immutable_keys:
        if stored.get(key) != fresh.get(key):
            raise GateDFailure(
                f"prepared storage projection changed: {key}"
            )
    recheck = fresh["preparation_capacity_check"]
    final = dict(stored)
    passed = recheck.get("state") == "PASS"
    final["state"] = "PASS" if passed else "FAIL"
    final["gate_e_storage_authorized"] = passed
    final["final_capacity_recheck"] = recheck
    return final, recheck


def validate_artifact_inventory(
    analysis: Path,
    inventory: dict[str, Any],
    directory_name: str,
) -> None:
    rows = inventory.get("files")
    if not isinstance(rows, list):
        raise GateDFailure(f"{directory_name} inventory has no file rows")
    observed: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise GateDFailure(f"{directory_name} inventory row is invalid")
        relative = row.get("path")
        if (
            not isinstance(relative, str)
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or relative in observed
        ):
            raise GateDFailure(
                f"{directory_name} inventory path is unsafe/duplicate"
            )
        observed.add(relative)
        path = analysis / relative
        if (
            path.is_symlink()
            or not path.is_file()
            or path.stat().st_size != row.get("bytes")
            or sha256(path) != row.get("sha256")
        ):
            raise GateDFailure(
                f"{directory_name} artifact changed: {relative}"
            )
    discovered = {
        path.relative_to(analysis).as_posix()
        for path in (analysis / directory_name).rglob("*")
        if path.is_file()
    }
    if discovered != observed:
        raise GateDFailure(
            f"{directory_name} has files outside its checksum inventory"
        )


def validate_preparation_commands(
    preparation: dict[str, Any], analysis: Path
) -> None:
    commands = preparation.get("commands")
    if not isinstance(commands, list) or len(commands) < 34:
        raise GateDFailure("preparation command evidence is incomplete")
    exhaustive_binding = preparation.get("exhaustive_subsample_audit")
    exhaustive_records = 0
    for command in commands:
        if (
            not isinstance(command, dict)
            or command.get("compiler_warning_found") is True
            or not HEX64.fullmatch(str(command.get("log_sha256", "")))
        ):
            raise GateDFailure("preparation retains failed command evidence")
        is_exhaustive = (
            command.get("name")
            == "exhaustive_subsample_coverage_audit"
        )
        if (
            not is_exhaustive
            and command.get("returncode") != 0
        ):
            raise GateDFailure("preparation retains failed command evidence")
        log = Path(str(command.get("log_path", ""))).resolve()
        try:
            log.relative_to(analysis)
        except ValueError as error:
            raise GateDFailure(
                "preparation command log is outside the analysis root"
            ) from error
        if (
            log.is_symlink()
            or not log.is_file()
            or log.stat().st_size != command.get("log_bytes")
            or sha256(log) != command["log_sha256"]
        ):
            raise GateDFailure(f"preparation command log changed: {log}")
        if is_exhaustive:
            exhaustive_records += 1
            observed = validate_exhaustive_audit_log(
                log.read_text(errors="replace"),
                command.get("returncode"),
            )
            if (
                not isinstance(exhaustive_binding, dict)
                or exhaustive_binding.get("result") != observed
            ):
                raise GateDFailure(
                    "prepared exhaustive subsample-audit result changed"
                )
    if exhaustive_records != 1:
        raise GateDFailure(
            "preparation must retain exactly one exhaustive subsample audit"
        )


def validate_subsample_log(
    text: str, scope: dict[str, Any] | None = None
) -> dict[str, Any]:
    lowered = text.lower()
    if (
        "nan" in lowered
        or re.search(r"(^|[^a-z])inf(?:inity)?([^a-z]|$)", lowered)
        or "1e-10" in lowered
        or "zero denominator" in lowered
        or "coverage incomplete" in lowered
        or "subsample_coverage_error" in lowered
        or "subsample_coverage_failure" in lowered
    ):
        raise GateDFailure(
            "strict plotting log contains NaN, infinity, or a placeholder "
            "1e-10 uncertainty"
        )
    pair_counts = {
        (row.get("flavour"), row.get("trigger")): row.get("pair_count")
        for row in (scope or {}).get("groups", [])
        if isinstance(row, dict)
    }
    allowed_matrix_groups: dict[tuple[str, str, str, str], int] = {}
    for row in (scope or {}).get("groups", []):
        if not isinstance(row, dict):
            continue
        for tune in (scope or {}).get("tunes", TUNES):
            for multiplicity_bin in row.get(
                "required_multiplicity_bins", []
            ):
                allowed_matrix_groups[
                    (
                        row.get("flavour"),
                        row.get("trigger"),
                        tune,
                        multiplicity_bin,
                    )
                ] = row.get("pair_count")
    matrix_count = 0
    total_records = 0
    nondegenerate_records = 0
    structural_records = 0
    context: dict[str, Any] | None = None
    seen_matrices: set[tuple[str, str, str, str, str]] = set()
    reference_identity_by_group: dict[
        tuple[str, str, str, str], tuple[int, int]
    ] = {}
    reference_records_by_group: dict[
        tuple[str, str, str, str], int
    ] = {}
    matrix_groups: set[tuple[str, str, str, str]] = set()
    matrix_records_by_group: dict[
        tuple[str, str, str, str], int
    ] = {}
    for line in text.splitlines():
        if line.startswith("UNCERTAINTY_MATRIX "):
            if scope is not None and context is not None:
                raise GateDFailure(
                    "uncertainty-matrix record lacks its paired yield/ratio "
                    "statistics"
                )
            context = dict(
                re.findall(r"(\w+)=([^\s]+)", line)
            )
            required = {
                "flavour",
                "trigger",
                "tune",
                "associate",
                "associate_pdg",
                "bin",
                "reference_pdg",
                "reference_index",
                "is_reference",
                "finite_yields",
                "finite_ratios",
                "yield_sem",
                "ratio_sem",
                "yield_degenerate",
                "ratio_degenerate",
                "yield_status",
                "ratio_status",
                "denominator_status",
                "status",
            }
            if not required.issubset(context):
                raise GateDFailure(
                    f"malformed uncertainty-matrix record: {line}"
                )
            if context["status"] != "PASS":
                raise GateDFailure(
                    f"failed uncertainty-matrix record: {line}"
                )
            try:
                associate_pdg = int(context["associate_pdg"])
                reference_pdg = int(context["reference_pdg"])
                reference_index = int(context["reference_index"])
            except ValueError as error:
                raise GateDFailure(
                    f"invalid explicit reference identity: {line}"
                ) from error
            if (
                associate_pdg == 0
                or reference_pdg == 0
                or reference_index < 0
                or context["is_reference"] not in {"true", "false"}
            ):
                raise GateDFailure(
                    f"invalid explicit reference identity: {line}"
                )
            is_reference = context["is_reference"] == "true"
            if is_reference != (associate_pdg == reference_pdg):
                raise GateDFailure(
                    "is_reference disagrees with explicit associate/reference "
                    f"PDG identity: {line}"
                )
            try:
                finite_yields = int(context["finite_yields"])
                yield_sem = float(context["yield_sem"])
            except ValueError as error:
                raise GateDFailure(
                    f"invalid yield-coverage matrix fields: {line}"
                ) from error
            if (
                finite_yields != 10
                or not math.isfinite(yield_sem)
                or yield_sem <= 0.0
                or context["yield_degenerate"] != "false"
                or context["yield_status"] != "PASS"
            ):
                raise GateDFailure(
                    f"yield-coverage matrix is not finite n=10: {line}"
                )
            ratio_sem: float | None = None
            if is_reference:
                if (
                    context["finite_ratios"] != "NA"
                    or context["ratio_sem"] != "NA"
                    or context["ratio_degenerate"] != "NA"
                    or context["ratio_status"] != "NOT_APPLICABLE"
                    or context["denominator_status"] != "NOT_APPLICABLE"
                ):
                    raise GateDFailure(
                        "structural reference ratio is not explicitly "
                        f"NOT_APPLICABLE: {line}"
                    )
            else:
                try:
                    finite_ratios = int(context["finite_ratios"])
                    ratio_sem = float(context["ratio_sem"])
                except ValueError as error:
                    raise GateDFailure(
                        f"invalid ratio-coverage matrix fields: {line}"
                    ) from error
                if (
                    finite_ratios != 10
                    or not math.isfinite(ratio_sem)
                    or ratio_sem <= 0.0
                    or context["ratio_degenerate"] != "false"
                    or context["ratio_status"] != "PASS"
                    or context["denominator_status"] != "valid"
                ):
                    raise GateDFailure(
                        f"ratio-coverage matrix is not finite n=10: {line}"
                    )
            pair_count = pair_counts.get(
                (context["flavour"], context["trigger"])
            )
            if scope is not None and (
                not isinstance(pair_count, int)
                or isinstance(pair_count, bool)
                or not 0 <= reference_index < pair_count
            ):
                raise GateDFailure(
                    f"reference index is outside configured group: {line}"
                )
            group_key = (
                context["flavour"],
                context["trigger"],
                context["tune"],
                context["bin"],
            )
            matrix_key = (*group_key, context["associate"])
            if scope is not None and group_key not in allowed_matrix_groups:
                raise GateDFailure(
                    f"uncertainty matrix is outside configured scope: {line}"
                )
            if matrix_key in seen_matrices:
                raise GateDFailure(
                    f"duplicate uncertainty-matrix record: {line}"
                )
            seen_matrices.add(matrix_key)
            matrix_groups.add(group_key)
            matrix_records_by_group[group_key] = (
                matrix_records_by_group.get(group_key, 0) + 1
            )
            reference_identity = (reference_pdg, reference_index)
            previous_reference = reference_identity_by_group.setdefault(
                group_key, reference_identity
            )
            if previous_reference != reference_identity:
                raise GateDFailure(
                    "uncertainty matrices disagree on explicit reference "
                    f"identity for {group_key}"
                )
            if context["is_reference"] == "true":
                reference_records_by_group[group_key] = (
                    reference_records_by_group.get(group_key, 0) + 1
                )
            context["reference_pdg"] = reference_pdg
            context["reference_index"] = reference_index
            context["associate_pdg"] = associate_pdg
            context["is_reference"] = is_reference
            context["yield_sem"] = yield_sem
            context["ratio_sem"] = ratio_sem
            context["seen_yield"] = False
            matrix_count += 1
            continue
        is_yield = "subsample yield stats" in line
        is_not_applicable_ratio = (
            line.strip()
            == "subsample ratio stats status=NOT_APPLICABLE "
            "reason=structural_reference_self_ratio"
        )
        is_ratio = (
            "subsample ratio stats" in line
            and not is_not_applicable_ratio
        )
        if not is_yield and not is_ratio and not is_not_applicable_ratio:
            continue
        if scope is not None and context is None:
            raise GateDFailure(
                f"subsample statistic has no uncertainty-matrix identity: {line}"
            )
        if context is not None:
            if is_yield:
                if context["seen_yield"]:
                    raise GateDFailure(
                        f"duplicate subsample-yield statistic: {line}"
                    )
                context["seen_yield"] = True
            elif not context["seen_yield"]:
                raise GateDFailure(
                    f"subsample-ratio statistic precedes yield: {line}"
                )
        if is_not_applicable_ratio:
            if (
                context is None
                or not context["is_reference"]
                or not context["seen_yield"]
            ):
                raise GateDFailure(
                    "NOT_APPLICABLE ratio is not the explicit structural "
                    f"reference record: {line}"
                )
            structural_records += 1
            context = None
            continue
        if (
            is_ratio
            and context is not None
            and context["is_reference"]
        ):
            raise GateDFailure(
                "structural reference self-ratio was emitted as a numeric "
                f"statistic: {line}"
            )
        total_records += 1
        count = re.search(r"(?:^|\s)n=(\d+)(?:\s|$)", line)
        mean = re.search(
            r"(?:^|\s)mean=([-+0-9.eE]+)(?:\s|$)", line
        )
        deviation = re.search(
            r"(?:^|\s)stdDev=([-+0-9.eE]+)(?:\s|$)", line
        )
        error = re.search(
            r"(?:^|\s)stdError=([-+0-9.eE]+)(?:\s|$)", line
        )
        if not count or int(count.group(1)) != 10 or not error:
            raise GateDFailure(
                f"strict plotting record does not contain n=10: {line}"
            )
        error_value = float(error.group(1))
        if not math.isfinite(error_value) or error_value < 0.0:
            raise GateDFailure(
                f"strict plotting record has a non-finite SEM: {line}"
            )
        if error_value <= 0.0:
            raise GateDFailure(
                "nondegenerate strict plotting record lacks a finite "
                f"positive SEM: {line}"
            )
        if context is not None:
            matrix_sem = (
                context["yield_sem"] if is_yield else context["ratio_sem"]
            )
            if matrix_sem is None or not math.isclose(
                error_value,
                matrix_sem,
                rel_tol=5e-6,
                abs_tol=1e-15,
            ):
                raise GateDFailure(
                    "verbose statistic SEM differs from its "
                    f"UNCERTAINTY_MATRIX record: {line}"
                )
        nondegenerate_records += 1
        if is_ratio:
            context = None
    if total_records == 0:
        raise GateDFailure(
            "strict plotting log contains no subsample yield/ratio records"
        )
    if scope is not None:
        if context is not None:
            raise GateDFailure(
                "final uncertainty-matrix record lacks paired statistics"
            )
        invalid_reference_groups = {
            group: reference_records_by_group.get(group, 0)
            for group in matrix_groups
            if reference_records_by_group.get(group, 0) != 1
        }
        if invalid_reference_groups:
            raise GateDFailure(
                "each flavour/trigger/tune/bin uncertainty group must emit "
                "exactly one explicit reference record: "
                f"{invalid_reference_groups}"
            )
        if set(allowed_matrix_groups) != matrix_groups:
            raise GateDFailure(
                "uncertainty-matrix flavour/trigger/tune/bin coverage "
                "differs from configured smoke scope"
            )
        invalid_group_sizes = {
            group: {
                "observed": matrix_records_by_group.get(group, 0),
                "expected": expected_size,
            }
            for group, expected_size in allowed_matrix_groups.items()
            if matrix_records_by_group.get(group, 0) != expected_size
        }
        if invalid_group_sizes:
            raise GateDFailure(
                "uncertainty-matrix associate coverage differs by group: "
                f"{invalid_group_sizes}"
            )
        expected = {
            "matrix": scope["expected_uncertainty_matrix_records"],
            "total": scope["expected_statistic_records"],
            "structural":
                scope["expected_structural_self_ratio_records"],
            "nondegenerate":
                scope["expected_nondegenerate_positive_sem_records"],
        }
        observed = {
            "matrix": matrix_count,
            "total": total_records,
            "structural": structural_records,
            "nondegenerate": nondegenerate_records,
        }
        if observed != expected:
            raise GateDFailure(
                "strict plotting log does not exactly cover the configured "
                f"smoke scope: observed={observed}, expected={expected}"
            )
    return {
        "schema": "hf_gate_d_subsample_log_validation_v2",
        "uncertainty_matrix_records": matrix_count,
        "total_statistic_records": total_records,
        "structural_self_ratio_records": structural_records,
        "nondegenerate_positive_sem_records": nondegenerate_records,
        "structural_self_ratio_definition": (
            "the single UNCERTAINTY_MATRIX record explicitly marked "
            "is_reference=true for its stable reference_pdg/reference_index, "
            "must carry finite_ratios=NA, ratio_sem=NA, "
            "ratio_status=NOT_APPLICABLE and the matching verbose "
            "NOT_APPLICABLE reason; a numeric self-ratio is forbidden"
        )
    }


def prepare(args: argparse.Namespace) -> int:
    checkout = args.checkout_root.resolve()
    analysis = args.analysis_root.resolve()
    if analysis.exists() or analysis.is_symlink():
        raise GateDFailure(
            f"refusing to alter existing Gate-D analysis root: {analysis}"
        )
    environment_evidence = validate_checkout(checkout, args.development)
    campaign_dir = args.campaign_dir.resolve()
    production = args.production_root.resolve()
    campaign, rows, gate_b = validate_campaign(
        campaign_dir,
        args.gate_b_report.resolve(),
        environment_evidence["repository_commit"],
    )
    analysis.mkdir(parents=True, mode=0o700)
    logs = analysis / "logs"
    logs.mkdir(mode=0o700)
    commands: list[dict[str, Any]] = []
    raw_bindings: list[dict[str, Any]] = []
    failure: str | None = None
    try:
        macro = checkout / "AnalysisScripts/status_analysis_THnSparse_qq.C"
        macro_hash = sha256(macro)
        base_environment = os.environ.copy()
        base_environment["HADRONIZATION_BASE"] = str(checkout)
        for row in sorted(rows, key=lambda item: TUNES.index(item["tune"])):
            raw, raw_hash = validate_raw_binding(production, row, gate_b)
            tune = row["tune"]
            receipt = (
                production
                / "raw_validation"
                / tune
                / "job_000"
                / f"attempt_{int(row['attempt']):03d}"
                / "receipt.json"
            )
            raw_bindings.append(
                {
                    "tune": tune,
                    "logical_id": 0,
                    "attempt": int(row["attempt"]),
                    "seed": int(row["seed"]),
                    "raw_path": str(raw),
                    "raw_sha256": raw_hash,
                    "raw_validation_receipt_path": str(receipt),
                    "raw_validation_receipt_sha256": sha256(receipt),
                }
            )
            analyses = [(0, -1, central_directory(analysis, tune))]
            analyses.extend(
                (10, block - 1, block_directory(analysis, tune, block))
                for block in range(1, 11)
            )
            for modulo, remainder, output in analyses:
                environment = base_environment.copy()
                environment["HADRONIZATION_EVENT_FILTER_MODULO"] = str(
                    modulo
                )
                environment["HADRONIZATION_EVENT_FILTER_REMAINDER"] = str(
                    remainder
                )
                label = (
                    "central"
                    if modulo == 0
                    else f"block_{remainder + 1:02d}"
                )
                record = run_logged(
                    [
                        str(checkout / "run_status_analysis.sh"),
                        str(raw),
                        str(output),
                        campaign["campaign"],
                        tune,
                        "0",
                        raw_hash,
                        environment_evidence["repository_commit"],
                        macro_hash,
                        f"gate_d_{label}",
                    ],
                    logs / f"analysis_{tune}_{label}.log",
                    cwd=checkout,
                    environment=environment,
                )
                record["name"] = f"analysis_{tune}_{label}"
                commands.append(record)
                if (
                    record["returncode"] != 0
                    or record["compiler_warning_found"]
                ):
                    raise GateDFailure(
                        f"Gate-D analysis failed for {tune}/{label}"
                    )

        pair_inventory_path = write_pair_inventory(checkout, analysis)
        config = prepare_plot_config(checkout, analysis)
        plot_scope = smoke_scope_contract(
            load_json(config, "generated Gate-D plot configuration")
        )
        plot_provenance_state = (
            analysis / "gate_d_plot_provenance_snapshot.json"
        )
        provenance_tool = checkout / "tools" / "final_plot_provenance.py"
        provenance_snapshot_record = run_logged(
            [
                sys.executable,
                str(provenance_tool),
                "snapshot",
                "--checkout",
                str(checkout),
                "--state",
                str(plot_provenance_state),
                "--config",
                str(config),
            ],
            logs / "plot_provenance_snapshot.log",
            cwd=checkout,
            environment=base_environment,
        )
        provenance_snapshot_record["name"] = "plot_provenance_snapshot"
        commands.append(provenance_snapshot_record)
        if (
            provenance_snapshot_record["returncode"] != 0
            or provenance_snapshot_record["compiler_warning_found"]
        ):
            raise GateDFailure("Gate-D plot-provenance snapshot failed")
        plot_script = "\n".join(
            (
                (
                    ".L "
                    + str(
                        checkout
                        / "PlottingScripts/improvedPlotting_THnSparse.C"
                    )
                    + "+"
                ),
                (
                    "int gate_d_plot_status = "
                    f'improvedPlotting_THnSparse("{config}");'
                ),
                "gSystem->Exit(gate_d_plot_status);",
                "",
            )
        )
        plot_record = run_logged(
            ["root", "-l", "-b"],
            logs / "strict_coverage_and_plots.log",
            cwd=checkout,
            environment=base_environment,
            stdin=plot_script,
        )
        plot_record["name"] = "strict_coverage_and_plots"
        commands.append(plot_record)
        plot_text = Path(plot_record["log_path"]).read_text(
            errors="replace"
        )
        if (
            plot_record["returncode"] != 0
            or plot_record["compiler_warning_found"]
            or "SUBSAMPLE_COVERAGE_ERROR" in plot_text
            or "SUBSAMPLE_COVERAGE_FAILURE" in plot_text
        ):
            raise GateDFailure(
                "strict plotting/coverage validation did not pass"
            )
        subsample_validation = validate_subsample_log(
            plot_text, plot_scope
        )
        provenance_arguments = [
            sys.executable,
            str(provenance_tool),
            "record",
            "--checkout",
            str(checkout),
            "--state",
            str(plot_provenance_state),
            "--target",
            "gate-d-smoke",
            "--command",
            (
                f"{plot_record['command_display']} "
                "[stdin_sha256="
                f"{hashlib.sha256(plot_script.encode()).hexdigest()}]"
            ),
            "--mode",
            "gate-d",
            "--config",
            str(config),
            "--pair-inventory",
            str(pair_inventory_path),
            "--pilot-manifest",
            str(campaign_dir / "candidate_manifest.jsonl"),
            "--require-boundary-receipt",
        ]
        if args.development:
            provenance_arguments.append("--development")
        provenance_record = run_logged(
            provenance_arguments,
            logs / "final_plot_provenance.log",
            cwd=checkout,
            environment=base_environment,
        )
        provenance_record["name"] = "final_plot_provenance"
        commands.append(provenance_record)
        if (
            provenance_record["returncode"] != 0
            or provenance_record["compiler_warning_found"]
            or "FINAL_PLOT_PROVENANCE_PASS" not in Path(
                provenance_record["log_path"]
            ).read_text(errors="replace")
        ):
            raise GateDFailure(
                "Gate-D final-plot provenance certification failed"
            )
        plot_provenance_state.unlink()
        exhaustive_config = prepare_exhaustive_audit_config(
            checkout, analysis
        )
        exhaustive_scope = validate_exhaustive_audit_config(
            load_json(
                exhaustive_config,
                "generated Gate-D exhaustive-audit configuration",
            ),
            analysis,
        )
        exhaustive_script = "\n".join(
            (
                (
                    ".L "
                    + str(
                        checkout
                        / "PlottingScripts/improvedPlotting_THnSparse.C"
                    )
                    + "+"
                ),
                (
                    "int gate_d_audit_status = "
                    f'improvedPlotting_THnSparse("{exhaustive_config}");'
                ),
                "gSystem->Exit(gate_d_audit_status);",
                "",
            )
        )
        exhaustive_record = run_logged(
            ["root", "-l", "-b"],
            logs / "exhaustive_subsample_coverage_audit.log",
            cwd=checkout,
            environment=base_environment,
            stdin=exhaustive_script,
        )
        exhaustive_record[
            "name"
        ] = "exhaustive_subsample_coverage_audit"
        commands.append(exhaustive_record)
        exhaustive_text = Path(
            exhaustive_record["log_path"]
        ).read_text(errors="replace")
        if exhaustive_record["compiler_warning_found"]:
            raise GateDFailure(
                "exhaustive subsample audit emitted compiler warnings"
            )
        exhaustive_result = validate_exhaustive_audit_log(
            exhaustive_text, exhaustive_record["returncode"]
        )
        inventory = plot_inventory(analysis, checkout)
        inventory_path = analysis / "gate_d_plot_inventory.json"
        exclusive_text(
            inventory_path,
            json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        )
        rendered = analysis / "rendered_pdfs"
        rendered.mkdir(mode=0o700)
        for index, row in enumerate(
            item
            for item in inventory["files"]
            if item["path"].endswith(".pdf")
        ):
            pdf = analysis / row["path"]
            prefix = rendered / Path(row["path"]).stem
            record = run_logged(
                [
                    "pdftoppm",
                    "-png",
                    "-r",
                    "120",
                    str(pdf),
                    str(prefix),
                ],
                logs / f"render_pdf_{index:03d}.log",
                cwd=checkout,
            )
            record["name"] = f"render_pdf_{index:03d}"
            commands.append(record)
            if record["returncode"] != 0:
                raise GateDFailure(f"PDF rendering failed: {pdf}")
        rendered_files = list(rendered.glob("*.png"))
        if len(rendered_files) < inventory["pdf_count"]:
            raise GateDFailure("not every PDF produced a rendered page")
        render_inventory = {
            "schema": "hf_gate_d_render_inventory_v1",
            "source_plot_inventory_sha256": sha256(inventory_path),
            "subsample_statistic_records":
                subsample_validation["total_statistic_records"],
            "subsample_log_validation": subsample_validation,
            "rendered_page_count": len(rendered_files),
            "files": [
                {
                    "path": path.relative_to(analysis).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
                for path in sorted(rendered_files)
            ],
        }
        exclusive_text(
            analysis / "gate_d_render_inventory.json",
            json.dumps(render_inventory, indent=2, sort_keys=True) + "\n",
        )
        storage_projection = build_storage_projection(
            analysis=analysis,
            production=production,
            pair_inventory_path=pair_inventory_path,
            gate_b=gate_b,
            plot_inventory=inventory,
            render_inventory=render_inventory,
        )
        if storage_projection["state"] != "PASS":
            raise GateDFailure(
                "full candidate, analysis, and publication outputs do not "
                "fit the conservative storage-headroom policy"
            )
    except BaseException as error:
        failure = f"{type(error).__name__}: {error}"
        traceback_path = logs / "preparation_failure.log"
        if not traceback_path.exists():
            exclusive_text(traceback_path, traceback.format_exc())

    final_commit = git(checkout, "rev-parse", "HEAD")
    final_status = git(
        checkout, "status", "--porcelain=v1", "--untracked-files=all"
    )
    environment_evidence["final_repository_commit"] = final_commit
    environment_evidence["final_status"] = final_status
    if (
        final_commit != environment_evidence["repository_commit"]
        or final_status != environment_evidence["initial_status"]
    ):
        failure = failure or "Gate-D preparation changed checkout state"

    report = {
        "schema": PREPARATION_SCHEMA,
        "state": "PASS" if failure is None else "FAIL",
        "canonical": not args.development and failure is None,
        "repository_commit": environment_evidence["repository_commit"],
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
        "analysis_root": str(analysis),
        "production_root": str(production),
        "environment": environment_evidence,
        "analysis_layout": {
            "central": "complete_root_GATE_D_<TUNE>",
            "blocks": (
                "SUBSAMPLES/combined_root_subSamples_<TUNE>/"
                "combined_root_<1..10>"
            ),
            "event_filter": "unsigned_event_id_modulo_v1",
            "block_count": 10,
            "central_events_per_tune": 1_000_000,
        },
        "gate_b_report": {
            "path": str(args.gate_b_report.resolve()),
            "sha256": sha256(args.gate_b_report.resolve()),
        },
        "pilot_manifest": {
            "campaign_directory": str(campaign_dir),
            "campaign_json_sha256": sha256(campaign_dir / "campaign.json"),
            "candidate_manifest_sha256": sha256(
                campaign_dir / "candidate_manifest.jsonl"
            ),
            "seed_ledger_sha256": sha256(
                campaign_dir / "seed_ledger.jsonl"
            ),
            "selected_rows": 3,
        },
        "raw_inputs": raw_bindings,
        "pair_inventory": {
            "path": str(pair_inventory_path)
            if "pair_inventory_path" in locals()
            else None,
            "sha256": sha256(pair_inventory_path)
            if "pair_inventory_path" in locals()
            else None,
            "rows": 9900 if "pair_inventory_path" in locals() else 0,
        },
        "plot_configuration": {
            "path": str(config) if "config" in locals() else None,
            "sha256": sha256(config)
            if "config" in locals()
            else None,
            "scope": plot_scope
            if "plot_scope" in locals()
            else None,
        },
        "plot_outputs": {
            "inventory_path": str(inventory_path)
            if "inventory_path" in locals()
            else None,
            "inventory_sha256": sha256(inventory_path)
            if "inventory_path" in locals()
            else None,
            "render_inventory_path": str(
                analysis / "gate_d_render_inventory.json"
            )
            if "render_inventory" in locals()
            else None,
            "render_inventory_sha256": sha256(
                analysis / "gate_d_render_inventory.json"
            )
            if "render_inventory" in locals()
            else None,
            "multiplicity_boundary_receipt_sha256": (
                inventory.get("multiplicity_boundary_receipt", {}).get(
                    "sha256"
                )
                if "inventory" in locals()
                else None
            ),
            "output_provenance_sidecars": (
                inventory.get("output_provenance_sidecar_count", 0)
                if "inventory" in locals()
                else 0
            ),
        },
        "exhaustive_subsample_audit": {
            "configuration": {
                "path": str(exhaustive_config)
                if "exhaustive_config" in locals()
                else None,
                "sha256": sha256(exhaustive_config)
                if "exhaustive_config" in locals()
                else None,
                "scope": exhaustive_scope
                if "exhaustive_scope" in locals()
                else None,
            },
            "result": exhaustive_result
            if "exhaustive_result" in locals()
            else None,
        },
        "storage_projection": (
            storage_projection
            if "storage_projection" in locals()
            else None
        ),
        "commands": commands,
        "failure": failure,
        "created_utc": utc_now(),
    }
    report_path = analysis / "gate_d_preparation_report.json"
    exclusive_text(
        report_path,
        json.dumps(report, indent=2, sort_keys=True) + "\n",
    )
    print(report_path.read_text(), end="")
    return 0 if failure is None else 1


def validate_human_report(
    path: Path,
    *,
    schema: str,
    commit: str,
    preparation_sha: str,
) -> dict[str, Any]:
    report = load_json(path, schema)
    expected = {
        "schema": schema,
        "state": "PASS",
        "repository_commit": commit,
        "gate_d_preparation_sha256": preparation_sha,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            raise GateDFailure(f"{schema} {key} differs")
    reviewer = report.get("reviewer")
    reviewed = report.get("reviewed_utc")
    if (
        not isinstance(reviewer, str)
        or not reviewer.strip()
        or "PLACEHOLDER" in reviewer.upper()
        or not isinstance(reviewed, str)
    ):
        raise GateDFailure(f"{schema} lacks a real reviewer/timestamp")
    try:
        timestamp = datetime.datetime.fromisoformat(reviewed)
    except ValueError as error:
        raise GateDFailure(f"{schema} timestamp is invalid") from error
    if (
        timestamp.tzinfo is None
        or timestamp.utcoffset() != datetime.timedelta(0)
    ):
        raise GateDFailure(f"{schema} timestamp must be UTC")
    return report


def validate_visual_report(
    path: Path,
    commit: str,
    preparation_sha: str,
    inventory_sha: str,
    render_inventory_sha: str,
    expected_pdf_count: int,
) -> dict[str, Any]:
    report = validate_human_report(
        path,
        schema=VISUAL_SCHEMA,
        commit=commit,
        preparation_sha=preparation_sha,
    )
    if report.get("plot_inventory_sha256") != inventory_sha:
        raise GateDFailure("visual review binds a different plot inventory")
    if (
        report.get("render_inventory_sha256") != render_inventory_sha
        or report.get("pdf_count_inspected") != expected_pdf_count
    ):
        raise GateDFailure(
            "visual review does not bind every rendered PDF"
        )
    checks = report.get("checks")
    required = {
        "all_pdf_pages_inspected",
        "visible_finite_error_bars",
        "correct_tune_ratio_styles",
        "readable_legends",
        "correct_multiplicity_ordering",
        "no_clipping",
        "no_empty_pads",
    }
    if (
        not isinstance(checks, dict)
        or not required.issubset(checks)
        or any(checks[key] is not True for key in required)
        or report.get("findings") not in ([], None)
    ):
        raise GateDFailure("visual review retains unchecked or failed items")
    return report


def validate_legacy_report(
    path: Path, commit: str, preparation_sha: str
) -> dict[str, Any]:
    report = validate_human_report(
        path,
        schema=LEGACY_SCHEMA,
        commit=commit,
        preparation_sha=preparation_sha,
    )
    if set(report.get("approved_difference_categories", [])) != (
        REQUIRED_DIFFERENCES
    ):
        raise GateDFailure(
            "legacy comparison does not cover exactly the approved "
            "central-selector differences"
        )
    legacy = report.get("legacy_dataset")
    comparison_artifact = report.get("comparison_artifact")
    rows = report.get("comparison_rows")
    if (
        not isinstance(legacy, dict)
        or not isinstance(comparison_artifact, dict)
        or not isinstance(rows, list)
        or not rows
    ):
        raise GateDFailure("legacy comparison evidence is incomplete")

    def bound_artifact(binding: dict, label: str) -> Path:
        artifact = Path(str(binding.get("path", ""))).expanduser().resolve()
        expected_sha = binding.get("sha256")
        expected_bytes = binding.get("bytes")
        if (
            artifact.is_symlink()
            or not artifact.is_file()
            or artifact.stat().st_size <= 0
            or not isinstance(expected_sha, str)
            or not HEX64.fullmatch(expected_sha)
            or sha256(artifact) != expected_sha
            or isinstance(expected_bytes, bool)
            or not isinstance(expected_bytes, int)
            or expected_bytes != artifact.stat().st_size
        ):
            raise GateDFailure(f"{label} binding is absent or stale")
        return artifact

    bound_artifact(
        {
            "path": legacy.get("inventory_path"),
            "sha256": legacy.get("inventory_sha256"),
            "bytes": legacy.get("inventory_bytes"),
        },
        "legacy dataset inventory",
    )
    bound_artifact(comparison_artifact, "legacy comparison artifact")
    limitations = set(legacy.get("provenance_limitations", []))
    required_limitations = {
        "seed_uniqueness_not_provable_from_outputs",
        "raw_files_lack_seed_metadata",
    }
    if (
        not isinstance(legacy.get("description"), str)
        or not legacy["description"].strip()
        or legacy.get("provenance_status")
        != "LEGACY_INCOMPLETE_NO_SEED_METADATA"
        or limitations != required_limitations
        or legacy.get("tunes") != list(TUNES)
        or legacy.get("events_per_tune") != 100_000_000
        or isinstance(legacy.get("file_count"), bool)
        or not isinstance(legacy.get("file_count"), int)
        or legacy["file_count"] <= 0
        or comparison_artifact.get("row_count") != len(rows)
    ):
        raise GateDFailure(
            "legacy dataset provenance/limitations are not explicit"
        )

    coverage: set[tuple[str, str]] = set()
    used_categories: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise GateDFailure("legacy comparison row is not an object")
        flavour = row.get("flavour")
        tune = row.get("tune")
        observable = row.get("observable")
        status = row.get("status")
        legacy_value = row.get("legacy_value")
        gate_d_value = row.get("gate_d_value")
        absolute_difference = row.get("absolute_difference")
        relative_difference = row.get("relative_difference")
        tolerance = row.get("acceptance_tolerance")
        numbers = (
            legacy_value,
            gate_d_value,
            absolute_difference,
            tolerance,
        )
        if (
            flavour not in {"charm", "beauty"}
            or tune not in TUNES
            or not isinstance(observable, str)
            or not observable.strip()
            or status not in {"AGREES", "EXPECTED_DIFFERENCE"}
            or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                for value in numbers
            )
            or absolute_difference < 0.0
            or tolerance < 0.0
            or not math.isclose(
                absolute_difference,
                abs(gate_d_value - legacy_value),
                rel_tol=1e-12,
                abs_tol=1e-15,
            )
        ):
            raise GateDFailure("legacy comparison row is malformed")
        expected_relative = (
            absolute_difference / abs(legacy_value)
            if legacy_value != 0.0
            else None
        )
        if (
            (expected_relative is None and relative_difference is not None)
            or (
                expected_relative is not None
                and (
                    isinstance(relative_difference, bool)
                    or not isinstance(relative_difference, (int, float))
                    or not math.isfinite(relative_difference)
                    or not math.isclose(
                        relative_difference,
                        expected_relative,
                        rel_tol=1e-12,
                        abs_tol=1e-15,
                    )
                )
            )
        ):
            raise GateDFailure(
                "legacy comparison relative difference is inconsistent"
            )
        categories = row.get("difference_categories", [])
        if (
            not isinstance(categories, list)
            or len(categories) != len(set(categories))
            or not set(categories).issubset(REQUIRED_DIFFERENCES)
        ):
            raise GateDFailure(
                "legacy comparison difference categories are invalid"
            )
        if status == "AGREES":
            if absolute_difference > tolerance or categories:
                raise GateDFailure(
                    "legacy AGREES row exceeds tolerance/has categories"
                )
        else:
            if (
                absolute_difference <= tolerance
                or not categories
                or not isinstance(row.get("physics_interpretation"), str)
                or not row["physics_interpretation"].strip()
            ):
                raise GateDFailure(
                    "legacy EXPECTED_DIFFERENCE row is not justified"
                )
            used_categories.update(categories)
        coverage.add((flavour, tune))
    expected_coverage = {
        (flavour, tune)
        for flavour in ("charm", "beauty")
        for tune in TUNES
    }
    if coverage != expected_coverage or used_categories != REQUIRED_DIFFERENCES:
        raise GateDFailure(
            "legacy comparison lacks charm/beauty/all-tune coverage or "
            "does not exercise every approved difference category"
        )
    return report


def seal_tree(path: Path) -> None:
    for item in sorted(
        path.rglob("*"), key=lambda candidate: len(candidate.parts), reverse=True
    ):
        if item.is_symlink():
            raise GateDFailure(f"evidence tree contains symlink: {item}")
        mode = item.stat().st_mode
        if item.is_dir():
            item.chmod((mode & ~0o222) | stat.S_IXUSR)
        else:
            item.chmod(mode & ~0o222)
    path.chmod(0o500)


def finalize(args: argparse.Namespace) -> int:
    checkout = args.checkout_root.resolve()
    output = args.output_directory.resolve()
    if output.exists() or output.is_symlink():
        raise GateDFailure(f"Gate-D output already exists: {output}")
    output.mkdir(parents=True, mode=0o700)
    command_logs = output / "command_logs"
    command_logs.mkdir(mode=0o700)
    environment = validate_checkout(checkout, args.development)
    analysis = args.analysis_root.resolve()
    preparation_path = analysis / "gate_d_preparation_report.json"
    preparation = load_json(preparation_path, "Gate-D preparation report")
    preparation_sha = sha256(preparation_path)
    commands: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    failure: str | None = None
    final_storage_projection: dict[str, Any] | None = None
    final_capacity_recheck: dict[str, Any] | None = None

    def requirement(
        number: int, title: str, passed: bool, evidence: Any, reason: str = ""
    ) -> None:
        requirements.append(
            {
                "number": number,
                "title": title,
                "state": "PASS" if passed else "FAIL",
                "evidence": evidence,
                "failure": None if passed else reason,
            }
        )

    try:
        if (
            preparation.get("schema") != PREPARATION_SCHEMA
            or preparation.get("state") != "PASS"
            or preparation.get("canonical") is not True
            or preparation.get("repository_commit")
            != environment["repository_commit"]
            or Path(preparation.get("analysis_root", "")).resolve()
            != analysis
        ):
            raise GateDFailure(
                "Gate-D preparation is not a canonical PASS for this checkout"
            )
        gate_b_path = Path(preparation["gate_b_report"]["path"])
        campaign_dir = args.campaign_dir.resolve()
        campaign, _, gate_b = validate_campaign(
            campaign_dir, gate_b_path, environment["repository_commit"]
        )
        production = Path(
            str(preparation.get("production_root", ""))
        ).resolve()
        if (
            not production.is_dir()
            or any(
                not Path(str(row.get("raw_path", ""))).resolve().is_relative_to(
                    production
                )
                for row in preparation.get("raw_inputs", [])
                if isinstance(row, dict)
            )
        ):
            raise GateDFailure(
                "prepared production-root binding is absent or inconsistent"
            )
        manifest_binding = preparation.get("pilot_manifest")
        if not isinstance(manifest_binding, dict):
            raise GateDFailure("preparation lacks pilot-manifest binding")
        expected_manifest_hashes = {
            "campaign_json_sha256": sha256(
                campaign_dir / "campaign.json"
            ),
            "candidate_manifest_sha256": sha256(
                campaign_dir / "candidate_manifest.jsonl"
            ),
            "seed_ledger_sha256": sha256(
                campaign_dir / "seed_ledger.jsonl"
            ),
            "selected_rows": 3,
        }
        if Path(
            str(manifest_binding.get("campaign_directory", ""))
        ).resolve() != campaign_dir:
            raise GateDFailure(
                "prepared pilot-manifest binding changed: "
                "campaign_directory"
            )
        for key, value in expected_manifest_hashes.items():
            if manifest_binding.get(key) != value:
                raise GateDFailure(
                    f"prepared pilot-manifest binding changed: {key}"
                )
        raw_bindings = preparation.get("raw_inputs")
        if not isinstance(raw_bindings, list) or len(raw_bindings) != 3:
            raise GateDFailure("preparation lacks three exact raw bindings")
        for binding in raw_bindings:
            raw = Path(str(binding.get("raw_path", "")))
            receipt = Path(
                str(binding.get("raw_validation_receipt_path", ""))
            )
            if (
                raw.is_symlink()
                or not raw.is_file()
                or sha256(raw) != binding.get("raw_sha256")
                or receipt.is_symlink()
                or not receipt.is_file()
                or sha256(receipt)
                != binding.get("raw_validation_receipt_sha256")
            ):
                raise GateDFailure(
                    f"prepared raw/receipt binding changed: "
                    f"{binding.get('tune')}"
                )
        pair_binding = preparation.get("pair_inventory")
        if not isinstance(pair_binding, dict):
            raise GateDFailure("preparation lacks pair checksum inventory")
        pair_inventory_path = Path(str(pair_binding.get("path", "")))
        if (
            pair_inventory_path.resolve()
            != (analysis / "gate_d_pair_inventory.jsonl").resolve()
            or pair_inventory_path.is_symlink()
            or not pair_inventory_path.is_file()
            or pair_binding.get("rows") != 9900
            or sha256(pair_inventory_path) != pair_binding.get("sha256")
        ):
            raise GateDFailure("prepared pair inventory binding changed")
        validate_pair_inventory(
            checkout, analysis, pair_inventory_path
        )
        validate_preparation_commands(preparation, analysis)
        plot_config_binding = preparation.get("plot_configuration")
        if not isinstance(plot_config_binding, dict):
            raise GateDFailure(
                "preparation lacks generated plot-configuration binding"
            )
        plot_config_path = Path(
            str(plot_config_binding.get("path", ""))
        )
        if (
            plot_config_path.resolve()
            != (analysis / "gate_d_plot_config.json").resolve()
            or plot_config_path.is_symlink()
            or not plot_config_path.is_file()
            or sha256(plot_config_path)
            != plot_config_binding.get("sha256")
        ):
            raise GateDFailure(
                "prepared Gate-D plot configuration changed"
            )
        plot_scope = smoke_scope_contract(
            load_json(
                plot_config_path, "generated Gate-D plot configuration"
            )
        )
        if plot_config_binding.get("scope") != plot_scope:
            raise GateDFailure(
                "prepared Gate-D plot smoke scope changed"
            )
        exhaustive_binding = preparation.get(
            "exhaustive_subsample_audit"
        )
        exhaustive_config_binding = (
            exhaustive_binding.get("configuration")
            if isinstance(exhaustive_binding, dict)
            else None
        )
        if not isinstance(exhaustive_config_binding, dict):
            raise GateDFailure(
                "preparation lacks exhaustive subsample-audit binding"
            )
        exhaustive_config_path = Path(
            str(exhaustive_config_binding.get("path", ""))
        )
        if (
            exhaustive_config_path.resolve()
            != (
                analysis
                / "gate_d_exhaustive_subsample_audit_config.json"
            ).resolve()
            or exhaustive_config_path.is_symlink()
            or not exhaustive_config_path.is_file()
            or sha256(exhaustive_config_path)
            != exhaustive_config_binding.get("sha256")
        ):
            raise GateDFailure(
                "prepared exhaustive subsample-audit configuration changed"
            )
        exhaustive_scope = validate_exhaustive_audit_config(
            load_json(
                exhaustive_config_path,
                "generated Gate-D exhaustive-audit configuration",
            ),
            analysis,
        )
        if exhaustive_config_binding.get("scope") != exhaustive_scope:
            raise GateDFailure(
                "prepared exhaustive subsample-audit scope changed"
            )

        pair_logs = []
        base_environment = os.environ.copy()
        base_environment["HADRONIZATION_BASE"] = str(checkout)
        for tune in TUNES:
            directories = [central_directory(analysis, tune)]
            directories.extend(
                block_directory(analysis, tune, block)
                for block in range(1, 11)
            )
            for index, directory in enumerate(directories):
                label = "central" if index == 0 else f"block_{index:02d}"
                record = run_logged(
                    [
                        str(
                            checkout
                            / "Validation/validate_pair_directory.sh"
                        ),
                        str(directory),
                    ],
                    command_logs
                    / f"pair_contract_{tune}_{label}.log",
                    cwd=checkout,
                    environment=base_environment,
                )
                record["name"] = f"pair_contract_{tune}_{label}"
                commands.append(record)
                pair_logs.append(record)
                if (
                    record["returncode"] != 0
                    or record["compiler_warning_found"]
                ):
                    raise GateDFailure(
                        f"pair contract failed for {tune}/{label}"
                    )
        requirement(
            1,
            "One-pass charge-resolved analysis for all central pairs",
            True,
            {"directories": 33, "pair_files": 9900},
        )
        requirement(
            2,
            "Legacy ROOT compatibility objects",
            True,
            {
                "validator": "ValidatePairDirectory.C",
                "objects": [
                    "summed MULTIPLICITY",
                    "hTrKinematics",
                    "hAsKinematics",
                    "hCorrelations",
                ],
            },
        )
        requirement(
            3,
            "Axis flow audit and no implicit upper cuts",
            True,
            {
                "pair_directory_validations": len(pair_logs),
                "physical_pt_axis_endpoint": 7000.0,
                "selection_upper_pt_cut": None,
            },
        )

        audit_macro = (
            checkout / "Validation/ValidateGateDPilotAnalysis.C"
        )
        audit_script = "\n".join(
            (
                f".L {audit_macro}+",
                (
                    "int gate_d_status = ValidateGateDPilotAnalysis("
                    f'"{analysis}");'
                ),
                "gSystem->Exit(gate_d_status);",
                "",
            )
        )
        audit_record = run_logged(
            ["root", "-l", "-b"],
            command_logs / "gate_d_analysis_audit.log",
            cwd=checkout,
            environment=base_environment,
            stdin=audit_script,
        )
        audit_record["name"] = "gate_d_analysis_audit"
        commands.append(audit_record)
        audit_text = Path(audit_record["log_path"]).read_text(
            errors="replace"
        )
        match = ANALYSIS_SUMMARY.findall(audit_text)
        if (
            audit_record["returncode"] != 0
            or audit_record["compiler_warning_found"]
            or len(match) != 1
            or "GATE_D_ANALYSIS_ERROR" in audit_text
        ):
            raise GateDFailure("Gate-D central/block/statistical audit failed")
        summary_counts = [int(value) for value in match[0]]
        finite_counts = summary_counts[:5]
        diagnostic_counts = summary_counts[5:]
        if any(value <= 0 for value in finite_counts):
            raise GateDFailure(
                "Gate-D statistical audit has no finite rows in a required "
                "estimator family"
            )
        requirement(
            4,
            "Corrected B0/Sigma_b trigger and filename",
            True,
            {"filename": "BzeroSigmabzero.root", "trigger_pdg": 511},
        )

        legacy = validate_legacy_report(
            args.legacy_comparison_report.resolve(),
            environment["repository_commit"],
            preparation_sha,
        )
        human_evidence = output / "human_evidence"
        human_evidence.mkdir(mode=0o700)
        legacy_snapshots = {}
        for label, source in (
            ("report", args.legacy_comparison_report.resolve()),
            (
                "dataset_inventory",
                Path(
                    legacy["legacy_dataset"]["inventory_path"]
                ).expanduser().resolve(),
            ),
            (
                "comparison_artifact",
                Path(
                    legacy["comparison_artifact"]["path"]
                ).expanduser().resolve(),
            ),
        ):
            suffix = source.suffix if source.suffix else ".bin"
            destination = human_evidence / f"legacy_{label}{suffix}"
            exclusive_bytes(destination, source.read_bytes())
            legacy_snapshots[label] = {
                "path": destination.relative_to(output).as_posix(),
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
        requirement(
            5,
            "Documented comparison with legacy 100M selector output",
            True,
            {
                "report_path": str(args.legacy_comparison_report.resolve()),
                "report_sha256": sha256(
                    args.legacy_comparison_report.resolve()
                ),
                "comparison_rows": len(legacy["comparison_rows"]),
                "immutable_snapshots": legacy_snapshots,
            },
        )
        requirement(
            6,
            "Expected central-selector differences are accounted for",
            True,
            {"categories": sorted(REQUIRED_DIFFERENCES)},
        )
        requirement(
            7,
            "All-primary-heavy closure and central ground-state coverage",
            True,
            {
                "closure_source": (
                    "raw primary_all_heavy_match_valid and independently "
                    "validated pair metadata"
                ),
                "closure_failures": 0,
            },
        )
        requirement(
            8,
            "Central plus ten disjoint event-ID-modulo blocks",
            True,
            {
                "central_events_per_tune": 1_000_000,
                "blocks": 10,
                "partition": "unsigned_event_id_modulo_v1",
                "histogram_union_checks": 4500,
            },
        )
        requirement(
            9,
            "SEM, covariance, nonlinear ratios, independent-tune propagation",
            True,
            {
                "finite_estimator_family_counts": {
                    "yield": finite_counts[0],
                    "balancing": finite_counts[1],
                    "baryon_reference_ratio": finite_counts[2],
                    "independent_tune_ratio": finite_counts[3],
                    "independent_baryon_tune_double_ratio":
                        finite_counts[4],
                },
                "full_inventory_diagnostics": {
                    "zero_yield_sem_rows": diagnostic_counts[0],
                    "nonfinite_yield_rows": diagnostic_counts[1],
                    "zero_balancing_sem_rows": diagnostic_counts[2],
                    "nonfinite_balancing_rows": diagnostic_counts[3],
                    "zero_baryon_ratio_sem_rows": diagnostic_counts[4],
                    "nonfinite_baryon_ratio_rows":
                        diagnostic_counts[5],
                    "zero_baryon_ratio_denominators":
                        diagnostic_counts[6],
                    "zero_tune_ratio_error_rows": diagnostic_counts[7],
                    "nonfinite_tune_ratio_rows": diagnostic_counts[8],
                    "zero_baryon_tune_double_ratio_error_rows":
                        diagnostic_counts[9],
                    "nonfinite_baryon_tune_double_ratio_rows":
                        diagnostic_counts[10],
                    "scope": (
                        "all 300 pair definitions; configured plotted "
                        "points are separately required finite/nonzero by "
                        "the strict plotting log"
                    ),
                },
                "sem": (
                    "sqrt(sum((x_k-xbar)^2)/(K*(K-1))), K=10"
                ),
                "independent_tunes": "quadrature",
            },
        )

        plot_inventory_path = analysis / "gate_d_plot_inventory.json"
        render_inventory_path = (
            analysis / "gate_d_render_inventory.json"
        )
        inventory = load_json(
            plot_inventory_path, "Gate-D plot inventory"
        )
        prepared_plot_outputs = preparation.get("plot_outputs")
        if (
            not isinstance(prepared_plot_outputs, dict)
            or Path(
                str(prepared_plot_outputs.get("inventory_path", ""))
            ).resolve()
            != plot_inventory_path.resolve()
            or prepared_plot_outputs.get("inventory_sha256")
            != sha256(plot_inventory_path)
            or Path(
                str(
                    prepared_plot_outputs.get(
                        "render_inventory_path", ""
                    )
                )
            ).resolve()
            != render_inventory_path.resolve()
            or prepared_plot_outputs.get("render_inventory_sha256")
            != sha256(render_inventory_path)
            or prepared_plot_outputs.get(
                "multiplicity_boundary_receipt_sha256"
            )
            != inventory.get("multiplicity_boundary_receipt", {}).get(
                "sha256"
            )
            or prepared_plot_outputs.get("output_provenance_sidecars")
            != inventory.get("output_provenance_sidecar_count")
            or inventory.get("schema")
            != "hf_gate_d_plot_inventory_v1"
            or int(inventory.get("pdf_count", 0)) <= 0
            or inventory.get("pdf_count") != inventory.get("png_count")
            or inventory.get("pdf_count") != inventory.get("macro_count")
            or inventory.get("output_provenance_sidecar_count")
            != (
                int(inventory.get("pdf_count", 0))
                + int(inventory.get("png_count", 0))
                + int(inventory.get("macro_count", 0))
            )
            or inventory.get("run_provenance_receipt_count") != 1
            or not isinstance(
                inventory.get("multiplicity_boundary_receipt"), dict
            )
            or not HEX64.fullmatch(
                str(
                    inventory["multiplicity_boundary_receipt"].get(
                        "sha256", ""
                    )
                )
            )
        ):
            raise GateDFailure("Gate-D plot inventory is invalid")
        validate_artifact_inventory(analysis, inventory, "plots")
        render_inventory = load_json(
            render_inventory_path, "Gate-D render inventory"
        )
        if (
            render_inventory.get("schema")
            != "hf_gate_d_render_inventory_v1"
            or render_inventory.get("source_plot_inventory_sha256")
            != sha256(plot_inventory_path)
            or int(render_inventory.get("rendered_page_count", 0))
            < int(inventory["pdf_count"])
            or int(
                render_inventory.get("subsample_statistic_records", 0)
            )
            <= 0
            or not isinstance(
                render_inventory.get("subsample_log_validation"), dict
            )
        ):
            raise GateDFailure("Gate-D render inventory is invalid")
        validate_artifact_inventory(
            analysis, render_inventory, "rendered_pdfs"
        )
        (
            final_storage_projection,
            final_capacity_recheck,
        ) = validate_and_recheck_storage_projection(
            stored=preparation.get("storage_projection"),
            analysis=analysis,
            production=production,
            pair_inventory_path=pair_inventory_path,
            gate_b=gate_b,
            plot_inventory=inventory,
            render_inventory=render_inventory,
        )
        if final_capacity_recheck["state"] != "PASS":
            raise GateDFailure(
                "current storage headroom no longer permits the full "
                "candidate campaign and analysis"
            )
        preparation_plot_commands = [
            row
            for row in preparation.get("commands", [])
            if row.get("name") == "strict_coverage_and_plots"
        ]
        if (
            len(preparation_plot_commands) != 1
            or preparation_plot_commands[0].get("returncode") != 0
        ):
            raise GateDFailure(
                "preparation lacks strict coverage/plot PASS command"
            )
        strict_plot_log = Path(
            str(preparation_plot_commands[0].get("log_path", ""))
        )
        subsample_validation = validate_subsample_log(
            strict_plot_log.read_text(errors="replace"), plot_scope
        )
        if (
            render_inventory["subsample_statistic_records"]
            != subsample_validation["total_statistic_records"]
            or render_inventory["subsample_log_validation"]
            != subsample_validation
        ):
            raise GateDFailure(
                "prepared subsample-log classification changed"
            )
        requirement(
            10,
            "Strict input and exhaustive subsample-coverage validators",
            True,
            {
                "strict_coverage_log_sha256":
                    preparation_plot_commands[0]["log_sha256"],
                "excluded_bins": [],
                "smoke_scope": plot_scope,
                "subsample_log_validation": subsample_validation,
                "exhaustive_full_paper_scope": exhaustive_scope,
                "exhaustive_audit_result":
                    exhaustive_binding["result"],
                "coverage_interpretation": (
                    "A nonzero full-scope pilot failure count is retained "
                    "as an explicit production-sizing result and forbids "
                    "publication promotion; the configured representative "
                    "smoke points must still pass n=10 with positive finite "
                    "SEM."
                ),
            },
        )

        visual = validate_visual_report(
            args.visual_review_report.resolve(),
            environment["repository_commit"],
            preparation_sha,
            sha256(plot_inventory_path),
            sha256(render_inventory_path),
            int(inventory["pdf_count"]),
        )
        visual_snapshot = human_evidence / "visual_review_report.json"
        exclusive_bytes(
            visual_snapshot,
            args.visual_review_report.resolve().read_bytes(),
        )
        requirement(
            11,
            "Representative plots rendered and visually inspected",
            True,
            {
                "visual_review_path":
                    str(args.visual_review_report.resolve()),
                "visual_review_sha256":
                    sha256(args.visual_review_report.resolve()),
                "reviewer": visual["reviewer"],
                "pdf_count": inventory["pdf_count"],
                "immutable_snapshot": {
                    "path": visual_snapshot.relative_to(output).as_posix(),
                    "bytes": visual_snapshot.stat().st_size,
                    "sha256": sha256(visual_snapshot),
                },
            },
        )
        requirement(
            12,
            "Measured full-campaign storage projection",
            True,
            {
                "schema": final_storage_projection["schema"],
                "state": final_storage_projection["state"],
                "gate_e_storage_authorized":
                    final_storage_projection[
                        "gate_e_storage_authorized"
                    ],
                "projected_required_additional_bytes":
                    final_storage_projection["projected_components"][
                        "total_required_additional_bytes"
                    ],
                "preparation_capacity_check":
                    final_storage_projection[
                        "preparation_capacity_check"
                    ],
            },
        )
        requirement(
            13,
            "Fresh finalization-time storage-capacity recheck",
            True,
            {
                "state": final_capacity_recheck["state"],
                "gate_e_storage_authorized":
                    final_storage_projection[
                        "gate_e_storage_authorized"
                    ],
                "capacity_recheck": final_capacity_recheck,
            },
        )
    except BaseException as error:
        failure = f"{type(error).__name__}: {error}"
        requirement(
            len(requirements) + 1,
            "Uncompleted Gate-D requirement",
            False,
            {},
            failure,
        )

    final_status = git(
        checkout, "status", "--porcelain=v1", "--untracked-files=all"
    )
    final_commit = git(checkout, "rev-parse", "HEAD")
    environment["final_status"] = final_status
    environment["final_repository_commit"] = final_commit
    if (
        final_status != environment["initial_status"]
        or final_commit != environment["repository_commit"]
    ):
        failure = failure or "Gate-D validation changed checkout state"
    if args.development:
        failure = failure or "development mode cannot produce canonical PASS"
    if len(requirements) != 13 or any(
        row["state"] != "PASS" for row in requirements
    ):
        failure = failure or "Gate-D requirements are incomplete or failed"

    combined_log = output / "gate_d.log"
    sections = []
    for record in commands:
        path = Path(record["log_path"])
        sections.extend(
            [
                f"COMMAND name={record['name']}",
                f"RETURN_CODE {record['returncode']}",
                path.read_text(errors="replace"),
                "",
            ]
        )
    if failure:
        sections.append(f"PUBLICATION_GATE_D_FAIL {failure}")
    else:
        sections.append("PUBLICATION_GATE_D_PASS requirements=13/13")
    exclusive_text(combined_log, "\n".join(sections) + "\n")
    for record in commands:
        path = Path(record["log_path"])
        record["log_path"] = path.relative_to(output).as_posix()

    state = "PASS" if failure is None else "FAIL"
    report = {
        "schema": REPORT_SCHEMA,
        "state": state,
        "canonical": not args.development and state == "PASS",
        "repository_commit": environment["repository_commit"],
        "campaign": campaign.get("campaign") if "campaign" in locals() else None,
        "campaign_ordinal": (
            campaign.get("campaign_ordinal")
            if "campaign" in locals()
            else None
        ),
        "created_utc": utc_now(),
        "environment": environment,
        "preparation": {
            "path": str(preparation_path),
            "sha256": preparation_sha,
        },
        "pilot_inputs": {
            "manifest": preparation.get("pilot_manifest"),
            "raw_files": preparation.get("raw_inputs"),
            "pair_inventory": preparation.get("pair_inventory"),
            "gate_b_report": preparation.get("gate_b_report"),
        },
        "storage_projection": (
            final_storage_projection
            if final_storage_projection is not None
            else preparation.get("storage_projection")
        ),
        "requirements": requirements,
        "commands": commands,
        "failure": failure,
        "log_path": combined_log.name,
        "log_sha256": sha256(combined_log),
    }
    report_path = output / "gate_d_report.json"
    exclusive_text(
        report_path,
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    inventory_rows = []
    for path in sorted(
        item for item in output.rglob("*") if item.is_file()
    ):
        if path.name == "gate_d_inventory.json":
            continue
        inventory_rows.append(
            {
                "path": path.relative_to(output).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    inventory_path = output / "gate_d_inventory.json"
    exclusive_text(
        inventory_path,
        json.dumps(
            {
                "schema": INVENTORY_SCHEMA,
                "state": state,
                "repository_commit": environment["repository_commit"],
                "files": inventory_rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    seal_tree(output)
    print(report_path.read_text(), end="")
    return 0 if state == "PASS" else 1


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description=(
            "Prepare or finalize the immutable Section-16 publication Gate D"
        )
    )
    subparsers = value.add_subparsers(dest="action", required=True)
    prepare_parser = subparsers.add_parser(
        "prepare",
        help=(
            "create central+10-block pilot analyses and representative plots; "
            "run the exhaustive full-paper coverage sizing audit; project "
            "full-campaign storage; does not claim human review"
        ),
    )
    prepare_parser.add_argument("analysis_root", type=Path)
    prepare_parser.add_argument("--campaign-dir", type=Path, required=True)
    prepare_parser.add_argument("--production-root", type=Path, required=True)
    prepare_parser.add_argument("--gate-b-report", type=Path, required=True)
    prepare_parser.add_argument(
        "--checkout-root", type=Path, default=ROOT
    )
    prepare_parser.add_argument("--development", action="store_true")
    prepare_parser.set_defaults(function=prepare)

    finalize_parser = subparsers.add_parser(
        "finalize",
        help=(
            "revalidate a PASS preparation and require explicit legacy and "
            "human visual-review evidence plus a fresh storage-capacity check"
        ),
    )
    finalize_parser.add_argument("output_directory", type=Path)
    finalize_parser.add_argument("--analysis-root", type=Path, required=True)
    finalize_parser.add_argument("--campaign-dir", type=Path, required=True)
    finalize_parser.add_argument(
        "--legacy-comparison-report", type=Path, required=True
    )
    finalize_parser.add_argument(
        "--visual-review-report", type=Path, required=True
    )
    finalize_parser.add_argument(
        "--checkout-root", type=Path, default=ROOT
    )
    finalize_parser.add_argument("--development", action="store_true")
    finalize_parser.set_defaults(function=finalize)
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        return int(args.function(args))
    except Exception as error:
        print(f"PUBLICATION_GATE_D_ERROR {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
