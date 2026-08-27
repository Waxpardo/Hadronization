#include "../generation/registries/GeneratedHeavyFlavourRegistry.h"
#include "../generation/registries/GeneratedTuneSettingRegistry.h"
#include "../generation/producer/HeavyFlavourUtils.h"
#include "../contracts/GeneratedPairRegistry.h"

#include "TFile.h"
#include "TTree.h"

#include <nlohmann/json.hpp>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using json = nlohmann::json;
using Hadronization::Origin;

constexpr const char* kExtractSchema =
    "hf_gate_b_pthat_sensitivity_extract_v1";

template <typename T>
bool ReadScalar(TTree* tree, const char* name, T& value) {
  if (!tree || !tree->GetBranch(name)) return false;
  tree->SetBranchAddress(name, &value);
  const bool ok = tree->GetEntry(0) > 0;
  tree->ResetBranchAddresses();
  return ok;
}

bool ReadString(TTree* tree, const char* name, std::string& value) {
  if (!tree || !tree->GetBranch(name)) return false;
  std::string* pointer = nullptr;
  tree->SetBranchAddress(name, &pointer);
  const bool ok = tree->GetEntry(0) > 0 && pointer;
  if (ok) value = *pointer;
  tree->ResetBranchAddresses();
  return ok;
}

bool Finite(double value) { return std::isfinite(value); }

std::size_t FindBin(double value, const std::vector<double>& edges) {
  if (!Finite(value) || edges.size() < 2 || value < edges.front() ||
      value >= edges.back()) {
    return edges.size();
  }
  const auto upper = std::upper_bound(edges.begin(), edges.end(), value);
  return static_cast<std::size_t>(
      std::distance(edges.begin(), upper) - 1);
}

struct TriggerGroup {
  std::string name;
  std::string sector;
  std::set<int> pdgs;
};

struct YieldGroup {
  std::string name;
  std::string sector;
  std::string triggerGroup;
  std::set<int> associateAbsPdgs;
};

struct RatioDefinition {
  std::string name;
  std::string numerator;
  std::string denominator;
};

struct TriggerSums {
  std::uint64_t count = 0;
  double weight = 0.0;
  std::vector<std::uint64_t> ptCounts;
  std::vector<double> ptWeights;
  std::uint64_t candidateCount = 0;
  double candidateWeight = 0.0;
  std::uint64_t selectedHardCount = 0;
  double selectedHardWeight = 0.0;
  std::uint64_t unresolvedCount = 0;
  double unresolvedWeight = 0.0;
  std::uint64_t resolvedNonselectedCount = 0;
  double resolvedNonselectedWeight = 0.0;
  std::uint64_t invalidSelectedHardCount = 0;
  double invalidSelectedHardWeight = 0.0;
};

struct YieldSums {
  std::uint64_t osCount = 0;
  std::uint64_t ssCount = 0;
  double osWeight = 0.0;
  double ssWeight = 0.0;
};

struct BlockSums {
  std::uint64_t eventCount = 0;
  double sumWeights = 0.0;
  double sumWeights2 = 0.0;
  std::uint64_t negativeWeightEvents = 0;
  std::uint64_t zeroWeightEvents = 0;
  double minimumWeight = std::numeric_limits<double>::infinity();
  double maximumWeight = -std::numeric_limits<double>::infinity();
  double weightedMultiplicity = 0.0;
  std::vector<std::uint64_t> multiplicityCounts;
  std::vector<double> multiplicityWeights;
  std::uint64_t multiplicityOutOfRange = 0;
  std::map<int, std::uint64_t> processCounts;
  std::map<int, double> processWeights;
  std::map<int, std::uint64_t> hardChannelCounts;
  std::map<int, double> hardChannelWeights;
  std::map<std::string, TriggerSums> triggers;
  std::map<std::string, YieldSums> yields;
  std::map<std::string, std::map<int, std::uint64_t>> originCounts;
  std::map<std::string, std::map<int, double>> originWeights;
  std::uint64_t triggerPtOutOfRange = 0;
  std::uint64_t sameHardPairs = 0;
};

bool EligibleBase(int pdg, int status, int isFinal, int central, double pt,
                  double eta, bool trigger) {
  return isFinal && central && Hadronization::FindGroundState(pdg) &&
         Hadronization::IsDirectPrimaryStatus(status) &&
         Hadronization::IsCentralKinematic(pt, eta, trigger);
}

int SectorCharge(const std::string& sector, int qc, int qb) {
  return sector == "charm" ? qc : qb;
}

int SectorOrigin(const std::string& sector, int originC, int originB) {
  return sector == "charm" ? originC : originB;
}

int SectorHard(const std::string& sector, int hardC, int hardB) {
  return sector == "charm" ? hardC : hardB;
}

int AssociateOriginCategory(int origin, int associateHard, int triggerHard,
                            int associateCharge, int triggerCharge) {
  if (origin == static_cast<int>(Origin::kSelectedHard)) {
    if (associateHard >= 0 && associateHard != triggerHard &&
        associateCharge * triggerCharge < 0) {
      return 1;
    }
    return 2;
  }
  if (origin == static_cast<int>(Origin::kShower)) return 3;
  if (origin == static_cast<int>(Origin::kMPI)) return 4;
  if (origin == static_cast<int>(Origin::kOtherResolved)) return 5;
  return 6;
}

json IntegerMap(const std::map<int, std::uint64_t>& values) {
  json result = json::object();
  for (const auto& [key, value] : values) {
    result[std::to_string(key)] = value;
  }
  return result;
}

json DoubleMap(const std::map<int, double>& values) {
  json result = json::object();
  for (const auto& [key, value] : values) {
    result[std::to_string(key)] = value;
  }
  return result;
}

void PutFiniteOrNull(json& object, const std::string& key, double value) {
  object[key] = Finite(value) ? json(value) : json(nullptr);
}

std::string ThresholdLabel(double value) {
  std::ostringstream stream;
  stream << std::fixed << std::setprecision(1) << value;
  return stream.str();
}

}  // namespace

int ExtractPTHatSensitivity(const char* inputFile, const char* configFile,
                            const char* outputJson,
                            const char* expectedCampaign,
                            int expectedCampaignOrdinal,
                            const char* expectedTune, int expectedLogicalId,
                            const char* expectedRole, int expectedAttempt,
                            int expectedSeed,
                            unsigned long long expectedRequestedSuccesses,
                            double expectedPthatMin,
                            const char* expectedRepositoryCommit,
                            const char* expectedConfigSha256,
                            const char* expectedExecutableSha256,
                            const char* expectedTuneAllowlistSha256) {
  try {
    if (!inputFile || !configFile || !outputJson || !expectedCampaign ||
        !expectedTune || !expectedRole || !expectedRepositoryCommit ||
        !expectedConfigSha256 || !expectedExecutableSha256 ||
        !expectedTuneAllowlistSha256) {
      throw std::invalid_argument("null pTHat extractor argument");
    }

    std::ifstream configStream(configFile);
    if (!configStream) {
      throw std::runtime_error(std::string("cannot open spec ") + configFile);
    }
    const json spec = json::parse(configStream);
    if (spec.value("schema", "") !=
            "hf_gate_b_pthat_sensitivity_spec_v1" ||
        !spec.value("frozen", false)) {
      throw std::runtime_error("pTHat sensitivity spec is not frozen v1");
    }
    const json rawContract = spec.at("raw_contract");
    if (rawContract.at("raw_schema").get<std::string>() !=
            Hadronization::kRawSchema ||
        rawContract.at("selector").get<std::string>() !=
            Hadronization::kSelectorVersion ||
        rawContract.at("origin_algorithm").get<std::string>() !=
            Hadronization::kOriginAlgorithmVersion) {
      throw std::runtime_error("spec differs from compiled raw contract");
    }
    const int blockCount = spec.at("blocks").at("count").get<int>();
    if (blockCount != 10 ||
        spec.at("blocks").at("assignment").get<std::string>() !=
            "unsigned_event_id_modulo") {
      throw std::runtime_error("unsupported block contract");
    }
    const json decision = spec.at("decision");
    const json frozenMargins = {
        {"multiplicity_mean", 0.048790164169432},
        {"multiplicity_shape", 0.095310179804325},
        {"trigger_rate_per_generated_event", 0.139761942375159},
        {"trigger_pt_shape", 0.139761942375159},
        {"os_yield", 0.139761942375159},
        {"ss_yield", 0.139761942375159},
        {"balancing_yield", 0.139761942375159},
        {"baryon_meson_ratio", 0.182321556793955}};
    if (decision.at("familywise_alpha").get<double>() != 0.05 ||
        decision.at("predeclared_family_comparisons").get<int>() != 192 ||
        decision.at("critical_distribution").get<std::string>() !=
            "student_t" ||
        decision.at("conservative_degrees_of_freedom").get<int>() != 9 ||
        decision.at("bonferroni_critical_value").get<double>() !=
            5.797108070583989 ||
        decision.at("bonferroni_critical_value_definition")
                .get<std::string>() !=
            "t_9 quantile at 1 - 0.05/(2*192)" ||
        decision.at("margins_max_abs_log_ratio") != frozenMargins) {
      throw std::runtime_error(
          "pTHat simultaneous-decision contract differs from frozen values");
    }
    const double sameSignFactor =
        spec.at("selection").at("same_sign_pair_factor").get<double>();
    const json selection = spec.at("selection");
    if (sameSignFactor != 1.0 ||
        selection.at("direct_primary_status_min").get<int>() != 81 ||
        selection.at("direct_primary_status_max").get<int>() != 89 ||
        !selection.at("require_positive_status").get<bool>() ||
        !selection.at("require_final").get<bool>() ||
        !selection.at("require_central_ground_state").get<bool>() ||
        selection.at("trigger_pt_min_exclusive_gev").get<double>() != 1.0 ||
        selection.at("associate_pt_min_exclusive_gev").get<double>() != 0.15 ||
        selection.at("abs_eta_max_inclusive").get<double>() != 4.0 ||
        selection.at("trigger_origin").get<std::string>() !=
            "selected_hard" ||
        selection.at("associate_origins").get<std::string>() != "inclusive" ||
        !selection.at("ordered_pairs").get<bool>() ||
        selection.at("pair_combinatorics_mode").get<std::string>() !=
            "ordered_conditional_v1" ||
        !selection.at("exclude_same_event_record_index").get<bool>()) {
      throw std::runtime_error(
          "spec selection differs from the compiled Paul-selector contract");
    }
    const std::vector<double> ptEdges =
        spec.at("trigger_pt_bins_gev").get<std::vector<double>>();
    const std::vector<double> requiredPtEdges = {
        1.0, 2.0, 4.0, 8.0, 16.0, 7000.0};
    if (ptEdges != requiredPtEdges) {
      throw std::runtime_error(
          "frozen trigger-pT diagnostic binning changed");
    }
    if (spec.at("trigger_pt_diagnostic_overflow_policy").get<std::string>() !=
        "report_and_fail_closed_without_excluding_from_integrated_yields") {
      throw std::runtime_error("trigger-pT overflow policy changed");
    }
    const std::vector<double> multiplicityEdges =
        spec.at("multiplicity_bins").get<std::vector<double>>();
    if (!std::is_sorted(ptEdges.begin(), ptEdges.end()) ||
        !std::is_sorted(multiplicityEdges.begin(), multiplicityEdges.end()) ||
        std::adjacent_find(ptEdges.begin(), ptEdges.end()) != ptEdges.end() ||
        std::adjacent_find(multiplicityEdges.begin(),
                           multiplicityEdges.end()) != multiplicityEdges.end()) {
      throw std::runtime_error("invalid observable bin edges");
    }
    std::vector<double> diagnosticPtEdges = ptEdges;
    diagnosticPtEdges.back() =
        std::nextafter(diagnosticPtEdges.back(),
                       std::numeric_limits<double>::infinity());
    if (FindBin(ptEdges.back(), diagnosticPtEdges) !=
            diagnosticPtEdges.size() - 2 ||
        FindBin(diagnosticPtEdges.back(), diagnosticPtEdges) !=
            diagnosticPtEdges.size()) {
      throw std::runtime_error(
          "trigger-pT endpoint/overflow contract is not representable");
    }

    std::vector<TriggerGroup> triggerGroups;
    std::map<int, std::size_t> triggerLookup;
    for (const json& row : spec.at("trigger_groups")) {
      TriggerGroup group;
      group.name = row.at("name").get<std::string>();
      group.sector = row.at("sector").get<std::string>();
      for (const int pdg : row.at("pdgs").get<std::vector<int>>()) {
        if (!triggerLookup.emplace(pdg, triggerGroups.size()).second) {
          throw std::runtime_error("trigger PDG appears in multiple groups");
        }
        group.pdgs.insert(pdg);
      }
      triggerGroups.push_back(group);
    }
    std::vector<YieldGroup> yieldGroups;
    for (const json& row : spec.at("yield_groups")) {
      YieldGroup group;
      group.name = row.at("name").get<std::string>();
      group.sector = row.at("sector").get<std::string>();
      group.triggerGroup = row.at("trigger_group").get<std::string>();
      for (const int pdg :
           row.at("associate_abs_pdgs").get<std::vector<int>>()) {
        group.associateAbsPdgs.insert(std::abs(pdg));
      }
      yieldGroups.push_back(group);
    }
    std::vector<RatioDefinition> ratioDefinitions;
    for (const json& row : spec.at("baryon_meson_ratios")) {
      ratioDefinitions.push_back(
          {row.at("name").get<std::string>(),
           row.at("numerator_yield").get<std::string>(),
           row.at("denominator_yield").get<std::string>()});
    }
    std::map<std::pair<int, int>, bool> allowedPairs;
    std::set<int> compiledTriggers;
    for (const auto& pair : Hadronization::kPairDefinitions) {
      allowedPairs.emplace(
          std::make_pair(pair.triggerPdg, pair.associatePdg),
          std::string(pair.heavySign) == "OS");
      compiledTriggers.insert(pair.triggerPdg);
    }
    std::set<int> configuredTriggers;
    for (const auto& [pdg, index] : triggerLookup) {
      (void)index;
      configuredTriggers.insert(pdg);
    }
    if (configuredTriggers != compiledTriggers) {
      throw std::runtime_error(
          "spec trigger groups differ from the compiled pair registry");
    }

    TFile input(inputFile, "READ");
    if (input.IsZombie()) {
      throw std::runtime_error(std::string("cannot open raw input ") +
                               inputFile);
    }
    auto* tree = dynamic_cast<TTree*>(input.Get("tree"));
    auto* metadata = dynamic_cast<TTree*>(input.Get("job_metadata"));
    if (!tree || !metadata || metadata->GetEntries() != 1) {
      throw std::runtime_error("raw input lacks tree/job_metadata");
    }

    std::string campaign;
    std::string tune;
    std::string role;
    std::string rawSchema;
    std::string selector;
    std::string originAlgorithm;
    std::string speciesRegistrySha256;
    std::string tuneAllowlistSchema;
    std::string tuneAllowlistSha256;
    std::string configSha256;
    std::string executableSha256;
    std::string repositoryCommit;
    std::string repositoryDirty;
    int campaignOrdinal = -1;
    int logicalId = -1;
    int attempt = -1;
    int seed = -1;
    int complete = 0;
    unsigned long long requestedSuccesses = 0;
    unsigned long long successfulEvents = 0;
    unsigned long long treeEntries = 0;
    unsigned long long duplicateGroupsCharm = 0;
    unsigned long long duplicateGroupsBeauty = 0;
    unsigned long long duplicateDemotionsCharm = 0;
    unsigned long long duplicateDemotionsBeauty = 0;
    unsigned long long multiHeavyCharm = 0;
    unsigned long long multiHeavyBeauty = 0;
    double phaseSpacePthatMin = 0.0;
    double sigmaGenMb = 0.0;
    double sigmaErrMb = 0.0;
    double pythiaWeightSum = 0.0;
    double metadataSumWeights = 0.0;
    double metadataSumWeights2 = 0.0;

    if (!ReadString(metadata, "campaign", campaign) ||
        !ReadString(metadata, "tune", tune) ||
        !ReadString(metadata, "role", role) ||
        !ReadString(metadata, "raw_schema", rawSchema) ||
        !ReadString(metadata, "selector", selector) ||
        !ReadString(metadata, "origin_algorithm", originAlgorithm) ||
        !ReadString(metadata, "species_registry_sha256",
                    speciesRegistrySha256) ||
        !ReadString(metadata, "tune_difference_allowlist_schema",
                    tuneAllowlistSchema) ||
        !ReadString(metadata, "tune_difference_allowlist_sha256",
                    tuneAllowlistSha256) ||
        !ReadString(metadata, "config_sha256", configSha256) ||
        !ReadString(metadata, "executable_sha256", executableSha256) ||
        !ReadString(metadata, "repository_commit", repositoryCommit) ||
        !ReadString(metadata, "repository_dirty", repositoryDirty) ||
        !ReadScalar(metadata, "campaign_ordinal", campaignOrdinal) ||
        !ReadScalar(metadata, "logical_id", logicalId) ||
        !ReadScalar(metadata, "attempt", attempt) ||
        !ReadScalar(metadata, "seed", seed) ||
        !ReadScalar(metadata, "complete", complete) ||
        !ReadScalar(metadata, "requested_successes", requestedSuccesses) ||
        !ReadScalar(metadata, "successful_events", successfulEvents) ||
        !ReadScalar(metadata, "tree_entries", treeEntries) ||
        !ReadScalar(metadata, "phase_space_pthat_min",
                    phaseSpacePthatMin) ||
        !ReadScalar(metadata, "pythia_sigma_gen_mb", sigmaGenMb) ||
        !ReadScalar(metadata, "pythia_sigma_err_mb", sigmaErrMb) ||
        !ReadScalar(metadata, "pythia_weight_sum", pythiaWeightSum) ||
        !ReadScalar(metadata, "sum_weights", metadataSumWeights) ||
        !ReadScalar(metadata, "sum_weights2", metadataSumWeights2) ||
        !ReadScalar(metadata,
                    "duplicate_hard_carrier_conflict_groups_charm",
                    duplicateGroupsCharm) ||
        !ReadScalar(metadata,
                    "duplicate_hard_carrier_conflict_groups_beauty",
                    duplicateGroupsBeauty) ||
        !ReadScalar(metadata, "duplicate_hard_carrier_demotions_charm",
                    duplicateDemotionsCharm) ||
        !ReadScalar(metadata, "duplicate_hard_carrier_demotions_beauty",
                    duplicateDemotionsBeauty) ||
        !ReadScalar(metadata,
                    "multi_heavy_constituent_rejections_charm",
                    multiHeavyCharm) ||
        !ReadScalar(metadata,
                    "multi_heavy_constituent_rejections_beauty",
                    multiHeavyBeauty)) {
      throw std::runtime_error("raw metadata is incomplete for sensitivity");
    }
    const double pthatTolerance =
        std::max(1.0e-12, std::abs(expectedPthatMin) * 1.0e-12);
    if (campaign != expectedCampaign ||
        campaignOrdinal != expectedCampaignOrdinal ||
        tune != expectedTune || logicalId != expectedLogicalId ||
        role != expectedRole || attempt != expectedAttempt ||
        seed != expectedSeed ||
        requestedSuccesses != expectedRequestedSuccesses ||
        rawSchema != rawContract.at("raw_schema").get<std::string>() ||
        selector != rawContract.at("selector").get<std::string>() ||
        originAlgorithm !=
            rawContract.at("origin_algorithm").get<std::string>() ||
        std::abs(phaseSpacePthatMin - expectedPthatMin) > pthatTolerance ||
        tuneAllowlistSchema !=
            std::string(Hadronization::kTuneDifferenceAllowlistSchema) ||
        tuneAllowlistSha256 != expectedTuneAllowlistSha256 ||
        std::string(expectedTuneAllowlistSha256) !=
            std::string(Hadronization::kTuneDifferenceAllowlistSha256) ||
        configSha256 != expectedConfigSha256 ||
        executableSha256 != expectedExecutableSha256 ||
        repositoryCommit != expectedRepositoryCommit ||
        repositoryDirty != "false" || complete != 1 ||
        requestedSuccesses != successfulEvents ||
        treeEntries != successfulEvents ||
        static_cast<unsigned long long>(tree->GetEntries()) !=
            successfulEvents) {
      throw std::runtime_error("raw identity/contract mismatch");
    }
    if (!Finite(sigmaGenMb) || sigmaGenMb <= 0.0 ||
        !Finite(sigmaErrMb) || sigmaErrMb < 0.0 ||
        !Finite(pythiaWeightSum) || !Finite(metadataSumWeights) ||
        !Finite(metadataSumWeights2) || metadataSumWeights2 <= 0.0) {
      throw std::runtime_error("invalid structured normalization metadata");
    }

    const std::vector<const char*> requiredBranches = {
        "event_id",
        "process_code",
        "hard_channel",
        "event_weight",
        "multiplicity_primary_charged_eta10_v1",
        "heavyIndex",
        "heavyPdg",
        "heavyStatus",
        "heavyIsFinal",
        "heavyCentral",
        "heavyQc",
        "heavyQb",
        "heavyOriginC",
        "heavyOriginB",
        "heavyMatchResolutionC",
        "heavyMatchResolutionB",
        "heavyMatchedHardC",
        "heavyMatchedHardB",
        "heavyRejectedHardC",
        "heavyRejectedHardB",
        "heavyPt",
        "heavyEta",
        "heavyPhi"};
    for (const char* branch : requiredBranches) {
      if (!tree->GetBranch(branch)) {
        throw std::runtime_error(std::string("missing raw-v5 branch ") +
                                 branch);
      }
    }

    ULong64_t eventId = 0;
    Int_t processCode = 0;
    Int_t hardChannel = 0;
    Double_t eventWeight = 0.0;
    Int_t multiplicity = 0;
    std::vector<int>* heavyIndex = nullptr;
    std::vector<int>* heavyPdg = nullptr;
    std::vector<int>* heavyStatus = nullptr;
    std::vector<int>* heavyIsFinal = nullptr;
    std::vector<int>* heavyCentral = nullptr;
    std::vector<int>* heavyQc = nullptr;
    std::vector<int>* heavyQb = nullptr;
    std::vector<int>* heavyOriginC = nullptr;
    std::vector<int>* heavyOriginB = nullptr;
    std::vector<int>* heavyResolutionC = nullptr;
    std::vector<int>* heavyResolutionB = nullptr;
    std::vector<int>* heavyMatchedHardC = nullptr;
    std::vector<int>* heavyMatchedHardB = nullptr;
    std::vector<int>* heavyRejectedHardC = nullptr;
    std::vector<int>* heavyRejectedHardB = nullptr;
    std::vector<double>* heavyPt = nullptr;
    std::vector<double>* heavyEta = nullptr;
    std::vector<double>* heavyPhi = nullptr;

    tree->SetBranchAddress("event_id", &eventId);
    tree->SetBranchAddress("process_code", &processCode);
    tree->SetBranchAddress("hard_channel", &hardChannel);
    tree->SetBranchAddress("event_weight", &eventWeight);
    tree->SetBranchAddress("multiplicity_primary_charged_eta10_v1", &multiplicity);
    tree->SetBranchAddress("heavyIndex", &heavyIndex);
    tree->SetBranchAddress("heavyPdg", &heavyPdg);
    tree->SetBranchAddress("heavyStatus", &heavyStatus);
    tree->SetBranchAddress("heavyIsFinal", &heavyIsFinal);
    tree->SetBranchAddress("heavyCentral", &heavyCentral);
    tree->SetBranchAddress("heavyQc", &heavyQc);
    tree->SetBranchAddress("heavyQb", &heavyQb);
    tree->SetBranchAddress("heavyOriginC", &heavyOriginC);
    tree->SetBranchAddress("heavyOriginB", &heavyOriginB);
    tree->SetBranchAddress("heavyMatchResolutionC", &heavyResolutionC);
    tree->SetBranchAddress("heavyMatchResolutionB", &heavyResolutionB);
    tree->SetBranchAddress("heavyMatchedHardC", &heavyMatchedHardC);
    tree->SetBranchAddress("heavyMatchedHardB", &heavyMatchedHardB);
    tree->SetBranchAddress("heavyRejectedHardC", &heavyRejectedHardC);
    tree->SetBranchAddress("heavyRejectedHardB", &heavyRejectedHardB);
    tree->SetBranchAddress("heavyPt", &heavyPt);
    tree->SetBranchAddress("heavyEta", &heavyEta);
    tree->SetBranchAddress("heavyPhi", &heavyPhi);

    std::vector<BlockSums> blocks(static_cast<std::size_t>(blockCount));
    for (BlockSums& block : blocks) {
      block.multiplicityCounts.assign(multiplicityEdges.size() - 1, 0);
      block.multiplicityWeights.assign(multiplicityEdges.size() - 1, 0.0);
      for (const TriggerGroup& group : triggerGroups) {
        TriggerSums sums;
        sums.ptCounts.assign(diagnosticPtEdges.size() - 1, 0);
        sums.ptWeights.assign(diagnosticPtEdges.size() - 1, 0.0);
        block.triggers.emplace(group.name, sums);
        block.originCounts[group.sector];
        block.originWeights[group.sector];
      }
      for (const YieldGroup& group : yieldGroups) {
        block.yields.emplace(group.name, YieldSums{});
      }
    }

    std::set<ULong64_t> eventIds;
    for (Long64_t entry = 0; entry < tree->GetEntries(); ++entry) {
      if (tree->GetEntry(entry) <= 0) {
        throw std::runtime_error("failed reading raw tree entry");
      }
      if (!eventIds.insert(eventId).second) {
        throw std::runtime_error("duplicate event_id in raw input");
      }
      if (!Finite(eventWeight)) {
        throw std::runtime_error("non-finite event weight");
      }
      BlockSums& block =
          blocks[static_cast<std::size_t>(eventId %
                                          static_cast<ULong64_t>(blockCount))];
      ++block.eventCount;
      block.sumWeights += eventWeight;
      block.sumWeights2 += eventWeight * eventWeight;
      if (eventWeight < 0.0) ++block.negativeWeightEvents;
      if (eventWeight == 0.0) ++block.zeroWeightEvents;
      block.minimumWeight = std::min(block.minimumWeight, eventWeight);
      block.maximumWeight = std::max(block.maximumWeight, eventWeight);
      block.weightedMultiplicity += eventWeight * multiplicity;
      ++block.processCounts[processCode];
      block.processWeights[processCode] += eventWeight;
      ++block.hardChannelCounts[hardChannel];
      block.hardChannelWeights[hardChannel] += eventWeight;
      const std::size_t multiplicityBin =
          FindBin(static_cast<double>(multiplicity), multiplicityEdges);
      if (multiplicityBin >= block.multiplicityCounts.size()) {
        ++block.multiplicityOutOfRange;
      } else {
        ++block.multiplicityCounts[multiplicityBin];
        block.multiplicityWeights[multiplicityBin] += eventWeight;
      }

      const std::size_t size = heavyPdg ? heavyPdg->size() : 0;
      const bool vectorsValid =
          heavyIndex && heavyStatus && heavyIsFinal && heavyCentral &&
          heavyQc && heavyQb && heavyOriginC && heavyOriginB &&
          heavyResolutionC && heavyResolutionB && heavyMatchedHardC &&
          heavyMatchedHardB && heavyRejectedHardC && heavyRejectedHardB &&
          heavyPt && heavyEta && heavyPhi && heavyIndex->size() == size &&
          heavyStatus->size() == size && heavyIsFinal->size() == size &&
          heavyCentral->size() == size && heavyQc->size() == size &&
          heavyQb->size() == size && heavyOriginC->size() == size &&
          heavyOriginB->size() == size &&
          heavyResolutionC->size() == size &&
          heavyResolutionB->size() == size &&
          heavyMatchedHardC->size() == size &&
          heavyMatchedHardB->size() == size &&
          heavyRejectedHardC->size() == size &&
          heavyRejectedHardB->size() == size &&
          heavyPt->size() == size && heavyEta->size() == size &&
          heavyPhi->size() == size;
      if (!vectorsValid) {
        throw std::runtime_error("raw-v5 vector-size mismatch");
      }
      for (std::size_t index = 0; index < size; ++index) {
        if (!Finite((*heavyPt)[index]) || !Finite((*heavyEta)[index]) ||
            !Finite((*heavyPhi)[index])) {
          throw std::runtime_error("non-finite raw heavy-particle kinematics");
        }
      }

      for (std::size_t triggerIndex = 0; triggerIndex < size;
           ++triggerIndex) {
        const int triggerPdg = (*heavyPdg)[triggerIndex];
        const auto lookup = triggerLookup.find(triggerPdg);
        if (lookup == triggerLookup.end()) continue;
        const TriggerGroup& triggerGroup = triggerGroups[lookup->second];
        TriggerSums& triggerSums = block.triggers.at(triggerGroup.name);
        if (!EligibleBase(
                triggerPdg, (*heavyStatus)[triggerIndex],
                (*heavyIsFinal)[triggerIndex],
                (*heavyCentral)[triggerIndex], (*heavyPt)[triggerIndex],
                (*heavyEta)[triggerIndex], true)) {
          continue;
        }

        ++triggerSums.candidateCount;
        triggerSums.candidateWeight += eventWeight;
        const int triggerOrigin =
            SectorOrigin(triggerGroup.sector,
                         (*heavyOriginC)[triggerIndex],
                         (*heavyOriginB)[triggerIndex]);
        const int triggerHard =
            SectorHard(triggerGroup.sector,
                       (*heavyMatchedHardC)[triggerIndex],
                       (*heavyMatchedHardB)[triggerIndex]);
        const int triggerCharge =
            SectorCharge(triggerGroup.sector, (*heavyQc)[triggerIndex],
                         (*heavyQb)[triggerIndex]);
        if (triggerOrigin == static_cast<int>(Origin::kUnresolved)) {
          ++triggerSums.unresolvedCount;
          triggerSums.unresolvedWeight += eventWeight;
        } else if (triggerOrigin != static_cast<int>(Origin::kSelectedHard)) {
          ++triggerSums.resolvedNonselectedCount;
          triggerSums.resolvedNonselectedWeight += eventWeight;
        }
        if (triggerOrigin != static_cast<int>(Origin::kSelectedHard)) continue;
        if (triggerHard < 0 || triggerCharge == 0) {
          ++triggerSums.invalidSelectedHardCount;
          triggerSums.invalidSelectedHardWeight += eventWeight;
          continue;
        }
        ++triggerSums.selectedHardCount;
        triggerSums.selectedHardWeight += eventWeight;
        ++triggerSums.count;
        triggerSums.weight += eventWeight;
        const std::size_t ptBin =
            FindBin((*heavyPt)[triggerIndex], diagnosticPtEdges);
        if (ptBin >= triggerSums.ptCounts.size()) {
          ++block.triggerPtOutOfRange;
        } else {
          ++triggerSums.ptCounts[ptBin];
          triggerSums.ptWeights[ptBin] += eventWeight;
        }

        for (std::size_t associateIndex = 0; associateIndex < size;
             ++associateIndex) {
          if ((*heavyIndex)[associateIndex] ==
              (*heavyIndex)[triggerIndex]) {
            continue;
          }
          const int associatePdg = (*heavyPdg)[associateIndex];
          const auto allowed =
              allowedPairs.find({triggerPdg, associatePdg});
          if (allowed == allowedPairs.end()) continue;
          if (!EligibleBase(
                  associatePdg, (*heavyStatus)[associateIndex],
                  (*heavyIsFinal)[associateIndex],
                  (*heavyCentral)[associateIndex],
                  (*heavyPt)[associateIndex],
                  (*heavyEta)[associateIndex], false)) {
            continue;
          }
          const int associateCharge =
              SectorCharge(triggerGroup.sector,
                           (*heavyQc)[associateIndex],
                           (*heavyQb)[associateIndex]);
          if (associateCharge == 0) continue;
          const bool os = triggerCharge * associateCharge < 0;
          if (os != allowed->second) {
            throw std::runtime_error(
                "pair-registry heavy-sign mismatch in pTHat extraction");
          }
          const int associateHard =
              SectorHard(triggerGroup.sector,
                         (*heavyMatchedHardC)[associateIndex],
                         (*heavyMatchedHardB)[associateIndex]);
          if (associateHard >= 0 && associateHard == triggerHard) {
            ++block.sameHardPairs;
            continue;
          }
          const int associateOrigin =
              SectorOrigin(triggerGroup.sector,
                           (*heavyOriginC)[associateIndex],
                           (*heavyOriginB)[associateIndex]);
          const int originCategory = AssociateOriginCategory(
              associateOrigin, associateHard, triggerHard, associateCharge,
              triggerCharge);
          ++block.originCounts[triggerGroup.sector][originCategory];
          block.originWeights[triggerGroup.sector][originCategory] +=
              eventWeight;
          for (const YieldGroup& yieldGroup : yieldGroups) {
            if (yieldGroup.triggerGroup != triggerGroup.name ||
                yieldGroup.sector != triggerGroup.sector ||
                !yieldGroup.associateAbsPdgs.count(
                    std::abs(associatePdg))) {
              continue;
            }
            YieldSums& sums = block.yields.at(yieldGroup.name);
            if (os) {
              ++sums.osCount;
              sums.osWeight += eventWeight;
            } else {
              ++sums.ssCount;
              sums.ssWeight += eventWeight;
            }
          }
        }
      }
    }

    json output;
    output["schema"] = kExtractSchema;
    output["spec_schema"] = spec.at("schema");
    output["identity"] = {
        {"campaign", campaign},
        {"tune", tune},
        {"logical_id", logicalId},
        {"attempt", attempt},
        {"seed", seed},
        {"pthat_min", ThresholdLabel(phaseSpacePthatMin)},
        {"input_file", std::filesystem::absolute(inputFile).string()}};
    output["raw_contract"] = {
        {"raw_schema", rawSchema},
        {"selector", selector},
        {"origin_algorithm", originAlgorithm},
        {"species_registry_sha256", speciesRegistrySha256}};
    output["production_provenance"] = {
        {"campaign_ordinal", campaignOrdinal},
        {"role", role},
        {"config_sha256", configSha256},
        {"executable_sha256", executableSha256},
        {"repository_commit", repositoryCommit},
        {"repository_dirty", repositoryDirty},
        {"tune_difference_allowlist_schema", tuneAllowlistSchema},
        {"tune_difference_allowlist_sha256", tuneAllowlistSha256}};
    output["normalization_metadata"] = {
        {"pythia_sigma_gen_mb", sigmaGenMb},
        {"pythia_sigma_err_mb", sigmaErrMb},
        {"pythia_weight_sum", pythiaWeightSum},
        {"tree_sum_weights", metadataSumWeights},
        {"tree_sum_weights2", metadataSumWeights2},
        {"interpretation",
         "Structured PYTHIA metadata; unweighted event counts are not cross "
         "sections"}};
    output["origin_rejection_metadata"] = {
        {"duplicate_conflict_groups_charm", duplicateGroupsCharm},
        {"duplicate_conflict_groups_beauty", duplicateGroupsBeauty},
        {"duplicate_demotions_charm", duplicateDemotionsCharm},
        {"duplicate_demotions_beauty", duplicateDemotionsBeauty},
        {"multi_heavy_rejections_charm", multiHeavyCharm},
        {"multi_heavy_rejections_beauty", multiHeavyBeauty}};
    output["event_accounting"] = {
        {"requested_successes", requestedSuccesses},
        {"successful_events", successfulEvents},
        {"tree_entries", treeEntries},
        {"unique_event_ids", eventIds.size()}};
    output["block_assignment"] = {
        {"method", "unsigned_event_id_modulo"}, {"count", blockCount}};
    output["pair_combinatorics"] = {
        {"mode", "ordered_conditional_v1"},
        {"same_sign_pair_factor", sameSignFactor}};
    output["trigger_pt_diagnostic"] = {
        {"configured_upper_edge_gev", ptEdges.back()},
        {"upper_edge_inclusive_via_nextafter", true},
        {"overflow_policy",
         "report_and_fail_closed_without_excluding_from_integrated_yields"}};
    output["blocks"] = json::array();

    for (std::size_t blockIndex = 0; blockIndex < blocks.size();
         ++blockIndex) {
      const BlockSums& block = blocks[blockIndex];
      json row;
      row["block"] = blockIndex;
      row["unweighted_event_count"] = block.eventCount;
      row["event_weight_sum"] = block.sumWeights;
      row["event_weight_sum2"] = block.sumWeights2;
      row["negative_weight_events"] = block.negativeWeightEvents;
      row["zero_weight_events"] = block.zeroWeightEvents;
      PutFiniteOrNull(row, "minimum_event_weight", block.minimumWeight);
      PutFiniteOrNull(row, "maximum_event_weight", block.maximumWeight);
      PutFiniteOrNull(
          row, "effective_events",
          block.sumWeights2 > 0.0
              ? block.sumWeights * block.sumWeights / block.sumWeights2
              : std::numeric_limits<double>::quiet_NaN());
      row["process_counts_unweighted"] = IntegerMap(block.processCounts);
      row["process_weight_sums"] = DoubleMap(block.processWeights);
      row["hard_channel_counts_unweighted"] =
          IntegerMap(block.hardChannelCounts);
      row["hard_channel_weight_sums"] =
          DoubleMap(block.hardChannelWeights);
      row["multiplicity"] = {
          {"weighted_sum", block.weightedMultiplicity},
          {"bin_counts_unweighted", block.multiplicityCounts},
          {"bin_weight_sums", block.multiplicityWeights},
          {"out_of_range", block.multiplicityOutOfRange}};
      row["triggers"] = json::object();
      for (const TriggerGroup& group : triggerGroups) {
        const TriggerSums& sums = block.triggers.at(group.name);
        row["triggers"][group.name] = {
            {"unweighted_count", sums.count},
            {"weight_sum", sums.weight},
            {"pt_bin_counts_unweighted", sums.ptCounts},
            {"pt_bin_weight_sums", sums.ptWeights},
            {"candidate_count", sums.candidateCount},
            {"candidate_weight", sums.candidateWeight},
            {"selected_hard_count", sums.selectedHardCount},
            {"selected_hard_weight", sums.selectedHardWeight},
            {"unresolved_count", sums.unresolvedCount},
            {"unresolved_weight", sums.unresolvedWeight},
            {"resolved_nonselected_count",
             sums.resolvedNonselectedCount},
            {"resolved_nonselected_weight",
             sums.resolvedNonselectedWeight},
            {"invalid_selected_hard_count",
             sums.invalidSelectedHardCount},
            {"invalid_selected_hard_weight",
             sums.invalidSelectedHardWeight}};
      }
      row["yields"] = json::object();
      for (const YieldGroup& group : yieldGroups) {
        const YieldSums& sums = block.yields.at(group.name);
        const TriggerSums& triggers =
            block.triggers.at(group.triggerGroup);
        const double value =
            triggers.weight != 0.0
                ? (sums.osWeight - sameSignFactor * sums.ssWeight) /
                      triggers.weight
                : std::numeric_limits<double>::quiet_NaN();
        json yield = {
            {"trigger_count", triggers.count},
            {"trigger_weight", triggers.weight},
            {"os_pair_count", sums.osCount},
            {"ss_pair_count", sums.ssCount},
            {"os_pair_weight", sums.osWeight},
            {"ss_pair_weight", sums.ssWeight},
            {"pair_combinatorics_mode", "ordered_conditional_v1"},
            {"same_sign_pair_factor", sameSignFactor}};
        PutFiniteOrNull(yield, "value", value);
        row["yields"][group.name] = yield;
      }
      row["baryon_meson_ratios"] = json::object();
      for (const RatioDefinition& ratio : ratioDefinitions) {
        const json& numerator = row["yields"].at(ratio.numerator);
        const json& denominator = row["yields"].at(ratio.denominator);
        double value = std::numeric_limits<double>::quiet_NaN();
        if (!numerator.at("value").is_null() &&
            !denominator.at("value").is_null()) {
          const double denominatorValue =
              denominator.at("value").get<double>();
          if (denominatorValue != 0.0) {
            value =
                numerator.at("value").get<double>() / denominatorValue;
          }
        }
        json ratioOutput;
        PutFiniteOrNull(ratioOutput, "value", value);
        row["baryon_meson_ratios"][ratio.name] = ratioOutput;
      }
      row["associate_origin_counts"] = json::object();
      row["associate_origin_weight_sums"] = json::object();
      for (const TriggerGroup& group : triggerGroups) {
        row["associate_origin_counts"][group.sector] =
            IntegerMap(block.originCounts.at(group.sector));
        row["associate_origin_weight_sums"][group.sector] =
            DoubleMap(block.originWeights.at(group.sector));
      }
      row["technical_diagnostics"] = {
          {"multiplicity_out_of_range", block.multiplicityOutOfRange},
          {"trigger_pt_out_of_range", block.triggerPtOutOfRange},
          {"same_hard_pairs", block.sameHardPairs}};
      output["blocks"].push_back(row);
    }

    const std::filesystem::path destination(outputJson);
    if (!destination.parent_path().empty()) {
      std::filesystem::create_directories(destination.parent_path());
    }
    const std::filesystem::path temporary =
        destination.string() + ".partial";
    {
      std::ofstream stream(temporary);
      if (!stream) {
        throw std::runtime_error("cannot create extraction output");
      }
      stream << output.dump(2) << "\n";
      stream.flush();
      if (!stream) {
        throw std::runtime_error("failed writing extraction output");
      }
    }
    std::filesystem::rename(temporary, destination);
    std::cout << "PTHAT_EXTRACTION_PASS"
              << " tune=" << tune
              << " pthat_min=" << ThresholdLabel(phaseSpacePthatMin)
              << " events=" << successfulEvents
              << " blocks=" << blockCount << "\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "PTHAT_EXTRACTION_FAIL " << error.what() << "\n";
    return 1;
  }
}
