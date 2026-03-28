#ifdef __CLING__
#pragma cling optimize(0)
#endif
void SelectedParticleYields_Beauty_MONASH_12-01-2026_vs_27-03-2026()
{
//=========Macro generated from canvas: cYield_Beauty_MONASH/Beauty MONASH yields
//=========  (Sat Mar 28 16:45:22 2026) by ROOT version 6.38.04
   TCanvas *cYield_Beauty_MONASH = new TCanvas("cYield_Beauty_MONASH", "Beauty MONASH yields", 0, 0, 900, 700);
   gStyle->SetOptFit(0);
   gStyle->SetOptStat(0);
   gStyle->SetOptTitle(1);
   TColor::SetPalette(57, nullptr);
   cYield_Beauty_MONASH->Range(0.06626506,-3.146627,3.680723,0.2840606);
   cYield_Beauty_MONASH->SetFillColor(0);
   cYield_Beauty_MONASH->SetBorderMode(0);
   cYield_Beauty_MONASH->SetBorderSize(2);
   cYield_Beauty_MONASH->SetLogy();
   cYield_Beauty_MONASH->SetTickx(1);
   cYield_Beauty_MONASH->SetTicky(1);
   cYield_Beauty_MONASH->SetLeftMargin(0.12);
   cYield_Beauty_MONASH->SetRightMargin(0.05);
   cYield_Beauty_MONASH->SetTopMargin(0.08);
   cYield_Beauty_MONASH->SetBottomMargin(0.14);
   cYield_Beauty_MONASH->SetFrameBorderMode(0);
   cYield_Beauty_MONASH->SetFrameBorderMode(0);
   
   TH1D *hFrame_Beauty_MONASH__1 = new TH1D("hFrame_Beauty_MONASH", "", 3, 0.5, 3.5);
   hFrame_Beauty_MONASH__1->SetMinimum(0.002156103019124497);
   hFrame_Beauty_MONASH__1->SetMaximum(1.022364203710653);
   hFrame_Beauty_MONASH__1->SetStats(0);
   hFrame_Beauty_MONASH__1->SetLineColor(TColor::GetColor("#000099"));
   hFrame_Beauty_MONASH__1->GetXaxis()->SetTitle("Particle species");
   hFrame_Beauty_MONASH__1->GetXaxis()->SetBinLabel(1, "B^{#pm}");
   hFrame_Beauty_MONASH__1->GetXaxis()->SetBinLabel(2, "B^{0}/#bar{B}^{0}");
   hFrame_Beauty_MONASH__1->GetXaxis()->SetBinLabel(3, "#Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0}");
   hFrame_Beauty_MONASH__1->GetXaxis()->SetBit(TAxis::kLabelsHori);
   hFrame_Beauty_MONASH__1->GetXaxis()->SetLabelFont(42);
   hFrame_Beauty_MONASH__1->GetXaxis()->SetLabelSize(0.04199999943375587);
   hFrame_Beauty_MONASH__1->GetXaxis()->SetTitleSize(0.05000000074505806);
   hFrame_Beauty_MONASH__1->GetXaxis()->SetTitleOffset(1.149999976158142);
   hFrame_Beauty_MONASH__1->GetXaxis()->SetTitleFont(42);
   hFrame_Beauty_MONASH__1->GetYaxis()->SetTitle("Per-event yield");
   hFrame_Beauty_MONASH__1->GetYaxis()->SetLabelFont(42);
   hFrame_Beauty_MONASH__1->GetYaxis()->SetLabelSize(0.04199999943375587);
   hFrame_Beauty_MONASH__1->GetYaxis()->SetTitleSize(0.05000000074505806);
   hFrame_Beauty_MONASH__1->GetYaxis()->SetTitleOffset(1.25);
   hFrame_Beauty_MONASH__1->GetYaxis()->SetTitleFont(42);
   hFrame_Beauty_MONASH__1->GetZaxis()->SetLabelFont(42);
   hFrame_Beauty_MONASH__1->GetZaxis()->SetTitleOffset(1);
   hFrame_Beauty_MONASH__1->GetZaxis()->SetTitleFont(42);
   hFrame_Beauty_MONASH__1->Draw();
   
   std::vector<Double_t> gre_fx_vect0{ 0.92, 1.92, 2.92 };
   std::vector<Double_t> gre_fy_vect1{ 0.7572666267197088, 0.7570804178051493, 0.05760374039311809 };
   std::vector<Double_t> gre_fex_vect2{ 0, 0, 0 };
   std::vector<Double_t> gre_fey_vect3{ 4.019084373777505e-05, 6.738197052608122e-05, 1.500122441037448e-05 };
   TGraphErrors *gre = new TGraphErrors(3, gre_fx_vect0.data(), gre_fy_vect1.data(), gre_fex_vect2.data(), gre_fey_vect3.data());
   gre->SetName("gYield_12-01-2026_Beauty_MONASH");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetLineColor(TColor::GetColor("#0000cc"));
   gre->SetLineWidth(2);
   gre->SetMarkerColor(TColor::GetColor("#0000cc"));
   gre->SetMarkerStyle(20);
   gre->SetMarkerSize(1.2);
   
   TH1F *Graph_histogram1 = new TH1F("Graph_histogram1", "Graph", 100, 0.72, 3.12);
   Graph_histogram1->SetMinimum(0.05182986525183695);
   Graph_histogram1->SetMaximum(0.8272786254029204);
   Graph_histogram1->SetDirectory(nullptr);
   Graph_histogram1->SetStats(0);
   Graph_histogram1->SetLineColor(TColor::GetColor("#000099"));
   Graph_histogram1->GetXaxis()->SetLabelFont(42);
   Graph_histogram1->GetXaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram1->GetXaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram1->GetXaxis()->SetTitleOffset(1);
   Graph_histogram1->GetXaxis()->SetTitleFont(42);
   Graph_histogram1->GetYaxis()->SetLabelFont(42);
   Graph_histogram1->GetYaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram1->GetYaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram1->GetYaxis()->SetTitleFont(42);
   Graph_histogram1->GetZaxis()->SetLabelFont(42);
   Graph_histogram1->GetZaxis()->SetTitleOffset(1);
   Graph_histogram1->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_histogram1);
   
   gre->Draw("p l ");
   
   std::vector<Double_t> gre_fx_vect4{ 1.08, 2.08, 3.08 };
   std::vector<Double_t> gre_fy_vect5{ 0.05680382513945487, 0.05685344822411386, 0.004312206038248993 };
   std::vector<Double_t> gre_fex_vect6{ 0, 0, 0 };
   std::vector<Double_t> gre_fey_vect7{ 8.129101685770121e-05, 0.0001004727607599095, 2.055636834844895e-05 };
   gre = new TGraphErrors(3, gre_fx_vect4.data(), gre_fy_vect5.data(), gre_fex_vect6.data(), gre_fey_vect7.data());
   gre->SetName("gYield_27-03-2026_Beauty_MONASH");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetLineColor(TColor::GetColor("#cc0000"));
   gre->SetLineWidth(2);
   gre->SetMarkerColor(TColor::GetColor("#cc0000"));
   gre->SetMarkerStyle(21);
   gre->SetMarkerSize(1.2);
   
   TH1F *Graph_histogram2 = new TH1F("Graph_histogram2", "Graph", 100, 0.8800000000000001, 3.28);
   Graph_histogram2->SetMinimum(0.00386248470291049);
   Graph_histogram2->SetMaximum(0.0622201481163711);
   Graph_histogram2->SetDirectory(nullptr);
   Graph_histogram2->SetStats(0);
   Graph_histogram2->SetLineColor(TColor::GetColor("#000099"));
   Graph_histogram2->GetXaxis()->SetLabelFont(42);
   Graph_histogram2->GetXaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram2->GetXaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram2->GetXaxis()->SetTitleOffset(1);
   Graph_histogram2->GetXaxis()->SetTitleFont(42);
   Graph_histogram2->GetYaxis()->SetLabelFont(42);
   Graph_histogram2->GetYaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram2->GetYaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram2->GetYaxis()->SetTitleFont(42);
   Graph_histogram2->GetZaxis()->SetLabelFont(42);
   Graph_histogram2->GetZaxis()->SetTitleOffset(1);
   Graph_histogram2->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_histogram2);
   
   gre->Draw("p l ");
   
   TLegend *leg = new TLegend(0.58, 0.72, 0.88, 0.84, nullptr, "brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.032);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(0);
   TLegendEntry *legentry = leg->AddEntry("gYield_12-01-2026_Beauty_MONASH","Independent Sample","lp");
   legentry->SetLineColor(TColor::GetColor("#0000cc"));
   legentry->SetLineWidth(2);
   legentry->SetMarkerColor(TColor::GetColor("#0000cc"));
   legentry->SetMarkerStyle(20);
   legentry->SetMarkerSize(1.2);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("gYield_27-03-2026_Beauty_MONASH","Combined Sample","lp");
   legentry->SetLineColor(TColor::GetColor("#cc0000"));
   legentry->SetLineWidth(2);
   legentry->SetMarkerColor(TColor::GetColor("#cc0000"));
   legentry->SetMarkerSize(1.2);
   legentry->SetTextFont(42);
   leg->Draw();
   TLatex *tex = new TLatex(0.5, 0.955, "Beauty MONASH Per-Event Yields");
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
   cYield_Beauty_MONASH->Modified();
   cYield_Beauty_MONASH->SetSelected(cYield_Beauty_MONASH);
}
