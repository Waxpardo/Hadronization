// cc_mult_pt_analysis_multi.C
//
// What it does:
// - Reads MANY ROOT files per tune from:
//     RootFiles/ccbar/MONASH/*.root
//     RootFiles/ccbar/JUNCTIONS/*.root
// - Each input file contains TTree "tree" with branches:
//     vector<int>    ID
//     vector<double> PT
//     int            MULTIPLICITY
// - Splits total stats into N subsamples via round-robin assignment
// - Writes one ROOT output per subsample per tune:
//     AnalyzedData/<tag>/Charm/ccbar_MONASH_sub0.root ... sub(N-1).root
//     AnalyzedData/<tag>/Charm/ccbar_JUNCTIONS_sub0.root ... sub(N-1).root
//
// Output histograms per subsample file:
//   TH1D fHistEventCount
//   TH1D fHistMultiplicity
//   TH2D fHistPDGMult
//   TH2D fHistPtCharmMesons
//   TH2D fHistPtCharmBaryons
//   TH2D fHistPtDplus, fHistPtDzero, fHistPtDsplus
//   TH2D fHistPtLambdacPlus, fHistPtLambdac, fHistPtSigmacPlusPlus, fHistPtSigmacPlus,
//        fHistPtSigmacZero, fHistPtXicPlus, fHistPtXicZero, fHistPtOmegacZero
//   TH2D fHistPtPionsCharged, fHistPtPiPlus, fHistPtPiMinus, fHistPtPi0
//
// Charge-conjugate mode:
// - "combined" (default): current species histograms stay charge-conjugate combined
// - "separate"          : the current combined histograms are still written, and
//                         extra particle-only / anti-particle histograms are added
//                         with the suffixes "Particle" and "Bar"
//
// Pion protection:
// - Counts pion entries found in the TTrees (pi±/pi0).
// - Prints WARNING if zero pions were stored (usually means producer didn't write them).
//
// Usage:
//   root -l -b -q 'AnalysisScripts/cc_mult_pt_analysis_multi.C+(10, "12-01-2026", "combined")'
// ----------------------------------------------------------------------

#include <vector>
#include <string>
#include <iostream>
#include <cmath>
#include <fstream>

#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TString.h"
#include "TError.h"
#include "TSystemDirectory.h"
#include "TSystemFile.h"
#include "TList.h"
#include "TCollection.h"
#include "TSystem.h"

namespace {

  // ---------- Base path resolution ----------

  TString GetBaseDir()
  {
    const char* env = gSystem->Getenv("HADRONIZATION_BASE");
    if (env && env[0] != '\0') return TString(env);

    std::ifstream fin("base_path.txt");
    if (fin) {
      std::string line;
      std::getline(fin, line);
      if (!line.empty()) return TString(line.c_str());
    }

    return TString(".");
  }

  TString SanitizeOutputTag(const char* outputTag)
  {
    TString tag = outputTag ? TString(outputTag) : TString("");
    tag = tag.Strip(TString::kBoth);
    if (tag.IsNull()) tag = "default";
    tag.ReplaceAll("/", "_");
    return tag;
  }

  bool UseSeparateChargeHistograms(const char* chargeMode)
  {
    TString mode = chargeMode ? TString(chargeMode) : TString("");
    mode = mode.Strip(TString::kBoth);
    mode.ToLower();

    if (mode.IsNull() || mode == "combined" || mode == "combine") return false;
    if (mode == "separate" || mode == "split" || mode == "individual") return true;

    Warning("UseSeparateChargeHistograms",
            "Unknown charge mode '%s', falling back to combined", mode.Data());
    return false;
  }

  void EnableDefaultHistogramErrors()
  {
    static bool enabled = false;
    if (enabled) return;

    TH1::SetDefaultSumw2(kTRUE);
    enabled = true;
  }

  // ---------- PDG-based classification ----------

  bool IsCharmMeson(int pdg)
  {
    pdg = std::abs(pdg);

    // Common open-charm mesons
    if (pdg == 411 || pdg == 421 || pdg == 431) return true; // D+, D0, Ds+

    // Generic safety net: 4xx includes excited D states; exclude charmonium (44x)
    if (pdg >= 400 && pdg < 500) {
      const int tens = (pdg / 10) % 10;
      if (tens != 4) return true; // exclude 44x (charmonium)
    }

    return false;
  }

  bool IsCharmBaryon(int pdg)
  {
    pdg = std::abs(pdg);

    // Explicit charm baryons
    if (pdg == 4122) return true; // Lambda_c^+
    if (pdg == 4112 || pdg == 4212 || pdg == 4222) return true; // Sigma_c
    if (pdg == 4132 || pdg == 4232) return true; // Xi_c
    if (pdg == 4332) return true; // Omega_c

    // Generic safety net: 4xxx
    if (pdg >= 4000 && pdg < 5000) return true;

    return false;
  }

  bool IsPion(int pdg)
  {
    const int apdg = std::abs(pdg);
    return (apdg == 211 || apdg == 111); // pi± and pi0
  }

  TH1D* CreateEventCountHist()
  {
    TH1D* h = new TH1D("fHistEventCount", "Event count;Counter;Events", 1, 0.5, 1.5);
    h->GetXaxis()->SetBinLabel(1, "events");
    return h;
  }

  void InitChargeSplitHistPair(TH2D*& particleHist,
                               TH2D*& barHist,
                               bool enable,
                               const char* baseName,
                               const char* particleLabel,
                               const char* barLabel,
                               int nPtBins,
                               double ptMin,
                               double ptMax,
                               int nMultBins,
                               double multMin,
                               double multMax)
  {
    particleHist = nullptr;
    barHist = nullptr;
    if (!enable) return;

    const TString particleName = TString::Format("%sParticle", baseName);
    const TString barName = TString::Format("%sBar", baseName);
    const TString particleTitle = TString::Format("%s: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                                  particleLabel);
    const TString barTitle = TString::Format("%s: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                             barLabel);

    particleHist = new TH2D(particleName.Data(), particleTitle.Data(),
                            nPtBins, ptMin, ptMax,
                            nMultBins, multMin, multMax);
    barHist = new TH2D(barName.Data(), barTitle.Data(),
                       nPtBins, ptMin, ptMax,
                       nMultBins, multMin, multMax);
  }

  void FillChargeSplitHists(TH2D* particleHist,
                            TH2D* barHist,
                            int pdg,
                            double pt,
                            int multiplicity)
  {
    if (pdg > 0) {
      if (particleHist) particleHist->Fill(pt, multiplicity);
    } else if (pdg < 0) {
      if (barHist) barHist->Fill(pt, multiplicity);
    }
  }

  // ---------- Histogram container ----------

  struct CCHistSet {
    TH1D* fHistEventCount;
    TH1D* fHistMultiplicity;
    TH2D* fHistPDGMult;

    TH2D* fHistPtCharmMesons;
    TH2D* fHistPtCharmBaryons;

    TH2D* fHistPtDplus;
    TH2D* fHistPtDplusParticle;
    TH2D* fHistPtDplusBar;
    TH2D* fHistPtDzero;
    TH2D* fHistPtDzeroParticle;
    TH2D* fHistPtDzeroBar;
    TH2D* fHistPtDsplus;
    TH2D* fHistPtDsplusParticle;
    TH2D* fHistPtDsplusBar;

    TH2D* fHistPtLambdacPlus;
    TH2D* fHistPtLambdacPlusParticle;
    TH2D* fHistPtLambdacPlusBar;
    TH2D* fHistPtSigmacPlusPlus;
    TH2D* fHistPtSigmacPlusPlusParticle;
    TH2D* fHistPtSigmacPlusPlusBar;
    TH2D* fHistPtSigmacPlus;
    TH2D* fHistPtSigmacPlusParticle;
    TH2D* fHistPtSigmacPlusBar;
    TH2D* fHistPtSigmacZero;
    TH2D* fHistPtSigmacZeroParticle;
    TH2D* fHistPtSigmacZeroBar;
    TH2D* fHistPtXicPlus;
    TH2D* fHistPtXicPlusParticle;
    TH2D* fHistPtXicPlusBar;
    TH2D* fHistPtXicZero;
    TH2D* fHistPtXicZeroParticle;
    TH2D* fHistPtXicZeroBar;
    TH2D* fHistPtOmegacZero;
    TH2D* fHistPtOmegacZeroParticle;
    TH2D* fHistPtOmegacZeroBar;

    // pions
    TH2D* fHistPtPionsCharged;
    TH2D* fHistPtPiPlus;
    TH2D* fHistPtPiMinus;
    TH2D* fHistPtPi0;
  };

  // ---------- Create one full histogram set ----------

  CCHistSet* CreateCCHistSet(bool writeSeparateChargeHists)
  {
    const int    nMultBins = 300;
    const double multMin   = 0.0;
    const double multMax   = 300.0;

    const int    nPtBins   = 100;
    const double ptMin     = 0.0;
    const double ptMax     = 120.0;

    CCHistSet* h = new CCHistSet;

    h->fHistEventCount = CreateEventCountHist();

    h->fHistMultiplicity = new TH1D(
      "fHistMultiplicity",
      "Multiplicity;N_{ch};Events",
      nMultBins, multMin, multMax
    );

    h->fHistPDGMult = new TH2D(
      "fHistPDGMult",
      "PDG code vs multiplicity;PDG code;Multiplicity",
      8000, -4000.0, 4000.0,
      nMultBins, multMin, multMax
    );

    h->fHistPtCharmMesons = new TH2D(
      "fHistPtCharmMesons",
      "Charm mesons: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtCharmBaryons = new TH2D(
      "fHistPtCharmBaryons",
      "Charm baryons: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    // Mesons
    h->fHistPtDplus = new TH2D(
      "fHistPtDplus",
      "D^{#pm} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );
    InitChargeSplitHistPair(h->fHistPtDplusParticle, h->fHistPtDplusBar,
                            writeSeparateChargeHists,
                            "fHistPtDplus", "D^{+}", "D^{-}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtDzero = new TH2D(
      "fHistPtDzero",
      "D^{0}/#bar{D}^{0} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );
    InitChargeSplitHistPair(h->fHistPtDzeroParticle, h->fHistPtDzeroBar,
                            writeSeparateChargeHists,
                            "fHistPtDzero", "D^{0}", "#bar{D}^{0}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtDsplus = new TH2D(
      "fHistPtDsplus",
      "D_{s}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );
    InitChargeSplitHistPair(h->fHistPtDsplusParticle, h->fHistPtDsplusBar,
                            writeSeparateChargeHists,
                            "fHistPtDsplus", "D_{s}^{+}", "D_{s}^{-}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    // Baryons
    h->fHistPtLambdacPlus = new TH2D(
      "fHistPtLambdacPlus",
      "#Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );
    InitChargeSplitHistPair(h->fHistPtLambdacPlusParticle, h->fHistPtLambdacPlusBar,
                            writeSeparateChargeHists,
                            "fHistPtLambdacPlus", "#Lambda_{c}^{+}", "#bar{#Lambda}_{c}^{-}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtSigmacPlusPlus = new TH2D(
      "fHistPtSigmacPlusPlus",
      "#Sigma_{c}^{++}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );
    InitChargeSplitHistPair(h->fHistPtSigmacPlusPlusParticle, h->fHistPtSigmacPlusPlusBar,
                            writeSeparateChargeHists,
                            "fHistPtSigmacPlusPlus", "#Sigma_{c}^{++}", "#bar{#Sigma}_{c}^{--}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtSigmacPlus = new TH2D(
      "fHistPtSigmacPlus",
      "#Sigma_{c}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );
    InitChargeSplitHistPair(h->fHistPtSigmacPlusParticle, h->fHistPtSigmacPlusBar,
                            writeSeparateChargeHists,
                            "fHistPtSigmacPlus", "#Sigma_{c}^{+}", "#bar{#Sigma}_{c}^{-}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtSigmacZero = new TH2D(
      "fHistPtSigmacZero",
      "#Sigma_{c}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );
    InitChargeSplitHistPair(h->fHistPtSigmacZeroParticle, h->fHistPtSigmacZeroBar,
                            writeSeparateChargeHists,
                            "fHistPtSigmacZero", "#Sigma_{c}^{0}", "#bar{#Sigma}_{c}^{0}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtXicPlus = new TH2D(
      "fHistPtXicPlus",
      "#Xi_{c}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );
    InitChargeSplitHistPair(h->fHistPtXicPlusParticle, h->fHistPtXicPlusBar,
                            writeSeparateChargeHists,
                            "fHistPtXicPlus", "#Xi_{c}^{+}", "#bar{#Xi}_{c}^{-}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtXicZero = new TH2D(
      "fHistPtXicZero",
      "#Xi_{c}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );
    InitChargeSplitHistPair(h->fHistPtXicZeroParticle, h->fHistPtXicZeroBar,
                            writeSeparateChargeHists,
                            "fHistPtXicZero", "#Xi_{c}^{0}", "#bar{#Xi}_{c}^{0}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtOmegacZero = new TH2D(
      "fHistPtOmegacZero",
      "#Omega_{c}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );
    InitChargeSplitHistPair(h->fHistPtOmegacZeroParticle, h->fHistPtOmegacZeroBar,
                            writeSeparateChargeHists,
                            "fHistPtOmegacZero", "#Omega_{c}^{0}", "#bar{#Omega}_{c}^{0}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    // Pions (consistent with bb script)
    h->fHistPtPionsCharged = new TH2D(
      "fHistPtPionsCharged",
      "#pi^{#pm}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtPiPlus = new TH2D(
      "fHistPtPiPlus",
      "#pi^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtPiMinus = new TH2D(
      "fHistPtPiMinus",
      "#pi^{-}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtPi0 = new TH2D(
      "fHistPtPi0",
      "#pi^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    return h;
  }

  // ---------- Write one histogram set to a ROOT file ----------

  void WriteCCHistSetToFile(CCHistSet* hset, const char* outputFile)
  {
    if (!hset || !outputFile) return;

    TFile* fout = TFile::Open(outputFile, "RECREATE");
    if (!fout || fout->IsZombie()) {
      Error("WriteCCHistSetToFile", "Cannot create output file %s", outputFile);
      if (fout) fout->Close();
      return;
    }

    hset->fHistEventCount->Write();
    hset->fHistMultiplicity->Write();
    hset->fHistPDGMult->Write();

    hset->fHistPtCharmMesons->Write();
    hset->fHistPtCharmBaryons->Write();

    hset->fHistPtDplus->Write();
    if (hset->fHistPtDplusParticle) hset->fHistPtDplusParticle->Write();
    if (hset->fHistPtDplusBar) hset->fHistPtDplusBar->Write();
    hset->fHistPtDzero->Write();
    if (hset->fHistPtDzeroParticle) hset->fHistPtDzeroParticle->Write();
    if (hset->fHistPtDzeroBar) hset->fHistPtDzeroBar->Write();
    hset->fHistPtDsplus->Write();
    if (hset->fHistPtDsplusParticle) hset->fHistPtDsplusParticle->Write();
    if (hset->fHistPtDsplusBar) hset->fHistPtDsplusBar->Write();

    hset->fHistPtLambdacPlus->Write();
    if (hset->fHistPtLambdacPlusParticle) hset->fHistPtLambdacPlusParticle->Write();
    if (hset->fHistPtLambdacPlusBar) hset->fHistPtLambdacPlusBar->Write();
    {
      TH2D* hLambdacAlias = dynamic_cast<TH2D*>(hset->fHistPtLambdacPlus->Clone("fHistPtLambdac"));
      if (hLambdacAlias) {
        hLambdacAlias->Write();
        delete hLambdacAlias;
      }
    }
    hset->fHistPtSigmacPlusPlus->Write();
    if (hset->fHistPtSigmacPlusPlusParticle) hset->fHistPtSigmacPlusPlusParticle->Write();
    if (hset->fHistPtSigmacPlusPlusBar) hset->fHistPtSigmacPlusPlusBar->Write();
    hset->fHistPtSigmacPlus->Write();
    if (hset->fHistPtSigmacPlusParticle) hset->fHistPtSigmacPlusParticle->Write();
    if (hset->fHistPtSigmacPlusBar) hset->fHistPtSigmacPlusBar->Write();
    hset->fHistPtSigmacZero->Write();
    if (hset->fHistPtSigmacZeroParticle) hset->fHistPtSigmacZeroParticle->Write();
    if (hset->fHistPtSigmacZeroBar) hset->fHistPtSigmacZeroBar->Write();
    hset->fHistPtXicPlus->Write();
    if (hset->fHistPtXicPlusParticle) hset->fHistPtXicPlusParticle->Write();
    if (hset->fHistPtXicPlusBar) hset->fHistPtXicPlusBar->Write();
    hset->fHistPtXicZero->Write();
    if (hset->fHistPtXicZeroParticle) hset->fHistPtXicZeroParticle->Write();
    if (hset->fHistPtXicZeroBar) hset->fHistPtXicZeroBar->Write();
    hset->fHistPtOmegacZero->Write();
    if (hset->fHistPtOmegacZeroParticle) hset->fHistPtOmegacZeroParticle->Write();
    if (hset->fHistPtOmegacZeroBar) hset->fHistPtOmegacZeroBar->Write();

    // pions
    hset->fHistPtPionsCharged->Write();
    hset->fHistPtPiPlus->Write();
    hset->fHistPtPiMinus->Write();
    hset->fHistPtPi0->Write();

    fout->Close();
  }

  // ---------- Fill all subsample histogram sets from one file ----------

  void FillFromFileCC(const char* filename,
                      std::vector<CCHistSet*>& hsets,
                      Long64_t& globalEventIndex,
                      Long64_t& globalPionCountInTree)
  {
    if (hsets.empty()) {
      Error("FillFromFileCC", "No histogram sets provided.");
      return;
    }

    TFile* fin = TFile::Open(filename, "READ");
    if (!fin || fin->IsZombie()) {
      Error("FillFromFileCC", "Cannot open input file %s", filename);
      if (fin) fin->Close();
      return;
    }

    TTree* tree = dynamic_cast<TTree*>(fin->Get("tree"));
    if (!tree) {
      Error("FillFromFileCC", "TTree 'tree' not found in %s", filename);
      fin->Close();
      return;
    }

    // Protect against missing branches (consistent with bb script)
    if (!tree->GetBranch("ID") || !tree->GetBranch("PT") || !tree->GetBranch("MULTIPLICITY")) {
      Error("FillFromFileCC", "Missing required branches in %s (need ID, PT, MULTIPLICITY)", filename);
      fin->Close();
      return;
    }

    std::vector<int>*    ID  = nullptr;
    std::vector<double>* PT  = nullptr;
    int MULTIPLICITY = 0;

    tree->SetBranchAddress("ID",           &ID);
    tree->SetBranchAddress("PT",           &PT);
    tree->SetBranchAddress("MULTIPLICITY", &MULTIPLICITY);

    const Long64_t nEntries = tree->GetEntries();
    const int nSub = static_cast<int>(hsets.size());

    for (Long64_t i = 0; i < nEntries; ++i, ++globalEventIndex) {
      tree->GetEntry(i);

      const int subIndex = static_cast<int>(globalEventIndex % nSub);
      CCHistSet* hset = hsets[subIndex];
      if (!hset) continue;

      hset->fHistEventCount->Fill(1.0);
      hset->fHistMultiplicity->Fill(MULTIPLICITY);

      if (!ID || !PT) continue;
      const std::size_t nParts = ID->size();
      if (PT->size() != nParts) continue;

      for (std::size_t j = 0; j < nParts; ++j) {
        const int    pdg  = ID->at(j);
        const int    apdg = std::abs(pdg);
        const double pt   = PT->at(j);

        hset->fHistPDGMult->Fill(pdg, MULTIPLICITY);

        // --------- pions ---------
        if (IsPion(pdg)) {
          ++globalPionCountInTree;

          if (apdg == 211) {
            hset->fHistPtPionsCharged->Fill(pt, MULTIPLICITY);
            if (pdg == 211)  hset->fHistPtPiPlus->Fill(pt, MULTIPLICITY);
            if (pdg == -211) hset->fHistPtPiMinus->Fill(pt, MULTIPLICITY);
          } else if (apdg == 111) {
            hset->fHistPtPi0->Fill(pt, MULTIPLICITY);
          }
        }

        // --------- charm global ---------
        if (IsCharmMeson(pdg)) {
          hset->fHistPtCharmMesons->Fill(pt, MULTIPLICITY);
        }
        if (IsCharmBaryon(pdg)) {
          hset->fHistPtCharmBaryons->Fill(pt, MULTIPLICITY);
        }

        // --------- species-resolved charm mesons ---------
        // Filled with abs(PDG), so the species histograms are charge-conjugate combined.
        if (apdg == 411) {          // D^{#pm}
          hset->fHistPtDplus->Fill(pt, MULTIPLICITY);
          FillChargeSplitHists(hset->fHistPtDplusParticle, hset->fHistPtDplusBar,
                               pdg, pt, MULTIPLICITY);
        } else if (apdg == 421) {   // D^{0}/#bar{D}^{0}
          hset->fHistPtDzero->Fill(pt, MULTIPLICITY);
          FillChargeSplitHists(hset->fHistPtDzeroParticle, hset->fHistPtDzeroBar,
                               pdg, pt, MULTIPLICITY);
        } else if (apdg == 431) {   // Ds+
          hset->fHistPtDsplus->Fill(pt, MULTIPLICITY);
          FillChargeSplitHists(hset->fHistPtDsplusParticle, hset->fHistPtDsplusBar,
                               pdg, pt, MULTIPLICITY);
        }

        // --------- species-resolved charm baryons ---------
        if (apdg == 4122) {         // #Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-}
          hset->fHistPtLambdacPlus->Fill(pt, MULTIPLICITY);
          FillChargeSplitHists(hset->fHistPtLambdacPlusParticle, hset->fHistPtLambdacPlusBar,
                               pdg, pt, MULTIPLICITY);
        } else if (apdg == 4222) {  // Sigma_c^{++}
          hset->fHistPtSigmacPlusPlus->Fill(pt, MULTIPLICITY);
          FillChargeSplitHists(hset->fHistPtSigmacPlusPlusParticle, hset->fHistPtSigmacPlusPlusBar,
                               pdg, pt, MULTIPLICITY);
        } else if (apdg == 4212) {  // Sigma_c^{+}
          hset->fHistPtSigmacPlus->Fill(pt, MULTIPLICITY);
          FillChargeSplitHists(hset->fHistPtSigmacPlusParticle, hset->fHistPtSigmacPlusBar,
                               pdg, pt, MULTIPLICITY);
        } else if (apdg == 4112) {  // Sigma_c^{0}
          hset->fHistPtSigmacZero->Fill(pt, MULTIPLICITY);
          FillChargeSplitHists(hset->fHistPtSigmacZeroParticle, hset->fHistPtSigmacZeroBar,
                               pdg, pt, MULTIPLICITY);
        } else if (apdg == 4232) {  // Xi_c^{+}
          hset->fHistPtXicPlus->Fill(pt, MULTIPLICITY);
          FillChargeSplitHists(hset->fHistPtXicPlusParticle, hset->fHistPtXicPlusBar,
                               pdg, pt, MULTIPLICITY);
        } else if (apdg == 4132) {  // Xi_c^{0}
          hset->fHistPtXicZero->Fill(pt, MULTIPLICITY);
          FillChargeSplitHists(hset->fHistPtXicZeroParticle, hset->fHistPtXicZeroBar,
                               pdg, pt, MULTIPLICITY);
        } else if (apdg == 4332) {  // Omega_c^{0}
          hset->fHistPtOmegacZero->Fill(pt, MULTIPLICITY);
          FillChargeSplitHists(hset->fHistPtOmegacZeroParticle, hset->fHistPtOmegacZeroBar,
                               pdg, pt, MULTIPLICITY);
        }
      }
    }

    fin->Close();
  }

  // ---------- Aggregate over directory into N subsamples ----------

  void AnalyzeCCbarMultiplicityPt_Multi(const char* inputDir,
                                        const char* outPrefix,
                                        int nSubSamples,
                                        bool writeSeparateChargeHists)
  {
    if (nSubSamples <= 0) {
      Error("AnalyzeCCbarMultiplicityPt_Multi",
            "nSubSamples must be > 0 (got %d)", nSubSamples);
      return;
    }

    std::cout << ">>> Analyzing directory: " << inputDir
              << "  ->  " << nSubSamples
              << " subsamples with prefix '" << outPrefix << "'"
              << std::endl;

    // 1) Create N histogram sets
    std::vector<CCHistSet*> hsets;
    hsets.reserve(nSubSamples);
    for (int i = 0; i < nSubSamples; ++i) {
      hsets.push_back(CreateCCHistSet(writeSeparateChargeHists));
    }

    // 2) List all ROOT files in inputDir
    TSystemDirectory dir("inputDir", inputDir);
    TList* fileList = dir.GetListOfFiles();
    if (!fileList) {
      Error("AnalyzeCCbarMultiplicityPt_Multi",
            "No file list for dir %s", inputDir);
      return;
    }

    fileList->Sort();

    int      nFiles = 0;
    Long64_t globalEventIndex = 0;
    Long64_t globalPionCountInTree = 0;

    TIter next(fileList);
    while (TSystemFile* f = (TSystemFile*)next()) {
      TString fname = f->GetName();
      if (f->IsDirectory()) continue;
      if (!fname.EndsWith(".root")) continue;

      TString fullPath = TString::Format("%s/%s", inputDir, fname.Data());
      std::cout << "  - Processing: " << fullPath << std::endl;

      FillFromFileCC(fullPath.Data(), hsets, globalEventIndex, globalPionCountInTree);
      ++nFiles;
    }

    if (nFiles == 0) {
      Error("AnalyzeCCbarMultiplicityPt_Multi",
            "No .root files found in directory %s", inputDir);
      return;
    }

    std::cout << ">>> Processed " << nFiles
              << " files from " << inputDir
              << " with total events = " << globalEventIndex
              << std::endl;

    // Pion protection / warning (consistent with bb script)
    if (globalPionCountInTree == 0) {
      std::cerr
        << "!!! WARNING: Found ZERO pions (pi± or pi0) in the input TTrees for directory: "
        << inputDir << "\n"
        << "    This usually means your PRODUCER did not store pions in the TTree branches ID/PT,\n"
        << "    even though PYTHIA normally generates plenty of pions.\n"
        << "    Action: modify ccbarcorrelations_status*.cpp to write pions (or charged primaries) into ID/PT.\n";
    } else {
      std::cout << ">>> Pion check: found " << globalPionCountInTree
                << " pion entries (pi±/pi0) in the input TTrees for " << inputDir << std::endl;
    }

    // 3) Write each subsample
    for (int i = 0; i < nSubSamples; ++i) {
      TString outName = TString::Format("%s%d.root", outPrefix, i);
      std::cout << ">>> Writing subsample " << i
                << " to " << outName << std::endl;
      WriteCCHistSetToFile(hsets[i], outName.Data());
    }

    std::cout << ">>> Done with directory: " << inputDir << std::endl;

    // Cleanup (nice-to-have, consistent with bb script)
    for (auto* hs : hsets) {
      if (!hs) continue;

      delete hs->fHistEventCount;
      delete hs->fHistMultiplicity;
      delete hs->fHistPDGMult;

      delete hs->fHistPtCharmMesons;
      delete hs->fHistPtCharmBaryons;

      delete hs->fHistPtDplus;
      delete hs->fHistPtDplusParticle;
      delete hs->fHistPtDplusBar;
      delete hs->fHistPtDzero;
      delete hs->fHistPtDzeroParticle;
      delete hs->fHistPtDzeroBar;
      delete hs->fHistPtDsplus;
      delete hs->fHistPtDsplusParticle;
      delete hs->fHistPtDsplusBar;

      delete hs->fHistPtLambdacPlus;
      delete hs->fHistPtLambdacPlusParticle;
      delete hs->fHistPtLambdacPlusBar;
      delete hs->fHistPtSigmacPlusPlus;
      delete hs->fHistPtSigmacPlusPlusParticle;
      delete hs->fHistPtSigmacPlusPlusBar;
      delete hs->fHistPtSigmacPlus;
      delete hs->fHistPtSigmacPlusParticle;
      delete hs->fHistPtSigmacPlusBar;
      delete hs->fHistPtSigmacZero;
      delete hs->fHistPtSigmacZeroParticle;
      delete hs->fHistPtSigmacZeroBar;
      delete hs->fHistPtXicPlus;
      delete hs->fHistPtXicPlusParticle;
      delete hs->fHistPtXicPlusBar;
      delete hs->fHistPtXicZero;
      delete hs->fHistPtXicZeroParticle;
      delete hs->fHistPtXicZeroBar;
      delete hs->fHistPtOmegacZero;
      delete hs->fHistPtOmegacZeroParticle;
      delete hs->fHistPtOmegacZeroBar;

      delete hs->fHistPtPionsCharged;
      delete hs->fHistPtPiPlus;
      delete hs->fHistPtPiMinus;
      delete hs->fHistPtPi0;

      delete hs;
    }
  }

} // end anonymous namespace

// ----------------------------------------------------------------------
// ROOT-friendly wrapper
// ----------------------------------------------------------------------
void cc_mult_pt_analysis_multi(int nSubSamples = 10,
                               const char* outputTag = "default",
                               const char* chargeMode = "combined")
{
  EnableDefaultHistogramErrors();

  // Create the dated output directory and both heavy-flavor subdirectories.
  TString base = GetBaseDir();
  TString tag = SanitizeOutputTag(outputTag);
  TString dateDir = base + "/AnalyzedData/" + tag;
  TString beautyDir = dateDir + "/Beauty";
  TString charmDir = dateDir + "/Charm";
  gSystem->mkdir(dateDir, true);
  gSystem->mkdir(beautyDir, true);
  gSystem->mkdir(charmDir, true);

  const bool writeSeparateChargeHists = UseSeparateChargeHistograms(chargeMode);
  std::cout << "Charm analysis charge mode: "
            << (writeSeparateChargeHists ? "separate" : "combined")
            << std::endl;

  // MONASH
  AnalyzeCCbarMultiplicityPt_Multi((base + "/RootFiles/ccbar/MONASH").Data(),
                                   (charmDir + "/ccbar_MONASH_sub").Data(),
                                   nSubSamples,
                                   writeSeparateChargeHists);

  // JUNCTIONS
  AnalyzeCCbarMultiplicityPt_Multi((base + "/RootFiles/ccbar/JUNCTIONS").Data(),
                                   (charmDir + "/ccbar_JUNCTIONS_sub").Data(),
                                   nSubSamples,
                                   writeSeparateChargeHists);
}
