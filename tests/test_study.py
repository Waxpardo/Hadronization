import json
import math
import re
import unittest

from helpers import ROOT, csv_rows, load_json


def edges(rows, observable, low, high):
    chosen = [row for row in rows if row.get("observable") == observable]
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
        excluded = [state for state in states if not state["central_eligible"]]
        self.assertEqual(len(excluded), 6)
        self.assertEqual({state["pdg"] for state in excluded},
                         {5212, -5212, 5312, -5312, 5322, -5322})
        self.assertTrue(all(state["status"] == "excluded_from_central"
                            and state["reason"] for state in excluded))
        header = (ROOT / "pipeline/generate/selected_states.hpp").read_text(
            encoding="utf-8")
        matches = re.findall(
            r'^\s*\{(-?[0-9]+),\s*"([^"]+)".*\s(true|false)\},$',
            header, re.MULTILINE)
        implementation = {(int(pdg), name, eligible == "true")
                          for pdg, name, eligible in matches}
        configured = {(state["pdg"], state["name"], state["central_eligible"])
                      for state in states}
        self.assertEqual(implementation, configured)

    def test_activity_and_balancing_identity_bijections(self):
        balancing = csv_rows("results/measurement/balancing.csv")
        configured_classes = {
            (row["id"], row["percentile_low"], row["percentile_high"])
            for row in self.study["activity"]["classes"]}
        canonical_classes = {
            (row["activity_id"], row["percentile_low"], row["percentile_high"])
            for row in balancing}
        self.assertEqual(configured_classes, canonical_classes)
        bounds = self.study["activity"]["canonical_realized_nch_bounds"]
        canonical_bounds = {
            (row["tune"], row["activity_id"], int(row["nch_low"]),
             int(row["nch_high"])) for row in balancing}
        configured_bounds = {
            (tune, activity, values["nch_low"], values["nch_high"])
            for tune, tune_rows in bounds.items()
            for activity, values in tune_rows.items()}
        self.assertEqual(configured_bounds, canonical_bounds)
        configured_pairs = {
            (row["flavour"], row["trigger"], row["os_associate"],
             row["ss_associate"]) for row in
            self.study["pair_observable"]["balancing_pairs"]}
        canonical_pairs = {
            (row["flavour"], row["trigger"], row["os_associate"],
             row["ss_associate"]) for row in balancing}
        self.assertEqual(len(configured_pairs), 16)
        self.assertEqual(configured_pairs, canonical_pairs)
        self.assertEqual(
            len(self.study["pair_observable"]["balancing_pairs"]),
            len(configured_pairs))

    def test_all_other_measurement_identities_and_binnings(self):
        correlation = csv_rows("results/measurement/correlations.csv")
        configured_contexts = {
            (tune, pair["flavour"], pair["trigger"], pair["associate"],
             context, pair["activity_id"])
            for tune in self.study["observables"]["correlations"]["tunes"]
            for pair in self.study["observables"]["correlations"]["pairs"]
            for context in pair["contexts"]}
        canonical_contexts = {
            (row["tune"], row["flavour"], row["trigger"], row["associate"],
             row["context"], row["activity_id"]) for row in correlation}
        self.assertEqual(configured_contexts, canonical_contexts)
        corr_axis = self.study["observables"]["correlations"]["delta_phi"]
        self.assertEqual(corr_axis,
                         {"kind": "uniform", "bins": 100,
                          "low": "-1.570796", "high": "4.712389"})

        kinematics = csv_rows("results/measurement/kinematics.csv")
        configured_species = {(row["id"], str(row["pdg"])) for row in
                              self.study["observables"]["inclusive_kinematics"]["species"]}
        canonical_species = {(row["species"], row["pdg"]) for row in kinematics}
        self.assertEqual(configured_species, canonical_species)
        axes = self.study["observables"]["inclusive_kinematics"]["axes"]
        self.assertEqual(axes["pt"]["edges"], edges(kinematics, "pt", "bin_low", "bin_high"))
        for observable in ("eta", "phi"):
            observed = edges(kinematics, observable, "bin_low", "bin_high")
            axis = axes[observable]
            self.assertEqual(len(observed) - 1, axis["bins"])
            self.assertEqual(float(observed[0]), float(axis["low"]))
            self.assertEqual(float(observed[-1]), float(axis["high"]))

        multiplicity = csv_rows("results/measurement/multiplicity.csv")
        mult_axis = self.study["observables"]["multiplicity"]["binning"]
        mult_bins = {(int(row["bin_index"]), row["nch_low"], row["nch_high"])
                     for row in multiplicity}
        self.assertEqual((len(mult_bins), min(mult_bins)[1], max(mult_bins)[2]),
                         (mult_axis["bins"], mult_axis["low"], mult_axis["high"]))

        sample = csv_rows("results/measurement/sample_counts.csv")
        configured_quantities = set(self.study["observables"]["sample_counts"]["quantities"])
        configured_quantities.update(row["id"] for row in
                                     self.study["observables"]["sample_counts"]["signed_species"])
        self.assertEqual(configured_quantities, {row["quantity"] for row in sample})
        configured_t1 = {(row["id"], str(row["pdg"])) for row in
                         self.study["observables"]["sample_counts"]["signed_species"]}
        canonical_t1 = {(row["quantity"], row["pdg"]) for row in sample if row["pdg"]}
        self.assertEqual(configured_t1, canonical_t1)

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


if __name__ == "__main__":
    unittest.main()
