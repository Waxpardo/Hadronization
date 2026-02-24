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
//     ccbar_MONASH_sub0.root ... sub(N-1).root
//     ccbar_JUNCTIONS_sub0.root ... sub(N-1).root
//
// Output histograms per subsample file:
//   TH1D fHistMultiplicity
//   TH2D fHistPDGMult
//   TH2D fHistPtCharmMesons
//   TH2D fHistPtCharmBaryons
//   TH2D fHistPtDplus, fHistPtDzero, fHistPtDsplus
//   TH2D fHistPtLambdacPlus, fHistPtSigmacPlusPlus, fHistPtSigmacPlus,
//        fHistPtSigmacZero, fHistPtXicPlus, fHistPtXicZero, fHistPtOmegacZero
//   TH2D fHistPtPionsCharged, fHistPtPiPlus, fHistPtPiMinus, fHistPtPi0
//
// Pion protection:
// - Counts pion entries found in the TTrees (pi±/pi0).
// - Prints WARNING if zero pions were stored (usually means producer didn't write them).
//
// Usage:
//   root -l -b -q 'AnalysisScripts/cc_mult_pt_analysis_multi.C+(10)'
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

  // ---------- Histogram container ----------

  struct CCHistSet {
    TH1D* fHistMultiplicity;
    TH2D* fHistPDGMult;

    TH2D* fHistPtCharmMesons;
    TH2D* fHistPtCharmBaryons;

    TH2D* fHistPtDplus;
    TH2D* fHistPtDzero;
    TH2D* fHistPtDsplus;

    TH2D* fHistPtLambdacPlus;
    TH2D* fHistPtSigmacPlusPlus;
    TH2D* fHistPtSigmacPlus;
    TH2D* fHistPtSigmacZero;
    TH2D* fHistPtXicPlus;
    TH2D* fHistPtXicZero;
    TH2D* fHistPtOmegacZero;

    // pions
    TH2D* fHistPtPionsCharged;
    TH2D* fHistPtPiPlus;
    TH2D* fHistPtPiMinus;
    TH2D* fHistPtPi0;
  };

  // ---------- Create one full histogram set ----------

  CCHistSet* CreateCCHistSet()
  {
    const int    nMultBins = 300;
    const double multMin   = 0.0;
    const double multMax   = 300.0;

    const int    nPtBins   = 100;
    const double ptMin     = 0.0;
    const double ptMax     = 120.0;

    CCHistSet* h = new CCHistSet;

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
      "D^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtDzero = new TH2D(
      "fHistPtDzero",
      "D^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtDsplus = new TH2D(
      "fHistPtDsplus",
      "D_{s}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    // Baryons
    h->fHistPtLambdacPlus = new TH2D(
      "fHistPtLambdacPlus",
      "#Lambda_{c}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtSigmacPlusPlus = new TH2D(
      "fHistPtSigmacPlusPlus",
      "#Sigma_{c}^{++}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtSigmacPlus = new TH2D(
      "fHistPtSigmacPlus",
      "#Sigma_{c}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtSigmacZero = new TH2D(
      "fHistPtSigmacZero",
      "#Sigma_{c}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtXicPlus = new TH2D(
      "fHistPtXicPlus",
      "#Xi_{c}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtXicZero = new TH2D(
      "fHistPtXicZero",
      "#Xi_{c}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtOmegacZero = new TH2D(
      "fHistPtOmegacZero",
      "#Omega_{c}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

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

    hset->fHistMultiplicity->Write();
    hset->fHistPDGMult->Write();

    hset->fHistPtCharmMesons->Write();
    hset->fHistPtCharmBaryons->Write();

    hset->fHistPtDplus->Write();
    hset->fHistPtDzero->Write();
    hset->fHistPtDsplus->Write();

    hset->fHistPtLambdacPlus->Write();
    hset->fHistPtSigmacPlusPlus->Write();
    hset->fHistPtSigmacPlus->Write();
    hset->fHistPtSigmacZero->Write();
    hset->fHistPtXicPlus->Write();
    hset->fHistPtXicZero->Write();
    hset->fHistPtOmegacZero->Write();

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
        if (apdg == 411) {          // D+
          hset->fHistPtDplus->Fill(pt, MULTIPLICITY);
        } else if (apdg == 421) {   // D0
          hset->fHistPtDzero->Fill(pt, MULTIPLICITY);
        } else if (apdg == 431) {   // Ds+
          hset->fHistPtDsplus->Fill(pt, MULTIPLICITY);
        }

        // --------- species-resolved charm baryons ---------
        if (apdg == 4122) {         // Lambda_c^+
          hset->fHistPtLambdacPlus->Fill(pt, MULTIPLICITY);
        } else if (apdg == 4222) {  // Sigma_c^{++}
          hset->fHistPtSigmacPlusPlus->Fill(pt, MULTIPLICITY);
        } else if (apdg == 4212) {  // Sigma_c^{+}
          hset->fHistPtSigmacPlus->Fill(pt, MULTIPLICITY);
        } else if (apdg == 4112) {  // Sigma_c^{0}
          hset->fHistPtSigmacZero->Fill(pt, MULTIPLICITY);
        } else if (apdg == 4232) {  // Xi_c^{+}
          hset->fHistPtXicPlus->Fill(pt, MULTIPLICITY);
        } else if (apdg == 4132) {  // Xi_c^{0}
          hset->fHistPtXicZero->Fill(pt, MULTIPLICITY);
        } else if (apdg == 4332) {  // Omega_c^{0}
          hset->fHistPtOmegacZero->Fill(pt, MULTIPLICITY);
        }
      }
    }

    fin->Close();
  }

  // ---------- Aggregate over directory into N subsamples ----------

  void AnalyzeCCbarMultiplicityPt_Multi(const char* inputDir,
                                        const char* outPrefix,
                                        int nSubSamples)
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
      hsets.push_back(CreateCCHistSet());
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

      delete hs->fHistMultiplicity;
      delete hs->fHistPDGMult;

      delete hs->fHistPtCharmMesons;
      delete hs->fHistPtCharmBaryons;

      delete hs->fHistPtDplus;
      delete hs->fHistPtDzero;
      delete hs->fHistPtDsplus;

      delete hs->fHistPtLambdacPlus;
      delete hs->fHistPtSigmacPlusPlus;
      delete hs->fHistPtSigmacPlus;
      delete hs->fHistPtSigmacZero;
      delete hs->fHistPtXicPlus;
      delete hs->fHistPtXicZero;
      delete hs->fHistPtOmegacZero;

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
void cc_mult_pt_analysis_multi(int nSubSamples = 10)
{
  // Ensure output directory exists
  TString base = GetBaseDir();
  TString outDir = base + "/AnalysisScripts/AnalyzedData";
  gSystem->mkdir(outDir, true);

  // MONASH
  AnalyzeCCbarMultiplicityPt_Multi((base + "/RootFiles/ccbar/MONASH").Data(),
                                   (outDir + "/ccbar_MONASH_sub").Data(),
                                   nSubSamples);

  // JUNCTIONS
  AnalyzeCCbarMultiplicityPt_Multi((base + "/RootFiles/ccbar/JUNCTIONS").Data(),
                                   (outDir + "/ccbar_JUNCTIONS_sub").Data(),
                                   nSubSamples);
}
