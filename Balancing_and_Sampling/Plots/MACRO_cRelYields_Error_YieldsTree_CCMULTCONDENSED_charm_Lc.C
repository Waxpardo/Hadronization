#ifdef __CLING__
#pragma cling optimize(0)
#endif
void MACRO_cRelYields_Error_YieldsTree_CCMULTCONDENSED_charm_Lc()
{
//=========Macro generated from canvas: cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity/cRelYields
//=========  (Thu Apr 18 16:08:47 2024) by ROOT version 6.28/04
   TCanvas *cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity = new TCanvas("cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity", "cRelYields",2085,109,800,600);
   cRelYields_integrated->Range(0,0,1,1);
   cRelYields_integrated->SetFillColor(0);
   cRelYields_integrated->SetBorderMode(0);
   cRelYields_integrated->SetBorderSize(2);
   cRelYields_integrated->SetLeftMargin(0.15);
   cRelYields_integrated->SetRightMargin(0.25);
   cRelYields_integrated->SetBottomMargin(0.25);
   cRelYields_integrated->SetFrameBorderMode(0);
  
// ------------>Primitives in pad: mainPadRelJunctions_integrated yields for prompt D^{+} trigger as function of multiplicity
   TPad *mainPadRelJunctions_integrated = new TPad("mainPadRelJunctions_integrated yields for prompt D^{+} trigger as function of multiplicity", "mainPad",0.05,0.3,0.95,0.95);
   mainPadRelJunctions_integrated->Draw();
   mainPadRelJunctions_integrated->cd();
   mainPadRelJunctions_integrated->Range(-0.5,0.01,4.5,0.2766667);
   mainPadRelJunctions_integrated->SetFillColor(0);
   mainPadRelJunctions_integrated->SetBorderMode(0);
   mainPadRelJunctions_integrated->SetBorderSize(2);
   mainPadRelJunctions_integrated->SetBottomMargin(0);
   mainPadRelJunctions_integrated->SetFrameBorderMode(0);
   mainPadRelJunctions_integrated->SetFrameBorderMode(0);
   
   TH1D *hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971 = new TH1D("hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971","integrated yields for prompt D^{+} trigger as function of multiplicity",4,0,4);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->SetMinimum(0.01);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->SetMaximum(0.25);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->SetStats(0);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->SetLineColor(ci);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->GetXaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->GetXaxis()->SetLabelSize(0.05);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->GetXaxis()->SetTitleOffset(1);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->GetXaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->GetYaxis()->SetTitle("baryon/meson yield");
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->GetYaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->GetYaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->GetZaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->GetZaxis()->SetTitleOffset(1);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->GetZaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__971->Draw("PE");
   
   TLegend *leg = new TLegend(0.63,0.68,0.9,0.88,NULL,"brNDC");
   leg->SetBorderSize(1);
   leg->SetTextSize(0.03);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   TLegendEntry *entry=leg->AddEntry("NULL","MONASH","l");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("NULL","JUNCTIONS","l");

   ci = TColor::GetColor("#ff0000");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hRelYields_MONASH_integrated yields for prompt D^{+} trigger as function of multiplicity_24_0","D^{+}#bar#Lambda_{c}^{+}/D^{+}D^{-}","l");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972","hRelYields_24_0",4,0,4);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->SetBinContent(1,0.1166751);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->SetBinError(1,0.0009609569);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__972->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973","hRelYields_24_0",4,0,4);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->SetBinContent(1,0.1149187);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->SetBinError(1,0.001082448);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__973->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974","hRelYields_24_1",4,0,4);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->SetBinContent(2,0.096937);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->SetBinError(2,0.001361645);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__974->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975","hRelYields_24_1",4,0,4);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->SetBinContent(2,0.1127716);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->SetBinError(2,0.001000801);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__975->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976","hRelYields_24_2",4,0,4);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->SetBinContent(3,0.0924712);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->SetBinError(3,0.0004379909);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__976->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977","hRelYields_24_2",4,0,4);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->SetBinContent(3,0.1178652);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->SetBinError(3,0.0006101813);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__977->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978","hRelYields_24_3",4,0,4);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->SetBinContent(4,0.0751013);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->SetBinError(4,0.001948754);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__978->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979","hRelYields_24_3",4,0,4);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->SetBinContent(4,0.09918407);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->SetBinError(4,0.001898751);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__979->Draw("same PE");
   
   TPaveText *pt = new TPaveText(0.15,0.9308974,0.85,0.995,"blNDC");
   pt->SetName("title");
   pt->SetBorderSize(0);
   pt->SetFillColor(0);
   pt->SetFillStyle(0);
   pt->SetTextFont(42);
   TText *pt_LaTex = pt->AddText("integrated yields for prompt D^{+} trigger as function of multiplicity");
   pt->Draw();
   mainPadRelJunctions_integrated->Modified();
   cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity->cd();
  
// ------------>Primitives in pad: miniPadRelJunctions_integrated yields for prompt D^{+} trigger as function of multiplicity
   TPad *miniPadRelJunctions_integrated = new TPad("miniPadRelJunctions_integrated yields for prompt D^{+} trigger as function of multiplicity", "miniPad",0.05,0.1,0.95,0.3);
   miniPadRelJunctions_integrated->Draw();
   miniPadRelJunctions_integrated->cd();
   miniPadRelJunctions_integrated->Range(-0.5,-0.7190909,4.5,1.99);
   miniPadRelJunctions_integrated->SetFillColor(0);
   miniPadRelJunctions_integrated->SetBorderMode(0);
   miniPadRelJunctions_integrated->SetBorderSize(2);
   miniPadRelJunctions_integrated->SetTopMargin(0);
   miniPadRelJunctions_integrated->SetBottomMargin(0.45);
   miniPadRelJunctions_integrated->SetFrameBorderMode(0);
   miniPadRelJunctions_integrated->SetFrameBorderMode(0);
   
   TH1D *hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980 = new TH1D("hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980","",4,0,4);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->SetMinimum(0.5);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->SetMaximum(1.99);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->SetStats(0);

   ci = TColor::GetColor("#000099");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->SetLineColor(ci);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetXaxis()->SetBinLabel(1,"  80-100 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetXaxis()->SetBinLabel(2,"  40-80 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetXaxis()->SetBinLabel(3,"  5-40 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetXaxis()->SetBinLabel(4,"  top 5% multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetXaxis()->SetLabelOffset(0.035);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetXaxis()->SetLabelSize(0.15);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetXaxis()->SetTitleSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetXaxis()->SetTickLength(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetXaxis()->SetTitleOffset(1.75);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetYaxis()->SetTitle("JUN / MON");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetYaxis()->SetLabelSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetYaxis()->SetTitleSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetYaxis()->SetTitleOffset(0.42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__980->Draw("PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981","hRelYieldsRatio_24_0",4,0,4);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->SetBinContent(1,0.9849466);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->SetBinError(1,0.01252227);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_0__981->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982","hRelYieldsRatio_24_1",4,0,4);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->SetBinContent(2,1.16335);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->SetBinError(2,0.02051183);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_1__982->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983","hRelYieldsRatio_24_2",4,0,4);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->SetBinContent(3,1.274615);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->SetBinError(3,0.008698426);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_2__983->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984","hRelYieldsRatio_24_3",4,0,4);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->SetBinContent(4,1.32067);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->SetBinError(4,0.04047154);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_3__984->Draw("same PE");
   miniPadRelJunctions_integrated->Modified();
   cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity->cd();
   cRelYields_integrated->Modified();
   cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity->cd();
   cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity->SetSelected(cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity);
}
