// T1: the generated-sample table, counted from the current campaign's raw trees.
//
//   root -l -b -q 'tools/count_generated_sample.C("<input>","<out.json>","MONASH")'
//
// <input> is a raw file, a directory of them, or a text file listing one path
// per line. The output JSON carries the counts, the event totals, and the
// definition block that says what was counted; a TeX table body is written
// beside it.
//
// WHAT IS COUNTED, AND WHAT IS DELIBERATELY NOT (ruling R37, owner decision O2).
//
// SPECIES YIELDS are exact signed-PDG matches over `heavyPdg`, filtered on
// `heavyIsFinal`. Eight rows: B+, B-, Lambda_b, Lambda_b-bar, D+, D-,
// Lambda_c+, Lambda_c-bar.
//
// CONTENT SUMS are sum(heavyNc + heavyNcbar) and sum(heavyNb + heavyNbbar) over
// the same `heavyIsFinal` filter: the heavy QUARKS bound inside final heavy
// hadrons. A hidden-heavy state contributes 2, which is correct -- a J/psi
// carries one c and one c-bar.
//
// NOT `final_heavy_qc_sum` / `final_heavy_qb_sum` (finding F55). Those are the
// NET-VALENCE conservation checksums, qc = nc - ncbar summed over the event
// (HeavyFlavourUtils.h:344-345), and the producer requires them to be ZERO in a
// good event: `heavyFlavourConservationOk = finalHeavyQcSum == 0 &&
// finalHeavyQbSum == 0` (heavyflavourcorrelations_status.cpp:1369-1370). Using
// them would tabulate zero and look like a sample with no heavy flavour in it.
//
// NO KINEMATIC ACCEPTANCE. The producer stores every `isHadron &&
// hasHeavyConstituent` particle with no isFinal gate and no cut at storage
// (`:1071`); this macro applies `heavyIsFinal` and nothing else. The old
// table's `acc` superscript described a different quantity (pT >= 0.15,
// |eta| <= 4) and does not survive.
//
// THE BRANCH PREFLIGHT IS THE POINT OF THIS FILE'S CAUTION. A missing branch in
// a chain reads as a silent zero, and a table of zeros is a publishable-looking
// artifact. Every required branch is checked by name before a single entry is
// read, and an absent one is refused by name.

#include "TChain.h"
#include "TFile.h"
#include "TSystem.h"
#include "TSystemDirectory.h"
#include "TSystemFile.h"

#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

namespace {

const char* const kTreeName = "tree";

// The branches this count cannot be computed without.
const std::vector<std::string> kRequiredBranches = {
    "heavyPdg", "heavyIsFinal", "heavyNc", "heavyNcbar", "heavyNb", "heavyNbbar",
};

struct Species {
    int pdg;
    const char* key;    // JSON key
    const char* tex;    // TeX row label
};

// The eight rows of the sample table, in the manuscript's own order.
const std::vector<Species> kSpecies = {
    {  521, "Bplus",           "$B^{+}$"},
    { -521, "Bminus",          "$B^{-}$"},
    { 5122, "Lambdab",         "$\\Lambda_{b}^{0}$"},
    {-5122, "Lambdabbar",      "$\\overline{\\Lambda}_{b}^{0}$"},
    {  411, "Dplus",           "$D^{+}$"},
    { -411, "Dminus",          "$D^{-}$"},
    { 4122, "Lambdacplus",     "$\\Lambda_{c}^{+}$"},
    {-4122, "Lambdacplusbar",  "$\\overline{\\Lambda}_{c}^{-}$"},
};

std::string JsonEscape(const std::string& text)
{
    std::string out;
    for (const char c : text) {
        if (c == '"' || c == '\\') { out += '\\'; }
        out += c;
    }
    return out;
}

// Thin-space thousands separators, the form the manuscript table uses.
std::string TexNumber(long long value)
{
    std::string digits = std::to_string(value < 0 ? -value : value);
    std::string out;
    for (std::size_t i = 0; i < digits.size(); ++i) {
        if (i > 0 && (digits.size() - i) % 3 == 0) { out += "\\,"; }
        out += digits[i];
    }
    return (value < 0 ? "-" : "") + out;
}

bool HasSuffix(const std::string& text, const std::string& suffix)
{
    return text.size() >= suffix.size() &&
           text.compare(text.size() - suffix.size(), suffix.size(), suffix) == 0;
}

// A file, a directory of .root files, or a text file listing paths.
std::vector<std::string> ResolveInputs(const std::string& input)
{
    std::vector<std::string> paths;
    FileStat_t stat;
    if (gSystem->GetPathInfo(input.c_str(), stat) != 0) {
        throw std::runtime_error("input does not exist: " + input);
    }
    if (R_ISDIR(stat.fMode)) {
        TSystemDirectory directory(input.c_str(), input.c_str());
        TList* files = directory.GetListOfFiles();
        if (files == nullptr) {
            throw std::runtime_error("cannot list directory: " + input);
        }
        TIter next(files);
        while (TObject* entry = next()) {
            const std::string name = entry->GetName();
            if (HasSuffix(name, ".root")) { paths.push_back(input + "/" + name); }
        }
        std::sort(paths.begin(), paths.end());
    } else if (HasSuffix(input, ".root")) {
        paths.push_back(input);
    } else {
        std::ifstream listing(input);
        std::string line;
        while (std::getline(listing, line)) {
            while (!line.empty() && (line.back() == '\r' || line.back() == ' ')) {
                line.pop_back();
            }
            if (!line.empty() && line[0] != '#') { paths.push_back(line); }
        }
    }
    if (paths.empty()) {
        throw std::runtime_error("no input .root files resolved from: " + input);
    }
    return paths;
}

}  // namespace

int count_generated_sample(const char* input,
                           const char* outputJson,
                           const char* tuneLabel = "")
{
    try {
        const std::vector<std::string> paths = ResolveInputs(input);

        TChain chain(kTreeName);
        for (const std::string& path : paths) {
            if (chain.Add(path.c_str(), 0) == 0) {
                throw std::runtime_error("no '" + std::string(kTreeName) +
                                         "' tree in " + path);
            }
        }
        const Long64_t entries = chain.GetEntries();
        if (entries <= 0) {
            throw std::runtime_error("the chain carries no entries");
        }

        // THE PREFLIGHT. Before any entry is read: every required branch, by
        // name. Without this a renamed or absent branch reads as a silent zero.
        std::vector<std::string> missing;
        for (const std::string& name : kRequiredBranches) {
            if (chain.GetBranch(name.c_str()) == nullptr) {
                missing.push_back(name);
            }
        }
        if (!missing.empty()) {
            std::string joined;
            for (const std::string& name : missing) {
                if (!joined.empty()) { joined += ", "; }
                joined += name;
            }
            throw std::runtime_error(
                "the input tree is missing required branch(es): " + joined +
                ". A count over an absent branch is a silent zero, so this is "
                "refused rather than reported.");
        }

        std::vector<int>* heavyPdg = nullptr;
        std::vector<int>* heavyIsFinal = nullptr;
        std::vector<int>* heavyNc = nullptr;
        std::vector<int>* heavyNcbar = nullptr;
        std::vector<int>* heavyNb = nullptr;
        std::vector<int>* heavyNbbar = nullptr;

        chain.SetBranchAddress("heavyPdg", &heavyPdg);
        chain.SetBranchAddress("heavyIsFinal", &heavyIsFinal);
        chain.SetBranchAddress("heavyNc", &heavyNc);
        chain.SetBranchAddress("heavyNcbar", &heavyNcbar);
        chain.SetBranchAddress("heavyNb", &heavyNb);
        chain.SetBranchAddress("heavyNbbar", &heavyNbbar);

        std::map<int, long long> yields;
        for (const Species& species : kSpecies) { yields[species.pdg] = 0; }
        long long charmContent = 0;
        long long beautyContent = 0;
        long long finalHeavyHadrons = 0;

        for (Long64_t entry = 0; entry < entries; ++entry) {
            chain.GetEntry(entry);
            const std::size_t size = heavyPdg->size();
            if (heavyIsFinal->size() != size || heavyNc->size() != size ||
                heavyNcbar->size() != size || heavyNb->size() != size ||
                heavyNbbar->size() != size) {
                throw std::runtime_error(
                    "heavy vectors disagree on length in entry " +
                    std::to_string(entry));
            }
            for (std::size_t i = 0; i < size; ++i) {
                if ((*heavyIsFinal)[i] == 0) { continue; }
                ++finalHeavyHadrons;
                const int pdg = (*heavyPdg)[i];
                const auto found = yields.find(pdg);
                if (found != yields.end()) { ++found->second; }
                charmContent += (*heavyNc)[i] + (*heavyNcbar)[i];
                beautyContent += (*heavyNb)[i] + (*heavyNbbar)[i];
            }
        }

        std::ostringstream json;
        json << std::setprecision(17);
        json << "{\n";
        json << "  \"schema\": \"hadronization_generated_sample_count_v1\",\n";
        json << "  \"tune\": \"" << JsonEscape(tuneLabel) << "\",\n";
        json << "  \"input\": \"" << JsonEscape(input) << "\",\n";
        json << "  \"input_file_count\": " << paths.size() << ",\n";
        json << "  \"events\": " << entries << ",\n";
        json << "  \"final_heavy_hadrons\": " << finalHeavyHadrons << ",\n";
        json << "  \"content_sums\": {\n";
        json << "    \"charm\": " << charmContent << ",\n";
        json << "    \"beauty\": " << beautyContent << "\n";
        json << "  },\n";
        json << "  \"species_yields\": {\n";
        for (std::size_t i = 0; i < kSpecies.size(); ++i) {
            json << "    \"" << kSpecies[i].key << "\": "
                 << yields[kSpecies[i].pdg]
                 << (i + 1 < kSpecies.size() ? ",\n" : "\n");
        }
        json << "  },\n";
        json << "  \"definitions\": {\n";
        json << "    \"species_yield\": \"exact signed-PDG match over heavyPdg, "
                "filtered on heavyIsFinal\",\n";
        json << "    \"content_sum_charm\": \"sum(heavyNc + heavyNcbar) over "
                "heavyIsFinal; heavy quarks bound in final heavy hadrons; a "
                "hidden-charm state contributes 2\",\n";
        json << "    \"content_sum_beauty\": \"sum(heavyNb + heavyNbbar) over "
                "heavyIsFinal\",\n";
        json << "    \"not_used\": \"final_heavy_qc_sum and final_heavy_qb_sum "
                "are net-valence conservation checksums, zero in a good event "
                "(heavyflavourcorrelations_status.cpp:1369-1370)\",\n";
        json << "    \"acceptance\": \"none; the producer stores every isHadron "
                "&& hasHeavyConstituent particle with no kinematic cut at "
                "storage (:1071) and this count applies heavyIsFinal only\",\n";
        json << "    \"decay_policy\": \"StabilizeHeavyHadrons (:360-421) "
                "disables decay for every heavy-flavour hadron in the PYTHIA "
                "table and throws if one remains enabled, so content is counted "
                "at hadronization, before weak decays\",\n";
        json << "    \"record\": \"docs2/physics/SAMPLE_COUNTING.md\"\n";
        json << "  }\n";
        json << "}\n";

        std::ofstream out(outputJson);
        if (!out) {
            throw std::runtime_error("cannot write " + std::string(outputJson));
        }
        out << json.str();
        out.close();

        // The TeX table body, in the manuscript's row order and separators.
        const std::string texPath = std::string(outputJson) + ".tex";
        std::ofstream tex(texPath);
        tex << "$N_{\\mathrm{ev}}$ & " << TexNumber(entries) << " \\\\\n";
        tex << "$N_{b+\\bar b}$ & " << TexNumber(beautyContent) << " \\\\\n";
        tex << "$N_{c+\\bar c}$ & " << TexNumber(charmContent) << " \\\\\n";
        tex << "\\midrule\n";
        for (const Species& species : kSpecies) {
            tex << species.tex << " & " << TexNumber(yields[species.pdg])
                << " \\\\\n";
        }
        tex.close();

        std::cout << "GENERATED_SAMPLE_COUNT tune=" << tuneLabel
                  << " files=" << paths.size()
                  << " events=" << entries
                  << " final_heavy_hadrons=" << finalHeavyHadrons
                  << " content_c=" << charmContent
                  << " content_b=" << beautyContent << std::endl;
        std::cout << "GENERATED_SAMPLE_COUNT_WROTE " << outputJson
                  << " " << texPath << std::endl;
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "GENERATED_SAMPLE_COUNT_REFUSED " << error.what()
                  << std::endl;
        return 1;
    }
}
