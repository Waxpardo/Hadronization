// heavyflavourcorrelations_status.cpp
//
// Purpose:
// - Generate pp events with PYTHIA8 in a single run
// - Enable both hard charm and hard beauty production
// - Save final-state charm hadrons, beauty hadrons, and pions (pi+, pi-, pi0) into a ROOT TTree
// - Compute charged multiplicity Nch from prompt charged primaries (e, mu, pi, K, p)
//
// Notes:
// - This is a single PYTHIA generation, not two separate runs.
// - The same generated event record is scanned for both charm and beauty hadrons.
// - To work properly, your settings must enable both ccbar and bbbar hard processes.
//
// Build example:
//   g++ -O2 -std=c++17 heavyflavourcorrelations_status.cpp \
//       $(pythia8-config --cxxflags --libs) $(root-config --cflags --libs) \
//       -o heavyflavourcorrelations_status
//
// Run:
//   ./heavyflavourcorrelations_status output.root 123 456

#include <iostream>
#include <cmath>
#include <chrono>
#include <ctime>
#include <vector>
#include <string>
#include <cstdlib>
#include <unistd.h>   // getpid()

#include "Pythia8/Pythia.h"

#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"

#define PI 3.14159265358979323846

using namespace std;
using namespace Pythia8;

// ---------------------------------------------------------
// Helper functions
// ---------------------------------------------------------

bool IsBeauty(int particlepdg) {
  int pdg = std::abs(particlepdg);
  pdg /= 10; // drop last digit
  if (pdg % 10 == 5) return true;
  pdg /= 10;
  if (pdg % 10 == 5) return true;
  pdg /= 10;
  if (pdg % 10 == 5) return true;
  return false;
}

bool IsCharm(int particlepdg) {
  int pdg = std::abs(particlepdg);
  pdg /= 10; // drop last digit
  if (pdg % 10 == 4) return true;
  pdg /= 10;
  if (pdg % 10 == 4) return true;
  pdg /= 10;
  if (pdg % 10 == 4) return true;
  return false;
}

bool IsPion(int particlepdg) {
  const int apdg = std::abs(particlepdg);
  return (apdg == 211 || apdg == 111);
}

double DeltaPhi(double phi1, double phi2) {
  return std::fmod(phi1 - phi2 + 2.5 * PI, 2.0 * PI) - 0.5 * PI;
}

bool IsChargedPrimaryForMult(int pdgAbs) {
  return (pdgAbs == 11   || // e
          pdgAbs == 13   || // mu
          pdgAbs == 211  || // pi
          pdgAbs == 321  || // K
          pdgAbs == 2212);  // p
}

bool IsPromptByStatus(int status) {
  return (status >= 81 && status <= 89);
}

// Optional per-particle class:
// 5 = beauty hadron
// 4 = charm hadron
// 0 = pion
int HFClass(int pdg) {
  if (IsBeauty(pdg)) return 5;
  if (IsCharm(pdg))  return 4;
  if (IsPion(pdg))   return 0;
  return -1;
}

int main(int argc, char** argv) {
  auto start = std::chrono::high_resolution_clock::now();

  if (argc != 4) {
    std::cout << "Error: wrong number of arguments.\n"
              << "Expected:\n"
              << "  ./heavyflavourcorrelations_status output.root random_number1 random_number2\n";
    return 1;
  }

  const char* outName = argv[1];

  TFile* output = TFile::Open(outName, "CREATE");
  if (!output || output->IsZombie()) {
    std::cerr << "Error: could not create output file '" << outName
              << "'. It may already exist or path is invalid.\n";
    if (output) output->Close();
    return 1;
  }

  // ---------------------------------------------------------
  // Tree definition
  // ---------------------------------------------------------
  TTree* tree = new TTree("tree", "combined charm+beauty correlations");

  Int_t MULTIPLICITY = 0;
  Int_t nEvents = 0;
  Int_t charmness = 0;
  Int_t beautiness = 0;

  std::vector<Int_t>    vID;
  std::vector<Int_t>    vHFCLASS;
  std::vector<Double_t> vPt;
  std::vector<Double_t> vEta;
  std::vector<Double_t> vY;
  std::vector<Double_t> vPhi;
  std::vector<Double_t> vCharge;
  std::vector<Double_t> vStatus;
  std::vector<Double_t> vMother1;
  std::vector<Double_t> vMotherID;

  tree->Branch("ID",           &vID);
  tree->Branch("HFCLASS",      &vHFCLASS);
  tree->Branch("PT",           &vPt);
  tree->Branch("ETA",          &vEta);
  tree->Branch("Y",            &vY);
  tree->Branch("PHI",          &vPhi);
  tree->Branch("CHARGE",       &vCharge);
  tree->Branch("STATUS",       &vStatus);
  tree->Branch("MOTHER",       &vMother1);
  tree->Branch("MOTHERID",     &vMotherID);
  tree->Branch("MULTIPLICITY", &MULTIPLICITY, "MULTIPLICITY/I");
  tree->Branch("NCHARM",       &charmness,    "NCHARM/I");
  tree->Branch("NBEAUTY",      &beautiness,   "NBEAUTY/I");

  // ---------------------------------------------------------
  // Histograms
  // ---------------------------------------------------------
  TH1D* hMULTIPLICITY = new TH1D("hMULTIPLICITY", "Multiplicity;N_{ch};Events", 301, -0.5, 300.5);

  TH1D* hidCharm  = new TH1D("hidCharm",  "PDG Codes for Charm hadrons;PDG;Counts", 12000, -6000, 6000);
  TH1D* hidBeauty = new TH1D("hidBeauty", "PDG Codes for Beauty hadrons;PDG;Counts", 12000, -6000, 6000);

  TH1D* hCharmPart  = new TH1D("hCharmPart",  "Charm particles per event;N_{charm};Events",   200, -0.5, 200.5);
  TH1D* hBeautyPart = new TH1D("hBeautyPart", "Beauty particles per event;N_{beauty};Events", 200, -0.5, 200.5);

  TH1D* hPtTriggerDD   = new TH1D("hPtTriggerDD",   "p_{T} for trigger D^{0};p_{T} (GeV/c);Counts", 50, 0, 10);
  TH1D* hPtAssociateDD = new TH1D("hPtAssociateDD", "p_{T} for associate #bar{D}^{0};p_{T} (GeV/c);Counts", 50, 0, 10);
  TH1D* hDeltaPhiDD    = new TH1D("hDeltaPhiDD",    "D^{0}#bar{D}^{0} correlations;#Delta#phi;Counts", 100, -PI/2, 3*PI/2);

  TH1D* hPtTriggerBB   = new TH1D("hPtTriggerBB",   "p_{T} for trigger B^{+};p_{T} (GeV/c);Counts", 50, 0, 10);
  TH1D* hPtAssociateBB = new TH1D("hPtAssociateBB", "p_{T} for associate B^{-};p_{T} (GeV/c);Counts", 50, 0, 10);
  TH1D* hDeltaPhiBB    = new TH1D("hDeltaPhiBB",    "B^{+}B^{-} correlations;#Delta#phi;Counts", 100, -PI/2, 3*PI/2);

  // ---------------------------------------------------------
  // Kinematic acceptance
  // ---------------------------------------------------------
  const double pTmin  = 0.15;
  const double etamax = 4.0;

  // ---------------------------------------------------------
  // PYTHIA setup: single generation, both charm and beauty enabled
  // ---------------------------------------------------------
  Pythia pythia;

  // Start from one of your existing settings files if you want,
  // but then explicitly force both charm and beauty hard processes on.
  //
  // You can replace this file with a dedicated combined settings file if preferred.
  pythia.readFile("pythiasettings_Hard_Low_cc.cmnd");

  // IMPORTANT:
  // Explicitly enable both heavy-flavour production channels in the SAME run.
  pythia.readString("HardQCD:gg2ccbar = on");
  pythia.readString("HardQCD:qqbar2ccbar = on");
  pythia.readString("HardQCD:gg2bbbar = on");
  pythia.readString("HardQCD:qqbar2bbbar = on");

  nEvents = pythia.mode("Main:numberOfEvents");

  const int processid = getpid();
  const int seedMod1  = std::stoi(argv[2]);
  const int seedMod2  = std::stoi(argv[3]);

  const int seed = (static_cast<int>(time(nullptr)) + processid + seedMod1 + seedMod2) % 900000000;
  pythia.readString("Random:setSeed = on");
  pythia.readString("Random:seed = " + std::to_string(seed));

  pythia.init();

  std::cout << "Generating " << nEvents
            << " events in a single PYTHIA run with both charm and beauty enabled, seed "
            << seed << "...\n";

  // ---------------------------------------------------------
  // Event loop
  // ---------------------------------------------------------
  for (int iEvent = 0; iEvent < nEvents; ++iEvent) {
    if (!pythia.next()) continue;

    const int nPart = pythia.event.size();

    MULTIPLICITY = 0;
    charmness    = 0;
    beautiness   = 0;

    vID.clear();
    vHFCLASS.clear();
    vPt.clear();
    vEta.clear();
    vY.clear();
    vPhi.clear();
    vCharge.clear();
    vStatus.clear();
    vMother1.clear();
    vMotherID.clear();

    // -----------------------------------------
    // Particle loop
    // -----------------------------------------
    for (int iPart = 0; iPart < nPart; ++iPart) {
      const Particle& particle = pythia.event[iPart];
      if (!particle.isFinal()) continue;

      const int    id     = particle.id();
      const int    apdg   = std::abs(id);
      const double pT     = particle.pT();
      const double eta    = particle.eta();
      const double y      = particle.y();
      const double phi    = particle.phi();
      const double charge = particle.charge();
      const int    istat  = particle.status();

      // Multiplicity from charged primaries in acceptance
      if (pT >= pTmin && std::abs(eta) <= etamax) {
        if (IsChargedPrimaryForMult(apdg) && particle.isCharged()) {
          if (IsPromptByStatus(istat)) {
            MULTIPLICITY++;
          }
        }
      }

      // Save charm hadrons, beauty hadrons, and pions
      const bool isC  = IsCharm(id);
      const bool isB  = IsBeauty(id);
      const bool isPi = IsPion(id);

      if (!(isC || isB || isPi)) continue;
      if (pT < pTmin || std::abs(eta) > etamax) continue;

      const int m1  = particle.mother1();
      const int mID = (m1 > 0 && m1 < nPart) ? pythia.event[m1].id() : 0;

      if (isC) {
        hidCharm->Fill(static_cast<double>(id));
        charmness++;
      }
      if (isB) {
        hidBeauty->Fill(static_cast<double>(id));
        beautiness++;
      }

      vID.push_back(id);
      vHFCLASS.push_back(HFClass(id));
      vPt.push_back(pT);
      vEta.push_back(eta);
      vY.push_back(y);
      vPhi.push_back(phi);
      vCharge.push_back(charge);
      vStatus.push_back(static_cast<double>(istat));
      vMother1.push_back(static_cast<double>(m1));
      vMotherID.push_back(static_cast<double>(mID));
    }

    hMULTIPLICITY->Fill(static_cast<double>(MULTIPLICITY));
    hCharmPart->Fill(static_cast<double>(charmness));
    hBeautyPart->Fill(static_cast<double>(beautiness));

    // -----------------------------------------
    // QA: D0 - anti-D0 correlations
    // -----------------------------------------
    for (int iPart = 0; iPart < nPart; ++iPart) {
      const Particle& pTrig = pythia.event[iPart];
      if (!pTrig.isFinal()) continue;
      if (pTrig.id() != 421) continue;
      if (pTrig.pT() < pTmin || std::abs(pTrig.eta()) > etamax) continue;

      for (int jPart = 0; jPart < nPart; ++jPart) {
        if (jPart == iPart) continue;
        const Particle& pAssoc = pythia.event[jPart];
        if (!pAssoc.isFinal()) continue;
        if (pAssoc.id() != -421) continue;
        if (pAssoc.pT() < pTmin || std::abs(pAssoc.eta()) > etamax) continue;

        const double dphi = DeltaPhi(pTrig.phi(), pAssoc.phi());
        hPtTriggerDD->Fill(pTrig.pT());
        hPtAssociateDD->Fill(pAssoc.pT());
        hDeltaPhiDD->Fill(dphi);
      }
    }

    // -----------------------------------------
    // QA: B+ - B- correlations
    // -----------------------------------------
    for (int iPart = 0; iPart < nPart; ++iPart) {
      const Particle& pTrig = pythia.event[iPart];
      if (!pTrig.isFinal()) continue;
      if (pTrig.id() != 521) continue;
      if (pTrig.pT() < pTmin || std::abs(pTrig.eta()) > etamax) continue;

      for (int jPart = 0; jPart < nPart; ++jPart) {
        if (jPart == iPart) continue;
        const Particle& pAssoc = pythia.event[jPart];
        if (!pAssoc.isFinal()) continue;
        if (pAssoc.id() != -521) continue;
        if (pAssoc.pT() < pTmin || std::abs(pAssoc.eta()) > etamax) continue;

        const double dphi = DeltaPhi(pTrig.phi(), pAssoc.phi());
        hPtTriggerBB->Fill(pTrig.pT());
        hPtAssociateBB->Fill(pAssoc.pT());
        hDeltaPhiBB->Fill(dphi);
      }
    }

    if (vID.empty()) continue;
    tree->Fill();
  }

  // ---------------------------------------------------------
  // Write output
  // ---------------------------------------------------------
  output->cd();
  tree->Write();

  hMULTIPLICITY->Write();
  hidCharm->Write();
  hidBeauty->Write();
  hCharmPart->Write();
  hBeautyPart->Write();

  hPtTriggerDD->Write();
  hPtAssociateDD->Write();
  hDeltaPhiDD->Write();

  hPtTriggerBB->Write();
  hPtAssociateBB->Write();
  hDeltaPhiBB->Write();

  std::cout << "File created: " << output->GetName() << "\n";
  output->Close();

  auto end = std::chrono::high_resolution_clock::now();
  auto duration = std::chrono::duration_cast<std::chrono::minutes>(end - start);
  std::cout << "This script took " << duration.count() << " minutes.\n";

  return 0;
}