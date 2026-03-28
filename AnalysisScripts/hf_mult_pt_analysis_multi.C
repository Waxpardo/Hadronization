//
// hf_mult_pt_analysis_multi.C
//
// Combined analysis for the unified heavy-flavour sample.
// Reads:
//   RootFiles/HF/MONASH/*.root
//   RootFiles/HF/JUNCTIONS/*.root
//
// and writes:
//   AnalyzedData/<tag>/Beauty/hf_MONASH_sub0.root, ...
//   AnalyzedData/<tag>/Beauty/hf_JUNCTIONS_sub0.root, ...
//   AnalyzedData/<tag>/Charm/hf_MONASH_sub0.root, ...
//   AnalyzedData/<tag>/Charm/hf_JUNCTIONS_sub0.root, ...
//
// Usage:
//   root -l -b -q 'AnalysisScripts/hf_mult_pt_analysis_multi.C+(10, "27-03-2026", "combined")'
//
// Notes:
// - Uses round-robin event assignment into N subsamples
// - Reads the unified TTree once and fills both Beauty and Charm outputs
// - Charge-conjugate mode:
//     * "combined" (default): current species histograms stay charge-conjugate combined
//     * "separate"          : the current combined histograms are still written, and
//                             extra particle-only / anti-particle histograms are added
//                             with the suffixes "Particle" and "Bar"
// - Default convention:
//     * Beauty takes HFCLASS == 5 or 45
//     * Charm  takes HFCLASS == 4 only
//   so Bc hadrons are counted with beauty only by default.
//

#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <cmath>

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

  // --------------------------------------------------
  // Base-path helpers
  // --------------------------------------------------

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

  // --------------------------------------------------
  // Classification helpers
  // --------------------------------------------------

  bool HasQuarkDigit(int particlepdg, int qdigit)
  {
    int pdg = std::abs(particlepdg);
    pdg /= 10; if (pdg % 10 == qdigit) return true;
    pdg /= 10; if (pdg % 10 == qdigit) return true;
    pdg /= 10; if (pdg % 10 == qdigit) return true;
    return false;
  }

  bool IsBeauty(int particlepdg) { return HasQuarkDigit(particlepdg, 5); }
  bool IsCharm (int particlepdg) { return HasQuarkDigit(particlepdg, 4); }
  bool IsBcHadron(int particlepdg) { return IsBeauty(particlepdg) && IsCharm(particlepdg); }

  bool IsPion(int particlepdg)
  {
    const int apdg = std::abs(particlepdg);
    return (apdg == 211 || apdg == 111);
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

  int HFClassFromPDG(int pdg)
  {
    if (IsBcHadron(pdg)) return 45;
    if (IsBeauty(pdg))   return 5;
    if (IsCharm(pdg))    return 4;
    if (IsPion(pdg))     return 0;
    return -1;
  }

  bool IsBeautyMeson(int pdg)
  {
    pdg = std::abs(pdg);

    if (pdg == 511 || pdg == 521 || pdg == 531 || pdg == 541) return true;

    if (pdg >= 500 && pdg < 600) {
      const int tens = (pdg / 10) % 10;
      if (tens != 5) return true; // exclude bottomonium 55x
    }

    return false;
  }

  bool IsBeautyBaryon(int pdg)
  {
    pdg = std::abs(pdg);

    if (pdg == 5122) return true;
    if (pdg == 5112 || pdg == 5212 || pdg == 5222) return true;
    if (pdg == 5132 || pdg == 5232) return true;
    if (pdg == 5332) return true;

    if (pdg >= 5000 && pdg < 6000) return true;

    return false;
  }

  bool IsCharmMeson(int pdg)
  {
    pdg = std::abs(pdg);

    if (pdg == 411 || pdg == 421 || pdg == 431) return true;

    if (pdg >= 400 && pdg < 500) {
      const int tens = (pdg / 10) % 10;
      if (tens != 4) return true; // exclude charmonium 44x
    }

    return false;
  }

  bool IsCharmBaryon(int pdg)
  {
    pdg = std::abs(pdg);

    if (pdg == 4122 || pdg == 4132 || pdg == 4232 || pdg == 4332) return true;

    if (pdg >= 4000 && pdg < 5000) return true;

    return false;
  }

  // --------------------------------------------------
  // Beauty histogram container
  // --------------------------------------------------

  struct BBHistSet {
    TH1D* fHistEventCount;
    TH1D* fHistMultiplicity;
    TH2D* fHistPDGMult;

    TH2D* fHistPtBeautyMesons;
    TH2D* fHistPtBeautyBaryons;

    TH2D* fHistPtBplus;
    TH2D* fHistPtBplusParticle;
    TH2D* fHistPtBplusBar;
    TH2D* fHistPtBzero;
    TH2D* fHistPtBzeroParticle;
    TH2D* fHistPtBzeroBar;
    TH2D* fHistPtBs0;
    TH2D* fHistPtBs0Particle;
    TH2D* fHistPtBs0Bar;
    TH2D* fHistPtBcplus;
    TH2D* fHistPtBcplusParticle;
    TH2D* fHistPtBcplusBar;

    TH2D* fHistPtLambdab;
    TH2D* fHistPtLambdabParticle;
    TH2D* fHistPtLambdabBar;
    TH2D* fHistPtSigmabPlus;
    TH2D* fHistPtSigmabPlusParticle;
    TH2D* fHistPtSigmabPlusBar;
    TH2D* fHistPtSigmabZero;
    TH2D* fHistPtSigmabZeroParticle;
    TH2D* fHistPtSigmabZeroBar;
    TH2D* fHistPtSigmabMinus;
    TH2D* fHistPtSigmabMinusParticle;
    TH2D* fHistPtSigmabMinusBar;
    TH2D* fHistPtXibZero;
    TH2D* fHistPtXibZeroParticle;
    TH2D* fHistPtXibZeroBar;
    TH2D* fHistPtXibMinus;
    TH2D* fHistPtXibMinusParticle;
    TH2D* fHistPtXibMinusBar;
    TH2D* fHistPtOmegabMinus;
    TH2D* fHistPtOmegabMinusParticle;
    TH2D* fHistPtOmegabMinusBar;

    TH2D* fHistPtPionsCharged;
    TH2D* fHistPtPiPlus;
    TH2D* fHistPtPiMinus;
    TH2D* fHistPtPi0;
  };

  BBHistSet* CreateBBHistSet(bool writeSeparateChargeHists)
  {
    const int    nMultBins = 300;
    const double multMin   = 0.0;
    const double multMax   = 300.0;

    const int    nPtBins   = 100;
    const double ptMin     = 0.0;
    const double ptMax     = 120.0;

    BBHistSet* h = new BBHistSet;

    h->fHistEventCount = CreateEventCountHist();

    h->fHistMultiplicity = new TH1D("fHistMultiplicity", "Multiplicity;N_{ch};Events",
                                    nMultBins, multMin, multMax);

    h->fHistPDGMult = new TH2D("fHistPDGMult", "PDG code vs multiplicity;PDG code;Multiplicity",
                               8000, -4000.0, 4000.0,
                               nMultBins, multMin, multMax);

    h->fHistPtBeautyMesons = new TH2D("fHistPtBeautyMesons",
                                      "Beauty mesons: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                      nPtBins, ptMin, ptMax,
                                      nMultBins, multMin, multMax);

    h->fHistPtBeautyBaryons = new TH2D("fHistPtBeautyBaryons",
                                       "Beauty baryons: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                       nPtBins, ptMin, ptMax,
                                       nMultBins, multMin, multMax);

    h->fHistPtBplus = new TH2D("fHistPtBplus",
                               "B^{#pm} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                               nPtBins, ptMin, ptMax,
                               nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtBplusParticle, h->fHistPtBplusBar,
                            writeSeparateChargeHists,
                            "fHistPtBplus", "B^{+}", "B^{-}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtBzero = new TH2D("fHistPtBzero",
                               "B^{0}/#bar{B}^{0} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                               nPtBins, ptMin, ptMax,
                               nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtBzeroParticle, h->fHistPtBzeroBar,
                            writeSeparateChargeHists,
                            "fHistPtBzero", "B^{0}", "#bar{B}^{0}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtBs0 = new TH2D("fHistPtBs0",
                             "B_{s}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                             nPtBins, ptMin, ptMax,
                             nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtBs0Particle, h->fHistPtBs0Bar,
                            writeSeparateChargeHists,
                            "fHistPtBs0", "B_{s}^{0}", "#bar{B}_{s}^{0}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtBcplus = new TH2D("fHistPtBcplus",
                                "B_{c}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                nPtBins, ptMin, ptMax,
                                nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtBcplusParticle, h->fHistPtBcplusBar,
                            writeSeparateChargeHists,
                            "fHistPtBcplus", "B_{c}^{+}", "B_{c}^{-}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtLambdab = new TH2D("fHistPtLambdab",
                                 "#Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                 nPtBins, ptMin, ptMax,
                                 nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtLambdabParticle, h->fHistPtLambdabBar,
                            writeSeparateChargeHists,
                            "fHistPtLambdab", "#Lambda_{b}^{0}", "#bar{#Lambda}_{b}^{0}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtSigmabPlus = new TH2D("fHistPtSigmabPlus",
                                    "#Sigma_{b}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                    nPtBins, ptMin, ptMax,
                                    nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtSigmabPlusParticle, h->fHistPtSigmabPlusBar,
                            writeSeparateChargeHists,
                            "fHistPtSigmabPlus", "#Sigma_{b}^{+}", "#bar{#Sigma}_{b}^{-}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtSigmabZero = new TH2D("fHistPtSigmabZero",
                                    "#Sigma_{b}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                    nPtBins, ptMin, ptMax,
                                    nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtSigmabZeroParticle, h->fHistPtSigmabZeroBar,
                            writeSeparateChargeHists,
                            "fHistPtSigmabZero", "#Sigma_{b}^{0}", "#bar{#Sigma}_{b}^{0}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtSigmabMinus = new TH2D("fHistPtSigmabMinus",
                                     "#Sigma_{b}^{-}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                     nPtBins, ptMin, ptMax,
                                     nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtSigmabMinusParticle, h->fHistPtSigmabMinusBar,
                            writeSeparateChargeHists,
                            "fHistPtSigmabMinus", "#Sigma_{b}^{-}", "#bar{#Sigma}_{b}^{+}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtXibZero = new TH2D("fHistPtXibZero",
                                 "#Xi_{b}^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                 nPtBins, ptMin, ptMax,
                                 nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtXibZeroParticle, h->fHistPtXibZeroBar,
                            writeSeparateChargeHists,
                            "fHistPtXibZero", "#Xi_{b}^{0}", "#bar{#Xi}_{b}^{0}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtXibMinus = new TH2D("fHistPtXibMinus",
                                  "#Xi_{b}^{-}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                  nPtBins, ptMin, ptMax,
                                  nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtXibMinusParticle, h->fHistPtXibMinusBar,
                            writeSeparateChargeHists,
                            "fHistPtXibMinus", "#Xi_{b}^{-}", "#bar{#Xi}_{b}^{+}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtOmegabMinus = new TH2D("fHistPtOmegabMinus",
                                     "#Omega_{b}^{-}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                     nPtBins, ptMin, ptMax,
                                     nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtOmegabMinusParticle, h->fHistPtOmegabMinusBar,
                            writeSeparateChargeHists,
                            "fHistPtOmegabMinus", "#Omega_{b}^{-}", "#bar{#Omega}_{b}^{+}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtPionsCharged = new TH2D("fHistPtPionsCharged",
                                      "#pi^{#pm}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                      nPtBins, ptMin, ptMax,
                                      nMultBins, multMin, multMax);

    h->fHistPtPiPlus = new TH2D("fHistPtPiPlus",
                                "#pi^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                nPtBins, ptMin, ptMax,
                                nMultBins, multMin, multMax);

    h->fHistPtPiMinus = new TH2D("fHistPtPiMinus",
                                 "#pi^{-}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                 nPtBins, ptMin, ptMax,
                                 nMultBins, multMin, multMax);

    h->fHistPtPi0 = new TH2D("fHistPtPi0",
                             "#pi^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                             nPtBins, ptMin, ptMax,
                             nMultBins, multMin, multMax);

    return h;
  }

  void WriteBBHistSetToFile(BBHistSet* hset, const char* outputFile)
  {
    if (!hset || !outputFile) return;

    TFile* fout = TFile::Open(outputFile, "RECREATE");
    if (!fout || fout->IsZombie()) {
      Error("WriteBBHistSetToFile", "Cannot create output file %s", outputFile);
      if (fout) fout->Close();
      return;
    }

    hset->fHistEventCount->Write();
    hset->fHistMultiplicity->Write();
    hset->fHistPDGMult->Write();

    hset->fHistPtBeautyMesons->Write();
    hset->fHistPtBeautyBaryons->Write();

    hset->fHistPtBplus->Write();
    if (hset->fHistPtBplusParticle) hset->fHistPtBplusParticle->Write();
    if (hset->fHistPtBplusBar) hset->fHistPtBplusBar->Write();
    hset->fHistPtBzero->Write();
    if (hset->fHistPtBzeroParticle) hset->fHistPtBzeroParticle->Write();
    if (hset->fHistPtBzeroBar) hset->fHistPtBzeroBar->Write();
    hset->fHistPtBs0->Write();
    if (hset->fHistPtBs0Particle) hset->fHistPtBs0Particle->Write();
    if (hset->fHistPtBs0Bar) hset->fHistPtBs0Bar->Write();
    hset->fHistPtBcplus->Write();
    if (hset->fHistPtBcplusParticle) hset->fHistPtBcplusParticle->Write();
    if (hset->fHistPtBcplusBar) hset->fHistPtBcplusBar->Write();

    hset->fHistPtLambdab->Write();
    if (hset->fHistPtLambdabParticle) hset->fHistPtLambdabParticle->Write();
    if (hset->fHistPtLambdabBar) hset->fHistPtLambdabBar->Write();
    hset->fHistPtSigmabPlus->Write();
    if (hset->fHistPtSigmabPlusParticle) hset->fHistPtSigmabPlusParticle->Write();
    if (hset->fHistPtSigmabPlusBar) hset->fHistPtSigmabPlusBar->Write();
    hset->fHistPtSigmabZero->Write();
    if (hset->fHistPtSigmabZeroParticle) hset->fHistPtSigmabZeroParticle->Write();
    if (hset->fHistPtSigmabZeroBar) hset->fHistPtSigmabZeroBar->Write();
    hset->fHistPtSigmabMinus->Write();
    if (hset->fHistPtSigmabMinusParticle) hset->fHistPtSigmabMinusParticle->Write();
    if (hset->fHistPtSigmabMinusBar) hset->fHistPtSigmabMinusBar->Write();
    hset->fHistPtXibZero->Write();
    if (hset->fHistPtXibZeroParticle) hset->fHistPtXibZeroParticle->Write();
    if (hset->fHistPtXibZeroBar) hset->fHistPtXibZeroBar->Write();
    hset->fHistPtXibMinus->Write();
    if (hset->fHistPtXibMinusParticle) hset->fHistPtXibMinusParticle->Write();
    if (hset->fHistPtXibMinusBar) hset->fHistPtXibMinusBar->Write();
    hset->fHistPtOmegabMinus->Write();
    if (hset->fHistPtOmegabMinusParticle) hset->fHistPtOmegabMinusParticle->Write();
    if (hset->fHistPtOmegabMinusBar) hset->fHistPtOmegabMinusBar->Write();

    hset->fHistPtPionsCharged->Write();
    hset->fHistPtPiPlus->Write();
    hset->fHistPtPiMinus->Write();
    hset->fHistPtPi0->Write();

    fout->Close();
  }

  // --------------------------------------------------
  // Charm histogram container
  // --------------------------------------------------

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
    TH2D* fHistPtLambdac;
    TH2D* fHistPtLambdacParticle;
    TH2D* fHistPtLambdacBar;

    TH2D* fHistPtPionsCharged;
    TH2D* fHistPtPiPlus;
    TH2D* fHistPtPiMinus;
    TH2D* fHistPtPi0;
  };

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

    h->fHistMultiplicity = new TH1D("fHistMultiplicity", "Multiplicity;N_{ch};Events",
                                    nMultBins, multMin, multMax);

    h->fHistPDGMult = new TH2D("fHistPDGMult", "PDG code vs multiplicity;PDG code;Multiplicity",
                               8000, -4000.0, 4000.0,
                               nMultBins, multMin, multMax);

    h->fHistPtCharmMesons = new TH2D("fHistPtCharmMesons",
                                     "Charm mesons: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                     nPtBins, ptMin, ptMax,
                                     nMultBins, multMin, multMax);

    h->fHistPtCharmBaryons = new TH2D("fHistPtCharmBaryons",
                                      "Charm baryons: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                      nPtBins, ptMin, ptMax,
                                      nMultBins, multMin, multMax);

    h->fHistPtDplus = new TH2D("fHistPtDplus",
                               "D^{#pm} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                               nPtBins, ptMin, ptMax,
                               nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtDplusParticle, h->fHistPtDplusBar,
                            writeSeparateChargeHists,
                            "fHistPtDplus", "D^{+}", "D^{-}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtDzero = new TH2D("fHistPtDzero",
                               "D^{0}/#bar{D}^{0} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                               nPtBins, ptMin, ptMax,
                               nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtDzeroParticle, h->fHistPtDzeroBar,
                            writeSeparateChargeHists,
                            "fHistPtDzero", "D^{0}", "#bar{D}^{0}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtDsplus = new TH2D("fHistPtDsplus",
                                "D_{s}^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                nPtBins, ptMin, ptMax,
                                nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtDsplusParticle, h->fHistPtDsplusBar,
                            writeSeparateChargeHists,
                            "fHistPtDsplus", "D_{s}^{+}", "D_{s}^{-}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtLambdac = new TH2D("fHistPtLambdac",
                                 "#Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-} (charge-conjugate combined): p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                 nPtBins, ptMin, ptMax,
                                 nMultBins, multMin, multMax);
    InitChargeSplitHistPair(h->fHistPtLambdacParticle, h->fHistPtLambdacBar,
                            writeSeparateChargeHists,
                            "fHistPtLambdac", "#Lambda_{c}^{+}", "#bar{#Lambda}_{c}^{-}",
                            nPtBins, ptMin, ptMax, nMultBins, multMin, multMax);

    h->fHistPtPionsCharged = new TH2D("fHistPtPionsCharged",
                                      "#pi^{#pm}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                      nPtBins, ptMin, ptMax,
                                      nMultBins, multMin, multMax);

    h->fHistPtPiPlus = new TH2D("fHistPtPiPlus",
                                "#pi^{+}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                nPtBins, ptMin, ptMax,
                                nMultBins, multMin, multMax);

    h->fHistPtPiMinus = new TH2D("fHistPtPiMinus",
                                 "#pi^{-}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                                 nPtBins, ptMin, ptMax,
                                 nMultBins, multMin, multMax);

    h->fHistPtPi0 = new TH2D("fHistPtPi0",
                             "#pi^{0}: p_{T} vs multiplicity;p_{T} (GeV/c);Multiplicity",
                             nPtBins, ptMin, ptMax,
                             nMultBins, multMin, multMax);

    return h;
  }

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
    hset->fHistPtLambdac->Write();
    if (hset->fHistPtLambdacParticle) hset->fHistPtLambdacParticle->Write();
    if (hset->fHistPtLambdacBar) hset->fHistPtLambdacBar->Write();
    {
      TH2D* hLambdacAlias = dynamic_cast<TH2D*>(hset->fHistPtLambdac->Clone("fHistPtLambdacPlus"));
      if (hLambdacAlias) {
        hLambdacAlias->Write();
        delete hLambdacAlias;
      }
    }

    hset->fHistPtPionsCharged->Write();
    hset->fHistPtPiPlus->Write();
    hset->fHistPtPiMinus->Write();
    hset->fHistPtPi0->Write();

    fout->Close();
  }

  // --------------------------------------------------
  // Cleanup helpers
  // --------------------------------------------------

  void DeleteBBHistSet(BBHistSet* hs)
  {
    if (!hs) return;
    delete hs->fHistEventCount;
    delete hs->fHistMultiplicity;
    delete hs->fHistPDGMult;
    delete hs->fHistPtBeautyMesons;
    delete hs->fHistPtBeautyBaryons;
    delete hs->fHistPtBplus;
    delete hs->fHistPtBplusParticle;
    delete hs->fHistPtBplusBar;
    delete hs->fHistPtBzero;
    delete hs->fHistPtBzeroParticle;
    delete hs->fHistPtBzeroBar;
    delete hs->fHistPtBs0;
    delete hs->fHistPtBs0Particle;
    delete hs->fHistPtBs0Bar;
    delete hs->fHistPtBcplus;
    delete hs->fHistPtBcplusParticle;
    delete hs->fHistPtBcplusBar;
    delete hs->fHistPtLambdab;
    delete hs->fHistPtLambdabParticle;
    delete hs->fHistPtLambdabBar;
    delete hs->fHistPtSigmabPlus;
    delete hs->fHistPtSigmabPlusParticle;
    delete hs->fHistPtSigmabPlusBar;
    delete hs->fHistPtSigmabZero;
    delete hs->fHistPtSigmabZeroParticle;
    delete hs->fHistPtSigmabZeroBar;
    delete hs->fHistPtSigmabMinus;
    delete hs->fHistPtSigmabMinusParticle;
    delete hs->fHistPtSigmabMinusBar;
    delete hs->fHistPtXibZero;
    delete hs->fHistPtXibZeroParticle;
    delete hs->fHistPtXibZeroBar;
    delete hs->fHistPtXibMinus;
    delete hs->fHistPtXibMinusParticle;
    delete hs->fHistPtXibMinusBar;
    delete hs->fHistPtOmegabMinus;
    delete hs->fHistPtOmegabMinusParticle;
    delete hs->fHistPtOmegabMinusBar;
    delete hs->fHistPtPionsCharged;
    delete hs->fHistPtPiPlus;
    delete hs->fHistPtPiMinus;
    delete hs->fHistPtPi0;
    delete hs;
  }

  void DeleteCCHistSet(CCHistSet* hs)
  {
    if (!hs) return;
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
    delete hs->fHistPtLambdac;
    delete hs->fHistPtLambdacParticle;
    delete hs->fHistPtLambdacBar;
    delete hs->fHistPtPionsCharged;
    delete hs->fHistPtPiPlus;
    delete hs->fHistPtPiMinus;
    delete hs->fHistPtPi0;
    delete hs;
  }

  // --------------------------------------------------
  // Core file reader: one pass fills both B and C
  // --------------------------------------------------

  void FillFromFileCombined(const char* filename,
                            std::vector<BBHistSet*>& beautySets,
                            std::vector<CCHistSet*>& charmSets,
                            Long64_t& globalEventIndex,
                            Long64_t& globalPionCountInTree)
  {
    if (beautySets.empty() || charmSets.empty()) {
      Error("FillFromFileCombined", "Empty histogram set collection.");
      return;
    }

    TFile* fin = TFile::Open(filename, "READ");
    if (!fin || fin->IsZombie()) {
      Error("FillFromFileCombined", "Cannot open input file %s", filename);
      if (fin) fin->Close();
      return;
    }

    TTree* tree = dynamic_cast<TTree*>(fin->Get("tree"));
    if (!tree) {
      Error("FillFromFileCombined", "TTree 'tree' not found in %s", filename);
      fin->Close();
      return;
    }

    std::vector<int>*    ID = nullptr;
    std::vector<int>*    HFCLASS = nullptr;
    std::vector<double>* PT = nullptr;
    int MULTIPLICITY = 0;

    if (!tree->GetBranch("ID") || !tree->GetBranch("PT") || !tree->GetBranch("MULTIPLICITY")) {
      Error("FillFromFileCombined", "Missing required branches in %s", filename);
      fin->Close();
      return;
    }

    tree->SetBranchAddress("ID", &ID);
    tree->SetBranchAddress("PT", &PT);
    tree->SetBranchAddress("MULTIPLICITY", &MULTIPLICITY);
    if (tree->GetBranch("HFCLASS")) tree->SetBranchAddress("HFCLASS", &HFCLASS);

    const Long64_t nEntries = tree->GetEntries();
    const int nSub = static_cast<int>(beautySets.size());

    for (Long64_t i = 0; i < nEntries; ++i, ++globalEventIndex) {
      tree->GetEntry(i);

      const int subIndex = static_cast<int>(globalEventIndex % nSub);
      BBHistSet* bset = beautySets[subIndex];
      CCHistSet* cset = charmSets[subIndex];
      if (!bset || !cset) continue;

      bset->fHistEventCount->Fill(1.0);
      cset->fHistEventCount->Fill(1.0);
      bset->fHistMultiplicity->Fill(MULTIPLICITY);
      cset->fHistMultiplicity->Fill(MULTIPLICITY);

      if (!ID || !PT) continue;
      const std::size_t nParts = ID->size();
      if (PT->size() != nParts) continue;
      if (HFCLASS && HFCLASS->size() != nParts) continue;

      for (std::size_t j = 0; j < nParts; ++j) {
        const int pdg   = ID->at(j);
        const int apdg  = std::abs(pdg);
        const double pt = PT->at(j);

        int hf = HFCLASS ? HFCLASS->at(j) : HFClassFromPDG(pdg);

        bset->fHistPDGMult->Fill(pdg, MULTIPLICITY);
        cset->fHistPDGMult->Fill(pdg, MULTIPLICITY);

        // Pions go to both outputs
        if (IsPion(pdg)) {
          ++globalPionCountInTree;

          if (apdg == 211) {
            bset->fHistPtPionsCharged->Fill(pt, MULTIPLICITY);
            cset->fHistPtPionsCharged->Fill(pt, MULTIPLICITY);

            if (pdg == 211) {
              bset->fHistPtPiPlus->Fill(pt, MULTIPLICITY);
              cset->fHistPtPiPlus->Fill(pt, MULTIPLICITY);
            }
            if (pdg == -211) {
              bset->fHistPtPiMinus->Fill(pt, MULTIPLICITY);
              cset->fHistPtPiMinus->Fill(pt, MULTIPLICITY);
            }
          } else if (apdg == 111) {
            bset->fHistPtPi0->Fill(pt, MULTIPLICITY);
            cset->fHistPtPi0->Fill(pt, MULTIPLICITY);
          }
        }

        // ---------------- Beauty ----------------
        const bool takeBeauty = (hf == 5 || hf == 45);

        if (takeBeauty) {
          if (IsBeautyMeson(pdg))  bset->fHistPtBeautyMesons->Fill(pt, MULTIPLICITY);
          if (IsBeautyBaryon(pdg)) bset->fHistPtBeautyBaryons->Fill(pt, MULTIPLICITY);

          // Species histograms are filled with abs(PDG), so they are charge-conjugate combined.
          if      (apdg == 521)  {
            bset->fHistPtBplus->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(bset->fHistPtBplusParticle, bset->fHistPtBplusBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 511)  {
            bset->fHistPtBzero->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(bset->fHistPtBzeroParticle, bset->fHistPtBzeroBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 531)  {
            bset->fHistPtBs0->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(bset->fHistPtBs0Particle, bset->fHistPtBs0Bar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 541)  {
            bset->fHistPtBcplus->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(bset->fHistPtBcplusParticle, bset->fHistPtBcplusBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 5122) {
            bset->fHistPtLambdab->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(bset->fHistPtLambdabParticle, bset->fHistPtLambdabBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 5222) {
            bset->fHistPtSigmabPlus->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(bset->fHistPtSigmabPlusParticle, bset->fHistPtSigmabPlusBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 5212) {
            bset->fHistPtSigmabZero->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(bset->fHistPtSigmabZeroParticle, bset->fHistPtSigmabZeroBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 5112) {
            bset->fHistPtSigmabMinus->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(bset->fHistPtSigmabMinusParticle, bset->fHistPtSigmabMinusBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 5232) {
            bset->fHistPtXibZero->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(bset->fHistPtXibZeroParticle, bset->fHistPtXibZeroBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 5132) {
            bset->fHistPtXibMinus->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(bset->fHistPtXibMinusParticle, bset->fHistPtXibMinusBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 5332) {
            bset->fHistPtOmegabMinus->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(bset->fHistPtOmegabMinusParticle, bset->fHistPtOmegabMinusBar,
                                 pdg, pt, MULTIPLICITY);
          }
        }

        // ---------------- Charm ----------------
        // Default: charm-only only. Excludes Bc (HFCLASS == 45).
        // If you want Bc counted in charm too, replace this line with:
        // const bool takeCharm = (hf == 4 || hf == 45);
        const bool takeCharm = (hf == 4);

        if (takeCharm) {
          if (IsCharmMeson(pdg))  cset->fHistPtCharmMesons->Fill(pt, MULTIPLICITY);
          if (IsCharmBaryon(pdg)) cset->fHistPtCharmBaryons->Fill(pt, MULTIPLICITY);

          if      (apdg == 411)  {
            cset->fHistPtDplus->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(cset->fHistPtDplusParticle, cset->fHistPtDplusBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 421)  {
            cset->fHistPtDzero->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(cset->fHistPtDzeroParticle, cset->fHistPtDzeroBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 431)  {
            cset->fHistPtDsplus->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(cset->fHistPtDsplusParticle, cset->fHistPtDsplusBar,
                                 pdg, pt, MULTIPLICITY);
          } else if (apdg == 4122) {
            cset->fHistPtLambdac->Fill(pt, MULTIPLICITY);
            FillChargeSplitHists(cset->fHistPtLambdacParticle, cset->fHistPtLambdacBar,
                                 pdg, pt, MULTIPLICITY);
          }
        }
      }
    }

    fin->Close();
  }

  // --------------------------------------------------
  // Analyze one tune directory
  // --------------------------------------------------

  void AnalyzeHFTuneMulti(const char* inputDir,
                          const char* beautyOutPrefix,
                          const char* charmOutPrefix,
                          int nSubSamples,
                          bool writeSeparateChargeHists)
  {
    if (nSubSamples <= 0) {
      Error("AnalyzeHFTuneMulti", "nSubSamples must be > 0");
      return;
    }

    std::cout << ">>> Analyzing directory: " << inputDir
              << " -> " << nSubSamples
              << " subsamples" << std::endl;

    std::vector<BBHistSet*> beautySets;
    std::vector<CCHistSet*> charmSets;
    beautySets.reserve(nSubSamples);
    charmSets.reserve(nSubSamples);

    for (int i = 0; i < nSubSamples; ++i) {
      beautySets.push_back(CreateBBHistSet(writeSeparateChargeHists));
      charmSets.push_back(CreateCCHistSet(writeSeparateChargeHists));
    }

    TSystemDirectory dir("inputDir", inputDir);
    TList* fileList = dir.GetListOfFiles();
    if (!fileList) {
      Error("AnalyzeHFTuneMulti", "No file list for dir %s", inputDir);
      for (auto* hs : beautySets) DeleteBBHistSet(hs);
      for (auto* hs : charmSets) DeleteCCHistSet(hs);
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

      FillFromFileCombined(fullPath.Data(),
                           beautySets,
                           charmSets,
                           globalEventIndex,
                           globalPionCountInTree);
      ++nFiles;
    }

    if (nFiles == 0) {
      Error("AnalyzeHFTuneMulti", "No .root files found in directory %s", inputDir);
      for (auto* hs : beautySets) DeleteBBHistSet(hs);
      for (auto* hs : charmSets) DeleteCCHistSet(hs);
      return;
    }

    std::cout << ">>> Processed " << nFiles
              << " files from " << inputDir
              << " with total events = " << globalEventIndex
              << std::endl;

    if (globalPionCountInTree == 0) {
      std::cerr << "!!! WARNING: zero pions found in the input TTrees for "
                << inputDir << std::endl;
    }

    for (int i = 0; i < nSubSamples; ++i) {
      TString beautyOut = TString::Format("%s%d.root", beautyOutPrefix, i);
      TString charmOut  = TString::Format("%s%d.root", charmOutPrefix, i);

      std::cout << ">>> Writing subsample " << i
                << "\n    Beauty -> " << beautyOut
                << "\n    Charm  -> " << charmOut
                << std::endl;

      WriteBBHistSetToFile(beautySets[i], beautyOut.Data());
      WriteCCHistSetToFile(charmSets[i], charmOut.Data());
    }

    for (auto* hs : beautySets) DeleteBBHistSet(hs);
    for (auto* hs : charmSets) DeleteCCHistSet(hs);
  }

} // end anonymous namespace

// --------------------------------------------------
// ROOT-friendly entry point
// --------------------------------------------------
void hf_mult_pt_analysis_multi(int nSubSamples = 10,
                               const char* outputTag = "default",
                               const char* chargeMode = "combined")
{
  EnableDefaultHistogramErrors();

  TString base = GetBaseDir();
  TString tag  = SanitizeOutputTag(outputTag);
  const bool writeSeparateChargeHists = UseSeparateChargeHistograms(chargeMode);

  std::cout << "Unified HF analysis charge mode: "
            << (writeSeparateChargeHists ? "separate" : "combined")
            << std::endl;

  TString dateDir   = base + "/AnalyzedData/" + tag;
  TString beautyDir = dateDir + "/Beauty";
  TString charmDir  = dateDir + "/Charm";

  gSystem->mkdir(dateDir, true);
  gSystem->mkdir(beautyDir, true);
  gSystem->mkdir(charmDir, true);

  AnalyzeHFTuneMulti((base + "/RootFiles/HF/MONASH").Data(),
                     (beautyDir + "/hf_MONASH_sub").Data(),
                     (charmDir  + "/hf_MONASH_sub").Data(),
                     nSubSamples,
                     writeSeparateChargeHists);

  AnalyzeHFTuneMulti((base + "/RootFiles/HF/JUNCTIONS").Data(),
                     (beautyDir + "/hf_JUNCTIONS_sub").Data(),
                     (charmDir  + "/hf_JUNCTIONS_sub").Data(),
                     nSubSamples,
                     writeSeparateChargeHists);
}
