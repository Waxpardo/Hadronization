// One-pass central publication analysis.
//
// Reads the canonical raw schema once and emits the Paul-compatible ROOT
// object contract for every signed pair in GeneratedPairRegistry.h.

#include "GeneratedPairRegistry.h"
#include "../SimulationScripts/GeneratedHeavyFlavourRegistry.h"
#include "../SimulationScripts/HeavyFlavourUtils.h"

#include "TChain.h"
#include "TFile.h"
#include "TH1D.h"
#include "THnSparse.h"
#include "TObjString.h"
#include "TParameter.h"
#include "TSystem.h"
#include "TTree.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace {

using Hadronization::Origin;

struct PairAccumulator {
  const Hadronization::PairDefinition* definition = nullptr;
  THnSparseD* associate = nullptr;
  THnSparseD* correlation = nullptr;
  THnSparseD* correlationByOrigin = nullptr;
  double weightedPairs = 0.0;
  unsigned long long pairs = 0;
};

struct TriggerAccumulator {
  int pdg = 0;
  std::string sector;
  THnSparseD* histogram = nullptr;
  double weightedTriggers = 0.0;
  unsigned long long triggers = 0;
};

std::vector<std::string> ResolveInputs(const std::string& input) {
  if (input.size() >= 4 && input.substr(input.size() - 4) == ".txt") {
    std::ifstream stream(input);
    if (!stream) throw std::runtime_error("cannot open input list " + input);
    std::vector<std::string> files;
    std::string line;
    while (std::getline(stream, line)) {
      const auto first = line.find_first_not_of(" \t\r");
      if (first == std::string::npos || line[first] == '#') continue;
      const auto last = line.find_last_not_of(" \t\r");
      files.push_back(line.substr(first, last - first + 1));
    }
    if (files.empty()) throw std::runtime_error("input list is empty");
    return files;
  }
  return {input};
}

TH1D* SumMultiplicity(const std::vector<std::string>& inputs) {
  TH1D* sum = nullptr;
  for (const auto& input : inputs) {
    TFile file(input.c_str(), "READ");
    auto* histogram = dynamic_cast<TH1D*>(file.Get("hMULTIPLICITY"));
    if (!histogram) {
      throw std::runtime_error("missing hMULTIPLICITY in " + input);
    }
    if (!sum) {
      sum = dynamic_cast<TH1D*>(histogram->Clone("summed MULTIPLICITY"));
      sum->SetDirectory(nullptr);
      sum->Reset();
      sum->Sumw2();
    }
    sum->Add(histogram);
  }
  return sum;
}

std::vector<double> PtEdges() {
  std::vector<double> edges;
  for (int bin = 0; bin <= 100; ++bin) edges.push_back(0.5 * bin);
  for (double edge : {60., 75., 100., 150., 250., 500., 1000., 2000.,
                      4000., 7000.}) {
    edges.push_back(edge);
  }
  return edges;
}

THnSparseD* MakeSingle(const char* name) {
  const std::vector<double> ptEdges = PtEdges();
  const int bins[4] = {100, 100, static_cast<int>(ptEdges.size()) - 1, 4096};
  const double minimum[4] = {-M_PI, -4.0, 0.0, -0.5};
  const double maximum[4] = {M_PI, 4.0, 7000.0, 4095.5};
  auto* histogram = new THnSparseD(name, "(phi,eta,pt,Nch)", 4, bins,
                                   minimum, maximum);
  histogram->GetAxis(2)->Set(bins[2], ptEdges.data());
  histogram->GetAxis(0)->SetTitle("#phi");
  histogram->GetAxis(1)->SetTitle("#eta");
  histogram->GetAxis(2)->SetTitle("p_{T} (GeV/c)");
  histogram->GetAxis(3)->SetTitle("N_{ch}^{hadronisation}");
  histogram->Sumw2();
  return histogram;
}

THnSparseD* MakeCorrelation(const char* name, bool withOrigin) {
  const std::vector<double> ptEdges = PtEdges();
  const int dimensions = withOrigin ? 8 : 7;
  int bins[8] = {100, 100, 100, 100,
                 static_cast<int>(ptEdges.size()) - 1,
                 static_cast<int>(ptEdges.size()) - 1, 4096, 6};
  double minimum[8] = {-M_PI / 2.0, -8.0, -4.0, -4.0,
                       0.0, 0.0, -0.5, 0.5};
  double maximum[8] = {3.0 * M_PI / 2.0, 8.0, 4.0, 4.0,
                       7000.0, 7000.0, 4095.5, 6.5};
  auto* histogram = new THnSparseD(
      name,
      withOrigin ? "(dphi,deta,trEta,asEta,trPt,asPt,Nch,associateOrigin)"
                 : "(dphi,deta,trEta,asEta,trPt,asPt,Nch)",
      dimensions, bins, minimum, maximum);
  histogram->GetAxis(4)->Set(bins[4], ptEdges.data());
  histogram->GetAxis(5)->Set(bins[5], ptEdges.data());
  histogram->GetAxis(0)->SetTitle("#Delta#phi");
  histogram->GetAxis(1)->SetTitle("#Delta#eta");
  histogram->GetAxis(2)->SetTitle("#eta^{trig}");
  histogram->GetAxis(3)->SetTitle("#eta^{assoc}");
  histogram->GetAxis(4)->SetTitle("p_{T}^{trig} (GeV/c)");
  histogram->GetAxis(5)->SetTitle("p_{T}^{assoc} (GeV/c)");
  histogram->GetAxis(6)->SetTitle("N_{ch}^{hadronisation}");
  if (withOrigin) histogram->GetAxis(7)->SetTitle("associate origin category");
  histogram->Sumw2();
  return histogram;
}

bool EligibleBase(int pdg, int status, int isFinal, int central, double pt,
                  double eta, bool trigger) {
  return isFinal && central && Hadronization::FindGroundState(pdg) &&
         Hadronization::IsDirectPrimaryStatus(status) &&
         Hadronization::IsCentralKinematic(pt, eta, trigger);
}

int SectorCharge(const std::string& sector, int qc, int qb) {
  return sector == "charm" ? qc : qb;
}

int SectorOrigin(const std::string& sector, int originC, int originB) {
  return sector == "charm" ? originC : originB;
}

int SectorHardIndex(const std::string& sector, int hardC, int hardB) {
  return sector == "charm" ? hardC : hardB;
}

// 1 selected hard companion, 2 selected hard noncompanion, 3 shower,
// 4 MPI, 5 other resolved, 6 unresolved.
int AssociateOriginCategory(int origin, int associateHard,
                            int triggerHard, int associateSectorCharge,
                            int triggerSectorCharge) {
  if (origin == static_cast<int>(Origin::kSelectedHard)) {
    if (associateHard >= 0 && associateHard != triggerHard &&
        associateSectorCharge * triggerSectorCharge < 0) {
      return 1;
    }
    return 2;
  }
  if (origin == static_cast<int>(Origin::kShower)) return 3;
  if (origin == static_cast<int>(Origin::kMPI)) return 4;
  if (origin == static_cast<int>(Origin::kOtherResolved)) return 5;
  return 6;
}

}  // namespace

int status_analysis_THnSparse_qq(
    const char* inputPath, const char* outputDirectory,
    const char* selectionMode = "central_primary_ground_v1") {
  if (std::string(selectionMode) != "central_primary_ground_v1") {
    std::cerr << "ERROR: unsupported selection mode. Use the separate "
                 "status_analysis_THnSparse_qq_legacy.C for legacy results.\n";
    return 2;
  }
  try {
    const std::vector<std::string> inputs = ResolveInputs(inputPath);
    gSystem->mkdir(outputDirectory, true);
    std::unique_ptr<TH1D> multiplicity(SumMultiplicity(inputs));
    if (multiplicity->GetBinContent(multiplicity->GetNbinsX() + 1) != 0.0) {
      throw std::runtime_error("central multiplicity overflow is nonzero");
    }

    TChain chain("tree");
    for (const auto& input : inputs) {
      if (chain.Add(input.c_str()) == 0) {
        throw std::runtime_error("cannot add raw input " + input);
      }
    }
    const std::vector<const char*> requiredBranches = {
        "event_weight", "multiplicity_hadronisation_v1", "heavyIndex",
        "heavyPdg", "heavyStatus", "heavyIsFinal", "heavyCentral", "heavyQc",
        "heavyQb", "heavyOriginC", "heavyOriginB", "heavyMatchedHardC",
        "heavyMatchedHardB", "heavyPt", "heavyEta", "heavyPhi"};
    for (const char* branch : requiredBranches) {
      if (!chain.GetBranch(branch)) {
        throw std::runtime_error(std::string("missing raw branch ") + branch);
      }
    }

    std::map<std::pair<int, int>, std::size_t> pairLookup;
    std::vector<PairAccumulator> pairs;
    pairs.reserve(Hadronization::kPairDefinitions.size());
    for (const auto& definition : Hadronization::kPairDefinitions) {
      PairAccumulator accumulator;
      accumulator.definition = &definition;
      accumulator.associate = MakeSingle("hAsKinematics");
      accumulator.correlation = MakeCorrelation("hCorrelations", false);
      accumulator.correlationByOrigin =
          MakeCorrelation("hCorrelationsByOrigin", true);
      pairLookup[{definition.triggerPdg, definition.associatePdg}] =
          pairs.size();
      pairs.push_back(accumulator);
    }

    std::map<int, TriggerAccumulator> triggers;
    for (const auto& definition : Hadronization::kPairDefinitions) {
      if (triggers.count(definition.triggerPdg)) continue;
      TriggerAccumulator trigger;
      trigger.pdg = definition.triggerPdg;
      trigger.sector = std::string(definition.sector);
      trigger.histogram = MakeSingle("hTrKinematics");
      triggers.emplace(trigger.pdg, trigger);
    }

    Double_t eventWeight = 0.0;
    Int_t eventMultiplicity = 0;
    std::vector<int>* heavyIndex = nullptr;
    std::vector<int>* heavyPdg = nullptr;
    std::vector<int>* heavyStatus = nullptr;
    std::vector<int>* heavyIsFinal = nullptr;
    std::vector<int>* heavyCentral = nullptr;
    std::vector<int>* heavyQc = nullptr;
    std::vector<int>* heavyQb = nullptr;
    std::vector<int>* heavyOriginC = nullptr;
    std::vector<int>* heavyOriginB = nullptr;
    std::vector<int>* heavyMatchedHardC = nullptr;
    std::vector<int>* heavyMatchedHardB = nullptr;
    std::vector<double>* heavyPt = nullptr;
    std::vector<double>* heavyEta = nullptr;
    std::vector<double>* heavyPhi = nullptr;
    chain.SetBranchAddress("event_weight", &eventWeight);
    chain.SetBranchAddress("multiplicity_hadronisation_v1", &eventMultiplicity);
    chain.SetBranchAddress("heavyIndex", &heavyIndex);
    chain.SetBranchAddress("heavyPdg", &heavyPdg);
    chain.SetBranchAddress("heavyStatus", &heavyStatus);
    chain.SetBranchAddress("heavyIsFinal", &heavyIsFinal);
    chain.SetBranchAddress("heavyCentral", &heavyCentral);
    chain.SetBranchAddress("heavyQc", &heavyQc);
    chain.SetBranchAddress("heavyQb", &heavyQb);
    chain.SetBranchAddress("heavyOriginC", &heavyOriginC);
    chain.SetBranchAddress("heavyOriginB", &heavyOriginB);
    chain.SetBranchAddress("heavyMatchedHardC", &heavyMatchedHardC);
    chain.SetBranchAddress("heavyMatchedHardB", &heavyMatchedHardB);
    chain.SetBranchAddress("heavyPt", &heavyPt);
    chain.SetBranchAddress("heavyEta", &heavyEta);
    chain.SetBranchAddress("heavyPhi", &heavyPhi);

    unsigned long long sameHardConstituentPairs = 0;
    unsigned long long invalidVectorEvents = 0;
    double totalWeight = 0.0;
    for (Long64_t event = 0; event < chain.GetEntries(); ++event) {
      chain.GetEntry(event);
      totalWeight += eventWeight;
      const std::size_t size = heavyPdg->size();
      if (heavyIndex->size() != size || heavyStatus->size() != size ||
          heavyIsFinal->size() != size || heavyCentral->size() != size ||
          heavyQc->size() != size || heavyQb->size() != size ||
          heavyOriginC->size() != size || heavyOriginB->size() != size ||
          heavyMatchedHardC->size() != size ||
          heavyMatchedHardB->size() != size || heavyPt->size() != size ||
          heavyEta->size() != size || heavyPhi->size() != size) {
        ++invalidVectorEvents;
        continue;
      }
      for (std::size_t triggerIndex = 0; triggerIndex < size; ++triggerIndex) {
        const int triggerPdg = (*heavyPdg)[triggerIndex];
        auto triggerIterator = triggers.find(triggerPdg);
        if (triggerIterator == triggers.end()) continue;
        TriggerAccumulator& trigger = triggerIterator->second;
        const std::string& sector = trigger.sector;
        const int triggerOrigin =
            SectorOrigin(sector, (*heavyOriginC)[triggerIndex],
                         (*heavyOriginB)[triggerIndex]);
        if (!EligibleBase(triggerPdg, (*heavyStatus)[triggerIndex],
                          (*heavyIsFinal)[triggerIndex],
                          (*heavyCentral)[triggerIndex],
                          (*heavyPt)[triggerIndex], (*heavyEta)[triggerIndex],
                          true) ||
            triggerOrigin != static_cast<int>(Origin::kSelectedHard)) {
          continue;
        }
        const int triggerCharge =
            SectorCharge(sector, (*heavyQc)[triggerIndex],
                         (*heavyQb)[triggerIndex]);
        const int triggerHard =
            SectorHardIndex(sector, (*heavyMatchedHardC)[triggerIndex],
                            (*heavyMatchedHardB)[triggerIndex]);
        if (triggerCharge == 0 || triggerHard < 0) continue;

        const double triggerValues[4] = {
            Hadronization::WrapAbsolutePhi((*heavyPhi)[triggerIndex]),
            (*heavyEta)[triggerIndex], (*heavyPt)[triggerIndex],
            static_cast<double>(eventMultiplicity)};
        trigger.histogram->Fill(triggerValues, eventWeight);
        trigger.weightedTriggers += eventWeight;
        ++trigger.triggers;

        for (std::size_t associateIndex = 0; associateIndex < size;
             ++associateIndex) {
          if ((*heavyIndex)[associateIndex] == (*heavyIndex)[triggerIndex]) {
            continue;
          }
          const int associatePdg = (*heavyPdg)[associateIndex];
          const auto pairIterator =
              pairLookup.find({triggerPdg, associatePdg});
          if (pairIterator == pairLookup.end()) continue;
          if (!EligibleBase(associatePdg, (*heavyStatus)[associateIndex],
                            (*heavyIsFinal)[associateIndex],
                            (*heavyCentral)[associateIndex],
                            (*heavyPt)[associateIndex],
                            (*heavyEta)[associateIndex], false)) {
            continue;
          }
          const int associateCharge =
              SectorCharge(sector, (*heavyQc)[associateIndex],
                           (*heavyQb)[associateIndex]);
          if (associateCharge == 0) continue;
          PairAccumulator& pair = pairs[pairIterator->second];
          const bool expectedOS = pair.definition->heavySign == "OS";
          if ((triggerCharge * associateCharge < 0) != expectedOS) {
            throw std::runtime_error("pair-registry heavy-sign mismatch");
          }
          const int associateHard =
              SectorHardIndex(sector, (*heavyMatchedHardC)[associateIndex],
                              (*heavyMatchedHardB)[associateIndex]);
          if (associateHard >= 0 && associateHard == triggerHard) {
            ++sameHardConstituentPairs;
            if (sameHardConstituentPairs <= 20) {
              std::cerr << "SAME_HARD_CONSTITUENT event=" << event
                        << " trigger_pdg=" << triggerPdg
                        << " associate_pdg=" << associatePdg
                        << " trigger_index=" << (*heavyIndex)[triggerIndex]
                        << " associate_index=" << (*heavyIndex)[associateIndex]
                        << " hard_index=" << triggerHard
                        << " trigger_status=" << (*heavyStatus)[triggerIndex]
                        << " associate_status=" << (*heavyStatus)[associateIndex]
                        << "\n";
            }
            continue;
          }
          const int associateOrigin =
              SectorOrigin(sector, (*heavyOriginC)[associateIndex],
                           (*heavyOriginB)[associateIndex]);
          const int originCategory = AssociateOriginCategory(
              associateOrigin, associateHard, triggerHard, associateCharge,
              triggerCharge);
          const double associateValues[4] = {
              Hadronization::WrapAbsolutePhi((*heavyPhi)[associateIndex]),
              (*heavyEta)[associateIndex], (*heavyPt)[associateIndex],
              static_cast<double>(eventMultiplicity)};
          const double correlationValues[7] = {
              Hadronization::WrapDeltaPhi((*heavyPhi)[triggerIndex],
                                          (*heavyPhi)[associateIndex]),
              (*heavyEta)[triggerIndex] - (*heavyEta)[associateIndex],
              (*heavyEta)[triggerIndex], (*heavyEta)[associateIndex],
              (*heavyPt)[triggerIndex], (*heavyPt)[associateIndex],
              static_cast<double>(eventMultiplicity)};
          double originValues[8];
          std::copy(correlationValues, correlationValues + 7, originValues);
          originValues[7] = originCategory;
          pair.associate->Fill(associateValues, eventWeight);
          pair.correlation->Fill(correlationValues, eventWeight);
          pair.correlationByOrigin->Fill(originValues, eventWeight);
          pair.weightedPairs += eventWeight;
          ++pair.pairs;
        }
      }
    }
    if (invalidVectorEvents != 0) {
      throw std::runtime_error("raw vector-size mismatches: " +
                               std::to_string(invalidVectorEvents));
    }
    if (sameHardConstituentPairs != 0) {
      throw std::runtime_error("distinct pairs matched the same hard constituent: " +
                               std::to_string(sameHardConstituentPairs));
    }

    const std::string analysisSchema = "paul_pair_objects_primary_ground_v1";
    for (auto& pair : pairs) {
      const std::string path =
          std::string(outputDirectory) + "/" +
          std::string(pair.definition->filename);
      TFile output(path.c_str(), "RECREATE");
      if (output.IsZombie()) {
        throw std::runtime_error("cannot create " + path);
      }
      multiplicity->Write("summed MULTIPLICITY");
      TriggerAccumulator& trigger = triggers.at(pair.definition->triggerPdg);
      trigger.histogram->Write("hTrKinematics");
      pair.associate->Write("hAsKinematics");
      pair.correlation->Write("hCorrelations");
      pair.correlationByOrigin->Write("hCorrelationsByOrigin");
      TObjString schema(analysisSchema.c_str());
      schema.Write("analysis_schema");
      TObjString selector(Hadronization::kSelectorVersion);
      selector.Write("selector_version");
      TObjString speciesSha(
          std::string(Hadronization::kSpeciesRegistrySha256).c_str());
      speciesSha.Write("species_registry_sha256");
      TObjString pairSha(
          std::string(Hadronization::kPairRegistrySha256).c_str());
      pairSha.Write("pair_registry_sha256");
      TObjString sector(std::string(pair.definition->sector).c_str());
      sector.Write("heavy_sector");
      TObjString sign(std::string(pair.definition->heavySign).c_str());
      sign.Write("heavy_sign");
      TParameter<int>("trigger_pdg", pair.definition->triggerPdg).Write();
      TParameter<int>("associate_pdg", pair.definition->associatePdg).Write();
      TParameter<int>("reference_meson_pdg",
                      pair.definition->referenceMesonPdg).Write();
      TParameter<double>("trigger_pt_min_exclusive", 1.0).Write();
      TParameter<double>("associate_pt_min_exclusive", 0.15).Write();
      TParameter<double>("eta_abs_max_inclusive", 4.0).Write();
      TParameter<Long64_t>("input_events", chain.GetEntries()).Write();
      TParameter<double>("input_sum_weights", totalWeight).Write();
      TParameter<Long64_t>("trigger_count",
                           static_cast<Long64_t>(trigger.triggers)).Write();
      TParameter<double>("trigger_sum_weights",
                         trigger.weightedTriggers).Write();
      TParameter<Long64_t>("pair_count",
                           static_cast<Long64_t>(pair.pairs)).Write();
      TParameter<double>("pair_sum_weights", pair.weightedPairs).Write();
      output.Write();
      output.Close();
    }

    for (auto& pair : pairs) {
      delete pair.associate;
      delete pair.correlation;
      delete pair.correlationByOrigin;
    }
    for (auto& item : triggers) delete item.second.histogram;
    std::cout << "ONE_PASS_ANALYSIS_SUMMARY inputs=" << inputs.size()
              << " events=" << chain.GetEntries()
              << " pairs_written=" << pairs.size()
              << " same_hard_constituent_pairs=" << sameHardConstituentPairs
              << " selection=" << selectionMode << "\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "ONE_PASS_ANALYSIS_ERROR " << error.what() << "\n";
    return 1;
  }
}
