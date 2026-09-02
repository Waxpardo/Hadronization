import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from helpers import ROOT, load_json


def load_submit():
    path = ROOT / "pipeline/generate/submit.py"
    spec = importlib.util.spec_from_file_location("nominal_submit", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GeneratorContract(unittest.TestCase):
    def test_pure_physics_selection_origin_and_state_contracts_compile(self):
        compiler = shutil.which("c++") or shutil.which("g++")
        if not compiler:
            self.skipTest("C++ compiler unavailable; doctor reports it as optional")
        source = r'''
#include "physics.hpp"
#include "study_contract.hpp"
#include <cmath>
#include <map>
using namespace Hadronization;
int main() {
  if (!CarriesSignedHeavyConstituent(4, 4, 1)) return 1;
  if (CarriesSignedHeavyConstituent(-4, 4, 1)) return 2;
  if (!IsCentralKinematic(1.01, 4.0, true)) return 3;
  if (IsCentralKinematic(1.0, 0.0, true)) return 4;
  if (!CountsNchPrimaryChargedV1(true, true, false, 0.151, 1.0, 1.0)) return 5;
  if (CountsNchPrimaryChargedV1(true, true, true, 1.0, 0.0, 1.0)) return 6;
  const auto* state = FindSelectedState(421);
  if (!state || state->id != "dzero" || state->name != "D0" ||
      state->sector != "charm" || state->kind != "meson" || state->spin2j1 != 1 ||
      state->charge3 != 0 || state->qc != 1 || state->qb != 0 ||
      state->valence != "c ubar" || !state->pairAnalysisEligible ||
      state->status != "pair_analysis" || FindSelectedState(999999)) return 7;
  if (IsPairAnalysisEligible(5212) || !IsPairAnalysisEligible(521)) return 8;
  if (TuneOrdinal("MONASH") != 0 || TuneOrdinal("CLOSEPACKING") != 2 ||
      TuneOrdinal("close_packing") != 2 ||
      FindTuneDefinition("junctions")->name != "JUNCTIONS" ||
      TuneCardBasename(kTuneDefinitions[2]) != "close_packing.cmnd" ||
      kTuneDefinitions[2].card != "config/tunes/close_packing.cmnd") return 9;
  std::map<int, int> pdg{{1, 4}, {2, 4}, {3, 421}};
  std::map<int, int> status{{1, -23}, {2, -51}, {3, 83}};
  std::map<int, std::vector<int>> mothers{{1, {}}, {2, {1}}, {3, {2}}};
  const auto originMatch = MatchHeavyOriginGraph(
      3, 4, 4, 1, [&](int i) { return pdg[i]; },
      [&](int i) { return status[i]; }, [&](int i) { return mothers[i]; },
      [&](int i, int signedFlavour) { return i == 1 && signedFlavour == 4; });
  if (originMatch.origin != Origin::kSelectedHard || originMatch.hardRootIndex != 1 ||
      originMatch.depth != 2 || originMatch.resolution != MatchResolution::kUnique) return 10;
  std::vector<int> final{1, 1}, charge{1, 1};
  std::vector<int> origins(2, static_cast<int>(Origin::kSelectedHard));
  std::vector<int> resolutions(2, static_cast<int>(MatchResolution::kUnique));
  std::vector<int> matched{9, 9};
  const auto unique = EnforceUniqueFinalHardCarrier(final, charge, origins, resolutions, matched);
  if (unique.conflictGroups != 1 || unique.demotedMatches != 2 || matched[0] != -1 ||
      resolutions[1] != static_cast<int>(MatchResolution::kDuplicateHardCarrier)) return 11;
  final = {1}; charge = {2}; origins = {static_cast<int>(Origin::kSelectedHard)};
  resolutions = {static_cast<int>(MatchResolution::kUnique)}; matched = {8};
  std::vector<int> rejected{-1};
  if (RejectFinalMultiHeavyCarrier(final, charge, origins, resolutions, matched, rejected) != 1 ||
      rejected[0] != 8 || resolutions[0] !=
          static_cast<int>(MatchResolution::kMultipleHeavyConstituents)) return 12;
  if (EventId(3, 2, 999, 4, 17) !=
      ((3ULL << 48) | (2ULL << 46) | (999ULL << 32) | (4ULL << 20) | 17ULL)) return 13;
  const auto dbar = DecodeHeavyContent(-421, true, false);
  const auto lambdab = DecodeHeavyContent(5122, false, true);
  if (dbar.ncbar != 1 || dbar.qc() != -1 || lambdab.nb != 1 || lambdab.qb() != 1) return 14;
  int baryon = 0;
  if (!DecodePythiaBaryonNumber(-5122, false, true, -3, baryon) || baryon != -1) return 15;
  if (LightGridCell(0.0, 0.0) < 0 || LightGridCell(4.1, 0.0) != -1 ||
      !(WrapAbsolutePhi(4.0) < 3.141593) ||
      !(WrapDeltaPhi(0.0, 0.0) > -1.570797)) return 16;
  return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "contract.cpp"
            binary = Path(directory) / "contract"
            source_path.write_text(source, encoding="utf-8")
            command = [compiler, "-std=c++17", "-Wall", "-Wextra", "-Wpedantic",
                       "-Wconversion", "-Wshadow", "-Werror",
                       "-I" + str(ROOT / "pipeline/generate"), str(source_path),
                       "-o", str(binary)]
            subprocess.run(command, check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            subprocess.run([str(binary)], check=True)

    def test_exact_success_and_nominal_only_source_guards(self):
        source = (ROOT / "pipeline/generate/producer.cpp").read_text(encoding="utf-8")
        self.assertIn("while (successes < requestedSuccesses", source)
        self.assertIn("successes == requestedSuccesses", source)
        self.assertIn("StabilizeHeavyHadrons", source)
        self.assertIn("mayDecay(id, false)", source)
        self.assertIn("kRawMultiplicityEta10Branch", source)
        self.assertIn("kRawTuneAllowlistSchemaBranch", source)
        self.assertNotIn("multiplicity_final_charged_nonheavy_eta10_v1", source)
        self.assertNotIn('metadata.Branch("study_definition_schema"', source)
        self.assertNotIn("card_variant", source)
        settings = (ROOT / "pipeline/generate/study_contract.hpp").read_text(
            encoding="utf-8")
        self.assertNotIn("SystematicVariation", settings)
        self.assertNotIn("SigmaProcess:renormMultFac", settings)

    def test_seed_block_attempt_and_card_materialization(self):
        submit = load_submit()
        campaign, study, tunes = submit.campaign_inputs()
        self.assertEqual(submit.seed_for(campaign, "MONASH", 0, 0), 130000001)
        self.assertEqual(submit.seed_for(campaign, "CLOSEPACKING", 999, 4), 132401000)
        card = ROOT / "config/tunes/monash.cmnd"
        materialized = submit.materialized_card(card, 100000).decode("utf-8")
        self.assertIn("Main:numberOfEvents = 100000", materialized)
        self.assertEqual(materialized.count("Main:numberOfEvents"), 1)

    def test_full_generator_link_or_explicit_skip(self):
        submit = load_submit()
        try:
            submit.runtime_contract.resolve(require_root=True, require_pythia=True)
        except ValueError:
            self.skipTest("PYTHIA unavailable; full generator link is not falsely green")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "producer"
            result = subprocess.run(
                [__import__("sys").executable,
                 str(ROOT / "pipeline/generate/submit.py"), "build", "--component", "producer",
                 "--producer", str(output)], cwd=str(ROOT), text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
