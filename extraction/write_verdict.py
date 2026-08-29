#!/usr/bin/env python3
"""Write the fail-closed corrected seven-render verdict contract."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from combine_derived import (combined_systematic, endpoint_contrast,  # noqa: E402
                             ratio_at, trend_difference, verdict)
from combine_per_class import source_exclusions  # noqa: E402
from harvest_class_axis import (assert_resolved_campaign, class_names,  # noqa: E402
                                parse_bin, parse_log)
from harvest_class_report import compare_rows  # noqa: E402
from ratio_trend import (block_covariance,  # noqa: E402
                         endpoint_contrast as aligned_endpoint_contrast)

CONTRACT_PATH = ROOT / "config/verdict_v3.json"
VERDICT_SCHEMA = "hadronization_verdict_v3"
CONTRACT_SCHEMA = "hadronization_verdict_contract_v3"
RECEIPT_SCHEMA = "hadronization_measurement_receipt_v3"
BOUNDARY_SCHEMA = "hadronization_multiplicity_boundary_receipt_v2"
EFFECTIVE_SETTINGS_SCHEMA = "hadronization_effective_tune_settings_receipt_v1"
ENVELOPE_SCHEMA = "hadronization_systematics_envelope_v1"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
PAIRS = (("MONASH", "JUNCTIONS"), ("MONASH", "CLOSEPACKING"))
OBSERVABLES = ("B+ - Lambda_b", "B+ - B-", "Lambda_b / B-")
HEX40 = re.compile(r"[0-9a-f]{40}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def require_regular(path: Path, label: str) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} is absent or a symlink: {path}")
    return path.resolve()


def require_expected_path(path: Path, expected: Path, label: str) -> Path:
    resolved = require_regular(path, label)
    if resolved != expected.resolve():
        raise ValueError(
            f"{label} resolves to {resolved}, expected {expected.resolve()}"
        )
    return resolved


def read_json(path: Path, label: str) -> tuple[Path, dict[str, Any]]:
    resolved = require_regular(path, label)
    try:
        payload = json.loads(resolved.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not valid JSON: {resolved}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"{label} is not a JSON object: {resolved}")
    return resolved, payload


def source_commit() -> str:
    commit = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    if not HEX40.fullmatch(commit):
        raise ValueError(f"source commit is malformed: {commit!r}")
    return commit


def parse_assignments(values: list[str], label: str) -> dict[str, Path]:
    parsed: dict[str, Path] = {}
    for value in values:
        name, separator, raw_path = value.partition("=")
        if not separator or not name or not raw_path:
            raise ValueError(f"{label} needs NAME=PATH, got {value!r}")
        if name in parsed:
            raise ValueError(f"duplicate {label} for {name}")
        parsed[name] = Path(raw_path)
    return parsed


def included_campaigns(policy: dict[str, Any]) -> list[str]:
    return [
        arm["campaign"]
        for source in policy["sources"]
        if source.get("included") is True
        for arm in source.get("campaigns", [])
        if arm.get("included") is True
    ]


def policy_record(
    policy_path: Path, policy: dict[str, Any], envelope: dict[str, Any]
) -> dict[str, Any]:
    if policy.get("schema") != "hadronization_systematics_sources_v1":
        raise ValueError("systematics source contract schema differs")
    exclusions, unreasoned = source_exclusions(policy)
    if unreasoned:
        raise ValueError(
            "systematics source exclusions are unreasoned: "
            + "; ".join(unreasoned)
        )
    if envelope.get("sources") != policy.get("sources"):
        raise ValueError(
            "systematic-source drift between envelope and committed policy"
        )
    if envelope.get("exclusions") != exclusions:
        raise ValueError(
            "systematic exclusion drift between envelope and committed policy"
        )
    return {
        "path": policy_path.as_posix(),
        "sha256": sha256(policy_path),
        "schema": policy["schema"],
        "included_sources": [
            source for source in policy["sources"]
            if source.get("included") is True
        ],
        "excluded_sources": [
            source for source in policy["sources"]
            if source.get("included") is False
        ],
        "exclusions": exclusions,
        "declared_absent": policy.get("declared_absent", []),
    }


def validate_boundary_receipt(
    path: Path,
    class_contract_path: Path,
    class_contract: dict[str, Any],
) -> tuple[dict[str, dict[str, float]], dict[str, Any]]:
    resolved, receipt = read_json(path, "multiplicity-boundary receipt")
    body = dict(receipt)
    claimed = body.pop("payload_sha256", None)
    if (
        receipt.get("schema") != BOUNDARY_SCHEMA
        or receipt.get("schema_version") != 2
        or receipt.get("completion_status") != "PASS"
        or claimed != json_sha256(body)
        or receipt.get("class_contract_sha256") != sha256(class_contract_path)
        or not isinstance(receipt.get("tunes"), dict)
        or set(receipt["tunes"]) != set(TUNES)
    ):
        raise ValueError(
            f"boundary receipt is incomplete or mismatched: {resolved}"
        )

    expected_classes = class_contract.get("classes")
    if not isinstance(expected_classes, list) or not expected_classes:
        raise ValueError("multiplicity class contract has no classes")
    achieved: dict[str, dict[str, float]] = {}
    for tune in TUNES:
        tune_record = receipt["tunes"][tune]
        rows = (
            tune_record.get("classes")
            if isinstance(tune_record, dict) else None
        )
        partition = (
            tune_record.get("partition")
            if isinstance(tune_record, dict) else None
        )
        if (
            not isinstance(rows, list)
            or len(rows) != len(expected_classes)
            or not isinstance(partition, dict)
            or partition.get("coverage") != "PASS"
            or partition.get("disjointness") != "PASS"
        ):
            raise ValueError(
                f"boundary receipt tune partition differs: {tune}"
            )
        by_window: dict[tuple[float, float], dict[str, Any]] = {}
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"malformed boundary class row for {tune}")
            window = (
                float(row.get("percentile_min", math.nan)),
                float(row.get("percentile_max", math.nan)),
            )
            if window in by_window:
                raise ValueError(
                    f"duplicate boundary class window for {tune}: {window}"
                )
            by_window[window] = row
        achieved[tune] = {}
        for expected in expected_classes:
            window = (
                float(expected["percentile_min"]),
                float(expected["percentile_max"]),
            )
            row = by_window.get(window)
            if row is None:
                raise ValueError(
                    f"boundary receipt lacks {tune}/{expected['class']}"
                )
            value = float(
                row.get("achieved_weighted_fraction", math.nan)
            )
            if not math.isfinite(value) or value < 0.0 or value > 1.0:
                raise ValueError(
                    "boundary achieved_weighted_fraction is invalid for "
                    f"{tune}/{expected['class']}"
                )
            achieved[tune][expected["class"]] = value
    return achieved, {
        "path": resolved.as_posix(),
        "sha256": sha256(resolved),
        "schema": receipt["schema"],
        "completion_status": receipt["completion_status"],
        "payload_sha256": claimed,
    }


def parse_pair_counts(
    text: str,
) -> dict[tuple[str, str, str, str, str], dict[str, int]]:
    rows: dict[tuple[str, str, str, str, str], dict[str, int]] = {}
    for line in text.splitlines():
        if not line.startswith("PAIR_COUNTS "):
            continue
        fields = dict(
            token.split("=", 1) for token in line.split() if "=" in token
        )
        try:
            bin_name = fields["bin"]
            cls, _low, _high = parse_bin(
                bin_name
                if bin_name.startswith("hDPhi") else "hDPhi" + bin_name
            )
            key = (
                fields["flavour"], fields["trigger"], fields["tune"],
                fields["associate"], cls,
            )
            values = {
                "N_OS": float(fields["n_os"]),
                "N_SS": float(fields["n_ss"]),
                "N_trig": float(fields["n_trig"]),
            }
        except (KeyError, ValueError) as error:
            raise ValueError(f"malformed PAIR_COUNTS row: {line}") from error
        if key in rows:
            raise ValueError(f"duplicate PAIR_COUNTS identity: {key}")
        if any(
            not math.isfinite(value) or value < 0.0
            for value in values.values()
        ):
            raise ValueError(f"invalid PAIR_COUNTS values for {key}")
        if any(value != int(value) for value in values.values()):
            raise ValueError(f"PAIR_COUNTS values are not integral for {key}")
        rows[key] = {
            name: int(value) for name, value in values.items()
        }
    if not rows:
        raise ValueError("render log carries no PAIR_COUNTS rows")
    return rows


def count_disclosure(
    uncertainty_row: dict[str, Any], counts: dict[str, int], context: str
) -> dict[str, Any]:
    n_trig = counts["N_trig"]
    n_os = counts["N_OS"]
    n_ss = counts["N_SS"]
    if n_trig == 0:
        raise ZeroDivisionError(f"{context}: N_trig is zero")
    if n_os == 0:
        raise ZeroDivisionError(f"{context}: N_OS is zero")
    balance_per_trigger = (n_os - n_ss) / n_trig
    if not math.isclose(
        float(uncertainty_row["central_triggers"]), n_trig,
        rel_tol=5e-15, abs_tol=0.0,
    ):
        raise ValueError(
            f"{context}: PAIR_COUNTS N_trig disagrees with "
            "UNCERTAINTY_MATRIX"
        )
    if not math.isclose(
        float(uncertainty_row["central_yield"]), balance_per_trigger,
        rel_tol=5e-15, abs_tol=1e-15,
    ):
        raise ValueError(
            f"{context}: PAIR_COUNTS yield disagrees with "
            "UNCERTAINTY_MATRIX"
        )
    return {
        "N_trig": n_trig,
        "N_OS": n_os,
        "N_SS": n_ss,
        "N_OS_over_N_trig": n_os / n_trig,
        "N_SS_over_N_trig": n_ss / n_trig,
        "N_OS_minus_N_SS_over_N_trig": balance_per_trigger,
        "same_sign_fraction_of_opposite_sign_counts": {
            "formula": "N_SS / N_OS",
            "value": n_ss / n_os,
        },
        "retained_fraction_after_subtraction": {
            "formula": "(N_OS - N_SS) / N_OS",
            "value": (n_os - n_ss) / n_os,
        },
    }


def measurement_binding(
    campaign: str,
    dataset: str,
    log_path: Path,
    receipt_path: Path,
    results_root: Path,
    commit: str,
    class_contract_path: Path,
    class_contract: dict[str, Any],
) -> tuple[
    dict[str, Any], dict, dict[str, dict[str, float]], dict
]:
    base = (
        results_root / campaign / commit[:12] / "measurements" / dataset
    )
    log = require_expected_path(
        log_path, base / "render.log", f"{campaign} render log"
    )
    receipt_file, receipt = read_json(
        receipt_path, f"{campaign} measurement receipt"
    )
    if receipt_file != (base / "measurement_receipt.json").resolve():
        raise ValueError(
            f"{campaign} measurement receipt is outside its commit-scoped root"
        )
    log_digest = sha256(log)
    if (
        receipt.get("schema") != RECEIPT_SCHEMA
        or receipt.get("completion_status") != "PASS"
        or receipt.get("purpose") != "measurement"
        or receipt.get("publication_eligible") is not False
        or receipt.get("campaign") != campaign
        or receipt.get("render_exit_status") != 0
        or receipt.get("output_assertion_exit_status") != 0
        or receipt.get("log_sha256") != log_digest
        or receipt.get("failure_reasons") not in ([], None)
        or receipt.get("missing_uncertainty_identities") not in ([], None)
        or receipt.get("unexpected_uncertainty_identities") not in ([], None)
        or receipt.get("duplicate_uncertainty_identities") not in (0, None)
        or receipt.get("non_pass_uncertainty_rows") not in ([], None)
    ):
        raise ValueError(
            f"{campaign} measurement receipt is not an exact PASS for its log"
        )
    text = log.read_text(errors="replace")
    assert_resolved_campaign(text, campaign)
    rows = parse_log(text)
    for key, row in rows.items():
        if row.get("block_count") != 10 or len(row["block_yields"]) != 10:
            raise ValueError(
                f"{campaign} {key}: v2 block contract does not carry ten blocks"
            )
        if row["is_reference"] == "false" and len(row["block_ratios"]) != 10:
            raise ValueError(
                f"{campaign} {key}: v2 ratio contract does not carry ten blocks"
            )
    if (
        receipt.get("uncertainty_matrix_rows") != len(rows)
        or receipt.get("expected_uncertainty_matrix_rows") != len(rows)
    ):
        raise ValueError(
            f"{campaign} receipt row count disagrees with its render log"
        )
    boundary_path = base / "plots/multiplicity_boundary_receipt_v2.json"
    achieved, boundary = validate_boundary_receipt(
        boundary_path, class_contract_path, class_contract
    )
    return ({
        "campaign": campaign,
        "dataset": dataset,
        "render_log": {
            "path": log.as_posix(),
            "sha256": log_digest,
        },
        "measurement_receipt": {
            "path": receipt_file.as_posix(),
            "sha256": sha256(receipt_file),
            "schema": receipt["schema"],
            "completion_status": receipt["completion_status"],
        },
        "multiplicity_boundary_receipt": boundary,
    }, rows, achieved, parse_pair_counts(text))


def quantity(
    rows: dict, observable: str, tune: str, cls: str
) -> tuple[float, float]:
    if observable == "Lambda_b / B-":
        return ratio_at(rows, tune, cls)
    associate = "Lambda_b" if observable == "B+ - Lambda_b" else "B-"
    row = rows[("BEAUTY", "B^{+}", tune, associate, cls)]
    return float(row["central_yield"]), float(row["yield_sem"])


def separation(
    rows: dict, observable: str, tune_a: str, tune_b: str, cls: str
) -> tuple[float, float]:
    value_a, sem_a = quantity(rows, observable, tune_a, cls)
    value_b, sem_b = quantity(rows, observable, tune_b, cls)
    return value_a - value_b, math.hypot(sem_a, sem_b)


def assert_covariance_diagonal(
    covariance: dict[str, Any], per_class: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    classes = covariance.get("classes")
    matrix = covariance.get("covariance_of_means")
    sems = {
        row["class"]: float(row["ratio_sem"]) for row in per_class
    }
    if (
        classes != [row["class"] for row in per_class]
        or not isinstance(matrix, list)
        or len(matrix) != len(per_class)
        or any(
            not isinstance(row, list) or len(row) != len(per_class)
            for row in matrix
        )
    ):
        raise ValueError(
            "covariance matrix is not the required 11 by 11 class order"
        )
    proof = []
    for index, cls in enumerate(classes):
        diagonal = float(matrix[index][index])
        squared_sem = sems[cls] ** 2
        if not math.isclose(
            diagonal, squared_sem, rel_tol=5e-15, abs_tol=1e-30
        ):
            raise ValueError(
                f"{cls} covariance diagonal disagrees with SEM squared"
            )
        proof.append({
            "class": cls,
            "covariance_diagonal": diagonal,
            "ratio_sem_squared": squared_sem,
            "agrees": True,
        })
    return proof


def configuration_disclosure(
    contract: dict[str, Any],
    configuration: dict[str, str],
    binding: dict[str, Any],
    rows: dict,
    achieved: dict[str, dict[str, float]],
    pair_counts: dict,
    classes: list[str],
) -> dict[str, Any]:
    identity = contract["principal_count_identity"]
    tunes: dict[str, Any] = {}
    for tune in TUNES:
        disclosed = []
        for cls in classes:
            key = (
                identity["flavour"], identity["trigger"], tune,
                identity["associate"], cls,
            )
            if key not in rows:
                raise ValueError(
                    f"missing UNCERTAINTY_MATRIX identity: {key}"
                )
            if key not in pair_counts:
                raise ValueError(f"missing PAIR_COUNTS identity: {key}")
            row = rows[key]
            pooled_ratio, ratio_sem = ratio_at(rows, tune, cls)
            blocks = list(row["block_ratios"])
            if len(blocks) != 10:
                raise ValueError(
                    f"{configuration['campaign']} {tune}/{cls}: "
                    "expected ten block ratios"
                )
            disclosed.append({
                "class": cls,
                **count_disclosure(
                    row, pair_counts[key],
                    f"{configuration['campaign']} {tune}/{cls}",
                ),
                "pooled_ratio": pooled_ratio,
                "ratio_sem": ratio_sem,
                "achieved_weighted_fraction": achieved[tune][cls],
                "block_ratios": blocks,
                "block_order":
                    "canonical_slot_modulo_10_ascending_0_to_9",
            })
        tunes[tune] = {"classes": disclosed}
    return {
        "campaign": configuration["campaign"],
        "dataset": configuration["dataset"],
        "role": configuration["role"],
        "inputs": binding,
        "tunes": tunes,
    }


def effective_settings_binding(
    path: Path,
    raw_paths: dict[str, Path],
    expected: Path,
    allowlist_path: Path,
) -> dict[str, Any]:
    receipt_path = require_expected_path(
        path, expected, "effective-settings receipt"
    )
    _, receipt = read_json(receipt_path, "effective-settings receipt")
    if (
        receipt.get("schema") != EFFECTIVE_SETTINGS_SCHEMA
        or receipt.get("status") != "PASS"
        or receipt.get("allowlist", {}).get("sha256")
        != sha256(allowlist_path)
        or set(receipt.get("inputs", {})) != set(TUNES)
    ):
        raise ValueError("effective-settings receipt is not an exact PASS")
    inputs = {}
    if set(raw_paths) != set(TUNES):
        raise ValueError(
            "--effective-raw must name MONASH, JUNCTIONS, and CLOSEPACKING"
        )
    for tune in TUNES:
        raw = require_regular(
            raw_paths[tune], f"{tune} effective-settings raw input"
        )
        record = receipt["inputs"][tune]
        measured = sha256(raw)
        if (
            record.get("basename") != raw.name
            or record.get("sha256") != measured
        ):
            raise ValueError(
                f"{tune} raw input does not match effective-settings receipt"
            )
        inputs[tune] = {"path": raw.as_posix(), "sha256": measured}
    return {
        "path": receipt_path.as_posix(),
        "sha256": sha256(receipt_path),
        "schema": receipt["schema"],
        "status": receipt["status"],
        "raw_inputs": inputs,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    out = [
        "# Corrected result candidate",
        "",
        f"Source commit: `{payload['source_commit']}`",
        "",
        "The c11-minus-c1 endpoint contrast is the primary model-free trend statistic.",
        "The physical-coordinate fit is deferred pending owner authorization.",
        "",
        "| tune | endpoint value | SEM |",
        "|---|---:|---:|",
    ]
    for tune in TUNES:
        endpoint = payload["nominal_ratio_trend"][tune][
            "endpoint_c11_minus_c1"
        ]
        out.append(
            f"| {tune} | {endpoint['difference']:+.8g} "
            f"| {endpoint['sem']:.8g} |"
        )
    out.extend([
        "",
        "The JSON record contains the seven-render counts, ratios, block vectors, covariance matrices, policy, exclusions, and exact input hashes.",
    ])
    return "\n".join(out) + "\n"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    staged = path.parent / f".{path.name}.staging.{os.getpid()}"
    staged.write_text(text)
    os.replace(staged, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--nominal", type=Path, required=True)
    parser.add_argument("--nominal-receipt", type=Path, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument(
        "--variation", action="append", default=[], required=True,
        metavar="CAMPAIGN=LOG",
    )
    parser.add_argument(
        "--variation-receipt", action="append", default=[], required=True,
        metavar="CAMPAIGN=RECEIPT",
    )
    parser.add_argument("--envelope", type=Path, required=True)
    parser.add_argument("--effective-settings", type=Path, required=True)
    parser.add_argument(
        "--effective-raw", action="append", default=[], required=True,
        metavar="TUNE=ROOT",
    )
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-markdown", type=Path, required=True)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    args = parser.parse_args()

    try:
        results_root = args.results_root.resolve()
        if not results_root.is_dir():
            raise ValueError(f"results root is absent: {results_root}")
        contract_path, contract = read_json(
            args.contract, "verdict-v3 contract"
        )
        if contract.get("schema") != CONTRACT_SCHEMA:
            raise ValueError("verdict-v3 contract schema differs")
        fit_status = contract.get("supporting_fit_status")
        if (
            not isinstance(fit_status, dict)
            or fit_status.get("status")
            != "DEFERRED_PENDING_OWNER_AUTHORIZATION"
            or fit_status.get("physical_coordinate_fit_produced") is not False
        ):
            raise ValueError(
                "the physical-coordinate fit must remain deferred pending "
                "owner authorization"
            )
        configurations_contract = contract.get("rendered_configurations")
        if (
            not isinstance(configurations_contract, list)
            or len(configurations_contract) != 7
            or sum(
                row.get("role") == "nominal_numerical_source"
                for row in configurations_contract
                if isinstance(row, dict)
            ) != 1
        ):
            raise ValueError(
                "verdict-v3 requires one nominal and six included renders"
            )
        commit = source_commit()
        short = commit[:12]
        outputs = contract["output_paths_relative_to_results_root"]
        expected_envelope = results_root / outputs[
            "systematics_envelope"
        ].format(commit=short)
        expected_effective = results_root / outputs[
            "effective_settings_receipt"
        ].format(commit=short)
        expected_json = results_root / outputs[
            "verdict_json"
        ].format(commit=short)
        expected_markdown = results_root / outputs[
            "verdict_markdown"
        ].format(commit=short)
        if args.out_json.resolve() != expected_json.resolve():
            raise ValueError(
                f"verdict JSON output must be {expected_json.resolve()}"
            )
        if args.out_markdown.resolve() != expected_markdown.resolve():
            raise ValueError(
                "verdict Markdown output must be "
                f"{expected_markdown.resolve()}"
            )
        if args.out_json.resolve() == args.out_markdown.resolve():
            raise ValueError(
                "verdict JSON and Markdown outputs resolve to one path"
            )

        class_contract_path, class_contract = read_json(
            ROOT / contract["class_contract"],
            "multiplicity class contract",
        )
        classes = [row["class"] for row in class_contract["classes"]]
        if classes != class_names() or len(classes) != 11:
            raise ValueError(
                "verdict-v3 requires the exact committed eleven-class contract"
            )

        policy_path, policy = read_json(
            ROOT / contract["systematics_sources_contract"],
            "systematics source contract",
        )
        expected_variations = [
            row["campaign"]
            for row in contract["rendered_configurations"]
            if row["role"] == "included_systematic_variation"
        ]
        if expected_variations != included_campaigns(policy):
            raise ValueError(
                "verdict contract variation order drifts from systematics policy"
            )
        variation_paths = parse_assignments(
            args.variation, "--variation"
        )
        variation_receipts = parse_assignments(
            args.variation_receipt, "--variation-receipt"
        )
        if (
            list(variation_paths) != expected_variations
            or list(variation_receipts) != expected_variations
        ):
            raise ValueError(
                "variation logs and receipts must name the six included "
                "campaigns in contract order"
            )

        nominal_contract = contract["nominal"]
        configurations: list[dict[str, Any]] = []
        numerical_rows: dict[str, dict] = {}
        measurement_bindings: dict[str, dict[str, Any]] = {}
        for configuration in contract["rendered_configurations"]:
            campaign = configuration["campaign"]
            if configuration["role"] == "nominal_numerical_source":
                log_path = args.nominal
                receipt_path = args.nominal_receipt
            else:
                log_path = variation_paths[campaign]
                receipt_path = variation_receipts[campaign]
            binding, rows, achieved, counts = measurement_binding(
                campaign,
                configuration["dataset"],
                log_path,
                receipt_path,
                results_root,
                commit,
                class_contract_path,
                class_contract,
            )
            measurement_bindings[campaign] = binding
            numerical_rows[campaign] = rows
            configurations.append(configuration_disclosure(
                contract,
                configuration,
                binding,
                rows,
                achieved,
                counts,
                classes,
            ))

        nominal_binding = measurement_bindings[nominal_contract["campaign"]]
        nominal_log = Path(nominal_binding["render_log"]["path"])
        control_contract = contract["historical_control"]
        expected_control = (
            results_root / control_contract["results_root_relative_path"]
        )
        control = require_expected_path(
            args.control, expected_control, "historical control log"
        )
        control_digest = sha256(control)
        if control_digest != control_contract["sha256"]:
            raise ValueError(
                "historical control log digest differs from the committed pin"
            )
        if control == nominal_log or control_digest == sha256(nominal_log):
            raise ValueError(
                "nominal numerical source and historical control resolve "
                "to the same bytes"
            )
        control_rows = parse_log(
            control.read_text(errors="replace"),
            validate_block_contract=False,
        )
        comparison = compare_rows(
            numerical_rows[nominal_contract["campaign"]], control_rows
        )
        if comparison["shared_rows"] <= 0 or not comparison["agree"]:
            raise ValueError(
                "historical shared-field reproduction control failed"
            )

        envelope_path, envelope = read_json(
            args.envelope, "systematics envelope"
        )
        envelope_path = require_expected_path(
            envelope_path, expected_envelope, "systematics envelope"
        )
        if (
            envelope.get("schema") != ENVELOPE_SCHEMA
            or envelope.get("status") != "COMPLETE"
            or envelope.get("missing") not in ([], None)
            or not envelope.get("rows")
        ):
            raise ValueError("systematics envelope is not COMPLETE")
        provenance = envelope.get("provenance")
        if (
            not isinstance(provenance, dict)
            or provenance.get("producing_commit") != commit
        ):
            raise ValueError("systematics envelope source commit differs")
        if provenance.get("sources_contract_sha256") != sha256(policy_path):
            raise ValueError(
                "systematics envelope source-policy digest differs"
            )
        policy_binding = policy_record(policy_path, policy, envelope)
        envelope_receipts = provenance.get("measurement_receipts")
        if not isinstance(envelope_receipts, dict):
            raise ValueError(
                "systematics envelope carries no measurement receipts"
            )
        for campaign in expected_variations:
            recorded = envelope_receipts.get(campaign, {})
            binding = measurement_bindings[campaign]
            if (
                recorded.get("receipt_sha256")
                != binding["measurement_receipt"]["sha256"]
                or recorded.get("boundary_receipt_sha256")
                != binding["multiplicity_boundary_receipt"]["sha256"]
                or recorded.get("completion_status") != "PASS"
            ):
                raise ValueError(
                    "systematics envelope input binding differs for "
                    f"{campaign}"
                )
        nominal_boundary = nominal_binding[
            "multiplicity_boundary_receipt"
        ]
        if (
            provenance.get("nominal_boundary_receipt_sha256")
            != nominal_boundary["sha256"]
            or Path(str(provenance.get(
                "nominal_boundary_receipt_path", ""
            ))).resolve()
            != Path(nominal_boundary["path"]).resolve()
        ):
            raise ValueError(
                "systematics envelope nominal boundary binding differs"
            )

        allowlist_path = require_regular(
            ROOT / contract["effective_settings_allowlist"],
            "effective-settings allowlist",
        )
        effective_binding = effective_settings_binding(
            args.effective_settings,
            parse_assignments(args.effective_raw, "--effective-raw"),
            expected_effective,
            allowlist_path,
        )

        nominal = numerical_rows[nominal_contract["campaign"]]
        variations = {
            campaign: numerical_rows[campaign]
            for campaign in expected_variations
        }
        nominal_trend: dict[str, Any] = {}
        for tune in TUNES:
            per_class = next(
                row["tunes"][tune]["classes"]
                for row in configurations
                if row["campaign"] == nominal_contract["campaign"]
            )
            blocks = {
                row["class"]: row["block_ratios"] for row in per_class
            }
            expected_sems = {
                row["class"]: row["ratio_sem"] for row in per_class
            }
            covariance = block_covariance(blocks, expected_sems)
            proof = assert_covariance_diagonal(covariance, per_class)
            endpoint = aligned_endpoint_contrast(
                per_class[-1]["pooled_ratio"],
                per_class[-1]["block_ratios"],
                per_class[0]["pooled_ratio"],
                per_class[0]["block_ratios"],
            )
            nominal_trend[tune] = {
                "per_class": [
                    {
                        key: row[key]
                        for key in (
                            "class", "pooled_ratio", "ratio_sem",
                            "block_ratios",
                        )
                    }
                    for row in per_class
                ],
                "endpoint_c11_minus_c1": endpoint,
                "covariance_of_class_means": covariance,
                "covariance_diagonal_proof": proof,
            }

        per_class_verdicts = []
        for tune_a, tune_b in PAIRS:
            for observable in OBSERVABLES:
                for cls in classes:
                    value, stat = separation(
                        nominal, observable, tune_a, tune_b, cls
                    )
                    varied = {
                        campaign: separation(
                            rows, observable, tune_a, tune_b, cls
                        )
                        for campaign, rows in variations.items()
                    }
                    combined = combined_systematic(
                        value, stat, varied
                    )
                    result = verdict(
                        value, stat, combined["combined_absolute"]
                    )
                    per_class_verdicts.append({
                        "pair": f"{tune_a}-{tune_b}",
                        "observable": observable,
                        "class": cls,
                        **result,
                        "terms_percent": combined["terms_percent"],
                        "quoted_arm": combined["quoted_arm"],
                        "dropped": combined["dropped"],
                    })

        endpoint_verdicts = []
        for tune in TUNES:
            value, stat = endpoint_contrast(nominal, tune)
            varied = {
                campaign: endpoint_contrast(rows, tune)
                for campaign, rows in variations.items()
            }
            combined = combined_systematic(value, stat, varied)
            endpoint_verdicts.append({
                "quantity": f"endpoint contrast {tune}",
                **verdict(value, stat, combined["combined_absolute"]),
                "terms_percent": combined["terms_percent"],
            })
        for tune in ("JUNCTIONS", "CLOSEPACKING"):
            value, stat = trend_difference(nominal, tune)
            varied = {
                campaign: trend_difference(rows, tune)
                for campaign, rows in variations.items()
            }
            combined = combined_systematic(value, stat, varied)
            endpoint_verdicts.append({
                "quantity": f"endpoint contrast {tune} - MONASH",
                **verdict(value, stat, combined["combined_absolute"]),
                "terms_percent": combined["terms_percent"],
                "quoted_arm": combined["quoted_arm"],
                "dropped": combined["dropped"],
            })

        payload = {
            "schema": VERDICT_SCHEMA,
            "created_utc": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
            "source_commit": commit,
            "verdict_contract": {
                "path": contract_path.as_posix(),
                "sha256": sha256(contract_path),
                "schema": contract["schema"],
            },
            "multiplicity_class_contract": {
                "path": class_contract_path.as_posix(),
                "sha256": sha256(class_contract_path),
                "schema": class_contract.get("schema"),
            },
            "effective_settings_allowlist": {
                "path": allowlist_path.as_posix(),
                "sha256": sha256(allowlist_path),
            },
            "roles": {
                "nominal":
                    "new v2 render; sole source of new numerical arithmetic",
                "historical_control":
                    "accepted render; shared-field reproduction comparison only",
            },
            "historical_control": {
                "path": control.as_posix(),
                "sha256": control_digest,
                "shared_fields": control_contract["shared_fields"],
                "comparison": comparison,
                "used_for_new_arithmetic": False,
            },
            "systematics_envelope": {
                "path": envelope_path.as_posix(),
                "sha256": sha256(envelope_path),
                "schema": envelope["schema"],
                "status": envelope["status"],
            },
            "systematics_policy": policy_binding,
            "effective_settings_receipt": effective_binding,
            "rendered_configurations": configurations,
            "nominal_ratio_trend": nominal_trend,
            "systematic_verdict": {
                "per_class": per_class_verdicts,
                "endpoint": endpoint_verdicts,
                "derived_delta_sem_method":
                    "independent_variation_and_nominal_quadrature_v1",
            },
            "excluded_rendered_configurations":
                contract["excluded_rendered_configurations"],
            "supporting_fit_status": contract["supporting_fit_status"],
        }
        body = dict(payload)
        payload["payload_sha256"] = json_sha256(body)
        atomic_write(
            args.out_json.resolve(),
            json.dumps(
                payload, indent=2, sort_keys=True, allow_nan=False
            ) + "\n",
        )
        atomic_write(
            args.out_markdown.resolve(), render_markdown(payload)
        )
        print(
            "VERDICT_V3 "
            f"configurations={len(configurations)} "
            f"classes={len(classes)} tunes={len(TUNES)} "
            f"out={args.out_json.resolve()}"
        )
        return 0
    except (
        KeyError, OSError, TypeError, ValueError, ZeroDivisionError,
        subprocess.SubprocessError,
    ) as error:
        print(f"VERDICT_V3_REFUSED {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
