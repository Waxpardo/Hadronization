// ---------------------------------------------------------------------------
// Plot_InclusiveKinematicSpectra_Raw.C
//
// Draw inclusive single-particle kinematic spectra directly from the generated
// raw trees. Canonical raw-v5 files are selected exclusively through the
// sealed canonical manifest and read through their
// authoritative heavy-particle vectors and event weights; the legacy
// recursive ID/PT/ETA/PHI reader remains an explicitly labelled diagnostic
// path.
// This deliberately does not use hTrKinematics or hAsKinematics from the
// THnSparse pair files, because those objects are trigger/associate
// conditioned and are not inclusive particle spectra.
//
// Default usage from the Hadronization repository root:
//
//   root -l -b <<'ROOT'
//   .L PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C+
//   Plot_InclusiveKinematicSpectra_Raw("RootFiles/HF",
//                                      "PlottingScripts/Plots/KinematicSpectra",
//                                      true, true,
//                                      "selector")
//   .q
//   ROOT
// ---------------------------------------------------------------------------

#include <algorithm>
#include <cctype>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "TCanvas.h"
#include "TChain.h"
#include "TFile.h"
#include "TAxis.h"
#include "TH1D.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TLine.h"
#include "TPad.h"
#include "TString.h"
#include "TStyle.h"
#include "TSystem.h"
#include "TTree.h"

#include "HistogramErrorUtils.h"
#include "TunePlotStyle.h"
#include "../SimulationScripts/GeneratedHeavyFlavourRegistry.h"
#include "../SimulationScripts/HeavyFlavourUtils.h"
#include "../SimulationScripts/Sha256.h"

#if __has_include(<nlohmann/json.hpp>)
#include <nlohmann/json.hpp>
#elif __has_include("nlohmann/json.hpp")
#include "nlohmann/json.hpp"
#else
#error "Could not find nlohmann/json.hpp. Source setupEnv.sh before compiling."
#endif

using json = nlohmann::json;

namespace InclusiveRawKinematics {

constexpr double kMultiplicityXMax = 170.0;
constexpr double kMultiplicityRatioYMin = 0.0;
constexpr double kMultiplicityRatioYMax = 4.0;
constexpr double kInclusivePtConfiguredMaxGeV = 7000.0;
constexpr double kInclusivePtDisplayMaxGeV = 50.0;

struct MultiplicityPercentileClass {
  double minPercentile;
  double maxPercentile;
  const char* label;
};

struct SpeciesDef {
  std::string key;
  std::string label;
  int pdg = 0;
  bool logPt = true;
};

struct HistSet {
  TH1D* pt = nullptr;
  TH1D* eta = nullptr;
  TH1D* phi = nullptr;
};

struct TuneData {
  std::string tune;
  int nFiles = 0;
  Long64_t nEvents = 0;
  Long64_t nSelectedParticles = 0;
  double selectedParticleWeight = 0.0;
  std::string inputContract;
  std::map<std::string, HistSet> spectra;
  TH1D* multiplicity = nullptr;
};

enum class RawInputMode {
  kCanonicalV5,
  kLegacy
};

enum class DatasetInputMode {
  kCanonicalManifest,
  kLegacyRecursiveDiagnostic
};

std::vector<std::string> TuneNames();

struct RawInputContract {
  RawInputMode mode = RawInputMode::kLegacy;
  bool hasEventWeight = false;
  std::string schema;
};

const char* RawInputModeName(RawInputMode mode)
{
  return mode == RawInputMode::kCanonicalV5
           ? "canonical raw-v5 heavy-vector mode"
           : "legacy ID/PT/ETA/PHI compatibility mode";
}

const char* DatasetInputModeName(DatasetInputMode mode)
{
  return mode == DatasetInputMode::kCanonicalManifest
           ? "sealed_canonical_manifest"
           : "legacy_recursive_diagnostic";
}

bool HasBranch(TTree* tree, const char* name)
{
  return tree && tree->GetBranch(name);
}

bool HasAllBranches(TTree* tree, const std::vector<const char*>& names)
{
  return std::all_of(names.begin(), names.end(),
                     [tree](const char* name) { return HasBranch(tree, name); });
}

bool HasAnyBranch(TTree* tree, const std::vector<const char*>& names)
{
  return std::any_of(names.begin(), names.end(),
                     [tree](const char* name) { return HasBranch(tree, name); });
}

bool ReadMetadataString(TTree* metadata, const char* name, std::string& value)
{
  if (!metadata || metadata->GetEntries() != 1 || !metadata->GetBranch(name)) {
    return false;
  }
  std::string* pointer = nullptr;
  metadata->SetBranchAddress(name, &pointer);
  const bool ok = metadata->GetEntry(0) > 0 && pointer;
  if (ok) value = *pointer;
  metadata->ResetBranchAddresses();
  return ok;
}

RawInputContract InspectRawInputContract(const std::string& filePath)
{
  std::unique_ptr<TFile> file(TFile::Open(filePath.c_str(), "READ"));
  if (!file || file->IsZombie()) {
    throw std::runtime_error("Could not open raw input: " + filePath);
  }

  TTree* tree = dynamic_cast<TTree*>(file->Get("tree"));
  if (!tree) {
    throw std::runtime_error("Raw input has no tree: " + filePath);
  }

  const std::vector<const char*> canonicalBranches = {
    "event_weight", "heavyPdg", "heavyStatus", "heavyIsFinal",
    "heavyCentral", "heavyPt", "heavyEta", "heavyPhi"
  };
  const std::vector<const char*> legacyBranches = {"ID", "PT", "ETA", "PHI"};

  if (HasAllBranches(tree, canonicalBranches)) {
    RawInputContract contract;
    contract.mode = RawInputMode::kCanonicalV5;
    contract.hasEventWeight = true;

    TTree* metadata = dynamic_cast<TTree*>(file->Get("job_metadata"));
    if (!ReadMetadataString(metadata, "raw_schema", contract.schema)) {
      throw std::runtime_error(
        "Authoritative heavy-vector input is missing job_metadata.raw_schema: " +
        filePath);
    }
    if (contract.schema != Hadronization::kRawSchema) {
      throw std::runtime_error(
        "Unsupported authoritative raw schema '" + contract.schema +
        "' in " + filePath + " (expected " +
        std::string(Hadronization::kRawSchema) + ")");
    }

    std::string speciesSchema;
    std::string speciesSha256;
    if (!ReadMetadataString(
          metadata, "species_registry_schema", speciesSchema) ||
        !ReadMetadataString(
          metadata, "species_registry_sha256", speciesSha256)) {
      throw std::runtime_error(
        "Canonical raw input is missing species-registry metadata required "
        "to interpret heavyCentral: " + filePath);
    }
    if (speciesSchema !=
          std::string(Hadronization::kSpeciesRegistrySchema) ||
        speciesSha256 !=
          std::string(Hadronization::kSpeciesRegistrySha256)) {
      throw std::runtime_error(
        "Canonical raw input species registry does not match this plotting "
        "checkout: " + filePath);
    }
    return contract;
  }

  if (HasAnyBranch(tree, canonicalBranches)) {
    throw std::runtime_error(
      "Raw input has an incomplete authoritative heavy-vector contract: " +
      filePath);
  }
  if (!HasAllBranches(tree, legacyBranches)) {
    throw std::runtime_error(
      "Raw input is neither canonical raw-v5 nor a supported legacy tree: " +
      filePath);
  }

  RawInputContract contract;
  contract.mode = RawInputMode::kLegacy;
  contract.hasEventWeight = HasBranch(tree, "event_weight");
  contract.schema = "legacy_status";
  return contract;
}

void RequireCompatibleContract(const RawInputContract& expected,
                               const RawInputContract& observed,
                               const std::string& filePath)
{
  if (expected.mode != observed.mode ||
      expected.hasEventWeight != observed.hasEventWeight ||
      expected.schema != observed.schema) {
    throw std::runtime_error(
      "Mixed raw-tree contracts within one tune are not supported; mismatch at " +
      filePath);
  }
}

bool PassCanonicalInclusiveSelection(int status, int isFinal, int central,
                                     double pt, double eta)
{
  // These are inclusive single-particle, associate-acceptance spectra. They
  // deliberately do not impose a selected-hard-origin requirement.
  return isFinal && central &&
         Hadronization::IsDirectPrimaryStatus(status) &&
         Hadronization::IsCentralKinematic(pt, eta, false);
}

std::string JoinPath(const std::vector<std::string>& pieces)
{
  std::string path;
  for (const auto& piece : pieces) {
    if (piece.empty()) continue;
    if (!path.empty() && path.back() != '/') path += "/";
    if (!path.empty() && piece.front() == '/') path += piece.substr(1);
    else path += piece;
  }
  return path;
}

bool IsAbsolutePath(const std::string& path)
{
  return !path.empty() && path.front() == '/';
}

std::string ExpandPath(const std::string& path)
{
  char* expanded = gSystem->ExpandPathName(path.c_str());
  std::string result = expanded ? expanded : path;
  delete[] expanded;
  return result;
}

std::string FindHadronizationBase()
{
  const char* envBase = std::getenv("HADRONIZATION_BASE");
  if (envBase && !gSystem->AccessPathName(JoinPath({envBase, "PlottingScripts"}).c_str())) {
    return ExpandPath(envBase);
  }

  std::string current = ExpandPath(gSystem->WorkingDirectory());
  while (!current.empty() && current != "/") {
    if (!gSystem->AccessPathName(JoinPath({current, "PlottingScripts"}).c_str())) {
      return current;
    }
    const size_t slash = current.find_last_of('/');
    if (slash == std::string::npos || slash == 0) break;
    current = current.substr(0, slash);
  }

  return ExpandPath(gSystem->WorkingDirectory());
}

std::string ResolveFromBase(const std::string& path, const std::string& base)
{
  if (path.empty()) return path;
  const std::string expanded = ExpandPath(path);
  if (IsAbsolutePath(expanded)) return expanded;
  return JoinPath({base, expanded});
}

std::string ParentPath(const std::string& path)
{
  const size_t slash = path.find_last_of('/');
  if (slash == std::string::npos) return ".";
  if (slash == 0) return "/";
  return path.substr(0, slash);
}

std::string EnvironmentValue(const char* name)
{
  const char* value = std::getenv(name);
  return value ? std::string(value) : std::string();
}

bool IsDirectory(const std::string& path)
{
  void* dir = gSystem->OpenDirectory(path.c_str());
  if (!dir) return false;
  gSystem->FreeDirectory(dir);
  return true;
}

void CollectRootFiles(const std::string& path, std::vector<std::string>& files)
{
  if (IsDirectory(path)) {
    void* dir = gSystem->OpenDirectory(path.c_str());
    if (!dir) return;

    const char* entry = nullptr;
    while ((entry = gSystem->GetDirEntry(dir))) {
      const std::string name(entry);
      if (name == "." || name == "..") continue;

      const std::string child = JoinPath({path, name});
      if (IsDirectory(child)) CollectRootFiles(child, files);
      else if (name.size() >= 5 && name.substr(name.size() - 5) == ".root") files.push_back(child);
    }

    gSystem->FreeDirectory(dir);
    return;
  }

  if (path.size() >= 5 && path.substr(path.size() - 5) == ".root") files.push_back(path);
}

bool IsSafeRelativePath(const std::string& path)
{
  if (path.empty() || IsAbsolutePath(path)) return false;
  std::istringstream stream(path);
  std::string component;
  while (std::getline(stream, component, '/')) {
    if (component.empty() || component == "." || component == "..") {
      return false;
    }
  }
  return true;
}

bool IsLowerHexSha256(const std::string& value)
{
  return value.size() == 64 &&
         std::all_of(
           value.begin(), value.end(),
           [](unsigned char character) {
             return std::isdigit(character) ||
                    (character >= 'a' && character <= 'f');
           });
}

json ReadJsonFile(const std::string& path, const std::string& label)
{
  std::ifstream input(path);
  if (!input) {
    throw std::runtime_error("Missing " + label + ": " + path);
  }
  json value;
  input >> value;
  if (!value.is_object()) {
    throw std::runtime_error(label + " is not a JSON object: " + path);
  }
  return value;
}

struct RawFileSelection {
  DatasetInputMode mode = DatasetInputMode::kLegacyRecursiveDiagnostic;
  std::string source;
  std::map<std::string, std::vector<std::string>> filesByTune;
};

DatasetInputMode ResolveDatasetInputMode(const std::string& requested)
{
  if (requested == "legacy_recursive_diagnostic") {
    return DatasetInputMode::kLegacyRecursiveDiagnostic;
  }
  const std::string status = EnvironmentValue(
      "HADRONIZATION_DATASET_STATUS");
  const std::string publicationEligible = EnvironmentValue(
      "HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE");
  if (requested == "canonical_manifest") {
    if (status != "canonical" || publicationEligible != "true") {
      throw std::runtime_error(
          "canonical_manifest mode requires "
          "HADRONIZATION_DATASET_STATUS=canonical and "
          "HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE=true");
    }
    return DatasetInputMode::kCanonicalManifest;
  }
  if (requested != "selector") {
    throw std::runtime_error(
        "Unknown raw input mode '" + requested +
        "'; use selector, canonical_manifest, or "
        "legacy_recursive_diagnostic");
  }
  if (status == "canonical" && publicationEligible == "true") {
    return DatasetInputMode::kCanonicalManifest;
  }
  if (status.rfind("legacy", 0) == 0 &&
      publicationEligible == "false") {
    return DatasetInputMode::kLegacyRecursiveDiagnostic;
  }
  throw std::runtime_error(
      "selector mode requires a consistent status/publication-eligibility "
      "pair from tools/dataset_selector.py; direct legacy diagnostics must "
      "pass legacy_recursive_diagnostic explicitly");
}

RawFileSelection LoadCanonicalManifestSelection(
    const std::string& hadronizationBase)
{
  const std::string configuredManifest = EnvironmentValue(
      "HADRONIZATION_CANONICAL_MANIFEST");
  const std::string configuredProduction = EnvironmentValue(
      "HADRONIZATION_PRODUCTION_ROOT");
  if (configuredManifest.empty() || configuredProduction.empty()) {
    throw std::runtime_error(
        "Canonical dataset selection requires both "
        "HADRONIZATION_CANONICAL_MANIFEST and "
        "HADRONIZATION_PRODUCTION_ROOT");
  }
  const std::string manifestPath =
      ResolveFromBase(configuredManifest, hadronizationBase);
  const std::string productionRoot =
      ResolveFromBase(configuredProduction, hadronizationBase);
  const std::string freezeDirectory = ParentPath(manifestPath);
  const std::string summaryPath =
      JoinPath({freezeDirectory, "freeze_summary.json"});
  const std::string receiptPath =
      JoinPath({freezeDirectory,
                "canonical_raw_validation_receipt.json"});
  const std::string sealPath =
      JoinPath({freezeDirectory, "freeze_seal.json"});

  const std::string manifestSha =
      Hadronization::Sha256FileHex(manifestPath);
  const std::string receiptSha =
      Hadronization::Sha256FileHex(receiptPath);
  const json summary = ReadJsonFile(summaryPath, "canonical freeze summary");
  const json receipt =
      ReadJsonFile(receiptPath, "canonical raw-validation receipt");
  const json seal = ReadJsonFile(sealPath, "canonical freeze seal");
  const std::string summarySchema = summary.value("schema", "");
  const bool firstStage =
      summarySchema == "hf_canonical_freeze_summary_v3";
  const bool superseding =
      summarySchema == "hf_superseding_canonical_freeze_summary_v4";
  const std::string rowSchema =
      firstStage ? "hf_canonical_raw_manifest_v2"
                 : "hf_superseding_canonical_raw_manifest_v3";
  const std::string receiptSchema =
      firstStage ? "hf_canonical_raw_validation_receipt_v2"
                 : "hf_superseding_canonical_raw_validation_receipt_v3";
  const std::string sealSchema =
      firstStage ? "hf_canonical_freeze_seal_v2"
                 : "hf_superseding_canonical_freeze_seal_v3";
  const int jobsPerTune = summary.value("jobs_per_tune", -1);
  const int expectedRows =
      jobsPerTune > 0 ? static_cast<int>(TuneNames().size()) * jobsPerTune
                      : -1;
  const bool validShape =
      (firstStage && jobsPerTune == 100) ||
      (superseding && jobsPerTune >= 110 && jobsPerTune % 10 == 0);
  std::map<std::string, std::vector<std::string>> sealedSourceContracts;
  std::map<std::string, int> sealedSourceExposure;
  bool validSourceInventory = !superseding;
  if (superseding) {
    const json sources = summary.value("source_freezes", json::array());
    int sourceJobs = 0;
    validSourceInventory = sources.is_array() && sources.size() >= 2;
    if (validSourceInventory) {
      for (const auto& source : sources) {
        const std::string campaign = source.value("campaign", "");
        const std::vector<std::string> contract = {
            source.value("canonical_manifest_sha256", ""),
            source.value("freeze_summary_sha256", ""),
            source.value("freeze_seal_sha256", ""),
        };
        const int sourceExposure =
            source.value("jobs_in_final_union_per_tune", -1);
        if (campaign.empty() ||
            source.value("production_prefix", "") != campaign ||
            sourceExposure < 1 ||
            !std::all_of(
                contract.begin(), contract.end(),
                [](const std::string& value) {
                  return IsLowerHexSha256(value);
                }) ||
            !sealedSourceContracts.emplace(campaign, contract).second) {
          validSourceInventory = false;
          break;
        }
        sealedSourceExposure[campaign] = sourceExposure;
        sourceJobs += sourceExposure;
      }
      validSourceInventory =
          validSourceInventory && sourceJobs == jobsPerTune &&
          sources.back().value("campaign", "") ==
              summary.value("campaign", "") &&
          Hadronization::Sha256Hex(sources.dump()) ==
              summary.value("source_freezes_sha256", "");
    }
  }
  const bool validSupersedingBinding =
      !superseding ||
      (validSourceInventory &&
       IsLowerHexSha256(summary.value("source_freezes_sha256", "")) &&
       receipt.value("jobs_per_tune", -1) == jobsPerTune &&
       seal.value("jobs_per_tune", -1) == jobsPerTune &&
       receipt.value("source_freezes_sha256", "") ==
           summary.value("source_freezes_sha256", "") &&
       seal.value("source_freezes_sha256", "") ==
           summary.value("source_freezes_sha256", "") &&
       receipt.value("supersedes", json::object()) ==
           summary.value("supersedes", json::object()) &&
       seal.value("supersedes", json::object()) ==
           summary.value("supersedes", json::object()));
  if ((!firstStage && !superseding) ||
      summary.value("canonical_manifest_sha256", "") != manifestSha ||
      !validShape ||
      summary.value("state", "") !=
          "AWAITING_EXHAUSTIVE_RAW_VALIDATION" ||
      summary.value("campaign", "").empty() ||
      summary.value("campaign_ordinal", -1) < 1 ||
      summary.value("successful_events_per_job", -1) != 1000000 ||
      summary.value("successful_events_per_tune", -1LL) !=
          static_cast<Long64_t>(jobsPerTune) * 1000000LL ||
      summary.value("block_count", -1) != 10 ||
      summary.value("jobs_per_tune_per_block", -1) != jobsPerTune / 10 ||
      receipt.value("schema", "") != receiptSchema ||
      receipt.value("state", "") != "PASS" ||
      receipt.value("canonical_manifest_sha256", "") != manifestSha ||
      receipt.value("canonical_manifest_rows", -1) != expectedRows ||
      receipt.value("validated_raw_files", -1) != expectedRows ||
      receipt.value("validated_successful_events", -1LL) !=
          static_cast<Long64_t>(expectedRows) * 1000000LL ||
      seal.value("schema", "") != sealSchema ||
      seal.value("state", "") != "SEALED" ||
      seal.value("canonical_manifest_sha256", "") != manifestSha ||
      seal.value("validation_receipt_path", "") !=
          "canonical_raw_validation_receipt.json" ||
      seal.value("validation_receipt_sha256", "") != receiptSha ||
      !validSupersedingBinding) {
    throw std::runtime_error(
        "Canonical raw manifest is not bound to the expected sealed PASS "
        "freeze: " + manifestPath);
  }

  RawFileSelection selection;
  selection.mode = DatasetInputMode::kCanonicalManifest;
  selection.source = manifestPath;
  const std::vector<std::string> tunes = TuneNames();
  std::map<std::string, std::set<int>> slots;
  std::map<std::string, std::map<int, int>> blockCounts;
  std::map<std::string, std::map<int, std::string>> pathsBySlot;
  std::map<std::string, std::vector<std::string>> sourceContracts;
  std::map<std::string, std::map<std::string, int>> sourceTuneCounts;
  std::set<std::string> rawPaths;
  std::ifstream input(manifestPath);
  if (!input) {
    throw std::runtime_error(
        "Cannot open canonical manifest: " + manifestPath);
  }
  int rows = 0;
  std::string line;
  while (std::getline(input, line)) {
    if (line.empty()) continue;
    const json row = json::parse(line);
    const std::string tune = row.at("tune").get<std::string>();
    if (std::find(tunes.begin(), tunes.end(), tune) == tunes.end()) {
      throw std::runtime_error(
          "Unknown tune in canonical manifest: " + tune);
    }
    const int slot = row.at("canonical_slot").get<int>();
    const int block = row.at("block").get<int>();
    const std::string rawRelative = row.at("raw_path").get<std::string>();
    const std::string expectedRawSha =
        row.at("raw_sha256").get<std::string>();
    bool validCampaignBinding = false;
    if (firstStage) {
      validCampaignBinding =
          row.value("campaign", "") == summary.value("campaign", "");
    } else {
      const std::string sourceCampaign = row.value("campaign", "");
      const std::vector<std::string> sourceContract = {
          row.value("source_manifest_sha256", ""),
          row.value("source_freeze_summary_sha256", ""),
          row.value("source_freeze_seal_sha256", ""),
      };
      validCampaignBinding =
          !sourceCampaign.empty() &&
          row.value("source_production_prefix", "") == sourceCampaign &&
          row.value("source_canonical_slot", -1) >= 0 &&
          row.value("final_campaign", "") ==
              summary.value("campaign", "") &&
          row.value("final_campaign_ordinal", -1) ==
              summary.value("campaign_ordinal", -1) &&
          std::all_of(
              sourceContract.begin(), sourceContract.end(),
              [](const std::string& value) {
                return IsLowerHexSha256(value);
              });
      const auto known = sourceContracts.find(sourceCampaign);
      if (validCampaignBinding && known == sourceContracts.end()) {
        sourceContracts[sourceCampaign] = sourceContract;
      } else if (validCampaignBinding && known->second != sourceContract) {
        validCampaignBinding = false;
      }
      const auto sealed = sealedSourceContracts.find(sourceCampaign);
      if (validCampaignBinding &&
          (sealed == sealedSourceContracts.end() ||
           sealed->second != sourceContract)) {
        validCampaignBinding = false;
      }
      if (validCampaignBinding) {
        ++sourceTuneCounts[sourceCampaign][tune];
      }
    }
    if (row.at("schema").get<std::string>() != rowSchema ||
        row.at("raw_schema").get<std::string>() !=
            "hf_primary_ground_raw_v7" ||
        row.at("selector").get<std::string>() !=
            "hard_trigger_primary_ground__primary_ground_associate_v1" ||
        row.at("requested_successes").get<int>() != 1000000 ||
        !IsLowerHexSha256(expectedRawSha) ||
        !validCampaignBinding ||
        slot < 0 || slot >= jobsPerTune || block != slot % 10 ||
        !slots[tune].insert(slot).second ||
        !IsSafeRelativePath(rawRelative) ||
        !rawPaths.insert(rawRelative).second) {
      throw std::runtime_error(
          "Invalid or duplicate canonical manifest row");
    }

    const std::string rawPath =
        JoinPath({productionRoot, rawRelative});
    Long_t id = 0;
    Long64_t bytes = 0;
    Long_t flags = 0;
    Long_t modification = 0;
    if (gSystem->GetPathInfo(rawPath.c_str(), &id, &bytes, &flags,
                             &modification) != 0 ||
        bytes <= 0 ||
        bytes != row.at("raw_bytes").get<Long64_t>()) {
      throw std::runtime_error(
          "Canonical raw file is missing or has the wrong size: " +
          rawPath);
    }
    if (Hadronization::Sha256FileHex(rawPath) != expectedRawSha) {
      throw std::runtime_error(
          "Canonical raw file checksum differs from the sealed manifest: " +
          rawPath);
    }
    ++blockCounts[tune][block];
    pathsBySlot[tune][slot] = rawPath;
    ++rows;
  }
  if (rows != expectedRows) {
    throw std::runtime_error(
        "Canonical manifest row count differs from the sealed summary");
  }
  if (superseding && sourceContracts != sealedSourceContracts) {
    throw std::runtime_error(
        "Superseding manifest/source-freeze inventory differs");
  }
  if (superseding) {
    for (const auto& source : sealedSourceExposure) {
      for (const auto& tune : tunes) {
        if (sourceTuneCounts[source.first][tune] != source.second) {
          throw std::runtime_error(
              "Superseding source has unequal or incorrect tune exposure: " +
              source.first);
        }
      }
    }
  }
  for (const std::string& tune : tunes) {
    if (static_cast<int>(slots[tune].size()) != jobsPerTune) {
      throw std::runtime_error(
          "Canonical manifest does not contain the sealed equal exposure for " +
          tune);
    }
    for (int slot = 0; slot < jobsPerTune; ++slot) {
      if (!slots[tune].count(slot) || !pathsBySlot[tune].count(slot)) {
        throw std::runtime_error(
            "Canonical manifest slots are not contiguous for " + tune);
      }
      selection.filesByTune[tune].push_back(pathsBySlot[tune].at(slot));
    }
    for (int block = 0; block < 10; ++block) {
      if (blockCounts[tune][block] != jobsPerTune / 10) {
        throw std::runtime_error(
            "Canonical manifest blocks do not have equal exposure for " +
            tune);
      }
    }
  }
  return selection;
}

RawFileSelection LoadRawFileSelection(const std::string& inputBaseDir,
                                      const std::string& requestedMode,
                                      const std::string& hadronizationBase)
{
  const DatasetInputMode mode = ResolveDatasetInputMode(requestedMode);
  if (mode == DatasetInputMode::kCanonicalManifest) {
    return LoadCanonicalManifestSelection(hadronizationBase);
  }

  RawFileSelection selection;
  selection.mode = DatasetInputMode::kLegacyRecursiveDiagnostic;
  selection.source = inputBaseDir;
  for (const std::string& tune : TuneNames()) {
    CollectRootFiles(
        JoinPath({inputBaseDir, tune}), selection.filesByTune[tune]);
    std::sort(selection.filesByTune[tune].begin(),
              selection.filesByTune[tune].end());
  }
  std::cerr
      << "WARNING: using explicit legacy recursive diagnostic input. "
         "Directory discovery can include reserves or unrelated files and "
         "must never be used for a canonical publication result."
      << std::endl;
  return selection;
}

void EnsureDirectory(const std::string& path)
{
  if (gSystem->mkdir(path.c_str(), true) != 0 && gSystem->AccessPathName(path.c_str())) {
    throw std::runtime_error("Could not create output directory: " + path);
  }
}

double Pi()
{
  return std::acos(-1.0);
}

double WrapToMinusPiPi(double phi)
{
  const double pi = Pi();
  const double twoPi = 2.0 * pi;
  while (phi < -pi) phi += twoPi;
  while (phi >= pi) phi -= twoPi;
  return phi;
}

std::vector<std::string> TuneNames()
{
  return {"MONASH", "JUNCTIONS", "CLOSEPACKING"};
}

std::vector<SpeciesDef> Species()
{
  return {
    {"Bplus", "#it{B}^{+}", 521, true},
    {"Bminus", "#it{B}^{-}", -521, true},
    {"Lambdab", "#Lambda_{b}^{0}", 5122, true},
    {"Lambdabbar", "#bar{#Lambda}_{b}^{0}", -5122, true},
    {"Sigmabzero", "#Sigma_{b}^{0}", 5212, true},
    {"Sigmabzerobar", "#bar{#Sigma}_{b}^{0}", -5212, true},
    {"Dplus", "#it{D}^{+}", 411, true},
    {"Dminus", "#it{D}^{-}", -411, true},
    {"Lambdacplus", "#Lambda_{c}^{+}", 4122, true},
    {"Lambdacplusbar", "#bar{#Lambda}_{c}^{-}", -4122, true},
  };
}

Color_t TuneColor(const std::string& tune)
{
  return HadronizationPlotStyle::TuneColor(tune);
}

int TuneMarker(const std::string& tune)
{
  return HadronizationPlotStyle::TuneMarker(tune);
}

int TuneLineStyle(const std::string& tune)
{
  return HadronizationPlotStyle::TuneLineStyle(tune);
}

const char* MultiplicityDefinitionLine1()
{
  return "pp, #sqrt{s} = 13.6 TeV";
}

const char* MultiplicityDefinitionLine2()
{
  return "#it{p}_{T} > 0.15 GeV/#it{c}";
}

const char* MultiplicityDefinitionLine3()
{
  return "|#eta| #leq 4";
}

const char* MultiplicityAxisTitle()
{
  return "Multiplicity #it{N}_{ch}";
}

const char* MultiplicitySpectrumYTitle(bool normalizeShape)
{
  return normalizeShape ? "Normalized event counts" : "Event counts / bin width";
}

std::vector<MultiplicityPercentileClass> MultiplicityPercentileClasses()
{
  return {
    {90.0, 100.0, "90-100%"},
    {80.0, 90.0, "80-90%"},
    {70.0, 80.0, "70-80%"},
    {60.0, 70.0, "60-70%"},
    {50.0, 60.0, "50-60%"},
    {40.0, 50.0, "40-50%"},
    {30.0, 40.0, "30-40%"},
    {20.0, 30.0, "20-30%"},
    {10.0, 20.0, "10-20%"},
    {1.0, 10.0, "1-10%"},
    {0.0, 1.0, "0-1%"},
  };
}

HistSet BookSpeciesHistograms(const SpeciesDef& species, const std::string& tune)
{
  const std::string prefix = "hInclusive_" + species.key + "_" + tune;
  // Keep the established 0.5 GeV bins in the displayed 0--50 GeV region,
  // then use coarse tail bins so no selected raw-v5 particle is silently
  // discarded from normalization. ROOT upper edges are exclusive, hence the
  // one-ULP extension that includes exactly 7000 GeV.
  std::vector<double> ptEdges;
  for (int index = 0; index <= 100; ++index) {
    ptEdges.push_back(0.5 * static_cast<double>(index));
  }
  for (double edge : {
         60.0, 75.0, 100.0, 150.0, 250.0, 500.0,
         1000.0, 2000.0, 4000.0}) {
    ptEdges.push_back(edge);
  }
  ptEdges.push_back(
    std::nextafter(kInclusivePtConfiguredMaxGeV,
                   std::numeric_limits<double>::infinity()));

  HistSet hists;
  hists.pt = new TH1D((prefix + "_pT").c_str(), "",
                      static_cast<int>(ptEdges.size()) - 1,
                      ptEdges.data());
  // ROOT histogram upper edges are exclusive, and one nextafter step still
  // rounds eta = +4 into overflow in TH1::FindBin. This negligible guard
  // keeps the documented inclusive endpoint visible.
  hists.eta =
    new TH1D((prefix + "_eta").c_str(), "", 100, -4.0, 4.0 + 1.0e-12);
  hists.phi = new TH1D((prefix + "_phi").c_str(), "", 100, -Pi(), Pi());

  for (TH1D* hist : {hists.pt, hists.eta, hists.phi}) {
    hist->SetDirectory(nullptr);
    hist->Sumw2();
  }

  return hists;
}

void DeleteHistSet(HistSet& hists)
{
  delete hists.pt;
  delete hists.eta;
  delete hists.phi;
  hists.pt = nullptr;
  hists.eta = nullptr;
  hists.phi = nullptr;
}

void AddMultiplicityHistogram(TuneData& data, const std::string& filePath,
                              bool strictInputs)
{
  std::unique_ptr<TFile> file(TFile::Open(filePath.c_str(), "READ"));
  if (!file || file->IsZombie()) {
    if (strictInputs) {
      throw std::runtime_error(
          "Could not open multiplicity input: " + filePath);
    }
    return;
  }

  TH1D* source = dynamic_cast<TH1D*>(file->Get("hMULTIPLICITY"));
  if (!source) {
    if (strictInputs) {
      throw std::runtime_error(
          "Missing hMULTIPLICITY in raw input: " + filePath);
    }
    return;
  }

  if (!data.multiplicity) {
    data.multiplicity = dynamic_cast<TH1D*>(source->Clone(("hMultiplicity_" + data.tune).c_str()));
    data.multiplicity->SetDirectory(nullptr);
    data.multiplicity->Reset();
    if (data.multiplicity->GetSumw2N() == 0) data.multiplicity->Sumw2();
  }
  data.multiplicity->Add(source);
}

TuneData BuildTuneSpectra(const std::string& tune,
                          const std::vector<std::string>& selectedFiles,
                          DatasetInputMode datasetMode,
                          bool strictInputs)
{
  const std::vector<std::string>& files = selectedFiles;
  const bool canonical =
      datasetMode == DatasetInputMode::kCanonicalManifest;
  const bool effectiveStrictInputs = strictInputs || canonical;

  if (files.empty()) {
    const std::string message =
        "No selected raw ROOT files found for tune " + tune;
    if (effectiveStrictInputs) throw std::runtime_error(message);
    std::cerr << "WARNING: " << message << std::endl;
  }
  if (canonical &&
      (files.size() < 100 || files.size() % 10 != 0)) {
    throw std::runtime_error(
        "Canonical raw selection must contain at least 100 files and equal "
        "ten-block exposure for " + tune);
  }

  TuneData data;
  data.tune = tune;
  data.nFiles = static_cast<int>(files.size());

  const std::vector<SpeciesDef> speciesDefs = Species();
  std::map<int, std::string> speciesByPdg;
  for (const SpeciesDef& species : speciesDefs) {
    speciesByPdg[species.pdg] = species.key;
    data.spectra[species.key] = BookSpeciesHistograms(species, tune);
  }

  RawInputContract contract;
  if (!files.empty()) {
    contract = InspectRawInputContract(files.front());
    for (size_t index = 1; index < files.size(); ++index) {
      RequireCompatibleContract(
        contract, InspectRawInputContract(files[index]), files[index]);
    }
    const RawInputMode expectedMode =
        canonical ? RawInputMode::kCanonicalV5 : RawInputMode::kLegacy;
    if (contract.mode != expectedMode) {
      throw std::runtime_error(
          std::string("Raw file contract does not match dataset input mode ") +
          DatasetInputModeName(datasetMode) + " for " + tune);
    }
    data.inputContract = RawInputModeName(contract.mode);
    if (contract.mode == RawInputMode::kCanonicalV5) {
      data.inputContract += " (" + contract.schema + ")";
    } else {
      data.inputContract +=
        contract.hasEventWeight ? " (stored event_weight)" : " (unit weights)";
      std::cerr
        << "WARNING: " << tune << " uses " << RawInputModeName(contract.mode)
        << ". Final-state and pT/eta acceptance are assumed to have been "
           "applied by the legacy producer; direct-primary and origin "
           "semantics cannot be reconstructed from these branches. "
        << (contract.hasEventWeight
              ? "The stored event_weight is used."
              : "No event_weight branch exists, so unit weights are used.")
        << std::endl;
    }
  }

  TChain chain("tree");
  for (const std::string& file : files) {
    chain.Add(file.c_str());
    AddMultiplicityHistogram(data, file, effectiveStrictInputs);
  }

  if (files.empty()) return data;

  chain.SetBranchStatus("*", 0);

  Double_t eventWeight = 1.0;
  std::vector<Int_t>* pdg = nullptr;
  std::vector<Int_t>* status = nullptr;
  std::vector<Int_t>* isFinal = nullptr;
  std::vector<Int_t>* central = nullptr;
  std::vector<Double_t>* pt = nullptr;
  std::vector<Double_t>* eta = nullptr;
  std::vector<Double_t>* phi = nullptr;

  if (contract.hasEventWeight) {
    chain.SetBranchStatus("event_weight", 1);
    chain.SetBranchAddress("event_weight", &eventWeight);
  }

  if (contract.mode == RawInputMode::kCanonicalV5) {
    for (const char* branch : {"heavyPdg", "heavyStatus", "heavyIsFinal",
                               "heavyCentral", "heavyPt", "heavyEta",
                               "heavyPhi"}) {
      chain.SetBranchStatus(branch, 1);
    }
    chain.SetBranchAddress("heavyPdg", &pdg);
    chain.SetBranchAddress("heavyStatus", &status);
    chain.SetBranchAddress("heavyIsFinal", &isFinal);
    chain.SetBranchAddress("heavyCentral", &central);
    chain.SetBranchAddress("heavyPt", &pt);
    chain.SetBranchAddress("heavyEta", &eta);
    chain.SetBranchAddress("heavyPhi", &phi);
  } else {
    for (const char* branch : {"ID", "PT", "ETA", "PHI"}) {
      chain.SetBranchStatus(branch, 1);
    }
    chain.SetBranchAddress("ID", &pdg);
    chain.SetBranchAddress("PT", &pt);
    chain.SetBranchAddress("ETA", &eta);
    chain.SetBranchAddress("PHI", &phi);
  }

  const Long64_t nEntries = chain.GetEntries();
  data.nEvents = nEntries;

  for (Long64_t entry = 0; entry < nEntries; ++entry) {
    if ((entry + 1) % 5000000 == 0) {
      std::cout << tune << ": processed " << (entry + 1) << " / " << nEntries << " events\r" << std::flush;
    }

    eventWeight = 1.0;
    if (chain.GetEntry(entry) <= 0 || !pdg || !pt || !eta || !phi) {
      throw std::runtime_error(
        "Could not read required raw vectors for " + tune +
        " at tree entry " + std::to_string(entry));
    }
    if (!std::isfinite(eventWeight)) {
      throw std::runtime_error(
        "Non-finite event_weight for " + tune +
        " at tree entry " + std::to_string(entry));
    }

    const size_t n = pdg->size();
    const bool commonSizesMatch =
      pt->size() == n && eta->size() == n && phi->size() == n;
    const bool canonicalSizesMatch =
      contract.mode != RawInputMode::kCanonicalV5 ||
      (status && isFinal && central && status->size() == n &&
       isFinal->size() == n && central->size() == n);
    if (!commonSizesMatch || !canonicalSizesMatch) {
      throw std::runtime_error(
        "Inconsistent raw-vector lengths for " + tune +
        " at tree entry " + std::to_string(entry));
    }

    for (size_t i = 0; i < n; ++i) {
      const auto found = speciesByPdg.find(pdg->at(i));
      if (found == speciesByPdg.end()) continue;

      const double particlePt = pt->at(i);
      const double particleEta = eta->at(i);
      const double particlePhi = phi->at(i);
      if (!std::isfinite(particlePt) || !std::isfinite(particleEta) ||
          !std::isfinite(particlePhi)) {
        throw std::runtime_error(
          "Non-finite selected-particle kinematics for " + tune +
          " at tree entry " + std::to_string(entry));
      }

      if (contract.mode == RawInputMode::kCanonicalV5 &&
          !PassCanonicalInclusiveSelection(
            status->at(i), isFinal->at(i), central->at(i),
            particlePt, particleEta)) {
        continue;
      }

      HistSet& hists = data.spectra[found->second];
      const int ptBin = hists.pt->FindFixBin(particlePt);
      if (ptBin <= 0 || ptBin > hists.pt->GetNbinsX()) {
        std::ostringstream message;
        message
          << "Selected particle pT histogram overflow for " << tune
          << " at tree entry " << entry
          << ", vector index " << i
          << ": pT=" << particlePt
          << " GeV/c is outside [0, nextafter("
          << kInclusivePtConfiguredMaxGeV
          << ", +inf)). Refuse to truncate a publication spectrum.";
        throw std::runtime_error(message.str());
      }
      hists.pt->Fill(particlePt, eventWeight);
      hists.eta->Fill(particleEta, eventWeight);
      hists.phi->Fill(WrapToMinusPiPi(particlePhi), eventWeight);
      ++data.nSelectedParticles;
      data.selectedParticleWeight += eventWeight;
    }
  }
  if (nEntries >= 5000000) std::cout << std::string(80, ' ') << "\r" << std::flush;

  return data;
}

TuneData BuildTuneMultiplicityOnly(const std::string& tune,
                                   const std::vector<std::string>& selectedFiles,
                                   DatasetInputMode datasetMode,
                                   bool strictInputs)
{
  const std::vector<std::string>& files = selectedFiles;
  const bool canonical =
      datasetMode == DatasetInputMode::kCanonicalManifest;
  const bool effectiveStrictInputs = strictInputs || canonical;

  if (files.empty()) {
    const std::string message =
        "No selected raw ROOT files found for tune " + tune;
    if (effectiveStrictInputs) throw std::runtime_error(message);
    std::cerr << "WARNING: " << message << std::endl;
  }
  if (canonical &&
      (files.size() < 100 || files.size() % 10 != 0)) {
    throw std::runtime_error(
        "Canonical raw selection must contain at least 100 files and equal "
        "ten-block exposure for " + tune);
  }

  TuneData data;
  data.tune = tune;
  data.nFiles = static_cast<int>(files.size());

  if (!files.empty()) {
    const RawInputContract first = InspectRawInputContract(files.front());
    const RawInputMode expectedMode =
        canonical ? RawInputMode::kCanonicalV5 : RawInputMode::kLegacy;
    if (first.mode != expectedMode) {
      throw std::runtime_error(
          std::string("Raw file contract does not match dataset input mode ") +
          DatasetInputModeName(datasetMode) + " for " + tune);
    }
    for (size_t index = 1; index < files.size(); ++index) {
      const RawInputContract observed =
          InspectRawInputContract(files[index]);
      RequireCompatibleContract(first, observed, files[index]);
      if (observed.mode != expectedMode) {
        throw std::runtime_error(
            "Raw file contract changes within selected multiplicity input");
      }
    }
  }
  for (const std::string& file : files) {
    AddMultiplicityHistogram(data, file, effectiveStrictInputs);
  }
  data.nEvents = data.multiplicity
                   ? static_cast<Long64_t>(std::llround(data.multiplicity->GetEntries()))
                   : 0;

  return data;
}

void NormalizeShape(TH1D* hist)
{
  if (!hist) return;
  PlotErrorUtils::NormalizeToUnitShape(hist);
}

void ApplyBinWidthNormalization(TH1D* hist)
{
  if (!hist) return;
  if (hist->GetSumw2N() == 0) hist->Sumw2();
  for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
    const double width = hist->GetBinWidth(bin);
    if (width <= 0.0) continue;
    hist->SetBinContent(bin, hist->GetBinContent(bin) / width);
    hist->SetBinError(bin, hist->GetBinError(bin) / width);
  }
}

TH1D* CloneForPlot(TH1D* source,
                   const std::string& name,
                   const std::string& tune,
                   const std::string& xTitle,
                   bool normalizeShape)
{
  if (!source) return nullptr;
  TH1D* hist = dynamic_cast<TH1D*>(source->Clone(name.c_str()));
  if (!hist) return nullptr;
  hist->SetDirectory(nullptr);
  hist->SetStats(0);
  hist->SetTitle("");
  hist->SetLineColor(TuneColor(tune));
  hist->SetMarkerColor(TuneColor(tune));
  hist->SetMarkerStyle(TuneMarker(tune));
  hist->SetLineStyle(TuneLineStyle(tune));
  hist->SetLineWidth(2);
  hist->SetMarkerSize(0.9);
  hist->GetXaxis()->SetTitle(xTitle.c_str());
  hist->GetYaxis()->SetTitle(normalizeShape ? "Normalized entries" : "Counts / bin width");
  hist->GetXaxis()->SetTitleOffset(1.08);
  hist->GetYaxis()->SetTitleOffset(1.52);
  hist->GetXaxis()->SetTitleSize(0.045);
  hist->GetYaxis()->SetTitleSize(0.045);
  hist->GetXaxis()->SetLabelSize(0.040);
  hist->GetYaxis()->SetLabelSize(0.040);

  if (normalizeShape) NormalizeShape(hist);
  else ApplyBinWidthNormalization(hist);

  return hist;
}

TH1D* BuildRatioHistogram(TH1D* numerator,
                          TH1D* denominator,
                          const std::string& name,
                          const std::string& tune)
{
  if (!numerator || !denominator) return nullptr;

  TH1D* ratio = dynamic_cast<TH1D*>(numerator->Clone(name.c_str()));
  if (!ratio) return nullptr;
  ratio->SetDirectory(nullptr);
  ratio->Reset();
  ratio->SetStats(0);
  ratio->SetTitle("");
  ratio->SetLineColor(TuneColor(tune));
  ratio->SetMarkerColor(TuneColor(tune));
  ratio->SetMarkerStyle(TuneMarker(tune));
  ratio->SetLineStyle(TuneLineStyle(tune));
  ratio->SetLineWidth(2);
  ratio->SetMarkerSize(0.75);
  ratio->GetXaxis()->SetTitle(MultiplicityAxisTitle());
  ratio->GetYaxis()->SetTitle("Tune / MONASH");
  ratio->GetXaxis()->SetRangeUser(0.0, kMultiplicityXMax);

  const int nBins = std::min(numerator->GetNbinsX(), denominator->GetNbinsX());
  for (int bin = 1; bin <= nBins; ++bin) {
    const double num = numerator->GetBinContent(bin);
    const double den = denominator->GetBinContent(bin);
    if (num <= 0.0 || den <= 0.0) continue;

    const double value = num / den;
    const double numErr = numerator->GetBinError(bin);
    const double denErr = denominator->GetBinError(bin);
    const double relErr2 =
      (numErr > 0.0 ? (numErr / num) * (numErr / num) : 0.0) +
      (denErr > 0.0 ? (denErr / den) * (denErr / den) : 0.0);
    ratio->SetBinContent(bin, value);
    ratio->SetBinError(bin, value * std::sqrt(relErr2));
  }

  return ratio;
}

double MaximumWithErrors(const std::vector<TH1D*>& hists)
{
  double maximum = 0.0;
  for (TH1D* hist : hists) {
    if (!hist) continue;
    const int first = std::max(1, hist->GetXaxis()->GetFirst());
    const int last =
      std::min(hist->GetNbinsX(), hist->GetXaxis()->GetLast());
    for (int bin = first; bin <= last; ++bin) {
      maximum = std::max(maximum, hist->GetBinContent(bin) + hist->GetBinError(bin));
    }
  }
  return maximum > 0.0 ? maximum : 1.0;
}

double PositiveMinimum(const std::vector<TH1D*>& hists)
{
  double minimum = 1.0e30;
  for (TH1D* hist : hists) {
    if (!hist) continue;
    const int first = std::max(1, hist->GetXaxis()->GetFirst());
    const int last =
      std::min(hist->GetNbinsX(), hist->GetXaxis()->GetLast());
    for (int bin = first; bin <= last; ++bin) {
      const double content = hist->GetBinContent(bin);
      if (content > 0.0 && content < minimum) minimum = content;
    }
  }
  return minimum < 1.0e30 ? minimum : 1.0e-12;
}

void ApplyMultiplicityAxisLabels(TH1D* hist, bool normalizeShape)
{
  if (!hist) return;
  hist->GetXaxis()->SetTitle(MultiplicityAxisTitle());
  hist->GetYaxis()->SetTitle(MultiplicitySpectrumYTitle(normalizeShape));
}

void ApplyPiLabels(TH1D* hist)
{
  if (!hist) return;
  TAxis* axis = hist->GetXaxis();
  axis->SetNdivisions(4, false);
  axis->ChangeLabel(1, -1, -1, -1, -1, -1, "-#pi");
  axis->ChangeLabel(2, -1, -1, -1, -1, -1, "-#pi/2");
  axis->ChangeLabel(3, -1, -1, -1, -1, -1, "0");
  axis->ChangeLabel(4, -1, -1, -1, -1, -1, "#pi/2");
  axis->ChangeLabel(5, -1, -1, -1, -1, -1, "#pi");
}

void DrawSimulationInfoBlock(double x, double y, double headerSize, double bodySize)
{
  TLatex text;
  text.SetNDC();
  text.SetTextAlign(13);
  text.SetTextFont(62);
  text.SetTextSize(headerSize);
  text.DrawLatex(x, y, "PYTHIA 8");

  text.SetTextFont(42);
  text.SetTextSize(bodySize);
  const double spacing = 0.043;
  text.DrawLatex(x, y - spacing, MultiplicityDefinitionLine1());
  text.DrawLatex(x, y - 2.0 * spacing, MultiplicityDefinitionLine2());
  text.DrawLatex(x, y - 3.0 * spacing, MultiplicityDefinitionLine3());
}

double CalculateMultiplicityThreshold(TH1D* hist, double percentile)
{
  if (!hist) return 1.0;

  const double total = hist->Integral(1, hist->GetNbinsX());
  if (total <= 0.0) return hist->GetBinCenter(1);

  const double target = ((100.0 - percentile) / 100.0) * total;
  double running = 0.0;
  for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
    running += hist->GetBinContent(bin);
    if (running >= target) return hist->GetBinCenter(bin);
  }

  return hist->GetBinCenter(hist->GetNbinsX());
}

std::map<double, double> MultiplicityThresholds(TH1D* hist)
{
  std::map<double, double> thresholds;
  for (double percentile : {0.0, 1.0, 10.0, 20.0, 30.0, 40.0, 50.0,
                            60.0, 70.0, 80.0, 90.0, 100.0}) {
    thresholds[percentile] = CalculateMultiplicityThreshold(hist, percentile);
  }
  return thresholds;
}

void DrawMonashPercentileInset(TH1D* monash,
                               const std::string& outputStem,
                               std::vector<TH1D*>& keepAlive,
                               bool normalizeShape)
{
  if (!monash) return;

  TPad* inset = new TPad(("pMonashPercentiles_" + outputStem).c_str(),
                         "MONASH multiplicity percentile boundaries",
                         0.18, 0.07, 0.58, 0.43);
  inset->SetFillColor(kWhite);
  inset->SetFillStyle(1001);
  inset->SetFrameFillColor(kWhite);
  inset->SetFrameLineWidth(1);
  inset->SetTicks(1, 1);
  inset->SetLogx();
  inset->SetLogy();
  inset->SetTopMargin(0.12);
  inset->SetBottomMargin(0.25);
  inset->SetLeftMargin(0.18);
  inset->SetRightMargin(0.065);
  inset->Draw();
  inset->cd();

  TH1D* insetHist = dynamic_cast<TH1D*>(monash->Clone(("hMonashPercentileInset_" + outputStem).c_str()));
  if (!insetHist) return;
  keepAlive.push_back(insetHist);
  insetHist->SetDirectory(nullptr);
  insetHist->SetStats(0);
  insetHist->SetTitle("");
  insetHist->SetLineColor(kBlack);
  insetHist->SetLineWidth(2);
  insetHist->SetMarkerSize(0.0);

  const double xMin = 1.0;
  const double xMax = kMultiplicityXMax;
  const double yMin = std::max(PositiveMinimum({insetHist}) * 0.5, 1.0e-10);
  const double yMax = std::max(insetHist->GetMaximum() * 3.0, yMin * 10.0);
  insetHist->SetMinimum(yMin);
  insetHist->SetMaximum(yMax);
  insetHist->GetXaxis()->SetRangeUser(xMin, xMax);
  insetHist->GetXaxis()->SetTitle(MultiplicityAxisTitle());
  insetHist->GetYaxis()->SetTitle(MultiplicitySpectrumYTitle(normalizeShape));
  insetHist->GetXaxis()->SetTitleSize(0.062);
  insetHist->GetXaxis()->SetTitleOffset(1.02);
  insetHist->GetYaxis()->SetTitleSize(0.060);
  insetHist->GetYaxis()->SetTitleOffset(1.05);
  insetHist->GetXaxis()->SetLabelSize(0.055);
  insetHist->GetYaxis()->SetLabelSize(0.055);
  insetHist->GetYaxis()->SetNdivisions(503);
  insetHist->Draw("HIST");

  const auto thresholds = MultiplicityThresholds(insetHist);
  for (const auto& item : thresholds) {
    const double x = item.second;
    if (x < xMin || x > xMax) continue;
    TLine* line = new TLine(x, yMin, x, yMax);
    line->SetLineColor(kGray + 2);
    line->SetLineStyle(2);
    line->SetLineWidth(1);
    line->Draw("same");
  }
  insetHist->Draw("HIST SAME");

  TLatex label;
  label.SetTextFont(42);
  label.SetTextSize(0.044);
  label.SetTextAlign(22);
  label.SetTextAngle(90);
  const double yLabel = yMin * std::pow(yMax / yMin, 0.34);
  for (const auto& activityClass : MultiplicityPercentileClasses()) {
    const double left = thresholds.count(activityClass.maxPercentile) ? thresholds.at(activityClass.maxPercentile) : xMin;
    const double right = thresholds.count(activityClass.minPercentile) ? thresholds.at(activityClass.minPercentile) : xMax;
    if (right < xMin || left > xMax) continue;
    const double xLabel = std::sqrt(std::max(left, xMin) * std::min(right, xMax));
    label.DrawLatex(xLabel, yLabel, activityClass.label);
  }

  TLatex title;
  title.SetNDC();
  title.SetTextFont(62);
  title.SetTextSize(0.054);
  title.SetTextAlign(13);
  title.DrawLatex(0.02, 0.965, "MONASH percentile boundaries");
  inset->RedrawAxis();
}

void DrawMultiplicityOverlayWithRatio(const std::vector<TH1D*>& hists,
                                      const std::vector<std::string>& tunes,
                                      const std::string& outputDir,
                                      const std::string& outputStem,
                                      bool normalizeShape,
                                      bool logY)
{
  (void)normalizeShape;

  TCanvas* canvas = new TCanvas(("c_" + outputStem).c_str(), outputStem.c_str(), 1800, 1650);

  TPad* mainPad = new TPad(("pMain_" + outputStem).c_str(), "multiplicity spectrum", 0.0, 0.31, 1.0, 1.0);
  mainPad->SetTicks(1, 1);
  mainPad->SetLeftMargin(0.16);
  mainPad->SetRightMargin(0.045);
  mainPad->SetTopMargin(0.12);
  mainPad->SetBottomMargin(0.025);
  if (logY) mainPad->SetLogy();
  mainPad->Draw();

  TPad* ratioPad = new TPad(("pRatio_" + outputStem).c_str(), "tune ratios", 0.0, 0.0, 1.0, 0.31);
  ratioPad->SetTicks(1, 1);
  ratioPad->SetLeftMargin(0.16);
  ratioPad->SetRightMargin(0.045);
  ratioPad->SetTopMargin(0.035);
  ratioPad->SetBottomMargin(0.34);
  ratioPad->Draw();

  mainPad->cd();
  TH1D* monash = nullptr;
  for (size_t i = 0; i < tunes.size(); ++i) {
    if (tunes[i] == "MONASH") {
      monash = hists[i];
      break;
    }
  }
  std::vector<TH1D*> insetKeepAlive;

  if (!hists.empty()) {
    const double maxY = MaximumWithErrors(hists);
    const double minY = logY ? std::max(PositiveMinimum(hists) * 0.35, 1.0e-12) : 0.0;
    const double upper = logY ? maxY * 8.0 : maxY * 1.28;

    TLegend* legend = new TLegend(0.735, 0.685, 0.925, 0.815);
    legend->SetBorderSize(0);
    legend->SetFillStyle(0);
    legend->SetTextFont(42);
    legend->SetTextSize(0.034);

    for (size_t i = 0; i < hists.size(); ++i) {
      hists[i]->SetMinimum(minY);
      hists[i]->SetMaximum(std::max(upper, minY * 10.0));
      hists[i]->GetXaxis()->SetRangeUser(0.0, kMultiplicityXMax);
      hists[i]->GetXaxis()->SetLabelSize(0.0);
      hists[i]->GetXaxis()->SetTitleSize(0.0);
      hists[i]->Draw(i == 0 ? "E1 HIST" : "E1 HIST SAME");
      legend->AddEntry(hists[i], tunes[i].c_str(), "lp");
    }
    legend->Draw();
    DrawSimulationInfoBlock(0.57, 0.805, 0.032, 0.030);
    DrawMonashPercentileInset(monash, outputStem, insetKeepAlive, normalizeShape);
    mainPad->cd();

  } else {
    TLatex latex;
    latex.SetNDC();
    latex.SetTextAlign(22);
    latex.SetTextSize(0.04);
    latex.DrawLatex(0.50, 0.50, "No input histograms found");
  }

  ratioPad->cd();
  std::vector<TH1D*> ratios;

  for (size_t i = 0; i < tunes.size(); ++i) {
    if (tunes[i] == "MONASH") continue;
    TH1D* ratio = BuildRatioHistogram(hists[i], monash, "hRatio_" + outputStem + "_" + tunes[i], tunes[i]);
    if (ratio) ratios.push_back(ratio);
  }

  if (!ratios.empty()) {
    for (size_t i = 0; i < ratios.size(); ++i) {
      ratios[i]->SetMinimum(kMultiplicityRatioYMin);
      ratios[i]->SetMaximum(kMultiplicityRatioYMax);
      ratios[i]->GetXaxis()->SetTitleSize(0.105);
      ratios[i]->GetXaxis()->SetLabelSize(0.090);
      ratios[i]->GetXaxis()->SetTitleOffset(1.02);
      ratios[i]->GetYaxis()->SetTitleSize(0.090);
      ratios[i]->GetYaxis()->SetLabelSize(0.075);
      ratios[i]->GetYaxis()->SetTitleOffset(0.70);
      ratios[i]->GetYaxis()->SetNdivisions(505);
      ratios[i]->Draw(i == 0 ? "E1 HIST" : "E1 HIST SAME");
    }

    TLine* unity = new TLine(0.0, 1.0, kMultiplicityXMax, 1.0);
    unity->SetLineColor(kGray + 2);
    unity->SetLineStyle(2);
    unity->SetLineWidth(1);
    unity->Draw("same");
    for (TH1D* ratio : ratios) ratio->Draw("E1 HIST SAME");
    ratioPad->RedrawAxis();
  }

  canvas->cd();
  const std::string outBase = JoinPath({outputDir, outputStem});
  canvas->SaveAs((outBase + ".png").c_str());
  canvas->SaveAs((outBase + ".pdf").c_str());
  canvas->SaveAs((outBase + ".C").c_str());

  delete canvas;
  for (TH1D* hist : insetKeepAlive) delete hist;
  for (TH1D* ratio : ratios) delete ratio;
}

void DrawOverlay(const std::vector<TuneData>& tuneData,
                 const SpeciesDef* species,
                 const std::string& variable,
                 const std::string& xTitle,
                 const std::string& outputDir,
                 const std::string& outputStem,
                 bool normalizeShape,
                 bool logY)
{
  std::vector<TH1D*> hists;
  std::vector<std::string> tunes;

  for (const TuneData& data : tuneData) {
    TH1D* source = nullptr;
    if (!species) {
      source = data.multiplicity;
    } else {
      const auto found = data.spectra.find(species->key);
      if (found == data.spectra.end()) continue;
      if (variable == "pT") source = found->second.pt;
      else if (variable == "eta") source = found->second.eta;
      else if (variable == "phi") source = found->second.phi;
    }

    TH1D* hist = CloneForPlot(source,
                              "hPlot_" + outputStem + "_" + data.tune,
                              data.tune,
                              xTitle,
                              normalizeShape);
    if (!hist) continue;
    if (variable == "phi") ApplyPiLabels(hist);
    if (variable == "pT") {
      hist->GetXaxis()->SetRangeUser(
        0.0,
        std::nextafter(kInclusivePtDisplayMaxGeV, 0.0));
    }
    hists.push_back(hist);
    tunes.push_back(data.tune);
  }

  EnsureDirectory(outputDir);

  const bool isMultiplicity = (!species && variable == "multiplicity");
  if (isMultiplicity) {
    for (TH1D* hist : hists) ApplyMultiplicityAxisLabels(hist, normalizeShape);
    DrawMultiplicityOverlayWithRatio(hists, tunes, outputDir, outputStem, normalizeShape, logY);
    for (TH1D* hist : hists) delete hist;
    return;
  }

  TCanvas* canvas = new TCanvas(("c_" + outputStem).c_str(), outputStem.c_str(), 860, 680);
  canvas->SetTicks(1, 1);
  canvas->SetLeftMargin(0.16);
  canvas->SetRightMargin(0.045);
  canvas->SetBottomMargin(0.14);
  canvas->SetTopMargin(0.13);
  if (logY) canvas->SetLogy();

  if (!hists.empty()) {
    const double maxY = MaximumWithErrors(hists);
    const double minY = logY ? std::max(PositiveMinimum(hists) * 0.35, 1.0e-12) : 0.0;
    const double upper = logY ? maxY * 8.0 : maxY * 1.28;

    TLegend* legend = new TLegend(0.62, 0.705, 0.91, 0.855);
    legend->SetBorderSize(0);
    legend->SetFillStyle(0);
    legend->SetTextSize(0.035);

    for (size_t i = 0; i < hists.size(); ++i) {
      hists[i]->SetMinimum(minY);
      hists[i]->SetMaximum(std::max(upper, minY * 10.0));
      hists[i]->Draw(i == 0 ? "E1 HIST" : "E1 HIST SAME");
      legend->AddEntry(hists[i], tunes[i].c_str(), "lp");
    }
    legend->Draw();

    TLatex title;
    title.SetNDC();
    title.SetTextAlign(13);
    title.SetTextSize(0.034);
    if (species) title.DrawLatex(0.16, 0.965, ("Inclusive generated " + species->label).c_str());
    else title.DrawLatex(0.16, 0.965, "Shared event multiplicity");
  } else {
    TLatex latex;
    latex.SetNDC();
    latex.SetTextAlign(22);
    latex.SetTextSize(0.04);
    latex.DrawLatex(0.50, 0.50, "No input histograms found");
  }

  const std::string outBase = JoinPath({outputDir, outputStem});
  canvas->SaveAs((outBase + ".png").c_str());
  canvas->SaveAs((outBase + ".pdf").c_str());
  canvas->SaveAs((outBase + ".C").c_str());

  delete canvas;
  for (TH1D* hist : hists) delete hist;
}

void SetPlotStyle()
{
  gStyle->SetOptStat(0);
  gStyle->SetTitleFont(42, "XYZ");
  gStyle->SetLabelFont(42, "XYZ");
  gStyle->SetTitleSize(0.045, "XYZ");
  gStyle->SetLabelSize(0.040, "XYZ");
  gStyle->SetLegendBorderSize(0);
  gStyle->SetErrorX(0.0);
}

void DeleteTuneData(std::vector<TuneData>& tuneData)
{
  for (TuneData& data : tuneData) {
    delete data.multiplicity;
    data.multiplicity = nullptr;
    for (auto& item : data.spectra) DeleteHistSet(item.second);
  }
}

} // namespace InclusiveRawKinematics

void Plot_InclusiveKinematicSpectra_Raw(const char* inputBaseDir = "RootFiles/HF",
                                        const char* outputDir = "PlottingScripts/Plots/KinematicSpectra",
                                        bool normalizeShape = true,
                                        bool strictInputs = true,
                                        const char* inputMode = "selector")
{
  using namespace InclusiveRawKinematics;

  SetPlotStyle();

  const std::string base = FindHadronizationBase();
  const std::string resolvedInput = ResolveFromBase(inputBaseDir ? inputBaseDir : "RootFiles/HF", base);
  const std::string resolvedOutput =
    ResolveFromBase(outputDir ? outputDir : "PlottingScripts/Plots/KinematicSpectra", base);
  const RawFileSelection selection = LoadRawFileSelection(
      resolvedInput, inputMode ? inputMode : "selector", base);
  const std::string suffix = normalizeShape ? "shape" : "density";

  std::cout << "Inclusive raw kinematic spectra\n";
  std::cout << "================================\n";
  std::cout << "Input base: " << resolvedInput << "\n";
  std::cout << "Input mode: " << DatasetInputModeName(selection.mode) << "\n";
  std::cout << "Input selection source: " << selection.source << "\n";
  std::cout << "Output dir: " << resolvedOutput << "\n";
  std::cout << "Canonical selection: exact PDG ID, final, direct-primary, "
               "central-registry ground state\n";
  std::cout << "Inclusive acceptance: pT > 0.15 GeV/c and |eta| <= 4\n";
  std::cout << "Origin policy: inclusive (no selected-hard-origin requirement); "
               "no pair conditioning\n";
  std::cout << "pT histogram: 0--7000 GeV/c (exact 7000 retained; true "
               "overflow is fatal), displayed through 50 GeV/c\n";
  std::cout << "Weights: stored event_weight for canonical raw-v5 inputs\n\n";

  std::vector<TuneData> tuneData;
  for (const std::string& tune : TuneNames()) {
    TuneData data = BuildTuneSpectra(
        tune, selection.filesByTune.at(tune), selection.mode, strictInputs);
    std::cout << tune
              << ": files=" << data.nFiles
              << " tree entries=" << data.nEvents
              << " selected particles=" << data.nSelectedParticles
              << " selected weighted sum=" << data.selectedParticleWeight
              << " input=" << data.inputContract;
    if (data.multiplicity) {
      std::cout << " multiplicity entries=" << static_cast<Long64_t>(std::llround(data.multiplicity->GetEntries()));
    }
    std::cout << "\n";
    tuneData.push_back(data);
  }
  std::cout << "\n";

  DrawOverlay(tuneData,
              nullptr,
              "multiplicity",
              MultiplicityAxisTitle(),
              JoinPath({resolvedOutput, "Multiplicity"}),
              "MultiplicitySpectrum_Shared_" + suffix,
              normalizeShape,
              true);

  const std::vector<SpeciesDef> speciesDefs = Species();
  for (const SpeciesDef& species : speciesDefs) {
    DrawOverlay(tuneData,
                &species,
                "pT",
                "#it{p}_{T} (GeV/#it{c})",
                JoinPath({resolvedOutput, "Inclusive", "pT"}),
                "Inclusive_pT_" + species.key + "_" + suffix,
                normalizeShape,
                species.logPt);
    DrawOverlay(tuneData,
                &species,
                "eta",
                "#eta",
                JoinPath({resolvedOutput, "Inclusive", "eta"}),
                "Inclusive_eta_" + species.key + "_" + suffix,
                normalizeShape,
                false);
    DrawOverlay(tuneData,
                &species,
                "phi",
                "#phi",
                JoinPath({resolvedOutput, "Inclusive", "phi"}),
                "Inclusive_phi_" + species.key + "_" + suffix,
                normalizeShape,
                false);
  }

  DeleteTuneData(tuneData);
}

void Plot_InclusiveMultiplicitySpectrum_Raw(const char* inputBaseDir = "RootFiles/HF",
                                            const char* outputDir = "PlottingScripts/Plots/KinematicSpectra",
                                            bool normalizeShape = true,
                                            bool strictInputs = true,
                                            const char* inputMode = "selector")
{
  using namespace InclusiveRawKinematics;

  SetPlotStyle();

  const std::string base = FindHadronizationBase();
  const std::string resolvedInput = ResolveFromBase(inputBaseDir ? inputBaseDir : "RootFiles/HF", base);
  const std::string resolvedOutput =
    ResolveFromBase(outputDir ? outputDir : "PlottingScripts/Plots/KinematicSpectra", base);
  const RawFileSelection selection = LoadRawFileSelection(
      resolvedInput, inputMode ? inputMode : "selector", base);
  const std::string suffix = normalizeShape ? "shape" : "density";

  std::cout << "Inclusive raw multiplicity spectrum\n";
  std::cout << "===================================\n";
  std::cout << "Input base: " << resolvedInput << "\n";
  std::cout << "Input mode: " << DatasetInputModeName(selection.mode) << "\n";
  std::cout << "Input selection source: " << selection.source << "\n";
  std::cout << "Output dir: " << resolvedOutput << "\n";
  std::cout << "Nch definition: status-81--89 charged e/mu/pi/K/p, pT >= 0.15 GeV/c, |eta| <= 4 (not prompt multiplicity)\n";
  std::cout << "pp sqrt(s)=13.6 TeV\n\n";

  std::vector<TuneData> tuneData;
  for (const std::string& tune : TuneNames()) {
    TuneData data = BuildTuneMultiplicityOnly(
        tune, selection.filesByTune.at(tune), selection.mode, strictInputs);
    std::cout << tune
              << ": files=" << data.nFiles
              << " multiplicity entries=" << data.nEvents
              << "\n";
    tuneData.push_back(data);
  }
  std::cout << "\n";

  DrawOverlay(tuneData,
              nullptr,
              "multiplicity",
              MultiplicityAxisTitle(),
              JoinPath({resolvedOutput, "Multiplicity"}),
              "MultiplicitySpectrum_Shared_" + suffix,
              normalizeShape,
              true);

  DeleteTuneData(tuneData);
}

int TestInclusiveRawCanonicalManifestSelection(
    const char* manifestPath,
    const char* productionRoot,
    int expectedFilesPerTune = 110)
{
  using namespace InclusiveRawKinematics;

  const std::string oldStatus =
      EnvironmentValue("HADRONIZATION_DATASET_STATUS");
  const std::string oldEligible =
      EnvironmentValue("HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE");
  const std::string oldManifest =
      EnvironmentValue("HADRONIZATION_CANONICAL_MANIFEST");
  const std::string oldProduction =
      EnvironmentValue("HADRONIZATION_PRODUCTION_ROOT");
  const bool hadStatus = std::getenv("HADRONIZATION_DATASET_STATUS");
  const bool hadEligible =
      std::getenv("HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE");
  const bool hadManifest =
      std::getenv("HADRONIZATION_CANONICAL_MANIFEST");
  const bool hadProduction =
      std::getenv("HADRONIZATION_PRODUCTION_ROOT");
  auto restore = [&]() {
    if (hadStatus) {
      gSystem->Setenv("HADRONIZATION_DATASET_STATUS", oldStatus.c_str());
    } else {
      gSystem->Unsetenv("HADRONIZATION_DATASET_STATUS");
    }
    if (hadEligible) {
      gSystem->Setenv(
          "HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE",
          oldEligible.c_str());
    } else {
      gSystem->Unsetenv(
          "HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE");
    }
    if (hadManifest) {
      gSystem->Setenv(
          "HADRONIZATION_CANONICAL_MANIFEST", oldManifest.c_str());
    } else {
      gSystem->Unsetenv("HADRONIZATION_CANONICAL_MANIFEST");
    }
    if (hadProduction) {
      gSystem->Setenv(
          "HADRONIZATION_PRODUCTION_ROOT", oldProduction.c_str());
    } else {
      gSystem->Unsetenv("HADRONIZATION_PRODUCTION_ROOT");
    }
  };

  int errors = 0;
  try {
    gSystem->Setenv("HADRONIZATION_DATASET_STATUS", "canonical");
    gSystem->Setenv(
        "HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE", "true");
    gSystem->Setenv("HADRONIZATION_CANONICAL_MANIFEST", manifestPath);
    gSystem->Setenv("HADRONIZATION_PRODUCTION_ROOT", productionRoot);
    const RawFileSelection selection =
        LoadRawFileSelection("", "selector", FindHadronizationBase());
    if (selection.mode != DatasetInputMode::kCanonicalManifest) ++errors;
    for (const std::string& tune : TuneNames()) {
      const auto found = selection.filesByTune.find(tune);
      if (found == selection.filesByTune.end() ||
          static_cast<int>(found->second.size()) != expectedFilesPerTune) {
        ++errors;
      }
      if (found != selection.filesByTune.end() &&
          std::any_of(
              found->second.begin(), found->second.end(),
              [](const std::string& path) {
                return path.find("reserve") != std::string::npos;
              })) {
        ++errors;
      }
    }
    if (ResolveDatasetInputMode("legacy_recursive_diagnostic") !=
        DatasetInputMode::kLegacyRecursiveDiagnostic) {
      ++errors;
    }
  } catch (const std::exception& error) {
    std::cerr << "INCLUSIVE_RAW_DATASET_SELECTION_TEST_ERROR "
              << error.what() << std::endl;
    ++errors;
  }
  restore();
  std::cout
      << "INCLUSIVE_RAW_DATASET_SELECTION_TEST "
      << "errors=" << errors
      << " files_per_tune=" << expectedFilesPerTune
      << " reserve_discovery=false"
      << std::endl;
  return errors;
}

int TestInclusiveRawTuneStylePreservation()
{
  using namespace InclusiveRawKinematics;

  TH1D source("hInclusiveStyleSource", "", 2, 0.0, 2.0);
  source.Sumw2();
  source.SetBinContent(1, 2.0);
  source.SetBinError(1, 0.2);
  TH1D denominator("hInclusiveStyleDenominator", "", 2, 0.0, 2.0);
  denominator.Sumw2();
  denominator.SetBinContent(1, 1.0);
  denominator.SetBinError(1, 0.1);

  int errors = 0;
  for (const std::string& tune :
       std::vector<std::string>{"MONASH", "JUNCTIONS", "CLOSEPACKING"}) {
    TH1D* styled = CloneForPlot(
        &source, "hInclusiveStyle_" + tune, tune, "x", false);
    TH1D* ratio = BuildRatioHistogram(
        &source, &denominator, "hInclusiveRatioStyle_" + tune, tune);
    for (TH1D* histogram : {styled, ratio}) {
      if (!histogram ||
          histogram->GetLineColor() != TuneColor(tune) ||
          histogram->GetMarkerColor() != TuneColor(tune) ||
          histogram->GetMarkerStyle() != TuneMarker(tune) ||
          histogram->GetLineStyle() != TuneLineStyle(tune)) {
        ++errors;
      }
    }
    delete styled;
    delete ratio;
  }
  std::cout << "INCLUSIVE_RAW_TUNE_STYLE_TEST errors=" << errors
            << " monash_line=1 junctions_line=2 closepacking_line=7"
            << std::endl;
  return errors;
}
