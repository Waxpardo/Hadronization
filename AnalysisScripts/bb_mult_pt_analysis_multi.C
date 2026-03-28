// bb_mult_pt_analysis_multi.C
//
// Build the same beauty-hadron multiplicity/pT histograms as
// AnalyzeBBbarMultiplicityPt, but aggregating over MANY jobs and
// splitting the total statistics into N subsamples with (almost)
// equal number of events using round-robin event assignment.
//
// Usage (from Hadronization base):
//   root -l -b -q 'AnalysisScripts/bb_mult_pt_analysis_multi.C+(10, "12-01-2026")'
//
// This will:
//   - For MONASH   : read RootFiles/bbbar/MONASH/*.root
//                    write AnalyzedData/<tag>/Beauty/bbbar_MONASH_sub0.root, ..., sub(N-1).root
//   - For JUNCTIONS: read RootFiles/bbbar/JUNCTIONS/*.root
//                    write AnalyzedData/<tag>/Beauty/bbbar_JUNCTIONS_sub0.root, ..., sub(N-1).root
//
// Input files (each):
//   TTree "tree" with branches:
//     vector<int>    ID
//     vector<double> PT
//     int            MULTIPLICITY
//
// Output files (per tune, per subsample) contain:
//   TH1D fHistMultiplicity
//   TH2D fHistPDGMult
//   TH2D fHistPtBeautyMesons
//   TH2D fHistPtBeautyBaryons
//   TH2D fHistPtBplus, fHistPtBzero, fHistPtBs0, fHistPtBcplus
//   TH2D fHistPtLambdab, fHistPtSigmabPlus, fHistPtSigmabZero, fHistPtSigmabMinus
//   TH2D fHistPtXibZero, fHistPtXibMinus, fHistPtOmegabMinus
//
// Each subsample ROOT file has the SAME histogram names; they live in
// different files, so there are no name clashes.
//
// Species-resolved histograms are filled using abs(PDG), so these histograms
// are charge-conjugate combined. For example:
//   fHistPtBplus   -> B^{#pm}
//   fHistPtBzero   -> B^{0}/#bar{B}^{0}
//   fHistPtLambdab -> #Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0}
//
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

  // ---------- PDG-based classification ----------

  bool IsBeautyMeson(int pdg)
  {
    pdg = std::abs(pdg);

    // Common open-beauty mesons:
    if (pdg == 511 || pdg == 521 || pdg == 531 || pdg == 541) return true;

    // Generic safety net: 5xx (includes excited open-B), exclude bottomonium (55x)
    if (pdg >= 500 && pdg < 600) {
      const int tens = (pdg / 10) % 10;
      if (tens != 5) return true; // exclude 55x (bottomonium)
    }

    return false;
  }

  bool IsBeautyBaryon(int pdg)
  {
    pdg = std::abs(pdg);

    // Some explicit beauty baryons:
    if (pdg == 5122) return true; // Lambda_b^0

    if (pdg == 5112 || pdg == 5212 || pdg == 5222) return true; // Sigma_b

    if (pdg == 5132 || pdg == 5232) return true; // Xi_b

    if (pdg == 5332) return true; // Omega_b

    // Generic safety net: 5xxx
    if (pdg >= 5000 && pdg < 6000) return true;

    return false;
  }

  bool IsPion(int pdg)
  {
    const int apdg = std::abs(pdg);
    return (apdg == 211 || apdg == 111); // pi+/- and pi0
  }

  // ---------- Histogram container ----------

  struct BBHistSet {
    // event-level
    TH1D* fHistMultiplicity;

    // debugging / QA
    TH2D* fHistPDGMult;

    // beauty global
    TH2D* fHistPtBeautyMesons;
    TH2D* fHistPtBeautyBaryons;

    // beauty species
    TH2D* fHistPtBplus;
    TH2D* fHistPtBzero;
    TH2D* fHistPtBs0;
    TH2D* fHistPtBcplus;

    TH2D* fHistPtLambdab;
    TH2D* fHistPtSigmabPlus;
    TH2D* fHistPtSigmabZero;
    TH2D* fHistPtSigmabMinus;
    TH2D* fHistPtXibZero;
    TH2D* fHistPtXibMinus;
    TH2D* fHistPtOmegabMinus;

    // pions
    TH2D* fHistPtPionsCharged; // pi+ and pi-
    TH2D* fHistPtPiPlus;
    TH2D* fHistPtPiMinus;
    TH2D* fHistPtPi0;
  };

  // ---------- Create one full histogram set ----------

  BBHistSet* CreateBBHistSet()
  {
    const int    nMultBins = 300;
    const double multMin   = 0.0;
    const double multMax   = 300.0;

    const int    nPtBins   = 100;
    const double ptMin     = 0.0;
    const double ptMax     = 120.0;

    BBHistSet* h = new BBHistSet;

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

    h->fHistPtBeautyMesons = new TH2D(
      "fHistPtBeautyMesons",
      "Beauty mesons: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtBeautyBaryons = new TH2D(
      "fHistPtBeautyBaryons",
      "Beauty baryons: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    // beauty mesons
    h->fHistPtBplus = new TH2D(
      "fHistPtBplus",
      "B^{#pm} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtBzero = new TH2D(
      "fHistPtBzero",
      "B^{0}/#bar{B}^{0} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtBs0 = new TH2D(
      "fHistPtBs0",
      "B_{s}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtBcplus = new TH2D(
      "fHistPtBcplus",
      "B_{c}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    // beauty baryons
    h->fHistPtLambdab = new TH2D(
      "fHistPtLambdab",
      "#Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtSigmabPlus = new TH2D(
      "fHistPtSigmabPlus",
      "#Sigma_{b}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtSigmabZero = new TH2D(
      "fHistPtSigmabZero",
      "#Sigma_{b}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtSigmabMinus = new TH2D(
      "fHistPtSigmabMinus",
      "#Sigma_{b}^{-}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtXibZero = new TH2D(
      "fHistPtXibZero",
      "#Xi_{b}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtXibMinus = new TH2D(
      "fHistPtXibMinus",
      "#Xi_{b}^{-}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    h->fHistPtOmegabMinus = new TH2D(
      "fHistPtOmegabMinus",
      "#Omega_{b}^{-}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
      nPtBins, ptMin, ptMax,
      nMultBins, multMin, multMax
    );

    // pions
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

  void WriteBBHistSetToFile(BBHistSet* hset, const char* outputFile)
  {
    if (!hset || !outputFile) return;

    TFile* fout = TFile::Open(outputFile, "RECREATE");
    if (!fout || fout->IsZombie()) {
      Error("WriteBBHistSetToFile", "Cannot create output file %s", outputFile);
      if (fout) fout->Close();
      return;
    }

    hset->fHistMultiplicity->Write();
    hset->fHistPDGMult->Write();

    hset->fHistPtBeautyMesons->Write();
    hset->fHistPtBeautyBaryons->Write();

    hset->fHistPtBplus->Write();
    hset->fHistPtBzero->Write();
    hset->fHistPtBs0->Write();
    hset->fHistPtBcplus->Write();

    hset->fHistPtLambdab->Write();
    hset->fHistPtSigmabPlus->Write();
    hset->fHistPtSigmabZero->Write();
    hset->fHistPtSigmabMinus->Write();
    hset->fHistPtXibZero->Write();
    hset->fHistPtXibMinus->Write();
    hset->fHistPtOmegabMinus->Write();

    // pions
    hset->fHistPtPionsCharged->Write();
    hset->fHistPtPiPlus->Write();
    hset->fHistPtPiMinus->Write();
    hset->fHistPtPi0->Write();

    fout->Close();
  }

  // ---------- Fill all subsample histogram sets from one file ----------

  void FillFromFile(const char* filename,
                    std::vector<BBHistSet*>& hsets,
                    Long64_t& globalEventIndex,
                    Long64_t& globalPionCountInTree)
  {
    if (hsets.empty()) {
      Error("FillFromFile", "No histogram sets provided.");
      return;
    }

    TFile* fin = TFile::Open(filename, "READ");
    if (!fin || fin->IsZombie()) {
      Error("FillFromFile", "Cannot open input file %s", filename);
      if (fin) fin->Close();
      return;
    }

    TTree* tree = dynamic_cast<TTree*>(fin->Get("tree"));
    if (!tree) {
      Error("FillFromFile", "TTree 'tree' not found in %s", filename);
      fin->Close();
      return;
    }

    std::vector<int>*    ID  = nullptr;
    std::vector<double>* PT  = nullptr;
    int MULTIPLICITY = 0;

    // Protect against missing branches
    if (!tree->GetBranch("ID") || !tree->GetBranch("PT") || !tree->GetBranch("MULTIPLICITY")) {
      Error("FillFromFile", "Missing required branches in %s (need ID, PT, MULTIPLICITY)", filename);
      fin->Close();
      return;
    }

    tree->SetBranchAddress("ID",           &ID);
    tree->SetBranchAddress("PT",           &PT);
    tree->SetBranchAddress("MULTIPLICITY", &MULTIPLICITY);

    const Long64_t nEntries = tree->GetEntries();
    const int nSub = static_cast<int>(hsets.size());

    for (Long64_t i = 0; i < nEntries; ++i, ++globalEventIndex) {
      tree->GetEntry(i);

      int subIndex = static_cast<int>(globalEventIndex % nSub);
      BBHistSet* hset = hsets[subIndex];
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

        // --------- beauty global ---------
        if (IsBeautyMeson(pdg)) {
          hset->fHistPtBeautyMesons->Fill(pt, MULTIPLICITY);
        }
        if (IsBeautyBaryon(pdg)) {
          hset->fHistPtBeautyBaryons->Fill(pt, MULTIPLICITY);
        }

        // --------- species-resolved beauty mesons ---------
        // Filled with abs(PDG), so the species histograms are charge-conjugate combined.
        if (apdg == 521) {           // B^{#pm}
          hset->fHistPtBplus->Fill(pt, MULTIPLICITY);
        } else if (apdg == 511) {    // B^{0}/#bar{B}^{0}
          hset->fHistPtBzero->Fill(pt, MULTIPLICITY);
        } else if (apdg == 531) {    // Bs0
          hset->fHistPtBs0->Fill(pt, MULTIPLICITY);
        } else if (apdg == 541) {    // Bc+
          hset->fHistPtBcplus->Fill(pt, MULTIPLICITY);
        }

        // --------- species-resolved beauty baryons ---------
        if (apdg == 5122) {          // #Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0}
          hset->fHistPtLambdab->Fill(pt, MULTIPLICITY);
        } else if (apdg == 5222) {   // Sigma_b^+
          hset->fHistPtSigmabPlus->Fill(pt, MULTIPLICITY);
        } else if (apdg == 5212) {   // Sigma_b^0
          hset->fHistPtSigmabZero->Fill(pt, MULTIPLICITY);
        } else if (apdg == 5112) {   // Sigma_b^-
          hset->fHistPtSigmabMinus->Fill(pt, MULTIPLICITY);
        } else if (apdg == 5232) {   // Xi_b^0
          hset->fHistPtXibZero->Fill(pt, MULTIPLICITY);
        } else if (apdg == 5132) {   // Xi_b^-
          hset->fHistPtXibMinus->Fill(pt, MULTIPLICITY);
        } else if (apdg == 5332) {   // Omega_b^-
          hset->fHistPtOmegabMinus->Fill(pt, MULTIPLICITY);
        }
      }
    }

    fin->Close();
  }

  // ---------- Aggregate over directory into N subsamples ----------

  void AnalyzeBBbarMultiplicityPt_Multi(const char* inputDir,
                                        const char* outPrefix,
                                        int nSubSamples)
  {
    if (nSubSamples <= 0) {
      Error("AnalyzeBBbarMultiplicityPt_Multi",
            "nSubSamples must be > 0 (got %d)", nSubSamples);
      return;
    }

    std::cout << ">>> Analyzing directory: " << inputDir
              << "  ->  " << nSubSamples
              << " subsamples with prefix '" << outPrefix << "'"
              << std::endl;

    // 1) Create N histogram sets (one per subsample)
    std::vector<BBHistSet*> hsets;
    hsets.reserve(nSubSamples);
    for (int i = 0; i < nSubSamples; ++i) {
      hsets.push_back(CreateBBHistSet());
    }

    // 2) List all ROOT files in inputDir
    TSystemDirectory dir("inputDir", inputDir);
    TList* fileList = dir.GetListOfFiles();
    if (!fileList) {
      Error("AnalyzeBBbarMultiplicityPt_Multi",
            "No file list for dir %s", inputDir);
      return;
    }

    fileList->Sort();  // deterministic order

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

      FillFromFile(fullPath.Data(), hsets, globalEventIndex, globalPionCountInTree);
      ++nFiles;
    }

    if (nFiles == 0) {
      Error("AnalyzeBBbarMultiplicityPt_Multi",
            "No .root files found in directory %s", inputDir);
      return;
    }

    std::cout << ">>> Processed " << nFiles
              << " files from " << inputDir
              << " with total events = " << globalEventIndex
              << std::endl;

    // 2b) Protection / warning about pions
    if (globalPionCountInTree == 0) {
      std::cerr
        << "!!! WARNING: Found ZERO pions (pi± or pi0) in the input TTrees for directory: "
        << inputDir << "\n"
        << "    This usually means your PRODUCER did not store pions in the TTree branches ID/PT,\n"
        << "    even though PYTHIA normally generates plenty of pions.\n"
        << "    Action: modify bbbarcorrelations_status.cpp to write pions (or charged primaries) into ID/PT.\n";
    } else {
      std::cout << ">>> Pion check: found " << globalPionCountInTree
                << " pion entries (pi±/pi0) in the input TTrees for " << inputDir << std::endl;
    }

    // 3) Write each subsample to its own ROOT file
    for (int i = 0; i < nSubSamples; ++i) {
      TString outName = TString::Format("%s%d.root", outPrefix, i);
      std::cout << ">>> Writing subsample " << i
                << " to " << outName << std::endl;
      WriteBBHistSetToFile(hsets[i], outName.Data());
    }

    std::cout << ">>> Done with directory: " << inputDir << std::endl;

    // Cleanup (nice-to-have in long ROOT sessions)
    for (auto* hs : hsets) {
      if (!hs) continue;
      delete hs->fHistMultiplicity;
      delete hs->fHistPDGMult;

      delete hs->fHistPtBeautyMesons;
      delete hs->fHistPtBeautyBaryons;

      delete hs->fHistPtBplus;
      delete hs->fHistPtBzero;
      delete hs->fHistPtBs0;
      delete hs->fHistPtBcplus;

      delete hs->fHistPtLambdab;
      delete hs->fHistPtSigmabPlus;
      delete hs->fHistPtSigmabZero;
      delete hs->fHistPtSigmabMinus;
      delete hs->fHistPtXibZero;
      delete hs->fHistPtXibMinus;
      delete hs->fHistPtOmegabMinus;

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
void bb_mult_pt_analysis_multi(int nSubSamples = 10, const char* outputTag = "default")
{
  // Create the dated output directory and both heavy-flavor subdirectories.
  TString base = GetBaseDir();
  TString tag = SanitizeOutputTag(outputTag);
  TString dateDir = base + "/AnalyzedData/" + tag;
  TString beautyDir = dateDir + "/Beauty";
  TString charmDir = dateDir + "/Charm";
  gSystem->mkdir(dateDir, true);
  gSystem->mkdir(beautyDir, true);
  gSystem->mkdir(charmDir, true);

  // MONASH
  AnalyzeBBbarMultiplicityPt_Multi((base + "/RootFiles/bbbar/MONASH").Data(),
                                   (beautyDir + "/bbbar_MONASH_sub").Data(),
                                   nSubSamples);

  // JUNCTIONS
  AnalyzeBBbarMultiplicityPt_Multi((base + "/RootFiles/bbbar/JUNCTIONS").Data(),
                                   (beautyDir + "/bbbar_JUNCTIONS_sub").Data(),
                                   nSubSamples);
}
