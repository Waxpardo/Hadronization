#ifdef __CLING__
#pragma cling optimize(0)
#endif
void MACRO_cRelYields_Error_YieldsTree_BBMULTGENERAL_beauty_Lb()
{
//=========Macro generated from canvas: cRelYields_integrated yields for B^{+} trigger as function of multiplicity/cRelYields
//=========  (Thu Apr 18 16:08:37 2024) by ROOT version 6.28/04
   TCanvas *cRelYields_integrated yields for B^{+} trigger as function of multiplicity = new TCanvas("cRelYields_integrated yields for B^{+} trigger as function of multiplicity", "cRelYields",2080,154,800,600);
   cRelYields_integrated->Range(0,0,1,1);
   cRelYields_integrated->SetFillColor(0);
   cRelYields_integrated->SetBorderMode(0);
   cRelYields_integrated->SetBorderSize(2);
   cRelYields_integrated->SetLeftMargin(0.15);
   cRelYields_integrated->SetRightMargin(0.25);
   cRelYields_integrated->SetBottomMargin(0.25);
   cRelYields_integrated->SetFrameBorderMode(0);
  
// ------------>Primitives in pad: mainPadRelJunctions_integrated yields for B^{+} trigger as function of multiplicity
   TPad *mainPadRelJunctions_integrated = new TPad("mainPadRelJunctions_integrated yields for B^{+} trigger as function of multiplicity", "mainPad",0.05,0.3,0.95,0.95);
   mainPadRelJunctions_integrated->Draw();
   mainPadRelJunctions_integrated->cd();
   mainPadRelJunctions_integrated->Range(-0.8750001,0.01,7.875,0.6655556);
   mainPadRelJunctions_integrated->SetFillColor(0);
   mainPadRelJunctions_integrated->SetBorderMode(0);
   mainPadRelJunctions_integrated->SetBorderSize(2);
   mainPadRelJunctions_integrated->SetBottomMargin(0);
   mainPadRelJunctions_integrated->SetFrameBorderMode(0);
   mainPadRelJunctions_integrated->SetFrameBorderMode(0);
   
   TH1D *hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171 = new TH1D("hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171","integrated yields for B^{+} trigger as function of multiplicity",7,0,7);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->SetMinimum(0.01);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->SetMaximum(0.6);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->SetStats(0);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->SetLineColor(ci);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->GetXaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->GetXaxis()->SetLabelSize(0.05);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->GetXaxis()->SetTitleOffset(1);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->GetXaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->GetYaxis()->SetTitle("baryon/meson yield");
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->GetYaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->GetYaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->GetZaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->GetZaxis()->SetTitleOffset(1);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->GetZaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__171->Draw("PE");
   
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
   entry=leg->AddEntry("hRelYields_MONASH_integrated yields for B^{+} trigger as function of multiplicity_56_0","B^{+}#Lambda_{b}^{0}/B^{+}B^{-}","l");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172","hRelYields_56_0",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->SetBinContent(1,0.07596721);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->SetBinError(1,0.000302524);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__172->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173","hRelYields_56_0",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->SetBinContent(1,0.1381588);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->SetBinError(1,0.001103693);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__173->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174","hRelYields_56_1",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->SetBinContent(2,0.07587484);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->SetBinError(2,0.0002815033);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__174->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175","hRelYields_56_1",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->SetBinContent(2,0.230639);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->SetBinError(2,0.001290936);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__175->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176","hRelYields_56_2",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->SetBinContent(3,0.07721588);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->SetBinError(3,0.0005088646);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__176->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177","hRelYields_56_2",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->SetBinContent(3,0.2897852);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->SetBinError(3,0.001820998);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__177->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178","hRelYields_56_3",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->SetBinContent(4,0.07883188);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->SetBinError(4,0.0002846872);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__178->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179","hRelYields_56_3",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->SetBinContent(4,0.3353132);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->SetBinError(4,0.001969886);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__179->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180","hRelYields_56_4",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->SetBinContent(5,0.07994347);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->SetBinError(5,0.0004823898);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__180->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181","hRelYields_56_4",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->SetBinContent(5,0.3629264);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->SetBinError(5,0.002591761);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__181->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182","hRelYields_56_5",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->SetBinContent(6,0.07993319);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->SetBinError(6,0.0007326005);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__182->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183","hRelYields_56_5",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->SetBinContent(6,0.3663039);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->SetBinError(6,0.004535783);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__183->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184","hRelYields_56_6",7,0,7);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->SetBinContent(7,0.07796704);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->SetBinError(7,0.001820971);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__184->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185","hRelYields_56_6",7,0,7);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->SetBinContent(7,0.3522209);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->SetBinError(7,0.009296825);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__185->Draw("same PE");
   
   TPaveText *pt = new TPaveText(0.15,0.9308974,0.85,0.995,"blNDC");
   pt->SetName("title");
   pt->SetBorderSize(0);
   pt->SetFillColor(0);
   pt->SetFillStyle(0);
   pt->SetTextFont(42);
   TText *pt_LaTex = pt->AddText("integrated yields for B^{+} trigger as function of multiplicity");
   pt->Draw();
   mainPadRelJunctions_integrated->Modified();
   cRelYields_integrated yields for B^{+} trigger as function of multiplicity->cd();
  
// ------------>Primitives in pad: miniPadRelJunctions_integrated yields for B^{+} trigger as function of multiplicity
   TPad *miniPadRelJunctions_integrated = new TPad("miniPadRelJunctions_integrated yields for B^{+} trigger as function of multiplicity", "miniPad",0.05,0.1,0.95,0.3);
   miniPadRelJunctions_integrated->Draw();
   miniPadRelJunctions_integrated->cd();
   miniPadRelJunctions_integrated->Range(-0.8750001,-5.764545,7.875,7.49);
   miniPadRelJunctions_integrated->SetFillColor(0);
   miniPadRelJunctions_integrated->SetBorderMode(0);
   miniPadRelJunctions_integrated->SetBorderSize(2);
   miniPadRelJunctions_integrated->SetTopMargin(0);
   miniPadRelJunctions_integrated->SetBottomMargin(0.45);
   miniPadRelJunctions_integrated->SetFrameBorderMode(0);
   miniPadRelJunctions_integrated->SetFrameBorderMode(0);
   
   TH1D *hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186 = new TH1D("hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186","",7,0,7);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->SetMinimum(0.2);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->SetMaximum(7.49);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->SetStats(0);

   ci = TColor::GetColor("#000099");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->SetLineColor(ci);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetBinLabel(1,"  80-100 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetBinLabel(2,"  60-80 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetBinLabel(3,"  40-60 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetBinLabel(4,"  20-40 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetBinLabel(5,"  5-20 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetBinLabel(6,"  1-5% multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetBinLabel(7,"  top 1% multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetLabelOffset(0.035);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetLabelSize(0.15);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetTitleSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetTickLength(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetTitleOffset(1.75);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetYaxis()->SetTitle("JUN / MON");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetYaxis()->SetLabelSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetYaxis()->SetTitleSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetYaxis()->SetTitleOffset(0.42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__186->Draw("PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187","hRelYieldsRatio_56_0",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->SetBinContent(1,1.818664);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->SetBinError(1,0.01751675);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_0__187->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188","hRelYieldsRatio_56_1",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->SetBinContent(2,3.039729);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->SetBinError(2,0.02053769);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_1__188->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189","hRelYieldsRatio_56_2",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->SetBinContent(3,3.752922);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->SetBinError(3,0.0379603);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_2__189->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190","hRelYieldsRatio_56_3",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->SetBinContent(4,4.253522);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->SetBinError(4,0.02433574);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_3__190->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191","hRelYieldsRatio_56_4",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->SetBinContent(5,4.539787);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->SetBinError(5,0.045988);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_4__191->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192","hRelYieldsRatio_56_5",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->SetBinContent(6,4.582625);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->SetBinError(6,0.07420004);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_5__192->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193","hRelYieldsRatio_56_6",7,0,7);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->SetBinContent(7,4.517562);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->SetBinError(7,0.1732796);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_56_6__193->Draw("same PE");
   miniPadRelJunctions_integrated->Modified();
   cRelYields_integrated yields for B^{+} trigger as function of multiplicity->cd();
   cRelYields_integrated->Modified();
   cRelYields_integrated yields for B^{+} trigger as function of multiplicity->cd();
   cRelYields_integrated yields for B^{+} trigger as function of multiplicity->SetSelected(cRelYields_integrated yields for B^{+} trigger as function of multiplicity);
}
