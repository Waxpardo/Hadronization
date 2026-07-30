#ifndef HADRONIZATION_HEAVY_FLAVOUR_UTILS_H
#define HADRONIZATION_HEAVY_FLAVOUR_UTILS_H

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

inline constexpr const char* kRawSchema = "hf_primary_ground_raw_v7";
inline constexpr const char* kSelectorVersion =
    "hard_trigger_primary_ground__primary_ground_associate_v1";
inline constexpr const char* kOriginAlgorithmVersion =
    "signed_heavy_constituent_complete_mothers_unique_v4";
inline constexpr const char* kMultiplicityCentral =
    "NCH_PRIMARY_CHARGED_ETA10_V1";
inline constexpr const char* kMultiplicityCrossCheck =
    "NCH_PRIMARY_CHARGED_ETA40_V1";
inline constexpr const char* kMultiplicityDefinitionVersion =
    "primary_charged_light_hadron_level_v1";
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

// ---------------------------------------------------------------------------
// Charged-particle multiplicity, NCH_PRIMARY_CHARGED_*_V1.
//
// This is a genuine charged-particle multiplicity, not a count of directly
// produced hadronisation products. It is the hadron-level analogue of the
// conventional experimental primary-charged-particle definition: a charged
// particle with proper lifetime c*tau0 > 1 cm that is either produced
// directly in the collision or descends only from particles with
// c*tau0 < 1 cm.
//
// That lifetime condition is enforced at generation time, not here. All three
// tune cards set `ParticleDecays:limitTau0 = on` with `tau0Max = 0.01` mm, so
// every strong and electromagnetic decay proceeds while every weakly decaying
// light hadron stays final. No light hadron has 0.01 mm < c*tau0 < 10 mm, so
// for light flavour this card value is exactly equivalent to the conventional
// 1 cm/c threshold; `Validation/TestPrimaryChargedDefinition.C` asserts that
// equivalence against the installed PYTHIA ParticleData rather than trusting
// it. Consequently `isFinal()` already means "primary" for light hadrons and
// no ancestry traversal is required to exclude weak-decay products.
//
// Open- and hidden-heavy hadrons are excluded from the count. Their decays are
// disabled deliberately, so they are final here purely as an artefact of the
// production policy, and an experiment would instead count their decay
// daughters. Excluding them also removes the autocorrelation that would
// otherwise exist between the event-activity classifier and the heavy-flavour
// observable it classifies. The paper must state this exclusion.
// ---------------------------------------------------------------------------

inline constexpr double kMultiplicityPtMin = 0.15;
inline constexpr double kMultiplicityEtaCentral = 1.0;
inline constexpr double kMultiplicityEtaWide = 4.0;

// Diagnostic composition buckets. Index 5 collects every remaining charged
// species (predominantly Sigma+-, Xi-, Omega-), which the conventional
// primary definition includes and which a five-species list would silently
// drop.
inline constexpr int kMultiplicitySpeciesBuckets = 6;

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
      return 5;
  }
}

inline bool IsMultiplicityKinematic(double pt, double eta, double etaMax) {
  return std::isfinite(pt) && std::isfinite(eta) && pt > kMultiplicityPtMin &&
         std::abs(eta) <= etaMax;
}

// `isCharged` and `hasHeavyConstituent` come from the generator's
// ParticleData, so this stays free of any hand-rolled PDG decoding.
inline bool CountsNchPrimaryChargedV1(bool isFinal, bool isCharged,
                                      bool hasHeavyConstituent, double pt,
                                      double eta, double etaMax) {
  return isFinal && isCharged && !hasHeavyConstituent &&
         IsMultiplicityKinematic(pt, eta, etaMax);
}

// ---------------------------------------------------------------------------
// Light-hadron compensation grid (auxiliary, raw-v7).
//
// The central observable is heavy-flavour compensation. Electric charge and
// baryon number, however, are balanced predominantly by LIGHT hadrons, which
// the heavy-hadron collection does not store. Rather than serialise every
// light particle, the producer accumulates net electric charge and net baryon
// number of final light primaries on a fixed (eta, phi) grid. The grid is
// trigger-agnostic: any Delta-phi or Delta-eta profile relative to any trigger
// is recovered at analysis time by rotating/shifting cell indices, so no
// future trigger definition is foreclosed.
//
// This is auxiliary. It is NOT part of the central selector and must not be
// presented as a charge or baryon-number balance function without a dedicated
// analysis and its own validation.
// ---------------------------------------------------------------------------
inline constexpr int kLightGridPhiBins = 16;
inline constexpr int kLightGridEtaBins = 8;
inline constexpr double kLightGridEtaMax = 4.0;
inline constexpr int kLightGridCells =
    kLightGridPhiBins * kLightGridEtaBins;
inline constexpr const char* kLightCompensationGridSchema =
    "light_compensation_grid_v1";

// Returns the flat cell index, or -1 when outside the grid acceptance.
inline int LightGridCell(double eta, double phi) {
  constexpr double pi = 3.14159265358979323846;
  if (!std::isfinite(eta) || !std::isfinite(phi)) return -1;
  if (std::abs(eta) > kLightGridEtaMax) return -1;
  const double wrapped =
      std::fmod(phi + 3.0 * pi, 2.0 * pi) - pi;  // [-pi, pi)
  int phiBin = static_cast<int>(
      std::floor((wrapped + pi) / (2.0 * pi / kLightGridPhiBins)));
  if (phiBin < 0) phiBin = 0;
  if (phiBin >= kLightGridPhiBins) phiBin = kLightGridPhiBins - 1;
  int etaBin = static_cast<int>(std::floor(
      (eta + kLightGridEtaMax) /
      (2.0 * kLightGridEtaMax / kLightGridEtaBins)));
  if (etaBin < 0) etaBin = 0;
  if (etaBin >= kLightGridEtaBins) etaBin = kLightGridEtaBins - 1;
  return etaBin * kLightGridPhiBins + phiBin;
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

}  // namespace Hadronization
#endif
