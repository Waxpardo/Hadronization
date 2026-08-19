// B_Balancing_MakeOutputYields.C
// Macro that calculates the yields as before, but takes a root file as input, so that the output yields are created in batches too.
// This allows for sampling in order to calculate errors


void normalise(TH1D* hist, TH1D* trig, Double_t xmin, Double_t xmax) {
	Int_t bin_start = trig->FindBin(xmin);
	Int_t bin_finish = trig->FindBin(xmax);
	Double_t integral = trig->Integral(bin_start, bin_finish);
	std::cout << "function integral = " << integral << std::endl;
	hist->Scale(1./integral);
}

bool isInArray(int num, int arr[], int size) {
    for (int i = 0; i < size; ++i) {
        if (arr[i] == num) {
            return true; // If num is found in the array, return true
        }
    }
    return false; // If num is not found in the array, return false
}

const char* concatString(const char* str1, const char* str2) {
  
  // Calculate the length of the concatenated string
  size_t len1 = strlen(str1);
  size_t len2 = strlen(str2);
  size_t totalLen = len1 + len2 + 1; // +1 for null terminator

  // Allocate memory for the concatenated string
  char* concatenated = new char[totalLen];
  // Copy the first string
  strcpy(concatenated, str1);
  // Add a space
  strcat(concatenated, " ");
  // Concatenate the second string
  strcat(concatenated, str2);
  
  // Debugging
  // std::cout << "Concatenated string: " << concatenated << std::endl;

  return concatenated;
}

void setCanvasMargins(TCanvas *canvas, double_t LeftMargin, double_t RightMargin, double_t TopMargin, double_t BottomMargin) {
  canvas->SetLeftMargin(LeftMargin);
  canvas->SetRightMargin(RightMargin);
  canvas->SetTopMargin(TopMargin);
  canvas->SetBottomMargin(BottomMargin);
}
  
struct BaseLabels {
  const char* LegendTitle;
  Color_t Color;
  Int_t LineStyle;
  Int_t LineWidth;
};

struct PathAndLabels : public BaseLabels {
  std::string Path;
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

// Input vector should countain per trigger yield histograms!
TTree* CalculateOS_minus_SS(Int_t Nbatch, const char* treeName,
			  std::vector<HistAndLabels> vHistAndLabels,
			  const char* plotTitle, Int_t Nhist,
			  Bool_t junctions = false, Bool_t division = false,
			  Bool_t write = false) {

  // + = + = + = + = + = + = + = + = + = + = + = + = + = + = + = + = + + = + = + = + = + = + = + = + = + = + = + = + = + = + = + = +
  // Integer of the associate of interest for the relative yields
  // Hard-coded for now
  Int_t NAssociates = 1;
  Int_t intAssociate[1] = {3};
  Int_t counterLineStyle = 0; // Used to iterate over intAssociate

  // The line styles and widths are also hard-coded
  Int_t RelYieldsLineStyles[2] = {1, 2};
  Int_t RelYieldsLineWidths[2] = {1, 2};

  // + = + = + = + = + = + = + = + = + = + = + = + = + = + = + = + = + + = + = + = + = + = + = + = + = + = + = + = + = + = + = + = +
  // When MONASH and JUNCTIONS are involved, the number of histograms is doubled compared to the
  // actual number of configurations
  Int_t Nconfigs;
  if (!junctions) { Nconfigs = Nhist; }
  if (junctions) { Nconfigs = Nhist/2; }

  std::cout << "Nconfigs = " << Nconfigs << std::endl;
  std::cout << std::endl;

  // Plot yields for different associates
  TCanvas* cYields = new TCanvas(Form("cYields_%s", plotTitle), "cYields", 800, 600);
  setCanvasMargins(cYields, 0.15, 0.1, 0.1, 0.20);

  // Plot the B+B-/B+Lb yield as a function of the configurations (pT, multiplicity, rapidity, ...)
  TCanvas* cRelYields = new TCanvas(Form("cRelYields_%s", plotTitle), "cRelYields", 800, 600);
  setCanvasMargins(cRelYields, 0.15, 0.25, 0.1, 0.25);

  // Plot the charm/beauty yields for different combinations
  TCanvas* cDivYields = new TCanvas(Form("cDivYields_%s", plotTitle), "cDivYields", 800, 600);
  setCanvasMargins(cRelYields, 0.15, 0.25, 0.1, 0.25);

  // Define a template for this plot to set titles, stats, etc.
  TH1D* hYieldsTemplate = new TH1D(Form("hYieldsTemplate_%s", plotTitle), "hYieldsTemplate", vHistAndLabels.size()/Nhist, 0, vHistAndLabels.size()/Nhist);

  TH1D* hYieldsRatioTemplate = new TH1D(Form("hYieldsRatioTemplate_%s", plotTitle), "hYieldsRatioTemplate", vHistAndLabels.size()/Nhist, 0, vHistAndLabels.size()/Nhist);
  
  TH1D* hRelYieldsTemplate = new TH1D(Form("hRelYieldsTemplate_%s", plotTitle), "hRelYieldsTemplate", Nconfigs, 0, Nconfigs);

  TH1D* hRelYieldsRatioTemplate = new TH1D(Form("hRelYieldsRatioTemplate_%s", plotTitle), "hRelYieldsRatioTemplate", Nconfigs, 0, Nconfigs);

  TH1D* hDivYieldsTemplate;

  // Figure this out when I start working with the charm/beauty divided yields again
  if (!junctions) { hDivYieldsTemplate = new TH1D(Form("hDivYieldsTemplate_%s", plotTitle), "hDivYieldsTemplate", (vHistAndLabels.size()/Nconfigs)/2, 0, (vHistAndLabels.size()/Nconfigs)/2); }
  if (junctions) { hDivYieldsTemplate = new TH1D(Form("hDivYieldsTemplate_%s", plotTitle), "hDivYieldsTemplate", (vHistAndLabels.size()/Nconfigs)/4, 0, (vHistAndLabels.size()/Nconfigs)/4); }

  cYields->cd();
  hYieldsTemplate->SetTitle(plotTitle);
  hYieldsTemplate->GetYaxis()->SetTitle("Yield");
  if (!junctions) { hYieldsTemplate->GetXaxis()->SetTitle("Associate"); }
  hYieldsTemplate->GetXaxis()->SetLabelSize(0.05);
  hYieldsTemplate->SetStats(0);
  hYieldsTemplate->GetYaxis()->SetRangeUser(1e-4, 1e0); // 1e-4, 1e0
  if (!junctions) { hYieldsTemplate->Draw("PE"); }

  cRelYields->cd();
  hRelYieldsTemplate->SetTitle(plotTitle);
  hRelYieldsTemplate->GetYaxis()->SetTitle("relative yield");
  hRelYieldsTemplate->GetXaxis()->SetLabelSize(0.05);
  hRelYieldsTemplate->SetStats(0);
  hRelYieldsTemplate->GetYaxis()->SetRangeUser(5e-1, 0.25); // for beauty: (5e-1,0.5)
  if (!junctions) { hRelYieldsTemplate->Draw("PE"); }

  if (division) {
    cDivYields->cd();
    hDivYieldsTemplate->SetTitle(plotTitle);
    hDivYieldsTemplate->GetYaxis()->SetTitle("relative yield");
    hDivYieldsTemplate->GetXaxis()->SetLabelSize(0.05);
    hDivYieldsTemplate->SetStats(0);
    hDivYieldsTemplate->GetYaxis()->SetRangeUser(1e-1, 300);
    hDivYieldsTemplate->Draw("PE");
  }

  // When plotting JUNCTIONS yields, it is also interesting to divide them by the MONASH yields
  // for a better comparison. This is set up here and regulated later by the junctions bool
  TPad* mainPadJunctions = new TPad(Form("mainPadJunctions_%s", plotTitle), "mainPad", 0.05, 0.30, 0.95, 0.95);
  mainPadJunctions->SetBottomMargin(0);
  mainPadJunctions->SetRightMargin(0.1);
  TPad* miniPadJunctions = new TPad(Form("miniPadJunctions_%s", plotTitle), "miniPad", 0.05, 0.10, 0.95, 0.30);
  miniPadJunctions->SetTopMargin(0);
  miniPadJunctions->SetBottomMargin(0.35);
  mainPadJunctions->SetRightMargin(0.1);
  
  if (junctions) {
    cYields->cd();
    mainPadJunctions->Draw(); miniPadJunctions->Draw();

    hYieldsTemplate->SetMinimum(5e-5); // 5e-5

    hYieldsRatioTemplate->SetTitle("");
    hYieldsRatioTemplate->GetYaxis()->SetTitle("JUN / MON");
    hYieldsRatioTemplate->GetXaxis()->SetTitle("Associate");
    hYieldsRatioTemplate->GetXaxis()->SetLabelSize(0.05);
    hYieldsRatioTemplate->SetStats(0);
    hYieldsRatioTemplate->GetYaxis()->SetRangeUser(5e-2, 50);

    hYieldsRatioTemplate->GetYaxis()->SetLabelSize(3*0.035);
    hYieldsRatioTemplate->GetYaxis()->SetTitleSize(3.0*0.035);
    hYieldsRatioTemplate->GetYaxis()->SetTitleOffset(12*0.035);
    hYieldsRatioTemplate->GetXaxis()->SetTickLength(3*0.035);
    hYieldsRatioTemplate->GetXaxis()->SetLabelOffset(0.035);
    hYieldsRatioTemplate->GetXaxis()->SetTitleSize(3*0.035);
    hYieldsRatioTemplate->GetXaxis()->SetTitleOffset(50*0.035);
    hYieldsRatioTemplate->SetLabelSize(3*0.05);
    
    mainPadJunctions->cd(); hYieldsTemplate->Draw("PE");
    miniPadJunctions->cd(); hYieldsRatioTemplate->Draw("PE");
  }

  // We do the same for the relative plots (e.g. B+B-/B+Lb) to show explicit dependencies
  TPad* mainPadRelJunctions = new TPad(Form("mainPadRelJunctions_%s", plotTitle), "mainPad", 0.05, 0.30, 0.95, 0.95);
  mainPadRelJunctions->SetBottomMargin(0);
  mainPadRelJunctions->SetRightMargin(0.1);
  TPad* miniPadRelJunctions = new TPad(Form("miniPadRelJunctions_%s", plotTitle), "miniPad", 0.05, 0.10, 0.95, 0.30);
  miniPadRelJunctions->SetTopMargin(0);
  miniPadRelJunctions->SetBottomMargin(0.45);
  mainPadRelJunctions->SetRightMargin(0.1);
  
  if (junctions) {
    cRelYields->cd();
    mainPadRelJunctions->Draw(); miniPadRelJunctions->Draw();

    hRelYieldsTemplate->SetMinimum(1e-2); // for beauty: 1e-2

    hRelYieldsRatioTemplate->SetTitle("");
    hRelYieldsRatioTemplate->GetYaxis()->SetTitle("JUN / MON");
    hRelYieldsRatioTemplate->GetXaxis()->SetLabelSize(0.05);
    hRelYieldsRatioTemplate->SetStats(0);
    hRelYieldsRatioTemplate->GetYaxis()->SetRangeUser(0, 5); // for beauty: (1,7)
    hRelYieldsRatioTemplate->SetMaximum(5.49); // for beauty: 7.49

    hRelYieldsRatioTemplate->GetYaxis()->SetLabelSize(3*0.035);
    hRelYieldsRatioTemplate->GetYaxis()->SetTitleSize(3.0*0.035);
    hRelYieldsRatioTemplate->GetYaxis()->SetTitleOffset(12*0.035);
    hRelYieldsRatioTemplate->GetXaxis()->SetTickLength(3*0.035);
    hRelYieldsRatioTemplate->GetXaxis()->SetLabelOffset(0.035);
    hRelYieldsRatioTemplate->GetXaxis()->SetTitleSize(3*0.035);
    hRelYieldsRatioTemplate->GetXaxis()->SetTitleOffset(50*0.035);
    hRelYieldsRatioTemplate->SetLabelSize(3*0.05);
    
    mainPadRelJunctions->cd(); hRelYieldsTemplate->Draw("PE");
    miniPadRelJunctions->cd(); hRelYieldsRatioTemplate->Draw("PE");
  }

  // Define legend for yield plot outside for-loop
  TLegend* lYields = new TLegend(0.63, 0.88, 0.9, 0.58);
  lYields->SetTextSize(0.03);

  TLegend* lRelYields = new TLegend(0.63, 0.88, 0.9, 0.68);
  lRelYields->SetTextSize(0.03);

  TLegend* lDivYields = new TLegend(0.63, 0.88, 0.9, 0.68);
  lDivYields->SetTextSize(0.03);

  // In order not to condense the information displayed in the legend
  if (junctions) {
    TLegendEntry* entryMonash = lYields->AddEntry("Monash", "MONASH (MON)", "l");
    entryMonash->SetLineColor(kBlack);
    entryMonash->SetLineStyle(1);
    entryMonash->SetLineWidth(2);

    TLegendEntry* entryJunctions = lYields->AddEntry("Junctions", "JUNCTIONS (JUN)", "l");
    entryJunctions->SetLineColor(kRed);
    entryJunctions->SetLineStyle(1);
    entryJunctions->SetLineWidth(2);

    TLegendEntry* entryMonashRel = lRelYields->AddEntry("MonashRel", "MONASH", "l");
    entryMonashRel->SetLineColor(kBlack);
    entryMonashRel->SetLineStyle(1);
    entryMonashRel->SetLineWidth(1);

    TLegendEntry* entryJunctionsRel = lRelYields->AddEntry("JunctionsRel", "JUNCTIONS", "l");
    entryJunctionsRel->SetLineColor(kRed);
    entryJunctionsRel->SetLineStyle(1);
    entryJunctionsRel->SetLineWidth(1);

    TLegendEntry* entryMonashDiv = lDivYields->AddEntry("MonashDiv", "MONASH", "l");
    entryMonashDiv->SetLineColor(kBlack);
    entryMonashDiv->SetLineStyle(1);
    entryMonashDiv->SetLineWidth(1);

    TLegendEntry* entryJunctionsDiv = lDivYields->AddEntry("JunctionsDiv", "JUNCTIONS", "l");
    entryJunctionsDiv->SetLineColor(kRed);
    entryJunctionsDiv->SetLineStyle(1);
    entryJunctionsDiv->SetLineWidth(1);
  }

  // Draw canvas and legend of yields for different associates
  if (!junctions) {
     cYields->cd(); gPad->SetLogy();
     cYields->Draw();
     lYields->Draw();
     cRelYields->cd(); // gPad->SetLogy();
     lRelYields->Draw();
  }
  if (junctions) {
    cYields->cd();
    mainPadJunctions->cd(); gPad->SetLogy();
    lYields->Draw();
    miniPadJunctions->cd(); gPad->SetLogy();

    cRelYields->cd();
    mainPadRelJunctions->cd(); // gPad->SetLogy();
    lRelYields->Draw();
    miniPadRelJunctions->cd(); // gPad->SetLogy(); 
  }

  if (division) { cDivYields->cd(); gPad->SetLogy(); lDivYields->Draw(); }

  // Check for memory-error
  std::cout << "If this message is followed by a memory error:" << std::endl;
  std::cout << "most likely the intAssociate variable at the beginning of the code has not been changed yet" << std::endl;
  std::cout << "i.e. you are trying to access an associate number which is out of bounds" << std::endl;

  // The yields are stored in a 3D-array with structure [associate][tune][condition]
  // in order to maintain clarity and to allow for more flexible filling of dependencies
  Double_t vYields[vHistAndLabels.size()/Nhist][2][Nconfigs]; // save to output
  TH1D* hYieldsRatio[vHistAndLabels.size()/Nhist][Nhist/2]; // change to Nconfigs?
  // [tune][condition]
  TH1D* hRelYields[2][Nconfigs];
  TH1D* hRelYieldsRatio[Nconfigs];

  // The charm/beauty yield histograms have structure [associate][tune][condition]
  Double_t vDivYieldsCharm[vHistAndLabels.size()/Nhist][2][Nconfigs];
  Double_t vDivYieldsBeauty[vHistAndLabels.size()/Nhist][2][Nconfigs];
  TH1D* hDivYields[vHistAndLabels.size()][2][Nconfigs];

  std::cout << std::endl;
  std::cout << "If you see this message, ignore the previous. Set-up was successful" << std::endl;
  std::cout << std::endl;

  // Create output file to store yields, this will be used for sampling to estimate the error bars on the values
  // TFile* outputFile = new TFile(Form("yieldOutput_%i.root", Nbatch), "RECREATE");
  TTree* outputTree = new TTree(Form("YieldsTree_%s", treeName), "Tree containing yields[Associate][Tune][Config] array");
  outputTree->Branch("vYields", vYields, Form("vYields[%d][2][%d]/D", int(vHistAndLabels.size()/Nhist), int(Nconfigs)));

  Int_t vHistAndLabelsSize = vHistAndLabels.size();
  outputTree->Branch("vHistAndLabelsSize", &vHistAndLabelsSize);
  outputTree->Branch("Nhist", &Nhist);
  outputTree->Branch("Nconfigs", &Nconfigs);


  


  
  for (Int_t i = 0; i < vHistAndLabels.size(); i+=Nhist) {

    HistAndLabels histEntry = vHistAndLabels[i];

    // Compare OS and SS on the same canvas    
    TCanvas* cOverview = new TCanvas(Form("cOverview_%s_%i", plotTitle, i), Form("%s%s and %s%s both drawn for %s", histEntry.TriggerName, histEntry.AssociateNameOS, histEntry.TriggerName, histEntry.AssociateNameSS, histEntry.LegendTitle), 800, 600);
    // setCanvasMargins(cOverview, 0.15, 0.1, 0.1, 0.1);
    // cOverview->cd();
    /*
    // Subtract OS from SS to get the background reduced plots
    TCanvas* cCorr = new TCanvas(Form("cCorr_%i", i), Form("%s%s - %s%s for %s", OS.TriggerName, OS.AssociateName, SS.TriggerName, SS.AssociateName, OS.PtRegion), 800, 600);
    setCanvasMargins(cCorr, 0.15, 0.1, 0.1, 0.1);
    */
    TPad* mainPad = new TPad(Form("mainPad_%s_%i", plotTitle, i), "mainPad", 0.03, 0.3, 1.0, 1.0);
    mainPad->Draw();
    TPad* miniPad = new TPad(Form("miniPad_%s_%i", plotTitle, i), "miniPad", 0.03, 0.0, 1.0, 0.3);
    miniPad->Draw();
    Double_t mod = 0.7 / 0.3;

    TLegend* lOverview = new TLegend(0.20, 0.88, 0.40, 0.68);
    lOverview->SetTextSize(0.03);
    TLegend* lCorr = new TLegend(0.65, 0.88, 0.85, 0.78);
    lCorr->SetTextSize(0.03);




    
    for (int j = i; j < i+Nhist; j++) {

      if (j != i) // Redefine to access all histograms in j-loop
	{ histEntry = vHistAndLabels[j]; }

      TH1D* hDPhiOS = histEntry.hDPhiOS; TH1D* hDPhiSS = histEntry.hDPhiSS;
      hDPhiOS->SetTitle(Form("%s%s #Delta#phi angular correlations", histEntry.TriggerName, histEntry.AssociateNameOS));
      hDPhiOS->GetXaxis()->SetTitle("#Delta#phi (rad)");
      hDPhiOS->GetYaxis()->SetTitle("#frac{1}{N_{trigger}} #frac{dN}{d#Delta#phi}");
      hDPhiOS->GetYaxis()->SetRangeUser(histEntry.DrawYmin, histEntry.DrawYmax);
      hDPhiOS->SetStats(0);
      hDPhiOS->SetLineColor(kRed);
      hDPhiOS->SetLineStyle(histEntry.LineStyle);
      hDPhiOS->SetLineWidth(histEntry.LineWidth);
      hDPhiSS->SetLineColor(kBlue);
      hDPhiSS->SetLineStyle(histEntry.LineStyle);
      hDPhiSS->SetLineWidth(histEntry.LineWidth);
      
      // cOverview->cd();
      // mainPad->cd();
      // if (j == i) { hDPhiOS->Draw("hist E"); hDPhiSS->Draw("same hist E"); }
      // else { hDPhiOS->Draw("same hist E"); hDPhiSS->Draw("same hist E"); }
      
      lOverview->AddEntry(hDPhiOS, Form("OS = %s%s (%s)", histEntry.TriggerName, histEntry.AssociateNameOS, histEntry.LegendTitle));
      lOverview->AddEntry(hDPhiSS, Form("SS = %s%s (%s)", histEntry.TriggerName, histEntry.AssociateNameSS, histEntry.LegendTitle));
      
      TH1D* hCorr = (TH1D*)hDPhiOS->Clone();
      hCorr->Add(hDPhiSS, -1.);
      // normalise(hCorr, histEntry.hTrPtOS, -1.57, 4.71); // OPTION: normalise after subtraction
      
      hCorr->GetYaxis()->SetRangeUser(histEntry.DrawYmin, histEntry.DrawYmax);
      hCorr->SetTitle("OS - SS");
      hCorr->SetTitleSize(0.8);
      hCorr->GetXaxis()->SetLabelSize(0.07);
      hCorr->GetYaxis()->SetLabelSize(0.07);
      hCorr->GetYaxis()->SetTitle("");
      hCorr->GetXaxis()->SetTitle("");
      hCorr->SetLineColor(kBlack);
      hCorr->SetLineStyle(histEntry.LineStyle);
      hCorr->SetLineWidth(histEntry.LineWidth);

      // lCorr->AddEntry(hCorr, Form("%s%s (%s)", OS.TriggerName, OS.AssociateName, OS.PtRegion));
      lCorr->AddEntry(hCorr, Form("OS - SS (%s)", histEntry.LegendTitle));
      
      // cCorr->cd();
      miniPad->cd();
      // if (j == i) { hCorr->Draw("hist E"); }
      // else { hCorr->Draw("same hist E"); }

      // Yield is calculated using the whole DPhi range, can be changed if desired
      TH1D* hYields[vHistAndLabels.size()/Nhist][Nhist]; 
      hYields[i/Nhist][j-i] = new TH1D(Form("hYields_%s_%i_%i", plotTitle, i, j), Form("hYields_%i_%i", i, j), vHistAndLabels.size()/Nhist, 0, vHistAndLabels.size()/Nhist);

      // Divide JUNCTIONS by MONASH (only need half of the entries c.f. before)
      if (junctions && (j-i) < Nhist/2) {
	hYieldsRatio[i/Nhist][j-i] = new TH1D(Form("hYieldsRatio_%s_%i_%i", plotTitle, i, j), Form("hYieldsRatio_%i_%i", i, j), vHistAndLabels.size()/Nhist, 0, vHistAndLabels.size()/Nhist);
      }

      // Calculate the yields, the region can be specified if desired
      Double_t yield = hCorr->Integral();
      std::cout << Form("yield for %s associate (%s) = ", histEntry.AssociateNameOS, histEntry.LegendTitle) << yield*1e3 << "e-3" << std::endl;

      // For JUNCTIONS:
      // The yields are stored in a 3D-array with structure [associate][tune][condition]
      // in order to maintain clarity and to allow for more flexible filling of dependencies

      // MONASH (first half of entries)
      // Nconfigs = Nhist/2 when JUNCTIONS = true
      // Nconfigs = Nhist when JUNCTIONS = false
      if (j-i < Nconfigs) {
	vYields[i/Nhist][0][j-i] = yield; }

      // JUNCTIONS (second half of entries)
      if (junctions && j-i >= Nhist/2) { vYields[i/Nhist][1][(j-i)-Nhist/2] = yield; }

      if (junctions && j-i < Nhist/2) {
	hYieldsRatio[i/Nhist][j-i]->SetLineStyle(histEntry.LineStyle);
	hYieldsRatio[i/Nhist][j-i]->SetLineWidth(histEntry.LineWidth);
	hYieldsRatio[i/Nhist][j-i]->SetLineColor(kBlack);
	hYieldsRatio[i/Nhist][j-i]->SetMarkerColor(kBlack);
      }

      // Fill yield arrays for charm/beauty yield division plots
      // These arrays are seperate from the former arrays as the plots are to been
      // regarded as standalone from the others
      // CHARM (first half of entries) -----------------------------------------
      if (division && i < vHistAndLabels.size()/2) {

	// std::cout << "CHARM i/Nhist = " << i/Nhist << std::endl;

	// MONASH
	if (j-i < Nconfigs) {
	  vDivYieldsCharm[i/Nhist][0][j-i] = yield;
	  }

	// JUNCTIONS
	if (j-i > Nconfigs) {
	  vDivYieldsCharm[i/Nhist][1][(j-i)-Nconfigs] = yield; // CHECK
	}
      }

      // BEAUTY ----------------------------------------------------------------
      if (division && i >= vHistAndLabels.size()/2) {

	/*
	std::cout << std::endl;
	std::cout << "Nhist = " << Nhist << std::endl;
	std::cout << "i = " << i << std::endl;
	std::cout << "j = " << j << std::endl;
	std::cout << "j-i = " << j-i << std::endl;
	std::cout << "i/Nhist = " << i/Nhist << std::endl;
	std::cout << "(i-vHistAndLabels.size()/2)/Nhist = " << (i-vHistAndLabels.size()/2)/Nhist << std::endl;
	std::cout << std::endl;
	*/		
	
	// MONASH
	if (j-i < Nconfigs) {
	  vDivYieldsBeauty[(i-vHistAndLabels.size()/2) / Nhist][0][j-i] = yield;
	  }

	// JUNCTIONS
	if (j-i > Nconfigs) {
	  vDivYieldsBeauty[(i-vHistAndLabels.size()/2) / Nhist][1][(j-i)-Nconfigs] = yield; // CHECK
	}
      }
	
      // NOTE: Custom error until error propagation is correctly implemented
      // same case below for the ratio histograms
      hYields[i/Nhist][j-i]->SetBinContent(1+i/Nhist, yield);
      hYields[i/Nhist][j-i]->SetBinError(1+i/Nhist, 1e-9); // until error propagation is correctly implemented
      hYields[i/Nhist][j-i]->SetLineStyle(histEntry.LineStyle);
      hYields[i/Nhist][j-i]->SetLineWidth(histEntry.LineWidth);
      hYields[i/Nhist][j-i]->SetLineColor(histEntry.Color);
      hYields[i/Nhist][j-i]->SetMarkerColor(histEntry.Color);
      // hYields[i/Nhist][j-i]->SetMarkerStyle(1);
      
      cYields->cd();
      if (!junctions) { hYields[i/Nhist][j-i]->Draw("same PE"); }
      if (junctions) { mainPadJunctions->cd(); hYields[i/Nhist][j-i]->Draw("same PE"); }
      
      // Condense the information displayed in the legend for
      // MONASH + JUNCTIONS to only show MONASH
      if (i == 0 && junctions && j < Nhist/2) { lYields->AddEntry(hYields[i/Nhist][j-i], Form("%s", histEntry.LegendTitle)); }
      if (i == 0 && !junctions) { lYields->AddEntry(hYields[i/Nhist][j-i], Form("%s", histEntry.LegendTitle)); }

      // Define associate label names for relative yield plot
      // (i == 0) because it only needs to be done once
      if (i == 0 && j < Nconfigs && !junctions) { hRelYieldsTemplate->GetXaxis()->SetBinLabel(1+(j-i), histEntry.LegendTitle); }
      if (i == 0 && j < Nconfigs && junctions) { hRelYieldsRatioTemplate->GetXaxis()->SetBinLabel(1+(j-i), histEntry.LegendTitle); }
      
      } // END OF j for-loop over configurations

    // Draw ratios of JUNCTIONS / MONASH yields
    miniPadJunctions->cd();
    if (junctions) { for (Int_t k = 0; k < Nhist/2; k++) {
	
	// Get the JUNCTIONS / MONASH yield, given that MONASH is stored before JUNCTIONS in the
	// input configurations
	Double_t yieldMonash = 0; Double_t yieldJunctions = 0;
	yieldMonash = vYields[i/Nhist][0][k];
	yieldJunctions = vYields[i/Nhist][1][k];
      
	hYieldsRatio[i/Nhist][k]->SetBinContent(1+i/Nhist, yieldJunctions / yieldMonash);
	// hYieldsRatio[i/Nhist][k]->SetBinError(1+i/Nhist, 1e-9); // until error propagation is correctly implemented
	hYieldsRatio[i/Nhist][k]->Draw("same PE");
	
      } // END of k for-loop over yields array
    } // if (junctions) for k-loop

    // Draw relative yields for B+B-/B+Lb
    // Has the possibility to be generalised for more associates in the future
    cRelYields->cd();
    if (isInArray(i/Nhist, intAssociate, NAssociates)) { for (Int_t l = 0; l < Nconfigs; l++) {

	if (junctions) { mainPadRelJunctions->cd(); }
	
	// MONASH
	hRelYields[0][l] = new TH1D(Form("hRelYields_MONASH_%s_%i_%i", plotTitle, i, l), Form("hRelYields_%i_%i", i, l), Nconfigs, 0, Nconfigs);
	hRelYields[0][l]->SetBinContent(1+l, vYields[i/Nhist][0][l] / vYields[0][0][l]);
	hRelYields[0][l]->SetBinError(1+l, 1e-9);
	hRelYields[0][l]->SetLineColor(kBlack);
	hRelYields[0][l]->SetLineStyle(RelYieldsLineStyles[counterLineStyle]);
	hRelYields[0][l]->SetLineWidth(RelYieldsLineWidths[counterLineStyle]);
	
	hRelYields[0][l]->Draw("same PE");
	
	// JUNCTIONS
	if (junctions) {
	  hRelYields[1][l] = new TH1D(Form("hRelYields_JUNCTIONS_%s_%i_%i", plotTitle, i, l), Form("hRelYields_%i_%i", i, l), Nconfigs, 0, Nconfigs);
	  hRelYields[1][l]->SetBinContent(1+l, vYields[i/Nhist][1][l] / vYields[0][1][l]);
	  hRelYields[1][l]->SetBinError(1+l, 1e-9);
	  hRelYields[1][l]->SetLineColor(kRed);
	  hRelYields[1][l]->SetLineStyle(RelYieldsLineStyles[counterLineStyle]);
	  hRelYields[1][l]->SetLineWidth(RelYieldsLineWidths[counterLineStyle]);
	
	  hRelYields[1][l]->Draw("same PE");

	  hRelYieldsRatio[l] = new TH1D(Form("hRelYieldsRatio_JUNCTIONS_%s_%i_%i", plotTitle, i, l), Form("hRelYieldsRatio_%i_%i", i, l), Nconfigs, 0, Nconfigs);
	  
	  // Draw the JUNCTIONS / MONASH ratio
	  hRelYieldsRatio[l]->SetBinContent(1+l,
					    (vYields[i/Nhist][1][l] / vYields[0][1][l]) /
					    (vYields[i/Nhist][0][l] / vYields[0][0][l]));
	  // hRelYieldsRatio[l]->SetBinError(1+l, 1e-9);
	  hRelYieldsRatio[l]->SetLineColor(kBlack);
	  hRelYieldsRatio[l]->SetLineStyle(RelYieldsLineStyles[counterLineStyle]);
	  hRelYieldsRatio[l]->SetLineWidth(RelYieldsLineWidths[counterLineStyle]);
	
	  miniPadRelJunctions->cd();
	  hRelYieldsRatio[l]->Draw("same PE");
	}
	
	if (l == 0) {
	TLegendEntry* entryRelYields =
	  lRelYields->AddEntry(hRelYields[0][l],
			       Form("%s%s/%s%s",
				    histEntry.TriggerName, histEntry.AssociateNameOS,
				    vHistAndLabels[0].TriggerName,
				    vHistAndLabels[0].AssociateNameOS), "l");
	}
	
      } // END of l for-loop over yields array

      counterLineStyle++;
      
    } // associate selection criterium (e.g. Lb for B+)
    
    // Draw canvas and legend of configurations
    /*
    cOverview->cd();
    mainPad->cd(); gPad->SetLogy(); lOverview->Draw(); lCorr->Draw();
    miniPad->cd(); gPad->SetLogy(); 
    cOverview->Draw();
    */

    // cOverview->cd(); gPad->SetLogy(); cOverview->Draw(); lOverview->Draw();
    // cCorr->cd(); gPad->SetLogy(); cCorr->Draw(); lCorr->Draw();

    // Define associate label names for yield plots
    hYieldsTemplate->GetXaxis()->SetBinLabel(1+i/Nhist, histEntry.AssociateNameOS);
    hYieldsRatioTemplate->GetXaxis()->SetBinLabel(1+i/Nhist, histEntry.AssociateNameOS);

    // For the charm/beauty division plots,fFind the correct bin label using a TEMP
    if (division && i < vHistAndLabels.size()/2) {
    const char* TEMP = concatString(histEntry.AssociateNameOS, "/");
    const char* dividedAssociateName = concatString(TEMP, vHistAndLabels[i+vHistAndLabels.size()/2].AssociateNameOS);
    hDivYieldsTemplate->GetXaxis()->SetBinLabel(1+i/Nhist, dividedAssociateName);
    }
    
  } // END OF i for-loop over associates

  // Draw relative yields for charm/beauty
  // This can only be done when all associate yields have been calculated (charm and beauty)
  cDivYields->cd();
  if (division) { for (Int_t n = 0; n < vHistAndLabels.size()/2; n+= Nconfigs) {

      for (Int_t m = 0; m < Nconfigs; m++) {
	
	std::cout << vDivYieldsCharm[n/Nhist][0][m] << " / " << vDivYieldsBeauty[n/Nhist][0][m] << std::endl;

	HistAndLabels histEntryDiv = vHistAndLabels[n+m];

	// MONASH
	if (!junctions) {
	  hDivYields[n/Nhist][0][m] = new TH1D(Form("hDivYields_MONASH_%s_%i_%i", plotTitle, n, m), Form("hDivYields_%i", m), (vHistAndLabels.size()/Nconfigs)/2, 0, (vHistAndLabels.size()/Nconfigs)/2);
	  hDivYields[n/Nhist][0][m]->SetBinContent(1+n/Nconfigs, vDivYieldsCharm[n/Nhist][0][m] / vDivYieldsBeauty[n/Nhist][0][m]);
	  hDivYields[n/Nhist][0][m]->SetBinError(1+n/Nconfigs, 1e-9);
	}
	
	if (junctions) {
	  hDivYields[n/Nhist][0][m] = new TH1D(Form("hDivYields_MONASH_%s_%i_%i", plotTitle, n, m), Form("hDivYields_%i", m), (vHistAndLabels.size()/Nconfigs)/4, 0, (vHistAndLabels.size()/Nconfigs)/4);
	  hDivYields[n/Nhist][0][m]->SetBinContent(1+n/(2*Nconfigs), vDivYieldsCharm[n/Nhist][0][m] / vDivYieldsBeauty[n/Nhist][0][m]);
	  hDivYields[n/Nhist][0][m]->SetBinError(1+n/(2*Nconfigs), 1e-9);
	}
	
	hDivYields[n/Nhist][0][m]->SetLineColor(kBlack);
	hDivYields[n/Nhist][0][m]->SetMarkerColor(kBlack);
	hDivYields[n/Nhist][0][m]->SetLineStyle(histEntryDiv.LineStyle);
	hDivYields[n/Nhist][0][m]->SetLineWidth(histEntryDiv.LineWidth);
	
	hDivYields[n/Nhist][0][m]->Draw("same PE");
	
	// JUNCTIONS
	if (junctions) {
	  hDivYields[n/Nhist][1][m] = new TH1D(Form("hDivYields_JUNCTIONS_%s_%i_%i", plotTitle, n, m), Form("hDivYields_%i", m), (vHistAndLabels.size()/Nconfigs)/4, 0, (vHistAndLabels.size()/Nconfigs)/4);
	  hDivYields[n/Nhist][1][m]->SetBinContent(1+n/(2*Nconfigs), vDivYieldsCharm[n/Nhist][1][m] / vDivYieldsBeauty[n/Nhist][1][m]);
	  hDivYields[n/Nhist][1][m]->SetBinError(1+n/(2*Nconfigs), 1e-9);
	  hDivYields[n/Nhist][1][m]->SetLineColor(kRed);
	  hDivYields[n/Nhist][1][m]->SetMarkerColor(kRed);
	  hDivYields[n/Nhist][1][m]->SetLineStyle(histEntryDiv.LineStyle);
	  hDivYields[n/Nhist][1][m]->SetLineWidth(histEntryDiv.LineWidth);
	  
	  hDivYields[n/Nhist][1][m]->Draw("same PE");
	}

	if (n == 0) {
	  lDivYields->AddEntry(hDivYields[n/Nhist][0][m], histEntryDiv.LegendTitle);
	}
	
      } // END of m for-loop over yields array
    } // END of n for-loop over associates
  } // division selection criterium
  
  if (write) { cYields->SaveAs("Plots/BpYields/BpYieldsLL.pdf"); }

  outputTree->Fill();
  // outputTree->Write();
  // cYields->Write();
  // cRelYields->Write();
  // outputFile->Close();

  return outputTree;
  
} // END OF function declaration

std::vector<HistAndLabels> configureInput(std::vector<PathAndLabels>     vPathAndLabels,
					  std::vector<RootFileAndLabels> vRootFileAndLabels,
					  std::vector<HistNameAndLabels> vHistNameAndLabels) {
  // Returns vector: LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateName, OSHist, SSHist, DrawYmin, DrawYmax

  // const char* CombinedLegendTitle;
  std::vector<HistAndLabels> vHistAndLabels;
  // *** HistLegendTitle, Color, LineStyle, LineWidth, Hist ***
  // To be filled in for loops below

  for (int i = 0; i < vRootFileAndLabels.size(); i++) { // associate loop

    RootFileAndLabels rootEntry = vRootFileAndLabels[i];
    
    for (int j = 0; j < vPathAndLabels.size(); j++) { // simulation settings

      PathAndLabels pathEntry = vPathAndLabels[j];
      
      TFile* OStree = new TFile((pathEntry.Path + rootEntry.OSRootFile).c_str());
      TFile* SStree = new TFile((pathEntry.Path + rootEntry.SSRootFile).c_str());

      for (int k = 0; k < vHistNameAndLabels.size(); k++) { // dependencies loop

	HistNameAndLabels histEntry = vHistNameAndLabels[k];

	// *** ------fill vector with histograms -------- ***

	// std::cout << "i, j, k = " << i << ", " << j << ", " << k << std::endl;

	TH1D* hDPhiOS = (TH1D*)OStree->Get(histEntry.HistName);
	TH1D* hDPhiSS = (TH1D*)SStree->Get(histEntry.HistName);
	TH1D* hTrPtOS = (TH1D*)OStree->Get(histEntry.TrPtName);
	TH1D* hTrPtSS = (TH1D*)SStree->Get(histEntry.TrPtName);

	if (strcmp(rootEntry.TriggerName, rootEntry.AssociateNameSS) == 0) { hDPhiSS->Scale(0.5); } // Prevent double-counting

	// Normalise function doesn't seem to work correctly?
	// normalise(hDPhiOS, hTrPtOS, -1.57, 4.71);
	// normalise(hDPhiSS, hTrPtSS, -1.57, 4.71);

	// std::cout << "trigger pT hist name = " << histEntry.TrPtName << std::endl;
	
	hDPhiOS->Scale(1/hTrPtOS->Integral());
	hDPhiSS->Scale(1/hTrPtSS->Integral());
	
	// std::cout << "OS trigger integral" << " for " << histEntry.HistName << " and " << rootEntry.AssociateNameOS << " associate = " << hTrPtOS->Integral() << std::endl;
	// std::cout << "SS trigger integral" << " for " << histEntry.HistName << " and " << rootEntry.AssociateNameSS << " associate = " << hTrPtSS->Integral() << std::endl;
	// std::cout << std::endl;

	// If we do JUNCTIONS vs MONASH comparison, we change the color setting in the input
	// configurations as a flag. Other dependencies can still be plotted with different
	// linestyles or linewidths
	// Lastly, the title needs to indicate whether MONASH or JUNCTIONS is involved
	const char* CombinedLegendTitle = concatString(pathEntry.LegendTitle, histEntry.LegendTitle);
	
	if (pathEntry.Color != -1) {
	  vHistAndLabels.push_back({
	      CombinedLegendTitle, pathEntry.Color, histEntry.LineStyle, histEntry.LineWidth,
	      rootEntry.TriggerName, rootEntry.AssociateNameOS, rootEntry.AssociateNameSS,
	      hDPhiOS, hDPhiSS,
	      rootEntry.DrawYmin, rootEntry.DrawYmax
	  });
	}
	
	else {
	  vHistAndLabels.push_back({
	      histEntry.LegendTitle, histEntry.Color, histEntry.LineStyle, histEntry.LineWidth,
	      rootEntry.TriggerName, rootEntry.AssociateNameOS, rootEntry.AssociateNameSS,
	      hDPhiOS, hDPhiSS,
	      rootEntry.DrawYmin, rootEntry.DrawYmax
	  });
	}
	
      } // k
      
    } // j
    
  } // i

  return vHistAndLabels;
  
} // END OF configureInput()



std::vector<HistAndLabels> configureInputMult(std::vector<PathAndLabels>     vPathAndLabels,
					  std::vector<RootFileAndLabels> vRootFileAndLabels,
					  std::vector<HistNameAndLabels> vHistNameAndLabels) {
  // Returns vector: LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateName, OSHist, SSHist, DrawYmin, DrawYmax

  std::vector<HistAndLabels> vHistAndLabels;
  // *** HistLegendTitle, Color, LineStyle, LineWidth, Hist ***
  // To be filled in for loops below

  for (int i = 0; i < vRootFileAndLabels.size(); i++) { // associate loop

    RootFileAndLabels rootEntry = vRootFileAndLabels[i];
    
    for (int j = 0; j < vPathAndLabels.size(); j++) { // simulation settings

      PathAndLabels pathEntry = vPathAndLabels[j];
      
      TFile* OStree = new TFile((pathEntry.Path + rootEntry.OSRootFile).c_str());
      TFile* SStree = new TFile((pathEntry.Path + rootEntry.SSRootFile).c_str());

      for (int k = 0; k < vHistNameAndLabels.size(); k++) { // dependencies loop

	if (k == 2) { continue; }
	if (k == 4) { continue; }
	if (k == 6) { continue; }

	HistNameAndLabels histEntry = vHistNameAndLabels[k];

	// *** ------fill vector with histograms -------- ***

	TH1D* hDPhiOS = (TH1D*)OStree->Get(histEntry.HistName);
	TH1D* hDPhiSS = (TH1D*)SStree->Get(histEntry.HistName);
	TH1D* hTrPtOS = (TH1D*)OStree->Get(histEntry.TrPtName);
	TH1D* hTrPtSS = (TH1D*)SStree->Get(histEntry.TrPtName);

	// std::cout << "trigger pT hist name = " << histEntry.TrPtName << std::endl;
	// std::cout << "OS trigger integral" << " for " << histEntry.HistName << " and " << rootEntry.AssociateNameOS << " associate = " << hTrPtOS->Integral() << std::endl;
	
	if (strcmp(rootEntry.TriggerName, rootEntry.AssociateNameSS) == 0) { hDPhiSS->Scale(0.5); } // Prevent double-counting
	
	hDPhiOS->Scale(1/hTrPtOS->Integral());
	hDPhiSS->Scale(1/hTrPtSS->Integral());

	// Only makes sense to check the next bin if there is a next bin
	// Histograms need to defined outside if-statement, however
	TH1D* hDPhiOSNext; TH1D* hDPhiSSNext; TH1D* hTrPtOSNext; TH1D* hTrPtSSNext;
	
	if (k+1 < vHistNameAndLabels.size()) {
	  HistNameAndLabels histEntryNext = vHistNameAndLabels[k+1]; // combining multiplicity bins
	
	  hDPhiOSNext = (TH1D*)OStree->Get(histEntryNext.HistName);
	  hDPhiSSNext = (TH1D*)SStree->Get(histEntryNext.HistName);
	  hTrPtOSNext = (TH1D*)OStree->Get(histEntryNext.TrPtName);
	  hTrPtSSNext = (TH1D*)SStree->Get(histEntryNext.TrPtName);

	  if (strcmp(rootEntry.TriggerName, rootEntry.AssociateNameSS) == 0) { hDPhiSSNext->Scale(0.5); } // Prevent double-counting

	  hDPhiOSNext->Scale(1/hTrPtOSNext->Integral());
	  hDPhiSSNext->Scale(1/hTrPtSSNext->Integral());
	
	} // k-next makes sense
	
	// Combine multiplicity bins in order not to overload the reader
	// This selection is kept explicit to allow some flexiblity in combining bins
	// After the event loop one can easily combine the desired histograms
	if (k == 0) {
	  histEntry.LegendTitle = concatString(pathEntry.LegendTitle, histEntry.LegendTitle);
	}
	
	if (k == 1) { // combine 2nd and 3rd bin
	  hDPhiOS->Add(hDPhiOSNext);
	  hDPhiSS->Add(hDPhiSSNext);
	  histEntry.LegendTitle = concatString(pathEntry.LegendTitle, "40-80 % multiplicity bin");
	}

	if (k == 3) { // combine 4th and 5th bin
	  hDPhiOS->Add(hDPhiOSNext);
	  hDPhiSS->Add(hDPhiSSNext);
	  histEntry.LegendTitle = concatString(pathEntry.LegendTitle, "5-40 % multiplicity bin");
	}

	if (k == 5) { // combine 6th and 7th bin
	  hDPhiOS->Add(hDPhiOSNext);
	  hDPhiSS->Add(hDPhiSSNext);
	  histEntry.LegendTitle = concatString(pathEntry.LegendTitle, "top 5% multiplicity bin");
	}

	/*
        if (k == 6) {
	  histEntry.LegendTitle = concatString(pathEntry.LegendTitle, histEntry.LegendTitle);
	}
	*/

	if (pathEntry.Color != -1) {
	  vHistAndLabels.push_back({
	      histEntry.LegendTitle, pathEntry.Color, histEntry.LineStyle, histEntry.LineWidth,
	      rootEntry.TriggerName, rootEntry.AssociateNameOS, rootEntry.AssociateNameSS,
	      hDPhiOS, hDPhiSS,
	      rootEntry.DrawYmin, rootEntry.DrawYmax
	    });
	}

	else {
	  vHistAndLabels.push_back({
	      histEntry.LegendTitle, histEntry.Color, histEntry.LineStyle, histEntry.LineWidth,
	      rootEntry.TriggerName, rootEntry.AssociateNameOS, rootEntry.AssociateNameSS,
	      hDPhiOS, hDPhiSS,
	      rootEntry.DrawYmin, rootEntry.DrawYmax
	  });
	}
	
      } // k
      
    } // j
    
  } // i

  return vHistAndLabels;
  
} // END OF configureInputMult()

std::vector<HistAndLabels> configureInputBeautyAndCharm(
					  std::vector<PathAndLabels>     vPathAndLabels,
					  std::vector<RootFileAndLabels> vRootFileAndLabels,
					  std::vector<HistNameAndLabels> vHistNameAndLabels) {
  // Returns vector: LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateName, OSHist, SSHist, DrawYmin, DrawYmax
  
  // const char* CombinedLegendTitle;
  std::vector<HistAndLabels> vHistAndLabels;
  // *** HistLegendTitle, Color, LineStyle, LineWidth, Hist ***
  // To be filled in for loops below

  for (int i = 0; i < vRootFileAndLabels.size(); i++) { // associate loop

    RootFileAndLabels rootEntry = vRootFileAndLabels[i];

    // Avoid that charm associates are matched with beauty trees
    // The input structure MUST be:
    // vPaths = {charm_monash, charm_junctions, beauty_monash, beauty_junctions}
    Int_t path_start = 0;
    Int_t path_end = vPathAndLabels.size()/2;
    
    if (i >= vRootFileAndLabels.size()/2) {
      path_start = vPathAndLabels.size()/2;
      path_end = vPathAndLabels.size();
    }
    
    for (Int_t j = path_start; j < path_end; j++) { // simulation settings

      PathAndLabels pathEntry = vPathAndLabels[j];

      TFile* OStree = new TFile((pathEntry.Path + rootEntry.OSRootFile).c_str());
      TFile* SStree = new TFile((pathEntry.Path + rootEntry.SSRootFile).c_str());

      for (int k = 0; k < vHistNameAndLabels.size(); k++) { // dependencies loop

	HistNameAndLabels histEntry = vHistNameAndLabels[k];

	// *** ------fill vector with histograms -------- ***

	// std::cout << "i, j, k = " << i << ", " << j << ", " << k << std::endl;

	TH1D* hDPhiOS = (TH1D*)OStree->Get(histEntry.HistName);
	TH1D* hDPhiSS = (TH1D*)SStree->Get(histEntry.HistName);
	TH1D* hTrPtOS = (TH1D*)OStree->Get(histEntry.TrPtName);
	TH1D* hTrPtSS = (TH1D*)SStree->Get(histEntry.TrPtName);

	if (strcmp(rootEntry.TriggerName, rootEntry.AssociateNameSS) == 0) { hDPhiSS->Scale(0.5); } // Prevent double-counting

	// Normalise function doesn't seem to work correctly?
	// normalise(hDPhiOS, hTrPtOS, -1.57, 4.71);
	// normalise(hDPhiSS, hTrPtSS, -1.57, 4.71);

	// std::cout << "trigger pT hist name = " << histEntry.TrPtName << std::endl;
	
	hDPhiOS->Scale(1/hTrPtOS->Integral());
	hDPhiSS->Scale(1/hTrPtSS->Integral());
	
	// std::cout << "OS trigger integral" << " for " << histEntry.HistName << " and " << rootEntry.AssociateNameOS << " associate = " << hTrPtOS->Integral() << std::endl;
	// std::cout << "SS trigger integral" << " for " << histEntry.HistName << " and " << rootEntry.AssociateNameSS << " associate = " << hTrPtSS->Integral() << std::endl;
	// std::cout << std::endl;

	// If we do JUNCTIONS vs MONASH comparison, we change the color setting in the input
	// configurations as a flag. Other dependencies can still be plotted with different
	// linestyles or linewidths
	// Lastly, the title needs to indicate whether MONASH or JUNCTIONS is involved
	const char* CombinedLegendTitle = concatString(pathEntry.LegendTitle, histEntry.LegendTitle);
	
	if (pathEntry.Color != -1) {
	  vHistAndLabels.push_back({
	      CombinedLegendTitle, pathEntry.Color, histEntry.LineStyle, histEntry.LineWidth,
	      rootEntry.TriggerName, rootEntry.AssociateNameOS, rootEntry.AssociateNameSS,
	      hDPhiOS, hDPhiSS,
	      rootEntry.DrawYmin, rootEntry.DrawYmax
	  });
	}
	
	else {
	  vHistAndLabels.push_back({
	      histEntry.LegendTitle, histEntry.Color, histEntry.LineStyle, histEntry.LineWidth,
	      rootEntry.TriggerName, rootEntry.AssociateNameOS, rootEntry.AssociateNameSS,
	      hDPhiOS, hDPhiSS,
	      rootEntry.DrawYmin, rootEntry.DrawYmax
	  });
	}
	
      } // k
      
    } // j
    
  } // i

  return vHistAndLabels;
  
} // END OF configureInputBeautyAndCharm()


// root -l (-b -q) "B_Balancing_MakeOutputYields.C(1, \"/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_JUNCTIONS_214/\", \"/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_214/\")"
int B_Balancing_MakeOutputYields(Int_t Nbatch, const char* path_bb_214, const char* path_bb_JUNCTIONS_214, const char* path_cc_214, const char* path_cc_JUNCTIONS_214, const char* path_cc_prompt_214, const char* path_cc_prompt_JUNCTIONS_214, const char* path_cc_non_prompt_214, const char* path_cc_non_prompt_JUNCTIONS_214) {

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

  // Output file for trees for different configurations and settings
  TFile* outputFile = new TFile(Form("yieldOutput_%i.root", Nbatch), "RECREATE");
  
  // Define inputs for configureInput()
  // That function then prepares the input for the main function call, harryPlotter, which plots everything
  Bool_t junctions = false; // MONASH vs JUNCTIONS comparison ON
  Bool_t division = false;  // D / B comparison ON
  Bool_t write = false;     // Write to local (as pdf) ON

  // Select which part of the code to run
  // Details can be changed as desired below
  Bool_t bb_JUNCTIONS_MULTIPLICITY_GENERAL = true;
  Bool_t bb_JUNCTIONS_MULTIPLICITY_CONDENSED = true;
  
  Bool_t cc_JUNCTIONS_MULTIPLICITY_GENERAL = true;
  Bool_t cc_JUNCTIONS_MULTIPLICITY_CONDENSED = true;
  
  Bool_t cc_PROMPT_JUNCTIONS_MULTIPLICITY_GENERAL = true;
  Bool_t cc_PROMPT_JUNCTIONS_MULTIPLICITY_CONDENSED = true;

  Bool_t cc_NON_PROMPT_JUNCTIONS_MULTIPLICITY_GENERAL = true;
  Bool_t cc_NON_PROMPT_JUNCTIONS_MULTIPLICITY_CONDENSED = true;

  // const char* path_bb_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_214/";
  
  std::vector<PathAndLabels> vPathAndLabels;
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({"MONASH", -1, -1, -1, path_bb_214});

  std::vector<RootFileAndLabels> vRootFileAndLabels;
  // *** LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateNameOS, AssociateNameSS, OSRootFile, SSRootFile, DrawYmin, DrawYmax ***
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "B^{-}", "B^{+}", "BplusBminus.root", "BplusBplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "B_{c}^{-}", "B_{c}^{+}", "BplusBcminus.root", "BplusBcplus.root", 1e-8, 1e-2});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#barB^{0}", "B^{0}", "BplusBzerobar.root", "BplusBzero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#barB_{s}^{0}", "B_{s}^{0}", "BplusBszerobar.root", "BplusBszero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Lambda_{b}^{0}", "#bar#Lambda_{b}^{0}", "BplusLb.root", "BplusLbbar.root", 1e-8, 1e-2});
  
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{+}", "#bar#Sigma_{b}^{+}", "BplusSigmabplus.root", "BplusSigmabplusbar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{0}", "#bar#Sigma_{b}^{0}", "BplusSigmabzero.root", "BplusSigmabzerobar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{-}", "#bar#Sigma_{b}^{-}", "BplusSigmabminus.root", "BplusSigmabminusbar.root", 1e-8, 1e-2});
    

  std::vector<HistNameAndLabels> vHistNameAndLabels;
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"low-low", kBlack, 1, 1, "hDPhiLL", "hTrPtL"});
  vHistNameAndLabels.push_back({"int-int", kBlue, 2, 2, "hDPhiII", "hTrPtI"});
  vHistNameAndLabels.push_back({"high-high", kRed, 3, 3, "hDPhiHH", "hTrPtH"});
  
  // Trigger pT study: low-low, int-int, high-high
  std::vector<HistAndLabels> vInput;
  
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of pT", vHistNameAndLabels.size(), junctions, division, write);
  
  // Multiplicity study: centrality classes
  vHistNameAndLabels.clear();
  vInput.clear();

  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"80-100 % multiplicity bin", kBlue, 2, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 % multiplicity bin", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 % multiplicity bin", kBlack, 3, 2, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 % multiplicity bin", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 % multiplicity bin", kBlack, 1, 1, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5% multiplicity bin", kRed, 2, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"top 1% multiplicity bin", kRed, 1, 1, "hDPhiM1", "hTrPtM1"});

  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of multiplicity", vHistNameAndLabels.size(), division, write);

  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();

  // vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of multiplicity", 4, junctions, division, write);
  
  // Rapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiYCC", "hTrPtYC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiYCF", "hTrPtYC"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiYFC", "hTrPtYF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiYFF", "hTrPtYF"});

  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of rapidity", vHistNameAndLabels.size(), junctions, division, write);

  // Pseudorapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiEtaCC", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiEtaCF", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiEtaFC", "hTrPtEtaF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiEtaFF", "hTrPtEtaF"});
  
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of pseudorapidity", vHistNameAndLabels.size(), junctions, division, write);

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

  // Now plot JUNCTIONS results and compare with MONASH
  vPathAndLabels.clear();
  vHistNameAndLabels.clear();
  vInput.clear();

  // const char* path_bb_JUNCTIONS_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_JUNCTIONS_214/";
  junctions = true;
  
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({" ", kBlack, -1, -1, path_bb_214});
  vPathAndLabels.push_back({" ", kRed, -1, -1, path_bb_JUNCTIONS_214});

  vHistNameAndLabels.push_back({"all bins", kBlack, 1, 1, "hDPhi", "hTrPt"});

  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger", vPathAndLabels.size()*vHistNameAndLabels.size(), junctions, division, write);

  // JUNCTIONS pT study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"low-low", kBlack, 1, 1, "hDPhiLL", "hTrPtL"});
  vHistNameAndLabels.push_back({"int-int", kBlue, 2, 2, "hDPhiII", "hTrPtI"});
  vHistNameAndLabels.push_back({"high-high", kRed, 3, 3, "hDPhiHH", "hTrPtH"});

  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of pT", vPathAndLabels.size()*vHistNameAndLabels.size(), junctions, division, write);

  // JUNCTIONS multiplicity study: centrality classes
  vHistNameAndLabels.clear();
  vInput.clear();

  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"80-100 % multiplicity bin", kBlue, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 % multiplicity bin", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 % multiplicity bin", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 % multiplicity bin", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 % multiplicity bin", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5% multiplicity bin", kRed, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"top 1% multiplicity bin", kRed, 4, 3, "hDPhiM1", "hTrPtM1"});

  if (bb_JUNCTIONS_MULTIPLICITY_GENERAL) {
  vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  TTree* bb_J_MULT_GENERAL_tree = CalculateOS_minus_SS(Nbatch, "BBMULTGENERAL", vInput, "integrated yields for B^{+} trigger as function of multiplicity", vPathAndLabels.size()*vHistNameAndLabels.size(), junctions, division, write);
  outputFile->cd();
  bb_J_MULT_GENERAL_tree->Write();
  }
  
  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();

  if (bb_JUNCTIONS_MULTIPLICITY_CONDENSED) {
  vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  TTree* bb_J_MULT_CONDENSED_tree = CalculateOS_minus_SS(Nbatch, "BBMULTCONDENSED", vInput, "integrated yields for B^{+} trigger as function of multiplicity condensed", 4*vPathAndLabels.size(), junctions, division, write);
  outputFile->cd();
  bb_J_MULT_CONDENSED_tree->Write();
  }
  
  // JUNCTIONS Rapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiYCC", "hTrPtYC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiYCF", "hTrPtYC"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiYFC", "hTrPtYF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiYFF", "hTrPtYF"});

  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of rapidity", vPathAndLabels.size()*vHistNameAndLabels.size(), junctions, division, write);

  // JUNCTIONS Pseudorapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiEtaCC", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiEtaCF", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiEtaFC", "hTrPtEtaF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiEtaFF", "hTrPtEtaF"});
  
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of pseudorapidity", vPathAndLabels.size()*vHistNameAndLabels.size(), junctions, division, write);

  // -------------------------------------------------------------- //
  
  // JUNCTIONS
  // TRIGGER = Lb
  vRootFileAndLabels.clear();
  vHistNameAndLabels.clear();
  vInput.clear();
  
  // *** LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateNameOS, AssociateNameSS, OSRootFile, SSRootFile, DrawYmin, DrawYmax ***
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "#bar#Lambda_{b}^{0}", "B^{-}", "B^{+}", "LbbarBminus.root", "LbbarBplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "#bar#Lambda_{b}^{0}", "B_{c}^{-}", "B_{c}^{+}", "LbbarBcminus.root", "LbbarBcplus.root", 1e-8, 1e-2});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "#bar#Lambda_{b}^{0}", "#barB^{0}", "B^{0}", "LbbarBzerobar.root", "LbbarBzero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "#bar#Lambda_{b}^{0}", "#barB_{s}^{0}", "B_{s}^{0}", "LbbarBszerobar.root", "LbbarBszero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "#bar#Lambda_{b}^{0}", "#Lambda_{b}^{0}", "#bar#Lambda_{b}^{0}", "LbbarLb.root", "LbbarLbbar.root", 1e-8, 1e-2});

  vHistNameAndLabels.push_back({"(all bins)", kBlack, 1, 1, "hDPhi", "hTrPt"});

  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for #bar#Lambda_{b}^{0} trigger", vPathAndLabels.size()*vHistNameAndLabels.size(), junctions, division, write);

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

  // CHARM JUNCTIONS STUDY

  vPathAndLabels.clear();
  vRootFileAndLabels.clear();
  vHistNameAndLabels.clear();
  vInput.clear();

  junctions = true;
  // const char* path_cc_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_214/";
  // const char* path_cc_JUNCTIONS_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_JUNCTIONS_214/";
  
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({" ", kBlack, -1, -1, path_cc_214});
  vPathAndLabels.push_back({" ", kRed, -1, -1, path_cc_JUNCTIONS_214});

  // *** LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateNameOS, AssociateNameSS, OSRootFile, SSRootFile, DrawYmin, DrawYmax ***
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "D^{-}", "D^{+}", "DplusDminus.root", "DplusDplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "D_{s}^{-}", "D_{s}^{+}", "DplusDsminus.root", "DplusDsplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#barD^{0}", "D^{0}", "DplusDzerobar.root", "DplusDzero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Lambda_{c}^{+}", "#Lambda_{c}^{+}", "DplusLambdacplusbar.root", "DplusLambdacplus.root", 1e-8, 1e-2});
  
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{++}", "#Sigma_{c}^{++}", "DplusSigmacplusplusbar.root", "DplusSigmacplusplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{+}", "#Sigma_{c}^{+}", "DplusSigmacplusbar.root", "DplusSigmacplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{0}", "#Sigma_{c}^{0}", "DplusSigmaczerobar.root", "DplusSigmaczero.root", 1e-8, 1e-2});
  

  // Trigger pT study: low-low, int-int, high-high
  
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"low-low", kBlack, 1, 1, "hDPhiLL", "hTrPtL"});
  vHistNameAndLabels.push_back({"int-int", kBlue, 2, 2, "hDPhiII", "hTrPtI"});
  vHistNameAndLabels.push_back({"high-high", kRed, 3, 3, "hDPhiHH", "hTrPtH"});
  
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for D^{+} trigger as function of pT", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);
  
  // Multiplicity study: centrality classes
  vHistNameAndLabels.clear();
  vInput.clear();

  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"80-100 % multiplicity bin", kBlue, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 % multiplicity bin", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 % multiplicity bin", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 % multiplicity bin", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 % multiplicity bin", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5% multiplicity bin", kRed, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"top 1% multiplicity bin", kRed, 4, 3, "hDPhiM1", "hTrPtM1"});

  if (cc_JUNCTIONS_MULTIPLICITY_GENERAL) {
    vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
    TTree* cc_J_MULT_GENERAL_tree = CalculateOS_minus_SS(Nbatch, "CCMULTGENERAL", vInput, "integrated yields for D^{+} trigger as function of multiplicity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);
    outputFile->cd();
    cc_J_MULT_GENERAL_tree->Write();
  }
  
  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();

  if (cc_JUNCTIONS_MULTIPLICITY_CONDENSED) {
    vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
    TTree* cc_J_MULT_CONDENSED_tree = CalculateOS_minus_SS(Nbatch, "CCMULTCONDENSED", vInput, "integrated yields for D^{+} trigger as function of multiplicity", 4*vPathAndLabels.size(), junctions, write);
    outputFile->cd();
    cc_J_MULT_CONDENSED_tree->Write();
  }
  
  // Rapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiYCC", "hTrPtYC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiYCF", "hTrPtYC"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiYFC", "hTrPtYF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiYFF", "hTrPtYF"});

  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for D^{+} trigger as function of rapidity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);

  // Pseudorapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiEtaCC", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiEtaCF", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiEtaFC", "hTrPtEtaF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiEtaFF", "hTrPtEtaF"});
  
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for D^{+} trigger as function of pseudorapidity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);

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

  // PROMPT CHARM JUNCTIONS STUDY

  vPathAndLabels.clear();
  vRootFileAndLabels.clear();
  vHistNameAndLabels.clear();
  vInput.clear();

  junctions = true;
  
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({" ", kBlack, -1, -1, path_cc_prompt_214});
  vPathAndLabels.push_back({" ", kRed, -1, -1, path_cc_prompt_JUNCTIONS_214});

  // *** LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateNameOS, AssociateNameSS, OSRootFile, SSRootFile, DrawYmin, DrawYmax ***
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "D^{-}", "D^{+}", "DplusDminus.root", "DplusDplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "D_{s}^{-}", "D_{s}^{+}", "DplusDsminus.root", "DplusDsplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#barD^{0}", "D^{0}", "DplusDzerobar.root", "DplusDzero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Lambda_{c}^{+}", "#Lambda_{c}^{+}", "DplusLambdacplusbar.root", "DplusLambdacplus.root", 1e-8, 1e-2});
  
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{++}", "#Sigma_{c}^{++}", "DplusSigmacplusplusbar.root", "DplusSigmacplusplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{+}", "#Sigma_{c}^{+}", "DplusSigmacplusbar.root", "DplusSigmacplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{0}", "#Sigma_{c}^{0}", "DplusSigmaczerobar.root", "DplusSigmaczero.root", 1e-8, 1e-2});
  

  // Trigger pT study: low-low, int-int, high-high
  
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"low-low", kBlack, 1, 1, "hDPhiLL", "hTrPtL"});
  vHistNameAndLabels.push_back({"int-int", kBlue, 2, 2, "hDPhiII", "hTrPtI"});
  vHistNameAndLabels.push_back({"high-high", kRed, 3, 3, "hDPhiHH", "hTrPtH"});
  
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for prompt D^{+} trigger as function of pT", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);
  
  // Multiplicity study: centrality classes
  vHistNameAndLabels.clear();
  vInput.clear();

  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"80-100 % multiplicity bin", kBlue, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 % multiplicity bin", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 % multiplicity bin", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 % multiplicity bin", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 % multiplicity bin", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5% multiplicity bin", kRed, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"top 1% multiplicity bin", kRed, 4, 3, "hDPhiM1", "hTrPtM1"});
  
  if (cc_PROMPT_JUNCTIONS_MULTIPLICITY_GENERAL) {
  vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  TTree* cc_prompt_J_MULT_GENERAL_tree = CalculateOS_minus_SS(Nbatch, "CCPROMPTMULTGENERAL", vInput, "integrated yields for prompt D^{+} trigger as function of multiplicity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);
  outputFile->cd();
  cc_prompt_J_MULT_GENERAL_tree->Write();
  }
  
  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();

  if (cc_PROMPT_JUNCTIONS_MULTIPLICITY_CONDENSED) {
  vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  TTree* cc_prompt_J_MULT_CONDENSED_tree = CalculateOS_minus_SS(Nbatch, "CCPROMPTMULTCONDENSED", vInput, "integrated yields for prompt D^{+} trigger as function of multiplicity", 4*vPathAndLabels.size(), junctions, division, write);
  outputFile->cd();
  cc_prompt_J_MULT_CONDENSED_tree->Write();
  }
  
  // Rapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiYCC", "hTrPtYC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiYCF", "hTrPtYC"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiYFC", "hTrPtYF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiYFF", "hTrPtYF"});

  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for prompt D^{+} trigger as function of rapidity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);

  // Pseudorapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiEtaCC", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiEtaCF", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiEtaFC", "hTrPtEtaF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiEtaFF", "hTrPtEtaF"});
  
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for prompt D^{+} trigger as function of pseudorapidity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);

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

  // NON-PROMPT CHARM JUNCTIONS STUDY

  vPathAndLabels.clear();
  vRootFileAndLabels.clear();
  vHistNameAndLabels.clear();
  vInput.clear();

  junctions = true;
  
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({" ", kBlack, -1, -1, path_cc_non_prompt_214});
  vPathAndLabels.push_back({" ", kRed, -1, -1, path_cc_non_prompt_JUNCTIONS_214});

  // *** LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateNameOS, AssociateNameSS, OSRootFile, SSRootFile, DrawYmin, DrawYmax ***
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "D^{-}", "D^{+}", "DplusDminus.root", "DplusDplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "D_{s}^{-}", "D_{s}^{+}", "DplusDsminus.root", "DplusDsplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#barD^{0}", "D^{0}", "DplusDzerobar.root", "DplusDzero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Lambda_{c}^{+}", "#Lambda_{c}^{+}", "DplusLambdacplusbar.root", "DplusLambdacplus.root", 1e-8, 1e-2});
  
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{++}", "#Sigma_{c}^{++}", "DplusSigmacplusplusbar.root", "DplusSigmacplusplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{+}", "#Sigma_{c}^{+}", "DplusSigmacplusbar.root", "DplusSigmacplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Sigma_{c}^{0}", "#Sigma_{c}^{0}", "DplusSigmaczerobar.root", "DplusSigmaczero.root", 1e-8, 1e-2});
  

  // Trigger pT study: low-low, int-int, high-high
  
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"low-low", kBlack, 1, 1, "hDPhiLL", "hTrPtL"});
  vHistNameAndLabels.push_back({"int-int", kBlue, 2, 2, "hDPhiII", "hTrPtI"});
  vHistNameAndLabels.push_back({"high-high", kRed, 3, 3, "hDPhiHH", "hTrPtH"});
  
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for prompt D^{+} trigger as function of pT", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);
  
  // Multiplicity study: centrality classes
  vHistNameAndLabels.clear();
  vInput.clear();

  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"80-100 % multiplicity bin", kBlue, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 % multiplicity bin", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 % multiplicity bin", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 % multiplicity bin", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 % multiplicity bin", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5% multiplicity bin", kRed, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"top 1% multiplicity bin", kRed, 4, 3, "hDPhiM1", "hTrPtM1"});
  
  if (cc_NON_PROMPT_JUNCTIONS_MULTIPLICITY_GENERAL) {
  vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  TTree* cc_non_prompt_J_MULT_GENERAL_tree = CalculateOS_minus_SS(Nbatch, "CCNONPROMPTMULTGENERAL", vInput, "integrated yields for prompt D^{+} trigger as function of multiplicity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);
  outputFile->cd();
  cc_non_prompt_J_MULT_GENERAL_tree->Write();
  }
  
  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();

  if (cc_NON_PROMPT_JUNCTIONS_MULTIPLICITY_CONDENSED) {
  vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  TTree* cc_non_prompt_J_MULT_CONDENSED_tree = CalculateOS_minus_SS(Nbatch, "CCNONPROMPTMULTCONDENSED", vInput, "integrated yields for prompt D^{+} trigger as function of multiplicity", 4*vPathAndLabels.size(), junctions, division, write);
  outputFile->cd();
  cc_non_prompt_J_MULT_CONDENSED_tree->Write();
  }
  
  // Rapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiYCC", "hTrPtYC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiYCF", "hTrPtYC"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiYFC", "hTrPtYF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiYFF", "hTrPtYF"});

  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for prompt D^{+} trigger as function of rapidity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);

  // Pseudorapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiEtaCC", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiEtaCF", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiEtaFC", "hTrPtEtaF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiEtaFF", "hTrPtEtaF"});
  
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for prompt D^{+} trigger as function of pseudorapidity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);

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
  
  // CHARM DIVIDED BY BEAUTY STUDY
  // NOTE: division requires a new function bool to work, as the yields need to be divided at
  // the end of the OS - SS algorithm. Cannot be done by changing the input configuration alone.

  vPathAndLabels.clear();
  vRootFileAndLabels.clear();
  vHistNameAndLabels.clear();
  vInput.clear();

  junctions = true;
  division = true;
  
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({" ", kBlack, -1, -1, path_cc_214});
  vPathAndLabels.push_back({" ", kRed, -1, -1, path_cc_JUNCTIONS_214});
  vPathAndLabels.push_back({" ", kBlack, -1, -1, path_bb_214});
  vPathAndLabels.push_back({" ", kRed, -1, -1, path_bb_JUNCTIONS_214});

  // *** LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateNameOS, AssociateNameSS, OSRootFile, SSRootFile, DrawYmin, DrawYmax ***
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "D^{-}", "D^{+}", "DplusDminus.root", "DplusDplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#barD^{0}", "D^{0}", "DplusDzerobar.root", "DplusDzero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "D_{s}^{-}", "D_{s}^{+}", "DplusDsminus.root", "DplusDsplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#bar#Lambda_{c}^{+}", "#Lambda_{c}^{+}", "DplusLambdacplusbar.root", "DplusLambdacplus.root", 1e-8, 1e-2});
  /*
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#Sigma_{b}^{+}", "#bar#Sigma_{b}^{+}", "BplusSigmabplus.root", "BplusSigmabplusbar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#Sigma_{b}^{0}", "#bar#Sigma_{b}^{0}", "BplusSigmabzero.root", "BplusSigmabzerobar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#Sigma_{b}^{-}", "#bar#Sigma_{b}^{-}", "BplusSigmabminus.root", "BplusSigmabminusbar.root", 1e-8, 1e-2});
  */

  // *** LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateNameOS, AssociateNameSS, OSRootFile, SSRootFile, DrawYmin, DrawYmax ***
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "B^{-}", "B^{+}", "BplusBminus.root", "BplusBplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#barB^{0}", "B^{0}", "BplusBzerobar.root", "BplusBzero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#barB_{s}^{0}", "B_{s}^{0}", "BplusBszerobar.root", "BplusBszero.root", 1e-8, 1e-2});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Lambda_{b}^{0}", "#bar#Lambda_{b}^{0}", "BplusLb.root", "BplusLbbar.root", 1e-8, 1e-2});
  /*
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{+}", "#bar#Sigma_{b}^{+}", "BplusSigmabplus.root", "BplusSigmabplusbar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{0}", "#bar#Sigma_{b}^{0}", "BplusSigmabzero.root", "BplusSigmabzerobar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{-}", "#bar#Sigma_{b}^{-}", "BplusSigmabminus.root", "BplusSigmabminusbar.root", 1e-8, 1e-2});
  */
  
  // Trigger pT study: low-low, int-int, high-high
  
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"low-low", kBlack, 1, 1, "hDPhiLL", "hTrPtL"});
  vHistNameAndLabels.push_back({"int-int", kBlue, 2, 2, "hDPhiII", "hTrPtI"});
  vHistNameAndLabels.push_back({"high-high", kRed, 3, 3, "hDPhiHH", "hTrPtH"});
  
  // vInput = configureInputBeautyAndCharm(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for D^{+} / B^{+} trigger as function of pT", vHistNameAndLabels.size()*vPathAndLabels.size()/2, junctions, division, write);
  
  // Multiplicity study: centrality classes
  vHistNameAndLabels.clear();
  vInput.clear();

  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"80-100 % multiplicity bin", kBlue, 2, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 % multiplicity bin", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 % multiplicity bin", kBlack, 3, 2, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 % multiplicity bin", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 % multiplicity bin", kBlack, 1, 1, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5% multiplicity bin", kRed, 2, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"top 1% multiplicity bin", kRed, 1, 1, "hDPhiM1", "hTrPtM1"});

  // vInput = configureInputBeautyAndCharm(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for D^{+} / B^{+} trigger as function of multiplicity", vHistNameAndLabels.size()*vPathAndLabels.size()/2, junctions, division, write);

  // Rapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiYCC", "hTrPtYC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiYCF", "hTrPtYC"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiYFC", "hTrPtYF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiYFF", "hTrPtYF"});

  // vInput = configureInputBeautyAndCharm(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for D^{+} / B^{+} trigger as function of rapidity", vHistNameAndLabels.size()*vPathAndLabels.size()/2, junctions, division, write);

  // Pseudorapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiEtaCC", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiEtaCF", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiEtaFC", "hTrPtEtaF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiEtaFF", "hTrPtEtaF"});
  
  // vInput = configureInputBeautyAndCharm(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for D^{+} / B^{+} trigger as function of pseudorapidity", vHistNameAndLabels.size()*vPathAndLabels.size()/2, junctions, division, write);
  
  return 0;
  
}
