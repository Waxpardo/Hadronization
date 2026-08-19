#ifndef HADRONIZATION_MULTIPLICITY_BOUNDARY_UTILS_H
#define HADRONIZATION_MULTIPLICITY_BOUNDARY_UTILS_H

#include "../generation/producer/Sha256.h"

#include <TH1D.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <limits>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace HadronizationMultiplicity {

constexpr const char* kBoundaryReceiptSchema =
    "hadronization_multiplicity_boundary_receipt_v1";
// The receipt states how its numbers were made. The classes are no longer
// per-tune weighted quantiles: docs/PRODUCTION_SHAPE_DECISION.md rules one set
// of common absolute N_ch boundaries for every tune.
constexpr const char* kBoundaryAlgorithm =
    "common_absolute_nch_class_boundaries_v1";

struct HistogramIdentity {
  int nBins = 0;
  int sumw2Size = 0;
  double integral = 0.0;
  std::vector<double> edges;
  std::vector<double> contents;
  std::vector<double> errors;
  std::vector<double> sumw2;
};

inline int IntegerBinCenter(
    const HistogramIdentity& identity, int regularBin,
    const std::string& context);

inline HistogramIdentity CaptureHistogramIdentity(
    const TH1D* histogram, const std::string& context) {
  if (!histogram || !histogram->GetXaxis()) {
    throw std::runtime_error(
        "Missing summed MULTIPLICITY histogram/axis in " + context);
  }

  HistogramIdentity identity;
  identity.nBins = histogram->GetNbinsX();
  if (identity.nBins <= 0) {
    throw std::runtime_error(
        "summed MULTIPLICITY has no regular bins in " + context);
  }

  identity.edges.reserve(static_cast<std::size_t>(identity.nBins + 1));
  for (int bin = 1; bin <= identity.nBins; ++bin) {
    identity.edges.push_back(histogram->GetXaxis()->GetBinLowEdge(bin));
  }
  identity.edges.push_back(
      histogram->GetXaxis()->GetBinUpEdge(identity.nBins));
  for (std::size_t index = 0; index < identity.edges.size(); ++index) {
    if (!std::isfinite(identity.edges[index]) ||
        (index != 0 &&
         !(identity.edges[index] > identity.edges[index - 1]))) {
      throw std::runtime_error(
          "summed MULTIPLICITY has non-finite or non-increasing bin "
          "edges in " +
          context);
    }
  }
  int previousCenter = 0;
  for (int bin = 1; bin <= identity.nBins; ++bin) {
    const int center = IntegerBinCenter(identity, bin, context);
    if (bin != 1 && center != previousCenter + 1) {
      throw std::runtime_error(
          "summed MULTIPLICITY regular bins must represent consecutive "
          "integer Nch values in " +
          context);
    }
    previousCenter = center;
  }

  identity.contents.reserve(static_cast<std::size_t>(identity.nBins + 2));
  identity.errors.reserve(static_cast<std::size_t>(identity.nBins + 2));
  for (int bin = 0; bin <= identity.nBins + 1; ++bin) {
    const double content = histogram->GetBinContent(bin);
    const double error = histogram->GetBinError(bin);
    if (!std::isfinite(content) || content < 0.0 ||
        !std::isfinite(error) || error < 0.0) {
      throw std::runtime_error(
          "summed MULTIPLICITY has invalid bin content/error at bin " +
          std::to_string(bin) + " in " + context);
    }
    identity.contents.push_back(content);
    identity.errors.push_back(error);
    if (bin >= 1 && bin <= identity.nBins) identity.integral += content;
  }
  if (!std::isfinite(identity.integral) || !(identity.integral > 0.0)) {
    throw std::runtime_error(
        "summed MULTIPLICITY has non-finite or non-positive regular-bin "
        "integral in " +
        context);
  }
  // The percentile definition is explicitly regular-bin-only. Nonzero flow
  // bins would make that convention lose events, so publication runs reject
  // them instead of silently excluding them.
  if (identity.contents.front() != 0.0 ||
      identity.contents.back() != 0.0) {
    throw std::runtime_error(
        "summed MULTIPLICITY underflow/overflow must both be exactly zero "
        "for the regular-bin percentile convention in " +
        context);
  }

  identity.sumw2Size = histogram->GetSumw2N();
  if (identity.sumw2Size != 0 &&
      identity.sumw2Size != identity.nBins + 2) {
    throw std::runtime_error(
        "summed MULTIPLICITY has an unexpected Sumw2 size in " + context);
  }
  identity.sumw2.reserve(static_cast<std::size_t>(identity.sumw2Size));
  for (int index = 0; index < identity.sumw2Size; ++index) {
    const double value = histogram->GetSumw2()->At(index);
    if (!std::isfinite(value) || value < 0.0) {
      throw std::runtime_error(
          "summed MULTIPLICITY has invalid Sumw2 data in " + context);
    }
    identity.sumw2.push_back(value);
  }
  return identity;
}

inline void RequireIdenticalHistogram(
    const HistogramIdentity& expected,
    const HistogramIdentity& observed,
    const std::string& expectedContext,
    const std::string& observedContext) {
  if (expected.nBins != observed.nBins ||
      expected.sumw2Size != observed.sumw2Size ||
      expected.edges != observed.edges ||
      expected.contents != observed.contents ||
      expected.errors != observed.errors ||
      expected.sumw2 != observed.sumw2) {
    throw std::runtime_error(
        "summed MULTIPLICITY bin edges, contents, errors, or Sumw2 differ "
        "between tune-level pair inputs:\n  reference: " +
        expectedContext + "\n  observed: " + observedContext);
  }
}

inline std::string HistogramIdentitySha256(
    const HistogramIdentity& identity) {
  std::ostringstream serialized;
  serialized << "summed_multiplicity_identity_v1\n"
             << identity.nBins << "\n"
             << identity.sumw2Size << "\n"
             << std::scientific
             << std::setprecision(std::numeric_limits<double>::max_digits10);
  const auto append = [&](const char* label,
                          const std::vector<double>& values) {
    serialized << label << " " << values.size() << "\n";
    for (const double value : values) serialized << value << "\n";
  };
  append("edges", identity.edges);
  append("contents", identity.contents);
  append("errors", identity.errors);
  append("sumw2", identity.sumw2);
  return Hadronization::Sha256Hex(serialized.str());
}

inline int IntegerBinCenter(
    const HistogramIdentity& identity, int regularBin,
    const std::string& context) {
  if (regularBin < 1 || regularBin > identity.nBins) {
    throw std::runtime_error(
        "regular multiplicity bin is outside its axis in " + context);
  }
  const double center =
      0.5 * (identity.edges[regularBin - 1] +
             identity.edges[regularBin]);
  const double rounded = std::round(center);
  if (!std::isfinite(center) ||
      std::abs(center - rounded) > 1e-9 ||
      rounded < static_cast<double>(std::numeric_limits<int>::min()) ||
      rounded > static_cast<double>(std::numeric_limits<int>::max())) {
    throw std::runtime_error(
        "summed MULTIPLICITY quantile boundary is not an integer Nch bin "
        "center in " +
        context);
  }
  return static_cast<int>(rounded);
}

inline int ThresholdForPercentile(
    const HistogramIdentity& identity, double percentile,
    const std::string& context) {
  if (!std::isfinite(percentile) ||
      percentile < 0.0 || percentile > 100.0) {
    throw std::runtime_error(
        "invalid multiplicity percentile " + std::to_string(percentile) +
        " in " + context);
  }
  const double target =
      ((100.0 - percentile) / 100.0) * identity.integral;
  double running = 0.0;
  for (int bin = 1; bin <= identity.nBins; ++bin) {
    running += identity.contents[static_cast<std::size_t>(bin)];
    if (running >= target) {
      return IntegerBinCenter(identity, bin, context);
    }
  }
  throw std::runtime_error(
      "failed to locate multiplicity threshold for percentile " +
      std::to_string(percentile) +
      "; refusing first/last-bin fallback in " + context);
}

inline int ThresholdForPercentile(
    const TH1D* histogram, double percentile, const std::string& context) {
  return ThresholdForPercentile(
      CaptureHistogramIdentity(histogram, context), percentile, context);
}

inline std::pair<int, int> DiscreteClassRange(
    const std::map<double, int>& thresholds,
    double lowActivityPercentile,
    double highActivityPercentile) {
  if (!std::isfinite(lowActivityPercentile) ||
      !std::isfinite(highActivityPercentile) ||
      !(lowActivityPercentile >= 0.0 &&
        highActivityPercentile <= 100.0 &&
        lowActivityPercentile < highActivityPercentile)) {
    throw std::runtime_error("invalid multiplicity-percentile interval");
  }
  int minimum = thresholds.at(highActivityPercentile);
  if (highActivityPercentile < 100.0) ++minimum;
  const int maximum = thresholds.at(lowActivityPercentile);
  if (minimum > maximum) {
    throw std::runtime_error(
        "empty discrete multiplicity class for percentiles [" +
        std::to_string(lowActivityPercentile) + "," +
        std::to_string(highActivityPercentile) + "]: Nch=[" +
        std::to_string(minimum) + "," + std::to_string(maximum) + "]");
  }
  return {minimum, maximum};
}

inline int FindRegularBinForNch(
    const HistogramIdentity& identity, int nch,
    const std::string& context) {
  for (int bin = 1; bin <= identity.nBins; ++bin) {
    if (IntegerBinCenter(identity, bin, context) == nch) return bin;
  }
  throw std::runtime_error(
      "Nch=" + std::to_string(nch) +
      " is not represented by a regular integer bin in " + context);
}

inline double InclusiveWeight(
    const HistogramIdentity& identity, int nchMin, int nchMax,
    const std::string& context) {
  if (nchMin > nchMax) {
    throw std::runtime_error("invalid inclusive Nch range in " + context);
  }
  const int first = FindRegularBinForNch(identity, nchMin, context);
  const int last = FindRegularBinForNch(identity, nchMax, context);
  double total = 0.0;
  for (int bin = first; bin <= last; ++bin) {
    total += identity.contents[static_cast<std::size_t>(bin)];
  }
  return total;
}

inline double CumulativeFractionThrough(
    const HistogramIdentity& identity, int nch,
    const std::string& context) {
  const int last = FindRegularBinForNch(identity, nch, context);
  double total = 0.0;
  for (int bin = 1; bin <= last; ++bin) {
    total += identity.contents[static_cast<std::size_t>(bin)];
  }
  return total / identity.integral;
}

inline double CumulativeFractionBefore(
    const HistogramIdentity& identity, int nch,
    const std::string& context) {
  const int boundary = FindRegularBinForNch(identity, nch, context);
  double total = 0.0;
  for (int bin = 1; bin < boundary; ++bin) {
    total += identity.contents[static_cast<std::size_t>(bin)];
  }
  return total / identity.integral;
}

inline std::vector<std::pair<double, double>>
ValidateAndOrderPartition(
    const std::vector<std::pair<double, double>>& configuredClasses) {
  std::vector<std::pair<double, double>> partition;
  for (const auto& interval : configuredClasses) {
    const double low = interval.first;
    const double high = interval.second;
    if (!std::isfinite(low) || !std::isfinite(high) ||
        low < 0.0 || high > 100.0 || !(low < high)) {
      throw std::runtime_error(
          "invalid configured multiplicity-percentile class");
    }
    // The integrated 0-100% bin is an observable, not an additional member
    // of the mutually exclusive activity partition.
    if (low == 0.0 && high == 100.0 &&
        configuredClasses.size() > 1U) {
      continue;
    }
    partition.push_back(interval);
  }
  std::sort(
      partition.begin(), partition.end(),
      [](const auto& first, const auto& second) {
        if (first.first != second.first) {
          return first.first > second.first;
        }
        return first.second > second.second;
      });
  if (partition.empty() ||
      partition.front().second != 100.0 ||
      partition.back().first != 0.0) {
    throw std::runtime_error(
        "multiplicity-percentile classes must cover exactly 0-100%");
  }
  for (std::size_t index = 1; index < partition.size(); ++index) {
    if (partition[index - 1].first != partition[index].second) {
      throw std::runtime_error(
          "multiplicity-percentile classes have a gap or overlap");
    }
  }
  return partition;
}

inline void RequireDiscretePartitionCoverage(
    const std::vector<std::pair<double, double>>& configuredClasses,
    const std::map<double, int>& thresholds) {
  const auto partition = ValidateAndOrderPartition(configuredClasses);
  int expectedMinimum = thresholds.at(100.0);
  for (const auto& interval : partition) {
    const auto range =
        DiscreteClassRange(thresholds, interval.first, interval.second);
    if (range.first != expectedMinimum) {
      throw std::runtime_error(
          "discrete multiplicity classes have a gap or overlap at Nch=" +
          std::to_string(expectedMinimum));
    }
    expectedMinimum = range.second + 1;
  }
  if (expectedMinimum != thresholds.at(0.0) + 1) {
    throw std::runtime_error(
        "discrete multiplicity classes do not cover the full frozen Nch "
        "domain");
  }
}

}  // namespace HadronizationMultiplicity

#endif
