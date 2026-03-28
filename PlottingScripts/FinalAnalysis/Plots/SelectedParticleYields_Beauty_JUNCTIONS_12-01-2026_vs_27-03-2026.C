#ifdef __CLING__
#pragma cling optimize(0)
#endif
void SelectedParticleYields_Beauty_JUNCTIONS_12-01-2026_vs_27-03-2026()
{
//=========Macro generated from canvas: cYield_Beauty_JUNCTIONS/Beauty JUNCTIONS yields
//=========  (Sat Mar 28 16:45:22 2026) by ROOT version 6.38.04
   TCanvas *cYield_Beauty_JUNCTIONS = new TCanvas("cYield_Beauty_JUNCTIONS", "Beauty JUNCTIONS yields", 0, 0, 900, 700);
   gStyle->SetOptFit(0);
   gStyle->SetOptStat(0);
   gStyle->SetOptTitle(1);
   TColor::SetPalette(57, nullptr);
   cYield_Beauty_JUNCTIONS->Range(0.06626506,-2.686585,3.680723,0.0836424);
   cYield_Beauty_JUNCTIONS->SetFillColor(0);
   cYield_Beauty_JUNCTIONS->SetBorderMode(0);
   cYield_Beauty_JUNCTIONS->SetBorderSize(2);
   cYield_Beauty_JUNCTIONS->SetLogy();
   cYield_Beauty_JUNCTIONS->SetTickx(1);
   cYield_Beauty_JUNCTIONS->SetTicky(1);
   cYield_Beauty_JUNCTIONS->SetLeftMargin(0.12);
   cYield_Beauty_JUNCTIONS->SetRightMargin(0.05);
   cYield_Beauty_JUNCTIONS->SetTopMargin(0.08);
   cYield_Beauty_JUNCTIONS->SetBottomMargin(0.14);
   cYield_Beauty_JUNCTIONS->SetFrameBorderMode(0);
   cYield_Beauty_JUNCTIONS->SetFrameBorderMode(0);
   
   TH1D *hFrame_Beauty_JUNCTIONS__2 = new TH1D("hFrame_Beauty_JUNCTIONS", "", 3, 0.5, 3.5);
   hFrame_Beauty_JUNCTIONS__2->SetMinimum(0.005026284977025128);
   hFrame_Beauty_JUNCTIONS__2->SetMaximum(0.7278204407638184);
   hFrame_Beauty_JUNCTIONS__2->SetStats(0);
   hFrame_Beauty_JUNCTIONS__2->SetLineColor(TColor::GetColor("#000099"));
   hFrame_Beauty_JUNCTIONS__2->GetXaxis()->SetTitle("Particle species");
   hFrame_Beauty_JUNCTIONS__2->GetXaxis()->SetBinLabel(1, "B^{#pm}");
   hFrame_Beauty_JUNCTIONS__2->GetXaxis()->SetBinLabel(2, "B^{0}/#bar{B}^{0}");
   hFrame_Beauty_JUNCTIONS__2->GetXaxis()->SetBinLabel(3, "#Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0}");
   hFrame_Beauty_JUNCTIONS__2->GetXaxis()->SetBit(TAxis::kLabelsHori);
   hFrame_Beauty_JUNCTIONS__2->GetXaxis()->SetLabelFont(42);
   hFrame_Beauty_JUNCTIONS__2->GetXaxis()->SetLabelSize(0.04199999943375587);
   hFrame_Beauty_JUNCTIONS__2->GetXaxis()->SetTitleSize(0.05000000074505806);
   hFrame_Beauty_JUNCTIONS__2->GetXaxis()->SetTitleOffset(1.149999976158142);
   hFrame_Beauty_JUNCTIONS__2->GetXaxis()->SetTitleFont(42);
   hFrame_Beauty_JUNCTIONS__2->GetYaxis()->SetTitle("Per-event yield");
   hFrame_Beauty_JUNCTIONS__2->GetYaxis()->SetLabelFont(42);
   hFrame_Beauty_JUNCTIONS__2->GetYaxis()->SetLabelSize(0.04199999943375587);
   hFrame_Beauty_JUNCTIONS__2->GetYaxis()->SetTitleSize(0.05000000074505806);
   hFrame_Beauty_JUNCTIONS__2->GetYaxis()->SetTitleOffset(1.25);
   hFrame_Beauty_JUNCTIONS__2->GetYaxis()->SetTitleFont(42);
   hFrame_Beauty_JUNCTIONS__2->GetZaxis()->SetLabelFont(42);
   hFrame_Beauty_JUNCTIONS__2->GetZaxis()->SetTitleOffset(1);
   hFrame_Beauty_JUNCTIONS__2->GetZaxis()->SetTitleFont(42);
   hFrame_Beauty_JUNCTIONS__2->Draw();
   
   std::vector<Double_t> gre_fx_vect8{ 0.92, 1.92, 2.92 };
   std::vector<Double_t> gre_fy_vect9{ 0.5390615560715595, 0.5389593706886884, 0.13370197498216 };
   std::vector<Double_t> gre_fex_vect10{ 0, 0, 0 };
   std::vector<Double_t> gre_fey_vect11{ 6.469634608378216e-05, 8.762380657035366e-05, 2.895431738549326e-05 };
   TGraphErrors *gre = new TGraphErrors(3, gre_fx_vect8.data(), gre_fy_vect9.data(), gre_fex_vect10.data(), gre_fey_vect11.data());
   gre->SetName("gYield_12-01-2026_Beauty_JUNCTIONS");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetLineColor(TColor::GetColor("#0000cc"));
   gre->SetLineWidth(2);
   gre->SetMarkerColor(TColor::GetColor("#0000cc"));
   gre->SetMarkerStyle(20);
   gre->SetMarkerSize(1.2);
   
   TH1F *Graph_histogram3 = new TH1F("Graph_histogram3", "Graph", 100, 0.72, 3.12);
   Graph_histogram3->SetMinimum(0.09312769748948768);
   Graph_histogram3->SetMaximum(0.5796715755929301);
   Graph_histogram3->SetDirectory(nullptr);
   Graph_histogram3->SetStats(0);
   Graph_histogram3->SetLineColor(TColor::GetColor("#000099"));
   Graph_histogram3->GetXaxis()->SetLabelFont(42);
   Graph_histogram3->GetXaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram3->GetXaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram3->GetXaxis()->SetTitleOffset(1);
   Graph_histogram3->GetXaxis()->SetTitleFont(42);
   Graph_histogram3->GetYaxis()->SetLabelFont(42);
   Graph_histogram3->GetYaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram3->GetYaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram3->GetYaxis()->SetTitleFont(42);
   Graph_histogram3->GetZaxis()->SetLabelFont(42);
   Graph_histogram3->GetZaxis()->SetTitleOffset(1);
   Graph_histogram3->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_histogram3);
   
   gre->Draw("p l ");
   
   std::vector<Double_t> gre_fx_vect12{ 1.08, 2.08, 3.08 };
   std::vector<Double_t> gre_fy_vect13{ 0.04051591322911318, 0.04046374910789786, 0.01005256995405026 };
   std::vector<Double_t> gre_fex_vect14{ 0, 0, 0 };
   std::vector<Double_t> gre_fey_vect15{ 9.763306283783074e-05, 8.092376082274915e-05, 3.044109615761229e-05 };
   gre = new TGraphErrors(3, gre_fx_vect12.data(), gre_fy_vect13.data(), gre_fex_vect14.data(), gre_fey_vect15.data());
   gre->SetName("gYield_27-03-2026_Beauty_JUNCTIONS");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetLineColor(TColor::GetColor("#cc0000"));
   gre->SetLineWidth(2);
   gre->SetMarkerColor(TColor::GetColor("#cc0000"));
   gre->SetMarkerStyle(21);
   gre->SetMarkerSize(1.2);
   
   TH1F *Graph_histogram4 = new TH1F("Graph_histogram4", "Graph", 100, 0.8800000000000001, 3.28);
   Graph_histogram4->SetMinimum(0.006962987114486808);
   Graph_histogram4->SetMaximum(0.04367268803535685);
   Graph_histogram4->SetDirectory(nullptr);
   Graph_histogram4->SetStats(0);
   Graph_histogram4->SetLineColor(TColor::GetColor("#000099"));
   Graph_histogram4->GetXaxis()->SetLabelFont(42);
   Graph_histogram4->GetXaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram4->GetXaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram4->GetXaxis()->SetTitleOffset(1);
   Graph_histogram4->GetXaxis()->SetTitleFont(42);
   Graph_histogram4->GetYaxis()->SetLabelFont(42);
   Graph_histogram4->GetYaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram4->GetYaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram4->GetYaxis()->SetTitleFont(42);
   Graph_histogram4->GetZaxis()->SetLabelFont(42);
   Graph_histogram4->GetZaxis()->SetTitleOffset(1);
   Graph_histogram4->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_histogram4);
   
   gre->Draw("p l ");
   
   TLegend *leg = new TLegend(0.58, 0.72, 0.88, 0.84, nullptr, "brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.032);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(0);
   TLegendEntry *legentry = leg->AddEntry("gYield_12-01-2026_Beauty_JUNCTIONS","Independent Sample","lp");
   legentry->SetLineColor(TColor::GetColor("#0000cc"));
   legentry->SetLineWidth(2);
   legentry->SetMarkerColor(TColor::GetColor("#0000cc"));
   legentry->SetMarkerStyle(20);
   legentry->SetMarkerSize(1.2);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("gYield_27-03-2026_Beauty_JUNCTIONS","Combined Sample","lp");
   legentry->SetLineColor(TColor::GetColor("#cc0000"));
   legentry->SetLineWidth(2);
   legentry->SetMarkerColor(TColor::GetColor("#cc0000"));
   legentry->SetMarkerSize(1.2);
   legentry->SetTextFont(42);
   leg->Draw();
   TLatex *tex = new TLatex(0.5, 0.955, "Beauty JUNCTIONS Per-Event Yields");
   tex->SetTextAlign(22);
   tex->SetTextSize(0.045);
   tex->SetLineWidth(2);
   tex->SetNDC();
   tex->Draw();
   tex = new TLatex(0.5, 0.905, "Charge-conjugate-combined species from analyzed histograms");
   tex->SetTextAlign(22);
   tex->SetTextSize(0.027);
   tex->SetLineWidth(2);
   tex->SetNDC();
   tex->Draw();
   cYield_Beauty_JUNCTIONS->Modified();
   cYield_Beauty_JUNCTIONS->SetSelected(cYield_Beauty_JUNCTIONS);
}
