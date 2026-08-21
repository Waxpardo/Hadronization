#ifndef HADRONIZATION_COMMON_MULTIPLICITY_BOUNDARIES_H
#define HADRONIZATION_COMMON_MULTIPLICITY_BOUNDARIES_H

// The multiplicity axis: common absolute N_ch boundaries, one set shared by
// every tune. docs/PRODUCTION_SHAPE_DECISION.md rules that the activity classes
// are defined by absolute N_ch, with the percentile labels defined on the
// MONASH minimum-bias distribution and the per-tune residual published rather
// than hidden. The per-tune percentile derivation this replaces is readable at
// 33c9a8c30fa97c9281e26ecbd6d1becc1afb9c21; it folded each tune's activity
// distribution into the class definition.
//
// config/multiplicity_class_boundaries_v1.json is THE definition. It is read,
// never copied: a literal here would be a second definition, and two
// definitions drift. This header exists so the two consumers that resolve the
// artifact onto configured percentile labels share one implementation.

#include <cmath>
#include <cstddef>
#include <fstream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#if __has_include(<nlohmann/json.hpp>)
#include <nlohmann/json.hpp>
#elif __has_include("nlohmann/json.hpp")
#include "nlohmann/json.hpp"
#else
#error "Could not find nlohmann/json.hpp. Source the project/ROOT environment before compiling this macro."
#endif

#include "../generation/producer/Sha256.h"
#include "MultiplicityBoundaryUtils.h"

namespace HadronizationMultiplicity {

constexpr const char* kCommonBoundaryArtifactPath =
    "config/multiplicity_class_boundaries_v1.json";
constexpr const char* kCommonBoundaryArtifactSchema =
    "hadronization_multiplicity_class_boundaries_v1";

// Stated in the receipt so a reader cannot take a tune's "0-1%" for that tune's
// own top percentile. The boundaries are absolute and shared; only the LABELS
// are percentiles, and they are MONASH's.
constexpr const char* kCommonBoundaryLabelProvenance =
    "percentile labels are percentiles of the MONASH minimum-bias "
    "distribution, NOT of the labelled tune; the class boundaries are absolute "
    "N_ch and identical for every tune, and each tune's own realised fraction "
    "is published per class as achieved_weighted_fraction";

struct CommonBoundaries {
  std::string artifactPath;
  std::string artifactSha256;
  std::string definition;
  std::string derivedFrom;
  std::vector<std::string> classNames;
  std::vector<double> lowerEdgesNch;  // ascending half-integer lower edges
};

// Reads the committed artifact and fails closed on any disagreement with the
// configured class count. Truncating or padding would silently redefine the
// axis that every per-multiplicity number is conditioned on.
inline CommonBoundaries LoadCommonBoundaries(
    std::size_t configuredClassCount,
    const std::string& artifactPath = kCommonBoundaryArtifactPath) {
  CommonBoundaries loaded;
  loaded.artifactPath = artifactPath;
  std::ifstream stream(artifactPath);
  if (!stream.is_open()) {
    throw std::runtime_error(
        "Cannot open the multiplicity class-boundary artifact " + artifactPath);
  }
  nlohmann::json artifact;
  stream >> artifact;
  if (artifact.value("schema", std::string()) !=
      kCommonBoundaryArtifactSchema) {
    throw std::runtime_error(
        "Unexpected schema in multiplicity class-boundary artifact " +
        artifactPath);
  }
  loaded.artifactSha256 = Hadronization::Sha256FileHex(artifactPath);
  loaded.definition = artifact.value("definition", std::string());
  loaded.derivedFrom = artifact.value("derived_from", std::string());
  if (!artifact.contains("classes") || !artifact.at("classes").is_array() ||
      artifact.at("classes").empty()) {
    throw std::runtime_error(
        "Multiplicity class-boundary artifact defines no classes: " +
        artifactPath);
  }
  for (const auto& entry : artifact.at("classes")) {
    const double boundary = entry.at("boundary_nch").get<double>();
    // Half-integer boundaries are what make every integer N_ch unambiguous
    // about the class it falls in.
    if (!std::isfinite(boundary) ||
        std::abs(boundary - std::floor(boundary) - 0.5) > 1e-9) {
      throw std::runtime_error(
          "Multiplicity class boundary is not half-integer in " + artifactPath);
    }
    if (!loaded.lowerEdgesNch.empty() &&
        !(boundary > loaded.lowerEdgesNch.back())) {
      throw std::runtime_error(
          "Multiplicity class boundaries are not strictly ascending in " +
          artifactPath);
    }
    loaded.classNames.push_back(entry.at("class").get<std::string>());
    loaded.lowerEdgesNch.push_back(boundary);
  }
  if (loaded.lowerEdgesNch.size() != configuredClassCount) {
    throw std::runtime_error(
        "Configured multiplicity class count (" +
        std::to_string(configuredClassCount) + ") does not match the " +
        std::to_string(loaded.lowerEdgesNch.size()) +
        " classes defined in " + artifactPath +
        "; refusing to truncate or pad the axis");
  }
  return loaded;
}

// Resolves the ruled boundaries onto the configured percentile labels. The
// percentile keying the whole downstream is built on is preserved exactly;
// only the SOURCE of the N_ch values changes.
//
// orderedPartition runs from the lowest-activity class to the highest, the same
// direction as the ascending artifact boundaries, so class i of the partition
// is class i of the artifact. thresholds[p] is the inclusive upper N_ch of the
// class whose low-activity edge is p.
inline std::map<double, double> CommonThresholdsForConfiguredClasses(
    const CommonBoundaries& boundaries,
    const std::vector<std::pair<double, double>>& orderedPartition,
    const std::set<double>& requestedPercentiles,
    const HistogramIdentity& identity,
    const std::string& context) {
  if (orderedPartition.size() != boundaries.lowerEdgesNch.size()) {
    throw std::runtime_error(
        "Ordered multiplicity partition and class-boundary artifact disagree "
        "on the class count in " + context);
  }
  std::map<double, double> thresholds;
  thresholds[100.0] = boundaries.lowerEdgesNch.front() + 0.5;
  for (std::size_t index = 0; index + 1 < orderedPartition.size(); ++index) {
    thresholds[orderedPartition[index].first] =
        boundaries.lowerEdgesNch[index + 1] - 0.5;
  }
  // The ruled top class is open-ended, so its inclusive upper N_ch is the top
  // of the axis. That is a property of the BINNING - identical across tunes -
  // and not of this tune's distribution, which is what keeps the resolved
  // boundaries identical for every tune.
  thresholds[0.0] =
      static_cast<double>(IntegerBinCenter(identity, identity.nBins, context));

  std::set<double> resolved;
  for (const auto& entry : thresholds) resolved.insert(entry.first);
  if (resolved != requestedPercentiles) {
    throw std::runtime_error(
        "Configured multiplicity percentiles are not exactly the percentiles "
        "resolved from the common class boundaries in " + context);
  }
  return thresholds;
}

}  // namespace HadronizationMultiplicity

#endif
