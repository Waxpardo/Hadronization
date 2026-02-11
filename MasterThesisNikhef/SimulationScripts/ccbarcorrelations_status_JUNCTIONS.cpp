// ccbarcorrelations_status_JUNCTIONS.cpp
//
// The variables saved are necessary to create azimuthal angular correlation plots for beauty hadrons, which are defined as follows:   
// pT = transverse momentum
// eta = pseudorapidity
// phi = azimuthal angle
// ID = PDG ID of particle
// mother = index of mother particle
// motherID = PDG ID of mother particle
//
// Build example (adjust to your environment):
//   g++ -O2 -std=c++17 ccbarcorrelations_status_JUNCTIONS.cpp \
//       $(pythia8-config --cxxflags --libs) $(root-config --cflags --libs) \
//       -o ccbarcorrelations_status_JUNCTIONS
//
// Run:
//   ./ccbarcorrelations_status_JUNCTIONS output.root 123 456

#include <iostream>
#include <cmath>
#include <chrono>
#include <vector>
#include <string>
#include <unistd.h>   // getpid()

#include "Pythia8/Pythia.h"

#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"

#define PI 3.14159265358979323846

using namespace std;
using namespace Pythia8;

// Simple function that checks if a particle has any charm content
bool IsCharm(int particlepdg) {
  int pdg = std::abs(particlepdg);
  pdg /= 10; // last digit not quark content
  if (pdg % 10 == 4) return true;
  pdg /= 10;
  if (pdg % 10 == 4) return true;
  pdg /= 10;
  if (pdg % 10 == 4) return true;
  return false;
}

bool IsPion(int particlepdg) {
  const int apdg = std::abs(particlepdg);
  return (apdg == 211 || apdg == 111); // pi± or pi0
}

// Returns delta phi in range [-pi/2, 3pi/2)
double DeltaPhi(double phi1, double phi2) {
  return std::fmod(phi1 - phi2 + 2.5 * PI, 2.0 * PI) - 0.5 * PI;
}

// "Primary" charged particles used for multiplicity definition
bool IsChargedPrimaryForMult(int pdgAbs) {
  return (pdgAbs == 11   || // e
          pdgAbs == 13   || // mu
          pdgAbs == 211  || // pi
          pdgAbs == 321  || // K
          pdgAbs == 2212);  // p
}

// Prompt-like selection using status codes (kept to match your original intent)
bool IsPromptByStatus(int status) {
  return (status >= 81 && status <= 89);
}

int main(int argc, char** argv) {
  auto start = std::chrono::high_resolution_clock::now();

  if (argc != 4) {
    std::cout << "Error: wrong number of arguments.\n"
              << "Expected:\n"
              << "  ./ccbarcorrelations_status_JUNCTIONS output_name.root random_number1 random_number2\n";
    return 1;
  }

  const char* outName = argv[1];

  // Create output ROOT file; fail if it already exists
  TFile* output = TFile::Open(outName, "CREATE");
  if (!output || output->IsZombie()) {
    std::cerr << "Error: could not create output file '" << outName
              << "'. It may already exist or the path is invalid.\n";
    if (output) output->Close();
    return 1;
  }

  // Define TTree
  TTree* tree = new TTree("tree", "ccbar correlations (JUNCTIONS)");

  // Scalars
  Int_t MULTIPLICITY = 0;
  Int_t nEvents = 0;
  Int_t charmness = 0;

  // Event-level vectors
  std::vector<Int_t>    vID;
  std::vector<Double_t> vPt;
  std::vector<Double_t> vEta;
  std::vector<Double_t> vY;
  std::vector<Double_t> vPhi;
  std::vector<Double_t> vCharge;
  std::vector<Double_t> vStatus;
  std::vector<Double_t> vMother1;
  std::vector<Double_t> vMotherID;

  // Branches
  tree->Branch("ID",       &vID);
  tree->Branch("PT",       &vPt);
  tree->Branch("ETA",      &vEta);
  tree->Branch("Y",        &vY);
  tree->Branch("PHI",      &vPhi);
  tree->Branch("CHARGE",   &vCharge);
  tree->Branch("STATUS",   &vStatus);
  tree->Branch("MOTHER",   &vMother1);
  tree->Branch("MOTHERID", &vMotherID);
  tree->Branch("MULTIPLICITY", &MULTIPLICITY, "MULTIPLICITY/I");

  // QA histograms
  TH1D* hMULTIPLICITY = new TH1D("hMULTIPLICITY", "Multiplicity;N_{ch};Events", 301, -0.5, 300.5);
  TH1D* hidCharm      = new TH1D("hidCharm",      "PDG Codes for Charm hadrons;PDG;Counts", 12000, -6000, 6000);
  TH1D* hPtTrigger    = new TH1D("hPtTrigger",    "p_{T} for trigger D^{0};p_{T} (GeV/c);Counts", 50, 0, 10);
  TH1D* hPtAssociate  = new TH1D("hPtAssociate",  "p_{T} for associate #bar{D}^{0};p_{T} (GeV/c);Counts", 50, 0, 10);
  TH1D* hDeltaPhiDD   = new TH1D("hDeltaPhiDD",   "D^{0}#bar{D}^{0} correlations;#Delta#phi;Counts", 100, -PI/2, 3*PI/2);
  TH1D* hCharmPart    = new TH1D("hCharmPart",    "Charm Particles Per Event;N_{charm};Events", 200, -0.5, 200.5);

  // Acceptance
  const double pTmin  = 0.15;
  const double etamax = 4.0;

  // Setup PYTHIA
  Pythia pythia;

  // JUNCTIONS settings for ccbar
  pythia.readFile("pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd");
  nEvents = pythia.mode("Main:numberOfEvents");

  // Random seed
  const int processid = getpid();
  const int seedMod1  = std::stoi(argv[2]);
  const int seedMod2  = std::stoi(argv[3]);

  const int seed = (static_cast<int>(time(nullptr)) + processid + seedMod1 + seedMod2) % 900000000;
  pythia.readString("Random:setSeed = on");
  pythia.readString("Random:seed = " + std::to_string(seed));

  // Init
  pythia.init();
  std::cout << "Generating " << nEvents << " events (ccbar JUNCTIONS) with seed " << seed << "...\n";

  // Event loop
  for (int iEvent = 0; iEvent < nEvents; ++iEvent) {
    if (!pythia.next()) continue;

    const int nPart = pythia.event.size();

    MULTIPLICITY = 0;
    charmness    = 0;

    vID.clear();
    vPt.clear();
    vEta.clear();
    vY.clear();
    vPhi.clear();
    vCharge.clear();
    vStatus.clear();
    vMother1.clear();
    vMotherID.clear();

    // Particle loop: compute multiplicity + save (charm OR pions)
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

      // Multiplicity selection (charged primaries within acceptance)
      if (pT >= pTmin && std::abs(eta) <= etamax) {
        if (IsChargedPrimaryForMult(apdg) && particle.isCharged()) {
          if (IsPromptByStatus(istat)) {
            MULTIPLICITY++;
          }
        }
      }

      // Save to tree: charm hadrons OR pions (pi±, pi0), within acceptance
      if (!(IsCharm(id) || IsPion(id))) continue;
      if (pT < pTmin || std::abs(eta) > etamax) continue;

      // Safe mother access
      const int m1  = particle.mother1();
      const int mID = (m1 > 0 && m1 < nPart) ? pythia.event[m1].id() : 0;

      // Charm QA counting (only count charm here)
      if (IsCharm(id)) {
        hidCharm->Fill(static_cast<double>(id));
        charmness++;
      }

      // Fill vectors
      vID.push_back(id);
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

    // QA: D0 - D0bar correlations (final-state only + acceptance)
    for (int iPart = 0; iPart < nPart; ++iPart) {
      const Particle& pTrig = pythia.event[iPart];
      if (!pTrig.isFinal()) continue;
      if (pTrig.id() != 421) continue; // D0
      if (pTrig.pT() < pTmin || std::abs(pTrig.eta()) > etamax) continue;

      for (int jPart = 0; jPart < nPart; ++jPart) {
        if (jPart == iPart) continue;
        const Particle& pAssoc = pythia.event[jPart];
        if (!pAssoc.isFinal()) continue;
        if (pAssoc.id() != -421) continue; // anti-D0
        if (pAssoc.pT() < pTmin || std::abs(pAssoc.eta()) > etamax) continue;

        const double dphi = DeltaPhi(pTrig.phi(), pAssoc.phi());
        hPtTrigger->Fill(pTrig.pT());
        hPtAssociate->Fill(pAssoc.pT());
        hDeltaPhiDD->Fill(dphi);
      }
    }

    // Keep consistent with your existing workflow: don't store empty events
    if (vID.empty()) continue;

    tree->Fill();
  }

  // Write output and close it
  output->cd();
  tree->Write();
  hMULTIPLICITY->Write();
  hidCharm->Write();
  hPtTrigger->Write();
  hPtAssociate->Write();
  hDeltaPhiDD->Write();
  hCharmPart->Write();

  std::cout << "File created: " << output->GetName() << "\n";
  output->Close();

  auto end = std::chrono::high_resolution_clock::now();
  auto duration = std::chrono::duration_cast<std::chrono::minutes>(end - start);
  std::cout << "This script took " << duration.count() << " minutes to run.\n";

  return 0;
}
