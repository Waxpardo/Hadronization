#include "../generation/producer/HeavyFlavourUtils.h"
#include "../generation/registries/GeneratedHeavyFlavourRegistry.h"
#include "../generation/registries/GeneratedTuneSettingRegistry.h"
#include "../generation/producer/Sha256.h"
#include "../contracts/GeneratedPairRegistry.h"

#include "TBranch.h"
#include "TFile.h"
#include "TH1.h"
#include "TLeaf.h"
#include "TObjString.h"
#include "TTree.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <exception>
#include <iostream>
#include <iomanip>
#include <limits>
#include <locale>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <type_traits>
#include <vector>

namespace {

struct StoredAncestor {
  int pdg = 0;
  int status = 0;
  int mother1 = 0;
  int mother2 = 0;
  std::vector<int> mothers;
};

struct ReconstructedOrigin {
  int origin = static_cast<int>(Hadronization::Origin::kUnresolved);
  int resolution =
      static_cast<int>(Hadronization::MatchResolution::kNotApplicable);
  int matchedHard = -1;
  int depth = -1;
};


bool CarriesSignedHeavyConstituent(int pdg, int flavour, int requiredSign) {
  if (pdg == requiredSign * flavour) return true;
  const int absolute = std::abs(pdg);
  if (absolute >= 1000 && absolute <= 9999 &&
      (absolute / 10) % 10 == 0) {
    const int q1 = (absolute / 1000) % 10;
    const int q2 = (absolute / 100) % 10;
    const int sign = pdg > 0 ? 1 : -1;
    return sign == requiredSign && (q1 == flavour || q2 == flavour);
  }
  return false;
}

std::vector<int> StoredDirectMothers(
    const std::map<int, StoredAncestor>& ancestry, int index) {
  const auto found = ancestry.find(index);
  if (found == ancestry.end()) return {};
  std::vector<int> mothers = found->second.mothers;
  mothers.erase(
      std::remove_if(mothers.begin(), mothers.end(),
                     [](int mother) { return mother <= 0; }),
      mothers.end());
  std::sort(mothers.begin(), mothers.end());
  mothers.erase(std::unique(mothers.begin(), mothers.end()), mothers.end());
  return mothers;
}

std::vector<int> StoredNearestHeavyAncestors(
    const std::map<int, StoredAncestor>& ancestry,
    const std::vector<int>& starts, int flavour, int requiredSign,
    bool& graphComplete) {
  std::deque<std::pair<int, int>> queue;
  std::set<int> visited;
  for (const int start : starts) queue.push_back({start, 0});
  int foundDepth = -1;
  std::vector<int> found;
  while (!queue.empty()) {
    const auto [index, depth] = queue.front();
    queue.pop_front();
    if (foundDepth >= 0 && depth > foundDepth) break;
    if (index <= 0 || !visited.insert(index).second) continue;
    const auto node = ancestry.find(index);
    if (node == ancestry.end()) {
      graphComplete = false;
      continue;
    }
    if (std::abs(node->second.pdg) == flavour &&
        (node->second.pdg > 0 ? 1 : -1) == requiredSign) {
      foundDepth = depth;
      found.push_back(index);
      continue;
    }
    for (const int mother : StoredDirectMothers(ancestry, index)) {
      const auto parent = ancestry.find(mother);
      if (parent == ancestry.end()) {
        graphComplete = false;
      } else if (CarriesSignedHeavyConstituent(
                     parent->second.pdg, flavour, requiredSign)) {
        queue.push_back({mother, depth + 1});
      }
    }
  }
  return found;
}

ReconstructedOrigin ReconstructOrigin(
    const std::map<int, StoredAncestor>& ancestry,
    const std::vector<int>& allMothers, int flavour, int requiredSign,
    const std::map<int, int>& hardByIndex) {
  if (requiredSign == 0) return {};
  bool graphComplete = true;
  std::vector<int> starts;
  for (const int mother : allMothers) {
    const auto node = ancestry.find(mother);
    if (node == ancestry.end()) {
      graphComplete = false;
      continue;
    }
    if (CarriesSignedHeavyConstituent(node->second.pdg, flavour,
                                     requiredSign)) {
      starts.push_back(mother);
    }
  }
  std::sort(starts.begin(), starts.end());
  starts.erase(std::unique(starts.begin(), starts.end()), starts.end());
  if (starts.empty()) {
    return {static_cast<int>(Hadronization::Origin::kUnresolved),
            static_cast<int>(
                graphComplete
                    ? Hadronization::MatchResolution::kMissingCarrier
                    : Hadronization::MatchResolution::kBrokenLineage),
            -1, -1};
  }

  std::vector<int> candidates = StoredNearestHeavyAncestors(
      ancestry, starts, flavour, requiredSign, graphComplete);
  int totalDepth = 1;
  std::set<int> lineageVisited;
  while (candidates.size() == 1 && totalDepth < 1000) {
    const int index = candidates.front();
    if (!lineageVisited.insert(index).second) {
      return {static_cast<int>(Hadronization::Origin::kUnresolved),
              static_cast<int>(
                  Hadronization::MatchResolution::kBrokenLineage),
              -1, totalDepth};
    }
    const auto node = ancestry.find(index);
    if (node == ancestry.end()) {
      return {static_cast<int>(Hadronization::Origin::kUnresolved),
              static_cast<int>(
                  Hadronization::MatchResolution::kBrokenLineage),
              -1, totalDepth};
    }
    const auto hard = hardByIndex.find(index);
    if (hard != hardByIndex.end() &&
        hard->second == requiredSign * flavour) {
      return {static_cast<int>(Hadronization::Origin::kSelectedHard),
              static_cast<int>(Hadronization::MatchResolution::kUnique),
              index, totalDepth};
    }
    candidates.clear();
    for (const int mother : StoredDirectMothers(ancestry, index)) {
      const auto parent = ancestry.find(mother);
      if (parent == ancestry.end()) {
        graphComplete = false;
        continue;
      }
      if (std::abs(parent->second.pdg) == flavour &&
          (parent->second.pdg > 0 ? 1 : -1) == requiredSign) {
        candidates.push_back(mother);
      }
    }
    std::sort(candidates.begin(), candidates.end());
    candidates.erase(std::unique(candidates.begin(), candidates.end()),
                     candidates.end());
    if (candidates.empty()) {
      if (!graphComplete) {
        return {static_cast<int>(Hadronization::Origin::kUnresolved),
                static_cast<int>(
                    Hadronization::MatchResolution::kBrokenLineage),
                -1, totalDepth};
      }
      const int sourceStatus = std::abs(node->second.status);
      const auto origin =
          sourceStatus >= 31 && sourceStatus <= 39
              ? Hadronization::Origin::kMPI
              : (sourceStatus >= 41 && sourceStatus <= 59
                     ? Hadronization::Origin::kShower
                     : Hadronization::Origin::kOtherResolved);
      return {static_cast<int>(origin),
              static_cast<int>(Hadronization::MatchResolution::kUnique),
              -1, totalDepth};
    }
    ++totalDepth;
  }
  return {static_cast<int>(Hadronization::Origin::kUnresolved),
          static_cast<int>(
              candidates.size() > 1
                  ? Hadronization::MatchResolution::kAmbiguous
                  : Hadronization::MatchResolution::kBrokenLineage),
          -1, totalDepth};
}

bool IsPublicationTrigger(int pdg) {
  return std::any_of(
      Hadronization::kPairDefinitions.begin(),
      Hadronization::kPairDefinitions.end(),
      [pdg](const Hadronization::PairDefinition& pair) {
        return pair.triggerPdg == pdg;
      });
}

template <typename T>
bool ReadScalar(TTree* tree, const char* name, T& value) {
  if (!tree) return false;
  TBranch* branch = tree->GetBranch(name);
  if (!branch || std::string(branch->GetClassName()).size() != 0U) {
    return false;
  }
  TLeaf* leaf = branch->GetLeaf(name);
  if (!leaf) return false;
  const std::string type = leaf->GetTypeName();
  const bool correctType =
      (std::is_same_v<T, int> && type == "Int_t") ||
      (std::is_same_v<T, unsigned long long> && type == "ULong64_t") ||
      (std::is_same_v<T, long long> && type == "Long64_t") ||
      (std::is_same_v<T, double> && type == "Double_t");
  if (!correctType) return false;
  tree->SetBranchAddress(name, &value);
  const bool ok = tree->GetEntry(0) > 0;
  tree->ResetBranchAddresses();
  return ok;
}

bool ReadString(TTree* tree, const char* name, std::string& value) {
  if (!tree) return false;
  TBranch* branch = tree->GetBranch(name);
  if (!branch) return false;
  const std::string className = branch->GetClassName();
  if (className != "string" && className != "std::string") return false;
  std::string* pointer = nullptr;
  tree->SetBranchAddress(name, &pointer);
  if (tree->GetEntry(0) <= 0 || !pointer) {
    tree->ResetBranchAddresses();
    return false;
  }
  value = *pointer;
  tree->ResetBranchAddresses();
  return true;
}

}  // namespace

int ValidateRawOutput(const char* fileName, const char* expectedCampaign,
                      const char* expectedTune, int expectedLogicalId,
                      unsigned long long expectedSuccesses,
                      int expectedAttempt = -1, int expectedSeed = -1,
                      bool exhaustive = true,
                      const char* expectedRole = "",
                      int expectedCampaignOrdinal = -1,
                      double expectedPthatMin = -1.0,
                      unsigned long long expectedMultiplicityAuditEvents =
                          std::numeric_limits<unsigned long long>::max(),
                      const char* expectedConfigSha256 = "",
                      const char* expectedExecutableSha256 = "",
                      const char* expectedRepositoryCommit = "") {
  int errors = 0;
  auto fail = [&](const std::string& message) {
    std::cerr << "RAW_VALIDATION_ERROR " << message << "\n";
    ++errors;
  };

  TFile file(fileName, "READ");
  if (file.IsZombie()) {
    fail("file is missing, zombie, or unreadable");
    return errors;
  }
  auto* tree = dynamic_cast<TTree*>(file.Get("tree"));
  auto* metadata = dynamic_cast<TTree*>(file.Get("job_metadata"));
  auto* stability = dynamic_cast<TTree*>(file.Get("heavy_stability_audit"));
  auto* processCounts = dynamic_cast<TTree*>(file.Get("process_counts"));
  auto* effectiveSettings =
      dynamic_cast<TTree*>(file.Get("effective_settings"));
  auto* multiplicity = dynamic_cast<TH1*>(file.Get("hMULTIPLICITY"));
  auto* multiplicityWideHistogram =
      dynamic_cast<TH1*>(file.Get("hMULTIPLICITY_ETA40"));
  auto* processHistogram = dynamic_cast<TH1*>(file.Get("hPROCESS_CODE"));
  auto* stabilityCanonical =
      dynamic_cast<TObjString*>(file.Get("heavy_stability_audit_canonical"));
  auto* stabilityShaObject =
      dynamic_cast<TObjString*>(file.Get("heavy_stability_audit_sha256"));
  auto* effectiveSettingsCanonical = dynamic_cast<TObjString*>(
      file.Get("effective_settings_canonical"));
  auto* effectiveSettingsShaObject =
      dynamic_cast<TObjString*>(file.Get("effective_settings_sha256"));
  auto* primaryAllHeavyVersion = dynamic_cast<TObjString*>(
      file.Get("primary_all_heavy_match_version"));
  auto* multiplicityDefinitionVersion = dynamic_cast<TObjString*>(
      file.Get("multiplicity_definition"));
  if (!tree) fail("missing tree");
  if (!metadata || metadata->GetEntries() != 1) fail("missing/sized job_metadata");
  if (!stability || stability->GetEntries() == 0) fail("missing heavy_stability_audit");
  if (!processCounts || processCounts->GetEntries() == 0) fail("missing process_counts");
  if (!effectiveSettings || effectiveSettings->GetEntries() == 0) {
    fail("missing effective_settings");
  }
  if (!multiplicity) fail("missing hMULTIPLICITY");
  if (!multiplicityWideHistogram) {
    fail("missing hMULTIPLICITY_ETA40");
  }
  if (!processHistogram) fail("missing hPROCESS_CODE");
  if (!stabilityCanonical || !stabilityShaObject) {
    fail("missing heavy-stability checksum objects");
  }
  if (!effectiveSettingsCanonical || !effectiveSettingsShaObject) {
    fail("missing effective-settings checksum objects");
  }
  if (!primaryAllHeavyVersion) {
    fail("missing primary-all-heavy match contract object");
  }
  if (!multiplicityDefinitionVersion) {
    fail("missing multiplicity-definition contract object");
  }
  if (errors) return errors;

  std::string campaign, tune, role, schema, selector, originAlgorithm;
  std::string speciesSchema, registrySha, configSha;
  std::string multiplicityDefinition, lightGridSchema;
  std::string tuneAllowlistSchema, tuneAllowlistSha;
  std::string stabilityAuditSchema, stabilityAuditSha;
  std::string effectiveSettingsSchema, effectiveSettingsSha;
  std::string primaryAllHeavySchema;
  std::string executableSha, repositoryCommit, repositoryDirty;
  std::string rootVersion, pythiaVersion;
  int campaignOrdinal = -1;
  int logicalId = -1, attempt = -1, seed = -1, complete = 0;
  unsigned long long requested = 0, attempts = 0, successes = 0, failures = 0;
  unsigned long long entries = 0, decodeFailures = 0;
  unsigned long long duplicateConflictGroupsC = 0;
  unsigned long long duplicateConflictGroupsB = 0;
  unsigned long long duplicateDemotionsC = 0;
  unsigned long long duplicateDemotionsB = 0;
  unsigned long long multiHeavyRejectionsC = 0;
  unsigned long long multiHeavyRejectionsB = 0;
  unsigned long long conservationFailures = 0;
  unsigned long long classificationFailures = 0;
  unsigned long long primaryAllHeavyConflictGroups = 0;
  unsigned long long primaryAllHeavyDemotions = 0;
  unsigned long long primaryAllHeavyFailures = 0;
  unsigned long long effectiveSettingsEntries = 0;
  unsigned long long multiplicityOverflow = 0;
  unsigned long long multiplicityWideOverflow = 0;
  unsigned long long multiplicityAuditEvents = 0;
  unsigned long long peakRssKiB = 0;
  long long startUnixSeconds = 0;
  long long endUnixSeconds = 0;
  long long elapsedSeconds = 0;
  int rootCompressionSettings = -1;
  int rootCompressionAlgorithm = -1;
  int rootCompressionLevel = -1;
  double sumw = 0.0, sumw2 = 0.0, phaseSpacePthatMin = -1.0;
  double pythiaSigmaGenMb = 0.0, pythiaSigmaErrMb = 0.0;
  double pythiaWeightSum = 0.0;
  if (!ReadString(metadata, "campaign", campaign) ||
      !ReadString(metadata, "tune", tune) ||
      !ReadString(metadata, "role", role) ||
      !ReadString(metadata, "raw_schema", schema) ||
      !ReadString(metadata, "selector", selector) ||
      !ReadString(metadata, "origin_algorithm", originAlgorithm) ||
      !ReadString(metadata, "species_registry_schema", speciesSchema) ||
      !ReadString(metadata, "species_registry_sha256", registrySha) ||
      !ReadString(metadata, "multiplicity_definition",
                  multiplicityDefinition) ||
      !ReadString(metadata, "light_compensation_grid_schema",
                  lightGridSchema) ||
      !ReadString(metadata, "tune_difference_allowlist_schema",
                  tuneAllowlistSchema) ||
      !ReadString(metadata, "tune_difference_allowlist_sha256",
                  tuneAllowlistSha) ||
      !ReadString(metadata, "heavy_stability_audit_schema",
                  stabilityAuditSchema) ||
      !ReadString(metadata, "heavy_stability_audit_sha256",
                  stabilityAuditSha) ||
      !ReadString(metadata, "effective_settings_schema",
                  effectiveSettingsSchema) ||
      !ReadString(metadata, "effective_settings_sha256",
                  effectiveSettingsSha) ||
      !ReadString(metadata, "primary_all_heavy_match_schema",
                  primaryAllHeavySchema) ||
      !ReadString(metadata, "config_sha256", configSha) ||
      !ReadString(metadata, "executable_sha256", executableSha) ||
      !ReadString(metadata, "repository_commit", repositoryCommit) ||
      !ReadString(metadata, "repository_dirty", repositoryDirty) ||
      !ReadString(metadata, "root_version", rootVersion) ||
      !ReadString(metadata, "pythia_version", pythiaVersion)) {
    fail("missing string metadata");
  }
  if (!ReadScalar(metadata, "campaign_ordinal", campaignOrdinal) ||
      !ReadScalar(metadata, "logical_id", logicalId) ||
      !ReadScalar(metadata, "attempt", attempt) ||
      !ReadScalar(metadata, "seed", seed) ||
      !ReadScalar(metadata, "complete", complete) ||
      !ReadScalar(metadata, "requested_successes", requested) ||
      !ReadScalar(metadata, "attempts", attempts) ||
      !ReadScalar(metadata, "successful_events", successes) ||
      !ReadScalar(metadata, "failed_attempts", failures) ||
      !ReadScalar(metadata, "tree_entries", entries) ||
      !ReadScalar(metadata, "content_decode_failures", decodeFailures) ||
      !ReadScalar(metadata, "phase_space_pthat_min", phaseSpacePthatMin) ||
      !ReadScalar(metadata, "pythia_sigma_gen_mb", pythiaSigmaGenMb) ||
      !ReadScalar(metadata, "pythia_sigma_err_mb", pythiaSigmaErrMb) ||
      !ReadScalar(metadata, "pythia_weight_sum", pythiaWeightSum) ||
      !ReadScalar(metadata, "effective_settings_entries",
                  effectiveSettingsEntries) ||
      !ReadScalar(metadata, "start_unix_seconds", startUnixSeconds) ||
      !ReadScalar(metadata, "end_unix_seconds", endUnixSeconds) ||
      !ReadScalar(metadata, "elapsed_seconds", elapsedSeconds) ||
      !ReadScalar(metadata, "peak_rss_kib", peakRssKiB) ||
      !ReadScalar(metadata, "root_compression_settings",
                  rootCompressionSettings) ||
      !ReadScalar(metadata, "root_compression_algorithm",
                  rootCompressionAlgorithm) ||
      !ReadScalar(metadata, "root_compression_level",
                  rootCompressionLevel)) {
    fail("missing scalar metadata");
  }
  if (!ReadScalar(metadata, "duplicate_hard_carrier_conflict_groups_charm",
                  duplicateConflictGroupsC) ||
      !ReadScalar(metadata, "duplicate_hard_carrier_conflict_groups_beauty",
                  duplicateConflictGroupsB) ||
      !ReadScalar(metadata, "duplicate_hard_carrier_demotions_charm",
                  duplicateDemotionsC) ||
      !ReadScalar(metadata, "duplicate_hard_carrier_demotions_beauty",
                  duplicateDemotionsB) ||
      !ReadScalar(metadata, "multi_heavy_constituent_rejections_charm",
                  multiHeavyRejectionsC) ||
      !ReadScalar(metadata, "multi_heavy_constituent_rejections_beauty",
                  multiHeavyRejectionsB) ||
      !ReadScalar(metadata, "heavy_flavour_conservation_failures",
                  conservationFailures) ||
      !ReadScalar(metadata, "origin_classification_failures",
                  classificationFailures) ||
      !ReadScalar(metadata, "primary_all_heavy_conflict_groups",
                  primaryAllHeavyConflictGroups) ||
      !ReadScalar(metadata, "primary_all_heavy_demotions",
                  primaryAllHeavyDemotions) ||
      !ReadScalar(metadata, "primary_all_heavy_match_failures",
                  primaryAllHeavyFailures)) {
    fail("missing origin-rejection metadata");
  }
  if (!ReadScalar(metadata, "multiplicity_overflow", multiplicityOverflow) ||
      !ReadScalar(metadata, "multiplicity_wide_overflow",
                  multiplicityWideOverflow) ||
      !ReadScalar(metadata, "multiplicity_audit_events",
                  multiplicityAuditEvents) ||
      !ReadScalar(metadata, "sum_weights", sumw) ||
      !ReadScalar(metadata, "sum_weights2", sumw2)) {
    fail("missing or incorrectly typed accounting metadata");
  }

  if (campaign != expectedCampaign) fail("campaign mismatch");
  if (tune != expectedTune) fail("tune mismatch");
  if (campaign.empty() || campaignOrdinal < 1 || campaignOrdinal > 65535) {
    fail("invalid campaign identity metadata");
  }
  if (role != "primary" && role != "reserve" && role != "pilot") {
    fail("invalid role metadata");
  }
  if (std::string(expectedRole).size() > 0 && role != expectedRole) {
    fail("role mismatch");
  }
  if (expectedCampaignOrdinal >= 0 &&
      campaignOrdinal != expectedCampaignOrdinal) {
    fail("campaign ordinal mismatch");
  }
  if (schema != Hadronization::kRawSchema) fail("raw schema mismatch");
  if (selector != Hadronization::kSelectorVersion) fail("selector mismatch");
  if (originAlgorithm != Hadronization::kOriginAlgorithmVersion) {
    fail("origin-algorithm mismatch");
  }
  if (speciesSchema != Hadronization::kSpeciesRegistrySchema ||
      registrySha != Hadronization::kSpeciesRegistrySha256) {
    fail("species-registry checksum mismatch");
  }
  if (lightGridSchema !=
      Hadronization::kLightCompensationGridSchema) {
    fail("light-compensation-grid contract mismatch");
  }
  if (multiplicityDefinition !=
          Hadronization::kMultiplicityDefinitionVersion ||
      multiplicityDefinitionVersion->GetString().Data() !=
          multiplicityDefinition) {
    fail("multiplicity-definition contract mismatch");
  }
  if (tuneAllowlistSchema !=
          Hadronization::kTuneDifferenceAllowlistSchema ||
      tuneAllowlistSha !=
          Hadronization::kTuneDifferenceAllowlistSha256) {
    fail("tune-difference allowlist checksum mismatch");
  }
  if (stabilityAuditSchema !=
          Hadronization::kHeavyStabilityAuditSchema ||
      stabilityAuditSha.size() != 64 ||
      stabilityAuditSha != stabilityShaObject->GetString().Data() ||
      stabilityAuditSha !=
          Hadronization::Sha256Hex(
              stabilityCanonical->GetString().Data())) {
    fail("heavy-stability audit checksum mismatch");
  }
  if (effectiveSettingsSchema != Hadronization::kEffectiveSettingsSchema ||
      effectiveSettingsSha.size() != 64 ||
      effectiveSettingsSha != effectiveSettingsShaObject->GetString().Data() ||
      effectiveSettingsSha != Hadronization::Sha256Hex(
                                  effectiveSettingsCanonical->GetString().Data())) {
    fail("effective-settings checksum mismatch");
  }
  if (primaryAllHeavySchema !=
          Hadronization::kPrimaryAllHeavyMatchSchema ||
      primaryAllHeavyVersion->GetString().Data() !=
          primaryAllHeavySchema) {
    fail("primary-all-heavy match contract mismatch");
  }
  if (effectiveSettingsEntries !=
          static_cast<unsigned long long>(
              effectiveSettings->GetEntries()) ||
      effectiveSettingsEntries <=
          Hadronization::kAuditedPythiaSettingKeys.size()) {
    fail("effective-settings snapshot is not exhaustive/cardinality differs");
  }
  if (configSha.empty() || configSha == "UNRECORDED") {
    fail("config checksum missing");
  }
  if (executableSha.empty() || executableSha == "UNRECORDED") {
    fail("executable checksum missing");
  }
  if (repositoryCommit.empty() || repositoryCommit == "UNRECORDED") {
    fail("repository commit missing");
  }
  if (repositoryDirty != "false") {
    fail("tracked-dirty production build is not canonical");
  }
  // The pinned generator version comes from HF_PYTHIA8_VERSION, which
  // setupEnv.sh resolves from config/dependencies.conf and has already
  // asserted against `pythia8-config --version`. Hardcoding it here is what
  // let this check keep demanding 8.315 after the migration to 8.317; it went
  // unnoticed because nothing ran the validator in between. Reading the pin
  // from the environment keeps the version in exactly one place.
  const char* expectedPythiaEnv = std::getenv("HF_PYTHIA8_VERSION");
  const std::string expectedPythia =
      expectedPythiaEnv != nullptr ? expectedPythiaEnv : "";
  if (expectedPythia.empty()) {
    fail("HF_PYTHIA8_VERSION is not set; source setupEnv.sh before validating");
  }
  if (rootVersion.empty() || pythiaVersion.rfind(expectedPythia, 0) != 0) {
    fail("unexpected or missing ROOT/PYTHIA version metadata (expected PYTHIA " +
         expectedPythia + ", got '" + pythiaVersion + "')");
  }
  if (std::string(expectedConfigSha256).size() > 0 &&
      configSha != expectedConfigSha256) {
    fail("config checksum does not match authorization");
  }
  if (std::string(expectedExecutableSha256).size() > 0 &&
      executableSha != expectedExecutableSha256) {
    fail("executable checksum does not match authorization");
  }
  if (std::string(expectedRepositoryCommit).size() > 0 &&
      repositoryCommit != expectedRepositoryCommit) {
    fail("repository commit does not match authorization");
  }
  if (logicalId != expectedLogicalId) fail("logical ID mismatch");
  if (logicalId < 0 || logicalId > 16383 || attempt < 0 || attempt > 4095 ||
      seed < 1 || seed > 900000000) {
    fail("logical/attempt/seed metadata outside declared domains");
  }
  if (expectedAttempt >= 0 && attempt != expectedAttempt) fail("attempt mismatch");
  if (expectedSeed >= 0 && seed != expectedSeed) fail("seed mismatch");
  if (requested != expectedSuccesses || successes != expectedSuccesses ||
      entries != expectedSuccesses ||
      static_cast<unsigned long long>(tree->GetEntries()) != expectedSuccesses) {
    fail("exact-success/tree-entry contract mismatch");
  }
  if (attempts != successes + failures) fail("attempt accounting identity failed");
  if (!complete) fail("producer did not mark output complete");
  if (!std::isfinite(sumw) || !std::isfinite(sumw2) || sumw2 < 0.0) {
    fail("invalid weight sums");
  }
  if (!std::isfinite(phaseSpacePthatMin) || phaseSpacePthatMin < 0.0 ||
      !std::isfinite(pythiaSigmaGenMb) || pythiaSigmaGenMb <= 0.0 ||
      !std::isfinite(pythiaSigmaErrMb) || pythiaSigmaErrMb < 0.0 ||
      !std::isfinite(pythiaWeightSum)) {
    fail("invalid structured PYTHIA normalization metadata");
  }
  if (expectedPthatMin >= 0.0) {
    const double tolerance =
        std::max(1e-12, std::abs(expectedPthatMin) * 1e-12);
    if (std::abs(phaseSpacePthatMin - expectedPthatMin) > tolerance) {
      fail("PhaseSpace:pTHatMin does not match authorization");
    }
  }
  if (expectedMultiplicityAuditEvents !=
          std::numeric_limits<unsigned long long>::max() &&
      multiplicityAuditEvents != expectedMultiplicityAuditEvents) {
    fail("multiplicity-audit event count does not match authorization");
  }
  if (decodeFailures != 0) fail("heavy-content decode failures are nonzero");
  if (conservationFailures != 0) {
    fail("heavy-flavour conservation failures are nonzero");
  }
  if (classificationFailures != 0) {
    fail("origin-classification invariant failures are nonzero");
  }
  if (primaryAllHeavyFailures != 0) {
    fail("primary-all-heavy match invariant failures are nonzero");
  }
  if (startUnixSeconds <= 0 || endUnixSeconds < startUnixSeconds ||
      elapsedSeconds < 0 ||
      std::llabs((endUnixSeconds - startUnixSeconds) - elapsedSeconds) > 1) {
    fail("invalid start/end/elapsed runtime metadata");
  }
  if (peakRssKiB == 0) {
    fail("peak_rss_kib is missing or zero");
  }
  if (rootCompressionSettings != file.GetCompressionSettings() ||
      rootCompressionAlgorithm != file.GetCompressionAlgorithm() ||
      rootCompressionLevel != file.GetCompressionLevel() ||
      rootCompressionAlgorithm < 0 || rootCompressionLevel < 0) {
    fail("ROOT compression metadata disagrees with the output file");
  }
  if (multiplicityOverflow != 0 || multiplicityWideOverflow != 0) {
    fail("multiplicity overflow is nonzero");
  }
  if (static_cast<unsigned long long>(multiplicity->GetEntries()) !=
          expectedSuccesses ||
      static_cast<unsigned long long>(
          multiplicityWideHistogram->GetEntries()) !=
          expectedSuccesses) {
    fail("multiplicity histogram entries do not equal successful events");
  }
  const double histogramSumWeights =
      multiplicity->Integral(0, multiplicity->GetNbinsX() + 1);
  double histogramSumWeights2 = 0.0;
  if (multiplicity->GetSumw2N() <= 0) {
    fail("multiplicity histogram lacks Sumw2");
  } else {
    for (int bin = 0; bin <= multiplicity->GetNbinsX() + 1; ++bin) {
      histogramSumWeights2 += multiplicity->GetSumw2()->At(bin);
    }
  }
  const auto approximatelyEqual = [](double left, double right) {
    return std::abs(left - right) <=
           1e-10 * std::max({1.0, std::abs(left), std::abs(right)});
  };
  if (!approximatelyEqual(histogramSumWeights, sumw) ||
      !approximatelyEqual(histogramSumWeights2, sumw2)) {
    fail("weighted multiplicity histogram does not close to metadata");
  }
  const double strongHistogramSumWeights =
      multiplicityWideHistogram->Integral(
          0, multiplicityWideHistogram->GetNbinsX() + 1);
  double strongHistogramSumWeights2 = 0.0;
  if (multiplicityWideHistogram->GetSumw2N() <= 0) {
    fail("strong/EM multiplicity histogram lacks Sumw2");
  } else {
    for (int bin = 0;
         bin <= multiplicityWideHistogram->GetNbinsX() + 1; ++bin) {
      strongHistogramSumWeights2 +=
          multiplicityWideHistogram->GetSumw2()->At(bin);
    }
  }
  if (!approximatelyEqual(strongHistogramSumWeights, sumw) ||
      !approximatelyEqual(strongHistogramSumWeights2, sumw2)) {
    fail("strong/EM multiplicity histogram does not close to metadata");
  }

  int stabilityPdg = 0, stabilityIsHadron = 0, stabilityIsMeson = 0;
  int stabilityIsBaryon = 0, stabilitySpinType = 0, stabilityCharge3 = 0;
  int stabilityNCharm = 0, stabilityNBeauty = 0, stabilityOpenHeavy = 0;
  int stabilityHiddenHeavy = 0, stabilityCentral = 0;
  int stabilityNc = 0, stabilityNcbar = 0, stabilityNb = 0;
  int stabilityNbbar = 0, stabilityQc = 0, stabilityQb = 0;
  int stabilityStrangeness = 0, stabilityHasAnti = 0;
  int stabilityAntiparticleVerified = 0;
  int stabilityCanDecay = 0, stabilityOriginalMayDecay = 0;
  int stabilityFinalMayDecay = 0;
  double stabilityMass = 0.0, stabilityTau0 = 0.0;
  std::string* stabilityName = nullptr;
  const std::vector<std::tuple<const char*, void*, const char*>>
      stabilityBranches = {
          {"pdg", &stabilityPdg, "Int_t"},
          {"name", &stabilityName, "string"},
          {"is_hadron", &stabilityIsHadron, "Int_t"},
          {"is_meson", &stabilityIsMeson, "Int_t"},
          {"is_baryon", &stabilityIsBaryon, "Int_t"},
          {"spin_type", &stabilitySpinType, "Int_t"},
          {"charge3", &stabilityCharge3, "Int_t"},
          {"n_charm", &stabilityNCharm, "Int_t"},
          {"n_beauty", &stabilityNBeauty, "Int_t"},
          {"n_c", &stabilityNc, "Int_t"},
          {"n_cbar", &stabilityNcbar, "Int_t"},
          {"n_b", &stabilityNb, "Int_t"},
          {"n_bbar", &stabilityNbbar, "Int_t"},
          {"q_c", &stabilityQc, "Int_t"},
          {"q_b", &stabilityQb, "Int_t"},
          {"strangeness", &stabilityStrangeness, "Int_t"},
          {"open_heavy", &stabilityOpenHeavy, "Int_t"},
          {"hidden_heavy", &stabilityHiddenHeavy, "Int_t"},
          {"central_registry", &stabilityCentral, "Int_t"},
          {"has_antiparticle", &stabilityHasAnti, "Int_t"},
          {"antiparticle_verified", &stabilityAntiparticleVerified, "Int_t"},
          {"mass", &stabilityMass, "Double_t"},
          {"tau0", &stabilityTau0, "Double_t"},
          {"can_decay", &stabilityCanDecay, "Int_t"},
          {"original_may_decay", &stabilityOriginalMayDecay, "Int_t"},
          {"final_may_decay", &stabilityFinalMayDecay, "Int_t"}};
  for (const auto& [name, address, expectedType] : stabilityBranches) {
    TBranch* branch = stability->GetBranch(name);
    const std::string className = branch ? branch->GetClassName() : "";
    TLeaf* leaf = branch ? branch->GetLeaf(name) : nullptr;
    const bool isString = std::string(expectedType) == "string";
    const bool correct =
        branch &&
        (isString
             ? (className == "string" || className == "std::string")
             : (className.empty() && leaf &&
                std::string(leaf->GetTypeName()) == expectedType &&
                leaf->GetLenStatic() == 1));
    if (!correct) {
      fail(std::string("missing/incorrectly typed heavy-stability branch ") +
           name);
    } else {
      stability->SetBranchAddress(name, address);
    }
  }
  std::ostringstream reconstructedStability;
  reconstructedStability.imbue(std::locale::classic());
  reconstructedStability
      << "schema=" << Hadronization::kHeavyStabilityAuditSchema << "\n"
      << std::scientific << std::setprecision(17);
  std::map<int, std::array<int, 5>> stabilitySignedContent;
  int previousStabilityPdg = std::numeric_limits<int>::min();
  for (Long64_t row = 0; row < stability->GetEntries(); ++row) {
    stability->GetEntry(row);
    if (!stabilityName) {
      fail("null heavy-stability particle name");
      continue;
    }
    reconstructedStability
        << stabilityPdg << '\t' << std::quoted(*stabilityName) << '\t'
        << stabilityIsHadron << '\t' << stabilityIsMeson << '\t'
        << stabilityIsBaryon << '\t' << stabilitySpinType << '\t'
        << stabilityCharge3 << '\t' << stabilityNCharm << '\t'
        << stabilityNBeauty << '\t' << stabilityNc << '\t'
        << stabilityNcbar << '\t' << stabilityNb << '\t'
        << stabilityNbbar << '\t' << stabilityQc << '\t' << stabilityQb
        << '\t' << stabilityStrangeness << '\t' << stabilityOpenHeavy
        << '\t' << stabilityHiddenHeavy << '\t' << stabilityCentral << '\t'
        << stabilityHasAnti << '\t' << stabilityAntiparticleVerified << '\t'
        << stabilityMass << '\t' << stabilityTau0 << '\t'
        << stabilityCanDecay << '\t' << stabilityOriginalMayDecay << '\t'
        << stabilityFinalMayDecay << '\n';
    if (stabilityFinalMayDecay != 0) {
      fail("heavy hadron remains decay enabled");
    }
    if (stabilityPdg <= previousStabilityPdg) {
      fail("heavy-stability rows are not strictly signed-PDG ordered");
    }
    previousStabilityPdg = stabilityPdg;
    if (stabilityIsHadron != 1 ||
        (stabilityNCharm <= 0 && stabilityNBeauty <= 0)) {
      fail("heavy-stability audit contains a non-heavy/non-hadron row");
    }
    const Hadronization::HeavyContent decoded =
        Hadronization::DecodeHeavyContent(
            stabilityPdg, stabilityIsMeson != 0,
            stabilityIsBaryon != 0);
    if (stabilityQc != stabilityNc - stabilityNcbar ||
        stabilityQb != stabilityNb - stabilityNbbar ||
        stabilityNc != decoded.nc ||
        stabilityNcbar != decoded.ncbar ||
        stabilityNb != decoded.nb ||
        stabilityNbbar != decoded.nbbar ||
        stabilityNCharm != stabilityNc + stabilityNcbar ||
        stabilityNBeauty != stabilityNb + stabilityNbbar ||
        stabilityStrangeness != decoded.strangeness() ||
        stabilityOpenHeavy !=
            ((decoded.qc() != 0 || decoded.qb() != 0) ? 1 : 0) ||
        stabilityHiddenHeavy !=
            ((decoded.hiddenCharm() || decoded.hiddenBeauty()) ? 1 : 0) ||
        stabilityCentral !=
            (Hadronization::FindGroundState(stabilityPdg) ? 1 : 0) ||
        (stabilityIsMeson != 0 && stabilityIsBaryon != 0) ||
        (stabilityHasAnti != 0 && stabilityHasAnti != 1) ||
        stabilityAntiparticleVerified != 1 ||
        (stabilityCanDecay != 0 && stabilityCanDecay != 1) ||
        (stabilityOriginalMayDecay != 0 &&
         stabilityOriginalMayDecay != 1) ||
        !std::isfinite(stabilityMass) || stabilityMass < 0.0 ||
        !std::isfinite(stabilityTau0) || stabilityTau0 < 0.0) {
      fail("heavy-stability quark-content/antiparticle audit failed");
    }
    if (!stabilitySignedContent
             .emplace(stabilityPdg,
                      std::array<int, 5>{stabilityQc, stabilityQb,
                                         stabilityCharge3,
                                         stabilityHasAnti,
                                         stabilitySpinType})
             .second) {
      fail("duplicate signed PDG in heavy-stability audit");
    }
  }
  stability->ResetBranchAddresses();
  for (const auto& [pdg, content] : stabilitySignedContent) {
    if (content[3] == 0) continue;
    const auto conjugate = stabilitySignedContent.find(-pdg);
    if (conjugate == stabilitySignedContent.end() ||
        conjugate->second[0] != -content[0] ||
        conjugate->second[1] != -content[1] ||
        conjugate->second[2] != -content[2]) {
      fail("heavy-stability antiparticle pair is incomplete/inconsistent");
    }
  }
  if (reconstructedStability.str() !=
          stabilityCanonical->GetString().Data() ||
      Hadronization::Sha256Hex(reconstructedStability.str()) !=
          stabilityAuditSha) {
    fail("heavy-stability tree/canonical digest mismatch");
  }

  int code = 0;
  unsigned long long count = 0;
  unsigned long long processTotal = 0;
  unsigned long long charmProcessTotal = 0;
  unsigned long long beautyProcessTotal = 0;
  std::set<int> observedProcessCodes;
  std::map<int, unsigned long long> recordedProcessCounts;
  TBranch* processCodeBranch = processCounts->GetBranch("code");
  TBranch* processCountBranch = processCounts->GetBranch("count");
  TLeaf* processCodeLeaf =
      processCodeBranch ? processCodeBranch->GetLeaf("code") : nullptr;
  TLeaf* processCountLeaf =
      processCountBranch ? processCountBranch->GetLeaf("count") : nullptr;
  if (!processCodeLeaf || !processCountLeaf ||
      std::string(processCodeLeaf->GetTypeName()) != "Int_t" ||
      std::string(processCountLeaf->GetTypeName()) != "ULong64_t") {
    fail("process_counts scalar branch types differ from contract");
  }
  processCounts->SetBranchAddress("code", &code);
  processCounts->SetBranchAddress("count", &count);
  for (Long64_t row = 0; row < processCounts->GetEntries(); ++row) {
    processCounts->GetEntry(row);
    processTotal += count;
    if (!observedProcessCodes.insert(code).second) {
      fail("duplicate process-code summary row");
    }
    recordedProcessCounts[code] = count;
    if (code == 121 || code == 122) {
      charmProcessTotal += count;
    } else if (code == 123 || code == 124) {
      beautyProcessTotal += count;
    } else {
      fail("unexpected PYTHIA hard-process code");
    }
  }
  if (processTotal != expectedSuccesses) fail("process-code counts do not sum to successes");
  if (charmProcessTotal == 0 || beautyProcessTotal == 0) {
    fail("combined-heavy sample lacks a hard charm or beauty channel");
  }

  std::string* effectiveSettingName = nullptr;
  std::string* effectiveSettingValue = nullptr;
  TBranch* effectiveNameBranch = effectiveSettings->GetBranch("name");
  TBranch* effectiveValueBranch = effectiveSettings->GetBranch("value");
  const auto isStringBranch = [](TBranch* branch) {
    if (!branch) return false;
    const std::string name = branch->GetClassName();
    return name == "string" || name == "std::string";
  };
  if (!isStringBranch(effectiveNameBranch) ||
      !isStringBranch(effectiveValueBranch)) {
    fail("effective-settings tree lacks name/value branches");
  } else {
    effectiveSettings->SetBranchAddress("name", &effectiveSettingName);
    effectiveSettings->SetBranchAddress("value", &effectiveSettingValue);
    std::ostringstream reconstructedSettings;
    reconstructedSettings.imbue(std::locale::classic());
    reconstructedSettings << "schema="
                          << Hadronization::kEffectiveSettingsSchema << "\n";
    std::set<std::string> settingNames;
    std::map<std::string, std::string> settingValues;
    for (Long64_t row = 0; row < effectiveSettings->GetEntries(); ++row) {
      effectiveSettings->GetEntry(row);
      if (!effectiveSettingName || !effectiveSettingValue ||
          effectiveSettingName->empty() ||
          !settingNames.insert(*effectiveSettingName).second) {
        fail("invalid or duplicate effective-setting row");
        continue;
      }
      settingValues.emplace(*effectiveSettingName, *effectiveSettingValue);
      reconstructedSettings << std::quoted(*effectiveSettingName) << '\t'
                            << std::quoted(*effectiveSettingValue) << '\n';
    }
    effectiveSettings->ResetBranchAddresses();
    std::set<std::string> expectedSettingNames;
    for (const std::string_view name :
         Hadronization::kAuditedPythiaSettingKeys) {
      expectedSettingNames.emplace(name);
    }
    if (!std::includes(settingNames.begin(), settingNames.end(),
                       expectedSettingNames.begin(),
                       expectedSettingNames.end())) {
      fail("exhaustive settings snapshot omits a generated audit key");
    }
    const auto parseIntegerSetting =
        [&](const char* name, unsigned long long expected) {
          const auto found = settingValues.find(name);
          if (found == settingValues.end()) return false;
          std::size_t consumed = 0;
          try {
            const unsigned long long value =
                std::stoull(found->second, &consumed);
            return consumed == found->second.size() && value == expected;
          } catch (const std::exception&) {
            return false;
          }
        };
    const auto parseDoubleSetting =
        [&](const char* name, double expected) {
          const auto found = settingValues.find(name);
          if (found == settingValues.end()) return false;
          std::size_t consumed = 0;
          try {
            const double value = std::stod(found->second, &consumed);
            const double tolerance =
                1e-12 * std::max({1.0, std::abs(value),
                                  std::abs(expected)});
            return consumed == found->second.size() &&
                   std::isfinite(value) &&
                   std::abs(value - expected) <= tolerance;
          } catch (const std::exception&) {
            return false;
          }
        };
    if (settingValues["Random:setSeed"] != "true" ||
        settingValues["HardQCD:hardccbar"] != "true" ||
        settingValues["HardQCD:hardbbbar"] != "true" ||
        !parseIntegerSetting("Random:seed",
                             static_cast<unsigned long long>(seed)) ||
        !parseIntegerSetting("Main:numberOfEvents", requested) ||
        !parseDoubleSetting("PhaseSpace:pTHatMin",
                            phaseSpacePthatMin)) {
      fail("critical effective PYTHIA settings differ from job metadata");
    }
    if (reconstructedSettings.str() !=
            effectiveSettingsCanonical->GetString().Data() ||
        Hadronization::Sha256Hex(reconstructedSettings.str()) !=
            effectiveSettingsSha) {
      fail("effective-settings tree/canonical digest mismatch");
    }
  }

  const std::vector<std::tuple<const char*, const char*, int>>
      requiredEventScalars = {
          {"event_id", "ULong64_t", 1},
          {"process_code", "Int_t", 1},
          {"hard_channel", "Int_t", 1},
          {"event_weight", "Double_t", 1},
          {"pthat", "Double_t", 1},
          {"hard_scale", "Double_t", 1},
          {"n_mpi", "Int_t", 1},
          {"multiplicity_primary_charged_eta10_v1", "Int_t", 1},
          {"multiplicity_primary_charged_eta40_v1", "Int_t", 1},
          {"multiplicity_central_by_species", "Int_t", 6},
          {"light_charge3_grid", "Short_t",
           Hadronization::kLightGridCells},
          {"light_baryon_grid", "Short_t",
           Hadronization::kLightGridCells},
          {"MULTIPLICITY", "Int_t", 1},
          {"PROCESSCODE", "Int_t", 1},
          {"NCHARM", "Int_t", 1},
          {"NBEAUTY", "Int_t", 1},
          {"NBC", "Int_t", 1},
          {"final_heavy_qc_sum", "Int_t", 1},
          {"final_heavy_qb_sum", "Int_t", 1},
          {"heavy_flavour_conservation_ok", "Int_t", 1},
          {"origin_classification_valid", "Int_t", 1},
          {"primary_all_heavy_match_valid", "Int_t", 1}};
  for (const auto& [name, expectedType, expectedLength] :
       requiredEventScalars) {
    TBranch* branch = tree->GetBranch(name);
    TLeaf* leaf = branch ? branch->GetLeaf(name) : nullptr;
    if (!branch || !leaf || std::string(branch->GetClassName()).size() != 0U ||
        std::string(leaf->GetTypeName()) != expectedType ||
        leaf->GetLenStatic() != expectedLength) {
      fail(std::string("missing or incorrectly typed event scalar/array ") +
           name);
    }
  }

  const std::vector<const char*> requiredIntegerVectors = {
      "ID", "HFCLASS", "STATUS", "MOTHER", "MOTHERID",
      "heavyIndex", "heavyPdg", "heavyStatus", "heavyStatusAbs",
      "heavyIsFinal", "heavyIsMeson", "heavyIsBaryon", "heavyCharge3",
      "heavySpinType",
      "heavyMother1", "heavyMother2", "heavyDaughter1", "heavyDaughter2",
      "heavyMotherOffsets", "heavyMothers", "heavyNc", "heavyNcbar",
      "heavyNb", "heavyNbbar", "heavyQc", "heavyQb",
      "heavyBaryonNumber", "heavyStrangeness", "heavyCentral", "heavyOpen",
      "heavyHidden", "heavyStateCategory",
      "heavyOriginC", "heavyOriginB", "heavyMatchResolutionC",
      "heavyMatchResolutionB", "heavyMatchedHardC", "heavyMatchedHardB",
      "heavyRejectedHardC", "heavyRejectedHardB",
      "heavyOriginDepthC", "heavyOriginDepthB",
      "heavyConstituentOffsets", "heavyConstituentParentSlot",
      "heavyConstituentPdg", "heavyConstituentOrdinal",
      "heavyConstituentOrigin", "heavyConstituentMatchResolution",
      "heavyConstituentMatchedHard", "heavyConstituentRejectedHard",
      "heavyConstituentOriginDepth",
      "hard_indices", "hard_bottom_indices", "hard_ids",
      "hard_status", "hard_bottom_ids", "hard_bottom_status",
      "ancestryIndex", "ancestryPdg", "ancestryStatus", "ancestryMother1",
      "ancestryMother2", "ancestryMotherOffsets", "ancestryMothers",
      "multAuditParticleIndex", "multAuditPdg", "multAuditStatus",
      "multAuditIsHeavy"};
  for (const char* name : requiredIntegerVectors) {
    TBranch* branch = tree->GetBranch(name);
    if (!branch || std::string(branch->GetClassName()) != "vector<int>") {
      fail(std::string("missing or non-integer vector branch ") + name);
    }
  }
  const std::vector<const char*> requiredDoubleVectors = {
      "heavyPx", "heavyPy", "heavyPz", "heavyE", "heavyPt",
      "heavyEta", "heavyY", "heavyPhi", "heavyMass", "multAuditPt",
      "multAuditEta", "hard_px", "hard_py", "hard_pz", "hard_e"};
  for (const char* name : requiredDoubleVectors) {
    TBranch* branch = tree->GetBranch(name);
    if (!branch || std::string(branch->GetClassName()) != "vector<double>") {
      fail(std::string("missing or non-double vector branch ") + name);
    }
  }
  if (errors || !exhaustive) {
    std::cout << "RAW_VALIDATION_SUMMARY errors=" << errors
              << " exhaustive=" << exhaustive << "\n";
    return errors;
  }

  ULong64_t eventId = 0;
  Int_t processCodeEvent = 0;
  Int_t hardChannelEvent = 0;
  Double_t eventWeight = 0.0;
  Double_t eventPthat = 0.0;
  Double_t eventHardScale = 0.0;
  Int_t eventNMpi = 0;
  Int_t multiplicityCentral = 0;
  Int_t multiplicityWide = 0;
  Int_t finalHeavyQcSumEvent = 0;
  Int_t finalHeavyQbSumEvent = 0;
  Int_t heavyFlavourConservationOkEvent = 0;
  Int_t originClassificationValidEvent = 0;
  Int_t primaryAllHeavyMatchValidEvent = 0;
  Int_t multiplicityCentralBySpecies[
      Hadronization::kMultiplicitySpeciesBuckets] = {0, 0, 0, 0, 0, 0};
  std::vector<int>* heavyPdg = nullptr;
  std::vector<int>* heavyIndex = nullptr;
  std::vector<int>* heavyStatus = nullptr;
  std::vector<int>* heavyStatusAbs = nullptr;
  std::vector<int>* heavyIsFinal = nullptr;
  std::vector<int>* heavyIsMeson = nullptr;
  std::vector<int>* heavyIsBaryon = nullptr;
  std::vector<int>* heavyCharge3 = nullptr;
  std::vector<int>* heavySpinType = nullptr;
  std::vector<int>* heavyMother1 = nullptr;
  std::vector<int>* heavyMother2 = nullptr;
  std::vector<int>* heavyDaughter1 = nullptr;
  std::vector<int>* heavyDaughter2 = nullptr;
  std::vector<int>* heavyCentral = nullptr;
  std::vector<int>* heavyOpen = nullptr;
  std::vector<int>* heavyHidden = nullptr;
  std::vector<int>* heavyStateCategory = nullptr;
  std::vector<int>* heavyQc = nullptr;
  std::vector<int>* heavyQb = nullptr;
  std::vector<int>* heavyNc = nullptr;
  std::vector<int>* heavyNcbar = nullptr;
  std::vector<int>* heavyNb = nullptr;
  std::vector<int>* heavyNbbar = nullptr;
  std::vector<int>* heavyBaryonNumber = nullptr;
  std::vector<int>* heavyStrangeness = nullptr;
  std::vector<int>* heavyOriginC = nullptr;
  std::vector<int>* heavyOriginB = nullptr;
  std::vector<int>* heavyMatchResolutionC = nullptr;
  std::vector<int>* heavyMatchResolutionB = nullptr;
  std::vector<int>* heavyMatchedHardC = nullptr;
  std::vector<int>* heavyMatchedHardB = nullptr;
  std::vector<int>* heavyRejectedHardC = nullptr;
  std::vector<int>* heavyRejectedHardB = nullptr;
  std::vector<int>* heavyOriginDepthC = nullptr;
  std::vector<int>* heavyOriginDepthB = nullptr;
  std::vector<int>* hardIndices = nullptr;
  std::vector<int>* hardBottomIndices = nullptr;
  std::vector<int>* hardIds = nullptr;
  std::vector<int>* hardStatus = nullptr;
  std::vector<int>* hardBottomIds = nullptr;
  std::vector<int>* hardBottomStatus = nullptr;
  std::vector<double>* hardPx = nullptr;
  std::vector<double>* hardPy = nullptr;
  std::vector<double>* hardPz = nullptr;
  std::vector<double>* hardE = nullptr;
  std::vector<int>* heavyMotherOffsets = nullptr;
  std::vector<int>* heavyMothers = nullptr;
  std::vector<int>* heavyConstituentOffsets = nullptr;
  std::vector<int>* heavyConstituentParentSlot = nullptr;
  std::vector<int>* heavyConstituentPdg = nullptr;
  std::vector<int>* heavyConstituentOrdinal = nullptr;
  std::vector<int>* heavyConstituentOrigin = nullptr;
  std::vector<int>* heavyConstituentMatchResolution = nullptr;
  std::vector<int>* heavyConstituentMatchedHard = nullptr;
  std::vector<int>* heavyConstituentRejectedHard = nullptr;
  std::vector<int>* heavyConstituentOriginDepth = nullptr;
  std::vector<int>* ancestryIndex = nullptr;
  std::vector<int>* ancestryPdg = nullptr;
  std::vector<int>* ancestryStatus = nullptr;
  std::vector<int>* ancestryMother1 = nullptr;
  std::vector<int>* ancestryMother2 = nullptr;
  std::vector<int>* ancestryMotherOffsets = nullptr;
  std::vector<int>* ancestryMothers = nullptr;
  std::vector<int>* multAuditParticleIndex = nullptr;
  std::vector<int>* multAuditPdg = nullptr;
  std::vector<int>* multAuditStatus = nullptr;
  std::vector<int>* multAuditIsHeavy = nullptr;
  std::vector<double>* multAuditPt = nullptr;
  std::vector<double>* multAuditEta = nullptr;
  std::vector<double>* heavyPt = nullptr;
  std::vector<double>* heavyEta = nullptr;
  std::vector<double>* heavyPx = nullptr;
  std::vector<double>* heavyPy = nullptr;
  std::vector<double>* heavyPz = nullptr;
  std::vector<double>* heavyE = nullptr;
  std::vector<double>* heavyY = nullptr;
  std::vector<double>* heavyPhi = nullptr;
  std::vector<double>* heavyMass = nullptr;
  tree->SetBranchAddress("event_id", &eventId);
  tree->SetBranchAddress("process_code", &processCodeEvent);
  tree->SetBranchAddress("hard_channel", &hardChannelEvent);
  tree->SetBranchAddress("event_weight", &eventWeight);
  tree->SetBranchAddress("pthat", &eventPthat);
  tree->SetBranchAddress("hard_scale", &eventHardScale);
  tree->SetBranchAddress("n_mpi", &eventNMpi);
  tree->SetBranchAddress("multiplicity_primary_charged_eta10_v1",
                         &multiplicityCentral);
  tree->SetBranchAddress("multiplicity_primary_charged_eta40_v1",
                         &multiplicityWide);
  tree->SetBranchAddress("final_heavy_qc_sum", &finalHeavyQcSumEvent);
  tree->SetBranchAddress("final_heavy_qb_sum", &finalHeavyQbSumEvent);
  tree->SetBranchAddress("heavy_flavour_conservation_ok",
                         &heavyFlavourConservationOkEvent);
  tree->SetBranchAddress("origin_classification_valid",
                         &originClassificationValidEvent);
  tree->SetBranchAddress("primary_all_heavy_match_valid",
                         &primaryAllHeavyMatchValidEvent);
  tree->SetBranchAddress("multiplicity_central_by_species",
                         multiplicityCentralBySpecies);
  tree->SetBranchAddress("heavyPdg", &heavyPdg);
  tree->SetBranchAddress("heavyIndex", &heavyIndex);
  tree->SetBranchAddress("heavyStatus", &heavyStatus);
  tree->SetBranchAddress("heavyStatusAbs", &heavyStatusAbs);
  tree->SetBranchAddress("heavyIsFinal", &heavyIsFinal);
  tree->SetBranchAddress("heavyIsMeson", &heavyIsMeson);
  tree->SetBranchAddress("heavyIsBaryon", &heavyIsBaryon);
  tree->SetBranchAddress("heavyCharge3", &heavyCharge3);
  tree->SetBranchAddress("heavySpinType", &heavySpinType);
  tree->SetBranchAddress("heavyMother1", &heavyMother1);
  tree->SetBranchAddress("heavyMother2", &heavyMother2);
  tree->SetBranchAddress("heavyDaughter1", &heavyDaughter1);
  tree->SetBranchAddress("heavyDaughter2", &heavyDaughter2);
  tree->SetBranchAddress("heavyCentral", &heavyCentral);
  tree->SetBranchAddress("heavyOpen", &heavyOpen);
  tree->SetBranchAddress("heavyHidden", &heavyHidden);
  tree->SetBranchAddress("heavyStateCategory", &heavyStateCategory);
  tree->SetBranchAddress("heavyQc", &heavyQc);
  tree->SetBranchAddress("heavyQb", &heavyQb);
  tree->SetBranchAddress("heavyNc", &heavyNc);
  tree->SetBranchAddress("heavyNcbar", &heavyNcbar);
  tree->SetBranchAddress("heavyNb", &heavyNb);
  tree->SetBranchAddress("heavyNbbar", &heavyNbbar);
  tree->SetBranchAddress("heavyBaryonNumber", &heavyBaryonNumber);
  tree->SetBranchAddress("heavyStrangeness", &heavyStrangeness);
  tree->SetBranchAddress("heavyOriginC", &heavyOriginC);
  tree->SetBranchAddress("heavyOriginB", &heavyOriginB);
  tree->SetBranchAddress("heavyMatchResolutionC", &heavyMatchResolutionC);
  tree->SetBranchAddress("heavyMatchResolutionB", &heavyMatchResolutionB);
  tree->SetBranchAddress("heavyMatchedHardC", &heavyMatchedHardC);
  tree->SetBranchAddress("heavyMatchedHardB", &heavyMatchedHardB);
  tree->SetBranchAddress("heavyRejectedHardC", &heavyRejectedHardC);
  tree->SetBranchAddress("heavyRejectedHardB", &heavyRejectedHardB);
  tree->SetBranchAddress("heavyOriginDepthC", &heavyOriginDepthC);
  tree->SetBranchAddress("heavyOriginDepthB", &heavyOriginDepthB);
  tree->SetBranchAddress("hard_indices", &hardIndices);
  tree->SetBranchAddress("hard_bottom_indices", &hardBottomIndices);
  tree->SetBranchAddress("hard_ids", &hardIds);
  tree->SetBranchAddress("hard_status", &hardStatus);
  tree->SetBranchAddress("hard_bottom_ids", &hardBottomIds);
  tree->SetBranchAddress("hard_bottom_status", &hardBottomStatus);
  tree->SetBranchAddress("hard_px", &hardPx);
  tree->SetBranchAddress("hard_py", &hardPy);
  tree->SetBranchAddress("hard_pz", &hardPz);
  tree->SetBranchAddress("hard_e", &hardE);
  tree->SetBranchAddress("heavyMotherOffsets", &heavyMotherOffsets);
  tree->SetBranchAddress("heavyMothers", &heavyMothers);
  tree->SetBranchAddress("heavyConstituentOffsets",
                         &heavyConstituentOffsets);
  tree->SetBranchAddress("heavyConstituentParentSlot",
                         &heavyConstituentParentSlot);
  tree->SetBranchAddress("heavyConstituentPdg", &heavyConstituentPdg);
  tree->SetBranchAddress("heavyConstituentOrdinal",
                         &heavyConstituentOrdinal);
  tree->SetBranchAddress("heavyConstituentOrigin",
                         &heavyConstituentOrigin);
  tree->SetBranchAddress("heavyConstituentMatchResolution",
                         &heavyConstituentMatchResolution);
  tree->SetBranchAddress("heavyConstituentMatchedHard",
                         &heavyConstituentMatchedHard);
  tree->SetBranchAddress("heavyConstituentRejectedHard",
                         &heavyConstituentRejectedHard);
  tree->SetBranchAddress("heavyConstituentOriginDepth",
                         &heavyConstituentOriginDepth);
  tree->SetBranchAddress("ancestryIndex", &ancestryIndex);
  tree->SetBranchAddress("ancestryPdg", &ancestryPdg);
  tree->SetBranchAddress("ancestryStatus", &ancestryStatus);
  tree->SetBranchAddress("ancestryMother1", &ancestryMother1);
  tree->SetBranchAddress("ancestryMother2", &ancestryMother2);
  tree->SetBranchAddress("ancestryMotherOffsets", &ancestryMotherOffsets);
  tree->SetBranchAddress("ancestryMothers", &ancestryMothers);
  tree->SetBranchAddress("multAuditParticleIndex",
                         &multAuditParticleIndex);
  tree->SetBranchAddress("multAuditPdg", &multAuditPdg);
  tree->SetBranchAddress("multAuditStatus", &multAuditStatus);
  tree->SetBranchAddress("multAuditIsHeavy", &multAuditIsHeavy);
  tree->SetBranchAddress("multAuditPt", &multAuditPt);
  tree->SetBranchAddress("multAuditEta", &multAuditEta);
  tree->SetBranchAddress("heavyPt", &heavyPt);
  tree->SetBranchAddress("heavyEta", &heavyEta);
  tree->SetBranchAddress("heavyPx", &heavyPx);
  tree->SetBranchAddress("heavyPy", &heavyPy);
  tree->SetBranchAddress("heavyPz", &heavyPz);
  tree->SetBranchAddress("heavyE", &heavyE);
  tree->SetBranchAddress("heavyY", &heavyY);
  tree->SetBranchAddress("heavyPhi", &heavyPhi);
  tree->SetBranchAddress("heavyMass", &heavyMass);

  std::set<ULong64_t> eventIds;
  unsigned long long unresolvedCharmTriggerCandidates = 0;
  unsigned long long unresolvedBeautyTriggerCandidates = 0;
  unsigned long long resolvedNonhardCharmTriggerCandidates = 0;
  unsigned long long resolvedNonhardBeautyTriggerCandidates = 0;
  unsigned long long observedDuplicateDemotionsC = 0;
  unsigned long long observedDuplicateDemotionsB = 0;
  unsigned long long observedDuplicateGroupsC = 0;
  unsigned long long observedDuplicateGroupsB = 0;
  unsigned long long observedMultiHeavyRejectionsC = 0;
  unsigned long long observedMultiHeavyRejectionsB = 0;
  unsigned long long observedConservationFailures = 0;
  unsigned long long observedClassificationFailures = 0;
  unsigned long long observedPrimaryAllHeavyFailures = 0;
  unsigned long long observedPrimaryAllHeavyConflictGroups = 0;
  unsigned long long observedPrimaryAllHeavyDemotions = 0;
  unsigned long long observedMultiplicityOverflow = 0;
  unsigned long long observedMultiplicityWideOverflow = 0;
  double observedSumWeights = 0.0;
  double observedSumWeights2 = 0.0;
  std::map<int, unsigned long long> observedProcessCounts;
  const int centralMultiplicityBins = multiplicity->GetNbinsX();
  const int wideMultiplicityBins =
      multiplicityWideHistogram->GetNbinsX();
  if (centralMultiplicityBins < 1 || wideMultiplicityBins < 1) {
    fail("multiplicity histograms have no regular bins");
    return errors;
  }
  const std::size_t centralMultiplicityStorageSize =
      static_cast<std::size_t>(centralMultiplicityBins) + 2U;
  const std::size_t wideMultiplicityStorageSize =
      static_cast<std::size_t>(wideMultiplicityBins) + 2U;
  std::vector<double> observedMultiplicityBinSumW(
      centralMultiplicityStorageSize, 0.0);
  std::vector<double> observedMultiplicityBinSumW2(
      centralMultiplicityStorageSize, 0.0);
  std::vector<double> observedWideBinSumW(
      wideMultiplicityStorageSize, 0.0);
  std::vector<double> observedWideBinSumW2(
      wideMultiplicityStorageSize, 0.0);
  for (Long64_t entry = 0; entry < tree->GetEntries(); ++entry) {
    tree->GetEntry(entry);
    if (!eventIds.insert(eventId).second) fail("duplicate event ID");
    const int expectedHardChannel =
        (processCodeEvent == 121 || processCodeEvent == 122)
            ? 4
            : ((processCodeEvent == 123 || processCodeEvent == 124) ? 5 : 0);
    if (expectedHardChannel == 0 ||
        hardChannelEvent != expectedHardChannel) {
      fail("event process code and hard-flavour channel disagree");
    }
    try {
      const ULong64_t expectedEventId = Hadronization::EventId(
          campaignOrdinal, Hadronization::TuneOrdinal(tune), logicalId,
          attempt, static_cast<std::uint64_t>(entry));
      if (eventId != expectedEventId) {
        fail("event ID does not match campaign/tune/logical/attempt mapping");
      }
    } catch (const std::exception&) {
      fail("event-ID metadata fields are outside the declared bit contract");
    }
    if (!std::isfinite(eventWeight)) {
      fail("non-finite event weight");
    } else {
      observedSumWeights += eventWeight;
      observedSumWeights2 += eventWeight * eventWeight;
      ++observedProcessCounts[processCodeEvent];
      const int directBin = multiplicity->FindFixBin(multiplicityCentral);
      const int strongBin =
          multiplicityWideHistogram->FindFixBin(multiplicityWide);
      if (directBin < 0 ||
          directBin >= static_cast<int>(observedMultiplicityBinSumW.size()) ||
          strongBin < 0 ||
          strongBin >= static_cast<int>(observedWideBinSumW.size())) {
        fail("ROOT multiplicity bin lookup returned an invalid bin");
      } else {
        const std::size_t directBinIndex =
            static_cast<std::size_t>(directBin);
        const std::size_t strongBinIndex =
            static_cast<std::size_t>(strongBin);
        observedMultiplicityBinSumW[directBinIndex] += eventWeight;
        observedMultiplicityBinSumW2[directBinIndex] +=
            eventWeight * eventWeight;
        observedWideBinSumW[strongBinIndex] += eventWeight;
        observedWideBinSumW2[strongBinIndex] +=
            eventWeight * eventWeight;
      }
      if (multiplicityCentral < 0 ||
          multiplicityCentral > multiplicity->GetNbinsX() - 1) {
        ++observedMultiplicityOverflow;
      }
      if (multiplicityWide < 0 ||
          multiplicityWide >
              multiplicityWideHistogram->GetNbinsX() - 1) {
        ++observedMultiplicityWideOverflow;
      }
    }
    if (!std::isfinite(eventPthat) || !std::isfinite(eventHardScale) ||
        eventPthat + 1e-12 < phaseSpacePthatMin || eventNMpi < 0) {
      fail("invalid event hard-scale/pTHat/MPI metadata");
    }
    int centralComponentSum = 0;
    for (int species = 0;
         species < Hadronization::kMultiplicitySpeciesBuckets; ++species) {
      centralComponentSum += multiplicityCentralBySpecies[species];
    }
    if (centralComponentSum != multiplicityCentral) {
      fail("multiplicity component sum mismatch");
    }
    if (multiplicityCentral > multiplicityWide) {
      fail("central multiplicity window exceeds the wider window");
    }
    // Pilot-only independent recomputation. The flat record lists every
    // final charged particle, so both counters follow from it alone. The
    // live-generator test Validation/TestPrimaryChargedDefinition.C proves
    // separately that the record is complete.
    const std::size_t auditSize = multAuditPdg ? multAuditPdg->size() : 0;
    const bool auditSizesMatch =
        multAuditPdg && multAuditParticleIndex &&
        multAuditParticleIndex->size() == auditSize &&
        multAuditStatus && multAuditStatus->size() == auditSize &&
        multAuditIsHeavy && multAuditIsHeavy->size() == auditSize &&
        multAuditPt && multAuditPt->size() == auditSize &&
        multAuditEta && multAuditEta->size() == auditSize;
    if (!auditSizesMatch) {
      fail("multiplicity audit vector-size mismatch");
    } else if (static_cast<unsigned long long>(entry) <
               multiplicityAuditEvents) {
      int auditCentral = 0;
      int auditWide = 0;
      std::array<int, Hadronization::kMultiplicitySpeciesBuckets>
          auditCentralBySpecies{{0, 0, 0, 0, 0, 0}};
      int previousIndex = -1;
      for (std::size_t row = 0; row < auditSize; ++row) {
        const int particleIndex = (*multAuditParticleIndex)[row];
        if (particleIndex <= previousIndex) {
          fail("multiplicity audit rows are not strictly index-ordered");
        }
        previousIndex = particleIndex;
        const int isHeavy = (*multAuditIsHeavy)[row];
        if (isHeavy != 0 && isHeavy != 1) {
          fail("multiplicity audit heavy flag is not boolean");
          continue;
        }
        if (Hadronization::CountsNchPrimaryChargedV1(
                true, true, isHeavy != 0, (*multAuditPt)[row],
                (*multAuditEta)[row],
                Hadronization::kMultiplicityEtaCentral)) {
          ++auditCentral;
          ++auditCentralBySpecies[static_cast<std::size_t>(
              Hadronization::MultiplicitySpeciesIndex(
                  std::abs((*multAuditPdg)[row])))];
        }
        if (Hadronization::CountsNchPrimaryChargedV1(
                true, true, isHeavy != 0, (*multAuditPt)[row],
                (*multAuditEta)[row],
                Hadronization::kMultiplicityEtaWide)) {
          ++auditWide;
        }
      }
      if (auditCentral != multiplicityCentral ||
          auditWide != multiplicityWide) {
        fail("independent pilot multiplicity recomputation mismatch");
      }
      for (int species = 0;
           species < Hadronization::kMultiplicitySpeciesBuckets; ++species) {
        if (auditCentralBySpecies[static_cast<std::size_t>(species)] !=
            multiplicityCentralBySpecies[species]) {
          fail("independent pilot multiplicity species recomputation "
               "mismatch");
        }
      }
    } else if (auditSize != 0 ||
               (multAuditParticleIndex &&
                !multAuditParticleIndex->empty())) {
      fail("multiplicity audit data present beyond declared pilot range");
    }
    std::map<int, int> hardByIndex;
    std::set<int> hardIdSigns;
    const std::size_t hardSize = hardIndices ? hardIndices->size() : 0;
    const bool hardSizesMatch =
        hardBottomIndices && hardBottomIndices->size() == hardSize &&
        hardIds && hardIds->size() == hardSize &&
        hardStatus && hardStatus->size() == hardSize &&
        hardBottomIds && hardBottomIds->size() == hardSize &&
        hardBottomStatus && hardBottomStatus->size() == hardSize &&
        hardPx && hardPx->size() == hardSize &&
        hardPy && hardPy->size() == hardSize &&
        hardPz && hardPz->size() == hardSize &&
        hardE && hardE->size() == hardSize;
    if (!hardSizesMatch) {
      fail("per-event hard-parton vector lengths are inconsistent");
      continue;
    }
    for (std::size_t hard = 0; hard < hardSize; ++hard) {
      if ((*hardIndices)[hard] < 0 || (*hardBottomIndices)[hard] < 0 ||
          (std::abs((*hardIds)[hard]) != 4 &&
           std::abs((*hardIds)[hard]) != 5) ||
          std::abs((*hardStatus)[hard]) != 23 ||
          !std::isfinite((*hardPx)[hard]) ||
          !std::isfinite((*hardPy)[hard]) ||
          !std::isfinite((*hardPz)[hard]) ||
          !std::isfinite((*hardE)[hard]) ||
          (*hardBottomStatus)[hard] == 0) {
        fail("invalid hard-parton record");
      }
      if (!hardByIndex.emplace((*hardIndices)[hard], (*hardIds)[hard]).second) {
        fail("duplicate hard-parton root index");
      }
      hardIdSigns.insert((*hardIds)[hard]);
    }
    const int expectedHardFlavour = hardChannelEvent;
    if (hardSize != 2U ||
        hardIdSigns.size() != 2U ||
        hardIdSigns.count(expectedHardFlavour) != 1U ||
        hardIdSigns.count(-expectedHardFlavour) != 1U ||
        std::any_of(hardIdSigns.begin(), hardIdSigns.end(),
                    [expectedHardFlavour](int id) {
                      return std::abs(id) != expectedHardFlavour;
                    })) {
      fail("hard-parton list does not match the selected process channel");
    }

    const std::size_t size = heavyPdg ? heavyPdg->size() : 0;
    const bool sizesMatch =
        heavyIndex && heavyIndex->size() == size &&
        heavyStatus && heavyStatus->size() == size &&
        heavyStatusAbs && heavyStatusAbs->size() == size &&
        heavyIsFinal && heavyIsFinal->size() == size &&
        heavyIsMeson && heavyIsMeson->size() == size &&
        heavyIsBaryon && heavyIsBaryon->size() == size &&
        heavyCharge3 && heavyCharge3->size() == size &&
        heavySpinType && heavySpinType->size() == size &&
        heavyMother1 && heavyMother1->size() == size &&
        heavyMother2 && heavyMother2->size() == size &&
        heavyDaughter1 && heavyDaughter1->size() == size &&
        heavyDaughter2 && heavyDaughter2->size() == size &&
        heavyCentral && heavyCentral->size() == size &&
        heavyOpen && heavyOpen->size() == size &&
        heavyHidden && heavyHidden->size() == size &&
        heavyStateCategory && heavyStateCategory->size() == size &&
        heavyQc && heavyQc->size() == size &&
        heavyQb && heavyQb->size() == size &&
        heavyNc && heavyNc->size() == size &&
        heavyNcbar && heavyNcbar->size() == size &&
        heavyNb && heavyNb->size() == size &&
        heavyNbbar && heavyNbbar->size() == size &&
        heavyBaryonNumber && heavyBaryonNumber->size() == size &&
        heavyStrangeness && heavyStrangeness->size() == size &&
        heavyOriginC && heavyOriginC->size() == size &&
        heavyOriginB && heavyOriginB->size() == size &&
        heavyMatchResolutionC && heavyMatchResolutionC->size() == size &&
        heavyMatchResolutionB && heavyMatchResolutionB->size() == size &&
        heavyMatchedHardC && heavyMatchedHardC->size() == size &&
        heavyMatchedHardB && heavyMatchedHardB->size() == size &&
        heavyRejectedHardC && heavyRejectedHardC->size() == size &&
        heavyRejectedHardB && heavyRejectedHardB->size() == size &&
        heavyOriginDepthC && heavyOriginDepthC->size() == size &&
        heavyOriginDepthB && heavyOriginDepthB->size() == size &&
        heavyPx && heavyPx->size() == size &&
        heavyPy && heavyPy->size() == size &&
        heavyPz && heavyPz->size() == size &&
        heavyE && heavyE->size() == size &&
        heavyPt && heavyPt->size() == size &&
        heavyEta && heavyEta->size() == size &&
        heavyY && heavyY->size() == size &&
        heavyPhi && heavyPhi->size() == size &&
        heavyMass && heavyMass->size() == size &&
        heavyMotherOffsets && heavyMotherOffsets->size() == size + 1 &&
        heavyMotherOffsets && !heavyMotherOffsets->empty() &&
        heavyMothers &&
        static_cast<std::size_t>(heavyMotherOffsets->back()) ==
            heavyMothers->size() &&
        heavyConstituentOffsets &&
        heavyConstituentOffsets->size() == size + 1 &&
        !heavyConstituentOffsets->empty() &&
        heavyConstituentParentSlot && heavyConstituentPdg &&
        heavyConstituentOrdinal && heavyConstituentOrigin &&
        heavyConstituentMatchResolution && heavyConstituentMatchedHard &&
        heavyConstituentRejectedHard && heavyConstituentOriginDepth &&
        heavyConstituentParentSlot->size() ==
            heavyConstituentPdg->size() &&
        heavyConstituentOrdinal->size() == heavyConstituentPdg->size() &&
        heavyConstituentOrigin->size() == heavyConstituentPdg->size() &&
        heavyConstituentMatchResolution->size() ==
            heavyConstituentPdg->size() &&
        heavyConstituentMatchedHard->size() ==
            heavyConstituentPdg->size() &&
        heavyConstituentRejectedHard->size() ==
            heavyConstituentPdg->size() &&
        heavyConstituentOriginDepth->size() ==
            heavyConstituentPdg->size() &&
        static_cast<std::size_t>(heavyConstituentOffsets->back()) ==
            heavyConstituentPdg->size() &&
        ancestryIndex && ancestryPdg &&
        ancestryIndex->size() == ancestryPdg->size() &&
        ancestryStatus && ancestryIndex->size() == ancestryStatus->size() &&
        ancestryMother1 && ancestryIndex->size() == ancestryMother1->size() &&
        ancestryMother2 && ancestryIndex->size() == ancestryMother2->size() &&
        ancestryMotherOffsets &&
        ancestryMotherOffsets->size() == ancestryIndex->size() + 1 &&
        !ancestryMotherOffsets->empty() && ancestryMothers &&
        static_cast<std::size_t>(ancestryMotherOffsets->back()) ==
            ancestryMothers->size();
    if (!sizesMatch) {
      fail("per-event heavy vector lengths are inconsistent");
      continue;
    }
    if (heavyMotherOffsets->front() != 0) {
      fail("heavy-mother offsets do not start at zero");
    }
    if (heavyConstituentOffsets->front() != 0 ||
        ancestryMotherOffsets->front() != 0) {
      fail("constituent/ancestry offsets do not start at zero");
    }
    for (std::size_t offset = 1; offset < heavyMotherOffsets->size();
         ++offset) {
      if ((*heavyMotherOffsets)[offset] < 0 ||
          (*heavyMotherOffsets)[offset] <
              (*heavyMotherOffsets)[offset - 1]) {
        fail("heavy-mother offsets are not monotonic");
      }
    }
    for (std::size_t offset = 1;
         offset < heavyConstituentOffsets->size(); ++offset) {
      if ((*heavyConstituentOffsets)[offset] < 0 ||
          (*heavyConstituentOffsets)[offset] <
              (*heavyConstituentOffsets)[offset - 1]) {
        fail("heavy-constituent offsets are not monotonic");
      }
    }
    for (std::size_t offset = 1;
         offset < ancestryMotherOffsets->size(); ++offset) {
      if ((*ancestryMotherOffsets)[offset] < 0 ||
          (*ancestryMotherOffsets)[offset] <
              (*ancestryMotherOffsets)[offset - 1]) {
        fail("ancestry-mother offsets are not monotonic");
      }
    }
    std::map<int, StoredAncestor> storedAncestry;
    for (std::size_t node = 0; node < ancestryIndex->size(); ++node) {
      const int begin = (*ancestryMotherOffsets)[node];
      const int end = (*ancestryMotherOffsets)[node + 1];
      if (begin < 0 || end < begin ||
          static_cast<std::size_t>(end) > ancestryMothers->size()) {
        fail("stored ancestry complete-mother segment is invalid");
        continue;
      }
      std::vector<int> completeMothers(
          ancestryMothers->begin() + begin, ancestryMothers->begin() + end);
      if (std::any_of(completeMothers.begin(), completeMothers.end(),
                      [](int mother) { return mother <= 0; }) ||
          std::adjacent_find(completeMothers.begin(),
                             completeMothers.end()) !=
              completeMothers.end() ||
          !std::is_sorted(completeMothers.begin(),
                          completeMothers.end())) {
        fail("stored ancestry complete-mother list is invalid");
      }
      for (const int endpoint :
           {(*ancestryMother1)[node], (*ancestryMother2)[node]}) {
        if (endpoint > 0 &&
            !std::binary_search(completeMothers.begin(),
                                completeMothers.end(), endpoint)) {
          fail("ancestry endpoint is absent from complete-mother list");
        }
      }
      if ((*ancestryIndex)[node] <= 0 ||
          !storedAncestry
               .emplace((*ancestryIndex)[node],
                        StoredAncestor{(*ancestryPdg)[node],
                                       (*ancestryStatus)[node],
                                       (*ancestryMother1)[node],
                                       (*ancestryMother2)[node],
                                       completeMothers})
               .second) {
        fail("invalid or duplicate stored ancestry index");
      }
    }
    for (std::size_t index = 0; index < size; ++index) {
      const int begin = (*heavyMotherOffsets)[index];
      const int end = (*heavyMotherOffsets)[index + 1];
      if (begin < 0 || end < begin ||
          static_cast<std::size_t>(end) > heavyMothers->size()) {
        fail("heavy-mother segment is outside flattened storage");
        continue;
      }
      std::set<int> uniqueMothers;
      const bool requiresOriginGraph =
          (*heavyNc)[index] + (*heavyNcbar)[index] +
              (*heavyNb)[index] + (*heavyNbbar)[index] >
          0;
      const std::size_t beginIndex = static_cast<std::size_t>(begin);
      const std::size_t endIndex = static_cast<std::size_t>(end);
      for (std::size_t position = beginIndex; position < endIndex;
           ++position) {
        const int mother = (*heavyMothers)[position];
        if (mother <= 0 || mother == (*heavyIndex)[index] ||
            !uniqueMothers.insert(mother).second ||
            (requiresOriginGraph &&
             storedAncestry.count(mother) == 0)) {
          fail("heavy complete-mother list is invalid or unauditable");
        }
      }
      for (const int endpoint :
           {(*heavyMother1)[index], (*heavyMother2)[index]}) {
        if (endpoint > 0 &&
            (!uniqueMothers.count(endpoint) ||
             (requiresOriginGraph &&
              storedAncestry.count(endpoint) == 0))) {
          fail("heavy direct-mother endpoint is absent from complete audit");
        }
      }
    }
    std::vector<int> reconstructedOriginC(size);
    std::vector<int> reconstructedOriginB(size);
    std::vector<int> reconstructedResolutionC(size);
    std::vector<int> reconstructedResolutionB(size);
    std::vector<int> reconstructedMatchedC(size);
    std::vector<int> reconstructedMatchedB(size);
    std::vector<int> reconstructedRejectedC(size, -1);
    std::vector<int> reconstructedRejectedB(size, -1);
    std::vector<int> reconstructedDepthC(size);
    std::vector<int> reconstructedDepthB(size);
    for (std::size_t index = 0; index < size; ++index) {
      std::vector<int> allMothers;
      const int begin = (*heavyMotherOffsets)[index];
      const int end = (*heavyMotherOffsets)[index + 1];
      if (begin >= 0 && end >= begin &&
          static_cast<std::size_t>(end) <= heavyMothers->size()) {
        allMothers.insert(allMothers.end(), heavyMothers->begin() + begin,
                          heavyMothers->begin() + end);
      }
      allMothers.push_back((*heavyMother1)[index]);
      allMothers.push_back((*heavyMother2)[index]);
      allMothers.erase(
          std::remove_if(allMothers.begin(), allMothers.end(),
                         [](int mother) { return mother <= 0; }),
          allMothers.end());
      std::sort(allMothers.begin(), allMothers.end());
      allMothers.erase(std::unique(allMothers.begin(), allMothers.end()),
                       allMothers.end());
      const int charmSign =
          (*heavyQc)[index] > 0 ? 1 : ((*heavyQc)[index] < 0 ? -1 : 0);
      const int beautySign =
          (*heavyQb)[index] > 0 ? 1 : ((*heavyQb)[index] < 0 ? -1 : 0);
      const ReconstructedOrigin charm = ReconstructOrigin(
          storedAncestry, allMothers, 4, charmSign, hardByIndex);
      const ReconstructedOrigin beauty = ReconstructOrigin(
          storedAncestry, allMothers, 5, beautySign, hardByIndex);
      reconstructedOriginC[index] = charm.origin;
      reconstructedResolutionC[index] = charm.resolution;
      reconstructedMatchedC[index] = charm.matchedHard;
      reconstructedDepthC[index] = charm.depth;
      reconstructedOriginB[index] = beauty.origin;
      reconstructedResolutionB[index] = beauty.resolution;
      reconstructedMatchedB[index] = beauty.matchedHard;
      reconstructedDepthB[index] = beauty.depth;
    }
    const std::vector<int> preUniquenessMatchedC = reconstructedMatchedC;
    const std::vector<int> preUniquenessMatchedB = reconstructedMatchedB;
    Hadronization::EnforceUniqueFinalHardCarrier(
        *heavyIsFinal, *heavyQc, reconstructedOriginC,
        reconstructedResolutionC, reconstructedMatchedC);
    Hadronization::EnforceUniqueFinalHardCarrier(
        *heavyIsFinal, *heavyQb, reconstructedOriginB,
        reconstructedResolutionB, reconstructedMatchedB);
    for (std::size_t index = 0; index < size; ++index) {
      if (reconstructedResolutionC[index] ==
          static_cast<int>(
              Hadronization::MatchResolution::kDuplicateHardCarrier)) {
        reconstructedRejectedC[index] = preUniquenessMatchedC[index];
      }
      if (reconstructedResolutionB[index] ==
          static_cast<int>(
              Hadronization::MatchResolution::kDuplicateHardCarrier)) {
        reconstructedRejectedB[index] = preUniquenessMatchedB[index];
      }
    }
    Hadronization::RejectFinalMultiHeavyCarrier(
        *heavyIsFinal, *heavyQc, reconstructedOriginC,
        reconstructedResolutionC, reconstructedMatchedC,
        reconstructedRejectedC);
    Hadronization::RejectFinalMultiHeavyCarrier(
        *heavyIsFinal, *heavyQb, reconstructedOriginB,
        reconstructedResolutionB, reconstructedMatchedB,
        reconstructedRejectedB);
    if (reconstructedOriginC != *heavyOriginC ||
        reconstructedOriginB != *heavyOriginB ||
        reconstructedResolutionC != *heavyMatchResolutionC ||
        reconstructedResolutionB != *heavyMatchResolutionB ||
        reconstructedMatchedC != *heavyMatchedHardC ||
        reconstructedMatchedB != *heavyMatchedHardB ||
        reconstructedRejectedC != *heavyRejectedHardC ||
        reconstructedRejectedB != *heavyRejectedHardB ||
        reconstructedDepthC != *heavyOriginDepthC ||
        reconstructedDepthB != *heavyOriginDepthB) {
      fail("stored origin classification is not exactly reproducible from "
           "the retained ancestry graph");
    }

    const std::size_t constituentSize = heavyConstituentPdg->size();
    std::vector<int> reconstructedConstituentOrigin(constituentSize);
    std::vector<int> reconstructedConstituentResolution(constituentSize);
    std::vector<int> reconstructedConstituentMatched(constituentSize);
    std::vector<int> reconstructedConstituentRejected(constituentSize, -1);
    std::vector<int> reconstructedConstituentDepth(constituentSize);
    std::vector<int> constituentParentIsFinal(constituentSize, 0);
    std::size_t expectedConstituentTotal = 0;
    bool reconstructedAllHeavyValid = true;
    for (std::size_t parent = 0; parent < size; ++parent) {
      const int begin = (*heavyConstituentOffsets)[parent];
      const int end = (*heavyConstituentOffsets)[parent + 1];
      const int expectedCount =
          (*heavyNc)[parent] + (*heavyNcbar)[parent] +
          (*heavyNb)[parent] + (*heavyNbbar)[parent];
      if (begin < 0 || end < begin ||
          static_cast<std::size_t>(end) > constituentSize ||
          end - begin != expectedCount ||
          static_cast<std::size_t>(begin) != expectedConstituentTotal) {
        fail("heavy constituent offsets/counts are inconsistent");
        reconstructedAllHeavyValid = false;
        continue;
      }
      expectedConstituentTotal += static_cast<std::size_t>(expectedCount);
      std::vector<int> allMothers(
          heavyMothers->begin() + (*heavyMotherOffsets)[parent],
          heavyMothers->begin() + (*heavyMotherOffsets)[parent + 1]);
      std::size_t position = static_cast<std::size_t>(begin);
      const std::size_t endIndex = static_cast<std::size_t>(end);
      const std::array<std::pair<int, int>, 4> expectedConstituents{{
          {4, (*heavyNc)[parent]},
          {-4, (*heavyNcbar)[parent]},
          {5, (*heavyNb)[parent]},
          {-5, (*heavyNbbar)[parent]},
      }};
      for (const auto& [signedFlavour, countForSign] :
           expectedConstituents) {
        for (int ordinal = 0; ordinal < countForSign;
             ++ordinal, ++position) {
          if (position >= endIndex ||
              (*heavyConstituentParentSlot)[position] !=
                  static_cast<int>(parent) ||
              (*heavyConstituentPdg)[position] != signedFlavour ||
              (*heavyConstituentOrdinal)[position] != ordinal) {
            fail("flattened constituent identity/order is inconsistent");
            reconstructedAllHeavyValid = false;
            continue;
          }
          const ReconstructedOrigin reconstructed = ReconstructOrigin(
              storedAncestry, allMothers, std::abs(signedFlavour),
              signedFlavour > 0 ? 1 : -1, hardByIndex);
          reconstructedConstituentOrigin[position] = reconstructed.origin;
          reconstructedConstituentResolution[position] =
              reconstructed.resolution;
          reconstructedConstituentMatched[position] =
              reconstructed.matchedHard;
          reconstructedConstituentDepth[position] = reconstructed.depth;
          constituentParentIsFinal[position] = (*heavyIsFinal)[parent];
        }
      }
    }
    if (expectedConstituentTotal != constituentSize) {
      fail("heavy constituent offsets do not cover flattened rows exactly");
      reconstructedAllHeavyValid = false;
    }
    const Hadronization::CarrierUniquenessResult reconstructedUniqueness =
        Hadronization::EnforceUniqueFinalConstituentHardCarrier(
            *heavyConstituentParentSlot, constituentParentIsFinal,
            *heavyConstituentPdg,
            reconstructedConstituentOrigin,
            reconstructedConstituentResolution,
            reconstructedConstituentMatched,
            reconstructedConstituentRejected);
    observedPrimaryAllHeavyConflictGroups +=
        reconstructedUniqueness.conflictGroups;
    observedPrimaryAllHeavyDemotions +=
        reconstructedUniqueness.demotedMatches;
    if (reconstructedConstituentOrigin != *heavyConstituentOrigin ||
        reconstructedConstituentResolution !=
            *heavyConstituentMatchResolution ||
        reconstructedConstituentMatched !=
            *heavyConstituentMatchedHard ||
        reconstructedConstituentRejected !=
            *heavyConstituentRejectedHard ||
        reconstructedConstituentDepth !=
            *heavyConstituentOriginDepth) {
      fail("constituent-level primary-all-heavy matches are not exactly "
           "reproducible from complete ancestry");
      reconstructedAllHeavyValid = false;
    }
    std::map<int, int> selectedFinalConstituentParent;
    for (std::size_t constituent = 0; constituent < constituentSize;
         ++constituent) {
      const int parentSlot = (*heavyConstituentParentSlot)[constituent];
      const int signedFlavour = (*heavyConstituentPdg)[constituent];
      const int origin = (*heavyConstituentOrigin)[constituent];
      const int resolution =
          (*heavyConstituentMatchResolution)[constituent];
      const int matched = (*heavyConstituentMatchedHard)[constituent];
      const int rejected = (*heavyConstituentRejectedHard)[constituent];
      if ((std::abs(signedFlavour) != 4 &&
           std::abs(signedFlavour) != 5) ||
          (origin == static_cast<int>(Hadronization::Origin::kSelectedHard) &&
           (resolution != static_cast<int>(
                              Hadronization::MatchResolution::kUnique) ||
            matched < 0 || rejected != -1)) ||
          (origin != static_cast<int>(Hadronization::Origin::kSelectedHard) &&
           matched != -1) ||
          (origin == static_cast<int>(Hadronization::Origin::kUnresolved) &&
           resolution == static_cast<int>(
                             Hadronization::MatchResolution::kUnique))) {
        reconstructedAllHeavyValid = false;
      }
      if (matched >= 0) {
        const auto found = hardByIndex.find(matched);
        bool distinctParentConflict = false;
        if (constituentParentIsFinal[constituent]) {
          const auto [claim, inserted] =
              selectedFinalConstituentParent.emplace(matched, parentSlot);
          distinctParentConflict = !inserted && claim->second != parentSlot;
        }
        if (found == hardByIndex.end() || found->second != signedFlavour ||
            distinctParentConflict) {
          reconstructedAllHeavyValid = false;
        }
      }
      if (rejected >= 0) {
        const auto found = hardByIndex.find(rejected);
        if (found == hardByIndex.end() ||
            found->second != signedFlavour ||
            resolution != static_cast<int>(
                              Hadronization::MatchResolution::
                                  kDuplicateHardCarrier)) {
          reconstructedAllHeavyValid = false;
        }
      }
    }
    const int expectedPrimaryAllHeavyValid =
        reconstructedAllHeavyValid ? 1 : 0;
    if (primaryAllHeavyMatchValidEvent != expectedPrimaryAllHeavyValid) {
      fail("primary-all-heavy event validity flag differs from reconstruction");
    }
    if (!expectedPrimaryAllHeavyValid) {
      ++observedPrimaryAllHeavyFailures;
      fail("primary-all-heavy event match invariant failed");
    }

    std::set<int> selectedFinalHardC;
    std::set<int> selectedFinalHardB;
    std::map<int, std::size_t> duplicateClaimsC;
    std::map<int, std::size_t> duplicateClaimsB;
    std::set<int> eventHeavyIndices;
    int observedFinalQcSum = 0;
    int observedFinalQbSum = 0;
    for (std::size_t index = 0; index < size; ++index) {
      if ((*heavyIndex)[index] < 0 ||
          !eventHeavyIndices.insert((*heavyIndex)[index]).second) {
        fail("invalid or duplicate heavy event-record index");
      }
      if (((*heavyIsFinal)[index] != 0 && (*heavyIsFinal)[index] != 1) ||
          ((*heavyIsMeson)[index] != 0 && (*heavyIsMeson)[index] != 1) ||
          ((*heavyIsBaryon)[index] != 0 &&
           (*heavyIsBaryon)[index] != 1) ||
          ((*heavyCentral)[index] != 0 && (*heavyCentral)[index] != 1) ||
          ((*heavyOpen)[index] != 0 && (*heavyOpen)[index] != 1) ||
          ((*heavyHidden)[index] != 0 && (*heavyHidden)[index] != 1)) {
        fail("non-boolean heavy classification flag");
      }
      if ((*heavyStatusAbs)[index] != std::abs((*heavyStatus)[index]) ||
          ((*heavyIsMeson)[index] != 0 &&
           (*heavyIsBaryon)[index] != 0)) {
        fail("heavy status or meson/baryon classification mismatch");
      }
      const Hadronization::HeavyContent decoded =
          Hadronization::DecodeHeavyContent(
              (*heavyPdg)[index], (*heavyIsMeson)[index] != 0,
              (*heavyIsBaryon)[index] != 0);
      const auto stabilityRow =
          stabilitySignedContent.find((*heavyPdg)[index]);
      const int expectedBaryonNumber =
          (*heavyIsBaryon)[index] != 0
              ? ((*heavyPdg)[index] > 0 ? 1 : -1)
              : 0;
      if (stabilityRow == stabilitySignedContent.end() ||
          stabilityRow->second[0] != decoded.qc() ||
          stabilityRow->second[1] != decoded.qb() ||
          stabilityRow->second[2] != (*heavyCharge3)[index] ||
          stabilityRow->second[4] != (*heavySpinType)[index] ||
          (*heavyNc)[index] != decoded.nc ||
          (*heavyNcbar)[index] != decoded.ncbar ||
          (*heavyNb)[index] != decoded.nb ||
          (*heavyNbbar)[index] != decoded.nbbar ||
          (*heavyStrangeness)[index] != decoded.strangeness() ||
          ((*heavyCentral)[index] != 0) !=
              (Hadronization::FindGroundState((*heavyPdg)[index]) != nullptr) ||
          (*heavyBaryonNumber)[index] != expectedBaryonNumber) {
        fail("stored heavy identity/content differs from audited ParticleData");
      }
      const int expectedStateCategory = static_cast<int>(
          Hadronization::ClassifyHeavyStateDetailed(
              (*heavyCentral)[index] != 0, decoded,
              (*heavyIsMeson)[index] != 0,
              (*heavySpinType)[index]));
      if ((*heavyStateCategory)[index] != expectedStateCategory ||
          (*heavySpinType)[index] <= 0 ||
          (*heavyNc)[index] < 0 || (*heavyNcbar)[index] < 0 ||
          (*heavyNb)[index] < 0 || (*heavyNbbar)[index] < 0 ||
          ((*heavyOpen)[index] != 0) !=
              ((*heavyQc)[index] != 0 || (*heavyQb)[index] != 0) ||
          (*heavyQc)[index] !=
              (*heavyNc)[index] - (*heavyNcbar)[index] ||
          (*heavyQb)[index] !=
              (*heavyNb)[index] - (*heavyNbbar)[index] ||
          (*heavyHidden)[index] !=
              (((*heavyNc)[index] > 0 && (*heavyNcbar)[index] > 0) ||
               ((*heavyNb)[index] > 0 && (*heavyNbbar)[index] > 0))) {
        fail("heavy state-category/open-content mismatch");
      }
      if (!std::isfinite((*heavyPx)[index]) ||
          !std::isfinite((*heavyPy)[index]) ||
          !std::isfinite((*heavyPz)[index]) ||
          !std::isfinite((*heavyE)[index]) ||
          !std::isfinite((*heavyPt)[index]) ||
          !std::isfinite((*heavyEta)[index]) ||
          !std::isfinite((*heavyY)[index]) ||
          !std::isfinite((*heavyPhi)[index]) ||
          !std::isfinite((*heavyMass)[index]) ||
          (*heavyE)[index] < 0.0 || (*heavyPt)[index] < 0.0 ||
          (*heavyMass)[index] < 0.0 ||
          std::abs((*heavyPhi)[index]) >
              3.14159265358979323846 + 1e-12) {
        fail("non-finite heavy-hadron kinematics");
      }
      const double reconstructedPt =
          std::hypot((*heavyPx)[index], (*heavyPy)[index]);
      const double ptScale =
          std::max({1.0, reconstructedPt, (*heavyPt)[index]});
      const double invariantMassSquared =
          (*heavyE)[index] * (*heavyE)[index] -
          (*heavyPx)[index] * (*heavyPx)[index] -
          (*heavyPy)[index] * (*heavyPy)[index] -
          (*heavyPz)[index] * (*heavyPz)[index];
      const double storedMassSquared =
          (*heavyMass)[index] * (*heavyMass)[index];
      const double massScale =
          std::max({1.0, std::abs(invariantMassSquared),
                    std::abs(storedMassSquared)});
      const double fourVectorScale =
          std::max({1.0, (*heavyE)[index] * (*heavyE)[index],
                    (*heavyPx)[index] * (*heavyPx)[index] +
                        (*heavyPy)[index] * (*heavyPy)[index] +
                        (*heavyPz)[index] * (*heavyPz)[index]});
      if (std::abs(reconstructedPt - (*heavyPt)[index]) >
              1e-10 * ptScale ||
          std::abs(invariantMassSquared - storedMassSquared) >
              1e-11 * fourVectorScale + 1e-8 * massScale) {
        fail("heavy-hadron four-vector/derived kinematics mismatch");
      }
      if ((*heavyIsFinal)[index]) {
        observedFinalQcSum += (*heavyQc)[index];
        observedFinalQbSum += (*heavyQb)[index];
      }
      const auto validateCarrier =
          [&](int charge, int origin, int resolution, int matchedHard,
              int rejectedHard, int flavour,
              std::set<int>& selectedFinalHard,
              std::map<int, std::size_t>& duplicateClaims,
              unsigned long long& observedDuplicateDemotions,
              unsigned long long& observedMultiHeavyRejections,
              const char* sector) {
            if (origin < static_cast<int>(Hadronization::Origin::kUnresolved) ||
                origin >
                    static_cast<int>(Hadronization::Origin::kOtherResolved)) {
              fail(std::string("origin enum outside contract in ") + sector);
            }
            if (resolution <
                    static_cast<int>(
                        Hadronization::MatchResolution::kNotApplicable) ||
                resolution >
                    static_cast<int>(
                        Hadronization::MatchResolution::
                            kMultipleHeavyConstituents)) {
              fail(std::string("resolution enum outside contract in ") +
                   sector);
            }
            if (charge == 0) {
              if (origin !=
                      static_cast<int>(Hadronization::Origin::kUnresolved) ||
                  resolution != static_cast<int>(
                                    Hadronization::MatchResolution::
                                        kNotApplicable) ||
                  matchedHard != -1 || rejectedHard != -1) {
                fail(std::string("non-applicable sector has origin claim in ") +
                     sector);
              }
              return;
            }
            const auto validateHard =
                [&](int hardIndex, const char* purpose) {
                  const auto found = hardByIndex.find(hardIndex);
                  if (hardIndex < 0 || found == hardByIndex.end()) {
                    fail(std::string("invalid ") + purpose +
                         " hard-carrier index in " + sector);
                    return false;
                  }
                  const int requiredId = charge > 0 ? flavour : -flavour;
                  if (found->second != requiredId) {
                    fail(std::string(purpose) +
                         " hard-carrier flavour/sign mismatch in " + sector);
                    return false;
                  }
                  return true;
                };
            if (matchedHard >= 0) validateHard(matchedHard, "matched");
            if (rejectedHard >= 0) validateHard(rejectedHard, "rejected");

            const bool isFinal = (*heavyIsFinal)[index] != 0;
            const bool isMultiHeavy = std::abs(charge) > 1;
            if (isFinal && isMultiHeavy) {
              ++observedMultiHeavyRejections;
              if (origin !=
                      static_cast<int>(Hadronization::Origin::kUnresolved) ||
                  matchedHard != -1 ||
                  (resolution != static_cast<int>(
                                     Hadronization::MatchResolution::
                                         kMultipleHeavyConstituents) &&
                   resolution != static_cast<int>(
                                     Hadronization::MatchResolution::
                                         kDuplicateHardCarrier))) {
                fail(std::string("final multi-heavy carrier was not "
                                 "conservatively rejected in ") +
                     sector);
              }
            } else if (resolution ==
                       static_cast<int>(
                           Hadronization::MatchResolution::
                               kMultipleHeavyConstituents)) {
              fail(std::string("spurious multi-heavy rejection in ") +
                   sector);
            }

            if (resolution == static_cast<int>(
                                  Hadronization::MatchResolution::
                                      kDuplicateHardCarrier)) {
              ++observedDuplicateDemotions;
              if (!isFinal ||
                  origin !=
                      static_cast<int>(Hadronization::Origin::kUnresolved) ||
                  matchedHard != -1) {
                fail(std::string("invalid duplicate-carrier demotion in ") +
                     sector);
              }
              if (rejectedHard < 0) {
                fail(std::string("missing rejected hard carrier in ") +
                     sector);
              } else {
                ++duplicateClaims[rejectedHard];
              }
            } else if (rejectedHard != -1 &&
                       resolution !=
                           static_cast<int>(
                               Hadronization::MatchResolution::
                                   kMultipleHeavyConstituents)) {
              fail(std::string("spurious rejected hard carrier in ") +
                   sector);
            }
            if (origin ==
                static_cast<int>(Hadronization::Origin::kSelectedHard)) {
              if (resolution != static_cast<int>(
                                    Hadronization::MatchResolution::kUnique) ||
                  matchedHard < 0 || rejectedHard != -1 ||
                  (isFinal && isMultiHeavy)) {
                fail(std::string("invalid selected-hard metadata in ") +
                     sector);
              } else if (isFinal &&
                         !selectedFinalHard.insert(matchedHard).second) {
                fail(std::string("duplicate surviving selected hard carrier in ") +
                     sector);
              }
            } else if (matchedHard != -1) {
              fail(std::string("non-selected origin retains hard carrier in ") +
                   sector);
            }
            if (origin ==
                    static_cast<int>(Hadronization::Origin::kUnresolved) &&
                resolution ==
                    static_cast<int>(Hadronization::MatchResolution::kUnique)) {
              fail(std::string("unresolved origin marked uniquely resolved in ") +
                   sector);
            }
          };
      validateCarrier((*heavyQc)[index], (*heavyOriginC)[index],
                      (*heavyMatchResolutionC)[index],
                      (*heavyMatchedHardC)[index],
                      (*heavyRejectedHardC)[index], 4, selectedFinalHardC,
                      duplicateClaimsC, observedDuplicateDemotionsC,
                      observedMultiHeavyRejectionsC, "charm");
      validateCarrier((*heavyQb)[index], (*heavyOriginB)[index],
                      (*heavyMatchResolutionB)[index],
                      (*heavyMatchedHardB)[index],
                      (*heavyRejectedHardB)[index], 5, selectedFinalHardB,
                      duplicateClaimsB, observedDuplicateDemotionsB,
                      observedMultiHeavyRejectionsB, "beauty");
      if ((*heavyCentral)[index] && (*heavyIsFinal)[index] &&
          Hadronization::IsDirectPrimaryStatus((*heavyStatus)[index]) &&
          Hadronization::IsCentralKinematic((*heavyPt)[index],
                                            (*heavyEta)[index], true)) {
        const auto* state = Hadronization::FindGroundState((*heavyPdg)[index]);
        if (state && IsPublicationTrigger((*heavyPdg)[index]) &&
            state->sector == "charm" && (*heavyQc)[index] != 0) {
          if ((*heavyOriginC)[index] ==
                  static_cast<int>(Hadronization::Origin::kUnresolved) &&
              (*heavyMatchResolutionC)[index] ==
                  static_cast<int>(
                      Hadronization::MatchResolution::kUnique)) {
            fail("unresolved charm origin marked uniquely resolved");
          }
          if ((*heavyOriginC)[index] ==
              static_cast<int>(Hadronization::Origin::kUnresolved)) {
            ++unresolvedCharmTriggerCandidates;
          } else if ((*heavyOriginC)[index] !=
                     static_cast<int>(Hadronization::Origin::kSelectedHard)) {
            ++resolvedNonhardCharmTriggerCandidates;
          }
        }
        if (state && IsPublicationTrigger((*heavyPdg)[index]) &&
            state->sector == "beauty" && (*heavyQb)[index] != 0) {
          if ((*heavyOriginB)[index] ==
                  static_cast<int>(Hadronization::Origin::kUnresolved) &&
              (*heavyMatchResolutionB)[index] ==
                  static_cast<int>(
                      Hadronization::MatchResolution::kUnique)) {
            fail("unresolved beauty origin marked uniquely resolved");
          }
          if ((*heavyOriginB)[index] ==
              static_cast<int>(Hadronization::Origin::kUnresolved)) {
            ++unresolvedBeautyTriggerCandidates;
          } else if ((*heavyOriginB)[index] !=
                     static_cast<int>(Hadronization::Origin::kSelectedHard)) {
            ++resolvedNonhardBeautyTriggerCandidates;
          }
        }
      }
    }
    const auto validateDuplicateGroups =
        [&](const std::map<int, std::size_t>& claims,
            const std::set<int>& surviving, unsigned long long& observedGroups,
            const char* sector) {
          for (const auto& [hardIndex, claimCount] : claims) {
            ++observedGroups;
            if (claimCount < 2) {
              fail(std::string("duplicate-carrier group has fewer than two "
                               "claims in ") +
                   sector);
            }
            if (surviving.count(hardIndex) != 0) {
              fail(std::string("rejected duplicate carrier also survives in ") +
                   sector);
            }
          }
        };
    validateDuplicateGroups(duplicateClaimsC, selectedFinalHardC,
                            observedDuplicateGroupsC, "charm");
    validateDuplicateGroups(duplicateClaimsB, selectedFinalHardB,
                            observedDuplicateGroupsB, "beauty");
    const int expectedConservation =
        observedFinalQcSum == 0 && observedFinalQbSum == 0 ? 1 : 0;
    if (finalHeavyQcSumEvent != observedFinalQcSum ||
        finalHeavyQbSumEvent != observedFinalQbSum ||
        (heavyFlavourConservationOkEvent != 0 &&
         heavyFlavourConservationOkEvent != 1) ||
        heavyFlavourConservationOkEvent != expectedConservation) {
      fail("event heavy-flavour conservation record is inconsistent");
    }
    if (!expectedConservation) ++observedConservationFailures;
    if (originClassificationValidEvent != 1) {
      ++observedClassificationFailures;
      fail("event origin-classification invariant flag is not true");
    }
  }
  if (!approximatelyEqual(observedSumWeights, sumw) ||
      !approximatelyEqual(observedSumWeights2, sumw2)) {
    fail("tree event weights do not close independently to metadata");
  }
  if (observedProcessCounts != recordedProcessCounts) {
    fail("tree process counts do not match process_counts summary");
  }
  if (observedMultiplicityOverflow != multiplicityOverflow ||
      observedMultiplicityWideOverflow !=
          multiplicityWideOverflow) {
    fail("tree multiplicity overflows do not match metadata");
  }
  const auto compareHistogramBins =
      [&](TH1* histogram, const std::vector<double>& expectedSumW,
          const std::vector<double>& expectedSumW2, const char* label) {
        if (!histogram ||
            histogram->GetNbinsX() < 1) {
          fail(std::string(label) + " has no regular bins");
          return;
        }
        const std::size_t histogramStorageSize =
            static_cast<std::size_t>(histogram->GetNbinsX()) + 2U;
        if (expectedSumW.size() != histogramStorageSize ||
            expectedSumW2.size() != expectedSumW.size()) {
          fail(std::string(label) + " independent bin arrays are invalid");
          return;
        }
        for (int bin = 0; bin <= histogram->GetNbinsX() + 1; ++bin) {
          const std::size_t binIndex = static_cast<std::size_t>(bin);
          const double storedSumW = histogram->GetBinContent(bin);
          const double storedSumW2 =
              histogram->GetSumw2N() > 0
                  ? histogram->GetSumw2()->At(bin)
                  : std::numeric_limits<double>::quiet_NaN();
          if (!approximatelyEqual(storedSumW, expectedSumW[binIndex]) ||
              !approximatelyEqual(storedSumW2, expectedSumW2[binIndex])) {
            fail(std::string(label) +
                 " bin content/Sumw2 differs from event-tree reconstruction");
          }
        }
      };
  compareHistogramBins(multiplicity, observedMultiplicityBinSumW,
                       observedMultiplicityBinSumW2,
                       "hadronisation multiplicity");
  compareHistogramBins(multiplicityWideHistogram,
                       observedWideBinSumW,
                       observedWideBinSumW2,
                       "strong/EM multiplicity");
  if (static_cast<unsigned long long>(processHistogram->GetEntries()) !=
      expectedSuccesses) {
    fail("process histogram entries do not equal successful events");
  }
  for (int bin = 0; bin <= processHistogram->GetNbinsX() + 1; ++bin) {
    const int codeForBin =
        static_cast<int>(std::llround(processHistogram->GetBinCenter(bin)));
    const auto found = observedProcessCounts.find(codeForBin);
    const double expected =
        found == observedProcessCounts.end()
            ? 0.0
            : static_cast<double>(found->second);
    if (!approximatelyEqual(processHistogram->GetBinContent(bin), expected)) {
      fail("process histogram differs from event-tree reconstruction");
    }
  }
  if (observedDuplicateDemotionsC != duplicateDemotionsC ||
      observedDuplicateDemotionsB != duplicateDemotionsB ||
      observedDuplicateGroupsC != duplicateConflictGroupsC ||
      observedDuplicateGroupsB != duplicateConflictGroupsB) {
    fail("exact duplicate-carrier metadata reconstruction failed");
  }
  if (observedMultiHeavyRejectionsC != multiHeavyRejectionsC ||
      observedMultiHeavyRejectionsB != multiHeavyRejectionsB) {
    fail("exact multi-heavy rejection metadata reconstruction failed");
  }
  if (observedConservationFailures != conservationFailures ||
      observedClassificationFailures != classificationFailures ||
      observedPrimaryAllHeavyFailures != primaryAllHeavyFailures ||
      observedPrimaryAllHeavyConflictGroups !=
          primaryAllHeavyConflictGroups ||
      observedPrimaryAllHeavyDemotions != primaryAllHeavyDemotions) {
    fail("event invariant-failure totals do not match metadata");
  }
  std::cout << "RAW_ORIGIN_AUDIT unresolved_charm_trigger_candidates="
            << unresolvedCharmTriggerCandidates
            << " unresolved_beauty_trigger_candidates="
            << unresolvedBeautyTriggerCandidates
            << " resolved_nonhard_charm_trigger_candidates="
            << resolvedNonhardCharmTriggerCandidates
            << " resolved_nonhard_beauty_trigger_candidates="
            << resolvedNonhardBeautyTriggerCandidates
            << " duplicate_hard_carrier_groups_charm="
            << duplicateConflictGroupsC
            << " duplicate_hard_carrier_groups_beauty="
            << duplicateConflictGroupsB
            << " duplicate_hard_carrier_demotions_charm="
            << duplicateDemotionsC
            << " duplicate_hard_carrier_demotions_beauty="
            << duplicateDemotionsB
            << " multi_heavy_rejections_charm="
            << multiHeavyRejectionsC
            << " multi_heavy_rejections_beauty="
            << multiHeavyRejectionsB << "\n";
  std::cout << "RAW_VALIDATION_SUMMARY errors=" << errors
            << " entries=" << tree->GetEntries()
            << " process_codes=" << processCounts->GetEntries()
            << " stability_rows=" << stability->GetEntries() << "\n";
  return errors;
}
