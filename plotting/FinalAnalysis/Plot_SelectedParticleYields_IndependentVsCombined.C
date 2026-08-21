// ---------------------------------------------------------------------------
// Plot_SelectedParticleYields_IndependentVsCombined.C
//
// Plot per-event yields for selected beauty and charm species from analyzed
// ROOT files, comparing the latest (or explicitly chosen) independent and
// combined samples.
//
// Beauty species:
//   B^{#pm}, B^{0}/#bar{B}^{0}, #Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0}
//
// Charm species:
//   D^{#pm}, D^{0}/#bar{D}^{0}, #Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-}
//
// Important note:
// The analyzed ROOT files store these species with charge-conjugate states
// combined because the analysis macros fill with abs(PDG). Therefore:
//   - B^{#pm} comes from fHistPtBplus
//   - D^{#pm} comes from fHistPtDplus
//   - B^{0}/#bar{B}^{0}, D^{0}/#bar{D}^{0}, #Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0},
//     and #Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-} are also charge-conjugate combined
//
// The per-event yield is therefore:
//   (combined histogram integral) / N_events
// and the plotted uncertainty is taken from the spread of the per-subsample
// yields (mean ± SEM).
//
// Usage:
//   root -l -b -q 'plotting/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C'
//
//   root -l -b -q \
//     'plotting/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C("12-01-2026","27-03-2026",10)'
// ---------------------------------------------------------------------------

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <utility>
#include <vector>

#include "TCanvas.h"
#include "TCollection.h"
#include "TFile.h"
#include "TGraphErrors.h"
#include "TH1.h"
#include "TH1D.h"
#include "TH2.h"
#include "TH2D.h"
#include "TLegend.h"
#include "TList.h"
#include "TObject.h"
#include "TPad.h"
#include "TLine.h"
#include "TString.h"
#include "TStyle.h"
#include "TSystem.h"
#include "TSystemDirectory.h"
#include "TSystemFile.h"
#include "TLatex.h"

#include "../HistogramErrorUtils.h"

namespace {

enum class SampleKind {
  Unknown,
  Independent,
  Combined
};

struct SpeciesDef {
  TString label;
  std::vector<TString> combinedHistCandidates;
  std::vector<TString> splitHistBases;
  double scaleFactor;
};

struct YieldStats {
  double mean = 0.0;
  double error = 0.0;
  int nLoaded = 0;
};

std::pair<double,double> MeanSEM(const std::vector<double>& values)
{
  if (values.empty()) return std::make_pair(0.0, 0.0);

  double mean = 0.0;
  for (double value : values) mean += value;
  mean /= static_cast<double>(values.size());

  if (values.size() == 1) return std::make_pair(mean, 0.0);

  double var = 0.0;
  for (double value : values) var += (value - mean) * (value - mean);
  const double sem = std::sqrt(var / (values.size() * (values.size() - 1)));
  return std::make_pair(mean, sem);
}

TString ResolveAbsolutePath(const char* path)
{
  TString resolved = path ? TString(path) : TString("");
  resolved = resolved.Strip(TString::kBoth);
  if (resolved.IsNull()) return TString("");

  if (!gSystem->IsAbsoluteFileName(resolved.Data())) {
    resolved = gSystem->ConcatFileName(gSystem->WorkingDirectory(), resolved.Data());
  }

  return gSystem->UnixPathName(resolved);
}

TString BaseDirFromMacroPath(const char* macroPath)
{
  TString resolved = ResolveAbsolutePath(macroPath);
  if (resolved.IsNull()) return TString("");

  TString level1 = gSystem->DirName(resolved.Data()); // FinalAnalysis
  TString level2 = gSystem->DirName(level1.Data());   // plotting
  TString level3 = gSystem->DirName(level2.Data());   // Hadronization
  return gSystem->UnixPathName(level3);
}

TString GetHadronizationBaseDir()
{
  const char* env = gSystem->Getenv("HADRONIZATION_BASE");
  if (env && env[0] != '\0') return TString(env);

  TString fromMacro = BaseDirFromMacroPath(__FILE__);
  if (!fromMacro.IsNull()) return fromMacro;

  const char* candidates[] = {
    "base_path.txt",
    "../base_path.txt",
    "../../base_path.txt",
    nullptr
  };

  for (int i = 0; candidates[i] != nullptr; ++i) {
    std::ifstream fin(candidates[i]);
    if (!fin) continue;

    std::string line;
    std::getline(fin, line);
    if (!line.empty()) return TString(line.c_str());
  }

  return gSystem->UnixPathName(gSystem->WorkingDirectory());
}

TString GetAnalyzedDataDir()
{
  return GetHadronizationBaseDir() + "/AnalyzedData";
}

TString GetOutputDir()
{
  TString outDir = GetHadronizationBaseDir() + "/plotting/FinalAnalysis/Plots";
  gSystem->mkdir(outDir, true);
  return outDir;
}

bool FileExists(const TString& path)
{
  return !gSystem->AccessPathName(path.Data());
}

bool ParseDateTag(const TString& tag, int& year, int& month, int& day)
{
  unsigned int d = 0;
  unsigned int m = 0;
  unsigned int y = 0;

  if (std::sscanf(tag.Data(), "%u-%u-%u", &d, &m, &y) != 3) return false;
  if (d < 1 || d > 31) return false;
  if (m < 1 || m > 12) return false;
  if (y < 1900) return false;

  day = static_cast<int>(d);
  month = static_cast<int>(m);
  year = static_cast<int>(y);
  return true;
}

std::vector<TString> GetSortedAnalysisDates()
{
  std::vector<std::pair<long long, TString>> datedFolders;

  TSystemDirectory dir("AnalyzedData", GetAnalyzedDataDir());
  TList* entries = dir.GetListOfFiles();
  if (!entries) return {};

  TIter next(entries);
  while (TObject* obj = next()) {
    TSystemFile* file = dynamic_cast<TSystemFile*>(obj);
    if (!file || !file->IsDirectory()) continue;

    const TString name = file->GetName();
    if (name == "." || name == "..") continue;

    int year = 0;
    int month = 0;
    int day = 0;
    if (!ParseDateTag(name, year, month, day)) continue;

    const long long key = 10000LL * year + 100LL * month + day;
    datedFolders.push_back(std::make_pair(key, name));
  }

  std::sort(datedFolders.begin(), datedFolders.end(),
            [](const std::pair<long long, TString>& a,
               const std::pair<long long, TString>& b) {
              return a.first < b.first;
            });

  std::vector<TString> sortedDates;
  sortedDates.reserve(datedFolders.size());
  for (const auto& entry : datedFolders) sortedDates.push_back(entry.second);
  return sortedDates;
}

SampleKind DetectSampleKind(const TString& dateTag)
{
  const TString analyzedDir = GetAnalyzedDataDir() + "/" + dateTag;

  const std::vector<TString> combinedCandidates = {
    analyzedDir + "/Charm/hf_MONASH_sub0.root",
    analyzedDir + "/Charm/hf_JUNCTIONS_sub0.root",
    analyzedDir + "/Beauty/hf_MONASH_sub0.root",
    analyzedDir + "/Beauty/hf_JUNCTIONS_sub0.root"
  };
  for (const TString& path : combinedCandidates) {
    if (FileExists(path)) return SampleKind::Combined;
  }

  const std::vector<TString> independentCandidates = {
    analyzedDir + "/Charm/ccbar_MONASH_sub0.root",
    analyzedDir + "/Charm/ccbar_JUNCTIONS_sub0.root",
    analyzedDir + "/Beauty/bbbar_MONASH_sub0.root",
    analyzedDir + "/Beauty/bbbar_JUNCTIONS_sub0.root"
  };
  for (const TString& path : independentCandidates) {
    if (FileExists(path)) return SampleKind::Independent;
  }

  return SampleKind::Unknown;
}

bool ResolveLatestDateOfKind(SampleKind kind, TString& tag)
{
  const std::vector<TString> sortedDates = GetSortedAnalysisDates();
  for (auto it = sortedDates.rbegin(); it != sortedDates.rend(); ++it) {
    if (DetectSampleKind(*it) == kind) {
      tag = *it;
      return true;
    }
  }
  return false;
}

void ResolveSampleFolders(TString& independentTag, TString& combinedTag)
{
  independentTag = independentTag.Strip(TString::kBoth);
  combinedTag = combinedTag.Strip(TString::kBoth);

  if (independentTag.IsNull()) {
    if (!ResolveLatestDateOfKind(SampleKind::Independent, independentTag)) {
      std::cerr << "Could not find any independent analyzed folder under "
                << GetAnalyzedDataDir() << "\n";
    }
  }

  if (combinedTag.IsNull()) {
    if (!ResolveLatestDateOfKind(SampleKind::Combined, combinedTag)) {
      std::cerr << "Could not find any combined analyzed folder under "
                << GetAnalyzedDataDir() << "\n";
    }
  }
}

void SetStyle()
{
  gStyle->SetOptStat(0);
  gStyle->SetPadBottomMargin(0.18);
  gStyle->SetPadLeftMargin(0.12);
  gStyle->SetPadRightMargin(0.18);
  gStyle->SetPadTopMargin(0.10);
  gStyle->SetLegendBorderSize(0);
  gStyle->SetTitleSize(0.05, "XY");
  gStyle->SetLabelSize(0.042, "XY");
  gStyle->SetEndErrorSize(4);
}

TString ResolvePrefixStem(const TString& dateTag,
                          const TString& flavour,
                          const TString& tune)
{
  std::vector<TString> stems;

  if (flavour == "Charm") {
    stems.push_back(Form("hf_%s_sub", tune.Data()));
    stems.push_back(Form("ccbar_%s_sub", tune.Data()));
  } else if (flavour == "Beauty") {
    stems.push_back(Form("hf_%s_sub", tune.Data()));
    stems.push_back(Form("bbbar_%s_sub", tune.Data()));
  } else {
    return TString("");
  }

  for (const TString& stem : stems) {
    const TString probe = Form("%s/%s/%s/%s0.root",
                               GetAnalyzedDataDir().Data(),
                               dateTag.Data(),
                               flavour.Data(),
                               stem.Data());
    if (FileExists(probe)) return stem;
  }

  return TString("");
}

TH2* CloneTH2(TH2* h, const char* cloneName)
{
  if (!h) return nullptr;
  TH2* clone = dynamic_cast<TH2*>(h->Clone(cloneName));
  if (clone) {
    clone->SetDirectory(nullptr);
    PlotErrorUtils::EnsureSumw2(clone);
  }
  return clone;
}

TH2* GetChargeCombinedTH2(TFile* file,
                          const SpeciesDef& species,
                          const char* cloneName)
{
  if (!file) return nullptr;

  for (const TString& name : species.combinedHistCandidates) {
    TH2* h = dynamic_cast<TH2*>(file->Get(name));
    if (h) return CloneTH2(h, cloneName);
  }

  for (const TString& base : species.splitHistBases) {
    TH2* hParticle = dynamic_cast<TH2*>(file->Get(Form("%sParticle", base.Data())));
    TH2* hBar = dynamic_cast<TH2*>(file->Get(Form("%sBar", base.Data())));
    if (!hParticle || !hBar) continue;

    TH2* combined = CloneTH2(hParticle, cloneName);
    if (!combined) continue;
    PlotErrorUtils::EnsureSumw2(hBar);
    combined->Add(hBar);
    return combined;
  }

  return nullptr;
}

double GetEventCount(TFile* file)
{
  if (!file) return 0.0;

  if (TH1* hTaggedEventCount = dynamic_cast<TH1*>(file->Get("fHistTaggedEventCount"))) {
    return hTaggedEventCount->Integral(1, hTaggedEventCount->GetNbinsX());
  }

  if (TH1* hEventCount = dynamic_cast<TH1*>(file->Get("fHistEventCount"))) {
    return hEventCount->Integral(1, hEventCount->GetNbinsX());
  }

  if (TH1* hMult = dynamic_cast<TH1*>(file->Get("fHistMultiplicity"))) {
    return hMult->Integral(1, hMult->GetNbinsX());
  }

  return 0.0;
}

YieldStats ComputeYieldStats(const TString& dateTag,
                             const TString& flavour,
                             const TString& tune,
                             const SpeciesDef& species,
                             int nSub)
{
  YieldStats stats;

  const TString prefixStem = ResolvePrefixStem(dateTag, flavour, tune);
  if (prefixStem.IsNull()) {
    std::cerr << "Could not resolve file prefix for "
              << flavour << " " << tune << " in sample " << dateTag << ".\n";
    return stats;
  }

  double totalSpecies = 0.0;
  double totalEvents = 0.0;
  std::vector<double> subYields;
  subYields.reserve(nSub);

  for (int iSub = 0; iSub < nSub; ++iSub) {
    const TString filePath = Form("%s/%s/%s/%s%d.root",
                                  GetAnalyzedDataDir().Data(),
                                  dateTag.Data(),
                                  flavour.Data(),
                                  prefixStem.Data(),
                                  iSub);
    if (!FileExists(filePath)) {
      std::cerr << "Warning: missing file " << filePath << "\n";
      continue;
    }

    TFile* inputFile = TFile::Open(filePath, "READ");
    if (!inputFile || inputFile->IsZombie()) {
      std::cerr << "Warning: could not open " << filePath << "\n";
      if (inputFile) inputFile->Close();
      delete inputFile;
      continue;
    }

    TH2* hSpecies = GetChargeCombinedTH2(
      inputFile, species, Form("hSpecies_%s_%s_%s_sub%d",
                               flavour.Data(),
                               tune.Data(),
                               dateTag.Data(),
                               iSub));
    const double nEvents = GetEventCount(inputFile);

    if (!hSpecies || nEvents <= 0.0) {
      std::cerr << "Warning: missing required histograms in " << filePath
                << " for " << species.label << "\n";
      delete hSpecies;
      inputFile->Close();
      delete inputFile;
      continue;
    }

    const double speciesCount = hSpecies->Integral(1,
                                                   hSpecies->GetNbinsX(),
                                                   1,
                                                   hSpecies->GetNbinsY());

    const double subYield = species.scaleFactor * speciesCount / nEvents;
    subYields.push_back(subYield);
    totalSpecies += species.scaleFactor * speciesCount;
    totalEvents += nEvents;
    stats.nLoaded++;

    delete hSpecies;
    inputFile->Close();
    delete inputFile;
  }

  if (stats.nLoaded == 0 || totalEvents <= 0.0) return stats;

  stats.mean = totalSpecies / totalEvents;
  stats.error = MeanSEM(subYields).second;

  return stats;
}

TGraphErrors* BuildYieldGraph(const TString& dateTag,
                              const TString& flavour,
                              const TString& tune,
                              const std::vector<SpeciesDef>& speciesDefs,
                              int nSub,
                              double xShift,
                              double xError,
                              Color_t color,
                              Style_t markerStyle)
{
  (void)xShift;
  (void)xError;

  const int n = static_cast<int>(speciesDefs.size());
  TGraphErrors* graph = new TGraphErrors(n);
  graph->SetName(Form("gYield_%s_%s_%s", dateTag.Data(), flavour.Data(), tune.Data()));
  graph->SetLineColor(color);
  graph->SetMarkerColor(color);
  graph->SetLineWidth(2);
  graph->SetMarkerStyle(markerStyle);
  graph->SetMarkerSize(1.2);

  for (int i = 0; i < n; ++i) {
    const YieldStats stats = ComputeYieldStats(dateTag, flavour, tune, speciesDefs[i], nSub);
    const double x = static_cast<double>(i + 1);
    graph->SetPoint(i, x, stats.mean);
    graph->SetPointError(i, 0.5, stats.error);
  }

  return graph;
}

TGraphErrors* BuildRatioGraph(const TString& independentTag,
                              const TString& combinedTag,
                              const TString& flavour,
                              const TString& tune,
                              const std::vector<SpeciesDef>& speciesDefs,
                              int nSub,
                              Color_t color,
                              Style_t markerStyle)
{
  const int n = static_cast<int>(speciesDefs.size());
  TGraphErrors* graph = new TGraphErrors(n);
  graph->SetName(Form("gYieldRatio_%s_%s_%s",
                      flavour.Data(),
                      tune.Data(),
                      independentTag.Data()));
  graph->SetLineColor(color);
  graph->SetMarkerColor(color);
  graph->SetLineWidth(2);
  graph->SetMarkerStyle(markerStyle);
  graph->SetMarkerSize(1.2);

  for (int i = 0; i < n; ++i) {
    const YieldStats independentStats =
      ComputeYieldStats(independentTag, flavour, tune, speciesDefs[i], nSub);
    const YieldStats combinedStats =
      ComputeYieldStats(combinedTag, flavour, tune, speciesDefs[i], nSub);

    double ratio = 0.0;
    double ratioError = 0.0;
    if (independentStats.mean > 0.0 && combinedStats.mean > 0.0) {
      ratio = independentStats.mean / combinedStats.mean;

      const double independentRelError =
        (independentStats.error > 0.0 ? independentStats.error / independentStats.mean : 0.0);
      const double combinedRelError =
        (combinedStats.error > 0.0 ? combinedStats.error / combinedStats.mean : 0.0);
      ratioError = ratio * std::sqrt(independentRelError * independentRelError +
                                     combinedRelError * combinedRelError);
    }

    const double x = static_cast<double>(i + 1);
    graph->SetPoint(i, x, ratio);
    graph->SetPointError(i, 0.5, ratioError);
  }

  return graph;
}

double PositiveGraphMinimum(TGraphErrors* graph)
{
  if (!graph) return 0.0;

  double minVal = 1.0e99;
  const int n = graph->GetN();
  for (int i = 0; i < n; ++i) {
    double x = 0.0;
    double y = 0.0;
    graph->GetPoint(i, x, y);
    if (y > 0.0 && y < minVal) minVal = y;
  }

  return (minVal < 1.0e90 ? minVal : 0.0);
}

double PositiveGraphMinimumWithErrors(TGraphErrors* graph)
{
  if (!graph) return 0.0;

  double minVal = 1.0e99;
  const int n = graph->GetN();
  for (int i = 0; i < n; ++i) {
    double x = 0.0;
    double y = 0.0;
    graph->GetPoint(i, x, y);
    const double low = y - graph->GetErrorY(i);
    if (low > 0.0 && low < minVal) minVal = low;
    if (y > 0.0 && y < minVal) minVal = y;
  }

  return (minVal < 1.0e90 ? minVal : 0.0);
}

double GraphMaximum(TGraphErrors* graph)
{
  if (!graph) return 0.0;

  double maxVal = 0.0;
  const int n = graph->GetN();
  for (int i = 0; i < n; ++i) {
    double x = 0.0;
    double y = 0.0;
    graph->GetPoint(i, x, y);
    maxVal = std::max(maxVal, y + graph->GetErrorY(i));
  }

  return maxVal;
}

double SmallestPositive(double a, double b)
{
  if (a > 0.0 && b > 0.0) return std::min(a, b);
  if (a > 0.0) return a;
  if (b > 0.0) return b;
  return 0.0;
}

void SaveCanvas(TCanvas* canvas, const TString& outBase)
{
  canvas->SaveAs((outBase + ".png").Data());
  canvas->SaveAs((outBase + ".pdf").Data());
  canvas->SaveAs((outBase + ".C").Data());
}

std::vector<SpeciesDef> BeautySpecies()
{
  return {
    {"B^{#pm}",                              {"fHistPtBplus"},                        {"fHistPtBplus"},                        1.0},
    {"B^{0}/#bar{B}^{0}",                    {"fHistPtBzero"},                        {"fHistPtBzero"},                        1.0},
    {"#Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0}",{"fHistPtLambdab"},                      {"fHistPtLambdab"},                      1.0}
  };
}

std::vector<SpeciesDef> CharmSpecies()
{
  return {
    {"D^{#pm}",                              {"fHistPtDplus"},                        {"fHistPtDplus"},                        1.0},
    {"D^{0}/#bar{D}^{0}",                    {"fHistPtDzero"},                        {"fHistPtDzero"},                        1.0},
    {"#Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-}",{"fHistPtLambdac", "fHistPtLambdacPlus"},{"fHistPtLambdac", "fHistPtLambdacPlus"},1.0}
  };
}

void DrawYieldComparison(const TString& independentTag,
                         const TString& combinedTag,
                         const TString& flavour,
                         const TString& tune,
                         const std::vector<SpeciesDef>& speciesDefs,
                         int nSub)
{
  TGraphErrors* gIndependent = BuildYieldGraph(independentTag, flavour, tune, speciesDefs,
                                               nSub, -0.10, 0.055, kBlue + 1, 20);
  TGraphErrors* gCombined = BuildYieldGraph(combinedTag, flavour, tune, speciesDefs,
                                            nSub, +0.10, 0.055, kRed + 1, 21);
  TGraphErrors* gRatio = BuildRatioGraph(independentTag, combinedTag, flavour, tune, speciesDefs,
                                         nSub, kBlack, 24);

  const int nBins = static_cast<int>(speciesDefs.size());
  TH1D* frame = new TH1D(Form("hFrame_%s_%s", flavour.Data(), tune.Data()), "",
                         nBins, 0.5, nBins + 0.5);
  for (int i = 0; i < nBins; ++i) {
    frame->GetXaxis()->SetBinLabel(i + 1, speciesDefs[i].label.Data());
  }

  const double yMax = std::max(1.0e-6,
                               1.35 * std::max(GraphMaximum(gIndependent),
                                               GraphMaximum(gCombined)));
  const double yMinCandidate = SmallestPositive(PositiveGraphMinimum(gIndependent),
                                                PositiveGraphMinimum(gCombined));
  const double yMin = (yMinCandidate > 0.0 ? 0.5 * yMinCandidate : 1.0e-8);
  double ratioMax = std::max(1.05, 1.20 * GraphMaximum(gRatio));
  const double ratioMinCandidate = PositiveGraphMinimumWithErrors(gRatio);
  double ratioMin = (ratioMinCandidate > 0.0 ? 0.80 * ratioMinCandidate : 0.0);
  ratioMin = std::min(ratioMin, 1.0);
  ratioMin = std::max(0.0, ratioMin);
  if (ratioMin >= 1.0 - 1.0e-9) ratioMin = 0.98;
  if (ratioMax <= ratioMin) ratioMax = ratioMin + 0.1;

  const double padBottom = 0.10;
  const double padTop = 0.90;
  const double yieldPadRight = 0.39;
  const double ratioPadLeft = 0.41;
  const double ratioPadRight = 0.76;
  const double legendPadLeft = 0.77;

  TCanvas* canvas = new TCanvas(Form("cYield_%s_%s", flavour.Data(), tune.Data()),
                                Form("%s %s yields", flavour.Data(), tune.Data()),
                                1540, 780);

  TPad* yieldPad = new TPad(Form("pYield_%s_%s", flavour.Data(), tune.Data()), "",
                            0.00, padBottom, yieldPadRight, padTop);
  yieldPad->SetLeftMargin(0.16);
  yieldPad->SetRightMargin(0.04);
  yieldPad->SetBottomMargin(0.22);
  yieldPad->SetTopMargin(0.07);
  yieldPad->SetTicks(1, 1);
  yieldPad->SetLogy();
  yieldPad->Draw();
  yieldPad->cd();

  frame->SetTitle("");
  frame->GetXaxis()->SetTitle("");
  frame->GetYaxis()->SetTitle("Per-event yield");
  frame->GetYaxis()->SetTitleOffset(1.25);
  frame->GetXaxis()->SetLabelSize(0.053);
  frame->GetXaxis()->SetLabelOffset(0.006);
  frame->GetYaxis()->SetRangeUser(yMin, yMax);
  frame->LabelsOption("v", "X");
  frame->Draw();

  gIndependent->Draw("P SAME");
  gCombined->Draw("P SAME");

  TLatex latex;
  canvas->cd();
  latex.SetNDC();
  latex.SetTextAlign(22);
  latex.SetTextSize(0.042);
  const double titleX = 0.5 * legendPadLeft;
  latex.DrawLatex(titleX, 0.948,
                  Form("%s %s Per-Event Yields", flavour.Data(), tune.Data()));

  TPad* ratioPad = new TPad(Form("pRatio_%s_%s", flavour.Data(), tune.Data()), "",
                            ratioPadLeft, padBottom, ratioPadRight, padTop);
  ratioPad->SetLeftMargin(0.18);
  ratioPad->SetRightMargin(0.05);
  ratioPad->SetBottomMargin(0.22);
  ratioPad->SetTopMargin(0.07);
  ratioPad->SetTicks(1, 1);
  ratioPad->Draw();
  ratioPad->cd();

  TH1D* ratioFrame = new TH1D(Form("hRatioFrame_%s_%s", flavour.Data(), tune.Data()), "",
                              nBins, 0.5, nBins + 0.5);
  ratioFrame->SetMinimum(ratioMin);
  ratioFrame->SetMaximum(ratioMax);
  ratioFrame->SetTitle("");
  ratioFrame->GetXaxis()->SetTitle("");
  ratioFrame->GetYaxis()->SetTitle("Independent / Combined");
  ratioFrame->GetXaxis()->SetLabelSize(0.053);
  ratioFrame->GetXaxis()->SetLabelOffset(0.006);
  ratioFrame->GetYaxis()->SetLabelSize(0.048);
  ratioFrame->GetYaxis()->SetTitleSize(0.050);
  ratioFrame->GetYaxis()->SetTitleOffset(1.35);
  ratioFrame->LabelsOption("v", "X");
  for (int i = 0; i < nBins; ++i) {
    ratioFrame->GetXaxis()->SetBinLabel(i + 1, speciesDefs[i].label.Data());
  }
  ratioFrame->Draw();

  TLine* unityLine = new TLine(0.5, 1.0, nBins + 0.5, 1.0);
  unityLine->SetLineColor(kBlack);
  unityLine->SetLineStyle(2);
  unityLine->SetLineWidth(2);
  unityLine->Draw();

  gRatio->Draw("P SAME");

  canvas->cd();
  TPad* legendPad = new TPad(Form("pLegend_%s_%s", flavour.Data(), tune.Data()), "",
                             legendPadLeft, padBottom, 1.00, padTop);
  legendPad->SetLeftMargin(0.04);
  legendPad->SetRightMargin(0.04);
  legendPad->SetBottomMargin(0.10);
  legendPad->SetTopMargin(0.07);
  legendPad->SetFillStyle(0);
  legendPad->SetFrameFillStyle(0);
  legendPad->SetFrameLineColor(0);
  legendPad->SetFrameBorderMode(0);
  legendPad->Draw();
  legendPad->cd();

  TLegend* legend = new TLegend(0.03, 0.64, 0.99, 0.87);
  legend->SetFillStyle(1001);
  legend->SetFillColor(kWhite);
  legend->SetBorderSize(1);
  legend->SetTextSize(0.062);
  legend->AddEntry(gIndependent, "Independent Sample", "pe");
  legend->AddEntry(gCombined, "Combined Sample", "pe");
  legend->AddEntry(gRatio, "Independent / Combined", "pe");
  legend->Draw();

  canvas->cd();
  TLatex axisLabel;
  axisLabel.SetNDC();
  axisLabel.SetTextAlign(22);
  axisLabel.SetTextSize(0.038);
  axisLabel.DrawLatex(titleX, 0.060, "Particle species");

  const TString outBase = Form("%s/SelectedParticleYields_%s_%s_%s_vs_%s",
                               GetOutputDir().Data(),
                               flavour.Data(),
                               tune.Data(),
                               independentTag.Data(),
                               combinedTag.Data());
  SaveCanvas(canvas, outBase);

  delete unityLine;
  delete ratioFrame;
  delete legend;
  delete frame;
  delete gIndependent;
  delete gCombined;
  delete gRatio;
  delete canvas;
}

} // namespace

void Plot_SelectedParticleYields_IndependentVsCombined(const char* independentTag = "",
                                                       const char* combinedTag = "",
                                                       int nSub = 10)
{
  SetStyle();

  TString independent = independentTag ? TString(independentTag) : TString("");
  TString combined = combinedTag ? TString(combinedTag) : TString("");
  ResolveSampleFolders(independent, combined);

  if (independent.IsNull() || combined.IsNull()) {
    std::cerr << "Could not resolve both independent and combined analysis folders.\n";
    return;
  }

  std::cout << "Using independent sample folder: " << independent << "\n";
  std::cout << "Using combined sample folder:    " << combined << "\n";
  std::cout << "Plotting charge-conjugate-combined species yields from the analyzed histograms.\n";

  DrawYieldComparison(independent, combined, "Beauty", "MONASH",    BeautySpecies(), nSub);
  DrawYieldComparison(independent, combined, "Beauty", "JUNCTIONS", BeautySpecies(), nSub);
  DrawYieldComparison(independent, combined, "Charm",  "MONASH",    CharmSpecies(),  nSub);
  DrawYieldComparison(independent, combined, "Charm",  "JUNCTIONS", CharmSpecies(),  nSub);

  std::cout << "Wrote selected-particle yield plots to:\n"
            << "  " << GetOutputDir() << "\n";
}

void runSelectedParticleYieldPlots(const char* independentTag = "",
                                   const char* combinedTag = "",
                                   int nSub = 10)
{
  Plot_SelectedParticleYields_IndependentVsCombined(independentTag, combinedTag, nSub);
}
