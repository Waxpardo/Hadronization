// ---------------------------------------------------------------------------
// Plot_MultiplicityDistributions_TwoSamples.C
//
// Compare multiplicity distributions between two analyzed-data samples.
//
// By default, this macro compares the two most recent dated folders in:
//   - AnalyzedData/<DD-MM-YYYY>
//
// and produces four plots:
//   - Charm MONASH
//   - Charm JUNCTIONS
//   - Beauty MONASH
//   - Beauty JUNCTIONS
//
// The macro automatically supports both naming schemes:
//   Legacy split sample:
//     Charm  -> ccbar_<TUNE>_sub<i>.root
//     Beauty -> bbbar_<TUNE>_sub<i>.root
//
//   Unified HF sample:
//     Charm  -> hf_<TUNE>_sub<i>.root
//     Beauty -> hf_<TUNE>_sub<i>.root
//
// Usage:
//   root -l -b -q 'PlottingScripts/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C'
//
//   root -l -b -q \
//     'PlottingScripts/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C("12-01-2026","27-03-2026",10,true)'
// ---------------------------------------------------------------------------

#include <algorithm>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <utility>
#include <vector>

#include "TCanvas.h"
#include "TFile.h"
#include "TH1D.h"
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

bool ResolveLastTwoAnalysisDates(TString& olderDate, TString& newerDate)
{
  const std::vector<TString> sortedDates = GetSortedAnalysisDates();
  if (sortedDates.size() < 2) return false;

  olderDate = sortedDates[sortedDates.size() - 2];
  newerDate = sortedDates[sortedDates.size() - 1];
  return true;
}

enum class SampleKind {
  Unknown,
  Independent,
  Combined
};

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

TString SampleKindLabel(SampleKind kind)
{
  switch (kind) {
    case SampleKind::Independent: return "Independent Sample";
    case SampleKind::Combined:    return "Combined Sample";
    default:                      return "Sample";
  }
}

TString GetOutputDir()
{
  TString outDir = GetHadronizationBaseDir() + "/PlottingScripts/FinalAnalysis/Plots";
  gSystem->mkdir(outDir, true);
  return outDir;
}

void SetStyle()
{
  gStyle->SetOptStat(0);
  gStyle->SetPadBottomMargin(0.12);
  gStyle->SetPadLeftMargin(0.12);
  gStyle->SetPadRightMargin(0.05);
  gStyle->SetPadTopMargin(0.08);
  gStyle->SetLegendBorderSize(0);
  gStyle->SetTitleSize(0.05, "XY");
  gStyle->SetLabelSize(0.042, "XY");
}

TString BuildSubsamplePath(const TString& dateTag,
                           const TString& flavour,
                           const TString& prefixStem,
                           int iSub)
{
  return Form("%s/%s/%s/%s%d.root",
              GetAnalyzedDataDir().Data(),
              dateTag.Data(),
              flavour.Data(),
              prefixStem.Data(),
              iSub);
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
    const TString probe = BuildSubsamplePath(dateTag, flavour, stem, 0);
    if (!gSystem->AccessPathName(probe.Data())) return stem;
  }

  return TString("");
}

TH1D* LoadSummedMultiplicity(const TString& dateTag,
                             const TString& flavour,
                             const TString& tune,
                             int nSub)
{
  const TString prefixStem = ResolvePrefixStem(dateTag, flavour, tune);
  if (prefixStem.IsNull()) {
    std::cerr << "Could not resolve file prefix for "
              << flavour << " " << tune << " in sample " << dateTag << ".\n";
    return nullptr;
  }

  TH1D* hSum = nullptr;
  int nLoaded = 0;

  for (int iSub = 0; iSub < nSub; ++iSub) {
    const TString filePath = BuildSubsamplePath(dateTag, flavour, prefixStem, iSub);
    if (gSystem->AccessPathName(filePath.Data())) {
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

    TH1D* hMult = dynamic_cast<TH1D*>(inputFile->Get("fHistMultiplicity"));
    if (!hMult) {
      std::cerr << "Warning: histogram fHistMultiplicity not found in "
                << filePath << "\n";
      inputFile->Close();
      delete inputFile;
      continue;
    }

    if (!hSum) {
      hSum = dynamic_cast<TH1D*>(hMult->Clone(
        Form("hMult_%s_%s_%s", dateTag.Data(), flavour.Data(), tune.Data())
      ));
      hSum->SetDirectory(nullptr);
      hSum->Reset("ICES");
    }

    hSum->Add(hMult);
    ++nLoaded;

    inputFile->Close();
    delete inputFile;
  }

  if (!hSum || nLoaded == 0) {
    delete hSum;
    std::cerr << "No multiplicity histograms were loaded for "
              << flavour << " " << tune << " in sample " << dateTag << ".\n";
    return nullptr;
  }

  return hSum;
}

void NormalizeToUnity(TH1D* h)
{
  if (!h) return;
  const double integral = h->Integral(1, h->GetNbinsX());
  if (integral > 0.0) h->Scale(1.0 / integral);
}

double FindPositiveMinimum(TH1D* h)
{
  if (!h) return 1.0e-6;

  double minPositive = 1.0e9;
  for (int iBin = 1; iBin <= h->GetNbinsX(); ++iBin) {
    const double value = h->GetBinContent(iBin);
    if (value > 0.0 && value < minPositive) minPositive = value;
  }

  return (minPositive < 1.0e9 ? minPositive : 1.0e-6);
}

void StyleHistogram(TH1D* h, Color_t color, Style_t lineStyle)
{
  if (!h) return;
  h->SetLineColor(color);
  h->SetMarkerColor(color);
  h->SetLineWidth(3);
  h->SetLineStyle(lineStyle);
  h->SetMarkerStyle(20);
  h->SetMarkerSize(0.0);
}

void SaveCanvas(TCanvas* canvas, const TString& outBase)
{
  canvas->SaveAs((outBase + ".png").Data());
  canvas->SaveAs((outBase + ".pdf").Data());
  canvas->SaveAs((outBase + ".C").Data());
}

void DrawMultiplicityComparison(const TString& dateA,
                                const TString& dateB,
                                const TString& sampleLabelA,
                                const TString& sampleLabelB,
                                const TString& flavour,
                                const TString& tune,
                                int nSub,
                                bool normalize)
{
  TH1D* hA = LoadSummedMultiplicity(dateA, flavour, tune, nSub);
  TH1D* hB = LoadSummedMultiplicity(dateB, flavour, tune, nSub);

  if (!hA || !hB) {
    delete hA;
    delete hB;
    return;
  }

  if (normalize) {
    NormalizeToUnity(hA);
    NormalizeToUnity(hB);
  }

  StyleHistogram(hA, kBlue + 1, 1);
  StyleHistogram(hB, kRed + 1, 1);

  const double yMax = 1.35 * std::max(hA->GetMaximum(), hB->GetMaximum());
  const double yMin = 0.5 * std::min(FindPositiveMinimum(hA), FindPositiveMinimum(hB));

  TCanvas* canvas = new TCanvas(
    Form("cMult_%s_%s", flavour.Data(), tune.Data()),
    Form("%s %s multiplicity comparison", flavour.Data(), tune.Data()),
    950, 700
  );
  canvas->SetLogy();
  canvas->SetTicks(1, 1);

  hA->SetTitle("");
  hA->GetXaxis()->SetTitle("N_{ch}");
  hA->GetYaxis()->SetTitle(normalize ? "Normalised events" : "Events");
  hA->GetXaxis()->SetTitleOffset(1.05);
  hA->GetYaxis()->SetTitleOffset(1.25);
  hA->GetYaxis()->SetRangeUser(yMin, yMax);
  hA->Draw("hist");
  hB->Draw("hist same");

  TLegend* legend = new TLegend(0.52, 0.70, 0.88, 0.84);
  legend->SetFillStyle(0);
  legend->SetTextSize(0.032);
  legend->AddEntry(hA, sampleLabelA.Data(), "l");
  legend->AddEntry(hB, sampleLabelB.Data(), "l");
  legend->Draw();

  TLatex latex;
  latex.SetNDC();
  latex.SetTextAlign(22);
  latex.SetTextSize(0.045);
  latex.DrawLatex(0.50, 0.955,
                  Form("%s %s Multiplicity Distribution", flavour.Data(), tune.Data()));

  const TString outDir = GetOutputDir();
  const TString outBase = Form(
    "%s/MultiplicityComparison_%s_%s_%s_vs_%s",
    outDir.Data(),
    flavour.Data(),
    tune.Data(),
    dateA.Data(),
    dateB.Data()
  );

  SaveCanvas(canvas, outBase);

  delete legend;
  delete canvas;
  delete hA;
  delete hB;
}

} // namespace

void Plot_MultiplicityDistributions_TwoSamples(const char* dateA = "",
                                               const char* dateB = "",
                                               int nSub = 10,
                                               bool normalize = true)
{
  SetStyle();

  TString resolvedDateA = dateA ? TString(dateA).Strip(TString::kBoth) : TString("");
  TString resolvedDateB = dateB ? TString(dateB).Strip(TString::kBoth) : TString("");

  if (resolvedDateA.IsNull() && resolvedDateB.IsNull()) {
    if (!ResolveLastTwoAnalysisDates(resolvedDateA, resolvedDateB)) {
      std::cerr << "Could not find at least two dated folders under "
                << GetAnalyzedDataDir() << "\n";
      return;
    }
  } else if (resolvedDateA.IsNull() || resolvedDateB.IsNull()) {
    std::cerr << "Provide either both date folders or no dates at all.\n";
    return;
  }

  const TString sampleLabelA = SampleKindLabel(DetectSampleKind(resolvedDateA));
  const TString sampleLabelB = SampleKindLabel(DetectSampleKind(resolvedDateB));

  std::cout << "Using analysis folders:\n"
            << "  " << resolvedDateA << " -> " << sampleLabelA << "\n"
            << "  " << resolvedDateB << " -> " << sampleLabelB << "\n";

  DrawMultiplicityComparison(resolvedDateA, resolvedDateB, sampleLabelA, sampleLabelB,
                             "Charm",  "MONASH",    nSub, normalize);
  DrawMultiplicityComparison(resolvedDateA, resolvedDateB, sampleLabelA, sampleLabelB,
                             "Charm",  "JUNCTIONS", nSub, normalize);
  DrawMultiplicityComparison(resolvedDateA, resolvedDateB, sampleLabelA, sampleLabelB,
                             "Beauty", "MONASH",    nSub, normalize);
  DrawMultiplicityComparison(resolvedDateA, resolvedDateB, sampleLabelA, sampleLabelB,
                             "Beauty", "JUNCTIONS", nSub, normalize);

  std::cout << "Wrote multiplicity comparison plots to:\n"
            << "  " << GetOutputDir() << "\n";
}

void runFinalMultiplicityComparison(const char* dateA = "",
                                    const char* dateB = "",
                                    int nSub = 10,
                                    bool normalize = true)
{
  Plot_MultiplicityDistributions_TwoSamples(dateA, dateB, nSub, normalize);
}
