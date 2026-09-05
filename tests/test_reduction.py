import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

from helpers import ROOT, sha256
from test_analysis import MUTATOR, fixture_source


STATISTICS_HARNESS = r'''
#include "statistics.hpp"
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>
namespace HR=Hadronization::Reduction;
int main(int argc,char**argv){if(argc!=2)return 2;std::cout<<std::setprecision(17);const std::string mode=argv[1];
 if(mode=="scalar"){std::vector<std::vector<double>> z;const double n[]={0,1,1,2,3,5,7,11,19,29},d[]={1,2,3,4,5,7,11,13,17,31};for(int i=0;i<10;++i)z.push_back({n[i],d[i]});HR::DenominatorSeries ds{"D",{}, {},true,true};for(double v:d)ds.blocks.push_back(v);auto r=HR::PooledDeleteOne(z,[](const auto&v){return HR::Ratio(0,1,v);},{ds});std::cout<<r.center[0]<<' '<<r.leaveMean[0]<<' '<<r.covariance[0]<<' '<<r.originalBlockSem[0]<<' '<<r.complements.size()<<' '<<r.dof<<'\n';return 0;}
 if(mode=="vector"){std::vector<std::vector<double>> z;for(int i=1;i<=10;++i)z.push_back({double(i),double(11-i),double(i%3+1)});auto r=HR::PooledDeleteOne(z,[](const auto&v){return HR::Normalized(0,3,v);});std::cout<<r.center[0]+r.center[1]+r.center[2]<<' '<<r.covariance[1]<<' '<<HR::CovarianceNullResidual(r.covariance,3,{1,1,1})<<' '<<r.standardError[0]<<'\n';return 0;}
 if(mode=="statuses"){std::vector<std::vector<double>> z(10,std::vector<double>{-2,1,5,2,0});HR::DenominatorSeries cancelled{"T",{100,1,1,1,1,1,1,1,1,1},{},false,true};HR::DenominatorSeries surviving{"R",std::vector<double>(10,2),{},true,true};auto r=HR::PooledDeleteOne(z,[](const auto&v){return HR::Ratio(0,3,v);},{cancelled,surviving});std::cout<<r.valueStatus<<' '<<r.uncertaintyStatus<<' '<<r.center[0]<<' '<<r.cancelledParentDiagnostics.size()<<' '<<r.standardError[0]<<'\n';return 0;}
 if(mode=="missing"){std::vector<std::vector<double>> z(10,std::vector<double>{1,0});z[0][1]=10;HR::DenominatorSeries d{"D",{10,0,0,0,0,0,0,0,0,0},{},true,true};auto r=HR::PooledDeleteOne(z,[](const auto&v){return HR::Ratio(0,1,v);},{d});std::cout<<r.valueStatus<<' '<<r.uncertaintyStatus<<' '<<r.center[0]<<' '<<r.covariance.size()<<'\n';return 0;}
 if(mode=="unstable"){const double values[]={10,-1,-1,-1,-1,-1,-1,-1,-1,-1};std::vector<std::vector<double>> z;HR::DenominatorSeries d{"D",{}, {},true,true};for(double v:values){z.push_back({1,v});d.blocks.push_back(v);}auto r=HR::PooledDeleteOne(z,[](const auto&v){return HR::Ratio(0,1,v);},{d});std::cout<<r.valueStatus<<' '<<r.uncertaintyStatus<<' '<<r.center[0]<<' '<<r.complements.size()<<' '<<r.covariance.size()<<'\n';return 0;}
 if(mode=="event"){const auto c=HR::EventInfluenceCovariance({1.0},1,1,{14.0},{6.0},3);std::cout<<c[0]<<'\n';return 0;}return 3;}
'''


COMPACT_ORACLE = r'''
#include "TFile.h"
#include "TObjString.h"
#include "TTree.h"
#include <iomanip>
#include <iostream>
#include <string>
int main(int argc,char**argv){if(argc!=2)return 2;TFile f(argv[1],"READ");if(f.IsZombie())return 3;auto*c=dynamic_cast<TTree*>(f.Get("cells"));auto*g=dynamic_cast<TTree*>(f.Get("event_gram"));auto*m=dynamic_cast<TObjString*>(f.Get("metadata"));auto*r=dynamic_cast<TObjString*>(f.Get("receipt"));if(!c||!g||!m||!r)return 4;UInt_t p=0,s=0,b=0,n=0,k=0;Double_t v=0,a=0,w=0;ULong64_t fills=0;c->SetBranchAddress("projection_id",&p);c->SetBranchAddress("scope_id",&s);c->SetBranchAddress("block",&b);c->SetBranchAddress("bin",&n);c->SetBranchAddress("component",&k);c->SetBranchAddress("value",&v);c->SetBranchAddress("sumabs",&a);c->SetBranchAddress("row_sumw2",&w);c->SetBranchAddress("fills",&fills);std::cout<<std::setprecision(17);for(Long64_t i=0;i<c->GetEntries();++i){c->GetEntry(i);std::cout<<"C\t"<<p<<'\t'<<s<<'\t'<<b<<'\t'<<n<<'\t'<<k<<'\t'<<v<<'\t'<<a<<'\t'<<w<<'\t'<<fills<<'\n';}UInt_t l=0,rr=0;Double_t x=0;g->SetBranchAddress("projection_id",&p);g->SetBranchAddress("scope_id",&s);g->SetBranchAddress("block",&b);g->SetBranchAddress("left",&l);g->SetBranchAddress("right",&rr);g->SetBranchAddress("cross",&x);for(Long64_t i=0;i<g->GetEntries();++i){g->GetEntry(i);std::cout<<"G\t"<<p<<'\t'<<s<<'\t'<<b<<'\t'<<l<<'\t'<<rr<<'\t'<<x<<'\n';}std::cout<<"M\t"<<m->GetString().Data()<<'\n'<<"R\t"<<r->GetString().Data()<<'\n';return 0;}
'''


COMPACT_MUTATOR = r'''
#include "TFile.h"
#include "TObjString.h"
#include "TTree.h"
#include <string>
int main(int argc,char**argv){if(argc!=4)return 2;const std::string mode=argv[3];TFile input(argv[1],"READ");if(input.IsZombie())return 3;TFile output(argv[2],"RECREATE","",input.GetCompressionSettings());if(output.IsZombie())return 4;auto*c=dynamic_cast<TTree*>(input.Get("cells"));auto*g=dynamic_cast<TTree*>(input.Get("event_gram"));auto*m=dynamic_cast<TObjString*>(input.Get("metadata"));auto*r=dynamic_cast<TObjString*>(input.Get("receipt"));if(!c||!g||!m||!r)return 5;output.cd();auto*cc=c->CloneTree(-1,"fast");cc->SetName("cells");cc->Write();if(mode=="cycle")cc->Write();auto*gg=g->CloneTree(-1,"fast");gg->SetName("event_gram");gg->Write();std::string mt=m->GetString().Data(),rt=r->GetString().Data();auto flip=[](std::string&text,const std::string&key){const auto at=text.find(key);if(at==std::string::npos)return false;char&value=text[at+key.size()];value=value=='0'?'1':'0';return true;};if(mode=="scientific"){if(!flip(mt,"\"scientific_content_digest\":\""))return 6;}if(mode=="binding"){if(!flip(mt,"\"analysis_request_sha256\":\"")||!flip(rt,"\"analysis_request_sha256\":\""))return 7;}TObjString mo(mt.c_str());mo.Write("metadata");TObjString ro(rt.c_str());ro.Write("receipt");if(mode=="unknown"){TObjString extra("foreign");extra.Write("extra");}output.Close();return 0;}
'''


class ReductionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "pipeline/generate"))
        import runtime
        try:
            cls.runtime = runtime.resolve(require_root=True)
        except ValueError as error:
            raise unittest.SkipTest("ROOT unavailable for reduction fixture: {}".format(error))
        cls.environment = os.environ.copy()
        cls.environment.update(cls.runtime["environment"])
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name).resolve()
        cls.raw_root = cls.base / "raw"
        cls.work_root = cls.base / "analyze-work"
        cls.combined_root = cls.base / "analyzed-combined"
        cls.split_root = cls.base / "analyzed-split"
        cls.reduce_work = cls.base / "reduce-work"
        for path in (cls.raw_root, cls.work_root, cls.combined_root,
                     cls.split_root, cls.reduce_work):
            path.mkdir(parents=True)
        fixture = fixture_source()
        original_species = "std::vector<int>{421, -421, 431"
        if fixture.count(original_species) != 1:
            raise AssertionError("fixture heavy-species insertion point changed")
        fixture = fixture.replace(original_species,
                                  "std::vector<int>{421, -421, 411")
        fixture = fixture.replace(
            "const double ptValue = slot == 0 ? 1.0 : 0.15;",
            "const double ptValue = slot == 0 ? 1.0 : (slot == 2 ? 0.2 : 0.15);")
        fixture = fixture.replace(
            "const double etaValue = slot == 0 ? 4.0 : 4.1;",
            "const double etaValue = slot <= 2 ? 4.0 : 4.1;")
        activity_assignment = "mult10 = row; mult40 = row;"
        if fixture.count(activity_assignment) != 1:
            raise AssertionError("fixture activity insertion point changed")
        fixture = fixture.replace(
            activity_assignment,
            activity_assignment +
            "\n    if (fixtureLogical == 0 && row == 0) { mult10 = 3; mult40 = 3; }")
        fixture = fixture.replace("legacyMultiplicity = row;",
                                  "legacyMultiplicity = mult10;")
        cls._compile(fixture, cls.base / "fixture.cpp", cls.base / "fixture",
                     include_generate=True)
        cls._compile((ROOT / "pipeline/analyze/analyze.cpp").read_text(encoding="utf-8"),
                     cls.base / "analyze.cpp", cls.base / "analyzer",
                     include_generate=True)
        cls._compile(STATISTICS_HARNESS, cls.base / "statistics.cpp",
                     cls.base / "statistics", include_reduce=True, root=False)
        cls._compile(COMPACT_ORACLE, cls.base / "compact_oracle.cpp",
                     cls.base / "compact_oracle")
        cls._compile(MUTATOR, cls.base / "shard_mutator.cpp",
                     cls.base / "shard_mutator")
        cls._compile(COMPACT_MUTATOR, cls.base / "compact_mutator.cpp",
                     cls.base / "compact_mutator")
        cls.raw_paths = []
        for logical in range(10):
            path = cls.raw_root / "MONASH" / "opaque-{:03d}.root".format(logical)
            path.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run([str(cls.base / "fixture"), str(path), "valid",
                            str(logical), "0", "MONASH", "0", "3"],
                           check=True, env=cls.environment)
            cls.raw_paths.append(path)
        inspected = subprocess.run(
            [str(cls.base / "analyzer"), "inspect-raw", str(cls.raw_paths[0])],
            check=True, env=cls.environment, text=True, stdout=subprocess.PIPE)
        cls.raw_metadata = json.loads(inspected.stdout)
        cls._write_controls()
        cls.combined_plan = cls.work_root / "combined.json"
        cls.split_plan = cls.work_root / "split.json"
        cls._analyze("plan", "--campaign", str(cls.campaign_path),
                     "--manifest", str(cls.manifest_path), "--attempts",
                     str(cls.attempts_path), "--raw-root", str(cls.raw_root),
                     "--work-root", str(cls.work_root), "--output-root",
                     str(cls.combined_root), "--plan", str(cls.combined_plan),
                     "--target-bytes", "1000000000", check=True)
        cls._analyze("plan", "--campaign", str(cls.campaign_path),
                     "--manifest", str(cls.manifest_path), "--attempts",
                     str(cls.attempts_path), "--raw-root", str(cls.raw_root),
                     "--work-root", str(cls.work_root), "--output-root",
                     str(cls.split_root), "--plan", str(cls.split_plan),
                     "--target-bytes", "1", check=True)
        cls._analyze("run", "--plan", str(cls.combined_plan), check=True)
        cls._analyze("run", "--plan", str(cls.split_plan), check=True)
        cls.raw_hidden = cls.base / "raw-unavailable"
        cls.raw_root.rename(cls.raw_hidden)
        cls.combined_reduced = cls.base / "reduced-combined"
        cls.split_reduced = cls.base / "reduced-split"
        cls._reduce("run", "--plan", str(cls.combined_plan), "--analyzed-root",
                    str(cls.combined_root), "--work-root", str(cls.reduce_work),
                    "--output-root", str(cls.combined_reduced), check=True)
        cls._reduce("run", "--plan", str(cls.split_plan), "--analyzed-root",
                    str(cls.split_root), "--work-root", str(cls.reduce_work),
                    "--output-root", str(cls.split_reduced), check=True)
        cls.compact_root = next(cls.combined_reduced.rglob("*.root"))
        cls.compact_receipt = cls.compact_root.with_suffix(".json")
        cls.split_compact_root = next(cls.split_reduced.rglob("*.root"))
        cls.oracle = cls._compact_rows(cls.compact_root)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    @classmethod
    def _compile(cls, source, source_path, output, include_generate=False,
                 include_reduce=False, root=True):
        source_path.write_text(source, encoding="utf-8")
        command = [cls.environment["CXX"], "-std=c++17", "-O2", "-Wall",
                   "-Wextra", "-Wpedantic", "-Werror", str(source_path)]
        if include_generate:
            command.append("-I" + str(ROOT / "pipeline/generate"))
        if include_reduce:
            command.append("-I" + str(ROOT / "pipeline/reduce"))
        if root:
            command += shlex.split(subprocess.check_output(
                [cls.environment["ROOT_CONFIG"], "--cflags", "--libs"],
                text=True, env=cls.environment))
        subprocess.run(command + ["-o", str(output)], check=True,
                       env=cls.environment, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

    @classmethod
    def _write_controls(cls):
        control = cls.base / "control"
        (control / "config").mkdir(parents=True)
        (control / "data").mkdir()
        shutil.copy2(ROOT / "config/study.json", control / "config/study.json")
        campaign = json.loads((ROOT / "data/campaign.json").read_text(encoding="utf-8"))
        campaign["tune_order"] = ["MONASH"]
        campaign["logical_jobs_per_tune"] = 10
        campaign["successful_events_per_logical_job"] = 3
        campaign["successful_events_per_tune"] = 30
        campaign["blocks"] = {"count": 10, "logical_id_domain": [0, 9],
                              "logical_id_rule": "block=(logical_id%10)+1"}
        campaign["seed"]["attempt_domain"] = [0, 0]
        campaign["seed"]["tune_ordinals"] = {"MONASH": 0}
        campaign["attempt_evidence_inventory"] = {"file_count": 10,
                                                   "sha256": "a" * 64}
        campaign["accepted_source"]["tune_cards"] = {
            "MONASH": campaign["accepted_source"]["tune_cards"]["MONASH"]}
        campaign["accepted_source"]["producer_executable_sha256"] = "b" * 64
        campaign["accepted_source"]["producer_repository_commit"] = "c" * 40
        campaign["accepted_source"]["tune_cards"]["MONASH"][
            "accepted_effective_sha256"] = cls.raw_metadata["effective_settings_sha256"]
        cls.campaign_path = control / "data/campaign.json"
        cls.campaign_path.write_text(json.dumps(campaign, sort_keys=True), encoding="utf-8")
        rows = []
        for logical, path in enumerate(cls.raw_paths):
            storage = "MONASH/{}".format(path.name)
            rows.append({"accepted_attempt": 0,
                         "accepted_seed": 130000001 + logical,
                         "block": logical + 1, "bytes": path.stat().st_size,
                         "logical_id": logical, "raw_sha256": sha256(path),
                         "raw_storage_key": storage, "successful_events": 3,
                         "tune": "MONASH", "validation_log_sha256": "d" * 64,
                         "validation_receipt_sha256": "e" * 64})
        cls.manifest_path = control / "data/raw_manifest.jsonl"
        cls.manifest_path.write_text("".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in rows), encoding="utf-8")
        cls.attempts_path = control / "data/attempts.csv"
        cls.attempts_path.write_text(
            "tune,logical_id,attempt,seed,outcome,evidence_status,raw_storage_key\n" +
            "".join("MONASH,{0},0,{1},accepted,accepted_manifest_confirmed,"
                    "MONASH/opaque-{0:03d}.root\n".format(i, 130000001 + i)
                    for i in range(10)), encoding="utf-8")

    @classmethod
    def _analyze(cls, *arguments, check=False):
        result = subprocess.run([str(ROOT / "hadronization"), "analyze"] +
                                list(arguments), cwd=str(ROOT), env=cls.environment,
                                text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if check and result.returncode:
            raise AssertionError("analyze failed: {}".format(result.stderr))
        return result

    @classmethod
    def _reduce(cls, *arguments, check=False, environment=None):
        result = subprocess.run([str(ROOT / "hadronization"), "reduce"] +
                                list(arguments), cwd=str(ROOT),
                                env=environment or cls.environment, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check and result.returncode:
            raise AssertionError("reduce failed: {}".format(result.stderr))
        return result

    @classmethod
    def _compact_rows(cls, path):
        result = subprocess.run([str(cls.base / "compact_oracle"), str(path)],
                                check=True, env=cls.environment, text=True,
                                stdout=subprocess.PIPE)
        parsed = {"cells": {}, "gram": {}, "metadata": None, "receipt": None}
        for line in result.stdout.splitlines():
            kind, *values = line.split("\t")
            if kind == "C":
                key = tuple(map(int, values[:5]))
                parsed["cells"][key] = (float(values[5]), float(values[6]),
                                         float(values[7]), int(values[8]))
            elif kind == "G":
                parsed["gram"][tuple(map(int, values[:5]))] = float(values[5])
            elif kind == "M":
                parsed["metadata"] = json.loads(values[0])
            elif kind == "R":
                parsed["receipt"] = json.loads(values[0])
        return parsed

    @staticmethod
    def _rebind_storage(receipt_path, root_path):
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["storage_identity"]["root_bytes"] = root_path.stat().st_size
        receipt["storage_identity"]["root_sha256"] = sha256(root_path)
        receipt["storage_identity_sha256"] = hashlib.sha256(
            json.dumps(receipt["storage_identity"], sort_keys=True,
                       separators=(",", ":")).encode("ascii")).hexdigest()
        receipt_path.write_text(json.dumps(receipt, sort_keys=True), encoding="utf-8")

    def test_analysis_request_is_downstream_and_expands_exact_registry(self):
        spec = importlib.util.spec_from_file_location(
            "reduction_run_test", str(ROOT / "pipeline/reduce/run.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        analysis, digest = module.checked_analysis(ROOT / "config/analysis.json")
        self.assertEqual(analysis["version"], "1.0.0")
        states, pairs = module.state_registry(analysis)
        self.assertEqual(len(states), 50)
        self.assertEqual(len(pairs), 300)
        self.assertEqual({item["sign"] for item in pairs}, {-1, 1})
        self.assertEqual(digest, sha256(ROOT / "config/analysis.json"))
        self.assertNotIn("analysis", json.loads(
            (ROOT / "config/study.json").read_text(encoding="utf-8")))

    def test_single_numerical_core_matches_independent_hand_calculation(self):
        output = subprocess.check_output([str(self.base / "statistics"), "scalar"],
                                         text=True).split()
        center, leave_mean, covariance, old_sem = map(float, output[:4])
        numerators = [0, 1, 1, 2, 3, 5, 7, 11, 19, 29]
        denominators = [1, 2, 3, 4, 5, 7, 11, 13, 17, 31]
        expected_center = sum(numerators) / sum(denominators)
        leaves = [(sum(numerators) - numerators[i]) /
                  (sum(denominators) - denominators[i]) for i in range(10)]
        expected_mean = sum(leaves) / 10
        expected_covariance = 0.9 * sum(
            (value - expected_mean) ** 2 for value in leaves)
        blocks = [numerators[i] / denominators[i] for i in range(10)]
        block_mean = sum(blocks) / 10
        expected_old = math.sqrt(sum((value - block_mean) ** 2 for value in blocks) / 90)
        self.assertAlmostEqual(center, expected_center, places=15)
        self.assertAlmostEqual(leave_mean, expected_mean, places=15)
        self.assertAlmostEqual(covariance, expected_covariance, places=15)
        self.assertAlmostEqual(old_sem, expected_old, places=15)
        self.assertEqual(output[4:], ["10", "9"])
        self.assertNotAlmostEqual(expected_old ** 2, expected_covariance,
                                  places=8)
        dropped = leaves[:-1]
        dropped_mean = sum(dropped) / len(dropped)
        dropped_covariance = (len(dropped) - 1) / len(dropped) * sum(
            (value - dropped_mean) ** 2 for value in dropped)
        pooled_centering = 0.9 * sum(
            (value - expected_center) ** 2 for value in leaves)
        wrong_factor = sum((value - expected_mean) ** 2 for value in leaves) / 9
        for mutant in (dropped_covariance, pooled_centering, wrong_factor):
            self.assertNotAlmostEqual(mutant, expected_covariance, places=12)
        second_numerators = [value + index for index, value in enumerate(numerators)]
        second_denominators = [value + 2 for value in denominators]
        second_leaves = [
            (sum(second_numerators) - second_numerators[index]) /
            (sum(second_denominators) - second_denominators[index])
            for index in range(10)]
        second_mean = sum(second_leaves) / 10
        independent_tunes = expected_covariance + 0.9 * sum(
            (value - second_mean) ** 2 for value in second_leaves)
        all_n = numerators + second_numerators
        all_d = denominators + second_denominators
        pooled_tune_leaves = [(sum(all_n) - all_n[index]) /
                              (sum(all_d) - all_d[index])
                              for index in range(20)]
        pooled_tune_mean = sum(pooled_tune_leaves) / 20
        tune_pooling = 19 / 20 * sum(
            (value - pooled_tune_mean) ** 2 for value in pooled_tune_leaves)
        self.assertNotAlmostEqual(tune_pooling, independent_tunes, places=12)

    def test_full_vector_covariance_and_status_edges(self):
        vector = subprocess.check_output(
            [str(self.base / "statistics"), "vector"], text=True).split()
        self.assertAlmostEqual(float(vector[0]), 1.0, places=15)
        self.assertNotEqual(float(vector[1]), 0.0)
        self.assertLess(float(vector[2]), 1e-14)
        self.assertGreater(float(vector[3]), 0.0)
        status = subprocess.check_output(
            [str(self.base / "statistics"), "statuses"], text=True).split()
        self.assertEqual(status[:2], ["AVAILABLE", "AVAILABLE_ZERO_DISPERSION"])
        self.assertEqual(float(status[2]), -1.0)
        self.assertNotEqual(max(0.0, float(status[2])), float(status[2]))
        self.assertEqual(status[3], "1")
        self.assertEqual(float(status[4]), 0.0)
        missing = subprocess.check_output(
            [str(self.base / "statistics"), "missing"], text=True).split()
        self.assertEqual(missing,
                         ["UNSTABLE_DENOMINATOR", "LEAVE_DENOMINATOR_ZERO",
                          "1", "0"])
        unstable = subprocess.check_output(
            [str(self.base / "statistics"), "unstable"], text=True).split()
        self.assertEqual(unstable,
                         ["UNSTABLE_DENOMINATOR",
                          "DENOMINATOR_STATISTICALLY_UNRESOLVED",
                          "10", "10", "0"])
        event = subprocess.check_output(
            [str(self.base / "statistics"), "event"], text=True).strip()
        self.assertEqual(float(event), 3.0)

    def test_complete_admission_is_regrouping_invariant_and_raw_independent(self):
        first = json.loads(self.compact_receipt.read_text(encoding="utf-8"))
        second = json.loads(self.split_compact_root.with_suffix(".json").read_text(
            encoding="utf-8"))
        self.assertFalse(self.raw_root.exists())
        self.assertEqual(first["state"], "PUBLICATION_ELIGIBLE")
        self.assertEqual(first["scientific_identity"]["scientific_content_digest"],
                         second["scientific_identity"]["scientific_content_digest"])
        self.assertNotEqual(first["scientific_identity"]["parent_shard_set_digest"],
                            second["scientific_identity"]["parent_shard_set_digest"])
        self.assertEqual(first["scientific_identity"]["sources"], 10)
        self.assertEqual(first["scientific_identity"]["events"], 30)

    def test_compact_schema_domains_profiles_activities_and_diagnostics(self):
        metadata = self.oracle["metadata"]
        receipt = self.oracle["receipt"]
        self.assertEqual(metadata["schema"], "hadronization_compact_plot_source_v1")
        self.assertEqual(len(metadata["pair_queries"]), 300)
        self.assertEqual([item["id"] for item in metadata["profiles"]],
                         ["inclusive", "historical_1p0_0p15"])
        self.assertEqual([item["physical_field"] for item in metadata["activities"]],
                         ["a15_eta4", "a15_eta1"])
        self.assertEqual({item["name"] for item in metadata["projections"]},
                         {"activity_hist", "ordered_pair_scalar", "trigger_scalar",
                          "dphi_correlation", "origin", "closure_category_dphi",
                          "closure_species", "closure_full_visible", "G9", "T1"})
        self.assertFalse(metadata["pooled_copy"])
        self.assertEqual(receipt["estimator_policy_id"],
                         "pooled_delete_one_source_block_jackknife_v2")
        self.assertEqual(receipt["estimator_audit"]["evaluated_scalar_groups"],
                         150 * 2 * 2 * 12)
        self.assertIn("maximum_normalized_covariance_null_residual",
                      receipt["estimator_audit"])
        accounting = receipt["block_accounting"]["blocks"]
        self.assertEqual(len(accounting), 10)
        self.assertEqual({item["successful_events"] for item in accounting}, {3})
        self.assertEqual({item["sources"] for item in accounting}, {1})
        activities = receipt["activity_receipts"]
        self.assertTrue(any(not item["stable"] for activity in activities
                            for item in activity["classes"]))
        threshold = next(item for activity in activities
                         for item in activity["thresholds"]
                         if item["percentile"] == 70)
        self.assertEqual(len(threshold["below_margins"]), 10)
        self.assertEqual(len(threshold["through_margins"]), 10)
        self.assertTrue(any(value != threshold["pooled"]
                            for value in threshold["complements"]))

    def test_strict_profile_eta_endpoints_g9_t1_and_visible_closure_are_distinct(self):
        metadata = self.oracle["metadata"]
        scopes = {item["id"]: item for item in metadata["scopes"]}
        inclusive = {scope_id for scope_id, item in scopes.items()
                     if item["family"] == "pair" and item["profile"] == "inclusive"}
        historical = {scope_id for scope_id, item in scopes.items()
                      if item["family"] == "pair" and
                      item["profile"] == "historical_1p0_0p15"}
        inclusive_pairs = sum(value[0] for key, value in self.oracle["cells"].items()
                              if key[0] == 2 and key[1] in inclusive)
        historical_pairs = sum(value[0] for key, value in self.oracle["cells"].items()
                               if key[0] == 2 and key[1] in historical)
        self.assertGreater(inclusive_pairs, historical_pairs)
        self.assertTrue(any(key[0] == 9 for key in self.oracle["cells"]))
        self.assertTrue(any(key[0] == 10 for key in self.oracle["cells"]))
        dynamic = self.oracle["receipt"]["dynamic_species"]
        closure_species = dynamic["closure_species_pdgs"]
        low_pt_visible = closure_species.index(-421)
        self.assertTrue(any(key[0] == 7 and
                            key[3] % len(closure_species) == low_pt_visible
                            for key in self.oracle["cells"]))
        self.assertEqual(metadata["axes"]["dphi"]["low"], -math.pi / 2)
        self.assertEqual(metadata["axes"]["dphi"]["high"], 3 * math.pi / 2)

    def test_event_gram_is_event_aggregated_not_per_fill_squares(self):
        # A multi-pair fixture necessarily creates an O/S cross term. Its stored
        # event product can exceed either individual row-sumw2, which a per-fill
        # squaring implementation cannot produce for distinct primitives.
        cross = [value for key, value in self.oracle["gram"].items()
                 if key[3] != key[4] and value != 0.0]
        self.assertTrue(cross)
        row_sumw2 = [value[2] for key, value in self.oracle["cells"].items()
                     if key[0] in {2, 3}]
        self.assertGreater(max(map(abs, cross)), 0.0)
        self.assertGreater(max(row_sumw2), 0.0)

    def test_configurable_three_class_request_changes_only_downstream_projection(self):
        analysis = json.loads((ROOT / "config/analysis.json").read_text(encoding="utf-8"))
        analysis["percentile_intervals"] = [[0, 10], [10, 50], [50, 100]]
        path = self.base / "analysis-three.json"
        path.write_text(json.dumps(analysis, sort_keys=True), encoding="utf-8")
        output = self.base / "reduced-three"
        result = self._reduce("run", "--plan", str(self.combined_plan),
                              "--analysis", str(path), "--analyzed-root",
                              str(self.combined_root), "--work-root",
                              str(self.reduce_work), "--output-root", str(output),
                              check=True)
        root = next(output.rglob("*.root"))
        compact = self._compact_rows(root)
        pair_scopes = [item for item in compact["metadata"]["scopes"]
                       if item["family"] == "pair"]
        self.assertEqual({item["class_id"] for item in pair_scopes}, {0, 1, 2, 3})
        self.assertNotEqual(sha256(root), sha256(self.compact_root))
        self.assertIn("PUBLICATION_ELIGIBLE", result.stdout)

    def test_bounded_profile_changes_reuse_the_same_accepted_shards(self):
        spec = importlib.util.spec_from_file_location(
            "reduction_profile_test", str(ROOT / "pipeline/reduce/run.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        analysis = json.loads((ROOT / "config/analysis.json").read_text(encoding="utf-8"))
        analysis["profiles"].append({
            "id": "strict_2p0_0p25",
            "trigger_pt": {"operator": ">", "value": 2.0},
            "associate_pt": {"operator": ">", "value": 0.25}})
        path = self.base / "analysis-profile.json"
        path.write_text(json.dumps(analysis, sort_keys=True), encoding="utf-8")
        checked, changed_digest = module.checked_analysis(path)
        self.assertEqual(len(checked["profiles"]), 3)
        self.assertNotEqual(changed_digest, sha256(ROOT / "config/analysis.json"))
        output = self.base / "reduced-profile"
        self._reduce("run", "--plan", str(self.combined_plan), "--analysis",
                     str(path), "--analyzed-root", str(self.combined_root),
                     "--work-root", str(self.reduce_work), "--output-root",
                     str(output), check=True)
        receipt = json.loads(next(output.rglob("*.json")).read_text(encoding="utf-8"))
        self.assertEqual(receipt["state"], "PUBLICATION_ELIGIBLE")
        self.assertEqual(receipt["scientific_identity"]["sources"], 10)
        self.assertNotEqual(receipt["scientific_identity"][
            "analysis_request_sha256"], json.loads(
                self.compact_receipt.read_text(encoding="utf-8"))[
                    "scientific_identity"]["analysis_request_sha256"])
        invalids = []
        duplicate = json.loads(json.dumps(analysis))
        duplicate["profiles"][2]["id"] = "inclusive"
        invalids.append(duplicate)
        operator = json.loads(json.dumps(analysis))
        operator["profiles"][2]["trigger_pt"]["operator"] = ">="
        invalids.append(operator)
        malformed = json.loads(json.dumps(analysis))
        malformed["profiles"][2]["id"] = "bad profile"
        invalids.append(malformed)
        for index, payload in enumerate(invalids):
            mutant = self.base / "profile-invalid-{}.json".format(index)
            mutant.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            with self.assertRaises(ValueError):
                module.checked_analysis(mutant)

    def test_missing_and_foreign_shards_are_refused_before_reduction(self):
        copied = self.base / "admission-mutant"
        shutil.copytree(self.combined_root, copied)
        campaign_dir = next(path for path in copied.iterdir() if path.is_dir())
        missing = campaign_dir / "shard-0000.json"
        saved = missing.read_bytes()
        missing.unlink()
        result = self._reduce("run", "--plan", str(self.combined_plan),
                              "--analyzed-root", str(copied), "--work-root",
                              str(self.reduce_work), "--output-root",
                              str(self.base / "missing-output"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("exact shard-set closure differs", result.stderr)
        missing.write_bytes(saved)
        (campaign_dir / "foreign.root").write_bytes(b"foreign")
        result = self._reduce("run", "--plan", str(self.combined_plan),
                              "--analyzed-root", str(copied), "--work-root",
                              str(self.reduce_work), "--output-root",
                              str(self.base / "foreign-output"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("foreign", result.stderr)
        for mode in ("missing", "duplicate", "foreign"):
            mutant = self.base / ("source-" + mode)
            shutil.copytree(self.combined_root, mutant)
            receipt_path = next(mutant.rglob("shard-*.json"))
            payload = json.loads(receipt_path.read_text(encoding="utf-8"))
            if mode == "missing":
                payload["sources"] = payload["sources"][:-1]
            elif mode == "duplicate":
                payload["sources"][1] = payload["sources"][0]
            else:
                payload["sources"][0]["manifest_row"]["logical_id"] = 999
            receipt_path.write_text(json.dumps(payload, sort_keys=True),
                                    encoding="utf-8")
            result = self._reduce(
                "run", "--plan", str(self.combined_plan), "--analyzed-root",
                str(mutant), "--work-root", str(self.reduce_work),
                "--output-root", str(self.base / ("source-output-" + mode)))
            self.assertEqual(result.returncode, 2)
            self.assertIn("receipt/plan/source binding differs", result.stderr)
        dependency_mutant = self.base / "dependency-commit"
        shutil.copytree(self.combined_root, dependency_mutant)
        receipt_path = next(dependency_mutant.rglob("shard-*.json"))
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        payload["scientific_identity"]["lossless_dependency_identity"][
            "accepted_raw_definition"]["producer_repository_commit"] = "0" * 40
        receipt_path.write_text(json.dumps(payload, sort_keys=True),
                                encoding="utf-8")
        result = self._reduce(
            "run", "--plan", str(self.combined_plan), "--analyzed-root",
            str(dependency_mutant), "--work-root", str(self.reduce_work),
            "--output-root", str(self.base / "dependency-commit-output"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("dependency/commit marker differs", result.stderr)

    def test_consumed_rows_are_validated_after_receipt_admission(self):
        accounting_mutant = self.base / "consumed-row-accounting"
        shutil.copytree(self.combined_root, accounting_mutant)
        receipt_path = next(accounting_mutant.rglob("shard-*.json"))
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        payload["rows"]["events"] += 1
        payload["rows"]["heavy"] -= 1
        receipt_path.write_text(json.dumps(payload, sort_keys=True),
                                encoding="utf-8")
        result = self._reduce(
            "run", "--plan", str(self.combined_plan), "--analyzed-root",
            str(accounting_mutant), "--work-root", str(self.reduce_work),
            "--output-root", str(self.base / "consumed-row-accounting-output"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("receipt row accounting differs: events", result.stderr)
        expectations = {"wrong_cache": "pair cached authority",
                        "invalid_domain": "trigger row order/domain",
                        "shuffled_rows": "pair structural ownership"}
        for mode, diagnostic in expectations.items():
            mutant = self.base / ("consumed-" + mode)
            shutil.copytree(self.combined_root, mutant)
            root_path = next(mutant.rglob("shard-*.root"))
            replacement = root_path.with_suffix(".mutated.root")
            subprocess.run([str(self.base / "shard_mutator"), str(root_path),
                            str(replacement), mode], check=True,
                           env=self.environment)
            os.replace(str(replacement), str(root_path))
            self._rebind_storage(root_path.with_suffix(".json"), root_path)
            result = self._reduce(
                "run", "--plan", str(self.combined_plan), "--analyzed-root",
                str(mutant), "--work-root", str(self.reduce_work),
                "--output-root", str(self.base / ("consumed-output-" + mode)))
            self.assertEqual(result.returncode, 2)
            self.assertIn(diagnostic, result.stderr)

    def test_root_first_promotion_recovery_and_tamper_refusal(self):
        output = self.base / "interrupted"
        environment = dict(self.environment)
        environment["HADRONIZATION_REDUCE_FAIL_AFTER_ROOT_PROMOTION"] = "1"
        failed = self._reduce("run", "--plan", str(self.combined_plan),
                              "--analyzed-root", str(self.combined_root),
                              "--work-root", str(self.reduce_work),
                              "--output-root", str(output), environment=environment)
        self.assertEqual(failed.returncode, 2)
        self.assertIn("injected interruption", failed.stderr)
        root = next(output.rglob("*.root"))
        self.assertFalse(root.with_suffix(".json").exists())
        before = sha256(root)
        recovered = self._reduce("run", "--plan", str(self.combined_plan),
                                 "--analyzed-root", str(self.combined_root),
                                 "--work-root", str(self.reduce_work),
                                 "--output-root", str(output), check=True)
        self.assertIn("RECOVERED", recovered.stdout)
        self.assertEqual(sha256(root), before)
        no_overwrite = self._reduce("run", "--plan", str(self.combined_plan),
                                    "--analyzed-root", str(self.combined_root),
                                    "--work-root", str(self.reduce_work),
                                    "--output-root", str(output), "--no-resume")
        self.assertEqual(no_overwrite.returncode, 2)
        foreign_output = self.base / "foreign-recovery"
        foreign_root = foreign_output / self.compact_root.parent.name / self.compact_root.name
        foreign_root.parent.mkdir(parents=True)
        subprocess.run([str(self.base / "compact_mutator"),
                        str(self.compact_root), str(foreign_root), "binding"],
                       check=True, env=self.environment)
        refused = self._reduce(
            "run", "--plan", str(self.combined_plan), "--analyzed-root",
            str(self.combined_root), "--work-root", str(self.reduce_work),
            "--output-root", str(foreign_output))
        self.assertEqual(refused.returncode, 2)
        self.assertIn("embedded analysis_sha256 binding differs", refused.stderr)
        self.assertFalse(foreign_root.with_suffix(".json").exists())
        receipt = root.with_suffix(".json")
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        payload["scientific_identity"]["scientific_content_digest"] = "0" * 64
        receipt.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        verify = self._reduce("verify", "--root", str(root), "--receipt",
                              str(receipt), "--work-root", str(self.reduce_work))
        self.assertEqual(verify.returncode, 2)
        self.assertIn("nested digest differs", verify.stderr)

    def test_compact_unknown_cycles_config_and_scientific_tampering_fail(self):
        for mode in ("unknown", "cycle", "scientific", "binding"):
            root_path = self.base / ("compact-" + mode + ".root")
            subprocess.run([str(self.base / "compact_mutator"),
                            str(self.compact_root), str(root_path), mode],
                           check=True, env=self.environment)
            receipt_path = root_path.with_suffix(".json")
            shutil.copy2(self.compact_receipt, receipt_path)
            self._rebind_storage(receipt_path, root_path)
            verify = self._reduce("verify", "--root", str(root_path),
                                  "--receipt", str(receipt_path), "--work-root",
                                  str(self.reduce_work))
            self.assertEqual(verify.returncode, 2)
            expected = ("exact object set" if mode == "unknown" else
                        "duplicate ROOT key/cycle" if mode == "cycle" else
                        "scientific digest differs" if mode == "scientific" else
                        "metadata_sha256")
            self.assertIn(expected, verify.stderr)
        config = json.loads((ROOT / "config/analysis.json").read_text(encoding="utf-8"))
        config["version"] = "session-tag"
        bad_config = self.base / "analysis-tampered.json"
        bad_config.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
        verify = self._reduce("verify", "--root", str(self.compact_root),
                              "--receipt", str(self.compact_receipt),
                              "--analysis", str(bad_config), "--work-root",
                              str(self.reduce_work))
        self.assertEqual(verify.returncode, 2)
        self.assertIn("version differs", verify.stderr)
        receipt_path = self.base / "scientific-sidecar.json"
        payload = json.loads(self.compact_receipt.read_text(encoding="utf-8"))
        payload["scientific_identity"]["scientific_content_digest"] = "0" * 64
        payload["scientific_identity_sha256"] = hashlib.sha256(json.dumps(
            payload["scientific_identity"], sort_keys=True,
            separators=(",", ":")).encode("ascii")).hexdigest()
        receipt_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        verify = self._reduce("verify", "--root", str(self.compact_root),
                              "--receipt", str(receipt_path), "--work-root",
                              str(self.reduce_work))
        self.assertEqual(verify.returncode, 2)
        self.assertIn("scientific digest/readback differs", verify.stderr)

    def test_public_verify_and_explain_are_exact(self):
        verify = self._reduce("verify", "--root", str(self.compact_root),
                              "--receipt", str(self.compact_receipt),
                              "--work-root", str(self.reduce_work), check=True)
        self.assertIn("VERIFIED", verify.stdout)
        explain = self._reduce("explain", "--root", str(self.compact_root),
                               "--receipt", str(self.compact_receipt),
                               "--work-root", str(self.reduce_work), check=True)
        self.assertEqual(json.loads(explain.stdout)["state"],
                         "PUBLICATION_ELIGIBLE")


if __name__ == "__main__":
    unittest.main()
