// ---------------------------------------------------------------------------
// Plot_MultiplicityDistribution_PercentileBoundaries.C
//
// Draw charged-particle multiplicity distributions with event-activity
// percentile boundaries for all configured PYTHIA tunes.
//
// Default usage from the Hadronization repository root:
//
//   root -l -b -q 'PlottingScripts/Plot_MultiplicityDistribution_PercentileBoundaries.C'
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
    std::vector<std::string> tunes;
    std::vector<PercentileClass> percentileClasses;
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
    configOut.baseDir =
        ResolvePathFromBase(config["base_dir"].get<std::string>(), configOut.hadronizationBase);
    configOut.beautyCompleteRootDir = config["bb_bar_complete_root_dir"].get<std::string>();
    configOut.charmCompleteRootDir = config["cc_bar_complete_root_dir"].get<std::string>();
    configOut.beautyFileName =
        FirstOSFileName(config, "beauty_correlations_to_analyse", "BplusBminus.root");
    configOut.charmFileName =
        FirstOSFileName(config, "charm_correlations_to_analyse", "DplusDminus.root");
    configOut.outputDir = ResolvePathFromBase(outputDir, configOut.hadronizationBase);

    for (const auto& tune : config["PYTHIA_TUNES"]) {
        configOut.tunes.push_back(tune.get<std::string>());
    }
    configOut.percentileClasses = ReadPercentileClasses(config);

    return configOut;
}

double CalculateMultiplicityThreshold(TH1D* hMult, double percentile)
{
    if (!hMult) throw std::runtime_error("Cannot calculate multiplicity threshold: null histogram");

    const double totalIntegral = hMult->Integral();
    if (totalIntegral <= 0.0) return hMult->GetBinCenter(1);

    const double target = ((100.0 - percentile) / 100.0) * totalIntegral;
    double runningIntegral = 0.0;
    for (int iBin = 1; iBin <= hMult->GetNbinsX(); ++iBin) {
        runningIntegral += hMult->GetBinContent(iBin);
        if (runningIntegral >= target) return hMult->GetBinCenter(iBin);
    }

    return hMult->GetBinCenter(hMult->GetNbinsX());
}

std::map<double, double> CalculateThresholds(TH1D* hMult,
                                             const std::vector<PercentileClass>& classes)
{
    std::set<double> percentiles;
    for (const auto& entry : classes) {
        percentiles.insert(entry.minPercentile);
        percentiles.insert(entry.maxPercentile);
    }

    std::map<double, double> thresholds;
    for (double percentile : percentiles) {
        thresholds[percentile] = CalculateMultiplicityThreshold(hMult, percentile);
    }
    return thresholds;
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
                          const std::map<double, double>& thresholds,
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

        const double x = item.second;
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
        const double left = std::max(xMin, thresholds.at(entry.maxPercentile));
        const double right = std::min(xMax, thresholds.at(entry.minPercentile));
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

        const std::map<double, double> thresholds =
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

        const std::map<double, double> thresholds =
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

        const std::map<double, double> thresholds =
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
        "PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json",
    const char* outputDir = "PlottingScripts/Plots/MultiplicityDistribution",
    bool normalize = false,
    bool strictInputs = false,
    bool compactMonashOnly = false)
{
    using namespace MultiplicityPercentilePlot;

    SetPlotStyle();
    const PlotConfig config = ReadConfig(configuration, outputDir);

    std::cout << "Using Hadronization base: " << config.hadronizationBase << std::endl;
    std::cout << "Using analyzed data dir: " << config.baseDir << std::endl;
    std::cout << "Writing multiplicity plots to: " << config.outputDir << std::endl;

    if (compactMonashOnly) {
        DrawCompactMonashCanvas(config, normalize, strictInputs);
    } else {
        DrawSharedCanvas(config, normalize, strictInputs);
    }
}

void Plot_MultiplicityDistribution_PercentileBoundaries_ByFlavor(
    const char* configuration =
        "PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json",
    const char* outputDir = "PlottingScripts/Plots/MultiplicityDistribution",
    bool normalize = false,
    bool strictInputs = false)
{
    using namespace MultiplicityPercentilePlot;

    SetPlotStyle();
    const PlotConfig config = ReadConfig(configuration, outputDir);

    std::cout << "Using Hadronization base: " << config.hadronizationBase << std::endl;
    std::cout << "Using analyzed data dir: " << config.baseDir << std::endl;
    std::cout << "Writing by-flavor multiplicity debug plots to: " << config.outputDir << std::endl;

    DrawFlavorCanvas(config, "BEAUTY", normalize, strictInputs);
    DrawFlavorCanvas(config, "CHARM", normalize, strictInputs);
}
