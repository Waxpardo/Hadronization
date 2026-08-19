// yieldSampling_CC.C
// Macro that takes the batched yield outputs and adds them together into a histogram
// This is done per associate per tune per configuration
// (e.g. error for B- associate in MONASH for low-low pT)
// From here the standard deviation is calculated and passed to an array with identical structure as the input array

void setCanvasMargins(TCanvas *canvas, double_t LeftMargin, double_t RightMargin, double_t TopMargin, double_t BottomMargin) {
  canvas->SetLeftMargin(LeftMargin);
  canvas->SetRightMargin(RightMargin);
  canvas->SetTopMargin(TopMargin);
  canvas->SetBottomMargin(BottomMargin);
}

TTree* createTree(Int_t iTree) {

  // Technical set-up for code below
  // Allows for flexibility in adding trees to input
  std::vector<const char*> yieldTreeNames;
  yieldTreeNames.push_back("YieldsTree_CCMULTGENERAL");
  yieldTreeNames.push_back("YieldsTree_CCMULTCONDENSED");

  // Histograms are used to calculate the errors, but they need to be initialised before
  // the sizes are known, so a 3D vector is used.
  std::map<std::tuple<int, int, int>, TH1F*> hYields;
  std::map<std::tuple<int, int, int>, TH1F*> hYieldsRatio;
  std::map<std::tuple<int, int, int>, TH1F*> hRelYields;
  std::map<std::tuple<int, int, int>, TH1F*> hRelYieldsRatio;

  TCanvas* canvasDpMonash = new TCanvas(Form("canvasDpMonash_%s", yieldTreeNames[iTree]), Form("canvasDpMonash_%s", yieldTreeNames[iTree]), 800, 600);
  TCanvas* canvasDpMonashRatio = new TCanvas(Form("canvasDpMonashRatio_%s", yieldTreeNames[iTree]), Form("canvasDpMonashRatio_%s", yieldTreeNames[iTree]), 800, 600);
  TCanvas* canvasDpMonashRel = new TCanvas(Form("canvasDpMonashRel_%s", yieldTreeNames[iTree]), Form("canvasDpMonashRel_%s", yieldTreeNames[iTree]), 800, 600);
  TCanvas* canvasDpMonashRelRatio = new TCanvas(Form("canvasDpMonashRelRatio_%s", yieldTreeNames[iTree]), Form("canvasDpMonashRelRatio_%s", yieldTreeNames[iTree]), 800, 600);
    
  TLegend* legendDpMonash = new TLegend(0.6, 0.9, 0.9, 0.5);
  legendDpMonash->SetTextSize(0.03);
  TLegend* legendDpMonashRatio = new TLegend(0.6, 0.9, 0.9, 0.5);
  legendDpMonashRatio->SetTextSize(0.03);
  TLegend* legendDpMonashRel = new TLegend(0.6, 0.9, 0.9, 0.5);
  legendDpMonashRel->SetTextSize(0.03);
  TLegend* legendDpMonashRelRatio = new TLegend(0.6, 0.9, 0.9, 0.5);
  legendDpMonashRelRatio->SetTextSize(0.03);
  
  Int_t bins = 1.2e3;
  canvasDpMonash->cd();
  
  if (iTree == 0) { // DDMULTGENERAL
    TH1F* DpMonashTemplate = new TH1F("DpMonashTemplate", "D^{+}D^{-} Monash", bins, 0, 1);
    DpMonashTemplate->SetStats(0);
    DpMonashTemplate->GetXaxis()->SetTitle("yield");
    DpMonashTemplate->GetYaxis()->SetRangeUser(0, 15);
    DpMonashTemplate->GetXaxis()->SetRangeUser(0.3, 0.45);
    DpMonashTemplate->Draw("hist");
  }
  
  if (iTree == 1) { // DDMULTCONDENSED
    TH1F* DpMonashTemplatecond = new TH1F("DpMonashTemplatecond", "D^{+}D^{-} Monash", bins, 0, 1);
    DpMonashTemplatecond->SetStats(0);
    DpMonashTemplatecond->GetXaxis()->SetTitle("yield");
    DpMonashTemplatecond->GetYaxis()->SetRangeUser(0, 15);
    DpMonashTemplatecond->GetXaxis()->SetRangeUser(0.3, 0.45);
    DpMonashTemplatecond->Draw("hist");
  }
  
  canvasDpMonashRatio->cd();
  
  if (iTree == 0) { // DDMULTGENERAL
    TH1F* DpMonashRatioTemplate = new TH1F("DpMonashRatioTemplate", "D^{+}#Lambda_{c}^{+} Junctions / B^{+}#Lambda_{c}^{+} Monash", bins, 0, 35);
    DpMonashRatioTemplate->SetStats(0);
    DpMonashRatioTemplate->GetXaxis()->SetTitle("yield ratio");
    DpMonashRatioTemplate->GetYaxis()->SetRangeUser(0, 15);
    DpMonashRatioTemplate->GetXaxis()->SetRangeUser(1, 3.5);
    DpMonashRatioTemplate->Draw("hist");
  }
  
  if (iTree == 1) { // DDMULTCONDENSED
    TH1F* DpMonashRatioTemplatecond = new TH1F("DpMonashRatioTemplatecond", "D^{+}#Lambda_{c}^{+} Junctions / D^{+}#Lambda_{c}^{+} Monash", bins, 0, 35);
    DpMonashRatioTemplatecond->SetStats(0);
    DpMonashRatioTemplatecond->GetXaxis()->SetTitle("yield ratio");
    DpMonashRatioTemplatecond->GetYaxis()->SetRangeUser(0, 15);
    DpMonashRatioTemplatecond->GetXaxis()->SetRangeUser(1, 3.5);
    DpMonashRatioTemplatecond->Draw("hist");
  }
  
  canvasDpMonashRel->cd();
  
  if (iTree == 0) { // DDMULTGENERAL
    TH1F* DpMonashRelTemplate = new TH1F("DpMonashRelTemplate", "D^{+}#Lambda_{c}^{0} / D^{+}D^{-} Junctions", bins, 0, 3);
    DpMonashRelTemplate->SetStats(0);
    DpMonashRelTemplate->GetXaxis()->SetTitle("relative yield");
    DpMonashRelTemplate->GetYaxis()->SetRangeUser(0, 15);
    DpMonashRelTemplate->GetXaxis()->SetRangeUser(0.1, 0.4);
    DpMonashRelTemplate->Draw("hist");
  }
  
  if (iTree == 1) { // DDMULTCONDENSED
    TH1F* DpMonashRelTemplatecond = new TH1F("DpMonashRelTemplatecond", "D^{+}#Lambda_{c}^{+} / D^{+}D^{-} Junctions", bins, 0, 3);
    DpMonashRelTemplatecond->SetStats(0);
    DpMonashRelTemplatecond->GetXaxis()->SetTitle("relative yield");
    DpMonashRelTemplatecond->GetYaxis()->SetRangeUser(0, 15);
    DpMonashRelTemplatecond->GetXaxis()->SetRangeUser(0.1, 0.4);
    DpMonashRelTemplatecond->Draw("hist");
  }
  
  canvasDpMonashRelRatio->cd();
  
  if (iTree == 0) { // DDMULTGENERAL
    TH1F* DpMonashRelRatioTemplate = new TH1F("DpMonashRelRatioTemplate", "D^{+}#Lambda_{c}^{+} / D^{+}D^{-} | Junctions / Monash", bins, 0, 100);
    DpMonashRelRatioTemplate->SetStats(0);
    DpMonashRelRatioTemplate->GetXaxis()->SetTitle("junctions yield / monash yield");
    DpMonashRelRatioTemplate->GetYaxis()->SetRangeUser(0, 15);
    DpMonashRelRatioTemplate->GetXaxis()->SetRangeUser(0, 5.5);
    DpMonashRelRatioTemplate->Draw("hist");
  }
  
  if (iTree == 1) { // DDMULTCONDENSED
    TH1F* DpMonashRelRatioTemplatecond = new TH1F("DpMonashRelRatioTemplatecond", "D^{+}#Lambda_{c}^{+} / D^{+}D^{-} | Junctions / Monash", bins, 0, 100);
    DpMonashRelRatioTemplatecond->SetStats(0);
    DpMonashRelRatioTemplatecond->GetXaxis()->SetTitle("junctions yield / monash yield");
    DpMonashRelRatioTemplatecond->GetYaxis()->SetRangeUser(0, 15);
    DpMonashRelRatioTemplatecond->GetXaxis()->SetRangeUser(0, 5.5);
    DpMonashRelRatioTemplatecond->Draw("hist");
  }
  
  TFile* inputFile = TFile::Open("yieldOutput_1.root");
  TTree* inputTree = dynamic_cast<TTree*>(inputFile->Get(yieldTreeNames[iTree]));
  
  Int_t vHistAndLabelsSize = 0; Int_t Nhist = 0; Int_t Nconfigs = 0;
  
  inputTree->SetBranchAddress("vHistAndLabelsSize", &vHistAndLabelsSize);
  inputTree->SetBranchAddress("Nhist", &Nhist);
  inputTree->SetBranchAddress("Nconfigs", &Nconfigs);
  
  inputTree->GetEntry(0);
  
  std::cout << std::endl;
  std::cout << "Settings for array size, as derived from first output file: " << std::endl;
  std::cout << "iTree = " << iTree << " and tree name = " << yieldTreeNames[iTree] << std::endl;
  std::cout << "vHistAndLabelsSize[iTree] = " << vHistAndLabelsSize << std::endl
	    << "Nhist[iTree] = " << Nhist << std::endl
	    << "Nconfigs[iTree] = " << Nconfigs << std::endl;
  std::cout << std::endl;
  
  // The error (standard deviation) is then saved in a vector
  // This part is not dynamically allocated
  // The arrays are consistent with the B_Balancing_GeneralPlotting macro
  Double_t vYieldsErr[vHistAndLabelsSize/Nhist][2][Nconfigs];
  Double_t vYieldsRatioErr[vHistAndLabelsSize/Nhist][Nconfigs];
  Double_t vRelYieldsErr[vHistAndLabelsSize/Nhist][2][Nconfigs];
  Double_t vRelYieldsRatioErr[vHistAndLabelsSize/Nhist][Nconfigs];

  // Name will be "Error_YieldsTree_......"
  TTree* outputTree = new TTree(Form("Error_%s", yieldTreeNames[iTree]), "Tree containing errors on 4 yield combinations, contained as arrays");
  
  outputTree->Branch("vYieldsErr", vYieldsErr, Form("vYieldsErr[%d][2][%d]/D", int(vHistAndLabelsSize/Nhist), int(Nconfigs)));
  outputTree->Branch("vYieldsRatioErr", vYieldsRatioErr, Form("vYieldsRatioErr[%d][%d]/D", int(vHistAndLabelsSize/Nhist), int(Nconfigs)));
  outputTree->Branch("vRelYieldsErr", vRelYieldsErr, Form("vRelYieldsErr[%d][2][%d]/D", int(vHistAndLabelsSize/Nhist), int(Nconfigs)));
  outputTree->Branch("vRelYieldsRatioErr", vRelYieldsRatioErr, Form("vRelYieldsRatioErr[%d][%d]/D", int(vHistAndLabelsSize/Nhist), int(Nconfigs)));
  
  
  
  for (Int_t i = 1; i <= 20; i++) {
    
    TString rootFileName;
    rootFileName.Form("yieldOutput_%i.root", i);
    
    TFile* sampleFile = TFile::Open(rootFileName);
    
    TTree* sampleTree;
    sampleFile->GetObject(yieldTreeNames[iTree], sampleTree);
    
    /*
      std::cout << "vHistAndLabelsSize = " << vHistAndLabelsSize << std::endl
      << "Nhist = " << Nhist << std::endl
      << "Nconfigs = " << Nconfigs << std::endl;
    */
    
    Double_t vYields[vHistAndLabelsSize/Nhist][2][Nconfigs];
    sampleTree->SetBranchAddress("vYields", vYields);
    sampleTree->GetEntry(0);
    // std::cout << "vYields[0][0][0] (B+B- 80-100 % multiplicity bin) = " << vYields[0][0][0] << std::endl;
    
    // Fill the appropriate histograms with yields
    for (Int_t k = 0; k < vHistAndLabelsSize / Nhist; k++) {
      for (Int_t l = 0; l < 2; l++) {
	for (Int_t m = 0; m < Nconfigs; m++) {
	  
	  // Create unique key for the histogram
	  std::tuple<int, int, int> key = std::make_tuple(k, l, m);
	  
	  // If histogram for this key doesn't exist, create it
	  // -------------------------------------------------------------------------------------------------------
	  if (hYields.find(key) == hYields.end()) {
	    hYields[key] = new TH1F(Form("hYields_%s_%i_%i_%i", yieldTreeNames[iTree], k, l, m), Form("hYields_%s_%i_%i_%i", yieldTreeNames[iTree], k, l, m), bins, 0, 1);
	  }
	  
	  hYields[key]->Fill(vYields[k][l][m]);
	  
	  // -------------------------------------------------------------------------------------------------------
	  
	  if (l == 0) { // ratio only 1/2 of iterations
	    if (hYieldsRatio.find(key) == hYieldsRatio.end()) {
	      hYieldsRatio[key] = new TH1F(Form("hYieldsRatio_%s_%i_%i", yieldTreeNames[iTree], k, m), Form("hYieldsRatio_%s_%i_%i", yieldTreeNames[iTree], k, m), bins, 0, 35);
	    }
	    
	    hYieldsRatio[key]->Fill(vYields[k][1][m] / vYields[k][0][m]);
	  }
	  
	  // -------------------------------------------------------------------------------------------------------
	  
	  if (hRelYields.find(key) == hRelYields.end()) {
	    hRelYields[key] = new TH1F(Form("hRelYields_%s_%i_%i_%i", yieldTreeNames[iTree], k, l, m), Form("hRelYields_%s_%i_%i_%i", yieldTreeNames[iTree], k, l, m), bins, 0, 3);
	  }
	  
	  hRelYields[key]->Fill(vYields[k][l][m] / vYields[0][l][m]);
	  
	  // -------------------------------------------------------------------------------------------------------
	  
	  if (l == 0) { // ratio only 1/2 of iterations
	    if (hRelYieldsRatio.find(key) == hRelYieldsRatio.end()) {
	      hRelYieldsRatio[key] = new TH1F(Form("hRelYieldsRatio_%s_%i_%i", yieldTreeNames[iTree], k, m), Form("hRelYieldsRatio_%s_%i_%i", yieldTreeNames[iTree], k, m), bins, 0, 100);
	    }
	    
	    hRelYieldsRatio[key]->Fill( (vYields[k][1][m] / vYields[0][1][m]) / (vYields[k][0][m] / vYields[0][0][m]) );
	  }
	  
	  // -------------------------------------------------------------------------------------------------------
	  
	  
	  
	} // m
      } // l
    } // k
    
  } // loop over output.root
  
  



  // TODO: put this in functions 
  // Calculate errors from histograms, draw some for consistency checks
  // 1. Errors for yields -------------------------------------------------------------------------------------------------------
  for (auto& pair : hYields) {
    
    // pair.first gives tuple(i,j,k)
    // pair.second gives histogram at yield[i][j][k], combined for 40 output files
    
    Int_t i = 0; Int_t j = 0; Int_t k = 0;
    i = std::get<0>(pair.first); j = std::get<1>(pair.first); k = std::get<2>(pair.first);
    // std::cout << "i, j, k = " << i << ", " << j << ", " << k << std::endl;
    
    vYieldsErr[i][j][k] = pair.second->GetStdDev(); 
    std::cout << Form("hYields error[%i][%i][%i] = ", i, j, k) << pair.second->GetStdDev() << std::endl;
    
    if(i == 0 && j == 0 && k == 0) {
      // TCanvas* canvas = new TCanvas(Form("hYields[%i][%i][%i]", i, j, k), Form("hYields[%i][%i][%i]", i, j, k), 800, 600);
      // canvas->cd();
      // pair.second->Draw("hist");
    }
    
    canvasDpMonash->cd();
    
    if(iTree == 0 && i == 0 && j == 0) {
      
      if (k == 0) {
	pair.second->SetTitle("80 - 100 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(2); }
      
      if (k == 1) {
	pair.second->SetTitle("60 - 80 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(1); }
      
      if (k == 2) {
	pair.second->SetTitle("40 - 60 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(3); }
      
      if (k == 3) {
	pair.second->SetTitle("20 - 40 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(2); }
      
      if (k == 4) {
	pair.second->SetTitle("20 - 5 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(1); }
      
      if (k == 5) {
	pair.second->SetTitle("5 - 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(2); }
      
      if (k == 6) {
	pair.second->SetTitle("top 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(1); }
      
      pair.second->Draw("same hist");
      legendDpMonash->AddEntry(pair.second, Form("%s = %f",
						 pair.second->GetTitle(),
						 pair.second->GetStdDev()));
      
      if (k == 6) { legendDpMonash->Draw(); }
      
    } // if(iTree == 0 && i == 0 && j == 0)
    
    canvasDpMonash->cd();
    
    if(iTree == 1 && i == 0 && j == 0) {
      
      if (k == 0) {
	pair.second->SetTitle("80 - 100 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(1); }
      
      if (k == 1) {
	pair.second->SetTitle("40 - 80 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(2); }
      
      if (k == 2) {
	pair.second->SetTitle("5 - 40 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(1); }
      
      if (k == 3) {
	pair.second->SetTitle("top 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(1); }
      
      pair.second->Draw("same hist");
      legendDpMonash->AddEntry(pair.second, Form("%s = %f",
						 pair.second->GetTitle(),
						 pair.second->GetStdDev()));
      
      if (k == 3) { legendDpMonash->Draw(); }
      
    } // if (iTree == 1 && i == 0 && j == 0)
    
    
  } // yield errors
  
    // 2. Errors for yield ratios -------------------------------------------------------------------------------------------------------
  for (auto& pair : hYieldsRatio) {
    
    // pair.first gives tuple(i,j,k)
    // pair.second gives histogram at yield[i][j][k], combined for 40 output files
    
    Int_t i = 0; Int_t j = 0; Int_t k = 0;
    i = std::get<0>(pair.first); j = std::get<1>(pair.first); k = std::get<2>(pair.first);
    // std::cout << "i, j, k = " << i << ", " << j << ", " << k << std::endl;
    
    vYieldsRatioErr[i][k] = pair.second->GetStdDev(); 
    std::cout << Form("hYields error[%i][%i] = ", i, k) << pair.second->GetStdDev() << std::endl;
    
    if(i == 3 && j == 0 && k == 0) { // i = 4 is B+Lb
      // TCanvas* canvas = new TCanvas(Form("hYields[%i][%i][%i]", i, j, k), Form("hYields[%i][%i][%i]", i, j, k), 800, 600);
      // canvas->cd();
      // pair.second->Draw("hist");
    }
    
    canvasDpMonashRatio->cd();
    
    if(iTree == 0 && i == 3 && j == 0) {
      
      if (k == 0) {
	pair.second->SetTitle("80 - 100 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(2); }
      
      if (k == 1) {
	pair.second->SetTitle("60 - 80 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(1); }
      
      if (k == 2) {
	pair.second->SetTitle("40 - 60 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(3); }
      
      if (k == 3) {
	pair.second->SetTitle("20 - 40 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(2); }
      
      if (k == 4) {
	pair.second->SetTitle("20 - 5 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(1); }
      
      if (k == 5) {
	pair.second->SetTitle("5 - 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(2); }
      
      if (k == 6) {
	pair.second->SetTitle("top 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(1); }
      
      pair.second->Draw("same hist");
      legendDpMonashRatio->AddEntry(pair.second, Form("%s = %f",
						      pair.second->GetTitle(),
						      pair.second->GetStdDev()));
      
      if (k == 6) { legendDpMonashRatio->Draw(); }
      
    } // if(iTree == 0 && i == 0 && j == 0)
    
    canvasDpMonashRatio->cd();
    
    if(iTree == 1 && i == 3 && j == 0) {
      
      if (k == 0) {
	pair.second->SetTitle("80 - 100 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(1); }
      
      if (k == 1) {
	pair.second->SetTitle("40 - 80 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(2); }
      
      if (k == 2) {
	pair.second->SetTitle("5 - 40 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(1); }
      
      if (k == 3) {
	pair.second->SetTitle("top 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(1); }
      
      pair.second->Draw("same hist");
      legendDpMonashRatio->AddEntry(pair.second, Form("%s = %f",
						      pair.second->GetTitle(),
						      pair.second->GetStdDev()));
      
      if (k == 3) { legendDpMonashRatio->Draw(); }
      
    } // if (iTree == 1 && i == 0 && j == 0)
    
    
  } // yieldsRatio errors
  
  
    // 3. Errors for relative yields -------------------------------------------------------------------------------------------------------
  for (auto& pair : hRelYields) {
    
    // pair.first gives tuple(i,j,k)
    // pair.second gives histogram at yield[i][j][k], combined for 40 output files
    
    Int_t i = 0; Int_t j = 0; Int_t k = 0;
    i = std::get<0>(pair.first); j = std::get<1>(pair.first); k = std::get<2>(pair.first);
    // std::cout << "i, j, k = " << i << ", " << j << ", " << k << std::endl;
    
    vRelYieldsErr[i][j][k] = pair.second->GetStdDev(); 
    std::cout << Form("hYields error[%i][%i][%i] = ", i, j, k) << pair.second->GetStdDev() << std::endl;
    
    if(i == 3 && j == 1 && k == 0) {
      // TCanvas* canvas = new TCanvas(Form("hYields[%i][%i][%i]", i, j, k), Form("hYields[%i][%i][%i]", i, j, k), 800, 600);
      // canvas->cd();
      // pair.second->Draw("hist");
    }
    
    canvasDpMonashRel->cd();
    
    if(iTree == 0 && i == 3 && j == 1) {
      
      if (k == 0) {
	pair.second->SetTitle("80 - 100 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(2); }
      
      if (k == 1) {
	pair.second->SetTitle("60 - 80 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(1); }
      
      if (k == 2) {
	pair.second->SetTitle("40 - 60 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(3); }
      
      if (k == 3) {
	pair.second->SetTitle("20 - 40 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(2); }
      
      if (k == 4) {
	pair.second->SetTitle("20 - 5 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(1); }
      
      if (k == 5) {
	pair.second->SetTitle("5 - 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(2); }
      
      if (k == 6) {
	pair.second->SetTitle("top 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(1); }
      
      pair.second->Draw("same hist");
      legendDpMonashRel->AddEntry(pair.second, Form("%s = %f",
						    pair.second->GetTitle(),
						    pair.second->GetStdDev()));
      
      if (k == 6) { legendDpMonashRel->Draw(); }
      
    } // if(iTree == 0 && i == 0 && j == 0)
    
    canvasDpMonashRel->cd();
    
    if(iTree == 1 && i == 3 && j == 1) {
      
      if (k == 0) {
	pair.second->SetTitle("80 - 100 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(1); }
      
      if (k == 1) {
	pair.second->SetTitle("40 - 80 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(2); }
      
      if (k == 2) {
	pair.second->SetTitle("5 - 40 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(1); }
      
      if (k == 3) {
	pair.second->SetTitle("top 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(1); }
      
      pair.second->Draw("same hist");
      legendDpMonashRel->AddEntry(pair.second, Form("%s = %f",
						    pair.second->GetTitle(),
						    pair.second->GetStdDev()));
      
      if (k == 3) { legendDpMonashRel->Draw(); }
      
    } // if (iTree == 1 && i == 0 && j == 0)
    
    
  } // relYields errors
  
    // 4. Errors for relative yield ratios -------------------------------------------------------------------------------------------------------
  for (auto& pair : hRelYieldsRatio) {
    
    // pair.first gives tuple(i,j,k)
    // pair.second gives histogram at yield[i][j][k], combined for 40 output files
    
    Int_t i = 0; Int_t j = 0; Int_t k = 0;
    i = std::get<0>(pair.first); j = std::get<1>(pair.first); k = std::get<2>(pair.first);
    // std::cout << "i, j, k = " << i << ", " << j << ", " << k << std::endl;
    
    vRelYieldsRatioErr[i][k] = pair.second->GetStdDev(); 
    std::cout << Form("hYields error[%i][%i] = ", i, k) << pair.second->GetStdDev() << std::endl;
    
    if(i == 3 && j == 0 && k == 0) {
      // TCanvas* canvas = new TCanvas(Form("hYields[%i][%i][%i]", i, j, k), Form("hYields[%i][%i][%i]", i, j, k), 800, 600);
      // canvas->cd();
      // pair.second->Draw("hist");
    }
    
    canvasDpMonashRelRatio->cd();
    
    if(iTree == 0 && i == 3 && j == 0) {
      
      if (k == 0) {
	pair.second->SetTitle("80 - 100 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(2); }
      
      if (k == 1) {
	pair.second->SetTitle("60 - 80 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(1); }
      
      if (k == 2) {
	pair.second->SetTitle("40 - 60 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(3); }
      
      if (k == 3) {
	pair.second->SetTitle("20 - 40 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(2); }
      
      if (k == 4) {
	pair.second->SetTitle("20 - 5 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(1); }
      
      if (k == 5) {
	pair.second->SetTitle("5 - 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(2); }
      
      if (k == 6) {
	pair.second->SetTitle("top 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(1); }
      
      pair.second->Draw("same hist");
      legendDpMonashRelRatio->AddEntry(pair.second, Form("%s = %f",
							 pair.second->GetTitle(),
							 pair.second->GetStdDev()));
      
      if (k == 6) { legendDpMonashRelRatio->Draw(); }
      
    } // if(iTree == 0 && i == 0 && j == 0)
    
    canvasDpMonashRelRatio->cd();
    
    if(iTree == 1 && i == 3 && j == 0) {
      
      if (k == 0) {
	pair.second->SetTitle("80 - 100 % multiplicity bin");
	pair.second->SetLineColor(kBlue); pair.second->SetLineStyle(1); }
      
      if (k == 1) {
	pair.second->SetTitle("40 - 80 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(2); }
      
      if (k == 2) {
	pair.second->SetTitle("5 - 40 % multiplicity bin");
	pair.second->SetLineColor(kBlack); pair.second->SetLineStyle(1); }
      
      if (k == 3) {
	pair.second->SetTitle("top 1 % multiplicity bin");
	pair.second->SetLineColor(kRed); pair.second->SetLineStyle(1); }
      
      pair.second->Draw("same hist");
      legendDpMonashRelRatio->AddEntry(pair.second, Form("%s = %f",
							 pair.second->GetTitle(),
							 pair.second->GetStdDev()));
      
      if (k == 3) { legendDpMonashRelRatio->Draw(); }
      
    } // if (iTree == 1 && i == 0 && j == 0)
    
    
  } // relYieldsRatio errors
  
  outputTree->Fill();
  
  return outputTree;
  
} // createTree

int yieldSampling_CC() {

  TFile* outputFile = new TFile("yieldErrors_test.root", "RECREATE");
  
  TTree* outputTreeMULTGENERAL = createTree(0);
  TTree* outputTreeMULTCONDENSED = createTree(1);

  outputFile->cd();
  outputTreeMULTGENERAL->Write();
  outputTreeMULTCONDENSED->Write();
  
  /*
  if (iTree == yieldTreeNames.size()-1) {
      outputFile->cd();
      std::cout << vYieldsErrMULTGENERAL[0][0][0] << std::endl;
      outputTree->Fill();
      outputTree->Write();
    } 
  */
  
  return 0;

}
