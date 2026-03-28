// ---------------------------------------------------------------------------
// Plot_MultiplicityDistributions_TwoSamples.C
//
// Compare multiplicity distributions between two analyzed-data samples.
//
// By default, this macro compares:
//   - AnalyzedData/12-01-2026
//   - AnalyzedData/27-03-2026
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
#include <fstream>
#include <iostream>
#include <vector>

#include "TCanvas.h"
#include "TFile.h"
#include "TH1D.h"
#include "TLegend.h"
#include "TString.h"
#include "TStyle.h"
#include "TSystem.h"
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
  legend->AddEntry(hA, "Independent Sample", "l");
  legend->AddEntry(hB, "Combined Sample", "l");
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

void Plot_MultiplicityDistributions_TwoSamples(const char* dateA = "12-01-2026",
                                               const char* dateB = "27-03-2026",
                                               int nSub = 10,
                                               bool normalize = true)
{
  SetStyle();

  DrawMultiplicityComparison(dateA, dateB, "Charm",  "MONASH",    nSub, normalize);
  DrawMultiplicityComparison(dateA, dateB, "Charm",  "JUNCTIONS", nSub, normalize);
  DrawMultiplicityComparison(dateA, dateB, "Beauty", "MONASH",    nSub, normalize);
  DrawMultiplicityComparison(dateA, dateB, "Beauty", "JUNCTIONS", nSub, normalize);

  std::cout << "Wrote multiplicity comparison plots to:\n"
            << "  " << GetOutputDir() << "\n";
}

void runFinalMultiplicityComparison(const char* dateA = "12-01-2026",
                                    const char* dateB = "27-03-2026",
                                    int nSub = 10,
                                    bool normalize = true)
{
  Plot_MultiplicityDistributions_TwoSamples(dateA, dateB, nSub, normalize);
}
