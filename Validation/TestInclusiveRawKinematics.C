#include "../PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C"

#include "TFile.h"
#include "TH1D.h"
#include "TSystem.h"
#include "TTree.h"

#include <cmath>
#include <iostream>
#include <limits>
#include <string>
#include <unistd.h>
#include <vector>

namespace {

void WriteCanonicalToy(const std::string& path, bool includeTrueOverflow = false)
{
  TFile file(path.c_str(), "RECREATE");
  TTree tree("tree", "canonical inclusive-spectrum toy");

  double eventWeight = 1.0;
  std::vector<int> pdg;
  std::vector<int> status;
  std::vector<int> isFinal;
  std::vector<int> central;
  std::vector<double> pt;
  std::vector<double> eta;
  std::vector<double> phi;

  tree.Branch("event_weight", &eventWeight, "event_weight/D");
  tree.Branch("heavyPdg", &pdg);
  tree.Branch("heavyStatus", &status);
  tree.Branch("heavyIsFinal", &isFinal);
  tree.Branch("heavyCentral", &central);
  tree.Branch("heavyPt", &pt);
  tree.Branch("heavyEta", &eta);
  tree.Branch("heavyPhi", &phi);

  auto add = [&](int particlePdg, int particleStatus, int particleIsFinal,
                 int particleCentral, double particlePt, double particleEta,
                 double particlePhi) {
    pdg.push_back(particlePdg);
    status.push_back(particleStatus);
    isFinal.push_back(particleIsFinal);
    central.push_back(particleCentral);
    pt.push_back(particlePt);
    eta.push_back(particleEta);
    phi.push_back(particlePhi);
  };

  eventWeight = 2.0;
  add(411, 81, 1, 1, 0.2, 4.0, 4.0);  // accepted D+
  add(411, 81, 1, 1, 0.15, 0.0, 0.0); // strict pT boundary: rejected
  add(411, 81, 1, 1, 0.2, std::nextafter(4.0, 5.0), 0.0);
  add(411, 81, 0, 1, 0.2, 0.0, 0.0);
  add(411, 81, 1, 0, 0.2, 0.0, 0.0);
  add(411, -81, 1, 1, 0.2, 0.0, 0.0);
  add(411, 91, 1, 1, 0.2, 0.0, 0.0);
  add(411, 81, 1, 1, 7000.0, 0.0, 0.0);
  if (includeTrueOverflow) {
    add(411, 81, 1, 1,
        std::nextafter(7000.0, std::numeric_limits<double>::infinity()),
        0.0, 0.0);
  }
  add(-411, 89, 1, 1, 0.2, -4.0, -4.0); // accepted D-
  tree.Fill();

  pdg.clear();
  status.clear();
  isFinal.clear();
  central.clear();
  pt.clear();
  eta.clear();
  phi.clear();

  eventWeight = 3.0;
  add(411, 89, 1, 1, 1.0, 0.0, 0.0); // accepted D+
  tree.Fill();

  std::string rawSchema = Hadronization::kRawSchema;
  std::string speciesSchema(Hadronization::kSpeciesRegistrySchema);
  std::string speciesSha256(Hadronization::kSpeciesRegistrySha256);
  TTree metadata("job_metadata", "toy metadata");
  metadata.Branch("raw_schema", &rawSchema);
  metadata.Branch("species_registry_schema", &speciesSchema);
  metadata.Branch("species_registry_sha256", &speciesSha256);
  metadata.Fill();

  TH1D multiplicity("hMULTIPLICITY", "", 10, -0.5, 9.5);
  multiplicity.Sumw2();
  multiplicity.Fill(1.0, 2.0);
  multiplicity.Fill(2.0, 3.0);

  tree.Write();
  metadata.Write();
  multiplicity.Write();
  file.Close();
}

void WriteLegacyToy(const std::string& path)
{
  TFile file(path.c_str(), "RECREATE");
  TTree tree("tree", "legacy inclusive-spectrum toy");

  std::vector<int> pdg{411};
  std::vector<double> pt{0.15};
  std::vector<double> eta{4.0};
  std::vector<double> phi{0.0};
  tree.Branch("ID", &pdg);
  tree.Branch("PT", &pt);
  tree.Branch("ETA", &eta);
  tree.Branch("PHI", &phi);
  tree.Fill();
  tree.Write();
  TH1D multiplicity("hMULTIPLICITY", "", 10, -0.5, 9.5);
  multiplicity.Fill(1.0);
  multiplicity.Write();
  file.Close();
}

bool NearlyEqual(double left, double right, double tolerance = 1.0e-12)
{
  return std::abs(left - right) <= tolerance;
}

void DestroyTuneData(InclusiveRawKinematics::TuneData& data)
{
  delete data.multiplicity;
  data.multiplicity = nullptr;
  for (auto& item : data.spectra) {
    InclusiveRawKinematics::DeleteHistSet(item.second);
  }
}

} // namespace

int TestInclusiveRawKinematics()
{
  using namespace InclusiveRawKinematics;

  int failures = 0;
  auto require = [&](bool condition, const std::string& message) {
    if (!condition) {
      std::cerr << "INCLUSIVE_RAW_TEST_FAIL " << message << "\n";
      ++failures;
    }
  };

  require(!PassCanonicalInclusiveSelection(81, 1, 1, 0.15, 0.0),
          "canonical pT threshold must be strict");
  require(PassCanonicalInclusiveSelection(
            81, 1, 1, std::nextafter(0.15, 1.0), 4.0),
          "canonical selection rejected the accepted pT/eta boundary");
  require(!PassCanonicalInclusiveSelection(
            81, 1, 1, 1.0, std::nextafter(4.0, 5.0)),
          "canonical selection accepted |eta| > 4");
  require(!PassCanonicalInclusiveSelection(81, 0, 1, 1.0, 0.0),
          "canonical selection accepted a non-final particle");
  require(!PassCanonicalInclusiveSelection(91, 1, 1, 1.0, 0.0),
          "canonical selection accepted a non-direct-primary status");
  require(!PassCanonicalInclusiveSelection(81, 1, 0, 1.0, 0.0),
          "canonical selection accepted a noncentral state");

  const std::string base =
    std::string(gSystem->TempDirectory()) +
    "/hadronization_inclusive_raw_test_" + std::to_string(gSystem->GetPid());
  const std::string canonicalBase = base + "/canonical";
  const std::string canonicalTune = canonicalBase + "/MONASH";
  const std::string canonicalFile = canonicalTune + "/toy.root";
  const std::string legacyBase = base + "/legacy";
  const std::string legacyTune = legacyBase + "/MONASH";
  const std::string legacyFile = legacyTune + "/toy.root";
  const std::string overflowBase = base + "/overflow";
  const std::string overflowTune = overflowBase + "/MONASH";
  const std::string overflowFile = overflowTune + "/toy.root";

  gSystem->mkdir(canonicalTune.c_str(), true);
  gSystem->mkdir(legacyTune.c_str(), true);
  gSystem->mkdir(overflowTune.c_str(), true);
  WriteCanonicalToy(canonicalFile);
  WriteLegacyToy(legacyFile);
  WriteCanonicalToy(overflowFile, true);

  try {
    constexpr int kCanonicalFiles = 100;
    const std::vector<std::string> canonicalFiles(
      kCanonicalFiles, canonicalFile);
    TuneData canonical = BuildTuneSpectra(
      "MONASH", canonicalFiles, DatasetInputMode::kCanonicalManifest, true);
    TH1D* dplus = canonical.spectra.at("Dplus").pt;
    TH1D* dminus = canonical.spectra.at("Dminus").pt;
    require(canonical.inputContract.find(Hadronization::kRawSchema) !=
              std::string::npos,
            "canonical contract was not identified");
    require(canonical.nFiles == kCanonicalFiles,
            "canonical exposure count mismatch");
    require(canonical.nEvents == 2 * kCanonicalFiles,
            "canonical event count mismatch");
    require(canonical.nSelectedParticles == 4 * kCanonicalFiles,
            "canonical unweighted selected-particle count mismatch");
    require(NearlyEqual(
              canonical.selectedParticleWeight, 9.0 * kCanonicalFiles),
            "canonical selected-particle weighted sum mismatch");
    require(NearlyEqual(dplus->Integral(), 7.0 * kCanonicalFiles),
            "D+ spectrum did not use stored event weights and canonical cuts");
    require(NearlyEqual(
              dplus->GetBinContent(dplus->FindFixBin(7000.0)),
              2.0 * kCanonicalFiles),
            "exact pT=7000 GeV was not retained in the final finite bin");
    require(NearlyEqual(dplus->GetBinContent(dplus->GetNbinsX() + 1), 0.0),
            "canonical pT spectrum contains a silent overflow");
    const double etaIntegral =
      canonical.spectra.at("Dplus").eta->Integral();
    const double phiIntegral =
      canonical.spectra.at("Dplus").phi->Integral();
    require(NearlyEqual(etaIntegral, 7.0 * kCanonicalFiles) &&
              NearlyEqual(phiIntegral, 7.0 * kCanonicalFiles),
            "canonical selection was not applied consistently to pT/eta/phi "
            "(eta=" + std::to_string(etaIntegral) +
            ", phi=" + std::to_string(phiIntegral) + ")");
    require(NearlyEqual(
              dplus->GetBinError(dplus->FindBin(0.2)),
              2.0 * std::sqrt(static_cast<double>(kCanonicalFiles))),
            "D+ Sumw2 does not retain the event weight");
    require(NearlyEqual(
              canonical.spectra.at("Dplus").phi->GetBinContent(
                canonical.spectra.at("Dplus").phi->FindBin(
                  WrapToMinusPiPi(4.0))),
              2.0 * kCanonicalFiles),
            "absolute phi was not wrapped with its stored event weight");
    require(NearlyEqual(dminus->Integral(), 2.0 * kCanonicalFiles),
            "D- spectrum content mismatch");
    require(canonical.multiplicity &&
              NearlyEqual(
                canonical.multiplicity->Integral(),
                5.0 * kCanonicalFiles),
            "weighted multiplicity histogram was not retained");
    DestroyTuneData(canonical);

    TuneData legacy = BuildTuneSpectra(
      "MONASH", {legacyFile},
      DatasetInputMode::kLegacyRecursiveDiagnostic, true);
    require(legacy.inputContract.find("legacy") != std::string::npos,
            "legacy contract was not identified");
    require(legacy.nSelectedParticles == 1,
            "legacy compatibility reader unexpectedly changed its upstream "
            "selection");
    require(NearlyEqual(legacy.spectra.at("Dplus").pt->Integral(), 1.0),
            "legacy compatibility reader did not retain unit weighting");
    DestroyTuneData(legacy);

    bool overflowRejected = false;
    try {
      TuneData overflow = BuildTuneSpectra(
        "MONASH", std::vector<std::string>(kCanonicalFiles, overflowFile),
        DatasetInputMode::kCanonicalManifest, true);
      DestroyTuneData(overflow);
    } catch (const std::exception& error) {
      overflowRejected =
        std::string(error.what()).find("pT histogram overflow") !=
        std::string::npos;
    }
    require(overflowRejected,
            "pT > 7000 GeV was not rejected as a technical overflow");
  } catch (const std::exception& error) {
    std::cerr << "INCLUSIVE_RAW_TEST_FAIL unexpected exception: "
              << error.what() << "\n";
    ++failures;
  }

  gSystem->Unlink(canonicalFile.c_str());
  gSystem->Unlink(legacyFile.c_str());
  gSystem->Unlink(overflowFile.c_str());
  ::rmdir(canonicalTune.c_str());
  ::rmdir(canonicalBase.c_str());
  ::rmdir(legacyTune.c_str());
  ::rmdir(legacyBase.c_str());
  ::rmdir(overflowTune.c_str());
  ::rmdir(overflowBase.c_str());
  ::rmdir(base.c_str());

  if (failures == 0) {
    std::cout
      << "INCLUSIVE_RAW_TEST_PASS canonical_selection=final_direct_primary_"
         "central_ground acceptance=associate origin=inclusive "
         "event_weight=stored pt_endpoint=7000_inclusive "
         "pt_overflow=fail_closed legacy=explicit\n";
  }
  return failures;
}
