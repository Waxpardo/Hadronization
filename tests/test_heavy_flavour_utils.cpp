#include "../SimulationScripts/HeavyFlavourUtils.h"
#include "../SimulationScripts/GeneratedHeavyFlavourRegistry.h"
#include "../SimulationScripts/Sha256.h"

#include <cassert>
#include <cmath>
#include <iostream>
#include <map>
#include <set>
#include <vector>

using namespace Hadronization;

namespace {

struct OriginGraphNode {
  int pdg = 0;
  int status = 0;
  std::vector<int> mothers;
};

HeavyOriginMatch MatchTestOrigin(
    const std::vector<OriginGraphNode>& graph,
    const std::map<int, int>& selectedHardRoots, int particleIndex,
    int flavour, int requiredSign) {
  return MatchHeavyOriginGraph(
      particleIndex, static_cast<int>(graph.size()), flavour, requiredSign,
      [&graph](int index) {
        return graph[static_cast<std::size_t>(index)].pdg;
      },
      [&graph](int index) {
        return graph[static_cast<std::size_t>(index)].status;
      },
      [&graph](int index) {
        return graph[static_cast<std::size_t>(index)].mothers;
      },
      [&selectedHardRoots](int index, int signedFlavour) {
        const auto found = selectedHardRoots.find(index);
        return found != selectedHardRoots.end() &&
               found->second == signedFlavour;
      });
}

void AssertOrigin(const HeavyOriginMatch& match, Origin origin,
                  MatchResolution resolution, int hardRoot, int depth) {
  assert(match.origin == origin);
  assert(match.resolution == resolution);
  assert(match.hardRootIndex == hardRoot);
  assert(match.depth == depth);
}

}  // namespace

int main() {
  assert(std::string(kRawSchema) == "hf_primary_ground_raw_v5");
  assert(std::string(kOriginAlgorithmVersion) ==
         "signed_heavy_constituent_complete_mothers_unique_v4");
  assert(std::string(kHeavyStabilityAuditSchema) ==
         "heavy_stability_audit_v2");
  assert(std::string(kEffectiveSettingsSchema) ==
         "effective_pythia_settings_exhaustive_v2");
  assert(std::string(kPrimaryAllHeavyMatchSchema) ==
         "primary_all_heavy_constituent_match_v1");
  assert(static_cast<int>(MatchResolution::kMultipleHeavyConstituents) == 6);
  assert(Sha256Hex("") ==
         "e3b0c44298fc1c149afbf4c8996fb924"
         "27ae41e4649b934ca495991b7852b855");
  assert(Sha256Hex("abc") ==
         "ba7816bf8f01cfea414140de5dae2223"
         "b00361a396177a9cb410ff61f20015ad");
  Sha256 streamedDigest;
  streamedDigest.Update("a");
  streamedDigest.Update("b");
  streamedDigest.Update("c");
  assert(streamedDigest.FinalHex() == Sha256Hex("abc"));
  const auto dplus = DecodeHeavyContent(411, true, false);
  const auto dminus = DecodeHeavyContent(-411, true, false);
  const auto bplus = DecodeHeavyContent(521, true, false);
  const auto bcplus = DecodeHeavyContent(541, true, false);
  const auto xic = DecodeHeavyContent(4312, false, true);
  assert(dplus.qc() == 1 && dminus.qc() == -1);
  assert(bplus.qb() == -1 && bplus.qc() == 0);
  assert(bcplus.qc() == 1 && bcplus.qb() == -1);
  assert(xic.qc() == 1 && xic.strangeness() == -1);

  // Table-driven signed-content check for every operational central state,
  // including all explicit antiparticles and both Bc sectors.
  for (const auto& state : kGroundStates) {
    const bool isMeson = state.kind == "meson";
    const bool isBaryon = state.kind == "baryon";
    const HeavyContent decoded =
        DecodeHeavyContent(state.pdg, isMeson, isBaryon);
    assert(decoded.qc() == state.qc);
    assert(decoded.qb() == state.qb);
    assert(ClassifyHeavyState(true, decoded) ==
           HeavyStateCategory::kCentralGround);
    int exactBaryonNumber = 99;
    const int pythiaBaryonNumberType =
        isBaryon ? (state.pdg > 0 ? 3 : -3) : 0;
    assert(DecodePythiaBaryonNumber(
        state.pdg, isMeson, isBaryon, pythiaBaryonNumberType,
        exactBaryonNumber));
    assert(exactBaryonNumber ==
           (isBaryon ? (state.pdg > 0 ? 1 : -1) : 0));
  }

  struct NoncentralContentCase {
    int pdg;
    bool isMeson;
    bool isBaryon;
    int nc;
    int ncbar;
    int nb;
    int nbbar;
    int spinType;
    HeavyStateCategory category;
  };
  const std::vector<NoncentralContentCase> noncentralCases{
      {443, true, false, 1, 1, 0, 0, 3,
       HeavyStateCategory::kHiddenHeavy},
      {553, true, false, 0, 0, 1, 1, 3,
       HeavyStateCategory::kHiddenHeavy},
      {4422, false, true, 2, 0, 0, 0, 2,
       HeavyStateCategory::kMultiplyHeavy},
      {-4422, false, true, 0, 2, 0, 0, 2,
       HeavyStateCategory::kMultiplyHeavy},
      {5512, false, true, 0, 0, 2, 0, 2,
       HeavyStateCategory::kMultiplyHeavy},
      {-5512, false, true, 0, 0, 0, 2, 2,
       HeavyStateCategory::kMultiplyHeavy},
      {413, true, false, 1, 0, 0, 0, 3,
       HeavyStateCategory::kExcludedVector},
      {-413, true, false, 0, 1, 0, 0, 3,
       HeavyStateCategory::kExcludedVector},
      {10411, true, false, 1, 0, 0, 0, 1,
       HeavyStateCategory::kExcludedExcited},
      {-10411, true, false, 0, 1, 0, 0, 1,
       HeavyStateCategory::kExcludedExcited}};
  for (const auto& test : noncentralCases) {
    const HeavyContent decoded =
        DecodeHeavyContent(test.pdg, test.isMeson, test.isBaryon);
    assert(decoded.nc == test.nc && decoded.ncbar == test.ncbar);
    assert(decoded.nb == test.nb && decoded.nbbar == test.nbbar);
    assert(ClassifyHeavyStateDetailed(
               false, decoded, test.isMeson, test.spinType) ==
           test.category);
  }

  int baryonNumber = 99;
  assert(DecodePythiaBaryonNumber(411, true, false, 0, baryonNumber) &&
         baryonNumber == 0);
  assert(DecodePythiaBaryonNumber(-411, true, false, 0, baryonNumber) &&
         baryonNumber == 0);
  assert(DecodePythiaBaryonNumber(5122, false, true, 3, baryonNumber) &&
         baryonNumber == 1);
  assert(DecodePythiaBaryonNumber(-5122, false, true, -3, baryonNumber) &&
         baryonNumber == -1);
  assert(!DecodePythiaBaryonNumber(5122, false, true, 1, baryonNumber));
  assert(!DecodePythiaBaryonNumber(-5122, false, true, 3, baryonNumber));
  assert(!DecodePythiaBaryonNumber(411, true, true, 0, baryonNumber));

  // Exact status-23 hard root through a same-sign copy chain. Duplicate and
  // invalid ancestry endpoints normalize away and cannot create ambiguity.
  const std::vector<OriginGraphNode> hardCopyGraph{
      {}, {4, 23, {}}, {4, 51, {1}}, {411, 83, {2, 2, 0, 99}}};
  AssertOrigin(MatchTestOrigin(hardCopyGraph, {{1, 4}}, 3, 4, 1),
               Origin::kSelectedHard, MatchResolution::kUnique, 1, 2);

  // A heavy diquark endpoint in a junction-style mother range is traversed to
  // the same signed hard quark; unrelated light endpoints are ignored.
  const std::vector<OriginGraphNode> junctionGraph{
      {},
      {4, 23, {}},
      {4, 51, {1}},
      {4203, 74, {2}},
      {2, 74, {}},
      {4122, 83, {3, 4, 3}}};
  assert(CarriesSignedHeavyConstituent(4203, 4, 1));
  assert(!CarriesSignedHeavyConstituent(4203, 4, -1));
  AssertOrigin(MatchTestOrigin(junctionGraph, {{1, 4}}, 5, 4, 1),
               Origin::kSelectedHard, MatchResolution::kUnique, 1, 2);

  // Two equally near signed-heavy ancestors are intrinsically ambiguous, even
  // when one happens to be a selected-hard root.
  const std::vector<OriginGraphNode> ambiguousGraph{
      {}, {4, 23, {}}, {4, 45, {}}, {411, 83, {1, 2}}};
  AssertOrigin(MatchTestOrigin(ambiguousGraph, {{1, 4}}, 3, 4, 1),
               Origin::kUnresolved, MatchResolution::kAmbiguous, -1, 1);

  // A disconnected selected-hard quark cannot contaminate a shower, MPI, or
  // missing-carrier lineage.
  const std::vector<OriginGraphNode> showerGraph{
      {}, {4, 23, {}}, {4, 45, {}}, {411, 83, {2}}};
  AssertOrigin(MatchTestOrigin(showerGraph, {{1, 4}}, 3, 4, 1),
               Origin::kShower, MatchResolution::kUnique, -1, 1);
  const std::vector<OriginGraphNode> mpiGraph{
      {}, {4, 23, {}}, {4, 35, {}}, {411, 83, {2}}};
  AssertOrigin(MatchTestOrigin(mpiGraph, {{1, 4}}, 3, 4, 1),
               Origin::kMPI, MatchResolution::kUnique, -1, 1);
  const std::vector<OriginGraphNode> missingCarrierGraph{
      {}, {4, 23, {}}, {21, 51, {1}}, {411, 83, {2}}};
  AssertOrigin(MatchTestOrigin(missingCarrierGraph, {{1, 4}}, 3, 4, 1),
               Origin::kUnresolved, MatchResolution::kMissingCarrier, -1,
               -1);

  // Bc has independent c and anti-b lineages and is matched separately in the
  // two heavy-flavour sectors.
  const std::vector<OriginGraphNode> bcGraph{
      {},
      {4, 23, {}},
      {4, 51, {1}},
      {-5, 23, {}},
      {-5, 51, {3}},
      {541, 83, {2, 4}}};
  AssertOrigin(MatchTestOrigin(bcGraph, {{1, 4}, {3, -5}}, 5, 4, 1),
               Origin::kSelectedHard, MatchResolution::kUnique, 1, 2);
  AssertOrigin(MatchTestOrigin(bcGraph, {{1, 4}, {3, -5}}, 5, 5, -1),
               Origin::kSelectedHard, MatchResolution::kUnique, 3, 2);

  // A charm quark produced below a beauty lineage does not inherit the
  // selected-hard beauty origin and cannot connect to an unrelated hard c.
  const std::vector<OriginGraphNode> charmFromBeautyGraph{
      {},
      {5, 23, {}},
      {5, 51, {1}},
      {4, 91, {2}},
      {411, 83, {3}},
      {4, 23, {}}};
  AssertOrigin(
      MatchTestOrigin(charmFromBeautyGraph, {{1, 5}, {5, 4}}, 4, 4, 1),
      Origin::kOtherResolved, MatchResolution::kUnique, -1, 1);

  assert(ClassifyHeavyState(true, dplus) ==
         HeavyStateCategory::kCentralGround);
  HeavyContent hiddenCharm;
  hiddenCharm.nc = 1;
  hiddenCharm.ncbar = 1;
  assert(ClassifyHeavyState(false, hiddenCharm) ==
         HeavyStateCategory::kHiddenHeavy);
  HeavyContent doubleCharm;
  doubleCharm.nc = 2;
  assert(ClassifyHeavyState(false, doubleCharm) ==
         HeavyStateCategory::kMultiplyHeavy);
  assert(ClassifyHeavyStateDetailed(false, dplus, true, 3) ==
         HeavyStateCategory::kExcludedVector);
  assert(ClassifyHeavyStateDetailed(false, dplus, true, 1) ==
         HeavyStateCategory::kExcludedExcited);

  // Two indistinguishable same-sign constituents belonging to one final
  // multiply-heavy parent are one parent-level carrier claim, not a conflict.
  std::vector<int> sameParentSlot{7, 7, 8};
  std::vector<int> sameParentFinal{1, 1, 1};
  std::vector<int> sameParentPdg{4, 4, -4};
  std::vector<int> sameParentOrigin{
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kSelectedHard),
      static_cast<int>(Origin::kSelectedHard)};
  std::vector<int> sameParentResolution(
      3, static_cast<int>(MatchResolution::kUnique));
  std::vector<int> sameParentMatched{23, 23, 24};
  std::vector<int> sameParentRejected(3, -1);
  const CarrierUniquenessResult sameParentUniqueness =
      EnforceUniqueFinalConstituentHardCarrier(
          sameParentSlot, sameParentFinal, sameParentPdg, sameParentOrigin,
          sameParentResolution, sameParentMatched, sameParentRejected);
  assert(sameParentUniqueness.conflictGroups == 0);
  assert(sameParentUniqueness.demotedMatches == 0);
  assert(sameParentMatched[0] == 23 && sameParentMatched[1] == 23 &&
         sameParentMatched[2] == 24);
  assert(sameParentRejected[0] == -1 && sameParentRejected[1] == -1 &&
         sameParentRejected[2] == -1);
  // Reproduce the closure audit's carrier-parent lookup. Both qualifying rows
  // must resolve to parent 7, which is then classified as multiply-heavy.
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
    assert(closureCarrierParent < 0 ||
           closureCarrierParent == sameParentSlot[index]);
    closureCarrierParent = sameParentSlot[index];
  }
  assert(closureCarrierParent == 7 &&
         ClassifyHeavyState(false, doubleCharm) ==
             HeavyStateCategory::kMultiplyHeavy);

  // The same selected hard carrier claimed by distinct final parents remains a
  // conflict and every row in the conflicting parent claims is demoted.
  std::vector<int> distinctParentSlot{7, 7, 9, 8};
  std::vector<int> distinctParentFinal{1, 1, 1, 1};
  std::vector<int> distinctParentPdg{4, 4, 4, -4};
  std::vector<int> distinctParentOrigin(
      4, static_cast<int>(Origin::kSelectedHard));
  std::vector<int> distinctParentResolution(
      4, static_cast<int>(MatchResolution::kUnique));
  std::vector<int> distinctParentMatched{23, 23, 23, 24};
  std::vector<int> distinctParentRejected(4, -1);
  const CarrierUniquenessResult distinctParentUniqueness =
      EnforceUniqueFinalConstituentHardCarrier(
          distinctParentSlot, distinctParentFinal, distinctParentPdg,
          distinctParentOrigin, distinctParentResolution,
          distinctParentMatched, distinctParentRejected);
  assert(distinctParentUniqueness.conflictGroups == 1);
  assert(distinctParentUniqueness.demotedMatches == 3);
  for (const std::size_t index : {0U, 1U, 2U}) {
    assert(distinctParentOrigin[index] ==
           static_cast<int>(Origin::kUnresolved));
    assert(distinctParentResolution[index] ==
           static_cast<int>(MatchResolution::kDuplicateHardCarrier));
    assert(distinctParentMatched[index] == -1);
    assert(distinctParentRejected[index] == 23);
  }
  assert(distinctParentMatched[3] == 24 &&
         distinctParentRejected[3] == -1);

  // A Bc parent has independent charm and beauty carriers. Different hard
  // indices cannot conflict merely because both rows share the same parent.
  std::vector<int> bcParentSlot{4, 4};
  std::vector<int> bcParentFinal{1, 1};
  std::vector<int> bcConstituentPdg{4, -5};
  std::vector<int> bcOrigin(2, static_cast<int>(Origin::kSelectedHard));
  std::vector<int> bcResolution(2,
                                static_cast<int>(MatchResolution::kUnique));
  std::vector<int> bcMatched{20, 21};
  std::vector<int> bcRejected(2, -1);
  const CarrierUniquenessResult bcUniqueness =
      EnforceUniqueFinalConstituentHardCarrier(
          bcParentSlot, bcParentFinal, bcConstituentPdg, bcOrigin,
          bcResolution, bcMatched, bcRejected);
  assert(bcUniqueness.conflictGroups == 0 &&
         bcUniqueness.demotedMatches == 0);
  assert(bcMatched[0] == 20 && bcMatched[1] == 21);

  assert(IsDirectPrimaryStatus(81));
  assert(IsDirectPrimaryStatus(89));
  assert(!IsDirectPrimaryStatus(-83));
  assert(!IsDirectPrimaryStatus(91));
  assert(!IsCentralKinematic(1.0, 0.0, true));
  assert(IsCentralKinematic(std::nextafter(1.0, 2.0), 4.0, true));
  assert(!IsCentralKinematic(2.0, std::nextafter(4.0, 5.0), true));
  assert(!IsCentralKinematic(0.15, 0.0, false));
  assert(CountsNchHadronisationV1(211, 81, true,
                                  std::nextafter(0.15, 1.0), 4.0));
  assert(!CountsNchHadronisationV1(211, 81, true, 0.15, 0.0));
  assert(!CountsNchHadronisationV1(
      211, 81, true, 1.0, std::nextafter(4.0, 5.0)));
  assert(!CountsNchHadronisationV1(211, -81, true, 1.0, 0.0));
  assert(!CountsNchHadronisationV1(211, 81, false, 1.0, 0.0));
  assert(!CountsNchHadronisationV1(111, 81, true, 1.0, 0.0));
  for (const int pdg : {11, -11, 13, -13, 211, -211, 321, -321, 2212,
                        -2212}) {
    assert(CountsNchHadronisationV1(pdg, 85, true, 1.0, 0.0));
    assert(CountsNchFinalStrongEmV1(pdg, true, 1.0, 0.0, false));
    assert(!CountsNchFinalStrongEmV1(pdg, true, 1.0, 0.0, true));
  }
  for (const int weakParent : {13, 15, 211, 311, 310, 130, 321, 2112,
                               3122, 3112, 3222, 3312, 3322, 3334,
                               411, 511}) {
    assert(IsKnownWeakParent(weakParent));
    assert(IsKnownWeakParent(-weakParent));
  }
  for (const int strongOrStableParent : {22, 111, 113, 221, 223, 2212}) {
    assert(!IsKnownWeakParent(strongOrStableParent));
  }
  assert(std::string(kWeakDecayTransitionRuleVersion) ==
         "weak_decay_transition_pythia_status_v1");
  assert(IsWeakDecayTransitionV1(211, -81, 13, 91));
  assert(!IsWeakDecayTransitionV1(211, 81, 13, 91));
  assert(!IsWeakDecayTransitionV1(211, -81, 13, 99));
  assert(!IsWeakDecayTransitionV1(13, -81, 13, 91));
  assert(!IsWeakDecayTransitionV1(113, -81, 211, 91));

  const auto hasWeakTransition =
      [](int finalIndex, const std::vector<int>& pdg,
         const std::vector<int>& status,
         const std::vector<std::vector<int>>& mothers) {
        assert(pdg.size() == status.size());
        assert(pdg.size() == mothers.size());
        return HasWeakDecayTransitionV1(
            finalIndex, static_cast<int>(pdg.size()),
            [&pdg](int index) {
              return pdg[static_cast<std::size_t>(index)];
            },
            [&status](int index) {
              return status[static_cast<std::size_t>(index)];
            },
            [&mothers](int index) -> const std::vector<int>& {
              return mothers[static_cast<std::size_t>(index)];
            });
      };

  // A primary weak-capable species is not itself evidence of a decay.
  for (const int primary : {13, 211, 321}) {
    assert(!hasWeakTransition(
        1, {0, primary}, {-11, 81}, {{}, {}}));
  }
  // Same-particle event-record links are traversed but never classified as
  // weak transitions, even if the copy uses a decay-range status.
  assert(!hasWeakTransition(
      2, {0, 13, 13}, {-11, -81, 91}, {{}, {}, {1}}));
  // A copy after a genuine pion decay retains that earlier weak transition.
  assert(hasWeakTransition(
      3, {0, 211, 13, 13}, {-11, -81, -91, 99},
      {{}, {}, {1}, {2}}));
  assert(hasWeakTransition(
      2, {0, 211, 13}, {-11, -81, 91}, {{}, {}, {1}}));
  // Kaon and hyperon cascades are excluded once any actual registered weak
  // parent-to-decay-product edge occurs.
  assert(hasWeakTransition(
      3, {0, 321, 211, 13}, {-11, -81, -91, 91},
      {{}, {}, {1}, {2}}));
  assert(hasWeakTransition(
      4, {0, 3312, 3122, 211, 13}, {-11, -81, -91, -91, 91},
      {{}, {}, {1}, {2}, {3}}));
  // A normal decay-product status does not make strong/EM resonance lineage
  // weak when the actual parent is not in the weak-parent registry.
  assert(!hasWeakTransition(
      2, {0, 113, 211}, {-11, -81, 91}, {{}, {}, {1}}));
  // Malformed and cyclic ancestry must be handled deterministically. Invalid
  // mother indices are rejected, while a cycle with no qualifying transition
  // terminates without inventing a weak-decay classification.
  bool invalidMotherRejected = false;
  try {
    (void)hasWeakTransition(
        2, {0, 113, 211}, {-11, -81, 91}, {{}, {}, {3}});
  } catch (const std::invalid_argument&) {
    invalidMotherRejected = true;
  }
  assert(invalidMotherRejected);
  assert(!hasWeakTransition(
      2, {0, 13, 13}, {-11, -81, 91}, {{}, {2}, {1}}));

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
