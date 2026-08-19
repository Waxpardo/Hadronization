// MergeAnalysisObjects.C
//
// Object-level merger for the status-analysis ROOT outputs. This is a safer
// fallback when hadd becomes pathological on accumulated THnSparse objects.

#include <fstream>
#include <algorithm>
#include <cctype>
#include <iostream>
#include <memory>
#include <set>
#include <string>
#include <vector>

#include "TFile.h"
#include "TAxis.h"
#include "TArrayD.h"
#include "TH1.h"
#include "THnSparse.h"
#include "TKey.h"
#include "TList.h"
#include "TObject.h"
#include "TObjString.h"
#include "TParameter.h"
#include "TSystem.h"

namespace {

std::string Trim(const std::string& input)
{
    const char* whitespace = " \t\r\n";
    const std::size_t begin = input.find_first_not_of(whitespace);
    if (begin == std::string::npos) return "";
    const std::size_t end = input.find_last_not_of(whitespace);
    return input.substr(begin, end - begin + 1);
}

std::vector<std::string> ReadInputList(const char* inputListPath)
{
    std::ifstream input(inputListPath);
    std::vector<std::string> paths;
    std::string line;

    while (std::getline(input, line)) {
        line = Trim(line);
        if (line.empty() || line[0] == '#') continue;
        paths.push_back(line);
    }

    return paths;
}

bool IsLowerHex(const std::string& value, std::size_t length)
{
    return value.size() == length &&
           std::all_of(value.begin(), value.end(), [](unsigned char character) {
               return std::isdigit(character) ||
                      (character >= 'a' && character <= 'f');
           });
}

bool AxesEqual(const TAxis* first, const TAxis* second)
{
    if (!first || !second ||
        first->GetNbins() != second->GetNbins() ||
        first->GetXmin() != second->GetXmin() ||
        first->GetXmax() != second->GetXmax()) {
        return false;
    }
    const TArrayD* firstBins = first->GetXbins();
    const TArrayD* secondBins = second->GetXbins();
    if (!firstBins || !secondBins ||
        firstBins->GetSize() != secondBins->GetSize()) {
        return false;
    }
    for (int index = 0; index < firstBins->GetSize(); ++index) {
        if (firstBins->At(index) != secondBins->At(index)) return false;
    }
    return true;
}

bool HistogramsCompatible(const TH1* first, const TH1* second)
{
    if (!first || !second ||
        first->GetDimension() != second->GetDimension() ||
        first->GetSumw2N() != second->GetSumw2N() ||
        !AxesEqual(first->GetXaxis(), second->GetXaxis())) {
        return false;
    }
    if (first->GetDimension() >= 2 &&
        !AxesEqual(first->GetYaxis(), second->GetYaxis())) {
        return false;
    }
    return first->GetDimension() < 3 ||
           AxesEqual(first->GetZaxis(), second->GetZaxis());
}

bool SparseHistogramsCompatible(const THnSparse* first,
                                const THnSparse* second)
{
    if (!first || !second ||
        first->GetNdimensions() != second->GetNdimensions() ||
        first->GetCalculateErrors() != second->GetCalculateErrors()) {
        return false;
    }
    for (int axis = 0; axis < first->GetNdimensions(); ++axis) {
        if (!AxesEqual(first->GetAxis(axis), second->GetAxis(axis))) {
            return false;
        }
    }
    return true;
}

bool AddObject(TObject* target,
               TObject* source,
               const std::string& objectName,
               const std::string& sourcePath)
{
    if (auto* targetHist = dynamic_cast<TH1*>(target)) {
        auto* sourceHist = dynamic_cast<TH1*>(source);
        if (!sourceHist) {
            std::cerr << "ERROR: object '" << objectName << "' in " << sourcePath
                      << " is not a TH1-compatible object" << std::endl;
            return false;
        }
        if (!HistogramsCompatible(targetHist, sourceHist) ||
            !targetHist->Add(sourceHist)) {
            std::cerr << "ERROR: incompatible TH1 axis/error schema for '"
                      << objectName << "' in " << sourcePath << std::endl;
            return false;
        }
        return true;
    }

    if (auto* targetSparse = dynamic_cast<THnSparse*>(target)) {
        auto* sourceSparse = dynamic_cast<THnSparse*>(source);
        if (!sourceSparse) {
            std::cerr << "ERROR: object '" << objectName << "' in " << sourcePath
                      << " is not a THnSparse-compatible object" << std::endl;
            return false;
        }
        if (!SparseHistogramsCompatible(targetSparse, sourceSparse)) {
            std::cerr << "ERROR: incompatible THnSparse axis/error schema for '"
                      << objectName << "' in " << sourcePath << std::endl;
            return false;
        }
        // THnSparse::Add returns void in supported ROOT releases, so the
        // complete axis/error-schema comparison above is the fail-closed
        // compatibility check performed before mutating the target.
        targetSparse->Add(sourceSparse);
        return true;
    }

    if (auto* targetString = dynamic_cast<TObjString*>(target)) {
        auto* sourceString = dynamic_cast<TObjString*>(source);
        if (!sourceString ||
            targetString->GetString() != sourceString->GetString()) {
            std::cerr << "ERROR: invariant string object '" << objectName
                      << "' differs in " << sourcePath << std::endl;
            return false;
        }
        return true;
    }

    const bool additive =
        objectName == "input_events" ||
        objectName == "source_input_events" ||
        objectName == "input_file_count" ||
        objectName == "input_sum_weights" ||
        objectName == "primary_all_heavy_closure_failures" ||
        objectName == "direct_primary_heavy_count" ||
        objectName == "central_ground_state_count" ||
        objectName == "central_hard_trigger_count" ||
        objectName == "trigger_count" ||
        objectName == "trigger_sum_weights" ||
        objectName == "pair_count" ||
        objectName == "pair_sum_weights";
    if (auto* targetLong = dynamic_cast<TParameter<Long64_t>*>(target)) {
        auto* sourceLong = dynamic_cast<TParameter<Long64_t>*>(source);
        if (!sourceLong) return false;
        if (additive) {
            targetLong->SetVal(targetLong->GetVal() + sourceLong->GetVal());
        } else if (targetLong->GetVal() != sourceLong->GetVal()) {
            std::cerr << "ERROR: invariant integer parameter '" << objectName
                      << "' differs in " << sourcePath << std::endl;
            return false;
        }
        return true;
    }
    if (auto* targetInt = dynamic_cast<TParameter<int>*>(target)) {
        auto* sourceInt = dynamic_cast<TParameter<int>*>(source);
        if (!sourceInt) return false;
        if (additive) {
            targetInt->SetVal(targetInt->GetVal() + sourceInt->GetVal());
        } else if (targetInt->GetVal() != sourceInt->GetVal()) {
            std::cerr << "ERROR: invariant integer parameter '" << objectName
                      << "' differs in " << sourcePath << std::endl;
            return false;
        }
        return true;
    }
    if (auto* targetDouble = dynamic_cast<TParameter<double>*>(target)) {
        auto* sourceDouble = dynamic_cast<TParameter<double>*>(source);
        if (!sourceDouble) return false;
        if (additive) {
            targetDouble->SetVal(targetDouble->GetVal() +
                                 sourceDouble->GetVal());
        } else if (targetDouble->GetVal() != sourceDouble->GetVal()) {
            std::cerr << "ERROR: invariant floating parameter '" << objectName
                      << "' differs in " << sourcePath << std::endl;
            return false;
        }
        return true;
    }

    // Booleans are invariant, never additive. centralEligible is the only one
    // today: status_analysis_THnSparse_qq.C:1155 writes it from
    // pair.definition->centralEligible, a property of the generated pair
    // registry rather than of the events, so every input file for a given pair
    // carries the same value by construction. A disagreement means the inputs
    // were produced against different registries, which is exactly what a
    // merge must refuse rather than silently resolve -- summing the flags or
    // taking the first would let a review-blocked species into a central
    // result. Deliberately not added to the `additive` list above: there is no
    // meaningful sum of two eligibility flags.
    if (auto* targetBool = dynamic_cast<TParameter<bool>*>(target)) {
        auto* sourceBool = dynamic_cast<TParameter<bool>*>(source);
        if (!sourceBool) return false;
        if (targetBool->GetVal() != sourceBool->GetVal()) {
            std::cerr << "ERROR: invariant boolean parameter '" << objectName
                      << "' differs in " << sourcePath << std::endl;
            return false;
        }
        return true;
    }

    std::cerr << "ERROR: unsupported object type for '" << objectName
              << "': " << target->ClassName() << std::endl;
    return false;
}

} // namespace

int MergeAnalysisObjects(const char* inputListPath,
                         const char* outputPath,
                         bool verbose = true,
                         const char* manifestSha256 = "")
{
    TH1::AddDirectory(kFALSE);

    const std::vector<std::string> inputPaths = ReadInputList(inputListPath);
    if (inputPaths.empty()) {
        std::cerr << "ERROR: input list is empty: " << inputListPath << std::endl;
        return 1;
    }
    if (std::set<std::string>(inputPaths.begin(), inputPaths.end()).size() !=
        inputPaths.size()) {
        std::cerr << "ERROR: duplicate path in input list: "
                  << inputListPath << std::endl;
        return 1;
    }
    if (!IsLowerHex(manifestSha256, 64)) {
        std::cerr << "ERROR: invalid source-manifest SHA-256" << std::endl;
        return 1;
    }

    std::unique_ptr<TFile> firstFile(TFile::Open(inputPaths.front().c_str(), "READ"));
    if (!firstFile || firstFile->IsZombie()) {
        std::cerr << "ERROR: could not open first input file: "
                  << inputPaths.front() << std::endl;
        return 2;
    }

    std::vector<std::string> objectNames;
    std::vector<std::unique_ptr<TObject>> mergedObjects;
    std::set<std::string> sourceObjectNames;

    TIter nextKey(firstFile->GetListOfKeys());
    TKey* key = nullptr;
    while ((key = dynamic_cast<TKey*>(nextKey()))) {
        std::unique_ptr<TObject> object(key->ReadObj());
        if (!object) {
            std::cerr << "ERROR: could not read object from first input: "
                      << key->GetName() << std::endl;
            return 3;
        }

        const std::string keyName = key->GetName();
        if (!sourceObjectNames.insert(keyName).second) {
            std::cerr << "ERROR: duplicate ROOT key in first input: "
                      << keyName << std::endl;
            return 3;
        }
        // This SHA identifies one raw file and therefore cannot be represented
        // by a single value after merging.  The exact source-manifest SHA
        // written below replaces it for merged products.
        if (keyName == "upstream_raw_sha256" ||
            keyName == "upstream_effective_settings_sha256") {
            continue;
        }
        TObject* clone = object->Clone(keyName.c_str());
        if (!clone) {
            std::cerr << "ERROR: could not clone object: "
                      << object->GetName() << std::endl;
            return 4;
        }

        if (auto* hist = dynamic_cast<TH1*>(clone)) {
            hist->SetDirectory(nullptr);
        }

        objectNames.emplace_back(keyName);
        mergedObjects.emplace_back(clone);
    }

    if (mergedObjects.empty()) {
        std::cerr << "ERROR: no mergeable objects found in first input: "
                  << inputPaths.front() << std::endl;
        return 5;
    }

    for (std::size_t i = 1; i < inputPaths.size(); ++i) {
        std::unique_ptr<TFile> inputFile(TFile::Open(inputPaths[i].c_str(), "READ"));
        if (!inputFile || inputFile->IsZombie()) {
            std::cerr << "ERROR: could not open input file: "
                      << inputPaths[i] << std::endl;
            return 6;
        }
        std::set<std::string> currentObjectNames;
        TIter currentKey(inputFile->GetListOfKeys());
        while (auto* objectKey = dynamic_cast<TKey*>(currentKey())) {
            currentObjectNames.insert(objectKey->GetName());
        }
        if (currentObjectNames != sourceObjectNames) {
            std::cerr << "ERROR: ROOT object-key set differs in "
                      << inputPaths[i] << std::endl;
            return 7;
        }

        for (std::size_t j = 0; j < objectNames.size(); ++j) {
            // Owned here. TFile::Get hands ownership to the caller for
            // anything not adopted by TH1::AddDirectory, and :249 sets
            // AddDirectory(kFALSE), so in this file EVERY fetched object is
            // caller-owned, TH1 included. This loop runs
            // (inputs - 1) x ~62 objects for each of the 300 pair files, so
            // the leak scaled with inputs per merge: ~10x worse at 100 inputs
            // per block and fatal at 1000, under a 2.00 GiB cgroup cap.
            const std::unique_ptr<TObject> source(
                inputFile->Get(objectNames[j].c_str()));
            if (!source) {
                std::cerr << "ERROR: missing object '" << objectNames[j]
                          << "' in " << inputPaths[i] << std::endl;
                return 7;
            }

            if (!AddObject(mergedObjects[j].get(), source.get(),
                           objectNames[j], inputPaths[i])) {
                return 8;
            }
        }

        if (verbose && (((i + 1) % 10 == 0) || (i + 1 == inputPaths.size()))) {
            std::cout << "Merged " << (i + 1) << "/" << inputPaths.size()
                      << " files into " << outputPath << std::endl;
        }
    }

    const std::string outputDir = gSystem->DirName(outputPath);
    if (!outputDir.empty() && gSystem->AccessPathName(outputDir.c_str())) {
        if (gSystem->mkdir(outputDir.c_str(), true) != 0) {
            std::cerr << "ERROR: could not create output directory: "
                      << outputDir << std::endl;
            return 9;
        }
    }

    std::unique_ptr<TFile> outputFile(TFile::Open(outputPath, "RECREATE"));
    if (!outputFile || outputFile->IsZombie()) {
        std::cerr << "ERROR: could not create output file: "
                  << outputPath << std::endl;
        return 10;
    }

    outputFile->cd();
    for (std::size_t index = 0; index < mergedObjects.size(); ++index) {
        mergedObjects[index]->Write(objectNames[index].c_str(),
                                    TObject::kOverwrite);
    }
    TParameter<Long64_t>("merge_input_file_count",
                         static_cast<Long64_t>(inputPaths.size())).Write();
    TObjString(manifestSha256).Write("merge_input_manifest_sha256");
    outputFile->Close();

    if (verbose) {
        std::cout << "Wrote merged file: " << outputPath << std::endl;
    }

    return 0;
}

int TestMergeAnalysisAxisCompatibility()
{
    TH1D first("merge_axis_first", "", 2, 0.0, 2.0);
    TH1D same("merge_axis_same", "", 2, 0.0, 2.0);
    TH1D shifted("merge_axis_shifted", "", 2, 0.5, 2.5);
    first.Sumw2();
    same.Sumw2();
    shifted.Sumw2();
    if (!AddObject(&first, &same, "hCompatible", "synthetic-compatible")) {
        return 1;
    }
    if (AddObject(&first, &shifted, "hShifted", "synthetic-shifted")) {
        return 2;
    }

    const int bins[2] = {2, 3};
    const double minimum[2] = {0.0, -1.0};
    const double maximum[2] = {2.0, 2.0};
    const double shiftedMaximum[2] = {2.0, 3.0};
    THnSparseD sparseFirst(
        "merge_sparse_first", "", 2, bins, minimum, maximum);
    THnSparseD sparseSame(
        "merge_sparse_same", "", 2, bins, minimum, maximum);
    THnSparseD sparseShifted(
        "merge_sparse_shifted", "", 2, bins, minimum, shiftedMaximum);
    sparseFirst.Sumw2();
    sparseSame.Sumw2();
    sparseShifted.Sumw2();
    if (!AddObject(
            &sparseFirst, &sparseSame, "hSparseCompatible",
            "synthetic-compatible")) {
        return 3;
    }
    if (AddObject(
            &sparseFirst, &sparseShifted, "hSparseShifted",
            "synthetic-shifted")) {
        return 4;
    }
    std::cout << "MERGE_AXIS_COMPATIBILITY_PASS" << std::endl;
    return 0;
}
