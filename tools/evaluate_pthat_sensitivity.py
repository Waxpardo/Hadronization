#!/usr/bin/env python3
"""Extract and decide the predeclared Gate-B pTHat sensitivity test.

The nine raw inputs are selected only from the immutable Gate-B manifest.
Threshold samples are independent. Ten event_id-modulo blocks are extracted
from raw-v5 and all nonlinear observables are formed inside each block before
comparison. The decision fails closed: incomplete or statistically undefined
evidence can never produce PASS.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
import re
import statistics
import subprocess
import tempfile
from pathlib import Path
from typing import Any


SPEC_SCHEMA = "hf_gate_b_pthat_sensitivity_spec_v1"
EXTRACT_SCHEMA = "hf_gate_b_pthat_sensitivity_extract_v1"
REPORT_SCHEMA = "hf_gate_b_pthat_sensitivity_report_v1"
OUTCOMES = (
    "PASS",
    "TECHNICAL_FAIL",
    "INCONCLUSIVE",
    "SCIENTIFIC_REVIEW_REQUIRED",
)
EXIT_CODES = {
    "PASS": 0,
    "TECHNICAL_FAIL": 2,
    "INCONCLUSIVE": 3,
    "SCIENTIFIC_REVIEW_REQUIRED": 4,
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SAFE_TOKEN_RE = re.compile(r"^[A-Za-z0-9._-]+$")

# These values are part of the pre-data decision contract, rather than
# user-adjustable plotting parameters.  With 32 observables, three tunes and
# two independent threshold comparisons, the simultaneous family contains
# 192 comparisons.  The critical value was evaluated as
# scipy.stats.t.ppf(1 - 0.05 / (2 * 192), 9).
FROZEN_FAMILY_COMPARISONS = 192
FROZEN_BONFERRONI_CRITICAL_VALUE = 5.797108070583989
FROZEN_MARGINS_MAX_ABS_LOG_RATIO = {
    "multiplicity_mean": 0.048790164169432,
    "multiplicity_shape": 0.095310179804325,
    "trigger_rate_per_generated_event": 0.139761942375159,
    "trigger_pt_shape": 0.139761942375159,
    "os_yield": 0.139761942375159,
    "ss_yield": 0.139761942375159,
    "balancing_yield": 0.139761942375159,
    "baryon_meson_ratio": 0.182321556793955,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


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


def require_finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} is not numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} is not finite")
    return result


def expected_observable_names(spec: dict[str, Any]) -> list[str]:
    names = ["multiplicity_mean"]
    names.extend(
        f"multiplicity_shape:{index}"
        for index in range(len(spec["multiplicity_bins"]) - 1)
    )
    names.extend(
        f"trigger_rate_per_generated_event:{group['name']}"
        for group in spec["trigger_groups"]
    )
    names.extend(
        f"trigger_pt_shape:{group['name']}:{index}"
        for group in spec["trigger_groups"]
        for index in range(len(spec["trigger_pt_bins_gev"]) - 1)
    )
    names.extend(
        f"os_yield:{group['name']}" for group in spec["yield_groups"]
    )
    names.extend(
        f"ss_yield:{group['name']}" for group in spec["yield_groups"]
    )
    names.extend(
        f"balancing_yield:{group['name']}"
        for group in spec["yield_groups"]
    )
    names.extend(
        f"baryon_meson_ratio:{ratio['name']}"
        for ratio in spec["baryon_meson_ratios"]
    )
    if len(names) != len(set(names)):
        raise ValueError("decision observable names are not unique")
    return names


def validate_spec(spec: dict[str, Any]) -> None:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("frozen") is not True:
        raise ValueError("pTHat sensitivity specification is not frozen v1")
    review = spec.get("scientific_review")
    if (
        spec.get("scientific_review_status")
        != "APPROVED_GATE_B_OWNER_REVIEW"
        or not isinstance(review, dict)
        or set(review)
        != {
            "decision",
            "reviewer",
            "reviewer_role",
            "decision_utc",
            "rationale",
        }
        or review.get("decision") != "APPROVE_PTHAT_SENSITIVITY_SPEC"
        or review.get("reviewer_role")
        != "project_owner_or_designated_physics_statistics_reviewer"
        or not isinstance(review.get("reviewer"), str)
        or not review["reviewer"].strip()
        or any(
            token in review["reviewer"].upper()
            for token in ("PLACEHOLDER", "UNIT TEST", "SYNTHETIC", "TODO")
        )
        or not isinstance(review.get("rationale"), str)
        or not review["rationale"].strip()
        or not isinstance(review.get("decision_utc"), str)
    ):
        raise ValueError(
            "pTHat sensitivity specification lacks the required pre-pilot "
            "owner/physics-statistics approval"
        )
    try:
        decision_time = dt.datetime.fromisoformat(
            review["decision_utc"].replace("Z", "+00:00")
        )
    except ValueError as error:
        raise ValueError(
            "pTHat sensitivity scientific-review timestamp is invalid"
        ) from error
    if (
        decision_time.tzinfo is None
        or decision_time.astimezone(dt.timezone.utc)
        > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5)
    ):
        raise ValueError(
            "pTHat sensitivity scientific-review timestamp is absent/future"
        )
    decision = spec.get("decision", {})
    if tuple(decision.get("outcomes", ())) != OUTCOMES:
        raise ValueError("decision outcomes/order differ from the v1 contract")
    if (
        decision.get("multiple_comparison_method")
        != "bonferroni_simultaneous_log_ratio_ci_with_zero_shift_gate"
        or decision.get("independent_threshold_samples") is not True
    ):
        raise ValueError("unsupported statistical decision contract")
    if (
        decision.get("resolved_shift_policy")
        != "scientific_review_if_simultaneous_log_ratio_interval_excludes_zero_regardless_of_margin"
    ):
        raise ValueError("resolved pTHat-shift policy changed")
    alpha = require_finite(decision.get("familywise_alpha"), "familywise_alpha")
    if alpha != 0.05:
        raise ValueError("familywise_alpha differs from the frozen value 0.05")
    blocks = spec.get("blocks", {})
    if (
        blocks.get("count") != 10
        or blocks.get("minimum_finite_blocks") != 10
        or blocks.get("assignment") != "unsigned_event_id_modulo"
    ):
        raise ValueError("v1 requires ten complete event_id-modulo blocks")
    selection = spec.get("selection", {})
    expected_selection = {
        "direct_primary_status_min": 81,
        "direct_primary_status_max": 89,
        "require_positive_status": True,
        "require_final": True,
        "require_central_ground_state": True,
        "trigger_pt_min_exclusive_gev": 1.0,
        "associate_pt_min_exclusive_gev": 0.15,
        "abs_eta_max_inclusive": 4.0,
        "trigger_origin": "selected_hard",
        "associate_origins": "inclusive",
        "ordered_pairs": True,
        "pair_combinatorics_mode": "ordered_conditional_v1",
        "exclude_same_event_record_index": True,
        "same_sign_pair_factor": 1.0,
    }
    for key, expected in expected_selection.items():
        if selection.get(key) != expected:
            raise ValueError(
                f"selection {key}={selection.get(key)!r}, "
                f"expected {expected!r}"
            )
    if decision.get("forbid_event_count_as_cross_section") is not True:
        raise ValueError("event-count/cross-section safeguard was disabled")
    if (
        spec.get("trigger_pt_diagnostic_overflow_policy")
        != "report_and_fail_closed_without_excluding_from_integrated_yields"
    ):
        raise ValueError("trigger-pT diagnostic overflow policy changed")
    if spec.get("trigger_pt_bins_gev") != [
        1.0,
        2.0,
        4.0,
        8.0,
        16.0,
        7000.0,
    ]:
        raise ValueError("frozen trigger-pT diagnostic binning changed")
    profiles = spec.get("manifest_contract", {}).get("threshold_profiles", [])
    if {row.get("pthat_min") for row in profiles} != {"0.5", "1.0", "2.0"}:
        raise ValueError("exact three-threshold Gate-B profiles are required")
    family_size = (
        len(spec["manifest_contract"]["tunes"])
        * len(spec["manifest_contract"]["comparisons"])
        * len(expected_observable_names(spec))
    )
    critical = require_finite(
        decision.get("bonferroni_critical_value"),
        "bonferroni_critical_value",
    )
    if (
        family_size != FROZEN_FAMILY_COMPARISONS
        or decision.get("predeclared_family_comparisons")
        != FROZEN_FAMILY_COMPARISONS
        or decision.get("critical_distribution") != "student_t"
        or decision.get("conservative_degrees_of_freedom") != 9
        or critical != FROZEN_BONFERRONI_CRITICAL_VALUE
        or decision.get("bonferroni_critical_value_definition")
        != "t_9 quantile at 1 - 0.05/(2*192)"
    ):
        raise ValueError("predeclared simultaneous-CI family is inconsistent")
    margins = decision.get("margins_max_abs_log_ratio", {})
    if margins != FROZEN_MARGINS_MAX_ABS_LOG_RATIO:
        raise ValueError("equivalence margins differ from the frozen contract")


def validate_manifest(
    spec: dict[str, Any],
    campaign: dict[str, Any],
    rows: list[dict[str, Any]],
    checkout: Path | None = None,
    spec_sha256: str | None = None,
) -> dict[tuple[str, str], dict[str, Any]]:
    contract = spec["manifest_contract"]
    raw = spec["raw_contract"]
    if campaign.get("schema") != contract["schema"]:
        raise ValueError("Gate-B campaign schema mismatch")
    for key in ("raw_schema", "selector", "origin_algorithm"):
        if campaign.get(key) != raw[key]:
            raise ValueError(f"campaign {key} differs from sensitivity spec")
    campaign_spec_sha = campaign.get("pthat_sensitivity_spec_sha256")
    if (
        not isinstance(campaign_spec_sha, str)
        or not SHA256_RE.fullmatch(campaign_spec_sha)
    ):
        raise ValueError("Gate-B campaign lacks the canonical pTHat spec SHA-256")
    if spec_sha256 is not None and campaign_spec_sha != spec_sha256:
        raise ValueError("Gate-B campaign pTHat spec SHA-256 differs from input")
    if campaign.get("repository_dirty_at_generation") is not False:
        raise ValueError("Gate-B campaign was not generated from a clean checkout")
    repository_commit = campaign.get("repository_commit")
    legacy_commit = campaign.get("repository_implementation_commit")
    if (
        not isinstance(repository_commit, str)
        or not GIT_COMMIT_RE.fullmatch(repository_commit)
        or legacy_commit != repository_commit
    ):
        raise ValueError("Gate-B campaign repository commit is invalid/inconsistent")
    campaign_ordinal = campaign.get("campaign_ordinal")
    if (
        isinstance(campaign_ordinal, bool)
        or not isinstance(campaign_ordinal, int)
        or not 1 <= campaign_ordinal <= 65_535
    ):
        raise ValueError("Gate-B campaign ordinal is invalid")
    expected_count = len(contract["tunes"]) * len(
        contract["threshold_profiles"]
    )
    if contract["require_exact_nine_rows"] and (
        expected_count != 9 or len(rows) != 9
    ):
        raise ValueError("Gate-B pTHat decision requires exactly nine rows")
    profiles = {
        (profile["pthat_min"], int(profile["logical_id"])): profile
        for profile in contract["threshold_profiles"]
    }
    expected = {
        (tune, threshold): profile
        for tune in contract["tunes"]
        for (threshold, _), profile in profiles.items()
    }
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    seeds: set[int] = set()
    stable_names: set[tuple[str, str]] = set()
    for row in rows:
        tune = row.get("tune")
        threshold = str(row.get("pthat_min_override"))
        logical_id = int(row.get("logical_id", -1))
        profile = profiles.get((threshold, logical_id))
        identity = (tune, threshold)
        if tune not in contract["tunes"] or profile is None:
            raise ValueError(f"unexpected Gate-B row {identity}/{logical_id}")
        if identity in selected:
            raise ValueError(f"duplicate Gate-B threshold identity {identity}")
        exact = {
            "purpose": profile["purpose"],
            "requested_successes": int(profile["requested_successes"]),
            "campaign_ordinal": campaign_ordinal,
            "role": "pilot",
            "attempt": 0,
            "multiplicity_audit_events": 100,
            "repository_commit": repository_commit,
            "stable_name": f"hf_{tune}_job{logical_id:03d}.root",
        }
        for key, value in exact.items():
            if row.get(key) != value:
                raise ValueError(
                    f"Gate-B row {identity} has {key}={row.get(key)!r}, "
                    f"expected {value!r}"
                )
        if row.get("campaign") != campaign.get("campaign"):
            raise ValueError(f"campaign identity mismatch for {identity}")
        seed = int(row.get("seed", -1))
        if seed <= 0 or seed in seeds:
            raise ValueError("Gate-B threshold samples do not have unique seeds")
        seeds.add(seed)
        effective_card_sha = row.get("effective_card_sha256")
        if (
            not isinstance(effective_card_sha, str)
            or not SHA256_RE.fullmatch(effective_card_sha)
        ):
            raise ValueError(f"invalid effective-card SHA-256 for {identity}")
        stable_name = str(row.get("stable_name", ""))
        if (
            not stable_name.endswith(".root")
            or (tune, stable_name) in stable_names
        ):
            raise ValueError(f"invalid/duplicate stable name for {identity}")
        stable_names.add((tune, stable_name))
        selected[identity] = row
    if set(selected) != set(expected):
        raise ValueError(
            f"incomplete threshold/tune coverage: "
            f"missing={sorted(set(expected) - set(selected))}"
        )
    if contract["require_unique_seeds"] and len(seeds) != 9:
        raise ValueError("nine independent manifest seeds are required")
    if checkout is not None:
        species = checkout / raw["species_registry"]
        pairs = checkout / raw["pair_registry"]
        canonical_spec = checkout / "config/pthat_sensitivity_v1.json"
        tune_allowlist = checkout / "config/tune_difference_allowlist_v1.json"
        if sha256(species) != campaign.get("species_registry_sha256"):
            raise ValueError("campaign species registry differs from checkout")
        if sha256(pairs) != campaign.get("pair_registry_sha256"):
            raise ValueError("campaign pair registry differs from checkout")
        if sha256(canonical_spec) != campaign_spec_sha:
            raise ValueError("campaign pTHat spec differs from canonical checkout")
        if sha256(tune_allowlist) != campaign.get("tune_allowlist_sha256"):
            raise ValueError("campaign tune allowlist differs from checkout")
        for tune in contract["tunes"]:
            card = (
                checkout
                / "generation" / "cards"
                / f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
            )
            if sha256(card) != campaign.get("card_sha256", {}).get(tune):
                raise ValueError(f"campaign base card differs for {tune}")
    return selected


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    if (
        not math.isfinite(numerator)
        or not math.isfinite(denominator)
        or denominator == 0.0
    ):
        return None
    result = numerator / denominator
    return result if math.isfinite(result) else None


def derive_block_observables(
    block: dict[str, Any], spec: dict[str, Any]
) -> tuple[dict[str, float], list[str], list[str]]:
    """Derive all nonlinear quantities inside one block.

    Returns (flat observables, technical errors, precision/sparsity issues).
    """

    technical: list[str] = []
    incomplete: list[str] = []
    observables: dict[str, float] = {}
    decision = spec["decision"]
    try:
        sumw = require_finite(block.get("event_weight_sum"), "event_weight_sum")
        sumw2 = require_finite(
            block.get("event_weight_sum2"), "event_weight_sum2"
        )
    except ValueError as error:
        return {}, [str(error)], []
    if sumw <= 0.0 or sumw2 <= 0.0:
        return {}, ["nonpositive block event-weight exposure"], []
    effective = sumw * sumw / sumw2
    if effective < float(decision["minimum_effective_events_per_block"]):
        incomplete.append(
            f"effective events {effective:.6g} below "
            f"{decision['minimum_effective_events_per_block']}"
        )

    diagnostics = block.get("technical_diagnostics", {})
    for key in (
        "multiplicity_out_of_range",
        "trigger_pt_out_of_range",
        "same_hard_pairs",
    ):
        value = int(diagnostics.get(key, 0))
        if value != 0:
            technical.append(f"{key}={value}")

    multiplicity = block.get("multiplicity", {})
    try:
        weighted_nch = require_finite(
            multiplicity.get("weighted_sum"), "multiplicity weighted_sum"
        )
        mean_nch = weighted_nch / sumw
        if mean_nch <= 0.0:
            incomplete.append("multiplicity mean is nonpositive")
        else:
            observables["multiplicity_mean"] = mean_nch
        mult_weights = [
            require_finite(value, "multiplicity bin weight")
            for value in multiplicity.get("bin_weight_sums", [])
        ]
    except ValueError as error:
        technical.append(str(error))
        mult_weights = []
    if len(mult_weights) != len(spec["multiplicity_bins"]) - 1:
        technical.append("multiplicity shape bin count differs from spec")
    else:
        closure = sum(mult_weights)
        if not math.isclose(closure, sumw, rel_tol=1e-9, abs_tol=1e-8):
            technical.append(
                f"multiplicity weighted-bin closure {closure} != {sumw}"
            )
        for index, weight in enumerate(mult_weights):
            fraction = _safe_ratio(weight, sumw)
            name = f"multiplicity_shape:{index}"
            if fraction is None or fraction <= 0.0:
                incomplete.append(f"{name} has a zero/invalid denominator")
            else:
                observables[name] = fraction

    triggers = block.get("triggers", {})
    for group in spec["trigger_groups"]:
        name = group["name"]
        values = triggers.get(name)
        if not isinstance(values, dict):
            technical.append(f"missing trigger group {name}")
            continue
        count = int(values.get("unweighted_count", 0))
        try:
            trigger_weight = require_finite(
                values.get("weight_sum"), f"{name} trigger weight"
            )
            pt_weights = [
                require_finite(value, f"{name} trigger pT-bin weight")
                for value in values.get("pt_bin_weight_sums", [])
            ]
        except ValueError as error:
            technical.append(str(error))
            continue
        if (
            count < int(decision["minimum_unweighted_triggers_per_block"])
            or trigger_weight <= 0.0
        ):
            incomplete.append(
                f"{name} trigger denominator is sparse "
                f"(count={count}, weight={trigger_weight})"
            )
        trigger_rate = _safe_ratio(trigger_weight, sumw)
        rate_name = f"trigger_rate_per_generated_event:{name}"
        if trigger_rate is None or trigger_rate <= 0.0:
            incomplete.append(f"{rate_name} is zero/invalid")
        else:
            observables[rate_name] = trigger_rate
        if len(pt_weights) != len(spec["trigger_pt_bins_gev"]) - 1:
            technical.append(f"{name} trigger pT shape differs from spec")
        else:
            closure = sum(pt_weights)
            if not math.isclose(
                closure, trigger_weight, rel_tol=1e-9, abs_tol=1e-8
            ):
                technical.append(
                    f"{name} trigger pT weighted closure "
                    f"{closure} != {trigger_weight}"
                )
            for index, weight in enumerate(pt_weights):
                fraction = _safe_ratio(weight, trigger_weight)
                observable = f"trigger_pt_shape:{name}:{index}"
                if fraction is None or fraction <= 0.0:
                    incomplete.append(f"{observable} is sparse/zero")
                else:
                    observables[observable] = fraction

    yield_values: dict[str, float] = {}
    yields = block.get("yields", {})
    for definition in spec["yield_groups"]:
        name = definition["name"]
        values = yields.get(name)
        if not isinstance(values, dict):
            technical.append(f"missing yield group {name}")
            continue
        if values.get("same_sign_pair_factor") != 1.0:
            technical.append(f"{name} does not use central SS factor 1.0")
        if (
            values.get("pair_combinatorics_mode")
            != "ordered_conditional_v1"
        ):
            technical.append(
                f"{name} does not use ordered_conditional_v1 pairs"
            )
        trigger_count = int(values.get("trigger_count", 0))
        pair_count = int(values.get("os_pair_count", 0)) + int(
            values.get("ss_pair_count", 0)
        )
        try:
            trigger_weight = require_finite(
                values.get("trigger_weight"), f"{name} trigger weight"
            )
            os_weight = require_finite(
                values.get("os_pair_weight"), f"{name} OS weight"
            )
            ss_weight = require_finite(
                values.get("ss_pair_weight"), f"{name} SS weight"
            )
        except ValueError as error:
            technical.append(str(error))
            continue
        if trigger_count < int(decision["minimum_unweighted_triggers_per_block"]):
            incomplete.append(f"{name} trigger denominator is sparse")
        if pair_count < int(decision["minimum_unweighted_pairs_per_block"]):
            incomplete.append(f"{name} pair numerator is sparse ({pair_count})")
        os_value = _safe_ratio(os_weight, trigger_weight)
        if os_value is None or os_value <= 0.0:
            incomplete.append(
                f"{name} OS-per-trigger yield is zero/nonpositive or invalid"
            )
        else:
            observables[f"os_yield:{name}"] = os_value
        ss_value = _safe_ratio(
            float(spec["selection"]["same_sign_pair_factor"]) * ss_weight,
            trigger_weight,
        )
        if ss_value is None or ss_value <= 0.0:
            incomplete.append(
                f"{name} SS-per-trigger yield is zero/nonpositive or invalid"
            )
        else:
            observables[f"ss_yield:{name}"] = ss_value
        value = _safe_ratio(os_weight - ss_weight, trigger_weight)
        if value is None or value <= 0.0:
            incomplete.append(
                f"{name} balancing yield has zero/nonpositive denominator or value"
            )
        else:
            yield_values[name] = value
            observables[f"balancing_yield:{name}"] = value

    for definition in spec["baryon_meson_ratios"]:
        name = definition["name"]
        numerator = yield_values.get(definition["numerator_yield"])
        denominator = yield_values.get(definition["denominator_yield"])
        if numerator is None or denominator is None:
            incomplete.append(f"{name} lacks a finite within-block yield")
            continue
        value = _safe_ratio(numerator, denominator)
        if value is None or value <= 0.0:
            incomplete.append(f"{name} has a zero/nonpositive denominator")
        else:
            observables[f"baryon_meson_ratio:{name}"] = value

    return observables, technical, incomplete


def observable_kind(name: str) -> str:
    if name == "multiplicity_mean":
        return "multiplicity_mean"
    prefix = name.split(":", 1)[0]
    mapping = {
        "multiplicity_shape": "multiplicity_shape",
        "trigger_rate_per_generated_event": (
            "trigger_rate_per_generated_event"
        ),
        "trigger_pt_shape": "trigger_pt_shape",
        "os_yield": "os_yield",
        "ss_yield": "ss_yield",
        "balancing_yield": "balancing_yield",
        "baryon_meson_ratio": "baryon_meson_ratio",
    }
    if prefix not in mapping:
        raise ValueError(f"unknown decision observable {name}")
    return mapping[prefix]


def _sample_variance(values: list[float]) -> float:
    return statistics.variance(values) if len(values) > 1 else math.nan


def compare_observable(
    alternate: list[float],
    reference: list[float],
    critical_value: float,
    margin: float,
) -> dict[str, Any]:
    if (
        len(alternate) < 2
        or len(reference) < 2
        or any(not math.isfinite(value) or value <= 0.0 for value in alternate)
        or any(not math.isfinite(value) or value <= 0.0 for value in reference)
    ):
        return {"status": "INCONCLUSIVE", "reason": "nonpositive/incomplete blocks"}
    alternate_mean = statistics.fmean(alternate)
    reference_mean = statistics.fmean(reference)
    alternate_variance = _sample_variance(alternate)
    reference_variance = _sample_variance(reference)
    if (
        not math.isfinite(alternate_variance)
        or not math.isfinite(reference_variance)
    ):
        return {"status": "INCONCLUSIVE", "reason": "undefined block variance"}
    log_ratio = math.log(alternate_mean / reference_mean)
    standard_error = math.sqrt(
        alternate_variance
        / (len(alternate) * alternate_mean * alternate_mean)
        + reference_variance
        / (len(reference) * reference_mean * reference_mean)
    )
    lower = log_ratio - critical_value * standard_error
    upper = log_ratio + critical_value * standard_error
    if lower > margin or upper < -margin:
        status = "MATERIAL_SHIFT"
    elif lower > 0.0 or upper < 0.0:
        # Report a resolved nonzero shift even when it falls within the precision target.
        status = "RESOLVED_SHIFT"
    elif lower >= -margin and upper <= margin:
        status = "EQUIVALENT_NO_RESOLVED_SHIFT"
    else:
        status = "INCONCLUSIVE"
    return {
        "status": status,
        "alternate_mean": alternate_mean,
        "reference_mean": reference_mean,
        "log_ratio": log_ratio,
        "standard_error": standard_error,
        "simultaneous_ci_low": lower,
        "simultaneous_ci_high": upper,
        "margin_abs_log_ratio": margin,
        "alternate_blocks": len(alternate),
        "reference_blocks": len(reference),
    }


def _sum_nested_maps(
    blocks: list[dict[str, Any]], key: str
) -> dict[str, float]:
    total: dict[str, float] = {}
    for block in blocks:
        values = block.get(key, {})
        for code, value in values.items():
            total[str(code)] = total.get(str(code), 0.0) + float(value)
    return total


def _sum_origin_maps(
    blocks: list[dict[str, Any]], key: str
) -> dict[str, dict[str, float]]:
    total: dict[str, dict[str, float]] = {}
    for block in blocks:
        sectors = block.get(key, {})
        for sector, categories in sectors.items():
            destination = total.setdefault(str(sector), {})
            for category, value in categories.items():
                label = str(category)
                destination[label] = destination.get(label, 0.0) + float(value)
    return total


def validate_extraction(
    spec: dict[str, Any],
    campaign: dict[str, Any],
    row: dict[str, Any],
    extraction: dict[str, Any],
) -> tuple[
    dict[str, list[float]],
    list[str],
    list[str],
    list[str],
    dict[str, Any],
]:
    identity = (row["tune"], str(row["pthat_min_override"]))
    technical: list[str] = []
    incomplete: list[str] = []
    review: list[str] = []
    if extraction.get("schema") != EXTRACT_SCHEMA:
        return {}, ["missing/wrong extraction schema"], [], [], {}
    if extraction.get("spec_schema") != SPEC_SCHEMA:
        technical.append("missing/wrong frozen spec schema in extraction")
    expected_identity = {
        "campaign": campaign["campaign"],
        "tune": identity[0],
        "logical_id": int(row["logical_id"]),
        "attempt": 0,
        "seed": int(row["seed"]),
        "pthat_min": identity[1],
        "input_file": f"raw/{identity[0]}/{row['stable_name']}",
    }
    actual_identity = extraction.get("identity", {})
    for key, value in expected_identity.items():
        if actual_identity.get(key) != value:
            technical.append(
                f"{identity} extraction identity {key}="
                f"{actual_identity.get(key)!r}, expected {value!r}"
            )
    for key in ("raw_schema", "selector", "origin_algorithm"):
        if extraction.get("raw_contract", {}).get(key) != spec[
            "raw_contract"
        ][key]:
            technical.append(f"{identity} extraction {key} mismatch")
    if extraction.get("raw_contract", {}).get(
        "species_registry_sha256"
    ) != campaign.get("species_registry_sha256"):
        technical.append(f"{identity} species registry checksum mismatch")
    production_provenance = extraction.get("production_provenance", {})
    expected_production_provenance = {
        "campaign_ordinal": int(campaign["campaign_ordinal"]),
        "role": row["role"],
        "config_sha256": row["effective_card_sha256"],
        "repository_commit": row["repository_commit"],
        "repository_dirty": "false",
        "tune_difference_allowlist_schema": (
            "pythia_tune_difference_allowlist_v2"
        ),
        "tune_difference_allowlist_sha256": campaign[
            "tune_allowlist_sha256"
        ],
    }
    for key, value in expected_production_provenance.items():
        if production_provenance.get(key) != value:
            technical.append(
                f"{identity} production provenance {key}="
                f"{production_provenance.get(key)!r}, expected {value!r}"
            )
    executable_sha = production_provenance.get("executable_sha256")
    if (
        not isinstance(executable_sha, str)
        or not SHA256_RE.fullmatch(executable_sha)
    ):
        technical.append(f"{identity} producer executable SHA-256 is invalid")

    input_provenance = extraction.get("input_provenance", {})
    raw_sha = input_provenance.get("sha256")
    expected_manifest_path = f"raw/{identity[0]}/{row['stable_name']}"
    expected_manifest_digest = json_digest(row)
    for key, value in {
        "manifest_relative_path": expected_manifest_path,
        "checksum_sidecar": f"{expected_manifest_path}.sha256",
        "spec_sha256": campaign["pthat_sensitivity_spec_sha256"],
        "manifest_row_sha256": expected_manifest_digest,
        "tune_allowlist_sha256": campaign["tune_allowlist_sha256"],
    }.items():
        if input_provenance.get(key) != value:
            technical.append(
                f"{identity} input provenance {key} mismatch"
            )
    if (
        not isinstance(raw_sha, str)
        or not SHA256_RE.fullmatch(raw_sha)
        or isinstance(input_provenance.get("bytes"), bool)
        or not isinstance(input_provenance.get("bytes"), int)
        or input_provenance.get("bytes", 0) <= 0
    ):
        technical.append(f"{identity} raw input SHA/size provenance is invalid")

    submission = input_provenance.get("submission_claim", {})
    expected_submission_path = (
        "submission_receipts/gate_b_attempt0_submission_claim.json"
    )
    for key, value in {
        "path": expected_submission_path,
        "schema": "hf_gate_b_submission_claim_v1",
        "state": "claimed_before_condor_submit",
        "submission_kind": "gate_b",
        "campaign": campaign["campaign"],
        "campaign_ordinal": int(campaign["campaign_ordinal"]),
        "repository_commit": campaign["repository_commit"],
        "producer_executable_sha256": executable_sha,
        "campaign_json_sha256": input_provenance.get(
            "campaign_json_sha256"
        ),
        "candidate_manifest_sha256": input_provenance.get(
            "candidate_manifest_sha256"
        ),
    }.items():
        if submission.get(key) != value:
            technical.append(f"{identity} submission claim {key} mismatch")
    if (
        not isinstance(submission.get("sha256"), str)
        or not SHA256_RE.fullmatch(submission["sha256"])
    ):
        technical.append(f"{identity} submission claim SHA-256 is invalid")
    for key in ("campaign_json_sha256", "candidate_manifest_sha256"):
        value = input_provenance.get(key)
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
            technical.append(f"{identity} input provenance {key} is invalid")

    attempt_claim = input_provenance.get("attempt_start_claim", {})
    expected_attempt_path = (
        f"attempt_starts/{identity[0]}/job_{int(row['logical_id']):03d}/"
        "attempt_000.json"
    )
    for key, value in {
        "path": expected_attempt_path,
        "schema": "hf_attempt_start_claim_v1",
        "state": "claimed_before_producer_execution",
        "campaign": campaign["campaign"],
        "campaign_ordinal": int(campaign["campaign_ordinal"]),
        "tune": identity[0],
        "logical_id": int(row["logical_id"]),
        "role": row["role"],
        "attempt": 0,
        "seed": int(row["seed"]),
        "requested_successes": int(row["requested_successes"]),
        "repository_commit": row["repository_commit"],
        "effective_card_sha256": row["effective_card_sha256"],
        "producer_executable_sha256": executable_sha,
    }.items():
        if attempt_claim.get(key) != value:
            technical.append(f"{identity} attempt-start claim {key} mismatch")
    attempt_claim_sha = attempt_claim.get("sha256")
    if (
        not isinstance(attempt_claim_sha, str)
        or not SHA256_RE.fullmatch(attempt_claim_sha)
    ):
        technical.append(f"{identity} attempt-start claim SHA-256 is invalid")

    validation_receipt = input_provenance.get(
        "raw_validation_receipt", {}
    )
    expected_receipt_path = (
        f"raw_validation/{identity[0]}/job_{int(row['logical_id']):03d}/"
        "attempt_000/receipt.json"
    )
    for key, value in {
        "path": expected_receipt_path,
        "schema": "hf_raw_validation_receipt_v1",
        "result": "PASS",
        "validator_exit_status": 0,
        "output_sha256": raw_sha,
        "output_bytes": input_provenance.get("bytes"),
    }.items():
        if validation_receipt.get(key) != value:
            technical.append(
                f"{identity} raw-validation receipt {key} mismatch"
            )
    if (
        not isinstance(validation_receipt.get("sha256"), str)
        or not SHA256_RE.fullmatch(validation_receipt["sha256"])
    ):
        technical.append(
            f"{identity} raw-validation receipt SHA-256 is invalid"
        )
    expected_receipt_provenance = {
        "campaign": campaign["campaign"],
        "campaign_ordinal": int(campaign["campaign_ordinal"]),
        "tune": identity[0],
        "logical_id": int(row["logical_id"]),
        "role": row["role"],
        "attempt": 0,
        "seed": int(row["seed"]),
        "requested_successes": int(row["requested_successes"]),
        "phase_space_pthat_min": float(identity[1]),
        "multiplicity_audit_events": int(row["multiplicity_audit_events"]),
        "repository_commit": row["repository_commit"],
        "effective_card_sha256": row["effective_card_sha256"],
        "producer_executable_sha256": executable_sha,
        "attempt_start_claim_sha256": attempt_claim_sha,
        "cluster_id": attempt_claim.get("cluster_id"),
        "process_id": attempt_claim.get("process_id"),
    }
    if validation_receipt.get("expected_provenance") != (
        expected_receipt_provenance
    ):
        technical.append(
            f"{identity} raw-validation expected provenance mismatch"
        )
    for scheduler_key in ("cluster_id", "process_id"):
        value = attempt_claim.get(scheduler_key)
        if (
            not isinstance(value, str)
            or not SAFE_TOKEN_RE.fullmatch(value)
        ):
            technical.append(
                f"{identity} attempt-start {scheduler_key} is invalid"
            )
    if extraction.get("pair_combinatorics") != {
        "mode": "ordered_conditional_v1",
        "same_sign_pair_factor": 1.0,
    }:
        technical.append(
            f"{identity} extraction pair-combinatorics contract mismatch"
        )
    trigger_pt_diagnostic = extraction.get("trigger_pt_diagnostic", {})
    if (
        trigger_pt_diagnostic.get("configured_upper_edge_gev") != 7000.0
        or trigger_pt_diagnostic.get("upper_edge_inclusive_via_nextafter")
        is not True
        or trigger_pt_diagnostic.get("overflow_policy")
        != "report_and_fail_closed_without_excluding_from_integrated_yields"
    ):
        technical.append(
            f"{identity} extraction trigger-pT diagnostic contract mismatch"
        )
    blocks = extraction.get("blocks", [])
    if len(blocks) != spec["blocks"]["count"]:
        return (
            {},
            technical,
            [f"{identity} has {len(blocks)} blocks, expected 10"],
            review,
            {},
        )
    observed_blocks = {int(block.get("block", -1)) for block in blocks}
    if observed_blocks != set(range(10)):
        technical.append(f"{identity} block IDs are not exactly 0..9")

    observables_by_name: dict[str, list[float]] = {}
    event_count = 0
    block_sumw = 0.0
    block_sumw2 = 0.0
    unresolved = 0
    invalid_selected = 0
    negative_weight_events = 0
    zero_weight_events = 0
    minimum_weights: list[float] = []
    maximum_weights: list[float] = []
    for block in sorted(blocks, key=lambda value: int(value.get("block", -1))):
        block_id = int(block.get("block", -1))
        if int(block.get("unweighted_event_count", 0)) <= 0:
            incomplete.append(f"{identity} block {block_id} is empty")
        event_count += int(block.get("unweighted_event_count", 0))
        negative_weight_events += int(block.get("negative_weight_events", 0))
        zero_weight_events += int(block.get("zero_weight_events", 0))
        try:
            block_sumw += require_finite(
                block.get("event_weight_sum"), "block event_weight_sum"
            )
            block_sumw2 += require_finite(
                block.get("event_weight_sum2"), "block event_weight_sum2"
            )
            minimum_weights.append(
                require_finite(
                    block.get("minimum_event_weight"),
                    "minimum_event_weight",
                )
            )
            maximum_weights.append(
                require_finite(
                    block.get("maximum_event_weight"),
                    "maximum_event_weight",
                )
            )
        except ValueError as error:
            technical.append(f"{identity} block {block_id}: {error}")
        derived, block_technical, block_incomplete = derive_block_observables(
            block, spec
        )
        technical.extend(
            f"{identity} block {block_id}: {message}"
            for message in block_technical
        )
        incomplete.extend(
            f"{identity} block {block_id}: {message}"
            for message in block_incomplete
        )
        for name, value in derived.items():
            observables_by_name.setdefault(name, []).append(value)
        for values in block.get("triggers", {}).values():
            unresolved += int(values.get("unresolved_count", 0))
            invalid_selected += int(values.get("invalid_selected_hard_count", 0))
    accounting = extraction.get("event_accounting", {})
    expected_events = int(row["requested_successes"])
    if (
        event_count != expected_events
        or int(accounting.get("successful_events", -1)) != expected_events
        or int(accounting.get("tree_entries", -1)) != expected_events
        or int(accounting.get("unique_event_ids", -1)) != expected_events
    ):
        technical.append(
            f"{identity} event/block/unique-ID accounting does not close"
        )
    normalization = extraction.get("normalization_metadata", {})
    for block_value, metadata_key in (
        (block_sumw, "tree_sum_weights"),
        (block_sumw2, "tree_sum_weights2"),
        (block_sumw, "pythia_weight_sum"),
    ):
        try:
            metadata_value = require_finite(
                normalization.get(metadata_key), metadata_key
            )
            if not math.isclose(
                block_value, metadata_value, rel_tol=1e-9, abs_tol=1e-8
            ):
                technical.append(
                    f"{identity} block closure for {metadata_key} failed"
                )
        except ValueError as error:
            technical.append(f"{identity}: {error}")
    if invalid_selected:
        technical.append(
            f"{identity} has {invalid_selected} selected-hard candidates "
            "with invalid charge/index"
        )
    if (
        unresolved
        and spec["decision"]["unresolved_trigger_candidate_policy"]
        == "scientific_review_if_nonzero"
    ):
        review.append(
            f"{identity} has {unresolved} unresolved publication-trigger "
            "candidates"
        )

    process = _sum_nested_maps(blocks, "process_counts_unweighted")
    expected_codes = {
        str(value) for value in spec["decision"]["expected_process_codes"]
    }
    unexpected_codes = set(process) - expected_codes
    if unexpected_codes:
        technical.append(
            f"{identity} unexpected process codes {sorted(unexpected_codes)}"
        )
    hard_channels = _sum_nested_maps(
        blocks, "hard_channel_counts_unweighted"
    )
    missing_channels = {
        str(value) for value in spec["decision"]["required_hard_channels"]
    } - {code for code, count in hard_channels.items() if count > 0}
    if missing_channels:
        technical.append(
            f"{identity} missing hard channels {sorted(missing_channels)}"
        )

    for name, values in observables_by_name.items():
        if len(values) != spec["blocks"]["minimum_finite_blocks"]:
            incomplete.append(
                f"{identity} observable {name} has {len(values)}/10 "
                "finite positive blocks"
            )
    diagnostics = {
        "identity": {"tune": identity[0], "pthat_min": identity[1]},
        "events": event_count,
        "sum_weights": block_sumw,
        "sum_weights2": block_sumw2,
        "process_counts": process,
        "hard_channel_counts": hard_channels,
        "event_weight_diagnostics": {
            "negative_weight_events": negative_weight_events,
            "zero_weight_events": zero_weight_events,
            "minimum_event_weight": (
                min(minimum_weights) if minimum_weights else None
            ),
            "maximum_event_weight": (
                max(maximum_weights) if maximum_weights else None
            ),
        },
        "unresolved_trigger_candidates": unresolved,
        "invalid_selected_hard_candidates": invalid_selected,
        "associate_origin_counts": _sum_origin_maps(
            blocks, "associate_origin_counts"
        ),
        "associate_origin_weight_sums": _sum_origin_maps(
            blocks, "associate_origin_weight_sums"
        ),
        "origin_rejection_metadata": extraction.get(
            "origin_rejection_metadata", {}
        ),
        "normalization_metadata": normalization,
    }
    return observables_by_name, technical, incomplete, review, diagnostics


def evaluate(
    spec: dict[str, Any],
    campaign: dict[str, Any],
    rows: list[dict[str, Any]],
    extractions: dict[tuple[str, str], dict[str, Any]],
    spec_sha256: str | None = None,
) -> dict[str, Any]:
    validate_spec(spec)
    selected = validate_manifest(
        spec, campaign, rows, spec_sha256=spec_sha256
    )
    technical: list[str] = []
    incomplete: list[str] = []
    review: list[str] = []
    diagnostics: list[dict[str, Any]] = []
    input_provenance_evidence: list[dict[str, Any]] = []
    values: dict[tuple[str, str], dict[str, list[float]]] = {}
    for identity in sorted(selected):
        extraction = extractions.get(identity)
        if extraction is None:
            incomplete.append(f"missing extraction for {identity}")
            continue
        (
            values[identity],
            extraction_technical,
            extraction_incomplete,
            extraction_review,
            extraction_diagnostics,
        ) = validate_extraction(
            spec, campaign, selected[identity], extraction
        )
        technical.extend(extraction_technical)
        incomplete.extend(extraction_incomplete)
        review.extend(extraction_review)
        diagnostics.append(extraction_diagnostics)
        input_provenance_evidence.append(
            {
                "identity": {
                    "tune": identity[0],
                    "pthat_min": identity[1],
                },
                **extraction.get("input_provenance", {}),
                "production_provenance": extraction.get(
                    "production_provenance", {}
                ),
            }
        )

    sigma_checks: list[dict[str, Any]] = []
    sigma_order = spec["decision"]["sigma_nested_order"]
    sigma_tolerance = float(
        spec["decision"]["sigma_nested_tolerance_standard_errors"]
    )
    diagnostics_by_identity = {
        (
            row.get("identity", {}).get("tune"),
            row.get("identity", {}).get("pthat_min"),
        ): row
        for row in diagnostics
    }
    for tune in spec["manifest_contract"]["tunes"]:
        for lower_threshold, upper_threshold in zip(
            sigma_order, sigma_order[1:]
        ):
            lower = diagnostics_by_identity.get((tune, lower_threshold), {})
            upper = diagnostics_by_identity.get((tune, upper_threshold), {})
            try:
                lower_sigma = require_finite(
                    lower["normalization_metadata"]["pythia_sigma_gen_mb"],
                    "lower sigma",
                )
                upper_sigma = require_finite(
                    upper["normalization_metadata"]["pythia_sigma_gen_mb"],
                    "upper sigma",
                )
                lower_error = require_finite(
                    lower["normalization_metadata"]["pythia_sigma_err_mb"],
                    "lower sigma error",
                )
                upper_error = require_finite(
                    upper["normalization_metadata"]["pythia_sigma_err_mb"],
                    "upper sigma error",
                )
                combined_error = math.hypot(lower_error, upper_error)
                excess = upper_sigma - lower_sigma
                passed = excess <= sigma_tolerance * combined_error
                sigma_checks.append(
                    {
                        "tune": tune,
                        "lower_threshold": lower_threshold,
                        "upper_threshold": upper_threshold,
                        "lower_sigma_gen_mb": lower_sigma,
                        "upper_sigma_gen_mb": upper_sigma,
                        "combined_sigma_error_mb": combined_error,
                        "tolerance_standard_errors": sigma_tolerance,
                        "passed": passed,
                    }
                )
                if not passed:
                    technical.append(
                        f"{tune} structured sigma nesting failed for "
                        f"{lower_threshold} -> {upper_threshold}"
                    )
            except (KeyError, ValueError) as error:
                technical.append(
                    f"{tune} structured sigma metadata incomplete: {error}"
                )

    comparison_plan: list[tuple[str, str, str, str]] = []
    predeclared_observables = expected_observable_names(spec)
    for tune in spec["manifest_contract"]["tunes"]:
        for alternate, reference in spec["manifest_contract"]["comparisons"]:
            for observable in predeclared_observables:
                comparison_plan.append(
                    (tune, alternate, reference, observable)
                )
    comparisons: list[dict[str, Any]] = []
    if comparison_plan:
        alpha = float(spec["decision"]["familywise_alpha"])
        declared_family = int(
            spec["decision"]["predeclared_family_comparisons"]
        )
        if len(comparison_plan) != declared_family:
            technical.append(
                f"comparison family {len(comparison_plan)} != "
                f"predeclared {declared_family}"
            )
        adjusted_alpha = alpha / declared_family
        critical_value = float(
            spec["decision"]["bonferroni_critical_value"]
        )
        margins = spec["decision"]["margins_max_abs_log_ratio"]
        for tune, alternate, reference, observable in comparison_plan:
            kind = observable_kind(observable)
            result = compare_observable(
                values.get((tune, alternate), {}).get(observable, []),
                values.get((tune, reference), {}).get(observable, []),
                critical_value,
                float(margins[kind]),
            )
            result.update(
                {
                    "tune": tune,
                    "alternate_threshold": alternate,
                    "reference_threshold": reference,
                    "observable": observable,
                    "kind": kind,
                    "family_comparisons": declared_family,
                    "familywise_alpha": alpha,
                    "per_comparison_alpha": adjusted_alpha,
                    "critical_student_t": critical_value,
                    "conservative_degrees_of_freedom": int(
                        spec["decision"][
                            "conservative_degrees_of_freedom"
                        ]
                    ),
                }
            )
            comparisons.append(result)
            if result["status"] in {"MATERIAL_SHIFT", "RESOLVED_SHIFT"}:
                review.append(
                    f"{tune} {alternate}/{reference} {observable} "
                    + (
                        "is outside its predeclared precision target"
                        if result["status"] == "MATERIAL_SHIFT"
                        else "has a simultaneous interval excluding zero"
                    )
                )
            elif result["status"] == "INCONCLUSIVE":
                incomplete.append(
                    f"{tune} {alternate}/{reference} {observable} "
                    "does not establish equivalence"
                )
    else:
        incomplete.append("no complete pTHat observable comparisons")

    if technical:
        outcome = "TECHNICAL_FAIL"
    elif review:
        outcome = "SCIENTIFIC_REVIEW_REQUIRED"
    elif incomplete:
        outcome = "INCONCLUSIVE"
    else:
        outcome = "PASS"
    return {
        "schema": REPORT_SCHEMA,
        "campaign": campaign["campaign"],
        "campaign_ordinal": int(campaign["campaign_ordinal"]),
        "repository_commit": campaign["repository_commit"],
        "outcome": outcome,
        "decision_precedence": [
            "TECHNICAL_FAIL",
            "SCIENTIFIC_REVIEW_REQUIRED",
            "INCONCLUSIVE",
            "PASS",
        ],
        "statistical_contract": {
            "threshold_samples": "independent manifest seeds",
            "blocks": "event_id modulo 10",
            "block_estimator": (
                "OS-per-trigger, SS-per-trigger, OS-minus-SS yields, and "
                "baryon/meson ratios formed within block"
            ),
            "kinematic_selection": (
                "trigger pT>1 GeV, associate pT>0.15 GeV, |eta|<=4; "
                "no upper-pT selection"
            ),
            "trigger_pt_diagnostic_overflow": (
                "reported/fail-closed and never removed from integrated yields"
            ),
            "comparison": "independent-sample log ratio of block means",
            "family_adjustment": (
                "Bonferroni simultaneous two-sided Student-t confidence "
                "intervals with conservative df=9"
            ),
            "event_counts_are_cross_sections": False,
        },
        "technical_failures": sorted(set(technical)),
        "scientific_review_findings": sorted(set(review)),
        "inconclusive_findings": sorted(set(incomplete)),
        "sigma_nested_closure": sigma_checks,
        "input_provenance_evidence": input_provenance_evidence,
        "diagnostics": diagnostics,
        "comparisons": comparisons,
    }


def render_csv(report: dict[str, Any]) -> str:
    columns = [
        "tune",
        "alternate_threshold",
        "reference_threshold",
        "observable",
        "kind",
        "status",
        "alternate_mean",
        "reference_mean",
        "log_ratio",
        "standard_error",
        "simultaneous_ci_low",
        "simultaneous_ci_high",
        "margin_abs_log_ratio",
        "alternate_blocks",
        "reference_blocks",
        "family_comparisons",
        "familywise_alpha",
        "per_comparison_alpha",
        "critical_student_t",
        "conservative_degrees_of_freedom",
        "reason",
    ]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for row in report.get("comparisons", []):
        writer.writerow({key: row.get(key, "") for key in columns})
    return stream.getvalue()


def render_markdown(report: dict[str, Any]) -> str:
    statuses: dict[str, int] = {}
    for row in report.get("comparisons", []):
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1
    lines = [
        "# Gate-B pTHat sensitivity decision",
        "",
        f"**Outcome: {report['outcome']}**",
        "",
        "The result uses the frozen three-threshold manifest, ten disjoint "
        "`event_id % 10` blocks, independent-sample log-ratio comparisons, "
        "and Bonferroni simultaneous Student-t confidence intervals with "
        "conservative nine-block degrees of freedom. Structured "
        "PYTHIA `sigmaGen` metadata is reported separately; event counts are "
        "never interpreted as cross sections.",
        "",
        "## Comparison summary",
        "",
    ]
    if statuses:
        for status in sorted(statuses):
            lines.append(f"- {status}: {statuses[status]}")
    else:
        lines.append("- No complete comparisons.")
    for heading, key in (
        ("Technical failures", "technical_failures"),
        ("Scientific-review findings", "scientific_review_findings"),
        ("Inconclusive findings", "inconclusive_findings"),
    ):
        lines.extend(["", f"## {heading}", ""])
        findings = report.get(key, [])
        if findings:
            lines.extend(f"- {finding}" for finding in findings)
        else:
            lines.append("- None.")
    lines.extend(
        [
            "",
            "## Structured cross-section nesting",
            "",
            "| Tune | Thresholds | sigma low (mb) | sigma high (mb) | Pass |",
            "|---|---:|---:|---:|:---:|",
        ]
    )
    for row in report.get("sigma_nested_closure", []):
        lines.append(
            f"| {row['tune']} | {row['lower_threshold']} -> "
            f"{row['upper_threshold']} | "
            f"{row['lower_sigma_gen_mb']:.12g} | "
            f"{row['upper_sigma_gen_mb']:.12g} | "
            f"{'yes' if row['passed'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            "## Manifest-selected sample diagnostics",
            "",
            "| Tune | pTHatMin | Events | Sum weights | Unresolved trigger "
            "candidates | Duplicate demotions (c/b) | Multi-heavy "
            "rejections (c/b) | Process codes |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("diagnostics", []):
        identity = row.get("identity", {})
        rejection = row.get("origin_rejection_metadata", {})
        process_codes = ",".join(sorted(row.get("process_counts", {})))
        lines.append(
            f"| {identity.get('tune', '')} | "
            f"{identity.get('pthat_min', '')} | "
            f"{row.get('events', '')} | "
            f"{row.get('sum_weights', 0.0):.12g} | "
            f"{row.get('unresolved_trigger_candidates', '')} | "
            f"{rejection.get('duplicate_demotions_charm', '')}/"
            f"{rejection.get('duplicate_demotions_beauty', '')} | "
            f"{rejection.get('multi_heavy_rejections_charm', '')}/"
            f"{rejection.get('multi_heavy_rejections_beauty', '')} | "
            f"{process_codes} |"
        )
    lines.append("")
    return "\n".join(lines)


def _require_regular(path: Path, label: str) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} is absent, non-regular, or a symlink: {path}")
    return path


def _require_exact_fields(
    payload: dict[str, Any],
    expected: dict[str, Any],
    label: str,
) -> None:
    for key, value in expected.items():
        if payload.get(key) != value:
            raise ValueError(
                f"{label} {key}={payload.get(key)!r}, expected {value!r}"
            )


def _load_gate_b_submission_claim(
    campaign_dir: Path,
    production: Path,
    campaign: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    campaign_json = _require_regular(
        campaign_dir / "campaign.json", "Gate-B campaign manifest"
    )
    candidate_manifest = _require_regular(
        campaign_dir / "candidate_manifest.jsonl",
        "Gate-B candidate manifest",
    )
    claim_path = _require_regular(
        production
        / "submission_receipts"
        / "gate_b_attempt0_submission_claim.json",
        "Gate-B submission claim",
    )
    claim = json.loads(claim_path.read_text())
    _require_exact_fields(
        claim,
        {
            "schema": "hf_gate_b_submission_claim_v1",
            "state": "claimed_before_condor_submit",
            "submission_kind": "gate_b",
            "campaign": campaign["campaign"],
            "campaign_ordinal": int(campaign["campaign_ordinal"]),
            "repository_commit": campaign["repository_commit"],
            "campaign_json_sha256": sha256(campaign_json),
            "candidate_manifest_sha256": sha256(candidate_manifest),
        },
        "Gate-B submission claim",
    )
    producer_sha = claim.get("producer_executable_sha256")
    if not isinstance(producer_sha, str) or not SHA256_RE.fullmatch(producer_sha):
        raise ValueError("Gate-B submission claim producer SHA-256 is invalid")
    expected_allocations = [
        {
            "tune": row["tune"],
            "logical_id": int(row["logical_id"]),
            "attempt": int(row["attempt"]),
            "seed": int(row["seed"]),
            "campaign_ordinal": int(row["campaign_ordinal"]),
            "pthat_min_override": str(row["pthat_min_override"]),
            "multiplicity_audit_events": int(
                row["multiplicity_audit_events"]
            ),
            "repository_commit": row["repository_commit"],
            "effective_card_sha256": row["effective_card_sha256"],
        }
        for row in rows
    ]
    if claim.get("allocations") != expected_allocations:
        raise ValueError(
            "Gate-B submission claim does not bind the exact candidate rows"
        )
    return {
        "path": "submission_receipts/gate_b_attempt0_submission_claim.json",
        "sha256": sha256(claim_path),
        "schema": claim["schema"],
        "state": claim["state"],
        "submission_kind": claim["submission_kind"],
        "campaign": claim["campaign"],
        "campaign_ordinal": claim["campaign_ordinal"],
        "repository_commit": claim["repository_commit"],
        "producer_executable_sha256": producer_sha,
        "campaign_json_sha256": claim["campaign_json_sha256"],
        "candidate_manifest_sha256": claim["candidate_manifest_sha256"],
    }


def _load_raw_validation_provenance(
    production: Path,
    campaign: dict[str, Any],
    row: dict[str, Any],
    raw: Path,
    raw_sha: str,
    submission_claim: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    tune = str(row["tune"])
    logical_id = int(row["logical_id"])
    attempt = int(row["attempt"])
    attempt_relative = (
        f"attempt_starts/{tune}/job_{logical_id:03d}/"
        f"attempt_{attempt:03d}.json"
    )
    attempt_path = _require_regular(
        production / attempt_relative, "attempt-start claim"
    )
    attempt_claim = json.loads(attempt_path.read_text())
    expected_attempt = {
        "schema": "hf_attempt_start_claim_v1",
        "state": "claimed_before_producer_execution",
        "campaign": campaign["campaign"],
        "campaign_ordinal": int(campaign["campaign_ordinal"]),
        "tune": tune,
        "logical_id": logical_id,
        "role": row["role"],
        "attempt": attempt,
        "seed": int(row["seed"]),
        "requested_successes": int(row["requested_successes"]),
        "repository_commit": row["repository_commit"],
        "effective_card_sha256": row["effective_card_sha256"],
        "producer_executable_sha256": submission_claim[
            "producer_executable_sha256"
        ],
    }
    _require_exact_fields(attempt_claim, expected_attempt, "attempt-start claim")
    for key in ("cluster_id", "process_id"):
        token = attempt_claim.get(key)
        if not isinstance(token, str) or not SAFE_TOKEN_RE.fullmatch(token):
            raise ValueError(f"attempt-start claim has invalid {key}")
    attempt_sha = sha256(attempt_path)

    receipt_relative = (
        f"raw_validation/{tune}/job_{logical_id:03d}/"
        f"attempt_{attempt:03d}/receipt.json"
    )
    receipt_path = _require_regular(
        production / receipt_relative, "raw-validation receipt"
    )
    receipt = json.loads(receipt_path.read_text())
    expected_receipt_provenance = {
        "campaign": campaign["campaign"],
        "campaign_ordinal": int(campaign["campaign_ordinal"]),
        "tune": tune,
        "logical_id": logical_id,
        "role": row["role"],
        "attempt": attempt,
        "seed": int(row["seed"]),
        "requested_successes": int(row["requested_successes"]),
        "phase_space_pthat_min": float(row["pthat_min_override"]),
        "multiplicity_audit_events": int(row["multiplicity_audit_events"]),
        "repository_commit": row["repository_commit"],
        "effective_card_sha256": row["effective_card_sha256"],
        "producer_executable_sha256": submission_claim[
            "producer_executable_sha256"
        ],
        "attempt_start_claim_sha256": attempt_sha,
        "cluster_id": attempt_claim["cluster_id"],
        "process_id": attempt_claim["process_id"],
    }
    _require_exact_fields(
        receipt,
        {
            "schema": "hf_raw_validation_receipt_v1",
            "result": "PASS",
            "validator_exit_status": 0,
            "output_sha256": raw_sha,
            "output_bytes": raw.stat().st_size,
            "expected_provenance": expected_receipt_provenance,
        },
        "raw-validation receipt",
    )
    for key in (
        "validator_wrapper_sha256",
        "validator_macro_sha256",
        "validation_log_sha256",
    ):
        value = receipt.get(key)
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
            raise ValueError(f"raw-validation receipt has invalid {key}")
    dependencies = receipt.get("validator_dependency_sha256")
    if (
        not isinstance(dependencies, dict)
        or not dependencies
        or any(
            not isinstance(value, str) or not SHA256_RE.fullmatch(value)
            for value in dependencies.values()
        )
    ):
        raise ValueError(
            "raw-validation receipt dependency checksums are invalid"
        )
    log_name = receipt.get("validation_log_name")
    if (
        not isinstance(log_name, str)
        or Path(log_name).name != log_name
        or not log_name
    ):
        raise ValueError("raw-validation receipt log name is unsafe")
    validation_log = _require_regular(
        receipt_path.parent / log_name, "raw-validation log"
    )
    if sha256(validation_log) != receipt["validation_log_sha256"]:
        raise ValueError("raw-validation log differs from PASS receipt")

    return (
        {
            "path": attempt_relative,
            "sha256": attempt_sha,
            **expected_attempt,
            "cluster_id": attempt_claim["cluster_id"],
            "process_id": attempt_claim["process_id"],
        },
        {
            "path": receipt_relative,
            "sha256": sha256(receipt_path),
            "schema": receipt["schema"],
            "result": receipt["result"],
            "validator_exit_status": receipt["validator_exit_status"],
            "output_sha256": receipt["output_sha256"],
            "output_bytes": receipt["output_bytes"],
            "expected_provenance": receipt["expected_provenance"],
        },
    )


def _cpp_string(value: str) -> str:
    """Return a deterministic escaped C++ string literal."""

    return json.dumps(value, ensure_ascii=True)


def _run_root_extractions(
    requests: list[
        tuple[
            tuple[str, str],
            dict[str, Any],
            Path,
            Path,
            dict[str, Any],
        ]
    ],
    spec_path: Path,
    checkout: Path,
    extraction_dir: Path,
) -> None:
    build_dir = extraction_dir / ".aclic"
    build_dir.mkdir(parents=True, exist_ok=True)
    macro = checkout / "Validation/PTHatSensitivity.C"
    runner = extraction_dir / "run_pthat_extractions.C"
    log = extraction_dir / "pthat_extraction_root.log"
    lines = [
        "void run_pthat_extractions() {",
        f"  gSystem->SetBuildDir({_cpp_string(str(build_dir))}, true);",
        "  int failures = 0;",
        (
            "  if (gROOT->ProcessLine("
            + _cpp_string(f".L {macro}+")
            + ") != 0) {"
        ),
        '    std::cerr << "PTHAT_EXTRACTION_COMPILE_FAIL\\\\n";',
        "    gSystem->Exit(90);",
        "  }",
    ]
    for (tune, threshold), row, raw, output, input_provenance in requests:
        producer_sha = input_provenance["submission_claim"][
            "producer_executable_sha256"
        ]
        arguments = [
            _cpp_string(str(raw)),
            _cpp_string(str(spec_path)),
            _cpp_string(str(output)),
            _cpp_string(str(row["campaign"])),
            str(int(row["campaign_ordinal"])),
            _cpp_string(tune),
            str(int(row["logical_id"])),
            _cpp_string(str(row["role"])),
            str(int(row["attempt"])),
            str(int(row["seed"])),
            f"{int(row['requested_successes'])}ULL",
            f"{float(threshold):.17g}",
            _cpp_string(str(row["repository_commit"])),
            _cpp_string(str(row["effective_card_sha256"])),
            _cpp_string(str(producer_sha)),
            _cpp_string(str(input_provenance["tune_allowlist_sha256"])),
        ]
        call = "ExtractPTHatSensitivity(" + ",".join(arguments) + ")"
        lines.extend(
            [
                "  {",
                f"    Long_t code = gROOT->ProcessLine({_cpp_string(call)});",
                "    if (code != 0) ++failures;",
                "  }",
            ]
        )
    lines.extend(
        [
            "  gSystem->Exit(failures == 0 ? 0 : 91);",
            "}",
            "",
        ]
    )
    atomic_write(runner, "\n".join(lines))
    result = subprocess.run(
        ["root", "-l", "-b", "-q", str(runner)],
        check=False,
        text=True,
        capture_output=True,
        cwd=checkout,
    )
    atomic_write(log, result.stdout + result.stderr)
    if result.returncode != 0:
        diagnostic = "\n".join(
            (result.stdout + result.stderr).splitlines()[-40:]
        )
        raise RuntimeError(
            f"ROOT pTHat extraction failed with {result.returncode}:\n"
            f"{diagnostic}"
        )


def extract_all(
    spec_path: Path,
    spec: dict[str, Any],
    campaign: dict[str, Any],
    rows: list[dict[str, Any]],
    selected: dict[tuple[str, str], dict[str, Any]],
    campaign_dir: Path,
    production: Path,
    extraction_dir: Path,
    checkout: Path,
    reuse: bool,
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    if production.name != campaign["campaign"]:
        raise ValueError(
            "production root basename differs from Gate-B campaign identity"
        )
    submission_claim = _load_gate_b_submission_claim(
        campaign_dir, production, campaign, rows
    )
    spec_sha = sha256(spec_path)
    prepared: dict[
        tuple[str, str],
        tuple[dict[str, Any], Path, str, Path, dict[str, Any]],
    ] = {}
    requests: list[
        tuple[
            tuple[str, str],
            dict[str, Any],
            Path,
            Path,
            dict[str, Any],
        ]
    ] = []
    for identity in sorted(selected):
        row = selected[identity]
        tune, threshold = identity
        raw = (
            production
            / "raw"
            / tune
            / str(row["stable_name"])
        )
        _require_regular(raw, "manifest-selected raw file")
        raw_sha = sha256(raw)
        sidecar = Path(f"{raw}.sha256")
        _require_regular(sidecar, "raw checksum sidecar")
        expected_sidecar = f"{raw_sha}  {raw.name}\n"
        if sidecar.read_text() != expected_sidecar:
            raise ValueError(f"raw checksum sidecar mismatch: {raw}")
        attempt_claim, validation_receipt = (
            _load_raw_validation_provenance(
                production,
                campaign,
                row,
                raw,
                raw_sha,
                submission_claim,
            )
        )
        output = extraction_dir / f"{tune}_pthat_{threshold}.json"
        manifest_relative = f"raw/{tune}/{row['stable_name']}"
        input_provenance = {
            "manifest_relative_path": manifest_relative,
            "bytes": raw.stat().st_size,
            "sha256": raw_sha,
            "checksum_sidecar": f"{manifest_relative}.sha256",
            "spec_sha256": spec_sha,
            "manifest_row_sha256": json_digest(row),
            "campaign_json_sha256": sha256(campaign_dir / "campaign.json"),
            "candidate_manifest_sha256": sha256(
                campaign_dir / "candidate_manifest.jsonl"
            ),
            "tune_allowlist_sha256": campaign[
                "tune_allowlist_sha256"
            ],
            "submission_claim": submission_claim,
            "attempt_start_claim": attempt_claim,
            "raw_validation_receipt": validation_receipt,
        }
        prepared[identity] = (
            row,
            raw,
            raw_sha,
            output,
            input_provenance,
        )
        extraction: dict[str, Any] | None = None
        if reuse and output.is_file():
            candidate = json.loads(output.read_text())
            if candidate.get("input_provenance") == input_provenance:
                extraction = candidate
        if extraction is not None:
            result[identity] = extraction
        elif reuse:
            raise ValueError(
                f"reused extraction is absent/stale for {identity}"
            )
        else:
            requests.append(
                (identity, row, raw, output, input_provenance)
            )

    if requests:
        _run_root_extractions(
            requests, spec_path, checkout, extraction_dir
        )

    for identity in sorted(selected):
        if identity in result:
            continue
        row, raw, raw_sha, output, input_provenance = prepared[identity]
        tune, threshold = identity
        if not output.is_file():
            raise RuntimeError(f"raw extraction produced no output for {identity}")
        extraction = json.loads(output.read_text())
        if extraction.get("schema") != EXTRACT_SCHEMA:
            raise ValueError(f"raw extraction schema mismatch for {identity}")
        manifest_relative = f"raw/{tune}/{row['stable_name']}"
        extraction.setdefault("identity", {})["input_file"] = (
            manifest_relative
        )
        extraction["input_provenance"] = input_provenance
        atomic_write(
            output,
            json.dumps(
                extraction,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n",
        )
        result[identity] = extraction
    return result


def _write_failure_report(
    output_dir: Path,
    message: str,
    spec_sha256: str | None = None,
    manifest_sha256: str | None = None,
) -> int:
    report = {
        "schema": REPORT_SCHEMA,
        "campaign": None,
        "campaign_ordinal": None,
        "repository_commit": None,
        "outcome": "TECHNICAL_FAIL",
        "spec_sha256": spec_sha256,
        "manifest_sha256": manifest_sha256,
        "technical_failures": [message],
        "scientific_review_findings": [],
        "inconclusive_findings": [],
        "sigma_nested_closure": [],
        "input_provenance_evidence": [],
        "diagnostics": [],
        "comparisons": [],
    }
    atomic_write(
        output_dir / "pthat_sensitivity_decision.json",
        json.dumps(report, indent=2, sort_keys=True) + "\n",
    )
    atomic_write(
        output_dir / "pthat_sensitivity_comparisons.csv",
        render_csv(report),
    )
    atomic_write(
        output_dir / "pthat_sensitivity_decision.md",
        render_markdown(report),
    )
    return EXIT_CODES["TECHNICAL_FAIL"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Extract the exact nine manifest-selected Gate-B raw-v5 pilots "
            "and apply the frozen pTHat-sensitivity decision."
        ),
        epilog=(
            "Exit codes: 0 PASS, 2 TECHNICAL_FAIL, 3 INCONCLUSIVE, "
            "4 SCIENTIFIC_REVIEW_REQUIRED. Every outcome writes JSON, CSV, "
            "and Markdown reports."
        ),
    )
    parser.add_argument("campaign_dir", type=Path)
    parser.add_argument("production_root", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "config/pthat_sensitivity_v1.json",
    )
    parser.add_argument(
        "--checkout-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--extraction-dir",
        type=Path,
        help="default: OUTPUT_DIR/extractions",
    )
    parser.add_argument(
        "--reuse-extractions",
        action="store_true",
        help="do not run ROOT; require checksum-bound existing extractions",
    )
    args = parser.parse_args()
    campaign_dir = args.campaign_dir.resolve()
    production = args.production_root.resolve()
    output_dir = args.output_dir.resolve()
    checkout = args.checkout_root.resolve()
    spec_path = args.spec.resolve()
    extraction_dir = (
        args.extraction_dir.resolve()
        if args.extraction_dir
        else output_dir / "extractions"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    spec_sha: str | None = None
    manifest_sha: str | None = None
    try:
        canonical_spec_path = (
            checkout / "config/pthat_sensitivity_v1.json"
        ).resolve()
        if spec_path != canonical_spec_path:
            raise ValueError(
                "pTHat decision requires the checkout's canonical frozen spec"
            )
        spec = json.loads(spec_path.read_text())
        spec_sha = sha256(spec_path)
        validate_spec(spec)
        campaign = json.loads((campaign_dir / "campaign.json").read_text())
        expected_campaign_dir = (
            checkout / "campaigns" / str(campaign.get("campaign", ""))
        ).resolve()
        expected_production = (
            checkout / "Production" / str(campaign.get("campaign", ""))
        ).resolve()
        if campaign_dir != expected_campaign_dir:
            raise ValueError(
                "Gate-B campaign directory is not canonical for this checkout"
            )
        if production != expected_production:
            raise ValueError(
                "Gate-B production directory is not canonical for this checkout"
            )
        rows = load_jsonl(campaign_dir / "candidate_manifest.jsonl")
        manifest_sha = json_digest(rows)
        selected = validate_manifest(
            spec, campaign, rows, checkout, spec_sha
        )
        extractions = extract_all(
            spec_path,
            spec,
            campaign,
            rows,
            selected,
            campaign_dir,
            production,
            extraction_dir,
            checkout,
            args.reuse_extractions,
        )
        report = evaluate(
            spec, campaign, rows, extractions, spec_sha256=spec_sha
        )
        report["spec_sha256"] = spec_sha
        report["campaign_sha256"] = sha256(campaign_dir / "campaign.json")
        report["manifest_sha256"] = manifest_sha
        report["extraction_sha256"] = {
            f"{tune}:{threshold}": sha256(
                extraction_dir / f"{tune}_pthat_{threshold}.json"
            )
            for tune, threshold in sorted(extractions)
        }
        atomic_write(
            output_dir / "pthat_sensitivity_decision.json",
            json.dumps(
                report, indent=2, sort_keys=True, allow_nan=False
            )
            + "\n",
        )
        atomic_write(
            output_dir / "pthat_sensitivity_comparisons.csv",
            render_csv(report),
        )
        atomic_write(
            output_dir / "pthat_sensitivity_decision.md",
            render_markdown(report),
        )
        print(
            "PTHAT_SENSITIVITY_DECISION "
            f"outcome={report['outcome']} "
            f"comparisons={len(report['comparisons'])} "
            f"technical={len(report['technical_failures'])} "
            f"review={len(report['scientific_review_findings'])} "
            f"inconclusive={len(report['inconclusive_findings'])}"
        )
        return EXIT_CODES[report["outcome"]]
    except Exception as error:
        print(f"PTHAT_SENSITIVITY_TECHNICAL_FAIL {error}")
        return _write_failure_report(
            output_dir, str(error), spec_sha, manifest_sha
        )


if __name__ == "__main__":
    raise SystemExit(main())
