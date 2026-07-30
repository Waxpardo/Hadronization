#include <TFile.h>
#include <TTree.h>

#include <nlohmann/json.hpp>

#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <string>

namespace {

std::map<std::string, std::string> ReadEffectiveSettings(
    const char* path, const std::string& expectedTune, int& errors) {
  std::map<std::string, std::string> result;
  TFile file(path, "READ");
  auto* settings = file.Get<TTree>("effective_settings");
  auto* metadata = file.Get<TTree>("job_metadata");
  if (file.IsZombie() || !settings || !metadata) {
    std::cerr << "TUNE_AUDIT_ERROR missing effective settings in " << path
              << "\n";
    ++errors;
    return result;
  }
  std::string* tune = nullptr;
  metadata->SetBranchAddress("tune", &tune);
  metadata->GetEntry(0);
  if (!tune || *tune != expectedTune) {
    std::cerr << "TUNE_AUDIT_ERROR tune metadata mismatch in " << path << "\n";
    ++errors;
  }
  metadata->ResetBranchAddresses();
  std::string* name = nullptr;
  std::string* value = nullptr;
  settings->SetBranchAddress("name", &name);
  settings->SetBranchAddress("value", &value);
  for (Long64_t row = 0; row < settings->GetEntries(); ++row) {
    settings->GetEntry(row);
    if (!name || !value || name->empty() || !result.emplace(*name, *value).second) {
      std::cerr << "TUNE_AUDIT_ERROR invalid/duplicate setting row in " << path
                << "\n";
      ++errors;
    }
  }
  settings->ResetBranchAddresses();
  return result;
}

std::string ValueOrDefault(const std::map<std::string, std::string>& values,
                           const std::string& key) {
  const auto iterator = values.find(key);
  return iterator == values.end() ? "<PYTHIA_DEFAULT>" : iterator->second;
}

}  // namespace

int AuditTuneSettings(const char* monashPath, const char* junctionsPath,
                      const char* closePackingPath,
                      const char* allowlistPath,
                      const char* outputCsv = "effective_tune_differences.csv") {
  int errors = 0;
  const auto monash = ReadEffectiveSettings(monashPath, "MONASH", errors);
  const auto junctions =
      ReadEffectiveSettings(junctionsPath, "JUNCTIONS", errors);
  const auto closePacking =
      ReadEffectiveSettings(closePackingPath, "CLOSEPACKING", errors);
  std::ifstream allowlistStream(allowlistPath);
  nlohmann::json allowlist;
  allowlistStream >> allowlist;
  const std::set<std::string> allowed(
      allowlist["allowed_tune_differences"].begin(),
      allowlist["allowed_tune_differences"].end());
  const std::set<std::string> perJob(
      allowlist["allowed_per_job_differences"].begin(),
      allowlist["allowed_per_job_differences"].end());
  std::set<std::string> keys;
  for (const auto& [key, value] : monash) keys.insert(key);
  for (const auto& [key, value] : junctions) keys.insert(key);
  for (const auto& [key, value] : closePacking) keys.insert(key);

  std::ofstream csv(outputCsv);
  csv << "setting,MONASH,JUNCTIONS,CLOSEPACKING,classification\n";
  int differences = 0;
  for (const auto& key : keys) {
    const std::string m = ValueOrDefault(monash, key);
    const std::string j = ValueOrDefault(junctions, key);
    const std::string c = ValueOrDefault(closePacking, key);
    const bool differs = m != j || m != c;
    std::string classification = "common";
    if (differs) {
      ++differences;
      if (allowed.count(key)) {
        classification = "allowed_tune_difference";
      } else if (perJob.count(key)) {
        classification = "allowed_per_job_difference";
      } else {
        classification = "FORBIDDEN_DIFFERENCE";
        std::cerr << "TUNE_AUDIT_ERROR non-allowlisted post-init difference "
                  << key << " MONASH=" << m << " JUNCTIONS=" << j
                  << " CLOSEPACKING=" << c << "\n";
        ++errors;
      }
    }
    csv << '"' << key << "\",\"" << m << "\",\"" << j << "\",\"" << c
        << "\",\"" << classification << "\"\n";
    if (differs) {
      std::cout << "EFFECTIVE_TUNE_DIFFERENCE setting=" << key
                << " MONASH=" << m << " JUNCTIONS=" << j
                << " CLOSEPACKING=" << c
                << " classification=" << classification << "\n";
    }
  }
  std::cout << "EFFECTIVE_TUNE_AUDIT errors=" << errors
            << " settings=" << keys.size() << " differences=" << differences
            << " csv=" << outputCsv << "\n";
  return errors;
}
