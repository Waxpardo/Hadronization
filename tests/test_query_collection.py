"""Cold locator and bounded physical merge tests on immutable TEST_ONLY ROOT bytes."""

import copy
import importlib.util
import json
import math
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
FIXTURE = ROOT_DIR / "tests/fixtures/query_multitune"


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT_DIR / "pipeline/query" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c = load("tested_query_collection", "collection.py")
m = load("tested_query_merge", "merge.py")


class QueryCollectionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            c._root()
        except ImportError as error:
            raise unittest.SkipTest(str(error))
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name)
        cls.workspaces = sorted((FIXTURE / "queries").glob("shard-*"))
        cls.pins = [json.loads((ws / "manifest.json").read_text())["scientific_content_sha256"]
                    for ws in cls.workspaces]
        cls.sources = json.loads((FIXTURE / "expected-sources.json").read_text())
        cls.index_path = cls.base / "sharded.json"
        cls.sharded = c.create(cls.workspaces, cls.pins, cls.sources,
                               cls.index_path, cls.base / "build", test_only=True)
        cls.merged_path = m.merge(cls.index_path, c.r.sha_file(cls.index_path), cls.base / "merged")
        cls.merged = c.read(cls.merged_path, c.r.sha_file(cls.merged_path))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_ten_original_blocks_three_tunes_local_id_collision_and_streaming_support(self):
        index = c.read(self.index_path, c.r.sha_file(self.index_path))
        self.assertEqual(index["layout"], "SHARDED")
        self.assertEqual(index["state"], "TEST_ONLY")
        self.assertEqual(len(index["sources"]), 30)
        for tune in index["tune_ordinals"]:
            self.assertEqual({x["block"] for x in index["sources"] if x["tune"] == tune},
                             set(range(1, 11)))
        ROOT = c._root()
        local_ids = []
        for shard in index["shards"]:
            file = ROOT.TFile.Open(shard["query_root"]["path"])
            local_ids.append([int(row.source_id) for row in file.Get("sources")])
            file.Close()
        self.assertEqual(local_ids, [list(range(10))] * 3)
        self.assertEqual(len(list(c.iter_support(index, "events"))), 90)
        self.assertEqual(len(list(c.iter_support(index, "triggers"))), 150)
        self.assertEqual(index["scientific_identity_sha256"], self.merged["scientific_identity_sha256"])

    def test_native_parent_lineage_maps_exact_source_selection_on_both_layouts(self):
        sharded = c.source_lineage(self.index_path, c.r.sha_file(self.index_path))
        merged = c.source_lineage(self.merged_path, c.r.sha_file(self.merged_path))
        selection = sharded["source_selection"]
        self.assertEqual(sharded["schema"], "hadronization_query_collection_source_lineage_v1")
        self.assertEqual(selection, merged["source_selection"])
        self.assertEqual(len(selection["members"]), 30)
        self.assertEqual([member["source_id"] for member in selection["members"]], list(range(30)))
        self.assertEqual([count["count"] for count in selection["expected_events_by_tune"]], [30]*3)
        self.assertEqual(len(selection["provenance_parent_ids"]), 3)
        receipt = json.loads((self.workspaces[0] / "metadata.json").read_text())["input_receipt"]
        row = receipt["sources"][0]["manifest_row"]
        member = selection["members"][0]
        self.assertEqual(member["source_root_sha256"], row["raw_sha256"])
        self.assertEqual(member["receipt_sha256"], row["validation_receipt_sha256"])
        self.assertEqual(member["source_scientific_digest"],
                         c.r.sha_bytes(c.r.canonical(row).encode("ascii")))
        self.assertEqual(sharded["source_selection_digest_semantics"], "LEGACY_MANIFEST_ROW_SHA256")
        self.assertEqual(sharded["analyzed_source_scientific_content_digests"][0][
            "analyzed_source_scientific_digest"],
            receipt["scientific_identity"]["source_scientific_digests"][0])
        self.assertNotEqual(member["source_scientific_digest"],
                            sharded["analyzed_source_scientific_content_digests"][0][
                                "analyzed_source_scientific_digest"])
        self.assertEqual(sharded["accepted_raw_producer_commit"],
                         receipt["scientific_identity"]["lossless_dependency_identity"][
                             "accepted_raw_definition"]["producer_repository_commit"])
        one_tune = c.source_lineage(self.merged_path, c.r.sha_file(self.merged_path), ["MONASH"])
        self.assertEqual(len(one_tune["source_selection"]["members"]), 10)
        with self.assertRaises(ValueError):
            c.source_lineage(self.index_path, c.r.sha_file(self.index_path), ["FOREIGN"])

    def test_admission_closure_preserves_test_only_and_refuses_subset_or_ledger(self):
        expected_path = FIXTURE / "expected-sources.json"
        expected_sha = c.r.sha_file(expected_path)
        for path in (self.index_path, self.merged_path):
            proof = c.admission_closure(path, c.r.sha_file(path), expected_path, expected_sha)
            self.assertEqual(proof["schema"], c.ADMISSION_SCHEMA)
            self.assertEqual(proof["qualification"], "TEST_ONLY_DOMAIN_CLOSED")
            self.assertEqual(proof["index_state"], "TEST_ONLY")
            self.assertTrue(proof["domain_complete"])
            self.assertEqual(proof["source_count"], 30)
            self.assertEqual(proof["event_count"], 90)
            self.assertEqual(proof["per_tune_source_event_counts"], [
                {"tune": tune, "sources": 10, "events": 30}
                for tune, _ in sorted(self.sharded["tune_ordinals"].items(), key=lambda item: item[1])])
            natural = [[m["source_id"], m["tune"], m["logical_id"], m["block"], m["events"]]
                       for m in self.sources]
            self.assertEqual(proof["natural_members_sha256"],
                             c.r.sha_bytes(c.r.canonical(natural).encode("ascii")))
            self.assertIsNone(proof["work_sha256"])
        subset = self.base / "subset-sources.json"
        subset.write_text(json.dumps(self.sources[:-1]))
        with self.assertRaisesRegex(ValueError, "exact expected source membership"):
            c.admission_closure(self.index_path, c.r.sha_file(self.index_path),
                                subset, c.r.sha_file(subset))
        with self.assertRaisesRegex(ValueError, "both site work and collector"):
            c.admission_closure(self.index_path, c.r.sha_file(self.index_path),
                                expected_path, expected_sha,
                                work_path=self.base / "forged-ledger.json",
                                expected_work_sha256="a" * 64)

    def test_simulated_full_domain_requires_pinned_work_and_exact_parent_facts(self):
        # Synthetic local qualification only; no production or site admission.
        expected_path = FIXTURE / "expected-sources.json"
        expected_sha = c.r.sha_file(expected_path)
        index = copy.deepcopy(self.sharded)
        index["state"] = "EXTERNAL_ACCEPTANCE_REQUIRED"
        index_path = self.base / "simulated-external-index.json"
        index_path.write_text(json.dumps(index))
        index_sha = c.r.sha_file(index_path)
        work = {"schema": "hadronization_condor_query_work_v1", "state": "SITE_BOUND",
                "storage_semantics": "POSIX_NOOVERWRITE_VERIFIED",
                "expected_sources_sha256": expected_sha,
                "campaign_id": index["campaign"],
                "source_manifest_sha256": index["manifest_sha256"],
                "analysis_sha256": index["analysis_sha256"],
                "layout_sha256": index["layout_sha256"],
                "tune_ordinals": index["tune_ordinals"], "block_count": index["block_count"],
                "expected_source_count": 30, "expected_event_count": 90,
                "campaign_sha256": "a" * 64,
                "acquisition_manifest_sha256": "b" * 64,
                "site_admission_sha256": "c" * 64, "work": []}
        for shard in index["shards"]:
            metadata = c.r.json_file(Path(shard["metadata"]["path"]))
            work["work"].append({"ordinal": shard["ordinal"],
                                 "root": {"sha256": metadata["input_root_sha256"],
                                          "bytes": metadata["admission_build"]["root_bytes"]},
                                 "receipt": {"sha256": metadata["input_receipt_sha256"]}})
        work["input_file_count"] = 2 * len(work["work"])
        work["input_root_bytes"] = sum(item["root"]["bytes"] for item in work["work"])
        work_path = self.base / "simulated-site-work.json"
        closure_path = self.base / "simulated-collector-closure.json"
        def write_proofs():
            work_path.write_text(json.dumps(work))
            closure = {"schema": "hadronization_query_collection_closure_v1",
                       "state": "EXTERNALLY_PINNED", "work_sha256": c.r.sha_file(work_path),
                       "index_sha256": index_sha,
                       "scientific_identity_sha256": index["scientific_identity_sha256"],
                       "source_count": 30, "event_count": 90,
                       "external_pins_sha256": "d" * 64}
            closure_path.write_text(json.dumps(closure))
            return c.r.sha_file(work_path), c.r.sha_file(closure_path)
        work_sha, closure_sha = write_proofs()
        proof = c.admission_closure(index_path, index_sha, expected_path, expected_sha,
                                    work_path=work_path, expected_work_sha256=work_sha,
                                    closure_path=closure_path, expected_closure_sha256=closure_sha)
        self.assertEqual(proof["qualification"], "FULL_ACCEPTED_DOMAIN_CLOSED")
        self.assertEqual(proof["natural_members_sha256"],
                         c.admission_closure(self.index_path, c.r.sha_file(self.index_path),
                                             expected_path, expected_sha)["natural_members_sha256"])
        work["work"][0]["root"]["sha256"] = "e" * 64
        work_sha, closure_sha = write_proofs()
        with self.assertRaisesRegex(ValueError, "analyzed shard facts"):
            c.admission_closure(index_path, index_sha, expected_path, expected_sha,
                                work_path=work_path, expected_work_sha256=work_sha,
                                closure_path=closure_path, expected_closure_sha256=closure_sha)
        work["work"][0]["root"]["sha256"] = c.r.json_file(
            Path(index["shards"][0]["metadata"]["path"]))["input_root_sha256"]
        work["expected_event_count"] = 300000000
        work_sha, closure_sha = write_proofs()
        with self.assertRaisesRegex(ValueError, "exact query campaign domain"):
            c.admission_closure(index_path, index_sha, expected_path, expected_sha,
                                work_path=work_path, expected_work_sha256=work_sha,
                                closure_path=closure_path, expected_closure_sha256=closure_sha)

    def test_sharded_and_merged_cells_entries_and_sumw2_agree(self):
        ROOT = c._root()
        for family in c.FAMILIES:
            for tune, ordinal in self.sharded["tune_ordinals"].items():
                expected = {}
                entries = 0
                for shard in self.sharded["shards"]:
                    file = ROOT.TFile.Open(shard["query_root"]["path"])
                    hist = file.Get("sparse_" + family)
                    entries += hist.GetEntries() if len({x["tune"] for x in shard["members"]}) == 1 and shard["members"][0]["tune"] == tune else 0
                    for coord, value, variance in c._cells(hist):
                        if coord[0] == ordinal + 1:
                            old = expected.get(coord, (0.0, 0.0))
                            expected[coord] = (old[0] + value, old[1] + variance)
                    file.Close()
                part = next(p for p in self.merged["partitions"] if p["tune"] == tune)
                file = ROOT.TFile.Open(part["root"]["path"])
                hist = file.Get("sparse_" + family)
                actual = {coord: (value, variance) for coord, value, variance in c._cells(hist)}
                self.assertEqual(set(expected), set(actual), (family, tune))
                for coord in expected:
                    self.assertTrue(all(math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
                                        for a, b in zip(expected[coord], actual[coord])), (family, tune, coord))
                self.assertEqual(hist.GetEntries(), entries)
                file.Close()

    def test_missing_duplicate_foreign_source_and_missing_support_refuse(self):
        for mutant in (self.sources[:-1], self.sources + self.sources[:1],
                       [dict(self.sources[0], source_id=999)] + self.sources[1:]):
            with self.assertRaisesRegex(ValueError, "membership|duplicate"):
                c.create(self.workspaces, self.pins, mutant,
                         self.base / "missing-index.json", self.base / "build", test_only=True)
        altered = self.base / "without-support.root"
        shutil.copy2(self.workspaces[0] / "query.root", altered)
        ROOT = c._root()
        file = ROOT.TFile.Open(str(altered), "UPDATE")
        file.Delete("constituents;*")
        file.Close()
        index = copy.deepcopy(self.sharded)
        index["shards"][0]["query_root"] = c._fact(altered)
        path = self.base / "missing-support.json"
        c.r.atomic_json(path, index, exclusive=True)
        with self.assertRaisesRegex(ValueError, "required exact support"):
            c.read(path, c.r.sha_file(path))

    def test_relocation_changes_locator_only(self):
        new_root = self.base / "relocated-query.root"
        shutil.copy2(self.workspaces[0] / "query.root", new_root)
        index = copy.deepcopy(self.sharded)
        index["shards"][0]["query_root"] = c._fact(new_root)
        path = self.base / "relocated.json"
        c.r.atomic_json(path, index, exclusive=True)
        read = c.read(path, c.r.sha_file(path))
        self.assertEqual(read["scientific_identity_sha256"], self.sharded["scientific_identity_sha256"])


if __name__ == "__main__":
    unittest.main()
