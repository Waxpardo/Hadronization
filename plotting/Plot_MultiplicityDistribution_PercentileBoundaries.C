// ---------------------------------------------------------------------------
// Plot_MultiplicityDistribution_PercentileBoundaries.C
//
// Draw charged-particle multiplicity distributions with event-activity
// percentile boundaries for all configured PYTHIA tunes.
//
// Default usage from the Hadronization repository root:
//
//   root -l -b -q 'plotting/Plot_MultiplicityDistribution_PercentileBoundaries.C'
//
// The macro reads the same THnSparse JSON configuration used by Paul's plotting
// macro, so the percentile classes stay synchronized with the analysis plots.
// ---------------------------------------------------------------------------

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "TCanvas.h"
#include "TFile.h"
#include "TGraph.h"
#include "TGraphErrors.h"
#include "TH1D.h"
#include "TH1F.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TLine.h"
#include "TObject.h"
#include "TPad.h"
#include "TString.h"
#include "TStyle.h"
#include "TSystem.h"

#include "HistogramErrorUtils.h"
#include "MultiplicityBoundaryUtils.h"
#include "PairInputSelectionUtils.h"
#include "TunePlotStyle.h"

#if __has_include(<nlohmann/json.hpp>)
#include <nlohmann/json.hpp>
#elif __has_include("nlohmann/json.hpp")
#include "nlohmann/json.hpp"
#else
#error "Could not find nlohmann/json.hpp. Source the project/ROOT environment before compiling this macro."
#endif

using json = nlohmann::json;

namespace MultiplicityPercentilePlot {

constexpr double kMultiplicityXMax = 170.0;

struct PercentileClass {
    double minPercentile;
    double maxPercentile;
    std::string label;
};

struct PlotConfig {
    std::string hadronizationBase;
    std::string baseDir;
    std::string beautyCompleteRootDir;
    std::string charmCompleteRootDir;
    std::string beautyFileName;
    std::string charmFileName;
    std::string outputDir;
    std::string configurationPath;
    std::string configurationSha256;
    std::string boundaryReceiptPath;
    json boundaryReceipt;
    std::vector<std::string> tunes;
    std::vector<PercentileClass> percentileClasses;
    HadronizationPairInput::SelectionContract pairInputSelectionContract;
    std::string pairCombinatoricsMode;
    double sameSignPairFactor = 0.0;
};

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
    if (envBase && PathExists(JoinPath({envBase, "plotting"}))) {
        return ExpandPath(envBase);
    }

    std::string current = ExpandPath(gSystem->WorkingDirectory());
    while (!current.empty()) {
        if (PathExists(JoinPath({current, "plotting"})) ||
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
        JoinPath({hadronizationBase, "plotting", path})
    };

    for (const auto& candidate : candidates) {
        if (PathExists(candidate)) return candidate;
    }

    std::ostringstream message;
    message << "Could not find configuration file '" << path << "'. Tried:";
    for (const auto& candidate : candidates) message << "\n  - " << candidate;
    throw std::runtime_error(message.str());
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
    message << "Could not find multiplicity input ROOT file '" << fileName
            << "' for tune " << tune << ". Tried:";
    for (const auto& candidate : candidates) message << "\n  - " << candidate;
    throw std::runtime_error(message.str());
}

std::string FormatPercentile(double value)
{
    const int rounded = static_cast<int>(std::round(value));
    if (std::fabs(value - rounded) < 1.0e-9) return std::to_string(rounded);

    std::ostringstream stream;
    stream << value;
    return stream.str();
}

std::string PercentileLabel(double minPercentile, double maxPercentile)
{
    return FormatPercentile(minPercentile) + "-" + FormatPercentile(maxPercentile) + "%";
}

std::vector<PercentileClass> ReadPercentileClasses(const json& config)
{
    std::vector<PercentileClass> classes;
    for (const auto& entry : config["histograms_to_analyse"]) {
        const double minPercentile = entry["multiplicityMin"].get<double>();
        const double maxPercentile = entry["multiplicityMax"].get<double>();
        classes.push_back({
            minPercentile,
            maxPercentile,
            PercentileLabel(minPercentile, maxPercentile)
        });
    }
    return classes;
}

std::string FirstOSFileName(const json& config, const char* key, const char* fallback)
{
    if (config.contains(key) && config[key].is_array() && !config[key].empty()) {
        for (const auto& entry : config[key]) {
            if (entry.contains("OS") && entry["OS"].is_string()) {
                return entry["OS"].get<std::string>();
            }

            if (!entry.contains("configs") || !entry["configs"].is_array()) continue;
            for (const auto& correlationConfig : entry["configs"]) {
                if (correlationConfig.contains("OS") && correlationConfig["OS"].is_string()) {
                    return correlationConfig["OS"].get<std::string>();
                }
            }
        }
    }
    return fallback;
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
    configOut.configurationPath = configPath;
    configOut.configurationSha256 =
        Hadronization::Sha256FileHex(configPath);
    configOut.baseDir =
        ResolvePathFromBase(config["base_dir"].get<std::string>(), configOut.hadronizationBase);
    if (const char* selectedBase =
            std::getenv("HADRONIZATION_ANALYZED_DATA_BASE")) {
        if (*selectedBase) {
            configOut.baseDir =
                ResolvePathFromBase(selectedBase, configOut.hadronizationBase);
        }
    }
    configOut.beautyCompleteRootDir = config["bb_bar_complete_root_dir"].get<std::string>();
    configOut.charmCompleteRootDir = config["cc_bar_complete_root_dir"].get<std::string>();
    if (const char* selectedTag =
            std::getenv("HADRONIZATION_COMPLETE_ROOT_TAG")) {
        if (*selectedTag) {
            configOut.beautyCompleteRootDir = selectedTag;
            configOut.charmCompleteRootDir = selectedTag;
        }
    }
    configOut.beautyFileName =
        FirstOSFileName(config, "beauty_correlations_to_analyse", "BplusBminus.root");
    configOut.charmFileName =
        FirstOSFileName(config, "charm_correlations_to_analyse", "DplusDminus.root");
    configOut.outputDir = ResolvePathFromBase(outputDir, configOut.hadronizationBase);

    for (const auto& tune : config["PYTHIA_TUNES"]) {
        configOut.tunes.push_back(tune.get<std::string>());
    }
    configOut.percentileClasses = ReadPercentileClasses(config);
    configOut.pairInputSelectionContract =
        HadronizationPairInput::ParseSelectionContract(
            config.at("pair_input_selection_contract"));
    configOut.pairCombinatoricsMode =
        config.at("pair_combinatorics_mode").get<std::string>();
    configOut.sameSignPairFactor =
        config.at("same_sign_pair_factor").get<double>();

    std::set<std::string> receiptDirectories;
    for (const auto& canvas :
         config.at("global_canvases_to_be_drawn")) {
        if (canvas.at("write").get<bool>()) {
            const std::string writePath =
                ResolvePathFromBase(
                    canvas.at("write_path").get<std::string>(),
                    configOut.hadronizationBase);
            if (!writePath.empty() && writePath != "NONE") {
                receiptDirectories.insert(writePath);
            }
        }
    }
    if (receiptDirectories.size() != 1U) {
        throw std::runtime_error(
            "Exactly one global-canvas output directory is required to "
            "resolve the frozen multiplicity-boundary receipt");
    }
    configOut.boundaryReceiptPath =
        JoinPath({*receiptDirectories.begin(),
                  "multiplicity_boundary_receipt_v2.json"});
    if (PathExists(configOut.boundaryReceiptPath)) {
        std::ifstream receiptInput(configOut.boundaryReceiptPath);
        if (!receiptInput.is_open()) {
            throw std::runtime_error(
                "Could not open multiplicity-boundary receipt: " +
                configOut.boundaryReceiptPath);
        }
        configOut.boundaryReceipt = json::parse(receiptInput);
    }

    return configOut;
}

// The decorations and the receipt are both derived from the labelled tune's
// own merged event-activity distribution.  This is the PR-13 scientific
// definition; the shared utility supplies the later fail-closed and disjoint
// integer-bin behaviour.
std::map<double, int> CalculateThresholds(
    const TH1D* hMult,
    const std::vector<PercentileClass>& classes)
{
    std::set<double> percentiles;
    std::vector<std::pair<double, double>> configuredClasses;
    for (const auto& entry : classes) {
        percentiles.insert(entry.minPercentile);
        percentiles.insert(entry.maxPercentile);
        configuredClasses.push_back(
            {entry.minPercentile, entry.maxPercentile});
    }
    const std::string context = "standalone multiplicity-boundary plot";
    HadronizationMultiplicity::ValidateAndOrderPartition(configuredClasses);
    const auto identity =
        HadronizationMultiplicity::CaptureHistogramIdentity(hMult, context);
    std::map<double, int> thresholds;
    for (const double percentile : percentiles) {
        thresholds[percentile] =
            HadronizationMultiplicity::ThresholdForPercentile(
                identity, percentile, context);
    }
    return thresholds;
}

void VerifyBoundaryReceiptForHistogram(
    const PlotConfig& config,
    const std::string& tune,
    const TH1D* histogram,
    bool strictInputs)
{
    if (config.boundaryReceipt.empty()) {
        if (strictInputs) {
            throw std::runtime_error(
                "Missing frozen multiplicity-boundary receipt: " +
                config.boundaryReceiptPath +
                ". Run the matching thnsparse target successfully first.");
        }
        std::cerr
            << "WARNING: diagnostic-only boundary drawing without frozen "
            << "receipt " << config.boundaryReceiptPath << std::endl;
        return;
    }
    const json& receipt = config.boundaryReceipt;
    if (receipt.value("schema", std::string()) !=
            HadronizationMultiplicity::kBoundaryReceiptSchema ||
        receipt.value("schema_version", 0) != 2 ||
        receipt.value("algorithm", std::string()) !=
            HadronizationMultiplicity::kBoundaryAlgorithm ||
        receipt.value("completion_status", std::string()) != "PASS" ||
        receipt.value("configuration_sha256", std::string()) !=
            config.configurationSha256) {
        throw std::runtime_error(
            "Multiplicity-boundary receipt schema/configuration mismatch: " +
            config.boundaryReceiptPath);
    }
    json payload = receipt;
    const std::string claimedPayloadSha =
        payload.value("payload_sha256", std::string());
    payload.erase("payload_sha256");
    if (claimedPayloadSha.size() != 64U ||
        Hadronization::Sha256Hex(payload.dump()) !=
            claimedPayloadSha) {
        throw std::runtime_error(
            "Multiplicity-boundary receipt payload SHA-256 mismatch: " +
            config.boundaryReceiptPath);
    }
    if (!receipt.contains("tunes") ||
        !receipt.at("tunes").contains(tune)) {
        throw std::runtime_error(
            "Multiplicity-boundary receipt has no tune " + tune);
    }
    const json& tuneReceipt = receipt.at("tunes").at(tune);
    const auto identity =
        HadronizationMultiplicity::CaptureHistogramIdentity(
            histogram, "standalone boundary receipt check for " + tune);
    if (tuneReceipt.value(
            "histogram_identity_sha256", std::string()) !=
        HadronizationMultiplicity::HistogramIdentitySha256(identity)) {
        throw std::runtime_error(
            "Multiplicity histogram identity differs from frozen receipt "
            "for tune " + tune);
    }

    const std::string centralReferencePath =
        tuneReceipt.value("central_reference_path", std::string());
    const std::string centralReferenceSha =
        tuneReceipt.value(
            "central_source_file_sha256", std::string());
    if (centralReferencePath.empty() ||
        centralReferenceSha.size() != 64U ||
        Hadronization::Sha256FileHex(centralReferencePath) !=
            centralReferenceSha) {
        throw std::runtime_error(
            "Frozen central multiplicity source file/hash is unavailable "
            "or changed for tune " + tune);
    }

    std::map<double, int> storedThresholds;
    for (const auto& threshold : tuneReceipt.at("thresholds")) {
        storedThresholds.emplace(
            threshold.at("percentile").get<double>(),
            threshold.at("nch_threshold").get<int>());
    }
    const auto recomputed =
        CalculateThresholds(
            histogram,
            config.percentileClasses);
    if (recomputed != storedThresholds) {
        throw std::runtime_error(
            "Recomputed multiplicity thresholds differ from frozen receipt "
            "for tune " + tune);
    }
    std::vector<std::pair<double, double>> configuredClasses;
    for (const auto& activityClass : config.percentileClasses) {
        configuredClasses.push_back({
            activityClass.minPercentile,
            activityClass.maxPercentile});
    }
    HadronizationMultiplicity::RequireDiscretePartitionCoverage(
        configuredClasses, storedThresholds);
    const json& partition = tuneReceipt.at("partition");
    if (partition.value("coverage", std::string()) != "PASS" ||
        partition.value("disjointness", std::string()) != "PASS") {
        throw std::runtime_error(
            "Multiplicity-boundary receipt does not certify a complete, "
            "disjoint partition for tune " + tune);
    }
    std::cout
        << "MULTIPLICITY_BOUNDARY_RECEIPT_CONSUMED"
        << " tune=" << tune
        << " path=" << config.boundaryReceiptPath
        << " payload_sha256=" << claimedPayloadSha
        << " status=PASS" << std::endl;
}

TH1D* LoadMultiplicityHistogram(const PlotConfig& config,
                                const std::string& tune,
                                const char* flavor,
                                bool normalize,
                                bool strictInputs)
{
    const bool isBeauty = (std::string(flavor) == "BEAUTY");
    const std::string completeRootDir =
        isBeauty ? config.beautyCompleteRootDir : config.charmCompleteRootDir;
    const std::string fileName = isBeauty ? config.beautyFileName : config.charmFileName;

    std::string filePath;
    try {
        filePath = ResolveCompleteRootFile(config.baseDir, tune, completeRootDir, fileName);
    } catch (const std::exception& error) {
        if (strictInputs) throw;
        std::cerr << "WARNING: " << error.what() << std::endl;
        return nullptr;
    }

    TFile* file = TFile::Open(filePath.c_str(), "READ");
    if (!file || file->IsZombie()) {
        if (file) file->Close();
        if (strictInputs) {
            throw std::runtime_error("Could not open input ROOT file: " + filePath);
        }
        std::cerr << "WARNING: could not open input ROOT file: " << filePath << std::endl;
        return nullptr;
    }

    const auto projectionMode =
        HadronizationPairInput::ValidateSelectionMetadata(
        *file, config.pairInputSelectionContract, completeRootDir, filePath);
    HadronizationPairInput::ValidateConfiguredCombinatorics(
        projectionMode, config.pairCombinatoricsMode,
        config.sameSignPairFactor, config.pairInputSelectionContract,
        filePath);

    TH1D* source = dynamic_cast<TH1D*>(file->Get("summed MULTIPLICITY"));
    if (!source) {
        file->Close();
        delete file;
        if (strictInputs) {
            throw std::runtime_error("Missing 'summed MULTIPLICITY' in " + filePath);
        }
        std::cerr << "WARNING: missing 'summed MULTIPLICITY' in " << filePath << std::endl;
        return nullptr;
    }
    VerifyBoundaryReceiptForHistogram(
        config, tune, source, strictInputs);

    TH1D* hist = dynamic_cast<TH1D*>(source->Clone(Form("hMultiplicity_%s_%s",
                                                       flavor, tune.c_str())));
    hist->SetDirectory(nullptr);
    file->Close();
    delete file;

    PlotErrorUtils::EnsureSumw2(hist);
    if (normalize) {
        PlotErrorUtils::NormalizeToUnitShape(hist);
    }

    return hist;
}

TH1D* LoadSharedMultiplicityHistogram(const PlotConfig& config,
                                      const std::string& tune,
                                      bool normalize,
                                      bool strictInputs)
{
    std::vector<std::string> attemptedFlavors;
    for (const char* flavor : {"BEAUTY", "CHARM"}) {
        attemptedFlavors.push_back(flavor);
        TH1D* hist = LoadMultiplicityHistogram(config, tune, flavor, normalize, false);
        if (!hist) continue;

        hist->SetName(Form("hMultiplicity_SHARED_%s", tune.c_str()));
        return hist;
    }

    if (strictInputs) {
        std::ostringstream message;
        message << "Could not find a shared multiplicity input for tune " << tune
                << ". Tried flavors:";
        for (const auto& flavor : attemptedFlavors) message << " " << flavor;
        throw std::runtime_error(message.str());
    }

    return nullptr;
}

Color_t TuneColor(const std::string& tune)
{
    return HadronizationPlotStyle::TuneColor(tune);
}

const char* MultiplicityYAxisTitle(bool normalize)
{
    return normalize ? "Probability P(N_{ch})" : "Counts";
}

const char* MultiplicityXAxisTitle()
{
    return "Multiplicity N_{ch}";
}

double PositiveMinimum(TH1D* hist)
{
    double minimum = 1.0e30;
    for (int iBin = 1; iBin <= hist->GetNbinsX(); ++iBin) {
        const double value = hist->GetBinContent(iBin);
        if (value > 0.0 && value < minimum) minimum = value;
    }
    return minimum < 1.0e30 ? minimum : 1.0e-8;
}

double UpperX(TH1D* hist)
{
    for (int iBin = hist->GetNbinsX(); iBin >= 1; --iBin) {
        if (hist->GetBinContent(iBin) > 0.0) {
            return 1.25 * hist->GetBinLowEdge(iBin + 1);
        }
    }
    return hist->GetXaxis()->GetXmax();
}

void StyleHistogram(TH1D* hist, const std::string& tune, bool normalize)
{
    hist->SetStats(0);
    hist->SetTitle("");
    hist->SetLineColor(TuneColor(tune));
    hist->SetMarkerColor(TuneColor(tune));
    hist->SetMarkerStyle(HadronizationPlotStyle::TuneMarker(tune));
    hist->SetLineStyle(HadronizationPlotStyle::TuneLineStyle(tune));
    hist->SetLineWidth(2);
    hist->GetXaxis()->SetTitle(MultiplicityXAxisTitle());
    hist->GetYaxis()->SetTitle(MultiplicityYAxisTitle(normalize));
    hist->GetXaxis()->SetTitleOffset(1.1);
    hist->GetYaxis()->SetTitleOffset(1.25);
}

TGraphErrors* BuildMultiplicityGraph(TH1D* hist,
                                     const std::string& tune,
                                     double xMin,
                                     double xMax)
{
    std::vector<double> xValues;
    std::vector<double> yValues;
    std::vector<double> xErrors;
    std::vector<double> yErrors;
    for (int iBin = 1; iBin <= hist->GetNbinsX(); ++iBin) {
        const double x = hist->GetBinCenter(iBin);
        const double y = hist->GetBinContent(iBin);
        if (x < xMin || x > xMax || y <= 0.0) continue;
        xValues.push_back(x);
        yValues.push_back(y);
        xErrors.push_back(0.0);
        yErrors.push_back(hist->GetBinError(iBin));
    }

    TGraphErrors* graph = new TGraphErrors(static_cast<int>(xValues.size()),
                                           xValues.data(),
                                           yValues.data(),
                                           xErrors.data(),
                                           yErrors.data());
    graph->SetName(Form("gMultiplicity_%s", tune.c_str()));
    graph->SetLineColor(TuneColor(tune));
    graph->SetMarkerColor(TuneColor(tune));
    graph->SetMarkerStyle(HadronizationPlotStyle::TuneMarker(tune));
    graph->SetLineStyle(HadronizationPlotStyle::TuneLineStyle(tune));
    graph->SetLineWidth(2);
    return graph;
}

void DrawClassDecorations(const std::vector<PercentileClass>& classes,
                          const std::map<double, int>& thresholds,
                          double xMin,
                          double xMax,
                          double yMin,
                          double yMax)
{
    const double labelY =
        std::pow(10.0, std::log10(yMin) + 0.53 * (std::log10(yMax) - std::log10(yMin)));

    for (const auto& item : thresholds) {
        const double percentile = item.first;
        if (percentile <= 0.0 || percentile >= 100.0) continue;

        // Adjacent inclusive integer classes meet between Nch bins. Drawing
        // at threshold+0.5 displays the same tie rule used by the analysis:
        // the threshold integer stays in the lower-activity class.
        const double x = static_cast<double>(item.second) + 0.5;
        if (x <= xMin || x >= xMax) continue;
        TLine* line = new TLine(x, yMin, x, yMax);
        line->SetLineColor(kGray + 2);
        line->SetLineStyle(2);
        line->SetLineWidth(1);
        line->Draw("same");
    }

    TLatex latex;
    latex.SetTextAlign(22);
    latex.SetTextAngle(90);
    latex.SetTextSize(0.040);
    latex.SetTextFont(42);

    for (const auto& entry : classes) {
        if (entry.minPercentile == 0.0 &&
            entry.maxPercentile == 100.0 &&
            classes.size() > 1U) {
            continue;
        }
        const auto range =
            HadronizationMultiplicity::DiscreteClassRange(
                thresholds, entry.minPercentile,
                entry.maxPercentile);
        const double left =
            std::max(xMin, static_cast<double>(range.first) - 0.5);
        const double right =
            std::min(xMax, static_cast<double>(range.second) + 0.5);
        if (right <= xMin || left >= xMax || right <= left) continue;

        const double x = std::sqrt(left * right);
        latex.DrawLatex(x, labelY, entry.label.c_str());
    }
}

void DrawMissingInputMessage(const char* flavor, const std::string& tune)
{
    TLatex latex;
    latex.SetNDC();
    latex.SetTextAlign(22);
    latex.SetTextSize(0.045);
    latex.DrawLatex(0.50, 0.56, tune.c_str());
    latex.SetTextSize(0.035);
    latex.DrawLatex(0.50, 0.48, Form("%s input not found", flavor));
}

void DrawFlavorCanvas(const PlotConfig& config,
                      const char* flavor,
                      bool normalize,
                      bool strictInputs)
{
    const int nTunes = static_cast<int>(config.tunes.size());
    if (nTunes == 0) throw std::runtime_error("No PYTHIA_TUNES configured");

    TCanvas* canvas = new TCanvas(Form("cMultiplicityPercentiles_%s", flavor),
                                  Form("%s multiplicity percentile boundaries", flavor),
                                  520 * nTunes, 640);
    canvas->Divide(nTunes, 1, 0.001, 0.001);
    std::vector<TObject*> keepAlive;

    for (int iTune = 0; iTune < nTunes; ++iTune) {
        const std::string tune = config.tunes[iTune];
        canvas->cd(iTune + 1);
        gPad->SetLogx();
        gPad->SetLogy();
        gPad->SetTicks(1, 1);
        gPad->SetTopMargin(0.08);
        gPad->SetBottomMargin(0.14);
        gPad->SetLeftMargin(iTune == 0 ? 0.14 : 0.08);
        gPad->SetRightMargin(0.03);

        TH1D* hist = LoadMultiplicityHistogram(config, tune, flavor, normalize, strictInputs);
        if (!hist) {
            DrawMissingInputMessage(flavor, tune);
            continue;
        }

        const double xMin = 1.0;
        const double xMax = kMultiplicityXMax;
        const double yMin = std::max(PositiveMinimum(hist) * 0.45, normalize ? 1.0e-10 : 0.45);
        const double yMax = std::max(hist->GetMaximum() * 3.0, yMin * 10.0);

        TH1F* frame = gPad->DrawFrame(xMin, yMin, xMax, yMax);
        frame->SetTitle("");
        frame->GetXaxis()->SetTitle(MultiplicityXAxisTitle());
        frame->GetYaxis()->SetTitle(MultiplicityYAxisTitle(normalize));
        frame->GetXaxis()->SetTitleOffset(1.0);
        frame->GetYaxis()->SetTitleOffset(1.25);

        TGraphErrors* graph = BuildMultiplicityGraph(hist, tune, xMin, xMax);
        keepAlive.push_back(hist);
        keepAlive.push_back(graph);
        graph->Draw("LE1 same");

        const std::map<double, int> thresholds =
            CalculateThresholds(hist, config.percentileClasses);
        DrawClassDecorations(config.percentileClasses, thresholds, xMin, xMax, yMin, yMax);
        graph->Draw("LE1 same");
        gPad->RedrawAxis();

        TLatex title;
        title.SetNDC();
        title.SetTextAlign(22);
        title.SetTextSize(0.045);
        title.DrawLatex(0.50, 0.955, Form("%s %s", flavor, tune.c_str()));

    }

    if (gSystem->mkdir(config.outputDir.c_str(), true) != 0 &&
        gSystem->AccessPathName(config.outputDir.c_str())) {
        throw std::runtime_error("Could not create output directory: " + config.outputDir);
    }

    const std::string suffix = normalize ? "normalized" : "counts";
    const std::string outBase =
        JoinPath({config.outputDir,
                  std::string("MultiplicityDistributionPercentileBoundaries_") +
                      flavor + "_" + suffix});

    canvas->SaveAs((outBase + ".png").c_str());
    canvas->SaveAs((outBase + ".pdf").c_str());
    canvas->SaveAs((outBase + ".C").c_str());
    delete canvas;
    for (TObject* object : keepAlive) delete object;
}

void DrawSharedCanvas(const PlotConfig& config,
                      bool normalize,
                      bool strictInputs)
{
    const int nTunes = static_cast<int>(config.tunes.size());
    if (nTunes == 0) throw std::runtime_error("No PYTHIA_TUNES configured");

    TCanvas* canvas = new TCanvas("cMultiplicityPercentiles_SHARED",
                                  "Shared multiplicity percentile boundaries",
                                  520 * nTunes, 640);
    canvas->Divide(nTunes, 1, 0.001, 0.001);
    std::vector<TObject*> keepAlive;

    for (int iTune = 0; iTune < nTunes; ++iTune) {
        const std::string tune = config.tunes[iTune];
        canvas->cd(iTune + 1);
        gPad->SetLogx();
        gPad->SetLogy();
        gPad->SetTicks(1, 1);
        gPad->SetTopMargin(0.08);
        gPad->SetBottomMargin(0.14);
        gPad->SetLeftMargin(iTune == 0 ? 0.14 : 0.08);
        gPad->SetRightMargin(0.03);

        TH1D* hist = LoadSharedMultiplicityHistogram(config, tune, normalize, strictInputs);
        if (!hist) {
            DrawMissingInputMessage("SHARED", tune);
            continue;
        }

        const double xMin = 1.0;
        const double xMax = kMultiplicityXMax;
        const double yMin = std::max(PositiveMinimum(hist) * 0.45, normalize ? 1.0e-10 : 0.45);
        const double yMax = std::max(hist->GetMaximum() * 3.0, yMin * 10.0);

        TH1F* frame = gPad->DrawFrame(xMin, yMin, xMax, yMax);
        frame->SetTitle("");
        frame->GetXaxis()->SetTitle(MultiplicityXAxisTitle());
        frame->GetYaxis()->SetTitle(MultiplicityYAxisTitle(normalize));
        frame->GetXaxis()->SetTitleOffset(1.0);
        frame->GetYaxis()->SetTitleOffset(1.25);

        TGraphErrors* graph = BuildMultiplicityGraph(hist, tune, xMin, xMax);
        keepAlive.push_back(hist);
        keepAlive.push_back(graph);
        graph->Draw("LE1 same");

        const std::map<double, int> thresholds =
            CalculateThresholds(hist, config.percentileClasses);
        DrawClassDecorations(config.percentileClasses, thresholds, xMin, xMax, yMin, yMax);
        graph->Draw("LE1 same");
        gPad->RedrawAxis();

        TLatex title;
        title.SetNDC();
        title.SetTextAlign(22);
        title.SetTextSize(0.045);
        title.DrawLatex(0.50, 0.955, tune.c_str());

    }

    if (gSystem->mkdir(config.outputDir.c_str(), true) != 0 &&
        gSystem->AccessPathName(config.outputDir.c_str())) {
        throw std::runtime_error("Could not create output directory: " + config.outputDir);
    }

    const std::string suffix = normalize ? "normalized" : "counts";
    const std::string outBase =
        JoinPath({config.outputDir,
                  std::string("MultiplicityDistributionPercentileBoundaries_SHARED_") +
                      suffix});

    canvas->SaveAs((outBase + ".png").c_str());
    canvas->SaveAs((outBase + ".pdf").c_str());
    canvas->SaveAs((outBase + ".C").c_str());
    delete canvas;
    for (TObject* object : keepAlive) delete object;
}

void DrawCompactMonashCanvas(const PlotConfig& config,
                             bool normalize,
                             bool strictInputs)
{
    const std::string tune = "MONASH";
    TCanvas* canvas = new TCanvas("cMultiplicityPercentiles_MONASH_compact",
                                  "MONASH compact multiplicity percentile boundaries",
                                  820, 660);
    TH1D* hist = nullptr;
    TGraphErrors* graph = nullptr;

    canvas->SetLogx();
    canvas->SetLogy();
    canvas->SetTicks(1, 1);
    canvas->SetTopMargin(0.08);
    canvas->SetBottomMargin(0.16);
    canvas->SetLeftMargin(0.14);
    canvas->SetRightMargin(0.04);

    hist = LoadSharedMultiplicityHistogram(config, tune, normalize, strictInputs);
    if (!hist) {
        DrawMissingInputMessage("SHARED", tune);
    } else {
        const double xMin = 1.0;
        const double xMax = kMultiplicityXMax;
        const double yMin = std::max(PositiveMinimum(hist) * 0.45, normalize ? 1.0e-10 : 0.45);
        const double yMax = std::max(hist->GetMaximum() * 3.0, yMin * 10.0);

        TH1F* frame = gPad->DrawFrame(xMin, yMin, xMax, yMax);
        frame->SetTitle("");
        frame->GetXaxis()->SetTitle(MultiplicityXAxisTitle());
        frame->GetYaxis()->SetTitle(MultiplicityYAxisTitle(normalize));
        frame->GetXaxis()->SetTitleOffset(1.0);
        frame->GetYaxis()->SetTitleOffset(1.20);

        graph = BuildMultiplicityGraph(hist, tune, xMin, xMax);
        graph->Draw("LE1 same");

        const std::map<double, int> thresholds =
            CalculateThresholds(hist, config.percentileClasses);
        DrawClassDecorations(config.percentileClasses, thresholds, xMin, xMax, yMin, yMax);
        graph->Draw("LE1 same");

        TLegend* legend = new TLegend(0.64, 0.78, 0.91, 0.88);
        legend->SetBorderSize(0);
        legend->SetFillStyle(0);
        legend->SetTextSize(0.036);
        legend->AddEntry(graph, "MONASH example", "lp");
        legend->Draw();

        TLatex title;
        title.SetNDC();
        title.SetTextAlign(13);
        title.SetTextSize(0.040);
        title.DrawLatex(0.14, 0.955, "MONASH percentile boundaries");
        gPad->RedrawAxis();
    }

    if (gSystem->mkdir(config.outputDir.c_str(), true) != 0 &&
        gSystem->AccessPathName(config.outputDir.c_str())) {
        throw std::runtime_error("Could not create output directory: " + config.outputDir);
    }

    const std::string suffix = normalize ? "normalized" : "counts";
    const std::string outBase =
        JoinPath({config.outputDir,
                  std::string("MultiplicityDistributionPercentileBoundaries_MONASH_compact_") +
                      suffix});

    canvas->SaveAs((outBase + ".png").c_str());
    canvas->SaveAs((outBase + ".pdf").c_str());
    canvas->SaveAs((outBase + ".C").c_str());
    delete canvas;
    delete hist;
    delete graph;
}

void SetPlotStyle()
{
    gStyle->SetOptStat(0);
    gStyle->SetTitleFont(42, "XYZ");
    gStyle->SetLabelFont(42, "XYZ");
    gStyle->SetLegendBorderSize(0);
}

} // namespace MultiplicityPercentilePlot

void Plot_MultiplicityDistribution_PercentileBoundaries(
    const char* configuration =
        "plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json",
    const char* outputDir = "plotting/Plots/MultiplicityDistribution",
    bool normalize = false,
    bool strictInputs = true,
    bool compactMonashOnly = false)
{
    using namespace MultiplicityPercentilePlot;

    SetPlotStyle();
    const PlotConfig config = ReadConfig(configuration, outputDir);

    std::cout << "Using Hadronization base: " << config.hadronizationBase << std::endl;
    std::cout << "Using analyzed data dir: " << config.baseDir << std::endl;
    std::cout << "Using complete-root tag: "
              << config.beautyCompleteRootDir << std::endl;
    std::cout << "Writing multiplicity plots to: " << config.outputDir << std::endl;

    if (compactMonashOnly) {
        DrawCompactMonashCanvas(config, normalize, strictInputs);
    } else {
        DrawSharedCanvas(config, normalize, strictInputs);
    }
}

void Plot_MultiplicityDistribution_PercentileBoundaries_ByFlavor(
    const char* configuration =
        "plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json",
    const char* outputDir = "plotting/Plots/MultiplicityDistribution",
    bool normalize = false,
    bool strictInputs = true)
{
    using namespace MultiplicityPercentilePlot;

    SetPlotStyle();
    const PlotConfig config = ReadConfig(configuration, outputDir);

    std::cout << "Using Hadronization base: " << config.hadronizationBase << std::endl;
    std::cout << "Using analyzed data dir: " << config.baseDir << std::endl;
    std::cout << "Using beauty/charm complete-root tags: "
              << config.beautyCompleteRootDir << " / "
              << config.charmCompleteRootDir << std::endl;
    std::cout << "Writing by-flavor multiplicity debug plots to: " << config.outputDir << std::endl;

    DrawFlavorCanvas(config, "BEAUTY", normalize, strictInputs);
    DrawFlavorCanvas(config, "CHARM", normalize, strictInputs);
}

int TestMultiplicityDatasetSelectorOverrides(
    const char* configuration,
    const char* analyzedDataBase,
    const char* completeRootTag)
{
    using namespace MultiplicityPercentilePlot;

    const char* oldBasePointer =
        std::getenv("HADRONIZATION_ANALYZED_DATA_BASE");
    const char* oldTagPointer =
        std::getenv("HADRONIZATION_COMPLETE_ROOT_TAG");
    const bool hadBase = oldBasePointer != nullptr;
    const bool hadTag = oldTagPointer != nullptr;
    const std::string oldBase = oldBasePointer ? oldBasePointer : "";
    const std::string oldTag = oldTagPointer ? oldTagPointer : "";
    auto restore = [&]() {
        if (hadBase) {
            gSystem->Setenv(
                "HADRONIZATION_ANALYZED_DATA_BASE", oldBase.c_str());
        } else {
            gSystem->Unsetenv("HADRONIZATION_ANALYZED_DATA_BASE");
        }
        if (hadTag) {
            gSystem->Setenv(
                "HADRONIZATION_COMPLETE_ROOT_TAG", oldTag.c_str());
        } else {
            gSystem->Unsetenv("HADRONIZATION_COMPLETE_ROOT_TAG");
        }
    };

    int errors = 0;
    try {
        gSystem->Setenv(
            "HADRONIZATION_ANALYZED_DATA_BASE", analyzedDataBase);
        gSystem->Setenv(
            "HADRONIZATION_COMPLETE_ROOT_TAG", completeRootTag);
        const PlotConfig config = ReadConfig(
            configuration, "plotting/Plots/MultiplicityDistribution");
        const std::string expectedBase = ResolvePathFromBase(
            analyzedDataBase, config.hadronizationBase);
        if (config.baseDir != expectedBase ||
            config.beautyCompleteRootDir != completeRootTag ||
            config.charmCompleteRootDir != completeRootTag) {
            ++errors;
        }
        bool v2PolicyEnforced = false;
        try {
            const auto mode =
                HadronizationPairInput::DetermineProjectionMode(
                    HadronizationPairInput::
                        kRequiredV2MetadataObjectCount,
                    config.pairInputSelectionContract,
                    completeRootTag, "synthetic-v2.root");
            v2PolicyEnforced =
                HadronizationPairInput::AllowsV2(
                    config.pairInputSelectionContract) &&
                mode ==
                    HadronizationPairInput::ProjectionMode::kMetadataV2;
            if (v2PolicyEnforced) {
                HadronizationPairInput::ValidateConfiguredCombinatorics(
                    mode, config.pairCombinatoricsMode,
                    config.sameSignPairFactor,
                    config.pairInputSelectionContract,
                    "synthetic-v2.root");
            }
        } catch (const std::exception&) {
            v2PolicyEnforced =
                !HadronizationPairInput::AllowsV2(
                    config.pairInputSelectionContract);
        }
        bool legacyPolicyEnforced = false;
        try {
            const auto mode =
                HadronizationPairInput::DetermineProjectionMode(
                    0, config.pairInputSelectionContract,
                    config.pairInputSelectionContract
                        .legacyMetadataFreeCompleteRootTag,
                    "synthetic-legacy.root");
            legacyPolicyEnforced =
                HadronizationPairInput::AllowsLegacy(
                    config.pairInputSelectionContract) &&
                mode ==
                    HadronizationPairInput::ProjectionMode::
                        kTaggedLegacyRecutsV1;
        } catch (const std::exception&) {
            legacyPolicyEnforced =
                !HadronizationPairInput::AllowsLegacy(
                    config.pairInputSelectionContract);
        }
        bool wrongTagRejected = false;
        try {
            (void)HadronizationPairInput::DetermineProjectionMode(
                0, config.pairInputSelectionContract, completeRootTag,
                "synthetic-untagged.root");
        } catch (const std::exception&) {
            wrongTagRejected = true;
        }
        bool partialRejected = false;
        try {
            (void)HadronizationPairInput::DetermineProjectionMode(
                5, config.pairInputSelectionContract, completeRootTag,
                "synthetic-partial.root");
        } catch (const std::exception&) {
            partialRejected = true;
        }
        if (!v2PolicyEnforced || !legacyPolicyEnforced ||
            !wrongTagRejected || !partialRejected) {
            ++errors;
        }
    } catch (const std::exception& error) {
        std::cerr << "MULTIPLICITY_DATASET_SELECTOR_TEST_ERROR "
                  << error.what() << std::endl;
        ++errors;
    }
    restore();
    std::cout << "MULTIPLICITY_DATASET_SELECTOR_TEST errors=" << errors
              << " contract_policy_enforced=true"
              << std::endl;
    return errors;
}
