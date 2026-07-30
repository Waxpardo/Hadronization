#ifndef HADRONIZATION_HEAVY_FLAVOUR_UTILS_H
#define HADRONIZATION_HEAVY_FLAVOUR_UTILS_H

#include <array>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <string>

namespace Hadronization {

inline constexpr const char* kRawSchema = "hf_primary_ground_raw_v3";
inline constexpr const char* kSelectorVersion =
    "hard_trigger_primary_ground__primary_ground_associate_v1";
inline constexpr const char* kOriginAlgorithmVersion =
    "signed_heavy_carrier_explicit_parent_v1";
inline constexpr const char* kMultiplicityCentral = "NCH_HADRONISATION_V1";
inline constexpr const char* kMultiplicityCrossCheck = "NCH_FINAL_STRONG_EM_V1";

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
  kBrokenLineage = 4
};

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
                                    double eta, bool hasWeakAncestor) {
  return isFinal && IsMultiplicitySpecies(std::abs(pdg)) &&
         IsMultiplicityKinematic(pt, eta) && !hasWeakAncestor;
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
  // Versioned NCH_FINAL_STRONG_EM_V1 exclusion list. Heavy parents are
  // included even though the central production disables their decays.
  switch (std::abs(absPdg)) {
    case 13:
    case 15:
    case 211:
    case 310:
    case 130:
    case 321:
    case 2112:
    case 3122:
    case 3112:
    case 3222:
    case 3312:
    case 3322:
    case 3334:
      return true;
    default:
      break;
  }
  // Conventional open-heavy PDG encodings contain a c/b quark digit.
  const int id = std::abs(absPdg);
  return ((id / 10) % 10 == 4 || (id / 100) % 10 == 4 ||
          (id / 1000) % 10 == 4 || (id / 10) % 10 == 5 ||
          (id / 100) % 10 == 5 || (id / 1000) % 10 == 5);
}

}  // namespace Hadronization
#endif
