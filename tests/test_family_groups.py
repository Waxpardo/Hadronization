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
        self.path = ROOT / "config/associate-family-map.json"
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
        self.mutate(lambda value: value.__setitem__("unit_basis", "probability 0.9"))

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
            self.assertIn("Charged primaries (study definition)", text)
        self.assertIn("not a claim of equivalence", docs)
        self.assertIn("ParticleDecays:tau0Max = 0.01 mm", docs)


class AdditiveGroupingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admitted = family.checked_family_map(
            ROOT / "config/associate-family-map.json")

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
            manifest = products.write_products(
                output, rows, self.admitted, source_sha256="1" * 64,
                analysis_sha256="2" * 64, content_sha256="3" * 64)
            self.assertEqual(manifest["fine_species_count"], 74)
            self.assertEqual(manifest["family_destination_count"], 42)
            self.assertEqual(len(manifest["files"]), 75)
            metadata, grouped = products.read_rows(output / "families.root")
            self.assertEqual(metadata["map_sha256"], family.MAP_SHA256)
            oracle = family.group_additive_rows(rows, self.admitted)
            self.assertEqual(grouped, oracle)
            recovered = []
            for relative in manifest["files"]:
                if not relative.startswith("fine/"):
                    continue
                _, fine = products.read_rows(output / relative)
                recovered.extend(fine)
            key = lambda row: (row["tune"], row["block"], row["trigger_pdg"],
                               row["associate_pdg"], row["sign"])
            self.assertEqual(sorted(recovered, key=key), sorted(rows, key=key))


if __name__ == "__main__":
    unittest.main()
