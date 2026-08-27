// Exercises the generated species-ordinal table's lookup semantics.
//
// THE PROPERTY THAT MATTERS IS FAIL-CLOSED (F6). The table is the complete
// admissible set, and a sector-charged PDG absent from it must FAIL the run.
// There is deliberately no overflow bin: an overflow bin is how 152 species
// became invisible in the first place, so a lookup that quietly returned a
// sentinel would reintroduce exactly the defect the axis exists to remove.

#include "../contracts/GeneratedSpeciesOrdinals.h"

#include <cstdio>
#include <set>
#include <string>

namespace {

int errors = 0;

void Check(bool condition, const std::string& what) {
  if (!condition) {
    std::printf("FAIL %s\n", what.c_str());
    ++errors;
  }
}

}  // namespace

int main() {
  using namespace Hadronization;

  Check(kSpeciesOrdinalCount == 202,
        "the ratified table is 202 species, got " +
            std::to_string(kSpeciesOrdinalCount));
  Check(kSpeciesOrdinals.size() ==
            static_cast<std::size_t>(kSpeciesOrdinalCount),
        "the array size must equal kSpeciesOrdinalCount");

  // Round trip: every ordinal's PDG must look up to that same ordinal. This is
  // what makes the axis's index space well defined.
  for (int ordinal = 0; ordinal < kSpeciesOrdinalCount; ++ordinal) {
    const int pdg = kSpeciesOrdinals[static_cast<std::size_t>(ordinal)].pdg;
    int found = -1;
    if (!SpeciesOrdinalFor(pdg, found)) {
      Check(false, "pdg " + std::to_string(pdg) + " in the table did not look up");
      continue;
    }
    Check(found == ordinal,
          "pdg " + std::to_string(pdg) + " looked up to ordinal " +
              std::to_string(found) + ", expected " + std::to_string(ordinal));
  }

  // Ascending, unique PDGs -- the binary search depends on both.
  std::set<int> seen;
  for (std::size_t index = 0; index + 1 < kSpeciesOrdinals.size(); ++index) {
    Check(kSpeciesOrdinals[index].pdg < kSpeciesOrdinals[index + 1].pdg,
          "the table is not in strictly ascending PDG order at index " +
              std::to_string(index));
  }
  for (const auto& row : kSpeciesOrdinals) seen.insert(row.pdg);
  Check(seen.size() == kSpeciesOrdinals.size(), "the table repeats a PDG");

  // ---------------------------------------------------------------------
  // FAIL-CLOSED. Absent PDGs must return false, not a bin.
  // ---------------------------------------------------------------------
  const int absent[] = {
      0,        // not a particle
      21,       // gluon
      2212,     // proton, no heavy content
      443,      // J/psi -- hidden charm, q_c = q_b = 0, deliberately excluded
      553,      // Upsilon -- hidden beauty, same reason
      999999,   // beyond any PDG the generator can emit
      -999999,
  };
  for (const int pdg : absent) {
    int ordinal = 12345;
    Check(!SpeciesOrdinalFor(pdg, ordinal),
          "pdg " + std::to_string(pdg) +
              " must NOT resolve -- the table is the complete admissible set "
              "and there is no overflow bin");
  }

  // Hidden-heavy exclusion is a property of the axis, not an accident: a
  // state with q_c = q_b = 0 cannot compensate, so it can never fill a
  // compensation bin. Spot-check that none of the classic ones is present.
  for (const int hidden : {441, 443, 445, 551, 553, 555, 10441, 20443}) {
    int ordinal = -1;
    Check(!SpeciesOrdinalFor(hidden, ordinal),
          "hidden-heavy pdg " + std::to_string(hidden) +
              " must be absent: it carries no net heavy flavour and would add "
              "a bin that can never fill");
  }

  // Every category must be in range, and kOtherNoncentral (3) must be empty
  // by construction -- every row has open heavy flavour, so the
  // hasCharm||hasBeauty branch always fires first.
  int categoryCounts[6] = {0, 0, 0, 0, 0, 0};
  for (int ordinal = 0; ordinal < kSpeciesOrdinalCount; ++ordinal) {
    const int category = SpeciesCategoryForOrdinal(ordinal);
    Check(category >= 0 && category <= 5,
          "ordinal " + std::to_string(ordinal) + " has category " +
              std::to_string(category) + ", outside [0,5]");
    if (category >= 0 && category <= 5) ++categoryCounts[category];
  }
  Check(categoryCounts[3] == 0,
        "kOtherNoncentral must be unreachable for an open-heavy table, got " +
            std::to_string(categoryCounts[3]));
  Check(SpeciesCategoryForOrdinal(-1) == -1 &&
            SpeciesCategoryForOrdinal(kSpeciesOrdinalCount) == -1,
        "an out-of-range ordinal must report -1, not a category");

  // The legibility string must actually decode the axis: it is what a reader
  // has instead of this repository.
  const std::string labels = kSpeciesOrdinalLabels;
  Check(!labels.empty() && labels.front() == '{' && labels.back() == '}',
        "the labels object must be a JSON object");
  for (const int ordinal : {0, 1, kSpeciesOrdinalCount - 1}) {
    const std::string key = "\"" + std::to_string(ordinal) + "\":" +
                            std::to_string(
                                kSpeciesOrdinals[static_cast<std::size_t>(
                                                     ordinal)]
                                    .pdg);
    Check(labels.find(key) != std::string::npos,
          "the labels object does not carry " + key);
  }

  std::printf("SPECIES_ORDINALS errors=%d species=%d digest=%s\n", errors,
              kSpeciesOrdinalCount, kSpeciesOrdinalDigest);
  return errors == 0 ? 0 : 1;
}
