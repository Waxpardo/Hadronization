// ---------------------------------------------------------------------------
// Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples.C
//
// Produces species-resolved heavy-flavour pT spectra vs multiplicity percentile
// from the analyzed ROOT subsamples stored in AnalyzedData.
//
// For a selected flavor (Charm or Beauty), the comparison mode produces one
// canvas per multiplicity percentile, with all available species overlaid:
//   - MONASH on the left
//   - JUNCTIONS on the right
//
// This means 5 canvases per flavor and 10 canvases if both flavors are run.
//
// A tune-by-tune species-panel mode is kept for backward compatibility.
//
// Each pad corresponds to one hadron species and contains the five
// multiplicity classes:
//   80-100%, 60-80%, 40-60%, 20-40%, 0-20%
// ordered from lowest to highest multiplicity.
//
// The plotted uncertainties are computed from the spread across subsamples:
//   one normalized spectrum per subsample -> mean ± SEM bin-by-bin.
//
// Histogram handling is flexible:
//   - if <base>Particle and <base>Bar exist, the macro plots both separately
//   - otherwise it uses the single histogram object stored in the file and
//     takes the pad label directly from that histogram title
//
// Usage:
//   .L "plotting/PtMultiplicity/Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples.C"
//   runHFSpeciesResolvedSpectra("27-03-2026", "Charm", 10);   // 5 canvases
//   runHFSpeciesResolvedSpectra("27-03-2026", "Beauty", 10);  // 5 canvases
//   runHFSpeciesResolvedSpectra("27-03-2026", "MONASH", 10);    // legacy mode
//   runHFSpeciesResolvedSpectra("27-03-2026", "JUNCTIONS", 10); // legacy mode
// ---------------------------------------------------------------------------

#include <algorithm>
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

struct SpeciesDef {
    TString key;
    std::vector<TString> objectNames;
    std::vector<TString> splitBases;
    TString fallbackCombinedLabel;
    TString fallbackParticleLabel;
    TString fallbackBarLabel;
};

enum DrawMode {
    kDrawSingle = 0,
    kDrawParticle = 1,
    kDrawBar = 2
};

struct PlotEntry {
    int speciesIndex;
    DrawMode mode;
    TString key;
    TString label;
};

struct LoadedSample {
    TFile* file;
    TH1* mult;

    LoadedSample() : file(nullptr), mult(nullptr) {}
};

struct FlavorPlotData {
    std::vector<PlotEntry> entries;
    std::vector<std::vector<TH1D*> > curves;
    std::vector<TString> singleObjectLabels;
    std::vector<TString> missingLabels;
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

static const int kSpeciesColors[] = {
    kBlue + 1,
    kRed + 1,
    kGreen + 2,
    kViolet + 1,
    kOrange + 7,
    kTeal + 2,
    kMagenta + 1,
    kCyan + 2,
    kPink + 7,
    kAzure + 7,
    kSpring + 5,
    kBlack
};

static const int kSpeciesMarkersFilled[] = {
    20, 21, 22, 23, 29, 33, 34, 47, 43, 39, 41, 45
};

static const int kSpeciesMarkersOpen[] = {
    24, 25, 26, 32, 30, 27, 28, 46, 42, 40, 44, 30
};

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

bool HasSplitHistPair(TFile* file, const std::vector<TString>& splitBases)
{
    if (!file) return false;

    for (const TString& base : splitBases) {
        if (GetObj<TH2>(file, Form("%sParticle", base.Data())) &&
            GetObj<TH2>(file, Form("%sBar", base.Data()))) {
            return true;
        }
    }

    return false;
}

TH2* GetSplitHist(TFile* file,
                  const std::vector<TString>& splitBases,
                  bool wantParticle,
                  const char* cloneName)
{
    if (!file) return nullptr;

    for (const TString& base : splitBases) {
        const TString histName = TString::Format("%s%s",
                                                 base.Data(),
                                                 wantParticle ? "Particle" : "Bar");
        if (TH2* hist = GetObj<TH2>(file, histName.Data())) return CloneTH2(hist, cloneName);
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

SpeciesDef MakeSpecies(const char* key,
                       const std::vector<TString>& objectNames,
                       const std::vector<TString>& splitBases,
                       const char* fallbackCombinedLabel,
                       const char* fallbackParticleLabel,
                       const char* fallbackBarLabel)
{
    SpeciesDef spec;
    spec.key = key;
    spec.objectNames = objectNames;
    spec.splitBases = splitBases;
    spec.fallbackCombinedLabel = fallbackCombinedLabel;
    spec.fallbackParticleLabel = fallbackParticleLabel;
    spec.fallbackBarLabel = fallbackBarLabel;
    return spec;
}

std::vector<SpeciesDef> BuildCharmSpecies()
{
    std::vector<SpeciesDef> defs;
    defs.push_back(MakeSpecies("Dzero",
                               {"fHistPtDzero"},
                               {"fHistPtDzero"},
                               "D^{0}/#bar{D}^{0}",
                               "D^{0}",
                               "#bar{D}^{0}"));
    defs.push_back(MakeSpecies("Dplus",
                               {"fHistPtDplus"},
                               {"fHistPtDplus"},
                               "D^{#pm}",
                               "D^{+}",
                               "D^{-}"));
    defs.push_back(MakeSpecies("Dsplus",
                               {"fHistPtDsplus"},
                               {"fHistPtDsplus"},
                               "D_{s}^{#pm}",
                               "D_{s}^{+}",
                               "D_{s}^{-}"));
    defs.push_back(MakeSpecies("Lambdac",
                               {"fHistPtLambdac", "fHistPtLambdacPlus"},
                               {"fHistPtLambdac"},
                               "#Lambda_{c}^{+}/#bar{#Lambda}_{c}^{-}",
                               "#Lambda_{c}^{+}",
                               "#bar{#Lambda}_{c}^{-}"));
    return defs;
}

std::vector<SpeciesDef> BuildBeautySpecies()
{
    std::vector<SpeciesDef> defs;
    defs.push_back(MakeSpecies("Bplus",
                               {"fHistPtBplus"},
                               {"fHistPtBplus"},
                               "B^{#pm}",
                               "B^{+}",
                               "B^{-}"));
    defs.push_back(MakeSpecies("Bzero",
                               {"fHistPtBzero"},
                               {"fHistPtBzero"},
                               "B^{0}/#bar{B}^{0}",
                               "B^{0}",
                               "#bar{B}^{0}"));
    defs.push_back(MakeSpecies("Bs0",
                               {"fHistPtBs0"},
                               {"fHistPtBs0"},
                               "B_{s}^{0}/#bar{B}_{s}^{0}",
                               "B_{s}^{0}",
                               "#bar{B}_{s}^{0}"));
    defs.push_back(MakeSpecies("Bcplus",
                               {"fHistPtBcplus"},
                               {"fHistPtBcplus"},
                               "B_{c}^{#pm}",
                               "B_{c}^{+}",
                               "B_{c}^{-}"));
    defs.push_back(MakeSpecies("Lambdab",
                               {"fHistPtLambdab"},
                               {"fHistPtLambdab"},
                               "#Lambda_{b}^{0}/#bar{#Lambda}_{b}^{0}",
                               "#Lambda_{b}^{0}",
                               "#bar{#Lambda}_{b}^{0}"));
    defs.push_back(MakeSpecies("SigmabPlus",
                               {"fHistPtSigmabPlus"},
                               {"fHistPtSigmabPlus"},
                               "#Sigma_{b}^{+}/#bar{#Sigma}_{b}^{-}",
                               "#Sigma_{b}^{+}",
                               "#bar{#Sigma}_{b}^{-}"));
    defs.push_back(MakeSpecies("SigmabZero",
                               {"fHistPtSigmabZero"},
                               {"fHistPtSigmabZero"},
                               "#Sigma_{b}^{0}/#bar{#Sigma}_{b}^{0}",
                               "#Sigma_{b}^{0}",
                               "#bar{#Sigma}_{b}^{0}"));
    defs.push_back(MakeSpecies("SigmabMinus",
                               {"fHistPtSigmabMinus"},
                               {"fHistPtSigmabMinus"},
                               "#Sigma_{b}^{-}/#bar{#Sigma}_{b}^{+}",
                               "#Sigma_{b}^{-}",
                               "#bar{#Sigma}_{b}^{+}"));
    defs.push_back(MakeSpecies("XibZero",
                               {"fHistPtXibZero"},
                               {"fHistPtXibZero"},
                               "#Xi_{b}^{0}/#bar{#Xi}_{b}^{0}",
                               "#Xi_{b}^{0}",
                               "#bar{#Xi}_{b}^{0}"));
    defs.push_back(MakeSpecies("XibMinus",
                               {"fHistPtXibMinus"},
                               {"fHistPtXibMinus"},
                               "#Xi_{b}^{-}/#bar{#Xi}_{b}^{+}",
                               "#Xi_{b}^{-}",
                               "#bar{#Xi}_{b}^{+}"));
    defs.push_back(MakeSpecies("OmegabMinus",
                               {"fHistPtOmegabMinus"},
                               {"fHistPtOmegabMinus"},
                               "#Omega_{b}^{-}/#bar{#Omega}_{b}^{+}",
                               "#Omega_{b}^{-}",
                               "#bar{#Omega}_{b}^{+}"));
    return defs;
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

TString NormalizeTuneTag(const char* tuneTag)
{
    TString tune = tuneTag ? TString(tuneTag) : TString("");
    tune = tune.Strip(TString::kBoth);
    tune.ToUpper();

    if (tune == "MONASH") return "MONASH";
    if (tune == "JUNCTIONS" || tune == "JUN") return "JUNCTIONS";
    if (tune == "CLOSEPACKING" || tune == "CLOSE_PACKING" || tune == "CP") return "CLOSEPACKING";

    std::cout << "Unknown tune '" << tuneTag
              << "'. Expected MONASH, JUNCTIONS, or CLOSEPACKING.\n";
    return "";
}

TString NormalizeTuneTagQuiet(const char* tuneTag)
{
    TString tune = tuneTag ? TString(tuneTag) : TString("");
    tune = tune.Strip(TString::kBoth);
    tune.ToUpper();

    if (tune == "MONASH") return "MONASH";
    if (tune == "JUNCTIONS" || tune == "JUN") return "JUNCTIONS";
    if (tune == "CLOSEPACKING" || tune == "CLOSE_PACKING" || tune == "CP") return "CLOSEPACKING";

    return "";
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

TString ResolveFlavorPrefix(const TString& dateTag,
                           const TString& flavorTag,
                           const TString& tuneTag)
{
    if (flavorTag == "Charm") {
        return PlotPathUtils::ResolveAnalyzedPrefix(
            dateTag,
            "Charm",
            {TString::Format("hf_%s_sub", tuneTag.Data()),
             TString::Format("ccbar_%s_sub", tuneTag.Data())}
        );
    }

    return PlotPathUtils::ResolveAnalyzedPrefix(
        dateTag,
        "Beauty",
        {TString::Format("hf_%s_sub", tuneTag.Data()),
         TString::Format("bbbar_%s_sub", tuneTag.Data())}
    );
}

std::vector<SpeciesDef> BuildSpeciesForFlavor(const TString& flavorTag,
                                              bool includeHeavyBeautyExtras = false)
{
    if (flavorTag == "Charm") return BuildCharmSpecies();

    std::vector<SpeciesDef> beautyDefs = BuildBeautySpecies();
    if (includeHeavyBeautyExtras) return beautyDefs;

    std::vector<SpeciesDef> filtered;
    for (const SpeciesDef& spec : beautyDefs) {
        if (spec.key == "SigmabPlus" ||
            spec.key == "SigmabZero" ||
            spec.key == "SigmabMinus" ||
            spec.key == "XibZero" ||
            spec.key == "XibMinus" ||
            spec.key == "OmegabMinus") {
            continue;
        }
        filtered.push_back(spec);
    }
    return filtered;
}

int FindSpeciesIndex(const std::vector<SpeciesDef>& speciesDefs, const char* key)
{
    for (size_t i = 0; i < speciesDefs.size(); ++i) {
        if (speciesDefs[i].key == key) return static_cast<int>(i);
    }
    return -1;
}

void AppendRequestedEntry(std::vector<PlotEntry>& entries,
                          const std::vector<SpeciesDef>& speciesDefs,
                          const char* key,
                          DrawMode mode)
{
    const int speciesIndex = FindSpeciesIndex(speciesDefs, key);
    if (speciesIndex < 0) return;

    PlotEntry entry;
    entry.speciesIndex = speciesIndex;
    entry.mode = mode;
    entry.key = speciesDefs[speciesIndex].key;
    if (mode == kDrawParticle) entry.key += "Particle";
    else if (mode == kDrawBar) entry.key += "Bar";
    else entry.key += "Single";
    entries.push_back(entry);
}

std::vector<PlotEntry> BuildRequestedEntriesForFlavor(const std::vector<SpeciesDef>& speciesDefs,
                                                      const TString& flavorTag,
                                                      bool includeHeavyBeautyExtras = false)
{
    std::vector<PlotEntry> entries;

    if (flavorTag == "Charm") {
        AppendRequestedEntry(entries, speciesDefs, "Dzero", kDrawParticle);
        AppendRequestedEntry(entries, speciesDefs, "Dzero", kDrawBar);
        AppendRequestedEntry(entries, speciesDefs, "Dplus", kDrawParticle);
        AppendRequestedEntry(entries, speciesDefs, "Dplus", kDrawBar);
        AppendRequestedEntry(entries, speciesDefs, "Dsplus", kDrawParticle);
        AppendRequestedEntry(entries, speciesDefs, "Dsplus", kDrawBar);
        AppendRequestedEntry(entries, speciesDefs, "Lambdac", kDrawParticle);
        AppendRequestedEntry(entries, speciesDefs, "Lambdac", kDrawBar);
        return entries;
    }

    AppendRequestedEntry(entries, speciesDefs, "Bplus", kDrawParticle);
    AppendRequestedEntry(entries, speciesDefs, "Bplus", kDrawBar);
    AppendRequestedEntry(entries, speciesDefs, "Bzero", kDrawParticle);
    AppendRequestedEntry(entries, speciesDefs, "Bzero", kDrawBar);
    AppendRequestedEntry(entries, speciesDefs, "Bs0", kDrawParticle);
    AppendRequestedEntry(entries, speciesDefs, "Bs0", kDrawBar);
    AppendRequestedEntry(entries, speciesDefs, "Bcplus", kDrawParticle);
    AppendRequestedEntry(entries, speciesDefs, "Bcplus", kDrawBar);
    AppendRequestedEntry(entries, speciesDefs, "Lambdab", kDrawParticle);
    AppendRequestedEntry(entries, speciesDefs, "Lambdab", kDrawBar);

    if (includeHeavyBeautyExtras) {
        AppendRequestedEntry(entries, speciesDefs, "SigmabPlus", kDrawParticle);
        AppendRequestedEntry(entries, speciesDefs, "SigmabPlus", kDrawBar);
        AppendRequestedEntry(entries, speciesDefs, "SigmabZero", kDrawParticle);
        AppendRequestedEntry(entries, speciesDefs, "SigmabZero", kDrawBar);
        AppendRequestedEntry(entries, speciesDefs, "SigmabMinus", kDrawParticle);
        AppendRequestedEntry(entries, speciesDefs, "SigmabMinus", kDrawBar);
        AppendRequestedEntry(entries, speciesDefs, "XibZero", kDrawParticle);
        AppendRequestedEntry(entries, speciesDefs, "XibZero", kDrawBar);
        AppendRequestedEntry(entries, speciesDefs, "XibMinus", kDrawParticle);
        AppendRequestedEntry(entries, speciesDefs, "XibMinus", kDrawBar);
        AppendRequestedEntry(entries, speciesDefs, "OmegabMinus", kDrawParticle);
        AppendRequestedEntry(entries, speciesDefs, "OmegabMinus", kDrawBar);
    }

    return entries;
}

TString DetermineSingleLabel(TFile* file, const SpeciesDef& spec)
{
    if (TH2* direct = GetDirectHist(file, spec.objectNames)) {
        return LabelFromTitle(direct->GetTitle(), spec.fallbackCombinedLabel.Data());
    }

    return spec.fallbackCombinedLabel;
}

TString DetermineSplitLabel(TFile* file,
                            const SpeciesDef& spec,
                            bool wantParticle,
                            const char* fallback)
{
    if (!file) return fallback;

    for (const TString& base : spec.splitBases) {
        const TString histName = TString::Format("%s%s",
                                                 base.Data(),
                                                 wantParticle ? "Particle" : "Bar");
        if (TH2* hist = GetObj<TH2>(file, histName.Data())) {
            return LabelFromTitle(hist->GetTitle(), fallback);
        }
    }

    return fallback;
}

std::vector<PlotEntry> BuildPlotEntries(const std::vector<SpeciesDef>& speciesDefs,
                                        const std::vector<PlotEntry>& requestedEntries,
                                        const std::vector<LoadedSample>& samples,
                                        std::vector<TString>& singleObjectLabels,
                                        std::vector<TString>& missingLabels)
{
    std::vector<PlotEntry> entries;
    if (samples.empty() || !samples.front().file) return entries;

    for (const PlotEntry& requested : requestedEntries) {
        if (requested.speciesIndex < 0 ||
            requested.speciesIndex >= static_cast<int>(speciesDefs.size())) {
            continue;
        }

        const SpeciesDef& spec = speciesDefs[requested.speciesIndex];
        bool anySplit = false;
        bool anyDirect = false;
        for (const LoadedSample& sample : samples) {
            if (!sample.file) continue;
            if (HasSplitHistPair(sample.file, spec.splitBases)) anySplit = true;
            if (GetDirectHist(sample.file, spec.objectNames)) anyDirect = true;
        }

        PlotEntry entry = requested;
        if (entry.mode == kDrawParticle) {
            if (!anySplit && !anyDirect) {
                missingLabels.push_back(spec.fallbackParticleLabel);
                continue;
            }
            if (anySplit) {
                entry.label = DetermineSplitLabel(samples.front().file,
                                                  spec,
                                                  true,
                                                  spec.fallbackParticleLabel.Data());
            } else {
                entry.label = DetermineSingleLabel(samples.front().file, spec);
                singleObjectLabels.push_back(entry.label);
            }
            entries.push_back(entry);
            continue;
        }

        if (entry.mode == kDrawBar) {
            if (!anySplit) {
                missingLabels.push_back(spec.fallbackBarLabel);
                continue;
            }
            entry.label = DetermineSplitLabel(samples.front().file,
                                              spec,
                                              false,
                                              spec.fallbackBarLabel.Data());
            entries.push_back(entry);
            continue;
        }

        if (!anyDirect && !anySplit) {
            missingLabels.push_back(spec.fallbackCombinedLabel);
            continue;
        }

        entry.label = DetermineSingleLabel(samples.front().file, spec);
        entries.push_back(entry);
        if (anyDirect) singleObjectLabels.push_back(entry.label);
    }

    return entries;
}

TH2* GetHistogramForEntry(TFile* file,
                          const SpeciesDef& spec,
                          const PlotEntry& entry,
                          const char* cloneName)
{
    if (entry.mode == kDrawParticle) {
        if (TH2* split = GetSplitHist(file, spec.splitBases, true, cloneName)) return split;
        return GetDirectHist(file, spec.objectNames, cloneName);
    }

    if (entry.mode == kDrawBar) {
        return GetSplitHist(file, spec.splitBases, false, cloneName);
    }

    if (TH2* direct = GetDirectHist(file, spec.objectNames, cloneName)) return direct;
    return GetCombinedFromSplitPair(file, spec.splitBases, cloneName);
}

std::vector<TH1D*> BuildCurvesForEntry(const PlotEntry& entry,
                                       const SpeciesDef& spec,
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

            TH2* source = GetHistogramForEntry(sample.file,
                                               spec,
                                               entry,
                                               Form("h2_%s_sub%zu_%s",
                                                    entry.key.Data(),
                                                    iSub,
                                                    cdef.tag));
            if (!source) continue;

            TH1D* spectrum = BuildSpectrumOneSub(
                source,
                PercentileRange(sample.mult, cdef.pTop, cdef.pBot),
                Form("h_%s_sub%zu_%s", entry.key.Data(), iSub, cdef.tag),
                xTitle,
                yTitle
            );
            delete source;

            if (spectrum) oneSubsamplePerFile.push_back(spectrum);
        }

        TH1D* combined = CombineSubsampleSpectra(
            oneSubsamplePerFile,
            Form("h_%s_%s", entry.key.Data(), cdef.tag),
            xTitle,
            yTitle
        );

        for (TH1D* hist : oneSubsamplePerFile) delete hist;
        curves.push_back(combined);
    }

    return curves;
}

std::pair<int, int> LayoutForCount(int nPads)
{
    if (nPads <= 1)  return {1, 1};
    if (nPads <= 4)  return {2, 2};
    if (nPads <= 6)  return {3, 2};
    if (nPads <= 8)  return {4, 2};
    if (nPads <= 10) return {5, 2};
    if (nPads <= 12) return {4, 3};
    if (nPads <= 15) return {5, 3};
    if (nPads <= 16) return {4, 4};
    return {5, 4};
}

int SpeciesStyleSlot(const PlotEntry& entry)
{
    const int nSlots = static_cast<int>(sizeof(kSpeciesColors) / sizeof(kSpeciesColors[0]));
    if (nSlots <= 0) return 0;
    return std::max(0, entry.speciesIndex) % nSlots;
}

void StyleSpeciesCurve(TH1D* hist, const PlotEntry& entry)
{
    if (!hist) return;

    const int slot = SpeciesStyleSlot(entry);
    hist->SetLineColor(kSpeciesColors[slot]);
    hist->SetMarkerColor(kSpeciesColors[slot]);
    hist->SetLineWidth(2);
    hist->SetFillStyle(0);
    hist->SetFillColor(0);

    if (entry.mode == kDrawBar) {
        hist->SetLineStyle(2);
        hist->SetMarkerStyle(kSpeciesMarkersOpen[slot]);
    } else if (entry.mode == kDrawParticle) {
        hist->SetLineStyle(1);
        hist->SetMarkerStyle(kSpeciesMarkersFilled[slot]);
    } else {
        hist->SetLineStyle(1);
        hist->SetMarkerStyle(kSpeciesMarkersFilled[slot]);
    }

    hist->SetMarkerSize(0.9);
}

void StyleCurve(TH1D* hist, int classIndex)
{
    if (!hist) return;

    hist->SetLineColor(kStyle[classIndex].color);
    hist->SetLineStyle(kStyle[classIndex].lstyle);
    hist->SetLineWidth(kStyle[classIndex].lwidth);
    hist->SetFillStyle(0);
    hist->SetFillColor(0);
    hist->SetMarkerColor(kStyle[classIndex].color);
    hist->SetMarkerStyle(kStyle[classIndex].marker);
    hist->SetMarkerSize(0.9);
}

void DrawEntryPad(TPad* pad,
                  const PlotEntry& entry,
                  const std::vector<TH1D*>& curves,
                  bool drawLegend,
                  const char* headerLine)
{
    if (!pad) return;

    pad->cd();
    pad->SetLogy();
    pad->SetTicks(1, 1);
    pad->SetTopMargin(0.09);
    pad->SetBottomMargin(0.16);
    pad->SetLeftMargin(0.16);
    pad->SetRightMargin(0.05);

    TH1D* frame = nullptr;
    for (TH1D* hist : curves) {
        if (!hist) continue;
        frame = hist;
        break;
    }

    if (!frame) {
        TLatex latex;
        latex.SetNDC();
        latex.SetTextSize(0.08);
        latex.DrawLatex(0.18, 0.55, entry.label.Data());
        latex.DrawLatex(0.18, 0.42, "No entries");
        return;
    }

    double yMax = 0.0;
    double yMinPositive = 1e9;

    for (TH1D* hist : curves) {
        if (!hist) continue;
        for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
            const double value = hist->GetBinContent(bin);
            const double error = hist->GetBinError(bin);
            yMax = std::max(yMax, value + error);
            if (value > 0.0) yMinPositive = std::min(yMinPositive, value);
        }
    }

    if (yMax <= 0.0) yMax = 1.0;
    const double yMin = (yMinPositive < 1e9 ? std::max(1e-6, 0.5 * yMinPositive) : 1e-6);
    const double xMax = (kFixedXMax > 0.0 ? kFixedXMax : AutoXMax(curves));

    frame->SetMinimum(yMin);
    frame->SetMaximum(1.8 * yMax);
    frame->GetXaxis()->SetRangeUser(0.0, xMax);
    frame->GetXaxis()->SetTitleSize(0.075);
    frame->GetYaxis()->SetTitleSize(0.075);
    frame->GetXaxis()->SetLabelSize(0.065);
    frame->GetYaxis()->SetLabelSize(0.065);
    frame->GetXaxis()->SetTitleOffset(0.95);
    frame->GetYaxis()->SetTitleOffset(1.0);

    for (size_t i = 0; i < curves.size(); ++i) {
        StyleCurve(curves[i], static_cast<int>(i));
    }

    bool drewFirst = false;
    for (TH1D* hist : curves) {
        if (!hist) continue;
        hist->Draw(drewFirst ? "E1 X0 SAME" : "E1 X0");
        drewFirst = true;
    }

    TLatex latex;
    latex.SetNDC();
    latex.SetTextSize(0.085);
    latex.DrawLatex(0.18, 0.88, entry.label.Data());

    if (drawLegend) {
        latex.SetTextSize(0.055);
        latex.DrawLatex(0.18, 0.78, headerLine);

        TLegend* legend = new TLegend(0.45, 0.48, 0.90, 0.76);
        legend->SetTextSize(0.07);
        for (size_t i = 0; i < kClasses.size(); ++i) {
            if (!curves[i]) continue;
            legend->AddEntry(curves[i], kClasses[i].label, "ep");
        }
        legend->Draw();
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

void DrawFlavorCanvas(const char* flavorLabel,
                      const char* tuneTag,
                      const char* dateTag,
                      const std::vector<PlotEntry>& entries,
                      const std::vector<std::vector<TH1D*> >& curvesPerEntry)
{
    if (entries.empty()) {
        std::cout << "No spectra could be built for " << flavorLabel
                  << " (" << tuneTag << ").\n";
        return;
    }

    const std::pair<int, int> layout = LayoutForCount(static_cast<int>(entries.size()));
    const int width = std::max(900, 360 * layout.first);
    const int height = std::max(700, 300 * layout.second);

    const TString canvasName = TString::Format("cSpeciesSpectra_%s_%s",
                                               flavorLabel,
                                               tuneTag);
    TCanvas* canvas = new TCanvas(canvasName.Data(), canvasName.Data(), width, height);
    canvas->Divide(layout.first, layout.second, 0.001, 0.001);

    const TString headerLine = TString::Format("%s, %s, %s",
                                               flavorLabel,
                                               tuneTag,
                                               dateTag);

    for (size_t i = 0; i < entries.size(); ++i) {
        canvas->cd(static_cast<int>(i) + 1);
        DrawEntryPad(dynamic_cast<TPad*>(gPad),
                     entries[i],
                     curvesPerEntry[i],
                     i == 0,
                     headerLine.Data());
    }

    const TString baseName = TString::Format("SpeciesResolvedSpectra_%s_%s_%s",
                                             flavorLabel,
                                             tuneTag,
                                             dateTag);
    const TString pngPath = PlotPathUtils::BuildPtMultiplicityPlotPath(baseName + ".png");
    const TString pdfPath = PlotPathUtils::BuildPtMultiplicityPlotPath(baseName + ".pdf");

    canvas->SaveAs(pngPath);
    canvas->SaveAs(pdfPath);

    std::cout << "Saved " << flavorLabel << " spectra canvas to:\n"
              << "  " << pngPath << "\n"
              << "  " << pdfPath << "\n";

    delete canvas;
}

void DrawFlavorPanel(TPad* containerPad,
                     const char* flavorLabel,
                     const char* tuneTag,
                     const char* dateTag,
                     const std::vector<PlotEntry>& entries,
                     const std::vector<std::vector<TH1D*> >& curvesPerEntry)
{
    if (!containerPad) return;

    containerPad->cd();
    containerPad->SetFillStyle(0);
    containerPad->SetMargin(0.0, 0.0, 0.0, 0.0);

    if (entries.empty()) {
        TLatex latex;
        latex.SetNDC();
        latex.SetTextSize(0.05);
        latex.DrawLatex(0.08, 0.90, Form("%s, %s, %s", flavorLabel, tuneTag, dateTag));
        latex.DrawLatex(0.08, 0.80, "No spectra could be built");
        return;
    }

    const std::pair<int, int> layout = LayoutForCount(static_cast<int>(entries.size()));
    containerPad->Divide(layout.first, layout.second, 0.001, 0.001);

    const TString headerLine = TString::Format("%s, %s, %s",
                                               flavorLabel,
                                               tuneTag,
                                               dateTag);

    for (size_t i = 0; i < entries.size(); ++i) {
        containerPad->cd(static_cast<int>(i) + 1);
        DrawEntryPad(dynamic_cast<TPad*>(gPad),
                     entries[i],
                     curvesPerEntry[i],
                     i == 0,
                     headerLine.Data());
    }
}

void DrawFlavorComparisonCanvas(const char* flavorLabel,
                                const char* dateTag,
                                const std::vector<PlotEntry>& monashEntries,
                                const std::vector<std::vector<TH1D*> >& monashCurves,
                                const std::vector<PlotEntry>& junctionEntries,
                                const std::vector<std::vector<TH1D*> >& junctionCurves)
{
    const std::pair<int, int> layoutMonash = LayoutForCount(static_cast<int>(monashEntries.size()));
    const std::pair<int, int> layoutJunctions = LayoutForCount(static_cast<int>(junctionEntries.size()));
    const int widthMonash = std::max(900, 360 * layoutMonash.first);
    const int widthJunctions = std::max(900, 360 * layoutJunctions.first);
    const int height = std::max(std::max(700, 300 * layoutMonash.second),
                                std::max(700, 300 * layoutJunctions.second));

    const TString canvasName = TString::Format("cSpeciesSpectraCompare_%s", flavorLabel);
    TCanvas* canvas = new TCanvas(canvasName.Data(),
                                  canvasName.Data(),
                                  widthMonash + widthJunctions,
                                  height);
    canvas->Divide(2, 1, 0.003, 0.003);

    canvas->cd(1);
    DrawFlavorPanel(dynamic_cast<TPad*>(gPad),
                    flavorLabel,
                    "MONASH",
                    dateTag,
                    monashEntries,
                    monashCurves);

    canvas->cd(2);
    DrawFlavorPanel(dynamic_cast<TPad*>(gPad),
                    flavorLabel,
                    "JUNCTIONS",
                    dateTag,
                    junctionEntries,
                    junctionCurves);

    const TString baseName = TString::Format("SpeciesResolvedSpectraCompareTunes_%s_%s",
                                             flavorLabel,
                                             dateTag);
    const TString pngPath = PlotPathUtils::BuildPtMultiplicityPlotPath(baseName + ".png");
    const TString pdfPath = PlotPathUtils::BuildPtMultiplicityPlotPath(baseName + ".pdf");

    canvas->SaveAs(pngPath);
    canvas->SaveAs(pdfPath);

    std::cout << "Saved side-by-side " << flavorLabel << " comparison canvas to:\n"
              << "  " << pngPath << "\n"
              << "  " << pdfPath << "\n";

    delete canvas;
}

bool ClassCurveExists(const FlavorPlotData& data, int classIndex)
{
    for (size_t iEntry = 0; iEntry < data.curves.size(); ++iEntry) {
        if (classIndex >= static_cast<int>(data.curves[iEntry].size())) continue;
        if (data.curves[iEntry][classIndex]) return true;
    }

    return false;
}

std::vector<TH1D*> CollectClassCurves(const FlavorPlotData& data, int classIndex)
{
    std::vector<TH1D*> curves;

    for (size_t iEntry = 0; iEntry < data.curves.size(); ++iEntry) {
        if (classIndex >= static_cast<int>(data.curves[iEntry].size())) continue;
        if (TH1D* hist = data.curves[iEntry][classIndex]) curves.push_back(hist);
    }

    return curves;
}

double FindOverlayYMax(const std::vector<TH1D*>& curves)
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

double FindOverlayYMinPositive(const std::vector<TH1D*>& curves)
{
    double yMinPositive = 1e9;

    for (TH1D* hist : curves) {
        if (!hist) continue;
        for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
            const double value = hist->GetBinContent(bin);
            if (value > 0.0) yMinPositive = std::min(yMinPositive, value);
        }
    }

    return (yMinPositive < 1e9 ? yMinPositive : 1e-6);
}

void DrawMultiplicityOverlayPad(TPad* pad,
                                const FlavorPlotData& data,
                                const char* flavorLabel,
                                const char* tuneTag,
                                const CDef& classDef,
                                int classIndex,
                                bool drawLegend,
                                double globalXMax,
                                double globalYMin,
                                double globalYMax)
{
    if (!pad) return;

    pad->cd();
    pad->SetLogy();
    pad->SetTicks(1, 1);
    pad->SetTopMargin(0.18);
    pad->SetBottomMargin(0.14);
    pad->SetLeftMargin(0.13);
    pad->SetRightMargin(0.04);

    TH1D* frame = nullptr;
    for (size_t iEntry = 0; iEntry < data.curves.size(); ++iEntry) {
        if (classIndex >= static_cast<int>(data.curves[iEntry].size())) continue;
        if (data.curves[iEntry][classIndex]) {
            frame = data.curves[iEntry][classIndex];
            break;
        }
    }

    TLatex latex;
    latex.SetNDC();

    if (!frame) {
        latex.SetTextSize(0.05);
        latex.DrawLatex(0.14, 0.95, Form("%s, %s", flavorLabel, tuneTag));
        latex.DrawLatex(0.14, 0.88, Form("Multiplicity: %s", classDef.label));
        latex.DrawLatex(0.14, 0.76, "No entries");
        return;
    }

    frame->SetMinimum(globalYMin);
    frame->SetMaximum(1.8 * globalYMax);
    frame->GetXaxis()->SetRangeUser(0.0, globalXMax);
    frame->GetXaxis()->SetTitleSize(0.055);
    frame->GetYaxis()->SetTitleSize(0.055);
    frame->GetXaxis()->SetLabelSize(0.048);
    frame->GetYaxis()->SetLabelSize(0.048);
    frame->GetXaxis()->SetTitleOffset(1.05);
    frame->GetYaxis()->SetTitleOffset(1.05);

    bool drewFirst = false;
    for (size_t iEntry = 0; iEntry < data.entries.size(); ++iEntry) {
        if (classIndex >= static_cast<int>(data.curves[iEntry].size())) continue;

        TH1D* hist = data.curves[iEntry][classIndex];
        if (!hist) continue;

        StyleSpeciesCurve(hist, data.entries[iEntry]);
        hist->Draw(drewFirst ? "E1 X0 SAME" : "E1 X0");
        drewFirst = true;
    }

    latex.SetTextSize(0.046);
    latex.DrawLatex(0.14, 0.96, Form("%s, %s", flavorLabel, tuneTag));
    latex.DrawLatex(0.14, 0.89, Form("Multiplicity: %s", classDef.label));

    if (drawLegend) {
        TLegend* legend = new TLegend(0.48, 0.40, 0.95, 0.78);
        legend->SetTextSize((data.entries.size() > 7) ? 0.03 : 0.036);
        if (data.entries.size() > 6) legend->SetNColumns(2);

        for (size_t iEntry = 0; iEntry < data.entries.size(); ++iEntry) {
            if (classIndex >= static_cast<int>(data.curves[iEntry].size())) continue;

            TH1D* hist = data.curves[iEntry][classIndex];
            if (!hist) continue;
            legend->AddEntry(hist, data.entries[iEntry].label, "lp");
        }

        legend->Draw();
    }
}

void DrawMultiplicityComparisonCanvasesForFlavor(const char* flavorLabel,
                                                 const char* dateTag,
                                                 const FlavorPlotData& monashData,
                                                 const FlavorPlotData& junctionsData)
{
    for (size_t iClass = 0; iClass < kClasses.size(); ++iClass) {
        const bool monashHasData = ClassCurveExists(monashData, static_cast<int>(iClass));
        const bool junctionsHasData = ClassCurveExists(junctionsData, static_cast<int>(iClass));
        if (!monashHasData && !junctionsHasData) continue;

        std::vector<TH1D*> allCurves = CollectClassCurves(monashData, static_cast<int>(iClass));
        std::vector<TH1D*> junctionCurves = CollectClassCurves(junctionsData, static_cast<int>(iClass));
        allCurves.insert(allCurves.end(), junctionCurves.begin(), junctionCurves.end());

        const double globalXMax = (kFixedXMax > 0.0 ? kFixedXMax : AutoXMax(allCurves));
        const double globalYMax = FindOverlayYMax(allCurves);
        const double globalYMin = std::max(1e-6, 0.5 * FindOverlayYMinPositive(allCurves));

        const TString canvasName = TString::Format("cSpeciesSpectraCompareTunes_%s_%s",
                                                   flavorLabel,
                                                   kClasses[iClass].tag);
        TCanvas* canvas = new TCanvas(canvasName.Data(), canvasName.Data(), 1800, 700);
        canvas->Divide(2, 1, 0.003, 0.003);

        canvas->cd(1);
        DrawMultiplicityOverlayPad(dynamic_cast<TPad*>(gPad),
                                   monashData,
                                   flavorLabel,
                                   "MONASH",
                                   kClasses[iClass],
                                   static_cast<int>(iClass),
                                   true,
                                   globalXMax,
                                   globalYMin,
                                   globalYMax);

        canvas->cd(2);
        DrawMultiplicityOverlayPad(dynamic_cast<TPad*>(gPad),
                                   junctionsData,
                                   flavorLabel,
                                   "JUNCTIONS",
                                   kClasses[iClass],
                                   static_cast<int>(iClass),
                                   true,
                                   globalXMax,
                                   globalYMin,
                                   globalYMax);

        const TString baseName = TString::Format("SpeciesResolvedSpectraCompareTunes_%s_%s_%s",
                                                 flavorLabel,
                                                 kClasses[iClass].tag,
                                                 dateTag);
        const TString pngPath = PlotPathUtils::BuildPtMultiplicityPlotPath(baseName + ".png");
        const TString pdfPath = PlotPathUtils::BuildPtMultiplicityPlotPath(baseName + ".pdf");

        canvas->SaveAs(pngPath);
        canvas->SaveAs(pdfPath);

        std::cout << "Saved " << flavorLabel << " comparison canvas for "
                  << kClasses[iClass].label << " multiplicity to:\n"
                  << "  " << pngPath << "\n"
                  << "  " << pdfPath << "\n";

        delete canvas;
    }
}

void DeleteCurves(std::vector<std::vector<TH1D*> >& curvesPerEntry)
{
    for (std::vector<TH1D*>& curves : curvesPerEntry) {
        for (TH1D* hist : curves) delete hist;
        curves.clear();
    }
}

FlavorPlotData BuildFlavorPlotData(const std::vector<SpeciesDef>& speciesDefs,
                                   const std::vector<PlotEntry>& requestedEntries,
                                   const std::vector<LoadedSample>& samples,
                                   const char* xTitle,
                                   const char* yTitle)
{
    FlavorPlotData data;
    data.entries = BuildPlotEntries(speciesDefs,
                                    requestedEntries,
                                    samples,
                                    data.singleObjectLabels,
                                    data.missingLabels);

    data.curves.reserve(data.entries.size());
    for (const PlotEntry& entry : data.entries) {
        data.curves.push_back(BuildCurvesForEntry(entry,
                                                  speciesDefs[entry.speciesIndex],
                                                  samples,
                                                  xTitle,
                                                  yTitle));
    }

    return data;
}

void PrintPlotDataSummary(const char* flavorLabel,
                          const char* tuneTag,
                          const FlavorPlotData& data)
{
    PrintLabelList(Form("%s %s species read from single histogram objects: ",
                        flavorLabel,
                        tuneTag),
                   data.singleObjectLabels);
    PrintLabelList(Form("%s %s species skipped because no usable histogram source was found: ",
                        flavorLabel,
                        tuneTag),
                   data.missingLabels);
}

void Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples_WithPrefixes(
    const char* charmPrefix,
    const char* beautyPrefix,
    const char* dateTag,
    const char* tuneTag,
    int nSub,
    bool includeHeavyBeautyExtras = false)
{
    SetStyle();

    if (nSub <= 0) {
        std::cout << "nSub must be > 0\n";
        return;
    }

    std::vector<LoadedSample> charmSamples;
    std::vector<LoadedSample> beautySamples;

    const bool charmOk = LoadSamples(charmPrefix, nSub, "Charm", charmSamples);
    const bool beautyOk = LoadSamples(beautyPrefix, nSub, "Beauty", beautySamples);

    if (!charmOk || !beautyOk) {
        CloseSamples(charmSamples);
        CloseSamples(beautySamples);
        std::cout << "Aborting due to missing files or multiplicity histograms.\n";
        return;
    }

    const char* xTitle = "p_{T} (GeV/c)";
    const char* yTitle = "Normalized counts";

    const std::vector<SpeciesDef> charmSpecies = BuildSpeciesForFlavor("Charm");
    const std::vector<SpeciesDef> beautySpecies =
        BuildSpeciesForFlavor("Beauty", includeHeavyBeautyExtras);
    const std::vector<PlotEntry> charmRequests =
        BuildRequestedEntriesForFlavor(charmSpecies, "Charm");
    const std::vector<PlotEntry> beautyRequests =
        BuildRequestedEntriesForFlavor(beautySpecies,
                                       "Beauty",
                                       includeHeavyBeautyExtras);

    FlavorPlotData charmData =
        BuildFlavorPlotData(charmSpecies, charmRequests, charmSamples, xTitle, yTitle);
    FlavorPlotData beautyData =
        BuildFlavorPlotData(beautySpecies, beautyRequests, beautySamples, xTitle, yTitle);

    PrintPlotDataSummary("Charm", tuneTag, charmData);
    PrintPlotDataSummary("Beauty", tuneTag, beautyData);

    DrawFlavorCanvas("Charm", tuneTag, dateTag, charmData.entries, charmData.curves);
    DrawFlavorCanvas("Beauty", tuneTag, dateTag, beautyData.entries, beautyData.curves);

    DeleteCurves(charmData.curves);
    DeleteCurves(beautyData.curves);
    CloseSamples(charmSamples);
    CloseSamples(beautySamples);
}

void Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples_CompareTunesForFlavor(
    const char* dateTag,
    const char* flavorTag,
    int nSub,
    bool includeHeavyBeautyExtras = false)
{
    SetStyle();

    if (nSub <= 0) {
        std::cout << "nSub must be > 0\n";
        return;
    }

    const TString resolvedDate = PlotPathUtils::ResolveAnalysisDate(dateTag);
    if (resolvedDate.Length() == 0) return;

    const TString resolvedFlavor = NormalizeFlavorTag(flavorTag);
    if (resolvedFlavor.Length() == 0) {
        std::cout << "Unknown flavor '" << flavorTag
                  << "'. Expected Charm or Beauty.\n";
        return;
    }

    const TString monashPrefix = ResolveFlavorPrefix(resolvedDate, resolvedFlavor, "MONASH");
    const TString junctionsPrefix = ResolveFlavorPrefix(resolvedDate, resolvedFlavor, "JUNCTIONS");

    std::cout << "Species-resolved HF spectra comparison input date: " << resolvedDate << "\n";
    std::cout << "  Flavor           : " << resolvedFlavor << "\n";
    std::cout << "  MONASH prefix    : " << monashPrefix << "*.root\n";
    std::cout << "  JUNCTIONS prefix : " << junctionsPrefix << "*.root\n";

    std::vector<LoadedSample> monashSamples;
    std::vector<LoadedSample> junctionsSamples;

    const bool monashOk = LoadSamples(monashPrefix.Data(), nSub, "MONASH", monashSamples);
    const bool junctionsOk = LoadSamples(junctionsPrefix.Data(), nSub, "JUNCTIONS", junctionsSamples);

    if (!monashOk || !junctionsOk) {
        CloseSamples(monashSamples);
        CloseSamples(junctionsSamples);
        std::cout << "Aborting due to missing files or multiplicity histograms.\n";
        return;
    }

    const std::vector<SpeciesDef> speciesDefs =
        BuildSpeciesForFlavor(resolvedFlavor, includeHeavyBeautyExtras);
    const std::vector<PlotEntry> requestedEntries =
        BuildRequestedEntriesForFlavor(speciesDefs,
                                       resolvedFlavor,
                                       includeHeavyBeautyExtras);
    const char* xTitle = "p_{T} (GeV/c)";
    const char* yTitle = "Normalized counts";

    FlavorPlotData monashData =
        BuildFlavorPlotData(speciesDefs,
                            requestedEntries,
                            monashSamples,
                            xTitle,
                            yTitle);
    FlavorPlotData junctionsData =
        BuildFlavorPlotData(speciesDefs,
                            requestedEntries,
                            junctionsSamples,
                            xTitle,
                            yTitle);

    PrintPlotDataSummary(resolvedFlavor.Data(), "MONASH", monashData);
    PrintPlotDataSummary(resolvedFlavor.Data(), "JUNCTIONS", junctionsData);

    DrawMultiplicityComparisonCanvasesForFlavor(resolvedFlavor.Data(),
                                                resolvedDate.Data(),
                                                monashData,
                                                junctionsData);

    DeleteCurves(monashData.curves);
    DeleteCurves(junctionsData.curves);
    CloseSamples(monashSamples);
    CloseSamples(junctionsSamples);
}

} // namespace

void Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples_ForTune(const char* dateTag = "",
                                                                        const char* tuneTag = "MONASH",
                                                                        int nSub = 10,
                                                                        bool includeHeavyBeautyExtras = false)
{
    const TString resolvedDate = PlotPathUtils::ResolveAnalysisDate(dateTag);
    if (resolvedDate.Length() == 0) return;

    const TString resolvedTune = NormalizeTuneTag(tuneTag);
    if (resolvedTune.Length() == 0) return;

    const TString charmPrefix = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate,
        "Charm",
        {TString::Format("hf_%s_sub", resolvedTune.Data()),
         TString::Format("ccbar_%s_sub", resolvedTune.Data())}
    );
    const TString beautyPrefix = PlotPathUtils::ResolveAnalyzedPrefix(
        resolvedDate,
        "Beauty",
        {TString::Format("hf_%s_sub", resolvedTune.Data()),
         TString::Format("bbbar_%s_sub", resolvedTune.Data())}
    );

    std::cout << "Species-resolved HF spectra input date: " << resolvedDate << "\n";
    std::cout << "  Tune          : " << resolvedTune << "\n";
    std::cout << "  Charm prefix  : " << charmPrefix << "*.root\n";
    std::cout << "  Beauty prefix : " << beautyPrefix << "*.root\n";

    Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples_WithPrefixes(
        charmPrefix.Data(),
        beautyPrefix.Data(),
        resolvedDate.Data(),
        resolvedTune.Data(),
        nSub,
        includeHeavyBeautyExtras
    );
}

void Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples(const char* dateTag = "",
                                                                const char* selectorTag = "Charm",
                                                                int nSub = 10,
                                                                bool includeHeavyBeautyExtras = false)
{
    const TString resolvedTune = NormalizeTuneTagQuiet(selectorTag);
    if (resolvedTune.Length() > 0) {
        Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples_ForTune(dateTag,
                                                                           resolvedTune.Data(),
                                                                           nSub,
                                                                           includeHeavyBeautyExtras);
        return;
    }

    const TString resolvedFlavor = NormalizeFlavorTag(selectorTag);
    if (resolvedFlavor.Length() > 0) {
        Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples_CompareTunesForFlavor(
            dateTag,
            resolvedFlavor.Data(),
            nSub,
            includeHeavyBeautyExtras
        );
        return;
    }

    std::cout << "Unknown selector '" << selectorTag
              << "'. Expected Charm, Beauty, MONASH, JUNCTIONS, or CLOSEPACKING.\n";
}

void runHFSpeciesResolvedSpectra(const char* dateTag = "",
                                 const char* selectorTag = "Charm",
                                 int nSub = 10,
                                 bool includeHeavyBeautyExtras = false)
{
    Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples(dateTag,
                                                               selectorTag,
                                                               nSub,
                                                               includeHeavyBeautyExtras);
}

void runHFSpeciesResolvedSpectraWithPrefixes(const char* charmPrefix,
                                             const char* beautyPrefix,
                                             const char* dateTag,
                                             const char* tuneTag,
                                             int nSub = 10,
                                             bool includeHeavyBeautyExtras = false)
{
    const TString resolvedTune = NormalizeTuneTag(tuneTag);
    if (resolvedTune.Length() == 0) return;

    Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples_WithPrefixes(
        charmPrefix,
        beautyPrefix,
        dateTag,
        resolvedTune.Data(),
        nSub,
        includeHeavyBeautyExtras
    );
}

void runHFSpeciesResolvedSpectraMonash(const char* dateTag = "",
                                       int nSub = 10,
                                       bool includeHeavyBeautyExtras = false)
{
    Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples_ForTune(dateTag,
                                                                       "MONASH",
                                                                       nSub,
                                                                       includeHeavyBeautyExtras);
}

void runHFSpeciesResolvedSpectraJunctions(const char* dateTag = "",
                                          int nSub = 10,
                                          bool includeHeavyBeautyExtras = false)
{
    Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples_ForTune(dateTag,
                                                                       "JUNCTIONS",
                                                                       nSub,
                                                                       includeHeavyBeautyExtras);
}

void runHFSpeciesResolvedSpectraCharm(const char* dateTag = "",
                                      int nSub = 10,
                                      bool includeHeavyBeautyExtras = false)
{
    Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples(dateTag,
                                                               "Charm",
                                                               nSub,
                                                               includeHeavyBeautyExtras);
}

void runHFSpeciesResolvedSpectraBeauty(const char* dateTag = "",
                                       int nSub = 10,
                                       bool includeHeavyBeautyExtras = false)
{
    Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples(dateTag,
                                                               "Beauty",
                                                               nSub,
                                                               includeHeavyBeautyExtras);
}

void runHFSpeciesResolvedSpectraBothTunes(const char* dateTag = "",
                                          int nSub = 10,
                                          bool includeHeavyBeautyExtras = false)
{
    Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples(dateTag,
                                                               "Charm",
                                                               nSub,
                                                               includeHeavyBeautyExtras);
    Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples(dateTag,
                                                               "Beauty",
                                                               nSub,
                                                               includeHeavyBeautyExtras);
}
