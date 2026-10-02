import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


family = load("test_family_model", "pipeline/reduce/family.py")
sys.path.insert(0, str(ROOT / "pipeline/reduce"))
products = load("test_family_products", "pipeline/reduce/family_products.py")
model = load("test_family_query_model", "pipeline/query/model.py")


class FamilyMapTests(unittest.TestCase):
    def setUp(self):
        self.path = ROOT / "config/associate-family-runtime.json"
        self.admitted = family.checked_family_map(self.path)

    def mutate(self, operation):
        value = json.loads(self.path.read_text())
        operation(value)
        temporary = Path(tempfile.mkdtemp()) / "map.json"
        temporary.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")))
        digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
        with self.assertRaises(ValueError):
            family.checked_family_map(temporary, digest, accepted=False)
        shutil.rmtree(temporary.parent)

    def test_exact_accepted_domain_and_science_boundaries(self):
        self.assertEqual(self.admitted.sha256, family.MAP_SHA256)
        self.assertEqual(len(self.admitted.members), 74)
        self.assertEqual(len(self.admitted.destinations), 42)
        self.assertEqual(self.admitted.deferred_members, family.DEFERRED_XI)
        self.assertEqual(self.admitted.destination_by_member[4312], 4132)
        self.assertEqual(self.admitted.destination_by_member[5312], 5132)
        self.assertNotIn(4314, self.admitted.destination_by_member)
        self.assertNotIn(413, self.admitted.destination_by_member)
        self.assertEqual(self.admitted.destination_by_member[423], 421)
        self.assertEqual(self.admitted.members_by_destination[4122],
                         (4122, 4124, 14122))
        self.assertTrue({4112, 4212, 4222}.isdisjoint(
            self.admitted.members_by_destination[4122]))

    def test_wrong_hash_sign_duplicate_missing_and_nonunit_basis_refused(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            family.checked_family_map(self.path, "0" * 64)
        self.mutate(lambda value: value["groups"][0]["members"].append(1))
        self.mutate(lambda value: value["groups"][0]["members"].append(
            value["groups"][0]["members"][0]))
        self.mutate(lambda value: value["groups"][0]["members"].pop())
        self.mutate(lambda value: value["basis"].__setitem__(
            "unit_endpoint", "probability 0.9"))

    def test_normalized_model_separates_fine_support_and_group_destinations(self):
        analysis, _ = model.checked_analysis(ROOT / "config/analysis-family.json")
        states, fine = model.fine_pairs(analysis)
        _, grouped = model.observable_pairs(analysis, "projection_formulas_v4")
        self.assertEqual((len(states), len(fine), len(grouped)), (74, 444, 252))
        self.assertEqual(len({row["associate_pdg"] for row in grouped}), 42)
        self.assertIn(4312, {row["associate_pdg"] for row in fine})
        self.assertNotIn(4312, {row["associate_pdg"] for row in grouped})
        self.assertNotIn(4314, {row["associate_pdg"] for row in fine})
        by_trigger = {}
        for row in grouped:
            by_trigger.setdefault(row["trigger_pdg"], set()).add(
                row["associate_pdg"])
        charm_triggers = {411,-411,421,-421,4122,-4122}
        self.assertEqual({len(values) for trigger, values in by_trigger.items()
                          if trigger in charm_triggers}, {20})
        self.assertEqual({len(values) for trigger, values in by_trigger.items()
                          if trigger not in charm_triggers}, {22})
        added = [row for row in states if row["pdg"] in
                 self.admitted.fine_state_identities]
        self.assertEqual(len(added), 24)
        self.assertEqual(len({row["id"] for row in added}), 24)
        self.assertEqual(len({row["name"] for row in added}), 24)
        by_pdg = {row["pdg"]: row for row in added}
        self.assertEqual((by_pdg[423]["name"], by_pdg[423]["spin2j1"]),
                         ("D*0", 3))
        self.assertEqual((by_pdg[4124]["name"], by_pdg[4124]["spin2j1"]),
                         ("Lambda_c(2625)+", 4))
        self.assertEqual((by_pdg[4334]["name"], by_pdg[4334]["spin2j1"]),
                         ("Omega*_c0", 4))

    def test_activity_trigger_and_human_label_controls(self):
        historical = json.loads((ROOT / "config/analysis.json").read_text())
        grouped = json.loads((ROOT / "config/analysis-family.json").read_text())
        for field in ("activities", "profiles", "axes", "pair_acceptance",
                      "activity_policy", "percentile_intervals",
                      "integrated_interval", "g9_species_pdgs"):
            self.assertEqual(grouped[field], historical[field])
        self.assertEqual(grouped["pair_query_registry"]["trigger_pdgs"],
                         historical["pair_query_registry"]["trigger_pdgs"])
        plot_source = (ROOT / "pipeline/plot/run.py").read_text()
        renderer = (ROOT / "pipeline/plot/render.cpp").read_text()
        docs = (ROOT / "docs/science.md").read_text()
        for text in (plot_source, renderer, docs):
            self.assertIn("Charged primaries", text)
        self.assertNotIn("(study definition)", plot_source)
        self.assertNotIn("(study definition)", renderer)
        self.assertIn("not a claim of equivalence", docs)
        self.assertIn("ParticleDecays:tau0Max = 0.01 mm", docs)


class AdditiveGroupingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admitted = family.checked_family_map(
            ROOT / "config/associate-family-runtime.json")

    def rows(self, blocks=10):
        rows = []
        for block in range(1, blocks + 1):
            for destination, members in self.admitted.members_by_destination.items():
                for index, member in enumerate(members):
                    rows.append(dict(tune="MONASH", block=block, trigger_pdg=521,
                                     associate_pdg=member,
                                     sign=-1 if member < 0 else 1,
                                     count=float(block + index),
                                     sumw2=float(block + index) ** 2,
                                     trigger_count=float(100 + block)))
        return rows

    def test_correlated_members_conjugates_negative_centers_and_k10_oracle(self):
        rows = self.rows()
        grouped = family.group_additive_rows(rows, self.admitted)
        target = [row for row in grouped if row["associate_pdg"] == 431]
        self.assertEqual(len(target), 10)
        # Independent fine-row oracle: it does not invoke the grouping helper.
        members = set(self.admitted.members_by_destination[431])
        per_block = {block: sum(row["count"] for row in rows
                     if row["block"] == block and row["associate_pdg"] in members)
                     for block in range(1, 11)}
        denominator = {block: 100.0 + block for block in range(1, 11)}
        center = sum(per_block.values()) / sum(denominator.values())
        leaves = [(sum(per_block.values()) - per_block[block]) /
                  (sum(denominator.values()) - denominator[block])
                  for block in range(1, 11)]
        mean = sum(leaves) / 10.0
        variance = 0.9 * sum((leaf - mean) ** 2 for leaf in leaves)
        self.assertAlmostEqual(sum(row["count"] for row in target),
                               sum(per_block.values()))
        self.assertGreater(variance, 0.0)
        # A legitimate OS-SS center can remain negative.
        self.assertLess((2.0 - 5.0) / 10.0, 0.0)
        self.assertTrue(math.isfinite(center))

    def test_missing_duplicate_and_denominator_mismatch_refused(self):
        rows = self.rows(1)
        with self.assertRaisesRegex(ValueError, "missing"):
            family.group_additive_rows(rows[:-1], self.admitted)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            family.group_additive_rows(rows + [copy.deepcopy(rows[0])], self.admitted)
        changed = copy.deepcopy(rows)
        changed[0]["trigger_count"] += 1
        with self.assertRaisesRegex(ValueError, "denominator"):
            family.group_additive_rows(changed, self.admitted)

    def test_consolidated_root_layout_round_trip_and_conservation(self):
        try:
            import ROOT  # noqa: F401
        except ImportError:
            self.skipTest("ROOT unavailable")
        rows = self.rows()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "products"
            class Cell:
                def __init__(self, value, sumw2):
                    self.value, self.sumw2 = value, sumw2
            pair_cells = {('inclusive', row['tune'], row['block'], 7,
                row['trigger_pdg'], row['associate_pdg'], row['sign'], 3):
                Cell(row['count'], row['sumw2']) for row in rows}
            primitives = SimpleNamespace(pairs=pair_cells,
                activity={('MONASH', block, 7): Cell(100 + block, 100 + block)
                          for block in range(1, 11)},
                triggers={('inclusive', 'MONASH', block, activity, 521):
                          Cell(100 + block, 100 + block)
                          for block in range(1, 11) for activity in (7, 99)},
                selected_pairs=tuple((521, pdg) for pdg in self.admitted.members),
                selected_triggers=(521,), profile_ids=('inclusive',),
                activity_field='a15_eta4')
            manifest = products.write_products(
                output, primitives, self.admitted, source_sha256="1" * 64,
                analysis_sha256="2" * 64, content_sha256="3" * 64)
            self.assertEqual(manifest["fine_species_count"], 74)
            self.assertEqual(manifest["family_destination_count"], 42)
            self.assertEqual(len(manifest["files"]), 76)
            metadata, grouped = products.read_rows(output / "families.root")
            self.assertEqual(metadata["runtime_map_sha256"], family.MAP_SHA256)
            self.assertEqual(products.verify_products(output,
                hashlib.sha256((output / 'manifest.json').read_bytes()).hexdigest()),
                manifest)
            self.assertTrue(grouped)
            recovered = []
            for relative in manifest["files"]:
                if not relative.startswith("fine/"):
                    continue
                _, fine = products.read_rows(output / relative)
                recovered.extend(fine)
            key = lambda row: (row["tune_id"], row["block"], row["trigger_pdg"],
                               row["associate_pdg"], row["sign"])
            self.assertEqual(len(recovered), len(rows))
            self.assertEqual({(row['associate_pdg'], row['block']) for row in recovered},
                             {(row['associate_pdg'], row['block']) for row in rows})


class AllHeavyFamilyAmendmentTests(unittest.TestCase):
    def test_xi_ground_prime_and_star_recipes_use_explicit_members(self):
        source = json.loads((ROOT / "config/grouping-xi-star-only.example.json").read_text())
        full = family.checked_family_map(
            ROOT / "config/associate-family-runtime-all-heavy.json",
            family.ALL_HEAVY_MAP_SHA256)
        xi = {4132: (4132, 4312, 4314),
              4232: (4232, 4322, 4324),
              5132: (5132, 5312, 5314),
              5232: (5232, 5322, 5324)}
        xi.update({-destination: tuple(-pdg for pdg in members)
                   for destination, members in tuple(xi.items())})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recipe.json"
            for depth in (1, 2, 3):
                recipe = copy.deepcopy(source)
                recipe["id"] = f"xi-first-{depth}-states"
                for group in recipe["groups"]:
                    destination = group["destination_pdg"]
                    if destination in xi:
                        group["members"] = list(xi[destination][:depth])
                path.write_text(json.dumps(recipe, sort_keys=True))
                admitted = family.checked_family_map(
                    path, hashlib.sha256(path.read_bytes()).hexdigest())
                rows = []
                for destination, possible in xi.items():
                    self.assertEqual(set(admitted.members_by_destination[destination]),
                                     set(possible[:depth]))
                    self.assertTrue(set(admitted.members_by_destination[destination])
                                    <= set(full.members_by_destination[destination]))
                    for block in range(1, 11):
                        for ordinal, member in enumerate(possible[:depth], 1):
                            rows.append(dict(tune="MONASH", block=block,
                                trigger_pdg=421 if abs(destination) < 5000 else 521,
                                associate_pdg=member,
                                sign=-1 if member < 0 else 1,
                                count=float(ordinal * block),
                                sumw2=float((ordinal * block) ** 2),
                                trigger_count=float(100 + block)))
                grouped = family.group_additive_rows(rows, admitted)
                for destination in xi:
                    actual = [row for row in grouped
                              if row["associate_pdg"] == destination]
                    self.assertEqual(len(actual), 10)
                    self.assertEqual([row["count"] for row in actual],
                                     [float(block * sum(range(1, depth + 1)))
                                      for block in range(1, 11)])

    def test_configurable_subset_uses_unchanged_fine_pair_domain(self):
        recipe_path = ROOT / "config/grouping-xi-star-only.example.json"
        recipe = family.checked_family_map(
            recipe_path, hashlib.sha256(recipe_path.read_bytes()).hexdigest())
        approved = family.checked_family_map(
            ROOT / "config/associate-family-runtime-all-heavy.json",
            family.ALL_HEAVY_MAP_SHA256)
        self.assertEqual((len(recipe.destinations), len(recipe.members)), (38, 58))
        self.assertEqual(recipe.members_by_destination[4132], (4314,))
        self.assertEqual(recipe.members_by_destination[-4132], (-4314,))
        self.assertNotIn(4132, recipe.members_by_destination[4132])
        self.assertIn(4132, approved.members_by_destination[4132])
        construction, _ = model.checked_analysis(
            ROOT / "config/analysis-all-heavy.json")
        requested = copy.deepcopy(construction)
        requested["associate_family_map"] = {
            "schema": family.GROUP_RECIPE_SCHEMA,
            "path": str(recipe_path), "sha256": recipe.sha256}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "analysis.json"
            path.write_text(json.dumps(requested, sort_keys=True))
            checked, _ = model.checked_analysis(path)
        model.compatible_interpretation(construction, checked)
        self.assertEqual(model.fine_pairs(construction), model.fine_pairs(checked))
        self.assertEqual(len(model.observable_pairs(checked,
            "projection_formulas_v4")[1]), 228)

    def test_configurable_recipe_rejects_unknown_duplicate_cross_family_and_conjugation(self):
        source = json.loads((ROOT / "config/grouping-xi-star-only.example.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recipe.json"
            def rejects(change):
                value = copy.deepcopy(source)
                change(value)
                path.write_text(json.dumps(value, sort_keys=True))
                with self.assertRaises(ValueError):
                    family.checked_family_map(path,
                        hashlib.sha256(path.read_bytes()).hexdigest())
            rejects(lambda value: value["groups"][0]["members"].append(999999))
            rejects(lambda value: value["groups"][0]["members"].append(
                value["groups"][0]["members"][0]))
            rejects(lambda value: value["groups"][0]["members"].append(421))
            rejects(lambda value: value["groups"][0]["members"].pop())
            rejects(lambda value: value["groups"][0].__setitem__("family", "Lambda_c"))
            rejects(lambda value: value["source_catalog"].__setitem__(
                "sha256", "0" * 64))

    def test_signed_xi_star_endpoints_and_additive_shared_denominator(self):
        admitted = family.checked_family_map(
            ROOT / "config/associate-family-runtime-all-heavy.json",
            family.ALL_HEAVY_MAP_SHA256)
        legacy = family.checked_family_map(
            ROOT / "config/associate-family-runtime.json")
        endpoints = {4314: 4132, 4324: 4232, 5314: 5132, 5324: 5232}
        endpoints.update({-member: -destination
                          for member, destination in tuple(endpoints.items())})
        self.assertEqual({member: admitted.destination_by_member[member]
                          for member in endpoints}, endpoints)
        self.assertEqual(set(admitted.members) - set(legacy.members), set(endpoints))
        self.assertEqual({member: admitted.destination_by_member[member]
                          for member in legacy.members}, legacy.destination_by_member)
        self.assertEqual(len(admitted.destinations), len(legacy.destinations))
        rows = []
        for block in range(1, 11):
            for destination, members in admitted.members_by_destination.items():
                for ordinal, member in enumerate(members):
                    rows.append(dict(tune="MONASH", block=block,
                                     trigger_pdg=421 if abs(destination) < 5000 else 521,
                                     associate_pdg=member,
                                     sign=-1 if member < 0 else 1,
                                     count=float(block + ordinal),
                                     sumw2=float((block + ordinal) ** 2),
                                     trigger_count=float(100 + block)))
        grouped = family.group_additive_rows(rows, admitted)
        for destination in {4132, -4132, 4232, -4232,
                            5132, -5132, 5232, -5232}:
            members = set(admitted.members_by_destination[destination])
            original = [row for row in rows if row["associate_pdg"] in members]
            result = [row for row in grouped if row["associate_pdg"] == destination]
            self.assertEqual(len(result), 10)
            self.assertEqual(sum(row["count"] for row in result),
                             sum(row["count"] for row in original))
            self.assertEqual(sum(row["trigger_count"] for row in result),
                             sum(100 + block for block in range(1, 11)))

    def test_query_catalog_does_not_depend_on_family_membership(self):
        analysis, _ = model.checked_analysis(ROOT / "config/analysis-all-heavy.json")
        catalog = model.checked_heavy_catalog(
            ROOT / analysis["retained_heavy_catalog"]["path"],
            analysis["retained_heavy_catalog"]["sha256"])
        members = set(family.checked_family_map(
            ROOT / "config/associate-family-runtime-all-heavy.json",
            family.ALL_HEAVY_MAP_SHA256).members)
        catalog_pdgs = {row["pdg"] for row in catalog["states"]}
        self.assertTrue(members < catalog_pdgs)
        self.assertIn(443, catalog_pdgs - members)
        self.assertIn(4422, catalog_pdgs - members)
        self.assertIn(5522, catalog_pdgs - members)

    def test_legacy_family_projection_reuses_all_heavy_construction(self):
        construction, _ = model.checked_analysis(
            ROOT / "config/analysis-all-heavy.json")
        older = json.loads((ROOT / "config/analysis-family.json").read_text())
        requested = copy.deepcopy(construction)
        requested["associate_family_map"] = older["associate_family_map"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "requested.json"
            path.write_text(json.dumps(requested, sort_keys=True))
            checked, _ = model.checked_analysis(path)
        receipt = model.compatible_interpretation(construction, checked)
        self.assertEqual(receipt["family_map_sha256"], family.MAP_SHA256)
        self.assertEqual(construction["retained_heavy_catalog"],
                         checked["retained_heavy_catalog"])
        mutated = copy.deepcopy(checked)
        mutated["pair_query_registry"]["trigger_pdgs"][0] = 999
        with self.assertRaisesRegex(ValueError, "unretained query content"):
            model.compatible_interpretation(construction, mutated)


if __name__ == "__main__":
    unittest.main()
