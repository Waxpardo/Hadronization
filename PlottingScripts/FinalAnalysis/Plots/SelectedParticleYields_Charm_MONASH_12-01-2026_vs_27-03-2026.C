#ifdef __CLING__
#pragma cling optimize(0)
#endif
void SelectedParticleYields_Charm_MONASH_12-01-2026_vs_27-03-2026()
{
//=========Macro generated from canvas: cYield_Charm_MONASH/Charm MONASH yields
//=========  (Sat Mar 28 16:45:22 2026) by ROOT version 6.38.04
   TCanvas *cYield_Charm_MONASH = new TCanvas("cYield_Charm_MONASH", "Charm MONASH yields", 0, 0, 900, 700);
   gStyle->SetOptFit(0);
   gStyle->SetOptStat(0);
   gStyle->SetOptTitle(1);
   TColor::SetPalette(57, nullptr);
   cYield_Charm_MONASH->Range(0.06626506,-1.955641,3.680723,0.3018981);
   cYield_Charm_MONASH->SetFillColor(0);
   cYield_Charm_MONASH->SetBorderMode(0);
   cYield_Charm_MONASH->SetBorderSize(2);
   cYield_Charm_MONASH->SetLogy();
   cYield_Charm_MONASH->SetTickx(1);
   cYield_Charm_MONASH->SetTicky(1);
   cYield_Charm_MONASH->SetLeftMargin(0.12);
   cYield_Charm_MONASH->SetRightMargin(0.05);
   cYield_Charm_MONASH->SetTopMargin(0.08);
   cYield_Charm_MONASH->SetBottomMargin(0.14);
   cYield_Charm_MONASH->SetFrameBorderMode(0);
   cYield_Charm_MONASH->SetFrameBorderMode(0);
   
   TH1D *hFrame_Charm_MONASH__3 = new TH1D("hFrame_Charm_MONASH", "", 3, 0.5, 3.5);
   hFrame_Charm_MONASH__3->SetMinimum(0.02293056729990792);
   hFrame_Charm_MONASH__3->SetMaximum(1.322193602408611);
   hFrame_Charm_MONASH__3->SetStats(0);
   hFrame_Charm_MONASH__3->SetLineColor(TColor::GetColor("#000099"));
   hFrame_Charm_MONASH__3->GetXaxis()->SetTitle("Particle species");
   hFrame_Charm_MONASH__3->GetXaxis()->SetBinLabel(1, "D^{#pm}");
   hFrame_Charm_MONASH__3->GetXaxis()->SetBinLabel(2, "D^{0}/#bar{D}^{0}");
   hFrame_Charm_MONASH__3->GetXaxis()->SetBinLabel(3, "#Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-}");
   hFrame_Charm_MONASH__3->GetXaxis()->SetBit(TAxis::kLabelsHori);
   hFrame_Charm_MONASH__3->GetXaxis()->SetLabelFont(42);
   hFrame_Charm_MONASH__3->GetXaxis()->SetLabelSize(0.04199999943375587);
   hFrame_Charm_MONASH__3->GetXaxis()->SetTitleSize(0.05000000074505806);
   hFrame_Charm_MONASH__3->GetXaxis()->SetTitleOffset(1.149999976158142);
   hFrame_Charm_MONASH__3->GetXaxis()->SetTitleFont(42);
   hFrame_Charm_MONASH__3->GetYaxis()->SetTitle("Per-event yield");
   hFrame_Charm_MONASH__3->GetYaxis()->SetLabelFont(42);
   hFrame_Charm_MONASH__3->GetYaxis()->SetLabelSize(0.04199999943375587);
   hFrame_Charm_MONASH__3->GetYaxis()->SetTitleSize(0.05000000074505806);
   hFrame_Charm_MONASH__3->GetYaxis()->SetTitleOffset(1.25);
   hFrame_Charm_MONASH__3->GetYaxis()->SetTitleFont(42);
   hFrame_Charm_MONASH__3->GetZaxis()->SetLabelFont(42);
   hFrame_Charm_MONASH__3->GetZaxis()->SetTitleOffset(1);
   hFrame_Charm_MONASH__3->GetZaxis()->SetTitleFont(42);
   hFrame_Charm_MONASH__3->Draw();
   
   std::vector<Double_t> gre_fx_vect16{ 0.92, 1.92, 2.92 };
   std::vector<Double_t> gre_fy_vect17{ 0.5098757542796919, 0.9793409104321523, 0.05516538400080739 };
   std::vector<Double_t> gre_fex_vect18{ 0, 0, 0 };
   std::vector<Double_t> gre_fey_vect19{ 7.446779703447869e-05, 6.175801867087476e-05, 2.959952245973399e-05 };
   TGraphErrors *gre = new TGraphErrors(3, gre_fx_vect16.data(), gre_fy_vect17.data(), gre_fex_vect18.data(), gre_fey_vect19.data());
   gre->SetName("gYield_12-01-2026_Charm_MONASH");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetLineColor(TColor::GetColor("#0000cc"));
   gre->SetLineWidth(2);
   gre->SetMarkerColor(TColor::GetColor("#0000cc"));
   gre->SetMarkerStyle(20);
   gre->SetMarkerSize(1.2);
   
   TH1F *Graph_histogram5 = new TH1F("Graph_histogram5", "Graph", 100, 0.72, 3.12);
   Graph_histogram5->SetMinimum(0.04962220603051289);
   Graph_histogram5->SetMaximum(1.071829356848071);
   Graph_histogram5->SetDirectory(nullptr);
   Graph_histogram5->SetStats(0);
   Graph_histogram5->SetLineColor(TColor::GetColor("#000099"));
   Graph_histogram5->GetXaxis()->SetLabelFont(42);
   Graph_histogram5->GetXaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram5->GetXaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram5->GetXaxis()->SetTitleOffset(1);
   Graph_histogram5->GetXaxis()->SetTitleFont(42);
   Graph_histogram5->GetYaxis()->SetLabelFont(42);
   Graph_histogram5->GetYaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram5->GetYaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram5->GetYaxis()->SetTitleFont(42);
   Graph_histogram5->GetZaxis()->SetLabelFont(42);
   Graph_histogram5->GetZaxis()->SetTitleOffset(1);
   Graph_histogram5->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_histogram5);
   
   gre->Draw("p l ");
   
   std::vector<Double_t> gre_fx_vect20{ 1.08, 2.08, 3.08 };
   std::vector<Double_t> gre_fy_vect21{ 0.3687138256717025, 0.7080003617682946, 0.04586113459981583 };
   std::vector<Double_t> gre_fex_vect22{ 0, 0, 0 };
   std::vector<Double_t> gre_fey_vect23{ 0.0001978796487774072, 0.000206395399750901, 8.765925894593545e-05 };
   gre = new TGraphErrors(3, gre_fx_vect20.data(), gre_fy_vect21.data(), gre_fex_vect22.data(), gre_fey_vect23.data());
   gre->SetName("gYield_27-03-2026_Charm_MONASH");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetLineColor(TColor::GetColor("#cc0000"));
   gre->SetLineWidth(2);
   gre->SetMarkerColor(TColor::GetColor("#cc0000"));
   gre->SetMarkerStyle(21);
   gre->SetMarkerSize(1.2);
   
   TH1F *Graph_histogram6 = new TH1F("Graph_histogram6", "Graph", 100, 0.8800000000000001, 3.28);
   Graph_histogram6->SetMinimum(0.04119612780678291);
   Graph_histogram6->SetMaximum(0.7744500853507631);
   Graph_histogram6->SetDirectory(nullptr);
   Graph_histogram6->SetStats(0);
   Graph_histogram6->SetLineColor(TColor::GetColor("#000099"));
   Graph_histogram6->GetXaxis()->SetLabelFont(42);
   Graph_histogram6->GetXaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram6->GetXaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram6->GetXaxis()->SetTitleOffset(1);
   Graph_histogram6->GetXaxis()->SetTitleFont(42);
   Graph_histogram6->GetYaxis()->SetLabelFont(42);
   Graph_histogram6->GetYaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram6->GetYaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram6->GetYaxis()->SetTitleFont(42);
   Graph_histogram6->GetZaxis()->SetLabelFont(42);
   Graph_histogram6->GetZaxis()->SetTitleOffset(1);
   Graph_histogram6->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_histogram6);
   
   gre->Draw("p l ");
   
   TLegend *leg = new TLegend(0.58, 0.72, 0.88, 0.84, nullptr, "brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.032);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(0);
   TLegendEntry *legentry = leg->AddEntry("gYield_12-01-2026_Charm_MONASH","Independent Sample","lp");
   legentry->SetLineColor(TColor::GetColor("#0000cc"));
   legentry->SetLineWidth(2);
   legentry->SetMarkerColor(TColor::GetColor("#0000cc"));
   legentry->SetMarkerStyle(20);
   legentry->SetMarkerSize(1.2);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("gYield_27-03-2026_Charm_MONASH","Combined Sample","lp");
   legentry->SetLineColor(TColor::GetColor("#cc0000"));
   legentry->SetLineWidth(2);
   legentry->SetMarkerColor(TColor::GetColor("#cc0000"));
   legentry->SetMarkerSize(1.2);
   legentry->SetTextFont(42);
   leg->Draw();
   TLatex *tex = new TLatex(0.5, 0.955, "Charm MONASH Per-Event Yields");
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
   cYield_Charm_MONASH->Modified();
   cYield_Charm_MONASH->SetSelected(cYield_Charm_MONASH);
}
