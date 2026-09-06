#ifndef HADRONIZATION_PLOT_PROJECTION_HPP
#define HADRONIZATION_PLOT_PROJECTION_HPP

#include "../reduce/statistics.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace Hadronization::Plot {

inline constexpr const char* kProjectionSchema =
    "hadronization_numerical_projection_v1";
inline constexpr double kPi = 3.141592653589793238462643383279502884;
inline constexpr double kDeltaPhiLow = -kPi / 2.0;
inline constexpr double kDeltaPhiHigh = 3.0 * kPi / 2.0;

inline double Wrap(double value, double low, double high) {
  const double period = high - low;
  if (!std::isfinite(value) || !(period > 0.0)) {
    throw std::invalid_argument("wrap domain is not finite and positive");
  }
  value = std::fmod(value - low, period);
  if (value < 0.0) value += period;
  value += low;
  if (value >= high) value = low;
  return value;
}

inline double DeltaPhi(double triggerPhi, double associatePhi) {
  return Wrap(triggerPhi - associatePhi, kDeltaPhiLow, kDeltaPhiHigh);
}

inline double AssociatePhi(double triggerPhi, double deltaPhi) {
  return Wrap(triggerPhi - deltaPhi, -kPi, kPi);
}

struct CellKey {
  std::uint32_t projection = 0;
  std::uint32_t scope = 0;
  std::uint32_t block = 0;
  std::uint32_t bin = 0;
  std::uint32_t component = 0;
  auto Tie() const {
    return std::tie(projection, scope, block, bin, component);
  }
  bool operator<(const CellKey& other) const { return Tie() < other.Tie(); }
};

struct CellValue {
  double value = 0.0;
  double absoluteSum = 0.0;
  double rowSumW2 = 0.0;
  std::uint64_t fills = 0;
};

struct Scope {
  int id = -1;
  std::string family;
  std::string tune;
  std::string profile;
  std::string activity;
  int classId = -1;
};

struct Pair {
  int id = -1;
  int triggerPdg = 0;
  int associatePdg = 0;
  int sign = 0;
  int referencePdg = 0;
  bool centralEligible = false;
  std::string sector;
};

struct Boundary {
  int tuneId = -1;
  int activityId = -1;
  int classId = -1;
  int low = -1;
  int high = -1;
  bool stable = true;
  bool resolved = true;
  bool empty = false;
};

struct ClassDefinition {
  int id = -1;
  bool integrated = false;
  int percentileLow = -1;
  int percentileHigh = -1;
};

struct Axis {
  int bins = 0;
  double low = 0.0;
  double high = 0.0;
  std::vector<double> edges;
};

struct Domains {
  std::vector<int> blockIds;
  std::vector<std::string> tunes;
  std::vector<std::string> profiles;
  std::vector<std::string> activities;
  std::vector<Scope> scopes;
  std::vector<Pair> pairs;
  std::vector<int> triggers;
  std::vector<std::pair<int, int>> correlations;
  std::vector<int> g9Species;
  std::vector<int> closureSpecies;
  std::vector<int> t1Species;
  std::vector<std::string> origins;
  std::vector<std::string> closureCategories;
  std::vector<ClassDefinition> classes;
  std::vector<Boundary> boundaries;
  Axis dphi;
  Axis eta;
  Axis phi;
  Axis pt;
  int activityBins = 0;
  std::uint64_t events = 0;
};

struct ProjectionResult {
  Reduction::JackknifeResult estimate;
  std::string diagnostic;
  std::vector<std::vector<double>> referenceComplements;
  std::vector<double> referenceLeaveMean;
};

struct Row {
  std::string family;
  std::string semanticId;
  std::string roleId;
  std::string quantity;
  std::string tune;
  std::string referenceTune;
  std::string profile;
  std::string activity;
  int classId = -1;
  int percentileLow = -1;
  int percentileHigh = -1;
  int nchLow = -1;
  int nchHigh = -1;
  int triggerPdg = 0;
  int associatePdg = 0;
  int referencePdg = 0;
  std::string component;
  std::string axis;
  int binIndex = -1;
  double binLow = std::numeric_limits<double>::quiet_NaN();
  double binHigh = std::numeric_limits<double>::quiet_NaN();
};

struct Role {
  std::string id;
  std::string family;
  std::string selector;
};

class Source {
 public:
  explicit Source(Domains domains) : domains_(std::move(domains)) {
    if (domains_.blockIds.size() != 10) {
      throw std::invalid_argument("projection requires the exact K=10 block domain");
    }
    for (std::size_t index = 0; index < domains_.blockIds.size(); ++index) {
      if (domains_.blockIds[index] != static_cast<int>(index + 1)) {
        throw std::invalid_argument("projection block IDs are not canonical");
      }
    }
  }

  const Domains& Domain() const { return domains_; }

  void AddCell(const CellKey& key, const CellValue& value) {
    if (!std::isfinite(value.value) || !std::isfinite(value.absoluteSum) ||
        !std::isfinite(value.rowSumW2) || value.absoluteSum < std::abs(value.value) ||
        value.rowSumW2 < 0.0 || !cells_.emplace(key, value).second) {
      throw std::runtime_error("compact cell is duplicate or numerically invalid");
    }
  }

  std::vector<double> Blocks(std::uint32_t projection, std::uint32_t scope,
                             std::uint32_t bin, std::uint32_t component) const {
    std::vector<double> values;
    values.reserve(domains_.blockIds.size());
    for (const int block : domains_.blockIds) {
      const auto found = cells_.find({projection, scope,
                                      static_cast<std::uint32_t>(block), bin,
                                      component});
      values.push_back(found == cells_.end() ? 0.0 : found->second.value);
    }
    return values;
  }

  std::vector<std::vector<double>> BlockVectors(
      const std::vector<std::tuple<std::uint32_t, std::uint32_t,
                                   std::uint32_t, std::uint32_t>>& coordinates) const {
    std::vector<std::vector<double>> result(domains_.blockIds.size());
    for (const auto& coordinate : coordinates) {
      const auto values = Blocks(std::get<0>(coordinate), std::get<1>(coordinate),
                                 std::get<2>(coordinate), std::get<3>(coordinate));
      for (std::size_t block = 0; block < values.size(); ++block) {
        result[block].push_back(values[block]);
      }
    }
    return result;
  }

 private:
  Domains domains_;
  std::map<CellKey, CellValue> cells_;
};

inline Reduction::DenominatorSeries ExactDenominator(
    const std::string& id, const std::vector<double>& blocks,
    bool survives = true) {
  return {id, blocks, {}, survives, true};
}

inline std::vector<std::string> BoundaryReasons(const Domains& domains,
                                                const Scope& scope) {
  if (scope.classId <= 0) return {};
  const auto tune = std::find(domains.tunes.begin(), domains.tunes.end(), scope.tune);
  const auto activity = std::find(domains.activities.begin(), domains.activities.end(),
                                  scope.activity);
  if (tune == domains.tunes.end() || activity == domains.activities.end()) {
    throw std::runtime_error("scope tune/activity is outside compact dictionaries");
  }
  const int tuneId = static_cast<int>(tune - domains.tunes.begin());
  const int activityId = static_cast<int>(activity - domains.activities.begin());
  const auto boundary = std::find_if(
      domains.boundaries.begin(), domains.boundaries.end(), [&](const auto& value) {
        return value.tuneId == tuneId && value.activityId == activityId &&
               value.classId == scope.classId;
      });
  if (boundary == domains.boundaries.end()) {
    throw std::runtime_error("class boundary receipt is missing");
  }
  std::vector<std::string> reasons;
  if (!boundary->stable) reasons.push_back("CLASS_BOUNDARY_UNSTABLE");
  if (!boundary->resolved) reasons.push_back("CLASS_BOUNDARY_UNRESOLVED");
  return reasons;
}

inline ProjectionResult Estimate(
    const std::vector<std::vector<double>>& blockVectors,
    const Reduction::EstimatorFunction& function,
    const std::vector<Reduction::DenominatorSeries>& denominators = {},
    const std::vector<std::string>& reasons = {}) {
  ProjectionResult result;
  result.estimate = Reduction::PooledDeleteOne(blockVectors, function, denominators,
                                                {}, reasons);
  if (std::find(reasons.begin(), reasons.end(), "CLASS_BOUNDARY_UNSTABLE") !=
          reasons.end() ||
      std::find(reasons.begin(), reasons.end(), "CLASS_BOUNDARY_UNRESOLVED") !=
          reasons.end()) {
    result.diagnostic = "fixed_pooled_boundary_delete_one";
  }
  return result;
}

inline ProjectionResult EstimateAfterExactCancellation(
    const std::vector<std::vector<double>>& blockVectors,
    const Reduction::EstimatorFunction& function,
    const std::vector<Reduction::DenominatorSeries>& survivingDenominators,
    const std::vector<std::string>& cancelledParents,
    const std::vector<std::string>& reasons = {}) {
  ProjectionResult result = Estimate(blockVectors, function,
                                     survivingDenominators, reasons);
  result.estimate.cancelledParentDiagnostics = cancelledParents;
  if (!cancelledParents.empty()) {
    if (!result.diagnostic.empty()) result.diagnostic += ";";
    result.diagnostic += "exact_algebraic_cancellation:";
    for (std::size_t index = 0; index < cancelledParents.size(); ++index) {
      if (index != 0) result.diagnostic += ",";
      result.diagnostic += cancelledParents[index];
    }
  }
  return result;
}

inline ProjectionResult IndependentRatio(const ProjectionResult& numerator,
                                         const ProjectionResult& denominator) {
  ProjectionResult output;
  auto& result = output.estimate;
  result.policy = Reduction::kEstimatorPolicy;
  result.blocks = numerator.estimate.blocks;
  result.dof = numerator.estimate.dof;
  for (const auto& reason : numerator.estimate.reasons) {
    Reduction::AddReason(result, reason);
  }
  for (const auto& reason : denominator.estimate.reasons) {
    Reduction::AddReason(result, reason);
  }
  if (numerator.estimate.center.size() != denominator.estimate.center.size() ||
      numerator.estimate.center.empty()) {
    result.valueStatus = numerator.estimate.center.empty()
                             ? numerator.estimate.valueStatus
                             : denominator.estimate.valueStatus;
    Reduction::AddReason(result, "INDEPENDENT_RATIO_INPUT_UNAVAILABLE");
    return output;
  }
  const std::size_t dimension = numerator.estimate.center.size();
  result.dimension = dimension;
  result.center.resize(dimension);
  for (std::size_t index = 0; index < dimension; ++index) {
    if (denominator.estimate.center[index] == 0.0) {
      result.center.clear();
      result.valueStatus = "POOLED_DENOMINATOR_ZERO";
      result.uncertaintyStatus = "UNAVAILABLE";
      result.reasons.push_back("POOLED_DENOMINATOR_ZERO:REFERENCE_TUNE");
      return output;
    }
    result.center[index] = numerator.estimate.center[index] /
                           denominator.estimate.center[index];
  }
  result.valueStatus =
      numerator.estimate.valueStatus == "UNSTABLE_DENOMINATOR" ||
              denominator.estimate.valueStatus == "UNSTABLE_DENOMINATOR"
          ? "UNSTABLE_DENOMINATOR"
          : "AVAILABLE";
  if (numerator.estimate.covariance.size() != dimension * dimension ||
      denominator.estimate.covariance.size() != dimension * dimension) {
    if (std::find(result.reasons.begin(), result.reasons.end(),
                  "CLASS_BOUNDARY_UNRESOLVED") != result.reasons.end()) {
      result.uncertaintyStatus = "CLASS_BOUNDARY_UNRESOLVED";
    } else if (std::find(result.reasons.begin(), result.reasons.end(),
                         "CLASS_BOUNDARY_UNSTABLE") != result.reasons.end()) {
      result.uncertaintyStatus = "CLASS_BOUNDARY_UNSTABLE";
    } else {
      result.uncertaintyStatus = "SOURCE_UNCERTAINTY_UNAVAILABLE";
    }
    return output;
  }
  result.covariance.assign(dimension * dimension, 0.0);
  for (std::size_t row = 0; row < dimension; ++row) {
    for (std::size_t column = 0; column < dimension; ++column) {
      const double ar = numerator.estimate.center[row];
      const double ac = numerator.estimate.center[column];
      const double br = denominator.estimate.center[row];
      const double bc = denominator.estimate.center[column];
      result.covariance[row * dimension + column] =
          numerator.estimate.covariance[row * dimension + column] / (br * bc) +
          ar * ac * denominator.estimate.covariance[row * dimension + column] /
              (br * br * bc * bc);
    }
  }
  result.standardError.resize(dimension);
  bool zero = true;
  for (std::size_t index = 0; index < dimension; ++index) {
    const double variance = result.covariance[index * dimension + index];
    if (!(variance >= 0.0) || !std::isfinite(variance)) {
      result.covariance.clear();
      result.standardError.clear();
      result.uncertaintyStatus = "COVARIANCE_ARITHMETIC_FAILURE";
      return output;
    }
    result.standardError[index] = std::sqrt(variance);
    if (variance != 0.0) zero = false;
  }
  result.uncertaintyStatus = zero ? "AVAILABLE_ZERO_DISPERSION" : "AVAILABLE";
  if (!numerator.estimate.complements.empty()) {
    for (const auto& value : numerator.estimate.complements) {
      result.complements.push_back(value);
    }
    result.leaveMean = numerator.estimate.leaveMean;
  }
  if (!denominator.estimate.complements.empty()) {
    output.referenceComplements.reserve(denominator.estimate.complements.size());
    for (const auto& value : denominator.estimate.complements) {
      output.referenceComplements.push_back(value);
    }
    output.referenceLeaveMean = denominator.estimate.leaveMean;
  }
  output.diagnostic = "independent_tune_covariance_sum";
  return output;
}

inline std::vector<Role> NominalRoles(const Domains& domains) {
  std::vector<Role> roles = {
      {"balancing.integrated.charm", "balancing", "integrated charm"},
      {"balancing.integrated.beauty", "balancing", "integrated beauty"},
      {"balancing.activity.charm", "balancing", "activity charm"},
      {"balancing.activity.beauty", "balancing", "activity beauty"},
      {"balancing.baryon_meson.activity", "balancing", "activity ratio"},
  };
  for (const auto& tune : domains.tunes) {
    roles.push_back({"correlations." + tune + ".charm", "correlations",
                     "tune=" + tune + ",sector=charm"});
    roles.push_back({"correlations." + tune + ".beauty", "correlations",
                     "tune=" + tune + ",sector=beauty"});
  }
  for (const int pdg : domains.g9Species) {
    for (const std::string axis : {"pt", "eta", "phi"}) {
      roles.push_back({"kinematics." + std::to_string(pdg) + "." + axis,
                       "kinematics", "pdg=" + std::to_string(pdg) +
                                         ",axis=" + axis});
    }
  }
  roles.push_back({"multiplicity.composite", "multiplicity",
                   "normalized distributions and independent tune ratios"});
  std::vector<std::string> ids;
  for (const auto& role : roles) ids.push_back(role.id);
  std::sort(ids.begin(), ids.end());
  if (std::adjacent_find(ids.begin(), ids.end()) != ids.end()) {
    throw std::runtime_error("nominal role registry contains a collision");
  }
  return roles;
}

}  // namespace Hadronization::Plot

#endif
