#include "../AnalysisScripts/GeneratedPairRegistry.h"
#include "../SimulationScripts/Sha256.h"
#include "PairInputSelectionUtils.h"

#include <algorithm>
#include <array>
#include <cctype>
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
const std::set<std::string> kCanonicalPairFiles = [] {
    std::set<std::string> names;
    for (const auto& pair : Hadronization::kPairDefinitions) {
        names.insert(std::string(pair.filename));
    }
    return names;
}();

struct CanonicalManifestEvidence {
    std::set<std::string> rows;
    std::set<int> slots;
    std::string sha256;
    int rowsPerTune = 0;
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

bool IsDirectory(const std::string& path)
{
    void* directory = gSystem->OpenDirectory(path.c_str());
    if (!directory) return false;
    gSystem->FreeDirectory(directory);
    return true;
}

std::string ResolveCompleteRootDirectory(
    const std::string& baseDirectory,
    const std::string& tune,
    const std::string& completeRootTag)
{
    const std::vector<std::string> candidates = {
        Join({baseDirectory, tune, completeRootTag + "_" + tune}),
        Join({baseDirectory, tune, completeRootTag}),
        Join({baseDirectory, completeRootTag + "_" + tune}),
        Join({baseDirectory, completeRootTag}),
    };
    for (const auto& candidate : candidates) {
        if (IsDirectory(candidate)) return candidate;
    }
    std::ostringstream message;
    message << "Could not resolve complete-root directory for tune " << tune
            << " and tag " << completeRootTag << ". Tried:";
    for (const auto& candidate : candidates) {
        message << "\n  - " << candidate;
    }
    throw std::runtime_error(message.str());
}

std::string ResolveSubsampleTuneDirectory(
    const std::string& subsampleBase,
    const std::string& tune)
{
    const std::vector<std::string> candidates = {
        subsampleBase + "_" + tune,
        Join({subsampleBase, tune}),
    };
    for (const auto& candidate : candidates) {
        if (IsDirectory(candidate)) return candidate;
    }
    std::ostringstream message;
    message << "Could not resolve subsample directory for tune " << tune
            << ". Tried:";
    for (const auto& candidate : candidates) {
        message << "\n  - " << candidate;
    }
    throw std::runtime_error(message.str());
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

std::string EnvironmentOverride(const char* name,
                                const std::string& fallback)
{
    const char* value = std::getenv(name);
    if (!value || std::string(value).empty()) return fallback;
    return AbsoluteFromBase(value);
}

std::string EnvironmentTagOverride(const char* name,
                                   const std::string& fallback)
{
    const char* value = std::getenv(name);
    return (!value || std::string(value).empty()) ? fallback
                                                  : std::string(value);
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

bool IsSafeRelativePath(const std::string& path)
{
    if (path.empty() || path.front() == '/') return false;
    std::istringstream stream(path);
    std::string component;
    while (std::getline(stream, component, '/')) {
        if (component.empty() || component == "." || component == "..") {
            return false;
        }
    }
    return true;
}

bool IsLowerHexSha256(const std::string& value)
{
    return value.size() == 64 &&
           std::all_of(
               value.begin(), value.end(),
               [](unsigned char character) {
                   return std::isdigit(character) ||
                          (character >= 'a' && character <= 'f');
               });
}

CanonicalManifestEvidence ReadCanonicalTuneManifest(
    const std::string& manifestPath,
    const std::string& tune,
    int expectedTuneRows,
    int expectedBlock,
    int centralSlots)
{
    std::ifstream input(manifestPath);
    if (!input) {
        throw std::runtime_error(
            "Missing canonical merged source manifest: " + manifestPath);
    }

    CanonicalManifestEvidence evidence;
    evidence.sha256 = Hadronization::Sha256FileHex(manifestPath);
    std::map<std::string, int> tuneCounts;
    std::map<std::string, std::set<int>> tuneSlots;
    std::map<std::string, std::array<std::string, 3>> sourceContracts;
    std::map<std::string, std::map<std::string, int>> sourceTuneCounts;
    std::set<std::string> rawPaths;
    std::string manifestSchema;
    std::string finalCampaign;
    int finalCampaignOrdinal = -1;
    int totalRows = 0;
    std::string line;
    while (std::getline(input, line)) {
        if (line.empty()) continue;
        const json row = json::parse(line);
        const std::string rowTune = row.at("tune").get<std::string>();
        if (std::find(kTunes.begin(), kTunes.end(), rowTune) ==
            kTunes.end()) {
            throw std::runtime_error(
                "Unknown tune in canonical source manifest: " + rowTune);
        }
        const std::string rowSchema =
            row.at("schema").get<std::string>();
        if (manifestSchema.empty()) {
            manifestSchema = rowSchema;
        } else if (manifestSchema != rowSchema) {
            throw std::runtime_error(
                "Canonical source manifest mixes row schemas: " +
                manifestPath);
        }
        if ((rowSchema != "hf_canonical_raw_manifest_v2" &&
             rowSchema != "hf_superseding_canonical_raw_manifest_v3") ||
            row.at("raw_schema").get<std::string>() !=
                "hf_primary_ground_raw_v7" ||
            row.at("selector").get<std::string>() !=
                "hard_trigger_primary_ground__primary_ground_associate_v1") {
            throw std::runtime_error(
                "Canonical source-manifest contract differs: " +
                manifestPath);
        }
        if (rowSchema == "hf_canonical_raw_manifest_v2") {
            const std::string campaign =
                row.at("campaign").get<std::string>();
            if (campaign.empty() ||
                (!finalCampaign.empty() && finalCampaign != campaign)) {
                throw std::runtime_error(
                    "First-stage canonical campaign identity differs: " +
                    manifestPath);
            }
            finalCampaign = campaign;
        } else {
            const std::string campaign =
                row.at("campaign").get<std::string>();
            const std::string prefix =
                row.at("source_production_prefix").get<std::string>();
            const std::string rowFinalCampaign =
                row.at("final_campaign").get<std::string>();
            const int rowFinalOrdinal =
                row.at("final_campaign_ordinal").get<int>();
            const int sourceSlot =
                row.at("source_canonical_slot").get<int>();
            const std::array<std::string, 3> sourceContract = {
                row.at("source_manifest_sha256").get<std::string>(),
                row.at("source_freeze_summary_sha256").get<std::string>(),
                row.at("source_freeze_seal_sha256").get<std::string>(),
            };
            if (campaign.empty() || prefix != campaign ||
                rowFinalCampaign.empty() || rowFinalOrdinal < 1 ||
                sourceSlot < 0 ||
                !std::all_of(
                    sourceContract.begin(), sourceContract.end(),
                    [](const std::string& value) {
                        return IsLowerHexSha256(value);
                    }) ||
                (!finalCampaign.empty() &&
                 finalCampaign != rowFinalCampaign) ||
                (finalCampaignOrdinal >= 0 &&
                 finalCampaignOrdinal != rowFinalOrdinal)) {
                throw std::runtime_error(
                    "Superseding canonical source provenance differs: " +
                    manifestPath);
            }
            finalCampaign = rowFinalCampaign;
            finalCampaignOrdinal = rowFinalOrdinal;
            const auto known = sourceContracts.find(campaign);
            if (known == sourceContracts.end()) {
                sourceContracts[campaign] = sourceContract;
            } else if (known->second != sourceContract) {
                throw std::runtime_error(
                    "Superseding source-freeze identity differs: " +
                    manifestPath);
            }
            ++sourceTuneCounts[campaign][rowTune];
        }
        const int slot = row.at("canonical_slot").get<int>();
        const int block = row.at("block").get<int>();
        const std::string rawPath =
            row.at("raw_path").get<std::string>();
        const std::string rawSha =
            row.at("raw_sha256").get<std::string>();
        if (slot < 0 ||
            (centralSlots > 0 && slot >= centralSlots) ||
            block != slot % 10 ||
            (expectedBlock >= 0 && block != expectedBlock) ||
            row.at("requested_successes").get<int>() != 1000000 ||
            row.at("raw_bytes").get<Long64_t>() <= 0 ||
            !IsSafeRelativePath(rawPath) ||
            !rawPaths.insert(rawPath).second ||
            !IsLowerHexSha256(rawSha) ||
            !tuneSlots[rowTune].insert(slot).second) {
            throw std::runtime_error(
                "Invalid slot/block/raw path in canonical source manifest: " +
                manifestPath);
        }
        ++tuneCounts[rowTune];
        ++totalRows;
        if (rowTune != tune) continue;
        if (!evidence.slots.insert(slot).second ||
            !evidence.rows.insert(row.dump()).second) {
            throw std::runtime_error(
                "Duplicate canonical row/slot in " + manifestPath);
        }
    }

    const int derivedRows = tuneCounts[tune];
    for (const auto& source : sourceTuneCounts) {
        int expectedSourceRows = -1;
        for (const auto& expectedTune : kTunes) {
            const auto found = source.second.find(expectedTune);
            const int count =
                found == source.second.end() ? 0 : found->second;
            if (count < 1 ||
                (expectedSourceRows >= 0 && count != expectedSourceRows)) {
                throw std::runtime_error(
                    "Superseding source has unequal tune exposure: " +
                    source.first + " in " + manifestPath);
            }
            expectedSourceRows = count;
        }
    }
    if (derivedRows < 1 ||
        (expectedTuneRows > 0 && derivedRows != expectedTuneRows)) {
        throw std::runtime_error(
            "Canonical source-manifest selected tune count differs: " +
            manifestPath);
    }
    for (const auto& expectedTune : kTunes) {
        if (tuneCounts[expectedTune] != derivedRows ||
            static_cast<int>(tuneSlots[expectedTune].size()) !=
                derivedRows) {
            throw std::runtime_error(
                "Canonical source-manifest tune exposure differs: " +
                manifestPath);
        }
    }
    const int expectedTotalRows =
        derivedRows * static_cast<int>(kTunes.size());
    if (totalRows != expectedTotalRows ||
        static_cast<int>(evidence.rows.size()) != derivedRows ||
        static_cast<int>(evidence.slots.size()) != derivedRows) {
        throw std::runtime_error(
            "Canonical source-manifest row count differs: " + manifestPath);
    }
    if (expectedBlock < 0) {
        const bool validFirstStage =
            manifestSchema == "hf_canonical_raw_manifest_v2" &&
            derivedRows == 100;
        const bool validSuperseding =
            manifestSchema ==
                "hf_superseding_canonical_raw_manifest_v3" &&
            derivedRows >= 110 && derivedRows % 10 == 0 &&
            sourceContracts.size() >= 2;
        if (!validFirstStage && !validSuperseding) {
            throw std::runtime_error(
                "Canonical central manifest is not sealed-v2 N=100 or "
                "superseding-v3 equal N>=110: " +
                manifestPath);
        }
        for (const auto& expectedTune : kTunes) {
            for (int slot = 0; slot < derivedRows; ++slot) {
                if (!tuneSlots[expectedTune].count(slot)) {
                    throw std::runtime_error(
                        "Canonical central slots are not contiguous: " +
                        manifestPath);
                }
            }
        }
    } else {
        const bool validFirstStage =
            manifestSchema == "hf_canonical_raw_manifest_v2" &&
            centralSlots == 100;
        const bool validSuperseding =
            manifestSchema ==
                "hf_superseding_canonical_raw_manifest_v3" &&
            centralSlots >= 110 && centralSlots % 10 == 0 &&
            sourceContracts.size() >= 2;
        if ((!validFirstStage && !validSuperseding) ||
            derivedRows != centralSlots / 10) {
            throw std::runtime_error(
                "Canonical block exposure differs from central manifest: " +
                manifestPath);
        }
        for (const auto& expectedTune : kTunes) {
            for (int slot = expectedBlock; slot < centralSlots; slot += 10) {
                if (!tuneSlots[expectedTune].count(slot)) {
                    throw std::runtime_error(
                        "Canonical block slots are not the exact modulo "
                        "subset: " + manifestPath);
                }
            }
        }
    }
    evidence.rowsPerTune = derivedRows;
    return evidence;
}

void ValidateMergedProvenance(const std::string& directory,
                              const std::string& tune,
                              int expectedInputs,
                              const CanonicalManifestEvidence& manifest)
{
    const std::string provenancePath = Join(
        {directory, "merge_provenance.json"});
    std::ifstream input(provenancePath);
    if (!input) {
        throw std::runtime_error(
            "Missing canonical merge provenance: " + provenancePath);
    }
    json provenance;
    input >> provenance;
    const bool valid =
        provenance.value("schema", "") ==
            "hf_merged_pair_directory_provenance_v2" &&
        provenance.value("status", "") == "PASS" &&
        provenance.value("tune", "") == tune &&
        provenance.value("selected_tune", "") == tune &&
        provenance.value("source_manifest", "") ==
            "source_manifest.jsonl" &&
        provenance.value("source_manifest_scope", "") ==
            "all_tunes_with_explicit_tune_filter_v1" &&
        provenance.value("source_manifest_sha256", "") ==
            manifest.sha256 &&
        provenance.value("source_manifest_total_rows", -1) ==
            expectedInputs * static_cast<int>(kTunes.size()) &&
        provenance.value(
            "source_manifest_tune_counts", json::object()) ==
            json{
                {"MONASH", expectedInputs},
                {"JUNCTIONS", expectedInputs},
                {"CLOSEPACKING", expectedInputs},
            } &&
        provenance.value("selected_tune_input_file_count", -1) ==
            expectedInputs &&
        provenance.value("merge_input_file_count", -1) == expectedInputs &&
        provenance.value("pair_file_count", -1) ==
            static_cast<int>(kCanonicalPairFiles.size());
    if (!valid) {
        throw std::runtime_error(
            "Canonical merge provenance contract differs: " +
            provenancePath);
    }
}

std::set<int> ReadLegacyJobManifest(const std::string& manifestPath,
                                    std::set<int>& aggregateJobIds,
                                    std::set<std::string>& aggregateLines,
                                    std::vector<std::string>& lines)
{
    std::ifstream manifest(manifestPath);
    if (!manifest) {
        throw std::runtime_error("Missing manifest: " + manifestPath);
    }
    std::set<int> sampleIds;
    const std::regex jobPattern("_job([0-9]+)$");
    std::string line;
    while (std::getline(manifest, line)) {
        if (line.empty()) continue;
        std::smatch match;
        if (!std::regex_search(line, match, jobPattern)) {
            throw std::runtime_error(
                "Unrecognised manifest entry: " + line);
        }
        const int jobId = std::stoi(match[1].str());
        if (!sampleIds.insert(jobId).second ||
            !aggregateJobIds.insert(jobId).second ||
            !aggregateLines.insert(line).second) {
            throw std::runtime_error(
                "Duplicate job assignment in " + manifestPath);
        }
        lines.push_back(line);
    }
    if (sampleIds.size() != 10) {
        throw std::runtime_error(
            "Expected ten jobs in " + manifestPath);
    }
    return sampleIds;
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

    const auto selectionContract =
        HadronizationPairInput::ParseSelectionContract(
            config.at("pair_input_selection_contract"));
    const std::string configuredPairCombinatorics =
        config.at("pair_combinatorics_mode").get<std::string>();
    const double configuredSameSignFactor =
        config.at("same_sign_pair_factor").get<double>();
    const std::string analyzedBase = EnvironmentOverride(
        "HADRONIZATION_ANALYZED_DATA_BASE",
        AbsoluteFromBase(config.at("base_dir").get<std::string>()));
    const std::string completeTag = EnvironmentTagOverride(
        "HADRONIZATION_COMPLETE_ROOT_TAG",
        config.at("bb_bar_complete_root_dir").get<std::string>());
    const std::string charmCompleteTag = EnvironmentTagOverride(
        "HADRONIZATION_COMPLETE_ROOT_TAG",
        config.at("cc_bar_complete_root_dir").get<std::string>());
    if (completeTag != charmCompleteTag) {
        throw std::runtime_error("Beauty and charm complete-root tags differ");
    }
    const std::string subsampleBase = EnvironmentOverride(
        "HADRONIZATION_SUBSAMPLE_BASE",
        AbsoluteFromBase(
            config.at("bb_bar_complete_root_dir_sub_samples")
                .get<std::string>()));
    const std::string charmSubsampleBase = EnvironmentOverride(
        "HADRONIZATION_SUBSAMPLE_BASE",
        AbsoluteFromBase(
            config.at("cc_bar_complete_root_dir_sub_samples")
                .get<std::string>()));
    if (subsampleBase != charmSubsampleBase) {
        throw std::runtime_error("Beauty and charm subsample bases differ");
    }

    const std::set<std::string> configuredPairs = ConfiguredPairs(config);
    const std::set<std::string> comparisonPairs = configuredPairs;
    json report = {
        {"status", "running"},
        {"configuration", AbsoluteFromBase(configuration)},
        {"configuration_resolved", RealPath(AbsoluteFromBase(configuration))},
        {"validated_at_utc", UtcTimestamp()},
        {"validation_host", gSystem->HostName()},
        {"root_version", gROOT->GetVersion()},
        {"checkout", ProjectBase()},
        {"checkout_resolved", RealPath(ProjectBase())},
        {"central_definition",
         "resolved flat or nested from analyzed-data base + tag + tune"},
        {"subsample_definition",
         "resolved as <base>_<TUNE> or <base>/<TUNE>, then "
         "combined_root_<1..10>"},
        {"complete_root_tag", completeTag},
        {"n_subsamples", nSubsamples},
        {"pair_combinatorics_mode", configuredPairCombinatorics},
        {"same_sign_pair_factor", configuredSameSignFactor},
        {"configured_pair_files", configuredPairs},
        {"final_configured_union_comparison_files", comparisonPairs},
        {"required_objects", kObjectNames},
        {"tunes", json::object()},
        {"comparisons", json::array()}
    };

    std::map<std::string, std::vector<std::string>> centralNames;
    std::map<std::string, std::map<std::string, std::string>> tuneSchemas;
    int productionMode = -1;  // 0: exact tagged legacy; 1: canonical v2.
    int canonicalFilesPerTune = -1;
    std::string canonicalCentralManifestSha;
    std::map<int, std::string> canonicalBlockManifestSha;

    for (const auto& tune : kTunes) {
        std::cout << "Validating tune " << tune << "..." << std::endl;
        const std::string centralDir =
            ResolveCompleteRootDirectory(
                analyzedBase, tune, completeTag);
        const std::string tuneSubsampleBase =
            ResolveSubsampleTuneDirectory(subsampleBase, tune);
        centralNames[tune] = RootFiles(centralDir);
        const std::set<std::string> centralFileSet(
            centralNames[tune].begin(), centralNames[tune].end());
        std::vector<std::string> missingConfiguredPairs;
        std::set_difference(
            configuredPairs.begin(), configuredPairs.end(),
            centralFileSet.begin(), centralFileSet.end(),
            std::back_inserter(missingConfiguredPairs));
        if (!missingConfiguredPairs.empty()) {
            std::ostringstream message;
            message << "Configured pair files are absent for " << tune << ":";
            for (const auto& name : missingConfiguredPairs) {
                message << "\n  - " << name;
            }
            throw std::runtime_error(message.str());
        }
        const bool canonicalMode = centralFileSet == kCanonicalPairFiles;
        const bool legacyMode = centralNames[tune].size() == 56;
        if (!canonicalMode && !legacyMode) {
            throw std::runtime_error(
                "Central ROOT inventory is neither the exact 300-pair "
                "canonical registry nor the 56-file tagged legacy set: " +
                centralDir);
        }
        if (productionMode < 0) {
            productionMode = canonicalMode ? 1 : 0;
        } else if (productionMode != (canonicalMode ? 1 : 0)) {
            throw std::runtime_error(
                "Mixed canonical and legacy inventories across tunes");
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
        tuneReport["input_contract"] =
            canonicalMode ? "canonical_300_pair_metadata_v2"
                          : "tagged_legacy_56_pair_metadata_free";

        std::set<int> aggregateJobIds;
        std::set<std::string> aggregateManifestLines;
        std::set<std::string> aggregateCanonicalRows;
        CanonicalManifestEvidence centralManifest;
        if (canonicalMode) {
            const std::string manifestPath =
                Join({centralDir, "source_manifest.jsonl"});
            centralManifest = ReadCanonicalTuneManifest(
                manifestPath, tune, 0, -1, 0);
            if (canonicalFilesPerTune < 0) {
                canonicalFilesPerTune = centralManifest.rowsPerTune;
            } else if (canonicalFilesPerTune !=
                       centralManifest.rowsPerTune) {
                throw std::runtime_error(
                    "Canonical merged source manifests use unequal tune "
                    "exposure");
            }
            if (canonicalCentralManifestSha.empty()) {
                canonicalCentralManifestSha = centralManifest.sha256;
            } else if (canonicalCentralManifestSha !=
                       centralManifest.sha256) {
                throw std::runtime_error(
                    "Canonical central directories do not contain identical "
                    "all-tune source-manifest bytes");
            }
            ValidateMergedProvenance(
                centralDir, tune, centralManifest.rowsPerTune,
                centralManifest);
            tuneReport["central_manifest"] = manifestPath;
            tuneReport["central_manifest_sha256"] =
                centralManifest.sha256;
            tuneReport["central_input_files"] =
                centralManifest.rowsPerTune;
        }
        for (int sample = 1; sample <= nSubsamples; ++sample) {
            const std::string sampleDir =
                Join({tuneSubsampleBase, "combined_root_" + std::to_string(sample)});
            const auto names = RootFiles(sampleDir);
            if (names != centralNames[tune]) {
                throw std::runtime_error("Subsample ROOT file set differs from central: " + sampleDir);
            }

            if (canonicalMode) {
                const std::string manifestPath =
                    Join({sampleDir, "source_manifest.jsonl"});
                const CanonicalManifestEvidence sampleManifest =
                    ReadCanonicalTuneManifest(
                        manifestPath, tune,
                        centralManifest.rowsPerTune / 10, sample - 1,
                        centralManifest.rowsPerTune);
                const auto knownBlockSha =
                    canonicalBlockManifestSha.find(sample);
                if (knownBlockSha == canonicalBlockManifestSha.end()) {
                    canonicalBlockManifestSha[sample] =
                        sampleManifest.sha256;
                } else if (knownBlockSha->second != sampleManifest.sha256) {
                    throw std::runtime_error(
                        "Canonical tune directories do not contain identical "
                        "all-tune source-manifest bytes for block " +
                        std::to_string(sample));
                }
                ValidateMergedProvenance(
                    sampleDir, tune, sampleManifest.rowsPerTune,
                    sampleManifest);
                for (const auto& row : sampleManifest.rows) {
                    if (!aggregateCanonicalRows.insert(row).second) {
                        throw std::runtime_error(
                            "Duplicate canonical row across block manifests "
                            "for " + tune);
                    }
                }
                tuneReport["subsamples"].push_back({
                    {"index", sample},
                    {"directory", sampleDir},
                    {"root_file_count", names.size()},
                    {"manifest", manifestPath},
                    {"manifest_sha256", sampleManifest.sha256},
                    {"canonical_slots", sampleManifest.slots}
                });
            } else {
                const std::string manifestPath =
                    Join({sampleDir, "jobs_used.txt"});
                std::vector<std::string> manifestLines;
                const std::set<int> sampleIds = ReadLegacyJobManifest(
                    manifestPath, aggregateJobIds,
                    aggregateManifestLines, manifestLines);
                tuneReport["subsamples"].push_back({
                    {"index", sample},
                    {"directory", sampleDir},
                    {"root_file_count", names.size()},
                    {"manifest", manifestPath},
                    {"job_ids", sampleIds},
                    {"manifest_entries", manifestLines}
                });
            }
        }
        if (canonicalMode) {
            if (aggregateCanonicalRows != centralManifest.rows) {
                throw std::runtime_error(
                    "Ten canonical block manifests do not exactly union to "
                    "the central source manifest for " + tune);
            }
            tuneReport["aggregate_canonical_row_count"] =
                aggregateCanonicalRows.size();
        } else {
            if (aggregateJobIds.size() != 100 ||
                *aggregateJobIds.begin() != 0 ||
                *aggregateJobIds.rbegin() != 99) {
                throw std::runtime_error(
                    "Subsample job union is not exactly job IDs 0-99 for " +
                    tune);
            }
            tuneReport["aggregate_job_ids"] = aggregateJobIds;
            tuneReport["aggregate_job_count"] = aggregateJobIds.size();
        }

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
            const auto centralProjectionMode =
                HadronizationPairInput::ValidateSelectionMetadata(
                    centralFile, selectionContract, completeTag,
                    centralPath);
            const auto expectedProjectionMode =
                canonicalMode
                    ? HadronizationPairInput::ProjectionMode::kMetadataV2
                    : HadronizationPairInput::LegacyProjectionMode(
                          selectionContract);
            if (centralProjectionMode != expectedProjectionMode) {
                throw std::runtime_error(
                    "Central inventory and pair-selection metadata mode "
                    "disagree: " + centralPath);
            }
            HadronizationPairInput::ValidateConfiguredCombinatorics(
                centralProjectionMode, configuredPairCombinatorics,
                configuredSameSignFactor, selectionContract, centralPath);
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
                const auto sampleProjectionMode =
                    HadronizationPairInput::ValidateSelectionMetadata(
                        sampleFile, selectionContract, completeTag,
                        samplePath);
                if (sampleProjectionMode != expectedProjectionMode) {
                    throw std::runtime_error(
                        "Central/block pair-selection metadata mode differs: " +
                        samplePath);
                }
                HadronizationPairInput::ValidateConfiguredCombinatorics(
                    sampleProjectionMode, configuredPairCombinatorics,
                    configuredSameSignFactor, selectionContract, samplePath);
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
    report["input_contract"] =
        productionMode == 1 ? "canonical_300_pair_metadata_v2"
                            : "tagged_legacy_56_pair_metadata_free";
    report["pair_selection_projection_mode"] =
        productionMode == 1 ? "metadata_v2_upstream_selected"
                            : "tagged_legacy_plot_recuts_v1";
    if (productionMode == 1) {
        report["canonical_files_per_tune"] = canonicalFilesPerTune;
        report["canonical_files_per_tune_per_block"] =
            canonicalFilesPerTune / 10;
    }
    report["subsample_union"] =
        productionMode == 1
            ? "ten canonical block source manifests exactly union to the "
              "central tune subset"
            : "legacy job IDs 0-99 exactly once per tune";
    report["central_matches_subsample_union_for_all_configured_final_pairs"] =
        true;
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

int TestTHnSparseCanonicalSourceManifest(
    const char* centralManifestPath,
    const char* blockManifestPath,
    int expectedFilesPerTune = 110)
{
    int errors = 0;
    try {
        const CanonicalManifestEvidence central =
            ReadCanonicalTuneManifest(
                centralManifestPath, "MONASH",
                expectedFilesPerTune, -1, 0);
        const CanonicalManifestEvidence block =
            ReadCanonicalTuneManifest(
                blockManifestPath, "MONASH",
                expectedFilesPerTune / 10, 0,
                expectedFilesPerTune);
        if (central.rowsPerTune != expectedFilesPerTune ||
            block.rowsPerTune != expectedFilesPerTune / 10 ||
            static_cast<int>(central.rows.size()) !=
                expectedFilesPerTune ||
            static_cast<int>(block.rows.size()) !=
                expectedFilesPerTune / 10) {
            ++errors;
        }
        for (const auto& row : block.rows) {
            if (!central.rows.count(row)) ++errors;
        }
        if (kCanonicalPairFiles.size() !=
            Hadronization::kPairDefinitions.size()) {
            ++errors;
        }
    } catch (const std::exception& error) {
        std::cerr << "THNSPARSE_CANONICAL_MANIFEST_TEST_ERROR "
                  << error.what() << std::endl;
        ++errors;
    }
    std::cout << "THNSPARSE_CANONICAL_MANIFEST_TEST "
              << "errors=" << errors
              << " files_per_tune=" << expectedFilesPerTune
              << " files_per_block=" << expectedFilesPerTune / 10
              << " pair_registry_files=" << kCanonicalPairFiles.size()
              << std::endl;
    return errors;
}

int TestTHnSparseDatasetSelectorOverrides(
    const char* analyzedDataBase,
    const char* completeRootTag,
    const char* subsampleBase)
{
    const std::array<const char*, 3> names = {
        "HADRONIZATION_ANALYZED_DATA_BASE",
        "HADRONIZATION_COMPLETE_ROOT_TAG",
        "HADRONIZATION_SUBSAMPLE_BASE",
    };
    std::array<bool, 3> existed{};
    std::array<std::string, 3> previous{};
    for (std::size_t index = 0; index < names.size(); ++index) {
        const char* value = std::getenv(names[index]);
        existed[index] = value != nullptr;
        previous[index] = value ? value : "";
    }
    auto restore = [&]() {
        for (std::size_t index = 0; index < names.size(); ++index) {
            if (existed[index]) {
                gSystem->Setenv(names[index], previous[index].c_str());
            } else {
                gSystem->Unsetenv(names[index]);
            }
        }
    };

    int errors = 0;
    try {
        gSystem->Setenv(names[0], analyzedDataBase);
        gSystem->Setenv(names[1], completeRootTag);
        gSystem->Setenv(names[2], subsampleBase);
        const std::string selectedBase =
            EnvironmentOverride(names[0], "unused-base");
        const std::string selectedTag =
            EnvironmentTagOverride(names[1], "unused-tag");
        const std::string selectedSubsamples =
            EnvironmentOverride(names[2], "unused-subsamples");
        if (selectedBase != AbsoluteFromBase(analyzedDataBase) ||
            selectedTag != completeRootTag ||
            selectedSubsamples != AbsoluteFromBase(subsampleBase)) {
            ++errors;
        }
        if (ResolveCompleteRootDirectory(
                selectedBase, "MONASH", selectedTag) !=
                Join({selectedBase, "MONASH",
                      selectedTag + "_MONASH"}) ||
            ResolveSubsampleTuneDirectory(
                selectedSubsamples, "MONASH") !=
                Join({selectedSubsamples, "MONASH"})) {
            ++errors;
        }
    } catch (const std::exception& error) {
        std::cerr << "THNSPARSE_DATASET_SELECTOR_TEST_ERROR "
                  << error.what() << std::endl;
        ++errors;
    }
    restore();
    std::cout << "THNSPARSE_DATASET_SELECTOR_TEST errors=" << errors
              << " overrides=true nested_layout=true"
              << std::endl;
    return errors;
}
