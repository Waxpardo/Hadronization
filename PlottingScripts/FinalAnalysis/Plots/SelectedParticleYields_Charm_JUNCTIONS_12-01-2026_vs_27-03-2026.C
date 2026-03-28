#ifdef __CLING__
#pragma cling optimize(0)
#endif
void SelectedParticleYields_Charm_JUNCTIONS_12-01-2026_vs_27-03-2026()
{
//=========Macro generated from canvas: cYield_Charm_JUNCTIONS/Charm JUNCTIONS yields
//=========  (Sat Mar 28 16:45:22 2026) by ROOT version 6.38.04
   TCanvas *cYield_Charm_JUNCTIONS = new TCanvas("cYield_Charm_JUNCTIONS", "Charm JUNCTIONS yields", 0, 0, 900, 700);
   gStyle->SetOptFit(0);
   gStyle->SetOptStat(0);
   gStyle->SetOptTitle(1);
   TColor::SetPalette(57, nullptr);
   cYield_Charm_JUNCTIONS->Range(0.06626506,-1.760625,3.680723,0.256288);
   cYield_Charm_JUNCTIONS->SetFillColor(0);
   cYield_Charm_JUNCTIONS->SetBorderMode(0);
   cYield_Charm_JUNCTIONS->SetBorderSize(2);
   cYield_Charm_JUNCTIONS->SetLogy();
   cYield_Charm_JUNCTIONS->SetTickx(1);
   cYield_Charm_JUNCTIONS->SetTicky(1);
   cYield_Charm_JUNCTIONS->SetLeftMargin(0.12);
   cYield_Charm_JUNCTIONS->SetRightMargin(0.05);
   cYield_Charm_JUNCTIONS->SetTopMargin(0.08);
   cYield_Charm_JUNCTIONS->SetBottomMargin(0.14);
   cYield_Charm_JUNCTIONS->SetFrameBorderMode(0);
   cYield_Charm_JUNCTIONS->SetFrameBorderMode(0);
   
   TH1D *hFrame_Charm_JUNCTIONS__4 = new TH1D("hFrame_Charm_JUNCTIONS", "", 3, 0.5, 3.5);
   hFrame_Charm_JUNCTIONS__4->SetMinimum(0.03324625200930543);
   hFrame_Charm_JUNCTIONS__4->SetMaximum(1.244328112272437);
   hFrame_Charm_JUNCTIONS__4->SetStats(0);
   hFrame_Charm_JUNCTIONS__4->SetLineColor(TColor::GetColor("#000099"));
   hFrame_Charm_JUNCTIONS__4->GetXaxis()->SetTitle("Particle species");
   hFrame_Charm_JUNCTIONS__4->GetXaxis()->SetBinLabel(1, "D^{#pm}");
   hFrame_Charm_JUNCTIONS__4->GetXaxis()->SetBinLabel(2, "D^{0}/#bar{D}^{0}");
   hFrame_Charm_JUNCTIONS__4->GetXaxis()->SetBinLabel(3, "#Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-}");
   hFrame_Charm_JUNCTIONS__4->GetXaxis()->SetBit(TAxis::kLabelsHori);
   hFrame_Charm_JUNCTIONS__4->GetXaxis()->SetLabelFont(42);
   hFrame_Charm_JUNCTIONS__4->GetXaxis()->SetLabelSize(0.04199999943375587);
   hFrame_Charm_JUNCTIONS__4->GetXaxis()->SetTitleSize(0.05000000074505806);
   hFrame_Charm_JUNCTIONS__4->GetXaxis()->SetTitleOffset(1.149999976158142);
   hFrame_Charm_JUNCTIONS__4->GetXaxis()->SetTitleFont(42);
   hFrame_Charm_JUNCTIONS__4->GetYaxis()->SetTitle("Per-event yield");
   hFrame_Charm_JUNCTIONS__4->GetYaxis()->SetLabelFont(42);
   hFrame_Charm_JUNCTIONS__4->GetYaxis()->SetLabelSize(0.04199999943375587);
   hFrame_Charm_JUNCTIONS__4->GetYaxis()->SetTitleSize(0.05000000074505806);
   hFrame_Charm_JUNCTIONS__4->GetYaxis()->SetTitleOffset(1.25);
   hFrame_Charm_JUNCTIONS__4->GetYaxis()->SetTitleFont(42);
   hFrame_Charm_JUNCTIONS__4->GetZaxis()->SetLabelFont(42);
   hFrame_Charm_JUNCTIONS__4->GetZaxis()->SetTitleOffset(1);
   hFrame_Charm_JUNCTIONS__4->GetZaxis()->SetTitleFont(42);
   hFrame_Charm_JUNCTIONS__4->Draw();
   
   std::vector<Double_t> gre_fx_vect24{ 0.92, 1.92, 2.92 };
   std::vector<Double_t> gre_fy_vect25{ 0.4816345693224507, 0.9216455907332256, 0.06649250401861086 };
   std::vector<Double_t> gre_fex_vect26{ 0, 0, 0 };
   std::vector<Double_t> gre_fey_vect27{ 6.750183445564857e-05, 7.893687598707491e-05, 2.987086497394346e-05 };
   TGraphErrors *gre = new TGraphErrors(3, gre_fx_vect24.data(), gre_fy_vect25.data(), gre_fex_vect26.data(), gre_fey_vect27.data());
   gre->SetName("gYield_12-01-2026_Charm_JUNCTIONS");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetLineColor(TColor::GetColor("#0000cc"));
   gre->SetLineWidth(2);
   gre->SetMarkerColor(TColor::GetColor("#0000cc"));
   gre->SetMarkerStyle(20);
   gre->SetMarkerSize(1.2);
   
   TH1F *Graph_histogram7 = new TH1F("Graph_histogram7", "Graph", 100, 0.72, 3.12);
   Graph_histogram7->SetMinimum(0.05981636983827322);
   Graph_histogram7->SetMaximum(1.00725071705477);
   Graph_histogram7->SetDirectory(nullptr);
   Graph_histogram7->SetStats(0);
   Graph_histogram7->SetLineColor(TColor::GetColor("#000099"));
   Graph_histogram7->GetXaxis()->SetLabelFont(42);
   Graph_histogram7->GetXaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram7->GetXaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram7->GetXaxis()->SetTitleOffset(1);
   Graph_histogram7->GetXaxis()->SetTitleFont(42);
   Graph_histogram7->GetYaxis()->SetLabelFont(42);
   Graph_histogram7->GetYaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram7->GetYaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram7->GetYaxis()->SetTitleFont(42);
   Graph_histogram7->GetZaxis()->SetLabelFont(42);
   Graph_histogram7->GetZaxis()->SetTitleOffset(1);
   Graph_histogram7->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_histogram7);
   
   gre->Draw("p l ");
   
   std::vector<Double_t> gre_fx_vect28{ 1.08, 2.08, 3.08 };
   std::vector<Double_t> gre_fy_vect29{ 0.3283758620297261, 0.6280039560141657, 0.1615043488059703 };
   std::vector<Double_t> gre_fex_vect30{ 0, 0, 0 };
   std::vector<Double_t> gre_fey_vect31{ 9.6955095816268e-05, 0.0001498497040024754, 0.0001270347905842288 };
   gre = new TGraphErrors(3, gre_fx_vect28.data(), gre_fy_vect29.data(), gre_fex_vect30.data(), gre_fey_vect31.data());
   gre->SetName("gYield_27-03-2026_Charm_JUNCTIONS");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetLineColor(TColor::GetColor("#cc0000"));
   gre->SetLineWidth(2);
   gre->SetMarkerColor(TColor::GetColor("#cc0000"));
   gre->SetMarkerStyle(21);
   gre->SetMarkerSize(1.2);
   
   TH1F *Graph_histogram8 = new TH1F("Graph_histogram8", "Graph", 100, 0.8800000000000001, 3.28);
   Graph_histogram8->SetMinimum(0.1146996648451079);
   Graph_histogram8->SetMaximum(0.6748314548884463);
   Graph_histogram8->SetDirectory(nullptr);
   Graph_histogram8->SetStats(0);
   Graph_histogram8->SetLineColor(TColor::GetColor("#000099"));
   Graph_histogram8->GetXaxis()->SetLabelFont(42);
   Graph_histogram8->GetXaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram8->GetXaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram8->GetXaxis()->SetTitleOffset(1);
   Graph_histogram8->GetXaxis()->SetTitleFont(42);
   Graph_histogram8->GetYaxis()->SetLabelFont(42);
   Graph_histogram8->GetYaxis()->SetLabelSize(0.04199999943375587);
   Graph_histogram8->GetYaxis()->SetTitleSize(0.05000000074505806);
   Graph_histogram8->GetYaxis()->SetTitleFont(42);
   Graph_histogram8->GetZaxis()->SetLabelFont(42);
   Graph_histogram8->GetZaxis()->SetTitleOffset(1);
   Graph_histogram8->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_histogram8);
   
   gre->Draw("p l ");
   
   TLegend *leg = new TLegend(0.58, 0.72, 0.88, 0.84, nullptr, "brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.032);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(0);
   TLegendEntry *legentry = leg->AddEntry("gYield_12-01-2026_Charm_JUNCTIONS","Independent Sample","lp");
   legentry->SetLineColor(TColor::GetColor("#0000cc"));
   legentry->SetLineWidth(2);
   legentry->SetMarkerColor(TColor::GetColor("#0000cc"));
   legentry->SetMarkerStyle(20);
   legentry->SetMarkerSize(1.2);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("gYield_27-03-2026_Charm_JUNCTIONS","Combined Sample","lp");
   legentry->SetLineColor(TColor::GetColor("#cc0000"));
   legentry->SetLineWidth(2);
   legentry->SetMarkerColor(TColor::GetColor("#cc0000"));
   legentry->SetMarkerSize(1.2);
   legentry->SetTextFont(42);
   leg->Draw();
   TLatex *tex = new TLatex(0.5, 0.955, "Charm JUNCTIONS Per-Event Yields");
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
   cYield_Charm_JUNCTIONS->Modified();
   cYield_Charm_JUNCTIONS->SetSelected(cYield_Charm_JUNCTIONS);
}
