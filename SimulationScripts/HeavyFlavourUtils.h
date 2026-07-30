#ifndef HADRONIZATION_HEAVY_FLAVOUR_UTILS_H
#define HADRONIZATION_HEAVY_FLAVOUR_UTILS_H

#include "GeneratedWeakParentRegistry.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <deque>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace Hadronization {

inline constexpr const char* kRawSchema = "hf_primary_ground_raw_v5";
inline constexpr const char* kSelectorVersion =
    "hard_trigger_primary_ground__primary_ground_associate_v1";
inline constexpr const char* kOriginAlgorithmVersion =
    "signed_heavy_constituent_complete_mothers_unique_v4";
inline constexpr const char* kMultiplicityCentral = "NCH_HADRONISATION_V1";
inline constexpr const char* kMultiplicityCrossCheck = "NCH_FINAL_STRONG_EM_V1";
inline constexpr const char* kHeavyStabilityAuditSchema =
    "heavy_stability_audit_v2";
inline constexpr const char* kEffectiveSettingsSchema =
    "effective_pythia_settings_exhaustive_v2";
inline constexpr const char* kPrimaryAllHeavyMatchSchema =
    "primary_all_heavy_constituent_match_v1";

enum class Origin : int {
  kUnresolved = 0,
  kSelectedHard = 1,
  kShower = 2,
  kMPI = 3,
  kOtherResolved = 4
};

enum class MatchResolution : int {
  kNotApplicable = 0,
  kUnique = 1,
  kAmbiguous = 2,
  kMissingCarrier = 3,
  kBrokenLineage = 4,
  kDuplicateHardCarrier = 5,
  kMultipleHeavyConstituents = 6
};

struct HeavyOriginMatch {
  Origin origin = Origin::kUnresolved;
  int hardRootIndex = -1;
  int depth = -1;
  MatchResolution resolution = MatchResolution::kNotApplicable;
};

inline bool CarriesSignedHeavyConstituent(int pdg, int flavour,
                                          int requiredSign) {
  if (pdg == requiredSign * flavour) return true;
  const int absolute = std::abs(pdg);
  // PYTHIA/PDG diquark code q1 q2 0 spin. The sign identifies a diquark or
  // antidiquark, so a heavy-flavour-bearing junction endpoint is explicit.
  if (absolute >= 1000 && absolute <= 9999 &&
      (absolute / 10) % 10 == 0) {
    const int q1 = (absolute / 1000) % 10;
    const int q2 = (absolute / 100) % 10;
    const int sign = pdg > 0 ? 1 : -1;
    return sign == requiredSign && (q1 == flavour || q2 == flavour);
  }
  return false;
}

// Pure graph traversal used by the producer's PYTHIA adapter. pdgAt/statusAt
// return node properties, mothersAt returns direct expanded mother indices,
// and isSelectedHardRoot verifies an exact signed selected-hard root. The
// helper owns no generator state, making every topology independently
// testable while preserving the v4 traversal and depth semantics.
template <typename PdgAt, typename StatusAt, typename MothersAt,
          typename IsSelectedHardRoot>
HeavyOriginMatch MatchHeavyOriginGraph(
    int particleIndex, int particleCount, int flavour, int requiredSign,
    PdgAt pdgAt, StatusAt statusAt, MothersAt mothersAt,
    IsSelectedHardRoot isSelectedHardRoot) {
  if (requiredSign == 0) return {};
  if (particleIndex <= 0 || particleIndex >= particleCount) {
    return {Origin::kUnresolved, -1, -1,
            MatchResolution::kBrokenLineage};
  }

  const auto normalizedMothers = [&](int index) {
    std::vector<int> mothers = mothersAt(index);
    mothers.erase(
        std::remove_if(mothers.begin(), mothers.end(),
                       [particleCount](int mother) {
                         return mother <= 0 || mother >= particleCount;
                       }),
        mothers.end());
    std::sort(mothers.begin(), mothers.end());
    mothers.erase(std::unique(mothers.begin(), mothers.end()), mothers.end());
    return mothers;
  };

  std::vector<int> starts;
  for (const int mother : normalizedMothers(particleIndex)) {
    if (CarriesSignedHeavyConstituent(pdgAt(mother), flavour, requiredSign)) {
      starts.push_back(mother);
    }
  }
  if (starts.empty()) {
    return {Origin::kUnresolved, -1, -1,
            MatchResolution::kMissingCarrier};
  }

  std::deque<std::pair<int, int>> queue;
  std::set<int> visited;
  for (const int start : starts) queue.push_back({start, 0});
  int foundDepth = -1;
  std::vector<int> candidates;
  while (!queue.empty()) {
    const auto [index, depth] = queue.front();
    queue.pop_front();
    if (foundDepth >= 0 && depth > foundDepth) break;
    if (!visited.insert(index).second) continue;
    const int pdg = pdgAt(index);
    if (std::abs(pdg) == flavour &&
        (pdg > 0 ? 1 : -1) == requiredSign) {
      foundDepth = depth;
      candidates.push_back(index);
      continue;
    }
    for (const int mother : normalizedMothers(index)) {
      if (CarriesSignedHeavyConstituent(pdgAt(mother), flavour,
                                       requiredSign)) {
        queue.push_back({mother, depth + 1});
      }
    }
  }

  int totalDepth = 1;
  std::set<int> lineageVisited;
  while (candidates.size() == 1U && totalDepth < 1000) {
    const int index = candidates.front();
    if (!lineageVisited.insert(index).second) {
      return {Origin::kUnresolved, -1, totalDepth,
              MatchResolution::kBrokenLineage};
    }
    if (isSelectedHardRoot(index, requiredSign * flavour)) {
      return {Origin::kSelectedHard, index, totalDepth,
              MatchResolution::kUnique};
    }

    candidates.clear();
    for (const int mother : normalizedMothers(index)) {
      const int parentPdg = pdgAt(mother);
      if (std::abs(parentPdg) == flavour &&
          (parentPdg > 0 ? 1 : -1) == requiredSign) {
        candidates.push_back(mother);
      }
    }
    std::sort(candidates.begin(), candidates.end());
    candidates.erase(std::unique(candidates.begin(), candidates.end()),
                     candidates.end());
    if (candidates.empty()) {
      const int sourceStatus = std::abs(statusAt(index));
      if (sourceStatus >= 31 && sourceStatus <= 39) {
        return {Origin::kMPI, -1, totalDepth, MatchResolution::kUnique};
      }
      if (sourceStatus >= 41 && sourceStatus <= 59) {
        return {Origin::kShower, -1, totalDepth,
                MatchResolution::kUnique};
      }
      return {Origin::kOtherResolved, -1, totalDepth,
              MatchResolution::kUnique};
    }
    ++totalDepth;
  }

  return {Origin::kUnresolved, -1, totalDepth,
          candidates.size() > 1U ? MatchResolution::kAmbiguous
                                 : MatchResolution::kBrokenLineage};
}

enum class HeavyStateCategory : int {
  kCentralGround = 0,
  kHiddenHeavy = 1,
  kMultiplyHeavy = 2,
  kOtherNoncentral = 3,
  kExcludedVector = 4,
  kExcludedExcited = 5
};

struct CarrierUniquenessResult {
  std::uint64_t conflictGroups = 0;
  std::uint64_t demotedMatches = 0;
};

// A selected hard quark can be incorporated into at most one final open-heavy
// hadron. PYTHIA may assign the same fragmenting string/junction mother range
// to several final hadrons; independent ancestry walks can then appear unique
// while claiming the same carrier. Such assignments are not distinguishable
// from the event record and must all be marked unresolved rather than choosing
// one hadron arbitrarily.
inline CarrierUniquenessResult EnforceUniqueFinalHardCarrier(
    const std::vector<int>& isFinal, const std::vector<int>& sectorCharge,
    std::vector<int>& origin, std::vector<int>& resolution,
    std::vector<int>& matchedHard) {
  const std::size_t size = isFinal.size();
  if (sectorCharge.size() != size || origin.size() != size ||
      resolution.size() != size || matchedHard.size() != size) {
    throw std::invalid_argument(
        "hard-carrier uniqueness vectors have inconsistent sizes");
  }

  std::map<int, std::vector<std::size_t>> claims;
  for (std::size_t index = 0; index < size; ++index) {
    if (!isFinal[index] || sectorCharge[index] == 0 ||
        origin[index] != static_cast<int>(Origin::kSelectedHard) ||
        matchedHard[index] < 0) {
      continue;
    }
    claims[matchedHard[index]].push_back(index);
  }

  CarrierUniquenessResult result;
  for (const auto& [hardIndex, indices] : claims) {
    (void)hardIndex;
    if (indices.size() < 2) continue;
    ++result.conflictGroups;
    result.demotedMatches += indices.size();
    for (const std::size_t index : indices) {
      origin[index] = static_cast<int>(Origin::kUnresolved);
      resolution[index] =
          static_cast<int>(MatchResolution::kDuplicateHardCarrier);
      matchedHard[index] = -1;
    }
  }
  return result;
}

// The validation-only all-primary-heavy closure records one row for every
// c, cbar, b, or bbar constituent. Enforce carrier uniqueness between distinct
// final parent hadrons, not between indistinguishable constituent rows within
// one multiply-heavy parent. This does not alter Paul's central trigger
// definition. demotedMatches remains a constituent-row count.
inline CarrierUniquenessResult EnforceUniqueFinalConstituentHardCarrier(
    const std::vector<int>& parentSlot,
    const std::vector<int>& parentIsFinal,
    const std::vector<int>& signedConstituent,
    std::vector<int>& origin, std::vector<int>& resolution,
    std::vector<int>& matchedHard, std::vector<int>& rejectedHard) {
  const std::size_t size = parentSlot.size();
  if (parentIsFinal.size() != size || signedConstituent.size() != size ||
      origin.size() != size || resolution.size() != size ||
      matchedHard.size() != size || rejectedHard.size() != size) {
    throw std::invalid_argument(
        "constituent hard-carrier uniqueness vectors have inconsistent sizes");
  }

  std::map<int, std::map<int, std::vector<std::size_t>>> claims;
  for (std::size_t index = 0; index < size; ++index) {
    if (!parentIsFinal[index] || signedConstituent[index] == 0 ||
        origin[index] != static_cast<int>(Origin::kSelectedHard) ||
        matchedHard[index] < 0) {
      continue;
    }
    if (parentSlot[index] < 0) {
      throw std::invalid_argument(
          "final constituent claim has an invalid parent slot");
    }
    claims[matchedHard[index]][parentSlot[index]].push_back(index);
  }

  CarrierUniquenessResult result;
  for (const auto& [hardIndex, claimsByParent] : claims) {
    (void)hardIndex;
    if (claimsByParent.size() < 2) continue;
    ++result.conflictGroups;
    for (const auto& [parent, indices] : claimsByParent) {
      (void)parent;
      result.demotedMatches += indices.size();
      for (const std::size_t index : indices) {
        rejectedHard[index] = matchedHard[index];
        origin[index] = static_cast<int>(Origin::kUnresolved);
        resolution[index] =
            static_cast<int>(MatchResolution::kDuplicateHardCarrier);
        matchedHard[index] = -1;
      }
    }
  }
  return result;
}

// A single matched-hard index cannot represent an open-heavy hadron carrying
// more than one same-sign quark from the same heavy-flavour sector. Apply this
// only after EnforceUniqueFinalHardCarrier. Duplicate-carrier conflicts retain
// their more specific resolution, while every other final multi-heavy claim is
// conservatively made unresolved. rejectedHard preserves any candidate that
// was rejected so the raw validator can audit the decision exactly.
inline std::uint64_t RejectFinalMultiHeavyCarrier(
    const std::vector<int>& isFinal, const std::vector<int>& sectorCharge,
    std::vector<int>& origin, std::vector<int>& resolution,
    std::vector<int>& matchedHard, std::vector<int>& rejectedHard) {
  const std::size_t size = isFinal.size();
  if (sectorCharge.size() != size || origin.size() != size ||
      resolution.size() != size || matchedHard.size() != size ||
      rejectedHard.size() != size) {
    throw std::invalid_argument(
        "multi-heavy rejection vectors have inconsistent sizes");
  }

  std::uint64_t rejected = 0;
  for (std::size_t index = 0; index < size; ++index) {
    if (!isFinal[index] || std::abs(sectorCharge[index]) <= 1) continue;
    ++rejected;
    if (resolution[index] ==
        static_cast<int>(MatchResolution::kDuplicateHardCarrier)) {
      // The uniqueness pass already cleared matchedHard and stored the
      // rejected candidate. Retain that auditable, more specific reason.
      origin[index] = static_cast<int>(Origin::kUnresolved);
      matchedHard[index] = -1;
      continue;
    }
    if (matchedHard[index] >= 0) rejectedHard[index] = matchedHard[index];
    origin[index] = static_cast<int>(Origin::kUnresolved);
    resolution[index] =
        static_cast<int>(MatchResolution::kMultipleHeavyConstituents);
    matchedHard[index] = -1;
  }
  return rejected;
}

struct HeavyContent {
  int nc = 0;
  int ncbar = 0;
  int nb = 0;
  int nbbar = 0;
  int ns = 0;
  int nsbar = 0;

  int qc() const { return nc - ncbar; }
  int qb() const { return nb - nbbar; }
  int strangeness() const { return nsbar - ns; }
  bool hasCharm() const { return nc + ncbar > 0; }
  bool hasBeauty() const { return nb + nbbar > 0; }
  bool hiddenCharm() const { return nc > 0 && ncbar > 0; }
  bool hiddenBeauty() const { return nb > 0 && nbbar > 0; }
};

inline HeavyStateCategory ClassifyHeavyState(bool central,
                                             const HeavyContent& content) {
  if (central) return HeavyStateCategory::kCentralGround;
  if (content.hiddenCharm() || content.hiddenBeauty()) {
    return HeavyStateCategory::kHiddenHeavy;
  }
  if (std::abs(content.qc()) > 1 || std::abs(content.qb()) > 1) {
    return HeavyStateCategory::kMultiplyHeavy;
  }
  return HeavyStateCategory::kOtherNoncentral;
}

inline HeavyStateCategory ClassifyHeavyStateDetailed(
    bool central, const HeavyContent& content, bool isMeson, int spinType) {
  const HeavyStateCategory broad = ClassifyHeavyState(central, content);
  if (broad != HeavyStateCategory::kOtherNoncentral) return broad;
  if (isMeson && spinType == 3) {
    return HeavyStateCategory::kExcludedVector;
  }
  if (content.hasCharm() || content.hasBeauty()) {
    return HeavyStateCategory::kExcludedExcited;
  }
  return HeavyStateCategory::kOtherNoncentral;
}

inline int ParseBoundedInt(const char* text, const char* name, int minimum,
                           int maximum) {
  std::size_t consumed = 0;
  const std::string value = text ? text : "";
  long long parsed = 0;
  try {
    parsed = std::stoll(value, &consumed);
  } catch (const std::exception&) {
    throw std::invalid_argument(std::string(name) + " is not an integer");
  }
  if (consumed != value.size() || parsed < minimum || parsed > maximum) {
    throw std::out_of_range(std::string(name) + " is outside [" +
                            std::to_string(minimum) + "," +
                            std::to_string(maximum) + "]");
  }
  return static_cast<int>(parsed);
}

inline int TuneOrdinal(const std::string& tune) {
  if (tune == "MONASH" || tune == "monash") return 0;
  if (tune == "JUNCTIONS" || tune == "junctions") return 1;
  if (tune == "CLOSEPACKING" || tune == "closepacking") return 2;
  throw std::invalid_argument("unknown tune: " + tune);
}

// Collision-free bit layout for the supported production domain:
// [campaign:16][tune:2][logical:14][attempt:12][local-success:20].
inline std::uint64_t EventId(int campaignOrdinal, int tuneOrdinal,
                             int logicalId, int attempt,
                             std::uint64_t localSuccess) {
  if (campaignOrdinal < 0 || campaignOrdinal > 0xffff ||
      tuneOrdinal < 0 || tuneOrdinal > 3 ||
      logicalId < 0 || logicalId > 0x3fff ||
      attempt < 0 || attempt > 0xfff ||
      localSuccess >= (1ULL << 20)) {
    throw std::out_of_range("event-ID field exceeds declared bit allocation");
  }
  return (static_cast<std::uint64_t>(campaignOrdinal) << 48) |
         (static_cast<std::uint64_t>(tuneOrdinal) << 46) |
         (static_cast<std::uint64_t>(logicalId) << 32) |
         (static_cast<std::uint64_t>(attempt) << 20) | localSuccess;
}

inline void AddQuark(HeavyContent& content, int flavour, bool anti) {
  if (flavour == 3) anti ? ++content.nsbar : ++content.ns;
  if (flavour == 4) anti ? ++content.ncbar : ++content.nc;
  if (flavour == 5) anti ? ++content.nbbar : ++content.nb;
}

// Decode conventional PDG meson/baryon quark digits. PYTHIA's
// nQuarksInCode is separately used as a completeness guard in the producer.
inline HeavyContent DecodeHeavyContent(int pdg, bool isMeson, bool isBaryon) {
  HeavyContent content;
  const int id = std::abs(pdg);
  const bool antiParticle = pdg < 0;
  if (isMeson) {
    const int qHeavy = (id / 100) % 10;
    const int qLight = (id / 10) % 10;
    if (qHeavy == 0 || qLight == 0) return content;
    // PDG meson sign convention: for a positive code the larger-flavour
    // constituent is a quark when even and an antiquark when odd.
    const bool heavyIsAnti = (qHeavy % 2 != 0) ^ antiParticle;
    AddQuark(content, qHeavy, heavyIsAnti);
    AddQuark(content, qLight, !heavyIsAnti);
  } else if (isBaryon) {
    const std::array<int, 3> quarks{
        (id / 1000) % 10, (id / 100) % 10, (id / 10) % 10};
    for (const int quark : quarks) {
      if (quark != 0) AddQuark(content, quark, antiParticle);
    }
  }
  return content;
}

// PYTHIA ParticleData::baryonNumberType returns three times baryon number.
// Convert that API value to the exact integer B stored by the raw schema, and
// reject inconsistent meson/baryon or particle/antiparticle classifications.
inline bool DecodePythiaBaryonNumber(int signedPdg, bool isMeson,
                                     bool isBaryon, int baryonNumberType,
                                     int& baryonNumber) {
  baryonNumber = 0;
  if (signedPdg == 0 || isMeson == isBaryon) return false;
  if (isMeson) return baryonNumberType == 0;
  const int expected = signedPdg > 0 ? 3 : -3;
  if (baryonNumberType != expected) return false;
  baryonNumber = expected / 3;
  return true;
}

inline bool IsCentralKinematic(double pt, double eta, bool trigger) {
  return std::isfinite(pt) && std::isfinite(eta) &&
         pt > (trigger ? 1.0 : 0.15) && std::abs(eta) <= 4.0;
}

inline bool IsDirectPrimaryStatus(int status) {
  const int absolute = std::abs(status);
  return status > 0 && absolute >= 81 && absolute <= 89;
}

inline int MultiplicitySpeciesIndex(int absPdg) {
  switch (std::abs(absPdg)) {
    case 11:
      return 0;
    case 13:
      return 1;
    case 211:
      return 2;
    case 321:
      return 3;
    case 2212:
      return 4;
    default:
      return -1;
  }
}

inline bool IsMultiplicitySpecies(int absPdg) {
  return MultiplicitySpeciesIndex(absPdg) >= 0;
}

inline bool IsMultiplicityKinematic(double pt, double eta) {
  return std::isfinite(pt) && std::isfinite(eta) && pt > 0.15 &&
         std::abs(eta) <= 4.0;
}

inline bool CountsNchHadronisationV1(int pdg, int status, bool isFinal,
                                    double pt, double eta) {
  return isFinal && IsMultiplicitySpecies(std::abs(pdg)) &&
         IsDirectPrimaryStatus(status) && IsMultiplicityKinematic(pt, eta);
}

inline bool CountsNchFinalStrongEmV1(int pdg, bool isFinal, double pt,
                                    double eta,
                                    bool hasWeakDecayTransition) {
  return isFinal && IsMultiplicitySpecies(std::abs(pdg)) &&
         IsMultiplicityKinematic(pt, eta) && !hasWeakDecayTransition;
}

inline double WrapAbsolutePhi(double phi) {
  constexpr double pi = 3.14159265358979323846;
  return std::fmod(phi + 3.0 * pi, 2.0 * pi) - pi;
}

inline double WrapDeltaPhi(double triggerPhi, double associatePhi) {
  constexpr double pi = 3.14159265358979323846;
  return std::fmod(triggerPhi - associatePhi + 2.5 * pi, 2.0 * pi) -
         0.5 * pi;
}

inline bool IsKnownWeakParent(int absPdg) {
  // NCH_FINAL_STRONG_EM_V1 light-parent exclusions are generated from the
  // machine-readable weak-decay registry. Heavy parents are included below
  // even though the central production disables their decays.
  const int id = std::abs(absPdg);
  if (std::find(kWeakLightParentAbsPdgs.begin(),
                kWeakLightParentAbsPdgs.end(), id) !=
      kWeakLightParentAbsPdgs.end()) {
    return true;
  }
  // Conventional open-heavy PDG encodings contain a c/b quark digit.
  return ((id / 10) % 10 == 4 || (id / 100) % 10 == 4 ||
          (id / 1000) % 10 == 4 || (id / 10) % 10 == 5 ||
          (id / 100) % 10 == 5 || (id / 1000) % 10 == 5);
}

// PYTHIA 8 documents absolute statuses 91--97 as particles produced in
// decay processes. Status 99 is a Bose--Einstein momentum-shift copy and is
// deliberately excluded. The parent must also be a disappeared event-record
// entry; a positive parent with a decay-product child is not a valid
// transition under this operational rule.
inline bool IsWeakDecayTransitionV1(int parentPdg, int parentStatus,
                                    int childPdg, int childStatus) {
  if (std::abs(parentPdg) == std::abs(childPdg)) return false;
  const int childStatusAbs = std::abs(childStatus);
  return parentStatus < 0 &&
         childStatusAbs >= kWeakDecayProductStatusAbsMin &&
         childStatusAbs <= kWeakDecayProductStatusAbsMax &&
         IsKnownWeakParent(parentPdg);
}

// Traverse explicit mother edges and classify transitions, not ancestor
// species. Same-absolute-PDG copy/recoil/oscillation edges are followed but
// never by themselves imply a weak decay. pdgAt/statusAt return node values;
// mothersAt returns the explicit direct mothers of a node.
template <typename PdgAt, typename StatusAt, typename MothersAt>
inline bool HasWeakDecayTransitionV1(int particleIndex, int particleCount,
                                     PdgAt pdgAt, StatusAt statusAt,
                                     MothersAt mothersAt) {
  if (particleCount <= 0 || particleIndex < 0 ||
      particleIndex >= particleCount) {
    throw std::invalid_argument(
        "weak-transition ancestry start is outside the graph");
  }
  std::deque<std::pair<int, int>> queue;
  std::set<std::pair<int, int>> visitedEdges;
  const auto enqueueMothers = [&](int child) {
    for (const int parent : mothersAt(child)) {
      if (parent <= 0 || parent >= particleCount) {
        throw std::invalid_argument(
            "weak-transition ancestry contains an invalid mother index");
      }
      queue.emplace_back(parent, child);
    }
  };
  enqueueMothers(particleIndex);
  while (!queue.empty()) {
    const auto [parent, child] = queue.front();
    queue.pop_front();
    if (!visitedEdges.insert({parent, child}).second) continue;
    if (IsWeakDecayTransitionV1(pdgAt(parent), statusAt(parent),
                                pdgAt(child), statusAt(child))) {
      return true;
    }
    enqueueMothers(parent);
  }
  return false;
}

}  // namespace Hadronization
#endif
