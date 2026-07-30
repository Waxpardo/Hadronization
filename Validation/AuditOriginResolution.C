#include "../SimulationScripts/GeneratedHeavyFlavourRegistry.h"
#include "../SimulationScripts/HeavyFlavourUtils.h"
#include "../AnalysisScripts/GeneratedPairRegistry.h"

#include <TFile.h>
#include <TH3D.h>
#include <TTree.h>

#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <string>
#include <tuple>
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

struct Counts {
  ULong64_t candidates = 0;
  ULong64_t selectedHard = 0;
  ULong64_t shower = 0;
  ULong64_t mpi = 0;
  ULong64_t otherResolved = 0;
  ULong64_t unresolved = 0;
  double sumWeights = 0.0;
};

void AddOrigin(Counts& counts, int origin, double weight) {
  ++counts.candidates;
  counts.sumWeights += weight;
  if (origin == static_cast<int>(Hadronization::Origin::kSelectedHard)) {
    ++counts.selectedHard;
  } else if (origin == static_cast<int>(Hadronization::Origin::kShower)) {
    ++counts.shower;
  } else if (origin == static_cast<int>(Hadronization::Origin::kMPI)) {
    ++counts.mpi;
  } else if (origin ==
             static_cast<int>(Hadronization::Origin::kOtherResolved)) {
    ++counts.otherResolved;
  } else {
    ++counts.unresolved;
  }
}

}  // namespace

int AuditOriginResolution(const char* inputPath, const char* outputPath) {
  TFile input(inputPath, "READ");
  auto* tree = input.Get<TTree>("tree");
  auto* metadata = input.Get<TTree>("job_metadata");
  if (input.IsZombie() || !tree || !metadata) {
    std::cerr << "ORIGIN_AUDIT_ERROR invalid raw input\n";
    return 1;
  }
  std::string* tunePointer = nullptr;
  metadata->SetBranchAddress("tune", &tunePointer);
  metadata->GetEntry(0);
  const std::string tune = tunePointer ? *tunePointer : "UNKNOWN";
  metadata->ResetBranchAddresses();

  Int_t hardChannel = 0;
  Int_t multiplicity = 0;
  Double_t eventWeight = 0.0;
  std::vector<int>* pdg = nullptr;
  std::vector<int>* status = nullptr;
  std::vector<int>* isFinal = nullptr;
  std::vector<int>* central = nullptr;
  std::vector<int>* originC = nullptr;
  std::vector<int>* originB = nullptr;
  std::vector<int>* resolutionC = nullptr;
  std::vector<int>* resolutionB = nullptr;
  std::vector<double>* pt = nullptr;
  std::vector<double>* eta = nullptr;
  tree->SetBranchAddress("hard_channel", &hardChannel);
  tree->SetBranchAddress("multiplicity_hadronisation_v1", &multiplicity);
  tree->SetBranchAddress("event_weight", &eventWeight);
  tree->SetBranchAddress("heavyPdg", &pdg);
  tree->SetBranchAddress("heavyStatus", &status);
  tree->SetBranchAddress("heavyIsFinal", &isFinal);
  tree->SetBranchAddress("heavyCentral", &central);
  tree->SetBranchAddress("heavyOriginC", &originC);
  tree->SetBranchAddress("heavyOriginB", &originB);
  tree->SetBranchAddress("heavyMatchResolutionC", &resolutionC);
  tree->SetBranchAddress("heavyMatchResolutionB", &resolutionB);
  tree->SetBranchAddress("heavyPt", &pt);
  tree->SetBranchAddress("heavyEta", &eta);

  using Key = std::tuple<int, int, int, int>;
  // key: role (0 associate, 1 trigger), hard channel, signed PDG, resolution
  std::map<Key, Counts> summary;
  TH3D triggerTotalCharm(
      "hTriggerCandidateTotalCharm",
      "Charm trigger candidates;p_{T};#eta;N_{ch}", 100, 0, 50, 80, -4, 4,
      128, -0.5, 511.5);
  TH3D triggerUnresolvedCharm(
      "hTriggerCandidateUnresolvedCharm",
      "Unresolved charm trigger candidates;p_{T};#eta;N_{ch}", 100, 0, 50,
      80, -4, 4, 128, -0.5, 511.5);
  TH3D triggerTotalBeauty(
      "hTriggerCandidateTotalBeauty",
      "Beauty trigger candidates;p_{T};#eta;N_{ch}", 100, 0, 50, 80, -4, 4,
      128, -0.5, 511.5);
  TH3D triggerUnresolvedBeauty(
      "hTriggerCandidateUnresolvedBeauty",
      "Unresolved beauty trigger candidates;p_{T};#eta;N_{ch}", 100, 0, 50,
      80, -4, 4, 128, -0.5, 511.5);
  triggerTotalCharm.Sumw2();
  triggerUnresolvedCharm.Sumw2();
  triggerTotalBeauty.Sumw2();
  triggerUnresolvedBeauty.Sumw2();

  for (Long64_t entry = 0; entry < tree->GetEntries(); ++entry) {
    tree->GetEntry(entry);
    for (std::size_t index = 0; index < pdg->size(); ++index) {
      const auto* state = Hadronization::FindGroundState((*pdg)[index]);
      if (!state || !(*central)[index] || !(*isFinal)[index] ||
          !Hadronization::IsDirectPrimaryStatus((*status)[index])) {
        continue;
      }
      const bool charm = state->sector == "charm";
      const int origin = charm ? (*originC)[index] : (*originB)[index];
      const int resolution =
          charm ? (*resolutionC)[index] : (*resolutionB)[index];
      if (Hadronization::IsCentralKinematic((*pt)[index], (*eta)[index],
                                            false)) {
        AddOrigin(summary[{0, hardChannel, (*pdg)[index], resolution}],
                  origin, eventWeight);
      }
      if (IsPublicationTrigger((*pdg)[index]) &&
          Hadronization::IsCentralKinematic((*pt)[index], (*eta)[index],
                                            true)) {
        AddOrigin(summary[{1, hardChannel, (*pdg)[index], resolution}],
                  origin, eventWeight);
        TH3D* total = charm ? &triggerTotalCharm : &triggerTotalBeauty;
        TH3D* unresolved =
            charm ? &triggerUnresolvedCharm : &triggerUnresolvedBeauty;
        total->Fill((*pt)[index], (*eta)[index], multiplicity, eventWeight);
        if (origin == static_cast<int>(Hadronization::Origin::kUnresolved)) {
          unresolved->Fill((*pt)[index], (*eta)[index], multiplicity,
                           eventWeight);
        }
      }
    }
  }
  tree->ResetBranchAddresses();

  TFile output(outputPath, "CREATE");
  if (output.IsZombie()) return 2;
  triggerTotalCharm.Write();
  triggerUnresolvedCharm.Write();
  triggerTotalBeauty.Write();
  triggerUnresolvedBeauty.Write();
  TTree summaryTree("origin_summary",
                    "origin counts by role, channel, species, resolution");
  std::string outputTune = tune;
  Int_t role = 0;
  Int_t outputHardChannel = 0;
  Int_t outputPdg = 0;
  Int_t outputResolution = 0;
  Counts outputCounts;
  summaryTree.Branch("tune", &outputTune);
  summaryTree.Branch("role", &role, "role/I");
  summaryTree.Branch("hard_channel", &outputHardChannel, "hard_channel/I");
  summaryTree.Branch("pdg", &outputPdg, "pdg/I");
  summaryTree.Branch("resolution", &outputResolution, "resolution/I");
  summaryTree.Branch("candidates", &outputCounts.candidates, "candidates/l");
  summaryTree.Branch("selected_hard", &outputCounts.selectedHard,
                     "selected_hard/l");
  summaryTree.Branch("shower", &outputCounts.shower, "shower/l");
  summaryTree.Branch("mpi", &outputCounts.mpi, "mpi/l");
  summaryTree.Branch("other_resolved", &outputCounts.otherResolved,
                     "other_resolved/l");
  summaryTree.Branch("unresolved", &outputCounts.unresolved, "unresolved/l");
  summaryTree.Branch("sum_weights", &outputCounts.sumWeights, "sum_weights/D");
  ULong64_t totalTriggerCandidates = 0;
  ULong64_t unresolvedTriggerCandidates = 0;
  for (const auto& [key, counts] : summary) {
    std::tie(role, outputHardChannel, outputPdg, outputResolution) = key;
    outputCounts = counts;
    summaryTree.Fill();
    if (role == 1) {
      totalTriggerCandidates += counts.candidates;
      unresolvedTriggerCandidates += counts.unresolved;
    }
  }
  summaryTree.Write();
  output.Write();
  output.Close();
  const double unresolvedFraction =
      totalTriggerCandidates == 0
          ? 0.0
          : static_cast<double>(unresolvedTriggerCandidates) /
                static_cast<double>(totalTriggerCandidates);
  std::cout << "ORIGIN_RESOLUTION_AUDIT tune=" << tune
            << " trigger_candidates=" << totalTriggerCandidates
            << " unresolved_trigger_candidates="
            << unresolvedTriggerCandidates
            << " unresolved_fraction=" << unresolvedFraction
            << " summary_rows=" << summary.size() << " output=" << outputPath
            << "\n";
  return 0;
}
