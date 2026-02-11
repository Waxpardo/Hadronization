// B_Balancing_CompareSimulationSettings.C
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

struct HistAndDrawOptions {
  TH1D* Hist;
  const char* LegendName;
  Color_t Color;
  Int_t LineStyle;
  Double_t LineWidth;
};


struct HistAndLabels {

  TH1D* Hist;
  const char* TriggerName;
  const char* AssociateName;
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

struct SimHistAndLabels { // vector simulaton histograms and labels

  vector<HistAndDrawOptions> vHists; // accessed via different ROOT files, also contains draw options
  const char* TriggerName;
  const char* AssociateName;
  Double_t DrawYmin;
  Double_t DrawYmax;
  
};

// Input vector should countain per trigger yield histograms!
void CalculateOS_minus_SS(std::vector<SimHistAndLabels> vOSHistAndLabels,
			  std::vector<SimHistAndLabels> vSSHistAndLabels,
			  bool write) {

  // Plot yields for different associates
  TCanvas* cYields = new TCanvas("cYields", "cYields", 800, 600);
  setCanvasMargins(cYields, 0.15, 0.1, 0.1, 0.1);

  // Define a template for this plot to set titles, stats, etc.
  TH1D* hYieldsTemplate = new TH1D("hYieldsTemplate", "hYieldsTemplate", vOSHistAndLabels.size(), 0, vOSHistAndLabels.size());

  // When the PtRegions (LL, II, HH) are drawn, some attention is necessary to get the correct line styles and widths
  Int_t PtRegionLineStyles[3] = {3, 5, 1}; 
  Int_t PtRegionLineWidths[3] = {2, 2, 2}; 

  // Define legend for yield plot outside for-loop
  TLegend* lYields = new TLegend(0.53, 0.38, 0.9, 0.18);
  lYields->SetTextSize(0.03);

  
  
  for (int i = 0; i < vOSHistAndLabels.size(); i++) {

    SimHistAndLabels OS = vOSHistAndLabels[i];
    SimHistAndLabels SS = vSSHistAndLabels[i];

    // Compare OS and SS on the same canvas    
    TCanvas* cOverview = new TCanvas(Form("cOverview_%i", i), Form("%s%s and %s%s both drawn for all pT bins", OS.TriggerName, OS.AssociateName, SS.TriggerName, SS.AssociateName), 800, 600);
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
    TLegend* lCorr = new TLegend(0.15, 0.90, 0.50, 0.75);
    lCorr->SetTextSize(0.03);

    std::vector<HistAndDrawOptions> vhDrawOS = OS.vHists; std::vector<HistAndDrawOptions> vhDrawSS = SS.vHists;

    for (int j = 0; j < vhDrawOS.size(); j++ ) { // loop over simulation settings for given trigger-associate pair

      HistAndDrawOptions hDrawOS = vhDrawOS[j]; HistAndDrawOptions hDrawSS = vhDrawSS[j]; // take hist and draw options
      
      TH1D* hOS = hDrawOS.Hist; TH1D* hSS = hDrawSS.Hist; // take hist
      hOS->SetTitle(Form("%s%s #Delta#phi angular correlations", OS.TriggerName, OS.AssociateName));
      hOS->GetYaxis()->SetTitle("#frac{1}{N_{trigger}} #frac{dN}{d#Delta#phi}");
      hOS->GetYaxis()->SetRangeUser(OS.DrawYmin, OS.DrawYmax);
      hOS->SetStats(0);
      hOS->SetLineColor(hDrawOS.Color);
      hSS->SetLineColor(hDrawOS.Color);      
      hOS->SetLineStyle(1); hOS->SetLineWidth(2);
      hSS->SetLineStyle(3); hSS->SetLineWidth(2);

      cOverview->cd();
      mainPad->cd();
      if (i == 0 && j == 0) { hOS->Draw("hist E"); hSS->Draw("same hist E"); }
      else { hOS->Draw("same hist E"); hSS->Draw("same hist E"); }
      
      lOverview->AddEntry(hOS, Form("OS = %s%s (%s)", OS.TriggerName, OS.AssociateName, hDrawOS.LegendName));
      lOverview->AddEntry(hSS, Form("SS = %s%s (%s)", SS.TriggerName, SS.AssociateName, hDrawSS.LegendName));
      
      TH1D* hCorr = (TH1D*)hOS->Clone();
      hCorr->SetLineColor(hDrawOS.Color);
      hCorr->Add(hSS, -1.);
      hCorr->GetYaxis()->SetRangeUser(OS.DrawYmin, OS.DrawYmax);
      hCorr->SetTitle("OS - SS");
      hCorr->SetTitleSize(0.8);
      hCorr->GetXaxis()->SetLabelSize(0.07);
      hCorr->GetYaxis()->SetLabelSize(0.07);
      hCorr->GetYaxis()->SetTitle("");
      hCorr->GetXaxis()->SetTitle("");

      lCorr->AddEntry(hCorr, Form("OS - SS (%s)", hDrawOS.LegendName));
      
      miniPad->cd();
      if (i == 0 && j == 0) { hCorr->Draw("hist E"); }
      else { hCorr->Draw("same hist E"); }

      TH1D* hYields[5][4]; 
      hYields[i][j] = new TH1D(Form("hYields_%i_%i", i, j), Form("hYields_%i_%i", i, j), vOSHistAndLabels.size(), 0, vOSHistAndLabels.size());
	
      Double_t yield = hCorr->Integral();
      std::cout << Form("yield for %s associate (setting = %s) = ", OS.AssociateName, hDrawOS.LegendName) << yield*1e3 << "e-3" << std::endl;
	
      // Note: division by 3 to get proper bin number
      // Custom error until I figure out what to do with the error
      cYields->cd();

      if (i == 0 && j == 0) {
	hYieldsTemplate->SetTitle("integrated yields for B^{+} trigger (all pT bins)");
	hYieldsTemplate->GetYaxis()->SetTitle("Yield");
	hYieldsTemplate->GetXaxis()->SetTitle("Associate");
	hYieldsTemplate->GetXaxis()->SetLabelSize(0.05);
	hYieldsTemplate->SetStats(0);
	hYieldsTemplate->GetYaxis()->SetRangeUser(1e-4, 10.);
	hYieldsTemplate->Draw("PE");
      }

      if (i == 0) { lYields->AddEntry(hYields[i][j], Form("%s", hDrawOS.LegendName)); }
      
      hYields[i][j]->SetBinContent(i+1, yield);
      hYields[i][j]->SetBinError(i+1, 1e-9); // until I figure out what to do with the large error bars I get
      // hYields[i][j]->SetLineStyle(PtRegionLineStyles[j-i]);
      // hYields[i][j]->SetLineWidth(PtRegionLineWidths[j-i]);
      hYields[i][j]->SetLineColor(hDrawOS.Color);
      hYields[i][j]->SetMarkerColor(hDrawOS.Color);
      hYields[i][j]->Draw("same PE");
      
      } // END OF j for-loop over simulation settings
      
    // Draw canvas and legend of superimposed PtRegions
    cOverview->cd();
    mainPad->cd(); gPad->SetLogy(); // lOverview->Draw();
    lCorr->Draw();
    miniPad->cd(); gPad->SetLogy(); 
    cOverview->Draw();
    
    // Define associate label names for yield plots
    hYieldsTemplate->GetXaxis()->SetBinLabel(1+i, OS.AssociateName);
    
  } // END OF i for-loop over input vector

  // Draw canvas and legend of yields for different associates
  cYields->cd(); gPad->SetLogy(); cYields->Draw(); lYields->Draw();
  if (write) { cYields->SaveAs("Plots/BpYields/BpYields.pdf"); }

} // END OF function declaration

int B_Balancing_CompareSimulationSettings() {

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

  std::vector<SimHistAndLabels> vOSHistAndLabels; std::vector<SimHistAndLabels> vSSHistAndLabels;

  // Retrieve histograms from ROOT files, calculate per trigger yield and add them to input vector of the function that calculates the OS and SS correlations.
  // Paths are numbered as in DESCRIPTIONS.txt
  std::string path_211 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_211/";
  std::string path_221 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_221/";
  std::string path_231 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_231/";
  std::string path_241 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_241/";
  std::vector<std::string> vPaths;
  vPaths.push_back(path_211); vPaths.push_back(path_221); vPaths.push_back(path_231); vPaths.push_back(path_241);

  // The arrays below are tied to the property of the n-th entry in the vector above
  // They are used to label the simulation settings
  // Other implementations are also possible
  const char* vLegendNames[4] =
    {
      "hardbbbar, pTHatMin = 1",
      "hardbbbar, pTHatMin = 10",
      "allQCD, pTHatMin = 1",
      "allQCD, pTHatMin = 10"
    };
  Color_t vColours[4] = {kBlack, kRed, kViolet, kBlue};
  Int_t vLineStyles[4] = {1, 1, 1, 1};
  Double_t vLineWidths[4] = {1, 1, 3, 1};

  // Input vectors
  // contain: root file name, trigger name, associate name, plotting range
  
  // OS
  vector<RootFileAndLabels> vOSRootFileAndLabels;
  vOSRootFileAndLabels.push_back({"BplusBminus.root", "B^{+}", "B^{-}", 1e-4, 1e0});
  vOSRootFileAndLabels.push_back({"BplusBcminus.root", "B^{+}", "B_{c}^{-}", 1e-8, 1e-2});
  vOSRootFileAndLabels.push_back({"BplusBzerobar.root", "B^{+}", "#barB^{0}", 1e-5, 1e0});
  vOSRootFileAndLabels.push_back({"BplusBzerobar.root", "B^{+}", "#barB_{s}^{0}", 1e-6, 1e0});
  vOSRootFileAndLabels.push_back({"BplusLb.root", "B^{+}", "#Lambda_{b}^{0}", 1e-6, 1e-2});

  // SS
  vector<RootFileAndLabels> vSSRootFileAndLabels;
  vSSRootFileAndLabels.push_back({"BplusBplus.root", "B^{+}", "B^{+}", -1, -1});
  vSSRootFileAndLabels.push_back({"BplusBcplus.root", "B^{+}", "B_{c}^{+}", -1, -1});
  vSSRootFileAndLabels.push_back({"BplusBzero.root", "B^{+}", "B^{0}", -1, -1});
  vSSRootFileAndLabels.push_back({"BplusBszero.root", "B^{+}", "B_{s}^{0}", -1, -1});
  vSSRootFileAndLabels.push_back({"BplusLbbar.root", "B^{+}", "#bar#Lambda_{b}^{0}", -1, -1});

  for (int i = 0; i < vOSRootFileAndLabels.size(); i++) {

    RootFileAndLabels OS = vOSRootFileAndLabels[i]; RootFileAndLabels SS = vSSRootFileAndLabels[i];
    
    // These vectors save ROOT files with different simulation settings
    // so that they can be compared in the same yield plot
    std::vector<HistAndDrawOptions> vHistsOS; std::vector<HistAndDrawOptions> vHistsSS; 

    for (int j = 0; j < vPaths.size(); j++) {
    
      std::string path = vPaths[j];
    
      TFile* OSTree = new TFile((path + OS.RootFile).c_str());
      TFile* SSTree = new TFile((path + SS.RootFile).c_str());

      TH1D* hOSDPhi = (TH1D*)OSTree->Get("hDPhi");
      TH1D* hOSTrPt = (TH1D*)OSTree->Get("hTrPt");

      TH1D* hSSDPhi = (TH1D*)SSTree->Get("hDPhi");
      TH1D* hSSTrPt = (TH1D*)SSTree->Get("hTrPt");

      if (j != 0) { // Prevent double counting
	hSSDPhi->Scale(1./2);
	hSSTrPt->Scale(1./2);
      }
      
      normalise(hOSDPhi, hOSTrPt, -1.57, 4.71);
      normalise(hSSDPhi, hSSTrPt, -1.57, 4.71);
    
      vHistsOS.push_back({hOSDPhi, vLegendNames[j], vColours[j], vLineStyles[j], vLineWidths[j]});
      vHistsSS.push_back({hSSDPhi, vLegendNames[j], vColours[j], vLineStyles[j], vLineWidths[j]});
    
    } // END OF for-loop over trigger-associate pairs i

    vOSHistAndLabels.push_back({vHistsOS, OS.TriggerName, OS.AssociateName, OS.DrawYmin, OS.DrawYmax});
    vSSHistAndLabels.push_back({vHistsSS, SS.TriggerName, SS.AssociateName, SS.DrawYmin, SS.DrawYmax});
    
  } // END OF for-loop over simulation settings j

  bool write = false;
  CalculateOS_minus_SS(vOSHistAndLabels, vSSHistAndLabels, write);

  return 0;
  
}
