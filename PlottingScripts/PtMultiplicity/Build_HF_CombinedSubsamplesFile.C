// ---------------------------------------------------------------------------
// Build_HF_CombinedSubsamplesFile.C
//
// Combine the analyzed heavy-flavour subsamples into one ROOT file that stores
// the same observables used by the current plotting macros:
//
//   - source pT x multiplicity histograms for each particle / antiparticle
//   - source pT x multiplicity histograms for the charge-combined species
//   - source pT x multiplicity histograms for the sum over all selected species
//   - minimum-bias pT spectra
//   - pT spectra in the five multiplicity-percentile classes
//   - mean +- SEM multiplicity histograms across subsamples
//
// The 1D spectra are combined exactly like the plotting macros:
//   one normalized spectrum per subsample -> mean +- SEM bin-by-bin.
//
// The output file layout is:
//   <Flavor>/<Tune>/Metadata
//   <Flavor>/<Tune>/Multiplicity
//   <Flavor>/<Tune>/Source2D
//   <Flavor>/<Tune>/Spectra/MinimumBias
//   <Flavor>/<Tune>/Spectra/ByMultiplicity/<class-tag>
//
// Default particle content matches the current plot macros:
//   Charm  : D0, D0bar, D+, D-, Ds+, Ds-, Lambdac, barLambdac
//   Beauty : B+, B-, B0, barB0, Bs0, barBs0, Bc+, Bc-, Lambdab, barLambdab
//
// Heavier beauty baryons are disabled by default and can be re-enabled with
// includeHeavyBeautyExtras = true.
//
// Usage (from the repo root):
//
//   Shell one-liner (ACLiC compiled):
//     root -l -b -q 'PlottingScripts/PtMultiplicity/Build_HF_CombinedSubsamplesFile.C+("08-04-2026_100M_Separate",10)'
//
//   Interactive ROOT session:
//     .L "PlottingScripts/PtMultiplicity/Build_HF_CombinedSubsamplesFile.C"
//     runHFCombinedSubsamplesFile("27-03-2026", 10);
//     runHFCombinedSubsamplesFile("27-03-2026", 10, true);
//     runHFCombinedSubsamplesFile("27-03-2026", 10, false,
//                                 "AnalyzedData/27-03-2026/custom.root");
// ---------------------------------------------------------------------------

#include <algorithm>
#include <cctype>
#include <cmath>
#include <iostream>
#include <utility>
#include <vector>

#include "TDirectory.h"
#include "TFile.h"
#include "TH1.h"
#include "TH1D.h"
#include "TH2.h"
#include "TNamed.h"
#include "TROOT.h"
#include "TString.h"
#include "TSystem.h"

#include "PlottingPathUtils.h"
#include "../HistogramErrorUtils.h"

namespace {

struct PlotPathBootstrap {
    PlotPathBootstrap() { PlotPathUtils::RegisterMacroPath(__FILE__); }
} gPlotPathBootstrap;

struct ClassDef {
    double pTop;
    double pBot;
    const char* tag;
    const char* label;
};

enum RequestMode {
    kPreferDirect = 0,
    kPreferParticle = 1,
    kPreferBar = 2
};

struct ParticleDef {
    TString key;
    TString flavorDir;
    std::vector<TString> directNames;
    std::vector<TString> splitBases;
    TString fallbackDirectLabel;
    TString fallbackParticleLabel;
    TString fallbackBarLabel;
};

struct HistogramRequest {
    const ParticleDef* def;
    RequestMode mode;
    TString outputTag;
    TString fallbackLabel;

    HistogramRequest() : def(nullptr), mode(kPreferDirect), outputTag(""), fallbackLabel("") {}
};

struct LoadedSample {
    TFile* file;
    TH1* mult;
    TH1* taggedMult;

    LoadedSample() : file(nullptr), mult(nullptr), taggedMult(nullptr) {}
};

static const std::vector<ClassDef> kClasses = {
    { 80,100, "80_100", "80-100%" },
    { 60, 80, "60_80",  "60-80%"  },
    { 40, 60, "40_60",  "40-60%"  },
    { 20, 40, "20_40",  "20-40%"  },
    {  0, 20, "0_20",   "0-20%"   }
};

template<class T>
T* GetObj(TFile* file, const char* name)
{
    return file ? dynamic_cast<T*>(file->Get(name)) : nullptr;
}

TH1* GetMultiplicityHist(TFile* file)
{
    if (TH1* tagged = GetObj<TH1>(file, "fHistTaggedMultiplicity")) return tagged;
    return GetObj<TH1>(file, "fHistMultiplicity");
}

TH1* GetTaggedMultiplicityHist(TFile* file)
{
    return GetObj<TH1>(file, "fHistTaggedMultiplicity");
}

TH2* CloneTH2(TH2* hist, const char* cloneName)
{
    if (!hist) return nullptr;

    TH2* clone = dynamic_cast<TH2*>(hist->Clone(cloneName));
    if (!clone) return nullptr;

    clone->SetDirectory(nullptr);
    PlotErrorUtils::EnsureSumw2(clone);
    return clone;
}

TH1D* CloneTH1D(TH1* hist, const char* cloneName)
{
    if (!hist) return nullptr;

    TH1D* clone = dynamic_cast<TH1D*>(hist->Clone(cloneName));
    if (!clone) return nullptr;

    clone->SetDirectory(nullptr);
    PlotErrorUtils::EnsureSumw2(clone);
    return clone;
}

TH2* GetDirectHist(TFile* file,
                   const std::vector<TString>& names,
                   const char* cloneName = nullptr)
{
    if (!file) return nullptr;

    for (const TString& name : names) {
        TH2* hist = GetObj<TH2>(file, name.Data());
        if (!hist) continue;
        if (!cloneName) return hist;
        return CloneTH2(hist, cloneName);
    }

    return nullptr;
}

TH2* GetSplitHist(TFile* file,
                  const std::vector<TString>& splitBases,
                  bool wantParticle,
                  const char* cloneName = nullptr)
{
    if (!file) return nullptr;

    for (const TString& base : splitBases) {
        const TString histName = TString::Format("%s%s",
                                                 base.Data(),
                                                 wantParticle ? "Particle" : "Bar");
        TH2* hist = GetObj<TH2>(file, histName.Data());
        if (!hist) continue;
        if (!cloneName) return hist;
        return CloneTH2(hist, cloneName);
    }

    return nullptr;
}

TH2* GetCombinedFromSplitPair(TFile* file,
                              const std::vector<TString>& splitBases,
                              const char* cloneName)
{
    if (!file) return nullptr;

    for (const TString& base : splitBases) {
        TH2* particleHist = GetObj<TH2>(file, Form("%sParticle", base.Data()));
        TH2* barHist = GetObj<TH2>(file, Form("%sBar", base.Data()));
        if (!particleHist || !barHist) continue;

        TH2* combined = CloneTH2(particleHist, cloneName);
        if (!combined) continue;

        PlotErrorUtils::EnsureSumw2(barHist);
        combined->Add(barHist);
        return combined;
    }

    return nullptr;
}

ParticleDef MakeParticleDef(const char* key,
                            const char* flavorDir,
                            const std::vector<TString>& directNames,
                            const std::vector<TString>& splitBases,
                            const char* fallbackDirectLabel,
                            const char* fallbackParticleLabel,
                            const char* fallbackBarLabel)
{
    ParticleDef def;
    def.key = key;
    def.flavorDir = flavorDir;
    def.directNames = directNames;
    def.splitBases = splitBases;
    def.fallbackDirectLabel = fallbackDirectLabel;
    def.fallbackParticleLabel = fallbackParticleLabel;
    def.fallbackBarLabel = fallbackBarLabel;
    return def;
}

std::vector<ParticleDef> BuildParticleDefs()
{
    std::vector<ParticleDef> defs;

    defs.push_back(MakeParticleDef(
        "Dzero", "Charm",
        {"fHistPtDzero"}, {"fHistPtDzero"},
        "D^{0}/#bar{D}^{0}",
        "D^{0}",
        "#bar{D}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "Dplus", "Charm",
        {"fHistPtDplus"}, {"fHistPtDplus"},
        "D^{#pm}",
        "D^{+}",
        "D^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "Dsplus", "Charm",
        {"fHistPtDsplus"}, {"fHistPtDsplus"},
        "D_{s}^{#pm}",
        "D_{s}^{+}",
        "D_{s}^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "Lambdac", "Charm",
        {"fHistPtLambdac", "fHistPtLambdacPlus"}, {"fHistPtLambdac"},
        "#Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-}",
        "#Lambda_{c}^{+}",
        "#bar{#Lambda}_{c}^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "Bplus", "Beauty",
        {"fHistPtBplus"}, {"fHistPtBplus"},
        "B^{#pm}",
        "B^{+}",
        "B^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "Bzero", "Beauty",
        {"fHistPtBzero"}, {"fHistPtBzero"},
        "B^{0}/#bar{B}^{0}",
        "B^{0}",
        "#bar{B}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "Bs0", "Beauty",
        {"fHistPtBs0"}, {"fHistPtBs0"},
        "B_{s}^{0}/#bar{B}_{s}^{0}",
        "B_{s}^{0}",
        "#bar{B}_{s}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "Bcplus", "Beauty",
        {"fHistPtBcplus"}, {"fHistPtBcplus"},
        "B_{c}^{#pm}",
        "B_{c}^{+}",
        "B_{c}^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "Lambdab", "Beauty",
        {"fHistPtLambdab"}, {"fHistPtLambdab"},
        "#Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0}",
        "#Lambda_{b}^{0}",
        "#bar{#Lambda}_{b}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "SigmabPlus", "Beauty",
        {"fHistPtSigmabPlus"}, {"fHistPtSigmabPlus"},
        "#Sigma_{b}^{+}/#bar{#Sigma}_{b}^{-}",
        "#Sigma_{b}^{+}",
        "#bar{#Sigma}_{b}^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "SigmabZero", "Beauty",
        {"fHistPtSigmabZero"}, {"fHistPtSigmabZero"},
        "#Sigma_{b}^{0}/#bar{#Sigma}_{b}^{0}",
        "#Sigma_{b}^{0}",
        "#bar{#Sigma}_{b}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "SigmabMinus", "Beauty",
        {"fHistPtSigmabMinus"}, {"fHistPtSigmabMinus"},
        "#Sigma_{b}^{-}/#bar{#Sigma}_{b}^{+}",
        "#Sigma_{b}^{-}",
        "#bar{#Sigma}_{b}^{+}"
    ));

    defs.push_back(MakeParticleDef(
        "XibZero", "Beauty",
        {"fHistPtXibZero"}, {"fHistPtXibZero"},
        "#Xi_{b}^{0}/#bar{#Xi}_{b}^{0}",
        "#Xi_{b}^{0}",
        "#bar{#Xi}_{b}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "XibMinus", "Beauty",
        {"fHistPtXibMinus"}, {"fHistPtXibMinus"},
        "#Xi_{b}^{-}/#bar{#Xi}_{b}^{+}",
        "#Xi_{b}^{-}",
        "#bar{#Xi}_{b}^{+}"
    ));

    defs.push_back(MakeParticleDef(
        "OmegabMinus", "Beauty",
        {"fHistPtOmegabMinus"}, {"fHistPtOmegabMinus"},
        "#Omega_{b}^{-}/#bar{#Omega}_{b}^{+}",
        "#Omega_{b}^{-}",
        "#bar{#Omega}_{b}^{+}"
    ));

    return defs;
}

std::vector<ParticleDef>& PersistentParticleDefs()
{
    static std::vector<ParticleDef> defs = BuildParticleDefs();
    return defs;
}

const ParticleDef* FindParticleDefByKey(const std::vector<ParticleDef>& defs,
                                        const char* key)
{
    for (const ParticleDef& def : defs) {
        if (def.key == key) return &def;
    }
    return nullptr;
}

TString LabelFromTitle(const char* title, const char* fallback)
{
    TString label = title ? TString(title) : TString("");
    label = label.Strip(TString::kBoth);

    const Ssiz_t semicolonPos = label.First(';');
    if (semicolonPos != kNPOS) label.Remove(semicolonPos);

    const Ssiz_t colonPos = label.First(':');
    if (colonPos != kNPOS) label.Remove(colonPos);

    label.ReplaceAll(" (charge-conjugate combined)", "");
    label = label.Strip(TString::kBoth);

    if (label.IsNull()) label = fallback ? TString(fallback) : TString("");
    return label;
}

HistogramRequest MakeRequest(const ParticleDef* def,
                             RequestMode mode,
                             const char* outputTag,
                             const char* fallbackLabel)
{
    HistogramRequest request;
    request.def = def;
    request.mode = mode;
    request.outputTag = outputTag;
    request.fallbackLabel = fallbackLabel;
    return request;
}

void AppendRequestsForKey(std::vector<HistogramRequest>& requests,
                          const std::vector<ParticleDef>& defs,
                          const char* key)
{
    const ParticleDef* def = FindParticleDefByKey(defs, key);
    if (!def) return;

    TString particleTag = def->key;
    TString barTag = def->key;
    TString combinedTag = def->key + "Combined";

    if (def->key == "Dzero") barTag = "Dbar0";
    else if (def->key == "Dplus") barTag = "Dminus";
    else if (def->key == "Dsplus") barTag = "Dsminus";
    else if (def->key == "Lambdac") barTag = "barLambdac";
    else if (def->key == "Bplus") barTag = "Bminus";
    else if (def->key == "Bzero") barTag = "barB0";
    else if (def->key == "Bs0") barTag = "barBs0";
    else if (def->key == "Bcplus") barTag = "Bcminus";
    else if (def->key == "Lambdab") barTag = "barLambdab";
    else if (def->key == "SigmabPlus") barTag = "barSigmabMinus";
    else if (def->key == "SigmabZero") barTag = "barSigmabZero";
    else if (def->key == "SigmabMinus") barTag = "barSigmabPlus";
    else if (def->key == "XibZero") barTag = "barXibZero";
    else if (def->key == "XibMinus") barTag = "barXibPlus";
    else if (def->key == "OmegabMinus") barTag = "barOmegabPlus";

    requests.push_back(MakeRequest(def,
                                   kPreferParticle,
                                   particleTag.Data(),
                                   def->fallbackParticleLabel.Data()));
    requests.push_back(MakeRequest(def,
                                   kPreferBar,
                                   barTag.Data(),
                                   def->fallbackBarLabel.Data()));
    requests.push_back(MakeRequest(def,
                                   kPreferDirect,
                                   combinedTag.Data(),
                                   def->fallbackDirectLabel.Data()));
}

std::vector<HistogramRequest> BuildRequestsForFlavor(const TString& flavorTag,
                                                     bool includeHeavyBeautyExtras)
{
    std::vector<HistogramRequest> requests;
    std::vector<ParticleDef>& defs = PersistentParticleDefs();

    if (flavorTag == "Charm") {
        AppendRequestsForKey(requests, defs, "Dzero");
        AppendRequestsForKey(requests, defs, "Dplus");
        AppendRequestsForKey(requests, defs, "Dsplus");
        AppendRequestsForKey(requests, defs, "Lambdac");
        return requests;
    }

    AppendRequestsForKey(requests, defs, "Bplus");
    AppendRequestsForKey(requests, defs, "Bzero");
    AppendRequestsForKey(requests, defs, "Bs0");
    AppendRequestsForKey(requests, defs, "Bcplus");
    AppendRequestsForKey(requests, defs, "Lambdab");

    if (includeHeavyBeautyExtras) {
        AppendRequestsForKey(requests, defs, "SigmabPlus");
        AppendRequestsForKey(requests, defs, "SigmabZero");
        AppendRequestsForKey(requests, defs, "SigmabMinus");
        AppendRequestsForKey(requests, defs, "XibZero");
        AppendRequestsForKey(requests, defs, "XibMinus");
        AppendRequestsForKey(requests, defs, "OmegabMinus");
    }

    return requests;
}

std::vector<HistogramRequest> FilterRequestsByMode(const std::vector<HistogramRequest>& requests,
                                                   RequestMode mode)
{
    std::vector<HistogramRequest> filtered;
    for (const HistogramRequest& request : requests) {
        if (request.mode == mode) filtered.push_back(request);
    }
    return filtered;
}

TH2* GetHistogramForRequest(TFile* file,
                            const HistogramRequest& request,
                            const char* cloneName)
{
    if (!file || !request.def) return nullptr;

    if (request.mode == kPreferParticle) {
        if (TH2* split = GetSplitHist(file, request.def->splitBases, true, cloneName)) return split;
        return GetDirectHist(file, request.def->directNames, cloneName);
    }

    if (request.mode == kPreferBar) {
        return GetSplitHist(file, request.def->splitBases, false, cloneName);
    }

    if (TH2* direct = GetDirectHist(file, request.def->directNames, cloneName)) return direct;
    return GetCombinedFromSplitPair(file, request.def->splitBases, cloneName);
}

TString DetermineDisplayLabel(TFile* file, const HistogramRequest& request)
{
    if (!file || !request.def) return request.fallbackLabel;

    if (request.mode == kPreferParticle) {
        if (TH2* split = GetSplitHist(file, request.def->splitBases, true)) {
            return LabelFromTitle(split->GetTitle(), request.fallbackLabel.Data());
        }
        if (TH2* direct = GetDirectHist(file, request.def->directNames)) {
            return LabelFromTitle(direct->GetTitle(), request.fallbackLabel.Data());
        }
        return request.fallbackLabel;
    }

    if (request.mode == kPreferBar) {
        if (TH2* split = GetSplitHist(file, request.def->splitBases, false)) {
            return LabelFromTitle(split->GetTitle(), request.fallbackLabel.Data());
        }
        return request.fallbackLabel;
    }

    if (TH2* direct = GetDirectHist(file, request.def->directNames)) {
        return LabelFromTitle(direct->GetTitle(), request.fallbackLabel.Data());
    }

    if (TH2* combined = GetCombinedFromSplitPair(file, request.def->splitBases, "tmpCombined")) {
        const TString label = LabelFromTitle(combined->GetTitle(),
                                             request.fallbackLabel.Data());
        delete combined;
        return label;
    }

    return request.fallbackLabel;
}

TString ResolvePrefixForFlavor(const TString& dateTag,
                               const TString& flavorTag,
                               const char* tuneTag)
{
    if (flavorTag == "Charm") {
        return PlotPathUtils::ResolveAnalyzedPrefix(
            dateTag,
            "Charm",
            {TString::Format("hf_%s_sub", tuneTag),
             TString::Format("ccbar_%s_sub", tuneTag)}
        );
    }

    return PlotPathUtils::ResolveAnalyzedPrefix(
        dateTag,
        "Beauty",
        {TString::Format("hf_%s_sub", tuneTag),
         TString::Format("bbbar_%s_sub", tuneTag)}
    );
}

bool LoadSamples(const char* prefix,
                 int nSub,
                 const char* label,
                 std::vector<LoadedSample>& samples)
{
    samples.assign(nSub, LoadedSample());

    bool ok = true;
    for (int i = 0; i < nSub; ++i) {
        const TString fileName = TString::Format("%s%d.root", prefix, i);
        TFile* file = TFile::Open(fileName, "READ");
        if (!file || file->IsZombie()) {
            std::cout << "Error opening " << label << " file " << fileName << "\n";
            ok = false;
            if (file) {
                file->Close();
                delete file;
            }
            continue;
        }

        TH1* mult = GetMultiplicityHist(file);
        if (!mult) {
            std::cout << "Missing multiplicity histogram in " << fileName
                      << " (expected fHistTaggedMultiplicity or fHistMultiplicity)\n";
            file->Close();
            delete file;
            ok = false;
            continue;
        }

        samples[i].file = file;
        samples[i].mult = mult;
        samples[i].taggedMult = GetTaggedMultiplicityHist(file);
    }

    return ok;
}

void CloseSamples(std::vector<LoadedSample>& samples)
{
    for (LoadedSample& sample : samples) {
        if (!sample.file) continue;
        sample.file->Close();
        delete sample.file;
        sample.file = nullptr;
        sample.mult = nullptr;
        sample.taggedMult = nullptr;
    }
}

std::pair<int, int> PercentileRange(TH1* hMult, double pTop, double pBot)
{
    if (!hMult) return {1, 1};

    const int nBins = hMult->GetNbinsX();
    const double total = hMult->Integral(1, nBins);
    if (total <= 0.0) return {1, nBins};

    const double thrTop = total * (pTop / 100.0);
    const double thrBot = total * (pBot / 100.0);

    double cumulative = 0.0;
    int yHigh = nBins;
    int yLow = nBins;

    for (int bin = nBins; bin >= 1; --bin) {
        cumulative += hMult->GetBinContent(bin);
        if (cumulative >= thrTop) {
            yHigh = bin;
            break;
        }
    }

    for (int bin = yHigh; bin >= 1; --bin) {
        if (cumulative >= thrBot) {
            yLow = bin;
            break;
        }
        cumulative += hMult->GetBinContent(bin - 1);
    }

    if (yLow > yHigh) std::swap(yLow, yHigh);
    return {yLow, yHigh};
}

TH1D* BuildSpectrumOneSub(TH2* source,
                          std::pair<int, int> yRange,
                          const char* name,
                          const char* xTitle,
                          const char* yTitle)
{
    if (!source) return nullptr;

    TH1D* projected = source->ProjectionX(Form("%s_proj", name),
                                          yRange.first,
                                          yRange.second,
                                          "e");
    if (!projected) return nullptr;

    TH1D* hist = dynamic_cast<TH1D*>(projected->Clone(name));
    delete projected;
    if (!hist) return nullptr;

    hist->SetDirectory(nullptr);
    hist->SetTitle("");
    hist->GetXaxis()->SetTitle(xTitle);
    hist->GetYaxis()->SetTitle(yTitle);
    PlotErrorUtils::EnsureSumw2(hist);
    PlotErrorUtils::NormalizeToUnitShape(hist);
    return hist;
}

TH1D* BuildMinimumBiasSpectrumOneSub(TH2* source,
                                     const char* name,
                                     const char* xTitle,
                                     const char* yTitle)
{
    if (!source) return nullptr;

    TH1D* projected = source->ProjectionX(Form("%s_proj", name),
                                          1,
                                          source->GetNbinsY(),
                                          "e");
    if (!projected) return nullptr;

    TH1D* hist = dynamic_cast<TH1D*>(projected->Clone(name));
    delete projected;
    if (!hist) return nullptr;

    hist->SetDirectory(nullptr);
    hist->SetTitle("");
    hist->GetXaxis()->SetTitle(xTitle);
    hist->GetYaxis()->SetTitle(yTitle);
    PlotErrorUtils::EnsureSumw2(hist);
    PlotErrorUtils::NormalizeToUnitShape(hist);
    return hist;
}

TH1D* CombineSubsampleTH1D(const std::vector<TH1D*>& hists,
                           const char* name,
                           const char* title = nullptr)
{
    TH1D* ref = nullptr;
    for (TH1D* hist : hists) {
        if (hist) {
            ref = hist;
            break;
        }
    }
    if (!ref) return nullptr;

    TH1D* combined = dynamic_cast<TH1D*>(ref->Clone(name));
    if (!combined) return nullptr;

    combined->SetDirectory(nullptr);
    combined->Reset("ICES");
    PlotErrorUtils::EnsureSumw2(combined);
    if (title) combined->SetTitle(title);

    for (int bin = 1; bin <= ref->GetNbinsX(); ++bin) {
        std::vector<double> values;
        values.reserve(hists.size());

        for (TH1D* hist : hists) {
            if (!hist) continue;
            values.push_back(hist->GetBinContent(bin));
        }

        if (values.empty()) continue;

        double mean = 0.0;
        for (double value : values) mean += value;
        mean /= static_cast<double>(values.size());

        double sem = 0.0;
        if (values.size() > 1) {
            double var = 0.0;
            for (double value : values) var += (value - mean) * (value - mean);
            sem = std::sqrt(var / (values.size() * (values.size() - 1)));
        }

        combined->SetBinContent(bin, mean);
        combined->SetBinError(bin, sem);
    }

    return combined;
}

TH2* CombineSubsampleTH2(const std::vector<TH2*>& hists,
                         const char* name,
                         const char* title = nullptr)
{
    TH2* ref = nullptr;
    for (TH2* hist : hists) {
        if (hist) {
            ref = hist;
            break;
        }
    }
    if (!ref) return nullptr;

    TH2* combined = dynamic_cast<TH2*>(ref->Clone(name));
    if (!combined) return nullptr;

    combined->SetDirectory(nullptr);
    combined->Reset("ICES");
    PlotErrorUtils::EnsureSumw2(combined);
    if (title) combined->SetTitle(title);

    for (int xBin = 1; xBin <= ref->GetNbinsX(); ++xBin) {
        for (int yBin = 1; yBin <= ref->GetNbinsY(); ++yBin) {
            std::vector<double> values;
            values.reserve(hists.size());

            for (TH2* hist : hists) {
                if (!hist) continue;
                values.push_back(hist->GetBinContent(xBin, yBin));
            }

            if (values.empty()) continue;

            double mean = 0.0;
            for (double value : values) mean += value;
            mean /= static_cast<double>(values.size());

            double sem = 0.0;
            if (values.size() > 1) {
                double var = 0.0;
                for (double value : values) var += (value - mean) * (value - mean);
                sem = std::sqrt(var / (values.size() * (values.size() - 1)));
            }

            combined->SetBinContent(xBin, yBin, mean);
            combined->SetBinError(xBin, yBin, sem);
        }
    }

    return combined;
}

std::vector<TH2*> BuildSubsampleSource2DForRequest(const HistogramRequest& request,
                                                   const std::vector<LoadedSample>& samples)
{
    std::vector<TH2*> perSub(samples.size(), nullptr);

    for (size_t iSub = 0; iSub < samples.size(); ++iSub) {
        const LoadedSample& sample = samples[iSub];
        if (!sample.file) continue;

        perSub[iSub] = GetHistogramForRequest(sample.file,
                                              request,
                                              Form("h2_%s_sub%d",
                                                   request.outputTag.Data(),
                                                   static_cast<int>(iSub)));
    }

    return perSub;
}

std::vector<TH2*> BuildSubsampleSource2DForAggregate(const std::vector<HistogramRequest>& requests,
                                                     const TString& outputTag,
                                                     const std::vector<LoadedSample>& samples)
{
    std::vector<TH2*> perSub(samples.size(), nullptr);

    for (size_t iSub = 0; iSub < samples.size(); ++iSub) {
        const LoadedSample& sample = samples[iSub];
        if (!sample.file) continue;

        TH2* sum = nullptr;
        for (const HistogramRequest& request : requests) {
            TH2* hist = GetHistogramForRequest(sample.file,
                                              request,
                                              Form("h2_%s_sub%d_%s",
                                                   outputTag.Data(),
                                                   static_cast<int>(iSub),
                                                   request.outputTag.Data()));
            if (!hist) continue;

            if (!sum) {
                sum = hist;
            } else {
                PlotErrorUtils::EnsureSumw2(sum);
                sum->Add(hist);
                delete hist;
            }
        }

        perSub[iSub] = sum;
    }

    return perSub;
}

TH1D* BuildCombinedMinimumBiasSpectrum(const std::vector<TH2*>& perSub,
                                       const char* name,
                                       const char* title,
                                       const char* xTitle,
                                       const char* yTitle)
{
    std::vector<TH1D*> spectra;
    spectra.reserve(perSub.size());

    for (size_t iSub = 0; iSub < perSub.size(); ++iSub) {
        TH2* source = perSub[iSub];
        if (!source) continue;

        TH1D* spectrum = BuildMinimumBiasSpectrumOneSub(source,
                                                        Form("%s_sub%d",
                                                             name,
                                                             static_cast<int>(iSub)),
                                                        xTitle,
                                                        yTitle);
        if (spectrum) spectra.push_back(spectrum);
    }

    TH1D* combined = CombineSubsampleTH1D(spectra, name, title);
    if (combined) {
        combined->GetXaxis()->SetTitle(xTitle);
        combined->GetYaxis()->SetTitle(yTitle);
    }

    for (TH1D* hist : spectra) delete hist;
    return combined;
}

TH1D* BuildCombinedClassSpectrum(const std::vector<TH2*>& perSub,
                                 const std::vector<LoadedSample>& samples,
                                 const ClassDef& cdef,
                                 const char* name,
                                 const char* title,
                                 const char* xTitle,
                                 const char* yTitle)
{
    std::vector<TH1D*> spectra;
    spectra.reserve(perSub.size());

    for (size_t iSub = 0; iSub < perSub.size() && iSub < samples.size(); ++iSub) {
        TH2* source = perSub[iSub];
        const LoadedSample& sample = samples[iSub];
        if (!source || !sample.mult) continue;

        TH1D* spectrum = BuildSpectrumOneSub(source,
                                             PercentileRange(sample.mult, cdef.pTop, cdef.pBot),
                                             Form("%s_sub%d",
                                                  name,
                                                  static_cast<int>(iSub)),
                                             xTitle,
                                             yTitle);
        if (spectrum) spectra.push_back(spectrum);
    }

    TH1D* combined = CombineSubsampleTH1D(spectra, name, title);
    if (combined) {
        combined->GetXaxis()->SetTitle(xTitle);
        combined->GetYaxis()->SetTitle(yTitle);
    }

    for (TH1D* hist : spectra) delete hist;
    return combined;
}

void DeleteTH2Vector(std::vector<TH2*>& hists)
{
    for (TH2* hist : hists) delete hist;
    hists.clear();
}

TDirectory* EnsureSubDir(TDirectory* parent, const char* name)
{
    if (!parent) return nullptr;

    if (TDirectory* existing = parent->GetDirectory(name)) return existing;
    return parent->mkdir(name);
}

void WriteNamed(TDirectory* dir, const char* name, const char* title)
{
    if (!dir) return;
    dir->cd();
    TNamed info(name, title);
    info.Write();
}

void WriteTH1D(TDirectory* dir, TH1D* hist, const char* name)
{
    if (!dir || !hist) return;
    dir->cd();
    hist->SetName(name);
    hist->Write();
}

void WriteTH2(TDirectory* dir, TH2* hist, const char* name)
{
    if (!dir || !hist) return;
    dir->cd();
    hist->SetName(name);
    hist->Write();
}

void BuildAndWriteRequestOutputs(const HistogramRequest& request,
                                 const TString& displayLabel,
                                 const std::vector<LoadedSample>& samples,
                                 TDirectory* source2DDir,
                                 TDirectory* minimumBiasDir,
                                 const std::vector<TDirectory*>& classDirs)
{
    std::vector<TH2*> perSub = BuildSubsampleSource2DForRequest(request, samples);

    TH2* combined2D = CombineSubsampleTH2(perSub,
                                          request.outputTag.Data(),
                                          displayLabel.Data());
    if (combined2D) WriteTH2(source2DDir, combined2D, request.outputTag.Data());

    TH1D* minimumBias = BuildCombinedMinimumBiasSpectrum(perSub,
                                                         request.outputTag.Data(),
                                                         displayLabel.Data(),
                                                         "p_{T} (GeV/c)",
                                                         "Normalized counts");
    if (minimumBias) WriteTH1D(minimumBiasDir, minimumBias, request.outputTag.Data());

    for (size_t iClass = 0; iClass < kClasses.size() && iClass < classDirs.size(); ++iClass) {
        const ClassDef& cdef = kClasses[iClass];
        TH1D* spectrum = BuildCombinedClassSpectrum(perSub,
                                                    samples,
                                                    cdef,
                                                    Form("%s_%s",
                                                         request.outputTag.Data(),
                                                         cdef.tag),
                                                    displayLabel.Data(),
                                                    "p_{T} (GeV/c)",
                                                    "Normalized counts");
        if (spectrum) WriteTH1D(classDirs[iClass], spectrum, request.outputTag.Data());
        delete spectrum;
    }

    delete combined2D;
    delete minimumBias;
    DeleteTH2Vector(perSub);
}

void BuildAndWriteAggregateOutputs(const std::vector<HistogramRequest>& aggregateRequests,
                                   const TString& outputTag,
                                   const TString& displayLabel,
                                   const std::vector<LoadedSample>& samples,
                                   TDirectory* source2DDir,
                                   TDirectory* minimumBiasDir,
                                   const std::vector<TDirectory*>& classDirs)
{
    if (aggregateRequests.empty()) return;

    std::vector<TH2*> perSub = BuildSubsampleSource2DForAggregate(aggregateRequests,
                                                                  outputTag,
                                                                  samples);

    TH2* combined2D = CombineSubsampleTH2(perSub,
                                          outputTag.Data(),
                                          displayLabel.Data());
    if (combined2D) WriteTH2(source2DDir, combined2D, outputTag.Data());

    TH1D* minimumBias = BuildCombinedMinimumBiasSpectrum(perSub,
                                                         outputTag.Data(),
                                                         displayLabel.Data(),
                                                         "p_{T} (GeV/c)",
                                                         "Normalized counts");
    if (minimumBias) WriteTH1D(minimumBiasDir, minimumBias, outputTag.Data());

    for (size_t iClass = 0; iClass < kClasses.size() && iClass < classDirs.size(); ++iClass) {
        const ClassDef& cdef = kClasses[iClass];
        TH1D* spectrum = BuildCombinedClassSpectrum(perSub,
                                                    samples,
                                                    cdef,
                                                    Form("%s_%s",
                                                         outputTag.Data(),
                                                         cdef.tag),
                                                    displayLabel.Data(),
                                                    "p_{T} (GeV/c)",
                                                    "Normalized counts");
        if (spectrum) WriteTH1D(classDirs[iClass], spectrum, outputTag.Data());
        delete spectrum;
    }

    delete combined2D;
    delete minimumBias;
    DeleteTH2Vector(perSub);
}

void BuildAndWriteMultiplicityOutputs(const std::vector<LoadedSample>& samples,
                                      TDirectory* multiplicityDir)
{
    std::vector<TH1D*> inclusiveMults;
    std::vector<TH1D*> taggedMults;
    inclusiveMults.reserve(samples.size());
    taggedMults.reserve(samples.size());

    for (size_t iSub = 0; iSub < samples.size(); ++iSub) {
        const LoadedSample& sample = samples[iSub];
        if (sample.mult) {
            TH1D* clone = CloneTH1D(sample.mult,
                                    Form("fHistMultiplicity_sub%d",
                                         static_cast<int>(iSub)));
            if (clone) inclusiveMults.push_back(clone);
        }

        TH1* taggedSource = sample.taggedMult ? sample.taggedMult : sample.mult;
        if (taggedSource) {
            TH1D* clone = CloneTH1D(taggedSource,
                                    Form("fHistTaggedMultiplicity_sub%d",
                                         static_cast<int>(iSub)));
            if (clone) taggedMults.push_back(clone);
        }
    }

    TH1D* combinedMult = CombineSubsampleTH1D(inclusiveMults,
                                              "fHistMultiplicity",
                                              "Multiplicity");
    TH1D* combinedTaggedMult = CombineSubsampleTH1D(taggedMults,
                                                    "fHistTaggedMultiplicity",
                                                    "Tagged multiplicity");

    if (combinedMult) WriteTH1D(multiplicityDir, combinedMult, "fHistMultiplicity");
    if (combinedTaggedMult) WriteTH1D(multiplicityDir,
                                      combinedTaggedMult,
                                      "fHistTaggedMultiplicity");

    delete combinedMult;
    delete combinedTaggedMult;
    for (TH1D* hist : inclusiveMults) delete hist;
    for (TH1D* hist : taggedMults) delete hist;
}

bool BuildFlavorTuneContent(const TString& dateTag,
                            const TString& flavorTag,
                            const char* tuneTag,
                            int nSub,
                            bool includeHeavyBeautyExtras,
                            TDirectory* outFile)
{
    const TString prefix = ResolvePrefixForFlavor(dateTag, flavorTag, tuneTag);
    if (prefix.IsNull()) {
        std::cout << "Could not resolve input prefix for " << flavorTag
                  << ", " << tuneTag << "\n";
        return false;
    }

    std::vector<LoadedSample> samples;
    const TString sampleLabel = flavorTag + " " + tuneTag;
    if (!LoadSamples(prefix.Data(), nSub, sampleLabel.Data(), samples)) {
        std::cout << "Continuing with available " << sampleLabel << " subsamples.\n";
    }

    TDirectory* flavorDir = EnsureSubDir(outFile, flavorTag.Data());
    TDirectory* tuneDir = EnsureSubDir(flavorDir, tuneTag);
    TDirectory* metadataDir = EnsureSubDir(tuneDir, "Metadata");
    TDirectory* multiplicityDir = EnsureSubDir(tuneDir, "Multiplicity");
    TDirectory* source2DDir = EnsureSubDir(tuneDir, "Source2D");
    TDirectory* spectraDir = EnsureSubDir(tuneDir, "Spectra");
    TDirectory* minimumBiasDir = EnsureSubDir(spectraDir, "MinimumBias");
    TDirectory* byMultDir = EnsureSubDir(spectraDir, "ByMultiplicity");

    std::vector<TDirectory*> classDirs;
    classDirs.reserve(kClasses.size());
    for (const ClassDef& cdef : kClasses) {
        classDirs.push_back(EnsureSubDir(byMultDir, cdef.tag));
    }

    WriteNamed(metadataDir, "DateTag", dateTag.Data());
    WriteNamed(metadataDir, "TuneTag", tuneTag);
    WriteNamed(metadataDir, "FlavorTag", flavorTag.Data());
    WriteNamed(metadataDir,
               "CombinationRule",
               "All stored bins are mean content across subsamples with SEM as bin error. "
               "The 1D spectra are built from one normalized projection per subsample before averaging.");

    TString selectedSpeciesText = "Default light-hadron content";
    if (flavorTag == "Beauty" && includeHeavyBeautyExtras) {
        selectedSpeciesText += " + heavy beauty baryons";
    }
    WriteNamed(metadataDir, "SelectedSpecies", selectedSpeciesText.Data());

    BuildAndWriteMultiplicityOutputs(samples, multiplicityDir);

    const std::vector<HistogramRequest> requests =
        BuildRequestsForFlavor(flavorTag, includeHeavyBeautyExtras);

    TFile* labelFile = nullptr;
    for (const LoadedSample& sample : samples) {
        if (sample.file) {
            labelFile = sample.file;
            break;
        }
    }

    for (const HistogramRequest& request : requests) {
        const TString label = DetermineDisplayLabel(labelFile, request);
        BuildAndWriteRequestOutputs(request,
                                    label,
                                    samples,
                                    source2DDir,
                                    minimumBiasDir,
                                    classDirs);
    }

    const std::vector<HistogramRequest> particleRequests =
        FilterRequestsByMode(requests, kPreferParticle);
    const std::vector<HistogramRequest> barRequests =
        FilterRequestsByMode(requests, kPreferBar);
    const std::vector<HistogramRequest> combinedRequests =
        FilterRequestsByMode(requests, kPreferDirect);

    BuildAndWriteAggregateOutputs(particleRequests,
                                  "AllParticlesParticle",
                                  "All selected particles",
                                  samples,
                                  source2DDir,
                                  minimumBiasDir,
                                  classDirs);
    BuildAndWriteAggregateOutputs(barRequests,
                                  "AllParticlesBar",
                                  "All selected antiparticles",
                                  samples,
                                  source2DDir,
                                  minimumBiasDir,
                                  classDirs);
    BuildAndWriteAggregateOutputs(combinedRequests,
                                  "AllParticlesCombined",
                                  "All selected particles and antiparticles",
                                  samples,
                                  source2DDir,
                                  minimumBiasDir,
                                  classDirs);

    CloseSamples(samples);
    return true;
}

TString DefaultOutputPath(const TString& dateTag)
{
    return PlotPathUtils::GetAnalyzedDataDir() + "/" + dateTag
         + "/hf_combined_plot_histograms.root";
}

} // namespace

void runHFCombinedSubsamplesFile(const char* dateTag = "",
                                 int nSub = 10,
                                 bool includeHeavyBeautyExtras = false,
                                 const char* outputPath = "")
{
    gROOT->SetBatch(kTRUE);

    const TString resolvedDate = PlotPathUtils::ResolveAnalysisDate(dateTag);
    if (resolvedDate.IsNull()) return;

    TString outPath = outputPath ? TString(outputPath) : TString("");
    outPath = outPath.Strip(TString::kBoth);
    if (outPath.IsNull()) outPath = DefaultOutputPath(resolvedDate);

    if (!gSystem->IsAbsoluteFileName(outPath.Data())) {
        outPath = gSystem->ConcatFileName(gSystem->WorkingDirectory(), outPath.Data());
    }
    outPath = gSystem->UnixPathName(outPath);

    const TString outDir = gSystem->DirName(outPath.Data());
    gSystem->mkdir(outDir, true);

    TFile* outFile = TFile::Open(outPath, "RECREATE");
    if (!outFile || outFile->IsZombie()) {
        std::cout << "Could not create output file: " << outPath << "\n";
        if (outFile) {
            outFile->Close();
            delete outFile;
        }
        return;
    }

    WriteNamed(outFile,
               "FileDescription",
               "Heavy-flavour subsamples combined into mean+-SEM histograms for plot-ready spectra.");

    bool wroteAnything = false;
    wroteAnything |= BuildFlavorTuneContent(resolvedDate,
                                            "Charm",
                                            "MONASH",
                                            nSub,
                                            includeHeavyBeautyExtras,
                                            outFile);
    wroteAnything |= BuildFlavorTuneContent(resolvedDate,
                                            "Charm",
                                            "JUNCTIONS",
                                            nSub,
                                            includeHeavyBeautyExtras,
                                            outFile);
    wroteAnything |= BuildFlavorTuneContent(resolvedDate,
                                            "Charm",
                                            "CLOSEPACKING",
                                            nSub,
                                            includeHeavyBeautyExtras,
                                            outFile);
    wroteAnything |= BuildFlavorTuneContent(resolvedDate,
                                            "Beauty",
                                            "MONASH",
                                            nSub,
                                            includeHeavyBeautyExtras,
                                            outFile);
    wroteAnything |= BuildFlavorTuneContent(resolvedDate,
                                            "Beauty",
                                            "JUNCTIONS",
                                            nSub,
                                            includeHeavyBeautyExtras,
                                            outFile);
    wroteAnything |= BuildFlavorTuneContent(resolvedDate,
                                            "Beauty",
                                            "CLOSEPACKING",
                                            nSub,
                                            includeHeavyBeautyExtras,
                                            outFile);

    outFile->Write();
    outFile->Close();
    delete outFile;

    if (wroteAnything) {
        std::cout << "Wrote combined HF plot-input file to:\n  "
                  << outPath << "\n";
    } else {
        std::cout << "No content was written to " << outPath << "\n";
    }
}

// Filename-matching entry point so ACLiC + syntax works from the shell:
//   root -l -b -q 'PlottingScripts/PtMultiplicity/Build_HF_CombinedSubsamplesFile.C+("08-04-2026_100M_Separate",10)'
void Build_HF_CombinedSubsamplesFile(const char* dateTag = "",
                                     int nSub = 10,
                                     bool includeHeavyBeautyExtras = false,
                                     const char* outputPath = "")
{
    runHFCombinedSubsamplesFile(dateTag, nSub, includeHeavyBeautyExtras, outputPath);
}
