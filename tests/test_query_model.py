"""One axis-aware released selection model for every public query route."""

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("released_query_model", ROOT / "pipeline/query/model.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class ReleasedQueryModel(unittest.TestCase):
    def setUp(self):
        self.analysis = json.loads((ROOT / "config/analysis.json").read_text())
        self.edges = self.analysis["axes"]["pt"]["edges"]

    def test_all_selected_pair_scope_preserves_frozen_eligibility(self):
        states, original = model.state_registry(self.analysis)
        broad_states, broad = model.observable_pairs(self.analysis, 'projection_formulas_v4')
        _, earlier = model.observable_pairs(self.analysis, 'projection_formulas_v3')
        self.assertEqual(broad_states, states)
        self.assertEqual(broad, original)
        self.assertEqual(len(broad), 300)
        excluded = {5212, -5212, 5312, -5312, 5322, -5322}
        self.assertEqual({s['pdg'] for s in states if not s['pair_analysis_eligible']}, excluded)
        self.assertFalse(excluded & {p['associate_pdg'] for p in earlier})
        self.assertTrue(excluded <= {p['associate_pdg'] for p in broad})
        with self.assertRaisesRegex(ValueError, 'unknown numerical'):
            model.observable_pairs(self.analysis, 'unbound-policy')

    def test_same_query_bytes_admit_inclusive_and_two_aligned_rectangles(self):
        profiles = copy.deepcopy(self.analysis["profiles"])
        profiles.append({"id": "second_rectangle", "trigger_pt": {"operator": ">=", "value": 2.5},
                         "associate_pt": {"operator": ">=", "value": 0.5}, "relative_pt": None})
        self.assertEqual(model.validate_phase_a_profiles(profiles, self.edges), profiles)
        normalized = model.load_normalized(ROOT / "config/analysis.json")
        self.assertEqual(normalized.sha256, model.support.sha_file(ROOT / "config/analysis.json"))
        self.assertEqual(normalized.profile("inclusive")["trigger_pt"], None)
        self.assertEqual(normalized.to_dict(), self.analysis)
        with self.assertRaises(TypeError):
            normalized.analysis["axes"] = {}
        with self.assertRaises(TypeError):
            normalized.profile("inclusive")["id"] = "changed"

    def test_d0_default_dplus_alternate_and_archived_v2_are_distinct(self):
        current = self.analysis
        self.assertEqual(current["version"], "2.2.0")
        self.assertEqual(current["profiles"], [{"id": "inclusive", "trigger_pt": None,
                                                "associate_pt": None, "relative_pt": None}])
        self.assertIn("G9_direct_primary_selected_no_pt_floor_eta4", current["projection_recipes"])
        self.assertEqual(current["paper_defaults"], {
            "charm_meson_pdg": 421, "selectable_charm_meson_pdgs": [421, 411],
            "historical_charm_meson_pdg": 411,
            "p8_charm_tuple": [421, -4122, -421]})
        registry = current["pair_query_registry"]
        for species in (421, 411):
            for signed in (species, -species):
                self.assertIn(signed, registry["trigger_pdgs"])
                self.assertIn(signed, registry["associate_pdgs"]["charm"])
        self.assertEqual(len(current["g9_species_pdgs"]), 10)
        self.assertIn(421, current["g9_species_pdgs"])
        self.assertIn(-421, current["g9_species_pdgs"])
        self.assertNotIn(411, current["g9_species_pdgs"])
        self.assertEqual(registry["reference_meson_by_trigger"]["4122"], -421)
        self.assertEqual(registry["reference_meson_by_trigger"]["-4122"], 421)
        self.assertEqual(current["correlations"]["identities"][2:],
                         [[421, -421], [4122, -421]])
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "analysis.json"
            legacy = copy.deepcopy(current)
            legacy["version"] = "2.0.0"
            legacy.pop("paper_defaults")
            legacy["profiles"].append({"id": "historical_rectangle",
                "trigger_pt": {"operator": ">=", "value": 1.0},
                "associate_pt": {"operator": ">=", "value": 0.15}, "relative_pt": None})
            legacy["projection_recipes"][1] = "G9_direct_primary_selected_strict_pt0p15_eta4"
            legacy["pair_query_registry"]["reference_meson_by_trigger"].update({
                "4122": -411, "-4122": 411})
            legacy["correlations"]["identities"][2:] = [[411, -411], [4122, -411]]
            legacy["g9_species_pdgs"] = sorted({pdg for pdg in legacy["g9_species_pdgs"]
                                                 if abs(pdg) != 421} | {-411, 411})
            path.write_text(json.dumps(legacy))
            self.assertEqual(model.checked_analysis(path)[0]["version"], "2.0.0")
            alternate = model.select_charm_meson_recipe(current, 411)
            path.write_text(json.dumps(alternate))
            self.assertEqual(model.checked_analysis(path)[0]["paper_defaults"]["p8_charm_tuple"],
                             [411, -4122, -411])
            self.assertEqual(alternate["pair_query_registry"]["reference_meson_by_trigger"]["4122"], -411)
            self.assertEqual(alternate["correlations"]["identities"][2:], [[411, -411], [4122, -411]])
            self.assertEqual(len(alternate["g9_species_pdgs"]), 10)
            both = model.select_charm_meson_recipe(current, 421, include_alternate_g9=True)
            path.write_text(json.dumps(both))
            self.assertEqual(len(model.checked_analysis(path)[0]["g9_species_pdgs"]), 12)
            for malformed in ([-421, 421, 411], [-421, 421, 999999]):
                changed = copy.deepcopy(current)
                changed["g9_species_pdgs"] = sorted(set(changed["g9_species_pdgs"]) | set(malformed))
                path.write_text(json.dumps(changed))
                with self.assertRaises(ValueError):
                    model.checked_analysis(path)
            mismatched = copy.deepcopy(alternate)
            mismatched["pair_query_registry"]["reference_meson_by_trigger"]["4122"] = -421
            path.write_text(json.dumps(mismatched))
            with self.assertRaises(ValueError):
                model.checked_analysis(path)
            for wrong in ({"charm_meson_pdg": 411,
                           "selectable_charm_meson_pdgs": [421, 411],
                           "historical_charm_meson_pdg": 411,
                           "p8_charm_tuple": [421, -4122, -421]},
                          {"charm_meson_pdg": 421,
                           "selectable_charm_meson_pdgs": [421],
                           "historical_charm_meson_pdg": 411,
                           "p8_charm_tuple": [421, -4122, -421]}):
                changed = copy.deepcopy(current)
                changed["paper_defaults"] = wrong
                path.write_text(json.dumps(changed))
                with self.assertRaises(ValueError):
                    model.checked_analysis(path)

    def test_axisless_offedge_diagonal_and_strict_release_refuse(self):
        for minima in ((1.1, 0.5), (2.5, 0.15 + 1e-10)):
            request = copy.deepcopy(self.analysis)
            request["profiles"].append({"id": "offedge_rectangle",
                "trigger_pt": {"operator": ">=", "value": minima[0]},
                "associate_pt": {"operator": ">=", "value": minima[1]}, "relative_pt": None})
            with self.assertRaises(ValueError):
                model.primitive_routes(request, self.analysis, "auto")
            with tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "analysis.json"
                path.write_text(json.dumps(request))
                with self.assertRaises(ValueError):
                    model.checked_analysis(path)
        with self.assertRaisesRegex(ValueError, "requires a finite ordered pT axis"):
            model.validate_phase_a_profiles(self.analysis["profiles"])
        diagonal = copy.deepcopy(self.analysis["profiles"])
        diagonal.append({"id": "diagonal", "trigger_pt": None,
                         "associate_pt": None, "relative_pt": "trigger_pt>=associate_pt"})
        with self.assertRaisesRegex(ValueError, "eventwise relative"):
            model.validate_phase_a_profiles(diagonal, self.edges)
        strict = copy.deepcopy(self.analysis["profiles"])
        strict.append({"id": "strict", "trigger_pt": {"operator": ">", "value": 1.0},
                       "associate_pt": {"operator": ">=", "value": 0.15}, "relative_pt": None})
        with self.assertRaisesRegex(ValueError, "released"):
            model.validate_phase_a_profiles(strict, self.edges)

    def test_equal_configured_minima_and_independent_particle_values(self):
        profile = {"id": "equal_minima", "trigger_pt": {"operator": ">=", "value": 0.5},
                   "associate_pt": {"operator": ">=", "value": 0.5}, "relative_pt": None}
        self.assertEqual(model.validate_phase_a_profiles(self.analysis["profiles"] + [profile], self.edges)[-1], profile)
        self.assertEqual(model.profile_tokens(profile), [">=0.5", ">=0.5", "NONE"])
        with tempfile.TemporaryDirectory() as temporary:
            request = copy.deepcopy(self.analysis)
            request["profiles"].append(profile)
            path = Path(temporary) / "optional-analysis.json"
            path.write_text(json.dumps(request))
            self.assertEqual(model.checked_analysis(path)[0]["profiles"][-1], profile)
        ordered = {**profile, "id": "ordered_minima", "trigger_pt": {"operator": ">=", "value": 1.0},
                   "associate_pt": {"operator": ">=", "value": 0.15}}
        self.assertEqual(model.profile_tokens(ordered), [">=1.0", ">=0.15", "NONE"])

    def test_postquery_compatibility_is_content_based_and_rejects_mutants(self):
        requested = copy.deepcopy(self.analysis)
        requested['profiles'].append({'id': 'equal_minima',
            'trigger_pt': {'operator': '>=', 'value': 1.0},
            'associate_pt': {'operator': '>=', 'value': 1.0},
            'relative_pt': None})
        requested['percentile_intervals'] = [[0, 10], [10, 50], [50, 100]]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'request.json'
            path.write_text(json.dumps(requested))
            verified, _ = model.checked_analysis(path)
        compatible = model.compatible_interpretation(self.analysis, verified)
        self.assertEqual(compatible['profile_ids'], ['inclusive', 'equal_minima'])
        self.assertEqual(compatible['percentile_intervals'], [[0, 10], [10, 50], [50, 100]])
        for field, mutate in (
                ('axes', lambda x: x['pt']['edges'].__setitem__(1, 0.16)),
                ('g9_species_pdgs', lambda x: x.__setitem__(0, -9999)),
                ('pair_query_registry', lambda x: x['trigger_pdgs'].__setitem__(0, 9999)),
                ('activities', lambda x: x[0].__setitem__('physical_field', 'missing')),
                ('lossless_input', lambda x: x.__setitem__('schema_digest', '0'*64))):
            changed = copy.deepcopy(verified)
            mutate(changed[field])
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                model.compatible_interpretation(self.analysis, changed)
        for trigger, associate in ((-1., 0.5), (1.1, 0.5), (0.5, 1.0)):
            changed = copy.deepcopy(verified)
            changed['profiles'][-1]['trigger_pt']['value'] = trigger
            changed['profiles'][-1]['associate_pt']['value'] = associate
            with self.subTest(minima=(trigger, associate)), self.assertRaises(ValueError):
                model.compatible_interpretation(self.analysis, changed)


if __name__ == "__main__":
    unittest.main()
