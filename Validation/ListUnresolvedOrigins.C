#include "../generation/registries/GeneratedHeavyFlavourRegistry.h"
#include "../generation/producer/HeavyFlavourUtils.h"
#include "../generation/producer/Sha256.h"
#include "../contracts/GeneratedPairRegistry.h"

#include <TFile.h>
#include <TTree.h>

#include <nlohmann/json.hpp>

#include <algorithm>
#include <array>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

bool IsPublicationTriggerForUnresolvedList(int pdg) {
  return std::any_of(
      Hadronization::kPairDefinitions.begin(),
      Hadronization::kPairDefinitions.end(),
      [pdg](const Hadronization::PairDefinition& pair) {
        return pair.triggerPdg == pdg;
      });
}

struct UnresolvedCounts {
  ULong64_t candidates = 0;
  double sumWeights = 0.0;
  double sumWeights2 = 0.0;
};

void VerifyRawValidationReceiptForList(const char* rawPath,
                                       const char* receiptPath,
                                       const std::string& tune) {
  if (!receiptPath || std::string(receiptPath).empty()) {
    throw std::runtime_error(
        "a raw-validation PASS receipt is mandatory");
  }
  const std::filesystem::path path(receiptPath);
  if (!std::filesystem::is_regular_file(path) ||
      std::filesystem::is_symlink(path)) {
    throw std::runtime_error(
        "raw-validation receipt is absent, non-regular, or a symlink");
  }
  std::ifstream stream(path);
  nlohmann::json receipt;
  stream >> receipt;
  // Three receipt generations; see the same block in AuditOriginResolution.C.
  // v1 = result / validator_exit_status, has output_bytes.
  // v2 = state / validator_status, has NO output_bytes -- a weaker contract,
  //      accepted so the HF_PT2 campaign stays auditable.
  // v3 = state / validator_status, output_bytes restored.
  const std::string receiptSchema = receipt.value("schema", std::string());
  const bool isV1 = receiptSchema == "hf_raw_validation_receipt_v1";
  const bool isV2 = receiptSchema == "hf_raw_validation_receipt_v2";
  const bool isV3 = receiptSchema == "hf_raw_validation_receipt_v3";
  const bool bindsInputBytes = isV1 || isV3;
  const std::string receiptVerdict =
      receipt.contains("state") ? receipt.value("state", std::string())
                                : receipt.value("result", std::string());
  const int receiptExitStatus =
      receipt.contains("validator_status")
          ? receipt.value("validator_status", -1)
          : receipt.value("validator_exit_status", -1);
  // v2 and v3 lift tune to the top level; v1 kept it inside expected_provenance.
  const std::string receiptTune =
      receipt.contains("tune")
          ? receipt.value("tune", std::string())
          : (receipt.contains("expected_provenance") &&
                     receipt["expected_provenance"].is_object()
                 ? receipt["expected_provenance"].value("tune", std::string())
                 : std::string());
  // The v1 expected_provenance.attempt_start_claim_sha256 binding is NOT
  // checked any more. It hashed a submission claim, and claims were removed
  // with the gate layer, so no current receipt can carry one and none can be
  // reconstructed. The tune binding it also provided is preserved above.
  if ((!isV1 && !isV2 && !isV3) ||
      receiptVerdict != "PASS" ||
      receiptExitStatus != 0 ||
      receiptTune != tune ||
      receipt.value("output_sha256", std::string()) !=
          Hadronization::Sha256FileHex(rawPath) ||
      (bindsInputBytes &&
       receipt.value("output_bytes", std::uintmax_t{0}) !=
           std::filesystem::file_size(rawPath))) {
    throw std::runtime_error(
        "raw-validation receipt does not bind an exact PASS/provenance");
  }
  if (isV2) {
    std::cerr << "RAW_RECEIPT_WEAK_BINDING schema=" << receiptSchema
              << " path=" << path
              << " (no output_bytes; input-size binding unchecked)\n";
  }
}

}  // namespace

int ListUnresolvedOrigins(const char* path,
                          const char* validationReceiptPath,
                          int maximumRows = 20) {
  try {
    if (maximumRows < 0) {
      throw std::runtime_error("maximumRows must be nonnegative");
    }
    TFile input(path, "READ");
    if (input.IsZombie()) throw std::runtime_error("cannot open raw input");
    auto* tree = dynamic_cast<TTree*>(input.Get("tree"));
    auto* metadata = dynamic_cast<TTree*>(input.Get("job_metadata"));
    if (!tree || !metadata || metadata->GetEntries() != 1) {
      throw std::runtime_error("missing raw tree or single-row job_metadata");
    }

    const std::array<const char*, 5> metadataBranches = {
        "raw_schema", "selector", "origin_algorithm", "tune", "complete"};
    for (const char* name : metadataBranches) {
      if (!metadata->GetBranch(name)) {
        throw std::runtime_error(std::string("missing metadata branch ") +
                                 name);
      }
    }
    std::string* rawSchema = nullptr;
    std::string* selector = nullptr;
    std::string* originAlgorithm = nullptr;
    std::string* tunePointer = nullptr;
    Int_t complete = 0;
    metadata->SetBranchAddress("raw_schema", &rawSchema);
    metadata->SetBranchAddress("selector", &selector);
    metadata->SetBranchAddress("origin_algorithm", &originAlgorithm);
    metadata->SetBranchAddress("tune", &tunePointer);
    metadata->SetBranchAddress("complete", &complete);
    metadata->GetEntry(0);
    if (!rawSchema || !selector || !originAlgorithm || !tunePointer ||
        *rawSchema != Hadronization::kRawSchema ||
        *selector != Hadronization::kSelectorVersion ||
        *originAlgorithm != Hadronization::kOriginAlgorithmVersion ||
        complete != 1) {
      metadata->ResetBranchAddresses();
      throw std::runtime_error(
          "input does not satisfy the publication raw contract");
    }
    const std::string tune = *tunePointer;
    metadata->ResetBranchAddresses();
    VerifyRawValidationReceiptForList(path, validationReceiptPath, tune);

    const std::array<const char*, 24> requiredBranches = {
        "event_id",
        "hard_channel",
        "event_weight",
        "multiplicity_primary_charged_eta10_v1",
        "heavyIndex",
        "heavyPdg",
        "heavyStatus",
        "heavyIsFinal",
        "heavyCentral",
        "heavyQc",
        "heavyQb",
        "heavyOriginC",
        "heavyOriginB",
        "heavyMatchResolutionC",
        "heavyMatchResolutionB",
        "heavyMatchedHardC",
        "heavyMatchedHardB",
        "heavyRejectedHardC",
        "heavyRejectedHardB",
        "heavyOriginDepthC",
        "heavyOriginDepthB",
        "heavyMotherOffsets",
        "heavyMothers",
        "heavyPt"};
    for (const char* name : requiredBranches) {
      if (!tree->GetBranch(name)) {
        throw std::runtime_error(std::string("missing raw branch ") + name);
      }
    }
    if (!tree->GetBranch("heavyEta")) {
      throw std::runtime_error("missing raw branch heavyEta");
    }

    ULong64_t eventId = 0;
    Int_t hardChannel = 0;
    Int_t multiplicity = 0;
    Double_t eventWeight = 0.0;
    std::vector<int>* heavyIndex = nullptr;
    std::vector<int>* pdg = nullptr;
    std::vector<int>* status = nullptr;
    std::vector<int>* isFinal = nullptr;
    std::vector<int>* central = nullptr;
    std::vector<int>* qc = nullptr;
    std::vector<int>* qb = nullptr;
    std::vector<int>* originC = nullptr;
    std::vector<int>* originB = nullptr;
    std::vector<int>* resolutionC = nullptr;
    std::vector<int>* resolutionB = nullptr;
    std::vector<int>* matchedC = nullptr;
    std::vector<int>* matchedB = nullptr;
    std::vector<int>* rejectedC = nullptr;
    std::vector<int>* rejectedB = nullptr;
    std::vector<int>* depthC = nullptr;
    std::vector<int>* depthB = nullptr;
    std::vector<int>* motherOffsets = nullptr;
    std::vector<int>* mothers = nullptr;
    std::vector<double>* pt = nullptr;
    std::vector<double>* eta = nullptr;
    tree->SetBranchAddress("event_id", &eventId);
    tree->SetBranchAddress("hard_channel", &hardChannel);
    tree->SetBranchAddress("event_weight", &eventWeight);
    tree->SetBranchAddress("multiplicity_primary_charged_eta10_v1", &multiplicity);
    tree->SetBranchAddress("heavyIndex", &heavyIndex);
    tree->SetBranchAddress("heavyPdg", &pdg);
    tree->SetBranchAddress("heavyStatus", &status);
    tree->SetBranchAddress("heavyIsFinal", &isFinal);
    tree->SetBranchAddress("heavyCentral", &central);
    tree->SetBranchAddress("heavyQc", &qc);
    tree->SetBranchAddress("heavyQb", &qb);
    tree->SetBranchAddress("heavyOriginC", &originC);
    tree->SetBranchAddress("heavyOriginB", &originB);
    tree->SetBranchAddress("heavyMatchResolutionC", &resolutionC);
    tree->SetBranchAddress("heavyMatchResolutionB", &resolutionB);
    tree->SetBranchAddress("heavyMatchedHardC", &matchedC);
    tree->SetBranchAddress("heavyMatchedHardB", &matchedB);
    tree->SetBranchAddress("heavyRejectedHardC", &rejectedC);
    tree->SetBranchAddress("heavyRejectedHardB", &rejectedB);
    tree->SetBranchAddress("heavyOriginDepthC", &depthC);
    tree->SetBranchAddress("heavyOriginDepthB", &depthB);
    tree->SetBranchAddress("heavyMotherOffsets", &motherOffsets);
    tree->SetBranchAddress("heavyMothers", &mothers);
    tree->SetBranchAddress("heavyPt", &pt);
    tree->SetBranchAddress("heavyEta", &eta);

    std::map<std::string, UnresolvedCounts> counts;
    int rows = 0;
    for (Long64_t entry = 0; entry < tree->GetEntries(); ++entry) {
      if (tree->GetEntry(entry) <= 0) {
        throw std::runtime_error("failed to read raw tree entry");
      }
      if (!std::isfinite(eventWeight)) {
        throw std::runtime_error("non-finite event weight");
      }
      if (!pdg || !heavyIndex || !status || !isFinal || !central || !qc ||
          !qb || !originC || !originB || !resolutionC || !resolutionB ||
          !matchedC || !matchedB || !rejectedC || !rejectedB || !depthC ||
          !depthB || !motherOffsets || !mothers || !pt || !eta) {
        throw std::runtime_error("null raw event vector");
      }
      const std::size_t size = pdg->size();
      const std::array<std::size_t, 17> sizes = {
          heavyIndex->size(), status->size(),     isFinal->size(),
          central->size(),    qc->size(),         qb->size(),
          originC->size(),    originB->size(),    resolutionC->size(),
          resolutionB->size(), matchedC->size(),   matchedB->size(),
          rejectedC->size(),  rejectedB->size(),  depthC->size(),
          depthB->size(),     pt->size()};
      if (std::any_of(sizes.begin(), sizes.end(),
                      [size](std::size_t value) { return value != size; }) ||
          eta->size() != size || motherOffsets->size() != size + 1 ||
          motherOffsets->empty() || motherOffsets->front() != 0 ||
          motherOffsets->back() != static_cast<int>(mothers->size())) {
        throw std::runtime_error("misaligned raw event vectors");
      }

      for (std::size_t index = 0; index < size; ++index) {
        const auto* state = Hadronization::FindGroundState((*pdg)[index]);
        if (!state || !(*central)[index] || !(*isFinal)[index] ||
            !Hadronization::IsDirectPrimaryStatus((*status)[index]) ||
            !Hadronization::IsCentralKinematic((*pt)[index], (*eta)[index],
                                               false)) {
          continue;
        }
        const bool charm = state->sector == "charm";
        const int sectorCharge = charm ? (*qc)[index] : (*qb)[index];
        const int origin = charm ? (*originC)[index] : (*originB)[index];
        if (sectorCharge == 0 ||
            origin !=
                static_cast<int>(Hadronization::Origin::kUnresolved)) {
          continue;
        }
        const bool triggerCandidate =
            IsPublicationTriggerForUnresolvedList((*pdg)[index]) &&
            Hadronization::IsCentralKinematic((*pt)[index], (*eta)[index],
                                              true);
        const std::string sector = charm ? "charm" : "beauty";
        const auto record = [&](const std::string& role) {
          UnresolvedCounts& count = counts[role + ":" + sector];
          ++count.candidates;
          count.sumWeights += eventWeight;
          count.sumWeights2 += eventWeight * eventWeight;
        };
        record("associate");
        if (triggerCandidate) record("trigger_candidate");

        if (rows >= maximumRows) continue;
        const int resolution =
            charm ? (*resolutionC)[index] : (*resolutionB)[index];
        const int matched = charm ? (*matchedC)[index] : (*matchedB)[index];
        const int rejected =
            charm ? (*rejectedC)[index] : (*rejectedB)[index];
        const int depth = charm ? (*depthC)[index] : (*depthB)[index];
        const int begin = (*motherOffsets)[index];
        const int end = (*motherOffsets)[index + 1];
        if (begin < 0 || end < begin ||
            end > static_cast<int>(mothers->size())) {
          throw std::runtime_error("invalid flattened mother offsets");
        }
        std::cout << "UNRESOLVED"
                  << " tune=" << tune << " entry=" << entry
                  << " event_id=" << eventId
                  << " hard_channel=" << hardChannel
                  << " multiplicity=" << multiplicity
                  << " event_weight=" << eventWeight
                  << " heavy_slot=" << index
                  << " event_record_index=" << (*heavyIndex)[index]
                  << " pdg=" << (*pdg)[index]
                  << " status=" << (*status)[index]
                  << " pt=" << (*pt)[index] << " eta=" << (*eta)[index]
                  << " sector=" << sector
                  << " sector_charge=" << sectorCharge
                  << " trigger_candidate=" << (triggerCandidate ? 1 : 0)
                  << " resolution=" << resolution
                  << " matched_hard=" << matched
                  << " rejected_hard=" << rejected
                  << " origin_depth=" << depth << " mothers=";
        for (int offset = begin; offset < end; ++offset) {
          if (offset != begin) std::cout << ",";
          std::cout << (*mothers)[offset];
        }
        std::cout << "\n";
        ++rows;
      }
    }
    tree->ResetBranchAddresses();

    for (const auto& [key, count] : counts) {
      const double effectiveEntries =
          count.sumWeights2 > 0.0
              ? count.sumWeights * count.sumWeights / count.sumWeights2
              : std::numeric_limits<double>::quiet_NaN();
      std::cout << "UNRESOLVED_SUMMARY"
                << " tune=" << tune << " role_sector=" << key
                << " candidates=" << count.candidates
                << " sum_weights=" << count.sumWeights
                << " sum_weights2=" << count.sumWeights2
                << " effective_entries=" << effectiveEntries
                << " effective_entries_defined="
                << (count.sumWeights2 > 0.0 ? 1 : 0) << "\n";
    }
    std::cout << "UNRESOLVED_LIST"
              << " tune=" << tune << " printed_rows=" << rows
              << " maximum_rows=" << maximumRows << "\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "UNRESOLVED_LIST_ERROR " << error.what() << "\n";
    return 1;
  }
}
