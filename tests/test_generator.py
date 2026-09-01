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
#include "selected_states.hpp"
using namespace Hadronization;
int main() {
  if (!CarriesSignedHeavyConstituent(4, 4, 1)) return 1;
  if (CarriesSignedHeavyConstituent(-4, 4, 1)) return 2;
  if (!IsCentralKinematic(1.01, 4.0, true)) return 3;
  if (IsCentralKinematic(1.0, 0.0, true)) return 4;
  if (!CountsNchFinalChargedNonHeavyV1(true, true, false, 0.151, 1.0, 1.0)) return 5;
  if (CountsNchFinalChargedNonHeavyV1(true, true, true, 1.0, 0.0, 1.0)) return 6;
  if (!FindSelectedState(421) || FindSelectedState(999999)) return 7;
  if (IsCentralEligible(5212) || !IsCentralEligible(521)) return 8;
  if (TuneOrdinal("MONASH") != 0 || TuneOrdinal("CLOSEPACKING") != 2) return 9;
  return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "contract.cpp"
            binary = Path(directory) / "contract"
            source_path.write_text(source, encoding="utf-8")
            command = [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
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
        self.assertNotIn("card_variant", source)
        settings = (ROOT / "pipeline/generate/tune_settings.hpp").read_text(
            encoding="utf-8")
        self.assertNotIn("SystematicVariation", settings)
        self.assertNotIn("SigmaProcess:renormMultFac", settings)

    def test_seed_block_attempt_and_card_materialization(self):
        submit = load_submit()
        campaign, study, tunes = submit.campaign_inputs()
        rows = submit.plan_rows(campaign, tunes)
        self.assertEqual(len(rows), 3000)
        self.assertEqual(rows[0]["block"], 1)
        self.assertEqual(rows[9]["block"], 10)
        self.assertEqual(rows[10]["block"], 1)
        self.assertEqual(rows[0]["seed"],
                         submit.seed_for(campaign, "MONASH", 0, rows[0]["attempt"]))
        self.assertGreaterEqual(rows[0]["attempt"], 1)
        card = ROOT / "config/tunes/monash.cmnd"
        materialized = submit.materialized_card(card, 100000).decode("utf-8")
        self.assertIn("Main:numberOfEvents = 100000", materialized)
        self.assertEqual(materialized.count("Main:numberOfEvents"), 1)

    def test_full_generator_link_or_explicit_skip(self):
        submit = load_submit()
        values = submit.site_values(ROOT / "config/site.conf")
        pythia_available = (values.get("PYTHIA8_CONFIG")
                            or values.get("PYTHIA8_PREFIX")
                            or shutil.which("pythia8-config"))
        if not pythia_available:
            self.skipTest("PYTHIA unavailable; full generator link is not falsely green")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "producer"
            result = subprocess.run(
                [__import__("sys").executable,
                 str(ROOT / "pipeline/generate/submit.py"), "build",
                 "--output", str(output)], cwd=str(ROOT), text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
