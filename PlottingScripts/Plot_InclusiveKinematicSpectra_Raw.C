// ---------------------------------------------------------------------------
// Plot_InclusiveKinematicSpectra_Raw.C
//
// Draw inclusive single-particle kinematic spectra directly from the generated
// raw RootFiles/HF trees. This deliberately does not use hTrKinematics or
// hAsKinematics from the THnSparse pair files, because those objects are
// trigger/associate conditioned and are not inclusive particle spectra.
//
// Default usage from the Hadronization repository root:
//
//   root -l -b <<'ROOT'
//   .L PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C+
//   Plot_InclusiveKinematicSpectra_Raw("RootFiles/HF",
//                                      "PlottingScripts/Plots/KinematicSpectra",
//                                      true, true)
//   .q
//   ROOT
// ---------------------------------------------------------------------------

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "TCanvas.h"
#include "TChain.h"
#include "TFile.h"
#include "TAxis.h"
#include "TH1D.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TLine.h"
#include "TPad.h"
#include "TString.h"
#include "TStyle.h"
#include "TSystem.h"

#include "HistogramErrorUtils.h"
#include "TunePlotStyle.h"

namespace InclusiveRawKinematics {

constexpr double kMultiplicityXMax = 170.0;
constexpr double kMultiplicityRatioYMin = 0.0;
constexpr double kMultiplicityRatioYMax = 4.0;
constexpr int kSharedMultiplicityLineStyle = 1;

struct MultiplicityPercentileClass {
  double minPercentile;
  double maxPercentile;
  const char* label;
};

struct SpeciesDef {
  std::string key;
  std::string label;
  int pdg = 0;
  bool logPt = true;
};

struct HistSet {
  TH1D* pt = nullptr;
  TH1D* eta = nullptr;
  TH1D* phi = nullptr;
};

struct TuneData {
  std::string tune;
  int nFiles = 0;
  Long64_t nEvents = 0;
  std::map<std::string, HistSet> spectra;
  TH1D* multiplicity = nullptr;
};

std::string JoinPath(const std::vector<std::string>& pieces)
{
  std::string path;
  for (const auto& piece : pieces) {
    if (piece.empty()) continue;
    if (!path.empty() && path.back() != '/') path += "/";
    if (!path.empty() && piece.front() == '/') path += piece.substr(1);
    else path += piece;
  }
  return path;
}

bool IsAbsolutePath(const std::string& path)
{
  return !path.empty() && path.front() == '/';
}

std::string ExpandPath(const std::string& path)
{
  char* expanded = gSystem->ExpandPathName(path.c_str());
  std::string result = expanded ? expanded : path;
  delete[] expanded;
  return result;
}

std::string FindHadronizationBase()
{
  const char* envBase = std::getenv("HADRONIZATION_BASE");
  if (envBase && !gSystem->AccessPathName(JoinPath({envBase, "PlottingScripts"}).c_str())) {
    return ExpandPath(envBase);
  }

  std::string current = ExpandPath(gSystem->WorkingDirectory());
  while (!current.empty() && current != "/") {
    if (!gSystem->AccessPathName(JoinPath({current, "PlottingScripts"}).c_str())) {
      return current;
    }
    const size_t slash = current.find_last_of('/');
    if (slash == std::string::npos || slash == 0) break;
    current = current.substr(0, slash);
  }

  return ExpandPath(gSystem->WorkingDirectory());
}

std::string ResolveFromBase(const std::string& path, const std::string& base)
{
  if (path.empty()) return path;
  const std::string expanded = ExpandPath(path);
  if (IsAbsolutePath(expanded)) return expanded;
  return JoinPath({base, expanded});
}

bool IsDirectory(const std::string& path)
{
  void* dir = gSystem->OpenDirectory(path.c_str());
  if (!dir) return false;
  gSystem->FreeDirectory(dir);
  return true;
}

void CollectRootFiles(const std::string& path, std::vector<std::string>& files)
{
  if (IsDirectory(path)) {
    void* dir = gSystem->OpenDirectory(path.c_str());
    if (!dir) return;

    const char* entry = nullptr;
    while ((entry = gSystem->GetDirEntry(dir))) {
      const std::string name(entry);
      if (name == "." || name == "..") continue;

      const std::string child = JoinPath({path, name});
      if (IsDirectory(child)) CollectRootFiles(child, files);
      else if (name.size() >= 5 && name.substr(name.size() - 5) == ".root") files.push_back(child);
    }

    gSystem->FreeDirectory(dir);
    return;
  }

  if (path.size() >= 5 && path.substr(path.size() - 5) == ".root") files.push_back(path);
}

void EnsureDirectory(const std::string& path)
{
  if (gSystem->mkdir(path.c_str(), true) != 0 && gSystem->AccessPathName(path.c_str())) {
    throw std::runtime_error("Could not create output directory: " + path);
  }
}

double Pi()
{
  return std::acos(-1.0);
}

double WrapToMinusPiPi(double phi)
{
  const double pi = Pi();
  const double twoPi = 2.0 * pi;
  while (phi < -pi) phi += twoPi;
  while (phi >= pi) phi -= twoPi;
  return phi;
}

std::vector<std::string> TuneNames()
{
  return {"MONASH", "JUNCTIONS", "CLOSEPACKING"};
}

std::vector<SpeciesDef> Species()
{
  return {
    {"Bplus", "#it{B}^{+}", 521, true},
    {"Bminus", "#it{B}^{-}", -521, true},
    {"Lambdab", "#Lambda_{b}^{0}", 5122, true},
    {"Lambdabbar", "#bar{#Lambda}_{b}^{0}", -5122, true},
    {"Sigmabzero", "#Sigma_{b}^{0}", 5212, true},
    {"Sigmabzerobar", "#bar{#Sigma}_{b}^{0}", -5212, true},
    {"Dplus", "#it{D}^{+}", 411, true},
    {"Dminus", "#it{D}^{-}", -411, true},
    {"Lambdacplus", "#Lambda_{c}^{+}", 4122, true},
    {"Lambdacplusbar", "#bar{#Lambda}_{c}^{-}", -4122, true},
  };
}

Color_t TuneColor(const std::string& tune)
{
  return HadronizationPlotStyle::TuneColor(tune);
}

int TuneMarker(const std::string& tune)
{
  return HadronizationPlotStyle::TuneMarker(tune);
}

int TuneLineStyle(const std::string& tune)
{
  return HadronizationPlotStyle::TuneLineStyle(tune);
}

const char* MultiplicityDefinitionLine1()
{
  return "pp, #sqrt{s} = 14 TeV";
}

const char* MultiplicityDefinitionLine2()
{
  return "#it{p}_{T} #geq 0.15 GeV/#it{c}";
}

const char* MultiplicityDefinitionLine3()
{
  return "|#eta| #leq 4";
}

const char* MultiplicityAxisTitle()
{
  return "Multiplicity #it{N}_{ch}";
}

const char* MultiplicitySpectrumYTitle(bool normalizeShape)
{
  return normalizeShape ? "Normalized event counts" : "Event counts / bin width";
}

std::vector<MultiplicityPercentileClass> MultiplicityPercentileClasses()
{
  return {
    {90.0, 100.0, "90-100%"},
    {80.0, 90.0, "80-90%"},
    {70.0, 80.0, "70-80%"},
    {60.0, 70.0, "60-70%"},
    {50.0, 60.0, "50-60%"},
    {40.0, 50.0, "40-50%"},
    {30.0, 40.0, "30-40%"},
    {20.0, 30.0, "20-30%"},
    {10.0, 20.0, "10-20%"},
    {1.0, 10.0, "1-10%"},
    {0.0, 1.0, "0-1%"},
  };
}

HistSet BookSpeciesHistograms(const SpeciesDef& species, const std::string& tune)
{
  const std::string prefix = "hInclusive_" + species.key + "_" + tune;
  HistSet hists;
  hists.pt = new TH1D((prefix + "_pT").c_str(), "", 100, 0.0, 50.0);
  hists.eta = new TH1D((prefix + "_eta").c_str(), "", 100, -4.0, 4.0);
  hists.phi = new TH1D((prefix + "_phi").c_str(), "", 100, -Pi(), Pi());

  for (TH1D* hist : {hists.pt, hists.eta, hists.phi}) {
    hist->SetDirectory(nullptr);
    hist->Sumw2();
  }

  return hists;
}

void DeleteHistSet(HistSet& hists)
{
  delete hists.pt;
  delete hists.eta;
  delete hists.phi;
  hists.pt = nullptr;
  hists.eta = nullptr;
  hists.phi = nullptr;
}

void AddMultiplicityHistogram(TuneData& data, const std::string& filePath)
{
  std::unique_ptr<TFile> file(TFile::Open(filePath.c_str(), "READ"));
  if (!file || file->IsZombie()) return;

  TH1D* source = dynamic_cast<TH1D*>(file->Get("hMULTIPLICITY"));
  if (!source) return;

  if (!data.multiplicity) {
    data.multiplicity = dynamic_cast<TH1D*>(source->Clone(("hMultiplicity_" + data.tune).c_str()));
    data.multiplicity->SetDirectory(nullptr);
    data.multiplicity->Reset();
    if (data.multiplicity->GetSumw2N() == 0) data.multiplicity->Sumw2();
  }
  data.multiplicity->Add(source);
}

TuneData BuildTuneSpectra(const std::string& tune,
                          const std::string& inputBaseDir,
                          bool strictInputs)
{
  const std::string tuneDir = JoinPath({inputBaseDir, tune});
  std::vector<std::string> files;
  CollectRootFiles(tuneDir, files);
  std::sort(files.begin(), files.end());

  if (files.empty()) {
    const std::string message = "No raw ROOT files found for tune " + tune + " in " + tuneDir;
    if (strictInputs) throw std::runtime_error(message);
    std::cerr << "WARNING: " << message << std::endl;
  }

  TuneData data;
  data.tune = tune;
  data.nFiles = static_cast<int>(files.size());

  const std::vector<SpeciesDef> speciesDefs = Species();
  std::map<int, std::string> speciesByPdg;
  for (const SpeciesDef& species : speciesDefs) {
    speciesByPdg[species.pdg] = species.key;
    data.spectra[species.key] = BookSpeciesHistograms(species, tune);
  }

  TChain chain("tree");
  for (const std::string& file : files) {
    chain.Add(file.c_str());
    AddMultiplicityHistogram(data, file);
  }

  if (files.empty()) return data;

  if (!chain.GetBranch("ID") || !chain.GetBranch("PT") ||
      !chain.GetBranch("ETA") || !chain.GetBranch("PHI")) {
    throw std::runtime_error("Raw tree for " + tune + " is missing one of ID, PT, ETA, or PHI");
  }

  std::vector<Int_t>* id = nullptr;
  std::vector<Double_t>* pt = nullptr;
  std::vector<Double_t>* eta = nullptr;
  std::vector<Double_t>* phi = nullptr;

  chain.SetBranchStatus("*", 0);
  chain.SetBranchStatus("ID", 1);
  chain.SetBranchStatus("PT", 1);
  chain.SetBranchStatus("ETA", 1);
  chain.SetBranchStatus("PHI", 1);
  chain.SetBranchAddress("ID", &id);
  chain.SetBranchAddress("PT", &pt);
  chain.SetBranchAddress("ETA", &eta);
  chain.SetBranchAddress("PHI", &phi);

  const Long64_t nEntries = chain.GetEntries();
  data.nEvents = nEntries;

  for (Long64_t entry = 0; entry < nEntries; ++entry) {
    if ((entry + 1) % 5000000 == 0) {
      std::cout << tune << ": processed " << (entry + 1) << " / " << nEntries << " events\r" << std::flush;
    }

    chain.GetEntry(entry);
    if (!id || !pt || !eta || !phi) continue;

    const size_t n = id->size();
    if (pt->size() != n || eta->size() != n || phi->size() != n) continue;

    for (size_t i = 0; i < n; ++i) {
      const auto found = speciesByPdg.find(id->at(i));
      if (found == speciesByPdg.end()) continue;

      HistSet& hists = data.spectra[found->second];
      hists.pt->Fill(pt->at(i));
      hists.eta->Fill(eta->at(i));
      hists.phi->Fill(WrapToMinusPiPi(phi->at(i)));
    }
  }
  if (nEntries >= 5000000) std::cout << std::string(80, ' ') << "\r" << std::flush;

  return data;
}

TuneData BuildTuneMultiplicityOnly(const std::string& tune,
                                   const std::string& inputBaseDir,
                                   bool strictInputs)
{
  const std::string tuneDir = JoinPath({inputBaseDir, tune});
  std::vector<std::string> files;
  CollectRootFiles(tuneDir, files);
  std::sort(files.begin(), files.end());

  if (files.empty()) {
    const std::string message = "No raw ROOT files found for tune " + tune + " in " + tuneDir;
    if (strictInputs) throw std::runtime_error(message);
    std::cerr << "WARNING: " << message << std::endl;
  }

  TuneData data;
  data.tune = tune;
  data.nFiles = static_cast<int>(files.size());

  for (const std::string& file : files) AddMultiplicityHistogram(data, file);
  data.nEvents = data.multiplicity
                   ? static_cast<Long64_t>(std::llround(data.multiplicity->GetEntries()))
                   : 0;

  return data;
}

void NormalizeShape(TH1D* hist)
{
  if (!hist) return;
  PlotErrorUtils::NormalizeToUnitShape(hist);
}

void ApplyBinWidthNormalization(TH1D* hist)
{
  if (!hist) return;
  if (hist->GetSumw2N() == 0) hist->Sumw2();
  for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
    const double width = hist->GetBinWidth(bin);
    if (width <= 0.0) continue;
    hist->SetBinContent(bin, hist->GetBinContent(bin) / width);
    hist->SetBinError(bin, hist->GetBinError(bin) / width);
  }
}

TH1D* CloneForPlot(TH1D* source,
                   const std::string& name,
                   const std::string& tune,
                   const std::string& xTitle,
                   bool normalizeShape)
{
  if (!source) return nullptr;
  TH1D* hist = dynamic_cast<TH1D*>(source->Clone(name.c_str()));
  if (!hist) return nullptr;
  hist->SetDirectory(nullptr);
  hist->SetStats(0);
  hist->SetTitle("");
  hist->SetLineColor(TuneColor(tune));
  hist->SetMarkerColor(TuneColor(tune));
  hist->SetMarkerStyle(TuneMarker(tune));
  hist->SetLineStyle(TuneLineStyle(tune));
  hist->SetLineWidth(2);
  hist->SetMarkerSize(0.9);
  hist->GetXaxis()->SetTitle(xTitle.c_str());
  hist->GetYaxis()->SetTitle(normalizeShape ? "Normalized entries" : "Counts / bin width");
  hist->GetXaxis()->SetTitleOffset(1.08);
  hist->GetYaxis()->SetTitleOffset(1.52);
  hist->GetXaxis()->SetTitleSize(0.045);
  hist->GetYaxis()->SetTitleSize(0.045);
  hist->GetXaxis()->SetLabelSize(0.040);
  hist->GetYaxis()->SetLabelSize(0.040);

  if (normalizeShape) NormalizeShape(hist);
  else ApplyBinWidthNormalization(hist);

  return hist;
}

TH1D* BuildRatioHistogram(TH1D* numerator,
                          TH1D* denominator,
                          const std::string& name,
                          const std::string& tune)
{
  if (!numerator || !denominator) return nullptr;

  TH1D* ratio = dynamic_cast<TH1D*>(numerator->Clone(name.c_str()));
  if (!ratio) return nullptr;
  ratio->SetDirectory(nullptr);
  ratio->Reset();
  ratio->SetStats(0);
  ratio->SetTitle("");
  ratio->SetLineColor(TuneColor(tune));
  ratio->SetMarkerColor(TuneColor(tune));
  ratio->SetMarkerStyle(TuneMarker(tune));
  ratio->SetLineStyle(TuneLineStyle(tune));
  ratio->SetLineWidth(2);
  ratio->SetMarkerSize(0.75);
  ratio->GetXaxis()->SetTitle(MultiplicityAxisTitle());
  ratio->GetYaxis()->SetTitle("Tune / MONASH");
  ratio->GetXaxis()->SetRangeUser(0.0, kMultiplicityXMax);

  const int nBins = std::min(numerator->GetNbinsX(), denominator->GetNbinsX());
  for (int bin = 1; bin <= nBins; ++bin) {
    const double num = numerator->GetBinContent(bin);
    const double den = denominator->GetBinContent(bin);
    if (num <= 0.0 || den <= 0.0) continue;

    const double value = num / den;
    const double numErr = numerator->GetBinError(bin);
    const double denErr = denominator->GetBinError(bin);
    const double relErr2 =
      (numErr > 0.0 ? (numErr / num) * (numErr / num) : 0.0) +
      (denErr > 0.0 ? (denErr / den) * (denErr / den) : 0.0);
    ratio->SetBinContent(bin, value);
    ratio->SetBinError(bin, value * std::sqrt(relErr2));
  }

  return ratio;
}

double MaximumWithErrors(const std::vector<TH1D*>& hists)
{
  double maximum = 0.0;
  for (TH1D* hist : hists) {
    if (!hist) continue;
    for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
      maximum = std::max(maximum, hist->GetBinContent(bin) + hist->GetBinError(bin));
    }
  }
  return maximum > 0.0 ? maximum : 1.0;
}

double PositiveMinimum(const std::vector<TH1D*>& hists)
{
  double minimum = 1.0e30;
  for (TH1D* hist : hists) {
    if (!hist) continue;
    for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
      const double content = hist->GetBinContent(bin);
      if (content > 0.0 && content < minimum) minimum = content;
    }
  }
  return minimum < 1.0e30 ? minimum : 1.0e-12;
}

void ApplyMultiplicityAxisLabels(TH1D* hist, bool normalizeShape)
{
  if (!hist) return;
  hist->GetXaxis()->SetTitle(MultiplicityAxisTitle());
  hist->GetYaxis()->SetTitle(MultiplicitySpectrumYTitle(normalizeShape));
}

void ApplyPiLabels(TH1D* hist)
{
  if (!hist) return;
  TAxis* axis = hist->GetXaxis();
  axis->SetNdivisions(4, false);
  axis->ChangeLabel(1, -1, -1, -1, -1, -1, "-#pi");
  axis->ChangeLabel(2, -1, -1, -1, -1, -1, "-#pi/2");
  axis->ChangeLabel(3, -1, -1, -1, -1, -1, "0");
  axis->ChangeLabel(4, -1, -1, -1, -1, -1, "#pi/2");
  axis->ChangeLabel(5, -1, -1, -1, -1, -1, "#pi");
}

void DrawSimulationInfoBlock(double x, double y, double headerSize, double bodySize)
{
  TLatex text;
  text.SetNDC();
  text.SetTextAlign(13);
  text.SetTextFont(62);
  text.SetTextSize(headerSize);
  text.DrawLatex(x, y, "PYTHIA 8");

  text.SetTextFont(42);
  text.SetTextSize(bodySize);
  const double spacing = 0.043;
  text.DrawLatex(x, y - spacing, MultiplicityDefinitionLine1());
  text.DrawLatex(x, y - 2.0 * spacing, MultiplicityDefinitionLine2());
  text.DrawLatex(x, y - 3.0 * spacing, MultiplicityDefinitionLine3());
}

double CalculateMultiplicityThreshold(TH1D* hist, double percentile)
{
  if (!hist) return 1.0;

  const double total = hist->Integral(1, hist->GetNbinsX());
  if (total <= 0.0) return hist->GetBinCenter(1);

  const double target = ((100.0 - percentile) / 100.0) * total;
  double running = 0.0;
  for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
    running += hist->GetBinContent(bin);
    if (running >= target) return hist->GetBinCenter(bin);
  }

  return hist->GetBinCenter(hist->GetNbinsX());
}

std::map<double, double> MultiplicityThresholds(TH1D* hist)
{
  std::map<double, double> thresholds;
  for (double percentile : {0.0, 1.0, 10.0, 20.0, 30.0, 40.0, 50.0,
                            60.0, 70.0, 80.0, 90.0, 100.0}) {
    thresholds[percentile] = CalculateMultiplicityThreshold(hist, percentile);
  }
  return thresholds;
}

void DrawMonashPercentileInset(TH1D* monash,
                               const std::string& outputStem,
                               std::vector<TH1D*>& keepAlive,
                               bool normalizeShape)
{
  if (!monash) return;

  TPad* inset = new TPad(("pMonashPercentiles_" + outputStem).c_str(),
                         "MONASH multiplicity percentile boundaries",
                         0.18, 0.07, 0.58, 0.43);
  inset->SetFillColor(kWhite);
  inset->SetFillStyle(1001);
  inset->SetFrameFillColor(kWhite);
  inset->SetFrameLineWidth(1);
  inset->SetTicks(1, 1);
  inset->SetLogx();
  inset->SetLogy();
  inset->SetTopMargin(0.12);
  inset->SetBottomMargin(0.25);
  inset->SetLeftMargin(0.18);
  inset->SetRightMargin(0.065);
  inset->Draw();
  inset->cd();

  TH1D* insetHist = dynamic_cast<TH1D*>(monash->Clone(("hMonashPercentileInset_" + outputStem).c_str()));
  if (!insetHist) return;
  keepAlive.push_back(insetHist);
  insetHist->SetDirectory(nullptr);
  insetHist->SetStats(0);
  insetHist->SetTitle("");
  insetHist->SetLineColor(kBlack);
  insetHist->SetLineWidth(2);
  insetHist->SetMarkerSize(0.0);

  const double xMin = 1.0;
  const double xMax = kMultiplicityXMax;
  const double yMin = std::max(PositiveMinimum({insetHist}) * 0.5, 1.0e-10);
  const double yMax = std::max(insetHist->GetMaximum() * 3.0, yMin * 10.0);
  insetHist->SetMinimum(yMin);
  insetHist->SetMaximum(yMax);
  insetHist->GetXaxis()->SetRangeUser(xMin, xMax);
  insetHist->GetXaxis()->SetTitle(MultiplicityAxisTitle());
  insetHist->GetYaxis()->SetTitle(MultiplicitySpectrumYTitle(normalizeShape));
  insetHist->GetXaxis()->SetTitleSize(0.062);
  insetHist->GetXaxis()->SetTitleOffset(1.02);
  insetHist->GetYaxis()->SetTitleSize(0.060);
  insetHist->GetYaxis()->SetTitleOffset(1.05);
  insetHist->GetXaxis()->SetLabelSize(0.055);
  insetHist->GetYaxis()->SetLabelSize(0.055);
  insetHist->GetYaxis()->SetNdivisions(503);
  insetHist->Draw("HIST");

  const auto thresholds = MultiplicityThresholds(insetHist);
  for (const auto& item : thresholds) {
    const double x = item.second;
    if (x < xMin || x > xMax) continue;
    TLine* line = new TLine(x, yMin, x, yMax);
    line->SetLineColor(kGray + 2);
    line->SetLineStyle(2);
    line->SetLineWidth(1);
    line->Draw("same");
  }
  insetHist->Draw("HIST SAME");

  TLatex label;
  label.SetTextFont(42);
  label.SetTextSize(0.044);
  label.SetTextAlign(22);
  label.SetTextAngle(90);
  const double yLabel = yMin * std::pow(yMax / yMin, 0.34);
  for (const auto& activityClass : MultiplicityPercentileClasses()) {
    const double left = thresholds.count(activityClass.maxPercentile) ? thresholds.at(activityClass.maxPercentile) : xMin;
    const double right = thresholds.count(activityClass.minPercentile) ? thresholds.at(activityClass.minPercentile) : xMax;
    if (right < xMin || left > xMax) continue;
    const double xLabel = std::sqrt(std::max(left, xMin) * std::min(right, xMax));
    label.DrawLatex(xLabel, yLabel, activityClass.label);
  }

  TLatex title;
  title.SetNDC();
  title.SetTextFont(62);
  title.SetTextSize(0.054);
  title.SetTextAlign(13);
  title.DrawLatex(0.02, 0.965, "MONASH percentile boundaries");
  inset->RedrawAxis();
}

void DrawMultiplicityOverlayWithRatio(const std::vector<TH1D*>& hists,
                                      const std::vector<std::string>& tunes,
                                      const std::string& outputDir,
                                      const std::string& outputStem,
                                      bool normalizeShape,
                                      bool logY)
{
  (void)normalizeShape;

  TCanvas* canvas = new TCanvas(("c_" + outputStem).c_str(), outputStem.c_str(), 1800, 1650);

  TPad* mainPad = new TPad(("pMain_" + outputStem).c_str(), "multiplicity spectrum", 0.0, 0.31, 1.0, 1.0);
  mainPad->SetTicks(1, 1);
  mainPad->SetLeftMargin(0.16);
  mainPad->SetRightMargin(0.045);
  mainPad->SetTopMargin(0.12);
  mainPad->SetBottomMargin(0.025);
  if (logY) mainPad->SetLogy();
  mainPad->Draw();

  TPad* ratioPad = new TPad(("pRatio_" + outputStem).c_str(), "tune ratios", 0.0, 0.0, 1.0, 0.31);
  ratioPad->SetTicks(1, 1);
  ratioPad->SetLeftMargin(0.16);
  ratioPad->SetRightMargin(0.045);
  ratioPad->SetTopMargin(0.035);
  ratioPad->SetBottomMargin(0.34);
  ratioPad->Draw();

  mainPad->cd();
  TH1D* monash = nullptr;
  for (size_t i = 0; i < tunes.size(); ++i) {
    if (tunes[i] == "MONASH") {
      monash = hists[i];
      break;
    }
  }
  std::vector<TH1D*> insetKeepAlive;

  if (!hists.empty()) {
    const double maxY = MaximumWithErrors(hists);
    const double minY = logY ? std::max(PositiveMinimum(hists) * 0.35, 1.0e-12) : 0.0;
    const double upper = logY ? maxY * 8.0 : maxY * 1.28;

    TLegend* legend = new TLegend(0.735, 0.685, 0.925, 0.815);
    legend->SetBorderSize(0);
    legend->SetFillStyle(0);
    legend->SetTextFont(42);
    legend->SetTextSize(0.034);

    for (size_t i = 0; i < hists.size(); ++i) {
      hists[i]->SetMinimum(minY);
      hists[i]->SetMaximum(std::max(upper, minY * 10.0));
      hists[i]->GetXaxis()->SetRangeUser(0.0, kMultiplicityXMax);
      hists[i]->GetXaxis()->SetLabelSize(0.0);
      hists[i]->GetXaxis()->SetTitleSize(0.0);
      hists[i]->SetLineStyle(kSharedMultiplicityLineStyle);
      hists[i]->Draw(i == 0 ? "E1 HIST" : "E1 HIST SAME");
      legend->AddEntry(hists[i], tunes[i].c_str(), "lp");
    }
    legend->Draw();
    DrawSimulationInfoBlock(0.57, 0.805, 0.032, 0.030);
    DrawMonashPercentileInset(monash, outputStem, insetKeepAlive, normalizeShape);
    mainPad->cd();

  } else {
    TLatex latex;
    latex.SetNDC();
    latex.SetTextAlign(22);
    latex.SetTextSize(0.04);
    latex.DrawLatex(0.50, 0.50, "No input histograms found");
  }

  ratioPad->cd();
  std::vector<TH1D*> ratios;

  for (size_t i = 0; i < tunes.size(); ++i) {
    if (tunes[i] == "MONASH") continue;
    TH1D* ratio = BuildRatioHistogram(hists[i], monash, "hRatio_" + outputStem + "_" + tunes[i], tunes[i]);
    if (ratio) ratios.push_back(ratio);
  }

  if (!ratios.empty()) {
    for (size_t i = 0; i < ratios.size(); ++i) {
      ratios[i]->SetMinimum(kMultiplicityRatioYMin);
      ratios[i]->SetMaximum(kMultiplicityRatioYMax);
      ratios[i]->GetXaxis()->SetTitleSize(0.105);
      ratios[i]->GetXaxis()->SetLabelSize(0.090);
      ratios[i]->GetXaxis()->SetTitleOffset(1.02);
      ratios[i]->GetYaxis()->SetTitleSize(0.090);
      ratios[i]->GetYaxis()->SetLabelSize(0.075);
      ratios[i]->GetYaxis()->SetTitleOffset(0.70);
      ratios[i]->GetYaxis()->SetNdivisions(505);
      ratios[i]->SetLineStyle(kSharedMultiplicityLineStyle);
      ratios[i]->Draw(i == 0 ? "E1 HIST" : "E1 HIST SAME");
    }

    TLine* unity = new TLine(0.0, 1.0, kMultiplicityXMax, 1.0);
    unity->SetLineColor(kGray + 2);
    unity->SetLineStyle(2);
    unity->SetLineWidth(1);
    unity->Draw("same");
    for (TH1D* ratio : ratios) ratio->Draw("E1 HIST SAME");
    ratioPad->RedrawAxis();
  }

  canvas->cd();
  const std::string outBase = JoinPath({outputDir, outputStem});
  canvas->SaveAs((outBase + ".png").c_str());
  canvas->SaveAs((outBase + ".pdf").c_str());
  canvas->SaveAs((outBase + ".C").c_str());

  delete canvas;
  for (TH1D* hist : insetKeepAlive) delete hist;
  for (TH1D* ratio : ratios) delete ratio;
}

void DrawOverlay(const std::vector<TuneData>& tuneData,
                 const SpeciesDef* species,
                 const std::string& variable,
                 const std::string& xTitle,
                 const std::string& outputDir,
                 const std::string& outputStem,
                 bool normalizeShape,
                 bool logY)
{
  std::vector<TH1D*> hists;
  std::vector<std::string> tunes;

  for (const TuneData& data : tuneData) {
    TH1D* source = nullptr;
    if (!species) {
      source = data.multiplicity;
    } else {
      const auto found = data.spectra.find(species->key);
      if (found == data.spectra.end()) continue;
      if (variable == "pT") source = found->second.pt;
      else if (variable == "eta") source = found->second.eta;
      else if (variable == "phi") source = found->second.phi;
    }

    TH1D* hist = CloneForPlot(source,
                              "hPlot_" + outputStem + "_" + data.tune,
                              data.tune,
                              xTitle,
                              normalizeShape);
    if (!hist) continue;
    if (variable == "phi") ApplyPiLabels(hist);
    hists.push_back(hist);
    tunes.push_back(data.tune);
  }

  EnsureDirectory(outputDir);

  const bool isMultiplicity = (!species && variable == "multiplicity");
  if (isMultiplicity) {
    for (TH1D* hist : hists) ApplyMultiplicityAxisLabels(hist, normalizeShape);
    DrawMultiplicityOverlayWithRatio(hists, tunes, outputDir, outputStem, normalizeShape, logY);
    for (TH1D* hist : hists) delete hist;
    return;
  }

  TCanvas* canvas = new TCanvas(("c_" + outputStem).c_str(), outputStem.c_str(), 860, 680);
  canvas->SetTicks(1, 1);
  canvas->SetLeftMargin(0.16);
  canvas->SetRightMargin(0.045);
  canvas->SetBottomMargin(0.14);
  canvas->SetTopMargin(0.13);
  if (logY) canvas->SetLogy();

  if (!hists.empty()) {
    const double maxY = MaximumWithErrors(hists);
    const double minY = logY ? std::max(PositiveMinimum(hists) * 0.35, 1.0e-12) : 0.0;
    const double upper = logY ? maxY * 8.0 : maxY * 1.28;

    TLegend* legend = new TLegend(0.62, 0.705, 0.91, 0.855);
    legend->SetBorderSize(0);
    legend->SetFillStyle(0);
    legend->SetTextSize(0.035);

    for (size_t i = 0; i < hists.size(); ++i) {
      hists[i]->SetMinimum(minY);
      hists[i]->SetMaximum(std::max(upper, minY * 10.0));
      hists[i]->Draw(i == 0 ? "E1 HIST" : "E1 HIST SAME");
      legend->AddEntry(hists[i], tunes[i].c_str(), "lp");
    }
    legend->Draw();

    TLatex title;
    title.SetNDC();
    title.SetTextAlign(13);
    title.SetTextSize(0.034);
    if (species) title.DrawLatex(0.16, 0.965, ("Inclusive generated " + species->label).c_str());
    else title.DrawLatex(0.16, 0.965, "Shared event multiplicity");
  } else {
    TLatex latex;
    latex.SetNDC();
    latex.SetTextAlign(22);
    latex.SetTextSize(0.04);
    latex.DrawLatex(0.50, 0.50, "No input histograms found");
  }

  const std::string outBase = JoinPath({outputDir, outputStem});
  canvas->SaveAs((outBase + ".png").c_str());
  canvas->SaveAs((outBase + ".pdf").c_str());
  canvas->SaveAs((outBase + ".C").c_str());

  delete canvas;
  for (TH1D* hist : hists) delete hist;
}

void SetPlotStyle()
{
  gStyle->SetOptStat(0);
  gStyle->SetTitleFont(42, "XYZ");
  gStyle->SetLabelFont(42, "XYZ");
  gStyle->SetTitleSize(0.045, "XYZ");
  gStyle->SetLabelSize(0.040, "XYZ");
  gStyle->SetLegendBorderSize(0);
  gStyle->SetErrorX(0.0);
}

void DeleteTuneData(std::vector<TuneData>& tuneData)
{
  for (TuneData& data : tuneData) {
    delete data.multiplicity;
    data.multiplicity = nullptr;
    for (auto& item : data.spectra) DeleteHistSet(item.second);
  }
}

} // namespace InclusiveRawKinematics

void Plot_InclusiveKinematicSpectra_Raw(const char* inputBaseDir = "RootFiles/HF",
                                        const char* outputDir = "PlottingScripts/Plots/KinematicSpectra",
                                        bool normalizeShape = true,
                                        bool strictInputs = true)
{
  using namespace InclusiveRawKinematics;

  SetPlotStyle();

  const std::string base = FindHadronizationBase();
  const std::string resolvedInput = ResolveFromBase(inputBaseDir ? inputBaseDir : "RootFiles/HF", base);
  const std::string resolvedOutput =
    ResolveFromBase(outputDir ? outputDir : "PlottingScripts/Plots/KinematicSpectra", base);
  const std::string suffix = normalizeShape ? "shape" : "density";

  std::cout << "Inclusive raw kinematic spectra\n";
  std::cout << "================================\n";
  std::cout << "Input base: " << resolvedInput << "\n";
  std::cout << "Output dir: " << resolvedOutput << "\n";
  std::cout << "Selection: exact PDG ID, stored final-state raw-tree particles, no pair conditioning\n";
  std::cout << "Raw producer acceptance already applied: pT >= 0.15 GeV/c and |eta| <= 4\n";
  std::cout << "Additional plotting cuts: none\n\n";

  std::vector<TuneData> tuneData;
  for (const std::string& tune : TuneNames()) {
    TuneData data = BuildTuneSpectra(tune, resolvedInput, strictInputs);
    std::cout << tune
              << ": files=" << data.nFiles
              << " tree entries=" << data.nEvents;
    if (data.multiplicity) {
      std::cout << " multiplicity entries=" << static_cast<Long64_t>(std::llround(data.multiplicity->GetEntries()));
    }
    std::cout << "\n";
    tuneData.push_back(data);
  }
  std::cout << "\n";

  DrawOverlay(tuneData,
              nullptr,
              "multiplicity",
              MultiplicityAxisTitle(),
              JoinPath({resolvedOutput, "Multiplicity"}),
              "MultiplicitySpectrum_Shared_" + suffix,
              normalizeShape,
              true);

  const std::vector<SpeciesDef> speciesDefs = Species();
  for (const SpeciesDef& species : speciesDefs) {
    DrawOverlay(tuneData,
                &species,
                "pT",
                "#it{p}_{T} (GeV/#it{c})",
                JoinPath({resolvedOutput, "Inclusive", "pT"}),
                "Inclusive_pT_" + species.key + "_" + suffix,
                normalizeShape,
                species.logPt);
    DrawOverlay(tuneData,
                &species,
                "eta",
                "#eta",
                JoinPath({resolvedOutput, "Inclusive", "eta"}),
                "Inclusive_eta_" + species.key + "_" + suffix,
                normalizeShape,
                false);
    DrawOverlay(tuneData,
                &species,
                "phi",
                "#phi",
                JoinPath({resolvedOutput, "Inclusive", "phi"}),
                "Inclusive_phi_" + species.key + "_" + suffix,
                normalizeShape,
                false);
  }

  DeleteTuneData(tuneData);
}

void Plot_InclusiveMultiplicitySpectrum_Raw(const char* inputBaseDir = "RootFiles/HF",
                                            const char* outputDir = "PlottingScripts/Plots/KinematicSpectra",
                                            bool normalizeShape = true,
                                            bool strictInputs = true)
{
  using namespace InclusiveRawKinematics;

  SetPlotStyle();

  const std::string base = FindHadronizationBase();
  const std::string resolvedInput = ResolveFromBase(inputBaseDir ? inputBaseDir : "RootFiles/HF", base);
  const std::string resolvedOutput =
    ResolveFromBase(outputDir ? outputDir : "PlottingScripts/Plots/KinematicSpectra", base);
  const std::string suffix = normalizeShape ? "shape" : "density";

  std::cout << "Inclusive raw multiplicity spectrum\n";
  std::cout << "===================================\n";
  std::cout << "Input base: " << resolvedInput << "\n";
  std::cout << "Output dir: " << resolvedOutput << "\n";
  std::cout << "Nch definition: prompt charged e/mu/pi/K/p, pT >= 0.15 GeV/c, |eta| <= 4, status 81-89\n";
  std::cout << "pp sqrt(s)=14 TeV\n\n";

  std::vector<TuneData> tuneData;
  for (const std::string& tune : TuneNames()) {
    TuneData data = BuildTuneMultiplicityOnly(tune, resolvedInput, strictInputs);
    std::cout << tune
              << ": files=" << data.nFiles
              << " multiplicity entries=" << data.nEvents
              << "\n";
    tuneData.push_back(data);
  }
  std::cout << "\n";

  DrawOverlay(tuneData,
              nullptr,
              "multiplicity",
              MultiplicityAxisTitle(),
              JoinPath({resolvedOutput, "Multiplicity"}),
              "MultiplicitySpectrum_Shared_" + suffix,
              normalizeShape,
              true);

  DeleteTuneData(tuneData);
}
