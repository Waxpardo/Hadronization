#include "../AnalysisScripts/status_analysis_THnSparse_qq.C"

#include "TFile.h"
#include "TSystem.h"
#include "TTree.h"

#include <limits>
#include <string>
#include <vector>

namespace {

enum class Mutation {
  kNone,
  kIncomplete,
  kRequestedMismatch,
  kAttemptIdentityMismatch,
  kContentDecodeFailure,
  kConservationFailure,
  kClassificationFailure,
  kPrimaryMatchFailure,
  kMultiplicityOverflow,
  kStrongEmMultiplicityOverflow,
  kNonFiniteWeight,
  kWrongWeightType,
  kWrongVectorType,
};

void WriteFixture(const std::string& path, Mutation mutation) {
  TFile output(path.c_str(), "RECREATE");

  std::string campaign = "RAW_CONTRACT_TEST";
  std::string tune = "MONASH";
  std::string rawSchema = "hf_primary_ground_raw_v6";
  std::string selector(Hadronization::kSelectorVersion);
  std::string originAlgorithm =
      "signed_heavy_constituent_complete_mothers_unique_v4";
  std::string speciesSha(Hadronization::kSpeciesRegistrySha256);
  std::string tuneAllowlistSchema(
      Hadronization::kTuneDifferenceAllowlistSchema);
  std::string tuneAllowlistSha(
      Hadronization::kTuneDifferenceAllowlistSha256);
  std::string stabilitySchema(Hadronization::kHeavyStabilityAuditSchema);
  std::string stabilitySha(64, 'a');
  std::string settingsSchema =
      "effective_pythia_settings_exhaustive_v2";
  std::string settingsSha(64, 'b');
  std::string repositoryCommit(40, 'c');
  std::string repositoryDirty = "false";
  std::string executableSha(64, 'd');
  Int_t logicalId = 0;
  Int_t complete = mutation == Mutation::kIncomplete ? 0 : 1;
  ULong64_t requested =
      mutation == Mutation::kRequestedMismatch ? 2 : 1;
  ULong64_t attempts =
      mutation == Mutation::kAttemptIdentityMismatch ? 2 : 1;
  ULong64_t successes = 1;
  ULong64_t failures = 0;
  ULong64_t entries = 1;
  ULong64_t decodeFailures =
      mutation == Mutation::kContentDecodeFailure ? 1 : 0;
  ULong64_t conservationFailures =
      mutation == Mutation::kConservationFailure ? 1 : 0;
  ULong64_t classificationFailures =
      mutation == Mutation::kClassificationFailure ? 1 : 0;
  ULong64_t primaryFailures =
      mutation == Mutation::kPrimaryMatchFailure ? 1 : 0;
  ULong64_t multiplicityOverflow =
      mutation == Mutation::kMultiplicityOverflow ? 1 : 0;
  ULong64_t strongEmMultiplicityOverflow =
      mutation == Mutation::kStrongEmMultiplicityOverflow ? 1 : 0;
  Double_t sumWeights = 1.0;
  Double_t sumWeights2 = 1.0;

  TTree metadata("job_metadata", "raw fixture metadata");
  metadata.Branch("campaign", &campaign);
  metadata.Branch("tune", &tune);
  metadata.Branch("raw_schema", &rawSchema);
  metadata.Branch("selector", &selector);
  metadata.Branch("origin_algorithm", &originAlgorithm);
  metadata.Branch("species_registry_sha256", &speciesSha);
  metadata.Branch("tune_difference_allowlist_schema",
                  &tuneAllowlistSchema);
  metadata.Branch("tune_difference_allowlist_sha256",
                  &tuneAllowlistSha);
  metadata.Branch("heavy_stability_audit_schema", &stabilitySchema);
  metadata.Branch("heavy_stability_audit_sha256", &stabilitySha);
  metadata.Branch("effective_settings_schema", &settingsSchema);
  metadata.Branch("effective_settings_sha256", &settingsSha);
  metadata.Branch("repository_commit", &repositoryCommit);
  metadata.Branch("repository_dirty", &repositoryDirty);
  metadata.Branch("executable_sha256", &executableSha);
  metadata.Branch("logical_id", &logicalId, "logical_id/I");
  metadata.Branch("complete", &complete, "complete/I");
  metadata.Branch("requested_successes", &requested,
                  "requested_successes/l");
  metadata.Branch("attempts", &attempts, "attempts/l");
  metadata.Branch("successful_events", &successes,
                  "successful_events/l");
  metadata.Branch("failed_attempts", &failures, "failed_attempts/l");
  metadata.Branch("tree_entries", &entries, "tree_entries/l");
  metadata.Branch("content_decode_failures", &decodeFailures,
                  "content_decode_failures/l");
  metadata.Branch("heavy_flavour_conservation_failures",
                  &conservationFailures,
                  "heavy_flavour_conservation_failures/l");
  metadata.Branch("origin_classification_failures",
                  &classificationFailures,
                  "origin_classification_failures/l");
  metadata.Branch("primary_all_heavy_match_failures",
                  &primaryFailures,
                  "primary_all_heavy_match_failures/l");
  metadata.Branch("multiplicity_overflow", &multiplicityOverflow,
                  "multiplicity_overflow/l");
  metadata.Branch("multiplicity_wide_overflow",
                  &strongEmMultiplicityOverflow,
                  "multiplicity_wide_overflow/l");
  metadata.Branch("sum_weights", &sumWeights, "sum_weights/D");
  metadata.Branch("sum_weights2", &sumWeights2, "sum_weights2/D");
  metadata.Fill();
  metadata.Write();

  ULong64_t eventId = 1;
  Double_t eventWeight =
      mutation == Mutation::kNonFiniteWeight
          ? std::numeric_limits<double>::quiet_NaN()
          : 1.0;
  Float_t wrongWeight = 1.0F;
  Int_t multiplicity = 0;
  Int_t conservationValid = 1;
  Int_t classificationValid = 1;
  Int_t primaryValid = 1;
  std::vector<int> integers;
  std::vector<double> doubles;
  std::vector<float> wrongDoubles;
  TTree tree("tree", "raw fixture tree");
  tree.Branch("event_id", &eventId, "event_id/l");
  if (mutation == Mutation::kWrongWeightType) {
    tree.Branch("event_weight", &wrongWeight, "event_weight/F");
  } else {
    tree.Branch("event_weight", &eventWeight, "event_weight/D");
  }
  tree.Branch("multiplicity_primary_charged_eta10_v1", &multiplicity,
              "multiplicity_primary_charged_eta10_v1/I");
  tree.Branch("heavy_flavour_conservation_ok", &conservationValid,
              "heavy_flavour_conservation_ok/I");
  tree.Branch("origin_classification_valid", &classificationValid,
              "origin_classification_valid/I");
  tree.Branch("primary_all_heavy_match_valid", &primaryValid,
              "primary_all_heavy_match_valid/I");
  for (const char* name : {
           "heavyIndex", "heavyPdg", "heavyStatus", "heavyIsFinal",
           "heavyCentral", "heavyQc", "heavyQb", "heavyOriginC",
           "heavyOriginB", "heavyMatchResolutionC",
           "heavyMatchResolutionB", "heavyMatchedHardC",
           "heavyMatchedHardB", "heavyRejectedHardC",
           "heavyRejectedHardB"}) {
    tree.Branch(name, &integers);
  }
  if (mutation == Mutation::kWrongVectorType) {
    tree.Branch("heavyPt", &wrongDoubles);
  } else {
    tree.Branch("heavyPt", &doubles);
  }
  tree.Branch("heavyEta", &doubles);
  tree.Branch("heavyPhi", &doubles);
  tree.Fill();
  tree.Write();
  output.Close();
}

}  // namespace

int TestAnalysisRawInputContract() {
  const std::string directory =
      std::string(gSystem->TempDirectory()) +
      "/hadronization_analysis_raw_contract_" +
      std::to_string(gSystem->GetPid());
  if (gSystem->mkdir(directory.c_str(), true) != 0) {
    return 1;
  }
  int failures = 0;
  const auto check = [&](const char* name, Mutation mutation,
                         bool expectedPass) {
    const std::string path = directory + "/" + name + ".root";
    WriteFixture(path, mutation);
    const bool passed = ValidateStatusAnalysisRawInput(path.c_str()) == 0;
    if (passed != expectedPass) {
      ++failures;
      std::cerr << "ANALYSIS_RAW_CONTRACT_TEST_ERROR case=" << name
                << " expected_pass=" << expectedPass
                << " observed_pass=" << passed << "\n";
    }
    gSystem->Unlink(path.c_str());
  };

  check("valid", Mutation::kNone, true);
  check("incomplete", Mutation::kIncomplete, false);
  check("requested_mismatch", Mutation::kRequestedMismatch, false);
  check("attempt_identity", Mutation::kAttemptIdentityMismatch, false);
  check("decode_failure", Mutation::kContentDecodeFailure, false);
  check("conservation_failure", Mutation::kConservationFailure, false);
  check("classification_failure", Mutation::kClassificationFailure, false);
  check("primary_match_failure", Mutation::kPrimaryMatchFailure, false);
  check("multiplicity_overflow", Mutation::kMultiplicityOverflow, false);
  check("strong_em_overflow", Mutation::kStrongEmMultiplicityOverflow,
        false);
  check("nonfinite_weight", Mutation::kNonFiniteWeight, false);
  check("wrong_weight_type", Mutation::kWrongWeightType, false);
  check("wrong_vector_type", Mutation::kWrongVectorType, false);
  gSystem->Unlink(directory.c_str());
  std::cout << "ANALYSIS_RAW_CONTRACT_TEST_SUMMARY failures="
            << failures << "\n";
  return failures;
}
