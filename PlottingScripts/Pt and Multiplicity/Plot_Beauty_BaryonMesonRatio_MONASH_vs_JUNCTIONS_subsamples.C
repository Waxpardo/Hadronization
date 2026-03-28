// ---------------------------------------------------------------------------
// Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C
//
// Compares beauty baryon/meson pT spectra for MONASH vs JUNCTIONS,
// using *file-level subsamples* for uncertainty estimation.
//
// Expected input files when using the date-based wrapper below:
//   AnalyzedData/<date>/Beauty/bbbar_MONASH_sub0.root ...
//   AnalyzedData/<date>/Beauty/bbbar_JUNCTIONS_sub0.root ...
//   MONASH:    bbbar_MONASH_sub0.root ... bbbar_MONASH_sub(Nsub-1).root
//   JUNCTIONS: bbbar_JUNCTIONS_sub0.root ... bbbar_JUNCTIONS_sub(Nsub-1).root
//
// In each file we expect:
//
//   TH1D  fHistMultiplicity
//   TH2D  fHistPtBeautyMesons
//   TH2D  fHistPtBeautyBaryons
//   TH2D  fHistPtLambdab
//   TH2D  fHistPtBplus
//
// For each of the 5 multiplicity percentile classes
//   [0–20], [20–40], [40–60], [60–80], [80–100]% (0–20% = highest multiplicity)
// it produces:
//
//   1) Global beauty baryon / beauty meson ratio:
//        fHistPtBeautyBaryons / fHistPtBeautyMesons
//      → Ratio_BeautyBaryonMeson_MONASH_vs_JUNCTIONS_XX_YY.png
//
//   2) (#Lambda_b + #bar{#Lambda}_b) / B^{#pm} ratio:
//        fHistPtLambdab / fHistPtBplus
//      → Ratio_LambdabOverBpm_MONASH_vs_JUNCTIONS_XX_YY.png
//
// where XX_YY are the percentile bounds (0_20, 20_40, ..., 80_100).
//
// Uncertainties come from the spread across the N subsamples.
//
// New:
//   - All baryon/meson plots share the same y-axis range.
//   - All (#Lambda_b + #bar{#Lambda}_b)/B^{#pm} plots share the same y-axis range.
//   - Optional pT rebinning of the final ratio histograms (default: factor 2).
//
// Usage (example):
//   .L Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C
//   runBeautyRatios("12-01-2026");
//   runBeautyRatios();   // if no date is given, use the latest folder in AnalyzedData
// ---------------------------------------------------------------------------

#include <vector>
#include <string>
#include <cmath>
#include <utility>
#include <algorithm>
#include <iostream>

#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TH1D.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TStyle.h"
#include "TLine.h"
#include "TString.h"

#include "PlottingPathUtils.h"

namespace {

struct PlotPathBootstrap {
    PlotPathBootstrap() { PlotPathUtils::RegisterMacroPath(__FILE__); }
} gPlotPathBootstrap;

void SetStyle() {
    gStyle->SetOptStat(0);
    gStyle->SetPadBottomMargin(0.13);
    gStyle->SetPadLeftMargin(0.12);
    gStyle->SetPadRightMargin(0.05);
    gStyle->SetTitleSize(0.05,"XY");
    gStyle->SetLabelSize(0.045,"XY");
}

template<class T>
T* GetObj(TFile* f, const char* name) {
    return f ? dynamic_cast<T*>(f->Get(name)) : nullptr;
}

TH2* CloneTH2(TH2* h, const char* cloneName)
{
    if (!h) return nullptr;
    TH2* clone = dynamic_cast<TH2*>(h->Clone(cloneName));
    if (clone) clone->SetDirectory(nullptr);
    return clone;
}

TH2* GetChargeCombinedHist(TFile* f,
                           const std::vector<TString>& combinedNames,
                           const std::vector<TString>& splitBases,
                           const char* cloneName)
{
    if (!f) return nullptr;

    for (const TString& name : combinedNames) {
        if (TH2* h = GetObj<TH2>(f, name.Data())) return CloneTH2(h, cloneName);
    }

    for (const TString& base : splitBases) {
        TH2* hParticle = GetObj<TH2>(f, Form("%sParticle", base.Data()));
        TH2* hBar = GetObj<TH2>(f, Form("%sBar", base.Data()));
        if (!hParticle || !hBar) continue;

        TH2* combined = CloneTH2(hParticle, cloneName);
        if (!combined) continue;
        combined->Add(hBar);
        return combined;
    }

    return nullptr;
}

TH2* GetBeautyLambdaHist(TFile* f, const char* cloneName)
{
    return GetChargeCombinedHist(f, {"fHistPtLambdab"}, {"fHistPtLambdab"}, cloneName);
}

TH2* GetBeautyBHist(TFile* f, const char* cloneName)
{
    return GetChargeCombinedHist(f, {"fHistPtBplus"}, {"fHistPtBplus"}, cloneName);
}

// Find Y-bin range corresponding to percentile class (top = highest mult)
std::pair<int,int> PercentileRange(TH1* hMult, double pTop, double pBot)
{
    int nb = hMult->GetNbinsX();
    double total = hMult->Integral(1, nb);
    if (total <= 0) return {1, nb};

    double thrTop = total*(pTop/100.0);
    double thrBot = total*(pBot/100.0);

    double cum = 0.0;
    int yH = nb, yL = nb;

    // find upper edge (highest multiplicity → highest bin)
    for (int b = nb; b >= 1; --b) {
        cum += hMult->GetBinContent(b);
        if (cum >= thrTop) { yH = b; break; }
    }
    // now go down until we pass thrBot
    for (int b = yH; b >= 1; --b) {
        if (cum >= thrBot) { yL = b; break; }
        cum += hMult->GetBinContent(b-1);
    }
    if (yL > yH) std::swap(yL, yH);
    return {yL, yH};
}

// Build ratio for ONE subsample, for a given multiplicity Y-range
// num2D / den2D → hRatio(pt), no internal subsampling (errors set later).
TH1D* BuildRatioOneSub(TH2* hNum, TH2* hDen,
                       std::pair<int,int> yr,
                       const char* name,
                       const char* ytitle)
{
    if (!hNum || !hDen) return nullptr;

    TH1D* hDenFull = hDen->ProjectionX(Form("%s_D_full",name),
                                       yr.first, yr.second,"e");
    TH1D* hNumFull = hNum->ProjectionX(Form("%s_N_full",name),
                                       yr.first, yr.second,"e");

    TH1D* hR = new TH1D(name,"",
                        hDenFull->GetNbinsX(),
                        hDenFull->GetXaxis()->GetXmin(),
                        hDenFull->GetXaxis()->GetXmax());
    hR->GetYaxis()->SetTitle(ytitle);
    hR->GetXaxis()->SetTitle("p_{T} (GeV/c)");
    hR->Sumw2(); // but we will overwrite errors later

    for (int bx=1; bx<=hR->GetNbinsX(); ++bx){
        double D = hDenFull->GetBinContent(bx);
        double N = hNumFull->GetBinContent(bx);
        double R = (D > 0.0 ? N/D : 0.0);
        hR->SetBinContent(bx, R);
        hR->SetBinError(bx, 0.0); // errors from subsample spread later
    }

    delete hDenFull;
    delete hNumFull;
    return hR;
}

// Combine ratios from all subsamples: mean ± SEM across subsamples
TH1D* CombineSubsampleRatios(const std::vector<TH1D*>& rs,
                             const char* name,
                             const char* ytitle)
{
    if (rs.empty()) return nullptr;

    TH1D* ref = rs[0];
    int nbx = ref->GetNbinsX();
    double xmin = ref->GetXaxis()->GetXmin();
    double xmax = ref->GetXaxis()->GetXmax();

    TH1D* hC = new TH1D(name,"", nbx, xmin, xmax);
    hC->GetXaxis()->SetTitle(ref->GetXaxis()->GetTitle());
    hC->GetYaxis()->SetTitle(ytitle);
    hC->Sumw2();

    const int ns = (int)rs.size();

    for (int bx=1; bx<=nbx; ++bx){
        std::vector<double> vals;
        vals.reserve(ns);
        for (auto* h : rs){
            vals.push_back(h->GetBinContent(bx));
        }

        double mean = 0.0;
        for (double x : vals) mean += x;
        mean /= (vals.empty() ? 1.0 : (double)vals.size());

        double var = 0.0;
        for (double x : vals) var += (x - mean)*(x - mean);

        double sem = 0.0;
        if (vals.size() > 1) {
            sem = std::sqrt(var / (vals.size() * (vals.size() - 1)));
        }

        hC->SetBinContent(bx, mean);
        hC->SetBinError(bx, sem);
    }

    return hC;
}

struct SampleHists {
    TH1* hMult   = nullptr;
    TH2* hMeson  = nullptr;
    TH2* hBaryon = nullptr;
    TH2* hLb     = nullptr;
    TH2* hBplus  = nullptr;
};

} // end namespace


// ============================================================================
// MAIN FUNCTION
// ============================================================================
//
// rebinFactor: merge pT bins in the *final ratio histograms*.
//              e.g. 2 → merge 2 bins into 1, 5 → 5 bins into 1, etc.
//
void Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples_WithPrefixes(
        const char* prefixMONASH = "bbbar_MONASH_sub",
        const char* prefixJUN    = "bbbar_JUNCTIONS_sub",
        int nSub                 = 10,
        int rebinFactor          = 2)
{
    SetStyle();

    if (nSub <= 0) {
        std::cout << "nSub must be > 0 (got " << nSub << ")\n";
        return;
    }
    if (rebinFactor <= 0) {
        std::cout << "rebinFactor must be > 0, setting to 1.\n";
        rebinFactor = 1;
    }

    const char* MULT_HIST     = "fHistMultiplicity";
    const char* MESON_HIST    = "fHistPtBeautyMesons";
    const char* BARYON_HIST   = "fHistPtBeautyBaryons";
    // --- Load all subsamples for MONASH and JUNCTIONS ---
    std::vector<TFile*> fM(nSub, nullptr), fJ(nSub, nullptr);
    std::vector<SampleHists> monash(nSub), jun(nSub);

    bool okAllM = true, okAllJ = true;

    for (int i = 0; i < nSub; ++i) {
        TString nameM = Form("%s%d.root", prefixMONASH, i);
        TString nameJ = Form("%s%d.root", prefixJUN,    i);

        fM[i] = TFile::Open(nameM, "READ");
        fJ[i] = TFile::Open(nameJ, "READ");

        if (!fM[i] || fM[i]->IsZombie()) {
            std::cout << "Error opening MONASH subsample file: " << nameM << "\n";
            okAllM = false;
        } else {
            monash[i].hMult   = GetObj<TH1>(fM[i], MULT_HIST);
            monash[i].hMeson  = GetObj<TH2>(fM[i], MESON_HIST);
            monash[i].hBaryon = GetObj<TH2>(fM[i], BARYON_HIST);
            monash[i].hLb     = GetBeautyLambdaHist(fM[i], Form("hLbM_sub%d", i));
            monash[i].hBplus  = GetBeautyBHist(fM[i], Form("hBplusM_sub%d", i));
            if (! (monash[i].hMult && monash[i].hMeson && monash[i].hBaryon &&
                   monash[i].hLb   && monash[i].hBplus) ) {
                std::cout << "Missing MONASH histos in subsample " << i
                          << " (" << nameM << ")\n";
                okAllM = false;
            }
        }

        if (!fJ[i] || fJ[i]->IsZombie()) {
            std::cout << "Error opening JUNCTIONS subsample file: " << nameJ << "\n";
            okAllJ = false;
        } else {
            jun[i].hMult   = GetObj<TH1>(fJ[i], MULT_HIST);
            jun[i].hMeson  = GetObj<TH2>(fJ[i], MESON_HIST);
            jun[i].hBaryon = GetObj<TH2>(fJ[i], BARYON_HIST);
            jun[i].hLb     = GetBeautyLambdaHist(fJ[i], Form("hLbJ_sub%d", i));
            jun[i].hBplus  = GetBeautyBHist(fJ[i], Form("hBplusJ_sub%d", i));
            if (! (jun[i].hMult && jun[i].hMeson && jun[i].hBaryon &&
                   jun[i].hLb   && jun[i].hBplus) ) {
                std::cout << "Missing JUNCTIONS histos in subsample " << i
                          << " (" << nameJ << ")\n";
                okAllJ = false;
            }
        }
    }

    if (!okAllM || !okAllJ) {
        std::cout << "Aborting due to missing files/histograms.\n";
        for (auto& sample : monash) {
            delete sample.hLb;
            delete sample.hBplus;
        }
        for (auto& sample : jun) {
            delete sample.hLb;
            delete sample.hBplus;
        }
        for (auto* f : fM) if (f) f->Close();
        for (auto* f : fJ) if (f) f->Close();
        return;
    }

    // --- Define 5 multiplicity percentile classes ---
    struct CDef { double pTop,pBot; const char* tag; const char* label; };
    std::vector<CDef> classes = {
        {  0, 20, "0_20",   "[0-20%]"   },
        { 20, 40, "20_40",  "[20-40%]"  },
        { 40, 60, "40_60",  "[40-60%]"  },
        { 60, 80, "60_80",  "[60-80%]"  },
        { 80,100, "80_100", "[80-100%]" }
    };


    // --- Container to hold final (combined) histograms per class ---
    struct ClassRatios {
        CDef  cls;
        TH1D* rGlobM = nullptr;
        TH1D* rGlobJ = nullptr;
        TH1D* rLamM  = nullptr;
        TH1D* rLamJ  = nullptr;
    };

    std::vector<ClassRatios> allRatios;
    allRatios.reserve(classes.size());

    double globalMaxGlob = 0.0; // for all baryon/meson plots
    double globalMaxLam  = 0.0; // for all (#Lambda_b + #bar{#Lambda}_b)/B^{#pm} plots

    // --- Loop over multiplicity classes: build and combine ratios ---
    for (auto C : classes){
        std::vector<TH1D*> rGlobM_sub, rGlobJ_sub;
        std::vector<TH1D*> rLamM_sub,  rLamJ_sub;

        // Build ratios for each subsample
        for (int i=0; i<nSub; ++i){
            auto yrM = PercentileRange(monash[i].hMult, C.pTop, C.pBot);
            auto yrJ = PercentileRange(jun[i].hMult,    C.pTop, C.pBot);

            // Global beauty baryon/meson
            TH1D* rGM = BuildRatioOneSub(monash[i].hBaryon, monash[i].hMeson,
                                         yrM,
                                         Form("rGlob_M_sub%d_%s", i, C.tag),
                                         "Beauty baryon / Beauty meson");
            TH1D* rGJ = BuildRatioOneSub(jun[i].hBaryon, jun[i].hMeson,
                                         yrJ,
                                         Form("rGlob_J_sub%d_%s", i, C.tag),
                                         "Beauty baryon / Beauty meson");

            // (#Lambda_b + #bar{#Lambda}_b) / B^{#pm}
            TH1D* rLM = BuildRatioOneSub(monash[i].hLb, monash[i].hBplus,
                                         yrM,
                                         Form("rLam_M_sub%d_%s", i, C.tag),
                                         "(#Lambda_{b}^{0} + #bar{#Lambda}_{b}^{0}) / B^{#pm}");
            TH1D* rLJ = BuildRatioOneSub(jun[i].hLb, jun[i].hBplus,
                                         yrJ,
                                         Form("rLam_J_sub%d_%s", i, C.tag),
                                         "(#Lambda_{b}^{0} + #bar{#Lambda}_{b}^{0}) / B^{#pm}");

            if (rGM && rGJ && rLM && rLJ) {
                rGlobM_sub.push_back(rGM);
                rGlobJ_sub.push_back(rGJ);
                rLamM_sub.push_back(rLM);
                rLamJ_sub.push_back(rLJ);
            } else {
                std::cout << "Warning: missing ratio in subsample " << i
                          << " for class " << C.tag << "\n";
                if (rGM) delete rGM;
                if (rGJ) delete rGJ;
                if (rLM) delete rLM;
                if (rLJ) delete rLJ;
            }
        }

        if (rGlobM_sub.empty() || rGlobJ_sub.empty() ||
            rLamM_sub.empty()  || rLamJ_sub.empty()) {
            std::cout << "Skipping class " << C.tag
                      << " due to missing subsample ratios.\n";
            // clean partial
            for (auto* h : rGlobM_sub) delete h;
            for (auto* h : rGlobJ_sub) delete h;
            for (auto* h : rLamM_sub)  delete h;
            for (auto* h : rLamJ_sub)  delete h;
            continue;
        }

        // Combine across subsamples: mean ± SEM
        TH1D* rGlobM = CombineSubsampleRatios(rGlobM_sub,
                            Form("ratioGlob_MONASH_%s",C.tag),
                            "Beauty baryon / Beauty meson");
        TH1D* rGlobJ = CombineSubsampleRatios(rGlobJ_sub,
                            Form("ratioGlob_JUNCTIONS_%s",C.tag),
                            "Beauty baryon / Beauty meson");

        TH1D* rLamM  = CombineSubsampleRatios(rLamM_sub,
                            Form("ratioLamB_MONASH_%s",C.tag),
                            "(#Lambda_{b}^{0} + #bar{#Lambda}_{b}^{0}) / B^{#pm}");
        TH1D* rLamJ  = CombineSubsampleRatios(rLamJ_sub,
                            Form("ratioLamB_JUNCTIONS_%s",C.tag),
                            "(#Lambda_{b}^{0} + #bar{#Lambda}_{b}^{0}) / B^{#pm}");

        // Clean up individual subsample ratio histos
        for (auto* h : rGlobM_sub) delete h;
        for (auto* h : rGlobJ_sub) delete h;
        for (auto* h : rLamM_sub)  delete h;
        for (auto* h : rLamJ_sub)  delete h;

        if (!rGlobM || !rGlobJ || !rLamM || !rLamJ) {
            std::cout << "Skipping class " << C.tag
                      << " due to missing combined histos.\n";
            if (rGlobM) delete rGlobM;
            if (rGlobJ) delete rGlobJ;
            if (rLamM)  delete rLamM;
            if (rLamJ)  delete rLamJ;
            continue;
        }

        // --- Rebin pT if requested (merge bins) ---
        if (rebinFactor > 1) {
            TH1D* tmp;

            tmp = (TH1D*)rGlobM->Rebin(rebinFactor,
                     Form("%s_reb", rGlobM->GetName()));
            delete rGlobM;
            rGlobM = tmp;

            tmp = (TH1D*)rGlobJ->Rebin(rebinFactor,
                     Form("%s_reb", rGlobJ->GetName()));
            delete rGlobJ;
            rGlobJ = tmp;

            tmp = (TH1D*)rLamM->Rebin(rebinFactor,
                     Form("%s_reb", rLamM->GetName()));
            delete rLamM;
            rLamM = tmp;

            tmp = (TH1D*)rLamJ->Rebin(rebinFactor,
                     Form("%s_reb", rLamJ->GetName()));
            delete rLamJ;
            rLamJ = tmp;
        }

        // --- Update global y-max trackers ---
        double locMaxGlob = std::max(rGlobM->GetMaximum(), rGlobJ->GetMaximum());
        double locMaxLam  = std::max(rLamM->GetMaximum(),  rLamJ->GetMaximum());

        if (locMaxGlob > globalMaxGlob) globalMaxGlob = locMaxGlob;
        if (locMaxLam  > globalMaxLam)  globalMaxLam  = locMaxLam;

        // Store for drawing later
        ClassRatios CR;
        CR.cls   = C;
        CR.rGlobM = rGlobM;
        CR.rGlobJ = rGlobJ;
        CR.rLamM  = rLamM;
        CR.rLamJ  = rLamJ;

        allRatios.push_back(CR);
    }

    if (globalMaxGlob <= 0.0) globalMaxGlob = 1.0;
    if (globalMaxLam  <= 0.0) globalMaxLam  = 1.0;

    // Add a bit of headroom
    globalMaxGlob *= 1.3;
    globalMaxLam  *= 1.3;

    // --- Now draw everything with unified y-ranges ---
    for (auto& CR : allRatios) {
        auto C = CR.cls;

        // --- 1) Global beauty baryon/meson ratio ---
        if (CR.rGlobM && CR.rGlobJ) {
            CR.rGlobM->SetLineColor(kRed+1);
            CR.rGlobM->SetMarkerColor(kRed+1);
            CR.rGlobM->SetMarkerStyle(20);

            CR.rGlobJ->SetLineColor(kBlue+1);
            CR.rGlobJ->SetMarkerColor(kBlue+1);
            CR.rGlobJ->SetMarkerStyle(21);

            TCanvas* cGlob = new TCanvas(Form("c_ratioGlob_%s",C.tag),
                                         Form("Beauty Baryon/Meson %s", C.label),
                                         900,650);

            CR.rGlobM->SetMinimum(0.0);
            CR.rGlobM->SetMaximum(globalMaxGlob);

            CR.rGlobM->Draw("E1");
            CR.rGlobJ->Draw("E1 SAME");

            TLegend* legGlob = new TLegend(0.65,0.75,0.88,0.90);
            legGlob->AddEntry(CR.rGlobM,"MONASH","lep");
            legGlob->AddEntry(CR.rGlobJ,"JUNCTIONS","lep");
            legGlob->Draw();

            TString outGlob = Form("Ratio_BeautyBaryonMeson_MONASH_vs_JUNCTIONS_%s.png",
                                   C.tag);
            cGlob->SaveAs(PlotPathUtils::BuildPtMultiplicityPlotPath(outGlob.Data()));

            delete cGlob;
        }

        // --- 2) (#Lambda_b + #bar{#Lambda}_b) / B^{#pm} ratio ---
        if (CR.rLamM && CR.rLamJ) {
            CR.rLamM->SetLineColor(kRed+1);
            CR.rLamM->SetMarkerColor(kRed+1);
            CR.rLamM->SetMarkerStyle(20);

            CR.rLamJ->SetLineColor(kBlue+1);
            CR.rLamJ->SetMarkerColor(kBlue+1);
            CR.rLamJ->SetMarkerStyle(21);

            TCanvas* cLam = new TCanvas(Form("c_ratioLamB_%s",C.tag),
                                        Form("(#Lambda_{b}^{0} + #bar{#Lambda}_{b}^{0})/B^{#pm} vs. p_{T} %s", C.label),
                                        900,650);

            CR.rLamM->SetMinimum(0.0);
            CR.rLamM->SetMaximum(globalMaxLam);

            CR.rLamM->SetTitle(Form("(#Lambda_{b}^{0} + #bar{#Lambda}_{b}^{0})/B^{#pm} vs. p_{T} %s", C.label));

            CR.rLamM->Draw("E1");
            CR.rLamJ->Draw("E1 SAME");

            TLegend* legLam = new TLegend(0.65,0.75,0.88,0.90);
            legLam->AddEntry(CR.rLamM,"MONASH","lep");
            legLam->AddEntry(CR.rLamJ,"JUNCTIONS","lep");
            legLam->Draw();

            TString outLam = Form("Ratio_LambdabOverBpm_MONASH_vs_JUNCTIONS_%s.png",
                                  C.tag);
            cLam->SaveAs(PlotPathUtils::BuildPtMultiplicityPlotPath(outLam.Data()));

            delete cLam;
        }

        // delete combined histos after drawing
        delete CR.rGlobM;
        delete CR.rGlobJ;
        delete CR.rLamM;
        delete CR.rLamJ;
    }

    for (auto& sample : monash) {
        delete sample.hLb;
        delete sample.hBplus;
    }
    for (auto& sample : jun) {
        delete sample.hLb;
        delete sample.hBplus;
    }

    for (auto* f : fM) if (f) f->Close();
    for (auto* f : fJ) if (f) f->Close();

    std::cout << "\nSaved:\n";
    std::cout << "  " << PlotPathUtils::GetPtMultiplicityPlotsDir()
              << "/Ratio_BeautyBaryonMeson_MONASH_vs_JUNCTIONS_*.png\n";
    std::cout << "  " << PlotPathUtils::GetPtMultiplicityPlotsDir()
              << "/Ratio_LambdabOverBpm_MONASH_vs_JUNCTIONS_*.png\n";
}

void Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples(const char* dateTag = "",
                                                                    int nSub = 10,
                                                                    int rebinFactor = 2)
{
    TString resolvedDate = PlotPathUtils::ResolveAnalysisDate(dateTag);
    if (resolvedDate.Length() == 0) return;

    TString prefixMONASH = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate, "Beauty", {"hf_MONASH_sub", "bbbar_MONASH_sub"});
    TString prefixJUN = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate, "Beauty", {"hf_JUNCTIONS_sub", "bbbar_JUNCTIONS_sub"});

    std::cout << "Beauty input date: " << resolvedDate << "\n";
    std::cout << "  MONASH    : " << prefixMONASH << "*.root\n";
    std::cout << "  JUNCTIONS : " << prefixJUN << "*.root\n";

    Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples_WithPrefixes(
        prefixMONASH.Data(),
        prefixJUN.Data(),
        nSub,
        rebinFactor
    );
}

// Convenience wrapper: same behavior as the main function name, but shorter to type interactively.
void runBeautyRatios(const char* dateTag = "", int nSub = 10, int rebinFactor = 2)
{
    Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples(dateTag, nSub, rebinFactor);
}
