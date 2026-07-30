// One-pass central publication analysis.
//
// Reads the canonical raw schema once and emits the Paul-compatible ROOT
// object contract for every signed pair in GeneratedPairRegistry.h.

#include "GeneratedPairRegistry.h"
#include "AssociateOriginCategoryContract.h"
#include "../SimulationScripts/GeneratedHeavyFlavourRegistry.h"
#include "../SimulationScripts/GeneratedTuneSettingRegistry.h"
#include "../SimulationScripts/HeavyFlavourUtils.h"

#include "TChain.h"
#include "TFile.h"
#include "TBranch.h"
#include "TLeaf.h"
#include "TH1D.h"
#include "THnSparse.h"
#include "TObjString.h"
#include "TParameter.h"
#include "TSystem.h"
#include "TTree.h"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <tuple>
#include <utility>
#include <vector>

namespace {

using Hadronization::Origin;

constexpr const char* kRequiredRawSchema = "hf_primary_ground_raw_v5";
constexpr const char* kRequiredOriginAlgorithm =
    "signed_heavy_constituent_complete_mothers_unique_v4";
constexpr const char* kRequiredEffectiveSettingsSchema =
    "effective_pythia_settings_exhaustive_v2";
constexpr const char* kAnalysisSchema =
    "paul_pair_objects_primary_ground_v2";
constexpr const char* kAnalysisImplementation =
    "one_pass_primary_ground_pair_analysis_v2";
constexpr const char* kAnalysisVersion =
    "status_analysis_THnSparse_qq_v2";
constexpr const char* kPairCombinatoricsMode =
    "ordered_conditional_v1";
constexpr const char* kAllEventsFilter = "all_events_v1";
constexpr const char* kModuloEventFilter =
    "unsigned_event_id_modulo_v1";
constexpr const char* kRawInputValidationContract =
    "analysis_raw_input_fail_closed_v1";
struct RawInputContract {
  std::string campaign;
  std::string tune;
  std::string rawSchema;
  std::string selector;
  std::string originAlgorithm;
  std::string speciesRegistrySha256;
  std::string tuneDifferenceAllowlistSchema;
  std::string tuneDifferenceAllowlistSha256;
  std::string heavyStabilityAuditSchema;
  std::string heavyStabilityAuditSha256;
  std::string effectiveSettingsSchema;
  std::string effectiveSettingsSha256;
  std::string repositoryCommit;
  std::string repositoryDirty;
  std::string executableSha256;
  int logicalId = -1;
  int complete = 0;
  unsigned long long requestedSuccesses = 0;
  unsigned long long attempts = 0;
  unsigned long long successfulEvents = 0;
  unsigned long long failedAttempts = 0;
  unsigned long long treeEntries = 0;
  unsigned long long contentDecodeFailures = 0;
  unsigned long long heavyFlavourConservationFailures = 0;
  unsigned long long originClassificationFailures = 0;
  unsigned long long primaryAllHeavyMatchFailures = 0;
  unsigned long long multiplicityOverflow = 0;
  unsigned long long multiplicityStrongEmOverflow = 0;
  double sumWeights = 0.0;
  double sumWeights2 = 0.0;
};

struct PairAccumulator {
  const Hadronization::PairDefinition* definition = nullptr;
  THnSparseD* associate = nullptr;
  THnSparseD* correlation = nullptr;
  THnSparseD* correlationByOrigin = nullptr;
  double weightedPairs = 0.0;
  unsigned long long pairs = 0;
};

struct TriggerAccumulator {
  int pdg = 0;
  std::string sector;
  THnSparseD* histogram = nullptr;
  double weightedTriggers = 0.0;
  unsigned long long triggers = 0;
};

std::vector<std::string> ResolveInputs(const std::string& input) {
  if (input.size() >= 4 && input.substr(input.size() - 4) == ".txt") {
    throw std::runtime_error(
        "central analysis accepts one manifest-selected raw job at a time; "
        "analyze independent seeds separately and merge only through "
        "MergeCanonicalAnalysis.C");
  }
  return {input};
}

bool ReadMetadataString(TTree* tree, const char* name, std::string& value) {
  if (!tree) return false;
  TBranch* branch = tree->GetBranch(name);
  if (!branch) return false;
  const std::string className = branch->GetClassName();
  if (className != "string" && className != "std::string") return false;
  std::string* pointer = nullptr;
  tree->SetBranchAddress(name, &pointer);
  const bool ok = tree->GetEntry(0) > 0 && pointer;
  if (ok) value = *pointer;
  tree->ResetBranchAddresses();
  return ok;
}

template <typename T>
bool ReadMetadataScalar(TTree* tree, const char* name, T& value) {
  if (!tree) return false;
  TBranch* branch = tree->GetBranch(name);
  if (!branch || std::string(branch->GetClassName()).size() != 0U) {
    return false;
  }
  TLeaf* leaf = branch->GetLeaf(name);
  if (!leaf || leaf->GetLenStatic() != 1) return false;
  const std::string type = leaf->GetTypeName();
  const bool correctType =
      (std::is_same_v<T, int> && type == "Int_t") ||
      (std::is_same_v<T, unsigned long long> && type == "ULong64_t") ||
      (std::is_same_v<T, double> && type == "Double_t");
  if (!correctType) return false;
  tree->SetBranchAddress(name, &value);
  const bool ok = tree->GetEntry(0) > 0;
  tree->ResetBranchAddresses();
  return ok;
}

bool HasScalarBranch(TTree* tree, const char* name, const char* type) {
  TBranch* branch = tree ? tree->GetBranch(name) : nullptr;
  TLeaf* leaf = branch ? branch->GetLeaf(name) : nullptr;
  return branch && leaf &&
         std::string(branch->GetClassName()).empty() &&
         std::string(leaf->GetTypeName()) == type &&
         leaf->GetLenStatic() == 1;
}

bool NearlyEqual(double first, double second) {
  if (!std::isfinite(first) || !std::isfinite(second)) return false;
  const double scale =
      std::max({1.0, std::abs(first), std::abs(second)});
  return std::abs(first - second) <= 1e-10 * scale;
}

bool IsLowerHex(const std::string& value, std::size_t length) {
  return value.size() == length &&
         std::all_of(value.begin(), value.end(), [](unsigned char character) {
           return std::isdigit(character) ||
                  (character >= 'a' && character <= 'f');
         });
}

std::string RequiredEnvironment(const char* name) {
  const char* value = gSystem->Getenv(name);
  if (!value || !*value) {
    throw std::runtime_error(std::string("missing required analysis provenance ") +
                             name);
  }
  return value;
}

RawInputContract ValidateRawInputs(const std::vector<std::string>& inputs) {
  const std::vector<const char*> requiredIntegerVectors = {
      "heavyIndex",          "heavyPdg",
      "heavyStatus",         "heavyIsFinal",
      "heavyCentral",        "heavyQc",
      "heavyQb",             "heavyOriginC",
      "heavyOriginB",        "heavyMatchResolutionC",
      "heavyMatchResolutionB", "heavyMatchedHardC",
      "heavyMatchedHardB",   "heavyRejectedHardC",
      "heavyRejectedHardB"};
  const std::vector<const char*> requiredDoubleVectors = {
      "heavyPt", "heavyEta", "heavyPhi"};
  const std::vector<std::tuple<const char*, const char*>>
      requiredEventScalars = {
          {"event_id", "ULong64_t"},
          {"event_weight", "Double_t"},
          {"multiplicity_hadronisation_v1", "Int_t"},
          {"heavy_flavour_conservation_ok", "Int_t"},
          {"origin_classification_valid", "Int_t"},
          {"primary_all_heavy_match_valid", "Int_t"}};
  RawInputContract common;
  bool first = true;
  std::set<int> logicalIds;
  for (const auto& input : inputs) {
    TFile file(input.c_str(), "READ");
    if (file.IsZombie()) {
      throw std::runtime_error("cannot open raw input " + input);
    }
    auto* metadata = dynamic_cast<TTree*>(file.Get("job_metadata"));
    auto* tree = dynamic_cast<TTree*>(file.Get("tree"));
    if (!metadata || metadata->GetEntries() != 1 || !tree) {
      throw std::runtime_error("missing raw tree/job_metadata in " + input);
    }
    RawInputContract current;
    if (!ReadMetadataString(metadata, "campaign", current.campaign) ||
        !ReadMetadataString(metadata, "tune", current.tune) ||
        !ReadMetadataString(metadata, "raw_schema", current.rawSchema) ||
        !ReadMetadataString(metadata, "selector", current.selector) ||
        !ReadMetadataString(metadata, "origin_algorithm",
                            current.originAlgorithm) ||
        !ReadMetadataString(metadata, "species_registry_sha256",
                            current.speciesRegistrySha256) ||
        !ReadMetadataString(metadata, "tune_difference_allowlist_schema",
                            current.tuneDifferenceAllowlistSchema) ||
        !ReadMetadataString(metadata, "tune_difference_allowlist_sha256",
                            current.tuneDifferenceAllowlistSha256) ||
        !ReadMetadataString(metadata, "heavy_stability_audit_schema",
                            current.heavyStabilityAuditSchema) ||
        !ReadMetadataString(metadata, "heavy_stability_audit_sha256",
                            current.heavyStabilityAuditSha256) ||
        !ReadMetadataString(metadata, "effective_settings_schema",
                            current.effectiveSettingsSchema) ||
        !ReadMetadataString(metadata, "effective_settings_sha256",
                            current.effectiveSettingsSha256) ||
        !ReadMetadataString(metadata, "repository_commit",
                            current.repositoryCommit) ||
        !ReadMetadataString(metadata, "repository_dirty",
                            current.repositoryDirty) ||
        !ReadMetadataString(metadata, "executable_sha256",
                            current.executableSha256) ||
        !ReadMetadataScalar(metadata, "logical_id", current.logicalId) ||
        !ReadMetadataScalar(metadata, "complete", current.complete) ||
        !ReadMetadataScalar(metadata, "requested_successes",
                            current.requestedSuccesses) ||
        !ReadMetadataScalar(metadata, "attempts", current.attempts) ||
        !ReadMetadataScalar(metadata, "successful_events",
                            current.successfulEvents) ||
        !ReadMetadataScalar(metadata, "failed_attempts",
                            current.failedAttempts) ||
        !ReadMetadataScalar(metadata, "tree_entries",
                            current.treeEntries) ||
        !ReadMetadataScalar(metadata, "content_decode_failures",
                            current.contentDecodeFailures) ||
        !ReadMetadataScalar(
            metadata, "heavy_flavour_conservation_failures",
            current.heavyFlavourConservationFailures) ||
        !ReadMetadataScalar(
            metadata, "origin_classification_failures",
            current.originClassificationFailures) ||
        !ReadMetadataScalar(metadata, "primary_all_heavy_match_failures",
                            current.primaryAllHeavyMatchFailures) ||
        !ReadMetadataScalar(metadata, "multiplicity_overflow",
                            current.multiplicityOverflow) ||
        !ReadMetadataScalar(metadata, "multiplicity_strong_em_overflow",
                            current.multiplicityStrongEmOverflow) ||
        !ReadMetadataScalar(metadata, "sum_weights", current.sumWeights) ||
        !ReadMetadataScalar(metadata, "sum_weights2",
                            current.sumWeights2)) {
      throw std::runtime_error("incomplete raw provenance in " + input);
    }
    if (current.rawSchema != kRequiredRawSchema ||
        current.selector != Hadronization::kSelectorVersion ||
        current.originAlgorithm != kRequiredOriginAlgorithm ||
        current.speciesRegistrySha256 !=
            Hadronization::kSpeciesRegistrySha256 ||
        current.tuneDifferenceAllowlistSchema !=
            Hadronization::kTuneDifferenceAllowlistSchema ||
        current.tuneDifferenceAllowlistSha256 !=
            Hadronization::kTuneDifferenceAllowlistSha256 ||
        current.heavyStabilityAuditSchema !=
            Hadronization::kHeavyStabilityAuditSchema ||
        !IsLowerHex(current.heavyStabilityAuditSha256, 64) ||
        current.effectiveSettingsSchema !=
            kRequiredEffectiveSettingsSchema ||
        !IsLowerHex(current.effectiveSettingsSha256, 64)) {
      throw std::runtime_error("raw contract mismatch in " + input);
    }
    if (!IsLowerHex(current.repositoryCommit, 40) ||
        !IsLowerHex(current.executableSha256, 64) ||
        current.complete != 1 || current.requestedSuccesses == 0 ||
        current.requestedSuccesses != current.successfulEvents ||
        current.successfulEvents != current.treeEntries ||
        current.treeEntries !=
            static_cast<unsigned long long>(tree->GetEntries()) ||
        current.attempts !=
            current.successfulEvents + current.failedAttempts ||
        current.contentDecodeFailures != 0 ||
        current.heavyFlavourConservationFailures != 0 ||
        current.originClassificationFailures != 0 ||
        current.primaryAllHeavyMatchFailures != 0 ||
        current.multiplicityOverflow != 0 ||
        current.multiplicityStrongEmOverflow != 0 ||
        !std::isfinite(current.sumWeights) ||
        !std::isfinite(current.sumWeights2) ||
        current.sumWeights2 < 0.0 ||
        current.repositoryDirty != "false" || current.campaign.empty() ||
        current.tune.empty() || current.logicalId < 0) {
      throw std::runtime_error("invalid raw implementation provenance in " +
                               input);
    }
    if (!logicalIds.insert(current.logicalId).second) {
      throw std::runtime_error("duplicate raw logical ID in input set: " +
                               input);
    }
    for (const char* branch : requiredIntegerVectors) {
      TBranch* object = tree->GetBranch(branch);
      if (!object || std::string(object->GetClassName()) != "vector<int>") {
        throw std::runtime_error(std::string("missing v5 raw branch ") +
                                 branch + " in " + input);
      }
    }
    for (const char* branch : requiredDoubleVectors) {
      TBranch* object = tree->GetBranch(branch);
      if (!object ||
          std::string(object->GetClassName()) != "vector<double>") {
        throw std::runtime_error(std::string("missing v5 raw branch ") +
                                 branch + " in " + input);
      }
    }
    for (const auto& [branch, type] : requiredEventScalars) {
      if (!HasScalarBranch(tree, branch, type)) {
        throw std::runtime_error(
            std::string("missing or incorrectly typed v5 raw scalar ") +
            branch + " in " + input);
      }
    }

    ULong64_t eventId = 0;
    Double_t eventWeight = 0.0;
    Int_t eventMultiplicity = 0;
    Int_t conservationValid = 0;
    Int_t classificationValid = 0;
    Int_t primaryAllHeavyValid = 0;
    std::vector<int>* heavyIndex = nullptr;
    std::vector<int>* heavyPdg = nullptr;
    std::vector<int>* heavyStatus = nullptr;
    std::vector<int>* heavyIsFinal = nullptr;
    std::vector<int>* heavyCentral = nullptr;
    std::vector<int>* heavyQc = nullptr;
    std::vector<int>* heavyQb = nullptr;
    std::vector<int>* heavyOriginC = nullptr;
    std::vector<int>* heavyOriginB = nullptr;
    std::vector<int>* heavyMatchResolutionC = nullptr;
    std::vector<int>* heavyMatchResolutionB = nullptr;
    std::vector<int>* heavyMatchedHardC = nullptr;
    std::vector<int>* heavyMatchedHardB = nullptr;
    std::vector<int>* heavyRejectedHardC = nullptr;
    std::vector<int>* heavyRejectedHardB = nullptr;
    std::vector<double>* heavyPt = nullptr;
    std::vector<double>* heavyEta = nullptr;
    std::vector<double>* heavyPhi = nullptr;
    tree->SetBranchAddress("event_id", &eventId);
    tree->SetBranchAddress("event_weight", &eventWeight);
    tree->SetBranchAddress("multiplicity_hadronisation_v1",
                           &eventMultiplicity);
    tree->SetBranchAddress("heavy_flavour_conservation_ok",
                           &conservationValid);
    tree->SetBranchAddress("origin_classification_valid",
                           &classificationValid);
    tree->SetBranchAddress("primary_all_heavy_match_valid",
                           &primaryAllHeavyValid);
    tree->SetBranchAddress("heavyIndex", &heavyIndex);
    tree->SetBranchAddress("heavyPdg", &heavyPdg);
    tree->SetBranchAddress("heavyStatus", &heavyStatus);
    tree->SetBranchAddress("heavyIsFinal", &heavyIsFinal);
    tree->SetBranchAddress("heavyCentral", &heavyCentral);
    tree->SetBranchAddress("heavyQc", &heavyQc);
    tree->SetBranchAddress("heavyQb", &heavyQb);
    tree->SetBranchAddress("heavyOriginC", &heavyOriginC);
    tree->SetBranchAddress("heavyOriginB", &heavyOriginB);
    tree->SetBranchAddress("heavyMatchResolutionC",
                           &heavyMatchResolutionC);
    tree->SetBranchAddress("heavyMatchResolutionB",
                           &heavyMatchResolutionB);
    tree->SetBranchAddress("heavyMatchedHardC", &heavyMatchedHardC);
    tree->SetBranchAddress("heavyMatchedHardB", &heavyMatchedHardB);
    tree->SetBranchAddress("heavyRejectedHardC", &heavyRejectedHardC);
    tree->SetBranchAddress("heavyRejectedHardB", &heavyRejectedHardB);
    tree->SetBranchAddress("heavyPt", &heavyPt);
    tree->SetBranchAddress("heavyEta", &heavyEta);
    tree->SetBranchAddress("heavyPhi", &heavyPhi);

    double observedSumWeights = 0.0;
    double observedSumWeights2 = 0.0;
    for (Long64_t entry = 0; entry < tree->GetEntries(); ++entry) {
      if (tree->GetEntry(entry) <= 0) {
        tree->ResetBranchAddresses();
        throw std::runtime_error("cannot read raw tree entry in " + input);
      }
      if (!std::isfinite(eventWeight)) {
        tree->ResetBranchAddresses();
        throw std::runtime_error("non-finite raw event weight in " + input);
      }
      if (eventMultiplicity < 0 || eventMultiplicity > 4095) {
        tree->ResetBranchAddresses();
        throw std::runtime_error("raw multiplicity outside histogram domain in " +
                                 input);
      }
      if (conservationValid != 1 || classificationValid != 1 ||
          primaryAllHeavyValid != 1) {
        tree->ResetBranchAddresses();
        throw std::runtime_error("raw event invariant flag is not true in " +
                                 input);
      }
      if (!heavyIndex || !heavyPdg || !heavyStatus || !heavyIsFinal ||
          !heavyCentral || !heavyQc || !heavyQb || !heavyOriginC ||
          !heavyOriginB || !heavyMatchResolutionC ||
          !heavyMatchResolutionB || !heavyMatchedHardC ||
          !heavyMatchedHardB || !heavyRejectedHardC ||
          !heavyRejectedHardB || !heavyPt || !heavyEta || !heavyPhi) {
        tree->ResetBranchAddresses();
        throw std::runtime_error("null raw vector branch in " + input);
      }
      const std::size_t size = heavyPdg->size();
      if (heavyIndex->size() != size || heavyStatus->size() != size ||
          heavyIsFinal->size() != size || heavyCentral->size() != size ||
          heavyQc->size() != size || heavyQb->size() != size ||
          heavyOriginC->size() != size || heavyOriginB->size() != size ||
          heavyMatchResolutionC->size() != size ||
          heavyMatchResolutionB->size() != size ||
          heavyMatchedHardC->size() != size ||
          heavyMatchedHardB->size() != size ||
          heavyRejectedHardC->size() != size ||
          heavyRejectedHardB->size() != size ||
          heavyPt->size() != size || heavyEta->size() != size ||
          heavyPhi->size() != size) {
        tree->ResetBranchAddresses();
        throw std::runtime_error("raw vector-size mismatch in " + input);
      }
      for (std::size_t particle = 0; particle < size; ++particle) {
        if (!std::isfinite((*heavyPt)[particle]) ||
            !std::isfinite((*heavyEta)[particle]) ||
            !std::isfinite((*heavyPhi)[particle])) {
          tree->ResetBranchAddresses();
          throw std::runtime_error(
              "non-finite raw heavy-hadron kinematics in " + input);
        }
      }
      observedSumWeights += eventWeight;
      observedSumWeights2 += eventWeight * eventWeight;
      if (!std::isfinite(observedSumWeights) ||
          !std::isfinite(observedSumWeights2)) {
        tree->ResetBranchAddresses();
        throw std::runtime_error("non-finite raw accumulated weights in " +
                                 input);
      }
    }
    tree->ResetBranchAddresses();
    if (!NearlyEqual(observedSumWeights, current.sumWeights) ||
        !NearlyEqual(observedSumWeights2, current.sumWeights2)) {
      throw std::runtime_error(
          "raw tree weights do not close to metadata in " + input);
    }
    if (first) {
      common = current;
      first = false;
    } else if (current.campaign != common.campaign ||
               current.tune != common.tune ||
               current.rawSchema != common.rawSchema ||
               current.selector != common.selector ||
               current.originAlgorithm != common.originAlgorithm ||
               current.speciesRegistrySha256 !=
                   common.speciesRegistrySha256 ||
               current.tuneDifferenceAllowlistSchema !=
                   common.tuneDifferenceAllowlistSchema ||
               current.tuneDifferenceAllowlistSha256 !=
                   common.tuneDifferenceAllowlistSha256 ||
               current.heavyStabilityAuditSchema !=
                   common.heavyStabilityAuditSchema ||
               current.heavyStabilityAuditSha256 !=
                   common.heavyStabilityAuditSha256 ||
               current.effectiveSettingsSchema !=
                   common.effectiveSettingsSchema ||
               current.effectiveSettingsSha256 !=
                   common.effectiveSettingsSha256 ||
               current.repositoryCommit != common.repositoryCommit ||
               current.repositoryDirty != common.repositoryDirty ||
               current.executableSha256 != common.executableSha256 ||
               current.complete != common.complete ||
               current.requestedSuccesses != common.requestedSuccesses ||
               current.attempts != common.attempts ||
               current.successfulEvents != common.successfulEvents ||
               current.failedAttempts != common.failedAttempts ||
               current.treeEntries != common.treeEntries ||
               current.contentDecodeFailures !=
                   common.contentDecodeFailures ||
               current.heavyFlavourConservationFailures !=
                   common.heavyFlavourConservationFailures ||
               current.originClassificationFailures !=
                   common.originClassificationFailures ||
               current.primaryAllHeavyMatchFailures !=
                   common.primaryAllHeavyMatchFailures ||
               current.multiplicityOverflow !=
                   common.multiplicityOverflow ||
               current.multiplicityStrongEmOverflow !=
                   common.multiplicityStrongEmOverflow) {
      throw std::runtime_error("mixed raw provenance is forbidden: " + input);
    }
  }
  return common;
}

TH1D* SumMultiplicity(const std::vector<std::string>& inputs) {
  TH1D* sum = nullptr;
  for (const auto& input : inputs) {
    TFile file(input.c_str(), "READ");
    auto* histogram = dynamic_cast<TH1D*>(file.Get("hMULTIPLICITY"));
    if (!histogram) {
      throw std::runtime_error("missing hMULTIPLICITY in " + input);
    }
    if (!sum) {
      sum = dynamic_cast<TH1D*>(histogram->Clone("summed MULTIPLICITY"));
      sum->SetDirectory(nullptr);
      sum->Reset();
      sum->Sumw2();
    }
    sum->Add(histogram);
  }
  return sum;
}

bool HistogramsExactlyCompatible(const TH1D& first, const TH1D& second) {
  if (first.GetNbinsX() != second.GetNbinsX() ||
      first.GetEntries() != second.GetEntries()) {
    return false;
  }
  for (int bin = 0; bin <= first.GetNbinsX() + 1; ++bin) {
    if (first.GetBinLowEdge(bin) != second.GetBinLowEdge(bin) ||
        first.GetBinContent(bin) != second.GetBinContent(bin) ||
        first.GetBinError(bin) != second.GetBinError(bin)) {
      return false;
    }
  }
  return true;
}

std::vector<double> PtEdges() {
  std::vector<double> edges;
  for (int bin = 0; bin <= 100; ++bin) edges.push_back(0.5 * bin);
  for (double edge : {60., 75., 100., 150., 250., 500., 1000., 2000.,
                      4000.}) {
    edges.push_back(edge);
  }
  edges.push_back(
      std::nextafter(7000.0, std::numeric_limits<double>::infinity()));
  return edges;
}

std::vector<double> InclusiveUniformEdges(int bins, double minimum,
                                          double inclusiveMaximum) {
  std::vector<double> edges(bins + 1);
  for (int bin = 0; bin <= bins; ++bin) {
    edges[bin] =
        minimum + (inclusiveMaximum - minimum) * bin / bins;
  }
  // Variable-bin TAxis lookup compares directly to the final edge. This
  // retains the documented inclusive physical endpoint without the rounding
  // overflow that ROOT's uniform-axis arithmetic produces at +eta/+deta.
  edges.back() = std::nextafter(
      inclusiveMaximum, std::numeric_limits<double>::infinity());
  return edges;
}

THnSparseD* MakeSingle(const char* name) {
  const std::vector<double> ptEdges = PtEdges();
  const std::vector<double> etaEdges =
      InclusiveUniformEdges(100, -4.0, 4.0);
  const int bins[4] = {100, 100, static_cast<int>(ptEdges.size()) - 1, 4096};
  const double minimum[4] = {-M_PI, -4.0, 0.0, -0.5};
  const double maximum[4] = {
      M_PI,
      std::nextafter(4.0, std::numeric_limits<double>::infinity()),
      7000.0,
      4095.5};
  auto* histogram = new THnSparseD(name, "(phi,eta,pt,Nch)", 4, bins,
                                   minimum, maximum);
  histogram->GetAxis(1)->Set(bins[1], etaEdges.data());
  histogram->GetAxis(2)->Set(bins[2], ptEdges.data());
  histogram->GetAxis(0)->SetTitle("#phi");
  histogram->GetAxis(1)->SetTitle("#eta");
  histogram->GetAxis(2)->SetTitle("p_{T} (GeV/c)");
  histogram->GetAxis(3)->SetTitle("N_{ch}^{hadronisation}");
  histogram->Sumw2();
  return histogram;
}

THnSparseD* MakeCorrelation(const char* name, bool withOrigin) {
  const std::vector<double> ptEdges = PtEdges();
  const std::vector<double> deltaEtaEdges =
      InclusiveUniformEdges(100, -8.0, 8.0);
  const std::vector<double> etaEdges =
      InclusiveUniformEdges(100, -4.0, 4.0);
  const int dimensions = withOrigin ? 8 : 7;
  int bins[8] = {100, 100, 100, 100,
                 static_cast<int>(ptEdges.size()) - 1,
                 static_cast<int>(ptEdges.size()) - 1, 4096, 6};
  double minimum[8] = {-M_PI / 2.0, -8.0, -4.0, -4.0,
                       0.0, 0.0, -0.5, 0.5};
  double maximum[8] = {
      3.0 * M_PI / 2.0,
      std::nextafter(8.0, std::numeric_limits<double>::infinity()),
      std::nextafter(4.0, std::numeric_limits<double>::infinity()),
      std::nextafter(4.0, std::numeric_limits<double>::infinity()),
      7000.0, 7000.0, 4095.5, 6.5};
  auto* histogram = new THnSparseD(
      name,
      withOrigin ? "(dphi,deta,trEta,asEta,trPt,asPt,Nch,associateOrigin)"
                 : "(dphi,deta,trEta,asEta,trPt,asPt,Nch)",
      dimensions, bins, minimum, maximum);
  histogram->GetAxis(1)->Set(bins[1], deltaEtaEdges.data());
  histogram->GetAxis(2)->Set(bins[2], etaEdges.data());
  histogram->GetAxis(3)->Set(bins[3], etaEdges.data());
  histogram->GetAxis(4)->Set(bins[4], ptEdges.data());
  histogram->GetAxis(5)->Set(bins[5], ptEdges.data());
  histogram->GetAxis(0)->SetTitle("#Delta#phi");
  histogram->GetAxis(1)->SetTitle("#Delta#eta");
  histogram->GetAxis(2)->SetTitle("#eta^{trig}");
  histogram->GetAxis(3)->SetTitle("#eta^{assoc}");
  histogram->GetAxis(4)->SetTitle("p_{T}^{trig} (GeV/c)");
  histogram->GetAxis(5)->SetTitle("p_{T}^{assoc} (GeV/c)");
  histogram->GetAxis(6)->SetTitle("N_{ch}^{hadronisation}");
  if (withOrigin) histogram->GetAxis(7)->SetTitle("associate origin category");
  histogram->Sumw2();
  return histogram;
}

bool EligibleBase(int pdg, int status, int isFinal, int central, double pt,
                  double eta, bool trigger) {
  return isFinal && central && Hadronization::FindGroundState(pdg) &&
         Hadronization::IsDirectPrimaryStatus(status) &&
         Hadronization::IsCentralKinematic(pt, eta, trigger);
}

int SectorCharge(const std::string& sector, int qc, int qb) {
  if (sector == "charm") return qc;
  if (sector == "beauty") return qb;
  throw std::runtime_error("unknown heavy sector: " + sector);
}

int SectorOrigin(const std::string& sector, int originC, int originB) {
  if (sector == "charm") return originC;
  if (sector == "beauty") return originB;
  throw std::runtime_error("unknown heavy sector: " + sector);
}

int SectorHardIndex(const std::string& sector, int hardC, int hardB) {
  if (sector == "charm") return hardC;
  if (sector == "beauty") return hardB;
  throw std::runtime_error("unknown heavy sector: " + sector);
}

}  // namespace

int ValidateStatusAnalysisRawInput(const char* inputPath) {
  try {
    const RawInputContract contract =
        ValidateRawInputs(ResolveInputs(inputPath ? inputPath : ""));
    std::cout << "ANALYSIS_RAW_INPUT_VALIDATION contract="
              << kRawInputValidationContract
              << " campaign=" << contract.campaign
              << " tune=" << contract.tune
              << " logical_id=" << contract.logicalId
              << " entries=" << contract.treeEntries << "\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "ANALYSIS_RAW_INPUT_VALIDATION_ERROR "
              << error.what() << "\n";
    return 1;
  }
}

int status_analysis_THnSparse_qq(
    const char* inputPath, const char* outputDirectory,
    const char* selectionMode = "central_primary_ground_v1",
    int eventFilterModulo = 0, int eventFilterRemainder = -1) {
  if (std::string(selectionMode) != "central_primary_ground_v1") {
    std::cerr << "ERROR: unsupported selection mode. Use the separate "
                 "status_analysis_THnSparse_qq_legacy.C for legacy results.\n";
    return 2;
  }
  if ((eventFilterModulo == 0 && eventFilterRemainder != -1) ||
      (eventFilterModulo != 0 &&
       (eventFilterModulo < 2 || eventFilterRemainder < 0 ||
        eventFilterRemainder >= eventFilterModulo))) {
    std::cerr << "ERROR: event filter must be (0,-1) for the complete "
                 "sample or (modulo>=2,0<=remainder<modulo).\n";
    return 2;
  }
  try {
    const std::vector<std::string> inputs = ResolveInputs(inputPath);
    const RawInputContract rawContract = ValidateRawInputs(inputs);
    const std::string analysisCommit =
        RequiredEnvironment("HADRONIZATION_ANALYSIS_COMMIT");
    const std::string analysisMacroSha256 =
        RequiredEnvironment("HADRONIZATION_ANALYSIS_MACRO_SHA256");
    const std::string analysisProfile =
        RequiredEnvironment("HADRONIZATION_ANALYSIS_PROFILE");
    const std::string upstreamRawSha256 =
        RequiredEnvironment("HADRONIZATION_RAW_INPUT_SHA256");
    if (!IsLowerHex(analysisCommit, 40) ||
        !IsLowerHex(analysisMacroSha256, 64) ||
        !IsLowerHex(upstreamRawSha256, 64) ||
        analysisProfile != selectionMode) {
      throw std::runtime_error("invalid analysis implementation provenance");
    }
    const char* expectedCampaign =
        gSystem->Getenv("HADRONIZATION_EXPECTED_CAMPAIGN");
    const char* expectedTune =
        gSystem->Getenv("HADRONIZATION_EXPECTED_TUNE");
    const char* expectedLogicalId =
        gSystem->Getenv("HADRONIZATION_EXPECTED_LOGICAL_ID");
    if ((expectedCampaign && *expectedCampaign &&
         rawContract.campaign != expectedCampaign) ||
        (expectedTune && *expectedTune && rawContract.tune != expectedTune) ||
        (expectedLogicalId && *expectedLogicalId &&
         rawContract.logicalId != std::stoi(expectedLogicalId))) {
      throw std::runtime_error("raw manifest identity differs from analysis job");
    }
    gSystem->mkdir(outputDirectory, true);
    std::unique_ptr<TH1D> sourceMultiplicity(SumMultiplicity(inputs));
    if (sourceMultiplicity->GetBinContent(
            sourceMultiplicity->GetNbinsX() + 1) != 0.0) {
      throw std::runtime_error("central multiplicity overflow is nonzero");
    }
    std::unique_ptr<TH1D> multiplicity(
        dynamic_cast<TH1D*>(sourceMultiplicity->Clone(
            "summed MULTIPLICITY")));
    if (!multiplicity) {
      throw std::runtime_error("cannot clone multiplicity histogram");
    }
    multiplicity->SetDirectory(nullptr);
    multiplicity->Reset();
    multiplicity->Sumw2();

    TChain chain("tree");
    for (const auto& input : inputs) {
      if (chain.Add(input.c_str()) == 0) {
        throw std::runtime_error("cannot add raw input " + input);
      }
    }
    const std::vector<const char*> requiredBranches = {
        "event_id", "event_weight", "multiplicity_hadronisation_v1",
        "primary_all_heavy_match_valid", "heavyIndex",
        "heavyPdg", "heavyStatus", "heavyIsFinal", "heavyCentral", "heavyQc",
        "heavyQb", "heavyOriginC", "heavyOriginB", "heavyMatchedHardC",
        "heavyMatchedHardB", "heavyPt", "heavyEta", "heavyPhi"};
    for (const char* branch : requiredBranches) {
      if (!chain.GetBranch(branch)) {
        throw std::runtime_error(std::string("missing raw branch ") + branch);
      }
    }

    std::map<std::pair<int, int>, std::size_t> pairLookup;
    std::vector<PairAccumulator> pairs;
    pairs.reserve(Hadronization::kPairDefinitions.size());
    for (const auto& definition : Hadronization::kPairDefinitions) {
      PairAccumulator accumulator;
      accumulator.definition = &definition;
      accumulator.associate = MakeSingle("hAsKinematics");
      accumulator.correlation = MakeCorrelation("hCorrelations", false);
      accumulator.correlationByOrigin =
          MakeCorrelation("hCorrelationsByOrigin", true);
      const auto identity =
          std::make_pair(definition.triggerPdg, definition.associatePdg);
      if (!pairLookup.emplace(identity, pairs.size()).second) {
        throw std::runtime_error(
            "duplicate trigger/associate pair in generated registry");
      }
      pairs.push_back(accumulator);
    }

    std::map<int, TriggerAccumulator> triggers;
    for (const auto& definition : Hadronization::kPairDefinitions) {
      if (triggers.count(definition.triggerPdg)) continue;
      TriggerAccumulator trigger;
      trigger.pdg = definition.triggerPdg;
      trigger.sector = std::string(definition.sector);
      trigger.histogram = MakeSingle("hTrKinematics");
      triggers.emplace(trigger.pdg, trigger);
    }

    ULong64_t eventId = 0;
    Double_t eventWeight = 0.0;
    Int_t eventMultiplicity = 0;
    Int_t primaryAllHeavyMatchValid = 0;
    std::vector<int>* heavyIndex = nullptr;
    std::vector<int>* heavyPdg = nullptr;
    std::vector<int>* heavyStatus = nullptr;
    std::vector<int>* heavyIsFinal = nullptr;
    std::vector<int>* heavyCentral = nullptr;
    std::vector<int>* heavyQc = nullptr;
    std::vector<int>* heavyQb = nullptr;
    std::vector<int>* heavyOriginC = nullptr;
    std::vector<int>* heavyOriginB = nullptr;
    std::vector<int>* heavyMatchedHardC = nullptr;
    std::vector<int>* heavyMatchedHardB = nullptr;
    std::vector<double>* heavyPt = nullptr;
    std::vector<double>* heavyEta = nullptr;
    std::vector<double>* heavyPhi = nullptr;
    chain.SetBranchAddress("event_id", &eventId);
    chain.SetBranchAddress("event_weight", &eventWeight);
    chain.SetBranchAddress("multiplicity_hadronisation_v1", &eventMultiplicity);
    chain.SetBranchAddress("primary_all_heavy_match_valid",
                           &primaryAllHeavyMatchValid);
    chain.SetBranchAddress("heavyIndex", &heavyIndex);
    chain.SetBranchAddress("heavyPdg", &heavyPdg);
    chain.SetBranchAddress("heavyStatus", &heavyStatus);
    chain.SetBranchAddress("heavyIsFinal", &heavyIsFinal);
    chain.SetBranchAddress("heavyCentral", &heavyCentral);
    chain.SetBranchAddress("heavyQc", &heavyQc);
    chain.SetBranchAddress("heavyQb", &heavyQb);
    chain.SetBranchAddress("heavyOriginC", &heavyOriginC);
    chain.SetBranchAddress("heavyOriginB", &heavyOriginB);
    chain.SetBranchAddress("heavyMatchedHardC", &heavyMatchedHardC);
    chain.SetBranchAddress("heavyMatchedHardB", &heavyMatchedHardB);
    chain.SetBranchAddress("heavyPt", &heavyPt);
    chain.SetBranchAddress("heavyEta", &heavyEta);
    chain.SetBranchAddress("heavyPhi", &heavyPhi);

    unsigned long long sameHardConstituentPairs = 0;
    unsigned long long invalidVectorEvents = 0;
    unsigned long long selectedEvents = 0;
    unsigned long long selectedClosureFailures = 0;
    unsigned long long selectedDirectPrimaryHeavy = 0;
    unsigned long long selectedCentralGroundStates = 0;
    unsigned long long selectedCentralHardTriggers = 0;
    double totalWeight = 0.0;
    for (Long64_t event = 0; event < chain.GetEntries(); ++event) {
      if (chain.GetEntry(event) <= 0) {
        throw std::runtime_error("cannot read chained raw event");
      }
      if (!std::isfinite(eventWeight)) {
        throw std::runtime_error(
            "non-finite event weight reached analysis event loop");
      }
      if (eventFilterModulo > 0 &&
          eventId % static_cast<ULong64_t>(eventFilterModulo) !=
              static_cast<ULong64_t>(eventFilterRemainder)) {
        continue;
      }
      if (!heavyIndex || !heavyPdg || !heavyStatus || !heavyIsFinal ||
          !heavyCentral || !heavyQc || !heavyQb || !heavyOriginC ||
          !heavyOriginB || !heavyMatchedHardC || !heavyMatchedHardB ||
          !heavyPt || !heavyEta || !heavyPhi) {
        ++invalidVectorEvents;
        continue;
      }
      const std::size_t size = heavyPdg->size();
      if (heavyIndex->size() != size || heavyStatus->size() != size ||
          heavyIsFinal->size() != size || heavyCentral->size() != size ||
          heavyQc->size() != size || heavyQb->size() != size ||
          heavyOriginC->size() != size || heavyOriginB->size() != size ||
          heavyMatchedHardC->size() != size ||
          heavyMatchedHardB->size() != size || heavyPt->size() != size ||
          heavyEta->size() != size || heavyPhi->size() != size) {
        ++invalidVectorEvents;
        continue;
      }
      ++selectedEvents;
      totalWeight += eventWeight;
      multiplicity->Fill(eventMultiplicity, eventWeight);
      if (primaryAllHeavyMatchValid != 1) {
        ++selectedClosureFailures;
      }
      for (std::size_t index = 0; index < size; ++index) {
        if (!(*heavyIsFinal)[index] ||
            !Hadronization::IsDirectPrimaryStatus((*heavyStatus)[index])) {
          continue;
        }
        ++selectedDirectPrimaryHeavy;
        if (EligibleBase((*heavyPdg)[index], (*heavyStatus)[index],
                         (*heavyIsFinal)[index], (*heavyCentral)[index],
                         (*heavyPt)[index], (*heavyEta)[index], false)) {
          ++selectedCentralGroundStates;
        }
      }
      for (std::size_t triggerIndex = 0; triggerIndex < size; ++triggerIndex) {
        const int triggerPdg = (*heavyPdg)[triggerIndex];
        auto triggerIterator = triggers.find(triggerPdg);
        if (triggerIterator == triggers.end()) continue;
        TriggerAccumulator& trigger = triggerIterator->second;
        const std::string& sector = trigger.sector;
        const int triggerOrigin =
            SectorOrigin(sector, (*heavyOriginC)[triggerIndex],
                         (*heavyOriginB)[triggerIndex]);
        if (!EligibleBase(triggerPdg, (*heavyStatus)[triggerIndex],
                          (*heavyIsFinal)[triggerIndex],
                          (*heavyCentral)[triggerIndex],
                          (*heavyPt)[triggerIndex], (*heavyEta)[triggerIndex],
                          true) ||
            triggerOrigin != static_cast<int>(Origin::kSelectedHard)) {
          continue;
        }
        const int triggerCharge =
            SectorCharge(sector, (*heavyQc)[triggerIndex],
                         (*heavyQb)[triggerIndex]);
        const int triggerHard =
            SectorHardIndex(sector, (*heavyMatchedHardC)[triggerIndex],
                            (*heavyMatchedHardB)[triggerIndex]);
        if (triggerCharge == 0 || triggerHard < 0) continue;
        ++selectedCentralHardTriggers;

        const double triggerValues[4] = {
            Hadronization::WrapAbsolutePhi((*heavyPhi)[triggerIndex]),
            (*heavyEta)[triggerIndex], (*heavyPt)[triggerIndex],
            static_cast<double>(eventMultiplicity)};
        trigger.histogram->Fill(triggerValues, eventWeight);
        trigger.weightedTriggers += eventWeight;
        ++trigger.triggers;

        for (std::size_t associateIndex = 0; associateIndex < size;
             ++associateIndex) {
          if ((*heavyIndex)[associateIndex] == (*heavyIndex)[triggerIndex]) {
            continue;
          }
          const int associatePdg = (*heavyPdg)[associateIndex];
          const auto pairIterator =
              pairLookup.find({triggerPdg, associatePdg});
          if (pairIterator == pairLookup.end()) continue;
          if (!EligibleBase(associatePdg, (*heavyStatus)[associateIndex],
                            (*heavyIsFinal)[associateIndex],
                            (*heavyCentral)[associateIndex],
                            (*heavyPt)[associateIndex],
                            (*heavyEta)[associateIndex], false)) {
            continue;
          }
          const int associateCharge =
              SectorCharge(sector, (*heavyQc)[associateIndex],
                           (*heavyQb)[associateIndex]);
          if (associateCharge == 0) continue;
          PairAccumulator& pair = pairs[pairIterator->second];
          const bool expectedOS = pair.definition->heavySign == "OS";
          if ((triggerCharge * associateCharge < 0) != expectedOS) {
            throw std::runtime_error("pair-registry heavy-sign mismatch");
          }
          const int associateHard =
              SectorHardIndex(sector, (*heavyMatchedHardC)[associateIndex],
                              (*heavyMatchedHardB)[associateIndex]);
          if (associateHard >= 0 && associateHard == triggerHard) {
            ++sameHardConstituentPairs;
            if (sameHardConstituentPairs <= 20) {
              std::cerr << "SAME_HARD_CONSTITUENT event=" << event
                        << " trigger_pdg=" << triggerPdg
                        << " associate_pdg=" << associatePdg
                        << " trigger_index=" << (*heavyIndex)[triggerIndex]
                        << " associate_index=" << (*heavyIndex)[associateIndex]
                        << " hard_index=" << triggerHard
                        << " trigger_status=" << (*heavyStatus)[triggerIndex]
                        << " associate_status=" << (*heavyStatus)[associateIndex]
                        << "\n";
            }
            continue;
          }
          const int associateOrigin =
              SectorOrigin(sector, (*heavyOriginC)[associateIndex],
                           (*heavyOriginB)[associateIndex]);
          const int originCategory =
              Hadronization::AssociateOriginCategory(
                  static_cast<Origin>(associateOrigin), associateHard,
                  triggerHard, associateCharge, triggerCharge);
          const double associateValues[4] = {
              Hadronization::WrapAbsolutePhi((*heavyPhi)[associateIndex]),
              (*heavyEta)[associateIndex], (*heavyPt)[associateIndex],
              static_cast<double>(eventMultiplicity)};
          const double correlationValues[7] = {
              Hadronization::WrapDeltaPhi((*heavyPhi)[triggerIndex],
                                          (*heavyPhi)[associateIndex]),
              (*heavyEta)[triggerIndex] - (*heavyEta)[associateIndex],
              (*heavyEta)[triggerIndex], (*heavyEta)[associateIndex],
              (*heavyPt)[triggerIndex], (*heavyPt)[associateIndex],
              static_cast<double>(eventMultiplicity)};
          double originValues[8];
          std::copy(correlationValues, correlationValues + 7, originValues);
          originValues[7] = originCategory;
          pair.associate->Fill(associateValues, eventWeight);
          pair.correlation->Fill(correlationValues, eventWeight);
          pair.correlationByOrigin->Fill(originValues, eventWeight);
          pair.weightedPairs += eventWeight;
          ++pair.pairs;
        }
      }
    }
    if (invalidVectorEvents != 0) {
      throw std::runtime_error("raw vector-size mismatches: " +
                               std::to_string(invalidVectorEvents));
    }
    if (sameHardConstituentPairs != 0) {
      throw std::runtime_error("distinct pairs matched the same hard constituent: " +
                               std::to_string(sameHardConstituentPairs));
    }
    if (selectedEvents == 0) {
      throw std::runtime_error("event filter selected zero events");
    }
    if (selectedClosureFailures != 0) {
      throw std::runtime_error(
          "selected events fail primary-all-heavy closure: " +
          std::to_string(selectedClosureFailures));
    }
    if (multiplicity->GetBinContent(0) != 0.0 ||
        multiplicity->GetBinContent(multiplicity->GetNbinsX() + 1) != 0.0) {
      throw std::runtime_error(
          "selected-event multiplicity has underflow or overflow");
    }
    if (eventFilterModulo == 0 &&
        !HistogramsExactlyCompatible(*multiplicity, *sourceMultiplicity)) {
      throw std::runtime_error(
          "tree-derived complete-sample multiplicity differs from "
          "hMULTIPLICITY");
    }

    for (auto& pair : pairs) {
      const std::string path =
          std::string(outputDirectory) + "/" +
          std::string(pair.definition->filename);
      TFile output(path.c_str(), "RECREATE");
      if (output.IsZombie()) {
        throw std::runtime_error("cannot create " + path);
      }
      multiplicity->Write("summed MULTIPLICITY");
      TriggerAccumulator& trigger = triggers.at(pair.definition->triggerPdg);
      trigger.histogram->Write("hTrKinematics");
      pair.associate->Write("hAsKinematics");
      pair.correlation->Write("hCorrelations");
      pair.correlationByOrigin->Write("hCorrelationsByOrigin");
      TObjString originCategorySchema(
          Hadronization::kAssociateOriginCategorySchema);
      originCategorySchema.Write("associate_origin_category_schema");
      TObjString originCategoryLabels(
          Hadronization::kAssociateOriginCategoryLabels);
      originCategoryLabels.Write("associate_origin_category_labels");
      TObjString schema(kAnalysisSchema);
      schema.Write("analysis_schema");
      TObjString implementation(kAnalysisImplementation);
      implementation.Write("analysis_implementation");
      TObjString version(kAnalysisVersion);
      version.Write("analysis_version");
      TObjString profile(analysisProfile.c_str());
      profile.Write("analysis_profile");
      TObjString pairCombinatorics(kPairCombinatoricsMode);
      pairCombinatorics.Write("pair_combinatorics_mode");
      TObjString eventFilter(eventFilterModulo == 0
                                 ? kAllEventsFilter
                                 : kModuloEventFilter);
      eventFilter.Write("event_filter_schema");
      TObjString macroSha(analysisMacroSha256.c_str());
      macroSha.Write("analysis_macro_sha256");
      TObjString analysisRepositoryCommit(analysisCommit.c_str());
      analysisRepositoryCommit.Write("analysis_repository_commit");
      TObjString selector(Hadronization::kSelectorVersion);
      selector.Write("selector_version");
      TObjString rawSchema(rawContract.rawSchema.c_str());
      rawSchema.Write("upstream_raw_schema");
      TObjString rawSha(upstreamRawSha256.c_str());
      rawSha.Write("upstream_raw_sha256");
      TObjString originAlgorithm(rawContract.originAlgorithm.c_str());
      originAlgorithm.Write("upstream_origin_algorithm");
      TObjString upstreamSelector(rawContract.selector.c_str());
      upstreamSelector.Write("upstream_selector_version");
      TObjString upstreamCampaign(rawContract.campaign.c_str());
      upstreamCampaign.Write("upstream_campaign");
      TObjString upstreamTune(rawContract.tune.c_str());
      upstreamTune.Write("upstream_tune");
      TObjString upstreamCommit(rawContract.repositoryCommit.c_str());
      upstreamCommit.Write("upstream_repository_commit");
      TObjString upstreamExecutable(rawContract.executableSha256.c_str());
      upstreamExecutable.Write("upstream_executable_sha256");
      TObjString stabilitySchema(
          rawContract.heavyStabilityAuditSchema.c_str());
      stabilitySchema.Write("upstream_heavy_stability_audit_schema");
      TObjString stabilitySha(
          rawContract.heavyStabilityAuditSha256.c_str());
      stabilitySha.Write("upstream_heavy_stability_audit_sha256");
      TObjString effectiveSettingsSchema(
          rawContract.effectiveSettingsSchema.c_str());
      effectiveSettingsSchema.Write("upstream_effective_settings_schema");
      TObjString effectiveSettingsSha(
          rawContract.effectiveSettingsSha256.c_str());
      effectiveSettingsSha.Write("upstream_effective_settings_sha256");
      TObjString speciesSha(
          std::string(Hadronization::kSpeciesRegistrySha256).c_str());
      speciesSha.Write("species_registry_sha256");
      TObjString tuneAllowlistSchema(
          rawContract.tuneDifferenceAllowlistSchema.c_str());
      tuneAllowlistSchema.Write(
          "upstream_tune_difference_allowlist_schema");
      TObjString tuneAllowlistSha(
          rawContract.tuneDifferenceAllowlistSha256.c_str());
      tuneAllowlistSha.Write(
          "upstream_tune_difference_allowlist_sha256");
      TObjString pairSha(
          std::string(Hadronization::kPairRegistrySha256).c_str());
      pairSha.Write("pair_registry_sha256");
      TObjString sector(std::string(pair.definition->sector).c_str());
      sector.Write("heavy_sector");
      TObjString sign(std::string(pair.definition->heavySign).c_str());
      sign.Write("heavy_sign");
      TParameter<int>("trigger_pdg", pair.definition->triggerPdg).Write();
      TParameter<int>("associate_pdg", pair.definition->associatePdg).Write();
      TParameter<int>("reference_meson_pdg",
                      pair.definition->referenceMesonPdg).Write();
      TParameter<double>("trigger_pt_min_exclusive", 1.0).Write();
      TParameter<double>("associate_pt_min_exclusive", 0.15).Write();
      TParameter<double>("eta_abs_max_inclusive", 4.0).Write();
      TParameter<double>("same_sign_pair_factor", 1.0).Write();
      TParameter<int>("event_filter_modulo", eventFilterModulo).Write();
      TParameter<int>("event_filter_remainder",
                      eventFilterRemainder).Write();
      TParameter<Long64_t>(
          "upstream_heavy_flavour_conservation_failures",
          static_cast<Long64_t>(
              rawContract.heavyFlavourConservationFailures)).Write();
      TParameter<Long64_t>(
          "upstream_origin_classification_failures",
          static_cast<Long64_t>(
              rawContract.originClassificationFailures)).Write();
      TParameter<Long64_t>("source_input_events",
                           chain.GetEntries()).Write();
      TParameter<Long64_t>(
          "input_events", static_cast<Long64_t>(selectedEvents)).Write();
      TParameter<int>("input_file_count",
                      static_cast<int>(inputs.size())).Write();
      TParameter<double>("input_sum_weights", totalWeight).Write();
      // Historical pair-file-v2 name retained for compatibility. This is an
      // invariant-failure count (raw primary_all_heavy_match_valid != 1), not
      // the category-sum closure table produced by AuditOriginResolution.
      TParameter<Long64_t>(
          "primary_all_heavy_closure_failures",
          static_cast<Long64_t>(selectedClosureFailures)).Write();
      TParameter<Long64_t>(
          "direct_primary_heavy_count",
          static_cast<Long64_t>(selectedDirectPrimaryHeavy)).Write();
      TParameter<Long64_t>(
          "central_ground_state_count",
          static_cast<Long64_t>(selectedCentralGroundStates)).Write();
      TParameter<Long64_t>(
          "central_hard_trigger_count",
          static_cast<Long64_t>(selectedCentralHardTriggers)).Write();
      TParameter<Long64_t>("trigger_count",
                           static_cast<Long64_t>(trigger.triggers)).Write();
      TParameter<double>("trigger_sum_weights",
                         trigger.weightedTriggers).Write();
      TParameter<Long64_t>("pair_count",
                           static_cast<Long64_t>(pair.pairs)).Write();
      TParameter<double>("pair_sum_weights", pair.weightedPairs).Write();
      output.Write();
      output.Close();
    }

    for (auto& pair : pairs) {
      delete pair.associate;
      delete pair.correlation;
      delete pair.correlationByOrigin;
    }
    for (auto& item : triggers) delete item.second.histogram;
    std::cout << "ONE_PASS_ANALYSIS_SUMMARY inputs=" << inputs.size()
              << " source_events=" << chain.GetEntries()
              << " selected_events=" << selectedEvents
              << " pairs_written=" << pairs.size()
              << " same_hard_constituent_pairs=" << sameHardConstituentPairs
              << " primary_all_heavy_closure_failures="
              << selectedClosureFailures
              << " central_ground_state_count="
              << selectedCentralGroundStates
              << " event_filter_modulo=" << eventFilterModulo
              << " event_filter_remainder=" << eventFilterRemainder
              << " selection=" << selectionMode << "\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "ONE_PASS_ANALYSIS_ERROR " << error.what() << "\n";
    return 1;
  }
}

int TestStatusAnalysisBoundaryBinning() {
  std::unique_ptr<THnSparseD> single(MakeSingle("test_single"));
  std::unique_ptr<THnSparseD> correlation(
      MakeCorrelation("test_correlation", false));
  std::unique_ptr<THnSparseD> byOrigin(
      MakeCorrelation("test_correlation_by_origin", true));
  const double singleUpper[4] = {0.0, 4.0, 7000.0, 1.0};
  const double singleLower[4] = {0.0, -4.0, 1.01, 1.0};
  single->Fill(singleUpper);
  single->Fill(singleLower);
  const double correlationUpper[7] = {
      0.0, 8.0, 4.0, -4.0, 7000.0, 7000.0, 1.0};
  const double correlationLower[7] = {
      0.0, -8.0, -4.0, 4.0, 1.01, 0.151, 1.0};
  correlation->Fill(correlationUpper);
  correlation->Fill(correlationLower);
  double originUpper[8];
  double originLower[8];
  std::copy(correlationUpper, correlationUpper + 7, originUpper);
  std::copy(correlationLower, correlationLower + 7, originLower);
  originUpper[7] = 6.0;
  originLower[7] = 1.0;
  byOrigin->Fill(originUpper);
  byOrigin->Fill(originLower);

  auto allStoredBinsAreInRange = [](THnSparseD* histogram) {
    std::vector<Int_t> coordinates(histogram->GetNdimensions());
    for (Long64_t bin = 0; bin < histogram->GetNbins(); ++bin) {
      histogram->GetBinContent(bin, coordinates.data());
      for (int axis = 0; axis < histogram->GetNdimensions(); ++axis) {
        if (coordinates[axis] <= 0 ||
            coordinates[axis] > histogram->GetAxis(axis)->GetNbins()) {
          std::cerr << "BOUNDARY_BINNING_OUT_OF_RANGE histogram="
                    << histogram->GetName() << " axis=" << axis
                    << " coordinate=" << coordinates[axis]
                    << " bins=" << histogram->GetAxis(axis)->GetNbins()
                    << " maximum="
                    << std::setprecision(17)
                    << histogram->GetAxis(axis)->GetXmax()
                    << "\n";
          return false;
        }
      }
    }
    return true;
  };
  const bool pass =
      single->GetEntries() == 2.0 && correlation->GetEntries() == 2.0 &&
      byOrigin->GetEntries() == 2.0 &&
      allStoredBinsAreInRange(single.get()) &&
      allStoredBinsAreInRange(correlation.get()) &&
      allStoredBinsAreInRange(byOrigin.get());
  std::cout << "ANALYSIS_BOUNDARY_BINNING_TEST_"
            << (pass ? "PASS" : "FAIL")
            << " eta_upper=4 deta_upper=8 pt_upper=7000"
            << " single_entries=" << single->GetEntries()
            << " correlation_entries=" << correlation->GetEntries()
            << " origin_entries=" << byOrigin->GetEntries() << "\n";
  return pass ? 0 : 1;
}

int TestStatusAnalysisRejectsInputList() {
  try {
    (void)ResolveInputs("independent_raw_jobs.txt");
  } catch (const std::runtime_error& error) {
    const std::string message = error.what();
    if (message.find("one manifest-selected raw job at a time") !=
        std::string::npos) {
      std::cout << "ANALYSIS_SINGLE_INPUT_TEST_PASS\n";
      return 0;
    }
    std::cerr << "ANALYSIS_SINGLE_INPUT_TEST_FAIL unexpected_message="
              << message << "\n";
    return 1;
  }
  std::cerr << "ANALYSIS_SINGLE_INPUT_TEST_FAIL list_was_accepted\n";
  return 1;
}
