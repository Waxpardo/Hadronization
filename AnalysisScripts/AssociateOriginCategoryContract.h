#ifndef HADRONIZATION_ASSOCIATE_ORIGIN_CATEGORY_CONTRACT_H
#define HADRONIZATION_ASSOCIATE_ORIGIN_CATEGORY_CONTRACT_H

#include "../SimulationScripts/HeavyFlavourUtils.h"

namespace Hadronization {

inline constexpr const char* kAssociateOriginCategorySchema =
    "associate_origin_category_v1";
inline constexpr const char* kAssociateOriginCategoryLabels =
    "{\"1\":\"selected_hard_companion\","
    "\"2\":\"selected_hard_noncompanion\",\"3\":\"shower\","
    "\"4\":\"mpi\",\"5\":\"other_resolved\","
    "\"6\":\"unresolved_or_ambiguous\"}";

// 1 selected-hard companion, 2 selected-hard noncompanion, 3 shower,
// 4 MPI, 5 other resolved, 6 unresolved or ambiguous.
inline int AssociateOriginCategory(
    Origin origin, int associateHard, int triggerHard,
    int associateSectorCharge, int triggerSectorCharge) {
  if (origin == Origin::kSelectedHard) {
    if (associateHard >= 0 && associateHard != triggerHard &&
        associateSectorCharge * triggerSectorCharge < 0) {
      return 1;
    }
    return 2;
  }
  if (origin == Origin::kShower) return 3;
  if (origin == Origin::kMPI) return 4;
  if (origin == Origin::kOtherResolved) return 5;
  return 6;
}

}  // namespace Hadronization

#endif
