#include <algorithm>
#include <climits>
#include <cmath>
#include <ctime>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <map>
#include <regex>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "TClass.h"
#include "TFile.h"
#include "TKey.h"
#include "TH1D.h"
#include "THnSparse.h"
#include "TROOT.h"
#include "TSystem.h"

#if __has_include(<nlohmann/json.hpp>)
#include <nlohmann/json.hpp>
#elif __has_include("nlohmann/json.hpp")
#include "nlohmann/json.hpp"
#else
#error "Could not find nlohmann/json.hpp. Source setupEnv.sh before compiling this macro."
#endif

using json = nlohmann::json;

namespace {

const std::vector<std::string> kTunes = {"MONASH", "JUNCTIONS", "CLOSEPACKING"};
const std::vector<std::string> kObjectNames = {
    "summed MULTIPLICITY", "hTrKinematics", "hAsKinematics", "hCorrelations"
};
const std::set<std::string> kIntegralPairs = {
    "BplusBminus.root", "BplusBplus.root", "LbbarBminus.root",
    "DplusDminus.root", "DplusDplus.root", "LambdacplusDminus.root"
};

std::string Join(const std::vector<std::string>& parts)
{
    std::string result;
    for (const auto& part : parts) {
        if (part.empty()) continue;
        if (!result.empty() && result.back() != '/') result += '/';
        std::string clean = part;
        while (!result.empty() && !clean.empty() && clean.front() == '/') clean.erase(clean.begin());
        result += clean;
    }
    return result;
}

bool Exists(const std::string& path)
{
    return !gSystem->AccessPathName(path.c_str());
}

std::string RealPath(const std::string& path)
{
    char resolved[PATH_MAX];
    return ::realpath(path.c_str(), resolved) ? std::string(resolved) : path;
}

std::string UtcTimestamp()
{
    const std::time_t now = std::time(nullptr);
    std::tm utc{};
    gmtime_r(&now, &utc);
    char buffer[32];
    std::strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &utc);
    return buffer;
}

std::string ProjectBase()
{
    const char* configured = std::getenv("HADRONIZATION_BASE");
    if (configured && Exists(Join({configured, "PlottingScripts"}))) return configured;
    return gSystem->WorkingDirectory();
}

std::string AbsoluteFromBase(const std::string& path)
{
    if (!path.empty() && path.front() == '/') return path;
    return Join({ProjectBase(), path});
}

std::vector<std::string> RootFiles(const std::string& directory)
{
    void* handle = gSystem->OpenDirectory(directory.c_str());
    if (!handle) throw std::runtime_error("Cannot open directory: " + directory);
    std::vector<std::string> names;
    const char* entry = nullptr;
    while ((entry = gSystem->GetDirEntry(handle))) {
        const std::string name(entry);
        if (name.size() > 5 && name.substr(name.size() - 5) == ".root") names.push_back(name);
    }
    gSystem->FreeDirectory(handle);
    std::sort(names.begin(), names.end());
    return names;
}

std::set<std::string> ConfiguredPairs(const json& config)
{
    std::set<std::string> result;
    for (const auto* section : {"beauty_correlations_to_analyse", "charm_correlations_to_analyse"}) {
        for (const auto& trigger : config.at(section)) {
            for (const auto& pair : trigger.at("configs")) {
                result.insert(pair.at("OS").get<std::string>());
                result.insert(pair.at("SS").get<std::string>());
            }
        }
    }
    return result;
}

std::string ExpectedType(const std::string& objectName)
{
    return objectName == "summed MULTIPLICITY" ? "TH1D" : "THnSparseD";
}

double Entries(TObject* object)
{
    if (auto* histogram = dynamic_cast<TH1*>(object)) return histogram->GetEntries();
    if (auto* sparse = dynamic_cast<THnSparseD*>(object)) return sparse->GetEntries();
    return std::numeric_limits<double>::quiet_NaN();
}

double Integral(TObject* object)
{
    if (auto* histogram = dynamic_cast<TH1*>(object)) {
        return histogram->Integral(0, histogram->GetNbinsX() + 1);
    }
    if (auto* sparse = dynamic_cast<THnSparseD*>(object)) {
        TH1D* projection = sparse->Projection(0, "E");
        const double value = projection->Integral(0, projection->GetNbinsX() + 1);
        delete projection;
        return value;
    }
    return std::numeric_limits<double>::quiet_NaN();
}

std::string Schema(TObject* object)
{
    std::ostringstream out;
    if (auto* histogram = dynamic_cast<TH1*>(object)) {
        out << histogram->ClassName() << ':' << histogram->GetNbinsX() << ':'
            << histogram->GetXaxis()->GetXmin() << ':' << histogram->GetXaxis()->GetXmax();
        return out.str();
    }
    if (auto* sparse = dynamic_cast<THnSparseD*>(object)) {
        out << "THnSparseD:" << sparse->GetNdimensions();
        for (int dimension = 0; dimension < sparse->GetNdimensions(); ++dimension) {
            const TAxis* axis = sparse->GetAxis(dimension);
            out << ':' << axis->GetNbins() << ':' << axis->GetXmin() << ':' << axis->GetXmax();
        }
        return out.str();
    }
    return "INVALID";
}

TObject* CheckedObject(TFile& file, const std::string& objectName, const std::string& path)
{
    TObject* object = file.Get(objectName.c_str());
    const bool correct = objectName == "summed MULTIPLICITY"
        ? dynamic_cast<TH1D*>(object) != nullptr
        : dynamic_cast<THnSparseD*>(object) != nullptr;
    if (!correct) {
        throw std::runtime_error(
            "Missing or wrong type for '" + objectName + "' in " + path +
            "; expected " + ExpectedType(objectName));
    }
    return object;
}

void CheckKeyType(TFile& file, const std::string& objectName, const std::string& path)
{
    TKey* key = file.GetKey(objectName.c_str());
    if (!key) throw std::runtime_error("Missing object '" + objectName + "' in " + path);
    const std::string className = key->GetClassName();
    const bool correct = objectName == "summed MULTIPLICITY"
        ? className == "TH1D"
        : className == "THnSparseT<TArrayD>" || className == "THnSparseD";
    if (!correct) {
        throw std::runtime_error(
            "Wrong type for '" + objectName + "' in " + path + ": " + className +
            "; expected " + ExpectedType(objectName));
    }
}

json FileFingerprint(const std::string& path)
{
    Long_t id = 0;
    Long64_t size = 0;
    Long_t flags = 0;
    Long_t modification = 0;
    if (gSystem->GetPathInfo(path.c_str(), &id, &size, &flags, &modification) != 0) {
        throw std::runtime_error("Cannot stat file: " + path);
    }
    return {
        {"path", path},
        {"resolved_path", RealPath(path)},
        {"size_bytes", size},
        {"mtime_epoch", modification}
    };
}

bool CloseEnough(double central, double subsampleSum)
{
    if (!std::isfinite(central) || !std::isfinite(subsampleSum)) return false;
    const double scale = std::max({1.0, std::abs(central), std::abs(subsampleSum)});
    return std::abs(central - subsampleSum) <= 1e-9 * scale;
}

} // namespace

int Validate_THnSparse_Production(
    const char* configuration =
        "PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json",
    const char* reportPath =
        "PlottingScripts/validation/final_thnsparse_input_validation.json")
{
    std::ifstream configInput(AbsoluteFromBase(configuration));
    if (!configInput) throw std::runtime_error(std::string("Cannot open config: ") + configuration);
    json config;
    configInput >> config;

    const int nSubsamples = config.at("nSubSamples").get<int>();
    if (nSubsamples != 10) throw std::runtime_error("Final production must use exactly ten subsamples");

    const std::string analyzedBase = AbsoluteFromBase(config.at("base_dir").get<std::string>());
    const std::string completeTag = config.at("bb_bar_complete_root_dir").get<std::string>();
    if (completeTag != config.at("cc_bar_complete_root_dir").get<std::string>()) {
        throw std::runtime_error("Beauty and charm complete-root tags differ");
    }
    const std::string subsampleBase =
        AbsoluteFromBase(config.at("bb_bar_complete_root_dir_sub_samples").get<std::string>());
    if (subsampleBase !=
        AbsoluteFromBase(config.at("cc_bar_complete_root_dir_sub_samples").get<std::string>())) {
        throw std::runtime_error("Beauty and charm subsample bases differ");
    }

    const std::set<std::string> configuredPairs = ConfiguredPairs(config);
    std::set<std::string> comparisonPairs;
    std::set_intersection(
        configuredPairs.begin(), configuredPairs.end(),
        kIntegralPairs.begin(), kIntegralPairs.end(),
        std::inserter(comparisonPairs, comparisonPairs.begin()));
    json report = {
        {"status", "running"},
        {"configuration", AbsoluteFromBase(configuration)},
        {"configuration_resolved", RealPath(AbsoluteFromBase(configuration))},
        {"validated_at_utc", UtcTimestamp()},
        {"validation_host", gSystem->HostName()},
        {"root_version", gROOT->GetVersion()},
        {"checkout", ProjectBase()},
        {"checkout_resolved", RealPath(ProjectBase())},
        {"central_definition", Join({analyzedBase, completeTag + "_<TUNE>"})},
        {"subsample_definition", subsampleBase + "_<TUNE>/combined_root_<1..10>"},
        {"n_subsamples", nSubsamples},
        {"configured_pair_files", configuredPairs},
        {"representative_union_comparison_files", comparisonPairs},
        {"required_objects", kObjectNames},
        {"tunes", json::object()},
        {"comparisons", json::array()}
    };

    std::map<std::string, std::vector<std::string>> centralNames;
    std::map<std::string, std::map<std::string, std::string>> tuneSchemas;

    for (const auto& tune : kTunes) {
        std::cout << "Validating tune " << tune << "..." << std::endl;
        const std::string centralDir = Join({analyzedBase, completeTag + "_" + tune});
        const std::string tuneSubsampleBase = subsampleBase + "_" + tune;
        centralNames[tune] = RootFiles(centralDir);
        if (centralNames[tune].size() != 56) {
            throw std::runtime_error("Expected 56 central ROOT files in " + centralDir);
        }

        json tuneReport = {
            {"central_directory", centralDir},
            {"central_directory_resolved", RealPath(centralDir)},
            {"central_root_file_count", centralNames[tune].size()},
            {"subsample_base", tuneSubsampleBase},
            {"subsample_base_resolved", RealPath(tuneSubsampleBase)},
            {"subsamples", json::array()},
            {"central_fingerprints", json::array()}
        };

        std::set<int> aggregateJobIds;
        std::set<std::string> aggregateManifestLines;
        for (int sample = 1; sample <= nSubsamples; ++sample) {
            const std::string sampleDir =
                Join({tuneSubsampleBase, "combined_root_" + std::to_string(sample)});
            const auto names = RootFiles(sampleDir);
            if (names != centralNames[tune]) {
                throw std::runtime_error("Subsample ROOT file set differs from central: " + sampleDir);
            }

            const std::string manifestPath = Join({sampleDir, "jobs_used.txt"});
            std::ifstream manifest(manifestPath);
            if (!manifest) throw std::runtime_error("Missing manifest: " + manifestPath);
            std::set<int> sampleIds;
            std::vector<std::string> manifestLines;
            const std::regex jobPattern("_job([0-9]+)$");
            std::string line;
            while (std::getline(manifest, line)) {
                if (line.empty()) continue;
                std::smatch match;
                if (!std::regex_search(line, match, jobPattern)) {
                    throw std::runtime_error("Unrecognised manifest entry: " + line);
                }
                const int jobId = std::stoi(match[1].str());
                if (!sampleIds.insert(jobId).second ||
                    !aggregateJobIds.insert(jobId).second ||
                    !aggregateManifestLines.insert(line).second) {
                    throw std::runtime_error("Duplicate job assignment in " + manifestPath);
                }
                manifestLines.push_back(line);
            }
            if (sampleIds.size() != 10) {
                throw std::runtime_error("Expected ten jobs in " + manifestPath);
            }
            tuneReport["subsamples"].push_back({
                {"index", sample},
                {"directory", sampleDir},
                {"root_file_count", names.size()},
                {"manifest", manifestPath},
                {"job_ids", sampleIds},
                {"manifest_entries", manifestLines}
            });
        }
        if (aggregateJobIds.size() != 100 ||
            *aggregateJobIds.begin() != 0 || *aggregateJobIds.rbegin() != 99) {
            throw std::runtime_error("Subsample job union is not exactly job IDs 0-99 for " + tune);
        }
        tuneReport["aggregate_job_ids"] = aggregateJobIds;
        tuneReport["aggregate_job_count"] = aggregateJobIds.size();

        std::size_t fileIndex = 0;
        for (const auto& fileName : centralNames[tune]) {
            ++fileIndex;
            if (fileIndex == 1 || fileIndex % 10 == 0 || fileIndex == centralNames[tune].size()) {
                std::cout << "  object inventory " << fileIndex << "/"
                          << centralNames[tune].size() << ": " << fileName << std::endl;
            }
            const std::string centralPath = Join({centralDir, fileName});
            TFile centralFile(centralPath.c_str(), "READ");
            if (centralFile.IsZombie()) throw std::runtime_error("Cannot open " + centralPath);
            tuneReport["central_fingerprints"].push_back(FileFingerprint(centralPath));
            for (const auto& objectName : kObjectNames) {
                CheckKeyType(centralFile, objectName, centralPath);
            }
            centralFile.Close();

            for (int sample = 1; sample <= nSubsamples; ++sample) {
                const std::string samplePath = Join({
                    tuneSubsampleBase, "combined_root_" + std::to_string(sample), fileName
                });
                TFile sampleFile(samplePath.c_str(), "READ");
                if (sampleFile.IsZombie()) throw std::runtime_error("Cannot open " + samplePath);
                for (const auto& objectName : kObjectNames) {
                    CheckKeyType(sampleFile, objectName, samplePath);
                }
                sampleFile.Close();
            }
        }

        for (const auto& fileName : comparisonPairs) {
            std::cout << "  central/subsample comparison: " << fileName << std::endl;
            if (!std::binary_search(centralNames[tune].begin(), centralNames[tune].end(), fileName)) {
                throw std::runtime_error("Configured pair is missing from central production: " + fileName);
            }
            const std::string centralPath = Join({centralDir, fileName});
            for (const auto& objectName : kObjectNames) {
                TFile centralFile(centralPath.c_str(), "READ");
                if (centralFile.IsZombie()) throw std::runtime_error("Cannot open " + centralPath);
                TObject* centralObject = CheckedObject(centralFile, objectName, centralPath);
                tuneSchemas[tune][fileName + "::" + objectName] = Schema(centralObject);
                const double centralEntries = Entries(centralObject);
                const double centralIntegral = Integral(centralObject);
                double subsampleEntries = 0.0;
                double subsampleIntegral = 0.0;
                for (int sample = 1; sample <= nSubsamples; ++sample) {
                    const std::string samplePath = Join({
                        tuneSubsampleBase, "combined_root_" + std::to_string(sample), fileName
                    });
                    TFile sampleFile(samplePath.c_str(), "READ");
                    TObject* sampleObject = CheckedObject(sampleFile, objectName, samplePath);
                    subsampleEntries += Entries(sampleObject);
                    subsampleIntegral += Integral(sampleObject);
                    sampleFile.Close();
                }
                const bool entriesMatch = CloseEnough(centralEntries, subsampleEntries);
                const bool integralMatch = CloseEnough(centralIntegral, subsampleIntegral);
                report["comparisons"].push_back({
                    {"tune", tune},
                    {"file", fileName},
                    {"object", objectName},
                    {"central_entries", centralEntries},
                    {"subsample_entries_sum", subsampleEntries},
                    {"entries_match", entriesMatch},
                    {"integral_checked", true},
                    {"central_integral", centralIntegral},
                    {"subsample_integral_sum", subsampleIntegral},
                    {"integral_match", integralMatch}
                });
                if (!entriesMatch || !integralMatch) {
                    throw std::runtime_error(
                        "Central/subsample mismatch for " + tune + "/" + fileName + "/" + objectName);
                }
                centralFile.Close();
            }
        }

        report["tunes"][tune] = tuneReport;
    }

    for (std::size_t index = 1; index < kTunes.size(); ++index) {
        if (centralNames[kTunes[index]] != centralNames[kTunes[0]]) {
            throw std::runtime_error("Central ROOT filename inventory differs between tunes");
        }
        if (tuneSchemas[kTunes[index]] != tuneSchemas[kTunes[0]]) {
            throw std::runtime_error("Configured object schemas differ between tunes");
        }
    }

    report["same_root_file_inventory_across_tunes"] = true;
    report["same_configured_object_schemas_across_tunes"] = true;
    report["all_required_objects_present"] = true;
    report["subsamples_disjoint"] = true;
    report["subsample_union_job_ids"] = "0-99 exactly once per tune";
    report["central_matches_subsample_union_for_representative_final_pairs"] = true;
    report["status"] = "passed";

    const std::string absoluteReportPath = AbsoluteFromBase(reportPath);
    gSystem->mkdir(gSystem->DirName(absoluteReportPath.c_str()), true);
    std::ofstream output(absoluteReportPath);
    if (!output) throw std::runtime_error("Cannot write report: " + absoluteReportPath);
    output << report.dump(2) << '\n';
    output.close();
    std::cout << "Validation passed; report written to " << absoluteReportPath << std::endl;
    return 0;
}
