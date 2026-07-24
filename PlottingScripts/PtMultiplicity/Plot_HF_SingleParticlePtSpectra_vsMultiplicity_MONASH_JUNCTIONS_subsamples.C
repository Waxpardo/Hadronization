// ---------------------------------------------------------------------------
// Plot_HF_SingleParticlePtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C
//
// For one selected hadron species, produce one wide comparison canvas with:
//   - MONASH on the left
//   - JUNCTIONS on the right
//
// Each tune panel overlays the five multiplicity-percentile spectra:
//   80-100%, 60-80%, 40-60%, 20-40%, 0-20%
// ordered from lowest to highest multiplicity.
//
// The spectra are built from the analyzed ROOT subsamples in AnalyzedData and
// the uncertainties are computed as mean ± SEM across subsamples, bin by bin.
//
// Charge handling:
//   - For positive-species requests such as Dplus or Bplus, the macro prefers
//     split Particle histograms when available and otherwise falls back to the
//     direct histogram stored in the file.
//   - For anti-particle requests such as Dminus or Bminus, split Bar
//     histograms are required.
//   - Combined aliases such as Dpm or Bpm use the direct histogram first and
//     otherwise sum Particle + Bar when both exist.
//
// If a flavor selector is passed instead, the macro loops over all particles of
// that flavor and produces one side-by-side comparison canvas for each particle.
//
// Example usage:
//   .L "PlottingScripts/PtMultiplicity/Plot_HF_SingleParticlePtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C"
//   runHFSingleParticleSpectra("27-03-2026", "Dzero", 10);
//   runHFSingleParticleSpectra("27-03-2026", "Bplus", 10);
//   runHFSingleParticleSpectra("27-03-2026", "Dminus", 10);
//   runHFSingleParticleSpectra("27-03-2026", "Charm", 10);
//   runHFSingleParticleSpectra("27-03-2026", "Beauty", 10);
//
// ---------------------------------------------------------------------------

#include <algorithm>
#include <cctype>
#include <cmath>
#include <iostream>
#include <utility>
#include <vector>

#include "TCanvas.h"
#include "TFile.h"
#include "TH1.h"
#include "TH1D.h"
#include "TH2.h"
#include "TLegend.h"
#include "TLatex.h"
#include "TPad.h"
#include "TROOT.h"
#include "TString.h"
#include "TStyle.h"

#include "PlottingPathUtils.h"
#include "../HistogramErrorUtils.h"

namespace {

struct PlotPathBootstrap {
    PlotPathBootstrap() { PlotPathUtils::RegisterMacroPath(__FILE__); }
} gPlotPathBootstrap;

struct CDef {
    double pTop;
    double pBot;
    const char* tag;
    const char* label;
};

struct StyleDef {
    int color;
    int lstyle;
    int lwidth;
    int marker;
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
    std::vector<TString> directAliases;
    std::vector<TString> particleAliases;
    std::vector<TString> barAliases;
    TString fallbackDirectLabel;
    TString fallbackParticleLabel;
    TString fallbackBarLabel;
};

struct ResolvedParticleRequest {
    const ParticleDef* def;
    RequestMode mode;
    TString outputTag;

    ResolvedParticleRequest() : def(nullptr), mode(kPreferDirect), outputTag("") {}
};

struct LoadedSample {
    TFile* file;
    TH1* mult;

    LoadedSample() : file(nullptr), mult(nullptr) {}
};

static const std::vector<CDef> kClasses = {
    { 80,100, "80_100", "80-100%" },
    { 60, 80, "60_80",  "60-80%"  },
    { 40, 60, "40_60",  "40-60%"  },
    { 20, 40, "20_40",  "20-40%"  },
    {  0, 20, "0_20",   "0-20%"   }
};

static const StyleDef kStyle[5] = {
    { kOrange + 7, 1, 2, 20 },
    { kViolet + 1, 1, 2, 21 },
    { kGreen + 2,  1, 2, 22 },
    { kRed + 1,    1, 2, 23 },
    { kBlue + 1,   1, 2, 33 }
};

static const double kFixedXMax = 0.0;

TString NormalizeFlavorTag(const char* flavorTag)
{
    TString flavor = flavorTag ? TString(flavorTag) : TString("");
    flavor = flavor.Strip(TString::kBoth);
    flavor.ToUpper();

    if (flavor == "CHARM" || flavor == "C") return "Charm";
    if (flavor == "BEAUTY" || flavor == "B") return "Beauty";

    return "";
}

void SetStyle()
{
    gStyle->SetOptStat(0);
    gStyle->SetOptTitle(0);
    gStyle->SetLegendBorderSize(0);
    gStyle->SetErrorX(0.0);
}

template<class T>
T* GetObj(TFile* file, const char* name)
{
    return file ? dynamic_cast<T*>(file->Get(name)) : nullptr;
}

TH1* GetMultiplicityHist(TFile* file)
{
    if (TH1* hTagged = GetObj<TH1>(file, "fHistTaggedMultiplicity")) return hTagged;
    return GetObj<TH1>(file, "fHistMultiplicity");
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

TString NormalizeSelector(const char* raw)
{
    TString token = raw ? TString(raw) : TString("");
    token.ToLower();

    token.ReplaceAll("#bar{", "bar");
    token.ReplaceAll("\\bar{", "bar");
    token.ReplaceAll("bar{", "bar");
    token.ReplaceAll("#", "");
    token.ReplaceAll("\\", "");
    token.ReplaceAll("{", "");
    token.ReplaceAll("}", "");
    token.ReplaceAll("^", "");
    token.ReplaceAll("_", "");
    token.ReplaceAll("/", "");
    token.ReplaceAll("(", "");
    token.ReplaceAll(")", "");
    token.ReplaceAll(" ", "");
    token.ReplaceAll("+", "plus");
    token.ReplaceAll("-", "minus");

    TString cleaned = "";
    for (int i = 0; i < token.Length(); ++i) {
        const char ch = token[i];
        if (std::isalnum(static_cast<unsigned char>(ch))) cleaned.Append(ch);
    }

    return cleaned;
}

bool MatchesAnyAlias(const TString& normalizedToken,
                     const std::vector<TString>& aliases)
{
    for (const TString& alias : aliases) {
        if (normalizedToken == NormalizeSelector(alias.Data())) return true;
    }

    return false;
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

ParticleDef MakeParticleDef(const char* key,
                            const char* flavorDir,
                            const std::vector<TString>& directNames,
                            const std::vector<TString>& splitBases,
                            const std::vector<TString>& directAliases,
                            const std::vector<TString>& particleAliases,
                            const std::vector<TString>& barAliases,
                            const char* fallbackDirectLabel,
                            const char* fallbackParticleLabel,
                            const char* fallbackBarLabel)
{
    ParticleDef def;
    def.key = key;
    def.flavorDir = flavorDir;
    def.directNames = directNames;
    def.splitBases = splitBases;
    def.directAliases = directAliases;
    def.particleAliases = particleAliases;
    def.barAliases = barAliases;
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
        {"d0pair", "dzero", "d0", "dzerocombined", "d0combined", "d0paircombined"},
        {"dzero", "d0", "dzeroparticle", "d0particle"},
        {"bardzero", "bard0", "dzerobar", "d0bar", "dbar0"},
        "D^{0}/#bar{D}^{0}",
        "D^{0}",
        "#bar{D}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "Dplus", "Charm",
        {"fHistPtDplus"}, {"fHistPtDplus"},
        {"dpm", "dplusminus", "dpmcombined", "dpluscombined"},
        {"dplus", "dplusparticle"},
        {"dminus", "dplusbar", "dminusparticle"},
        "D^{#pm}",
        "D^{+}",
        "D^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "Dsplus", "Charm",
        {"fHistPtDsplus"}, {"fHistPtDsplus"},
        {"dspm", "dscombined", "dspluscombined"},
        {"dsplus", "ds", "dsplusparticle"},
        {"dsminus", "dsbar"},
        "D_{s}^{#pm}",
        "D_{s}^{+}",
        "D_{s}^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "Lambdac", "Charm",
        {"fHistPtLambdac", "fHistPtLambdacPlus"}, {"fHistPtLambdac"},
        {"lambdaccombined", "lccombined"},
        {"lambdac", "lc", "lambdacplus"},
        {"barlambdac", "lambdacbar", "lambdacminus", "barlc"},
        "#Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-}",
        "#Lambda_{c}^{+}",
        "#bar{#Lambda}_{c}^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "Bplus", "Beauty",
        {"fHistPtBplus"}, {"fHistPtBplus"},
        {"bpm", "bplusminus", "bpmcombined", "bpluscombined"},
        {"bplus", "bplusparticle"},
        {"bminus", "bplusbar"},
        "B^{#pm}",
        "B^{+}",
        "B^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "Bzero", "Beauty",
        {"fHistPtBzero"}, {"fHistPtBzero"},
        {"b0pair", "bzero", "b0", "bzerocombined", "b0combined"},
        {"bzero", "b0", "bzeroparticle", "b0particle"},
        {"barbzero", "barb0", "bzerobar", "b0bar"},
        "B^{0}/#bar{B}^{0}",
        "B^{0}",
        "#bar{B}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "Bs0", "Beauty",
        {"fHistPtBs0"}, {"fHistPtBs0"},
        {"bspair", "bs0combined", "bscombined"},
        {"bs0", "bs", "bszero", "bs0particle"},
        {"barbs0", "barbs", "bs0bar"},
        "B_{s}^{0}/#bar{B}_{s}^{0}",
        "B_{s}^{0}",
        "#bar{B}_{s}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "Bcplus", "Beauty",
        {"fHistPtBcplus"}, {"fHistPtBcplus"},
        {"bcpm", "bccombined", "bcpluscombined"},
        {"bcplus", "bc", "bcplusparticle"},
        {"bcminus", "bcbar"},
        "B_{c}^{#pm}",
        "B_{c}^{+}",
        "B_{c}^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "Lambdab", "Beauty",
        {"fHistPtLambdab"}, {"fHistPtLambdab"},
        {"lambdabcombined", "lbcombined"},
        {"lambdab", "lb", "lambdab0"},
        {"barlambdab", "lambdabbar", "barlb"},
        "#Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0}",
        "#Lambda_{b}^{0}",
        "#bar{#Lambda}_{b}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "SigmabPlus", "Beauty",
        {"fHistPtSigmabPlus"}, {"fHistPtSigmabPlus"},
        {"sigmabpluscombined"},
        {"sigmabplus"},
        {"barsigmabminus", "sigmabplusbar"},
        "#Sigma_{b}^{+}/#bar{#Sigma}_{b}^{-}",
        "#Sigma_{b}^{+}",
        "#bar{#Sigma}_{b}^{-}"
    ));

    defs.push_back(MakeParticleDef(
        "SigmabZero", "Beauty",
        {"fHistPtSigmabZero"}, {"fHistPtSigmabZero"},
        {"sigmabzerocombined"},
        {"sigmabzero"},
        {"barsigmabzero", "sigmabzerobar"},
        "#Sigma_{b}^{0}/#bar{#Sigma}_{b}^{0}",
        "#Sigma_{b}^{0}",
        "#bar{#Sigma}_{b}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "SigmabMinus", "Beauty",
        {"fHistPtSigmabMinus"}, {"fHistPtSigmabMinus"},
        {"sigmabminuscombined"},
        {"sigmabminus"},
        {"barsigmabplus", "sigmabminusbar"},
        "#Sigma_{b}^{-}/#bar{#Sigma}_{b}^{+}",
        "#Sigma_{b}^{-}",
        "#bar{#Sigma}_{b}^{+}"
    ));

    defs.push_back(MakeParticleDef(
        "XibZero", "Beauty",
        {"fHistPtXibZero"}, {"fHistPtXibZero"},
        {"xibzerocombined"},
        {"xibzero"},
        {"barxibzero", "xibzerobar"},
        "#Xi_{b}^{0}/#bar{#Xi}_{b}^{0}",
        "#Xi_{b}^{0}",
        "#bar{#Xi}_{b}^{0}"
    ));

    defs.push_back(MakeParticleDef(
        "XibMinus", "Beauty",
        {"fHistPtXibMinus"}, {"fHistPtXibMinus"},
        {"xibminuscombined"},
        {"xibminus"},
        {"barxibplus", "xibminusbar"},
        "#Xi_{b}^{-}/#bar{#Xi}_{b}^{+}",
        "#Xi_{b}^{-}",
        "#bar{#Xi}_{b}^{+}"
    ));

    defs.push_back(MakeParticleDef(
        "OmegabMinus", "Beauty",
        {"fHistPtOmegabMinus"}, {"fHistPtOmegabMinus"},
        {"omegabminuscombined"},
        {"omegabminus", "omegab"},
        {"baromegabplus", "omegabminusbar"},
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

const ParticleDef* FindParticleDefByKey(const std::vector<ParticleDef>& defs, const char* key)
{
    for (const ParticleDef& def : defs) {
        if (def.key == key) return &def;
    }
    return nullptr;
}

ResolvedParticleRequest ResolveParticleRequest(const char* particleTag)
{
    const TString normalizedToken = NormalizeSelector(particleTag);
    ResolvedParticleRequest request;
    std::vector<ParticleDef>& persistentDefs = PersistentParticleDefs();
    for (size_t i = 0; i < persistentDefs.size(); ++i) {
        const ParticleDef& def = persistentDefs[i];

        if (MatchesAnyAlias(normalizedToken, def.barAliases)) {
            request.def = &persistentDefs[i];
            request.mode = kPreferBar;
            request.outputTag = def.key + "Bar";
            return request;
        }

        if (MatchesAnyAlias(normalizedToken, def.directAliases)) {
            request.def = &persistentDefs[i];
            request.mode = kPreferDirect;
            request.outputTag = def.key + "Combined";
            return request;
        }

        if (MatchesAnyAlias(normalizedToken, def.particleAliases)) {
            request.def = &persistentDefs[i];
            request.mode = kPreferParticle;
            request.outputTag = def.key;
            return request;
        }
    }

    return request;
}

ResolvedParticleRequest MakeDefaultFlavorRequest(const ParticleDef& def)
{
    ResolvedParticleRequest request;
    request.def = &def;
    request.mode = kPreferParticle;
    request.outputTag = def.key;
    return request;
}

ResolvedParticleRequest MakeFlavorRequest(const ParticleDef* def,
                                         RequestMode mode,
                                         const char* outputTag)
{
    ResolvedParticleRequest request;
    if (!def) return request;

    request.def = def;
    request.mode = mode;
    request.outputTag = outputTag;
    return request;
}

void AppendFlavorRequest(std::vector<ResolvedParticleRequest>& requests,
                         const std::vector<ParticleDef>& defs,
                         const char* key,
                         RequestMode mode,
                         const char* outputTag)
{
    const ParticleDef* def = FindParticleDefByKey(defs, key);
    if (!def) return;
    requests.push_back(MakeFlavorRequest(def, mode, outputTag));
}

std::vector<ResolvedParticleRequest> BuildFlavorRequests(const TString& flavorTag,
                                                         bool includeHeavyBeautyExtras = false)
{
    std::vector<ResolvedParticleRequest> requests;
    std::vector<ParticleDef>& defs = PersistentParticleDefs();

    if (flavorTag == "Charm") {
        AppendFlavorRequest(requests, defs, "Dzero", kPreferParticle, "Dzero");
        AppendFlavorRequest(requests, defs, "Dzero", kPreferBar, "Dbar0");
        AppendFlavorRequest(requests, defs, "Dplus", kPreferParticle, "Dplus");
        AppendFlavorRequest(requests, defs, "Dplus", kPreferBar, "Dminus");
        AppendFlavorRequest(requests, defs, "Dsplus", kPreferParticle, "Dsplus");
        AppendFlavorRequest(requests, defs, "Dsplus", kPreferBar, "Dsminus");
        AppendFlavorRequest(requests, defs, "Lambdac", kPreferParticle, "Lambdac");
        AppendFlavorRequest(requests, defs, "Lambdac", kPreferBar, "barLambdac");
        return requests;
    }

    if (flavorTag == "Beauty") {
        AppendFlavorRequest(requests, defs, "Bplus", kPreferParticle, "Bplus");
        AppendFlavorRequest(requests, defs, "Bplus", kPreferBar, "Bminus");
        AppendFlavorRequest(requests, defs, "Bzero", kPreferParticle, "Bzero");
        AppendFlavorRequest(requests, defs, "Bzero", kPreferBar, "barB0");
        AppendFlavorRequest(requests, defs, "Bs0", kPreferParticle, "Bs0");
        AppendFlavorRequest(requests, defs, "Bs0", kPreferBar, "barBs0");
        AppendFlavorRequest(requests, defs, "Bcplus", kPreferParticle, "Bcplus");
        AppendFlavorRequest(requests, defs, "Bcplus", kPreferBar, "Bcminus");
        AppendFlavorRequest(requests, defs, "Lambdab", kPreferParticle, "Lambdab");
        AppendFlavorRequest(requests, defs, "Lambdab", kPreferBar, "barLambdab");

        if (includeHeavyBeautyExtras) {
            AppendFlavorRequest(requests, defs, "SigmabPlus", kPreferParticle, "SigmabPlus");
            AppendFlavorRequest(requests, defs, "SigmabPlus", kPreferBar, "barSigmabMinus");
            AppendFlavorRequest(requests, defs, "SigmabZero", kPreferParticle, "SigmabZero");
            AppendFlavorRequest(requests, defs, "SigmabZero", kPreferBar, "barSigmabZero");
            AppendFlavorRequest(requests, defs, "SigmabMinus", kPreferParticle, "SigmabMinus");
            AppendFlavorRequest(requests, defs, "SigmabMinus", kPreferBar, "barSigmabPlus");
            AppendFlavorRequest(requests, defs, "XibZero", kPreferParticle, "XibZero");
            AppendFlavorRequest(requests, defs, "XibZero", kPreferBar, "barXibZero");
            AppendFlavorRequest(requests, defs, "XibMinus", kPreferParticle, "XibMinus");
            AppendFlavorRequest(requests, defs, "XibMinus", kPreferBar, "barXibPlus");
            AppendFlavorRequest(requests, defs, "OmegabMinus", kPreferParticle, "OmegabMinus");
            AppendFlavorRequest(requests, defs, "OmegabMinus", kPreferBar, "barOmegabPlus");
        }
    }

    return requests;
}

void PrintAvailableParticles()
{
    std::cout
        << "Available particle selectors include:\n"
        << "  Charm  : Dzero, Dplus, Dsplus, Lambdac, Dminus, Dbar0, Dsminus, barLambdac, Dpm\n"
        << "  Beauty : Bplus, Bzero, Bs0, Bcplus, Lambdab,\n"
        << "           SigmabPlus, SigmabZero, SigmabMinus, XibZero, XibMinus, OmegabMinus,\n"
        << "           Bminus, barB0, barBs0, Bcminus, barLambdab, Bpm\n";
}

void PrintAvailableSelectors()
{
    std::cout << "Flavor selectors: Charm, Beauty\n"
              << "Default flavor loops use:\n"
              << "  Charm  : D0, #bar{D}0, D+, D-, Ds+, Ds-, #Lambda_c+, #bar{#Lambda}_c-\n"
              << "  Beauty : B+, B-, B0, #bar{B}0, Bs0, #bar{B}s0, Bc+, Bc-, #Lambda_b0, #bar{#Lambda}_b0\n"
              << "Heavier beauty baryons can be re-enabled with includeHeavyBeautyExtras = true.\n";
    PrintAvailableParticles();
}

TString DetermineDisplayLabel(TFile* file, const ResolvedParticleRequest& request)
{
    if (!request.def) return "";

    if (request.mode == kPreferParticle) {
        if (TH2* split = GetSplitHist(file, request.def->splitBases, true)) {
            return LabelFromTitle(split->GetTitle(), request.def->fallbackParticleLabel.Data());
        }

        if (TH2* direct = GetDirectHist(file, request.def->directNames)) {
            return LabelFromTitle(direct->GetTitle(), request.def->fallbackParticleLabel.Data());
        }

        return request.def->fallbackParticleLabel;
    }

    if (request.mode == kPreferBar) {
        if (TH2* split = GetSplitHist(file, request.def->splitBases, false)) {
            return LabelFromTitle(split->GetTitle(), request.def->fallbackBarLabel.Data());
        }

        return request.def->fallbackBarLabel;
    }

    if (TH2* direct = GetDirectHist(file, request.def->directNames)) {
        return LabelFromTitle(direct->GetTitle(), request.def->fallbackDirectLabel.Data());
    }

    if (TH2* combined = GetCombinedFromSplitPair(file, request.def->splitBases, nullptr)) {
        const TString label = LabelFromTitle(combined->GetTitle(),
                                             request.def->fallbackDirectLabel.Data());
        delete combined;
        return label;
    }

    return request.def->fallbackDirectLabel;
}

TH2* GetRequestedHist(TFile* file,
                      const ResolvedParticleRequest& request,
                      const char* cloneName)
{
    if (!request.def || !file) return nullptr;

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

        TH1* hMult = GetMultiplicityHist(file);
        if (!hMult) {
            std::cout << "Missing multiplicity histogram in " << fileName
                      << " (expected fHistTaggedMultiplicity or fHistMultiplicity)\n";
            file->Close();
            delete file;
            ok = false;
            continue;
        }

        samples[i].file = file;
        samples[i].mult = hMult;
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

TH1D* CombineSubsampleSpectra(const std::vector<TH1D*>& spectra,
                              const char* name,
                              const char* xTitle,
                              const char* yTitle)
{
    if (spectra.empty()) return nullptr;

    TH1D* ref = spectra.front();
    if (!ref) return nullptr;

    TH1D* combined = new TH1D(name,
                              "",
                              ref->GetNbinsX(),
                              ref->GetXaxis()->GetXmin(),
                              ref->GetXaxis()->GetXmax());
    combined->SetDirectory(nullptr);
    combined->GetXaxis()->SetTitle(xTitle);
    combined->GetYaxis()->SetTitle(yTitle);
    PlotErrorUtils::EnsureSumw2(combined);

    for (int bin = 1; bin <= ref->GetNbinsX(); ++bin) {
        std::vector<double> values;
        values.reserve(spectra.size());

        for (TH1D* hist : spectra) {
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

double AutoXMax(const std::vector<TH1D*>& curves, double marginFrac = 0.03)
{
    double xMax = 0.0;

    for (TH1D* hist : curves) {
        if (!hist) continue;

        for (int bin = hist->GetNbinsX(); bin >= 1; --bin) {
            if (hist->GetBinContent(bin) <= 0.0) continue;
            xMax = std::max(xMax, hist->GetXaxis()->GetBinUpEdge(bin));
            break;
        }
    }

    if (xMax <= 0.0) xMax = 10.0;
    return xMax * (1.0 + marginFrac);
}

std::vector<TH1D*> BuildTuneCurves(const ResolvedParticleRequest& request,
                                   const std::vector<LoadedSample>& samples,
                                   const char* xTitle,
                                   const char* yTitle)
{
    std::vector<TH1D*> curves;
    curves.reserve(kClasses.size());

    for (const CDef& cdef : kClasses) {
        std::vector<TH1D*> oneSubsamplePerFile;
        oneSubsamplePerFile.reserve(samples.size());

        for (size_t iSub = 0; iSub < samples.size(); ++iSub) {
            const LoadedSample& sample = samples[iSub];
            if (!sample.file || !sample.mult) continue;

            TH2* source = GetRequestedHist(sample.file,
                                           request,
                                           Form("h2_%s_sub%zu_%s",
                                                request.outputTag.Data(),
                                                iSub,
                                                cdef.tag));
            if (!source) continue;

            TH1D* spectrum = BuildSpectrumOneSub(
                source,
                PercentileRange(sample.mult, cdef.pTop, cdef.pBot),
                Form("h_%s_sub%zu_%s", request.outputTag.Data(), iSub, cdef.tag),
                xTitle,
                yTitle
            );
            delete source;

            if (spectrum) oneSubsamplePerFile.push_back(spectrum);
        }

        TH1D* combined = CombineSubsampleSpectra(
            oneSubsamplePerFile,
            Form("h_%s_%s", request.outputTag.Data(), cdef.tag),
            xTitle,
            yTitle
        );

        for (TH1D* hist : oneSubsamplePerFile) delete hist;
        curves.push_back(combined);
    }

    return curves;
}

void DeleteCurves(std::vector<TH1D*>& curves)
{
    for (TH1D* hist : curves) delete hist;
    curves.clear();
}

double FindGlobalYMax(const std::vector<TH1D*>& monashCurves,
                      const std::vector<TH1D*>& junctionCurves)
{
    double yMax = 0.0;

    for (size_t i = 0; i < monashCurves.size(); ++i) {
        TH1D* curves[] = {
            (i < monashCurves.size() ? monashCurves[i] : nullptr),
            (i < junctionCurves.size() ? junctionCurves[i] : nullptr)
        };

        for (TH1D* hist : curves) {
            if (!hist) continue;

            for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
                yMax = std::max(yMax, hist->GetBinContent(bin) + hist->GetBinError(bin));
            }
        }
    }

    return (yMax > 0.0 ? yMax : 1.0);
}

double FindGlobalYMinPositive(const std::vector<TH1D*>& monashCurves,
                              const std::vector<TH1D*>& junctionCurves)
{
    double yMinPositive = 1e9;

    for (size_t i = 0; i < monashCurves.size(); ++i) {
        TH1D* curves[] = {
            (i < monashCurves.size() ? monashCurves[i] : nullptr),
            (i < junctionCurves.size() ? junctionCurves[i] : nullptr)
        };

        for (TH1D* hist : curves) {
            if (!hist) continue;

            for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
                const double value = hist->GetBinContent(bin);
                if (value > 0.0) yMinPositive = std::min(yMinPositive, value);
            }
        }
    }

    return (yMinPositive < 1e9 ? yMinPositive : 1e-6);
}

void DrawSpectraPanel(const std::vector<TH1D*>& curves,
                      const char* tuneTag,
                      const char* particleLabel,
                      const char* dateTag,
                      double globalXMax,
                      double globalYMin,
                      double globalYMax,
                      bool isLeftPad)
{
    TPad* pad = dynamic_cast<TPad*>(gPad);
    if (!pad) return;

    pad->SetLogy();
    pad->SetTopMargin(0.22);
    pad->SetBottomMargin(0.13);
    pad->SetLeftMargin(isLeftPad ? 0.14 : 0.12);
    pad->SetRightMargin(0.05);
    pad->SetTicks(1, 1);

    TH1D* frame = nullptr;
    for (TH1D* hist : curves) {
        if (!hist) continue;
        frame = hist;
        break;
    }

    if (!frame) {
        TLatex latex;
        latex.SetNDC();
        latex.SetTextSize(0.054);
        latex.DrawLatex(0.14, 0.95, particleLabel);
        latex.DrawLatex(0.14, 0.88, tuneTag);
        latex.SetTextSize(0.040);
        latex.DrawLatex(0.14, 0.81, Form("Date: %s", dateTag));
        latex.DrawLatex(0.14, 0.72, "No entries");
    } else {
        frame->SetMinimum(globalYMin);
        frame->SetMaximum(1.8 * globalYMax);
        frame->GetXaxis()->SetRangeUser(0.0, globalXMax);
        frame->GetXaxis()->SetTitleSize(0.058);
        frame->GetYaxis()->SetTitleSize(0.058);
        frame->GetXaxis()->SetLabelSize(0.048);
        frame->GetYaxis()->SetLabelSize(0.048);
        frame->GetXaxis()->SetTitleOffset(1.0);
        frame->GetYaxis()->SetTitleOffset(isLeftPad ? 1.05 : 0.95);

        for (size_t i = 0; i < curves.size(); ++i) {
            TH1D* hist = curves[i];
            if (!hist) continue;

            hist->SetLineColor(kStyle[i].color);
            hist->SetLineStyle(kStyle[i].lstyle);
            hist->SetLineWidth(kStyle[i].lwidth);
            hist->SetFillStyle(0);
            hist->SetFillColor(0);
            hist->SetMarkerColor(kStyle[i].color);
            hist->SetMarkerStyle(kStyle[i].marker);
            hist->SetMarkerSize(0.9);
        }

        bool drewFirst = false;
        for (TH1D* hist : curves) {
            if (!hist) continue;
            hist->Draw(drewFirst ? "E1 X0 SAME" : "E1 X0");
            drewFirst = true;
        }

        TLatex latex;
        latex.SetNDC();
        latex.SetTextSize(0.052);
        latex.DrawLatex(0.14, 0.95, particleLabel);
        latex.DrawLatex(0.14, 0.88, tuneTag);
        latex.SetTextSize(0.040);
        latex.DrawLatex(0.14, 0.81, Form("Date: %s", dateTag));

        const double plotLeft = pad->GetLeftMargin();
        const double plotRight = 1.0 - pad->GetRightMargin();
        const double plotTop = 1.0 - pad->GetTopMargin();
        const double legendWidth = 0.30;
        const double legendHeight = 0.24;
        const double legendX2 = plotRight - 0.02;
        const double legendX1 = std::max(plotLeft + 0.06, legendX2 - legendWidth);
        const double legendY2 = plotTop - 0.035;
        const double legendY1 = std::max(pad->GetBottomMargin() + 0.18,
                                         legendY2 - legendHeight);

        TLegend* legend = new TLegend(legendX1, legendY1, legendX2, legendY2);
        legend->SetTextSize(0.036);
        legend->SetBorderSize(0);
        legend->SetFillStyle(0);
        legend->SetFillColorAlpha(0, 0.0);
        for (size_t i = 0; i < kClasses.size(); ++i) {
            if (!curves[i]) continue;
            legend->AddEntry(curves[i], kClasses[i].label, "ep");
        }
        legend->Draw();
    }
}

void DrawSpectraComparisonCanvas(const std::vector<TH1D*>& monashCurves,
                                 const std::vector<TH1D*>& junctionsCurves,
                                 const char* particleLabel,
                                 const char* dateTag,
                                 const char* outFileBase,
                                 double globalXMax,
                                 double globalYMin,
                                 double globalYMax)
{
    TCanvas* canvas = new TCanvas(Form("c_%s", outFileBase),
                                  outFileBase,
                                  1900,
                                  760);
    canvas->Divide(2, 1, 0.0, 0.0);

    canvas->cd(1);
    DrawSpectraPanel(monashCurves,
                     "MONASH",
                     particleLabel,
                     dateTag,
                     globalXMax,
                     globalYMin,
                     globalYMax,
                     true);

    canvas->cd(2);
    DrawSpectraPanel(junctionsCurves,
                     "JUNCTIONS",
                     particleLabel,
                     dateTag,
                     globalXMax,
                     globalYMin,
                     globalYMax,
                     false);

    const TString pngPath = PlotPathUtils::BuildPtMultiplicityPlotPath(
        TString::Format("%s.png", outFileBase));
    const TString pdfPath = PlotPathUtils::BuildPtMultiplicityPlotPath(
        TString::Format("%s.pdf", outFileBase));

    canvas->SaveAs(pngPath);
    canvas->SaveAs(pdfPath);

    std::cout << "Saved side-by-side particle spectrum canvas to:\n"
              << "  " << pngPath << "\n"
              << "  " << pdfPath << "\n";

    delete canvas;
}

TString ResolvePrefixForParticle(const TString& dateTag,
                                 const ParticleDef& def,
                                 const char* tuneTag)
{
    if (def.flavorDir == "Charm") {
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

bool GenerateSingleParticlePlots(const TString& resolvedDate,
                                 const ResolvedParticleRequest& request,
                                 int nSub)
{
    if (!request.def) return false;

    const TString monashPrefix = ResolvePrefixForParticle(resolvedDate, *request.def, "MONASH");
    const TString junctionsPrefix = ResolvePrefixForParticle(resolvedDate, *request.def, "JUNCTIONS");

    std::cout << "Single-particle HF spectra input date: " << resolvedDate << "\n";
    std::cout << "  Particle        : " << request.outputTag << "\n";
    std::cout << "  Flavor          : " << request.def->flavorDir << "\n";
    std::cout << "  MONASH prefix   : " << monashPrefix << "*.root\n";
    std::cout << "  JUNCTIONS prefix: " << junctionsPrefix << "*.root\n";

    std::vector<LoadedSample> monashSamples;
    std::vector<LoadedSample> junctionsSamples;

    const bool monashOk = LoadSamples(monashPrefix.Data(), nSub, "MONASH", monashSamples);
    const bool junctionsOk = LoadSamples(junctionsPrefix.Data(), nSub, "JUNCTIONS", junctionsSamples);

    if (!monashOk || !junctionsOk) {
        CloseSamples(monashSamples);
        CloseSamples(junctionsSamples);
        std::cout << "Aborting due to missing files or multiplicity histograms.\n";
        return false;
    }

    const char* xTitle = "p_{T} (GeV/c)";
    const char* yTitle = "Normalized counts";

    std::vector<TH1D*> monashCurves = BuildTuneCurves(request, monashSamples, xTitle, yTitle);
    std::vector<TH1D*> junctionsCurves = BuildTuneCurves(request, junctionsSamples, xTitle, yTitle);

    bool monashHasData = false;
    bool junctionsHasData = false;
    for (TH1D* hist : monashCurves) {
        if (hist) {
            monashHasData = true;
            break;
        }
    }
    for (TH1D* hist : junctionsCurves) {
        if (hist) {
            junctionsHasData = true;
            break;
        }
    }

    if (!monashHasData && !junctionsHasData) {
        std::cout << "No usable histograms were found for particle '" << request.outputTag << "'.\n";
        if (request.mode == kPreferBar) {
            std::cout << "Anti-particle requests require split Bar histograms to be present.\n";
        }
        DeleteCurves(monashCurves);
        DeleteCurves(junctionsCurves);
        CloseSamples(monashSamples);
        CloseSamples(junctionsSamples);
        return false;
    }

    if (!monashHasData || !junctionsHasData) {
        std::cout << "Warning: one tune is missing usable histograms for particle '"
                  << request.outputTag << "'.\n";
    }

    TString particleLabel = "";
    if (monashSamples.size() > 0 && monashSamples.front().file) {
        particleLabel = DetermineDisplayLabel(monashSamples.front().file, request);
    }
    if (particleLabel.IsNull() && junctionsSamples.size() > 0 && junctionsSamples.front().file) {
        particleLabel = DetermineDisplayLabel(junctionsSamples.front().file, request);
    }
    if (particleLabel.IsNull()) particleLabel = request.outputTag;

    std::vector<TH1D*> allCurves = monashCurves;
    allCurves.insert(allCurves.end(), junctionsCurves.begin(), junctionsCurves.end());

    const double globalXMax = (kFixedXMax > 0.0 ? kFixedXMax : AutoXMax(allCurves));
    const double globalYMax = FindGlobalYMax(monashCurves, junctionsCurves);
    const double globalYMin = std::max(1e-6, 0.5 * FindGlobalYMinPositive(monashCurves, junctionsCurves));

    const TString outFileBase = TString::Format("SingleParticleSpectra_%s_%s",
                                                request.outputTag.Data(),
                                                resolvedDate.Data());

    DrawSpectraComparisonCanvas(monashCurves,
                                junctionsCurves,
                                particleLabel.Data(),
                                resolvedDate.Data(),
                                outFileBase.Data(),
                                globalXMax,
                                globalYMin,
                                globalYMax);

    DeleteCurves(monashCurves);
    DeleteCurves(junctionsCurves);
    CloseSamples(monashSamples);
    CloseSamples(junctionsSamples);
    return true;
}

} // namespace

void Plot_HF_SingleParticlePtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples(
    const char* dateTag = "",
    const char* selectorTag = "Dplus",
    int nSub = 10,
    bool includeHeavyBeautyExtras = false)
{
    SetStyle();

    if (nSub <= 0) {
        std::cout << "nSub must be > 0\n";
        return;
    }

    const TString resolvedDate = PlotPathUtils::ResolveAnalysisDate(dateTag);
    if (resolvedDate.Length() == 0) return;

    const TString resolvedFlavor = NormalizeFlavorTag(selectorTag);
    if (resolvedFlavor.Length() > 0) {
        const std::vector<ResolvedParticleRequest> requests =
            BuildFlavorRequests(resolvedFlavor, includeHeavyBeautyExtras);
        if (requests.empty()) {
            std::cout << "No particles are registered for flavor '" << selectorTag << "'.\n";
            return;
        }

        std::cout << "Generating multiplicity-overlay spectra for all "
                  << resolvedFlavor << " particles";
        if (resolvedFlavor == "Beauty") {
            std::cout << (includeHeavyBeautyExtras
                              ? " including heavier beauty baryons.\n"
                              : " with heavier beauty baryons disabled by default.\n");
        } else {
            std::cout << ".\n";
        }
        for (size_t i = 0; i < requests.size(); ++i) {
            GenerateSingleParticlePlots(resolvedDate, requests[i], nSub);
        }
        return;
    }

    const ResolvedParticleRequest request = ResolveParticleRequest(selectorTag);
    if (!request.def) {
        std::cout << "Unknown selector '" << selectorTag << "'.\n";
        PrintAvailableSelectors();
        return;
    }

    GenerateSingleParticlePlots(resolvedDate, request, nSub);
}

void runHFSingleParticleSpectra(const char* dateTag = "",
                                const char* selectorTag = "Dplus",
                                int nSub = 10,
                                bool includeHeavyBeautyExtras = false)
{
    Plot_HF_SingleParticlePtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples(
        dateTag,
        selectorTag,
        nSub,
        includeHeavyBeautyExtras
    );
}

void runHFSingleParticleSpectraCharm(const char* dateTag = "",
                                     int nSub = 10,
                                     bool includeHeavyBeautyExtras = false)
{
    Plot_HF_SingleParticlePtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples(
        dateTag,
        "Charm",
        nSub,
        includeHeavyBeautyExtras
    );
}

void runHFSingleParticleSpectraBeauty(const char* dateTag = "",
                                      int nSub = 10,
                                      bool includeHeavyBeautyExtras = false)
{
    Plot_HF_SingleParticlePtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples(
        dateTag,
        "Beauty",
        nSub,
        includeHeavyBeautyExtras
    );
}
