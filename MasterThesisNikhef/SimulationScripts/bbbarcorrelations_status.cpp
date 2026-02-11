// bbbarcorrelations_status.cpp
//
// PYTHIA8 event generator + ROOT output
// - Generates pp -> bbbar events using settings from pythiasettings_Hard_Low_bb.cmnd
// - Saves BEAUTY final-state particles AND PIONS (pi+, pi-, pi0) into the output TTree
// - Computes multiplicity Nch from charged "primary" particles (e, mu, pi, K, p)
// The variables saved are necessary to create azimuthal angular correlation plots for beauty hadrons, which are defined as follows:
// pT = transverse momentum
// eta = pseudorapidity
// phi = azimuthal angle
// ID = PDG ID of particle
// mother = index of mother particle 
// motherID = PDG ID of mother particle
//
// Build example (adjust include/library flags as needed):
//   g++ -O2 -std=c++17 bbbarcorrelations_status.cpp \
//       $(pythia8-config --cxxflags --libs) $(root-config --cflags --libs) \
//       -o bbbarcorrelations_status
//
// Run:
//   ./bbbarcorrelations_status output.root 123 456

#include <iostream>
#include <cmath>
#include <chrono>
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

// Checks if a PDG code contains a b-quark using PDG digit structure.
bool IsBeauty(int particlepdg) {
  int pdg = std::abs(particlepdg);
  pdg /= 10;               // ignore last digit (spin/excitation)
  if (pdg % 10 == 5) return true;
  pdg /= 10;
  if (pdg % 10 == 5) return true;
  pdg /= 10;
  if (pdg % 10 == 5) return true;
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

// Prompt-like selection using status codes (kept to match your intent).
// Note: status-code semantics can vary with generator settings; if you want
// truly robust prompt definitions, use Pythia flags and/or ancestry checks.
bool IsPromptByStatus(int status) {
  return (status >= 81 && status <= 89);
}

int main(int argc, char** argv) {
  auto start = std::chrono::high_resolution_clock::now();

  if (argc != 4) {
    std::cout << "Error: wrong number of arguments.\n"
              << "Expected:\n"
              << "  ./bbbarcorrelations_status output_name.root random_number1 random_number2\n";
    return 1;
  }

  const char* outName = argv[1];

  // Create output ROOT file (RECREATE will overwrite existing; use CREATE if you want to fail instead)
  // If you want to *fail* if exists, use "CREATE". We'll implement that behavior:
  TFile* output = TFile::Open(outName, "CREATE");
  if (!output || output->IsZombie()) {
    std::cerr << "Error: could not create output file '" << outName
              << "'. It may already exist or path is invalid.\n";
    if (output) output->Close();
    return 1;
  }

  // Define output TTree
  TTree* tree = new TTree("tree", "bbbar correlations");

  // Scalars
  Int_t  MULTIPLICITY = 0;
  Int_t  nEvents = 0;
  Int_t  beautiness = 0;

  // Per-particle vectors saved to tree
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
  TH1D* hidBeauty     = new TH1D("hidBeauty",     "PDG Codes for Beauty hadrons;PDG;Counts", 12000, -6000, 6000);
  TH1D* hPtTrigger    = new TH1D("hPtTrigger",    "p_{T} for trigger B^{+};p_{T} (GeV/c);Counts", 50, 0, 10);
  TH1D* hPtAssociate  = new TH1D("hPtAssociate",  "p_{T} for associate B^{-};p_{T} (GeV/c);Counts", 50, 0, 10);
  TH1D* hDeltaPhiBB   = new TH1D("hDeltaPhiBB",   "B^{+}B^{-} correlations;#Delta#phi;Counts", 100, -PI/2, 3*PI/2);
  TH1D* hBeautyPart   = new TH1D("hBeautyPart",   "Beauty Particles Per Event;N_{beauty};Events", 200, -0.5, 200.5);

  // Kinematic constraints (applied to *saved* particles and to multiplicity counting)
  const double pTmin  = 0.15;
  const double etamax = 4.0;

  // Setup PYTHIA
  Pythia pythia;
  pythia.readFile("pythiasettings_Hard_Low_bb.cmnd");
  nEvents = pythia.mode("Main:numberOfEvents");

  // Random seed
  const int processid = getpid();
  const int seedMod1  = std::stoi(argv[2]);
  const int seedMod2  = std::stoi(argv[3]);

  const int seed = (static_cast<int>(time(nullptr)) + processid + seedMod1 + seedMod2) % 900000000;
  pythia.readString("Random:setSeed = on");
  pythia.readString("Random:seed = " + std::to_string(seed));

  pythia.init();

  std::cout << "Generating " << nEvents << " events with seed " << seed << "...\n";

  // Event loop
  for (int iEvent = 0; iEvent < nEvents; ++iEvent) {
    if (!pythia.next()) continue;

    const int nPart = pythia.event.size();

    MULTIPLICITY = 0;
    beautiness   = 0;

    vID.clear();
    vPt.clear();
    vEta.clear();
    vY.clear();
    vPhi.clear();
    vCharge.clear();
    vStatus.clear();
    vMother1.clear();
    vMotherID.clear();

    // Particle loop: compute multiplicity from final-state charged primaries,
    // and save final-state BEAUTY and PIONS with kinematic cuts.
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

      // multiplicity selection (charged primaries, within kinematic acceptance)
      if (pT >= pTmin && std::abs(eta) <= etamax) {
        if (IsChargedPrimaryForMult(apdg)) {
          // charged requirement: protect against any weirdness
          if (particle.isCharged()) {
            if (IsPromptByStatus(istat)) {
              MULTIPLICITY++;
            }
          }
        }
      }

      // Save to tree: BEAUTY hadrons OR PIONS (pi± and pi0), within kinematic acceptance
      if (!(IsBeauty(id) || IsPion(id))) continue;
      if (pT < pTmin || std::abs(eta) > etamax) continue;

      // Mother protection
      const int m1 = particle.mother1();
      const int motherID = (m1 > 0 && m1 < nPart) ? pythia.event[m1].id() : 0;

      // Count beauty entries saved (for QA)
      if (IsBeauty(id)) {
        hidBeauty->Fill(static_cast<double>(id));
        beautiness++;
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
      vMotherID.push_back(static_cast<double>(motherID));
    }

    hMULTIPLICITY->Fill(static_cast<double>(MULTIPLICITY));
    hBeautyPart->Fill(static_cast<double>(beautiness));

    // B+ B- correlation QA (use final-state only + acceptance)
    // Note: since you force many B hadrons stable in the .cmnd, they should appear as final.
    for (int iPart = 0; iPart < nPart; ++iPart) {
      const Particle& pTrig = pythia.event[iPart];
      if (!pTrig.isFinal()) continue;
      if (pTrig.id() != 521) continue; // B+
      if (pTrig.pT() < pTmin || std::abs(pTrig.eta()) > etamax) continue;

      for (int jPart = 0; jPart < nPart; ++jPart) {
        if (jPart == iPart) continue;
        const Particle& pAssoc = pythia.event[jPart];
        if (!pAssoc.isFinal()) continue;
        if (pAssoc.id() != -521) continue; // B-
        if (pAssoc.pT() < pTmin || std::abs(pAssoc.eta()) > etamax) continue;

        const double dphi = DeltaPhi(pTrig.phi(), pAssoc.phi());
        hPtTrigger->Fill(pTrig.pT());
        hPtAssociate->Fill(pAssoc.pT());
        hDeltaPhiBB->Fill(dphi);
      }
    }

    // Avoid filling empty events (optional: you can remove this if you want all events saved)
    if (vID.empty()) continue;

    tree->Fill();
  }

  output->cd();
  tree->Write();
  hMULTIPLICITY->Write();
  hidBeauty->Write();
  hPtTrigger->Write();
  hPtAssociate->Write();
  hDeltaPhiBB->Write();
  hBeautyPart->Write();

  std::cout << "File created: " << output->GetName() << "\n";
  output->Close();

  auto end = std::chrono::high_resolution_clock::now();
  auto duration = std::chrono::duration_cast<std::chrono::minutes>(end - start);
  std::cout << "This script took " << duration.count() << " minutes.\n";

  return 0;
}
