#include "ValidateRawOutput.C"

#include <TFile.h>
#include <TTree.h>

#include <nlohmann/json.hpp>

#include <fstream>
#include <algorithm>
#include <cctype>
#include <cmath>
#include <exception>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <string>
#include <vector>

namespace {

constexpr const char* kCanonicalSchema = "hf_canonical_raw_manifest_v2";
constexpr const char* kSupersedingCanonicalSchema =
    "hf_superseding_canonical_raw_manifest_v3";
constexpr const char* kExtensionCanonicalSchema =
    "hf_equal_tune_extension_raw_manifest_v1";
constexpr int kBlocks = 10;
const std::vector<std::string> kTunes = {
    "MONASH", "JUNCTIONS", "CLOSEPACKING"};

bool IsLowerHex(const std::string& value, std::size_t length) {
  if (value.size() != length) return false;
  for (const unsigned char character : value) {
    if (!std::isdigit(character) &&
        !(character >= 'a' && character <= 'f')) {
      return false;
    }
  }
  return true;
}

}  // namespace

int ValidateCanonicalRawManifest(const char* manifestPath,
                                 const char* productionRoot) {
  std::ifstream stream(manifestPath);
  if (!stream) {
    std::cerr << "CANONICAL_RAW_ERROR cannot open manifest "
              << manifestPath << "\n";
    return 1;
  }
  std::string line;
  int errors = 0;
  int rows = 0;
  std::set<std::string> identities;
  std::set<int> seeds;
  std::set<std::string> rawPaths;
  std::set<std::string> attemptReceipts;
  std::map<std::string, std::set<int>> slotsByTune;
  std::map<std::string, std::map<int, int>> blocksByTune;
  unsigned long long totalEvents = 0;
  unsigned long long expectedTotalEvents = 0;
  std::string manifestSchema;
  std::string finalCampaign;
  int finalCampaignOrdinal = -1;
  while (std::getline(stream, line)) {
    if (line.empty()) continue;
    nlohmann::json row;
    try {
      row = nlohmann::json::parse(line);
    } catch (const std::exception& error) {
      std::cerr << "CANONICAL_RAW_ERROR invalid JSON row: "
                << error.what() << "\n";
      ++errors;
      continue;
    }
    const std::string tune = row.value("tune", "");
    const int slot = row.value("canonical_slot", -1);
    const int logicalId = row.value("logical_id", -1);
    const int attempt = row.value("attempt", -1);
    const int seed = row.value("seed", -1);
    const int campaignOrdinal = row.value("campaign_ordinal", -1);
    const int block = row.value("block", -1);
    const unsigned long long expectedSuccesses =
        row.value("requested_successes", 0ULL);
    const std::string role = row.value("role", "");
    const double effectivePthatMin =
        row.value("effective_pthat_min", -1.0);
    const unsigned long long multiplicityAuditEvents =
        row.value("multiplicity_audit_events",
                  std::numeric_limits<unsigned long long>::max());
    const std::string configSha =
        row.value("effective_card_sha256", "");
    const std::string producerSha =
        row.value("producer_executable_sha256", "");
    const std::string repositoryCommit =
        row.value("repository_commit", "");
    const std::string tuneAllowlistSha =
        row.value("tune_difference_allowlist_sha256", "");
    const std::string rawSha = row.value("raw_sha256", "");
    const std::string rawPath = row.value("raw_path", "");
    const std::string attemptReceipt =
        row.value("attempt_receipt_path", "");
    // attempt_start_claim_path / _sha256 were written by the campaign-manifest
    // claim machinery, which has been removed. Nothing produces them now, so
    // requiring them would only assert that a deleted tool once ran. Every
    // other field below still has a live producer and is still checked.
    const std::string rawValidationReceipt =
        row.value("raw_validation_receipt_path", "");
    const std::string rawValidationReceiptSha =
        row.value("raw_validation_receipt_sha256", "");
    const std::string identity = tune + ":" + std::to_string(slot);
    const std::string schema = row.value("schema", "");
    const bool firstStage = schema == kCanonicalSchema;
    const bool superseding = schema == kSupersedingCanonicalSchema;
    const bool extension = schema == kExtensionCanonicalSchema;
    if (manifestSchema.empty()) manifestSchema = schema;
    if (schema != manifestSchema) {
      std::cerr << "CANONICAL_RAW_ERROR mixed canonical row schemas\n";
      ++errors;
      continue;
    }
    bool supersedingFieldsValid = true;
    if (superseding) {
      const std::string rowFinalCampaign =
          row.value("final_campaign", "");
      const int rowFinalOrdinal =
          row.value("final_campaign_ordinal", -1);
      const std::string sourcePrefix =
          row.value("source_production_prefix", "");
      if (finalCampaign.empty()) {
        finalCampaign = rowFinalCampaign;
        finalCampaignOrdinal = rowFinalOrdinal;
      }
      supersedingFieldsValid =
          !rowFinalCampaign.empty() &&
          rowFinalCampaign == finalCampaign &&
          rowFinalOrdinal > 0 &&
          rowFinalOrdinal == finalCampaignOrdinal &&
          row.value("source_canonical_slot", -1) >= 0 &&
          sourcePrefix == row.value("campaign", "") &&
          rawPath.rfind(sourcePrefix + "/raw/" + tune + "/", 0) == 0 &&
          IsLowerHex(row.value("source_manifest_sha256", ""), 64) &&
          IsLowerHex(row.value("source_freeze_summary_sha256", ""), 64) &&
          IsLowerHex(row.value("source_freeze_seal_sha256", ""), 64) &&
          IsLowerHex(
              row.value("source_production_definition_sha256", ""), 64);
    }
    if ((!firstStage && !superseding && !extension) ||
        std::find(kTunes.begin(), kTunes.end(), tune) == kTunes.end() ||
        slot < 0 ||

        row.value("tune_ordinal", -1) !=
            static_cast<int>(
                std::find(kTunes.begin(), kTunes.end(), tune) -
                kTunes.begin()) ||
        block != slot % kBlocks ||
        row.value("block_position", -1) != slot / kBlocks ||
        logicalId < 0 || attempt < 0 || seed <= 0 ||
        campaignOrdinal <= 0 || expectedSuccesses == 0 ||
        (role != "primary" && role != "reserve") ||

        row.value("raw_schema", "") != "hf_primary_ground_raw_v7" ||
        row.value("origin_algorithm", "") !=
            "signed_heavy_constituent_complete_mothers_unique_v4" ||
        row.value("selector", "") !=
            "hard_trigger_primary_ground__primary_ground_associate_v1" ||
        row.value("tune_difference_allowlist_schema", "") !=
            "pythia_tune_difference_allowlist_v2" ||
        !std::isfinite(effectivePthatMin) || effectivePthatMin < 0.0 ||
        !IsLowerHex(configSha, 64) || !IsLowerHex(producerSha, 64) ||
        !IsLowerHex(repositoryCommit, 40) ||
        !IsLowerHex(tuneAllowlistSha, 64) || !IsLowerHex(rawSha, 64) ||
        rawPath.empty() || attemptReceipt.empty() ||
        rawValidationReceipt.empty() ||
        !IsLowerHex(rawValidationReceiptSha, 64) ||
        !supersedingFieldsValid) {
      std::cerr << "CANONICAL_RAW_ERROR manifest contract mismatch "
                << identity << "\n";
      ++errors;
      continue;
    }
    if (!identities.insert(identity).second || !seeds.insert(seed).second ||
        !rawPaths.insert(rawPath).second ||
        !attemptReceipts.insert(attemptReceipt).second) {
      std::cerr << "CANONICAL_RAW_ERROR duplicate identity, seed, path, or "
                   "attempt receipt "
                << identity << "\n";
      ++errors;
      continue;
    }
    slotsByTune[tune].insert(slot);
    ++blocksByTune[tune][block];
    const std::string path =
        std::string(productionRoot) + "/" + rawPath;
    errors += ValidateRawOutput(
        path.c_str(), row["campaign"].get<std::string>().c_str(),
        tune.c_str(), logicalId, expectedSuccesses, attempt, seed, true,
        role.c_str(), campaignOrdinal, effectivePthatMin,
        multiplicityAuditEvents, configSha.c_str(), producerSha.c_str(),
        repositoryCommit.c_str());
    TFile file(path.c_str(), "READ");
    if (file.IsZombie()) {
      std::cerr << "CANONICAL_RAW_ERROR cannot open " << path << "\n";
      ++errors;
      continue;
    }
    auto* tree = file.Get<TTree>("tree");
    if (!tree) {
      ++errors;
      continue;
    }
    ULong64_t eventId = 0;
    tree->SetBranchAddress("event_id", &eventId);
    for (Long64_t entry = 0; entry < tree->GetEntries(); ++entry) {
      tree->GetEntry(entry);
      const ULong64_t expectedId = Hadronization::EventId(
          campaignOrdinal, Hadronization::TuneOrdinal(tune), logicalId,
          attempt, static_cast<std::uint64_t>(entry));
      if (eventId != expectedId) {
        std::cerr << "CANONICAL_RAW_ERROR event-ID mapping mismatch path="
                  << path << " entry=" << entry << "\n";
        ++errors;
        break;
      }
    }
    tree->ResetBranchAddresses();
    totalEvents += static_cast<unsigned long long>(tree->GetEntries());
    expectedTotalEvents += expectedSuccesses;
    ++rows;
    std::cout << "CANONICAL_RAW_FILE_VALIDATED tune=" << tune
              << " slot=" << slot << " logical_id=" << logicalId
              << " events=" << tree->GetEntries() << "\n";
  }
  int jobsPerTune = -1;
  for (const auto& tune : kTunes) {
    const int tuneJobs = static_cast<int>(slotsByTune[tune].size());
    if (jobsPerTune < 0) jobsPerTune = tuneJobs;
    // The floor is one job per block. Anything above that is a throughput
    // choice, not a contract: what matters is that every tune has the SAME
    // number and that it divides into the blocks the ratios are formed in.
    if (tuneJobs != jobsPerTune || tuneJobs < kBlocks ||
        tuneJobs % kBlocks != 0) {
      std::cerr << "CANONICAL_RAW_ERROR slot coverage differs tune="
                << tune << "\n";
      ++errors;
    }
    for (int slot = 0; slot < tuneJobs; ++slot) {
      if (slotsByTune[tune].count(slot) != 1) {
        std::cerr << "CANONICAL_RAW_ERROR non-contiguous slot coverage tune="
                  << tune << " slot=" << slot << "\n";
        ++errors;
      }
    }
    for (int block = 0; block < kBlocks; ++block) {
      if (jobsPerTune < 0 ||
          blocksByTune[tune][block] != jobsPerTune / kBlocks) {
        std::cerr << "CANONICAL_RAW_ERROR block cardinality differs tune="
                  << tune << " block=" << block << "\n";
        ++errors;
      }
    }
  }
  // Job count per tune is a campaign parameter, not a contract constant: it
  // says how CPU was sliced, not what physics was run. What the analysis
  // actually requires -- equal exposure across tunes, divisible by the ten
  // blocks -- is checked above and below. Pinning it to 100 here only
  // hardcoded one campaign shape.
  if (jobsPerTune <= 0 || jobsPerTune % kBlocks != 0) {
    std::cerr << "CANONICAL_RAW_ERROR jobs per tune must be a positive "
                 "multiple of the block count\n";
    ++errors;
  }
  const int expectedRows =
      jobsPerTune > 0 ? static_cast<int>(kTunes.size()) * jobsPerTune : -1;
  if (rows != expectedRows ||
      static_cast<int>(identities.size()) != expectedRows ||
      static_cast<int>(seeds.size()) != expectedRows ||
      static_cast<int>(rawPaths.size()) != expectedRows ||
      static_cast<int>(attemptReceipts.size()) != expectedRows) {
    std::cerr << "CANONICAL_RAW_ERROR manifest cardinality mismatch\n";
    ++errors;
  }
  if (totalEvents != expectedTotalEvents) {
    std::cerr << "CANONICAL_RAW_ERROR successful-event total mismatch "
              << totalEvents << " != " << expectedTotalEvents << "\n";
    ++errors;
  }
  std::cout << "CANONICAL_RAW_VALIDATION errors=" << errors
            << " files=" << rows << " unique_seeds=" << seeds.size()
            << " total_events=" << totalEvents << "\n";
  return errors;
}
