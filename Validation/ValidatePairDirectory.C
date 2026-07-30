#include "../AnalysisScripts/GeneratedPairRegistry.h"
#include "../AnalysisScripts/AssociateOriginCategoryContract.h"
#include "../SimulationScripts/GeneratedHeavyFlavourRegistry.h"
#include "../SimulationScripts/GeneratedTuneSettingRegistry.h"
#include "../SimulationScripts/HeavyFlavourUtils.h"
#include "../SimulationScripts/Sha256.h"

#include <TFile.h>
#include <TH1.h>
#include <TH1D.h>
#include <THnSparse.h>
#include <TKey.h>
#include <TObjString.h>
#include <TParameter.h>
#include <TSystem.h>

#include <algorithm>
#include <cctype>
#include <cmath>
#include <cstring>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <string>
#include <vector>

namespace {

constexpr const char* kRequiredAnalysisSchema =
    "paul_pair_objects_primary_ground_v2";
constexpr const char* kRequiredAnalysisImplementation =
    "one_pass_primary_ground_pair_analysis_v2";
constexpr const char* kRequiredAnalysisVersion =
    "status_analysis_THnSparse_qq_v2";
constexpr const char* kRequiredAnalysisProfile =
    "central_primary_ground_v1";
constexpr const char* kRequiredPairCombinatoricsMode =
    "ordered_conditional_v1";
constexpr const char* kRequiredRawSchema = "hf_primary_ground_raw_v5";
constexpr const char* kRequiredOriginAlgorithm =
    "signed_heavy_constituent_complete_mothers_unique_v4";
constexpr const char* kRequiredEffectiveSettingsSchema =
    "effective_pythia_settings_exhaustive_v2";
constexpr const char* kAllEventsFilter = "all_events_v1";
constexpr const char* kModuloEventFilter =
    "unsigned_event_id_modulo_v1";

struct SparseTotals {
  double content = 0.0;
  double errorSquared = 0.0;
};

using SparseCoordinate = std::vector<Int_t>;
using SparseBinMap = std::map<SparseCoordinate, SparseTotals>;

bool NearlyEqual(double first, double second,
                 double relativeTolerance = 1e-10) {
  return std::abs(first - second) <=
         relativeTolerance * std::max({1.0, std::abs(first), std::abs(second)});
}

bool IsLowerHex(const std::string& value, std::size_t length) {
  return value.size() == length &&
         std::all_of(value.begin(), value.end(), [](unsigned char character) {
           return std::isdigit(character) ||
                  (character >= 'a' && character <= 'f');
         });
}

bool HasInclusiveUpperEdge(TAxis* axis, double endpoint) {
  return axis &&
         axis->GetXmax() ==
             std::nextafter(endpoint,
                            std::numeric_limits<double>::infinity()) &&
         axis->FindFixBin(endpoint) >= 1 &&
         axis->FindFixBin(endpoint) <= axis->GetNbins();
}

std::string ObjectString(TFile& file, const char* name) {
  auto* object = dynamic_cast<TObjString*>(file.Get(name));
  return object ? std::string(object->GetString().Data()) : std::string();
}

SparseTotals ValidateSparse(THnSparse* histogram, const std::string& path,
                            int& errors) {
  bool valid = true;
  SparseTotals totals;
  std::vector<Int_t> coordinates(histogram->GetNdimensions());
  for (Long64_t bin = 0; bin < histogram->GetNbins(); ++bin) {
    const double content = histogram->GetBinContent(bin, coordinates.data());
    const double errorSquared = histogram->GetBinError2(bin);
    if (!std::isfinite(content) || !std::isfinite(errorSquared) ||
        errorSquared < 0.0) {
      std::cerr << "PAIR_VALIDATION_ERROR non-finite sparse bin in " << path
                << "\n";
      ++errors;
      valid = false;
      break;
    }
    totals.content += content;
    totals.errorSquared += errorSquared;
    for (int axis = 0; axis < histogram->GetNdimensions(); ++axis) {
      if (coordinates[axis] <= 0 ||
          coordinates[axis] > histogram->GetAxis(axis)->GetNbins()) {
        std::cerr << "PAIR_VALIDATION_ERROR sparse under/overflow in " << path
                  << " axis=" << axis << "\n";
        ++errors;
        valid = false;
        break;
      }
    }
  }
  if (!valid) return {};
  return totals;
}

SparseBinMap SparseContents(THnSparse* histogram) {
  SparseBinMap contents;
  if (!histogram) return contents;
  std::vector<Int_t> coordinates(histogram->GetNdimensions());
  for (Long64_t bin = 0; bin < histogram->GetNbins(); ++bin) {
    const double content =
        histogram->GetBinContent(bin, coordinates.data());
    contents[coordinates] = {content, histogram->GetBinError2(bin)};
  }
  return contents;
}

std::string SparseBinSumw2Digest(const SparseBinMap& contents) {
  Hadronization::Sha256 digest;
  digest.Update("thnsparse-coordinate-content-sumw2-v1");
  auto updateUint64 = [&](std::uint64_t value) {
    char bytes[8];
    for (int byte = 7; byte >= 0; --byte) {
      bytes[7 - byte] =
          static_cast<char>((value >> (8 * byte)) & 0xffU);
    }
    digest.Update(bytes, sizeof(bytes));
  };
  auto updateUint32 = [&](std::uint32_t value) {
    char bytes[4];
    for (int byte = 3; byte >= 0; --byte) {
      bytes[3 - byte] =
          static_cast<char>((value >> (8 * byte)) & 0xffU);
    }
    digest.Update(bytes, sizeof(bytes));
  };
  static_assert(sizeof(Int_t) == sizeof(std::uint32_t));
  static_assert(sizeof(double) == sizeof(std::uint64_t));
  updateUint64(contents.size());
  for (const auto& [coordinate, totals] : contents) {
    updateUint64(coordinate.size());
    for (const Int_t value : coordinate) {
      std::uint32_t bits = 0;
      std::memcpy(&bits, &value, sizeof(bits));
      updateUint32(bits);
    }
    std::uint64_t contentBits = 0;
    std::uint64_t sumw2Bits = 0;
    std::memcpy(&contentBits, &totals.content, sizeof(contentBits));
    std::memcpy(&sumw2Bits, &totals.errorSquared, sizeof(sumw2Bits));
    updateUint64(contentBits);
    updateUint64(sumw2Bits);
  }
  return digest.FinalHex();
}

std::string HistogramBinSumw2Digest(TH1* histogram) {
  if (!histogram) return {};
  Hadronization::Sha256 digest;
  digest.Update("th1-axis-content-sumw2-entries-v1");
  auto updateUint64 = [&](std::uint64_t value) {
    char bytes[8];
    for (int byte = 7; byte >= 0; --byte) {
      bytes[7 - byte] =
          static_cast<char>((value >> (8 * byte)) & 0xffU);
    }
    digest.Update(bytes, sizeof(bytes));
  };
  auto updateDouble = [&](double value) {
    static_assert(sizeof(double) == sizeof(std::uint64_t));
    std::uint64_t bits = 0;
    std::memcpy(&bits, &value, sizeof(bits));
    updateUint64(bits);
  };
  updateUint64(static_cast<std::uint64_t>(histogram->GetNbinsX()));
  for (int bin = 1; bin <= histogram->GetNbinsX() + 1; ++bin) {
    updateDouble(histogram->GetXaxis()->GetBinLowEdge(bin));
  }
  updateDouble(histogram->GetEntries());
  for (int bin = 0; bin <= histogram->GetNbinsX() + 1; ++bin) {
    updateDouble(histogram->GetBinContent(bin));
    const double error = histogram->GetBinError(bin);
    updateDouble(
        histogram->GetSumw2N() > 0
            ? histogram->GetSumw2()->At(bin)
            : error * error);
  }
  return digest.FinalHex();
}

bool ValidateOriginClosure(THnSparse* correlation, THnSparse* byOrigin,
                           const std::string& path, int& errors) {
  using Coordinate = std::vector<Int_t>;
  std::map<Coordinate, SparseTotals> decomposed;
  std::vector<Int_t> originCoordinates(byOrigin->GetNdimensions());
  for (Long64_t bin = 0; bin < byOrigin->GetNbins(); ++bin) {
    const double content =
        byOrigin->GetBinContent(bin, originCoordinates.data());
    const double errorSquared = byOrigin->GetBinError2(bin);
    Coordinate key(originCoordinates.begin(), originCoordinates.begin() + 7);
    auto& total = decomposed[key];
    total.content += content;
    total.errorSquared += errorSquared;
  }

  bool valid = true;
  std::set<Coordinate> seen;
  std::vector<Int_t> coordinates(correlation->GetNdimensions());
  for (Long64_t bin = 0; bin < correlation->GetNbins(); ++bin) {
    const double content =
        correlation->GetBinContent(bin, coordinates.data());
    const double errorSquared = correlation->GetBinError2(bin);
    const Coordinate key(coordinates.begin(), coordinates.end());
    seen.insert(key);
    const auto found = decomposed.find(key);
    if (found == decomposed.end() ||
        !NearlyEqual(content, found->second.content) ||
        !NearlyEqual(errorSquared, found->second.errorSquared)) {
      std::cerr << "PAIR_VALIDATION_ERROR associate-origin closure mismatch in "
                << path << "\n";
      ++errors;
      valid = false;
      break;
    }
  }
  if (valid) {
    for (const auto& [key, total] : decomposed) {
      if (!seen.count(key) &&
          (!NearlyEqual(total.content, 0.0) ||
           !NearlyEqual(total.errorSquared, 0.0))) {
        std::cerr
            << "PAIR_VALIDATION_ERROR origin component without inclusive bin in "
            << path << "\n";
        ++errors;
        valid = false;
        break;
      }
    }
  }
  return valid;
}

}  // namespace

int ValidatePairDirectory(const char* directory, bool requireAll = true,
                          int expectedMergeInputFiles = -1,
                          const char* expectedMergeManifestSha256 = "") {
  int errors = 0;
  auto fail = [&](const std::string& message) {
    std::cerr << "PAIR_VALIDATION_ERROR " << message << "\n";
    ++errors;
  };
  std::set<std::string> expected;
  const bool merged = expectedMergeInputFiles > 0;
  if (merged &&
      !IsLowerHex(expectedMergeManifestSha256, 64)) {
    fail("invalid expected merged-directory contract");
  }
  for (const auto& pair : Hadronization::kPairDefinitions) {
    expected.insert(std::string(pair.filename));
  }

  std::set<std::string> found;
  void* handle = gSystem->OpenDirectory(directory);
  if (!handle) {
    fail(std::string("cannot open directory ") + directory);
    return errors;
  }
  while (const char* entry = gSystem->GetDirEntry(handle)) {
    const std::string name(entry);
    if (name.size() > 5 && name.substr(name.size() - 5) == ".root") {
      found.insert(name);
    }
  }
  gSystem->FreeDirectory(handle);
  if (requireAll && found != expected) {
    for (const auto& missing : expected) {
      if (!found.count(missing)) fail("missing expected file " + missing);
    }
    for (const auto& extra : found) {
      if (!expected.count(extra)) fail("unexpected ROOT file " + extra);
    }
  }

  std::map<int, std::pair<Long64_t, double>> triggerTotals;
  std::map<int, std::string> triggerHistogramDigests;
  int triggerHistogramIdentityComparisons = 0;
  std::string multiplicityHistogramDigest;
  int multiplicityHistogramIdentityComparisons = 0;
  std::string commonAnalysisCommit;
  std::string commonAnalysisMacroSha;
  std::string commonUpstreamCampaign;
  std::string commonUpstreamTune;
  std::string commonUpstreamRawSha;
  std::string commonUpstreamCommit;
  std::string commonUpstreamExecutable;
  std::string commonTuneAllowlistSha;
  std::string commonStabilityAuditSha;
  std::string commonEffectiveSettingsSha;
  std::string commonMergeManifestSha;
  Long64_t commonInputEvents = -1;
  double commonInputWeights = 0.0;
  int commonInputFiles = -1;
  Long64_t commonSourceInputEvents = -1;
  int commonEventFilterModulo = -1;
  int commonEventFilterRemainder = -2;
  std::string commonEventFilterSchema;
  for (const auto& pair : Hadronization::kPairDefinitions) {
    const std::string path =
        std::string(directory) + "/" + std::string(pair.filename);
    if (gSystem->AccessPathName(path.c_str())) {
      if (requireAll) continue;
      continue;
    }
    TFile file(path.c_str(), "READ");
    if (file.IsZombie()) {
      fail("zombie file " + path);
      continue;
    }
    const std::set<std::string> requiredObjects = {
        "summed MULTIPLICITY",
        "hTrKinematics",
        "hAsKinematics",
        "hCorrelations",
        "hCorrelationsByOrigin",
        "associate_origin_category_schema",
        "associate_origin_category_labels",
        "analysis_schema",
        "analysis_implementation",
        "analysis_version",
        "analysis_profile",
        "pair_combinatorics_mode",
        "event_filter_schema",
        "analysis_macro_sha256",
        "analysis_repository_commit",
        "selector_version",
        "upstream_raw_schema",
        "upstream_raw_sha256",
        "upstream_origin_algorithm",
        "upstream_selector_version",
        "upstream_campaign",
        "upstream_tune",
        "upstream_repository_commit",
        "upstream_executable_sha256",
        "upstream_heavy_stability_audit_schema",
        "upstream_heavy_stability_audit_sha256",
        "upstream_effective_settings_schema",
        "upstream_effective_settings_sha256",
        "species_registry_sha256",
        "upstream_tune_difference_allowlist_schema",
        "upstream_tune_difference_allowlist_sha256",
        "pair_registry_sha256",
        "heavy_sector",
        "heavy_sign",
        "trigger_pdg",
        "associate_pdg",
        "reference_meson_pdg",
        "trigger_pt_min_exclusive",
        "associate_pt_min_exclusive",
        "eta_abs_max_inclusive",
        "same_sign_pair_factor",
        "event_filter_modulo",
        "event_filter_remainder",
        "upstream_heavy_flavour_conservation_failures",
        "upstream_origin_classification_failures",
        "input_events",
        "source_input_events",
        "input_file_count",
        "input_sum_weights",
        "primary_all_heavy_closure_failures",
        "direct_primary_heavy_count",
        "central_ground_state_count",
        "central_hard_trigger_count",
        "trigger_count",
        "trigger_sum_weights",
        "pair_count",
        "pair_sum_weights"};
    std::set<std::string> expectedObjects = requiredObjects;
    if (merged) {
      expectedObjects.erase("upstream_raw_sha256");
      expectedObjects.erase("upstream_effective_settings_sha256");
      expectedObjects.insert("merge_input_file_count");
      expectedObjects.insert("merge_input_manifest_sha256");
    }
    std::set<std::string> objectNames;
    TIter nextKey(file.GetListOfKeys());
    while (auto* key = dynamic_cast<TKey*>(nextKey())) {
      objectNames.insert(key->GetName());
    }
    if (objectNames != expectedObjects) {
      for (const auto& missing : expectedObjects) {
        if (!objectNames.count(missing)) {
          fail("missing required object " + missing + " in " + path);
        }
      }
      for (const auto& extra : objectNames) {
        if (!expectedObjects.count(extra)) {
          fail("unexpected object " + extra + " in " + path);
        }
      }
      continue;
    }
    auto* multiplicity = dynamic_cast<TH1D*>(file.Get("summed MULTIPLICITY"));
    auto* trigger = dynamic_cast<THnSparseD*>(file.Get("hTrKinematics"));
    auto* associate = dynamic_cast<THnSparseD*>(file.Get("hAsKinematics"));
    auto* correlation = dynamic_cast<THnSparseD*>(file.Get("hCorrelations"));
    auto* byOrigin = dynamic_cast<THnSparseD*>(
        file.Get("hCorrelationsByOrigin"));
    if (!multiplicity || !trigger || !associate || !correlation || !byOrigin) {
      fail("missing required histogram object in " + path);
      continue;
    }
    if (trigger->GetNdimensions() != 4 ||
        associate->GetNdimensions() != 4 ||
        correlation->GetNdimensions() != 7 ||
        byOrigin->GetNdimensions() != 8) {
      fail("THnSparse dimensionality mismatch in " + path);
    }
    if (multiplicity->GetSumw2N() != multiplicity->GetNcells() ||
        !trigger->GetCalculateErrors() ||
        !associate->GetCalculateErrors() ||
        !correlation->GetCalculateErrors() ||
        !byOrigin->GetCalculateErrors()) {
      fail("stored Sumw2 contract mismatch in " + path);
    }
    if (!HasInclusiveUpperEdge(trigger->GetAxis(1), 4.0) ||
        !HasInclusiveUpperEdge(associate->GetAxis(1), 4.0) ||
        !HasInclusiveUpperEdge(trigger->GetAxis(2), 7000.0) ||
        !HasInclusiveUpperEdge(associate->GetAxis(2), 7000.0) ||
        !HasInclusiveUpperEdge(correlation->GetAxis(1), 8.0) ||
        !HasInclusiveUpperEdge(correlation->GetAxis(2), 4.0) ||
        !HasInclusiveUpperEdge(correlation->GetAxis(3), 4.0) ||
        !HasInclusiveUpperEdge(correlation->GetAxis(4), 7000.0) ||
        !HasInclusiveUpperEdge(correlation->GetAxis(5), 7000.0) ||
        !HasInclusiveUpperEdge(byOrigin->GetAxis(1), 8.0) ||
        !HasInclusiveUpperEdge(byOrigin->GetAxis(2), 4.0) ||
        !HasInclusiveUpperEdge(byOrigin->GetAxis(3), 4.0) ||
        !HasInclusiveUpperEdge(byOrigin->GetAxis(4), 7000.0) ||
        !HasInclusiveUpperEdge(byOrigin->GetAxis(5), 7000.0) ||
        byOrigin->GetAxis(7)->GetNbins() != 6 ||
        byOrigin->GetAxis(7)->GetXmin() != 0.5 ||
        byOrigin->GetAxis(7)->GetXmax() != 6.5) {
      fail("THnSparse axis contract mismatch in " + path);
    }
    const int multiplicityOverflowBin = multiplicity->GetNbinsX() + 1;
    if (multiplicity->GetBinContent(0) != 0.0 ||
        multiplicity->GetBinError(0) != 0.0 ||
        multiplicity->GetBinContent(multiplicityOverflowBin) != 0.0 ||
        multiplicity->GetBinError(multiplicityOverflowBin) != 0.0) {
      fail("multiplicity under/overflow in " + path);
    }
    const SparseTotals triggerTotalsHistogram =
        ValidateSparse(trigger, path + ":hTrKinematics", errors);
    const std::string triggerHistogramDigest =
        SparseBinSumw2Digest(SparseContents(trigger));
    const std::string currentMultiplicityHistogramDigest =
        HistogramBinSumw2Digest(multiplicity);
    const SparseTotals associateTotalsHistogram =
        ValidateSparse(associate, path + ":hAsKinematics", errors);
    const SparseTotals correlationTotalsHistogram =
        ValidateSparse(correlation, path + ":hCorrelations", errors);
    const SparseTotals originTotalsHistogram =
        ValidateSparse(byOrigin, path + ":hCorrelationsByOrigin", errors);
    ValidateOriginClosure(correlation, byOrigin, path, errors);

    const std::string schema = ObjectString(file, "analysis_schema");
    const std::string originCategorySchema =
        ObjectString(file, "associate_origin_category_schema");
    const std::string originCategoryLabels =
        ObjectString(file, "associate_origin_category_labels");
    const std::string implementation =
        ObjectString(file, "analysis_implementation");
    const std::string version = ObjectString(file, "analysis_version");
    const std::string profile = ObjectString(file, "analysis_profile");
    const std::string pairCombinatorics =
        ObjectString(file, "pair_combinatorics_mode");
    const std::string eventFilterSchema =
        ObjectString(file, "event_filter_schema");
    const std::string macroSha =
        ObjectString(file, "analysis_macro_sha256");
    const std::string analysisCommit =
        ObjectString(file, "analysis_repository_commit");
    const std::string selector = ObjectString(file, "selector_version");
    const std::string rawSchema = ObjectString(file, "upstream_raw_schema");
    const std::string rawSha = ObjectString(file, "upstream_raw_sha256");
    const std::string originAlgorithm =
        ObjectString(file, "upstream_origin_algorithm");
    const std::string upstreamSelector =
        ObjectString(file, "upstream_selector_version");
    const std::string upstreamCampaign =
        ObjectString(file, "upstream_campaign");
    const std::string upstreamTune = ObjectString(file, "upstream_tune");
    const std::string upstreamCommit =
        ObjectString(file, "upstream_repository_commit");
    const std::string upstreamExecutable =
        ObjectString(file, "upstream_executable_sha256");
    const std::string stabilityAuditSchema =
        ObjectString(file, "upstream_heavy_stability_audit_schema");
    const std::string stabilityAuditSha =
        ObjectString(file, "upstream_heavy_stability_audit_sha256");
    const std::string effectiveSettingsSchema =
        ObjectString(file, "upstream_effective_settings_schema");
    const std::string effectiveSettingsSha =
        ObjectString(file, "upstream_effective_settings_sha256");
    const std::string speciesSha =
        ObjectString(file, "species_registry_sha256");
    const std::string tuneAllowlistSchema =
        ObjectString(file, "upstream_tune_difference_allowlist_schema");
    const std::string tuneAllowlistSha =
        ObjectString(file, "upstream_tune_difference_allowlist_sha256");
    const std::string pairSha =
        ObjectString(file, "pair_registry_sha256");
    const std::string sector = ObjectString(file, "heavy_sector");
    const std::string sign = ObjectString(file, "heavy_sign");
    auto* triggerPdg =
        dynamic_cast<TParameter<int>*>(file.Get("trigger_pdg"));
    auto* associatePdg =
        dynamic_cast<TParameter<int>*>(file.Get("associate_pdg"));
    auto* referencePdg =
        dynamic_cast<TParameter<int>*>(file.Get("reference_meson_pdg"));
    auto* triggerPtMin =
        dynamic_cast<TParameter<double>*>(
            file.Get("trigger_pt_min_exclusive"));
    auto* associatePtMin =
        dynamic_cast<TParameter<double>*>(
            file.Get("associate_pt_min_exclusive"));
    auto* etaAbsMax =
        dynamic_cast<TParameter<double>*>(
            file.Get("eta_abs_max_inclusive"));
    auto* sameSignPairFactor =
        dynamic_cast<TParameter<double>*>(
            file.Get("same_sign_pair_factor"));
    auto* eventFilterModulo =
        dynamic_cast<TParameter<int>*>(file.Get("event_filter_modulo"));
    auto* eventFilterRemainder =
        dynamic_cast<TParameter<int>*>(file.Get("event_filter_remainder"));
    auto* conservationFailures =
        dynamic_cast<TParameter<Long64_t>*>(
            file.Get("upstream_heavy_flavour_conservation_failures"));
    auto* classificationFailures =
        dynamic_cast<TParameter<Long64_t>*>(
            file.Get("upstream_origin_classification_failures"));
    auto* triggerCount =
        dynamic_cast<TParameter<Long64_t>*>(file.Get("trigger_count"));
    auto* triggerWeights =
        dynamic_cast<TParameter<double>*>(file.Get("trigger_sum_weights"));
    auto* pairCount =
        dynamic_cast<TParameter<Long64_t>*>(file.Get("pair_count"));
    auto* pairWeights =
        dynamic_cast<TParameter<double>*>(file.Get("pair_sum_weights"));
    auto* inputEvents =
        dynamic_cast<TParameter<Long64_t>*>(file.Get("input_events"));
    auto* sourceInputEvents =
        dynamic_cast<TParameter<Long64_t>*>(
            file.Get("source_input_events"));
    auto* inputFiles =
        dynamic_cast<TParameter<int>*>(file.Get("input_file_count"));
    auto* inputWeights =
        dynamic_cast<TParameter<double>*>(file.Get("input_sum_weights"));
    auto* closureFailures =
        dynamic_cast<TParameter<Long64_t>*>(
            file.Get("primary_all_heavy_closure_failures"));
    auto* directPrimaryHeavy =
        dynamic_cast<TParameter<Long64_t>*>(
            file.Get("direct_primary_heavy_count"));
    auto* centralGroundStates =
        dynamic_cast<TParameter<Long64_t>*>(
            file.Get("central_ground_state_count"));
    auto* centralHardTriggers =
        dynamic_cast<TParameter<Long64_t>*>(
            file.Get("central_hard_trigger_count"));
    auto* mergeInputFiles =
        dynamic_cast<TParameter<Long64_t>*>(
            file.Get("merge_input_file_count"));
    const std::string mergeManifestSha =
        ObjectString(file, "merge_input_manifest_sha256");
    const char* expectedCommit =
        gSystem->Getenv("HADRONIZATION_ANALYSIS_COMMIT");
    const char* expectedMacroSha =
        gSystem->Getenv("HADRONIZATION_ANALYSIS_MACRO_SHA256");
    const char* expectedRawSha =
        gSystem->Getenv("HADRONIZATION_EXPECTED_RAW_SHA256");
    const char* expectedCampaign =
        gSystem->Getenv("HADRONIZATION_EXPECTED_CAMPAIGN");
    const char* expectedTune =
        gSystem->Getenv("HADRONIZATION_EXPECTED_TUNE");
    if (schema != kRequiredAnalysisSchema ||
        originCategorySchema !=
            Hadronization::kAssociateOriginCategorySchema ||
        originCategoryLabels !=
            Hadronization::kAssociateOriginCategoryLabels ||
        implementation != kRequiredAnalysisImplementation ||
        version != kRequiredAnalysisVersion ||
        profile != kRequiredAnalysisProfile ||
        pairCombinatorics != kRequiredPairCombinatoricsMode ||
        !eventFilterModulo || !eventFilterRemainder ||
        !((eventFilterSchema == kAllEventsFilter &&
           eventFilterModulo->GetVal() == 0 &&
           eventFilterRemainder->GetVal() == -1) ||
          (eventFilterSchema == kModuloEventFilter &&
           eventFilterModulo->GetVal() >= 2 &&
           eventFilterRemainder->GetVal() >= 0 &&
           eventFilterRemainder->GetVal() <
               eventFilterModulo->GetVal())) ||
        selector != Hadronization::kSelectorVersion ||
        rawSchema != kRequiredRawSchema ||
        originAlgorithm != kRequiredOriginAlgorithm ||
        upstreamSelector != Hadronization::kSelectorVersion ||
        speciesSha != Hadronization::kSpeciesRegistrySha256 ||
        tuneAllowlistSchema !=
            Hadronization::kTuneDifferenceAllowlistSchema ||
        tuneAllowlistSha !=
            Hadronization::kTuneDifferenceAllowlistSha256 ||
        pairSha != Hadronization::kPairRegistrySha256 ||
        sector != pair.sector || sign != pair.heavySign ||
        upstreamCampaign.empty() || upstreamTune.empty() ||
        !IsLowerHex(macroSha, 64) || !IsLowerHex(analysisCommit, 40) ||
        ((!merged && !IsLowerHex(rawSha, 64)) ||
         (merged &&
          (!mergeInputFiles ||
           mergeInputFiles->GetVal() != expectedMergeInputFiles ||
           mergeManifestSha != expectedMergeManifestSha256))) ||
        !IsLowerHex(upstreamCommit, 40) ||
        !IsLowerHex(upstreamExecutable, 64) ||
        stabilityAuditSchema !=
            Hadronization::kHeavyStabilityAuditSchema ||
        !IsLowerHex(stabilityAuditSha, 64) ||
        effectiveSettingsSchema != kRequiredEffectiveSettingsSchema ||
        (!merged && !IsLowerHex(effectiveSettingsSha, 64)) ||
        (expectedCommit && *expectedCommit &&
         analysisCommit != expectedCommit) ||
        (expectedMacroSha && *expectedMacroSha &&
         macroSha != expectedMacroSha) ||
        (expectedRawSha && *expectedRawSha && rawSha != expectedRawSha) ||
        (expectedCampaign && *expectedCampaign &&
         upstreamCampaign != expectedCampaign) ||
        (expectedTune && *expectedTune && upstreamTune != expectedTune) ||
        !triggerPdg || triggerPdg->GetVal() != pair.triggerPdg ||
        !associatePdg || associatePdg->GetVal() != pair.associatePdg ||
        !referencePdg ||
        referencePdg->GetVal() != pair.referenceMesonPdg ||
        !triggerPtMin || !NearlyEqual(triggerPtMin->GetVal(), 1.0) ||
        !associatePtMin ||
        !NearlyEqual(associatePtMin->GetVal(), 0.15) ||
        !etaAbsMax || !NearlyEqual(etaAbsMax->GetVal(), 4.0) ||
        !sameSignPairFactor ||
        sameSignPairFactor->GetVal() != 1.0 ||
        !conservationFailures || conservationFailures->GetVal() != 0 ||
        !classificationFailures || classificationFailures->GetVal() != 0 ||
        !inputEvents || inputEvents->GetVal() <= 0 ||
        !sourceInputEvents ||
        sourceInputEvents->GetVal() < inputEvents->GetVal() ||
        (eventFilterModulo &&
         eventFilterModulo->GetVal() == 0 &&
         sourceInputEvents->GetVal() != inputEvents->GetVal()) ||
        !inputFiles || inputFiles->GetVal() <= 0 ||
        (merged && inputFiles->GetVal() != expectedMergeInputFiles) ||
        !inputWeights || !std::isfinite(inputWeights->GetVal()) ||
        !closureFailures || closureFailures->GetVal() != 0 ||
        !directPrimaryHeavy || directPrimaryHeavy->GetVal() < 0 ||
        !centralGroundStates || centralGroundStates->GetVal() < 0 ||
        centralGroundStates->GetVal() > directPrimaryHeavy->GetVal() ||
        !centralHardTriggers || centralHardTriggers->GetVal() < 0 ||
        centralHardTriggers->GetVal() > centralGroundStates->GetVal() ||
        !triggerCount || !triggerWeights || !pairCount || !pairWeights ||
        !std::isfinite(triggerWeights->GetVal()) ||
        !std::isfinite(pairWeights->GetVal())) {
      fail("metadata contract mismatch in " + path);
      continue;
    }
    if (commonAnalysisCommit.empty()) {
      commonAnalysisCommit = analysisCommit;
      commonAnalysisMacroSha = macroSha;
      commonUpstreamCampaign = upstreamCampaign;
      commonUpstreamTune = upstreamTune;
      commonUpstreamRawSha = rawSha;
      commonUpstreamCommit = upstreamCommit;
      commonUpstreamExecutable = upstreamExecutable;
      commonTuneAllowlistSha = tuneAllowlistSha;
      commonStabilityAuditSha = stabilityAuditSha;
      commonEffectiveSettingsSha = effectiveSettingsSha;
      commonMergeManifestSha = mergeManifestSha;
      commonInputEvents = inputEvents->GetVal();
      commonInputFiles = inputFiles->GetVal();
      commonInputWeights = inputWeights->GetVal();
      commonSourceInputEvents = sourceInputEvents->GetVal();
      commonEventFilterModulo = eventFilterModulo->GetVal();
      commonEventFilterRemainder = eventFilterRemainder->GetVal();
      commonEventFilterSchema = eventFilterSchema;
    } else if (analysisCommit != commonAnalysisCommit ||
               macroSha != commonAnalysisMacroSha ||
               upstreamCampaign != commonUpstreamCampaign ||
               upstreamTune != commonUpstreamTune ||
               rawSha != commonUpstreamRawSha ||
               upstreamCommit != commonUpstreamCommit ||
               upstreamExecutable != commonUpstreamExecutable ||
               tuneAllowlistSha != commonTuneAllowlistSha ||
               stabilityAuditSha != commonStabilityAuditSha ||
               effectiveSettingsSha != commonEffectiveSettingsSha ||
               mergeManifestSha != commonMergeManifestSha ||
               inputEvents->GetVal() != commonInputEvents ||
               sourceInputEvents->GetVal() != commonSourceInputEvents ||
               eventFilterModulo->GetVal() != commonEventFilterModulo ||
               eventFilterRemainder->GetVal() != commonEventFilterRemainder ||
               eventFilterSchema != commonEventFilterSchema ||
               inputFiles->GetVal() != commonInputFiles ||
               !NearlyEqual(inputWeights->GetVal(), commonInputWeights)) {
      fail("mixed provenance across pair files in " + path);
      continue;
    }
    if (!NearlyEqual(triggerTotalsHistogram.content,
                     triggerWeights->GetVal()) ||
        !NearlyEqual(associateTotalsHistogram.content,
                     pairWeights->GetVal()) ||
        !NearlyEqual(correlationTotalsHistogram.content,
                     pairWeights->GetVal()) ||
        !NearlyEqual(originTotalsHistogram.content, pairWeights->GetVal())) {
      fail("histogram integral/metadata mismatch in " + path);
    }
    if (!NearlyEqual(
            multiplicity->Integral(1, multiplicity->GetNbinsX()),
            inputWeights->GetVal()) ||
        static_cast<Long64_t>(multiplicity->GetEntries()) !=
            inputEvents->GetVal() ||
        static_cast<Long64_t>(trigger->GetEntries()) !=
            triggerCount->GetVal() ||
        static_cast<Long64_t>(associate->GetEntries()) !=
            pairCount->GetVal() ||
        static_cast<Long64_t>(correlation->GetEntries()) !=
            pairCount->GetVal() ||
        static_cast<Long64_t>(byOrigin->GetEntries()) !=
            pairCount->GetVal()) {
      fail("event/fill-count metadata mismatch in " + path);
    }
    const auto total =
        std::make_pair(triggerCount->GetVal(), triggerWeights->GetVal());
    if (multiplicityHistogramDigest.empty()) {
      multiplicityHistogramDigest = currentMultiplicityHistogramDigest;
    } else {
      ++multiplicityHistogramIdentityComparisons;
      if (multiplicityHistogramDigest !=
          currentMultiplicityHistogramDigest) {
        fail("selected-event multiplicity histogram bins/Sumw2 differ "
             "across pair files in " +
             path);
      }
    }
    const auto previous = triggerTotals.find(pair.triggerPdg);
    if (previous == triggerTotals.end()) {
      triggerTotals[pair.triggerPdg] = total;
      triggerHistogramDigests[pair.triggerPdg] =
          triggerHistogramDigest;
    } else if (previous->second != total) {
      fail("shared trigger denominator differs across pair files for PDG " +
           std::to_string(pair.triggerPdg));
    } else {
      ++triggerHistogramIdentityComparisons;
      if (triggerHistogramDigests.at(pair.triggerPdg) !=
          triggerHistogramDigest) {
        fail("shared trigger histogram bins/Sumw2 differ across pair files "
             "for PDG " +
             std::to_string(pair.triggerPdg));
      }
    }
  }
  std::cout << "PAIR_DIRECTORY_VALIDATION errors=" << errors
            << " expected_files=" << expected.size()
            << " found_root_files=" << found.size()
            << " analysis_commit=" << commonAnalysisCommit
            << " analysis_macro_sha256=" << commonAnalysisMacroSha
            << " raw_campaign=" << commonUpstreamCampaign
            << " raw_tune=" << commonUpstreamTune
            << " upstream_raw_sha256=" << commonUpstreamRawSha
            << " upstream_commit=" << commonUpstreamCommit
            << " upstream_executable_sha256="
            << commonUpstreamExecutable
            << " upstream_tune_allowlist_sha256="
            << commonTuneAllowlistSha
            << " upstream_stability_sha256="
            << commonStabilityAuditSha
            << " upstream_settings_sha256="
            << commonEffectiveSettingsSha
            << " merge_input_files="
            << (merged ? expectedMergeInputFiles : 0)
            << " merge_manifest_sha256=" << commonMergeManifestSha
            << " pair_combinatorics_mode="
            << kRequiredPairCombinatoricsMode
            << " event_filter_schema=" << commonEventFilterSchema
            << " event_filter_modulo=" << commonEventFilterModulo
            << " event_filter_remainder=" << commonEventFilterRemainder
            << " source_input_events=" << commonSourceInputEvents
            << " selected_input_events=" << commonInputEvents
            << " trigger_histogram_digest_groups="
            << triggerHistogramDigests.size()
            << " trigger_histogram_identity_comparisons="
            << triggerHistogramIdentityComparisons
            << " multiplicity_histogram_digest_groups="
            << (multiplicityHistogramDigest.empty() ? 0 : 1)
            << " multiplicity_histogram_identity_comparisons="
            << multiplicityHistogramIdentityComparisons
            << " same_sign_pair_factor=1\n";
  return errors;
}

int TestPairHistogramIdentity() {
  const Int_t dimensions = 2;
  const Int_t bins[dimensions] = {4, 4};
  const Double_t minimum[dimensions] = {0.0, 0.0};
  const Double_t maximum[dimensions] = {4.0, 4.0};
  THnSparseD reference("reference_trigger", "", dimensions, bins, minimum,
                       maximum);
  THnSparseD identical("identical_trigger", "", dimensions, bins, minimum,
                       maximum);
  THnSparseD redistributed("redistributed_trigger", "", dimensions, bins,
                           minimum, maximum);
  reference.Sumw2();
  identical.Sumw2();
  redistributed.Sumw2();

  Double_t firstBin[dimensions] = {0.5, 0.5};
  Double_t secondBin[dimensions] = {1.5, 1.5};
  Double_t thirdBin[dimensions] = {2.5, 0.5};
  Double_t fourthBin[dimensions] = {3.5, 1.5};
  reference.Fill(firstBin, 1.0);
  reference.Fill(secondBin, 2.0);
  identical.Fill(firstBin, 1.0);
  identical.Fill(secondBin, 2.0);
  redistributed.Fill(thirdBin, 1.0);
  redistributed.Fill(fourthBin, 2.0);

  int errors = 0;
  if (SparseBinSumw2Digest(SparseContents(&reference)) !=
      SparseBinSumw2Digest(SparseContents(&identical))) {
    std::cerr << "PAIR_TRIGGER_HISTOGRAM_IDENTITY_TEST identical histograms "
                 "were rejected\n";
    ++errors;
  }
  if (SparseBinSumw2Digest(SparseContents(&reference)) ==
      SparseBinSumw2Digest(SparseContents(&redistributed))) {
    std::cerr << "PAIR_HISTOGRAM_IDENTITY_TEST equal count/weight but "
                 "different bins were accepted\n";
    ++errors;
  }

  TH1D multiplicityReference("multiplicity_reference", "", 4, 0.0, 4.0);
  TH1D multiplicityIdentical("multiplicity_identical", "", 4, 0.0, 4.0);
  TH1D multiplicityRedistributed("multiplicity_redistributed", "", 4, 0.0,
                                 4.0);
  multiplicityReference.Sumw2();
  multiplicityIdentical.Sumw2();
  multiplicityRedistributed.Sumw2();
  multiplicityReference.Fill(0.5, 1.0);
  multiplicityReference.Fill(1.5, 2.0);
  multiplicityIdentical.Fill(0.5, 1.0);
  multiplicityIdentical.Fill(1.5, 2.0);
  multiplicityRedistributed.Fill(2.5, 1.0);
  multiplicityRedistributed.Fill(3.5, 2.0);
  if (HistogramBinSumw2Digest(&multiplicityReference) !=
      HistogramBinSumw2Digest(&multiplicityIdentical)) {
    std::cerr << "PAIR_HISTOGRAM_IDENTITY_TEST identical multiplicity "
                 "histograms were rejected\n";
    ++errors;
  }
  if (HistogramBinSumw2Digest(&multiplicityReference) ==
      HistogramBinSumw2Digest(&multiplicityRedistributed)) {
    std::cerr << "PAIR_HISTOGRAM_IDENTITY_TEST equal integral/entries but "
                 "redistributed multiplicity bins were accepted\n";
    ++errors;
  }
  std::cout
      << "PAIR_HISTOGRAM_IDENTITY_TEST errors=" << errors
      << " trigger_equal_count_weight_redistribution_rejected="
      << (errors == 0 ? "true" : "false")
      << " multiplicity_equal_integral_entries_redistribution_rejected="
      << (errors == 0 ? "true" : "false") << "\n";
  return errors;
}

int TestPairTriggerHistogramIdentity() {
  return TestPairHistogramIdentity();
}
