#ifdef __CLING__
#pragma cling optimize(0)
#endif
void globalCanvasYieldsMACRO()
{
//=========Macro generated from canvas: c2x3_yields/balancing yields for beauty and charm on a 2x3 canvas
//=========  (Mon Jun 17 11:56:40 2024) by ROOT version 6.28/04
   TCanvas *c2x3_yields = new TCanvas("c2x3_yields", "balancing yields for beauty and charm on a 2x3 canvas",120,64,1200,1000);
   c2x3_yields->Range(0,0,1,1);
   c2x3_yields->SetFillColor(0);
   c2x3_yields->SetBorderMode(0);
   c2x3_yields->SetBorderSize(2);
   c2x3_yields->SetRightMargin(0.05);
   c2x3_yields->SetBottomMargin(0.05);
   c2x3_yields->SetFrameBorderMode(0);
  
// ------------>Primitives in pad: c00_yields
   TPad *c00_yields = new TPad("c00_yields", "yields for JUNCTIONS beauty",0.05,0.65,0.5,0.95);
   c00_yields->Draw();
   c00_yields->cd();
   c00_yields->Range(-2.002503,-4.227678,8.010013,1.60206);
   c00_yields->SetFillColor(0);
   c00_yields->SetBorderMode(0);
   c00_yields->SetBorderSize(2);
   c00_yields->SetLogy();
   c00_yields->SetTicky(1);
   c00_yields->SetLeftMargin(0.2);
   c00_yields->SetRightMargin(0.001);
   c00_yields->SetTopMargin(0);
   c00_yields->SetBottomMargin(0.001);
   c00_yields->SetFrameBorderMode(0);
   c00_yields->SetFrameBorderMode(0);
   
   TH1D *hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1 = new TH1D("hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1","",8,0,8);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->SetMinimum(6e-05);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->SetMaximum(40);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->SetStats(0);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->SetLineColor(ci);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetBinLabel(1,"B^{-}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetBinLabel(2,"B_{c}^{-}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetBinLabel(3,"#barB^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetBinLabel(4,"#barB_{s}^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetBinLabel(5,"#Lambda_{b}^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetBinLabel(6,"#Sigma_{b}^{+}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetBinLabel(7,"#Sigma_{b}^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetBinLabel(8,"#Sigma_{b}^{-}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetLabelSize(0.05);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetTitleOffset(1);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetXaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetYaxis()->SetTitle("Integrated yield");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetYaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetYaxis()->SetLabelSize(0.05);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetYaxis()->SetTitleSize(0.06);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetYaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetZaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetZaxis()->SetTitleOffset(1);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->GetZaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__1->Draw("PE");
   
   TLegend *leg = new TLegend(0.45,0.85,0.75,0.95,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.05);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   TLegendEntry *entry=leg->AddEntry("NULL","Junctions","");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   leg = new TLegend(0.25,0.85,0.4,0.95,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.05);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("NULL","(a)","");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2","hYields_0_0",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->SetBinContent(1,0.3050817);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->SetBinError(1,0.0006022949);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->SetLineWidth(2);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__2->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3","hYields_0_1",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->SetBinContent(1,0.2486956);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->SetBinError(1,0.0005390598);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__3->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4","hYields_0_2",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->SetBinContent(1,0.238998);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->SetBinError(1,0.0007781807);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__4->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5","hYields_3_3",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->SetBinContent(2,0.0002416089);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->SetBinError(2,1.893674e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->SetLineWidth(2);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__5->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6","hYields_3_4",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->SetBinContent(2,0.0004423891);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->SetBinError(2,3.368561e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__6->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7","hYields_3_5",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->SetBinContent(2,0.0005979627);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->SetBinError(2,3.338043e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__7->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8","hYields_6_6",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->SetBinContent(3,0.3022574);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->SetBinError(3,0.0005126794);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->SetLineWidth(2);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__8->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9","hYields_6_7",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->SetBinContent(3,0.24455);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->SetBinError(3,0.000612854);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__9->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10","hYields_6_8",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->SetBinContent(3,0.2328172);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->SetBinError(3,0.0004647616);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__10->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11","hYields_9_9",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->SetBinContent(4,0.06066873);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->SetBinError(4,0.0003094531);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->SetLineWidth(2);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__11->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12","hYields_9_10",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->SetBinContent(4,0.04716865);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->SetBinError(4,0.000337216);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__12->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13","hYields_9_11",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->SetBinContent(4,0.04452323);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->SetBinError(4,0.0003164768);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__13->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14","hYields_12_12",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->SetBinContent(5,0.04214973);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->SetBinError(5,0.0003095339);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->SetLineWidth(2);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__14->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15","hYields_12_13",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->SetBinContent(5,0.0720683);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->SetBinError(5,0.000371353);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__15->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16","hYields_12_14",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->SetBinContent(5,0.08673867);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->SetBinError(5,0.0004905289);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__16->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17","hYields_15_15",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->SetBinContent(6,0.02654821);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->SetBinError(6,0.0002552513);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->SetLineWidth(2);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__17->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18","hYields_15_16",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->SetBinContent(6,0.05470533);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->SetBinError(6,0.000344206);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__18->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19","hYields_15_17",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->SetBinContent(6,0.06355573);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->SetBinError(6,0.0004242799);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__19->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20","hYields_18_18",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->SetBinContent(7,0.02841817);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->SetBinError(7,0.000303463);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->SetLineWidth(2);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__20->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21","hYields_18_19",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->SetBinContent(7,0.06104288);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->SetBinError(7,0.0003137876);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__21->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22","hYields_18_20",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->SetBinContent(7,0.07200098);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->SetBinError(7,0.0003151413);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__22->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23","hYields_21_21",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->SetBinContent(8,0.02662379);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->SetBinError(8,0.0002289951);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->SetLineWidth(2);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__23->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24","hYields_21_22",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->SetBinContent(8,0.05484605);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->SetBinError(8,0.0004009004);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__24->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25","hYields_21_23",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->SetBinContent(8,0.06349167);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->SetBinError(8,0.0005126199);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->SetLineWidth(3);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__25->Draw("same PE");
   c00_yields->Modified();
   c2x3_yields->cd();
  
// ------------>Primitives in pad: c01_yields
   TPad *c01_yields = new TPad("c01_yields", "yields for JUNCTIONS beauty",0.501,0.65,0.95,0.95);
   c01_yields->Draw();
   c01_yields->cd();
   c01_yields->Range(0,-4.227678,7.777778,1.60206);
   c01_yields->SetFillColor(0);
   c01_yields->SetBorderMode(0);
   c01_yields->SetBorderSize(2);
   c01_yields->SetLogy();
   c01_yields->SetLeftMargin(0);
   c01_yields->SetTopMargin(0);
   c01_yields->SetBottomMargin(0.001);
   c01_yields->SetFrameBorderMode(0);
   c01_yields->SetFrameBorderMode(0);
   
   TH1D *hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26 = new TH1D("hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26","",7,0,7);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->SetMinimum(6e-05);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->SetMaximum(40);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->SetLineColor(ci);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetXaxis()->SetBinLabel(1,"D^{-}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetXaxis()->SetBinLabel(2,"D_{s}^{-}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetXaxis()->SetBinLabel(3,"#barD^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetXaxis()->SetBinLabel(4,"#bar#Lambda_{c}^{+}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetXaxis()->SetBinLabel(5,"#bar#Sigma_{c}^{++}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetXaxis()->SetBinLabel(6,"#bar#Sigma_{c}^{+}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetXaxis()->SetBinLabel(7,"#bar#Sigma_{c}^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetXaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetXaxis()->SetLabelSize(0.05);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetXaxis()->SetTitleOffset(1);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetXaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetYaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetYaxis()->SetLabelSize(0.05);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetYaxis()->SetTitleSize(0.06);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetYaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetZaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetZaxis()->SetTitleOffset(1);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->GetZaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__26->Draw("PE");
   
   leg = new TLegend(0.05,0.85,0.2,0.95,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.05);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("NULL","(b)","");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   leg = new TLegend(0.45,0.68,0.75,0.98,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.05);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("NULL","B^{+} trigger","l");

   ci = TColor::GetColor("#ff0000");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("NULL","D^{+} trigger","l");

   ci = TColor::GetColor("#0000ff");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("NULL","Ratio","l");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27","hYields_0_0",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->SetBinContent(1,0.1248002);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->SetBinError(1,0.0003085851);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->SetLineWidth(2);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__27->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28","hYields_0_1",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->SetBinContent(1,0.1377168);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->SetBinError(1,0.0003313827);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__28->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29","hYields_0_2",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->SetBinContent(1,0.1778241);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->SetBinError(1,0.0007053081);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__29->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30","hYields_3_3",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->SetBinContent(2,0.02679214);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->SetBinError(2,0.0001092683);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->SetLineWidth(2);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__30->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31","hYields_3_4",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->SetBinContent(2,0.02742158);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->SetBinError(2,0.0001408698);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__31->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32","hYields_3_5",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->SetBinContent(2,0.03298141);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->SetBinError(2,0.0001698512);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__32->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33","hYields_6_6",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->SetBinContent(3,0.1236441);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->SetBinError(3,0.000235813);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->SetLineWidth(2);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__33->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34","hYields_6_7",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->SetBinContent(3,0.1353078);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->SetBinError(3,0.0004308343);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__34->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35","hYields_6_8",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->SetBinContent(3,0.1633559);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->SetBinError(3,0.0005570099);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__35->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36","hYields_9_9",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->SetBinContent(4,0.01434187);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->SetBinError(4,0.0001311601);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->SetLineWidth(2);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__36->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37","hYields_9_10",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->SetBinContent(4,0.01553055);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->SetBinError(4,0.0001405679);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__37->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38","hYields_9_11",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->SetBinContent(4,0.02078423);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->SetBinError(4,0.0001532067);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__38->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39","hYields_12_12",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->SetBinContent(5,0.002601329);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->SetBinError(5,4.151795e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->SetLineWidth(2);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__39->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40","hYields_12_13",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->SetBinContent(5,0.007787068);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->SetBinError(5,0.0001480804);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__40->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41","hYields_12_14",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->SetBinContent(5,0.01337305);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->SetBinError(5,0.0001247391);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__41->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42","hYields_15_15",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->SetBinContent(6,0.002715437);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->SetBinError(6,7.438942e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->SetLineWidth(2);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__42->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43","hYields_15_16",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->SetBinContent(6,0.008015649);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->SetBinError(6,0.0001310321);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__43->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44","hYields_15_17",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->SetBinContent(6,0.01405096);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->SetBinError(6,0.0001399288);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__44->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45","hYields_18_18",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->SetBinContent(7,0.002651722);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->SetBinError(7,7.391264e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->SetLineWidth(2);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__45->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46","hYields_18_19",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->SetBinContent(7,0.007722167);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->SetBinError(7,0.0001299412);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__46->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47","hYields_18_20",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->SetBinContent(7,0.0132231);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->SetBinError(7,0.0001181889);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->SetLineWidth(3);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->SetMarkerColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__47->Draw("same PE");
   c01_yields->Modified();
   c2x3_yields->cd();
  
// ------------>Primitives in pad: c10_yields
   TPad *c10_yields = new TPad("c10_yields", "yields for MONASH charm",0.05,0.35,0.5,0.651);
   c10_yields->Draw();
   c10_yields->cd();
   c10_yields->Range(-2.002503,-4.221849,8.010013,1.60206);
   c10_yields->SetFillColor(0);
   c10_yields->SetBorderMode(0);
   c10_yields->SetBorderSize(2);
   c10_yields->SetLogy();
   c10_yields->SetTickx(1);
   c10_yields->SetTicky(1);
   c10_yields->SetLeftMargin(0.2);
   c10_yields->SetRightMargin(0.001);
   c10_yields->SetTopMargin(0);
   c10_yields->SetBottomMargin(0);
   c10_yields->SetFrameBorderMode(0);
   c10_yields->SetFrameBorderMode(0);
   
   TH1D *hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48 = new TH1D("hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48","",8,0,8);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->SetMinimum(6e-05);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->SetMaximum(40);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->SetLineColor(ci);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetBinLabel(1,"B^{-}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetBinLabel(2,"B_{c}^{-}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetBinLabel(3,"#barB^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetBinLabel(4,"#barB_{s}^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetBinLabel(5,"#Lambda_{b}^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetBinLabel(6,"#Sigma_{b}^{+}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetBinLabel(7,"#Sigma_{b}^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetBinLabel(8,"#Sigma_{b}^{-}");
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetLabelSize(0.05);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetTitleOffset(1);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetXaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetYaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetYaxis()->SetLabelSize(0.05);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetYaxis()->SetTitleSize(0.06);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetYaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetZaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetZaxis()->SetTitleOffset(1);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->GetZaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__48->Draw("PE");
   
   leg = new TLegend(0.45,0.85,0.75,0.95,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.05);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("NULL","Monash","");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   leg = new TLegend(0.25,0.85,0.4,0.95,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.05);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("NULL","(c)","");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49","hYields_0_0",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->SetBinContent(1,0.354507);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->SetBinError(1,0.0004844964);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__49->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50","hYields_0_1",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->SetBinContent(1,0.3624975);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->SetBinError(1,0.0005303311);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__50->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51","hYields_0_2",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->SetBinContent(1,0.3747261);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->SetBinError(1,0.000599433);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__51->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52","hYields_3_3",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->SetBinContent(2,0.000462957);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->SetBinError(2,1.498432e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__52->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53","hYields_3_4",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->SetBinContent(2,0.0009418034);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->SetBinError(2,1.992384e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__53->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54","hYields_3_5",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->SetBinContent(2,0.0009990335);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->SetBinError(2,2.452023e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__54->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55","hYields_6_6",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->SetBinContent(3,0.3531745);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->SetBinError(3,0.0004716844);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__55->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56","hYields_6_7",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->SetBinContent(3,0.3587837);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->SetBinError(3,0.0003684041);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__56->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57","hYields_6_8",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->SetBinContent(3,0.3673974);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->SetBinError(3,0.0005271825);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__57->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58","hYields_9_9",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->SetBinContent(4,0.07912466);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->SetBinError(4,0.0002327538);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__58->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59","hYields_9_10",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->SetBinContent(4,0.08079633);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->SetBinError(4,0.0002337812);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__59->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60","hYields_9_11",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->SetBinContent(4,0.08233191);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->SetBinError(4,0.0002380761);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__60->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61","hYields_12_12",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->SetBinContent(5,0.02693091);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->SetBinError(5,9.152005e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__61->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62","hYields_12_13",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->SetBinContent(5,0.02799056);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->SetBinError(5,0.0001661018);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__62->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63","hYields_12_14",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->SetBinContent(5,0.02995691);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->SetBinError(5,0.0001571639);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__63->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64","hYields_15_15",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->SetBinContent(6,0.001371449);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->SetBinError(6,2.84799e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__64->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65","hYields_15_16",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->SetBinContent(6,0.001985751);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->SetBinError(6,3.949543e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__65->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66","hYields_15_17",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->SetBinContent(6,0.002705425);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->SetBinError(6,4.015393e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__66->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67","hYields_18_18",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->SetBinContent(7,0.001382776);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->SetBinError(7,2.968567e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__67->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68","hYields_18_19",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->SetBinContent(7,0.00198294);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->SetBinError(7,4.048875e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__68->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69","hYields_18_20",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->SetBinContent(7,0.00270606);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->SetBinError(7,5.039378e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__69->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70","hYields_21_21",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->SetBinContent(8,0.001383018);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->SetBinError(8,2.396475e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_21__70->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71","hYields_21_22",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->SetBinContent(8,0.001985487);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->SetBinError(8,3.640117e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_22__71->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72 = new TH1D("hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72","hYields_21_23",8,0,8);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->SetBinContent(8,0.002688479);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->SetBinError(8,4.959972e-05);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->SetEntries(1);

   ci = TColor::GetColor("#ff0000");
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_21_23__72->Draw("same PE");
   c10_yields->Modified();
   c2x3_yields->cd();
  
// ------------>Primitives in pad: c11_yields
   TPad *c11_yields = new TPad("c11_yields", "yields for MONASH charm",0.501,0.35,0.95,0.651);
   c11_yields->Draw();
   c11_yields->cd();
   c11_yields->Range(0,-4.221849,7.777778,1.60206);
   c11_yields->SetFillColor(0);
   c11_yields->SetBorderMode(0);
   c11_yields->SetBorderSize(2);
   c11_yields->SetLogy();
   c11_yields->SetTickx(1);
   c11_yields->SetLeftMargin(0);
   c11_yields->SetTopMargin(0);
   c11_yields->SetBottomMargin(0);
   c11_yields->SetFrameBorderMode(0);
   c11_yields->SetFrameBorderMode(0);
   
   TH1D *hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73 = new TH1D("hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73","",7,0,7);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->SetMinimum(6e-05);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->SetMaximum(40);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->SetLineColor(ci);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetXaxis()->SetBinLabel(1,"D^{-}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetXaxis()->SetBinLabel(2,"D_{s}^{-}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetXaxis()->SetBinLabel(3,"#barD^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetXaxis()->SetBinLabel(4,"#bar#Lambda_{c}^{+}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetXaxis()->SetBinLabel(5,"#bar#Sigma_{c}^{++}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetXaxis()->SetBinLabel(6,"#bar#Sigma_{c}^{+}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetXaxis()->SetBinLabel(7,"#bar#Sigma_{c}^{0}");
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetXaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetXaxis()->SetLabelSize(0.05);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetXaxis()->SetTitleOffset(1);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetXaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetYaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetYaxis()->SetLabelSize(0.05);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetYaxis()->SetTitleSize(0.06);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetYaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetZaxis()->SetLabelFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetZaxis()->SetTitleOffset(1);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->GetZaxis()->SetTitleFont(42);
   hYieldsTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__73->Draw("PE");
   
   leg = new TLegend(0.45,0.68,0.75,0.98,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.05);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("NULL","60 - 100% multiplicity bin","l");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("NULL","20 - 60% multiplicity bin","l");
   entry->SetLineColor(1);
   entry->SetLineStyle(2);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("NULL","0 - 20% multiplicity bin","l");
   entry->SetLineColor(1);
   entry->SetLineStyle(3);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   leg = new TLegend(0.05,0.85,0.2,0.95,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.05);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("NULL","(d)","");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74","hYields_0_0",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->SetBinContent(1,0.1325841);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->SetBinError(1,0.000376488);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__74->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75","hYields_0_1",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->SetBinContent(1,0.1537362);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->SetBinError(1,0.0004628045);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__75->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76","hYields_0_2",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->SetBinContent(1,0.1998841);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->SetBinError(1,0.0007483774);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__76->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77","hYields_3_3",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->SetBinContent(2,0.03098456);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->SetBinError(2,0.0003094337);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_3__77->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78","hYields_3_4",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->SetBinContent(2,0.03341463);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->SetBinError(2,0.0003293869);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_4__78->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79","hYields_3_5",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->SetBinContent(2,0.0403891);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->SetBinError(2,0.0003244311);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_3_5__79->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80","hYields_6_6",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->SetBinContent(3,0.1312472);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->SetBinError(3,0.0003644653);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__80->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81","hYields_6_7",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->SetBinContent(3,0.150874);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->SetBinError(3,0.0006962555);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__81->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82","hYields_6_8",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->SetBinContent(3,0.1824929);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->SetBinError(3,0.0005061746);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__82->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83","hYields_9_9",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->SetBinContent(4,0.01546926);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->SetBinError(4,0.0001145552);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_9__83->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84","hYields_9_10",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->SetBinContent(4,0.01490272);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->SetBinError(4,0.0002023265);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_10__84->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85","hYields_9_11",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->SetBinContent(4,0.01792805);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->SetBinError(4,0.000132342);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_9_11__85->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86","hYields_12_12",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->SetBinContent(5,0.000933737);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->SetBinError(5,3.543269e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__86->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87","hYields_12_13",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->SetBinContent(5,0.001055837);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->SetBinError(5,4.11337e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__87->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88","hYields_12_14",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->SetBinContent(5,0.00121677);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->SetBinError(5,5.211957e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__88->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89","hYields_15_15",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->SetBinContent(6,0.0009628021);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->SetBinError(6,4.57895e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_15__89->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90","hYields_15_16",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->SetBinContent(6,0.001028852);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->SetBinError(6,4.398405e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_16__90->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91","hYields_15_17",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->SetBinContent(6,0.001203505);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->SetBinError(6,4.539625e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_15_17__91->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92","hYields_18_18",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->SetBinContent(7,0.0009934633);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->SetBinError(7,3.765479e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->SetLineWidth(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__92->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93","hYields_18_19",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->SetBinContent(7,0.001030275);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->SetBinError(7,4.037491e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->SetLineStyle(2);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__93->Draw("same PE");
   
   TH1D *hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94 = new TH1D("hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94","hYields_18_20",7,0,7);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->SetBinContent(7,0.00120045);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->SetBinError(7,4.203599e-05);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->SetEntries(1);

   ci = TColor::GetColor("#0000ff");
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->SetLineColor(ci);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->SetLineStyle(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->SetLineWidth(3);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->SetMarkerStyle(0);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->GetXaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->GetXaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->GetXaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->GetYaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->GetYaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->GetZaxis()->SetLabelFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->GetZaxis()->SetTitleOffset(1);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->GetZaxis()->SetTitleFont(42);
   hYields_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__94->Draw("same PE");
   c11_yields->Modified();
   c2x3_yields->cd();
  
// ------------>Primitives in pad: c20mini_yields
   TPad *c20mini_yields = new TPad("c20mini_yields", "yields ratio for beauty",0.05,0,0.5,0.351);
   c20mini_yields->Draw();
   c20mini_yields->cd();
   c20mini_yields->Range(-2.002503,-1.830442,8.010013,1.69897);
   c20mini_yields->SetFillColor(0);
   c20mini_yields->SetBorderMode(0);
   c20mini_yields->SetBorderSize(2);
   c20mini_yields->SetLogy();
   c20mini_yields->SetTickx(1);
   c20mini_yields->SetTicky(1);
   c20mini_yields->SetLeftMargin(0.2);
   c20mini_yields->SetRightMargin(0.001);
   c20mini_yields->SetTopMargin(0);
   c20mini_yields->SetBottomMargin(0.15);
   c20mini_yields->SetFrameBorderMode(0);
   c20mini_yields->SetFrameBorderMode(0);
   
   TH1D *hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95 = new TH1D("hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95","",8,0,8);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->SetMinimum(0.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->SetMaximum(50);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->SetLineColor(ci);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetBinLabel(1,"B^{-}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetBinLabel(2,"B_{c}^{-}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetBinLabel(3,"#barB^{0}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetBinLabel(4,"#barB_{s}^{0}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetBinLabel(5,"#Lambda_{b}^{0}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetBinLabel(6,"#Sigma_{b}^{+}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetBinLabel(7,"#Sigma_{b}^{0}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetBinLabel(8,"#Sigma_{b}^{-}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetLabelFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetLabelSize(0.06);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetTitleSize(0.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetTickLength(0.035);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetTitleOffset(1.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetXaxis()->SetTitleFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetYaxis()->SetTitle("JUN / MON");
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetYaxis()->SetLabelFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetYaxis()->SetLabelSize(0.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetYaxis()->SetTitleSize(0.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetYaxis()->SetTitleOffset(1.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetYaxis()->SetTitleFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetZaxis()->SetLabelFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetZaxis()->SetTitleOffset(1);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->GetZaxis()->SetTitleFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__95->Draw("PE");
   
   leg = new TLegend(0.25,0.85,0.4,0.95,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.05);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("NULL","(e)","");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96","hYieldsRatio_0_0",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->SetBinContent(1,0.8605802);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->SetBinError(1,0.001974704);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__96->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97","hYieldsRatio_0_1",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->SetBinContent(1,0.6860615);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->SetBinError(1,0.001701614);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__97->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98","hYieldsRatio_0_2",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->SetBinContent(1,0.6377938);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->SetBinError(1,0.002597825);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__98->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99","hYieldsRatio_6_6",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->SetBinContent(2,0.521882);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->SetBinError(2,0.04211226);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__99->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100","hYieldsRatio_6_7",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->SetBinContent(2,0.4697256);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->SetBinError(2,0.03736381);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__100->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101","hYieldsRatio_6_8",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->SetBinContent(2,0.5985412);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->SetBinError(2,0.0342687);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__101->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102","hYieldsRatio_12_12",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->SetBinContent(3,0.85583);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->SetBinError(3,0.001650542);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__102->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103","hYieldsRatio_12_13",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->SetBinContent(3,0.6816084);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->SetBinError(3,0.001795274);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__103->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104","hYieldsRatio_12_14",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->SetBinContent(3,0.6336932);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->SetBinError(3,0.001605749);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__104->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105","hYieldsRatio_18_18",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->SetBinContent(4,0.7667487);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->SetBinError(4,0.004509014);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__105->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106","hYieldsRatio_18_19",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->SetBinContent(4,0.583797);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->SetBinError(4,0.004588433);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__106->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107","hYieldsRatio_18_20",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->SetBinContent(4,0.5407773);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->SetBinError(4,0.003739795);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__107->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108","hYieldsRatio_24_24",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->SetBinContent(5,1.565106);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->SetBinError(5,0.01446808);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__108->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109","hYieldsRatio_24_25",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->SetBinContent(5,2.574736);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->SetBinError(5,0.02326538);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__109->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110","hYieldsRatio_24_26",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->SetBinContent(5,2.895448);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->SetBinError(5,0.02308443);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__110->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111","hYieldsRatio_30_30",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->SetBinContent(6,19.35778);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->SetBinError(6,0.3798324);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__111->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112","hYieldsRatio_30_31",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->SetBinContent(6,27.54894);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->SetBinError(6,0.5334634);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__112->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113","hYieldsRatio_30_32",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->SetBinContent(6,23.49196);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->SetBinError(6,0.4326304);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__113->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114","hYieldsRatio_36_36",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->SetBinContent(7,20.55154);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->SetBinError(7,0.5552549);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__114->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115","hYieldsRatio_36_37",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->SetBinContent(7,30.78403);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->SetBinError(7,0.5981951);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__115->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116","hYieldsRatio_36_38",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->SetBinContent(7,26.60732);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->SetBinError(7,0.5399587);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__116->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117","hYieldsRatio_42_42",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->SetBinContent(8,19.2505);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->SetBinError(8,0.3327657);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_42__117->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118","hYieldsRatio_42_43",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->SetBinContent(8,27.62348);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->SetBinError(8,0.5159761);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_43__118->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119","hYieldsRatio_42_44",8,0,8);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->SetBinContent(8,23.61621);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->SetBinError(8,0.471633);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPBhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_42_44__119->Draw("same PE");
   c20mini_yields->Modified();
   c2x3_yields->cd();
  
// ------------>Primitives in pad: c21mini_yields
   TPad *c21mini_yields = new TPad("c21mini_yields", "yields ratio for charm",0.501,0,0.95,0.351);
   c21mini_yields->Draw();
   c21mini_yields->cd();
   c21mini_yields->Range(0,-1.830442,7.777778,1.69897);
   c21mini_yields->SetFillColor(0);
   c21mini_yields->SetBorderMode(0);
   c21mini_yields->SetBorderSize(2);
   c21mini_yields->SetLogy();
   c21mini_yields->SetTickx(1);
   c21mini_yields->SetLeftMargin(0);
   c21mini_yields->SetTopMargin(0);
   c21mini_yields->SetBottomMargin(0.15);
   c21mini_yields->SetFrameBorderMode(0);
   c21mini_yields->SetFrameBorderMode(0);
   
   TH1D *hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120 = new TH1D("hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120","",7,0,7);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->SetMinimum(0.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->SetMaximum(50);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->SetLineColor(ci);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetTitle("Associate");
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetBinLabel(1,"D^{-}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetBinLabel(2,"D_{s}^{-}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetBinLabel(3,"#barD^{0}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetBinLabel(4,"#bar#Lambda_{c}^{+}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetBinLabel(5,"#bar#Sigma_{c}^{++}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetBinLabel(6,"#bar#Sigma_{c}^{+}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetBinLabel(7,"#bar#Sigma_{c}^{0}");
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetLabelFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetLabelSize(0.06);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetTitleSize(0.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetTickLength(0.035);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetTitleOffset(1.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetXaxis()->SetTitleFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetYaxis()->SetTitle("JUN / MON");
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetYaxis()->SetLabelFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetYaxis()->SetLabelSize(0.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetYaxis()->SetTitleSize(0.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetYaxis()->SetTitleOffset(1.05);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetYaxis()->SetTitleFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetZaxis()->SetLabelFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetZaxis()->SetTitleOffset(1);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->GetZaxis()->SetTitleFont(42);
   hYieldsRatioTemplate_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity__120->Draw("PE");
   
   leg = new TLegend(0.05,0.85,0.2,0.95,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.05);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("NULL","(f)","");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121","hYieldsRatio_0_0",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->SetBinContent(1,0.9412902);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->SetBinError(1,0.003586159);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_0__121->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122","hYieldsRatio_0_1",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->SetBinContent(1,0.8957995);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->SetBinError(1,0.002620892);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_1__122->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123","hYieldsRatio_0_2",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->SetBinContent(1,0.8896359);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->SetBinError(1,0.005536947);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_0_2__123->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124","hYieldsRatio_6_6",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->SetBinContent(2,0.8646933);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->SetBinError(2,0.009688112);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_6__124->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125","hYieldsRatio_6_7",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->SetBinContent(2,0.820646);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->SetBinError(2,0.00884451);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_7__125->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126","hYieldsRatio_6_8",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->SetBinContent(2,0.816592);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->SetBinError(2,0.0072621);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_6_8__126->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127","hYieldsRatio_12_12",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->SetBinContent(3,0.942071);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->SetBinError(3,0.00350919);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_12__127->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128","hYieldsRatio_12_13",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->SetBinContent(3,0.8968266);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->SetBinError(3,0.004589487);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_13__128->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129","hYieldsRatio_12_14",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->SetBinContent(3,0.8951355);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->SetBinError(3,0.004088762);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_12_14__129->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130","hYieldsRatio_18_18",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->SetBinContent(4,0.9271206);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->SetBinError(4,0.01136887);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_18__130->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131","hYieldsRatio_18_19",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->SetBinContent(4,1.042128);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->SetBinError(4,0.01766228);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_19__131->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132","hYieldsRatio_18_20",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->SetBinContent(4,1.159314);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->SetBinError(4,0.01183072);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_18_20__132->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133","hYieldsRatio_24_24",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->SetBinContent(5,2.785934);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->SetBinError(5,0.07602631);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_24__133->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134","hYieldsRatio_24_25",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->SetBinContent(5,7.375256);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->SetBinError(5,0.2952995);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_25__134->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135","hYieldsRatio_24_26",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->SetBinContent(5,10.99061);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->SetBinError(5,0.4806592);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_24_26__135->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136","hYieldsRatio_30_30",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->SetBinContent(6,2.820348);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->SetBinError(6,0.14467);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_30__136->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137","hYieldsRatio_30_31",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->SetBinContent(6,7.79087);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->SetBinError(6,0.3291411);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_31__137->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138","hYieldsRatio_30_32",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->SetBinContent(6,11.67503);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->SetBinError(6,0.473999);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_30_32__138->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139","hYieldsRatio_36_36",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->SetBinContent(7,2.669169);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->SetBinError(7,0.09476128);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->SetLineWidth(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_36__139->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140","hYieldsRatio_36_37",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->SetBinContent(7,7.495251);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->SetBinError(7,0.3081348);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->SetLineStyle(2);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_37__140->Draw("same PE");
   
   TH1D *hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141 = new TH1D("hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141","hYieldsRatio_36_38",7,0,7);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->SetBinContent(7,11.01511);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->SetBinError(7,0.3891396);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->SetEntries(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->SetLineStyle(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->SetLineWidth(3);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->GetXaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->GetXaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->GetXaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->GetYaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->GetYaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->GetZaxis()->SetLabelFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->GetZaxis()->SetTitleOffset(1);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->GetZaxis()->SetTitleFont(42);
   hYieldsRatio_integratedsPyieldssPforsPpromptsPDhA{pL}sPtriggersPassPfunctionsPofsPmultiplicity_36_38__141->Draw("same PE");
   c21mini_yields->Modified();
   c2x3_yields->cd();
   c2x3_yields->Modified();
   c2x3_yields->cd();
   c2x3_yields->SetSelected(c2x3_yields);
}
