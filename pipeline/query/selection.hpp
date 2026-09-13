#ifndef HADRONIZATION_QUERY_SELECTION_HPP
#define HADRONIZATION_QUERY_SELECTION_HPP

#include <cmath>
#include <cerrno>
#include <cstdlib>
#include <stdexcept>
#include <string>

namespace HadronizationQuery {

inline double ReadFiniteDouble(const std::string& text) {
  char* end=nullptr;errno=0;
  const double value=std::strtod(text.c_str(),&end);
  // strtod may report ERANGE for a representable subnormal. Preserve that
  // binary64 value; reject overflow and underflow that rounded a nonzero to0.
  if (text.empty() || end!=text.c_str()+text.size() || !std::isfinite(value) ||
      (errno==ERANGE && value==0.0)) throw std::runtime_error("invalid finite floating field");
  return value;
}

// This predicate is shared by exact ROOT queries and compact projections.
// Current inclusive paper profile and optional independent-minima rectangles.
struct Threshold {
  bool enabled = false;
  bool inclusive = false;
  double value = 0.0;
  bool Accept(double pt) const {
    if (!std::isfinite(pt) || pt < 0.0) return false;
    return !enabled || (inclusive ? pt >= value : pt > value);
  }
};

inline Threshold ReadThreshold(const std::string& token) {
  if (token == "NONE") return {};
  Threshold result;
  result.enabled = true;
  std::size_t offset = 0;
  if (token.compare(0, 2, ">=") == 0) {
    result.inclusive = true;
    offset = 2;
  } else {
    throw std::runtime_error("released pT threshold must declare >=");
  }
  result.value = ReadFiniteDouble(token.substr(offset));
  if (result.value < 0.0) throw std::runtime_error("invalid pT threshold");
  return result;
}

struct Profile {
  int id = 0;
  std::string name;
  Threshold trigger, associate;
  bool Trigger(double pt) const { return trigger.Accept(pt); }
  bool Pair(double triggerPt, double associatePt) const {
    return Trigger(triggerPt) && associate.Accept(associatePt);
  }
};

inline Profile ReadProfile(int id, const std::string& name,
                           const std::string& trigger,
                           const std::string& associate,
                           const std::string& relative) {
  if (relative != "NONE")
    throw std::runtime_error("eventwise relative pT selection is not released");
  Profile result{id, name, ReadThreshold(trigger), ReadThreshold(associate)};
  if (result.trigger.enabled != result.associate.enabled)
    throw std::runtime_error("released rectangle requires both minima or neither");
  if (!result.trigger.enabled && name != "inclusive")
    throw std::runtime_error("released no-floor profile must be named inclusive");
  if (result.trigger.enabled && result.associate.enabled &&
      result.trigger.value < result.associate.value) {
    throw std::runtime_error("configured trigger minimum must be at least associate minimum");
  }
  return result;
}

}  // namespace HadronizationQuery
#endif
