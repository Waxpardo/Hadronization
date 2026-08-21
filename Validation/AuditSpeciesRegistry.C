#include "../generation/registries/GeneratedHeavyFlavourRegistry.h"
#include "../generation/producer/HeavyFlavourUtils.h"

#include <Pythia8/Pythia.h>

#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <set>
#include <string>

namespace {

std::string CsvField(const std::string& value) {
  std::string escaped;
  escaped.reserve(value.size() + 2);
  escaped.push_back('"');
  for (const char character : value) {
    if (character == '"') escaped.push_back('"');
    escaped.push_back(character);
  }
  escaped.push_back('"');
  return escaped;
}

}  // namespace

int AuditSpeciesRegistry(
    const char* outputCsv = "species_registry_pythia_audit.csv") {
  Pythia8::Pythia pythia;
  int errors = 0;
  std::set<int> observed;
  std::ofstream csv(outputCsv);
  if (!csv) {
    std::cerr << "SPECIES_REGISTRY_ERROR cannot open output=" << outputCsv
              << "\n";
    return 1;
  }
  csv << "pdg,registry_name,pythia_name,pythia_conjugate_name,sector,kind,"
         "charge3,spin2j1,is_hadron,is_meson,is_baryon,has_antiparticle,"
         "n_down_in_code,n_up_in_code,n_strange_in_code,n_charm_in_code,"
         "n_beauty_in_code,decoded_qc,decoded_qb,"
         "mass_gev,pythia_result\n";
  csv << std::setprecision(17);
  for (const auto& state : Hadronization::kGroundStates) {
    bool valid = true;
    const bool isParticle = pythia.particleData.isParticle(state.pdg);
    const bool isHadron = pythia.particleData.isHadron(state.pdg);
    const bool isMeson = pythia.particleData.isMeson(state.pdg);
    const bool isBaryon = pythia.particleData.isBaryon(state.pdg);
    const auto entry =
        pythia.particleData.particleDataEntryPtr(std::abs(state.pdg));
    const bool hasAntiparticle = entry && entry->hasAnti();
    const std::string pythiaName =
        isParticle ? pythia.particleData.name(state.pdg) : "";
    const std::string conjugateName =
        pythia.particleData.isParticle(-state.pdg)
            ? pythia.particleData.name(-state.pdg)
            : "";
    const double mass = entry ? entry->m0() : 0.0;
    if (!observed.insert(state.pdg).second ||
        !isParticle || !isHadron ||
        (state.kind == "meson" && !isMeson) ||
        (state.kind == "baryon" && !isBaryon) ||
        pythia.particleData.chargeType(state.pdg) != state.charge3 ||
        pythia.particleData.spinType(state.pdg) != state.spin2j1 ||
        !hasAntiparticle || pythiaName.empty() || conjugateName.empty() ||
        !std::isfinite(mass) || mass <= 0.0) {
      valid = false;
    }
    const int down = pythia.particleData.nQuarksInCode(state.pdg, 1);
    const int up = pythia.particleData.nQuarksInCode(state.pdg, 2);
    const int strange = pythia.particleData.nQuarksInCode(state.pdg, 3);
    const int charm = pythia.particleData.nQuarksInCode(state.pdg, 4);
    const int beauty = pythia.particleData.nQuarksInCode(state.pdg, 5);
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
    csv << state.pdg << ',' << CsvField(std::string(state.name)) << ','
        << CsvField(pythiaName) << ',' << CsvField(conjugateName) << ','
        << state.sector << ',' << state.kind << ',' << state.charge3 << ','
        << state.spin2j1 << ',' << (isHadron ? 1 : 0) << ','
        << (isMeson ? 1 : 0) << ',' << (isBaryon ? 1 : 0) << ','
        << (hasAntiparticle ? 1 : 0) << ',' << down << ',' << up << ','
        << strange << ',' << charm << ',' << beauty << ',' << content.qc()
        << ',' << content.qb() << ',' << mass << ','
        << (valid ? "PASS" : "FAIL") << "\n";
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
