// B_Balancing_GeneralPlotting.C
// Main plotting script for different balancing plots using OS - SS yields

// TODO: cut irrelevant parts from code

void normalise(TH1D* hist, TH1D* trig, Double_t xmin, Double_t xmax) {
	Int_t bin_start = trig->FindBin(xmin);
	Int_t bin_finish = trig->FindBin(xmax);
	Double_t integral = trig->Integral(bin_start, bin_finish);
	std::cout << "function integral = " << integral << std::endl;
	hist->Scale(1./integral);
}

bool isInArray(int num, std::vector<int>arr, int size) {
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

// In order to save the outputs as a PDF in an automised way,
// it is required to create a settings struct
// Could also use vectors, but at the cost of clarity.
struct DrawOptions {
  // Name which is used for writing the plots to the local directory
  const char* WriteName;
  const char* labelID;
  
  TPad* yieldPad;
  TPad* yieldMiniPad;
  TPad* relYieldPad;
  TPad* relYieldMiniPad;

  std::vector<Int_t> vAssociates;
  
  Double_t RelYieldsYmin;
  Double_t RelYieldsYmax;
  Double_t RelYieldsMin;

  Double_t RelYieldsRatioYmin;
  Double_t RelYieldsRatioYmax;
  Double_t RelYieldsRatioMax;

  Double_t LegendRelYieldsXmin;
  Double_t LegendRelYieldsYmin;
  Double_t LegendRelYieldsXmax;
  Double_t LegendRelYieldsYmax;

  Color_t LineColor;

  // Set log scale to gPad?
  Bool_t MainPadOptLog;
  Bool_t MiniPadOptLog;

  // Control whether MONASH, JUNCTIONS or both are used for the errors
  // 0 indicates MONASH
  // 1 indicates JUNCTIONS
  // -1 indicates that we don't use this option, i.e. both MONASH and JUNCTIONS errors are taken
  Int_t OptError;
};

// Input vector should countain per trigger yield histograms!
void CalculateOS_minus_SS(std::vector<HistAndLabels> vHistAndLabels,
			  const char* plotTitle, Int_t Nhist,
			  Bool_t junctions = false, Bool_t division = false,
			  Bool_t write = false,
			  const char* errFileName = nullptr, const char* errTreeName = nullptr,
			  DrawOptions drawOptions = {}) {

  TPad* yieldPad = drawOptions.yieldPad;
  if (yieldPad != nullptr) {
    std::cout << std::endl;
    std::cout << yieldPad->GetName() << std::endl;
    std::cout << std::endl;
  }

  TPad* yieldMiniPad = drawOptions.yieldMiniPad;
  if (yieldMiniPad != nullptr) {
    std::cout << std::endl;
    std::cout << yieldMiniPad->GetName() << std::endl;
    std::cout << std::endl;
  }

  TPad* relYieldPad = drawOptions.relYieldPad;
  if (relYieldPad != nullptr) {
    std::cout << std::endl;
    std::cout << relYieldPad->GetName() << std::endl;
    std::cout << std::endl;
  }

  TPad* relYieldMiniPad = drawOptions.relYieldMiniPad;
  if (relYieldMiniPad != nullptr) {
    std::cout << std::endl;
    std::cout << relYieldMiniPad->GetName() << std::endl;
    std::cout << std::endl;
  }

  std::cout << "test" << std::endl;
  
  // Integer of the associate of interest for the relative yields
  Int_t NAssociates = drawOptions.vAssociates.size();
  // Int_t intAssociate[2] = {3, 5}; // for beauty: 4, 6 (Lb0, Sb0), for charm: 3, 5 (Lc+, Sc+)
  std::vector<Int_t> intAssociate = drawOptions.vAssociates;
  Int_t counterLineStyle = 0; // Used to iterate over intAssociate

  // The line styles and widths are also hard-coded
  Int_t RelYieldsLineStyles[2] = {1, 2}; // {1, 2}
  Int_t RelYieldsLineWidths[2] = {1, 2}; // {1, 2}

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

  // When MONASH and JUNCTIONS are involved, the number of histograms is doubled compared to the
  // actual number of configurations
  Int_t Nconfigs;
  if (!junctions) { Nconfigs = Nhist; }
  if (junctions) { Nconfigs = Nhist/2; }

  std::cout << "Nconfigs = " << Nconfigs << std::endl;
  std::cout << std::endl;

  TH1D* hYieldsRatioTemplate = new TH1D(Form("hYieldsRatioTemplate_%s", plotTitle), "hYieldsRatioTemplate", vHistAndLabels.size()/Nhist, 0, vHistAndLabels.size()/Nhist);
  
  TH1D* hRelYieldsTemplate = new TH1D(Form("hRelYieldsTemplate_%s", plotTitle), "hRelYieldsTemplate", Nconfigs, 0, Nconfigs);

  TH1D* hRelYieldsRatioTemplate = new TH1D(Form("hRelYieldsRatioTemplate_%s", plotTitle), "hRelYieldsRatioTemplate", Nconfigs, 0, Nconfigs);

  TH1D* hDivYieldsTemplate;

  // Figure this out when I start working with the charm/beauty divided yields again
  if (!junctions) { hDivYieldsTemplate = new TH1D(Form("hDivYieldsTemplate_%s", plotTitle), "hDivYieldsTemplate", (vHistAndLabels.size()/Nconfigs)/2, 0, (vHistAndLabels.size()/Nconfigs)/2); }
  if (junctions) { hDivYieldsTemplate = new TH1D(Form("hDivYieldsTemplate_%s", plotTitle), "hDivYieldsTemplate", (vHistAndLabels.size()/Nconfigs)/4, 0, (vHistAndLabels.size()/Nconfigs)/4); }

  // Function pad
  cYields->cd();
  hYieldsTemplate->SetTitle(plotTitle);
  hYieldsTemplate->GetYaxis()->SetTitle("Integrated yield");
  if (!junctions) { hYieldsTemplate->GetXaxis()->SetTitle("Associate"); }
  hYieldsTemplate->GetXaxis()->SetLabelSize(0.05);
  hYieldsTemplate->SetStats(0);
  hYieldsTemplate->GetYaxis()->SetRangeUser(1e-4, 4e1); // 1e-4, 1e0
  if (!junctions) { hYieldsTemplate->Draw("PE"); }

  // Global pad
  if (yieldPad != nullptr) {
    yieldPad->cd();
    hYieldsTemplate->SetTitle("");
    hYieldsTemplate->GetYaxis()->SetTitleSize(0.06);
    hYieldsTemplate->GetYaxis()->SetLabelSize(0.05);
    if (strcmp(yieldPad->GetName(), "c00_yields") == 0) { hYieldsTemplate->GetYaxis()->SetTitle("Integrated yield"); }
    else { hYieldsTemplate->GetYaxis()->SetTitle(""); }
    hYieldsTemplate->GetXaxis()->SetTitle("");
    // if (strcmp(yieldPad->GetName(), "c11_yields") == 0) { hYieldsTemplate->GetXaxis()->SetTitle("Associate"); }
    // else { hYieldsTemplate->GetXaxis()->SetTitle(""); }
    // hYieldsTemplate->GetXaxis()->SetLabelSize(0.05);
    hYieldsTemplate->SetStats(0);
    hYieldsTemplate->GetYaxis()->SetRangeUser(1e-4, 4e1); // 1e-4, 1e0
    hYieldsTemplate->SetMinimum(6e-5); // 6e-5

    // if (strcmp(yieldPad->GetName(), "c11_yields") == 0) { hYieldsTemplate->GetXaxis()->SetTitleOffset(1.2); }
    if (strcmp(yieldPad->GetName(), "c10_yields") == 0 ||
	strcmp(yieldPad->GetName(), "c11_yields") == 0) { gPad->SetTickx(); }
    if (strcmp(yieldPad->GetName(), "c00_yields") == 0 ||
	strcmp(yieldPad->GetName(), "c10_yields") == 0) { gPad->SetTicky(); }

    hYieldsTemplate->Draw("PE");
  }

  // Function pad
  cRelYields->cd();
  hRelYieldsTemplate->SetTitle(plotTitle);
  hRelYieldsTemplate->GetYaxis()->SetTitle("baryon/meson yield");
  hRelYieldsTemplate->GetXaxis()->SetLabelSize(0.050);
  hRelYieldsTemplate->SetStats(0);
  hRelYieldsTemplate->GetYaxis()->SetRangeUser(drawOptions.RelYieldsYmin, drawOptions.RelYieldsYmax); // for beauty: (5e-1, 0.5), for beauty(Lb+Sb): (1e-3, 0.6), for charm: (5e-1, 0.25), for charm and prompt-charm(Lc+ + Sc+): (1e-3, 0.6), for non-prompt charm: (5e-1, 0.6), for non-prompt charm(Lc+ + Sc+): (3e-4, 0.6)
  if (!junctions) { hRelYieldsTemplate->Draw("PE"); }

  // Global pad
  if (relYieldPad != nullptr) { 
    relYieldPad->cd();
    hRelYieldsTemplate->SetTitle("");
    hRelYieldsTemplate->GetYaxis()->SetTitle("baryon/meson yield");
    hRelYieldsTemplate->GetYaxis()->SetTitleSize(0.050);
    hRelYieldsTemplate->GetXaxis()->SetLabelSize(0.050);
    hRelYieldsTemplate->SetStats(0);
    hRelYieldsTemplate->GetYaxis()->SetRangeUser(drawOptions.RelYieldsYmin, drawOptions.RelYieldsYmax); // for beauty: (5e-1, 0.5), for beauty(Lb+Sb): (1e-3, 0.6), for charm: (5e-1, 0.25), for charm and prompt-charm(Lc+ + Sc+): (1e-3, 0.6), for non-prompt charm: (5e-1, 0.6), for non-prompt charm(Lc+ + Sc+): (3e-4, 0.6)

    if (strcmp(relYieldPad->GetName(), "c00_relYields") == 0 || strcmp(relYieldPad->GetName(), "c10_relYields") == 0)
      { gPad->SetTicky(); }
    
    hRelYieldsTemplate->Draw("PE");
  }

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

  // Function pad
  if (junctions) {
    cYields->cd();
    mainPadJunctions->Draw(); miniPadJunctions->Draw();

    hYieldsTemplate->SetMinimum(5e-5); // 5e-5

    hYieldsRatioTemplate->SetTitle("");
    hYieldsRatioTemplate->GetYaxis()->SetTitle("JUN / MON");
    if (yieldMiniPad == nullptr) { hYieldsRatioTemplate->GetXaxis()->SetTitle("Associate"); }
    hYieldsRatioTemplate->GetXaxis()->SetTitleSize(0.050);
    hYieldsRatioTemplate->GetXaxis()->SetLabelSize(0.050);
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

  // Global pad
  if (yieldMiniPad != nullptr) {
    yieldMiniPad->cd();
    hYieldsTemplate->SetMinimum(5e-5); // 5e-5

    hYieldsRatioTemplate->SetTitle("");
    hYieldsRatioTemplate->GetYaxis()->SetTitle("JUN / MON");
    if (strcmp(yieldMiniPad->GetName(), "c21mini_yields") == 0) { hYieldsRatioTemplate->GetXaxis()->SetTitle("Associate"); }
    else { hYieldsRatioTemplate->GetXaxis()->SetTitle(""); }
    hYieldsRatioTemplate->SetStats(0);
    hYieldsRatioTemplate->GetYaxis()->SetRangeUser(5e-2, 50);

    hYieldsRatioTemplate->GetYaxis()->SetLabelSize(0.050); // 3*
    hYieldsRatioTemplate->GetYaxis()->SetTitleSize(0.050); // 3.5*
    hYieldsRatioTemplate->GetYaxis()->SetTitleOffset(30*0.035); // 12*
    hYieldsRatioTemplate->GetXaxis()->SetTickLength(0.035); // 4*
    hYieldsRatioTemplate->GetXaxis()->SetLabelOffset(0.005);
    hYieldsRatioTemplate->GetXaxis()->SetLabelSize(0.06); // 3.5*
    hYieldsRatioTemplate->GetXaxis()->SetTitleSize(0.050); // 3.5*
    hYieldsRatioTemplate->GetXaxis()->SetTitleOffset(30*0.035); // 30*

    if (strcmp(yieldMiniPad->GetName(), "c20mini_yields") == 0 ||
	strcmp(yieldMiniPad->GetName(), "c21mini_yields") == 0) { gPad->SetTickx(); }
    if (strcmp(yieldMiniPad->GetName(), "c20mini_yields") == 0) { gPad->SetTicky(); }
    

    hYieldsRatioTemplate->Draw("PE");
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

    hRelYieldsTemplate->SetMinimum(drawOptions.RelYieldsMin); // for beauty, charm: 1e-2, for beauty(Lb+Sb): 2e-3, for charm and prompt-charm(Lc+ + Sc+): 2e-3, for non-prompt charm(Lc+ + Sc+): 3e-4

    hRelYieldsRatioTemplate->SetTitle("");
    hRelYieldsRatioTemplate->GetYaxis()->SetTitle("JUN / MON");
    hRelYieldsRatioTemplate->GetXaxis()->SetLabelSize(0.05);
    hRelYieldsRatioTemplate->SetStats(0);
    hRelYieldsRatioTemplate->GetYaxis()->SetRangeUser(drawOptions.RelYieldsRatioYmin, drawOptions.RelYieldsRatioYmax); // for beauty: (1, 7), for beauty(Lb+Sb): (2e-1, 70), for charm: (0, 5), for charm and prompt-charm(Lc+ + Sc+): (0, 14), for prompt-charm: (0.5, 1.5), for non-prompt-charm: (0, 7)
    hRelYieldsRatioTemplate->SetMaximum(drawOptions.RelYieldsRatioMax); // for beauty: 7.49, for beauty(Lb+Sb): 79.99, for charm: 5.49, for charm and prompt-charm(Lc+ + Sc+): 15.99, for prompt-charm: 1.99, for non-prompt-charm: 7.49

    hRelYieldsRatioTemplate->GetYaxis()->SetLabelSize(3*0.035);
    hRelYieldsRatioTemplate->GetYaxis()->SetTitleSize(3.0*0.050);
    hRelYieldsRatioTemplate->GetYaxis()->SetTitleOffset(12*0.035);
    hRelYieldsRatioTemplate->GetXaxis()->SetTickLength(3*0.035);
    hRelYieldsRatioTemplate->GetXaxis()->SetLabelOffset(0.035);
    hRelYieldsRatioTemplate->GetXaxis()->SetLabelSize(3*0.060);
    hRelYieldsRatioTemplate->GetXaxis()->SetTitleSize(3*0.035);
    hRelYieldsRatioTemplate->GetXaxis()->SetTitleOffset(50*0.035);
    
    mainPadRelJunctions->cd(); hRelYieldsTemplate->Draw("PE"); 
    miniPadRelJunctions->cd(); hRelYieldsRatioTemplate->Draw("PE");

    // Global pad
    if (relYieldMiniPad != nullptr) {
      relYieldMiniPad->cd();

      hRelYieldsRatioTemplate->GetXaxis()->SetTitleSize(3.5*0.050);
      hRelYieldsRatioTemplate->GetXaxis()->SetTitleOffset(32*0.035);

      if (strcmp(relYieldMiniPad->GetName(), "c00mini_relYields") == 0 ||
	  strcmp(relYieldMiniPad->GetName(), "c01mini_relYields") == 0)
	{ hRelYieldsRatioTemplate->GetYaxis()->SetNdivisions(7); } // think about this

      if (strcmp(relYieldMiniPad->GetName(), "c10mini_relYields") == 0 ||
	  strcmp(relYieldMiniPad->GetName(), "c11mini_relYields") == 0)
	{ hRelYieldsRatioTemplate->GetYaxis()->SetNdivisions(4); } // think about this, doesn't work right now

      if (strcmp(relYieldMiniPad->GetName(), "c01mini_relYields") == 0 ||
	  strcmp(relYieldMiniPad->GetName(), "c11mini_relYields") == 0)
	{ hRelYieldsRatioTemplate->GetXaxis()->SetTitle("multiplicity bin"); }
      
      if (strcmp(relYieldMiniPad->GetName(), "c00mini_relYields") == 0 ||
	  strcmp(relYieldMiniPad->GetName(), "c01mini_relYields") == 0 ||
	  strcmp(relYieldMiniPad->GetName(), "c10mini_relYields") == 0 ||
	  strcmp(relYieldMiniPad->GetName(), "c11mini_relYields") == 0)
	{ gPad->SetTickx(); }

      if (strcmp(relYieldMiniPad->GetName(), "c00mini_relYields") == 0 ||
	  strcmp(relYieldMiniPad->GetName(), "c10mini_relYields") == 0)
	{ gPad->SetTicky(); }
      
      hRelYieldsRatioTemplate->Draw("PE"); }
  }

  // Define legend for yield plot outside for-loop
  TLegend* lYields = new TLegend(0.45, 0.68, 0.75, 0.98); // 0.63 // 0.58 // 0.90 // 0.88
  lYields->SetTextSize(0.05);

  TLegend* lRelYields = new TLegend(drawOptions.LegendRelYieldsXmin, drawOptions.LegendRelYieldsYmin,
				    drawOptions.LegendRelYieldsXmax, drawOptions.LegendRelYieldsYmax);
  lRelYields->SetTextSize(0.05);

  TLegend* lDivYields = new TLegend(0.63, 0.88, 0.9, 0.68);
  lDivYields->SetTextSize(0.05);

  // In order to condense the information displayed in the legend
  if (junctions) {
    TLegendEntry* entryMonash = lYields->AddEntry("Monash", "Monash (MON)", "l");
    entryMonash->SetLineColor(kBlack);
    entryMonash->SetLineStyle(1);
    entryMonash->SetLineWidth(2);

    TLegendEntry* entryJunctions = lYields->AddEntry("Junctions", "Junctions (JUN)", "l");
    entryJunctions->SetLineColor(kRed);
    entryJunctions->SetLineStyle(1);
    entryJunctions->SetLineWidth(2);

    TLegendEntry* entryMonashRel = lRelYields->AddEntry("MonashRel", "Monash", "l");
    entryMonashRel->SetLineColor(kBlack);
    entryMonashRel->SetLineStyle(1);
    entryMonashRel->SetLineWidth(1);

    TLegendEntry* entryJunctionsRel = lRelYields->AddEntry("JunctionsRel", "Junctions", "l");
    entryJunctionsRel->SetLineColor(kRed);
    entryJunctionsRel->SetLineStyle(1);
    entryJunctionsRel->SetLineWidth(1);

    TLegendEntry* entryMonashDiv = lDivYields->AddEntry("MonashDiv", "Monash", "l");
    entryMonashDiv->SetLineColor(kBlack);
    entryMonashDiv->SetLineStyle(1);
    entryMonashDiv->SetLineWidth(1);

    TLegendEntry* entryJunctionsDiv = lDivYields->AddEntry("JunctionsDiv", "Junctions", "l");
    entryJunctionsDiv->SetLineColor(kRed);
    entryJunctionsDiv->SetLineStyle(1);
    entryJunctionsDiv->SetLineWidth(1);
  }

  // Global pad
  if (yieldPad != nullptr) {
    yieldPad->cd();
    lYields->SetBorderSize(0);

    TLegendEntry* entryJunctionsBeauty = lYields->AddEntry("Beauty_Junctions", "B^{+} trigger", "l");
    entryJunctionsBeauty->SetLineColor(kRed);
    entryJunctionsBeauty->SetLineStyle(1);
    entryJunctionsBeauty->SetLineWidth(2);

    TLegendEntry* entryJunctionsCharm = lYields->AddEntry("Charm_Junctions", "D^{+} trigger", "l");
    entryJunctionsCharm->SetLineColor(kBlue);
    entryJunctionsCharm->SetLineStyle(1);
    entryJunctionsCharm->SetLineWidth(2);

    TLegendEntry* entryMonash = lYields->AddEntry("Monash", "Ratio", "l");
    entryMonash->SetLineColor(kBlack);
    entryMonash->SetLineStyle(1);
    entryMonash->SetLineWidth(2);

    if (strcmp(yieldPad->GetName(), "c10_yields") == 0) {

	TLegend* lGlobalRelYieldsMONASH = new TLegend(0.25+0.20, 0.85, 0.55+0.20, 0.95);
	lGlobalRelYieldsMONASH->SetTextSize(0.05);
	lGlobalRelYieldsMONASH->SetBorderSize(0);
	lGlobalRelYieldsMONASH->Draw();

	TLegendEntry* entry = lGlobalRelYieldsMONASH->AddEntry("entryMonash", "Monash", "");
	entry->SetLineColor(kBlack);
	entry->SetLineStyle(1);
	entry->SetLineWidth(2);
      }

      if (strcmp(yieldPad->GetName(), "c00_yields") == 0) {

	TLegend* lGlobalRelYieldsJUNCTIONS = new TLegend(0.25+0.20, 0.85, 0.55+0.20, 0.95);
	lGlobalRelYieldsJUNCTIONS->SetTextSize(0.05);
	lGlobalRelYieldsJUNCTIONS->SetBorderSize(0);
	lGlobalRelYieldsJUNCTIONS->Draw();

	TLegendEntry* entry = lGlobalRelYieldsJUNCTIONS->AddEntry("entryJunctions", "Junctions", "");
	entry->SetLineColor(kBlack);
	entry->SetLineStyle(1);
	entry->SetLineWidth(2);
      }

    // Draw some things on the other pad to save space
    if (strcmp(yieldPad->GetName(), "c11_yields") == 0) {
      TLegend* lYieldsM = new TLegend(0.45, 0.68, 0.75, 0.98); // 0.63 // 0.88 // 0.90 // 0.58
      lYieldsM->SetTextSize(0.05);
      lYieldsM->SetBorderSize(0);
    
      TLegendEntry* entryM60_100 = lYieldsM->AddEntry("M60_100", "60 - 100% multiplicity bin", "l");
      entryM60_100->SetLineColor(kBlack);
      entryM60_100->SetLineStyle(1);
      entryM60_100->SetLineWidth(2);

      /*
      TLegendEntry* entryM40_80 = lYieldsM->AddEntry("M40_80", "40 - 80% multiplicity bin", "l");
      entryM40_80->SetLineColor(kBlack);
      entryM40_80->SetLineStyle(1);
      entryM40_80->SetLineWidth(1);
      */

      TLegendEntry* entryM20_60 = lYieldsM->AddEntry("M20_60", "20 - 60% multiplicity bin", "l");
      entryM20_60->SetLineColor(kBlack);
      entryM20_60->SetLineStyle(2);
      entryM20_60->SetLineWidth(2);
      
      TLegendEntry* entryM0_20 = lYieldsM->AddEntry("M0_20", "0 - 20% multiplicity bin", "l");
      entryM0_20->SetLineColor(kBlack);
      entryM0_20->SetLineStyle(3);
      entryM0_20->SetLineWidth(2);

      lYieldsM->Draw();
    }
  }

  // Label the pads in the case of using global pads
  // Default labelling is (a), (b), (c), ...
  if (drawOptions.labelID != nullptr) {
    TLegend* lLab;

    // Yield plots
    if (yieldPad != nullptr) {
      if (strcmp(yieldPad->GetName(), "c00_yields") == 0 ||
	  strcmp(yieldPad->GetName(), "c10_yields") == 0) {
	lLab = new TLegend(0.05+0.20, 0.85, 0.20+0.20, 0.95); // left margin = 0.20
      }
      else { lLab = new TLegend(0.05, 0.85, 0.20, 0.95); }
      yieldPad->cd();
    }

    // Yield ratio plot
    if (yieldMiniPad != nullptr) {
      if (strcmp(yieldMiniPad->GetName(), "c20mini_yields") == 0) {
	lLab = new TLegend(0.05+0.20, 0.85, 0.20+0.20, 0.95); // left margin = 0.20
      }
      else { lLab = new TLegend(0.05, 0.85, 0.20, 0.95); }
      yieldMiniPad->cd();
    }

    // Relative yield plots
    if (relYieldPad != nullptr) {
      if (strcmp(relYieldPad->GetName(), "c00_relYields") == 0 ||
	  strcmp(relYieldPad->GetName(), "c10_relYields") == 0) {
	lLab = new TLegend(0.05+0.20, 0.75, 0.20+0.20, 0.85); // left margin = 0.20
      }
      else { lLab = new TLegend(0.05, 0.75, 0.20, 0.85); }
      relYieldPad->cd();
    }
    
    lLab->SetTextSize(0.05);
    lLab->SetBorderSize(0);
    lLab->AddEntry("", drawOptions.labelID, "");
    lLab->Draw();
  }

  // Draw canvas and legend of yields for different associates
  if (!junctions) {
     cYields->cd(); gPad->SetLogy();
     cYields->Draw();
     lYields->Draw();
     cRelYields->cd(); // gPad->SetLogy();
     lRelYields->Draw();

     // Global pad
     if (yieldPad != nullptr) {
       yieldPad->cd(); gPad->SetLogy();
       if (strcmp(yieldPad->GetName(), "c01_yields") == 0) { lYields->Draw(); }
     }
  }
  
  if (junctions) {
    cYields->cd();
    mainPadJunctions->cd(); gPad->SetLogy();
    lYields->Draw();
    miniPadJunctions->cd(); gPad->SetLogy();

    cRelYields->cd();
    mainPadRelJunctions->cd();
    if (drawOptions.MainPadOptLog) { gPad->SetLogy(); } // log ON for ALL Lambda + Sigma plots
    lRelYields->Draw();
    miniPadRelJunctions->cd();
    if (drawOptions.MiniPadOptLog) { gPad->SetLogy(); } // log ON for BEAUTY Lambda + Sigma plots

    // Global pad
    if (yieldMiniPad != nullptr) {
      yieldMiniPad->cd(); gPad->SetLogy();
    }
    if (relYieldPad != nullptr) {
      if (drawOptions.MiniPadOptLog) {
	relYieldMiniPad->cd(); // This raises an error if relYieldMiniPad is undefined (or nullptr)
	gPad->SetLogy(); } // log ON for ALL Lambda + Sigma plots
      
      relYieldPad->cd();
      if (drawOptions.MainPadOptLog) { gPad->SetLogy(); } // log ON for ALL Lambda + Sigma plots
      
      if (strcmp(relYieldPad->GetName(), "c01_relYields") == 0) {

	TLegend* lGlobalRelYields1 = new TLegend(0.25, 0.55, 0.55, 0.85);
	lGlobalRelYields1->SetTextSize(0.05);
	lGlobalRelYields1->SetBorderSize(0);
	lGlobalRelYields1->Draw();
	
	TLegendEntry* entryJunctionsBeauty = lGlobalRelYields1->AddEntry("Beauty", "B^{+} Junctions", "l");
	entryJunctionsBeauty->SetLineColor(kRed);
	entryJunctionsBeauty->SetLineStyle(1);
	entryJunctionsBeauty->SetLineWidth(2);
	
	TLegendEntry* entryJunctionsCharm = lGlobalRelYields1->AddEntry("Charm", "D^{+} Junctions", "l");
	entryJunctionsCharm->SetLineColor(kBlue);
	entryJunctionsCharm->SetLineStyle(1);
	entryJunctionsCharm->SetLineWidth(2);

	TLegendEntry* entryMonash = lGlobalRelYields1->AddEntry("Ratio", "Both Monash", "l");
	entryMonash->SetLineColor(kBlack);
	entryMonash->SetLineStyle(1);
	entryMonash->SetLineWidth(2);

	TLegend* lGlobalRelYields2 = new TLegend(0.60, 0.55, 0.85, 0.85);
	lGlobalRelYields2->SetTextSize(0.05);
	lGlobalRelYields2->SetBorderSize(0);
	lGlobalRelYields2->Draw();
	
	TLegendEntry *entryLb = lGlobalRelYields2->AddEntry((TObject*)0, "B^{+}#Lambda_{b}^{0}/B^{+}B^{-}", "l");
	entryLb->SetLineColor(kRed);

	TLegendEntry *entrySb = lGlobalRelYields2->AddEntry((TObject*)0, "B^{+}#Sigma_{b}^{0}/B^{+}B^{-}", "l");
	entrySb->SetLineColor(kRed);
	entrySb->SetLineStyle(2);
	entrySb->SetLineWidth(2);

	TLegendEntry *entryLc = lGlobalRelYields2->AddEntry((TObject*)0, "D^{+}#bar#Lambda_{c}^{+}/D^{+}D^{-}", "l");
	entryLc->SetLineColor(kBlue);

	TLegendEntry *entrySc = lGlobalRelYields2->AddEntry((TObject*)0, "D^{+}#bar#Sigma_{c}^{+}/D^{+}D^{-}", "l");
	entrySc->SetLineColor(kBlue);
	entrySc->SetLineStyle(2);
	entrySc->SetLineWidth(2);
      } // legend
    } // if relYieldPad != nullptr
  } // if junctions 
  
  if (division) { cDivYields->cd(); gPad->SetLogy(); lDivYields->Draw(); }

  // Check for memory-error
  std::cout << "If this message is followed by a memory error:" << std::endl;
  std::cout << "most likely the intAssociate variable at the beginning of the code has not been changed yet" << std::endl;
  std::cout << "i.e. you are trying to access an associate number which is out of bounds" << std::endl;

  // The yields are stored in a 3D-array with structure [associate][tune][condition]
  // in order to maintain clarity and to allow for more flexible filling of dependencies
  Double_t vYields[vHistAndLabels.size()/Nhist][2][Nconfigs];
  TH1D* hYields[vHistAndLabels.size()/Nhist][Nhist]; 
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

  // Calculate the erors using the sampling method
  // This part is NOT dynamically allocated! (can be done by seperating trees in yieldSampling.C)
  Double_t vYieldsErr[vHistAndLabels.size()/Nhist][2][Nconfigs];
  Double_t vYieldsRatioErr[vHistAndLabels.size()/Nhist][Nconfigs];
  Double_t vRelYieldsErr[vHistAndLabels.size()/Nhist][2][Nconfigs];
  Double_t vRelYieldsRatioErr[vHistAndLabels.size()/Nhist][Nconfigs];

  
  // The error are calculated with a sampling method (as explained in these scripts ....)
  // Retrieve the arrays with errors, identical structure to the vYields arrays
  // Open the ROOT file
  TFile *inputFile = TFile::Open(errFileName); // dont forget to change!
  if (!inputFile || !inputFile->IsOpen()) {
    // Handle error opening the file
    std::cout << "Don't forget the file path" << std::endl;
    return;
  }
  
  std::cout << "entered tree name = " << errTreeName << std::endl;

  // Get the TTree
  TTree *inputTree = dynamic_cast<TTree*>(inputFile->Get(errTreeName));
  
  if (!inputTree) { std::cout << "oeps, waar is mn tree?" << std::endl; }
  
  // Set branch addresses to connect branches with the arrays
  inputTree->SetBranchAddress("vYieldsErr", vYieldsErr);
  inputTree->SetBranchAddress("vYieldsRatioErr", vYieldsRatioErr);
  inputTree->SetBranchAddress("vRelYieldsErr", vRelYieldsErr);
  inputTree->SetBranchAddress("vRelYieldsRatioErr", vRelYieldsRatioErr);
  
  inputTree->GetEntry(0);

  /*
  std::cout << std::endl;
  std::cout << "vHistAndLabels.size() / Nhist = " << vHistAndLabels.size() / Nhist << std::endl;
  std::cout << "Nconfigs = " << Nconfigs << std::endl;
  std::cout << std::endl;
  
  std::cout << "vError = " << std::endl;
  for (Int_t i = 0; i < vHistAndLabels.size() / Nhist; i++) {
    std::cout << "Associate nr = " << i << std::endl;
    for (Int_t j = 0; j < 2; j++) {
      if (j == 0) { std::cout << "MONASH" << std::endl; }
      if (j == 1) { std::cout << "JUNCTIONS" << std::endl; }
      for (Int_t k = 0; k < Nconfigs; k++) {
	std::cout << "Multiplicity bin k = " << k << std::endl;
	std::cout << vYieldsErr[i][j][k] << std::endl;
      }
    }
  }
  */
  

  /*
  // This part takes the errors from txt files
  // Can be used optionally if there is a mistake with the error files
  // 1. vYieldsErr.txt
  std::ifstream inputFileYieldsErr("vYieldsErrBBMULTCONDENSED.txt");

  if (!inputFileYieldsErr.is_open()) {
        std::cerr << "Error opening file!" << std::endl;
  }

  for (int i = 0; i < vHistAndLabels.size() / Nhist; ++i) {
        for (int j = 0; j < 2; ++j) {
            for (int k = 0; k < Nconfigs; ++k) {
                double value;
                if (!(inputFileYieldsErr >> value)) {
                    std::cerr << "Error reading value from file!" << std::endl;
                }
                vYieldsErr[i][j][k] = value;
            }
        }
    }
  inputFileYieldsErr.close();

  // 2. vYieldsRatioErr.txt
  std::ifstream inputFileYieldsRatioErr("vYieldsRatioErrBBMULTCONDENSED.txt");

  if (!inputFileYieldsRatioErr.is_open()) {
        std::cerr << "Error opening file!" << std::endl;
  }

  for (int i = 0; i < vHistAndLabels.size() / Nhist; ++i) {
            for (int k = 0; k < Nconfigs; ++k) {
                double value;
                if (!(inputFileYieldsRatioErr >> value)) {
                    std::cerr << "Error reading value from file!" << std::endl;
                }
                vYieldsRatioErr[i][k] = value;
            }
    }
  inputFileYieldsRatioErr.close();

  // 3. vRelYieldsErr.txt
  std::ifstream inputFileRelYieldsErr("vRelYieldsErrBBMULTCONDENSED.txt");

  if (!inputFileRelYieldsErr.is_open()) {
        std::cerr << "Error opening file!" << std::endl;
  }

  for (int i = 0; i < vHistAndLabels.size() / Nhist; ++i) {
        for (int j = 0; j < 2; ++j) {
            for (int k = 0; k < Nconfigs; ++k) {
                double value;
                if (!(inputFileRelYieldsErr >> value)) {
                    std::cerr << "Error reading value from file!" << std::endl;
                }
                vRelYieldsErr[i][j][k] = value;
            }
        }
    }
  inputFileRelYieldsErr.close();

  // 4. vRelYieldsRatioErr.txt
  std::ifstream inputFileRelYieldsRatioErr("vRelYieldsRatioErrBBMULTCONDENSED.txt");

  if (!inputFileRelYieldsRatioErr.is_open()) {
        std::cerr << "Error opening file!" << std::endl;
  }

  for (int i = 0; i < vHistAndLabels.size() / Nhist; ++i) {
            for (int k = 0; k < Nconfigs; ++k) {
                double value;
                if (!(inputFileRelYieldsRatioErr >> value)) {
                    std::cerr << "Error reading value from file!" << std::endl;
                }
                vRelYieldsRatioErr[i][k] = value;
            }
    }
  inputFileRelYieldsRatioErr.close();
   
  
  // Print to check  
  std::cout << "vYieldsErr" << std::endl;
  for (Int_t i = 0; i < vHistAndLabels.size() / Nhist; i++) {
    for (Int_t j = 0; j < 2; j++) {
      if (j == 0) { std::cout << "MONASH" << std::endl; }
      if (j == 1) { std::cout << "JUNCTIONS" << std::endl; }
      for (Int_t k = 0; k < Nconfigs; k++) {
	std::cout << vYieldsErr[i][j][k] << std::endl;
      }
    }
  }

  std::cout << "vYieldsRatioErr" << std::endl;
  for (Int_t i = 0; i < vHistAndLabels.size() / Nhist; i++) {
      for (Int_t k = 0; k < Nconfigs; k++) {
	std::cout << vYieldsRatioErr[i][k] << std::endl;
      }
  }

  std::cout << "vRelYieldsErr" << std::endl;
  for (Int_t i = 0; i < vHistAndLabels.size() / Nhist; i++) {
    for (Int_t j = 0; j < 2; j++) {
      for (Int_t k = 0; k < Nconfigs; k++) {
	std::cout << vRelYieldsErr[i][j][k] << std::endl;
      }
    }
  }

  std::cout << "vRelYieldsRatioErr" << std::endl;
  for (Int_t i = 0; i < vHistAndLabels.size() / Nhist; i++) {
      for (Int_t k = 0; k < Nconfigs; k++) {
	std::cout << vRelYieldsRatioErr[i][k] << std::endl;
      }
  }
  */  



    

  
  for (Int_t i = 0; i < vHistAndLabels.size(); i+=Nhist) {

    HistAndLabels histEntry = vHistAndLabels[i];

    // Compare OS and SS on the same canvas    
    TCanvas* cOverview = new TCanvas(Form("cOverview_%s_%i", plotTitle, i), Form("%s%s and %s%s both drawn for %s", histEntry.TriggerName, histEntry.AssociateNameOS, histEntry.TriggerName, histEntry.AssociateNameSS, histEntry.LegendTitle), 800, 600);
    setCanvasMargins(cOverview, 0.15, 0.1, 0.1, 0.1);
    cOverview->cd();
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
      
      cOverview->cd();
      mainPad->cd();
      if (j == i) { hDPhiOS->Draw("hist E"); hDPhiSS->Draw("same hist E"); }
      else { hDPhiOS->Draw("same hist E"); hDPhiSS->Draw("same hist E"); }
      
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
      if (j == i) { hCorr->Draw("hist E"); }
      else { hCorr->Draw("same hist E"); }

      // Yield is calculated using the whole DPhi range, can be changed if desired
      hYields[i/Nhist][j-i] = new TH1D(Form("hYields_%s_%i_%i", plotTitle, i, j), Form("hYields_%i_%i", i, j), vHistAndLabels.size()/Nhist, 0, vHistAndLabels.size()/Nhist);

      // Divide JUNCTIONS by MONASH (only need half of the entries c.f. before)
      if (junctions && (j-i) < Nhist/2) {
	hYieldsRatio[i/Nhist][j-i] = new TH1D(Form("hYieldsRatio_%s_%i_%i", plotTitle, i, j), Form("hYieldsRatio_%i_%i", i, j), vHistAndLabels.size()/Nhist, 0, vHistAndLabels.size()/Nhist);
      }

      // Calculate the yields, the region can be specified if desired
      Double_t yield = hCorr->Integral();
      std::cout << Form("yield for %s associate (%s) = ", histEntry.AssociateNameOS, histEntry.LegendTitle) << yield*1e3 << "e-3" << std::endl;

      // For JUNCTIONS (which means both MONASH and JUNCTIONS):
      // The yields are stored in a 3D-array with structure [associate][tune][condition]
      // in order to maintain clarity and to allow for more flexible filling of dependencies

      // MONASH (first half of entries)
      // And equivalently for ONLY JUNCTIONS:
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
	if (j-i >= Nconfigs) { 
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
      // hYields[i/Nhist][j-i]->SetBinError(1+i/Nhist, 1e-9);

      if (errTreeName != nullptr) { // Errors are calculated for this dependency
	// The errors can be calculated for the ONLY MONASH or ONLY JUNCTIONS case
	if (j-i < Nconfigs && drawOptions.OptError != -1) {
	  /*
	  std::cout << "error = " << vYieldsErr[i/Nhist][0][j-i] << std::endl;
	  std::cout << "i/Nhist = " << i/Nhist << std::endl;
	  std::cout << "j-i = " << j-i << std::endl;
	  */
	  hYields[i/Nhist][j-i]->SetBinError(1+i/Nhist, vYieldsErr[i/Nhist][drawOptions.OptError][j-i]);
	}
	// The general case is here, for the combined plots:
	if (j-i < Nconfigs && drawOptions.OptError == -1) { // MONASH, was j < Nhist/2
	  /*
	  std::cout << "MONASH error = " << vYieldsErr[i/Nhist][0][j-i] << std::endl;
	  std::cout << "i/Nhist = " << i/Nhist << std::endl;
	  std::cout << "j-i = " << j-i << std::endl;
	  */
	  hYields[i/Nhist][j-i]->SetBinError(1+i/Nhist, vYieldsErr[i/Nhist][0][j-i]);
	}
	
	
	if (junctions && j-i >= Nconfigs) { // JUNCTIONS, was j >= Nhist/2
	  /*
	  std::cout << "JUNCTIONS error = " << vYieldsErr[i/Nhist][1][j-i] << std::endl;
	  std::cout << "i/Nhist = " << i/Nhist << std::endl;
	  std::cout << "j-i-Nconfigs = " << j-i-Nconfigs << std::endl;
	  */
	  hYields[i/Nhist][j-i]->SetBinError(1+i/Nhist, vYieldsErr[i/Nhist][1][j-i-Nconfigs]);
	}
      };
      
      hYields[i/Nhist][j-i]->SetLineStyle(histEntry.LineStyle);
      hYields[i/Nhist][j-i]->SetLineWidth(histEntry.LineWidth);
      hYields[i/Nhist][j-i]->SetLineColor(drawOptions.LineColor); // histEntry.Color
      hYields[i/Nhist][j-i]->SetMarkerColor(histEntry.Color);
      hYields[i/Nhist][j-i]->SetMarkerStyle(0);
      
      cYields->cd();
      if (!junctions) { hYields[i/Nhist][j-i]->Draw("same PE"); }
      if (junctions) { mainPadJunctions->cd(); hYields[i/Nhist][j-i]->Draw("same PE"); }

      if (yieldPad != nullptr) {
      yieldPad->cd();
      hYields[i/Nhist][j-i]->Draw("same PE");
      }

      // Condense the information displayed in the legend for MONASH + JUNCTIONS to only show MONASH
      // This is not done for the global pad in order to keep the legend entries black
      if (yieldPad == nullptr) {
	// MONASH + JUNCTIONS
	if (i == 0 && junctions && j < Nhist/2) {
	  lYields->AddEntry(hYields[i/Nhist][j-i], Form("%s", histEntry.LegendTitle));
	}
	// MONASH
	if (i == 0 && !junctions) {
	  lYields->AddEntry(hYields[i/Nhist][j-i], Form("%s", histEntry.LegendTitle));
	}
      }

      // Define associate label names for relative yield plot
      // (i == 0) because it only needs to be done once
      if (i == 0 && j < Nconfigs && !junctions) { hRelYieldsTemplate->GetXaxis()->SetBinLabel(1+(j-i), histEntry.LegendTitle); }
      if (i == 0 && j < Nconfigs && junctions) { hRelYieldsRatioTemplate->GetXaxis()->SetBinLabel(1+(j-i), histEntry.LegendTitle); }
      
      } // END OF j for-loop over configurations

    // Draw ratios of JUNCTIONS / MONASH yields
    if (junctions) { for (Int_t k = 0; k < Nhist/2; k++) {
	
	// Get the JUNCTIONS / MONASH yield, given that MONASH is stored before JUNCTIONS in the
	// input configurations
	Double_t yieldMonash = 0; Double_t yieldJunctions = 0;
	yieldMonash = vYields[i/Nhist][0][k];
	yieldJunctions = vYields[i/Nhist][1][k];
      
	hYieldsRatio[i/Nhist][k]->SetBinContent(1+i/Nhist, yieldJunctions / yieldMonash);
	if (errTreeName != nullptr) {
	  hYieldsRatio[i/Nhist][k]->SetBinError(1+i/Nhist, vYieldsRatioErr[i/Nhist][k]);
	}
	if (!errTreeName) { hYieldsRatio[i/Nhist][k]->SetBinError(1+i/Nhist, 1e-9); }

	miniPadJunctions->cd();
	hYieldsRatio[i/Nhist][k]->Draw("same PE");

	if (yieldMiniPad != nullptr) {
	  yieldMiniPad->cd();
	  hYieldsRatio[i/Nhist][k]->Draw("same PE");
	}
	
      } // END of k for-loop over yields array
    } // if (junctions) for k-loop

    // Draw relative yields for B+B-/B+Lb  and B+B-/B+Sb
    // Has the possibility to be generalised for more associates in the future
    cRelYields->cd();
    if (isInArray(i/Nhist, intAssociate, NAssociates)) { for (Int_t l = 0; l < Nconfigs; l++) {

	if (junctions) { mainPadRelJunctions->cd(); }
	
	// MONASH
	hRelYields[0][l] = new TH1D(Form("hRelYields_MONASH_%s_%i_%i", plotTitle, i, l), Form("hRelYields_%i_%i", i, l), Nconfigs, 0, Nconfigs);
	hRelYields[0][l]->SetBinContent(1+l, vYields[i/Nhist][0][l] / vYields[0][0][l]);
	if (errTreeName != nullptr) {
	  hRelYields[0][l]->SetBinError(1+l, vRelYieldsErr[i/Nhist][0][l]); }
	if (!errTreeName) { hRelYields[0][l]->SetBinError(1+l, 1e-9); }
	hRelYields[0][l]->SetLineColor(kBlack);
	hRelYields[0][l]->SetLineStyle(RelYieldsLineStyles[counterLineStyle]);
	hRelYields[0][l]->SetLineWidth(RelYieldsLineWidths[counterLineStyle]);
	
	hRelYields[0][l]->Draw("same PE");

	if (relYieldPad != nullptr) {
	    relYieldPad->cd();
	    hRelYields[0][l]->Draw("same PE");
	  }
	
	// JUNCTIONS
	if (junctions) {
	  hRelYields[1][l] = new TH1D(Form("hRelYields_JUNCTIONS_%s_%i_%i", plotTitle, i, l), Form("hRelYields_%i_%i", i, l), Nconfigs, 0, Nconfigs);
	  hRelYields[1][l]->SetBinContent(1+l, vYields[i/Nhist][1][l] / vYields[0][1][l]);
	  if (errTreeName != nullptr) {
	    hRelYields[1][l]->SetBinError(1+l, vRelYieldsErr[i/Nhist][1][l]); }
	  if (!errTreeName) { hRelYields[1][l]->SetBinError(1+l, 1e-9); }
	  hRelYields[1][l]->SetLineColor(kRed);
	  hRelYields[1][l]->SetLineStyle(RelYieldsLineStyles[counterLineStyle]);
	  hRelYields[1][l]->SetLineWidth(RelYieldsLineWidths[counterLineStyle]);
	
	  hRelYields[1][l]->Draw("same PE");

	  if (relYieldPad != nullptr) {
	    relYieldPad->cd();
	    if (strcmp(relYieldPad->GetName(), "c01_relYields") == 0 ||
		strcmp(relYieldPad->GetName(), "c11_relYields") == 0)
	      { hRelYields[1][l]->SetLineColor(kBlue); }
	    hRelYields[1][l]->Draw("same PE");
	  }

	  hRelYieldsRatio[l] = new TH1D(Form("hRelYieldsRatio_JUNCTIONS_%s_%i_%i", plotTitle, i, l), Form("hRelYieldsRatio_%i_%i", i, l), Nconfigs, 0, Nconfigs);
	  
	  // Draw the JUNCTIONS / MONASH ratio
	  hRelYieldsRatio[l]->SetBinContent(1+l,
					    (vYields[i/Nhist][1][l] / vYields[0][1][l]) /
					    (vYields[i/Nhist][0][l] / vYields[0][0][l]));
	  if (errTreeName != nullptr) {
	    hRelYieldsRatio[l]->SetBinError(1+l, vRelYieldsRatioErr[i/Nhist][l]); }
	  if (!errTreeName) { hRelYieldsRatio[l]->SetBinError(1+l, 1e-9); }
	  hRelYieldsRatio[l]->SetLineColor(kBlack);
	  hRelYieldsRatio[l]->SetLineStyle(RelYieldsLineStyles[counterLineStyle]);
	  hRelYieldsRatio[l]->SetLineWidth(RelYieldsLineWidths[counterLineStyle]);
	
	  miniPadRelJunctions->cd();
	  hRelYieldsRatio[l]->Draw("same PE");

	  if (relYieldMiniPad != nullptr) {
	    relYieldMiniPad->cd();
	    hRelYieldsRatio[l]->Draw("same PE");
	  }
	  
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
    cOverview->cd();
    mainPad->cd(); gPad->SetLogy(); lOverview->Draw(); lCorr->Draw();
    miniPad->cd(); gPad->SetLogy(); 
    cOverview->Draw();
    
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
  
  if (write) {
    cYields->SaveAs(Form("Plots/PDF_cYields_%s.pdf", errTreeName));
    cRelYields->SaveAs(Form("Plots/PDF_cRelYields_%s_%s.pdf", errTreeName, drawOptions.WriteName));

    cYields->SaveAs(Form("Plots/PNG_cYields_%s.png", errTreeName));
    cRelYields->SaveAs(Form("Plots/PNG_cRelYields_%s_%s.png", errTreeName, drawOptions.WriteName));

    cYields->SaveAs(Form("Plots/MACRO_cYields_%s.C", errTreeName));
    cRelYields->SaveAs(Form("Plots/MACRO_cRelYields_%s_%s.C", errTreeName, drawOptions.WriteName));
  }
  
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

	if (k == 1) { continue; }
	if (k == 3) { continue; }
	if (k == 5) { continue; }
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
	TH1D* hDPhiOSNextNext; TH1D* hDPhiSSNextNext; TH1D* hTrPtOSNextNext; TH1D* hTrPtSSNextNext;
	
	if (k+1 < vHistNameAndLabels.size()) {
	  HistNameAndLabels histEntryNext = vHistNameAndLabels[k+1]; // combining multiplicity bins
	
	  hDPhiOSNext = (TH1D*)OStree->Get(histEntryNext.HistName);
	  hDPhiSSNext = (TH1D*)SStree->Get(histEntryNext.HistName);
	  hTrPtOSNext = (TH1D*)OStree->Get(histEntryNext.TrPtName);
	  hTrPtSSNext = (TH1D*)SStree->Get(histEntryNext.TrPtName);

	  if (strcmp(rootEntry.TriggerName, rootEntry.AssociateNameSS) == 0) { hDPhiSSNext->Scale(0.5); } // Prevent double-counting

	  hDPhiOSNext->Scale(1/hTrPtOSNext->Integral());
	  hDPhiSSNext->Scale(1/hTrPtSSNext->Integral());

	  // Only makes sense to check the next-to-next bin if there is a next-to-next bin
	  if (k+2 < vHistNameAndLabels.size()) {
	    HistNameAndLabels histEntryNextNext = vHistNameAndLabels[k+1]; // combining multiplicity bins
	
	    hDPhiOSNextNext = (TH1D*)OStree->Get(histEntryNext.HistName);
	    hDPhiSSNextNext = (TH1D*)SStree->Get(histEntryNext.HistName);
	    hTrPtOSNextNext = (TH1D*)OStree->Get(histEntryNext.TrPtName);
	    hTrPtSSNextNext = (TH1D*)SStree->Get(histEntryNext.TrPtName);
	    
	    if (strcmp(rootEntry.TriggerName, rootEntry.AssociateNameSS) == 0) { hDPhiSSNext->Scale(0.5); } // Prevent double-counting
	  
	    hDPhiOSNextNext->Scale(1/hTrPtOSNextNext->Integral());
	    hDPhiSSNextNext->Scale(1/hTrPtSSNextNext->Integral());
	
	  } // k-next-to-next makes sense
	  
	} // k-next makes sense
	
	// Combine multiplicity bins in order not to overload the reader
	// This selection is kept explicit to allow some flexiblity in combining bins
	// After the event loop one can easily combine the desired histograms

	// Explanation of binning:
	// 1st = 80-100
	// 2nd = 60-80
	
	// 3rd = 40-60
	// 4th = 20-40
	
	// 5th = 5-20
	// 6th = 1-5
	// 7th = 0-1

	if (k == 0) { // combine 1st and 2nd bin
	  hDPhiOS->Add(hDPhiOSNext);
	  hDPhiSS->Add(hDPhiSSNext);
	  histEntry.LegendTitle = concatString(pathEntry.LegendTitle, "60-100 % multiplicity bin");
	}

	/*
	if (k == 1) {
	  hDPhiOS->Add(hDPhiOSNext);
	  hDPhiSS->Add(hDPhiSSNext);
	  histEntry.LegendTitle = concatString(pathEntry.LegendTitle, "40-80% multiplicity bin");
	}
	*/

	if (k == 2) { // combine 3rd and 4th bin
	  hDPhiOS->Add(hDPhiOSNext);
	  hDPhiSS->Add(hDPhiSSNext);
	  histEntry.LegendTitle = concatString(pathEntry.LegendTitle, "20-60 % multiplicity bin");
	}


	if (k == 4) { // combine 5th, 6th and 7th bin
	  hDPhiOS->Add(hDPhiOSNext); hDPhiOS->Add(hDPhiOSNextNext);
	  hDPhiSS->Add(hDPhiSSNext); hDPhiSS->Add(hDPhiSSNextNext);
	  histEntry.LegendTitle = concatString(pathEntry.LegendTitle, "0-20 % multiplicity bin");
	}

	/*
        if (k == 5) {
	  histEntry.LegendTitle = concatString(pathEntry.LegendTitle, histEntry.LegendTitle);
	}
	*/
	
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



int B_Balancing_GeneralPlotting() {

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

  // Before the calls of the plotting function, we set up global pads
  // in order to draw several outputs on the same canvas
  // Define the global yield canvas for the condensed multiplicity bins
  TCanvas* c2x3_yields = new TCanvas("c2x3_yields", "balancing yields for beauty and charm on a 2x3 canvas", 1200, 1000);
  setCanvasMargins(c2x3_yields, 0.1, 0.05, 0.1, 0.05);
  c2x3_yields->cd();
  
  // Necessary to avoid overlapping of axes
  Double_t eps = 1e-3;

  // Subpads are created with names indicating their position on the large canvas (xy)
  // A TLegendEntry is used to add identifiers to each pad
  // The standard is (a), (b), (c), etc. but this can be changed by the user
  TPad* c00_yields = new TPad("c00_yields", "yields for JUNCTIONS beauty", 0.05, 0.65, 0.50, 0.95); // 0.05, 0.55, 0.50, 0.95
  c00_yields->SetTopMargin(0);
  c00_yields->SetLeftMargin(0.20);
  c00_yields->SetRightMargin(eps);
  c00_yields->SetBottomMargin(eps);
  c00_yields->Draw();

  TPad* c01_yields = new TPad("c01_yields", "yields for JUNCTIONS beauty", 0.50+eps, 0.65, 0.95, 0.95); // 0.50+eps, 0.55, 0.95, 0.95
  c01_yields->SetTopMargin(0);
  c01_yields->SetLeftMargin(0.20);
  c01_yields->SetLeftMargin(0);
  c01_yields->SetBottomMargin(eps);
  c01_yields->Draw();
  
  TPad* c10_yields = new TPad("c10_yields", "yields for MONASH charm", 0.05, 0.35, 0.50, 0.65+eps); // 0.05, 0.15, 0.50, 0.55+eps
  c10_yields->SetLeftMargin(0.20);
  c10_yields->SetRightMargin(eps);
  c10_yields->SetTopMargin(0);
  c10_yields->SetBottomMargin(0);
  c10_yields->Draw();
  
  TPad* c11_yields = new TPad("c11_yields", "yields for MONASH charm", 0.50+eps, 0.35, 0.95, 0.65+eps); // 0.50+eps, 0.15, 0.95, 0.55+eps
  c11_yields->SetLeftMargin(0);
  c11_yields->SetTopMargin(0);
  c11_yields->SetBottomMargin(0);
  c11_yields->Draw();

  // Minipads
  TPad* c20mini_yields = new TPad("c20mini_yields", "yields ratio for beauty", 0.05, 0, 0.50, 0.35+eps); // 0.05, 0.05, 0.50, 0.15+eps
  c20mini_yields->SetLeftMargin(0.20);
  c20mini_yields->SetRightMargin(eps);
  c20mini_yields->SetTopMargin(0);
  c20mini_yields->SetBottomMargin(0.15);
  c20mini_yields->Draw();
  
  TPad* c21mini_yields = new TPad("c21mini_yields", "yields ratio for charm", 0.50+eps, 0, 0.95, 0.35+eps); // 0.50+eps, 0.05, 0.95, 0.15+eps
  c21mini_yields->SetLeftMargin(0);
  c21mini_yields->SetTopMargin(0);
  c21mini_yields->SetBottomMargin(0.15);
  c21mini_yields->Draw();
  //
  
  // Define the global relative yield canvas for the baryon/meson ratios
  TCanvas* c2x2_relYields = new TCanvas("c2x2_relYields", "relative balancing yields for beauty and charm on a 2x2 canvas", 1200, 1000);
  setCanvasMargins(c2x2_relYields, 0.1, 0.1, 0.1, 0.05);
  c2x2_relYields->cd();
  
  TPad* c00_relYields = new TPad("c00_relYields", "relative yields for MONASH beauty", 0.050, 0.675, 0.50, 1.0);
  c00_relYields->SetLeftMargin(0.20);
  c00_relYields->SetRightMargin(eps);
  c00_relYields->SetBottomMargin(eps);
  c00_relYields->Draw();

  // MiniPad
  TPad* c00mini_relYields = new TPad("c00mini_relYields", "ratio relative yields for MONASH beauty", 0.050, 0.575, 0.50, 0.675+eps);
  c00mini_relYields->SetTopMargin(0);
  c00mini_relYields->SetLeftMargin(0.20);
  c00mini_relYields->SetRightMargin(eps);
  c00mini_relYields->SetBottomMargin(0.40);
  c00mini_relYields->Draw();
  //
  
  TPad* c01_relYields = new TPad("c01_relYields", "relative yields for JUNCTIONS beauty", 0.50+eps, 0.675, 0.95, 1.0);
  c01_relYields->SetLeftMargin(0);
  c01_relYields->SetBottomMargin(eps);
  c01_relYields->Draw();

  // MiniPad
  TPad* c01mini_relYields = new TPad("c01mini_relYields", "ratio relative yields for JUNCTIONS beauty", 0.50+eps, 0.575, 0.95, 0.675+eps);
  c01mini_relYields->SetTopMargin(0);
  c01mini_relYields->SetLeftMargin(0);
  c01mini_relYields->SetBottomMargin(0.40);
  c01mini_relYields->Draw();
  //
  
  TPad* c10_relYields = new TPad("c10_relYields", "relative yields for MONASH charm", 0.05, 0.20, 0.50, 0.525);
  // c10_relYields->SetTopMargin(0);
  c10_relYields->SetLeftMargin(0.20);
  c10_relYields->SetRightMargin(eps);
  c10_relYields->SetBottomMargin(eps);
  c10_relYields->Draw();

  // miniPad
  TPad* c10mini_relYields = new TPad("c10mini_relYields", "ratio relative yields for MONASH charm", 0.05, 0.10, 0.50, 0.20+eps);
  c10mini_relYields->SetLeftMargin(0.20);
  c10mini_relYields->SetRightMargin(eps);
  c10mini_relYields->SetTopMargin(0);
  c10mini_relYields->SetBottomMargin(0.40);
  c10mini_relYields->Draw();
  //
  
  TPad* c11_relYields = new TPad("c11_relYields", "relative yields for JUNCTIONS charm", 0.50+eps, 0.20, 0.95, 0.525);
  // c11_relYields->SetTopMargin(0);
  c11_relYields->SetLeftMargin(0);
  c11_relYields->SetBottomMargin(eps);
  c11_relYields->Draw();

  // miniPad
  TPad* c11mini_relYields = new TPad("c11mini_relYields", "ratio relative yields for JUNCTIONS charm", 0.50+eps, 0.10, 0.95, 0.20+eps);
  c11mini_relYields->SetLeftMargin(0);
  c11mini_relYields->SetTopMargin(0);
  c11mini_relYields->SetBottomMargin(0.40);
  c11mini_relYields->Draw();
  //

  // Set up drawing options to automate the plotting process.
  // Keep in mind that these structs are only used for the relative ratio plots, and hence only make sense
  // for the general multiplicity (all multiplicity bins) plots.
  //
  /*
  struct DrawOptions {
  // Name which is used for writing the plots to the local directory
  const char* WriteName;

  std::vector<Int_t> vAssociates;
  
  Double_t RelYieldsYmin;
  Double_t RelYieldsYmax;
  Double_t RelYieldsMin;

  Double_t RelYieldsRatioYmin;
  Double_t RelYieldsRatioYmax;
  Double_t RelYieldsRatioMax;

  Double_t LegendRelYieldsXmin;
  Double_t LegendRelYieldsYmin;
  Double_t LegendRelYieldsXmax;
  Double_t LegendRelYieldsYmax;

  // Set log scale to gPad?
  Bool MainPadOptLog;
  Bool MiniPadOptLog; 
  };
  */

  DrawOptions drawOptions_bb_BOTH_MULTIPLICITY_Lb; // Only Lambda_{b} for beauty (214 or 215)
  std::vector<Int_t> vAssociatesBB_Lb = {4};
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.WriteName = "beauty_Lb";
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.labelID = "(a)";
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.yieldPad = nullptr;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.yieldMiniPad = nullptr;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.relYieldPad = c00_relYields;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.relYieldMiniPad = c00mini_relYields;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.vAssociates = vAssociatesBB_Lb;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.RelYieldsYmin = 5e-1;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.RelYieldsYmax = 0.4;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.RelYieldsMin = 1e-2;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.RelYieldsRatioYmin = 2e-1;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.RelYieldsRatioYmax = 7;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.RelYieldsRatioMax = 7.49;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.LegendRelYieldsXmin = 0.63;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.LegendRelYieldsYmin = 0.88;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.LegendRelYieldsXmax = 0.9;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.LegendRelYieldsYmax = 0.68;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.LineColor = kRed;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.MainPadOptLog = false;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.MiniPadOptLog = false;
  drawOptions_bb_BOTH_MULTIPLICITY_Lb.OptError = -1;

  DrawOptions drawOptions_bb_BOTH_MULTIPLICITY_LbSb; // Lambda_{b} and Sigma_{b} for beauty (214 or 215)
  std::vector<Int_t> vAssociatesBB_LbSb = {4, 6};
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.WriteName = "beauty_LbSb";
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.labelID = "(c)";
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.yieldPad = nullptr;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.yieldMiniPad = nullptr;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.relYieldPad = c10_relYields;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.relYieldMiniPad = c10mini_relYields;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.vAssociates = vAssociatesBB_LbSb;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.RelYieldsYmin = 1e-3;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.RelYieldsYmax = 4;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.RelYieldsMin = 2e-3;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.RelYieldsRatioYmin = 0.5;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.RelYieldsRatioYmax = 190;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.RelYieldsRatioMax = 199.99;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.LegendRelYieldsXmin = 0.63;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.LegendRelYieldsYmin = 0.88;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.LegendRelYieldsXmax = 0.9;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.LegendRelYieldsYmax = 0.68;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.LineColor = kRed;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.MainPadOptLog = true;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.MiniPadOptLog = true;
  drawOptions_bb_BOTH_MULTIPLICITY_LbSb.OptError = -1;

  DrawOptions drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED; // Condensed multiplicities, other drawing options in principle irrelevant
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.WriteName = "condensed_beauty_BOTH";
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.labelID = "(e)";
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.yieldPad = nullptr;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.yieldMiniPad = c20mini_yields;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.relYieldPad = nullptr;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.relYieldMiniPad = nullptr;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.vAssociates = vAssociatesBB_Lb;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.RelYieldsYmin = 5e-1;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.RelYieldsYmax = 0.6;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.RelYieldsMin = 1e-2;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.RelYieldsRatioYmin = 2e-1;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.RelYieldsRatioYmax = 7;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.RelYieldsRatioMax = 7.49;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.LegendRelYieldsXmin = 0.63;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.LegendRelYieldsYmin = 0.88;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.LegendRelYieldsXmax = 0.9;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.LegendRelYieldsYmax = 0.68;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.LineColor = kRed;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.MainPadOptLog = false;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.MiniPadOptLog = false;
  drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED.OptError = -1;

  DrawOptions drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED; // Condensed multiplicities, other drawing options in principle irrelevant
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.WriteName = "condensed_beauty_MONASH";
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.labelID = "(c)";
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.yieldPad = c10_yields;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.yieldMiniPad = nullptr;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.relYieldPad = nullptr;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.relYieldMiniPad = nullptr;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.vAssociates = vAssociatesBB_Lb;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.RelYieldsYmin = 5e-1;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.RelYieldsYmax = 0.6;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.RelYieldsMin = 1e-2;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.RelYieldsRatioYmin = 2e-1;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.RelYieldsRatioYmax = 7;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.RelYieldsRatioMax = 7.49;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.LegendRelYieldsXmin = 0.63;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.LegendRelYieldsYmin = 0.88;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.LegendRelYieldsXmax = 0.9;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.LegendRelYieldsYmax = 0.68;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.LineColor = kRed;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.MainPadOptLog = false;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.MiniPadOptLog = false;
  drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED.OptError = 0;

  DrawOptions drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED; // Condensed multiplicities, other drawing options in principle irrelevant
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.WriteName = "condensed_beauty_JUNCTIONS";
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.labelID = "(a)";
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.yieldPad = c00_yields;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.yieldMiniPad = nullptr;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.relYieldPad = nullptr;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.relYieldMiniPad = nullptr;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.vAssociates = vAssociatesBB_Lb;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsYmin = 5e-1;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsYmax = 0.6;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsMin = 1e-2;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsRatioYmin = 2e-1;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsRatioYmax = 7;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsRatioMax = 7.49;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.LegendRelYieldsXmin = 0.63;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.LegendRelYieldsYmin = 0.88;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.LegendRelYieldsXmax = 0.9;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.LegendRelYieldsYmax = 0.68;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.LineColor = kRed;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.MainPadOptLog = false;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.MiniPadOptLog = false;
  drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED.OptError = 1;

  DrawOptions drawOptions_cc_BOTH_MULTIPLICITY_Lc; // Only Lambda_{c} for prompt charm (214prompt or 215)
  std::vector<Int_t> vAssociatesCC_Lc = {3};
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.WriteName = "charm_Lc";
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.labelID = "(b)";
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.yieldPad = nullptr;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.yieldMiniPad = nullptr;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.relYieldPad = c01_relYields;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.relYieldMiniPad = c01mini_relYields;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.vAssociates = vAssociatesCC_Lc;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.RelYieldsYmin = 5e-1; // 5e-1
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.RelYieldsYmax = 0.4; // 0.25
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.RelYieldsMin = 1e-2; // 1e-2
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.RelYieldsRatioYmin = 2e-1; // 0.5
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.RelYieldsRatioYmax = 7; // 1.5
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.RelYieldsRatioMax = 7.49; // 1.99
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.LegendRelYieldsXmin = 0.63;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.LegendRelYieldsYmin = 0.88;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.LegendRelYieldsXmax = 0.9;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.LegendRelYieldsYmax = 0.68;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.LineColor = kBlue;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.MainPadOptLog = false;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.MiniPadOptLog = false;
  drawOptions_cc_BOTH_MULTIPLICITY_Lc.OptError = -1;

  DrawOptions drawOptions_cc_BOTH_MULTIPLICITY_LcSc; // Lambda_{c} and Sigma_{c} for prompt charm (214prompt or 215)
  std::vector<Int_t> vAssociatesCC_LcSc = {3, 5};
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.WriteName = "charm_LcSc";
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.labelID = "(d)";
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.yieldPad = nullptr;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.yieldMiniPad = nullptr;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.relYieldPad = c11_relYields;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.relYieldMiniPad = c11mini_relYields;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.vAssociates = vAssociatesCC_LcSc;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.RelYieldsYmin = 1e-3; // 1e-3
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.RelYieldsYmax = 4; // 4
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.RelYieldsMin = 2e-3; // 2e-3
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.RelYieldsRatioYmin = 0.5; // 0
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.RelYieldsRatioYmax = 190; // 14
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.RelYieldsRatioMax = 199.99; // 15.99
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.LegendRelYieldsXmin = 0.63;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.LegendRelYieldsYmin = 0.88;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.LegendRelYieldsXmax = 0.9;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.LegendRelYieldsYmax = 0.68;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.LineColor = kBlue;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.MainPadOptLog = true;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.MiniPadOptLog = true;
  drawOptions_cc_BOTH_MULTIPLICITY_LcSc.OptError = -1;

  DrawOptions drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED; // Condensed yields, other drawing options in principle irrelevant
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.WriteName = "condensed_charm_BOTH";
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.labelID = "(f)";
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.yieldPad = nullptr;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.yieldMiniPad = c21mini_yields;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.relYieldPad = nullptr;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.relYieldMiniPad = nullptr;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.vAssociates = vAssociatesCC_Lc;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.RelYieldsYmin = 5e-1;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.RelYieldsYmax = 0.25;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.RelYieldsMin = 1e-2;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.RelYieldsRatioYmin = 0.5;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.RelYieldsRatioYmax = 1.5;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.RelYieldsRatioMax = 1.99;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.LegendRelYieldsXmin = 0.63;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.LegendRelYieldsYmin = 0.88;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.LegendRelYieldsXmax = 0.9;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.LegendRelYieldsYmax = 0.68;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.LineColor = kBlue;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.MainPadOptLog = false;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.MiniPadOptLog = false;
  drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED.OptError = -1;

  DrawOptions drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED; // Condensed yields, other drawing options in principle irrelevant
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.WriteName = "condensed_charm_MONASH";
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.labelID = "(d)";
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.yieldPad = c11_yields;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.yieldMiniPad = nullptr;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.relYieldPad = nullptr;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.relYieldMiniPad = nullptr;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.vAssociates = vAssociatesCC_Lc;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.RelYieldsYmin = 5e-1;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.RelYieldsYmax = 0.25;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.RelYieldsMin = 1e-2;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.RelYieldsRatioYmin = 0.5;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.RelYieldsRatioYmax = 1.5;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.RelYieldsRatioMax = 1.99;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.LegendRelYieldsXmin = 0.54;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.LegendRelYieldsYmin = 0.58;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.LegendRelYieldsXmax = 0.88;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.LegendRelYieldsYmax = 0.88;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.LineColor = kBlue;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.MainPadOptLog = false;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.MiniPadOptLog = false;
  drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED.OptError = 0;

  DrawOptions drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED; // Condensed yields, other drawing options in principle irrelevant
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.WriteName = "condensed_charm_JUNCTIONS";
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.labelID = "(b)";
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.yieldPad = c01_yields;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.yieldMiniPad = nullptr;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.relYieldPad = nullptr;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.relYieldMiniPad = nullptr;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.vAssociates = vAssociatesCC_Lc;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsYmin = 5e-1;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsYmax = 0.25;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsMin = 1e-2;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsRatioYmin = 0.5;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsRatioYmax = 1.5;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.RelYieldsRatioMax = 1.99;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.LegendRelYieldsXmin = 0.63;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.LegendRelYieldsYmin = 0.88;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.LegendRelYieldsXmax = 0.9;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.LegendRelYieldsYmax = 0.68;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.LineColor = kBlue;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.MainPadOptLog = false;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.MiniPadOptLog = false;
  drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED.OptError = 1;
  
  // Define inputs for configureInput()
  // That function then prepares the input for the main function call, harryPlotter, which plots everything
  Bool_t junctions = false;            // MONASH vs JUNCTIONS comparison
  Bool_t division = false;             // D / B comparison
  Bool_t write = false;                // Write to local (as pdf)
  Bool_t writeGlobalYields = true;    // Write global yield plot to local 
  Bool_t writeGlobalRelYields = false;  // Write global relative yield plot to local
  const char* errFileName;             // Created with sampling in yieldSampling.C macro
  const char* errTreeName;             // Created with sampling in yieldSampling.C macro

  // Select which part of the code to run
  // Details can be changed as desired below
  // If one does not care about the individual parts, but only wants the combined plots, then
  // set the values below and ignore the others
  Bool_t GLOBAL_CANVAS = true;
  Bool_t RELATIVE_CANVAS = false;
  
  Bool_t bb_MONASH_MULTIPLICITY_CONDENSED = false;
  Bool_t bb_JUNCTIONS_MULTIPLICITY_CONDENSED = false;
  Bool_t bb_BOTH_MULTIPLICITY_CONDENSED = false;
  
  Bool_t bb_BOTH_MULTIPLICITY_GENERAL_Lb = false; // Draw only Lambda_{b} in ratio plots
  Bool_t bb_BOTH_MULTIPLICITY_GENERAL_LbSb = false; // Draw Lambda_{b} and Sigma_{b} in ratio plots

  // Careful: for (215) these are also used, but they are PROMPT
  Bool_t cc_MONASH_MULTIPLICITY_CONDENSED = false;
  Bool_t cc_JUNCTIONS_MULTIPLICITY_CONDENSED = false;
  Bool_t cc_BOTH_MULTIPLICITY_CONDENSED = false;
  
  Bool_t cc_BOTH_MULTIPLICITY_GENERAL_Lc = false; // Draw only Lambda_{c} in ratio plots
  Bool_t cc_BOTH_MULTIPLICITY_GENERAL_LcSc = false; // Draw Lambda_{c} and Sigma_{c} in ratio plots

  /*
  Bool_t cc_PROMPT_BOTH_MULTIPLICITY_GENERAL = false;
  Bool_t cc_PROMPT_BOTH_MULTIPLICITY_CONDENSED = false;

  Bool_t cc_NON_PROMPT_BOTH_MULTIPLICITY_GENERAL = false;
  Bool_t cc_NON_PROMPT_BOTH_MULTIPLICITY_CONDENSED = false;
  */

  if (GLOBAL_CANVAS) {
    bb_MONASH_MULTIPLICITY_CONDENSED = true;
    bb_JUNCTIONS_MULTIPLICITY_CONDENSED = true;
    bb_BOTH_MULTIPLICITY_CONDENSED = true;
    cc_MONASH_MULTIPLICITY_CONDENSED = true;
    cc_JUNCTIONS_MULTIPLICITY_CONDENSED = true;
    cc_BOTH_MULTIPLICITY_CONDENSED = true;
  }

  if (RELATIVE_CANVAS) {
    bb_BOTH_MULTIPLICITY_GENERAL_Lb = true;
    bb_BOTH_MULTIPLICITY_GENERAL_LbSb = true;
    cc_BOTH_MULTIPLICITY_GENERAL_Lc = true;
    cc_BOTH_MULTIPLICITY_GENERAL_LcSc = true;
  }

  std::string path_bb_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_214/";
  std::string path_bb_215 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_215/";
  
  std::vector<PathAndLabels> vPathAndLabels;
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({" ", -1, -1, -1, path_bb_215});

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
  vHistNameAndLabels.push_back({"80-100 %", kBlack, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 %", kBlack, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 %", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 %", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 %", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5 %", kBlack, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"0-1 %", kBlack, 4, 3, "hDPhiM1", "hTrPtM1"});

  errFileName = "yieldErrors_bb_215_3MULT.root"; // 3MULT has only 3 condensed multiplicity bins
  errTreeName = "Error_YieldsTree_BBMULTGENERAL";

  // if (bb_MONASH_MULTIPLICITY_GENERAL) {
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of multiplicity", vHistNameAndLabels.size(), division, write, errFileName, errTreeName);
  // }

  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();

  errTreeName = "Error_YieldsTree_BBMULTCONDENSED";

  if (bb_MONASH_MULTIPLICITY_CONDENSED) {
    vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
    CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of multiplicity", 3*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName, drawOptions_bb_MONASH_MULTIPLICITY_CONDENSED);
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

  // JUNCTIONS only study
  vPathAndLabels.clear();
  vHistNameAndLabels.clear();
  vInput.clear();

  std::string path_bb_JUNCTIONS_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_JUNCTIONS_214/";
  std::string path_bb_JUNCTIONS_215 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_JUNCTIONS_215/";
  
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({" ", kRed, -1, -1, path_bb_JUNCTIONS_215});

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
  vHistNameAndLabels.push_back({"80-100 %", kBlue, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 %", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 %", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 %", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 %", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5 %", kRed, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"0-1 %", kRed, 4, 3, "hDPhiM1", "hTrPtM1"});

  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();
  errFileName = "yieldErrors_bb_215_3MULT.root";
  errTreeName = "Error_YieldsTree_BBMULTCONDENSED";

  if (bb_JUNCTIONS_MULTIPLICITY_CONDENSED) {
  vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of multiplicity", 3*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName, drawOptions_bb_JUNCTIONS_MULTIPLICITY_CONDENSED);
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

  junctions = true;
  
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({" ", kBlack, -1, -1, path_bb_215});
  vPathAndLabels.push_back({" ", kRed, -1, -1, path_bb_JUNCTIONS_215});

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
  vHistNameAndLabels.push_back({"80-100 %", kBlue, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 %", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 %", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 %", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 %", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5 %", kRed, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"0-1 %", kRed, 4, 3, "hDPhiM1", "hTrPtM1"});

  errFileName = "yieldErrors_bb_215_3MULT.root";
  errTreeName = "Error_YieldsTree_BBMULTGENERAL";
  
  if (bb_BOTH_MULTIPLICITY_GENERAL_Lb) {
  vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of multiplicity", vPathAndLabels.size()*vHistNameAndLabels.size(), junctions, division, write, errFileName, errTreeName, drawOptions_bb_BOTH_MULTIPLICITY_Lb);
  }

  if (bb_BOTH_MULTIPLICITY_GENERAL_LbSb) {
  vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of multiplicity", vPathAndLabels.size()*vHistNameAndLabels.size(), junctions, division, write, errFileName, errTreeName, drawOptions_bb_BOTH_MULTIPLICITY_LbSb);
  }
  
  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();
  errTreeName = "Error_YieldsTree_BBMULTCONDENSED";

  if (bb_BOTH_MULTIPLICITY_CONDENSED) {
  vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vInput, "integrated yields for B^{+} trigger as function of multiplicity", 3*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName, drawOptions_bb_BOTH_MULTIPLICITY_CONDENSED);
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

  // CHARM ONLY MONASH STUDY
  // 214 = INCLUSIVE (but 'slightly' wrong multiplicity definition that only includes
  // charged particles and not necessarily charged primaries)
  // 215 = PROMPT (with correct multiplicity definition)

  vPathAndLabels.clear();
  vRootFileAndLabels.clear();
  vHistNameAndLabels.clear();
  vInput.clear();

  junctions = false;
  std::string path_cc_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_214/";
  // 215 is PROMPT
  std::string path_cc_215 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_215/"; 
  
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({" ", kBlack, -1, -1, path_cc_215});

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
  vHistNameAndLabels.push_back({"80-100 %", kBlue, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 %", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 %", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 %", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 %", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5 %", kRed, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"0-1 %", kRed, 4, 3, "hDPhiM1", "hTrPtM1"});

  errFileName = "yieldErrors_cc_215_3MULT.root"; // keep in mind this is PROMPT!!!
  
  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();
  errTreeName = "Error_YieldsTree_CCMULTCONDENSED";

  if (cc_MONASH_MULTIPLICITY_CONDENSED) {
  vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vInput, "integrated yields for prompt D^{+} trigger as function of multiplicity", 3*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName, drawOptions_cc_MONASH_MULTIPLICITY_CONDENSED);
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

  // CHARM ONLY JUNCTIONS STUDY
  // 214 = INCLUSIVE (but 'slightly' wrong multiplicity definition that only includes
  // charged particles and not necessarily charged primaries)
  // 215 = PROMPT (with correct multiplicity definition)

  vPathAndLabels.clear();
  vRootFileAndLabels.clear();
  vHistNameAndLabels.clear();
  vInput.clear();

  junctions = false;
  std::string path_cc_JUNCTIONS_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_JUNCTIONS_214/";
  // 215 is PROMPT
  std::string path_cc_JUNCTIONS_215 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_JUNCTIONS_215/";
  
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({" ", kBlue, -1, -1, path_cc_JUNCTIONS_215});
  
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
  vHistNameAndLabels.push_back({"80-100 %", kBlue, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 %", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 %", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 %", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 %", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5 %", kRed, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"0-1 %", kRed, 4, 3, "hDPhiM1", "hTrPtM1"});

  errFileName = "yieldErrors_cc_215_3MULT.root"; // keep in mind this is PROMPT!!!
  
  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();
  errTreeName = "Error_YieldsTree_CCMULTCONDENSED";

  if (cc_JUNCTIONS_MULTIPLICITY_CONDENSED) {
  vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vInput, "integrated yields for prompt D^{+} trigger as function of multiplicity", 3*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName, drawOptions_cc_JUNCTIONS_MULTIPLICITY_CONDENSED);
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

  // CHARM BOTH MONASH AND JUNCTIONS STUDY
  // 214 = INCLUSIVE (but 'slightly' wrong multiplicity definition that only includes
  // charged particles and not necessarily charged primaries)
  // 215 = PROMPT (with correct multiplicity definition)

  vPathAndLabels.clear();
  vRootFileAndLabels.clear();
  vHistNameAndLabels.clear();
  vInput.clear();

  junctions = true;
  
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({" ", kBlack, -1, -1, path_cc_215});
  vPathAndLabels.push_back({" ", kBlue, -1, -1, path_cc_JUNCTIONS_215});

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
  vHistNameAndLabels.push_back({"80-100 %", kBlue, 1, 2, "hDPhiM80_100", "hTrPtM80_100"});
  vHistNameAndLabels.push_back({"60-80 %", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  vHistNameAndLabels.push_back({"40-60 %", kBlack, 2, 3, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 %", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  vHistNameAndLabels.push_back({"5-20 %", kBlack, 3, 3, "hDPhiM5_20", "hTrPtM5_20"});
  vHistNameAndLabels.push_back({"1-5 %", kRed, 3, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"0-1 %", kRed, 4, 3, "hDPhiM1", "hTrPtM1"});

  errFileName = "yieldErrors_cc_215_3MULT.root"; // keep in mind this is PROMPT!!!
  errTreeName = "Error_YieldsTree_CCMULTGENERAL";
  
  if (cc_BOTH_MULTIPLICITY_GENERAL_Lc) {
  vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vInput, "integrated yields for prompt D^{+} trigger as function of multiplicity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName, drawOptions_cc_BOTH_MULTIPLICITY_Lc);
  }

  if (cc_BOTH_MULTIPLICITY_GENERAL_LcSc) {
  vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vInput, "integrated yields for prompt D^{+} trigger as function of multiplicity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName, drawOptions_cc_BOTH_MULTIPLICITY_LcSc);
  }
  
  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();
  errTreeName = "Error_YieldsTree_CCMULTCONDENSED";

  if (cc_BOTH_MULTIPLICITY_CONDENSED) {
  vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vInput, "integrated yields for prompt D^{+} trigger as function of multiplicity", 3*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName, drawOptions_cc_BOTH_MULTIPLICITY_CONDENSED);
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

  /*
  // PROMPT CHARM JUNCTIONS STUDY

  vPathAndLabels.clear();
  vRootFileAndLabels.clear();
  vHistNameAndLabels.clear();
  vInput.clear();

  junctions = true;
  std::string path_cc_prompt_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_prompt_214/";
  std::string path_cc_prompt_JUNCTIONS_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_prompt_JUNCTIONS_214/";
  
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

  errFileName = "yieldErrors_cc_214.root";
  errTreeName = "Error_YieldsTree_CCPROMPTMULTGENERAL";
  
  if (cc_PROMPT_BOTH_MULTIPLICITY_GENERAL) {
  vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vYieldsPad, vInput, "integrated yields for prompt D^{+} trigger as function of multiplicity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName);
  }
  
  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();
  errTreeName = "Error_YieldsTree_CCPROMPTMULTCONDENSED";

  if (cc_PROMPT_BOTH_MULTIPLICITY_CONDENSED) {
  vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vYieldsPad, vInput, "integrated yields for prompt D^{+} trigger as function of multiplicity", 3*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName);
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
  std::string path_cc_non_prompt_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_non_prompt_214/";
  std::string path_cc_non_prompt_JUNCTIONS_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_non_prompt_JUNCTIONS_214/";
  
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
  // CalculateOS_minus_SS(vInput, "integrated yields for non-prompt D^{+} trigger as function of pT", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);
  
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

  errFileName = "yieldErrors_cc_214.root";
  errTreeName = "Error_YieldsTree_CCNONPROMPTMULTGENERAL";
  
  if (cc_NON_PROMPT_BOTH_MULTIPLICITY_GENERAL) {
  vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vYieldsPad, vInput, "integrated yields for non-prompt D^{+} trigger as function of multiplicity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName);
  }
  
  // Multiplicity study: combined bins (c.f. configureInputMult)
  vInput.clear();
  errTreeName = "Error_YieldsTree_CCNONPROMPTMULTCONDENSED";

  if (cc_NON_PROMPT_BOTH_MULTIPLICITY_CONDENSED) {
  vInput = configureInputMult(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  CalculateOS_minus_SS(vYieldsPad, vInput, "integrated yields for non-prompt D^{+} trigger as function of multiplicity", 3*vPathAndLabels.size(), junctions, division, write, errFileName, errTreeName);
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
  // CalculateOS_minus_SS(vInput, "integrated yields for non-prompt D^{+} trigger as function of rapidity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);

  // Pseudorapidity study
  vHistNameAndLabels.clear();
  vInput.clear();
  
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiEtaCC", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 3, 2, "hDPhiEtaCF", "hTrPtEtaC"});
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 4, 2, "hDPhiEtaFC", "hTrPtEtaF"}); 
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 2, 1, "hDPhiEtaFF", "hTrPtEtaF"});
  
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // CalculateOS_minus_SS(vInput, "integrated yields for non-prompt D^{+} trigger as function of pseudorapidity", vHistNameAndLabels.size()*vPathAndLabels.size(), junctions, division, write);

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
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#Sigma_{b}^{+}", "#bar#Sigma_{b}^{+}", "BplusSigmabplus.root", "BplusSigmabplusbar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#Sigma_{b}^{0}", "#bar#Sigma_{b}^{0}", "BplusSigmabzero.root", "BplusSigmabzerobar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "D^{+}", "#Sigma_{b}^{-}", "#bar#Sigma_{b}^{-}", "BplusSigmabminus.root", "BplusSigmabminusbar.root", 1e-8, 1e-2});
  

  // *** LegendTitle, Color, LineStyle, LineWidth, TriggerName, AssociateNameOS, AssociateNameSS, OSRootFile, SSRootFile, DrawYmin, DrawYmax ***
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "B^{-}", "B^{+}", "BplusBminus.root", "BplusBplus.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#barB^{0}", "B^{0}", "BplusBzerobar.root", "BplusBzero.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#barB_{s}^{0}", "B_{s}^{0}", "BplusBszerobar.root", "BplusBszero.root", 1e-8, 1e-2});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Lambda_{b}^{0}", "#bar#Lambda_{b}^{0}", "BplusLb.root", "BplusLbbar.root", 1e-8, 1e-2});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{+}", "#bar#Sigma_{b}^{+}", "BplusSigmabplus.root", "BplusSigmabplusbar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{0}", "#bar#Sigma_{b}^{0}", "BplusSigmabzero.root", "BplusSigmabzerobar.root", 1e-6, 1e0});
  vRootFileAndLabels.push_back({"-1", kBlack, 1, 1, "B^{+}", "#Sigma_{b}^{-}", "#bar#Sigma_{b}^{-}", "BplusSigmabminus.root", "BplusSigmabminusbar.root", 1e-8, 1e-2});
  
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
  */

  // Write global canvasses to local
  if (writeGlobalYields) {
    c2x3_yields->SaveAs("Plots/globalCanvasYieldsPDF.pdf");
    c2x3_yields->SaveAs("Plots/globalCanvasYieldsPNG.png");
    c2x3_yields->SaveAs("Plots/globalCanvasYieldsMACRO.C");
  }
  if (writeGlobalRelYields) {
    c2x2_relYields->SaveAs("Plots/globalCanvasRelativeYieldsPDF.pdf");
    c2x2_relYields->SaveAs("Plots/globalCanvasRelativeYieldsPNG.png");
    c2x2_relYields->SaveAs("Plots/globalCanvasRelativeYieldsMACRO.C");
  }
  
  return 0;
  
}
