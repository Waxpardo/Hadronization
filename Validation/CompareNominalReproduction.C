// Pre-registration S10.1: does the rebuilt producer reproduce the nominal?
//
//   root -l -b -q 'Validation/CompareNominalReproduction.C("reference.root","candidate.root")'
//
// The systematics deployment rebuilt the producer, because the audited-key list
// grew from 46 to 49 (config/systematic_variation_settings_v1.json). The
// pre-registration's first positive check is that this rebuild still reproduces
// the nominal: "A deployment that cannot reproduce the nominal is not a
// variation of it."
//
// WHAT MUST MATCH, AND WHY THAT IS THE RIGHT BAR. Byte identity is the wrong
// bar and would fail for legitimate reasons: the two files carry different
// executable_sha256 and repository_commit, and the effective_settings /
// audited-key snapshot has three more rows. What must match is the PHYSICS --
// every value in the event tree, for the same seed. The producer translation
// unit is byte-identical between the campaign commit and the deploy commit
// (verified in git), so any difference in the event tree would mean the
// registry-header change reached the event loop, which it must not.
//
// So this compares the event tree leaf by leaf, entry by entry, and reports
// metadata differences as a labelled list rather than as a failure -- the
// caller decides which of those are expected.

#include "TFile.h"
#include "TLeaf.h"
#include "TObjArray.h"
#include "TTree.h"

#include <algorithm>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

namespace {

// FNV-1a over the decimal rendering of every leaf value, in a fixed leaf order.
// Decimal rather than raw bytes so that a difference in storage layout between
// two ROOT writes cannot masquerade as a physics difference.
struct Hash {
    std::uint64_t state = 1469598103934665603ULL;
    void feed(const std::string& text) {
        for (const unsigned char byte : text) {
            state ^= byte;
            state *= 1099511628211ULL;
        }
    }
};

std::vector<std::string> LeafNames(TTree* tree) {
    std::vector<std::string> names;
    TObjArray* leaves = tree->GetListOfLeaves();
    for (int index = 0; index < leaves->GetEntries(); ++index) {
        names.emplace_back(
            static_cast<TLeaf*>(leaves->At(index))->GetName());
    }
    std::sort(names.begin(), names.end());
    return names;
}

// Digest of every value in the tree, leaf order fixed by name so the two files
// are walked identically even if their branch order differed.
std::uint64_t TreeDigest(TTree* tree, const std::vector<std::string>& names,
                         long long& valuesRead) {
    Hash hash;
    const long long entries = tree->GetEntries();
    valuesRead = 0;
    for (long long entry = 0; entry < entries; ++entry) {
        tree->GetEntry(entry);
        for (const std::string& name : names) {
            TLeaf* leaf = tree->GetLeaf(name.c_str());
            if (leaf == nullptr) continue;
            const int count = leaf->GetLen();
            hash.feed(name);
            for (int element = 0; element < count; ++element) {
                std::ostringstream rendered;
                rendered << std::setprecision(17) << leaf->GetValue(element);
                hash.feed(rendered.str());
                hash.feed(",");
                ++valuesRead;
            }
        }
    }
    return hash.state;
}

// String metadata must be read as strings, not through TLeaf::GetValue.
// The three differences this comparison EXPECTS -- executable_sha256,
// repository_commit and the audited-settings digest -- are all string fields, so
// reading them numerically would have compared pointers and reported "no
// differences" for exactly the fields that must differ.
std::map<std::string, std::string> MetadataValues(TTree* tree) {
    std::map<std::string, std::string> values;
    if (tree == nullptr || tree->GetEntries() < 1) return values;

    TObjArray* leaves = tree->GetListOfLeaves();
    std::vector<std::string> stringBranches;
    for (int index = 0; index < leaves->GetEntries(); ++index) {
        auto* leaf = static_cast<TLeaf*>(leaves->At(index));
        if (std::string(leaf->GetTypeName()) == "string") {
            stringBranches.emplace_back(leaf->GetName());
        }
    }
    // Read THROUGH the pointer ROOT owns, not through a buffer handed to it.
    //
    // The first version of this passed the address of a local std::string and
    // then read that local back. ROOT is free to replace the pointer with its
    // own buffer -- which it does -- so the local stayed empty, every string
    // field compared "" to "", and the two fields that MUST differ
    // (executable_sha256, repository_commit) were reported as identical. A
    // silent false negative on exactly the fields the check is about.
    //
    // reserve() first: the vector must not reallocate after its element
    // addresses have been handed to SetBranchAddress.
    std::vector<std::string*> targets;
    targets.reserve(stringBranches.size());
    for (std::size_t index = 0; index < stringBranches.size(); ++index) {
        targets.push_back(nullptr);
        tree->SetBranchAddress(stringBranches[index].c_str(), &targets[index]);
    }

    tree->GetEntry(0);

    for (std::size_t index = 0; index < stringBranches.size(); ++index) {
        values[stringBranches[index]] =
            targets[index] != nullptr ? *targets[index] : "<unreadable>";
    }
    for (int index = 0; index < leaves->GetEntries(); ++index) {
        auto* leaf = static_cast<TLeaf*>(leaves->At(index));
        const std::string name = leaf->GetName();
        if (values.count(name) != 0) continue;
        if (leaf->GetLeafCount() != nullptr) {
            values[name] = "<variable-length, not compared>";
            continue;
        }
        std::ostringstream rendered;
        rendered << std::setprecision(17) << leaf->GetValue(0);
        values[name] = rendered.str();
    }
    return values;
}

}  // namespace

int CompareNominalReproduction(const char* referencePath,
                               const char* candidatePath) {
    TFile reference(referencePath, "READ");
    TFile candidate(candidatePath, "READ");
    if (reference.IsZombie() || candidate.IsZombie()) {
        std::cerr << "ERROR: could not open both files\n";
        return 2;
    }

    auto* referenceTree = dynamic_cast<TTree*>(reference.Get("tree"));
    auto* candidateTree = dynamic_cast<TTree*>(candidate.Get("tree"));
    if (referenceTree == nullptr || candidateTree == nullptr) {
        std::cerr << "ERROR: missing event tree in one of the files\n";
        return 2;
    }

    const long long referenceEntries = referenceTree->GetEntries();
    const long long candidateEntries = candidateTree->GetEntries();
    std::cout << "event tree entries: reference " << referenceEntries
              << ", candidate " << candidateEntries << "\n";

    const std::vector<std::string> referenceLeaves = LeafNames(referenceTree);
    const std::vector<std::string> candidateLeaves = LeafNames(candidateTree);
    std::cout << "event tree leaves:  reference " << referenceLeaves.size()
              << ", candidate " << candidateLeaves.size() << "\n";

    int status = 0;
    if (referenceLeaves != candidateLeaves) {
        std::cout << "LEAF SET DIFFERS -- the event tree schema changed\n";
        status = 1;
    }
    if (referenceEntries != candidateEntries) {
        std::cout << "ENTRY COUNT DIFFERS\n";
        status = 1;
    }

    if (status == 0) {
        long long referenceValues = 0;
        long long candidateValues = 0;
        const std::uint64_t referenceDigest =
            TreeDigest(referenceTree, referenceLeaves, referenceValues);
        const std::uint64_t candidateDigest =
            TreeDigest(candidateTree, candidateLeaves, candidateValues);
        std::cout << "values compared:    " << referenceValues << " vs "
                  << candidateValues << "\n";
        std::cout << "event tree digest:  " << std::hex << referenceDigest
                  << " vs " << candidateDigest << std::dec << "\n";
        if (referenceDigest != candidateDigest ||
            referenceValues != candidateValues) {
            std::cout << "EVENT TREE CONTENT DIFFERS -- the rebuild reached "
                         "the event loop\n";
            status = 1;
        } else {
            std::cout << "EVENT TREE IDENTICAL -- every value, every entry\n";
        }
    }

    // Metadata differences are REPORTED, not judged. Three are expected:
    // executable_sha256, repository_commit, and the audited-settings count.
    auto referenceMetadata =
        MetadataValues(dynamic_cast<TTree*>(reference.Get("job_metadata")));
    auto candidateMetadata =
        MetadataValues(dynamic_cast<TTree*>(candidate.Get("job_metadata")));
    std::cout << "\njob_metadata fields differing (strings read as strings):\n";
    int differing = 0;
    for (const auto& [name, value] : referenceMetadata) {
        const auto found = candidateMetadata.find(name);
        if (found == candidateMetadata.end()) {
            std::cout << "  " << name << ": absent in candidate\n";
            ++differing;
        } else if (found->second != value) {
            std::cout << "  " << name << ": " << value << " -> "
                      << found->second << "\n";
            ++differing;
        }
    }
    if (differing == 0) std::cout << "  (none)\n";
    std::cout << "\nNOMINAL_REPRODUCTION "
              << (status == 0 ? "PASS" : "FAIL")
              << " metadata_fields_differing=" << differing << "\n";
    return status;
}
