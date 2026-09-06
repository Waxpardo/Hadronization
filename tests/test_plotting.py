import csv
import copy
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

from helpers import ROOT, TUNES, sha256
from test_analysis import fixture_source
from test_reduction import COMPACT_MUTATOR, COMPACT_ORACLE


GEOMETRY_AND_RATIO = r'''
#include "projection.hpp"
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <string>
#include <vector>
namespace HP=Hadronization::Plot;namespace HR=Hadronization::Reduction;
void family(const std::vector<std::vector<double>>& values,std::size_t component){
 for(std::size_t block=0;block<values.size();++block){if(block)std::cout<<';';
   const double value=values[block][component];
   if(std::isfinite(value))std::cout<<value;else std::cout<<'-';}
 std::cout<<'\n';
}
int main(){
 std::cout<<std::setprecision(17);
 std::cout<<HP::DeltaPhi(-HP::kPi/2,0)<<' '<<HP::DeltaPhi(3*HP::kPi/2,0)<<' '
          <<HP::DeltaPhi(.25,-.75)<<' '
          <<HP::DeltaPhi(.25,HP::AssociatePhi(.25,1.0))<<'\n';
 std::vector<std::vector<double>> a,b;
 HP::BlockSeries referencePrimitive;
 referencePrimitive.exact=true;
 for(int i=0;i<10;++i){
   a.push_back({double(i+2),double(i+5)});
   b.push_back({double(3*i+4),double(i+7)});
   referencePrimitive.values.push_back(double(3*i+4));
   referencePrimitive.absoluteErrorBounds.push_back(0.0);
 }
 auto make=[](const auto& values){return HP::Estimate(
   values,[](const auto& pooled){return HR::Ratio(0,1,pooled);});};
 const auto x=make(a),y=make(b);
 const auto ratio=HP::IndependentRatio(
   x,y,{HP::Denominator("reference_tune_numerator",referencePrimitive)});
 std::cout<<ratio.estimate.center[0]<<' '<<ratio.estimate.covariance[0]<<' '
          <<ratio.estimate.standardError[0]<<' '<<ratio.estimate.leaveMean[0]<<' '
          <<ratio.referenceLeaveMean[0]<<'\n';
 family(ratio.estimate.complements,0);
 family(ratio.referenceComplements,0);

 HP::Domains domains;for(int block=1;block<=10;++block)domains.blockIds.push_back(block);
 HP::Source source(domains);
 for(int block=1;block<=10;++block){
   source.AddCell({2,0,unsigned(block),0,0},{1.0,1.0e16,1.0,2});
   source.AddCell({2,0,unsigned(block),1,0},
                  {0.9999999999999999,1.0e16,1.0,2});
 }
 const auto net=HP::Difference(source.Series(2,0,0,0),source.Series(2,0,1,0));
 std::vector<std::vector<double>> identityBlocks(10,std::vector<double>{1.0});
 auto identity=[](const auto& pooled){return HR::FunctionValue{true,{pooled[0]}, {}};};
 const auto typed=HP::Estimate(identityBlocks,identity,
                              {HP::Denominator("typed_net",net,false)});
 auto dropped=net;dropped.absoluteErrorBounds.clear();
 const auto metadataDrop=HP::Estimate(identityBlocks,identity,
                                      {HP::Denominator("typed_net",dropped,false)});
 auto forced=net;forced.exact=true;
 const auto forcedExact=HP::Estimate(identityBlocks,identity,
                                     {HP::Denominator("typed_net",forced,false)});
 std::cout<<typed.estimate.valueStatus<<' '<<metadataDrop.estimate.valueStatus<<' '
          <<forcedExact.estimate.valueStatus<<' '<<net.values[0]<<' '
          <<net.absoluteErrorBounds[0]<<'\n';

 HR::DenominatorSeries exactZero{"cancelled_zero",std::vector<double>(10,0.0),
                                  {},false,true};
 const auto pooledZero=HP::Estimate(identityBlocks,identity,{exactZero});
 std::vector<double> complementBlocks={9,1,1,1,1,1,1,1,1,-8};
 HR::DenominatorSeries exactComplement{"cancelled_complement",complementBlocks,
                                       {},false,true};
 const auto complementZero=HP::Estimate(identityBlocks,identity,{exactComplement});
 HR::DenominatorSeries numericComplement=exactComplement;
 numericComplement.id="cancelled_numeric_complement";
 numericComplement.exact=false;
 numericComplement.absoluteErrorBounds=std::vector<double>(10,0.0);
 numericComplement.absoluteErrorBounds.back()=0.5;
 const auto complementUnresolved=HP::Estimate(identityBlocks,identity,
                                               {numericComplement});
 std::cout<<pooledZero.estimate.valueStatus<<' '
          <<complementZero.estimate.valueStatus<<' '
          <<complementZero.estimate.uncertaintyStatus<<' '
          <<complementUnresolved.estimate.valueStatus<<' '
          <<complementUnresolved.estimate.uncertaintyStatus<<'\n';

 HR::DenominatorSeries low{"low_information",{20,-1,-1,-1,-1,-1,-1,-1,-1,-1},
                            {},false,true};
 const auto cancelledLow=HP::Estimate(identityBlocks,identity,{low});
 low.algebraicallySurvives=true;
 const auto survivingLow=HP::Estimate(identityBlocks,identity,{low});
 std::cout<<cancelledLow.estimate.valueStatus<<' '
          <<cancelledLow.estimate.uncertaintyStatus<<' '
          <<cancelledLow.estimate.reasons.size()<<' '
          <<survivingLow.estimate.valueStatus<<' '
          <<survivingLow.estimate.uncertaintyStatus<<'\n';

 auto boundary=HP::Estimate(a,[](const auto& pooled){return HR::Ratio(0,1,pooled);},
                            {},{"CLASS_BOUNDARY_UNSTABLE"});
 std::cout<<boundary.estimate.center[0]<<' '<<boundary.estimate.valueStatus<<' '
          <<boundary.estimate.uncertaintyStatus<<' '
          <<boundary.estimate.covariance.size()<<' '<<boundary.diagnostic<<'\n';

 std::vector<std::vector<double>> sourceBlocks,referenceBlocks;
 std::vector<HP::BlockSeries> referenceBins(3);
 for(auto& series:referenceBins)series.exact=true;
 for(int i=0;i<10;++i){
   sourceBlocks.push_back({double(i+2),double(2*i+3),double(i+1)});
   referenceBlocks.push_back({double(2*i+5),0.0,double(i+4)});
   for(std::size_t component=0;component<3;++component){
     referenceBins[component].values.push_back(referenceBlocks.back()[component]);
     referenceBins[component].absoluteErrorBounds.push_back(0.0);
   }
 }
 auto normalized=[](const auto& blocks){
   HP::BlockSeries total;total.exact=true;
   for(const auto& block:blocks){
     total.values.push_back(std::accumulate(block.begin(),block.end(),0.0));
     total.absoluteErrorBounds.push_back(0.0);
   }
   return HP::Estimate(blocks,[](const auto& pooled){return HR::Normalized(0,3,pooled);},
                       {HP::Denominator("total",total)});
 };
 const auto vectorRatio=HP::IndependentRatio(
   normalized(sourceBlocks),normalized(referenceBlocks),
   {HP::Denominator("reference_bin_0",referenceBins[0]),
    HP::Denominator("reference_bin_1",referenceBins[1]),
    HP::Denominator("reference_bin_2",referenceBins[2])});
 std::cout<<HP::ValueStatus(vectorRatio,0)<<' '<<HP::ValueStatus(vectorRatio,1)<<' '
          <<HP::ValueStatus(vectorRatio,2)<<' '
          <<HP::UncertaintyStatus(vectorRatio,0)<<' '
          <<HP::UncertaintyStatus(vectorRatio,1)<<' '
          <<HP::UncertaintyStatus(vectorRatio,2)<<' '
          <<vectorRatio.estimate.covariance[2]<<'\n';
 family(vectorRatio.estimate.complements,0);
 family(vectorRatio.estimate.complements,2);
 family(vectorRatio.referenceComplements,0);
 family(vectorRatio.referenceComplements,2);
 int finiteInvalid=0;for(std::size_t block=0;block<10;++block){
   finiteInvalid+=std::isfinite(vectorRatio.estimate.complements[block][1]);
   finiteInvalid+=std::isfinite(vectorRatio.referenceComplements[block][1]);}
 std::cout<<finiteInvalid<<'\n';
 auto referenceSurviving=exactComplement;
 referenceSurviving.algebraicallySurvives=true;
 const auto referenceComplementFailure=HP::IndependentRatio(
   x,y,{referenceSurviving});
 std::cout<<referenceComplementFailure.estimate.center[0]<<' '
          <<HP::ValueStatus(referenceComplementFailure,0)<<' '
          <<HP::UncertaintyStatus(referenceComplementFailure,0)<<'\n';
}
'''


class PlottingContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "pipeline/generate"))
        import runtime
        try:
            cls.runtime = runtime.resolve(require_root=True)
        except ValueError as error:
            raise unittest.SkipTest("ROOT unavailable for plot fixture: {}".format(error))
        cls.environment = os.environ.copy()
        cls.environment.update(cls.runtime["environment"])
        cls.environment["PYTHONDONTWRITEBYTECODE"] = "1"
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name).resolve()
        cls.raw = cls.base / "raw"
        cls.work = cls.base / "analyze-work"
        cls.analyzed = cls.base / "analyzed"
        cls.reduce_work = cls.base / "reduce-work"
        cls.plot_work = cls.base / "plot-work"
        for path in (cls.raw, cls.work, cls.analyzed, cls.reduce_work,
                     cls.plot_work):
            path.mkdir(parents=True)
        source = fixture_source()
        source = source.replace(
            "std::vector<int>{421, -421, 431",
            "std::vector<int>{421, -421, 421, 421, 421, 421, 421, 421, "
            "-4422, -4422, -4422, 431", 1)
        source = source.replace("const bool reductionBoundary = false;",
                                "const bool reductionBoundary = true;", 1)
        source = source.replace(
            "(reductionBoundary && slot <= 2 ? 4.0 : 4.1)",
            "(reductionBoundary && slot <= 10 ? 4.0 : 4.1)", 1)
        source = source.replace(
            "    if (resolutionEvents && row == 0)\n",
            "    if (!resolutionEvents && row == 0 && fixtureLogical != 0)\n"
            "      heavyPdgs.erase(heavyPdgs.begin() + 2, "
            "heavyPdgs.begin() + 11);\n"
            "    if (resolutionEvents && row == 0)\n", 1)
        source = source.replace(
            "if (row == 0 && absolutePdg != 421) {",
            "if (row == 0 && (absolutePdg != 421 || slot > 0)) {", 1)
        source = source.replace(
            "weight = 1.0, pthat = 2.0",
            "weight = fixtureLogical == 0 ? 2.0 : 1.0, pthat = 2.0", 1)
        source = source.replace(
            'md["sum_weights"] = 3.0; md["sum_weights2"] = 3.0;',
            'md["sum_weights"] = 3.0 * weight; '
            'md["sum_weights2"] = 3.0 * weight * weight;', 1)
        source = source.replace(
            'md["pythia_weight_sum"] = 3.0;',
            'md["pythia_weight_sum"] = 3.0 * weight;', 1)
        source = source.replace(
            "mult10 = row; mult40 = row;",
            "mult10 = row; mult40 = row;\n"
            "    if (fixtureLogical == 0 && row == 0) { mult10 = 3; mult40 = 3; }",
            1)
        source = source.replace("legacyMultiplicity = row;",
                                "legacyMultiplicity = mult10;", 1)
        cls._compile(source, cls.base / "fixture.cpp", cls.base / "fixture",
                     include_generate=True)
        cls._compile((ROOT / "pipeline/analyze/analyze.cpp").read_text(
            encoding="utf-8"), cls.base / "analyze.cpp", cls.base / "analyzer",
            include_generate=True)
        cls._compile(COMPACT_ORACLE, cls.base / "compact-oracle.cpp",
                     cls.base / "compact-oracle")
        cls._compile(COMPACT_MUTATOR, cls.base / "compact-mutator.cpp",
                     cls.base / "compact-mutator")
        cls._compile(GEOMETRY_AND_RATIO, cls.base / "geometry.cpp",
                     cls.base / "geometry", include_plot=True, root=False)
        cls._write_inputs()
        cls.plan = cls.work / "plan.json"
        cls._analyze("plan", "--campaign", str(cls.campaign), "--manifest",
                     str(cls.manifest), "--attempts", str(cls.attempts),
                     "--raw-root", str(cls.raw), "--work-root", str(cls.work),
                     "--output-root", str(cls.analyzed), "--plan", str(cls.plan),
                     "--target-bytes", "1000000000", check=True)
        cls._analyze("run", "--plan", str(cls.plan), check=True)
        cls.raw_hidden = cls.base / "raw-unavailable"
        cls.raw.rename(cls.raw_hidden)
        cls.current_output = cls.base / "reduced-current"
        cls._reduce("run", "--plan", str(cls.plan), "--analyzed-root",
                    str(cls.analyzed), "--work-root", str(cls.reduce_work),
                    "--output-root", str(cls.current_output), check=True)
        cls.root = next(cls.current_output.rglob("plot-source-*.root"))
        cls.receipt = cls.root.with_suffix(".json")
        analysis = json.loads((ROOT / "config/analysis.json").read_text(
            encoding="utf-8"))
        analysis["percentile_intervals"] = [[0, 10], [10, 50], [50, 100]]
        cls.alt_analysis = cls.base / "analysis-three.json"
        cls.alt_analysis.write_text(json.dumps(analysis, sort_keys=True),
                                    encoding="utf-8")
        cls.alt_output = cls.base / "reduced-three"
        cls._reduce("run", "--plan", str(cls.plan), "--analysis",
                    str(cls.alt_analysis), "--analyzed-root", str(cls.analyzed),
                    "--work-root", str(cls.reduce_work), "--output-root",
                    str(cls.alt_output), check=True)
        cls.alt_root = next(cls.alt_output.rglob("plot-source-*.root"))
        cls.alt_receipt = cls.alt_root.with_suffix(".json")
        specification = importlib.util.spec_from_file_location(
            "plotting_contract", str(ROOT / "pipeline/plot/run.py"))
        cls.plot = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(cls.plot)
        cls.admitted, cls.summary = cls.plot.admit(
            cls.root, cls.receipt, ROOT / "config/analysis.json", cls.plot_work)
        cls.domains = cls.admitted["scientific_identity"]["compact_domains"]
        cls.config, cls.config_sha = cls.plot.checked_plot_config(
            ROOT / "config/plot.json")
        cls.oracle = cls._oracle(cls.root)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    @classmethod
    def _compile(cls, source, source_path, output, include_generate=False,
                 include_plot=False, root=True):
        source_path.write_text(source, encoding="utf-8")
        command = [cls.environment["CXX"], "-std=c++17", "-O2", "-Wall",
                   "-Wextra", "-Wpedantic", "-Werror", str(source_path)]
        if include_generate:
            command.append("-I" + str(ROOT / "pipeline/generate"))
        if include_plot:
            command.append("-I" + str(ROOT / "pipeline/plot"))
            command.append("-I" + str(ROOT / "pipeline/reduce"))
        if root:
            command += shlex.split(subprocess.check_output(
                [cls.environment["ROOT_CONFIG"], "--cflags", "--libs"],
                text=True, env=cls.environment))
        completed = subprocess.run(command + ["-o", str(output)],
                                   env=cls.environment, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.returncode or completed.stdout.strip() or completed.stderr.strip():
            raise AssertionError("fixture compile failed: {}".format(
                completed.stderr.strip() or completed.stdout.strip()))

    @classmethod
    def _write_inputs(cls):
        raw_paths = []
        metadata = {}
        for tune_id, tune in enumerate(TUNES):
            for logical in range(10):
                path = cls.raw / tune / "opaque-{:03d}.root".format(logical)
                path.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run([str(cls.base / "fixture"), str(path), "valid",
                                str(logical), "0", tune, str(tune_id), "3"],
                               check=True, env=cls.environment)
                raw_paths.append((tune_id, tune, logical, path))
            inspected = subprocess.run(
                [str(cls.base / "analyzer"), "inspect-raw",
                 str(raw_paths[-10][3])], check=True, env=cls.environment,
                text=True, stdout=subprocess.PIPE)
            metadata[tune] = json.loads(inspected.stdout)
        control = cls.base / "control"
        (control / "data").mkdir(parents=True)
        campaign = json.loads((ROOT / "data/campaign.json").read_text(
            encoding="utf-8"))
        campaign["tune_order"] = list(TUNES)
        campaign["logical_jobs_per_tune"] = 10
        campaign["successful_events_per_logical_job"] = 3
        campaign["successful_events_per_tune"] = 30
        campaign["blocks"] = {"count": 10, "logical_id_domain": [0, 9],
                              "logical_id_rule": "block=(logical_id%10)+1"}
        campaign["seed"]["attempt_domain"] = [0, 0]
        campaign["seed"]["tune_ordinals"] = {
            tune: index for index, tune in enumerate(TUNES)}
        campaign["attempt_evidence_inventory"] = {"file_count": 30,
                                                    "sha256": "a" * 64}
        campaign["accepted_source"]["producer_executable_sha256"] = "b" * 64
        campaign["accepted_source"]["producer_repository_commit"] = "c" * 40
        for tune in TUNES:
            campaign["accepted_source"]["tune_cards"][tune][
                "accepted_effective_sha256"] = metadata[tune][
                    "effective_settings_sha256"]
        cls.campaign = control / "data/campaign.json"
        cls.campaign.write_text(json.dumps(campaign, sort_keys=True),
                                encoding="utf-8")
        rows = []
        attempts = ["tune,logical_id,attempt,seed,outcome,evidence_status,"
                    "raw_storage_key\n"]
        for tune_id, tune, logical, path in raw_paths:
            seed = 130000001 + tune_id * 1000000 + logical
            storage = "{}/{}".format(tune, path.name)
            rows.append({"accepted_attempt": 0, "accepted_seed": seed,
                         "block": logical + 1, "bytes": path.stat().st_size,
                         "logical_id": logical, "raw_sha256": sha256(path),
                         "raw_storage_key": storage, "successful_events": 3,
                         "tune": tune, "validation_log_sha256": "d" * 64,
                         "validation_receipt_sha256": "e" * 64})
            attempts.append("{},{},0,{},accepted,accepted_manifest_confirmed,{}\n".format(
                tune, logical, seed, storage))
        cls.manifest = control / "data/raw_manifest.jsonl"
        cls.manifest.write_text("".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in rows), encoding="utf-8")
        cls.attempts = control / "data/attempts.csv"
        cls.attempts.write_text("".join(attempts), encoding="utf-8")

    @classmethod
    def _analyze(cls, *arguments, check=False):
        completed = subprocess.run([str(ROOT / "hadronization"), "analyze"] +
                                   list(arguments), cwd=str(ROOT),
                                   env=cls.environment, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check and completed.returncode:
            raise AssertionError("analyze failed: {}".format(completed.stderr))
        return completed

    @classmethod
    def _reduce(cls, *arguments, check=False):
        completed = subprocess.run([str(ROOT / "hadronization"), "reduce"] +
                                   list(arguments), cwd=str(ROOT),
                                   env=cls.environment, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check and completed.returncode:
            raise AssertionError("reduce failed: {}".format(completed.stderr))
        return completed

    @classmethod
    def _oracle(cls, path):
        completed = subprocess.run([str(cls.base / "compact-oracle"), str(path)],
                                   check=True, env=cls.environment, text=True,
                                   stdout=subprocess.PIPE)
        result = {"cells": {}, "metadata": None, "receipt": None}
        for line in completed.stdout.splitlines():
            kind, *fields = line.split("\t")
            if kind == "C":
                result["cells"][tuple(map(int, fields[:5]))] = float(fields[5])
            elif kind == "M":
                result["metadata"] = json.loads(fields[0])
            elif kind == "R":
                result["receipt"] = json.loads(fields[0])
        return result

    def _plot_cli(self, *arguments, python=None):
        command = [str(ROOT / "hadronization"), "plot"] + list(arguments)
        environment = dict(self.environment)
        if python:
            environment["PYTHON"] = python
            command = [python, str(ROOT / "pipeline/plot/run.py")] + list(arguments)
        return subprocess.run(command, cwd=str(ROOT), env=environment, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _query(self, family, *extra, root=None, receipt=None, analysis=None,
               preset="all_registered"):
        completed = self._plot_cli(
            "query", "--root", str(root or self.root), "--receipt",
            str(receipt or self.receipt), "--analysis",
            str(analysis or ROOT / "config/analysis.json"), "--work-dir",
            str(self.plot_work), "--preset", preset, "--family", family, *extra)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_public_admission_help_and_scale_metadata(self):
        help_result = self._plot_cli("--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        for command in ("query", "export", "verify"):
            self.assertIn(command, help_result.stdout)
        payload = self._query(
            "balancing", "--tune", "MONASH", "--profile", "inclusive",
            "--activity", "charged_light_sector_activity_a15_v1_eta4",
            "--class-id", "0", "--pair", "411:-411")
        self.assertGreater(payload["row_count"], 0)
        scale = payload["compact_scale"]
        self.assertEqual(scale["successful_events_total"], 90)
        self.assertEqual(scale["sources_total"], 30)
        self.assertEqual([item["successful_events"] for item in scale["tunes"]],
                         [30, 30, 30])
        self.assertEqual(scale["class_count"], 12)

    def test_alternate_scale_metadata_is_derived_without_phase_a_constants(self):
        receipt = copy.deepcopy(self.admitted)
        total_events = 0
        total_sources = 0
        expected_events = []
        expected_sources = []
        for tune_id in range(len(TUNES)):
            tune_events = 0
            tune_sources = 0
            for block in receipt["_embedded_block_accounting"]["blocks"]:
                if block["tune"] != tune_id:
                    continue
                block["sources"] = tune_id + block["block"]
                block["successful_events"] = (tune_id + 2) * block["block"]
                tune_sources += block["sources"]
                tune_events += block["successful_events"]
            expected_sources.append(tune_sources)
            expected_events.append(tune_events)
            total_sources += tune_sources
            total_events += tune_events
        receipt["scientific_identity"]["events"] = total_events
        receipt["scientific_identity"]["sources"] = total_sources
        scale = self.plot.compact_scale(receipt)
        self.assertEqual(scale["successful_events_total"], total_events)
        self.assertEqual(scale["sources_total"], total_sources)
        self.assertEqual([item["successful_events"] for item in scale["tunes"]],
                         expected_events)
        self.assertEqual([item["sources"] for item in scale["tunes"]],
                         expected_sources)
        self.assertEqual(scale["block_ids"], list(range(1, 11)))

    def test_admission_rejects_receipt_config_state_domain_lineage_and_symlink(self):
        mutations = []
        original = json.loads(self.receipt.read_text(encoding="utf-8"))
        wrong_sha = json.loads(json.dumps(original))
        wrong_sha["storage_identity"]["root_sha256"] = "0" * 64
        mutations.append(wrong_sha)
        partial = json.loads(json.dumps(original))
        partial["state"] = "NONPUBLICATION_PARTIAL"
        mutations.append(partial)
        domain = json.loads(json.dumps(original))
        domain["scientific_identity"]["compact_domains"]["class_dictionary"][0][
            "id"] = 99
        mutations.append(domain)
        lineage = json.loads(json.dumps(original))
        lineage["scientific_identity"]["input_lineage_sha256"] = "0" * 64
        mutations.append(lineage)
        for index, payload in enumerate(mutations):
            path = self.base / "receipt-mutant-{}.json".format(index)
            path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            result = self._plot_cli(
                "query", "--root", str(self.root), "--receipt", str(path),
                "--work-dir", str(self.plot_work), "--family", "balancing")
            self.assertEqual(result.returncode, 2)
        link = self.base / "compact-link.root"
        link.symlink_to(self.root)
        result = self._plot_cli(
            "query", "--root", str(link), "--receipt", str(self.receipt),
            "--work-dir", str(self.plot_work), "--family", "balancing")
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlink", result.stderr)
        changed = json.loads((ROOT / "config/analysis.json").read_text(
            encoding="utf-8"))
        changed["version"] = "wrong"
        bad_analysis = self.base / "analysis-wrong.json"
        bad_analysis.write_text(json.dumps(changed), encoding="utf-8")
        result = self._plot_cli(
            "query", "--root", str(self.root), "--receipt", str(self.receipt),
            "--analysis", str(bad_analysis), "--work-dir", str(self.plot_work),
            "--family", "balancing")
        self.assertEqual(result.returncode, 2)
        canonical = lambda value: json.dumps(
            value, sort_keys=True, separators=(",", ":"))
        metadata = copy.deepcopy(self.oracle["metadata"])
        embedded = copy.deepcopy(self.oracle["receipt"])
        for payload in (metadata, embedded):
            payload["compact_domains"]["analysis_request_sha256"] = "0" * 64
            payload["compact_domains_sha256"] = hashlib.sha256(
                canonical(payload["compact_domains"]).encode("ascii")).hexdigest()
        metadata_path = self.base / "coherent-domain.metadata.json"
        embedded_path = self.base / "coherent-domain.embedded.json"
        metadata_path.write_text(canonical(metadata), encoding="ascii")
        embedded_path.write_text(canonical(embedded), encoding="ascii")
        rebound_root = self.base / "coherent-domain.root"
        subprocess.run([str(self.base / "compact-mutator"), str(self.root),
                        str(rebound_root), "payload", str(metadata_path),
                        str(embedded_path)], check=True, env=self.environment)
        external = json.loads(self.receipt.read_text(encoding="utf-8"))
        scientific = external["scientific_identity"]
        scientific["compact_domains"] = metadata["compact_domains"]
        scientific["compact_domains_sha256"] = metadata["compact_domains_sha256"]
        scientific["metadata_sha256"] = hashlib.sha256(
            canonical(metadata).encode("ascii")).hexdigest()
        scientific["embedded_receipt_sha256"] = hashlib.sha256(
            canonical(embedded).encode("ascii")).hexdigest()
        external["scientific_identity_sha256"] = hashlib.sha256(
            canonical(scientific).encode("ascii")).hexdigest()
        external["storage_identity"]["root_bytes"] = rebound_root.stat().st_size
        external["storage_identity"]["root_sha256"] = sha256(rebound_root)
        external["storage_identity_sha256"] = hashlib.sha256(canonical(
            external["storage_identity"]).encode("ascii")).hexdigest()
        rebound_receipt = self.base / "coherent-domain.json"
        rebound_receipt.write_text(canonical(external), encoding="ascii")
        result = self._plot_cli(
            "query", "--root", str(rebound_root), "--receipt",
            str(rebound_receipt), "--work-dir", str(self.plot_work),
            "--family", "balancing")
        self.assertEqual(result.returncode, 2)
        self.assertRegex(result.stderr, "domain|binding|request")

    def test_admission_rejects_extra_object_and_cycle(self):
        for mode in ("unknown", "cycle"):
            root = self.base / (mode + ".root")
            subprocess.run([str(self.base / "compact-mutator"), str(self.root),
                            str(root), mode], check=True, env=self.environment)
            receipt = self.base / (mode + ".json")
            payload = json.loads(self.receipt.read_text(encoding="utf-8"))
            payload["storage_identity"]["root_bytes"] = root.stat().st_size
            payload["storage_identity"]["root_sha256"] = sha256(root)
            payload["storage_identity_sha256"] = hashlib.sha256(json.dumps(
                payload["storage_identity"], sort_keys=True,
                separators=(",", ":")).encode("ascii")).hexdigest()
            receipt.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            result = self._plot_cli(
                "query", "--root", str(root), "--receipt", str(receipt),
                "--work-dir", str(self.plot_work), "--family", "balancing")
            self.assertEqual(result.returncode, 2)
            self.assertRegex(result.stderr, "object set|cycle")

    def test_pooled_balance_complements_covariance_and_statuses_match_oracle(self):
        scope = next(item for item in self.domains["scope_dictionary"]
                     if item["family"] == "pair" and item["tune"] == "MONASH" and
                     item["profile"] == "inclusive" and item["activity"] ==
                     "charged_light_sector_activity_a15_v1_eta4" and
                     item["class_id"] == 0)
        pairs = {(item["trigger_pdg"], item["associate_pdg"]): item["id"]
                 for item in self.domains["pair_query_dictionary"]}
        trigger = next(item["id"] for item in self.domains["trigger_dictionary"]
                       if item["signed_pdg"] == 421)
        cells = self.oracle["cells"]
        def blocks(projection, bin_id):
            return [cells.get((projection, scope["id"], block, bin_id, 0), 0.0)
                    for block in range(1, 11)]
        opposite = blocks(2, pairs[(421, -421)])
        same = blocks(2, pairs[(421, 421)])
        denominator = blocks(3, trigger)
        center = (sum(opposite) - sum(same)) / sum(denominator)
        complements = [((sum(opposite) - opposite[index]) -
                        (sum(same) - same[index])) /
                       (sum(denominator) - denominator[index])
                       for index in range(10)]
        mean = sum(complements) / 10.0
        covariance = 0.9 * sum((value - mean) ** 2 for value in complements)
        blockwise = [(opposite[index] - same[index]) / denominator[index]
                     for index in range(10)]
        ratio_mean = sum(blockwise) / 10.0
        wrong_centering = 0.9 * sum((value - center) ** 2
                                    for value in complements)
        wrong_factor = sum((value - mean) ** 2 for value in complements)
        self.assertNotAlmostEqual(center, ratio_mean, places=10)
        self.assertNotAlmostEqual(covariance, wrong_centering, places=10)
        self.assertNotAlmostEqual(covariance, wrong_factor, places=10)
        self.assertIn(0.0, same)
        payload = self._query(
            "balancing", "--tune", "MONASH", "--profile", "inclusive",
            "--activity", "charged_light_sector_activity_a15_v1_eta4",
            "--class-id", "0", "--pair", "421:-421")
        row = next(item for item in payload["rows"]
                   if item["quantity"] == "os_minus_ss_per_trigger")
        self.assertAlmostEqual(float(row["value"]), center, places=15)
        actual_complements = list(map(float, row["source_tune_complements"].split(";")))
        self.assertEqual(len(actual_complements), 10)
        for actual, expected in zip(actual_complements, complements):
            self.assertAlmostEqual(actual, expected, places=15)
        self.assertAlmostEqual(float(row["variance"]), covariance, places=15)
        self.assertEqual(row["estimator"],
                         "pooled_delete_one_source_block_jackknife_v2")
        self.assertTrue(any(float(item["value"]) < 0 for item in payload["rows"]
                            if item["value"]))
        zero_dispersion = self._query("sample_counts", "--tune", "MONASH")
        self.assertTrue(any(item["value_status"] == "AVAILABLE" and
                            float(item["finite_mc_error"]) == 0.0 and
                            float(item["variance"]) == 0.0
                            for item in zero_dispersion["rows"]
                            if item["finite_mc_error"] and item["variance"]))
        missing = self._query(
            "balancing", "--tune", "MONASH", "--profile", "inclusive",
            "--activity", "charged_light_sector_activity_a15_v1_eta4",
            "--class-id", "0", "--pair", "521:-521")
        self.assertTrue(any(item["value_status"] == "POOLED_DENOMINATOR_ZERO"
                            for item in missing["rows"]))
        self.assertFalse(any(item["reference_tune"] == "MONASH"
                             for item in missing["rows"]))
        baryon = self._query(
            "balancing", "--tune", "MONASH", "--profile", "inclusive",
            "--activity", "charged_light_sector_activity_a15_v1_eta4",
            "--class-id", "0", "--pair", "421:-4122")
        ratio = next(item for item in baryon["rows"]
                     if item["quantity"] == "baryon_meson_reference_ratio")
        self.assertIn("exact_algebraic_cancellation:shared_trigger",
                      ratio["diagnostic"])

    def test_independent_tune_ratio_geometry_and_mutants(self):
        output = subprocess.check_output([str(self.base / "geometry")],
                                         text=True).splitlines()
        geometry = list(map(float, output[0].split()))
        self.assertEqual(geometry[0], -math.pi / 2)
        self.assertEqual(geometry[1], -math.pi / 2)
        self.assertEqual(geometry[2:], [1.0, 1.0])
        self.assertNotEqual(round(math.pi, 6), math.pi)
        ratio, covariance, error, source_mean, reference_mean = map(
            float, output[1].split())
        first_n = [float(index + 2) for index in range(10)]
        first_d = [float(index + 5) for index in range(10)]
        second_n = [float(3 * index + 4) for index in range(10)]
        second_d = [float(index + 7) for index in range(10)]
        def estimate(numerators, denominators):
            center = sum(numerators) / sum(denominators)
            leaves = [(sum(numerators) - numerators[index]) /
                      (sum(denominators) - denominators[index])
                      for index in range(10)]
            mean = sum(leaves) / 10.0
            variance = 0.9 * sum((value - mean) ** 2 for value in leaves)
            return center, leaves, variance
        first = estimate(first_n, first_d)
        second = estimate(second_n, second_d)
        expected = first[0] / second[0]
        source_family = [value / second[0] for value in first[1]]
        reference_family = [first[0] / value for value in second[1]]
        expected_source_mean = sum(source_family) / 10.0
        expected_reference_mean = sum(reference_family) / 10.0
        source_bias_corrected_center = 10.0 * expected - 9.0 * expected_source_mean
        expected_covariance = 0.9 * (
            sum((value - expected_source_mean) ** 2
                for value in source_family) +
            sum((value - expected_reference_mean) ** 2
                for value in reference_family))
        linearized = (first[2] / second[0] ** 2 +
                      first[0] ** 2 * second[2] / second[0] ** 4)
        paired = [first[1][index] / second[1][index] for index in range(10)]
        paired_mean = sum(paired) / 10.0
        paired_covariance = 0.9 * sum((value - paired_mean) ** 2 for value in paired)
        combined_mean = sum(source_family + reference_family) / 20.0
        combined_centering = 0.9 * sum(
            (value - combined_mean) ** 2
            for value in source_family + reference_family)
        wrong_factor = expected_covariance / 0.9
        pooled_family = source_family + reference_family
        pooled_mean = sum(pooled_family) / len(pooled_family)
        pooled_tune_deletion = 19.0 / 20.0 * sum(
            (value - pooled_mean) ** 2 for value in pooled_family)
        third_n = [float(2 * index + 5) for index in range(10)]
        third_d = [float(index + 9) for index in range(10)]
        third = estimate(third_n, third_d)
        third_family = [value / second[0] for value in third[1]]
        pooled_thirty = source_family + reference_family + third_family
        pooled_thirty_mean = sum(pooled_thirty) / 30.0
        pooled_thirty_covariance = 29.0 / 30.0 * sum(
            (value - pooled_thirty_mean) ** 2 for value in pooled_thirty)
        self.assertAlmostEqual(ratio, expected, places=15)
        self.assertNotAlmostEqual(ratio, source_bias_corrected_center, places=12)
        self.assertAlmostEqual(covariance, expected_covariance, places=15)
        self.assertAlmostEqual(error, math.sqrt(expected_covariance), places=15)
        self.assertAlmostEqual(source_mean, expected_source_mean, places=15)
        self.assertAlmostEqual(reference_mean, expected_reference_mean, places=15)
        self.assertAlmostEqual(expected_covariance, 0.0017791710298199297,
                               places=16)
        self.assertAlmostEqual(linearized, 0.0017662834141002417, places=16)
        for mutant in (linearized, paired_covariance, combined_centering,
                       wrong_factor, pooled_tune_deletion,
                       pooled_thirty_covariance):
            self.assertNotAlmostEqual(mutant, expected_covariance, places=10)
        exported_source = list(map(float, output[2].split(";")))
        exported_reference = list(map(float, output[3].split(";")))
        self.assertEqual(exported_source, source_family)
        self.assertEqual(exported_reference, reference_family)
        self.assertNotEqual(exported_source, first[1])
        self.assertNotEqual(exported_reference, second[1])

        typed, dropped, forced, net_value, net_bound = output[4].split()
        self.assertEqual(typed, "DENOMINATOR_NUMERICALLY_UNRESOLVED")
        self.assertEqual((dropped, forced), ("AVAILABLE", "AVAILABLE"))
        self.assertNotEqual(float(net_value), 0.0)
        self.assertGreater(float(net_bound), abs(float(net_value)))
        pooled, cancelled_value, cancelled_uncertainty, numerical_value, \
            numerical_uncertainty = output[5].split()
        self.assertEqual(pooled, "POOLED_DENOMINATOR_ZERO")
        self.assertEqual(cancelled_value, "AVAILABLE")
        self.assertEqual(cancelled_uncertainty, "LEAVE_DENOMINATOR_ZERO")
        self.assertEqual(numerical_value, "AVAILABLE")
        self.assertEqual(numerical_uncertainty,
                         "LEAVE_DENOMINATOR_NUMERICALLY_UNRESOLVED")
        cancelled_value, cancelled_uncertainty, cancelled_reasons, \
            surviving_value, surviving_uncertainty = output[6].split()
        self.assertEqual((cancelled_value, cancelled_uncertainty,
                          cancelled_reasons),
                         ("AVAILABLE", "AVAILABLE_ZERO_DISPERSION", "0"))
        self.assertEqual(surviving_value, "UNSTABLE_DENOMINATOR")
        self.assertEqual(surviving_uncertainty,
                         "DENOMINATOR_STATISTICALLY_UNRESOLVED")
        boundary_value, value_status, uncertainty_status, covariance_size, diagnostic = \
            output[7].split()
        self.assertAlmostEqual(float(boundary_value), first[0], places=15)
        self.assertEqual(value_status, "AVAILABLE")
        self.assertEqual(uncertainty_status, "CLASS_BOUNDARY_UNSTABLE")
        self.assertEqual(covariance_size, "0")
        self.assertEqual(diagnostic, "fixed_pooled_boundary_delete_one")

        vector_status = output[8].split()
        self.assertEqual(vector_status[:3],
                         ["AVAILABLE", "POOLED_DENOMINATOR_ZERO", "AVAILABLE"])
        self.assertEqual(vector_status[3:6],
                         ["AVAILABLE", "UNAVAILABLE", "AVAILABLE"])
        vector_covariance = float(vector_status[6])
        source_zero = list(map(float, output[9].split(";")))
        source_two = list(map(float, output[10].split(";")))
        reference_zero = list(map(float, output[11].split(";")))
        reference_two = list(map(float, output[12].split(";")))
        mean_source_zero = sum(source_zero) / 10.0
        mean_source_two = sum(source_two) / 10.0
        mean_reference_zero = sum(reference_zero) / 10.0
        mean_reference_two = sum(reference_two) / 10.0
        reconstructed = 0.9 * sum(
            (source_zero[index] - mean_source_zero) *
            (source_two[index] - mean_source_two) +
            (reference_zero[index] - mean_reference_zero) *
            (reference_two[index] - mean_reference_two)
            for index in range(10))
        self.assertAlmostEqual(vector_covariance, reconstructed, places=15)
        self.assertNotEqual(vector_covariance, 0.0)
        self.assertEqual(output[13], "0")
        retained_center, retained_value_status, retained_uncertainty_status = \
            output[14].split()
        self.assertAlmostEqual(float(retained_center), expected, places=15)
        self.assertEqual(retained_value_status, "UNSTABLE_DENOMINATOR")
        self.assertEqual(retained_uncertainty_status, "LEAVE_DENOMINATOR_ZERO")

    def test_complete_pair_correlation_profile_activity_and_role_sets(self):
        roles, rows, unused = self.plot.engine_rows(
            self.root, self.admitted, ("balancing", "correlations"), self.plot_work)
        del unused
        self.assertEqual(len(roles), 42)
        self.assertEqual(len({item["id"] for item in roles}), 42)
        expected_roles = {
            "balancing.integrated.charm", "balancing.integrated.beauty",
            "balancing.activity.charm", "balancing.activity.beauty",
            "balancing.baryon_meson.activity", "multiplicity.composite",
        }
        expected_roles.update(
            "correlations.{}.{}".format(tune, sector)
            for tune in TUNES for sector in ("charm", "beauty"))
        expected_roles.update(
            "kinematics.{}.{}".format(item["signed_pdg"], axis)
            for item in self.domains["g9_species_dictionary"]
            for axis in ("pt", "eta", "phi"))
        self.assertEqual({item["id"] for item in roles}, expected_roles)
        correlation_roles = {item["id"] for item in roles
                             if item["family"] == "correlations"}
        self.assertEqual(correlation_roles, {
            "correlations.{}.{}".format(tune, sector)
            for tune in TUNES for sector in ("charm", "beauty")})
        self.assertFalse(any(row["tune"] == "MONASH" and
                             row["reference_tune"] == "MONASH"
                             for row in rows))
        selected = [row for row in rows if row["family"] == "balancing" and
                    row["quantity"] == "ordered_pair_yield" and
                    row["tune"] == "MONASH" and row["profile"] == "inclusive" and
                    row["activity_id"] ==
                    "charged_light_sector_activity_a15_v1_eta4" and
                    row["class_id"] == "0"]
        self.assertEqual(len(selected), 300)
        self.assertEqual(len({(row["trigger_pdg"], row["associate_pdg"])
                              for row in selected}), 300)
        self.assertEqual({row["profile"] for row in rows
                          if row["family"] == "correlations"},
                         {"inclusive", "historical_1p0_0p15"})
        self.assertEqual({row["activity_id"] for row in rows
                          if row["family"] == "correlations"},
                         {item["id"] for item in self.domains["activities"]})
        expected = {
            (scope["tune"], scope["profile"], scope["activity"],
             str(scope["class_id"]), str(identity["trigger_pdg"]),
             str(identity["associate_pdg"]), component, str(bin_index))
            for scope in self.domains["scope_dictionary"]
            if scope["family"] == "pair"
            for identity in self.domains["correlation_dictionary"]
            for component in ("OS", "SS", "OS_MINUS_SS")
            for bin_index in range(self.domains["axes"]["dphi"]["bins"])
        }
        correlations = [row for row in rows if row["family"] == "correlations"]
        observed = {
            (row["tune"], row["profile"], row["activity_id"], row["class_id"],
             row["trigger_pdg"], row["associate_pdg"], row["component"],
             row["bin_index"]) for row in correlations
        }
        self.assertEqual(observed, expected)
        materialized_classes = {str(item["id"])
                                for item in self.domains["class_dictionary"]}
        self.assertEqual({row["class_id"] for row in correlations},
                         materialized_classes)
        role_rows = [row for row in correlations if row["role_id"] != "-"]
        self.assertEqual({row["profile"] for row in role_rows}, {"inclusive"})
        self.assertEqual({row["activity_id"] for row in role_rows},
                         {"charged_light_sector_activity_a15_v1_eta4"})
        self.assertEqual({row["class_id"] for row in role_rows},
                         materialized_classes)
        self.assertTrue(all(row["role_id"] == "-" for row in correlations
                            if row["profile"] == "historical_1p0_0p15" or
                            row["activity_id"] ==
                            "charged_light_sector_activity_a15_v1_eta1"))

        fake_reference = dict(next(
            row for row in rows if row["quantity"] == "ratio_to_reference_tune"))
        fake_reference["role_id"] = "-"
        fake_reference["tune"] = fake_reference["reference_tune"]
        with self.assertRaisesRegex(ValueError, "fake reference-tune"):
            self.plot.validate_engine_relations(
                roles, [fake_reference], self.admitted, ("balancing",))
        wrong_role = dict(next(row for row in correlations
                               if row["role_id"] != "-"))
        wrong_role["profile"] = "historical_1p0_0p15"
        with self.assertRaisesRegex(ValueError, "role/context"):
            self.plot.validate_engine_relations(
                roles, [wrong_role], self.admitted, ("balancing",))
        available_value = dict(next(row for row in rows
                                    if row["value"] != "-"))
        available_value["role_id"] = "-"
        missing_value = dict(available_value)
        missing_value["value"] = "-"
        with self.assertRaisesRegex(ValueError, "value/status"):
            self.plot.validate_engine_relations(
                roles, [missing_value], self.admitted, ("balancing",))
        short_replicas = dict(correlations[0])
        short_replicas["role_id"] = "-"
        short_replicas["source_tune_complements"] = ";".join(["0x0p+0"] * 9)
        with self.assertRaisesRegex(ValueError, "cardinality"):
            self.plot.validate_engine_relations(
                roles, [short_replicas], self.admitted, ("balancing",))
        natural = dict(next(row for row in rows
                            if row["quantity"] == "ordered_pair_yield" and
                            row["role_id"] == "-"))
        duplicate = dict(natural)
        duplicate["semantic_id"] += "/mutant"
        with self.assertRaisesRegex(ValueError, "natural keys"):
            self.plot.validate_engine_relations(
                roles, [natural, duplicate], self.admitted, ("balancing",))

        admitted, unused_summary = self.plot.admit(
            self.alt_root, self.alt_receipt, self.alt_analysis, self.plot_work)
        del unused_summary
        unused_roles, alternate, unused_build = self.plot.engine_rows(
            self.alt_root, admitted, ("correlations",), self.plot_work)
        del unused_roles, unused_build
        alt_domains = admitted["scientific_identity"]["compact_domains"]
        alt_expected = {
            (scope["tune"], scope["profile"], scope["activity"],
             str(scope["class_id"]), str(identity["trigger_pdg"]),
             str(identity["associate_pdg"]), component, str(bin_index))
            for scope in alt_domains["scope_dictionary"]
            if scope["family"] == "pair"
            for identity in alt_domains["correlation_dictionary"]
            for component in ("OS", "SS", "OS_MINUS_SS")
            for bin_index in range(alt_domains["axes"]["dphi"]["bins"])
        }
        self.assertEqual({
            (row["tune"], row["profile"], row["activity_id"], row["class_id"],
             row["trigger_pdg"], row["associate_pdg"], row["component"],
             row["bin_index"]) for row in alternate}, alt_expected)

    def test_g9_t1_origin_and_closure_domains_remain_distinct(self):
        expectations = {
            "kinematics": "kinematics",
            "sample_counts": "sample_counts",
            "origin": "origin",
            "closure_species": "closure_species",
            "closure_full_visible": "closure_full_visible",
            "closure_category_dphi": "closure_category_dphi",
        }
        for family, expected in expectations.items():
            roles, rows, unused = self.plot.engine_rows(
                self.root, self.admitted, (family,), self.plot_work)
            del roles, unused
            self.assertTrue(rows)
            self.assertEqual({row["family"] for row in rows}, {expected})
        unused_roles, g9, unused_build = self.plot.engine_rows(
            self.root, self.admitted, ("kinematics",), self.plot_work)
        del unused_roles, unused_build
        pt = [row for row in g9 if row["axis"] == "pt"]
        self.assertTrue(any(row["bin_low"] == "-" for row in pt))
        self.assertTrue(any(row["bin_high"] == "-" for row in pt))
        self.assertEqual({int(row["associate_pdg"]) for row in g9},
                         set(self.domains["g9_species_dictionary"][index]["signed_pdg"]
                             for index in range(10)))

    def test_normalized_vector_complements_reconstruct_full_singular_covariance(self):
        unused_roles, rows, unused_build = self.plot.engine_rows(
            self.root, self.admitted, ("multiplicity",), self.plot_work)
        del unused_roles, unused_build
        tune_ratios = [row for row in rows
                       if row["quantity"] == "ratio_to_reference_tune"]
        self.assertTrue(tune_ratios)
        self.assertFalse(any(row["tune"] == "MONASH" for row in tune_ratios))
        self.assertFalse(any(row["tune"] == row["reference_tune"]
                             for row in rows if row["reference_tune"] != "-"))
        multiplicity_roles = [row for row in rows if row["role_id"] != "-"]
        self.assertTrue(multiplicity_roles)
        self.assertTrue(all(
            row["role_id"] == "multiplicity.composite" and
            row["activity_id"] ==
            "charged_light_sector_activity_a15_v1_eta4"
            for row in multiplicity_roles))
        self.assertTrue(all(row["role_id"] == "-" for row in rows
                            if row["activity_id"] ==
                            "charged_light_sector_activity_a15_v1_eta1"))
        selected = [row for row in rows if row["tune"] == "MONASH" and
                    row["axis"] == "nch" and row["quantity"] ==
                    "normalized_distribution" and row["activity_id"] ==
                    "charged_light_sector_activity_a15_v1_eta4"]
        selected.sort(key=lambda row: int(row["bin_index"]))
        centers = [float.fromhex(row["value"]) for row in selected]
        self.assertAlmostEqual(sum(centers), 1.0, places=15)
        complements = [list(map(float.fromhex,
                                row["source_tune_complements"].split(";")))
                       for row in selected]
        for block in range(10):
            self.assertAlmostEqual(sum(row[block] for row in complements),
                                   1.0, places=15)
        means = [sum(row) / 10.0 for row in complements]
        block_sums = [sum(complements[row][block] - means[row]
                          for row in range(len(selected))) for block in range(10)]
        residuals = [0.9 * sum((complements[row][block] - means[row]) *
                               block_sums[block] for block in range(10))
                     for row in range(len(selected))]
        self.assertLess(max(map(abs, residuals)), 1e-14)
        varying = [row for row in range(len(selected))
                   if any(complements[row][block] != means[row]
                          for block in range(10))]
        off_diagonal = [0.9 * sum(
            (complements[left][block] - means[left]) *
            (complements[right][block] - means[right]) for block in range(10))
            for position, left in enumerate(varying)
            for right in varying[position + 1:]]
        self.assertTrue(any(abs(value) > 0 for value in off_diagonal))

        ratio_rows = [row for row in tune_ratios
                      if row["tune"] == "JUNCTIONS" and row["activity_id"] ==
                      "charged_light_sector_activity_a15_v1_eta4"]
        valid = [row for row in ratio_rows
                 if row["uncertainty_status"] in
                 {"AVAILABLE", "AVAILABLE_ZERO_DISPERSION"}]
        invalid = [row for row in ratio_rows if row["value"] == "-"]
        self.assertGreaterEqual(len(valid), 2)
        self.assertTrue(invalid)
        self.assertTrue(all(row["value"] != "1" for row in invalid))
        self.assertTrue(all(len(row["source_tune_complements"].split(";")) == 10
                            and len(row["reference_tune_complements"].split(";")) == 10
                            for row in ratio_rows))
        families = []
        for row in valid:
            source_family = list(map(float.fromhex,
                                     row["source_tune_complements"].split(";")))
            reference_family = list(map(float.fromhex,
                                        row["reference_tune_complements"].split(";")))
            source_mean = sum(source_family) / 10.0
            reference_mean = sum(reference_family) / 10.0
            variance = 0.9 * (
                sum((value - source_mean) ** 2 for value in source_family) +
                sum((value - reference_mean) ** 2
                    for value in reference_family))
            self.assertAlmostEqual(variance, float.fromhex(row["variance"]),
                                   places=15)
            self.assertAlmostEqual(math.sqrt(variance),
                                   float.fromhex(row["finite_mc_error"]), places=15)
            families.append((source_family, reference_family,
                             source_mean, reference_mean))
        cross_covariances = []
        for index, left in enumerate(families):
            for right in families[index + 1:]:
                cross_covariances.append(0.9 * sum(
                    (left[0][block] - left[2]) *
                    (right[0][block] - right[2]) +
                    (left[1][block] - left[3]) *
                    (right[1][block] - right[3])
                    for block in range(10)))
        self.assertTrue(cross_covariances)
        self.assertTrue(all(math.isfinite(value) for value in cross_covariances))

    def test_dynamic_default_and_three_class_compacts(self):
        default = self._query(
            "balancing", "--tune", "MONASH", "--profile", "inclusive",
            "--activity", "charged_light_sector_activity_a15_v1_eta4",
            "--pair", "411:-411")
        alternate = self._query(
            "balancing", "--tune", "MONASH", "--profile", "inclusive",
            "--activity", "charged_light_sector_activity_a15_v1_eta4",
            "--pair", "411:-411", root=self.alt_root,
            receipt=self.alt_receipt, analysis=self.alt_analysis)
        self.assertEqual({int(row["class_id"]) for row in default["rows"]},
                         set(range(12)))
        self.assertEqual({int(row["class_id"]) for row in alternate["rows"]},
                         set(range(4)))
        self.assertEqual(alternate["compact_scale"]["class_count"], 4)
        self.assertEqual([item["percentile_interval"] for item in
                          alternate["compact_scale"]["class_dictionary"]],
                         [[0, 100], [0, 10], [10, 50], [50, 100]])
        boundary_map = {}
        for receipt in self.admitted["_embedded_activity_receipts"]:
            tune = self.domains["tune_dictionary"][receipt["tune"]]
            activity = self.domains["activities"][receipt["activity_id"]]["id"]
            for class_id, boundary in enumerate(receipt["classes"]):
                boundary_map[(tune, activity, class_id)] = boundary
        self.assertTrue(any(
            class_id > 0 and (not boundary["stable"] or not boundary["resolved"])
            for (unused_tune, unused_activity, class_id), boundary
            in boundary_map.items()))
        unused_roles, rows, unused_build = self.plot.engine_rows(
            self.root, self.admitted, ("balancing",), self.plot_work)
        del unused_roles, unused_build
        projected = next(
            row for row in rows
            if row["quantity"] == "os_minus_ss_per_trigger" and
            row["value"] != "-" and
            "fixed_pooled_boundary_delete_one" in row["diagnostic"])
        boundary = boundary_map[(projected["tune"], projected["activity_id"],
                                 int(projected["class_id"]))]
        expected = []
        if not boundary["stable"]:
            expected.append("CLASS_BOUNDARY_UNSTABLE")
        if not boundary["resolved"]:
            expected.append("CLASS_BOUNDARY_UNRESOLVED")
        self.assertTrue(set(expected).issubset(set(projected["reasons"].split(","))))
        self.assertIn("fixed_pooled_boundary_delete_one", projected["diagnostic"])

    def test_presentation_presets_composition_and_noncentral_guards(self):
        default = self.plot.resolve_selection(
            self.config, self.domains, "paper_default", [], [])
        self.assertEqual(default["family_tokens"],
                         ["D", "LambdaC", "B", "LambdaB"])
        augmented = self.plot.resolve_selection(
            self.config, self.domains, "paper_default", ["Ds"], [])
        self.assertEqual(augmented["family_tokens"][:4], default["family_tokens"])
        self.assertEqual(augmented["family_tokens"][-1], "Ds")
        central = self.plot.resolve_selection(
            self.config, self.domains, "all_central", [], ["Omega"])
        registered = self.plot.resolve_selection(
            self.config, self.domains, "all_registered", [], [])
        self.assertEqual(len(registered["signed_pdgs"]), 50)
        self.assertEqual(registered["noncentral_signed_pdgs"],
                         [-5322, -5312, -5212, 5212, 5312, 5322])
        self.assertFalse(set(registered["noncentral_signed_pdgs"]).intersection(
            central["signed_pdgs"]))
        for arguments in (("unknown", [], []),
                          ("paper_default", ["Ds", "Ds"], []),
                          ("paper_default", ["Ds"], ["Ds"])):
            with self.assertRaises(ValueError):
                self.plot.resolve_selection(self.config, self.domains, *arguments)
        for pdg in registered["noncentral_signed_pdgs"]:
            trigger = 511
            result = self._plot_cli(
                "query", "--root", str(self.root), "--receipt", str(self.receipt),
                "--work-dir", str(self.plot_work), "--family", "balancing",
                "--pair", "{}:{}".format(trigger, pdg))
            self.assertEqual(result.returncode, 2)
            self.assertIn("--diagnostic-pdg", result.stderr)

    def test_layout_facets_stable_paginated_and_axis_inputs_include_errors(self):
        unused_roles, rows, unused_build = self.plot.engine_rows(
            self.root, self.admitted, ("balancing",), self.plot_work)
        del unused_roles, unused_build
        default = self.plot.resolve_selection(
            self.config, self.domains, "paper_default", [], [])
        augmented = self.plot.resolve_selection(
            self.config, self.domains, "all_central", [], [])
        first = self.plot.layout_primitives(
            self.config, default, self.plot.filter_rows(rows, default))
        second = self.plot.layout_primitives(
            self.config, augmented, self.plot.filter_rows(rows, augmented))
        default_ids = [facet["facet_id"] for page in first["pages"]
                       for facet in page["facets"]]
        augmented_ids = [facet["facet_id"] for page in second["pages"]
                         for facet in page["facets"]]
        self.assertEqual(augmented_ids[:len(default_ids)], default_ids)
        self.assertEqual(len(second["pages"]), 2)
        roles = [page["output_role"] for page in second["pages"]]
        self.assertEqual(len(roles), len(set(roles)))
        self.assertTrue(all(facet["axis_range_input"]["valid_points"] > 0
                            for page in first["pages"] for facet in page["facets"]))
        self.assertEqual(self.config["style_identities"]["tunes"][0]["id"],
                         "MONASH")

    def test_deterministic_exports_atomicity_exact_set_and_presentation_identity(self):
        first = self.base / "export-one"
        second = self.base / "export-two"
        command = ("export", "--root", str(self.root), "--receipt", str(self.receipt),
                   "--work-dir", str(self.plot_work), "--preset", "paper_default")
        for output, python in ((first, sys.executable),
                               (second, "/usr/bin/python3")):
            completed = self._plot_cli(*command, "--output", str(output),
                                       python=python)
            self.assertEqual(completed.returncode, 0, completed.stderr)
        first_bytes = {path.name: path.read_bytes() for path in first.iterdir()}
        second_bytes = {path.name: path.read_bytes() for path in second.iterdir()}
        self.assertEqual(first_bytes, second_bytes)
        verified = self._plot_cli("verify", "--output", str(first))
        self.assertEqual(verified.returncode, 0, verified.stderr)
        collision = self._plot_cli(*command, "--output", str(first))
        self.assertEqual(collision.returncode, 2)
        reused = self._plot_cli(*command, "--output", str(first), "--reuse")
        self.assertEqual(reused.returncode, 0, reused.stderr)
        (first / "stale.txt").write_text("stale", encoding="ascii")
        stale = self._plot_cli("verify", "--output", str(first))
        self.assertEqual(stale.returncode, 2)
        (first / "stale.txt").unlink()
        interrupted = self.base / "export-interrupted"
        environment = dict(self.environment)
        environment["HADRONIZATION_PLOT_FAIL_BEFORE_MANIFEST"] = "1"
        failed = subprocess.run(
            [str(ROOT / "hadronization"), "plot"] + list(command) +
            ["--output", str(interrupted)], cwd=str(ROOT), env=environment,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(failed.returncode, 2)
        self.assertFalse(interrupted.exists())
        self.assertFalse(any(interrupted.parent.glob(
            ".{}.plot-stage-*".format(interrupted.name))))
        augmented = self.base / "export-augmented"
        completed = self._plot_cli(*command, "--include", "Ds", "--output",
                                   str(augmented))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        original_manifest = json.loads((second / "manifest.json").read_text())
        augmented_manifest = json.loads((augmented / "manifest.json").read_text())
        reached_roles = set()
        for family in self.plot.DEFAULT_FAMILIES:
            with (second / (family + ".csv")).open(
                    encoding="ascii", newline="") as handle:
                reached_roles.update(row["role_id"] for row in
                                     csv.DictReader(handle) if row["role_id"])
        self.assertEqual(len(original_manifest["roles"]), 42)
        self.assertEqual(reached_roles,
                         {role["id"] for role in original_manifest["roles"]})
        self.assertEqual(original_manifest["compact_input"][
            "scientific_content_digest"], augmented_manifest["compact_input"][
                "scientific_content_digest"])
        self.assertNotEqual(original_manifest["request_id"],
                            augmented_manifest["request_id"])
        self.assertNotEqual((second / "manifest.json").read_bytes(),
                            (augmented / "manifest.json").read_bytes())

    def test_migration_and_lossless_paths_are_not_runtime_inputs(self):
        before = self._query(
            "balancing", "--tune", "MONASH", "--profile", "inclusive",
            "--activity", "charged_light_sector_activity_a15_v1_eta4",
            "--class-id", "0", "--pair", "411:-411")
        measurement = ROOT / "results/measurement"
        hidden = self.base / "migration-unavailable"
        measurement.rename(hidden)
        try:
            after = self._query(
                "balancing", "--tune", "MONASH", "--profile", "inclusive",
                "--activity", "charged_light_sector_activity_a15_v1_eta4",
                "--class-id", "0", "--pair", "411:-411")
        finally:
            hidden.rename(measurement)
        self.assertFalse(self.raw_hidden.parent.joinpath("raw").exists())
        self.assertEqual(before["rows"], after["rows"])


if __name__ == "__main__":
    unittest.main()
