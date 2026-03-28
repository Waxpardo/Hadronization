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
//
// Usage:
//   root -l -b -q \
//     'PlottingScripts/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C'
//
//   root -l -b -q \
//     'PlottingScripts/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C("12-01-2026","27-03-2026",10)'
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
#include "TString.h"
#include "TStyle.h"
#include "TSystem.h"
#include "TSystemDirectory.h"
#include "TSystemFile.h"
#include "TLatex.h"

namespace {

enum class SampleKind {
  Unknown,
  Independent,
  Combined
};

struct SpeciesDef {
  TString label;
  std::vector<TString> histCandidates;
  double scaleFactor;
};

struct YieldStats {
  double mean = 0.0;
  double sem = 0.0;
  int nLoaded = 0;
};

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
  TString level2 = gSystem->DirName(level1.Data());   // PlottingScripts
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
  TString outDir = GetHadronizationBaseDir() + "/PlottingScripts/FinalAnalysis/Plots";
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
  gStyle->SetPadBottomMargin(0.14);
  gStyle->SetPadLeftMargin(0.12);
  gStyle->SetPadRightMargin(0.22);
  gStyle->SetPadTopMargin(0.08);
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

TH2* GetFirstMatchingTH2(TFile* file, const std::vector<TString>& names)
{
  if (!file) return nullptr;

  for (const TString& name : names) {
    TH2* h = dynamic_cast<TH2*>(file->Get(name));
    if (h) return h;
  }

  return nullptr;
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

    TH1* hMult = dynamic_cast<TH1*>(inputFile->Get("fHistMultiplicity"));
    TH2* hSpecies = GetFirstMatchingTH2(inputFile, species.histCandidates);

    if (!hMult || !hSpecies) {
      std::cerr << "Warning: missing required histograms in " << filePath
                << " for " << species.label << "\n";
      inputFile->Close();
      delete inputFile;
      continue;
    }

    const double nEvents = hMult->Integral(1, hMult->GetNbinsX());
    const double speciesCount = hSpecies->Integral(1, hSpecies->GetNbinsX(),
                                                   1, hSpecies->GetNbinsY());

    if (nEvents <= 0.0) {
      inputFile->Close();
      delete inputFile;
      continue;
    }

    const double yield = species.scaleFactor * speciesCount / nEvents;
    subYields.push_back(yield);
    totalSpecies += species.scaleFactor * speciesCount;
    totalEvents += nEvents;
    stats.nLoaded++;

    inputFile->Close();
    delete inputFile;
  }

  if (stats.nLoaded == 0 || totalEvents <= 0.0) return stats;

  stats.mean = totalSpecies / totalEvents;

  if (subYields.size() > 1) {
    double avg = 0.0;
    for (double y : subYields) avg += y;
    avg /= static_cast<double>(subYields.size());

    double var = 0.0;
    for (double y : subYields) var += (y - avg) * (y - avg);
    stats.sem = std::sqrt(var / (subYields.size() * (subYields.size() - 1)));
  } else {
    stats.sem = 0.0;
  }

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
    const double x = static_cast<double>(i + 1) + xShift;
    graph->SetPoint(i, x, stats.mean);
    graph->SetPointError(i, xError, stats.sem);
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
    {"B^{#pm}",                              {"fHistPtBplus"},        1.0},
    {"B^{0}/#bar{B}^{0}",                    {"fHistPtBzero"},        1.0},
    {"#Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0}",{"fHistPtLambdab"},      1.0}
  };
}

std::vector<SpeciesDef> CharmSpecies()
{
  return {
    {"D^{#pm}",                              {"fHistPtDplus"},                        1.0},
    {"D^{0}/#bar{D}^{0}",                    {"fHistPtDzero"},                        1.0},
    {"#Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-}",{"fHistPtLambdac", "fHistPtLambdacPlus"},1.0}
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

  TCanvas* canvas = new TCanvas(Form("cYield_%s_%s", flavour.Data(), tune.Data()),
                                Form("%s %s yields", flavour.Data(), tune.Data()),
                                1100, 700);
  canvas->SetTicks(1, 1);
  canvas->SetLogy();

  frame->SetTitle("");
  frame->GetXaxis()->SetTitle("Particle species");
  frame->GetYaxis()->SetTitle("Per-event yield");
  frame->GetXaxis()->SetTitleOffset(1.15);
  frame->GetYaxis()->SetTitleOffset(1.25);
  frame->GetYaxis()->SetRangeUser(yMin, yMax);
  frame->LabelsOption("h", "X");
  frame->Draw();

  gIndependent->Draw("P SAME");
  gCombined->Draw("P SAME");

  TLegend* legend = new TLegend(0.80, 0.73, 0.98, 0.86);
  legend->SetFillStyle(1001);
  legend->SetFillColor(kWhite);
  legend->SetBorderSize(1);
  legend->SetTextSize(0.030);
  legend->AddEntry(gIndependent, "Independent Sample", "pe");
  legend->AddEntry(gCombined, "Combined Sample", "pe");
  legend->Draw();

  TLatex latex;
  latex.SetNDC();
  latex.SetTextAlign(22);
  latex.SetTextSize(0.045);
  const double titleX = 0.5 * (canvas->GetLeftMargin() + 1.0 - canvas->GetRightMargin());
  latex.DrawLatex(titleX, 0.955,
                  Form("%s %s Per-Event Yields", flavour.Data(), tune.Data()));

  const TString outBase = Form("%s/SelectedParticleYields_%s_%s_%s_vs_%s",
                               GetOutputDir().Data(),
                               flavour.Data(),
                               tune.Data(),
                               independentTag.Data(),
                               combinedTag.Data());
  SaveCanvas(canvas, outBase);

  delete legend;
  delete canvas;
  delete frame;
  delete gIndependent;
  delete gCombined;
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
