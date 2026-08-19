#include "../AnalysisScripts/AssociateOriginCategoryContract.h"

#include <cstring>
#include <iostream>

int main() {
  using Hadronization::AssociateOriginCategory;
  using Hadronization::Origin;

  int errors = 0;
  errors += AssociateOriginCategory(Origin::kSelectedHard, 11, 10, -1, 1) != 1;
  errors += AssociateOriginCategory(Origin::kSelectedHard, 10, 10, -1, 1) != 2;
  errors += AssociateOriginCategory(Origin::kSelectedHard, 11, 10, 1, 1) != 2;
  errors += AssociateOriginCategory(Origin::kShower, -1, 10, -1, 1) != 3;
  errors += AssociateOriginCategory(Origin::kMPI, -1, 10, -1, 1) != 4;
  errors += AssociateOriginCategory(Origin::kOtherResolved, -1, 10, -1, 1) != 5;
  errors += AssociateOriginCategory(Origin::kUnresolved, -1, 10, -1, 1) != 6;
  errors += std::strcmp(
      Hadronization::kAssociateOriginCategoryLabels,
      "{\"1\":\"selected_hard_companion\","
      "\"2\":\"selected_hard_noncompanion\",\"3\":\"shower\","
      "\"4\":\"mpi\",\"5\":\"other_resolved\","
      "\"6\":\"unresolved_or_ambiguous\"}") != 0;

  std::cout << "ASSOCIATE_ORIGIN_CATEGORY_TEST errors=" << errors << "\n";
  return errors == 0 ? 0 : 1;
}
