#include "../SimulationScripts/GeneratedHeavyFlavourRegistry.h"
#include "../SimulationScripts/HeavyFlavourUtils.h"

#include <Pythia8/Pythia.h>

#include <fstream>
#include <iostream>
#include <set>
#include <string>

int AuditSpeciesRegistry(
    const char* outputCsv = "species_registry_pythia_audit.csv") {
  Pythia8::Pythia pythia;
  int errors = 0;
  std::set<int> observed;
  std::ofstream csv(outputCsv);
  csv << "pdg,name,sector,kind,charge3,spin2j1,nCharm,nBeauty,result\n";
  for (const auto& state : Hadronization::kGroundStates) {
    bool valid = true;
    if (!observed.insert(state.pdg).second ||
        !pythia.particleData.isParticle(state.pdg) ||
        !pythia.particleData.isHadron(state.pdg) ||
        (state.kind == "meson" &&
         !pythia.particleData.isMeson(state.pdg)) ||
        (state.kind == "baryon" &&
         !pythia.particleData.isBaryon(state.pdg)) ||
        pythia.particleData.chargeType(state.pdg) != state.charge3 ||
        pythia.particleData.spinType(state.pdg) != state.spin2j1) {
      valid = false;
    }
    const int charm =
        pythia.particleData.nQuarksInCode(state.pdg, 4);
    const int beauty =
        pythia.particleData.nQuarksInCode(state.pdg, 5);
    const auto content = Hadronization::DecodeHeavyContent(
        state.pdg, pythia.particleData.isMeson(state.pdg),
        pythia.particleData.isBaryon(state.pdg));
    if (content.qc() != state.qc || content.qb() != state.qb ||
        (std::abs(state.qc) > 0 && charm == 0) ||
        (std::abs(state.qb) > 0 && beauty == 0)) {
      valid = false;
    }
    if (!Hadronization::FindGroundState(-state.pdg)) valid = false;
    if (!valid) {
      std::cerr << "SPECIES_REGISTRY_ERROR pdg=" << state.pdg
                << " name=" << state.name << "\n";
      ++errors;
    }
    csv << state.pdg << ',' << state.name << ',' << state.sector << ','
        << state.kind << ',' << state.charge3 << ',' << state.spin2j1 << ','
        << charm << ',' << beauty << ',' << (valid ? "PASS" : "FAIL")
        << "\n";
  }
  for (const int explicitlyExcited :
       {413, -413, 423, -423, 433, -433, 513, -513, 523, -523, 533,
        -533, 543, -543, 4114, -4114, 4224, -4224, 4334, -4334, 5114,
        -5114, 5224, -5224, 5334, -5334}) {
    if (Hadronization::FindGroundState(explicitlyExcited)) {
      std::cerr << "SPECIES_REGISTRY_ERROR excited state included pdg="
                << explicitlyExcited << "\n";
      ++errors;
    }
  }
  std::cout << "SPECIES_REGISTRY_AUDIT errors=" << errors
            << " signed_states=" << Hadronization::kGroundStates.size()
            << " pythia_version=" << PYTHIA_VERSION << " csv=" << outputCsv
            << "\n";
  return errors;
}
