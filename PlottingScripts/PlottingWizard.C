// PlottingWizard.C
// Harry Plotter

void normalise(TH1D* hist, TH1D* trig, Double_t xmin, Double_t xmax) {
	Int_t bin_start = trig->FindBin(xmin);
	Int_t bin_finish = trig->FindBin(xmax);
	Double_t integral = trig->Integral(bin_start, bin_finish);
	hist->Scale(1./integral);
}

bool valid(Int_t setting) {
  if (setting == -1) { return false; }
  else { return true; }
}

void setCanvasMargins(TCanvas *canvas, double_t LeftMargin, double_t RightMargin, double_t TopMargin, double_t BottomMargin) {
  canvas->SetLeftMargin(LeftMargin);
  canvas->SetRightMargin(RightMargin);
  canvas->SetTopMargin(TopMargin);
  canvas->SetBottomMargin(BottomMargin);
}

// Only used for data management course poster
void SetAxisLabelsInDegrees(TAxis* axis) {
  int num_bins = axis->GetNbins();
  for (int i = 1; i <= num_bins; ++i) {
    double old_value = axis->GetBinLowEdge(i);
    double new_value = old_value * 180.0 / TMath::Pi();
    if ((int)new_value == -89 || (int)new_value % 90 == 0 || (int)new_value == 89 || (int)new_value == 179) {
      axis->SetBinLabel(i, Form("%.0f", new_value));
    } else {
      axis->SetBinLabel(i, "");
    }
    if ((int)new_value == 266) { new_value = 270; axis->SetBinLabel(i, Form("%.0f", new_value)); } 
  }
  axis->SetTitle("angle difference (degrees)");
  // Set tick marks every 90 degrees
  // axis->SetTickLength(0.03); // Set the length of tick marks
  axis->SetNdivisions(-504); // -404 = 4 ticks between each label
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
  const char* RootFile;
};

 struct HistNameAndLabels : public BaseLabels {
   const char* HistName;
   const char* TrPtName;
};

struct HistAndLabels : public BaseLabels {
  TH1D* Hist;
};

std::vector<HistAndLabels> configureInput(std::vector<PathAndLabels>     vPathAndLabels,
					  std::vector<RootFileAndLabels> vRootFileAndLabels,
					  std::vector<HistNameAndLabels> vHistNameAndLabels) {
  
  std::vector<HistAndLabels> vHistAndLabels;
  // *** HistLegendTitle, Color, LineStyle, LineWidth, Hist ***
  // To be filled in for loops below
  
  for (int i = 0; i < vPathAndLabels.size(); i++) {

    PathAndLabels pathEntry = vPathAndLabels[i];

    for (int j = 0; j < vRootFileAndLabels.size(); j++) {

      RootFileAndLabels rootEntry = vRootFileAndLabels[j];
      TFile* tree = new TFile((pathEntry.Path + rootEntry.RootFile).c_str());

      for (int k = 0; k < vHistNameAndLabels.size(); k++) {

	HistNameAndLabels histEntry = vHistNameAndLabels[k];

	std::cout << histEntry.LegendTitle << std::endl;

	// *** ------fill vector with histograms -------- ***

	TH1D* hDPhi = (TH1D*)tree->Get(histEntry.HistName);
	TH1D* hTrPt = (TH1D*)tree->Get(histEntry.TrPtName);
	normalise(hDPhi, hTrPt, -1.57, 4.71);
	vHistAndLabels.push_back({
	    histEntry.LegendTitle, histEntry.Color, histEntry.LineStyle, histEntry.LineWidth,
	    hDPhi
	  });
	
      } // k
	     
    } // j
    
  } // i

  return vHistAndLabels;
  
}

void harryPlotter(std::vector<HistAndLabels> vInput, const char* plotTitle, Double_t DrawYmin, Double_t DrawYmax) {

  TCanvas* c = new TCanvas(Form("canvas_%s", plotTitle), Form("canvas_%s", plotTitle), 800, 600);
  setCanvasMargins(c, 0.15, 0.1, 0.1, 0.1);

  TLegend* l = new TLegend(0.2, 0.8, 0.4, 0.6);
  
  TH1D* hTEMPLATE = new TH1D("hTEMPLATE", Form("%s", plotTitle), 100, -1.57, 4.71);
  hTEMPLATE->SetStats(0);
  hTEMPLATE->SetTitle(plotTitle);
  // hTEMPLATE->GetYaxis()->SetTitle("#frac{1}{N_{trigger}} #frac{dN}{d#Delta#phi}");
  hTEMPLATE->GetYaxis()->SetTitle("B^{+}B^{-} pairs / total number of B^{+} mesons");
  // hTEMPLATE->GetXaxis()->SetTitle("#Delta#phi (rad)");
  hTEMPLATE->GetYaxis()->SetRangeUser(DrawYmin, DrawYmax);
  hTEMPLATE->Draw("hist E");

  // This part is only necessary for the data management poster
  TAxis *xaxis = hTEMPLATE->GetXaxis();
  SetAxisLabelsInDegrees(xaxis);
  hTEMPLATE->GetXaxis()->SetTitleOffset(1.4);
  c->Update();
  c->Draw();
  
  for (Int_t i = 0; i < vInput.size(); i++) {

    HistAndLabels inputEntry = vInput[i];

    inputEntry.Hist->SetLineColor(inputEntry.Color);
    inputEntry.Hist->SetLineStyle(inputEntry.LineStyle);
    inputEntry.Hist->SetLineWidth(inputEntry.LineWidth);
    inputEntry.Hist->Draw("same hist E");
    l->AddEntry(inputEntry.Hist, inputEntry.LegendTitle);
      
  } // for

  // l->Draw();
  
}

int PlottingWizard() {

  // Define inputs for configureInput()
  // That function then prepares the input for the main function call, harryPlotter, which plots everything

  std::string path_214 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_214/";
  // std::string path_221 = "/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_bb_221/";
  
  std::vector<PathAndLabels> vPathAndLabels;
  // *** LegendTitle, Color, LineStyle, LineWidth, PathName ***
  vPathAndLabels.push_back({"ROOT_214", -1, -1, -1, path_214});
  // vPathAndLabels.push_back({path_221, "ROOT_221", -1, -1, -1});

  std::vector<RootFileAndLabels> vRootFileAndLabels;
  // *** LegendTitle, Color, LineStyle, LineWidth, RootFile ***
  vRootFileAndLabels.push_back({"B^{+}B^{-}", -1, -1, -1, "BplusBminus.root"});
  // vRootFileAndLabels.push_back({"B^{+}#Lambda_{b}", -1, -1, -1, "BplusLb.root"});

  std::vector<HistNameAndLabels> vHistNameAndLabels;
  // *** HistLegendTitle, Color, LineStyle, LineWidth, HistName, TrPtName ***
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiYCC", "hTrPtYCC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 2, 1, "hDPhiYCF", "hTrPtYCC"});
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 2, 1, "hDPhiYFC", "hTrPtYFF"});
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 1, 1, "hDPhiYFF", "hTrPtYFF"});

  std::vector<HistAndLabels> vInput;
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // harryPlotter(vInput, "rapidity B^{+}B^{-} angular correlations (yCrit = 2)", 1e-3, 6.5e-2);

  vHistNameAndLabels.clear();
  vHistNameAndLabels.push_back({"trigger central, assoc central", kBlue, 1, 1, "hDPhiEtaCC", "hTrPtEtaCC"});
  vHistNameAndLabels.push_back({"trigger central, assoc forward", kBlue, 2, 1, "hDPhiEtaCF", "hTrPtEtaCC"});
  vHistNameAndLabels.push_back({"trigger forward, assoc central", kRed, 2, 1, "hDPhiEtaFC", "hTrPtEtaFF"});
  vHistNameAndLabels.push_back({"trigger forward, assoc forward", kRed, 1, 1, "hDPhiEtaFF", "hTrPtEtaFF"});

  vInput.clear();
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // harryPlotter(vInput, "pseudorapidity B^{+}B^{-} angular correlations (etaCrit = 2)", 1e-3, 5e-2);

  vHistNameAndLabels.clear();
  vHistNameAndLabels.push_back({"80-100 % multiplicity bin", kBlue, 2, 2, "hDPhiM80_100", "hTrPtM80_100"});
  // vHistNameAndLabels.push_back({"60-80 % multiplicity bin", kBlue, 1, 1, "hDPhiM60_80", "hTrPtM60_80"});
  // vHistNameAndLabels.push_back({"40-60 % multiplicity bin", kBlack, 3, 2, "hDPhiM40_60", "hTrPtM40_60"});
  vHistNameAndLabels.push_back({"20-40 % multiplicity bin", kBlack, 2, 2, "hDPhiM20_40", "hTrPtM20_40"});
  // vHistNameAndLabels.push_back({"5-20 % multiplicity bin", kBlack, 1, 1, "hDPhiM5_20", "hTrPtM5_20"});
  // vHistNameAndLabels.push_back({"1-5% multiplicity bin", kRed, 2, 2, "hDPhiM1_5", "hTrPtM1_5"});
  vHistNameAndLabels.push_back({"top 1% multiplicity bin", kRed, 1, 1, "hDPhiM1", "hTrPtM1"});

  vInput.clear();
  // vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  // harryPlotter(vInput, "multiplicity B^{+}B^{-} angular correlations", 1e-3, 0.7e-1);

  vInput.clear();
  vHistNameAndLabels.clear();
  vHistNameAndLabels.push_back({" ", kBlack, 1, 1, "hDPhi", "hTrPt"});

  vInput = configureInput(vPathAndLabels, vRootFileAndLabels, vHistNameAndLabels);
  harryPlotter(vInput, "Production origin of B^{+}B^{-} particle pairs", 1e-4, 0.2e-1);
  
  return 0;

}
