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

struct HistAndLabels {

  TH1D* Hist;
  const char* TriggerName;
  const char* AssociateName;
  const char* PtRegion;
  Double_t DrawYmin;
  Double_t DrawYmax;
  
};

struct RootFileAndLabels {

  const char* RootFile;
  const char* TriggerName;
  const char* AssociateName;
  Double_t DrawYmin;
  Double_t DrawYmax;
  
};

struct IntegrationBins {

  const char* RegionName;
  Double_t xmin;
  Double_t xmax;
  Color_t Color;
  
};

void doubleCounting() {

  // 80 = with double counting, 81 is with correct counting
  TFile* doubleCountingBpBmTree = new TFile("/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_221/BplusBminus.root");
  TFile* doubleCountingBpBpTree = new TFile("/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_221/BplusBplus.root");
  TFile* normalCountingBpBmTree = new TFile("/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_only_82/BplusBminus.root");
  TFile* normalCountingBpBpTree = new TFile("/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_only_82/BplusBplus.root");

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

  // Set up vectors so that we can just loop over them
  // (saves the writer of this script some hard-needed time)
  std::vector<TH1D*> vdoubleCounting;
  vdoubleCounting.push_back(doubleCountingBpBm); vdoubleCounting.push_back(doubleCountingBpBp);
  std::vector<TH1D*> vnormalCounting;
  vnormalCounting.push_back(normalCountingBpBm); vnormalCounting.push_back(normalCountingBpBp);


  
  for (int i = 0; i < 2; i++) {

    // Retrieve histograms from input vectors
    TH1D* hdoubleCounting = vdoubleCounting[i];
    TH1D* hnormalCounting = vnormalCounting[i];
    const char* particlePair;
    if (i == 0) { particlePair = "B^{+}B^{-}" ;} if (i == 1) { particlePair = "B^{+}B^{+}"; }
    
    // Comparison of normal and double counting for BpBm (would not expect a difference)
    TCanvas* c = new TCanvas(Form("cRatio_%i", i), Form("double / normal counting %s", particlePair), 800, 600);
    setCanvasMargins(c, 0.15, 0.1, 0.1, 0.1);
    c->cd();
    
    TPad* mainPad = new TPad(Form("mainPad_%i", i), "mainPad", 0.03, 0.3, 1.0, 1.0);
    mainPad->Draw();
    TPad* miniPad = new TPad(Form("miniPad_%i", i), "miniPad", 0.03, 0.0, 1.0, 0.3);
    miniPad->Draw();
    Double_t mod = 0.7 / 0.3;
    
    TLegend* l = new TLegend(0.15, 0.88, 0.30, 0.78);
    l->SetBorderSize(1);
    l->SetTextSize(0.03);
    l->AddEntry(hdoubleCounting, "double counting");
    l->AddEntry(hnormalCounting, "correct counting");  
    
    // * Main Pad * //
    mainPad->cd();
    gPad->SetLogy();
    hdoubleCounting->SetStats(0);
    hdoubleCounting->GetYaxis()->SetTitle("#frac{1}{N_{trigger}} #frac{dN}{dp_{#phi}}");
    hdoubleCounting->Draw("hist E");
    hdoubleCounting->SetLineColor(kRed);
    hnormalCounting->Draw("same hist E");
    hnormalCounting->SetLineColor(kBlack);
    l->Draw();
    
    // * Mini Pad * //
    miniPad->cd();
    TH1D* hRatio = (TH1D*)hdoubleCounting->Clone();
    hRatio->SetStats(0);
    hRatio->SetTitle("");
    hRatio->GetYaxis()->SetTitle("double / correct");
    hRatio->SetLineColor(kBlack);
    hRatio->Divide(hnormalCounting);
    hRatio->Draw("hist E");
    
  } // end of for-loop over double/normal counting


  // Compare OS and SS on the same canvas
  TCanvas* cBOverview = new TCanvas("cBOverview", "OS and SS both drawn", 800, 600);
  setCanvasMargins(cBOverview, 0.15, 0.1, 0.1, 0.1);
  cBOverview->cd();
  gPad->SetLogy();

  normalCountingBpBm->GetYaxis()->SetRangeUser(1e-7, 1e-1);
  normalCountingBpBm->Draw("hist E");
  normalCountingBpBp->Draw("same hist E");

  // Subtract OS from SS to get the background reduced plots
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

// Input vector should countain per trigger yield histograms!
void CalculateOS_minus_SS(std::vector<HistAndLabels> vOSHistAndLabels,
			  std::vector<HistAndLabels> vSSHistAndLabels,
			  bool write) {

  // Iterator step size = 3 in order to easily loop over the different PtRegions (LL, II, HH)
  // 0(+3) -> LL
  // 1(+3) -> II
  // 2(+3) -> HH
  // An independent check is provided in case more trigger-associate pT regions are added

  // Plot yields for different associates
  TCanvas* cYields = new TCanvas("cYields", "cYields", 800, 600);
  setCanvasMargins(cYields, 0.15, 0.1, 0.1, 0.1);

  // Define a template for this plot to set titles, stats, etc.
  TH1D* hYieldsTemplate = new TH1D("hYieldsTemplate", "hYieldsTemplate", vOSHistAndLabels.size()/3, 0, vOSHistAndLabels.size()/3);

  // When the PtRegions (LL, II, HH) are drawn, some attention is necessary to get the correct line styles and widths
  Int_t PtRegionLineStyles[3] = {3, 5, 1}; 
  Int_t PtRegionLineWidths[3] = {2, 2, 2}; 

  // Define the following vector to save some time labelling the bins in the yields histogram
  // std::vector<const char*> vAssociatesNames;
  std::vector<IntegrationBins> vYieldIntegrationBins = {{"all", -1.57, 4.71, kBlack},
							{"near-side", -0.5, 0.5, kBlue},
							{"away-side", 2.5, 4.5, kRed}};

  // Define legend for yield plot outside for-loop
  TLegend* lYields = new TLegend(0.63, 0.88, 0.9, 0.58);
  lYields->SetTextSize(0.03);

  
  
  for (int i = 0; i < vOSHistAndLabels.size(); i = i+3) {

    HistAndLabels OS = vOSHistAndLabels[i];
    HistAndLabels SS = vSSHistAndLabels[i];

    // Compare OS and SS on the same canvas    
    TCanvas* cOverview = new TCanvas(Form("cOverview_%i", i), Form("%s%s and %s%s both drawn for %s", OS.TriggerName, OS.AssociateName, SS.TriggerName, SS.AssociateName, OS.PtRegion), 800, 600);
    setCanvasMargins(cOverview, 0.15, 0.1, 0.1, 0.1);
    /*
    // Subtract OS from SS to get the background reduced plots
    TCanvas* cCorr = new TCanvas(Form("cCorr_%i", i), Form("%s%s - %s%s for %s", OS.TriggerName, OS.AssociateName, SS.TriggerName, SS.AssociateName, OS.PtRegion), 800, 600);
    setCanvasMargins(cCorr, 0.15, 0.1, 0.1, 0.1);
    */
    TPad* mainPad = new TPad(Form("mainPad_%i", i), "mainPad", 0.03, 0.3, 1.0, 1.0);
    mainPad->Draw();
    TPad* miniPad = new TPad(Form("miniPad_%i", i), "miniPad", 0.03, 0.0, 1.0, 0.3);
    miniPad->Draw();
    Double_t mod = 0.7 / 0.3;

    TLegend* lOverview = new TLegend(0.20, 0.88, 0.40, 0.68);
    lOverview->SetTextSize(0.03);
    TLegend* lCorr = new TLegend(0.65, 0.88, 0.85, 0.78);
    lCorr->SetTextSize(0.03);

    for (int j = i; j < i+3; j++) {

      bool IsLL = false; bool IsII = false; bool IsHH = false;

      if (j != i) // Redefine to access all PtRegions
	{ OS = vOSHistAndLabels[j];
	  SS = vSSHistAndLabels[j]; }

      if (strcmp(OS.PtRegion, "LL") == 0 || strcmp(OS.PtRegion, "Low-Low") == 0) { IsLL = true; }
      if (strcmp(OS.PtRegion, "II") == 0 || strcmp(OS.PtRegion, "Int-Int") == 0) { IsII = true; }
      if (strcmp(OS.PtRegion, "HH") == 0 || strcmp(OS.PtRegion, "High-High") == 0) { IsHH = true; }

      // if (IsII) { continue; } // Option to skip PtRegion
      // if (IsHH) { continue; }

      TH1D* hOS = OS.Hist; TH1D* hSS = SS.Hist;
      hOS->SetTitle(Form("%s%s #Delta#phi angular correlations", OS.TriggerName, OS.AssociateName));
      hOS->GetYaxis()->SetTitle("#frac{1}{N_{trigger}} #frac{dN}{d#Delta#phi}");
      hOS->GetYaxis()->SetRangeUser(OS.DrawYmin, OS.DrawYmax);
      hOS->SetStats(0);
      hOS->SetLineColor(kRed);
      hSS->SetLineColor(kBlue);
      
      if (IsLL)
	{ hOS->SetLineStyle(3); hOS->SetLineWidth(2);
	  hSS->SetLineStyle(3); hSS->SetLineWidth(2); }
      if (IsII)
	{ hOS->SetLineStyle(5); hOS->SetLineWidth(2);
	  hSS->SetLineStyle(5); hSS->SetLineWidth(2); }
      if (IsHH)
	{ hOS->SetLineStyle(1); hOS->SetLineWidth(3);
	  hSS->SetLineStyle(1); hSS->SetLineWidth(3); }

      cOverview->cd();
      mainPad->cd();
      if (j == i) { hOS->Draw("hist E"); hSS->Draw("same hist E"); }
      else { hOS->Draw("same hist E"); hSS->Draw("same hist E"); }
      
      lOverview->AddEntry(hOS, Form("OS = %s%s (%s)", OS.TriggerName, OS.AssociateName, OS.PtRegion));
      lOverview->AddEntry(hSS, Form("SS = %s%s (%s)", SS.TriggerName, SS.AssociateName, SS.PtRegion));
      
      TH1D* hCorr = (TH1D*)hOS->Clone();
      hCorr->SetLineColor(kBlack);
      hCorr->Add(hSS, -1.);
      hCorr->GetYaxis()->SetRangeUser(OS.DrawYmin, OS.DrawYmax);
      hCorr->SetTitle("OS - SS");
      hCorr->SetTitleSize(0.8);
      hCorr->GetXaxis()->SetLabelSize(0.07);
      hCorr->GetYaxis()->SetLabelSize(0.07);
      hCorr->GetYaxis()->SetTitle("");
      hCorr->GetXaxis()->SetTitle("");

      // lCorr->AddEntry(hCorr, Form("%s%s (%s)", OS.TriggerName, OS.AssociateName, OS.PtRegion));
      lCorr->AddEntry(hCorr, Form("OS - SS (%s)", OS.PtRegion));
      
      // cCorr->cd();
      miniPad->cd();
      if (j == i) { hCorr->Draw("hist E"); }
      else { hCorr->Draw("same hist E"); }

      // i = associates, j = LL, II, HH, k = all, away, near
      // 1+i/3 gives bin number 1, 2, 3, etc.
      // j-i gives number 0, 1, 2 for LL, II, HH
      // k = 0, 1, 2 gives all, away, near
      // Define the histograms as an array
      TH1D* hYields[8][3][3]; 
      
      for (int k = 0; k<vYieldIntegrationBins.size(); k++) {

	// We integrate over 3 different regions (over all DPhi, over away-side and over near-side)
	// Respective associate yields are set in the following histogram
	// Divide by 3 as LL, II, and HH are included in the input vectors
	// std::cout<<"i, j, k = "<<i<<","<<j<<","<<k<<std::endl;
	hYields[i/3][j-i][k] = new TH1D(Form("hYieldsLL_%i_%i_%i", i, j, k), Form("hYieldsLL_%i_%i_%i", i, j, k), vOSHistAndLabels.size()/3, 0, vOSHistAndLabels.size()/3);
	
	IntegrationBins Bins = vYieldIntegrationBins[k];

	Double_t yield = hCorr->Integral(hCorr->FindBin(Bins.xmin), hCorr->FindBin(Bins.xmax));
	std::cout << Form("yield for (%s, %s) %s associate = ", Bins.RegionName, OS.PtRegion, OS.AssociateName) << yield*1e3 << "e-3" << std::endl;
	
	// Note: division by 3 to get proper bin number
	// Custom error until I figure out what to do with the error
	cYields->cd();

	if (i == 0 && j == 0 && k == 0) {
	  hYieldsTemplate->SetTitle("integrated yields for B^{+} trigger");
	  hYieldsTemplate->GetYaxis()->SetTitle("Yield");
	  hYieldsTemplate->GetXaxis()->SetTitle("Associate");
	  hYieldsTemplate->GetXaxis()->SetLabelSize(0.05);
	  hYieldsTemplate->SetStats(0);
	  hYieldsTemplate->GetYaxis()->SetRangeUser(1e-8, 1.);
	  hYieldsTemplate->Draw("PE");
	}

	hYields[i/3][j-i][k]->SetBinContent(1+i/3, yield);
	hYields[i/3][j-i][k]->SetBinError(1+i/3, 1e-9); // until I figure out what to do with the large error bars I get
	hYields[i/3][j-i][k]->SetLineStyle(PtRegionLineStyles[j-i]);
	hYields[i/3][j-i][k]->SetLineWidth(PtRegionLineWidths[j-i]);
	hYields[i/3][j-i][k]->SetLineColor(Bins.Color);
	hYields[i/3][j-i][k]->SetMarkerColor(Bins.Color);
	// hYields[i/3][j-i][k]->SetMarkerStyle(1);
	hYields[i/3][j-i][k]->Draw("same PE");
	
	if (i == 0) { lYields->AddEntry(hYields[i/3][j-i][k], Form("%s (%s)", Bins.RegionName, OS.PtRegion)); }
	
      } // END OF k for-loop over yield integration bins
      
    } // END OF j for-loop over PtRegions
    
    // Draw canvas and legend of superimposed PtRegions
    cOverview->cd();
    mainPad->cd(); gPad->SetLogy(); lOverview->Draw(); lCorr->Draw();
    miniPad->cd(); gPad->SetLogy(); 
    cOverview->Draw();
    
    // cOverview->cd(); gPad->SetLogy(); cOverview->Draw(); lOverview->Draw();
    // cCorr->cd(); gPad->SetLogy(); cCorr->Draw(); lCorr->Draw();

    // Define associate label names for yield plots
    hYieldsTemplate->GetXaxis()->SetBinLabel(1+i/3, OS.AssociateName);
    
  } // END OF i for-loop over input vector

  // Draw canvas and legend of yields for different associates
  cYields->cd(); gPad->SetLogy(); cYields->Draw(); lYields->Draw();
  // cYields->SaveAs("Plots/BpYields/BpYieldsLL.pdf");

} // END OF function declaration

int B_Balancing() {

  // Simple function that can check if the double counting procedure went as expected
  // doubleCounting();

  // Now calculate the opposite sign and same sign correlations in order to remove background from trigger-associate correlations
  // OS and SS defined as follows:
  //
  // Pick trigger (e.g. B+) and match with associates (e.g. B-, B0, Bs0, Lb)
  // OS is defined by correlation that matches b-bbar pair
  // SS is defined by correlation that matches b-b or bbar-bbar pair (depending on trigger)
  //
  // Examples:
  // OS = B+B-, SS = B+B+
  // OS = B+B0bar, SS = B+B0
  // OS = B+Lbbar, SS = BLb

  // TODO: make a loop that gets all the pt combinations (LL, II, HH) automatically
  // TODO: make miniPads for the subtracted plots and include yield in plot
  // TODO: make yield plots as function of associate
  // TODO: add (OS) B+Bc-, B+Bs0bar, B+Lb and create more correlations in simulation script (anti Sigma baryons...)

  std::vector<HistAndLabels> vOSHistAndLabels; std::vector<HistAndLabels> vSSHistAndLabels;

  // Retrieve histograms from ROOT files, calculate per trigger yield and add them to input vector of the function that calculates the OS and SS correlations.
  std::string path = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_only_82/";

  // Input vectors
  // contain: root file name, trigger name, associate name, plotting range
  
  // OS
  vector<RootFileAndLabels> vOSRootFileAndLabels;
  vOSRootFileAndLabels.push_back({"BplusBminus.root", "B^{+}", "B^{-}", 1e-6, 1e0});
  vOSRootFileAndLabels.push_back({"BplusBcminus.root", "B^{+}", "B_{c}^{-}", 1e-8, 1e-2});
  vOSRootFileAndLabels.push_back({"BplusBzerobar.root", "B^{+}", "#barB^{0}", 1e-6, 1e0});
  vOSRootFileAndLabels.push_back({"BplusBzerobar.root", "B^{+}", "#barB_{s}^{0}", 1e-6, 1e0});
  vOSRootFileAndLabels.push_back({"BplusLb.root", "B^{+}", "#Lambda_{b}^{0}", 1e-8, 1e-2});
  vOSRootFileAndLabels.push_back({"BplusSigmabplus.root", "B^{+}", "#Sigma_{b}^{+}", 1e-8, 1e-2});
  vOSRootFileAndLabels.push_back({"BplusSigmabzero.root", "B^{+}", "#Sigma_{b}^{0}", 1e-8, 1e-2});
  vOSRootFileAndLabels.push_back({"BplusSigmabminus.root", "B^{+}", "#Sigma_{b}^{-}", 1e-8, 1e-2});

  // SS
  vector<RootFileAndLabels> vSSRootFileAndLabels;
  vSSRootFileAndLabels.push_back({"BplusBplus.root", "B^{+}", "B^{+}", -1, -1});
  vSSRootFileAndLabels.push_back({"BplusBcplus.root", "B^{+}", "B_{c}^{+}", -1, -1});
  vSSRootFileAndLabels.push_back({"BplusBzero.root", "B^{+}", "B^{0}", -1, -1});
  vSSRootFileAndLabels.push_back({"BplusBszero.root", "B^{+}", "B_{s}^{0}", -1, -1});
  vSSRootFileAndLabels.push_back({"BplusLbbar.root", "B^{+}", "#bar#Lambda_{b}^{0}", -1, -1});
  vSSRootFileAndLabels.push_back({"BplusSigmabplusbar.root", "B^{+}", "#bar#Sigma_{b}^{+}", -1, -1});
  vSSRootFileAndLabels.push_back({"BplusSigmabzerobar.root", "B^{+}", "#bar#Sigma_{b}^{0}", -1, -1});
  vSSRootFileAndLabels.push_back({"BplusSigmabminusbar.root", "B^{+}", "#bar#Sigma_{b}^{-}", -1, -1});

  for (int i = 0; i < vOSRootFileAndLabels.size(); i++) {

    RootFileAndLabels OS = vOSRootFileAndLabels[i]; RootFileAndLabels SS = vSSRootFileAndLabels[i];

    TFile* OSTree = new TFile((path + OS.RootFile).c_str());
    TFile* SSTree = new TFile((path + SS.RootFile).c_str());

    TH1D* hOSDPhiLL = (TH1D*)OSTree->Get("hDPhiLL");
    TH1D* hOSDPhiII = (TH1D*)OSTree->Get("hDPhiII");
    TH1D* hOSDPhiHH = (TH1D*)OSTree->Get("hDPhiHH");
    TH1D* hOSTrPt = (TH1D*)OSTree->Get("hTrPt");

    TH1D* hSSDPhiLL = (TH1D*)SSTree->Get("hDPhiLL");
    TH1D* hSSDPhiII = (TH1D*)SSTree->Get("hDPhiII");
    TH1D* hSSDPhiHH = (TH1D*)SSTree->Get("hDPhiHH");
    TH1D* hSSTrPt = (TH1D*)SSTree->Get("hTrPt");

    normalise(hOSDPhiLL, hOSTrPt, -1.57, 4.71);
    normalise(hOSDPhiII, hOSTrPt, -1.57, 4.71);
    normalise(hOSDPhiHH, hOSTrPt, -1.57, 4.71);
    
    normalise(hSSDPhiLL, hSSTrPt, -1.57, 4.71);
    normalise(hSSDPhiII, hSSTrPt, -1.57, 4.71);
    normalise(hSSDPhiHH, hSSTrPt, -1.57, 4.71);

    vOSHistAndLabels.push_back({hOSDPhiLL, OS.TriggerName, OS.AssociateName, "Low-Low", OS.DrawYmin, OS.DrawYmax});
    vOSHistAndLabels.push_back({hOSDPhiII, OS.TriggerName, OS.AssociateName, "Int-Int", OS.DrawYmin, OS.DrawYmax});
    vOSHistAndLabels.push_back({hOSDPhiHH, OS.TriggerName, OS.AssociateName, "High-High", OS.DrawYmin, OS.DrawYmax});

    vSSHistAndLabels.push_back({hSSDPhiLL, SS.TriggerName, SS.AssociateName, "Low-Low", SS.DrawYmin, SS.DrawYmax});
    vSSHistAndLabels.push_back({hSSDPhiII, SS.TriggerName, SS.AssociateName, "Int-Int", SS.DrawYmin, SS.DrawYmax});
    vSSHistAndLabels.push_back({hSSDPhiHH, SS.TriggerName, SS.AssociateName, "High-High", SS.DrawYmin, SS.DrawYmax});
    
  }

  bool write = false;
  CalculateOS_minus_SS(vOSHistAndLabels, vSSHistAndLabels, write);

  /*
  // OS
  TFile* BpBmTree = new TFile((path + "BplusBminus.root").c_str());
  TFile* BpBcmTree = new TFile((path + "BplusBcminus.root").c_str());
  TFile* BpB0barTree = new TFile((path + "BplusBzerobar.root").c_str());
  TFile* BpBs0barTree = new TFile((path + "BplusBszerobar.root").c_str());
  TFile* BpLbTree = new TFile((path + "BplusLb.root").c_str());
  // SS
  TFile* BpBpTree = new TFile((path + "BplusBplus.root").c_str());
  TFile* BpBcpTree = new TFile((path + "BplusBcplus.root").c_str());
  TFile* BpB0Tree = new TFile((path + "BplusBzero.root").c_str());
  TFile* BpBs0Tree = new TFile((path + "BplusBszero.root").c_str());
  TFile* BpLbbarTree = new TFile((path + "BplusLbbar.root").c_str());

  // OS
  TH1D* hBpBm = (TH1D*)BpBmTree->Get("hDPhiHH");
  TH1D* hBpBmTrPt = (TH1D*)BpBmTree->Get("hTrPt");
  TH1D* hBpBcm = (TH1D*)BpBcmTree->Get("hDPhiHH");
  TH1D* hBpBcmTrPt = (TH1D*)BpBcmTree->Get("hTrPt");
  TH1D* hBpB0bar = (TH1D*)BpB0barTree->Get("hDPhiHH");
  TH1D* hBpB0barTrPt = (TH1D*)BpB0barTree->Get("hTrPt");
  TH1D* hBpBs0bar = (TH1D*)BpBs0barTree->Get("hDPhiHH");
  TH1D* hBpBs0barTrPt = (TH1D*)BpBs0barTree->Get("hTrPt");
  TH1D* hBpLb = (TH1D*)BpLbTree->Get("hDPhiHH");
  TH1D* hBpLbTrPt = (TH1D*)BpLbTree->Get("hTrPt");
  // SS
  TH1D* hBpBp = (TH1D*)BpBpTree->Get("hDPhiHH");
  TH1D* hBpBpTrPt = (TH1D*)BpBpTree->Get("hTrPt");
  TH1D* hBpBcp = (TH1D*)BpBcpTree->Get("hDPhiHH");
  TH1D* hBpBcpTrPt = (TH1D*)BpBcpTree->Get("hTrPt");
  TH1D* hBpB0 = (TH1D*)BpB0Tree->Get("hDPhiHH");
  TH1D* hBpB0TrPt = (TH1D*)BpB0Tree->Get("hTrPt");
  TH1D* hBpBs0 = (TH1D*)BpBs0Tree->Get("hDPhiHH");
  TH1D* hBpBs0TrPt = (TH1D*)BpBs0Tree->Get("hTrPt");
  TH1D* hBpLbbar = (TH1D*)BpLbbarTree->Get("hDPhiHH");
  TH1D* hBpLbbarTrPt = (TH1D*)BpLbbarTree->Get("hTrPt");

  // OS
  normalise(hBpBm, hBpBmTrPt, -1.57, 4.71);
  normalise(hBpBcm, hBpBcmTrPt, -1.57, 4.71);
  normalise(hBpB0bar, hBpB0barTrPt, -1.57, 4.71);
  normalise(hBpBs0bar, hBpBs0barTrPt, -1.57, 4.71);
  normalise(hBpLb, hBpLbTrPt, -1.57, 4.71);
  // SS
  normalise(hBpBp, hBpBpTrPt, -1.57, 4.71);
  normalise(hBpBcp, hBpBcpTrPt, -1.57, 4.71);
  normalise(hBpB0, hBpB0TrPt, -1.57, 4.71);
  normalise(hBpBs0, hBpBs0TrPt, -1.57, 4.71);
  normalise(hBpLbbar, hBpLbbarTrPt, -1.57, 4.71);

  // OS
  vOSHistAndLabels.push_back({hBpBm, "B^{+}", "B^{-}", 1e-6, 1e-2});
  vOSHistAndLabels.push_back({hBpBcm, "B^{+}", "B_{c}^{-}", 1e-6, 1e-2});
  vOSHistAndLabels.push_back({hBpB0bar, "B^{+}", "B^{0}bar", 1e-6, 1e-2});
  vOSHistAndLabels.push_back({hBpBs0bar, "B^{+}", "B_{s}^{0}bar", 1e-6, 1e-2});
  vOSHistAndLabels.push_back({hBpLb, "B^{+}", "#Lambda_{b}^{0}", 1e-6, 1e-2});
  // SS
  vSSHistAndLabels.push_back({hBpBp, "B^{+}", "B^{+}", 1e-6, 1e-2});
  vSSHistAndLabels.push_back({hBpBcp, "B^{+}", "B_{c}^{+}", 1e-6, 1e-2});
  vSSHistAndLabels.push_back({hBpB0, "B^{+}", "B^{0}", 1e-6, 1e-2});
  vSSHistAndLabels.push_back({hBpBs0, "B^{+}", "B_{s}^{0}", 1e-6, 1e-2});
  vSSHistAndLabels.push_back({hBpLbbar, "B^{+}", "#Lambda_{b}^{0}bar", 1e-6, 1e-2});
  
  CalculateOS_minus_SS(vOSHistAndLabels, vSSHistAndLabels);
  */

  return 0;
  
}
