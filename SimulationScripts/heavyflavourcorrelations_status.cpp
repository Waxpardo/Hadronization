// Canonical combined-heavy PYTHIA producer for the publication analysis.
//
// Usage:
//   heavyflavourcorrelations_status MODE OUTPUT SEED CAMPAIGN
//       CAMPAIGN_ORDINAL LOGICAL_ID ROLE ATTEMPT
//
// MODE is monash, junctions, or closepacking. SEED is passed to PYTHIA
// unchanged and must be allocated by the immutable campaign seed ledger.

#include "GeneratedHeavyFlavourRegistry.h"
#include "HeavyFlavourUtils.h"

#include "Pythia8/Pythia.h"

#include "TFile.h"
#include "TH1D.h"
#include "TH1I.h"
#include "TObjString.h"
#include "TParameter.h"
#include "TROOT.h"
#include "TTree.h"

#include <algorithm>
#include <array>
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
#include <map>
#include <set>
#include <sstream>
#include <string>
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
  int openHeavy = 0;
  int hiddenHeavy = 0;
  int central = 0;
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

struct OriginMatch {
  Origin origin = Origin::kUnresolved;
  int hardRootIndex = -1;
  int depth = -1;
  MatchResolution resolution = MatchResolution::kNotApplicable;
};

std::string GetEnv(const char* name, const std::string& fallback = "") {
  const char* value = std::getenv(name);
  return value ? value : fallback;
}

std::string ResolveSettingsFile(const std::string& mode) {
  if (mode == "monash") return "pythiasettings_Hard_Low_ccbb_MONASH.cmnd";
  if (mode == "junctions") return "pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd";
  if (mode == "closepacking") {
    return "pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd";
  }
  return "";
}

std::string CanonicalTune(const std::string& mode) {
  if (mode == "monash") return "MONASH";
  if (mode == "junctions") return "JUNCTIONS";
  if (mode == "closepacking") return "CLOSEPACKING";
  return "";
}

bool IsMultiplicitySpecies(int absPdg) {
  return absPdg == 11 || absPdg == 13 || absPdg == 211 ||
         absPdg == 321 || absPdg == 2212;
}

int MultiplicitySpeciesIndex(int absPdg) {
  if (absPdg == 11) return 0;
  if (absPdg == 13) return 1;
  if (absPdg == 211) return 2;
  if (absPdg == 321) return 3;
  if (absPdg == 2212) return 4;
  return -1;
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

std::vector<int> DirectMotherEndpoints(const Event& event, int particleIndex) {
  std::vector<int> result{
      event[particleIndex].mother1(), event[particleIndex].mother2()};
  result.erase(std::remove_if(result.begin(), result.end(),
                              [&event](int index) {
                                return index <= 0 || index >= event.size();
                              }),
               result.end());
  std::sort(result.begin(), result.end());
  result.erase(std::unique(result.begin(), result.end()), result.end());
  return result;
}

bool CarriesSignedHeavyConstituent(int pdg, int flavour, int requiredSign) {
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

bool HasWeakAncestor(const Event& event, int particleIndex) {
  std::deque<int> queue;
  std::set<int> visited;
  for (const int mother : ExplicitMotherIndices(event, particleIndex)) {
    queue.push_back(mother);
  }
  while (!queue.empty()) {
    const int index = queue.front();
    queue.pop_front();
    if (index <= 0 || index >= event.size() || !visited.insert(index).second) {
      continue;
    }
    if (IsKnownWeakParent(std::abs(event[index].id()))) return true;
    for (const int mother : ExplicitMotherIndices(event, index)) {
      queue.push_back(mother);
    }
  }
  return false;
}

std::vector<HardParton> FindHardPartons(const Event& event) {
  std::vector<HardParton> result;
  for (int index = 0; index < event.size(); ++index) {
    const Particle& particle = event[index];
    if (particle.statusAbs() != 23 ||
        (std::abs(particle.id()) != 4 && std::abs(particle.id()) != 5)) {
      continue;
    }
    int bottom = particle.iBotCopy();
    if (bottom <= 0 || bottom >= event.size()) bottom = index;
    result.push_back({index, bottom, particle.id()});
  }
  return result;
}

std::vector<int> NearestHeavyAncestors(const Event& event,
                                       const std::vector<int>& starts,
                                       int flavour, int requiredSign) {
  std::deque<std::pair<int, int>> queue;
  std::set<int> visited;
  for (const int start : starts) queue.push_back({start, 0});
  int foundDepth = -1;
  std::vector<int> found;
  while (!queue.empty()) {
    const auto [index, depth] = queue.front();
    queue.pop_front();
    if (foundDepth >= 0 && depth > foundDepth) break;
    if (index <= 0 || index >= event.size() || !visited.insert(index).second) {
      continue;
    }
    const Particle& ancestor = event[index];
    if (std::abs(ancestor.id()) == flavour &&
        (ancestor.id() > 0 ? 1 : -1) == requiredSign) {
      foundDepth = depth;
      found.push_back(index);
      continue;
    }
    for (const int mother : DirectMotherEndpoints(event, index)) {
      if (CarriesSignedHeavyConstituent(event[mother].id(), flavour,
                                        requiredSign)) {
        queue.push_back({mother, depth + 1});
      }
    }
  }
  return found;
}

OriginMatch MatchOrigin(const Event& event, int particleIndex, int flavour,
                        int requiredSign,
                        const std::vector<HardParton>& hardPartons) {
  if (requiredSign == 0) return {};
  // PYTHIA records the complete fragmenting string/junction parton range as
  // the hadron's mothers. Search that range for the nearest matching signed
  // heavy constituent. Multiple equally near candidates remain unresolved;
  // selecting a convenient one would double-assign a hard constituent.
  const std::vector<int> allMothers =
      ExplicitMotherIndices(event, particleIndex);
  std::vector<int> starts;
  for (const int mother : allMothers) {
    if (CarriesSignedHeavyConstituent(event[mother].id(), flavour,
                                     requiredSign)) {
      starts.push_back(mother);
    }
  }
  // A heavy hadron without a uniquely traceable heavy-carrying string
  // constituent is unresolved by construction. Searching unrelated gluons in
  // the complete string range can spuriously connect it to another hard quark.
  if (starts.empty()) {
    return {Origin::kUnresolved, -1, -1,
            MatchResolution::kMissingCarrier};
  }

  std::vector<int> candidates =
      NearestHeavyAncestors(event, starts, flavour, requiredSign);
  int totalDepth = 1;
  std::set<int> lineageVisited;
  while (candidates.size() == 1 && totalDepth < 1000) {
    const int index = candidates.front();
    if (!lineageVisited.insert(index).second) {
      return {Origin::kUnresolved, -1, totalDepth,
              MatchResolution::kBrokenLineage};
    }
    const Particle& ancestor = event[index];
    for (const auto& hard : hardPartons) {
      if (hard.id != requiredSign * flavour) continue;
      if (index == hard.rootIndex) {
        return {Origin::kSelectedHard, hard.rootIndex, totalDepth,
                MatchResolution::kUnique};
      }
    }
    candidates.clear();
    for (const int mother : DirectMotherEndpoints(event, index)) {
      if (mother <= 0 || mother >= event.size()) continue;
      const Particle& parent = event[mother];
      if (std::abs(parent.id()) == flavour &&
          (parent.id() > 0 ? 1 : -1) == requiredSign) {
        candidates.push_back(mother);
      }
    }
    std::sort(candidates.begin(), candidates.end());
    candidates.erase(std::unique(candidates.begin(), candidates.end()),
                     candidates.end());
    if (candidates.empty()) {
      const int sourceStatus = ancestor.statusAbs();
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
  // Multiple equally near heavy ancestors are a genuine unresolved topology.
  return {Origin::kUnresolved, -1, totalDepth,
          candidates.size() > 1 ? MatchResolution::kAmbiguous
                                : MatchResolution::kBrokenLineage};
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
    for (const int mother : DirectMotherEndpoints(event, index)) {
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

std::vector<std::string> ConfiguredSettingKeys(
    const std::string& settingsFile) {
  std::set<std::string> keys;
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
    keys.insert(key.substr(first, last - first + 1));
  }
  keys.insert("Random:setSeed");
  keys.insert("Random:seed");
  return {keys.begin(), keys.end()};
}

std::vector<std::pair<std::string, std::string>> EffectiveSettingRows(
    Pythia& pythia, const std::vector<std::string>& keys) {
  std::vector<std::pair<std::string, std::string>> rows;
  for (const auto& key : keys) {
    rows.push_back({key, pythia.settings.output(key, false)});
  }
  return rows;
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
      rows.push_back({
          signedId,
          pythia.particleData.name(signedId),
          1,
          entry->isMeson() ? 1 : 0,
          entry->isBaryon() ? 1 : 0,
          entry->spinType(),
          entry->chargeType(signedId),
          nCharm,
          nBeauty,
          ((content.qc() != 0) || (content.qb() != 0)) ? 1 : 0,
          (content.hiddenCharm() || content.hiddenBeauty()) ? 1 : 0,
          FindGroundState(signedId) ? 1 : 0,
          entry->m0(),
          entry->tau0(),
          entry->canDecay() ? 1 : 0,
          original ? 1 : 0,
          0});
    }
  }
  for (const int id : heavyIds) {
    if (pythia.particleData.mayDecay(id)) {
      throw std::runtime_error("heavy hadron remained decay-enabled: " +
                               std::to_string(id));
    }
  }
  return rows;
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
  if (!pythia.readFile(settingsFile)) {
    std::cerr << "ERROR: could not read PYTHIA card " << settingsFile << "\n";
    return 3;
  }
  pythia.readString("Random:setSeed = on");
  pythia.readString("Random:seed = " + std::to_string(seed));
  const std::vector<std::string> configuredSettingKeys =
      ConfiguredSettingKeys(settingsFile);

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
  const std::string effectiveSettings = CaptureChangedSettings(pythia);
  const auto effectiveSettingRows =
      EffectiveSettingRows(pythia, configuredSettingKeys);
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
  Int_t multiplicity = 0;
  Int_t multiplicityStrongEm = 0;
  Int_t nCharmOnly = 0;
  Int_t nBeautyOnly = 0;
  Int_t nBc = 0;
  Int_t multiplicityDirectBySpecies[5] = {0, 0, 0, 0, 0};
  Int_t multiplicityStrongEmBySpecies[5] = {0, 0, 0, 0, 0};

  std::vector<int> hardIndices;
  std::vector<int> hardBottomIndices;
  std::vector<int> hardIds;

  // Legacy reader branches. They now contain every recognized heavy hadron
  // over full phase space; the integer-rich branches below are authoritative.
  std::vector<int> legacyId;
  std::vector<int> legacyClass;
  std::vector<double> legacyPt, legacyEta, legacyY, legacyPhi, legacyCharge;
  std::vector<double> legacyStatus, legacyMother, legacyMotherId;

  std::vector<int> heavyIndex, heavyPdg, heavyStatus, heavyStatusAbs;
  std::vector<int> heavyIsFinal, heavyIsMeson, heavyIsBaryon, heavyCharge3;
  std::vector<int> heavyMother1, heavyMother2, heavyDaughter1, heavyDaughter2;
  std::vector<int> heavyMotherOffsets, heavyMothers;
  std::vector<int> heavyNc, heavyNcbar, heavyNb, heavyNbbar, heavyQc, heavyQb;
  std::vector<int> heavyBaryonNumber, heavyStrangeness, heavyCentral;
  std::vector<int> heavyOpen, heavyHidden;
  std::vector<int> heavyOriginC, heavyOriginB;
  std::vector<int> heavyMatchResolutionC, heavyMatchResolutionB;
  std::vector<int> heavyMatchedHardC, heavyMatchedHardB;
  std::vector<int> heavyOriginDepthC, heavyOriginDepthB;
  std::vector<double> heavyPx, heavyPy, heavyPz, heavyE, heavyPt, heavyEta;
  std::vector<double> heavyY, heavyPhi, heavyMass;
  std::vector<int> ancestryIndex, ancestryPdg, ancestryStatus;
  std::vector<int> ancestryMother1, ancestryMother2;
  std::vector<int> multAuditPdg, multAuditStatus, multAuditHasWeakAncestor;
  std::vector<double> multAuditPt, multAuditEta;

  tree.Branch("event_id", &eventId, "event_id/l");
  tree.Branch("process_code", &processCode, "process_code/I");
  tree.Branch("hard_channel", &hardChannel, "hard_channel/I");
  tree.Branch("event_weight", &eventWeight, "event_weight/D");
  tree.Branch("pthat", &pTHat, "pthat/D");
  tree.Branch("hard_scale", &hardScale, "hard_scale/D");
  tree.Branch("n_mpi", &nMPI, "n_mpi/I");
  tree.Branch("multiplicity_hadronisation_v1", &multiplicity,
              "multiplicity_hadronisation_v1/I");
  tree.Branch("multiplicity_final_strong_em_v1", &multiplicityStrongEm,
              "multiplicity_final_strong_em_v1/I");
  tree.Branch("multiplicity_direct_by_species",
              multiplicityDirectBySpecies,
              "multiplicity_direct_by_species[5]/I");
  tree.Branch("multiplicity_strong_em_by_species",
              multiplicityStrongEmBySpecies,
              "multiplicity_strong_em_by_species[5]/I");
  tree.Branch("hard_indices", &hardIndices);
  tree.Branch("hard_bottom_indices", &hardBottomIndices);
  tree.Branch("hard_ids", &hardIds);

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
  tree.Branch("MULTIPLICITY", &multiplicity, "MULTIPLICITY/I");
  tree.Branch("PROCESSCODE", &processCode, "PROCESSCODE/I");
  tree.Branch("NCHARM", &nCharmOnly, "NCHARM/I");
  tree.Branch("NBEAUTY", &nBeautyOnly, "NBEAUTY/I");
  tree.Branch("NBC", &nBc, "NBC/I");

#define BRANCH_VECTOR(name) tree.Branch(#name, &name)
  BRANCH_VECTOR(heavyIndex);
  BRANCH_VECTOR(heavyPdg);
  BRANCH_VECTOR(heavyStatus);
  BRANCH_VECTOR(heavyStatusAbs);
  BRANCH_VECTOR(heavyIsFinal);
  BRANCH_VECTOR(heavyIsMeson);
  BRANCH_VECTOR(heavyIsBaryon);
  BRANCH_VECTOR(heavyCharge3);
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
  BRANCH_VECTOR(heavyOriginC);
  BRANCH_VECTOR(heavyOriginB);
  BRANCH_VECTOR(heavyMatchResolutionC);
  BRANCH_VECTOR(heavyMatchResolutionB);
  BRANCH_VECTOR(heavyMatchedHardC);
  BRANCH_VECTOR(heavyMatchedHardB);
  BRANCH_VECTOR(heavyOriginDepthC);
  BRANCH_VECTOR(heavyOriginDepthB);
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
  BRANCH_VECTOR(multAuditPdg);
  BRANCH_VECTOR(multAuditStatus);
  BRANCH_VECTOR(multAuditHasWeakAncestor);
  BRANCH_VECTOR(multAuditPt);
  BRANCH_VECTOR(multAuditEta);
#undef BRANCH_VECTOR

  TH1D hMultiplicity("hMULTIPLICITY",
                     "NCH_HADRONISATION_V1;N_{ch};successful events",
                     4096, -0.5, 4095.5);
  hMultiplicity.Sumw2();
  TH1D hMultiplicityStrongEm(
      "hMULTIPLICITY_FINAL_STRONG_EM_V1",
      "NCH_FINAL_STRONG_EM_V1;N_{ch};successful events", 4096, -0.5, 4095.5);
  hMultiplicityStrongEm.Sumw2();
  TH1I hProcessCode("hPROCESS_CODE", "hard process code;code;events", 1000, -0.5,
                    999.5);

  std::uint64_t attempts = 0;
  std::uint64_t successes = 0;
  std::uint64_t failures = 0;
  double sumWeights = 0.0;
  double sumWeights2 = 0.0;
  std::map<int, std::uint64_t> processCounts;
  std::uint64_t multiplicityOverflow = 0;
  std::uint64_t multiplicityStrongEmOverflow = 0;
  std::uint64_t contentDecodeFailures = 0;

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
    hardChannel = HardChannel(hardPartons);
    hardIndices.clear();
    hardBottomIndices.clear();
    hardIds.clear();
    for (const auto& hard : hardPartons) {
      hardIndices.push_back(hard.rootIndex);
      hardBottomIndices.push_back(hard.bottomIndex);
      hardIds.push_back(hard.id);
    }

    multiplicity = 0;
    multiplicityStrongEm = 0;
    nCharmOnly = 0;
    nBeautyOnly = 0;
    nBc = 0;
    std::fill(std::begin(multiplicityDirectBySpecies),
              std::end(multiplicityDirectBySpecies), 0);
    std::fill(std::begin(multiplicityStrongEmBySpecies),
              std::end(multiplicityStrongEmBySpecies), 0);

#define CLEAR_VECTOR(name) name.clear()
    CLEAR_VECTOR(legacyId); CLEAR_VECTOR(legacyClass); CLEAR_VECTOR(legacyPt);
    CLEAR_VECTOR(legacyEta); CLEAR_VECTOR(legacyY); CLEAR_VECTOR(legacyPhi);
    CLEAR_VECTOR(legacyCharge); CLEAR_VECTOR(legacyStatus);
    CLEAR_VECTOR(legacyMother); CLEAR_VECTOR(legacyMotherId);
    CLEAR_VECTOR(heavyIndex); CLEAR_VECTOR(heavyPdg); CLEAR_VECTOR(heavyStatus);
    CLEAR_VECTOR(heavyStatusAbs); CLEAR_VECTOR(heavyIsFinal);
    CLEAR_VECTOR(heavyIsMeson); CLEAR_VECTOR(heavyIsBaryon);
    CLEAR_VECTOR(heavyCharge3); CLEAR_VECTOR(heavyMother1);
    CLEAR_VECTOR(heavyMother2); CLEAR_VECTOR(heavyDaughter1);
    CLEAR_VECTOR(heavyDaughter2); CLEAR_VECTOR(heavyMotherOffsets);
    CLEAR_VECTOR(heavyMothers); CLEAR_VECTOR(heavyNc); CLEAR_VECTOR(heavyNcbar);
    CLEAR_VECTOR(heavyNb); CLEAR_VECTOR(heavyNbbar); CLEAR_VECTOR(heavyQc);
    CLEAR_VECTOR(heavyQb); CLEAR_VECTOR(heavyBaryonNumber);
    CLEAR_VECTOR(heavyStrangeness); CLEAR_VECTOR(heavyCentral);
    CLEAR_VECTOR(heavyOpen); CLEAR_VECTOR(heavyHidden);
    CLEAR_VECTOR(heavyOriginC); CLEAR_VECTOR(heavyOriginB);
    CLEAR_VECTOR(heavyMatchResolutionC);
    CLEAR_VECTOR(heavyMatchResolutionB);
    CLEAR_VECTOR(heavyMatchedHardC); CLEAR_VECTOR(heavyMatchedHardB);
    CLEAR_VECTOR(heavyOriginDepthC); CLEAR_VECTOR(heavyOriginDepthB);
    CLEAR_VECTOR(heavyPx); CLEAR_VECTOR(heavyPy); CLEAR_VECTOR(heavyPz);
    CLEAR_VECTOR(heavyE); CLEAR_VECTOR(heavyPt); CLEAR_VECTOR(heavyEta);
    CLEAR_VECTOR(heavyY); CLEAR_VECTOR(heavyPhi); CLEAR_VECTOR(heavyMass);
    CLEAR_VECTOR(ancestryIndex); CLEAR_VECTOR(ancestryPdg);
    CLEAR_VECTOR(ancestryStatus); CLEAR_VECTOR(ancestryMother1);
    CLEAR_VECTOR(ancestryMother2);
    CLEAR_VECTOR(multAuditPdg); CLEAR_VECTOR(multAuditStatus);
    CLEAR_VECTOR(multAuditHasWeakAncestor); CLEAR_VECTOR(multAuditPt);
    CLEAR_VECTOR(multAuditEta);
#undef CLEAR_VECTOR
    heavyMotherOffsets.push_back(0);
    std::set<int> ancestryNodes;

    for (int index = 0; index < pythia.event.size(); ++index) {
      const Particle& particle = pythia.event[index];
      const int id = particle.id();
      const int absId = std::abs(id);
      if (particle.isFinal() && IsMultiplicitySpecies(absId)) {
        const bool hasWeakAncestor = HasWeakAncestor(pythia.event, index);
        if (successes < multiplicityAuditEvents) {
          multAuditPdg.push_back(id);
          multAuditStatus.push_back(particle.status());
          multAuditHasWeakAncestor.push_back(hasWeakAncestor ? 1 : 0);
          multAuditPt.push_back(particle.pT());
          multAuditEta.push_back(particle.eta());
        }
        if (particle.pT() > 0.15 && std::abs(particle.eta()) <= 4.0) {
          const int speciesIndex = MultiplicitySpeciesIndex(absId);
          if (IsDirectPrimaryStatus(particle.status())) {
            ++multiplicity;
            ++multiplicityDirectBySpecies[speciesIndex];
          }
          if (!hasWeakAncestor) {
            ++multiplicityStrongEm;
            ++multiplicityStrongEmBySpecies[speciesIndex];
          }
        }
      }

      if (!pythia.particleData.isHadron(id)) continue;
      const int pythiaCharm = pythia.particleData.nQuarksInCode(id, 4);
      const int pythiaBeauty = pythia.particleData.nQuarksInCode(id, 5);
      if (pythiaCharm == 0 && pythiaBeauty == 0) continue;

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
      CollectOriginAuditNodes(
          pythia.event, index, 4,
          content.qc() > 0 ? 1 : (content.qc() < 0 ? -1 : 0),
          ancestryNodes);
      CollectOriginAuditNodes(
          pythia.event, index, 5,
          content.qb() > 0 ? 1 : (content.qb() < 0 ? -1 : 0),
          ancestryNodes);
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
      heavyMother1.push_back(particle.mother1());
      heavyMother2.push_back(particle.mother2());
      heavyDaughter1.push_back(particle.daughter1());
      heavyDaughter2.push_back(particle.daughter2());
      for (const int mother : particle.motherList()) heavyMothers.push_back(mother);
      heavyMotherOffsets.push_back(static_cast<int>(heavyMothers.size()));
      heavyNc.push_back(content.nc);
      heavyNcbar.push_back(content.ncbar);
      heavyNb.push_back(content.nb);
      heavyNbbar.push_back(content.nbbar);
      heavyQc.push_back(content.qc());
      heavyQb.push_back(content.qb());
      heavyBaryonNumber.push_back(
          pythia.particleData.baryonNumberType(id));
      heavyStrangeness.push_back(content.strangeness());
      heavyCentral.push_back(FindGroundState(id) ? 1 : 0);
      heavyOpen.push_back((content.qc() != 0 || content.qb() != 0) ? 1 : 0);
      heavyHidden.push_back(
          (content.hiddenCharm() || content.hiddenBeauty()) ? 1 : 0);
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

    for (const int index : ancestryNodes) {
      const Particle& ancestor = pythia.event[index];
      ancestryIndex.push_back(index);
      ancestryPdg.push_back(ancestor.id());
      ancestryStatus.push_back(ancestor.status());
      ancestryMother1.push_back(ancestor.mother1());
      ancestryMother2.push_back(ancestor.mother2());
    }

    hMultiplicity.Fill(multiplicity, eventWeight);
    hMultiplicityStrongEm.Fill(multiplicityStrongEm, eventWeight);
    if (multiplicity > 4095) ++multiplicityOverflow;
    if (multiplicityStrongEm > 4095) ++multiplicityStrongEmOverflow;
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
  const bool complete = successes == requestedSuccesses &&
                        attempts == successes + failures &&
                        static_cast<std::uint64_t>(tree.GetEntries()) == successes;

  output.cd();
  tree.Write();
  hMultiplicity.Write();
  hMultiplicityStrongEm.Write();
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
  stability.Branch("open_heavy", &stabilityValue.openHeavy, "open_heavy/I");
  stability.Branch("hidden_heavy", &stabilityValue.hiddenHeavy,
                   "hidden_heavy/I");
  stability.Branch("central_registry", &stabilityValue.central,
                   "central_registry/I");
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
      "post-init values for every explicitly configured PYTHIA setting");
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
  TTree metadata("job_metadata", "immutable logical-attempt metadata");
  std::string rawSchema = kRawSchema;
  std::string selector = kSelectorVersion;
  std::string originAlgorithm = kOriginAlgorithmVersion;
  std::string speciesSchema(kSpeciesRegistrySchema);
  std::string speciesSha(kSpeciesRegistrySha256);
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
  ULong64_t multStrongOverflow = multiplicityStrongEmOverflow;
  ULong64_t decodeFailures = contentDecodeFailures;
  ULong64_t multiplicityAuditEventCount = multiplicityAuditEvents;
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
  metadata.Branch("multiplicity_overflow", &multOverflow,
                  "multiplicity_overflow/l");
  metadata.Branch("multiplicity_strong_em_overflow", &multStrongOverflow,
                  "multiplicity_strong_em_overflow/l");
  metadata.Branch("content_decode_failures", &decodeFailures,
                  "content_decode_failures/l");
  metadata.Branch("multiplicity_audit_events", &multiplicityAuditEventCount,
                  "multiplicity_audit_events/l");
  metadata.Branch("elapsed_seconds", &elapsed, "elapsed_seconds/L");
  metadata.Branch("host", &host);
  metadata.Branch("condor_cluster", &condorCluster);
  metadata.Branch("condor_process", &condorProcess);
  metadata.Branch("complete", &completeFlag, "complete/I");
  metadata.Fill();
  metadata.Write();

  TObjString settingsObject(effectiveSettings.c_str());
  settingsObject.Write("effective_changed_settings");
  TObjString statisticsObject(pythiaStatistics.c_str());
  statisticsObject.Write("pythia_statistics");
  TObjString multiplicityCentral(kMultiplicityCentral);
  multiplicityCentral.Write("multiplicity_central_version");
  TObjString multiplicityCrossCheck(kMultiplicityCrossCheck);
  multiplicityCrossCheck.Write("multiplicity_crosscheck_version");
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
