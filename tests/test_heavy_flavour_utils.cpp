#include "../SimulationScripts/HeavyFlavourUtils.h"

#include <cassert>
#include <cmath>
#include <iostream>
#include <set>

using namespace Hadronization;

int main() {
  const auto dplus = DecodeHeavyContent(411, true, false);
  const auto dminus = DecodeHeavyContent(-411, true, false);
  const auto bplus = DecodeHeavyContent(521, true, false);
  const auto bcplus = DecodeHeavyContent(541, true, false);
  const auto xic = DecodeHeavyContent(4312, false, true);
  assert(dplus.qc() == 1 && dminus.qc() == -1);
  assert(bplus.qb() == -1 && bplus.qc() == 0);
  assert(bcplus.qc() == 1 && bcplus.qb() == -1);
  assert(xic.qc() == 1 && xic.strangeness() == -1);

  assert(IsDirectPrimaryStatus(81));
  assert(IsDirectPrimaryStatus(89));
  assert(!IsDirectPrimaryStatus(-83));
  assert(!IsDirectPrimaryStatus(91));
  assert(!IsCentralKinematic(1.0, 0.0, true));
  assert(IsCentralKinematic(std::nextafter(1.0, 2.0), 4.0, true));
  assert(!IsCentralKinematic(2.0, std::nextafter(4.0, 5.0), true));
  assert(!IsCentralKinematic(0.15, 0.0, false));

  std::set<std::uint64_t> ids;
  for (int tune = 0; tune < 3; ++tune) {
    for (int logical = 0; logical < 200; ++logical) {
      for (int attempt = 0; attempt < 4; ++attempt) {
        for (std::uint64_t event : {0ULL, 999999ULL}) {
          assert(ids.insert(EventId(1, tune, logical, attempt, event)).second);
        }
      }
    }
  }
  assert(WrapDeltaPhi(0.0, 0.0) == 0.0);
  const double wrapped = WrapDeltaPhi(-3.0, 3.0);
  assert(wrapped >= -M_PI / 2.0 && wrapped < 3.0 * M_PI / 2.0);
  std::cout << "heavy-flavour utility tests passed\n";
}
