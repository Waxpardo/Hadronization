#!/usr/bin/env python3
"""Focused regression tests for the independent robustness cross-check."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from array import array
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/statistical_robustness.py"
SPEC = importlib.util.spec_from_file_location(
    "statistical_robustness", MODULE_PATH
)
assert SPEC and SPEC.loader
robustness = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = robustness
SPEC.loader.exec_module(robustness)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def build_producer_v2_freeze(directory: Path, jobs_per_tune: int = 110) -> Path:
    campaign = "JB0_PRODUCER_V2_TEST"
    production = directory / "production"
    campaign_root = production / campaign
    commit = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    contracts = json.loads(
        (ROOT / "config/statistical_robustness_v1.json").read_text()
    )["contracts"]
    for tune_ordinal, tune in enumerate(robustness.EXPECTED_TUNES):
        card = (
            ROOT
            / "generation/cards"
            / f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
        )
        for logical_id in range(jobs_per_tune):
            raw = (
                campaign_root
                / "raw"
                / tune
                / f"hf_{tune}_job{logical_id:03d}.root"
            )
            raw.parent.mkdir(parents=True, exist_ok=True)
            raw.write_bytes(f"{campaign}:{tune}:{logical_id}\n".encode())
            raw.with_suffix(".root.sha256").write_text(
                f"{digest(raw)}  {raw.name}\n"
            )
            write_json(
                campaign_root
                / "attempt_metadata"
                / tune
                / f"job{logical_id:03d}.json",
                {
                    "producer_exit": 0,
                    "campaign": campaign,
                    "campaign_ordinal": 991,
                    "tune": tune,
                    "tune_ordinal": tune_ordinal,
                    "logical_id": logical_id,
                    "attempt": 0,
                    "role": "primary",
                    "requested_successes": 17,
                    "seed": tune_ordinal * 100000 + logical_id + 1,
                    "effective_card_sha256": digest(card),
                    "producer_executable_sha256": "7" * 64,
                    "repository_commit": commit,
                    "multiplicity_audit_events": 0,
                    "pthat_min_override": "NONE",
                },
            )
            validation = (
                campaign_root
                / "raw_validation"
                / tune
                / f"job{logical_id:03d}"
                / "attempt000"
            )
            validation.mkdir(parents=True, exist_ok=True)
            log = validation / "validate_raw_output.log"
            log.write_text("RAW_OUTPUT_VALIDATION PASS\n")
            write_json(
                validation / "receipt.json",
                {
                    "schema": "hf_raw_output_validation_receipt_v2",
                    "state": "PASS",
                    "campaign": campaign,
                    "tune": tune,
                    "logical_id": logical_id,
                    "raw_path": raw.relative_to(campaign_root).as_posix(),
                    "raw_sha256": digest(raw),
                    "validation_log_sha256": digest(log),
                    "raw_schema": contracts["raw_schema"],
                },
            )
    freeze = directory / "freeze"
    command = [
        sys.executable,
        str(ROOT / "tools/build_canonical_manifest.py"),
        campaign,
        str(freeze),
        "--production-root",
        str(production),
    ]
    for tune in robustness.EXPECTED_TUNES:
        command.extend(("--tune", tune))
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stdout + completed.stderr)
    return freeze


def rewrite_producer_freeze(
    freeze: Path,
    rows: list[dict],
    seal: dict,
    *,
    rewrite_blocks: bool = True,
) -> None:
    manifest = freeze / "canonical_manifest.jsonl"
    manifest.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )
    seal["canonical_manifest_sha256"] = digest(manifest)
    if rewrite_blocks:
        for block in range(10):
            (freeze / f"block_{block + 1:02d}.jsonl").write_text(
                "".join(
                    json.dumps(row, sort_keys=True) + "\n"
                    for row in rows
                    if row["canonical_slot"] % 10 == block
                )
            )
    write_json(freeze / "freeze_seal.json", seal)


class StatisticalFormulaTest(unittest.TestCase):
    def test_predeclared_config_matches_registries(self) -> None:
        spec = json.loads(
            (ROOT / "config/statistical_robustness_v1.json").read_text()
        )
        lookup = robustness.validate_spec(spec, ROOT)
        self.assertEqual(lookup[(411, -411)]["filename"], "DplusDminus.root")
        self.assertEqual(lookup[(521, 5122)]["heavy_sign"], "OS")
        historical, registry_sha = (
            robustness.load_historical_provenance_entry(ROOT, "HF_RUN3_V1")
        )
        self.assertEqual(
            historical["raw_production"]["repository_commit"],
            "e6429b779d62dba4ec0fb65628470a041ee6a5e9",
        )
        self.assertEqual(
            historical["pair_analysis"]["repository_commit"],
            "61fe978f66c00e8467f88c00d677462292dd5a1c",
        )
        self.assertRegex(registry_sha, r"^[0-9a-f]{64}$")

    def test_nominal_canvases_keep_validated_headroom(self) -> None:
        configuration = json.loads(
            (
                ROOT
                / "plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json"
            ).read_text()
        )
        expected = {
            "mini_beauty_balancing_JUNCTIONS_CLOSEPACKING_over_MONASH",
            "mini_beauty_balancing_JUNCTIONS_CLOSEPACKING_over_MONASH_lambda_trigger",
            "mini_charm_balancing_JUNCTIONS_CLOSEPACKING_over_MONASH",
            "mini_charm_balancing_JUNCTIONS_CLOSEPACKING_over_MONASH_lambda_trigger",
        }
        canvases = {
            row["canvas_name"]: row
            for row in configuration["canvases_to_be_drawn"]
            if row["canvas_name"] in expected
        }
        self.assertEqual(set(canvases), expected)
        for name, canvas in canvases.items():
            with self.subTest(canvas=name):
                self.assertEqual(canvas["y_min_axis"], 0)
                self.assertEqual(canvas["y_max_axis"], 2.5)

        by_name = {
            row["canvas_name"]: row
            for row in configuration["canvases_to_be_drawn"]
        }
        monash_full = by_name[
            "mini_beauty_balancing_MONASH_full_multiplicity"
        ]
        # The sealed HF_RUN3_V1 Bc 0-1% envelope reaches 8.75e-5.
        self.assertEqual(monash_full["y_min_axis"], 0.00005)
        self.assertEqual(monash_full["y_max_axis"], 0.8)

    def test_block_sem_and_jackknife_formulae(self) -> None:
        block = robustness.block_sem([1.0, 3.0])
        self.assertAlmostEqual(block["mean"], 2.0)
        self.assertAlmostEqual(block["standard_error"], 1.0)
        jackknife = robustness.jackknife_standard_error([1.0, 3.0])
        self.assertAlmostEqual(jackknife["mean"], 2.0)
        self.assertAlmostEqual(jackknife["standard_error"], 1.0)

    def test_nonlinear_quantities_are_formed_inside_every_resample(self) -> None:
        records = []
        for slot in range(100):
            triggers = 100.0 + slot
            meson_yield = 0.20 + 0.0005 * slot
            baryon_yield = 0.08 + 0.0003 * slot + 0.000001 * slot * slot
            records.append(
                robustness.ObservableTerms(
                    robustness.PairTerms(
                        triggers * (meson_yield + 0.1),
                        triggers,
                        triggers * 0.1,
                        triggers,
                    ),
                    robustness.PairTerms(
                        triggers * (baryon_yield + 0.05),
                        triggers,
                        triggers * 0.05,
                        triggers,
                    ),
                )
            )
        results, denominators = robustness.compute_robustness(
            records, "synthetic"
        )
        by_quantity = {row["quantity"]: row for row in results}
        ratio = by_quantity["baryon_over_reference_meson_ratio"]
        full_terms = robustness.sum_terms(records, range(100))
        expected = robustness.evaluate_terms(full_terms, "expected")[
            "baryon_over_reference_meson_ratio"
        ]
        self.assertAlmostEqual(ratio["central_full_union"], expected)
        self.assertNotAlmostEqual(
            ratio["central_full_union"],
            ratio["primary_10_block"]["mean"],
            places=6,
        )
        self.assertEqual(ratio["primary_10_block"]["replicates"], 10)
        self.assertEqual(
            len(ratio["primary_10_block"]["estimates_in_block_index_order"]),
            10,
        )
        self.assertEqual(ratio["alternative_partition"]["replicates"], 20)
        self.assertEqual(ratio["alternative_partition_block_count"], 20)
        self.assertEqual(
            ratio["delete_one_file_jackknife"]["replicates"], 100
        )
        self.assertEqual(
            len(
                ratio["delete_one_file_jackknife"][
                    "estimates_in_omitted_slot_order"
                ]
            ),
            100,
        )
        self.assertGreater(ratio["primary_10_block"]["standard_error"], 0.0)
        self.assertGreater(
            ratio["alternative_partition"]["standard_error"], 0.0
        )
        self.assertGreater(
            ratio["delete_one_file_jackknife"]["standard_error"], 0.0
        )
        self.assertGreater(
            denominators["minimum_absolute_trigger_denominator"], 0.0
        )

    def test_superseding_n110_and_n120_partition_shapes(self) -> None:
        for slots, alternative_blocks in ((110, 11), (120, 20)):
            records = [
                robustness.ObservableTerms(
                    robustness.PairTerms(
                        30.0 + index, 100.0 + index,
                        5.0, 100.0 + index,
                    ),
                    robustness.PairTerms(
                        18.0 + 0.2 * index, 100.0 + index,
                        4.0, 100.0 + index,
                    ),
                )
                for index in range(slots)
            ]
            results, _ = robustness.compute_robustness(
                records, f"synthetic_n{slots}"
            )
            for result in results:
                self.assertEqual(
                    result["alternative_partition_block_count"],
                    alternative_blocks,
                )
                self.assertEqual(
                    result["alternative_partition"]["replicates"],
                    alternative_blocks,
                )
                self.assertEqual(
                    result["delete_one_file_jackknife"]["replicates"],
                    slots,
                )

    def test_exact_zero_denominators_fail_closed(self) -> None:
        bad = robustness.ObservableTerms(
            robustness.PairTerms(1.0, 0.0, 1.0, 0.0),
            robustness.PairTerms(1.0, 0.0, 1.0, 0.0),
        )
        with self.assertRaisesRegex(ValueError, "zero trigger"):
            robustness.evaluate_terms(bad, "zero")

        zero_reference = robustness.ObservableTerms(
            robustness.PairTerms(1.0, 10.0, 1.0, 10.0),
            robustness.PairTerms(2.0, 10.0, 1.0, 10.0),
        )
        with self.assertRaisesRegex(ValueError, "reference-meson"):
            robustness.evaluate_terms(zero_reference, "zero-reference")

    def test_negative_os_minus_ss_is_retained(self) -> None:
        negative = robustness.ObservableTerms(
            robustness.PairTerms(0.5, 10.0, 1.0, 10.0),
            robustness.PairTerms(0.2, 10.0, 0.4, 10.0),
        )
        values = robustness.evaluate_terms(negative, "negative")
        self.assertAlmostEqual(
            values["reference_meson_balancing_yield"], -0.05
        )
        self.assertAlmostEqual(values["baryon_balancing_yield"], -0.02)
        self.assertAlmostEqual(
            values["baryon_over_reference_meson_ratio"], 0.4
        )

    def test_leave_one_block_boundary_stability_is_strict(self) -> None:
        centers = [0.0, 1.0, 2.0]
        contents = [
            [1.0 + (slot % 3), 2.0, 3.0]
            for slot in range(100)
        ]
        central = [
            sum(row[index] for row in contents)
            for index in range(len(centers))
        ]
        frozen = {
            percentile: robustness.strict_stability_threshold(
                centers, central, percentile, f"central/{percentile}"
            )
            for percentile in (0.0, 50.0, 100.0)
        }
        stability = (
            robustness.leave_one_primary_block_out_boundary_stability(
                centers, contents, frozen, "synthetic"
            )
        )
        self.assertEqual(len(stability), 10)
        self.assertTrue(
            all(row["retained_canonical_slots"] == 90 for row in stability)
        )
        with self.assertRaisesRegex(ValueError, "invalid percentile"):
            robustness.strict_stability_threshold(
                centers,
                [1.0, 1.0, 1.0],
                -1.0,
                "invalid",
            )

    def test_origin_exclusion_is_formed_inside_every_resample(self) -> None:
        inclusive = []
        resolved = []
        for slot in range(100):
            triggers = 100.0
            inclusive.append(
                robustness.ObservableTerms(
                    robustness.PairTerms(30.0 + slot / 100.0, triggers, 5.0, triggers),
                    robustness.PairTerms(18.0 + slot / 200.0, triggers, 4.0, triggers),
                )
            )
            resolved.append(
                robustness.ObservableTerms(
                    robustness.PairTerms(28.0 + slot / 100.0, triggers, 4.0, triggers),
                    robustness.PairTerms(16.0 + slot / 200.0, triggers, 3.0, triggers),
                )
            )
        inclusive_results, _ = robustness.compute_robustness(
            inclusive, "inclusive"
        )
        resolved_results, _ = robustness.compute_robustness(
            resolved, "resolved"
        )
        inclusive_ratio = {
            row["quantity"]: row for row in inclusive_results
        }["baryon_over_reference_meson_ratio"]
        resolved_ratio = {
            row["quantity"]: row for row in resolved_results
        }["baryon_over_reference_meson_ratio"]
        self.assertNotEqual(
            inclusive_ratio["central_full_union"],
            resolved_ratio["central_full_union"],
        )
        self.assertNotEqual(
            inclusive_ratio["primary_10_block"]["standard_error"],
            resolved_ratio["primary_10_block"]["standard_error"],
        )


class CommitLineageTest(unittest.TestCase):
    def test_newer_clean_checkout_is_accepted_only_with_exact_macro(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            checkout = Path(temporary) / "checkout"
            subprocess.run(
                ["git", "init", str(checkout)], check=True, capture_output=True
            )
            subprocess.run(
                ["git", "-C", str(checkout), "config", "user.name", "J-b0 Test"],
                check=True,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(checkout),
                    "config",
                    "user.email",
                    "jb0@example.invalid",
                ],
                check=True,
            )
            macro = checkout / "analysis/status_analysis_THnSparse_qq.C"
            macro.parent.mkdir(parents=True)
            macro.write_text("// stable analysis implementation\n")
            subprocess.run(
                ["git", "-C", str(checkout), "add", "analysis"], check=True
            )
            subprocess.run(
                ["git", "-C", str(checkout), "commit", "-m", "raw producer"],
                check=True,
                capture_output=True,
            )
            raw_commit = subprocess.check_output(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
            ).strip()
            (checkout / "pair-stage.txt").write_text("pair analysis\n")
            subprocess.run(
                ["git", "-C", str(checkout), "add", "pair-stage.txt"], check=True
            )
            subprocess.run(
                ["git", "-C", str(checkout), "commit", "-m", "pair analysis"],
                check=True,
                capture_output=True,
            )
            analysis_commit = subprocess.check_output(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
            ).strip()
            (checkout / "audit-stage.txt").write_text("newer audit checkout\n")
            subprocess.run(
                ["git", "-C", str(checkout), "add", "audit-stage.txt"], check=True
            )
            subprocess.run(
                ["git", "-C", str(checkout), "commit", "-m", "audit checkout"],
                check=True,
                capture_output=True,
            )
            robustness_commit = subprocess.check_output(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
            ).strip()
            provenance = {
                "analysis_repository_commit": analysis_commit,
                "analysis_macro_sha256": digest(macro),
            }
            rows = [
                {
                    "campaign": "CURRENT_GRAPH_TEST",
                    "tune": tune,
                    "repository_commit": raw_commit,
                    "producer_executable_sha256": "a" * 64,
                }
                for tune in robustness.EXPECTED_TUNES
            ]
            freeze = {
                "campaign": "CURRENT_GRAPH_TEST",
                "repository_commit": raw_commit,
                "jobs_per_tune": 1,
                "canonical_manifest_sha256": "b" * 64,
                "freeze_seal_sha256": "c" * 64,
            }
            lineage = robustness.validate_analysis_checkout_lineage(
                checkout, rows, freeze, provenance
            )
            self.assertEqual(lineage["raw_production_commit"], raw_commit)
            self.assertEqual(lineage["pair_analysis_commit"], analysis_commit)
            self.assertEqual(
                lineage["robustness_checkout_commit"], robustness_commit
            )

            macro.write_text("// changed analysis implementation\n")
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(checkout),
                    "add",
                    "analysis/status_analysis_THnSparse_qq.C",
                ],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(checkout), "commit", "-m", "change macro"],
                check=True,
                capture_output=True,
            )
            with self.assertRaisesRegex(ValueError, "macro checksum"):
                robustness.validate_analysis_checkout_lineage(
                    checkout, rows, freeze, provenance
                )

            subprocess.run(
                ["git", "-C", str(checkout), "checkout", "--detach", raw_commit],
                check=True,
                capture_output=True,
            )
            (checkout / "sibling.txt").write_text("sibling history\n")
            subprocess.run(
                ["git", "-C", str(checkout), "add", "sibling.txt"], check=True
            )
            subprocess.run(
                ["git", "-C", str(checkout), "commit", "-m", "sibling"],
                check=True,
                capture_output=True,
            )
            with self.assertRaisesRegex(ValueError, "not an ancestor"):
                robustness.validate_analysis_checkout_lineage(
                    checkout, rows, freeze, provenance
                )


class HistoricalProjectionBridgeTest(unittest.TestCase):
    def _commit(self, checkout: Path, message: str) -> str:
        subprocess.run(
            ["git", "-C", str(checkout), "add", "-A"], check=True
        )
        subprocess.run(
            ["git", "-C", str(checkout), "commit", "-m", message],
            check=True,
            capture_output=True,
        )
        return subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
        ).strip()

    def _fixture(self, directory: Path) -> dict:
        checkout = directory / "checkout"
        subprocess.run(
            ["git", "init", str(checkout)], check=True, capture_output=True
        )
        subprocess.run(
            ["git", "-C", str(checkout), "config", "user.name", "J-b0 Test"],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(checkout),
                "config",
                "user.email",
                "jb0@example.invalid",
            ],
            check=True,
        )
        (checkout / "projection.txt").write_text("fresh-history root\n")
        rebuild_root = self._commit(checkout, "projection root")

        campaign = "HF_RUN3_V1"
        raw_commit = "1" * 40
        analysis_commit = "2" * 40
        executable_hash = "3" * 64
        macro_hash = "4" * 64
        manifest_hash = "5" * 64
        seal_hash = "6" * 64
        allowlist_hash = "7" * 64
        rows = []
        for index, tune in enumerate(robustness.EXPECTED_TUNES):
            rows.append(
                {
                    "campaign": campaign,
                    "tune": tune,
                    "canonical_slot": 0,
                    "logical_id": 0,
                    "repository_commit": raw_commit,
                    "producer_executable_sha256": executable_hash,
                    "raw_sha256": f"{index + 8:064x}",
                    "raw_validation_receipt_path":
                        f"raw_validation/{tune}/job000/attempt000/receipt.json",
                    "raw_validation_receipt_sha256": f"{index + 11:064x}",
                    "tune_difference_allowlist_sha256": allowlist_hash,
                }
            )
        freeze = {
            "campaign": campaign,
            "repository_commit": raw_commit,
            "jobs_per_tune": 1,
            "canonical_manifest_sha256": manifest_hash,
            "freeze_seal_sha256": seal_hash,
        }
        analysis = {
            "analysis_repository_commit": analysis_commit,
            "analysis_macro_sha256": macro_hash,
            "analysis_schema": "paul_pair_objects_primary_ground_v3",
            "analysis_implementation":
                "one_pass_primary_ground_pair_analysis_v2",
            "analysis_version": "status_analysis_THnSparse_qq_v2",
            "analysis_profile": "central_primary_ground_v1",
        }
        analysis_root = directory / "analysis"
        receipt_path = (
            analysis_root
            / "validation/analysis_output_manifest_validation.json"
        )
        receipt = {
            "schema": "hf_analysis_output_validation_v3",
            "status": "PASS",
            "canonical_manifest_sha256": manifest_hash,
            "canonical_freeze_seal_sha256": seal_hash,
            "canonical_manifest_rows": len(rows),
            "validated_output_count": len(rows),
            "missing_output_count": 0,
            "analysis_commit": analysis_commit,
            "analysis_macro_sha256": macro_hash,
            "validated_outputs": [
                {
                    "tune": row["tune"],
                    "canonical_slot": row["canonical_slot"],
                    "logical_id": row["logical_id"],
                    "raw_sha256": row["raw_sha256"],
                    "raw_validation_receipt_sha256":
                        row["raw_validation_receipt_sha256"],
                    "analysis_commit": analysis_commit,
                    "analysis_macro_sha256": macro_hash,
                    "upstream_tune_difference_allowlist_sha256":
                        allowlist_hash,
                }
                for row in rows
            ],
        }
        write_json(receipt_path, receipt)
        registry = {
            "schema": robustness.HISTORICAL_PROVENANCE_SCHEMA,
            "purpose": (
                "Provenance only. This fixture changes no physics decision."
            ),
            "history_model": {
                "historical_history": "separate historical archive history",
                "rebuild_history": "fresh rebuild history",
                "projection_source_commit": "8" * 40,
                "rebuild_root_commit": rebuild_root,
                "projection_boundary": "No Git ancestry crosses this boundary.",
            },
            "campaigns": {
                campaign: {
                    "canonical_freeze": {
                        "manifest_sha256": manifest_hash,
                        "seal_sha256": seal_hash,
                        "rows": len(rows),
                        "tunes": len(robustness.EXPECTED_TUNES),
                        "jobs_per_tune": 1,
                        "blocks": 10,
                    },
                    "raw_production": {
                        "repository_commit": raw_commit,
                        "producer_executable_sha256": executable_hash,
                    },
                    "analysis_validation_receipt": {
                        "relative_path": (
                            "validation/analysis_output_manifest_validation.json"
                        ),
                        "sha256": digest(receipt_path),
                        "schema": receipt["schema"],
                        "status": receipt["status"],
                        "canonical_manifest_rows": len(rows),
                        "validated_output_count": len(rows),
                        "missing_output_count": 0,
                    },
                    "pair_analysis": {
                        "repository_commit": analysis_commit,
                        "macro_sha256": macro_hash,
                        "schema": analysis["analysis_schema"],
                        "implementation": analysis[
                            "analysis_implementation"
                        ],
                        "version": analysis["analysis_version"],
                        "profile": analysis["analysis_profile"],
                    },
                    "archive_generation_evidence": {
                        "raw_to_analysis_ancestor": True,
                        "ancestry_path_definition": "ordered identities",
                        "ancestry_path_commit_count": 1,
                        "ancestry_path_identities_sha256": "9" * 64,
                        "analysis_macro_historical_path":
                            "AnalysisScripts/status_analysis_THnSparse_qq.C",
                        "analysis_macro_git_blob": "a" * 40,
                        "analysis_to_projection_source_ancestor": False,
                    },
                }
            },
        }
        registry_path = (
            checkout / "config/accepted_historical_provenance_v1.json"
        )
        write_json(registry_path, registry)
        self._commit(checkout, "accepted historical projection")
        return {
            "checkout": checkout,
            "analysis_root": analysis_root,
            "receipt_path": receipt_path,
            "receipt": receipt,
            "registry_path": registry_path,
            "rows": rows,
            "freeze": freeze,
            "analysis": analysis,
            "raw_commit": raw_commit,
            "analysis_commit": analysis_commit,
        }

    def _validate(self, fixture: dict) -> dict:
        return robustness.validate_analysis_checkout_lineage(
            fixture["checkout"],
            fixture["rows"],
            fixture["freeze"],
            fixture["analysis"],
            fixture["analysis_root"],
        )

    def test_exact_projection_passes_without_historical_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            for commit in (
                fixture["raw_commit"], fixture["analysis_commit"]
            ):
                self.assertFalse(
                    robustness.commit_exists(fixture["checkout"], commit)
                )
            self.assertEqual(
                subprocess.check_output(
                    ["git", "-C", str(fixture["checkout"]), "remote"],
                    text=True,
                ),
                "",
            )
            lineage = self._validate(fixture)
            self.assertEqual(
                lineage["provenance_mode"],
                robustness.ACCEPTED_HISTORICAL_PROJECTION,
            )
            self.assertRegex(
                lineage["accepted_historical_provenance_registry_sha256"],
                r"^[0-9a-f]{64}$",
            )
            self.assertEqual(
                lineage["analysis_validation_receipt"]["status"], "PASS"
            )
            raw_lineage = robustness.validate_raw_checkout_lineage(
                fixture["checkout"],
                fixture["rows"],
                fixture["freeze"],
                "origin-audit",
            )
            self.assertEqual(
                raw_lineage["provenance_mode"],
                robustness.ACCEPTED_HISTORICAL_PROJECTION,
            )
            for commit in (
                fixture["raw_commit"], fixture["analysis_commit"]
            ):
                self.assertFalse(
                    robustness.commit_exists(fixture["checkout"], commit)
                )

    def test_each_pinned_projection_field_is_load_bearing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            mutations = {
                "manifest hash": lambda value: value["freeze"].update(
                    canonical_manifest_sha256="0" * 64
                ),
                "seal hash": lambda value: value["freeze"].update(
                    freeze_seal_sha256="0" * 64
                ),
                "campaign": lambda value: (
                    value["freeze"].update(campaign="UNKNOWN"),
                    [row.update(campaign="UNKNOWN") for row in value["rows"]],
                ),
                "raw commit": lambda value: (
                    value["freeze"].update(repository_commit="b" * 40),
                    [
                        row.update(repository_commit="b" * 40)
                        for row in value["rows"]
                    ],
                ),
                "executable hash": lambda value: [
                    row.update(producer_executable_sha256="c" * 64)
                    for row in value["rows"]
                ],
                "analysis commit": lambda value: value["analysis"].update(
                    analysis_repository_commit="d" * 40
                ),
                "macro hash": lambda value: value["analysis"].update(
                    analysis_macro_sha256="e" * 64
                ),
                "schema": lambda value: value["analysis"].update(
                    analysis_schema="paul_pair_objects_primary_ground_v2"
                ),
                "implementation": lambda value: value["analysis"].update(
                    analysis_implementation="other"
                ),
                "version": lambda value: value["analysis"].update(
                    analysis_version="other"
                ),
                "profile": lambda value: value["analysis"].update(
                    analysis_profile="other"
                ),
                "count": lambda value: value["freeze"].update(
                    jobs_per_tune=2
                ),
            }
            for label, mutate in mutations.items():
                with self.subTest(field=label):
                    candidate = {
                        **fixture,
                        "rows": copy.deepcopy(fixture["rows"]),
                        "freeze": copy.deepcopy(fixture["freeze"]),
                        "analysis": copy.deepcopy(fixture["analysis"]),
                    }
                    mutate(candidate)
                    with self.assertRaises(ValueError):
                        self._validate(candidate)

            original_receipt = fixture["receipt_path"].read_text()
            fixture["receipt_path"].write_text(original_receipt + " ")
            with self.assertRaisesRegex(ValueError, "receipt bytes"):
                self._validate(fixture)
            fixture["receipt_path"].write_text(original_receipt)

    def test_missing_unknown_dirty_and_wrong_projection_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)

            missing = self._fixture(base / "missing")
            missing["registry_path"].unlink()
            self._commit(missing["checkout"], "remove registry")
            with self.assertRaisesRegex(ValueError, "registry is absent"):
                self._validate(missing)

            dirty = self._fixture(base / "dirty")
            (dirty["checkout"] / "projection.txt").write_text("dirty\n")
            with self.assertRaisesRegex(ValueError, "tracked modifications"):
                self._validate(dirty)

            wrong_root = self._fixture(base / "wrong_root")
            registry = json.loads(wrong_root["registry_path"].read_text())
            registry["history_model"]["rebuild_root_commit"] = "f" * 40
            write_json(wrong_root["registry_path"], registry)
            self._commit(wrong_root["checkout"], "wrong projection root")
            with self.assertRaisesRegex(ValueError, "accepted rebuild root"):
                self._validate(wrong_root)

            unknown = self._fixture(base / "unknown")
            unknown["freeze"]["campaign"] = "UNKNOWN"
            for row in unknown["rows"]:
                row["campaign"] = "UNKNOWN"
            with self.assertRaisesRegex(ValueError, "not accepted"):
                self._validate(unknown)


class ProducerV2CanonicalFreezeTest(unittest.TestCase):
    def test_real_builder_contract_and_fail_closed_mutants(self) -> None:
        spec = json.loads(
            (ROOT / "config/statistical_robustness_v1.json").read_text()
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = build_producer_v2_freeze(root / "base")
            rows, provenance = robustness.validate_canonical_freeze(base, spec)
            self.assertEqual(len(rows), 330)
            self.assertEqual(provenance["jobs_per_tune"], 110)
            self.assertEqual(
                provenance["canonical_freeze_contract"], "PRODUCER_V2"
            )
            self.assertEqual(provenance["expanded_artifacts"]["state"], "ABSENT")
            self.assertNotEqual(provenance["jobs_per_tune"], 100)

            def copied(name: str) -> Path:
                target = root / name
                shutil.copytree(base, target)
                return target

            def objects(freeze: Path) -> tuple[list[dict], dict]:
                manifest_rows = [
                    json.loads(line)
                    for line in (freeze / "canonical_manifest.jsonl")
                    .read_text()
                    .splitlines()
                ]
                seal = json.loads((freeze / "freeze_seal.json").read_text())
                return manifest_rows, seal

            mutants: list[tuple[str, object]] = []

            def manifest_tamper(freeze: Path) -> None:
                path = freeze / "canonical_manifest.jsonl"
                path.write_text(path.read_text() + "{}\n")

            mutants.append(("manifest_tamper", manifest_tamper))

            def seal_tamper(freeze: Path) -> None:
                seal = json.loads((freeze / "freeze_seal.json").read_text())
                seal["canonical_manifest_sha256"] = "0" * 64
                write_json(freeze / "freeze_seal.json", seal)

            mutants.append(("seal_tamper", seal_tamper))

            def wrong_campaign(freeze: Path) -> None:
                seal = json.loads((freeze / "freeze_seal.json").read_text())
                seal["campaign"] = "OTHER_CAMPAIGN"
                write_json(freeze / "freeze_seal.json", seal)

            mutants.append(("wrong_campaign", wrong_campaign))

            def unequal_exposure(freeze: Path) -> None:
                changed, seal = objects(freeze)
                changed.pop()
                seal["rows"] = len(changed)
                rewrite_producer_freeze(freeze, changed, seal)

            mutants.append(("unequal_exposure", unequal_exposure))

            def duplicate_missing_slot(freeze: Path) -> None:
                changed, seal = objects(freeze)
                changed[-1]["canonical_slot"] = 108
                changed[-1]["block"] = 8
                changed[-1]["block_position"] = 10
                rewrite_producer_freeze(freeze, changed, seal)

            mutants.append(("duplicate_missing_slot", duplicate_missing_slot))

            def invalid_row_provenance(freeze: Path) -> None:
                changed, seal = objects(freeze)
                changed[0]["repository_commit"] = "z" * 40
                rewrite_producer_freeze(freeze, changed, seal)

            mutants.append(("invalid_row_provenance", invalid_row_provenance))

            def bad_total(freeze: Path) -> None:
                seal = json.loads((freeze / "freeze_seal.json").read_text())
                seal["total_requested_successes"] += 1
                write_json(freeze / "freeze_seal.json", seal)

            mutants.append(("bad_total", bad_total))

            def corrupt_block(freeze: Path) -> None:
                (freeze / "block_01.jsonl").write_text("not-json\n")

            mutants.append(("corrupt_block", corrupt_block))

            def reordered_block(freeze: Path) -> None:
                path = freeze / "block_01.jsonl"
                lines = path.read_text().splitlines()
                path.write_text("\n".join(reversed(lines)) + "\n")

            mutants.append(("reordered_block", reordered_block))

            def missing_block(freeze: Path) -> None:
                (freeze / "block_01.jsonl").unlink()

            mutants.append(("missing_block", missing_block))

            def symlink_block(freeze: Path) -> None:
                path = freeze / "block_01.jsonl"
                path.unlink()
                os.symlink(freeze / "block_02.jsonl", path)

            mutants.append(("symlink_block", symlink_block))

            def partial_expanded(freeze: Path) -> None:
                write_json(freeze / "freeze_summary.json", {"schema": "partial"})

            mutants.append(("partial_expanded", partial_expanded))

            def unrelated_schema(freeze: Path) -> None:
                seal = json.loads((freeze / "freeze_seal.json").read_text())
                seal["schema"] = "unrelated_freeze_schema"
                write_json(freeze / "freeze_seal.json", seal)

            mutants.append(("unrelated_schema", unrelated_schema))

            def unsealed_extra(freeze: Path) -> None:
                (freeze / "unsealed.txt").write_text("not in the v2 seal\n")

            mutants.append(("unsealed_extra", unsealed_extra))

            for name, mutate in mutants:
                with self.subTest(mutant=name):
                    freeze = copied(name)
                    mutate(freeze)  # type: ignore[operator]
                    with self.assertRaises(ValueError):
                        robustness.validate_canonical_freeze(freeze, spec)


class CanonicalFreezeTest(unittest.TestCase):
    def test_exact_sealed_300_row_freeze_is_accepted(self) -> None:
        spec = json.loads(
            (ROOT / "config/statistical_robustness_v1.json").read_text()
        )
        contracts = spec["contracts"]
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            rows = []
            index = 0
            for tune_ordinal, tune in enumerate(robustness.EXPECTED_TUNES):
                for slot in range(100):
                    rows.append(
                        {
                            "schema": contracts["canonical_manifest_schema"],
                            "tune": tune,
                            "tune_ordinal": tune_ordinal,
                            "canonical_slot": slot,
                            "block": slot % 10,
                            "block_position": slot // 10,
                            "raw_schema": contracts["raw_schema"],
                            "selector": contracts["selector"],
                            "origin_algorithm": contracts["origin_algorithm"],
                            "species_registry_sha256":
                                contracts["species_registry_sha256"],
                            "pair_registry_sha256":
                                contracts["pair_registry_sha256"],
                            "tune_difference_allowlist_schema":
                                contracts[
                                    "tune_difference_allowlist_schema"
                                ],
                            "tune_difference_allowlist_sha256":
                                contracts[
                                    "tune_difference_allowlist_sha256"
                                ],
                            "repository_commit": "a" * 40,
                            "raw_sha256": f"{index:064x}",
                            "producer_executable_sha256": "b" * 64,
                            "effective_card_sha256": "c" * 64,
                            "seed": index + 1,
                            "raw_path": f"raw/{tune}/job_{slot:03d}.root",
                            "requested_successes": 1_000_000,
                        }
                    )
                    index += 1
            manifest = directory / "canonical_manifest.jsonl"
            manifest.write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
            )
            block_hashes = {}
            for block in range(10):
                path = directory / f"block_{block + 1:02d}.jsonl"
                path.write_text(
                    "".join(
                        json.dumps(row, sort_keys=True) + "\n"
                        for row in rows
                        if row["canonical_slot"] % 10 == block
                    )
                )
                block_hashes[path.name] = digest(path)
            summary = {
                "schema": contracts["canonical_summary_schema"],
                "campaign": "synthetic",
                "campaign_ordinal": 999,
                "canonical_manifest_sha256": digest(manifest),
                "block_manifest_sha256": block_hashes,
                "jobs_per_tune": 100,
                "block_count": 10,
                "jobs_per_tune_per_block": 10,
                "raw_schema": contracts["raw_schema"],
                "origin_algorithm": contracts["origin_algorithm"],
                "selector": contracts["selector"],
                "species_registry_sha256":
                    contracts["species_registry_sha256"],
                "pair_registry_sha256": contracts["pair_registry_sha256"],
                "tune_difference_allowlist_schema":
                    contracts["tune_difference_allowlist_schema"],
                "tune_difference_allowlist_sha256":
                    contracts["tune_difference_allowlist_sha256"],
            }
            (directory / "freeze_summary.json").write_text(
                json.dumps(summary)
            )
            validation_log = directory / "canonical_raw_validation.log"
            validation_log.write_text(
                "CANONICAL_RAW_VALIDATION errors=0 files=300\n"
            )
            receipt = {
                "schema": contracts["canonical_validation_receipt_schema"],
                "state": "PASS",
                "canonical_manifest_sha256": digest(manifest),
                "canonical_manifest_rows": 300,
                "validation_log_sha256": digest(validation_log),
            }
            receipt_path = directory / "canonical_raw_validation_receipt.json"
            receipt_path.write_text(json.dumps(receipt))
            seal = {
                "schema": contracts["canonical_seal_schema"],
                "state": "SEALED",
                "canonical_manifest_sha256": digest(manifest),
                "validation_receipt_path":
                    "canonical_raw_validation_receipt.json",
                "validation_receipt_sha256": digest(receipt_path),
                "validation_log_path": "canonical_raw_validation.log",
                "validation_log_sha256": digest(validation_log),
            }
            (directory / "freeze_seal.json").write_text(json.dumps(seal))
            validated, provenance = robustness.validate_canonical_freeze(
                directory, spec
            )
            self.assertEqual(len(validated), 300)
            self.assertEqual(
                provenance["successful_events_per_tune"], 100_000_000
            )
            self.assertEqual(
                provenance["canonical_freeze_contract"],
                "EXPANDED_CANONICAL_V3",
            )
            summary["schema"] = "unrelated_expanded_schema"
            (directory / "freeze_summary.json").write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError, "summary differs"):
                robustness.validate_canonical_freeze(directory, spec)


class BoundaryReceiptTest(unittest.TestCase):
    def _receipt(self, directory: Path) -> tuple[dict, dict]:
        try:
            import ROOT as pyroot  # type: ignore
        except ImportError:
            self.skipTest("PyROOT is unavailable")
        spec = json.loads(
            (ROOT / "config/statistical_robustness_v1.json").read_text()
        )
        configuration = (
            ROOT
            / spec["contracts"]["boundary_configuration_path"]
        )
        configured = json.loads(configuration.read_text())
        intervals = sorted(
            {
                (
                    float(row["multiplicityMin"]),
                    float(row["multiplicityMax"]),
                )
                for row in configured["histograms_to_analyse"]
                if not (
                    float(row["multiplicityMin"]) == 0.0
                    and float(row["multiplicityMax"]) == 100.0
                )
            }
        )
        percentiles = sorted(
            {value for interval in intervals for value in interval}
        )
        contents = [1.0] * 101
        integral = sum(contents)

        payload = {
            "schema": robustness.BOUNDARY_RECEIPT_SCHEMA,
            "schema_version": 2,
            "algorithm": "per_tune_summed_multiplicity_quantiles_discrete_v2",
            "completion_status": "PASS",
            "configuration_path":
                spec["contracts"]["boundary_configuration_path"],
            "configuration_sha256": digest(configuration),
            "plotter_source_sha256": digest(
                ROOT / "plotting/improvedPlotting_THnSparse.C"
            ),
            "boundary_utility_sha256": digest(
                ROOT / "plotting/MultiplicityBoundaryUtils.h"
            ),
            "class_contract_sha256": digest(
                ROOT / "config/multiplicity_percentile_classes_v2.json"
            ),
            "policy": {
                "normalization": "sum_of_regular_bins",
                "underflow": "must_be_exactly_zero_and_is_excluded",
                "overflow": "must_be_exactly_zero_and_is_excluded",
                "class_bounds": "inclusive_integer_nch",
            },
            "tunes": {},
        }
        for tune in robustness.EXPECTED_TUNES:
            source = directory / f"{tune}.root"
            root_file = pyroot.TFile(str(source), "RECREATE")
            histogram = pyroot.TH1D(
                "summed MULTIPLICITY",
                "summed MULTIPLICITY",
                101,
                -0.5,
                100.5,
            )
            histogram.Sumw2()
            for index, value in enumerate(contents, start=1):
                histogram.SetBinContent(index, value)
                histogram.SetBinError(index, math.sqrt(value))
            histogram.Write()
            root_file.Close()

            thresholds = {
                percentile: robustness.strict_stability_threshold(
                    list(map(float, range(101))),
                    contents,
                    percentile,
                    f"{tune}/fixture",
                )
                for percentile in percentiles
            }
            threshold_rows = []
            for percentile, threshold in sorted(thresholds.items()):
                before = sum(contents[:threshold]) / integral
                through = sum(contents[: threshold + 1]) / integral
                threshold_rows.append(
                    {
                        "percentile": percentile,
                        "nch_threshold": threshold,
                        "target_low_activity_fraction":
                            (100.0 - percentile) / 100.0,
                        "achieved_exclusive_fraction_before_threshold":
                            before,
                        "achieved_inclusive_fraction_through_threshold":
                            through,
                    }
                )
            class_rows = []
            for low, high in intervals:
                minimum = thresholds[high] + (1 if high < 100.0 else 0)
                maximum = thresholds[low]
                achieved = (
                    sum(contents[minimum : maximum + 1]) / integral
                )
                class_rows.append(
                    {
                        "percentile_min": low,
                        "percentile_max": high,
                        "nch_min_inclusive": minimum,
                        "nch_max_inclusive": maximum,
                        "target_fraction": (high - low) / 100.0,
                        "achieved_weighted_fraction": achieved,
                    }
                )
            payload["tunes"][tune] = {
                "central_reference_path": source.resolve().as_posix(),
                "central_source_file_sha256": digest(source),
                "histogram_name": "summed MULTIPLICITY",
                "regular_bin_integral": integral,
                "underflow": 0.0,
                "overflow": 0.0,
                "thresholds": threshold_rows,
                "classes": class_rows,
                "partition": {
                    "nch_min_inclusive": thresholds[100.0],
                    "nch_max_inclusive": thresholds[0.0],
                    "coverage": "PASS",
                    "disjointness": "PASS",
                },
            }
        receipt = dict(payload)
        receipt["payload_sha256"] = robustness.json_sha256(payload)
        return spec, receipt

    def test_contiguous_frozen_class_union_and_quantile_recheck(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            spec, receipt = self._receipt(directory)
            path = directory / "multiplicity_boundary_receipt_v2.json"
            path.write_text(json.dumps(receipt, sort_keys=True))
            _, ranges, _, binding = robustness.validate_boundary_receipt(
                path, spec, ROOT
            )
            self.assertEqual(
                binding["provenance_mode"], "CURRENT_PLOTTER_SOURCE"
            )
            for tune in robustness.EXPECTED_TUNES:
                self.assertEqual(
                    ranges[tune]["highest_activity_percentile_0_10"],
                    (91.0, 100.0),
                )

            bad = json.loads(path.read_text())
            bad["tunes"]["MONASH"]["thresholds"][0][
                "achieved_inclusive_fraction_through_threshold"
            ] -= 0.01
            body = dict(bad)
            body.pop("payload_sha256")
            bad["payload_sha256"] = robustness.json_sha256(body)
            path.write_text(json.dumps(bad, sort_keys=True))
            with self.assertRaisesRegex(
                ValueError, "was not recomputed from the frozen source"
            ):
                robustness.validate_boundary_receipt(path, spec, ROOT)

    def test_exact_accepted_historical_digest_is_an_explicit_route(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "sources").mkdir()
            spec, receipt = self._receipt(directory / "sources")
            checkout = directory / "checkout"
            for relative in (
                spec["contracts"]["boundary_configuration_path"],
                "plotting/improvedPlotting_THnSparse.C",
                "plotting/MultiplicityBoundaryUtils.h",
                "config/multiplicity_percentile_classes_v2.json",
            ):
                source = ROOT / relative
                target = checkout / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            (checkout / "plotting/improvedPlotting_THnSparse.C").write_text(
                "// a newer plotter that did not create the accepted receipt\n"
            )
            relative = (
                "HF_RUN3_V1/4d309e9f99e4/plotting/THnSparse/"
                "multiplicity_boundary_receipt_v2.json"
            )
            path = directory / "results" / relative
            write_json(path, receipt)
            accepted = {
                "schema": "hadronization_accepted_measurements_v1",
                "nominal": {
                    "campaign": "HF_RUN3_V1",
                    "accepted_root": "4d309e9f99e4",
                    "boundary_receipt_path": relative,
                    "boundary_receipt_sha256": digest(path),
                },
            }
            write_json(
                checkout / "config/accepted_measurements_v1.json", accepted
            )
            _, _, _, binding = robustness.validate_boundary_receipt(
                path, spec, checkout
            )
            self.assertEqual(
                binding["provenance_mode"],
                "ACCEPTED_HISTORICAL_RECEIPT_DIGEST",
            )
            self.assertEqual(
                binding["accepted_boundary_receipt_sha256"], digest(path)
            )

            accepted["nominal"]["boundary_receipt_sha256"] = "0" * 64
            write_json(
                checkout / "config/accepted_measurements_v1.json", accepted
            )
            with self.assertRaisesRegex(ValueError, "matches neither"):
                robustness.validate_boundary_receipt(path, spec, checkout)


class SyntheticRootContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            import ROOT as pyroot  # type: ignore
        except ImportError:
            cls.pyroot = None
        else:
            cls.pyroot = pyroot
            pyroot.gROOT.SetBatch(True)

    def _write_pair_file(
        self,
        path: Path,
        pair: dict,
        row: dict,
        contracts: dict,
        same_sign_factor: float = 1.0,
        second_origin_category: float = 1.0,
        origin_category_labels: str | None = None,
        analysis_commit: str = "e" * 40,
        analysis_macro_sha256: str = "d" * 64,
        analysis_schema: str | None = None,
    ) -> None:
        assert self.pyroot is not None
        root = self.pyroot
        path.parent.mkdir(parents=True, exist_ok=True)
        output = root.TFile(str(path), "RECREATE")
        multiplicity = root.TH1D(
            "summed MULTIPLICITY", "", 4096, -0.5, 4095.5
        )
        multiplicity.Sumw2()
        multiplicity.Fill(10.0, 2.0)
        multiplicity.Fill(11.0, 3.0)
        trigger = root.THnSparseD(
            "hTrKinematics",
            "",
            4,
            array("i", [100, 100, 4, 4096]),
            array("d", [-math.pi, -4.0, 0.0, -0.5]),
            array(
                "d",
                [
                    math.pi,
                    math.nextafter(4.0, math.inf),
                    math.nextafter(7000.0, math.inf),
                    4095.5,
                ],
            ),
        )
        eta_edges = array(
            "d", [-4.0 + 8.0 * index / 100 for index in range(101)]
        )
        eta_edges[-1] = math.nextafter(4.0, math.inf)
        delta_eta_edges = array(
            "d", [-8.0 + 16.0 * index / 100 for index in range(101)]
        )
        delta_eta_edges[-1] = math.nextafter(8.0, math.inf)
        pt_edges = array(
            "d",
            [0.0, 50.0, 100.0, 1000.0, math.nextafter(7000.0, math.inf)],
        )
        trigger.GetAxis(1).Set(100, eta_edges)
        trigger.GetAxis(2).Set(4, pt_edges)
        trigger.Sumw2()
        trigger.Fill(array("d", [0.0, 0.0, 5.0, 10.0]), 2.0)
        trigger.Fill(array("d", [0.1, 0.1, 200.0, 11.0]), 3.0)
        associate = root.THnSparseD(
            "hAsKinematics",
            "",
            4,
            array("i", [100, 100, 4, 4096]),
            array("d", [-math.pi, -4.0, 0.0, -0.5]),
            array(
                "d",
                [
                    math.pi,
                    math.nextafter(4.0, math.inf),
                    math.nextafter(7000.0, math.inf),
                    4095.5,
                ],
            ),
        )
        associate.GetAxis(1).Set(100, eta_edges)
        associate.GetAxis(2).Set(4, pt_edges)
        associate.Sumw2()
        associate.Fill(array("d", [0.2, 0.0, 2.0, 10.0]), 1.0)
        associate.Fill(array("d", [0.3, 0.1, 150.0, 11.0]), 4.0)
        correlation = root.THnSparseD(
            "hCorrelations",
            "",
            7,
            array("i", [100, 100, 100, 100, 4, 4, 4096]),
            array(
                "d",
                [-math.pi / 2, -8.0, -4.0, -4.0, 0.0, 0.0, -0.5],
            ),
            array(
                "d",
                [
                    3 * math.pi / 2,
                    math.nextafter(8.0, math.inf),
                    math.nextafter(4.0, math.inf),
                    math.nextafter(4.0, math.inf),
                    math.nextafter(7000.0, math.inf),
                    math.nextafter(7000.0, math.inf),
                    4095.5,
                ],
            ),
        )
        correlation.GetAxis(1).Set(100, delta_eta_edges)
        correlation.GetAxis(2).Set(100, eta_edges)
        correlation.GetAxis(3).Set(100, eta_edges)
        correlation.GetAxis(4).Set(4, pt_edges)
        correlation.GetAxis(5).Set(4, pt_edges)
        correlation.Sumw2()
        correlation.Fill(
            array("d", [0.2, 0.0, 0.0, 0.0, 5.0, 2.0, 10.0]), 1.0
        )
        correlation.Fill(
            array(
                "d",
                [0.3, 0.0, 0.1, 0.1, 200.0, 150.0, 11.0],
            ),
            4.0,
        )
        correlation_by_origin = root.THnSparseD(
            "hCorrelationsByOrigin",
            "",
            8,
            array("i", [100, 100, 100, 100, 4, 4, 4096, 6]),
            array(
                "d",
                [-math.pi / 2, -8.0, -4.0, -4.0, 0.0, 0.0, -0.5, 0.5],
            ),
            array(
                "d",
                [
                    3 * math.pi / 2,
                    math.nextafter(8.0, math.inf),
                    math.nextafter(4.0, math.inf),
                    math.nextafter(4.0, math.inf),
                    math.nextafter(7000.0, math.inf),
                    math.nextafter(7000.0, math.inf),
                    4095.5,
                    6.5,
                ],
            ),
        )
        correlation_by_origin.GetAxis(1).Set(100, delta_eta_edges)
        correlation_by_origin.GetAxis(2).Set(100, eta_edges)
        correlation_by_origin.GetAxis(3).Set(100, eta_edges)
        correlation_by_origin.GetAxis(4).Set(4, pt_edges)
        correlation_by_origin.GetAxis(5).Set(4, pt_edges)
        correlation_by_origin.Sumw2()
        correlation_by_origin.Fill(
            array(
                "d",
                [0.2, 0.0, 0.0, 0.0, 5.0, 2.0, 10.0, 1.0],
            ),
            1.0,
        )
        correlation_by_origin.Fill(
            array(
                "d",
                [
                    0.3,
                    0.0,
                    0.1,
                    0.1,
                    200.0,
                    150.0,
                    11.0,
                    second_origin_category,
                ],
            ),
            4.0,
        )
        multiplicity.Write()
        trigger.Write()
        associate.Write()
        correlation.Write()
        correlation_by_origin.Write()
        strings = {
            "analysis_schema": (
                contracts["analysis_schema"]
                if analysis_schema is None
                else analysis_schema
            ),
            "analysis_implementation": contracts["analysis_implementation"],
            "analysis_version": contracts["analysis_version"],
            "analysis_profile": contracts["analysis_profile"],
            "pair_combinatorics_mode":
                contracts["pair_combinatorics_mode"],
            "associate_origin_category_schema":
                contracts["associate_origin_category_schema"],
            "associate_origin_category_labels":
                (
                    contracts["associate_origin_category_labels"]
                    if origin_category_labels is None
                    else origin_category_labels
                ),
            "event_filter_schema": "all_events_v1",
            "analysis_macro_sha256": analysis_macro_sha256,
            "analysis_repository_commit": analysis_commit,
            "selector_version": contracts["selector"],
            "upstream_raw_schema": contracts["raw_schema"],
            "upstream_raw_sha256": row["raw_sha256"],
            "upstream_origin_algorithm": contracts["origin_algorithm"],
            "upstream_selector_version": contracts["selector"],
            "upstream_campaign": row["campaign"],
            "upstream_tune": row["tune"],
            "upstream_repository_commit": row["repository_commit"],
            "upstream_executable_sha256":
                row["producer_executable_sha256"],
            "upstream_heavy_stability_audit_schema":
                "heavy_stability_audit_v2",
            "upstream_heavy_stability_audit_sha256": "f" * 64,
            "upstream_effective_settings_schema":
                contracts["effective_settings_schema"],
            "upstream_effective_settings_sha256": "1" * 64,
            "species_registry_sha256":
                contracts["species_registry_sha256"],
            "upstream_tune_difference_allowlist_schema":
                contracts["tune_difference_allowlist_schema"],
            "upstream_tune_difference_allowlist_sha256":
                contracts["tune_difference_allowlist_sha256"],
            "pair_registry_sha256": contracts["pair_registry_sha256"],
            "heavy_sector": pair["sector"],
            "heavy_sign": pair["heavy_sign"],
        }
        for name, value in strings.items():
            root.TObjString(value).Write(name)
        integer_parameters = {
            "trigger_pdg": pair["trigger_pdg"],
            "associate_pdg": pair["associate_pdg"],
            "reference_meson_pdg": pair["reference_meson_pdg"],
            "input_file_count": 1,
            "event_filter_modulo": 0,
            "event_filter_remainder": -1,
        }
        long_parameters = {
            "upstream_heavy_flavour_conservation_failures": 0,
            "upstream_origin_classification_failures": 0,
            "input_events": 2,
            "source_input_events": 2,
            "primary_all_heavy_closure_failures": 0,
            "direct_primary_heavy_count": 2,
            "central_ground_state_count": 2,
            "central_hard_trigger_count": 2,
            "trigger_count": 2,
            "pair_count": 2,
        }
        double_parameters = {
            "trigger_pt_min_exclusive": 1.0,
            "associate_pt_min_exclusive": 0.15,
            "eta_abs_max_inclusive": 4.0,
            "same_sign_pair_factor": same_sign_factor,
            "input_sum_weights": 5.0,
            "trigger_sum_weights": 5.0,
            "pair_sum_weights": 5.0,
        }
        for name, value in integer_parameters.items():
            root.TParameter("int")(name, value).Write()
        for name, value in long_parameters.items():
            root.TParameter("Long64_t")(name, value).Write()
        for name, value in double_parameters.items():
            root.TParameter("double")(name, value).Write()
        output.Close()

    def test_full_preselected_kinematics_are_integrated_without_recut(self) -> None:
        if self.pyroot is None:
            self.skipTest("PyROOT is unavailable")
        spec = json.loads(
            (ROOT / "config/statistical_robustness_v1.json").read_text()
        )
        pair_lookup = robustness.validate_spec(spec, ROOT)
        pair = pair_lookup[(411, -411)]
        row = {
            "tune": "MONASH",
            "canonical_slot": 0,
            "campaign": "synthetic",
            "raw_sha256": "a" * 64,
            "repository_commit": "b" * 40,
            "producer_executable_sha256": "c" * 64,
            "requested_successes": 2,
        }
        with tempfile.TemporaryDirectory() as temporary:
            per_job = Path(temporary)
            path = per_job / "MONASH/slot_000/DplusDminus.root"
            self._write_pair_file(path, pair, row, spec["contracts"])
            values, (_, contents) = robustness.inspect_pair_file(
                path,
                per_job,
                row,
                pair,
                spec["contracts"],
                {"inclusive": (0.0, 15.0)},
                {},
                {},
            )
            self.assertEqual(sum(contents), 5.0)
            # The pT=(200,150) entry is deliberately beyond the obsolete
            # plotting windows (20,100) and must remain in this audit.
            self.assertAlmostEqual(values["inclusive"][0], 5.0)
            self.assertAlmostEqual(values["inclusive"][1], 5.0)
            self.assertAlmostEqual(values["inclusive"][2], 5.0)

    def test_mixed_pair_provenance_is_rejected(self) -> None:
        if self.pyroot is None:
            self.skipTest("PyROOT is unavailable")
        spec = json.loads(
            (ROOT / "config/statistical_robustness_v1.json").read_text()
        )
        pair = robustness.validate_spec(spec, ROOT)[(411, -411)]
        row = {
            "tune": "MONASH",
            "canonical_slot": 0,
            "campaign": "synthetic",
            "raw_sha256": "a" * 64,
            "repository_commit": "b" * 40,
            "producer_executable_sha256": "c" * 64,
            "requested_successes": 2,
        }
        with tempfile.TemporaryDirectory() as temporary:
            per_job = Path(temporary)
            first = per_job / "first.root"
            second = per_job / "second.root"
            self._write_pair_file(first, pair, row, spec["contracts"])
            self._write_pair_file(
                second,
                pair,
                row,
                spec["contracts"],
                analysis_commit="f" * 40,
            )
            common: dict[str, str] = {}
            inventory: dict[Path, dict] = {}
            robustness.inspect_pair_file(
                first,
                per_job,
                row,
                pair,
                spec["contracts"],
                {"inclusive": (0.0, 15.0)},
                common,
                inventory,
            )
            with self.assertRaisesRegex(ValueError, "mixed analysis"):
                robustness.inspect_pair_file(
                    second,
                    per_job,
                    row,
                    pair,
                    spec["contracts"],
                    {"inclusive": (0.0, 15.0)},
                    common,
                    inventory,
                )

    def test_unresolved_associate_category_is_excluded_only_from_sensitivity(
        self,
    ) -> None:
        if self.pyroot is None:
            self.skipTest("PyROOT is unavailable")
        spec = json.loads(
            (ROOT / "config/statistical_robustness_v1.json").read_text()
        )
        pair = robustness.validate_spec(spec, ROOT)[(411, -411)]
        row = {
            "tune": "MONASH",
            "canonical_slot": 0,
            "campaign": "synthetic",
            "raw_sha256": "a" * 64,
            "repository_commit": "b" * 40,
            "producer_executable_sha256": "c" * 64,
            "requested_successes": 2,
        }
        with tempfile.TemporaryDirectory() as temporary:
            per_job = Path(temporary)
            path = per_job / "MONASH/slot_000/DplusDminus.root"
            self._write_pair_file(
                path,
                pair,
                row,
                spec["contracts"],
                second_origin_category=6.0,
            )
            values, _ = robustness.inspect_pair_file(
                path,
                per_job,
                row,
                pair,
                spec["contracts"],
                {"inclusive": (0.0, 15.0)},
                {},
                {},
            )
            self.assertAlmostEqual(values["inclusive"][0], 5.0)
            self.assertAlmostEqual(values["inclusive"][1], 5.0)
            self.assertAlmostEqual(values["inclusive"][2], 1.0)

    def test_wrong_same_sign_factor_is_rejected(self) -> None:
        if self.pyroot is None:
            self.skipTest("PyROOT is unavailable")
        spec = json.loads(
            (ROOT / "config/statistical_robustness_v1.json").read_text()
        )
        pair = robustness.validate_spec(spec, ROOT)[(411, -411)]
        row = {
            "tune": "MONASH",
            "canonical_slot": 0,
            "campaign": "synthetic",
            "raw_sha256": "a" * 64,
            "repository_commit": "b" * 40,
            "producer_executable_sha256": "c" * 64,
            "requested_successes": 2,
        }
        with tempfile.TemporaryDirectory() as temporary:
            per_job = Path(temporary)
            path = per_job / "MONASH/slot_000/DplusDminus.root"
            self._write_pair_file(
                path, pair, row, spec["contracts"], same_sign_factor=0.5
            )
            with self.assertRaisesRegex(ValueError, "same_sign_pair_factor"):
                robustness.inspect_pair_file(
                    path,
                    per_job,
                    row,
                    pair,
                    spec["contracts"],
                    {},
                    {},
                    {},
                )

    def test_wrong_associate_origin_labels_are_rejected(self) -> None:
        if self.pyroot is None:
            self.skipTest("PyROOT is unavailable")
        spec = json.loads(
            (ROOT / "config/statistical_robustness_v1.json").read_text()
        )
        pair = robustness.validate_spec(spec, ROOT)[(411, -411)]
        row = {
            "tune": "MONASH",
            "canonical_slot": 0,
            "campaign": "synthetic",
            "raw_sha256": "a" * 64,
            "repository_commit": "b" * 40,
            "producer_executable_sha256": "c" * 64,
            "requested_successes": 2,
        }
        with tempfile.TemporaryDirectory() as temporary:
            per_job = Path(temporary)
            path = per_job / "MONASH/slot_000/DplusDminus.root"
            self._write_pair_file(
                path,
                pair,
                row,
                spec["contracts"],
                origin_category_labels='{"6":"silently_redefined"}',
            )
            with self.assertRaisesRegex(
                ValueError, "associate_origin_category_labels"
            ):
                robustness.inspect_pair_file(
                    path,
                    per_job,
                    row,
                    pair,
                    spec["contracts"],
                    {},
                    {},
                    {},
                )


if __name__ == "__main__":
    unittest.main()
