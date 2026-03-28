// ---------------------------------------------------------------------------
// Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C
//
// For both charm and beauty, compares baryon/meson pT ratios
// for MONASH vs JUNCTIONS, using *file-level subsamples*.
//
// Expected input files when using the date-based wrappers below:
//   AnalyzedData/<date>/Beauty/bbbar_MONASH_sub0.root ...
//   AnalyzedData/<date>/Beauty/bbbar_JUNCTIONS_sub0.root ...
//   AnalyzedData/<date>/Charm/ccbar_MONASH_sub0.root ...
//   AnalyzedData/<date>/Charm/ccbar_JUNCTIONS_sub0.root ...
//
//   Beauty:
//     bbbar_MONASH_sub0.root ... bbbar_MONASH_sub(Nsub-1).root
//     bbbar_JUNCTIONS_sub0.root ... bbbar_JUNCTIONS_sub(Nsub-1).root
//
//   Charm:
//     ccbar_MONASH_sub0.root ... ccbar_MONASH_sub(Nsub-1).root
//     ccbar_JUNCTIONS_sub0.root ... ccbar_JUNCTIONS_sub(Nsub-1).root
//
// In each file we expect:
//
//   TH1D  fHistMultiplicity
//
//   Beauty:
//     TH2D  fHistPtBeautyMesons
//     TH2D  fHistPtBeautyBaryons
//
//   Charm:
//     TH2D  fHistPtCharmMesons
//     TH2D  fHistPtCharmBaryons
//
// For each of the 5 multiplicity percentile classes
//   [0–20], [20–40], [40–60], [60–80], [80–100]%
// (0–20% = highest multiplicity) it produces one plot with 4 curves:
//
//   - Beauty baryon/meson, MONASH
//   - Beauty baryon/meson, JUNCTIONS
//   - Charm  baryon/meson, MONASH
//   - Charm  baryon/meson, JUNCTIONS
//
// Uncertainties: SEM from spread across subsamples.
//
// All plots share a common y-axis max across classes.
// Optional pT rebinning of final ratio histograms.
//
// Usage:
//   .L Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C
//   runCharmBeautyRatios("12-01-2026");
//   runCharmBeautyRatios();   // if no date is given, use the latest folder in AnalyzedData
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

struct SampleHistsSimple {
    TH1* hMult   = nullptr;
    TH2* hMeson  = nullptr;
    TH2* hBaryon = nullptr;
};

} // end namespace


// ============================================================================
// MAIN FUNCTION
// ============================================================================
//
// rebinFactor: merge pT bins in the *final ratio histograms*.
//              e.g. 2 → merge 2 bins into 1, etc.
//
void Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples_WithPrefixes(
        const char* bPrefixMONASH = "bbbar_MONASH_sub",
        const char* bPrefixJUN    = "bbbar_JUNCTIONS_sub",
        const char* cPrefixMONASH = "ccbar_MONASH_sub",
        const char* cPrefixJUN    = "ccbar_JUNCTIONS_sub",
        int nSub                  = 10,
        int rebinFactor           = 2)
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

    const char* MULT_HIST      = "fHistMultiplicity";

    // Beauty hist names
    const char* B_MESON_HIST   = "fHistPtBeautyMesons";
    const char* B_BARYON_HIST  = "fHistPtBeautyBaryons";

    // Charm hist names
    const char* C_MESON_HIST   = "fHistPtCharmMesons";
    const char* C_BARYON_HIST  = "fHistPtCharmBaryons";

    // --- Load all subsamples for beauty and charm (MONASH & JUNCTIONS) ---
    std::vector<TFile*> fBM(nSub, nullptr), fBJ(nSub, nullptr);
    std::vector<TFile*> fCM(nSub, nullptr), fCJ(nSub, nullptr);

    std::vector<SampleHistsSimple> bMonash(nSub), bJun(nSub);
    std::vector<SampleHistsSimple> cMonash(nSub), cJun(nSub);

    bool okAllBM = true, okAllBJ = true;
    bool okAllCM = true, okAllCJ = true;

    for (int i = 0; i < nSub; ++i) {
        // Beauty MONASH/JUNCTIONS
        TString bNameM = Form("%s%d.root", bPrefixMONASH, i);
        TString bNameJ = Form("%s%d.root", bPrefixJUN,    i);

        fBM[i] = TFile::Open(bNameM, "READ");
        fBJ[i] = TFile::Open(bNameJ, "READ");

        if (!fBM[i] || fBM[i]->IsZombie()) {
            std::cout << "Error opening BEAUTY MONASH subsample file: " << bNameM << "\n";
            okAllBM = false;
        } else {
            bMonash[i].hMult   = GetObj<TH1>(fBM[i], MULT_HIST);
            bMonash[i].hMeson  = GetObj<TH2>(fBM[i], B_MESON_HIST);
            bMonash[i].hBaryon = GetObj<TH2>(fBM[i], B_BARYON_HIST);
            if (!(bMonash[i].hMult && bMonash[i].hMeson && bMonash[i].hBaryon)) {
                std::cout << "Missing BEAUTY MONASH histos in subsample " << i
                          << " (" << bNameM << ")\n";
                okAllBM = false;
            }
        }

        if (!fBJ[i] || fBJ[i]->IsZombie()) {
            std::cout << "Error opening BEAUTY JUNCTIONS subsample file: " << bNameJ << "\n";
            okAllBJ = false;
        } else {
            bJun[i].hMult   = GetObj<TH1>(fBJ[i], MULT_HIST);
            bJun[i].hMeson  = GetObj<TH2>(fBJ[i], B_MESON_HIST);
            bJun[i].hBaryon = GetObj<TH2>(fBJ[i], B_BARYON_HIST);
            if (!(bJun[i].hMult && bJun[i].hMeson && bJun[i].hBaryon)) {
                std::cout << "Missing BEAUTY JUNCTIONS histos in subsample " << i
                          << " (" << bNameJ << ")\n";
                okAllBJ = false;
            }
        }

        // Charm MONASH/JUNCTIONS
        TString cNameM = Form("%s%d.root", cPrefixMONASH, i);
        TString cNameJ = Form("%s%d.root", cPrefixJUN,    i);

        fCM[i] = TFile::Open(cNameM, "READ");
        fCJ[i] = TFile::Open(cNameJ, "READ");

        if (!fCM[i] || fCM[i]->IsZombie()) {
            std::cout << "Error opening CHARM MONASH subsample file: " << cNameM << "\n";
            okAllCM = false;
        } else {
            cMonash[i].hMult   = GetObj<TH1>(fCM[i], MULT_HIST);
            cMonash[i].hMeson  = GetObj<TH2>(fCM[i], C_MESON_HIST);
            cMonash[i].hBaryon = GetObj<TH2>(fCM[i], C_BARYON_HIST);
            if (!(cMonash[i].hMult && cMonash[i].hMeson && cMonash[i].hBaryon)) {
                std::cout << "Missing CHARM MONASH histos in subsample " << i
                          << " (" << cNameM << ")\n";
                okAllCM = false;
            }
        }

        if (!fCJ[i] || fCJ[i]->IsZombie()) {
            std::cout << "Error opening CHARM JUNCTIONS subsample file: " << cNameJ << "\n";
            okAllCJ = false;
        } else {
            cJun[i].hMult   = GetObj<TH1>(fCJ[i], MULT_HIST);
            cJun[i].hMeson  = GetObj<TH2>(fCJ[i], C_MESON_HIST);
            cJun[i].hBaryon = GetObj<TH2>(fCJ[i], C_BARYON_HIST);
            if (!(cJun[i].hMult && cJun[i].hMeson && cJun[i].hBaryon)) {
                std::cout << "Missing CHARM JUNCTIONS histos in subsample " << i
                          << " (" << cNameJ << ")\n";
                okAllCJ = false;
            }
        }
    }

    if (!okAllBM || !okAllBJ || !okAllCM || !okAllCJ) {
        std::cout << "Aborting due to missing files/histograms.\n";
        for (auto* f : fBM) if (f) f->Close();
        for (auto* f : fBJ) if (f) f->Close();
        for (auto* f : fCM) if (f) f->Close();
        for (auto* f : fCJ) if (f) f->Close();
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

    struct ClassRatios {
        CDef  cls;
        TH1D* bM = nullptr; // beauty MONASH
        TH1D* bJ = nullptr; // beauty JUNCTIONS
        TH1D* cM = nullptr; // charm MONASH
        TH1D* cJ = nullptr; // charm JUNCTIONS
    };

    std::vector<ClassRatios> allRatios;
    allRatios.reserve(classes.size());

    double globalMax = 0.0; // common ymax for all plots

    // --- Loop over multiplicity classes: build and combine ratios ---
    for (auto C : classes){
        std::vector<TH1D*> bM_sub, bJ_sub;
        std::vector<TH1D*> cM_sub, cJ_sub;

        // Build ratios for each subsample
        for (int i=0; i<nSub; ++i){
            // beauty percentiles
            auto yrBM = PercentileRange(bMonash[i].hMult, C.pTop, C.pBot);
            auto yrBJ = PercentileRange(bJun[i].hMult,    C.pTop, C.pBot);

            // charm percentiles
            auto yrCM = PercentileRange(cMonash[i].hMult, C.pTop, C.pBot);
            auto yrCJ = PercentileRange(cJun[i].hMult,    C.pTop, C.pBot);

            // Beauty baryon/meson
            TH1D* rBM = BuildRatioOneSub(bMonash[i].hBaryon, bMonash[i].hMeson,
                                         yrBM,
                                         Form("rBeauty_M_sub%d_%s", i, C.tag),
                                         "Baryon / Meson");
            TH1D* rBJ = BuildRatioOneSub(bJun[i].hBaryon, bJun[i].hMeson,
                                         yrBJ,
                                         Form("rBeauty_J_sub%d_%s", i, C.tag),
                                         "Baryon / Meson");

            // Charm baryon/meson
            TH1D* rCM = BuildRatioOneSub(cMonash[i].hBaryon, cMonash[i].hMeson,
                                         yrCM,
                                         Form("rCharm_M_sub%d_%s", i, C.tag),
                                         "Baryon / Meson");
            TH1D* rCJ = BuildRatioOneSub(cJun[i].hBaryon, cJun[i].hMeson,
                                         yrCJ,
                                         Form("rCharm_J_sub%d_%s", i, C.tag),
                                         "Baryon / Meson");

            if (rBM && rBJ && rCM && rCJ) {
                bM_sub.push_back(rBM);
                bJ_sub.push_back(rBJ);
                cM_sub.push_back(rCM);
                cJ_sub.push_back(rCJ);
            } else {
                std::cout << "Warning: missing ratio in subsample " << i
                          << " for class " << C.tag << "\n";
                if (rBM) delete rBM;
                if (rBJ) delete rBJ;
                if (rCM) delete rCM;
                if (rCJ) delete rCJ;
            }
        }

        if (bM_sub.empty() || bJ_sub.empty() ||
            cM_sub.empty() || cJ_sub.empty()) {
            std::cout << "Skipping class " << C.tag
                      << " due to missing subsample ratios.\n";
            for (auto* h : bM_sub) delete h;
            for (auto* h : bJ_sub) delete h;
            for (auto* h : cM_sub) delete h;
            for (auto* h : cJ_sub) delete h;
            continue;
        }

        // Combine across subsamples: mean ± SEM
        TH1D* hBM = CombineSubsampleRatios(bM_sub,
                            Form("ratioBeautyM_%s",C.tag),
                            "Baryon / Meson");
        TH1D* hBJ = CombineSubsampleRatios(bJ_sub,
                            Form("ratioBeautyJ_%s",C.tag),
                            "Baryon / Meson");
        TH1D* hCM = CombineSubsampleRatios(cM_sub,
                            Form("ratioCharmM_%s",C.tag),
                            "Baryon / Meson");
        TH1D* hCJ = CombineSubsampleRatios(cJ_sub,
                            Form("ratioCharmJ_%s",C.tag),
                            "Baryon / Meson");

        for (auto* h : bM_sub) delete h;
        for (auto* h : bJ_sub) delete h;
        for (auto* h : cM_sub) delete h;
        for (auto* h : cJ_sub) delete h;

        if (!hBM || !hBJ || !hCM || !hCJ) {
            std::cout << "Skipping class " << C.tag
                      << " due to missing combined histos.\n";
            if (hBM) delete hBM;
            if (hBJ) delete hBJ;
            if (hCM) delete hCM;
            if (hCJ) delete hCJ;
            continue;
        }

        // --- Rebin pT if requested ---
        if (rebinFactor > 1) {
            TH1D* tmp;

            tmp = (TH1D*)hBM->Rebin(rebinFactor,
                     Form("%s_reb", hBM->GetName()));
            delete hBM; hBM = tmp;

            tmp = (TH1D*)hBJ->Rebin(rebinFactor,
                     Form("%s_reb", hBJ->GetName()));
            delete hBJ; hBJ = tmp;

            tmp = (TH1D*)hCM->Rebin(rebinFactor,
                     Form("%s_reb", hCM->GetName()));
            delete hCM; hCM = tmp;

            tmp = (TH1D*)hCJ->Rebin(rebinFactor,
                     Form("%s_reb", hCJ->GetName()));
            delete hCJ; hCJ = tmp;
        }

        // Track global max
        double locMax = std::max(
            std::max(hBM->GetMaximum(), hBJ->GetMaximum()),
            std::max(hCM->GetMaximum(), hCJ->GetMaximum())
        );
        if (locMax > globalMax) globalMax = locMax;

        ClassRatios CR;
        CR.cls = C;
        CR.bM  = hBM;
        CR.bJ  = hBJ;
        CR.cM  = hCM;
        CR.cJ  = hCJ;

        allRatios.push_back(CR);
    }

    if (globalMax <= 0.0) globalMax = 1.0;
    globalMax *= 1.3; // headroom

    // --- Draw one plot per multiplicity class with 4 curves ---
    for (auto& CR : allRatios) {
        auto C = CR.cls;

        // Styling
        // Beauty MONASH: red
        CR.bM->SetLineColor(kRed+1);
        CR.bM->SetMarkerColor(kRed+1);
        CR.bM->SetMarkerStyle(20);

        // Beauty JUNCTIONS: blue
        CR.bJ->SetLineColor(kBlue+1);
        CR.bJ->SetMarkerColor(kBlue+1);
        CR.bJ->SetMarkerStyle(21);

        // Charm MONASH: magenta
        CR.cM->SetLineColor(kMagenta+1);
        CR.cM->SetMarkerColor(kMagenta+1);
        CR.cM->SetMarkerStyle(24);

        // Charm JUNCTIONS: green
        CR.cJ->SetLineColor(kGreen+2);
        CR.cJ->SetMarkerColor(kGreen+2);
        CR.cJ->SetMarkerStyle(25);

        TCanvas* c = new TCanvas(Form("c_ratio_CB_%s",C.tag),
                                 Form("Charm & Beauty Baryon/Meson %s", C.label),
                                 900,650);

        CR.bM->SetMinimum(0.0);
        CR.bM->SetMaximum(globalMax);

        CR.bM->Draw("E1");
        CR.bJ->Draw("E1 SAME");
        CR.cM->Draw("E1 SAME");
        CR.cJ->Draw("E1 SAME");

        TLegend* leg = new TLegend(0.60,0.70,0.88,0.90);
        leg->AddEntry(CR.bM,"Beauty MONASH","lep");
        leg->AddEntry(CR.bJ,"Beauty JUNCTIONS","lep");
        leg->AddEntry(CR.cM,"Charm MONASH","lep");
        leg->AddEntry(CR.cJ,"Charm JUNCTIONS","lep");
        leg->Draw();

        TString outName = Form("Ratio_BaryonMeson_CharmBeauty_MONASH_vs_JUNCTIONS_%s.png",
                               C.tag);
        c->SaveAs(PlotPathUtils::BuildPtMultiplicityPlotPath(outName.Data()));

        delete c;

        // clean histos now that they're saved
        delete CR.bM;
        delete CR.bJ;
        delete CR.cM;
        delete CR.cJ;
    }

    for (auto* f : fBM) if (f) f->Close();
    for (auto* f : fBJ) if (f) f->Close();
    for (auto* f : fCM) if (f) f->Close();
    for (auto* f : fCJ) if (f) f->Close();

    std::cout << "\nSaved:\n";
    std::cout << "  " << PlotPathUtils::GetPtMultiplicityPlotsDir()
              << "/Ratio_BaryonMeson_CharmBeauty_MONASH_vs_JUNCTIONS_*.png\n";
}

void Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples(const char* dateTag = "",
                                                                         int nSub = 10,
                                                                         int rebinFactor = 2)
{
    TString resolvedDate = PlotPathUtils::ResolveAnalysisDate(dateTag);
    if (resolvedDate.Length() == 0) return;

    TString bPrefixMONASH = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate, "Beauty", {"hf_MONASH_sub", "bbbar_MONASH_sub"});
    TString bPrefixJUN = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate, "Beauty", {"hf_JUNCTIONS_sub", "bbbar_JUNCTIONS_sub"});
    TString cPrefixMONASH = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate, "Charm", {"hf_MONASH_sub", "ccbar_MONASH_sub"});
    TString cPrefixJUN = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate, "Charm", {"hf_JUNCTIONS_sub", "ccbar_JUNCTIONS_sub"});

    std::cout << "Combined charm/beauty input date: " << resolvedDate << "\n";
    std::cout << "  Beauty MONASH    : " << bPrefixMONASH << "*.root\n";
    std::cout << "  Beauty JUNCTIONS : " << bPrefixJUN << "*.root\n";
    std::cout << "  Charm MONASH     : " << cPrefixMONASH << "*.root\n";
    std::cout << "  Charm JUNCTIONS  : " << cPrefixJUN << "*.root\n";

    Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples_WithPrefixes(
        bPrefixMONASH.Data(),
        bPrefixJUN.Data(),
        cPrefixMONASH.Data(),
        cPrefixJUN.Data(),
        nSub,
        rebinFactor
    );
}

void runBaryonMesonCharmBeauty(const char* dateTag = "", int nSub = 10, int rebinFactor = 2)
{
    Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples(dateTag, nSub, rebinFactor);
}

void runCharmBeautyRatios(const char* dateTag = "", int nSub = 10, int rebinFactor = 2)
{
    Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples(dateTag, nSub, rebinFactor);
}
