// combinedCanvasPlots
// ROOT macro that combines seperate plots onto one, with shared axes.
// This is done to split crowded plots and make them more readable.

// The script is not very flexible, but it is not intended this way, the plots are specifically
// used for my thesis.
// Changes can be made straightforwardly.

// The macro uses an automasation procedure to set up the histograms more directly.
// The histograms that we want to plot originate from charm (cc) and beauty (bb) productions,
// from different simulation settings (e.g. 214, 215), from different balancing pairs (e.g. B+B-, B+Lb, ...)
// and different multiplicity bins (e.g. all bins, 3 bins, 7 bins, ...).

// In order to draw everything in the most direct way, the histogram vectors are prepared in two steps:
// 1. In the first step we take the root files with all these different origins and add them together in a way which
// makes sense. The same-sign pairs (B+B+, D+D+, B+Lb0) are not physical (physical correlations come from quark-antiquark pairs)
// and are subtracted from like-sign pairs. In this script this is done in a later stage, as it is only necessary for
// balancing studies.
// Plotting options and names are given to this vector, though many are overwritten in later stages, hence they can be
// considered for removal. The names are useful for debugging, however.
// 2. The vectors originating from different correlations and multiplicity binnings are gathered together and
// put into one big vector. This big vector is given to the main plotting function and is looped over.
// A more direct procedure is used sometimes in this macro, where histograms are taken directly from the source root files.
// These steps can also be automised, but their application is very niche and automisation reduces the clarity of the code.

// Calculates the geometric mean of a pair x1 and x2
Double_t geometricMean(Double_t x1, Double_t x2) {
  return pow(x1*x2 , 0.5);
}

void setCanvasMargins(TCanvas *canvas, double_t LeftMargin, double_t RightMargin, double_t TopMargin, double_t BottomMargin) {
  canvas->SetLeftMargin(LeftMargin);
  canvas->SetRightMargin(RightMargin);
  canvas->SetTopMargin(TopMargin);
  canvas->SetBottomMargin(BottomMargin);
}

// Simple function that sets the axes and other configurations to draw DPhi correlations
// Sometimes the function settings are overwritten later, which is slightly messy, but can be improved if desired.
void histDPhiMakeUp(TH1D* hist, Color_t color, Double_t DrawYmin, Double_t DrawYmax) {
  hist->SetStats(0);
  hist->SetLineColor(color);
  hist->SetTitle("");
  hist->GetXaxis()->SetTitle("#Delta#phi (rad)");
  hist->GetXaxis()->SetTitleSize(0.05);
  hist->GetXaxis()->SetLabelSize(0.05);
  hist->GetYaxis()->SetTitle("#frac{1}{N_{trigger}} #frac{dN}{d#Delta#phi}");
  hist->GetYaxis()->SetTitleSize(0.05);
  hist->GetYaxis()->SetLabelSize(0.05);
  hist->GetYaxis()->SetRangeUser(DrawYmin, DrawYmax);
}

// The structs defined below are used to be consistent with other scripts I used, though
// most settings are overwritten later in this script.
// I would not worry too much about what happens here.
struct BaseLabels {
  const char* LegendTitle;
  Color_t Color;
  Int_t LineStyle;
  Int_t LineWidth;
};

struct RootFileAndLabels : public BaseLabels {
  const char* TriggerName;
  const char* AssociateNameOS;
  const char* AssociateNameSS;
  const char* OSRootFile;
  const char* SSRootFile;
  Double_t DrawYmin;
  Double_t DrawYmax;
};

struct HistNameAndLabels : public BaseLabels {
   const char* HistName;
   const char* TrPtName;
};

struct HistAndLabels : public BaseLabels {
  const char* TriggerName;
  const char* AssociateNameOS;
  const char* AssociateNameSS;
  TH1D* hDPhiOS;
  TH1D* hDPhiSS;
  Double_t DrawYmin;
  Double_t DrawYmax;
};

// Function to get bin number and bin content
std::pair<int, double> getBinInfo(TH1D* hist, double value) {
    // Find the bin number for the given value
    int binNumber = hist->FindBin(value);

    // Get the bin content
    double binContent = hist->GetBinContent(binNumber);

    return std::make_pair(binNumber, binContent);
}

// Function that plots the histograms in several ways after the input is given by the
// configureInput() function.
void HarryPlotter(std::vector<HistAndLabels> vhBpAs,
		  std::vector<HistAndLabels> vhBpAsMult,
		  std::vector<HistAndLabels> vhDpAs,
		  std::vector<HistAndLabels> vhDpAsMult,
		  bool write,
		  const char* writeName) {

  // Necessary to avoid overlapping of axes
  Double_t eps = 1e-3;

  TCanvas* c1x2_DPhi = new TCanvas("c1x2_Dphi", "DPhi for B+B- and D+D- on 1x2 canvas", 1600, 1200);
  setCanvasMargins(c1x2_DPhi, 0.15, 0.1, 0.1, 0.05);
  c1x2_DPhi->cd();
  TPad* c00_DPhi = new TPad("c00_DPhi", "DPhi for B+B-", 0.05, 0.10, 0.525, 0.95);
  c00_DPhi->SetLeftMargin(0.22);
  c00_DPhi->SetRightMargin(eps);
  c00_DPhi->Draw();
  TPad* c01_DPhi = new TPad("c01_DPhi", "DPhi for D+D-", 0.525+eps, 0.10, 0.95, 0.95);
  c01_DPhi->SetLeftMargin(0);
  c01_DPhi->Draw();

  TLegend* l00_DPhi = new TLegend(0.25, 0.75, 0.40, 0.8);
  l00_DPhi->SetTextSize(0.05);
  l00_DPhi->SetBorderSize(0);
  l00_DPhi->AddEntry("", "(a) B^{+}B^{-}", "");
  TLegend* l01_DPhi = new TLegend(0.25-0.15, 0.75, 0.40-0.15, 0.8);
  l01_DPhi->SetTextSize(0.05);
  l01_DPhi->SetBorderSize(0);
  l01_DPhi->AddEntry("", "(b) D^{+}D^{-}", "");

  TH1D* hBpBm = vhBpAs[0].hDPhiOS;
  histDPhiMakeUp(hBpBm, kRed, 0, 0.01);
  hBpBm->GetXaxis()->SetTitle("");
  hBpBm->GetYaxis()->SetNdivisions(5);
  // hBpBm->GetYaxis()->SetTitleOffset(3);
  c00_DPhi->cd();
  gPad->SetTicky();
  hBpBm->Draw("hist E");
  l00_DPhi->Draw();

  TH1D* hDpDm = vhDpAs[0].hDPhiOS;
  histDPhiMakeUp(hDpDm, kBlue, 0, 0.01);
  hDpDm->GetXaxis()->SetTitle("#Delta#phi (rad)");
  hDpDm->GetYaxis()->SetNdivisions(5);
  c01_DPhi->cd();
  hDpDm->Draw("hist E");
  l01_DPhi->Draw();

  if (write) {
    c1x2_DPhi->SaveAs(Form("Plots/c1x2_DPhi_%s.pdf", writeName));
    c1x2_DPhi->SaveAs(Form("Plots/c1x2_DPhi_%s.png", writeName));
  }

  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  // MULTIPLICITY DPHI STUDY
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  
  TCanvas* c2x3_DPhi_Mult = new TCanvas("c2x3_Dphi_Mult", "DPhi with multiplicity dependence for B+B- and D+D- on 2x3 canvas", 1200, 1000);
  setCanvasMargins(c2x3_DPhi_Mult, 0.15, 0.1, 0.1, 0.05);
  c2x3_DPhi_Mult->cd();
  TPad* c00_DPhi_Mult = new TPad("c00_DPhi_Mult", "DPhi as function of multiplicity for B+B-", 0.05, 0.50, 0.38, 0.95);
  c00_DPhi_Mult->SetLeftMargin(0.22);
  c00_DPhi_Mult->SetRightMargin(eps);
  c00_DPhi_Mult->SetBottomMargin(eps);
  c00_DPhi_Mult->Draw();
  TPad* c01_DPhi_Mult = new TPad("c01_DPhi_Mult", "DPhi as function of multiplicity for B+B-", 0.38+eps, 0.50, 0.65, 0.95);
  c01_DPhi_Mult->SetLeftMargin(0);
  c01_DPhi_Mult->SetRightMargin(eps);
  c01_DPhi_Mult->SetBottomMargin(eps);
  c01_DPhi_Mult->Draw();
  TPad* c02_DPhi_Mult = new TPad("c02_DPhi_Mult", "DPhi as function of multiplicity for B+B-", 0.65+eps, 0.50, 0.95, 0.95);
  c02_DPhi_Mult->SetLeftMargin(0);
  c02_DPhi_Mult->SetBottomMargin(eps);
  c02_DPhi_Mult->Draw();
  TPad* c10_DPhi_Mult = new TPad("c10_DPhi_Mult", "DPhi as function of multiplicity for D+D-", 0.05, 0.05, 0.38, 0.50+eps);
  c10_DPhi_Mult->SetLeftMargin(0.22);
  c10_DPhi_Mult->SetRightMargin(eps);
  c10_DPhi_Mult->SetTopMargin(0);
  c10_DPhi_Mult->Draw();
  TPad* c11_DPhi_Mult = new TPad("c11_DPhi_Mult", "DPhi as function of multiplicity for D+D-", 0.38+eps, 0.05, 0.65, 0.50+eps);
  c11_DPhi_Mult->SetLeftMargin(0);
  c11_DPhi_Mult->SetRightMargin(eps);
  c11_DPhi_Mult->SetTopMargin(0);
  c11_DPhi_Mult->Draw();
  TPad* c12_DPhi_Mult = new TPad("c12_DPhi_Mult", "DPhi as function of multiplicity for D+D-", 0.65+eps, 0.05, 0.95, 0.50+eps);
  c12_DPhi_Mult->SetLeftMargin(0);
  c12_DPhi_Mult->SetTopMargin(0);
  c12_DPhi_Mult->Draw();

  // Needs to be defined before the legends in order to add the histograms to the entries
  // Normally this would be achieved with a template histogram
  // Use the i+7*x structure to find associate x
  TH1D* hBpBmMult80_100 = vhBpAsMult[0].hDPhiOS;
  histDPhiMakeUp(hBpBmMult80_100, kRed, 0, 0.02);
  hBpBmMult80_100->SetMinimum(1e-4);
  hBpBmMult80_100->GetXaxis()->SetTitle("");
  hBpBmMult80_100->GetYaxis()->SetNdivisions(5);
  // hBpBmMult80_100->GetYaxis()->SetTitleOffset(3);
  c00_DPhi_Mult->cd();
  gPad->SetTicky();
  hBpBmMult80_100->Draw("hist E");

  TH1D* hBpBmMult20_40 = vhBpAsMult[3].hDPhiOS;
  histDPhiMakeUp(hBpBmMult20_40, kRed, 0, 0.02);
  hBpBmMult20_40->SetMinimum(1e-4);
  hBpBmMult20_40->GetXaxis()->SetTitle("");
  hBpBmMult20_40->GetYaxis()->SetNdivisions(5);
  c01_DPhi_Mult->cd();
  gPad->SetTicky();
  hBpBmMult20_40->Draw("hist E");

  TH1D* hBpBmMult0_1 = vhBpAsMult[6].hDPhiOS;
  histDPhiMakeUp(hBpBmMult0_1, kRed, 0, 0.02);
  hBpBmMult0_1->SetMinimum(1e-4);
  hBpBmMult0_1->GetXaxis()->SetTitle("");
  hBpBmMult0_1->GetYaxis()->SetNdivisions(5);
  c02_DPhi_Mult->cd();
  hBpBmMult0_1->Draw("hist E");

  TH1D* hDpDmMult80_100 = vhDpAsMult[0].hDPhiOS;
  histDPhiMakeUp(hDpDmMult80_100, kBlue, 0, 0.009);
  hDpDmMult80_100->SetMaximum(0.0119);
  hDpDmMult80_100->GetXaxis()->SetTitle("");
  hDpDmMult80_100->GetYaxis()->SetTitle("");
  // hDpDmMult80_100->GetYaxis()->SetTitleOffset(3);
  c10_DPhi_Mult->cd();
  gPad->SetTicky();
  gPad->SetTickx();
  hDpDmMult80_100->Draw("hist E");

  TH1D* hDpDmMult20_40 = vhDpAsMult[3].hDPhiOS;
  histDPhiMakeUp(hDpDmMult20_40, kBlue, 0, 0.009);
  hDpDmMult20_40->SetMaximum(0.0119);
  hDpDmMult20_40->GetXaxis()->SetTitle("");
  c11_DPhi_Mult->cd();
  gPad->SetTicky();
  gPad->SetTickx();
  hDpDmMult20_40->Draw("hist E");

  TH1D* hDpDmMult0_1 = vhDpAsMult[6].hDPhiOS;
  histDPhiMakeUp(hDpDmMult0_1, kBlue, 0, 0.009);
  hDpDmMult0_1->SetMaximum(0.0119);
  // hDpDmMult0_1->GetXaxis()->SetTitle("");
  c12_DPhi_Mult->cd();
  gPad->SetTickx();
  hDpDmMult0_1->Draw("hist E");

  TLegend* lhists_DPhi_Mult = new TLegend(0.30, 0.6, 0.50, 0.75);
  lhists_DPhi_Mult->SetTextSize(0.05);
  lhists_DPhi_Mult->SetBorderSize(0);
  // lhists_DPhi_Mult->SetLineWidth(2);
  lhists_DPhi_Mult->SetMargin(0.5);
  lhists_DPhi_Mult->AddEntry(hBpBm, "B^{+}B^{-}", "l");
  lhists_DPhi_Mult->AddEntry(hDpDm, "D^{+}D^{-}", "l");
  TLegend* l00_DPhi_Mult = new TLegend(0.25, 0.75, 0.40, 0.8);
  l00_DPhi_Mult->SetTextSize(0.05);
  l00_DPhi_Mult->SetBorderSize(0);
  l00_DPhi_Mult->AddEntry("", "(a) 80-100%", "");
  TLegend* l01_DPhi_Mult = new TLegend(0.25-0.1, 0.75, 0.40-0.1, 0.8);
  l01_DPhi_Mult->SetTextSize(0.05);
  l01_DPhi_Mult->SetBorderSize(0);
  l01_DPhi_Mult->AddEntry("", "(b) 20-40%", "");
  TLegend* l02_DPhi_Mult = new TLegend(0.25-0.1, 0.75, 0.40-0.1, 0.8);
  l02_DPhi_Mult->SetTextSize(0.05);
  l02_DPhi_Mult->SetBorderSize(0);
  l02_DPhi_Mult->AddEntry("", "(c) 0-1%", "");
  TLegend* l10_DPhi_Mult = new TLegend(0.25, 0.75+0.1, 0.40, 0.8+0.1);
  l10_DPhi_Mult->SetTextSize(0.05);
  l10_DPhi_Mult->SetBorderSize(0);
  l10_DPhi_Mult->AddEntry("", "(d) 80-100%", "");
  TLegend* l11_DPhi_Mult = new TLegend(0.25-0.1, 0.75+0.1, 0.40-0.1, 0.8+0.1);
  l11_DPhi_Mult->SetTextSize(0.05);
  l11_DPhi_Mult->SetBorderSize(0);
  l11_DPhi_Mult->AddEntry("", "(e) 20-40%", "");
  TLegend* l12_DPhi_Mult = new TLegend(0.25-0.1, 0.75+0.1, 0.40-0.1, 0.8+0.1);
  l12_DPhi_Mult->SetTextSize(0.05);
  l12_DPhi_Mult->SetBorderSize(0);
  l12_DPhi_Mult->AddEntry("", "(f) 0-1%", "");

  c00_DPhi_Mult->cd(); lhists_DPhi_Mult->Draw(); l00_DPhi_Mult->Draw();
  c01_DPhi_Mult->cd(); l01_DPhi_Mult->Draw();
  c02_DPhi_Mult->cd(); l02_DPhi_Mult->Draw();
  c10_DPhi_Mult->cd(); l10_DPhi_Mult->Draw();
  c11_DPhi_Mult->cd(); l11_DPhi_Mult->Draw();
  c12_DPhi_Mult->cd(); l12_DPhi_Mult->Draw();
  
  if (write) {
    c2x3_DPhi_Mult->SaveAs(Form("Plots/c2x3_DPhi_Mult_%s.pdf", writeName));
    c2x3_DPhi_Mult->SaveAs(Form("Plots/c2x3_DPhi_Mult_%s.png", writeName));
  }

  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  // SAME SIGN - OPPOSITE SIGN STUDY
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////////

  TCanvas* c2x2_SS_OS = new TCanvas("c2x2_SS_OS", "SS_OS for B+B- and D+D- on 2x2 canvas", 1200, 1000);
  setCanvasMargins(c2x2_SS_OS, 0.15, 0.1, 0.1, 0.05);
  c2x2_SS_OS->cd();
  
  TPad* c00_SS_OS = new TPad("c00_SS_OS", "SS_OS for B+B- and B+B+", 0.05, 0.50, 0.50, 0.95);
  c00_SS_OS->SetLeftMargin(0.20);
  c00_SS_OS->SetRightMargin(eps);
  c00_SS_OS->SetBottomMargin(eps);
  c00_SS_OS->Draw();
  
  TPad* c01_SS_OS = new TPad("c01_SS_OS", "SS_OS for B+Lb and B+Lbbar", 0.50+eps, 0.50, 0.95, 0.95);
  c01_SS_OS->SetLeftMargin(0);
  c01_SS_OS->SetBottomMargin(eps);
  c01_SS_OS->Draw();
  
  TPad* c10_SS_OS = new TPad("c10_SS_OS", "SS_OS for D+D- and D+D+", 0.05, 0.05, 0.50, 0.50+eps);
  c10_SS_OS->SetLeftMargin(0.20);
  c10_SS_OS->SetRightMargin(eps);
  c10_SS_OS->SetTopMargin(0);
  c10_SS_OS->Draw();
 
 TPad* c11_SS_OS = new TPad("c11_SS_OS", "SS_OS for D+Lc+bar and D+Lc+", 0.50+eps, 0.05, 0.95, 0.50+eps);
 c11_SS_OS->SetLeftMargin(0);
 c11_SS_OS->SetTopMargin(0);
 c11_SS_OS->Draw();

 TH1D* hBpBmOS = (TH1D*)vhBpAs[0].hDPhiOS->Clone();
 TH1D* hBpBpSS = (TH1D*)vhBpAs[0].hDPhiSS->Clone();
 histDPhiMakeUp(hBpBmOS, kRed, 1e-6, 5e-2);
 hBpBmOS->SetMinimum(6e-7);
 hBpBmOS->GetXaxis()->SetTitle("");
 hBpBmOS->GetYaxis()->SetLabelOffset(0);
 hBpBpSS->SetLineStyle(2);
 hBpBpSS->SetLineColor(kRed);
 c00_SS_OS->cd();
 gPad->SetLogy();
 gPad->SetTicky();
 hBpBmOS->Draw("hist E");
 hBpBpSS->Draw("same hist E");

 TH1D* hBpLbOS = vhBpAs[4].hDPhiOS;
 TH1D* hBpLbbarSS = vhBpAs[4].hDPhiSS;
 histDPhiMakeUp(hBpLbOS, kRed, 1e-6, 5e-2);
 hBpLbOS->SetMinimum(6e-7);
 hBpLbOS->GetXaxis()->SetTitle("");
 hBpLbbarSS->SetLineStyle(2);
 hBpLbbarSS->SetLineColor(kRed);
 c01_SS_OS->cd();
 gPad->SetLogy();
 hBpLbOS->Draw("hist E");
 hBpLbbarSS->Draw("same hist E");

 TH1D* hDpDmOS = (TH1D*)vhDpAs[0].hDPhiOS->Clone();
 TH1D* hDpDpSS = (TH1D*)vhDpAs[0].hDPhiSS->Clone();
 histDPhiMakeUp(hDpDmOS, kBlue, 1e-6, 5e-2);
 hDpDmOS->SetMinimum(6e-7);
 hDpDmOS->GetXaxis()->SetTitle("");
 hDpDmOS->GetYaxis()->SetTitle("");
 hDpDmOS->GetYaxis()->SetLabelOffset(0);
 hDpDpSS->SetLineStyle(2);
 hDpDpSS->SetLineColor(kBlue);
 c10_SS_OS->cd();
 gPad->SetLogy();
 gPad->SetTicky();
 gPad->SetTickx();
 hDpDmOS->Draw("hist E");
 hDpDpSS->Draw("same hist E");
 
 TH1D* hDpLcpbarOS = vhDpAs[3].hDPhiOS;
 TH1D* hDpLcpSS = vhDpAs[3].hDPhiSS;
 histDPhiMakeUp(hDpLcpbarOS, kBlue, 1e-6, 5e-2);
 hDpLcpbarOS->SetMinimum(6e-7);
 // hDpLcpbarOS->GetXaxis()->SetTitle("");
 hDpLcpSS->SetLineStyle(2);
 hDpLcpSS->SetLineColor(kBlue);
 c11_SS_OS->cd();
 gPad->SetLogy();
 gPad->SetTickx();
 hDpLcpbarOS->Draw("hist E");
 hDpLcpSS->Draw("same hist E");
  
 TLegend* l00_SS_OS = new TLegend(0.30, 0.65, 0.40, 0.85);
 l00_SS_OS->SetTextSize(0.05);
 l00_SS_OS->SetBorderSize(0);
 l00_SS_OS->SetMargin(0.7);
 l00_SS_OS->AddEntry("", "(a)", "");
 l00_SS_OS->AddEntry(hBpBmOS, "B^{+}B^{-}", "l");
 l00_SS_OS->AddEntry(hBpBpSS, "B^{+}B^{+}", "l");
 TLegend* l01_SS_OS = new TLegend(0.30-0.2, 0.65, 0.40-0.2, 0.85);
 l01_SS_OS->SetTextSize(0.05);
 l01_SS_OS->SetBorderSize(0);
 l01_SS_OS->SetMargin(0.7);
 l01_SS_OS->AddEntry("", "(b)", "");
 l01_SS_OS->AddEntry(hBpLbOS, "B^{+}#Lambda_{b}^{0}", "l");
 l01_SS_OS->AddEntry(hBpLbbarSS, "B^{+}#bar#Lambda_{b}^{0}", "l");
 TLegend* l10_SS_OS = new TLegend(0.30, 0.65+0.1, 0.40, 0.85+0.1);
 l10_SS_OS->SetTextSize(0.05);
 l10_SS_OS->SetBorderSize(0);
 l10_SS_OS->SetMargin(0.7);
 l10_SS_OS->AddEntry("", "(c)", "");
 l10_SS_OS->AddEntry(hDpDmOS, "D^{+}D^{-}", "l");
 l10_SS_OS->AddEntry(hDpDpSS, "D^{+}D^{+}", "l");
 TLegend* l11_SS_OS = new TLegend(0.30-0.2, 0.65+0.1, 0.40-0.2, 0.85+0.1);
 l11_SS_OS->SetTextSize(0.05);
 l11_SS_OS->SetBorderSize(0);
 l11_SS_OS->SetMargin(0.7);
 l11_SS_OS->AddEntry("", "(d)", "");
 l11_SS_OS->AddEntry(hDpLcpbarOS, "D^{+}#bar#Lambda_{c}^{+}", "l");
 l11_SS_OS->AddEntry(hDpLcpSS, "D^{+}#Lambda_{c}^{+}", "l");
 
 c00_SS_OS->cd(); l00_SS_OS->Draw();
 c01_SS_OS->cd(); l01_SS_OS->Draw();
 c10_SS_OS->cd(); l10_SS_OS->Draw();
 c11_SS_OS->cd(); l11_SS_OS->Draw();

 if (write) {
   c2x2_SS_OS->SaveAs(Form("Plots/c2x2_SS_OS_%s.pdf", writeName));
   c2x2_SS_OS->SaveAs(Form("Plots/c2x2_SS_OS_%s.png", writeName));
 }

 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 // BALANCING
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////

 // Set up a 1x2 canvas like before
 // Template histograms are used for drawing options
 TH1D* hYieldsBpAsTemplate = new TH1D("hYieldsBpAsTemplate", "hYieldsBpAsTemplate", 8, 0, 8);
 histDPhiMakeUp(hYieldsBpAsTemplate, kRed, 1e-4, 1e0);
 hYieldsBpAsTemplate->GetYaxis()->SetTitle("yield");
 hYieldsBpAsTemplate->GetXaxis()->SetTitle("");
 hYieldsBpAsTemplate->GetXaxis()->SetLabelSize(0.05);
 TH1D* hYieldsDpAsTemplate = new TH1D("hYieldsDpAsTemplate", "hYieldsDpAsTemplate", 7, 0, 7);
 histDPhiMakeUp(hYieldsDpAsTemplate, kBlue, 1e-4, 1e0);
 hYieldsDpAsTemplate->GetXaxis()->SetTitle("Associate");
 hYieldsDpAsTemplate->GetXaxis()->SetLabelSize(0.05);
 
 TCanvas* c1x2_Bal = new TCanvas("c1x2_Bal", "Balancing for B+B- and D+D- on 1x2 canvas", 1600, 1200);
 setCanvasMargins(c1x2_Bal, 0.15, 0.1, 0.1, 0.05);
 c1x2_Bal->cd();
 TPad* c00_Bal = new TPad("c00_Bal", "Balancing for B+B-", 0.05, 0.10, 0.525, 0.95);
 c00_Bal->SetLeftMargin(0.20);
 c00_Bal->SetRightMargin(eps);
 c00_Bal->Draw();
 TPad* c01_Bal = new TPad("c01_Bal", "Balancing for D+D-", 0.525+eps, 0.10, 0.95, 0.95);
 c01_Bal->SetLeftMargin(0);
 c01_Bal->Draw();
 
 TLegend* l00_Bal = new TLegend(0.55, 0.75, 0.70, 0.8);
 l00_Bal->SetTextSize(0.05);
 l00_Bal->SetBorderSize(0);
 l00_Bal->AddEntry("", "(a) B^{+}{associate}", "");
 TLegend* l01_Bal = new TLegend(0.55-0.15, 0.75, 0.70-0.15, 0.8);
 l01_Bal->SetTextSize(0.05);
 l01_Bal->SetBorderSize(0);
 l01_Bal->AddEntry("", "(b) D^{+}{associate}", "");

 c00_Bal->cd();
 gPad->SetLogy();
 gPad->SetTicky();
 hYieldsBpAsTemplate->Draw("PE");
 l00_Bal->Draw();

 c01_Bal->cd();
 gPad->SetLogy();
 hYieldsDpAsTemplate->Draw("PE");
 l01_Bal->Draw();
 
 // Calculate the yields and fill the histograms
 // The histograms are drawn sharing a canvas afterwards
 TH1D* hYieldsBpAs[8];
 TH1D* hYieldsDpAs[7];

 for (Int_t i = 0; i < vhBpAs.size(); i++) {

   TH1D* hDPhiOS = vhBpAs[i].hDPhiOS;
   TH1D* hDPhiSS = vhBpAs[i].hDPhiSS;

   // Subtract SS from OS to reduce background
   TH1D* hCorr = (TH1D*)hDPhiOS->Clone();
   hCorr->Add(hDPhiSS, -1.);

   // Errors can be implemented later, but are typically about 0.1% of the yield value
   // It is kept like this for now
   Double_t yield = hCorr->Integral();

   c00_Bal->cd();
   hYieldsBpAs[i] = new TH1D(Form("hYieldsBpAs_%i", i), Form("hYieldsBpAs_%i", i), 8, 0, 8);
   hYieldsBpAs[i]->SetLineColor(kRed);
   hYieldsBpAs[i]->SetBinContent(1+i, yield);
   hYieldsBpAs[i]->SetBinError(1+i, yield/1e2);
   hYieldsBpAs[i]->Draw("same PE");

   hYieldsBpAsTemplate->GetXaxis()->SetBinLabel(1+i, vhBpAs[i].AssociateNameOS);

 } // for Int_i, BpAs

 for (Int_t i = 0; i < vhDpAs.size(); i++) {

   TH1D* hDPhiOS = vhDpAs[i].hDPhiOS;
   TH1D* hDPhiSS = vhDpAs[i].hDPhiSS;

   // Subtract SS from OS to reduce background
   TH1D* hCorr = (TH1D*)hDPhiOS->Clone();
   hCorr->Add(hDPhiSS, -1.);

   // Errors can be implemented later, but are typically about 0.1% of the yield value
   // It is kept like this for now
   Double_t yield = hCorr->Integral();

   c01_Bal->cd();
   hYieldsDpAs[i] = new TH1D(Form("hYieldsDpAs_%i", i), Form("hYieldsDpAs_%i", i), 7, 0, 7);
   hYieldsDpAs[i]->SetLineColor(kBlue);
   hYieldsDpAs[i]->SetBinContent(1+i, yield);
   hYieldsDpAs[i]->SetBinError(1+i, yield/1e2);
   hYieldsDpAs[i]->Draw("same PE");

   hYieldsDpAsTemplate->GetXaxis()->SetBinLabel(1+i, vhDpAs[i].AssociateNameOS);

 } // for Int_i, DpAs

 if (write) {
   c1x2_Bal->SaveAs(Form("Plots/c1x2_Balancing_%s.pdf", writeName));
   c1x2_Bal->SaveAs(Form("Plots/c1x2_Balancing_%s.png", writeName));
 }

 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 // PTHATMIN STUDY
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 
 // The pTHatMin study is only done a while ago with older simulation.
 // The image is clear anyways and the conclusion still holds, so the older information is used here.
 // This could be implemented into a configureInput function, but the benefit is minimal in this case.
 std::string path = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/";

 TFile* hBpBm_pT1_File = new TFile((path + "BplusBminus_8.root").c_str()); // pTHatMin = 1
 TH1D* hBpBm_pT1 = (TH1D*)hBpBm_pT1_File->Get("hDPhi");
 TH1D* hBpBmTrPt_pT1 = (TH1D*)hBpBm_pT1_File->Get("hTrPt");
 hBpBm_pT1->Scale(1/hBpBmTrPt_pT1->Integral());

 TFile* hBpBm_pT4_File = new TFile((path + "BplusBminus_4.root").c_str()); // pTHatMin = 4
 TH1D* hBpBm_pT4 = (TH1D*)hBpBm_pT4_File->Get("hDPhi");
 TH1D* hBpBmTrPt_pT4 = (TH1D*)hBpBm_pT4_File->Get("hTrPt");
 hBpBm_pT4->Scale(1/hBpBmTrPt_pT4->Integral());

 TFile* hBpBm_pT10_File = new TFile((path + "BplusBminus_9.root").c_str()); // pTHatMin = 10
 TH1D* hBpBm_pT10 = (TH1D*)hBpBm_pT10_File->Get("hDPhi");
 TH1D* hBpBmTrPt_pT10 = (TH1D*)hBpBm_pT10_File->Get("hTrPt"); 
 hBpBm_pT10->Scale(1/hBpBmTrPt_pT10->Integral());

 TFile* hDpDm_pT1_File = new TFile((path + "DplusDminus_6.root").c_str()); // pTHatMin = 1
 TH1D* hDpDm_pT1 = (TH1D*)hDpDm_pT1_File->Get("hDPhi");
 TH1D* hDpDmTrPt_pT1 = (TH1D*)hDpDm_pT1_File->Get("hTrPt");
 hDpDm_pT1->Scale(1/hDpDmTrPt_pT1->Integral());

 TFile* hDpDm_pT4_File = new TFile((path + "DplusDminus_7.root").c_str()); // pTHatMin = 4
 TH1D* hDpDm_pT4 = (TH1D*)hDpDm_pT4_File->Get("hDPhi");
 TH1D* hDpDmTrPt_pT4 = (TH1D*)hDpDm_pT4_File->Get("hTrPt"); 
 hDpDm_pT4->Scale(1/hDpDmTrPt_pT4->Integral());

 TFile* hDpDm_pT10_File = new TFile((path + "DplusDminus_8.root").c_str()); // pTHatMin = 10
 TH1D* hDpDm_pT10 = (TH1D*)hDpDm_pT10_File->Get("hDPhi");
 TH1D* hDpDmTrPt_pT10 = (TH1D*)hDpDm_pT10_File->Get("hTrPt");
 hDpDm_pT10->Scale(1/hDpDmTrPt_pT10->Integral());

 TCanvas* c2x3_DPhi_pTHatMin = new TCanvas("c2x3_Dphi_pTHatMin", "DPhi with pTHatMin dependence for B+B- and D+D- on 2x3 canvas", 1200, 1000);
 setCanvasMargins(c2x3_DPhi_pTHatMin, 0.20, 0.1, 0.1, 0.05);
 c2x3_DPhi_pTHatMin->cd();
 TPad* c00_DPhi_pTHatMin = new TPad("c00_DPhi_pTHatMin", "DPhi for pTHatMin = 1 for B+B-", 0.05, 0.50, 0.38, 0.95);
 c00_DPhi_pTHatMin->SetLeftMargin(0.22);
 c00_DPhi_pTHatMin->SetRightMargin(eps);
 c00_DPhi_pTHatMin->SetBottomMargin(eps);
 c00_DPhi_pTHatMin->Draw();
 TPad* c01_DPhi_pTHatMin = new TPad("c01_DPhi_pTHatMin", "DPhi for pTHatMin = 4 for B+B-", 0.38+eps, 0.50, 0.65, 0.95);
 c01_DPhi_pTHatMin->SetLeftMargin(0);
 c01_DPhi_pTHatMin->SetRightMargin(eps);
 c01_DPhi_pTHatMin->SetBottomMargin(eps);
 c01_DPhi_pTHatMin->Draw();
 TPad* c02_DPhi_pTHatMin = new TPad("c02_DPhi_pTHatMin", "DPhi for pTHatMin = 10 for B+B-", 0.65+eps, 0.50, 0.95, 0.95);
 c02_DPhi_pTHatMin->SetLeftMargin(0);
 c02_DPhi_pTHatMin->SetBottomMargin(eps);
 c02_DPhi_pTHatMin->Draw();
 TPad* c10_DPhi_pTHatMin = new TPad("c10_DPhi_pTHatMin", "DPhi for pTHatMin = 1 for D+D-", 0.05, 0.05, 0.38, 0.50+eps);
 c10_DPhi_pTHatMin->SetLeftMargin(0.22);
 c10_DPhi_pTHatMin->SetRightMargin(eps);
 c10_DPhi_pTHatMin->SetTopMargin(0);
 c10_DPhi_pTHatMin->Draw();
 TPad* c11_DPhi_pTHatMin = new TPad("c11_DPhi_pTHatMin", "DPhi for pTHatMin = 4 for D+D-", 0.38+eps, 0.05, 0.65, 0.50+eps);
 c11_DPhi_pTHatMin->SetLeftMargin(0);
 c11_DPhi_pTHatMin->SetRightMargin(eps);
 c11_DPhi_pTHatMin->SetTopMargin(0);
 c11_DPhi_pTHatMin->Draw();
 TPad* c12_DPhi_pTHatMin = new TPad("c12_DPhi_pTHatMin", "DPhi for pTHatMin = 10 for D+D-", 0.65+eps, 0.05, 0.95, 0.50+eps);
 c12_DPhi_pTHatMin->SetLeftMargin(0);
 c12_DPhi_pTHatMin->SetTopMargin(0);
 c12_DPhi_pTHatMin->Draw();
 
 // pTHatMin = 1
 histDPhiMakeUp(hBpBm_pT1, kRed, 0.0001, 0.02); // 0.0001
 hBpBm_pT1->SetMinimum(1e-4);
 hBpBm_pT1->GetXaxis()->SetTitle("");
 // hBpBm_pT1->GetYaxis()->SetTitleOffset(3);
 hBpBm_pT1->GetYaxis()->SetNdivisions(5);
 c00_DPhi_pTHatMin->cd();
 gPad->SetTicky();
 hBpBm_pT1->Draw("hist E");
 
 // pTHatMin = 4
 histDPhiMakeUp(hBpBm_pT4, kRed, 0, 0.02);
 hBpBm_pT4->SetMinimum(1e-4);
 hBpBm_pT4->GetXaxis()->SetTitle("");
 hBpBm_pT4->GetYaxis()->SetNdivisions(5);
 c01_DPhi_pTHatMin->cd();
 gPad->SetTicky();
 hBpBm_pT4->Draw("hist E");
 
 // pTHatMin = 10
 histDPhiMakeUp(hBpBm_pT10, kRed, 0, 0.02);
 hBpBm_pT10->SetMinimum(1e-4);
 hBpBm_pT10->GetXaxis()->SetTitle("");
 hBpBm_pT10->GetYaxis()->SetNdivisions(5);
 c02_DPhi_pTHatMin->cd();
 hBpBm_pT10->Draw("hist E");
 
 // pTHatMin = 1
 histDPhiMakeUp(hDpDm_pT1, kBlue, 0, 0.011);
 hDpDm_pT1->SetMaximum(0.0119);
 hDpDm_pT1->GetXaxis()->SetTitle("");
 hDpDm_pT1->GetYaxis()->SetTitle("");
 // hDpDm_pT1->GetYaxis()->SetTitleOffset(3);
 c10_DPhi_pTHatMin->cd();
 gPad->SetTicky();
 gPad->SetTickx();
 hDpDm_pT1->Draw("hist E");
 
 // pTHatMin = 4
 histDPhiMakeUp(hDpDm_pT4, kBlue, 0, 0.011);
 hDpDm_pT4->SetMaximum(0.0119);
 hDpDm_pT4->GetXaxis()->SetTitle("");
 c11_DPhi_pTHatMin->cd();
 gPad->SetTicky();
 gPad->SetTickx();
 hDpDm_pT4->Draw("hist E");
 
 // pTHatMin = 10
 histDPhiMakeUp(hDpDm_pT10, kBlue, 0, 0.011);
 hDpDm_pT10->SetMaximum(0.0119);
 // hDpDm_pT10->GetXaxis()->SetTitle("");
 c12_DPhi_pTHatMin->cd();
 gPad->SetTickx();
 hDpDm_pT10->Draw("hist E");
 
 TLegend* lhists_DPhi_pTHatMin = new TLegend(0.30, 0.6, 0.50, 0.75);
 lhists_DPhi_pTHatMin->SetTextSize(0.05);
 lhists_DPhi_pTHatMin->SetBorderSize(0);
 // lhists_DPhi_pTHatMin->SetLineWidth(2);
 lhists_DPhi_pTHatMin->SetMargin(0.5);
 lhists_DPhi_pTHatMin->AddEntry(hBpBm, "B^{+}B^{-}", "l");
 lhists_DPhi_pTHatMin->AddEntry(hDpDm, "D^{+}D^{-}", "l");
 TLegend* l00_DPhi_pTHatMin = new TLegend(0.25, 0.75, 0.40, 0.8);
 l00_DPhi_pTHatMin->SetTextSize(0.05);
 l00_DPhi_pTHatMin->SetBorderSize(0);
 l00_DPhi_pTHatMin->AddEntry("", "(a) pTHatMin = 1", "");
 TLegend* l01_DPhi_pTHatMin = new TLegend(0.25-0.1, 0.75, 0.40-0.1, 0.8);
 l01_DPhi_pTHatMin->SetTextSize(0.05);
 l01_DPhi_pTHatMin->SetBorderSize(0);
 l01_DPhi_pTHatMin->AddEntry("", "(b) pTHatMin = 4", "");
 TLegend* l02_DPhi_pTHatMin = new TLegend(0.25-0.1, 0.75, 0.40-0.1, 0.8);
 l02_DPhi_pTHatMin->SetTextSize(0.05);
 l02_DPhi_pTHatMin->SetBorderSize(0);
 l02_DPhi_pTHatMin->AddEntry("", "(c) pTHatMin = 10", "");
 TLegend* l10_DPhi_pTHatMin = new TLegend(0.25, 0.75+0.1, 0.40, 0.8+0.1);
 l10_DPhi_pTHatMin->SetTextSize(0.05);
 l10_DPhi_pTHatMin->SetBorderSize(0);
 l10_DPhi_pTHatMin->AddEntry("", "(d) pTHatMin = 1", "");
 TLegend* l11_DPhi_pTHatMin = new TLegend(0.25-0.1, 0.75+0.1, 0.40-0.1, 0.8+0.1);
 l11_DPhi_pTHatMin->SetTextSize(0.05);
 l11_DPhi_pTHatMin->SetBorderSize(0);
 l11_DPhi_pTHatMin->AddEntry("", "(e) pTHatMin = 4", "");
 TLegend* l12_DPhi_pTHatMin = new TLegend(0.25-0.1, 0.75+0.1, 0.40-0.1, 0.8+0.1);
 l12_DPhi_pTHatMin->SetTextSize(0.05);
 l12_DPhi_pTHatMin->SetBorderSize(0);
 l12_DPhi_pTHatMin->AddEntry("", "(f) pTHatMin = 10", "");
 
 c00_DPhi_pTHatMin->cd(); lhists_DPhi_pTHatMin->Draw(); l00_DPhi_pTHatMin->Draw();
 c01_DPhi_pTHatMin->cd(); l01_DPhi_pTHatMin->Draw();
 c02_DPhi_pTHatMin->cd(); l02_DPhi_pTHatMin->Draw();
 c10_DPhi_pTHatMin->cd(); l10_DPhi_pTHatMin->Draw();
 c11_DPhi_pTHatMin->cd(); l11_DPhi_pTHatMin->Draw();
 c12_DPhi_pTHatMin->cd(); l12_DPhi_pTHatMin->Draw();
 
 if (write) {
   c2x3_DPhi_pTHatMin->SaveAs("Plots/c2x3_DPhi_pTHatMin.pdf");
   c2x3_DPhi_pTHatMin->SaveAs("Plots/c2x3_DPhi_pTHatMin.png");
 }

 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 // MULTIPLICITY SPECTRUM
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////

 // Beauty Monash
 path = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_215/";
 
 TFile* hBeautyMult_File = new TFile((path + "BplusBminus.root").c_str());
 TH1D* hBeautyMult = (TH1D*)hBeautyMult_File->Get("summed MULTIPLICITY");
 // hBeautyMult->Scale(1/hBeautyMult->Integral());

 // (prompt) Charm Monash
 path = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_215/";
 
 TFile* hCharmMult_File = new TFile((path + "DplusDminus.root").c_str());
 TH1D* hCharmMult = (TH1D*)hCharmMult_File->Get("summed MULTIPLICITY");
 // hCharmMult->Scale(1/hCharmMult->Integral());

 TCanvas* c1x2_Mult = new TCanvas("c1x2_Mult", "Monash multiplicity distributions for B+B- and D+D- on 1x2 canvas", 1600, 1200);
 setCanvasMargins(c1x2_Mult, 0.15, 0.1, 0.1, 0.05);
 c1x2_Mult->cd();
 TPad* c00_Mult = new TPad("c00_Mult", "Multiplicity distribution for B+B-", 0.05, 0.10, 0.525, 0.95);
 c00_Mult->SetLeftMargin(0.20);
 c00_Mult->SetRightMargin(eps);
 c00_Mult->Draw();
 TPad* c01_Mult = new TPad("c01_Mult", "Multiplicity distribution for D+D-", 0.525+eps, 0.10, 0.95, 0.95);
 c01_Mult->SetLeftMargin(0);
 c01_Mult->Draw();
 
 TLegend* l00_Mult = new TLegend(0.22, 0.82, 0.37, 0.87);
 l00_Mult->SetTextSize(0.05);
 l00_Mult->SetBorderSize(0);
 l00_Mult->AddEntry("", "(a) beauty", "");
 TLegend* l01_Mult = new TLegend(0.22-0.20, 0.82, 0.37-0.20, 0.87);
 l01_Mult->SetTextSize(0.05);
 l01_Mult->SetBorderSize(0);
 l01_Mult->AddEntry("", "(b) charm", "");

 /*
 histDPhiMakeUp(hBeautyMult, kRed, 1, 2e8);
 hBeautyMult->GetXaxis()->SetTitle("");
 // Events multiplicity < 1 make no sense
 hBeautyMult->GetYaxis()->SetTitle("counts");
 hBeautyMult->GetYaxis()->SetTitleSize(0.05);
 hBeautyMult->GetXaxis()->SetTitleSize(0.05);
 hBeautyMult->GetXaxis()->SetLabelOffset(0);
 c00_Mult->cd();
 gPad->SetTicky();
 gPad->SetLogy();
 gPad->SetLogx();
 hBeautyMult->Draw("hist E");
 l00_Mult->Draw();
 */

 // Template to avoid bins < 1
 TH1D* hMultBeautyTemplate = new TH1D("hMultBeautyTemplate", "multiplicity beauty template", 300, 1, 301);
 histDPhiMakeUp(hMultBeautyTemplate, kRed, 1, 2.5e8);
 hMultBeautyTemplate->GetXaxis()->SetTitle("");
 hMultBeautyTemplate->GetYaxis()->SetTitle("counts");
 hMultBeautyTemplate->GetYaxis()->SetTitleSize(0.05);
 hMultBeautyTemplate->GetXaxis()->SetTitleSize(0.05);
 hMultBeautyTemplate->GetXaxis()->SetLabelOffset(0);
 c00_Mult->cd();
 gPad->SetTicky();
 gPad->SetLogy();
 gPad->SetLogx();
 hMultBeautyTemplate->Draw("hist E");
 hBeautyMult->SetLineColor(kRed);
 hBeautyMult->Draw("same hist E");
 l00_Mult->Draw();

 // Beauty bin shading
 // Due to the binning of the original multiplicity histograms, the values will always be in the next bin
 // e.g. value 22 will be in bin number 23
 std::vector<Int_t> vBeautyLimits;
 vBeautyLimits.push_back(22);
 vBeautyLimits.push_back(36);
 vBeautyLimits.push_back(50);
 vBeautyLimits.push_back(68);
 vBeautyLimits.push_back(92);
 vBeautyLimits.push_back(113);

 std::vector<const char*> vBeautyText;
 vBeautyText.push_back("80-100 %");
 vBeautyText.push_back("60-80 %");
 vBeautyText.push_back("40-60 %");
 vBeautyText.push_back("20-40 %");
 vBeautyText.push_back("5-20 %");
 vBeautyText.push_back("1-5 %");
 vBeautyText.push_back("0-1 %");

 Int_t counter = 1;
 for (auto& i : vBeautyLimits) {
   // Get bin info
   // std::pair<int, double> binInfo = getBinInfo(hBeautyMult, vBeautyLimits[i]);
    
   // Output the bin number and bin content
   // std::cout << "Value " << vBeautyLimits[i] << " is in bin number " << binInfo.first
   // << " with content " << binInfo.second << std::endl;
   
   Double_t binCenter = hBeautyMult->GetBinCenter(i+1);
   Double_t binContent = hBeautyMult->GetBinContent(i+1);
   std::cout << binCenter << std::endl;
   TLine* binLine = new TLine(binCenter, 0, binCenter, binContent); // x1, y1, x2, y2

   c00_Mult->cd();
   binLine->Draw("same");

   if (counter % 2 == 0) {
     TH1D* hRange = (TH1D*)hBeautyMult->Clone(Form("hBeautyMultRange_%i", counter));
     Double_t x_left, x_right;
     x_left = hBeautyMult->GetBinCenter(1+vBeautyLimits[counter-2]); x_right = binCenter;
     std::cout << x_left << " to " << x_right << std::endl;
     
     hRange->GetXaxis()->SetRangeUser(x_left, x_right);
     hRange->SetFillStyle(3003);
     hRange->SetFillColor(kBlack);
     hRange->Draw("same FC");
   }
   
   // Add text inside the bin
   // Align the text in the middle of the bin
   Double_t binAlign;
   if (counter == 1) { binAlign = geometricMean(1, binCenter); }
   else { binAlign = 1 + geometricMean(hBeautyMult->GetBinCenter(vBeautyLimits[counter-2]), binCenter); }
   TLatex* binText = new TLatex(binAlign, pow(binContent, 0.5), vBeautyText[counter-1]);
   binText->SetTextAlign(22); // Center alignment
   binText->SetTextAngle(90);
   binText->SetTextSize(0.03);
   binText->Draw("same");

   counter++;
 } // for i over BeautyLimits

 // Text for the last bin can be treated seperately
 Double_t binAlign = geometricMean(vBeautyLimits[5], 240);
 Double_t binContent = hBeautyMult->GetBinCenter(300 - vBeautyLimits[5] + 1);
 TLatex* binText = new TLatex(binAlign, pow(binContent, 0.5), vBeautyText[6]);
 binText->SetTextAlign(22); // Center alignment
 binText->SetTextAngle(90);
 binText->SetTextSize(0.03);
 binText->Draw("same");

 /*
 histDPhiMakeUp(hCharmMult, kBlue, 1, 2e8);
 hCharmMult->GetXaxis()->SetTitle("multiplicity");
 hCharmMult->GetXaxis()->SetTitleSize(0.05);
 hCharmMult->GetXaxis()->SetLabelOffset(0);
 hCharmMult->GetXaxis()->SetTitleOffset(1.0);
 hCharmMult->GetYaxis()->SetTitleSize(0.05);
 c01_Mult->cd();
 gPad->SetLogy();
 gPad->SetLogx();
 hCharmMult->Draw("hist E");
 l01_Mult->Draw();
 */
 
 // Template to avoid bins < 1
 TH1D* hMultCharmTemplate = new TH1D("hMultCharmTemplate", "multiplicity charm template", 300, 1, 301);
 histDPhiMakeUp(hMultCharmTemplate, kBlue, 1, 2.5e8);
 hMultCharmTemplate->GetXaxis()->SetTitle("multiplicity");
 hMultCharmTemplate->GetXaxis()->SetTitleSize(0.05);
 hMultCharmTemplate->GetXaxis()->SetTitleSize(0.05);
 hMultCharmTemplate->GetXaxis()->SetTitleOffset(1.0);
 hMultCharmTemplate->GetYaxis()->SetTitleSize(0.05);
 c01_Mult->cd();
 gPad->SetLogy();
 gPad->SetLogx();
 hMultCharmTemplate->Draw("hist E");
 hCharmMult->SetLineColor(kBlue);
 hCharmMult->Draw("same hist E");
 l01_Mult->Draw();


 // Charm bin shading
 // Due to the binning of the original multiplicity histograms, the values will always be in the next bin
 // e.g. value 22 will be in bin number 23
 std::vector<Int_t> vCharmLimits;
 vCharmLimits.push_back(7);
 vCharmLimits.push_back(10);
 vCharmLimits.push_back(14);
 vCharmLimits.push_back(24);
 vCharmLimits.push_back(47);
 vCharmLimits.push_back(76);

 std::vector<const char*> vCharmText;
 vCharmText.push_back("80-100 %");
 vCharmText.push_back("60-80 %");
 vCharmText.push_back("40-60 %");
 vCharmText.push_back("20-40 %");
 vCharmText.push_back("5-20 %");
 vCharmText.push_back("1-5 %");
 vCharmText.push_back("0-1 %");

 counter = 1;
 for (auto& i : vCharmLimits) {
   // Get bin info
   // std::pair<int, double> binInfo = getBinInfo(hCharmMult, vCharmLimits[i]);
    
   // Output the bin number and bin content
   // std::cout << "Value " << vCharmLimits[i] << " is in bin number " << binInfo.first
   // << " with content " << binInfo.second << std::endl;
   
   Double_t binCenter = hCharmMult->GetBinCenter(i+1);
   Double_t binContent = hCharmMult->GetBinContent(i+1);
   std::cout << binCenter << std::endl;
   TLine* binLine = new TLine(binCenter, 0, binCenter, binContent); // x1, y1, x2, y2

   c01_Mult->cd();
   binLine->Draw("same");

   if (counter % 2 == 0) {
     TH1D* hRange = (TH1D*)hCharmMult->Clone(Form("hCharmMultRange_%i", counter));
     Double_t x_left, x_right;
     x_left = hCharmMult->GetBinCenter(1+vCharmLimits[counter-2]); x_right = binCenter;
     std::cout << x_left << " to " << x_right << std::endl;
     
     hRange->GetXaxis()->SetRangeUser(x_left, x_right);
     hRange->SetFillStyle(3003);
     hRange->SetFillColor(kBlack);
     hRange->Draw("same FC");
   }
   
   // Add text inside the bin
   // Align the text in the middle of the bin
   Double_t binAlign;
   if (counter == 1) { binAlign = geometricMean(1, binCenter); }
   else { binAlign = 1 + geometricMean(hCharmMult->GetBinCenter(vCharmLimits[counter-2]), binCenter); }
   TLatex* binText = new TLatex(binAlign, pow(binContent, 0.5), vCharmText[counter-1]);
   binText->SetTextAlign(22); // Center alignment
   binText->SetTextAngle(90);
   binText->SetTextSize(0.03);
   binText->Draw("same");

   counter++;
 } // for i over CharmLimits

 // Text for the last bin can be treated seperately
 binAlign = geometricMean(vCharmLimits[5], 210);
 binContent = hCharmMult->GetBinCenter(300 - vCharmLimits[5] + 1);
 binText = new TLatex(binAlign, pow(binContent, 0.5), vCharmText[6]);
 binText->SetTextAlign(22); // Center alignment
 binText->SetTextAngle(90);
 binText->SetTextSize(0.03);
 binText->Draw("same");
 
 if (write) {
   c1x2_Mult->SaveAs("Plots/c1x2_MultiplicityDistributions_215.pdf");
   c1x2_Mult->SaveAs("Plots/c1x2_MultiplicityDistributions_215.png");
 }

 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 // INCLUSIVE CHARM ORIGIN STUDY
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////

 TCanvas* c3x2_DPhiOrigin = new TCanvas("c1x2_DphiOrigin", "DPhiOrigin: inclusive charm on 3x2 canvas", 1600, 1200);
 setCanvasMargins(c3x2_DPhiOrigin, 0.15, 0.1, 0.1, 0.05);
 c3x2_DPhiOrigin->cd();
  
 // Subpads are created with names indicating their position on the large canvas (xy)
 // A TLegendEntry is used to add identifiers to each pad
 // The standard is (a), (b), (c), etc. but this can be changed by the user
 TPad* c00_DPhiOrigin = new TPad("c00_DPhiOrigin", "LL prompt/prompt", 0.05, 0.65, 0.50, 0.95); // 0.05, 0.55, 0.50, 0.95
 c00_DPhiOrigin->SetTopMargin(0);
 c00_DPhiOrigin->SetLeftMargin(0.20);
 c00_DPhiOrigin->SetRightMargin(eps);
 c00_DPhiOrigin->SetBottomMargin(eps);
 c00_DPhiOrigin->Draw();
 
 TPad* c01_DPhiOrigin = new TPad("c01_DPhiOrigin", "HH prompt/prompt", 0.50+eps, 0.65, 0.95, 0.95); // 0.50+eps, 0.55, 0.95, 0.95
 c01_DPhiOrigin->SetTopMargin(0);
 c01_DPhiOrigin->SetLeftMargin(0.20);
 c01_DPhiOrigin->SetLeftMargin(0);
 c01_DPhiOrigin->SetBottomMargin(eps);
 c01_DPhiOrigin->Draw();
 
 TPad* c10_DPhiOrigin = new TPad("c10_DPhiOrigin", "LL non-prompt/non-prompt", 0.05, 0.35, 0.50, 0.65+eps); // 0.05, 0.15, 0.50, 0.55+eps
 c10_DPhiOrigin->SetLeftMargin(0.20);
 c10_DPhiOrigin->SetRightMargin(eps);
 c10_DPhiOrigin->SetTopMargin(0);
 c10_DPhiOrigin->SetBottomMargin(0);
 c10_DPhiOrigin->Draw();
 
 TPad* c11_DPhiOrigin = new TPad("c11_DPhiOrigin", "HH non-prompt/non-prompt", 0.50+eps, 0.35, 0.95, 0.65+eps); // 0.50+eps, 0.15, 0.95, 0.55+eps
 c11_DPhiOrigin->SetLeftMargin(0);
 c11_DPhiOrigin->SetTopMargin(0);
 c11_DPhiOrigin->SetBottomMargin(0);
 c11_DPhiOrigin->Draw();
 
 // Minipads
 TPad* c20_DPhiOrigin = new TPad("c20_DPhiOrigin", "LL prompt/non-prompt + vv", 0.05, 0, 0.50, 0.35+eps); // 0.05, 0.05, 0.50, 0.15+eps
 c20_DPhiOrigin->SetLeftMargin(0.20);
 c20_DPhiOrigin->SetRightMargin(eps);
 c20_DPhiOrigin->SetTopMargin(0);
 c20_DPhiOrigin->SetBottomMargin(0.15);
 c20_DPhiOrigin->Draw();
 
 TPad* c21_DPhiOrigin = new TPad("c21_DPhiOrigin", "HH prompt/non-prompt + vv", 0.50+eps, 0, 0.95, 0.35+eps); // 0.50+eps, 0.05, 0.95, 0.15+eps
 c21_DPhiOrigin->SetLeftMargin(0);
 c21_DPhiOrigin->SetTopMargin(0);
 c21_DPhiOrigin->SetBottomMargin(0.15);
 c21_DPhiOrigin->Draw();

 // Retrieve histograms
 // Could be done with configure input, but not strictly necessary or useful here
 const char* pathDpDm = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_214/DplusDminus.root"; // inclusive charm
 TFile* DpDmFile = new TFile(pathDpDm);

 // Low-low
 TH1D* hDpDmOriginLLPr = (TH1D*)DpDmFile->Get("hDPhiLLPr");
 TH1D* hDpDmTrPtOriginLLPr = (TH1D*)DpDmFile->Get("hTrPtLLPr");
 hDpDmOriginLLPr->Scale(1/hDpDmTrPtOriginLLPr->Integral());
 hDpDmOriginLLPr->SetLineStyle(1);
 hDpDmOriginLLPr->SetLineWidth(1);

 TH1D* hDpDmOriginLLSc = (TH1D*)DpDmFile->Get("hDPhiLLSc");
 TH1D* hDpDmTrPtOriginLLSc = (TH1D*)DpDmFile->Get("hTrPtLLSc");
 hDpDmOriginLLSc->Scale(1/hDpDmTrPtOriginLLSc->Integral());
 hDpDmOriginLLSc->SetLineStyle(4);
 hDpDmOriginLLSc->SetLineWidth(2);

 TH1D* hDpDmOriginLLPrSc = (TH1D*)DpDmFile->Get("hDPhiLLPrSc");
 TH1D* hDpDmTrPtOriginLLPrSc = (TH1D*)DpDmFile->Get("hTrPtLLPrSc");
 hDpDmOriginLLPrSc->Scale(1/hDpDmTrPtOriginLLPrSc->Integral());
 hDpDmOriginLLPrSc->SetLineStyle(3);
 hDpDmOriginLLPrSc->SetLineWidth(2);

 // High-high
 TH1D* hDpDmOriginHHPr = (TH1D*)DpDmFile->Get("hDPhiHHPr");
 TH1D* hDpDmTrPtOriginHHPr = (TH1D*)DpDmFile->Get("hTrPtHHPr");
 hDpDmOriginHHPr->Scale(1/hDpDmTrPtOriginHHPr->Integral());
 hDpDmOriginHHPr->SetLineStyle(1);
 hDpDmOriginHHPr->SetLineWidth(1);

 TH1D* hDpDmOriginHHSc = (TH1D*)DpDmFile->Get("hDPhiHHSc");
 TH1D* hDpDmTrPtOriginHHSc = (TH1D*)DpDmFile->Get("hTrPtHHSc");
 hDpDmOriginHHSc->Scale(1/hDpDmTrPtOriginHHSc->Integral());
 hDpDmOriginHHSc->SetLineStyle(2);
 hDpDmOriginHHSc->SetLineWidth(2);

 TH1D* hDpDmOriginHHPrSc = (TH1D*)DpDmFile->Get("hDPhiHHPrSc");
 TH1D* hDpDmTrPtOriginHHPrSc = (TH1D*)DpDmFile->Get("hTrPtHHPrSc");
 hDpDmOriginHHPrSc->Scale(1/hDpDmTrPtOriginHHPrSc->Integral());
 hDpDmOriginHHPrSc->SetLineStyle(3);
 hDpDmOriginHHPrSc->SetLineWidth(2);

 TLegend* l01_DPhiOriginLabels = new TLegend(0.72-0.20, 0.10, 1.00-0.20, 0.40);
 l01_DPhiOriginLabels->SetTextSize(0.06);
 l01_DPhiOriginLabels->SetBorderSize(0);
 l01_DPhiOriginLabels->AddEntry(hDpDmOriginLLPr, "prompt/prompt", "L");
 l01_DPhiOriginLabels->AddEntry(hDpDmOriginLLSc, "non-prompt/non-prompt", "L");
 l01_DPhiOriginLabels->AddEntry(hDpDmOriginLLPrSc, "non-prompt/prompt + vv", "L");
 TLegend* l00_DPhiOrigin = new TLegend(0.23, 0.81, 0.40, 0.86);
 l00_DPhiOrigin->SetTextSize(0.06);
 l00_DPhiOrigin->SetBorderSize(0);
 l00_DPhiOrigin->AddEntry("", "(a) low-low: pT < 3 GeV", "");
 TLegend* l01_DPhiOrigin = new TLegend(0.23-0.20, 0.81, 0.40-0.20, 0.86);
 l01_DPhiOrigin->SetTextSize(0.06);
 l01_DPhiOrigin->SetBorderSize(0);
 l01_DPhiOrigin->AddEntry("", "(b) high-high: pT > 8 GeV", "");
 TLegend* l10_DPhiOrigin = new TLegend(0.25, 0.81, 0.30, 0.86);
 l10_DPhiOrigin->SetTextSize(0.06);
 l10_DPhiOrigin->SetBorderSize(0);
 l10_DPhiOrigin->AddEntry("", "(c)", "");
 TLegend* l11_DPhiOrigin = new TLegend(0.25-0.20, 0.81, 0.30-0.20, 0.86);
 l11_DPhiOrigin->SetTextSize(0.06);
 l11_DPhiOrigin->SetBorderSize(0);
 l11_DPhiOrigin->AddEntry("", "(d)", "");
 TLegend* l20_DPhiOrigin = new TLegend(0.25, 0.81+0.03, 0.30, 0.86+0.03);
 l20_DPhiOrigin->SetTextSize(0.055);
 l20_DPhiOrigin->SetBorderSize(0);
 l20_DPhiOrigin->AddEntry("", "(e)", "");
 TLegend* l21_DPhiOrigin = new TLegend(0.25-0.20, 0.81+0.03, 0.30-0.20, 0.86+0.03);
 l21_DPhiOrigin->SetTextSize(0.055);
 l21_DPhiOrigin->SetBorderSize(0);
 l21_DPhiOrigin->AddEntry("", "(f)", "");
 
 // low-low prompt/prompt
 histDPhiMakeUp(hDpDmOriginLLPr, kBlue, 1e-4, 2e-1);
 hDpDmOriginLLPr->SetMaximum(3e-1);
 hDpDmOriginLLPr->SetMinimum(7e-5);
 hDpDmOriginLLPr->GetXaxis()->SetTitle("");
 hDpDmOriginLLPr->GetYaxis()->SetNdivisions(5);
 // hDpDmOriginLLPr->GetYaxis()->SetTitleOffset(3);
 c00_DPhiOrigin->cd();
 gPad->SetTicky();
 gPad->SetLogy();
 hDpDmOriginLLPr->Draw("hist E");
 l00_DPhiOrigin->Draw();

 // low-low non-prompt/non-prompt
 histDPhiMakeUp(hDpDmOriginLLSc, kBlue, 1e-4, 2e-1);
 hDpDmOriginLLSc->SetMaximum(3e-1);
 hDpDmOriginLLSc->SetMinimum(7e-5);
 hDpDmOriginLLSc->GetXaxis()->SetTitle("");
 hDpDmOriginLLSc->GetYaxis()->SetTitle("");
 hDpDmOriginLLSc->GetYaxis()->SetNdivisions(5);
 c10_DPhiOrigin->cd();
 gPad->SetTickx();
 gPad->SetTicky();
 gPad->SetLogy();
 hDpDmOriginLLSc->Draw("hist E");
 l10_DPhiOrigin->Draw();

 // low-low prompt/non-prompt + vv
 histDPhiMakeUp(hDpDmOriginLLPrSc, kBlue, 1e-4, 2e-1);
 hDpDmOriginLLPrSc->SetMaximum(3e-1);
 hDpDmOriginLLPrSc->SetMinimum(7e-5);
 hDpDmOriginLLPrSc->GetXaxis()->SetTitle("");
 hDpDmOriginLLPrSc->GetYaxis()->SetTitle("");
 hDpDmOriginLLPrSc->GetYaxis()->SetNdivisions(5);
 c20_DPhiOrigin->cd();
 gPad->SetTickx();
 gPad->SetTicky();
 gPad->SetLogy();
 hDpDmOriginLLPrSc->Draw("hist E");
 l20_DPhiOrigin->Draw();

 // high-high prompt/prompt
 histDPhiMakeUp(hDpDmOriginHHPr, kBlue, 1e-4, 2e-1);
 hDpDmOriginHHPr->SetMaximum(3e-1);
 hDpDmOriginHHPr->SetMinimum(7e-5);
 hDpDmOriginHHPr->GetXaxis()->SetTitle("");
 hDpDmOriginHHPr->GetYaxis()->SetNdivisions(5);
 c01_DPhiOrigin->cd();
 gPad->SetLogy();
 hDpDmOriginHHPr->Draw("hist E");
 l01_DPhiOrigin->Draw();
 l01_DPhiOriginLabels->Draw();

 // high-high non-prompt/non-prompt
 histDPhiMakeUp(hDpDmOriginHHSc, kBlue, 1e-4, 2e-1);
 hDpDmOriginHHSc->SetMaximum(3e-1);
 hDpDmOriginHHSc->SetMinimum(7e-5);
 hDpDmOriginHHSc->GetXaxis()->SetTitle("");
 hDpDmOriginHHSc->GetYaxis()->SetNdivisions(5);
 c11_DPhiOrigin->cd();
 gPad->SetTickx();
 gPad->SetLogy();
 hDpDmOriginHHSc->Draw("hist E");
 l11_DPhiOrigin->Draw();

 // high-high prompt/non-prompt + vv
 histDPhiMakeUp(hDpDmOriginHHPrSc, kBlue, 1e-4, 2e-1);
 hDpDmOriginHHPrSc->SetMaximum(3e-1);
 hDpDmOriginHHPrSc->SetMinimum(7e-5);
 hDpDmOriginHHPrSc->GetYaxis()->SetNdivisions(5);
 c21_DPhiOrigin->cd();
 gPad->SetTickx();
 gPad->SetLogy();
 hDpDmOriginHHPrSc->Draw("hist E");
 l21_DPhiOrigin->Draw();
 
 if (write) {
   c3x2_DPhiOrigin->SaveAs("Plots/c3x2_DPhiOrigin_214.pdf");
   c3x2_DPhiOrigin->SaveAs("Plots/c3x2_DPhiOrigin_214.png");
 }

 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 // ANGULAR CORRELATIONS AS FUNCTION OF PT
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////
 ////////////////////////////////////////////////////////////////////////////////////

 // Study that compares beauty and charm for low-low, int-int and high-high pT regions
 // Works for both 214 and 215
 std::string path_bb = Form("/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_%s/", writeName);
 std::string path_cc = Form("/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_%s/", writeName);

 TFile* hBpBm_File = new TFile((path_bb + "BplusBminus.root").c_str());
 TH1D* hBpBmLL = (TH1D*)hBpBm_File->Get("hDPhiLL");
 TH1D* hBpBmTrPtLL = (TH1D*)hBpBm_File->Get("hTrPtL");
 hBpBmLL->Scale(1/hBpBmTrPtLL->Integral());

 TH1D* hBpBmII = (TH1D*)hBpBm_File->Get("hDPhiII");
 TH1D* hBpBmTrPtII = (TH1D*)hBpBm_File->Get("hTrPtI");
 hBpBmII->Scale(1/hBpBmTrPtII->Integral());

 TH1D* hBpBmHH = (TH1D*)hBpBm_File->Get("hDPhiHH");
 TH1D* hBpBmTrPtHH = (TH1D*)hBpBm_File->Get("hTrPtH"); 
 hBpBmHH->Scale(1/hBpBmTrPtHH->Integral());

 TFile* hDpDm_File = new TFile((path_cc + "DplusDminus.root").c_str());
 TH1D* hDpDmLL = (TH1D*)hDpDm_File->Get("hDPhiLL");
 TH1D* hDpDmTrPtLL = (TH1D*)hDpDm_File->Get("hTrPtL");
 hDpDmLL->Scale(1/hDpDmTrPtLL->Integral());

 TH1D* hDpDmII = (TH1D*)hDpDm_File->Get("hDPhiII");
 TH1D* hDpDmTrPtII = (TH1D*)hDpDm_File->Get("hTrPtI"); 
 hDpDmII->Scale(1/hDpDmTrPtII->Integral());

 TH1D* hDpDmHH = (TH1D*)hDpDm_File->Get("hDPhiHH");
 TH1D* hDpDmTrPtHH = (TH1D*)hDpDm_File->Get("hTrPtH");
 hDpDmHH->Scale(1/hDpDmTrPtHH->Integral());

 TCanvas* c2x3_DPhi_pT = new TCanvas("c2x3_Dphi_pTH", "DPhi with pT dependence for B+B- and D+D- on 2x3 canvas", 1200, 1000);
 setCanvasMargins(c2x3_DPhi_pT, 0.20, 0.1, 0.1, 0.05);
 c2x3_DPhi_pT->cd();
 TPad* c00_DPhiLL = new TPad("c00_DPhiLL", "DPhi for pT LL for B+B-", 0.05, 0.50, 0.38, 0.95);
 c00_DPhiLL->SetLeftMargin(0.22);
 c00_DPhiLL->SetRightMargin(eps);
 c00_DPhiLL->SetBottomMargin(eps);
 c00_DPhiLL->Draw();
 TPad* c01_DPhiII = new TPad("c01_DPhiII", "DPhi for pT II for B+B-", 0.38+eps, 0.50, 0.65, 0.95);
 c01_DPhiII->SetLeftMargin(0);
 c01_DPhiII->SetRightMargin(eps);
 c01_DPhiII->SetBottomMargin(eps);
 c01_DPhiII->Draw();
 TPad* c02_DPhiHH = new TPad("c02_DPhiHH", "DPhi for pT HH for B+B-", 0.65+eps, 0.50, 0.95, 0.95);
 c02_DPhiHH->SetLeftMargin(0);
 c02_DPhiHH->SetBottomMargin(eps);
 c02_DPhiHH->Draw();
 TPad* c10_DPhiLL = new TPad("c10_DPhiLL", "DPhi for pT LL for D+D-", 0.05, 0.05, 0.38, 0.50+eps);
 c10_DPhiLL->SetLeftMargin(0.22);
 c10_DPhiLL->SetRightMargin(eps);
 c10_DPhiLL->SetTopMargin(0);
 c10_DPhiLL->Draw();
 TPad* c11_DPhiII = new TPad("c11_DPhiII", "DPhi for pT II for D+D-", 0.38+eps, 0.05, 0.65, 0.50+eps);
 c11_DPhiII->SetLeftMargin(0);
 c11_DPhiII->SetRightMargin(eps);
 c11_DPhiII->SetTopMargin(0);
 c11_DPhiII->Draw();
 TPad* c12_DPhiHH = new TPad("c12_DPhiHH", "DPhi for pT HH for D+D-", 0.65+eps, 0.05, 0.95, 0.50+eps);
 c12_DPhiHH->SetLeftMargin(0);
 c12_DPhiHH->SetTopMargin(0);
 c12_DPhiHH->Draw();
 
 // Low-low BpBm
 histDPhiMakeUp(hBpBmLL, kRed, 1e-5, 1e-1); // 0.0001
 hBpBmLL->SetMaximum(1.5e-1);
 hBpBmLL->SetMinimum(8e-6);
 hBpBmLL->GetXaxis()->SetTitle("");
 // hBpBmLL->GetYaxis()->SetTitleOffset(3);
 // hBpBmLL->GetYaxis()->SetNdivisions(5);
 c00_DPhiLL->cd();
 gPad->SetLogy();
 gPad->SetTicky();
 hBpBmLL->Draw("hist E");
 
 // Int-int BpBm
 histDPhiMakeUp(hBpBmII, kRed, 1e-5, 1e-1);
 hBpBmII->SetMaximum(1.5e-1);
 hBpBmII->SetMinimum(8e-6);
 hBpBmII->GetXaxis()->SetTitle("");
 // hBpBmII->GetYaxis()->SetNdivisions(5);
 c01_DPhiII->cd();
 gPad->SetLogy();
 gPad->SetTicky();
 hBpBmII->Draw("hist E");
 
 // High-high BpBm
 histDPhiMakeUp(hBpBmHH, kRed, 1e-5, 1e-1);
 hBpBmHH->SetMaximum(1.5e-1);
 hBpBmHH->SetMinimum(8e-6);
 hBpBmHH->GetXaxis()->SetTitle("");
 // hBpBmHH->GetYaxis()->SetNdivisions(5);
 c02_DPhiHH->cd(); 
 gPad->SetLogy();
 hBpBmHH->Draw("hist E");
 
 // Low-low DpDm
 histDPhiMakeUp(hDpDmLL, kBlue, 1e-5, 1e-1);
 hDpDmLL->SetMaximum(1.5e-1);
 hDpDmLL->SetMinimum(8e-6);
 hDpDmLL->GetXaxis()->SetTitle("");
 hDpDmLL->GetYaxis()->SetTitle("");
 // hDpDmLL->GetYaxis()->SetTitleOffset(3);
 c10_DPhiLL->cd();
 gPad->SetLogy();
 gPad->SetTicky();
 gPad->SetTickx();
 hDpDmLL->Draw("hist E");
 
 // Int-int DpDm
 histDPhiMakeUp(hDpDmII, kBlue, 1e-5, 1e-1);
 hDpDmII->SetMaximum(1.5e-1);
 hDpDmII->SetMinimum(8e-6);
 hDpDmII->GetXaxis()->SetTitle("");
 c11_DPhiII->cd();
 gPad->SetLogy();
 gPad->SetTicky();
 gPad->SetTickx();
 hDpDmII->Draw("hist E");
 
 // High-high DpDm
 histDPhiMakeUp(hDpDmHH, kBlue, 1e-5, 1e-1);
 hDpDmHH->SetMaximum(1.5e-1);
 hDpDmHH->SetMinimum(8e-6);
 // hDpDmHH->GetXaxis()->SetTitle("");
 c12_DPhiHH->cd();
 gPad->SetLogy();
 gPad->SetTickx();
 hDpDmHH->Draw("hist E");
 
 TLegend* lhists_DPhi_pT = new TLegend(0.30, 0.6, 0.50, 0.75);
 lhists_DPhi_pT->SetTextSize(0.05);
 lhists_DPhi_pT->SetBorderSize(0);
 // lhists_DPhi_pTH->SetLineWidth(2);
 lhists_DPhi_pT->SetMargin(0.5);
 lhists_DPhi_pT->AddEntry(hBpBm, "B^{+}B^{-}", "l");
 lhists_DPhi_pT->AddEntry(hDpDm, "D^{+}D^{-}", "l");
 TLegend* l00_DPhiLL = new TLegend(0.25, 0.75, 0.40, 0.8);
 l00_DPhiLL->SetTextSize(0.05);
 l00_DPhiLL->SetBorderSize(0);
 l00_DPhiLL->AddEntry("", "(a) pT < 3 GeV ", "");
 TLegend* l01_DPhiII = new TLegend(0.25-0.1, 0.75, 0.40-0.1, 0.8);
 l01_DPhiII->SetTextSize(0.055);
 l01_DPhiII->SetBorderSize(0);
 l01_DPhiII->AddEntry("", "(b) 3 < pT < 8 GeV", "");
 TLegend* l02_DPhiHH = new TLegend(0.25-0.1, 0.75, 0.40-0.1, 0.8);
 l02_DPhiHH->SetTextSize(0.05);
 l02_DPhiHH->SetBorderSize(0);
 l02_DPhiHH->AddEntry("", "(c) pT > 8 GeV", "");
 TLegend* l10_DPhiLL = new TLegend(0.25, 0.75+0.1, 0.40, 0.8+0.1);
 l10_DPhiLL->SetTextSize(0.05);
 l10_DPhiLL->SetBorderSize(0);
 l10_DPhiLL->AddEntry("", "(d) pT < 3 GeV", "");
 TLegend* l11_DPhiII = new TLegend(0.25-0.1, 0.75+0.1, 0.40-0.1, 0.8+0.1);
 l11_DPhiII->SetTextSize(0.055);
 l11_DPhiII->SetBorderSize(0);
 l11_DPhiII->AddEntry("", "(e) 3 < pT < 8 GeV", "");
 TLegend* l12_DPhiHH = new TLegend(0.25-0.1, 0.75+0.1, 0.40-0.1, 0.8+0.1);
 l12_DPhiHH->SetTextSize(0.05);
 l12_DPhiHH->SetBorderSize(0);
 l12_DPhiHH->AddEntry("", "(f) pT > 8 GeV", "");
 
 c00_DPhiLL->cd(); lhists_DPhi_pT->Draw(); l00_DPhiLL->Draw();
 c01_DPhiII->cd(); l01_DPhiII->Draw();
 c02_DPhiHH->cd(); l02_DPhiHH->Draw();
 c10_DPhiLL->cd(); l10_DPhiLL->Draw();
 c11_DPhiII->cd(); l11_DPhiII->Draw();
 c12_DPhiHH->cd(); l12_DPhiHH->Draw();
 
 if (write) {
   c2x3_DPhi_pT->SaveAs(Form("Plots/c2x3_DPhi_pT_Dependence_%s.pdf", writeName));
   c2x3_DPhi_pT->SaveAs(Form("Plots/c2x3_DPhi_pT_Dependence_%s.png", writeName));
 }
  
} // END of HarryPlotter

// Function that takes the input ROOT paths and histogram names to create vectors with all
// histograms to be used in the plotting function above.
std::vector<HistAndLabels> configureInput(std::string path,
					  std::vector<RootFileAndLabels> vRootFileAndLabels,
					  std::vector<HistNameAndLabels> vHistNameAndLabels) {
  // Returns vector: LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateName, OSHist, SSHist, DrawYmin, DrawYmax
  // This vector is used in the function above to couple settings and histograms together in order
  // to automise the plotting procedure.

  // const char* CombinedLegendTitle;
  std::vector<HistAndLabels> vHistAndLabels;
  // *** HistLegendTitle, Color, LineStyle, LineWidth, Hist ***
  // To be filled in for loops below

  for (int i = 0; i < vRootFileAndLabels.size(); i++) { // associate loop

    RootFileAndLabels rootEntry = vRootFileAndLabels[i];

    TFile* OStree = new TFile((path + rootEntry.OSRootFile).c_str());
    TFile* SStree = new TFile((path + rootEntry.SSRootFile).c_str());

    for (int k = 0; k < vHistNameAndLabels.size(); k++) { // dependencies loop
      // (k is used instead of j to keep consistency with the definition in the
      // balancing plotting macro)
      
      HistNameAndLabels histEntry = vHistNameAndLabels[k];
      
      // *** ------fill vector with histograms -------- ***
      
      // std::cout << "i, j, k = " << i << ", " << j << ", " << k << std::endl;
      
      TH1D* hDPhiOS = (TH1D*)OStree->Get(histEntry.HistName);
      TH1D* hDPhiSS = (TH1D*)SStree->Get(histEntry.HistName);
      TH1D* hTrPtOS = (TH1D*)OStree->Get(histEntry.TrPtName);
      TH1D* hTrPtSS = (TH1D*)SStree->Get(histEntry.TrPtName);
      
      if (strcmp(rootEntry.TriggerName, rootEntry.AssociateNameSS) == 0) { hDPhiSS->Scale(0.5); } // Prevent double-counting
      
      // std::cout << "trigger pT hist name = " << histEntry.TrPtName << std::endl;
      
      hDPhiOS->Scale(1/hTrPtOS->Integral());
      hDPhiSS->Scale(1/hTrPtSS->Integral());
      
      vHistAndLabels.push_back({
	  histEntry.LegendTitle, histEntry.Color, histEntry.LineStyle, histEntry.LineWidth,
	  rootEntry.TriggerName, rootEntry.AssociateNameOS, rootEntry.AssociateNameSS,
	  hDPhiOS, hDPhiSS,
	  rootEntry.DrawYmin, rootEntry.DrawYmax
	});
      
    } // k
    
  } // i
  
  return vHistAndLabels;
  
} // END OF configureInput()

int combinedCanvasPlots() {
  // Main macro, configureInput is given inputs and the main plotting function, HarryPlotter()
  // is called here
  
  std::vector<RootFileAndLabels> vRootFileAndLabels;
  std::vector<HistNameAndLabels> vHistNameAndLabels;

  std::string path_bb_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_214/";
  std::string path_bb_215 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_215/";
  
  // *** LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateNameOS, AssociateNameSS, OSRootFile, SSRootFile, DrawYmin, DrawYmax ***
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "B^{-}", "B^{+}", "BplusBminus.root", "BplusBplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "B_{c}^{-}", "B_{c}^{+}", "BplusBcminus.root", "BplusBcplus.root", 1e-8, 1e-2});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#barB^{0}", "B^{0}", "BplusBzerobar.root", "BplusBzero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#barB_{s}^{0}", "B_{s}^{0}", "BplusBszerobar.root", "BplusBszero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Lambda_{b}^{0}", "#bar#Lambda_{b}^{0}", "BplusLb.root", "BplusLbbar.root", 1e-8, 1e-2});
  
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{+}", "#bar#Sigma_{b}^{+}", "BplusSigmabplus.root", "BplusSigmabplusbar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{0}", "#bar#Sigma_{b}^{0}", "BplusSigmabzero.root", "BplusSigmabzerobar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{-}", "#bar#Sigma_{b}^{-}", "BplusSigmabminus.root", "BplusSigmabminusbar.root", 1e-8, 1e-2});

  vHistNameAndLabels.push_back({"all bins", kBlack, 1, 2, "hDPhi", "hTrPt"});

  std::vector<HistAndLabels> vhBpAs = configureInput(path_bb_215,
						     vRootFileAndLabels,
						     vHistNameAndLabels);

  vHistNameAndLabels.clear();

  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"80-100 % multiplicity bin", kBlack, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 % multiplicity bin", kBlack, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 % multiplicity bin", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 % multiplicity bin", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 % multiplicity bin", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5 % multiplicity bin", kBlack, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"0-1 % multiplicity bin", kBlack, 4, 3, "hDPhiM1", "hTrPtM1"});

  std::vector<HistAndLabels> vhBpAsMult = configureInput(path_bb_215,
						     vRootFileAndLabels,
						     vHistNameAndLabels);
  
  vHistNameAndLabels.clear();

  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //
  // -------------------------------------------------------------- //

  std::string path_cc_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_214/";
  std::string path_cc_215 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_215/";

  vRootFileAndLabels.clear();
  
  // *** LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateNameOS, AssociateNameSS, OSRootFile, SSRootFile, DrawYmin, DrawYmax ***
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "D^{-}", "D^{+}", "DplusDminus.root", "DplusDplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "D_{s}^{-}", "D_{s}^{+}", "DplusDsminus.root", "DplusDsplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#barD^{0}", "D^{0}", "DplusDzerobar.root", "DplusDzero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Lambda_{c}^{+}", "#Lambda_{c}^{+}", "DplusLambdacplusbar.root", "DplusLambdacplus.root", 1e-8, 1e-2});
  
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{++}", "#Sigma_{c}^{++}", "DplusSigmacplusplusbar.root", "DplusSigmacplusplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{+}", "#Sigma_{c}^{+}", "DplusSigmacplusbar.root", "DplusSigmacplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{0}", "#Sigma_{c}^{0}", "DplusSigmaczerobar.root", "DplusSigmaczero.root", 1e-8, 1e-2});

  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"all bins", kBlue, 1, 2, "hDPhi", "hTrPt"});

  std::vector<HistAndLabels> vhDpAs = configureInput(path_cc_215,
						     vRootFileAndLabels,
						     vHistNameAndLabels);

  vHistNameAndLabels.clear();

  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"80-100 % multiplicity bin", kBlue, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 % multiplicity bin", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 % multiplicity bin", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 % multiplicity bin", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 % multiplicity bin", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5 % multiplicity bin", kRed, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"0-1 % multiplicity bin", kRed, 4, 3, "hDPhiM1", "hTrPtM1"});

  std::vector<HistAndLabels> vhDpAsMult = configureInput(path_cc_215,
						     vRootFileAndLabels,
						     vHistNameAndLabels);
  
  vHistNameAndLabels.clear();

  //////////////
  // PLOTTING //
  // PLOTTING //
  // PLOTTING //
  // PLOTTING //
  //////////////

  bool write = false;
  const char* writeName = "215";
  // MAKE SURE this is equal to the path which is used above (e.g. path_bb_215 and path_cc_215 for "215")
  
  HarryPlotter(vhBpAs,
	       vhBpAsMult,
	       vhDpAs,
	       vhDpAsMult,
	       write,
	       writeName);
  
  return 0;
}
