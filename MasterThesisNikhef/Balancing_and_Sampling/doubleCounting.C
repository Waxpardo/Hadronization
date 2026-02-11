// B_Balancing.C
// Simple script that compares two histograms of same trigger and associate species (B+, B+) to check if there was accidental double counting.
// As a sanity check, it also compares different species (B+, B-)

void normalise(TH1D* hist, TH1D* trig, Double_t xmin, Double_t xmax) {
	Int_t bin_start = trig->FindBin(xmin);
	Int_t bin_finish = trig->FindBin(xmax);
	Double_t integral = trig->Integral(bin_start, bin_finish);
	hist->Scale(1./integral);
}

void setCanvasMargins(TCanvas *canvas, double_t LeftMargin, double_t RightMargin, double_t TopMargin, double_t BottomMargin) {
  canvas->SetLeftMargin(LeftMargin);
  canvas->SetRightMargin(RightMargin);
  canvas->SetTopMargin(TopMargin);
  canvas->SetBottomMargin(BottomMargin);
}

void readTree() {

  TFile* doubleCountingBpBmTree = new TFile("/home/pveen/scripts/Nikhef/MasterThesis/complete_root_bb_only_80/BplusBminus.root");
  TFile* doubleCountingBpBpTree = new TFile("/home/pveen/scripts/Nikhef/MasterThesis/complete_root_bb_only_80/BplusBplus.root");
  TFile* normalCountingBpBmTree = new TFile("/home/pveen/scripts/Nikhef/MasterThesis/complete_root_bb_only_81/BplusBminus.root");
  TFile* normalCountingBpBpTree = new TFile("/home/pveen/scripts/Nikhef/MasterThesis/complete_root_bb_only_81/BplusBplus.root");

  TH1D* doubleCountingBpBm = (TH1D*)doubleCountingBpBmTree->Get("hDPhiHH");
  TH1D* doubleCountingBpBmTrPt = (TH1D*)doubleCountingBpBmTree->Get("hTrPt");
  normalise(doubleCountingBpBm, doubleCountingBpBmTrPt, -1.57, 4.71);
  
  TH1D* doubleCountingBpBp = (TH1D*)doubleCountingBpBpTree->Get("hDPhiHH");
  TH1D* doubleCountingBpBpTrPt = (TH1D*)doubleCountingBpBpTree->Get("hTrPt");
  normalise(doubleCountingBpBp, doubleCountingBpBpTrPt, -1.57, 4.71);
  
  TH1D* normalCountingBpBm = (TH1D*)normalCountingBpBmTree->Get("hDPhiHH");
  TH1D* normalCountingBpBmTrPt = (TH1D*)normalCountingBpBmTree->Get("hTrPt");
  normalise(normalCountingBpBm, normalCountingBpBmTrPt, -1.57, 4.71);
  
  TH1D* normalCountingBpBp = (TH1D*)normalCountingBpBpTree->Get("hDPhiHH");
  TH1D* normalCountingBpBpTrPt = (TH1D*)normalCountingBpBpTree->Get("hTrPt");
  normalise(normalCountingBpBp, normalCountingBpBpTrPt, -1.57, 4.71);

  TCanvas* cBpBm = new TCanvas("cBpBm", "cBpBm", 800, 600);
  setCanvasMargins(cBpBm, 0.15, 0.1, 0.1, 0.1);
  cBpBm->cd();
  
  doubleCountingBpBm->Draw("hist E");
  doubleCountingBpBm->SetLineColor(kRed);
  
  normalCountingBpBm->Draw("same hist E");
  normalCountingBpBm->SetLineColor(kBlack);

  // TODO: add ratio plots as subpads to main pad
  TCanvas* cBpBmRatio = new TCanvas("cBpBmRatio", "double counting BpBm / normal counting BpBm", 800, 600);
  setCanvasMargins(cBpBm, 0.15, 0.1, 0.1, 0.1);
  cBpBmRatio->cd();

  TH1D* hRatioBpBm = (TH1D*)doubleCountingBpBm->Clone();
  hRatioBpBm->Divide(normalCountingBpBm);
  hRatioBpBm->Draw("hist E");

  TCanvas* cBpBp = new TCanvas("cBpBp", "cBpBp", 800, 600);
  setCanvasMargins(cBpBp, 0.15, 0.1, 0.1, 0.1);
  cBpBp->cd();
  
  doubleCountingBpBp->SetLineColor(kRed);
  doubleCountingBpBp->GetYaxis()->SetRangeUser(1e-6, 1.5e-5);
  doubleCountingBpBp->Draw("hist E");

  normalCountingBpBp->SetLineColor(kBlack);
  normalCountingBpBp->Draw("same hist E");

  // TODO: add ratio plots as subpads to main pad
  TCanvas* cBpBpRatio = new TCanvas("cBpBpRatio", "double counting BpBp / normal counting BpBp", 800, 600);
  setCanvasMargins(cBpBp, 0.15, 0.1, 0.1, 0.1);
  cBpBpRatio->cd();

  TH1D* hRatioBpBp = (TH1D*)doubleCountingBpBp->Clone();
  hRatioBpBp->Divide(normalCountingBpBp);
  hRatioBpBp->GetYaxis()->SetRangeUser(1.5, 2.5);
  hRatioBpBp->Draw("hist E");

  TCanvas* cBOverview = new TCanvas("cBOverview", "OS and SS both drawn", 800, 600);
  setCanvasMargins(cBOverview, 0.15, 0.1, 0.1, 0.1);
  cBOverview->cd();
  gPad->SetLogy();

  normalCountingBpBm->GetYaxis()->SetRangeUser(1e-7, 1e-1);
  normalCountingBpBm->Draw("hist E");
  normalCountingBpBp->Draw("same hist E");

  TCanvas* cBCorr = new TCanvas("cBCorr", "OS - SS", 800, 600);
  setCanvasMargins(cBCorr, 0.15, 0.1, 0.1, 0.1);
  cBCorr->cd();
  gPad->SetLogy();
  
  TH1D* hBCorr = (TH1D*)normalCountingBpBm->Clone();
  hBCorr->Add(normalCountingBpBp, -1.);
  hBCorr->Draw("hist E");

  Double_t yield = hBCorr->Integral();
  std::cout << "yield for B- associate = " << yield*1e3 << "e-3" << std::endl;
  
}

int B_Balancing() {

  doubleCounting();
  
  return 0;
  
}
