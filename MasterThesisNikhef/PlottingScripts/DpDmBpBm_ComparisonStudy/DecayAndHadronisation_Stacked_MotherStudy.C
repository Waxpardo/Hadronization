// DecayAndHadronisation_Stacked_MotherStudy.C
// This macro visualises the origin of the trigger and associate particles with respect to the
// angular correlations that are found, i.e. it draws plots using the 2-dimensional histograms
// containing both the azimuthal angular correlations between the trigger and associate and the PDG
// ID of the mother of either the trigger or associate, as indicated in the histogram names.
// Several plots are produced, some of which are 'relative abundance' showing the distribution of
// mothers for each angular correlation bin, while others are 'stacked' or 'raw' and show how each
// angular correlation bin is exactly made up of which mothers (including normalisation).
// The histograms and PDG IDs are set up for D+D- studies, as in the other plotting scripts.

// The script is not optimised nor perfected, but it should be clear in which ways the code can be
// improved (i.e. seperate function for histogram filling, no distinction in trigger/associate,
// canvas titles).

// Short summary of code structure:
//
// The script takes histogram names as arguments and then takes them from a ROOT file, as defined
// in the 6th line of the readTree function.
// A method is set up which allows to check if all particles are identified by using their PDG IDs.
// The main bin loop is started over the 2D histogram and the mother PDG IDs are obtained for every
// bin and subsequently checked and added to the correct particle histogram [be careful when
// modifying this part of the code, as e.g. introducing a new particle means a new histogram needs
// to be defined, the PDG ID needs to be added to the known list, the PDG ID check needs to be
// added, the total counter needs to be incremented by one and in the final consistency checks,
// after printing the bin information, the nMissing counter will also need to be increased by one.
// There are some consistency checks which will fail when one forgets any of these steps.].
// If `print` is set to `true`, then bin information and consistency checks will be printed.
// Depending on if `trigger` or `associate` has been set to `true` the relevant plotting part of
// the code will be executed, starting with relative abundance plots and ending with raw stacked
// plots.
// If `write` is set to `true`, then some of the canvases will be saved as PDFs.

// Comments on other mother study macros:
//
// The other three mother study macros are very similar in structure to this code, hence this
// file will be refered to as the main documentation. There are some differences however, and they
// will be highlighted here.
// 
// DecayAndHadronisation_Stacked_MotherStudy.C -> both prompt and non-prompt production is analysed
// with Delta phi of the trigger and associate particles for low-low and high-high pT regions,
// linear scale is used, stacked plots are shown.
// DecayAndHadronisation_Markers_MotherStudy.C -> same as DecayAndHadronisation_Stacked_MotherStudy.C,
// but with log scale marker plots. The log marker plots allow to visualise even the smallest of
// contributions, while the stacked plots are better at showing the main components of the angular
// correlations.
//
// The non-prompt case is zoomed in on and a study is done on the Delta phi of the mother(s) of the
// trigger and associate, which can be the same mother or a different mother, being the main point
// of this study. There is no classification based on pT regions, as it is not expected to change
// much, but can be added if desired.
// SameDiffMother_Stacked_MotherStudy.C -> for linear stacked plots
// SameDiffMother_Markers_MotherStudy.C -> for log marker plots

// Good luck!

// The histograms are normalised by the number of triggers, which is obtained by integrating the trigger spectrum
void normalise(TH1* hist, TH1* trig, Double_t xmin, Double_t xmax) {
    Int_t bin_start = trig->FindBin(xmin);
    Int_t bin_finish = trig->FindBin(xmax);
    Double_t integral = trig->Integral(bin_start, bin_finish);
    hist->Scale(1./integral);
}

// Function that checks if an element is already in an array
// This is used to see if the code is not missing a particle mother in the event by checking if the current PDG ID is already in the list of total known PDG IDs
bool isElementInArray(const int arr[], int size, int target) {
    for (int i = 0; i < size; ++i) {
        if (arr[i] == target) {
            return true;
        }
    }
    return false;
}

// Function that prints a given vector of ints
// Used to display known and unknown PDG IDs in events
void printVector(const std::vector<int>& vec) {
    for (const int& element : vec) {
        std::cout << element << " ";
    }
    std::cout << std::endl;
}

// The canvas margins are standardised in this way for every function call
void setCanvasMargins(TCanvas *canvas, double_t LeftMargin, double_t RightMargin, double_t TopMargin, double_t BottomMargin) {
  canvas->SetLeftMargin(LeftMargin);
  canvas->SetRightMargin(RightMargin);
  canvas->SetTopMargin(TopMargin);
  canvas->SetBottomMargin(BottomMargin);
}

// ReadTree draws the plots showing Delta phi and particle mother relations
// The function takes several arguments, most of which are self-explanatory settings:
// > trigger or associate should `true` to indicate which part of the ptTrRegionVector should be used, as it contains both trigger and associate ROOT files. This can also be implemented in a saner way, as the plotting part now essentially appears twice in the script, but it should at least be clear to follow.
// > print will show all details regarding events analysed
// > write will save several canvases as PDF file
// The axis range settings are straight-forward in what they do. They are initialised to 0 if one does not want to set specific ranges.
// The first arguments are less self-explanatory. ptRegion is a const char* that indicates which trigger-associate pT range should be taken for the DPhi histogram, while the ptTrRegionVector contains the histogram names that should be used. This vector contains both the trigger and associate histogram names.
void readTree(const char* ptRegion, vector<const char*> ptTrRegionVector,
	      bool trigger,
	      bool associate,
	      bool print,
	      bool write = false,
	      Double_t legendXmin = 0, Double_t legendYmin = 0, Double_t legendXmax = 0, Double_t legendYmax = 0,
	      Double_t stackedYmin = 0, Double_t stackedYmax = 0
	      ) {

  TFile* rootFile2D = new TFile("../RootFiles/DplusDminus_60_2D.root"); 
  const char* ptTrRegion;
  if (trigger) { ptTrRegion = ptTrRegionVector[0]; }
  if (associate) { ptTrRegion = ptTrRegionVector[1]; }
  TH2* hDPhiMother = (TH2*)rootFile2D->Get(ptTrRegion);
  TH1D* hPt = (TH1D*)rootFile2D->Get("hTrPt");
  TH1D* hDPhi = (TH1D*)rootFile2D->Get(ptRegion); 

  // Integrate from -pi/2 to +3pi/2
  normalise(hDPhiMother, hPt, -1.57, 4.71);
  normalise(hDPhi, hPt, -1.57, 4.71);
  
  // Set up and define histograms for the particle abundances that will be plotted
  // Both 'raw' (Raw) particle counts per bin as well as relative abundances per bin will be used (Rel)
  // Quarks
  TH1D* hUQuarkRaw = (TH1D*)hDPhi->Clone(); TH1D* hUQuarkRel = (TH1D*)hDPhi->Clone(); // c-quarks
  hUQuarkRaw->SetName("hUQuarkRaw"); hUQuarkRaw->SetTitle("u-quarks");
  hUQuarkRel->SetName("hUQuarkRel"); hUQuarkRel->SetTitle("u-quarks");
  TH1D* hDQuarkRaw = (TH1D*)hDPhi->Clone(); TH1D* hDQuarkRel = (TH1D*)hDPhi->Clone(); // c-quarks
  hDQuarkRaw->SetName("hDQuarkRaw"); hDQuarkRaw->SetTitle("d-quarks");
  hDQuarkRel->SetName("hDQuarkRel"); hDQuarkRel->SetTitle("d-quarks");
  TH1D* hSQuarkRaw = (TH1D*)hDPhi->Clone(); TH1D* hSQuarkRel = (TH1D*)hDPhi->Clone(); // c-quarks
  hSQuarkRaw->SetName("hSQuarkRaw"); hSQuarkRaw->SetTitle("s-quarks");
  hSQuarkRel->SetName("hSQuarkRel"); hSQuarkRel->SetTitle("s-quarks");
  TH1D* hCQuarkRaw = (TH1D*)hDPhi->Clone(); TH1D* hCQuarkRel = (TH1D*)hDPhi->Clone(); // c-quarks
  hCQuarkRaw->SetName("hCQuarkRaw"); hCQuarkRaw->SetTitle("c-quarks");
  hCQuarkRel->SetName("hCQuarkRel"); hCQuarkRel->SetTitle("c-quarks");
  TH1D* hBQuarkRaw = (TH1D*)hDPhi->Clone(); TH1D* hBQuarkRel = (TH1D*)hDPhi->Clone(); // c-quarks
  hBQuarkRaw->SetName("hBQuarkRaw"); hBQuarkRaw->SetTitle("b-quarks");
  hBQuarkRel->SetName("hBQuarkRel"); hBQuarkRel->SetTitle("b-quarks");
  TH1D* hHadronisationRaw = (TH1D*)hDPhi->Clone(); TH1D* hHadronisationRel = (TH1D*)hDPhi->Clone(); // other
  hHadronisationRaw->SetName("hHadronisationRaw"); hHadronisationRaw->SetTitle("hadronisation");
  hHadronisationRel->SetName("hHadronisationRel"); hHadronisationRel->SetTitle("hadronisation");
  
  // Diquarks
  TH1D* hDiQuarksRaw = (TH1D*)hDPhi->Clone(); TH1D* hDiQuarksRel = (TH1D*)hDPhi->Clone();
  hDiQuarksRaw->SetName("hDiQuarksRaw"); hDiQuarksRaw->SetTitle("di-quarks");
  hDiQuarksRel->SetName("hDiQuarksRel"); hDiQuarksRel->SetTitle("di-quarks");
  
  // Gluons
  TH1D* hGluonsRaw = (TH1D*)hDPhi->Clone(); TH1D* hGluonsRel = (TH1D*)hDPhi->Clone();
  hGluonsRaw->SetName("hGluonsRaw"); hGluonsRaw->SetTitle("gluons");
  hGluonsRel->SetName("hGluonsRel"); hGluonsRel->SetTitle("gluons");

  // D-mesons
  TH1D* hDMesonsRaw = (TH1D*)hDPhi->Clone(); TH1D* hDMesonsRel = (TH1D*)hDPhi->Clone();
  hDMesonsRaw->SetName("hDMesonsRaw"); hDMesonsRaw->SetTitle("excited d-mesons");
  hDMesonsRel->SetName("hDMesonsRel"); hDMesonsRel->SetTitle("excited d-mesons");
  TH1D* hADMesonsRaw = (TH1D*)hDPhi->Clone(); TH1D* hADMesonsRel = (TH1D*)hDPhi->Clone();
  hADMesonsRaw->SetName("hADMesonsRaw"); hADMesonsRaw->SetTitle("excited anti-d-mesons");
  hADMesonsRel->SetName("hADMesonsRel"); hADMesonsRel->SetTitle("excited anti-d-mesons");

  // B-mesons
  // *** Collected ***
  TH1D* hBMesonsChargedRaw = (TH1D*)hDPhi->Clone(); TH1D* hBMesonsChargedRel = (TH1D*)hDPhi->Clone(); // charged
  hBMesonsChargedRaw->SetName("hBMesonsChargedRaw"); hBMesonsChargedRaw->SetTitle("b-mesons (charged)");
  hBMesonsChargedRel->SetName("hBMesonsChargedRel"); hBMesonsChargedRel->SetTitle("b-mesons (charged)");
  TH1D* hBMesonsNeutralRaw = (TH1D*)hDPhi->Clone(); TH1D* hBMesonsNeutralRel = (TH1D*)hDPhi->Clone(); // neutral
  hBMesonsNeutralRaw->SetName("hBMesonsNeutralRaw"); hBMesonsNeutralRaw->SetTitle("b-mesons (neutral)");
  hBMesonsNeutralRel->SetName("hBMesonsNeutralRel"); hBMesonsNeutralRel->SetTitle("b-mesons (neutral)");

  // *** Divided ***
  TH1D* hBpRaw = (TH1D*)hDPhi->Clone(); TH1D* hBpRel = (TH1D*)hDPhi->Clone(); // B+
  hBpRaw->SetName("hBpRaw"); hBpRaw->SetTitle("B^{+}");
  hBpRel->SetName("hBpRel"); hBpRel->SetTitle("B^{+}");
  TH1D* hBmRaw = (TH1D*)hDPhi->Clone(); TH1D* hBmRel = (TH1D*)hDPhi->Clone(); // B-
  hBmRaw->SetName("hBmRaw"); hBmRaw->SetTitle("B^{-}");
  hBmRel->SetName("hBmRel"); hBmRel->SetTitle("B^{-}");
  TH1D* hB0Raw = (TH1D*)hDPhi->Clone(); TH1D* hB0Rel = (TH1D*)hDPhi->Clone(); // B0
  hB0Raw->SetName("hB0Raw"); hB0Raw->SetTitle("B^{0}");
  hB0Rel->SetName("hB0Rel"); hB0Rel->SetTitle("B^{0}");
  TH1D* hAB0Raw = (TH1D*)hDPhi->Clone(); TH1D* hAB0Rel = (TH1D*)hDPhi->Clone(); // AB0
  hAB0Raw->SetName("hAB0Raw"); hAB0Raw->SetTitle("anti-B^{0}");
  hAB0Rel->SetName("hAB0Rel"); hAB0Rel->SetTitle("anti-B^{0}");
  TH1D* hBs0Raw = (TH1D*)hDPhi->Clone(); TH1D* hBs0Rel = (TH1D*)hDPhi->Clone(); // Bs0
  hBs0Raw->SetName("hBs0Raw"); hBs0Raw->SetTitle("B_{s}^{0}");
  hBs0Rel->SetName("hBs0Rel"); hBs0Rel->SetTitle("B_{s}^{0}");
  TH1D* hABs0Raw = (TH1D*)hDPhi->Clone(); TH1D* hABs0Rel = (TH1D*)hDPhi->Clone(); // ABs0
  hABs0Raw->SetName("hABs0Raw"); hABs0Raw->SetTitle("anti-B_{s}^{0}");
  hABs0Rel->SetName("hABs0Rel"); hABs0Rel->SetTitle("anti-B_{s}^{0}");
  
  // B-baryons
  TH1D* hBBaryonsRaw = (TH1D*)hDPhi->Clone(); TH1D* hBBaryonsRel = (TH1D*)hDPhi->Clone();
  hBBaryonsRaw->SetName("hBBaryonsRaw"); hBBaryonsRaw->SetTitle("b-baryons");
  hBBaryonsRel->SetName("hBBaryonsRel"); hBBaryonsRel->SetTitle("b-baryons");
  
  // This part is for debugging of the IDs
  Int_t nMissing{0}; Int_t nMiss{0};
  Int_t KnownIds[] = {1, 2, 3, 4, 5,
    1103, 2101, 2103, 2203, 3101, 3103, 3201, 3203, 3303, 4103, 4203, 4303,
    21,
    413, 415, 425, 435,
    -413, -415, -425, -435,
    511, -511, 513, -513, 521, -521, 523, -523, 531, -531, 533, -533, 541, -541,
    5122, -5122, 5112, -5112, 5222, -5222, 5212, -5212, 5132, -5132, 5232, -5232, 5332, -5332};
  vector<Int_t> UnidentifiedIDs;

  // Start main loops over DPhi and MotherID bins
  int nBinsDPhi = hDPhiMother->GetXaxis()->GetNbins();
  // int nBinsDPhi = 30;
  int nBinsMotherID = hDPhiMother->GetYaxis()->GetNbins();
  // int nBinsMotherID = 10;
  
  for (int i = 0; i <= nBinsDPhi; i++) {

    Double_t nTot = 0;
    
    // Quark counters
    Double_t nd{0}; Double_t nu{0}; Double_t ns{0}; Double_t nc{0}; Double_t nb{0};
    
    // Diquark counters
    Double_t ndd1{0}; Double_t nud0{0}; Double_t nud1{0}; Double_t nuu1{0};
    Double_t nsd0{0}; Double_t nsd1{0}; Double_t nsu0{0}; Double_t nsu1{0};
    Double_t nss1{0};
    Double_t ncd1{0}; Double_t ncu1{0}; Double_t ncs1{0};
    
    // Gluons counter
    Double_t nGluon{0};
    
    // D-meson counters
    Double_t nDpstar2010{0}; Double_t nD2pstar2460{0}; Double_t nD20star2460{0};
    Double_t nDps2star2573{0};
    Double_t nADpstar2010{0}; Double_t nAD2pstar2460{0}; Double_t nAD20star2460{0};
    Double_t nADps2star2573{0};
    
    // B-meson counters
    Double_t nBp{0}; Double_t nBm{0}; Double_t nBpstar{0}; Double_t nBmstar{0};
    Double_t nAB0{0}; Double_t nB0{0}; Double_t nB0star{0}; Double_t nAB0star{0};
    Double_t nBs0{0}; Double_t nABs0{0}; Double_t nABs0star{0}; Double_t nBs0star{0};
    Double_t nBcp{0}; Double_t nBcm{0};
    
    // B-baryon counters
    Double_t nLb{0}; Double_t nALb{0};
    Double_t nSigmabm{0}; Double_t nASigmabm{0}; Double_t nSigmabp{0}; Double_t nASigmabp{0}; Double_t nSigmab0{0}; Double_t nASigmab0{0};
    Double_t nXibm{0}; Double_t nAXibm{0}; Double_t nXib0{0}; Double_t nAXib0{0};
    Double_t nOmegabm{0}; Double_t nAOmegabm{0};
    
    for (int j = 1; j <= nBinsMotherID; j++) {
      
      double binCount = hDPhiMother->GetBinContent(i, j);
      if (binCount != 0) {

	nTot += binCount;
	
	double phiMin = hDPhiMother->GetXaxis()->GetBinLowEdge(i);
	double phiMax = hDPhiMother->GetXaxis()->GetBinUpEdge(i);
	if (print) {
	  std::cout << "DPhi bin number: " << i << " DPhi_min = " << phiMin
		    << ", DPhi_max = " << phiMax << std::endl;
	  std::cout << "Bin (" << i << ", " << j << ") has content: " << binCount << std::endl; }
	double ID = hDPhiMother->GetYaxis()->GetBinCenter(j);
	if (print) {
	  std::cout << "Mother ID bin number: " << j << " Mother ID: " << ID << std::endl; }
	
	// Incrementing counters when PDG ID is found
	// Be careful to increment with the count of the bin and not just by one
	if (ID == 1) { nu += binCount; } // up-quark
	if (ID == 2) { nd += binCount; } // down-quark
	if (ID == 3) { ns += binCount; } // strange-quark
	if (ID == 4) { nc += binCount; } // charm-quark
	if (ID == 5) { nb += binCount; } // beauty-quark

	// Gluons
	if (ID == 21) { nGluon += binCount; } // gluon
	
	// Diquarks
	if (ID == 1103) { ndd1 += binCount; } // (dd)1
	if (ID == 2101) { nud0 += binCount; } // (ud)0
	if (ID == 2103) { nud1 += binCount; } // (ud)1
	if (ID == 2203) { nuu1 += binCount; } // (uu)1
	if (ID == 3101) { nsd0 += binCount; } // (sd)0
	if (ID == 3103) { nsd1 += binCount; } // (sd)1
	if (ID == 3201) { nsu0 += binCount; } // (su)0
	if (ID == 3303) { nss1 += binCount; } // (ss)1
	if (ID == 3203) { nsu1 += binCount; } // (su)1
	if (ID == 4103) { ncd1 += binCount; } // (cd)1
	if (ID == 4203) { ncu1 += binCount; } // (cu)1
	if (ID == 4303) { ncs1 += binCount; } // (cs)1
	
	// D-mesons
	if (ID == 413) { nDpstar2010 += binCount; } // D*+(2010)
	if (ID == 415) { nD2pstar2460 += binCount; } // D2*+(2460)
	if (ID == 425) { nD20star2460 += binCount; } // D2*0(2460)
	if (ID == 435) { nDps2star2573 += binCount; } // D*+(2573)
	if (ID == -413) { nADpstar2010 += binCount; } // anti-D*+(2010)
	if (ID == -415) { nAD2pstar2460 += binCount; } // anti-D2*+(2460)
	if (ID == -425) { nAD20star2460 += binCount; } // anti-D2*0(2460)
	if (ID == -435) { nADps2star2573 += binCount; } // anti-D*+(2573)

	// B-mesons
	if (ID == 521) { nBp += binCount; } // B+
	if (ID == -521) { nBm += binCount; } // B-
	if (ID == 523) { nBpstar += binCount; } // B*+
	if (ID == -523) { nBmstar += binCount; } // B*-
	if (ID == 511) { nB0 += binCount; } // B0
	if (ID == -511) { nAB0 += binCount; } // anti-B0
	if (ID == 513) { nB0star += binCount; } // B*0
	if (ID == -513) { nAB0star += binCount; } // AB*0
	if (ID == 531) { nBs0 += binCount; } // Bs0
	if (ID == -531) { nABs0 += binCount; } // anti-Bs0
	if (ID == 533) { nBs0star += binCount; } // Bs*0
	if (ID == -533) { nABs0star += binCount; } // anti-Bs*0
	if (ID == 541) { nBcp += binCount; } // Bc+
	if (ID == -541) { nBcm += binCount; } // Bc-
	
	// B-baryons
	if (ID == 5122) { nLb += binCount; } // Lb
	if (ID == -5122) { nALb += binCount; } // anti-Lb
	if (ID == 5112) { nSigmabm += binCount; } // Sigmab-
	if (ID == -5112) { nASigmabm += binCount; } // anti-Sigmab-
	if (ID == 5222) { nSigmabp += binCount; } // Sigmab+
	if (ID == -5222) { nASigmabp += binCount; } // anti-Sigmab+
	if (ID == 5212) { nSigmab0 += binCount; } // Sigmab0
	if (ID == -5212) { nASigmab0 += binCount; } // anti-Sigmab0
	if (ID == 5132) { nXibm += binCount; } // Xib-
	if (ID == -5132) { nAXibm += binCount; } // anti-Xib-
	if (ID == 5232) { nXib0 += binCount; } // Xi0
	if (ID == -5232) { nAXib0 += binCount; } // anti-Xi0
	if (ID == 5332) { nOmegabm += binCount; } // Omegab-
	if (ID == -5332) { nAOmegabm += binCount; } // anti-Omegab-
	
	if (!isElementInArray(KnownIds, 54, ID)) { UnidentifiedIDs.push_back(ID); nMiss += binCount; }
	
	if (print) { std::cout << std::endl; }
      }
      
    } // MotherID loop

    // Fill histograms with particle abundances (raw and relative)
    // (possible to implement) Define lower bound to cut noise
    /*
    if (reduceNoise) {
      Double_t lowerBound = 1e-2;
      
      // Quarks
      hCQuarkRaw->SetBinContent(i, nc); hCQuarkRel->SetBinContent(i, nc/nTot);
      Double_t nOtherQuarks = nu + nd + ns + nb;
      hOtherQuarksRaw->SetBinContent(i, nOtherQuarks); hOtherQuarksRel->SetBinContent(i, nOtherQuarks/nTot);
      
      // Diquarks
      Double_t nDiQuarks = ndd1 + nud0 + nud1 + nuu1 + nsd0 + nsd1 + nsu0 + nss1 + nsu1 + ncd1 + ncu1 + ncs1;
      hDiQuarksRaw->SetBinContent(i, nDiQuarks); hDiQuarksRel->SetBinContent(i, nDiQuarks/nTot);
      
      // Gluons
      hGluonsRaw->SetBinContent(i, nGluon); hGluonsRel->SetBinContent(i, nGluon/nTot);
      
      // D-mesons
      Double_t nDMesons = nDpstar2010 + nD2pstar2460 + nD20star2460 + nDps2star2573;
      hDMesonsRaw->SetBinContent(i, nDMesons); hDMesonsRel->SetBinContent(i, nDMesons/nTot);
      
      // B-mesons
      Double_t nBMesonsCharged = nBp + nBm + nBpstar + nBmstar + nBcp + nBcm;
      if (nBMesonsCharged/nTot > lowerBound) { hBMesonsChargedRel->SetBinContent(i, nBMesonsCharged/nTot); }
      else { hBMesonsChargedRaw->SetBinContent(i, 0); hBMesonsChargedRel->SetBinContent(i, 0); }
      Double_t nBMesonsNeutral = nB0 + nAB0 + nB0star + nAB0star + nBs0 + nABs0 + nBs0star + nABs0star;
      hBMesonsNeutralRaw->SetBinContent(i, nBMesonsNeutral); hBMesonsNeutralRel->SetBinContent(i, nBMesonsNeutral/nTot);
      
      // B-baryons
      Double_t nBBaryons = nLb + nALb + nSigmabm + nASigmabm + nSigmabp + nASigmabp + nSigmab0 + nASigmab0 + nXibm + nAXibm + nXib0 + nAXib0 + nOmegabm + nAOmegabm;
      hBBaryonsRaw->SetBinContent(i, nBBaryons); hBBaryonsRel->SetBinContent(i, nBBaryons/nTot);
    } // reduce noise if-statement
    */
    
    // Quarks
    hUQuarkRaw->SetBinContent(i, nu); hUQuarkRel->SetBinContent(i, nu/nTot);
    hDQuarkRaw->SetBinContent(i, nd); hDQuarkRel->SetBinContent(i, nd/nTot);
    hSQuarkRaw->SetBinContent(i, ns); hSQuarkRel->SetBinContent(i, ns/nTot);
    hCQuarkRaw->SetBinContent(i, nc); hCQuarkRel->SetBinContent(i, nc/nTot);
    hBQuarkRaw->SetBinContent(i, nb); hBQuarkRel->SetBinContent(i, nb/nTot);
    Double_t nHadronisation = nu + nd + ns + nc + nb + nGluon;
    hHadronisationRaw->SetBinContent(i, nHadronisation); hHadronisationRel->SetBinContent(i, nHadronisation/nTot);
    
    // Diquarks
    Double_t nDiQuarks = ndd1 + nud0 + nud1 + nuu1 + nsd0 + nsd1 + nsu0 + nss1 + nsu1 + ncd1 + ncu1 + ncs1;
    hDiQuarksRaw->SetBinContent(i, nDiQuarks); hDiQuarksRel->SetBinContent(i, nDiQuarks/nTot);
    
    // Gluons
    hGluonsRaw->SetBinContent(i, nGluon); hGluonsRel->SetBinContent(i, nGluon/nTot);
    
    // D-mesons
    Double_t nDMesons = nDpstar2010 + nD2pstar2460 + nD20star2460 + nDps2star2573;
    hDMesonsRaw->SetBinContent(i, nDMesons); hDMesonsRel->SetBinContent(i, nDMesons/nTot);
    Double_t nADMesons = nADpstar2010 + nAD2pstar2460 + nAD20star2460 + nADps2star2573;
    hADMesonsRaw->SetBinContent(i, nADMesons); hADMesonsRel->SetBinContent(i, nADMesons/nTot);
      
    // B-mesons
    // *** collected ***
    Double_t nBMesonsCharged = nBp + nBm + nBpstar + nBmstar + nBcp + nBcm;
    hBMesonsChargedRaw->SetBinContent(i, nBMesonsCharged); hBMesonsChargedRel->SetBinContent(i, nBMesonsCharged/nTot);
    Double_t nBMesonsNeutral = nB0 + nAB0 + nB0star + nAB0star + nBs0 + nABs0 + nBs0star + nABs0star;
    hBMesonsNeutralRaw->SetBinContent(i, nBMesonsNeutral); hBMesonsNeutralRel->SetBinContent(i, nBMesonsNeutral/nTot);

    // *** divided ***
    hBpRaw->SetBinContent(i, nBp); hBpRel->SetBinContent(i, nBp/nTot);
    hBmRaw->SetBinContent(i, nBm); hBmRel->SetBinContent(i, nBm/nTot);
    hB0Raw->SetBinContent(i, nB0); hB0Rel->SetBinContent(i, nB0/nTot);
    hAB0Raw->SetBinContent(i, nAB0); hAB0Rel->SetBinContent(i, nAB0/nTot);
    hBs0Raw->SetBinContent(i, nBs0); hBs0Rel->SetBinContent(i, nBs0/nTot);
    hABs0Raw->SetBinContent(i, nABs0); hABs0Rel->SetBinContent(i, nABs0/nTot);
    
    // B-baryons
    Double_t nBBaryons = nLb + nALb + nSigmabm + nASigmabm + nSigmabp + nASigmabp + nSigmab0 + nASigmab0 + nXibm + nAXibm + nXib0 + nAXib0 + nOmegabm + nAOmegabm;
    hBBaryonsRaw->SetBinContent(i, nBBaryons); hBBaryonsRel->SetBinContent(i, nBBaryons/nTot);
      
    if (print) {
      // Particle abundances ---------------------------------------------------------------------
      std::cout << "Quark abundances" << std::endl;
      std::cout << "u = " << nu / nTot * 100 << "%" << std::endl;
      std::cout << "d = " << nd / nTot * 100 << "%" << std::endl;
      std::cout << "s = " << ns / nTot * 100 << "%" << std::endl;
      std::cout << "c = " << nc / nTot * 100 << "%" << std::endl;
      std::cout << "b = " << nb / nTot * 100 << "%" << std::endl;
      // --------------------------------------------------------------------------
      std::cout << std::endl;
      std::cout << "Diquark abundances" << std::endl;
      std::cout << "(dd)1 = " << ndd1 / nTot * 100 << "%" << std::endl;
      std::cout << "(ud)0 = " << nud0 / nTot * 100 << "%" << std::endl;
      std::cout << "(ud)1 = " << nud1 / nTot * 100 << "%" << std::endl;
      std::cout << "(uu)1 = " << nuu1 / nTot * 100 << "%" << std::endl;
      std::cout << "(sd)0 = " << nsd0 / nTot * 100 << "%" << std::endl;
      std::cout << "(sd)1 = " << nsd1 / nTot * 100 << "%" << std::endl;
      std::cout << "(su)0 = " << nsu0 / nTot * 100 << "%" << std::endl;
      std::cout << "(su)1 = " << nsu1 / nTot * 100 << "%" << std::endl;
      std::cout << "(ss)1 = " << nss1 / nTot * 100 << "%" << std::endl;
      std::cout << "(cd)1 = " << ncd1 / nTot * 100 << "%" << std::endl;
      std::cout << "(cu)1 = " << ncu1 / nTot * 100 << "%" << std::endl;
      std::cout << "(cs)1 = " << ncs1 / nTot * 100 << "%" << std::endl;
      // --------------------------------------------------------------------------
      std::cout << std::endl;
      std::cout << "gluons = " << nGluon / nTot * 100 << "%" << std::endl;
      // --------------------------------------------------------------------------
      std::cout << std::endl;
      std::cout << "D-meson abundances" << std::endl;
      std::cout << "D^{*+} (2010) = " << nDpstar2010 / nTot * 100 << "%" << std::endl;
      std::cout << "D_{2}^{*+} (2460) = " << nD2pstar2460 / nTot * 100 << "%" << std::endl;
      std::cout << "D_{2}^{*0} (2460) = " << nD20star2460 / nTot * 100 << "%" << std::endl;
      std::cout << "D_{s2}^{*+} (2573) = " << nDps2star2573 / nTot * 100 << "%" << std::endl;
      std::cout << "anti-D^{*+} (2010) = " << nADpstar2010 / nTot * 100 << "%" << std::endl;
      std::cout << "anti-D_{2}^{*+} (2460) = " << nAD2pstar2460 / nTot * 100 << "%" << std::endl;
      std::cout << "anti-D_{2}^{*0} (2460) = " << nAD20star2460 / nTot * 100 << "%" << std::endl;
      std::cout << "anti-D_{s2}^{*+} (2573) = " << nADps2star2573 / nTot * 100 << "%" << std::endl;
    // --------------------------------------------------------------------------
      std::cout << std::endl;
      std::cout << "B-meson abundances" << std::endl;
      std::cout << "B^{+} = " << nBp / nTot * 100 << "%" << std::endl;
      std::cout << "B^{-} = " << nBm / nTot * 100 << "%" << std::endl;
      std::cout << "B^{*+} = " << nBpstar / nTot * 100 << "%" << std::endl;
      std::cout << "B^{*-} = " << nBmstar / nTot * 100 << "%" << std::endl;
      std::cout << "B^{0} = " << nB0 / nTot * 100 << "%" << std::endl;
      std::cout << "anti-B^{0} = " << nAB0 / nTot * 100 << "%" << std::endl;
      std::cout << "B^{*0} = " << nB0star / nTot * 100 << "%" << std::endl;
      std::cout << "anti-B^{*0} = " << nAB0star / nTot * 100 << "%" << std::endl;
      std::cout << "B_s^{0} = " << nBs0 / nTot * 100 << "%" << std::endl;
      std::cout << "anti-B_s^{0} = " << nABs0 / nTot * 100 << "%" << std::endl;
      std::cout << "B_s^{*0} = " << nBs0star / nTot * 100 << "%" << std::endl;
      std::cout << "anti-B_s^{*0} = " << nABs0star / nTot * 100 << "%" << std::endl;
      std::cout << "B_c^{+} = " << nBcp / nTot * 100 << "%" << std::endl;
      std::cout << "B_c^{-} = " << nBcm / nTot * 100 << "%" << std::endl;
      // --------------------------------------------------------------------------
      std::cout << std::endl;
      std::cout << "B-baryon abundances" << std::endl;
      std::cout << "Lambda_{b} = " << nLb / nTot * 100 << "%" << std::endl;
      std::cout << "anti-Lambda_{b} = " << nALb / nTot * 100 << "%" << std::endl;
      std::cout << "Sigma_b^{-} = " << nSigmabm / nTot * 100 << "%" << std::endl;
      std::cout << "anti-Sigma_b^{-} = " << nASigmabm / nTot * 100 << "%" << std::endl;
      std::cout << "Sigma_b^{+} = " << nSigmabp / nTot * 100 << "%" << std::endl;
      std::cout << "anti-Sigma_b^{+} = " << nASigmabp / nTot * 100 << "%" << std::endl;
      std::cout << "Sigma_b^{0} = " << nSigmab0 / nTot * 100 << "%" << std::endl;
      std::cout << "anti-Sigma_b^{0} = " << nASigmab0 / nTot * 100 << "%" << std::endl;
      std::cout << "Xi_b^{-} = " << nXibm / nTot * 100 << "%" << std::endl;
      std::cout << "anti-Xi_b^{-} = " << nAXibm / nTot * 100 << "%" << std::endl;
      std::cout << "Xi_b^{0} = " << nXib0 / nTot * 100 << "%" << std::endl;
      std::cout << "anti-Xi_b^{0} = " << nAXib0 / nTot * 100 << "%" << std::endl;
      std::cout << "Omega_b^{-} = " << nOmegabm / nTot * 100 << "%" << std::endl;
      std::cout << "anti-Omega_b^{-} = " << nAOmegabm / nTot * 100 << "%" << std::endl;
      
      // For debugging
      nMissing = nTot
	- nu - nd - ns - nc - nb
	- ndd1 - nud0 - nud1 - nuu1 - nsd0 -nsd1 - nsu0 - nsu1 - nss1 - ncd1 - ncu1 - ncs1 
	- nGluon
	- nDpstar2010 - nD2pstar2460 - nD20star2460 - nDps2star2573
	- nADpstar2010 - nAD2pstar2460 - nAD20star2460 - nADps2star2573
	- nBp - nBm - nBpstar - nBmstar - nB0 - nAB0 - nB0star - nAB0star - nBs0 - nABs0 - nBs0star - nABs0star - nBcp - nBcm -
	nLb - nALb - nSigmabm - nASigmabm - nSigmabp - nASigmabp - nSigmab0 - nASigmab0 - nXibm - nAXibm - nXib0 - nAXib0 - nOmegabm - nAOmegabm;
      // Simple checks for consistency
      std::cout << std::endl;
      std::cout << "nMissing = " << nMissing << std::endl;
      std::cout << "Unidentified = " << nMissing / nTot * 100 << "%"  << std::endl;
      std::cout << "Equal to " << nMiss / nTot * 100 << "% ?" << std::endl;
      printVector(UnidentifiedIDs);
    }
    
  } // DPhi loop

  // Plot the trigger particles
  if (trigger) {

  TCanvas *cBMesons = new TCanvas(Form("cBMesonsTr_%s", ptRegion), Form("B mesons divided histograms Tr %s", ptRegion), 800, 600);
  cBMesons->cd();
  setCanvasMargins(cBMesons, 0.15, 0.1, 0.1, 0.1);
  gPad->SetLogy();

  // hHadronisationRel->SetTitle(Form("Trigger mothers %s", ptRegion));
  hHadronisationRel->SetTitle("");
  hHadronisationRel->GetYaxis()->SetTitle("relative abundance per bin");
  hHadronisationRel->GetYaxis()->SetRangeUser(1e-4, 2);
  hHadronisationRel->GetXaxis()->SetTitle("#Delta#phi (trigger, associate) (rad)");
  hHadronisationRel->SetStats(0);
  hHadronisationRel->SetLineColor(kBlue);
  hHadronisationRel->SetLineWidth(3);
  hHadronisationRel->Draw("hist");

  hDMesonsRel->SetLineColor(kRed);
  hDMesonsRel->SetLineStyle(1);
  hDMesonsRel->SetLineWidth(3);
  hDMesonsRel->Draw("same hist");

  hBpRel->SetLineColor(kYellow+2);
  hBpRel->SetLineStyle(1);
  hBpRel->SetLineWidth(3);
  hBpRel->Draw("same hist");

  hBmRel->SetLineColor(kYellow+2);
  hBmRel->SetLineStyle(3);
  hBmRel->SetLineWidth(3);
  hBmRel->Draw("same hist");

  hB0Rel->SetLineColor(kOrange+4);
  hB0Rel->SetLineStyle(1);
  hB0Rel->SetLineWidth(3);
  hB0Rel->Draw("same hist");

  hAB0Rel->SetLineColor(kOrange+4);
  hAB0Rel->SetLineStyle(3);
  hAB0Rel->SetLineWidth(3);
  hAB0Rel->Draw("same hist");

  hBs0Rel->SetLineColor(kOrange);
  hBs0Rel->SetLineStyle(1);
  hBs0Rel->SetLineWidth(2);
  hBs0Rel->Draw("same hist");

  hABs0Rel->SetLineColor(kOrange);
  hABs0Rel->SetLineStyle(3);
  hABs0Rel->SetLineWidth(2);
  hABs0Rel->Draw("same hist");

  hBBaryonsRel->SetLineColor(kMagenta);
  hBBaryonsRel->SetLineStyle(1);
  hBBaryonsRel->SetLineWidth(1);
  hBBaryonsRel->Draw("same hist");

  TLegend *legendBMesons = new TLegend(0.60, 0.70, 0.80, 0.40);
  legendBMesons->SetBorderSize(0);
  legendBMesons->SetTextSize(0.03);
  legendBMesons->AddEntry(hHadronisationRel, "hadronisation");
  legendBMesons->AddEntry(hDMesonsRel, hDMesonsRel->GetTitle());
  legendBMesons->AddEntry(hBpRel, hBpRel->GetTitle());
  legendBMesons->AddEntry(hBmRel, hBmRel->GetTitle());
  legendBMesons->AddEntry(hB0Rel, hB0Rel->GetTitle());
  legendBMesons->AddEntry(hAB0Rel, hAB0Rel->GetTitle());
  legendBMesons->AddEntry(hBs0Rel, hBs0Rel->GetTitle());
  legendBMesons->AddEntry(hABs0Rel, hABs0Rel->GetTitle());
  legendBMesons->AddEntry(hBBaryonsRel, hBBaryonsRel->GetTitle());
  legendBMesons->Draw();

  TCanvas *cStacked = new TCanvas(Form("cStackedTr_%s", ptRegion), Form("stacked histograms Tr %s", ptRegion), 800, 600);
  cStacked->cd();
  setCanvasMargins(cStacked, 0.15, 0.1, 0.1, 0.1);

  // Define the stack colors and fill styles
  hHadronisationRaw->SetFillStyle(1001);
  hHadronisationRaw->SetFillColor(kBlue);
  hDMesonsRaw->SetFillStyle(1001);
  hDMesonsRaw->SetFillColor(kRed);
  hBMesonsChargedRaw->SetFillStyle(1001);
  hBMesonsChargedRaw->SetFillColor(kOrange+4);
  hBMesonsNeutralRaw->SetFillStyle(3001);
  hBMesonsNeutralRaw->SetFillColor(kOrange+4);
  hBBaryonsRaw->SetFillStyle(1001);
  hBBaryonsRaw->SetFillColor(kMagenta);

  if (stackedYmin != 0) {
    hDPhi->GetYaxis()->SetRangeUser(stackedYmin, stackedYmax);
    hDPhi->GetYaxis()->SetRangeUser(stackedYmin, stackedYmax);
  }

  // Stack defined below, but first draw the original Delta phi histogram to compare with
  // hDPhi->SetTitle(Form("Trigger mothers %s", ptRegion));
  hDPhi->SetTitle("");
  hDPhi->GetYaxis()->SetTitle("#frac{1}{N_{trigger}} #frac{dN}{d#Delta#phi}");
  hDPhi->GetXaxis()->SetTitle("#Delta#phi (trigger, associate) (rad)");
  hDPhi->SetStats(0);
  hDPhi->SetLineColor(kBlack);
  hDPhi->SetLineWidth(3);
  hDPhi->Draw("hist");
  
  THStack* stack = new THStack("stackTr", "");
  stack->Add(hHadronisationRaw);
  stack->Add(hDMesonsRaw);
  stack->Add(hBMesonsChargedRaw); 
  stack->Add(hBMesonsNeutralRaw);
  stack->Add(hBBaryonsRaw);
  stack->Draw("same hist");

  TLegend *legendStacked = new TLegend(legendXmin, legendYmin, legendXmax, legendYmax);
  legendStacked->SetBorderSize(0);
  legendStacked->SetTextSize(0.03);
  legendStacked->AddEntry(hDPhi, "#Delta#phi");
  legendStacked->AddEntry(hHadronisationRaw, "hadronisation", "F");
  legendStacked->AddEntry(hDMesonsRaw, hDMesonsRaw->GetTitle(), "F");
  legendStacked->AddEntry(hBMesonsNeutralRaw, hBMesonsNeutralRaw->GetTitle(), "F");
  legendStacked->AddEntry(hBMesonsChargedRaw, hBMesonsChargedRaw->GetTitle(), "F");
  legendStacked->AddEntry(hBBaryonsRaw, hBBaryonsRaw->GetTitle(), "F");
  
  legendStacked->Draw();

  if (write) {
    cBMesons->SaveAs(Form("Plots/DecayAndHadronisation/cBMesonsTr_%s_%s.pdf", ptRegion, ptTrRegion));
    cStacked->SaveAs(Form("Plots/DecayAndHadronisation/cStackedTr_%s_%s.pdf", ptRegion, ptTrRegion));
  }
  
  } // end of if (trigger) statement ----------------------------------------------------------
  
  //
  //
  //
  //
  //
  //
  //
  //
  //
  //
  // Now plot the associate mother IDs ------------------------------------------------
  //
  //
  //
  //
  //
  //
  //
  //
  //
  //
  
  if (associate) {

  TCanvas *cBMesons = new TCanvas(Form("cBMesonsAs_%s", ptRegion), Form("B mesons divided histograms As %s", ptRegion), 800, 600);
  cBMesons->cd();
  setCanvasMargins(cBMesons, 0.15, 0.1, 0.1, 0.1);
  gPad->SetLogy();

  // hHadronisationRel->SetTitle(Form("Associate mothers %s", ptRegion));
  hHadronisationRel->SetTitle("");
  hHadronisationRel->GetYaxis()->SetTitle("relative abundance per bin");
  hHadronisationRel->GetYaxis()->SetRangeUser(1e-4, 2);
  hHadronisationRel->GetXaxis()->SetTitle("#Delta#phi (trigger, associate) (rad)");
  hHadronisationRel->SetStats(0);
  hHadronisationRel->SetLineColor(kBlue);
  hHadronisationRel->SetLineWidth(3);
  hHadronisationRel->Draw("hist");

  hADMesonsRel->SetLineColor(kRed);
  hADMesonsRel->SetLineStyle(3);
  hADMesonsRel->SetLineWidth(3);
  hADMesonsRel->Draw("same hist");

  hBpRel->SetLineColor(kYellow+2);
  hBpRel->SetLineStyle(1);
  hBpRel->SetLineWidth(3);
  hBpRel->Draw("same hist");

  hBmRel->SetLineColor(kYellow+2);
  hBmRel->SetLineStyle(3);
  hBmRel->SetLineWidth(3);
  hBmRel->Draw("same hist");

  hB0Rel->SetLineColor(kOrange+4);
  hB0Rel->SetLineStyle(1);
  hB0Rel->SetLineWidth(3);
  hB0Rel->Draw("same hist");

  hAB0Rel->SetLineColor(kOrange+4);
  hAB0Rel->SetLineStyle(3);
  hAB0Rel->SetLineWidth(3);
  hAB0Rel->Draw("same hist");

  hBs0Rel->SetLineColor(kOrange);
  hBs0Rel->SetLineStyle(1);
  hBs0Rel->SetLineWidth(2);
  hBs0Rel->Draw("same hist");

  hABs0Rel->SetLineColor(kOrange);
  hABs0Rel->SetLineStyle(3);
  hABs0Rel->SetLineWidth(2);
  hABs0Rel->Draw("same hist");

  hBBaryonsRel->SetLineColor(kMagenta);
  hBBaryonsRel->SetLineStyle(1);
  hBBaryonsRel->SetLineWidth(1);
  hBBaryonsRel->Draw("same hist");

  hBBaryonsRel->SetLineColor(kRed);

  TLegend *legendBMesons = new TLegend(0.60, 0.70, 0.80, 0.40);
  legendBMesons->SetBorderSize(0);
  legendBMesons->SetTextSize(0.03);
  legendBMesons->AddEntry(hHadronisationRel, "hadronisation");
  legendBMesons->AddEntry(hADMesonsRel, hADMesonsRel->GetTitle());
  legendBMesons->AddEntry(hBpRel, hBpRel->GetTitle());
  legendBMesons->AddEntry(hBmRel, hBmRel->GetTitle());
  legendBMesons->AddEntry(hB0Rel, hB0Rel->GetTitle());
  legendBMesons->AddEntry(hAB0Rel, hAB0Rel->GetTitle());
  legendBMesons->AddEntry(hBs0Rel, hBs0Rel->GetTitle());
  legendBMesons->AddEntry(hABs0Rel, hABs0Rel->GetTitle());
  legendBMesons->AddEntry(hBBaryonsRel, hBBaryonsRel->GetTitle());
  legendBMesons->Draw();

  TCanvas *cStacked = new TCanvas(Form("cStackedAs_%s", ptRegion), Form("stacked histograms As %s", ptRegion), 800, 600);
  cStacked->cd();
  setCanvasMargins(cStacked, 0.15, 0.1, 0.1, 0.1);

  // Define the stack colors and fill styles
  hHadronisationRaw->SetFillStyle(1001);
  hHadronisationRaw->SetFillColor(kBlue);
  hBMesonsChargedRaw->SetFillStyle(1001);
  hBMesonsChargedRaw->SetFillColor(kOrange+4);
  hBMesonsNeutralRaw->SetFillStyle(3001);
  hBMesonsNeutralRaw->SetFillColor(kOrange+4);
  hADMesonsRaw->SetFillStyle(3001);
  hADMesonsRaw->SetFillColor(kRed);
  hBBaryonsRaw->SetFillStyle(1001);
  hBBaryonsRaw->SetFillColor(kMagenta);

  if (stackedYmin != 0) {
    hDPhi->GetYaxis()->SetRangeUser(stackedYmin, stackedYmax);
    hDPhi->GetYaxis()->SetRangeUser(stackedYmin, stackedYmax);
  }

  // Stack defined below, but first the original Delta phi histogram to compare with
  // hDPhi->SetTitle(Form("Associate mothers %s", ptRegion));
  hDPhi->SetTitle("");
  hDPhi->GetYaxis()->SetTitle("#frac{1}{N_{trigger}} #frac{dN}{d#Delta#phi}");
  hDPhi->GetXaxis()->SetTitle("#Delta#phi (trigger, associate) (rad)");
  hDPhi->SetStats(0);
  hDPhi->SetLineColor(kBlack);
  hDPhi->SetLineWidth(3);
  hDPhi->Draw("hist");
  
  THStack* stack = new THStack("stackAs", "");
  stack->Add(hHadronisationRaw);
  stack->Add(hADMesonsRaw);
  stack->Add(hBMesonsChargedRaw); 
  stack->Add(hBMesonsNeutralRaw);
  stack->Add(hBBaryonsRaw);
  stack->Draw("same hist");

  TLegend *legendStacked = new TLegend(legendXmin, legendYmin, legendXmax, legendYmax);
  legendStacked->SetBorderSize(0);
  legendStacked->SetTextSize(0.03);
  legendStacked->AddEntry(hDPhi, "#Delta#phi");
  legendStacked->AddEntry(hHadronisationRaw, "hadronisation", "F");
  legendStacked->AddEntry(hADMesonsRaw, hADMesonsRaw->GetTitle(), "F");
  legendStacked->AddEntry(hBMesonsNeutralRaw, hBMesonsNeutralRaw->GetTitle(), "F");
  legendStacked->AddEntry(hBMesonsChargedRaw, hBMesonsChargedRaw->GetTitle(), "F");
  legendStacked->AddEntry(hBBaryonsRaw, hBBaryonsRaw->GetTitle(), "F");
  legendStacked->Draw(); 

  if (write) {
    cBMesons->SaveAs(Form("Plots/DecayAndHadronisation/cBMesonsAs_%s_%s.pdf", ptRegion, ptTrRegion));
    cStacked->SaveAs(Form("Plots/DecayAndHadronisation/cStackedAs_%s_%s.pdf", ptRegion, ptTrRegion));
  }

  } // end of if (associate) statement
  
} // readTree

int DecayAndHadronisation_Stacked_MotherStudy() {

  /*
void readTree(const char* ptRegion, vector<const char*> ptTrRegion [ 0 = trigger, 1 = associate],
              bool trigger,
              bool associate,
	      bool print,
	      bool write = false,
	      Double_t legendXmin = 0, Double_t legendYmin = 0, Double_t legendXmax = 0, Double_t legendYmax = 0,
	      Double_t stackedYmin = 0, Double_t stackedYmax = 0
	      ) {
  */

  // As long as this vector is implemented in the order trigger, associate, it can be used as an argument in combination with the bool trigger or associate.
  // It should be easy to add different pT regions if relevant
  vector<const char*> ptTrRegionVectorHH;
  ptTrRegionVectorHH.push_back("hDPhiTrMotherHH");
  ptTrRegionVectorHH.push_back("hDPhiAsMotherHH");
  vector<const char*> ptTrRegionVectorLL;
  ptTrRegionVectorLL.push_back("hDPhiTrMotherLL");
  ptTrRegionVectorLL.push_back("hDPhiAsMotherLL");

  // It's wise to save sometimes
  bool write = false;
  
  // Trigger
  
  readTree("hDPhiHH", ptTrRegionVectorHH,
           true,
	   false,
	   false,
	   write,
	   0.36, 0.58, 0.56, 0.88,
	   1e-7, 5e-5);
  
  readTree("hDPhiLL", ptTrRegionVectorLL,
           true,
           false,
	   false,
	   write,
	   0.24, 0.50, 0.44, 0.81,
	   1e-4, 3e-3);
  

  // Associate
  
  readTree("hDPhiHH", ptTrRegionVectorHH,
	   false,
	   true,
	   false,
	   write,
	   0.36, 0.58, 0.56, 0.88,
	   3e-8, 5e-5);
  
  readTree("hDPhiLL", ptTrRegionVectorLL,
	   false,
	   true,
	   false,
	   write,
	   0.24, 0.50, 0.44, 0.81,
	   3e-5, 3e-3);
  
  
  return 0;
}
