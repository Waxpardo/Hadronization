// Selected-state implementation view of config/study.json.
#ifndef HADRONIZATION_GENERATED_HEAVY_FLAVOUR_REGISTRY_H
#define HADRONIZATION_GENERATED_HEAVY_FLAVOUR_REGISTRY_H

#include <array>
#include <string_view>

namespace Hadronization {
inline constexpr std::string_view kSpeciesRegistrySchema =
    "hadronization_study_v1:selected_states";
inline constexpr std::string_view kSpeciesRegistrySha256 =
    "694bc8c32d7be18e57abd8629ed76de2d09ccfdf25d87c3c9df4a4472c34354d";

struct SelectedState {
  int pdg;
  std::string_view name;
  std::string_view sector;
  std::string_view kind;
  int spin2j1;
  int charge3;
  int qc;
  int qb;
  // false => produced, stored and analysed normally, but excluded from
  // central published results pending physics review. See
  // config/heavy_flavour_species_v1.json for the per-state reason.
  bool centralEligible;
};

inline constexpr std::array<SelectedState, 50> kSelectedStates{{
  {421, "D0", "charm", "meson", 1, 0, 1, 0, true},
  {-421, "D0bar", "charm", "meson", 1, 0, -1, 0, true},
  {411, "Dplus", "charm", "meson", 1, 3, 1, 0, true},
  {-411, "Dminus", "charm", "meson", 1, -3, -1, 0, true},
  {431, "Dsplus", "charm", "meson", 1, 3, 1, 0, true},
  {-431, "Dsminus", "charm", "meson", 1, -3, -1, 0, true},
  {4122, "Lambdacplus", "charm", "baryon", 2, 3, 1, 0, true},
  {-4122, "Lambdacplusbar", "charm", "baryon", 2, -3, -1, 0, true},
  {4112, "Sigmaczero", "charm", "baryon", 2, 0, 1, 0, true},
  {-4112, "Sigmaczerobar", "charm", "baryon", 2, 0, -1, 0, true},
  {4212, "Sigmacplus", "charm", "baryon", 2, 3, 1, 0, true},
  {-4212, "Sigmacplusbar", "charm", "baryon", 2, -3, -1, 0, true},
  {4222, "Sigmacplusplus", "charm", "baryon", 2, 6, 1, 0, true},
  {-4222, "Sigmacplusplusbar", "charm", "baryon", 2, -6, -1, 0, true},
  {4132, "Xiczero", "charm", "baryon", 2, 0, 1, 0, true},
  {-4132, "Xiczerobar", "charm", "baryon", 2, 0, -1, 0, true},
  {4232, "Xicplus", "charm", "baryon", 2, 3, 1, 0, true},
  {-4232, "Xicplusbar", "charm", "baryon", 2, -3, -1, 0, true},
  {4312, "Xicprimezero", "charm", "baryon", 2, 0, 1, 0, true},
  {-4312, "Xicprimezerobar", "charm", "baryon", 2, 0, -1, 0, true},
  {4322, "Xicprimeplus", "charm", "baryon", 2, 3, 1, 0, true},
  {-4322, "Xicprimeplusbar", "charm", "baryon", 2, -3, -1, 0, true},
  {4332, "Omegaczero", "charm", "baryon", 2, 0, 1, 0, true},
  {-4332, "Omegaczerobar", "charm", "baryon", 2, 0, -1, 0, true},
  {511, "Bzero", "beauty", "meson", 1, 0, 0, -1, true},
  {-511, "Bzerobar", "beauty", "meson", 1, 0, 0, 1, true},
  {521, "Bplus", "beauty", "meson", 1, 3, 0, -1, true},
  {-521, "Bminus", "beauty", "meson", 1, -3, 0, 1, true},
  {531, "Bszero", "beauty", "meson", 1, 0, 0, -1, true},
  {-531, "Bszerobar", "beauty", "meson", 1, 0, 0, 1, true},
  {541, "Bcplus", "beauty", "meson", 1, 3, 1, -1, true},
  {-541, "Bcminus", "beauty", "meson", 1, -3, -1, 1, true},
  {5122, "Lambdabzero", "beauty", "baryon", 2, 0, 0, 1, true},
  {-5122, "Lambdabzerobar", "beauty", "baryon", 2, 0, 0, -1, true},
  {5112, "Sigmabminus", "beauty", "baryon", 2, -3, 0, 1, true},
  {-5112, "Sigmabminusbar", "beauty", "baryon", 2, 3, 0, -1, true},
  {5212, "Sigmabzero", "beauty", "baryon", 2, 0, 0, 1, false},
  {-5212, "Sigmabzerobar", "beauty", "baryon", 2, 0, 0, -1, false},
  {5222, "Sigmabplus", "beauty", "baryon", 2, 3, 0, 1, true},
  {-5222, "Sigmabplusbar", "beauty", "baryon", 2, -3, 0, -1, true},
  {5132, "Xibminus", "beauty", "baryon", 2, -3, 0, 1, true},
  {-5132, "Xibminusbar", "beauty", "baryon", 2, 3, 0, -1, true},
  {5232, "Xibzero", "beauty", "baryon", 2, 0, 0, 1, true},
  {-5232, "Xibzerobar", "beauty", "baryon", 2, 0, 0, -1, true},
  {5312, "Xibprimeminus", "beauty", "baryon", 2, -3, 0, 1, false},
  {-5312, "Xibprimeminusbar", "beauty", "baryon", 2, 3, 0, -1, false},
  {5322, "Xibprimezero", "beauty", "baryon", 2, 0, 0, 1, false},
  {-5322, "Xibprimezerobar", "beauty", "baryon", 2, 0, 0, -1, false},
  {5332, "Omegabminus", "beauty", "baryon", 2, -3, 0, 1, true},
  {-5332, "Omegabminusbar", "beauty", "baryon", 2, 3, 0, -1, true},
}};

inline const SelectedState* FindSelectedState(int pdg) {
  for (const auto& state : kSelectedStates) {
    if (state.pdg == pdg) return &state;
  }
  return nullptr;
}

// A state excluded from central results. Callers that build published central
// figures must skip these; completeness checks keep them available.
inline bool IsCentralEligible(int signedPdg) {
  const SelectedState* state = FindSelectedState(signedPdg);
  return state != nullptr && state->centralEligible;
}

}  // namespace Hadronization
#endif
