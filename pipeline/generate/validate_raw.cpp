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
  const std::array<const char*, 8> zeroCounters{{
      "multiplicity_overflow", "multiplicity_wide_overflow", "content_decode_failures",
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
  std::map<int, std::array<int, 4>> stabilityContent;
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
    if (!stabilityContent.emplace(stabilityPdg, std::array<int, 4>{{
            stabilityQc, stabilityQb, stabilityCharge3, stabilityHasAnti}}).second) {
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
    const auto integerSetting = [&settings](const char* name, unsigned long long expected) {
      const auto found = settings.find(name); if (found == settings.end()) return false;
      try { return std::stoull(found->second) == expected; } catch (...) { return false; }
    };
    const auto doubleSetting = [&settings](const char* name, double expected) {
      const auto found = settings.find(name); if (found == settings.end()) return false;
      try { return Approximately(std::stod(found->second), expected); } catch (...) { return false; }
    };
    if (settings["Random:setSeed"] != "true" || settings["HardQCD:hardccbar"] != "true" ||
        settings["HardQCD:hardbbbar"] != "true" || !integerSetting("Random:seed", static_cast<unsigned long long>(auth.seed)) ||
        !integerSetting("Main:numberOfEvents", auth.events) ||
        !doubleSetting("PhaseSpace:pTHatMin", auth.pthatMin)) {
      fail("effective settings disagree with authorization");
    }
  }

  if (BranchNames(processCounts) != std::set<std::string>{"code", "count"}) {
    fail("process-count branch contract mismatch");
  } else {
    TLeaf* codeLeaf = processCounts->GetBranch("code")->GetLeaf("code");
    TLeaf* countLeaf = processCounts->GetBranch("count")->GetLeaf("count");
    if (!codeLeaf || !countLeaf || codeLeaf->GetTypeName() != std::string("Int_t") ||
        countLeaf->GetTypeName() != std::string("ULong64_t")) {
      fail("process-count branch type mismatch");
    }
    int code = 0; unsigned long long count = 0; std::set<int> codes; unsigned long long total = 0;
    processCounts->SetBranchAddress("code", &code); processCounts->SetBranchAddress("count", &count);
    for (Long64_t row = 0; row < processCounts->GetEntries(); ++row) {
      processCounts->GetEntry(row); total += count;
      if (!codes.insert(code).second || (code < 121 || code > 124)) fail("invalid process summary row");
      const int bin = processHistogram->FindFixBin(code);
      if (!Approximately(processHistogram->GetBinContent(bin), static_cast<double>(count))) fail("process histogram/tree mismatch");
    }
    processCounts->ResetBranchAddresses();
    if (total != auth.events || !Approximately(processHistogram->Integral(0, processHistogram->GetNbinsX() + 1), static_cast<double>(auth.events))) {
      fail("process accounting does not close to successes");
    }
  }

  ULong64_t eventId = 0; Int_t processCode = 0; Int_t hardChannel = 0;
  Double_t weight = 0.0; Int_t mult = 0; Int_t multWide = 0;
  Int_t conservation = 0; Int_t origin = 0; Int_t match = 0;
  tree->SetBranchAddress("event_id", &eventId); tree->SetBranchAddress("process_code", &processCode);
  tree->SetBranchAddress("hard_channel", &hardChannel); tree->SetBranchAddress("event_weight", &weight);
  tree->SetBranchAddress("multiplicity_primary_charged_eta10_v1", &mult);
  tree->SetBranchAddress("multiplicity_primary_charged_eta40_v1", &multWide);
  tree->SetBranchAddress("heavy_flavour_conservation_ok", &conservation);
  tree->SetBranchAddress("origin_classification_valid", &origin);
  tree->SetBranchAddress("primary_all_heavy_match_valid", &match);
  std::set<ULong64_t> eventIds; double observedSumW = 0.0; double observedSumW2 = 0.0;
  std::vector<double> centralBins(static_cast<std::size_t>(multiplicity->GetNbinsX()) + 2U, 0.0);
  std::vector<double> wideBins(static_cast<std::size_t>(multiplicityWide->GetNbinsX()) + 2U, 0.0);
  for (Long64_t row = 0; row < tree->GetEntries(); ++row) {
    tree->GetEntry(row);
    if (!eventIds.insert(eventId).second) fail("duplicate event ID");
    try {
      const auto expected = Hadronization::EventId(auth.campaignOrdinal,
          Hadronization::TuneOrdinal(auth.tune), auth.logicalId, auth.attempt,
          static_cast<std::uint64_t>(row));
      if (eventId != expected) fail("event ID outside frozen logical identity");
    } catch (const std::exception&) { fail("event-ID domain invalid"); }
    const int expectedChannel = (processCode == 121 || processCode == 122) ? 4 :
                                ((processCode == 123 || processCode == 124) ? 5 : 0);
    if (expectedChannel == 0 || hardChannel != expectedChannel) fail("process/hard-channel mismatch");
    if (!std::isfinite(weight)) fail("non-finite event weight");
    if (conservation != 1 || origin != 1 || match != 1) fail("false required event validity flag");
    observedSumW += weight; observedSumW2 += weight * weight;
    centralBins.at(static_cast<std::size_t>(multiplicity->FindFixBin(mult))) += weight;
    wideBins.at(static_cast<std::size_t>(multiplicityWide->FindFixBin(multWide))) += weight;
  }
  tree->ResetBranchAddresses();
  if (!Approximately(observedSumW, doubles["sum_weights"]) ||
      !Approximately(observedSumW2, doubles["sum_weights2"])) fail("event weights do not close to metadata");
  if (static_cast<unsigned long long>(multiplicity->GetEntries()) != auth.events ||
      static_cast<unsigned long long>(multiplicityWide->GetEntries()) != auth.events ||
      multiplicity->GetSumw2N() <= 0 || multiplicityWide->GetSumw2N() <= 0) {
    fail("multiplicity histogram entry/Sumw2 contract mismatch");
  }
  for (int bin = 0; bin <= multiplicity->GetNbinsX() + 1; ++bin) {
    if (!Approximately(centralBins.at(static_cast<std::size_t>(bin)), multiplicity->GetBinContent(bin))) {
      fail("central multiplicity histogram closure failed"); break;
    }
  }
  for (int bin = 0; bin <= multiplicityWide->GetNbinsX() + 1; ++bin) {
    if (!Approximately(wideBins.at(static_cast<std::size_t>(bin)), multiplicityWide->GetBinContent(bin))) {
      fail("wide multiplicity histogram closure failed"); break;
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
