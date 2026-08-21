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
//   .L plotting/Plot_InclusiveKinematicSpectra_Raw.C+
//   Plot_InclusiveKinematicSpectra_Raw("RootFiles/HF",
//                                      "plotting/Plots/KinematicSpectra",
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

#include "CommonMultiplicityBoundaries.h"
#include "GeneratedClassLabelPrecision.h"
#include "HistogramErrorUtils.h"
#include "TunePlotStyle.h"
#include "../generation/registries/GeneratedHeavyFlavourRegistry.h"
#include "../generation/producer/HeavyFlavourUtils.h"
#include "../generation/producer/Sha256.h"

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
  if (envBase && !gSystem->AccessPathName(JoinPath({envBase, "plotting"}).c_str())) {
    return ExpandPath(envBase);
  }

  std::string current = ExpandPath(gSystem->WorkingDirectory());
  while (!current.empty() && current != "/") {
    if (!gSystem->AccessPathName(JoinPath({current, "plotting"}).c_str())) {
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

// ---------------------------------------------------------------------------
// The canonical-freeze contract derives campaign shape from the manifest.
// It supports both 100-by-1,000,000 and 1,000-by-100,000 event decompositions.
//
// A sealed freeze contains these artifacts:
//
//   REQUIRED   canonical_manifest.jsonl   the rows, one per promoted raw file
//   REQUIRED   freeze_seal.json           the seal, cross-checked against them
//   PER ROW    raw_sha256, raw_validation_receipt_path/_sha256,
//              raw_validation_log_path/_sha256, attempt_receipt_path
//   OPTIONAL   canonical_raw_validation.log, verified against the derived
//              shape IF PRESENT -- absent is "not claimed", never "passed"
//
// Each row names its raw validation receipt and digest.
// The code derives tunes, job counts, event counts, and block width from the rows.
// It rejects absent seals, digest drift, unequal exposure, incomplete blocks, and duplicate slots.
// ---------------------------------------------------------------------------

struct DerivedFreezeShape {
  std::vector<std::string> tunes;
  int jobsPerTune = 0;
  long long eventsPerJob = 0;
  int rows = 0;
  int blocks = 0;
};

// Reads the manifest once. The cheap structural derivation runs before any
// checksum, so an inconsistent freeze is refused in milliseconds rather than
// after re-hashing hundreds of gigabytes.
std::vector<json> ReadManifestRows(const std::string& manifestPath)
{
  std::ifstream input(manifestPath);
  if (!input) {
    throw std::runtime_error(
        "Cannot open canonical manifest: " + manifestPath);
  }
  std::vector<json> rows;
  std::string line;
  while (std::getline(input, line)) {
    if (line.empty()) continue;
    rows.push_back(json::parse(line));
  }
  if (rows.empty()) {
    throw std::runtime_error("Canonical manifest is empty: " + manifestPath);
  }
  return rows;
}

DerivedFreezeShape DeriveFreezeShape(const std::vector<json>& rows,
                                     const std::string& manifestPath)
{
  DerivedFreezeShape shape;
  shape.rows = static_cast<int>(rows.size());

  std::map<std::string, int> perTune;
  std::set<long long> eventValues;
  std::set<int> blockValues;
  for (const json& row : rows) {
    if (!row.contains("tune") || !row.contains("requested_successes") ||
        !row.contains("block")) {
      throw std::runtime_error(
          "Canonical manifest row lacks tune/requested_successes/block: " +
          manifestPath);
    }
    ++perTune[row.at("tune").get<std::string>()];
    eventValues.insert(row.at("requested_successes").get<long long>());
    blockValues.insert(row.at("block").get<int>());
  }

  // A freeze whose jobs do not all request the same exposure has no single
  // events-per-job, and every per-tune total below would be a fiction.
  if (eventValues.size() != 1U) {
    throw std::runtime_error(
        "Canonical manifest has non-uniform requested_successes; the freeze "
        "has no single events-per-job: " + manifestPath);
  }
  shape.eventsPerJob = *eventValues.begin();
  if (shape.eventsPerJob <= 0) {
    throw std::runtime_error(
        "Canonical manifest declares a non-positive events-per-job: " +
        manifestPath);
  }

  if (perTune.empty()) {
    throw std::runtime_error("Canonical manifest names no tunes: " +
                             manifestPath);
  }
  shape.jobsPerTune = perTune.begin()->second;
  for (const auto& entry : perTune) {
    if (entry.second != shape.jobsPerTune) {
      throw std::runtime_error(
          "Canonical manifest has unequal per-tune exposure; tune " +
          entry.first + " is not matched to the others in " + manifestPath);
    }
    shape.tunes.push_back(entry.first);
  }

  shape.blocks = static_cast<int>(blockValues.size());
  if (shape.blocks <= 0 || *blockValues.begin() != 0 ||
      *blockValues.rbegin() != shape.blocks - 1) {
    throw std::runtime_error(
        "Canonical manifest block indices are not a contiguous 0..N-1 range: " +
        manifestPath);
  }
  if (shape.jobsPerTune % shape.blocks != 0) {
    throw std::runtime_error(
        "Canonical manifest jobs-per-tune is not divisible by its block "
        "count; blocks cannot carry equal exposure: " + manifestPath);
  }
  if (shape.rows !=
      static_cast<int>(shape.tunes.size()) * shape.jobsPerTune) {
    throw std::runtime_error(
        "Canonical manifest row count is not tunes x jobs-per-tune: " +
        manifestPath);
  }
  // The tune SET is derived, but it still has to be the set this macro draws.
  // A freeze naming other tunes is a different measurement, not a shape
  // variation, and selecting files nothing reads would fail silently.
  std::vector<std::string> expectedTunes = TuneNames();
  std::sort(expectedTunes.begin(), expectedTunes.end());
  if (shape.tunes != expectedTunes) {
    throw std::runtime_error(
        "Canonical manifest tunes are not the configured tune set: " +
        manifestPath);
  }
  return shape;
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
  const std::string sealPath =
      JoinPath({freezeDirectory, "freeze_seal.json"});
  const std::string validationLogPath =
      JoinPath({freezeDirectory, "canonical_raw_validation.log"});

  const std::vector<json> rows = ReadManifestRows(manifestPath);
  const DerivedFreezeShape shape = DeriveFreezeShape(rows, manifestPath);
  const std::string manifestSha =
      Hadronization::Sha256FileHex(manifestPath);

  // ---- the seal must agree with what the manifest says about itself -------
  const json seal = ReadJsonFile(sealPath, "canonical freeze seal");
  const long long sealedEvents =
      seal.value("total_requested_successes", -1LL);
  const long long derivedEvents =
      static_cast<long long>(shape.rows) * shape.eventsPerJob;
  std::vector<std::string> sealedTunes;
  if (seal.contains("tunes") && seal.at("tunes").is_array()) {
    for (const auto& tune : seal.at("tunes")) {
      sealedTunes.push_back(tune.get<std::string>());
    }
  }
  std::vector<std::string> sortedSealedTunes = sealedTunes;
  std::sort(sortedSealedTunes.begin(), sortedSealedTunes.end());
  if (seal.value("schema", "") != "hf_canonical_freeze_seal_v2" ||
      seal.value("canonical_manifest_sha256", "") != manifestSha ||
      seal.value("rows", -1) != shape.rows ||
      seal.value("jobs_per_tune", -1) != shape.jobsPerTune ||
      seal.value("blocks", -1) != shape.blocks ||
      sealedEvents != derivedEvents ||
      sortedSealedTunes != shape.tunes) {
    throw std::runtime_error(
        "Canonical freeze seal disagrees with its own manifest (schema, "
        "manifest digest, rows, jobs-per-tune, blocks, tunes or total "
        "exposure): " + sealPath);
  }

  // ---- the campaign-level validation log, if the campaign ran one ---------
  // Absent means "not claimed". It is never read as "passed": the per-row
  // checksum verification below is performed regardless, and is the same
  // exhaustive check validate_canonical_manifest.sh performs.
  std::string validationLogStatus = "absent";
  if (!gSystem->AccessPathName(validationLogPath.c_str())) {
    std::ifstream logInput(validationLogPath);
    std::ostringstream expected;
    expected << "CANONICAL_RAW_VALIDATION errors=0 files=" << shape.rows;
    std::string logLine;
    bool matched = false;
    while (std::getline(logInput, logLine)) {
      if (logLine.rfind(expected.str(), 0) == 0) matched = true;
    }
    if (!matched) {
      throw std::runtime_error(
          "Canonical raw-validation log is present but does not record "
          "errors=0 for this freeze's row count: " + validationLogPath);
    }
    validationLogStatus = "verified";
  }

  std::cout
      << "CANONICAL_FREEZE_CONTRACT"
      << " manifest=" << manifestPath
      << " manifest_sha256=" << manifestSha
      << " tunes=" << shape.tunes.size()
      << " jobs_per_tune=" << shape.jobsPerTune
      << " events_per_job=" << shape.eventsPerJob
      << " events_per_tune="
      << static_cast<long long>(shape.jobsPerTune) * shape.eventsPerJob
      << " rows=" << shape.rows
      << " blocks=" << shape.blocks
      << " validation_log=" << validationLogStatus
      << " shape=derived" << std::endl;

  // ---- rows -------------------------------------------------------------
  RawFileSelection selection;
  selection.mode = DatasetInputMode::kCanonicalManifest;
  selection.source = manifestPath;
  std::map<std::string, std::set<int>> slots;
  std::map<std::string, std::map<int, int>> blockCounts;
  std::map<std::string, std::map<int, std::string>> pathsBySlot;
  std::set<std::string> rawPaths;
  std::set<long long> seeds;
  // The campaign identity every row must agree on. In a union freeze each row's
  // `campaign` names the SOURCE it came from and `final_campaign` names the
  // union, so the shared identity is the latter where it exists. Requiring
  // `campaign` itself to be uniform would reject a legitimate union.
  const auto campaignIdentity = [](const json& row) {
    const std::string finalCampaign = row.value("final_campaign", "");
    return finalCampaign.empty() ? row.value("campaign", "") : finalCampaign;
  };
  const std::string campaign = campaignIdentity(rows.front());
  if (campaign.empty()) {
    throw std::runtime_error(
        "Canonical manifest rows do not name a campaign: " + manifestPath);
  }

  // ---- the identity chain: selector -> campaign -> these rows -------------
  // Rows agreeing with EACH OTHER is not the same as belonging to the dataset
  // the selector promoted. HADRONIZATION_CANONICAL_MANIFEST is only a path, so
  // without this any other campaign's correctly sealed freeze would satisfy
  // every check above and render under this dataset's authorization.
  const std::string promotedCampaign =
      EnvironmentValue("HADRONIZATION_CAMPAIGN");
  if (promotedCampaign.empty()) {
    throw std::runtime_error(
        "Canonical dataset selection requires HADRONIZATION_CAMPAIGN, the "
        "campaign the selector promoted; refusing to accept a freeze whose "
        "provenance cannot be checked against it");
  }
  if (promotedCampaign != campaign) {
    throw std::runtime_error(
        "Canonical manifest belongs to campaign '" + campaign +
        "' but the selector promoted '" + promotedCampaign + "': " +
        manifestPath);
  }

  for (const json& row : rows) {
    const std::string tune = row.at("tune").get<std::string>();
    const int slot = row.at("canonical_slot").get<int>();
    const int block = row.at("block").get<int>();
    const std::string rawRelative = row.at("raw_path").get<std::string>();
    const std::string expectedRawSha =
        row.at("raw_sha256").get<std::string>();

    // Every row carries its own per-job validation evidence. This is the
    // substantive validation record the narrowed contract relies on, so its
    // absence or a malformed digest is a refusal, not a warning.
    const bool perJobEvidence =
        !row.value("attempt_receipt_path", std::string()).empty() &&
        !row.value("raw_validation_log_path", std::string()).empty() &&
        IsLowerHexSha256(row.value("raw_validation_log_sha256", "")) &&
        !row.value("raw_validation_receipt_path", std::string()).empty() &&
        IsLowerHexSha256(row.value("raw_validation_receipt_sha256", ""));

    if (row.at("raw_schema").get<std::string>() !=
            "hf_primary_ground_raw_v7" ||
        row.at("selector").get<std::string>() !=
            "hard_trigger_primary_ground__primary_ground_associate_v1" ||
        row.at("requested_successes").get<long long>() !=
            shape.eventsPerJob ||
        campaignIdentity(row) != campaign ||
        !IsLowerHexSha256(expectedRawSha) ||
        !perJobEvidence ||
        slot < 0 || slot >= shape.jobsPerTune ||
        block != slot % shape.blocks ||
        !slots[tune].insert(slot).second ||
        !seeds.insert(row.at("seed").get<long long>()).second ||
        !IsSafeRelativePath(rawRelative) ||
        !rawPaths.insert(rawRelative).second) {
      throw std::runtime_error(
          "Invalid or duplicate canonical manifest row for " + tune +
          " slot " + std::to_string(slot));
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
  }

  for (const std::string& tune : shape.tunes) {
    if (static_cast<int>(slots[tune].size()) != shape.jobsPerTune) {
      throw std::runtime_error(
          "Canonical manifest does not contain equal exposure for " + tune);
    }
    for (int slot = 0; slot < shape.jobsPerTune; ++slot) {
      if (!slots[tune].count(slot) || !pathsBySlot[tune].count(slot)) {
        throw std::runtime_error(
            "Canonical manifest slots are not contiguous for " + tune);
      }
      selection.filesByTune[tune].push_back(pathsBySlot[tune].at(slot));
    }
    for (int block = 0; block < shape.blocks; ++block) {
      if (blockCounts[tune][block] != shape.jobsPerTune / shape.blocks) {
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

// ONE beam-energy string for the whole raw-tree figure family. Figure 4 and the
// 30 species panels must not be able to disagree about √s.
const char* BeamEnergyLine()
{
  return "pp, #sqrt{s} = 13.6 TeV";
}

// ONE format for an acceptance number, so the trailing-decimal question ("|η| ≤ 1"
// vs "|η| ≤ 1.0") is a single open decision for the family rather than a
// per-figure accident. Change "%g" here and every acceptance line follows.
std::string AcceptanceNumber(double value)
{
  return TString::Format("%g", value).Data();
}

const char* MultiplicityDefinitionLine1()
{
  return BeamEnergyLine();
}

// Derive the multiplicity caption from the producer's central-counter constants.
// The wide-associate acceptance does not define hMULTIPLICITY.
const char* MultiplicityDefinitionLine2()
{
  static const std::string line =
      std::string("#it{p}_{T} > ") +
      TString::Format("%.2f", Hadronization::kMultiplicityPtMin).Data() +
      " GeV/#it{c}";
  return line.c_str();
}

const char* MultiplicityDefinitionLine3()
{
  static const std::string line =
      std::string("|#eta| #leq ") +
      AcceptanceNumber(Hadronization::kMultiplicityEtaCentral) +
      ", primary charged, heavy flavour excluded";
  return line.c_str();
}

// ---------------------------------------------------------------------------
// The per-species panels' own acceptance.
//
// E10 was a caption that took the ASSOCIATE acceptance and printed it over the
// CENTRAL multiplicity counter. The mirror-image gap sat on these panels: they
// stated no acceptance at all, so a reader could not tell that the drawn η range
// IS the cut rather than a zoom, and the run record's §1.2 wording appeared
// nowhere on the figures it describes.
//
// Every number below comes from the predicate that fills these histograms --
// PassCanonicalInclusiveSelection, i.e. IsDirectPrimaryStatus and
// IsCentralKinematic(..., trigger=false). Those two now read their limits from
// named constants instead of literals, so these lines cannot drift from the cut.
//
// "direct primary hadronisation products", never "prompt": Model.tex mislabels
// this same status window, and the figures must not inherit that.
const char* SpeciesSelectionLine1()
{
  static const std::string line =
      std::string("direct primary hadronisation products (status ") +
      TString::Format("%d", Hadronization::kDirectPrimaryStatusMin).Data() +
      "-" +
      TString::Format("%d", Hadronization::kDirectPrimaryStatusMax).Data() +
      ")";
  return line.c_str();
}

const char* SpeciesSelectionLine2()
{
  static const std::string line =
      std::string("#it{p}_{T} > ") +
      TString::Format("%.2f", Hadronization::kCentralPtMinAssociate).Data() +
      " GeV/#it{c}, |#eta| #leq " +
      AcceptanceNumber(Hadronization::kCentralEtaAbsMax);
  return line.c_str();
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

// Every figure this macro draws is a DENSE spectrum -- figure 4 carries ~170
// bins and each species panel ~100 -- so the whole file runs in dense-spectrum
// mode. See plotting/TunePlotStyle.h for why the marker mandate is conditioned
// on density rather than dropped.
constexpr bool kDenseSpectra = true;

// A never-drawn stand-in that carries the tune's REAL marker, so the legend
// still shows circle / square / triangle while no marker is drawn on the data.
TH1D* MakeTuneLegendProxy(const std::string& tune, const std::string& name)
{
  TH1D* proxy = new TH1D(name.c_str(), "", 1, 0.0, 1.0);
  proxy->SetDirectory(nullptr);
  proxy->SetStats(0);
  proxy->SetLineColor(TuneColor(tune));
  proxy->SetMarkerColor(TuneColor(tune));
  proxy->SetMarkerStyle(TuneMarker(tune));   // the real marker, legend only
  proxy->SetLineStyle(TuneLineStyle(tune));
  proxy->SetLineWidth(2);
  proxy->SetMarkerSize(1.1);
  return proxy;
}

// Draw indices with the reference tune LAST, so it is never buried by a curve
// that agrees with it to within a line width. Legend order is unaffected.
std::vector<size_t> ReferenceLastOrder(const std::vector<std::string>& tunes)
{
  std::vector<size_t> order;
  for (size_t i = 0; i < tunes.size(); ++i)
    if (!HadronizationPlotStyle::IsReferenceTune(tunes[i])) order.push_back(i);
  for (size_t i = 0; i < tunes.size(); ++i)
    if (HadronizationPlotStyle::IsReferenceTune(tunes[i])) order.push_back(i);
  return order;
}

// The acceptance block's anchor, chosen from the panel's own data.
//
// THE DEFECT THIS CLOSES. The block was pinned bottom-left for all 30 panels.
// That is empty space on 26 of them. On the four lowest-statistics pT panels --
// Lambda_c+, Lambda_c-bar, Sigma_b0, Sigma_b0-bar -- the spectrum falls into
// that corner and the error bars cross the text. Suppressing the markers cut the
// overlap but did not remove it, because the E1 bars are tall where the counts
// are small.
//
// A fixed anchor cannot serve both cases, so the anchor is computed. The rule is
// one rule for all 30 panels: measure the block's own box against the drawn bins,
// use the bottom-left anchor when that box is clear, and use the top-left anchor
// when it is not.
//
// The measurement includes the error bars, because the bars are what strike the
// text. It does not drop them and it does not shorten the caption.
// The caption's footprint, ONE BOX PER LINE.
//
// A single rectangle around all four lines is the wrong shape. Three of the four
// lines are short, so that rectangle claims the white space to their right, and
// a curve passing through that white space reads as a collision when the text is
// untouched. Measured against the four per-line boxes instead, only a curve that
// crosses actual glyphs counts.
//
// The widths are measured, not guessed. tools/check_panel_caption_collisions.py
// calibrates them on a panel where the block sits in the open and reports, on an
// 856-pixel canvas:
//
//     line 1  "PYTHIA 8"                      x = [167, 229]  -> width 0.073
//     line 2  BeamEnergyLine                  x = [194, 299]  -> width 0.154
//     line 3  SpeciesSelectionLine1           x = [167, 553]  -> width 0.451
//     line 4  SpeciesSelectionLine2           x = [204, 342]  -> width 0.205
//
// Widths run from the anchor x, so each box starts where its line starts.
// THE CAPTION SITS ABOVE THE FRAME.
//
// WHY THE ANCHOR LADDER WAS NOT ENOUGH. The ladder searched inside the frame and
// reached 28 of 30 panels. Two pT panels -- Lambda_c-bar and Sigma_b0-bar -- have
// no clear baseline anywhere inside the frame, because their error bars span the
// frame across the caption's x range.
//
// TWO OPTIONS WERE MEASURED before this one was chosen.
//
// Option A lowered the y-axis so the data rose above the caption. Measured on
// render #5's generated files, the extra range needed at the bottom anchor was:
// pT D+ 0.20 decades, D- 0.37, Sigma_b0 0.80, Lambda_c+ 1.26, Lambda_c-bar 1.52,
// and Sigma_b0-bar 5.69. Nearly six decades of empty axis under one panel is a
// figure a reader can misread. On the linear eta panels the same rule demanded a
// NEGATIVE minimum, which a normalised-entries axis cannot carry.
//
// Option B moves the caption out of the frame. It cannot meet the data at any
// statistics, so it holds for every future campaign and not only for this one.
// It costs frame height: 0.730 of the canvas becomes 0.580, which is 20.5 %.
//
// Option B also makes the family MORE uniform, not less. All 30 captions sit at
// one position, where the ladder gave three.
//
// The constants come from the geometry and from a preview. The title baseline is
// 0.965. A first caption baseline of 0.920 put the block under the title's
// descender -- Sigma_b0-bar carries a subscript -- so the gap is 0.065 and the
// first baseline is 0.900. Four lines at 0.044 and one glyph height below the
// last put the caption's lowest edge at 0.738. A top margin of 0.28 sets the
// frame top at 0.720, which clears it by 0.018.
constexpr double kPanelTopMargin = 0.28;
constexpr double kCaptionFirstBaseline = 0.900;

constexpr int kBlockLines = 4;
constexpr double kBlockLineWidthNdc[kBlockLines] = {0.073, 0.154, 0.451, 0.205};
constexpr double kBlockGlyphNdc = 0.030;

// Box for one caption line. `line` is 0 for the top line.
inline void BlockLineBoxNdc(double x, double yTop, double dy, int line,
                            double* x0, double* x1, double* y0, double* y1)
{
  const double baseline = yTop - line * dy;
  *x0 = x;
  *x1 = x + kBlockLineWidthNdc[line];
  *y1 = baseline + kBlockGlyphNdc;
  *y0 = baseline - kBlockGlyphNdc;
}

// Convert a pad-NDC coordinate to the user coordinate the histograms live in.
inline double NdcToUserX(double ndc, double leftMargin, double rightMargin,
                         double axisMin, double axisMax)
{
  const double span = 1.0 - leftMargin - rightMargin;
  const double frac = (ndc - leftMargin) / span;
  return axisMin + frac * (axisMax - axisMin);
}

inline double NdcToUserY(double ndc, double bottomMargin, double topMargin,
                         double axisMin, double axisMax, bool logY)
{
  const double span = 1.0 - bottomMargin - topMargin;
  const double frac = (ndc - bottomMargin) / span;
  if (!logY) return axisMin + frac * (axisMax - axisMin);
  const double lo = std::log10(std::max(axisMin, 1.0e-300));
  const double hi = std::log10(std::max(axisMax, 1.0e-300));
  return std::pow(10.0, lo + frac * (hi - lo));
}

// True when no drawn bin, INCLUDING its error bar, enters the block's box.
inline bool BlockRegionIsClear(const std::vector<TH1D*>& hists,
                               double x0Ndc, double x1Ndc,
                               double y0Ndc, double y1Ndc,
                               double leftMargin, double rightMargin,
                               double bottomMargin, double topMargin,
                               double yAxisMin, double yAxisMax, bool logY)
{
  if (hists.empty()) return true;
  // The DISPLAYED range, not the full axis. The pT panels are binned to 7000
  // GeV/c and drawn to 50 through SetRange, so GetXmin/GetXmax would map the
  // block's box across the whole axis and scan bins the reader never sees.
  const TAxis* axis = hists.front()->GetXaxis();
  const double xAxisMin = axis->GetBinLowEdge(axis->GetFirst());
  const double xAxisMax = axis->GetBinUpEdge(axis->GetLast());

  const double xLo = NdcToUserX(x0Ndc, leftMargin, rightMargin, xAxisMin, xAxisMax);
  const double xHi = NdcToUserX(x1Ndc, leftMargin, rightMargin, xAxisMin, xAxisMax);
  const double yLo = NdcToUserY(y0Ndc, bottomMargin, topMargin, yAxisMin, yAxisMax, logY);
  const double yHi = NdcToUserY(y1Ndc, bottomMargin, topMargin, yAxisMin, yAxisMax, logY);

  for (const TH1D* hist : hists) {
    if (!hist) continue;
    for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
      const double centre = hist->GetBinCenter(bin);
      if (centre < xLo || centre > xHi) continue;
      const double content = hist->GetBinContent(bin);
      if (content == 0.0) continue;
      const double error = hist->GetBinError(bin);
      const double low = content - error;
      const double high = content + error;
      if (high >= yLo && low <= yHi) return false;
    }
  }
  return true;
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
  hist->SetMarkerStyle(
      HadronizationPlotStyle::SpectrumMarker(kDenseSpectra, tune));
  hist->SetLineStyle(TuneLineStyle(tune));
  hist->SetLineWidth(2);
  hist->SetMarkerSize(
      HadronizationPlotStyle::SpectrumMarkerSize(kDenseSpectra, 0.9f));
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
  ratio->SetMarkerStyle(
      HadronizationPlotStyle::SpectrumMarker(kDenseSpectra, tune));
  ratio->SetLineStyle(TuneLineStyle(tune));
  ratio->SetLineWidth(2);
  ratio->SetMarkerSize(
      HadronizationPlotStyle::SpectrumMarkerSize(kDenseSpectra, 0.75f));
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

// ---------------------------------------------------------------------------
// The inset's boundary markers come from the COMMITTED ARTIFACT, never from a
// quantile of the drawn histogram.
//
// What this replaces, and why it was wrong. The previous implementation took
// running-integral quantiles of whichever histogram it was handed
// (`CalculateMultiplicityThreshold`). That is a per-tune derivation of an axis
// that docs/PRODUCTION_SHAPE_DECISION.md ruled is ABSOLUTE and shared, and it
// was wrong twice over:
//
//   1. The drawn histogram is the PRODUCTION sample -- HardQCD with
//      pTHatMin = 2 -- while the percentile labels are defined on the MONASH
//      MINIMUM-BIAS distribution. Quantiles of one distribution were being
//      drawn under labels defined on a different one.
//   2. config/multiplicity_class_boundaries_v1.json says in its own text that
//      it is THE one definition and that no consumer may carry a copy, because
//      "two definitions drift, and the axis is the thing every per-multiplicity
//      number is conditioned on". This macro was a third consumer that never
//      read it.
//
// So: boundaries are read from the artifact, and the labels are RECOMPUTED from
// the committed MB anchor as the fraction strictly below each boundary -- the
// same rule, and the same source files, as tools/class_label_format.py.
// Recomputed rather than transcribed so a label cannot drift away from the
// sample it claims to describe.
// ---------------------------------------------------------------------------

struct CommonBoundaryMarker {
  double nch;            // absolute half-integer lower edge, from the artifact
  // MONASH-MB percentile in the receipt's convention: 100 - (fraction strictly
  // below), i.e. "top p%". A low-activity edge therefore carries a LARGE
  // number: boundary -0.5 is 100%, boundary 32.5 is 8.422%. Verified against
  // results/validation/plotting/hf_run3_v1_threetune_20260816/
  // multiplicity_boundary_receipt_v1_polished.json to better than 0.0005 on
  // all eleven boundaries, which is the receipt's own rounding.
  double mbPercentile;
  std::string className; // c1 ... c11, from the artifact
};

std::map<int, double> LoadMinimumBiasNch(const std::string& base,
                                         const std::string& tune)
{
  const std::string path = base +
      "/AnalysisScripts/anchors/b4_multiplicity_mb/nch_mb_" + tune + ".csv";
  std::ifstream stream(path);
  if (!stream.is_open()) {
    throw std::runtime_error(
        "Cannot open the committed minimum-bias anchor " + path +
        ". The inset's percentile labels are defined on it and are not "
        "recoverable from the production sample.");
  }
  std::map<int, double> distribution;
  std::string line;
  std::getline(stream, line);  // header: nch,count
  while (std::getline(stream, line)) {
    if (line.empty()) continue;
    const size_t comma = line.find(',');
    if (comma == std::string::npos) continue;
    distribution[std::stoi(line.substr(0, comma))] =
        std::stod(line.substr(comma + 1));
  }
  if (distribution.empty()) {
    throw std::runtime_error("Minimum-bias anchor is empty: " + path);
  }
  return distribution;
}

std::vector<CommonBoundaryMarker> CommonBoundaryMarkers(const std::string& base)
{
  const auto boundaries = HadronizationMultiplicity::LoadCommonBoundaries(
      MultiplicityPercentileClasses().size(),
      base + "/" + HadronizationMultiplicity::kCommonBoundaryArtifactPath);

  // The common percentile labels come from the MONASH minimum-bias anchor.
  const auto mb = LoadMinimumBiasNch(base, "MONASH");
  double total = 0.0;
  for (const auto& entry : mb) total += entry.second;

  std::vector<CommonBoundaryMarker> markers;
  for (size_t i = 0; i < boundaries.lowerEdgesNch.size(); ++i) {
    const double edge = boundaries.lowerEdgesNch[i];
    double below = 0.0;
    for (const auto& entry : mb) {
      if (entry.first < edge) below += entry.second;
    }
    markers.push_back(
        {edge, 100.0 - 100.0 * below / total, boundaries.classNames[i]});
  }

  std::cout << "COMMON_MULTIPLICITY_BOUNDARIES_CONSUMED"
            << " artifact=" << boundaries.artifactPath
            << " sha256=" << boundaries.artifactSha256
            << " classes=" << markers.size()
            << " label_provenance=MONASH_MB_recomputed"
            << std::endl;
  return markers;
}

void DrawMonashPercentileInset(TH1D* monash,
                               const std::string& outputStem,
                               std::vector<TH1D*>& keepAlive,
                               bool normalizeShape)
{
  if (!monash) return;

  TPad* inset = new TPad(("pMonashPercentiles_" + outputStem).c_str(),
                         "MONASH multiplicity percentile boundaries",
                         // This frame reaches N_ch 72.6 with a top edge at 9.4e-6.
                         // The earliest spectrum crossing occurs at N_ch 77.
                         0.18, 0.07, 0.50, 0.38);
  // A transparent inset keeps any spectrum overlap visible.
  inset->SetFillStyle(0);
  inset->SetFrameFillStyle(0);
  inset->SetFrameLineWidth(1);
  inset->SetTicks(1, 1);
  inset->SetLogx();
  inset->SetLogy();
  // 0.12 put the frame top at NDC 0.88 while the provenance line sits at 0.895,
  // so the frame line and its tick marks ran straight through the text. 0.20
  // drops the frame to 0.80 and leaves the two-line header its own band.
  inset->SetTopMargin(0.20);
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

  const auto markers = CommonBoundaryMarkers(FindHadronizationBase());
  for (const auto& marker : markers) {
    if (marker.nch < xMin || marker.nch > xMax) continue;
    TLine* line = new TLine(marker.nch, yMin, marker.nch, yMax);
    line->SetLineColor(kGray + 2);
    line->SetLineStyle(2);
    line->SetLineWidth(1);
    line->Draw("same");
  }
  insetHist->Draw("HIST SAME");

  // One label per class band, placed between this class's lower edge and the
  // next one's. The top class is open-ended, so its right edge is the frame.
  TLatex label;
  label.SetTextFont(42);
  label.SetTextSize(0.044);
  label.SetTextAlign(22);
  label.SetTextAngle(90);
  // 0.34 placed the label centres at 4.14e-6. These labels are ROTATED and
  // CENTRED, so each one extends about a decade above its own centre, and the
  // top class -- whose label sits at the geometric mean of [32.5, 170], i.e.
  // N_ch 74.3, where this curve has fallen to 2.05e-5 -- was struck straight
  // through by the curve it annotates. 0.20 drops the centres to 2.60e-7,
  // clearing the curve there, and still leaves every label inside the frame:
  // lower fractions began clipping the labels on the axis.
  const double yLabel = yMin * std::pow(yMax / yMin, 0.20);
  for (size_t i = 0; i < markers.size(); ++i) {
    const double left = std::max(markers[i].nch, xMin);
    const double right = (i + 1 < markers.size())
                             ? std::min(markers[i + 1].nch, xMax)
                             : xMax;
    if (right <= left) continue;
    const double xLabel = std::sqrt(left * right);
    // The MB-percentile range this absolute class spans. Percentiles DECREASE
    // with activity, so this class's own lower N_ch edge carries the larger
    // number and the next edge the smaller; the top class runs down to 0.
    const double hiPct = markers[i].mbPercentile;
    const double loPct =
        (i + 1 < markers.size()) ? markers[i + 1].mbPercentile : 0.0;
    // Precision comes from the generated header, which is the SAME constant the
    // legend labels in the plotting configs are generated with. It was 0 here
    // and 1 there; at 0 decimals E9's corrected 59.8 and the wrong 59.9 it
    // replaced both render as "60", hiding the correction on the figure.
    label.DrawLatex(
        xLabel, yLabel,
        Form("%.*f-%.*f%%", Hadronization::kClassLabelDecimals, loPct,
             Hadronization::kClassLabelDecimals, hiPct));
  }

  TLatex title;
  title.SetNDC();
  title.SetTextFont(62);
  title.SetTextSize(0.054);
  title.SetTextAlign(13);
  title.DrawLatex(0.02, 0.965, "Common absolute N_{ch} classes");
  TLatex provenance;
  provenance.SetNDC();
  provenance.SetTextFont(42);
  provenance.SetTextSize(0.042);
  provenance.SetTextAlign(13);
  provenance.DrawLatex(0.02, 0.895,
                       "labels: MONASH min-bias percentiles");
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
    }
    const std::vector<size_t> drawOrder = ReferenceLastOrder(tunes);
    for (size_t k = 0; k < drawOrder.size(); ++k) {
      hists[drawOrder[k]]->Draw(k == 0 ? "E1 HIST" : "E1 HIST SAME");
    }
    // Legend keeps the declared tune order and carries the marker the curves
    // no longer draw.
    for (size_t i = 0; i < hists.size(); ++i) {
      TH1D* proxy = MakeTuneLegendProxy(
          tunes[i], "hLegendProxy_" + outputStem + "_" + tunes[i]);
      insetKeepAlive.push_back(proxy);
      legend->AddEntry(proxy, tunes[i].c_str(), "lp");
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
    // The ratio pad holds no reference curve -- MONASH is its denominator -- so
    // the order here is simply the declared one.

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
  // The 0.28 margin places the frame at 0.720 below the caption at 0.738.
  canvas->SetTopMargin(kPanelTopMargin);
  if (logY) canvas->SetLogy();

  if (!hists.empty()) {
    const double maxY = MaximumWithErrors(hists);
    const double minY = logY ? std::max(PositiveMinimum(hists) * 0.35, 1.0e-12) : 0.0;
    const double upper = logY ? maxY * 8.0 : maxY * 1.28;

    // The frame lost height to the caption's margin, so the legend keeps its
    // position AS A FRACTION OF THE FRAME rather than in canvas NDC. It sat at
    // 0.705-0.855 inside a frame running 0.14 to 0.87, which is 0.774 to 0.979
    // of the frame height. Those fractions are preserved here, so the legend
    // stays where a reader of the earlier panels expects it.
    const double frameLo = 0.14;
    const double frameHi = 1.0 - kPanelTopMargin;
    const double frameH = frameHi - frameLo;
    TLegend* legend = new TLegend(0.62, frameLo + 0.774 * frameH,
                                  0.91, frameLo + 0.979 * frameH);
    legend->SetBorderSize(0);
    legend->SetFillStyle(0);
    legend->SetTextSize(0.035);

    for (size_t i = 0; i < hists.size(); ++i) {
      hists[i]->SetMinimum(minY);
      hists[i]->SetMaximum(std::max(upper, minY * 10.0));
    }
    const std::vector<size_t> panelOrder = ReferenceLastOrder(tunes);
    for (size_t k = 0; k < panelOrder.size(); ++k) {
      hists[panelOrder[k]]->Draw(k == 0 ? "E1 HIST" : "E1 HIST SAME");
    }
    for (size_t i = 0; i < hists.size(); ++i) {
      legend->AddEntry(
          MakeTuneLegendProxy(tunes[i],
                              "hPanelLegendProxy_" + outputStem + "_" + tunes[i]),
          tunes[i].c_str(), "lp");
    }
    legend->Draw();

    TLatex title;
    title.SetNDC();
    title.SetTextAlign(13);
    title.SetTextSize(0.034);
    if (species) title.DrawLatex(0.16, 0.965, ("Inclusive generated " + species->label).c_str());
    else title.DrawLatex(0.16, 0.965, "Shared event multiplicity");

    // The panel states its own acceptance.
    //
    // Placed BOTTOM-left. The first attempt put it top-left under the title,
    // which read fine in the source and collided on the page: the status line is
    // long enough to run under the legend's second entry on all three
    // observables, and on the log-y pT panels the block also sat on the data.
    // Only looking at the render showed it. The lower half of the frame is empty
    // for every observable here -- pT falls away to the right, eta is a band
    // around 0.01, phi is flat -- so the block clears both the legend (y >= 0.70)
    // and the data.
    //
    // Every constant derives from the filling predicate; see
    // SpeciesSelectionLine1/2.
    if (species) {
      TLatex info;
      info.SetNDC();
      info.SetTextFont(42);
      info.SetTextAlign(13);
      const double dy = 0.044;

      // ONE position for all 30 panels: the caption sits above the frame.
      //
      // The ladder that searched inside the frame is gone from the decision. It
      // reached 28 of 30, and the two it could not reach have no clear baseline
      // inside the frame at any height. See kPanelTopMargin for the measurement
      // that chose this over lowering the y-axis.
      //
      // The clearance test stays, and it now guards rather than chooses. The
      // caption band must lie OUTSIDE the frame. If a later edit moves the
      // margin or the baseline back inside, this prints the failure instead of
      // rediscovering it in a render.
      const double kAnchorX = 0.195;
      const double chosen = kCaptionFirstBaseline;
      const double captionBottom = chosen - (kBlockLines - 1) * dy - kBlockGlyphNdc;
      const double frameTop = 1.0 - kPanelTopMargin;
      const bool outsideFrame = captionBottom > frameTop;

      // Second half of the guard: no drawn bin, error bar included, may enter
      // any of the four line boxes. Geometry alone would pass if a later edit
      // changed the frame without moving the caption, so both halves are
      // reported.
      bool boxesClear = true;
      for (int line = 0; line < kBlockLines && boxesClear; ++line) {
        double bx0, bx1, by0, by1;
        BlockLineBoxNdc(kAnchorX, chosen, dy, line, &bx0, &bx1, &by0, &by1);
        boxesClear = BlockRegionIsClear(
            hists, bx0, bx1, by0, by1,
            canvas->GetLeftMargin(), canvas->GetRightMargin(),
            canvas->GetBottomMargin(), canvas->GetTopMargin(),
            minY, std::max(upper, minY * 10.0), logY);
      }

      std::cout << "ACCEPTANCE_BLOCK_ANCHOR stem=" << outputStem
                << " baseline=" << chosen
                << " caption_bottom=" << captionBottom
                << " frame_top=" << frameTop
                << " boxes_clear=" << (boxesClear ? 1 : 0)
                << ((outsideFrame && boxesClear) ? " status=ABOVE_FRAME"
                                                 : " status=CAPTION_GUARD_FAILED")
                << std::endl;

      const double x = kAnchorX;
      double y = chosen;
      info.SetTextFont(62);
      info.SetTextSize(0.030);
      info.DrawLatex(x, y, "PYTHIA 8");
      info.SetTextFont(42);
      info.SetTextSize(0.028);
      y -= dy;
      info.DrawLatex(x, y, BeamEnergyLine());
      y -= dy;
      info.DrawLatex(x, y, SpeciesSelectionLine1());
      y -= dy;
      info.DrawLatex(x, y, SpeciesSelectionLine2());
    }
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
                                        const char* outputDir = "plotting/Plots/KinematicSpectra",
                                        bool normalizeShape = true,
                                        bool strictInputs = true,
                                        const char* inputMode = "selector")
{
  using namespace InclusiveRawKinematics;

  SetPlotStyle();

  const std::string base = FindHadronizationBase();
  const std::string resolvedInput = ResolveFromBase(inputBaseDir ? inputBaseDir : "RootFiles/HF", base);
  const std::string resolvedOutput =
    ResolveFromBase(outputDir ? outputDir : "plotting/Plots/KinematicSpectra", base);
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
                                            const char* outputDir = "plotting/Plots/KinematicSpectra",
                                            bool normalizeShape = true,
                                            bool strictInputs = true,
                                            const char* inputMode = "selector")
{
  using namespace InclusiveRawKinematics;

  SetPlotStyle();

  const std::string base = FindHadronizationBase();
  const std::string resolvedInput = ResolveFromBase(inputBaseDir ? inputBaseDir : "RootFiles/HF", base);
  const std::string resolvedOutput =
    ResolveFromBase(outputDir ? outputDir : "plotting/Plots/KinematicSpectra", base);
  const RawFileSelection selection = LoadRawFileSelection(
      resolvedInput, inputMode ? inputMode : "selector", base);
  const std::string suffix = normalizeShape ? "shape" : "density";

  std::cout << "Inclusive raw multiplicity spectrum\n";
  std::cout << "===================================\n";
  std::cout << "Input base: " << resolvedInput << "\n";
  std::cout << "Input mode: " << DatasetInputModeName(selection.mode) << "\n";
  std::cout << "Input selection source: " << selection.source << "\n";
  std::cout << "Output dir: " << resolvedOutput << "\n";
  std::cout << "Nch definition: final charged non-heavy particles, pT > 0.15 GeV/c, |eta| <= 1\n";
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
    int expectedFilesPerTune = 110,
    // The campaign the selector promotes. Passed rather than derived from the
    // manifest on purpose: deriving it would make the identity check circular
    // and unable to detect the mismatch it exists to catch.
    const char* promotedCampaign = "")
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
  const std::string oldCampaign =
      EnvironmentValue("HADRONIZATION_CAMPAIGN");
  const bool hadCampaign = std::getenv("HADRONIZATION_CAMPAIGN");
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
    if (hadCampaign) {
      gSystem->Setenv("HADRONIZATION_CAMPAIGN", oldCampaign.c_str());
    } else {
      gSystem->Unsetenv("HADRONIZATION_CAMPAIGN");
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
    // Empty means "the fixture's own campaign", which is what every positive
    // case wants; a test severing the chain passes a different one.
    if (promotedCampaign && *promotedCampaign) {
      gSystem->Setenv("HADRONIZATION_CAMPAIGN", promotedCampaign);
    } else {
      std::ifstream firstRow(manifestPath);
      std::string line;
      std::getline(firstRow, line);
      const json row = json::parse(line);
      const std::string derived = row.value("final_campaign", "").empty()
          ? row.value("campaign", "")
          : row.value("final_campaign", "");
      gSystem->Setenv("HADRONIZATION_CAMPAIGN", derived.c_str());
    }
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
    // DENSE-SPECTRUM CONTRACT. A drawn curve carries the tune's colour and the
    // DENSE marker; the tune's real marker survives only on the legend proxy.
    // Asserting both halves is the point: checking the curve alone would pass
    // if the marker vanished from the figure altogether, and checking the proxy
    // alone would pass if the ribbons came back.
    for (TH1D* histogram : {styled, ratio}) {
      if (!histogram ||
          histogram->GetLineColor() != TuneColor(tune) ||
          histogram->GetMarkerColor() != TuneColor(tune) ||
          histogram->GetMarkerStyle() !=
              HadronizationPlotStyle::SpectrumMarker(kDenseSpectra, tune) ||
          histogram->GetLineStyle() != TuneLineStyle(tune)) {
        ++errors;
      }
    }
    TH1D* proxy = MakeTuneLegendProxy(tune, "hInclusiveLegendProxy_" + tune);
    if (!proxy ||
        proxy->GetMarkerStyle() != TuneMarker(tune) ||
        proxy->GetMarkerColor() != TuneColor(tune) ||
        proxy->GetLineColor() != TuneColor(tune)) {
      ++errors;
    }
    delete proxy;
    delete styled;
    delete ratio;
  }
  std::cout << "INCLUSIVE_RAW_TUNE_STYLE_TEST errors=" << errors
            << " mode=dense_spectrum drawn_marker="
            << HadronizationPlotStyle::kDenseSpectrumMarker
            << " legend_markers=20/21/22 all_lines_solid=1" << std::endl;
  return errors;
}
