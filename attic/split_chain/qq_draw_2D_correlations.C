// qq_draw_2D_correlations.C
//
// Draw OS - SS 1D and 2D correlations from the compact ROOT files produced by
// status_analysis_qq.C. The default input path matches the 10-05-2026 bundle.

#include <iostream>
#include <vector>

#include "TCanvas.h"
#include "TFile.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TROOT.h"
#include "TString.h"
#include "TStyle.h"
#include "TSystem.h"

struct QQPairConfig {
    const char *title;
    const char *stem;
    const char *fileOS;
    const char *fileSS;
};

TString JoinPath(const char *dir, const TString &name)
{
    TString path(dir);
    if (!path.EndsWith("/")) {
        path += "/";
    }
    path += name;
    return path;
}

TString JoinPath(const char *dir, const char *name)
{
    return JoinPath(dir, TString(name));
}

TH1D *CloneH1(TFile &file, const char *histName, const TString &cloneName, const TString &filePath)
{
    TH1D *hist = dynamic_cast<TH1D *>(file.Get(histName));
    if (!hist) {
        std::cerr << "Missing TH1D '" << histName << "' in " << filePath << std::endl;
        return nullptr;
    }

    TH1D *clone = dynamic_cast<TH1D *>(hist->Clone(cloneName));
    clone->SetDirectory(nullptr);
    return clone;
}

TH2D *CloneH2(TFile &file, const char *histName, const TString &cloneName, const TString &filePath)
{
    TH2D *hist = dynamic_cast<TH2D *>(file.Get(histName));
    if (!hist) {
        std::cerr << "Missing TH2D '" << histName << "' in " << filePath << std::endl;
        return nullptr;
    }

    TH2D *clone = dynamic_cast<TH2D *>(hist->Clone(cloneName));
    clone->SetDirectory(nullptr);
    return clone;
}

bool ScaleByTriggerIntegral(TH1 *hist, TH1D *triggerPt, const TString &label)
{
    const double integral = triggerPt ? triggerPt->Integral() : 0.0;
    if (integral <= 0.0) {
        std::cerr << "Cannot normalise " << label << ": trigger integral is " << integral << std::endl;
        return false;
    }

    hist->Scale(1.0 / integral);
    return true;
}

void SaveCanvas(TCanvas *canvas, const char *outputDir, const TString &stem)
{
    gSystem->mkdir(outputDir, kTRUE);
    canvas->SaveAs(JoinPath(outputDir, stem + ".pdf"));
    canvas->SaveAs(JoinPath(outputDir, stem + ".png"));
}

bool DrawInclusiveDPhi(const QQPairConfig &pair, TFile &fileOS, TFile &fileSS,
                       const TString &pathOS, const TString &pathSS, const char *outputDir)
{
    TH1D *hDPhiOS = CloneH1(fileOS, "hDPhi", Form("%s_hDPhi_OS", pair.stem), pathOS);
    TH1D *hDPhiSS = CloneH1(fileSS, "hDPhi", Form("%s_hDPhi_SS", pair.stem), pathSS);
    TH1D *hTrPtOS = CloneH1(fileOS, "hTrPt", Form("%s_hTrPt_OS", pair.stem), pathOS);
    TH1D *hTrPtSS = CloneH1(fileSS, "hTrPt", Form("%s_hTrPt_SS", pair.stem), pathSS);

    if (!hDPhiOS || !hDPhiSS || !hTrPtOS || !hTrPtSS) {
        return false;
    }

    if (!ScaleByTriggerIntegral(hDPhiOS, hTrPtOS, Form("%s hDPhi OS", pair.stem)) ||
        !ScaleByTriggerIntegral(hDPhiSS, hTrPtSS, Form("%s hDPhi SS", pair.stem))) {
        return false;
    }

    TH1D *hSubtracted = dynamic_cast<TH1D *>(hDPhiOS->Clone(Form("%s_hDPhi_OSminusSS", pair.stem)));
    hSubtracted->SetDirectory(nullptr);
    hSubtracted->Add(hDPhiSS, -1.0);
    hSubtracted->SetTitle(Form("%s OS - SS;#Delta#varphi;1/N_{trig} dN_{pairs}/d#Delta#varphi", pair.title));
    hSubtracted->SetLineColor(kBlue + 2);
    hSubtracted->SetLineWidth(2);
    hSubtracted->SetMarkerStyle(20);
    hSubtracted->SetMarkerSize(0.7);
    hSubtracted->GetYaxis()->SetTitleOffset(1.55);

    TCanvas *canvas = new TCanvas(Form("c_%s_DPhi", pair.stem), Form("%s #Delta#varphi", pair.title), 1000, 800);
    canvas->SetLeftMargin(0.17);
    canvas->SetBottomMargin(0.12);
    hSubtracted->Draw("E1");

    SaveCanvas(canvas, outputDir, Form("%s_DPhi_OSminusSS", pair.stem));
    return true;
}

bool Draw2DCorrelations(const QQPairConfig &pair, TFile &fileOS, TFile &fileSS,
                        const TString &pathOS, const TString &pathSS, const char *outputDir)
{
    TH2D *hDPhiDEtaOS = CloneH2(fileOS, "hDPhiDEta", Form("%s_hDPhiDEta_OS", pair.stem), pathOS);
    TH2D *hDPhiDEtaM60_100_OS = CloneH2(fileOS, "hDPhiDEtaM60_100", Form("%s_hDPhiDEtaM60_100_OS", pair.stem), pathOS);
    TH2D *hDPhiDEtaM20_60_OS = CloneH2(fileOS, "hDPhiDEtaM20_60", Form("%s_hDPhiDEtaM20_60_OS", pair.stem), pathOS);
    TH2D *hDPhiDEtaM00_20_OS = CloneH2(fileOS, "hDPhiDEtaM00_20", Form("%s_hDPhiDEtaM00_20_OS", pair.stem), pathOS);
    TH2D *hDPhiDEtaSS = CloneH2(fileSS, "hDPhiDEta", Form("%s_hDPhiDEta_SS", pair.stem), pathSS);
    TH2D *hDPhiDEtaM60_100_SS = CloneH2(fileSS, "hDPhiDEtaM60_100", Form("%s_hDPhiDEtaM60_100_SS", pair.stem), pathSS);
    TH2D *hDPhiDEtaM20_60_SS = CloneH2(fileSS, "hDPhiDEtaM20_60", Form("%s_hDPhiDEtaM20_60_SS", pair.stem), pathSS);
    TH2D *hDPhiDEtaM00_20_SS = CloneH2(fileSS, "hDPhiDEtaM00_20", Form("%s_hDPhiDEtaM00_20_SS", pair.stem), pathSS);

    TH1D *hTrPtOS = CloneH1(fileOS, "hTrPt", Form("%s_hTrPt_2D_OS", pair.stem), pathOS);
    TH1D *hTrPtM60_100_OS = CloneH1(fileOS, "hTrPtM60_100", Form("%s_hTrPtM60_100_OS", pair.stem), pathOS);
    TH1D *hTrPtM20_60_OS = CloneH1(fileOS, "hTrPtM20_60", Form("%s_hTrPtM20_60_OS", pair.stem), pathOS);
    TH1D *hTrPtM00_20_OS = CloneH1(fileOS, "hTrPtM00_20", Form("%s_hTrPtM00_20_OS", pair.stem), pathOS);
    TH1D *hTrPtSS = CloneH1(fileSS, "hTrPt", Form("%s_hTrPt_2D_SS", pair.stem), pathSS);
    TH1D *hTrPtM60_100_SS = CloneH1(fileSS, "hTrPtM60_100", Form("%s_hTrPtM60_100_SS", pair.stem), pathSS);
    TH1D *hTrPtM20_60_SS = CloneH1(fileSS, "hTrPtM20_60", Form("%s_hTrPtM20_60_SS", pair.stem), pathSS);
    TH1D *hTrPtM00_20_SS = CloneH1(fileSS, "hTrPtM00_20", Form("%s_hTrPtM00_20_SS", pair.stem), pathSS);

    if (!hDPhiDEtaOS || !hDPhiDEtaM60_100_OS || !hDPhiDEtaM20_60_OS || !hDPhiDEtaM00_20_OS ||
        !hDPhiDEtaSS || !hDPhiDEtaM60_100_SS || !hDPhiDEtaM20_60_SS || !hDPhiDEtaM00_20_SS ||
        !hTrPtOS || !hTrPtM60_100_OS || !hTrPtM20_60_OS || !hTrPtM00_20_OS ||
        !hTrPtSS || !hTrPtM60_100_SS || !hTrPtM20_60_SS || !hTrPtM00_20_SS) {
        return false;
    }

    if (!ScaleByTriggerIntegral(hDPhiDEtaOS, hTrPtOS, Form("%s hDPhiDEta OS", pair.stem)) ||
        !ScaleByTriggerIntegral(hDPhiDEtaM60_100_OS, hTrPtM60_100_OS, Form("%s hDPhiDEtaM60_100 OS", pair.stem)) ||
        !ScaleByTriggerIntegral(hDPhiDEtaM20_60_OS, hTrPtM20_60_OS, Form("%s hDPhiDEtaM20_60 OS", pair.stem)) ||
        !ScaleByTriggerIntegral(hDPhiDEtaM00_20_OS, hTrPtM00_20_OS, Form("%s hDPhiDEtaM00_20 OS", pair.stem)) ||
        !ScaleByTriggerIntegral(hDPhiDEtaSS, hTrPtSS, Form("%s hDPhiDEta SS", pair.stem)) ||
        !ScaleByTriggerIntegral(hDPhiDEtaM60_100_SS, hTrPtM60_100_SS, Form("%s hDPhiDEtaM60_100 SS", pair.stem)) ||
        !ScaleByTriggerIntegral(hDPhiDEtaM20_60_SS, hTrPtM20_60_SS, Form("%s hDPhiDEtaM20_60 SS", pair.stem)) ||
        !ScaleByTriggerIntegral(hDPhiDEtaM00_20_SS, hTrPtM00_20_SS, Form("%s hDPhiDEtaM00_20 SS", pair.stem))) {
        return false;
    }

    TH2D *hSubtracted = dynamic_cast<TH2D *>(hDPhiDEtaOS->Clone(Form("%s_hDPhiDEta_OSminusSS", pair.stem)));
    hSubtracted->SetDirectory(nullptr);
    hSubtracted->Add(hDPhiDEtaSS, -1.0);
    hSubtracted->Rebin2D(5, 5);
    hSubtracted->SetTitle(Form("%s OS - SS, per trigger;#Delta#varphi;#Delta#eta", pair.title));
    hSubtracted->GetZaxis()->SetTitle("");

    gStyle->SetPalette(kBird);

    TCanvas *cInclusive = new TCanvas(Form("c_%s_DPhiDEta", pair.stem),
                                      Form("%s #Delta#varphi#Delta#eta", pair.title), 1200, 900);
    cInclusive->SetRightMargin(0.14);
    cInclusive->SetTheta(30);
    cInclusive->SetPhi(50);
    hSubtracted->Draw("SURF1 FB");
    SaveCanvas(cInclusive, outputDir, Form("%s_DPhiDEta_OSminusSS", pair.stem));

    TH2D *hSub_M00_20 = dynamic_cast<TH2D *>(hDPhiDEtaM00_20_OS->Clone(Form("%s_hSub_M00_20", pair.stem)));
    TH2D *hSub_M20_60 = dynamic_cast<TH2D *>(hDPhiDEtaM20_60_OS->Clone(Form("%s_hSub_M20_60", pair.stem)));
    TH2D *hSub_M60_100 = dynamic_cast<TH2D *>(hDPhiDEtaM60_100_OS->Clone(Form("%s_hSub_M60_100", pair.stem)));

    hSub_M00_20->SetDirectory(nullptr);
    hSub_M20_60->SetDirectory(nullptr);
    hSub_M60_100->SetDirectory(nullptr);

    hSub_M00_20->Add(hDPhiDEtaM00_20_SS, -1.0);
    hSub_M20_60->Add(hDPhiDEtaM20_60_SS, -1.0);
    hSub_M60_100->Add(hDPhiDEtaM60_100_SS, -1.0);

    hSub_M00_20->Rebin2D(5, 5);
    hSub_M20_60->Rebin2D(5, 5);
    hSub_M60_100->Rebin2D(5, 5);

    hSub_M60_100->SetTitle(Form("%s OS - SS, 60-100%%, per trigger;#Delta#varphi;#Delta#eta", pair.title));
    hSub_M20_60->SetTitle(Form("%s OS - SS, 20-60%%, per trigger;#Delta#varphi;#Delta#eta", pair.title));
    hSub_M00_20->SetTitle(Form("%s OS - SS, 0-20%%, per trigger;#Delta#varphi;#Delta#eta", pair.title));
    hSub_M60_100->GetZaxis()->SetTitle("");
    hSub_M20_60->GetZaxis()->SetTitle("");
    hSub_M00_20->GetZaxis()->SetTitle("");

    TCanvas *cMultiplicity = new TCanvas(Form("c_%s_DPhiDEta_mult", pair.stem),
                                         Form("%s multiplicity bins", pair.title), 2400, 800);
    cMultiplicity->Divide(3, 1);

    cMultiplicity->cd(1);
    gPad->SetTheta(30);
    gPad->SetPhi(50);
    gPad->SetRightMargin(0.12);
    hSub_M60_100->Draw("SURF1 FB");

    cMultiplicity->cd(2);
    gPad->SetTheta(30);
    gPad->SetPhi(50);
    gPad->SetRightMargin(0.12);
    hSub_M20_60->Draw("SURF1 FB");

    cMultiplicity->cd(3);
    gPad->SetTheta(30);
    gPad->SetPhi(50);
    gPad->SetRightMargin(0.12);
    hSub_M00_20->Draw("SURF1 FB");

    SaveCanvas(cMultiplicity, outputDir, Form("%s_DPhiDEta_multiplicity_OSminusSS", pair.stem));
    return true;
}

bool DrawQQPair(const QQPairConfig &pair, const char *inputDir, const char *outputDir)
{
    TString pathOS = JoinPath(inputDir, pair.fileOS);
    TString pathSS = JoinPath(inputDir, pair.fileSS);

    TFile fileOS(pathOS, "READ");
    TFile fileSS(pathSS, "READ");

    if (fileOS.IsZombie()) {
        std::cerr << "Could not open OS file " << pathOS << std::endl;
        return false;
    }
    if (fileSS.IsZombie()) {
        std::cerr << "Could not open SS file " << pathSS << std::endl;
        return false;
    }

    const bool drew1D = DrawInclusiveDPhi(pair, fileOS, fileSS, pathOS, pathSS, outputDir);
    const bool drew2D = Draw2DCorrelations(pair, fileOS, fileSS, pathOS, pathSS, outputDir);
    return drew1D && drew2D;
}

int qq_draw_2D_correlations(const char *inputDir = "AnalyzedData/10-05-2026/QQ",
                            const char *outputDir = "PlottingScripts/QQCorrelations/Plots/10-05-2026")
{
    gROOT->SetBatch(kTRUE);
    gStyle->SetOptStat(0);

    const std::vector<QQPairConfig> pairs = {
        {"D^{+}D^{-}", "DplusDminus", "DplusDminus.root", "DplusDplus.root"},
        {"D^{+}#bar{#Lambda}_{c}", "DplusLambdac", "DplusLambdacplusbar.root", "DplusLambdacplus.root"},
        {"D^{+}#bar{#Sigma}_{c}^{+}", "DplusSigmacplus", "DplusSigmacplusbar.root", "DplusSigmacplus.root"},
        {"B^{+}B^{-}", "BplusBminus", "BplusBminus.root", "BplusBplus.root"},
        {"B^{+}#Lambda_{b}^{0}", "BplusLb", "BplusLb.root", "BplusLbbar.root"},
        {"B^{+}#Sigma_{b}^{0}", "BplusSigmabzero", "BplusSigmabzero.root", "BplusSigmabzerobar.root"},
    };

    int nFailed = 0;
    for (const QQPairConfig &pair : pairs) {
        std::cout << "Drawing " << pair.stem << std::endl;
        if (!DrawQQPair(pair, inputDir, outputDir)) {
            ++nFailed;
        }
    }

    if (nFailed > 0) {
        std::cerr << nFailed << " pair(s) failed. See messages above." << std::endl;
        return 1;
    }

    std::cout << "Wrote QQ correlation plots to " << outputDir << std::endl;
    return 0;
}
