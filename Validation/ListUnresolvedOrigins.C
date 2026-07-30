#include "../SimulationScripts/GeneratedHeavyFlavourRegistry.h"
#include "../SimulationScripts/HeavyFlavourUtils.h"
#include "../AnalysisScripts/GeneratedPairRegistry.h"

#include <TFile.h>
#include <TTree.h>

#include <algorithm>
#include <iostream>
#include <vector>

namespace {

bool IsPublicationTrigger(int pdg) {
  return std::any_of(
      Hadronization::kPairDefinitions.begin(),
      Hadronization::kPairDefinitions.end(),
      [pdg](const Hadronization::PairDefinition& pair) {
        return pair.triggerPdg == pdg;
      });
}

}  // namespace

void ListUnresolvedOrigins(const char* path, int maximumRows = 20) {
  TFile input(path, "READ");
  auto* tree = input.Get<TTree>("tree");
  if (!tree) {
    std::cerr << "ERROR: missing tree in " << path << "\n";
    return;
  }

  ULong64_t eventId = 0;
  std::vector<int>* pdg = nullptr;
  std::vector<int>* status = nullptr;
  std::vector<int>* isFinal = nullptr;
  std::vector<int>* central = nullptr;
  std::vector<int>* qc = nullptr;
  std::vector<int>* qb = nullptr;
  std::vector<int>* originC = nullptr;
  std::vector<int>* originB = nullptr;
  std::vector<int>* resolutionC = nullptr;
  std::vector<int>* resolutionB = nullptr;
  std::vector<int>* mother1 = nullptr;
  std::vector<int>* mother2 = nullptr;
  std::vector<double>* pt = nullptr;
  std::vector<double>* eta = nullptr;
  tree->SetBranchAddress("event_id", &eventId);
  tree->SetBranchAddress("heavyPdg", &pdg);
  tree->SetBranchAddress("heavyStatus", &status);
  tree->SetBranchAddress("heavyIsFinal", &isFinal);
  tree->SetBranchAddress("heavyCentral", &central);
  tree->SetBranchAddress("heavyQc", &qc);
  tree->SetBranchAddress("heavyQb", &qb);
  tree->SetBranchAddress("heavyOriginC", &originC);
  tree->SetBranchAddress("heavyOriginB", &originB);
  tree->SetBranchAddress("heavyMatchResolutionC", &resolutionC);
  tree->SetBranchAddress("heavyMatchResolutionB", &resolutionB);
  tree->SetBranchAddress("heavyMother1", &mother1);
  tree->SetBranchAddress("heavyMother2", &mother2);
  tree->SetBranchAddress("heavyPt", &pt);
  tree->SetBranchAddress("heavyEta", &eta);

  int rows = 0;
  for (Long64_t entry = 0; entry < tree->GetEntries() && rows < maximumRows;
       ++entry) {
    tree->GetEntry(entry);
    for (std::size_t index = 0; index < pdg->size() && rows < maximumRows;
         ++index) {
      if (!(*central)[index] || !IsPublicationTrigger((*pdg)[index]) ||
          !(*isFinal)[index] ||
          !Hadronization::IsDirectPrimaryStatus((*status)[index]) ||
          !Hadronization::IsCentralKinematic((*pt)[index], (*eta)[index],
                                             true)) {
        continue;
      }
      const auto* state = Hadronization::FindGroundState((*pdg)[index]);
      const bool unresolvedCharm =
          state && state->sector == "charm" && (*qc)[index] != 0 &&
          (*originC)[index] ==
              static_cast<int>(Hadronization::Origin::kUnresolved);
      const bool unresolvedBeauty =
          state && state->sector == "beauty" && (*qb)[index] != 0 &&
          (*originB)[index] ==
              static_cast<int>(Hadronization::Origin::kUnresolved);
      if (!unresolvedCharm && !unresolvedBeauty) continue;
      std::cout << "UNRESOLVED entry=" << entry << " event_id=" << eventId
                << " heavy_slot=" << index << " pdg=" << (*pdg)[index]
                << " status=" << (*status)[index] << " pt=" << (*pt)[index]
                << " eta=" << (*eta)[index]
                << " mother1=" << (*mother1)[index]
                << " mother2=" << (*mother2)[index]
                << " sector=" << (unresolvedCharm ? "charm" : "beauty")
                << " resolution="
                << (unresolvedCharm ? (*resolutionC)[index]
                                    : (*resolutionB)[index])
                << "\n";
      ++rows;
    }
  }
  tree->ResetBranchAddresses();
  std::cout << "UNRESOLVED_LIST rows=" << rows << "\n";
}
