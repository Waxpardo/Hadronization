// improvedPlotting.C
// Paul Veen (paul.veen@cern.ch)

// C headers
#include <iostream>
#include <fstream>
#include <algorithm>
#include <random>
#include <cmath>

// ROOT headers
#include "TFile.h"
#include "TH1D.h"
#include "TCanvas.h"
#include "TString.h" // TODO: can use this for the legend entry names?
#include <TLegend.h>

// For me the code does not work when this is explicitly included
// I guess it depends on the set-up
// Enable this if there is unexplainable problems with reading the .json file
// #include <nlohmann/json.hpp>

using json = nlohmann::json;

// TODO: put structs in a header file (only after plotting is done in configuration.json)

// TODO: add verbose/debug flags to configuration.json

// TODO: update the other configuration.json files with the "configuration.json" script

// TODO: optimise drawing ranges for all plots

// TODO: add many more error statements and checks. 
// It needs to be clear for the user what went wrong when something went wrong (in particular related to the configuration.json)

// TODO: add new junctions simulations

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


struct YieldsAndErrors {
    std::vector<std::vector<std::vector<Double_t>>> vYields;
    std::vector<std::vector<std::vector<Double_t>>> vYieldsErrors;
    std::vector<std::vector<std::vector<Double_t>>> vYieldsRatioErrors;
};


struct canvasConfigs {
    std::string canvasName;
    std::string drawFunctionToUse; // name of functions defined in improvedPlotting()
    std::vector<std::string> vCanvasTUNES; // tune to be drawn on given canvas
    std::string FLAVOUR; // just one allowed, but could implement with a new function
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
    std::string base_dir;

    // MONASH, JUNCTIONS, else...
    std::vector<std::string> vTUNES;

    // Which complete_root production? (beauty and charm)
    std::string bbBarDir;
    std::string ccBarDir;
    std::string bbBarDir_subSamples;
    std::string ccBarDir_subSamples;

    // (BplusBminus.root,BplusBplus.root), ...
    std::vector<TriggerAssociateOSandSS> vBeautyTriggerAssociateOSandSS;
    std::vector<TriggerAssociateOSandSS> vCharmTriggerAssociateOSandSS;

    // (hDPhiLL, hTrPtL), ...
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames;

    // Plotting settings
    std::vector<canvasConfigs> vCanvasConfigs;
    canvasConfigs currentCanvasConfigs; // filled later, when looping over vCanvasConfigs, given as argument to plotting function
    std::vector<globalCanvasConfigs> vGlobalCanvasConfigs;
};


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


CONFIGS readConfig(const char* configurations) {

    std::cout << std::endl;
    std::cout << "*** Reading configuration.json ***" << std::endl;
    std::cout << std::endl;

    // Open the JSON configuration file
    std::ifstream configFile(configurations);
    if (!configFile.is_open()) {
        std::cerr << "Error opening configuration file." << std::endl;
    }

    // Parse the JSON file
    json config;
    configFile >> config;

    // Extract values from the JSON
    // Generic options
    bool VERBOSE = config["VERBOSE"].get<bool>();
    bool CALCULATE_ERRORS = config["calculate_errors"].get<bool>();
    std::string bbBarDir_sub_samples = config["bb_bar_complete_root_dir_sub_samples"];
    std::string ccBarDir_sub_samples = config["cc_bar_complete_root_dir_sub_samples"];
    int nSubSamples = config["nSubSamples"].get<int>();

    // RootFiles path ("base directory")
    std::string base_dir = config["base_dir"];

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
        std::cout << "Full path charm sub samples" << TUNE << ": " << path_to_complete_root_dir_sub_samples << std::endl;
    }
    std::cout << std::endl;

    // Which correlations need to be analysed?
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
    std::vector<TriggerAssociateOSandSS> vCharmTriggerAssociateOSandSS;
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

    // Which histograms need to be analysed?
    // i.e. which dependencies (pT, mult, etc.)
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames;
    for (const auto& configPair : config["histograms_to_analyse"]) {
        HistogramAndTriggerPtHistogramNames pair;
        pair.hDPhi = configPair["hDPhi"].get<std::string>();
        pair.hTrPt = configPair["hTrPt"].get<std::string>();
        vHistogramAndTriggerPtHistogramNames.push_back(pair);
    }
    for (const auto& pair : vHistogramAndTriggerPtHistogramNames) {
        std::cout << "hDPhi: " << pair.hDPhi << ", hTrPt: " << pair.hTrPt << std::endl;
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
        std::string nominatorTuneName = configPair["nominator_TUNE"].get<std::string>();
        pair.indexNominatorTUNE = findTuneIndex(vTUNES, nominatorTuneName);
        if (pair.indexNominatorTUNE != -1) {
            std::cout << "Index of " << nominatorTuneName << " is: " << pair.indexNominatorTUNE << std::endl;
        } else {
            std::cout << nominatorTuneName << " ERROR: TUNE not found in vTUNES." << std::endl;
        }
        std::string denominatorTuneName = configPair["denominator_TUNE"].get<std::string>();
        pair.indexDenominatorTUNE = findTuneIndex(vTUNES, denominatorTuneName);
        if (pair.indexDenominatorTUNE != -1) {
            std::cout << "Index of " << denominatorTuneName << " is: " << pair.indexDenominatorTUNE << std::endl;
        } else {
            std::cout << nominatorTuneName << " ERROR: TUNE not found in vTUNES." << std::endl;
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
        pair.writePath = configPair["write_path"].get<std::string>();
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
        pair.writePath = configPair["write_path"].get<std::string>();
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
    configs_from_json.base_dir = base_dir;
    configs_from_json.vTUNES = vTUNES;
    configs_from_json.bbBarDir = bbBarDir;
    configs_from_json.ccBarDir = ccBarDir;
    configs_from_json.bbBarDir_subSamples = bbBarDir_sub_samples;
    configs_from_json.ccBarDir_subSamples = ccBarDir_sub_samples;
    configs_from_json.vBeautyTriggerAssociateOSandSS = vBeautyTriggerAssociateOSandSS;
    configs_from_json.vCharmTriggerAssociateOSandSS = vCharmTriggerAssociateOSandSS;
    configs_from_json.vHistogramAndTriggerPtHistogramNames = vHistogramAndTriggerPtHistogramNames;
    configs_from_json.vCanvasConfigs = vCanvasConfigs;
    configs_from_json.vGlobalCanvasConfigs = vGlobalCanvasConfigs;

    std::cout << "Configurations successfully read from JSON with parameters:" << std::endl;
    std::cout << "VERBOSE = " << VERBOSE << std::endl;
    std::cout << "- CALCULATE_ERRORS = " << CALCULATE_ERRORS << std::endl;
    std::cout << "- nSubSamples = " << nSubSamples << std::endl;
    std::cout << "- base_dir = " << base_dir << std::endl;
    std::cout << "- vTUNES.size() = " << vTUNES.size() << std::endl;
    std::cout << "- bbBarDir = " << bbBarDir << std::endl;
    std::cout << "- ccBarDir = " << ccBarDir << std::endl;
    std::cout << "- bbBarDir_sub_samples = " << bbBarDir_sub_samples << std::endl;
    std::cout << "- ccBarDir_sub_samples = " << ccBarDir_sub_samples << std::endl;
    std::cout << "- vBeautyTriggerAssociateOSandSS.size() = " << vBeautyTriggerAssociateOSandSS.size() << std::endl;
    std::cout << "- vCharmTriggerAssociateOSandSS.size() = " << vCharmTriggerAssociateOSandSS.size() << std::endl;
    std::cout << "- vHistogramAndTriggerPtHistogramNames.size() = " << vHistogramAndTriggerPtHistogramNames.size() << std::endl;
    // vCanvasConfigs
    // TODO: give overview of canvases to be drawn and their settings etc.
    std::cout << std::endl;

    return configs_from_json;

} // readConfig()


// Simple function that returns the propagated error from a ratio A/B with errors for A and B
// Assumes A and B are uncorrelated
Double_t propagateRatioError(Double_t valueA, Double_t valueB, Double_t errorA, Double_t errorB) {
    Double_t relativeUncertainty = pow((errorA / valueA), 2) + pow((errorB / valueB), 2);
    return ((valueA / valueB) * sqrt(relativeUncertainty));
} // propagateRatioError()


// Simple function to calculate the yield given by two normalised OS and SS histograms
// Their angular spectra are subtracted (OS - SS) to reduce background
// and the full spectrum is integrated, though there is a posiblity to chose the integration range
// (if desired)
Double_t calculateOneYield(bool VERBOSE, TH1D *hDPhiOS, TH1D *hTrPtOS, TH1D *hDPhiSS, TH1D *hTrPtSS, const char* FLAVOUR, 
                           Int_t i, Int_t j, Int_t k, Int_t l) {

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
YieldsAndErrors calculateYieldsVector(CONFIGS configs_from_json, const char* FLAVOUR) {

    std::cout << "*** Calculating yields for " << FLAVOUR << " ***" << std::endl;

    // Retrieve settings from configuration.json
    bool VERBOSE = configs_from_json.VERBOSE;
    bool CALCULATE_ERRORS = configs_from_json.CALCULATE_ERRORS;
    int nSubSamples = configs_from_json.nSubSamples;
    std::string base_dir = configs_from_json.base_dir;
    std::vector<std::string> vTUNES = configs_from_json.vTUNES;
    std::string complete_root_dir;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { complete_root_dir = configs_from_json.bbBarDir; }
    if (strcmp(FLAVOUR, "CHARM")  == 0) { complete_root_dir = configs_from_json.ccBarDir; }
    std::string complete_root_dir_sub_samples;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { complete_root_dir_sub_samples = configs_from_json.bbBarDir_subSamples; }
    if (strcmp(FLAVOUR, "CHARM")  == 0) { complete_root_dir_sub_samples = configs_from_json.ccBarDir_subSamples; }
    std::vector<TriggerAssociateOSandSS> vTriggerAssociateOSandSS;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { vTriggerAssociateOSandSS = configs_from_json.vBeautyTriggerAssociateOSandSS; }
    if (strcmp(FLAVOUR, "CHARM")  == 0) { vTriggerAssociateOSandSS = configs_from_json.vCharmTriggerAssociateOSandSS; }
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames = configs_from_json.vHistogramAndTriggerPtHistogramNames;

    // TODO: make these vectors into arrays, don't think vector is necessary
    // and the subYields are stored in an array anyways
    std::vector<std::vector<std::vector<Double_t>>> vYields;
    std::vector<std::vector<std::vector<Double_t>>> vYieldsErrors;
    std::vector<std::vector<std::vector<Double_t>>> vYieldsRatioErrors;
    Double_t vSubYields[vTUNES.size()][vTriggerAssociateOSandSS.size()][vHistogramAndTriggerPtHistogramNames.size()][nSubSamples];


    // TODO: make vTUNES.size into nTUNES, like in the plotting functions
    // Loop over TUNES
    for (Int_t i=0; i<vTUNES.size(); i++) {


        std::string TUNE = vTUNES[i];
        std::cout << "starting loop over " << TUNE << std::endl;
        std::cout << std::endl;


        // Loop over ASSOCIATES
        for (Int_t j=0; j<vTriggerAssociateOSandSS.size(); j++) {


            TriggerAssociateOSandSS fileNamesOSandSS = vTriggerAssociateOSandSS[j];
            std::cout << "starting loop over OS file: " << fileNamesOSandSS.OS << " and SS file: " << fileNamesOSandSS.SS << std::endl;
            TFile *OStree = new TFile((base_dir + "/" + TUNE + "/" + complete_root_dir + "_" + TUNE + "/" + fileNamesOSandSS.OS).c_str());
            TFile *SStree = new TFile((base_dir + "/" + TUNE + "/" + complete_root_dir + "_" + TUNE + "/" + fileNamesOSandSS.SS).c_str());
            std::cout << std::endl;


            // Loop over DEPENDENCIES
            for (Int_t k=0; k<vHistogramAndTriggerPtHistogramNames.size(); k++) {


                HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
                std::cout << "analysing histogram " << hDPhiAndhTrPtNames.hDPhi << " with trigger pT histogram " << hDPhiAndhTrPtNames.hTrPt << std::endl;

                TH1D *hDPhiOS = (TH1D*)OStree->Get((hDPhiAndhTrPtNames.hDPhi).c_str());
	            TH1D *hDPhiSS = (TH1D*)SStree->Get((hDPhiAndhTrPtNames.hDPhi).c_str());
	            TH1D *hTrPtOS = (TH1D*)OStree->Get((hDPhiAndhTrPtNames.hTrPt).c_str());
	            TH1D *hTrPtSS = (TH1D*)SStree->Get((hDPhiAndhTrPtNames.hTrPt).c_str());

                // Prevent double-counting
	            if (strcmp((fileNamesOSandSS.trigger).c_str(), 
                           (fileNamesOSandSS.associateSS).c_str()) == 0) { 
                    hDPhiSS->Scale(0.5); } 


                // Calculate yield value and assign to appropriate place in vector
                Double_t yield = calculateOneYield(VERBOSE, hDPhiOS, hTrPtOS, hDPhiSS, hTrPtSS, FLAVOUR, i, j, k, 0);
                if (i >= vYields.size()) { vYields.resize(i + 1); }
                if (j >= vYields[i].size()) { vYields[i].resize(j + 1); }
                if (k >= vYields[i][j].size()) { vYields[i][j].resize(k + 1); }
                vYields[i][j][k] = yield; 
                if (VERBOSE) { 
                    std::cout << "vYields[" << i << "][" << j << "][" << k << "] = " << vYields[i][j][k] << std::endl;
                    std::cout << std::endl;
                }


                // Calculate the error on the yield by subsampling with N samples
                // Not the most efficient way, but it is straightforward and clear
                // and anyways the files are quite small so it doesn't take too long
                if (CALCULATE_ERRORS) {
                    

                    // Error estimation is independent of binning, however one needs to make sure the 
                    // yield values are within the min and max bin ranges
                    TH1D *hSubYields = new TH1D(Form("hSubYields_%s_%i%i%i", FLAVOUR, i, j, k), Form("hSubYields_%s_%i%i%i", FLAVOUR, i, j, k), 50, vYields[i][j][k]/5, vYields[i][j][k]*5);
                    TH1D *hSubRatioYields = new TH1D(Form("hSubRatioYields_%s_%i%i%i", FLAVOUR, i, j, k), Form("hSubRatioYields_%s_%i%i%i", FLAVOUR, i, j, k), 50, (vYields[i][j][k]/vYields[i][0][k])/5, (vYields[i][j][k]/vYields[i][0][k])*5);


                    for (Int_t l = 1; l < nSubSamples+1; l++) {


                        TFile *OStree_subSamples = new TFile((complete_root_dir_sub_samples + "_" + TUNE + "/" + Form("combined_root_%i",l) + "/" + fileNamesOSandSS.OS).c_str());
                        TFile *SStree_subSamples = new TFile((complete_root_dir_sub_samples + "_" + TUNE + "/" + Form("combined_root_%i",l) + "/" + fileNamesOSandSS.SS).c_str());

                        TH1D *hDPhiOS_subSamples = (TH1D*)OStree_subSamples->Get((hDPhiAndhTrPtNames.hDPhi).c_str());
	                    TH1D *hDPhiSS_subSamples = (TH1D*)SStree_subSamples->Get((hDPhiAndhTrPtNames.hDPhi).c_str());
	                    TH1D *hTrPtOS_subSamples = (TH1D*)OStree_subSamples->Get((hDPhiAndhTrPtNames.hTrPt).c_str());
	                    TH1D *hTrPtSS_subSamples = (TH1D*)SStree_subSamples->Get((hDPhiAndhTrPtNames.hTrPt).c_str());

                        Double_t subYield = calculateOneYield(VERBOSE, hDPhiOS_subSamples, hTrPtOS_subSamples, hDPhiSS_subSamples, hTrPtSS_subSamples,
                                                              FLAVOUR, i, j, k, l);
                        vSubYields[i][j][k][l] = subYield;
                        if (VERBOSE) {
                            std::cout << "vSubYields[" << i << "][" << j << "][" << k << "][" << l << "] = " << subYield << std::endl;
                            std::cout << std::endl;
                        }

                        hSubYields->Fill(subYield);
                        hSubRatioYields->Fill((vSubYields[i][j][k][l])/(vSubYields[i][0][k][l]));

                        // TODO: debug checks not appearing anymore due to memory deletion?
                        TCanvas *cTestHDPhiOS;
                        if (i==0 && j==0 && k==0 && l==1) {
                            cTestHDPhiOS = new TCanvas(Form("testHDPhiOS_%s", FLAVOUR), "testHDPhiOS",600,800);
                            cTestHDPhiOS->cd();
                            hDPhiOS_subSamples->Draw("hist");
                        }
                        if (i==0 && j==0 && k==0 && l==2) {
                            cTestHDPhiOS->cd();
                            hDPhiOS_subSamples->Draw("same hist");
                        }

                        // Free memory
                        OStree_subSamples->Close();
                        SStree_subSamples->Close();
                        // TODO: Close and delete more things? Memory issuse?
                        // Seems to automatically close histograms too?


                    } // Loop over SUBSAMPLES


                    TCanvas *cTestSubYields;
                    TCanvas *cTestSubRatioYields;
                    if (i==1 && j==4 && k==0) {
                            cTestSubYields = new TCanvas(Form("testSubYields_%s", FLAVOUR), "testSubYields",600,800);
                            cTestSubYields->cd();
                            hSubYields->Draw("hist");
                        }
                    if (i==1 && j==4 && k==0) {
                        cTestSubRatioYields = new TCanvas(Form("testSubRatioYields_%s", FLAVOUR), "testSubRatioYields",600,800);
                        cTestSubRatioYields->cd();
                        hSubRatioYields->Draw("hist");
                    }
                    Double_t yieldError = hSubYields->GetStdDev();
                    Double_t yieldRatioError = hSubRatioYields->GetStdDev();
                    if (i >= vYieldsErrors.size()) { vYieldsErrors.resize(i + 1); }
                    if (j >= vYieldsErrors[i].size()) { vYieldsErrors[i].resize(j + 1); }
                    if (k >= vYieldsErrors[i][j].size()) { vYieldsErrors[i][j].resize(k + 1); }
                    vYieldsErrors[i][j][k] = yieldError; 
                    std::cout << "vYieldsErrors[" << i << "][" << j << "][" << k << "] = " << vYieldsErrors[i][j][k] << std::endl;
                    std::cout << std::endl;
                    if (i >= vYieldsRatioErrors.size()) { vYieldsRatioErrors.resize(i + 1); }
                    if (j >= vYieldsRatioErrors[i].size()) { vYieldsRatioErrors[i].resize(j + 1); }
                    if (k >= vYieldsRatioErrors[i][j].size()) { vYieldsRatioErrors[i][j].resize(k + 1); }
                    vYieldsRatioErrors[i][j][k] = yieldRatioError; 
                    std::cout << "vYieldsRatioErrors[" << i << "][" << j << "][" << k << "] = " << vYieldsRatioErrors[i][j][k] << std::endl;
                    std::cout << std::endl;


                } // calculate errors


            } // Loop over DEPENDENCIES


            // TODO: cannot seem to draw 'test' plots for the yields anymore when this is enabled?
            // Free memory
            // OStree->Close();
            // SStree->Close();


        } // Loop over ASSOCIATES


    } // Loop over TUNES


    // TODO: make the names better
    YieldsAndErrors vYieldsAndErrors;
    vYieldsAndErrors.vYields = vYields;
    if (CALCULATE_ERRORS) { vYieldsAndErrors.vYieldsErrors = vYieldsErrors; }
    if (CALCULATE_ERRORS) { vYieldsAndErrors.vYieldsRatioErrors = vYieldsRatioErrors; }
    return vYieldsAndErrors;


} // calculateYieldsVector()


TPad* drawBalancingPlots(CONFIGS configs_from_json, const char* FLAVOUR, YieldsAndErrors vYieldsAndErrors) {


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
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { vTriggerAssociateOSandSS = configs_from_json.vBeautyTriggerAssociateOSandSS; }
    if (strcmp(FLAVOUR, "CHARM" ) == 0)  { vTriggerAssociateOSandSS = configs_from_json.vCharmTriggerAssociateOSandSS; }
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames = configs_from_json.vHistogramAndTriggerPtHistogramNames;

    Int_t nTUNES = vTUNES.size();
    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    Int_t nDependencies = vHistogramAndTriggerPtHistogramNames.size();

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


                HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
                if (VERBOSE) {
                    std::cout << "plotting histogram " << hDPhiAndhTrPtNames.hDPhi << " with trigger pT histogram " << hDPhiAndhTrPtNames.hTrPt << std::endl;
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
                cYields->cd();
                vHists[i][k]->Draw("same PE");
                if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                    cMiniPad->cd();
                    vHists[i][k]->Draw("same PE");
                }

                if (colourTUNEMap.find(TUNE) != colourTUNEMap.end()) {
                    Int_t colour = colourTUNEMap[TUNE];
                    vHists[i][k]->SetLineColor(colour);
                    if (VERBOSE) { std::cout << "Found colour: " << colour << std::endl; }
                } else {
                    if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                }

                if (lineStyleDependencyMap.find(hDPhiAndhTrPtNames.hDPhi) != lineStyleDependencyMap.end()) {
                    Int_t lineStyle = lineStyleDependencyMap[hDPhiAndhTrPtNames.hDPhi];
                    vHists[i][k]->SetLineStyle(lineStyle);
                    if (VERBOSE) { std::cout << "Found lineStyle: " << lineStyle << std::endl; }
                } else {
                    if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                }

                // TODO: move this outside loop (also for the other ones below)
                // Draw legend
                if (legend != nullptr && alreadyInLegend.find(hDPhiAndhTrPtNames.hDPhi) == alreadyInLegend.end()) {
                    if (legendEntriesMap.find(hDPhiAndhTrPtNames.hDPhi) != legendEntriesMap.end()) {
                        std::string displayName = legendEntriesMap[hDPhiAndhTrPtNames.hDPhi];
                        if (VERBOSE) { std::cout << "Found displayName: " << displayName << std::endl; }
                        legend->AddEntry(vHists[i][k], displayName.c_str(), "l");
                    } else {
                        if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                    }
                    alreadyInLegend.insert(hDPhiAndhTrPtNames.hDPhi);
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


TPad* drawBalancingPlotsTUNERatios(CONFIGS configs_from_json, const char* FLAVOUR, YieldsAndErrors vYieldsAndErrors,
                                  Int_t indexNominatorTUNE, Int_t indexDenominatorTUNE) {


    std::cout << "*** Drawing balancing plots with TUNE ratios for " << FLAVOUR;


    // Retrieve settings from configuration.json
    canvasConfigs canvasConfigs = configs_from_json.currentCanvasConfigs;
    bool VERBOSE = configs_from_json.VERBOSE;
    bool CALCULATE_ERRORS = configs_from_json.CALCULATE_ERRORS;
    std::string base_dir = configs_from_json.base_dir;
    std::vector<std::string> vTUNES = configs_from_json.vTUNES; // TODO: put the name of the tune in output for clarity?
    std::vector<TriggerAssociateOSandSS> vTriggerAssociateOSandSS;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { vTriggerAssociateOSandSS = configs_from_json.vBeautyTriggerAssociateOSandSS; }
    if (strcmp(FLAVOUR, "CHARM") == 0)  { vTriggerAssociateOSandSS = configs_from_json.vCharmTriggerAssociateOSandSS; }
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames = configs_from_json.vHistogramAndTriggerPtHistogramNames;

    std::cout << " and TUNE = " << vTUNES[indexNominatorTUNE] << "/" << vTUNES[indexDenominatorTUNE] << " ***" << std::endl;

    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    Int_t nDependencies = vHistogramAndTriggerPtHistogramNames.size();

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


            HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
            // TODO: verbose
            if (VERBOSE) { 
                std::cout << "plotting histogram " << hDPhiAndhTrPtNames.hDPhi << " with trigger pT histogram " << hDPhiAndhTrPtNames.hTrPt << std::endl;
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
            cYields->cd();
            vHists[k]->SetLineColor(kBlack);
            vHists[k]->Draw("same PE");
            if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                cMiniPad->cd();
                vHists[k]->Draw("same PE");
            }

            if (lineStyleDependencyMap.find(hDPhiAndhTrPtNames.hDPhi) != lineStyleDependencyMap.end()) {
                Int_t lineStyle = lineStyleDependencyMap[hDPhiAndhTrPtNames.hDPhi];
                vHists[k]->SetLineStyle(lineStyle);
                if (VERBOSE) { std::cout << "Found lineStyle: " << lineStyle << std::endl; }
            } else {
                if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
            }

            // Draw legend
            if (legend != nullptr && alreadyInLegend.find(hDPhiAndhTrPtNames.hDPhi) == alreadyInLegend.end()) {
                if (legendEntriesMap.find(hDPhiAndhTrPtNames.hDPhi) != legendEntriesMap.end()) {
                    std::string displayName = legendEntriesMap[hDPhiAndhTrPtNames.hDPhi];
                    if (VERBOSE) { std::cout << "Found displayName: " << displayName << std::endl; }
                    legend->AddEntry(vHists[k], displayName.c_str(), "l");
                } else {
                    if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                }
                alreadyInLegend.insert(hDPhiAndhTrPtNames.hDPhi);
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


TPad* drawBalancingBaryonMesonRatioPlots(CONFIGS configs_from_json, const char* FLAVOUR, YieldsAndErrors vYieldsAndErrors) {


    std::cout << "*** Drawing balancing baryon/meson ratio plots for " << FLAVOUR << " ***" << std::endl;


    // Retrieve settings from configuration.json
    canvasConfigs canvasConfigs = configs_from_json.currentCanvasConfigs;
    bool VERBOSE = configs_from_json.VERBOSE;
    bool CALCULATE_ERRORS = configs_from_json.CALCULATE_ERRORS;
    std::string base_dir = configs_from_json.base_dir;
    std::vector<std::string> vTUNES = configs_from_json.vTUNES;
    std::vector<TriggerAssociateOSandSS> vTriggerAssociateOSandSS;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { vTriggerAssociateOSandSS = configs_from_json.vBeautyTriggerAssociateOSandSS; }
    if (strcmp(FLAVOUR, "CHARM") == 0)  { vTriggerAssociateOSandSS = configs_from_json.vCharmTriggerAssociateOSandSS; }
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames = configs_from_json.vHistogramAndTriggerPtHistogramNames;

    Int_t nTUNES = vTUNES.size();
    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    Int_t nDependencies = vHistogramAndTriggerPtHistogramNames.size();

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


                HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
                if (VERBOSE) { 
                    std::cout << "plotting histogram " << hDPhiAndhTrPtNames.hDPhi << " with trigger pT histogram " << hDPhiAndhTrPtNames.hTrPt << std::endl;
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
                cYields->cd();
                vHists[i][j]->Draw("same PE");
                if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                    cMiniPad->cd();
                    vHists[i][j]->Draw("same PE");
                }

                hYieldsTemplate->GetXaxis()->SetBinLabel(1+k, (hDPhiAndhTrPtNames.hDPhi).c_str());

                if (colourTUNEMap.find(TUNE) != colourTUNEMap.end()) {
                    Int_t colour = colourTUNEMap[TUNE];
                    vHists[i][j]->SetLineColor(colour);
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
                        legend->AddEntry(vHists[i][j], displayName.c_str(), "l");
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


TPad* drawBalancingBaryonMesonRatioPlotsTUNERatios(CONFIGS configs_from_json, const char* FLAVOUR, YieldsAndErrors vYieldsAndErrors,
                                                  Int_t indexNominatorTUNE, Int_t indexDenominatorTUNE) {


    std::cout << "*** Drawing balancing baryon/meson ratio plots with TUNE ratios for " << FLAVOUR << " ***" << std::endl;


    // Retrieve settings from configuration.json
    canvasConfigs canvasConfigs = configs_from_json.currentCanvasConfigs;
    bool VERBOSE = configs_from_json.VERBOSE;
    bool CALCULATE_ERRORS = configs_from_json.CALCULATE_ERRORS;
    std::string base_dir = configs_from_json.base_dir;
    std::vector<std::string> vTUNES = configs_from_json.vTUNES;
    std::vector<TriggerAssociateOSandSS> vTriggerAssociateOSandSS;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) { vTriggerAssociateOSandSS = configs_from_json.vBeautyTriggerAssociateOSandSS; }
    if (strcmp(FLAVOUR, "CHARM") == 0)  { vTriggerAssociateOSandSS = configs_from_json.vCharmTriggerAssociateOSandSS; }
    std::vector<HistogramAndTriggerPtHistogramNames> vHistogramAndTriggerPtHistogramNames = configs_from_json.vHistogramAndTriggerPtHistogramNames;

    std::cout << " and TUNE = " << vTUNES[indexNominatorTUNE] << "/" << vTUNES[indexDenominatorTUNE] << " ***" << std::endl;

    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    Int_t nDependencies = vHistogramAndTriggerPtHistogramNames.size();

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


            HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
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
            cYields->cd();
            vHists[j]->SetLineColor(kBlack);
            vHists[j]->Draw("same PE");
            if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                cMiniPad->cd();
                vHists[j]->Draw("same PE");
            }

            hYieldsTemplate->GetXaxis()->SetBinLabel(1+k, (hDPhiAndhTrPtNames.hDPhi).c_str());

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
                legend->AddEntry(vHists[j], displayName.c_str(), "l");
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
int improvedPlotting(const char* configuration) {

    // Read configurations defined by user in configuration.json
    CONFIGS configs_from_json = readConfig(configuration);
    bool VERBOSE = configs_from_json.VERBOSE;

    // Calculate the 3D yield vector
    // TODO: define this below in loop
    YieldsAndErrors vYields; // used in loop over canvas settings
    YieldsAndErrors vYieldsBeauty;
    YieldsAndErrors vYieldsCharm;
    vYieldsBeauty = calculateYieldsVector(configs_from_json,"BEAUTY");
    vYieldsCharm =  calculateYieldsVector(configs_from_json,"CHARM");

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
        Int_t indexNominatorTUNE = canvasConfigs.indexNominatorTUNE;
        Int_t indexDenominatorTUNE = canvasConfigs.indexDenominatorTUNE;
        // TODO: alternatively, just don't define vYieldsBeauty above, 
        // it's a bit redundant now..
        // TODO: add more error messages and checks
        if (strcmp(FLAVOUR.c_str(), "BEAUTY") == 0) { vYields = vYieldsBeauty; }
        if (strcmp(FLAVOUR.c_str(), "CHARM" ) == 0) { vYields = vYieldsCharm;  }

        if (strcmp(drawFunctionToUse.c_str(), "drawBalancingPlots") == 0) { 
            TPad *cMiniPad = drawBalancingPlots(configs_from_json, FLAVOUR.c_str(), vYields); 
            cMiniCanvasMap[canvasName] = cMiniPad;
        }
        if (strcmp(drawFunctionToUse.c_str(), "drawBalancingPlotsTUNERatios") == 0) { 
            TPad *cMiniPad = drawBalancingPlotsTUNERatios(configs_from_json,FLAVOUR.c_str(), vYields, indexNominatorTUNE, indexDenominatorTUNE);
            cMiniCanvasMap[canvasName] = cMiniPad; 
        }
        if (strcmp(drawFunctionToUse.c_str(), "drawBalancingBaryonMesonRatioPlots") == 0) { 
            TPad *cMiniPad = drawBalancingBaryonMesonRatioPlots(configs_from_json,FLAVOUR.c_str(), vYields);
            cMiniCanvasMap[canvasName] = cMiniPad; 
        }
        if (strcmp(drawFunctionToUse.c_str(), "drawBalancingBaryonMesonRatioPlotsTUNERatios") == 0) { 
            TPad *cMiniPad = drawBalancingBaryonMesonRatioPlotsTUNERatios(configs_from_json,FLAVOUR.c_str(), vYields, indexNominatorTUNE, indexDenominatorTUNE); 
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
