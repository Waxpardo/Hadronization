#include "ValidateRawOutput.C"

#include <TFile.h>
#include <TTree.h>

#include <nlohmann/json.hpp>

#include <fstream>
#include <iostream>
#include <set>
#include <string>

int ValidateCanonicalRawManifest(const char* manifestPath,
                                 const char* productionRoot) {
  std::ifstream stream(manifestPath);
  std::string line;
  int errors = 0;
  int rows = 0;
  std::set<std::string> identities;
  std::set<int> seeds;
  unsigned long long totalEvents = 0;
  while (std::getline(stream, line)) {
    if (line.empty()) continue;
    const nlohmann::json row = nlohmann::json::parse(line);
    const std::string tune = row["tune"];
    const int slot = row["canonical_slot"];
    const int logicalId = row["logical_id"];
    const int attempt = row["attempt"];
    const int seed = row["seed"];
    const int campaignOrdinal = row["campaign_ordinal"];
    const unsigned long long expectedSuccesses =
        row["requested_successes"];
    const std::string identity = tune + ":" + std::to_string(slot);
    if (!identities.insert(identity).second || !seeds.insert(seed).second) {
      std::cerr << "CANONICAL_RAW_ERROR duplicate identity or seed "
                << identity << "\n";
      ++errors;
      continue;
    }
    const std::string path =
        std::string(productionRoot) + "/" +
        row["raw_path"].get<std::string>();
    errors += ValidateRawOutput(
        path.c_str(), row["campaign"].get<std::string>().c_str(),
        tune.c_str(), logicalId, expectedSuccesses, attempt, seed, true);
    TFile file(path.c_str(), "READ");
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
    ++rows;
    std::cout << "CANONICAL_RAW_FILE_VALIDATED tune=" << tune
              << " slot=" << slot << " logical_id=" << logicalId
              << " events=" << tree->GetEntries() << "\n";
  }
  if (rows != 300 || identities.size() != 300 || seeds.size() != 300) {
    std::cerr << "CANONICAL_RAW_ERROR manifest cardinality mismatch\n";
    ++errors;
  }
  std::cout << "CANONICAL_RAW_VALIDATION errors=" << errors
            << " files=" << rows << " unique_seeds=" << seeds.size()
            << " total_events=" << totalEvents << "\n";
  return errors;
}
