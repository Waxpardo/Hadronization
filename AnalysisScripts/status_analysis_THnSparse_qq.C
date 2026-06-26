// status_analysis_qq.C
// ROOT macro that creates azimuthal angular correlations on a given trigger and associate particle pair using input simulated with PYTHIA as in the script bbbarcorrelations_status.cpp
// Histograms are created for the angular correlations of the trigger and associate and saved to an output ROOT file.
// This script is focussed on beauty and charm hadrons and includes histograms for different pT regions and has a possibility to investigate pseudorapidity dependence and production mechanisms for beauty correlations.
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

Double_t DeltaPhi(Double_t phi1, Double_t phi2)
{
	// Returns delta phi in range (-pi/2 3pi/2)
	// Specific range is used to make the near- and away-side peak more visible
	return fmod(phi1 - phi2 + 2.5 * PI, 2 * PI) - 0.5 * PI;
}

void status_file(Int_t id_trigger, Int_t id_associate, const char *fIn, const char *fOut, const char *outputDir, const char *title)
{
	// This functions takes the trigger and associate id and creates a ROOT output file with the same filename
	// containing the histograms produced in this macro

	// Define the TChain
	TChain *ch1 = new TChain("tree");
	TFile *output = new TFile(Form("%s/%s", outputDir, fOut), "RECREATE");

	// OPTION 1: SINGLE FILE
	ch1->Add(fIn);

	// OPTION 2: BATCH FILE STRUCTURE
	// Number of trees to be added to the TChain
	// This can be changed by the user
	/*
	int ntrees = 25;

	for( int i = 1; i < ntrees+1;  i++) {
	// One can change the file path accordingly
	  ch1->Add(Form("Group%i/output.root",i)); // Group%i/output.root
	}
	// COMMENT TILL THIS LINE TO DISABLE OPTION 2
	*/

	// *** --------- ***

	// First retrieve the event information histograms that are produced in the Pythia simulations
	// Can be made into a function that takes the histograms from the TCHain and adds them
	TH1D *hMULTIPLICITY = 0;

	for (Int_t iEntry = 0; iEntry < ch1->GetNtrees(); iEntry++)
	{

		ch1->GetEntry(iEntry);
		TFile *currentFile = ch1->GetCurrentFile();
		TH1D *hEntryMULTIPLICITY = (TH1D *)currentFile->Get("hMULTIPLICITY");

		if (!hMULTIPLICITY)
		{
			hMULTIPLICITY = (TH1D *)hEntryMULTIPLICITY->Clone("summed MULTIPLICITY");
			hMULTIPLICITY->Reset();
		}

		hMULTIPLICITY->Add(hEntryMULTIPLICITY);
	}

	// cout << "integral = " << hTotMULTIPLICITY->Integral() << endl;

	// Now we define vectors that carry the information at event level
	vector<Int_t> *vID = 0;
	vector<Double_t> *vPt = 0;
	vector<Double_t> *vPhi = 0;
	vector<Double_t> *vCharge = 0;
	vector<Double_t> *vStatus = 0;
	vector<Double_t> *vEta = 0;
	vector<Double_t> *vY = 0;
	vector<Double_t> *vMother1 = 0;
	vector<Double_t> *vMotherID = 0;
	Int_t nMPIs = 0;
	Int_t MULTIPLICITY = 0;
	// Int_t nJets = 0;

	// Setting up chain branch addresses to the vectors defined above
	ch1->SetBranchAddress("ID", &vID);
	ch1->SetBranchAddress("PT", &vPt);
	ch1->SetBranchAddress("PHI", &vPhi);
	ch1->SetBranchAddress("CHARGE", &vCharge);
	ch1->SetBranchAddress("ETA", &vEta);
	ch1->SetBranchAddress("Y", &vY);
	ch1->SetBranchAddress("STATUS", &vStatus);
	ch1->SetBranchAddress("MOTHER", &vMother1);
	ch1->SetBranchAddress("MOTHERID", &vMotherID);
	ch1->SetBranchAddress("nMPIs", &nMPIs);
	ch1->SetBranchAddress("MULTIPLICITY", &MULTIPLICITY);
	// ch1->SetBranchAddress("nJets", &nJets);

	// Variables used in this script
	// p indicates trigger particle variables
	// a indicates associate particle variables
	Int_t aID, pID;
	Double_t px, py;
	Double_t pPt, pPhi, pCharge, pStatus, pEta, pY, pMother, pMotherPhi, pMotherID;
	Double_t aPt, aPhi, aCharge, aStatus, aEta, aY, aMother, aMotherPhi, aMotherID;
	int nTrigger = 0;

	// Besides pT dependence, it is also interesting to look at the data as a function of multiplicity and (pseudo)rapidity
	// Classification is set here, first for pseudorapidity and rapidity, and then for multiplicity:
	// (F) Forward > abs(etaCrit), (C) Central < abs(etaCrit)
	Double_t etaCrit = 2; // pseudorapidity
	Double_t yCrit = 2;	  // rapidity

	// The multiplicity cuts are defined using the percentiles of the total multiplicity
	Double_t multCrit0, multCrit20, multCrit40, multCrit60, multCrit80; // To be filled with multiplicity (careful: it's analogous to centrality, so 80_100 is the 20% lowest multiplicious events
	Bool_t flag0_20 = true;
	Bool_t flag20_40 = true;
	Bool_t flag40_60 = true;
	Bool_t flag60_80 = true;
	Bool_t flag80_100 = true;	   // Flags are used so that only one for loop is necessary
	Double_t multCrit1, multCrit5; // Specific selection cuts for top 1% and top 5% of multiplicity events
	Bool_t flag1 = true;
	Bool_t flag5 = true;
	Int_t fullIntegral = 0;
	Int_t currentIntegral = 0;

	// Calculation of multiplicity percentiles
	fullIntegral = hMULTIPLICITY->Integral();

	for (Int_t i = 0; i <= hMULTIPLICITY->GetNbinsX(); i++)
	{

		currentIntegral += hMULTIPLICITY->GetBinContent(i);

		if (flag80_100 && currentIntegral >= 0.2 * fullIntegral)
		{
			multCrit80 = hMULTIPLICITY->GetBinCenter(i);
			flag80_100 = false;
		}

		if (flag60_80 && currentIntegral >= 0.4 * fullIntegral)
		{
			multCrit60 = hMULTIPLICITY->GetBinCenter(i);
			flag60_80 = false;
		}

		if (flag40_60 && currentIntegral >= 0.6 * fullIntegral)
		{
			multCrit40 = hMULTIPLICITY->GetBinCenter(i);
			flag40_60 = false;
		}

		if (flag20_40 && currentIntegral >= 0.8 * fullIntegral)
		{
			multCrit20 = hMULTIPLICITY->GetBinCenter(i);
			flag20_40 = false;
		}

		if (flag5 && currentIntegral >= 0.95 * fullIntegral)
		{
			multCrit5 = hMULTIPLICITY->GetBinCenter(i);
			flag5 = false;
		}

		if (flag1 && currentIntegral >= 0.99 * fullIntegral)
		{
			multCrit1 = hMULTIPLICITY->GetBinCenter(i);
			flag1 = false;
		}
	}

	// There is a possiblity to change status settings for production studies
	// This is only used to double-check whether these histograms are consistent with their status
	// They can be removed from this script or the title of the plots can be changed in drawing scripts
	// This is not used for beauty angular correlations, but the settings can be changed easily to allow for a different production study
	Double_t primary_status = 83;
	Double_t secondary_status = 91;

	// Indicate the total number of events analysed
	int nEvents = ch1->GetEntries();
	cout << "The number of events for this analysis is: " << nEvents << endl;

	// Definitions of produced histograms
	// The histograms are divided into two categories: angular correlations and trigger spectra, the latter can be integrated over in local scripts to obtain the total number of triggers, which the yield is then normalised over.
	// The naming convention is as follows:
	// h = histogram
	// TrPt = trigger spectra
	// DPhi = Delta phi (angular correlations)
	// Pr = primary status, Sc = secondary status (production mechanisms)

	// Set up the THnSparses for single particle kinematics and for correlations
	// φ η pT mult
	Int_t nBinsSingle[4] = {100, 100, 100, 100};
	Double_t vMinSingle[4] = {-PI / 2, -4, 0, 0};
	Double_t vMaxSingle[4] = {3 * PI / 2, 4, 50, 400};
	THnSparseD *hTrKinematics = new THnSparseD("hTrKinematics", "hTrKinematics (phi, eta, pt, mult)", 4, nBinsSingle, vMinSingle, vMaxSingle);
	THnSparseD *hAsKinematics = new THnSparseD("hAsKinematics", "hAsKinematics (phi, eta, pt, mult)", 4, nBinsSingle, vMinSingle, vMaxSingle);
	hTrKinematics->GetAxis(0)->SetTitle("#phi");
	hTrKinematics->GetAxis(1)->SetTitle("#eta");
	hTrKinematics->GetAxis(2)->SetTitle("p_{T} (GeV/c)");
	hTrKinematics->GetAxis(3)->SetTitle("Multiplicity");
	hAsKinematics->GetAxis(0)->SetTitle("#phi");
	hAsKinematics->GetAxis(1)->SetTitle("#eta");
	hAsKinematics->GetAxis(2)->SetTitle("p_{T} (GeV/c)");
	hAsKinematics->GetAxis(3)->SetTitle("Multiplicity");

	// Δφ Δη TrPt AsPt mult
	// TODO: to be complete, one should add also the TrEta and AsEta
	Int_t nBinsCorr[7] = {100, 100, 100, 100, 100, 100, 100};
	Double_t vMinCorr[7] = {-PI / 2, -8, -4, -4, 0, 0, 0};
	Double_t vMaxCorr[7] = {3 * PI / 2, 8, 4, 4, 50, 50, 400};
	THnSparseD *hCorrelations = new THnSparseD("hCorrelations", "hCorrelations (dPhi, dEta, trEta, asEta trPt, asPt, mult)", 7, nBinsCorr, vMinCorr, vMaxCorr);
	hCorrelations->GetAxis(0)->SetTitle("#Delta#phi");
	hCorrelations->GetAxis(1)->SetTitle("#Delta#eta");
	hCorrelations->GetAxis(2)->SetTitle("#eta^{trig}");
	hCorrelations->GetAxis(3)->SetTitle("#eta^{assoc}");
	hCorrelations->GetAxis(4)->SetTitle("p_{T}^{trig} (GeV/c)");
	hCorrelations->GetAxis(5)->SetTitle("p_{T}^{assoc} (GeV/c)");
	hCorrelations->GetAxis(6)->SetTitle("Multiplicity");

	// Event loop - DPhi spectra
	// Retrieve variables for trigger particle from event, naming is straight-forward
	for (int iEvent = 0; iEvent < nEvents; iEvent++)
	{
		ch1->GetEntry(iEvent);
		int nparticles = vID->size();

		for (int ipart = 0; ipart < nparticles; ipart++)
		{
			pID = (*vID)[ipart];
			pPhi = (*vPhi)[ipart];
			pPt = (*vPt)[ipart];
			pStatus = (*vStatus)[ipart];
			pEta = (*vEta)[ipart];
			pY = (*vY)[ipart]; // not to be confused with the y-component of the momentum, denoted py!
			pMother = (*vMother1)[ipart];
			pMotherPhi = (*vPhi)[pMother];
			pMotherID = (*vMotherID)[ipart];

			if (pID == id_trigger && pPt >= 1.)
			{
				// All mothers in the non junctions charm sample for D+ are excited D states?
				// To include them or not?

				// This can be enabled to allow only prompt states (even excluding excited states)
				// if(!(81 <= pStatus && pStatus <= 89)) { continue; }
				// std::cout << "pID = " << pID << ", pStatus = " << pStatus << " and pMotherID = " << pMotherID << std::endl;

				// This can be enabled to allow only non-prompt states (including excited states?)
				// if(!(91 <= pStatus && pStatus <= 99)) { continue; }

				nTrigger++;
				Double_t vValuesTr[4] = {pPhi, pEta, pPt, static_cast<Double_t>(MULTIPLICITY)};
				hTrKinematics->Fill(vValuesTr);

				// Now try to find an associate and get its properties
				for (int jpart = 0; jpart < nparticles; jpart++)
				{
					if (jpart == ipart)
						continue; // Do not correlate with it self
					aID = (*vID)[jpart];
					aPhi = (*vPhi)[jpart];
					aPt = (*vPt)[jpart];
					aStatus = (*vStatus)[jpart];
					aEta = (*vEta)[jpart];
					aY = (*vY)[jpart];
					aMother = (*vMother1)[jpart];
					aMotherPhi = (*vPhi)[aMother];
					aMotherID = (*vMotherID)[jpart];

					if (aID == id_associate && aPt >= 1.)
					{

						// This can be enabled to allow only prompt states (even excluding excited states)
						if (!(81 <= aStatus && aStatus <= 89))
						{
							continue;
						}

						// This can be enabled to allow only non-prompt states (including excited states?)
						// if(!(91 <= aStatus && aStatus <= 99)) {continue; }

						Double_t vValuesAs[4] = {aPhi, aEta, aPt, static_cast<Double_t>(MULTIPLICITY)};
						Double_t vValuesCorr[7] = {DeltaPhi(pPhi, aPhi), (pEta-aEta), pEta, aEta, pPt, aPt, static_cast<Double_t>(MULTIPLICITY)};
						hAsKinematics->Fill(vValuesAs);
						hCorrelations->Fill(vValuesCorr);

					} // Associate Condition
				} // Associate Loop
			} // Trigger Codition
		} // Trigger Loop
	} // End of event loop

	if (nTrigger == 0)
	{
		cout << "Have not found any trigger particle with id: " << id_trigger << endl;
		output->Close();
		return;
	}
	hTrKinematics->Write();
	hAsKinematics->Write();
	hCorrelations->Write();
	output->Write();
	output->Close();
	cout << "The total number of triggers is: " << nTrigger << endl;

	cout << "File: " << fOut << " has been created!" << endl;
}

int status_analysis_THnSparse_qq(const char *fIn, const char *outputDir)
{

	// Trigger and associate can be chosen as desired, correlations will be created and put into the output ROOT file as named in the function argument

	// TRIGGER = D+

	status_file(411, 411, fIn, "DplusDplus.root", outputDir, "D^{+}D^{+}");
	status_file(411, -411, fIn, "DplusDminus.root", outputDir, "D^{+}D^{-}");
	status_file(411, 4122, fIn, "DplusLambdacplus.root", outputDir, "D^{+}#Lambda_{c}^{+}");
	status_file(411, -4122, fIn, "DplusLambdacplusbar.root", outputDir, "D^{+}#bar#Lambda_{c}^{+}");
	// status_file(411, 4212, fIn, "DplusSigmacplus.root", outputDir, "D^{+}#Sigma_{c}^{+}");
	// status_file(411, -4212, fIn, "DplusSigmacplusbar.root", outputDir, "D^{+}#bar#Sigma_{c}^{+}");

	// TRIGGER = B+
	status_file(521,521, fIn, "BplusBplus.root", outputDir, "B^{+}B^{+}");
	status_file(521, -521, fIn, "BplusBminus.root", outputDir, "B^{+}B^{-}");
	status_file(521, 5122, fIn, "BplusLb.root", outputDir, "B^{+}#Lambda_{b}^{0}");
	status_file(521, -5122, fIn, "BplusLbbar.root", outputDir, "B^{+}#bar#Lambda_{b}^{0}");
	status_file(521, 5212, fIn, "BplusSigmabzero.root", outputDir, "B^{+}#Sigma_{b}^{0}");
	status_file(521, -5212, fIn, "BplusSigmabzerobar.root", outputDir, "B^{+}#bar#Sigma_{b}^{0}");

	return 0;
}
