// Canonical combined-heavy PYTHIA producer for the publication analysis.
//
// Usage:
//   heavyflavourcorrelations_status MODE OUTPUT SEED CAMPAIGN
//       CAMPAIGN_ORDINAL LOGICAL_ID ROLE ATTEMPT
//
// MODE is monash, junctions, or closepacking. SEED is passed to PYTHIA
// unchanged and must be allocated by the immutable campaign seed ledger.

#include "physics.hpp"
#include "selected_states.hpp"
#include "sha256.hpp"
#include "tune_settings.hpp"

#include "Pythia8/Pythia.h"

#include "TFile.h"
#include "TH1D.h"
#include "TH1I.h"
#include "TObjString.h"
#include "TParameter.h"
#include "TROOT.h"
#include "TString.h"
#include "TTree.h"

#include <algorithm>
#include <array>
#include <cctype>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <exception>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <sys/resource.h>
#include <vector>

using namespace Pythia8;
using namespace Hadronization;

namespace {

struct StabilityRow {
  int pdg = 0;
  std::string name;
  int isHadron = 0;
  int isMeson = 0;
  int isBaryon = 0;
  int spinType = 0;
  int charge3 = 0;
  int nCharm = 0;
  int nBeauty = 0;
  int nc = 0;
  int ncbar = 0;
  int nb = 0;
  int nbbar = 0;
  int qc = 0;
  int qb = 0;
  int strangeness = 0;
  int openHeavy = 0;
  int hiddenHeavy = 0;
  int central = 0;
  int hasAnti = 0;
  int antiparticleVerified = 0;
  double mass = 0.0;
  double tau0 = 0.0;
  int canDecay = 0;
  int originalMayDecay = 0;
  int finalMayDecay = 0;
};

struct HardParton {
  int rootIndex = -1;
  int bottomIndex = -1;
  int id = 0;
};

using OriginMatch = HeavyOriginMatch;

std::string GetEnv(const char* name, const std::string& fallback = "") {
  const char* value = std::getenv(name);
  return value ? value : fallback;
}

ULong64_t PeakRssKiB() {
  struct rusage usage {};
  if (getrusage(RUSAGE_SELF, &usage) != 0 || usage.ru_maxrss <= 0) {
    throw std::runtime_error("getrusage returned no positive peak RSS");
  }
#if defined(__APPLE__)
  // Darwin reports ru_maxrss in bytes.
  return static_cast<ULong64_t>(
      (static_cast<unsigned long long>(usage.ru_maxrss) + 1023ULL) /
      1024ULL);
#elif defined(__linux__) || defined(__FreeBSD__) || defined(__NetBSD__) || \
    defined(__OpenBSD__)
  // Linux and the BSDs report ru_maxrss in KiB.
  return static_cast<ULong64_t>(usage.ru_maxrss);
#else
#error "Define the ru_maxrss unit conversion for this target platform"
#endif
}

// The three published tunes. The published JUNCTIONS tune retunes StringZ,
// StringFlav and pT0Ref away from Monash, and those settings govern baryon
// production, so a MONASH-vs-JUNCTIONS difference in a baryon observable cannot
// be attributed to junction formation on its own. Ruling R32 of 2026-08-30
// states that limit in the paper rather than isolating it with a fourth,
// matched configuration.
//
// Adding a configuration means one entry here and one card. There is
// deliberately no fixed-width tune ordinal anywhere in the pipeline.
const std::vector<std::string>& KnownTunes() {
  static const std::vector<std::string> tunes = {
      "MONASH", "JUNCTIONS", "CLOSEPACKING"};
  return tunes;
}

std::string CanonicalTune(const std::string& mode) {
  std::string upper;
  upper.reserve(mode.size());
  for (const char character : mode) {
    upper.push_back(static_cast<char>(
        std::toupper(static_cast<unsigned char>(character))));
  }
  for (const std::string& tune : KnownTunes()) {
    if (tune == upper) return tune;
  }
  return "";
}

std::string ResolveSettingsFile(const std::string& mode) {
  const std::string tune = CanonicalTune(mode);
  if (tune.empty()) return "";
  if (tune == "MONASH") return "monash.cmnd";
  if (tune == "JUNCTIONS") return "junctions.cmnd";
  return "close_packing.cmnd";
}

std::vector<int> ExplicitMotherIndices(const Event& event, int particleIndex) {
  std::vector<int> result = event[particleIndex].motherList();
  // Some junction/string-fragmentation statuses encode a physically relevant
  // heavy-line continuation in mother1/mother2 that is not returned by
  // motherList(). Keep both explicit endpoints as well as PYTHIA's expanded
  // interpretation, then deduplicate before traversing.
  result.push_back(event[particleIndex].mother1());
  result.push_back(event[particleIndex].mother2());
  result.erase(std::remove_if(result.begin(), result.end(),
                              [&event](int index) {
                                return index <= 0 || index >= event.size();
                              }),
               result.end());
  std::sort(result.begin(), result.end());
  result.erase(std::unique(result.begin(), result.end()), result.end());
  return result;
}

std::vector<HardParton> FindHardPartons(const Event& event) {
  std::vector<HardParton> result;
  for (int index = 0; index < event.size(); ++index) {
    const Particle& particle = event[index];
    if (particle.statusAbs() != 23 ||
        (std::abs(particle.id()) != 4 && std::abs(particle.id()) != 5)) {
      continue;
    }
    const int bottom = particle.iBotCopy();
    result.push_back({index, bottom, particle.id()});
  }
  return result;
}

bool IsExactSignedHardPair(const Event& event,
                           const std::vector<HardParton>& hardPartons) {
  if (hardPartons.size() != 2U) return false;
  const int flavour = std::abs(hardPartons.front().id);
  if ((flavour != 4 && flavour != 5) ||
      hardPartons[0].id != -hardPartons[1].id) {
    return false;
  }
  std::set<int> roots;
  for (const auto& hard : hardPartons) {
    if (hard.rootIndex <= 0 || hard.rootIndex >= event.size() ||
        hard.bottomIndex <= 0 || hard.bottomIndex >= event.size() ||
        event[hard.rootIndex].statusAbs() != 23 ||
        event[hard.rootIndex].id() != hard.id ||
        event[hard.rootIndex].iBotCopy() != hard.bottomIndex ||
        !roots.insert(hard.rootIndex).second) {
      return false;
    }
  }
  return true;
}

OriginMatch MatchOrigin(const Event& event, int particleIndex, int flavour,
                        int requiredSign,
                        const std::vector<HardParton>& hardPartons) {
  return MatchHeavyOriginGraph(
      particleIndex, event.size(), flavour, requiredSign,
      [&event](int index) { return event[index].id(); },
      [&event](int index) { return event[index].status(); },
      [&event](int index) {
        return ExplicitMotherIndices(event, index);
      },
      [&hardPartons](int index, int signedFlavour) {
        return std::any_of(
            hardPartons.begin(), hardPartons.end(),
            [index, signedFlavour](const HardParton& hard) {
              return hard.rootIndex == index && hard.id == signedFlavour;
            });
      });
}

void CollectOriginAuditNodes(const Event& event, int particleIndex, int flavour,
                             int requiredSign, std::set<int>& nodes) {
  if (requiredSign == 0) return;
  std::deque<int> queue;
  for (const int mother : ExplicitMotherIndices(event, particleIndex)) {
    nodes.insert(mother);
    if (CarriesSignedHeavyConstituent(event[mother].id(), flavour,
                                     requiredSign)) {
      queue.push_back(mother);
    }
  }
  std::set<int> expanded;
  while (!queue.empty()) {
    const int index = queue.front();
    queue.pop_front();
    if (!expanded.insert(index).second) continue;
    for (const int mother : ExplicitMotherIndices(event, index)) {
      nodes.insert(mother);
      if (CarriesSignedHeavyConstituent(event[mother].id(), flavour,
                                       requiredSign)) {
        queue.push_back(mother);
      }
    }
  }
}

std::string CaptureChangedSettings(Pythia& pythia) {
  std::ostringstream capture;
  std::streambuf* previous = std::cout.rdbuf(capture.rdbuf());
  pythia.settings.listChanged();
  std::cout.rdbuf(previous);
  return capture.str();
}

std::string CaptureStatistics(Pythia& pythia) {
  std::ostringstream capture;
  std::streambuf* previous = std::cout.rdbuf(capture.rdbuf());
  pythia.stat();
  std::cout.rdbuf(previous);
  return capture.str();
}

bool IsKnownSetting(Settings& settings, const std::string& key) {
  return settings.isFlag(key) || settings.isMode(key) ||
         settings.isParm(key) || settings.isWord(key) ||
         settings.isFVec(key) || settings.isMVec(key) ||
         settings.isPVec(key) || settings.isWVec(key);
}

std::vector<std::string> CardSettingKeys(const std::string& settingsFile) {
  std::vector<std::string> keys;
  std::ifstream stream(settingsFile);
  if (!stream) {
    throw std::runtime_error("cannot reopen settings file for audit");
  }
  std::string line;
  while (std::getline(stream, line)) {
    const std::size_t comment = line.find('!');
    if (comment != std::string::npos) line.erase(comment);
    const std::size_t equals = line.find('=');
    if (equals == std::string::npos) continue;
    std::string key = line.substr(0, equals);
    const std::size_t first = key.find_first_not_of(" \t\r\n");
    const std::size_t last = key.find_last_not_of(" \t\r\n");
    if (first == std::string::npos) continue;
    keys.push_back(key.substr(first, last - first + 1));
  }
  std::sort(keys.begin(), keys.end());
  keys.erase(std::unique(keys.begin(), keys.end()), keys.end());
  return keys;
}

std::vector<std::string> AuditedSettingKeys(
    Settings& settings, const std::string& settingsFile) {
  const std::vector<std::string> configured = CardSettingKeys(settingsFile);
  std::set<std::string> declared;
  std::vector<std::string> audited;
  audited.reserve(kAuditedPythiaSettingKeys.size());
  for (const std::string_view key : kAuditedPythiaSettingKeys) {
    const std::string value(key);
    if (!declared.insert(value).second || !IsKnownSetting(settings, value)) {
      throw std::runtime_error(
          "unknown or duplicate setting in generated tune audit: " + value);
    }
    audited.push_back(value);
  }
  for (const auto& key : configured) {
    if (!IsKnownSetting(settings, key)) {
      throw std::runtime_error(
          "unknown or misspelled setting in PYTHIA card: " + key);
    }
    if (declared.count(key) == 0) {
      throw std::runtime_error(
          "configured setting is absent from tune allowlist: " + key);
    }
  }
  return audited;
}

std::vector<std::pair<std::string, std::string>> EffectiveSettingRows(
    Pythia& pythia) {
  std::map<std::string, std::string> values;
  const auto append = [&](const auto& entries) {
    for (const auto& [normalizedName, entry] : entries) {
      (void)normalizedName;
      if (entry.name.empty() ||
          !values
               .emplace(entry.name,
                        pythia.settings.output(entry.name, false))
               .second) {
        throw std::runtime_error(
            "duplicate/empty name in exhaustive post-init settings");
      }
    }
  };
  append(pythia.settings.getFlagMap(""));
  append(pythia.settings.getModeMap(""));
  append(pythia.settings.getParmMap(""));
  append(pythia.settings.getWordMap(""));
  append(pythia.settings.getFVecMap(""));
  append(pythia.settings.getMVecMap(""));
  append(pythia.settings.getPVecMap(""));
  append(pythia.settings.getWVecMap(""));
  if (values.empty()) {
    throw std::runtime_error("exhaustive post-init settings snapshot is empty");
  }
  return {values.begin(), values.end()};
}

std::string SerializeEffectiveSettings(
    const std::vector<std::pair<std::string, std::string>>& rows) {
  std::ostringstream stream;
  stream.imbue(std::locale::classic());
  stream << "schema=" << kEffectiveSettingsSchema << "\n";
  for (const auto& [name, value] : rows) {
    stream << std::quoted(name) << '\t' << std::quoted(value) << '\n';
  }
  return stream.str();
}

std::vector<StabilityRow> StabilizeHeavyHadrons(Pythia& pythia) {
  std::vector<StabilityRow> rows;
  std::vector<int> heavyIds;
  for (auto iterator = pythia.particleData.begin();
       iterator != pythia.particleData.end(); ++iterator) {
    const auto& entry = iterator->second;
    const int id = iterator->first;
    if (!entry->isHadron()) continue;
    const int nCharm = entry->nQuarksInCode(4);
    const int nBeauty = entry->nQuarksInCode(5);
    if (nCharm == 0 && nBeauty == 0) continue;
    heavyIds.push_back(id);
    const bool original = entry->mayDecay();
    pythia.particleData.mayDecay(id, false);
    const std::vector<int> signs =
        entry->hasAnti() ? std::vector<int>{id, -id} : std::vector<int>{id};
    for (const int signedId : signs) {
      const HeavyContent content = DecodeHeavyContent(
          signedId, entry->isMeson(), entry->isBaryon());
      StabilityRow row;
      row.pdg = signedId;
      row.name = pythia.particleData.name(signedId);
      row.isHadron = 1;
      row.isMeson = entry->isMeson() ? 1 : 0;
      row.isBaryon = entry->isBaryon() ? 1 : 0;
      row.spinType = entry->spinType();
      row.charge3 = entry->chargeType(signedId);
      row.nCharm = nCharm;
      row.nBeauty = nBeauty;
      row.nc = content.nc;
      row.ncbar = content.ncbar;
      row.nb = content.nb;
      row.nbbar = content.nbbar;
      row.qc = content.qc();
      row.qb = content.qb();
      row.strangeness = content.strangeness();
      row.openHeavy = (content.qc() != 0 || content.qb() != 0) ? 1 : 0;
      row.hiddenHeavy =
          (content.hiddenCharm() || content.hiddenBeauty()) ? 1 : 0;
      row.central = FindSelectedState(signedId) ? 1 : 0;
      row.hasAnti = entry->hasAnti() ? 1 : 0;
      row.antiparticleVerified =
          (!entry->hasAnti() ||
           (pythia.particleData.isHadron(-signedId) &&
            pythia.particleData.nQuarksInCode(-signedId, 4) == nCharm &&
            pythia.particleData.nQuarksInCode(-signedId, 5) == nBeauty))
              ? 1
              : 0;
      row.mass = entry->m0();
      row.tau0 = entry->tau0();
      row.canDecay = entry->canDecay() ? 1 : 0;
      row.originalMayDecay = original ? 1 : 0;
      row.finalMayDecay = 0;
      rows.push_back(row);
    }
  }
  for (const int id : heavyIds) {
    if (pythia.particleData.mayDecay(id)) {
      throw std::runtime_error("heavy hadron remained decay-enabled: " +
                               std::to_string(id));
    }
  }
  std::sort(rows.begin(), rows.end(),
            [](const StabilityRow& left, const StabilityRow& right) {
              if (left.pdg != right.pdg) return left.pdg < right.pdg;
              return left.name < right.name;
            });
  return rows;
}

void VerifyPostInitHeavyStability(Pythia& pythia,
                                  std::vector<StabilityRow>& rows) {
  for (auto& row : rows) {
    row.finalMayDecay =
        pythia.particleData.mayDecay(row.pdg) ? 1 : 0;
    if (row.finalMayDecay != 0) {
      throw std::runtime_error(
          "post-init heavy hadron remained decay-enabled: " +
          std::to_string(row.pdg));
    }
  }
}

std::string SerializeStabilityAudit(const std::vector<StabilityRow>& rows) {
  std::ostringstream stream;
  stream.imbue(std::locale::classic());
  stream << "schema=" << kHeavyStabilityAuditSchema << "\n";
  stream << std::scientific << std::setprecision(17);
  for (const auto& row : rows) {
    stream << row.pdg << '\t' << std::quoted(row.name) << '\t'
           << row.isHadron << '\t' << row.isMeson << '\t' << row.isBaryon
           << '\t' << row.spinType << '\t' << row.charge3 << '\t'
           << row.nCharm << '\t' << row.nBeauty << '\t' << row.nc << '\t'
           << row.ncbar << '\t' << row.nb << '\t' << row.nbbar << '\t'
           << row.qc << '\t' << row.qb << '\t' << row.strangeness << '\t'
           << row.openHeavy << '\t' << row.hiddenHeavy << '\t'
           << row.central << '\t' << row.hasAnti << '\t'
           << row.antiparticleVerified << '\t' << row.mass << '\t'
           << row.tau0 << '\t' << row.canDecay << '\t'
           << row.originalMayDecay << '\t' << row.finalMayDecay << '\n';
  }
  return stream.str();
}

int HardChannel(const std::vector<HardParton>& hardPartons) {
  bool charm = false;
  bool beauty = false;
  for (const auto& hard : hardPartons) {
    charm = charm || std::abs(hard.id) == 4;
    beauty = beauty || std::abs(hard.id) == 5;
  }
  return charm && !beauty ? 4 : (beauty && !charm ? 5 : (charm && beauty ? 45 : 0));
}

}  // namespace

int main(int argc, char** argv) {
  const auto wallStart = std::chrono::system_clock::now();
  if (argc != 9) {
    std::cerr
        << "Usage: " << argv[0]
        << " MODE OUTPUT SEED CAMPAIGN CAMPAIGN_ORDINAL LOGICAL_ID ROLE ATTEMPT\n";
    return 2;
  }

  const std::string mode = argv[1];
  const std::string tune = CanonicalTune(mode);
  const std::string settingsFile = ResolveSettingsFile(mode);
  const std::string outputName = argv[2];
  const std::string campaign = argv[4];
  const std::string role = argv[7];
  if (settingsFile.empty()) {
    std::cerr << "ERROR: unknown mode '" << mode << "'\n";
    return 2;
  }

  int seed = 0;
  int campaignOrdinal = 0;
  int logicalId = 0;
  int attempt = 0;
  try {
    seed = ParseBoundedInt(argv[3], "seed", 1, 900000000);
    campaignOrdinal =
        ParseBoundedInt(argv[5], "campaign ordinal", 1, 65535);
    logicalId = ParseBoundedInt(argv[6], "logical ID", 0, 16383);
    attempt = ParseBoundedInt(argv[8], "attempt", 0, 4095);
  } catch (const std::exception& error) {
    std::cerr << "ERROR: " << error.what() << "\n";
    return 2;
  }
  if (role != "primary" && role != "reserve" && role != "pilot") {
    std::cerr << "ERROR: ROLE must be primary, reserve, or pilot\n";
    return 2;
  }

  Pythia pythia;
  if (!pythia.readFile(settingsFile) || pythia.settings.readingFailed()) {
    std::cerr << "ERROR: could not read PYTHIA card " << settingsFile << "\n";
    return 3;
  }
  if (!pythia.readString("Random:setSeed = on") ||
      !pythia.readString("Random:seed = " + std::to_string(seed)) ||
      pythia.settings.readingFailed()) {
    std::cerr << "ERROR: could not apply deterministic seed settings\n";
    return 3;
  }
  std::vector<std::string> configuredSettingKeys;
  try {
    configuredSettingKeys =
        AuditedSettingKeys(pythia.settings, settingsFile);
  } catch (const std::exception& error) {
    std::cerr << "ERROR: tune-setting audit setup failed: " << error.what()
              << "\n";
    return 3;
  }

  std::vector<StabilityRow> stabilityRows;
  try {
    stabilityRows = StabilizeHeavyHadrons(pythia);
  } catch (const std::exception& error) {
    std::cerr << "ERROR: heavy-stability setup failed: " << error.what() << "\n";
    return 3;
  }

  if (!pythia.init()) {
    std::cerr << "ERROR: PYTHIA initialization failed\n";
    return 3;
  }
  try {
    VerifyPostInitHeavyStability(pythia, stabilityRows);
  } catch (const std::exception& error) {
    std::cerr << "ERROR: post-init heavy-stability audit failed: "
              << error.what() << "\n";
    return 3;
  }
  const std::string effectiveSettings = CaptureChangedSettings(pythia);
  const auto effectiveSettingRows = EffectiveSettingRows(pythia);
  {
    std::set<std::string> exhaustiveNames;
    for (const auto& [name, value] : effectiveSettingRows) {
      (void)value;
      exhaustiveNames.insert(name);
    }
    for (const auto& configured : configuredSettingKeys) {
      if (exhaustiveNames.count(configured) == 0U) {
        std::cerr << "ERROR: configured setting is absent from exhaustive "
                     "post-init snapshot: "
                  << configured << "\n";
        return 3;
      }
    }
  }
  const std::string effectiveSettingsCanonical =
      SerializeEffectiveSettings(effectiveSettingRows);
  const std::string effectiveSettingsSha256 =
      Sha256Hex(effectiveSettingsCanonical);
  const double phaseSpacePthatMin = pythia.parm("PhaseSpace:pTHatMin");
  const std::uint64_t requestedSuccesses =
      static_cast<std::uint64_t>(pythia.mode("Main:numberOfEvents"));
  if (requestedSuccesses == 0 || requestedSuccesses >= (1ULL << 20)) {
    std::cerr << "ERROR: requested successes must be in [1,1048575]\n";
    return 3;
  }
  const std::uint64_t ceilingFactor = static_cast<std::uint64_t>(
      ParseBoundedInt(GetEnv("HADRONIZATION_ATTEMPT_CEILING_FACTOR", "10").c_str(),
                      "attempt ceiling factor", 1, 1000));
  const std::uint64_t attemptCeiling = requestedSuccesses * ceilingFactor;
  std::uint64_t forcedFailures = 0;
  std::uint64_t abortAfterAttempts = 0;
  std::uint64_t multiplicityAuditEvents = 0;
  if (!GetEnv("HADRONIZATION_FORCE_FAILURES").empty() ||
      !GetEnv("HADRONIZATION_ABORT_AFTER_ATTEMPTS").empty()) {
    if (role != "pilot") {
      std::cerr << "ERROR: failure injection is restricted to pilot jobs\n";
      return 3;
    }
    forcedFailures = static_cast<std::uint64_t>(ParseBoundedInt(
        GetEnv("HADRONIZATION_FORCE_FAILURES", "0").c_str(),
        "HADRONIZATION_FORCE_FAILURES", 0,
        static_cast<int>(std::min<std::uint64_t>(
            attemptCeiling, static_cast<std::uint64_t>(
                                std::numeric_limits<int>::max())))));
    abortAfterAttempts = static_cast<std::uint64_t>(ParseBoundedInt(
        GetEnv("HADRONIZATION_ABORT_AFTER_ATTEMPTS", "0").c_str(),
        "HADRONIZATION_ABORT_AFTER_ATTEMPTS", 0,
        static_cast<int>(std::min<std::uint64_t>(
            attemptCeiling, static_cast<std::uint64_t>(
                                std::numeric_limits<int>::max())))));
  }
  if (!GetEnv("HADRONIZATION_STORE_MULTIPLICITY_AUDIT_EVENTS").empty()) {
    if (role != "pilot") {
      std::cerr << "ERROR: full multiplicity audit records are pilot-only\n";
      return 3;
    }
    multiplicityAuditEvents =
        static_cast<std::uint64_t>(ParseBoundedInt(
            GetEnv("HADRONIZATION_STORE_MULTIPLICITY_AUDIT_EVENTS").c_str(),
            "HADRONIZATION_STORE_MULTIPLICITY_AUDIT_EVENTS", 0,
            static_cast<int>(requestedSuccesses)));
  }
  int debugLocalEvent = -1;
  if (!GetEnv("HADRONIZATION_DEBUG_LOCAL_EVENT").empty()) {
    debugLocalEvent = ParseBoundedInt(
        GetEnv("HADRONIZATION_DEBUG_LOCAL_EVENT").c_str(),
        "HADRONIZATION_DEBUG_LOCAL_EVENT", 0,
        static_cast<int>(requestedSuccesses - 1));
  }

  TFile output(outputName.c_str(), "CREATE");
  if (output.IsZombie()) {
    std::cerr << "ERROR: could not create unique output " << outputName << "\n";
    return 4;
  }

  TTree tree("tree", "canonical stable-heavy combined charm+beauty events");
  ULong64_t eventId = 0;
  Int_t processCode = 0;
  Int_t hardChannel = 0;
  Double_t eventWeight = 0.0;
  Double_t pTHat = 0.0;
  Double_t hardScale = 0.0;
  Int_t nMPI = 0;
  Int_t multiplicityCentral = 0;
  Int_t multiplicityWide = 0;
  Int_t nCharmOnly = 0;
  Int_t nBeautyOnly = 0;
  Int_t nBc = 0;
  Int_t finalHeavyQcSum = 0;
  Int_t finalHeavyQbSum = 0;
  Int_t heavyFlavourConservationOk = 0;
  Int_t originClassificationValid = 0;
  Int_t primaryAllHeavyMatchValid = 0;
  Int_t multiplicityCentralBySpecies[kMultiplicitySpeciesBuckets] = {
      0, 0, 0, 0, 0, 0};
  // Auxiliary light-hadron compensation grid (raw-v7). Net charge is summed in
  // units of e/3 to stay exactly integral.
  Short_t lightCharge3Grid[kLightGridCells] = {0};
  Short_t lightBaryonGrid[kLightGridCells] = {0};

  std::vector<int> hardIndices;
  std::vector<int> hardBottomIndices;
  std::vector<int> hardIds, hardStatus, hardBottomIds, hardBottomStatus;
  std::vector<double> hardPx, hardPy, hardPz, hardE;

  // Legacy reader branches. They now contain every recognized heavy hadron
  // over full phase space; the integer-rich branches below are authoritative.
  std::vector<int> legacyId;
  std::vector<int> legacyClass;
  std::vector<double> legacyPt, legacyEta, legacyY, legacyPhi, legacyCharge;
  // Raw-v5 never serializes discrete status/index values as floating point.
  // The upper-case names are retained only as a migration convenience for
  // schema-aware consumers; historical raw schemas keep their original
  // vector<double> representation in the explicitly labelled legacy reader.
  std::vector<int> legacyStatus, legacyMother, legacyMotherId;

  std::vector<int> heavyIndex, heavyPdg, heavyStatus, heavyStatusAbs;
  std::vector<int> heavyIsFinal, heavyIsMeson, heavyIsBaryon, heavyCharge3;
  std::vector<int> heavySpinType;
  std::vector<int> heavyMother1, heavyMother2, heavyDaughter1, heavyDaughter2;
  std::vector<int> heavyMotherOffsets, heavyMothers;
  std::vector<int> heavyNc, heavyNcbar, heavyNb, heavyNbbar, heavyQc, heavyQb;
  std::vector<int> heavyBaryonNumber, heavyStrangeness, heavyCentral;
  std::vector<int> heavyOpen, heavyHidden, heavyStateCategory;
  std::vector<int> heavyOriginC, heavyOriginB;
  std::vector<int> heavyMatchResolutionC, heavyMatchResolutionB;
  std::vector<int> heavyMatchedHardC, heavyMatchedHardB;
  std::vector<int> heavyRejectedHardC, heavyRejectedHardB;
  std::vector<int> heavyOriginDepthC, heavyOriginDepthB;
  std::vector<int> heavyConstituentOffsets, heavyConstituentParentSlot;
  std::vector<int> heavyConstituentPdg, heavyConstituentOrdinal;
  std::vector<int> heavyConstituentOrigin;
  std::vector<int> heavyConstituentMatchResolution;
  std::vector<int> heavyConstituentMatchedHard;
  std::vector<int> heavyConstituentRejectedHard;
  std::vector<int> heavyConstituentOriginDepth;
  std::vector<double> heavyPx, heavyPy, heavyPz, heavyE, heavyPt, heavyEta;
  std::vector<double> heavyY, heavyPhi, heavyMass;
  std::vector<int> ancestryIndex, ancestryPdg, ancestryStatus;
  std::vector<int> ancestryMother1, ancestryMother2;
  std::vector<int> ancestryMotherOffsets, ancestryMothers;
  // Pilot-only flat record of every final charged particle, so the raw
  // validator can recompute both counters independently of the producer.
  std::vector<int> multAuditParticleIndex, multAuditPdg, multAuditStatus;
  std::vector<int> multAuditIsHeavy;
  std::vector<double> multAuditPt, multAuditEta;

  tree.Branch("event_id", &eventId, "event_id/l");
  tree.Branch("process_code", &processCode, "process_code/I");
  tree.Branch("hard_channel", &hardChannel, "hard_channel/I");
  tree.Branch("event_weight", &eventWeight, "event_weight/D");
  tree.Branch("pthat", &pTHat, "pthat/D");
  tree.Branch("hard_scale", &hardScale, "hard_scale/D");
  tree.Branch("n_mpi", &nMPI, "n_mpi/I");
  tree.Branch("multiplicity_final_charged_nonheavy_eta10_v1",
              &multiplicityCentral,
              "multiplicity_final_charged_nonheavy_eta10_v1/I");
  tree.Branch("multiplicity_final_charged_nonheavy_eta40_v1",
              &multiplicityWide,
              "multiplicity_final_charged_nonheavy_eta40_v1/I");
  tree.Branch("multiplicity_central_by_species",
              multiplicityCentralBySpecies,
              "multiplicity_central_by_species[6]/I");
  tree.Branch("light_charge3_grid", lightCharge3Grid,
              Form("light_charge3_grid[%d]/S", kLightGridCells));
  tree.Branch("light_baryon_grid", lightBaryonGrid,
              Form("light_baryon_grid[%d]/S", kLightGridCells));
  tree.Branch("hard_indices", &hardIndices);
  tree.Branch("hard_bottom_indices", &hardBottomIndices);
  tree.Branch("hard_ids", &hardIds);
  tree.Branch("hard_status", &hardStatus);
  tree.Branch("hard_bottom_ids", &hardBottomIds);
  tree.Branch("hard_bottom_status", &hardBottomStatus);
  tree.Branch("hard_px", &hardPx);
  tree.Branch("hard_py", &hardPy);
  tree.Branch("hard_pz", &hardPz);
  tree.Branch("hard_e", &hardE);

  tree.Branch("ID", &legacyId);
  tree.Branch("HFCLASS", &legacyClass);
  tree.Branch("PT", &legacyPt);
  tree.Branch("ETA", &legacyEta);
  tree.Branch("Y", &legacyY);
  tree.Branch("PHI", &legacyPhi);
  tree.Branch("CHARGE", &legacyCharge);
  tree.Branch("STATUS", &legacyStatus);
  tree.Branch("MOTHER", &legacyMother);
  tree.Branch("MOTHERID", &legacyMotherId);
  tree.Branch("MULTIPLICITY", &multiplicityCentral, "MULTIPLICITY/I");
  tree.Branch("PROCESSCODE", &processCode, "PROCESSCODE/I");
  tree.Branch("NCHARM", &nCharmOnly, "NCHARM/I");
  tree.Branch("NBEAUTY", &nBeautyOnly, "NBEAUTY/I");
  tree.Branch("NBC", &nBc, "NBC/I");
  tree.Branch("final_heavy_qc_sum", &finalHeavyQcSum,
              "final_heavy_qc_sum/I");
  tree.Branch("final_heavy_qb_sum", &finalHeavyQbSum,
              "final_heavy_qb_sum/I");
  tree.Branch("heavy_flavour_conservation_ok",
              &heavyFlavourConservationOk,
              "heavy_flavour_conservation_ok/I");
  tree.Branch("origin_classification_valid", &originClassificationValid,
              "origin_classification_valid/I");
  tree.Branch("primary_all_heavy_match_valid", &primaryAllHeavyMatchValid,
              "primary_all_heavy_match_valid/I");

#define BRANCH_VECTOR(name) tree.Branch(#name, &name)
  BRANCH_VECTOR(heavyIndex);
  BRANCH_VECTOR(heavyPdg);
  BRANCH_VECTOR(heavyStatus);
  BRANCH_VECTOR(heavyStatusAbs);
  BRANCH_VECTOR(heavyIsFinal);
  BRANCH_VECTOR(heavyIsMeson);
  BRANCH_VECTOR(heavyIsBaryon);
  BRANCH_VECTOR(heavyCharge3);
  BRANCH_VECTOR(heavySpinType);
  BRANCH_VECTOR(heavyMother1);
  BRANCH_VECTOR(heavyMother2);
  BRANCH_VECTOR(heavyDaughter1);
  BRANCH_VECTOR(heavyDaughter2);
  BRANCH_VECTOR(heavyMotherOffsets);
  BRANCH_VECTOR(heavyMothers);
  BRANCH_VECTOR(heavyNc);
  BRANCH_VECTOR(heavyNcbar);
  BRANCH_VECTOR(heavyNb);
  BRANCH_VECTOR(heavyNbbar);
  BRANCH_VECTOR(heavyQc);
  BRANCH_VECTOR(heavyQb);
  BRANCH_VECTOR(heavyBaryonNumber);
  BRANCH_VECTOR(heavyStrangeness);
  BRANCH_VECTOR(heavyCentral);
  BRANCH_VECTOR(heavyOpen);
  BRANCH_VECTOR(heavyHidden);
  BRANCH_VECTOR(heavyStateCategory);
  BRANCH_VECTOR(heavyOriginC);
  BRANCH_VECTOR(heavyOriginB);
  BRANCH_VECTOR(heavyMatchResolutionC);
  BRANCH_VECTOR(heavyMatchResolutionB);
  BRANCH_VECTOR(heavyMatchedHardC);
  BRANCH_VECTOR(heavyMatchedHardB);
  BRANCH_VECTOR(heavyRejectedHardC);
  BRANCH_VECTOR(heavyRejectedHardB);
  BRANCH_VECTOR(heavyOriginDepthC);
  BRANCH_VECTOR(heavyOriginDepthB);
  BRANCH_VECTOR(heavyConstituentOffsets);
  BRANCH_VECTOR(heavyConstituentParentSlot);
  BRANCH_VECTOR(heavyConstituentPdg);
  BRANCH_VECTOR(heavyConstituentOrdinal);
  BRANCH_VECTOR(heavyConstituentOrigin);
  BRANCH_VECTOR(heavyConstituentMatchResolution);
  BRANCH_VECTOR(heavyConstituentMatchedHard);
  BRANCH_VECTOR(heavyConstituentRejectedHard);
  BRANCH_VECTOR(heavyConstituentOriginDepth);
  BRANCH_VECTOR(heavyPx);
  BRANCH_VECTOR(heavyPy);
  BRANCH_VECTOR(heavyPz);
  BRANCH_VECTOR(heavyE);
  BRANCH_VECTOR(heavyPt);
  BRANCH_VECTOR(heavyEta);
  BRANCH_VECTOR(heavyY);
  BRANCH_VECTOR(heavyPhi);
  BRANCH_VECTOR(heavyMass);
  BRANCH_VECTOR(ancestryIndex);
  BRANCH_VECTOR(ancestryPdg);
  BRANCH_VECTOR(ancestryStatus);
  BRANCH_VECTOR(ancestryMother1);
  BRANCH_VECTOR(ancestryMother2);
  BRANCH_VECTOR(ancestryMotherOffsets);
  BRANCH_VECTOR(ancestryMothers);
  BRANCH_VECTOR(multAuditParticleIndex);
  BRANCH_VECTOR(multAuditPdg);
  BRANCH_VECTOR(multAuditStatus);
  BRANCH_VECTOR(multAuditIsHeavy);
  BRANCH_VECTOR(multAuditPt);
  BRANCH_VECTOR(multAuditEta);
#undef BRANCH_VECTOR

  TH1D hMultiplicity(
      "hMULTIPLICITY",
      "NCH_FINAL_CHARGED_NONHEAVY_ETA10_V1;N_{ch};successful events", 4096,
      -0.5,
      4095.5);
  hMultiplicity.Sumw2();
  TH1D hMultiplicityWide(
      "hMULTIPLICITY_ETA40",
      "NCH_FINAL_CHARGED_NONHEAVY_ETA40_V1;N_{ch};successful events", 4096,
      -0.5,
      4095.5);
  hMultiplicityWide.Sumw2();
  TH1I hProcessCode("hPROCESS_CODE", "hard process code;code;events", 1000, -0.5,
                    999.5);

  std::uint64_t attempts = 0;
  std::uint64_t successes = 0;
  std::uint64_t failures = 0;
  double sumWeights = 0.0;
  double sumWeights2 = 0.0;
  std::map<int, std::uint64_t> processCounts;
  std::uint64_t multiplicityOverflow = 0;
  std::uint64_t multiplicityWideOverflow = 0;
  std::uint64_t contentDecodeFailures = 0;
  std::uint64_t duplicateHardCarrierConflictGroupsC = 0;
  std::uint64_t duplicateHardCarrierConflictGroupsB = 0;
  std::uint64_t duplicateHardCarrierDemotionsC = 0;
  std::uint64_t duplicateHardCarrierDemotionsB = 0;
  std::uint64_t multiHeavyConstituentRejectionsC = 0;
  std::uint64_t multiHeavyConstituentRejectionsB = 0;
  std::uint64_t heavyFlavourConservationFailures = 0;
  std::uint64_t originClassificationFailures = 0;
  std::uint64_t primaryAllHeavyConflictGroups = 0;
  std::uint64_t primaryAllHeavyDemotions = 0;
  std::uint64_t primaryAllHeavyMatchFailures = 0;

  std::cout << "PRODUCTION_START campaign=" << campaign << " tune=" << tune
            << " logical_id=" << logicalId << " role=" << role
            << " attempt=" << attempt << " seed=" << seed
            << " requested_successes=" << requestedSuccesses << "\n";

  while (successes < requestedSuccesses && attempts < attemptCeiling) {
    ++attempts;
    if (abortAfterAttempts > 0 && attempts > abortAfterAttempts) {
      std::cerr << "INJECTED_ABORT attempts=" << attempts
                << " successes=" << successes << "\n";
      return 99;
    }
    if (attempts <= forcedFailures) {
      ++failures;
      continue;
    }
    if (!pythia.next()) {
      ++failures;
      continue;
    }

    eventId = EventId(campaignOrdinal, TuneOrdinal(tune), logicalId, attempt,
                      successes);
    processCode = pythia.info.code();
    eventWeight = pythia.info.weight();
    pTHat = pythia.info.pTHat();
    hardScale = pythia.info.scalup();
    nMPI = pythia.info.nMPI();
    const std::vector<HardParton> hardPartons = FindHardPartons(pythia.event);
    if (!IsExactSignedHardPair(pythia.event, hardPartons)) {
      std::cerr << "ERROR: generated event does not contain exactly one "
                   "validated signed hard-heavy pair"
                << " process_code=" << processCode
                << " local_success=" << successes
                << " candidates=" << hardPartons.size() << "\n";
      for (const auto& hard : hardPartons) {
        const bool rootInRange =
            hard.rootIndex > 0 && hard.rootIndex < pythia.event.size();
        const bool bottomInRange =
            hard.bottomIndex > 0 && hard.bottomIndex < pythia.event.size();
        std::cerr << "  hard root=" << hard.rootIndex
                  << " id=" << hard.id
                  << " root_status="
                  << (rootInRange ? pythia.event[hard.rootIndex].status() : 0)
                  << " bottom=" << hard.bottomIndex
                  << " bottom_id="
                  << (bottomInRange ? pythia.event[hard.bottomIndex].id() : 0)
                  << " bottom_status="
                  << (bottomInRange
                          ? pythia.event[hard.bottomIndex].status()
                          : 0)
                  << "\n";
      }
      output.Close();
      return 6;
    }
    hardChannel = HardChannel(hardPartons);
    const int processHardChannel =
        (processCode == 121 || processCode == 122)
            ? 4
            : ((processCode == 123 || processCode == 124) ? 5 : 0);
    if (hardChannel != processHardChannel) {
      std::cerr << "ERROR: verified hard pair disagrees with PYTHIA process "
                   "code mapping"
                << " process_code=" << processCode
                << " hard_channel=" << hardChannel << "\n";
      output.Close();
      return 6;
    }
    hardIndices.clear();
    hardBottomIndices.clear();
    hardIds.clear();
    hardStatus.clear();
    hardBottomIds.clear();
    hardBottomStatus.clear();
    hardPx.clear();
    hardPy.clear();
    hardPz.clear();
    hardE.clear();
    for (const auto& hard : hardPartons) {
      hardIndices.push_back(hard.rootIndex);
      hardBottomIndices.push_back(hard.bottomIndex);
      hardIds.push_back(hard.id);
      hardStatus.push_back(pythia.event[hard.rootIndex].status());
      hardBottomIds.push_back(pythia.event[hard.bottomIndex].id());
      hardBottomStatus.push_back(pythia.event[hard.bottomIndex].status());
      hardPx.push_back(pythia.event[hard.rootIndex].px());
      hardPy.push_back(pythia.event[hard.rootIndex].py());
      hardPz.push_back(pythia.event[hard.rootIndex].pz());
      hardE.push_back(pythia.event[hard.rootIndex].e());
    }

    multiplicityCentral = 0;
    multiplicityWide = 0;
    nCharmOnly = 0;
    nBeautyOnly = 0;
    nBc = 0;
    finalHeavyQcSum = 0;
    finalHeavyQbSum = 0;
    heavyFlavourConservationOk = 0;
    originClassificationValid = 1;
    primaryAllHeavyMatchValid = 1;
    std::fill(std::begin(multiplicityCentralBySpecies),
              std::end(multiplicityCentralBySpecies), 0);
    std::fill(std::begin(lightCharge3Grid), std::end(lightCharge3Grid), 0);
    std::fill(std::begin(lightBaryonGrid), std::end(lightBaryonGrid), 0);

#define CLEAR_VECTOR(name) name.clear()
    CLEAR_VECTOR(legacyId); CLEAR_VECTOR(legacyClass); CLEAR_VECTOR(legacyPt);
    CLEAR_VECTOR(legacyEta); CLEAR_VECTOR(legacyY); CLEAR_VECTOR(legacyPhi);
    CLEAR_VECTOR(legacyCharge); CLEAR_VECTOR(legacyStatus);
    CLEAR_VECTOR(legacyMother); CLEAR_VECTOR(legacyMotherId);
    CLEAR_VECTOR(heavyIndex); CLEAR_VECTOR(heavyPdg); CLEAR_VECTOR(heavyStatus);
    CLEAR_VECTOR(heavyStatusAbs); CLEAR_VECTOR(heavyIsFinal);
    CLEAR_VECTOR(heavyIsMeson); CLEAR_VECTOR(heavyIsBaryon);
    CLEAR_VECTOR(heavyCharge3); CLEAR_VECTOR(heavySpinType);
    CLEAR_VECTOR(heavyMother1);
    CLEAR_VECTOR(heavyMother2); CLEAR_VECTOR(heavyDaughter1);
    CLEAR_VECTOR(heavyDaughter2); CLEAR_VECTOR(heavyMotherOffsets);
    CLEAR_VECTOR(heavyMothers); CLEAR_VECTOR(heavyNc); CLEAR_VECTOR(heavyNcbar);
    CLEAR_VECTOR(heavyNb); CLEAR_VECTOR(heavyNbbar); CLEAR_VECTOR(heavyQc);
    CLEAR_VECTOR(heavyQb); CLEAR_VECTOR(heavyBaryonNumber);
    CLEAR_VECTOR(heavyStrangeness); CLEAR_VECTOR(heavyCentral);
    CLEAR_VECTOR(heavyOpen); CLEAR_VECTOR(heavyHidden);
    CLEAR_VECTOR(heavyStateCategory);
    CLEAR_VECTOR(heavyOriginC); CLEAR_VECTOR(heavyOriginB);
    CLEAR_VECTOR(heavyMatchResolutionC);
    CLEAR_VECTOR(heavyMatchResolutionB);
    CLEAR_VECTOR(heavyMatchedHardC); CLEAR_VECTOR(heavyMatchedHardB);
    CLEAR_VECTOR(heavyRejectedHardC); CLEAR_VECTOR(heavyRejectedHardB);
    CLEAR_VECTOR(heavyOriginDepthC); CLEAR_VECTOR(heavyOriginDepthB);
    CLEAR_VECTOR(heavyConstituentOffsets);
    CLEAR_VECTOR(heavyConstituentParentSlot);
    CLEAR_VECTOR(heavyConstituentPdg);
    CLEAR_VECTOR(heavyConstituentOrdinal);
    CLEAR_VECTOR(heavyConstituentOrigin);
    CLEAR_VECTOR(heavyConstituentMatchResolution);
    CLEAR_VECTOR(heavyConstituentMatchedHard);
    CLEAR_VECTOR(heavyConstituentRejectedHard);
    CLEAR_VECTOR(heavyConstituentOriginDepth);
    CLEAR_VECTOR(heavyPx); CLEAR_VECTOR(heavyPy); CLEAR_VECTOR(heavyPz);
    CLEAR_VECTOR(heavyE); CLEAR_VECTOR(heavyPt); CLEAR_VECTOR(heavyEta);
    CLEAR_VECTOR(heavyY); CLEAR_VECTOR(heavyPhi); CLEAR_VECTOR(heavyMass);
    CLEAR_VECTOR(ancestryIndex); CLEAR_VECTOR(ancestryPdg);
    CLEAR_VECTOR(ancestryStatus); CLEAR_VECTOR(ancestryMother1);
    CLEAR_VECTOR(ancestryMother2); CLEAR_VECTOR(ancestryMotherOffsets);
    CLEAR_VECTOR(ancestryMothers);
    CLEAR_VECTOR(multAuditParticleIndex); CLEAR_VECTOR(multAuditPdg);
    CLEAR_VECTOR(multAuditStatus); CLEAR_VECTOR(multAuditIsHeavy);
    CLEAR_VECTOR(multAuditPt); CLEAR_VECTOR(multAuditEta);
#undef CLEAR_VECTOR
    heavyMotherOffsets.push_back(0);
    heavyConstituentOffsets.push_back(0);
    std::set<int> ancestryNodes;

    for (int index = 0; index < pythia.event.size(); ++index) {
      const Particle& particle = pythia.event[index];
      const int id = particle.id();
      const int absId = std::abs(id);
      // Charged-particle multiplicity. Heavy-flavour hadrons are excluded:
      // they are final only because their decays were disabled, so an
      // experiment would count their daughters instead, and including them
      // would correlate the event-activity classifier with the observable it
      // classifies.
      const int pythiaCharm = pythia.particleData.nQuarksInCode(id, 4);
      const int pythiaBeauty = pythia.particleData.nQuarksInCode(id, 5);
      const bool hasHeavyConstituent = pythiaCharm != 0 || pythiaBeauty != 0;
      // Auxiliary light-hadron compensation grid: every final light
      // primary, charged or neutral, since baryon number is carried by
      // neutrons and Lambdas too.
      if (particle.isFinal() && !hasHeavyConstituent) {
        const int cell = LightGridCell(particle.eta(), particle.phi());
        if (cell >= 0) {
          lightCharge3Grid[cell] = static_cast<Short_t>(
              lightCharge3Grid[cell] + pythia.particleData.chargeType(id));
          if (pythia.particleData.isBaryon(id)) {
            lightBaryonGrid[cell] = static_cast<Short_t>(
                lightBaryonGrid[cell] + (id > 0 ? 1 : -1));
          }
        }
      }

      if (particle.isFinal() && particle.isCharged()) {
        if (successes < multiplicityAuditEvents) {
          multAuditParticleIndex.push_back(index);
          multAuditPdg.push_back(id);
          multAuditStatus.push_back(particle.status());
          multAuditIsHeavy.push_back(hasHeavyConstituent ? 1 : 0);
          multAuditPt.push_back(particle.pT());
          multAuditEta.push_back(particle.eta());
        }
        if (CountsNchFinalChargedNonHeavyV1(
                particle.isFinal(), particle.isCharged(), hasHeavyConstituent,
                particle.pT(), particle.eta(), kMultiplicityEtaCentral)) {
          ++multiplicityCentral;
          ++multiplicityCentralBySpecies[MultiplicitySpeciesIndex(absId)];
        }
        if (CountsNchFinalChargedNonHeavyV1(
                particle.isFinal(), particle.isCharged(), hasHeavyConstituent,
                particle.pT(), particle.eta(), kMultiplicityEtaWide)) {
          ++multiplicityWide;
        }
      }

      if (!pythia.particleData.isHadron(id) || !hasHeavyConstituent) continue;

      const bool isMeson = pythia.particleData.isMeson(id);
      const bool isBaryon = pythia.particleData.isBaryon(id);
      const HeavyContent content = DecodeHeavyContent(id, isMeson, isBaryon);
      if ((pythiaCharm > 0 && !content.hasCharm()) ||
          (pythiaBeauty > 0 && !content.hasBeauty())) {
        ++contentDecodeFailures;
      }
      const OriginMatch charmOrigin =
          MatchOrigin(pythia.event, index, 4,
                      content.qc() > 0 ? 1 : (content.qc() < 0 ? -1 : 0),
                      hardPartons);
      const OriginMatch beautyOrigin =
          MatchOrigin(pythia.event, index, 5,
                      content.qb() > 0 ? 1 : (content.qb() < 0 ? -1 : 0),
                      hardPartons);
      const std::array<std::pair<int, int>, 4> signedConstituents{{
          {4, content.nc},
          {-4, content.ncbar},
          {5, content.nb},
          {-5, content.nbbar},
      }};
      const int heavySlot = static_cast<int>(heavyPdg.size());
      for (const auto& [signedFlavour, count] : signedConstituents) {
        if (count <= 0) continue;
        const int flavour = std::abs(signedFlavour);
        const int sign = signedFlavour > 0 ? 1 : -1;
        const OriginMatch constituentMatch =
            MatchOrigin(pythia.event, index, flavour, sign, hardPartons);
        CollectOriginAuditNodes(pythia.event, index, flavour, sign,
                                ancestryNodes);
        for (int ordinal = 0; ordinal < count; ++ordinal) {
          heavyConstituentParentSlot.push_back(heavySlot);
          heavyConstituentPdg.push_back(signedFlavour);
          heavyConstituentOrdinal.push_back(ordinal);
          heavyConstituentOrigin.push_back(
              static_cast<int>(constituentMatch.origin));
          heavyConstituentMatchResolution.push_back(
              static_cast<int>(constituentMatch.resolution));
          heavyConstituentMatchedHard.push_back(
              constituentMatch.hardRootIndex);
          heavyConstituentRejectedHard.push_back(-1);
          heavyConstituentOriginDepth.push_back(constituentMatch.depth);
        }
      }
      if (static_cast<int>(successes) == debugLocalEvent) {
        std::cout << "DEBUG_HEAVY_ORIGIN index=" << index << " pdg=" << id
                  << " status=" << particle.status()
                  << " qc=" << content.qc() << " qb=" << content.qb()
                  << " charm_origin=" << static_cast<int>(charmOrigin.origin)
                  << " charm_hard=" << charmOrigin.hardRootIndex
                  << " beauty_origin="
                  << static_cast<int>(beautyOrigin.origin)
                  << " beauty_hard=" << beautyOrigin.hardRootIndex << "\n";
      }

      const int mother1 = particle.mother1();
      const int motherId =
          mother1 > 0 && mother1 < pythia.event.size()
              ? pythia.event[mother1].id()
              : 0;
      const bool hasCharm = content.hasCharm();
      const bool hasBeauty = content.hasBeauty();
      const int legacyHfClass =
          hasCharm && hasBeauty ? 45 : (hasBeauty ? 5 : (hasCharm ? 4 : -1));
      nBc += hasCharm && hasBeauty ? 1 : 0;
      nCharmOnly += hasCharm && !hasBeauty ? 1 : 0;
      nBeautyOnly += hasBeauty && !hasCharm ? 1 : 0;

      legacyId.push_back(id);
      legacyClass.push_back(legacyHfClass);
      legacyPt.push_back(particle.pT());
      legacyEta.push_back(particle.eta());
      legacyY.push_back(particle.y());
      legacyPhi.push_back(particle.phi());
      legacyCharge.push_back(particle.charge());
      legacyStatus.push_back(particle.status());
      legacyMother.push_back(mother1);
      legacyMotherId.push_back(motherId);

      heavyIndex.push_back(index);
      heavyPdg.push_back(id);
      heavyStatus.push_back(particle.status());
      heavyStatusAbs.push_back(particle.statusAbs());
      heavyIsFinal.push_back(particle.isFinal() ? 1 : 0);
      heavyIsMeson.push_back(isMeson ? 1 : 0);
      heavyIsBaryon.push_back(isBaryon ? 1 : 0);
      heavyCharge3.push_back(pythia.particleData.chargeType(id));
      const int spinType = pythia.particleData.spinType(id);
      heavySpinType.push_back(spinType);
      heavyMother1.push_back(particle.mother1());
      heavyMother2.push_back(particle.mother2());
      heavyDaughter1.push_back(particle.daughter1());
      heavyDaughter2.push_back(particle.daughter2());
      for (const int mother : ExplicitMotherIndices(pythia.event, index)) {
        heavyMothers.push_back(mother);
      }
      heavyMotherOffsets.push_back(static_cast<int>(heavyMothers.size()));
      heavyConstituentOffsets.push_back(
          static_cast<int>(heavyConstituentPdg.size()));
      heavyNc.push_back(content.nc);
      heavyNcbar.push_back(content.ncbar);
      heavyNb.push_back(content.nb);
      heavyNbbar.push_back(content.nbbar);
      heavyQc.push_back(content.qc());
      heavyQb.push_back(content.qb());
      int baryonNumber = 0;
      if (!DecodePythiaBaryonNumber(
              id, isMeson, isBaryon,
              pythia.particleData.baryonNumberType(id), baryonNumber)) {
        ++contentDecodeFailures;
      }
      heavyBaryonNumber.push_back(baryonNumber);
      heavyStrangeness.push_back(content.strangeness());
      const bool selectedState = FindSelectedState(id) != nullptr;
      heavyCentral.push_back(selectedState ? 1 : 0);
      heavyOpen.push_back((content.qc() != 0 || content.qb() != 0) ? 1 : 0);
      heavyHidden.push_back(
          (content.hiddenCharm() || content.hiddenBeauty()) ? 1 : 0);
      heavyStateCategory.push_back(
          static_cast<int>(ClassifyHeavyStateDetailed(
              selectedState, content, isMeson, spinType)));
      heavyOriginC.push_back(static_cast<int>(charmOrigin.origin));
      heavyOriginB.push_back(static_cast<int>(beautyOrigin.origin));
      heavyMatchResolutionC.push_back(
          static_cast<int>(charmOrigin.resolution));
      heavyMatchResolutionB.push_back(
          static_cast<int>(beautyOrigin.resolution));
      heavyMatchedHardC.push_back(charmOrigin.hardRootIndex);
      heavyMatchedHardB.push_back(beautyOrigin.hardRootIndex);
      heavyOriginDepthC.push_back(charmOrigin.depth);
      heavyOriginDepthB.push_back(beautyOrigin.depth);
      heavyPx.push_back(particle.px());
      heavyPy.push_back(particle.py());
      heavyPz.push_back(particle.pz());
      heavyE.push_back(particle.e());
      heavyPt.push_back(particle.pT());
      heavyEta.push_back(particle.eta());
      heavyY.push_back(particle.y());
      heavyPhi.push_back(particle.phi());
      heavyMass.push_back(particle.m());
    }

    const std::vector<int> originalMatchedHardC = heavyMatchedHardC;
    const std::vector<int> originalMatchedHardB = heavyMatchedHardB;
    const CarrierUniquenessResult charmUniqueness =
        EnforceUniqueFinalHardCarrier(
            heavyIsFinal, heavyQc, heavyOriginC, heavyMatchResolutionC,
            heavyMatchedHardC);
    const CarrierUniquenessResult beautyUniqueness =
        EnforceUniqueFinalHardCarrier(
            heavyIsFinal, heavyQb, heavyOriginB, heavyMatchResolutionB,
            heavyMatchedHardB);
    duplicateHardCarrierConflictGroupsC += charmUniqueness.conflictGroups;
    duplicateHardCarrierConflictGroupsB += beautyUniqueness.conflictGroups;
    duplicateHardCarrierDemotionsC += charmUniqueness.demotedMatches;
    duplicateHardCarrierDemotionsB += beautyUniqueness.demotedMatches;
    heavyRejectedHardC.assign(heavyPdg.size(), -1);
    heavyRejectedHardB.assign(heavyPdg.size(), -1);
    for (std::size_t index = 0; index < heavyPdg.size(); ++index) {
      if (heavyMatchResolutionC[index] ==
          static_cast<int>(MatchResolution::kDuplicateHardCarrier)) {
        heavyRejectedHardC[index] = originalMatchedHardC[index];
      }
      if (heavyMatchResolutionB[index] ==
          static_cast<int>(MatchResolution::kDuplicateHardCarrier)) {
        heavyRejectedHardB[index] = originalMatchedHardB[index];
      }
    }
    multiHeavyConstituentRejectionsC += RejectFinalMultiHeavyCarrier(
        heavyIsFinal, heavyQc, heavyOriginC, heavyMatchResolutionC,
        heavyMatchedHardC, heavyRejectedHardC);
    multiHeavyConstituentRejectionsB += RejectFinalMultiHeavyCarrier(
        heavyIsFinal, heavyQb, heavyOriginB, heavyMatchResolutionB,
        heavyMatchedHardB, heavyRejectedHardB);

    std::vector<int> constituentParentIsFinal;
    constituentParentIsFinal.reserve(heavyConstituentParentSlot.size());
    for (const int parentSlot : heavyConstituentParentSlot) {
      if (parentSlot < 0 ||
          parentSlot >= static_cast<int>(heavyIsFinal.size())) {
        primaryAllHeavyMatchValid = 0;
        constituentParentIsFinal.push_back(0);
      } else {
        constituentParentIsFinal.push_back(heavyIsFinal[parentSlot]);
      }
    }
    const CarrierUniquenessResult constituentUniqueness =
        EnforceUniqueFinalConstituentHardCarrier(
            heavyConstituentParentSlot, constituentParentIsFinal,
            heavyConstituentPdg,
            heavyConstituentOrigin, heavyConstituentMatchResolution,
            heavyConstituentMatchedHard, heavyConstituentRejectedHard);
    primaryAllHeavyConflictGroups += constituentUniqueness.conflictGroups;
    primaryAllHeavyDemotions += constituentUniqueness.demotedMatches;

    std::map<int, int> survivingFinalConstituentParent;
    for (std::size_t constituent = 0;
         constituent < heavyConstituentPdg.size(); ++constituent) {
      const int parentSlot = heavyConstituentParentSlot[constituent];
      const int signedFlavour = heavyConstituentPdg[constituent];
      const int origin = heavyConstituentOrigin[constituent];
      const int resolution =
          heavyConstituentMatchResolution[constituent];
      const int matched = heavyConstituentMatchedHard[constituent];
      const int rejected = heavyConstituentRejectedHard[constituent];
      const bool isFinal = constituentParentIsFinal[constituent] != 0;
      if ((std::abs(signedFlavour) != 4 &&
           std::abs(signedFlavour) != 5) ||
          (origin == static_cast<int>(Origin::kSelectedHard) &&
           (resolution != static_cast<int>(MatchResolution::kUnique) ||
            matched < 0 || rejected != -1)) ||
          (origin != static_cast<int>(Origin::kSelectedHard) &&
           matched != -1) ||
          (origin == static_cast<int>(Origin::kUnresolved) &&
           resolution == static_cast<int>(MatchResolution::kUnique))) {
        primaryAllHeavyMatchValid = 0;
        continue;
      }
      if (matched >= 0) {
        const auto hard = std::find_if(
            hardPartons.begin(), hardPartons.end(),
            [matched](const HardParton& candidate) {
              return candidate.rootIndex == matched;
            });
        bool distinctParentConflict = false;
        if (isFinal) {
          const auto [claim, inserted] =
              survivingFinalConstituentParent.emplace(matched, parentSlot);
          distinctParentConflict = !inserted && claim->second != parentSlot;
        }
        if (hard == hardPartons.end() || hard->id != signedFlavour ||
            distinctParentConflict) {
          primaryAllHeavyMatchValid = 0;
        }
      }
      if (rejected >= 0) {
        const auto hard = std::find_if(
            hardPartons.begin(), hardPartons.end(),
            [rejected](const HardParton& candidate) {
              return candidate.rootIndex == rejected;
            });
        if (hard == hardPartons.end() || hard->id != signedFlavour ||
            resolution !=
                static_cast<int>(
                    MatchResolution::kDuplicateHardCarrier)) {
          primaryAllHeavyMatchValid = 0;
        }
      }
    }

    std::set<int> survivingFinalHardC;
    std::set<int> survivingFinalHardB;
    for (std::size_t index = 0; index < heavyPdg.size(); ++index) {
      if (heavyIsFinal[index]) {
        finalHeavyQcSum += heavyQc[index];
        finalHeavyQbSum += heavyQb[index];
      }
      const auto validateSelectedCarrier =
          [&](int sectorCharge, int origin, int resolution, int matchedHard,
              int rejectedHard, int flavour, std::set<int>& surviving) {
            if (sectorCharge == 0) {
              return origin == static_cast<int>(Origin::kUnresolved) &&
                     resolution ==
                         static_cast<int>(MatchResolution::kNotApplicable) &&
                     matchedHard == -1 && rejectedHard == -1;
            }
            if (origin != static_cast<int>(Origin::kSelectedHard)) {
              return matchedHard == -1;
            }
            const auto hard = std::find_if(
                hardPartons.begin(), hardPartons.end(),
                [matchedHard](const HardParton& candidate) {
                  return candidate.rootIndex == matchedHard;
                });
            const int requiredId =
                sectorCharge > 0 ? flavour : -flavour;
            if (resolution != static_cast<int>(MatchResolution::kUnique) ||
                rejectedHard != -1 || hard == hardPartons.end() ||
                hard->id != requiredId ||
                (heavyIsFinal[index] &&
                 !surviving.insert(matchedHard).second)) {
              return false;
            }
            return true;
          };
      if (!validateSelectedCarrier(
              heavyQc[index], heavyOriginC[index],
              heavyMatchResolutionC[index], heavyMatchedHardC[index],
              heavyRejectedHardC[index], 4, survivingFinalHardC) ||
          !validateSelectedCarrier(
              heavyQb[index], heavyOriginB[index],
              heavyMatchResolutionB[index], heavyMatchedHardB[index],
              heavyRejectedHardB[index], 5, survivingFinalHardB)) {
        originClassificationValid = 0;
      }
    }
    heavyFlavourConservationOk =
        finalHeavyQcSum == 0 && finalHeavyQbSum == 0 ? 1 : 0;
    if (!heavyFlavourConservationOk) {
      ++heavyFlavourConservationFailures;
    }
    if (!originClassificationValid) {
      ++originClassificationFailures;
    }
    if (!primaryAllHeavyMatchValid) {
      ++primaryAllHeavyMatchFailures;
    }

    ancestryMotherOffsets.push_back(0);
    for (const int index : ancestryNodes) {
      const Particle& ancestor = pythia.event[index];
      ancestryIndex.push_back(index);
      ancestryPdg.push_back(ancestor.id());
      ancestryStatus.push_back(ancestor.status());
      ancestryMother1.push_back(ancestor.mother1());
      ancestryMother2.push_back(ancestor.mother2());
      for (const int mother : ExplicitMotherIndices(pythia.event, index)) {
        ancestryMothers.push_back(mother);
      }
      ancestryMotherOffsets.push_back(
          static_cast<int>(ancestryMothers.size()));
    }

    hMultiplicity.Fill(multiplicityCentral, eventWeight);
    hMultiplicityWide.Fill(multiplicityWide, eventWeight);
    if (multiplicityCentral > 4095) ++multiplicityOverflow;
    if (multiplicityWide > 4095) ++multiplicityWideOverflow;
    hProcessCode.Fill(processCode);
    ++processCounts[processCode];
    sumWeights += eventWeight;
    sumWeights2 += eventWeight * eventWeight;
    tree.Fill();
    if (static_cast<int>(successes) == debugLocalEvent) {
      std::cout << "DEBUG_EVENT_LIST local_success=" << successes << "\n";
      pythia.event.list();
    }
    ++successes;
  }

  const std::string pythiaStatistics = CaptureStatistics(pythia);
  const std::string stabilityAuditCanonical =
      SerializeStabilityAudit(stabilityRows);
  const std::string stabilityAuditSha256 =
      Sha256Hex(stabilityAuditCanonical);
  double metadataPthatMin = phaseSpacePthatMin;
  double pythiaSigmaGenMb = pythia.info.sigmaGen();
  double pythiaSigmaErrMb = pythia.info.sigmaErr();
  double pythiaWeightSum = pythia.info.weightSum();
  const bool complete = successes == requestedSuccesses &&
                        attempts == successes + failures &&
                        static_cast<std::uint64_t>(tree.GetEntries()) ==
                            successes &&
                        contentDecodeFailures == 0 &&
                        heavyFlavourConservationFailures == 0 &&
                        originClassificationFailures == 0 &&
                        primaryAllHeavyMatchFailures == 0;

  output.cd();
  tree.Write();
  hMultiplicity.Write();
  hMultiplicityWide.Write();
  hProcessCode.Write();

  TTree stability("heavy_stability_audit",
                  "all PYTHIA heavy-hadron ParticleData entries");
  StabilityRow stabilityValue;
  stability.Branch("pdg", &stabilityValue.pdg, "pdg/I");
  stability.Branch("name", &stabilityValue.name);
  stability.Branch("is_hadron", &stabilityValue.isHadron, "is_hadron/I");
  stability.Branch("is_meson", &stabilityValue.isMeson, "is_meson/I");
  stability.Branch("is_baryon", &stabilityValue.isBaryon, "is_baryon/I");
  stability.Branch("spin_type", &stabilityValue.spinType, "spin_type/I");
  stability.Branch("charge3", &stabilityValue.charge3, "charge3/I");
  stability.Branch("n_charm", &stabilityValue.nCharm, "n_charm/I");
  stability.Branch("n_beauty", &stabilityValue.nBeauty, "n_beauty/I");
  stability.Branch("n_c", &stabilityValue.nc, "n_c/I");
  stability.Branch("n_cbar", &stabilityValue.ncbar, "n_cbar/I");
  stability.Branch("n_b", &stabilityValue.nb, "n_b/I");
  stability.Branch("n_bbar", &stabilityValue.nbbar, "n_bbar/I");
  stability.Branch("q_c", &stabilityValue.qc, "q_c/I");
  stability.Branch("q_b", &stabilityValue.qb, "q_b/I");
  stability.Branch("strangeness", &stabilityValue.strangeness,
                   "strangeness/I");
  stability.Branch("open_heavy", &stabilityValue.openHeavy, "open_heavy/I");
  stability.Branch("hidden_heavy", &stabilityValue.hiddenHeavy,
                   "hidden_heavy/I");
  stability.Branch("central_registry", &stabilityValue.central,
                   "central_registry/I");
  stability.Branch("has_antiparticle", &stabilityValue.hasAnti,
                   "has_antiparticle/I");
  stability.Branch("antiparticle_verified",
                   &stabilityValue.antiparticleVerified,
                   "antiparticle_verified/I");
  stability.Branch("mass", &stabilityValue.mass, "mass/D");
  stability.Branch("tau0", &stabilityValue.tau0, "tau0/D");
  stability.Branch("can_decay", &stabilityValue.canDecay, "can_decay/I");
  stability.Branch("original_may_decay", &stabilityValue.originalMayDecay,
                   "original_may_decay/I");
  stability.Branch("final_may_decay", &stabilityValue.finalMayDecay,
                   "final_may_decay/I");
  for (const auto& row : stabilityRows) {
    stabilityValue = row;
    stability.Fill();
  }
  stability.Write();

  TTree processSummary("process_counts", "unweighted successful-event counts");
  Int_t summaryCode = 0;
  ULong64_t summaryCount = 0;
  processSummary.Branch("code", &summaryCode, "code/I");
  processSummary.Branch("count", &summaryCount, "count/l");
  for (const auto& [code, count] : processCounts) {
    summaryCode = code;
    summaryCount = count;
    processSummary.Fill();
  }
  processSummary.Write();

  TTree effectiveSettingsTree(
      "effective_settings",
      "exhaustive post-init values for every PYTHIA Settings entry");
  std::string effectiveSettingName;
  std::string effectiveSettingValue;
  effectiveSettingsTree.Branch("name", &effectiveSettingName);
  effectiveSettingsTree.Branch("value", &effectiveSettingValue);
  for (const auto& [name, value] : effectiveSettingRows) {
    effectiveSettingName = name;
    effectiveSettingValue = value;
    effectiveSettingsTree.Fill();
  }
  effectiveSettingsTree.Write();

  const auto wallEnd = std::chrono::system_clock::now();
  const auto elapsedSeconds =
      std::chrono::duration_cast<std::chrono::seconds>(wallEnd - wallStart)
          .count();
  ULong64_t peakRssKiB = 0;
  try {
    peakRssKiB = PeakRssKiB();
  } catch (const std::exception& error) {
    std::cerr << "ERROR: resource accounting failed: " << error.what()
              << "\n";
    output.Close();
    return 8;
  }
  Int_t rootCompressionSettings = output.GetCompressionSettings();
  Int_t rootCompressionAlgorithm = output.GetCompressionAlgorithm();
  Int_t rootCompressionLevel = output.GetCompressionLevel();
  TTree metadata("job_metadata", "immutable logical-attempt metadata");
  std::string rawSchema = kRawSchema;
  std::string selector = kSelectorVersion;
  std::string originAlgorithm = kOriginAlgorithmVersion;
  std::string speciesSchema(kSpeciesRegistrySchema);
  std::string speciesSha(kSpeciesRegistrySha256);
  std::string multiplicityDefinition(kMultiplicityDefinitionVersion);
  std::string lightGridSchema(kLightCompensationGridSchema);
  std::string studyDefinitionSchema(kStudyDefinitionSchema);
  std::string studyDefinitionSha(kStudyDefinitionSha256);
  std::string stabilityAuditSchema(kHeavyStabilityAuditSchema);
  std::string stabilityAuditSha = stabilityAuditSha256;
  std::string effectiveSettingsSchema = kEffectiveSettingsSchema;
  std::string effectiveSettingsSha = effectiveSettingsSha256;
  std::string primaryAllHeavySchema = kPrimaryAllHeavyMatchSchema;
  std::string configSha = GetEnv("HADRONIZATION_CONFIG_SHA256", "UNRECORDED");
  std::string executableSha =
      GetEnv("HADRONIZATION_EXECUTABLE_SHA256", "UNRECORDED");
  std::string repositoryCommit =
      GetEnv("HADRONIZATION_REPOSITORY_COMMIT", "UNRECORDED");
  std::string repositoryDirty =
      GetEnv("HADRONIZATION_REPOSITORY_DIRTY", "UNRECORDED");
  std::string rootVersion = gROOT->GetVersion();
  std::string pythiaVersion = std::to_string(PYTHIA_VERSION);
  std::string host = GetEnv("HOSTNAME", "unknown");
  std::string condorCluster = GetEnv("CLUSTERID", "");
  std::string condorProcess = GetEnv("PROCESSID", "");
  ULong64_t requested = requestedSuccesses;
  ULong64_t attemptCount = attempts;
  ULong64_t successCount = successes;
  ULong64_t failureCount = failures;
  ULong64_t entryCount = tree.GetEntries();
  ULong64_t multOverflow = multiplicityOverflow;
  ULong64_t multWideOverflow = multiplicityWideOverflow;
  ULong64_t decodeFailures = contentDecodeFailures;
  ULong64_t duplicateConflictGroupsC =
      duplicateHardCarrierConflictGroupsC;
  ULong64_t duplicateConflictGroupsB =
      duplicateHardCarrierConflictGroupsB;
  ULong64_t duplicateDemotionsC = duplicateHardCarrierDemotionsC;
  ULong64_t duplicateDemotionsB = duplicateHardCarrierDemotionsB;
  ULong64_t multiHeavyRejectionsC = multiHeavyConstituentRejectionsC;
  ULong64_t multiHeavyRejectionsB = multiHeavyConstituentRejectionsB;
  ULong64_t conservationFailures = heavyFlavourConservationFailures;
  ULong64_t classificationFailures = originClassificationFailures;
  ULong64_t allHeavyConflictGroups = primaryAllHeavyConflictGroups;
  ULong64_t allHeavyDemotions = primaryAllHeavyDemotions;
  ULong64_t allHeavyFailures = primaryAllHeavyMatchFailures;
  ULong64_t effectiveSettingCount = effectiveSettingRows.size();
  ULong64_t multiplicityAuditEventCount = multiplicityAuditEvents;
  Long64_t startUnixSeconds =
      std::chrono::duration_cast<std::chrono::seconds>(
          wallStart.time_since_epoch())
          .count();
  Long64_t endUnixSeconds =
      std::chrono::duration_cast<std::chrono::seconds>(
          wallEnd.time_since_epoch())
          .count();
  Long64_t elapsed = elapsedSeconds;
  Int_t completeFlag = complete ? 1 : 0;
  std::string metadataCampaign = campaign;
  std::string metadataTune = tune;
  std::string metadataRole = role;
  metadata.Branch("campaign", &metadataCampaign);
  metadata.Branch("campaign_ordinal", &campaignOrdinal,
                  "campaign_ordinal/I");
  metadata.Branch("raw_schema", &rawSchema);
  metadata.Branch("selector", &selector);
  metadata.Branch("origin_algorithm", &originAlgorithm);
  metadata.Branch("species_registry_schema", &speciesSchema);
  metadata.Branch("species_registry_sha256", &speciesSha);
  metadata.Branch("multiplicity_definition", &multiplicityDefinition);
  metadata.Branch("light_compensation_grid_schema", &lightGridSchema);
  metadata.Branch("study_definition_schema", &studyDefinitionSchema);
  metadata.Branch("study_definition_sha256", &studyDefinitionSha);
  metadata.Branch("heavy_stability_audit_schema", &stabilityAuditSchema);
  metadata.Branch("heavy_stability_audit_sha256", &stabilityAuditSha);
  metadata.Branch("effective_settings_schema", &effectiveSettingsSchema);
  metadata.Branch("effective_settings_sha256", &effectiveSettingsSha);
  metadata.Branch("effective_settings_entries", &effectiveSettingCount,
                  "effective_settings_entries/l");
  metadata.Branch("primary_all_heavy_match_schema",
                  &primaryAllHeavySchema);
  metadata.Branch("config_sha256", &configSha);
  metadata.Branch("executable_sha256", &executableSha);
  metadata.Branch("repository_commit", &repositoryCommit);
  metadata.Branch("repository_dirty", &repositoryDirty);
  metadata.Branch("root_version", &rootVersion);
  metadata.Branch("pythia_version", &pythiaVersion);
  metadata.Branch("tune", &metadataTune);
  metadata.Branch("logical_id", &logicalId, "logical_id/I");
  metadata.Branch("role", &metadataRole);
  metadata.Branch("attempt", &attempt, "attempt/I");
  metadata.Branch("seed", &seed, "seed/I");
  metadata.Branch("requested_successes", &requested, "requested_successes/l");
  metadata.Branch("attempts", &attemptCount, "attempts/l");
  metadata.Branch("successful_events", &successCount, "successful_events/l");
  metadata.Branch("failed_attempts", &failureCount, "failed_attempts/l");
  metadata.Branch("tree_entries", &entryCount, "tree_entries/l");
  metadata.Branch("sum_weights", &sumWeights, "sum_weights/D");
  metadata.Branch("sum_weights2", &sumWeights2, "sum_weights2/D");
  metadata.Branch("phase_space_pthat_min", &metadataPthatMin,
                  "phase_space_pthat_min/D");
  metadata.Branch("pythia_sigma_gen_mb", &pythiaSigmaGenMb,
                  "pythia_sigma_gen_mb/D");
  metadata.Branch("pythia_sigma_err_mb", &pythiaSigmaErrMb,
                  "pythia_sigma_err_mb/D");
  metadata.Branch("pythia_weight_sum", &pythiaWeightSum,
                  "pythia_weight_sum/D");
  metadata.Branch("multiplicity_overflow", &multOverflow,
                  "multiplicity_overflow/l");
  metadata.Branch("multiplicity_wide_overflow", &multWideOverflow,
                  "multiplicity_wide_overflow/l");
  metadata.Branch("content_decode_failures", &decodeFailures,
                  "content_decode_failures/l");
  metadata.Branch("duplicate_hard_carrier_conflict_groups_charm",
                  &duplicateConflictGroupsC,
                  "duplicate_hard_carrier_conflict_groups_charm/l");
  metadata.Branch("duplicate_hard_carrier_conflict_groups_beauty",
                  &duplicateConflictGroupsB,
                  "duplicate_hard_carrier_conflict_groups_beauty/l");
  metadata.Branch("duplicate_hard_carrier_demotions_charm",
                  &duplicateDemotionsC,
                  "duplicate_hard_carrier_demotions_charm/l");
  metadata.Branch("duplicate_hard_carrier_demotions_beauty",
                  &duplicateDemotionsB,
                  "duplicate_hard_carrier_demotions_beauty/l");
  metadata.Branch("multi_heavy_constituent_rejections_charm",
                  &multiHeavyRejectionsC,
                  "multi_heavy_constituent_rejections_charm/l");
  metadata.Branch("multi_heavy_constituent_rejections_beauty",
                  &multiHeavyRejectionsB,
                  "multi_heavy_constituent_rejections_beauty/l");
  metadata.Branch("heavy_flavour_conservation_failures",
                  &conservationFailures,
                  "heavy_flavour_conservation_failures/l");
  metadata.Branch("origin_classification_failures",
                  &classificationFailures,
                  "origin_classification_failures/l");
  metadata.Branch("primary_all_heavy_conflict_groups",
                  &allHeavyConflictGroups,
                  "primary_all_heavy_conflict_groups/l");
  metadata.Branch("primary_all_heavy_demotions", &allHeavyDemotions,
                  "primary_all_heavy_demotions/l");
  metadata.Branch("primary_all_heavy_match_failures", &allHeavyFailures,
                  "primary_all_heavy_match_failures/l");
  metadata.Branch("multiplicity_audit_events", &multiplicityAuditEventCount,
                  "multiplicity_audit_events/l");
  metadata.Branch("start_unix_seconds", &startUnixSeconds,
                  "start_unix_seconds/L");
  metadata.Branch("end_unix_seconds", &endUnixSeconds,
                  "end_unix_seconds/L");
  metadata.Branch("elapsed_seconds", &elapsed, "elapsed_seconds/L");
  metadata.Branch("peak_rss_kib", &peakRssKiB, "peak_rss_kib/l");
  metadata.Branch("root_compression_settings", &rootCompressionSettings,
                  "root_compression_settings/I");
  metadata.Branch("root_compression_algorithm", &rootCompressionAlgorithm,
                  "root_compression_algorithm/I");
  metadata.Branch("root_compression_level", &rootCompressionLevel,
                  "root_compression_level/I");
  metadata.Branch("host", &host);
  metadata.Branch("condor_cluster", &condorCluster);
  metadata.Branch("condor_process", &condorProcess);
  metadata.Branch("complete", &completeFlag, "complete/I");
  metadata.Fill();
  metadata.Write();

  TObjString settingsObject(effectiveSettings.c_str());
  settingsObject.Write("effective_changed_settings");
  TObjString effectiveSettingsCanonicalObject(
      effectiveSettingsCanonical.c_str());
  effectiveSettingsCanonicalObject.Write("effective_settings_canonical");
  TObjString effectiveSettingsShaObject(effectiveSettingsSha256.c_str());
  effectiveSettingsShaObject.Write("effective_settings_sha256");
  TObjString statisticsObject(pythiaStatistics.c_str());
  statisticsObject.Write("pythia_statistics");
  TObjString stabilityCanonicalObject(stabilityAuditCanonical.c_str());
  stabilityCanonicalObject.Write("heavy_stability_audit_canonical");
  TObjString stabilityShaObject(stabilityAuditSha256.c_str());
  stabilityShaObject.Write("heavy_stability_audit_sha256");
  TObjString multiplicityCentralName(kMultiplicityCentral);
  multiplicityCentralName.Write("multiplicity_central_version");
  TObjString multiplicityCrossCheckName(kMultiplicityCrossCheck);
  multiplicityCrossCheckName.Write("multiplicity_crosscheck_version");
  TObjString multiplicityDefinitionContract(kMultiplicityDefinitionVersion);
  multiplicityDefinitionContract.Write("multiplicity_definition");
  TObjString primaryAllHeavyMatchContract(kPrimaryAllHeavyMatchSchema);
  primaryAllHeavyMatchContract.Write("primary_all_heavy_match_version");
  output.Write();
  output.Close();

  std::cout << "PRODUCTION_END attempts=" << attempts
            << " successful_events=" << successes << " failed_attempts="
            << failures << " tree_entries=" << tree.GetEntries()
            << " sumw=" << std::setprecision(17) << sumWeights
            << " sumw2=" << sumWeights2
            << " content_decode_failures=" << contentDecodeFailures
            << " complete=" << completeFlag << "\n";
  if (!complete) {
    std::cerr << "ERROR: exact-success contract failed\n";
    return 5;
  }
  return 0;
}
