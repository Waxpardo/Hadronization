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
  // The diagonal is always available when uncertainty is valid. Dense
  // covariance is an optional derived view; leaves are the primary factors.
  std::vector<double> diagonalVariance;
  std::vector<double> standardError;
  std::vector<DenominatorAudit> denominatorAudits;
  std::vector<std::string> cancelledParentDiagnostics;
  std::size_t dimension = 0;
  std::size_t blocks = 0;
  int dof = 0;
};

struct ActivityAtom {
  double measure = 0.0;
  double numerator = 0.0;
  double denominator = 0.0;
};

struct ActivityClassSpec {
  bool integrated = false;
  int lowPercent = 0;
  int highPercent = 100;
};

struct ActivityClassBoundary {
  int low = -1;
  int high = -1;
  bool empty = true;
};

struct ActivityThresholdAudit {
  int percentile = -1;
  int pooledThreshold = -1;
  std::vector<double> belowMargins;
  std::vector<double> throughMargins;
  bool statisticallyResolved = false;
};

struct ReclassifiedRatioResult {
  ActivityClassBoundary pooledBoundary;
  std::vector<ActivityClassBoundary> deleteOneBoundaries;
  double center = std::numeric_limits<double>::quiet_NaN();
  std::vector<double> complements;
  double leaveMean = std::numeric_limits<double>::quiet_NaN();
  double variance = std::numeric_limits<double>::quiet_NaN();
  std::string centerStatus = "UNDEFINED";
  std::string uncertaintyStatus = "WITHHELD_UNCERTAINTY";
  std::vector<std::string> reasons;
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

inline int ActivityThreshold(const std::vector<double>& histogram,
                             int percentile) {
  if (percentile < 0 || percentile > 100 || histogram.empty() ||
      !FiniteVector(histogram) ||
      std::any_of(histogram.begin(), histogram.end(),
                  [](double value) { return value < 0.0; })) {
    throw std::invalid_argument("activity measure/percentile is invalid");
  }
  const double total = Sum(histogram);
  if (!(total > 0.0)) throw std::domain_error("ACTIVITY_MEASURE_UNDEFINED");
  const double target = (100.0 - percentile) / 100.0 * total;
  double cumulative = 0.0;
  for (std::size_t bin = 0; bin < histogram.size(); ++bin) {
    cumulative += histogram[bin];
    if (cumulative >= target) return static_cast<int>(bin);
  }
  return static_cast<int>(histogram.size() - 1);
}

inline ActivityClassBoundary ResolveActivityClass(
    const std::vector<double>& histogram, const ActivityClassSpec& spec) {
  if (spec.lowPercent < 0 || spec.highPercent > 100 ||
      spec.lowPercent >= spec.highPercent || histogram.empty() ||
      !FiniteVector(histogram) ||
      std::any_of(histogram.begin(),histogram.end(),
                  [](double value){return value < 0.0;})) {
    throw std::invalid_argument("activity class interval is invalid");
  }
  if (!(Sum(histogram) > 0.0))
    throw std::domain_error("ACTIVITY_MEASURE_UNDEFINED");
  ActivityClassBoundary result;
  if (spec.integrated) {
    result.low = 0;
    result.high = static_cast<int>(histogram.size() - 1);
  } else {
    result.low = spec.highPercent == 100 ? 0 :
        ActivityThreshold(histogram, spec.highPercent) + 1;
    result.high = spec.lowPercent == 0 ?
        static_cast<int>(histogram.size() - 1) :
        ActivityThreshold(histogram, spec.lowPercent);
  }
  result.empty = result.low > result.high;
  if (!result.empty) {
    std::vector<double> classMeasure(histogram.begin()+result.low,
                                     histogram.begin()+result.high+1);
    result.empty = !(Sum(classMeasure) > 0.0);
  }
  return result;
}

// The t9 test asks whether the pooled cumulative curve is distinguishable
// from the target on both sides of the integer threshold. It is distinct from
// delete-one boundary stability: all ten leaves can select the same bin while
// the pooled threshold remains statistically unresolved.
inline ActivityThresholdAudit AuditActivityThreshold(
    const std::vector<std::vector<double>>& blockHistogram, int percentile,
    const EstimatorPolicy& policy = {}) {
  if (blockHistogram.size() != 10 || blockHistogram.front().empty())
    throw std::invalid_argument("activity margin requires the K10 design");
  const std::size_t bins = blockHistogram.front().size();
  for (const auto& block : blockHistogram)
    if (block.size() != bins || !FiniteVector(block))
      throw std::invalid_argument("activity margin block domain differs");
  std::vector<double> pooled;
  pooled.reserve(bins);
  for (std::size_t bin=0;bin<bins;++bin) {
    std::vector<double> terms;
    terms.reserve(10);
    for (const auto& block:blockHistogram) terms.push_back(block[bin]);
    pooled.push_back(Sum(terms));
  }
  ActivityThresholdAudit audit;
  audit.percentile=percentile;
  audit.pooledThreshold=ActivityThreshold(pooled,percentile);
  if (percentile==0 || percentile==100) {
    audit.statisticallyResolved=true;
    return audit;
  }
  const double targetFraction=(100.0-percentile)/100.0;
  for (const auto& block:blockHistogram) {
    const double total=Sum(block);
    const double below=Sum(std::vector<double>(
        block.begin(),block.begin()+audit.pooledThreshold));
    const double through=Sum(std::vector<double>(
        block.begin(),block.begin()+audit.pooledThreshold+1));
    audit.belowMargins.push_back(below-targetFraction*total);
    audit.throughMargins.push_back(through-targetFraction*total);
  }
  const auto resolvedSide=[&](const std::vector<double>& margins, bool positive) {
    const double pooledMargin=Sum(margins);
    const double mean=pooledMargin/10.0;
    std::vector<double> squares;
    squares.reserve(10);
    for (double margin:margins)
      squares.push_back((margin-mean)*(margin-mean));
    const double variance=10.0/9.0*Sum(squares);
    return std::isfinite(variance) && variance>=0.0 &&
        (positive?pooledMargin:-pooledMargin)>
            policy.phaseAT9Quantile*std::sqrt(variance);
  };
  audit.statisticallyResolved=resolvedSide(audit.throughMargins,true) &&
      resolvedSide(audit.belowMargins,false);
  return audit;
}

// The activity coordinate is retained until each tune-local block omission is
// evaluated. Reusing pooled class membership would change the estimator.
inline ReclassifiedRatioResult ReclassifiedActivityRatio(
    const std::vector<std::vector<ActivityAtom>>& blockAtoms,
    const ActivityClassSpec& spec) {
  ReclassifiedRatioResult result;
  if (blockAtoms.empty() || blockAtoms.front().empty())
    throw std::invalid_argument("activity block atoms are empty");
  const std::size_t bins = blockAtoms.front().size();
  for (const auto& block : blockAtoms) {
    if (block.size() != bins) throw std::invalid_argument("activity bins differ");
    for (const auto& atom : block) {
      // Event weights may be signed. The pooled and each leave-one-out
      // histogram, rather than each source block, must be nonnegative.
      if (!std::isfinite(atom.measure) ||
          !std::isfinite(atom.numerator) || !std::isfinite(atom.denominator))
        throw std::invalid_argument("activity atom is nonfinite/negative measure");
    }
  }
  const auto aggregate = [&](std::size_t omitted) {
    std::vector<ActivityAtom> binsOut(bins);
    for (std::size_t bin = 0; bin < bins; ++bin) {
      std::vector<double> measure, numerator, denominator;
      for (std::size_t block = 0; block < blockAtoms.size(); ++block) {
        if (block == omitted) continue;
        measure.push_back(blockAtoms[block][bin].measure);
        numerator.push_back(blockAtoms[block][bin].numerator);
        denominator.push_back(blockAtoms[block][bin].denominator);
      }
      binsOut[bin] = {Sum(measure),Sum(numerator),Sum(denominator)};
    }
    return binsOut;
  };
  const auto evaluate = [&](const std::vector<ActivityAtom>& atoms,
                            ActivityClassBoundary& boundary) {
    std::vector<double> measure;
    measure.reserve(bins);
    for (const auto& atom : atoms) measure.push_back(atom.measure);
    boundary = ResolveActivityClass(measure,spec);
    if (boundary.empty) return std::numeric_limits<double>::quiet_NaN();
    std::vector<double> numerators,denominators;
    for (int bin = boundary.low; bin <= boundary.high; ++bin) {
      numerators.push_back(atoms[bin].numerator);
      denominators.push_back(atoms[bin].denominator);
    }
    const double denominator = Sum(denominators);
    return denominator == 0.0 ? std::numeric_limits<double>::quiet_NaN()
                              : Sum(numerators) / denominator;
  };
  try {
    result.center = evaluate(aggregate(blockAtoms.size()),result.pooledBoundary);
  } catch (const std::domain_error&) {
    return result;
  }
  if (!std::isfinite(result.center)) {
    result.centerStatus = result.pooledBoundary.empty ? "EMPTY_CLASS" : "UNDEFINED";
    return result;
  }
  result.centerStatus = "AVAILABLE";
  if (blockAtoms.size() != 10) {
    result.uncertaintyStatus = "INCOMPLETE_BLOCK_COVERAGE";
    return result;
  }
  result.complements.reserve(10);
  for (std::size_t omitted = 0; omitted < 10; ++omitted) {
    ActivityClassBoundary boundary;
    double leaf = std::numeric_limits<double>::quiet_NaN();
    try {
      leaf = evaluate(aggregate(omitted),boundary);
    } catch (const std::domain_error&) {
      // Undefined retained activity measure is a point-local refusal.
    }
    result.deleteOneBoundaries.push_back(boundary);
    result.complements.push_back(leaf);
  }
  if (!FiniteVector(result.complements)) return result;
  result.leaveMean = Sum(result.complements) / 10.0;
  std::vector<double> terms;
  for (double leaf : result.complements)
    terms.push_back((leaf-result.leaveMean)*(leaf-result.leaveMean));
  result.variance = 0.9 * Sum(terms);
  if (std::any_of(result.deleteOneBoundaries.begin(),
                  result.deleteOneBoundaries.end(),
                  [&](const ActivityClassBoundary& leaf) {
                    return leaf.low != result.pooledBoundary.low ||
                           leaf.high != result.pooledBoundary.high ||
                           leaf.empty != result.pooledBoundary.empty;
                  })) {
    result.reasons.push_back("CLASS_BOUNDARY_UNSTABLE");
    // Correct deletion-specific leaves remain diagnostic. The accepted
    // boundary policy withholds unconditional class uncertainty.
    return result;
  }
  result.uncertaintyStatus = result.variance == 0.0 ?
      "AVAILABLE_ZERO_DISPERSION" : "AVAILABLE";
  return result;
}

inline double AccumulationErrorBound(double sumabs, std::uint64_t fills) {
  if (fills < 2) return 0.0;
  constexpr double unit = 0x1p-53;
  const double operations = 2.0 * static_cast<double>(fills) + 2.0;
  if (!std::isfinite(operations) || operations * unit >= 1.0) {
    return std::numeric_limits<double>::infinity();
  }
  return operations * unit / (1.0 - operations * unit) * sumabs;
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
    const std::vector<std::string>& externalUncertaintyReasons = {},
    bool materializeDense = true) {
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
  if (materializeDense) {
    if (outputDimension > std::numeric_limits<std::size_t>::max() / outputDimension)
      throw std::overflow_error("dense covariance dimension overflows");
    result.covariance.assign(outputDimension * outputDimension, 0.0);
  }
  result.diagonalVariance.assign(outputDimension, 0.0);
  const double factor = static_cast<double>(result.blocks - 1) /
                        static_cast<double>(result.blocks);
  for (std::size_t row = 0; row < outputDimension; ++row) {
    for (std::size_t column = materializeDense ? 0 : row;
         column < (materializeDense ? outputDimension : row + 1); ++column) {
      std::vector<double> terms;
      terms.reserve(result.blocks);
      for (const auto& value : result.complements) {
        terms.push_back(factor * (value[row] - result.leaveMean[row]) *
                        (value[column] - result.leaveMean[column]));
      }
      const double value = Sum(terms);
      if (materializeDense) result.covariance[row * outputDimension + column] = value;
      if (row == column) result.diagonalVariance[row] = value;
    }
  }
  result.standardError.resize(outputDimension);
  bool zeroDispersion = true;
  for (std::size_t component = 0; component < outputDimension; ++component) {
    const double diagonal = result.diagonalVariance[component];
    if (diagonal < 0.0 || !std::isfinite(diagonal)) {
      AddReason(result, "COVARIANCE_ARITHMETIC_FAILURE");
      result.covariance.clear();
      result.diagonalVariance.clear();
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
