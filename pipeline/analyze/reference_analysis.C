// Temporary scientific reference only. ANALYZE-1 replaces/removes this file
// with the consolidated one-file analyzer. No public command calls it.

#include <array>
#include <cmath>
#include <cstddef>
#include <stdexcept>
#include <vector>

namespace ReferenceAnalysis {

bool CountsActivity(bool isFinal, bool isCharged, int charmConstituents,
                    int beautyConstituents, double pt, double eta) {
  return isFinal && isCharged && charmConstituents == 0 &&
         beautyConstituents == 0 && pt > 0.15 && std::abs(eta) <= 1.0;
}

bool DirectHadronizationStatus(int status) {
  const int absolute = std::abs(status);
  return absolute >= 81 && absolute <= 89;
}

bool TriggerAcceptance(bool isFinal, bool isSelectedState, int status,
                       double pt, double eta, bool selectedHardOrigin) {
  return isFinal && isSelectedState && DirectHadronizationStatus(status) &&
         pt > 1.0 && std::abs(eta) <= 4.0 && selectedHardOrigin;
}

bool AssociateAcceptance(bool isFinal, bool isSelectedState, int status,
                         double pt, double eta) {
  return isFinal && isSelectedState && DirectHadronizationStatus(status) &&
         pt > 0.15 && std::abs(eta) <= 4.0;
}

double BalancingYield(double oppositeSign, double sameSign,
                      double triggerDenominator) {
  if (!(triggerDenominator > 0.0)) {
    throw std::domain_error("non-positive trigger denominator");
  }
  return oppositeSign / triggerDenominator -
         sameSign / triggerDenominator;  // same-sign factor is exactly 1.0.
}

template <std::size_t N>
double SampleSem(const std::array<double, N>& values) {
  static_assert(N > 1, "sample SEM needs at least two blocks");
  double mean = 0.0;
  for (const double value : values) mean += value;
  mean /= static_cast<double>(N);
  double squares = 0.0;
  for (const double value : values) {
    const double delta = value - mean;
    squares += delta * delta;
  }
  return std::sqrt(squares /
                   (static_cast<double>(N) * static_cast<double>(N - 1)));
}

double WithinBlockRatio(double numeratorOs, double numeratorSs,
                        double numeratorTriggers, double denominatorOs,
                        double denominatorSs, double denominatorTriggers) {
  const double denominator = BalancingYield(
      denominatorOs, denominatorSs, denominatorTriggers);
  if (denominator == 0.0) {
    throw std::domain_error("zero reference balancing yield");
  }
  return BalancingYield(numeratorOs, numeratorSs, numeratorTriggers) /
         denominator;
}

const std::vector<double>& InclusivePtEdges() {
  static const std::vector<double> edges = [] {
    std::vector<double> value;
    for (int half = 0; half <= 100; ++half) {
      value.push_back(0.5 * static_cast<double>(half));
    }
    for (const double edge : {60.0, 75.0, 100.0, 150.0, 250.0, 500.0,
                              1000.0, 2000.0, 4000.0, 7000.0}) {
      value.push_back(edge);
    }
    return value;
  }();
  return edges;
}

}  // namespace ReferenceAnalysis
