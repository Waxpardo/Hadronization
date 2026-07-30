#include "../SimulationScripts/HeavyFlavourUtils.h"

#include <iostream>
#include <stdexcept>
#include <vector>

int TestHardCarrierUniqueness() {
  using Hadronization::CarrierUniquenessResult;
  using Hadronization::EnforceUniqueFinalHardCarrier;
  using Hadronization::MatchResolution;
  using Hadronization::Origin;

  std::vector<int> isFinal{1, 1, 1, 0, 1};
  std::vector<int> charge{1, 1, -1, -1, 1};
  std::vector<int> origin{
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kShower)};
  std::vector<int> resolution{
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kUnique)};
  std::vector<int> matchedHard{5, 5, 6, 6, -1};

  const CarrierUniquenessResult result = EnforceUniqueFinalHardCarrier(
      isFinal, charge, origin, resolution, matchedHard);
  if (result.conflictGroups != 1 || result.demotedMatches != 2) return 1;
  for (int index : {0, 1}) {
    if (origin[index] != static_cast<int>(Origin::kUnresolved) ||
        resolution[index] !=
            static_cast<int>(MatchResolution::kDuplicateHardCarrier) ||
        matchedHard[index] != -1) {
      return 2;
    }
  }
  if (origin[2] != static_cast<int>(Origin::kSelectedHard) ||
      matchedHard[2] != 6 || origin[3] != static_cast<int>(Origin::kSelectedHard) ||
      matchedHard[3] != 6 || origin[4] != static_cast<int>(Origin::kShower)) {
    return 3;
  }

  bool rejectedMismatchedVectors = false;
  try {
    std::vector<int> shortCharge{1};
    EnforceUniqueFinalHardCarrier(isFinal, shortCharge, origin, resolution,
                                  matchedHard);
  } catch (const std::invalid_argument&) {
    rejectedMismatchedVectors = true;
  }
  if (!rejectedMismatchedVectors) return 4;

  std::cout << "HARD_CARRIER_UNIQUENESS_TEST_PASS conflict_groups="
            << result.conflictGroups
            << " demoted_matches=" << result.demotedMatches << "\n";
  return 0;
}
