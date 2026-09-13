import json
import copy
import hashlib
import importlib.util
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from helpers import ROOT, csv_rows, load_json


def validate_references(study):
    states = study["selected_states"]
    by_id = {state["id"]: state for state in states}
    if len(by_id) != len(states):
        raise AssertionError("selected-state ID is not unique")
    for pair in study["pair_observable"]["balancing_pairs"]:
        for field in ("trigger", "os_associate", "ss_associate"):
            identifier = pair[field]
            state = by_id.get(identifier)
            if state is None:
                raise AssertionError("dangling study state reference")
            if state["pdg"] != pair[field + "_pdg"]:
                raise AssertionError("mis-PDG study state reference")
            if state["sector"] != pair["flavour"]:
                raise AssertionError("mis-flavour study state reference")
            if not state["pair_analysis_eligible"]:
                raise AssertionError("ineligible balancing-pair state reference")
    for species in study["observables"]["inclusive_kinematics"]["species"]:
        state = by_id.get(species["id"])
        if state is None or state["pdg"] != species["pdg"]:
            raise AssertionError("dangling or mis-PDG inclusive state reference")


def edges(rows, observable, low, high):
    chosen = [row for row in rows if row.get("axis") == observable and row[low] and row[high]]
    bins = sorted({(int(row["bin_index"]), row[low], row[high]) for row in chosen})
    return [bins[0][1]] + [row[2] for row in bins]


class StudyContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = load_json("config/study.json")

    def test_schema_scope_and_frozen_predicates(self):
        study = self.study
        self.assertEqual(study["schema"], "hadronization_study_v1")
        self.assertEqual(study["scope"]["uncertainty"], "statistical_only")
        self.assertIs(study["scope"]["variation_selection"], False)
        self.assertEqual(study["scope"]["systematic_uncertainty"],
                         "disabled_and_absent")
        activity = study["activity"]["predicate"]
        self.assertEqual(activity, {
            "abs_eta_max": "1.0", "abs_eta_relation": "inclusive",
            "charged": True, "final": True, "heavy_constituent": "none",
            "pt_min_gev": "0.15", "pt_min_relation": "exclusive"})
        trigger = study["selection"]["trigger"]
        associate = study["selection"]["associate"]
        self.assertEqual((trigger["pt_min_gev"], associate["pt_min_gev"]),
                         ("1.0", "0.15"))
        self.assertEqual((trigger["abs_eta_max"], associate["abs_eta_max"]),
                         ("4.0", "4.0"))
        self.assertEqual((trigger["pythia_status_abs_min"],
                          trigger["pythia_status_abs_max"]), (81, 89))
        self.assertEqual(trigger["origin"], "selected_hard_process")
        self.assertEqual(associate["origin"], "unrestricted")
        pair = study["pair_observable"]
        self.assertIs(pair["ordered_conditional_pairs"], True)
        self.assertEqual(pair["sign_definition"], "heavy_flavour_sign")
        self.assertEqual(pair["same_sign_factor"], "1.0")
        self.assertEqual(pair["integration"], "full_delta_phi")
        stats = study["statistics"]
        self.assertEqual(stats["central"], "pooled_complete_sample")
        self.assertEqual(stats["blocks"], 10)
        self.assertEqual(stats["uncertainty"],
                         "sample_stdev(block_estimators)/sqrt(10)")
        self.assertEqual(stats["nonlinear_ratios"], "formed_within_each_block")

    def test_selected_state_membership_and_header_parity(self):
        states = self.study["selected_states"]
        self.assertEqual(len(states), 50)
        self.assertEqual(len({state["pdg"] for state in states}), 50)
        self.assertEqual(len({state["id"] for state in states}), 50)
        excluded = [state for state in states if not state["pair_analysis_eligible"]]
        self.assertEqual(len(excluded), 6)
        self.assertEqual({state["pdg"] for state in excluded},
                         {5212, -5212, 5312, -5312, 5322, -5322})
        self.assertTrue(all(state["status"] == "excluded_from_pair_analysis"
                            and state["reason"] for state in excluded))
        self.assertTrue(all(state["status"] == "pair_analysis"
                            for state in states if state["pair_analysis_eligible"]))
        by_pdg = {state["pdg"]: state["id"] for state in states}
        self.assertEqual(by_pdg[421], "dzero")
        self.assertEqual(by_pdg[-421], "dzerobar")
        self.assertEqual(by_pdg[5122], "lambdab")
        self.assertEqual(by_pdg[-5122], "lambdabbar")
        validate_references(self.study)

    def test_generated_contract_is_exact_full_field_and_tune_parity(self):
        path = ROOT / "pipeline/generate/study_contract.py"
        spec = importlib.util.spec_from_file_location("study_contract_generator", str(path))
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        header = ROOT / "pipeline/generate/study_contract.hpp"
        self.assertEqual(header.read_bytes(), generator.render())
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "study_contract.hpp"
            result = subprocess.run(
                [sys.executable, str(path), "generate", "--output", str(target)],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.read_bytes(), header.read_bytes())
        digest = hashlib.sha256((ROOT / "config/study.json").read_bytes()).hexdigest()
        self.assertIn('kStudyDefinitionSha256 = "{}"'.format(digest),
                      header.read_text(encoding="utf-8"))
        for state in self.study["selected_states"]:
            for field in ("id", "name", "sector", "kind", "valence", "status"):
                self.assertIn(json.dumps(str(state[field])), header.read_text(encoding="utf-8"))
        for tune in self.study["tunes"]:
            self.assertIn(json.dumps(tune["name"]), header.read_text(encoding="utf-8"))
            self.assertIn(json.dumps(tune["card"]), header.read_text(encoding="utf-8"))

    def test_generated_contract_check_rejects_any_field_or_digest_drift(self):
        header = (ROOT / "pipeline/generate/study_contract.hpp").read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "study_contract.hpp"
            target.write_bytes(header.replace(b'"dzero"', b'"dzero_DRIFT"', 1))
            result = subprocess.run(
                [sys.executable, str(ROOT / "pipeline/generate/study_contract.py"),
                 "check", "--output", str(target)], text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stale", result.stderr)
            target.write_bytes(header.replace(b"kStudyDefinitionSha256 = \"",
                                              b"kStudyDefinitionSha256 = \"0", 1))
            result = subprocess.run(
                [sys.executable, str(ROOT / "pipeline/generate/study_contract.py"),
                 "check", "--output", str(target)], text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(result.returncode, 0)
            target.write_bytes(header.replace(b"  return -1;", b"  return 0;", 1))
            result = subprocess.run(
                [sys.executable, str(ROOT / "pipeline/generate/study_contract.py"),
                 "check", "--output", str(target)], text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stale", result.stderr)

    def test_reference_gate_rejects_dangling_and_mis_pdg_states(self):
        dangling = copy.deepcopy(self.study)
        dangling["pair_observable"]["balancing_pairs"][0]["trigger"] = "missing"
        with self.assertRaisesRegex(AssertionError, "dangling"):
            validate_references(dangling)
        wrong = copy.deepcopy(self.study)
        wrong["pair_observable"]["balancing_pairs"][0]["trigger_pdg"] = 999
        with self.assertRaisesRegex(AssertionError, "mis-PDG"):
            validate_references(wrong)

    def test_activity_and_balancing_export_identities(self):
        balancing = csv_rows("results/numerical/balancing.csv")
        manifest = load_json("results/numerical/manifest.json")
        exported_classes = {
            (int(row["class_id"]), float(row["percentile_low"]),
             float(row["percentile_high"])) for row in balancing
            if row["profile"] == "inclusive" and
            row["activity_id"] == "charged_light_sector_activity_a15_v1_eta1"}
        compact_classes = {
            (row["id"], float(row["percentile_interval"][0]),
             float(row["percentile_interval"][1]))
            for row in manifest["compact_input"]["scale"]["class_dictionary"]}
        configured_intervals = {
            (float(row["percentile_low"]), float(row["percentile_high"]))
            for row in self.study["activity"]["classes"]}
        self.assertEqual(exported_classes, compact_classes)
        self.assertEqual(configured_intervals,
                         {(low, high) for unused, low, high in compact_classes})
        self.assertEqual({row["tune"] for row in balancing},
                         {row["name"] for row in self.study["tunes"]})
        self.assertEqual({row["quantity"] for row in balancing}, {
            "ordered_pair_yield", "os_minus_ss_per_trigger", "ratio_to_reference_tune",
            "baryon_meson_reference_ratio", "baryon_meson_ratio_to_reference_tune"})
        selected = ({int(row["trigger_pdg"]) for row in balancing} |
                    {int(row["associate_pdg"]) for row in balancing})
        self.assertEqual(selected, {
            -5122, -4122, -521, -511, -421, -411,
            411, 421, 511, 521, 4122, 5122})

    def test_all_other_numerical_export_identities_and_binnings(self):
        correlation = csv_rows("results/numerical/correlations.csv")
        by_id = {state["id"]: state["pdg"] for state in self.study["selected_states"]}
        configured_pairs = {
            (by_id[pair["trigger"]], by_id[pair["associate"]])
            for pair in self.study["observables"]["correlations"]["pairs"]}
        exported_pairs = {
            (int(row["trigger_pdg"]), int(row["associate_pdg"]))
            for row in correlation if row["profile"] == "inclusive"}
        self.assertEqual(configured_pairs, exported_pairs)
        self.assertEqual({row["component"] for row in correlation},
                         {"OS", "SS", "OS_MINUS_SS"})
        groups = {}
        for row in correlation:
            key = tuple(row[field] for field in (
                "tune", "profile", "activity_id", "class_id",
                "trigger_pdg", "associate_pdg", "component"))
            groups.setdefault(key, []).append(row)
        self.assertTrue(all(len(rows) == 100 for rows in groups.values()))
        corr_axis = self.study["observables"]["correlations"]["delta_phi"]
        self.assertEqual(corr_axis,
                         {"kind": "uniform", "bins": 100,
                          "low": "-1.570796", "high": "4.712389"})
        example = sorted(next(iter(groups.values())), key=lambda row: int(row["bin_index"]))
        self.assertTrue(math.isclose(float(example[0]["bin_low"]), float(corr_axis["low"]),
                                     abs_tol=1e-6))
        self.assertTrue(math.isclose(float(example[-1]["bin_high"]), float(corr_axis["high"]),
                                     abs_tol=1e-6))

        kinematics = csv_rows("results/numerical/kinematics.csv")
        configured_species = {str(row["pdg"]) for row in
                              self.study["observables"]["inclusive_kinematics"]["species"]}
        self.assertEqual(configured_species, {row["associate_pdg"] for row in kinematics})
        axes = self.study["observables"]["inclusive_kinematics"]["axes"]
        representative = [row for row in kinematics
                          if row["tune"] == "MONASH" and row["associate_pdg"] == "411"]
        self.assertEqual([float(value) for value in axes["pt"]["edges"]],
                         [float(value) for value in edges(
                             representative, "pt", "bin_low", "bin_high")])
        for observable in ("eta", "phi"):
            observed = edges(representative, observable, "bin_low", "bin_high")
            axis = axes[observable]
            self.assertEqual(len(observed) - 1, axis["bins"])
            self.assertTrue(math.isclose(float(observed[0]), float(axis["low"]),
                                         abs_tol=1e-6))
            self.assertTrue(math.isclose(float(observed[-1]), float(axis["high"]),
                                         abs_tol=1e-6))

        multiplicity = csv_rows("results/numerical/multiplicity.csv")
        mult_axis = self.study["observables"]["multiplicity"]["binning"]
        representative = [row for row in multiplicity
                          if row["tune"] == "MONASH" and
                          row["activity_id"] == "charged_light_sector_activity_a15_v1_eta1" and
                          row["quantity"] == "normalized_distribution"]
        self.assertEqual(len(representative), mult_axis["bins"])
        self.assertEqual({int(row["bin_index"]) for row in representative}, set(range(4096)))

        sample = csv_rows("results/numerical/sample_counts.csv")
        configured_t1 = {str(row["pdg"]) for row in
                         self.study["observables"]["sample_counts"]["signed_species"]}
        exported_t1 = {row["associate_pdg"] for row in sample
                       if row["component"] == "hadron_count"}
        self.assertLessEqual(configured_t1, exported_t1)
        self.assertEqual({row["quantity"] for row in sample}, {"exact_t1_count"})
        self.assertEqual({row["component"] for row in sample}, {
            "hadron_count", "charm_plus_anticharm_constituent_count",
            "beauty_plus_antibeauty_constituent_count"})

    def test_no_selectable_variation_structure(self):
        forbidden_keys = {"variations", "variation_modes", "systematics_selector"}
        stack = [self.study]
        seen = set()
        while stack:
            value = stack.pop()
            if isinstance(value, dict):
                seen.update(value)
                stack.extend(value.values())
            elif isinstance(value, list):
                stack.extend(value)
        self.assertTrue(forbidden_keys.isdisjoint(seen))
        path = ROOT / "pipeline/generate/study_contract.py"
        spec = importlib.util.spec_from_file_location("nominal_structure_gate", str(path))
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        mutated = copy.deepcopy(self.study)
        mutated["variations"] = [{"id": "forbidden_reintroduction"}]
        with self.assertRaisesRegex(ValueError, "selectable variation"):
            generator.validate(mutated)


if __name__ == "__main__":
    unittest.main()
