// containsExcitedD.C
// Simple macro to investigate particle contents of the 'prompt' ccbar simulation outputs
// (in order to see if they are really 'prompt')

int containsExcitedD() {

  TFile* rootFile2D = new TFile("/home/pveen/scripts/Nikhef/MasterThesis/RootFiles/complete_root_cc_prompt_214/DplusDminus.root");

  TH2D* hDPhiMother = (TH2D*)rootFile2D->Get("hDPhiTrMother");
  
  // Start main loops over DPhi and MotherID bins
  int nBinsDPhi = hDPhiMother->GetXaxis()->GetNbins();
  // int nBinsDPhi = 30;
  int nBinsMotherID = hDPhiMother->GetYaxis()->GetNbins();
  // int nBinsMotherID = 10;

  for (int i = 0; i <= nBinsDPhi; i++) {

    for (int j = 1; j <= nBinsMotherID; j++) {
      
      double binCount = hDPhiMother->GetBinContent(i, j);
      if (binCount != 0) {
	
	double phiMin = hDPhiMother->GetXaxis()->GetBinLowEdge(i);
	double phiMax = hDPhiMother->GetXaxis()->GetBinUpEdge(i);
	
	std::cout << "DPhi bin number: " << i << " DPhi_min = " << phiMin
		  << ", DPhi_max = " << phiMax << std::endl;
	std::cout << "Bin (" << i << ", " << j << ") has content: " << binCount << std::endl;
	
	double ID = hDPhiMother->GetYaxis()->GetBinCenter(j);
	std::cout << "Mother ID bin number: " << j << " Mother ID: " << ID << std::endl;

      } // if
      
    } // j
    
  } //i

  return 0;

}
