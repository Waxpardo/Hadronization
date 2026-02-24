// status_analysis_cc.C
// ROOT macro that creates azimuthal angular correlations on a given trigger and associate particle pair using input simulated with PYTHIA as in the script ccbarcorrelations_status.cpp
// Histograms are created for the angular correlations of the trigger and associate and saved to an output ROOT file.
// This script is focussed on charm hadrons and includes histograms containing PDG IDs of the trigger and associate mothers as well as a general split in pT regions and production mechanism.
// The code is layed out in such a way that it should be easy to append or modify other settings, as desired.

// C++ libraries
#include <iostream>
#include <vector>
// ROOT libraries
#include "TFile.h"
#include "TH1D.h"
#include "TTree.h"
#include "TChain.h"
#include "TString.h"

#define PI 3.14159265
using namespace std;
using namespace TMath;

Double_t DeltaPhi(Double_t phi1, Double_t phi2) {
        // Returns delta phi in range -pi/2 3pi/2
        // Used to make the near- and away-side peak better visible 
	return fmod(phi1-phi2+2.5*PI,2*PI)-0.5*PI;
	}
	
void status_file(Int_t id_trigger,Int_t id_associate, TString filename, const char* title) {
        // This functions takes the trigger and associate id and creates a ROOT output file with the same filename
        // containing the histograms produced in this macro
	
	// Define the TChain
	TChain *ch1 = new TChain("tree");
	TFile *output = new TFile(filename,"RECREATE");

	// OPTION 1: SINGLE FILE
	ch1->Add("output.root");

	// OPTION 2: BATCH FILE STRUCTURE
	// Number of trees to be added to the TChain
	// This can be changed by the user
	/*
 	int ntrees = 25;
	
	for( int i = 1; i < ntrees+1;  i++) {
	// One can change the file path accordingly
	  ch1->Add(Form("Group%i/output.root",i)); 
	}
	// COMMENT TILL THIS LINE TO DISABLE OPTION 2
	*/

	// *** --------- ***

	// First retrieve the event information histograms that are produced in the Pythia simulations
	// Can be made into a function that takes the histograms from the TCHain and adds them
	TH1D* hMULTIPLICITY = 0;

	for (Int_t iEntry = 0; iEntry < ch1->GetNtrees(); iEntry++) {

	  ch1->GetEntry(iEntry);
	  TFile* currentFile = ch1->GetCurrentFile();
	  TH1D* hEntryMULTIPLICITY = (TH1D*)currentFile->Get("hMULTIPLICITY");
	  
	  if (!hMULTIPLICITY) {
	    hMULTIPLICITY = (TH1D*)hEntryMULTIPLICITY->Clone("summed MULTIPLICITY");
	    hMULTIPLICITY->Reset();
	  }

	  hMULTIPLICITY->Add(hEntryMULTIPLICITY);

	}

	// cout << "integral = " << hTotMULTIPLICITY->Integral() << endl;
	
	// Now we define vectors that carry the information at event level
	vector<Int_t>* vID = 0;
	vector<Double_t>* vPt = 0;
	vector<Double_t>* vPhi = 0;
	vector<Double_t>* vStatus = 0;
	vector<Double_t>* vEta = 0;
	vector<Double_t>* vY = 0;
	vector<Double_t>* vMother1 = 0;
	vector<Double_t>* vMotherID = 0;
	Int_t MULTIPLICITY = 0;
	
	// Setting up chain branch addresses to the vectors defined above
	ch1->SetBranchAddress("ID",&vID);
	ch1->SetBranchAddress("PT",&vPt);
	ch1->SetBranchAddress("PHI",&vPhi);
	ch1->SetBranchAddress("ETA",&vEta);
	ch1->SetBranchAddress("Y",&vY);
	ch1->SetBranchAddress("STATUS",&vStatus);
	ch1->SetBranchAddress("MOTHER",&vMother1);
	ch1->SetBranchAddress("MOTHERID",&vMotherID);
	ch1->SetBranchAddress("MULTIPLICITY",&MULTIPLICITY);
	
	// Variables used in this script
	// p indicates trigger particle variables
	// a indicates associate particle variables
	Int_t aID,pID;
	Double_t pPt,pPhi,pStatus,pEta,pY,pMother,pMotherPhi,pMotherID;
	Double_t aPt,aPhi,aStatus,aEta,aY,aMother,aMotherPhi,aMotherID;
	int nTrigger = 0;

	// Besides pT dependence, it is also interesting to look at the data as a function of multiplicity and (pseudo)rapidity
	// Classification is set here, first for pseudorapidity and rapidity, and then for multiplicity:
	// (F) Forward > abs(etaCrit), (C) Central < abs(etaCrit)
	Double_t etaCrit = 2; // pseudorapidity
	Double_t yCrit = 2; // rapidity

	// The multiplicity cuts are defined using the percentiles of the total multiplicity
	Double_t multCrit0, multCrit20, multCrit40, multCrit60, multCrit80; // To be filled with multiplicity (careful: it's analogous to centrality, so 80_100 is the 20% lowest multiplicious events
	Bool_t flag0_20 = true; Bool_t flag20_40 = true; Bool_t flag40_60 = true; Bool_t flag60_80 = true; Bool_t flag80_100 = true; // Flags are used so that only one for loop is necessary
	Double_t multCrit1, multCrit5; // Specific selection cuts for top 1% and top 5% of multiplicity events
	Bool_t flag1 = true; Bool_t flag5 = true;
	Int_t fullIntegral = 0; Int_t currentIntegral = 0;

	// Calculation of multiplicity percentiles
	fullIntegral = hMULTIPLICITY->Integral();
	
	for (Int_t i = 0; i <= hMULTIPLICITY->GetNbinsX(); i++) {

	  currentIntegral += hMULTIPLICITY->GetBinContent(i);

	  if (flag80_100 && currentIntegral >= 0.2 * fullIntegral) { multCrit80 = hMULTIPLICITY->GetBinCenter(i); flag80_100 = false; }
	  
          if (flag60_80 && currentIntegral >= 0.4 * fullIntegral) { multCrit60 = hMULTIPLICITY->GetBinCenter(i); flag60_80 = false; }

          if (flag40_60 && currentIntegral >= 0.6 * fullIntegral) { multCrit40 = hMULTIPLICITY->GetBinCenter(i); flag40_60 = false; }

          if (flag20_40 && currentIntegral >= 0.8 * fullIntegral) { multCrit20 = hMULTIPLICITY->GetBinCenter(i); flag20_40 = false; }

	  if (flag5 && currentIntegral >= 0.95 * fullIntegral) { multCrit5 = hMULTIPLICITY->GetBinCenter(i); flag5 = false; }

	  if (flag1 && currentIntegral >= 0.99 * fullIntegral) { multCrit1 = hMULTIPLICITY->GetBinCenter(i); flag1 = false; }

	} 
	
	// This is only used to double-check whether these histograms are consistent with their status                        
	// They can be removed from this script or the title of the plots can be changed in drawing scripts 
	Double_t primary_status = 83;
	Double_t secondary_status = 91;
	
	// Indicate the total number of events analysed
	int nEvents = ch1->GetEntries();
	cout<<"The number of events for this analysis is: "<<nEvents<<endl;
	
	// Definitions of produced histograms                                                                               
        // The histograms are divided into two categories: angular correlations and trigger spectra, the latter can be integrated over in local scripts to obtain the total number of triggers, which the yield is then normalised over.                                      
	// The naming convention is as follows:                                                                                      
	// h = histogram                                                              
	// TrPt = trigger spectra                                                                                                   
	// DPhi = Delta phi (angular correlations)                                                                                  
	// Pr = primary status, Sc = secondary status (production mechanisms)                                                        

	// Furthermore, the trigger-associate pairs can be divided according to their pT, indicated as follows:        
	// Low (L): 1 < pT < 3 GeV                                                                                                 
	// Intermediate (I): 3 < pT < 8 GeV                                                                                         
	// High (H): pT > 8 GeV                                                                                                     
	// Hence there are 6 total combinations for trigger-associate pairs (LL), (IL), (HL), (II), (HI) and (HH).  

	// At this point the charm study starts differing from beauty, as charm hadrons can be produced not only from hadronisation mechanisms (prompt), but also from decaying beauty hadrons or excited D-states (non-prompt). This becomes a pronounced feature of PYTHIA and shows in the appearance of near-side structures in the angular correlations for D hadron correlations.
	// In order to look at this, several additional histograms are produced (e.g. combining primary and secondary production processes) and, in particular, a study is done using 2D histograms to check the origin of the angular correlations using the PDG IDs of their mothers
	// This is even done for the angular correlations of their mothers, in order to conclude whether the trigger and associate mothers are different or identical.

	// The histograms are defined compactly for clarity

	// Distribution of variables
	TH1D* hEtaTr = new TH1D("hEtaTr",Form("Pseudorapidity distribution for trigger %s;#eta;Counts",title),100,-4,4);
	TH1D* hEtaAs = new TH1D("hEtaAs",Form("Pseudorapidity distribution for associate %s;#eta;Counts",title),100,-4,4);
	TH1D* hYTr = new TH1D("hYTr",Form("Rapidity distribution for trigger %s;#eta;Counts",title),100,-4,4);
	TH1D* hYAs = new TH1D("hYAs",Form("Rapidity distribution for associate %s;#eta;Counts",title),100,-4,4);
	TH1D* hMULT = new TH1D("hMULT",Form("Multiplicity per event for %s;multiplicity;Counts",title),100,0,400);

	// 2-dimensional histograms
	TH2D* hTrPtEta = new TH2D("hPtEta",Form("pT and pseudorapidity trigger pT for trigger %s;p_{T};#eta;Counts",title),100,0,50,100,-4,4); 
	TH2D* hTrPtY = new TH2D("hPtY",Form("pT and rapidity trigger pT for trigger %s;p_{T};y;Counts",title),100,0,50,100,-4,4);

	// No trigger-associate pT constraints
	TH1D *hTrPt = new TH1D("hTrPt",Form("Trigger Transverse Momentum for %s;p_{T} GeV/c;Counts",title),100,0,50);
	TH1D *hTrPtPr = new TH1D("hTrPtPr",Form("Trigger Transverse Momentum for %s from %.1f;p_{T} GeV/c;Counts",title,primary_status),100,0,50);
	TH1D *hTrPtSc = new TH1D("hTrPtSc",Form("Trigger Transverse Momentum for %s from %.1f;p_{T} GeV/c;Counts",title,secondary_status),100,0,50);
	TH1D *hTrPtPrSc = new TH1D("hTrPtPrSc",Form("Trigger Transverse Momentum for %s from %.1f and %.1f;p_{T} GeV/c;Counts",title,primary_status,secondary_status),100,0,50);

	TH1D *hDPhi = new TH1D("hDPhi",Form("#Delta#phi for all processes for %s pair;#Delta#Phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D *hDPhiPr = new TH1D("hDPhiPr",Form("#Delta#phi for production mechanism %.1f for %s pair;#Delta#Phi (rad);Counts",primary_status,title),100,-PI/2,3*PI/2);
	TH1D *hDPhiSc = new TH1D("hDphiSc",Form("#Delta#phi for production mechanism %.1f for %s pair;#Delta#Phi (rad);Counts",secondary_status,title),100,-PI/2,3*PI/2);
	
	/*
	TH1D *hTrPtLLPr = new TH1D("hTrPtLLPr",Form("Trigger Transverse Momentum for %s from %.1f for low-low p_{T};p_{T} GeV/c;Counts",title,primary_status),100,0,50);
        TH1D *hTrPtLLSc = new TH1D("hTrPtLLSc",Form("Trigger Transverse Momentum for %s from %.1f for low-low p_{T};p_{T} GeV/c;Counts",title,secondary_status),100,0,50);
        TH1D *hTrPtLLPrSc = new TH1D("hTrPtLLPrSc",Form("Trigger Transverse Momentum for %s from %.1f and %.1f for low-low p_{T};p_{T} GeV/c;Counts",title,primary_status,secondary_status),100,0,50);
	TH1D *hTrPtHHPr = new TH1D("hTrPtHHPr",Form("Trigger Transverse Momentum for %s from %.1f for high-high p_{T};p_{T} GeV/c;Counts",title,primary_status),100,0,50);
	TH1D *hTrPtHHSc = new TH1D("hTrPtHHSc",Form("Trigger Transverse Momentum for %s from %.1f for high-high p_{T};p_{T} GeV/c;Counts",title,secondary_status),100,0,50);
        TH1D *hTrPtHHPrSc = new TH1D("hTrPtHHPrSc",Form("Trigger Transverse Momentum for %s from %.1f and %.1f for high-high p_{T};p_{T} GeV/c;Counts",title,primary_status,secondary_status),100,0,50);
	*/

	// pT dependence
	TH1D* hDPhiLL = new TH1D("hDPhiLL",Form("%s #Delta#phi correlation for low-low p_{T};#Delta#phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D* hDPhiLI = new TH1D("hDPhiLI",Form("%s #Delta#phi correlation for low-int p_{T};#Delta#phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D* hDPhiLH = new TH1D("hDPhiLH",Form("%s #Delta#phi correlation for low-high p_{T};#Delta#phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D* hDPhiIL = new TH1D("hDPhiIL",Form("%s #Delta#phi correlation for intermediate-low p_{T};#Delta#phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D* hDPhiII = new TH1D("hDPhiII",Form("%s #Delta#phi correlation for intermediate-intermediate p_{T};#Delta#phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D* hDPhiIH = new TH1D("hDPhiIH",Form("%s #Delta#phi correlation for intermediate-high p_{T};#Delta#phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D* hDPhiHL = new TH1D("hDPhiHL",Form("%s #Delta#phi correlation for high-low p_{T};#Delta#phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D* hDPhiHI = new TH1D("hDPhiHI",Form("%s #Delta#phi correlation for high-intermediate p_{T};#Delta#phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D* hDPhiHH = new TH1D("hDPhiHH",Form("%s #Delta#phi correlation for high-high p_{T};#Delta#phi (rad);Counts",title),100,-PI/2,3*PI/2);

	// Trigger pT on pT cuts
	TH1D* hTrPtL = new TH1D("hTrPtL",Form("Trigger Transverse Momentum for low p_{T} %s;p_{T} GeV/c;Counts",title),100,0,50);
	TH1D* hTrPtI = new TH1D("hTrPtI",Form("Trigger Transverse Momentum for intermediate p_{T} %s;p_{T} GeV/c;Counts",title),100,0,50);
	TH1D* hTrPtH = new TH1D("hTrPtH",Form("Trigger Transverse Momentum for high p_{T} %s;p_{T} GeV/c;Counts",title),100,0,50);

	// Pseudorapidity dependence
	TH1D* hDPhiEtaCC = new TH1D("hDPhiEtaCC",Form("%s #Delta#phi correlation for trigger abs(eta) < %g, assoc abs(eta) < %g;#Delta#phi (rad);Counts",title,etaCrit,etaCrit),100,-PI/2,3*PI/2);
	TH1D* hDPhiEtaCF = new TH1D("hDPhiEtaCF",Form("%s #Delta#phi correlation for trigger abs(eta) < %g, assoc abs(eta) > %g;#Delta#phi (rad);Counts",title,etaCrit,etaCrit),100,-PI/2,3*PI/2);
	TH1D* hDPhiEtaFC = new TH1D("hDPhiEtaFC",Form("%s #Delta#phi correlation for trigger abs(eta) > %g, assoc abs(eta) < %g;#Delta#phi (rad);Counts",title,etaCrit,etaCrit),100,-PI/2,3*PI/2);
	TH1D* hDPhiEtaFF = new TH1D("hDPhiEtaFF",Form("%s #Delta#phi correlation for trigger abs(eta) > %g, assoc abs(eta) > %g;#Delta#phi (rad);Counts",title,etaCrit,etaCrit),100,-PI/2,3*PI/2);

	// Trigger pT on pseudorapidity cuts
	TH1D* hTrPtEtaC = new TH1D("hTrPtEtaC",Form("Trigger Transverse Momentum for %s with trigger abs(eta) < %g, assoc abs(eta) < %g;p_{T} GeV/c;Counts",title,etaCrit,etaCrit),100,0,50);
        TH1D* hTrPtEtaF = new TH1D("hTrPtEtaF",Form("Trigger Transverse Momentum for %s with trigger abs(eta) > %g, assoc abs(eta) > %g;p_{T} GeV/c;Counts",title,etaCrit,etaCrit),100,0,50);

	// Rapidity dependence              
        TH1D* hDPhiYCC = new TH1D("hDPhiYCC",Form("%s #Delta#phi correlation for trigger abs(eta) < %g, assoc abs(eta) < %g;#Delta#phi (rad);Counts",title,etaCrit,etaCrit),100,-PI/2,3*PI/2);
	TH1D* hDPhiYCF = new TH1D("hDPhiYCF",Form("%s #Delta#phi correlation for trigger abs(eta) < %g, assoc abs(eta) > %g;#Delta#phi (rad);Counts",title,etaCrit,etaCrit),100,-PI/2,3*PI/2);
        TH1D* hDPhiYFC = new TH1D("hDPhiYFC",Form("%s #Delta#phi correlation for trigger abs(eta) > %g, assoc abs(eta) < %g;#Delta#phi (rad);Counts",title,etaCrit,etaCrit),100,-PI/2,3*PI/2);
	TH1D* hDPhiYFF = new TH1D("hDPhiYFF",Form("%s #Delta#phi correlation for trigger abs(eta) > %g, assoc abs(eta) > %g;#Delta#phi (rad);Counts",title,etaCrit,etaCrit),100,-PI/2,3*PI/2);

	// Trigger pT on rapidity cuts
        TH1D* hTrPtYC = new TH1D("hTrPtYC",Form("Trigger Transverse Momentum for %s with trigger abs(eta) < %g, assoc abs(eta) < %g;p_{T} GeV/c;Counts",title,etaCrit,etaCrit),100,0,50);
	TH1D* hTrPtYF = new TH1D("hTrPtYF",Form("Trigger Transverse Momentum for %s with trigger abs(eta) > %g, assoc abs(eta) > %g;p_{T} GeV/c;Counts",title,etaCrit,etaCrit),100,0,50);

	// Multiplicity dependence (trigger pT included)
	TH1D* hDPhiM80_100 = new TH1D("hDPhiM80_100",Form("%s #Delta#phi correlation for 80-100 centrality bin (0 < MULT < %g);#Delta#phi (rad);Counts",title,multCrit80),100,-PI/2,3*PI/2);
	TH1D* hTrPtM80_100 = new TH1D("hTrPtM80_100",Form("Trigger Transverse Momentum for %s with 80-100 centrality bin (0 < MULT < %g);p_{T} GeV/c;Counts",title,multCrit80),100,0,50);
	TH1D* hDPhiM60_80 = new TH1D("hDPhiM60_80",Form("%s #Delta#phi correlation for 60-80 centrality bin (%g < MULT < %g);#Delta#phi (rad);Counts",title,multCrit80,multCrit60),100,-PI/2,3*PI/2);
	TH1D* hTrPtM60_80 = new TH1D("hTrPtM60_80",Form("Trigger Transverse Momentum for %s with 60-80 centrality bin (%g < MULT < %g);p_{T} GeV/c;Counts",title,multCrit80,multCrit60),100,0,50);
	TH1D* hDPhiM40_60 = new TH1D("hDPhiM40_60",Form("%s #Delta#phi correlation for 40-60 centrality bin (%g < MULT < %g);#Delta#phi (rad);Counts",title,multCrit60,multCrit40),100,-PI/2,3*PI/2);
	TH1D* hTrPtM40_60 = new TH1D("hTrPtM40_60",Form("Trigger Transverse Momentum for %s with 40-60 centrality bin (%g < MULT < %g);p_{T} GeV/c;Counts",title,multCrit60,multCrit40),100,0,50);
	TH1D* hDPhiM20_40 = new TH1D("hDPhiM20_40",Form("%s #Delta#phi correlation for 20-40 centrality bin (%g < MULT < %g);#Delta#phi (rad);Counts",title,multCrit40,multCrit20),100,-PI/2,3*PI/2);
        TH1D* hTrPtM20_40 = new TH1D("hTrPtM20_40",Form("Trigger Transverse Momentum for %s with 20-40 centrality bin (%g < MULT < %g);p_{T} GeV/c;Counts",title,multCrit40,multCrit20),100,0,50);
        TH1D* hDPhiM5_20 = new TH1D("hDPhiM5_20",Form("%s #Delta#phi correlation for 5-20 centrality bin (MULT > %g);#Delta#phi (rad);Counts",title,multCrit20),100,-PI/2,3*PI/2);
        TH1D* hTrPtM5_20 = new TH1D("hTrPtM5_20",Form("Trigger Transverse Momentum for %s with 5-20 centrality bin (MULT > %g);p_{T} GeV/c;Counts",title,multCrit20),100,0,50);
	// Top 5 and top 1%
	TH1D* hDPhiM1_5 = new TH1D("hDPhiM1_5",Form("%s #Delta#phi correlation for 1-5 centrality bin (MULT > %g);#Delta#phi (rad);Counts",title,multCrit5),100,-PI/2,3*PI/2);
	TH1D* hTrPtM1_5 = new TH1D("hTrPtM1_5",Form("Trigger Transverse Momentum for %s with 1-5 centrality bin (MULT > %g);p_{T} GeV/c;Counts",title,multCrit5),100,0,50);
        TH1D* hDPhiM1 = new TH1D("hDPhiM1",Form("%s #Delta#phi correlation for top 1%% most multiplicious events (MULT > %g);#Delta#phi (rad);Counts",title,multCrit1),100,-PI/2,3*PI/2);
        TH1D* hTrPtM1 = new TH1D("hTrPtM1",Form("Trigger Transverse Momentum for %s with top 1%% most multiplicious events (MULT > %g);p_{T} GeV/c;Counts",title,multCrit1),100,0,50);
	
	// Hadronisation production mechanism for (LL) and (HH)
	TH1D* hDPhiLLPr = new TH1D("hDPhiLLPr",Form("%s #Delta#phi correlation for low-low p_{T} from %.1f;#Delta#phi (rad);Counts",title,primary_status),100,-PI/2,3*PI/2);
	TH1D* hDPhiHHPr = new TH1D("hDPhiHHPr",Form("%s #Delta#phi correlation for high-high p_{T} from %.1f;#Delta#phi (rad);Counts",title, primary_status),100,-PI/2,3*PI/2);
	
	// Decay production mechanism for (LL) and (HH)
	TH1D* hDPhiLLSc = new TH1D("hDPhiLLSc",Form("%s #Delta#phi correlation for low-low p_{T} from %.1f;#Delta#phi (rad);Counts",title, secondary_status),100,-PI/2,3*PI/2);
	TH1D* hDPhiHHSc = new TH1D("hDPhiHHSc",Form("%s #Delta#phi correlation for high-high p_{T} from %.1f;#Delta#phi (rad);Counts",title, secondary_status),100,-PI/2,3*PI/2);

	// The following histograms are used for combined mother ID and angular correlation studies
	// Delta phi of trigger, associate and mother IDs
	TH2D* hDPhiTrMother = new TH2D("hDPhiTrMother",Form("%s #Delta#phi and trigger mother IDs for all p_{T};#Delta#Phi (rad);trigger mother",title),100,-PI/2,3*PI/2,12001,-6000.5,6000.5);
	TH2D* hDPhiAsMother = new TH2D("hDPhiAsMother",Form("%s #Delta#phi and associate mother IDs for all p_{T};#Delta#Phi (rad);associate mother",title),100,-PI/2,3*PI/2,12001,-6000.5,6000.5);
	TH2D* hDPhiTrMotherLL = new TH2D("hDPhiTrMotherLL",Form("%s #Delta#phi and trigger mother IDs for low-low p_{T};#Delta#Phi (rad);trigger mother",title),100,-PI/2,3*PI/2,12001,-6000.5,6000.5);
	TH2D* hDPhiTrMotherHH = new TH2D("hDPhiTrMotherHH",Form("%s #Delta#phi and trigger mother IDs for high-high p_{T};#Delta#Phi (rad);trigger mother",title),100,-PI/2,3*PI/2,12001,-6000.5,6000.5);
	TH2D* hDPhiAsMotherLL = new TH2D("hDPhiAsMotherLL",Form("%s #Delta#phi and associate mother IDs for low-low p_{T};#Delta#Phi (rad);associate mother",title),100,-PI/2,3*PI/2,12001,-6000.5,6000.5);
	TH2D* hDPhiAsMotherHH = new TH2D("hDPhiAsMotherHH",Form("%s #Delta#phi and associate mother IDs for high-high p_{T};#Delta#Phi (rad);associate mother",title),100,-PI/2,3*PI/2,12001,-6000.5,6000.5);
	
	// Delta phi of mothers and mother IDs
	TH2D* hDPhiOfSameMotherTr = new TH2D("hDPhiOfSameMotherTr",Form("#Delta#phi of mothers and same mother ID %s;#Delta#phi (trigger mother, associate mother) (rad);trigger mother",title),100,-PI/2,3*PI/2,12001,-6000.5,6000.5);
	TH1D *hTrPtSameMother = new TH1D("hTrPtSameMother",Form("Trigger Transverse Momentum for %s for decay with same mother of trigger and associate;p_{T} GeV/c;Counts",title),100,0,50);
	TH2D* hDPhiOfDiffMotherTr = new TH2D("hDPhiOfDiffMotherTr",Form("#Delta#phi of mothers and trigger diff mother ID %s;#Delta#phi (trigger mother, associate mother) (rad);trigger mother",title),100,-PI/2,3*PI/2,12001,-6000.5,6000.5);
	TH2D* hDPhiOfDiffMotherAs = new TH2D("hDPhiOfDiffMotherAs",Form("#Delta#phi of mothers and associate diff mother ID %s;#Delta#phi (trigger mother, associate mother) (rad);associate mother",title),100,-PI/2,3*PI/2,12001,-6000.5,6000.5);
	TH1D *hTrPtDiffMother = new TH1D("hTrPtDiffMother",Form("Trigger Transverse Momentum for %s for decay with different mothers of trigger and associate;p_{T} GeV/c;Counts",title),100,0,50);

	// Prompt/non-prompt or vice-versa combinations of trigger and associate
	// Done in combination with prompt/prompt and non-prompt/non-prompt studies above
	TH1D* hDPhiPrSc = new TH1D("hDPhiPrSc",Form("%s #Delta#phi correlations with prompt/non-prompt or vv production mechanism for all p_{T};#Delta#Phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D* hDPhiLLPrSc = new TH1D("hDPhiLLPrSc",Form("%s #Delta#phi correlations with prompt/non-prompt or vv production mechanism for low-low p_{T};#Delta#Phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D* hDPhiHHPrSc = new TH1D("hDPhiHHPrSc",Form("%s #Delta#phi correlations with prompt/non-prompt or vv production mechanism for high-high p_{T};#Delta#Phi (rad);Counts",title),100,-PI/2,3*PI/2);
	TH1D *hTrPtLLPr = new TH1D("hTrPtLLPr",Form("Trigger Transverse Momentum for %s from %.1f for low-low p_{T};p_{T} GeV/c;Counts",title,primary_status),100,0,50);
        TH1D *hTrPtLLSc = new TH1D("hTrPtLLSc",Form("Trigger Transverse Momentum for %s from %.1f for low-low p_{T};p_{T} GeV/c;Counts",title,secondary_status),100,0,50);
        TH1D *hTrPtLLPrSc = new TH1D("hTrPtLLPrSc",Form("Trigger Transverse Momentum for %s from %.1f and %.1f for low-low p_{T};p_{T} GeV/c;Counts",title,primary_status,secondary_status),100,0,50);
        TH1D *hTrPtHHPr = new TH1D("hTrPtHHPr",Form("Trigger Transverse Momentum for %s from %.1f for high-high p_{T};p_{T} GeV/c;Counts",title,primary_status),100,0,50);
        TH1D *hTrPtHHSc = new TH1D("hTrPtHHSc",Form("Trigger Transverse Momentum for %s from %.1f for high-high p_{T};p_{T} GeV/c;Counts",title,secondary_status),100,0,50);
        TH1D *hTrPtHHPrSc = new TH1D("hTrPtHHPrSc",Form("Trigger Transverse Momentum for %s from %.1f and %.1f for high-high p_{T};p_{T} GeV/c;Counts",title,primary_status,secondary_status),100,0,50);

	// Event Loop
	// Retrieve variables for trigger particle from event, naming is straight-forward
	for( int iEvent = 0; iEvent < nEvents; iEvent++ ) {
		ch1->GetEntry(iEvent);
		int nparticles = vID->size();

		for( int ipart = 0; ipart < nparticles; ipart++ ) {
			pID = (*vID)[ipart];
			pPhi = (*vPhi)[ipart];
			pPt = (*vPt)[ipart];
			pStatus = (*vStatus)[ipart];
			pEta = (*vEta)[ipart];
			pY = (*vY)[ipart];
			pMother = (*vMother1)[ipart];
			pMotherPhi = (*vPhi)[pMother];
			pMotherID = (*vMotherID)[ipart];
				
			if( pID == id_trigger && pPt > 1.) {

			        // This can be enabled to allow only prompt states (even excluding excited states)                                                                                                                                                               
			        if(!(81 <= pStatus && pStatus <= 89)) { continue; }

			        // This can be enabled to allow only non-prompt states (including excited states?)                                                                                                                                                                
			        // if(!(91 <= pStatus && pStatus <= 99)) { continue; } 

			        nTrigger++;
			        hTrPtEta->Fill(pPt,pEta);
				hTrPtY->Fill(pPt,pY);
				hEtaTr->Fill(pEta);
				hYTr->Fill(pY);
				hTrPt->Fill(pPt);

				// *** --------- *** //

				// Filling trigger spectra for multiplicity range correlations
				if(MULTIPLICITY <= multCrit80) { hTrPtM80_100->Fill(pPt);
				} // End of 80-100 % centrality bin
				
				if(multCrit80 < MULTIPLICITY && MULTIPLICITY <= multCrit60) { hTrPtM60_80->Fill(pPt);
				} // End of 60-80 % centrality bin
				
				if(multCrit60 < MULTIPLICITY && MULTIPLICITY <= multCrit40) { hTrPtM40_60->Fill(pPt);
				} // End of 40-60 % centrality bin
				
				if(multCrit40 < MULTIPLICITY && MULTIPLICITY <= multCrit20) { hTrPtM20_40->Fill(pPt);
				} // End of 20-40 % centrality bin
				
				if(multCrit20 < MULTIPLICITY && MULTIPLICITY <= multCrit5) { hTrPtM5_20->Fill(pPt);
				} // End of 0-20 % centrality bin
				
				if(multCrit5 < MULTIPLICITY && MULTIPLICITY <= multCrit1) { hTrPtM1_5->Fill(pPt);
				} // End of top 5% of centrality bins
				
				if(MULTIPLICITY >= multCrit1) { hTrPtM1->Fill(pPt);
				} // End of top 1% of centrality bins

				// *** --------- *** //

				// Filling trigger spectra for triger momentum range correlations
				if(pPt >= 1. && pPt < 3.) { hTrPtL->Fill(pPt);
				} // End of low transverse momentum

				if(pPt >= 3. && pPt < 8.) { hTrPtI->Fill(pPt);
				} // End of intermediate-intermediate transverse momentum
				
				if(pPt >= 8.) { hTrPtH->Fill(pPt);
				} // End of high-high transverse momentum
				
				// *** --------- *** //
				
				// Filling trigger spectra for pseudorapidity range correlations
				if((pEta >= -1.0*etaCrit && pEta <= etaCrit) && (aEta >= -1.0*etaCrit && aEta <= etaCrit)) {
				  hTrPtEtaC->Fill(pPt);
				} // End of backward-backward pseudorapidity range correlations
				
				if((pEta < -1.0*etaCrit || pEta > etaCrit) && (aEta < -1.0*etaCrit || aEta > etaCrit)) {
				  hTrPtEtaF->Fill(pPt);
				} // End of forward-forward pseudorapidity range correlations

				// *** --------- *** //
				
				// Filling trigger spectra for rapidity range correlations
				if((pY >= -1.0*yCrit && pY <= yCrit) && (aY >= -1.0*yCrit && aY <= yCrit)) {
				  hTrPtYC->Fill(pPt);
				} // End of backward-backward rapidity range correlations                                                                                                                     
				if((pY < -1.0*yCrit || pY > yCrit) && (aY < -1.0*yCrit || aY > yCrit)) {
				  hTrPtYF->Fill(pPt);
				} // End of forward-forward rapidity range correlations

				// *** --------- *** //

				// Now try to find an associate and get its properties
				for( int jpart = 0; jpart < nparticles; jpart++ ) {
					if( jpart == ipart ) continue; // Do not correlate with itself
						aID = (*vID)[jpart];
						aPhi = (*vPhi)[jpart];
						aPt = (*vPt)[jpart];
						aStatus = (*vStatus)[jpart];
						aEta = (*vEta)[jpart];
						aY = (*vY)[jpart];
						aMother = (*vMother1)[jpart];
						aMotherPhi = (*vPhi)[aMother];
						aMotherID = (*vMotherID)[jpart];

						if( aID == id_associate && aPt > 1.) {

						  // This can be enabled to allow only prompt states (even excluding excited states)                                                                                                                                              
                                                  if(!(81 <= aStatus && aStatus <= 89)) { continue; }

                                                  // This can be enabled to allow only non-prompt states (including excited states?)                                                                                                                                              
                                                  // if(!(91 <= aStatus && aStatus <= 99)) {continue; }

						  hEtaAs->Fill(aEta);
						  hYAs->Fill(aY);
						  hDPhi->Fill(DeltaPhi(pPhi,aPhi));
						  hDPhiTrMother->Fill(DeltaPhi(pPhi,aPhi),pMotherID);
						  hDPhiAsMother->Fill(DeltaPhi(pPhi,aPhi),aMotherID);

						  if( 81 <= pStatus && pStatus <= 89 &&  81 <= aStatus && aStatus <= 89 ) { // Hadronisation production mechanism
						    hTrPtPr->Fill(pPt); // normalisation method inconsistent with other trigger pT !!! (kept like this for consistency with former plots, but needs to be addressed)
						    hDPhiPr->Fill(DeltaPhi(pPhi,aPhi));
						  }
						  
						  if( 91 <= pStatus && pStatus <= 99 &&  91 <= aStatus && aStatus <= 99 ) { // Decay production mechanism
						    hTrPtSc->Fill(pPt);
						    hDPhiSc->Fill(DeltaPhi(pPhi,aPhi));

						    if ( pMother == aMother) { 
						      hDPhiOfSameMotherTr->Fill(DeltaPhi(pMotherPhi, aMotherPhi), pMotherID); 
						      hTrPtSameMother->Fill(pPt);
						    }
						    if ( pMother != aMother) { 
						      hDPhiOfDiffMotherTr->Fill(DeltaPhi(pMotherPhi, aMotherPhi), pMotherID); 
						      hDPhiOfDiffMotherAs->Fill(DeltaPhi(pMotherPhi, aMotherPhi), aMotherID);
						      hTrPtDiffMother->Fill(pPt);
						    }
						  } // prompt/non-prompt
						  
						  if ( 81 <= pStatus && pStatus <= 89 && 91 <= aStatus && aStatus <= 99) { 
						    hDPhiPrSc->Fill(DeltaPhi(pPhi,aPhi)); 
						    hTrPtPrSc->Fill(pPt);
						  } // non-prompt/prompt
						  if ( 91 <= pStatus && pStatus <= 99 && 81 <= aStatus && aStatus <= 89) { 
						    hDPhiPrSc->Fill(DeltaPhi(pPhi,aPhi)); 
						    hTrPtPrSc->Fill(pPt);
						  }

						  // *** --------- *** // 

						  // Filling multiplicity range correlations
						  if(MULTIPLICITY <= multCrit80) {
						    hDPhiM80_100->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of 80-100 % centrality bin
						    
						  if(multCrit80 < MULTIPLICITY && MULTIPLICITY <= multCrit60) {
						    hDPhiM60_80->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of 60-80 % centrality bin
						    
						  if(multCrit60 < MULTIPLICITY && MULTIPLICITY <= multCrit40) {
						    hDPhiM40_60->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of 40-60 % centrality bin
						    
						  if(multCrit40 < MULTIPLICITY && MULTIPLICITY <= multCrit20) {
						    hDPhiM20_40->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of 20-40 % centrality bin
						    
						  if(multCrit20 < MULTIPLICITY && MULTIPLICITY <= multCrit5) {
						    hDPhiM5_20->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of 0-20 % centrality bin
						    
						  if(multCrit5 < MULTIPLICITY && MULTIPLICITY <= multCrit1) {
						    hDPhiM1_5->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of top 5% of centrality bins
						    
						  if(MULTIPLICITY >= multCrit1) {
						    hDPhiM1->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of top 1% of centrality bins


						  // *** --------- *** //

						  // Filling momentum range correlations
						  if(pPt >= 1. && pPt < 3. && aPt > 1. && aPt < 3.) {
						    hDPhiLL->Fill(DeltaPhi(pPhi,aPhi));
						    hDPhiTrMotherLL->Fill(DeltaPhi(pPhi,aPhi),pMotherID);
						    hDPhiAsMotherLL->Fill(DeltaPhi(pPhi,aPhi),aMotherID);
						    if( 81 <= pStatus && pStatus <= 89 && 81 <= aStatus && aStatus <= 89 ) { hDPhiLLPr->Fill(DeltaPhi(pPhi,aPhi)); hTrPtLLPr->Fill(pPt); } // also here: normalisation needs fixing!
						    if( 91 <= pStatus && pStatus <= 99 && 91 <= aStatus && aStatus <= 99 ) { hDPhiLLSc->Fill(DeltaPhi(pPhi,aPhi)); hTrPtLLSc->Fill(pPt); }
						    if( 81 <= pStatus && pStatus <= 89 && 91 <= aStatus && aStatus <= 99 ) { hDPhiLLPrSc->Fill(DeltaPhi(pPhi,aPhi)); hTrPtLLPrSc->Fill(pPt); } // prompt/non-prompt
						    if( 91 <= pStatus && pStatus <= 99 && 81 <= aStatus && aStatus <= 89 ) { hDPhiLLPrSc->Fill(DeltaPhi(pPhi,aPhi)); hTrPtLLPrSc->Fill(pPt); } // non-prompt/prompt
						  } // End of low-low transverse momentum

						  if(pPt >= 1. && pPt < 3. && aPt >= 3. && aPt < 8.) {
						    hDPhiLI->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of low-intermediate transverse momentum

						  if(pPt >= 1. && pPt < 3. && aPt >= 8.) {
						    hDPhiLH->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of low-high transverse momentum
						  
						  if(pPt >= 3. && pPt < 8. && aPt > 1. && aPt < 3.) {
						    hDPhiIL->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of intermediate-low transverse momentum

						  if(pPt >= 3. && pPt < 8. && aPt >= 3. && aPt < 8.) {
						    hDPhiII->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of intermediate-intermediate momentum

						  if(pPt >= 3. && pPt < 8. && aPt >= 8.) {
						    hDPhiIH->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of intermediate-high momentum
						  
						  if(pPt >= 8. && aPt > 1. && aPt < 3.) {
						    hDPhiHL->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of high-low transverse momentum
						  
						  if(pPt >= 8. && aPt >=3. && aPt < 8.) {
						    hDPhiHI->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of high-intermediate transverse momentum
						  
						  if(pPt >= 8. && aPt >= 8.) {
						    hDPhiHH->Fill(DeltaPhi(pPhi,aPhi));
						    hDPhiTrMotherHH->Fill(DeltaPhi(pPhi,aPhi),pMotherID);
						    hDPhiAsMotherHH->Fill(DeltaPhi(pPhi,aPhi),aMotherID);
						    if( 81 <= pStatus && pStatus <= 89 && 81 <= aStatus && aStatus <= 89 ) { hDPhiHHPr->Fill(DeltaPhi(pPhi,aPhi)); hTrPtHHPr->Fill(pPt); }
						    if( 91 <= pStatus && pStatus <= 99 && 91 <= aStatus && aStatus <= 99 ) { hDPhiHHSc->Fill(DeltaPhi(pPhi,aPhi)); hTrPtHHSc->Fill(pPt); }
						    if( 81 <= pStatus && pStatus <= 89 && 91 <= aStatus && aStatus <= 99 ) { hDPhiHHPrSc->Fill(DeltaPhi(pPhi,aPhi)); hTrPtHHPrSc->Fill(pPt); } 	 
						    if( 91 <= pStatus && pStatus <= 99 && 81 <= aStatus && aStatus <= 89 ) { hDPhiHHPrSc->Fill(DeltaPhi(pPhi,aPhi)); hTrPtHHPrSc->Fill(pPt); } 
						  } // End of high-high transverse momentum
						  
						  // *** --------- *** //

						  // Filling pseudorapidity range correlations
						  if((pEta >= -1.0*etaCrit && pEta <= etaCrit) && (aEta >= -1.0*etaCrit && aEta <= etaCrit)) {
						    hDPhiEtaCC->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of backward-backward pseudorapidity range correlations

						  if((pEta >= -1.0*etaCrit && pEta <= etaCrit) && (aEta < -1.0*etaCrit || aEta > etaCrit)) {
						    hDPhiEtaCF->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of backward-forward pseudorapidity range correlations 
						  
						  if((pEta < -1.0*etaCrit || pEta > etaCrit) && (aEta >= -1.0*etaCrit && aEta <= etaCrit)) {
						    hDPhiEtaFC->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of forward-backward pseudorapidity range correlations 
						  
						  if((pEta < -1.0*etaCrit || pEta > etaCrit) && (aEta < -1.0*etaCrit || aEta > etaCrit)) {
						    hDPhiEtaFF->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of forward-forward pseudorapidity range correlations
						  
						  // Filling rapidity range correlations
						  if((pY >= -1.0*yCrit && pY <= yCrit) && (aY >= -1.0*yCrit && aY <= yCrit)) {
						    hDPhiYCC->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of backward-backward rapidity range correlations
						  
						  if((pY >= -1.0*yCrit && pY <= yCrit) && (aY < -1.0*yCrit || aY > yCrit)) {
						    hDPhiYCF->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of backward-forward rapidity range correlations
						  
						  if((pY < -1.0*yCrit || pY > yCrit) && (aY >= -1.0*yCrit && aY <= yCrit)) {
						    hDPhiYFC->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of forward-backward rapidity range correlations
						  
						  if((pY < -1.0*yCrit || pY > yCrit) && (aY < -1.0*yCrit || aY > yCrit)) {
						    hDPhiYFF->Fill(DeltaPhi(pPhi,aPhi));
						  } // End of forward-forward rapidity range correlations 
							
						} // Associate Condition	
				} // Associate Loop
			} // Trigger Codition
		} // Trigger Loop
	} // End of event loop
	
	if(nTrigger == 0){
		cout<<"Have not found any trigger particle with id: "<<id_trigger<<endl;
		output->Close();
		return;
	}
	output->Write();
	output->Close();
	cout<<"The total number of triggers is: "<<nTrigger<<endl;
	
	cout<<"File: "<<filename<<" has been created!"<<endl;
}


int status_analysis_cc() {

        // Trigger and associate can be chosen as desired, correlations will be created and put into the output ROOT file as named in the function argument 

        // TRIGGER = D+  

	status_file(411,411,"DplusDplus.root","D^{+}D^{+}");
	status_file(411,-411,"DplusDminus.root","D^{+}D^{-}");
	status_file(411,421,"DplusDzero.root","D^{+}D^{0}");
	status_file(411,-421,"DplusDzerobar.root","D^{+}#barD^{0}");
	status_file(411,431,"DplusDsplus.root","D^{+}D_{s}^{+}");
	status_file(411,-431,"DplusDsminus.root","D^{+}D_{s}^{-}");
	status_file(411,4122,"DplusLambdacplus.root","D^{+}#Lambda_{c}^{+}");
	status_file(411,-4122,"DplusLambdacplusbar.root","D^{+}#bar#Lambda_{c}^{+}");
	status_file(411,4222,"DplusSigmacplusplus.root","D^{+}#Sigma_{c}^{++}");
	status_file(411,-4222,"DplusSigmacplusplusbar.root","D^{+}#bar#Sigma_{c}^{++}");
	status_file(411,4212,"DplusSigmacplus.root","D^{+}#Sigma_{c}^{+}");
	status_file(411,-4212,"DplusSigmacplusbar.root","D^{+}#bar#Sigma_{c}^{+}");
	status_file(411,4112,"DplusSigmaczero.root","D^{+}#Sigma_{c}^{0}");
	status_file(411,-4112,"DplusSigmaczerobar.root","D^{+}#bar#Sigma_{c}^{0}");

	/*
	// TRIGGER = D-

	status_file(-411,411,"DminusDplus.root","D^{-}D^{+}");
	status_file(-411,-411,"DminusDminus.root","D^{-}D^{-}");
	status_file(-411,421,"DminusDzero.root","D^{-}D^{0}");
	status_file(-411,-421,"DminusDzerobar.root","D^{-}#barD^{0}");
	status_file(-411,431,"DminusDsplus.root","D^{-}D_{s}^{+}");
	status_file(-411,-431,"DminusDsminus.root","D^{-}D_{s}^{-}");
	status_file(-411,4122,"DminusLambdacplus.root","D^{-}#Lambda_{c}^{+}");
	status_file(-411,-4122,"DminusLambdacplusbar.root","D^{-}#bar#Lambda_{c}^{+}");
	status_file(-411,4222,"DminusSigmacplusplus.root","D^{-}#Sigma_{c}^{++}");
	status_file(-411,-4222,"DminusSigmacplusplusbar.root","D^{-}#bar#Sigma_{c}^{++}");
	status_file(-411,4212,"DminusSigmacplus.root","D^{-}#Sigma_{c}^{+}");
	status_file(-411,-4212,"DminusSigmacplusbar.root","D^{-}#bar#Sigma_{c}^{+}");
	status_file(-411,4112,"DminusSigmaczero.root","D^{-}#Sigma_{c}^{0}");
	status_file(-411,-4112,"DminusSigmaczerobar.root","D^{-}#bar#Sigma_{c}^{0}");

	// TRIGGER = Lc+

	status_file(4122,411,"LambdacplusDplus.root","#Lambda_{c}^{+}D^{+}");
	status_file(4122,-411,"LambdacplusDminus.root","#Lambda_{c}^{+}D^{-}");
	status_file(4122,421,"LambdacplusDzero.root","#Lambda_{c}^{+}D^{0}");
	status_file(4122,-421,"LambdacplusDzerobar.root","#Lambda_{c}^{+}#barD^{0}");
	status_file(4122,431,"LambdacplusDsplus.root","#Lambda_{c}^{+}D_{s}^{+}");
	status_file(4122,-431,"LambdacplusDsminus.root","#Lambda_{c}^{+}D_{s}^{-}");
	status_file(4122,4122,"LambdacplusLambdacplus.root","#Lambda_{c}^{+}#Lambda_{c}^{+}");
	status_file(4122,-4122,"LambdacplusLambdacplusbar.root","#Lambda_{c}^{+}#bar#Lambda_{c}^{+}");
	status_file(4122,4222,"LambdacplusSigmacplusplus.root","#Lambda_{c}^{+}#Sigma_{c}^{++}");
	status_file(4122,-4222,"LambdacplusSigmacplusplusbar.root","Lambda_{c}^{+}#bar#Sigma_{c}^{++}");
        status_file(4122,4212,"LambdacplusSigmacplus.root","#Lambda_{c}^{+}#Sigma_{c}^{+}");
        status_file(4122,-4212,"LambdacplusSigmacplusbar.root","#Lambda_{c}^{+}#bar#Sigma_{c}^{+}");
        status_file(4122,4112,"LambdacplusSigmaczero.root","#Lambda_{c}^{+}#Sigma_{c}^{0}");
        status_file(4122,-4112,"LambdacplusSigmaczerobar.root","#Lambda_{c}^{+}#bar#Sigma_{c}^{0}");

	// TRIGGER = Lc+bar

	status_file(-4122,411,"LambdacplusbarDplus.root","#bar#Lambda_{c}^{+}D^{+}");
        status_file(-4122,-411,"LambdacplusbarDminus.root","#bar#Lambda_{c}^{+}D^{-}");
        status_file(-4122,421,"LambdacplusbarDzero.root","#bar#Lambda_{c}^{+}D^{0}");
        status_file(-4122,-421,"LambdacplusbarDzerobar.root","#bar#Lambda_{c}^{+}#barD^{0}");
        status_file(-4122,431,"LambdacplusbarDsplus.root","#bar#Lambda_{c}^{+}D_{s}^{+}");
        status_file(-4122,-431,"LambdacplusbarDsminus.root","#bar#Lambda_{c}^{+}D_{s}^{-}");
        status_file(-4122,4122,"LambdacplusbarLambdacplus.root","#bar#Lambda_{c}^{+}#Lambda_{c}^{+}");
        status_file(-4122,-4122,"LambdacplusbarLambdacplusbar.root","#bar#Lambda_{c}^{+}#bar#Lambda_{c}^{+}");
	status_file(-4122,4222,"LambdacplusbarSigmacplusplus.root","#bar#Lambda_{c}^{+}#Sigma_{c}^{++}");
	status_file(-4122,-4222,"LambdacplusbarSigmacplusplusbar.root","#barLambda_{c}^{+}#bar#Sigma_{c}^{++}");
        status_file(-4122,4212,"LambdacplusbarSigmacplus.root","#bar#Lambda_{c}^{+}#Sigma_{c}^{+}");
        status_file(-4122,-4212,"LambdacplusbarSigmacplusbar.root","#bar#Lambda_{c}^{+}#bar#Sigma_{c}^{+}");
        status_file(-4122,4112,"LambdacplusbarSigmaczero.root","#bar#Lambda_{c}^{+}#Sigma_{c}^{0}");
        status_file(-4122,-4112,"LambdacplusbarSigmaczerobar.root","#bar#Lambda_{c}^{+}#bar#Sigma_{c}^{0}");
	*/
	

	return 0;
}

