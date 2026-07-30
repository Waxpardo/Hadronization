// improvedPlotting_THnSparse.C
// Paul Veen (paul.veen@cern.ch)

// C headers
#include <iostream>
#include <fstream>
#include <algorithm>
#include <array>
#include <random>
#include <cmath>
#include <cstring>
#include <cstdlib>
#include <filesystem>
#include <map>
#include <set>
#include <stdexcept>
#include <sstream>
#include <limits>
#include <memory>
#include <vector>

#if defined(__GLIBC__)
#include <malloc.h>
#endif

// ROOT headers
#include "TFile.h"
#include "TH1D.h"
#include "THnSparse.h"
#include "TObjString.h"
#include "TParameter.h"
#include "TSystem.h"
#include "TCanvas.h"
#include "TString.h" // TODO: can use this for the legend entry names?
#include <TLegend.h>

#include "../AnalysisScripts/GeneratedPairRegistry.h"
#include "../AnalysisScripts/AssociateOriginCategoryContract.h"
#include "../SimulationScripts/Sha256.h"
#include "MultiplicityBoundaryUtils.h"
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

// TODO: add many more plots and options to draw them (e.g. delta phi, delta phi delta eta, angular correlations, multiplciity spectra, kinematics, etc.) and add them to PDF

// TODO: display_name is used now.. maybe better to use the binLabel everywhere?

// Define a structure to hold OS and SS correlation file names

struct TriggerAssociateOSandSS {
    std::string trigger;
    std::string associateOS;
    std::string associateSS;
    std::string OS;
    std::string SS;
    Int_t triggerPdg = 0;
    Int_t associateOSPdg = 0;
    Int_t associateSSPdg = 0;
    Int_t referenceMesonPdg = 0;
    bool legacyRegistryFilenames = false;
};

struct HistogramAndTriggerPtHistogramNames {
    std::string hDPhi;
    std::string hTrPt;
};

enum class PairSelectionProjectionMode {
    kUpstreamSelectedV2,
    kLegacyPlotRecutsV1
};

const char* PairSelectionProjectionModeName(
    PairSelectionProjectionMode mode
) {
    switch (mode) {
        case PairSelectionProjectionMode::kUpstreamSelectedV2:
            return "upstream_selected_v2";
        case PairSelectionProjectionMode::kLegacyPlotRecutsV1:
            return "tagged_legacy_recuts_v1";
    }
    return "unknown_pair_selection_mode";
}

bool IsLegacyPairSelectionMode(PairSelectionProjectionMode mode) {
    return mode != PairSelectionProjectionMode::kUpstreamSelectedV2;
}

struct PairInputSelectionContract {
    std::string mode;
    std::string legacyMetadataFreeCompleteRootTag;
    std::string histogramPtEtaFieldSemantics;
    std::string analysisSchema;
    std::string analysisImplementation;
    std::string analysisVersion;
    std::string analysisProfile;
    std::string selectorVersion;
    std::string pairCombinatoricsMode;
    Double_t triggerPtMinExclusive;
    Double_t associatePtMinExclusive;
    Double_t etaAbsMaxInclusive;
    Double_t sameSignPairFactor;
    std::string ptUpperSelection;
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
    std::size_t referenceAssociateIndex = 0;
    Int_t referenceMesonPdg = 0;
};


struct YieldsAndErrorsMap {
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYields;
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYieldsErrors;
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYieldsRatioErrors;
    std::map<std::string, std::size_t> mapReferenceAssociateIndex;
    std::map<std::string, Int_t> mapReferenceMesonPdg;
    Int_t subsampleCoverageFailures = 0;
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
    std::vector<std::string> vBinsToIgnore; // bins omitted from this canvas
    std::vector<Int_t> vIndexNominatorTUNES; // used for TUNE ratio plots, e.g. MONASH/JUNCTIONS to study enhancement explicitly
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
    std::string PAIR_COMBINATORICS_MODE;
    Double_t SAME_SIGN_PAIR_FACTOR;
    PairInputSelectionContract PAIR_INPUT_SELECTION_CONTRACT;
    bool DRAW_CORRELATION_PLOTS;
    bool SUBSAMPLE_COVERAGE_AUDIT;
    std::string base_dir;
    std::vector<std::string> vSubsampleErrorBinsToExclude;
    std::string configurationPath;
    std::string configurationSha256;
    std::string multiplicityBoundaryReceiptPath;
    json multiplicityBoundaryReceipt;

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
    std::map<std::string, std::map<double, double>>
        multiplicityPercentileThresholdsByTune;

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

void ReleaseUnusedHeap() {
#if defined(__GLIBC__)
    // Deletes release ROOT's sparse/projection buffers, but glibc may retain
    // the freed multi-GB arenas. Return them to the OS between pair files so a
    // multi-tune batch job remains within the worker memory limit.
    malloc_trim(0);
#endif
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

const Hadronization::PairDefinition& PairDefinitionForConfiguredFile(
    const std::string& fileName,
    const std::string& sector,
    const std::string& heavySign,
    const std::string& context
) {
    const Hadronization::PairDefinition* match = nullptr;
    for (const auto& definition : Hadronization::kPairDefinitions) {
        if (definition.filename != fileName ||
            definition.sector != sector ||
            definition.heavySign != heavySign) {
            continue;
        }
        if (match) {
            throw std::runtime_error(
                "Pair registry contains a duplicate " + heavySign +
                " definition for configured file '" + fileName +
                "' in " + context);
        }
        match = &definition;
    }
    if (!match) {
        throw std::runtime_error(
            "No exact " + sector + "/" + heavySign +
            " pair-registry definition for configured file '" + fileName +
            "' in " + context);
    }
    return *match;
}

TriggerAssociateOSandSS ResolveConfiguredPairFromRegistry(
    const std::string& sector,
    const std::string& groupTrigger,
    const std::string& configuredTrigger,
    const std::string& associateOS,
    const std::string& associateSS,
    const std::string& osFile,
    const std::string& ssFile
) {
    const std::string context =
        sector + " trigger group '" + groupTrigger + "'";
    if (configuredTrigger != groupTrigger) {
        throw std::runtime_error(
            "Configured pair trigger '" + configuredTrigger +
            "' differs from its group trigger '" + groupTrigger +
            "' in " + context);
    }
    const auto& osDefinition = PairDefinitionForConfiguredFile(
        osFile, sector, "OS", context);
    const auto& ssDefinition = PairDefinitionForConfiguredFile(
        ssFile, sector, "SS", context);
    if (osDefinition.triggerPdg != ssDefinition.triggerPdg) {
        throw std::runtime_error(
            "Configured OS/SS files have different trigger PDGs in " +
            context + ": " + osFile + " / " + ssFile);
    }
    if (osDefinition.associatePdg != -ssDefinition.associatePdg) {
        throw std::runtime_error(
            "Configured OS/SS files are not the signed associate pair in " +
            context + ": " + osFile + " / " + ssFile);
    }
    if (osDefinition.referenceMesonPdg !=
        ssDefinition.referenceMesonPdg) {
        throw std::runtime_error(
            "Configured OS/SS files disagree on reference_meson_pdg in " +
            context + ": " + osFile + " / " + ssFile);
    }

    TriggerAssociateOSandSS configured;
    configured.trigger = configuredTrigger;
    configured.associateOS = associateOS;
    configured.associateSS = associateSS;
    configured.OS = osFile;
    configured.SS = ssFile;
    configured.triggerPdg = osDefinition.triggerPdg;
    configured.associateOSPdg = osDefinition.associatePdg;
    configured.associateSSPdg = ssDefinition.associatePdg;
    configured.referenceMesonPdg = osDefinition.referenceMesonPdg;
    configured.legacyRegistryFilenames =
        osDefinition.legacyFilename && ssDefinition.legacyFilename;
    return configured;
}

struct ReferenceAssociateSelection {
    std::size_t index;
    Int_t pdg;
};

ReferenceAssociateSelection ResolveReferenceAssociateSelection(
    const std::vector<TriggerAssociateOSandSS>& configurations,
    const std::string& context
) {
    if (configurations.empty()) {
        throw std::runtime_error(
            "Cannot resolve reference meson from an empty trigger group: " +
            context);
    }
    const Int_t triggerPdg = configurations.front().triggerPdg;
    const Int_t referencePdg =
        configurations.front().referenceMesonPdg;
    if (triggerPdg == 0 || referencePdg == 0) {
        throw std::runtime_error(
            "Unresolved pair-registry PDG identity in " + context);
    }

    std::set<std::string> osFiles;
    std::set<std::string> ssFiles;
    std::set<Int_t> osAssociates;
    std::vector<std::size_t> matches;
    for (std::size_t index = 0; index < configurations.size(); ++index) {
        const auto& configured = configurations[index];
        if (configured.triggerPdg != triggerPdg ||
            configured.referenceMesonPdg != referencePdg) {
            throw std::runtime_error(
                "Configured associates disagree on trigger/reference PDG in " +
                context);
        }
        if (!osFiles.insert(configured.OS).second ||
            !ssFiles.insert(configured.SS).second ||
            !osAssociates.insert(configured.associateOSPdg).second) {
            throw std::runtime_error(
                "Duplicate configured pair identity in " + context);
        }
        if (configured.associateOSPdg == referencePdg) {
            matches.push_back(index);
        }
    }
    if (matches.size() != 1) {
        throw std::runtime_error(
            Form("Expected exactly one configured signed reference meson "
                 "PDG %d in %s, found %zu",
                 referencePdg, context.c_str(), matches.size()));
    }
    return {matches.front(), referencePdg};
}

std::vector<Int_t> ReferenceFirstAssociateOrder(
    std::size_t numberOfAssociates,
    std::size_t referenceIndex
) {
    if (referenceIndex >= numberOfAssociates) {
        throw std::runtime_error(
            "Reference-associate index is outside configured associate range");
    }
    std::vector<Int_t> order;
    order.reserve(numberOfAssociates);
    order.push_back(static_cast<Int_t>(referenceIndex));
    for (std::size_t index = 0; index < numberOfAssociates; ++index) {
        if (index != referenceIndex) {
            order.push_back(static_cast<Int_t>(index));
        }
    }
    return order;
}

using MultiplicityHistogramIdentity =
    HadronizationMultiplicity::HistogramIdentity;

MultiplicityHistogramIdentity CaptureMultiplicityHistogramIdentity(
    TH1D* histogram,
    const std::string& context
) {
    return HadronizationMultiplicity::CaptureHistogramIdentity(
        histogram, context);
}

void RequireIdenticalMultiplicityHistogram(
    const MultiplicityHistogramIdentity& expected,
    const MultiplicityHistogramIdentity& observed,
    const std::string& expectedContext,
    const std::string& observedContext
) {
    HadronizationMultiplicity::RequireIdenticalHistogram(
        expected, observed, expectedContext, observedContext);
}

bool PairSelectionContractAllowsV2(
    const PairInputSelectionContract& contract
) {
    return contract.mode == "v2_metadata_or_tagged_legacy_recuts_v1" ||
           contract.mode == "v2_metadata_only_v1";
}

bool PairSelectionContractAllowsLegacy(
    const PairInputSelectionContract& contract
) {
    return contract.mode == "v2_metadata_or_tagged_legacy_recuts_v1" ||
           contract.mode == "tagged_legacy_recuts_only_v1";
}

std::string ReadSelectionMetadataString(
    TFile* file,
    const char* objectName,
    const std::string& filePath
) {
    TObjString* object = dynamic_cast<TObjString*>(file->Get(objectName));
    if (!object) {
        throw std::runtime_error(
            "Missing or wrong-type selection metadata '" +
            std::string(objectName) + "' in " + filePath);
    }
    return object->GetString().Data();
}

Double_t ReadSelectionMetadataDouble(
    TFile* file,
    const char* objectName,
    const std::string& filePath
) {
    TParameter<double>* object =
        dynamic_cast<TParameter<double>*>(file->Get(objectName));
    if (!object || !std::isfinite(object->GetVal())) {
        throw std::runtime_error(
            "Missing, wrong-type, or non-finite selection metadata '" +
            std::string(objectName) + "' in " + filePath);
    }
    return object->GetVal();
}

void RequireSelectionMetadataString(
    TFile* file,
    const char* objectName,
    const std::string& expected,
    const std::string& filePath
) {
    const std::string actual =
        ReadSelectionMetadataString(file, objectName, filePath);
    if (actual != expected) {
        throw std::runtime_error(
            "Selection metadata mismatch for '" + std::string(objectName) +
            "' in " + filePath + ": expected '" + expected +
            "', got '" + actual + "'");
    }
}

void RequireSelectionMetadataDouble(
    TFile* file,
    const char* objectName,
    Double_t expected,
    const std::string& filePath
) {
    const Double_t actual =
        ReadSelectionMetadataDouble(file, objectName, filePath);
    const Double_t scale =
        std::max({1.0, std::abs(expected), std::abs(actual)});
    if (std::abs(actual - expected) > 1e-12 * scale) {
        throw std::runtime_error(
            Form("Selection metadata mismatch for '%s' in %s: "
                 "expected %.17g, got %.17g",
                 objectName, filePath.c_str(), expected, actual));
    }
}

Int_t ReadPairIdentityMetadataInt(
    TFile* file,
    const char* objectName,
    const std::string& filePath
) {
    TParameter<int>* object =
        dynamic_cast<TParameter<int>*>(file->Get(objectName));
    if (!object) {
        throw std::runtime_error(
            "Missing or wrong-type pair-identity metadata '" +
            std::string(objectName) + "' in " + filePath);
    }
    return object->GetVal();
}

void RequirePairIdentityMetadataInt(
    TFile* file,
    const char* objectName,
    Int_t expected,
    const std::string& filePath
) {
    const Int_t actual =
        ReadPairIdentityMetadataInt(file, objectName, filePath);
    if (actual != expected) {
        throw std::runtime_error(
            Form("Pair-identity metadata mismatch for '%s' in %s: "
                 "expected %d, got %d",
                 objectName, filePath.c_str(), expected, actual));
    }
}

void ValidateConfiguredPairFileIdentity(
    TFile* file,
    PairSelectionProjectionMode selectionMode,
    const PairInputSelectionContract& contract,
    const std::string& activeCompleteRootTag,
    const TriggerAssociateOSandSS& configured,
    bool isOS,
    const std::string& sector,
    const std::string& filePath
) {
    if (!file) {
        throw std::runtime_error(
            "Cannot validate pair identity in null file: " + filePath);
    }
    const std::array<const char*, 6> identityObjects = {
        "pair_registry_sha256",
        "heavy_sector",
        "heavy_sign",
        "trigger_pdg",
        "associate_pdg",
        "reference_meson_pdg"
    };
    std::size_t present = 0;
    for (const char* objectName : identityObjects) {
        if (file->GetListOfKeys() &&
            file->GetListOfKeys()->FindObject(objectName)) {
            ++present;
        }
    }

    if (IsLegacyPairSelectionMode(selectionMode)) {
        if (!PairSelectionContractAllowsLegacy(contract) ||
            activeCompleteRootTag !=
                contract.legacyMetadataFreeCompleteRootTag ||
            !configured.legacyRegistryFilenames) {
            throw std::runtime_error(
                "Pair-identity metadata-free fallback is forbidden outside "
                "the exact tagged legacy registry mapping: " + filePath);
        }
        if (present != 0) {
            throw std::runtime_error(
                Form("Tagged legacy pair file must be identity-metadata-free; "
                     "found %zu/%zu identity objects in %s",
                     present, identityObjects.size(), filePath.c_str()));
        }
        return;
    }

    if (present != identityObjects.size()) {
        throw std::runtime_error(
            Form("Canonical pair file has incomplete signed identity "
                 "metadata: found %zu/%zu objects in %s",
                 present, identityObjects.size(), filePath.c_str()));
    }
    RequireSelectionMetadataString(
        file, "pair_registry_sha256",
        std::string(Hadronization::kPairRegistrySha256), filePath);
    RequireSelectionMetadataString(
        file, "heavy_sector", sector, filePath);
    RequireSelectionMetadataString(
        file, "heavy_sign", isOS ? "OS" : "SS", filePath);
    RequirePairIdentityMetadataInt(
        file, "trigger_pdg", configured.triggerPdg, filePath);
    RequirePairIdentityMetadataInt(
        file, "associate_pdg",
        isOS ? configured.associateOSPdg : configured.associateSSPdg,
        filePath);
    RequirePairIdentityMetadataInt(
        file, "reference_meson_pdg",
        configured.referenceMesonPdg, filePath);
}

PairSelectionProjectionMode ValidatePairInputSelectionContract(
    TFile* file,
    const PairInputSelectionContract& contract,
    const std::string& activeCompleteRootTag,
    const std::string& filePath
) {
    if (!file) {
        throw std::runtime_error(
            "Cannot validate pair selection metadata in null file: " +
            filePath);
    }

    const std::array<const char*, 12> requiredV2Objects = {
        "analysis_schema",
        "analysis_implementation",
        "analysis_version",
        "analysis_profile",
        "associate_origin_category_schema",
        "associate_origin_category_labels",
        "selector_version",
        "pair_combinatorics_mode",
        "trigger_pt_min_exclusive",
        "associate_pt_min_exclusive",
        "eta_abs_max_inclusive",
        "same_sign_pair_factor"
    };
    std::size_t presentV2Objects = 0;
    for (const char* objectName : requiredV2Objects) {
        if (file->GetListOfKeys() &&
            file->GetListOfKeys()->FindObject(objectName)) {
            ++presentV2Objects;
        }
    }

    if (presentV2Objects == 0) {
        if (!PairSelectionContractAllowsLegacy(contract)) {
            throw std::runtime_error(
                "Metadata-free pair file is forbidden by selection contract "
                "mode '" + contract.mode + "': " + filePath);
        }
        if (activeCompleteRootTag !=
            contract.legacyMetadataFreeCompleteRootTag) {
            throw std::runtime_error(
                "Metadata-free pair file is allowed only for the explicitly "
                "tagged legacy input '" +
                contract.legacyMetadataFreeCompleteRootTag +
                "', but active complete-root tag is '" +
                activeCompleteRootTag + "': " + filePath);
        }
        return PairSelectionProjectionMode::kLegacyPlotRecutsV1;
    }

    if (presentV2Objects != requiredV2Objects.size()) {
        throw std::runtime_error(
            Form("Partial v2 pair-selection metadata in %s: found %zu/%zu "
                 "required objects; refusing legacy fallback",
                 filePath.c_str(), presentV2Objects,
                 requiredV2Objects.size()));
    }
    if (!PairSelectionContractAllowsV2(contract)) {
        throw std::runtime_error(
            "V2 pair metadata is forbidden by selection contract mode '" +
            contract.mode + "': " + filePath);
    }

    RequireSelectionMetadataString(
        file, "analysis_schema", contract.analysisSchema, filePath);
    RequireSelectionMetadataString(
        file, "analysis_implementation", contract.analysisImplementation,
        filePath);
    RequireSelectionMetadataString(
        file, "analysis_version", contract.analysisVersion, filePath);
    RequireSelectionMetadataString(
        file, "analysis_profile", contract.analysisProfile, filePath);
    RequireSelectionMetadataString(
        file, "associate_origin_category_schema",
        std::string(Hadronization::kAssociateOriginCategorySchema),
        filePath);
    RequireSelectionMetadataString(
        file, "associate_origin_category_labels",
        std::string(Hadronization::kAssociateOriginCategoryLabels),
        filePath);
    RequireSelectionMetadataString(
        file, "selector_version", contract.selectorVersion, filePath);
    RequireSelectionMetadataString(
        file, "pair_combinatorics_mode",
        contract.pairCombinatoricsMode, filePath);
    RequireSelectionMetadataDouble(
        file, "trigger_pt_min_exclusive",
        contract.triggerPtMinExclusive, filePath);
    RequireSelectionMetadataDouble(
        file, "associate_pt_min_exclusive",
        contract.associatePtMinExclusive, filePath);
    RequireSelectionMetadataDouble(
        file, "eta_abs_max_inclusive",
        contract.etaAbsMaxInclusive, filePath);
    RequireSelectionMetadataDouble(
        file, "same_sign_pair_factor",
        contract.sameSignPairFactor, filePath);

    // The exact v2 schema above declares no upper-pT selection. Reject
    // unversioned attempts to introduce one rather than silently applying a
    // second, incompatible selection in the plotting layer.
    const std::array<const char*, 8> forbiddenUpperPtObjects = {
        "trigger_pt_max",
        "trigger_pt_max_inclusive",
        "trigger_pt_max_exclusive",
        "associate_pt_max",
        "associate_pt_max_inclusive",
        "associate_pt_max_exclusive",
        "trigger_pt_upper_selection",
        "associate_pt_upper_selection"
    };
    for (const char* objectName : forbiddenUpperPtObjects) {
        if (file->GetListOfKeys() &&
            file->GetListOfKeys()->FindObject(objectName)) {
            throw std::runtime_error(
                "Unexpected upper-pT selection metadata '" +
                std::string(objectName) + "' in v2 pair file " + filePath);
        }
    }
    if (contract.ptUpperSelection != "none") {
        throw std::runtime_error(
            "V2 pair-selection contract must declare pt_upper_selection="
            "'none'");
    }

    return PairSelectionProjectionMode::kUpstreamSelectedV2;
}

void RequireMatchingPairSelectionModes(
    PairSelectionProjectionMode first,
    PairSelectionProjectionMode second,
    const std::string& context
) {
    if (first != second) {
        throw std::runtime_error(
            "Mixed pair-selection modes in " + context + ": " +
            PairSelectionProjectionModeName(first) + " versus " +
            PairSelectionProjectionModeName(second));
    }
}

void ValidatePairCombinatoricsForSelectionMode(
    PairSelectionProjectionMode selectionMode,
    const std::string& configuredMode,
    Double_t configuredSameSignFactor,
    const PairInputSelectionContract& contract,
    const std::string& filePath
) {
    const bool factorIsOne =
        std::isfinite(configuredSameSignFactor) &&
        std::abs(configuredSameSignFactor - 1.0) <= 1e-12;
    const bool factorIsHalf =
        std::isfinite(configuredSameSignFactor) &&
        std::abs(configuredSameSignFactor - 0.5) <= 1e-12;
    if (selectionMode ==
        PairSelectionProjectionMode::kUpstreamSelectedV2) {
        if (configuredMode != "ordered_conditional_v1" ||
            !factorIsOne ||
            contract.pairCombinatoricsMode !=
                "ordered_conditional_v1" ||
            std::abs(contract.sameSignPairFactor - 1.0) > 1e-12) {
            throw std::runtime_error(
                "Canonical v2 pair input requires "
                "pair_combinatorics_mode=ordered_conditional_v1 and "
                "same_sign_pair_factor=1.0: " + filePath);
        }
        return;
    }
    if (configuredMode != "legacy_identical_ss_half_v1" ||
        !factorIsHalf ||
        !PairSelectionContractAllowsLegacy(contract)) {
        throw std::runtime_error(
            "Tagged metadata-free legacy input requires the "
            "explicit diagnostic mode "
            "pair_combinatorics_mode=legacy_identical_ss_half_v1 and "
            "same_sign_pair_factor=0.5; refusing silent reinterpretation "
            "under the canonical ordered convention: " + filePath);
    }
}

void CloseAndDeleteInputFile(TFile*& file) {
    if (!file) { return; }
    // TFile::Close() does not necessarily destroy objects materialised by
    // Get(). Delete the read-only in-memory object list explicitly so the
    // large THnSparse buffers do not accumulate across pairs and tunes.
    if (file->GetList()) { file->GetList()->Delete(); }
    file->Close();
    delete file;
    file = nullptr;
}

template <typename TObjectType>
void DeleteInputObject(TFile* file, TObjectType*& object) {
    if (!object) { return; }
    if (file && file->GetList()) { file->GetList()->Remove(object); }
    delete object;
    object = nullptr;
}


// Derive the histograms (delta phi and trigger pt) from the THnSparse, including user-defined cuts
// Pay attention that the OS and SS histograms need to have the same amount of bins!
void ValidateProjectionCuts(
    const BinsFromTHnSparse& cuts,
    PairSelectionProjectionMode selectionMode
) {
    const std::array<Double_t, 6> alwaysActiveValues = {
        cuts.triggerPhiMin, cuts.triggerPhiMax,
        cuts.assocPhiMin, cuts.assocPhiMax,
        cuts.multiplicityMin, cuts.multiplicityMax
    };
    if (!std::all_of(alwaysActiveValues.begin(), alwaysActiveValues.end(),
                     [](Double_t value) { return std::isfinite(value); })) {
        throw std::runtime_error("non-finite active projection cut");
    }
    if (cuts.multiplicityMin > cuts.multiplicityMax) {
        throw std::runtime_error("inverted multiplicity projection cut");
    }

    const std::array<Double_t, 8> legacyKinematicValues = {
        cuts.triggerEtaMin, cuts.triggerEtaMax,
        cuts.assocEtaMin, cuts.assocEtaMax,
        cuts.triggerPtMin, cuts.triggerPtMax,
        cuts.assocPtMin, cuts.assocPtMax
    };
    if (IsLegacyPairSelectionMode(selectionMode)) {
        if (!std::all_of(
                legacyKinematicValues.begin(),
                legacyKinematicValues.end(),
                [](Double_t value) { return std::isfinite(value); })) {
            throw std::runtime_error(
                "non-finite legacy pT/eta projection cut");
        }
        if (cuts.triggerEtaMin > cuts.triggerEtaMax ||
            cuts.assocEtaMin > cuts.assocEtaMax ||
            cuts.triggerPtMin > cuts.triggerPtMax ||
            cuts.assocPtMin > cuts.assocPtMax) {
            throw std::runtime_error(
                "inverted legacy pT/eta projection cut");
        }
    }
    // Paul-compatible pair objects retain delta-phi but not the two
    // individual azimuths. The checked-in paper configs use the full
    // individual-phi range. Reject a narrower request instead of applying it
    // only to the trigger denominator.
    constexpr Double_t phiTolerance = 1e-6;
    if (cuts.triggerPhiMin > -M_PI + phiTolerance ||
        cuts.triggerPhiMax < M_PI - phiTolerance ||
        cuts.assocPhiMin > -M_PI + phiTolerance ||
        cuts.assocPhiMax < M_PI - phiTolerance) {
        throw std::runtime_error(
            "individual trigger/associate phi cuts are unsupported by the "
            "current pair-object schema");
    }
}


TH1D* GetCorrelationHistograms(
    THnSparseD* hCorrelations,
    const BinsFromTHnSparse& cuts,
    PairSelectionProjectionMode selectionMode,
    const TString& suffix = ""
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
    ValidateProjectionCuts(cuts, selectionMode);

    // Reset axes
    for (int i = 0; i < hCorrelations->GetNdimensions(); ++i) { hCorrelations->GetAxis(i)->SetRange(); }

    if (selectionMode ==
        PairSelectionProjectionMode::kLegacyPlotRecutsV1) {
        // Match Paul's stable-main legacy projection: apply the configured
        // trigger and associate pT/eta cuts to the correlation numerator.
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
    }

    std::cout << "--> pair selection mode "
              << PairSelectionProjectionModeName(selectionMode)
              << "; applying multiplicity cut from "
              << cuts.multiplicityMin << " to "
              << cuts.multiplicityMax << std::endl;

    hCorrelations->GetAxis(6)->SetRangeUser(
        cuts.multiplicityMin,
        cuts.multiplicityMax
    );

    TH1D* hDPhi = (TH1D*)hCorrelations->Projection(0, "E");
    hDPhi->SetDirectory(nullptr);
    hDPhi->SetName(Form("hDPhi%s", suffix.Data()));

    return hDPhi;
}


// Derive the trigger pt histogram from the trigger kinematics THnSparse, including user-defined cuts
// This histogram is then used for normalisation of the hDPhi histogram
// Pay attention that the OS and SS histograms need to have the same amount of bins!
TH1D* GetTriggerPtHistograms(
    THnSparseD* hTrKinematics,
    const BinsFromTHnSparse& cuts,
    PairSelectionProjectionMode selectionMode,
    const TString& suffix = ""
) {
    // THnSparse hCorrelations: (careful: the 'trigger' and 'associate' refer to the pairs)
        // 0 = phi
        // 1 = eta
        // 2 = pt
        // 3 = Multiplicity

    if (!hTrKinematics) {
        throw std::runtime_error("Cannot project trigger pT: hTrKinematics is null");
    }
    ValidateProjectionCuts(cuts, selectionMode);

    // Reset axes
    for (int i = 0; i < hTrKinematics->GetNdimensions(); ++i) { hTrKinematics->GetAxis(i)->SetRange(); }

    if (selectionMode ==
        PairSelectionProjectionMode::kLegacyPlotRecutsV1) {
        hTrKinematics->GetAxis(0)->SetRangeUser(
            cuts.triggerPhiMin,
            cuts.triggerPhiMax
        );

        hTrKinematics->GetAxis(1)->SetRangeUser(
            cuts.triggerEtaMin,
            cuts.triggerEtaMax
        );

        hTrKinematics->GetAxis(2)->SetRangeUser(
            cuts.triggerPtMin,
            cuts.triggerPtMax
        );
    }

    std::cout << "--> pair selection mode "
              << PairSelectionProjectionModeName(selectionMode)
              << "; applying multiplicity cut from "
              << cuts.multiplicityMin << " to "
              << cuts.multiplicityMax << std::endl;

    hTrKinematics->GetAxis(3)->SetRangeUser(
        cuts.multiplicityMin,
        cuts.multiplicityMax
    );

    TH1D* hTrPt = (TH1D*)hTrKinematics->Projection(2, "E");
    hTrPt->SetDirectory(nullptr);
    hTrPt->SetName(Form("hTrPt%s", suffix.Data()));

    return hTrPt;
}


// Helper function to calculate multiplicity cuts using multiplicity percentiles 
double GetMultiplicityThreshold(
    TH1D* hMult,
    double percentile
) {
    return static_cast<double>(
        HadronizationMultiplicity::ThresholdForPercentile(
            hMult, percentile, "multiplicity-threshold calculation"));
}

std::pair<double, double> GetDiscreteMultiplicityRange(
    const std::map<double, double>& thresholds,
    double lowActivityPercentile,
    double highActivityPercentile
) {
    std::map<double, int> integerThresholds;
    for (const auto& [percentile, threshold] : thresholds) {
        const double rounded = std::round(threshold);
        if (!std::isfinite(threshold) ||
            std::abs(threshold - rounded) > 1e-9) {
            throw std::runtime_error(
                "frozen multiplicity threshold is not an integer Nch");
        }
        integerThresholds[percentile] = static_cast<int>(rounded);
    }
    const auto range = HadronizationMultiplicity::DiscreteClassRange(
        integerThresholds, lowActivityPercentile,
        highActivityPercentile);
    return {
        static_cast<double>(range.first),
        static_cast<double>(range.second)};
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

void WriteMultiplicityBoundaryReceipt(const CONFIGS& configs) {
    if (configs.multiplicityBoundaryReceiptPath.empty() ||
        !configs.multiplicityBoundaryReceipt.is_object() ||
        !configs.multiplicityBoundaryReceipt.contains("tunes")) {
        throw std::runtime_error(
            "Multiplicity-boundary receipt was not frozen");
    }
    const std::string outputDirectory =
        ParentPath(configs.multiplicityBoundaryReceiptPath);
    if (outputDirectory.empty() ||
        (gSystem->mkdir(outputDirectory.c_str(), true) != 0 &&
         gSystem->AccessPathName(outputDirectory.c_str()))) {
        throw std::runtime_error(
            "Could not create multiplicity-boundary receipt directory: " +
            outputDirectory);
    }

    json receipt = configs.multiplicityBoundaryReceipt;
    receipt["completion_status"] = "PASS";
    receipt["plotter_source_sha256"] =
        Hadronization::Sha256FileHex(
            JoinPath({FindHadronizationBase(),
                      "PlottingScripts",
                      "improvedPlotting_THnSparse.C"}));
    receipt["boundary_utility_sha256"] =
        Hadronization::Sha256FileHex(
            JoinPath({FindHadronizationBase(),
                      "PlottingScripts",
                      "MultiplicityBoundaryUtils.h"}));
    const std::string canonicalPayload = receipt.dump();
    receipt["payload_sha256"] =
        Hadronization::Sha256Hex(canonicalPayload);
    const std::string serializedReceipt = receipt.dump(2) + "\n";

    const std::filesystem::path finalPath(
        configs.multiplicityBoundaryReceiptPath);
    if (std::filesystem::exists(finalPath) ||
        std::filesystem::is_symlink(finalPath)) {
        if (std::filesystem::is_symlink(finalPath) ||
            !std::filesystem::is_regular_file(finalPath)) {
            throw std::runtime_error(
                "Existing multiplicity-boundary receipt is not a regular "
                "file: " + configs.multiplicityBoundaryReceiptPath);
        }
        std::ifstream existing(configs.multiplicityBoundaryReceiptPath);
        const std::string existingBytes(
            (std::istreambuf_iterator<char>(existing)),
            std::istreambuf_iterator<char>());
        if (!existing.good() && !existing.eof()) {
            throw std::runtime_error(
                "Could not read existing multiplicity-boundary receipt: " +
                configs.multiplicityBoundaryReceiptPath);
        }
        if (existingBytes != serializedReceipt) {
            throw std::runtime_error(
                "Existing multiplicity-boundary receipt differs; refusing "
                "to overwrite a frozen publication definition: " +
                configs.multiplicityBoundaryReceiptPath);
        }
        std::cout
            << "MULTIPLICITY_BOUNDARY_RECEIPT"
            << " path=" << configs.multiplicityBoundaryReceiptPath
            << " payload_sha256="
            << receipt.at("payload_sha256").get<std::string>()
            << " tune_count=" << receipt.at("tunes").size()
            << " status=REUSED_IDENTICAL" << std::endl;
        return;
    }

    const std::string temporaryPath =
        configs.multiplicityBoundaryReceiptPath +
        Form(".tmp.%d", gSystem->GetPid());
    {
        std::ofstream output(temporaryPath);
        if (!output.is_open()) {
            throw std::runtime_error(
                "Could not open temporary multiplicity-boundary receipt: " +
                temporaryPath);
        }
        output << serializedReceipt;
        output.flush();
        if (!output.good()) {
            throw std::runtime_error(
                "Could not write complete multiplicity-boundary receipt: " +
                temporaryPath);
        }
    }
    if (gSystem->Rename(
            temporaryPath.c_str(),
            configs.multiplicityBoundaryReceiptPath.c_str()) != 0) {
        throw std::runtime_error(
            "Could not atomically publish multiplicity-boundary receipt: " +
            configs.multiplicityBoundaryReceiptPath);
    }
    std::cout
        << "MULTIPLICITY_BOUNDARY_RECEIPT"
        << " path=" << configs.multiplicityBoundaryReceiptPath
        << " payload_sha256="
        << receipt.at("payload_sha256").get<std::string>()
        << " tune_count=" << receipt.at("tunes").size()
        << " status=PASS" << std::endl;
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

bool IsBinUsedByAnyCanvas(
    const CONFIGS& configs,
    const char* flavour,
    const std::string& trigger,
    const std::string& histogramName
) {
    for (const auto& canvas : configs.vCanvasConfigs) {
        if (!canvas.FLAVOUR.empty() && canvas.FLAVOUR != flavour) {
            continue;
        }
        if (!canvas.TriggerToUse.empty() &&
            canvas.TriggerToUse != trigger) {
            continue;
        }
        if (!isInVector(histogramName, canvas.vBinsToIgnore)) {
            return true;
        }
    }
    return false;
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
    yieldsAndErrors.referenceAssociateIndex =
        mapYieldsAndErrors.mapReferenceAssociateIndex.at(trigger);
    yieldsAndErrors.referenceMesonPdg =
        mapYieldsAndErrors.mapReferenceMesonPdg.at(trigger);

    return yieldsAndErrors;
}

void ApplyTuneVisualStyle(TH1D* hist, const std::string& tune, bool applyTuneLineStyle = false)
{
    if (!hist) return;
    HadronizationPlotStyle::ApplyTuneLineAndMarker(hist, tune, applyTuneLineStyle);
    hist->SetLineWidth(2);
    hist->SetMarkerSize(1.0);
}

std::string DisplayLabelForMultiplicityBin(
    const BinsFromTHnSparse& bin,
    const std::map<std::string, std::string>& legendEntriesMap
) {
    const auto found = legendEntriesMap.find(bin.hDPhi);
    if (found != legendEntriesMap.end()) { return found->second; }
    if (!bin.binLabel.empty()) { return bin.binLabel; }
    return bin.hDPhi;
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


// Function that creates a map storing both the dependency object (the 'bin' we want to draw)
// and the integer of the vYields vector that contains this bin (the third one)
// This allows to calculate all the multiplicity bins, but draw only a selection of them
std::map<std::size_t, std::string> CreateDependencyMap(const YieldsAndErrors& yields, const std::vector<BinsFromTHnSparse>& bins) {

    std::map<std::size_t, std::string> dependencyMap;

    std::size_t nDependencies = 0;
    if (!yields.vYields.empty() && !yields.vYields[0].empty())
        nDependencies = yields.vYields[0][0].size();
    if (bins.size() != nDependencies)
        throw std::runtime_error("Number of BinsFromTHnSparse objects does not match k dimension.");

    for (std::size_t k = 0; k < nDependencies; ++k) { dependencyMap[k] = bins[k].hDPhi; }

    return dependencyMap;
}


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

void RequireExactJsonKeys(
    const json& object,
    const std::set<std::string>& expected,
    const std::string& context
) {
    if (!object.is_object()) {
        throw std::runtime_error(context + " must be a JSON object");
    }
    std::set<std::string> actual;
    for (auto iterator = object.begin(); iterator != object.end(); ++iterator) {
        actual.insert(iterator.key());
    }
    if (actual != expected) {
        std::ostringstream message;
        message << context << " has an unsupported or missing field set";
        for (const auto& key : expected) {
            if (!actual.count(key)) message << "\n  missing: " << key;
        }
        for (const auto& key : actual) {
            if (!expected.count(key)) message << "\n  unsupported: " << key;
        }
        throw std::runtime_error(message.str());
    }
}

PairInputSelectionContract ParsePairInputSelectionContract(
    const json& object
) {
    const std::set<std::string> expectedKeys = {
        "mode",
        "legacy_metadata_free_complete_root_tag",
        "histogram_pt_eta_fields",
        "v2_analysis_schema",
        "v2_analysis_implementation",
        "v2_analysis_version",
        "v2_analysis_profile",
        "v2_selector_version",
        "v2_pair_combinatorics_mode",
        "v2_trigger_pt_min_exclusive",
        "v2_associate_pt_min_exclusive",
        "v2_eta_abs_max_inclusive",
        "v2_same_sign_pair_factor",
        "v2_pt_upper_selection"
    };
    RequireExactJsonKeys(
        object, expectedKeys, "pair_input_selection_contract");

    PairInputSelectionContract contract;
    contract.mode = object.at("mode").get<std::string>();
    contract.legacyMetadataFreeCompleteRootTag =
        object.at("legacy_metadata_free_complete_root_tag")
            .get<std::string>();
    contract.histogramPtEtaFieldSemantics =
        object.at("histogram_pt_eta_fields").get<std::string>();
    contract.analysisSchema =
        object.at("v2_analysis_schema").get<std::string>();
    contract.analysisImplementation =
        object.at("v2_analysis_implementation").get<std::string>();
    contract.analysisVersion =
        object.at("v2_analysis_version").get<std::string>();
    contract.analysisProfile =
        object.at("v2_analysis_profile").get<std::string>();
    contract.selectorVersion =
        object.at("v2_selector_version").get<std::string>();
    contract.pairCombinatoricsMode =
        object.at("v2_pair_combinatorics_mode").get<std::string>();
    contract.triggerPtMinExclusive =
        object.at("v2_trigger_pt_min_exclusive").get<Double_t>();
    contract.associatePtMinExclusive =
        object.at("v2_associate_pt_min_exclusive").get<Double_t>();
    contract.etaAbsMaxInclusive =
        object.at("v2_eta_abs_max_inclusive").get<Double_t>();
    contract.sameSignPairFactor =
        object.at("v2_same_sign_pair_factor").get<Double_t>();
    contract.ptUpperSelection =
        object.at("v2_pt_upper_selection").get<std::string>();

    if (!PairSelectionContractAllowsV2(contract) &&
        !PairSelectionContractAllowsLegacy(contract)) {
        throw std::runtime_error(
            "Unsupported pair_input_selection_contract mode: " +
            contract.mode);
    }
    if (PairSelectionContractAllowsLegacy(contract) &&
        contract.legacyMetadataFreeCompleteRootTag.empty()) {
        throw std::runtime_error(
            "Legacy pair-selection mode requires an explicit metadata-free "
            "complete-root tag");
    }
    if (contract.histogramPtEtaFieldSemantics !=
        "legacy_recuts_only_v1") {
        throw std::runtime_error(
            "histogram_pt_eta_fields must be "
            "'legacy_recuts_only_v1'; v2 inputs are already selected "
            "upstream");
    }

    // These values are the only central v2 selection understood by this
    // plotting implementation. A different definition requires a new
    // versioned code path, not a silent JSON edit.
    const bool supportedV2 =
        contract.analysisSchema ==
            "paul_pair_objects_primary_ground_v2" &&
        contract.analysisImplementation ==
            "one_pass_primary_ground_pair_analysis_v2" &&
        contract.analysisVersion ==
            "status_analysis_THnSparse_qq_v2" &&
        contract.analysisProfile ==
            "central_primary_ground_v1" &&
        contract.selectorVersion ==
            "hard_trigger_primary_ground__primary_ground_associate_v1" &&
        contract.pairCombinatoricsMode ==
            "ordered_conditional_v1" &&
        std::abs(contract.triggerPtMinExclusive - 1.0) <= 1e-12 &&
        std::abs(contract.associatePtMinExclusive - 0.15) <= 1e-12 &&
        std::abs(contract.etaAbsMaxInclusive - 4.0) <= 1e-12 &&
        std::abs(contract.sameSignPairFactor - 1.0) <= 1e-12 &&
        contract.ptUpperSelection == "none";
    if (!supportedV2) {
        throw std::runtime_error(
            "Unsupported central v2 pair-selection definition");
    }

    return contract;
}

std::map<std::string, std::map<double, double>>
FreezeAndValidateMultiplicityDefinitions(
    const std::string& baseDir,
    const std::vector<std::string>& tunes,
    const std::string& beautyCompleteRootTag,
    const std::string& charmCompleteRootTag,
    const std::string& beautySubsampleBase,
    const std::string& charmSubsampleBase,
    Int_t nSubSamples,
    bool calculateErrors,
    const std::map<std::string, std::vector<TriggerAssociateOSandSS>>&
        beautyConfigs,
    const std::map<std::string, std::vector<TriggerAssociateOSandSS>>&
        charmConfigs,
    const std::vector<BinsFromTHnSparse>& bins,
    json* receiptOut = nullptr,
    const std::string& configurationPath = "",
    const std::string& configurationSha256 = ""
) {
    if (tunes.empty() || (beautyConfigs.empty() && charmConfigs.empty())) {
        throw std::runtime_error(
            "Cannot freeze multiplicity definitions without tunes and "
            "configured pair inputs");
    }
    if (calculateErrors && nSubSamples <= 0) {
        throw std::runtime_error(
            "Cannot validate block multiplicity definitions with a "
            "non-positive block count");
    }
    if (receiptOut) {
        const bool validConfigurationSha =
            configurationSha256.size() == 64U &&
            std::all_of(
                configurationSha256.begin(),
                configurationSha256.end(),
                [](unsigned char character) {
                    return (character >= '0' && character <= '9') ||
                           (character >= 'a' && character <= 'f');
                });
        if (configurationPath.empty() || !validConfigurationSha) {
            throw std::runtime_error(
                "Multiplicity-boundary receipt requires the exact "
                "configuration path and lowercase SHA-256");
        }
    }
    std::set<double> requestedPercentiles;
    for (const auto& bin : bins) {
        requestedPercentiles.insert(bin.multiplicityMin);
        requestedPercentiles.insert(bin.multiplicityMax);
    }
    if (requestedPercentiles.empty()) {
        throw std::runtime_error(
            "Cannot freeze multiplicity definitions without requested "
            "percentiles");
    }
    std::set<std::pair<double, double>> uniqueConfiguredClasses;
    for (const auto& bin : bins) {
        uniqueConfiguredClasses.insert(
            {bin.multiplicityMin, bin.multiplicityMax});
    }
    const std::vector<std::pair<double, double>> configuredClasses(
        uniqueConfiguredClasses.begin(), uniqueConfiguredClasses.end());
    const auto orderedPartition =
        HadronizationMultiplicity::ValidateAndOrderPartition(
            configuredClasses);

    json receipt = {
        {"schema", HadronizationMultiplicity::kBoundaryReceiptSchema},
        {"schema_version", 1},
        {"algorithm", HadronizationMultiplicity::kBoundaryAlgorithm},
        {"configuration_path", configurationPath},
        {"configuration_sha256", configurationSha256},
        {"policy", {
            {"normalization", "sum_of_regular_bins"},
            {"underflow", "must_be_exactly_zero_and_is_excluded"},
            {"overflow", "must_be_exactly_zero_and_is_excluded"},
            {"threshold_rule",
             "first_ascending_integer_nch_bin_with_inclusive_cumulative_"
             "weight_ge_(100-percentile)/100"},
            {"tie_rule",
             "boundary_integer_belongs_to_lower_activity_class;_adjacent_"
             "higher_activity_class_starts_at_boundary_plus_one"},
            {"class_bounds", "inclusive_integer_nch"},
            {"integrated_0_100_observable",
             "excluded_from_mutually_exclusive_partition"}
        }},
        {"tunes", json::object()}
    };

    std::map<std::string, std::map<double, double>> thresholdsByTune;
    for (const auto& tune : tunes) {
        bool haveCentralIdentity = false;
        MultiplicityHistogramIdentity centralIdentity;
        std::string centralIdentityPath;
        std::string centralSourceFileSha256;
        std::string centralMergeManifestSha256;
        std::string centralPairRegistrySha256;
        std::size_t centralFilesValidated = 0;
        std::size_t blockFilesValidated = 0;
        std::set<std::string> visitedCentral;
        json blockReceipts = json::array();

        const auto validateCentralPath =
            [&](const std::string& path) {
                if (!visitedCentral.insert(path).second) return;
                std::unique_ptr<TFile> file(OpenRootFileOrThrow(path));
                TH1D* histogram = GetObjectOrThrow<TH1D>(
                    file.get(), "summed MULTIPLICITY", path);
                const MultiplicityHistogramIdentity observed =
                    CaptureMultiplicityHistogramIdentity(histogram, path);
                if (!haveCentralIdentity) {
                    centralIdentity = observed;
                    centralIdentityPath = path;
                    centralSourceFileSha256 =
                        Hadronization::Sha256FileHex(path);
                    if (TObjString* mergeManifest =
                            dynamic_cast<TObjString*>(
                                file->Get(
                                    "merge_input_manifest_sha256"))) {
                        centralMergeManifestSha256 =
                            mergeManifest->GetString().Data();
                    }
                    if (TObjString* pairRegistry =
                            dynamic_cast<TObjString*>(
                                file->Get("pair_registry_sha256"))) {
                        centralPairRegistrySha256 =
                            pairRegistry->GetString().Data();
                    }
                    haveCentralIdentity = true;
                    for (const double percentile : requestedPercentiles) {
                        thresholdsByTune[tune][percentile] =
                            static_cast<double>(
                                HadronizationMultiplicity::
                                    ThresholdForPercentile(
                                        centralIdentity, percentile,
                                        path));
                    }
                } else {
                    RequireIdenticalMultiplicityHistogram(
                        centralIdentity, observed,
                        centralIdentityPath, path);
                }
                ++centralFilesValidated;
            };

        const auto visitCentralConfig =
            [&](const std::map<
                    std::string,
                    std::vector<TriggerAssociateOSandSS>>& configurations,
                const std::string& completeRootTag) {
                for (const auto& [trigger, pairs] : configurations) {
                    (void)trigger;
                    for (const auto& pair : pairs) {
                        validateCentralPath(ResolveCompleteRootFile(
                            baseDir, tune, completeRootTag, pair.OS));
                        validateCentralPath(ResolveCompleteRootFile(
                            baseDir, tune, completeRootTag, pair.SS));
                    }
                }
            };
        visitCentralConfig(beautyConfigs, beautyCompleteRootTag);
        visitCentralConfig(charmConfigs, charmCompleteRootTag);
        if (!haveCentralIdentity) {
            throw std::runtime_error(
                "No central summed MULTIPLICITY input was validated for " +
                tune);
        }

        if (calculateErrors) {
            for (Int_t block = 1; block <= nSubSamples; ++block) {
                bool haveBlockIdentity = false;
                MultiplicityHistogramIdentity blockIdentity;
                std::string blockIdentityPath;
                std::set<std::string> visitedBlock;
                const std::size_t blockFilesBefore =
                    blockFilesValidated;
                const auto validateBlockPath =
                    [&](const std::string& path) {
                        if (!visitedBlock.insert(path).second) return;
                        std::unique_ptr<TFile> file(
                            OpenRootFileOrThrow(path));
                        TH1D* histogram = GetObjectOrThrow<TH1D>(
                            file.get(), "summed MULTIPLICITY", path);
                        const MultiplicityHistogramIdentity observed =
                            CaptureMultiplicityHistogramIdentity(
                                histogram, path);
                        if (!haveBlockIdentity) {
                            blockIdentity = observed;
                            blockIdentityPath = path;
                            haveBlockIdentity = true;
                        } else {
                            RequireIdenticalMultiplicityHistogram(
                                blockIdentity, observed,
                                blockIdentityPath, path);
                        }
                        ++blockFilesValidated;
                    };
                const auto visitBlockConfig =
                    [&](const std::map<
                            std::string,
                            std::vector<TriggerAssociateOSandSS>>&
                            configurations,
                        const std::string& subsampleBase) {
                        for (const auto& [trigger, pairs] :
                             configurations) {
                            (void)trigger;
                            for (const auto& pair : pairs) {
                                validateBlockPath(ResolveSubSampleRootFile(
                                    subsampleBase, tune, block, pair.OS));
                                validateBlockPath(ResolveSubSampleRootFile(
                                    subsampleBase, tune, block, pair.SS));
                            }
                        }
                    };
                visitBlockConfig(beautyConfigs, beautySubsampleBase);
                visitBlockConfig(charmConfigs, charmSubsampleBase);
                if (!haveBlockIdentity) {
                    throw std::runtime_error(
                        Form("No block-%d summed MULTIPLICITY input was "
                             "validated for %s",
                             block, tune.c_str()));
                }
                blockReceipts.push_back({
                    {"block", block},
                    {"reference_path", blockIdentityPath},
                    {"histogram_identity_sha256",
                     HadronizationMultiplicity::
                         HistogramIdentitySha256(blockIdentity)},
                    {"files_validated",
                     blockFilesValidated - blockFilesBefore},
                    {"exact_comparisons",
                     blockFilesValidated - blockFilesBefore - 1U}
                });
            }
        }

        const auto requireOptionalSha256 =
            [&](const std::string& value, const char* field) {
                if (value.empty()) return;
                const bool valid =
                    value.size() == 64U &&
                    std::all_of(
                        value.begin(), value.end(),
                        [](unsigned char character) {
                            return
                                (character >= '0' && character <= '9') ||
                                (character >= 'a' && character <= 'f');
                        });
                if (!valid) {
                    throw std::runtime_error(
                        "Invalid " + std::string(field) +
                        " in multiplicity source " +
                        centralIdentityPath);
                }
            };
        requireOptionalSha256(
            centralMergeManifestSha256,
            "merge_input_manifest_sha256");
        requireOptionalSha256(
            centralPairRegistrySha256, "pair_registry_sha256");

        std::map<double, int> integerThresholds;
        for (const auto& [percentile, threshold] :
             thresholdsByTune.at(tune)) {
            const double rounded = std::round(threshold);
            if (!std::isfinite(threshold) ||
                std::abs(threshold - rounded) > 1e-9) {
                throw std::runtime_error(
                    "Frozen multiplicity threshold is not an integer Nch "
                    "for tune " + tune);
            }
            integerThresholds[percentile] =
                static_cast<int>(rounded);
        }
        HadronizationMultiplicity::RequireDiscretePartitionCoverage(
            configuredClasses, integerThresholds);

        json thresholdRecords = json::array();
        for (const auto& [percentile, threshold] :
             integerThresholds) {
            thresholdRecords.push_back({
                {"percentile", percentile},
                {"nch_threshold", threshold},
                {"target_low_activity_fraction",
                 (100.0 - percentile) / 100.0},
                {"achieved_exclusive_fraction_before_threshold",
                 HadronizationMultiplicity::
                     CumulativeFractionBefore(
                         centralIdentity, threshold,
                         centralIdentityPath)},
                {"achieved_inclusive_fraction_through_threshold",
                 HadronizationMultiplicity::
                     CumulativeFractionThrough(
                         centralIdentity, threshold,
                         centralIdentityPath)}
            });
        }

        json classRecords = json::array();
        double achievedPartitionFraction = 0.0;
        for (const auto& interval : orderedPartition) {
            const auto range =
                HadronizationMultiplicity::DiscreteClassRange(
                    integerThresholds, interval.first,
                    interval.second);
            const double achievedFraction =
                HadronizationMultiplicity::InclusiveWeight(
                    centralIdentity, range.first, range.second,
                    centralIdentityPath) /
                centralIdentity.integral;
            achievedPartitionFraction += achievedFraction;
            classRecords.push_back({
                {"percentile_min", interval.first},
                {"percentile_max", interval.second},
                {"nch_min_inclusive", range.first},
                {"nch_max_inclusive", range.second},
                {"target_fraction",
                 (interval.second - interval.first) / 100.0},
                {"achieved_weighted_fraction",
                 achievedFraction}
            });
        }
        if (!std::isfinite(achievedPartitionFraction) ||
            std::abs(achievedPartitionFraction - 1.0) > 1e-12) {
            throw std::runtime_error(
                "Frozen multiplicity classes do not exhaust the regular-bin "
                "weight for tune " + tune);
        }

        json mergeManifestValue = nullptr;
        if (!centralMergeManifestSha256.empty()) {
            mergeManifestValue = centralMergeManifestSha256;
        }
        json pairRegistryValue = nullptr;
        if (!centralPairRegistrySha256.empty()) {
            pairRegistryValue = centralPairRegistrySha256;
        }
        receipt["tunes"][tune] = {
            {"central_reference_path", centralIdentityPath},
            {"central_source_file_sha256",
             centralSourceFileSha256},
            {"central_merge_input_manifest_sha256",
             mergeManifestValue},
            {"pair_registry_sha256", pairRegistryValue},
            {"histogram_identity_sha256",
             HadronizationMultiplicity::
                 HistogramIdentitySha256(centralIdentity)},
            {"histogram_name", "summed MULTIPLICITY"},
            {"regular_bin_integral", centralIdentity.integral},
            {"underflow", centralIdentity.contents.front()},
            {"overflow", centralIdentity.contents.back()},
            {"central_files_validated", centralFilesValidated},
            {"central_exact_comparisons",
             centralFilesValidated - 1U},
            {"block_files_validated", blockFilesValidated},
            {"blocks", blockReceipts},
            {"thresholds", thresholdRecords},
            {"classes", classRecords},
            {"partition", {
                {"nch_min_inclusive",
                 integerThresholds.at(100.0)},
                {"nch_max_inclusive",
                 integerThresholds.at(0.0)},
                {"coverage", "PASS"},
                {"disjointness", "PASS"},
                {"achieved_weighted_fraction",
                 achievedPartitionFraction}
            }}
        };

        std::cout
            << "MULTIPLICITY_IDENTITY"
            << " tune=" << tune
            << " central_reference=" << centralIdentityPath
            << " central_files=" << centralFilesValidated
            << " block_files=" << blockFilesValidated
            << " integral=" << centralIdentity.integral
            << " percentile_count="
            << thresholdsByTune.at(tune).size()
            << " status=PASS"
            << std::endl;
        for (const auto& [percentile, threshold] :
             thresholdsByTune.at(tune)) {
            std::cout << "MULTIPLICITY_BOUNDARY"
                      << " tune=" << tune
                      << " percentile=" << percentile
                      << " nch=" << threshold
                      << " central_reference=" << centralIdentityPath
                      << std::endl;
        }
    }
    if (receiptOut) {
        *receiptOut = std::move(receipt);
    }
    return thresholdsByTune;
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
    const std::string configurationSha256 =
        Hadronization::Sha256FileHex(configurationPath);

    // Extract values from the JSON
    // Generic options
    bool VERBOSE = config["VERBOSE"].get<bool>();
    bool CALCULATE_ERRORS = config["calculate_errors"].get<bool>();
    const PairInputSelectionContract PAIR_INPUT_SELECTION_CONTRACT =
        ParsePairInputSelectionContract(
            config.at("pair_input_selection_contract"));
    std::string bbBarDir_sub_samples = ResolvePathFromBase(config["bb_bar_complete_root_dir_sub_samples"], hadronizationBase);
    std::string ccBarDir_sub_samples = ResolvePathFromBase(config["cc_bar_complete_root_dir_sub_samples"], hadronizationBase);
    if (const char* selectedSubsamples =
            std::getenv("HADRONIZATION_SUBSAMPLE_BASE")) {
        bbBarDir_sub_samples =
            ResolvePathFromBase(selectedSubsamples, hadronizationBase);
        ccBarDir_sub_samples = bbBarDir_sub_samples;
    }
    int nSubSamples = config["nSubSamples"].get<int>();
    const std::string PAIR_COMBINATORICS_MODE =
        config.at("pair_combinatorics_mode").get<std::string>();
    const Double_t SAME_SIGN_PAIR_FACTOR =
        config.at("same_sign_pair_factor").get<Double_t>();
    if (!std::isfinite(SAME_SIGN_PAIR_FACTOR) ||
        SAME_SIGN_PAIR_FACTOR <= 0.0) {
        throw std::runtime_error(
            "same_sign_pair_factor must be finite and positive");
    }
    if (PAIR_COMBINATORICS_MODE == "ordered_conditional_v1") {
        if (std::abs(SAME_SIGN_PAIR_FACTOR - 1.0) > 1e-12) {
            throw std::runtime_error(
                "ordered_conditional_v1 requires same_sign_pair_factor = 1.0");
        }
        if (!PairSelectionContractAllowsV2(
                PAIR_INPUT_SELECTION_CONTRACT) ||
            PAIR_INPUT_SELECTION_CONTRACT.pairCombinatoricsMode !=
                "ordered_conditional_v1" ||
            std::abs(
                PAIR_INPUT_SELECTION_CONTRACT.sameSignPairFactor - 1.0) >
                1e-12) {
            throw std::runtime_error(
                "Canonical ordered pair combinatorics require the exact "
                "v2 ordered_conditional_v1 metadata assertion");
        }
    } else if (PAIR_COMBINATORICS_MODE ==
               "legacy_identical_ss_half_v1") {
        if (std::abs(SAME_SIGN_PAIR_FACTOR - 0.5) > 1e-12) {
            throw std::runtime_error(
                "legacy_identical_ss_half_v1 requires "
                "same_sign_pair_factor = 0.5");
        }
        if (!PairSelectionContractAllowsLegacy(
                PAIR_INPUT_SELECTION_CONTRACT)) {
            throw std::runtime_error(
                "Legacy half-weight pair combinatorics require the explicit "
                "tagged legacy-recutter selection contract");
        }
    } else {
        throw std::runtime_error(
            "Unsupported pair_combinatorics_mode: " +
            PAIR_COMBINATORICS_MODE);
    }
    bool DRAW_CORRELATION_PLOTS = config["draw_correlation_plots"].get<bool>();
    bool SUBSAMPLE_COVERAGE_AUDIT =
        config.value("subsample_coverage_audit", false);
    const std::vector<std::string> vSubsampleErrorBinsToExclude =
        config.value("subsample_error_bins_to_exclude", std::vector<std::string>{});

    // RootFiles path ("base directory")
    std::string base_dir = ResolvePathFromBase(config["base_dir"], hadronizationBase);
    if (const char* selectedBase =
            std::getenv("HADRONIZATION_ANALYZED_DATA_BASE")) {
        base_dir = ResolvePathFromBase(selectedBase, hadronizationBase);
    }

    // Tunes
    std::vector<std::string> vTUNES;
    for (const auto& TUNE : config["PYTHIA_TUNES"]) {
        vTUNES.push_back(TUNE);
    }

    // Complete_root_dirs
    std::string bbBarDir = config["bb_bar_complete_root_dir"];
    std::string ccBarDir = config["cc_bar_complete_root_dir"];
    if (const char* selectedTag =
            std::getenv("HADRONIZATION_COMPLETE_ROOT_TAG")) {
        bbBarDir = selectedTag;
        ccBarDir = selectedTag;
    }

    // Print the portable resolver inputs without implying one fixed on-disk
    // layout. ResolveCompleteRootFile supports both flat and nested tune paths.
    for (const auto& TUNE : vTUNES) {
        std::cout << "Beauty central resolver " << TUNE
                  << ": base=" << base_dir << ", tag=" << bbBarDir << std::endl;
        std::cout << "Beauty subsample resolver " << TUNE
                  << ": base=" << bbBarDir_sub_samples << std::endl;
    }
    for (const auto& TUNE : vTUNES) {
        std::cout << "Charm central resolver " << TUNE
                  << ": base=" << base_dir << ", tag=" << ccBarDir << std::endl;
        std::cout << "Charm subsample resolver " << TUNE
                  << ": base=" << ccBarDir_sub_samples << std::endl;
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
        const std::string groupTrigger =
            triggerEntry["trigger"].get<std::string>();
        if (beautyConfigs.count(groupTrigger)) {
            throw std::runtime_error(
                "Duplicate beauty trigger group in configuration: " +
                groupTrigger);
        }
        auto& configs = beautyConfigs[groupTrigger];
        // Fill the map with the configs for the specific trigger
        for (const auto& cfg : triggerEntry["configs"]) {
            configs.push_back(ResolveConfiguredPairFromRegistry(
                "beauty", groupTrigger,
                cfg["trigger"].get<std::string>(),
                cfg["associateOS"].get<std::string>(),
                cfg["associateSS"].get<std::string>(),
                cfg["OS"].get<std::string>(),
                cfg["SS"].get<std::string>()));
            std::cout << "OS File: " << cfg["OS"] << ", SS File: " << cfg["SS"] << std::endl;
        }
        const auto reference = ResolveReferenceAssociateSelection(
            configs, "beauty trigger group '" + groupTrigger + "'");
        std::cout << "Reference meson for " << groupTrigger
                  << ": PDG=" << reference.pdg
                  << ", configured associate index=" << reference.index
                  << std::endl;
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
        const std::string groupTrigger =
            triggerEntry["trigger"].get<std::string>();
        if (charmConfigs.count(groupTrigger)) {
            throw std::runtime_error(
                "Duplicate charm trigger group in configuration: " +
                groupTrigger);
        }
        auto& configs = charmConfigs[groupTrigger];
        // Fill the map with the configs for the specific trigger
        for (const auto& cfg : triggerEntry["configs"]) {
            configs.push_back(ResolveConfiguredPairFromRegistry(
                "charm", groupTrigger,
                cfg["trigger"].get<std::string>(),
                cfg["associateOS"].get<std::string>(),
                cfg["associateSS"].get<std::string>(),
                cfg["OS"].get<std::string>(),
                cfg["SS"].get<std::string>()));
            std::cout << "OS File: " << cfg["OS"] << ", SS File: " << cfg["SS"] << std::endl;
        }
        const auto reference = ResolveReferenceAssociateSelection(
            configs, "charm trigger group '" + groupTrigger + "'");
        std::cout << "Reference meson for " << groupTrigger
                  << ": PDG=" << reference.pdg
                  << ", configured associate index=" << reference.index
                  << std::endl;
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
        ValidateProjectionCuts(
            pair,
            PairSelectionProjectionMode::kLegacyPlotRecutsV1);
        if (!(pair.multiplicityMin >= 0.0 &&
              pair.multiplicityMax <= 100.0 &&
              pair.multiplicityMin < pair.multiplicityMax)) {
            throw std::runtime_error(
                "histograms_to_analyse contains an invalid multiplicity "
                "percentile interval");
        }
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
        pair.TriggerToUse = configPair["TriggerToUse"].get<std::string>(); // must be identical to trigger name from 'histograms to draw' section! TODO: do something about that.. TODO: make naming consistent (with _)
        std::vector<std::string> vBinsToIgnore;
        for (const auto& binToIgnore : configPair["bins_to_ignore"]) {
            vBinsToIgnore.push_back(binToIgnore);
        }
        pair.vBinsToIgnore = vBinsToIgnore;
        pair.vIndexNominatorTUNES.clear();
        if (configPair.contains("nominator_TUNES")) {
            for (const auto& tune : configPair["nominator_TUNES"]) {
                std::string tuneName = tune.get<std::string>();
                Int_t tuneIndex = findTuneIndex(vTUNES, tuneName);
                if (tuneIndex != -1) {
                    pair.vIndexNominatorTUNES.push_back(tuneIndex);
                    std::cout << "Index of " << tuneName << " is: " << tuneIndex << std::endl;
                } else { std::cout << tuneName << " ERROR: TUNE not found in vTUNES." << std::endl; }
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
    std::set<std::string> boundaryReceiptDirectories;
    for (const auto& globalCanvas : vGlobalCanvasConfigs) {
        if (globalCanvas.write &&
            !globalCanvas.writePath.empty() &&
            globalCanvas.writePath != "NONE") {
            boundaryReceiptDirectories.insert(
                globalCanvas.writePath);
        }
    }
    if ((!SUBSAMPLE_COVERAGE_AUDIT &&
         boundaryReceiptDirectories.size() != 1U) ||
        (SUBSAMPLE_COVERAGE_AUDIT &&
         boundaryReceiptDirectories.size() > 1U)) {
        throw std::runtime_error(
            SUBSAMPLE_COVERAGE_AUDIT
                ? "Audit-only mode permits zero or one, but not multiple, "
                  "multiplicity-boundary receipt directories"
                : "Exactly one global-canvas output directory is required "
                  "to store the multiplicity-boundary receipt");
    }
    const std::string multiplicityBoundaryReceiptPath =
        boundaryReceiptDirectories.empty()
            ? std::string()
            : JoinPath({*boundaryReceiptDirectories.begin(),
                        "multiplicity_boundary_receipt_v1.json"});

    // TODO: make a function that prints content of a vector
    CONFIGS configs_from_json;
    configs_from_json.VERBOSE = VERBOSE;
    configs_from_json.CALCULATE_ERRORS = CALCULATE_ERRORS;
    configs_from_json.nSubSamples = nSubSamples;
    configs_from_json.PAIR_COMBINATORICS_MODE = PAIR_COMBINATORICS_MODE;
    configs_from_json.SAME_SIGN_PAIR_FACTOR = SAME_SIGN_PAIR_FACTOR;
    configs_from_json.PAIR_INPUT_SELECTION_CONTRACT =
        PAIR_INPUT_SELECTION_CONTRACT;
    configs_from_json.DRAW_CORRELATION_PLOTS = DRAW_CORRELATION_PLOTS;
    configs_from_json.SUBSAMPLE_COVERAGE_AUDIT = SUBSAMPLE_COVERAGE_AUDIT;
    configs_from_json.base_dir = base_dir;
    configs_from_json.vSubsampleErrorBinsToExclude = vSubsampleErrorBinsToExclude;
    configs_from_json.configurationPath = configurationPath;
    configs_from_json.configurationSha256 = configurationSha256;
    configs_from_json.multiplicityBoundaryReceiptPath =
        multiplicityBoundaryReceiptPath;
    configs_from_json.vTUNES = vTUNES;
    configs_from_json.bbBarDir = bbBarDir;
    configs_from_json.ccBarDir = ccBarDir;
    configs_from_json.bbBarDir_subSamples = bbBarDir_sub_samples;
    configs_from_json.ccBarDir_subSamples = ccBarDir_sub_samples;
    configs_from_json.vBeautyTriggerAssociateOSandSS = vBeautyTriggerAssociateOSandSS; // toremove
    configs_from_json.vCharmTriggerAssociateOSandSS = vCharmTriggerAssociateOSandSS; // toremove
    configs_from_json.beautyConfigs = beautyConfigs;
    configs_from_json.charmConfigs = charmConfigs;
    configs_from_json.multiplicityPercentileThresholdsByTune =
        FreezeAndValidateMultiplicityDefinitions(
            base_dir, vTUNES, bbBarDir, ccBarDir,
            bbBarDir_sub_samples, ccBarDir_sub_samples,
            nSubSamples, CALCULATE_ERRORS,
            beautyConfigs, charmConfigs, vBinsFromTHnSparse,
            &configs_from_json.multiplicityBoundaryReceipt,
            configurationPath, configurationSha256);
    // configs_from_json.vHistogramAndTriggerPtHistogramNames = vHistogramAndTriggerPtHistogramNames;
    configs_from_json.vBinsFromTHnSparse = vBinsFromTHnSparse;
    configs_from_json.vCanvasConfigs = vCanvasConfigs;
    configs_from_json.vGlobalCanvasConfigs = vGlobalCanvasConfigs;

    std::cout << "Configurations successfully read from JSON with parameters:" << std::endl;
    std::cout << "VERBOSE = " << VERBOSE << std::endl;
    std::cout << "- CALCULATE_ERRORS = " << CALCULATE_ERRORS << std::endl;
    std::cout << "- nSubSamples = " << nSubSamples << std::endl;
    std::cout << "- PAIR_COMBINATORICS_MODE = "
              << PAIR_COMBINATORICS_MODE << std::endl;
    std::cout << "- SAME_SIGN_PAIR_FACTOR = "
              << SAME_SIGN_PAIR_FACTOR << std::endl;
    std::cout << "- PAIR_INPUT_SELECTION_CONTRACT = "
              << PAIR_INPUT_SELECTION_CONTRACT.mode << std::endl;
    std::cout << "- DRAW_CORRELATION_PLOTS = " << DRAW_CORRELATION_PLOTS << std::endl;
    std::cout << "- SUBSAMPLE_COVERAGE_AUDIT = "
              << SUBSAMPLE_COVERAGE_AUDIT << std::endl;
    std::cout << "- base_dir = " << base_dir << std::endl;
    std::cout << "- configuration_sha256 = "
              << configurationSha256 << std::endl;
    std::cout << "- multiplicity_boundary_receipt = "
              << multiplicityBoundaryReceiptPath << std::endl;
    std::cout << "- vTUNES.size() = " << vTUNES.size() << std::endl;
    std::cout << "- bbBarDir = " << bbBarDir << std::endl;
    std::cout << "- ccBarDir = " << ccBarDir << std::endl;
    std::cout << "- bbBarDir_sub_samples = " << bbBarDir_sub_samples << std::endl;
    std::cout << "- ccBarDir_sub_samples = " << ccBarDir_sub_samples << std::endl;
    std::cout << "- vBeautyTriggerAssociateOSandSS.size() = " << vBeautyTriggerAssociateOSandSS.size() << std::endl;
    std::cout << "- vCharmTriggerAssociateOSandSS.size() = " << vCharmTriggerAssociateOSandSS.size() << std::endl;
    // std::cout << "- vHistogramAndTriggerPtHistogramNames.size() = " << vHistogramAndTriggerPtHistogramNames.size() << std::endl;
    std::cout << "- vBinsFromTHnSparse.size() = " << vBinsFromTHnSparse.size() << std::endl;
    std::cout << "- vSubsampleErrorBinsToExclude.size() = "
              << vSubsampleErrorBinsToExclude.size() << std::endl;
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
        errorA < 0.0 || errorB < 0.0 || valueB == 0.0) {
        return std::numeric_limits<Double_t>::quiet_NaN();
    }

    // Absolute derivative propagation remains defined for A == 0:
    // sigma^2(A/B) = (sigma_A/B)^2 + (A sigma_B/B^2)^2.
    const Double_t derivativeAContribution = errorA / valueB;
    const Double_t derivativeBContribution =
        (valueA / valueB) * (errorB / valueB);
    const Double_t propagated = std::hypot(
        derivativeAContribution, derivativeBContribution);
    return std::isfinite(propagated)
        ? propagated
        : std::numeric_limits<Double_t>::quiet_NaN();
} // propagateRatioError()


Double_t safeRatio(Double_t numerator, Double_t denominator) {
    if (!std::isfinite(numerator) || !std::isfinite(denominator) || denominator == 0.0) {
        return std::numeric_limits<Double_t>::quiet_NaN();
    }
    return numerator / denominator;
}


void SetPlotPointOrThrow(
    TH1D* histogram,
    Int_t bin,
    Double_t value,
    Double_t error,
    Bool_t requirePositiveError,
    Bool_t logarithmicY,
    Double_t configuredYMinimum,
    Double_t configuredYMaximum,
    const std::string& context
) {
    if (!histogram) {
        throw std::runtime_error("Cannot set plot point on a null histogram: " + context);
    }
    if (!std::isfinite(value)) {
        throw std::runtime_error("Non-finite plotted value: " + context);
    }
    if (!std::isfinite(error) || error < 0.0) {
        throw std::runtime_error("Invalid plotted uncertainty: " + context);
    }
    if (requirePositiveError && error == 0.0) {
        throw std::runtime_error("Zero uncertainty for a final plotted observable: " + context);
    }
    if (logarithmicY && value <= 0.0) {
        throw std::runtime_error(
            "Non-positive value cannot be represented on the configured "
            "logarithmic y axis: " + context);
    }
    if (!std::isfinite(configuredYMinimum) ||
        !std::isfinite(configuredYMaximum) ||
        configuredYMinimum >= configuredYMaximum) {
        throw std::runtime_error(
            "Invalid configured y-axis range for plotted point: " + context);
    }
    const Double_t lowerEnvelope = value - error;
    const Double_t upperEnvelope = value + error;
    if (!std::isfinite(lowerEnvelope) || !std::isfinite(upperEnvelope)) {
        throw std::runtime_error(
            "Non-finite uncertainty envelope for plotted point: " + context);
    }
    if (logarithmicY && lowerEnvelope <= 0.0) {
        throw std::runtime_error(
            "Uncertainty envelope reaches a non-positive value on the "
            "configured logarithmic y axis: " + context);
    }
    const Double_t rangeTolerance =
        1e-12 * std::max(
            {1.0, std::abs(configuredYMinimum),
             std::abs(configuredYMaximum), std::abs(lowerEnvelope),
             std::abs(upperEnvelope)});
    if (lowerEnvelope < configuredYMinimum - rangeTolerance ||
        upperEnvelope > configuredYMaximum + rangeTolerance) {
        throw std::runtime_error(
            Form("Plotted uncertainty envelope [%.17g, %.17g] is clipped by "
                 "configured y-axis [%.17g, %.17g]: %s",
                 lowerEnvelope, upperEnvelope, configuredYMinimum,
                 configuredYMaximum, context.c_str()));
    }
    histogram->SetBinContent(bin, value);
    histogram->SetBinError(bin, error);
}

void SetNestedYieldValue(
    std::vector<std::vector<std::vector<Double_t>>>& values,
    Int_t tune,
    Int_t associate,
    Int_t dependency,
    Double_t value
) {
    if (static_cast<std::size_t>(tune) >= values.size()) { values.resize(tune + 1); }
    if (static_cast<std::size_t>(associate) >= values[tune].size()) {
        values[tune].resize(associate + 1);
    }
    if (static_cast<std::size_t>(dependency) >= values[tune][associate].size()) {
        values[tune][associate].resize(dependency + 1);
    }
    values[tune][associate][dependency] = value;
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

struct SubsampleTechnicalCoverage {
    bool isReference = false;
    bool yieldNonDegenerate = false;
    bool ratioNonDegenerate = false;
    bool yieldSemValid = false;
    bool ratioSemValid = false;
    bool yieldComplete = false;
    bool ratioComplete = false;
    bool complete = false;
};

SubsampleTechnicalCoverage EvaluateSubsampleTechnicalCoverage(
    Double_t centralYield,
    Double_t centralReferenceYield,
    Double_t centralRatio,
    const SubsampleStatistics& yieldStats,
    const SubsampleStatistics& ratioStats,
    Int_t expectedSubsamples,
    bool isReference,
    bool requirePositiveFinalError
) {
    SubsampleTechnicalCoverage coverage;
    coverage.isReference = isReference;
    coverage.yieldNonDegenerate =
        std::isfinite(yieldStats.stdDev) && yieldStats.stdDev > 0.0;
    coverage.ratioNonDegenerate =
        !isReference && std::isfinite(ratioStats.stdDev) &&
        ratioStats.stdDev > 0.0;
    coverage.yieldSemValid =
        std::isfinite(yieldStats.stdError) &&
        yieldStats.stdError >= 0.0 &&
        (!(requirePositiveFinalError ||
           coverage.yieldNonDegenerate) ||
         yieldStats.stdError > 0.0);
    coverage.ratioSemValid =
        isReference ||
        (std::isfinite(ratioStats.stdError) &&
         ratioStats.stdError >= 0.0 &&
         (!(requirePositiveFinalError ||
            coverage.ratioNonDegenerate) ||
          ratioStats.stdError > 0.0));
    coverage.yieldComplete =
        expectedSubsamples > 0 &&
        std::isfinite(centralYield) &&
        yieldStats.nValues == expectedSubsamples &&
        coverage.yieldSemValid;
    coverage.ratioComplete =
        isReference ||
        (expectedSubsamples > 0 &&
         std::isfinite(centralReferenceYield) &&
         centralReferenceYield != 0.0 &&
         std::isfinite(centralRatio) &&
         ratioStats.nValues == expectedSubsamples &&
         coverage.ratioSemValid);
    coverage.complete =
        coverage.yieldComplete && coverage.ratioComplete;
    return coverage;
}

bool IsIntegratedMultiplicityBin(const BinsFromTHnSparse& bin) {
    constexpr Double_t tolerance = 1e-9;
    return std::abs(bin.multiplicityMin) < tolerance &&
           std::abs(bin.multiplicityMax - 100.0) < tolerance;
}

void ApplyCorrelationSubsampleSEM(
    TH1D* central,
    const std::vector<std::vector<Double_t>>& blockBinValues,
    Int_t expectedSubsamples,
    const std::string& context
) {
    if (!central) {
        throw std::runtime_error(
            "Cannot apply correlation uncertainty to null histogram: " +
            context);
    }
    if (blockBinValues.size() !=
        static_cast<std::size_t>(central->GetNbinsX() + 1)) {
        throw std::runtime_error(
            "Correlation uncertainty bin layout mismatch: " + context);
    }
    for (Int_t bin = 1; bin <= central->GetNbinsX(); ++bin) {
        const SubsampleStatistics stats =
            calculateSubsampleStatistics(blockBinValues[bin]);
        if (stats.nValues != expectedSubsamples ||
            !std::isfinite(stats.stdError) || stats.stdError < 0.0) {
            throw std::runtime_error(
                Form("Invalid correlation-bin SEM for %s bin=%d n=%d sem=%g",
                     context.c_str(), bin, stats.nValues, stats.stdError));
        }
        const Double_t centralValue = central->GetBinContent(bin);
        if (centralValue != 0.0 && stats.stdError == 0.0) {
            throw std::runtime_error(
                Form("Zero correlation-bin SEM for nonzero %s bin=%d",
                     context.c_str(), bin));
        }
        central->SetBinError(bin, stats.stdError);
        std::cout << "CORRELATION_BIN_UNCERTAINTY"
                  << " context=" << context
                  << " bin=" << bin
                  << " n=" << stats.nValues
                  << " central=" << centralValue
                  << " block_mean=" << stats.mean
                  << " stdError=" << stats.stdError
                  << std::endl;
    }
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
    const Double_t nTriggersOS = hTrPtOS ? hTrPtOS->Integral() : 0.0;
    const Double_t nTriggersSS = hTrPtSS ? hTrPtSS->Integral() : 0.0;
    if (nTriggersOS <= 0.0 || nTriggersSS <= 0.0) {
        std::cerr << "WARNING: zero trigger normalisation while calculating yield"
                  << " (OS triggers=" << nTriggersOS
                  << ", SS triggers=" << nTriggersSS << ")" << std::endl;
        return std::numeric_limits<Double_t>::quiet_NaN();
    }
    const Double_t triggerDifference = std::abs(nTriggersOS - nTriggersSS);
    const Double_t triggerScale =
        std::max({1.0, std::abs(nTriggersOS), std::abs(nTriggersSS)});
    if (triggerDifference > 1e-10 * triggerScale) {
        throw std::runtime_error(
            Form("OS/SS trigger denominators differ: OS=%.17g SS=%.17g",
                 nTriggersOS, nTriggersSS));
    }
	hDPhiOS->Scale(1.0 / nTriggersOS);
	hDPhiSS->Scale(1.0 / nTriggersSS);
    if (VERBOSE) {
        std::cout << "hDPhiOS Integral: " << hDPhiOS->Integral() 
                  << ", hDPhiSS Integral: " << hDPhiSS->Integral() << std::endl;
    }
    TH1D *hCorr = (TH1D*)hDPhiOS->Clone();
    hCorr->SetDirectory(nullptr);
    hCorr->Add(hDPhiSS, -1.);

    const Double_t yield = hCorr->Integral();
    delete hCorr;
    return yield;
} // calculateOneYield()


// Yields are calculated by looping over TUNES (e.g. MONASH),
// then ASSOCIATES (e.g. B-)
// and then DEPENDENCIES (e.g. DPhiLL)
// Function needs to be called for the FLAVOUR seperately (e.g. Beauty)
// The output is a 3D vector with the structure
// v[TUNE][ASSOCIATE][DEPENDENCY]
// TODO: change the .size() to variables nTUNES, etc. Like in the plotting function below
YieldsAndErrorsMap calculateYieldsVector(CONFIGS configs_from_json, const char* FLAVOUR, TCanvas* cAngularCorrelations) {

    std::cout << "*** Calculating yields for " << FLAVOUR << " ***" << std::endl;

    // Retrieve settings from configuration.json
    bool VERBOSE = configs_from_json.VERBOSE;
    bool CALCULATE_ERRORS = configs_from_json.CALCULATE_ERRORS;
    bool SUBSAMPLE_COVERAGE_AUDIT =
        configs_from_json.SUBSAMPLE_COVERAGE_AUDIT;
    int nSubSamples = configs_from_json.nSubSamples;
    const Double_t SAME_SIGN_PAIR_FACTOR =
        configs_from_json.SAME_SIGN_PAIR_FACTOR;
    const std::string PAIR_COMBINATORICS_MODE =
        configs_from_json.PAIR_COMBINATORICS_MODE;
    const PairInputSelectionContract PAIR_INPUT_SELECTION_CONTRACT =
        configs_from_json.PAIR_INPUT_SELECTION_CONTRACT;
    bool DRAW_CORRELATION_PLOTS = configs_from_json.DRAW_CORRELATION_PLOTS;
    std::string base_dir = configs_from_json.base_dir;
    std::vector<std::string> vTUNES = configs_from_json.vTUNES;
    std::string complete_root_dir;
    std::string heavySector;
    if (strcmp(FLAVOUR, "BEAUTY") == 0) {
        complete_root_dir = configs_from_json.bbBarDir;
        heavySector = "beauty";
    }
    if (strcmp(FLAVOUR, "CHARM")  == 0) {
        complete_root_dir = configs_from_json.ccBarDir;
        heavySector = "charm";
    }
    if (heavySector.empty()) {
        throw std::runtime_error(
            "Unsupported flavour in calculateYieldsVector: " +
            std::string(FLAVOUR ? FLAVOUR : "<null>"));
    }
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
    const std::vector<std::string> vSubsampleErrorBinsToExclude =
        configs_from_json.vSubsampleErrorBinsToExclude;
    const Int_t nTUNES = static_cast<Int_t>(vTUNES.size());
    const Int_t nDependencies = static_cast<Int_t>(vBinsFromTHnSparse.size());

    // TODO: make these vectors into arrays, don't think vector is necessary
    // and the subYields are stored in an array anyways
    YieldsAndErrorsMap mapYieldsAndErrors;
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYields;
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYieldsErrors;
    std::map<std::string, std::vector<std::vector<std::vector<Double_t>>>> mapYieldsRatioErrors;
    bool observedPairSelectionMode = false;
    PairSelectionProjectionMode commonPairSelectionMode =
        PairSelectionProjectionMode::kLegacyPlotRecutsV1;
    const auto observePairSelectionMode =
        [&](PairSelectionProjectionMode mode, const std::string& path) {
            if (!observedPairSelectionMode) {
                commonPairSelectionMode = mode;
                observedPairSelectionMode = true;
                std::cout
                    << "PAIR_INPUT_SELECTION mode="
                    << PairSelectionProjectionModeName(mode)
                    << " first_file=" << path << std::endl;
                std::cout
                    << "PAIR_COMBINATORICS"
                    << " selection_mode="
                    << PairSelectionProjectionModeName(mode)
                    << " configured_mode=" << PAIR_COMBINATORICS_MODE
                    << " same_sign_factor=" << SAME_SIGN_PAIR_FACTOR
                    << " first_file=" << path
                    << " status=PASS" << std::endl;
                return;
            }
            RequireMatchingPairSelectionModes(
                commonPairSelectionMode, mode,
                "one plotting invocation (file " + path + ")");
        };

    // TODO: make vTUNES.size into nTUNES, like in the plotting functions

    TPad *pCharmMeson = nullptr;
    TPad *pCharmBaryon = nullptr;
    TPad *pCharmMesonSub = nullptr;
    TPad *pCharmBaryonSub = nullptr;
    TPad *pBeautyMeson = nullptr;
    TPad *pBeautyBaryon = nullptr;
    TPad *pBeautyMesonSub = nullptr;
    TPad *pBeautyBaryonSub = nullptr;
    if (DRAW_CORRELATION_PLOTS) {
        if (strcmp(FLAVOUR, "CHARM") == 0) {
            cAngularCorrelations->cd();
            pCharmMeson      = createMiniPad("pCharmMeson",     0.00,0.50,0.50,1.00);
            pCharmBaryon     = createMiniPad("pCharmBaryon",    0.50,0.50,1.00,1.00);
            pCharmMesonSub   = createMiniPad("pCharmMesonSub",  0.00,0.00,0.50,0.50);
            pCharmBaryonSub  = createMiniPad("pCharmBaryonSub", 0.50,0.00,1.00,0.50);
            pCharmMeson->cd(); gPad->SetLogy();
            pCharmBaryon->cd(); gPad->SetLogy();
        }
        if (strcmp(FLAVOUR, "BEAUTY") == 0) {
            cAngularCorrelations->cd();
            pBeautyMeson      = createMiniPad("pBeautyMeson",     0.00,0.50,0.50,1.00);
            pBeautyBaryon     = createMiniPad("pBeautyBaryon",    0.50,0.50,1.00,1.00);
            pBeautyMesonSub   = createMiniPad("pBeautyMesonSub",  0.00,0.00,0.50,0.50);
            pBeautyBaryonSub  = createMiniPad("pBeautyBaryonSub", 0.50,0.00,1.00,0.50);
            pBeautyMeson->cd(); gPad->SetLogy();
            pBeautyBaryon->cd(); gPad->SetLogy();
        }
    }

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
        const ReferenceAssociateSelection referenceSelection =
            ResolveReferenceAssociateSelection(
                vTriggerAssociateOSandSS,
                std::string(FLAVOUR) + " trigger '" + trigger + "'");
        const std::vector<Int_t> associateProcessingOrder =
            ReferenceFirstAssociateOrder(
                vTriggerAssociateOSandSS.size(),
                referenceSelection.index);
        std::cout
            << "REFERENCE_ASSOCIATE"
            << " flavour=" << FLAVOUR
            << " trigger=" << trigger
            << " pdg=" << referenceSelection.pdg
            << " index=" << referenceSelection.index
            << " os_file="
            << vTriggerAssociateOSandSS[referenceSelection.index].OS
            << " source=generated_pair_registry"
            << std::endl;
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


            const auto thresholdsForTune =
                configs_from_json.multiplicityPercentileThresholdsByTune.find(
                    TUNE);
            if (thresholdsForTune ==
                configs_from_json
                    .multiplicityPercentileThresholdsByTune.end()) {
                throw std::runtime_error(
                    "Missing frozen multiplicity definition for tune " +
                    TUNE);
            }
            const std::map<double, double>& percentileToMultiplicity =
                thresholdsForTune->second;

            // Process the metadata-selected reference first so every block
            // ratio has its matching denominator, while retaining the
            // configured associate order in all stored/drawn vectors.
            for (const Int_t j : associateProcessingOrder) {


                TriggerAssociateOSandSS fileNamesOSandSS = vTriggerAssociateOSandSS[j];
                std::cout << "starting loop over OS file: " << fileNamesOSandSS.OS << " and SS file: " << fileNamesOSandSS.SS << std::endl;
                const std::string osFilePath = ResolveCompleteRootFile(base_dir, TUNE, complete_root_dir, fileNamesOSandSS.OS);
                const std::string ssFilePath = ResolveCompleteRootFile(base_dir, TUNE, complete_root_dir, fileNamesOSandSS.SS);
                TFile *OStree = OpenRootFileOrThrow(osFilePath);
                TFile *SStree = OpenRootFileOrThrow(ssFilePath);
                const PairSelectionProjectionMode osSelectionMode =
                    ValidatePairInputSelectionContract(
                        OStree, PAIR_INPUT_SELECTION_CONTRACT,
                        complete_root_dir, osFilePath);
                const PairSelectionProjectionMode ssSelectionMode =
                    ValidatePairInputSelectionContract(
                        SStree, PAIR_INPUT_SELECTION_CONTRACT,
                        complete_root_dir, ssFilePath);
                RequireMatchingPairSelectionModes(
                    osSelectionMode, ssSelectionMode,
                    "central OS/SS pair " + osFilePath + " / " +
                    ssFilePath);
                ValidatePairCombinatoricsForSelectionMode(
                    osSelectionMode, PAIR_COMBINATORICS_MODE,
                    SAME_SIGN_PAIR_FACTOR,
                    PAIR_INPUT_SELECTION_CONTRACT, osFilePath);
                ValidatePairCombinatoricsForSelectionMode(
                    ssSelectionMode, PAIR_COMBINATORICS_MODE,
                    SAME_SIGN_PAIR_FACTOR,
                    PAIR_INPUT_SELECTION_CONTRACT, ssFilePath);
                ValidateConfiguredPairFileIdentity(
                    OStree, osSelectionMode,
                    PAIR_INPUT_SELECTION_CONTRACT,
                    complete_root_dir, fileNamesOSandSS, true,
                    heavySector, osFilePath);
                ValidateConfiguredPairFileIdentity(
                    SStree, ssSelectionMode,
                    PAIR_INPUT_SELECTION_CONTRACT,
                    complete_root_dir, fileNamesOSandSS, false,
                    heavySector, ssFilePath);
                observePairSelectionMode(osSelectionMode, osFilePath);
                observePairSelectionMode(ssSelectionMode, ssFilePath);
                std::cout << std::endl;

                // The percentile thresholds were derived once from the
                // tune-level central multiplicity identity and validated
                // against every configured central and block pair file.
                if (VERBOSE) {
                    for (const auto& [percentile, mult] : percentileToMultiplicity) {
                        std::cout
                        << percentile
                        << "% -> multiplicity "
                        << mult
                        << std::endl;
                    }
                }
                THnSparseD *hCorrelationsOS =
                    GetObjectOrThrow<THnSparseD>(OStree, "hCorrelations", osFilePath);
                THnSparseD *hCorrelationsSS =
                    GetObjectOrThrow<THnSparseD>(SStree, "hCorrelations", ssFilePath);
                THnSparseD *hTrKinematicsOS =
                    GetObjectOrThrow<THnSparseD>(OStree, "hTrKinematics", osFilePath);
                THnSparseD *hTrKinematicsSS =
                    GetObjectOrThrow<THnSparseD>(SStree, "hTrKinematics", ssFilePath);

                // Loop over DEPENDENCIES
                for (Int_t k=0; k<nDependencies; k++) {

                    BinsFromTHnSparse binFromTHnSparse = vBinsFromTHnSparse[k];
                    if (VERBOSE) {
                        const auto displayedMultiplicityRange =
                            GetDiscreteMultiplicityRange(
                                percentileToMultiplicity,
                                binFromTHnSparse.multiplicityMin,
                                binFromTHnSparse.multiplicityMax);
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
                            << " | Mult=[" << displayedMultiplicityRange.first
                            << ", " << displayedMultiplicityRange.second << "]"
                        << std::endl;
                        std::cout << std::endl;
                    }

                    // Add correct multiplicity cut to project out the relevant histograms from the THnSparse
                    BinsFromTHnSparse cuts{};
                    cuts.triggerPhiMin = binFromTHnSparse.triggerPhiMin;
                    cuts.triggerPhiMax = binFromTHnSparse.triggerPhiMax;
                    cuts.assocPhiMin = binFromTHnSparse.assocPhiMin;
                    cuts.assocPhiMax = binFromTHnSparse.assocPhiMax;
                    cuts.triggerEtaMin = binFromTHnSparse.triggerEtaMin;
                    cuts.triggerEtaMax = binFromTHnSparse.triggerEtaMax;
                    cuts.assocEtaMin = binFromTHnSparse.assocEtaMin;
                    cuts.assocEtaMax = binFromTHnSparse.assocEtaMax;
                    cuts.triggerPtMin = binFromTHnSparse.triggerPtMin;
                    cuts.triggerPtMax = binFromTHnSparse.triggerPtMax;
                    cuts.assocPtMin = binFromTHnSparse.assocPtMin;
                    cuts.assocPtMax = binFromTHnSparse.assocPtMax;
                    // Definition of multiplicity is 'reversed' w.r.t. json
                    // The way below it cuts on [lower_multiplicity, higher_multiplicity]
                    // Which is what we want
                    const auto multiplicityRange =
                        GetDiscreteMultiplicityRange(
                            percentileToMultiplicity,
                            binFromTHnSparse.multiplicityMin,
                            binFromTHnSparse.multiplicityMax);
                    cuts.multiplicityMin = multiplicityRange.first;
                    cuts.multiplicityMax = multiplicityRange.second;

                    // Retreive the histograms from the correlations THnSparse (Δφ, Δη, TrPt, AsPt, multiplicity)
                    // THnSparseD *hAsKinematics = (THnSparseD*)OStree->Get("hAsKinematics");
                    // Apply cuts to THnSparses
                    // Retreive the TH1 hDPhiOS/SS and hTrPtOS/SS objects as before
                    // Maybe add one element 'binLabel' to the BinsFromTHnSparse struct?
                    TH1D *hDPhiOS = GetCorrelationHistograms(
                        hCorrelationsOS, cuts, osSelectionMode, "OS");
                    TH1D *hDPhiSS = GetCorrelationHistograms(
                        hCorrelationsSS, cuts, ssSelectionMode, "SS");
                    TH1D *hTrPtOS = GetTriggerPtHistograms(
                        hTrKinematicsOS, cuts, osSelectionMode, "OS");
                    TH1D *hTrPtSS = GetTriggerPtHistograms(
                        hTrKinematicsSS, cuts, ssSelectionMode, "SS");
                    const Double_t centralTriggerCount = hTrPtOS->Integral();

                    if (VERBOSE) {
                        std::cout << "hDPhiOS->GetEntries() = " << hDPhiOS->GetEntries() << std::endl;
                        std::cout << "hDPhiSS0>GetEntries() = " << hDPhiSS->GetEntries() << std::endl;
                    }

                    // Prevent double-counting
                    if (strcmp((fileNamesOSandSS.trigger).c_str(), 
                            (fileNamesOSandSS.associateSS).c_str()) == 0) { 
                        hDPhiSS->Scale(SAME_SIGN_PAIR_FACTOR); }


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


                    const bool drawThisCorrelation =
                        DRAW_CORRELATION_PLOTS &&
                        IsIntegratedMultiplicityBin(binFromTHnSparse) &&
                        TUNE == "MONASH" &&
                        (fileNamesOSandSS.OS == "BplusBminus.root" ||
                         fileNamesOSandSS.OS == "LbbarBminus.root" ||
                         fileNamesOSandSS.OS == "DplusDminus.root" ||
                         fileNamesOSandSS.OS == "LambdacplusDminus.root");

                    // Calculate the yield and per-bin correlation errors by
                    // subsampling with N disjoint blocks.
                    // Not the most efficient way, but it is straightforward and clear
                    // and anyways the files are quite small so it doesn't take too long
                    const bool requiredByCanvas = IsBinUsedByAnyCanvas(
                        configs_from_json, FLAVOUR, trigger,
                        binFromTHnSparse.hDPhi);
                    const bool excludeSubsampleError =
                        isInVector(
                            binFromTHnSparse.hDPhi,
                            vSubsampleErrorBinsToExclude) ||
                        (!SUBSAMPLE_COVERAGE_AUDIT &&
                         !drawThisCorrelation && !requiredByCanvas);
                    std::vector<std::vector<Double_t>> subOSBinValues;
                    std::vector<std::vector<Double_t>> subSSBinValues;
                    std::vector<std::vector<Double_t>> subDifferenceBinValues;
                    if (drawThisCorrelation) {
                        const std::size_t binSlots =
                            static_cast<std::size_t>(hDPhiOS->GetNbinsX() + 1);
                        subOSBinValues.resize(binSlots);
                        subSSBinValues.resize(binSlots);
                        subDifferenceBinValues.resize(binSlots);
                    }
                    if (CALCULATE_ERRORS && excludeSubsampleError) {
                        const Double_t unavailableError =
                            std::numeric_limits<Double_t>::quiet_NaN();
                        SetNestedYieldValue(vYieldsErrors, i, j, k, unavailableError);
                        SetNestedYieldValue(vYieldsRatioErrors, i, j, k, unavailableError);
                        std::cout
                            << "subsample error coverage excluded"
                            << " flavour=" << FLAVOUR
                            << " tune=" << TUNE
                            << " pair=" << fileNamesOSandSS.OS
                            << " bin=" << binFromTHnSparse.hDPhi
                            << " reason="
                            << (requiredByCanvas
                                    ? "configured-production-coverage"
                                    : "not-used-by-any-output-canvas")
                            << std::endl;
                    }
                    if (CALCULATE_ERRORS && !excludeSubsampleError) {
                        std::vector<Double_t> subYieldValues;
                        std::vector<Double_t> subRatioValues;
                        std::vector<Double_t> subTriggerCounts;
                        subYieldValues.reserve(nSubSamples);
                        subRatioValues.reserve(nSubSamples);
                        subTriggerCounts.reserve(nSubSamples);


                        for (Int_t l = 1; l < nSubSamples+1; l++) {


                            const std::string osSubSamplePath = ResolveSubSampleRootFile(complete_root_dir_sub_samples, TUNE, l, fileNamesOSandSS.OS);
                            const std::string ssSubSamplePath = ResolveSubSampleRootFile(complete_root_dir_sub_samples, TUNE, l, fileNamesOSandSS.SS);
                            TFile *OStree_subSamples = OpenRootFileOrThrow(osSubSamplePath);
                            TFile *SStree_subSamples = OpenRootFileOrThrow(ssSubSamplePath);
                            const PairSelectionProjectionMode
                                osSubsampleSelectionMode =
                                    ValidatePairInputSelectionContract(
                                        OStree_subSamples,
                                        PAIR_INPUT_SELECTION_CONTRACT,
                                        complete_root_dir,
                                        osSubSamplePath);
                            const PairSelectionProjectionMode
                                ssSubsampleSelectionMode =
                                    ValidatePairInputSelectionContract(
                                        SStree_subSamples,
                                        PAIR_INPUT_SELECTION_CONTRACT,
                                        complete_root_dir,
                                        ssSubSamplePath);
                            RequireMatchingPairSelectionModes(
                                osSubsampleSelectionMode,
                                ssSubsampleSelectionMode,
                                "subsample OS/SS pair " +
                                    osSubSamplePath + " / " +
                                    ssSubSamplePath);
                            RequireMatchingPairSelectionModes(
                                osSelectionMode,
                                osSubsampleSelectionMode,
                                "central/subsample pair " +
                                    osFilePath + " / " +
                                    osSubSamplePath);
                            ValidatePairCombinatoricsForSelectionMode(
                                osSubsampleSelectionMode,
                                PAIR_COMBINATORICS_MODE,
                                SAME_SIGN_PAIR_FACTOR,
                                PAIR_INPUT_SELECTION_CONTRACT,
                                osSubSamplePath);
                            ValidatePairCombinatoricsForSelectionMode(
                                ssSubsampleSelectionMode,
                                PAIR_COMBINATORICS_MODE,
                                SAME_SIGN_PAIR_FACTOR,
                                PAIR_INPUT_SELECTION_CONTRACT,
                                ssSubSamplePath);
                            ValidateConfiguredPairFileIdentity(
                                OStree_subSamples,
                                osSubsampleSelectionMode,
                                PAIR_INPUT_SELECTION_CONTRACT,
                                complete_root_dir, fileNamesOSandSS, true,
                                heavySector, osSubSamplePath);
                            ValidateConfiguredPairFileIdentity(
                                SStree_subSamples,
                                ssSubsampleSelectionMode,
                                PAIR_INPUT_SELECTION_CONTRACT,
                                complete_root_dir, fileNamesOSandSS, false,
                                heavySector, ssSubSamplePath);
                            observePairSelectionMode(
                                osSubsampleSelectionMode,
                                osSubSamplePath);
                            observePairSelectionMode(
                                ssSubsampleSelectionMode,
                                ssSubSamplePath);

                            // Retreive the histograms from the correlations THnSparse (Δφ, Δη, TrPt, AsPt, multiplicity)
                            // THnSparseD *hAsKinematics = (THnSparseD*)OStree->Get("hAsKinematics");
                            THnSparseD *hCorrelationsOS_subSamples = GetObjectOrThrow<THnSparseD>(OStree_subSamples, "hCorrelations", osSubSamplePath);
                            THnSparseD *hCorrelationsSS_subSamples = GetObjectOrThrow<THnSparseD>(SStree_subSamples, "hCorrelations", ssSubSamplePath);
                            THnSparseD *hTrKinematicsOS_subSamples = GetObjectOrThrow<THnSparseD>(OStree_subSamples, "hTrKinematics", osSubSamplePath);
                            THnSparseD *hTrKinematicsSS_subSamples = GetObjectOrThrow<THnSparseD>(SStree_subSamples, "hTrKinematics", ssSubSamplePath); // in principle the same as OS...

                            // Apply cuts to THnSparses
                            // Retreive the TH1 hDPhiOS/SS and hTrPtOS/SS objects as before
                            // Maybe add one element 'binLabel' to the BinsFromTHnSparse struct?
                            TH1D *hDPhiOS_subSamples =
                                GetCorrelationHistograms(
                                    hCorrelationsOS_subSamples, cuts,
                                    osSubsampleSelectionMode);
                            TH1D *hDPhiSS_subSamples =
                                GetCorrelationHistograms(
                                    hCorrelationsSS_subSamples, cuts,
                                    ssSubsampleSelectionMode);
                            TH1D *hTrPtOS_subSamples =
                                GetTriggerPtHistograms(
                                    hTrKinematicsOS_subSamples, cuts,
                                    osSubsampleSelectionMode);
                            TH1D *hTrPtSS_subSamples =
                                GetTriggerPtHistograms(
                                    hTrKinematicsSS_subSamples, cuts,
                                    ssSubsampleSelectionMode);
                            subTriggerCounts.push_back(
                                hTrPtOS_subSamples->Integral());

                            // Apply the same same-sign double-counting correction used for the central yield.
                            if (strcmp((fileNamesOSandSS.trigger).c_str(),
                                       (fileNamesOSandSS.associateSS).c_str()) == 0) {
                                hDPhiSS_subSamples->Scale(
                                    SAME_SIGN_PAIR_FACTOR);
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
                            if (drawThisCorrelation) {
                                for (Int_t bin = 1;
                                     bin <= hDPhiOS_subSamples->GetNbinsX();
                                     ++bin) {
                                    const Double_t os =
                                        hDPhiOS_subSamples->GetBinContent(bin);
                                    const Double_t ss =
                                        hDPhiSS_subSamples->GetBinContent(bin);
                                    subOSBinValues[bin].push_back(os);
                                    subSSBinValues[bin].push_back(ss);
                                    subDifferenceBinValues[bin].push_back(
                                        os - ss);
                                }
                            }
                            if (VERBOSE) {
                                std::cout << "vSubYields[" << i << "][" << j << "][" << k << "][" << (l - 1) << "] = " << subYield << std::endl;
                                std::cout << std::endl;
                            }

                            subYieldValues.push_back(subYield);
                            if (static_cast<std::size_t>(j) !=
                                referenceSelection.index) {
                                subRatioValues.push_back(safeRatio(
                                    vSubYields[i][j][k][l - 1],
                                    vSubYields[i]
                                              [referenceSelection.index][k]
                                              [l - 1]));
                            }

                            // Free memory
                            delete hDPhiOS_subSamples;
                            delete hDPhiSS_subSamples;
                            delete hTrPtOS_subSamples;
                            delete hTrPtSS_subSamples;
                            DeleteInputObject(OStree_subSamples, hCorrelationsOS_subSamples);
                            DeleteInputObject(SStree_subSamples, hCorrelationsSS_subSamples);
                            DeleteInputObject(OStree_subSamples, hTrKinematicsOS_subSamples);
                            DeleteInputObject(SStree_subSamples, hTrKinematicsSS_subSamples);
                            CloseAndDeleteInputFile(OStree_subSamples);
                            CloseAndDeleteInputFile(SStree_subSamples);


                        } // Loop over SUBSAMPLES


                        const bool isReference =
                            static_cast<std::size_t>(j) ==
                            referenceSelection.index;
                        const SubsampleStatistics yieldStats =
                            calculateSubsampleStatistics(subYieldValues);
                        const SubsampleStatistics yieldRatioStats =
                            calculateSubsampleStatistics(subRatioValues);
                        const Double_t referenceYield =
                            vYields[i][referenceSelection.index][k];
                        const Double_t centralRatio = isReference
                            ? std::numeric_limits<Double_t>::quiet_NaN()
                            : safeRatio(yield, referenceYield);
                        const bool requirePositiveFinalError =
                            requiredByCanvas || drawThisCorrelation;
                        const SubsampleTechnicalCoverage technicalCoverage =
                            EvaluateSubsampleTechnicalCoverage(
                                yield, referenceYield, centralRatio,
                                yieldStats, yieldRatioStats,
                                nSubSamples, isReference,
                                requirePositiveFinalError);
                        // Copy the structured-binding element before capture:
                        // capturing it directly is a C++20 extension, while
                        // the supported ROOT/ACLiC toolchain is C++17.
                        const std::string triggerName = trigger;
                        const auto recordCoverageFailure =
                            [&](const char* kind,
                                const std::string& message) {
                                ++mapYieldsAndErrors
                                      .subsampleCoverageFailures;
                                std::cout
                                    << "SUBSAMPLE_COVERAGE_FAILURE"
                                    << " kind=" << kind
                                    << " flavour=" << FLAVOUR
                                    << " trigger=" << triggerName
                                    << " tune=" << TUNE
                                    << " pair="
                                    << fileNamesOSandSS.OS
                                    << " bin="
                                    << binFromTHnSparse.hDPhi
                                    << " message=" << message
                                    << std::endl;
                                if (!SUBSAMPLE_COVERAGE_AUDIT) {
                                    throw std::runtime_error(message);
                                }
                            };
                        if (!technicalCoverage.yieldComplete) {
                            recordCoverageFailure(
                                "yield",
                                Form("yield technical coverage incomplete: "
                                     "central=%.17g n=%d/%d stdDev=%.17g "
                                     "stdError=%.17g positive_required=%s",
                                     yield, yieldStats.nValues, nSubSamples,
                                     yieldStats.stdDev,
                                     yieldStats.stdError,
                                     (requirePositiveFinalError ||
                                              technicalCoverage
                                                  .yieldNonDegenerate
                                          ? "true"
                                          : "false")));
                        }
                        if (!technicalCoverage.ratioComplete) {
                            recordCoverageFailure(
                                "ratio",
                                Form("ratio technical coverage incomplete: "
                                     "central=%.17g reference=%.17g "
                                     "n=%d/%d stdDev=%.17g "
                                     "stdError=%.17g positive_required=%s",
                                     centralRatio, referenceYield,
                                     yieldRatioStats.nValues,
                                     nSubSamples,
                                     yieldRatioStats.stdDev,
                                     yieldRatioStats.stdError,
                                     (requirePositiveFinalError ||
                                              technicalCoverage
                                                  .ratioNonDegenerate
                                          ? "true"
                                          : "false")));
                        }
                        const Double_t unavailableError =
                            std::numeric_limits<Double_t>::quiet_NaN();
                        Double_t yieldError =
                            technicalCoverage.yieldComplete
                            ? yieldStats.stdError : unavailableError;
                        Double_t yieldRatioError =
                            !isReference &&
                                    technicalCoverage.ratioComplete
                                ? yieldRatioStats.stdError
                                : unavailableError;
                        std::ostringstream blockTriggerCounts;
                        for (std::size_t block = 0;
                             block < subTriggerCounts.size(); ++block) {
                            if (block != 0) blockTriggerCounts << ",";
                            blockTriggerCounts << subTriggerCounts[block];
                        }
                        std::cout
                            << "UNCERTAINTY_MATRIX"
                            << " flavour=" << FLAVOUR
                            << " trigger=" << trigger
                            << " tune=" << TUNE
                            << " associate=" << fileNamesOSandSS.associateOS
                            << " associate_pdg="
                            << fileNamesOSandSS.associateOSPdg
                            << " reference_pdg="
                            << referenceSelection.pdg
                            << " reference_index="
                            << referenceSelection.index
                            << " is_reference="
                            << (static_cast<std::size_t>(j) ==
                                        referenceSelection.index
                                    ? "true"
                                    : "false")
                            << " bin=" << binFromTHnSparse.hDPhi
                            << " central_triggers=" << centralTriggerCount
                            << " block_triggers=" << blockTriggerCounts.str()
                            << " finite_yields=" << yieldStats.nValues
                            << " finite_ratios="
                            << (isReference
                                    ? "NA"
                                    : std::to_string(
                                          yieldRatioStats.nValues))
                            << " central_yield=" << yield
                            << " yield_sem=" << yieldError
                            << " reference_yield=" << referenceYield
                            << " ratio_sem="
                            << (isReference
                                    ? "NA"
                                    : Form("%.17g", yieldRatioError))
                            << " yield_degenerate="
                            << (!technicalCoverage.yieldNonDegenerate
                                    ? "true"
                                    : "false")
                            << " ratio_degenerate="
                            << (isReference
                                    ? "NA"
                                    : (technicalCoverage.ratioNonDegenerate
                                           ? "false"
                                           : "true"))
                            << " yield_status="
                            << (technicalCoverage.yieldComplete
                                    ? "PASS"
                                    : "FAIL")
                            << " ratio_status="
                            << (isReference
                                    ? "NOT_APPLICABLE"
                                    : (technicalCoverage.ratioComplete
                                           ? "PASS"
                                           : "FAIL"))
                            << " denominator_status="
                            << (isReference
                                    ? "NOT_APPLICABLE"
                                    : (std::isfinite(referenceYield) &&
                                               referenceYield != 0.0
                                           ? "valid"
                                           : "invalid"))
                            << " status="
                            << (technicalCoverage.complete
                                    ? "PASS"
                                    : "FAIL")
                            << std::endl;
                        if (VERBOSE) {
                            std::cout << "subsample yield stats n=" << yieldStats.nValues
                                      << " mean=" << yieldStats.mean
                                      << " stdDev=" << yieldStats.stdDev
                                      << " stdError=" << yieldStats.stdError << std::endl;
                            if (isReference) {
                                std::cout
                                    << "subsample ratio stats"
                                    << " status=NOT_APPLICABLE"
                                    << " reason=structural_reference_self_ratio"
                                    << std::endl;
                            } else {
                                std::cout << "subsample ratio stats n=" << yieldRatioStats.nValues
                                          << " mean=" << yieldRatioStats.mean
                                          << " stdDev=" << yieldRatioStats.stdDev
                                          << " stdError=" << yieldRatioStats.stdError << std::endl;
                            }
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
                            std::cout << "vYieldsRatioErrors[" << i << "][" << j << "][" << k << "] = ";
                            if (isReference) {
                                std::cout << "NOT_APPLICABLE";
                            } else {
                                std::cout << vYieldsRatioErrors[i][j][k];
                            }
                            std::cout << std::endl;
                            std::cout << std::endl;
                        }


                    } // calculate errors

                    if (drawThisCorrelation) {
                        if (!CALCULATE_ERRORS || excludeSubsampleError) {
                            throw std::runtime_error(
                                "Final angular-correlation panels require "
                                "ten-block subsample uncertainties: " +
                                fileNamesOSandSS.OS);
                        }
                        const std::string uncertaintyContext =
                            std::string(FLAVOUR) + "_" + TUNE + "_" +
                            fileNamesOSandSS.OS;
                        ApplyCorrelationSubsampleSEM(
                            hDPhiOS, subOSBinValues, nSubSamples,
                            uncertaintyContext + "_OS");
                        ApplyCorrelationSubsampleSEM(
                            hDPhiSS, subSSBinValues, nSubSamples,
                            uncertaintyContext + "_SS");

                        TH1D *hSub = static_cast<TH1D*>(
                            hDPhiOS->Clone(
                                Form("%s_sub",
                                     fileNamesOSandSS.OS.c_str())));
                        hSub->SetDirectory(nullptr);
                        hSub->Add(hDPhiSS, -1.0);
                        ApplyCorrelationSubsampleSEM(
                            hSub, subDifferenceBinValues, nSubSamples,
                            uncertaintyContext + "_OSminusSS");

                        TPad *padOSSS = nullptr;
                        TPad *padSub = nullptr;
                        TString title;
                        if (fileNamesOSandSS.OS ==
                            "DplusDminus.root") {
                            padOSSS = pCharmMeson;
                            padSub = pCharmMesonSub;
                            title = "D^{+} trigger";
                        } else if (fileNamesOSandSS.OS ==
                                   "LambdacplusDminus.root") {
                            padOSSS = pCharmBaryon;
                            padSub = pCharmBaryonSub;
                            title = "#Lambda_{c}^{+} trigger";
                        } else if (fileNamesOSandSS.OS ==
                                   "BplusBminus.root") {
                            padOSSS = pBeautyMeson;
                            padSub = pBeautyMesonSub;
                            title = "B^{+} trigger";
                        } else if (fileNamesOSandSS.OS ==
                                   "LbbarBminus.root") {
                            padOSSS = pBeautyBaryon;
                            padSub = pBeautyBaryonSub;
                            title = "#bar#Lambda_{b}^{0} trigger";
                        }
                        if (!padOSSS || !padSub) {
                            delete hSub;
                            throw std::runtime_error(
                                "Missing configured angular-correlation pad "
                                "for " + fileNamesOSandSS.OS);
                        }

                        cAngularCorrelations->cd();
                        padOSSS->cd();
                        hDPhiOS->SetLineColor(kBlack);
                        hDPhiOS->SetMarkerColor(kBlack);
                        hDPhiOS->SetMarkerStyle(20);
                        hDPhiSS->SetLineColor(kRed + 1);
                        hDPhiSS->SetMarkerColor(kRed + 1);
                        hDPhiSS->SetMarkerStyle(24);
                        hDPhiSS->SetLineStyle(2);
                        hDPhiOS->SetTitle(title);
                        hDPhiOS->GetXaxis()->SetTitle("#Delta#varphi");
                        hDPhiOS->GetYaxis()->SetTitle(
                            "pairs per trigger / bin");
                        hDPhiOS->GetYaxis()->SetRangeUser(1e-6, 1e-2);
                        hDPhiOS->SetStats(0);
                        hDPhiSS->SetStats(0);
                        TH1D* drawnOS = static_cast<TH1D*>(
                            hDPhiOS->DrawCopy("E1"));
                        TH1D* drawnSS = static_cast<TH1D*>(
                            hDPhiSS->DrawCopy("E1 same"));

                        auto leg = new TLegend(0.55, 0.70, 0.88, 0.88);
                        leg->SetBorderSize(0);
                        leg->SetFillStyle(0);
                        leg->AddEntry(drawnOS, "OS", "lep");
                        leg->AddEntry(drawnSS, "SS", "lep");
                        leg->AddEntry(
                            static_cast<TObject*>(nullptr),
                            "0-100%, 10-block SEM", "");
                        leg->Draw();

                        padSub->cd();
                        hSub->SetLineColor(kBlue + 1);
                        hSub->SetMarkerColor(kBlue + 1);
                        hSub->SetMarkerStyle(20);
                        hSub->SetTitle("");
                        hSub->GetXaxis()->SetTitle("#Delta#varphi");
                        hSub->GetYaxis()->SetTitle(
                            "(OS-SS) pairs per trigger / bin");
                        hSub->SetStats(0);
                        hSub->DrawCopy("E1");
                        delete hSub;
                    }

                    delete hDPhiOS;
                    delete hDPhiSS;
                    delete hTrPtOS;
                    delete hTrPtSS;


                } // Loop over DEPENDENCIES


                DeleteInputObject(OStree, hCorrelationsOS);
                DeleteInputObject(SStree, hCorrelationsSS);
                DeleteInputObject(OStree, hTrKinematicsOS);
                DeleteInputObject(SStree, hTrKinematicsSS);
                CloseAndDeleteInputFile(OStree);
                CloseAndDeleteInputFile(SStree);
                ReleaseUnusedHeap();


            } // Loop over ASSOCIATES


        } // Loop over TUNES


        // Store the {trigger, vYields} objects in the map
        std::cout << "storing trigger " << trigger << " in yields map" << std::endl;
        mapYields[trigger] = std::move(vYields);
        mapYieldsErrors[trigger] = std::move(vYieldsErrors);
        mapYieldsRatioErrors[trigger] = std::move(vYieldsRatioErrors);
        mapYieldsAndErrors.mapReferenceAssociateIndex[trigger] =
            referenceSelection.index;
        mapYieldsAndErrors.mapReferenceMesonPdg[trigger] =
            referenceSelection.pdg;

        // Retreive the vYields for this trigger
        mapYieldsAndErrors.mapYields = mapYields;
        if (CALCULATE_ERRORS) { mapYieldsAndErrors.mapYieldsErrors = mapYieldsErrors; }
        if (CALCULATE_ERRORS) { mapYieldsAndErrors.mapYieldsRatioErrors = mapYieldsRatioErrors; }


    } // Loop over TRIGGERS

    if (DRAW_CORRELATION_PLOTS) {
        const std::string correlationPlotDir = ResolvePathFromBase("PlottingScripts/Plots/THnSparse/Correlations", FindHadronizationBase());
        writeCanvasToFiles(VERBOSE, cAngularCorrelations, correlationPlotDir, Form("%sCorrelations_MONASH", FLAVOUR));
    }

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
    std::vector<std::string> vBinsToIgnore = canvasConfigs.vBinsToIgnore;

    // Function that transforms the map storing trigger and vYieldsAndErrors into just vYieldsAndErrors
    auto vYieldsAndErrors = YieldsAndErrorsForGivenTrigger(canvasConfigs.TriggerToUse, mapYieldsAndErrors, CALCULATE_ERRORS);

    Int_t nTUNES = vTUNES.size();
    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    // Int_t nDependencies = vHistogramAndTriggerPtHistogramNames.size();
    Int_t nDependencies = vBinsFromTHnSparse.size();

    // Values will be drawn from a 2D vector of TH1D with number of ASSOCIATES bins
    // This way the TUNE and DEPENDENCY can be looped over, while the data points will be the ASSOCIATES
    std::vector<std::vector<TH1D*>> vHists(
        nTUNES, std::vector<TH1D*>(nDependencies, nullptr));
    if (VERBOSE) {
        std::cout << "number of associates: " << nAssociates << std::endl;
        std::cout << std::endl;
    }

    // We construct a map object that links the bin integer (integer k of vYields[i][j][k]) with the corresponding bin name
    // This way we can compute all yields in the beginning, but only draw the ones we are interested in
    // The bins that we want to draw are the ones we declare in the legend entries block of the json
    // usage example: dependencyMap[k] == "hDPhiM90_100"
    auto dependencyMap = CreateDependencyMap(vYieldsAndErrors, vBinsFromTHnSparse);

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
    TPad* cMiniPad = nullptr;
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

    std::map<std::string, Int_t> lineStyleDependencyMap = canvasConfigs.lineStyleDependencyMap;

    TLegend *legend = nullptr;
    std::map<std::string, std::string> legendEntriesMap = canvasConfigs.legendEntriesMap;
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        std::cout << "- Creating legend at positions x1(" << canvasConfigs.xMinLegend << "," << canvasConfigs.yMinLegend << ") and x2(" << canvasConfigs.xMaxLegend << "," << canvasConfigs.yMaxLegend << ")" << std::endl;
        legend = new TLegend(canvasConfigs.xMinLegend, canvasConfigs.yMinLegend, canvasConfigs.xMaxLegend, canvasConfigs.yMaxLegend);
        legend->SetBorderSize(0);
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
                    std::cout << "dependency map " << dependencyMap[k] << std::endl;
                    std::cout << std::endl;
                }

                if (isInVector(binFromTHnSparse.hDPhi, vBinsToIgnore)) {
                    if (VERBOSE) {
                        std::cout << "Configured not to draw bin "
                                  << binFromTHnSparse.hDPhi << std::endl;
                    }
                    continue;
                }

                // Check if this bin should be drawn or not
                // use binFromTHnSparse.hDPhi
                // TODO: allow also to use binLabel
                // TODO: make this verbose
                auto it = legendEntriesMap.find(dependencyMap[k]);
                if (it == legendEntriesMap.end()) { continue; }

                vHists[i][k] = new TH1D(Form("hYields_%s_%i_%i_%i_%s", FLAVOUR, i, j, k, (canvasConfigs.canvasName).c_str()), Form("hYields_%s_%i_%i_%i_%s", FLAVOUR, i, j, k, (canvasConfigs.canvasName).c_str()), nAssociates, 0, nAssociates);
                const Double_t yield = vYieldsAndErrors.vYields[i][j][k];
                const Double_t yieldError = CALCULATE_ERRORS ? vYieldsAndErrors.vYieldsErrors[i][j][k] : 0.0;
                SetPlotPointOrThrow(
                    vHists[i][k], 1+j, yield, yieldError, CALCULATE_ERRORS,
                    canvasConfigs.setLogy,
                    canvasConfigs.yMinAxis, canvasConfigs.yMaxAxis,
                    Form("%s yield, tune=%s, associate=%s, bin=%s",
                         FLAVOUR, TUNE.c_str(), associateName.c_str(), binFromTHnSparse.hDPhi.c_str()));
                ApplyTuneVisualStyle(vHists[i][k], TUNE, true);
                cYields->cd();
                vHists[i][k]->Draw("same PE");
                if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                    cMiniPad->cd();
                    vHists[i][k]->Draw("same PE");
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
                const std::string legendKey = binFromTHnSparse.hDPhi + "::" + TUNE;
                if (legend != nullptr && alreadyInLegend.find(legendKey) == alreadyInLegend.end()) {
                    if (legendEntriesMap.find(binFromTHnSparse.hDPhi) != legendEntriesMap.end()) {
                        std::string displayName = legendEntriesMap[binFromTHnSparse.hDPhi];
                        if (vCanvasTUNES.size() > 1) { displayName += " (" + TUNE + ")"; }
                        if (VERBOSE) { std::cout << "Found displayName: " << displayName << std::endl; }
                        legend->AddEntry(vHists[i][k], displayName.c_str(), "lep");
                    } else {
                        if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                    }
                    alreadyInLegend.insert(legendKey);
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
                                  std::vector<Int_t> vIndexNominatorTUNES, Int_t indexDenominatorTUNE) {


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
    std::vector<std::string> vBinsToIgnore = canvasConfigs.vBinsToIgnore;

    for (const auto& indexNominatorTUNE : vIndexNominatorTUNES) { std::cout << " and TUNE = " << vTUNES[indexNominatorTUNE] << "/" << vTUNES[indexDenominatorTUNE] << " ***" << std::endl; }
    // Int_t indexNominatorTUNE = vIndexNominatorTUNES[0];

    // Function that transforms the map storing trigger and vYieldsAndErrors into just vYieldsAndErrors
    auto vYieldsAndErrors = YieldsAndErrorsForGivenTrigger(canvasConfigs.TriggerToUse, mapYieldsAndErrors, CALCULATE_ERRORS);

    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    Int_t nDependencies = vBinsFromTHnSparse.size();
    Int_t nTUNES = vIndexNominatorTUNES.size(); // nominator TUNES to be used in the TUNE ratios

    // Values will be drawn from a 2D vector of TH1D with number of ASSOCIATES bins
    // This way the TUNE and DEPENDENCY can be looped over, while the data points will be the ASSOCIATES
    std::vector<std::vector<TH1D*>> vHists(
        nDependencies, std::vector<TH1D*>(nTUNES, nullptr));
    if (VERBOSE) {
        std::cout << "number of associates: " << nAssociates << std::endl;
        std::cout << std::endl;
    }

    // We construct a map object that links the bin integer (integer k of vYields[i][j][k]) with the corresponding bin name
    // This way we can compute all yields in the beginning, but only draw the ones we are interested in
    // The bins that we want to draw are the ones we declare in the legend entries block of the json
    // usage example: dependencyMap[k] == "hDPhiM90_100"
    auto dependencyMap = CreateDependencyMap(vYieldsAndErrors, vBinsFromTHnSparse);

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
    TPad* cMiniPad = nullptr;
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

    std::map<std::string, Int_t> lineStyleDependencyMap = canvasConfigs.lineStyleDependencyMap;

    TLegend *legend = nullptr;
    std::map<std::string, std::string> legendEntriesMap = canvasConfigs.legendEntriesMap;
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        std::cout << "- Creating legend at positions x1(" << canvasConfigs.xMinLegend << "," << canvasConfigs.yMinLegend << ") and x2(" << canvasConfigs.xMaxLegend << "," << canvasConfigs.yMaxLegend << ")" << std::endl;
        legend = new TLegend(canvasConfigs.xMinLegend, canvasConfigs.yMinLegend, canvasConfigs.xMaxLegend, canvasConfigs.yMaxLegend);
        legend->SetBorderSize(0);
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

            if (isInVector(binFromTHnSparse.hDPhi, vBinsToIgnore)) {
                if (VERBOSE) {
                    std::cout << "Configured not to draw bin "
                              << binFromTHnSparse.hDPhi << std::endl;
                }
                continue;
            }

            // Check if this bin should be drawn or not
            // use binFromTHnSparse.hDPhi
            // TODO: allow also to use binLabel
            // TODO: make this verbose
            auto it = legendEntriesMap.find(dependencyMap[k]);
            if (it == legendEntriesMap.end()) { continue; }


            for (Int_t iTUNE=0; iTUNE < nTUNES; iTUNE++) {


                Int_t indexNominatorTUNE = vIndexNominatorTUNES[iTUNE];
                if (VERBOSE) { std::cout << "starting loop over nominator TUNE: " << indexNominatorTUNE << std::endl; }


                vHists[k][iTUNE] = new TH1D(Form("hYields_%s_%i_%i_%i_%s", FLAVOUR, j, k, iTUNE, (canvasConfigs.canvasName).c_str()), Form("hYields_%s_%i_%i_%i_%s", FLAVOUR, j, k, iTUNE, (canvasConfigs.canvasName).c_str()), nAssociates, 0, nAssociates);
                const Double_t numerator = vYieldsAndErrors.vYields[indexNominatorTUNE][j][k];
                const Double_t denominator = vYieldsAndErrors.vYields[indexDenominatorTUNE][j][k];
                const Double_t tuneRatio = safeRatio(numerator, denominator);
                const Double_t tuneRatioError = CALCULATE_ERRORS
                    ? propagateRatioError(
                        numerator, denominator,
                        vYieldsAndErrors.vYieldsErrors[indexNominatorTUNE][j][k],
                        vYieldsAndErrors.vYieldsErrors[indexDenominatorTUNE][j][k])
                    : 0.0;
                SetPlotPointOrThrow(
                    vHists[k][iTUNE], 1+j, tuneRatio, tuneRatioError, CALCULATE_ERRORS,
                    canvasConfigs.setLogy,
                    canvasConfigs.yMinAxis, canvasConfigs.yMaxAxis,
                    Form("%s tune ratio %s/%s, associate=%s, bin=%s",
                         FLAVOUR, vTUNES[indexNominatorTUNE].c_str(),
                         vTUNES[indexDenominatorTUNE].c_str(), associateName.c_str(),
                         binFromTHnSparse.hDPhi.c_str()));
                cYields->cd();
                ApplyTuneVisualStyle(vHists[k][iTUNE], vTUNES[indexNominatorTUNE], true);

                vHists[k][iTUNE]->Draw("same PE");
                if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                    cMiniPad->cd();
                    vHists[k][iTUNE]->Draw("same PE");
                }

                if (lineStyleDependencyMap.find(binFromTHnSparse.hDPhi) != lineStyleDependencyMap.end()) {
                    Int_t lineStyle = lineStyleDependencyMap[binFromTHnSparse.hDPhi];
                    vHists[k][iTUNE]->SetLineStyle(lineStyle);
                    if (VERBOSE) { std::cout << "Found lineStyle: " << lineStyle << std::endl; }
                } else {
                    if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                }

                // Draw legend
                const std::string numeratorTune = vTUNES[indexNominatorTUNE];
                const std::string denominatorTune = vTUNES[indexDenominatorTUNE];
                const std::string legendKey =
                    binFromTHnSparse.hDPhi + "::" + numeratorTune + "/" + denominatorTune;
                if (legend != nullptr && alreadyInLegend.find(legendKey) == alreadyInLegend.end()) {
                    if (legendEntriesMap.find(binFromTHnSparse.hDPhi) != legendEntriesMap.end()) {
                        std::string displayName = legendEntriesMap[binFromTHnSparse.hDPhi];
                        displayName += " (" + numeratorTune + "/" + denominatorTune + ")";
                        if (VERBOSE) { std::cout << "Found displayName: " << displayName << std::endl; }
                        legend->AddEntry(vHists[k][iTUNE], displayName.c_str(), "lep");
                    } else {
                        if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                    }
                    alreadyInLegend.insert(legendKey);
                }

                if (VERBOSE) { std::cout << std::endl; }


            } // loop over NOMINATOR TUNES


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
    std::vector<std::string> vBinsToIgnore = canvasConfigs.vBinsToIgnore;

    // Function that transforms the map storing trigger and vYieldsAndErrors into just vYieldsAndErrors
    auto vYieldsAndErrors = YieldsAndErrorsForGivenTrigger(canvasConfigs.TriggerToUse, mapYieldsAndErrors, CALCULATE_ERRORS);

    Int_t nTUNES = vTUNES.size();
    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    const ReferenceAssociateSelection drawingReference =
        ResolveReferenceAssociateSelection(
            vTriggerAssociateOSandSS,
            std::string(FLAVOUR) + " baryon/meson canvas trigger '" +
                canvasConfigs.TriggerToUse + "'");
    if (drawingReference.index !=
            vYieldsAndErrors.referenceAssociateIndex ||
        drawingReference.pdg != vYieldsAndErrors.referenceMesonPdg) {
        throw std::runtime_error(
            "Baryon/meson drawing reference differs from the reference used "
            "for block uncertainties");
    }
    const std::size_t referenceIndex = drawingReference.index;
    Int_t nDependencies;
    // We could have calculated more bins than we want to draw here, in that case, take the (non-empty) vector vBinsToIgnore
    // and subtract the template size
    if (vBinsToIgnore[0] != "NONE" && vBinsToIgnore[0] != "" && vBinsToIgnore[0] != "NULL") { nDependencies = vBinsFromTHnSparse.size() - vBinsToIgnore.size(); }
    else {nDependencies = vBinsFromTHnSparse.size(); }

    // We construct a map object that links the bin integer (integer k of vYields[i][j][k]) with the corresponding bin name
    // This way we can compute all yields in the beginning, but only draw the ones we are interested in
    // The bins that we want to draw are the ones we declare in the legend entries block of the json
    // usage example: dependencyMap[k] == "hDPhiM90_100"
    auto dependencyMap = CreateDependencyMap(vYieldsAndErrors, vBinsFromTHnSparse);

    // Values will be drawn from a 2D vector of TH1D with number of DEPENDENCIES bins
    // This way the TUNE and ASSOCIATE can be looped over, while the data points will be the DEPENDENCIES
    std::vector<std::vector<TH1D*>> vHists(
        nTUNES, std::vector<TH1D*>(nAssociates, nullptr));
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
    TPad* cMiniPad = nullptr;
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

    std::map<std::string, Int_t> lineStyleBaryonMap = canvasConfigs.lineStyleBaryonMap;

    TLegend *legend = nullptr;
    std::map<std::string, std::string> legendEntriesMap = canvasConfigs.legendEntriesMap;
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        std::cout << "- Creating legend at positions x1(" << canvasConfigs.xMinLegend << "," << canvasConfigs.yMinLegend << ") and x2(" << canvasConfigs.xMaxLegend << "," << canvasConfigs.yMaxLegend << ")" << std::endl;
        legend = new TLegend(canvasConfigs.xMinLegend, canvasConfigs.yMinLegend, canvasConfigs.xMaxLegend, canvasConfigs.yMaxLegend);
        legend->SetBorderSize(0);
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
            Int_t skippedBins = 0; // for the k-loop over skipped dependencies


            // Loop over DEPENDENCIES
            for (Int_t k=0; k<nDependencies+skippedBins; k++) {


                std::cout << "k = " << k << std::endl;
                // HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
                BinsFromTHnSparse binFromTHnSparse = vBinsFromTHnSparse[k];
                if (VERBOSE) { 
                    std::cout << "plotting histogram " << binFromTHnSparse.hDPhi << " with trigger pT histogram " << binFromTHnSparse.hTrPt << std::endl;
                    std::cout << std::endl;
                }

                // Skip bins if desired from config
                if (isInVector(binFromTHnSparse.hDPhi, vBinsToIgnore)) { 
                    std::cout << "do not draw bin " << binFromTHnSparse.hDPhi << " >>> skipping this bin" << std::endl;
                    skippedBins++;
                    continue;
                }
                
                vHists[i][j] = new TH1D(Form("hYieldsBaryonMesonRatio_%s_%i_%i_%i_%s", FLAVOUR, i, j, k-skippedBins, (canvasConfigs.canvasName).c_str()), Form("hYieldsBaryonMesonRatio_%s_%i_%i_%i_%s", FLAVOUR, i, j, k-skippedBins, (canvasConfigs.canvasName).c_str()), nDependencies, 0, nDependencies);
                const Double_t baryonMesonRatio =
                    safeRatio(
                        vYieldsAndErrors.vYields[i][j][k],
                        vYieldsAndErrors.vYields[i][referenceIndex][k]);
                const Double_t baryonMesonRatioError =
                    CALCULATE_ERRORS ? vYieldsAndErrors.vYieldsRatioErrors[i][j][k] : 0.0;
                SetPlotPointOrThrow(
                    vHists[i][j], 1+k-skippedBins, baryonMesonRatio,
                    baryonMesonRatioError, CALCULATE_ERRORS,
                    canvasConfigs.setLogy,
                    canvasConfigs.yMinAxis, canvasConfigs.yMaxAxis,
                    Form("%s baryon/meson ratio, tune=%s, associate=%s, bin=%s",
                         FLAVOUR, TUNE.c_str(), associateName.c_str(),
                         binFromTHnSparse.hDPhi.c_str()));
                ApplyTuneVisualStyle(vHists[i][j], TUNE, true);
                cYields->cd();
                vHists[i][j]->Draw("same PE");
                if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                    cMiniPad->cd();
                    vHists[i][j]->Draw("same PE");
                }

                hYieldsTemplate->GetXaxis()->SetBinLabel(1+k-skippedBins, (binFromTHnSparse.hDPhi).c_str());

                if (lineStyleBaryonMap.find(associateName) != lineStyleBaryonMap.end()) {
                    Int_t lineStyle = lineStyleBaryonMap[associateName];
                    vHists[i][j]->SetLineStyle(lineStyle);
                    if (VERBOSE) { std::cout << "Found lineStyle: " << lineStyle << std::endl; }
                } else {
                    if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                }

                // Draw legend
                // TODO: only do this once (but cannot put j==0)
                const std::string legendKey = associateName + "::" + TUNE;
                if (legend != nullptr && alreadyInLegend.find(legendKey) == alreadyInLegend.end()) {
                    if (legendEntriesMap.find(associateName) != legendEntriesMap.end()) {
                        std::string displayName = legendEntriesMap[associateName];
                        if (nTUNES > 1) { displayName += " (" + TUNE + ")"; }
                        if (VERBOSE) { std::cout << "Found displayName: " << displayName << std::endl; }
                        legend->AddEntry(vHists[i][j], displayName.c_str(), "lep");
                    } else {
                        if (VERBOSE) { std::cout << "objectName not found in the map!" << std::endl; }
                    }
                    alreadyInLegend.insert(legendKey);
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
                                                  std::vector<Int_t> vIndexNominatorTUNES, Int_t indexDenominatorTUNE) {


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
    std::vector<std::string> vBinsToIgnore = canvasConfigs.vBinsToIgnore;

    for (const auto& indexNominatorTUNE : vIndexNominatorTUNES) { std::cout << " and TUNE = " << vTUNES[indexNominatorTUNE] << "/" << vTUNES[indexDenominatorTUNE] << " ***" << std::endl; }
    // Int_t indexNominatorTUNE = vIndexNominatorTUNES[0];

    // Function that transforms the map storing trigger and vYieldsAndErrors into just vYieldsAndErrors
    auto vYieldsAndErrors = YieldsAndErrorsForGivenTrigger(canvasConfigs.TriggerToUse, mapYieldsAndErrors, CALCULATE_ERRORS);

    Int_t nAssociates = vTriggerAssociateOSandSS.size();
    const ReferenceAssociateSelection drawingReference =
        ResolveReferenceAssociateSelection(
            vTriggerAssociateOSandSS,
            std::string(FLAVOUR) +
                " baryon/meson tune-ratio canvas trigger '" +
                canvasConfigs.TriggerToUse + "'");
    if (drawingReference.index !=
            vYieldsAndErrors.referenceAssociateIndex ||
        drawingReference.pdg != vYieldsAndErrors.referenceMesonPdg) {
        throw std::runtime_error(
            "Baryon/meson tune-ratio reference differs from the reference "
            "used for block uncertainties");
    }
    const std::size_t referenceIndex = drawingReference.index;
    Int_t nDependencies;
    // We could have calculated more bins than we want to draw here, in that case, take the (non-empty) vector vBinsToIgnore
    // and subtract the template size
    if (vBinsToIgnore[0] != "NONE" && vBinsToIgnore[0] != "" && vBinsToIgnore[0] != "NULL") { nDependencies = vBinsFromTHnSparse.size() - vBinsToIgnore.size(); }
    else {nDependencies = vBinsFromTHnSparse.size(); }
    Int_t nTUNES = vIndexNominatorTUNES.size(); // nominator TUNES to be used in the TUNE ratios

    // We construct a map object that links the bin integer (integer k of vYields[i][j][k]) with the corresponding bin name
    // This way we can compute all yields in the beginning, but only draw the ones we are interested in
    // The bins that we want to draw are the ones we declare in the legend entries block of the json
    // usage example: dependencyMap[k] == "hDPhiM90_100"
    auto dependencyMap = CreateDependencyMap(vYieldsAndErrors, vBinsFromTHnSparse);

    // Values will be drawn from a 2D vector of TH1D with number of DEPENDENCIES bins
    // This way the TUNE and ASSOCIATE can be looped over, while the data points will be the DEPENDENCIES
    std::vector<std::vector<TH1D*>> vHists(
        nAssociates, std::vector<TH1D*>(nTUNES, nullptr));
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
    TPad* cMiniPad = nullptr;
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

    std::map<std::string, Int_t> lineStyleBaryonMap = canvasConfigs.lineStyleBaryonMap;

    TLegend *legend = nullptr;
    std::map<std::string, std::string> legendEntriesMap = canvasConfigs.legendEntriesMap;
    if (canvasConfigs.xMinLegend != -1 && canvasConfigs.xMaxLegend != -1 && canvasConfigs.yMinLegend != -1 && canvasConfigs.yMaxLegend != -1) {
        std::cout << "- Creating legend at positions x1(" << canvasConfigs.xMinLegend << "," << canvasConfigs.yMinLegend << ") and x2(" << canvasConfigs.xMaxLegend << "," << canvasConfigs.yMaxLegend << ")" << std::endl;
        legend = new TLegend(canvasConfigs.xMinLegend, canvasConfigs.yMinLegend, canvasConfigs.xMaxLegend, canvasConfigs.yMaxLegend);
        legend->SetBorderSize(0);
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
        if (VERBOSE) {
            // std::cout << "starting loop over associate: " << associateName << std::endl;
            // std::cout << "starting loop over OS file: " << fileNamesOSandSS.OS << " and SS file: " << fileNamesOSandSS.SS << std::endl;
            // std::cout << std::endl;
        }
        Int_t skippedBins = 0; // for the k-loop over skipped dependencies

        // Loop over DEPENDENCIES
        for (Int_t k=0; k<nDependencies+skippedBins; k++) {


            // HistogramAndTriggerPtHistogramNames hDPhiAndhTrPtNames = vHistogramAndTriggerPtHistogramNames[k];
            BinsFromTHnSparse binFromTHnSparse = vBinsFromTHnSparse[k];
            // TODO: verbose
            // std::cout << "plotting histogram " << hDPhiAndhTrPtNames.hDPhi << " with trigger pT histogram " << hDPhiAndhTrPtNames.hTrPt << std::endl;

            // Skip bins if desired from config
            if (isInVector(binFromTHnSparse.hDPhi, vBinsToIgnore)) { 
                std::cout << "do not draw bin " << binFromTHnSparse.hDPhi << " >>> skipping this bin" << std::endl;
                skippedBins++;
                continue;
            }


            for (Int_t iTUNE=0; iTUNE < nTUNES; iTUNE++) {


                Int_t indexNominatorTUNE = vIndexNominatorTUNES[iTUNE];
                if (VERBOSE) { std::cout << "starting loop over nominator TUNE: " << indexNominatorTUNE << std::endl; }
                
                vHists[j][iTUNE] = new TH1D(Form("hYieldsBaryonMesonRatio_%s_%i_%i_%i_%s", FLAVOUR, j, k-skippedBins, iTUNE, (canvasConfigs.canvasName).c_str()), Form("hYieldsBaryonMesonRatio_%s_%i_%i_%i_%s", FLAVOUR, j, k-skippedBins, iTUNE, (canvasConfigs.canvasName).c_str()), nDependencies, 0, nDependencies);
                const Double_t numeratorBaryonMesonRatio = safeRatio(
                    vYieldsAndErrors.vYields[indexNominatorTUNE][j][k],
                    vYieldsAndErrors.vYields[indexNominatorTUNE]
                                             [referenceIndex][k]);
                const Double_t denominatorBaryonMesonRatio = safeRatio(
                    vYieldsAndErrors.vYields[indexDenominatorTUNE][j][k],
                    vYieldsAndErrors.vYields[indexDenominatorTUNE]
                                             [referenceIndex][k]);
                const Double_t tuneDoubleRatio = safeRatio(numeratorBaryonMesonRatio, denominatorBaryonMesonRatio);
                const Double_t tuneDoubleRatioError = CALCULATE_ERRORS
                    ? propagateRatioError(
                        numeratorBaryonMesonRatio, denominatorBaryonMesonRatio,
                        vYieldsAndErrors.vYieldsRatioErrors[indexNominatorTUNE][j][k],
                        vYieldsAndErrors.vYieldsRatioErrors[indexDenominatorTUNE][j][k])
                    : 0.0;
                SetPlotPointOrThrow(
                    vHists[j][iTUNE], 1+k-skippedBins, tuneDoubleRatio,
                    tuneDoubleRatioError, CALCULATE_ERRORS,
                    canvasConfigs.setLogy,
                    canvasConfigs.yMinAxis, canvasConfigs.yMaxAxis,
                    Form("%s baryon/meson tune double ratio %s/%s, associate=%s, bin=%s",
                         FLAVOUR, vTUNES[indexNominatorTUNE].c_str(),
                         vTUNES[indexDenominatorTUNE].c_str(), associateName.c_str(),
                         binFromTHnSparse.hDPhi.c_str()));
    
                cYields->cd();

                ApplyTuneVisualStyle(vHists[j][iTUNE], vTUNES[indexNominatorTUNE], true);

                vHists[j][iTUNE]->Draw("same PE");
                if (canvasConfigs.xMinPad != -1 && canvasConfigs.xMaxPad != -1 && canvasConfigs.yMinPad != -1 && canvasConfigs.yMaxPad != -1) {
                    cMiniPad->cd();
                    vHists[j][iTUNE]->Draw("same PE");
                }

                hYieldsTemplate->GetXaxis()->SetBinLabel(1+k-skippedBins, DisplayLabelForMultiplicityBin(binFromTHnSparse, legendEntriesMap).c_str());
                // hYieldsTemplate->GetXaxis()->SetBinLabel(1+k-skippedBins, (binFromTHnSparse.hDPhi).c_str());

                if (lineStyleBaryonMap.find(associateName) != lineStyleBaryonMap.end()) {
                        Int_t lineStyle = lineStyleBaryonMap[associateName];
                        vHists[j][iTUNE]->SetLineStyle(lineStyle);
                        // TODO: verbose
                        // std::cout << "Found lineStyle: " << lineStyle << std::endl;
                    } else {
                        // TODO: verbose
                        // std::cout << "objectName not found in the map!" << std::endl;
                    }

                // TODO: verbose
                // std::cout << std::endl;


            } // Loop over NOMINATOR TUNES


        } // Loop over DEPENDENCIES


        // Draw one line-and-marker legend entry for every numerator tune.
        for (Int_t iTUNE = 0; iTUNE < nTUNES; ++iTUNE) {
            const std::string numeratorTune = vTUNES[vIndexNominatorTUNES[iTUNE]];
            const std::string denominatorTune = vTUNES[indexDenominatorTUNE];
            const std::string legendKey =
                associateName + "::" + numeratorTune + "/" + denominatorTune;
            if (legend != nullptr && alreadyInLegend.find(legendKey) == alreadyInLegend.end()) {
                if (legendEntriesMap.find(associateName) != legendEntriesMap.end()) {
                    std::string displayName = legendEntriesMap[associateName] +
                        " (" + numeratorTune + "/" + denominatorTune + ")";
                    legend->AddEntry(vHists[j][iTUNE], displayName.c_str(), "lep");
                }
                alreadyInLegend.insert(legendKey);
            }
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


int freezeMultiplicityBoundaries_THnSparse(const char* configuration) {
    try {
        CONFIGS configs_from_json = readConfig(configuration);
        WriteMultiplicityBoundaryReceipt(configs_from_json);
        std::cout
            << "MULTIPLICITY_BOUNDARY_FREEZE status=PASS configuration="
            << configuration << std::endl;
        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "MULTIPLICITY_BOUNDARY_FREEZE status=FAIL error="
            << error.what() << std::endl;
        return 1;
    }
}


// Run macro with 
// >> root 'improvedPlotting_THnSparse.C("configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json")'
int improvedPlotting_THnSparse(const char* configuration) {

    // Read configurations defined by user in configuration.json
    CONFIGS configs_from_json = readConfig(configuration);
    bool VERBOSE = configs_from_json.VERBOSE;

    // Prepare the Delta Phi plots
    // TODO: this is still hardcoded
    // TODO: also this can be repeated in the loops
    TCanvas *cCharm = nullptr;
    TCanvas *cBeauty = nullptr;
    if (configs_from_json.DRAW_CORRELATION_PLOTS) {
        cCharm = new TCanvas("cCharmCorrelations","Charm correlations",1000,800);
        cBeauty = new TCanvas("cBeautyCorrelations","Beauty correlations",1000,800);
    }

    // Calculate the 3D yield vector
    // TODO: define this below in loop
    YieldsAndErrorsMap mapYields; // used in loop over canvas settings
    YieldsAndErrorsMap mapYieldsBeauty;
    YieldsAndErrorsMap mapYieldsCharm;
    mapYieldsBeauty = calculateYieldsVector(configs_from_json, "BEAUTY", cBeauty);
    mapYieldsCharm =  calculateYieldsVector(configs_from_json, "CHARM", cCharm);
    if (configs_from_json.SUBSAMPLE_COVERAGE_AUDIT) {
        const Int_t totalCoverageFailures =
            mapYieldsBeauty.subsampleCoverageFailures +
            mapYieldsCharm.subsampleCoverageFailures;
        std::cout << "SUBSAMPLE_COVERAGE_AUDIT_SUMMARY"
                  << " beauty_failures="
                  << mapYieldsBeauty.subsampleCoverageFailures
                  << " charm_failures="
                  << mapYieldsCharm.subsampleCoverageFailures
                  << " total_failures=" << totalCoverageFailures
                  << std::endl;
        if (totalCoverageFailures > 0) {
            return 2;
        }
        std::cout << "Subsample coverage audit passed; no canvases were drawn."
                  << std::endl;
        return 0;
    }

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
        std::vector<Int_t> vIndexNominatorTUNES = canvasConfigs.vIndexNominatorTUNES;
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
            TPad *cMiniPad = drawBalancingPlotsTUNERatios(configs_from_json,FLAVOUR.c_str(), mapYields, vIndexNominatorTUNES, indexDenominatorTUNE);
            cMiniCanvasMap[canvasName] = cMiniPad; 
        }
        if (strcmp(drawFunctionToUse.c_str(), "drawBalancingBaryonMesonRatioPlots") == 0) { 
            TPad *cMiniPad = drawBalancingBaryonMesonRatioPlots(configs_from_json,FLAVOUR.c_str(), mapYields);
            cMiniCanvasMap[canvasName] = cMiniPad; 
        }
        if (strcmp(drawFunctionToUse.c_str(), "drawBalancingBaryonMesonRatioPlotsTUNERatios") == 0) { 
            TPad *cMiniPad = drawBalancingBaryonMesonRatioPlotsTUNERatios(configs_from_json,FLAVOUR.c_str(), mapYields, vIndexNominatorTUNES, indexDenominatorTUNE); 
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
            const auto miniCanvasIt = cMiniCanvasMap.find(cMiniCanvas);
            if (miniCanvasIt == cMiniCanvasMap.end() || miniCanvasIt->second == nullptr) {
                std::cerr << "- ERROR: required mini canvas " << cMiniCanvas
                          << " is absent or was not requested as a mini pad"
                          << std::endl;
                delete globalCanvas;
                return 18;
            }
            globalCanvas->cd();
            miniCanvasIt->second->Draw();
        } // Loop over mini canvas names
        if (globalCanvasConfig.write) { 
            writeCanvasToFiles(VERBOSE, globalCanvas, globalCanvasConfig.writePath, globalCanvasConfig.writeName); 
        }
    } // Loop over global canvas settings
    std::cout << "Global canvases drawn without problems (...?)" << std::endl;
    // Publish the frozen machine-readable boundary definition only after the
    // complete requested plotting workflow has succeeded.
    WriteMultiplicityBoundaryReceipt(configs_from_json);

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
