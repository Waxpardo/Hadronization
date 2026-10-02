"""Exact-row checks for independently retained heavy species."""

from array import array
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from pipeline.query import fine


class FineExactSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import ROOT
        except ImportError:
            raise unittest.SkipTest("ROOT unavailable")
        cls.ROOT = ROOT

    def _tree(self, file, name, columns, rows):
        tree = self.ROOT.TTree(name, name)
        values = {}
        for field, kind in columns.items():
            code, leaf = {"u64": ("Q", "l"), "i": ("i", "I"),
                          "u32": ("I", "i"), "byte": ("B", "b"),
                          "double": ("d", "D")}[kind]
            values[field] = array(code, [0])
            tree.Branch(field, values[field], field + "/" + leaf)
        for row in rows:
            for field, value in row.items():
                values[field][0] = value
            tree.Fill()
        file.cd()
        tree.Write()

    def _source(self, path, *, foreign=False, nonfinite=False):
        file = self.ROOT.TFile(str(path), "RECREATE")
        self._tree(file, "events", {"event_id": "u64", "weight": "double"},
                   [{"event_id": 1, "weight": 2.5}])
        heavy = []
        for identity, pdg, status, final, selected, content in (
                (0, 421, 82, 1, 1, (1, 0)),
                (1, -421, -82, 0, 0, (0, 1)),
                (2, 999 if foreign else -421, 82, 1, 1, (0, 1)),
                (3, 443, 82, 1, 0, (1, 1))):
            heavy.append({"event_id": 1, "heavy_index": identity, "pdg": pdg,
                          "status": status, "final": final, "selected": selected,
                          "pair_eligible": selected, "nc": content[0],
                          "ncbar": content[1], "nb": 0, "nbbar": 0,
                          "pt": float("nan") if nonfinite and identity == 0 else 0.5,
                          "eta": 0.0, "phi": 0.2})
        self._tree(file, "heavy", {"event_id": "u64", "heavy_index": "i",
                   "pdg": "i", "status": "i", "final": "byte",
                   "selected": "byte", "pair_eligible": "byte",
                   "nc": "i", "ncbar": "i", "nb": "i", "nbbar": "i",
                   "pt": "double", "eta": "double", "phi": "double"}, heavy)
        self._tree(file, "triggers", {"event_id": "u64", "heavy_index": "i",
                   "sector": "i", "rejection_mask": "u32"},
                   [{"event_id": 1, "heavy_index": 0, "sector": 4,
                     "rejection_mask": 0}])
        self._tree(file, "event_ranges", {"first_id": "u64", "count": "u64",
                   "source_id": "u32"},
                   [{"first_id": 1, "count": 1, "source_id": 0}])
        file.Close()
        return {"shards": [{"query_root": {"path": str(path)},
                            "members": [{"tune": "MONASH", "block": 1}]}]}

    def test_history_copy_does_not_duplicate_final_particle_or_pair(self):
        catalog = {421: {"nc": 1, "ncbar": 0, "nb": 0, "nbbar": 0},
                   -421: {"nc": 0, "ncbar": 1, "nb": 0, "nbbar": 0},
                   443: {"nc": 1, "ncbar": 1, "nb": 0, "nbbar": 0}}
        with tempfile.TemporaryDirectory() as directory:
            index = self._source(Path(directory) / "support.root")
            observed, final, pairs = fine._exact_rows(index, catalog)
            self.assertEqual(sum(item[0] for item in observed.values()), 4)
            self.assertEqual(sum(item[0] for item in final.values()), 3)
            self.assertEqual(sum(item[0] for item in pairs.values()), 2)
            self.assertEqual(pairs[("MONASH", 1, 421, -421, 82, -1)][1], 2.5)
            self.assertEqual(pairs[("MONASH", 1, 421, 443, 82, 0)][1], 2.5)

    def test_unknown_observed_identity_fails_even_with_pinned_dictionary(self):
        catalog = {421: {"nc": 1, "ncbar": 0, "nb": 0, "nbbar": 0},
                   -421: {"nc": 0, "ncbar": 1, "nb": 0, "nbbar": 0},
                   443: {"nc": 1, "ncbar": 1, "nb": 0, "nbbar": 0}}
        with tempfile.TemporaryDirectory() as directory:
            index = self._source(Path(directory) / "foreign.root", foreign=True)
            with self.assertRaisesRegex(ValueError, "absent from catalog"):
                fine._exact_rows(index, catalog)

    def test_nonfinite_final_kinematics_refused_before_sparse_closure(self):
        catalog = {421: {"nc": 1, "ncbar": 0, "nb": 0, "nbbar": 0},
                   -421: {"nc": 0, "ncbar": 1, "nb": 0, "nbbar": 0},
                   443: {"nc": 1, "ncbar": 1, "nb": 0, "nbbar": 0}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nonfinite.root"
            index = self._source(path, nonfinite=True)
            with self.assertRaisesRegex(ValueError, "kinematics"):
                fine._exact_rows(index, catalog)

    def test_zero_net_heavy_state_cannot_be_relabeled_same_sign(self):
        class Axis:
            def __init__(self, name, label="", center=0):
                self.name, self.label, self.center = name, label, center
            def GetName(self): return self.name
            def GetBinLabel(self, coordinate): return self.label
            def GetNbins(self): return 1
            def GetBinCenter(self, coordinate): return self.center
        names = ("trigger_pdg", "associate_pdg", "sign", "origin", "associate_status")
        axes = [Axis(name, str(421 if name == "trigger_pdg" else 443)
                     if name.endswith("pdg") else "",
                     1 if name == "sign" else -1 if name == "origin" else 82)
                for name in names]
        cell = SimpleNamespace(family="pairs", coordinates=[1] * len(axes),
                               tune="MONASH", block=1, value=1.0, sumw2=1.0)
        class Source:
            index = {"tune_ordinals": [0]}
            def scan(self, families, tunes, callback): callback(cell, axes)
        catalog = {421: {"nc": 1, "ncbar": 0, "nb": 0, "nbbar": 0},
                   443: {"nc": 1, "ncbar": 1, "nb": 0, "nbbar": 0}}
        with self.assertRaisesRegex(ValueError, "flavour sign"):
            fine._fine_cells(Source(), catalog)


if __name__ == "__main__":
    unittest.main()
