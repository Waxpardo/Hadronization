// ProductionOriginStudy.C
// ROOT macro that plots azimuthal angular correlations of D+D- pairs in a certain pT region and based on the production origin of the trigger (D+) and associate (D-), which can be prompt (hadronisation) or non-prompt (decay).
// The script is set up in such a way that it should be straight-forward to append different pT regions or correlation pairs or modify parts of the code.

// The histograms are normalised by the number of triggers, which is obtained by integrating the trigger spectrum
void normalise(TH1D* hist, TH1D* trig, Double_t xmin, Double_t xmax) {
	Int_t bin_start = trig->FindBin(xmin);
	Int_t bin_finish = trig->FindBin(xmax);
	Double_t integral = trig->Integral(bin_start, bin_finish);
	hist->Scale(1./integral);
}

// This struct is used to define make-up settings already when the ROOT file is given as an argument to the readTree function
struct HistogramAndLabels {
  const char* HistFile;
  const char* HistTitle;
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

// The readTree function draws the D+D- histograms based on the production origin
// Pr = primary = prompt
// Sc = secondary = non-prompt
// PrSc = prompt trigger/non-prompt associate or vice-versa
// The write option can be enabled in order to save the output canvas as PDF
void readTree(vector<HistogramAndLabels> HistogramAndLabelsPrVector, vector<HistogramAndLabels> HistogramAndLabelsScVector, vector<HistogramAndLabels> HistogramAndLabelsPrScVector,
	      bool write,
	      Double_t Ymin, Double_t Ymax) {

  TFile* rootFile = new TFile("../RootFiles/DplusDminus_60_prompt_non_prompt.root");

  TCanvas* canvas = new TCanvas("name", "title", 800, 600);
  setCanvasMargins(canvas, 0.20, 0.05, 0.10, 0.15);
  TLegend* legend = new TLegend(0.58, 0.18, 0.78, 0.38);
  legend->SetBorderSize(0);
  legend->SetTextSize(0.03);
  canvas->cd();
  gPad->SetLogy();

  TH1D* hTrPtPr = (TH1D*)rootFile->Get("hTrPtPr");
  TH1D* hTrPtSc = (TH1D*)rootFile->Get("hTrPtSc");
  TH1D* hTrPtPrSc = (TH1D*)rootFile->Get("hTrPtPrSc");

  TH1D* hTEMPLATE = new TH1D("hTEMPLATE", "hTEMPLATE", 100, -1.57, 4.71);
  // hTEMPLATE->SetTitle("#Delta#phi correlations trigger D^{+}D^{-}");
  hTEMPLATE->SetTitle("");
  hTEMPLATE->GetYaxis()->SetTitle("#frac{1}{N_{trigger}} #frac{dN}{d#Delta#phi}");
  hTEMPLATE->GetYaxis()->SetRangeUser(Ymin, Ymax);
  hTEMPLATE->SetStats(0);
  hTEMPLATE->Draw("hist E");
  
  for (int i = 0 ; i < HistogramAndLabelsPrVector.size() ; i++) {
    
    TH1D* hDPhiPr = (TH1D*)rootFile->Get(HistogramAndLabelsPrVector[i].HistFile); // from decay (non-prompt)
    TH1D* hDPhiSc = (TH1D*)rootFile->Get(HistogramAndLabelsScVector[i].HistFile); // from hadronisation (prompt)
    TH1D* hDPhiPrSc = (TH1D*)rootFile->Get(HistogramAndLabelsPrScVector[i].HistFile); // from decay/hadronisation (non-prompt/prompt)

    // Integrate from -pi/2 to +3pi/2
    normalise(hDPhiPr, hTrPtPr, -1.57, 4.71);
    normalise(hDPhiSc, hTrPtSc, -1.57, 4.71);
    normalise(hDPhiPrSc, hTrPtPrSc, -1.57, 4.71);

    hDPhiPr->SetLineColor(HistogramAndLabelsPrVector[i].Color);
    hDPhiPr->SetLineStyle(HistogramAndLabelsPrVector[i].LineStyle);
    hDPhiPr->SetLineWidth(HistogramAndLabelsPrVector[i].LineWidth);
    hDPhiPr->Draw("same hist E");
    
    hDPhiSc->SetLineColor(HistogramAndLabelsScVector[i].Color);
    hDPhiSc->SetLineStyle(HistogramAndLabelsScVector[i].LineStyle);
    hDPhiSc->SetLineWidth(HistogramAndLabelsScVector[i].LineWidth);
    hDPhiSc->Draw("same hist E");

    hDPhiPrSc->SetLineColor(HistogramAndLabelsPrScVector[i].Color);
    hDPhiPrSc->SetLineStyle(HistogramAndLabelsPrScVector[i].LineStyle);
    hDPhiPrSc->SetLineWidth(HistogramAndLabelsPrScVector[i].LineWidth);
    hDPhiPrSc->Draw("same hist E");   

    legend->AddEntry(hDPhiPr, HistogramAndLabelsPrVector[i].HistTitle);
    legend->AddEntry(hDPhiSc, HistogramAndLabelsScVector[i].HistTitle);
    legend->AddEntry(hDPhiPrSc, HistogramAndLabelsPrScVector[i].HistTitle);    

  } // for loop - statement

  legend->Draw();

  if (write) { canvas->SaveAs("Plots/ToDecay_or_ToHadronise.pdf"); }
  
} // readTree - function

int ProductionOriginStudy() {

  vector<HistogramAndLabels> HistogramAndLabelsPrVector;
  HistogramAndLabelsPrVector.push_back({"hDPhiHHPr", "prompt (HH)", kBlue, 1, 1}); // hadronisation HH
  HistogramAndLabelsPrVector.push_back({"hDPhiLLPr", "prompt (LL)", kBlue, 2, 3}); // hadronisation HH
  
  vector<HistogramAndLabels> HistogramAndLabelsScVector;
  HistogramAndLabelsScVector.push_back({"hDPhiHHSc", "non-prompt (HH)", kRed, 1, 1}); // decay HH 
  HistogramAndLabelsScVector.push_back({"hDPhiLLSc", "non-prompt (LL)", kRed, 2, 3}); // decay LL
  
  // For the following, the histograms have a trigger from hadronisation and an associate from decay, or vice-versa
  vector<HistogramAndLabels> HistogramAndLabelsPrScVector;
  HistogramAndLabelsPrScVector.push_back({"hDPhiHHPrSc", "prompt/non-prompt (HH)", kBlack, 1, 1}); // hadronisation/decay HH 
  HistogramAndLabelsPrScVector.push_back({"hDPhiLLPrSc", "prompt/non-prompt (LL)", kBlack, 2, 3}); // hadronisation/decay LL

  // Consider saving
  bool write = false;

  readTree(HistogramAndLabelsPrVector, HistogramAndLabelsScVector, HistogramAndLabelsPrScVector,
	   write,
	   1e-7, 5e-2);
  
  return 0;

}
