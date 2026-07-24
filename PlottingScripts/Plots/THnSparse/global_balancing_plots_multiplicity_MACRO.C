#ifdef __CLING__
#pragma cling optimize(0)
#endif
void global_balancing_plots_multiplicity_MACRO()
{
//=========Macro generated from canvas: global_balancing_plots/global_balancing_plots
//=========  (Wed Jul 15 22:32:51 2026) by ROOT version 6.30/01
   TCanvas *global_balancing_plots = new TCanvas("global_balancing_plots", "global_balancing_plots",0,0,1000,950);
   global_balancing_plots->Range(0,0,1,1);
   global_balancing_plots->SetFillColor(0);
   global_balancing_plots->SetBorderMode(0);
   global_balancing_plots->SetBorderSize(2);
   global_balancing_plots->SetFrameBorderMode(0);
  
// ------------>Primitives in pad: cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING
   TPad *cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44 = new TPad("cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING", "cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING",0.05,0.76,0.5,0.95);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->Draw();
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->cd();
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->Range(-0.2634352,-4.003911,5.005269,-0.0929991);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetFillColor(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetBorderMode(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetBorderSize(2);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetLogy();
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetTickx(1);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetTicky(1);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetLeftMargin(0.05);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetRightMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetTopMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetBottomMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetFrameBorderMode(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->SetFrameBorderMode(0);
   
   TH1D *hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111 = new TH1D("hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111","",5,0,5);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->SetMinimum(0.0001);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->SetMaximum(0.8);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->SetStats(0);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->SetLineColor(ci);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->GetXaxis()->SetLabelFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->GetXaxis()->SetTitleOffset(1);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->GetXaxis()->SetTitleFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->GetYaxis()->SetTitle("yield");
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->GetYaxis()->SetLabelFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->GetYaxis()->SetTitleFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->GetZaxis()->SetLabelFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->GetZaxis()->SetTitleOffset(1);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->GetZaxis()->SetTitleFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING__111->Draw("PE");
   
   TH1D *hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112 = new TH1D("hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112","hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->SetBinContent(1,0.07941868);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->SetBinError(1,0.0008843924);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->SetLineColor(ci);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING__112->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113 = new TH1D("hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113","hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->SetBinContent(1,0.07801556);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->SetBinError(1,0.0002374273);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->SetLineColor(ci);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->SetLineStyle(2);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING__113->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114 = new TH1D("hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114","hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->SetBinContent(1,0.08267929);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->SetBinError(1,0.0004409664);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->SetLineColor(ci);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->SetLineStyle(3);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING__114->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115 = new TH1D("hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115","hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->SetBinContent(1,0.08564956);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->SetBinError(1,0.0004521401);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->SetLineColor(ci);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->SetLineStyle(4);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING__115->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116 = new TH1D("hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116","hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->SetBinContent(1,0.09225949);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->SetBinError(1,0.0005106971);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->SetLineColor(ci);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->SetLineStyle(5);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING__116->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117 = new TH1D("hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117","hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->SetBinContent(1,0.09524143);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->SetBinError(1,0.0005511355);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->SetLineColor(ci);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->SetLineStyle(6);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING__117->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118 = new TH1D("hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118","hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->SetBinContent(1,0.09829722);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->SetBinError(1,0.0007618896);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->SetLineColor(ci);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->SetLineStyle(7);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING__118->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119 = new TH1D("hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119","hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->SetBinContent(1,0.1022005);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->SetBinError(1,0.0006829427);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->SetLineColor(ci);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->SetLineStyle(8);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING__119->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120 = new TH1D("hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120","hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->SetBinContent(1,0.1022005);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->SetBinError(1,0.0006829427);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->SetLineColor(ci);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->SetLineStyle(9);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING__120->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121 = new TH1D("hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121","hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->SetBinContent(1,0.1022005);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->SetBinError(1,0.0006829427);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->SetLineColor(ci);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->SetLineStyle(10);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING__121->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122 = new TH1D("hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122","hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->SetBinContent(1,0.1024401);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->SetBinError(1,0.002160481);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->SetLineColor(ci);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING__122->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123 = new TH1D("hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123","hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->SetBinContent(2,0.0002251361);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->SetBinError(2,3.124616e-05);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->SetLineColor(ci);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_0_mini_beauty_balancing_CLOSEPACKING__123->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124 = new TH1D("hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124","hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->SetBinContent(2,0.0001967761);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->SetBinError(2,1.699622e-05);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->SetLineColor(ci);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->SetLineStyle(2);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_1_mini_beauty_balancing_CLOSEPACKING__124->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125 = new TH1D("hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125","hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->SetBinContent(2,0.0001396918);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->SetBinError(2,1.550281e-05);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->SetLineColor(ci);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->SetLineStyle(3);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_2_mini_beauty_balancing_CLOSEPACKING__125->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126 = new TH1D("hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126","hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->SetBinContent(2,9.500783e-05);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->SetBinError(2,1.788256e-05);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->SetLineColor(ci);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->SetLineStyle(4);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_3_mini_beauty_balancing_CLOSEPACKING__126->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127 = new TH1D("hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127","hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->SetBinContent(2,7.103988e-05);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->SetBinError(2,2.35291e-05);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->SetLineColor(ci);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->SetLineStyle(5);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_4_mini_beauty_balancing_CLOSEPACKING__127->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128 = new TH1D("hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128","hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->SetBinContent(2,7.190882e-05);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->SetBinError(2,1.776109e-05);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->SetLineColor(ci);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->SetLineStyle(6);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_5_mini_beauty_balancing_CLOSEPACKING__128->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129 = new TH1D("hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129","hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->SetBinContent(2,7.279928e-05);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->SetBinError(2,2.420519e-05);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->SetLineColor(ci);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->SetLineStyle(7);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_6_mini_beauty_balancing_CLOSEPACKING__129->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130 = new TH1D("hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130","hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->SetBinContent(2,6.507512e-05);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->SetBinError(2,2.430512e-05);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->SetLineColor(ci);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->SetLineStyle(8);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_7_mini_beauty_balancing_CLOSEPACKING__130->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131 = new TH1D("hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131","hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->SetBinContent(2,6.507512e-05);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->SetBinError(2,2.430512e-05);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->SetLineColor(ci);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->SetLineStyle(9);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_8_mini_beauty_balancing_CLOSEPACKING__131->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132 = new TH1D("hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132","hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->SetBinContent(2,6.507512e-05);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->SetBinError(2,2.430512e-05);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->SetLineColor(ci);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->SetLineStyle(10);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_9_mini_beauty_balancing_CLOSEPACKING__132->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133 = new TH1D("hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133","hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->SetBinContent(2,8.371003e-05);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->SetBinError(2,5.541715e-05);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->SetLineColor(ci);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_10_mini_beauty_balancing_CLOSEPACKING__133->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134 = new TH1D("hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134","hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->SetBinContent(3,0.01713363);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->SetBinError(3,0.0003195647);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->SetLineColor(ci);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_0_mini_beauty_balancing_CLOSEPACKING__134->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135 = new TH1D("hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135","hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->SetBinContent(3,0.01795582);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->SetBinError(3,0.0001684836);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->SetLineColor(ci);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->SetLineStyle(2);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_1_mini_beauty_balancing_CLOSEPACKING__135->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136 = new TH1D("hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136","hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->SetBinContent(3,0.0184866);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->SetBinError(3,0.0002035061);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->SetLineColor(ci);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->SetLineStyle(3);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_2_mini_beauty_balancing_CLOSEPACKING__136->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137 = new TH1D("hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137","hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->SetBinContent(3,0.01940781);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->SetBinError(3,0.000342);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->SetLineColor(ci);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->SetLineStyle(4);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_3_mini_beauty_balancing_CLOSEPACKING__137->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138 = new TH1D("hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138","hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->SetBinContent(3,0.01951466);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->SetBinError(3,0.0002563126);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->SetLineColor(ci);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->SetLineStyle(5);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_4_mini_beauty_balancing_CLOSEPACKING__138->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139 = new TH1D("hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139","hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->SetBinContent(3,0.02102973);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->SetBinError(3,0.0002996669);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->SetLineColor(ci);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->SetLineStyle(6);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_5_mini_beauty_balancing_CLOSEPACKING__139->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140 = new TH1D("hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140","hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->SetBinContent(3,0.02258234);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->SetBinError(3,0.0005544821);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->SetLineColor(ci);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->SetLineStyle(7);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_6_mini_beauty_balancing_CLOSEPACKING__140->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141 = new TH1D("hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141","hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->SetBinContent(3,0.02285066);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->SetBinError(3,0.000433536);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->SetLineColor(ci);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->SetLineStyle(8);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_7_mini_beauty_balancing_CLOSEPACKING__141->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142 = new TH1D("hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142","hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->SetBinContent(3,0.02285066);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->SetBinError(3,0.000433536);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->SetLineColor(ci);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->SetLineStyle(9);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_8_mini_beauty_balancing_CLOSEPACKING__142->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143 = new TH1D("hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143","hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->SetBinContent(3,0.02285066);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->SetBinError(3,0.000433536);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->SetLineColor(ci);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->SetLineStyle(10);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_9_mini_beauty_balancing_CLOSEPACKING__143->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144 = new TH1D("hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144","hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->SetBinContent(3,0.02440147);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->SetBinError(3,0.000518811);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->SetLineColor(ci);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_10_mini_beauty_balancing_CLOSEPACKING__144->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145 = new TH1D("hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145","hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->SetBinContent(4,0.07851038);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->SetBinError(4,0.0004641066);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->SetLineColor(ci);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_0_mini_beauty_balancing_CLOSEPACKING__145->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146 = new TH1D("hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146","hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->SetBinContent(4,0.07573665);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->SetBinError(4,0.0002106279);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->SetLineColor(ci);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->SetLineStyle(2);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_1_mini_beauty_balancing_CLOSEPACKING__146->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147 = new TH1D("hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147","hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->SetBinContent(4,0.08096968);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->SetBinError(4,0.0003327375);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->SetLineColor(ci);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->SetLineStyle(3);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_2_mini_beauty_balancing_CLOSEPACKING__147->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148 = new TH1D("hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148","hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->SetBinContent(4,0.08494355);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->SetBinError(4,0.0004962338);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->SetLineColor(ci);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->SetLineStyle(4);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_3_mini_beauty_balancing_CLOSEPACKING__148->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149 = new TH1D("hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149","hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->SetBinContent(4,0.09046929);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->SetBinError(4,0.0008001937);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->SetLineColor(ci);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->SetLineStyle(5);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_4_mini_beauty_balancing_CLOSEPACKING__149->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150 = new TH1D("hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150","hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->SetBinContent(4,0.09393809);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->SetBinError(4,0.0003369071);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->SetLineColor(ci);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->SetLineStyle(6);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_5_mini_beauty_balancing_CLOSEPACKING__150->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151 = new TH1D("hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151","hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->SetBinContent(4,0.09749279);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->SetBinError(4,0.000822976);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->SetLineColor(ci);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->SetLineStyle(7);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_6_mini_beauty_balancing_CLOSEPACKING__151->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152 = new TH1D("hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152","hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->SetBinContent(4,0.1010895);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->SetBinError(4,0.001251561);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->SetLineColor(ci);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->SetLineStyle(8);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_7_mini_beauty_balancing_CLOSEPACKING__152->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153 = new TH1D("hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153","hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->SetBinContent(4,0.1010895);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->SetBinError(4,0.001251561);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->SetLineColor(ci);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->SetLineStyle(9);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_8_mini_beauty_balancing_CLOSEPACKING__153->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154 = new TH1D("hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154","hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->SetBinContent(4,0.1010895);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->SetBinError(4,0.001251561);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->SetLineColor(ci);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->SetLineStyle(10);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_9_mini_beauty_balancing_CLOSEPACKING__154->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155 = new TH1D("hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155","hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->SetBinContent(4,0.1014147);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->SetBinError(4,0.001815189);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->SetLineColor(ci);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_10_mini_beauty_balancing_CLOSEPACKING__155->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156 = new TH1D("hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156","hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->SetBinContent(5,0.04144056);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->SetBinError(5,0.0002202563);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->SetLineColor(ci);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_0_mini_beauty_balancing_CLOSEPACKING__156->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157 = new TH1D("hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157","hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->SetBinContent(5,0.03756455);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->SetBinError(5,0.0002357117);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->SetLineColor(ci);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->SetLineStyle(2);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_1_mini_beauty_balancing_CLOSEPACKING__157->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158 = new TH1D("hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158","hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->SetBinContent(5,0.03179816);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->SetBinError(5,0.0003927383);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->SetLineColor(ci);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->SetLineStyle(3);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_2_mini_beauty_balancing_CLOSEPACKING__158->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159 = new TH1D("hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159","hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->SetBinContent(5,0.02930173);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->SetBinError(5,0.000211543);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->SetLineColor(ci);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->SetLineStyle(4);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_3_mini_beauty_balancing_CLOSEPACKING__159->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160 = new TH1D("hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160","hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->SetBinContent(5,0.02539676);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->SetBinError(5,0.000304509);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->SetLineColor(ci);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->SetLineStyle(5);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_4_mini_beauty_balancing_CLOSEPACKING__160->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161 = new TH1D("hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161","hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->SetBinContent(5,0.02393485);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->SetBinError(5,0.0002959147);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->SetLineColor(ci);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->SetLineStyle(6);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_5_mini_beauty_balancing_CLOSEPACKING__161->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162 = new TH1D("hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162","hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->SetBinContent(5,0.02243674);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->SetBinError(5,0.0004154444);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->SetLineColor(ci);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->SetLineStyle(7);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_6_mini_beauty_balancing_CLOSEPACKING__162->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163 = new TH1D("hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163","hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->SetBinContent(5,0.02044288);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->SetBinError(5,0.0002657112);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->SetLineColor(ci);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->SetLineStyle(8);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_7_mini_beauty_balancing_CLOSEPACKING__163->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164 = new TH1D("hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164","hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->SetBinContent(5,0.02044288);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->SetBinError(5,0.0002657112);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->SetLineColor(ci);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->SetLineStyle(9);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_8_mini_beauty_balancing_CLOSEPACKING__164->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165 = new TH1D("hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165","hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->SetBinContent(5,0.02044288);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->SetBinError(5,0.0002657112);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->SetLineColor(ci);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->SetLineStyle(10);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_9_mini_beauty_balancing_CLOSEPACKING__165->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166 = new TH1D("hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166","hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING",5,0,5);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->SetBinContent(5,0.01967186);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->SetBinError(5,0.0004891341);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->SetLineColor(ci);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_10_mini_beauty_balancing_CLOSEPACKING__166->Draw("same PE");
   
   TLegend *leg = new TLegend(0.63,0.68,0.9,0.88,NULL,"brNDC");
   leg->SetBorderSize(1);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   TLegendEntry *entry=leg->AddEntry("hYields_BEAUTY_2_0_0_mini_beauty_balancing_CLOSEPACKING","0-1%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_2_0_1_mini_beauty_balancing_CLOSEPACKING","1-10%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(2);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_2_0_2_mini_beauty_balancing_CLOSEPACKING","10-20%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(3);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_2_0_3_mini_beauty_balancing_CLOSEPACKING","20-30%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(4);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_2_0_4_mini_beauty_balancing_CLOSEPACKING","30-40%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(5);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_2_0_5_mini_beauty_balancing_CLOSEPACKING","40-50%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(6);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_2_0_6_mini_beauty_balancing_CLOSEPACKING","50-60%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(7);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_2_0_7_mini_beauty_balancing_CLOSEPACKING","60-70%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(8);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_2_0_8_mini_beauty_balancing_CLOSEPACKING","70-80%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(9);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_2_0_9_mini_beauty_balancing_CLOSEPACKING","80-90%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(10);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_2_0_10_mini_beauty_balancing_CLOSEPACKING","90-100%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING__44->Modified();
   global_balancing_plots->cd();
  
// ------------>Primitives in pad: cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS
   TPad *cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45 = new TPad("cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS", "cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS",0.05,0.57,0.5,0.759);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->Draw();
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->cd();
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->Range(-0.2634352,-4.003911,5.005269,-0.0929991);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetFillColor(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetBorderMode(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetBorderSize(2);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetLogy();
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetTickx(1);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetTicky(1);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetLeftMargin(0.05);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetRightMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetTopMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetBottomMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetFrameBorderMode(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->SetFrameBorderMode(0);
   
   TH1D *hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167 = new TH1D("hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167","",5,0,5);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->SetMinimum(0.0001);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->SetMaximum(0.8);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->SetLineColor(ci);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->GetXaxis()->SetLabelFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->GetXaxis()->SetTitleOffset(1);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->GetXaxis()->SetTitleFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->GetYaxis()->SetTitle("yield");
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->GetYaxis()->SetLabelFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->GetYaxis()->SetTitleFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->GetZaxis()->SetLabelFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->GetZaxis()->SetTitleOffset(1);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->GetZaxis()->SetTitleFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS__167->Draw("PE");
   
   TH1D *hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168 = new TH1D("hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168","hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->SetBinContent(1,0.08202858);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->SetBinError(1,0.0008975451);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->SetLineColor(ci);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS__168->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169 = new TH1D("hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169","hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->SetBinContent(1,0.07914677);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->SetBinError(1,0.0002992768);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->SetLineColor(ci);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->SetLineStyle(2);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS__169->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170 = new TH1D("hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170","hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->SetBinContent(1,0.08379824);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->SetBinError(1,0.0003043884);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->SetLineColor(ci);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->SetLineStyle(3);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS__170->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171 = new TH1D("hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171","hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->SetBinContent(1,0.08903434);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->SetBinError(1,0.0003446627);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->SetLineColor(ci);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->SetLineStyle(4);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS__171->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172 = new TH1D("hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172","hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->SetBinContent(1,0.09176641);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->SetBinError(1,0.0002889855);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->SetLineColor(ci);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->SetLineStyle(5);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS__172->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173 = new TH1D("hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173","hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->SetBinContent(1,0.09628493);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->SetBinError(1,0.0004958993);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->SetLineColor(ci);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->SetLineStyle(6);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS__173->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174 = new TH1D("hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174","hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->SetBinContent(1,0.09915924);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->SetBinError(1,0.0008097531);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->SetLineColor(ci);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->SetLineStyle(7);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS__174->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175 = new TH1D("hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175","hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->SetBinContent(1,0.09995289);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->SetBinError(1,0.0006179377);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->SetLineColor(ci);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->SetLineStyle(8);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS__175->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176 = new TH1D("hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176","hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->SetBinContent(1,0.1010049);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->SetBinError(1,0.0006427429);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->SetLineColor(ci);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->SetLineStyle(9);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS__176->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177 = new TH1D("hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177","hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->SetBinContent(1,0.1010049);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->SetBinError(1,0.0006427429);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->SetLineColor(ci);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->SetLineStyle(10);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS__177->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178 = new TH1D("hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178","hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->SetBinContent(1,0.1003568);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->SetBinError(1,0.00168594);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->SetLineColor(ci);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS__178->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179 = new TH1D("hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179","hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->SetBinContent(2,0.0003217201);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->SetBinError(2,5.774562e-05);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->SetLineColor(ci);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_0_mini_beauty_balancing_JUNCTIONS__179->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180 = new TH1D("hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180","hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->SetBinContent(2,0.0002287237);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->SetBinError(2,1.415116e-05);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->SetLineColor(ci);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->SetLineStyle(2);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_1_mini_beauty_balancing_JUNCTIONS__180->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181 = new TH1D("hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181","hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->SetBinContent(2,0.0001375126);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->SetBinError(2,1.236632e-05);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->SetLineColor(ci);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->SetLineStyle(3);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_2_mini_beauty_balancing_JUNCTIONS__181->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182 = new TH1D("hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182","hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->SetBinContent(2,9.251615e-05);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->SetBinError(2,1.608119e-05);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->SetLineColor(ci);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->SetLineStyle(4);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_3_mini_beauty_balancing_JUNCTIONS__182->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183 = new TH1D("hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183","hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->SetBinContent(2,7.844719e-05);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->SetBinError(2,1.797171e-05);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->SetLineColor(ci);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->SetLineStyle(5);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_4_mini_beauty_balancing_JUNCTIONS__183->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184 = new TH1D("hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184","hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->SetBinContent(2,9.396325e-05);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->SetBinError(2,2.341228e-05);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->SetLineColor(ci);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->SetLineStyle(6);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_5_mini_beauty_balancing_JUNCTIONS__184->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185 = new TH1D("hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185","hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->SetBinContent(2,0.0001112542);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->SetBinError(2,3.97594e-05);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->SetLineColor(ci);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->SetLineStyle(7);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_6_mini_beauty_balancing_JUNCTIONS__185->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186 = new TH1D("hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186","hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->SetBinContent(2,0.0001177675);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->SetBinError(2,3.326151e-05);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->SetLineColor(ci);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->SetLineStyle(8);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_7_mini_beauty_balancing_JUNCTIONS__186->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187 = new TH1D("hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187","hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->SetBinContent(2,0.0001264009);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->SetBinError(2,3.438475e-05);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->SetLineColor(ci);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->SetLineStyle(9);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_8_mini_beauty_balancing_JUNCTIONS__187->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188 = new TH1D("hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188","hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->SetBinContent(2,0.0001264009);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->SetBinError(2,3.438475e-05);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->SetLineColor(ci);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->SetLineStyle(10);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_9_mini_beauty_balancing_JUNCTIONS__188->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189 = new TH1D("hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189","hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->SetLineColor(ci);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_10_mini_beauty_balancing_JUNCTIONS__189->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190 = new TH1D("hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190","hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->SetBinContent(3,0.01601228);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->SetBinError(3,0.0003093362);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->SetLineColor(ci);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_0_mini_beauty_balancing_JUNCTIONS__190->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191 = new TH1D("hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191","hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->SetBinContent(3,0.01539551);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->SetBinError(3,0.0001401426);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->SetLineColor(ci);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->SetLineStyle(2);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_1_mini_beauty_balancing_JUNCTIONS__191->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192 = new TH1D("hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192","hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->SetBinContent(3,0.0162874);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->SetBinError(3,0.0001675266);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->SetLineColor(ci);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->SetLineStyle(3);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_2_mini_beauty_balancing_JUNCTIONS__192->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193 = new TH1D("hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193","hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->SetBinContent(3,0.01693757);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->SetBinError(3,0.0002993291);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->SetLineColor(ci);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->SetLineStyle(4);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_3_mini_beauty_balancing_JUNCTIONS__193->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194 = new TH1D("hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194","hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->SetBinContent(3,0.0180055);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->SetBinError(3,0.0002647195);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->SetLineColor(ci);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->SetLineStyle(5);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_4_mini_beauty_balancing_JUNCTIONS__194->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195 = new TH1D("hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195","hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->SetBinContent(3,0.0193486);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->SetBinError(3,0.0003049792);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->SetLineColor(ci);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->SetLineStyle(6);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_5_mini_beauty_balancing_JUNCTIONS__195->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196 = new TH1D("hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196","hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->SetBinContent(3,0.01992244);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->SetBinError(3,0.0003339702);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->SetLineColor(ci);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->SetLineStyle(7);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_6_mini_beauty_balancing_JUNCTIONS__196->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197 = new TH1D("hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197","hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->SetBinContent(3,0.02098073);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->SetBinError(3,0.0003570297);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->SetLineColor(ci);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->SetLineStyle(8);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_7_mini_beauty_balancing_JUNCTIONS__197->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198 = new TH1D("hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198","hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->SetBinContent(3,0.0223835);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->SetBinError(3,0.0008295597);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->SetLineColor(ci);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->SetLineStyle(9);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_8_mini_beauty_balancing_JUNCTIONS__198->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199 = new TH1D("hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199","hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->SetBinContent(3,0.0223835);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->SetBinError(3,0.0008295597);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->SetLineColor(ci);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->SetLineStyle(10);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_9_mini_beauty_balancing_JUNCTIONS__199->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200 = new TH1D("hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200","hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->SetBinContent(3,0.02125382);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->SetBinError(3,0.0007882944);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->SetLineColor(ci);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_10_mini_beauty_balancing_JUNCTIONS__200->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201 = new TH1D("hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201","hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->SetBinContent(4,0.07772892);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->SetBinError(4,0.0005959043);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->SetLineColor(ci);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_0_mini_beauty_balancing_JUNCTIONS__201->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202 = new TH1D("hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202","hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->SetBinContent(4,0.07750392);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->SetBinError(4,0.0002036423);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->SetLineColor(ci);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->SetLineStyle(2);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_1_mini_beauty_balancing_JUNCTIONS__202->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203 = new TH1D("hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203","hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->SetBinContent(4,0.08293051);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->SetBinError(4,0.0002964412);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->SetLineColor(ci);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->SetLineStyle(3);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_2_mini_beauty_balancing_JUNCTIONS__203->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204 = new TH1D("hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204","hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->SetBinContent(4,0.08743844);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->SetBinError(4,0.0007029365);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->SetLineColor(ci);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->SetLineStyle(4);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_3_mini_beauty_balancing_JUNCTIONS__204->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205 = new TH1D("hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205","hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->SetBinContent(4,0.09141713);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->SetBinError(4,0.0003910843);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->SetLineColor(ci);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->SetLineStyle(5);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_4_mini_beauty_balancing_JUNCTIONS__205->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206 = new TH1D("hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206","hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->SetBinContent(4,0.09647285);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->SetBinError(4,0.0005990432);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->SetLineColor(ci);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->SetLineStyle(6);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_5_mini_beauty_balancing_JUNCTIONS__206->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207 = new TH1D("hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207","hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->SetBinContent(4,0.09914334);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->SetBinError(4,0.0008168711);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->SetLineColor(ci);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->SetLineStyle(7);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_6_mini_beauty_balancing_JUNCTIONS__207->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208 = new TH1D("hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208","hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->SetBinContent(4,0.1011396);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->SetBinError(4,0.0006128009);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->SetLineColor(ci);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->SetLineStyle(8);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_7_mini_beauty_balancing_JUNCTIONS__208->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209 = new TH1D("hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209","hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->SetBinContent(4,0.1037857);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->SetBinError(4,0.000634506);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->SetLineColor(ci);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->SetLineStyle(9);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_8_mini_beauty_balancing_JUNCTIONS__209->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210 = new TH1D("hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210","hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->SetBinContent(4,0.1037857);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->SetBinError(4,0.000634506);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->SetLineColor(ci);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->SetLineStyle(10);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_9_mini_beauty_balancing_JUNCTIONS__210->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211 = new TH1D("hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211","hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->SetBinContent(4,0.1037207);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->SetBinError(4,0.002401543);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->SetLineColor(ci);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_10_mini_beauty_balancing_JUNCTIONS__211->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212 = new TH1D("hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212","hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->SetBinContent(5,0.04461856);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->SetBinError(5,0.0007936169);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->SetLineColor(ci);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_0_mini_beauty_balancing_JUNCTIONS__212->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213 = new TH1D("hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213","hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->SetBinContent(5,0.04075669);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->SetBinError(5,0.0002654534);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->SetLineColor(ci);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->SetLineStyle(2);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_1_mini_beauty_balancing_JUNCTIONS__213->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214 = new TH1D("hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214","hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->SetBinContent(5,0.03518929);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->SetBinError(5,0.0001903448);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->SetLineColor(ci);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->SetLineStyle(3);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_2_mini_beauty_balancing_JUNCTIONS__214->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215 = new TH1D("hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215","hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->SetBinContent(5,0.03097156);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->SetBinError(5,0.0005279782);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->SetLineColor(ci);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->SetLineStyle(4);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_3_mini_beauty_balancing_JUNCTIONS__215->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216 = new TH1D("hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216","hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->SetBinContent(5,0.02881253);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->SetBinError(5,0.0003706632);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->SetLineColor(ci);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->SetLineStyle(5);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_4_mini_beauty_balancing_JUNCTIONS__216->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217 = new TH1D("hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217","hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->SetBinContent(5,0.02629014);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->SetBinError(5,0.000270571);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->SetLineColor(ci);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->SetLineStyle(6);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_5_mini_beauty_balancing_JUNCTIONS__217->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218 = new TH1D("hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218","hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->SetBinContent(5,0.02446002);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->SetBinError(5,0.0005019051);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->SetLineColor(ci);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->SetLineStyle(7);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_6_mini_beauty_balancing_JUNCTIONS__218->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219 = new TH1D("hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219","hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->SetBinContent(5,0.02306431);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->SetBinError(5,0.0003344119);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->SetLineColor(ci);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->SetLineStyle(8);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_7_mini_beauty_balancing_JUNCTIONS__219->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220 = new TH1D("hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220","hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->SetBinContent(5,0.02121429);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->SetBinError(5,0.0005742262);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->SetLineColor(ci);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->SetLineStyle(9);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_8_mini_beauty_balancing_JUNCTIONS__220->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221 = new TH1D("hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221","hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->SetBinContent(5,0.02121429);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->SetBinError(5,0.0005742262);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->SetLineColor(ci);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->SetLineStyle(10);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_9_mini_beauty_balancing_JUNCTIONS__221->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222 = new TH1D("hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222","hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS",5,0,5);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->SetBinContent(5,0.02089704);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->SetBinError(5,0.001136803);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->SetLineColor(ci);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_10_mini_beauty_balancing_JUNCTIONS__222->Draw("same PE");
   
   leg = new TLegend(0.63,0.68,0.9,0.88,NULL,"brNDC");
   leg->SetBorderSize(1);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("hYields_BEAUTY_1_0_0_mini_beauty_balancing_JUNCTIONS","0-1%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_1_0_1_mini_beauty_balancing_JUNCTIONS","1-10%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(2);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_1_0_2_mini_beauty_balancing_JUNCTIONS","10-20%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(3);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_1_0_3_mini_beauty_balancing_JUNCTIONS","20-30%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(4);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_1_0_4_mini_beauty_balancing_JUNCTIONS","30-40%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(5);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_1_0_5_mini_beauty_balancing_JUNCTIONS","40-50%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(6);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_1_0_6_mini_beauty_balancing_JUNCTIONS","50-60%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(7);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_1_0_7_mini_beauty_balancing_JUNCTIONS","60-70%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(8);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_1_0_8_mini_beauty_balancing_JUNCTIONS","70-80%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(9);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_1_0_9_mini_beauty_balancing_JUNCTIONS","80-90%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(10);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_1_0_10_mini_beauty_balancing_JUNCTIONS","90-100%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS__45->Modified();
   global_balancing_plots->cd();
  
// ------------>Primitives in pad: cMiniPad_BEAUTY_mini_beauty_balancing_MONASH
   TPad *cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46 = new TPad("cMiniPad_BEAUTY_mini_beauty_balancing_MONASH", "cMiniPad_BEAUTY_mini_beauty_balancing_MONASH",0.05,0.38,0.5,0.569);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->Draw();
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->cd();
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->Range(-0.2634352,-4.003911,5.005269,-0.0929991);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetFillColor(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetBorderMode(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetBorderSize(2);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetLogy();
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetTickx(1);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetTicky(1);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetLeftMargin(0.05);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetRightMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetTopMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetBottomMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetFrameBorderMode(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->SetFrameBorderMode(0);
   
   TH1D *hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223 = new TH1D("hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223","",5,0,5);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->SetMinimum(0.0001);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->SetMaximum(0.8);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->SetLineColor(ci);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetXaxis()->SetBinLabel(1,"B-");
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetXaxis()->SetBinLabel(2,"Bc-");
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetXaxis()->SetBinLabel(3,"B_s^0-bar");
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetXaxis()->SetBinLabel(4,"B^{0}-bar");
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetXaxis()->SetBinLabel(5,"Lambda_b");
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetXaxis()->SetLabelFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetXaxis()->SetTitleOffset(1);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetXaxis()->SetTitleFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetYaxis()->SetTitle("yield");
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetYaxis()->SetLabelFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetYaxis()->SetTitleFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetZaxis()->SetLabelFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetZaxis()->SetTitleOffset(1);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->GetZaxis()->SetTitleFont(42);
   hYieldsTemplate_BEAUTY_mini_beauty_balancing_MONASH__223->Draw("PE");
   
   TH1D *hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224 = new TH1D("hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224","hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->SetBinContent(1,0.1210016);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->SetBinError(1,0.0008776974);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->SetEntries(1);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->SetLineWidth(2);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->SetMarkerStyle(20);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH__224->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225 = new TH1D("hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225","hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->SetBinContent(1,0.1152791);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->SetBinError(1,0.0003622607);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->SetEntries(1);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->SetLineStyle(2);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->SetLineWidth(2);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->SetMarkerStyle(20);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH__225->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226 = new TH1D("hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226","hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->SetBinContent(1,0.1130191);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->SetBinError(1,0.0004529631);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->SetEntries(1);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->SetLineStyle(3);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->SetLineWidth(2);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->SetMarkerStyle(20);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH__226->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227 = new TH1D("hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227","hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->SetBinContent(1,0.1112031);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->SetBinError(1,0.0004002487);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->SetEntries(1);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->SetLineStyle(4);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->SetLineWidth(2);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->SetMarkerStyle(20);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH__227->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228 = new TH1D("hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228","hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->SetBinContent(1,0.1113163);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->SetBinError(1,0.000393679);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->SetEntries(1);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->SetLineStyle(5);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->SetLineWidth(2);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->SetMarkerStyle(20);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH__228->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229 = new TH1D("hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229","hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->SetBinContent(1,0.1110559);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->SetBinError(1,0.0007457405);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->SetEntries(1);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->SetLineStyle(6);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->SetLineWidth(2);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->SetMarkerStyle(20);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH__229->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230 = new TH1D("hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230","hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->SetBinContent(1,0.1110559);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->SetBinError(1,0.0007457405);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->SetEntries(1);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->SetLineStyle(7);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->SetLineWidth(2);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->SetMarkerStyle(20);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH__230->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231 = new TH1D("hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231","hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->SetBinContent(1,0.1089957);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->SetBinError(1,0.001000551);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->SetEntries(1);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->SetLineStyle(8);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->SetLineWidth(2);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->SetMarkerStyle(20);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH__231->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232 = new TH1D("hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232","hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->SetBinContent(1,0.1089957);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->SetBinError(1,0.001000551);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->SetEntries(1);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->SetLineStyle(9);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->SetLineWidth(2);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->SetMarkerStyle(20);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH__232->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233 = new TH1D("hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233","hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->SetBinContent(1,0.1089957);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->SetBinError(1,0.001000551);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->SetEntries(1);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->SetLineStyle(10);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->SetLineWidth(2);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->SetMarkerStyle(20);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH__233->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234 = new TH1D("hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234","hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->SetBinContent(1,0.103358);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->SetBinError(1,0.002310613);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->SetEntries(1);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->SetLineWidth(2);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->SetMarkerStyle(20);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH__234->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235 = new TH1D("hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235","hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->SetBinContent(2,0.0002769943);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->SetBinError(2,2.619004e-05);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->SetEntries(1);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->SetLineWidth(2);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->SetMarkerStyle(20);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_0_mini_beauty_balancing_MONASH__235->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236 = new TH1D("hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236","hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->SetBinContent(2,0.0003214005);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->SetBinError(2,1.385636e-05);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->SetEntries(1);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->SetLineStyle(2);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->SetLineWidth(2);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->SetMarkerStyle(20);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_1_mini_beauty_balancing_MONASH__236->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237 = new TH1D("hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237","hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->SetBinContent(2,0.0002405845);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->SetBinError(2,2.341716e-05);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->SetEntries(1);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->SetLineStyle(3);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->SetLineWidth(2);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->SetMarkerStyle(20);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_2_mini_beauty_balancing_MONASH__237->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238 = new TH1D("hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238","hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->SetBinContent(2,0.0002196243);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->SetBinError(2,2.794182e-05);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->SetEntries(1);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->SetLineStyle(4);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->SetLineWidth(2);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->SetMarkerStyle(20);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_3_mini_beauty_balancing_MONASH__238->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239 = new TH1D("hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239","hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->SetBinContent(2,0.0002370392);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->SetBinError(2,3.85415e-05);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->SetEntries(1);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->SetLineStyle(5);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->SetLineWidth(2);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->SetMarkerStyle(20);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_4_mini_beauty_balancing_MONASH__239->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240 = new TH1D("hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240","hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->SetBinContent(2,0.0001134712);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->SetBinError(2,1.499182e-05);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->SetEntries(1);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->SetLineStyle(6);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->SetLineWidth(2);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->SetMarkerStyle(20);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_5_mini_beauty_balancing_MONASH__240->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241 = new TH1D("hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241","hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->SetBinContent(2,0.0001134712);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->SetBinError(2,1.499182e-05);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->SetEntries(1);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->SetLineStyle(7);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->SetLineWidth(2);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->SetMarkerStyle(20);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_6_mini_beauty_balancing_MONASH__241->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242 = new TH1D("hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242","hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->SetBinContent(2,9.430267e-05);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->SetBinError(2,2.417784e-05);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->SetEntries(1);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->SetLineStyle(8);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->SetLineWidth(2);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->SetMarkerStyle(20);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_7_mini_beauty_balancing_MONASH__242->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243 = new TH1D("hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243","hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->SetBinContent(2,9.430267e-05);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->SetBinError(2,2.417784e-05);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->SetEntries(1);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->SetLineStyle(9);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->SetLineWidth(2);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->SetMarkerStyle(20);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_8_mini_beauty_balancing_MONASH__243->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244 = new TH1D("hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244","hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->SetBinContent(2,9.430267e-05);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->SetBinError(2,2.417784e-05);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->SetEntries(1);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->SetLineStyle(10);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->SetLineWidth(2);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->SetMarkerStyle(20);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_9_mini_beauty_balancing_MONASH__244->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245 = new TH1D("hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245","hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->SetBinContent(2,0.0001298196);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->SetBinError(2,6.647711e-05);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->SetEntries(1);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->SetLineWidth(2);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->SetMarkerStyle(20);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_10_mini_beauty_balancing_MONASH__245->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246 = new TH1D("hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246","hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->SetBinContent(3,0.02625593);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->SetBinError(3,0.0002647591);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->SetEntries(1);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->SetLineWidth(2);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->SetMarkerStyle(20);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_0_mini_beauty_balancing_MONASH__246->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247 = new TH1D("hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247","hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->SetBinContent(3,0.02569882);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->SetBinError(3,9.338871e-05);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->SetEntries(1);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->SetLineStyle(2);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->SetLineWidth(2);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->SetMarkerStyle(20);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_1_mini_beauty_balancing_MONASH__247->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248 = new TH1D("hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248","hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->SetBinContent(3,0.02520724);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->SetBinError(3,0.0002478301);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->SetEntries(1);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->SetLineStyle(3);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->SetLineWidth(2);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->SetMarkerStyle(20);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_2_mini_beauty_balancing_MONASH__248->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249 = new TH1D("hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249","hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->SetBinContent(3,0.02528709);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->SetBinError(3,0.0001769648);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->SetEntries(1);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->SetLineStyle(4);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->SetLineWidth(2);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->SetMarkerStyle(20);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_3_mini_beauty_balancing_MONASH__249->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250 = new TH1D("hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250","hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->SetBinContent(3,0.02526838);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->SetBinError(3,0.000256159);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->SetEntries(1);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->SetLineStyle(5);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->SetLineWidth(2);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->SetMarkerStyle(20);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_4_mini_beauty_balancing_MONASH__250->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251 = new TH1D("hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251","hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->SetBinContent(3,0.02494205);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->SetBinError(3,0.0002130903);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->SetEntries(1);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->SetLineStyle(6);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->SetLineWidth(2);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->SetMarkerStyle(20);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_5_mini_beauty_balancing_MONASH__251->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252 = new TH1D("hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252","hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->SetBinContent(3,0.02494205);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->SetBinError(3,0.0002130903);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->SetEntries(1);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->SetLineStyle(7);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->SetLineWidth(2);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->SetMarkerStyle(20);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_6_mini_beauty_balancing_MONASH__252->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253 = new TH1D("hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253","hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->SetBinContent(3,0.02427931);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->SetBinError(3,0.0002278309);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->SetEntries(1);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->SetLineStyle(8);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->SetLineWidth(2);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->SetMarkerStyle(20);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_7_mini_beauty_balancing_MONASH__253->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254 = new TH1D("hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254","hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->SetBinContent(3,0.02427931);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->SetBinError(3,0.0002278309);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->SetEntries(1);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->SetLineStyle(9);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->SetLineWidth(2);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->SetMarkerStyle(20);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_8_mini_beauty_balancing_MONASH__254->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255 = new TH1D("hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255","hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->SetBinContent(3,0.02427931);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->SetBinError(3,0.0002278309);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->SetEntries(1);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->SetLineStyle(10);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->SetLineWidth(2);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->SetMarkerStyle(20);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_9_mini_beauty_balancing_MONASH__255->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256 = new TH1D("hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256","hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->SetBinContent(3,0.02315115);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->SetBinError(3,0.00084365);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->SetEntries(1);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->SetLineWidth(2);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->SetMarkerStyle(20);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_10_mini_beauty_balancing_MONASH__256->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257 = new TH1D("hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257","hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->SetBinContent(4,0.1167316);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->SetBinError(4,0.0006470829);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->SetEntries(1);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->SetLineWidth(2);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->SetMarkerStyle(20);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_0_mini_beauty_balancing_MONASH__257->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258 = new TH1D("hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258","hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->SetBinContent(4,0.1133695);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->SetBinError(4,0.0002569718);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->SetEntries(1);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->SetLineStyle(2);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->SetLineWidth(2);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->SetMarkerStyle(20);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_1_mini_beauty_balancing_MONASH__258->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259 = new TH1D("hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259","hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->SetBinContent(4,0.1121364);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->SetBinError(4,0.0003449865);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->SetEntries(1);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->SetLineStyle(3);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->SetLineWidth(2);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->SetMarkerStyle(20);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_2_mini_beauty_balancing_MONASH__259->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260 = new TH1D("hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260","hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->SetBinContent(4,0.1115793);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->SetBinError(4,0.0003841999);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->SetEntries(1);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->SetLineStyle(4);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->SetLineWidth(2);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->SetMarkerStyle(20);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_3_mini_beauty_balancing_MONASH__260->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261 = new TH1D("hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261","hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->SetBinContent(4,0.1109765);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->SetBinError(4,0.0009608394);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->SetEntries(1);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->SetLineStyle(5);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->SetLineWidth(2);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->SetMarkerStyle(20);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_4_mini_beauty_balancing_MONASH__261->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262 = new TH1D("hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262","hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->SetBinContent(4,0.1109154);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->SetBinError(4,0.0006114275);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->SetEntries(1);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->SetLineStyle(6);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->SetLineWidth(2);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->SetMarkerStyle(20);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_5_mini_beauty_balancing_MONASH__262->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263 = new TH1D("hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263","hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->SetBinContent(4,0.1109154);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->SetBinError(4,0.0006114275);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->SetEntries(1);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->SetLineStyle(7);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->SetLineWidth(2);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->SetMarkerStyle(20);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_6_mini_beauty_balancing_MONASH__263->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264 = new TH1D("hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264","hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->SetBinContent(4,0.1101383);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->SetBinError(4,0.0006172897);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->SetEntries(1);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->SetLineStyle(8);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->SetLineWidth(2);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->SetMarkerStyle(20);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_7_mini_beauty_balancing_MONASH__264->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265 = new TH1D("hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265","hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->SetBinContent(4,0.1101383);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->SetBinError(4,0.0006172897);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->SetEntries(1);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->SetLineStyle(9);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->SetLineWidth(2);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->SetMarkerStyle(20);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_8_mini_beauty_balancing_MONASH__265->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266 = new TH1D("hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266","hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->SetBinContent(4,0.1101383);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->SetBinError(4,0.0006172897);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->SetEntries(1);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->SetLineStyle(10);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->SetLineWidth(2);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->SetMarkerStyle(20);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_9_mini_beauty_balancing_MONASH__266->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267 = new TH1D("hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267","hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->SetBinContent(4,0.1062357);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->SetBinError(4,0.002373641);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->SetEntries(1);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->SetLineWidth(2);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->SetMarkerStyle(20);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_10_mini_beauty_balancing_MONASH__267->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268 = new TH1D("hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268","hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->SetBinContent(5,0.01989677);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->SetBinError(5,0.0005003761);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->SetEntries(1);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->SetLineWidth(2);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->SetMarkerStyle(20);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_0_mini_beauty_balancing_MONASH__268->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269 = new TH1D("hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269","hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->SetBinContent(5,0.01922559);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->SetBinError(5,0.0001316935);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->SetEntries(1);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->SetLineStyle(2);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->SetLineWidth(2);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->SetMarkerStyle(20);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_1_mini_beauty_balancing_MONASH__269->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270 = new TH1D("hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270","hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->SetBinContent(5,0.01876559);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->SetBinError(5,0.0001750556);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->SetEntries(1);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->SetLineStyle(3);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->SetLineWidth(2);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->SetMarkerStyle(20);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_2_mini_beauty_balancing_MONASH__270->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271 = new TH1D("hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271","hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->SetBinContent(5,0.01866807);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->SetBinError(5,0.0001899072);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->SetEntries(1);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->SetLineStyle(4);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->SetLineWidth(2);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->SetMarkerStyle(20);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_3_mini_beauty_balancing_MONASH__271->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272 = new TH1D("hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272","hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->SetBinContent(5,0.01862602);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->SetBinError(5,0.0001710089);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->SetEntries(1);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->SetLineStyle(5);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->SetLineWidth(2);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->SetMarkerStyle(20);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_4_mini_beauty_balancing_MONASH__272->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273 = new TH1D("hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273","hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->SetBinContent(5,0.01911179);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->SetBinError(5,0.0003595918);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->SetEntries(1);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->SetLineStyle(6);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->SetLineWidth(2);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->SetMarkerStyle(20);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_5_mini_beauty_balancing_MONASH__273->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274 = new TH1D("hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274","hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->SetBinContent(5,0.01911179);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->SetBinError(5,0.0003595918);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->SetEntries(1);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->SetLineStyle(7);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->SetLineWidth(2);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->SetMarkerStyle(20);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_6_mini_beauty_balancing_MONASH__274->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275 = new TH1D("hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275","hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->SetBinContent(5,0.01848332);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->SetBinError(5,0.0004719797);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->SetEntries(1);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->SetLineStyle(8);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->SetLineWidth(2);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->SetMarkerStyle(20);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_7_mini_beauty_balancing_MONASH__275->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276 = new TH1D("hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276","hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->SetBinContent(5,0.01848332);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->SetBinError(5,0.0004719797);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->SetEntries(1);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->SetLineStyle(9);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->SetLineWidth(2);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->SetMarkerStyle(20);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_8_mini_beauty_balancing_MONASH__276->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277 = new TH1D("hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277","hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->SetBinContent(5,0.01848332);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->SetBinError(5,0.0004719797);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->SetEntries(1);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->SetLineStyle(10);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->SetLineWidth(2);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->SetMarkerStyle(20);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_9_mini_beauty_balancing_MONASH__277->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278 = new TH1D("hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278","hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH",5,0,5);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->SetBinContent(5,0.01834783);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->SetBinError(5,0.0008111813);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->SetEntries(1);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->SetLineWidth(2);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->SetMarkerStyle(20);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_10_mini_beauty_balancing_MONASH__278->Draw("same PE");
   
   leg = new TLegend(0.63,0.68,0.9,0.88,NULL,"brNDC");
   leg->SetBorderSize(1);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("hYields_BEAUTY_0_0_0_mini_beauty_balancing_MONASH","0-1%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_0_0_1_mini_beauty_balancing_MONASH","1-10%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(2);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_0_0_2_mini_beauty_balancing_MONASH","10-20%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(3);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_0_0_3_mini_beauty_balancing_MONASH","20-30%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(4);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_0_0_4_mini_beauty_balancing_MONASH","30-40%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(5);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_0_0_5_mini_beauty_balancing_MONASH","40-50%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(6);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_0_0_6_mini_beauty_balancing_MONASH","50-60%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(7);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_0_0_7_mini_beauty_balancing_MONASH","60-70%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(8);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_0_0_8_mini_beauty_balancing_MONASH","70-80%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(9);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_0_0_9_mini_beauty_balancing_MONASH","80-90%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(10);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_BEAUTY_0_0_10_mini_beauty_balancing_MONASH","90-100%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   cMiniPad_BEAUTY_mini_beauty_balancing_MONASH__46->Modified();
   global_balancing_plots->cd();
  
// ------------>Primitives in pad: cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH
   TPad *cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47 = new TPad("cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH", "cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH",0.05,0.19,0.5,0.379);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->Draw();
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->cd();
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->Range(-0.2634352,-1.004008,5.005269,3.004008);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetFillColor(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetBorderMode(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetBorderSize(2);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetLogy();
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetTickx(1);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetTicky(1);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetLeftMargin(0.05);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetRightMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetTopMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetBottomMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetFrameBorderMode(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->SetFrameBorderMode(0);
   
   TH1D *hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279 = new TH1D("hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279","",5,0,5);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->SetMinimum(0.1);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->SetMaximum(1000);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->SetLineColor(ci);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetXaxis()->SetBinLabel(1,"B-");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetXaxis()->SetBinLabel(2,"Bc-");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetXaxis()->SetBinLabel(3,"B_s^0-bar");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetXaxis()->SetBinLabel(4,"B^{0}-bar");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetXaxis()->SetBinLabel(5,"Lambda_b");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetXaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetXaxis()->SetTitleOffset(1);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetXaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetYaxis()->SetTitle("CP/MON");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetYaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetYaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetZaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetZaxis()->SetTitleOffset(1);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->GetZaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__279->Draw("PE");
   
   TH1D *hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280 = new TH1D("hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280","hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->SetBinContent(1,0.6563439);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->SetBinError(1,0.008722741);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->SetLineColor(ci);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->SetMarkerColor(ci);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->SetMarkerStyle(22);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__280->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281 = new TH1D("hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281","hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->SetBinContent(1,0.6767537);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->SetBinError(1,0.002960514);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->SetLineColor(ci);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->SetLineStyle(2);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->SetMarkerColor(ci);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->SetMarkerStyle(22);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__281->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282 = new TH1D("hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282","hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->SetBinContent(1,0.7315516);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->SetBinError(1,0.004880529);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->SetLineColor(ci);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->SetLineStyle(3);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->SetMarkerColor(ci);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->SetMarkerStyle(22);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__282->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283 = new TH1D("hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283","hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->SetBinContent(1,0.7702083);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->SetBinError(1,0.004921023);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->SetLineColor(ci);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->SetLineStyle(4);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->SetMarkerColor(ci);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->SetMarkerStyle(22);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__283->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284 = new TH1D("hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284","hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->SetBinContent(1,0.8288053);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->SetBinError(1,0.005444217);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->SetLineColor(ci);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->SetLineStyle(5);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->SetMarkerColor(ci);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->SetMarkerStyle(22);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__284->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285 = new TH1D("hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285","hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->SetBinContent(1,0.8575992);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->SetBinError(1,0.007602093);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->SetLineColor(ci);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->SetLineStyle(6);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->SetMarkerColor(ci);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->SetMarkerStyle(22);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__285->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286 = new TH1D("hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286","hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->SetBinContent(1,0.885115);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->SetBinError(1,0.009076955);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->SetLineColor(ci);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->SetLineStyle(7);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->SetMarkerColor(ci);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->SetMarkerStyle(22);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__286->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287 = new TH1D("hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287","hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->SetBinContent(1,0.9376555);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->SetBinError(1,0.01064648);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->SetLineColor(ci);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->SetLineStyle(8);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->SetMarkerColor(ci);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->SetMarkerStyle(22);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__287->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288 = new TH1D("hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288","hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->SetBinContent(1,0.9376555);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->SetBinError(1,0.01064648);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->SetLineColor(ci);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->SetLineStyle(9);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->SetMarkerColor(ci);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->SetMarkerStyle(22);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__288->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289 = new TH1D("hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289","hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->SetBinContent(1,0.9376555);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->SetBinError(1,0.01064648);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->SetLineColor(ci);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->SetLineStyle(10);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->SetMarkerColor(ci);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->SetMarkerStyle(22);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__289->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290 = new TH1D("hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290","hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->SetBinContent(1,0.9911197);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->SetBinError(1,0.03046079);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->SetLineColor(ci);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->SetMarkerColor(ci);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->SetMarkerStyle(22);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__290->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291 = new TH1D("hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291","hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->SetBinContent(2,0.8127824);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->SetBinError(2,0.1364941);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->SetLineColor(ci);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->SetMarkerStyle(22);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__291->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292 = new TH1D("hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292","hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->SetBinContent(2,0.6122457);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->SetBinError(2,0.05910327);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->SetLineColor(ci);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->SetLineStyle(2);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->SetMarkerStyle(22);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__292->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293 = new TH1D("hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293","hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->SetBinContent(2,0.5806352);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->SetBinError(2,0.08571059);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->SetLineColor(ci);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->SetLineStyle(3);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->SetMarkerStyle(22);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__293->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294 = new TH1D("hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294","hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->SetBinContent(2,0.4325925);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->SetBinError(2,0.0982793);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->SetLineColor(ci);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->SetLineStyle(4);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->SetMarkerStyle(22);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__294->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295 = new TH1D("hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295","hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->SetBinContent(2,0.2996967);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->SetBinError(2,0.1105784);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->SetLineColor(ci);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->SetLineStyle(5);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->SetMarkerStyle(22);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__295->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296 = new TH1D("hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296","hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->SetBinContent(2,0.6337187);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->SetBinError(2,0.1775115);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->SetLineColor(ci);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->SetLineStyle(6);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->SetMarkerColor(ci);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->SetMarkerStyle(22);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__296->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297 = new TH1D("hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297","hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->SetBinContent(2,0.6415662);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->SetBinError(2,0.2295397);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->SetLineColor(ci);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->SetLineStyle(7);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->SetMarkerColor(ci);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->SetMarkerStyle(22);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__297->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298 = new TH1D("hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298","hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->SetBinContent(2,0.6900665);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->SetBinError(2,0.3126167);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->SetLineColor(ci);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->SetLineStyle(8);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->SetMarkerColor(ci);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->SetMarkerStyle(22);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__298->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299 = new TH1D("hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299","hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->SetBinContent(2,0.6900665);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->SetBinError(2,0.3126167);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->SetLineColor(ci);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->SetLineStyle(9);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->SetMarkerColor(ci);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->SetMarkerStyle(22);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__299->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300 = new TH1D("hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300","hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->SetBinContent(2,0.6900665);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->SetBinError(2,0.3126167);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->SetLineColor(ci);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->SetLineStyle(10);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->SetMarkerColor(ci);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->SetMarkerStyle(22);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__300->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301 = new TH1D("hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301","hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->SetBinContent(2,0.6448183);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->SetBinError(2,0.5396789);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->SetLineColor(ci);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->SetMarkerColor(ci);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->SetMarkerStyle(22);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__301->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302 = new TH1D("hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302","hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->SetBinContent(3,0.6525622);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->SetBinError(3,0.01383608);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->SetLineColor(ci);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->SetMarkerStyle(22);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__302->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303 = new TH1D("hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303","hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->SetBinContent(3,0.698702);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->SetBinError(3,0.007030582);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->SetLineColor(ci);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->SetLineStyle(2);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->SetMarkerStyle(22);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__303->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304 = new TH1D("hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304","hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->SetBinContent(3,0.7333845);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->SetBinError(3,0.01082445);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->SetLineColor(ci);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->SetLineStyle(3);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->SetMarkerStyle(22);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__304->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305 = new TH1D("hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305","hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->SetBinContent(3,0.7674986);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->SetBinError(3,0.01455219);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->SetLineColor(ci);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->SetLineStyle(4);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->SetMarkerStyle(22);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__305->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306 = new TH1D("hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306","hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->SetBinContent(3,0.7722954);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->SetBinError(3,0.01281361);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->SetLineColor(ci);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->SetLineStyle(5);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->SetMarkerStyle(22);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__306->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307 = new TH1D("hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307","hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->SetBinContent(3,0.8431438);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->SetBinError(3,0.01400846);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->SetLineColor(ci);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->SetLineStyle(6);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->SetMarkerColor(ci);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->SetMarkerStyle(22);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__307->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308 = new TH1D("hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308","hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->SetBinContent(3,0.9053922);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->SetBinError(3,0.02353809);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->SetLineColor(ci);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->SetLineStyle(7);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->SetMarkerColor(ci);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->SetMarkerStyle(22);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__308->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309 = new TH1D("hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309","hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->SetBinContent(3,0.9411578);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->SetBinError(3,0.01992085);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->SetLineColor(ci);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->SetLineStyle(8);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->SetMarkerColor(ci);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->SetMarkerStyle(22);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__309->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310 = new TH1D("hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310","hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->SetBinContent(3,0.9411578);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->SetBinError(3,0.01992085);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->SetLineColor(ci);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->SetLineStyle(9);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->SetMarkerColor(ci);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->SetMarkerStyle(22);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__310->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311 = new TH1D("hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311","hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->SetBinContent(3,0.9411578);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->SetBinError(3,0.01992085);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->SetLineColor(ci);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->SetLineStyle(10);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->SetMarkerColor(ci);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->SetMarkerStyle(22);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__311->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312 = new TH1D("hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312","hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->SetBinContent(3,1.054007);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->SetBinError(3,0.0444685);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->SetLineColor(ci);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->SetMarkerColor(ci);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->SetMarkerStyle(22);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__312->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313 = new TH1D("hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313","hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->SetBinContent(4,0.6725716);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->SetBinError(4,0.005450457);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->SetLineColor(ci);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->SetMarkerColor(ci);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->SetMarkerStyle(22);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__313->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314 = new TH1D("hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314","hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->SetBinContent(4,0.6680514);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->SetBinError(4,0.002396815);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->SetLineColor(ci);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->SetLineStyle(2);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->SetMarkerColor(ci);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->SetMarkerStyle(22);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__314->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315 = new TH1D("hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315","hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->SetBinContent(4,0.7220639);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->SetBinError(4,0.003706659);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->SetLineColor(ci);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->SetLineStyle(3);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->SetMarkerColor(ci);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->SetMarkerStyle(22);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__315->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316 = new TH1D("hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316","hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->SetBinContent(4,0.7612845);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->SetBinError(4,0.005162404);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->SetLineColor(ci);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->SetLineStyle(4);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->SetMarkerColor(ci);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->SetMarkerStyle(22);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__316->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317 = new TH1D("hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317","hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->SetBinContent(4,0.8152113);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->SetBinError(4,0.01009001);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->SetLineColor(ci);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->SetLineStyle(5);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->SetMarkerColor(ci);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->SetMarkerStyle(22);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__317->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318 = new TH1D("hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318","hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->SetBinContent(4,0.8469347);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->SetBinError(4,0.005569917);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->SetLineColor(ci);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->SetLineStyle(6);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->SetMarkerColor(ci);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->SetMarkerStyle(22);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__318->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319 = new TH1D("hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319","hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->SetBinContent(4,0.8789835);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->SetBinError(4,0.008861862);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->SetLineColor(ci);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->SetLineStyle(7);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->SetMarkerColor(ci);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->SetMarkerStyle(22);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__319->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320 = new TH1D("hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320","hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->SetBinContent(4,0.9178422);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->SetBinError(4,0.01247369);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->SetLineColor(ci);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->SetLineStyle(8);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->SetMarkerColor(ci);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->SetMarkerStyle(22);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__320->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321 = new TH1D("hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321","hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->SetBinContent(4,0.9178422);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->SetBinError(4,0.01247369);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->SetLineColor(ci);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->SetLineStyle(9);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->SetMarkerColor(ci);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->SetMarkerStyle(22);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__321->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322 = new TH1D("hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322","hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->SetBinContent(4,0.9178422);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->SetBinError(4,0.01247369);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->SetLineColor(ci);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->SetLineStyle(10);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->SetMarkerColor(ci);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->SetMarkerStyle(22);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__322->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323 = new TH1D("hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323","hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->SetBinContent(4,0.9546201);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->SetBinError(4,0.02732915);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->SetLineColor(ci);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->SetMarkerColor(ci);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->SetMarkerStyle(22);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__323->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324 = new TH1D("hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324","hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->SetBinContent(5,2.082778);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->SetBinError(5,0.05353597);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->SetLineColor(ci);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->SetMarkerColor(ci);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->SetMarkerStyle(22);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_CLOSEPACKING_over_MONASH__324->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325 = new TH1D("hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325","hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->SetBinContent(5,1.953883);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->SetBinError(5,0.0181506);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->SetLineColor(ci);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->SetLineStyle(2);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->SetMarkerColor(ci);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->SetMarkerStyle(22);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_CLOSEPACKING_over_MONASH__325->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326 = new TH1D("hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326","hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->SetBinContent(5,1.694493);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->SetBinError(5,0.02622735);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->SetLineColor(ci);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->SetLineStyle(3);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->SetMarkerColor(ci);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->SetMarkerStyle(22);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_CLOSEPACKING_over_MONASH__326->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327 = new TH1D("hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327","hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->SetBinContent(5,1.569618);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->SetBinError(5,0.01957983);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->SetLineColor(ci);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->SetLineStyle(4);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->SetMarkerColor(ci);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->SetMarkerStyle(22);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_CLOSEPACKING_over_MONASH__327->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328 = new TH1D("hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328","hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->SetBinContent(5,1.36351);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->SetBinError(5,0.02059108);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->SetLineColor(ci);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->SetLineStyle(5);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->SetMarkerColor(ci);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->SetMarkerStyle(22);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_CLOSEPACKING_over_MONASH__328->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329 = new TH1D("hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329","hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->SetBinContent(5,1.25236);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->SetBinError(5,0.02819517);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->SetLineColor(ci);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->SetLineStyle(6);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->SetMarkerColor(ci);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->SetMarkerStyle(22);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_CLOSEPACKING_over_MONASH__329->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330 = new TH1D("hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330","hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->SetBinContent(5,1.173974);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->SetBinError(5,0.03099074);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->SetLineColor(ci);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->SetLineStyle(7);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->SetMarkerColor(ci);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->SetMarkerStyle(22);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_CLOSEPACKING_over_MONASH__330->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331 = new TH1D("hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331","hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->SetBinContent(5,1.106018);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->SetBinError(5,0.03169083);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->SetLineColor(ci);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->SetLineStyle(8);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->SetMarkerColor(ci);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->SetMarkerStyle(22);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_CLOSEPACKING_over_MONASH__331->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332 = new TH1D("hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332","hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->SetBinContent(5,1.106018);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->SetBinError(5,0.03169083);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->SetLineColor(ci);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->SetLineStyle(9);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->SetMarkerColor(ci);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->SetMarkerStyle(22);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_CLOSEPACKING_over_MONASH__332->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333 = new TH1D("hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333","hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->SetBinContent(5,1.106018);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->SetBinError(5,0.03169083);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->SetLineColor(ci);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->SetLineStyle(10);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->SetMarkerColor(ci);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->SetMarkerStyle(22);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_CLOSEPACKING_over_MONASH__333->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334 = new TH1D("hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334","hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH",5,0,5);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->SetBinContent(5,1.072163);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->SetBinError(5,0.05438402);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->SetLineColor(ci);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->SetMarkerColor(ci);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->SetMarkerStyle(22);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_CLOSEPACKING_over_MONASH__334->Draw("same PE");
   cMiniPad_BEAUTY_mini_beauty_balancing_CLOSEPACKING_over_MONASH__47->Modified();
   global_balancing_plots->cd();
  
// ------------>Primitives in pad: cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH
   TPad *cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48 = new TPad("cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH", "cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH",0.05,0,0.5,0.189);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->Draw();
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->cd();
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->Range(-0.2634352,-2.001252,5.005269,3.005006);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetFillColor(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetBorderMode(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetBorderSize(2);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetLogy();
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetTickx(1);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetTicky(1);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetLeftMargin(0.05);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetRightMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetTopMargin(0.001);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetBottomMargin(0.2);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetFrameBorderMode(0);
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->SetFrameBorderMode(0);
   
   TH1D *hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335 = new TH1D("hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335","",5,0,5);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->SetMinimum(0.1);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->SetMaximum(1000);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->SetLineColor(ci);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetXaxis()->SetBinLabel(1,"B-");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetXaxis()->SetBinLabel(2,"Bc-");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetXaxis()->SetBinLabel(3,"B_s^0-bar");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetXaxis()->SetBinLabel(4,"B^{0}-bar");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetXaxis()->SetBinLabel(5,"Lambda_b");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetXaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetXaxis()->SetTitleOffset(1);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetXaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetYaxis()->SetTitle("JUN/MON");
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetYaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetYaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetZaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetZaxis()->SetTitleOffset(1);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->GetZaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__335->Draw("PE");
   
   TH1D *hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336 = new TH1D("hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336","hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->SetBinContent(1,0.677913);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->SetBinError(1,0.008899503);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->SetLineColor(ci);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->SetMarkerColor(ci);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->SetMarkerStyle(21);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__336->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337 = new TH1D("hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337","hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->SetBinContent(1,0.6865664);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->SetBinError(1,0.003375592);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->SetLineColor(ci);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->SetLineStyle(2);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->SetMarkerColor(ci);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->SetMarkerStyle(21);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__337->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338 = new TH1D("hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338","hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->SetBinContent(1,0.7414521);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->SetBinError(1,0.004010504);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->SetLineColor(ci);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->SetLineStyle(3);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->SetMarkerColor(ci);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->SetMarkerStyle(21);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__338->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339 = new TH1D("hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339","hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->SetBinContent(1,0.8006462);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->SetBinError(1,0.004232098);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->SetLineColor(ci);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->SetLineStyle(4);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->SetMarkerColor(ci);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->SetMarkerStyle(21);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__339->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340 = new TH1D("hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340","hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->SetBinContent(1,0.8243756);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->SetBinError(1,0.003903791);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->SetLineColor(ci);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->SetLineStyle(5);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->SetMarkerColor(ci);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->SetMarkerStyle(21);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__340->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341 = new TH1D("hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341","hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->SetBinContent(1,0.8669953);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->SetBinError(1,0.007337116);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->SetLineColor(ci);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->SetLineStyle(6);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->SetMarkerColor(ci);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->SetMarkerStyle(21);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__341->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342 = new TH1D("hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342","hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->SetBinContent(1,0.892877);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->SetBinError(1,0.009439948);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->SetLineColor(ci);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->SetLineStyle(7);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->SetMarkerColor(ci);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->SetMarkerStyle(21);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__342->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343 = new TH1D("hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343","hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->SetBinContent(1,0.9170348);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->SetBinError(1,0.01014922);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->SetLineColor(ci);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->SetLineStyle(8);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->SetMarkerColor(ci);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->SetMarkerStyle(21);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__343->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344 = new TH1D("hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344","hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->SetBinContent(1,0.9266865);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->SetBinError(1,0.01035077);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->SetLineColor(ci);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->SetLineStyle(9);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->SetMarkerColor(ci);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->SetMarkerStyle(21);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__344->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345 = new TH1D("hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345","hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->SetBinContent(1,0.9266865);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->SetBinError(1,0.01035077);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->SetLineColor(ci);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->SetLineStyle(10);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->SetMarkerColor(ci);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->SetMarkerStyle(21);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__345->Draw("same PE");
   
   TH1D *hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346 = new TH1D("hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346","hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->SetBinContent(1,0.9709629);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->SetBinError(1,0.02715205);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->SetLineColor(ci);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->SetMarkerColor(ci);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->SetMarkerStyle(21);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_0_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__346->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347 = new TH1D("hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347","hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->SetBinContent(2,1.161469);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->SetBinError(2,0.2356282);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->SetLineColor(ci);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->SetMarkerColor(ci);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->SetMarkerStyle(21);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__347->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348 = new TH1D("hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348","hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->SetBinContent(2,0.7116472);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->SetBinError(2,0.05366496);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->SetLineColor(ci);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->SetLineStyle(2);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->SetMarkerColor(ci);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->SetMarkerStyle(21);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__348->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349 = new TH1D("hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349","hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->SetBinContent(2,0.5715769);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->SetBinError(2,0.07574452);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->SetLineColor(ci);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->SetLineStyle(3);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->SetMarkerColor(ci);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->SetMarkerStyle(21);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__349->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350 = new TH1D("hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350","hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->SetBinContent(2,0.4212473);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->SetBinError(2,0.09073931);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->SetLineColor(ci);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->SetLineStyle(4);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->SetMarkerColor(ci);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->SetMarkerStyle(21);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__350->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351 = new TH1D("hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351","hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->SetBinContent(2,0.330946);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->SetBinError(2,0.09297224);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->SetLineColor(ci);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->SetLineStyle(5);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->SetMarkerColor(ci);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->SetMarkerStyle(21);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__351->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352 = new TH1D("hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352","hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->SetBinContent(2,0.8280802);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->SetBinError(2,0.23354);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->SetLineColor(ci);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->SetLineStyle(6);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->SetMarkerColor(ci);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->SetMarkerStyle(21);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__352->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353 = new TH1D("hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353","hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->SetBinContent(2,0.9804617);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->SetBinError(2,0.3735704);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->SetLineColor(ci);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->SetLineStyle(7);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->SetMarkerColor(ci);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->SetMarkerStyle(21);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__353->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354 = new TH1D("hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354","hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->SetBinContent(2,1.248825);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->SetBinError(2,0.4763613);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->SetLineColor(ci);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->SetLineStyle(8);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->SetMarkerColor(ci);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->SetMarkerStyle(21);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__354->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355 = new TH1D("hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355","hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->SetBinContent(2,1.340375);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->SetBinError(2,0.5010447);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->SetLineColor(ci);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->SetLineStyle(9);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->SetMarkerColor(ci);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->SetMarkerStyle(21);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__355->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356 = new TH1D("hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356","hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->SetBinContent(2,1.340375);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->SetBinError(2,0.5010447);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->SetLineColor(ci);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->SetLineStyle(10);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->SetMarkerColor(ci);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->SetMarkerStyle(21);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__356->Draw("same PE");
   
   TH1D *hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357 = new TH1D("hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357","hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->SetLineColor(ci);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->SetMarkerColor(ci);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->SetMarkerStyle(21);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_1_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__357->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358 = new TH1D("hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358","hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->SetBinContent(3,0.6098537);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->SetBinError(3,0.01328998);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->SetLineColor(ci);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->SetMarkerColor(ci);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->SetMarkerStyle(21);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__358->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359 = new TH1D("hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359","hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->SetBinContent(3,0.5990746);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->SetBinError(3,0.005871761);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->SetLineColor(ci);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->SetLineStyle(2);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->SetMarkerColor(ci);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->SetMarkerStyle(21);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__359->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360 = new TH1D("hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360","hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->SetBinContent(3,0.6461399);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->SetBinError(3,0.009193758);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->SetLineColor(ci);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->SetLineStyle(3);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->SetMarkerColor(ci);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->SetMarkerStyle(21);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__360->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361 = new TH1D("hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361","hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->SetBinContent(3,0.6698111);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->SetBinError(3,0.01273156);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->SetLineColor(ci);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->SetLineStyle(4);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->SetMarkerColor(ci);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->SetMarkerStyle(21);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__361->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362 = new TH1D("hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362","hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->SetBinContent(3,0.7125703);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->SetBinError(3,0.01272537);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->SetLineColor(ci);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->SetLineStyle(5);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->SetMarkerColor(ci);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->SetMarkerStyle(21);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__362->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363 = new TH1D("hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363","hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->SetBinContent(3,0.7757422);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->SetBinError(3,0.01390812);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->SetLineColor(ci);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->SetLineStyle(6);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->SetMarkerColor(ci);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->SetMarkerStyle(21);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__363->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364 = new TH1D("hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364","hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->SetBinContent(3,0.7987491);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->SetBinError(3,0.01502849);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->SetLineColor(ci);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->SetLineStyle(7);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->SetMarkerColor(ci);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->SetMarkerStyle(21);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__364->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365 = new TH1D("hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365","hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->SetBinContent(3,0.8641403);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->SetBinError(3,0.01679267);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->SetLineColor(ci);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->SetLineStyle(8);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->SetMarkerColor(ci);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->SetMarkerStyle(21);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__365->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366 = new TH1D("hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366","hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->SetBinContent(3,0.9219167);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->SetBinError(3,0.03524554);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->SetLineColor(ci);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->SetLineStyle(9);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->SetMarkerColor(ci);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->SetMarkerStyle(21);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__366->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367 = new TH1D("hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367","hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->SetBinContent(3,0.9219167);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->SetBinError(3,0.03524554);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->SetLineColor(ci);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->SetLineStyle(10);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->SetMarkerColor(ci);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->SetMarkerStyle(21);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__367->Draw("same PE");
   
   TH1D *hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368 = new TH1D("hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368","hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->SetBinContent(3,0.918046);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->SetBinError(3,0.04773465);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->SetLineColor(ci);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->SetMarkerColor(ci);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->SetMarkerStyle(21);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_2_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__368->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369 = new TH1D("hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369","hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->SetBinContent(4,0.6658772);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->SetBinError(4,0.006299597);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->SetLineColor(ci);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->SetMarkerColor(ci);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->SetMarkerStyle(21);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__369->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370 = new TH1D("hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370","hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->SetBinContent(4,0.68364);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->SetBinError(4,0.002372302);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->SetLineColor(ci);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->SetLineStyle(2);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->SetMarkerColor(ci);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->SetMarkerStyle(21);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__370->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371 = new TH1D("hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371","hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->SetBinContent(4,0.7395501);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->SetBinError(4,0.003487852);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->SetLineColor(ci);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->SetLineStyle(3);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->SetMarkerColor(ci);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->SetMarkerStyle(21);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__371->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372 = new TH1D("hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372","hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->SetBinContent(4,0.7836443);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->SetBinError(4,0.006853427);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->SetLineColor(ci);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->SetLineStyle(4);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->SetMarkerColor(ci);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->SetMarkerStyle(21);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__372->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373 = new TH1D("hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373","hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->SetBinContent(4,0.8237522);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->SetBinError(4,0.00795521);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->SetLineColor(ci);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->SetLineStyle(5);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->SetMarkerColor(ci);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->SetMarkerStyle(21);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__373->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374 = new TH1D("hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374","hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->SetBinContent(4,0.8697878);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->SetBinError(4,0.007222149);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->SetLineColor(ci);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->SetLineStyle(6);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->SetMarkerColor(ci);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->SetMarkerStyle(21);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__374->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375 = new TH1D("hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375","hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->SetBinContent(4,0.8938646);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->SetBinError(4,0.008861182);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->SetLineColor(ci);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->SetLineStyle(7);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->SetMarkerColor(ci);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->SetMarkerStyle(21);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__375->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376 = new TH1D("hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376","hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->SetBinContent(4,0.9182969);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->SetBinError(4,0.00757934);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->SetLineColor(ci);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->SetLineStyle(8);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->SetMarkerColor(ci);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->SetMarkerStyle(21);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__376->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377 = new TH1D("hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377","hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->SetBinContent(4,0.942322);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->SetBinError(4,0.007815522);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->SetLineColor(ci);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->SetLineStyle(9);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->SetMarkerColor(ci);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->SetMarkerStyle(21);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__377->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378 = new TH1D("hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378","hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->SetBinContent(4,0.942322);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->SetBinError(4,0.007815522);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->SetLineColor(ci);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->SetLineStyle(10);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->SetMarkerColor(ci);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->SetMarkerStyle(21);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__378->Draw("same PE");
   
   TH1D *hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379 = new TH1D("hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379","hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->SetBinContent(4,0.9763265);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->SetBinError(4,0.03141469);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->SetLineColor(ci);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->SetMarkerColor(ci);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->SetMarkerStyle(21);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_3_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__379->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380 = new TH1D("hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380","hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->SetBinContent(5,2.242503);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->SetBinError(5,0.0690756);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->SetLineColor(ci);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->SetMarkerColor(ci);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->SetMarkerStyle(21);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_0_mini_beauty_balancing_JUNCTIONS_over_MONASH__380->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381 = new TH1D("hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381","hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->SetBinContent(5,2.119919);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->SetBinError(5,0.02003766);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->SetLineColor(ci);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->SetLineStyle(2);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->SetMarkerColor(ci);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->SetMarkerStyle(21);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_1_mini_beauty_balancing_JUNCTIONS_over_MONASH__381->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382 = new TH1D("hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382","hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->SetBinContent(5,1.875203);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->SetBinError(5,0.02022099);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->SetLineColor(ci);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->SetLineStyle(3);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->SetMarkerColor(ci);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->SetMarkerStyle(21);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_2_mini_beauty_balancing_JUNCTIONS_over_MONASH__382->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383 = new TH1D("hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383","hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->SetBinContent(5,1.659066);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->SetBinError(5,0.03293543);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->SetLineColor(ci);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->SetLineStyle(4);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->SetMarkerColor(ci);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->SetMarkerStyle(21);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_3_mini_beauty_balancing_JUNCTIONS_over_MONASH__383->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384 = new TH1D("hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384","hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->SetBinContent(5,1.546897);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->SetBinError(5,0.02444849);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->SetLineColor(ci);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->SetLineStyle(5);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->SetMarkerColor(ci);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->SetMarkerStyle(21);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_4_mini_beauty_balancing_JUNCTIONS_over_MONASH__384->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385 = new TH1D("hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385","hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->SetBinContent(5,1.375598);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->SetBinError(5,0.02950106);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->SetLineColor(ci);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->SetLineStyle(6);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->SetMarkerColor(ci);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->SetMarkerStyle(21);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_5_mini_beauty_balancing_JUNCTIONS_over_MONASH__385->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386 = new TH1D("hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386","hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->SetBinContent(5,1.279839);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->SetBinError(5,0.03563053);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->SetLineColor(ci);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->SetLineStyle(7);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->SetMarkerColor(ci);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->SetMarkerStyle(21);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_6_mini_beauty_balancing_JUNCTIONS_over_MONASH__386->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387 = new TH1D("hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387","hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->SetBinContent(5,1.247844);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->SetBinError(5,0.03664251);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->SetLineColor(ci);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->SetLineStyle(8);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->SetMarkerColor(ci);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->SetMarkerStyle(21);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_7_mini_beauty_balancing_JUNCTIONS_over_MONASH__387->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388 = new TH1D("hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388","hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->SetBinContent(5,1.147753);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->SetBinError(5,0.04271013);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->SetLineColor(ci);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->SetLineStyle(9);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->SetMarkerColor(ci);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->SetMarkerStyle(21);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_8_mini_beauty_balancing_JUNCTIONS_over_MONASH__388->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389 = new TH1D("hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389","hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->SetBinContent(5,1.147753);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->SetBinError(5,0.04271013);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->SetLineColor(ci);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->SetLineStyle(10);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->SetMarkerColor(ci);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->SetMarkerStyle(21);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_9_mini_beauty_balancing_JUNCTIONS_over_MONASH__389->Draw("same PE");
   
   TH1D *hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390 = new TH1D("hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390","hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH",5,0,5);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->SetBinContent(5,1.138938);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->SetBinError(5,0.07983965);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->SetLineColor(ci);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->SetMarkerColor(ci);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->SetMarkerStyle(21);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->GetXaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->GetXaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->GetXaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->GetYaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->GetYaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->GetZaxis()->SetLabelFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->GetZaxis()->SetTitleOffset(1);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->GetZaxis()->SetTitleFont(42);
   hYields_BEAUTY_4_10_mini_beauty_balancing_JUNCTIONS_over_MONASH__390->Draw("same PE");
   cMiniPad_BEAUTY_mini_beauty_balancing_JUNCTIONS_over_MONASH__48->Modified();
   global_balancing_plots->cd();
  
// ------------>Primitives in pad: cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING
   TPad *cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49 = new TPad("cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING", "cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING",0.501,0.76,0.95,0.95);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->Draw();
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->cd();
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->Range(0,-4.003911,3.157895,-0.0929991);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetFillColor(0);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetBorderMode(0);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetBorderSize(2);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetLogy();
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetTickx(1);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetTicky(1);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetLeftMargin(0);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetRightMargin(0.05);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetTopMargin(0.001);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetBottomMargin(0.001);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetFrameBorderMode(0);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->SetFrameBorderMode(0);
   
   TH1D *hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391 = new TH1D("hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391","",3,0,3);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->SetMinimum(0.0001);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->SetMaximum(0.8);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->SetLineColor(ci);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->GetXaxis()->SetLabelFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->GetXaxis()->SetTitleOffset(1);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->GetXaxis()->SetTitleFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->GetYaxis()->SetTitle("yield");
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->GetYaxis()->SetLabelFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->GetYaxis()->SetTitleFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->GetZaxis()->SetLabelFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->GetZaxis()->SetTitleOffset(1);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->GetZaxis()->SetTitleFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_CLOSEPACKING__391->Draw("PE");
   
   TH1D *hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392 = new TH1D("hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392","hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->SetBinContent(1,0.2018736);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->SetBinError(1,0.001209584);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->SetLineColor(ci);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->SetMarkerColor(ci);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->SetMarkerStyle(22);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING__392->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393 = new TH1D("hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393","hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->SetBinContent(1,0.1810672);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->SetBinError(1,0.0003625407);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->SetLineColor(ci);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->SetLineStyle(2);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->SetMarkerColor(ci);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->SetMarkerStyle(22);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING__393->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394 = new TH1D("hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394","hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->SetBinContent(1,0.1610086);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->SetBinError(1,0.0003542363);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->SetLineColor(ci);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->SetLineStyle(3);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->SetMarkerColor(ci);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->SetMarkerStyle(22);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING__394->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395 = new TH1D("hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395","hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->SetBinContent(1,0.1518786);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->SetBinError(1,0.0002778575);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->SetLineColor(ci);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->SetLineStyle(4);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->SetMarkerColor(ci);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->SetMarkerStyle(22);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING__395->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396 = new TH1D("hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396","hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->SetBinContent(1,0.1425686);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->SetBinError(1,0.0003363228);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->SetLineColor(ci);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->SetLineStyle(5);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->SetMarkerColor(ci);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->SetMarkerStyle(22);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING__396->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397 = new TH1D("hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397","hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->SetBinContent(1,0.1393238);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->SetBinError(1,0.0002514405);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->SetLineColor(ci);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->SetLineStyle(6);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->SetMarkerColor(ci);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->SetMarkerStyle(22);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING__397->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398 = new TH1D("hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398","hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->SetBinContent(1,0.1371505);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->SetBinError(1,0.0002998201);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->SetLineColor(ci);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->SetLineStyle(7);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->SetMarkerColor(ci);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->SetMarkerStyle(22);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING__398->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399 = new TH1D("hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399","hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->SetBinContent(1,0.1319467);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->SetBinError(1,0.0001882852);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->SetLineColor(ci);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->SetLineStyle(8);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->SetMarkerColor(ci);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->SetMarkerStyle(22);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING__399->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400 = new TH1D("hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400","hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->SetBinContent(1,0.1319467);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->SetBinError(1,0.0001882852);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->SetLineColor(ci);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->SetLineStyle(9);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->SetMarkerColor(ci);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->SetMarkerStyle(22);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING__400->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401 = new TH1D("hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401","hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->SetBinContent(1,0.1319467);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->SetBinError(1,0.0001882852);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->SetLineColor(ci);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->SetLineStyle(10);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->SetMarkerColor(ci);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->SetMarkerStyle(22);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING__401->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402 = new TH1D("hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402","hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->SetBinContent(1,0.127112);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->SetBinError(1,0.0003142943);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->SetLineColor(ci);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->SetMarkerColor(ci);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->SetMarkerStyle(22);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING__402->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403 = new TH1D("hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403","hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->SetBinContent(2,0.1519011);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->SetBinError(2,0.001323287);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->SetLineColor(ci);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->SetMarkerColor(ci);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->SetMarkerStyle(22);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_0_mini_charm_balancing_CLOSEPACKING__403->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404 = new TH1D("hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404","hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->SetBinContent(2,0.1520284);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->SetBinError(2,0.0004445936);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->SetLineColor(ci);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->SetLineStyle(2);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->SetMarkerColor(ci);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->SetMarkerStyle(22);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_1_mini_charm_balancing_CLOSEPACKING__404->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405 = new TH1D("hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405","hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->SetBinContent(2,0.1507787);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->SetBinError(2,0.000208996);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->SetLineColor(ci);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->SetLineStyle(3);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->SetMarkerColor(ci);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->SetMarkerStyle(22);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_2_mini_charm_balancing_CLOSEPACKING__405->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406 = new TH1D("hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406","hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->SetBinContent(2,0.1468304);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->SetBinError(2,0.0002111376);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->SetLineColor(ci);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->SetLineStyle(4);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->SetMarkerColor(ci);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->SetMarkerStyle(22);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_3_mini_charm_balancing_CLOSEPACKING__406->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407 = new TH1D("hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407","hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->SetBinContent(2,0.1392901);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->SetBinError(2,0.0002971662);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->SetLineColor(ci);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->SetLineStyle(5);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->SetMarkerColor(ci);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->SetMarkerStyle(22);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_4_mini_charm_balancing_CLOSEPACKING__407->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408 = new TH1D("hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408","hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->SetBinContent(2,0.1370369);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->SetBinError(2,8.098327e-05);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->SetLineColor(ci);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->SetLineStyle(6);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->SetMarkerColor(ci);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->SetMarkerStyle(22);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_5_mini_charm_balancing_CLOSEPACKING__408->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409 = new TH1D("hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409","hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->SetBinContent(2,0.1355277);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->SetBinError(2,0.0002318955);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->SetLineColor(ci);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->SetLineStyle(7);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->SetMarkerColor(ci);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->SetMarkerStyle(22);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_6_mini_charm_balancing_CLOSEPACKING__409->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410 = new TH1D("hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410","hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->SetBinContent(2,0.129699);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->SetBinError(2,0.0001789888);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->SetLineColor(ci);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->SetLineStyle(8);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->SetMarkerColor(ci);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->SetMarkerStyle(22);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_7_mini_charm_balancing_CLOSEPACKING__410->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411 = new TH1D("hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411","hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->SetBinContent(2,0.129699);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->SetBinError(2,0.0001789888);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->SetLineColor(ci);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->SetLineStyle(9);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->SetMarkerColor(ci);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->SetMarkerStyle(22);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_8_mini_charm_balancing_CLOSEPACKING__411->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412 = new TH1D("hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412","hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->SetBinContent(2,0.129699);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->SetBinError(2,0.0001789888);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->SetLineColor(ci);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->SetLineStyle(10);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->SetMarkerColor(ci);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->SetMarkerStyle(22);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_9_mini_charm_balancing_CLOSEPACKING__412->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413 = new TH1D("hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413","hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->SetBinContent(2,0.1204132);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->SetBinError(2,0.0003136946);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->SetLineColor(ci);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->SetMarkerColor(ci);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->SetMarkerStyle(22);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_10_mini_charm_balancing_CLOSEPACKING__413->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414 = new TH1D("hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414","hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->SetBinContent(3,0.02718944);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->SetBinError(3,0.0007918484);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->SetLineColor(ci);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->SetMarkerColor(ci);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->SetMarkerStyle(22);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_0_mini_charm_balancing_CLOSEPACKING__414->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415 = new TH1D("hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415","hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->SetBinContent(3,0.02487922);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->SetBinError(3,0.0001774243);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->SetLineColor(ci);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->SetLineStyle(2);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->SetMarkerColor(ci);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->SetMarkerStyle(22);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_1_mini_charm_balancing_CLOSEPACKING__415->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416 = new TH1D("hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416","hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->SetBinContent(3,0.02171819);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->SetBinError(3,0.0001570542);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->SetLineColor(ci);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->SetLineStyle(3);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->SetMarkerColor(ci);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->SetMarkerStyle(22);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_2_mini_charm_balancing_CLOSEPACKING__416->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417 = new TH1D("hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417","hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->SetBinContent(3,0.01983338);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->SetBinError(3,0.0001455841);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->SetLineColor(ci);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->SetLineStyle(4);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->SetMarkerColor(ci);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->SetMarkerStyle(22);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_3_mini_charm_balancing_CLOSEPACKING__417->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418 = new TH1D("hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418","hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->SetBinContent(3,0.01727749);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->SetBinError(3,9.726185e-05);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->SetLineColor(ci);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->SetLineStyle(5);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->SetMarkerColor(ci);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->SetMarkerStyle(22);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_4_mini_charm_balancing_CLOSEPACKING__418->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419 = new TH1D("hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419","hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->SetBinContent(3,0.0159394);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->SetBinError(3,8.522477e-05);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->SetLineColor(ci);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->SetLineStyle(6);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->SetMarkerColor(ci);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->SetMarkerStyle(22);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_5_mini_charm_balancing_CLOSEPACKING__419->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420 = new TH1D("hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420","hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->SetBinContent(3,0.01504318);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->SetBinError(3,9.702354e-05);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->SetLineColor(ci);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->SetLineStyle(7);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->SetMarkerColor(ci);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->SetMarkerStyle(22);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_6_mini_charm_balancing_CLOSEPACKING__420->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421 = new TH1D("hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421","hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->SetBinContent(3,0.0129993);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->SetBinError(3,6.7332e-05);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->SetLineColor(ci);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->SetLineStyle(8);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->SetMarkerColor(ci);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->SetMarkerStyle(22);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_7_mini_charm_balancing_CLOSEPACKING__421->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422 = new TH1D("hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422","hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->SetBinContent(3,0.0129993);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->SetBinError(3,6.7332e-05);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->SetLineColor(ci);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->SetLineStyle(9);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->SetMarkerColor(ci);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->SetMarkerStyle(22);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_8_mini_charm_balancing_CLOSEPACKING__422->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423 = new TH1D("hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423","hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->SetBinContent(3,0.0129993);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->SetBinError(3,6.7332e-05);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->SetLineColor(ci);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->SetLineStyle(10);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->SetMarkerColor(ci);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->SetMarkerStyle(22);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_9_mini_charm_balancing_CLOSEPACKING__423->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424 = new TH1D("hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424","hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING",3,0,3);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->SetBinContent(3,0.01182831);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->SetBinError(3,0.0001028648);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->SetLineColor(ci);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->SetMarkerColor(ci);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->SetMarkerStyle(22);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_10_mini_charm_balancing_CLOSEPACKING__424->Draw("same PE");
   
   leg = new TLegend(0.63,0.68,0.9,0.88,NULL,"brNDC");
   leg->SetBorderSize(1);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("hYields_CHARM_2_0_0_mini_charm_balancing_CLOSEPACKING","0-1%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_2_0_1_mini_charm_balancing_CLOSEPACKING","1-10%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(2);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_2_0_2_mini_charm_balancing_CLOSEPACKING","10-20%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(3);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_2_0_3_mini_charm_balancing_CLOSEPACKING","20-30%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(4);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_2_0_4_mini_charm_balancing_CLOSEPACKING","30-40%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(5);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_2_0_5_mini_charm_balancing_CLOSEPACKING","40-50%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(6);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_2_0_6_mini_charm_balancing_CLOSEPACKING","50-60%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(7);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_2_0_7_mini_charm_balancing_CLOSEPACKING","60-70%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(8);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_2_0_8_mini_charm_balancing_CLOSEPACKING","70-80%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(9);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_2_0_9_mini_charm_balancing_CLOSEPACKING","80-90%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(10);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_2_0_10_mini_charm_balancing_CLOSEPACKING","90-100%","lep");

   ci = TColor::GetColor("#cc00cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(22);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING__49->Modified();
   global_balancing_plots->cd();
  
// ------------>Primitives in pad: cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS
   TPad *cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50 = new TPad("cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS", "cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS",0.501,0.57,0.95,0.759);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->Draw();
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->cd();
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->Range(0,-4.003911,3.157895,-0.0929991);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetFillColor(0);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetBorderMode(0);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetBorderSize(2);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetLogy();
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetTickx(1);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetTicky(1);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetLeftMargin(0);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetRightMargin(0.05);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetTopMargin(0.001);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetBottomMargin(0.001);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetFrameBorderMode(0);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->SetFrameBorderMode(0);
   
   TH1D *hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425 = new TH1D("hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425","",3,0,3);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->SetMinimum(0.0001);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->SetMaximum(0.8);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->SetLineColor(ci);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->GetXaxis()->SetLabelFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->GetXaxis()->SetTitleOffset(1);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->GetXaxis()->SetTitleFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->GetYaxis()->SetTitle("yield");
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->GetYaxis()->SetLabelFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->GetYaxis()->SetTitleFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->GetZaxis()->SetLabelFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->GetZaxis()->SetTitleOffset(1);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->GetZaxis()->SetTitleFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_JUNCTIONS__425->Draw("PE");
   
   TH1D *hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426 = new TH1D("hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426","hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->SetBinContent(1,0.2053488);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->SetBinError(1,0.0009597083);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->SetLineColor(ci);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->SetMarkerColor(ci);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->SetMarkerStyle(21);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS__426->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427 = new TH1D("hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427","hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->SetBinContent(1,0.1811731);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->SetBinError(1,0.0003281371);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->SetLineColor(ci);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->SetLineStyle(2);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->SetMarkerColor(ci);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->SetMarkerStyle(21);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS__427->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428 = new TH1D("hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428","hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->SetBinContent(1,0.1598062);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->SetBinError(1,0.0002491835);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->SetLineColor(ci);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->SetLineStyle(3);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->SetMarkerColor(ci);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->SetMarkerStyle(21);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS__428->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429 = new TH1D("hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429","hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->SetBinContent(1,0.1481558);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->SetBinError(1,0.0002290783);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->SetLineColor(ci);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->SetLineStyle(4);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->SetMarkerColor(ci);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->SetMarkerStyle(21);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS__429->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430 = new TH1D("hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430","hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->SetBinContent(1,0.1411379);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->SetBinError(1,0.0001283714);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->SetLineColor(ci);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->SetLineStyle(5);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->SetMarkerColor(ci);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->SetMarkerStyle(21);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS__430->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431 = new TH1D("hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431","hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->SetBinContent(1,0.1346073);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->SetBinError(1,0.0001002446);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->SetLineColor(ci);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->SetLineStyle(6);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->SetMarkerColor(ci);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->SetMarkerStyle(21);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS__431->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432 = new TH1D("hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432","hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->SetBinContent(1,0.1321891);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->SetBinError(1,0.0001798853);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->SetLineColor(ci);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->SetLineStyle(7);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->SetMarkerColor(ci);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->SetMarkerStyle(21);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS__432->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433 = new TH1D("hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433","hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->SetBinContent(1,0.1291587);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->SetBinError(1,0.0001341668);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->SetLineColor(ci);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->SetLineStyle(8);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->SetMarkerColor(ci);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->SetMarkerStyle(21);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS__433->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434 = new TH1D("hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434","hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->SetBinContent(1,0.1265773);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->SetBinError(1,0.0001894667);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->SetLineColor(ci);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->SetLineStyle(9);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->SetMarkerColor(ci);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->SetMarkerStyle(21);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS__434->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435 = new TH1D("hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435","hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->SetBinContent(1,0.1265773);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->SetBinError(1,0.0001894667);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->SetLineColor(ci);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->SetLineStyle(10);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->SetMarkerColor(ci);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->SetMarkerStyle(21);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS__435->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436 = new TH1D("hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436","hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->SetBinContent(1,0.123424);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->SetBinError(1,0.0003687006);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->SetLineColor(ci);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->SetMarkerColor(ci);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->SetMarkerStyle(21);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS__436->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437 = new TH1D("hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437","hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->SetBinContent(2,0.1494212);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->SetBinError(2,0.001300918);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->SetLineColor(ci);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->SetMarkerColor(ci);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->SetMarkerStyle(21);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_0_mini_charm_balancing_JUNCTIONS__437->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438 = new TH1D("hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438","hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->SetBinContent(2,0.1519379);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->SetBinError(2,0.0003431982);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->SetLineColor(ci);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->SetLineStyle(2);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->SetMarkerColor(ci);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->SetMarkerStyle(21);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_1_mini_charm_balancing_JUNCTIONS__438->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439 = new TH1D("hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439","hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->SetBinContent(2,0.1484858);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->SetBinError(2,0.0001857285);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->SetLineColor(ci);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->SetLineStyle(3);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->SetMarkerColor(ci);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->SetMarkerStyle(21);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_2_mini_charm_balancing_JUNCTIONS__439->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440 = new TH1D("hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440","hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->SetBinContent(2,0.1420188);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->SetBinError(2,0.000338852);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->SetLineColor(ci);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->SetLineStyle(4);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->SetMarkerColor(ci);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->SetMarkerStyle(21);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_3_mini_charm_balancing_JUNCTIONS__440->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441 = new TH1D("hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441","hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->SetBinContent(2,0.1371071);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->SetBinError(2,0.000219255);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->SetLineColor(ci);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->SetLineStyle(5);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->SetMarkerColor(ci);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->SetMarkerStyle(21);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_4_mini_charm_balancing_JUNCTIONS__441->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442 = new TH1D("hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442","hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->SetBinContent(2,0.1325375);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->SetBinError(2,0.0001634729);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->SetLineColor(ci);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->SetLineStyle(6);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->SetMarkerColor(ci);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->SetMarkerStyle(21);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_5_mini_charm_balancing_JUNCTIONS__442->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443 = new TH1D("hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443","hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->SetBinContent(2,0.1308792);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->SetBinError(2,0.0001674788);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->SetLineColor(ci);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->SetLineStyle(7);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->SetMarkerColor(ci);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->SetMarkerStyle(21);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_6_mini_charm_balancing_JUNCTIONS__443->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444 = new TH1D("hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444","hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->SetBinContent(2,0.1277115);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->SetBinError(2,0.0001442231);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->SetLineColor(ci);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->SetLineStyle(8);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->SetMarkerColor(ci);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->SetMarkerStyle(21);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_7_mini_charm_balancing_JUNCTIONS__444->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445 = new TH1D("hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445","hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->SetBinContent(2,0.1250131);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->SetBinError(2,0.0002146837);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->SetLineColor(ci);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->SetLineStyle(9);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->SetMarkerColor(ci);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->SetMarkerStyle(21);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_8_mini_charm_balancing_JUNCTIONS__445->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446 = new TH1D("hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446","hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->SetBinContent(2,0.1250131);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->SetBinError(2,0.0002146837);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->SetLineColor(ci);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->SetLineStyle(10);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->SetMarkerColor(ci);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->SetMarkerStyle(21);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_9_mini_charm_balancing_JUNCTIONS__446->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447 = new TH1D("hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447","hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->SetBinContent(2,0.1163594);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->SetBinError(2,0.0003479792);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->SetLineColor(ci);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->SetMarkerColor(ci);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->SetMarkerStyle(21);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_10_mini_charm_balancing_JUNCTIONS__447->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448 = new TH1D("hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448","hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->SetBinContent(3,0.03122249);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->SetBinError(3,0.0005241503);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->SetLineColor(ci);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->SetMarkerColor(ci);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->SetMarkerStyle(21);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_0_mini_charm_balancing_JUNCTIONS__448->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449 = new TH1D("hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449","hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->SetBinContent(3,0.02867929);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->SetBinError(3,0.0001609249);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->SetLineColor(ci);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->SetLineStyle(2);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->SetMarkerColor(ci);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->SetMarkerStyle(21);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_1_mini_charm_balancing_JUNCTIONS__449->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450 = new TH1D("hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450","hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->SetBinContent(3,0.02474784);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->SetBinError(3,9.584542e-05);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->SetLineColor(ci);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->SetLineStyle(3);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->SetMarkerColor(ci);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->SetMarkerStyle(21);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_2_mini_charm_balancing_JUNCTIONS__450->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451 = new TH1D("hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451","hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->SetBinContent(3,0.02205226);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->SetBinError(3,8.663711e-05);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->SetLineColor(ci);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->SetLineStyle(4);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->SetMarkerColor(ci);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->SetMarkerStyle(21);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_3_mini_charm_balancing_JUNCTIONS__451->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452 = new TH1D("hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452","hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->SetBinContent(3,0.0199409);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->SetBinError(3,0.0001048266);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->SetLineColor(ci);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->SetLineStyle(5);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->SetMarkerColor(ci);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->SetMarkerStyle(21);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_4_mini_charm_balancing_JUNCTIONS__452->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453 = new TH1D("hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453","hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->SetBinContent(3,0.01746761);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->SetBinError(3,7.617229e-05);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->SetLineColor(ci);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->SetLineStyle(6);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->SetMarkerColor(ci);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->SetMarkerStyle(21);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_5_mini_charm_balancing_JUNCTIONS__453->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454 = new TH1D("hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454","hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->SetBinContent(3,0.01641249);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->SetBinError(3,7.76461e-05);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->SetLineColor(ci);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->SetLineStyle(7);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->SetMarkerColor(ci);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->SetMarkerStyle(21);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_6_mini_charm_balancing_JUNCTIONS__454->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455 = new TH1D("hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455","hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->SetBinContent(3,0.01528062);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->SetBinError(3,4.47768e-05);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->SetLineColor(ci);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->SetLineStyle(8);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->SetMarkerColor(ci);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->SetMarkerStyle(21);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_7_mini_charm_balancing_JUNCTIONS__455->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456 = new TH1D("hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456","hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->SetBinContent(3,0.01431646);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->SetBinError(3,5.522984e-05);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->SetLineColor(ci);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->SetLineStyle(9);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->SetMarkerColor(ci);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->SetMarkerStyle(21);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_8_mini_charm_balancing_JUNCTIONS__456->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457 = new TH1D("hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457","hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->SetBinContent(3,0.01431646);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->SetBinError(3,5.522984e-05);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->SetLineColor(ci);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->SetLineStyle(10);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->SetMarkerColor(ci);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->SetMarkerStyle(21);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_9_mini_charm_balancing_JUNCTIONS__457->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458 = new TH1D("hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458","hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS",3,0,3);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->SetBinContent(3,0.0131145);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->SetBinError(3,0.0001443256);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->SetLineColor(ci);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->SetMarkerColor(ci);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->SetMarkerStyle(21);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_10_mini_charm_balancing_JUNCTIONS__458->Draw("same PE");
   
   leg = new TLegend(0.63,0.68,0.9,0.88,NULL,"brNDC");
   leg->SetBorderSize(1);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("hYields_CHARM_1_0_0_mini_charm_balancing_JUNCTIONS","0-1%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_1_0_1_mini_charm_balancing_JUNCTIONS","1-10%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(2);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_1_0_2_mini_charm_balancing_JUNCTIONS","10-20%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(3);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_1_0_3_mini_charm_balancing_JUNCTIONS","20-30%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(4);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_1_0_4_mini_charm_balancing_JUNCTIONS","30-40%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(5);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_1_0_5_mini_charm_balancing_JUNCTIONS","40-50%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(6);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_1_0_6_mini_charm_balancing_JUNCTIONS","50-60%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(7);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_1_0_7_mini_charm_balancing_JUNCTIONS","60-70%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(8);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_1_0_8_mini_charm_balancing_JUNCTIONS","70-80%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(9);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_1_0_9_mini_charm_balancing_JUNCTIONS","80-90%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(10);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_1_0_10_mini_charm_balancing_JUNCTIONS","90-100%","lep");

   ci = TColor::GetColor("#0000cc");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS__50->Modified();
   global_balancing_plots->cd();
  
// ------------>Primitives in pad: cMiniPad_CHARM_mini_charm_balancing_MONASH
   TPad *cMiniPad_CHARM_mini_charm_balancing_MONASH__51 = new TPad("cMiniPad_CHARM_mini_charm_balancing_MONASH", "cMiniPad_CHARM_mini_charm_balancing_MONASH",0.501,0.38,0.95,0.569);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->Draw();
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->cd();
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->Range(0,-4.003911,3.157895,-0.0929991);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetFillColor(0);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetBorderMode(0);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetBorderSize(2);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetLogy();
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetTickx(1);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetTicky(1);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetLeftMargin(0);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetRightMargin(0.05);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetTopMargin(0.001);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetBottomMargin(0.001);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetFrameBorderMode(0);
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->SetFrameBorderMode(0);
   
   TH1D *hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459 = new TH1D("hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459","",3,0,3);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->SetMinimum(0.0001);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->SetMaximum(0.8);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->SetLineColor(ci);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetXaxis()->SetBinLabel(1,"D-");
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetXaxis()->SetBinLabel(2,"D^{0}-bar");
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetXaxis()->SetBinLabel(3,"Lambda_c(+)-bar");
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetXaxis()->SetLabelFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetXaxis()->SetTitleOffset(1);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetXaxis()->SetTitleFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetYaxis()->SetTitle("yield");
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetYaxis()->SetLabelFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetYaxis()->SetTitleFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetZaxis()->SetLabelFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetZaxis()->SetTitleOffset(1);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->GetZaxis()->SetTitleFont(42);
   hYieldsTemplate_CHARM_mini_charm_balancing_MONASH__459->Draw("PE");
   
   TH1D *hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460 = new TH1D("hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460","hYields_CHARM_0_0_0_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->SetBinContent(1,0.2586502);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->SetBinError(1,0.0008341747);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->SetEntries(1);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->SetLineWidth(2);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->SetMarkerStyle(20);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_0_mini_charm_balancing_MONASH__460->Draw("same PE");
   
   TH1D *hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461 = new TH1D("hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461","hYields_CHARM_0_0_1_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->SetBinContent(1,0.225451);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->SetBinError(1,0.0003498644);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->SetEntries(1);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->SetLineStyle(2);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->SetLineWidth(2);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->SetMarkerStyle(20);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_1_mini_charm_balancing_MONASH__461->Draw("same PE");
   
   TH1D *hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462 = new TH1D("hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462","hYields_CHARM_0_0_2_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->SetBinContent(1,0.1996718);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->SetBinError(1,0.0002154022);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->SetEntries(1);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->SetLineStyle(3);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->SetLineWidth(2);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->SetMarkerStyle(20);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_2_mini_charm_balancing_MONASH__462->Draw("same PE");
   
   TH1D *hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463 = new TH1D("hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463","hYields_CHARM_0_0_3_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->SetBinContent(1,0.1743267);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->SetBinError(1,0.0002599427);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->SetEntries(1);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->SetLineStyle(4);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->SetLineWidth(2);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->SetMarkerStyle(20);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_3_mini_charm_balancing_MONASH__463->Draw("same PE");
   
   TH1D *hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464 = new TH1D("hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464","hYields_CHARM_0_0_4_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->SetBinContent(1,0.1691611);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->SetBinError(1,0.0003246344);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->SetEntries(1);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->SetLineStyle(5);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->SetLineWidth(2);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->SetMarkerStyle(20);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_4_mini_charm_balancing_MONASH__464->Draw("same PE");
   
   TH1D *hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465 = new TH1D("hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465","hYields_CHARM_0_0_5_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->SetBinContent(1,0.1543239);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->SetBinError(1,0.0001941088);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->SetEntries(1);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->SetLineStyle(6);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->SetLineWidth(2);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->SetMarkerStyle(20);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_5_mini_charm_balancing_MONASH__465->Draw("same PE");
   
   TH1D *hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466 = new TH1D("hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466","hYields_CHARM_0_0_6_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->SetBinContent(1,0.1543239);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->SetBinError(1,0.0001941088);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->SetEntries(1);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->SetLineStyle(7);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->SetLineWidth(2);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->SetMarkerStyle(20);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_6_mini_charm_balancing_MONASH__466->Draw("same PE");
   
   TH1D *hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467 = new TH1D("hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467","hYields_CHARM_0_0_7_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->SetBinContent(1,0.1393895);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->SetBinError(1,0.0002434024);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->SetEntries(1);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->SetLineStyle(8);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->SetLineWidth(2);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->SetMarkerStyle(20);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_7_mini_charm_balancing_MONASH__467->Draw("same PE");
   
   TH1D *hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468 = new TH1D("hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468","hYields_CHARM_0_0_8_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->SetBinContent(1,0.1393895);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->SetBinError(1,0.0002434024);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->SetEntries(1);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->SetLineStyle(9);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->SetLineWidth(2);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->SetMarkerStyle(20);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_8_mini_charm_balancing_MONASH__468->Draw("same PE");
   
   TH1D *hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469 = new TH1D("hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469","hYields_CHARM_0_0_9_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->SetBinContent(1,0.1393895);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->SetBinError(1,0.0002434024);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->SetEntries(1);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->SetLineStyle(10);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->SetLineWidth(2);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->SetMarkerStyle(20);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_9_mini_charm_balancing_MONASH__469->Draw("same PE");
   
   TH1D *hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470 = new TH1D("hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470","hYields_CHARM_0_0_10_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->SetBinContent(1,0.1300995);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->SetBinError(1,0.0001901282);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->SetEntries(1);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->SetLineWidth(2);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->SetMarkerStyle(20);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_10_mini_charm_balancing_MONASH__470->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471 = new TH1D("hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471","hYields_CHARM_0_1_0_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->SetBinContent(2,0.1914884);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->SetBinError(2,0.001271207);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->SetEntries(1);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->SetLineWidth(2);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->SetMarkerStyle(20);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_0_mini_charm_balancing_MONASH__471->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472 = new TH1D("hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472","hYields_CHARM_0_1_1_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->SetBinContent(2,0.1888201);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->SetBinError(2,0.0002731156);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->SetEntries(1);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->SetLineStyle(2);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->SetLineWidth(2);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->SetMarkerStyle(20);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_1_mini_charm_balancing_MONASH__472->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473 = new TH1D("hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473","hYields_CHARM_0_1_2_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->SetBinContent(2,0.183857);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->SetBinError(2,0.0003618617);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->SetEntries(1);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->SetLineStyle(3);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->SetLineWidth(2);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->SetMarkerStyle(20);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_2_mini_charm_balancing_MONASH__473->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474 = new TH1D("hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474","hYields_CHARM_0_1_3_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->SetBinContent(2,0.1685912);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->SetBinError(2,0.0002518395);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->SetEntries(1);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->SetLineStyle(4);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->SetLineWidth(2);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->SetMarkerStyle(20);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_3_mini_charm_balancing_MONASH__474->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475 = new TH1D("hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475","hYields_CHARM_0_1_4_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->SetBinContent(2,0.1649914);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->SetBinError(2,0.0002989243);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->SetEntries(1);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->SetLineStyle(5);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->SetLineWidth(2);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->SetMarkerStyle(20);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_4_mini_charm_balancing_MONASH__475->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476 = new TH1D("hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476","hYields_CHARM_0_1_5_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->SetBinContent(2,0.1530107);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->SetBinError(2,0.0002802121);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->SetEntries(1);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->SetLineStyle(6);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->SetLineWidth(2);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->SetMarkerStyle(20);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_5_mini_charm_balancing_MONASH__476->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477 = new TH1D("hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477","hYields_CHARM_0_1_6_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->SetBinContent(2,0.1530107);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->SetBinError(2,0.0002802121);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->SetEntries(1);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->SetLineStyle(7);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->SetLineWidth(2);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->SetMarkerStyle(20);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_6_mini_charm_balancing_MONASH__477->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478 = new TH1D("hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478","hYields_CHARM_0_1_7_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->SetBinContent(2,0.1366197);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->SetBinError(2,0.0001276187);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->SetEntries(1);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->SetLineStyle(8);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->SetLineWidth(2);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->SetMarkerStyle(20);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_7_mini_charm_balancing_MONASH__478->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479 = new TH1D("hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479","hYields_CHARM_0_1_8_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->SetBinContent(2,0.1366197);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->SetBinError(2,0.0001276187);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->SetEntries(1);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->SetLineStyle(9);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->SetLineWidth(2);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->SetMarkerStyle(20);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_8_mini_charm_balancing_MONASH__479->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480 = new TH1D("hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480","hYields_CHARM_0_1_9_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->SetBinContent(2,0.1366197);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->SetBinError(2,0.0001276187);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->SetEntries(1);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->SetLineStyle(10);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->SetLineWidth(2);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->SetMarkerStyle(20);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_9_mini_charm_balancing_MONASH__480->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481 = new TH1D("hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481","hYields_CHARM_0_1_10_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->SetBinContent(2,0.1225575);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->SetBinError(2,0.0004041432);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->SetEntries(1);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->SetLineWidth(2);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->SetMarkerStyle(20);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_10_mini_charm_balancing_MONASH__481->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482 = new TH1D("hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482","hYields_CHARM_0_2_0_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->SetBinContent(3,0.01822375);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->SetBinError(3,0.0004166984);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->SetEntries(1);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->SetLineWidth(2);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->SetMarkerStyle(20);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_0_mini_charm_balancing_MONASH__482->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483 = new TH1D("hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483","hYields_CHARM_0_2_1_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->SetBinContent(3,0.01845535);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->SetBinError(3,0.000135496);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->SetEntries(1);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->SetLineStyle(2);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->SetLineWidth(2);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->SetMarkerStyle(20);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_1_mini_charm_balancing_MONASH__483->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484 = new TH1D("hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484","hYields_CHARM_0_2_2_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->SetBinContent(3,0.01808872);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->SetBinError(3,0.0001691493);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->SetEntries(1);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->SetLineStyle(3);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->SetLineWidth(2);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->SetMarkerStyle(20);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_2_mini_charm_balancing_MONASH__484->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485 = new TH1D("hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485","hYields_CHARM_0_2_3_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->SetBinContent(3,0.01683392);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->SetBinError(3,8.906384e-05);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->SetEntries(1);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->SetLineStyle(4);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->SetLineWidth(2);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->SetMarkerStyle(20);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_3_mini_charm_balancing_MONASH__485->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486 = new TH1D("hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486","hYields_CHARM_0_2_4_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->SetBinContent(3,0.01647465);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->SetBinError(3,0.0001165126);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->SetEntries(1);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->SetLineStyle(5);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->SetLineWidth(2);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->SetMarkerStyle(20);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_4_mini_charm_balancing_MONASH__486->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487 = new TH1D("hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487","hYields_CHARM_0_2_5_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->SetBinContent(3,0.01532322);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->SetBinError(3,9.070377e-05);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->SetEntries(1);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->SetLineStyle(6);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->SetLineWidth(2);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->SetMarkerStyle(20);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_5_mini_charm_balancing_MONASH__487->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488 = new TH1D("hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488","hYields_CHARM_0_2_6_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->SetBinContent(3,0.01532322);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->SetBinError(3,9.070377e-05);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->SetEntries(1);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->SetLineStyle(7);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->SetLineWidth(2);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->SetMarkerStyle(20);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_6_mini_charm_balancing_MONASH__488->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489 = new TH1D("hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489","hYields_CHARM_0_2_7_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->SetBinContent(3,0.01426926);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->SetBinError(3,8.020636e-05);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->SetEntries(1);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->SetLineStyle(8);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->SetLineWidth(2);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->SetMarkerStyle(20);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_7_mini_charm_balancing_MONASH__489->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490 = new TH1D("hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490","hYields_CHARM_0_2_8_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->SetBinContent(3,0.01426926);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->SetBinError(3,8.020636e-05);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->SetEntries(1);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->SetLineStyle(9);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->SetLineWidth(2);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->SetMarkerStyle(20);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_8_mini_charm_balancing_MONASH__490->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491 = new TH1D("hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491","hYields_CHARM_0_2_9_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->SetBinContent(3,0.01426926);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->SetBinError(3,8.020636e-05);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->SetEntries(1);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->SetLineStyle(10);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->SetLineWidth(2);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->SetMarkerStyle(20);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_9_mini_charm_balancing_MONASH__491->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492 = new TH1D("hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492","hYields_CHARM_0_2_10_mini_charm_balancing_MONASH",3,0,3);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->SetBinContent(3,0.01358157);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->SetBinError(3,9.583323e-05);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->SetEntries(1);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->SetLineWidth(2);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->SetMarkerStyle(20);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_10_mini_charm_balancing_MONASH__492->Draw("same PE");
   
   leg = new TLegend(0.63,0.68,0.9,0.88,NULL,"brNDC");
   leg->SetBorderSize(1);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("hYields_CHARM_0_0_0_mini_charm_balancing_MONASH","0-1%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_0_0_1_mini_charm_balancing_MONASH","1-10%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(2);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_0_0_2_mini_charm_balancing_MONASH","10-20%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(3);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_0_0_3_mini_charm_balancing_MONASH","20-30%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(4);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_0_0_4_mini_charm_balancing_MONASH","30-40%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(5);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_0_0_5_mini_charm_balancing_MONASH","40-50%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(6);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_0_0_6_mini_charm_balancing_MONASH","50-60%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(7);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_0_0_7_mini_charm_balancing_MONASH","60-70%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(8);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_0_0_8_mini_charm_balancing_MONASH","70-80%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(9);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_0_0_9_mini_charm_balancing_MONASH","80-90%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(10);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   entry=leg->AddEntry("hYields_CHARM_0_0_10_mini_charm_balancing_MONASH","90-100%","lep");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1);
   entry->SetTextFont(42);
   leg->Draw();
   cMiniPad_CHARM_mini_charm_balancing_MONASH__51->Modified();
   global_balancing_plots->cd();
  
// ------------>Primitives in pad: cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH
   TPad *cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52 = new TPad("cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH", "cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH",0.501,0.19,0.95,0.379);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->Draw();
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->cd();
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->Range(0,-1.004008,3.157895,3.004008);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetFillColor(0);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetBorderMode(0);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetBorderSize(2);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetLogy();
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetTickx(1);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetTicky(1);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetLeftMargin(0);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetRightMargin(0.05);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetTopMargin(0.001);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetBottomMargin(0.001);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetFrameBorderMode(0);
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->SetFrameBorderMode(0);
   
   TH1D *hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493 = new TH1D("hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493","",3,0,3);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->SetMinimum(0.1);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->SetMaximum(1000);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->SetLineColor(ci);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetXaxis()->SetTitle("associate");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetXaxis()->SetBinLabel(1,"D-");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetXaxis()->SetBinLabel(2,"D^{0}-bar");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetXaxis()->SetBinLabel(3,"Lambda_c(+)-bar");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetXaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetXaxis()->SetTitleOffset(1);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetXaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetYaxis()->SetTitle("CP/MON");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetYaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetYaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetZaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetZaxis()->SetTitleOffset(1);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->GetZaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__493->Draw("PE");
   
   TH1D *hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494 = new TH1D("hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494","hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->SetBinContent(1,0.7804891);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->SetBinError(1,0.005310933);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->SetLineColor(ci);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->SetMarkerColor(ci);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->SetMarkerStyle(22);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__494->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495 = new TH1D("hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495","hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->SetBinContent(1,0.8031333);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->SetBinError(1,0.002034512);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->SetLineColor(ci);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->SetLineStyle(2);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->SetMarkerColor(ci);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->SetMarkerStyle(22);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__495->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496 = new TH1D("hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496","hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->SetBinContent(1,0.8063663);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->SetBinError(1,0.001975884);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->SetLineColor(ci);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->SetLineStyle(3);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->SetMarkerColor(ci);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->SetMarkerStyle(22);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__496->Draw("same PE");
   
   TH1D *hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497 = new TH1D("hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497","hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->SetBinContent(1,0.8712298);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->SetBinError(1,0.002056252);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->SetLineColor(ci);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->SetLineStyle(4);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->SetMarkerColor(ci);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->SetMarkerStyle(22);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__497->Draw("same PE");
   
   TH1D *hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498 = new TH1D("hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498","hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->SetBinContent(1,0.8427982);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->SetBinError(1,0.002562977);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->SetLineColor(ci);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->SetLineStyle(5);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->SetMarkerColor(ci);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->SetMarkerStyle(22);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__498->Draw("same PE");
   
   TH1D *hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499 = new TH1D("hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499","hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->SetBinContent(1,0.902801);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->SetBinError(1,0.001985974);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->SetLineColor(ci);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->SetLineStyle(6);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->SetMarkerColor(ci);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->SetMarkerStyle(22);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__499->Draw("same PE");
   
   TH1D *hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500 = new TH1D("hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500","hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->SetBinContent(1,0.8887181);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->SetBinError(1,0.00224143);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->SetLineColor(ci);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->SetLineStyle(7);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->SetMarkerColor(ci);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->SetMarkerStyle(22);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__500->Draw("same PE");
   
   TH1D *hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501 = new TH1D("hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501","hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->SetBinContent(1,0.9466039);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->SetBinError(1,0.00213469);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->SetLineColor(ci);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->SetLineStyle(8);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->SetMarkerColor(ci);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->SetMarkerStyle(22);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__501->Draw("same PE");
   
   TH1D *hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502 = new TH1D("hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502","hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->SetBinContent(1,0.9466039);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->SetBinError(1,0.00213469);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->SetLineColor(ci);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->SetLineStyle(9);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->SetMarkerColor(ci);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->SetMarkerStyle(22);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__502->Draw("same PE");
   
   TH1D *hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503 = new TH1D("hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503","hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->SetBinContent(1,0.9466039);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->SetBinError(1,0.00213469);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->SetLineColor(ci);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->SetLineStyle(10);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->SetMarkerColor(ci);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->SetMarkerStyle(22);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__503->Draw("same PE");
   
   TH1D *hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504 = new TH1D("hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504","hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->SetBinContent(1,0.9770366);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->SetBinError(1,0.002806213);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->SetLineColor(ci);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->SetMarkerColor(ci);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->SetMarkerStyle(22);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__504->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505 = new TH1D("hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505","hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->SetBinContent(2,0.7932654);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->SetBinError(2,0.008688365);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->SetLineColor(ci);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->SetMarkerColor(ci);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->SetMarkerStyle(22);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__505->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506 = new TH1D("hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506","hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->SetBinContent(2,0.8051494);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->SetBinError(2,0.002626854);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->SetLineColor(ci);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->SetLineStyle(2);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->SetMarkerColor(ci);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->SetMarkerStyle(22);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__506->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507 = new TH1D("hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507","hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->SetBinContent(2,0.8200866);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->SetBinError(2,0.001974177);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->SetLineColor(ci);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->SetLineStyle(3);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->SetMarkerColor(ci);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->SetMarkerStyle(22);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__507->Draw("same PE");
   
   TH1D *hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508 = new TH1D("hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508","hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->SetBinContent(2,0.8709259);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->SetBinError(2,0.001805813);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->SetLineColor(ci);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->SetLineStyle(4);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->SetMarkerColor(ci);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->SetMarkerStyle(22);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__508->Draw("same PE");
   
   TH1D *hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509 = new TH1D("hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509","hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->SetBinContent(2,0.8442269);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->SetBinError(2,0.002362931);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->SetLineColor(ci);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->SetLineStyle(5);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->SetMarkerColor(ci);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->SetMarkerStyle(22);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__509->Draw("same PE");
   
   TH1D *hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510 = new TH1D("hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510","hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->SetBinContent(2,0.8956032);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->SetBinError(2,0.001723421);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->SetLineColor(ci);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->SetLineStyle(6);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->SetMarkerColor(ci);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->SetMarkerStyle(22);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__510->Draw("same PE");
   
   TH1D *hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511 = new TH1D("hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511","hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->SetBinContent(2,0.8857398);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->SetBinError(2,0.002219916);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->SetLineColor(ci);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->SetLineStyle(7);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->SetMarkerColor(ci);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->SetMarkerStyle(22);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__511->Draw("same PE");
   
   TH1D *hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512 = new TH1D("hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512","hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->SetBinContent(2,0.9493435);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->SetBinError(2,0.001582035);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->SetLineColor(ci);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->SetLineStyle(8);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->SetMarkerColor(ci);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->SetMarkerStyle(22);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__512->Draw("same PE");
   
   TH1D *hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513 = new TH1D("hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513","hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->SetBinContent(2,0.9493435);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->SetBinError(2,0.001582035);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->SetLineColor(ci);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->SetLineStyle(9);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->SetMarkerColor(ci);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->SetMarkerStyle(22);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__513->Draw("same PE");
   
   TH1D *hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514 = new TH1D("hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514","hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->SetBinContent(2,0.9493435);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->SetBinError(2,0.001582035);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->SetLineColor(ci);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->SetLineStyle(10);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->SetMarkerColor(ci);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->SetMarkerStyle(22);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__514->Draw("same PE");
   
   TH1D *hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515 = new TH1D("hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515","hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->SetBinContent(2,0.9825043);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->SetBinError(2,0.004128956);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->SetLineColor(ci);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->SetMarkerColor(ci);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->SetMarkerStyle(22);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__515->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516 = new TH1D("hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516","hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->SetBinContent(3,1.491978);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->SetBinError(3,0.05524373);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->SetLineColor(ci);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->SetMarkerColor(ci);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->SetMarkerStyle(22);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_CLOSEPACKING_over_MONASH__516->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517 = new TH1D("hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517","hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->SetBinContent(3,1.348076);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->SetBinError(3,0.01379785);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->SetLineColor(ci);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->SetLineStyle(2);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->SetMarkerColor(ci);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->SetMarkerStyle(22);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_CLOSEPACKING_over_MONASH__517->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518 = new TH1D("hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518","hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->SetBinContent(3,1.200649);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->SetBinError(3,0.01419291);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->SetLineColor(ci);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->SetLineStyle(3);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->SetMarkerColor(ci);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->SetMarkerStyle(22);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_CLOSEPACKING_over_MONASH__518->Draw("same PE");
   
   TH1D *hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519 = new TH1D("hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519","hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->SetBinContent(3,1.178179);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->SetBinError(3,0.01066058);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->SetLineColor(ci);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->SetLineStyle(4);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->SetMarkerColor(ci);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->SetMarkerStyle(22);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_CLOSEPACKING_over_MONASH__519->Draw("same PE");
   
   TH1D *hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520 = new TH1D("hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520","hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->SetBinContent(3,1.048732);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->SetBinError(3,0.009479668);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->SetLineColor(ci);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->SetLineStyle(5);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->SetMarkerColor(ci);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->SetMarkerStyle(22);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_CLOSEPACKING_over_MONASH__520->Draw("same PE");
   
   TH1D *hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521 = new TH1D("hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521","hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->SetBinContent(3,1.040212);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->SetBinError(3,0.00829742);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->SetLineColor(ci);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->SetLineStyle(6);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->SetMarkerColor(ci);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->SetMarkerStyle(22);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_CLOSEPACKING_over_MONASH__521->Draw("same PE");
   
   TH1D *hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522 = new TH1D("hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522","hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->SetBinContent(3,0.9817243);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->SetBinError(3,0.008594272);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->SetLineColor(ci);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->SetLineStyle(7);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->SetMarkerColor(ci);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->SetMarkerStyle(22);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_CLOSEPACKING_over_MONASH__522->Draw("same PE");
   
   TH1D *hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523 = new TH1D("hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523","hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->SetBinContent(3,0.9110006);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->SetBinError(3,0.006963266);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->SetLineColor(ci);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->SetLineStyle(8);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->SetMarkerColor(ci);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->SetMarkerStyle(22);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_CLOSEPACKING_over_MONASH__523->Draw("same PE");
   
   TH1D *hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524 = new TH1D("hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524","hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->SetBinContent(3,0.9110006);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->SetBinError(3,0.006963266);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->SetLineColor(ci);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->SetLineStyle(9);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->SetMarkerColor(ci);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->SetMarkerStyle(22);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_CLOSEPACKING_over_MONASH__524->Draw("same PE");
   
   TH1D *hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525 = new TH1D("hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525","hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->SetBinContent(3,0.9110006);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->SetBinError(3,0.006963266);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->SetLineColor(ci);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->SetLineStyle(10);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->SetMarkerColor(ci);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->SetMarkerStyle(22);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_CLOSEPACKING_over_MONASH__525->Draw("same PE");
   
   TH1D *hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526 = new TH1D("hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526","hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH",3,0,3);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->SetBinContent(3,0.8709089);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->SetBinError(3,0.009753314);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->SetEntries(1);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->SetLineColor(ci);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->SetLineWidth(2);

   ci = TColor::GetColor("#cc00cc");
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->SetMarkerColor(ci);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->SetMarkerStyle(22);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_CLOSEPACKING_over_MONASH__526->Draw("same PE");
   cMiniPad_CHARM_mini_charm_balancing_CLOSEPACKING_over_MONASH__52->Modified();
   global_balancing_plots->cd();
  
// ------------>Primitives in pad: cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH
   TPad *cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53 = new TPad("cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH", "cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH",0.501,0,0.95,0.189);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->Draw();
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->cd();
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->Range(0,-2.001252,3.157895,3.005006);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetFillColor(0);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetBorderMode(0);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetBorderSize(2);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetLogy();
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetTickx(1);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetTicky(1);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetLeftMargin(0);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetRightMargin(0.05);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetTopMargin(0.001);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetBottomMargin(0.2);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetFrameBorderMode(0);
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->SetFrameBorderMode(0);
   
   TH1D *hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527 = new TH1D("hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527","",3,0,3);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->SetMinimum(0.1);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->SetMaximum(1000);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->SetStats(0);

   ci = TColor::GetColor("#000099");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->SetLineColor(ci);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetXaxis()->SetTitle("associate");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetXaxis()->SetBinLabel(1,"D-");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetXaxis()->SetBinLabel(2,"D^{0}-bar");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetXaxis()->SetBinLabel(3,"Lambda_c(+)-bar");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetXaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetXaxis()->SetTitleOffset(1);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetXaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetYaxis()->SetTitle("JUN/MON");
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetYaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetYaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetZaxis()->SetLabelFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetZaxis()->SetTitleOffset(1);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->GetZaxis()->SetTitleFont(42);
   hYieldsTUNERatiosTemplate_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__527->Draw("PE");
   
   TH1D *hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528 = new TH1D("hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528","hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->SetBinContent(1,0.7939248);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->SetBinError(1,0.004508166);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->SetLineColor(ci);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->SetMarkerColor(ci);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->SetMarkerStyle(21);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_0_mini_charm_balancing_JUNCTIONS_over_MONASH__528->Draw("same PE");
   
   TH1D *hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529 = new TH1D("hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529","hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->SetBinContent(1,0.8036031);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->SetBinError(1,0.001916654);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->SetLineColor(ci);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->SetLineStyle(2);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->SetMarkerColor(ci);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->SetMarkerStyle(21);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_1_mini_charm_balancing_JUNCTIONS_over_MONASH__529->Draw("same PE");
   
   TH1D *hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530 = new TH1D("hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530","hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->SetBinContent(1,0.8003445);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->SetBinError(1,0.001517521);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->SetLineColor(ci);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->SetLineStyle(3);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->SetMarkerColor(ci);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->SetMarkerStyle(21);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_2_mini_charm_balancing_JUNCTIONS_over_MONASH__530->Draw("same PE");
   
   TH1D *hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531 = new TH1D("hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531","hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->SetBinContent(1,0.8498744);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->SetBinError(1,0.001825585);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->SetLineColor(ci);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->SetLineStyle(4);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->SetMarkerColor(ci);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->SetMarkerStyle(21);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_3_mini_charm_balancing_JUNCTIONS_over_MONASH__531->Draw("same PE");
   
   TH1D *hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532 = new TH1D("hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532","hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->SetBinContent(1,0.8343404);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->SetBinError(1,0.0017719);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->SetLineColor(ci);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->SetLineStyle(5);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->SetMarkerColor(ci);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->SetMarkerStyle(21);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_4_mini_charm_balancing_JUNCTIONS_over_MONASH__532->Draw("same PE");
   
   TH1D *hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533 = new TH1D("hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533","hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->SetBinContent(1,0.8722389);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->SetBinError(1,0.001274983);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->SetLineColor(ci);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->SetLineStyle(6);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->SetMarkerColor(ci);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->SetMarkerStyle(21);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_5_mini_charm_balancing_JUNCTIONS_over_MONASH__533->Draw("same PE");
   
   TH1D *hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534 = new TH1D("hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534","hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->SetBinContent(1,0.856569);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->SetBinError(1,0.001587287);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->SetLineColor(ci);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->SetLineStyle(7);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->SetMarkerColor(ci);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->SetMarkerStyle(21);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_6_mini_charm_balancing_JUNCTIONS_over_MONASH__534->Draw("same PE");
   
   TH1D *hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535 = new TH1D("hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535","hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->SetBinContent(1,0.9266026);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->SetBinError(1,0.001882686);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->SetLineColor(ci);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->SetLineStyle(8);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->SetMarkerColor(ci);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->SetMarkerStyle(21);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_7_mini_charm_balancing_JUNCTIONS_over_MONASH__535->Draw("same PE");
   
   TH1D *hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536 = new TH1D("hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536","hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->SetBinContent(1,0.9080835);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->SetBinError(1,0.002088546);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->SetLineColor(ci);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->SetLineStyle(9);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->SetMarkerColor(ci);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->SetMarkerStyle(21);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_8_mini_charm_balancing_JUNCTIONS_over_MONASH__536->Draw("same PE");
   
   TH1D *hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537 = new TH1D("hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537","hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->SetBinContent(1,0.9080835);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->SetBinError(1,0.002088546);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->SetLineColor(ci);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->SetLineStyle(10);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->SetMarkerColor(ci);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->SetMarkerStyle(21);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_9_mini_charm_balancing_JUNCTIONS_over_MONASH__537->Draw("same PE");
   
   TH1D *hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538 = new TH1D("hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538","hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->SetBinContent(1,0.9486893);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->SetBinError(1,0.00315494);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->SetLineColor(ci);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->SetMarkerColor(ci);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->SetMarkerStyle(21);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_0_10_mini_charm_balancing_JUNCTIONS_over_MONASH__538->Draw("same PE");
   
   TH1D *hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539 = new TH1D("hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539","hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->SetBinContent(2,0.7803147);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->SetBinError(2,0.00854334);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->SetLineColor(ci);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->SetMarkerColor(ci);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->SetMarkerStyle(21);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_0_mini_charm_balancing_JUNCTIONS_over_MONASH__539->Draw("same PE");
   
   TH1D *hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540 = new TH1D("hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540","hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->SetBinContent(2,0.8046702);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->SetBinError(2,0.002158312);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->SetLineColor(ci);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->SetLineStyle(2);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->SetMarkerColor(ci);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->SetMarkerStyle(21);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_1_mini_charm_balancing_JUNCTIONS_over_MONASH__540->Draw("same PE");
   
   TH1D *hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541 = new TH1D("hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541","hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->SetBinContent(2,0.8076155);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->SetBinError(2,0.00188336);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->SetLineColor(ci);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->SetLineStyle(3);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->SetMarkerColor(ci);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->SetMarkerStyle(21);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_2_mini_charm_balancing_JUNCTIONS_over_MONASH__541->Draw("same PE");
   
   TH1D *hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542 = new TH1D("hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542","hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->SetBinContent(2,0.8423854);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->SetBinError(2,0.002371316);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->SetLineColor(ci);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->SetLineStyle(4);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->SetMarkerColor(ci);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->SetMarkerStyle(21);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_3_mini_charm_balancing_JUNCTIONS_over_MONASH__542->Draw("same PE");
   
   TH1D *hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543 = new TH1D("hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543","hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->SetBinContent(2,0.8309957);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->SetBinError(2,0.002008149);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->SetLineColor(ci);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->SetLineStyle(5);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->SetMarkerColor(ci);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->SetMarkerStyle(21);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_4_mini_charm_balancing_JUNCTIONS_over_MONASH__543->Draw("same PE");
   
   TH1D *hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544 = new TH1D("hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544","hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->SetBinContent(2,0.866198);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->SetBinError(2,0.001912522);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->SetLineColor(ci);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->SetLineStyle(6);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->SetMarkerColor(ci);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->SetMarkerStyle(21);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_5_mini_charm_balancing_JUNCTIONS_over_MONASH__544->Draw("same PE");
   
   TH1D *hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545 = new TH1D("hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545","hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->SetBinContent(2,0.8553598);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->SetBinError(2,0.001910966);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->SetLineColor(ci);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->SetLineStyle(7);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->SetMarkerColor(ci);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->SetMarkerStyle(21);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_6_mini_charm_balancing_JUNCTIONS_over_MONASH__545->Draw("same PE");
   
   TH1D *hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546 = new TH1D("hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546","hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->SetBinContent(2,0.9347954);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->SetBinError(2,0.001369999);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->SetLineColor(ci);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->SetLineStyle(8);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->SetMarkerColor(ci);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->SetMarkerStyle(21);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_7_mini_charm_balancing_JUNCTIONS_over_MONASH__546->Draw("same PE");
   
   TH1D *hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547 = new TH1D("hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547","hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->SetBinContent(2,0.9150446);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->SetBinError(2,0.001788826);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->SetLineColor(ci);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->SetLineStyle(9);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->SetMarkerColor(ci);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->SetMarkerStyle(21);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_8_mini_charm_balancing_JUNCTIONS_over_MONASH__547->Draw("same PE");
   
   TH1D *hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548 = new TH1D("hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548","hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->SetBinContent(2,0.9150446);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->SetBinError(2,0.001788826);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->SetLineColor(ci);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->SetLineStyle(10);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->SetMarkerColor(ci);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->SetMarkerStyle(21);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_9_mini_charm_balancing_JUNCTIONS_over_MONASH__548->Draw("same PE");
   
   TH1D *hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549 = new TH1D("hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549","hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->SetBinContent(2,0.949427);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->SetBinError(2,0.004226546);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->SetLineColor(ci);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->SetMarkerColor(ci);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->SetMarkerStyle(21);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_1_10_mini_charm_balancing_JUNCTIONS_over_MONASH__549->Draw("same PE");
   
   TH1D *hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550 = new TH1D("hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550","hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->SetBinContent(3,1.713286);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->SetBinError(3,0.04860005);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->SetLineColor(ci);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->SetMarkerColor(ci);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->SetMarkerStyle(21);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_0_mini_charm_balancing_JUNCTIONS_over_MONASH__550->Draw("same PE");
   
   TH1D *hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551 = new TH1D("hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551","hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->SetBinContent(3,1.553983);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->SetBinError(3,0.01435966);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->SetLineColor(ci);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->SetLineStyle(2);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->SetMarkerColor(ci);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->SetMarkerStyle(21);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_1_mini_charm_balancing_JUNCTIONS_over_MONASH__551->Draw("same PE");
   
   TH1D *hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552 = new TH1D("hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552","hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->SetBinContent(3,1.368137);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->SetBinError(3,0.01384742);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->SetLineColor(ci);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->SetLineStyle(3);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->SetMarkerColor(ci);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->SetMarkerStyle(21);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_2_mini_charm_balancing_JUNCTIONS_over_MONASH__552->Draw("same PE");
   
   TH1D *hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553 = new TH1D("hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553","hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->SetBinContent(3,1.309989);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->SetBinError(3,0.00863269);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->SetLineColor(ci);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->SetLineStyle(4);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->SetMarkerColor(ci);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->SetMarkerStyle(21);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_3_mini_charm_balancing_JUNCTIONS_over_MONASH__553->Draw("same PE");
   
   TH1D *hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554 = new TH1D("hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554","hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->SetBinContent(3,1.210399);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->SetBinError(3,0.01066602);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->SetLineColor(ci);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->SetLineStyle(5);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->SetMarkerColor(ci);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->SetMarkerStyle(21);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_4_mini_charm_balancing_JUNCTIONS_over_MONASH__554->Draw("same PE");
   
   TH1D *hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555 = new TH1D("hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555","hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->SetBinContent(3,1.139944);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->SetBinError(3,0.008381124);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->SetLineColor(ci);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->SetLineStyle(6);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->SetMarkerColor(ci);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->SetMarkerStyle(21);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_5_mini_charm_balancing_JUNCTIONS_over_MONASH__555->Draw("same PE");
   
   TH1D *hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556 = new TH1D("hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556","hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->SetBinContent(3,1.071086);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->SetBinError(3,0.008116291);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->SetLineColor(ci);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->SetLineStyle(7);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->SetMarkerColor(ci);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->SetMarkerStyle(21);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_6_mini_charm_balancing_JUNCTIONS_over_MONASH__556->Draw("same PE");
   
   TH1D *hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557 = new TH1D("hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557","hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->SetBinContent(3,1.070877);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->SetBinError(3,0.006788161);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->SetLineColor(ci);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->SetLineStyle(8);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->SetMarkerColor(ci);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->SetMarkerStyle(21);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_7_mini_charm_balancing_JUNCTIONS_over_MONASH__557->Draw("same PE");
   
   TH1D *hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558 = new TH1D("hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558","hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->SetBinContent(3,1.003308);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->SetBinError(3,0.006839974);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->SetLineColor(ci);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->SetLineStyle(9);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->SetMarkerColor(ci);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->SetMarkerStyle(21);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_8_mini_charm_balancing_JUNCTIONS_over_MONASH__558->Draw("same PE");
   
   TH1D *hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559 = new TH1D("hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559","hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->SetBinContent(3,1.003308);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->SetBinError(3,0.006839974);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->SetLineColor(ci);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->SetLineStyle(10);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->SetMarkerColor(ci);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->SetMarkerStyle(21);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_9_mini_charm_balancing_JUNCTIONS_over_MONASH__559->Draw("same PE");
   
   TH1D *hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560 = new TH1D("hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560","hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH",3,0,3);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->SetBinContent(3,0.9656097);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->SetBinError(3,0.01262328);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->SetEntries(1);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->SetLineColor(ci);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->SetLineWidth(2);

   ci = TColor::GetColor("#0000cc");
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->SetMarkerColor(ci);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->SetMarkerStyle(21);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->GetXaxis()->SetLabelFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->GetXaxis()->SetTitleOffset(1);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->GetXaxis()->SetTitleFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->GetYaxis()->SetLabelFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->GetYaxis()->SetTitleFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->GetZaxis()->SetLabelFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->GetZaxis()->SetTitleOffset(1);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->GetZaxis()->SetTitleFont(42);
   hYields_CHARM_2_10_mini_charm_balancing_JUNCTIONS_over_MONASH__560->Draw("same PE");
   cMiniPad_CHARM_mini_charm_balancing_JUNCTIONS_over_MONASH__53->Modified();
   global_balancing_plots->cd();
   global_balancing_plots->Modified();
   global_balancing_plots->SetSelected(global_balancing_plots);
}
