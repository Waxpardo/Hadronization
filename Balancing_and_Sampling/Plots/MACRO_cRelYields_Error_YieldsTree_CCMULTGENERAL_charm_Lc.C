#ifdef __CLING__
#pragma cling optimize(0)
#endif
void MACRO_cRelYields_Error_YieldsTree_CCMULTGENERAL_charm_Lc()
{
//=========Macro generated from canvas: cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity/cRelYields
//=========  (Thu Apr 18 16:08:43 2024) by ROOT version 6.28/04
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
   mainPadRelJunctions_integrated->Range(-0.8750001,0.01,7.875,0.2766667);
   mainPadRelJunctions_integrated->SetFillColor(0);
   mainPadRelJunctions_integrated->SetBorderMode(0);
   mainPadRelJunctions_integrated->SetBorderSize(2);
   mainPadRelJunctions_integrated->SetBottomMargin(0);
   mainPadRelJunctions_integrated->SetFrameBorderMode(0);
   mainPadRelJunctions_integrated->SetFrameBorderMode(0);
   
   TH1D *hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669 = new TH1D("hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669","integrated yields for prompt D^{+} trigger as function of multiplicity",7,0,7);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->SetMinimum(0.01);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->SetMaximum(0.25);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->SetStats(0);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->SetLineColor(ci);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->GetXaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->GetXaxis()->SetLabelSize(0.05);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->GetXaxis()->SetTitleOffset(1);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->GetXaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->GetYaxis()->SetTitle("baryon/meson yield");
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->GetYaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->GetYaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->GetZaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->GetZaxis()->SetTitleOffset(1);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->GetZaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__669->Draw("PE");
   
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
   entry=leg->AddEntry("hRelYields_MONASH_integrated yields for prompt D^{+} trigger as function of multiplicity_42_0","D^{+}#bar#Lambda_{c}^{+}/D^{+}D^{-}","l");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670","hRelYields_42_0",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->SetBinContent(1,0.1166751);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->SetBinError(1,0.0009609569);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__670->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671","hRelYields_42_0",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->SetBinContent(1,0.1149187);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->SetBinError(1,0.001082448);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__671->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672","hRelYields_42_1",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->SetBinContent(2,0.1029288);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->SetBinError(2,0.001197566);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__672->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673","hRelYields_42_1",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->SetBinContent(2,0.1081723);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->SetBinError(2,0.0007271731);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__673->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674","hRelYields_42_2",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->SetBinContent(3,0.096937);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->SetBinError(3,0.001361647);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__674->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675","hRelYields_42_2",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->SetBinContent(3,0.1127716);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->SetBinError(3,0.001000802);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__675->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676","hRelYields_42_3",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->SetBinContent(4,0.09572232);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->SetBinError(4,0.0007363211);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__676->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677","hRelYields_42_3",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->SetBinContent(4,0.1190279);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->SetBinError(4,0.001022974);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__677->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678","hRelYields_42_4",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->SetBinContent(5,0.08969224);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->SetBinError(5,0.000617081);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__678->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679","hRelYields_42_4",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->SetBinContent(5,0.1168809);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->SetBinError(5,0.0007738335);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__679->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680","hRelYields_42_5",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->SetBinContent(6,0.08018434);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->SetBinError(6,0.001534939);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__680->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681","hRelYields_42_5",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->SetBinContent(6,0.1060358);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->SetBinError(6,0.001598815);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__681->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682","hRelYields_42_6",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->SetBinContent(7,0.07063744);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->SetBinError(7,0.003375629);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__682->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683","hRelYields_42_6",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->SetBinContent(7,0.09321117);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->SetBinError(7,0.002743014);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__683->Draw("same PE");
   
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
   miniPadRelJunctions_integrated->Range(-0.8750001,-0.7190909,7.875,1.99);
   miniPadRelJunctions_integrated->SetFillColor(0);
   miniPadRelJunctions_integrated->SetBorderMode(0);
   miniPadRelJunctions_integrated->SetBorderSize(2);
   miniPadRelJunctions_integrated->SetTopMargin(0);
   miniPadRelJunctions_integrated->SetBottomMargin(0.45);
   miniPadRelJunctions_integrated->SetFrameBorderMode(0);
   miniPadRelJunctions_integrated->SetFrameBorderMode(0);
   
   TH1D *hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684 = new TH1D("hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684","",7,0,7);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->SetMinimum(0.5);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->SetMaximum(1.99);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->SetStats(0);

   ci = TColor::GetColor("#000099");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->SetLineColor(ci);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetBinLabel(1,"  80-100 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetBinLabel(2,"  60-80 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetBinLabel(3,"  40-60 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetBinLabel(4,"  20-40 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetBinLabel(5,"  5-20 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetBinLabel(6,"  1-5% multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetBinLabel(7,"  top 1% multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetLabelOffset(0.035);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetLabelSize(0.15);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetTitleSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetTickLength(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetTitleOffset(1.75);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetYaxis()->SetTitle("JUN / MON");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetYaxis()->SetLabelSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetYaxis()->SetTitleSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetYaxis()->SetTitleOffset(0.42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__684->Draw("PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685","hRelYieldsRatio_42_0",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->SetBinContent(1,0.9849466);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->SetBinError(1,0.01252227);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_0__685->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686","hRelYieldsRatio_42_1",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->SetBinContent(2,1.050943);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->SetBinError(2,0.01525557);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_1__686->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687","hRelYieldsRatio_42_2",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->SetBinContent(3,1.16335);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->SetBinError(3,0.02051187);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_2__687->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688","hRelYieldsRatio_42_3",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->SetBinContent(4,1.24347);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->SetBinError(4,0.01460202);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_3__688->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689","hRelYieldsRatio_42_4",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->SetBinContent(5,1.303133);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->SetBinError(5,0.01146035);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_4__689->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690","hRelYieldsRatio_42_5",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->SetBinContent(6,1.322401);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->SetBinError(6,0.03585374);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_5__690->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691","hRelYieldsRatio_42_6",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->SetBinContent(7,1.319572);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->SetBinError(7,0.07297531);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_6__691->Draw("same PE");
   miniPadRelJunctions_integrated->Modified();
   cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity->cd();
   cRelYields_integrated->Modified();
   cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity->cd();
   cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity->SetSelected(cRelYields_integrated yields for prompt D^{+} trigger as function of multiplicity);
}
