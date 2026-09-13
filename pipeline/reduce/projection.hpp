#ifndef HADRONIZATION_REDUCTION_PROJECTION_HPP
#define HADRONIZATION_REDUCTION_PROJECTION_HPP

#include "statistics.hpp"

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

namespace Hadronization::Projection {

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

struct BlockSeries {
  std::vector<double> values;
  std::vector<double> absoluteErrorBounds;
  bool exact = true;
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
  bool paperOutputOnly = false;
  std::vector<int> blockIds;
  std::vector<std::string> tunes;
  std::vector<std::string> profiles;
  std::vector<std::string> activities;
  // Finite-MC eligibility is a property of the admitted member/exposure
  // manifest, not of the observed primitive dispersion.  Empty means a
  // legacy synthetic fixture whose balanced design is established elsewhere.
  std::map<std::string, std::string> tuneDesignStatus;
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
  std::vector<std::string> componentValueStatus;
  std::vector<std::string> componentUncertaintyStatus;
  std::vector<std::vector<std::string>> componentReasons;
  // Ordered references into estimate.denominatorAudits. A vector ratio's
  // component depends on its own primitive denominator, not every other bin.
  std::vector<std::vector<std::size_t>> componentDenominatorAuditIndices;
  std::vector<std::vector<double>> blockInputs;
  std::vector<std::vector<std::vector<double>>> componentBlockInputs;
  std::vector<std::vector<double>> referenceBlockInputs;
  std::vector<std::vector<std::vector<double>>> referenceComponentBlockInputs;
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

  CellValue Cell(const CellKey& key) const {
    const auto found = cells_.find(key);
    return found == cells_.end() ? CellValue{} : found->second;
  }

  void AddCell(const CellKey& key, const CellValue& value) {
    if (!std::isfinite(value.value) || !std::isfinite(value.absoluteSum) ||
        !std::isfinite(value.rowSumW2) || value.absoluteSum < std::abs(value.value) ||
        value.rowSumW2 < 0.0 || value.fills == 0 ||
        !cells_.emplace(key, value).second) {
      throw std::runtime_error("compact cell is duplicate or numerically invalid");
    }
  }

  BlockSeries Series(std::uint32_t projection, std::uint32_t scope,
                     std::uint32_t bin, std::uint32_t component) const {
    BlockSeries series;
    series.values.reserve(domains_.blockIds.size());
    series.absoluteErrorBounds.reserve(domains_.blockIds.size());
    for (const int block : domains_.blockIds) {
      const auto found = cells_.find({projection, scope,
                                      static_cast<std::uint32_t>(block), bin,
                                      component});
      if (found == cells_.end()) {
        series.values.push_back(0.0);
        series.absoluteErrorBounds.push_back(0.0);
      } else {
        series.values.push_back(found->second.value);
        series.absoluteErrorBounds.push_back(Reduction::AccumulationErrorBound(
            found->second.absoluteSum, found->second.fills));
        series.exact = false;
      }
    }
    return series;
  }

  std::vector<std::vector<double>> BlockVectors(
      const std::vector<std::tuple<std::uint32_t, std::uint32_t,
                                   std::uint32_t, std::uint32_t>>& coordinates) const {
    std::vector<std::vector<double>> result(domains_.blockIds.size());
    for (const auto& coordinate : coordinates) {
      const auto series = Series(std::get<0>(coordinate), std::get<1>(coordinate),
                                 std::get<2>(coordinate), std::get<3>(coordinate));
      for (std::size_t block = 0; block < series.values.size(); ++block) {
        result[block].push_back(series.values[block]);
      }
    }
    return result;
  }

 private:
  Domains domains_;
  std::map<CellKey, CellValue> cells_;
};

inline BlockSeries Difference(const BlockSeries& first,
                              const BlockSeries& second) {
  if (first.values.size() != second.values.size() ||
      first.absoluteErrorBounds.size() != first.values.size() ||
      second.absoluteErrorBounds.size() != second.values.size()) {
    throw std::invalid_argument("block-series difference dimensions differ");
  }
  BlockSeries result;
  result.exact = first.exact && second.exact;
  result.values.resize(first.values.size());
  result.absoluteErrorBounds.resize(first.values.size());
  for (std::size_t block = 0; block < first.values.size(); ++block) {
    result.values[block] = first.values[block] - second.values[block];
    result.absoluteErrorBounds[block] = first.absoluteErrorBounds[block] +
                                        second.absoluteErrorBounds[block];
  }
  return result;
}

inline BlockSeries Total(const std::vector<BlockSeries>& inputs) {
  if (inputs.empty()) throw std::invalid_argument("block-series total is empty");
  const std::size_t blocks = inputs.front().values.size();
  BlockSeries result;
  result.values.assign(blocks, 0.0);
  result.absoluteErrorBounds.assign(blocks, 0.0);
  for (const auto& input : inputs) {
    if (input.values.size() != blocks ||
        input.absoluteErrorBounds.size() != blocks) {
      throw std::invalid_argument("block-series total dimensions differ");
    }
    result.exact = result.exact && input.exact;
    for (std::size_t block = 0; block < blocks; ++block) {
      result.values[block] += input.values[block];
      result.absoluteErrorBounds[block] += input.absoluteErrorBounds[block];
    }
  }
  return result;
}

inline Reduction::DenominatorSeries Denominator(
    const std::string& id, const BlockSeries& series, bool survives = true) {
  return {id, series.values, series.absoluteErrorBounds, survives, series.exact};
}

inline std::vector<std::string> BoundaryReasons(const Domains& domains,
                                                const Scope& scope) {
  std::vector<std::string> reasons;
  const auto design = domains.tuneDesignStatus.find(scope.tune);
  if (design != domains.tuneDesignStatus.end() && design->second != "AVAILABLE") {
    reasons.push_back(design->second);
  }
  if (scope.classId <= 0) return reasons;
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
  result.blockInputs = blockVectors;
  const bool smallDense = !blockVectors.empty() && blockVectors.front().size() <= 64;
  result.estimate = Reduction::PooledDeleteOne(blockVectors, function, denominators,
                                                {}, reasons, smallDense);
  if (!result.estimate.cancelledParentDiagnostics.empty()) {
    result.diagnostic = "exact_algebraic_cancellation:";
    for (std::size_t index = 0;
         index < result.estimate.cancelledParentDiagnostics.size(); ++index) {
      if (index != 0) result.diagnostic += ',';
      result.diagnostic += result.estimate.cancelledParentDiagnostics[index];
    }
  }
  if (std::find(reasons.begin(), reasons.end(), "CLASS_BOUNDARY_UNSTABLE") !=
          reasons.end() ||
      std::find(reasons.begin(), reasons.end(), "CLASS_BOUNDARY_UNRESOLVED") !=
          reasons.end()) {
    if (!result.diagnostic.empty()) result.diagnostic += ';';
    result.diagnostic += "fixed_pooled_boundary_delete_one";
  }
  return result;
}

inline std::string ValueStatus(const ProjectionResult& result,
                               std::size_t component) {
  return component < result.componentValueStatus.size()
             ? result.componentValueStatus[component]
             : result.estimate.valueStatus;
}

inline std::string UncertaintyStatus(const ProjectionResult& result,
                                     std::size_t component) {
  const std::string status = component < result.componentUncertaintyStatus.size()
      ? result.componentUncertaintyStatus[component] : result.estimate.uncertaintyStatus;
  const auto dimension = result.estimate.center.size();
  if ((status == "AVAILABLE" || status == "AVAILABLE_ZERO_DISPERSION") &&
      component < dimension && component < result.estimate.diagonalVariance.size()) {
    return result.estimate.diagonalVariance[component] == 0.0
        ? "AVAILABLE_ZERO_DISPERSION" : "AVAILABLE";
  }
  return status;
}

inline const std::vector<std::string>& Reasons(const ProjectionResult& result,
                                               std::size_t component) {
  return component < result.componentReasons.size()
             ? result.componentReasons[component]
             : result.estimate.reasons;
}

inline bool AvailableUncertainty(const std::string& status) {
  return status == "AVAILABLE" || status == "AVAILABLE_ZERO_DISPERSION";
}

// A family is the original accepted tune's aligned source-block domain.  The
// same reference tune is ONE family across every ratio which depends on it.
// Missing uncertainty masks a point; it never removes its central value/key.
struct JointPoint {
  std::string id;
  bool valid = false;
  std::map<std::string, std::array<double, 10>> complements;
  std::map<std::string, double> means;
};

inline void ValidateJointPoint(const JointPoint& point) {
  if (point.id.empty()) throw std::invalid_argument("joint point identity is empty");
  if (!point.valid) return;
  if (point.complements.empty() || point.complements.size() != point.means.size()) {
    throw std::invalid_argument("joint point family domain differs");
  }
  for (const auto& family : point.complements) {
    const auto mean = point.means.find(family.first);
    const std::vector<double> values(family.second.begin(), family.second.end());
    if (family.first.empty() || mean == point.means.end() ||
        !Reduction::FiniteVector(values) || !std::isfinite(mean->second) ||
        Reduction::Sum(values) / 10.0 != mean->second) {
      throw std::invalid_argument("joint delete-one family/mean differs");
    }
  }
}

inline double JointCovariance(const JointPoint& first, const JointPoint& second) {
  ValidateJointPoint(first);
  ValidateJointPoint(second);
  if (!first.valid || !second.valid) return std::numeric_limits<double>::quiet_NaN();
  std::vector<double> terms;
  for (const auto& family : first.complements) {
    const auto other = second.complements.find(family.first);
    if (other == second.complements.end()) continue;
    for (std::size_t block = 0; block < 10; ++block) {
      terms.push_back(0.9 * (family.second[block] - first.means.at(family.first)) *
                      (other->second[block] - second.means.at(family.first)));
    }
  }
  return Reduction::Sum(terms);
}

inline ProjectionResult IndependentRatio(
    const ProjectionResult& numerator, const ProjectionResult& denominator,
    const std::vector<Reduction::DenominatorSeries>& referenceDenominators) {
  ProjectionResult output;
  output.blockInputs = numerator.blockInputs;
  output.componentBlockInputs = numerator.componentBlockInputs;
  output.referenceBlockInputs = denominator.blockInputs;
  output.referenceComponentBlockInputs = denominator.componentBlockInputs;
  auto& result = output.estimate;
  result.policy = Reduction::kEstimatorPolicy;
  result.blocks = numerator.estimate.blocks;
  result.dof = numerator.estimate.dof;
  if (result.blocks != denominator.estimate.blocks || result.blocks != 10 ||
      result.dof != denominator.estimate.dof || result.dof != 9) {
    Reduction::AddReason(result, "INDEPENDENT_RATIO_BLOCK_DOMAIN_INVALID");
    return output;
  }
  const std::size_t dimension = std::max(numerator.estimate.center.size(),
                                         denominator.estimate.center.size());
  if (dimension == 0 || referenceDenominators.size() != dimension) {
    // Undefined parent centers do not erase the primitive audit. The emitted
    // scalar still proves which reference denominator failed.
    output.componentDenominatorAuditIndices.resize(referenceDenominators.size());
    for (std::size_t index = 0; index < referenceDenominators.size(); ++index) {
      const auto first = result.denominatorAudits.size();
      Reduction::AuditDenominators({referenceDenominators[index]}, {}, result);
      for (auto audit = first; audit < result.denominatorAudits.size(); ++audit) {
        output.componentDenominatorAuditIndices[index].push_back(audit);
      }
    }
    Reduction::AddReason(result, "INDEPENDENT_RATIO_INPUT_UNAVAILABLE");
    return output;
  }
  result.dimension = dimension;
  const double missing = std::numeric_limits<double>::quiet_NaN();
  result.center.assign(dimension, missing);
  result.standardError.assign(dimension, missing);
  const bool smallDense = dimension <= 64;
  if (smallDense) result.covariance.assign(dimension * dimension, missing);
  result.diagonalVariance.assign(dimension, missing);
  result.leaveMean.assign(dimension, missing);
  output.referenceLeaveMean.assign(dimension, missing);
  result.complements.assign(result.blocks, std::vector<double>(dimension, missing));
  output.referenceComplements.assign(
      result.blocks, std::vector<double>(dimension, missing));
  output.componentValueStatus.assign(dimension, "UNAVAILABLE");
  output.componentUncertaintyStatus.assign(dimension, "UNAVAILABLE");
  output.componentReasons.resize(dimension);
  output.componentDenominatorAuditIndices.resize(dimension);
  std::vector<unsigned char> uncertaintyReady(dimension, 0);
  // A denominator internal to the reference parent moves to the numerator of
  // the final ratio.  It must exist in the pooled and every delete-one leaf,
  // but its weak-information/sign screen is not a final-denominator veto.
  const auto cancelledReferenceScreen = [](const std::string& reason) {
    return reason.rfind("DENOMINATOR_STATISTICALLY_UNRESOLVED:", 0) == 0 ||
           reason.rfind("LEAVE_DENOMINATOR_SIGN_CHANGE:", 0) == 0;
  };
  for (const auto& audit : denominator.estimate.denominatorAudits) {
    if (std::find(result.cancelledParentDiagnostics.begin(),
                  result.cancelledParentDiagnostics.end(), audit.id) ==
        result.cancelledParentDiagnostics.end()) {
      result.cancelledParentDiagnostics.push_back(audit.id);
    }
  }
  const auto appendReason = [&](std::size_t component,
                                const std::string& reason) {
    auto& reasons = output.componentReasons[component];
    if (std::find(reasons.begin(), reasons.end(), reason) == reasons.end()) {
      reasons.push_back(reason);
    }
    Reduction::AddReason(result, reason);
  };
  for (std::size_t index = 0; index < dimension; ++index) {
    for (const auto& reason : numerator.estimate.reasons) appendReason(index, reason);
    for (const auto& reason : denominator.estimate.reasons) {
      if (!cancelledReferenceScreen(reason)) appendReason(index, reason);
    }
    Reduction::JackknifeResult audit;
    audit.blocks = result.blocks;
    audit.dof = result.dof;
    Reduction::AuditDenominators({referenceDenominators[index]}, {}, audit);
    for (std::size_t local = 0; local < audit.denominatorAudits.size(); ++local) {
      output.componentDenominatorAuditIndices[index].push_back(
          result.denominatorAudits.size() + local);
    }
    result.denominatorAudits.insert(result.denominatorAudits.end(),
                                    audit.denominatorAudits.begin(),
                                    audit.denominatorAudits.end());
    for (const auto& reason : audit.reasons) appendReason(index, reason);
    const auto pooledFailure = std::find_if(
        audit.reasons.begin(), audit.reasons.end(), [](const auto& reason) {
          return reason.rfind("POOLED_DENOMINATOR_ZERO:", 0) == 0 ||
                 reason.rfind("DENOMINATOR_NUMERICALLY_UNRESOLVED:", 0) == 0;
        });
    const bool sourceCenter = index < numerator.estimate.center.size() &&
                              std::isfinite(numerator.estimate.center[index]);
    const bool referenceCenter = index < denominator.estimate.center.size() &&
                                 std::isfinite(denominator.estimate.center[index]);
    if (!sourceCenter || !referenceCenter || pooledFailure != audit.reasons.end()) {
      if (pooledFailure != audit.reasons.end()) {
        output.componentValueStatus[index] = pooledFailure->substr(
            0, pooledFailure->find(':'));
      } else {
        output.componentValueStatus[index] = !sourceCenter
            ? ValueStatus(numerator, index) : ValueStatus(denominator, index);
        appendReason(index, "INDEPENDENT_RATIO_INPUT_UNAVAILABLE");
      }
      continue;
    }
    if (denominator.estimate.center[index] == 0.0) {
      output.componentValueStatus[index] = "POOLED_DENOMINATOR_ZERO";
      appendReason(index, "POOLED_DENOMINATOR_ZERO:REFERENCE_TUNE");
      continue;
    }
    result.center[index] = numerator.estimate.center[index] /
                           denominator.estimate.center[index];
    const bool statisticallyUnresolved = std::any_of(
        audit.reasons.begin(), audit.reasons.end(), [](const auto& reason) {
          return reason.rfind("DENOMINATOR_STATISTICALLY_UNRESOLVED:", 0) == 0;
        });
    output.componentValueStatus[index] =
        ValueStatus(numerator, index) == "UNSTABLE_DENOMINATOR" ||
                statisticallyUnresolved
            ? "UNSTABLE_DENOMINATOR"
            : "AVAILABLE";
    const auto auditUncertaintyFailure = std::find_if(
        audit.reasons.begin(), audit.reasons.end(), [](const auto& reason) {
          return reason.rfind("LEAVE_DENOMINATOR_", 0) == 0 ||
                 reason.rfind("DENOMINATOR_STATISTICALLY_UNRESOLVED:", 0) == 0 ||
                 reason.rfind("NONFINITE_INPUT", 0) == 0;
        });
    if (auditUncertaintyFailure != audit.reasons.end()) {
      output.componentUncertaintyStatus[index] = auditUncertaintyFailure->substr(
          0, auditUncertaintyFailure->find(':'));
      continue;
    }
    if (!AvailableUncertainty(UncertaintyStatus(numerator, index))) {
      output.componentUncertaintyStatus[index] =
          UncertaintyStatus(numerator, index);
      continue;
    }
    const auto referenceParentFailure = std::find_if(
        denominator.estimate.reasons.begin(), denominator.estimate.reasons.end(),
        [&](const auto& reason) { return !cancelledReferenceScreen(reason); });
    if (referenceParentFailure != denominator.estimate.reasons.end()) {
      output.componentUncertaintyStatus[index] = referenceParentFailure->substr(
          0, referenceParentFailure->find(':'));
      continue;
    }
    bool complementsValid = numerator.estimate.complements.size() == result.blocks &&
                            denominator.estimate.complements.size() == result.blocks;
    for (std::size_t block = 0; complementsValid && block < result.blocks; ++block) {
      complementsValid = index < numerator.estimate.complements[block].size() &&
                         index < denominator.estimate.complements[block].size() &&
                         std::isfinite(numerator.estimate.complements[block][index]) &&
                         std::isfinite(denominator.estimate.complements[block][index]) &&
                         denominator.estimate.complements[block][index] != 0.0;
    }
    if (!complementsValid) {
      output.componentUncertaintyStatus[index] =
          "SOURCE_UNCERTAINTY_UNAVAILABLE";
      appendReason(index, "INDEPENDENT_RATIO_COMPLEMENTS_UNAVAILABLE");
      continue;
    }
    std::vector<double> sourceFamily;
    std::vector<double> referenceFamily;
    sourceFamily.reserve(result.blocks);
    referenceFamily.reserve(result.blocks);
    for (std::size_t block = 0; block < result.blocks; ++block) {
      const double sourceValue = numerator.estimate.complements[block][index] /
                                 denominator.estimate.center[index];
      const double referenceValue = numerator.estimate.center[index] /
                                    denominator.estimate.complements[block][index];
      result.complements[block][index] = sourceValue;
      output.referenceComplements[block][index] = referenceValue;
      sourceFamily.push_back(sourceValue);
      referenceFamily.push_back(referenceValue);
    }
    result.leaveMean[index] = Reduction::Sum(sourceFamily) /
                              static_cast<double>(result.blocks);
    output.referenceLeaveMean[index] = Reduction::Sum(referenceFamily) /
                                       static_cast<double>(result.blocks);
    uncertaintyReady[index] = 1;
  }

  const double factor = static_cast<double>(result.blocks - 1) /
                        static_cast<double>(result.blocks);
  for (std::size_t row = 0; row < dimension; ++row) {
    for (std::size_t column = smallDense ? 0 : row;
         column < (smallDense ? dimension : row + 1); ++column) {
      if (!uncertaintyReady[row] || !uncertaintyReady[column]) continue;
      std::vector<double> terms;
      terms.reserve(2 * result.blocks);
      for (std::size_t block = 0; block < result.blocks; ++block) {
        terms.push_back(factor *
            (result.complements[block][row] - result.leaveMean[row]) *
            (result.complements[block][column] - result.leaveMean[column]));
        terms.push_back(factor *
            (output.referenceComplements[block][row] -
             output.referenceLeaveMean[row]) *
            (output.referenceComplements[block][column] -
             output.referenceLeaveMean[column]));
      }
      const double value = Reduction::Sum(terms);
      if (smallDense) result.covariance[row * dimension + column] = value;
      if (row == column) result.diagonalVariance[row] = value;
    }
  }
  for (std::size_t index = 0; index < dimension; ++index) {
    if (!uncertaintyReady[index]) continue;
    const double variance = result.diagonalVariance[index];
    if (!(variance >= 0.0) || !std::isfinite(variance)) {
      output.componentUncertaintyStatus[index] =
          "COVARIANCE_ARITHMETIC_FAILURE";
      appendReason(index, "COVARIANCE_ARITHMETIC_FAILURE");
      continue;
    }
    result.standardError[index] = std::sqrt(variance);
    output.componentUncertaintyStatus[index] =
        variance == 0.0 ? "AVAILABLE_ZERO_DISPERSION" : "AVAILABLE";
  }
  result.valueStatus = "COMPONENT_LOCAL";
  result.uncertaintyStatus = "COMPONENT_LOCAL";
  output.diagnostic = "exact_two_independent_tune_delete_one_families";
  return output;
}

inline std::vector<Role> NominalRoles(const Domains& domains) {
  (void)domains;
  std::vector<Role> roles = {
      {"balancing.integrated.charm", "balancing", "integrated charm"},
      {"balancing.integrated.beauty", "balancing", "integrated beauty"},
      {"balancing.activity.charm", "balancing", "activity charm"},
      {"balancing.activity.beauty", "balancing", "activity beauty"},
      {"balancing.baryon_meson.activity", "balancing", "activity ratio"},
      {"correlations.charm", "correlations",
       "all selected tunes, positive charm paper triggers"},
      {"correlations.beauty", "correlations",
       "all selected tunes, positive beauty paper triggers"},
      {"multiplicity.composite", "multiplicity",
       "normalized distributions and independent tune ratios"},
  };
  std::vector<std::string> ids;
  for (const auto& role : roles) ids.push_back(role.id);
  std::sort(ids.begin(), ids.end());
  if (std::adjacent_find(ids.begin(), ids.end()) != ids.end()) {
    throw std::runtime_error("nominal role registry contains a collision");
  }
  return roles;
}

}  // namespace Hadronization::Projection

#endif
