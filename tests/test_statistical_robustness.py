#!/usr/bin/env python3
"""Focused regression tests for the independent robustness cross-check."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
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


class StatisticalFormulaTest(unittest.TestCase):
    def test_predeclared_config_matches_registries(self) -> None:
        spec = json.loads(
            (ROOT / "config/statistical_robustness_v1.json").read_text()
        )
        lookup = robustness.validate_spec(spec, ROOT)
        self.assertEqual(lookup[(411, -411)]["filename"], "DplusDminus.root")
        self.assertEqual(lookup[(521, 5122)]["heavy_sign"], "OS")

    def test_nominal_tune_ratio_canvases_keep_validated_headroom(self) -> None:
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
            _, ranges, _, _ = robustness.validate_boundary_receipt(
                path, spec, ROOT
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
    ) -> None:
        assert self.pyroot is not None
        root = self.pyroot
        path.parent.mkdir(parents=True)
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
            "analysis_schema": contracts["analysis_schema"],
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
            "analysis_macro_sha256": "d" * 64,
            "analysis_repository_commit": "e" * 40,
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
