// ---------------------------------------------------------------------------
// Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C
//
// Plots pT spectra vs multiplicity percentile for:
//   Charm:  (#Lambda_c + #bar{#Lambda}_c) and D^{#pm}
//   Beauty: (#Lambda_b + #bar{#Lambda}_b) and B^{#pm}
//
// For each tune (MONASH and JUNCTIONS) separately, you get ONE plot per species,
// each plot containing 5 multiplicity classes as colored line curves:
//
//   [0-20], [20-40], [40-60], [60-80], [80-100]%   (0-20% = highest multiplicity)
//
// The spectra are built using file-level subsamples:
//   - For each subsample and mult class: TH2 -> ProjectionX in mult Y-range
//   - Normalize each projected spectrum to unit integral
//   - Combine the subsample spectra bin-by-bin with mean ± SEM
//
// X-axis is auto-cropped to the last pT bin that has content in ANY class curve,
// with a small margin, to avoid white space to the right.
//
// Expected files when using the date-based wrapper below:
//   AnalyzedData/<date>/Charm/ccbar_MONASH_sub0.root ...
//   AnalyzedData/<date>/Charm/ccbar_JUNCTIONS_sub0.root ...
//   AnalyzedData/<date>/Beauty/bbbar_MONASH_sub0.root ...
//   AnalyzedData/<date>/Beauty/bbbar_JUNCTIONS_sub0.root ...
//   Charm:
//     ccbar_MONASH_sub0.root ... ccbar_MONASH_sub(Nsub-1).root
//     ccbar_JUNCTIONS_sub0.root ... ccbar_JUNCTIONS_sub(Nsub-1).root
//
//   Beauty:
//     bbbar_MONASH_sub0.root ... bbbar_MONASH_sub(Nsub-1).root
//     bbbar_JUNCTIONS_sub0.root ... bbbar_JUNCTIONS_sub(Nsub-1).root
//
// Expected histograms in charm files:
//   TH1D fHistMultiplicity
//   TH2D fHistPtLambdac
//   TH2D fHistPtDplus
//
// Expected histograms in beauty files:
//   TH1D fHistMultiplicity
//   TH2D fHistPtLambdab
//   TH2D fHistPtBplus
//
// Usage:
//   .L Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C
//   runHFSpectra("12-01-2026");
//   runHFSpectra();   // if no date is given, use the latest folder in AnalyzedData
//
// Or customize paths/prefixes explicitly:
//   runHFSpectraWithPrefixes("/path/to/Charm/ccbar_MONASH_sub",
//                            "/path/to/Charm/ccbar_JUNCTIONS_sub",
//                            "/path/to/Beauty/bbbar_MONASH_sub",
//                            "/path/to/Beauty/bbbar_JUNCTIONS_sub",
//                            10);
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
#include "TString.h"
#include "TMath.h"
#include "TROOT.h"

#include "PlottingPathUtils.h"
#include "../HistogramErrorUtils.h"

namespace {

struct PlotPathBootstrap {
    PlotPathBootstrap() { PlotPathUtils::RegisterMacroPath(__FILE__); }
} gPlotPathBootstrap;

void SetStyle() {
    gStyle->SetOptStat(0);
    gStyle->SetPadBottomMargin(0.13);
    gStyle->SetPadLeftMargin(0.12);
    gStyle->SetPadRightMargin(0.05);
    gStyle->SetTitleSize(0.055,"XY");
    gStyle->SetLabelSize(0.048,"XY");
    gStyle->SetLegendBorderSize(0);
    gStyle->SetErrorX(0.0);
}

static const double kFixedXMax = 100.0; // set <=0 to enable auto-crop

template<class T>
T* GetObj(TFile* f, const char* name) {
    return f ? dynamic_cast<T*>(f->Get(name)) : nullptr;
}

TH2* CloneTH2(TH2* h, const char* cloneName)
{
    if (!h) return nullptr;
    TH2* clone = dynamic_cast<TH2*>(h->Clone(cloneName));
    if (clone) {
        clone->SetDirectory(nullptr);
        PlotErrorUtils::EnsureSumw2(clone);
    }
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
        PlotErrorUtils::EnsureSumw2(hBar);
        combined->Add(hBar);
        return combined;
    }

    return nullptr;
}

TH2* GetCharmLambdaHist(TFile* f, const char* cloneName)
{
    return GetChargeCombinedHist(
        f,
        {"fHistPtLambdac", "fHistPtLambdacPlus"},
        {"fHistPtLambdac", "fHistPtLambdacPlus"},
        cloneName
    );
}

TH2* GetCharmDHist(TFile* f, const char* cloneName)
{
    return GetChargeCombinedHist(f, {"fHistPtDplus"}, {"fHistPtDplus"}, cloneName);
}

TH2* GetBeautyLambdaHist(TFile* f, const char* cloneName)
{
    return GetChargeCombinedHist(f, {"fHistPtLambdab"}, {"fHistPtLambdab"}, cloneName);
}

TH2* GetBeautyBHist(TFile* f, const char* cloneName)
{
    return GetChargeCombinedHist(f, {"fHistPtBplus"}, {"fHistPtBplus"}, cloneName);
}

// Percentile range: highest multiplicity = highest mult bin
std::pair<int,int> PercentileRange(TH1* hMult, double pTop, double pBot)
{
    int nb = hMult->GetNbinsX();
    double total = hMult->Integral(1, nb);
    if (total <= 0) return {1, nb};

    double thrTop = total*(pTop/100.0);
    double thrBot = total*(pBot/100.0);

    double cum = 0.0;
    int yH = nb, yL = nb;

    for (int b = nb; b >= 1; --b) {
        cum += hMult->GetBinContent(b);
        if (cum >= thrTop) { yH = b; break; }
    }
    for (int b = yH; b >= 1; --b) {
        if (cum >= thrBot) { yL = b; break; }
        cum += hMult->GetBinContent(b-1);
    }
    if (yL > yH) std::swap(yL, yH);
    return {yL, yH};
}

void NormalizeToUnity(TH1D* h)
{
    PlotErrorUtils::NormalizeToUnitShape(h);
}

// One subsample: TH2 -> projection in mult range, then normalize to unit integral.
TH1D* BuildSpectrumOneSub(TH2* h2, std::pair<int,int> yr,
                          const char* name,
                          const char* xtitle,
                          const char* ytitle)
{
    if (!h2) return nullptr;

    TH1D* hp = h2->ProjectionX(Form("%s_proj", name), yr.first, yr.second, "e");
    if (!hp) return nullptr;

    TH1D* h = (TH1D*)hp->Clone(name);
    delete hp;

    h->SetTitle("");
    h->GetXaxis()->SetTitle(xtitle);
    h->GetYaxis()->SetTitle(ytitle);
    PlotErrorUtils::EnsureSumw2(h);
    NormalizeToUnity(h);
    return h;
}

// Combine subsamples bin-by-bin: mean ± SEM across the normalized subsamples.
TH1D* CombineSubsampleSpectra(const std::vector<TH1D*>& hs,
                              const char* name,
                              const char* xtitle,
                              const char* ytitle)
{
    if (hs.empty()) return nullptr;

    TH1D* ref = hs[0];
    int nbx = ref->GetNbinsX();
    double xmin = ref->GetXaxis()->GetXmin();
    double xmax = ref->GetXaxis()->GetXmax();

    TH1D* hC = new TH1D(name, "", nbx, xmin, xmax);
    hC->GetXaxis()->SetTitle(xtitle);
    hC->GetYaxis()->SetTitle(ytitle);
    PlotErrorUtils::EnsureSumw2(hC);

    const int nSubsamples = static_cast<int>(hs.size());

    for (int bx = 1; bx <= nbx; ++bx) {
        std::vector<double> values;
        values.reserve(nSubsamples);
        for (auto* h : hs) {
            if (!h) continue;
            values.push_back(h->GetBinContent(bx));
        }

        if (values.empty()) continue;

        double mean = 0.0;
        for (double v : values) mean += v;
        mean /= static_cast<double>(values.size());

        double sem = 0.0;
        if (values.size() > 1) {
            double var = 0.0;
            for (double v : values) var += (v - mean) * (v - mean);
            sem = std::sqrt(var / (values.size() * (values.size() - 1)));
        }

        hC->SetBinContent(bx, mean);
        hC->SetBinError(bx, sem);
    }

    return hC;
}

// Find last x (upper edge) where ANY of the curves has nonzero content.
// Adds a small margin.
double AutoXMax(const std::vector<TH1D*>& curves, double marginFrac = 0.05)
{
    double xmax = 0.0;
    for (auto* h : curves){
        if (!h) continue;
        int nb = h->GetNbinsX();
        for (int b = nb; b >= 1; --b){
            if (h->GetBinContent(b) > 0){
                double edge = h->GetXaxis()->GetBinUpEdge(b);
                xmax = std::max(xmax, edge);
                break;
            }
        }
    }
    if (xmax <= 0.0) xmax = 10.0;
    xmax *= (1.0 + marginFrac);
    return xmax;
}

// Multiplicity class definition (same as in your ratio macros)
struct CDef { double pTop, pBot; const char* tag; const char* label; };

static const std::vector<CDef> kClasses = {
    {  0, 20, "0_20",   "0-20%"   },
    { 20, 40, "20_40",  "20-40%"  },
    { 40, 60, "40_60",  "40-60%"  },
    { 60, 80, "60_80",  "60-80%"  },
    { 80,100, "80_100", "80-100%" }
};

// Color convention to match your example (keep consistent across all plots)
struct StyleDef { int color; int lstyle; int lwidth; };
static const StyleDef kStyle[5] = {
    { kOrange+7, 1, 3 }, // 0-20
    { kViolet+1, 1, 3 }, // 20-40
    { kGreen+2,  1, 3 }, // 40-60
    { kRed+1,    1, 3 }, // 60-80
    { kBlue+1,   1, 3 }  // 80-100
};

// Draw one tune/species plot (5 curves) and save png
void DrawSpectraPlot(const std::vector<TH1D*>& curves,
                     const char* canvasName,
                     const char* title,
                     const char* outPng)
{
    if (curves.size() != kClasses.size()) return;

    TCanvas* c = new TCanvas(canvasName, title, 1000, 650);
    c->SetLogy();

    // Determine X range and Y range
    double xmax = (kFixedXMax > 0.0 ? kFixedXMax : AutoXMax(curves, 0.03));

    double ymax = 0.0;
    double yminPos = 1e9;
    for (auto* h : curves){
        if (!h) continue;
        // find smallest positive content for a sensible y-min
        for (int b=1; b<=h->GetNbinsX(); ++b){
            double v = h->GetBinContent(b);
            double e = h->GetBinError(b);
            ymax = std::max(ymax, v + e);
            if (v > 0) yminPos = std::min(yminPos, v);
        }
    }
    if (ymax <= 0) ymax = 1.0;
    ymax *= 1.6;

    double ymin = 1e-5;

    // Style + axes on first hist
    TH1D* h0 = curves[0];
    h0->SetTitle(title);
    h0->SetMinimum(ymin);
    h0->SetMaximum(ymax);
    h0->GetXaxis()->SetRangeUser(0.0, xmax);

    // Draw histogram outlines first so the spectrum keeps the bin-width shape.
    for (size_t i=0; i<curves.size(); ++i){
        TH1D* h = curves[i];
        if (!h) continue;
        h->SetLineColor(kStyle[i].color);
        h->SetLineStyle(kStyle[i].lstyle);
        h->SetLineWidth(kStyle[i].lwidth);
        h->SetFillStyle(0);
        h->SetFillColor(0);
        h->SetMarkerStyle(1);
        h->SetMarkerSize(0.0);

        const char* opt = (i==0 ? "HIST" : "HIST SAME");
        h->Draw(opt);
    }

    // Overlay the statistical uncertainties as vertical bars for each bin.
    for (auto* h : curves){
        if (!h) continue;
        h->Draw("E0 X0 SAME");
    }

    TLegend* leg = new TLegend(0.62, 0.70, 0.88, 0.90);
    leg->SetTextSize(0.035);
    for (size_t i=0; i<kClasses.size(); ++i){
        leg->AddEntry(curves[i], Form("%s Multiplicity", kClasses[i].label), "l");
    }
    leg->Draw();

    c->SaveAs(PlotPathUtils::BuildPtMultiplicityPlotPath(outPng));
    delete c;
}

} // namespace


// ============================================================================
// MAIN DRIVER
// ============================================================================

void Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples_WithPrefixes(
        const char* cPrefixMONASH = "ccbar_MONASH_sub",
        const char* cPrefixJUN    = "ccbar_JUNCTIONS_sub",
        const char* bPrefixMONASH = "bbbar_MONASH_sub",
        const char* bPrefixJUN    = "bbbar_JUNCTIONS_sub",
        int nSub                  = 10)
{
    SetStyle();

    if (nSub <= 0) {
        std::cout << "nSub must be > 0\n";
        return;
    }

    const char* MULT_HIST = "fHistMultiplicity";

    // ---------- Load files ----------
    std::vector<TFile*> fCM(nSub,nullptr), fCJ(nSub,nullptr);
    std::vector<TFile*> fBM(nSub,nullptr), fBJ(nSub,nullptr);

    bool ok = true;

    struct CharmH { TH1* mult=nullptr; TH2* lc=nullptr; TH2* d=nullptr; };
    struct BeatH  { TH1* mult=nullptr; TH2* lb=nullptr; TH2* b=nullptr; };

    std::vector<CharmH> cM(nSub), cJ(nSub);
    std::vector<BeatH>  bM(nSub), bJ(nSub);

    for (int i=0;i<nSub;++i){
        // Charm
        TString cNameM = Form("%s%d.root", cPrefixMONASH, i);
        TString cNameJ = Form("%s%d.root", cPrefixJUN,    i);
        fCM[i] = TFile::Open(cNameM,"READ");
        fCJ[i] = TFile::Open(cNameJ,"READ");

        if (!fCM[i] || fCM[i]->IsZombie()) { std::cout<<"Error opening "<<cNameM<<"\n"; ok=false; }
        if (!fCJ[i] || fCJ[i]->IsZombie()) { std::cout<<"Error opening "<<cNameJ<<"\n"; ok=false; }

        if (ok){
            cM[i].mult = GetObj<TH1>(fCM[i], MULT_HIST);
            cM[i].lc   = GetCharmLambdaHist(fCM[i], Form("hLcCM_sub%d", i));
            cM[i].d    = GetCharmDHist(fCM[i], Form("hDCM_sub%d", i));

            cJ[i].mult = GetObj<TH1>(fCJ[i], MULT_HIST);
            cJ[i].lc   = GetCharmLambdaHist(fCJ[i], Form("hLcCJ_sub%d", i));
            cJ[i].d    = GetCharmDHist(fCJ[i], Form("hDCJ_sub%d", i));

            if (!(cM[i].mult && cM[i].lc && cM[i].d)) { std::cout<<"Missing charm MONASH hists in "<<cNameM<<"\n"; ok=false; }
            if (!(cJ[i].mult && cJ[i].lc && cJ[i].d)) { std::cout<<"Missing charm JUNCTIONS hists in "<<cNameJ<<"\n"; ok=false; }
        }

        // Beauty
        TString bNameM = Form("%s%d.root", bPrefixMONASH, i);
        TString bNameJ = Form("%s%d.root", bPrefixJUN,    i);
        fBM[i] = TFile::Open(bNameM,"READ");
        fBJ[i] = TFile::Open(bNameJ,"READ");

        if (!fBM[i] || fBM[i]->IsZombie()) { std::cout<<"Error opening "<<bNameM<<"\n"; ok=false; }
        if (!fBJ[i] || fBJ[i]->IsZombie()) { std::cout<<"Error opening "<<bNameJ<<"\n"; ok=false; }

        if (ok){
            bM[i].mult = GetObj<TH1>(fBM[i], MULT_HIST);
            bM[i].lb   = GetBeautyLambdaHist(fBM[i], Form("hLbBM_sub%d", i));
            bM[i].b    = GetBeautyBHist(fBM[i], Form("hBBM_sub%d", i));

            bJ[i].mult = GetObj<TH1>(fBJ[i], MULT_HIST);
            bJ[i].lb   = GetBeautyLambdaHist(fBJ[i], Form("hLbBJ_sub%d", i));
            bJ[i].b    = GetBeautyBHist(fBJ[i], Form("hBBJ_sub%d", i));

            if (!(bM[i].mult && bM[i].lb && bM[i].b)) { std::cout<<"Missing beauty MONASH hists in "<<bNameM<<"\n"; ok=false; }
            if (!(bJ[i].mult && bJ[i].lb && bJ[i].b)) { std::cout<<"Missing beauty JUNCTIONS hists in "<<bNameJ<<"\n"; ok=false; }
        }

        if (!ok) break;
    }

    if (!ok){
        for (auto& sample : cM) {
            delete sample.lc;
            delete sample.d;
        }
        for (auto& sample : cJ) {
            delete sample.lc;
            delete sample.d;
        }
        for (auto& sample : bM) {
            delete sample.lb;
            delete sample.b;
        }
        for (auto& sample : bJ) {
            delete sample.lb;
            delete sample.b;
        }
        for (auto* f : fCM) if (f) f->Close();
        for (auto* f : fCJ) if (f) f->Close();
        for (auto* f : fBM) if (f) f->Close();
        for (auto* f : fBJ) if (f) f->Close();
        std::cout<<"Aborting.\n";
        return;
    }

    // ---------- Build combined spectra per tune/species/class ----------
    // We will produce 8 plots:
    //   Charm MONASH: Lambdac, D
    //   Charm JUN:    Lambdac, D
    //   Beauty MONASH: Lambdab, Bpm
    //   Beauty JUN:    Lambdab, Bpm

    auto buildCurves = [&](const char* speciesTag,
                           const char* xtitle,
                           const char* ytitle,
                           // provide lambdas to access (mult, TH2*) for each subsample
                           auto getMult,
                           auto getH2) -> std::vector<TH1D*>
    {
        std::vector<TH1D*> curves;
        curves.reserve(kClasses.size());

        for (size_t ic=0; ic<kClasses.size(); ++ic){
            const auto& C = kClasses[ic];

            std::vector<TH1D*> subs;
            subs.reserve(nSub);

            for (int is=0; is<nSub; ++is){
                TH1* hMult = getMult(is);
                TH2* h2    = getH2(is);
                auto yr    = PercentileRange(hMult, C.pTop, C.pBot);

                TH1D* h = BuildSpectrumOneSub(
                    h2, yr,
                    Form("h_%s_%s_sub%d_%s", speciesTag, C.tag, is, "tmp"),
                    xtitle, ytitle
                );
                if (h) subs.push_back(h);
            }

            TH1D* comb = CombineSubsampleSpectra(
                subs,
                Form("h_%s_%s", speciesTag, C.tag),
                xtitle, ytitle
            );

            for (auto* h : subs) delete h;
            curves.push_back(comb);
        }

        return curves;
    };

    // Charm MONASH curves
    auto lc_CM = buildCurves("Lambdac_CM",
        "p_{T} (GeV/c)", "Normalized Counts",
        [&](int i){ return cM[i].mult; },
        [&](int i){ return cM[i].lc; }
    );
    auto d_CM = buildCurves("Dpm_CM",
        "p_{T} (GeV/c)", "Normalized Counts",
        [&](int i){ return cM[i].mult; },
        [&](int i){ return cM[i].d; }
    );

    // Charm JUN curves
    auto lc_CJ = buildCurves("Lambdac_CJ",
        "p_{T} (GeV/c)", "Normalized Counts",
        [&](int i){ return cJ[i].mult; },
        [&](int i){ return cJ[i].lc; }
    );
    auto d_CJ = buildCurves("Dpm_CJ",
        "p_{T} (GeV/c)", "Normalized Counts",
        [&](int i){ return cJ[i].mult; },
        [&](int i){ return cJ[i].d; }
    );

    // Beauty MONASH curves
    auto lb_BM = buildCurves("Lambdab_BM",
        "p_{T} (GeV/c)", "Normalized Counts",
        [&](int i){ return bM[i].mult; },
        [&](int i){ return bM[i].lb; }
    );
    auto b_BM = buildCurves("Bpm_BM",
        "p_{T} (GeV/c)", "Normalized Counts",
        [&](int i){ return bM[i].mult; },
        [&](int i){ return bM[i].b; }
    );

    // Beauty JUN curves
    auto lb_BJ = buildCurves("Lambdab_BJ",
        "p_{T} (GeV/c)", "Normalized Counts",
        [&](int i){ return bJ[i].mult; },
        [&](int i){ return bJ[i].lb; }
    );
    auto b_BJ = buildCurves("Bpm_BJ",
        "p_{T} (GeV/c)", "Normalized Counts",
        [&](int i){ return bJ[i].mult; },
        [&](int i){ return bJ[i].b; }
    );

    // ---------- Draw ----------
    // Titles/outnames tuned to look like your example figure
    DrawSpectraPlot(lc_CJ, "c_Lambdac_Junctions",
        "(#Lambda_{c}^{+} + #bar{#Lambda}_{c}^{-}) p_{T} Spectra by Multiplicity Percentile (JUNCTIONS)",
        "Spectra_Lambdac_JUNCTIONS.png");

    DrawSpectraPlot(lc_CM, "c_Lambdac_Monash",
        "(#Lambda_{c}^{+} + #bar{#Lambda}_{c}^{-}) p_{T} Spectra by Multiplicity Percentile (MONASH)",
        "Spectra_Lambdac_MONASH.png");

    DrawSpectraPlot(d_CJ, "c_Dpm_Junctions",
        "D^{#pm} p_{T} Spectra by Multiplicity Percentile (JUNCTIONS)",
        "Spectra_Dpm_JUNCTIONS.png");

    DrawSpectraPlot(d_CM, "c_Dpm_Monash",
        "D^{#pm} p_{T} Spectra by Multiplicity Percentile (MONASH)",
        "Spectra_Dpm_MONASH.png");

    DrawSpectraPlot(lb_BJ, "c_Lambdab_Junctions",
        "(#Lambda_{b}^{0} + #bar{#Lambda}_{b}^{0}) p_{T} Spectra by Multiplicity Percentile (JUNCTIONS)",
        "Spectra_Lambdab_JUNCTIONS.png");

    DrawSpectraPlot(lb_BM, "c_Lambdab_Monash",
        "(#Lambda_{b}^{0} + #bar{#Lambda}_{b}^{0}) p_{T} Spectra by Multiplicity Percentile (MONASH)",
        "Spectra_Lambdab_MONASH.png");

    DrawSpectraPlot(b_BJ, "c_Bpm_Junctions",
        "B^{#pm} p_{T} Spectra by Multiplicity Percentile (JUNCTIONS)",
        "Spectra_Bpm_JUNCTIONS.png");

    DrawSpectraPlot(b_BM, "c_Bpm_Monash",
        "B^{#pm} p_{T} Spectra by Multiplicity Percentile (MONASH)",
        "Spectra_Bpm_MONASH.png");

    // ---------- Cleanup ----------
    for (auto* h : lc_CM) if (h) delete h;
    for (auto* h : d_CM)  if (h) delete h;
    for (auto* h : lc_CJ) if (h) delete h;
    for (auto* h : d_CJ)  if (h) delete h;

    for (auto* h : lb_BM) if (h) delete h;
    for (auto* h : b_BM)  if (h) delete h;
    for (auto* h : lb_BJ) if (h) delete h;
    for (auto* h : b_BJ)  if (h) delete h;

    for (auto& sample : cM) {
        delete sample.lc;
        delete sample.d;
    }
    for (auto& sample : cJ) {
        delete sample.lc;
        delete sample.d;
    }
    for (auto& sample : bM) {
        delete sample.lb;
        delete sample.b;
    }
    for (auto& sample : bJ) {
        delete sample.lb;
        delete sample.b;
    }

    for (auto* f : fCM) if (f) f->Close();
    for (auto* f : fCJ) if (f) f->Close();
    for (auto* f : fBM) if (f) f->Close();
    for (auto* f : fBJ) if (f) f->Close();

    std::cout << "\nSaved:\n"
              << "  " << PlotPathUtils::GetPtMultiplicityPlotsDir()
              << "/Spectra_Lambdac_{MONASH,JUNCTIONS}.png\n"
              << "  " << PlotPathUtils::GetPtMultiplicityPlotsDir()
              << "/Spectra_Dpm_{MONASH,JUNCTIONS}.png\n"
              << "  " << PlotPathUtils::GetPtMultiplicityPlotsDir()
              << "/Spectra_Lambdab_{MONASH,JUNCTIONS}.png\n"
              << "  " << PlotPathUtils::GetPtMultiplicityPlotsDir()
              << "/Spectra_Bpm_{MONASH,JUNCTIONS}.png\n";
}


void Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples(const char* dateTag = "",
                                                                      int nSub = 10)
{
    TString resolvedDate = PlotPathUtils::ResolveAnalysisDate(dateTag);
    if (resolvedDate.Length() == 0) return;

    TString cPrefixMONASH = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate, "Charm", {"hf_MONASH_sub", "ccbar_MONASH_sub"});
    TString cPrefixJUN = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate, "Charm", {"hf_JUNCTIONS_sub", "ccbar_JUNCTIONS_sub"});
    TString bPrefixMONASH = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate, "Beauty", {"hf_MONASH_sub", "bbbar_MONASH_sub"});
    TString bPrefixJUN = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate, "Beauty", {"hf_JUNCTIONS_sub", "bbbar_JUNCTIONS_sub"});

    std::cout << "HF spectra input date: " << resolvedDate << "\n";
    std::cout << "  Charm MONASH     : " << cPrefixMONASH << "*.root\n";
    std::cout << "  Charm JUNCTIONS  : " << cPrefixJUN << "*.root\n";
    std::cout << "  Beauty MONASH    : " << bPrefixMONASH << "*.root\n";
    std::cout << "  Beauty JUNCTIONS : " << bPrefixJUN << "*.root\n";

    Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples_WithPrefixes(
        cPrefixMONASH.Data(),
        cPrefixJUN.Data(),
        bPrefixMONASH.Data(),
        bPrefixJUN.Data(),
        nSub
    );
}

// Keep a prefix-based entry point for custom studies.
void runHFSpectraWithPrefixes(const char* cPrefixMONASH = "ccbar_MONASH_sub",
                              const char* cPrefixJUN    = "ccbar_JUNCTIONS_sub",
                              const char* bPrefixMONASH = "bbbar_MONASH_sub",
                              const char* bPrefixJUN    = "bbbar_JUNCTIONS_sub",
                              int nSub                  = 10)
{
    Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples_WithPrefixes(
        cPrefixMONASH, cPrefixJUN,
        bPrefixMONASH, bPrefixJUN,
        nSub
    );
}

void runHFSpectra(const char* dateTag = "", int nSub = 10)
{
    Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples(dateTag, nSub);
}

void runHFSpectraWax(const char* dateTag = "", int nSub = 10)
{
    Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples(dateTag, nSub);
}
