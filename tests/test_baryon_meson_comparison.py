"""Fine-species baryon/meson comparison and saved-value rendering."""

import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from pipeline.reduce import baryon_meson_comparison as bm


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("root-config"), "ROOT is required")
class BaryonMesonComparison(unittest.TestCase):
    def test_joint_native_estimator_and_invalid_ratio(self):
        blocks = [[float(i), float(2*i), 100.] for i in range(1, 11)]
        result = bm.estimate(blocks)
        self.assertEqual(float.fromhex(result["Y_B"]["center"]), .055)
        self.assertEqual(float.fromhex(result["Y_M"]["center"]), .11)
        self.assertEqual(float.fromhex(result["R_BM"]["center"]), .5)
        self.assertEqual(float.fromhex(result["D"]["center"]), .055)
        self.assertEqual(float.fromhex(result["R_BM"]["error"]), 0.)
        invalid = bm.estimate([[1., 0., 100.]] * 10)
        self.assertIsNotNone(invalid["Y_B"]["center"])
        self.assertIsNone(invalid["R_BM"]["center"])
        self.assertNotIn(invalid["R_BM"]["uncertainty_status"], bm.AVAILABLE)

    def test_recipe_and_exact_primitives(self):
        recipe = json.loads((ROOT / "config/baryon-meson-comparison.json").read_text())
        bm.checked_recipe(recipe)
        mutant = dict(recipe, ordered_trigger_pdgs=[421, 521])
        with self.assertRaises(ValueError):
            bm.checked_recipe(mutant)
        for rows in ([[1., 2., 3.]] * 9, [[1.5, 2., 3.]] * 10):
            with self.assertRaises(ValueError):
                bm.estimate(rows)

    def test_authenticated_membership_counts_and_classification(self):
        manifest = json.loads((ROOT / "data/results/numerical/family-products/manifest.json").read_text())
        recipe = json.loads((ROOT / "config/baryon-meson-comparison.json").read_text())
        catalog, domains, rows, classification, classification_sha = bm.membership(
            manifest, recipe)
        self.assertEqual(catalog["particle_data_sha256"], bm._catalog(manifest)[0][
            "particle_data_sha256"])
        self.assertEqual(classification["basis"], "particleData.isMeson/isBaryon")
        self.assertEqual(len(classification_sha), 64)
        self.assertEqual({trigger: len(items) for trigger, items in domains.items()},
                         {421:42, 4122:42, 521:59, 5122:59})
        self.assertEqual(len(rows), 202)
        self.assertEqual(sum(row["kind"] == "meson" for row in rows), 84)
        self.assertEqual(sum(row["kind"] == "baryon" for row in rows), 118)
        mutant = [dict(row) for row in rows]
        mutant[0]["kind"] = "baryon" if mutant[0]["kind"] == "meson" else "meson"
        with self.assertRaises(ValueError):
            bm.checked_membership(mutant, {row["pdg"]:row for row in catalog["states"]},
                                  domains)
        with self.assertRaises(ValueError):
            bm.checked_membership(rows[:-1],
                                  {row["pdg"]:row for row in catalog["states"]},
                                  domains)
        wrong_sign = [dict(row) for row in rows]
        wrong_sign[0]["os_pdg"], wrong_sign[0]["ss_pdg"] = (
            wrong_sign[0]["ss_pdg"], wrong_sign[0]["os_pdg"])
        with self.assertRaises(ValueError):
            bm.checked_membership(wrong_sign,
                                  {row["pdg"]:row for row in catalog["states"]},
                                  domains)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "classification.json"
            mutant = copy.deepcopy(classification)
            mutant["states"][0]["kind"] = (
                "baryon" if mutant["states"][0]["kind"] == "meson" else "meson")
            path.write_text(json.dumps(mutant, sort_keys=True), encoding="ascii")
            with mock.patch.object(bm, "CLASSIFICATION", path):
                with self.assertRaisesRegex(ValueError, "classification"):
                    bm.membership(manifest, recipe)

    def _value(self):
        estimate = bm.estimate([[float(i), float(i+10), 100.]
                                for i in range(1, 11)])
        points, blocks = [], []
        for trigger in (421, 4122, 521, 5122):
            for observable in bm.OBSERVABLES:
                points.append(dict(index=len(points), tune="MONASH", trigger_pdg=trigger,
                    sector="charm" if trigger in (421, 4122) else "beauty",
                    species=42 if trigger in (421, 4122) else 59,
                    meson_species=18 if trigger in (421, 4122) else 24,
                    baryon_species=24 if trigger in (421, 4122) else 35,
                    trigger_count=1000., baryon_os=100., baryon_ss=10.,
                    meson_os=200., meson_ss=20., observable=observable,
                    **estimate[observable]))
            blocks.extend(dict(tune="MONASH", trigger_pdg=trigger, block=i,
                trigger_count=100., baryon_os=10., baryon_ss=1.,
                meson_os=20., meson_ss=2., baryon_net=9., meson_net=18.)
                for i in range(1, 11))
        return dict(schema=bm.SCHEMA, derivation_source_sha256=bm.SOURCE_SHA256,
            recipe=json.loads((ROOT / "config/baryon-meson-comparison.json").read_text()),
            points=points, block_primitives=blocks,
            membership=[dict(trigger_pdg=421, sector="charm", os_pdg=-421,
                ss_pdg=421, name="Dbar0", kind="meson", heavy_sign=-1,
                charge3=0)], covariance=[[0.0.hex()] * 16 for _ in range(16)])

    def test_typed_root_roundtrip_and_csv(self):
        value = self._value()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / bm.OBJECT_NAME
            digest = bm.write(value, path)
            self.assertEqual(bm.read(path, digest), value)
            self.assertIn(b"R_BM_error", bm.csv_bytes(dict(value,
                tunes=["MONASH"])))
            with self.assertRaises(FileExistsError):
                bm.write(value, path)

    def test_saved_uncertainty_and_covariance_mutants_are_rejected(self):
        value = self._value()
        with mock.patch.object(bm, "derive", return_value=value):
            changed_error = copy.deepcopy(value)
            changed_error["points"][0]["error"] = (.25).hex()
            with self.assertRaisesRegex(ValueError, "differs"):
                bm.verify(changed_error, {}, "a" * 64, "b" * 64, ".", "c" * 64)
            changed_covariance = copy.deepcopy(value)
            changed_covariance["covariance"][0][1] = (.25).hex()
            with self.assertRaisesRegex(ValueError, "differs"):
                bm.verify(changed_covariance, {}, "a" * 64, "b" * 64, ".", "c" * 64)

    def test_page_has_unshifted_bins_and_requested_titles(self):
        from pipeline.plot import run as plot
        from types import SimpleNamespace
        recipe = json.loads((ROOT / "config/baryon-meson-comparison.json").read_text())
        points = []
        for tune in ("MONASH", "JUNCTIONS", "CLOSEPACKING"):
            for trigger in recipe["ordered_trigger_pdgs"]:
                points.append(dict(tune=tune, trigger_pdg=trigger,
                    observable="R_BM", center=(.5).hex(), error=(.01).hex(),
                    value_status="AVAILABLE", uncertainty_status="AVAILABLE",
                    reasons=[]))
        value = dict(recipe=recipe, tunes=["MONASH", "JUNCTIONS", "CLOSEPACKING"],
                     points=points)
        context = SimpleNamespace(target_analysis_caption="PYTHIA 8.317; pp, #sqrt{s} = 13.6 TeV",
            sample_caption=["Hard heavy-flavour sample"], profile_definition={
                "trigger_eta":{"high":(4.).hex()}, "trigger_pt":{"low":None}})
        config, _ = plot.checked_plot_config(ROOT / "config/plot.json")
        labels = {"421":"D0", "4122":"Lambda_c+", "521":"B+", "5122":"Lambda_b0"}
        page = plot.baryon_meson_comparison_page(
            value, context, {"presentation":{"species_labels":labels}}, config)
        panel = page["panels"][0]
        self.assertEqual(panel["y_title"],
                         "#it{Y}_{#font[42]{Baryon}}/#it{Y}_{#font[42]{Meson}}")
        self.assertEqual(panel["x_title"], "Trigger Species")
        self.assertEqual(panel["y_range"], [0., 1.08])
        self.assertEqual(panel["guides"][0]["line_style"], 3)
        for series in panel["series"]:
            for slot, point in enumerate(series["points"], 1):
                self.assertEqual((point["bin_low"], point["bin_high"]),
                                 (slot-.5, slot+.5))


if __name__ == "__main__":
    unittest.main()
