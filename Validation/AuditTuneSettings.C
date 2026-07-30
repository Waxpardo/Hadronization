#include "../SimulationScripts/GeneratedTuneSettingRegistry.h"
#include "../SimulationScripts/HeavyFlavourUtils.h"
#include "../SimulationScripts/Sha256.h"

#include <TFile.h>
#include <TTree.h>

#include <nlohmann/json.hpp>

#include <algorithm>
#include <cctype>
#include <cmath>
#include <exception>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>

namespace {

struct InputSettings {
  std::map<std::string, std::string> values;
  unsigned long long requestedSuccesses = 0;
  unsigned long long effectiveSettingsEntries = 0;
  double pthatMin = -1.0;
};

std::string Lower(std::string value) {
  std::transform(value.begin(), value.end(), value.begin(),
                 [](unsigned char character) {
                   return static_cast<char>(std::tolower(character));
                 });
  return value;
}

bool DeclaredValueMatches(const std::string& actual,
                          const std::string& declared) {
  const std::string actualLower = Lower(actual);
  const std::string declaredLower = Lower(declared);
  const auto normalizeBoolean = [](const std::string& value) {
    if (value == "on" || value == "true") return std::string("true");
    if (value == "off" || value == "false") return std::string("false");
    return value;
  };
  if (normalizeBoolean(actualLower) == normalizeBoolean(declaredLower)) {
    return true;
  }
  std::size_t actualConsumed = 0;
  std::size_t declaredConsumed = 0;
  try {
    const double actualNumber =
        std::stod(actual, &actualConsumed);
    const double declaredNumber =
        std::stod(declared, &declaredConsumed);
    return actualConsumed == actual.size() &&
           declaredConsumed == declared.size() &&
           std::isfinite(actualNumber) &&
           std::isfinite(declaredNumber) &&
           std::abs(actualNumber - declaredNumber) <=
               1e-13 *
                   std::max({1.0, std::abs(actualNumber),
                             std::abs(declaredNumber)});
  } catch (const std::exception&) {
    return false;
  }
}

InputSettings ReadEffectiveSettings(
    const char* path, const std::string& expectedTune, int& errors) {
  InputSettings result;
  TFile file(path, "READ");
  auto* settings = file.Get<TTree>("effective_settings");
  auto* metadata = file.Get<TTree>("job_metadata");
  if (file.IsZombie() || !settings || !metadata) {
    std::cerr << "TUNE_AUDIT_ERROR missing effective settings in " << path
              << "\n";
    ++errors;
    return result;
  }
  if (metadata->GetEntries() != 1) {
    std::cerr << "TUNE_AUDIT_ERROR metadata cardinality differs in " << path
              << "\n";
    ++errors;
    return result;
  }
  std::string* tune = nullptr;
  std::string* rawSchema = nullptr;
  std::string* selector = nullptr;
  std::string* originAlgorithm = nullptr;
  std::string* allowlistSchema = nullptr;
  std::string* allowlistSha = nullptr;
  std::string* effectiveSettingsSchema = nullptr;
  metadata->SetBranchAddress("tune", &tune);
  metadata->SetBranchAddress("raw_schema", &rawSchema);
  metadata->SetBranchAddress("selector", &selector);
  metadata->SetBranchAddress("origin_algorithm", &originAlgorithm);
  metadata->SetBranchAddress("tune_difference_allowlist_schema",
                             &allowlistSchema);
  metadata->SetBranchAddress("tune_difference_allowlist_sha256",
                             &allowlistSha);
  metadata->SetBranchAddress("effective_settings_schema",
                             &effectiveSettingsSchema);
  metadata->SetBranchAddress("requested_successes",
                             &result.requestedSuccesses);
  metadata->SetBranchAddress("effective_settings_entries",
                             &result.effectiveSettingsEntries);
  metadata->SetBranchAddress("phase_space_pthat_min", &result.pthatMin);
  metadata->GetEntry(0);
  if (!tune || *tune != expectedTune || !rawSchema ||
      *rawSchema != Hadronization::kRawSchema || !selector ||
      *selector != Hadronization::kSelectorVersion || !originAlgorithm ||
      *originAlgorithm != Hadronization::kOriginAlgorithmVersion ||
      !allowlistSchema ||
      *allowlistSchema !=
          Hadronization::kTuneDifferenceAllowlistSchema ||
      !allowlistSha ||
      *allowlistSha != Hadronization::kTuneDifferenceAllowlistSha256 ||
      !effectiveSettingsSchema ||
      *effectiveSettingsSchema != Hadronization::kEffectiveSettingsSchema ||
      result.requestedSuccesses == 0 || !std::isfinite(result.pthatMin) ||
      result.pthatMin < 0.0 ||
      result.effectiveSettingsEntries !=
          static_cast<unsigned long long>(settings->GetEntries())) {
    std::cerr << "TUNE_AUDIT_ERROR provenance metadata mismatch in " << path
              << "\n";
    ++errors;
  }
  metadata->ResetBranchAddresses();
  std::string* name = nullptr;
  std::string* value = nullptr;
  settings->SetBranchAddress("name", &name);
  settings->SetBranchAddress("value", &value);
  for (Long64_t row = 0; row < settings->GetEntries(); ++row) {
    settings->GetEntry(row);
    if (!name || !value || name->empty() ||
        !result.values.emplace(*name, *value).second) {
      std::cerr << "TUNE_AUDIT_ERROR invalid/duplicate setting row in " << path
                << "\n";
      ++errors;
    }
  }
  settings->ResetBranchAddresses();
  std::set<std::string> expectedKeys;
  for (const std::string_view key :
       Hadronization::kAuditedPythiaSettingKeys) {
    expectedKeys.emplace(key);
  }
  std::set<std::string> actualKeys;
  for (const auto& [key, value] : result.values) {
    (void)value;
    actualKeys.insert(key);
  }
  if (!std::includes(actualKeys.begin(), actualKeys.end(),
                     expectedKeys.begin(), expectedKeys.end()) ||
      actualKeys.size() <= expectedKeys.size()) {
    std::cerr << "TUNE_AUDIT_ERROR exhaustive effective-setting key set "
                 "omits the generated subset in "
              << path << "\n";
    ++errors;
  }
  return result;
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
  if (!allowlistStream) {
    std::cerr << "TUNE_AUDIT_ERROR cannot read allowlist\n";
    return errors + 1;
  }
  std::ostringstream allowlistBytes;
  allowlistBytes << allowlistStream.rdbuf();
  if (Hadronization::Sha256Hex(allowlistBytes.str()) !=
      Hadronization::kTuneDifferenceAllowlistSha256) {
    std::cerr << "TUNE_AUDIT_ERROR allowlist checksum differs from build\n";
    ++errors;
  }
  nlohmann::json allowlist;
  allowlist = nlohmann::json::parse(allowlistBytes.str());
  if (allowlist.value("schema", std::string()) !=
      Hadronization::kTuneDifferenceAllowlistSchema) {
    std::cerr << "TUNE_AUDIT_ERROR allowlist schema differs from build\n";
    ++errors;
  }
  const std::set<std::string> allowed(
      allowlist["allowed_tune_differences"].begin(),
      allowlist["allowed_tune_differences"].end());
  const std::set<std::string> perJob(
      allowlist["allowed_per_job_differences"].begin(),
      allowlist["allowed_per_job_differences"].end());
  std::set<std::string> keys;
  for (const auto& [key, value] : monash.values) {
    (void)value;
    keys.insert(key);
  }
  const auto exactKeys = [](const InputSettings& settings) {
    std::set<std::string> result;
    for (const auto& [key, value] : settings.values) {
      (void)value;
      result.insert(key);
    }
    return result;
  };
  if (keys != exactKeys(junctions) || keys != exactKeys(closePacking) ||
      keys.empty()) {
    std::cerr << "TUNE_AUDIT_ERROR exhaustive post-init setting catalogs "
                 "differ across tunes\n";
    ++errors;
  }
  const auto approximatelyEqual = [](double left, double right) {
    return std::abs(left - right) <=
           1e-12 * std::max({1.0, std::abs(left), std::abs(right)});
  };
  if (monash.requestedSuccesses != junctions.requestedSuccesses ||
      monash.requestedSuccesses != closePacking.requestedSuccesses ||
      !approximatelyEqual(monash.pthatMin, junctions.pthatMin) ||
      !approximatelyEqual(monash.pthatMin, closePacking.pthatMin)) {
    std::cerr << "TUNE_AUDIT_ERROR compared jobs do not have aligned event "
                 "targets and pTHat thresholds\n";
    ++errors;
  }
  for (const auto& required :
       Hadronization::kCommonRequiredCardValues) {
    const std::string key(required.name);
    const std::string declared(required.value);
    if (allowed.count(key) != 0U) {
      std::cerr << "TUNE_AUDIT_ERROR common-required setting is also "
                   "allowlisted as a tune difference: "
                << key << "\n";
      ++errors;
      continue;
    }
    for (const auto* input : {&monash, &junctions, &closePacking}) {
      const auto found = input->values.find(key);
      if (found == input->values.end() ||
          !DeclaredValueMatches(found->second, declared)) {
        std::cerr << "TUNE_AUDIT_ERROR common-required post-init value "
                  << key << " differs from declared " << declared << "\n";
        ++errors;
      }
    }
  }

  std::ofstream csv(outputCsv);
  csv << "setting,MONASH,JUNCTIONS,CLOSEPACKING,classification\n";
  int differences = 0;
  for (const auto& key : keys) {
    const auto mIt = monash.values.find(key);
    const auto jIt = junctions.values.find(key);
    const auto cIt = closePacking.values.find(key);
    if (mIt == monash.values.end() || jIt == junctions.values.end() ||
        cIt == closePacking.values.end()) {
      std::cerr << "TUNE_AUDIT_ERROR missing exact post-init value for "
                << key << "\n";
      ++errors;
      continue;
    }
    const std::string& m = mIt->second;
    const std::string& j = jIt->second;
    const std::string& c = cIt->second;
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
