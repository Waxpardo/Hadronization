import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import sys
import unittest
from unittest import mock

from helpers import ROOT


def module():
    spec = importlib.util.spec_from_file_location("query_model", ROOT / "pipeline/query/model.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class QueryAttemptRetentionContract(unittest.TestCase):
    @staticmethod
    def runner():
        spec = importlib.util.spec_from_file_location("query_attempt_runner", ROOT / "pipeline/query/run.py")
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    def test_absent_work_root_failure_retention_and_retry_publication(self):
        runner = self.runner()
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            output, work = base / "collection/shards/shard-0000", base / "work"
            failed = runner.create_query_stage(output, work)
            self.assertTrue(work.is_dir())
            self.assertEqual(failed.parent, work / "attempts")
            self.assertFalse(output.exists())
            (failed / "partial").write_text("retained")
            runner.preserve_query_failure(failed, output, ValueError("synthetic ordinary failure"))
            failure = json.loads((failed / "failure.json").read_text())
            self.assertEqual(failure["state"], "PRESERVED_FAILED_ATTEMPT")
            successful = runner.create_query_stage(output, work)
            (successful / "manifest.json").write_text("complete")
            runner.publish_directory(successful, output)
            self.assertTrue((output / "manifest.json").is_file())
            self.assertFalse(successful.exists())
            self.assertTrue((failed / "partial").is_file())
            self.assertTrue((failed / "failure.json").is_file())

    def test_task_owned_process_interruption_leaves_private_stage(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            output, work = base / "collection/shards/shard-0000", base / "work"
            code = """
import importlib.util,time
from pathlib import Path
spec=importlib.util.spec_from_file_location('interrupted_query',Path({run!r}))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
stage=module.create_query_stage(Path({output!r}),Path({work!r}))
(stage/'started').write_text('task-owned')
print(stage,flush=True)
time.sleep(300)
""".format(run=str(ROOT / "pipeline/query/run.py"), output=str(output), work=str(work))
            process = subprocess.Popen([sys.executable, "-B", "-c", code], text=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stage = Path(process.stdout.readline().strip())
            self.assertTrue((stage / "started").is_file())
            process.terminate()
            process.wait(timeout=10)
            process.stdout.close()
            process.stderr.close()
            self.assertNotEqual(process.returncode, 0)
            self.assertTrue((stage / "started").is_file())
            self.assertFalse(output.exists())
            self.assertEqual(stage.parent, work / "attempts")

    def test_no_overwrite_symlink_and_cross_filesystem_refuse_before_stage(self):
        runner = self.runner()
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            output, work = base / "collection/shards/shard-0000", base / "work"
            output.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "never overwrite"):
                runner.create_query_stage(output, work)
            output.rmdir()
            target = base / "real-work"
            target.mkdir()
            linked = base / "linked-work"
            linked.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink component"):
                runner.create_query_stage(output, linked)
            with mock.patch.object(runner, "same_filesystem", return_value=False):
                with self.assertRaisesRegex(ValueError, "different filesystems"):
                    runner.create_query_stage(output, work)
            attempts = work / "attempts"
            self.assertTrue(attempts.is_dir())
            self.assertEqual(list(attempts.iterdir()), [])


class ExactProfileContract(unittest.TestCase):
    @staticmethod
    def runner():
        spec = importlib.util.spec_from_file_location("query_contract_runner", ROOT / "pipeline/query/run.py")
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    def test_scientific_binding_authenticates_complete_canonical_parent_receipt(self):
        runner = self.runner()
        receipt = {
            "scientific_identity_sha256": "1" * 64,
            "binding": {"source_subset_digest": "2" * 64, "source_ids": [0, 1]},
            "storage_identity": {"source_ids": [0, 1]},
            "sources": [{"source_id": 0}, {"source_id": 1}],
        }
        metadata = {
            "analysis_sha256": "3" * 64,
            "layout_sha256": "4" * 64,
            "dictionary_body_sha256": "5" * 64,
            "input_root_sha256": "6" * 64,
            "input_receipt_sha256": "7" * 64,
            "input_receipt": receipt,
        }
        original = runner.scientific_binding(metadata)
        self.assertEqual(original["schema"], "hadronization_query_scientific_binding_v2")
        self.assertEqual(original["input_receipt_canonical_sha256"], runner.payload_sha(receipt))
        mutant = copy.deepcopy(metadata)
        mutant["input_receipt"]["binding"]["source_ids"] = [100, 101]
        mutant["input_receipt"]["storage_identity"]["source_ids"] = [100, 101]
        mutant["input_receipt"]["sources"][0]["source_id"] = 100
        mutant["input_receipt"]["sources"][1]["source_id"] = 101
        self.assertNotEqual(runner.scientific_binding(mutant), original)

    def test_complete_phase_a_layout_is_one_exact_repository_owned_contract(self):
        runner = self.runner()
        layout = json.loads((ROOT / "config/query.json").read_text())
        self.assertEqual(runner.require_phase_a_layout(layout), layout)
        mutants = []
        for family in ("constituents", "event_compatibility", "source_counts"):
            mutant = copy.deepcopy(layout)
            del mutant["trees"][family]
            mutants.append(mutant)
        mutant = copy.deepcopy(layout)
        mutant["trees"]["pairs"] = mutant["trees"]["pairs"][:-1]
        mutants.append(mutant)
        mutant = copy.deepcopy(layout)
        del mutant["sparse"]["pairs"]
        mutants.append(mutant)
        mutant = copy.deepcopy(layout)
        mutant["sparse"]["triggers"] = mutant["sparse"]["triggers"][:-1]
        mutants.append(mutant)
        for mutant in mutants:
            with self.subTest(mutant=mutant):
                with self.assertRaisesRegex(ValueError, "complete canonical Phase-A layout"):
                    runner.require_phase_a_layout(mutant)

    def test_public_backend_route_preserves_endpoint_and_combined_profile_semantics(self):
        model = module()
        archived = json.loads((ROOT / "config/analysis.json").read_text())
        routes = model.primitive_routes(archived, archived, "auto")
        self.assertEqual([r["backend"] for r in routes], ["aligned_sparse"])
        combined = {"id": "min_2p5_0p5", "trigger_pt": {"operator": ">=", "value": 2.5},
                    "associate_pt": {"operator": ">=", "value": 0.5},
                    "relative_pt": None}
        request = copy.deepcopy(archived)
        request["profiles"] = [copy.deepcopy(archived["profiles"][0]), combined]
        self.assertEqual(model.primitive_routes(request, archived, "aligned_sparse")[1]["backend"], "aligned_sparse")
        for eta in (1.0, 1.13, 4.01):
            request["pair_acceptance"]["eta"]["value"] = eta
            with self.assertRaisesRegex(ValueError, "no exact aligned sparse route"):
                model.primitive_routes(request, archived, "aligned_sparse")
            self.assertEqual(model.primitive_routes(request, archived, "auto")[0]["backend"], "exact_rows")

    def test_phase_a_native_receipts_and_deferred_profile_guards(self):
        model=module();analysis=json.loads((ROOT/'config/analysis.json').read_text())
        model.validate_phase_a_profiles(analysis['profiles'], analysis['axes']['pt']['edges'])
        plans=model.primitive_routes(analysis,analysis,'aligned_sparse')
        names=['sparse:activity','sparse:pairs','sparse:triggers']+['tree:'+n for n in ('events','sources','source_blocks','source_counts','event_ranges','heavy','triggers','pairs','origins','closure','constituents','event_compatibility')]
        observations=[dict(ordinal=0,digests={n:'a'*64 for n in names},counts={n:17 for n in names})]
        receipts=model.authenticated_routes(analysis,plans,True,observations)
        self.assertEqual({r['route'] for r in receipts if r['primitive_family'] in ('pairs','triggers','activity')},{'NATIVE_ALIGNED_SPARSE'})
        self.assertEqual({r['route'] for r in receipts if r['primitive_family']=='diagnostics'},{'EXACT_ROWS'})
        inclusive=next(r for r in receipts if r['primitive_family']=='pairs' and r['profile_id']=='inclusive')
        self.assertEqual([r['predicate']['low_operator'] for r in inclusive['resolved_axis_selection'][:2]],[None,None])
        configurable=copy.deepcopy(analysis['profiles'])
        configurable.append(dict(id='ordered_minima',
            trigger_pt=dict(operator='>=',value=2.5),
            associate_pt=dict(operator='>=',value=.5),relative_pt=None))
        self.assertEqual(model.validate_phase_a_profiles(configurable, analysis['axes']['pt']['edges']),configurable)
        for deferred in [dict(id='relative_pt',trigger_pt=None,associate_pt=None,relative_pt='trigger_pt>=associate_pt'),
            dict(id='historical_strict_1p0_0p15',trigger_pt=dict(operator='>',value=1.),associate_pt=dict(operator='>',value=.15),relative_pt=None)]:
            with self.assertRaisesRegex(ValueError,'released|eventwise'):
                model.validate_phase_a_profiles([deferred], analysis['axes']['pt']['edges'])

    def test_atomic_directory_publication_cannot_replace_a_racing_destination(self):
        spec = importlib.util.spec_from_file_location("query_publish", ROOT / "pipeline/query/run.py")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            staging, output = base / "staging", base / "output"
            staging.mkdir(); (staging / "manifest.json").write_text("complete")
            output.mkdir()  # A different process created it after the initial check.
            with self.assertRaises(FileExistsError):
                runner.publish_directory(staging, output)
            self.assertTrue(staging.exists())
            self.assertEqual(list(output.iterdir()), [])
            output.rmdir()
            runner.publish_directory(staging, output)
            self.assertFalse(staging.exists())
            self.assertEqual((output / "manifest.json").read_text(), "complete")

    def test_declared_two_profiles_and_endpoint_mutants(self):
        model=module();analysis=json.loads((ROOT/'config/analysis.json').read_text());profiles=analysis['profiles']
        self.assertEqual([p['id'] for p in profiles],['inclusive'])
        self.assertEqual(model.profile_tokens(profiles[0]),['NONE','NONE','NONE'])
        self.assertIn(.15,analysis['axes']['pt']['edges']);self.assertIn(1.,analysis['axes']['pt']['edges'])
        rectangle=dict(id='optional_rectangle',trigger_pt=dict(operator='>=',value=1.0),
                       associate_pt=dict(operator='>=',value=.15),relative_pt=None)
        self.assertEqual(model.profile_tokens(rectangle),['>=1.0','>=0.15','NONE'])
        for role in ('trigger_pt','associate_pt'):
            mutant=copy.deepcopy(rectangle);mutant[role]['operator']='>'
            with self.assertRaisesRegex(ValueError,'released|Phase-A profile'):
                model.validate_phase_a_profiles([profiles[0],mutant], analysis['axes']['pt']['edges'])
        for trigger, associate in ((.15, .5), (-1., .15), (math.inf, .15), (math.nan, .15)):
            mutant = [copy.deepcopy(profiles[0]),
                      dict(id='invalid_rectangle', trigger_pt=dict(operator='>=', value=trigger),
                           associate_pt=dict(operator='>=', value=associate), relative_pt=None)]
            with self.assertRaises(ValueError):
                model.validate_phase_a_profiles(mutant, analysis['axes']['pt']['edges'])
        with self.assertRaisesRegex(ValueError,'regular-bin lower edge'):
            model.projection_contract(rectangle,'aligned_sparse',[0,.5,1,2])
        equal=dict(id='equal_minima',trigger_pt=dict(operator='>=',value=.5),
                   associate_pt=dict(operator='>=',value=.5),relative_pt=None)
        self.assertEqual(model.validate_phase_a_profiles([profiles[0],equal],analysis['axes']['pt']['edges'])[-1],equal)

    def test_shared_cpp_predicate_against_independent_binary64_oracle(self):
        compiler = shutil.which("c++")
        if compiler is None:
            self.skipTest("C++ compiler unavailable")
        source = r'''
#include "selection.hpp"
#include <iomanip>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <limits>
int main() {
  using namespace HadronizationQuery;
  const auto tiny=ReadThreshold(">=5e-324");
  if (tiny.value!=std::numeric_limits<double>::denorm_min() || tiny.Accept(0) || !tiny.Accept(tiny.value)) return 2;
  try { ReadProfile(0,"relative_pt","NONE","NONE","NONE"); return 3; }
  catch (const std::runtime_error&) {}
  const auto inclusive = ReadProfile(0,"inclusive","NONE","NONE","NONE");
  try { ReadProfile(1,"strict",">1.0",">0.15","NONE"); return 4; }
  catch (const std::runtime_error&) {}
  try { ReadProfile(2,"relative","NONE","NONE","trigger_pt>associate_pt"); return 5; }
  catch (const std::runtime_error&) {}
  const auto threshold = ReadProfile(2,"threshold",">=1.0",">=0.15","NONE");
  const auto equal = ReadProfile(3,"equal",">=0.5",">=0.5","NONE");
  if (!inclusive.Pair(0.1,2.0) || !threshold.Pair(1.2,2.0) ||
      !equal.Pair(0.5,0.5) || equal.Pair(0.499,0.5) || threshold.Pair(0.99,2.0)) return 6;
  double t=0,a=0;
  std::uint64_t tb=0,ab=0;
  while (std::cin >> tb >> ab) {
    std::memcpy(&t,&tb,8); std::memcpy(&a,&ab,8);
    for (const auto& p : {inclusive,threshold})
      std::cout << p.Trigger(t) << ' ' << p.Pair(t,a) << ' ';
    std::cout << '\n';
  }
}
'''
        values = [0.0, math.nextafter(0.0, 1.0),
                  math.nextafter(0.15, 0.0), 0.15, math.nextafter(0.15, 1.0),
                  0.2, math.nextafter(1.0, 0.0), 1.0, math.nextafter(1.0, 2.0),
                  7000.0, 7001.0]
        pairs = [(t, a) for t in values for a in values]
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary); cpp = base / "oracle.cpp"; binary = base / "oracle"
            cpp.write_text(source)
            build = subprocess.run([compiler, "-std=c++17", "-O2", "-Wall", "-Wextra",
                                    "-Wpedantic", "-Werror", "-ffp-contract=off",
                                    "-I" + str(ROOT / "pipeline/query"), str(cpp),
                                    "-o", str(binary)], capture_output=True, text=True)
            self.assertEqual((build.returncode, build.stdout, build.stderr), (0, "", ""))
            result = subprocess.run([str(binary)], input="".join(
                "{} {}\n".format(struct.unpack("=Q", struct.pack("=d", t))[0],
                                  struct.unpack("=Q", struct.pack("=d", a))[0])
                for t, a in pairs),
                check=True, text=True, capture_output=True)
        actual = [[int(x) for x in line.split()] for line in result.stdout.splitlines()]
        expected = [[1, 1, int(t >= 1.0), int(t >= 1.0 and a >= 0.15)] for t, a in pairs]
        self.assertEqual(actual, expected)
        # Both values occupy the same [0,.5) sparse pT cell, but exact outcomes differ.
        self.assertTrue(all(row[0] == 1 for row in actual))


class RootQueryContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_analysis import AnalysisShardContract
        cls.fixture = AnalysisShardContract
        cls.fixture.setUpClass()
        cls.base = cls.fixture.base
        cls.workspace = cls.base / "query"
        cls.work = cls.base / "query-work"
        cls.dictionary = cls.base / "campaign-pdgs.json"
        cls.prepared_pack = cls.base / "prepared-query-pack"
        spec = importlib.util.spec_from_file_location("query_runner", ROOT / "pipeline/query/run.py")
        cls.query = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.query)
        result = cls.cli("prepare-pack", "--output", cls.prepared_pack)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        receipt = json.loads(cls.fixture.receipt.read_text())
        result = cls.cli("census", "--input", cls.fixture.shard, "--receipt", cls.fixture.receipt,
                         "--expected-source-count", len(receipt["binding"]["source_ids"]),
                         "--output", cls.dictionary)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        result = cls.cli("build", "--input", cls.fixture.shard, "--receipt", cls.fixture.receipt,
                         "--dictionary", cls.dictionary, "--output", cls.workspace)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.trusted_content_sha256 = json.loads((cls.workspace / "manifest.json").read_text())["scientific_content_sha256"]

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    @classmethod
    def cli(cls, *args):
        if args and args[0] in ("verify", "scan", "project") and "--expected-content-sha256" not in args:
            # Captured immediately after trusted build, independent of mutated workspaces.
            args = args + ("--expected-content-sha256", cls.trusted_content_sha256)
        return subprocess.run([sys.executable, "-B", str(ROOT / "hadronization"), "query"] +
                              [str(x) for x in args] + ["--work-root", str(cls.work)],
                              text=True, capture_output=True, env=cls.fixture.environment)

    def test_exact_rows_match_independent_source_oracle(self):
        from test_analysis import EXPECTED_SCHEMA
        fields = [item.split(":")[0] for item in EXPECTED_SCHEMA["pairs"].split(",")]
        source = [dict(zip(fields, row)) for row in self.fixture.oracle["rows"]["pairs"]]
        predicates = {"inclusive": lambda t, a: True}
        counts = {}
        for name, predicate in predicates.items():
            result = self.cli("scan", "--workspace", self.workspace, "--profile", name)
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = ["\t".join(row[key] for key in
                                   ("event_id", "trigger_heavy_index", "associate_heavy_index"))
                        for row in source if predicate(float.fromhex(row["trigger_pt"]),
                                                       float.fromhex(row["associate_pt"]))]
            self.assertEqual(result.stdout.splitlines(), expected)
            counts[name] = len(expected)
        self.assertEqual(counts["inclusive"], len(source))
        self.assertTrue(any(float.fromhex(row["trigger_pt"]) < float.fromhex(row["associate_pt"])
                            for row in source))

    def test_current_pair_proof_rejects_one_omitted_registered_pair(self):
        fixture = ROOT / "tests/fixtures/query_pair_population"
        expected = json.loads((fixture / "expected.json").read_text())
        self.assertEqual(hashlib.sha256((fixture / "omit_pair.cpp").read_bytes()).hexdigest(),
                         expected["mutator_sha256"])
        self.assertEqual(hashlib.sha256((fixture / "make_positive_ss_unresolved.cpp").read_bytes()).hexdigest(),
                         expected["positive_materializer_sha256"])
        for name, field in (("positive-source.root", "source_root_sha256"),
                            ("positive-source.json", "source_receipt_sha256"),
                            ("dictionary.json", "dictionary_sha256")):
            self.assertEqual(hashlib.sha256((fixture / name).read_bytes()).hexdigest(), expected[field])
        analysis = json.loads((ROOT / "config/analysis.json").read_text())
        target = expected["omitted_pair"]
        mutator = self.base / "omit-registered-pair"
        self.fixture._compile((fixture / "omit_pair.cpp").read_text(),
                              self.base / "omit-registered-pair.cpp", mutator)
        modified = self.base / "missing-registered-pair.root"
        subprocess.run([str(mutator), str(fixture / "positive-source.root"), str(modified),
                        str(target["event_id"]), str(target["trigger_heavy_index"]),
                        str(target["associate_heavy_index"])], check=True,
                       env=self.fixture.environment, capture_output=True)
        receipt = json.loads((fixture / "positive-source.json").read_text())
        spec = self.base / "missing-registered-pair.tsv"
        spec.write_text(self.query.layout_spec(analysis,
            json.loads((ROOT / "config/query.json").read_text()), receipt["binding"],
            self.query.read_dictionary(fixture / "dictionary.json"), scientific_binding_sha="1" * 64,
            execution_attestation_sha="2" * 64))
        metadata = self.base / "missing-registered-pair.json"
        metadata.write_text('{"query_content_digests":"__QUERY_CONTENT_DIGESTS__",'
                            '"query_content_sha256":"__QUERY_CONTENT_SHA256__",'
                            '"pair_population_proof":"__PAIR_POPULATION_PROOF__"}')
        environment, binary, _ = self.query.build_tool(self.work)
        positive_metadata = self.base / "positive-pair-population.json"
        positive_metadata.write_bytes(metadata.read_bytes())
        positive_result = subprocess.run([str(binary), "build", str(spec),
            str(fixture / "positive-source.root"), str(self.base / "positive-pair-population.root"),
            str(positive_metadata)], text=True, capture_output=True, env=environment)
        self.assertEqual(positive_result.returncode, 0, positive_result.stderr)
        proof = json.loads(positive_metadata.read_text())["pair_population_proof"]
        signs = {item["sign"] for item in proof["by_tune_sector_sign"] if item["count"] > 0}
        self.assertEqual(signs, {-1, 1})
        self.assertEqual(proof["candidate_pairs"], proof["stored_pairs"])
        import ROOT as rootlib
        opened = rootlib.TFile.Open(str(fixture / "positive-source.root"), "READ")
        try:
            unresolved = expected["unresolved_same_sign_pair"]
            self.assertTrue(any(int(row.event_id) == unresolved["event_id"] and
                int(row.trigger_heavy_index) == unresolved["trigger_heavy_index"] and
                int(row.associate_heavy_index) == unresolved["associate_heavy_index"] and
                int(row.sign) == unresolved["sign"] and
                int(row.associate_origin) == unresolved["associate_origin"]
                for row in opened.Get("pairs")))
        finally:
            opened.Close()
        result = subprocess.run([str(binary), "build", str(spec), str(modified),
                                 str(self.base / "must-not-publish-missing-pair.root"),
                                 str(metadata)], text=True, capture_output=True, env=environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(expected["expected_error"] + str(target["event_id"]), result.stderr)
        self.assertIn("trigger=" + str(target["trigger_heavy_index"]), result.stderr)
        self.assertIn("associate=" + str(target["associate_heavy_index"]), result.stderr)
        self.assertEqual(hashlib.sha256((fixture / "selected_hard_noncompanion.cpp").read_bytes()).hexdigest(),
                         expected["selected_hard_noncompanion_mutator_sha256"])
        noncompanion_tool = self.base / "selected-hard-noncompanion"
        self.fixture._compile((fixture / "selected_hard_noncompanion.cpp").read_text(),
                              self.base / "selected-hard-noncompanion.cpp", noncompanion_tool)
        noncompanion = self.base / "missing-selected-hard-noncompanion.root"
        subprocess.run([str(noncompanion_tool), str(fixture / "positive-source.root"),
                        str(noncompanion)], check=True, env=environment, capture_output=True)
        case = expected["selected_hard_noncompanion"]
        opened = rootlib.TFile.Open(str(noncompanion), "READ")
        try:
            sector_origins = {int(row.heavy_index): (int(row.origin), int(row.resolution),
                int(row.matched_hard)) for row in opened.Get("origins")
                if int(row.event_id) == case["event_id"] and int(row.sector) == 4}
            self.assertEqual(sector_origins[case["trigger_heavy_index"]],
                             (1, 1, case["trigger_matched_hard"]))
            self.assertEqual(sector_origins[case["associate_heavy_index"]],
                             (1, 1, case["associate_matched_hard"]))
            self.assertEqual(sector_origins[case["same_root_opposite_sign_trigger_heavy_index"]],
                             (1, 1, case["associate_matched_hard"]))
            self.assertFalse(any(int(row.event_id) == case["event_id"] and
                int(row.trigger_heavy_index) == case["trigger_heavy_index"] and
                int(row.associate_heavy_index) == case["associate_heavy_index"]
                for row in opened.Get("pairs")))
            self.assertFalse(any(int(row.event_id) == case["event_id"] and
                int(row.trigger_heavy_index) == case["same_root_opposite_sign_trigger_heavy_index"] and
                int(row.associate_heavy_index) == case["associate_heavy_index"]
                for row in opened.Get("pairs")))
            selected = {int(row.heavy_index): (int(row.pdg), int(row.qc))
                        for row in opened.Get("heavy") if int(row.event_id) == case["event_id"]}
            self.assertEqual(selected[case["trigger_heavy_index"]][0], case["trigger_pdg"])
            self.assertEqual(selected[case["associate_heavy_index"]][0], case["associate_pdg"])
            self.assertEqual(selected[case["same_root_opposite_sign_trigger_heavy_index"]][0],
                             case["same_root_opposite_sign_trigger_pdg"])
            self.assertEqual(selected[case["trigger_heavy_index"]][1] *
                             selected[case["associate_heavy_index"]][1], case["sign"])
            self.assertEqual(selected[case["same_root_opposite_sign_trigger_heavy_index"]][1] *
                             selected[case["associate_heavy_index"]][1], -1)
        finally:
            opened.Close()
        noncompanion_metadata = self.base / "selected-hard-noncompanion.json"
        noncompanion_metadata.write_text('{"query_content_digests":"__QUERY_CONTENT_DIGESTS__",'
            '"query_content_sha256":"__QUERY_CONTENT_SHA256__",'
            '"pair_population_proof":"__PAIR_POPULATION_PROOF__"}')
        noncompanion_result = subprocess.run([str(binary), "build", str(spec), str(noncompanion),
            str(self.base / "must-not-publish-noncompanion.root"), str(noncompanion_metadata)],
            text=True, capture_output=True, env=environment)
        self.assertNotEqual(noncompanion_result.returncode, 0)
        self.assertIn("missing in-domain pair event=" + str(case["event_id"]),
                      noncompanion_result.stderr)
        for name, value in (("trigger", case["trigger_heavy_index"]),
                            ("associate", case["associate_heavy_index"]),
                            ("trigger_pdg", case["trigger_pdg"]),
                            ("associate_pdg", case["associate_pdg"]),
                            ("sign", case["sign"])):
            self.assertIn(name + "=" + str(value), noncompanion_result.stderr)
        self.assertEqual(hashlib.sha256((fixture / "corrupt_origin.cpp").read_bytes()).hexdigest(),
                         expected["corrupt_origin_sha256"])
        corruptor = self.base / "corrupt-registered-origin"
        self.fixture._compile((fixture / "corrupt_origin.cpp").read_text(),
                              self.base / "corrupt-registered-origin.cpp", corruptor)
        malformed = self.base / "malformed-registered-origin.root"
        subprocess.run([str(corruptor), str(fixture / "positive-source.root"), str(malformed)],
                       check=True, env=environment, capture_output=True)
        malformed_metadata = self.base / "malformed-registered-origin.json"
        # Use a fresh placeholder; the positive build consumed its own metadata.
        malformed_metadata.write_text('{"query_content_digests":"__QUERY_CONTENT_DIGESTS__",'
            '"query_content_sha256":"__QUERY_CONTENT_SHA256__",'
            '"pair_population_proof":"__PAIR_POPULATION_PROOF__"}')
        malformed_result = subprocess.run([str(binary), "build", str(spec), str(malformed),
            str(self.base / "must-not-publish-malformed-origin.root"), str(malformed_metadata)],
            text=True, capture_output=True, env=environment)
        self.assertNotEqual(malformed_result.returncode, 0)
        self.assertIn(expected["malformed_provenance_error"], malformed_result.stderr)

    def test_every_tree_digest_matches_independent_original_row_encoding(self):
        from test_analysis import EXPECTED_SCHEMA
        metadata = json.loads((self.workspace / "metadata.json").read_text())
        layout = json.loads((self.workspace / "layout.json").read_text())
        for name, selected in layout["trees"].items():
            schema = dict(field.split(":") for field in EXPECTED_SCHEMA[name].split(","))
            fields = list(schema)
            digest = hashlib.sha256()
            def field(value):
                encoded = value.encode("ascii")
                digest.update(len(encoded).to_bytes(8, "big")); digest.update(encoded)
            field("hadronization_query_tree_content_v1"); field(name)
            rows = self.fixture.oracle["rows"][name]
            field(str(len(rows)))
            for key in selected:
                field(key); field(schema[key]); field("1")
            for row in rows:
                named = dict(zip(fields, row))
                for key in selected:
                    value = named[key]
                    field(struct.pack(">d", float.fromhex(value)).hex()
                          if schema[key] == "Double_t" else str(int(value)))
            self.assertEqual(digest.hexdigest(), metadata["query_content_digests"]["tree:" + name], name)

    def test_rapidity_is_retained_exactly_and_is_not_eta(self):
        from test_analysis import EXPECTED_SCHEMA
        fields = [item.split(":")[0] for item in EXPECTED_SCHEMA["heavy"].split(",")]
        expected = [(float.fromhex(row[fields.index("eta")]),
                     float.fromhex(row[fields.index("rapidity")]))
                    for row in self.fixture.oracle["rows"]["heavy"]]
        self.assertTrue(any(eta != rapidity for eta, rapidity in expected))
        source = r'''
#include "TFile.h"
#include "TTree.h"
#include <iomanip>
#include <iostream>
int main(int argc,char** argv){
 if(argc!=2)return 2;TFile f(argv[1],"READ");auto* t=dynamic_cast<TTree*>(f.Get("heavy"));if(!t)return 3;
 Double_t eta=0,rapidity=0;t->SetBranchAddress("eta",&eta);t->SetBranchAddress("rapidity",&rapidity);
 std::cout<<std::hexfloat;
 for(Long64_t i=0;i<t->GetEntries();++i){if(t->GetEntry(i)<=0)return 4;std::cout<<eta<<'\t'<<rapidity<<'\n';}
}
'''
        self.fixture._compile(source, self.base / "rapidity-read.cpp", self.base / "rapidity-read")
        result = subprocess.run([str(self.base / "rapidity-read"), str(self.workspace / "query.root")],
                                text=True, capture_output=True, env=self.fixture.environment)
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        actual = [tuple(float.fromhex(value) for value in line.split("\t"))
                  for line in result.stdout.splitlines()]
        self.assertEqual(actual, expected)

    def test_trigger_and_valence_sign_counts_survive(self):
        from test_analysis import EXPECTED_SCHEMA
        trigger_fields = [x.split(":")[0] for x in EXPECTED_SCHEMA["triggers"].split(",")]
        pair_fields = [x.split(":")[0] for x in EXPECTED_SCHEMA["pairs"].split(",")]
        triggers = [dict(zip(trigger_fields, row)) for row in self.fixture.oracle["rows"]["triggers"]]
        pairs = [dict(zip(pair_fields, row)) for row in self.fixture.oracle["rows"]["pairs"]]
        event_fields = [x.split(":")[0] for x in EXPECTED_SCHEMA["events"].split(",")]
        weights = {int(row[event_fields.index("event_id")]):
                   float.fromhex(row[event_fields.index("weight")])
                   for row in self.fixture.oracle["rows"]["events"]}
        accepted = {(int(row["event_id"]), int(row["heavy_index"])) for row in triggers
                    if int(row["rejection_mask"]) == 0}
        paired = {(int(row["event_id"]), int(row["trigger_heavy_index"])) for row in pairs}
        expected = (len(accepted), len(accepted - paired),
                    sum(int(row["sign"]) == -1 for row in pairs),
                    sum(int(row["sign"]) == 1 for row in pairs))
        source = r'''
#include "TFile.h"
#include "TTree.h"
#include "THnSparse.h"
#include <iomanip>
#include <iostream>
#include <set>
#include <utility>
int main(int argc,char** argv){
 if(argc!=2)return 2;TFile f(argv[1],"READ");
 auto* t=dynamic_cast<TTree*>(f.Get("triggers"));auto* p=dynamic_cast<TTree*>(f.Get("pairs"));
 auto* h=dynamic_cast<THnSparseD*>(f.Get("sparse_triggers"));if(!t||!p||!h)return 3;
 ULong64_t event=0;Int_t index=0;UInt_t mask=0;
 t->SetBranchAddress("event_id",&event);t->SetBranchAddress("heavy_index",&index);t->SetBranchAddress("rejection_mask",&mask);
 std::set<std::pair<ULong64_t,Int_t>> accepted,paired;
 for(Long64_t i=0;i<t->GetEntries();++i){t->GetEntry(i);if(mask==0)accepted.emplace(event,index);}
 Int_t sign=0;p->SetBranchAddress("event_id",&event);p->SetBranchAddress("trigger_heavy_index",&index);p->SetBranchAddress("sign",&sign);
 Long64_t os=0,ss=0;for(Long64_t i=0;i<p->GetEntries();++i){p->GetEntry(i);paired.emplace(event,index);if(sign==-1)++os;else if(sign==1)++ss;else return 4;}
 Long64_t zero=0;for(const auto& key:accepted)if(!paired.count(key))++zero;
 double sum=0,sumw2=0;for(Long64_t i=0;i<h->GetNbins();++i){sum+=h->GetBinContent(i);sumw2+=h->GetBinError2(i);}
 std::cout<<accepted.size()<<' '<<zero<<' '<<os<<' '<<ss<<' '<<std::setprecision(17)
          <<sum<<' '<<sumw2<<' '<<h->GetEntries()<<'\n';
}
'''
        self.fixture._compile(source, self.base / "trigger-sign-read.cpp", self.base / "trigger-sign-read")
        query_root = self.workspace / "query.root"
        result = subprocess.run([str(self.base / "trigger-sign-read"), str(query_root)],
                                text=True, capture_output=True, env=self.fixture.environment)
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        values = result.stdout.split()
        self.assertEqual(tuple(map(int, values[:4])), expected)
        expected_weights = [weights[event] for event, _ in accepted]
        self.assertAlmostEqual(float(values[4]), sum(expected_weights), places=12)
        self.assertAlmostEqual(float(values[5]), sum(weight * weight for weight in expected_weights), places=12)
        self.assertEqual(float(values[6]), len(accepted))

    def test_prepared_pack_refuses_fallback_and_mismatch(self):
        receipt_sha = self.query.reduce.sha_file(self.fixture.receipt)
        output = self.base / "query-from-prepared-pack"
        environment = self.fixture.environment.copy()
        environment["CXX"] = "/definitely/not/a/compiler"
        environment["ROOT_CONFIG"] = "/definitely/not/root-config"
        prepared_dictionary = self.base / "prepared-census-pdgs.json"
        receipt_payload = json.loads(self.fixture.receipt.read_text())
        census_result = subprocess.run([
            sys.executable, "-B", str(ROOT / "hadronization"), "query", "census",
            "--input", str(self.fixture.shard), "--receipt", str(self.fixture.receipt),
            "--accepted-receipt-sha256", receipt_sha,
            "--expected-source-count", str(len(receipt_payload["binding"]["source_ids"])),
            "--output", str(prepared_dictionary), "--prepared-pack", str(self.prepared_pack),
            "--work-root", str(self.work)], text=True, capture_output=True, env=environment)
        self.assertEqual(census_result.returncode, 0, census_result.stderr)
        self.assertEqual(self.query.read_dictionary(prepared_dictionary)["body_sha256"],
                         self.query.read_dictionary(self.dictionary)["body_sha256"])
        result = subprocess.run([
            sys.executable, "-B", str(ROOT / "hadronization"), "query", "build",
            "--input", str(self.fixture.shard), "--receipt", str(self.fixture.receipt),
            "--accepted-receipt-sha256", receipt_sha, "--dictionary", str(self.dictionary),
            "--output", str(output), "--prepared-pack", str(self.prepared_pack),
            "--work-root", str(self.work)], text=True, capture_output=True, env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((output / "manifest.json").is_file())
        missing = self.base / "missing-pack"
        refused = subprocess.run([
            sys.executable, "-B", str(ROOT / "hadronization"), "query", "build",
            "--input", str(self.fixture.shard), "--receipt", str(self.fixture.receipt),
            "--accepted-receipt-sha256", receipt_sha, "--dictionary", str(self.dictionary),
            "--output", str(self.base / "query-missing-pack"), "--prepared-pack", str(missing),
            "--work-root", str(self.work)], text=True, capture_output=True, env=environment)
        self.assertNotEqual(refused.returncode, 0)
        self.assertFalse((self.base / "query-missing-pack").exists())
        corrupt = self.base / "corrupt-pack"
        shutil.copytree(self.prepared_pack, corrupt)
        with (corrupt / "query").open("ab") as handle:
            handle.write(b"x")
        refused = self.cli("verify", "--workspace", self.workspace, "--prepared-pack", corrupt)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("prepared query executable/build receipt identity", refused.stderr)

    def test_public_prepared_build_creates_absent_work_root_and_retains_failure(self):
        receipt_sha = self.query.reduce.sha_file(self.fixture.receipt)
        success_work = self.base / "absent-query-work-success"
        success_output = self.base / "absent-work-query-output"
        self.assertFalse(success_work.exists())
        command = [
            sys.executable, "-B", str(ROOT / "hadronization"), "query", "build",
            "--input", str(self.fixture.shard), "--receipt", str(self.fixture.receipt),
            "--accepted-receipt-sha256", receipt_sha,
            "--dictionary", str(self.dictionary), "--prepared-pack", str(self.prepared_pack),
            "--output", str(success_output), "--work-root", str(success_work),
        ]
        result = subprocess.run(command, text=True, capture_output=True, env=self.fixture.environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((success_output / "manifest.json").is_file())
        self.assertTrue((success_work / "attempts").is_dir())
        self.assertEqual(list((success_work / "attempts").iterdir()), [])

        payload = self.query.read_dictionary(self.dictionary)
        analysis = json.loads((ROOT / "config/analysis.json").read_text())
        configured = set(self.query.configured_pdgs(analysis))
        observed = payload["census"][0]["inputs"][0]["observed_pdgs"]
        omitted = next(pdg for pdg in observed if pdg not in configured)
        mutant = copy.deepcopy(payload)
        mutant["body"]["pdgs"].remove(omitted)
        mutant["body_sha256"] = self.query.payload_sha(mutant["body"])
        dictionary = self.base / "failure-retention-dictionary.json"
        dictionary.write_text(self.query.reduce.canonical(mutant))
        failure_work = self.base / "absent-query-work-failure"
        failure_output = self.base / "retained-failure-query-output"
        command[command.index("--dictionary") + 1] = str(dictionary)
        command[command.index("--output") + 1] = str(failure_output)
        command[command.index("--work-root") + 1] = str(failure_work)
        result = subprocess.run(command, text=True, capture_output=True, env=self.fixture.environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown PDG outside frozen campaign dictionary", result.stderr)
        self.assertFalse(failure_output.exists())
        stages = list((failure_work / "attempts").iterdir())
        self.assertEqual(len(stages), 1)
        self.assertTrue((stages[0] / "query.tsv").is_file())
        failure = json.loads((stages[0] / "failure.json").read_text())
        self.assertEqual(failure["state"], "PRESERVED_FAILED_ATTEMPT")

    def test_campaign_dictionary_consensus_and_unknown_refusal(self):
        payload = self.query.read_dictionary(self.dictionary)
        digest = payload["body_sha256"]
        self.assertEqual(self.query.require_dictionary_consensus([digest, digest]), digest)
        with self.assertRaisesRegex(ValueError, "one campaign PDG dictionary"):
            self.query.require_dictionary_consensus([digest, "0" * 64])
        observed = payload["census"][0]["inputs"][0]["observed_pdgs"]
        self.assertTrue(observed)
        body = copy.deepcopy(payload["body"])
        body["pdgs"].remove(observed[0])
        mutant = copy.deepcopy(payload)
        mutant["body"] = body
        mutant["body_sha256"] = self.query.payload_sha(body)
        spec_path, metadata_path = self.base / "unknown.tsv", self.base / "unknown-metadata.json"
        analysis = json.loads((ROOT / "config/analysis.json").read_text())
        layout = json.loads((ROOT / "config/query.json").read_text())
        receipt = json.loads(self.fixture.receipt.read_text())
        spec_path.write_text(self.query.layout_spec(analysis, layout, receipt["binding"], mutant,
            scientific_binding_sha="1"*64, execution_attestation_sha="2"*64))
        metadata_path.write_text('{"query_content_digests":"__QUERY_CONTENT_DIGESTS__",'
                                 '"query_content_sha256":"__QUERY_CONTENT_SHA256__","pair_population_proof":"__PAIR_POPULATION_PROOF__"}')
        environment, binary, _ = self.query.build_tool(self.work)
        result = subprocess.run([str(binary), "build", str(spec_path), str(self.fixture.shard),
                                 str(self.base / "unknown.root"), str(metadata_path)],
                                text=True, capture_output=True, env=environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown PDG outside frozen campaign dictionary", result.stderr)

    def test_public_verify_refuses_rebound_complete_parent_receipt(self):
        directory = self.base / "mutant-rebound-parent-receipt"
        shutil.copytree(self.workspace, directory)
        metadata = json.loads((directory / "metadata.json").read_text())
        parent = metadata["input_receipt"]
        source_ids = [value + 100 for value in parent["binding"]["source_ids"]]
        parent["binding"]["source_ids"] = source_ids
        parent["storage_identity"]["source_ids"] = source_ids
        for source, source_id in zip(parent["sources"], source_ids):
            source["source_id"] = source_id
        parent["storage_identity_sha256"] = self.query.payload_sha(parent["storage_identity"])
        (directory / "metadata.json").write_text(self.query.reduce.canonical(metadata))
        manifest = json.loads((directory / "manifest.json").read_text())
        for artifact in manifest["artifacts"]:
            if artifact["path"] == "metadata.json":
                artifact["bytes"] = (directory / "metadata.json").stat().st_size
                artifact["sha256"] = self.query.reduce.sha_file(directory / "metadata.json")
        (directory / "manifest.json").write_text(self.query.reduce.canonical(manifest))
        result = self.cli("verify", "--workspace", directory, "--prepared-pack", self.prepared_pack)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("independent scientific content binding", result.stderr)

    def test_public_build_refuses_incomplete_caller_layout_before_publication(self):
        for family in ("constituents", "event_compatibility", "source_counts"):
            with self.subTest(family=family):
                layout = json.loads((ROOT / "config/query.json").read_text())
                del layout["trees"][family]
                layout_path = self.base / ("incomplete-layout-" + family + ".json")
                layout_path.write_text(self.query.reduce.canonical(layout))
                output = self.base / ("incomplete-layout-output-" + family)
                result = self.cli(
                    "build", "--input", self.fixture.shard, "--receipt", self.fixture.receipt,
                    "--accepted-receipt-sha256", self.query.reduce.sha_file(self.fixture.receipt),
                    "--dictionary", self.dictionary, "--layout", layout_path,
                    "--prepared-pack", self.prepared_pack, "--output", output)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("complete canonical Phase-A layout", result.stderr)
                self.assertFalse(output.exists())

    def test_missing_retained_diagnostic_families_refuse(self):
        copier = r'''
#include "TFile.h"
#include "TKey.h"
#include "TTree.h"
#include <memory>
#include <string>
int main(int argc,char** argv){
 if(argc!=4)return 2;TFile input(argv[1],"READ"),output(argv[2],"RECREATE");
 TIter keys(input.GetListOfKeys());while(auto* item=keys()){
  auto* key=dynamic_cast<TKey*>(item);if(!key)return 3;
  if(std::string(key->GetName())==argv[3])continue;
  std::unique_ptr<TObject> object(key->ReadObj());output.cd();
  if(auto* tree=dynamic_cast<TTree*>(object.get())){
   std::unique_ptr<TTree> copy(tree->CloneTree(-1,"fast"));copy->Write(key->GetName());
  }else object->Write(key->GetName());
 }
 output.Close();return 0;
}
'''
        self.fixture._compile(copier, self.base / "omit-tree.cpp", self.base / "omit-tree")
        analysis = json.loads((ROOT / "config/analysis.json").read_text())
        layout = json.loads((ROOT / "config/query.json").read_text())
        receipt = json.loads(self.fixture.receipt.read_text())
        dictionary = self.query.read_dictionary(self.dictionary)
        spec_path = self.base / "missing-family.tsv"
        spec_path.write_text(self.query.layout_spec(analysis, layout, receipt["binding"], dictionary,
            scientific_binding_sha="1"*64, execution_attestation_sha="2"*64))
        environment, binary, _ = self.query.build_tool(self.work)
        for family in ("constituents", "event_compatibility", "source_counts"):
            with self.subTest(family=family):
                input_path = self.base / ("missing-" + family + ".root")
                subprocess.run([str(self.base / "omit-tree"), str(self.fixture.shard),
                                str(input_path), family], check=True, env=environment,
                               capture_output=True)
                metadata_path = self.base / ("missing-" + family + ".json")
                metadata_path.write_text('{"query_content_digests":"__QUERY_CONTENT_DIGESTS__",'
                                         '"query_content_sha256":"__QUERY_CONTENT_SHA256__","pair_population_proof":"__PAIR_POPULATION_PROOF__"}')
                result = subprocess.run([str(binary), "build", str(spec_path), str(input_path),
                                         str(self.base / ("missing-output-" + family + ".root")),
                                         str(metadata_path)], text=True, capture_output=True,
                                        env=environment)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("missing exact tree " + family, result.stderr)

    def test_public_verifier_no_overwrite_and_exact_fileset(self):
        result = self.cli("verify", "--workspace", self.workspace)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SPARSE\ttriggers\t6\t6\n", result.stdout)
        self.assertIn("SPARSE\tpairs\t38\t38\n", result.stdout)
        self.assertNotIn("pairs__relative_pt", result.stdout)
        before = (self.workspace / "manifest.json").read_bytes()
        duplicate = self.cli("build", "--input", self.fixture.shard, "--receipt", self.fixture.receipt,
                             "--dictionary", self.dictionary, "--output", self.workspace)
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertEqual((self.workspace / "manifest.json").read_bytes(), before)
        extra = self.workspace / "unmanifested"
        extra.write_text("mutant")
        try:
            self.assertNotEqual(self.cli("verify", "--workspace", self.workspace).returncode, 0)
        finally:
            extra.unlink()

    def test_natural_pdg_remapping_is_label_safe_and_associative(self):
        source = r'''
#include "__HEADER__"
#include <iostream>
#include <memory>
#include <tuple>
using Totals=std::map<int,double>;
std::unique_ptr<THnSparseD> histogram(const std::vector<int>& labels,const Totals& values) {
  int bins=labels.size(); double low=-.5,high=bins-.5;
  auto result=std::make_unique<THnSparseD>("test","test",1,&bins,&low,&high);
  result->Sumw2(); result->GetAxis(0)->SetName("pdg");
  for(int i=0;i<bins;++i) {
    result->GetAxis(0)->SetBinLabel(i+1,std::to_string(labels[i]).c_str());
    auto found=values.find(labels[i]);
    if(found!=values.end()){double coordinate=i;result->Fill(&coordinate,found->second);}
  }
  return result;
}
Totals decode(THnSparseD& h) {
  HadronizationQuery::NaturalSparseRows rows(h,{"pdg"});Totals result;
  while(rows.Next())result[rows.Pdg("pdg")]+=rows.value;
  return result;
}
Totals merge(Totals a,const Totals& b){for(const auto& x:b)a[x.first]+=x.second;return a;}
int main(){
  const Totals expected{{-521,6},{521,8},{5122,10},{9000001,12}};
  auto a=histogram({521,-521,5122},{{-521,1},{521,2},{5122,3}});
  auto b=histogram({9000001,5122,-521,521},{{-521,5},{521,6},{5122,7},{9000001,12}});
  auto c=histogram({-521,521,5122,9000001},expected);
  if(merge(decode(*a),decode(*b))!=decode(*c))return 2;
  auto reordered=histogram({5122,521,-521},{{-521,1},{521,2},{5122,3}});
  if(decode(*a)!=decode(*reordered))return 3;
  // Same shape, different signed labels: bin-wise addition would alias identities.
  auto different=histogram({411,-411,4122},{{411,2},{-411,1},{4122,3}});
  if(decode(*different)==decode(*a))return 4;
  const auto av=decode(*a),bv=decode(*b),cv=decode(*c),dv=decode(*different);
  if(merge(merge(av,bv),merge(cv,dv))!=merge(av,merge(bv,merge(cv,dv))))return 5;
  if(merge(merge(merge(av,bv),cv),dv)!=merge(merge(dv,cv),merge(bv,av)))return 6;
  for(const std::string label:{"", "521", "0521", "0", "521junk"}) {
    auto bad=histogram({521,-521,5122},{{521,1}});
    bad->GetAxis(0)->SetBinLabel(2,label.c_str());
    try{decode(*bad);return 7;}catch(const std::runtime_error&){}
  }
  int bins[3]={2,10,3};double low[3]={-.5,.5,-.5},high[3]={1.5,10.5,2.5};
  THnSparseD topology("topology","topology",3,bins,low,high);topology.Sumw2();
  for(int i=0;i<3;++i)topology.GetAxis(i)->SetName(std::vector<std::string>{"tune","block","pdg"}[i].c_str());
  for(int i=0;i<3;++i)topology.GetAxis(2)->SetBinLabel(i+1,std::to_string(std::vector<int>{5122,521,-521}[i]).c_str());
  for(int tune=0;tune<2;++tune)for(int block=1;block<=10;++block)for(int pdg=0;pdg<3;++pdg){
    double x[3]={double(tune),double(block),double(pdg)};topology.Fill(x,100*tune+10*block+pdg);
  }
  HadronizationQuery::NaturalSparseRows identity(topology,{"tune","block","pdg"});
  std::map<std::tuple<int,int,int>,double> byIdentity;
  while(identity.Next())byIdentity[{identity.Integer("tune"),identity.Integer("block"),identity.Pdg("pdg")}]+=identity.value;
  if(byIdentity.size()!=60 || byIdentity.at({0,1,5122})!=10 || byIdentity.at({1,1,5122})!=110 ||
     byIdentity.at({1,10,-521})!=202)return 8;
  std::cout<<"NATURAL_PDG_MERGE 2_inputs 4_inputs reordered rare missing distinct_labels 2_tunes 10_blocks associative PASS\n";
}
'''.replace("__HEADER__", str(ROOT / "pipeline/query/sparse.hpp"))
        self.fixture._compile(source, self.base / "natural-pdg.cpp", self.base / "natural-pdg")
        result = subprocess.run([str(self.base / "natural-pdg")], text=True,
                                capture_output=True, env=self.fixture.environment)
        self.assertEqual((result.returncode, result.stderr), (0, ""), result.stdout + result.stderr)
        self.assertIn("associative PASS", result.stdout)

    def test_native_aligned_inclusive_rectangles(self):
        from test_analysis import EXPECTED_SCHEMA
        source = r'''
#include "__SPARSE__"
#include "TFile.h"
#include "TH1D.h"
#include <iomanip>
#include <iostream>
#include <memory>
#include <string>
int main(int argc,char** argv) {
  if (argc!=2) return 2;
  TFile f(argv[1],"READ");
  for (const std::string name:{"pairs","triggers"}) {
    auto* h=dynamic_cast<THnSparseD*>(f.Get(("sparse_"+name).c_str()));
    if (!h) return 3;
    int output=-1;
    for (int a=0;a<h->GetNdimensions();++a) {
      auto* axis=h->GetAxis(a);const std::string field=axis->GetName();
      if (field==(name=="triggers"?"trigger_pt":"dphi")) output=a;
    }
    HadronizationQuery::SelectPhysicalEta(*h,"trigger_eta",4.0);
    if (name=="pairs") HadronizationQuery::SelectPhysicalEta(*h,"associate_eta",4.0);
    HadronizationQuery::SelectThreshold(*h,"trigger_pt",
      HadronizationQuery::ReadThreshold(name=="pairs"?">=0.0":">=1.0"));
    if (name=="pairs") HadronizationQuery::SelectThreshold(*h,"associate_pt",
      HadronizationQuery::ReadThreshold(">=0.0"));
    if (output<0) return 4;
    std::unique_ptr<TH1D> projected(h->Projection(output,"E"));
    double sum=0,sumw2=0;
    for (int b=0;b<=projected->GetNbinsX()+1;++b) {
      sum+=projected->GetBinContent(b);
      sumw2+=projected->GetBinError(b)*projected->GetBinError(b);
    }
    std::cout<<name<<'\t'<<std::setprecision(17)<<sum<<'\t'<<sumw2<<'\n';
  }
}
'''.replace("__SPARSE__", str(ROOT / "pipeline/query/sparse.hpp"))
        self.fixture._compile(source, self.base / "rectangle.cpp", self.base / "rectangle")
        output = subprocess.check_output([str(self.base / "rectangle"),
                                          str(self.workspace / "query.root")],
                                         text=True, env=self.fixture.environment)
        def rows(table):
            fields = [x.split(":")[0] for x in EXPECTED_SCHEMA[table].split(",")]
            return [dict(zip(fields, row)) for row in self.fixture.oracle["rows"][table]]
        heavy = {(x["event_id"], x["heavy_index"]): x for x in rows("heavy")}
        weights = {x["event_id"]: float.fromhex(x["weight"]) for x in rows("events")}
        expected = {name: [] for name in ("pairs", "triggers")}
        for row in rows("pairs"):
            trigger = heavy[row["event_id"], row["trigger_heavy_index"]]
            associate = heavy[row["event_id"], row["associate_heavy_index"]]
            t, a = float.fromhex(trigger["pt"]), float.fromhex(associate["pt"])
            if t >= 0 and a >= 0 and abs(float.fromhex(trigger["eta"])) <= 4 and abs(float.fromhex(associate["eta"])) <= 4:
                expected["pairs"].append(weights[row["event_id"]])
        for row in rows("triggers"):
            particle = heavy[row["event_id"], row["heavy_index"]]
            if not int(row["rejection_mask"]) and float.fromhex(particle["pt"]) >= 1 and abs(float.fromhex(particle["eta"])) <= 4:
                expected["triggers"].append(weights[row["event_id"]])
        for line in output.splitlines():
            name, total, sumw2 = line.split("\t")
            self.assertEqual(float(total), sum(expected[name]))
            self.assertAlmostEqual(float(sumw2), sum(w*w for w in expected[name]), places=12)
        self.assertGreater(len(expected["pairs"]), 0)

    def test_native_endpoint_predecessor_equal_successor_and_strict_mutant(self):
        source=r'''
#include "__HEADER__"
#include <iostream>
#include <cmath>
int main(){
 int bins[2]={4,4};double lo[2]={0,0},hi[2]={1.5,1.5};
 THnSparseD h("boundary","boundary",2,bins,lo,hi);h.Sumw2();
 const double edges[5]={0,.15,.5,1.,1.5};
 for(int i=0;i<2;++i){h.GetAxis(i)->Set(4,edges);h.GetAxis(i)->SetName(i?"associate_pt":"trigger_pt");}
 double expected=0;int ordinal=0;
 for(double t:{std::nextafter(1.,0.),1.,std::nextafter(1.,2.)})
  for(double a:{std::nextafter(.15,0.),.15,std::nextafter(.15,1.)}){
   double x[2]={t,a};const double weight=std::ldexp(1.,ordinal++);h.Fill(x,weight);
   if(t>=1.&&a>=.15)expected+=weight;
  }
 HadronizationQuery::SelectThreshold(h,"trigger_pt",HadronizationQuery::ReadThreshold(">=1.0"));
 HadronizationQuery::SelectThreshold(h,"associate_pt",HadronizationQuery::ReadThreshold(">=0.15"));
 HadronizationQuery::NaturalSparseRows rows(h,{"trigger_pt","associate_pt"});
 double actual=0;while(rows.Next())actual+=rows.value;
 if(actual!=expected||expected!=432.)return 2;
 try{HadronizationQuery::SelectThreshold(h,"trigger_pt",HadronizationQuery::ReadThreshold(">1.0"));return 3;}catch(const std::runtime_error&){}
 std::cout<<"NATIVE_ENDPOINT_9_COMBINATIONS_EQUALITY_INCLUDED_STRICT_MUTANT_REJECTED PASS\n";
}
'''.replace('__HEADER__',str(ROOT/'pipeline/query/sparse.hpp'))
        self.fixture._compile(source,self.base/'endpoint.cpp',self.base/'endpoint')
        completed=subprocess.run([str(self.base/'endpoint')],text=True,capture_output=True,env=self.fixture.environment)
        self.assertEqual((completed.returncode,completed.stderr),(0,''),completed.stdout)

    def test_native_persisted_unrelated_ranges_cannot_become_cuts(self):
        source = r'''
#include "__HEADER__"
#include "TFile.h"
#include <array>
#include <iostream>
int main(int argc, char** argv) {
 if(argc!=2)return 1;
 const int bins[6]={6,6,4,4,3,4};
 const double low[6]={0,0,-4,-4,0,-2},high[6]={4,4,4,4,3,2};
 THnSparseD clean("ranges","ranges",6,bins,low,high);clean.Sumw2();
 const std::vector<std::string> fields={"trigger_pt","associate_pt","trigger_eta","associate_eta","category","dphi"};
 for(int i=0;i<6;++i)clean.GetAxis(i)->SetName(fields[i].c_str());
 const double edges[7]={0,.15,.5,1,2.5,3,4};
 for(int i=0;i<2;++i)clean.GetAxis(i)->Set(6,edges);
 const std::vector<std::array<double,6>> events={
   {{2.5,.5,-4,4,.5,-1.5}}, // Both minima and eta endpoints included.
   {{std::nextafter(2.5,0.),.5,0,0,1.5,-.5}},
   {{2.5,std::nextafter(.5,0.),0,0,2.5,.5}},
   {{std::nextafter(2.5,3.),std::nextafter(.5,1.),0,0,1.5,1.5}},
   {{2.5,8,0,0,2.5,-1.5}}, // t<a is accepted; high overflow is retained.
   {{8,.5,0,0,.5,.5}},
   {{-.1,.5,0,0,.5,.5}}, {{2.5,-.1,0,0,1.5,.5}},
   {{2.5,.5,4.1,0,2.5,.5}}, {{0,0,0,0,2.5,1.5}}};
 double weight=1;
 for(auto event:events){
   for(int i:{2,3})if(event[i]==4)event[i]=std::nextafter(4.,0.);
   clean.Fill(event.data(),weight);weight*=2;
 }
 {
   TFile file(argv[1],"RECREATE");
   // Persist unrelated category/dphi state as well as stale declared ranges.
   for(int i=0;i<6;++i)clean.GetAxis(i)->SetRange(1,1);
   clean.Write();
 }
 TFile file(argv[1],"READ");
 auto* stored=dynamic_cast<THnSparseD*>(file.Get("ranges"));if(!stored)return 2;
 if(!stored->GetAxis(4)->TestBit(TAxis::kAxisRange))return 3;
 for(bool threshold:{true,false}) {
   double expected=0,expected2=0;weight=1;
   for(const auto& event:events){
     if(event[0]>=(threshold?2.5:0)&&event[1]>=(threshold?.5:0)&&std::abs(event[2])<=4&&std::abs(event[3])<=4){expected+=weight;expected2+=weight*weight;}
     weight*=2;
   }
   for(auto* histogram:{&clean,stored}){
     HadronizationQuery::ClearSparseRanges(*histogram);
     for(int i=0;i<6;++i)if(histogram->GetAxis(i)->TestBit(TAxis::kAxisRange))return 4;
     HadronizationQuery::SelectThreshold(*histogram,"trigger_pt",HadronizationQuery::ReadThreshold(threshold?">=2.5":"NONE"));
     HadronizationQuery::SelectThreshold(*histogram,"associate_pt",HadronizationQuery::ReadThreshold(threshold?">=0.5":"NONE"));
     for(const auto& field:{"trigger_eta","associate_eta"})HadronizationQuery::SelectPhysicalEta(*histogram,field,4);
     HadronizationQuery::NaturalSparseRows rows(*histogram,fields);
     double actual=0,actual2=0;while(rows.Next()){actual+=rows.value;actual2+=rows.sumw2;}
     if(actual!=expected||actual2!=expected2)return 5;
     histogram->GetAxis(4)->SetRange(2,2);histogram->GetAxis(5)->SetRange(2,2);
   }
 }
 std::cout<<"PERSISTED_RANGES_CLEARED_EQUALITY_OVERFLOW_RECTANGLE PASS\n";
}
'''.replace('__HEADER__', str(ROOT / 'pipeline/query/sparse.hpp'))
        self.fixture._compile(source, self.base / 'ranges.cpp', self.base / 'ranges')
        completed = subprocess.run([str(self.base / 'ranges'), str(self.base / 'ranges.root')],
            text=True, capture_output=True, env=self.fixture.environment)
        self.assertEqual((completed.returncode, completed.stderr), (0, ''), completed.stdout)

    def test_resigned_sparse_mutants_fail_independent_row_derivation(self):
        mutator = r'''
#include "TFile.h"
#include "TAxis.h"
#include "THnSparse.h"
#include "TKey.h"
#include "TTree.h"
#include "TObjString.h"
#include <cmath>
#include <fstream>
#include <memory>
#include <string>
int main(int argc,char** argv) {
  if (argc!=4&&argc!=6) return 2;
  TFile input(argv[1],"READ"),output(argv[2],"CREATE","",505);
  const std::string mode=argv[3];
  TIter keys(input.GetListOfKeys());
  while (auto* item=keys()) {
    auto* key=dynamic_cast<TKey*>(item);
    std::unique_ptr<TObject> object(key->ReadObj());
    if (mode=="payload" && (std::string(key->GetName())=="metadata" ||
                             std::string(key->GetName())=="query_spec")) {
      std::ifstream stream(argv[std::string(key->GetName())=="metadata"?4:5]);
      const std::string content{std::istreambuf_iterator<char>(stream),std::istreambuf_iterator<char>()};
      object=std::make_unique<TObjString>(content.c_str());
    }
    if (std::string(key->GetName())=="sparse_pairs") {
      auto* h=dynamic_cast<THnSparseD*>(object.get());
      if (mode=="sumw2") h->SetBinError2(0,h->GetBinError2(0)+1);
      if (mode=="cell") h->SetBinContent(Long64_t{0},h->GetBinContent(Long64_t{0})+1);
      if (mode=="axis") h->GetAxis(7)->SetName("wrong_pt");
      if (mode=="dictionary") h->GetAxis(4)->SetBinLabel(1,"999999");
    }
    output.cd();
    if (auto* tree=dynamic_cast<TTree*>(object.get())) {
      const std::string name=key->GetName();
      const bool depth=mode=="origin_depth"&&name=="origins";
      const bool pair=mode=="pair_dphi"&&name=="pairs";
      const bool weight=mode=="pair_weight"&&name=="pairs";
      Int_t depthValue=0;Double_t numericValue=0;
      if (depth) tree->SetBranchAddress("depth",&depthValue);
      if (pair) tree->SetBranchAddress("dphi",&numericValue);
      if (weight) tree->SetBranchAddress("weight",&numericValue);
      std::unique_ptr<TTree> copy(tree->CloneTree(depth||pair||weight?0:-1,"fast"));
      if (depth||pair||weight) for (Long64_t row=0;row<tree->GetEntries();++row) {
        tree->GetEntry(row);
        if (row==0) { if (depth) depthValue+=1000; else numericValue=std::nextafter(numericValue,INFINITY); }
        copy->Fill();
      }
      copy->Write(key->GetName());
    } else object->Write(key->GetName());
  }
  output.Close(); return 0;
}
'''
        self.fixture._compile(mutator, self.base / "query-mutator.cpp", self.base / "query-mutator")
        for mode in ("sumw2", "cell", "axis", "dictionary", "origin_depth", "pair_dphi", "pair_weight"):
            with self.subTest(mode=mode):
                directory = self.base / ("mutant-" + mode)
                shutil.copytree(self.workspace, directory)
                (directory / "query.root").unlink()
                subprocess.run([str(self.base / "query-mutator"), str(self.workspace / "query.root"),
                                str(directory / "query.root"), mode], check=True,
                               env=self.fixture.environment, capture_output=True)
                manifest = json.loads((directory / "manifest.json").read_text())
                for item in manifest["artifacts"]:
                    if item["path"] == "query.root":
                        item["bytes"] = (directory / "query.root").stat().st_size
                        item["sha256"] = self.query.reduce.sha_file(directory / "query.root")
                (directory / "manifest.json").write_text(json.dumps(manifest))
                result = self.cli("verify", "--workspace", directory)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("scientific content digest", result.stderr)
        # Recompute the changed ROOT's internal digest claims and replace both
        # internal/external metadata and query spec. Re-sign every artifact's
        # transport hash. The independently bound scientific manifest must still
        # refuse the change; container integrity alone is insufficient.
        directory = self.base / "mutant-rebound-content"
        shutil.copytree(self.workspace, directory)
        source = self.base / "mutant-origin_depth" / "query.root"
        environment, binary, _ = self.query.build_tool(self.work)
        output = self.query.execute(binary, ["content", directory / "query.tsv", source], environment)
        claims = dict(line.split("\t", 1) for line in output.splitlines())
        metadata = json.loads((directory / "metadata.json").read_text())
        metadata["query_content_digests"] = json.loads(claims["CONTENT_DIGESTS"])
        metadata["query_content_sha256"] = claims["SCIENTIFIC_CONTENT_SHA256"]
        (directory / "metadata.json").write_text(self.query.reduce.canonical(metadata))
        spec = self.query.layout_spec(json.loads((directory / "analysis.json").read_text()),
                                     json.loads((directory / "layout.json").read_text()),
                                     metadata["input_receipt"]["binding"],
                                     self.query.read_dictionary(directory / "dictionary.json"),
                                     metadata["query_content_sha256"],
                                     metadata["scientific_binding_sha256"],
                                     metadata["execution_attestation_sha256"])
        (directory / "query.tsv").write_text(spec)
        (directory / "query.root").unlink()
        subprocess.run([str(self.base / "query-mutator"), str(source), str(directory / "query.root"),
                        "payload", str(directory / "metadata.json"), str(directory / "query.tsv")],
                       check=True, env=environment, capture_output=True)
        manifest = json.loads((directory / "manifest.json").read_text())
        for artifact in manifest["artifacts"]:
            path = directory / artifact["path"]
            artifact["bytes"], artifact["sha256"] = path.stat().st_size, self.query.reduce.sha_file(path)
        (directory / "manifest.json").write_text(json.dumps(manifest))
        manifest["scientific_content_sha256"] = metadata["query_content_sha256"]
        (directory / "manifest.json").write_text(json.dumps(manifest))
        result = self.cli("verify", "--workspace", directory)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("trusted expected identity", result.stderr)
        provenance = self.base / "mutant-rebound-execution"
        shutil.copytree(self.workspace, provenance)
        metadata = json.loads((provenance / "metadata.json").read_text())
        metadata["query_build"]["binary_sha256"] = "0" * 64
        metadata["execution_attestation"] = self.query.execution_attestation(metadata)
        metadata["execution_attestation_sha256"] = self.query.payload_sha(metadata["execution_attestation"])
        (provenance / "metadata.json").write_text(self.query.reduce.canonical(metadata))
        (provenance / "query.tsv").write_text(self.query.layout_spec(
            json.loads((provenance / "analysis.json").read_text()),
            json.loads((provenance / "layout.json").read_text()),
            metadata["input_receipt"]["binding"],
            self.query.read_dictionary(provenance / "dictionary.json"),
            metadata["query_content_sha256"], metadata["scientific_binding_sha256"],
            metadata["execution_attestation_sha256"]))
        (provenance / "query.root").unlink()
        subprocess.run([str(self.base / "query-mutator"), str(self.workspace / "query.root"),
                        str(provenance / "query.root"), "payload", str(provenance / "metadata.json"),
                        str(provenance / "query.tsv")], check=True, env=environment, capture_output=True)
        manifest = json.loads((provenance / "manifest.json").read_text())
        for artifact in manifest["artifacts"]:
            path = provenance / artifact["path"]
            artifact["bytes"], artifact["sha256"] = path.stat().st_size, self.query.reduce.sha_file(path)
        (provenance / "manifest.json").write_text(json.dumps(manifest))
        result = self.cli("verify", "--workspace", provenance)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((provenance / "manifest.json").read_text())["scientific_content_sha256"],
                         self.trusted_content_sha256)
        result = self.cli("verify", "--workspace", provenance,
                          "--prepared-pack", self.prepared_pack)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explicit prepared build receipt", result.stderr)



if __name__ == "__main__":
    unittest.main()
