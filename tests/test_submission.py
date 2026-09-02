import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from helpers import ROOT


def load_submit():
    path = ROOT / "pipeline/generate/submit.py"
    spec = importlib.util.spec_from_file_location("nominal_submit", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def declared_array(source, name):
    match = re.search(r"{}\{{\{{(.*?)\}}\}};".format(name), source, re.DOTALL)
    if not match:
        raise AssertionError("validator array not found: {}".format(name))
    return re.findall(r'"([^"]+)"', match.group(1))


FIXTURE = r'''
#include "physics.hpp"
#include "sha256.hpp"
#include "study_contract.hpp"
#include "TFile.h"
#include "TH1D.h"
#include "TH1I.h"
#include "TObjString.h"
#include "TTree.h"
#include <iomanip>
#include <locale>
#include <map>
#include <sstream>
#include <string>
#include <vector>

using namespace Hadronization;

int main(int argc, char** argv) {
  if (argc != 3) return 2;
  const std::string mode = argv[2];
  TFile output(argv[1], "RECREATE");
  TTree tree("tree", "fixture");
  ULong64_t eventId = 0;
  Int_t processCode = 121, hardChannel = 4, nMpi = 1;
  Double_t wrongProcessCode = 121.0, weight = 1.0, pthat = 2.0, hardScale = 2.0;
  Int_t mult10 = 0, mult40 = 0, species[6] = {0,0,0,0,0,0};
  Short_t chargeGrid[kLightGridCells] = {0}, baryonGrid[kLightGridCells] = {0};
  Int_t legacyMultiplicity = 0, legacyProcess = 121, nCharm = 1, nBeauty = 0;
  Int_t nBc = 0, qcSum = 0, qbSum = 0, conservation = 1, origin = 1, match = 1;
  std::map<std::string, std::vector<int>> integerVectors;
  std::map<std::string, std::vector<double>> doubleVectors;
  const std::vector<std::string> integerNames = {@INT_VECTORS@};
  const std::vector<std::string> doubleNames = {@DOUBLE_VECTORS@};
  if (mode != "zero") {
    tree.Branch("event_id", &eventId, "event_id/l");
    if (mode == "wrong_type") tree.Branch("process_code", &wrongProcessCode, "process_code/D");
    else tree.Branch("process_code", &processCode, "process_code/I");
    tree.Branch("hard_channel", &hardChannel, "hard_channel/I");
    tree.Branch("event_weight", &weight, "event_weight/D");
    tree.Branch("pthat", &pthat, "pthat/D");
    tree.Branch("hard_scale", &hardScale, "hard_scale/D");
    tree.Branch("n_mpi", &nMpi, "n_mpi/I");
    const std::string centralName = mode == "layout" ?
        "multiplicity_final_charged_nonheavy_eta10_v1" :
        "multiplicity_primary_charged_eta10_v1";
    const std::string wideName = mode == "layout" ?
        "multiplicity_final_charged_nonheavy_eta40_v1" :
        "multiplicity_primary_charged_eta40_v1";
    tree.Branch(centralName.c_str(), &mult10, (centralName + "/I").c_str());
    tree.Branch(wideName.c_str(), &mult40, (wideName + "/I").c_str());
    tree.Branch("multiplicity_central_by_species", species,
                "multiplicity_central_by_species[6]/I");
    tree.Branch("light_charge3_grid", chargeGrid, "light_charge3_grid[128]/S");
    tree.Branch("light_baryon_grid", baryonGrid, "light_baryon_grid[128]/S");
    tree.Branch("MULTIPLICITY", &legacyMultiplicity, "MULTIPLICITY/I");
    tree.Branch("PROCESSCODE", &legacyProcess, "PROCESSCODE/I");
    tree.Branch("NCHARM", &nCharm, "NCHARM/I");
    tree.Branch("NBEAUTY", &nBeauty, "NBEAUTY/I");
    tree.Branch("NBC", &nBc, "NBC/I");
    tree.Branch("final_heavy_qc_sum", &qcSum, "final_heavy_qc_sum/I");
    tree.Branch("final_heavy_qb_sum", &qbSum, "final_heavy_qb_sum/I");
    tree.Branch("heavy_flavour_conservation_ok", &conservation,
                "heavy_flavour_conservation_ok/I");
    tree.Branch("origin_classification_valid", &origin, "origin_classification_valid/I");
    tree.Branch("primary_all_heavy_match_valid", &match,
                "primary_all_heavy_match_valid/I");
    for (const auto& name : integerNames) {
      if (mode == "missing" && name == "heavyPdg") continue;
      tree.Branch(name.c_str(), &integerVectors[name]);
    }
    for (const auto& name : doubleNames) tree.Branch(name.c_str(), &doubleVectors[name]);
  }

  TH1D hMultiplicity("hMULTIPLICITY", "fixture", 10, -0.5, 9.5);
  TH1D hMultiplicityWide("hMULTIPLICITY_ETA40", "fixture", 10, -0.5, 9.5);
  TH1I hProcess("hPROCESS_CODE", "fixture", 1000, -0.5, 999.5);
  hMultiplicity.Sumw2(); hMultiplicityWide.Sumw2();
  for (int row = 0; row < 3; ++row) {
    eventId = mode == "duplicate_event" ? EventId(3, 0, 0, 0, 0) :
              EventId(3, 0, 0, 0, static_cast<std::uint64_t>(row));
    mult10 = row; mult40 = row;
    legacyMultiplicity = row;
    if (mode == "false_flag" && row == 1) conservation = 0;
    tree.Fill(); hMultiplicity.Fill(mult10, weight);
    hMultiplicityWide.Fill(mult40, weight); hProcess.Fill(processCode);
  }
  tree.Write(); hMultiplicity.Write(); hMultiplicityWide.Write(); hProcess.Write();

  TTree stability("heavy_stability_audit", "fixture");
  Int_t pdg = 0, isHadron = 1, isMeson = 1, isBaryon = 0, spinType = 1;
  Int_t charge3 = 0, nHeavyCharm = 1, nHeavyBeauty = 0;
  Int_t nc = 0, ncbar = 0, nb = 0, nbbar = 0, qc = 0, qb = 0;
  Int_t strangeness = 0, openHeavy = 1, hiddenHeavy = 0, central = 1;
  Int_t hasAnti = 1, antiVerified = 1, canDecay = 1, originalMayDecay = 1;
  Int_t finalMayDecay = 0; Double_t mass = 1.0, tau0 = 0.0; std::string particleName;
  stability.Branch("pdg", &pdg, "pdg/I"); stability.Branch("name", &particleName);
  stability.Branch("is_hadron", &isHadron, "is_hadron/I");
  stability.Branch("is_meson", &isMeson, "is_meson/I");
  stability.Branch("is_baryon", &isBaryon, "is_baryon/I");
  stability.Branch("spin_type", &spinType, "spin_type/I");
  stability.Branch("charge3", &charge3, "charge3/I");
  stability.Branch("n_charm", &nHeavyCharm, "n_charm/I");
  stability.Branch("n_beauty", &nHeavyBeauty, "n_beauty/I");
  stability.Branch("n_c", &nc, "n_c/I"); stability.Branch("n_cbar", &ncbar, "n_cbar/I");
  stability.Branch("n_b", &nb, "n_b/I"); stability.Branch("n_bbar", &nbbar, "n_bbar/I");
  stability.Branch("q_c", &qc, "q_c/I"); stability.Branch("q_b", &qb, "q_b/I");
  stability.Branch("strangeness", &strangeness, "strangeness/I");
  stability.Branch("open_heavy", &openHeavy, "open_heavy/I");
  stability.Branch("hidden_heavy", &hiddenHeavy, "hidden_heavy/I");
  stability.Branch("central_registry", &central, "central_registry/I");
  stability.Branch("has_antiparticle", &hasAnti, "has_antiparticle/I");
  stability.Branch("antiparticle_verified", &antiVerified, "antiparticle_verified/I");
  stability.Branch("mass", &mass, "mass/D"); stability.Branch("tau0", &tau0, "tau0/D");
  stability.Branch("can_decay", &canDecay, "can_decay/I");
  stability.Branch("original_may_decay", &originalMayDecay, "original_may_decay/I");
  stability.Branch("final_may_decay", &finalMayDecay, "final_may_decay/I");
  std::ostringstream stabilityText; stabilityText.imbue(std::locale::classic());
  stabilityText << "schema=" << kHeavyStabilityAuditSchema << "\n"
                << std::scientific << std::setprecision(17);
  for (int sign : {-1, 1}) {
    pdg = sign * 421; particleName = sign < 0 ? "D0bar" : "D0";
    nc = sign > 0 ? 1 : 0; ncbar = sign < 0 ? 1 : 0; qc = sign;
    stability.Fill();
    stabilityText << pdg << '\t' << std::quoted(particleName) << '\t'
                  << isHadron << '\t' << isMeson << '\t' << isBaryon << '\t'
                  << spinType << '\t' << charge3 << '\t' << nHeavyCharm << '\t'
                  << nHeavyBeauty << '\t' << nc << '\t' << ncbar << '\t' << nb
                  << '\t' << nbbar << '\t' << qc << '\t' << qb << '\t'
                  << strangeness << '\t' << openHeavy << '\t' << hiddenHeavy
                  << '\t' << central << '\t' << hasAnti << '\t' << antiVerified
                  << '\t' << mass << '\t' << tau0 << '\t' << canDecay << '\t'
                  << originalMayDecay << '\t' << finalMayDecay << '\n';
  }
  stability.Write();
  std::string stabilitySha = Sha256Hex(stabilityText.str());
  if (mode == "audit") stabilitySha.assign(64, '0');
  TObjString stabilityCanonical(stabilityText.str().c_str());
  stabilityCanonical.Write("heavy_stability_audit_canonical");
  TObjString stabilityShaObject(stabilitySha.c_str());
  stabilityShaObject.Write("heavy_stability_audit_sha256");

  TTree processes("process_counts", "fixture"); Int_t summaryCode = 121;
  ULong64_t summaryCount = mode == "closure" ? 2 : 3;
  processes.Branch("code", &summaryCode, "code/I");
  processes.Branch("count", &summaryCount, "count/l"); processes.Fill(); processes.Write();

  std::map<std::string, std::string> settingValues = {
      {"HardQCD:hardbbbar", "true"}, {"HardQCD:hardccbar", "true"},
      {"Main:numberOfEvents", "3"}, {"PhaseSpace:pTHatMin", "2"},
      {"Random:seed", "130000001"}, {"Random:setSeed", "true"}};
  TTree settings("effective_settings", "fixture"); std::string settingName, settingValue;
  settings.Branch("name", &settingName); settings.Branch("value", &settingValue);
  std::ostringstream settingsText; settingsText.imbue(std::locale::classic());
  settingsText << "schema=" << kEffectiveSettingsSchema << "\n";
  for (const auto& row : settingValues) {
    settingName = row.first; settingValue = row.second; settings.Fill();
    settingsText << std::quoted(settingName) << '\t' << std::quoted(settingValue) << '\n';
  }
  settings.Write(); const std::string settingsSha = Sha256Hex(settingsText.str());
  TObjString settingsCanonical(settingsText.str().c_str());
  settingsCanonical.Write("effective_settings_canonical");
  TObjString settingsShaObject(settingsSha.c_str());
  settingsShaObject.Write("effective_settings_sha256");

  TTree metadata("job_metadata", "fixture");
  const std::vector<std::string> stringNames = {@METADATA_STRINGS@};
  const std::vector<std::string> intNames = {@METADATA_INTS@};
  const std::vector<std::string> unsignedNames = {@METADATA_UNSIGNED@};
  const std::vector<std::string> longNames = {@METADATA_LONG@};
  const std::vector<std::string> realNames = {@METADATA_DOUBLE@};
  std::map<std::string, std::string> ms; std::map<std::string, Int_t> mi;
  std::map<std::string, ULong64_t> mu; std::map<std::string, Long64_t> ml;
  std::map<std::string, Double_t> md;
  for (const auto& name : stringNames) metadata.Branch(name.c_str(), &ms[name]);
  for (const auto& name : intNames) metadata.Branch(name.c_str(), &mi[name], (name + "/I").c_str());
  for (const auto& name : unsignedNames) metadata.Branch(name.c_str(), &mu[name], (name + "/l").c_str());
  for (const auto& name : longNames) metadata.Branch(name.c_str(), &ml[name], (name + "/L").c_str());
  for (const auto& name : realNames) metadata.Branch(name.c_str(), &md[name], (name + "/D").c_str());
  ms["campaign"] = "HF_RUN3_V1"; ms["raw_schema"] = "hf_primary_ground_raw_v7";
  ms["selector"] = kSelectorVersion; ms["origin_algorithm"] = kOriginAlgorithmVersion;
  ms["species_registry_schema"] = std::string(kSpeciesRegistrySchema);
  ms["species_registry_sha256"] = std::string(kSpeciesRegistrySha256);
  ms["multiplicity_definition"] = std::string(kMultiplicityDefinitionVersion);
  ms["light_compensation_grid_schema"] = kLightCompensationGridSchema;
  ms["tune_difference_allowlist_schema"] = std::string(kTuneDifferenceAllowlistSchema);
  ms["tune_difference_allowlist_sha256"] = std::string(kTuneDifferenceAllowlistSha256);
  ms["heavy_stability_audit_schema"] = kHeavyStabilityAuditSchema;
  ms["heavy_stability_audit_sha256"] = stabilitySha;
  ms["effective_settings_schema"] = kEffectiveSettingsSchema;
  ms["effective_settings_sha256"] = settingsSha;
  ms["primary_all_heavy_match_schema"] = kPrimaryAllHeavyMatchSchema;
  ms["config_sha256"] = std::string(64, 'a'); ms["executable_sha256"] = std::string(64, 'b');
  ms["repository_commit"] = std::string(40, 'c'); ms["repository_dirty"] = "false";
  ms["root_version"] = "fixture"; ms["pythia_version"] = "8.317";
  ms["tune"] = mode == "identity" ? "JUNCTIONS" : "MONASH"; ms["role"] = "primary";
  ms["host"] = "fixture"; ms["condor_cluster"] = ""; ms["condor_process"] = "";
  mi["campaign_ordinal"] = 3; mi["logical_id"] = 0; mi["attempt"] = 0;
  mi["seed"] = 130000001; mi["complete"] = 1;
  mi["root_compression_settings"] = output.GetCompressionSettings();
  mi["root_compression_algorithm"] = output.GetCompressionAlgorithm();
  mi["root_compression_level"] = output.GetCompressionLevel();
  mu["requested_successes"] = 3; mu["attempts"] = 3;
  mu["successful_events"] = mode == "accounting" ? 2 : 3;
  mu["failed_attempts"] = 0; mu["tree_entries"] = 3;
  mu["effective_settings_entries"] = settingValues.size(); mu["peak_rss_kib"] = 1;
  ml["start_unix_seconds"] = 1; ml["end_unix_seconds"] = 2; ml["elapsed_seconds"] = 1;
  md["sum_weights"] = 3.0; md["sum_weights2"] = 3.0; md["phase_space_pthat_min"] = 2.0;
  md["pythia_sigma_gen_mb"] = 1.0; md["pythia_sigma_err_mb"] = 0.0;
  md["pythia_weight_sum"] = 3.0;
  metadata.Fill(); metadata.Write();
  TObjString changed("fixture"); changed.Write("effective_changed_settings");
  TObjString stats("fixture"); stats.Write("pythia_statistics");
  TObjString centralVersion(kMultiplicityCentral.data());
  centralVersion.Write("multiplicity_central_version");
  TObjString wideVersion(kMultiplicityCrossCheck.data());
  wideVersion.Write("multiplicity_crosscheck_version");
  TObjString definition(kMultiplicityDefinitionVersion.data());
  definition.Write("multiplicity_definition");
  TObjString matchVersion(kPrimaryAllHeavyMatchSchema);
  matchVersion.Write("primary_all_heavy_match_version");
  output.Write(); output.Close(); return 0;
}
'''


class SubmissionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.submit = load_submit()
        try:
            runtime = cls.submit.runtime_contract.resolve(require_root=True)
        except ValueError as error:
            raise unittest.SkipTest("ROOT unavailable for raw validator fixtures: {}".format(error))
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name)
        cls.validator = cls.base / "validate_raw"
        cls.submit.compile_validator(runtime, cls.validator)
        validator_source = (ROOT / "pipeline/generate/validate_raw.cpp").read_text(encoding="utf-8")
        replacements = {
            "@INT_VECTORS@": declared_array(validator_source, "integerVectors"),
            "@DOUBLE_VECTORS@": (declared_array(validator_source, "doubleVectors") +
                                  declared_array(validator_source, "finalDoubleVector") +
                                  declared_array(validator_source, "hardDoubleVectors")),
            "@METADATA_STRINGS@": declared_array(validator_source, "metadataStrings"),
            "@METADATA_INTS@": declared_array(validator_source, "metadataInts"),
            "@METADATA_UNSIGNED@": declared_array(validator_source, "metadataUnsigned"),
            "@METADATA_LONG@": declared_array(validator_source, "metadataLong"),
            "@METADATA_DOUBLE@": declared_array(validator_source, "metadataDouble"),
        }
        source = FIXTURE
        for token, values in replacements.items():
            source = source.replace(token, ", ".join(json.dumps(value) for value in values))
        source_path = cls.base / "fixture.cpp"
        source_path.write_text(source, encoding="utf-8")
        cls.fixture = cls.base / "fixture"
        environment = dict(__import__("os").environ)
        environment.update(runtime["environment"])
        flags = shlex.split(subprocess.check_output(
            [environment["ROOT_CONFIG"], "--cflags", "--libs"],
            text=True, env=environment))
        command = [environment["CXX"], "-std=c++17", "-Wall", "-Wextra",
                   "-Wpedantic", str(source_path),
                   "-I" + str(ROOT / "pipeline/generate")] + flags + ["-o", str(cls.fixture)]
        subprocess.run(command, check=True, env=environment,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def make_and_validate(self, mode):
        output = self.base / "{}.root".format(mode)
        subprocess.run([str(self.fixture), str(output), mode], check=True)
        command = [str(self.validator), str(output), "--campaign", "HF_RUN3_V1",
                   "--tune", "MONASH", "--campaign-ordinal", "3",
                   "--logical-id", "0", "--attempt", "0", "--seed", "130000001",
                   "--events", "3", "--pthat-min", "2", "--config-sha256", "a" * 64,
                   "--executable-sha256", "b" * 64, "--repository-commit", "c" * 40,
                   "--pythia-version", "8.317"]
        return subprocess.run(command, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)

    def test_validator_accepts_complete_compact_raw_v7_fixture(self):
        result = self.make_and_validate("valid")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("RAW_VALIDATION_PASS", result.stdout)

    def test_validator_rejects_schema_counterfeits_and_branch_mutations(self):
        diagnostics = {
            "zero": "exact 110-branch",
            "missing": "exact 110-branch",
            "wrong_type": "incorrectly typed event branch process_code",
            "layout": "exact 110-branch",
        }
        for mode, diagnostic in diagnostics.items():
            result = self.make_and_validate(mode)
            self.assertNotEqual(result.returncode, 0, mode)
            self.assertIn(diagnostic, result.stdout, (mode, result.stdout))

    def test_validator_rejects_identity_accounting_event_and_audit_mutations(self):
        diagnostics = {
            "identity": "authorization mismatch",
            "accounting": "exact-success/tree-entry",
            "duplicate_event": "duplicate event ID",
            "false_flag": "false required event validity flag",
            "audit": "heavy-stability tree/canonical digest mismatch",
            "closure": "process accounting",
        }
        for mode, diagnostic in diagnostics.items():
            result = self.make_and_validate(mode)
            self.assertNotEqual(result.returncode, 0, mode)
            self.assertIn(diagnostic, result.stdout, (mode, result.stdout))

    def test_complete_accepted_campaign_is_inventory_not_3000_new_attempts(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            measured = self.submit.inventory(
                campaign, tunes, ROOT / "data/raw_manifest.jsonl",
                ROOT / "data/attempts.csv", base / "raw", base / "work")
            rows = self.submit.plan_rows(campaign, tunes, measured, "continuation")
            self.assertEqual(rows, [])
            self.assertEqual(set(measured["statuses"].values()), {"accepted_missing_local"})

    def test_occupied_unregistered_path_refuses_and_reservation_never_reuses(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        campaign = dict(campaign)
        campaign["logical_jobs_per_tune"] = 1
        tunes = tunes[:1]
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            manifest = base / "manifest.jsonl"
            manifest.write_text("", encoding="utf-8")
            attempts = base / "attempts.csv"
            attempts.write_text("tune,logical_id,attempt,seed,outcome,raw_storage_key,evidence_status\n",
                                encoding="utf-8")
            stable = base / "raw/MONASH/hf_MONASH_job000.root"
            stable.parent.mkdir(parents=True)
            stable.write_bytes(b"occupied")
            measured = self.submit.inventory(campaign, tunes, manifest, attempts,
                                             base / "raw", base / "work")
            with self.assertRaisesRegex(ValueError, "refusing overwrite"):
                self.submit.plan_rows(campaign, tunes, measured, "continuation")
            stable.unlink()
            measured = self.submit.inventory(campaign, tunes, manifest, attempts,
                                             base / "raw", base / "work")
            first = self.submit.plan_rows(campaign, tunes, measured, "continuation")
            self.assertEqual(first[0]["attempt"], 0)
            self.submit.reserve_rows(campaign, first, base / "work", "d" * 64)
            measured = self.submit.inventory(campaign, tunes, manifest, attempts,
                                             base / "raw", base / "work")
            self.assertEqual(self.submit.plan_rows(campaign, tunes, measured, "continuation"), [])
            row = json.loads((base / "work/evidence/MONASH/job000/attempt00/reservation.json").read_text(
                encoding="utf-8"))
            self.assertEqual((row["attempt"], row["seed"], row["state"]),
                             (0, 130000001, "reserved"))

    def test_preworker_hold_is_durable_and_advances_the_next_attempt(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        campaign = dict(campaign)
        campaign["logical_jobs_per_tune"] = 1
        tunes = tunes[:1]
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            manifest = base / "manifest.jsonl"
            manifest.write_text("", encoding="utf-8")
            attempts = base / "attempts.csv"
            attempts.write_text(
                "tune,logical_id,attempt,seed,outcome,raw_storage_key,evidence_status\n",
                encoding="utf-8")
            measured = self.submit.inventory(campaign, tunes, manifest, attempts,
                                             base / "raw", base / "work")
            row = self.submit.plan_rows(campaign, tunes, measured, "continuation")[0]
            self.submit.reserve_rows(campaign, [row], base / "work", "d" * 64)
            args = type("Args", (), {"tune": "MONASH", "logical_id": 0,
                                     "attempt": 0, "state": "held",
                                     "reason": "periodic CPU hold"})()
            outcome = self.submit.record_preworker_outcome(args, base / "work")
            recorded = json.loads(outcome.read_text(encoding="utf-8"))
            self.assertEqual((recorded["state"], recorded["seed"], recorded["stage"]),
                             ("held", 130000001, "scheduler_before_worker"))
            measured = self.submit.inventory(campaign, tunes, manifest, attempts,
                                             base / "raw", base / "work")
            next_row = self.submit.plan_rows(campaign, tunes, measured, "continuation")[0]
            self.assertEqual((next_row["attempt"], next_row["seed"]), (1, 130100001))

    def test_promotion_is_no_overwrite_and_receipt_failure_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            partial = base / "partial.root"
            partial.write_bytes(b"validated fixture")
            stable = base / "raw/MONASH/hf_MONASH_job000.root"
            receipt = {"output_sha256": self.submit.digest_file(partial), "state": "PASS"}
            receipt_path = base / "evidence/validation_receipt.json"
            outcome_path = base / "evidence/outcome.json"
            with mock.patch.object(self.submit, "atomic_json", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(OSError, "disk full"):
                    self.submit.commit_validated_output(
                        partial, stable, receipt_path, outcome_path, receipt)
            self.assertFalse(stable.exists())
            self.submit.commit_validated_output(
                partial, stable, receipt_path, outcome_path, receipt)
            self.assertEqual(stable.read_bytes(), partial.read_bytes())
            stable.write_bytes(b"accepted namespace")
            with self.assertRaisesRegex(RuntimeError, "refusing overwrite"):
                self.submit.promote_no_overwrite(partial, stable, receipt["output_sha256"])
            self.assertEqual(stable.read_bytes(), b"accepted namespace")

    def test_scheduler_contract_and_each_liveness_clause_is_active(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        runtime = self.submit.runtime_contract.resolve()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            rendered = self.submit.render_submit(
                campaign, study, [], runtime, base / "producer", base / "validator",
                base / "raw", base / "work", "continuation")
        self.assertTrue(self.submit.validate_submit_contract(rendered))
        for clause in ("RemoteUserCpu > 3600", "CurrentTime - EnteredCurrentStatus) > 14400",
                       "on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)",
                       "max_retries = 0"):
            mutated = rendered.decode("utf-8").replace(clause, "REMOVED", 1)
            with self.assertRaisesRegex(ValueError, "Condor safety contract"):
                self.submit.validate_submit_contract(mutated)

    def test_default_generate_contacts_nothing_and_submit_no_work_contacts_nothing(self):
        ordinary = subprocess.run([str(ROOT / "hadronization"), "generate"],
                                  cwd="/tmp", text=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        self.assertEqual(ordinary.returncode, 0, ordinary.stderr)
        self.assertIn("jobs=0", ordinary.stdout)
        submitted = subprocess.run([str(ROOT / "hadronization"), "generate", "--submit"],
                                   cwd="/tmp", text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        self.assertEqual(submitted.returncode, 0, submitted.stderr)
        self.assertIn("scheduler not contacted", submitted.stdout)


if __name__ == "__main__":
    unittest.main()
