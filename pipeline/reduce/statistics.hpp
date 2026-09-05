#ifndef HADRONIZATION_REDUCTION_STATISTICS_HPP
#define HADRONIZATION_REDUCTION_STATISTICS_HPP

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <limits>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace Hadronization::Reduction {

inline constexpr const char* kEstimatorPolicy =
    "pooled_delete_one_source_block_jackknife_v2";

struct EstimatorPolicy {
  double denominatorResolutionAlpha = 0.05;
  double phaseAT9Quantile = 2.2621571628540993;
};

struct DenominatorSeries {
  std::string id;
  std::vector<double> blocks;
  std::vector<double> absoluteErrorBounds;
  bool algebraicallySurvives = true;
  bool exact = false;
};

struct FunctionValue {
  bool defined = false;
  std::vector<double> values;
  std::string reason;
};

using EstimatorFunction = std::function<FunctionValue(const std::vector<double>&)>;

struct DenominatorAudit {
  std::string id;
  bool algebraicallySurvives = true;
  double pooled = 0.0;
  double pooledErrorBound = 0.0;
  double varianceScale = 0.0;
  double information = 0.0;
  double cancellationRatio = 0.0;
  double minimumComplementLeverageGap = 0.0;
};

struct JackknifeResult {
  std::string policy = kEstimatorPolicy;
  std::string valueStatus = "UNAVAILABLE";
  std::string uncertaintyStatus = "UNAVAILABLE";
  std::vector<std::string> reasons;
  std::vector<double> center;
  std::vector<std::vector<double>> originalBlockEstimates;
  std::vector<double> originalBlockMean;
  std::vector<double> originalBlockSem;
  std::vector<std::vector<double>> complements;
  std::vector<double> leaveMean;
  std::vector<double> covariance;
  std::vector<double> standardError;
  std::vector<DenominatorAudit> denominatorAudits;
  std::vector<std::string> cancelledParentDiagnostics;
  std::size_t dimension = 0;
  std::size_t blocks = 0;
  int dof = 0;
};

inline void AddReason(JackknifeResult& result, const std::string& reason) {
  if (std::find(result.reasons.begin(), result.reasons.end(), reason) ==
      result.reasons.end()) {
    result.reasons.push_back(reason);
  }
}

inline bool FiniteVector(const std::vector<double>& values) {
  return std::all_of(values.begin(), values.end(),
                     [](double value) { return std::isfinite(value); });
}

inline double Sum(const std::vector<double>& values) {
  double total = 0.0;
  double correction = 0.0;
  for (const double value : values) {
    const double next = total + value;
    if (std::abs(total) >= std::abs(value)) {
      correction += (total - next) + value;
    } else {
      correction += (value - next) + total;
    }
    total = next;
  }
  return total + correction;
}

inline bool IntervalContainsZero(double value, double error) {
  return !std::isfinite(value) || !std::isfinite(error) || error < 0.0 ||
         std::abs(value) <= error;
}

inline void AuditDenominators(const std::vector<DenominatorSeries>& denominators,
                              const EstimatorPolicy& policy,
                              JackknifeResult& result) {
  for (const auto& series : denominators) {
    if (series.blocks.size() != result.blocks ||
        (!series.absoluteErrorBounds.empty() &&
         series.absoluteErrorBounds.size() != result.blocks) ||
        !FiniteVector(series.blocks) ||
        (!series.absoluteErrorBounds.empty() &&
         !FiniteVector(series.absoluteErrorBounds))) {
      AddReason(result, "NONFINITE_INPUT:" + series.id);
      continue;
    }
    const double pooled = Sum(series.blocks);
    const double pooledError = series.absoluteErrorBounds.empty()
                                   ? 0.0
                                   : Sum(series.absoluteErrorBounds);
    std::vector<double> squaredTerms;
    std::vector<double> absoluteTerms;
    squaredTerms.reserve(result.blocks);
    absoluteTerms.reserve(result.blocks);
    const double mean = pooled / static_cast<double>(result.blocks);
    double minimumGap = std::numeric_limits<double>::infinity();
    for (std::size_t block = 0; block < result.blocks; ++block) {
      const double delta = series.blocks[block] - mean;
      squaredTerms.push_back(delta * delta);
      absoluteTerms.push_back(std::abs(series.blocks[block]));
      if (pooled != 0.0) {
        minimumGap = std::min(minimumGap,
                              std::abs(1.0 - series.blocks[block] / pooled));
      }
    }
    const double squared = Sum(squaredTerms);
    const double absolute = Sum(absoluteTerms);
    const double variance = result.blocks > 1
        ? static_cast<double>(result.blocks) /
              static_cast<double>(result.blocks - 1) * squared
        : std::numeric_limits<double>::quiet_NaN();
    double information = std::numeric_limits<double>::infinity();
    if (variance > 0.0) information = pooled * pooled / variance;
    DenominatorAudit audit{series.id, series.algebraicallySurvives, pooled,
                           pooledError, variance, information,
                           pooled == 0.0
                               ? std::numeric_limits<double>::infinity()
                               : absolute / std::abs(pooled),
                           minimumGap};
    result.denominatorAudits.push_back(audit);
    if (!series.algebraicallySurvives) {
      result.cancelledParentDiagnostics.push_back(series.id);
    }
    if (series.exact && pooled == 0.0) {
      AddReason(result, "POOLED_DENOMINATOR_ZERO:" + series.id);
      continue;
    }
    if (!series.exact && IntervalContainsZero(pooled, pooledError)) {
      AddReason(result, "DENOMINATOR_NUMERICALLY_UNRESOLVED:" + series.id);
      continue;
    }
    for (std::size_t block = 0; block < result.blocks; ++block) {
      std::vector<double> retained;
      std::vector<double> retainedErrors;
      retained.reserve(result.blocks - 1);
      retainedErrors.reserve(result.blocks - 1);
      for (std::size_t candidate = 0; candidate < result.blocks; ++candidate) {
        if (candidate == block) continue;
        retained.push_back(series.blocks[candidate]);
        if (!series.absoluteErrorBounds.empty()) {
          retainedErrors.push_back(series.absoluteErrorBounds[candidate]);
        }
      }
      const double complement = Sum(retained);
      const double complementError = retainedErrors.empty()
          ? 0.0 : Sum(retainedErrors);
      if (series.exact && complement == 0.0) {
        AddReason(result, "LEAVE_DENOMINATOR_ZERO:" + series.id + ":" +
                              std::to_string(block + 1));
      } else if (!series.exact &&
                 IntervalContainsZero(complement, complementError)) {
        AddReason(result, "LEAVE_DENOMINATOR_NUMERICALLY_UNRESOLVED:" + series.id +
                              ":" + std::to_string(block + 1));
      } else if (series.algebraicallySurvives &&
                 std::signbit(complement) != std::signbit(pooled)) {
        AddReason(result, "LEAVE_DENOMINATOR_SIGN_CHANGE:" + series.id + ":" +
                              std::to_string(block + 1));
      }
    }
    if (series.algebraicallySurvives &&
        !(information > policy.phaseAT9Quantile * policy.phaseAT9Quantile)) {
      AddReason(result,
                "DENOMINATOR_STATISTICALLY_UNRESOLVED:" + series.id);
    }
  }
}

inline JackknifeResult PooledDeleteOne(
    const std::vector<std::vector<double>>& blockVectors,
    const EstimatorFunction& function,
    const std::vector<DenominatorSeries>& denominators = {},
    const EstimatorPolicy& policy = {},
    const std::vector<std::string>& externalUncertaintyReasons = {}) {
  JackknifeResult result;
  result.blocks = blockVectors.size();
  result.dof = result.blocks == 0 ? 0 : static_cast<int>(result.blocks - 1);
  if (result.blocks < 2) {
    AddReason(result, "INCOMPLETE_BLOCK_SET");
    return result;
  }
  result.dimension = blockVectors.front().size();
  if (result.dimension == 0 || std::any_of(
          blockVectors.begin(), blockVectors.end(), [&](const auto& values) {
            return values.size() != result.dimension || !FiniteVector(values);
          })) {
    AddReason(result, "NONFINITE_INPUT");
    return result;
  }
  std::vector<double> pooled(result.dimension, 0.0);
  for (std::size_t component = 0; component < result.dimension; ++component) {
    std::vector<double> column;
    column.reserve(result.blocks);
    for (const auto& block : blockVectors) column.push_back(block[component]);
    pooled[component] = Sum(column);
  }
  AuditDenominators(denominators, policy, result);
  const FunctionValue center = function(pooled);
  if (!center.defined || center.values.empty() || !FiniteVector(center.values)) {
    AddReason(result, center.reason.empty() ? "UNDEFINED_POOLED" : center.reason);
  } else {
    result.center = center.values;
    result.valueStatus = "AVAILABLE";
  }
  bool denominatorValueFailure = false;
  bool denominatorUncertaintyFailure = false;
  bool denominatorStatisticalFailure = false;
  for (const std::string& reason : result.reasons) {
    if (reason.rfind("POOLED_DENOMINATOR_ZERO:", 0) == 0 ||
        reason.rfind("DENOMINATOR_NUMERICALLY_UNRESOLVED:", 0) == 0) {
      denominatorValueFailure = true;
    }
    if (reason.rfind("LEAVE_DENOMINATOR_", 0) == 0 ||
        reason.rfind("DENOMINATOR_", 0) == 0 ||
        reason.rfind("NONFINITE_INPUT", 0) == 0) {
      denominatorUncertaintyFailure = true;
    }
    if (reason.rfind("DENOMINATOR_STATISTICALLY_UNRESOLVED:", 0) == 0) {
      denominatorStatisticalFailure = true;
    }
  }
  if (denominatorValueFailure) {
    const auto found = std::find_if(result.reasons.begin(), result.reasons.end(),
        [](const std::string& reason) {
          return reason.rfind("POOLED_DENOMINATOR_ZERO:", 0) == 0 ||
                 reason.rfind("DENOMINATOR_NUMERICALLY_UNRESOLVED:", 0) == 0;
        });
    result.valueStatus = found->substr(0, found->find(':'));
    result.center.clear();
  } else if (!result.center.empty() && denominatorStatisticalFailure) {
    result.valueStatus = "UNSTABLE_DENOMINATOR";
  }
  for (const auto& reason : externalUncertaintyReasons) AddReason(result, reason);
  if (result.center.empty()) return result;
  bool allOriginalBlocksDefined = true;
  result.originalBlockEstimates.reserve(result.blocks);
  for (const auto& block : blockVectors) {
    const FunctionValue value = function(block);
    if (!value.defined || value.values.size() != result.center.size() ||
        !FiniteVector(value.values)) {
      allOriginalBlocksDefined = false;
      result.originalBlockEstimates.push_back({});
    } else {
      result.originalBlockEstimates.push_back(value.values);
    }
  }
  if (allOriginalBlocksDefined) {
    result.originalBlockMean.assign(result.center.size(), 0.0);
    result.originalBlockSem.assign(result.center.size(), 0.0);
    for (std::size_t component = 0; component < result.center.size(); ++component) {
      std::vector<double> column;
      for (const auto& value : result.originalBlockEstimates) {
        column.push_back(value[component]);
      }
      const double mean = Sum(column) / static_cast<double>(result.blocks);
      result.originalBlockMean[component] = mean;
      std::vector<double> squaredTerms;
      squaredTerms.reserve(column.size());
      for (const double value : column) {
        squaredTerms.push_back((value - mean) * (value - mean));
      }
      const double squared = Sum(squaredTerms);
      result.originalBlockSem[component] = std::sqrt(
          squared / (static_cast<double>(result.blocks) *
                     static_cast<double>(result.blocks - 1)));
    }
  }
  result.complements.reserve(result.blocks);
  for (std::size_t removed = 0; removed < result.blocks; ++removed) {
    std::vector<double> complement(result.dimension, 0.0);
    for (std::size_t component = 0; component < result.dimension; ++component) {
      std::vector<double> column;
      column.reserve(result.blocks - 1);
      for (std::size_t block = 0; block < result.blocks; ++block) {
        if (block != removed) column.push_back(blockVectors[block][component]);
      }
      complement[component] = Sum(column);
    }
    const FunctionValue value = function(complement);
    if (!value.defined || value.values.size() != result.center.size() ||
        !FiniteVector(value.values)) {
      std::string reason = value.reason;
      if (reason == "POOLED_DENOMINATOR_ZERO") {
        reason = "LEAVE_DENOMINATOR_ZERO";
      } else if (reason == "POOLED_DENOMINATOR_NONPOSITIVE") {
        reason = "LEAVE_DENOMINATOR_NONPOSITIVE";
      }
      AddReason(result, reason.empty()
                            ? "UNDEFINED_COMPLEMENT:" +
                                  std::to_string(removed + 1)
                            : reason + ":" +
                                  std::to_string(removed + 1));
      denominatorUncertaintyFailure = true;
      result.complements.push_back({});
    } else {
      result.complements.push_back(value.values);
    }
  }
  for (const std::string& reason : result.reasons) {
    if (reason == "CLASS_BOUNDARY_UNSTABLE" ||
        reason == "CLASS_BOUNDARY_UNRESOLVED" ||
        reason == "INCOMPLETE_BLOCK_SET" ||
        reason == "UNEQUAL_DESIGN_EXPOSURE" ||
        reason == "INCOMPATIBLE_BLOCK_DESIGN") {
      denominatorUncertaintyFailure = true;
    }
  }
  if (denominatorUncertaintyFailure ||
      std::any_of(result.complements.begin(), result.complements.end(),
                  [](const auto& value) { return value.empty(); })) {
    if (!result.reasons.empty()) {
      result.uncertaintyStatus = result.reasons.back().substr(
          0, result.reasons.back().find(':'));
    }
    return result;
  }
  const std::size_t outputDimension = result.center.size();
  result.leaveMean.assign(outputDimension, 0.0);
  for (std::size_t component = 0; component < outputDimension; ++component) {
    std::vector<double> column;
    column.reserve(result.blocks);
    for (const auto& value : result.complements) column.push_back(value[component]);
    result.leaveMean[component] = Sum(column) /
                                  static_cast<double>(result.blocks);
  }
  result.covariance.assign(outputDimension * outputDimension, 0.0);
  const double factor = static_cast<double>(result.blocks - 1) /
                        static_cast<double>(result.blocks);
  for (std::size_t row = 0; row < outputDimension; ++row) {
    for (std::size_t column = 0; column < outputDimension; ++column) {
      std::vector<double> terms;
      terms.reserve(result.blocks);
      for (const auto& value : result.complements) {
        terms.push_back(factor * (value[row] - result.leaveMean[row]) *
                        (value[column] - result.leaveMean[column]));
      }
      result.covariance[row * outputDimension + column] = Sum(terms);
    }
  }
  result.standardError.resize(outputDimension);
  bool zeroDispersion = true;
  for (std::size_t component = 0; component < outputDimension; ++component) {
    const double diagonal = result.covariance[
        component * outputDimension + component];
    if (diagonal < 0.0 || !std::isfinite(diagonal)) {
      AddReason(result, "COVARIANCE_ARITHMETIC_FAILURE");
      result.covariance.clear();
      result.standardError.clear();
      return result;
    }
    result.standardError[component] = std::sqrt(diagonal);
    if (diagonal != 0.0) zeroDispersion = false;
  }
  result.uncertaintyStatus = zeroDispersion ? "AVAILABLE_ZERO_DISPERSION"
                                            : "AVAILABLE";
  return result;
}

inline FunctionValue Ratio(std::size_t numerator, std::size_t denominator,
                           const std::vector<double>& values) {
  if (numerator >= values.size() || denominator >= values.size() ||
      values[denominator] == 0.0) {
    return {false, {}, "POOLED_DENOMINATOR_ZERO"};
  }
  return {true, {values[numerator] / values[denominator]}, {}};
}

inline FunctionValue Normalized(std::size_t first, std::size_t count,
                                const std::vector<double>& values) {
  if (first > values.size() || count > values.size() - first || count == 0) {
    return {false, {}, "NORMALIZATION_DOMAIN_INVALID"};
  }
  std::vector<double> domain;
  domain.reserve(count);
  for (std::size_t index = 0; index < count; ++index) {
    domain.push_back(values[first + index]);
  }
  const double total = Sum(domain);
  if (total == 0.0 || !std::isfinite(total)) {
    return {false, {}, "POOLED_DENOMINATOR_ZERO"};
  }
  std::vector<double> result(count);
  for (std::size_t index = 0; index < count; ++index) {
    result[index] = values[first + index] / total;
  }
  return {true, result, {}};
}

inline double CovarianceNullResidual(const std::vector<double>& covariance,
                                     std::size_t dimension,
                                     const std::vector<double>& constraint) {
  if (covariance.size() != dimension * dimension ||
      constraint.size() != dimension) {
    throw std::invalid_argument("covariance/null-constraint dimensions differ");
  }
  double maximum = 0.0;
  for (std::size_t row = 0; row < dimension; ++row) {
    std::vector<double> terms;
    terms.reserve(dimension);
    for (std::size_t column = 0; column < dimension; ++column) {
      terms.push_back(covariance[row * dimension + column] *
                      constraint[column]);
    }
    const double value = Sum(terms);
    maximum = std::max(maximum, std::abs(value));
  }
  return maximum;
}

inline std::vector<double> EventInfluenceCovariance(
    const std::vector<double>& jacobian, std::size_t outputDimension,
    std::size_t primitiveDimension, const std::vector<double>& eventGram,
    const std::vector<double>& totals, std::uint64_t events) {
  if (events < 2 || jacobian.size() != outputDimension * primitiveDimension ||
      eventGram.size() != primitiveDimension * primitiveDimension ||
      totals.size() != primitiveDimension || !FiniteVector(jacobian) ||
      !FiniteVector(eventGram) || !FiniteVector(totals)) {
    throw std::invalid_argument("event-influence dimensions/domain differ");
  }
  std::vector<double> centered(eventGram);
  for (std::size_t row = 0; row < primitiveDimension; ++row) {
    for (std::size_t column = 0; column < primitiveDimension; ++column) {
      centered[row * primitiveDimension + column] -=
          totals[row] * totals[column] / static_cast<double>(events);
    }
  }
  std::vector<double> covariance(outputDimension * outputDimension, 0.0);
  const double sampleFactor = static_cast<double>(events) /
                              static_cast<double>(events - 1);
  for (std::size_t outRow = 0; outRow < outputDimension; ++outRow) {
    for (std::size_t outColumn = 0; outColumn < outputDimension; ++outColumn) {
      std::vector<double> terms;
      terms.reserve(primitiveDimension * primitiveDimension);
      for (std::size_t left = 0; left < primitiveDimension; ++left) {
        for (std::size_t right = 0; right < primitiveDimension; ++right) {
          terms.push_back(jacobian[outRow * primitiveDimension + left] *
                          centered[left * primitiveDimension + right] *
                          jacobian[outColumn * primitiveDimension + right]);
        }
      }
      covariance[outRow * outputDimension + outColumn] =
          sampleFactor * Sum(terms);
    }
  }
  return covariance;
}

}  // namespace Hadronization::Reduction

#endif
