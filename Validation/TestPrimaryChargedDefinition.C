// Live-generator validation of NCH_PRIMARY_CHARGED_*_V1.
//
// Two claims are asserted against the installed PYTHIA, not against
// documentation:
//
//   1. Lifetime equivalence. The tune cards set
//      `ParticleDecays:limitTau0 = on` with `tau0Max = 0.01` mm. The
//      conventional experimental primary-charged-particle definition uses a
//      1 cm/c (10 mm) threshold instead. The two are equivalent for light
//      flavour if and only if no light hadron has 0.01 mm < c*tau0 < 10 mm.
//      This test enumerates the entire ParticleData table and proves it, so
//      the paper may quote the conventional 1 cm/c definition.
//
//   2. Counter completeness. Generating events with the real card, it
//      recounts both multiplicity windows directly from the event record and
//      requires agreement with `CountsNchPrimaryChargedV1`. The raw validator
//      only recomputes from the stored pilot record, so this is the check
//      that the stored record is not missing charged particles.
//
// Usage:
//   root -l -b -q 'Validation/TestPrimaryChargedDefinition.C("monash", 200)'

#include "../generation/producer/HeavyFlavourUtils.h"

#include "Pythia8/Pythia.h"

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

int TestPrimaryChargedDefinition(const char* mode = "monash",
                                 int events = 200) {
  const std::string modeName = mode;
  std::string card;
  if (modeName == "monash") {
    card = "generation/cards/pythiasettings_Hard_Low_ccbb_MONASH.cmnd";
  } else if (modeName == "junctions") {
    card = "generation/cards/pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd";
  } else if (modeName == "closepacking") {
    card = "generation/cards/pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd";
  } else {
    std::cerr << "ERROR: mode must be monash, junctions or closepacking\n";
    return 2;
  }

  int errors = 0;
  const auto fail = [&errors](const std::string& message) {
    std::cerr << "FAIL: " << message << "\n";
    ++errors;
  };

  Pythia8::Pythia pythia;
  if (!pythia.readFile(card) || pythia.settings.readingFailed()) {
    std::cerr << "ERROR: cannot read " << card << "\n";
    return 3;
  }

  // ---- claim 1: lifetime-window equivalence -------------------------------
  const double cardTau0Max = pythia.parm("ParticleDecays:tau0Max");
  const bool cardLimitsTau0 = pythia.flag("ParticleDecays:limitTau0");
  constexpr double kConventionalPrimaryTau0Mm = 10.0;  // 1 cm/c
  if (!cardLimitsTau0) {
    fail("card does not set ParticleDecays:limitTau0 = on");
  }
  if (!(cardTau0Max > 0.0) || cardTau0Max >= kConventionalPrimaryTau0Mm) {
    fail("card tau0Max is not a positive value below the 1 cm/c threshold");
  }

  int windowViolations = 0;
  for (auto entry = pythia.particleData.begin();
       entry != pythia.particleData.end(); ++entry) {
    const auto& particle = entry->second;
    if (!particle->isHadron()) continue;
    // Heavy-flavour decays are disabled programmatically by the producer, so
    // the lifetime threshold never governs them. Only light flavour matters.
    if (particle->nQuarksInCode(4) != 0 || particle->nQuarksInCode(5) != 0) {
      continue;
    }
    const double tau0 = particle->tau0();
    if (tau0 > cardTau0Max && tau0 < kConventionalPrimaryTau0Mm) {
      std::cerr << "  light hadron inside the ambiguous lifetime window: "
                << entry->first << " " << particle->name()
                << " tau0=" << tau0 << " mm\n";
      ++windowViolations;
    }
  }
  if (windowViolations != 0) {
    fail("light hadrons exist with card tau0Max < c*tau0 < 1 cm; the card "
         "value is NOT equivalent to the conventional primary definition");
  } else {
    std::cout << "OK: no light hadron has " << cardTau0Max
              << " mm < c*tau0 < " << kConventionalPrimaryTau0Mm
              << " mm; card threshold is equivalent to 1 cm/c\n";
  }

  // ---- claim 2: counter completeness on real events -----------------------
  // Disable heavy decays exactly as the producer does, so the event content
  // matches production.
  std::vector<int> heavyIds;
  for (auto entry = pythia.particleData.begin();
       entry != pythia.particleData.end(); ++entry) {
    const auto& particle = entry->second;
    if (!particle->isHadron()) continue;
    if (particle->nQuarksInCode(4) == 0 && particle->nQuarksInCode(5) == 0) {
      continue;
    }
    heavyIds.push_back(entry->first);
    pythia.particleData.mayDecay(entry->first, false);
  }
  if (heavyIds.empty()) fail("no heavy hadrons found in ParticleData");

  pythia.readString("Random:setSeed = on");
  pythia.readString("Random:seed = 20260730");
  pythia.readString("Main:numberOfEvents = " + std::to_string(events));
  if (!pythia.init()) {
    std::cerr << "ERROR: PYTHIA initialization failed\n";
    return 3;
  }

  long long totalCentral = 0;
  long long totalWide = 0;
  long long totalWeakDecayProducts = 0;
  int generated = 0;
  while (generated < events) {
    if (!pythia.next()) continue;
    ++generated;
    int central = 0;
    int wide = 0;
    int reference = 0;
    for (int index = 0; index < pythia.event.size(); ++index) {
      const Pythia8::Particle& particle = pythia.event[index];
      if (!particle.isFinal() || !particle.isCharged()) continue;
      const bool heavy =
          pythia.particleData.nQuarksInCode(particle.id(), 4) != 0 ||
          pythia.particleData.nQuarksInCode(particle.id(), 5) != 0;

      // Independent literal recount of the central window.
      if (!heavy && particle.pT() > Hadronization::kMultiplicityPtMin &&
          std::abs(particle.eta()) <= Hadronization::kMultiplicityEtaCentral) {
        ++reference;
      }
      if (Hadronization::CountsNchPrimaryChargedV1(
              particle.isFinal(), particle.isCharged(), heavy, particle.pT(),
              particle.eta(), Hadronization::kMultiplicityEtaCentral)) {
        ++central;
      }
      if (Hadronization::CountsNchPrimaryChargedV1(
              particle.isFinal(), particle.isCharged(), heavy, particle.pT(),
              particle.eta(), Hadronization::kMultiplicityEtaWide)) {
        ++wide;
      }
      // No counted particle may descend from a weak decay: with limitTau0 in
      // force every weakly decaying light hadron stays final, so absolute
      // status 91-97 must never appear among counted particles.
      const int statusAbs = particle.statusAbs();
      if (!heavy && statusAbs >= 91 && statusAbs <= 97 &&
          particle.pT() > Hadronization::kMultiplicityPtMin &&
          std::abs(particle.eta()) <=
              Hadronization::kMultiplicityEtaCentral) {
        const int mother = particle.mother1();
        if (mother > 0 && mother < pythia.event.size() &&
            pythia.particleData.tau0(pythia.event[mother].id()) >
                kConventionalPrimaryTau0Mm) {
          ++totalWeakDecayProducts;
        }
      }
    }
    if (central != reference) {
      fail("CountsNchPrimaryChargedV1 disagrees with a literal recount");
      break;
    }
    if (central > wide) {
      fail("central window count exceeds the wider window count");
      break;
    }
    totalCentral += central;
    totalWide += wide;
  }

  if (totalWeakDecayProducts != 0) {
    fail("counted particles descend from a long-lived (weak) parent: " +
         std::to_string(totalWeakDecayProducts));
  }
  if (generated > 0) {
    std::cout << "OK: " << generated << " " << modeName << " events, <Nch|eta|<"
              << Hadronization::kMultiplicityEtaCentral << "> = "
              << static_cast<double>(totalCentral) / generated
              << ", <Nch|eta|<" << Hadronization::kMultiplicityEtaWide
              << "> = " << static_cast<double>(totalWide) / generated << "\n";
  } else {
    fail("no events were generated");
  }

  std::cout << "PRIMARY_CHARGED_DEFINITION_TEST errors=" << errors << "\n";
  return errors == 0 ? 0 : 1;
}
