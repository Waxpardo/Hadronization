// ---------------------------------------------------------------------------
// Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C
//
// Makes ratios vs multiplicity percentile bins using subsample ROOT files:
//
//   (1) (#Lambda_c + #bar{#Lambda}_c) / D^{#pm}   vs mult percentile
//   (2) (#Lambda_b + #bar{#Lambda}_b) / B^{#pm}   vs mult percentile
//
// For each tune, ratio points are computed per subsample as:
//   r = (Integral over pT of TH2 in mult-range for Lambda) / same for D (or B)
// Then combined across subsamples: mean ± SEM.
//
// Usage:
//   .L Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C
//   runHFRatios("12-01-2026");
//   runHFRatios();   // if no date is given, use the latest folder in AnalyzedData
//
// ---------------------------------------------------------------------------

#include <vector>
#include <string>
#include <cmath>
#include <utility>
#include <algorithm>
#include <iostream>

#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TH1D.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TStyle.h"
#include "TString.h"
#include "TGraphErrors.h"
#include "TAxis.h"
#include "TROOT.h"

#include "PlottingPathUtils.h"

namespace {

struct PlotPathBootstrap {
  PlotPathBootstrap() { PlotPathUtils::RegisterMacroPath(__FILE__); }
} gPlotPathBootstrap;

void SetStyle() {
  gStyle->SetOptStat(0);
  gStyle->SetPadBottomMargin(0.14);
  gStyle->SetPadLeftMargin(0.12);
  gStyle->SetPadRightMargin(0.05);
  gStyle->SetTitleSize(0.055,"XY");
  gStyle->SetLabelSize(0.045,"XY");
  gStyle->SetLegendBorderSize(0);
}

template<class T>
T* GetObj(TFile* f, const char* name) {
  return f ? dynamic_cast<T*>(f->Get(name)) : nullptr;
}

TH2* CloneTH2(TH2* h, const char* cloneName)
{
  if (!h) return nullptr;
  TH2* clone = dynamic_cast<TH2*>(h->Clone(cloneName));
  if (clone) clone->SetDirectory(nullptr);
  return clone;
}

TH2* GetChargeCombinedHist(TFile* f,
                           const std::vector<TString>& combinedNames,
                           const std::vector<TString>& splitBases,
                           const char* cloneName)
{
  if (!f) return nullptr;

  for (const TString& name : combinedNames) {
    if (TH2* h = GetObj<TH2>(f, name.Data())) return CloneTH2(h, cloneName);
  }

  for (const TString& base : splitBases) {
    TH2* hParticle = GetObj<TH2>(f, Form("%sParticle", base.Data()));
    TH2* hBar = GetObj<TH2>(f, Form("%sBar", base.Data()));
    if (!hParticle || !hBar) continue;

    TH2* combined = CloneTH2(hParticle, cloneName);
    if (!combined) continue;
    combined->Add(hBar);
    return combined;
  }

  return nullptr;
}

TH2* GetCharmLambdaHist(TFile* f, const char* cloneName)
{
  return GetChargeCombinedHist(
    f,
    {"fHistPtLambdac", "fHistPtLambdacPlus"},
    {"fHistPtLambdac", "fHistPtLambdacPlus"},
    cloneName
  );
}

TH2* GetCharmDHist(TFile* f, const char* cloneName)
{
  return GetChargeCombinedHist(f, {"fHistPtDplus"}, {"fHistPtDplus"}, cloneName);
}

TH2* GetBeautyLambdaHist(TFile* f, const char* cloneName)
{
  return GetChargeCombinedHist(f, {"fHistPtLambdab"}, {"fHistPtLambdab"}, cloneName);
}

TH2* GetBeautyBHist(TFile* f, const char* cloneName)
{
  return GetChargeCombinedHist(f, {"fHistPtBplus"}, {"fHistPtBplus"}, cloneName);
}

// same logic as your spectra macro
std::pair<int,int> PercentileRange(TH1* hMult, double pTop, double pBot)
{
  int nb = hMult->GetNbinsX();
  double total = hMult->Integral(1, nb);
  if (total <= 0) return {1, nb};

  double thrTop = total*(pTop/100.0);
  double thrBot = total*(pBot/100.0);

  double cum = 0.0;
  int yH = nb, yL = nb;

  for (int b = nb; b >= 1; --b) {
    cum += hMult->GetBinContent(b);
    if (cum >= thrTop) { yH = b; break; }
  }
  for (int b = yH; b >= 1; --b) {
    if (cum >= thrBot) { yL = b; break; }
    cum += hMult->GetBinContent(b-1);
  }
  if (yL > yH) std::swap(yL, yH);
  return {yL, yH};
}

struct CDef { double pTop, pBot; const char* tag; const char* label; };

static const std::vector<CDef> kClasses = {
  {  0, 20, "0_20",   "0-20%"   },
  { 20, 40, "20_40",  "20-40%"  },
  { 40, 60, "40_60",  "40-60%"  },
  { 60, 80, "60_80",  "60-80%"  },
  { 80,100, "80_100", "80-100%" }
};

// Tune styles (two curves)
struct TuneStyle { int color; int lstyle; int lwidth; int mstyle; };
static const TuneStyle kTuneStyle[2] = {
  { kBlue+1, 1, 3, 20 }, // MONASH
  { kRed+1,  1, 3, 21 }  // JUNCTIONS
};

// Integrate TH2 over pT in [ptMin,ptMax] and mult bins yr.first..yr.second
double YieldInClass(TH2* h2, std::pair<int,int> yr, double ptMin, double ptMax)
{
  if (!h2) return 0.0;

  int x1 = 1;
  int x2 = h2->GetXaxis()->GetNbins();

  if (ptMax > ptMin) {
    x1 = std::max(1, h2->GetXaxis()->FindBin(ptMin));
    x2 = std::min(h2->GetXaxis()->GetNbins(), h2->GetXaxis()->FindBin(ptMax - 1e-9));
  }

  // counts (not width-corrected) — correct for yields
  return h2->Integral(x1, x2, yr.first, yr.second);
}

// mean ± SEM over subsamples
std::pair<double,double> MeanSEM(const std::vector<double>& v)
{
  if (v.empty()) return {0.0, 0.0};
  double mean = 0.0;
  for (double x : v) mean += x;
  mean /= (double)v.size();

  if (v.size() == 1) return {mean, 0.0};

  double var = 0.0;
  for (double x : v) var += (x-mean)*(x-mean);

  double sem = std::sqrt(var / (v.size() * (v.size()-1)));
  return {mean, sem};
}

void DrawRatioVsMult(const std::vector<double>& yM, const std::vector<double>& eM,
                     const std::vector<double>& yJ, const std::vector<double>& eJ,
                     const char* title, const char* ytitle, const char* outPng)
{
  const int n = (int)kClasses.size();

  // x positions 1..n to use a labeled frame histogram
  std::vector<double> x(n), ex(n, 0.0);
  for (int i=0;i<n;++i) x[i] = i+1;

  TCanvas* c = new TCanvas(Form("c_%s", outPng), title, 1000, 650);

  // frame for labeled x-axis
  TH1D* frame = new TH1D("frame","", n, 0.5, n+0.5);
  frame->SetTitle(title);
  frame->GetYaxis()->SetTitle(ytitle);
  frame->GetXaxis()->SetTitle("Multiplicity percentile");
  for (int i=0;i<n;++i) frame->GetXaxis()->SetBinLabel(i+1, kClasses[i].label);

  double ymin = 1e9, ymax = -1e9;
  for (int i=0;i<n;++i){
    ymin = std::min(ymin, std::min(yM[i]-eM[i], yJ[i]-eJ[i]));
    ymax = std::max(ymax, std::max(yM[i]+eM[i], yJ[i]+eJ[i]));
  }
  if (!(ymax > ymin)) { ymin = 0.0; ymax = 1.0; }
  double pad = 0.25*(ymax - ymin);
  frame->SetMinimum(std::max(0.0, ymin - pad));
  frame->SetMaximum(ymax + pad);

  frame->Draw("AXIS");

  TGraphErrors* gM = new TGraphErrors(n, x.data(), (double*)yM.data(), ex.data(), (double*)eM.data());
  TGraphErrors* gJ = new TGraphErrors(n, x.data(), (double*)yJ.data(), ex.data(), (double*)eJ.data());

  gM->SetLineColor(kTuneStyle[0].color);
  gM->SetLineWidth(kTuneStyle[0].lwidth);
  gM->SetLineStyle(kTuneStyle[0].lstyle);
  gM->SetMarkerColor(kTuneStyle[0].color);
  gM->SetMarkerStyle(kTuneStyle[0].mstyle);
  gM->SetMarkerSize(1.2);

  gJ->SetLineColor(kTuneStyle[1].color);
  gJ->SetLineWidth(kTuneStyle[1].lwidth);
  gJ->SetLineStyle(kTuneStyle[1].lstyle);
  gJ->SetMarkerColor(kTuneStyle[1].color);
  gJ->SetMarkerStyle(kTuneStyle[1].mstyle);
  gJ->SetMarkerSize(1.2);

  gM->Draw("LP SAME");
  gJ->Draw("LP SAME");

  TLegend* leg = new TLegend(0.65, 0.70, 0.88, 0.85);
  leg->SetTextSize(0.04);
  leg->AddEntry(gM, "MONASH", "lp");
  leg->AddEntry(gJ, "JUNCTIONS", "lp");
  leg->Draw();

  c->SaveAs(PlotPathUtils::BuildPtMultiplicityPlotPath(outPng));

  delete leg;
  delete gM;
  delete gJ;
  delete frame;
  delete c;
}

} // namespace


void Plot_HF_Ratios_vsMultiplicityPercentile_subsamples_WithPrefixes(
  const char* cPrefixMONASH = "ccbar_MONASH_sub",
  const char* cPrefixJUN    = "ccbar_JUNCTIONS_sub",
  const char* bPrefixMONASH = "bbbar_MONASH_sub",
  const char* bPrefixJUN    = "bbbar_JUNCTIONS_sub",
  int nSub                  = 10,
  // set ptMax<=ptMin to integrate ALL pT bins
  double ptMin              = 0.0,
  double ptMax              = -1.0
)
{
  SetStyle();
  if (nSub <= 0) { std::cout << "nSub must be > 0\n"; return; }

  const char* MULT_HIST = "fHistMultiplicity";

  // storage: for each class we’ll accumulate subsample ratios, then mean±SEM
  const int nC = (int)kClasses.size();

  // ----- Lambda_c / D -----
  std::vector<double> yLCM(nC,0), eLCM(nC,0), yLCJ(nC,0), eLCJ(nC,0);

  for (int ic=0; ic<nC; ++ic){
    std::vector<double> rM, rJ;
    rM.reserve(nSub); rJ.reserve(nSub);

    for (int is=0; is<nSub; ++is){
      TFile* fM = TFile::Open(Form("%s%d.root", cPrefixMONASH, is), "READ");
      TFile* fJ = TFile::Open(Form("%s%d.root", cPrefixJUN,    is), "READ");
      if (!fM || fM->IsZombie() || !fJ || fJ->IsZombie()) { if(fM)fM->Close(); if(fJ)fJ->Close(); continue; }

      TH1* hMultM = GetObj<TH1>(fM, MULT_HIST);
      TH2* hLcM   = GetCharmLambdaHist(fM, Form("hLcM_%d_%d", ic, is));
      TH2* hDM    = GetCharmDHist(fM, Form("hDM_%d_%d", ic, is));

      TH1* hMultJ = GetObj<TH1>(fJ, MULT_HIST);
      TH2* hLcJ   = GetCharmLambdaHist(fJ, Form("hLcJ_%d_%d", ic, is));
      TH2* hDJ    = GetCharmDHist(fJ, Form("hDJ_%d_%d", ic, is));

      auto yrM = PercentileRange(hMultM, kClasses[ic].pTop, kClasses[ic].pBot);
      auto yrJ = PercentileRange(hMultJ, kClasses[ic].pTop, kClasses[ic].pBot);

      double NLcM = YieldInClass(hLcM, yrM, ptMin, ptMax);
      double NDM  = YieldInClass(hDM,  yrM, ptMin, ptMax);

      double NLcJ = YieldInClass(hLcJ, yrJ, ptMin, ptMax);
      double NDJ  = YieldInClass(hDJ,  yrJ, ptMin, ptMax);

      if (NDM > 0) rM.push_back(NLcM/NDM);
      if (NDJ > 0) rJ.push_back(NLcJ/NDJ);

      delete hLcM;
      delete hDM;
      delete hLcJ;
      delete hDJ;
      fM->Close(); fJ->Close();
    }

    auto [mM, sM] = MeanSEM(rM);
    auto [mJ, sJ] = MeanSEM(rJ);

    yLCM[ic]=mM; eLCM[ic]=sM;
    yLCJ[ic]=mJ; eLCJ[ic]=sJ;
  }

  DrawRatioVsMult(
    yLCM, eLCM, yLCJ, eLCJ,
    "(#Lambda_{c}^{+} + #bar{#Lambda}_{c}^{-})/D^{#pm} vs Multiplicity Percentile",
    "(#Lambda_{c}^{+} + #bar{#Lambda}_{c}^{-})/D^{#pm}",
    "Ratio_Lambdac_over_Dpm_vsMult.png"
  );

  // ----- Lambda_b / B+ -----
  std::vector<double> yLBM(nC,0), eLBM(nC,0), yLBJ(nC,0), eLBJ(nC,0);

  for (int ic=0; ic<nC; ++ic){
    std::vector<double> rM, rJ;
    rM.reserve(nSub); rJ.reserve(nSub);

    for (int is=0; is<nSub; ++is){
      TFile* fM = TFile::Open(Form("%s%d.root", bPrefixMONASH, is), "READ");
      TFile* fJ = TFile::Open(Form("%s%d.root", bPrefixJUN,    is), "READ");
      if (!fM || fM->IsZombie() || !fJ || fJ->IsZombie()) { if(fM)fM->Close(); if(fJ)fJ->Close(); continue; }

      TH1* hMultM = GetObj<TH1>(fM, MULT_HIST);
      TH2* hLbM   = GetBeautyLambdaHist(fM, Form("hLbM_%d_%d", ic, is));
      TH2* hBM    = GetBeautyBHist(fM, Form("hBM_%d_%d", ic, is));

      TH1* hMultJ = GetObj<TH1>(fJ, MULT_HIST);
      TH2* hLbJ   = GetBeautyLambdaHist(fJ, Form("hLbJ_%d_%d", ic, is));
      TH2* hBJ    = GetBeautyBHist(fJ, Form("hBJ_%d_%d", ic, is));

      auto yrM = PercentileRange(hMultM, kClasses[ic].pTop, kClasses[ic].pBot);
      auto yrJ = PercentileRange(hMultJ, kClasses[ic].pTop, kClasses[ic].pBot);

      double NLbM = YieldInClass(hLbM, yrM, ptMin, ptMax);
      double NBM  = YieldInClass(hBM,  yrM, ptMin, ptMax);

      double NLbJ = YieldInClass(hLbJ, yrJ, ptMin, ptMax);
      double NBJ  = YieldInClass(hBJ,  yrJ, ptMin, ptMax);

      if (NBM > 0) rM.push_back(NLbM/NBM);
      if (NBJ > 0) rJ.push_back(NLbJ/NBJ);

      delete hLbM;
      delete hBM;
      delete hLbJ;
      delete hBJ;
      fM->Close(); fJ->Close();
    }

    auto [mM, sM] = MeanSEM(rM);
    auto [mJ, sJ] = MeanSEM(rJ);

    yLBM[ic]=mM; eLBM[ic]=sM;
    yLBJ[ic]=mJ; eLBJ[ic]=sJ;
  }

  DrawRatioVsMult(
    yLBM, eLBM, yLBJ, eLBJ,
    "(#Lambda_{b}^{0} + #bar{#Lambda}_{b}^{0})/B^{#pm} vs Multiplicity Percentile",
    "(#Lambda_{b}^{0} + #bar{#Lambda}_{b}^{0})/B^{#pm}",
    "Ratio_Lambdab_over_Bpm_vsMult.png"
  );

  std::cout << "Saved:\n"
            << "  " << PlotPathUtils::GetPtMultiplicityPlotsDir()
            << "/Ratio_Lambdac_over_Dpm_vsMult.png\n"
            << "  " << PlotPathUtils::GetPtMultiplicityPlotsDir()
            << "/Ratio_Lambdab_over_Bpm_vsMult.png\n";
}


void Plot_HF_Ratios_vsMultiplicityPercentile_subsamples(const char* dateTag = "",
                                                            int nSub = 10,
                                                            double ptMin = 0.0,
                                                            double ptMax = -1.0)
{
  TString resolvedDate = PlotPathUtils::ResolveAnalysisDate(dateTag);
  if (resolvedDate.Length() == 0) return;

  TString cPrefixMONASH = PlotPathUtils::ResolveAnalyzedPrefix(
    resolvedDate, "Charm", {"hf_MONASH_sub", "ccbar_MONASH_sub"});
  TString cPrefixJUN = PlotPathUtils::ResolveAnalyzedPrefix(
    resolvedDate, "Charm", {"hf_JUNCTIONS_sub", "ccbar_JUNCTIONS_sub"});
  TString bPrefixMONASH = PlotPathUtils::ResolveAnalyzedPrefix(
    resolvedDate, "Beauty", {"hf_MONASH_sub", "bbbar_MONASH_sub"});
  TString bPrefixJUN = PlotPathUtils::ResolveAnalyzedPrefix(
    resolvedDate, "Beauty", {"hf_JUNCTIONS_sub", "bbbar_JUNCTIONS_sub"});

  std::cout << "HF ratio input date: " << resolvedDate << "\n";
  std::cout << "  Charm MONASH     : " << cPrefixMONASH << "*.root\n";
  std::cout << "  Charm JUNCTIONS  : " << cPrefixJUN << "*.root\n";
  std::cout << "  Beauty MONASH    : " << bPrefixMONASH << "*.root\n";
  std::cout << "  Beauty JUNCTIONS : " << bPrefixJUN << "*.root\n";

  Plot_HF_Ratios_vsMultiplicityPercentile_subsamples_WithPrefixes(
    cPrefixMONASH.Data(),
    cPrefixJUN.Data(),
    bPrefixMONASH.Data(),
    bPrefixJUN.Data(),
    nSub,
    ptMin,
    ptMax
  );
}

void runHFRatios(const char* dateTag = "",
                 int nSub = 10,
                 double ptMin = 0.0,
                 double ptMax = -1.0)
{
  Plot_HF_Ratios_vsMultiplicityPercentile_subsamples(dateTag, nSub, ptMin, ptMax);
}

void runHFRatiosWax(const char* dateTag = "",
                    int nSub = 10,
                    double ptMin = 0.0,
                    double ptMax = -1.0)
{
  Plot_HF_Ratios_vsMultiplicityPercentile_subsamples(dateTag, nSub, ptMin, ptMax);
}
