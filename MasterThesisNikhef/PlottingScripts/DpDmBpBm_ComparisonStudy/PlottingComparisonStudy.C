// PlottingComparisonStudy.C
// ROOT Macro that draws azimuthal angular correlations for B+B- and D+D- pairs for different pT constraints for both the trigger and associate particle and then compares the correlations by dividing.
// The code is set up in such a way that it is straight-forward to change the input ROOT files and pT regions to draw.

// The histograms are normalised by the number of triggers, which is obtained by integrating the trigger spectrum
void normalise(TH1D *hist, TH1D *trig, Double_t xmin, Double_t xmax){
	Int_t bin_start = trig->FindBin(xmin);
	Int_t bin_finish = trig->FindBin(xmax);
	Double_t integral = trig->Integral(bin_start, bin_finish);
	hist->Scale(1./integral);
}

// This struct is used to define make-up settings already when the histogram is given as argument to the readTree function
struct NormalisedHistogramAndLabels {
  TH1D* NormalisedHistogram;
  const char* LegendName;
  Color_t Color;
  Int_t LineStyle;
  Double_t LineWidth;
};

// The canvas margins are standardised in this way for every function call
void setCanvasMargins(TCanvas *canvas, double_t LeftMargin, double_t RightMargin, double_t TopMargin, double_t BottomMargin) {
  canvas->SetLeftMargin(LeftMargin);
  canvas->SetRightMargin(RightMargin);
  canvas->SetTopMargin(TopMargin);
  canvas->SetBottomMargin(BottomMargin);
}

// The readTree function draws the B+B- and D+D- histograms it gets as arguments in a vector of the struct NormalisedHistogramAndLabels, which enables the user to change make-up settings when calling the function.
// The write option can be enabled to save the output canvas as PDF.
// The Y range options are used to set the Y-axis range on the mainpad or minipad.
void readTree(vector<NormalisedHistogramAndLabels> vNormalisedHistogramsAndLabelsBpBm,
	      vector<NormalisedHistogramAndLabels> vNormalisedHistogramsAndLabelsDpDm,
	      const char* plotTitle,
	      bool write,
	      Double_t mainYmin = 0, Double_t mainYmax = 0,
	      Double_t miniYmin = 0, Double_t miniYmax = 0) {

  // Define canvas and legends
  TCanvas* mainCanvas = new TCanvas(Form("c_%s", plotTitle), Form("c_%s", plotTitle), 800, 600);
  setCanvasMargins(mainCanvas, 0.20, 0.05, 0.10, 0.15);
  mainCanvas->cd();
  TPad *mainPad = new TPad("mainPad", "Main", 0.03, 0.3, 1.0, 1.0);
  mainPad->SetLogy();
  mainPad->Draw();
  TLegend* mainLegend = new TLegend(0.58, 0.17, 0.78, 0.37);
  mainLegend->SetBorderSize(0); mainLegend->SetTextSize(0.03);
  TLegend* miniLegend = new TLegend(0.72, 0.17, 0.83, 0.37);
  miniLegend->SetBorderSize(0); miniLegend->SetTextSize(0.03);

  // Need a way to change the order of entries in the legend
  // Can in principle also be done by creating two seperate legends
  std::map<const char*, TH1D*> LegendEntriesBpBm; 
  std::map<const char*, TH1D*> LegendEntriesDpDm;

  // miniPad is scaled down, so we need to modifiy the text size
  // Simultaneously also define the text size for the mainPad
  Double_t textSize = 0.04;
  Double_t textSizeMod = 1.8;
  
  // Define miniPad for ratio plot
  // Pad initialised with xLow, yLow, xUp, yUp
  TPad *miniPad = new TPad("miniPad", "Ratio", 0.03, 0.0, 1.0, 0.3);
  miniPad->SetLogy();
  miniPad->Draw();

  // Template histograms to set titles, etc. (for mainpad and minipad)
  TH1D* hTEMPLATE_MAIN = new TH1D("hTEMPLATE_MAIN", "hTEMPLATE_MAIN", 100, -1.57, 4.71);
  TH1D* hTEMPLATE_MINI = new TH1D("hTEMPLATE_MINI", "hTEMPLATE_MINI", 100, -1.57, 4.71);
  
  // hTEMPLATE_MAIN->SetTitle(plotTitle);
  hTEMPLATE_MAIN->SetTitle("");
  hTEMPLATE_MAIN->GetXaxis()->SetTitleSize(textSize);
  hTEMPLATE_MAIN->GetYaxis()->SetTitle("#frac{1}{N_{trigger}} #frac{dN}{d#Delta#phi}");
  hTEMPLATE_MAIN->GetYaxis()->SetTitleSize(textSize);
  hTEMPLATE_MAIN->GetYaxis()->SetRangeUser(mainYmin, mainYmax);
  // hTEMPLATE_MAIN->GetYaxis()->SetTitleOffset(0.95);
  hTEMPLATE_MAIN->SetStats(0);
  
  // And for minipad
  hTEMPLATE_MINI->SetTitle("");
  hTEMPLATE_MINI->SetTitleSize(textSize * textSizeMod); // miniPad is scaled c.f. mainPad
  hTEMPLATE_MINI->GetXaxis()->SetTitle("");
  hTEMPLATE_MINI->GetXaxis()->SetLabelSize(textSize * textSizeMod);
  hTEMPLATE_MINI->GetYaxis()->SetTitle("B^{+}B^{-} / D^{+}D^{-}");
  hTEMPLATE_MINI->GetYaxis()->SetLabelSize(textSize * textSizeMod); 
  hTEMPLATE_MINI->GetYaxis()->SetTitleSize(textSize * textSizeMod);
  hTEMPLATE_MINI->GetYaxis()->SetTitleOffset(0.45);
  hTEMPLATE_MINI->GetYaxis()->SetRangeUser(miniYmin, miniYmax);
  hTEMPLATE_MINI->SetStats(0);

  mainPad->cd(); hTEMPLATE_MAIN->Draw("hist E");
  miniPad->cd(); hTEMPLATE_MINI->Draw("hist E");
  
  // Main loop over inputs
  // The inputs are given with an input ROOT file name and associated labels to be plotted
  // In this script all ratios are given as BpBm / DpDm
  for (Int_t i = 0; i < vNormalisedHistogramsAndLabelsBpBm.size(); i++) {

    TH1D* hBpBm = vNormalisedHistogramsAndLabelsBpBm[i].NormalisedHistogram;
    TH1D* hDpDm = vNormalisedHistogramsAndLabelsDpDm[i].NormalisedHistogram;

    // Calculate ratios and set up ratio histograms for miniPad
    TH1D* hDiv = (TH1D*)hBpBm->Clone("hDiv");
    hDiv->Divide(hDpDm);

    // Draw histogram on canvas with corresponding colors from input
    hBpBm->SetLineColor(vNormalisedHistogramsAndLabelsBpBm[i].Color);
    hBpBm->SetLineStyle(vNormalisedHistogramsAndLabelsBpBm[i].LineStyle);
    hBpBm->SetLineWidth(vNormalisedHistogramsAndLabelsBpBm[i].LineWidth);
    //
    hDpDm->SetLineColor(vNormalisedHistogramsAndLabelsDpDm[i].Color);
    hDpDm->SetLineStyle(vNormalisedHistogramsAndLabelsDpDm[i].LineStyle);
    hDpDm->SetLineWidth(vNormalisedHistogramsAndLabelsDpDm[i].LineWidth);
    //
    hDiv->SetLineColor(kBlack);
    hDiv->SetLineStyle(vNormalisedHistogramsAndLabelsBpBm[i].LineStyle);
    hDiv->SetLineWidth(vNormalisedHistogramsAndLabelsBpBm[i].LineWidth);
  
    mainPad->cd();
    hBpBm->Draw("same hist E"); hDpDm->Draw("same hist E");

    mainLegend->AddEntry(hBpBm, Form("B^{+}B^{-} (%s)", vNormalisedHistogramsAndLabelsBpBm[i].LegendName));
    mainLegend->AddEntry(hDpDm, Form("D^{+}D^{-} (%s)", vNormalisedHistogramsAndLabelsDpDm[i].LegendName));
    miniLegend->AddEntry(hDiv, vNormalisedHistogramsAndLabelsBpBm[i].LegendName);
    
    miniPad->cd();
    hDiv->Draw("same hist E");
    
  } // for-loop over input vector

  mainPad->cd();
  mainLegend->Draw();
  miniLegend->Draw();

  if (write) {
    mainCanvas->SaveAs(Form("Plots/cMatching_DpDmBpBm_Comparison_%s.pdf", plotTitle));
  }
  
} // readTree

int PlottingComparisonStudy() {

  std::vector<const char*> vptRegimes = {"hDPhiLL", "hDPhiIL", "hDPhiHL", "hDPhiII", "hDPhiHI", "hDPhiHH"};

  TFile* RootFileBpBm = new TFile("../RootFiles/BplusBminus_80.root", "READ");
  TFile* RootFileDpDm = new TFile("../RootFiles/DplusDminus_60.root", "READ");
  
  std::map<const char*, TH1D*> mapNormalisedHistogramsBpBm; 
  std::map<const char*, TH1D*> mapNormalisedHistogramsDpDm;

  for (auto& ptRegime : vptRegimes) {
    
    TH1D* hDPhiBpBm = (TH1D*)RootFileBpBm->Get(ptRegime);
    TH1D* hDPhiDpDm = (TH1D*)RootFileDpDm->Get(ptRegime);
    TH1D* hTrPtBpBm = (TH1D*)RootFileBpBm->Get("hTrPt");
    TH1D* hTrPtDpDm = (TH1D*)RootFileDpDm->Get("hTrPt");

    // Integrate from -pi/2 to +3pi/2
    normalise(hDPhiBpBm, hTrPtBpBm, -1.57, 4.71);
    normalise(hDPhiDpDm, hTrPtDpDm, -1.57, 4.71);

    mapNormalisedHistogramsBpBm[ptRegime] = hDPhiBpBm;
    mapNormalisedHistogramsDpDm[ptRegime] = hDPhiDpDm;
    
  } // for-loop over ptRegimes
    
  /*
  struct NormalisedHistogramAndLabels {
    TH1D* NormalisedHistogram;
    const char* LegendName;
    Color_t Color;
    Int_t LineStyle;
    Double_t LineWidth;
  };
  */

  // Initialisation can be changed and ROOT files can be added with different characteristics to compare for DpDm and BpBm
  std::vector<NormalisedHistogramAndLabels> vNormalisedHistogramsAndLabelsBpBm;
  vNormalisedHistogramsAndLabelsBpBm.push_back({mapNormalisedHistogramsBpBm["hDPhiLL"], "LL", kRed, 0, 3});
  vNormalisedHistogramsAndLabelsBpBm.push_back({mapNormalisedHistogramsBpBm["hDPhiII"], "II", kRed, 5, 2});
  vNormalisedHistogramsAndLabelsBpBm.push_back({mapNormalisedHistogramsBpBm["hDPhiHH"], "HH", kRed, 3, 2});
  // ...
  std::vector<NormalisedHistogramAndLabels> vNormalisedHistogramsAndLabelsDpDm;
  vNormalisedHistogramsAndLabelsDpDm.push_back({mapNormalisedHistogramsDpDm["hDPhiLL"], "LL", kBlue, 0, 3});
  vNormalisedHistogramsAndLabelsDpDm.push_back({mapNormalisedHistogramsDpDm["hDPhiII"], "II", kBlue, 5, 2});
  vNormalisedHistogramsAndLabelsDpDm.push_back({mapNormalisedHistogramsDpDm["hDPhiHH"], "HH", kBlue, 3, 2});
  // ...
  
  // One option to write them all
  bool write = false;

   /*
  void readTree(vector<RootFileAndLabels> vRootFileAndLabels,
	      const char* plotTitle,
	      bool write,
	      Double_t mainYmin = 0, Double_t mainYmax = 0,
	      Double_t miniYmin = 0, Double_t miniYmax = 0) {}
  */
  
  readTree(vNormalisedHistogramsAndLabelsBpBm,
	   vNormalisedHistogramsAndLabelsDpDm,
	   "B^{+}B^{-} and D^{+}D^{-} angular correlations",
	   write,
	   1e-7, 1e-2,
	   1e-1, 2e2);
  
  return 0;
}
