#!/usr/bin/env python3
"""Independent partition-sensitivity audit for final balancing observables.

The tool consumes only a sealed equal-tune canonical freeze and the
corresponding per-job Paul-compatible pair directories. It intentionally
makes no publication decision: the primary 10-block, largest equal-exposure
modulo partition not exceeding 20 blocks, and delete-one estimates are
reported side by side for expert review without an invented agreement
threshold.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import statistics
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence


SPEC_SCHEMA = "hf_statistical_robustness_spec_v1"
REPORT_SCHEMA = "hf_statistical_robustness_report_v1"
RESULT_SCHEMA = "hf_statistical_robustness_result_v1"
INVENTORY_SCHEMA = "hf_statistical_robustness_input_inventory_v1"
BOUNDARY_RECEIPT_SCHEMA = "hadronization_multiplicity_boundary_receipt_v1"
ORIGIN_CLOSURE_REPORT_SCHEMA = "hf_final_origin_closure_report_v1"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
EXPECTED_TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
MINIMUM_SLOTS = 100
_ROOT_HELPERS_DECLARED = False


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def json_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text().splitlines()
    except OSError as error:
        raise ValueError(f"cannot read JSONL {path}: {error}") from error
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"invalid JSONL object at {path}:{line_number}: {error}"
            ) from error
        if not isinstance(value, dict):
            raise ValueError(f"expected an object at {path}:{line_number}")
        rows.append(value)
    return rows


def require_finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} is not numeric: {value!r}")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} is not finite: {value!r}")
    return result


def require_int(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{label} is not an integer >= {minimum}: {value!r}")
    return value


def require_signed_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} is not an integer: {value!r}")
    return value


def nearly_equal(
    first: float, second: float, relative_tolerance: float = 1.0e-10
) -> bool:
    return abs(first - second) <= relative_tolerance * max(
        1.0, abs(first), abs(second)
    )


def validate_spec(spec: dict[str, Any], checkout: Path) -> dict[tuple[int, int], dict]:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("frozen") is not True:
        raise ValueError("statistical-robustness specification is not frozen v1")
    if (
        spec.get("scientific_review_status")
        != "PENDING_FINAL_PHYSICS_STATISTICS_REVIEW"
        or not isinstance(spec.get("fixed_nch_rationale"), str)
        or not spec["fixed_nch_rationale"].strip()
    ):
        raise ValueError(
            "statistical-robustness fixed-Nch review status/rationale is "
            "absent"
        )
    contracts = spec.get("contracts")
    method = spec.get("method")
    integration = spec.get("integration")
    if not isinstance(contracts, dict) or not isinstance(method, dict):
        raise ValueError("specification contracts/method are absent")
    expected_contracts = {
        "canonical_manifest_schema": "hf_canonical_raw_manifest_v2",
        "superseding_canonical_manifest_schema":
            "hf_superseding_canonical_raw_manifest_v3",
        "canonical_summary_schema": "hf_canonical_freeze_summary_v3",
        "superseding_canonical_summary_schema":
            "hf_superseding_canonical_freeze_summary_v4",
        "canonical_validation_receipt_schema":
            "hf_canonical_raw_validation_receipt_v2",
        "superseding_canonical_validation_receipt_schema":
            "hf_superseding_canonical_raw_validation_receipt_v3",
        "canonical_seal_schema": "hf_canonical_freeze_seal_v2",
        "superseding_canonical_seal_schema":
            "hf_superseding_canonical_freeze_seal_v3",
        "analysis_schema": "paul_pair_objects_primary_ground_v2",
        "analysis_implementation": "one_pass_primary_ground_pair_analysis_v2",
        "analysis_version": "status_analysis_THnSparse_qq_v2",
        "analysis_profile": "central_primary_ground_v1",
        "raw_schema": "hf_primary_ground_raw_v7",
        "selector": "hard_trigger_primary_ground__primary_ground_associate_v1",
        "origin_algorithm":
            "signed_heavy_constituent_complete_mothers_unique_v4",
        "heavy_stability_audit_schema": "heavy_stability_audit_v2",
        "associate_origin_category_schema": "associate_origin_category_v1",
        "associate_origin_category_labels": (
            '{"1":"selected_hard_companion",'
            '"2":"selected_hard_noncompanion","3":"shower",'
            '"4":"mpi","5":"other_resolved",'
            '"6":"unresolved_or_ambiguous"}'
        ),
        "pair_combinatorics_mode": "ordered_conditional_v1",
        "same_sign_pair_factor": 1.0,
        "canonical_files_per_tune_minimum": MINIMUM_SLOTS,
        "canonical_files_per_tune_policy":
            "manifest_derived_equal_N_divisible_by_10",
        "tunes": list(EXPECTED_TUNES),
        "effective_settings_schema": "effective_pythia_settings_exhaustive_v2",
    }
    for key, expected in expected_contracts.items():
        if contracts.get(key) != expected:
            raise ValueError(
                f"specification contract {key}={contracts.get(key)!r}, "
                f"expected {expected!r}"
            )
    for key in (
        "species_registry_sha256",
        "pair_registry_sha256",
        "tune_difference_allowlist_sha256",
    ):
        value = contracts.get(key)
        if not isinstance(value, str) or not HEX64.fullmatch(value):
            raise ValueError(f"invalid specification {key}")
    if (
        contracts.get("pair_registry_schema")
        != "heavy_flavour_pair_registry_v1"
        or contracts.get("tune_difference_allowlist_schema")
        != "pythia_tune_difference_allowlist_v2"
    ):
        raise ValueError("registry schemas differ from the v1 contract")

    expected_method = {
        "central_estimator":
            "full_union_of_manifest_derived_equal_N_canonical_files_per_tune",
        "block_standard_error":
            "sqrt(sum((x_k-mean(x))^2)/(K*(K-1)))",
        "os_ss_rule":
            "form_OS_per_trigger_minus_SS_per_trigger_inside_every_resample",
        "ratio_rule":
            "form_baryon_balancing_yield_over_reference_meson_balancing_yield_inside_every_resample",
        "root_sumw2_role":
            "retained_for_input_validation_only_not_used_as_block_covariance",
        "zero_trigger_denominator": "technical_failure",
        "zero_reference_meson_yield_denominator": "technical_failure",
        "nonfinite_value": "technical_failure",
        "negative_os_minus_ss_yield": "retain_and_report",
        "unresolved_associate_sensitivity":
            "repeat_every_observable_and_resample_excluding_origin_category_6",
        "multiplicity_boundary_source":
            "checksum_bound_full_paper_plot_boundary_receipt",
        "boundary_stability":
            "leave_one_primary_block_out_recompute_each_frozen_threshold",
        "decision_policy": "descriptive_only_no_pass_threshold",
    }
    for key, expected in expected_method.items():
        if method.get(key) != expected:
            raise ValueError(f"unsupported statistical method field {key}")
    primary = method.get("primary_partition")
    if (
        not isinstance(primary, dict)
        or primary.get("name") != "canonical_slot_modulo_10"
        or primary.get("blocks") != 10
        or primary.get("files_per_tune_per_block") != "N/10"
    ):
        raise ValueError("primary partition differs from the predeclared partition")
    alternative = method.get("alternative_partition")
    if (
        not isinstance(alternative, dict)
        or alternative.get("name")
        != "largest_equal_exposure_modulo_partition_not_exceeding_20"
        or alternative.get("block_count_rule")
        != "largest_divisor_of_N_in_[11,20],_else_10"
        or alternative.get("files_per_tune_per_block") != "N/K_alt"
    ):
        raise ValueError("alternative partition differs from its dynamic contract")
    jackknife = method.get("file_jackknife")
    if (
        not isinstance(jackknife, dict)
        or jackknife.get("name") != "delete_one_canonical_file"
        or jackknife.get("replicates") != "N"
        or jackknife.get("standard_error")
        != "sqrt((N-1)/N*sum((theta_i-mean(theta))^2))"
    ):
        raise ValueError("delete-one jackknife contract differs")

    expected_integration = {
        "input_role": "already_selected_one_pass_pair_objects",
        "downstream_kinematic_recuts": "none",
        "axis_range_applied": "multiplicity_only",
        "trigger_pt_selection":
            "validate_input_metadata_exclusive_gt_1_GeV",
        "associate_pt_selection":
            "validate_input_metadata_exclusive_gt_0p15_GeV",
        "eta_selection": "validate_input_metadata_abs_eta_le_4",
        "upper_pt_cut": "none",
        "sparse_underflow_overflow_policy": "technical_failure",
        "associate_origin_sensitivity_axis":
            "hCorrelationsByOrigin_axis_7_keep_categories_1_through_5",
    }
    if not isinstance(integration, dict) or integration != expected_integration:
        raise ValueError(
            "integration contract must consume the already-selected pair "
            "objects without downstream kinematic recuts"
        )

    selections = spec.get("multiplicity_selections")
    if not isinstance(selections, list) or not selections:
        raise ValueError("no multiplicity selections were predeclared")
    selection_names: set[str] = set()
    for selection in selections:
        if not isinstance(selection, dict):
            raise ValueError("multiplicity selection is not an object")
        name = selection.get("name")
        low = require_finite(selection.get("low_percentile"), f"{name} low")
        high = require_finite(selection.get("high_percentile"), f"{name} high")
        if (
            not isinstance(name, str)
            or not name
            or name in selection_names
            or low < 0.0
            or high > 100.0
            or low >= high
        ):
            raise ValueError(f"invalid multiplicity selection {selection!r}")
        selection_names.add(name)
    fixed_selections = spec.get("fixed_nch_selections")
    if not isinstance(fixed_selections, list) or not fixed_selections:
        raise ValueError("no fixed-Nch comparison selections were predeclared")
    for selection in fixed_selections:
        if not isinstance(selection, dict):
            raise ValueError("fixed-Nch selection is not an object")
        name = selection.get("name")
        minimum = require_int(selection.get("nch_min_inclusive"), f"{name} min")
        maximum = require_int(selection.get("nch_max_inclusive"), f"{name} max")
        if (
            not isinstance(name, str)
            or not name
            or name in selection_names
            or minimum > maximum
            or maximum > 4095
        ):
            raise ValueError(f"invalid fixed-Nch selection {selection!r}")
        selection_names.add(name)

    boundary_configuration = contracts.get("boundary_configuration_path")
    if (
        not isinstance(boundary_configuration, str)
        or not boundary_configuration
        or Path(boundary_configuration).is_absolute()
        or ".." in Path(boundary_configuration).parts
    ):
        raise ValueError("boundary configuration path is not checkout-relative")
    boundary_configuration_path = checkout / boundary_configuration
    if sha256(boundary_configuration_path) != contracts.get(
        "boundary_configuration_sha256"
    ):
        raise ValueError(
            "checked-out full-paper plotting configuration differs from spec"
        )

    registry_relative = Path(str(contracts.get("pair_registry_path", "")))
    if (
        not registry_relative.parts
        or registry_relative.is_absolute()
        or ".." in registry_relative.parts
    ):
        raise ValueError("pair registry path is not checkout-relative")
    registry_path = checkout / registry_relative
    if sha256(registry_path) != contracts["pair_registry_sha256"]:
        raise ValueError("checked-out pair registry checksum differs from spec")
    species_path = checkout / "config/heavy_flavour_species_v1.json"
    tune_allowlist_path = checkout / "config/tune_difference_allowlist_v1.json"
    if sha256(species_path) != contracts["species_registry_sha256"]:
        raise ValueError("checked-out species registry checksum differs from spec")
    if (
        sha256(tune_allowlist_path)
        != contracts["tune_difference_allowlist_sha256"]
    ):
        raise ValueError("checked-out tune allowlist checksum differs from spec")
    registry = load_json(registry_path)
    if (
        registry.get("schema") != contracts["pair_registry_schema"]
        or registry.get("pair_count") != 300
        or not isinstance(registry.get("pairs"), list)
        or len(registry["pairs"]) != 300
    ):
        raise ValueError("pair registry content/schema differs")
    pair_lookup: dict[tuple[int, int], dict] = {}
    filename_lookup: dict[str, dict] = {}
    for pair in registry["pairs"]:
        key = (int(pair["trigger_pdg"]), int(pair["associate_pdg"]))
        filename = pair.get("filename")
        if key in pair_lookup or filename in filename_lookup:
            raise ValueError("pair registry contains duplicate identities")
        pair_lookup[key] = pair
        filename_lookup[str(filename)] = pair

    observables = spec.get("observables")
    if not isinstance(observables, list) or not observables:
        raise ValueError("no representative observables were predeclared")
    sectors: set[str] = set()
    names: set[str] = set()
    for observable in observables:
        if not isinstance(observable, dict):
            raise ValueError("observable is not an object")
        name = observable.get("name")
        sector = observable.get("sector")
        trigger = require_int(observable.get("trigger_pdg"), f"{name} trigger")
        if (
            not isinstance(name, str)
            or not name
            or name in names
            or sector not in {"charm", "beauty"}
        ):
            raise ValueError(f"invalid representative observable {name!r}")
        names.add(name)
        sectors.add(str(sector))
        reference_pdg: int | None = None
        for family, kind in (("reference_meson", "meson"), ("baryon", "baryon")):
            definition = observable.get(family)
            if not isinstance(definition, dict):
                raise ValueError(f"{name} {family} definition is absent")
            for sign in ("os", "ss"):
                component = definition.get(sign)
                if not isinstance(component, dict):
                    raise ValueError(f"{name} {family}/{sign} is absent")
                associate = require_signed_int(
                    component.get("associate_pdg"),
                    f"{name} {family}/{sign} associate",
                )
                pair = pair_lookup.get((trigger, associate))
                if (
                    pair is None
                    or pair.get("filename") != component.get("filename")
                    or pair.get("sector") != sector
                    or pair.get("associate_kind") != kind
                    or pair.get("heavy_sign") != sign.upper()
                ):
                    raise ValueError(
                        f"{name} {family}/{sign} disagrees with pair registry"
                    )
                pair_reference = int(pair["reference_meson_pdg"])
                if reference_pdg is None:
                    reference_pdg = pair_reference
                elif reference_pdg != pair_reference:
                    raise ValueError(f"{name} has inconsistent reference mesons")
    if sectors != {"charm", "beauty"}:
        raise ValueError("representative set must cover charm and beauty")
    return pair_lookup


def validate_canonical_freeze(
    directory: Path, spec: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    contracts = spec["contracts"]
    manifest_path = directory / "canonical_manifest.jsonl"
    summary_path = directory / "freeze_summary.json"
    receipt_path = directory / "canonical_raw_validation_receipt.json"
    seal_path = directory / "freeze_seal.json"
    validation_log_path = directory / "canonical_raw_validation.log"
    for path in (
        manifest_path,
        summary_path,
        receipt_path,
        seal_path,
        validation_log_path,
    ):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"sealed canonical-freeze artifact is absent: {path}")

    rows = load_jsonl(manifest_path)
    summary = load_json(summary_path)
    receipt = load_json(receipt_path)
    seal = load_json(seal_path)
    manifest_sha = sha256(manifest_path)
    jobs_per_tune = require_int(
        summary.get("jobs_per_tune"), "canonical jobs per tune", MINIMUM_SLOTS
    )
    if jobs_per_tune % 10:
        raise ValueError("canonical jobs per tune is not divisible by ten")
    superseding = (
        summary.get("schema")
        == contracts["superseding_canonical_summary_schema"]
    )
    expected_summary_schema = (
        contracts["superseding_canonical_summary_schema"]
        if superseding
        else contracts["canonical_summary_schema"]
    )
    expected_row_schema = (
        contracts["superseding_canonical_manifest_schema"]
        if superseding
        else contracts["canonical_manifest_schema"]
    )
    expected_receipt_schema = (
        contracts["superseding_canonical_validation_receipt_schema"]
        if superseding
        else contracts["canonical_validation_receipt_schema"]
    )
    expected_seal_schema = (
        contracts["superseding_canonical_seal_schema"]
        if superseding
        else contracts["canonical_seal_schema"]
    )
    if (
        summary.get("schema") != expected_summary_schema
        or summary.get("canonical_manifest_sha256") != manifest_sha
        or (not superseding and jobs_per_tune != MINIMUM_SLOTS)
        or summary.get("block_count") != 10
        or summary.get("jobs_per_tune_per_block") != jobs_per_tune // 10
        or summary.get("raw_schema") != contracts["raw_schema"]
        or summary.get("origin_algorithm") != contracts["origin_algorithm"]
        or summary.get("selector") != contracts["selector"]
        or summary.get("species_registry_sha256")
        != contracts["species_registry_sha256"]
        or summary.get("pair_registry_sha256")
        != contracts["pair_registry_sha256"]
        or summary.get("tune_difference_allowlist_schema")
        != contracts["tune_difference_allowlist_schema"]
        or summary.get("tune_difference_allowlist_sha256")
        != contracts["tune_difference_allowlist_sha256"]
    ):
        raise ValueError("canonical freeze summary differs from robustness spec")
    if (
        receipt.get("schema")
        != expected_receipt_schema
        or receipt.get("state") != "PASS"
        or receipt.get("canonical_manifest_sha256") != manifest_sha
        or receipt.get("canonical_manifest_rows")
        != len(EXPECTED_TUNES) * jobs_per_tune
        or receipt.get("validation_log_sha256") != sha256(validation_log_path)
    ):
        raise ValueError("canonical validation receipt is not an exact PASS")
    if (
        seal.get("schema") != expected_seal_schema
        or seal.get("state") != "SEALED"
        or seal.get("canonical_manifest_sha256") != manifest_sha
        or seal.get("validation_receipt_path")
        != "canonical_raw_validation_receipt.json"
        or seal.get("validation_receipt_sha256") != sha256(receipt_path)
        or seal.get("validation_log_path") != "canonical_raw_validation.log"
        or seal.get("validation_log_sha256") != sha256(validation_log_path)
    ):
        raise ValueError("canonical freeze seal is invalid")

    if len(rows) != len(EXPECTED_TUNES) * jobs_per_tune:
        raise ValueError("canonical manifest row count differs from equal-tune N")
    expected_identities = [
        (tune, slot)
        for tune in EXPECTED_TUNES
        for slot in range(jobs_per_tune)
    ]
    identities: list[tuple[str, int]] = []
    seeds: set[int] = set()
    raw_paths: set[str] = set()
    requested_successes: set[int] = set()
    repository_commits: set[str] = set()
    for index, row in enumerate(rows):
        tune = row.get("tune")
        slot = require_int(row.get("canonical_slot"), f"row {index} slot")
        identities.append((str(tune), slot))
        if (
            row.get("schema") != expected_row_schema
            or tune not in EXPECTED_TUNES
            or row.get("tune_ordinal") != EXPECTED_TUNES.index(str(tune))
            or slot >= jobs_per_tune
            or row.get("block") != slot % 10
            or row.get("block_position") != slot // 10
            or row.get("raw_schema") != contracts["raw_schema"]
            or row.get("selector") != contracts["selector"]
            or row.get("origin_algorithm") != contracts["origin_algorithm"]
            or row.get("species_registry_sha256")
            != contracts["species_registry_sha256"]
            or row.get("pair_registry_sha256")
            != contracts["pair_registry_sha256"]
            or row.get("tune_difference_allowlist_schema")
            != contracts["tune_difference_allowlist_schema"]
            or row.get("tune_difference_allowlist_sha256")
            != contracts["tune_difference_allowlist_sha256"]
        ):
            raise ValueError(f"canonical manifest contract mismatch at row {index}")
        for key, pattern in (
            ("repository_commit", HEX40),
            ("raw_sha256", HEX64),
            ("producer_executable_sha256", HEX64),
            ("effective_card_sha256", HEX64),
        ):
            value = row.get(key)
            if not isinstance(value, str) or not pattern.fullmatch(value):
                raise ValueError(f"invalid canonical row {index} {key}")
        repository_commits.add(str(row["repository_commit"]))
        seed = require_int(row.get("seed"), f"row {index} seed", 1)
        raw_path = row.get("raw_path")
        requested = require_int(
            row.get("requested_successes"),
            f"row {index} requested_successes",
            1,
        )
        if (
            not isinstance(raw_path, str)
            or not raw_path
            or Path(raw_path).is_absolute()
            or ".." in Path(raw_path).parts
        ):
            raise ValueError(f"invalid canonical raw path at row {index}")
        if seed in seeds or raw_path in raw_paths:
            raise ValueError("canonical manifest has duplicate seed/raw path")
        seeds.add(seed)
        raw_paths.add(raw_path)
        requested_successes.add(requested)
    if identities != expected_identities:
        raise ValueError("canonical rows are not exact ordered tune/slot coverage")
    if len(requested_successes) != 1:
        raise ValueError("canonical files do not share one successful-event target")
    if len(repository_commits) != 1:
        raise ValueError("canonical freeze mixes repository commits")

    block_hashes = summary.get("block_manifest_sha256")
    if not isinstance(block_hashes, dict):
        raise ValueError("canonical block checksum map is absent")
    for block in range(10):
        name = f"block_{block + 1:02d}.jsonl"
        path = directory / name
        if (
            path.is_symlink()
            or not path.is_file()
            or block_hashes.get(name) != sha256(path)
            or load_jsonl(path)
            != [row for row in rows if row["canonical_slot"] % 10 == block]
        ):
            raise ValueError(f"canonical primary block differs: {name}")
    return rows, {
        "canonical_manifest_sha256": manifest_sha,
        "freeze_summary_sha256": sha256(summary_path),
        "validation_receipt_sha256": sha256(receipt_path),
        "validation_log_sha256": sha256(validation_log_path),
        "freeze_seal_sha256": sha256(seal_path),
        "campaign": summary.get("campaign"),
        "campaign_ordinal": summary.get("campaign_ordinal"),
        "repository_commit": next(iter(repository_commits)),
        "successful_events_per_job": next(iter(requested_successes)),
        "successful_events_per_tune":
            jobs_per_tune * next(iter(requested_successes)),
        "jobs_per_tune": jobs_per_tune,
    }


def validate_boundary_receipt(
    path: Path,
    spec: dict[str, Any],
    checkout: Path,
) -> tuple[
    dict[str, Any],
    dict[str, dict[str, tuple[float, float]]],
    dict[str, dict[float, int]],
    dict[str, Any],
]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"multiplicity-boundary receipt is absent: {path}")
    receipt = load_json(path)
    payload = dict(receipt)
    claimed_payload_sha = payload.pop("payload_sha256", None)
    expected_configuration = (
        checkout / str(spec["contracts"]["boundary_configuration_path"])
    )
    if (
        receipt.get("schema") != BOUNDARY_RECEIPT_SCHEMA
        or receipt.get("schema_version") != 1
        or receipt.get("algorithm")
        != "ascending_discrete_weighted_quantile_v1"
        or receipt.get("completion_status") != "PASS"
        or claimed_payload_sha != json_sha256(payload)
        or receipt.get("configuration_path")
        != spec["contracts"]["boundary_configuration_path"]
        or receipt.get("configuration_sha256")
        != sha256(expected_configuration)
        or receipt.get("plotter_source_sha256")
        != sha256(checkout / "PlottingScripts/improvedPlotting_THnSparse.C")
        or receipt.get("boundary_utility_sha256")
        != sha256(checkout / "PlottingScripts/MultiplicityBoundaryUtils.h")
        or not isinstance(receipt.get("tunes"), dict)
        or set(receipt["tunes"]) != set(EXPECTED_TUNES)
    ):
        raise ValueError(
            "multiplicity-boundary receipt is incomplete, stale, or not "
            "bound to the frozen full-paper configuration"
        )
    policy = receipt.get("policy")
    if (
        not isinstance(policy, dict)
        or policy.get("normalization") != "sum_of_regular_bins"
        or policy.get("underflow")
        != "must_be_exactly_zero_and_is_excluded"
        or policy.get("overflow")
        != "must_be_exactly_zero_and_is_excluded"
        or policy.get("class_bounds") != "inclusive_integer_nch"
    ):
        raise ValueError("multiplicity-boundary receipt policy differs")

    ranges_by_tune: dict[str, dict[str, tuple[float, float]]] = {}
    thresholds_by_tune: dict[str, dict[float, int]] = {}
    for tune in EXPECTED_TUNES:
        tune_receipt = receipt["tunes"][tune]
        if not isinstance(tune_receipt, dict):
            raise ValueError(f"invalid boundary receipt for tune {tune}")
        source = Path(str(tune_receipt.get("central_reference_path", "")))
        if (
            not source.is_absolute()
            or source.is_symlink()
            or not source.is_file()
            or sha256(source)
            != tune_receipt.get("central_source_file_sha256")
            or tune_receipt.get("histogram_name") != "summed MULTIPLICITY"
            or require_finite(
                tune_receipt.get("underflow"), f"{tune} boundary underflow"
            )
            != 0.0
            or require_finite(
                tune_receipt.get("overflow"), f"{tune} boundary overflow"
            )
            != 0.0
            or require_finite(
                tune_receipt.get("regular_bin_integral"),
                f"{tune} boundary integral",
            )
            <= 0.0
        ):
            raise ValueError(
                f"multiplicity-boundary central source is absent or changed: "
                f"{tune}"
            )
        threshold_rows = tune_receipt.get("thresholds")
        if not isinstance(threshold_rows, list) or not threshold_rows:
            raise ValueError(f"multiplicity thresholds are absent for {tune}")
        thresholds: dict[float, int] = {}
        for index, row in enumerate(threshold_rows):
            if not isinstance(row, dict):
                raise ValueError(f"invalid threshold row {tune}/{index}")
            percentile = require_finite(
                row.get("percentile"), f"{tune} threshold percentile"
            )
            threshold = require_int(
                row.get("nch_threshold"), f"{tune} Nch threshold"
            )
            if (
                percentile < 0.0
                or percentile > 100.0
                or percentile in thresholds
                or threshold > 4095
            ):
                raise ValueError(f"invalid or duplicate threshold for {tune}")
            for key in (
                "target_low_activity_fraction",
                "achieved_exclusive_fraction_before_threshold",
                "achieved_inclusive_fraction_through_threshold",
            ):
                fraction = require_finite(
                    row.get(key), f"{tune} threshold {percentile} {key}"
                )
                if fraction < 0.0 or fraction > 1.0:
                    raise ValueError(
                        f"invalid threshold fraction for {tune}/{percentile}"
                    )
            thresholds[percentile] = threshold

        # A checksum proves that the referenced ROOT file did not change, but
        # it does not prove that the JSON thresholds and achieved fractions
        # were derived from that histogram.  Recompute the complete discrete
        # quantile contract here so a hand-written receipt cannot authorize a
        # publication run.
        try:
            import ROOT  # type: ignore
        except ImportError as error:
            raise RuntimeError(
                "PyROOT is required to revalidate multiplicity boundaries"
            ) from error
        source_file = ROOT.TFile.Open(str(source), "READ")
        if not source_file or source_file.IsZombie():
            raise ValueError(
                f"cannot open multiplicity-boundary source for {tune}: "
                f"{source}"
            )
        try:
            histogram = source_file.Get("summed MULTIPLICITY")
            if (
                not histogram
                or not histogram.InheritsFrom("TH1")
                or histogram.GetDimension() != 1
                or histogram.GetNbinsX() <= 0
            ):
                raise ValueError(
                    f"{tune} boundary source lacks a one-dimensional "
                    "summed MULTIPLICITY histogram"
                )
            centers = [
                float(histogram.GetBinCenter(index))
                for index in range(1, histogram.GetNbinsX() + 1)
            ]
            contents = [
                float(histogram.GetBinContent(index))
                for index in range(1, histogram.GetNbinsX() + 1)
            ]
            errors = [
                float(histogram.GetBinError(index))
                for index in range(0, histogram.GetNbinsX() + 2)
            ]
            flows = (
                float(histogram.GetBinContent(0)),
                float(histogram.GetBinContent(histogram.GetNbinsX() + 1)),
            )
        finally:
            source_file.Close()
        if (
            any(
                not math.isfinite(value) or value < 0.0
                for value in contents + errors
            )
            or flows != (0.0, 0.0)
            or any(
                not math.isfinite(center)
                or abs(center - round(center)) > 1e-9
                for center in centers
            )
            or centers[0] < 0.0
            or any(
                int(round(second)) != int(round(first)) + 1
                for first, second in zip(centers, centers[1:])
            )
        ):
            raise ValueError(
                f"{tune} multiplicity histogram violates the frozen integer "
                "boundary contract"
            )
        integral = sum(contents)
        if (
            not math.isfinite(integral)
            or integral <= 0.0
            or not nearly_equal(
                integral,
                require_finite(
                    tune_receipt.get("regular_bin_integral"),
                    f"{tune} boundary integral",
                ),
            )
        ):
            raise ValueError(
                f"{tune} multiplicity-boundary integral differs from source"
            )
        by_percentile = {
            require_finite(row.get("percentile"), f"{tune} percentile"): row
            for row in threshold_rows
        }
        for percentile, claimed_threshold in thresholds.items():
            recomputed = strict_stability_threshold(
                centers,
                contents,
                percentile,
                f"{tune}/receipt",
            )
            row = by_percentile[percentile]
            if recomputed != claimed_threshold:
                raise ValueError(
                    f"{tune} multiplicity threshold {percentile:g} was not "
                    "derived from the checksum-bound source"
                )
            threshold_index = centers.index(float(recomputed))
            before = sum(contents[:threshold_index]) / integral
            through = sum(contents[: threshold_index + 1]) / integral
            target = (100.0 - percentile) / 100.0
            for key, expected in (
                ("target_low_activity_fraction", target),
                (
                    "achieved_exclusive_fraction_before_threshold",
                    before,
                ),
                (
                    "achieved_inclusive_fraction_through_threshold",
                    through,
                ),
            ):
                if not nearly_equal(
                    require_finite(row.get(key), f"{tune}/{percentile}/{key}"),
                    expected,
                ):
                    raise ValueError(
                        f"{tune} threshold {percentile:g} {key} was not "
                        "recomputed from the frozen source"
                    )

        class_rows = tune_receipt.get("classes")
        if not isinstance(class_rows, list) or not class_rows:
            raise ValueError(f"multiplicity classes are absent for {tune}")
        classes: dict[tuple[float, float], tuple[float, float]] = {}
        ordered_classes: list[tuple[float, float, int, int]] = []
        for index, row in enumerate(class_rows):
            if not isinstance(row, dict):
                raise ValueError(f"invalid class row {tune}/{index}")
            low = require_finite(
                row.get("percentile_min"), f"{tune} class low"
            )
            high = require_finite(
                row.get("percentile_max"), f"{tune} class high"
            )
            minimum = require_int(
                row.get("nch_min_inclusive"), f"{tune} class Nch min"
            )
            maximum = require_int(
                row.get("nch_max_inclusive"), f"{tune} class Nch max"
            )
            if (
                low < 0.0
                or high > 100.0
                or low >= high
                or minimum > maximum
                or maximum > 4095
                or (low, high) in classes
            ):
                raise ValueError(f"invalid multiplicity class for {tune}")
            classes[(low, high)] = (float(minimum), float(maximum))
            ordered_classes.append((low, high, minimum, maximum))
            expected_minimum = thresholds[high] + (
                1 if high < 100.0 else 0
            )
            expected_maximum = thresholds[low]
            if (minimum, maximum) != (
                expected_minimum,
                expected_maximum,
            ):
                raise ValueError(
                    f"{tune} class {low:g}-{high:g} does not follow the "
                    "frozen discrete-boundary rule"
                )
            first_index = centers.index(float(minimum))
            last_index = centers.index(float(maximum))
            achieved = (
                sum(contents[first_index : last_index + 1]) / integral
            )
            if (
                not nearly_equal(
                    require_finite(
                        row.get("target_fraction"),
                        f"{tune} class target fraction",
                    ),
                    (high - low) / 100.0,
                )
                or not nearly_equal(
                    require_finite(
                        row.get("achieved_weighted_fraction"),
                        f"{tune} class achieved fraction",
                    ),
                    achieved,
                )
            ):
                raise ValueError(
                    f"{tune} class {low:g}-{high:g} fractions were not "
                    "recomputed from the frozen source"
                )
        ordered_classes.sort()
        if (
            ordered_classes[0][0] != 0.0
            or ordered_classes[-1][1] != 100.0
        ):
            raise ValueError(f"multiplicity classes do not cover 0-100: {tune}")
        for first, second in zip(ordered_classes, ordered_classes[1:]):
            if first[1] != second[0] or first[2] != second[3] + 1:
                raise ValueError(
                    f"multiplicity classes are not contiguous/disjoint: {tune}"
                )
        partition = tune_receipt.get("partition")
        if (
            not isinstance(partition, dict)
            or partition.get("coverage") != "PASS"
            or partition.get("disjointness") != "PASS"
            or require_int(
                partition.get("nch_min_inclusive"), f"{tune} partition min"
            )
            != ordered_classes[-1][2]
            or require_int(
                partition.get("nch_max_inclusive"), f"{tune} partition max"
            )
            != ordered_classes[0][3]
        ):
            raise ValueError(f"multiplicity partition is invalid for {tune}")

        tune_ranges: dict[str, tuple[float, float]] = {}
        for selection in spec["multiplicity_selections"]:
            name = str(selection["name"])
            key = (
                float(selection["low_percentile"]),
                float(selection["high_percentile"]),
            )
            if key == (0.0, 100.0):
                tune_ranges[name] = (
                    float(partition["nch_min_inclusive"]),
                    float(partition["nch_max_inclusive"]),
                )
            elif key in classes:
                tune_ranges[name] = classes[key]
            else:
                # A predeclared selection may be the exact union of adjacent
                # frozen classes (notably 0--10% = 0--1% U 1--10%).  Accept
                # only a gap-free percentile and integer-Nch union; never
                # interpolate or recompute a new percentile boundary here.
                members = sorted(
                    (
                        low,
                        high,
                        int(bounds[0]),
                        int(bounds[1]),
                    )
                    for (low, high), bounds in classes.items()
                    if low >= key[0] and high <= key[1]
                )
                if (
                    not members
                    or members[0][0] != key[0]
                    or members[-1][1] != key[1]
                    or any(
                        first[1] != second[0]
                        for first, second in zip(members, members[1:])
                    )
                ):
                    raise ValueError(
                        f"{name} is not an exact contiguous union of frozen "
                        f"classes in the boundary receipt for {tune}"
                    )
                by_nch = sorted(members, key=lambda member: member[2])
                if any(
                    first[3] + 1 != second[2]
                    for first, second in zip(
                        by_nch, by_nch[1:]
                    )
                ):
                    raise ValueError(
                        f"{name} frozen classes are not an exact disjoint "
                        f"integer-Nch union for {tune}"
                    )
                tune_ranges[name] = (
                    float(by_nch[0][2]),
                    float(by_nch[-1][3]),
                )
        for selection in spec["fixed_nch_selections"]:
            tune_ranges[str(selection["name"])] = (
                float(selection["nch_min_inclusive"]),
                float(selection["nch_max_inclusive"]),
            )
        ranges_by_tune[tune] = tune_ranges
        thresholds_by_tune[tune] = thresholds

    return receipt, ranges_by_tune, thresholds_by_tune, {
        "path": path.resolve().as_posix(),
        "sha256": sha256(path),
        "payload_sha256": claimed_payload_sha,
        "configuration_path":
            spec["contracts"]["boundary_configuration_path"],
        "configuration_sha256": receipt["configuration_sha256"],
    }


def validate_final_origin_closure_report(
    path: Path,
    freeze_provenance: dict[str, Any],
    checkout: Path,
    spec: dict[str, Any],
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"final origin-closure report is absent: {path}")
    report = load_json(path)
    audit_macro = checkout / "Validation/AuditOriginResolution.C"
    if audit_macro.is_symlink() or not audit_macro.is_file():
        raise ValueError("final origin-audit implementation is absent")
    checkout_commit = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    contracts = spec["contracts"]
    if (
        report.get("schema") != ORIGIN_CLOSURE_REPORT_SCHEMA
        or report.get("completion_state") != "PASS"
        or report.get("publication_readiness") != "READY"
        or report.get("canonical_manifest_sha256")
        != freeze_provenance["canonical_manifest_sha256"]
        or report.get("freeze_seal_sha256")
        != freeze_provenance["freeze_seal_sha256"]
        or report.get("jobs_per_tune")
        != freeze_provenance["jobs_per_tune"]
        or report.get("audited_job_count")
        != len(EXPECTED_TUNES) * freeze_provenance["jobs_per_tune"]
        or report.get("unresolved_trigger_candidate_count") != 0
        or report.get("audit_macro_sha256") != sha256(audit_macro)
        or report.get("audit_checkout_commit") != checkout_commit
        or checkout_commit != freeze_provenance["repository_commit"]
    ):
        raise ValueError(
            "final origin-closure report is not a PASS for this exact sealed "
            "canonical manifest"
        )
    payload = dict(report)
    claimed_payload_sha = payload.pop("payload_sha256", None)
    if claimed_payload_sha != json_sha256(payload):
        raise ValueError("final origin-closure report payload checksum differs")

    audit_contract = report.get("audit_contract")
    expected_contract = {
        "audit_schema": "origin_resolution_audit_v3",
        "raw_schema": contracts["raw_schema"],
        "selector": contracts["selector"],
        "origin_algorithm": contracts["origin_algorithm"],
        "species_registry_sha256": contracts["species_registry_sha256"],
        "primary_all_heavy_closure_schema":
            "primary_all_heavy_closure_v1",
    }
    if (
        not isinstance(audit_contract, dict)
        or any(
            audit_contract.get(key) != value
            for key, value in expected_contract.items()
        )
    ):
        raise ValueError(
            "final origin-closure audit contract differs from the frozen "
            "analysis definition"
        )

    input_audits = report.get("input_audits")
    expected_identities = [
        (tune, slot)
        for tune in EXPECTED_TUNES
        for slot in range(int(freeze_provenance["jobs_per_tune"]))
    ]
    observed_identities: list[tuple[str, int]] = []
    if (
        not isinstance(input_audits, list)
        or len(input_audits) != len(expected_identities)
        or report.get("input_audit_inventory_sha256")
        != json_sha256(input_audits)
    ):
        raise ValueError("final origin input-audit inventory is incomplete")
    for index, record in enumerate(input_audits):
        if not isinstance(record, dict):
            raise ValueError(f"final origin input-audit row {index} is invalid")
        tune = record.get("tune")
        slot = require_int(
            record.get("canonical_slot"),
            f"final origin input-audit row {index} slot",
        )
        observed_identities.append((str(tune), slot))
        for path_key, hash_key in (
            ("raw_path", "raw_sha256"),
            (
                "raw_validation_receipt_path",
                "raw_validation_receipt_sha256",
            ),
            ("audit_path", "audit_sha256"),
            ("audit_log_path", "audit_log_sha256"),
        ):
            artifact = Path(str(record.get(path_key, "")))
            if (
                not artifact.is_absolute()
                or artifact.is_symlink()
                or not artifact.is_file()
                or not HEX64.fullmatch(str(record.get(hash_key, "")))
                or sha256(artifact) != record[hash_key]
            ):
                raise ValueError(
                    f"final origin input-audit artifact changed: "
                    f"{tune}/slot_{slot:03d}/{path_key}"
                )
    if observed_identities != expected_identities:
        raise ValueError(
            "final origin input audits do not have exact ordered tune/slot "
            "coverage"
        )

    origin_rows = report.get("origin_summary")
    closure_rows = report.get("primary_all_heavy_closure")
    if (
        not isinstance(origin_rows, list)
        or not origin_rows
        or not isinstance(closure_rows, list)
        or not closure_rows
        or require_int(
            report.get("closure_base_count"),
            "final origin closure-base count",
            1,
        )
        <= 0
    ):
        raise ValueError("final origin closure has vacuous/empty coverage")
    trigger_candidates = 0
    unresolved_triggers = 0
    for index, row in enumerate(origin_rows):
        if not isinstance(row, dict):
            raise ValueError(f"final origin summary row {index} is invalid")
        candidates = require_int(
            row.get("candidates"),
            f"final origin summary row {index} candidates",
        )
        if row.get("role") == 1:
            trigger_candidates += candidates
            if row.get("origin") == 0:
                unresolved_triggers += candidates
    if (
        trigger_candidates <= 0
        or unresolved_triggers
        != report["unresolved_trigger_candidate_count"]
    ):
        raise ValueError(
            "final origin trigger coverage/counts are empty or inconsistent"
        )
    for index, row in enumerate(closure_rows):
        if not isinstance(row, dict):
            raise ValueError(f"final closure row {index} is invalid")
        denominator = require_int(
            row.get("denominator_count"),
            f"final closure row {index} denominator",
            1,
        )
        count = require_int(
            row.get("count"), f"final closure row {index} count"
        )
        if count > denominator:
            raise ValueError(
                f"final closure row {index} exceeds its denominator"
            )
    return {
        "path": path.resolve().as_posix(),
        "sha256": sha256(path),
        "payload_sha256": claimed_payload_sha,
        "canonical_manifest_sha256":
            report["canonical_manifest_sha256"],
        "freeze_seal_sha256": report["freeze_seal_sha256"],
        "audit_macro_sha256": report["audit_macro_sha256"],
        "audit_checkout_commit": report["audit_checkout_commit"],
        "input_audit_inventory_sha256":
            report["input_audit_inventory_sha256"],
        "audited_job_count": report["audited_job_count"],
        "unresolved_trigger_candidate_count":
            report["unresolved_trigger_candidate_count"],
    }


@dataclass(frozen=True)
class PairTerms:
    os_pairs: float
    os_triggers: float
    ss_pairs: float
    ss_triggers: float

    def add(self, other: "PairTerms") -> "PairTerms":
        return PairTerms(
            self.os_pairs + other.os_pairs,
            self.os_triggers + other.os_triggers,
            self.ss_pairs + other.ss_pairs,
            self.ss_triggers + other.ss_triggers,
        )


@dataclass(frozen=True)
class ObservableTerms:
    meson: PairTerms
    baryon: PairTerms

    def add(self, other: "ObservableTerms") -> "ObservableTerms":
        return ObservableTerms(
            self.meson.add(other.meson),
            self.baryon.add(other.baryon),
        )


ZERO_PAIR_TERMS = PairTerms(0.0, 0.0, 0.0, 0.0)
ZERO_OBSERVABLE_TERMS = ObservableTerms(ZERO_PAIR_TERMS, ZERO_PAIR_TERMS)


def balancing_yield(terms: PairTerms, context: str) -> float:
    values = (
        terms.os_pairs,
        terms.os_triggers,
        terms.ss_pairs,
        terms.ss_triggers,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"{context}: non-finite OS/SS component")
    if terms.os_triggers == 0.0 or terms.ss_triggers == 0.0:
        raise ValueError(f"{context}: exact-zero trigger denominator")
    if not nearly_equal(terms.os_triggers, terms.ss_triggers):
        raise ValueError(
            f"{context}: OS/SS trigger denominators differ "
            f"({terms.os_triggers:.17g}, {terms.ss_triggers:.17g})"
        )
    result = (
        terms.os_pairs / terms.os_triggers
        - terms.ss_pairs / terms.ss_triggers
    )
    if not math.isfinite(result):
        raise ValueError(f"{context}: non-finite balancing yield")
    return result


def evaluate_terms(terms: ObservableTerms, context: str) -> dict[str, float]:
    meson = balancing_yield(terms.meson, f"{context}/reference_meson")
    baryon = balancing_yield(terms.baryon, f"{context}/baryon")
    trigger_values = (
        terms.meson.os_triggers,
        terms.meson.ss_triggers,
        terms.baryon.os_triggers,
        terms.baryon.ss_triggers,
    )
    if not all(
        nearly_equal(trigger_values[0], value) for value in trigger_values[1:]
    ):
        raise ValueError(f"{context}: shared trigger denominators differ")
    if meson == 0.0:
        raise ValueError(
            f"{context}: exact-zero reference-meson balancing-yield denominator"
        )
    ratio = baryon / meson
    if not math.isfinite(ratio):
        raise ValueError(f"{context}: non-finite baryon/reference-meson ratio")
    return {
        "reference_meson_balancing_yield": meson,
        "baryon_balancing_yield": baryon,
        "baryon_over_reference_meson_ratio": ratio,
        "trigger_denominator": trigger_values[0],
        "reference_meson_ratio_denominator": meson,
    }


def sum_terms(records: Sequence[ObservableTerms], slots: Iterable[int]) -> ObservableTerms:
    total = ZERO_OBSERVABLE_TERMS
    count = 0
    for slot in slots:
        total = total.add(records[slot])
        count += 1
    if count == 0:
        raise ValueError("cannot evaluate an empty resample")
    return total


def block_sem(values: Sequence[float]) -> dict[str, Any]:
    if len(values) < 2 or not all(math.isfinite(value) for value in values):
        raise ValueError("block estimates are incomplete or non-finite")
    mean = statistics.fmean(values)
    sem = math.sqrt(
        sum((value - mean) ** 2 for value in values)
        / (len(values) * (len(values) - 1))
    )
    sample_sd = statistics.stdev(values)
    if not math.isfinite(sem) or sem < 0.0:
        raise ValueError("block SEM is invalid")
    return {
        "replicates": len(values),
        "estimates_in_block_index_order": list(values),
        "mean": mean,
        "sample_standard_deviation": sample_sd,
        "standard_error": sem,
        "minimum": min(values),
        "maximum": max(values),
        "negative_replicates": sum(value < 0.0 for value in values),
        "zero_replicates": sum(value == 0.0 for value in values),
    }


def jackknife_standard_error(values: Sequence[float]) -> dict[str, Any]:
    if len(values) < 2 or not all(math.isfinite(value) for value in values):
        raise ValueError("jackknife estimates are incomplete or non-finite")
    mean = statistics.fmean(values)
    standard_error = math.sqrt(
        (len(values) - 1)
        / len(values)
        * sum((value - mean) ** 2 for value in values)
    )
    if not math.isfinite(standard_error) or standard_error < 0.0:
        raise ValueError("jackknife standard error is invalid")
    return {
        "replicates": len(values),
        "estimates_in_omitted_slot_order": list(values),
        "mean": mean,
        "standard_error": standard_error,
        "minimum": min(values),
        "maximum": max(values),
        "negative_replicates": sum(value < 0.0 for value in values),
        "zero_replicates": sum(value == 0.0 for value in values),
    }


def compute_robustness(
    records: Sequence[ObservableTerms], context: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    slots = len(records)
    if slots < MINIMUM_SLOTS or slots % 10:
        raise ValueError(
            f"{context}: expected N>=100 canonical records with N%10=0"
        )
    alternative_blocks = next(
        (
            blocks
            for blocks in range(min(20, slots), 10, -1)
            if slots % blocks == 0
        ),
        10,
    )
    central = evaluate_terms(
        sum_terms(records, range(slots)), f"{context}/central"
    )
    primary = [
        evaluate_terms(
            sum_terms(
                records,
                (slot for slot in range(slots) if slot % 10 == block),
            ),
            f"{context}/mod10_block_{block}",
        )
        for block in range(10)
    ]
    alternative = [
        evaluate_terms(
            sum_terms(
                records,
                (
                    slot
                    for slot in range(slots)
                    if slot % alternative_blocks == block
                ),
            ),
            f"{context}/alternative_modulo_{alternative_blocks}_block_{block}",
        )
        for block in range(alternative_blocks)
    ]
    jackknife = [
        evaluate_terms(
            sum_terms(
                records,
                (candidate for candidate in range(slots)
                 if candidate != omitted),
            ),
            f"{context}/delete_slot_{omitted:03d}",
        )
        for omitted in range(slots)
    ]
    quantities = (
        "reference_meson_balancing_yield",
        "baryon_balancing_yield",
        "baryon_over_reference_meson_ratio",
    )
    results: list[dict[str, Any]] = []
    for quantity in quantities:
        primary_summary = block_sem([row[quantity] for row in primary])
        alternative_summary = block_sem([row[quantity] for row in alternative])
        jackknife_summary = jackknife_standard_error(
            [row[quantity] for row in jackknife]
        )
        results.append(
            {
                "schema": RESULT_SCHEMA,
                "quantity": quantity,
                "central_full_union": central[quantity],
                "primary_10_block": primary_summary,
                "alternative_partition": alternative_summary,
                "alternative_partition_block_count": alternative_blocks,
                "delete_one_file_jackknife": jackknife_summary,
                "standard_error_ratios_for_description_only": {
                    "alternative_over_primary_10":
                        alternative_summary["standard_error"]
                        / primary_summary["standard_error"]
                        if primary_summary["standard_error"] != 0.0
                        else None,
                    "jackknife_over_primary_10":
                        jackknife_summary["standard_error"]
                        / primary_summary["standard_error"]
                        if primary_summary["standard_error"] != 0.0
                        else None,
                },
                "zero_standard_error_flags": {
                    "primary_10_block":
                        primary_summary["standard_error"] == 0.0,
                    "alternative_partition":
                        alternative_summary["standard_error"] == 0.0,
                    "delete_one_file_jackknife":
                        jackknife_summary["standard_error"] == 0.0,
                },
            }
        )
    all_replicates = [central, *primary, *alternative, *jackknife]
    denominator_diagnostics = {
        "minimum_absolute_trigger_denominator":
            min(abs(row["trigger_denominator"]) for row in all_replicates),
        "minimum_absolute_reference_meson_ratio_denominator":
            min(
                abs(row["reference_meson_ratio_denominator"])
                for row in all_replicates
            ),
        "central_trigger_denominator": central["trigger_denominator"],
        "central_reference_meson_ratio_denominator":
            central["reference_meson_ratio_denominator"],
        "negative_reference_meson_yield_replicates":
            sum(
                row["reference_meson_balancing_yield"] < 0.0
                for row in all_replicates
            ),
        "negative_baryon_yield_replicates":
            sum(
                row["baryon_balancing_yield"] < 0.0
                for row in all_replicates
            ),
    }
    return results, denominator_diagnostics


def _root_string(root_file: Any, name: str) -> str:
    value = root_file.Get(name)
    if not value or value.ClassName() != "TObjString":
        raise ValueError(f"missing TObjString {name}")
    return str(value.GetString())


def _root_parameter(root_file: Any, name: str) -> float | int:
    value = root_file.Get(name)
    if not value or not str(value.ClassName()).startswith("TParameter<"):
        raise ValueError(f"missing TParameter {name}")
    result = value.GetVal()
    if isinstance(result, float) and not math.isfinite(result):
        raise ValueError(f"non-finite TParameter {name}")
    return result


def _reset_sparse_axes(histogram: Any) -> None:
    for axis_index in range(histogram.GetNdimensions()):
        histogram.GetAxis(axis_index).SetRange(0, 0)


def _declare_root_helpers(root: Any) -> None:
    global _ROOT_HELPERS_DECLARED
    if _ROOT_HELPERS_DECLARED:
        return
    declaration = r"""
#include <THnSparse.h>
#include <cmath>
#include <vector>
namespace HadronizationStatisticalRobustnessV1 {
int ValidateSparseNoFlow(THnSparse* histogram) {
  if (!histogram) return 1;
  if (!histogram->GetCalculateErrors()) return 2;
  std::vector<Int_t> coordinates(histogram->GetNdimensions());
  for (Long64_t sparseBin = 0; sparseBin < histogram->GetNbins();
       ++sparseBin) {
    const double content =
        histogram->GetBinContent(sparseBin, coordinates.data());
    const double error = histogram->GetBinError(sparseBin);
    if (!std::isfinite(content) || !std::isfinite(error)) return 3;
    for (int axis = 0; axis < histogram->GetNdimensions(); ++axis) {
      if (coordinates[axis] <= 0 ||
          coordinates[axis] > histogram->GetAxis(axis)->GetNbins()) {
        return 4;
      }
    }
  }
  return 0;
}
}  // namespace HadronizationStatisticalRobustnessV1
"""
    if not root.gInterpreter.Declare(declaration):
        raise RuntimeError("cannot declare sparse-overflow validation helper")
    _ROOT_HELPERS_DECLARED = True


def _validate_sparse_no_flow(
    root: Any, histogram: Any, path: Path, object_name: str
) -> None:
    _declare_root_helpers(root)
    status = int(
        root.HadronizationStatisticalRobustnessV1.ValidateSparseNoFlow(
            histogram
        )
    )
    messages = {
        1: "is null",
        2: "lacks Sumw2 storage",
        3: "has a non-finite sparse bin",
        4: "has under/overflow content",
    }
    if status != 0:
        raise ValueError(
            f"{path}: {object_name} {messages.get(status, 'is invalid')}"
        )


def _has_inclusive_upper_edge(axis: Any, endpoint: float) -> bool:
    expected = math.nextafter(endpoint, math.inf)
    endpoint_bin = int(axis.FindFixBin(endpoint))
    return (
        float(axis.GetXmax()) == expected
        and 1 <= endpoint_bin <= int(axis.GetNbins())
    )


def _validate_pair_axis_contract(
    multiplicity: Any,
    trigger: Any,
    associate: Any,
    correlation: Any,
    correlation_by_origin: Any,
    path: Path,
) -> None:
    if (
        multiplicity.GetNbinsX() != 4096
        or float(multiplicity.GetXaxis().GetXmin()) != -0.5
        or float(multiplicity.GetXaxis().GetXmax()) != 4095.5
    ):
        raise ValueError(f"{path}: multiplicity axis contract differs")
    for single, name in (
        (trigger, "hTrKinematics"),
        (associate, "hAsKinematics"),
    ):
        if (
            single.GetAxis(0).GetNbins() != 100
            or single.GetAxis(1).GetNbins() != 100
            or single.GetAxis(3).GetNbins() != 4096
            or not _has_inclusive_upper_edge(single.GetAxis(1), 4.0)
            or not _has_inclusive_upper_edge(single.GetAxis(2), 7000.0)
            or float(single.GetAxis(3).GetXmin()) != -0.5
            or float(single.GetAxis(3).GetXmax()) != 4095.5
        ):
            raise ValueError(f"{path}: {name} axis contract differs")
    for sparse, name in (
        (correlation, "hCorrelations"),
        (correlation_by_origin, "hCorrelationsByOrigin"),
    ):
        if (
            sparse.GetAxis(0).GetNbins() != 100
            or sparse.GetAxis(1).GetNbins() != 100
            or sparse.GetAxis(2).GetNbins() != 100
            or sparse.GetAxis(3).GetNbins() != 100
            or sparse.GetAxis(6).GetNbins() != 4096
            or not _has_inclusive_upper_edge(sparse.GetAxis(1), 8.0)
            or not _has_inclusive_upper_edge(sparse.GetAxis(2), 4.0)
            or not _has_inclusive_upper_edge(sparse.GetAxis(3), 4.0)
            or not _has_inclusive_upper_edge(sparse.GetAxis(4), 7000.0)
            or not _has_inclusive_upper_edge(sparse.GetAxis(5), 7000.0)
            or float(sparse.GetAxis(6).GetXmin()) != -0.5
            or float(sparse.GetAxis(6).GetXmax()) != 4095.5
        ):
            raise ValueError(f"{path}: {name} axis contract differs")
    origin_axis = correlation_by_origin.GetAxis(7)
    if (
        origin_axis.GetNbins() != 6
        or float(origin_axis.GetXmin()) != 0.5
        or float(origin_axis.GetXmax()) != 6.5
    ):
        raise ValueError(f"{path}: associate-origin axis contract differs")


def _projection_integral(
    histogram: Any,
    kind: str,
    multiplicity_range: tuple[float, float],
) -> float:
    _reset_sparse_axes(histogram)
    if kind == "correlation":
        histogram.GetAxis(6).SetRangeUser(*multiplicity_range)
        projected = histogram.Projection(0, "E")
    elif kind == "correlation_resolved_associate_origins":
        histogram.GetAxis(6).SetRangeUser(*multiplicity_range)
        # The versioned origin category is:
        # 1 selected-hard companion, 2 selected-hard noncompanion,
        # 3 shower, 4 MPI, 5 other resolved, 6 unresolved.
        histogram.GetAxis(7).SetRange(1, 5)
        projected = histogram.Projection(0, "E")
    elif kind == "trigger":
        histogram.GetAxis(3).SetRangeUser(*multiplicity_range)
        projected = histogram.Projection(2, "E")
    else:
        raise ValueError(f"unknown projection kind {kind}")
    projected.SetDirectory(0)
    value = float(projected.Integral(1, projected.GetNbinsX()))
    if not math.isfinite(value):
        raise ValueError(f"non-finite {kind} projection")
    del projected
    return value


def _record_inventory(
    inventory: dict[Path, dict[str, Any]],
    path: Path,
    per_job_root: Path,
    tune: str,
    slot: int,
    raw_sha256: str,
) -> None:
    if path in inventory:
        existing = inventory[path]
        if (
            existing["tune"] != tune
            or existing["canonical_slot"] != slot
            or existing["upstream_raw_sha256"] != raw_sha256
            or existing["bytes"] != path.stat().st_size
            or existing["sha256"] != sha256(path)
        ):
            raise ValueError(f"consumed pair input changed during audit: {path}")
        return
    inventory[path] = {
        "schema": INVENTORY_SCHEMA,
        "tune": tune,
        "canonical_slot": slot,
        "path": path.relative_to(per_job_root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "upstream_raw_sha256": raw_sha256,
    }


def _validate_pair_file_contract(
    root: Any,
    root_file: Any,
    path: Path,
    row: dict[str, Any],
    pair: dict[str, Any],
    contracts: dict[str, Any],
    common_analysis: dict[str, str],
) -> tuple[Any, Any, Any, Any]:
    exact_strings = {
        "analysis_schema": contracts["analysis_schema"],
        "analysis_implementation": contracts["analysis_implementation"],
        "analysis_version": contracts["analysis_version"],
        "analysis_profile": contracts["analysis_profile"],
        "pair_combinatorics_mode": contracts["pair_combinatorics_mode"],
        "event_filter_schema": "all_events_v1",
        "selector_version": contracts["selector"],
        "upstream_raw_schema": contracts["raw_schema"],
        "upstream_raw_sha256": row["raw_sha256"],
        "upstream_origin_algorithm": contracts["origin_algorithm"],
        "upstream_selector_version": contracts["selector"],
        "upstream_campaign": row["campaign"],
        "upstream_tune": row["tune"],
        "upstream_repository_commit": row["repository_commit"],
        "upstream_executable_sha256": row["producer_executable_sha256"],
        "upstream_effective_settings_schema":
            contracts["effective_settings_schema"],
        "associate_origin_category_schema":
            contracts["associate_origin_category_schema"],
        "associate_origin_category_labels":
            contracts["associate_origin_category_labels"],
        "species_registry_sha256": contracts["species_registry_sha256"],
        "upstream_tune_difference_allowlist_schema":
            contracts["tune_difference_allowlist_schema"],
        "upstream_tune_difference_allowlist_sha256":
            contracts["tune_difference_allowlist_sha256"],
        "pair_registry_sha256": contracts["pair_registry_sha256"],
        "heavy_sector": pair["sector"],
        "heavy_sign": pair["heavy_sign"],
    }
    observed = {
        name: _root_string(root_file, name) for name in exact_strings
    }
    for name, expected in exact_strings.items():
        if observed[name] != expected:
            raise ValueError(
                f"{path}: {name}={observed[name]!r}, expected {expected!r}"
            )
    analysis_commit = _root_string(root_file, "analysis_repository_commit")
    macro_sha = _root_string(root_file, "analysis_macro_sha256")
    stability_schema = _root_string(
        root_file, "upstream_heavy_stability_audit_schema"
    )
    stability_sha = _root_string(
        root_file, "upstream_heavy_stability_audit_sha256"
    )
    effective_sha = _root_string(
        root_file, "upstream_effective_settings_sha256"
    )
    if (
        not HEX40.fullmatch(analysis_commit)
        or not HEX64.fullmatch(macro_sha)
        or stability_schema != contracts["heavy_stability_audit_schema"]
        or not HEX64.fullmatch(stability_sha)
        or not HEX64.fullmatch(effective_sha)
    ):
        raise ValueError(f"{path}: invalid analysis/upstream SHA provenance")
    current_common = {
        "analysis_repository_commit": analysis_commit,
        "analysis_macro_sha256": macro_sha,
    }
    if not common_analysis:
        common_analysis.update(current_common)
    elif current_common != common_analysis:
        raise ValueError(f"{path}: mixed analysis implementation provenance")

    expected_parameters: dict[str, int | float] = {
        "trigger_pdg": int(pair["trigger_pdg"]),
        "associate_pdg": int(pair["associate_pdg"]),
        "reference_meson_pdg": int(pair["reference_meson_pdg"]),
        "trigger_pt_min_exclusive": 1.0,
        "associate_pt_min_exclusive": 0.15,
        "eta_abs_max_inclusive": 4.0,
        "same_sign_pair_factor": 1.0,
        "upstream_heavy_flavour_conservation_failures": 0,
        "upstream_origin_classification_failures": 0,
        "event_filter_modulo": 0,
        "event_filter_remainder": -1,
        "input_events": int(row["requested_successes"]),
        "source_input_events": int(row["requested_successes"]),
        "input_file_count": 1,
        "primary_all_heavy_closure_failures": 0,
    }
    for name, expected in expected_parameters.items():
        observed_value = _root_parameter(root_file, name)
        if isinstance(expected, float):
            if not nearly_equal(float(observed_value), expected):
                raise ValueError(f"{path}: TParameter {name} differs")
        elif int(observed_value) != expected:
            raise ValueError(f"{path}: TParameter {name} differs")
    input_weight = float(_root_parameter(root_file, "input_sum_weights"))
    trigger_count = int(_root_parameter(root_file, "trigger_count"))
    trigger_weight = float(_root_parameter(root_file, "trigger_sum_weights"))
    pair_count = int(_root_parameter(root_file, "pair_count"))
    pair_weight = float(_root_parameter(root_file, "pair_sum_weights"))
    direct_primary_heavy = int(
        _root_parameter(root_file, "direct_primary_heavy_count")
    )
    central_ground_states = int(
        _root_parameter(root_file, "central_ground_state_count")
    )
    central_hard_triggers = int(
        _root_parameter(root_file, "central_hard_trigger_count")
    )
    if (
        not math.isfinite(input_weight)
        or input_weight == 0.0
        or trigger_count < 0
        or pair_count < 0
        or not math.isfinite(trigger_weight)
        or not math.isfinite(pair_weight)
        or direct_primary_heavy < 0
        or central_ground_states < 0
        or central_ground_states > direct_primary_heavy
        or central_hard_triggers < 0
        or central_hard_triggers > central_ground_states
    ):
        raise ValueError(f"{path}: invalid count/weight TParameters")

    multiplicity = root_file.Get("summed MULTIPLICITY")
    trigger = root_file.Get("hTrKinematics")
    associate = root_file.Get("hAsKinematics")
    correlation = root_file.Get("hCorrelations")
    correlation_by_origin = root_file.Get("hCorrelationsByOrigin")
    if (
        not multiplicity
        or multiplicity.ClassName() != "TH1D"
        or not trigger
        or not str(trigger.ClassName()).startswith("THnSparse")
        or not associate
        or not str(associate.ClassName()).startswith("THnSparse")
        or not correlation
        or not str(correlation.ClassName()).startswith("THnSparse")
        or not correlation_by_origin
        or not str(correlation_by_origin.ClassName()).startswith("THnSparse")
        or trigger.GetNdimensions() != 4
        or associate.GetNdimensions() != 4
        or correlation.GetNdimensions() != 7
        or correlation_by_origin.GetNdimensions() != 8
    ):
        raise ValueError(f"{path}: Paul-compatible histogram objects differ")
    _validate_pair_axis_contract(
        multiplicity,
        trigger,
        associate,
        correlation,
        correlation_by_origin,
        path,
    )
    for histogram, object_name in (
        (trigger, "hTrKinematics"),
        (associate, "hAsKinematics"),
        (correlation, "hCorrelations"),
        (correlation_by_origin, "hCorrelationsByOrigin"),
    ):
        _validate_sparse_no_flow(root, histogram, path, object_name)
    if (
        not nearly_equal(
            float(multiplicity.Integral(1, multiplicity.GetNbinsX())),
            input_weight,
        )
        or int(round(multiplicity.GetEntries())) != int(row["requested_successes"])
        or not nearly_equal(float(trigger.GetSumw()), trigger_weight)
        or not nearly_equal(float(associate.GetSumw()), pair_weight)
        or not nearly_equal(float(correlation.GetSumw()), pair_weight)
        or not nearly_equal(
            float(correlation_by_origin.GetSumw()), pair_weight
        )
        or int(round(trigger.GetEntries())) != trigger_count
        or int(round(associate.GetEntries())) != pair_count
        or int(round(correlation.GetEntries())) != pair_count
        or int(round(correlation_by_origin.GetEntries())) != pair_count
        or multiplicity.GetBinContent(0) != 0.0
        or multiplicity.GetBinContent(multiplicity.GetNbinsX() + 1) != 0.0
    ):
        raise ValueError(f"{path}: histogram/TParameter closure differs")
    return multiplicity, trigger, correlation, correlation_by_origin


def inspect_pair_file(
    path: Path,
    per_job_root: Path,
    row: dict[str, Any],
    pair: dict[str, Any],
    contracts: dict[str, Any],
    multiplicity_ranges: dict[str, tuple[float, float]],
    common_analysis: dict[str, str],
    inventory: dict[Path, dict[str, Any]],
) -> tuple[
    dict[str, tuple[float, float, float]],
    tuple[list[float], list[float]],
]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size <= 0:
        raise ValueError(f"pair input is absent, empty, or a symlink: {path}")
    _record_inventory(
        inventory,
        path,
        per_job_root,
        str(row["tune"]),
        int(row["canonical_slot"]),
        str(row["raw_sha256"]),
    )
    try:
        import ROOT  # type: ignore
    except ImportError as error:
        raise RuntimeError("PyROOT is required for the robustness audit") from error
    ROOT.TH1.AddDirectory(False)
    root_file = ROOT.TFile.Open(str(path), "READ")
    if not root_file or root_file.IsZombie():
        raise ValueError(f"cannot open pair ROOT input: {path}")
    try:
        (
            multiplicity,
            trigger,
            correlation,
            correlation_by_origin,
        ) = _validate_pair_file_contract(
            ROOT, root_file, path, row, pair, contracts, common_analysis
        )
        values: dict[str, tuple[float, float, float]] = {}
        for selection_name, multiplicity_range in multiplicity_ranges.items():
            pair_integral = _projection_integral(
                correlation, "correlation", multiplicity_range
            )
            origin_inclusive_integral = _projection_integral(
                correlation_by_origin, "correlation", multiplicity_range
            )
            if not nearly_equal(pair_integral, origin_inclusive_integral):
                raise ValueError(
                    f"{path}: hCorrelationsByOrigin does not close to "
                    f"hCorrelations for {selection_name}"
                )
            resolved_pair_integral = _projection_integral(
                correlation_by_origin,
                "correlation_resolved_associate_origins",
                multiplicity_range,
            )
            if resolved_pair_integral < 0.0:
                raise ValueError(
                    f"{path}: negative resolved-origin projection for "
                    f"{selection_name}"
                )
            trigger_integral = _projection_integral(
                trigger, "trigger", multiplicity_range
            )
            values[selection_name] = (
                pair_integral,
                trigger_integral,
                resolved_pair_integral,
            )
        centers = [
            float(multiplicity.GetBinCenter(index))
            for index in range(1, multiplicity.GetNbinsX() + 1)
        ]
        contents = [
            float(multiplicity.GetBinContent(index))
            for index in range(1, multiplicity.GetNbinsX() + 1)
        ]
        if not all(math.isfinite(value) for value in contents):
            raise ValueError(f"{path}: non-finite multiplicity histogram")
        return values, (centers, contents)
    finally:
        root_file.Close()


def strict_stability_threshold(
    centers: Sequence[float],
    contents: Sequence[float],
    percentile: float,
    context: str,
) -> int:
    if len(centers) != len(contents) or not centers:
        raise ValueError(f"{context}: multiplicity histogram layout is invalid")
    integer_centers: list[int] = []
    for index, center in enumerate(centers):
        rounded = round(center)
        if (
            not math.isfinite(center)
            or abs(center - rounded) > 1.0e-9
            or (integer_centers and rounded != integer_centers[-1] + 1)
        ):
            raise ValueError(
                f"{context}: multiplicity centers are not consecutive integers"
            )
        value = require_finite(contents[index], f"{context} content {index}")
        if value < 0.0:
            raise ValueError(f"{context}: negative multiplicity weight")
        integer_centers.append(int(rounded))
    if not math.isfinite(percentile) or not 0.0 <= percentile <= 100.0:
        raise ValueError(f"{context}: invalid percentile {percentile}")
    total = sum(contents)
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError(
            f"{context}: multiplicity histogram has nonpositive total weight"
        )
    target = (100.0 - percentile) / 100.0 * total
    running = 0.0
    for center, content in zip(integer_centers, contents):
        running += content
        if running >= target:
            return center
    raise ValueError(
        f"{context}: failed to locate percentile threshold; refusing "
        "first/last-bin fallback"
    )


def leave_one_primary_block_out_boundary_stability(
    centers: Sequence[float],
    contents_by_slot: Sequence[Sequence[float]],
    frozen_thresholds: dict[float, int],
    context: str,
) -> list[dict[str, Any]]:
    if (
        len(contents_by_slot) < MINIMUM_SLOTS
        or len(contents_by_slot) % 10
        or any(len(contents) != len(centers) for contents in contents_by_slot)
    ):
        raise ValueError(f"{context}: invalid slot multiplicity collection")
    results: list[dict[str, Any]] = []
    for omitted_block in range(10):
        retained = [0.0] * len(centers)
        retained_slots = 0
        for slot, contents in enumerate(contents_by_slot):
            if slot % 10 == omitted_block:
                continue
            retained_slots += 1
            retained = [
                total + value for total, value in zip(retained, contents)
            ]
        total = sum(retained)
        if retained_slots == 0 or not math.isfinite(total) or total <= 0.0:
            raise ValueError(
                f"{context}: empty leave-block-{omitted_block} histogram"
            )
        threshold_rows: list[dict[str, Any]] = []
        for percentile, frozen in sorted(frozen_thresholds.items()):
            threshold = strict_stability_threshold(
                centers,
                retained,
                percentile,
                f"{context}/omit_block_{omitted_block}/p{percentile:g}",
            )
            index = centers.index(float(threshold))
            before = sum(retained[:index]) / total
            through = sum(retained[: index + 1]) / total
            threshold_rows.append(
                {
                    "percentile": percentile,
                    "frozen_nch_threshold": frozen,
                    "leave_one_block_out_nch_threshold": threshold,
                    "shift_nch": threshold - frozen,
                    "target_low_activity_fraction":
                        (100.0 - percentile) / 100.0,
                    "achieved_exclusive_fraction_before_threshold": before,
                    "achieved_inclusive_fraction_through_threshold": through,
                }
            )
        results.append(
            {
                "omitted_primary_block": omitted_block,
                "retained_canonical_slots": retained_slots,
                "thresholds": threshold_rows,
                "maximum_absolute_shift_nch": max(
                    abs(row["shift_nch"]) for row in threshold_rows
                ),
            }
        )
    return results


def validate_boundary_source_union(
    tune: str,
    tune_receipt: dict[str, Any],
    aggregate_centers: Sequence[float],
    aggregate_contents: Sequence[float],
) -> dict[str, Any]:
    source = Path(str(tune_receipt["central_reference_path"]))
    try:
        import ROOT  # type: ignore
    except ImportError as error:
        raise RuntimeError(
            "PyROOT is required for boundary-source union validation"
        ) from error
    root_file = ROOT.TFile.Open(str(source), "READ")
    if not root_file or root_file.IsZombie():
        raise ValueError(f"cannot open boundary source for {tune}: {source}")
    try:
        histogram = root_file.Get("summed MULTIPLICITY")
        if (
            not histogram
            or histogram.ClassName() != "TH1D"
            or histogram.GetNbinsX() != len(aggregate_centers)
            or histogram.GetBinContent(0) != 0.0
            or histogram.GetBinContent(histogram.GetNbinsX() + 1) != 0.0
        ):
            raise ValueError(f"boundary source histogram differs for {tune}")
        source_centers = [
            float(histogram.GetBinCenter(index))
            for index in range(1, histogram.GetNbinsX() + 1)
        ]
        source_contents = [
            float(histogram.GetBinContent(index))
            for index in range(1, histogram.GetNbinsX() + 1)
        ]
        if source_centers != list(aggregate_centers):
            raise ValueError(f"boundary source binning differs for {tune}")
        differences = [
            abs(source_value - aggregate_value)
            for source_value, aggregate_value in zip(
                source_contents, aggregate_contents
            )
        ]
        for index, (source_value, aggregate_value) in enumerate(
            zip(source_contents, aggregate_contents)
        ):
            if not nearly_equal(
                source_value, aggregate_value, relative_tolerance=2.0e-10
            ):
                raise ValueError(
                    f"boundary source is not the per-job canonical union for "
                    f"{tune} at regular bin {index + 1}"
                )
        source_integral = sum(source_contents)
        receipt_integral = require_finite(
            tune_receipt["regular_bin_integral"],
            f"{tune} receipt regular-bin integral",
        )
        if not nearly_equal(
            source_integral, receipt_integral, relative_tolerance=2.0e-10
        ):
            raise ValueError(
                f"boundary receipt integral differs from its source for {tune}"
            )
        return {
            "central_reference_path": source.as_posix(),
            "central_source_file_sha256":
                tune_receipt["central_source_file_sha256"],
            "regular_bin_count": len(source_contents),
            "regular_bin_integral": source_integral,
            "maximum_absolute_bin_difference": max(differences, default=0.0),
            "relative_tolerance": 2.0e-10,
            "status": "PASS",
        }
    finally:
        root_file.Close()


def _pair_roles(
    observable: dict[str, Any], pair_lookup: dict[tuple[int, int], dict]
) -> dict[str, dict[str, Any]]:
    trigger = int(observable["trigger_pdg"])
    result: dict[str, dict[str, Any]] = {}
    for family in ("reference_meson", "baryon"):
        for sign in ("os", "ss"):
            component = observable[family][sign]
            result[f"{family}_{sign}"] = pair_lookup[
                (trigger, int(component["associate_pdg"]))
            ]
    return result


def run_audit(
    spec_path: Path,
    canonical_freeze: Path,
    per_job_root: Path,
    boundary_receipt_path: Path,
    origin_closure_report_path: Path,
    output_directory: Path,
    checkout: Path,
) -> dict[str, Any]:
    spec = load_json(spec_path)
    pair_lookup = validate_spec(spec, checkout)
    rows, freeze_provenance = validate_canonical_freeze(
        canonical_freeze, spec
    )
    (
        boundary_receipt,
        tune_multiplicity_ranges,
        tune_percentile_thresholds,
        boundary_binding,
    ) = validate_boundary_receipt(boundary_receipt_path, spec, checkout)
    origin_closure_binding = validate_final_origin_closure_report(
        origin_closure_report_path, freeze_provenance, checkout, spec
    )
    jobs_per_tune = int(freeze_provenance["jobs_per_tune"])
    alternative_blocks = next(
        (
            blocks
            for blocks in range(min(20, jobs_per_tune), 10, -1)
            if jobs_per_tune % blocks == 0
        ),
        10,
    )
    row_lookup = {
        (str(row["tune"]), int(row["canonical_slot"])): row for row in rows
    }
    common_analysis: dict[str, str] = {}
    inventory: dict[Path, dict[str, Any]] = {}
    selections = [
        *(
            {**selection, "selection_kind": "frozen_percentile"}
            for selection in spec["multiplicity_selections"]
        ),
        *(
            {**selection, "selection_kind": "fixed_nch"}
            for selection in spec["fixed_nch_selections"]
        ),
    ]
    integration = spec["integration"]
    contracts = spec["contracts"]

    first_observable = spec["observables"][0]
    multiplicity_source = _pair_roles(first_observable, pair_lookup)[
        "reference_meson_os"
    ]
    boundary_source_union_validation: dict[str, dict[str, Any]] = {}
    boundary_stability: dict[str, list[dict[str, Any]]] = {}
    for tune in EXPECTED_TUNES:
        aggregate_centers: list[float] | None = None
        aggregate_contents: list[float] | None = None
        slot_contents: list[list[float]] = []
        for slot in range(jobs_per_tune):
            row = row_lookup[(tune, slot)]
            path = (
                per_job_root
                / tune
                / f"slot_{slot:03d}"
                / str(multiplicity_source["filename"])
            )
            _, (centers, contents) = inspect_pair_file(
                path,
                per_job_root,
                row,
                multiplicity_source,
                contracts,
                {},
                common_analysis,
                inventory,
            )
            if aggregate_centers is None:
                aggregate_centers = centers
                aggregate_contents = [0.0] * len(contents)
            elif centers != aggregate_centers:
                raise ValueError(f"{path}: multiplicity binning differs")
            assert aggregate_contents is not None
            slot_contents.append(contents)
            aggregate_contents = [
                total + value
                for total, value in zip(aggregate_contents, contents)
            ]
        assert aggregate_centers is not None and aggregate_contents is not None
        boundary_source_union_validation[tune] = validate_boundary_source_union(
            tune,
            boundary_receipt["tunes"][tune],
            aggregate_centers,
            aggregate_contents,
        )
        boundary_stability[tune] = (
            leave_one_primary_block_out_boundary_stability(
                aggregate_centers,
                slot_contents,
                tune_percentile_thresholds[tune],
                tune,
            )
        )

    extracted: dict[
        tuple[str, int, str, str],
        dict[str, tuple[float, float, float]],
    ] = {}
    for tune in EXPECTED_TUNES:
        ranges = tune_multiplicity_ranges[tune]
        for slot in range(jobs_per_tune):
            row = row_lookup[(tune, slot)]
            unique_pairs: dict[str, dict[str, Any]] = {}
            for observable in spec["observables"]:
                for pair in _pair_roles(observable, pair_lookup).values():
                    existing = unique_pairs.get(str(pair["filename"]))
                    if existing is not None and existing != pair:
                        raise ValueError("filename maps to conflicting pair definitions")
                    unique_pairs[str(pair["filename"])] = pair
            for filename, pair in sorted(unique_pairs.items()):
                path = per_job_root / tune / f"slot_{slot:03d}" / filename
                values, _ = inspect_pair_file(
                    path,
                    per_job_root,
                    row,
                    pair,
                    contracts,
                    ranges,
                    common_analysis,
                    inventory,
                )
                extracted[(tune, slot, str(pair["sector"]), filename)] = values

    result_rows: list[dict[str, Any]] = []
    denominator_reports: list[dict[str, Any]] = []
    for tune in EXPECTED_TUNES:
        for observable in spec["observables"]:
            roles = _pair_roles(observable, pair_lookup)
            sector = str(observable["sector"])
            for selection in selections:
                selection_name = str(selection["name"])
                records: list[ObservableTerms] = []
                resolved_records: list[ObservableTerms] = []
                for slot in range(jobs_per_tune):
                    def value(role: str) -> tuple[float, float, float]:
                        pair = roles[role]
                        return extracted[
                            (
                                tune,
                                slot,
                                sector,
                                str(pair["filename"]),
                            )
                        ][selection_name]

                    meson_os = value("reference_meson_os")
                    meson_ss = value("reference_meson_ss")
                    baryon_os = value("baryon_os")
                    baryon_ss = value("baryon_ss")
                    trigger_denominators = (
                        meson_os[1],
                        meson_ss[1],
                        baryon_os[1],
                        baryon_ss[1],
                    )
                    if not all(
                        nearly_equal(trigger_denominators[0], denominator)
                        for denominator in trigger_denominators[1:]
                    ):
                        raise ValueError(
                            f"{tune}/{observable['name']}/{selection_name}/"
                            f"slot_{slot:03d}: shared trigger denominators differ"
                        )
                    records.append(
                        ObservableTerms(
                            PairTerms(
                                meson_os[0],
                                meson_os[1],
                                meson_ss[0],
                                meson_ss[1],
                            ),
                            PairTerms(
                                baryon_os[0],
                                baryon_os[1],
                                baryon_ss[0],
                                baryon_ss[1],
                            ),
                        )
                    )
                    resolved_records.append(
                        ObservableTerms(
                            PairTerms(
                                meson_os[2],
                                meson_os[1],
                                meson_ss[2],
                                meson_ss[1],
                            ),
                            PairTerms(
                                baryon_os[2],
                                baryon_os[1],
                                baryon_ss[2],
                                baryon_ss[1],
                            ),
                        )
                    )
                context = (
                    f"{tune}/{observable['name']}/{selection_name}"
                )
                computed, denominators = compute_robustness(records, context)
                resolved_computed, resolved_denominators = compute_robustness(
                    resolved_records,
                    f"{context}/exclude_unresolved_associate_origin_6",
                )
                resolved_by_quantity = {
                    result["quantity"]: result for result in resolved_computed
                }
                for result in computed:
                    resolved_result = resolved_by_quantity[result["quantity"]]
                    central_shift = (
                        resolved_result["central_full_union"]
                        - result["central_full_union"]
                    )
                    result["unresolved_associate_exclusion"] = {
                        "excluded_origin_category": 6,
                        "retained_origin_categories": [1, 2, 3, 4, 5],
                        "central_full_union":
                            resolved_result["central_full_union"],
                        "central_shift_excluded_minus_inclusive": central_shift,
                        "central_relative_shift":
                            central_shift / result["central_full_union"]
                            if result["central_full_union"] != 0.0
                            else None,
                        "primary_10_block":
                            resolved_result["primary_10_block"],
                        "alternative_partition":
                            resolved_result["alternative_partition"],
                        "alternative_partition_block_count":
                            resolved_result[
                                "alternative_partition_block_count"
                            ],
                        "delete_one_file_jackknife":
                            resolved_result["delete_one_file_jackknife"],
                    }
                    result.update(
                        {
                            "tune": tune,
                            "sector": sector,
                            "observable": observable["name"],
                            "multiplicity_selection": selection_name,
                            "multiplicity_selection_kind":
                                selection["selection_kind"],
                            "multiplicity_nch_min":
                                tune_multiplicity_ranges[tune][selection_name][0],
                            "multiplicity_nch_max":
                                tune_multiplicity_ranges[tune][selection_name][1],
                        }
                    )
                    result_rows.append(result)
                denominator_reports.append(
                    {
                        "tune": tune,
                        "sector": sector,
                        "observable": observable["name"],
                        "multiplicity_selection": selection_name,
                        "inclusive": denominators,
                        "exclude_unresolved_associate_origin_6":
                            resolved_denominators,
                    }
                )

    inventory_rows = [
        inventory[path] for path in sorted(inventory, key=lambda item: str(item))
    ]
    checkout_commit = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    tracked_status = subprocess.check_output(
        [
            "git",
            "-C",
            str(checkout),
            "status",
            "--porcelain",
            "--untracked-files=no",
        ],
        text=True,
    ).strip()
    if (
        checkout_commit != common_analysis.get("analysis_repository_commit")
        or tracked_status
    ):
        raise ValueError(
            "robustness checkout is not the exact clean analysis commit"
        )
    macro_path = checkout / "AnalysisScripts/status_analysis_THnSparse_qq.C"
    if sha256(macro_path) != common_analysis.get("analysis_macro_sha256"):
        raise ValueError("checked-out analysis macro checksum differs from inputs")
    for production_commit in sorted(
        {str(row["repository_commit"]) for row in rows}
    ):
        ancestor = subprocess.run(
            [
                "git",
                "-C",
                str(checkout),
                "merge-base",
                "--is-ancestor",
                production_commit,
                checkout_commit,
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if ancestor.returncode != 0:
            raise ValueError(
                f"production commit {production_commit} is not an ancestor "
                "of the analysis commit"
            )
    inventory_digest = json_sha256(inventory_rows)
    report = {
        "schema": REPORT_SCHEMA,
        "completion_state": "DESCRIPTIVE_CROSS_CHECK_COMPLETE",
        "publication_decision":
            "NOT_EVALUATED_NO_PREDECLARED_AGREEMENT_THRESHOLD",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "specification_path": spec_path.resolve().as_posix(),
        "specification_sha256": sha256(spec_path),
        "checkout": checkout.resolve().as_posix(),
        "canonical_freeze": canonical_freeze.resolve().as_posix(),
        "per_job_root": per_job_root.resolve().as_posix(),
        "canonical_provenance": freeze_provenance,
        "final_origin_closure_report": origin_closure_binding,
        "multiplicity_boundary_receipt": boundary_binding,
        "analysis_provenance": common_analysis,
        "method": spec["method"],
        "integration": integration,
        "partition_membership": {
            "primary_10_block": [
                {
                    "block": block,
                    "canonical_slots": [
                        slot
                        for slot in range(jobs_per_tune)
                        if slot % 10 == block
                    ],
                }
                for block in range(10)
            ],
            "alternative_partition": [
                {
                    "block": block,
                    "canonical_slots": [
                        slot
                        for slot in range(jobs_per_tune)
                        if slot % alternative_blocks == block
                    ],
                }
                for block in range(alternative_blocks)
            ],
            "delete_one_file_jackknife":
                "replicate index equals omitted canonical slot",
        },
        "multiplicity_percentile_thresholds_by_tune":
            tune_percentile_thresholds,
        "multiplicity_boundary_source_union_validation":
            boundary_source_union_validation,
        "leave_one_primary_block_out_boundary_stability_by_tune":
            boundary_stability,
        "fixed_nch_selections": spec["fixed_nch_selections"],
        "multiplicity_nch_ranges_by_tune": {
            tune: {
                name: {"minimum": interval[0], "maximum": interval[1]}
                for name, interval in ranges.items()
            }
            for tune, ranges in tune_multiplicity_ranges.items()
        },
        "consumed_pair_file_count": len(inventory_rows),
        "consumed_pair_inventory_sha256": inventory_digest,
        "denominator_diagnostics": denominator_reports,
        "results": result_rows,
        "interpretation_notice": (
            "The reported estimator differences are descriptive evidence. "
            "This v1 specification defines no numerical pass threshold; "
            "physics/statistics reviewers must assess any instability."
        ),
    }
    report["payload_sha256"] = json_sha256(report)

    outputs = spec["outputs"]
    json_path = output_directory / str(outputs["json"])
    csv_path = output_directory / str(outputs["csv"])
    inventory_path = output_directory / str(outputs["input_inventory_csv"])
    atomic_write(
        json_path,
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    csv_fields = [
        "schema",
        "tune",
        "sector",
        "observable",
        "multiplicity_selection",
        "multiplicity_selection_kind",
        "multiplicity_nch_min",
        "multiplicity_nch_max",
        "quantity",
        "central_full_union",
        "exclude_unresolved_central_full_union",
        "exclude_unresolved_central_shift",
        "exclude_unresolved_central_relative_shift",
        "exclude_unresolved_primary_10_block_standard_error",
        "exclude_unresolved_alternative_partition_standard_error",
        "exclude_unresolved_delete_one_file_jackknife_standard_error",
        "primary_10_block_replicates",
        "primary_10_block_mean",
        "primary_10_block_sample_standard_deviation",
        "primary_10_block_standard_error",
        "alternative_partition_block_count",
        "alternative_partition_replicates",
        "alternative_partition_mean",
        "alternative_partition_sample_standard_deviation",
        "alternative_partition_standard_error",
        "delete_one_file_jackknife_replicates",
        "delete_one_file_jackknife_mean",
        "delete_one_file_jackknife_standard_error",
        "alternative_over_primary_10",
        "jackknife_over_primary_10",
        "primary_10_block_zero_standard_error",
        "alternative_partition_zero_standard_error",
        "delete_one_file_jackknife_zero_standard_error",
    ]
    csv_stream = io.StringIO()
    writer = csv.DictWriter(csv_stream, fieldnames=csv_fields)
    writer.writeheader()
    for row in result_rows:
        primary = row["primary_10_block"]
        alternative = row["alternative_partition"]
        jackknife = row["delete_one_file_jackknife"]
        ratios = row["standard_error_ratios_for_description_only"]
        zero_flags = row["zero_standard_error_flags"]
        exclusion = row["unresolved_associate_exclusion"]
        writer.writerow(
            {
                "schema": row["schema"],
                "tune": row["tune"],
                "sector": row["sector"],
                "observable": row["observable"],
                "multiplicity_selection": row["multiplicity_selection"],
                "multiplicity_selection_kind":
                    row["multiplicity_selection_kind"],
                "multiplicity_nch_min": row["multiplicity_nch_min"],
                "multiplicity_nch_max": row["multiplicity_nch_max"],
                "quantity": row["quantity"],
                "central_full_union": row["central_full_union"],
                "exclude_unresolved_central_full_union":
                    exclusion["central_full_union"],
                "exclude_unresolved_central_shift":
                    exclusion[
                        "central_shift_excluded_minus_inclusive"
                    ],
                "exclude_unresolved_central_relative_shift":
                    exclusion["central_relative_shift"],
                "exclude_unresolved_primary_10_block_standard_error":
                    exclusion["primary_10_block"]["standard_error"],
                "exclude_unresolved_alternative_partition_standard_error":
                    exclusion["alternative_partition"]["standard_error"],
                "exclude_unresolved_delete_one_file_jackknife_standard_error":
                    exclusion["delete_one_file_jackknife"][
                        "standard_error"
                    ],
                "primary_10_block_replicates": primary["replicates"],
                "primary_10_block_mean": primary["mean"],
                "primary_10_block_sample_standard_deviation":
                    primary["sample_standard_deviation"],
                "primary_10_block_standard_error": primary["standard_error"],
                "alternative_partition_block_count":
                    row["alternative_partition_block_count"],
                "alternative_partition_replicates":
                    alternative["replicates"],
                "alternative_partition_mean": alternative["mean"],
                "alternative_partition_sample_standard_deviation":
                    alternative["sample_standard_deviation"],
                "alternative_partition_standard_error":
                    alternative["standard_error"],
                "delete_one_file_jackknife_replicates":
                    jackknife["replicates"],
                "delete_one_file_jackknife_mean": jackknife["mean"],
                "delete_one_file_jackknife_standard_error":
                    jackknife["standard_error"],
                "alternative_over_primary_10":
                    ratios["alternative_over_primary_10"],
                "jackknife_over_primary_10":
                    ratios["jackknife_over_primary_10"],
                "primary_10_block_zero_standard_error":
                    zero_flags["primary_10_block"],
                "alternative_partition_zero_standard_error":
                    zero_flags["alternative_partition"],
                "delete_one_file_jackknife_zero_standard_error":
                    zero_flags["delete_one_file_jackknife"],
            }
        )
    atomic_write(csv_path, csv_stream.getvalue())

    inventory_stream = io.StringIO()
    inventory_writer = csv.DictWriter(
        inventory_stream,
        fieldnames=[
            "schema",
            "tune",
            "canonical_slot",
            "path",
            "bytes",
            "sha256",
            "upstream_raw_sha256",
        ],
    )
    inventory_writer.writeheader()
    inventory_writer.writerows(inventory_rows)
    atomic_write(inventory_path, inventory_stream.getvalue())
    print(
        "STATISTICAL_ROBUSTNESS_COMPLETE "
        f"results={len(result_rows)} files={len(inventory_rows)} "
        f"json={json_path} csv={csv_path} inventory={inventory_path} "
        "decision=NOT_EVALUATED"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare primary 10-block SEM with the largest equal-exposure "
            "slot-modulo divisor in [11,20] (falling back to ten) and a "
            "manifest-derived N-file delete-one jackknife for predeclared "
            "representative observables."
        )
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "config/statistical_robustness_v1.json",
    )
    parser.add_argument("--canonical-freeze", type=Path, required=True)
    parser.add_argument("--per-job-root", type=Path, required=True)
    parser.add_argument(
        "--boundary-receipt",
        type=Path,
        required=True,
        help=(
            "PASS multiplicity_boundary_receipt_v1.json generated by the "
            "full paper plotting configuration"
        ),
    )
    parser.add_argument(
        "--origin-closure-report",
        type=Path,
        required=True,
        help=(
            "PASS final-origin closure report for the same sealed canonical "
            "manifest; pilot evidence is rejected"
        ),
    )
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument(
        "--checkout",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    try:
        run_audit(
            args.config.resolve(),
            args.canonical_freeze.resolve(),
            args.per_job_root.resolve(),
            args.boundary_receipt.resolve(),
            args.origin_closure_report.resolve(),
            args.output_directory.resolve(),
            args.checkout.resolve(),
        )
    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
        RuntimeError,
        subprocess.SubprocessError,
    ) as error:
        print(f"STATISTICAL_ROBUSTNESS_ERROR {error}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
