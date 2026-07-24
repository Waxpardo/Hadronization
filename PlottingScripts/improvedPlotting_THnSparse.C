// improvedPlotting.C
// Paul Veen (paul.veen@cern.ch)

// C headers
#include <iostream>
#include <fstream>
#include <algorithm>
#include <random>
#include <cmath>
#include <cstring>
#include <cstdlib>
#include <map>
#include <set>
#include <stdexcept>
#include <sstream>
#include <limits>
#include <vector>

// ROOT headers
#include "TFile.h"
#include "TH1D.h"
#include "THnSparse.h"
#include "TSystem.h"
#include "TCanvas.h"
#include "TString.h" // TODO: can use this for the legend entry names?
#include <TLegend.h>

#include "TunePlotStyle.h"

#if __has_include(<nlohmann/json.hpp>)
#include <nlohmann/json.hpp>
#elif __has_include("nlohmann/json.hpp")
#include "nlohmann/json.hpp"
#else
#error "Could not find nlohmann/json.hpp. Source the project/ROOT environment before compiling this macro."
#endif

using json = nlohmann::json;

// TODO: put structs in a header file (only after plotting is done in configuration.json)

// TODO: add verbose/debug flags to configuration.json

// TODO: update the other configuration.json files with the "configuration.json" script

// TODO: optimise drawing ranges for all plots

// TODO: add many more error statements and checks. 
// It needs to be clear for the user what went wrong when something went wrong (in particular related to the configuration.json)

// TODO: add new junctions simulations

// TODO: add close-packing simulations

// TODO: add many more plots and options to draw them (e.g. delta phi, delta phi delta eta, angular correlations, multiplciity spectra, kinematics, etc.) and add them to PDF

// TODO: display_name is used now.. maybe better to use the binLabel everywhere?

// Define a structure to hold OS and SS correlation file names

struct TriggerAssociateOSandSS {
    std::string trigger;
    std::string associateOS;
    std::string associateSS;
    std::string OS;
    std::string SS;
};

struct HistogramAndTriggerPtHistogramNames {
    std::string hDPhi;
    std::string hTrPt;
};


struct BinsFromTHnSparse {
    std::string binLabel;
    std::string hDPhi;
    std::string hTrPt;
    Double_t triggerPhiMin;
    Double_t triggerPhiMax;
    Double_t assocPhiMin;
    Double_t assocPhiMax;
    Double_t triggerEtaMin;
    Double_t triggerEtaMax;
    Double_t assocEtaMin;
    Double_t assocEtaMax;
    Double_t triggerPtMin;
    Double_t triggerPtMax;
    Double_t assocPtMin;
    Double_t assocPtMax;
    Double_t multiplicityMin;
    Double_t multiplicityMax;
};



struct YieldsAndErrors {
    std::vector<std::vector<std::vector<Double_t>>> vYields;
    std::vector<std::vector<std::vector<Double_t>>> vYieldsErrors;
    std::vector<std::vector<std::vector<Double_t>>> vYieldsRatioErrors;
};


struct YieldsAndErrorsMap {
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYields;
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYieldsErrors;
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYieldsRatioErrors;
};


struct SubsampleStatistics {
    Int_t nValues;
    Double_t mean;
    Double_t stdDev;
    Double_t stdError;
};


struct canvasConfigs {
    std::string canvasName;
    std::string drawFunctionToUse; // name of functions defined in improvedPlotting()
    std::vector<std::string> vCanvasTUNES; // tune to be drawn on given canvas
    std::string FLAVOUR; // just one allowed, but could implement with a new function
    std::string TriggerToUse; // which trigger to use in the yield plots?
    Int_t indexNominatorTUNE; // used for TUNE ratio plots, e.g. MONASH/JUNCTIONS to study enhancement explicitly
    Int_t indexDenominatorTUNE;
    std::vector<std::string> vBaryonNames; // baryons to be drawn (only for baryon/meson ratio plots!!!)
    bool useHardCodedSettings; // use hard-coded settings for this canvas (to be defined in function call)

    // Save output
    bool write;
    std::string writePath;
    std::string writeName;

    // Canvas settings
    std::string canvasTitle;
    std::string xAxisTitle;
    std::string yAxisTitle;
    Double_t xSizeCanvas; // new TCanvas(xSizeCanvas,ySizeCanvas)
    Double_t ySizeCanvas;
    Double_t xMinPad; // used for TPad(); mini pads that can be put on a global canvas to combine plots (optional argument)
    Double_t xMaxPad;
    Double_t yMinPad;
    Double_t yMaxPad;
    Double_t topMarginPad;
    Double_t bottomMarginPad;
    Double_t leftMarginPad;
    Double_t rightMarginPad;
    Double_t yMinAxis; // ->SetRangeUser()
    Double_t yMaxAxis;
    Double_t hMinimum; // ->SetMinimum()
    Double_t hMaximum; 
    bool setLogy;
    Double_t xMinLegend; // new TLegend(xMinLegend,yMinLegend,xMaxLegend,yMaxLegend)
    Double_t xMaxLegend;
    Double_t yMinLegend;
    Double_t yMaxLegend;
    // Empty is best set with entries = -1, sizes need to always match!! (TODO: fix this? make this better? necessary?)
    // TODO: add explanations to what these maps hold
    std::map<std::string, std::string> legendEntriesMap;
    std::map<std::string, Int_t> colourTUNEMap;
    std::map<std::string, Int_t> lineStyleDependencyMap; // TODO: same with lineWidths?
    std::map<std::string, Int_t> lineStyleBaryonMap;
};


// This struct is used to store the global canvases
// The user adds the names of the mini canvases that should be plotted on each global canvas
struct globalCanvasConfigs {
    std::string canvasName;
    std::string canvasTitle;
    std::vector<std::string> vMiniCanvases; // which TPads should be plotted on the global canvas

    // Save output
    bool write;
    std::string writePath;
    std::string writeName;

    Double_t xSizeCanvas; // new TCanvas(xSizeCanvas,ySizeCanvas)
    Double_t ySizeCanvas;
};


// To be taken from the configuration.json and send to main code
// output from readConfig()
struct CONFIGS {
    // General
    bool VERBOSE;
    bool CALCULATE_ERRORS;
    int nSubSamples;
    bool DRAW_CORRELATION_PLOTS;
    std::string base_dir;

    // MONASH, JUNCTIONS, else...
    std::vector<std::string> vTUNES;

    // Which complete_root production? (beauty and charm)
    std::string bbBarDir;
    std::string ccBarDir;
    std::string bbBarDir_subSamples;
    std::string ccBarDir_subSamples;

    // (BplusBminus.root,BplusBplus.root), added in a map with {trigger, {configs}}
    std::vector<TriggerAssociateOSandSS> vBeautyTriggerAssociateOSandSS;
    std::vector<TriggerAssociateOSandSS> vCharmTriggerAssociateOSandSS;
    std::map<std::string, std::vector<TriggerAssociateOSandSS>> beautyConfigs;
    std::map<std::string, std::vector<TriggerAssociateOSandSS>> charmConfigs;

    // Which bins will be plotted?
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames; // legacy
    std::vector<BinsFromTHnSparse> vBinsFromTHnSparse;

    // Plotting settings
    std::vector<canvasConfigs> vCanvasConfigs;
    canvasConfigs currentCanvasConfigs; // filled later, when looping over vCanvasConfigs, given as argument to plotting function
    std::vector<globalCanvasConfigs> vGlobalCanvasConfigs;
};

// Return type of function that projects out the THnSparse
struct CorrelationHistograms {
    TH1D* hDPhi;
    TH1D* hTrPt;
};


std::string JoinPath(const std::vector<std::string>& pieces) {
    std::string path;
    for (const auto& piece : pieces) {
        if (piece.empty()) { continue; }
        if (!path.empty() && path.back() != '/') { path += "/"; }
        if (!path.empty() && piece.front() == '/') {
            path += piece.substr(1);
        } else {
            path += piece;
        }
    }
    return path;
}


bool IsAbsolutePath(const std::string& path) {
    return !path.empty() && (path.front() == '/' || (path.size() > 1 && path[1] == ':'));
}


std::string ParentPath(const std::string& path) {
    if (path.empty() || path == "/") { return path; }
    const size_t slash = path.find_last_of('/');
    if (slash == std::string::npos) { return ""; }
    if (slash == 0) { return "/"; }
    return path.substr(0, slash);
}


std::string ExpandPath(const std::string& path) {
    char* expanded = gSystem->ExpandPathName(path.c_str());
    std::string result = expanded ? expanded : path;
    if (expanded) { delete[] expanded; }
    return result;
}


bool PathExists(const std::string& path) {
    return !path.empty() && !gSystem->AccessPathName(path.c_str());
}


std::string FindHadronizationBase() {
    const char* envBase = std::getenv("HADRONIZATION_BASE");
    if (envBase && PathExists(JoinPath({envBase, "PlottingScripts"}))) {
        return ExpandPath(envBase);
    }

    std::string current = ExpandPath(gSystem->WorkingDirectory());
    while (!current.empty()) {
        if (PathExists(JoinPath({current, "PlottingScripts", "improvedPlotting_THnSparse.C"})) ||
            PathExists(JoinPath({current, ".git"}))) {
            return current;
        }
        const std::string parent = ParentPath(current);
        if (parent == current) { break; }
        current = parent;
    }

    return ExpandPath(gSystem->WorkingDirectory());
}


std::string ResolvePathFromBase(const std::string& path, const std::string& hadronizationBase) {
    if (path.empty() || path == "NONE") { return path; }
    const std::string expanded = ExpandPath(path);
    if (IsAbsolutePath(expanded)) { return expanded; }
    return JoinPath({hadronizationBase, expanded});
}


std::string ResolveConfigurationPath(const std::string& path, const std::string& hadronizationBase) {
    const std::vector<std::string> candidates = {
        path,
        ResolvePathFromBase(path, hadronizationBase),
        JoinPath({hadronizationBase, "PlottingScripts", path})
    };

    for (const auto& candidate : candidates) {
        if (PathExists(candidate)) { return candidate; }
    }

    std::ostringstream message;
    message << "Could not find configuration file '" << path << "'. Tried:";
    for (const auto& candidate : candidates) { message << "\n  - " << candidate; }
    throw std::runtime_error(message.str());
}


std::string ResolveCompleteRootFile(
    const std::string& baseDir,
    const std::string& tune,
    const std::string& completeRootDir,
    const std::string& fileName
) {
    const std::vector<std::string> candidates = {
        JoinPath({baseDir, tune, completeRootDir + "_" + tune, fileName}),
        JoinPath({baseDir, tune, completeRootDir, fileName}),
        JoinPath({baseDir, completeRootDir + "_" + tune, fileName}),
        JoinPath({baseDir, completeRootDir, fileName})
    };

    for (const auto& candidate : candidates) {
        if (PathExists(candidate)) { return candidate; }
    }

    std::ostringstream message;
    message << "Could not find input ROOT file '" << fileName << "' for tune " << tune
            << ". Tried:";
    for (const auto& candidate : candidates) { message << "\n  - " << candidate; }
    throw std::runtime_error(message.str());
}


std::string ResolveSubSampleRootFile(
    const std::string& subSampleBaseDir,
    const std::string& tune,
    int subSampleIndex,
    const std::string& fileName
) {
    const std::string subSampleDir = Form("combined_root_%i", subSampleIndex);
    const std::vector<std::string> candidates = {
        JoinPath({subSampleBaseDir + "_" + tune, subSampleDir, fileName}),
        JoinPath({subSampleBaseDir, tune, subSampleDir, fileName})
    };

    for (const auto& candidate : candidates) {
        if (PathExists(candidate)) { return candidate; }
    }

    std::ostringstream message;
    message << "Could not find subsample ROOT file '" << fileName << "' for tune " << tune
            << ", subsample " << subSampleIndex << ". Tried:";
    for (const auto& candidate : candidates) { message << "\n  - " << candidate; }
    throw std::runtime_error(message.str());
}


TFile* OpenRootFileOrThrow(const std::string& path) {
    TFile* file = TFile::Open(path.c_str(), "READ");
    if (!file || file->IsZombie()) {
        throw std::runtime_error("Could not open input ROOT file: " + path);
    }
    return file;
}


template <typename TObjectType>
TObjectType* GetObjectOrThrow(TFile* file, const char* objectName, const std::string& filePath) {
    if (!file) {
        throw std::runtime_error(std::string("Null TFile while reading object: ") + objectName);
    }

    TObjectType* object = dynamic_cast<TObjectType*>(file->Get(objectName));
    if (!object) {
        throw std::runtime_error(
            std::string("Missing or wrong-type object '") + objectName + "' in " + filePath
        );
    }
    return object;
}


// Derive the histograms (delta phi and trigger pt) from the THnSparse, including user-defined cuts
// Pay attention that the OS and SS histograms need to have the same amount of bins!
TH1D* GetCorrelationHistograms(THnSparseD* hCorrelations, const BinsFromTHnSparse& cuts, const TString& suffix = ""
) {
    // THnSparse hCorrelations: (careful: the 'trigger' and 'associate' refer to the pairs)
        // 0 = DeltaPhi
        // 1 = DeltaEta
        // 2 = TriggerEta
        // 3 = AssocEta
        // 4 = TriggerPt
        // 5 = AssocPt
        // 6 = Multiplicity

    if (!hCorrelations) {
        throw std::runtime_error("Cannot project correlations: hCorrelations is null");
    }

    // Reset axes
    for (int i = 0; i < hCorrelations->GetNdimensions(); ++i) { hCorrelations->GetAxis(i)->SetRange(); }

        /*
        hCorrelations->GetAxis(2)->SetRangeUser(
            cuts.triggerEtaMin,
            cuts.triggerEtaMax
        );

        hCorrelations->GetAxis(3)->SetRangeUser(
            cuts.assocEtaMin,
            cuts.assocEtaMax
        );

        hCorrelations->GetAxis(4)->SetRangeUser(
            cuts.triggerPtMin,
            cuts.triggerPtMax
        );

        hCorrelations->GetAxis(5)->SetRangeUser(
            cuts.assocPtMin,
            cuts.assocPtMax
        );
        */

        std::cout << "--> applying multiplicity cut from " << cuts.multiplicityMin << " to " << cuts.multiplicityMax << std::endl;

        hCorrelations->GetAxis(6)->SetRangeUser(
            cuts.multiplicityMin,
            cuts.multiplicityMax
    );

    TH1D* hDPhi = (TH1D*)hCorrelations->Projection(0, "E");
    hDPhi->SetName(Form("hDPhi%s", suffix.Data()));

    return hDPhi;
}


// Derive the trigger pt histogram from the trigger kinematics THnSparse, including user-defined cuts
// This histogram is then used for normalisation of the hDPhi histogram
// Pay attention that the OS and SS histograms need to have the same amount of bins!
TH1D* GetTriggerPtHistograms(THnSparseD* hTrKinematics, const BinsFromTHnSparse& cuts, const TString& suffix = ""
) {
    // THnSparse hCorrelations: (careful: the 'trigger' and 'associate' refer to the pairs)
        // 0 = phi
        // 1 = eta
        // 2 = pt
        // 3 = Multiplicity

    if (!hTrKinematics) {
        throw std::runtime_error("Cannot project trigger pT: hTrKinematics is null");
    }

    // Reset axes
    for (int i = 0; i < hTrKinematics->GetNdimensions(); ++i) { hTrKinematics->GetAxis(i)->SetRange(); }

        std::cout << "--> applying multiplicity cut from " << cuts.multiplicityMin << " to " << cuts.multiplicityMax << std::endl;

        hTrKinematics->GetAxis(3)->SetRangeUser(
            cuts.multiplicityMin,
            cuts.multiplicityMax
        );

        TH1D* hTrPt = (TH1D*)hTrKinematics->Projection(2, "E");
        hTrPt->SetName(Form("hTrPt%s", suffix.Data()));

    return hTrPt;
}


// Helper function to calculate multiplicity cuts using multiplicity percentiles 
double GetMultiplicityThreshold(
    TH1D* hMult,
    double percentile
) {
    const double totalIntegral = hMult->Integral();

    double runningIntegral = 0.0;

    const double targetFraction =
        (100.0 - percentile) / 100.0;

    for (int ibin = 1; ibin <= hMult->GetNbinsX(); ++ibin)
    {
        runningIntegral += hMult->GetBinContent(ibin);

        if (runningIntegral >= targetFraction * totalIntegral)
        {
            return hMult->GetBinCenter(ibin);
        }
    }

    return hMult->GetBinCenter(hMult->GetNbinsX());
}


// Function to find the index of a tune name
int findTuneIndex(const std::vector<std::string>& vTUNES, const std::string& tuneName) {
    auto it = std::find(vTUNES.begin(), vTUNES.end(), tuneName);
    if (it != vTUNES.end()) {
        return std::distance(vTUNES.begin(), it);
    } else {
        return -1;
    }
}

// Simple function to check if canvas name is equal to the desired name.
// Used for hard-coded options on a specific canvas
// TODO: can also use generalised version for other strcmp I do? (loses, in my opinion, some clarity)
bool isCanvasNameEqualTo(std::string canvasName, std::string targetName) {
    return strcmp(canvasName.c_str(), targetName.c_str()) == 0;
}

// Function to write canvas to given path and name 
void writeCanvasToFiles(bool VERBOSE, TCanvas *canvas, std::string writePath, std::string writeName) {
    if (VERBOSE) { 
        std::cout << "- Writing canvas with name " << writeName << " to path " << writePath << std::endl;
    }
    gSystem->mkdir(writePath.c_str(), true);
    canvas->SaveAs((writePath + "/" + writeName + "_PDF" + ".pdf").c_str());
    canvas->SaveAs((writePath + "/" + writeName + "_PNG" + ".png").c_str());
    canvas->SaveAs((writePath + "/" + writeName + "_MACRO" + ".C").c_str());
    if (VERBOSE) {
        std::cout << "- Files written sucesfully (...?)" << std::endl;
    }
}


// TODO: isn't this the same as the function below?
// Maybe keep this one because it's more clear to the user what it does?
bool plotBaryon(const std::string& name, const std::vector<std::string>& baryonNames) {
    return std::find(baryonNames.begin(), baryonNames.end(), name) != baryonNames.end();
}


// Function to check if a string is in a vector of strings
bool isInVector(const std::string& value, const std::vector<std::string>& vec) {
    return std::find(vec.begin(), vec.end(), value) != vec.end();
}


YieldsAndErrors YieldsAndErrorsForGivenTrigger(const std::string& trigger, const YieldsAndErrorsMap& mapYieldsAndErrors, bool CALCULATE_ERRORS) {
    YieldsAndErrors yieldsAndErrors;

    std::cout << "Requested trigger: " << trigger << std::endl;
    std::cout << "Available keys in mapYields:" << std::endl;
    for (const auto& [key, value] : mapYieldsAndErrors.mapYields)
        std::cout << "  [" << key << "]\n";
    std::cout << "mapYieldsErrors keys:" << std::endl;
    for (const auto& [key, value] : mapYieldsAndErrors.mapYieldsErrors)
        std::cout << "  [" << key << "]\n";
    std::cout << "mapYieldsRatioErrors keys:" << std::endl;
    for (const auto& [key, value] : mapYieldsAndErrors.mapYieldsRatioErrors)
        std::cout << "  [" << key << "]\n";

    yieldsAndErrors.vYields = mapYieldsAndErrors.mapYields.at(trigger);
    if (CALCULATE_ERRORS) { yieldsAndErrors.vYieldsErrors = mapYieldsAndErrors.mapYieldsErrors.at(trigger); }
    if (CALCULATE_ERRORS) { yieldsAndErrors.vYieldsRatioErrors = mapYieldsAndErrors.mapYieldsRatioErrors.at(trigger); }

    return yieldsAndErrors;
}

void ApplyTuneVisualStyle(TH1D* hist, const std::string& tune, bool applyTuneLineStyle = false)
{
    if (!hist) return;
    HadronizationPlotStyle::ApplyTuneLineAndMarker(hist, tune, applyTuneLineStyle);
    hist->SetLineWidth(2);
    hist->SetMarkerSize(1.0);
}


// TODO: must be possible to do this more efficiently.. not really necessary for now to improve..
// TODO: get colour from predefined list (for the tunes)?
// User defined function that gives the ultimate freedom to come up with legend entries
// 'normal' entries with dependencies or baryon/meson ratios can be done easier with 'normal' configuration.json
// Use syntax
// void createCustomLegendEntry_NAME
// Then make sure this function is checked and called in the drawing function where it's used (see examples in those functions)
/*
void createCustomLegendEntry_BeautyMONASH(TLegend *legend, std::string displayName) {
    TH1D *dummyHist = new TH1D("dummyHist", "", 1, 0, 1);
    dummyHist->SetLineColor(kBlack);
    dummyHist->SetLineStyle(1);
    dummyHist->SetLineWidth(2);
    legend->AddEntry(dummyHist, displayName.c_str(), "l");
}
void createCustomLegendEntry_BeautyJUNCTIONS(TLegend *legend, std::string displayName) {
    TLegendEntry* entryJunctionsBeauty = legend->AddEntry("BeautyJUNCTIONS", displayName.c_str(), "l");
	entryJunctionsBeauty->SetLineColor(kRed);
	entryJunctionsBeauty->SetLineStyle(1);
	entryJunctionsBeauty->SetLineWidth(2);
}
*/


// Function that creates mini pads in case you do not want to use TCanvas->Divide()
// TODO: apply this function everywhere where required...
TPad* createMiniPad(const char* name,
                    double x1, double y1,
                    double x2, double y2)
{
    TPad *pad = new TPad(name, name, x1, y1, x2, y2);

    pad->SetTickx(1);
    pad->SetTicky(1);
    pad->SetTopMargin(0.05);
    pad->SetBottomMargin(0.12);
    pad->SetLeftMargin(0.14);
    pad->SetRightMargin(0.02);

    pad->Draw();

    return pad;
}


CONFIGS readConfig(const char* configurations) {

    std::cout << std::endl;
    std::cout << "*** Reading configuration.json ***" << std::endl;
    std::cout << std::endl;

    const std::string hadronizationBase = FindHadronizationBase();
    const std::string configurationPath = ResolveConfigurationPath(configurations, hadronizationBase);

    // Open the JSON configuration file
    std::ifstream configFile(configurationPath);
    if (!configFile.is_open()) {
        throw std::runtime_error("Error opening configuration file: " + configurationPath);
    }

    // Parse the JSON file
    json config;
    configFile >> config;

    // Extract values from the JSON
    // Generic options
    bool VERBOSE = config["VERBOSE"].get<bool>();
    bool CALCULATE_ERRORS = config["calculate_errors"].get<bool>();
    std::string bbBarDir_sub_samples = ResolvePathFromBase(config["bb_bar_complete_root_dir_sub_samples"], hadronizationBase);
    std::string ccBarDir_sub_samples = ResolvePathFromBase(config["cc_bar_complete_root_dir_sub_samples"], hadronizationBase);
    int nSubSamples = config["nSubSamples"].get<int>();
    bool DRAW_CORRELATION_PLOTS = config["draw_correlation_plots"].get<bool>();

    // RootFiles path ("base directory")
    std::string base_dir = ResolvePathFromBase(config["base_dir"], hadronizationBase);

    // Tunes
    std::vector<std::string> vTUNES;
    for (const auto& TUNE : config["PYTHIA_TUNES"]) {
        vTUNES.push_back(TUNE);
    }

    // Complete_root_dirs
    std::string bbBarDir = config["bb_bar_complete_root_dir"];
    std::string ccBarDir = config["cc_bar_complete_root_dir"];

    // Check if everything went well
    std::string path_to_complete_root_dir;
    std::string path_to_complete_root_dir_sub_samples;
    for (const auto& TUNE : vTUNES) {
        path_to_complete_root_dir = base_dir + "/" + TUNE + "/" + bbBarDir;
        path_to_complete_root_dir_sub_samples = bbBarDir_sub_samples + "_" + TUNE;
        std::cout << "Full path beauty " << TUNE << ": " << path_to_complete_root_dir << std::endl;
        std::cout << "Full path beauty sub samples " << TUNE << ": " << path_to_complete_root_dir_sub_samples << std::endl;
    }
    for (const auto& TUNE : vTUNES) {
        path_to_complete_root_dir = base_dir + "/" + TUNE + "/" + ccBarDir;
        path_to_complete_root_dir_sub_samples = ccBarDir_sub_samples + "_" + TUNE;
        std::cout << "Full path charm " << TUNE << ": " << path_to_complete_root_dir << std::endl;
        std::cout << "Full path charm sub samples " << TUNE << ": " << path_to_complete_root_dir_sub_samples << std::endl;
    }
    std::cout << std::endl;

    // toremove
    std::vector<TriggerAssociateOSandSS> vBeautyTriggerAssociateOSandSS;
    /*
    std::vector<TriggerAssociateOSandSS> vBeautyTriggerAssociateOSandSS;
    for (const auto& configPair : config["beauty_correlations_to_analyse"]) {
        TriggerAssociateOSandSS pair;
        pair.trigger = configPair["trigger"].get<std::string>();
        pair.associateOS = configPair["associateOS"].get<std::string>();
        pair.associateSS = configPair["associateSS"].get<std::string>();
        pair.OS = configPair["OS"].get<std::string>();
        pair.SS = configPair["SS"].get<std::string>();
        vBeautyTriggerAssociateOSandSS.push_back(pair);
    }
    for (const auto& pair : vBeautyTriggerAssociateOSandSS) {
        std::cout << "OS File: " << pair.OS << ", SS File: " << pair.SS << std::endl;
    }
    */

   // Which correlations need to be analysed?
    std::map<std::string, std::vector<TriggerAssociateOSandSS>> beautyConfigs;
    for (const auto& triggerEntry : config["beauty_correlations_to_analyse"]) {
        auto& configs = beautyConfigs[triggerEntry["trigger"].get<std::string>()];
        // Fill the map with the configs for the specific trigger
        for (const auto& cfg : triggerEntry["configs"]) {
            configs.push_back({
                cfg["trigger"].get<std::string>(),
                cfg["associateOS"].get<std::string>(),
                cfg["associateSS"].get<std::string>(),
                cfg["OS"].get<std::string>(),
                cfg["SS"].get<std::string>()
            });
            std::cout << "OS File: " << cfg["OS"] << ", SS File: " << cfg["SS"] << std::endl;
        }
    }

    // toremove
    std::vector<TriggerAssociateOSandSS> vCharmTriggerAssociateOSandSS;
    /*
    for (const auto& configPair : config["charm_correlations_to_analyse"]) {
        TriggerAssociateOSandSS pair;
        pair.trigger = configPair["trigger"].get<std::string>();
        pair.associateOS = configPair["associateOS"].get<std::string>();
        pair.associateSS = configPair["associateSS"].get<std::string>();
        pair.OS = configPair["OS"].get<std::string>();
        pair.SS = configPair["SS"].get<std::string>();
        vCharmTriggerAssociateOSandSS.push_back(pair);
    }
    for (const auto& pair : vBeautyTriggerAssociateOSandSS) {
        std::cout << "OS File: " << pair.OS << ", SS File: " << pair.SS << std::endl;
    }
    std::cout << std::endl;
    */

   std::map<std::string, std::vector<TriggerAssociateOSandSS>> charmConfigs;
    for (const auto& triggerEntry : config["charm_correlations_to_analyse"]) {
        auto& configs = charmConfigs[triggerEntry["trigger"].get<std::string>()];
        // Fill the map with the configs for the specific trigger
        for (const auto& cfg : triggerEntry["configs"]) {
            configs.push_back({
                cfg["trigger"].get<std::string>(),
                cfg["associateOS"].get<std::string>(),
                cfg["associateSS"].get<std::string>(),
                cfg["OS"].get<std::string>(),
                cfg["SS"].get<std::string>()
            });
            std::cout << "OS File: " << cfg["OS"] << ", SS File: " << cfg["SS"] << std::endl;
        }
    }

    // Which histograms need to be analysed?
    // i.e. which dependencies (pT, mult, etc.)
    // std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames;
    std::vector<BinsFromTHnSparse> vBinsFromTHnSparse;
    for (const auto& configPair : config["histograms_to_analyse"]) {
        // HistogramAndTriggerPtHistogramNames pair;
        BinsFromTHnSparse pair;
        pair.binLabel = configPair["binLabel"].get<std::string>();
        pair.hDPhi = configPair["hDPhi"].get<std::string>();
        pair.hTrPt = configPair["hTrPt"].get<std::string>();
        pair.triggerPhiMin = configPair["triggerPhiMin"].get<Double_t>();
        pair.triggerPhiMax = configPair["triggerPhiMax"].get<Double_t>();
        pair.assocPhiMin = configPair["assocPhiMin"].get<Double_t>();
        pair.assocPhiMax = configPair["assocPhiMax"].get<Double_t>();
        pair.triggerEtaMin = configPair["triggerEtaMin"].get<Double_t>();
        pair.triggerEtaMax = configPair["triggerEtaMax"].get<Double_t>();
        pair.assocEtaMin = configPair["assocEtaMin"].get<Double_t>();
        pair.assocEtaMax = configPair["assocEtaMax"].get<Double_t>();
        pair.triggerPtMin = configPair["triggerPtMin"].get<Double_t>();
        pair.triggerPtMax = configPair["triggerPtMax"].get<Double_t>();
        pair.assocPtMin = configPair["assocPtMin"].get<Double_t>();
        pair.assocPtMax = configPair["assocPtMax"].get<Double_t>();
        pair.multiplicityMin = configPair["multiplicityMin"].get<Double_t>();
        pair.multiplicityMax = configPair["multiplicityMax"].get<Double_t>();
        vBinsFromTHnSparse.push_back(pair);
    }
    for (const auto& pair : vBinsFromTHnSparse) {
        std::cout
            << "TrPhi=[" << pair.triggerPhiMin << ", " << pair.triggerPhiMax << "] "
            << "AssocPhi=[" << pair.assocPhiMin << ", " << pair.assocPhiMax << "] "
            << "TrEta=[" << pair.triggerEtaMin << ", " << pair.triggerEtaMax << "] "
            << "AssocEta=[" << pair.assocEtaMin << ", " << pair.assocEtaMax << "] "
            << "TrPt=[" << pair.triggerPtMin << ", " << pair.triggerPtMax << "] "
            << "AssocPt=[" << pair.assocPtMin << ", " << pair.assocPtMax << "] "
            << "Mult=[" << pair.multiplicityMin << ", " << pair.multiplicityMax << "]"
        << std::endl;
    }
    std::cout << std::endl;

    // How should everything be drawn?
    std::vector<canvasConfigs> vCanvasConfigs;
    for (const auto& configPair : config["canvases_to_be_drawn"]) {
        canvasConfigs pair;
        pair.canvasName = configPair["canvas_name"].get<std::string>();
        pair.drawFunctionToUse = configPair["draw_function_to_use"].get<std::string>();
        std::vector<std::string> vCanvasTUNES;
        for (const auto& TUNE : configPair["TUNES"]) {
            vCanvasTUNES.push_back(TUNE);
        }
        pair.vCanvasTUNES = vCanvasTUNES;
        pair.FLAVOUR = configPair["FLAVOUR"].get<std::string>();
        pair.TriggerToUse = configPair["TriggerToUse"].get<std::string>(); // must be identical to trigger name from 'histograms to draw' section! TODO: do something about that..
        std::string nominatorTuneName = configPair["nominator_TUNE"].get<std::string>();
        pair.indexNominatorTUNE = -1;
        if (nominatorTuneName != "NONE") {
            pair.indexNominatorTUNE = findTuneIndex(vTUNES, nominatorTuneName);
            if (pair.indexNominatorTUNE != -1) {
                std::cout << "Index of " << nominatorTuneName << " is: " << pair.indexNominatorTUNE << std::endl;
            } else {
                std::cout << nominatorTuneName << " ERROR: TUNE not found in vTUNES." << std::endl;
            }
        }
        std::string denominatorTuneName = configPair["denominator_TUNE"].get<std::string>();
        pair.indexDenominatorTUNE = -1;
        if (denominatorTuneName != "NONE") {
            pair.indexDenominatorTUNE = findTuneIndex(vTUNES, denominatorTuneName);
            if (pair.indexDenominatorTUNE != -1) {
                std::cout << "Index of " << denominatorTuneName << " is: " << pair.indexDenominatorTUNE << std::endl;
            } else {
                std::cout << denominatorTuneName << " ERROR: TUNE not found in vTUNES." << std::endl;
            }
        }
        std::vector<std::string> vBaryonNames;
        for (const auto& baryonName : configPair["baryons_to_plot_in_baryon/meson_ratio"]) {
            // TODO: verbose
            // std::cout << "pushing back " << baryonName << std::endl;
            vBaryonNames.push_back(baryonName);
        }
        // TODO: change all instances of 'bool' into 'Bool_t'
        pair.vBaryonNames = vBaryonNames;
        pair.useHardCodedSettings = configPair["use_hard_coded_settings"].get<bool>();
        pair.write = configPair["write"].get<bool>();
        pair.writePath = ResolvePathFromBase(configPair["write_path"].get<std::string>(), hadronizationBase);
        pair.writeName = configPair["write_name"].get<std::string>();

        // Plotting settings
        pair.canvasTitle = configPair["canvas_title"].get<std::string>();
        pair.xAxisTitle = configPair["x_axis_title"].get<std::string>();
        pair.yAxisTitle = configPair["y_axis_title"].get<std::string>();
        pair.xSizeCanvas = configPair["x_size_canvas"].get<Double_t>();
        pair.ySizeCanvas = configPair["y_size_canvas"].get<Double_t>();
        pair.xMinPad = configPair["x_min_mini_pad"].get<Double_t>();
        pair.xMaxPad = configPair["x_max_mini_pad"].get<Double_t>();
        pair.yMinPad = configPair["y_min_mini_pad"].get<Double_t>();
        pair.yMaxPad = configPair["y_max_mini_pad"].get<Double_t>();
        pair.topMarginPad = configPair["top_margin_mini_pad"].get<Double_t>();
        pair.bottomMarginPad = configPair["bottom_margin_mini_pad"].get<Double_t>();
        pair.leftMarginPad = configPair["left_margin_mini_pad"].get<Double_t>();
        pair.rightMarginPad = configPair["right_margin_mini_pad"].get<Double_t>();
        pair.yMinAxis = configPair["y_min_axis"].get<Double_t>();
        pair.yMaxAxis = configPair["y_max_axis"].get<Double_t>();
        pair.hMinimum = configPair["histogram_minimum"].get<Double_t>();
        pair.hMaximum = configPair["histogram_maximum"].get<Double_t>();
        pair.setLogy = configPair["set_log_y"].get<bool>();
        pair.xMinLegend = configPair["x_min_legend"].get<Double_t>();
        pair.xMaxLegend = configPair["x_max_legend"].get<Double_t>();
        pair.yMinLegend = configPair["y_min_legend"].get<Double_t>();
        pair.yMaxLegend = configPair["y_max_legend"].get<Double_t>();
        std::map<std::string, std::string> legendEntriesMap;
        for (const auto& configLegendPair : configPair["legend_entries"]) {
            std::string objectName = configLegendPair["object_name"].get<std::string>();
            std::string displayName = configLegendPair["display_name"].get<std::string>();
            legendEntriesMap[objectName] = displayName;
            // TODO: verbose
            // std::cout << "Inserted: " << objectName << " -> " << displayName << std::endl;
        }
        // TODO: probably better to add this to the configuration part where the dependenies are given. 
        // TODO: Possibly also do that for the baryons then.
        pair.legendEntriesMap = legendEntriesMap;
        std::map<std::string, Int_t> colourTUNEMap;
        for (const auto& configColourTUNEPair : configPair["TUNE_colours"]) {
            std::string objectName = configColourTUNEPair["TUNE_name"].get<std::string>();
            Int_t optionName = configColourTUNEPair["colour"].get<Int_t>();
            if (HadronizationPlotStyle::IsKnownTune(objectName)) {
                optionName = HadronizationPlotStyle::TuneColor(objectName);
            }
            colourTUNEMap[objectName] = optionName;
            // TODO: verbose
            // std::cout << "Inserted: " << objectName << " -> " << optionName << std::endl;
        }
        pair.colourTUNEMap = colourTUNEMap;
        std::map<std::string, Int_t> lineStyleDependencyMap;
        for (const auto& configLineStyleDependencyPair : configPair["dependency_line_styles"]) {
            std::string objectName = configLineStyleDependencyPair["dependency_name"].get<std::string>();
            Int_t optionName = configLineStyleDependencyPair["line_style"].get<Int_t>();
            lineStyleDependencyMap[objectName] = optionName;
            // TODO: verbose
            // std::cout << "Inserted: " << objectName << " -> " << optionName << std::endl;
        }
        pair.lineStyleDependencyMap = lineStyleDependencyMap;
        std::map<std::string, Int_t> lineStyleBaryonMap;
        for (const auto& configLineStyleBaryonPair : configPair["baryon_line_styles"]) {
            std::string objectName = configLineStyleBaryonPair["baryon_name"].get<std::string>();
            Int_t optionName = configLineStyleBaryonPair["line_style"].get<Int_t>();
            lineStyleBaryonMap[objectName] = optionName;
            // TODO: verbose
            // std::cout << "Inserted: " << objectName << " -> " << optionName << std::endl;
        }
        pair.lineStyleBaryonMap = lineStyleBaryonMap;

        // Sumarise configurations in struct, save per canvas
        // TODO: change names, don't let everything be 'pair'
        vCanvasConfigs.push_back(pair);
    }
    for (const auto& pair : vCanvasConfigs) {
        // TODO: verbose
        // std::cout << "canvasName: " << pair.canvasName << std::endl;
        // std::cout << "drawFunctionToUse: " << pair.drawFunctionToUse << std::endl;
        // TODO: add print for vTUNES (after general print vector function)
    }
    std::cout << std::endl;

    // Which canvases should go on global canvases?
    // Define all global canvases here
    std::vector<globalCanvasConfigs> vGlobalCanvasConfigs;
    for (const auto& configPair : config["global_canvases_to_be_drawn"]) {
        globalCanvasConfigs pair;
        pair.canvasName = configPair["canvas_name"].get<std::string>();
        pair.canvasTitle = configPair["canvas_title"].get<std::string>();
        std::vector<std::string> vMiniCanvases;
        for (const auto& miniCanvas : configPair["mini_canvases"]) {
            vMiniCanvases.push_back(miniCanvas);
        }
        pair.vMiniCanvases = vMiniCanvases;
        pair.write = configPair["write"].get<bool>();
        pair.writePath = ResolvePathFromBase(configPair["write_path"].get<std::string>(), hadronizationBase);
        pair.writeName = configPair["write_name"].get<std::string>();
        pair.xSizeCanvas = configPair["x_size_canvas"].get<Double_t>();
        pair.ySizeCanvas = configPair["y_size_canvas"].get<Double_t>();
        vGlobalCanvasConfigs.push_back(pair);
    }

    // TODO: make a function that prints content of a vector
    CONFIGS configs_from_json;
    configs_from_json.VERBOSE = VERBOSE;
    configs_from_json.CALCULATE_ERRORS = CALCULATE_ERRORS;
    configs_from_json.nSubSamples = nSubSamples;
    configs_from_json.DRAW_CORRELATION_PLOTS = DRAW_CORRELATION_PLOTS;
    configs_from_json.base_dir = base_dir;
    configs_from_json.vTUNES = vTUNES;
    configs_from_json.bbBarDir = bbBarDir;
    configs_from_json.ccBarDir = ccBarDir;
    configs_from_json.bbBarDir_subSamples = bbBarDir_sub_samples;
    configs_from_json.ccBarDir_subSamples = ccBarDir_sub_samples;
    configs_from_json.vBeautyTriggerAssociateOSandSS = vBeautyTriggerAssociateOSandSS; // toremove
    configs_from_json.vCharmTriggerAssociateOSandSS = vCharmTriggerAssociateOSandSS; // toremove
    configs_from_json.beautyConfigs = beautyConfigs;
    configs_from_json.charmConfigs = charmConfigs;
    // configs_from_json.vHistogramAndTriggerPtHistogramNames = vHistogramAndTriggerPtHistogramNames;
    configs_from_json.vBinsFromTHnSparse = vBinsFromTHnSparse;
    configs_from_json.vCanvasConfigs = vCanvasConfigs;
    configs_from_json.vGlobalCanvasConfigs = vGlobalCanvasConfigs;

    std::cout << "Configurations successfully read from JSON with parameters:" << std::endl;
    std::cout << "VERBOSE = " << VERBOSE << std::endl;
    std::cout << "- CALCULATE_ERRORS = " << CALCULATE_ERRORS << std::endl;
    std::cout << "- nSubSamples = " << nSubSamples << std::endl;
    std::cout << "- DRAW_CORRELATION_PLOTS = " << DRAW_CORRELATION_PLOTS << std::endl;
    std::cout << "- base_dir = " << base_dir << std::endl;
    std::cout << "- vTUNES.size() = " << vTUNES.size() << std::endl;
    std::cout << "- bbBarDir = " << bbBarDir << std::endl;
    std::cout << "- ccBarDir = " << ccBarDir << std::endl;
    std::cout << "- bbBarDir_sub_samples = " << bbBarDir_sub_samples << std::endl;
    std::cout << "- ccBarDir_sub_samples = " << ccBarDir_sub_samples << std::endl;
    std::cout << "- vBeautyTriggerAssociateOSandSS.size() = " << vBeautyTriggerAssociateOSandSS.size() << std::endl;
    std::cout << "- vCharmTriggerAssociateOSandSS.size() = " << vCharmTriggerAssociateOSandSS.size() << std::endl;
    // std::cout << "- vHistogramAndTriggerPtHistogramNames.size() = " << vHistogramAndTriggerPtHistogramNames.size() << std::endl;
    std::cout << "- vBinsFromTHnSparse.size() = " << vBinsFromTHnSparse.size() << std::endl;
    // vCanvasConfigs
    // TODO: give overview of canvases to be drawn and their settings etc.
    // Check if specific trigger configurations are read correctly
    std::cout << "Beauty triggers:\n";
    for (const auto& [trigger, configs] : beautyConfigs) {
        std::cout << "* Trigger: " << trigger << std::endl;;
        for (const auto& cfg : configs) {
            std::cout << "  OS associate: " << cfg.associateOS
                    << ", SS associate: " << cfg.associateSS << std::endl;;
        }
    }
    std::cout << "Charm triggers:\n";
    for (const auto& [trigger, configs] : charmConfigs) {
        std::cout << "* Trigger: " << trigger << std::endl;;
        for (const auto& cfg : configs) {
            std::cout << "  OS associate: " << cfg.associateOS
                    << ", SS associate: " << cfg.associateSS << std::endl;;
        }
    }
    std::cout << std::endl;

    return configs_from_json;

} // readConfig()


// Simple function that returns the propagated error from a ratio A/B with errors for A and B
// Assumes A and B are uncorrelated
Double_t propagateRatioError(Double_t valueA, Double_t valueB, Double_t errorA, Double_t errorB) {
    if (!std::isfinite(valueA) || !std::isfinite(valueB) ||
        !std::isfinite(errorA) || !std::isfinite(errorB) ||
        valueA == 0.0 || valueB == 0.0) {
        return 0.0;
    }

    Double_t relativeUncertainty = pow((errorA / valueA), 2) + pow((errorB / valueB), 2);
    return ((valueA / valueB) * sqrt(relativeUncertainty));
} // propagateRatioError()


Double_t safeRatio(Double_t numerator, Double_t denominator) {
    if (!std::isfinite(numerator) || !std::isfinite(denominator) || denominator == 0.0) {
        return std::numeric_limits<Double_t>::quiet_NaN();
    }
    return numerator / denominator;
}


SubsampleStatistics calculateSubsampleStatistics(const std::vector<Double_t>& values) {
    std::vector<Double_t> finiteValues;
    finiteValues.reserve(values.size());
    for (const auto value : values) {
        if (std::isfinite(value)) { finiteValues.push_back(value); }
    }

    SubsampleStatistics stats{static_cast<Int_t>(finiteValues.size()), 0.0, 0.0, 0.0};
    if (finiteValues.empty()) { return stats; }

    for (const auto value : finiteValues) { stats.mean += value; }
    stats.mean /= finiteValues.size();

    if (finiteValues.size() > 1) {
        Double_t variance = 0.0;
        for (const auto value : finiteValues) {
            variance += pow(value - stats.mean, 2);
        }
        variance /= (finiteValues.size() - 1);
        stats.stdDev = sqrt(variance);
        stats.stdError = stats.stdDev / sqrt(static_cast<Double_t>(finiteValues.size()));
    }

    return stats;
}


// Simple function to calculate the yield given by two normalised OS and SS histograms
// Their angular spectra are subtracted (OS - SS) to reduce background
// and the full spectrum is integrated, though there is a posiblity to chose the integration range
// (if desired)
Double_t calculateOneYield(bool VERBOSE, TH1D *hDPhiOS, TH1D *hTrPtOS, TH1D *hDPhiSS, TH1D *hTrPtSS, const char* FLAVOUR, 
                           Int_t i, Int_t j, Int_t k, Int_t l) {

    (void)FLAVOUR;
    (void)i;
    (void)j;
    (void)k;
    (void)l;

    // Normalise by number of triggers
    if (VERBOSE) {
        std::cout << "hDPhiOS Integral: " << hDPhiOS->Integral() 
                  << ", hDPhiSS Integral: " << hDPhiSS->Integral() << std::endl;
    }
	hDPhiOS->Scale(1/hTrPtOS->Integral());
	hDPhiSS->Scale(1/hTrPtSS->Integral());
    if (VERBOSE) {
        std::cout << "hDPhiOS Integral: " << hDPhiOS->Integral() 
                  << ", hDPhiSS Integral: " << hDPhiSS->Integral() << std::endl;
    }
    TH1D *hCorr = (TH1D*)hDPhiOS->Clone();
    hCorr->Add(hDPhiSS, -1.);

    return hCorr->Integral();
} // calculateOneYield()


// Yields are calculated by looping over TUNES (e.g. MONASH),
// then ASSOCIATES (e.g. B-)
// and then DEPENDENCIES (e.g. DPhiLL)
// Function needs to be called for the FLAVOUR seperately (e.g. Beauty)
// The output is a 3D vector with the structure
// v[TUNE][ASSOCIATE][DEPENDENCY]
// TODO: change the .size() to variables nTUNES, etc. Like in the plotting function below
YieldsAndErrorsMap calculateYieldsVector(CONFIGS configs_from_json, const char* FLAVOUR) {

    std::cout << "*** Calculating yields for " << FLAVOUR << " ***" << std::endl;

    // Retrieve settings from configuration.json
    bool VERBOSE = configs_from_json.VERBOSE;
    bool CALCULATE_ERRORS = configs_from_json.CALCULATE_ERRORS;
    int nSubSamples = configs_from_json.nSubSamples;
    bool DRAW_CORRELATION_PLOTS = configs_from_json.DRAW_CORRELATION_PLOTS;
    std::string base_dir = configs_from_json.base_dir;
    std::vector<std::string> vTUNES = configs_from_json.vTUNES;
    std::string complete_root_dir;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { complete_root_dir = configs_from_json.bbBarDir; }
    if (strcmp(FLAVOUR, "CHARM")  == 0) { complete_root_dir = configs_from_json.ccBarDir; }
    std::string complete_root_dir_sub_samples;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { complete_root_dir_sub_samples = configs_from_json.bbBarDir_subSamples; }
    if (strcmp(FLAVOUR, "CHARM")  == 0) { complete_root_dir_sub_samples = configs_from_json.ccBarDir_subSamples; }
    std::vector<TriggerAssociateOSandSS> vTriggerAssociateOSandSS;
    std::map<std::string, std::vector<TriggerAssociateOSandSS>> histConfigs;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { vTriggerAssociateOSandSS = configs_from_json.vBeautyTriggerAssociateOSandSS; } //toremove
    if (strcmp(FLAVOUR, "CHARM")  == 0) { vTriggerAssociateOSandSS = configs_from_json.vCharmTriggerAssociateOSandSS; } //toremove
    if (strcmp(FLAVOUR, "BEAUTY")  == 0) { histConfigs = configs_from_json.beautyConfigs; }
    if (strcmp(FLAVOUR, "CHARM")  == 0) { histConfigs = configs_from_json.charmConfigs; }
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames = configs_from_json.vHistogramAndTriggerPtHistogramNames; // remove this line later (toremove)
    std::vector<BinsFromTHnSparse> vBinsFromTHnSparse = configs_from_json.vBinsFromTHnSparse;
    const Int_t nTUNES = static_cast<Int_t>(vTUNES.size());
    const Int_t nDependencies = static_cast<Int_t>(vBinsFromTHnSparse.size());

    // TODO: make these vectors into arrays, don't think vector is necessary
    // and the subYields are stored in an array anyways
    YieldsAndErrorsMap mapYieldsAndErrors;
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYields;
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYieldsErrors;
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYieldsRatioErrors;

    // TODO: make vTUNES.size into nTUNES, like in the plotting functions

    // Loop over TRIGGERS
    // Output is put back in a map with structure {trigger, {vYields}}
    // So that it is easy to find back the vYields with the corresponding trigger particle
    for (const auto& [trigger, configs] : histConfigs) {

        
        std::cout << "starting loop over " << trigger << std::endl;
        std::vector<TriggerAssociateOSandSS> vTriggerAssociateOSandSS = configs;
        // COMMENT: the subsampling will also be affected by these changes
        // I need to make sure things are propagated with Inaki's improvements to the subsampling
        // (based on older code)
        const Int_t nAssociates = static_cast<Int_t>(vTriggerAssociateOSandSS.size());
        std::vector<std::vector<std::vector<Double_t>>> vYields;
        std::vector<std::vector<std::vector<Double_t>>> vYieldsErrors;
        std::vector<std::vector<std::vector<Double_t>>> vYieldsRatioErrors;
        std::vector<std::vector<std::vector<std::vector<Double_t>>>> vSubYields(
            vTUNES.size(),
            std::vector<std::vector<std::vector<Double_t>>>(
                vTriggerAssociateOSandSS.size(),
                std::vector<std::vector<Double_t>>(
                    vBinsFromTHnSparse.size(),
                    std::vector<Double_t>(nSubSamples, 0.0)
                )
            )
        );


        // Loop over TUNES
        for (Int_t i=0; i<nTUNES; i++) {


            std::string TUNE = vTUNES[i];
            std::cout << "starting loop over " << TUNE << std::endl;
            std::cout << std::endl;


            // Loop over ASSOCIATES
            for (Int_t j=0; j<nAssociates; j++) {


                TriggerAssociateOSandSS fileNamesOSandSS = vTriggerAssociateOSandSS[j];
                std::cout << "starting loop over OS file: " << fileNamesOSandSS.OS << " and SS file: " << fileNamesOSandSS.SS << std::endl;
                const std::string osFilePath = ResolveCompleteRootFile(base_dir, TUNE, complete_root_dir, fileNamesOSandSS.OS);
                const std::string ssFilePath = ResolveCompleteRootFile(base_dir, TUNE, complete_root_dir, fileNamesOSandSS.SS);
                TFile *OStree = OpenRootFileOrThrow(osFilePath);
                TFile *SStree = OpenRootFileOrThrow(ssFilePath);
                std::cout << std::endl;

                // This is where we calculate the multiplicity
                TH1D *hSummedMultiplicity = GetObjectOrThrow<TH1D>(OStree, "summed MULTIPLICITY", osFilePath);
                Double_t fullIntegral = 0;
                fullIntegral = hSummedMultiplicity->Integral();
                std::set<double> requestedPercentiles;
                std::map<double,double> percentileToMultiplicity;

                for (const auto& bin : vBinsFromTHnSparse)
                {
                    requestedPercentiles.insert(bin.multiplicityMin);
                    requestedPercentiles.insert(bin.multiplicityMax);
                }

                for (double percentile : requestedPercentiles)
                {
                    percentileToMultiplicity[percentile] =
                        GetMultiplicityThreshold(
                            hSummedMultiplicity,
                            percentile
                        );
                }

                // Debug
                if (VERBOSE) {
                    for (const auto& [percentile, mult] : percentileToMultiplicity) {
                        std::cout
                        << percentile
                        << "% -> multiplicity "
                        << mult
                        << std::endl;
                    }
                }

                // Loop over DEPENDENCIES
                for (Int_t k=0; k<nDependencies; k++) {

                    BinsFromTHnSparse binFromTHnSparse = vBinsFromTHnSparse[k];
                    if (VERBOSE) {
                        std::cout
                            << "Analysing bin " << k
                            << " | TrPhi=[" << binFromTHnSparse.triggerPhiMin
                            << ", " << binFromTHnSparse.triggerPhiMax << "]"
                            << " | AssocPhi=[" << binFromTHnSparse.assocPhiMin
                            << ", " << binFromTHnSparse.assocPhiMax << "]"
                            << " | TrEta=[" << binFromTHnSparse.triggerEtaMin
                            << ", " << binFromTHnSparse.triggerEtaMax << "]"
                            << " | AssocEta=[" << binFromTHnSparse.assocEtaMin
                            << ", " << binFromTHnSparse.assocEtaMax << "]"
                            << " | TrPt=[" << binFromTHnSparse.triggerPtMin
                            << ", " << binFromTHnSparse.triggerPtMax << "]"
                            << " | AssocPt=[" << binFromTHnSparse.assocPtMin
                            << ", " << binFromTHnSparse.assocPtMax << "]"
                            << " | Mult%=[" << binFromTHnSparse.multiplicityMin
                            << ", " << binFromTHnSparse.multiplicityMax << "]"
                            << " | Mult=[" << percentileToMultiplicity[binFromTHnSparse.multiplicityMax]
                            << ", "<< percentileToMultiplicity[binFromTHnSparse.multiplicityMin] << "]"
                        << std::endl;
                        std::cout << std::endl;
                    }

                    // Add correct multiplicity cut to project out the relevant histograms from the THnSparse
                    BinsFromTHnSparse cuts;
                    cuts.triggerPtMin = binFromTHnSparse.triggerPtMin;
                    cuts.triggerPtMax = binFromTHnSparse.triggerPtMax;
                    cuts.assocPtMin = binFromTHnSparse.assocPtMin;
                    cuts.assocPtMax = binFromTHnSparse.assocPtMax;
                    // Definition of multiplicity is 'reversed' w.r.t. json
                    // The way below it cuts on [lower_multiplicity, higher_multiplicity]
                    // Which is what we want
                    cuts.multiplicityMin = percentileToMultiplicity[binFromTHnSparse.multiplicityMax];
                    cuts.multiplicityMax = percentileToMultiplicity[binFromTHnSparse.multiplicityMin];

                    // Retreive the histograms from the correlations THnSparse (Δφ, Δη, TrPt, AsPt, multiplicity)
                    // THnSparseD *hAsKinematics = (THnSparseD*)OStree->Get("hAsKinematics");
                    THnSparseD *hCorrelationsOS = GetObjectOrThrow<THnSparseD>(OStree, "hCorrelations", osFilePath);
                    THnSparseD *hCorrelationsSS = GetObjectOrThrow<THnSparseD>(SStree, "hCorrelations", ssFilePath);
                    THnSparseD *hTrKinematicsOS = GetObjectOrThrow<THnSparseD>(OStree, "hTrKinematics", osFilePath);
                    THnSparseD *hTrKinematicsSS = GetObjectOrThrow<THnSparseD>(SStree, "hTrKinematics", ssFilePath); // in principle the same as OS...

                    // Apply cuts to THnSparses
                    // Retreive the TH1 hDPhiOS/SS and hTrPtOS/SS objects as before
                    // Maybe add one element 'binLabel' to the BinsFromTHnSparse struct?
                    TH1D *hDPhiOS = GetCorrelationHistograms(hCorrelationsOS, cuts);
                    TH1D *hDPhiSS = GetCorrelationHistograms(hCorrelationsSS, cuts);
                    TH1D *hTrPtOS = GetTriggerPtHistograms(hTrKinematicsOS, cuts);
                    TH1D *hTrPtSS = GetTriggerPtHistograms(hTrKinematicsSS, cuts);

                    if (VERBOSE) {
                        std::cout << "hDPhiOS->GetEntries() = " << hDPhiOS->GetEntries() << std::endl;
                        std::cout << "hDPhiSS0>GetEntries() = " << hDPhiSS->GetEntries() << std::endl;
                    }

                    // Prevent double-counting
                    if (strcmp((fileNamesOSandSS.trigger).c_str(), 
                            (fileNamesOSandSS.associateSS).c_str()) == 0) { 
                        hDPhiSS->Scale(0.5); } 


                    // Calculate yield value and assign to appropriate place in vector
                    Double_t yield = calculateOneYield(VERBOSE, hDPhiOS, hTrPtOS, hDPhiSS, hTrPtSS, FLAVOUR, i, j, k, 0);
                    if (static_cast<std::size_t>(i) >= vYields.size()) { vYields.resize(i + 1); }
                    if (static_cast<std::size_t>(j) >= vYields[i].size()) { vYields[i].resize(j + 1); }
                    if (static_cast<std::size_t>(k) >= vYields[i][j].size()) { vYields[i][j].resize(k + 1); }
                    vYields[i][j][k] = yield; 
                    if (VERBOSE) { 
                        std::cout << "vYields[" << i << "][" << j << "][" << k << "] = " << vYields[i][j][k] << std::endl;
                        std::cout << std::endl;
                    }


                    // If requested: draw correlation plots
                    // This part is hard-coded for now, but could get its own configuration section in the json
                    // to customise what should be drawn and how already in the json
                    // TODO: this needs to be automised and configurable in the json as well
                    if (DRAW_CORRELATION_PLOTS) {
                        if (VERBOSE) {
                            TCanvas *c_correlations = new TCanvas (Form("%s c_correlations %s minus %s for [%f, %f]", TUNE.c_str(), fileNamesOSandSS.OS.c_str(), fileNamesOSandSS.SS.c_str(), binFromTHnSparse.multiplicityMin, binFromTHnSparse.multiplicityMax), Form("%s c_correlations %s minus %s for [%f, %f]", TUNE.c_str(), fileNamesOSandSS.OS.c_str(), fileNamesOSandSS.SS.c_str(), binFromTHnSparse.multiplicityMin, binFromTHnSparse.multiplicityMax), 800, 600);
                            c_correlations->cd();
                            hDPhiOS->SetTitle(Form("%s c_correlations %s minus %s for [%f, %f]", TUNE.c_str(), fileNamesOSandSS.OS.c_str(), fileNamesOSandSS.SS.c_str(), binFromTHnSparse.multiplicityMin, binFromTHnSparse.multiplicityMax));
                            hDPhiOS->Draw("PE");
                        }

                        // Hard-coded: we only want to show correlations for B+B- and D+D-
                        // TODO: put an option in the configuration.json to give a list of desired correlations to draw
                        if (TUNE == "MONASH" &&
                           (strcmp(fileNamesOSandSS.OS.c_str(), "BplusBminus.root") == 0 ||
                            strcmp(fileNamesOSandSS.OS.c_str(), "DplusDminus.root") == 0)) {
                                TCanvas *c_correlations_OS_SS = new TCanvas(Form("c_correlations_OS_SS %s for [%f, %f]", fileNamesOSandSS.OS.c_str(), binFromTHnSparse.multiplicityMin, binFromTHnSparse.multiplicityMax), Form("c_correlations_OS_SS %s for [%f, %f]", fileNamesOSandSS.OS.c_str(), binFromTHnSparse.multiplicityMin, binFromTHnSparse.multiplicityMax), 800, 600);
                                TPad *cMiniPadOS = createMiniPad("cMiniPadOS", 0.00, 0.00, 0.50, 1.00);
                                TPad *cMiniPadOSSS = createMiniPad("cMiniPadSS", 0.50, 0.00, 1.00, 1.00);
                                TH1D *hTemplateOS = (TH1D*)hDPhiOS->Clone("hTemplateOS");
                                TH1D *hTemplateOSSS = (TH1D*)hDPhiSS->Clone("hTemplateOSSS");

                                cMiniPadOS->cd();
                                hTemplateOS->SetStats(0);
                                hTemplateOS->SetTitle(Form("OS: %s%s", fileNamesOSandSS.trigger.c_str(), fileNamesOSandSS.associateOS.c_str()));
                                hTemplateOS->GetXaxis()->SetTitle(hDPhiOS->GetXaxis()->GetTitle());
                                hTemplateOS->GetYaxis()->SetTitle(hDPhiOS->GetYaxis()->GetTitle());
                                hTemplateOS->GetYaxis()->SetRangeUser(0.,1.2*hDPhiOS->GetMaximum());
                                if (strcmp(fileNamesOSandSS.OS.c_str(), "BplusBminus.root") == 0) { hDPhiOS->SetLineColor(kRed); }
                                if (strcmp(fileNamesOSandSS.OS.c_str(), "DplusDminus.root") == 0) { hDPhiOS->SetLineColor(kBlue); }
                                hTemplateOS->Draw("PE");
                                hDPhiOS->Draw("PE SAME");

                                cMiniPadOSSS->cd();
                                hTemplateOSSS->SetStats(0);
                                hTemplateOSSS->SetTitle(Form("SS: %s%s", fileNamesOSandSS.trigger.c_str(), fileNamesOSandSS.associateSS.c_str()));
                                hTemplateOSSS->GetXaxis()->SetTitle(hDPhiOS->GetXaxis()->GetTitle());
                                hTemplateOSSS->GetYaxis()->SetTitle(hDPhiOS->GetYaxis()->GetTitle());
                                Double_t ymin = 0;
                                if (hDPhiSS->GetMinimum() != 0) { ymin = 0.1*std::min(hDPhiOS->GetMinimum(), hDPhiSS->GetMinimum()); }
                                else { ymin = 0.1*std::min(hDPhiOS->GetMinimum(), hDPhiSS->GetMinimum())+1e-6; }
                                
                                Double_t ymax = 10*std::max(hDPhiOS->GetMaximum(), hDPhiSS->GetMaximum());
                                hTemplateOSSS->GetYaxis()->SetRangeUser(ymin, ymax);
                                gPad->SetLogy();
                                if (strcmp(fileNamesOSandSS.OS.c_str(), "BplusBminus.root") == 0) { hDPhiSS->SetLineColor(kRed); }
                                if (strcmp(fileNamesOSandSS.OS.c_str(), "DplusDminus.root") == 0) { hDPhiSS->SetLineColor(kBlue); }
                                // hDPhiOS->SetLineStyle(1);
                                hDPhiSS->SetLineStyle(2);

                                hTemplateOSSS->Draw("PE");
                                hDPhiOS->Draw("PE SAME");
                                hDPhiSS->Draw("PE SAME");

                                TLegend *leg = new TLegend(0.60,0.75,0.88,0.88);
                                leg->SetBorderSize(0);
                                leg->SetFillStyle(0);
                                leg->AddEntry((TObject*)0,
                                Form("%.1f #leq N_{ch} percentile #leq %.1f", binFromTHnSparse.multiplicityMin, binFromTHnSparse.multiplicityMax), "");
                                leg->AddEntry(hDPhiOS,"OS","lep");
                                leg->AddEntry(hDPhiSS,"SS","lep");
                                leg->Draw();

                                c_correlations_OS_SS->cd();
                                const std::string correlationPlotDir = ResolvePathFromBase("PlottingScripts/Plots/THnSparse/Correlations", FindHadronizationBase());
                                writeCanvasToFiles(VERBOSE, c_correlations_OS_SS, correlationPlotDir, Form("c_correlations_OS_SS %s for [%f, %f]", fileNamesOSandSS.OS.c_str(), binFromTHnSparse.multiplicityMin, binFromTHnSparse.multiplicityMax));
                        }
                    }


                    // Calculate the error on the yield by subsampling with N samples
                    // Not the most efficient way, but it is straightforward and clear
                    // and anyways the files are quite small so it doesn't take too long
                    if (CALCULATE_ERRORS) {
                        std::vector<Double_t> subYieldValues;
                        std::vector<Double_t> subRatioValues;
                        subYieldValues.reserve(nSubSamples);
                        subRatioValues.reserve(nSubSamples);


                        for (Int_t l = 1; l < nSubSamples+1; l++) {


                            const std::string osSubSamplePath = ResolveSubSampleRootFile(complete_root_dir_sub_samples, TUNE, l, fileNamesOSandSS.OS);
                            const std::string ssSubSamplePath = ResolveSubSampleRootFile(complete_root_dir_sub_samples, TUNE, l, fileNamesOSandSS.SS);
                            TFile *OStree_subSamples = OpenRootFileOrThrow(osSubSamplePath);
                            TFile *SStree_subSamples = OpenRootFileOrThrow(ssSubSamplePath);

                            // Retreive the histograms from the correlations THnSparse (Δφ, Δη, TrPt, AsPt, multiplicity)
                            // THnSparseD *hAsKinematics = (THnSparseD*)OStree->Get("hAsKinematics");
                            THnSparseD *hCorrelationsOS_subSamples = GetObjectOrThrow<THnSparseD>(OStree_subSamples, "hCorrelations", osSubSamplePath);
                            THnSparseD *hCorrelationsSS_subSamples = GetObjectOrThrow<THnSparseD>(SStree_subSamples, "hCorrelations", ssSubSamplePath);
                            THnSparseD *hTrKinematicsOS_subSamples = GetObjectOrThrow<THnSparseD>(OStree_subSamples, "hTrKinematics", osSubSamplePath);
                            THnSparseD *hTrKinematicsSS_subSamples = GetObjectOrThrow<THnSparseD>(SStree_subSamples, "hTrKinematics", ssSubSamplePath); // in principle the same as OS...

                            // Apply cuts to THnSparses
                            // Retreive the TH1 hDPhiOS/SS and hTrPtOS/SS objects as before
                            // Maybe add one element 'binLabel' to the BinsFromTHnSparse struct?
                            TH1D *hDPhiOS_subSamples = GetCorrelationHistograms(hCorrelationsOS_subSamples, cuts);
                            TH1D *hDPhiSS_subSamples = GetCorrelationHistograms(hCorrelationsSS_subSamples, cuts);
                            TH1D *hTrPtOS_subSamples = GetTriggerPtHistograms(hTrKinematicsOS_subSamples, cuts);
                            TH1D *hTrPtSS_subSamples = GetTriggerPtHistograms(hTrKinematicsSS_subSamples, cuts);

                            // Apply the same same-sign double-counting correction used for the central yield.
                            if (strcmp((fileNamesOSandSS.trigger).c_str(),
                                       (fileNamesOSandSS.associateSS).c_str()) == 0) {
                                hDPhiSS_subSamples->Scale(0.5);
                            }

                            // TODO: when subsampling ok, remove this part
                            // HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
                            /* LEGACY CODE
                                TH1D *hDPhiOS_subSamples = (TH1D*)OStree_subSamples->Get((hDPhiAndhTrPtNames.hDPhi).c_str());
                                TH1D *hDPhiSS_subSamples = (TH1D*)SStree_subSamples->Get((hDPhiAndhTrPtNames.hDPhi).c_str());
                                TH1D *hTrPtOS_subSamples = (TH1D*)OStree_subSamples->Get((hDPhiAndhTrPtNames.hTrPt).c_str());
                                TH1D *hTrPtSS_subSamples = (TH1D*)SStree_subSamples->Get((hDPhiAndhTrPtNames.hTrPt).c_str());
                            LEGACY CODE */ 

                            Double_t subYield = calculateOneYield(VERBOSE, hDPhiOS_subSamples, hTrPtOS_subSamples, hDPhiSS_subSamples, hTrPtSS_subSamples,
                                                                FLAVOUR, i, j, k, l);
                            vSubYields[i][j][k][l - 1] = subYield;
                            if (VERBOSE) {
                                std::cout << "vSubYields[" << i << "][" << j << "][" << k << "][" << (l - 1) << "] = " << subYield << std::endl;
                                std::cout << std::endl;
                            }

                            subYieldValues.push_back(subYield);
                            subRatioValues.push_back(safeRatio(vSubYields[i][j][k][l - 1], vSubYields[i][0][k][l - 1]));

                            // Free memory
                            OStree_subSamples->Close();
                            SStree_subSamples->Close();
                            // TODO: Close and delete more things? Memory issuse?
                            // Seems to automatically close histograms too?


                        } // Loop over SUBSAMPLES


                        const SubsampleStatistics yieldStats = calculateSubsampleStatistics(subYieldValues);
                        const SubsampleStatistics yieldRatioStats = calculateSubsampleStatistics(subRatioValues);
                        Double_t yieldError = yieldStats.stdError;
                        Double_t yieldRatioError = yieldRatioStats.stdError;
                        if (VERBOSE) {
                            std::cout << "subsample yield stats n=" << yieldStats.nValues
                                      << " mean=" << yieldStats.mean
                                      << " stdDev=" << yieldStats.stdDev
                                      << " stdError=" << yieldStats.stdError << std::endl;
                            std::cout << "subsample ratio stats n=" << yieldRatioStats.nValues
                                      << " mean=" << yieldRatioStats.mean
                                      << " stdDev=" << yieldRatioStats.stdDev
                                      << " stdError=" << yieldRatioStats.stdError << std::endl;
                            std::cout << std::endl;
                        }
                        if (static_cast<std::size_t>(i) >= vYieldsErrors.size()) { vYieldsErrors.resize(i + 1); }
                        if (static_cast<std::size_t>(j) >= vYieldsErrors[i].size()) { vYieldsErrors[i].resize(j + 1); }
                        if (static_cast<std::size_t>(k) >= vYieldsErrors[i][j].size()) { vYieldsErrors[i][j].resize(k + 1); }
                        vYieldsErrors[i][j][k] = yieldError; 
                        if (VERBOSE) {
                            std::cout << "vYieldsErrors[" << i << "][" << j << "][" << k << "] = " << vYieldsErrors[i][j][k] << std::endl;
                            std::cout << std::endl;
                        }
                        if (static_cast<std::size_t>(i) >= vYieldsRatioErrors.size()) { vYieldsRatioErrors.resize(i + 1); }
                        if (static_cast<std::size_t>(j) >= vYieldsRatioErrors[i].size()) { vYieldsRatioErrors[i].resize(j + 1); }
                        if (static_cast<std::size_t>(k) >= vYieldsRatioErrors[i][j].size()) { vYieldsRatioErrors[i][j].resize(k + 1); }
                        vYieldsRatioErrors[i][j][k] = yieldRatioError; 
                        if (VERBOSE) {
                            std::cout << "vYieldsRatioErrors[" << i << "][" << j << "][" << k << "] = " << vYieldsRatioErrors[i][j][k] << std::endl;
                            std::cout << std::endl;
                        }


                    } // calculate errors


                } // Loop over DEPENDENCIES


                // TODO: cannot seem to draw 'test' plots for the yields anymore when this is enabled?
                // Free memory
                // OStree->Close();
                // SStree->Close();


            } // Loop over ASSOCIATES


        } // Loop over TUNES


        // Store the {trigger, vYields} objects in the map
        std::cout << "storing trigger " << trigger << " in yields map" << std::endl;
        mapYields[trigger] = std::move(vYields);
        mapYieldsErrors[trigger] = std::move(vYieldsErrors);
        mapYieldsRatioErrors[trigger] = std::move(vYieldsRatioErrors);

        // Retreive the vYields for this trigger
        mapYieldsAndErrors.mapYields = mapYields;
        if (CALCULATE_ERRORS) { mapYieldsAndErrors.mapYieldsErrors = mapYieldsErrors; }
        if (CALCULATE_ERRORS) { mapYieldsAndErrors.mapYieldsRatioErrors = mapYieldsRatioErrors; }


    } // Loop over TRIGGERS


    // TODO: make the names better
    // legacy, toremove
    /*
    YieldsAndErrors vYieldsAndErrors;
    vYieldsAndErrors.vYields = vYields;
    if (CALCULATE_ERRORS) { vYieldsAndErrors.vYieldsErrors = vYieldsErrors; }
    if (CALCULATE_ERRORS) { vYieldsAndErrors.vYieldsRatioErrors = vYieldsRatioErrors; }
    */
    
    return mapYieldsAndErrors;


} // calculateYieldsVector()


TPad* drawBalancingPlots(CONFIGS configs_from_json, const char* FLAVOUR, YieldsAndErrorsMap mapYieldsAndErrors) {


    std::cout << "*** Drawing balancing plots for " << FLAVOUR << " ***" << std::endl;


    // TODO: add checks for when things are == -1 or invalid. Give error message
    // Retrieve settings from configuration.json
    canvasConfigs canvasConfigs = configs_from_json.currentCanvasConfigs;
    bool VERBOSE = configs_from_json.VERBOSE;
    bool CALCULATE_ERRORS = configs_from_json.CALCULATE_ERRORS;
    std::string base_dir = configs_from_json.base_dir;
    std::vector<std::string> vTUNES = configs_from_json.vTUNES;
    std::vector<std::string> vCanvasTUNES = canvasConfigs.vCanvasTUNES;
    std::vector<TriggerAssociateOSandSS> vTriggerAssociateOSandSS;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { vTriggerAssociateOSandSS = configs_from_json.beautyConfigs.at(canvasConfigs.TriggerToUse); }
    if (strcmp(FLAVOUR, "CHARM") ==  0) { vTriggerAssociateOSandSS = configs_from_json.charmConfigs.at(canvasConfigs.TriggerToUse); }
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames = configs_from_json.vHistogramAndTriggerPtHistogramNames;
    std::vector<BinsFromTHnSparse> vBinsFromTHnSparse = configs_from_json.vBinsFromTHnSparse;

    // Function that transforms the map storing trigger and vYieldsAndErrors into just vYieldsAndErrors
    auto vYieldsAndErrors = YieldsAndErrorsForGivenTrigger(canvasConfigs.TriggerToUse, mapYieldsAndErrors, CALCULATE_ERRORS);

    Int_t nTUNES = vTUNES.size();
    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    // Int_t nDependencies = vHistogramAndTriggerPtHistogramNames.size();
    Int_t nDependencies = vBinsFromTHnSparse.size();

    // Values will be drawn from a 2D vector of TH1D with number of ASSOCIATES bins
    // This way the TUNE and DEPENDENCY can be looped over, while the data points will be the ASSOCIATES
    TH1D *vHists[nTUNES][nDependencies];
    if (VERBOSE) {
        std::cout << "number of associates: " << nAssociates << std::endl;
        std::cout << std::endl;
    }

    // Define a template for this plot to set titles, stats, etc.
    TH1D *hYieldsTemplate = new TH1D(Form("hYieldsTemplate_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("hYieldsTemplate_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), nAssociates, 0, nAssociates);
    hYieldsTemplate->SetTitle(canvasConfigs.canvasTitle.c_str());
    hYieldsTemplate->GetXaxis()->SetTitle(canvasConfigs.xAxisTitle.c_str());
    hYieldsTemplate->GetYaxis()->SetTitle(canvasConfigs.yAxisTitle.c_str());
    std::cout << "- Setting y-axis range: (" << canvasConfigs.yMinAxis << "," << canvasConfigs.yMaxAxis << ")" << std::endl;
    hYieldsTemplate->GetYaxis()->SetRangeUser(canvasConfigs.yMinAxis,canvasConfigs.yMaxAxis);

    TCanvas *cYields = new TCanvas(Form("cYields_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("cYields_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), canvasConfigs.xSizeCanvas, canvasConfigs.ySizeCanvas);
    cYields->cd();
    if (canvasConfigs.setLogy) { gPad->SetLogy(); }
    hYieldsTemplate->SetStats(0);
    hYieldsTemplate->Draw("PE");

    // Draw mini pad for global canvas (only used if asked in configurations)
    TPad* cMiniPad;
    if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
        std::cout << "- Creating mini pad with dimensions x1(" << canvasConfigs.xMinPad << "," << canvasConfigs.yMinPad << ") and x2(" << canvasConfigs.xMaxPad << "," << canvasConfigs.yMaxPad << ")" << std::endl;
        cMiniPad = new TPad(Form("cMiniPad_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("cMiniPad_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), canvasConfigs.xMinPad, canvasConfigs.yMinPad, canvasConfigs.xMaxPad, canvasConfigs.yMaxPad);
        cMiniPad->SetTickx(1);
        cMiniPad->SetTicky(1);
        if (canvasConfigs.topMarginPad != -1 && canvasConfigs.bottomMarginPad != -1 && canvasConfigs.leftMarginPad != -1 && canvasConfigs.rightMarginPad != -1) {
            std::cout << "- Setting mini pad margins to " << canvasConfigs.topMarginPad << " (top), " << canvasConfigs.bottomMarginPad << " (bottom), " << canvasConfigs.leftMarginPad << " (left), " << canvasConfigs.rightMarginPad << " (right)" << std::endl;
            cMiniPad->SetTopMargin(canvasConfigs.topMarginPad);
            cMiniPad->SetBottomMargin(canvasConfigs.bottomMarginPad);
            cMiniPad->SetLeftMargin(canvasConfigs.leftMarginPad);
            cMiniPad->SetRightMargin(canvasConfigs.rightMarginPad);
        }
        cMiniPad->cd();
        if (canvasConfigs.setLogy) { gPad->SetLogy(); }
        hYieldsTemplate->SetStats(0);
        hYieldsTemplate->Draw("PE");
    }

    std::map<std::string, Int_t> colourTUNEMap = canvasConfigs.colourTUNEMap;
    std::map<std::string, Int_t> lineStyleDependencyMap = canvasConfigs.lineStyleDependencyMap;

    TLegend *legend;
    std::map<std::string, std::string> legendEntriesMap = canvasConfigs.legendEntriesMap;
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        std::cout << "- Creating legend at positions x1(" << canvasConfigs.xMinLegend << "," << canvasConfigs.yMinLegend << ") and x2(" << canvasConfigs.xMaxLegend << "," << canvasConfigs.yMaxLegend << ")" << std::endl;
        legend = new TLegend(canvasConfigs.xMinLegend, canvasConfigs.yMinLegend, canvasConfigs.xMaxLegend, canvasConfigs.yMaxLegend);
    } else { std::cout << "- NOTE: Not drawing legend for this plot" << std::endl; }

    // Guarantee the legend entries are only drawn once
    std::set<std::string> alreadyInLegend;

    // Optional: define hard coded settings below
    if (canvasConfigs.useHardCodedSettings) {
        if (isCanvasNameEqualTo(canvasConfigs.canvasName, "canvas_name")) {
            std::cout << "- WARNING: using hard-coded settings for this canvas" << std::endl;
            std::cout << std::endl;
        }
    }


    // Loop over TUNES
    for (Int_t i=0; i<nTUNES; i++) {


        // Make sure we want to draw the given tune
        std::string TUNE = vTUNES[i];
        if (!isInVector(TUNE, vCanvasTUNES)) { continue; }
        if (VERBOSE) {
            std::cout << "starting loop over " << TUNE << std::endl;
            std::cout << std::endl;
        }


        // Loop over ASSOCIATES
        for (Int_t j=0; j<nAssociates; j++) {


            // TODO: fix this bug with associateName and formatting....
            TriggerAssociateOSandSS fileNamesOSandSS = vTriggerAssociateOSandSS[j];
            std::string associateName = fileNamesOSandSS.associateOS;
            if (VERBOSE) {
                std::cout << "starting loop over associate: " << associateName << std::endl;
                std::cout << "starting loop over OS file: " << fileNamesOSandSS.OS << " and SS file: " << fileNamesOSandSS.SS << std::endl;
                std::cout << std::endl;
            }

            if (i==0) { // only set the template histogram once
                // Define associate label names for yield plots
                hYieldsTemplate->GetXaxis()->SetBinLabel(1+j, associateName.c_str());
            }

            // Loop over DEPENDENCIES
            for (Int_t k=0; k<nDependencies; k++) {


                // HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
                BinsFromTHnSparse binFromTHnSparse = vBinsFromTHnSparse[k];
                if (VERBOSE) {
                    std::cout << "plotting histogram " << binFromTHnSparse.hDPhi << " with trigger pT histogram " << binFromTHnSparse.hTrPt << std::endl;
                    std::cout << std::endl;
                }

                vHists[i][k] = new TH1D(Form("hYields_%s_%i_%i_%i_%s", FLAVOUR, i, j, k, (canvasConfigs.canvasName).c_str()), Form("hYields_%s_%i_%i_%i_%s", FLAVOUR, i, j, k, (canvasConfigs.canvasName).c_str()), nAssociates, 0, nAssociates);
                vHists[i][k]->SetBinContent(1+j, vYieldsAndErrors.vYields[i][j][k]);
                if (CALCULATE_ERRORS) { 
                    vHists[i][k]->SetBinError(1+j, vYieldsAndErrors.vYieldsErrors[i][j][k]);
                }
                else {
                    vHists[i][k]->SetBinError(1+j, 1e-10);
                }
                ApplyTuneVisualStyle(vHists[i][k], TUNE);
                cYields->cd();
                vHists[i][k]->Draw("same PE");
                if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                    cMiniPad->cd();
                    vHists[i][k]->Draw("same PE");
                }

                if (colourTUNEMap.find(TUNE) != colourTUNEMap.end()) {
                    Int_t colour = colourTUNEMap[TUNE];
                    vHists[i][k]->SetLineColor(colour);
                    vHists[i][k]->SetMarkerColor(colour);
                    if (VERBOSE) { std::cout << "Found colour: " << colour << std::endl; }
                } else {
                    if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                }

                if (lineStyleDependencyMap.find(binFromTHnSparse.hDPhi) != lineStyleDependencyMap.end()) {
                    Int_t lineStyle = lineStyleDependencyMap[binFromTHnSparse.hDPhi];
                    vHists[i][k]->SetLineStyle(lineStyle);
                    if (VERBOSE) { std::cout << "Found lineStyle: " << lineStyle << std::endl; }
                } else {
                    if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                }

                // TODO: move this outside loop (also for the other ones below)
                // Draw legend
                if (legend != nullptr && alreadyInLegend.find(binFromTHnSparse.hDPhi) == alreadyInLegend.end()) {
                    if (legendEntriesMap.find(binFromTHnSparse.hDPhi) != legendEntriesMap.end()) {
                        std::string displayName = legendEntriesMap[binFromTHnSparse.hDPhi];
                        if (VERBOSE) { std::cout << "Found displayName: " << displayName << std::endl; }
                        legend->AddEntry(vHists[i][k], displayName.c_str(), "lep");
                    } else {
                        if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                    }
                    alreadyInLegend.insert(binFromTHnSparse.hDPhi);
                }

                if (VERBOSE) { std::cout << std::endl; }


            } // Loop over DEPENDENCIES


        } // Loop over ASSOCIATES


    } // Loop over TUNES


    // TODO: change cYields and stuff to just 'canvas'
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        cYields->cd();
        legend->Draw();
        if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
            cMiniPad->cd();
            legend->Draw();
        }
    }

    if (canvasConfigs.write) { 
        writeCanvasToFiles(VERBOSE, cYields, canvasConfigs.writePath, canvasConfigs.writeName); 
    }


    return cMiniPad;


} // drawBalancingPlots()


TPad* drawBalancingPlotsTUNERatios(CONFIGS configs_from_json, const char* FLAVOUR, YieldsAndErrorsMap mapYieldsAndErrors,
                                  Int_t indexNominatorTUNE, Int_t indexDenominatorTUNE) {


    std::cout << "*** Drawing balancing plots with TUNE ratios for " << FLAVOUR;


    // Retrieve settings from configuration.json
    canvasConfigs canvasConfigs = configs_from_json.currentCanvasConfigs;
    bool VERBOSE = configs_from_json.VERBOSE;
    bool CALCULATE_ERRORS = configs_from_json.CALCULATE_ERRORS;
    std::string base_dir = configs_from_json.base_dir;
    std::vector<std::string> vTUNES = configs_from_json.vTUNES; // TODO: put the name of the tune in output for clarity?
    std::vector<TriggerAssociateOSandSS> vTriggerAssociateOSandSS;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { vTriggerAssociateOSandSS = configs_from_json.beautyConfigs.at(canvasConfigs.TriggerToUse); }
    if (strcmp(FLAVOUR, "CHARM") ==  0) { vTriggerAssociateOSandSS = configs_from_json.charmConfigs.at(canvasConfigs.TriggerToUse); }
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames = configs_from_json.vHistogramAndTriggerPtHistogramNames;
    std::vector<BinsFromTHnSparse> vBinsFromTHnSparse = configs_from_json.vBinsFromTHnSparse;

    std::cout << " and TUNE = " << vTUNES[indexNominatorTUNE] << "/" << vTUNES[indexDenominatorTUNE] << " ***" << std::endl;

    // Function that transforms the map storing trigger and vYieldsAndErrors into just vYieldsAndErrors
    auto vYieldsAndErrors = YieldsAndErrorsForGivenTrigger(canvasConfigs.TriggerToUse, mapYieldsAndErrors, CALCULATE_ERRORS);

    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    // Int_t nDependencies = vHistogramAndTriggerPtHistogramNames.size();
    Int_t nDependencies = vBinsFromTHnSparse.size();

    // Values will be drawn from a 2D vector of TH1D with number of ASSOCIATES bins
    // This way the TUNE and DEPENDENCY can be looped over, while the data points will be the ASSOCIATES
    TH1D *vHists[nDependencies];
    if (VERBOSE) {
        std::cout << "number of associates: " << nAssociates << std::endl;
        std::cout << std::endl;
    }

    // Define a template for this plot to set titles, stats, etc.
    TH1D *hYieldsTemplate = new TH1D(Form("hYieldsTUNERatiosTemplate_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("hYieldsTUNERatiosTemplate_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), nAssociates, 0, nAssociates);
    hYieldsTemplate->SetTitle(canvasConfigs.canvasTitle.c_str());
    hYieldsTemplate->GetXaxis()->SetTitle(canvasConfigs.xAxisTitle.c_str());
    hYieldsTemplate->GetYaxis()->SetTitle(canvasConfigs.yAxisTitle.c_str());
    std::cout << "- Setting y-axis range: (" << canvasConfigs.yMinAxis << "," << canvasConfigs.yMaxAxis << ")" << std::endl;
    hYieldsTemplate->GetYaxis()->SetRangeUser(canvasConfigs.yMinAxis,canvasConfigs.yMaxAxis);

    TCanvas *cYields = new TCanvas(Form("cYieldsTUNERatios_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("cYieldsTUNERatios_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), canvasConfigs.xSizeCanvas, canvasConfigs.ySizeCanvas);
    cYields->cd();
    if (canvasConfigs.setLogy) { gPad->SetLogy(); }
    hYieldsTemplate->SetStats(0);
    hYieldsTemplate->Draw("PE");

    // Draw mini pad for global canvas (only used if asked in configurations)
    TPad* cMiniPad;
    if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
        std::cout << "- Creating mini pad with dimensions x1(" << canvasConfigs.xMinPad << "," << canvasConfigs.yMinPad << ") and x2(" << canvasConfigs.xMaxPad << "," << canvasConfigs.yMaxPad << ")" << std::endl;
        cMiniPad = new TPad(Form("cMiniPad_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("cMiniPad_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), canvasConfigs.xMinPad, canvasConfigs.yMinPad, canvasConfigs.xMaxPad, canvasConfigs.yMaxPad);
        cMiniPad->SetTickx(1);
        cMiniPad->SetTicky(1);
        if (canvasConfigs.topMarginPad != -1 && canvasConfigs.bottomMarginPad != -1 && canvasConfigs.leftMarginPad != -1 && canvasConfigs.rightMarginPad != -1) {
            std::cout << "- Setting mini pad margins to " << canvasConfigs.topMarginPad << " (top), " << canvasConfigs.bottomMarginPad << " (bottom), " << canvasConfigs.leftMarginPad << " (left), " << canvasConfigs.rightMarginPad << " (right)" << std::endl;
            cMiniPad->SetTopMargin(canvasConfigs.topMarginPad);
            cMiniPad->SetBottomMargin(canvasConfigs.bottomMarginPad);
            cMiniPad->SetLeftMargin(canvasConfigs.leftMarginPad);
            cMiniPad->SetRightMargin(canvasConfigs.rightMarginPad);
        }
        cMiniPad->cd();
        if (canvasConfigs.setLogy) { gPad->SetLogy(); }
        hYieldsTemplate->SetStats(0);
        hYieldsTemplate->Draw("PE");
    }

    std::map<std::string, Int_t> colourTUNEMap = canvasConfigs.colourTUNEMap;
    std::map<std::string, Int_t> lineStyleDependencyMap = canvasConfigs.lineStyleDependencyMap;

    TLegend *legend = nullptr;
    std::map<std::string, std::string> legendEntriesMap = canvasConfigs.legendEntriesMap;
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        std::cout << "- Creating legend at positions x1(" << canvasConfigs.xMinLegend << "," << canvasConfigs.yMinLegend << ") and x2(" << canvasConfigs.xMaxLegend << "," << canvasConfigs.yMaxLegend << ")" << std::endl;
        legend = new TLegend(canvasConfigs.xMinLegend, canvasConfigs.yMinLegend, canvasConfigs.xMaxLegend, canvasConfigs.yMaxLegend);
    } else { std::cout << "- NOTE: Not drawing legend for this plot" << std::endl; }

    // Guarantee the legend entries are only drawn once
    std::set<std::string> alreadyInLegend;

    // Optional: define hard coded settings below
    if (canvasConfigs.useHardCodedSettings) {
        if (isCanvasNameEqualTo(canvasConfigs.canvasName, "canvas_name")) {
            std::cout << "- WARNING: using hard-coded settings for this canvas" << std::endl;
            std::cout << std::endl;
        }
    }


    // Loop over ASSOCIATES
    for (Int_t j=0; j<nAssociates; j++) {


        // TODO: fix this bug with associateName and formatting....
        TriggerAssociateOSandSS fileNamesOSandSS = vTriggerAssociateOSandSS[j];
        std::string associateName = fileNamesOSandSS.associateOS;
        if (VERBOSE) {
            std::cout << "starting loop over associate: " << associateName << std::endl;
            std::cout << "starting loop over OS file: " << fileNamesOSandSS.OS << " and SS file: " << fileNamesOSandSS.SS << std::endl;
            std::cout << std::endl;
        }
        // Define associate label names for yield plots
        hYieldsTemplate->GetXaxis()->SetBinLabel(1+j, associateName.c_str());


        // Loop over DEPENDENCIES
        for (Int_t k=0; k<nDependencies; k++) {


            // HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
            BinsFromTHnSparse binFromTHnSparse = vBinsFromTHnSparse[k];
            // TODO: verbose
            if (VERBOSE) { 
                std::cout << "plotting histogram " << binFromTHnSparse.hDPhi << " with trigger pT histogram " << binFromTHnSparse.hTrPt << std::endl;
                std::cout << std::endl;
            }

            vHists[k] = new TH1D(Form("hYields_%s_%i_%i_%s", FLAVOUR, j, k, (canvasConfigs.canvasName).c_str()), Form("hYields_%s_%i_%i_%s", FLAVOUR, j, k, (canvasConfigs.canvasName).c_str()), nAssociates, 0, nAssociates);
            vHists[k]->SetBinContent(1+j, vYieldsAndErrors.vYields[indexNominatorTUNE][j][k]/vYieldsAndErrors.vYields[indexDenominatorTUNE][j][k]);
            if (CALCULATE_ERRORS) { 
                // TODO: implement ratio error in yield code
                // vHists[k]->SetBinError(1+j, vYieldsAndErrors.vYieldsErrors[i][j][k]);
                vHists[k]->SetBinError(1+j, propagateRatioError(vYieldsAndErrors.vYields[indexNominatorTUNE][j][k], 
                                                                vYieldsAndErrors.vYields[indexDenominatorTUNE][j][k],
                                                                vYieldsAndErrors.vYieldsErrors[indexNominatorTUNE][j][k],
                                                                vYieldsAndErrors.vYieldsErrors[indexDenominatorTUNE][j][k]));
            }
            else {
                vHists[k]->SetBinError(1+j, 1e-10);
            }
            ApplyTuneVisualStyle(vHists[k], vTUNES[indexNominatorTUNE]);
            cYields->cd();
            vHists[k]->Draw("same PE");
            if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                cMiniPad->cd();
                vHists[k]->Draw("same PE");
            }

            if (lineStyleDependencyMap.find(binFromTHnSparse.hDPhi) != lineStyleDependencyMap.end()) {
                Int_t lineStyle = lineStyleDependencyMap[binFromTHnSparse.hDPhi];
                vHists[k]->SetLineStyle(lineStyle);
                if (VERBOSE) { std::cout << "Found lineStyle: " << lineStyle << std::endl; }
            } else {
                if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
            }

            // Draw legend
            if (legend != nullptr && alreadyInLegend.find(binFromTHnSparse.hDPhi) == alreadyInLegend.end()) {
                if (legendEntriesMap.find(binFromTHnSparse.hDPhi) != legendEntriesMap.end()) {
                    std::string displayName = legendEntriesMap[binFromTHnSparse.hDPhi];
                    if (VERBOSE) { std::cout << "Found displayName: " << displayName << std::endl; }
                    legend->AddEntry(vHists[k], displayName.c_str(), "lep");
                } else {
                    if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                }
                alreadyInLegend.insert(binFromTHnSparse.hDPhi);
            }

            if (VERBOSE) { std::cout << std::endl; }


        } // Loop over DEPENDENCIES


    } // Loop over ASSOCIATES


    // TODO: change cYields and stuff to just 'canvas'
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        cYields->cd();
        legend->Draw();
        if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
            cMiniPad->cd();
            legend->Draw();
        }
    }

    if (canvasConfigs.write) { 
        writeCanvasToFiles(VERBOSE, cYields, canvasConfigs.writePath, canvasConfigs.writeName); 
    }


    return cMiniPad;


} // drawBalancingPlotsTUNERatios()


TPad* drawBalancingBaryonMesonRatioPlots(CONFIGS configs_from_json, const char* FLAVOUR, YieldsAndErrorsMap mapYieldsAndErrors) {


    std::cout << "*** Drawing balancing baryon/meson ratio plots for " << FLAVOUR << " ***" << std::endl;


    // Retrieve settings from configuration.json
    canvasConfigs canvasConfigs = configs_from_json.currentCanvasConfigs;
    bool VERBOSE = configs_from_json.VERBOSE;
    bool CALCULATE_ERRORS = configs_from_json.CALCULATE_ERRORS;
    std::string base_dir = configs_from_json.base_dir;
    std::vector<std::string> vTUNES = configs_from_json.vTUNES;
    std::vector<TriggerAssociateOSandSS> vTriggerAssociateOSandSS;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { vTriggerAssociateOSandSS = configs_from_json.beautyConfigs.at(canvasConfigs.TriggerToUse); }
    if (strcmp(FLAVOUR, "CHARM") ==  0) { vTriggerAssociateOSandSS = configs_from_json.charmConfigs.at(canvasConfigs.TriggerToUse); }
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames = configs_from_json.vHistogramAndTriggerPtHistogramNames;
    std::vector<BinsFromTHnSparse> vBinsFromTHnSparse = configs_from_json.vBinsFromTHnSparse;

    // Function that transforms the map storing trigger and vYieldsAndErrors into just vYieldsAndErrors
    auto vYieldsAndErrors = YieldsAndErrorsForGivenTrigger(canvasConfigs.TriggerToUse, mapYieldsAndErrors, CALCULATE_ERRORS);

    Int_t nTUNES = vTUNES.size();
    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    // Int_t nDependencies = vHistogramAndTriggerPtHistogramNames.size();
    Int_t nDependencies = vBinsFromTHnSparse.size();

    // Values will be drawn from a 2D vector of TH1D with number of DEPENDENCIES bins
    // This way the TUNE and ASSOCIATE can be looped over, while the data points will be the DEPENDENCIES
    TH1D *vHists[nTUNES][nAssociates];
    if (VERBOSE) { 
        std::cout << "number of dependencies: " << nDependencies << std::endl;
        std::cout << std::endl; 
    }

    // Define a template for this plot to set titles, stats, etc.
    TH1D *hYieldsTemplate = new TH1D(Form("hYieldsBaryonMesonRatioTemplate_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("hYieldsBaryonMesonRatioTemplate_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), nDependencies, 0, nDependencies);
    hYieldsTemplate->SetTitle(canvasConfigs.canvasTitle.c_str());
    hYieldsTemplate->GetXaxis()->SetTitle(canvasConfigs.xAxisTitle.c_str());
    hYieldsTemplate->GetYaxis()->SetTitle(canvasConfigs.yAxisTitle.c_str());
    std::cout << "- Setting y-axis range: (" << canvasConfigs.yMinAxis << "," << canvasConfigs.yMaxAxis << ")" << std::endl;
    hYieldsTemplate->GetYaxis()->SetRangeUser(canvasConfigs.yMinAxis,canvasConfigs.yMaxAxis);

    TCanvas *cYields = new TCanvas(Form("cYieldsBaryonMesonRatio_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("cYieldsBaryonMesonRatio_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), canvasConfigs.xSizeCanvas, canvasConfigs.ySizeCanvas);
    cYields->cd();
    if (canvasConfigs.setLogy) { gPad->SetLogy(); }
    hYieldsTemplate->SetStats(0);
    hYieldsTemplate->Draw("PE");

    // Draw mini pad for global canvas (only used if asked in configurations)
    TPad* cMiniPad;
    if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
        std::cout << "- Creating mini pad with dimensions x1(" << canvasConfigs.xMinPad << "," << canvasConfigs.yMinPad << ") and x2(" << canvasConfigs.xMaxPad << "," << canvasConfigs.yMaxPad << ")" << std::endl;
        cMiniPad = new TPad(Form("cMiniPad_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("cMiniPad_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), canvasConfigs.xMinPad, canvasConfigs.yMinPad, canvasConfigs.xMaxPad, canvasConfigs.yMaxPad);
        cMiniPad->SetTickx(1);
        cMiniPad->SetTicky(1);
        if (canvasConfigs.topMarginPad != -1 && canvasConfigs.bottomMarginPad != -1 && canvasConfigs.leftMarginPad != -1 && canvasConfigs.rightMarginPad != -1) {
            std::cout << "- Setting mini pad margins to " << canvasConfigs.topMarginPad << " (top), " << canvasConfigs.bottomMarginPad << " (bottom), " << canvasConfigs.leftMarginPad << " (left), " << canvasConfigs.rightMarginPad << " (right)" << std::endl;
            cMiniPad->SetTopMargin(canvasConfigs.topMarginPad);
            cMiniPad->SetBottomMargin(canvasConfigs.bottomMarginPad);
            cMiniPad->SetLeftMargin(canvasConfigs.leftMarginPad);
            cMiniPad->SetRightMargin(canvasConfigs.rightMarginPad);
        }
        cMiniPad->cd();
        if (canvasConfigs.setLogy) { gPad->SetLogy(); }
        hYieldsTemplate->SetStats(0);
        hYieldsTemplate->Draw("PE");
    }

    std::map<std::string, Int_t> colourTUNEMap = canvasConfigs.colourTUNEMap;
    std::map<std::string, Int_t> lineStyleBaryonMap = canvasConfigs.lineStyleBaryonMap;

    TLegend *legend = nullptr;
    std::map<std::string, std::string> legendEntriesMap = canvasConfigs.legendEntriesMap;
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        std::cout << "- Creating legend at positions x1(" << canvasConfigs.xMinLegend << "," << canvasConfigs.yMinLegend << ") and x2(" << canvasConfigs.xMaxLegend << "," << canvasConfigs.yMaxLegend << ")" << std::endl;
        legend = new TLegend(canvasConfigs.xMinLegend, canvasConfigs.yMinLegend, canvasConfigs.xMaxLegend, canvasConfigs.yMaxLegend);
    } else { std::cout << "- NOTE: Not drawing legend for this plot" << std::endl; }

    // Guarantee the legend entries are only drawn once
    std::set<std::string> alreadyInLegend;

    // Optional: define hard coded settings below
    if (canvasConfigs.useHardCodedSettings) {
        if (isCanvasNameEqualTo(canvasConfigs.canvasName, "mini_beauty_balancing_baryon_over_meson_ratio_lambda_only")) {
            std::cout << "- WARNING: using hard-coded settings for this canvas" << std::endl;
        }
    }


    // Loop over TUNES
    for (Int_t i=0; i<nTUNES; i++) {


        std::string TUNE = vTUNES[i];
        if (VERBOSE) {
            std::cout << "starting loop over " << TUNE << std::endl;
            std::cout << std::endl;
        }


        // Loop over ASSOCIATES
        for (Int_t j=0; j<nAssociates; j++) {


            // TODO: fix this bug with associateName and formatting....
            TriggerAssociateOSandSS fileNamesOSandSS = vTriggerAssociateOSandSS[j];
            std::string associateName = fileNamesOSandSS.associateOS;
            if (!plotBaryon(associateName, canvasConfigs.vBaryonNames)) {continue; }
            if (VERBOSE) {
                std::cout << "starting loop over associate: " << associateName << std::endl;
                std::cout << "starting loop over OS file: " << fileNamesOSandSS.OS << " and SS file: " << fileNamesOSandSS.SS << std::endl;
                std::cout << std::endl;
            }

            // Loop over DEPENDENCIES
            for (Int_t k=0; k<nDependencies; k++) {


                // HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
                BinsFromTHnSparse binFromTHnSparse = vBinsFromTHnSparse[k];
                if (VERBOSE) { 
                    std::cout << "plotting histogram " << binFromTHnSparse.hDPhi << " with trigger pT histogram " << binFromTHnSparse.hTrPt << std::endl;
                    std::cout << std::endl;
                }
                vHists[i][j] = new TH1D(Form("hYieldsBaryonMesonRatio_%s_%i_%i_%i_%s", FLAVOUR, i, j, k, (canvasConfigs.canvasName).c_str()), Form("hYieldsBaryonMesonRatio_%s_%i_%i_%i_%s", FLAVOUR, i, j, k, (canvasConfigs.canvasName).c_str()), nDependencies, 0, nDependencies);
                vHists[i][j]->SetBinContent(1+k, vYieldsAndErrors.vYields[i][j][k] / vYieldsAndErrors.vYields[i][0][k]);
                if (CALCULATE_ERRORS) { 
                    // Several options for error calculation/propagation
                    // Ratio calculated seperately:
                    vHists[i][j]->SetBinError(1+k, vYieldsAndErrors.vYieldsRatioErrors[i][j][k]);
                    // Naive error propagation (assuming no correlation):
                    /*
                    vHists[i][j]->SetBinError(1+k, propagateRatioError(vYieldsAndErrors.vYields[i][j][k], 
                                                                       vYieldsAndErrors.vYields[i][0][k],
                                                                       vYieldsAndErrors.vYieldsErrors[i][j][k],
                                                                       vYieldsAndErrors.vYieldsErrors[i][0][k]));
                    */
                    // Placeholder; same error as single yield:
                    // vHists[i][j]->SetBinError(1+k, vYieldsAndErrors.vYieldsErrors[i][j][k]);
                }
                else {
                    vHists[i][j]->SetBinError(1+k, 1e-10);
                }
                ApplyTuneVisualStyle(vHists[i][j], TUNE);
                cYields->cd();
                vHists[i][j]->Draw("same PE");
                if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                    cMiniPad->cd();
                    vHists[i][j]->Draw("same PE");
                }

                hYieldsTemplate->GetXaxis()->SetBinLabel(1+k, (binFromTHnSparse.hDPhi).c_str());

                if (colourTUNEMap.find(TUNE) != colourTUNEMap.end()) {
                    Int_t colour = colourTUNEMap[TUNE];
                    vHists[i][j]->SetLineColor(colour);
                    vHists[i][j]->SetMarkerColor(colour);
                    if (VERBOSE) { std::cout << "Found colour: " << colour << std::endl; }
                } else {
                    if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                }

                if (lineStyleBaryonMap.find(associateName) != lineStyleBaryonMap.end()) {
                    Int_t lineStyle = lineStyleBaryonMap[associateName];
                    vHists[i][j]->SetLineStyle(lineStyle);
                    if (VERBOSE) { std::cout << "Found lineStyle: " << lineStyle << std::endl; }
                } else {
                    if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                }

                // Draw legend
                // TODO: only do this once (but cannot put j==0)
                if (legend != nullptr && alreadyInLegend.find(associateName) == alreadyInLegend.end()) {
                    if (legendEntriesMap.find(associateName) != legendEntriesMap.end()) {
                        std::string displayName = legendEntriesMap[associateName];
                        if (VERBOSE) { std::cout << "Found displayName: " << displayName << std::endl; }
                        legend->AddEntry(vHists[i][j], displayName.c_str(), "lep");
                    } else {
                        if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                    }
                    alreadyInLegend.insert(associateName);
                }


                if (VERBOSE) { std::cout << std::endl; }


            } // Loop over DEPENDENCIES


        } // Loop over ASSOCIATES


    } // Loop over TUNES


    // TODO: change cYields and stuff to just 'canvas'
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        cYields->cd();
        legend->Draw();
        if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
            cMiniPad->cd();
            legend->Draw();
        }
    }

    if (canvasConfigs.write) { 
        writeCanvasToFiles(VERBOSE, cYields, canvasConfigs.writePath, canvasConfigs.writeName); 
    }


    return cMiniPad;


} // drawBalancingBaryonMesonRatioPlots()


TPad* drawBalancingBaryonMesonRatioPlotsTUNERatios(CONFIGS configs_from_json, const char* FLAVOUR, YieldsAndErrorsMap mapYieldsAndErrors,
                                                  Int_t indexNominatorTUNE, Int_t indexDenominatorTUNE) {


    std::cout << "*** Drawing balancing baryon/meson ratio plots with TUNE ratios for " << FLAVOUR << " ***" << std::endl;


    // Retrieve settings from configuration.json
    canvasConfigs canvasConfigs = configs_from_json.currentCanvasConfigs;
    bool VERBOSE = configs_from_json.VERBOSE;
    bool CALCULATE_ERRORS = configs_from_json.CALCULATE_ERRORS;
    std::string base_dir = configs_from_json.base_dir;
    std::vector<std::string> vTUNES = configs_from_json.vTUNES;
    std::vector<TriggerAssociateOSandSS> vTriggerAssociateOSandSS;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { vTriggerAssociateOSandSS = configs_from_json.beautyConfigs.at(canvasConfigs.TriggerToUse); }
    if (strcmp(FLAVOUR, "CHARM") ==  0) { vTriggerAssociateOSandSS = configs_from_json.charmConfigs.at(canvasConfigs.TriggerToUse); }
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames = configs_from_json.vHistogramAndTriggerPtHistogramNames;
    std::vector<BinsFromTHnSparse> vBinsFromTHnSparse = configs_from_json.vBinsFromTHnSparse;

    std::cout << " and TUNE = " << vTUNES[indexNominatorTUNE] << "/" << vTUNES[indexDenominatorTUNE] << " ***" << std::endl;

    // Function that transforms the map storing trigger and vYieldsAndErrors into just vYieldsAndErrors
    auto vYieldsAndErrors = YieldsAndErrorsForGivenTrigger(canvasConfigs.TriggerToUse, mapYieldsAndErrors, CALCULATE_ERRORS);

    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    // Int_t nDependencies = vHistogramAndTriggerPtHistogramNames.size();
    Int_t nDependencies = vBinsFromTHnSparse.size();

    // Values will be drawn from a 2D vector of TH1D with number of DEPENDENCIES bins
    // This way the TUNE and ASSOCIATE can be looped over, while the data points will be the DEPENDENCIES
    TH1D *vHists[nAssociates];
    // TODO: verbose
    // std::cout << "number of dependencies: " << nDependencies << std::endl;

    // Define a template for this plot to set titles, stats, etc.
    TH1D *hYieldsTemplate = new TH1D(Form("hYieldsBaryonMesonRatioTUNERatioTemplate_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("hYieldsBaryonMesonRatioTUNERatioTemplate_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), nDependencies, 0, nDependencies);
    hYieldsTemplate->SetTitle(canvasConfigs.canvasTitle.c_str());
    hYieldsTemplate->GetXaxis()->SetTitle(canvasConfigs.xAxisTitle.c_str());
    hYieldsTemplate->GetYaxis()->SetTitle(canvasConfigs.yAxisTitle.c_str());
    std::cout << "- Setting y-axis range: (" << canvasConfigs.yMinAxis << "," << canvasConfigs.yMaxAxis << ")" << std::endl;
    hYieldsTemplate->GetYaxis()->SetRangeUser(canvasConfigs.yMinAxis,canvasConfigs.yMaxAxis);

    TCanvas *cYields = new TCanvas(Form("cYieldsBaryonMesonRatioTUNERatio_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("cYieldsBaryonMesonRatioTUNERatio_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), canvasConfigs.xSizeCanvas, canvasConfigs.ySizeCanvas);
    cYields->cd();
    if (canvasConfigs.setLogy) { gPad->SetLogy(); }
    hYieldsTemplate->SetStats(0);
    hYieldsTemplate->Draw("PE");

    // Draw mini pad for global canvas (only used if asked in configurations)
    TPad* cMiniPad;
    if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
        std::cout << "- Creating mini pad with dimensions x1(" << canvasConfigs.xMinPad << "," << canvasConfigs.yMinPad << ") and x2(" << canvasConfigs.xMaxPad << "," << canvasConfigs.yMaxPad << ")" << std::endl;
        cMiniPad = new TPad(Form("cMiniPad_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), Form("cMiniPad_%s_%s", FLAVOUR, (canvasConfigs.canvasName).c_str()), canvasConfigs.xMinPad, canvasConfigs.yMinPad, canvasConfigs.xMaxPad, canvasConfigs.yMaxPad);
        cMiniPad->SetTickx(1);
        cMiniPad->SetTicky(1);
        if (canvasConfigs.topMarginPad != -1 && canvasConfigs.bottomMarginPad != -1 && canvasConfigs.leftMarginPad != -1 && canvasConfigs.rightMarginPad != -1) {
            std::cout << "- Setting mini pad margins to " << canvasConfigs.topMarginPad << " (top), " << canvasConfigs.bottomMarginPad << " (bottom), " << canvasConfigs.leftMarginPad << " (left), " << canvasConfigs.rightMarginPad << " (right)" << std::endl;
            cMiniPad->SetTopMargin(canvasConfigs.topMarginPad);
            cMiniPad->SetBottomMargin(canvasConfigs.bottomMarginPad);
            cMiniPad->SetLeftMargin(canvasConfigs.leftMarginPad);
            cMiniPad->SetRightMargin(canvasConfigs.rightMarginPad);
        }
        cMiniPad->cd();
        if (canvasConfigs.setLogy) { gPad->SetLogy(); }
        hYieldsTemplate->SetStats(0);
        hYieldsTemplate->Draw("PE");
    }

    std::map<std::string, Int_t> colourTUNEMap = canvasConfigs.colourTUNEMap;
    std::map<std::string, Int_t> lineStyleBaryonMap = canvasConfigs.lineStyleBaryonMap;

    TLegend *legend = nullptr;
    std::map<std::string, std::string> legendEntriesMap = canvasConfigs.legendEntriesMap;
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        std::cout << "- Creating legend at positions x1(" << canvasConfigs.xMinLegend << "," << canvasConfigs.yMinLegend << ") and x2(" << canvasConfigs.xMaxLegend << "," << canvasConfigs.yMaxLegend << ")" << std::endl;
        legend = new TLegend(canvasConfigs.xMinLegend, canvasConfigs.yMinLegend, canvasConfigs.xMaxLegend, canvasConfigs.yMaxLegend);
    } else { std::cout << "- NOTE: Not drawing legend for this plot" << std::endl; }

    // Guarantee the legend entries are only drawn once
    std::set<std::string> alreadyInLegend;

    // Optional: define hard coded settings below
    if (canvasConfigs.useHardCodedSettings) {
        if (isCanvasNameEqualTo(canvasConfigs.canvasName, "canvas_name")) {
            std::cout << "- WARNING: using hard-coded settings for this canvas" << std::endl;
            std::cout << std::endl;
        }
    }


    // Loop over ASSOCIATES
    for (Int_t j=0; j<nAssociates; j++) {


        // TODO: fix this bug with associateName and formatting....
        TriggerAssociateOSandSS fileNamesOSandSS = vTriggerAssociateOSandSS[j];
        std::string associateName = fileNamesOSandSS.associateOS;
        if (!plotBaryon(associateName, canvasConfigs.vBaryonNames)) {continue; }
        // TODO: verbose
        // std::cout << "starting loop over associate: " << associateName << std::endl;
        // std::cout << "starting loop over OS file: " << fileNamesOSandSS.OS << " and SS file: " << fileNamesOSandSS.SS << std::endl;
        // std::cout << std::endl;

        // Loop over DEPENDENCIES
        for (Int_t k=0; k<nDependencies; k++) {


            // HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
            BinsFromTHnSparse binFromTHnSparse = vBinsFromTHnSparse[k];
            // TODO: verbose
            // std::cout << "plotting histogram " << hDPhiAndhTrPtNames.hDPhi << " with trigger pT histogram " << hDPhiAndhTrPtNames.hTrPt << std::endl;

            vHists[j] = new TH1D(Form("hYieldsBaryonMesonRatio_%s_%i_%i_%s", FLAVOUR, j, k, (canvasConfigs.canvasName).c_str()), Form("hYieldsBaryonMesonRatio_%s_%i_%i_%s", FLAVOUR, j, k, (canvasConfigs.canvasName).c_str()), nDependencies, 0, nDependencies);
            vHists[j]->SetBinContent(1+k, (vYieldsAndErrors.vYields[indexNominatorTUNE][j][k] / vYieldsAndErrors.vYields[indexNominatorTUNE][0][k])
                                           / (vYieldsAndErrors.vYields[indexDenominatorTUNE][j][k] / vYieldsAndErrors.vYields[indexDenominatorTUNE][0][k]));
            if (CALCULATE_ERRORS) { 
                // Several options for error calculation/propagation
                // Ratio calculated seperately:
                // TODO: add this in yield calculation
                // TODO: also check if this is without bugs (features?) now..
                // vHists[j]->SetBinError(1+k, vYieldsAndErrors.vYieldsRatioErrors[i][j][k]);
                vHists[j]->SetBinError(1+k, propagateRatioError(vYieldsAndErrors.vYields[indexNominatorTUNE][j][k]/vYieldsAndErrors.vYields[indexDenominatorTUNE][j][k], 
                                                                vYieldsAndErrors.vYields[indexNominatorTUNE][0][k]/vYieldsAndErrors.vYields[indexDenominatorTUNE][0][k],
                                                                vYieldsAndErrors.vYieldsRatioErrors[indexNominatorTUNE][j][k],
                                                                vYieldsAndErrors.vYieldsRatioErrors[indexDenominatorTUNE][0][k]));
                // Naive error propagation (assuming no correlation):
                /*
                vHists[j]->SetBinError(1+k, propagateRatioError(vYieldsAndErrors.vYields[i][j][k], 
                                                                    vYieldsAndErrors.vYields[i][0][k],
                                                                    vYieldsAndErrors.vYieldsErrors[i][j][k],
                                                                    vYieldsAndErrors.vYieldsErrors[i][0][k]));
                */
                // Placeholder; same error as single yield:
                // vHists[j]->SetBinError(1+k, vYieldsAndErrors.vYieldsErrors[i][j][k]);
            }
            else {
                vHists[j]->SetBinError(1+k, 1e-10);
            }
            ApplyTuneVisualStyle(vHists[j], vTUNES[indexNominatorTUNE]);
            cYields->cd();
            vHists[j]->Draw("same PE");
            if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                cMiniPad->cd();
                vHists[j]->Draw("same PE");
            }

            hYieldsTemplate->GetXaxis()->SetBinLabel(1+k, (binFromTHnSparse.hDPhi).c_str());

            if (lineStyleBaryonMap.find(associateName) != lineStyleBaryonMap.end()) {
                    Int_t lineStyle = lineStyleBaryonMap[associateName];
                    vHists[j]->SetLineStyle(lineStyle);
                    // TODO: verbose
                    // std::cout << "Found lineStyle: " << lineStyle << std::endl;
                } else {
                    // TODO: verbose
                    // std::cout << "objectName not found in the map!" << std::endl;
                }

            // TODO: verbose
            // std::cout << std::endl;


        } // Loop over DEPENDENCIES


        // Draw legend
        if (legend != nullptr && alreadyInLegend.find(associateName) == alreadyInLegend.end()) {
            if (legendEntriesMap.find(associateName) != legendEntriesMap.end()) {
                std::string displayName = legendEntriesMap[associateName];
                // TODO: verbose
                // std::cout << "Found displayName: " << displayName << std::endl;
                legend->AddEntry(vHists[j], displayName.c_str(), "lep");
            } else {
                // TODO: verbose
                // std::cout << "objectName not found in the map!" << std::endl;
            }
            alreadyInLegend.insert(associateName);
        }


    } // Loop over ASSOCIATES


    // TODO: change cYields and stuff to just 'canvas'
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        cYields->cd();
        legend->Draw();
        if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
            cMiniPad->cd();
            legend->Draw();
        }
    }

    if (canvasConfigs.write) { 
        writeCanvasToFiles(VERBOSE, cYields, canvasConfigs.writePath, canvasConfigs.writeName); 
    }


    return cMiniPad;


} // drawBalancingBaryonMesonRatioPlotsTUNERatios()


// Run macro with 
// >> root 'improvedPlotting.C("configuration_multiplicity.json")'
int improvedPlotting_THnSparse(const char* configuration) {

    // Read configurations defined by user in configuration.json
    CONFIGS configs_from_json = readConfig(configuration);
    bool VERBOSE = configs_from_json.VERBOSE;

    // Calculate the 3D yield vector
    // TODO: define this below in loop
    YieldsAndErrorsMap mapYields; // used in loop over canvas settings
    YieldsAndErrorsMap mapYieldsBeauty;
    YieldsAndErrorsMap mapYieldsCharm;
    mapYieldsBeauty = calculateYieldsVector(configs_from_json,"BEAUTY");
    mapYieldsCharm =  calculateYieldsVector(configs_from_json,"CHARM");

    // Draw the balancing plots using the 3D yield vector and configurations given
    std::vector<canvasConfigs> vCanvasConfigs = configs_from_json.vCanvasConfigs;
    std::vector<TCanvas*> vCanvases;
    // Add the mini pads so they can be drawn on a global canvas after the loop
    // - map[key] = object
    std::map<std::string, TPad*> cMiniCanvasMap;

    for (const auto& canvasConfigs : vCanvasConfigs) {
        configs_from_json.currentCanvasConfigs = canvasConfigs;
        std::string canvasName = canvasConfigs.canvasName;
        std::string drawFunctionToUse = canvasConfigs.drawFunctionToUse;
        std::vector<std::string> vCanvasTUNES = canvasConfigs.vCanvasTUNES;
        std::string FLAVOUR = canvasConfigs.FLAVOUR;
        std::string TriggerToUse = canvasConfigs.TriggerToUse;
        Int_t indexNominatorTUNE = canvasConfigs.indexNominatorTUNE;
        Int_t indexDenominatorTUNE = canvasConfigs.indexDenominatorTUNE;
        // TODO: alternatively, just don't define vYieldsBeauty above, 
        // it's a bit redundant now..
        // TODO: add more error messages and checks
        if (strcmp(FLAVOUR.c_str(), "BEAUTY") == 0) { mapYields = mapYieldsBeauty; }
        if (strcmp(FLAVOUR.c_str(), "CHARM" ) == 0) { mapYields = mapYieldsCharm;  }

        if (strcmp(drawFunctionToUse.c_str(), "drawBalancingPlots") == 0) { 
            TPad *cMiniPad = drawBalancingPlots(configs_from_json, FLAVOUR.c_str(), mapYields); 
            cMiniCanvasMap[canvasName] = cMiniPad;
        }
        if (strcmp(drawFunctionToUse.c_str(), "drawBalancingPlotsTUNERatios") == 0) { 
            TPad *cMiniPad = drawBalancingPlotsTUNERatios(configs_from_json,FLAVOUR.c_str(), mapYields, indexNominatorTUNE, indexDenominatorTUNE);
            cMiniCanvasMap[canvasName] = cMiniPad; 
        }
        if (strcmp(drawFunctionToUse.c_str(), "drawBalancingBaryonMesonRatioPlots") == 0) { 
            TPad *cMiniPad = drawBalancingBaryonMesonRatioPlots(configs_from_json,FLAVOUR.c_str(), mapYields);
            cMiniCanvasMap[canvasName] = cMiniPad; 
        }
        if (strcmp(drawFunctionToUse.c_str(), "drawBalancingBaryonMesonRatioPlotsTUNERatios") == 0) { 
            TPad *cMiniPad = drawBalancingBaryonMesonRatioPlotsTUNERatios(configs_from_json,FLAVOUR.c_str(), mapYields, indexNominatorTUNE, indexDenominatorTUNE); 
            cMiniCanvasMap[canvasName] = cMiniPad;
        }
    } // Loop over canvas settings

    std::cout << std::endl;
    std::cout << "*** Drawing global canvases ***" << std::endl;
    std::vector<globalCanvasConfigs> vGlobalCanvasConfigs = configs_from_json.vGlobalCanvasConfigs;
    for (const auto& globalCanvasConfig : vGlobalCanvasConfigs) {
        TCanvas *globalCanvas = new TCanvas(Form("%s", (globalCanvasConfig.canvasName).c_str()), Form("%s", (globalCanvasConfig.canvasName).c_str()), globalCanvasConfig.xSizeCanvas, globalCanvasConfig.ySizeCanvas);
        for (const auto& cMiniCanvas : globalCanvasConfig.vMiniCanvases) {
            if (VERBOSE) { std::cout << "Using mini canvas with name = " << cMiniCanvas << std::endl; }
            // TODO: maybe add in global canvas settings an option to add a (custom) legend?
            if (!cMiniCanvasMap[cMiniCanvas]) { 
                std::cout << "- ERROR: did not find " << cMiniCanvas << " in global canvas settings" << std::endl;
                continue; 
            }
            globalCanvas->cd();
            cMiniCanvasMap[cMiniCanvas]->Draw(); 
        } // Loop over mini canvas names
        if (globalCanvasConfig.write) { 
            writeCanvasToFiles(VERBOSE, globalCanvas, globalCanvasConfig.writePath, globalCanvasConfig.writeName); 
        }
    } // Loop over global canvas settings
    std::cout << "Global canvases drawn without problems (...?)" << std::endl;

    // TODO: in existing functions, add the TUNE[i]/TUNE[j] subratio plots
    // (including error propagation)

    // TODO: add the part for miniPads

    // TODO: only for simple tests, remove
    /*
    drawBalancingPlots(configs_from_json,"BEAUTY",vYieldsBeauty);
    drawBalancingPlots(configs_from_json,"CHARM", vYieldsCharm);

    drawBalancingBaryonMesonRatioPlots(configs_from_json,"BEAUTY",vYieldsBeauty);
    drawBalancingBaryonMesonRatioPlots(configs_from_json,"CHARM", vYieldsCharm);
    */

    return 0;
}
