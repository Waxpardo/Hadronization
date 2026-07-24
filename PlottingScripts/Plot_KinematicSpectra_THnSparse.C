// ---------------------------------------------------------------------------
// Plot_KinematicSpectra_THnSparse.C
//
// Draw one-dimensional kinematic spectra from the THnSparse pair files used by
// Paul's plotting macro. The macro reads the same JSON configuration, so tune
// names, complete-root paths, and subsample paths stay synchronized.
//
// Default usage from the Hadronization repository root:
//
//   root -l -b -q 'PlottingScripts/Plot_KinematicSpectra_THnSparse.C'
//
// The output deliberately keeps event-level spectra, such as charged-particle
// multiplicity, shared across charm and beauty. These spectra come from the
// same HF event sample and should not be duplicated as separate charm/beauty
// paper plots.
// ---------------------------------------------------------------------------

#include <algorithm>
#include <cctype>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "TCanvas.h"
#include "TFile.h"
#include "TH1D.h"
#include "THnSparse.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TObject.h"
#include "TString.h"
#include "TStyle.h"
#include "TSystem.h"

#include "HistogramErrorUtils.h"
#include "TunePlotStyle.h"

#if __has_include(<nlohmann/json.hpp>)
#include <nlohmann/json.hpp>
#elif __has_include("nlohmann/json.hpp")
#include "nlohmann/json.hpp"
#else
#error "Could not find nlohmann/json.hpp. Source the project/ROOT environment before compiling this macro."
#endif

using json = nlohmann::json;

namespace KinematicSpectraPlot {

enum class Flavor {
    Beauty,
    Charm
};

enum class FileRole {
    OS,
    SS
};

enum class SourceKind {
    Multiplicity,
    TriggerKinematics,
    AssociateKinematics,
    Correlations
};

enum class PhiAxisPolicy {
    Strict,
    Native,
    LegacyRepair
};

struct PairConfig {
    Flavor flavor;
    std::string triggerLabel;
    std::string associateOSLabel;
    std::string associateSSLabel;
    std::string osFileName;
    std::string ssFileName;
};

struct PlotConfig {
    std::string hadronizationBase;
    std::string baseDir;
    std::string outputDir;
    std::string beautyCompleteRootDir;
    std::string charmCompleteRootDir;
    std::string beautySubsampleRootDir;
    std::string charmSubsampleRootDir;
    std::vector<std::string> tunes;
    std::vector<PairConfig> beautyPairs;
    std::vector<PairConfig> charmPairs;
    bool calculateErrors = false;
    int nSubSamples = 0;
};

struct SpectrumDef {
    std::string key;
    std::string title;
    std::string xTitle;
    std::string yTitleCounts;
    std::string yTitleShape;
    SourceKind sourceKind;
    int axis = -1;
    bool logY = false;
};

struct SampleRequest {
    Flavor flavor;
    FileRole role;
    std::string fileName;
    std::string displayLabel;
    bool sharedEventSample = false;
};

struct LoadedHistogram {
    TH1D* hist = nullptr;
    std::string tune;
};

std::string SourceKindName(SourceKind sourceKind)
{
    switch (sourceKind) {
        case SourceKind::Multiplicity:
            return "Multiplicity";
        case SourceKind::TriggerKinematics:
            return "Trigger";
        case SourceKind::AssociateKinematics:
            return "Associate";
        case SourceKind::Correlations:
            return "Correlation";
    }
    return "Other";
}

std::string JoinPath(const std::vector<std::string>& pieces)
{
    std::string path;
    for (const auto& piece : pieces) {
        if (piece.empty()) continue;
        if (!path.empty() && path.back() != '/') path += "/";
        if (!path.empty() && piece.front() == '/') {
            path += piece.substr(1);
        } else {
            path += piece;
        }
    }
    return path;
}

bool IsAbsolutePath(const std::string& path)
{
    return !path.empty() && (path.front() == '/' || (path.size() > 1 && path[1] == ':'));
}

std::string ParentPath(const std::string& path)
{
    if (path.empty() || path == "/") return path;
    const size_t slash = path.find_last_of('/');
    if (slash == std::string::npos) return "";
    if (slash == 0) return "/";
    return path.substr(0, slash);
}

std::string ExpandPath(const std::string& path)
{
    char* expanded = gSystem->ExpandPathName(path.c_str());
    std::string result = expanded ? expanded : path;
    if (expanded) delete[] expanded;
    return result;
}

bool PathExists(const std::string& path)
{
    return !path.empty() && !gSystem->AccessPathName(path.c_str());
}

std::string FindHadronizationBase()
{
    const char* envBase = std::getenv("HADRONIZATION_BASE");
    if (envBase && PathExists(JoinPath({envBase, "PlottingScripts"}))) {
        return ExpandPath(envBase);
    }

    std::string current = ExpandPath(gSystem->WorkingDirectory());
    while (!current.empty()) {
        if (PathExists(JoinPath({current, "PlottingScripts"})) ||
            PathExists(JoinPath({current, ".git"}))) {
            return current;
        }
        const std::string parent = ParentPath(current);
        if (parent == current) break;
        current = parent;
    }

    return ExpandPath(gSystem->WorkingDirectory());
}

std::string ResolvePathFromBase(const std::string& path, const std::string& hadronizationBase)
{
    if (path.empty() || path == "NONE") return path;
    const std::string expanded = ExpandPath(path);
    if (IsAbsolutePath(expanded)) return expanded;
    return JoinPath({hadronizationBase, expanded});
}

std::string ResolveConfigurationPath(const std::string& path, const std::string& hadronizationBase)
{
    const std::vector<std::string> candidates = {
        path,
        ResolvePathFromBase(path, hadronizationBase),
        JoinPath({hadronizationBase, "PlottingScripts", path})
    };

    for (const auto& candidate : candidates) {
        if (PathExists(candidate)) return candidate;
    }

    std::ostringstream message;
    message << "Could not find configuration file '" << path << "'. Tried:";
    for (const auto& candidate : candidates) message << "\n  - " << candidate;
    throw std::runtime_error(message.str());
}

std::string FlavorName(Flavor flavor)
{
    return flavor == Flavor::Beauty ? "Beauty" : "Charm";
}

std::string FlavorNameUpper(Flavor flavor)
{
    return flavor == Flavor::Beauty ? "BEAUTY" : "CHARM";
}

std::string SanitizeToken(std::string value)
{
    if (value.empty()) return "unnamed";

    for (char& c : value) {
        const bool keep =
            (c >= 'A' && c <= 'Z') ||
            (c >= 'a' && c <= 'z') ||
            (c >= '0' && c <= '9');
        if (!keep) c = '_';
    }

    while (value.find("__") != std::string::npos) {
        value.replace(value.find("__"), 2, "_");
    }
    if (!value.empty() && value.front() == '_') value.erase(value.begin());
    if (!value.empty() && value.back() == '_') value.pop_back();
    return value.empty() ? "unnamed" : value;
}

std::string StripRootExtension(std::string fileName)
{
    const std::string suffix = ".root";
    if (fileName.size() >= suffix.size() &&
        fileName.substr(fileName.size() - suffix.size()) == suffix) {
        fileName.resize(fileName.size() - suffix.size());
    }
    return fileName;
}

std::string SpectrumDirectoryName(const SpectrumDef& spectrum)
{
    if (spectrum.sourceKind == SourceKind::Multiplicity) return "Multiplicity";
    return SanitizeToken(spectrum.key);
}

std::string OutputSubdirectory(const SpectrumDef& spectrum)
{
    if (spectrum.sourceKind == SourceKind::Multiplicity) {
        return SpectrumDirectoryName(spectrum);
    }
    return JoinPath({SourceKindName(spectrum.sourceKind), SpectrumDirectoryName(spectrum)});
}

std::string TriggerParticleLatex(Flavor flavor)
{
    return flavor == Flavor::Beauty ? "#it{B}^{+}" : "#it{D}^{+}";
}

std::string AssociateParticleLatex(const std::string& fileName)
{
    const std::map<std::string, std::string> labels = {
        {"BplusBminus.root", "#it{B}^{-}"},
        {"BplusBplus.root", "#it{B}^{+}"},
        {"BplusLb.root", "#Lambda_{b}"},
        {"BplusLbbar.root", "#bar{#Lambda}_{b}"},
        {"BplusSigmabzero.root", "#Sigma_{b}^{0}"},
        {"BplusSigmabzerobar.root", "#bar{#Sigma}_{b}^{0}"},
        {"DplusDminus.root", "#it{D}^{-}"},
        {"DplusDplus.root", "#it{D}^{+}"},
        {"DplusLambdacplusbar.root", "#bar{#Lambda}_{c}^{-}"},
        {"DplusLambdacplus.root", "#Lambda_{c}^{+}"}
    };

    const auto found = labels.find(fileName);
    if (found != labels.end()) return found->second;
    return StripRootExtension(fileName);
}

std::string PairParticleLatex(Flavor flavor, const std::string& fileName)
{
    return TriggerParticleLatex(flavor) + " " + AssociateParticleLatex(fileName);
}

std::string RoleName(FileRole role)
{
    return role == FileRole::OS ? "OS" : "SS";
}

std::string CompleteRootDirForFlavor(const PlotConfig& config, Flavor flavor)
{
    return flavor == Flavor::Beauty ? config.beautyCompleteRootDir : config.charmCompleteRootDir;
}

std::string SubsampleRootDirForFlavor(const PlotConfig& config, Flavor flavor)
{
    return flavor == Flavor::Beauty ? config.beautySubsampleRootDir : config.charmSubsampleRootDir;
}

std::string ResolveCompleteRootFile(const std::string& baseDir,
                                    const std::string& tune,
                                    const std::string& completeRootDir,
                                    const std::string& fileName)
{
    const std::vector<std::string> candidates = {
        JoinPath({baseDir, tune, completeRootDir + "_" + tune, fileName}),
        JoinPath({baseDir, tune, completeRootDir, fileName}),
        JoinPath({baseDir, completeRootDir + "_" + tune, fileName}),
        JoinPath({baseDir, completeRootDir, fileName})
    };

    for (const auto& candidate : candidates) {
        if (PathExists(candidate)) return candidate;
    }

    std::ostringstream message;
    message << "Could not find input ROOT file '" << fileName << "' for tune "
            << tune << ". Tried:";
    for (const auto& candidate : candidates) message << "\n  - " << candidate;
    throw std::runtime_error(message.str());
}

std::string ResolveSubSampleRootFile(const std::string& subSampleBaseDir,
                                     const std::string& tune,
                                     int subSampleIndex,
                                     const std::string& fileName)
{
    const std::string subSampleDir = Form("combined_root_%i", subSampleIndex);
    const std::vector<std::string> candidates = {
        JoinPath({subSampleBaseDir + "_" + tune, subSampleDir, fileName}),
        JoinPath({subSampleBaseDir, tune, subSampleDir, fileName})
    };

    for (const auto& candidate : candidates) {
        if (PathExists(candidate)) return candidate;
    }

    std::ostringstream message;
    message << "Could not find subsample ROOT file '" << fileName << "' for tune "
            << tune << ", subsample " << subSampleIndex << ". Tried:";
    for (const auto& candidate : candidates) message << "\n  - " << candidate;
    throw std::runtime_error(message.str());
}

TFile* OpenRootFile(const std::string& path, bool strictInputs)
{
    TFile* file = TFile::Open(path.c_str(), "READ");
    if (!file || file->IsZombie()) {
        if (file) file->Close();
        if (strictInputs) throw std::runtime_error("Could not open input ROOT file: " + path);
        std::cerr << "WARNING: could not open input ROOT file: " << path << std::endl;
        return nullptr;
    }
    return file;
}

template <class T>
T* GetObject(TFile* file, const std::string& objectName, const std::string& filePath, bool strictInputs)
{
    if (!file) return nullptr;

    T* object = dynamic_cast<T*>(file->Get(objectName.c_str()));
    if (!object && strictInputs) {
        throw std::runtime_error("Missing '" + objectName + "' in " + filePath);
    }
    if (!object) {
        std::cerr << "WARNING: missing '" << objectName << "' in " << filePath << std::endl;
    }
    return object;
}

std::vector<PairConfig> ReadPairs(const json& config, const char* key, Flavor flavor)
{
    std::vector<PairConfig> pairs;
    if (!config.contains(key) || !config[key].is_array()) return pairs;

    const auto appendPair = [&pairs, flavor](const json& entry, const std::string& groupTrigger) {
        PairConfig pair;
        pair.flavor = flavor;
        pair.triggerLabel = entry.value("trigger", groupTrigger);
        pair.associateOSLabel = entry.value("associateOS", "");
        pair.associateSSLabel = entry.value("associateSS", "");
        pair.osFileName = entry.value("OS", "");
        pair.ssFileName = entry.value("SS", "");
        if (!pair.osFileName.empty()) pairs.push_back(pair);
    };

    for (const auto& entry : config[key]) {
        if (entry.contains("configs") && entry["configs"].is_array()) {
            const std::string groupTrigger = entry.value("trigger", "");
            for (const auto& nested : entry["configs"]) {
                appendPair(nested, groupTrigger);
            }
        } else {
            appendPair(entry, "");
        }
    }

    return pairs;
}

PlotConfig ReadConfig(const char* configuration, const char* outputDir)
{
    PlotConfig configOut;
    configOut.hadronizationBase = FindHadronizationBase();

    const std::string configPath =
        ResolveConfigurationPath(configuration, configOut.hadronizationBase);
    std::ifstream input(configPath);
    if (!input.is_open()) {
        throw std::runtime_error("Could not open configuration file: " + configPath);
    }

    json config = json::parse(input);
    configOut.baseDir =
        ResolvePathFromBase(config["base_dir"].get<std::string>(), configOut.hadronizationBase);
    configOut.outputDir = ResolvePathFromBase(outputDir, configOut.hadronizationBase);
    configOut.beautyCompleteRootDir = config["bb_bar_complete_root_dir"].get<std::string>();
    configOut.charmCompleteRootDir = config["cc_bar_complete_root_dir"].get<std::string>();
    configOut.beautySubsampleRootDir =
        ResolvePathFromBase(config.value("bb_bar_complete_root_dir_sub_samples", "NONE"),
                            configOut.hadronizationBase);
    configOut.charmSubsampleRootDir =
        ResolvePathFromBase(config.value("cc_bar_complete_root_dir_sub_samples", "NONE"),
                            configOut.hadronizationBase);
    configOut.calculateErrors = config.value("calculate_errors", false);
    configOut.nSubSamples = config.value("nSubSamples", 0);

    for (const auto& tune : config["PYTHIA_TUNES"]) {
        configOut.tunes.push_back(tune.get<std::string>());
    }
    configOut.beautyPairs = ReadPairs(config, "beauty_correlations_to_analyse", Flavor::Beauty);
    configOut.charmPairs = ReadPairs(config, "charm_correlations_to_analyse", Flavor::Charm);

    return configOut;
}

std::vector<SpectrumDef> KinematicSpectra()
{
    return {
        {"pT", "#it{p}_{T}", "#it{p}_{T} (GeV/#it{c})", "Counts", "Normalized counts",
         SourceKind::TriggerKinematics, 2, true},
        {"eta", "#eta", "#eta", "Counts", "Normalized counts",
         SourceKind::TriggerKinematics, 1, false},
        {"phi", "#phi", "#phi", "Counts", "Normalized counts",
         SourceKind::TriggerKinematics, 0, false}
    };
}

std::vector<SpectrumDef> CorrelationSpectra()
{
    return {
        {"deltaPhi", "#Delta#phi", "#Delta#phi", "Counts", "Normalized counts",
         SourceKind::Correlations, 0, false},
        {"deltaEta", "#Delta#eta", "#Delta#eta", "Counts", "Normalized counts",
         SourceKind::Correlations, 1, false}
    };
}

SpectrumDef MultiplicitySpectrum()
{
    return {"multiplicity", "charged-particle multiplicity", "Charged-particle multiplicity N_{ch}",
            "Counts", "Normalized events", SourceKind::Multiplicity, -1, true};
}

double Pi()
{
    return std::acos(-1.0);
}

bool IsSingleParticlePhiSpectrum(const SpectrumDef& spectrum)
{
    return spectrum.key == "phi" &&
           (spectrum.sourceKind == SourceKind::TriggerKinematics ||
            spectrum.sourceKind == SourceKind::AssociateKinematics);
}

bool IsDeltaPhiSpectrum(const SpectrumDef& spectrum)
{
    return spectrum.key == "deltaPhi" &&
           spectrum.sourceKind == SourceKind::Correlations;
}

bool NearlyEqual(double a, double b, double tolerance = 1.0e-6)
{
    return std::abs(a - b) < tolerance;
}

std::string ToLower(std::string value)
{
    std::transform(value.begin(), value.end(), value.begin(),
                   [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
    return value;
}

PhiAxisPolicy ParsePhiAxisPolicy(const char* value)
{
    const std::string policy = ToLower(value ? value : "strict");
    if (policy == "strict") return PhiAxisPolicy::Strict;
    if (policy == "native") return PhiAxisPolicy::Native;
    if (policy == "legacy" || policy == "legacy-repair" || policy == "legacy_repair") {
        return PhiAxisPolicy::LegacyRepair;
    }

    throw std::runtime_error(
        "Unknown phi axis policy '" + policy +
        "'. Use strict, native, or legacy-repair.");
}

std::string PhiAxisPolicyName(PhiAxisPolicy policy)
{
    switch (policy) {
        case PhiAxisPolicy::Strict:
            return "strict";
        case PhiAxisPolicy::Native:
            return "native";
        case PhiAxisPolicy::LegacyRepair:
            return "legacy-repair";
    }
    return "unknown";
}

double WrapToMinusPiPi(double phi)
{
    const double pi = Pi();
    const double twoPi = 2.0 * pi;
    while (phi < -pi) phi += twoPi;
    while (phi >= pi) phi -= twoPi;
    return phi;
}

bool AxisRangeIs(TAxis* axis, double xmin, double xmax)
{
    return axis && NearlyEqual(axis->GetXmin(), xmin) && NearlyEqual(axis->GetXmax(), xmax);
}

std::string AxisRangeString(TAxis* axis)
{
    if (!axis) return "[missing axis]";
    std::ostringstream stream;
    stream << "[" << axis->GetXmin() << ", " << axis->GetXmax() << "]";
    return stream.str();
}

std::string FlowString(TH1D* hist)
{
    if (!hist) return "underflow=missing overflow=missing";
    std::ostringstream stream;
    stream << "underflow=" << hist->GetBinContent(0)
           << " overflow=" << hist->GetBinContent(hist->GetNbinsX() + 1);
    return stream.str();
}

void ValidateSingleParticlePhiAxis(TAxis* axis,
                                   const std::string& filePath,
                                   const std::string& sourceName,
                                   PhiAxisPolicy policy)
{
    const double pi = Pi();
    if (AxisRangeIs(axis, -pi, pi)) return;

    std::ostringstream message;
    message << "Single-particle absolute phi axis in " << sourceName
            << " must be [-pi, pi] for final plots. File: " << filePath
            << ". Stored axis is " << AxisRangeString(axis) << ". ";

    if (policy == PhiAxisPolicy::Strict) {
        message << "Regenerate the THnSparse status-analysis outputs with "
                << "hTrKinematics/hAsKinematics booked as [-pi, pi], or rerun "
                << "with KINEMATIC_PHI_POLICY=native/legacy-repair for diagnostics only.";
        throw std::runtime_error(message.str());
    }

    std::cerr << "WARNING: " << message.str()
              << "Using phi policy " << PhiAxisPolicyName(policy)
              << "; do not use this as a final absolute-phi QA plot." << std::endl;
}

void ValidateDeltaPhiAxis(TAxis* axis,
                          const std::string& filePath,
                          const std::string& sourceName,
                          bool strictInputs)
{
    const double pi = Pi();
    if (AxisRangeIs(axis, -0.5 * pi, 1.5 * pi)) return;

    std::ostringstream message;
    message << "Correlation delta-phi axis in " << sourceName
            << " should be [-pi/2, 3pi/2] for Paul's correlation convention. File: "
            << filePath << ". Stored axis is " << AxisRangeString(axis) << ".";
    if (strictInputs) throw std::runtime_error(message.str());
    std::cerr << "WARNING: " << message.str() << std::endl;
}

void ValidateSingleParticlePhiFlow(TH1D* hist,
                                   const std::string& filePath,
                                   const std::string& sourceName,
                                   bool strictInputs)
{
    if (!hist) return;
    const double underflow = hist->GetBinContent(0);
    const double overflow = hist->GetBinContent(hist->GetNbinsX() + 1);
    if (underflow == 0.0 && overflow == 0.0) return;

    std::ostringstream message;
    message << "Single-particle absolute phi projection in " << sourceName
            << " has nonzero flow bins (" << FlowString(hist) << "). File: "
            << filePath << ". This means the plotted phi spectrum is not fully represented "
            << "by normal bins.";
    if (strictInputs) throw std::runtime_error(message.str());
    std::cerr << "WARNING: " << message.str() << std::endl;
}

TH1D* RemapLegacyPhiHistogramToMinusPiPi(TH1D* hist,
                                         const std::string& filePath,
                                         const std::string& sourceName)
{
    if (!hist) return nullptr;

    const double pi = Pi();
    TAxis* axis = hist->GetXaxis();
    if (NearlyEqual(axis->GetXmin(), -pi) && NearlyEqual(axis->GetXmax(), pi)) {
        return hist;
    }

    const std::string originalName = hist->GetName();
    const int nBins = hist->GetNbinsX();
    TH1D* remapped = new TH1D((originalName + "_minusPiPi").c_str(), "",
                              nBins, -pi, pi);
    remapped->SetDirectory(nullptr);
    remapped->Sumw2();

    for (int bin = 1; bin <= nBins; ++bin) {
        const double wrappedCenter = WrapToMinusPiPi(axis->GetBinCenter(bin));
        const int targetBin = remapped->GetXaxis()->FindFixBin(wrappedCenter);
        if (targetBin < 1 || targetBin > remapped->GetNbinsX()) continue;

        const double content = remapped->GetBinContent(targetBin) + hist->GetBinContent(bin);
        const double error2 = std::pow(remapped->GetBinError(targetBin), 2) +
                              std::pow(hist->GetBinError(bin), 2);
        remapped->SetBinContent(targetBin, content);
        remapped->SetBinError(targetBin, std::sqrt(error2));
    }

    std::cerr << "WARNING: legacy single-particle phi repair for " << sourceName
              << " in " << filePath << ". Stored axis is "
              << AxisRangeString(axis) << " with " << FlowString(hist)
              << ". The missing display interval is reconstructed from flow bins and "
              << "is not suitable for final phi QA." << std::endl;

    if (axis->GetXmin() > -pi && hist->GetBinContent(0) != 0.0) {
        std::vector<int> missingBins;
        for (int bin = 1; bin <= remapped->GetNbinsX(); ++bin) {
            if (remapped->GetXaxis()->GetBinCenter(bin) < axis->GetXmin()) {
                missingBins.push_back(bin);
            }
        }

        if (!missingBins.empty()) {
            const double underflowContent = hist->GetBinContent(0);
            const double underflowError = hist->GetBinError(0);
            const double perBinContent =
                underflowContent / static_cast<double>(missingBins.size());
            const double perBinError =
                underflowError / std::sqrt(static_cast<double>(missingBins.size()));

            for (int bin : missingBins) {
                const double content = remapped->GetBinContent(bin) + perBinContent;
                const double error2 = std::pow(remapped->GetBinError(bin), 2) +
                                      std::pow(perBinError, 2);
                remapped->SetBinContent(bin, content);
                remapped->SetBinError(bin, std::sqrt(error2));
            }
        }
    }

    remapped->SetEntries(hist->GetEntries());
    delete hist;
    remapped->SetName(originalName.c_str());
    return remapped;
}

TH1D* HandleSingleParticlePhiHistogram(TH1D* hist,
                                       const std::string& filePath,
                                       const std::string& sourceName,
                                       PhiAxisPolicy policy,
                                       bool strictInputs)
{
    if (!hist) return nullptr;

    const double pi = Pi();
    TAxis* axis = hist->GetXaxis();
    if (AxisRangeIs(axis, -pi, pi)) {
        ValidateSingleParticlePhiFlow(hist, filePath, sourceName, strictInputs);
        return hist;
    }

    if (policy == PhiAxisPolicy::LegacyRepair) {
        return RemapLegacyPhiHistogramToMinusPiPi(hist, filePath, sourceName);
    }

    return hist;
}

void NormalizeShape(TH1D* hist)
{
    if (!hist) return;
    PlotErrorUtils::NormalizeToUnitShape(hist);
}

void ApplyBinWidthNormalization(TH1D* hist)
{
    if (!hist) return;
    hist->Sumw2();
    for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
        const double width = hist->GetBinWidth(bin);
        if (width <= 0.0) continue;
        hist->SetBinContent(bin, hist->GetBinContent(bin) / width);
        hist->SetBinError(bin, hist->GetBinError(bin) / width);
    }
}

void ResetSparseRanges(THnSparseD* sparse)
{
    if (!sparse) return;
    for (int axis = 0; axis < sparse->GetNdimensions(); ++axis) {
        sparse->GetAxis(axis)->SetRange();
    }
}

TH1D* CloneMultiplicityHistogram(TFile* file,
                                 const std::string& filePath,
                                 const char* cloneName,
                                 bool strictInputs)
{
    TH1D* source = GetObject<TH1D>(file, "summed MULTIPLICITY", filePath, strictInputs);
    if (!source) return nullptr;

    TH1D* hist = dynamic_cast<TH1D*>(source->Clone(cloneName));
    if (!hist) return nullptr;
    hist->SetDirectory(nullptr);
    hist->Sumw2();
    return hist;
}

TH1D* ProjectSparseAxis(TFile* file,
                        const std::string& filePath,
                        const SpectrumDef& spectrum,
                        const char* cloneName,
                        bool strictInputs,
                        PhiAxisPolicy phiAxisPolicy)
{
    std::string sourceName;
    if (spectrum.sourceKind == SourceKind::TriggerKinematics) {
        sourceName = "hTrKinematics";
    } else if (spectrum.sourceKind == SourceKind::AssociateKinematics) {
        sourceName = "hAsKinematics";
    } else if (spectrum.sourceKind == SourceKind::Correlations) {
        sourceName = "hCorrelations";
    } else {
        throw std::runtime_error("ProjectSparseAxis called with non-THnSparse spectrum");
    }

    THnSparseD* sparse = GetObject<THnSparseD>(file, sourceName, filePath, strictInputs);
    if (!sparse) return nullptr;
    if (spectrum.axis < 0 || spectrum.axis >= sparse->GetNdimensions()) {
        throw std::runtime_error("Invalid axis " + std::to_string(spectrum.axis) +
                                 " for " + sourceName + " in " + filePath);
    }

    TAxis* projectedAxis = sparse->GetAxis(spectrum.axis);
    if (IsSingleParticlePhiSpectrum(spectrum)) {
        ValidateSingleParticlePhiAxis(projectedAxis, filePath, sourceName, phiAxisPolicy);
    } else if (IsDeltaPhiSpectrum(spectrum)) {
        ValidateDeltaPhiAxis(projectedAxis, filePath, sourceName, strictInputs);
    }

    ResetSparseRanges(sparse);
    TH1D* hist = dynamic_cast<TH1D*>(sparse->Projection(spectrum.axis, "E"));
    ResetSparseRanges(sparse);
    if (!hist) return nullptr;

    hist->SetName(cloneName);
    hist->SetTitle("");
    hist->SetDirectory(nullptr);
    hist->Sumw2();
    if (IsSingleParticlePhiSpectrum(spectrum)) {
        hist = HandleSingleParticlePhiHistogram(hist, filePath, sourceName,
                                                phiAxisPolicy, strictInputs);
    }
    return hist;
}

TH1D* LoadSpectrumFromFile(const std::string& filePath,
                           const SpectrumDef& spectrum,
                           const char* cloneName,
                           bool normalizeShape,
                           bool strictInputs,
                           PhiAxisPolicy phiAxisPolicy)
{
    std::unique_ptr<TFile> file(OpenRootFile(filePath, strictInputs));
    if (!file) return nullptr;

    TH1D* hist = nullptr;
    if (spectrum.sourceKind == SourceKind::Multiplicity) {
        hist = CloneMultiplicityHistogram(file.get(), filePath, cloneName, strictInputs);
    } else {
        hist = ProjectSparseAxis(file.get(), filePath, spectrum, cloneName,
                                 strictInputs, phiAxisPolicy);
    }

    if (!hist) return nullptr;
    if (normalizeShape) {
        NormalizeShape(hist);
    } else {
        ApplyBinWidthNormalization(hist);
    }
    return hist;
}

void ApplySubsampleErrors(TH1D* central, const std::vector<TH1D*>& subsamples)
{
    if (!central || subsamples.size() < 2) return;

    for (int bin = 1; bin <= central->GetNbinsX(); ++bin) {
        double mean = 0.0;
        int n = 0;
        for (TH1D* sub : subsamples) {
            if (!sub || bin > sub->GetNbinsX()) continue;
            mean += sub->GetBinContent(bin);
            ++n;
        }
        if (n < 2) continue;
        mean /= static_cast<double>(n);

        double variance = 0.0;
        for (TH1D* sub : subsamples) {
            if (!sub || bin > sub->GetNbinsX()) continue;
            const double diff = sub->GetBinContent(bin) - mean;
            variance += diff * diff;
        }
        variance /= static_cast<double>(n - 1);
        central->SetBinError(bin, std::sqrt(std::max(0.0, variance) / n));
    }
}

TH1D* LoadSpectrum(const PlotConfig& config,
                   const std::string& tune,
                   const SampleRequest& request,
                   const SpectrumDef& spectrum,
                   bool normalizeShape,
                   bool useSubsampleErrors,
                   bool strictInputs,
                   PhiAxisPolicy phiAxisPolicy)
{
    const std::string completeDir = CompleteRootDirForFlavor(config, request.flavor);
    const std::string filePath =
        ResolveCompleteRootFile(config.baseDir, tune, completeDir, request.fileName);
    const std::string cloneName =
        "h_" + SanitizeToken(spectrum.key) + "_" + SanitizeToken(tune) + "_" +
        SanitizeToken(request.displayLabel);

    TH1D* central =
        LoadSpectrumFromFile(filePath, spectrum, cloneName.c_str(), normalizeShape,
                             strictInputs, phiAxisPolicy);
    if (!central) return nullptr;

    if (useSubsampleErrors && config.calculateErrors && config.nSubSamples > 1) {
        std::vector<TH1D*> subsamples;
        const std::string subSampleDir = SubsampleRootDirForFlavor(config, request.flavor);
        if (subSampleDir != "NONE" && !subSampleDir.empty()) {
            for (int iSub = 1; iSub <= config.nSubSamples; ++iSub) {
                try {
                    const std::string subPath =
                        ResolveSubSampleRootFile(subSampleDir, tune, iSub, request.fileName);
                    const std::string subName = cloneName + "_sub" + std::to_string(iSub);
                    TH1D* subHist =
                        LoadSpectrumFromFile(subPath, spectrum, subName.c_str(),
                                             normalizeShape, strictInputs, phiAxisPolicy);
                    if (subHist) subsamples.push_back(subHist);
                } catch (const std::exception& error) {
                    if (strictInputs) {
                        for (TH1D* hist : subsamples) delete hist;
                        delete central;
                        throw;
                    }
                    std::cerr << "WARNING: " << error.what() << std::endl;
                }
            }
            ApplySubsampleErrors(central, subsamples);
            for (TH1D* hist : subsamples) delete hist;
        }
    }

    return central;
}

SampleRequest FirstAvailableSharedSample(const PlotConfig& config,
                                         const std::string& tune,
                                         bool strictInputs)
{
    std::vector<SampleRequest> candidates;
    if (!config.beautyPairs.empty()) {
        candidates.push_back({Flavor::Beauty, FileRole::OS, config.beautyPairs.front().osFileName,
                              "SharedEventSample", true});
    }
    if (!config.charmPairs.empty()) {
        candidates.push_back({Flavor::Charm, FileRole::OS, config.charmPairs.front().osFileName,
                              "SharedEventSample", true});
    }

    for (const auto& request : candidates) {
        try {
            ResolveCompleteRootFile(config.baseDir, tune,
                                    CompleteRootDirForFlavor(config, request.flavor),
                                    request.fileName);
            return request;
        } catch (const std::exception&) {
        }
    }

    if (strictInputs) {
        throw std::runtime_error("Could not find any shared multiplicity input file for tune " + tune);
    }
    return candidates.empty()
        ? SampleRequest{Flavor::Beauty, FileRole::OS, "", "SharedEventSample", true}
        : candidates.front();
}

Color_t TuneColor(const std::string& tune)
{
    return HadronizationPlotStyle::TuneColor(tune);
}

int TuneMarker(const std::string& tune)
{
    return HadronizationPlotStyle::TuneMarker(tune);
}

int TuneLineStyle(const std::string& tune)
{
    return HadronizationPlotStyle::TuneLineStyle(tune);
}

void StyleHistogram(TH1D* hist,
                    const std::string& tune,
                    const SpectrumDef& spectrum,
                    bool normalizeShape)
{
    if (!hist) return;
    hist->SetStats(0);
    hist->SetTitle("");
    hist->SetLineColor(TuneColor(tune));
    hist->SetMarkerColor(TuneColor(tune));
    hist->SetMarkerStyle(TuneMarker(tune));
    hist->SetLineStyle(TuneLineStyle(tune));
    hist->SetLineWidth(2);
    hist->SetMarkerSize(0.9);
    hist->GetXaxis()->SetTitle(spectrum.xTitle.c_str());
    hist->GetYaxis()->SetTitle(normalizeShape
                               ? spectrum.yTitleShape.c_str()
                               : spectrum.yTitleCounts.c_str());
    hist->GetXaxis()->SetTitleOffset(1.08);
    hist->GetYaxis()->SetTitleOffset(1.52);
    hist->GetXaxis()->SetTitleSize(0.045);
    hist->GetYaxis()->SetTitleSize(0.045);
    hist->GetXaxis()->SetLabelSize(0.040);
    hist->GetYaxis()->SetLabelSize(0.040);
    if (IsSingleParticlePhiSpectrum(spectrum) || IsDeltaPhiSpectrum(spectrum)) {
        TAxis* axis = hist->GetXaxis();
        const double pi = Pi();
        axis->SetNdivisions(4, false);
        if (AxisRangeIs(axis, -pi, pi)) {
            axis->ChangeLabel(1, -1, -1, -1, -1, -1, "-#pi");
            axis->ChangeLabel(2, -1, -1, -1, -1, -1, "-#pi/2");
            axis->ChangeLabel(3, -1, -1, -1, -1, -1, "0");
            axis->ChangeLabel(4, -1, -1, -1, -1, -1, "#pi/2");
            axis->ChangeLabel(5, -1, -1, -1, -1, -1, "#pi");
        } else if (AxisRangeIs(axis, -0.5 * pi, 1.5 * pi)) {
            axis->ChangeLabel(1, -1, -1, -1, -1, -1, "-#pi/2");
            axis->ChangeLabel(2, -1, -1, -1, -1, -1, "0");
            axis->ChangeLabel(3, -1, -1, -1, -1, -1, "#pi/2");
            axis->ChangeLabel(4, -1, -1, -1, -1, -1, "#pi");
            axis->ChangeLabel(5, -1, -1, -1, -1, -1, "3#pi/2");
        }
    }
}

double PositiveMinimum(const std::vector<LoadedHistogram>& loaded)
{
    double minimum = 1.0e30;
    for (const auto& item : loaded) {
        TH1D* hist = item.hist;
        if (!hist) continue;
        for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
            const double content = hist->GetBinContent(bin);
            if (content > 0.0 && content < minimum) minimum = content;
        }
    }
    return minimum < 1.0e30 ? minimum : 1.0e-8;
}

double MaximumWithErrors(const std::vector<LoadedHistogram>& loaded)
{
    double maximum = 0.0;
    for (const auto& item : loaded) {
        TH1D* hist = item.hist;
        if (!hist) continue;
        for (int bin = 1; bin <= hist->GetNbinsX(); ++bin) {
            maximum = std::max(maximum, hist->GetBinContent(bin) + hist->GetBinError(bin));
        }
    }
    return maximum > 0.0 ? maximum : 1.0;
}

void DrawMissingMessage(const std::string& label)
{
    TLatex latex;
    latex.SetNDC();
    latex.SetTextAlign(22);
    latex.SetTextSize(0.04);
    latex.DrawLatex(0.50, 0.54, "No input histograms found");
    latex.SetTextSize(0.03);
    latex.DrawLatex(0.50, 0.47, label.c_str());
}

void DrawTuneOverlay(const PlotConfig& config,
                     const SampleRequest& request,
                     const SpectrumDef& spectrum,
                     const std::string& outputStem,
                     bool normalizeShape,
                     bool useSubsampleErrors,
                     bool strictInputs,
                     PhiAxisPolicy phiAxisPolicy)
{
    std::vector<LoadedHistogram> loaded;
    for (const auto& tune : config.tunes) {
        try {
            TH1D* hist = LoadSpectrum(config, tune, request, spectrum, normalizeShape,
                                      useSubsampleErrors, strictInputs, phiAxisPolicy);
            if (!hist) continue;
            StyleHistogram(hist, tune, spectrum, normalizeShape);
            loaded.push_back({hist, tune});
        } catch (const std::exception& error) {
            if (strictInputs) {
                for (auto& item : loaded) delete item.hist;
                throw;
            }
            std::cerr << "WARNING: " << error.what() << std::endl;
        }
    }

    const int width = 860;
    const int height = 680;
    TCanvas* canvas = new TCanvas(("c_" + outputStem).c_str(),
                                  (spectrum.title + " " + request.displayLabel).c_str(),
                                  width, height);
    canvas->SetTicks(1, 1);
    canvas->SetLeftMargin(0.16);
    canvas->SetRightMargin(0.045);
    canvas->SetBottomMargin(0.14);
    canvas->SetTopMargin(0.13);
    if (spectrum.logY) canvas->SetLogy();

    if (loaded.empty()) {
        DrawMissingMessage(request.displayLabel);
    } else {
        const double maxY = MaximumWithErrors(loaded);
        const double minY = spectrum.logY ? std::max(PositiveMinimum(loaded) * 0.35, 1.0e-12) : 0.0;
        const double upper = spectrum.logY ? maxY * 8.0 : maxY * 1.28;

        TLegend* legend = new TLegend(0.62, 0.705, 0.91, 0.855);
        legend->SetBorderSize(0);
        legend->SetFillStyle(0);
        legend->SetTextSize(0.035);

        bool first = true;
        for (auto& item : loaded) {
            TH1D* hist = item.hist;
            hist->SetMinimum(minY);
            hist->SetMaximum(std::max(upper, minY * 10.0));
            hist->Draw(first ? "E1 HIST" : "E1 HIST SAME");
            legend->AddEntry(hist, item.tune.c_str(), "lp");
            first = false;
        }
        legend->Draw();

        TLatex title;
        title.SetNDC();
        title.SetTextAlign(13);
        title.SetTextSize(0.034);
        title.DrawLatex(0.16, 0.965, request.displayLabel.c_str());
    }

    const std::string outputCategoryDir = JoinPath({config.outputDir, OutputSubdirectory(spectrum)});
    if (gSystem->mkdir(outputCategoryDir.c_str(), true) != 0 &&
        gSystem->AccessPathName(outputCategoryDir.c_str())) {
        throw std::runtime_error("Could not create output directory: " + outputCategoryDir);
    }

    const std::string outBase = JoinPath({outputCategoryDir, outputStem});
    canvas->SaveAs((outBase + ".png").c_str());
    canvas->SaveAs((outBase + ".pdf").c_str());
    canvas->SaveAs((outBase + ".C").c_str());

    delete canvas;
    for (auto& item : loaded) delete item.hist;
}

std::string TriggerLabelForFlavor(Flavor flavor)
{
    return TriggerParticleLatex(flavor) + " trigger";
}

std::vector<SampleRequest> BuildTriggerRequests(const PlotConfig& config)
{
    std::vector<SampleRequest> requests;
    if (!config.beautyPairs.empty()) {
        requests.push_back({Flavor::Beauty, FileRole::OS, config.beautyPairs.front().osFileName,
                            FlavorName(Flavor::Beauty) + ": " +
                                TriggerLabelForFlavor(Flavor::Beauty),
                            false});
    }
    if (!config.charmPairs.empty()) {
        requests.push_back({Flavor::Charm, FileRole::OS, config.charmPairs.front().osFileName,
                            FlavorName(Flavor::Charm) + ": " +
                                TriggerLabelForFlavor(Flavor::Charm),
                            false});
    }
    return requests;
}

std::vector<SampleRequest> BuildAssociateRequests(const PlotConfig& config)
{
    std::vector<SampleRequest> requests;
    const auto appendRequests = [&requests](const std::vector<PairConfig>& pairs) {
        std::set<std::string> seen;
        for (const auto& pair : pairs) {
            const std::string flavor = FlavorName(pair.flavor);
            const std::string osKey = flavor + "|" + pair.osFileName;
            if (!pair.osFileName.empty() && !seen.count(osKey)) {
                seen.insert(osKey);
                requests.push_back({pair.flavor, FileRole::OS, pair.osFileName,
                                    flavor + " associate OS: " +
                                        AssociateParticleLatex(pair.osFileName),
                                    false});
            }

            const std::string ssKey = flavor + "|" + pair.ssFileName;
            if (!pair.ssFileName.empty() && !seen.count(ssKey)) {
                seen.insert(ssKey);
                requests.push_back({pair.flavor, FileRole::SS, pair.ssFileName,
                                    flavor + " associate SS: " +
                                        AssociateParticleLatex(pair.ssFileName),
                                    false});
            }
        }
    };

    appendRequests(config.beautyPairs);
    appendRequests(config.charmPairs);
    return requests;
}

std::vector<SampleRequest> BuildCorrelationRequests(const PlotConfig& config)
{
    std::vector<SampleRequest> requests;
    const auto appendRequests = [&requests](const std::vector<PairConfig>& pairs) {
        std::set<std::string> seen;
        for (const auto& pair : pairs) {
            const std::string flavor = FlavorName(pair.flavor);
            const std::string osKey = flavor + "|" + pair.osFileName;
            if (!pair.osFileName.empty() && !seen.count(osKey)) {
                seen.insert(osKey);
                requests.push_back({pair.flavor, FileRole::OS, pair.osFileName,
                                    flavor + " correlation OS: " +
                                        PairParticleLatex(pair.flavor, pair.osFileName),
                                    false});
            }

            const std::string ssKey = flavor + "|" + pair.ssFileName;
            if (!pair.ssFileName.empty() && !seen.count(ssKey)) {
                seen.insert(ssKey);
                requests.push_back({pair.flavor, FileRole::SS, pair.ssFileName,
                                    flavor + " correlation SS: " +
                                        PairParticleLatex(pair.flavor, pair.ssFileName),
                                    false});
            }
        }
    };

    appendRequests(config.beautyPairs);
    appendRequests(config.charmPairs);
    return requests;
}

void SetPlotStyle()
{
    gStyle->SetOptStat(0);
    gStyle->SetTitleFont(42, "XYZ");
    gStyle->SetLabelFont(42, "XYZ");
    gStyle->SetTitleSize(0.045, "XYZ");
    gStyle->SetLabelSize(0.040, "XYZ");
    gStyle->SetLegendBorderSize(0);
    gStyle->SetErrorX(0.0);
}

} // namespace KinematicSpectraPlot

void Plot_KinematicSpectra_THnSparse(
    const char* configuration =
        "PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json",
    const char* outputDir = "PlottingScripts/Plots/KinematicSpectra",
    bool normalizeShape = true,
    bool useSubsampleErrors = true,
    bool strictInputs = false,
    bool includeCorrelationSpectra = true,
    const char* phiAxisPolicy = "strict")
{
    using namespace KinematicSpectraPlot;

    SetPlotStyle();
    const PlotConfig config = ReadConfig(configuration, outputDir);
    const PhiAxisPolicy parsedPhiAxisPolicy = ParsePhiAxisPolicy(phiAxisPolicy);

    std::cout << "Using Hadronization base: " << config.hadronizationBase << std::endl;
    std::cout << "Using analyzed data dir: " << config.baseDir << std::endl;
    std::cout << "Writing kinematic spectra under: " << config.outputDir << std::endl;
    std::cout << "Single-particle phi axis policy: "
              << PhiAxisPolicyName(parsedPhiAxisPolicy) << std::endl;
    std::cout << "Subsample errors: "
              << ((useSubsampleErrors && config.calculateErrors) ? "enabled" : "disabled")
              << std::endl;

    const SpectrumDef multiplicity = MultiplicitySpectrum();
    const std::string suffix = normalizeShape ? "shape" : "density";

    SampleRequest sharedRequest =
        config.tunes.empty()
            ? SampleRequest{Flavor::Beauty, FileRole::OS, "", "Shared event multiplicity", true}
            : FirstAvailableSharedSample(config, config.tunes.front(), strictInputs);
    sharedRequest.displayLabel = "Shared event multiplicity";

    DrawTuneOverlay(config,
                    sharedRequest,
                    multiplicity,
                    "MultiplicitySpectrum_Shared_" + suffix,
                    normalizeShape,
                    useSubsampleErrors,
                    strictInputs,
                    parsedPhiAxisPolicy);

    std::vector<SpectrumDef> triggerSpectra = KinematicSpectra();
    std::vector<SampleRequest> triggerRequests = BuildTriggerRequests(config);
    for (const auto& request : triggerRequests) {
        for (auto spectrum : triggerSpectra) {
            spectrum.sourceKind = SourceKind::TriggerKinematics;
            DrawTuneOverlay(config,
                            request,
                            spectrum,
                            "Trigger_" + SanitizeToken(spectrum.key) + "_" +
                                FlavorNameUpper(request.flavor) + "_" + suffix,
                            normalizeShape,
                            useSubsampleErrors,
                            strictInputs,
                            parsedPhiAxisPolicy);
        }
    }

    std::vector<SpectrumDef> associateSpectra = KinematicSpectra();
    std::vector<SampleRequest> associateRequests = BuildAssociateRequests(config);
    for (const auto& request : associateRequests) {
        for (auto spectrum : associateSpectra) {
            spectrum.sourceKind = SourceKind::AssociateKinematics;
            DrawTuneOverlay(config,
                            request,
                            spectrum,
                            "Associate_" + SanitizeToken(spectrum.key) + "_" +
                                FlavorNameUpper(request.flavor) + "_" +
                                SanitizeToken(StripRootExtension(request.fileName)) + "_" + suffix,
                            normalizeShape,
                            useSubsampleErrors,
                            strictInputs,
                            parsedPhiAxisPolicy);
        }
    }

    if (includeCorrelationSpectra) {
        std::vector<SampleRequest> correlationRequests = BuildCorrelationRequests(config);
        for (const auto& request : correlationRequests) {
            for (const auto& spectrum : CorrelationSpectra()) {
                DrawTuneOverlay(config,
                                request,
                                spectrum,
                                "Correlation_" + SanitizeToken(spectrum.key) + "_" +
                                    FlavorNameUpper(request.flavor) + "_" +
                                    SanitizeToken(StripRootExtension(request.fileName)) + "_" + suffix,
                                normalizeShape,
                                useSubsampleErrors,
                                strictInputs,
                                parsedPhiAxisPolicy);
            }
        }
    }
}
