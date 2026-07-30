#!/usr/bin/env python3
"""Synthetic regression tests for the predeclared pTHat decision."""

from __future__ import annotations

import copy
import json
import math
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import evaluate_pthat_sensitivity as pthat  # noqa: E402


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def manifest_fixture(spec: dict) -> tuple[dict, list[dict]]:
    repository_commit = "c" * 40
    campaign = {
        "schema": spec["manifest_contract"]["schema"],
        "campaign": "HF_GATEB_SYNTHETIC",
        "campaign_ordinal": 2,
        "repository_commit": repository_commit,
        "repository_implementation_commit": repository_commit,
        "repository_dirty_at_generation": False,
        "raw_schema": spec["raw_contract"]["raw_schema"],
        "selector": spec["raw_contract"]["selector"],
        "origin_algorithm": spec["raw_contract"]["origin_algorithm"],
        "pthat_sensitivity_spec_sha256": pthat.sha256(
            ROOT / "config/pthat_sensitivity_v1.json"
        ),
        "species_registry_sha256": "a" * 64,
        "pair_registry_sha256": "b" * 64,
        "tune_allowlist_sha256": "d" * 64,
        "card_sha256": {
            tune: pthat.json_digest({"base_card": tune})
            for tune in spec["manifest_contract"]["tunes"]
        },
    }
    rows = []
    seed = 700_000_000
    for tune in spec["manifest_contract"]["tunes"]:
        for profile in spec["manifest_contract"]["threshold_profiles"]:
            rows.append(
                {
                    "campaign": campaign["campaign"],
                    "campaign_ordinal": campaign["campaign_ordinal"],
                    "tune": tune,
                    "logical_id": profile["logical_id"],
                    "role": "pilot",
                    "attempt": 0,
                    "seed": seed,
                    "requested_successes": profile["requested_successes"],
                    "pthat_min_override": profile["pthat_min"],
                    "purpose": profile["purpose"],
                    "multiplicity_audit_events": 100,
                    "stable_name": (
                        f"hf_{tune}_job{profile['logical_id']:03d}.root"
                    ),
                    "repository_commit": repository_commit,
                    "effective_card_sha256": pthat.json_digest(
                        {
                            "tune": tune,
                            "pthat_min": profile["pthat_min"],
                            "requested_successes": profile[
                                "requested_successes"
                            ],
                        }
                    ),
                }
            )
            seed += 1
    return campaign, rows


def _bin_weights(total: float, fractions: list[float]) -> list[float]:
    assert math.isclose(sum(fractions), 1.0)
    return [total * value for value in fractions]


def make_block(
    spec: dict,
    index: int,
    events: int,
    scale: float = 1.0,
    yield_overrides: dict[str, float] | None = None,
) -> dict:
    yield_overrides = yield_overrides or {}
    # Non-unit weights prove that every shape and normalization is weighted.
    event_weight = 0.8 + 0.04 * index
    sumw = events * event_weight
    sumw2 = events * event_weight * event_weight
    perturbation = (index - 4.5) * 1.0e-5
    multiplicity_fractions = [
        0.20 + perturbation,
        0.25 - perturbation,
        0.25,
        0.20,
        0.10,
    ]
    pt_fractions = [0.30, 0.28, 0.22, 0.14, 0.06]
    triggers = {}
    trigger_count = max(100, events // 20)
    trigger_weight = trigger_count * event_weight
    for group in spec["trigger_groups"]:
        triggers[group["name"]] = {
            "unweighted_count": trigger_count,
            "weight_sum": trigger_weight,
            "pt_bin_counts_unweighted": [
                max(1, round(trigger_count * value)) for value in pt_fractions
            ],
            "pt_bin_weight_sums": _bin_weights(
                trigger_weight, pt_fractions
            ),
            "candidate_count": trigger_count,
            "candidate_weight": trigger_weight,
            "selected_hard_count": trigger_count,
            "selected_hard_weight": trigger_weight,
            "unresolved_count": 0,
            "unresolved_weight": 0.0,
            "resolved_nonselected_count": 0,
            "resolved_nonselected_weight": 0.0,
            "invalid_selected_hard_count": 0,
            "invalid_selected_hard_weight": 0.0,
        }
    base_yields = {
        "charm_mesons": 0.80,
        "charm_baryons": 0.40,
        "beauty_mesons": 0.60,
        "beauty_baryons": 0.24,
    }
    base_yields.update(yield_overrides)
    yields = {}
    for definition in spec["yield_groups"]:
        value = base_yields[definition["name"]] * scale * (
            1.0 + perturbation
        )
        denominator = triggers[definition["trigger_group"]]["weight_sum"]
        ss_weight = 0.20 * denominator
        os_weight = ss_weight + value * denominator
        yields[definition["name"]] = {
            "trigger_count": trigger_count,
            "trigger_weight": denominator,
            "os_pair_count": max(50, trigger_count),
            "ss_pair_count": max(30, trigger_count // 2),
            "os_pair_weight": os_weight,
            "ss_pair_weight": ss_weight,
            "pair_combinatorics_mode": "ordered_conditional_v1",
            "same_sign_pair_factor": 1.0,
            "value": value,
        }
    return {
        "block": index,
        "unweighted_event_count": events,
        "event_weight_sum": sumw,
        "event_weight_sum2": sumw2,
        "negative_weight_events": 0,
        "zero_weight_events": 0,
        "minimum_event_weight": event_weight,
        "maximum_event_weight": event_weight,
        "effective_events": events,
        "process_counts_unweighted": {
            "121": events // 2,
            "123": events - events // 2,
        },
        "process_weight_sums": {
            "121": sumw / 2,
            "123": sumw / 2,
        },
        "hard_channel_counts_unweighted": {
            "4": events // 2,
            "5": events - events // 2,
        },
        "hard_channel_weight_sums": {"4": sumw / 2, "5": sumw / 2},
        "multiplicity": {
            "weighted_sum": sumw * (30.0 * scale) * (1.0 + perturbation),
            "bin_counts_unweighted": [
                max(1, round(events * value))
                for value in multiplicity_fractions
            ],
            "bin_weight_sums": _bin_weights(
                sumw, multiplicity_fractions
            ),
            "out_of_range": 0,
        },
        "triggers": triggers,
        "yields": yields,
        "baryon_meson_ratios": {},
        "associate_origin_counts": {
            "charm": {"1": 100, "3": 20},
            "beauty": {"1": 80, "4": 10},
        },
        "associate_origin_weight_sums": {
            "charm": {"1": 100.0, "3": 20.0},
            "beauty": {"1": 80.0, "4": 10.0},
        },
        "technical_diagnostics": {
            "multiplicity_out_of_range": 0,
            "trigger_pt_out_of_range": 0,
            "same_hard_pairs": 0,
        },
    }


def extraction_fixture(
    spec: dict,
    campaign: dict,
    row: dict,
    scale: float = 1.0,
    yield_overrides: dict[str, float] | None = None,
) -> dict:
    events_per_block = row["requested_successes"] // 10
    blocks = [
        make_block(spec, index, events_per_block, scale, yield_overrides)
        for index in range(10)
    ]
    sumw = sum(block["event_weight_sum"] for block in blocks)
    sumw2 = sum(block["event_weight_sum2"] for block in blocks)
    threshold = row["pthat_min_override"]
    sigma = {"0.5": 10.0, "1.0": 8.0, "2.0": 5.0}[threshold]
    raw_sha = pthat.json_digest(
        {
            "raw": row["stable_name"],
            "seed": row["seed"],
        }
    )
    executable_sha = "6" * 64
    manifest_relative = f"raw/{row['tune']}/{row['stable_name']}"
    attempt_path = (
        f"attempt_starts/{row['tune']}/job_{row['logical_id']:03d}/"
        "attempt_000.json"
    )
    attempt_sha = pthat.json_digest(
        {
            "attempt": attempt_path,
            "seed": row["seed"],
        }
    )
    attempt_claim = {
        "path": attempt_path,
        "sha256": attempt_sha,
        "schema": "hf_attempt_start_claim_v1",
        "state": "claimed_before_producer_execution",
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
        "tune": row["tune"],
        "logical_id": row["logical_id"],
        "role": row["role"],
        "attempt": row["attempt"],
        "seed": row["seed"],
        "requested_successes": row["requested_successes"],
        "repository_commit": row["repository_commit"],
        "effective_card_sha256": row["effective_card_sha256"],
        "producer_executable_sha256": executable_sha,
        "cluster_id": "12345",
        "process_id": str(row["logical_id"]),
    }
    receipt_expected = {
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
        "tune": row["tune"],
        "logical_id": row["logical_id"],
        "role": row["role"],
        "attempt": row["attempt"],
        "seed": row["seed"],
        "requested_successes": row["requested_successes"],
        "phase_space_pthat_min": float(threshold),
        "multiplicity_audit_events": row["multiplicity_audit_events"],
        "repository_commit": row["repository_commit"],
        "effective_card_sha256": row["effective_card_sha256"],
        "producer_executable_sha256": executable_sha,
        "attempt_start_claim_sha256": attempt_sha,
        "cluster_id": attempt_claim["cluster_id"],
        "process_id": attempt_claim["process_id"],
    }
    return {
        "schema": pthat.EXTRACT_SCHEMA,
        "spec_schema": pthat.SPEC_SCHEMA,
        "identity": {
            "campaign": campaign["campaign"],
            "tune": row["tune"],
            "logical_id": row["logical_id"],
            "attempt": row["attempt"],
            "seed": row["seed"],
            "pthat_min": threshold,
            "input_file": (
                f"raw/{row['tune']}/{row['stable_name']}"
            ),
        },
        "raw_contract": {
            "raw_schema": spec["raw_contract"]["raw_schema"],
            "selector": spec["raw_contract"]["selector"],
            "origin_algorithm": spec["raw_contract"]["origin_algorithm"],
            "species_registry_sha256": campaign[
                "species_registry_sha256"
            ],
        },
        "production_provenance": {
            "campaign_ordinal": campaign["campaign_ordinal"],
            "role": row["role"],
            "config_sha256": row["effective_card_sha256"],
            "executable_sha256": executable_sha,
            "repository_commit": row["repository_commit"],
            "repository_dirty": "false",
            "tune_difference_allowlist_schema": (
                "pythia_tune_difference_allowlist_v2"
            ),
            "tune_difference_allowlist_sha256": campaign[
                "tune_allowlist_sha256"
            ],
        },
        "input_provenance": {
            "manifest_relative_path": manifest_relative,
            "bytes": 123456,
            "sha256": raw_sha,
            "checksum_sidecar": f"{manifest_relative}.sha256",
            "spec_sha256": campaign["pthat_sensitivity_spec_sha256"],
            "manifest_row_sha256": pthat.json_digest(row),
            "campaign_json_sha256": "7" * 64,
            "candidate_manifest_sha256": "8" * 64,
            "tune_allowlist_sha256": campaign["tune_allowlist_sha256"],
            "submission_claim": {
                "path": (
                    "submission_receipts/"
                    "gate_b_attempt0_submission_claim.json"
                ),
                "sha256": "9" * 64,
                "schema": "hf_gate_b_submission_claim_v1",
                "state": "claimed_before_condor_submit",
                "submission_kind": "gate_b",
                "campaign": campaign["campaign"],
                "campaign_ordinal": campaign["campaign_ordinal"],
                "repository_commit": row["repository_commit"],
                "producer_executable_sha256": executable_sha,
                "campaign_json_sha256": "7" * 64,
                "candidate_manifest_sha256": "8" * 64,
            },
            "attempt_start_claim": attempt_claim,
            "raw_validation_receipt": {
                "path": (
                    f"raw_validation/{row['tune']}/"
                    f"job_{row['logical_id']:03d}/attempt_000/receipt.json"
                ),
                "sha256": "5" * 64,
                "schema": "hf_raw_validation_receipt_v1",
                "result": "PASS",
                "validator_exit_status": 0,
                "output_sha256": raw_sha,
                "output_bytes": 123456,
                "expected_provenance": receipt_expected,
            },
        },
        "normalization_metadata": {
            "pythia_sigma_gen_mb": sigma,
            "pythia_sigma_err_mb": 0.01,
            "pythia_weight_sum": sumw,
            "tree_sum_weights": sumw,
            "tree_sum_weights2": sumw2,
            "interpretation": (
                "Structured PYTHIA metadata; unweighted event counts "
                "are not cross sections"
            ),
        },
        "origin_rejection_metadata": {
            "duplicate_conflict_groups_charm": 0,
            "duplicate_conflict_groups_beauty": 0,
            "duplicate_demotions_charm": 0,
            "duplicate_demotions_beauty": 0,
            "multi_heavy_rejections_charm": 0,
            "multi_heavy_rejections_beauty": 0,
        },
        "event_accounting": {
            "requested_successes": row["requested_successes"],
            "successful_events": row["requested_successes"],
            "tree_entries": row["requested_successes"],
            "unique_event_ids": row["requested_successes"],
        },
        "block_assignment": {
            "method": "unsigned_event_id_modulo",
            "count": 10,
        },
        "pair_combinatorics": {
            "mode": "ordered_conditional_v1",
            "same_sign_pair_factor": 1.0,
        },
        "trigger_pt_diagnostic": {
            "configured_upper_edge_gev": 7000.0,
            "upper_edge_inclusive_via_nextafter": True,
            "overflow_policy": (
                "report_and_fail_closed_without_excluding_from_integrated_yields"
            ),
        },
        "blocks": blocks,
    }


def all_extractions(spec: dict, campaign: dict, rows: list[dict]) -> dict:
    return {
        (row["tune"], row["pthat_min_override"]): extraction_fixture(
            spec, campaign, row
        )
        for row in rows
    }


def test_identical_pass(spec: dict) -> None:
    campaign, rows = manifest_fixture(spec)
    report = pthat.evaluate(
        spec, campaign, rows, all_extractions(spec, campaign, rows)
    )
    assert report["outcome"] == "PASS", (
        report["technical_failures"],
        report["scientific_review_findings"],
        report["inconclusive_findings"][:3],
    )
    assert report["campaign"] == campaign["campaign"]
    assert report["campaign_ordinal"] == campaign["campaign_ordinal"]
    assert report["repository_commit"] == campaign["repository_commit"]
    assert report["comparisons"]
    assert len(report["comparisons"]) == spec["decision"][
        "predeclared_family_comparisons"
    ]
    assert {row["status"] for row in report["comparisons"]} == {
        "EQUIVALENT_NO_RESOLVED_SHIFT"
    }
    # Successful rendering is byte-deterministic.
    report_again = pthat.evaluate(
        spec, campaign, rows, all_extractions(spec, campaign, rows)
    )
    assert json.dumps(report, sort_keys=True) == json.dumps(
        report_again, sort_keys=True
    )
    assert pthat.render_csv(report) == pthat.render_csv(report_again)
    assert pthat.render_markdown(report) == pthat.render_markdown(report_again)


def test_planted_shift_requires_review(spec: dict) -> None:
    campaign, rows = manifest_fixture(spec)
    extracts = all_extractions(spec, campaign, rows)
    for row in rows:
        if (
            row["tune"] == "MONASH"
            and row["pthat_min_override"] == "0.5"
        ):
            extracts[(row["tune"], row["pthat_min_override"])] = (
                extraction_fixture(spec, campaign, row, scale=1.5)
            )
    report = pthat.evaluate(spec, campaign, rows, extracts)
    assert report["outcome"] == "SCIENTIFIC_REVIEW_REQUIRED"
    assert any(
        row["status"] == "MATERIAL_SHIFT"
        for row in report["comparisons"]
    )


def test_resolved_submargin_shift_still_requires_review(spec: dict) -> None:
    campaign, rows = manifest_fixture(spec)
    extracts = all_extractions(spec, campaign, rows)
    for row in rows:
        if (
            row["tune"] == "MONASH"
            and row["pthat_min_override"] == "0.5"
        ):
            extracts[(row["tune"], row["pthat_min_override"])] = (
                extraction_fixture(
                    spec,
                    campaign,
                    row,
                    yield_overrides={"charm_baryons": 0.42},
                )
            )
    report = pthat.evaluate(spec, campaign, rows, extracts)
    assert report["outcome"] == "SCIENTIFIC_REVIEW_REQUIRED"
    assert any(
        row["status"] == "RESOLVED_SHIFT"
        and row["observable"] == "balancing_yield:charm_baryons"
        for row in report["comparisons"]
    )


def test_equal_os_ss_shift_cannot_cancel_out_of_gate(spec: dict) -> None:
    campaign, rows = manifest_fixture(spec)
    extracts = all_extractions(spec, campaign, rows)
    identity = ("MONASH", "0.5")
    shifted = copy.deepcopy(extracts[identity])
    for block in shifted["blocks"]:
        values = block["yields"]["charm_mesons"]
        common_shift = 0.30 * values["trigger_weight"]
        values["os_pair_weight"] += common_shift
        values["ss_pair_weight"] += common_shift
        # The OS-minus-SS central observable is deliberately unchanged.
    extracts[identity] = shifted
    report = pthat.evaluate(spec, campaign, rows, extracts)
    assert report["outcome"] == "SCIENTIFIC_REVIEW_REQUIRED"
    statuses = {
        row["observable"]: row["status"]
        for row in report["comparisons"]
        if row["tune"] == identity[0]
        and row["alternate_threshold"] == identity[1]
    }
    assert statuses["balancing_yield:charm_mesons"] == (
        "EQUIVALENT_NO_RESOLVED_SHIFT"
    )
    assert statuses["os_yield:charm_mesons"] in {
        "MATERIAL_SHIFT",
        "RESOLVED_SHIFT",
    }
    assert statuses["ss_yield:charm_mesons"] in {
        "MATERIAL_SHIFT",
        "RESOLVED_SHIFT",
    }


def test_sparse_zero_is_inconclusive(spec: dict) -> None:
    campaign, rows = manifest_fixture(spec)
    extracts = all_extractions(spec, campaign, rows)
    identity = ("JUNCTIONS", "2.0")
    sparse = copy.deepcopy(extracts[identity])
    for block in sparse["blocks"]:
        values = block["yields"]["beauty_baryons"]
        values["os_pair_count"] = 0
        values["ss_pair_count"] = 0
        values["os_pair_weight"] = 0.0
        values["ss_pair_weight"] = 0.0
        values["value"] = 0.0
    extracts[identity] = sparse
    report = pthat.evaluate(spec, campaign, rows, extracts)
    assert report["outcome"] == "INCONCLUSIVE"
    assert not report["technical_failures"]
    assert any(
        "beauty_baryons" in finding
        for finding in report["inconclusive_findings"]
    )


def test_contract_defect_is_technical_failure(spec: dict) -> None:
    campaign, rows = manifest_fixture(spec)
    extracts = all_extractions(spec, campaign, rows)
    identity = ("CLOSEPACKING", "0.5")
    broken = copy.deepcopy(extracts[identity])
    broken["blocks"][0]["technical_diagnostics"]["same_hard_pairs"] = 1
    extracts[identity] = broken
    report = pthat.evaluate(spec, campaign, rows, extracts)
    assert report["outcome"] == "TECHNICAL_FAIL"
    assert any(
        "same_hard_pairs=1" in finding
        for finding in report["technical_failures"]
    )


def test_pair_contract_and_true_overflow_fail_closed(spec: dict) -> None:
    campaign, rows = manifest_fixture(spec)
    extracts = all_extractions(spec, campaign, rows)
    identity = ("MONASH", "1.0")
    broken = copy.deepcopy(extracts[identity])
    broken["pair_combinatorics"]["mode"] = "unordered_v0"
    broken["blocks"][0]["yields"]["charm_mesons"][
        "pair_combinatorics_mode"
    ] = "unordered_v0"
    broken["blocks"][1]["technical_diagnostics"][
        "trigger_pt_out_of_range"
    ] = 1
    extracts[identity] = broken
    report = pthat.evaluate(spec, campaign, rows, extracts)
    assert report["outcome"] == "TECHNICAL_FAIL"
    assert any(
        "pair-combinatorics contract mismatch" in finding
        for finding in report["technical_failures"]
    )
    assert any(
        "ordered_conditional_v1" in finding
        for finding in report["technical_failures"]
    )
    assert any(
        "trigger_pt_out_of_range=1" in finding
        for finding in report["technical_failures"]
    )


def test_frozen_pair_and_pt_endpoint_contract(spec: dict) -> None:
    changed_pairs = copy.deepcopy(spec)
    changed_pairs["selection"]["pair_combinatorics_mode"] = "unordered_v0"
    try:
        pthat.validate_spec(changed_pairs)
    except ValueError as error:
        assert "pair_combinatorics_mode" in str(error)
    else:
        raise AssertionError("changed pair-combinatorics mode was accepted")

    changed_pt = copy.deepcopy(spec)
    changed_pt["trigger_pt_bins_gev"][-1] = 50.0
    try:
        pthat.validate_spec(changed_pt)
    except ValueError as error:
        assert "trigger-pT diagnostic binning" in str(error)
    else:
        raise AssertionError("changed pT diagnostic endpoint was accepted")


def test_frozen_simultaneous_decision_values_reject_mutation(
    spec: dict,
) -> None:
    mutations = []
    changed_margin = copy.deepcopy(spec)
    changed_margin["decision"]["margins_max_abs_log_ratio"][
        "os_yield"
    ] += 1.0e-6
    mutations.append(changed_margin)
    changed_family = copy.deepcopy(spec)
    changed_family["decision"]["predeclared_family_comparisons"] = 193
    mutations.append(changed_family)
    changed_critical = copy.deepcopy(spec)
    changed_critical["decision"]["bonferroni_critical_value"] += 1.0e-6
    mutations.append(changed_critical)
    changed_definition = copy.deepcopy(spec)
    changed_definition["decision"][
        "bonferroni_critical_value_definition"
    ] = "post-hoc"
    mutations.append(changed_definition)
    for changed in mutations:
        try:
            pthat.validate_spec(changed)
        except ValueError:
            pass
        else:
            raise AssertionError("mutated frozen pTHat decision was accepted")


def test_provenance_mutations_fail_closed(spec: dict) -> None:
    campaign, rows = manifest_fixture(spec)
    baseline = all_extractions(spec, campaign, rows)
    identity = ("MONASH", "1.0")
    mutations: list[tuple[str, dict]] = []

    dirty = copy.deepcopy(baseline)
    dirty[identity]["production_provenance"]["repository_dirty"] = "true"
    mutations.append(("dirty", dirty))

    wrong_role = copy.deepcopy(baseline)
    wrong_role[identity]["production_provenance"]["role"] = "primary"
    mutations.append(("role", wrong_role))

    wrong_card = copy.deepcopy(baseline)
    wrong_card[identity]["production_provenance"]["config_sha256"] = "0" * 64
    mutations.append(("card", wrong_card))

    wrong_executable = copy.deepcopy(baseline)
    wrong_executable[identity]["production_provenance"][
        "executable_sha256"
    ] = "0" * 64
    mutations.append(("executable", wrong_executable))

    wrong_allowlist = copy.deepcopy(baseline)
    wrong_allowlist[identity]["production_provenance"][
        "tune_difference_allowlist_sha256"
    ] = "0" * 64
    mutations.append(("allowlist", wrong_allowlist))

    wrong_manifest_row = copy.deepcopy(baseline)
    wrong_manifest_row[identity]["input_provenance"][
        "manifest_row_sha256"
    ] = "0" * 64
    mutations.append(("manifest row", wrong_manifest_row))

    wrong_spec = copy.deepcopy(baseline)
    wrong_spec[identity]["input_provenance"]["spec_sha256"] = "0" * 64
    mutations.append(("spec", wrong_spec))

    failed_receipt = copy.deepcopy(baseline)
    failed_receipt[identity]["input_provenance"]["raw_validation_receipt"][
        "result"
    ] = "FAIL"
    mutations.append(("validation result", failed_receipt))

    wrong_raw_sha = copy.deepcopy(baseline)
    wrong_raw_sha[identity]["input_provenance"]["raw_validation_receipt"][
        "output_sha256"
    ] = "0" * 64
    mutations.append(("raw SHA", wrong_raw_sha))

    wrong_receipt_provenance = copy.deepcopy(baseline)
    wrong_receipt_provenance[identity]["input_provenance"][
        "raw_validation_receipt"
    ]["expected_provenance"]["role"] = "primary"
    mutations.append(("receipt provenance", wrong_receipt_provenance))

    wrong_attempt = copy.deepcopy(baseline)
    wrong_attempt[identity]["input_provenance"]["attempt_start_claim"][
        "seed"
    ] += 1
    mutations.append(("attempt-start claim", wrong_attempt))

    for label, extracts in mutations:
        report = pthat.evaluate(spec, campaign, rows, extracts)
        assert report["outcome"] == "TECHNICAL_FAIL", label
        assert report["technical_failures"], label

    changed_campaign = copy.deepcopy(campaign)
    changed_campaign["pthat_sensitivity_spec_sha256"] = "0" * 64
    try:
        pthat.evaluate(
            spec,
            changed_campaign,
            rows,
            baseline,
            spec_sha256=campaign["pthat_sensitivity_spec_sha256"],
        )
    except ValueError as error:
        assert "spec SHA-256" in str(error)
    else:
        raise AssertionError("campaign/spec SHA mutation was accepted")


def test_immutable_file_evidence_is_checked_before_extraction(
    spec: dict,
) -> None:
    campaign, rows = manifest_fixture(spec)
    with tempfile.TemporaryDirectory(
        prefix="pthat_provenance_test_"
    ) as temporary:
        root = Path(temporary)
        campaign_dir = root / "campaigns" / campaign["campaign"]
        production = root / "Production" / campaign["campaign"]
        campaign_path = campaign_dir / "campaign.json"
        candidate_path = campaign_dir / "candidate_manifest.jsonl"
        _write_json(campaign_path, campaign)
        candidate_path.write_text(
            "".join(
                json.dumps(row, sort_keys=True) + "\n" for row in rows
            )
        )
        producer_sha = "6" * 64
        allocations = [
            {
                "tune": row["tune"],
                "logical_id": row["logical_id"],
                "attempt": row["attempt"],
                "seed": row["seed"],
                "campaign_ordinal": row["campaign_ordinal"],
                "pthat_min_override": row["pthat_min_override"],
                "multiplicity_audit_events": row[
                    "multiplicity_audit_events"
                ],
                "repository_commit": row["repository_commit"],
                "effective_card_sha256": row["effective_card_sha256"],
            }
            for row in rows
        ]
        claim_path = (
            production
            / "submission_receipts"
            / "gate_b_attempt0_submission_claim.json"
        )
        claim = {
            "schema": "hf_gate_b_submission_claim_v1",
            "state": "claimed_before_condor_submit",
            "submission_kind": "gate_b",
            "campaign": campaign["campaign"],
            "campaign_ordinal": campaign["campaign_ordinal"],
            "repository_commit": campaign["repository_commit"],
            "producer_executable_sha256": producer_sha,
            "campaign_json_sha256": pthat.sha256(campaign_path),
            "candidate_manifest_sha256": pthat.sha256(candidate_path),
            "allocations": allocations,
        }
        _write_json(claim_path, claim)
        claim_summary = pthat._load_gate_b_submission_claim(
            campaign_dir, production, campaign, rows
        )

        row = rows[0]
        raw = (
            production / "raw" / row["tune"] / row["stable_name"]
        )
        raw.parent.mkdir(parents=True)
        raw.write_bytes(b"synthetic ROOT bytes")
        raw_sha = pthat.sha256(raw)
        attempt_path = (
            production
            / "attempt_starts"
            / row["tune"]
            / f"job_{row['logical_id']:03d}"
            / "attempt_000.json"
        )
        attempt = {
            "schema": "hf_attempt_start_claim_v1",
            "state": "claimed_before_producer_execution",
            "campaign": campaign["campaign"],
            "campaign_ordinal": campaign["campaign_ordinal"],
            "tune": row["tune"],
            "logical_id": row["logical_id"],
            "role": row["role"],
            "attempt": row["attempt"],
            "seed": row["seed"],
            "requested_successes": row["requested_successes"],
            "repository_commit": row["repository_commit"],
            "effective_card_sha256": row["effective_card_sha256"],
            "producer_executable_sha256": producer_sha,
            "cluster_id": "12345",
            "process_id": "0",
        }
        _write_json(attempt_path, attempt)
        validation_dir = (
            production
            / "raw_validation"
            / row["tune"]
            / f"job_{row['logical_id']:03d}"
            / "attempt_000"
        )
        validation_log = validation_dir / "validate_raw_output.log"
        validation_log.parent.mkdir(parents=True)
        validation_log.write_text("RAW_VALIDATION_SUMMARY errors=0\n")
        receipt_path = validation_dir / "receipt.json"
        receipt_provenance = {
            "campaign": campaign["campaign"],
            "campaign_ordinal": campaign["campaign_ordinal"],
            "tune": row["tune"],
            "logical_id": row["logical_id"],
            "role": row["role"],
            "attempt": row["attempt"],
            "seed": row["seed"],
            "requested_successes": row["requested_successes"],
            "phase_space_pthat_min": float(row["pthat_min_override"]),
            "multiplicity_audit_events": row[
                "multiplicity_audit_events"
            ],
            "repository_commit": row["repository_commit"],
            "effective_card_sha256": row["effective_card_sha256"],
            "producer_executable_sha256": producer_sha,
            "attempt_start_claim_sha256": pthat.sha256(attempt_path),
            "cluster_id": attempt["cluster_id"],
            "process_id": attempt["process_id"],
        }
        receipt = {
            "schema": "hf_raw_validation_receipt_v1",
            "result": "PASS",
            "validator_exit_status": 0,
            "validator_wrapper_sha256": "1" * 64,
            "validator_macro_sha256": "2" * 64,
            "validator_dependency_sha256": {"dependency": "3" * 64},
            "validation_log_name": validation_log.name,
            "validation_log_sha256": pthat.sha256(validation_log),
            "output_sha256": raw_sha,
            "output_bytes": raw.stat().st_size,
            "expected_provenance": receipt_provenance,
        }
        _write_json(receipt_path, receipt)
        attempt_summary, receipt_summary = (
            pthat._load_raw_validation_provenance(
                production,
                campaign,
                row,
                raw,
                raw_sha,
                claim_summary,
            )
        )
        assert attempt_summary["sha256"] == pthat.sha256(attempt_path)
        assert receipt_summary["result"] == "PASS"

        failed_receipt = copy.deepcopy(receipt)
        failed_receipt["result"] = "FAIL"
        _write_json(receipt_path, failed_receipt)
        try:
            pthat._load_raw_validation_provenance(
                production,
                campaign,
                row,
                raw,
                raw_sha,
                claim_summary,
            )
        except ValueError as error:
            assert "result" in str(error)
        else:
            raise AssertionError("FAIL raw-validation receipt was accepted")
        _write_json(receipt_path, receipt)

        changed_claim = copy.deepcopy(claim)
        changed_claim["allocations"][0]["seed"] += 1
        _write_json(claim_path, changed_claim)
        try:
            pthat._load_gate_b_submission_claim(
                campaign_dir, production, campaign, rows
            )
        except ValueError as error:
            assert "exact candidate rows" in str(error)
        else:
            raise AssertionError("mutated submission allocation was accepted")


def test_weights_and_within_block_covariance(spec: dict) -> None:
    block = make_block(spec, 0, 1000)
    block["multiplicity"]["weighted_sum"] = (
        37.0 * block["event_weight_sum"]
    )
    observables, technical, incomplete = pthat.derive_block_observables(
        block, spec
    )
    assert not technical
    assert not incomplete
    assert math.isclose(observables["multiplicity_mean"], 37.0)
    assert math.isclose(
        observables["os_yield:charm_mesons"], 1.0, rel_tol=1.0e-4
    )
    assert math.isclose(observables["ss_yield:charm_mesons"], 0.2)
    assert math.isclose(
        sum(
            observables[f"multiplicity_shape:{index}"]
            for index in range(len(spec["multiplicity_bins"]) - 1)
        ),
        1.0,
    )

    ratios = []
    numerator_values = []
    denominator_values = []
    for index in range(10):
        if index < 5:
            overrides = {"charm_baryons": 1.0, "charm_mesons": 1.0}
        else:
            overrides = {"charm_baryons": 9.0, "charm_mesons": 3.0}
        derived, technical, incomplete = pthat.derive_block_observables(
            make_block(spec, index, 1000, yield_overrides=overrides),
            spec,
        )
        assert not technical
        assert not incomplete
        ratios.append(
            derived["baryon_meson_ratio:charm_baryon_over_meson"]
        )
        numerator_values.append(derived["balancing_yield:charm_baryons"])
        denominator_values.append(derived["balancing_yield:charm_mesons"])
    mean_block_ratio = sum(ratios) / len(ratios)
    ratio_of_means = (
        sum(numerator_values) / sum(denominator_values)
    )
    assert math.isclose(mean_block_ratio, 2.0, rel_tol=2e-5)
    assert math.isclose(ratio_of_means, 2.5, rel_tol=2e-5)
    assert not math.isclose(mean_block_ratio, ratio_of_means, rel_tol=0.1)


def main() -> int:
    spec = json.loads(
        (ROOT / "config/pthat_sensitivity_v1.json").read_text()
    )
    try:
        pthat.validate_spec(spec)
    except ValueError as error:
        assert "lacks the required pre-pilot" in str(error)
    else:
        raise AssertionError(
            "pending pTHat scientific-review status was accepted"
        )
    spec["scientific_review_status"] = "APPROVED_GATE_B_OWNER_REVIEW"
    spec["scientific_review"] = {
        "decision": "APPROVE_PTHAT_SENSITIVITY_SPEC",
        "reviewer": "Independent Physics Reviewer",
        "reviewer_role":
            "project_owner_or_designated_physics_statistics_reviewer",
        "decision_utc": "2026-07-30T12:00:00+00:00",
        "rationale":
            "Synthetic approval used only to exercise the frozen decision "
            "mathematics; it is not a project approval artifact.",
    }
    pthat.validate_spec(spec)
    test_identical_pass(spec)
    test_planted_shift_requires_review(spec)
    test_resolved_submargin_shift_still_requires_review(spec)
    test_equal_os_ss_shift_cannot_cancel_out_of_gate(spec)
    test_sparse_zero_is_inconclusive(spec)
    test_contract_defect_is_technical_failure(spec)
    test_pair_contract_and_true_overflow_fail_closed(spec)
    test_frozen_pair_and_pt_endpoint_contract(spec)
    test_frozen_simultaneous_decision_values_reject_mutation(spec)
    test_provenance_mutations_fail_closed(spec)
    test_immutable_file_evidence_is_checked_before_extraction(spec)
    test_weights_and_within_block_covariance(spec)
    print("pTHat-sensitivity tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
