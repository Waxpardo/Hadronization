#include "../generation/producer/HeavyFlavourUtils.h"

#include <iostream>
#include <stdexcept>
#include <vector>

int TestHardCarrierUniqueness() {
  using Hadronization::CarrierUniquenessResult;
  using Hadronization::EnforceUniqueFinalConstituentHardCarrier;
  using Hadronization::EnforceUniqueFinalHardCarrier;
  using Hadronization::HeavyContent;
  using Hadronization::HeavyStateCategory;
  using Hadronization::MatchResolution;
  using Hadronization::Origin;
  using Hadronization::RejectFinalMultiHeavyCarrier;

  // Two independent collision groups: one three-way and one two-way. A
  // non-final claim to the second carrier is intentionally outside the final
  // state uniqueness invariant.
  std::vector<int> isFinal{1, 1, 1, 1, 1, 0, 1};
  std::vector<int> charge{1, 1, 1, -1, -1, -1, 0};
  std::vector<int> origin{
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kUnresolved)};
  std::vector<int> resolution{
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kNotApplicable)};
  std::vector<int> matchedHard{5, 5, 5, 6, 6, 6, -1};

  const CarrierUniquenessResult result = EnforceUniqueFinalHardCarrier(
      isFinal, charge, origin, resolution, matchedHard);
  if (result.conflictGroups != 2 || result.demotedMatches != 5) return 1;
  for (int index : {0, 1, 2, 3, 4}) {
    if (origin[index] != static_cast<int>(Origin::kUnresolved) ||
        resolution[index] !=
            static_cast<int>(MatchResolution::kDuplicateHardCarrier) ||
        matchedHard[index] != -1) {
      return 2;
    }
  }
  if (origin[5] != static_cast<int>(Origin::kSelectedHard) ||
      matchedHard[5] != 6 ||
      origin[6] != static_cast<int>(Origin::kUnresolved) ||
      resolution[6] != static_cast<int>(MatchResolution::kNotApplicable)) {
    return 3;
  }

  // Constituent rows are flattened, but uniqueness is a final-parent
  // invariant. Repeated same-sign rows within one multiply-heavy parent must
  // survive so the closure audit can identify that parent.
  std::vector<int> sameParentSlot{7, 7, 8};
  std::vector<int> sameParentFinal{1, 1, 1};
  std::vector<int> sameParentPdg{4, 4, -4};
  std::vector<int> sameParentOrigin(
      3, static_cast<int>(Origin::kSelectedHard));
  std::vector<int> sameParentResolution(
      3, static_cast<int>(MatchResolution::kUnique));
  std::vector<int> sameParentMatched{23, 23, 24};
  std::vector<int> sameParentRejected(3, -1);
  const CarrierUniquenessResult sameParentResult =
      EnforceUniqueFinalConstituentHardCarrier(
          sameParentSlot, sameParentFinal, sameParentPdg, sameParentOrigin,
          sameParentResolution, sameParentMatched, sameParentRejected);
  HeavyContent doubleCharm;
  doubleCharm.nc = 2;
  int closureCarrierParent = -1;
  for (std::size_t index = 0; index < sameParentSlot.size(); ++index) {
    if (sameParentPdg[index] != 4 ||
        sameParentOrigin[index] !=
            static_cast<int>(Origin::kSelectedHard) ||
        sameParentResolution[index] !=
            static_cast<int>(MatchResolution::kUnique) ||
        sameParentMatched[index] != 23) {
      continue;
    }
    if (closureCarrierParent >= 0 &&
        closureCarrierParent != sameParentSlot[index]) {
      return 4;
    }
    closureCarrierParent = sameParentSlot[index];
  }
  if (sameParentResult.conflictGroups != 0 ||
      sameParentResult.demotedMatches != 0 ||
      sameParentMatched[0] != 23 || sameParentMatched[1] != 23 ||
      closureCarrierParent != 7 ||
      Hadronization::ClassifyHeavyState(false, doubleCharm) !=
          HeavyStateCategory::kMultiplyHeavy) {
    return 4;
  }

  // Distinct final parents claiming hard index 23 are a real conflict.
  std::vector<int> distinctParentSlot{7, 7, 9, 8};
  std::vector<int> distinctParentFinal{1, 1, 1, 1};
  std::vector<int> distinctParentPdg{4, 4, 4, -4};
  std::vector<int> distinctParentOrigin(
      4, static_cast<int>(Origin::kSelectedHard));
  std::vector<int> distinctParentResolution(
      4, static_cast<int>(MatchResolution::kUnique));
  std::vector<int> distinctParentMatched{23, 23, 23, 24};
  std::vector<int> distinctParentRejected(4, -1);
  const CarrierUniquenessResult distinctParentResult =
      EnforceUniqueFinalConstituentHardCarrier(
          distinctParentSlot, distinctParentFinal, distinctParentPdg,
          distinctParentOrigin, distinctParentResolution,
          distinctParentMatched, distinctParentRejected);
  if (distinctParentResult.conflictGroups != 1 ||
      distinctParentResult.demotedMatches != 3 ||
      distinctParentMatched[0] != -1 || distinctParentMatched[1] != -1 ||
      distinctParentMatched[2] != -1 ||
      distinctParentRejected[0] != 23 ||
      distinctParentRejected[1] != 23 ||
      distinctParentRejected[2] != 23 ||
      distinctParentMatched[3] != 24) {
    return 5;
  }

  // Bc uses independent c and anti-b carrier assignments in the same parent.
  std::vector<int> bcParentSlot{4, 4};
  std::vector<int> bcParentFinal{1, 1};
  std::vector<int> bcConstituentPdg{4, -5};
  std::vector<int> bcConstituentOrigin(
      2, static_cast<int>(Origin::kSelectedHard));
  std::vector<int> bcConstituentResolution(
      2, static_cast<int>(MatchResolution::kUnique));
  std::vector<int> bcConstituentMatched{20, 21};
  std::vector<int> bcConstituentRejected(2, -1);
  const CarrierUniquenessResult bcConstituentResult =
      EnforceUniqueFinalConstituentHardCarrier(
          bcParentSlot, bcParentFinal, bcConstituentPdg, bcConstituentOrigin,
          bcConstituentResolution, bcConstituentMatched,
          bcConstituentRejected);
  if (bcConstituentResult.conflictGroups != 0 ||
      bcConstituentResult.demotedMatches != 0 ||
      bcConstituentMatched[0] != 20 || bcConstituentMatched[1] != 21) {
    return 6;
  }

  // Multi-heavy same-sector final states cannot be represented by one matched
  // index. Preserve a rejected candidate when one existed. Bc states remain
  // representable because charm and beauty are audited independently.
  std::vector<int> multiFinal{1, 1, 1, 1};
  std::vector<int> multiCharge{2, -2, 1, 0};
  std::vector<int> multiOrigin{
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kShower),
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kUnresolved)};
  std::vector<int> multiResolution{
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kUnique),
      static_cast<int>(MatchResolution::kNotApplicable)};
  std::vector<int> multiMatched{10, -1, 11, -1};
  std::vector<int> multiRejected(4, -1);
  if (RejectFinalMultiHeavyCarrier(
          multiFinal, multiCharge, multiOrigin, multiResolution, multiMatched,
          multiRejected) != 2) {
    return 7;
  }
  for (int index : {0, 1}) {
    if (multiOrigin[index] != static_cast<int>(Origin::kUnresolved) ||
        multiResolution[index] !=
            static_cast<int>(MatchResolution::kMultipleHeavyConstituents) ||
        multiMatched[index] != -1) {
      return 8;
    }
  }
  if (multiRejected[0] != 10 || multiRejected[1] != -1 ||
      multiOrigin[2] != static_cast<int>(Origin::kSelectedHard) ||
      multiMatched[2] != 11 ||
      multiResolution[3] != static_cast<int>(MatchResolution::kNotApplicable)) {
    return 9;
  }

  // If a multi-heavy state was already in a duplicate-carrier group, retain
  // the duplicate resolution so the complete group remains reconstructable.
  std::vector<int> overlapFinal{1, 1};
  std::vector<int> overlapCharge{2, 1};
  std::vector<int> overlapOrigin(2, static_cast<int>(Origin::kSelectedHard));
  std::vector<int> overlapResolution(2,
                                     static_cast<int>(MatchResolution::kUnique));
  std::vector<int> overlapMatched{12, 12};
  const std::vector<int> overlapOriginal = overlapMatched;
  const auto overlapResult = EnforceUniqueFinalHardCarrier(
      overlapFinal, overlapCharge, overlapOrigin, overlapResolution,
      overlapMatched);
  std::vector<int> overlapRejected = overlapOriginal;
  if (overlapResult.conflictGroups != 1 ||
      RejectFinalMultiHeavyCarrier(overlapFinal, overlapCharge, overlapOrigin,
                                   overlapResolution, overlapMatched,
                                   overlapRejected) != 1 ||
      overlapResolution[0] !=
          static_cast<int>(MatchResolution::kDuplicateHardCarrier)) {
    return 10;
  }

  std::vector<int> bcFinal{1};
  std::vector<int> bcCharmCharge{1};
  std::vector<int> bcBeautyCharge{-1};
  std::vector<int> bcCharmOrigin{static_cast<int>(Origin::kSelectedHard)};
  std::vector<int> bcBeautyOrigin{static_cast<int>(Origin::kSelectedHard)};
  std::vector<int> bcCharmResolution{
      static_cast<int>(MatchResolution::kUnique)};
  std::vector<int> bcBeautyResolution{
      static_cast<int>(MatchResolution::kUnique)};
  std::vector<int> bcCharmMatched{20};
  std::vector<int> bcBeautyMatched{21};
  std::vector<int> bcCharmRejected{-1};
  std::vector<int> bcBeautyRejected{-1};
  if (RejectFinalMultiHeavyCarrier(
          bcFinal, bcCharmCharge, bcCharmOrigin, bcCharmResolution,
          bcCharmMatched, bcCharmRejected) != 0 ||
      RejectFinalMultiHeavyCarrier(
          bcFinal, bcBeautyCharge, bcBeautyOrigin, bcBeautyResolution,
          bcBeautyMatched, bcBeautyRejected) != 0 ||
      bcCharmMatched[0] != 20 || bcBeautyMatched[0] != 21) {
    return 11;
  }

  bool rejectedMismatchedVectors = false;
  try {
    std::vector<int> shortCharge{1};
    EnforceUniqueFinalHardCarrier(isFinal, shortCharge, origin, resolution,
                                  matchedHard);
  } catch (const std::invalid_argument&) {
    rejectedMismatchedVectors = true;
  }
  if (!rejectedMismatchedVectors) return 12;
  rejectedMismatchedVectors = false;
  try {
    std::vector<int> shortRejected;
    RejectFinalMultiHeavyCarrier(multiFinal, multiCharge, multiOrigin,
                                 multiResolution, multiMatched, shortRejected);
  } catch (const std::invalid_argument&) {
    rejectedMismatchedVectors = true;
  }
  if (!rejectedMismatchedVectors) return 13;

  std::cout << "HARD_CARRIER_UNIQUENESS_TEST_PASS conflict_groups="
            << result.conflictGroups
            << " demoted_matches=" << result.demotedMatches
            << " multi_heavy_rejections=2 bc_sectors_preserved=2\n";
  return 0;
}
