// Temporary scientific reference only. PLOT-1 replaces/removes this file with
// the CSV-only renderer. No public command calls it.

#include <cmath>
#include <stdexcept>
#include <string_view>

namespace ReferencePlotting {

struct Axis {
  int bins;
  double low;
  double high;
};

inline constexpr Axis kDeltaPhi{100, -1.570796, 4.712389};
inline constexpr Axis kEta{100, -4.0, 4.0};
inline constexpr Axis kPhi{100, -3.141593, 3.141593};
inline constexpr Axis kMultiplicity{4096, -0.5, 4095.5};

inline constexpr std::string_view kMeasurementInputs[] = {
    "results/measurement/balancing.csv",
    "results/measurement/correlations.csv",
    "results/measurement/kinematics.csv",
    "results/measurement/multiplicity.csv",
    "results/measurement/sample_counts.csv",
};

double Density(double content, double total, double binWidth) {
  if (!(total > 0.0) || !(binWidth > 0.0)) {
    throw std::domain_error("density needs positive total and bin width");
  }
  return content / total / binWidth;
}

double IndependentDifferenceError(double firstSem, double secondSem) {
  return std::hypot(firstSem, secondSem);
}

}  // namespace ReferencePlotting
