#ifdef __CLING__
#pragma cling optimize(0)
#endif
void MACRO_cRelYields_Error_YieldsTree_BBMULTCONDENSED_beauty_Lb()
{
//=========Macro generated from canvas: cRelYields_integrated yields for B^{+} trigger as function of multiplicity/cRelYields
//=========  (Thu Apr 18 16:08:41 2024) by ROOT version 6.28/04
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
   mainPadRelJunctions_integrated->Range(-0.5,0.01,4.5,0.6655556);
   mainPadRelJunctions_integrated->SetFillColor(0);
   mainPadRelJunctions_integrated->SetBorderMode(0);
   mainPadRelJunctions_integrated->SetBorderSize(2);
   mainPadRelJunctions_integrated->SetBottomMargin(0);
   mainPadRelJunctions_integrated->SetFrameBorderMode(0);
   mainPadRelJunctions_integrated->SetFrameBorderMode(0);
   
   TH1D *hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506 = new TH1D("hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506","integrated yields for B^{+} trigger as function of multiplicity",4,0,4);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->SetMinimum(0.01);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->SetMaximum(0.6);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->SetStats(0);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->SetLineColor(ci);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->GetXaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->GetXaxis()->SetLabelSize(0.05);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->GetXaxis()->SetTitleOffset(1);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->GetXaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->GetYaxis()->SetTitle("baryon/meson yield");
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->GetYaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->GetYaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->GetZaxis()->SetLabelFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->GetZaxis()->SetTitleOffset(1);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->GetZaxis()->SetTitleFont(42);
   hRelYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__506->Draw("PE");
   
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
   entry=leg->AddEntry("hRelYields_MONASH_integrated yields for B^{+} trigger as function of multiplicity_32_0","B^{+}#Lambda_{b}^{0}/B^{+}B^{-}","l");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507","hRelYields_32_0",4,0,4);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->SetBinContent(1,0.07596721);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->SetBinError(1,0.000302524);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__507->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508","hRelYields_32_0",4,0,4);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->SetBinContent(1,0.1381588);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->SetBinError(1,0.001103693);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__508->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509","hRelYields_32_1",4,0,4);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->SetBinContent(2,0.07721588);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->SetBinError(2,0.0005088642);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__509->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510","hRelYields_32_1",4,0,4);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->SetBinContent(2,0.2897852);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->SetBinError(2,0.001820996);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__510->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511","hRelYields_32_2",4,0,4);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->SetBinContent(3,0.07939358);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->SetBinError(3,0.0002534001);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__511->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512","hRelYields_32_2",4,0,4);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->SetBinContent(3,0.3490951);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->SetBinError(3,0.001806321);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__512->Draw("same PE");
   
   TH1D *hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513 = new TH1D("hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513","hRelYields_32_3",4,0,4);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->SetBinContent(4,0.07893267);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->SetBinError(4,0.0008959274);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->SetEntries(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->GetXaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->GetXaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->GetXaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->GetYaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->GetYaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->GetZaxis()->SetLabelFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->GetZaxis()->SetTitleOffset(1);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->GetZaxis()->SetTitleFont(42);
   hRelYields_MONASH_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__513->Draw("same PE");
   
   TH1D *hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514 = new TH1D("hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514","hRelYields_32_3",4,0,4);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->SetBinContent(4,0.3590848);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->SetBinError(4,0.006361684);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->SetLineColor(ci);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->GetXaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->GetXaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->GetXaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->GetYaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->GetYaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->GetZaxis()->SetLabelFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->GetZaxis()->SetTitleOffset(1);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->GetZaxis()->SetTitleFont(42);
   hRelYields_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__514->Draw("same PE");
   
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
   miniPadRelJunctions_integrated->Range(-0.5,-5.764545,4.5,7.49);
   miniPadRelJunctions_integrated->SetFillColor(0);
   miniPadRelJunctions_integrated->SetBorderMode(0);
   miniPadRelJunctions_integrated->SetBorderSize(2);
   miniPadRelJunctions_integrated->SetTopMargin(0);
   miniPadRelJunctions_integrated->SetBottomMargin(0.45);
   miniPadRelJunctions_integrated->SetFrameBorderMode(0);
   miniPadRelJunctions_integrated->SetFrameBorderMode(0);
   
   TH1D *hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515 = new TH1D("hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515","",4,0,4);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->SetMinimum(0.2);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->SetMaximum(7.49);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->SetStats(0);

   ci = TColor::GetColor("#000099");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->SetLineColor(ci);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetXaxis()->SetBinLabel(1,"  80-100 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetXaxis()->SetBinLabel(2,"  40-80 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetXaxis()->SetBinLabel(3,"  5-40 % multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetXaxis()->SetBinLabel(4,"  top 5% multiplicity bin");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetXaxis()->SetLabelOffset(0.035);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetXaxis()->SetLabelSize(0.15);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetXaxis()->SetTitleSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetXaxis()->SetTickLength(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetXaxis()->SetTitleOffset(1.75);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetYaxis()->SetTitle("JUN / MON");
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetYaxis()->SetLabelSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetYaxis()->SetTitleSize(0.105);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetYaxis()->SetTitleOffset(0.42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__515->Draw("PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516","hRelYieldsRatio_32_0",4,0,4);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->SetBinContent(1,1.818664);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->SetBinError(1,0.01751675);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_0__516->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517","hRelYieldsRatio_32_1",4,0,4);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->SetBinContent(2,3.752922);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->SetBinError(2,0.03796026);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_1__517->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518","hRelYieldsRatio_32_2",4,0,4);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->SetBinContent(3,4.397019);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->SetBinError(3,0.027102);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_2__518->Draw("same PE");
   
   TH1D *hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519 = new TH1D("hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519","hRelYieldsRatio_32_3",4,0,4);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->SetBinContent(4,4.549255);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->SetBinError(4,0.1078061);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->SetEntries(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->GetXaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->GetXaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->GetXaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->GetYaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->GetYaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->GetZaxis()->SetLabelFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->GetZaxis()->SetTitleOffset(1);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->GetZaxis()->SetTitleFont(42);
   hRelYieldsRatio_JUNCTIONS_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_32_3__519->Draw("same PE");
   miniPadRelJunctions_integrated->Modified();
   cRelYields_integrated yields for B^{+} trigger as function of multiplicity->cd();
   cRelYields_integrated->Modified();
   cRelYields_integrated yields for B^{+} trigger as function of multiplicity->cd();
   cRelYields_integrated yields for B^{+} trigger as function of multiplicity->SetSelected(cRelYields_integrated yields for B^{+} trigger as function of multiplicity);
}
