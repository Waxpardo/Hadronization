// ---------------------------------------------------------------------------
// Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples.C
//
// Minimum-bias heavy-flavour pT spectra built from analyzed ROOT subsamples in
// AnalyzedData, with uncertainties computed as mean +- SEM across subsamples.
//
// For a flavor selector (Charm or Beauty), the macro produces:
//   1. one species-overlay comparison canvas:
//      - MONASH on the left
//      - JUNCTIONS on the right
//   2. one side-by-side comparison canvas per particle of that flavor:
//      - MONASH on the left
//      - JUNCTIONS on the right
//
// For a particle selector (for example Dzero or Bplus), the macro produces
// only the per-particle comparison canvas.
//
// Default flavor loops:
//   Charm  : D0, D+, D-, Ds, Lambdac
//   Beauty : B+, B-, B0, Bs, Bc, Lambdab
//
// Heavier beauty baryons (Sigmab, Xib, Omegab) are disabled by default and
// can be re-enabled with includeHeavyBeautyExtras = true.
//
// Usage:
//   .L "plotting/PtMultiplicity/Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples.C"
//   runHFMinimumBiasSpectra("27-03-2026", "Charm", 10);
//   runHFMinimumBiasSpectra("27-03-2026", "Beauty", 10);
//   runHFMinimumBiasSpectra("27-03-2026", "Beauty", 10, true);
//   runHFMinimumBiasSpectra("27-03-2026", "Dplus", 10);
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
#include "TLatex.h"
#include "TLegend.h"
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

    LoadedSample() : file(nullptr) {}
};

struct ParticleComparisonData {
    ResolvedParticleRequest request;
    TString label;
    TH1D* monash;
    TH1D* junctions;

    ParticleComparisonData() : monash(nullptr), junctions(nullptr) {}
};

static const StyleDef kSpeciesStyle[] = {
    { kBlue + 1,    1, 2, 20 },
    { kRed + 1,     1, 2, 21 },
    { kGreen + 2,   1, 2, 22 },
    { kViolet + 1,  1, 2, 23 },
    { kOrange + 7,  1, 2, 29 },
    { kTeal + 2,    1, 2, 33 },
    { kMagenta + 1, 1, 2, 34 },
    { kCyan + 2,    1, 2, 47 },
    { kPink + 7,    1, 2, 43 },
    { kAzure + 7,   1, 2, 39 },
    { kSpring + 5,  1, 2, 41 },
    { kBlack,       1, 2, 45 }
};

static const double kFixedXMax = 0.0;

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

TString NormalizeFlavorTag(const char* flavorTag)
{
    TString flavor = flavorTag ? TString(flavorTag) : TString("");
    flavor = flavor.Strip(TString::kBoth);
    flavor.ToUpper();

    if (flavor == "CHARM" || flavor == "C") return "Charm";
    if (flavor == "BEAUTY" || flavor == "B") return "Beauty";

    return "";
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
    std::vector<ParticleDef>& defs = PersistentParticleDefs();

    for (size_t i = 0; i < defs.size(); ++i) {
        const ParticleDef& def = defs[i];

        if (MatchesAnyAlias(normalizedToken, def.barAliases)) {
            request.def = &defs[i];
            request.mode = kPreferBar;
            request.outputTag = def.key + "Bar";
            return request;
        }

        if (MatchesAnyAlias(normalizedToken, def.directAliases)) {
            request.def = &defs[i];
            request.mode = kPreferDirect;
            request.outputTag = def.key + "Combined";
            return request;
        }

        if (MatchesAnyAlias(normalizedToken, def.particleAliases)) {
            request.def = &defs[i];
            request.mode = kPreferParticle;
            request.outputTag = def.key;
            return request;
        }
    }

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
        AppendFlavorRequest(requests, defs, "Dzero",  kPreferParticle, "Dzero");
        AppendFlavorRequest(requests, defs, "Dzero",  kPreferBar,      "Dbar0");
        AppendFlavorRequest(requests, defs, "Dplus",  kPreferParticle, "Dplus");
        AppendFlavorRequest(requests, defs, "Dplus",  kPreferBar,      "Dminus");
        AppendFlavorRequest(requests, defs, "Dsplus", kPreferParticle, "Dsplus");
        AppendFlavorRequest(requests, defs, "Dsplus", kPreferBar,      "Dsminus");
        AppendFlavorRequest(requests, defs, "Lambdac",kPreferParticle, "Lambdac");
        AppendFlavorRequest(requests, defs, "Lambdac",kPreferBar,      "barLambdac");
        return requests;
    }

    if (flavorTag == "Beauty") {
        AppendFlavorRequest(requests, defs, "Bplus",   kPreferParticle, "Bplus");
        AppendFlavorRequest(requests, defs, "Bplus",   kPreferBar,      "Bminus");
        AppendFlavorRequest(requests, defs, "Bzero",   kPreferParticle, "Bzero");
        AppendFlavorRequest(requests, defs, "Bzero",   kPreferBar,      "barB0");
        AppendFlavorRequest(requests, defs, "Bs0",     kPreferParticle, "Bs0");
        AppendFlavorRequest(requests, defs, "Bs0",     kPreferBar,      "barBs0");
        AppendFlavorRequest(requests, defs, "Bcplus",  kPreferParticle, "Bcplus");
        AppendFlavorRequest(requests, defs, "Bcplus",  kPreferBar,      "Bcminus");
        AppendFlavorRequest(requests, defs, "Lambdab", kPreferParticle, "Lambdab");
        AppendFlavorRequest(requests, defs, "Lambdab", kPreferBar,      "barLambdab");

        if (includeHeavyBeautyExtras) {
            AppendFlavorRequest(requests, defs, "SigmabPlus",  kPreferParticle, "SigmabPlus");
            AppendFlavorRequest(requests, defs, "SigmabPlus",  kPreferBar,      "barSigmabMinus");
            AppendFlavorRequest(requests, defs, "SigmabZero",  kPreferParticle, "SigmabZero");
            AppendFlavorRequest(requests, defs, "SigmabZero",  kPreferBar,      "barSigmabZero");
            AppendFlavorRequest(requests, defs, "SigmabMinus", kPreferParticle, "SigmabMinus");
            AppendFlavorRequest(requests, defs, "SigmabMinus", kPreferBar,      "barSigmabPlus");
            AppendFlavorRequest(requests, defs, "XibZero",     kPreferParticle, "XibZero");
            AppendFlavorRequest(requests, defs, "XibZero",     kPreferBar,      "barXibZero");
            AppendFlavorRequest(requests, defs, "XibMinus",    kPreferParticle, "XibMinus");
            AppendFlavorRequest(requests, defs, "XibMinus",    kPreferBar,      "barXibPlus");
            AppendFlavorRequest(requests, defs, "OmegabMinus", kPreferParticle, "OmegabMinus");
            AppendFlavorRequest(requests, defs, "OmegabMinus", kPreferBar,      "barOmegabPlus");
        }
    }

    return requests;
}

void PrintAvailableSelectors()
{
    std::cout
        << "Flavor selectors: Charm, Beauty\n"
        << "Default flavor loops use:\n"
        << "  Charm  : D0, #bar{D}0, D+, D-, Ds+, Ds-, #Lambda_c+, #bar{#Lambda}_c-\n"
        << "  Beauty : B+, B-, B0, #bar{B}0, Bs0, #bar{B}s0, Bc+, Bc-, #Lambda_b0, #bar{#Lambda}_b0\n"
        << "Heavier beauty baryons can be re-enabled with includeHeavyBeautyExtras = true.\n"
        << "Particle selectors include Dzero, Dplus, Dminus, Dsplus, Lambdac,\n"
        << "Bplus, Bminus, Bzero, Bs0, Bcplus, Lambdab, SigmabPlus, SigmabZero,\n"
        << "SigmabMinus, XibZero, XibMinus, OmegabMinus.\n";
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

TString ResolvePrefixForParticle(const TString& dateTag,
                                 const ResolvedParticleRequest& request,
                                 const char* tuneTag)
{
    if (!request.def) return "";
    return ResolvePrefixForFlavor(dateTag, request.def->flavorDir, tuneTag);
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

        samples[i].file = file;
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
    }
}

TH2* GetHistogramForRequest(TFile* file,
                            const ResolvedParticleRequest& request,
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

TH1D* BuildCombinedSpectrumForRequest(const ResolvedParticleRequest& request,
                                      const std::vector<LoadedSample>& samples,
                                      const char* xTitle,
                                      const char* yTitle)
{
    std::vector<TH1D*> oneSubsamplePerFile;
    oneSubsamplePerFile.reserve(samples.size());

    for (size_t iSub = 0; iSub < samples.size(); ++iSub) {
        const LoadedSample& sample = samples[iSub];
        if (!sample.file) continue;

        TH2* source = GetHistogramForRequest(sample.file,
                                             request,
                                             Form("h2_%s_sub%zu",
                                                  request.outputTag.Data(),
                                                  iSub));
        if (!source) continue;

        TH1D* spectrum = BuildMinimumBiasSpectrumOneSub(source,
                                                        Form("h_%s_sub%zu",
                                                             request.outputTag.Data(),
                                                             iSub),
                                                        xTitle,
                                                        yTitle);
        delete source;
        if (spectrum) oneSubsamplePerFile.push_back(spectrum);
    }

    TH1D* combined = CombineSubsampleSpectra(oneSubsamplePerFile,
                                             Form("h_%s_mb", request.outputTag.Data()),
                                             xTitle,
                                             yTitle);

    for (TH1D* hist : oneSubsamplePerFile) delete hist;
    return combined;
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

    if (TH2* combined = GetCombinedFromSplitPair(file, request.def->splitBases, "tmpLabel")) {
        const TString label = LabelFromTitle(combined->GetTitle(),
                                             request.def->fallbackDirectLabel.Data());
        delete combined;
        return label;
    }

    return request.def->fallbackDirectLabel;
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

double FindGlobalYMax(const std::vector<TH1D*>& curves)
{
    double yMax = 0.0;
    for (TH1D* hist : curves) {
        if (!hist) continue;
        for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
            yMax = std::max(yMax, hist->GetBinContent(bin) + hist->GetBinError(bin));
        }
    }
    return (yMax > 0.0 ? yMax : 1.0);
}

double FindGlobalYMinPositive(const std::vector<TH1D*>& curves)
{
    double yMinPositive = 1e30;
    for (TH1D* hist : curves) {
        if (!hist) continue;
        for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
            const double value = hist->GetBinContent(bin);
            if (value > 0.0) yMinPositive = std::min(yMinPositive, value);
        }
    }
    return (yMinPositive < 1e29 ? yMinPositive : 1e-6);
}

void StyleSpeciesCurve(TH1D* hist, int styleIndex)
{
    if (!hist) return;

    const int nStyles = static_cast<int>(sizeof(kSpeciesStyle) / sizeof(kSpeciesStyle[0]));
    const StyleDef& style = kSpeciesStyle[(nStyles > 0 ? styleIndex % nStyles : 0)];

    hist->SetLineColor(style.color);
    hist->SetMarkerColor(style.color);
    hist->SetLineStyle(style.lstyle);
    hist->SetLineWidth(style.lwidth);
    hist->SetMarkerStyle(style.marker);
    hist->SetMarkerSize(0.9);
    hist->SetFillStyle(0);
    hist->SetFillColor(0);
}

void StyleSingleCurve(TH1D* hist)
{
    if (!hist) return;

    hist->SetLineColor(kBlue + 1);
    hist->SetMarkerColor(kBlue + 1);
    hist->SetLineStyle(1);
    hist->SetLineWidth(2);
    hist->SetMarkerStyle(20);
    hist->SetMarkerSize(0.9);
    hist->SetFillStyle(0);
    hist->SetFillColor(0);
}

void DeleteParticleData(std::vector<ParticleComparisonData>& data)
{
    for (ParticleComparisonData& item : data) {
        delete item.monash;
        delete item.junctions;
        item.monash = nullptr;
        item.junctions = nullptr;
    }
}

void PrintLabelList(const char* prefix, const std::vector<TString>& labels)
{
    if (labels.empty()) return;

    std::cout << prefix;
    for (size_t i = 0; i < labels.size(); ++i) {
        if (i > 0) std::cout << ", ";
        std::cout << labels[i];
    }
    std::cout << "\n";
}

std::vector<ParticleComparisonData> BuildFlavorComparisonData(const TString& flavorTag,
                                                              bool includeHeavyBeautyExtras,
                                                              const std::vector<LoadedSample>& monashSamples,
                                                              const std::vector<LoadedSample>& junctionsSamples,
                                                              const char* xTitle,
                                                              const char* yTitle,
                                                              std::vector<TString>& missingLabels)
{
    std::vector<ParticleComparisonData> data;
    const std::vector<ResolvedParticleRequest> requests =
        BuildFlavorRequests(flavorTag, includeHeavyBeautyExtras);

    for (const ResolvedParticleRequest& request : requests) {
        ParticleComparisonData item;
        item.request = request;
        item.monash = BuildCombinedSpectrumForRequest(request, monashSamples, xTitle, yTitle);
        item.junctions = BuildCombinedSpectrumForRequest(request, junctionsSamples, xTitle, yTitle);

        if (!item.monash && !item.junctions) {
            if (request.mode == kPreferBar && request.def) {
                missingLabels.push_back(request.def->fallbackBarLabel);
            } else if (request.mode == kPreferParticle && request.def) {
                missingLabels.push_back(request.def->fallbackParticleLabel);
            } else if (request.def) {
                missingLabels.push_back(request.def->fallbackDirectLabel);
            }
            continue;
        }

        if (monashSamples.size() > 0 && monashSamples.front().file) {
            item.label = DetermineDisplayLabel(monashSamples.front().file, request);
        }
        if (item.label.IsNull() && junctionsSamples.size() > 0 && junctionsSamples.front().file) {
            item.label = DetermineDisplayLabel(junctionsSamples.front().file, request);
        }
        if (item.label.IsNull() && request.def) {
            if (request.mode == kPreferBar) item.label = request.def->fallbackBarLabel;
            else if (request.mode == kPreferParticle) item.label = request.def->fallbackParticleLabel;
            else item.label = request.def->fallbackDirectLabel;
        }

        data.push_back(item);
    }

    return data;
}

void DrawMinimumBiasOverlayPad(TPad* pad,
                               const char* flavorLabel,
                               const char* tuneTag,
                               const char* dateTag,
                               const std::vector<ParticleComparisonData>& data,
                               bool drawMonash,
                               double globalXMax,
                               double globalYMin,
                               double globalYMax)
{
    if (!pad) return;

    pad->cd();
    pad->SetLogy();
    pad->SetTicks(1, 1);
    pad->SetTopMargin(0.22);
    pad->SetBottomMargin(0.13);
    pad->SetLeftMargin(0.14);
    pad->SetRightMargin(0.05);

    TH1D* frame = nullptr;
    std::vector<TH1D*> curves;
    curves.reserve(data.size());

    for (const ParticleComparisonData& item : data) {
        TH1D* hist = (drawMonash ? item.monash : item.junctions);
        curves.push_back(hist);
        if (!frame && hist) frame = hist;
    }

    if (!frame) {
        TLatex latex;
        latex.SetNDC();
        latex.SetTextSize(0.055);
        latex.DrawLatex(0.14, 0.95, flavorLabel);
        latex.DrawLatex(0.14, 0.88, tuneTag);
        latex.SetTextSize(0.040);
        latex.DrawLatex(0.14, 0.81, Form("Date: %s", dateTag));
        latex.DrawLatex(0.14, 0.74, "No entries");
        return;
    }

    frame->SetMinimum(globalYMin);
    frame->SetMaximum(1.8 * globalYMax);
    frame->GetXaxis()->SetRangeUser(0.0, globalXMax);
    frame->GetXaxis()->SetTitleSize(0.058);
    frame->GetYaxis()->SetTitleSize(0.058);
    frame->GetXaxis()->SetLabelSize(0.048);
    frame->GetYaxis()->SetLabelSize(0.048);
    frame->GetXaxis()->SetTitleOffset(1.0);
    frame->GetYaxis()->SetTitleOffset(1.05);

    for (size_t i = 0; i < curves.size(); ++i) {
        TH1D* hist = curves[i];
        if (!hist) continue;
        StyleSpeciesCurve(hist, static_cast<int>(i));
        hist->Draw(frame == hist ? "E1" : "E1 SAME");
    }

    TLatex latex;
    latex.SetNDC();
    latex.SetTextSize(0.052);
    latex.DrawLatex(0.14, 0.95, flavorLabel);
    latex.DrawLatex(0.14, 0.88, tuneTag);
    latex.SetTextSize(0.040);
    latex.DrawLatex(0.14, 0.81, Form("Date: %s", dateTag));

    const double plotLeft = pad->GetLeftMargin();
    const double plotRight = 1.0 - pad->GetRightMargin();
    const double plotTop = 1.0 - pad->GetTopMargin();
    const double legendWidth = 0.31;
    const double legendHeight = std::min(0.50, 0.07 + 0.055 * static_cast<double>(data.size()));
    const double legendX2 = plotRight - 0.02;
    const double legendX1 = std::max(plotLeft + 0.06, legendX2 - legendWidth);
    const double legendY2 = plotTop - 0.035;
    const double legendY1 = std::max(pad->GetBottomMargin() + 0.14,
                                     legendY2 - legendHeight);

    TLegend* legend = new TLegend(legendX1, legendY1, legendX2, legendY2);
    legend->SetTextSize(0.036);
    legend->SetBorderSize(0);
    legend->SetFillStyle(0);
    legend->SetFillColorAlpha(0, 0.0);
    for (size_t i = 0; i < data.size(); ++i) {
        TH1D* hist = curves[i];
        if (!hist) continue;
        legend->AddEntry(hist, data[i].label.Data(), "lep");
    }
    legend->Draw();
}

void DrawFlavorMinimumBiasComparisonCanvas(const char* flavorLabel,
                                           const char* dateTag,
                                           const std::vector<ParticleComparisonData>& data)
{
    if (data.empty()) {
        std::cout << "No minimum-bias spectra could be built for " << flavorLabel << ".\n";
        return;
    }

    std::vector<TH1D*> allCurves;
    for (const ParticleComparisonData& item : data) {
        allCurves.push_back(item.monash);
        allCurves.push_back(item.junctions);
    }

    const double globalXMax = (kFixedXMax > 0.0 ? kFixedXMax : AutoXMax(allCurves));
    const double globalYMax = FindGlobalYMax(allCurves);
    const double globalYMin = std::max(1e-6, 0.5 * FindGlobalYMinPositive(allCurves));

    const TString baseName = TString::Format("MinimumBiasSpeciesResolvedSpectraCompareTunes_%s_%s",
                                             flavorLabel,
                                             dateTag);
    TCanvas* canvas = new TCanvas(Form("c_%s", baseName.Data()),
                                  baseName.Data(),
                                  1900,
                                  760);
    canvas->Divide(2, 1, 0.0, 0.0);

    canvas->cd(1);
    DrawMinimumBiasOverlayPad(dynamic_cast<TPad*>(gPad),
                              flavorLabel,
                              "MONASH",
                              dateTag,
                              data,
                              true,
                              globalXMax,
                              globalYMin,
                              globalYMax);

    canvas->cd(2);
    DrawMinimumBiasOverlayPad(dynamic_cast<TPad*>(gPad),
                              flavorLabel,
                              "JUNCTIONS",
                              dateTag,
                              data,
                              false,
                              globalXMax,
                              globalYMin,
                              globalYMax);

    const TString pngPath = PlotPathUtils::BuildPtMultiplicityPlotPath(baseName + ".png");
    const TString pdfPath = PlotPathUtils::BuildPtMultiplicityPlotPath(baseName + ".pdf");

    canvas->SaveAs(pngPath);
    canvas->SaveAs(pdfPath);

    std::cout << "Saved minimum-bias flavor comparison canvas to:\n"
              << "  " << pngPath << "\n"
              << "  " << pdfPath << "\n";

    delete canvas;
}

void DrawMinimumBiasSinglePad(TPad* pad,
                              TH1D* hist,
                              const char* tuneTag,
                              const char* particleLabel,
                              const char* dateTag,
                              double globalXMax,
                              double globalYMin,
                              double globalYMax)
{
    if (!pad) return;

    pad->cd();
    pad->SetLogy();
    pad->SetTicks(1, 1);
    pad->SetTopMargin(0.22);
    pad->SetBottomMargin(0.13);
    pad->SetLeftMargin(0.14);
    pad->SetRightMargin(0.05);

    if (!hist) {
        TLatex latex;
        latex.SetNDC();
        latex.SetTextSize(0.054);
        latex.DrawLatex(0.14, 0.95, particleLabel);
        latex.DrawLatex(0.14, 0.88, tuneTag);
        latex.SetTextSize(0.040);
        latex.DrawLatex(0.14, 0.81, Form("Date: %s", dateTag));
        latex.DrawLatex(0.14, 0.74, "No entries");
        return;
    }

    StyleSingleCurve(hist);
    hist->SetMinimum(globalYMin);
    hist->SetMaximum(1.8 * globalYMax);
    hist->GetXaxis()->SetRangeUser(0.0, globalXMax);
    hist->GetXaxis()->SetTitleSize(0.058);
    hist->GetYaxis()->SetTitleSize(0.058);
    hist->GetXaxis()->SetLabelSize(0.048);
    hist->GetYaxis()->SetLabelSize(0.048);
    hist->GetXaxis()->SetTitleOffset(1.0);
    hist->GetYaxis()->SetTitleOffset(1.05);
    hist->Draw("E1");

    TLatex latex;
    latex.SetNDC();
    latex.SetTextSize(0.052);
    latex.DrawLatex(0.14, 0.95, particleLabel);
    latex.DrawLatex(0.14, 0.88, tuneTag);
    latex.SetTextSize(0.040);
    latex.DrawLatex(0.14, 0.81, Form("Date: %s", dateTag));
}

void DrawParticleMinimumBiasComparisonCanvas(const ParticleComparisonData& item,
                                             const char* dateTag)
{
    if (!item.monash && !item.junctions) return;

    std::vector<TH1D*> curves;
    curves.push_back(item.monash);
    curves.push_back(item.junctions);

    const double globalXMax = (kFixedXMax > 0.0 ? kFixedXMax : AutoXMax(curves));
    const double globalYMax = FindGlobalYMax(curves);
    const double globalYMin = std::max(1e-6, 0.5 * FindGlobalYMinPositive(curves));

    const TString baseName = TString::Format("MinimumBiasSingleParticleSpectra_%s_%s",
                                             item.request.outputTag.Data(),
                                             dateTag);
    TCanvas* canvas = new TCanvas(Form("c_%s", baseName.Data()),
                                  baseName.Data(),
                                  1900,
                                  760);
    canvas->Divide(2, 1, 0.0, 0.0);

    canvas->cd(1);
    DrawMinimumBiasSinglePad(dynamic_cast<TPad*>(gPad),
                             item.monash,
                             "MONASH",
                             item.label.Data(),
                             dateTag,
                             globalXMax,
                             globalYMin,
                             globalYMax);

    canvas->cd(2);
    DrawMinimumBiasSinglePad(dynamic_cast<TPad*>(gPad),
                             item.junctions,
                             "JUNCTIONS",
                             item.label.Data(),
                             dateTag,
                             globalXMax,
                             globalYMin,
                             globalYMax);

    const TString pngPath = PlotPathUtils::BuildPtMultiplicityPlotPath(baseName + ".png");
    const TString pdfPath = PlotPathUtils::BuildPtMultiplicityPlotPath(baseName + ".pdf");

    canvas->SaveAs(pngPath);
    canvas->SaveAs(pdfPath);

    std::cout << "Saved minimum-bias particle comparison canvas to:\n"
              << "  " << pngPath << "\n"
              << "  " << pdfPath << "\n";

    delete canvas;
}

bool GenerateFlavorMinimumBiasPlots(const TString& resolvedDate,
                                    const TString& flavorTag,
                                    int nSub,
                                    bool includeHeavyBeautyExtras)
{
    const TString monashPrefix = ResolvePrefixForFlavor(resolvedDate, flavorTag, "MONASH");
    const TString junctionsPrefix = ResolvePrefixForFlavor(resolvedDate, flavorTag, "JUNCTIONS");

    std::cout << "Minimum-bias HF spectra input date: " << resolvedDate << "\n";
    std::cout << "  Flavor           : " << flavorTag << "\n";
    std::cout << "  MONASH prefix    : " << monashPrefix << "*.root\n";
    std::cout << "  JUNCTIONS prefix : " << junctionsPrefix << "*.root\n";

    std::vector<LoadedSample> monashSamples;
    std::vector<LoadedSample> junctionsSamples;

    const bool monashOk = LoadSamples(monashPrefix.Data(), nSub, "MONASH", monashSamples);
    const bool junctionsOk = LoadSamples(junctionsPrefix.Data(), nSub, "JUNCTIONS", junctionsSamples);

    if (!monashOk || !junctionsOk) {
        CloseSamples(monashSamples);
        CloseSamples(junctionsSamples);
        std::cout << "Aborting due to missing files.\n";
        return false;
    }

    const char* xTitle = "p_{T} (GeV/c)";
    const char* yTitle = "Normalized counts";
    std::vector<TString> missingLabels;
    std::vector<ParticleComparisonData> data =
        BuildFlavorComparisonData(flavorTag,
                                  includeHeavyBeautyExtras,
                                  monashSamples,
                                  junctionsSamples,
                                  xTitle,
                                  yTitle,
                                  missingLabels);

    PrintLabelList(Form("%s minimum-bias species skipped because no usable histogram source was found: ",
                        flavorTag.Data()),
                   missingLabels);

    DrawFlavorMinimumBiasComparisonCanvas(flavorTag.Data(),
                                          resolvedDate.Data(),
                                          data);

    for (const ParticleComparisonData& item : data) {
        DrawParticleMinimumBiasComparisonCanvas(item, resolvedDate.Data());
    }

    DeleteParticleData(data);
    CloseSamples(monashSamples);
    CloseSamples(junctionsSamples);
    return true;
}

bool GenerateSingleParticleMinimumBiasPlot(const TString& resolvedDate,
                                           const ResolvedParticleRequest& request,
                                           int nSub)
{
    if (!request.def) return false;

    const TString monashPrefix = ResolvePrefixForParticle(resolvedDate, request, "MONASH");
    const TString junctionsPrefix = ResolvePrefixForParticle(resolvedDate, request, "JUNCTIONS");

    std::cout << "Minimum-bias single-particle HF spectra input date: " << resolvedDate << "\n";
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
        std::cout << "Aborting due to missing files.\n";
        return false;
    }

    const char* xTitle = "p_{T} (GeV/c)";
    const char* yTitle = "Normalized counts";

    ParticleComparisonData item;
    item.request = request;
    item.monash = BuildCombinedSpectrumForRequest(request, monashSamples, xTitle, yTitle);
    item.junctions = BuildCombinedSpectrumForRequest(request, junctionsSamples, xTitle, yTitle);

    if (!item.monash && !item.junctions) {
        std::cout << "No usable histograms were found for particle '"
                  << request.outputTag << "'.\n";
        if (request.mode == kPreferBar) {
            std::cout << "Anti-particle requests require split Bar histograms to be present.\n";
        }
        CloseSamples(monashSamples);
        CloseSamples(junctionsSamples);
        return false;
    }

    if (monashSamples.size() > 0 && monashSamples.front().file) {
        item.label = DetermineDisplayLabel(monashSamples.front().file, request);
    }
    if (item.label.IsNull() && junctionsSamples.size() > 0 && junctionsSamples.front().file) {
        item.label = DetermineDisplayLabel(junctionsSamples.front().file, request);
    }
    if (item.label.IsNull()) item.label = request.outputTag;

    DrawParticleMinimumBiasComparisonCanvas(item, resolvedDate.Data());

    delete item.monash;
    delete item.junctions;
    CloseSamples(monashSamples);
    CloseSamples(junctionsSamples);
    return true;
}

} // namespace

void Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples(
    const char* dateTag = "",
    const char* selectorTag = "Charm",
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
        GenerateFlavorMinimumBiasPlots(resolvedDate,
                                       resolvedFlavor,
                                       nSub,
                                       includeHeavyBeautyExtras);
        return;
    }

    const ResolvedParticleRequest request = ResolveParticleRequest(selectorTag);
    if (!request.def) {
        std::cout << "Unknown selector '" << selectorTag << "'.\n";
        PrintAvailableSelectors();
        return;
    }

    GenerateSingleParticleMinimumBiasPlot(resolvedDate, request, nSub);
}

void runHFMinimumBiasSpectra(const char* dateTag = "",
                             const char* selectorTag = "Charm",
                             int nSub = 10,
                             bool includeHeavyBeautyExtras = false)
{
    Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples(dateTag,
                                                             selectorTag,
                                                             nSub,
                                                             includeHeavyBeautyExtras);
}

void runHFMinimumBiasSpectraCharm(const char* dateTag = "",
                                  int nSub = 10,
                                  bool includeHeavyBeautyExtras = false)
{
    Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples(dateTag,
                                                             "Charm",
                                                             nSub,
                                                             includeHeavyBeautyExtras);
}

void runHFMinimumBiasSpectraBeauty(const char* dateTag = "",
                                   int nSub = 10,
                                   bool includeHeavyBeautyExtras = false)
{
    Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples(dateTag,
                                                             "Beauty",
                                                             nSub,
                                                             includeHeavyBeautyExtras);
}

void runHFMinimumBiasSpectraBoth(const char* dateTag = "",
                                 int nSub = 10,
                                 bool includeHeavyBeautyExtras = false)
{
    Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples(dateTag,
                                                             "Charm",
                                                             nSub,
                                                             includeHeavyBeautyExtras);
    Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples(dateTag,
                                                             "Beauty",
                                                             nSub,
                                                             includeHeavyBeautyExtras);
}
