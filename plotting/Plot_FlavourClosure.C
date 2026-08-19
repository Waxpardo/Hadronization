// Flavour-closure figure.
//
// This is the figure that answers "does your balance function close?".
//
// Panel (a): the compensating flavour decomposed by heavy-state category.
//   The sparse holds only associates inside the analysis acceptance, so these
//   bars sum to the VISIBLE fraction, not to 1. The exact full-phase-space
//   closure is read separately from hFlavourClosureSummary and printed on the
//   panel; the difference between the two is precisely the flavour that
//   escapes the acceptance. The ground-state set is one bar among several: a
//   labelled SUBSET of a sum that is known to close, not a separate
//   non-closing observable.
//
// Panel (b): the Delta-phi shape of the compensation, per category, so the
//   reader sees not only how much flavour each species class carries but where
//   it sits relative to the trigger.
//
// Inputs are the hFlavourClosure sparse and hFlavourClosureSummary histogram
// written by analysis/status_analysis_THnSparse_qq.C.
//
// The closure objects are written by the analysis into every pair file
// belonging to a given trigger, so any one of them is a valid input.
//
// Usage:
//   root -l -b -q 'plotting/Plot_FlavourClosure.C("<dir>/DplusDminus.root","Dplus")'

#include "TCanvas.h"
#include "TFile.h"
#include "TH1D.h"
#include "THnSparse.h"
#include "TLegend.h"
#include "TLatex.h"
#include "TStyle.h"
#include "TSystem.h"

#include <array>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

// Must match Hadronization::HeavyStateCategory.
const std::array<const char*, 6> kCategoryLabel = {
    "ground state (central)", "hidden heavy", "multiply heavy",
    "other non-central", "excluded vector", "excluded excited"};
const std::array<int, 6> kCategoryColour = {kBlack, kAzure + 2, kOrange + 7,
                                            kGreen + 2, kRed + 1, kMagenta + 2};

template <typename T>
T* GetOrThrow(TFile& file, const char* name) {
  auto* object = dynamic_cast<T*>(file.Get(name));
  if (!object) {
    throw std::runtime_error(std::string("missing object '") + name +
                             "' in " + file.GetName());
  }
  return object;
}

}  // namespace

int Plot_FlavourClosure(const char* pairFilePath, const char* triggerName,
                        const char* outputDir = "plotting/Plots/Closure") {
  gStyle->SetOptStat(0);
  gSystem->mkdir(outputDir, kTRUE);

  const std::string path = pairFilePath;
  TFile file(path.c_str(), "READ");
  if (file.IsZombie()) {
    std::cerr << "ERROR: cannot open " << path << "\n";
    return 2;
  }

  auto* closure = GetOrThrow<THnSparseD>(file, "hFlavourClosure");
  auto* summary = GetOrThrow<TH1D>(file, "hFlavourClosureSummary");

  const double triggers = summary->GetBinContent(1);
  const double fullPhaseSpace = summary->GetBinContent(2);
  const double inAcceptance = summary->GetBinContent(3);
  if (triggers <= 0.0) {
    std::cerr << "ERROR: no weighted triggers in " << path << "\n";
    return 2;
  }

  // The sum rule is exact. Refuse to draw a figure that would misrepresent it.
  const double closureFraction = fullPhaseSpace / triggers;
  if (std::abs(closureFraction - 1.0) > 1e-6) {
    std::cerr << "ERROR: closure sum rule is violated (" << closureFraction
              << "); refusing to draw.\n";
    return 3;
  }
  const double visible = inAcceptance / triggers;

  // ---- panel (a): closure decomposed by category --------------------------
  auto* byCategory = new TH1D("hClosureByCategory",
                              ";heavy-state category;compensating flavour "
                              "per trigger",
                              6, -0.5, 5.5);
  double summed = 0.0;
  for (int category = 0; category < 6; ++category) {
    closure->GetAxis(4)->SetRange(category + 1, category + 1);
    TH1D* projection = closure->Projection(0, "E");
    const double value = projection->Integral(
        0, projection->GetNbinsX() + 1) / triggers;
    byCategory->SetBinContent(category + 1, value);
    byCategory->GetXaxis()->SetBinLabel(category + 1,
                                        kCategoryLabel[category]);
    summed += value;
    delete projection;
  }
  closure->GetAxis(4)->SetRange();
  byCategory->SetFillColor(kAzure - 9);
  byCategory->SetLineColor(kBlack);

  // ---- panel (b): Delta-phi shape per category ----------------------------
  auto* canvas = new TCanvas("cFlavourClosure", "flavour closure", 1200, 520);
  canvas->Divide(2, 1);

  canvas->cd(1);
  gPad->SetBottomMargin(0.22);
  gPad->SetGridy();
  byCategory->Draw("HIST");
  byCategory->GetXaxis()->LabelsOption("v");

  TLatex note;
  note.SetNDC();
  note.SetTextSize(0.032);
  note.DrawLatex(0.14, 0.93,
                 Form("#bf{%s} trigger", triggerName));
  note.DrawLatex(0.14, 0.88,
                 Form("closure (full phase space) = %.6f", closureFraction));
  note.DrawLatex(0.14, 0.83,
                 Form("visible in acceptance = %.3f", visible));
  note.DrawLatex(0.14, 0.78,
                 Form("categories sum to %.3f (= visible)", summed));
  // The category decomposition covers exactly the in-acceptance sum; any
  // mismatch means a category was dropped from the axis.
  if (std::abs(summed - visible) > 1e-6) {
    std::cerr << "WARNING: category sum " << summed
              << " does not match the in-acceptance sum " << visible
              << "; a category may be missing from the axis range.\n";
  }

  canvas->cd(2);
  gPad->SetGridy();
  auto* legend = new TLegend(0.55, 0.62, 0.88, 0.88);
  legend->SetBorderSize(0);
  legend->SetFillStyle(0);
  bool first = true;
  for (int category = 0; category < 6; ++category) {
    closure->GetAxis(4)->SetRange(category + 1, category + 1);
    TH1D* shape = closure->Projection(0, "E");
    shape->SetName(Form("hClosureDPhi_%d", category));
    shape->SetDirectory(nullptr);
    shape->Scale(1.0 / triggers);
    shape->SetLineColor(kCategoryColour[category]);
    shape->SetLineWidth(2);
    shape->SetTitle(";#Delta#varphi (rad);compensating flavour per trigger");
    if (shape->Integral() != 0.0) {
      shape->Draw(first ? "HIST" : "HIST SAME");
      legend->AddEntry(shape, kCategoryLabel[category], "l");
      first = false;
    } else {
      delete shape;
    }
  }
  closure->GetAxis(4)->SetRange();
  legend->Draw();

  const std::string stem =
      std::string(outputDir) + "/FlavourClosure_" + triggerName;
  canvas->SaveAs((stem + ".pdf").c_str());
  canvas->SaveAs((stem + ".png").c_str());

  std::cout << "FLAVOUR_CLOSURE_FIGURE trigger=" << triggerName
            << " closure=" << closureFraction << " visible=" << visible
            << " categories_sum=" << summed << "\n";
  std::cout << "  wrote " << stem << ".{pdf,png}\n";
  return 0;
}
