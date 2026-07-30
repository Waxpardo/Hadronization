#ifndef HADRONIZATION_PAIR_INPUT_SELECTION_UTILS_H
#define HADRONIZATION_PAIR_INPUT_SELECTION_UTILS_H

#include "../AnalysisScripts/AssociateOriginCategoryContract.h"

#include <TFile.h>
#include <TObjString.h>
#include <TParameter.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>

#if __has_include(<nlohmann/json.hpp>)
#include <nlohmann/json.hpp>
#elif __has_include("nlohmann/json.hpp")
#include "nlohmann/json.hpp"
#else
#error "Could not find nlohmann/json.hpp. Source setupEnv.sh before compiling."
#endif

namespace HadronizationPairInput {

enum class ProjectionMode {
  kMetadataV2,
  kTaggedLegacyRecutsV1,
};

inline constexpr std::size_t kRequiredV2MetadataObjectCount = 12;

struct SelectionContract {
  std::string mode;
  std::string legacyMetadataFreeCompleteRootTag;
  std::string histogramPtEtaFieldSemantics;
  std::string analysisSchema;
  std::string analysisImplementation;
  std::string analysisVersion;
  std::string analysisProfile;
  std::string selectorVersion;
  std::string pairCombinatoricsMode;
  double triggerPtMinExclusive = 0.0;
  double associatePtMinExclusive = 0.0;
  double etaAbsMaxInclusive = 0.0;
  double sameSignPairFactor = 0.0;
  std::string ptUpperSelection;
};

inline bool AllowsV2(const SelectionContract& contract) {
  return contract.mode == "v2_metadata_or_tagged_legacy_recuts_v1" ||
         contract.mode == "v2_metadata_only_v1";
}

inline bool AllowsLegacy(const SelectionContract& contract) {
  return contract.mode == "v2_metadata_or_tagged_legacy_recuts_v1" ||
         contract.mode == "tagged_legacy_recuts_only_v1";
}

inline ProjectionMode LegacyProjectionMode(
    const SelectionContract& contract) {
  if (AllowsLegacy(contract)) {
    return ProjectionMode::kTaggedLegacyRecutsV1;
  }
  throw std::runtime_error(
      "selection contract does not permit metadata-free legacy input: " +
      contract.mode);
}

inline void RequireExactKeys(const nlohmann::json& object,
                             const std::set<std::string>& expected,
                             const std::string& context) {
  if (!object.is_object()) {
    throw std::runtime_error(context + " must be a JSON object");
  }
  std::set<std::string> actual;
  for (auto iterator = object.begin(); iterator != object.end(); ++iterator) {
    actual.insert(iterator.key());
  }
  if (actual == expected) return;

  std::ostringstream message;
  message << context << " has an unsupported or missing field set";
  for (const auto& key : expected) {
    if (!actual.count(key)) message << "\n  missing: " << key;
  }
  for (const auto& key : actual) {
    if (!expected.count(key)) message << "\n  unsupported: " << key;
  }
  throw std::runtime_error(message.str());
}

inline SelectionContract ParseSelectionContract(
    const nlohmann::json& object) {
  const std::set<std::string> expectedKeys = {
      "mode",
      "legacy_metadata_free_complete_root_tag",
      "histogram_pt_eta_fields",
      "v2_analysis_schema",
      "v2_analysis_implementation",
      "v2_analysis_version",
      "v2_analysis_profile",
      "v2_selector_version",
      "v2_pair_combinatorics_mode",
      "v2_trigger_pt_min_exclusive",
      "v2_associate_pt_min_exclusive",
      "v2_eta_abs_max_inclusive",
      "v2_same_sign_pair_factor",
      "v2_pt_upper_selection",
  };
  RequireExactKeys(object, expectedKeys, "pair_input_selection_contract");

  SelectionContract contract;
  contract.mode = object.at("mode").get<std::string>();
  contract.legacyMetadataFreeCompleteRootTag =
      object.at("legacy_metadata_free_complete_root_tag")
          .get<std::string>();
  contract.histogramPtEtaFieldSemantics =
      object.at("histogram_pt_eta_fields").get<std::string>();
  contract.analysisSchema =
      object.at("v2_analysis_schema").get<std::string>();
  contract.analysisImplementation =
      object.at("v2_analysis_implementation").get<std::string>();
  contract.analysisVersion =
      object.at("v2_analysis_version").get<std::string>();
  contract.analysisProfile =
      object.at("v2_analysis_profile").get<std::string>();
  contract.selectorVersion =
      object.at("v2_selector_version").get<std::string>();
  contract.pairCombinatoricsMode =
      object.at("v2_pair_combinatorics_mode").get<std::string>();
  contract.triggerPtMinExclusive =
      object.at("v2_trigger_pt_min_exclusive").get<double>();
  contract.associatePtMinExclusive =
      object.at("v2_associate_pt_min_exclusive").get<double>();
  contract.etaAbsMaxInclusive =
      object.at("v2_eta_abs_max_inclusive").get<double>();
  contract.sameSignPairFactor =
      object.at("v2_same_sign_pair_factor").get<double>();
  contract.ptUpperSelection =
      object.at("v2_pt_upper_selection").get<std::string>();

  if (!AllowsV2(contract) && !AllowsLegacy(contract)) {
    throw std::runtime_error(
        "Unsupported pair_input_selection_contract mode: " + contract.mode);
  }
  if (AllowsLegacy(contract) &&
      contract.legacyMetadataFreeCompleteRootTag.empty()) {
    throw std::runtime_error(
        "Legacy pair-selection mode requires an explicit metadata-free "
        "complete-root tag");
  }
  if (contract.histogramPtEtaFieldSemantics != "legacy_recuts_only_v1") {
    throw std::runtime_error(
        "histogram_pt_eta_fields must be 'legacy_recuts_only_v1'");
  }

  const bool supportedV2 =
      contract.analysisSchema == "paul_pair_objects_primary_ground_v2" &&
      contract.analysisImplementation ==
          "one_pass_primary_ground_pair_analysis_v2" &&
      contract.analysisVersion == "status_analysis_THnSparse_qq_v2" &&
      contract.analysisProfile == "central_primary_ground_v1" &&
      contract.selectorVersion ==
          "hard_trigger_primary_ground__primary_ground_associate_v1" &&
      contract.pairCombinatoricsMode == "ordered_conditional_v1" &&
      std::abs(contract.triggerPtMinExclusive - 1.0) <= 1e-12 &&
      std::abs(contract.associatePtMinExclusive - 0.15) <= 1e-12 &&
      std::abs(contract.etaAbsMaxInclusive - 4.0) <= 1e-12 &&
      std::abs(contract.sameSignPairFactor - 1.0) <= 1e-12 &&
      contract.ptUpperSelection == "none";
  if (!supportedV2) {
    throw std::runtime_error(
        "Unsupported central v2 pair-selection definition");
  }
  return contract;
}

inline std::string ReadString(TFile& file, const char* name,
                              const std::string& path) {
  auto* object = dynamic_cast<TObjString*>(file.Get(name));
  if (!object) {
    throw std::runtime_error(
        "Missing or wrong-type selection metadata '" + std::string(name) +
        "' in " + path);
  }
  return object->GetString().Data();
}

inline double ReadDouble(TFile& file, const char* name,
                         const std::string& path) {
  auto* object = dynamic_cast<TParameter<double>*>(file.Get(name));
  if (!object || !std::isfinite(object->GetVal())) {
    throw std::runtime_error(
        "Missing, wrong-type, or non-finite selection metadata '" +
        std::string(name) + "' in " + path);
  }
  return object->GetVal();
}

inline void RequireString(TFile& file, const char* name,
                          const std::string& expected,
                          const std::string& path) {
  const std::string actual = ReadString(file, name, path);
  if (actual != expected) {
    throw std::runtime_error(
        "Selection metadata mismatch for '" + std::string(name) + "' in " +
        path + ": expected '" + expected + "', got '" + actual + "'");
  }
}

inline void RequireDouble(TFile& file, const char* name, double expected,
                          const std::string& path) {
  const double actual = ReadDouble(file, name, path);
  const double scale = std::max({1.0, std::abs(expected), std::abs(actual)});
  if (std::abs(actual - expected) > 1e-12 * scale) {
    std::ostringstream message;
    message << "Selection metadata mismatch for '" << name << "' in "
            << path << ": expected " << expected << ", got " << actual;
    throw std::runtime_error(message.str());
  }
}

inline ProjectionMode DetermineProjectionMode(
    std::size_t presentV2Objects, const SelectionContract& contract,
    const std::string& activeCompleteRootTag, const std::string& path) {
  if (presentV2Objects == 0) {
    if (!AllowsLegacy(contract)) {
      throw std::runtime_error(
          "Metadata-free pair file is forbidden by selection contract mode '" +
          contract.mode + "': " + path);
    }
    if (activeCompleteRootTag !=
        contract.legacyMetadataFreeCompleteRootTag) {
      throw std::runtime_error(
          "Metadata-free pair file is allowed only for the explicitly tagged "
          "legacy input '" + contract.legacyMetadataFreeCompleteRootTag +
          "', but active complete-root tag is '" + activeCompleteRootTag +
          "': " + path);
    }
    return LegacyProjectionMode(contract);
  }
  if (presentV2Objects != kRequiredV2MetadataObjectCount) {
    throw std::runtime_error(
        "Partial v2 pair-selection metadata in " + path +
        ": refusing legacy fallback");
  }
  if (!AllowsV2(contract)) {
    throw std::runtime_error(
        "V2 pair metadata is forbidden by selection contract mode '" +
        contract.mode + "': " + path);
  }
  return ProjectionMode::kMetadataV2;
}

inline ProjectionMode ValidateSelectionMetadata(
    TFile& file, const SelectionContract& contract,
    const std::string& activeCompleteRootTag, const std::string& path) {
  const std::array<const char*, 12> required = {
      "analysis_schema",
      "analysis_implementation",
      "analysis_version",
      "analysis_profile",
      "associate_origin_category_schema",
      "associate_origin_category_labels",
      "selector_version",
      "pair_combinatorics_mode",
      "trigger_pt_min_exclusive",
      "associate_pt_min_exclusive",
      "eta_abs_max_inclusive",
      "same_sign_pair_factor",
  };
  std::size_t present = 0;
  for (const char* name : required) {
    if (file.GetListOfKeys() && file.GetListOfKeys()->FindObject(name)) {
      ++present;
    }
  }
  const ProjectionMode mode =
      DetermineProjectionMode(present, contract, activeCompleteRootTag, path);
  if (mode != ProjectionMode::kMetadataV2) return mode;

  RequireString(file, "analysis_schema", contract.analysisSchema, path);
  RequireString(file, "analysis_implementation",
                contract.analysisImplementation, path);
  RequireString(file, "analysis_version", contract.analysisVersion, path);
  RequireString(file, "analysis_profile", contract.analysisProfile, path);
  RequireString(
      file, "associate_origin_category_schema",
      Hadronization::kAssociateOriginCategorySchema, path);
  RequireString(
      file, "associate_origin_category_labels",
      Hadronization::kAssociateOriginCategoryLabels, path);
  RequireString(file, "selector_version", contract.selectorVersion, path);
  RequireString(file, "pair_combinatorics_mode",
                contract.pairCombinatoricsMode, path);
  RequireDouble(file, "trigger_pt_min_exclusive",
                contract.triggerPtMinExclusive, path);
  RequireDouble(file, "associate_pt_min_exclusive",
                contract.associatePtMinExclusive, path);
  RequireDouble(file, "eta_abs_max_inclusive",
                contract.etaAbsMaxInclusive, path);
  RequireDouble(file, "same_sign_pair_factor",
                contract.sameSignPairFactor, path);

  const std::array<const char*, 8> forbiddenUpperPt = {
      "trigger_pt_max",
      "trigger_pt_max_inclusive",
      "trigger_pt_max_exclusive",
      "associate_pt_max",
      "associate_pt_max_inclusive",
      "associate_pt_max_exclusive",
      "trigger_pt_upper_selection",
      "associate_pt_upper_selection",
  };
  for (const char* name : forbiddenUpperPt) {
    if (file.GetListOfKeys() && file.GetListOfKeys()->FindObject(name)) {
      throw std::runtime_error(
          "Unsupported upper-pT selection metadata '" + std::string(name) +
          "' in " + path);
    }
  }
  return mode;
}

inline const char* ProjectionModeName(ProjectionMode mode) {
  switch (mode) {
    case ProjectionMode::kMetadataV2:
      return "metadata_v2_upstream_selected";
    case ProjectionMode::kTaggedLegacyRecutsV1:
      return "tagged_legacy_recuts_v1";
  }
  return "unknown_projection_mode";
}

inline void ValidateConfiguredCombinatorics(
    ProjectionMode projectionMode, const std::string& configuredMode,
    double configuredSameSignFactor, const SelectionContract& contract,
    const std::string& path) {
  const bool factorIsOne =
      std::isfinite(configuredSameSignFactor) &&
      std::abs(configuredSameSignFactor - 1.0) <= 1e-12;
  const bool factorIsHalf =
      std::isfinite(configuredSameSignFactor) &&
      std::abs(configuredSameSignFactor - 0.5) <= 1e-12;
  if (projectionMode == ProjectionMode::kMetadataV2) {
    if (configuredMode != "ordered_conditional_v1" || !factorIsOne ||
        contract.pairCombinatoricsMode != "ordered_conditional_v1" ||
        std::abs(contract.sameSignPairFactor - 1.0) > 1e-12) {
      throw std::runtime_error(
          "Canonical metadata-v2 pair input requires "
          "pair_combinatorics_mode=ordered_conditional_v1 and "
          "same_sign_pair_factor=1.0: " +
          path);
    }
    return;
  }
  if (configuredMode != "legacy_identical_ss_half_v1" ||
      !factorIsHalf || !AllowsLegacy(contract)) {
    throw std::runtime_error(
        "Tagged metadata-free legacy input requires "
        "pair_combinatorics_mode=legacy_identical_ss_half_v1 and "
        "same_sign_pair_factor=0.5: " +
        path);
  }
}

}  // namespace HadronizationPairInput

#endif
