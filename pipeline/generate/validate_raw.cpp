// Fail-closed validator for the frozen hf_primary_ground_raw_v7 interface.
#include "physics.hpp"
#include "sha256.hpp"
#include "study_contract.hpp"

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
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
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
  mothers.erase(std::remove_if(mothers.begin(), mothers.end(),
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
    const auto current = queue.front();
    queue.pop_front();
    const int index = current.first;
    const int depth = current.second;
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
    } else if (CarriesSignedHeavyConstituent(
                   node->second.pdg, flavour, requiredSign)) {
      starts.push_back(mother);
    }
  }
  std::sort(starts.begin(), starts.end());
  starts.erase(std::unique(starts.begin(), starts.end()), starts.end());
  if (starts.empty()) {
    return {static_cast<int>(Hadronization::Origin::kUnresolved),
            static_cast<int>(
                graphComplete ? Hadronization::MatchResolution::kMissingCarrier
                              : Hadronization::MatchResolution::kBrokenLineage),
            -1, -1};
  }

  std::vector<int> candidates = StoredNearestHeavyAncestors(
      ancestry, starts, flavour, requiredSign, graphComplete);
  int totalDepth = 1;
  std::set<int> lineageVisited;
  while (candidates.size() == 1U && totalDepth < 1000) {
    const int index = candidates.front();
    if (!lineageVisited.insert(index).second) {
      return {static_cast<int>(Hadronization::Origin::kUnresolved),
              static_cast<int>(Hadronization::MatchResolution::kBrokenLineage),
              -1, totalDepth};
    }
    const auto node = ancestry.find(index);
    if (node == ancestry.end()) {
      return {static_cast<int>(Hadronization::Origin::kUnresolved),
              static_cast<int>(Hadronization::MatchResolution::kBrokenLineage),
              -1, totalDepth};
    }
    const auto hard = hardByIndex.find(index);
    if (hard != hardByIndex.end() &&
        hard->second == requiredSign * flavour) {
      return {static_cast<int>(Hadronization::Origin::kSelectedHard),
              static_cast<int>(Hadronization::MatchResolution::kUnique), index,
              totalDepth};
    }
    candidates.clear();
    for (const int mother : StoredDirectMothers(ancestry, index)) {
      const auto parent = ancestry.find(mother);
      if (parent == ancestry.end()) {
        graphComplete = false;
      } else if (std::abs(parent->second.pdg) == flavour &&
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
                static_cast<int>(Hadronization::MatchResolution::kBrokenLineage),
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
              static_cast<int>(Hadronization::MatchResolution::kUnique), -1,
              totalDepth};
    }
    ++totalDepth;
  }
  return {static_cast<int>(Hadronization::Origin::kUnresolved),
          static_cast<int>(candidates.size() > 1U
                               ? Hadronization::MatchResolution::kAmbiguous
                               : Hadronization::MatchResolution::kBrokenLineage),
          -1, totalDepth};
}

struct Authorization {
  std::string path;
  std::string campaign;
  std::string tune;
  std::string configSha256;
  std::string executableSha256;
  std::string repositoryCommit;
  std::string pythiaVersion;
  int campaignOrdinal = -1;
  int logicalId = -1;
  int attempt = -1;
  int seed = -1;
  unsigned long long events = 0;
  double pthatMin = -1.0;
};

template <typename T>
bool ReadScalar(TTree* tree, const char* name, T& value) {
  TBranch* branch = tree ? tree->GetBranch(name) : nullptr;
  TLeaf* leaf = branch ? branch->GetLeaf(name) : nullptr;
  if (!leaf || std::string(branch->GetClassName()).size() != 0U) return false;
  const std::string type = leaf->GetTypeName();
  const bool correct =
      (std::is_same<T, int>::value && type == "Int_t") ||
      (std::is_same<T, unsigned long long>::value && type == "ULong64_t") ||
      (std::is_same<T, long long>::value && type == "Long64_t") ||
      (std::is_same<T, double>::value && type == "Double_t");
  if (!correct || leaf->GetLenStatic() != 1) return false;
  tree->SetBranchAddress(name, &value);
  const bool ok = tree->GetEntry(0) > 0;
  tree->ResetBranchAddresses();
  return ok;
}

bool ReadString(TTree* tree, const char* name, std::string& value) {
  TBranch* branch = tree ? tree->GetBranch(name) : nullptr;
  if (!branch) return false;
  const std::string type = branch->GetClassName();
  if (type != "string" && type != "std::string") return false;
  std::string* pointer = nullptr;
  tree->SetBranchAddress(name, &pointer);
  const bool ok = tree->GetEntry(0) > 0 && pointer != nullptr;
  if (ok) value = *pointer;
  tree->ResetBranchAddresses();
  return ok;
}

std::set<std::string> BranchNames(TTree* tree) {
  std::set<std::string> names;
  if (!tree) return names;
  const auto* branches = tree->GetListOfBranches();
  for (int index = 0; index < branches->GetEntries(); ++index) {
    names.insert(branches->At(index)->GetName());
  }
  return names;
}

template <std::size_t N>
void Add(std::set<std::string>& output, const std::array<const char*, N>& values) {
  output.insert(values.begin(), values.end());
}

bool Approximately(double left, double right) {
  return std::abs(left - right) <=
         1e-10 * std::max({1.0, std::abs(left), std::abs(right)});
}

Authorization Arguments(int argc, char** argv) {
  if (argc < 2) throw std::invalid_argument("usage: validate_raw FILE --key value ...");
  Authorization auth;
  auth.path = argv[1];
  std::map<std::string, std::string> values;
  for (int index = 2; index < argc; index += 2) {
    if (index + 1 >= argc || std::string(argv[index]).rfind("--", 0) != 0) {
      throw std::invalid_argument("validator options must be --key value pairs");
    }
    values.emplace(std::string(argv[index]).substr(2), argv[index + 1]);
  }
  const auto required = [&values](const std::string& name) {
    const auto found = values.find(name);
    if (found == values.end() || found->second.empty()) {
      throw std::invalid_argument("missing --" + name);
    }
    return found->second;
  };
  auth.campaign = required("campaign");
  auth.tune = required("tune");
  auth.configSha256 = required("config-sha256");
  auth.executableSha256 = required("executable-sha256");
  auth.repositoryCommit = required("repository-commit");
  auth.pythiaVersion = required("pythia-version");
  auth.campaignOrdinal = std::stoi(required("campaign-ordinal"));
  auth.logicalId = std::stoi(required("logical-id"));
  auth.attempt = std::stoi(required("attempt"));
  auth.seed = std::stoi(required("seed"));
  auth.events = std::stoull(required("events"));
  auth.pthatMin = std::stod(required("pthat-min"));
  if (values.size() != 12U) throw std::invalid_argument("unknown validator option");
  return auth;
}

int Validate(const Authorization& auth) {
  int errors = 0;
  const auto fail = [&errors](const std::string& message) {
    std::cerr << "RAW_VALIDATION_ERROR " << message << '\n';
    ++errors;
  };
  TFile file(auth.path.c_str(), "READ");
  if (file.IsZombie()) {
    fail("file is missing, zombie, or unreadable");
    return errors;
  }
  auto* tree = dynamic_cast<TTree*>(file.Get("tree"));
  auto* metadata = dynamic_cast<TTree*>(file.Get("job_metadata"));
  auto* stability = dynamic_cast<TTree*>(file.Get("heavy_stability_audit"));
  auto* processCounts = dynamic_cast<TTree*>(file.Get("process_counts"));
  auto* effectiveSettings = dynamic_cast<TTree*>(file.Get("effective_settings"));
  auto* multiplicity = dynamic_cast<TH1*>(file.Get("hMULTIPLICITY"));
  auto* multiplicityWide = dynamic_cast<TH1*>(file.Get("hMULTIPLICITY_ETA40"));
  auto* processHistogram = dynamic_cast<TH1*>(file.Get("hPROCESS_CODE"));
  auto* stabilityCanonical =
      dynamic_cast<TObjString*>(file.Get("heavy_stability_audit_canonical"));
  auto* stabilityDigest =
      dynamic_cast<TObjString*>(file.Get("heavy_stability_audit_sha256"));
  auto* settingsCanonical =
      dynamic_cast<TObjString*>(file.Get("effective_settings_canonical"));
  auto* settingsDigest =
      dynamic_cast<TObjString*>(file.Get("effective_settings_sha256"));
  auto* multiplicityCentralVersion =
      dynamic_cast<TObjString*>(file.Get("multiplicity_central_version"));
  auto* multiplicityWideVersion =
      dynamic_cast<TObjString*>(file.Get("multiplicity_crosscheck_version"));
  auto* multiplicityDefinitionObject =
      dynamic_cast<TObjString*>(file.Get("multiplicity_definition"));
  auto* primaryMatchVersion =
      dynamic_cast<TObjString*>(file.Get("primary_all_heavy_match_version"));
  if (!tree) fail("missing event tree");
  if (!metadata || metadata->GetEntries() != 1) fail("job_metadata must have one row");
  if (!stability || stability->GetEntries() <= 0) fail("missing heavy_stability_audit");
  if (!processCounts || processCounts->GetEntries() <= 0) fail("missing process_counts");
  if (!effectiveSettings || effectiveSettings->GetEntries() <= 0) fail("missing effective_settings");
  if (!multiplicity || !multiplicityWide || !processHistogram) fail("missing accounting histogram");
  if (!stabilityCanonical || !stabilityDigest || !settingsCanonical ||
      !settingsDigest) fail("missing audit digest object");
  if (!multiplicityCentralVersion || !multiplicityWideVersion ||
      !multiplicityDefinitionObject || !primaryMatchVersion) {
    fail("missing raw-v7 definition object");
  }
  if (errors != 0) return errors;

  const std::array<const char*, 22> scalarBranches{{
      "event_id", "process_code", "hard_channel", "event_weight", "pthat",
      "hard_scale", "n_mpi", "multiplicity_primary_charged_eta10_v1",
      "multiplicity_primary_charged_eta40_v1", "multiplicity_central_by_species",
      "light_charge3_grid", "light_baryon_grid", "MULTIPLICITY", "PROCESSCODE",
      "NCHARM", "NBEAUTY", "NBC", "final_heavy_qc_sum", "final_heavy_qb_sum",
      "heavy_flavour_conservation_ok", "origin_classification_valid",
      "primary_all_heavy_match_valid"}};
  const std::array<const char*, 68> integerVectors{{
      "ID", "HFCLASS", "STATUS", "MOTHER", "MOTHERID", "heavyIndex",
      "heavyPdg", "heavyStatus", "heavyStatusAbs", "heavyIsFinal",
      "heavyIsMeson", "heavyIsBaryon", "heavyCharge3", "heavySpinType",
      "heavyMother1", "heavyMother2", "heavyDaughter1", "heavyDaughter2",
      "heavyMotherOffsets", "heavyMothers", "heavyNc", "heavyNcbar", "heavyNb",
      "heavyNbbar", "heavyQc", "heavyQb", "heavyBaryonNumber",
      "heavyStrangeness", "heavyCentral", "heavyOpen", "heavyHidden",
      "heavyStateCategory", "heavyOriginC", "heavyOriginB",
      "heavyMatchResolutionC", "heavyMatchResolutionB", "heavyMatchedHardC",
      "heavyMatchedHardB", "heavyRejectedHardC", "heavyRejectedHardB",
      "heavyOriginDepthC", "heavyOriginDepthB", "heavyConstituentOffsets",
      "heavyConstituentParentSlot", "heavyConstituentPdg",
      "heavyConstituentOrdinal", "heavyConstituentOrigin",
      "heavyConstituentMatchResolution", "heavyConstituentMatchedHard",
      "heavyConstituentRejectedHard", "heavyConstituentOriginDepth",
      "hard_indices", "hard_bottom_indices", "hard_ids", "hard_status",
      "hard_bottom_ids", "hard_bottom_status", "ancestryIndex", "ancestryPdg",
      "ancestryStatus", "ancestryMother1", "ancestryMother2",
      "ancestryMotherOffsets", "ancestryMothers", "multAuditParticleIndex",
      "multAuditPdg", "multAuditStatus", "multAuditIsHeavy"}};
  const std::array<const char*, 15> doubleVectors{{
      "PT", "ETA", "Y", "PHI", "CHARGE", "heavyPx", "heavyPy", "heavyPz",
      "heavyE", "heavyPt", "heavyEta", "heavyY", "heavyPhi", "heavyMass",
      "multAuditPt"}};
  const std::array<const char*, 1> finalDoubleVector{{"multAuditEta"}};
  std::set<std::string> expectedTree;
  Add(expectedTree, scalarBranches);
  Add(expectedTree, integerVectors);
  Add(expectedTree, doubleVectors);
  Add(expectedTree, finalDoubleVector);
  const std::array<const char*, 4> hardDoubleVectors{{
      "hard_px", "hard_py", "hard_pz", "hard_e"}};
  Add(expectedTree, hardDoubleVectors);
  if (expectedTree.size() != 110U || BranchNames(tree) != expectedTree) {
    fail("event branch set is not the exact 110-branch raw-v7 interface");
  }
  const std::array<std::tuple<const char*, const char*, int>, 22> scalarTypes{{
      {"event_id", "ULong64_t", 1}, {"process_code", "Int_t", 1},
      {"hard_channel", "Int_t", 1}, {"event_weight", "Double_t", 1},
      {"pthat", "Double_t", 1}, {"hard_scale", "Double_t", 1},
      {"n_mpi", "Int_t", 1},
      {"multiplicity_primary_charged_eta10_v1", "Int_t", 1},
      {"multiplicity_primary_charged_eta40_v1", "Int_t", 1},
      {"multiplicity_central_by_species", "Int_t", 6},
      {"light_charge3_grid", "Short_t", Hadronization::kLightGridCells},
      {"light_baryon_grid", "Short_t", Hadronization::kLightGridCells},
      {"MULTIPLICITY", "Int_t", 1}, {"PROCESSCODE", "Int_t", 1},
      {"NCHARM", "Int_t", 1}, {"NBEAUTY", "Int_t", 1}, {"NBC", "Int_t", 1},
      {"final_heavy_qc_sum", "Int_t", 1}, {"final_heavy_qb_sum", "Int_t", 1},
      {"heavy_flavour_conservation_ok", "Int_t", 1},
      {"origin_classification_valid", "Int_t", 1},
      {"primary_all_heavy_match_valid", "Int_t", 1}}};
  for (const auto& spec : scalarTypes) {
    const char* name = std::get<0>(spec);
    TBranch* branch = tree->GetBranch(name);
    TLeaf* leaf = branch ? branch->GetLeaf(name) : nullptr;
    if (!leaf || std::string(branch->GetClassName()).size() != 0U ||
        leaf->GetTypeName() != std::string(std::get<1>(spec)) ||
        leaf->GetLenStatic() != std::get<2>(spec)) {
      fail(std::string("missing or incorrectly typed event branch ") + name);
    }
  }
  for (const std::string& name : expectedTree) {
    if (std::find(scalarBranches.begin(), scalarBranches.end(), name) !=
        scalarBranches.end()) continue;
    TBranch* branch = tree->GetBranch(name.c_str());
    const bool isDouble = (std::find(doubleVectors.begin(), doubleVectors.end(), name) !=
                           doubleVectors.end()) || name == "multAuditEta" ||
                          (std::find(hardDoubleVectors.begin(), hardDoubleVectors.end(), name) !=
                           hardDoubleVectors.end());
    const std::string expected = isDouble ? "vector<double>" : "vector<int>";
    if (!branch || branch->GetClassName() != expected) {
      fail("incorrect vector type for " + name);
    }
  }

  const std::array<const char*, 26> metadataStrings{{
      "campaign", "raw_schema", "selector", "origin_algorithm",
      "species_registry_schema", "species_registry_sha256",
      "multiplicity_definition", "light_compensation_grid_schema",
      "tune_difference_allowlist_schema", "tune_difference_allowlist_sha256",
      "heavy_stability_audit_schema", "heavy_stability_audit_sha256",
      "effective_settings_schema", "effective_settings_sha256",
      "primary_all_heavy_match_schema", "config_sha256", "executable_sha256",
      "repository_commit", "repository_dirty", "root_version", "pythia_version",
      "tune", "role", "host", "condor_cluster", "condor_process"}};
  const std::array<const char*, 8> metadataInts{{
      "campaign_ordinal", "logical_id", "attempt", "seed", "complete",
      "root_compression_settings", "root_compression_algorithm",
      "root_compression_level"}};
  const std::array<const char*, 22> metadataUnsigned{{
      "requested_successes", "attempts", "successful_events", "failed_attempts",
      "tree_entries", "multiplicity_overflow", "multiplicity_wide_overflow",
      "content_decode_failures", "duplicate_hard_carrier_conflict_groups_charm",
      "duplicate_hard_carrier_conflict_groups_beauty",
      "duplicate_hard_carrier_demotions_charm",
      "duplicate_hard_carrier_demotions_beauty",
      "multi_heavy_constituent_rejections_charm",
      "multi_heavy_constituent_rejections_beauty",
      "heavy_flavour_conservation_failures", "origin_classification_failures",
      "primary_all_heavy_conflict_groups", "primary_all_heavy_demotions",
      "primary_all_heavy_match_failures", "multiplicity_audit_events",
      "peak_rss_kib", "effective_settings_entries"}};
  const std::array<const char*, 3> metadataLong{{
      "start_unix_seconds", "end_unix_seconds", "elapsed_seconds"}};
  const std::array<const char*, 6> metadataDouble{{
      "sum_weights", "sum_weights2", "phase_space_pthat_min",
      "pythia_sigma_gen_mb", "pythia_sigma_err_mb", "pythia_weight_sum"}};
  std::set<std::string> expectedMetadata;
  Add(expectedMetadata, metadataStrings); Add(expectedMetadata, metadataInts);
  Add(expectedMetadata, metadataUnsigned); Add(expectedMetadata, metadataLong);
  Add(expectedMetadata, metadataDouble);
  if (expectedMetadata.size() != 65U || BranchNames(metadata) != expectedMetadata) {
    fail("metadata branch set is not the exact 65-branch raw-v7 interface");
  }
  for (const char* name : metadataStrings) {
    std::string unused;
    if (!ReadString(metadata, name, unused)) fail(std::string("bad string metadata ") + name);
  }
  for (const char* name : metadataInts) {
    int unused = 0; if (!ReadScalar(metadata, name, unused)) fail(std::string("bad Int_t metadata ") + name);
  }
  for (const char* name : metadataUnsigned) {
    unsigned long long unused = 0;
    if (!ReadScalar(metadata, name, unused)) fail(std::string("bad ULong64_t metadata ") + name);
  }
  for (const char* name : metadataLong) {
    long long unused = 0; if (!ReadScalar(metadata, name, unused)) fail(std::string("bad Long64_t metadata ") + name);
  }
  for (const char* name : metadataDouble) {
    double unused = 0; if (!ReadScalar(metadata, name, unused)) fail(std::string("bad Double_t metadata ") + name);
  }
  if (errors != 0) return errors;

  std::map<std::string, std::string> strings;
  for (const char* name : metadataStrings) ReadString(metadata, name, strings[name]);
  std::map<std::string, int> integers;
  for (const char* name : metadataInts) ReadScalar(metadata, name, integers[name]);
  std::map<std::string, unsigned long long> unsigneds;
  for (const char* name : metadataUnsigned) ReadScalar(metadata, name, unsigneds[name]);
  std::map<std::string, long long> longs;
  for (const char* name : metadataLong) ReadScalar(metadata, name, longs[name]);
  std::map<std::string, double> doubles;
  for (const char* name : metadataDouble) ReadScalar(metadata, name, doubles[name]);
  if (strings["campaign"] != auth.campaign || strings["tune"] != auth.tune ||
      integers["campaign_ordinal"] != auth.campaignOrdinal ||
      integers["logical_id"] != auth.logicalId || integers["attempt"] != auth.attempt ||
      integers["seed"] != auth.seed) fail("campaign/tune/logical/attempt/seed authorization mismatch");
  if (strings["config_sha256"] != auth.configSha256 ||
      strings["executable_sha256"] != auth.executableSha256 ||
      strings["repository_commit"] != auth.repositoryCommit ||
      strings["repository_dirty"] != "false") fail("config/executable/repository provenance mismatch");
  if (strings["raw_schema"] != Hadronization::kRawSchema ||
      strings["selector"] != Hadronization::kSelectorVersion ||
      strings["origin_algorithm"] != Hadronization::kOriginAlgorithmVersion ||
      strings["species_registry_schema"] != Hadronization::kSpeciesRegistrySchema ||
      strings["species_registry_sha256"] != Hadronization::kSpeciesRegistrySha256 ||
      strings["multiplicity_definition"] != Hadronization::kMultiplicityDefinitionVersion ||
      strings["light_compensation_grid_schema"] != Hadronization::kLightCompensationGridSchema ||
      strings["tune_difference_allowlist_schema"] != Hadronization::kTuneDifferenceAllowlistSchema ||
      strings["tune_difference_allowlist_sha256"] != Hadronization::kTuneDifferenceAllowlistSha256 ||
      strings["heavy_stability_audit_schema"] != Hadronization::kHeavyStabilityAuditSchema ||
      strings["effective_settings_schema"] != Hadronization::kEffectiveSettingsSchema ||
      strings["primary_all_heavy_match_schema"] != Hadronization::kPrimaryAllHeavyMatchSchema ||
      strings["role"] != "primary" || strings["pythia_version"].rfind(auth.pythiaVersion, 0) != 0) {
    fail("raw schema/selection/version definition mismatch");
  }
  if (unsigneds["requested_successes"] != auth.events ||
      unsigneds["successful_events"] != auth.events ||
      unsigneds["tree_entries"] != auth.events ||
      static_cast<unsigned long long>(tree->GetEntries()) != auth.events ||
      integers["complete"] != 1) fail("exact-success/tree-entry contract mismatch");
  if (unsigneds["attempts"] != unsigneds["successful_events"] +
      unsigneds["failed_attempts"]) fail("attempt accounting identity failed");
  if (!Approximately(doubles["phase_space_pthat_min"], auth.pthatMin) ||
      !std::isfinite(doubles["sum_weights"]) || !std::isfinite(doubles["sum_weights2"]) ||
      doubles["sum_weights2"] < 0.0 || doubles["pythia_sigma_gen_mb"] <= 0.0 ||
      doubles["pythia_sigma_err_mb"] < 0.0 || !std::isfinite(doubles["pythia_weight_sum"])) {
    fail("invalid normalization or phase-space metadata");
  }
  const std::array<const char*, 6> zeroCounters{{
      "content_decode_failures",
      "heavy_flavour_conservation_failures", "origin_classification_failures",
      "primary_all_heavy_match_failures", "primary_all_heavy_conflict_groups",
      "primary_all_heavy_demotions"}};
  for (const char* name : zeroCounters) if (unsigneds[name] != 0ULL) fail(std::string("nonzero validity counter ") + name);
  if (longs["start_unix_seconds"] <= 0 || longs["end_unix_seconds"] < longs["start_unix_seconds"] ||
      longs["elapsed_seconds"] < 0 ||
      std::llabs((longs["end_unix_seconds"] - longs["start_unix_seconds"]) - longs["elapsed_seconds"]) > 1) {
    fail("invalid runtime accounting");
  }
  if (integers["root_compression_settings"] != file.GetCompressionSettings() ||
      integers["root_compression_algorithm"] != file.GetCompressionAlgorithm() ||
      integers["root_compression_level"] != file.GetCompressionLevel()) fail("compression metadata mismatch");
  if (std::string(multiplicityCentralVersion->GetString().Data()) != Hadronization::kMultiplicityCentral ||
      std::string(multiplicityWideVersion->GetString().Data()) != Hadronization::kMultiplicityCrossCheck ||
      std::string(multiplicityDefinitionObject->GetString().Data()) != Hadronization::kMultiplicityDefinitionVersion ||
      std::string(primaryMatchVersion->GetString().Data()) != Hadronization::kPrimaryAllHeavyMatchSchema) {
    fail("raw-v7 definition object value mismatch");
  }

  int stabilityPdg = 0, stabilityIsHadron = 0, stabilityIsMeson = 0;
  int stabilityIsBaryon = 0, stabilitySpinType = 0, stabilityCharge3 = 0;
  int stabilityNCharm = 0, stabilityNBeauty = 0, stabilityNc = 0;
  int stabilityNcbar = 0, stabilityNb = 0, stabilityNbbar = 0;
  int stabilityQc = 0, stabilityQb = 0, stabilityStrangeness = 0;
  int stabilityOpenHeavy = 0, stabilityHiddenHeavy = 0, stabilityCentral = 0;
  int stabilityHasAnti = 0, stabilityAntiVerified = 0, stabilityCanDecay = 0;
  int stabilityOriginalMayDecay = 0, stabilityFinalMayDecay = 0;
  double stabilityMass = 0.0, stabilityTau0 = 0.0;
  std::string* stabilityName = nullptr;
  const std::array<std::tuple<const char*, void*, const char*>, 26> stabilityBranches{{
      {"pdg", &stabilityPdg, "Int_t"}, {"name", &stabilityName, "string"},
      {"is_hadron", &stabilityIsHadron, "Int_t"},
      {"is_meson", &stabilityIsMeson, "Int_t"},
      {"is_baryon", &stabilityIsBaryon, "Int_t"},
      {"spin_type", &stabilitySpinType, "Int_t"},
      {"charge3", &stabilityCharge3, "Int_t"},
      {"n_charm", &stabilityNCharm, "Int_t"},
      {"n_beauty", &stabilityNBeauty, "Int_t"},
      {"n_c", &stabilityNc, "Int_t"}, {"n_cbar", &stabilityNcbar, "Int_t"},
      {"n_b", &stabilityNb, "Int_t"}, {"n_bbar", &stabilityNbbar, "Int_t"},
      {"q_c", &stabilityQc, "Int_t"}, {"q_b", &stabilityQb, "Int_t"},
      {"strangeness", &stabilityStrangeness, "Int_t"},
      {"open_heavy", &stabilityOpenHeavy, "Int_t"},
      {"hidden_heavy", &stabilityHiddenHeavy, "Int_t"},
      {"central_registry", &stabilityCentral, "Int_t"},
      {"has_antiparticle", &stabilityHasAnti, "Int_t"},
      {"antiparticle_verified", &stabilityAntiVerified, "Int_t"},
      {"mass", &stabilityMass, "Double_t"}, {"tau0", &stabilityTau0, "Double_t"},
      {"can_decay", &stabilityCanDecay, "Int_t"},
      {"original_may_decay", &stabilityOriginalMayDecay, "Int_t"},
      {"final_may_decay", &stabilityFinalMayDecay, "Int_t"}}};
  std::set<std::string> expectedStability;
  for (const auto& spec : stabilityBranches) expectedStability.insert(std::get<0>(spec));
  if (BranchNames(stability) != expectedStability) {
    fail("heavy-stability branch set mismatch");
  }
  for (const auto& spec : stabilityBranches) {
    TBranch* branch = stability->GetBranch(std::get<0>(spec));
    TLeaf* leaf = branch ? branch->GetLeaf(std::get<0>(spec)) : nullptr;
    const std::string className = branch ? branch->GetClassName() : "";
    const bool stringBranch = std::string(std::get<2>(spec)) == "string";
    const bool correct = branch &&
        (stringBranch ? (className == "string" || className == "std::string") :
         (className.empty() && leaf && leaf->GetTypeName() == std::string(std::get<2>(spec)) &&
          leaf->GetLenStatic() == 1));
    if (!correct) fail(std::string("incorrect heavy-stability branch type ") + std::get<0>(spec));
    else stability->SetBranchAddress(std::get<0>(spec), std::get<1>(spec));
  }
  std::ostringstream reconstructedStability;
  reconstructedStability.imbue(std::locale::classic());
  reconstructedStability << "schema=" << Hadronization::kHeavyStabilityAuditSchema << "\n"
                         << std::scientific << std::setprecision(17);
  std::map<int, std::array<int, 5>> stabilityContent;
  int previousPdg = std::numeric_limits<int>::min();
  for (Long64_t row = 0; row < stability->GetEntries(); ++row) {
    stability->GetEntry(row);
    if (!stabilityName) { fail("null heavy-stability name"); continue; }
    reconstructedStability
        << stabilityPdg << '\t' << std::quoted(*stabilityName) << '\t'
        << stabilityIsHadron << '\t' << stabilityIsMeson << '\t'
        << stabilityIsBaryon << '\t' << stabilitySpinType << '\t'
        << stabilityCharge3 << '\t' << stabilityNCharm << '\t'
        << stabilityNBeauty << '\t' << stabilityNc << '\t' << stabilityNcbar
        << '\t' << stabilityNb << '\t' << stabilityNbbar << '\t' << stabilityQc
        << '\t' << stabilityQb << '\t' << stabilityStrangeness << '\t'
        << stabilityOpenHeavy << '\t' << stabilityHiddenHeavy << '\t'
        << stabilityCentral << '\t' << stabilityHasAnti << '\t'
        << stabilityAntiVerified << '\t' << stabilityMass << '\t' << stabilityTau0
        << '\t' << stabilityCanDecay << '\t' << stabilityOriginalMayDecay << '\t'
        << stabilityFinalMayDecay << '\n';
    if (stabilityPdg <= previousPdg) fail("heavy-stability signed PDGs are not ordered");
    previousPdg = stabilityPdg;
    const auto decoded = Hadronization::DecodeHeavyContent(
        stabilityPdg, stabilityIsMeson != 0, stabilityIsBaryon != 0);
    if (stabilityIsHadron != 1 || (stabilityNCharm <= 0 && stabilityNBeauty <= 0) ||
        stabilityNc != decoded.nc || stabilityNcbar != decoded.ncbar ||
        stabilityNb != decoded.nb || stabilityNbbar != decoded.nbbar ||
        stabilityQc != decoded.qc() || stabilityQb != decoded.qb() ||
        stabilityNCharm != stabilityNc + stabilityNcbar ||
        stabilityNBeauty != stabilityNb + stabilityNbbar ||
        stabilityStrangeness != decoded.strangeness() ||
        stabilityOpenHeavy != ((decoded.qc() != 0 || decoded.qb() != 0) ? 1 : 0) ||
        stabilityHiddenHeavy != ((decoded.hiddenCharm() || decoded.hiddenBeauty()) ? 1 : 0) ||
        stabilityCentral != (Hadronization::FindSelectedState(stabilityPdg) ? 1 : 0) ||
        stabilityAntiVerified != 1 || stabilityFinalMayDecay != 0 ||
        !std::isfinite(stabilityMass) || stabilityMass < 0.0 ||
        !std::isfinite(stabilityTau0) || stabilityTau0 < 0.0) {
      fail("heavy-stability content/stability invariant failed");
    }
    if (!stabilityContent.emplace(stabilityPdg, std::array<int, 5>{{
            stabilityQc, stabilityQb, stabilityCharge3, stabilityHasAnti,
            stabilitySpinType}}).second) {
      fail("duplicate heavy-stability signed PDG");
    }
  }
  stability->ResetBranchAddresses();
  for (const auto& row : stabilityContent) {
    if (row.second[3] == 0) continue;
    const auto anti = stabilityContent.find(-row.first);
    if (anti == stabilityContent.end() || anti->second[0] != -row.second[0] ||
        anti->second[1] != -row.second[1] || anti->second[2] != -row.second[2]) {
      fail("heavy-stability antiparticle pair mismatch");
    }
  }
  for (const auto& selected : Hadronization::kSelectedStates) {
    const auto found = stabilityContent.find(selected.pdg);
    if (found == stabilityContent.end()) {
      fail("heavy-stability audit omits selected signed PDG " +
           std::to_string(selected.pdg));
    }
  }
  if (strings["heavy_stability_audit_sha256"] != stabilityDigest->GetString().Data() ||
      strings["heavy_stability_audit_sha256"] !=
          Hadronization::Sha256Hex(stabilityCanonical->GetString().Data()) ||
      reconstructedStability.str() != stabilityCanonical->GetString().Data()) {
    fail("heavy-stability tree/canonical digest mismatch");
  }
  if (strings["effective_settings_sha256"] != settingsDigest->GetString().Data() ||
      strings["effective_settings_sha256"] !=
          Hadronization::Sha256Hex(settingsCanonical->GetString().Data()) ||
      unsigneds["effective_settings_entries"] !=
          static_cast<unsigned long long>(effectiveSettings->GetEntries())) {
    fail("effective-settings digest/cardinality mismatch");
  }
  if (BranchNames(effectiveSettings) != std::set<std::string>{"name", "value"}) {
    fail("effective-settings branch contract mismatch");
  } else {
    for (const char* branchName : {"name", "value"}) {
      const std::string type = effectiveSettings->GetBranch(branchName)->GetClassName();
      if (type != "string" && type != "std::string") {
        fail(std::string("effective-settings branch type mismatch: ") + branchName);
      }
    }
    std::string* name = nullptr; std::string* value = nullptr;
    effectiveSettings->SetBranchAddress("name", &name);
    effectiveSettings->SetBranchAddress("value", &value);
    std::set<std::string> names;
    std::ostringstream canonical; canonical.imbue(std::locale::classic());
    canonical << "schema=" << Hadronization::kEffectiveSettingsSchema << "\n";
    std::map<std::string, std::string> settings;
    for (Long64_t row = 0; row < effectiveSettings->GetEntries(); ++row) {
      effectiveSettings->GetEntry(row);
      if (!name || !value || name->empty() || !names.insert(*name).second) {
        fail("duplicate/empty effective setting"); continue;
      }
      settings[*name] = *value;
      canonical << std::quoted(*name) << '\t' << std::quoted(*value) << '\n';
    }
    effectiveSettings->ResetBranchAddresses();
    if (canonical.str() != settingsCanonical->GetString().Data() ||
        Hadronization::Sha256Hex(canonical.str()) != strings["effective_settings_sha256"]) {
      fail("effective-settings tree/canonical digest mismatch");
    }
    std::set<std::string> auditedNames;
    for (const std::string_view audited :
         Hadronization::kAuditedPythiaSettingKeys) {
      auditedNames.emplace(audited);
    }
    if (!std::includes(names.begin(), names.end(), auditedNames.begin(),
                       auditedNames.end())) {
      fail("effective-settings snapshot omits a generated audited setting");
    }
    const auto integerSetting = [&settings](const char* name, unsigned long long expected) {
      const auto found = settings.find(name); if (found == settings.end()) return false;
      std::size_t consumed = 0;
      try {
        return std::stoull(found->second, &consumed) == expected &&
               consumed == found->second.size();
      } catch (...) { return false; }
    };
    const auto doubleSetting = [&settings](const char* name, double expected) {
      const auto found = settings.find(name); if (found == settings.end()) return false;
      std::size_t consumed = 0;
      try {
        const double parsed = std::stod(found->second, &consumed);
        return consumed == found->second.size() && std::isfinite(parsed) &&
               Approximately(parsed, expected);
      } catch (...) { return false; }
    };
    const auto exactSetting = [&settings](const char* name, const char* expected) {
      const auto found = settings.find(name);
      return found != settings.end() && found->second == expected;
    };
    if (!exactSetting("Random:setSeed", "true") ||
        !exactSetting("HardQCD:hardccbar", "true") ||
        !exactSetting("HardQCD:hardbbbar", "true") ||
        !integerSetting("Random:seed", static_cast<unsigned long long>(auth.seed)) ||
        !integerSetting("Main:numberOfEvents", auth.events) ||
        !doubleSetting("PhaseSpace:pTHatMin", auth.pthatMin)) {
      fail("effective settings disagree with authorization");
    }
  }

  std::map<int, unsigned long long> recordedProcessCounts;
  if (BranchNames(processCounts) != std::set<std::string>{"code", "count"}) {
    fail("process-count branch contract mismatch");
  } else {
    TLeaf* codeLeaf = processCounts->GetBranch("code")->GetLeaf("code");
    TLeaf* countLeaf = processCounts->GetBranch("count")->GetLeaf("count");
    if (!codeLeaf || !countLeaf || codeLeaf->GetTypeName() != std::string("Int_t") ||
        countLeaf->GetTypeName() != std::string("ULong64_t")) {
      fail("process-count branch type mismatch");
    }
    int code = 0; unsigned long long count = 0; std::set<int> codes;
    unsigned long long total = 0;
    unsigned long long charmTotal = 0;
    unsigned long long beautyTotal = 0;
    processCounts->SetBranchAddress("code", &code); processCounts->SetBranchAddress("count", &count);
    for (Long64_t row = 0; row < processCounts->GetEntries(); ++row) {
      processCounts->GetEntry(row); total += count;
      if (!codes.insert(code).second || (code < 121 || code > 124)) {
        fail("invalid process summary row");
      }
      recordedProcessCounts[code] = count;
      if (code == 121 || code == 122) charmTotal += count;
      if (code == 123 || code == 124) beautyTotal += count;
      const int bin = processHistogram->FindFixBin(code);
      if (!Approximately(processHistogram->GetBinContent(bin), static_cast<double>(count))) fail("process histogram/tree mismatch");
    }
    processCounts->ResetBranchAddresses();
    if (total != auth.events || !Approximately(processHistogram->Integral(0, processHistogram->GetNbinsX() + 1), static_cast<double>(auth.events))) {
      fail("process accounting does not close to successes");
    }
    if (charmTotal == 0ULL || beautyTotal == 0ULL) {
      fail("completed nominal sample lacks a hard charm or beauty channel");
    }
  }

  ULong64_t eventId = 0;
  Int_t processCode = 0, hardChannel = 0, nMpi = 0;
  Double_t weight = 0.0, pthat = 0.0, hardScale = 0.0;
  Int_t mult = 0, multWide = 0, multSpecies[6] = {0, 0, 0, 0, 0, 0};
  Int_t legacyMult = 0, legacyProcess = 0;
  Int_t nCharm = 0, nBeauty = 0, nBc = 0;
  Int_t finalQc = 0, finalQb = 0;
  Int_t conservation = 0, originValid = 0, matchValid = 0;
  tree->SetBranchAddress("event_id", &eventId);
  tree->SetBranchAddress("process_code", &processCode);
  tree->SetBranchAddress("hard_channel", &hardChannel);
  tree->SetBranchAddress("event_weight", &weight);
  tree->SetBranchAddress("pthat", &pthat);
  tree->SetBranchAddress("hard_scale", &hardScale);
  tree->SetBranchAddress("n_mpi", &nMpi);
  tree->SetBranchAddress("multiplicity_primary_charged_eta10_v1", &mult);
  tree->SetBranchAddress("multiplicity_primary_charged_eta40_v1", &multWide);
  tree->SetBranchAddress("multiplicity_central_by_species", multSpecies);
  tree->SetBranchAddress("MULTIPLICITY", &legacyMult);
  tree->SetBranchAddress("PROCESSCODE", &legacyProcess);
  tree->SetBranchAddress("NCHARM", &nCharm);
  tree->SetBranchAddress("NBEAUTY", &nBeauty);
  tree->SetBranchAddress("NBC", &nBc);
  tree->SetBranchAddress("final_heavy_qc_sum", &finalQc);
  tree->SetBranchAddress("final_heavy_qb_sum", &finalQb);
  tree->SetBranchAddress("heavy_flavour_conservation_ok", &conservation);
  tree->SetBranchAddress("origin_classification_valid", &originValid);
  tree->SetBranchAddress("primary_all_heavy_match_valid", &matchValid);

  std::map<std::string, std::vector<int>*> intVectorValues;
  std::map<std::string, std::vector<double>*> doubleVectorValues;
  for (const char* name : integerVectors) {
    intVectorValues.emplace(name, nullptr);
    tree->SetBranchAddress(name, &intVectorValues.at(name));
  }
  for (const char* name : doubleVectors) {
    doubleVectorValues.emplace(name, nullptr);
    tree->SetBranchAddress(name, &doubleVectorValues.at(name));
  }
  for (const char* name : finalDoubleVector) {
    doubleVectorValues.emplace(name, nullptr);
    tree->SetBranchAddress(name, &doubleVectorValues.at(name));
  }
  for (const char* name : hardDoubleVectors) {
    doubleVectorValues.emplace(name, nullptr);
    tree->SetBranchAddress(name, &doubleVectorValues.at(name));
  }

  std::set<ULong64_t> eventIds;
  std::map<int, unsigned long long> observedProcessCounts;
  double observedSumW = 0.0;
  double observedSumW2 = 0.0;
  unsigned long long centralOverflow = 0;
  unsigned long long wideOverflow = 0;
  std::vector<double> centralBins(
      static_cast<std::size_t>(multiplicity->GetNbinsX()) + 2U, 0.0);
  std::vector<double> centralBins2(centralBins.size(), 0.0);
  std::vector<double> wideBins(
      static_cast<std::size_t>(multiplicityWide->GetNbinsX()) + 2U, 0.0);
  std::vector<double> wideBins2(wideBins.size(), 0.0);
  for (Long64_t row = 0; row < tree->GetEntries(); ++row) {
    tree->GetEntry(row);
    const bool nullIntVector = std::any_of(
        intVectorValues.begin(), intVectorValues.end(),
        [](const auto& item) { return item.second == nullptr; });
    const bool nullDoubleVector = std::any_of(
        doubleVectorValues.begin(), doubleVectorValues.end(),
        [](const auto& item) { return item.second == nullptr; });
    if (nullIntVector || nullDoubleVector) {
      fail("null event vector payload");
      continue;
    }
    const auto& iv = intVectorValues;
    const auto& dv = doubleVectorValues;
    const auto& ints = [&iv](const char* name) -> const std::vector<int>& {
      return *iv.at(name);
    };
    const auto& reals = [&dv](const char* name) -> const std::vector<double>& {
      return *dv.at(name);
    };
    const auto sameIntSize = [&ints](std::initializer_list<const char*> names,
                                     std::size_t size) {
      return std::all_of(names.begin(), names.end(),
                         [&ints, size](const char* name) {
                           return ints(name).size() == size;
                         });
    };
    const auto sameDoubleSize = [&reals](
                                    std::initializer_list<const char*> names,
                                    std::size_t size) {
      return std::all_of(names.begin(), names.end(),
                         [&reals, size](const char* name) {
                           return reals(name).size() == size;
                         });
    };

    if (!eventIds.insert(eventId).second) fail("duplicate event ID");
    try {
      const auto expected = Hadronization::EventId(
          auth.campaignOrdinal, Hadronization::TuneOrdinal(auth.tune),
          auth.logicalId, auth.attempt, static_cast<std::uint64_t>(row));
      if (eventId != expected) fail("event ID outside frozen logical identity");
    } catch (const std::exception&) {
      fail("event-ID domain invalid");
    }
    const int expectedChannel =
        (processCode == 121 || processCode == 122)
            ? 4
            : ((processCode == 123 || processCode == 124) ? 5 : 0);
    if (expectedChannel == 0 || hardChannel != expectedChannel) {
      fail("process/hard-channel mismatch");
    }
    if (!std::isfinite(weight)) fail("non-finite event weight");
    if (!std::isfinite(pthat) || pthat + 1e-12 < auth.pthatMin ||
        !std::isfinite(hardScale) || hardScale < 0.0 || nMpi < 0) {
      fail("invalid event pTHat/hard-scale/MPI physics");
    }
    int componentSum = 0;
    for (const int component : multSpecies) {
      if (component < 0) fail("negative multiplicity component");
      componentSum += component;
    }
    if (mult < 0 || multWide < 0 || mult > multWide ||
        componentSum != mult) {
      fail("invalid central/wide multiplicity physics");
    }
    if (legacyMult != mult || legacyProcess != processCode) {
      fail("legacy scalar aliases disagree with canonical event fields");
    }
    if (conservation != 1 || originValid != 1 || matchValid != 1) {
      fail("false required event validity flag");
    }
    if (std::isfinite(weight)) {
      observedSumW += weight;
      observedSumW2 += weight * weight;
      ++observedProcessCounts[processCode];
      const int centralBin = multiplicity->FindFixBin(mult);
      const int wideBin = multiplicityWide->FindFixBin(multWide);
      if (centralBin < 0 ||
          centralBin >= static_cast<int>(centralBins.size()) || wideBin < 0 ||
          wideBin >= static_cast<int>(wideBins.size())) {
        fail("ROOT multiplicity bin lookup is outside histogram storage");
      } else {
        const std::size_t cb = static_cast<std::size_t>(centralBin);
        const std::size_t wb = static_cast<std::size_t>(wideBin);
        centralBins[cb] += weight;
        centralBins2[cb] += weight * weight;
        wideBins[wb] += weight;
        wideBins2[wb] += weight * weight;
        if (centralBin == multiplicity->GetNbinsX() + 1) ++centralOverflow;
        if (wideBin == multiplicityWide->GetNbinsX() + 1) ++wideOverflow;
      }
    }

    const std::size_t hardSize = ints("hard_indices").size();
    if (hardSize != 2U ||
        !sameIntSize({"hard_bottom_indices", "hard_ids", "hard_status",
                      "hard_bottom_ids", "hard_bottom_status"},
                     hardSize) ||
        !sameDoubleSize({"hard_px", "hard_py", "hard_pz", "hard_e"},
                        hardSize)) {
      fail("hard vector lengths/exact-pair cardinality are inconsistent");
      continue;
    }
    std::map<int, int> hardByIndex;
    std::set<int> hardIds;
    for (std::size_t index = 0; index < hardSize; ++index) {
      const int hardIndex = ints("hard_indices")[index];
      const int hardId = ints("hard_ids")[index];
      if (hardIndex <= 0 || ints("hard_bottom_indices")[index] <= 0 ||
          std::abs(hardId) != expectedChannel ||
          std::abs(ints("hard_status")[index]) != 23 ||
          ints("hard_bottom_ids")[index] != hardId ||
          ints("hard_bottom_status")[index] == 0 ||
          !std::isfinite(reals("hard_px")[index]) ||
          !std::isfinite(reals("hard_py")[index]) ||
          !std::isfinite(reals("hard_pz")[index]) ||
          !std::isfinite(reals("hard_e")[index]) ||
          reals("hard_e")[index] < 0.0 ||
          !hardByIndex.emplace(hardIndex, hardId).second) {
        fail("invalid hard vector record");
      }
      hardIds.insert(hardId);
    }
    if (hardIds != std::set<int>{-expectedChannel, expectedChannel}) {
      fail("hard vectors do not encode the exact signed process pair");
    }

    const std::size_t heavySize = ints("heavyPdg").size();
    const bool heavyLengths =
        heavySize > 0U &&
        sameIntSize(
            {"heavyIndex", "heavyStatus", "heavyStatusAbs", "heavyIsFinal",
             "heavyIsMeson", "heavyIsBaryon", "heavyCharge3",
             "heavySpinType", "heavyMother1", "heavyMother2",
             "heavyDaughter1", "heavyDaughter2", "heavyNc", "heavyNcbar",
             "heavyNb", "heavyNbbar", "heavyQc", "heavyQb",
             "heavyBaryonNumber", "heavyStrangeness", "heavyCentral",
             "heavyOpen", "heavyHidden", "heavyStateCategory",
             "heavyOriginC", "heavyOriginB", "heavyMatchResolutionC",
             "heavyMatchResolutionB", "heavyMatchedHardC",
             "heavyMatchedHardB", "heavyRejectedHardC",
             "heavyRejectedHardB", "heavyOriginDepthC",
             "heavyOriginDepthB"},
            heavySize) &&
        sameDoubleSize({"heavyPx", "heavyPy", "heavyPz", "heavyE",
                        "heavyPt", "heavyEta", "heavyY", "heavyPhi",
                        "heavyMass"},
                       heavySize);
    const std::size_t legacySize = ints("ID").size();
    const bool legacyLengths =
        legacySize == heavySize &&
        sameIntSize({"HFCLASS", "STATUS", "MOTHER", "MOTHERID"},
                    legacySize) &&
        sameDoubleSize({"PT", "ETA", "Y", "PHI", "CHARGE"}, legacySize);
    const auto validOffsets = [](const std::vector<int>& offsets,
                                 std::size_t rows, std::size_t flattened) {
      if (offsets.size() != rows + 1U || offsets.empty() ||
          offsets.front() != 0 || offsets.back() < 0 ||
          static_cast<std::size_t>(offsets.back()) != flattened) {
        return false;
      }
      return std::adjacent_find(
                 offsets.begin(), offsets.end(),
                 [](int left, int right) { return left < 0 || right < left; }) ==
             offsets.end();
    };
    const bool motherOffsets = validOffsets(
        ints("heavyMotherOffsets"), heavySize, ints("heavyMothers").size());
    const std::size_t constituentSize = ints("heavyConstituentPdg").size();
    const bool constituentLengths =
        validOffsets(ints("heavyConstituentOffsets"), heavySize,
                     constituentSize) &&
        sameIntSize({"heavyConstituentParentSlot", "heavyConstituentOrdinal",
                     "heavyConstituentOrigin",
                     "heavyConstituentMatchResolution",
                     "heavyConstituentMatchedHard",
                     "heavyConstituentRejectedHard",
                     "heavyConstituentOriginDepth"},
                    constituentSize);
    const std::size_t ancestrySize = ints("ancestryIndex").size();
    const bool ancestryLengths =
        sameIntSize({"ancestryPdg", "ancestryStatus", "ancestryMother1",
                     "ancestryMother2"},
                    ancestrySize) &&
        validOffsets(ints("ancestryMotherOffsets"), ancestrySize,
                     ints("ancestryMothers").size());
    const std::size_t auditSize = ints("multAuditPdg").size();
    const bool auditLengths =
        sameIntSize({"multAuditParticleIndex", "multAuditStatus",
                     "multAuditIsHeavy"},
                    auditSize) &&
        sameDoubleSize({"multAuditPt", "multAuditEta"}, auditSize);
    if (!heavyLengths || !legacyLengths || !motherOffsets ||
        !constituentLengths || !ancestryLengths || !auditLengths) {
      fail("event heavy/legacy/constituent/ancestry vector lengths or offsets are inconsistent");
      continue;
    }
    if (static_cast<unsigned long long>(row) >=
            unsigneds["multiplicity_audit_events"] &&
        auditSize != 0U) {
      fail("multiplicity audit vectors exist beyond declared pilot range");
    }

    std::map<int, StoredAncestor> ancestry;
    for (std::size_t node = 0; node < ancestrySize; ++node) {
      const int begin = ints("ancestryMotherOffsets")[node];
      const int end = ints("ancestryMotherOffsets")[node + 1U];
      std::vector<int> mothers(
          ints("ancestryMothers").begin() + begin,
          ints("ancestryMothers").begin() + end);
      if (ints("ancestryIndex")[node] <= 0 ||
          !std::is_sorted(mothers.begin(), mothers.end()) ||
          std::adjacent_find(mothers.begin(), mothers.end()) != mothers.end() ||
          std::any_of(mothers.begin(), mothers.end(),
                      [](int mother) { return mother <= 0; }) ||
          !ancestry
               .emplace(ints("ancestryIndex")[node],
                        StoredAncestor{ints("ancestryPdg")[node],
                                       ints("ancestryStatus")[node],
                                       ints("ancestryMother1")[node],
                                       ints("ancestryMother2")[node], mothers})
               .second) {
        fail("invalid ancestry topology");
      }
      for (const int endpoint : {ints("ancestryMother1")[node],
                                 ints("ancestryMother2")[node]}) {
        if (endpoint > 0 && !std::binary_search(mothers.begin(), mothers.end(),
                                                endpoint)) {
          fail("ancestry endpoint is absent from its complete-mother segment");
        }
      }
    }

    int observedCharm = 0, observedBeauty = 0, observedBc = 0;
    int observedFinalQc = 0, observedFinalQb = 0;
    std::set<int> heavyIndices;
    std::vector<int> reconstructedOriginC(heavySize);
    std::vector<int> reconstructedOriginB(heavySize);
    std::vector<int> reconstructedResolutionC(heavySize);
    std::vector<int> reconstructedResolutionB(heavySize);
    std::vector<int> reconstructedMatchedC(heavySize);
    std::vector<int> reconstructedMatchedB(heavySize);
    std::vector<int> reconstructedRejectedC(heavySize, -1);
    std::vector<int> reconstructedRejectedB(heavySize, -1);
    std::vector<int> reconstructedDepthC(heavySize);
    std::vector<int> reconstructedDepthB(heavySize);
    for (std::size_t index = 0; index < heavySize; ++index) {
      const int begin = ints("heavyMotherOffsets")[index];
      const int end = ints("heavyMotherOffsets")[index + 1U];
      std::vector<int> mothers(ints("heavyMothers").begin() + begin,
                               ints("heavyMothers").begin() + end);
      if (!std::is_sorted(mothers.begin(), mothers.end()) ||
          std::adjacent_find(mothers.begin(), mothers.end()) != mothers.end() ||
          std::any_of(mothers.begin(), mothers.end(),
                      [](int mother) { return mother <= 0; })) {
        fail("invalid heavy complete-mother segment");
      }
      for (const int endpoint : {ints("heavyMother1")[index],
                                 ints("heavyMother2")[index]}) {
        if (endpoint > 0 &&
            !std::binary_search(mothers.begin(), mothers.end(), endpoint)) {
          fail("heavy endpoint is absent from its complete-mother segment");
        }
      }
      const int pdg = ints("heavyPdg")[index];
      const bool isMeson = ints("heavyIsMeson")[index] != 0;
      const bool isBaryon = ints("heavyIsBaryon")[index] != 0;
      const auto decoded =
          Hadronization::DecodeHeavyContent(pdg, isMeson, isBaryon);
      const auto stable = stabilityContent.find(pdg);
      const int expectedBaryon = isBaryon ? (pdg > 0 ? 1 : -1) : 0;
      if (ints("heavyIndex")[index] < 0 ||
          !heavyIndices.insert(ints("heavyIndex")[index]).second ||
          (ints("heavyIsFinal")[index] != 0 &&
           ints("heavyIsFinal")[index] != 1) ||
          (ints("heavyIsMeson")[index] != 0 &&
           ints("heavyIsMeson")[index] != 1) ||
          (ints("heavyIsBaryon")[index] != 0 &&
           ints("heavyIsBaryon")[index] != 1) ||
          isMeson == isBaryon ||
          ints("heavyStatusAbs")[index] !=
              std::abs(ints("heavyStatus")[index]) ||
          stable == stabilityContent.end() ||
          ints("heavyNc")[index] != decoded.nc ||
          ints("heavyNcbar")[index] != decoded.ncbar ||
          ints("heavyNb")[index] != decoded.nb ||
          ints("heavyNbbar")[index] != decoded.nbbar ||
          ints("heavyQc")[index] != decoded.qc() ||
          ints("heavyQb")[index] != decoded.qb() ||
          ints("heavyBaryonNumber")[index] != expectedBaryon ||
          ints("heavyStrangeness")[index] != decoded.strangeness() ||
          ints("heavyCentral")[index] !=
              (Hadronization::FindSelectedState(pdg) ? 1 : 0) ||
          ints("heavyOpen")[index] !=
              ((decoded.qc() != 0 || decoded.qb() != 0) ? 1 : 0) ||
          ints("heavyHidden")[index] !=
              ((decoded.hiddenCharm() || decoded.hiddenBeauty()) ? 1 : 0) ||
          ints("heavyStateCategory")[index] !=
              static_cast<int>(Hadronization::ClassifyHeavyStateDetailed(
                  Hadronization::FindSelectedState(pdg) != nullptr, decoded,
                  isMeson, ints("heavySpinType")[index]))) {
        fail("heavy identity/content/category invariant failed");
      } else if (stable->second[0] != decoded.qc() ||
                 stable->second[1] != decoded.qb() ||
                 stable->second[2] != ints("heavyCharge3")[index] ||
                 stable->second[4] != ints("heavySpinType")[index]) {
        fail("event heavy row disagrees with stability audit");
      }
      const bool finiteKinematics =
          std::isfinite(reals("heavyPx")[index]) &&
          std::isfinite(reals("heavyPy")[index]) &&
          std::isfinite(reals("heavyPz")[index]) &&
          std::isfinite(reals("heavyE")[index]) &&
          std::isfinite(reals("heavyPt")[index]) &&
          std::isfinite(reals("heavyEta")[index]) &&
          std::isfinite(reals("heavyY")[index]) &&
          std::isfinite(reals("heavyPhi")[index]) &&
          std::isfinite(reals("heavyMass")[index]) &&
          reals("heavyE")[index] >= 0.0 &&
          reals("heavyPt")[index] >= 0.0 &&
          reals("heavyMass")[index] >= 0.0;
      const double derivedPt =
          std::hypot(reals("heavyPx")[index], reals("heavyPy")[index]);
      const double derivedMass2 =
          reals("heavyE")[index] * reals("heavyE")[index] -
          reals("heavyPx")[index] * reals("heavyPx")[index] -
          reals("heavyPy")[index] * reals("heavyPy")[index] -
          reals("heavyPz")[index] * reals("heavyPz")[index];
      if (!finiteKinematics ||
          !Approximately(derivedPt, reals("heavyPt")[index]) ||
          !Approximately(derivedMass2,
                         reals("heavyMass")[index] *
                             reals("heavyMass")[index])) {
        fail("heavy kinematic invariant failed");
      }
      const bool hasCharm = decoded.hasCharm();
      const bool hasBeauty = decoded.hasBeauty();
      const int expectedClass =
          hasCharm && hasBeauty ? 45 : (hasBeauty ? 5 : 4);
      if (ints("ID")[index] != pdg ||
          ints("HFCLASS")[index] != expectedClass ||
          ints("STATUS")[index] != ints("heavyStatus")[index] ||
          ints("MOTHER")[index] != ints("heavyMother1")[index] ||
          !Approximately(reals("PT")[index], reals("heavyPt")[index]) ||
          !Approximately(reals("ETA")[index], reals("heavyEta")[index]) ||
          !Approximately(reals("Y")[index], reals("heavyY")[index]) ||
          !Approximately(reals("PHI")[index], reals("heavyPhi")[index]) ||
          !Approximately(3.0 * reals("CHARGE")[index],
                         static_cast<double>(ints("heavyCharge3")[index]))) {
        fail("legacy/full-heavy aliases disagree");
      }
      const int mother1 = ints("heavyMother1")[index];
      const auto motherRow = ancestry.find(mother1);
      const int expectedMotherPdg =
          mother1 > 0 && motherRow != ancestry.end() ? motherRow->second.pdg : 0;
      if (ints("MOTHERID")[index] != expectedMotherPdg) {
        fail("legacy mother-PDG alias disagrees with retained ancestry");
      }
      observedBc += hasCharm && hasBeauty ? 1 : 0;
      observedCharm += hasCharm && !hasBeauty ? 1 : 0;
      observedBeauty += hasBeauty && !hasCharm ? 1 : 0;
      if (ints("heavyIsFinal")[index] != 0) {
        observedFinalQc += decoded.qc();
        observedFinalQb += decoded.qb();
      }
      const int charmSign = decoded.qc() > 0 ? 1 : (decoded.qc() < 0 ? -1 : 0);
      const int beautySign = decoded.qb() > 0 ? 1 : (decoded.qb() < 0 ? -1 : 0);
      const auto charm = ReconstructOrigin(ancestry, mothers, 4, charmSign,
                                           hardByIndex);
      const auto beauty = ReconstructOrigin(ancestry, mothers, 5, beautySign,
                                            hardByIndex);
      reconstructedOriginC[index] = charm.origin;
      reconstructedOriginB[index] = beauty.origin;
      reconstructedResolutionC[index] = charm.resolution;
      reconstructedResolutionB[index] = beauty.resolution;
      reconstructedMatchedC[index] = charm.matchedHard;
      reconstructedMatchedB[index] = beauty.matchedHard;
      reconstructedDepthC[index] = charm.depth;
      reconstructedDepthB[index] = beauty.depth;
    }
    const std::vector<int> preUniqueC = reconstructedMatchedC;
    const std::vector<int> preUniqueB = reconstructedMatchedB;
    Hadronization::EnforceUniqueFinalHardCarrier(
        ints("heavyIsFinal"), ints("heavyQc"), reconstructedOriginC,
        reconstructedResolutionC, reconstructedMatchedC);
    Hadronization::EnforceUniqueFinalHardCarrier(
        ints("heavyIsFinal"), ints("heavyQb"), reconstructedOriginB,
        reconstructedResolutionB, reconstructedMatchedB);
    for (std::size_t index = 0; index < heavySize; ++index) {
      if (reconstructedResolutionC[index] == static_cast<int>(
              Hadronization::MatchResolution::kDuplicateHardCarrier)) {
        reconstructedRejectedC[index] = preUniqueC[index];
      }
      if (reconstructedResolutionB[index] == static_cast<int>(
              Hadronization::MatchResolution::kDuplicateHardCarrier)) {
        reconstructedRejectedB[index] = preUniqueB[index];
      }
    }
    Hadronization::RejectFinalMultiHeavyCarrier(
        ints("heavyIsFinal"), ints("heavyQc"), reconstructedOriginC,
        reconstructedResolutionC, reconstructedMatchedC,
        reconstructedRejectedC);
    Hadronization::RejectFinalMultiHeavyCarrier(
        ints("heavyIsFinal"), ints("heavyQb"), reconstructedOriginB,
        reconstructedResolutionB, reconstructedMatchedB,
        reconstructedRejectedB);
    if (reconstructedOriginC != ints("heavyOriginC") ||
        reconstructedOriginB != ints("heavyOriginB") ||
        reconstructedResolutionC != ints("heavyMatchResolutionC") ||
        reconstructedResolutionB != ints("heavyMatchResolutionB") ||
        reconstructedMatchedC != ints("heavyMatchedHardC") ||
        reconstructedMatchedB != ints("heavyMatchedHardB") ||
        reconstructedRejectedC != ints("heavyRejectedHardC") ||
        reconstructedRejectedB != ints("heavyRejectedHardB") ||
        reconstructedDepthC != ints("heavyOriginDepthC") ||
        reconstructedDepthB != ints("heavyOriginDepthB")) {
      fail("origin/carrier decision is not reproducible from retained ancestry");
    }

    std::vector<int> constituentOrigin(constituentSize);
    std::vector<int> constituentResolution(constituentSize);
    std::vector<int> constituentMatched(constituentSize);
    std::vector<int> constituentRejected(constituentSize, -1);
    std::vector<int> constituentDepth(constituentSize);
    std::vector<int> constituentParentFinal(constituentSize, 0);
    std::size_t coveredConstituents = 0;
    for (std::size_t parent = 0; parent < heavySize; ++parent) {
      const int begin = ints("heavyConstituentOffsets")[parent];
      const int end = ints("heavyConstituentOffsets")[parent + 1U];
      const int expectedCount =
          ints("heavyNc")[parent] + ints("heavyNcbar")[parent] +
          ints("heavyNb")[parent] + ints("heavyNbbar")[parent];
      if (end - begin != expectedCount ||
          static_cast<std::size_t>(begin) != coveredConstituents) {
        fail("heavy constituent offsets/counts disagree with decoded content");
        continue;
      }
      coveredConstituents += static_cast<std::size_t>(expectedCount);
      const int motherBegin = ints("heavyMotherOffsets")[parent];
      const int motherEnd = ints("heavyMotherOffsets")[parent + 1U];
      std::vector<int> mothers(ints("heavyMothers").begin() + motherBegin,
                               ints("heavyMothers").begin() + motherEnd);
      std::size_t position = static_cast<std::size_t>(begin);
      const std::array<std::pair<int, int>, 4> expectedRows{{
          {4, ints("heavyNc")[parent]},
          {-4, ints("heavyNcbar")[parent]},
          {5, ints("heavyNb")[parent]},
          {-5, ints("heavyNbbar")[parent]},
      }};
      for (const auto& expected : expectedRows) {
        for (int ordinal = 0; ordinal < expected.second;
             ++ordinal, ++position) {
          if (position >= static_cast<std::size_t>(end) ||
              ints("heavyConstituentParentSlot")[position] !=
                  static_cast<int>(parent) ||
              ints("heavyConstituentPdg")[position] != expected.first ||
              ints("heavyConstituentOrdinal")[position] != ordinal) {
            fail("flattened heavy constituent identity/order mismatch");
            continue;
          }
          const auto reconstructed = ReconstructOrigin(
              ancestry, mothers, std::abs(expected.first),
              expected.first > 0 ? 1 : -1, hardByIndex);
          constituentOrigin[position] = reconstructed.origin;
          constituentResolution[position] = reconstructed.resolution;
          constituentMatched[position] = reconstructed.matchedHard;
          constituentDepth[position] = reconstructed.depth;
          constituentParentFinal[position] = ints("heavyIsFinal")[parent];
        }
      }
    }
    if (coveredConstituents != constituentSize) {
      fail("heavy constituent offsets do not cover flattened rows exactly");
    }
    Hadronization::EnforceUniqueFinalConstituentHardCarrier(
        ints("heavyConstituentParentSlot"), constituentParentFinal,
        ints("heavyConstituentPdg"), constituentOrigin,
        constituentResolution, constituentMatched, constituentRejected);
    if (constituentOrigin != ints("heavyConstituentOrigin") ||
        constituentResolution != ints("heavyConstituentMatchResolution") ||
        constituentMatched != ints("heavyConstituentMatchedHard") ||
        constituentRejected != ints("heavyConstituentRejectedHard") ||
        constituentDepth != ints("heavyConstituentOriginDepth")) {
      fail("constituent origin/carrier decision is not reproducible from ancestry");
    }
    if (nCharm != observedCharm || nBeauty != observedBeauty ||
        nBc != observedBc ||
        nCharm + nBeauty + nBc != static_cast<int>(heavySize)) {
      fail("NCHARM/NBEAUTY/NBC disagree with legacy/full-heavy rows");
    }
    if (finalQc != observedFinalQc || finalQb != observedFinalQb ||
        observedFinalQc != 0 || observedFinalQb != 0 || conservation != 1) {
      fail("final heavy-flavour sums/conservation disagree");
    }
  }
  tree->ResetBranchAddresses();
  if (!Approximately(observedSumW, doubles["sum_weights"]) ||
      !Approximately(observedSumW2, doubles["sum_weights2"])) {
    fail("event weights do not close to metadata");
  }
  if (observedProcessCounts != recordedProcessCounts) {
    fail("event process counts do not match process summary");
  }
  if (centralOverflow != unsigneds["multiplicity_overflow"] ||
      wideOverflow != unsigneds["multiplicity_wide_overflow"]) {
    fail("event multiplicity overflows do not match metadata");
  }
  if (static_cast<unsigned long long>(multiplicity->GetEntries()) != auth.events ||
      static_cast<unsigned long long>(multiplicityWide->GetEntries()) != auth.events ||
      multiplicity->GetSumw2N() <= 0 || multiplicityWide->GetSumw2N() <= 0) {
    fail("multiplicity histogram entry/Sumw2 contract mismatch");
  }
  const auto compareHistogram = [&fail](
                                    TH1* histogram,
                                    const std::vector<double>& sums,
                                    const std::vector<double>& sums2,
                                    const char* label) {
    for (int bin = 0; bin <= histogram->GetNbinsX() + 1; ++bin) {
      const std::size_t index = static_cast<std::size_t>(bin);
      const double storedSumW2 =
          histogram->GetSumw2N() > 0 ? histogram->GetSumw2()->At(bin)
                                     : std::numeric_limits<double>::quiet_NaN();
      if (!Approximately(histogram->GetBinContent(bin), sums.at(index)) ||
          !Approximately(storedSumW2, sums2.at(index))) {
        fail(std::string(label) +
             " bin content/Sumw2 differs from event reconstruction");
      }
    }
  };
  compareHistogram(multiplicity, centralBins, centralBins2,
                   "central multiplicity histogram");
  compareHistogram(multiplicityWide, wideBins, wideBins2,
                   "wide multiplicity histogram");
  if (static_cast<unsigned long long>(processHistogram->GetEntries()) !=
      auth.events) {
    fail("process histogram entries do not equal successful events");
  }
  for (int bin = 0; bin <= processHistogram->GetNbinsX() + 1; ++bin) {
    const int code =
        static_cast<int>(std::llround(processHistogram->GetBinCenter(bin)));
    const auto found = observedProcessCounts.find(code);
    const double expected = found == observedProcessCounts.end()
                                ? 0.0
                                : static_cast<double>(found->second);
    if (!Approximately(processHistogram->GetBinContent(bin), expected)) {
      fail("process histogram differs from event reconstruction");
      break;
    }
  }
  if (errors == 0) std::cout << "RAW_VALIDATION_PASS " << auth.path << '\n';
  return errors;
}

}  // namespace

int main(int argc, char** argv) {
  try {
    const int errors = Validate(Arguments(argc, argv));
    return errors == 0 ? 0 : 1;
  } catch (const std::exception& error) {
    std::cerr << "RAW_VALIDATION_ERROR " << error.what() << '\n';
    return 2;
  }
}
