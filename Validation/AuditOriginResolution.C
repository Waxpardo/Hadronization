#include "../SimulationScripts/GeneratedHeavyFlavourRegistry.h"
#include "../SimulationScripts/HeavyFlavourUtils.h"
#include "../SimulationScripts/Sha256.h"
#include "../AnalysisScripts/GeneratedPairRegistry.h"

#include <TAxis.h>
#include <TFile.h>
#include <THnSparse.h>
#include <TObjString.h>
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
#include <memory>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace {

constexpr const char* kAuditSchema = "origin_resolution_audit_v3";
constexpr const char* kClosureSchema = "primary_all_heavy_closure_v1";

enum class AuditRole : int {
  kAssociate = 0,
  kTriggerCandidate = 1,
};

struct Contract {
  std::string rawSchema;
  std::string selector;
  std::string originAlgorithm;
  std::string speciesRegistrySchema;
  std::string speciesRegistrySha256;
  std::string tune;
  std::string campaign;
  std::string role;
  std::string repositoryCommit;
  std::string configSha256;
  std::string executableSha256;
  std::string condorCluster;
  std::string condorProcess;
  int campaignOrdinal = 0;
  int logicalId = 0;
  int attempt = 0;
  int seed = 0;
  ULong64_t requestedSuccesses = 0;
  ULong64_t multiplicityAuditEvents = 0;
  double phaseSpacePthatMin = 0.0;
};

struct Count {
  ULong64_t candidates = 0;
  double sumWeights = 0.0;
  double sumWeights2 = 0.0;
};

using Key = std::tuple<int, int, int, int, int>;
// role, hard channel, signed PDG, origin, resolution

enum class ClosureCategory : int {
  kCentralGroundAssociate = 0,
  kCentralGroundOutsideAssociate = 1,
  kExcludedVector = 2,
  kExcludedExcited = 3,
  kHiddenHeavy = 4,
  kMultiplyHeavy = 5,
  kOtherNoncentral = 6,
  kUnresolvedCompanion = 7
};

using ClosureBaseKey = std::tuple<int, int, int>;
// hard channel, exact hadronisation Nch, signed trigger PDG
using ClosureKey = std::tuple<int, int, int, int>;

const char* ClosureCategoryName(int category) {
  switch (static_cast<ClosureCategory>(category)) {
    case ClosureCategory::kCentralGroundAssociate:
      return "central_ground_associate";
    case ClosureCategory::kCentralGroundOutsideAssociate:
      return "central_ground_outside_associate_acceptance";
    case ClosureCategory::kExcludedVector:
      return "excluded_vector";
    case ClosureCategory::kExcludedExcited:
      return "excluded_excited";
    case ClosureCategory::kHiddenHeavy:
      return "hidden_heavy";
    case ClosureCategory::kMultiplyHeavy:
      return "multiply_heavy";
    case ClosureCategory::kOtherNoncentral:
      return "other_noncentral";
    case ClosureCategory::kUnresolvedCompanion:
      return "unresolved_companion";
  }
  return "invalid";
}

bool IsPublicationTrigger(int pdg) {
  return std::any_of(
      Hadronization::kPairDefinitions.begin(),
      Hadronization::kPairDefinitions.end(),
      [pdg](const Hadronization::PairDefinition& pair) {
        return pair.triggerPdg == pdg;
      });
}

int SpeciesIndex(int pdg) {
  for (std::size_t index = 0;
       index < Hadronization::kGroundStates.size(); ++index) {
    if (Hadronization::kGroundStates[index].pdg == pdg) {
      return static_cast<int>(index);
    }
  }
  return -1;
}

const char* RoleName(int role) {
  switch (static_cast<AuditRole>(role)) {
    case AuditRole::kAssociate:
      return "associate";
    case AuditRole::kTriggerCandidate:
      return "trigger_candidate";
  }
  return "invalid";
}

const char* OriginName(int origin) {
  switch (static_cast<Hadronization::Origin>(origin)) {
    case Hadronization::Origin::kUnresolved:
      return "unresolved";
    case Hadronization::Origin::kSelectedHard:
      return "selected_hard";
    case Hadronization::Origin::kShower:
      return "shower";
    case Hadronization::Origin::kMPI:
      return "MPI";
    case Hadronization::Origin::kOtherResolved:
      return "other_resolved";
  }
  return "invalid";
}

const char* ResolutionName(int resolution) {
  switch (static_cast<Hadronization::MatchResolution>(resolution)) {
    case Hadronization::MatchResolution::kNotApplicable:
      return "not_applicable";
    case Hadronization::MatchResolution::kUnique:
      return "unique";
    case Hadronization::MatchResolution::kAmbiguous:
      return "ambiguous";
    case Hadronization::MatchResolution::kMissingCarrier:
      return "missing_carrier";
    case Hadronization::MatchResolution::kBrokenLineage:
      return "broken_lineage";
    case Hadronization::MatchResolution::kDuplicateHardCarrier:
      return "duplicate_hard_carrier";
    case Hadronization::MatchResolution::kMultipleHeavyConstituents:
      return "multiple_heavy_constituents";
  }
  return "invalid";
}

bool ValidOriginResolution(int origin, int resolution) {
  const int unresolved =
      static_cast<int>(Hadronization::Origin::kUnresolved);
  const int unique =
      static_cast<int>(Hadronization::MatchResolution::kUnique);
  if (origin < unresolved ||
      origin > static_cast<int>(Hadronization::Origin::kOtherResolved) ||
      resolution <
          static_cast<int>(Hadronization::MatchResolution::kNotApplicable) ||
      resolution > static_cast<int>(
                       Hadronization::MatchResolution::
                           kMultipleHeavyConstituents)) {
    return false;
  }
  // Every resolved origin has a unique ancestry match. Every in-scope open
  // heavy candidate that is unresolved must carry a specific failure mode.
  return origin == unresolved ? resolution > unique : resolution == unique;
}

std::vector<double> PtEdges() {
  std::vector<double> edges;
  for (int bin = 0; bin <= 100; ++bin) edges.push_back(0.5 * bin);
  for (double edge : {60., 75., 100., 150., 250., 500., 1000., 2000.,
                      4000.}) {
    edges.push_back(edge);
  }
  edges.push_back(
      std::nextafter(7000.0, std::numeric_limits<double>::infinity()));
  return edges;
}

std::vector<double> InclusiveUniformEdges(int bins, double minimum,
                                          double inclusiveMaximum) {
  std::vector<double> edges(bins + 1);
  for (int bin = 0; bin <= bins; ++bin) {
    edges[bin] =
        minimum + (inclusiveMaximum - minimum) * bin / bins;
  }
  edges.back() = std::nextafter(
      inclusiveMaximum, std::numeric_limits<double>::infinity());
  return edges;
}

std::unique_ptr<THnSparseD> MakeAuditSparse(const char* name,
                                            const char* title) {
  const std::vector<double> ptEdges = PtEdges();
  const std::vector<double> etaEdges =
      InclusiveUniformEdges(100, -4.0, 4.0);
  const int bins[8] = {
      2,
      2,
      static_cast<int>(Hadronization::kGroundStates.size()),
      5,
      7,
      static_cast<int>(ptEdges.size()) - 1,
      100,
      4096};
  const double minimum[8] = {-0.5, 3.5, -0.5, -0.5,
                             -0.5, 0.0, -4.0, -0.5};
  const double maximum[8] = {
      1.5,
      5.5,
      static_cast<double>(Hadronization::kGroundStates.size()) - 0.5,
      4.5,
      6.5,
      7000.0,
      std::nextafter(4.0, std::numeric_limits<double>::infinity()),
      4095.5};
  auto histogram =
      std::make_unique<THnSparseD>(name, title, 8, bins, minimum, maximum);
  histogram->GetAxis(5)->Set(bins[5], ptEdges.data());
  histogram->GetAxis(6)->Set(bins[6], etaEdges.data());
  histogram->GetAxis(0)->SetTitle("role");
  histogram->GetAxis(1)->SetTitle("hard channel");
  histogram->GetAxis(2)->SetTitle("signed species index");
  histogram->GetAxis(3)->SetTitle("origin");
  histogram->GetAxis(4)->SetTitle("match resolution");
  histogram->GetAxis(5)->SetTitle("p_{T} (GeV/c)");
  histogram->GetAxis(6)->SetTitle("#eta");
  histogram->GetAxis(7)->SetTitle("N_{ch}^{hadronisation}");
  histogram->Sumw2();
  return histogram;
}

Contract ReadContract(TTree* metadata) {
  if (!metadata || metadata->GetEntries() != 1) {
    throw std::runtime_error("job_metadata must contain exactly one row");
  }
  const std::array<const char*, 25> required = {
      "raw_schema",
      "selector",
      "origin_algorithm",
      "species_registry_schema",
      "species_registry_sha256",
      "tune",
      "campaign",
      "campaign_ordinal",
      "role",
      "logical_id",
      "attempt",
      "seed",
      "requested_successes",
      "multiplicity_audit_events",
      "phase_space_pthat_min",
      "repository_commit",
      "config_sha256",
      "executable_sha256",
      "condor_cluster",
      "condor_process",
      "complete",
      "multiplicity_overflow",
      "heavy_flavour_conservation_failures",
      "origin_classification_failures",
      "primary_all_heavy_match_failures"};
  for (const char* name : required) {
    if (!metadata->GetBranch(name)) {
      throw std::runtime_error(std::string("missing metadata branch ") + name);
    }
  }

  std::string* rawSchema = nullptr;
  std::string* selector = nullptr;
  std::string* originAlgorithm = nullptr;
  std::string* registrySchema = nullptr;
  std::string* registrySha = nullptr;
  std::string* tune = nullptr;
  std::string* campaign = nullptr;
  std::string* role = nullptr;
  std::string* repositoryCommit = nullptr;
  std::string* configSha256 = nullptr;
  std::string* executableSha256 = nullptr;
  std::string* condorCluster = nullptr;
  std::string* condorProcess = nullptr;
  Int_t campaignOrdinal = 0;
  Int_t logicalId = 0;
  Int_t attempt = 0;
  Int_t seed = 0;
  ULong64_t requestedSuccesses = 0;
  ULong64_t multiplicityAuditEvents = 0;
  Double_t phaseSpacePthatMin = 0.0;
  Int_t complete = 0;
  ULong64_t multiplicityOverflow = 0;
  ULong64_t conservationFailures = 0;
  ULong64_t classificationFailures = 0;
  ULong64_t allHeavyFailures = 0;
  metadata->SetBranchAddress("raw_schema", &rawSchema);
  metadata->SetBranchAddress("selector", &selector);
  metadata->SetBranchAddress("origin_algorithm", &originAlgorithm);
  metadata->SetBranchAddress("species_registry_schema", &registrySchema);
  metadata->SetBranchAddress("species_registry_sha256", &registrySha);
  metadata->SetBranchAddress("tune", &tune);
  metadata->SetBranchAddress("campaign", &campaign);
  metadata->SetBranchAddress("campaign_ordinal", &campaignOrdinal);
  metadata->SetBranchAddress("role", &role);
  metadata->SetBranchAddress("logical_id", &logicalId);
  metadata->SetBranchAddress("attempt", &attempt);
  metadata->SetBranchAddress("seed", &seed);
  metadata->SetBranchAddress("requested_successes", &requestedSuccesses);
  metadata->SetBranchAddress("multiplicity_audit_events",
                             &multiplicityAuditEvents);
  metadata->SetBranchAddress("phase_space_pthat_min",
                             &phaseSpacePthatMin);
  metadata->SetBranchAddress("repository_commit", &repositoryCommit);
  metadata->SetBranchAddress("config_sha256", &configSha256);
  metadata->SetBranchAddress("executable_sha256", &executableSha256);
  metadata->SetBranchAddress("condor_cluster", &condorCluster);
  metadata->SetBranchAddress("condor_process", &condorProcess);
  metadata->SetBranchAddress("complete", &complete);
  metadata->SetBranchAddress("multiplicity_overflow",
                             &multiplicityOverflow);
  metadata->SetBranchAddress("heavy_flavour_conservation_failures",
                             &conservationFailures);
  metadata->SetBranchAddress("origin_classification_failures",
                             &classificationFailures);
  metadata->SetBranchAddress("primary_all_heavy_match_failures",
                             &allHeavyFailures);
  metadata->GetEntry(0);
  if (!rawSchema || !selector || !originAlgorithm || !registrySchema ||
      !registrySha || !tune || !campaign || !role || !repositoryCommit ||
      !configSha256 || !executableSha256 || !condorCluster ||
      !condorProcess) {
    metadata->ResetBranchAddresses();
    throw std::runtime_error("null string in job_metadata");
  }
  const Contract contract{
      *rawSchema,
      *selector,
      *originAlgorithm,
      *registrySchema,
      *registrySha,
      *tune,
      *campaign,
      *role,
      *repositoryCommit,
      *configSha256,
      *executableSha256,
      *condorCluster,
      *condorProcess,
      campaignOrdinal,
      logicalId,
      attempt,
      seed,
      requestedSuccesses,
      multiplicityAuditEvents,
      phaseSpacePthatMin};
  metadata->ResetBranchAddresses();

  if (contract.rawSchema != Hadronization::kRawSchema ||
      contract.selector != Hadronization::kSelectorVersion ||
      contract.originAlgorithm !=
          Hadronization::kOriginAlgorithmVersion ||
      contract.speciesRegistrySchema !=
          Hadronization::kSpeciesRegistrySchema ||
      contract.speciesRegistrySha256 !=
          Hadronization::kSpeciesRegistrySha256) {
    throw std::runtime_error(
        "raw input does not satisfy the publication analysis contract");
  }
  if (contract.tune != "MONASH" && contract.tune != "JUNCTIONS" &&
      contract.tune != "CLOSEPACKING") {
    throw std::runtime_error("unknown tune in job_metadata");
  }
  if (complete != 1 || multiplicityOverflow != 0 ||
      conservationFailures != 0 || classificationFailures != 0 ||
      allHeavyFailures != 0) {
    throw std::runtime_error(
        "raw input is incomplete or failed a producer invariant");
  }
  return contract;
}

struct ValidationReceiptEvidence {
  std::string receiptSha256;
  std::string rawSha256;
};

ValidationReceiptEvidence VerifyValidationReceipt(
    const char* rawPath, const char* receiptPath, const Contract& contract) {
  if (!receiptPath || std::string(receiptPath).empty()) {
    throw std::runtime_error(
        "a raw-validation PASS receipt is mandatory for origin audits");
  }
  const std::filesystem::path path(receiptPath);
  if (!std::filesystem::is_regular_file(path) ||
      std::filesystem::is_symlink(path)) {
    throw std::runtime_error(
        "raw-validation receipt is absent, non-regular, or a symlink");
  }
  std::ifstream stream(path);
  if (!stream) throw std::runtime_error("cannot read raw-validation receipt");
  nlohmann::json receipt;
  stream >> receipt;
  const std::string rawSha = Hadronization::Sha256FileHex(rawPath);
  const auto rawBytes = std::filesystem::file_size(rawPath);
  if (receipt.value("schema", std::string()) !=
          "hf_raw_validation_receipt_v1" ||
      receipt.value("result", std::string()) != "PASS" ||
      receipt.value("validator_exit_status", -1) != 0 ||
      receipt.value("output_sha256", std::string()) != rawSha ||
      receipt.value("output_bytes", std::uintmax_t{0}) != rawBytes ||
      !receipt.contains("validator_dependency_sha256") ||
      !receipt["validator_dependency_sha256"].is_object() ||
      receipt["validator_dependency_sha256"].empty()) {
    throw std::runtime_error(
        "raw-validation receipt does not bind an exact PASS to the input");
  }
  const nlohmann::json expected = {
      {"campaign", contract.campaign},
      {"campaign_ordinal", contract.campaignOrdinal},
      {"tune", contract.tune},
      {"logical_id", contract.logicalId},
      {"role", contract.role},
      {"attempt", contract.attempt},
      {"seed", contract.seed},
      {"requested_successes", contract.requestedSuccesses},
      {"phase_space_pthat_min", contract.phaseSpacePthatMin},
      {"multiplicity_audit_events", contract.multiplicityAuditEvents},
      {"repository_commit", contract.repositoryCommit},
      {"effective_card_sha256", contract.configSha256},
      {"producer_executable_sha256", contract.executableSha256},
      {"cluster_id", contract.condorCluster},
      {"process_id", contract.condorProcess}};
  if (!receipt.contains("expected_provenance") ||
      !receipt["expected_provenance"].is_object()) {
    throw std::runtime_error(
        "raw-validation receipt has no structured expected provenance");
  }
  const auto& provenance = receipt["expected_provenance"];
  for (const auto& [key, value] : expected.items()) {
    if (!provenance.contains(key) || provenance[key] != value) {
      throw std::runtime_error(
          "raw-validation receipt provenance differs at " + key);
    }
  }
  const std::string attemptStartSha =
      provenance.value("attempt_start_claim_sha256", std::string());
  if (attemptStartSha.size() != 64U) {
    throw std::runtime_error(
        "raw-validation provenance lacks attempt-start claim digest");
  }
  return {Hadronization::Sha256FileHex(path.string()), rawSha};
}

void AddCandidate(std::map<Key, Count>& summary, THnSparseD& unweighted,
                  THnSparseD& weighted, AuditRole role, int hardChannel,
                  int pdg, int origin, int resolution, double pt, double eta,
                  int multiplicity, double eventWeight) {
  const int speciesIndex = SpeciesIndex(pdg);
  if (speciesIndex < 0) {
    throw std::runtime_error("candidate is absent from species registry");
  }
  if (!ValidOriginResolution(origin, resolution)) {
    throw std::runtime_error("invalid origin/resolution combination");
  }
  if (!std::isfinite(eventWeight) || !std::isfinite(pt) ||
      !std::isfinite(eta)) {
    throw std::runtime_error("non-finite candidate value");
  }
  if (pt < 0.0 || pt > 7000.0 || eta < -4.0 || eta > 4.0 ||
      multiplicity < 0 || multiplicity > 4095) {
    throw std::runtime_error(
        "accepted candidate exceeds the versioned audit axes");
  }

  const int roleValue = static_cast<int>(role);
  const double values[8] = {
      static_cast<double>(roleValue),
      static_cast<double>(hardChannel),
      static_cast<double>(speciesIndex),
      static_cast<double>(origin),
      static_cast<double>(resolution),
      pt,
      eta,
      static_cast<double>(multiplicity)};
  unweighted.Fill(values, 1.0);
  weighted.Fill(values, eventWeight);
  Count& count =
      summary[{roleValue, hardChannel, pdg, origin, resolution}];
  ++count.candidates;
  count.sumWeights += eventWeight;
  count.sumWeights2 += eventWeight * eventWeight;
}

}  // namespace

int AuditOriginResolution(const char* inputPath, const char* outputPath,
                          const char* validationReceiptPath) {
  try {
    TFile input(inputPath, "READ");
    if (input.IsZombie()) {
      throw std::runtime_error("cannot open raw input");
    }
    auto* tree = dynamic_cast<TTree*>(input.Get("tree"));
    auto* metadata = dynamic_cast<TTree*>(input.Get("job_metadata"));
    if (!tree) throw std::runtime_error("missing raw event tree");
    const Contract contract = ReadContract(metadata);
    const ValidationReceiptEvidence validationEvidence =
        VerifyValidationReceipt(inputPath, validationReceiptPath, contract);

    const std::vector<const char*> requiredBranches = {
        "hard_channel",
        "hard_indices",
        "hard_ids",
        "event_weight",
        "multiplicity_hadronisation_v1",
        "heavy_flavour_conservation_ok",
        "origin_classification_valid",
        "primary_all_heavy_match_valid",
        "heavyPdg",
        "heavyStatus",
        "heavyIsFinal",
        "heavyCentral",
        "heavyStateCategory",
        "heavyQc",
        "heavyQb",
        "heavyOriginC",
        "heavyOriginB",
        "heavyMatchResolutionC",
        "heavyMatchResolutionB",
        "heavyMatchedHardC",
        "heavyMatchedHardB",
        "heavyPt",
        "heavyEta",
        "heavyConstituentOffsets",
        "heavyConstituentParentSlot",
        "heavyConstituentPdg",
        "heavyConstituentOrigin",
        "heavyConstituentMatchResolution",
        "heavyConstituentMatchedHard"};
    for (const char* name : requiredBranches) {
      if (!tree->GetBranch(name)) {
        throw std::runtime_error(std::string("missing raw branch ") + name);
      }
    }
    Int_t hardChannel = 0;
    Int_t multiplicity = 0;
    Int_t conservationOk = 0;
    Int_t classificationValid = 0;
    Int_t allHeavyValid = 0;
    Double_t eventWeight = 0.0;
    std::vector<int>* pdg = nullptr;
    std::vector<int>* status = nullptr;
    std::vector<int>* isFinal = nullptr;
    std::vector<int>* central = nullptr;
    std::vector<int>* stateCategory = nullptr;
    std::vector<int>* qc = nullptr;
    std::vector<int>* qb = nullptr;
    std::vector<int>* originC = nullptr;
    std::vector<int>* originB = nullptr;
    std::vector<int>* resolutionC = nullptr;
    std::vector<int>* resolutionB = nullptr;
    std::vector<int>* matchedC = nullptr;
    std::vector<int>* matchedB = nullptr;
    std::vector<int>* hardIndices = nullptr;
    std::vector<int>* hardIds = nullptr;
    std::vector<int>* constituentOffsets = nullptr;
    std::vector<int>* constituentParentSlot = nullptr;
    std::vector<int>* constituentPdg = nullptr;
    std::vector<int>* constituentOrigin = nullptr;
    std::vector<int>* constituentResolution = nullptr;
    std::vector<int>* constituentMatchedHard = nullptr;
    std::vector<double>* pt = nullptr;
    std::vector<double>* eta = nullptr;
    tree->SetBranchAddress("hard_channel", &hardChannel);
    tree->SetBranchAddress("event_weight", &eventWeight);
    tree->SetBranchAddress("multiplicity_hadronisation_v1", &multiplicity);
    tree->SetBranchAddress("heavy_flavour_conservation_ok", &conservationOk);
    tree->SetBranchAddress("origin_classification_valid",
                           &classificationValid);
    tree->SetBranchAddress("primary_all_heavy_match_valid",
                           &allHeavyValid);
    tree->SetBranchAddress("heavyPdg", &pdg);
    tree->SetBranchAddress("heavyStatus", &status);
    tree->SetBranchAddress("heavyIsFinal", &isFinal);
    tree->SetBranchAddress("heavyCentral", &central);
    tree->SetBranchAddress("heavyStateCategory", &stateCategory);
    tree->SetBranchAddress("heavyQc", &qc);
    tree->SetBranchAddress("heavyQb", &qb);
    tree->SetBranchAddress("heavyOriginC", &originC);
    tree->SetBranchAddress("heavyOriginB", &originB);
    tree->SetBranchAddress("heavyMatchResolutionC", &resolutionC);
    tree->SetBranchAddress("heavyMatchResolutionB", &resolutionB);
    tree->SetBranchAddress("heavyMatchedHardC", &matchedC);
    tree->SetBranchAddress("heavyMatchedHardB", &matchedB);
    tree->SetBranchAddress("hard_indices", &hardIndices);
    tree->SetBranchAddress("hard_ids", &hardIds);
    tree->SetBranchAddress("heavyConstituentOffsets",
                           &constituentOffsets);
    tree->SetBranchAddress("heavyConstituentParentSlot",
                           &constituentParentSlot);
    tree->SetBranchAddress("heavyConstituentPdg", &constituentPdg);
    tree->SetBranchAddress("heavyConstituentOrigin",
                           &constituentOrigin);
    tree->SetBranchAddress("heavyConstituentMatchResolution",
                           &constituentResolution);
    tree->SetBranchAddress("heavyConstituentMatchedHard",
                           &constituentMatchedHard);
    tree->SetBranchAddress("heavyPt", &pt);
    tree->SetBranchAddress("heavyEta", &eta);

    auto unweighted = MakeAuditSparse(
        "hOriginAuditUnweighted",
        "Unweighted origin audit;role;hard channel;species;origin;resolution;"
        "p_{T};#eta;N_{ch}");
    auto weighted = MakeAuditSparse(
        "hOriginAuditWeighted",
        "Event-weighted origin audit;role;hard channel;species;origin;"
        "resolution;p_{T};#eta;N_{ch}");
    std::map<Key, Count> summary;
    std::map<ClosureBaseKey, Count> closureDenominators;
    std::map<ClosureKey, Count> closureSummary;

    for (Long64_t entry = 0; entry < tree->GetEntries(); ++entry) {
      if (tree->GetEntry(entry) <= 0) {
        throw std::runtime_error("failed to read raw tree entry");
      }
      if (hardChannel != 4 && hardChannel != 5) {
        throw std::runtime_error("invalid hard-flavour channel");
      }
      if (!std::isfinite(eventWeight)) {
        throw std::runtime_error("non-finite event weight");
      }
      if (multiplicity < 0 || multiplicity > 4095) {
        throw std::runtime_error(
            "event multiplicity exceeds the versioned audit axis");
      }
      if (conservationOk != 1 || classificationValid != 1 ||
          allHeavyValid != 1) {
        throw std::runtime_error("event failed a producer invariant");
      }
      if (!pdg || !status || !isFinal || !central || !stateCategory ||
          !qc || !qb ||
          !originC || !originB || !resolutionC || !resolutionB || !pt ||
          !eta || !matchedC || !matchedB || !hardIndices || !hardIds ||
          !constituentOffsets || !constituentParentSlot ||
          !constituentPdg || !constituentOrigin ||
          !constituentResolution || !constituentMatchedHard) {
        throw std::runtime_error("null raw event vector");
      }
      const std::size_t size = pdg->size();
      if (status->size() != size || isFinal->size() != size ||
          central->size() != size || qc->size() != size ||
          stateCategory->size() != size ||
          qb->size() != size || originC->size() != size ||
          originB->size() != size || resolutionC->size() != size ||
          resolutionB->size() != size || matchedC->size() != size ||
          matchedB->size() != size || pt->size() != size ||
          eta->size() != size) {
        throw std::runtime_error("misaligned raw event vectors");
      }
      const std::size_t constituentSize = constituentPdg->size();
      if (hardIndices->size() != 2U || hardIds->size() != 2U ||
          constituentOffsets->size() != size + 1 ||
          constituentOffsets->empty() ||
          constituentOffsets->front() != 0 ||
          static_cast<std::size_t>(constituentOffsets->back()) !=
              constituentSize ||
          constituentParentSlot->size() != constituentSize ||
          constituentOrigin->size() != constituentSize ||
          constituentResolution->size() != constituentSize ||
          constituentMatchedHard->size() != constituentSize) {
        throw std::runtime_error(
            "misaligned primary-all-heavy constituent vectors");
      }

      for (std::size_t index = 0; index < size; ++index) {
        const auto* state = Hadronization::FindGroundState((*pdg)[index]);
        if (!state || !(*central)[index] || !(*isFinal)[index] ||
            !Hadronization::IsDirectPrimaryStatus((*status)[index])) {
          continue;
        }
        const bool charm = state->sector == "charm";
        const int sectorCharge = charm ? (*qc)[index] : (*qb)[index];
        if (sectorCharge == 0) {
          throw std::runtime_error(
              "central species has zero charge in its registry sector");
        }
        const int origin = charm ? (*originC)[index] : (*originB)[index];
        const int resolution =
            charm ? (*resolutionC)[index] : (*resolutionB)[index];

        if (Hadronization::IsCentralKinematic((*pt)[index], (*eta)[index],
                                              false)) {
          AddCandidate(summary, *unweighted, *weighted,
                       AuditRole::kAssociate, hardChannel, (*pdg)[index],
                       origin, resolution, (*pt)[index], (*eta)[index],
                       multiplicity, eventWeight);
        }
        if (IsPublicationTrigger((*pdg)[index]) &&
            Hadronization::IsCentralKinematic((*pt)[index], (*eta)[index],
                                              true)) {
          AddCandidate(summary, *unweighted, *weighted,
                       AuditRole::kTriggerCandidate, hardChannel,
                       (*pdg)[index], origin, resolution, (*pt)[index],
                       (*eta)[index], multiplicity, eventWeight);
          if (origin ==
              static_cast<int>(Hadronization::Origin::kSelectedHard)) {
            const int triggerHard =
                charm ? (*matchedC)[index] : (*matchedB)[index];
            const int flavour = charm ? 4 : 5;
            const int companionPdg =
                sectorCharge > 0 ? -flavour : flavour;
            int companionHard = -1;
            for (std::size_t hard = 0; hard < hardIds->size(); ++hard) {
              if ((*hardIds)[hard] == companionPdg) {
                if (companionHard >= 0) {
                  throw std::runtime_error(
                      "multiple companion hard roots in exact-pair event");
                }
                companionHard = (*hardIndices)[hard];
              }
            }
            if (triggerHard < 0 || companionHard < 0 ||
                triggerHard == companionHard) {
              throw std::runtime_error(
                  "selected trigger lacks a distinct signed companion root");
            }

            int carrierParent = -1;
            for (std::size_t constituent = 0;
                 constituent < constituentSize; ++constituent) {
              if ((*constituentPdg)[constituent] != companionPdg ||
                  (*constituentOrigin)[constituent] !=
                      static_cast<int>(
                          Hadronization::Origin::kSelectedHard) ||
                  (*constituentResolution)[constituent] !=
                      static_cast<int>(
                          Hadronization::MatchResolution::kUnique) ||
                  (*constituentMatchedHard)[constituent] != companionHard) {
                continue;
              }
              const int parent =
                  (*constituentParentSlot)[constituent];
              if (parent < 0 || parent >= static_cast<int>(size) ||
                  !(*isFinal)[parent]) {
                throw std::runtime_error(
                    "resolved companion constituent has an invalid parent");
              }
              // Multiple indistinguishable constituent rows may legitimately
              // identify the same multiply-heavy parent. Only distinct final
              // parents would violate the producer's carrier uniqueness rule.
              if (carrierParent >= 0 && carrierParent != parent) {
                throw std::runtime_error(
                    "companion hard constituent survives in multiple hadrons");
              }
              carrierParent = parent;
            }

            int closureCategory =
                static_cast<int>(
                    ClosureCategory::kUnresolvedCompanion);
            if (carrierParent >= 0) {
              const int category = (*stateCategory)[carrierParent];
              if (category == static_cast<int>(
                                  Hadronization::HeavyStateCategory::
                                      kCentralGround)) {
                const bool eligibleAssociate =
                    Hadronization::IsDirectPrimaryStatus(
                        (*status)[carrierParent]) &&
                    Hadronization::IsCentralKinematic(
                        (*pt)[carrierParent], (*eta)[carrierParent], false);
                closureCategory = static_cast<int>(
                    eligibleAssociate
                        ? ClosureCategory::kCentralGroundAssociate
                        : ClosureCategory::
                              kCentralGroundOutsideAssociate);
              } else if (
                  category ==
                  static_cast<int>(
                      Hadronization::HeavyStateCategory::kExcludedVector)) {
                closureCategory =
                    static_cast<int>(ClosureCategory::kExcludedVector);
              } else if (
                  category ==
                  static_cast<int>(
                      Hadronization::HeavyStateCategory::kExcludedExcited)) {
                closureCategory =
                    static_cast<int>(ClosureCategory::kExcludedExcited);
              } else if (
                  category ==
                  static_cast<int>(
                      Hadronization::HeavyStateCategory::kHiddenHeavy)) {
                closureCategory =
                    static_cast<int>(ClosureCategory::kHiddenHeavy);
              } else if (
                  category ==
                  static_cast<int>(
                      Hadronization::HeavyStateCategory::kMultiplyHeavy)) {
                closureCategory =
                    static_cast<int>(ClosureCategory::kMultiplyHeavy);
              } else {
                closureCategory =
                    static_cast<int>(ClosureCategory::kOtherNoncentral);
              }
            }
            const ClosureBaseKey base{
                hardChannel, multiplicity, (*pdg)[index]};
            Count& denominator = closureDenominators[base];
            ++denominator.candidates;
            denominator.sumWeights += eventWeight;
            denominator.sumWeights2 += eventWeight * eventWeight;
            Count& closure =
                closureSummary[{hardChannel, multiplicity,
                                (*pdg)[index], closureCategory}];
            ++closure.candidates;
            closure.sumWeights += eventWeight;
            closure.sumWeights2 += eventWeight * eventWeight;
          }
        }
      }
    }
    tree->ResetBranchAddresses();

    TFile output(outputPath, "CREATE");
    if (output.IsZombie()) {
      throw std::runtime_error(
          "cannot create audit output (path may already exist)");
    }
    unweighted->Write();
    weighted->Write();

    TTree speciesLookup("species_lookup",
                        "signed species index used by sparse audit axes");
    Int_t lookupIndex = 0;
    Int_t lookupPdg = 0;
    std::string lookupName;
    std::string lookupSector;
    speciesLookup.Branch("species_index", &lookupIndex, "species_index/I");
    speciesLookup.Branch("pdg", &lookupPdg, "pdg/I");
    speciesLookup.Branch("name", &lookupName);
    speciesLookup.Branch("sector", &lookupSector);
    for (std::size_t index = 0;
         index < Hadronization::kGroundStates.size(); ++index) {
      const auto& state = Hadronization::kGroundStates[index];
      lookupIndex = static_cast<int>(index);
      lookupPdg = state.pdg;
      lookupName = std::string(state.name);
      lookupSector = std::string(state.sector);
      speciesLookup.Fill();
    }
    speciesLookup.Write();

    TTree summaryTree(
        "origin_summary",
        "unweighted and event-weighted origin counts by full audit key");
    std::string outputTune = contract.tune;
    std::string outputSector;
    std::string outputSpecies;
    std::string outputRole;
    std::string outputOrigin;
    std::string outputResolution;
    Int_t role = 0;
    Int_t outputHardChannel = 0;
    Int_t outputPdg = 0;
    Int_t origin = 0;
    Int_t resolution = 0;
    ULong64_t candidates = 0;
    Double_t sumWeights = 0.0;
    Double_t sumWeights2 = 0.0;
    Double_t effectiveEntries = 0.0;
    Int_t effectiveEntriesDefined = 0;
    summaryTree.Branch("tune", &outputTune);
    summaryTree.Branch("sector", &outputSector);
    summaryTree.Branch("species", &outputSpecies);
    summaryTree.Branch("role_name", &outputRole);
    summaryTree.Branch("origin_name", &outputOrigin);
    summaryTree.Branch("resolution_name", &outputResolution);
    summaryTree.Branch("role", &role, "role/I");
    summaryTree.Branch("hard_channel", &outputHardChannel,
                       "hard_channel/I");
    summaryTree.Branch("pdg", &outputPdg, "pdg/I");
    summaryTree.Branch("origin", &origin, "origin/I");
    summaryTree.Branch("resolution", &resolution, "resolution/I");
    summaryTree.Branch("candidates", &candidates, "candidates/l");
    summaryTree.Branch("sum_weights", &sumWeights, "sum_weights/D");
    summaryTree.Branch("sum_weights2", &sumWeights2, "sum_weights2/D");
    summaryTree.Branch("effective_entries", &effectiveEntries,
                       "effective_entries/D");
    summaryTree.Branch("effective_entries_defined",
                       &effectiveEntriesDefined,
                       "effective_entries_defined/I");

    struct Aggregate {
      ULong64_t total = 0;
      ULong64_t unresolved = 0;
      double weightedTotal = 0.0;
      double weightedUnresolved = 0.0;
    };
    std::map<std::pair<int, std::string>, Aggregate> aggregates;
    for (const auto& [key, count] : summary) {
      std::tie(role, outputHardChannel, outputPdg, origin, resolution) = key;
      const auto* state = Hadronization::FindGroundState(outputPdg);
      if (!state) {
        throw std::runtime_error("summary species disappeared from registry");
      }
      outputSector = std::string(state->sector);
      outputSpecies = std::string(state->name);
      outputRole = RoleName(role);
      outputOrigin = OriginName(origin);
      outputResolution = ResolutionName(resolution);
      candidates = count.candidates;
      sumWeights = count.sumWeights;
      sumWeights2 = count.sumWeights2;
      effectiveEntriesDefined = sumWeights2 > 0.0 ? 1 : 0;
      effectiveEntries =
          effectiveEntriesDefined
              ? sumWeights * sumWeights / sumWeights2
              : std::numeric_limits<double>::quiet_NaN();
      summaryTree.Fill();

      Aggregate& aggregate = aggregates[{role, outputSector}];
      aggregate.total += candidates;
      aggregate.weightedTotal += sumWeights;
      if (origin == static_cast<int>(Hadronization::Origin::kUnresolved)) {
        aggregate.unresolved += candidates;
        aggregate.weightedUnresolved += sumWeights;
      }
    }
    summaryTree.Write();

    TTree closureTree(
        "primary_all_heavy_closure",
        "validation-only companion-hard-flavour closure by exact Nch");
    std::string closureSchema = kClosureSchema;
    std::string closureTune = contract.tune;
    std::string closureSector;
    std::string closureTriggerSpecies;
    std::string closureCategoryLabel;
    Int_t closureHardChannel = 0;
    Int_t closureMultiplicity = 0;
    Int_t closureTriggerPdg = 0;
    Int_t closureCategory = 0;
    ULong64_t closureCount = 0;
    ULong64_t closureDenominatorCount = 0;
    Double_t closureSumWeights = 0.0;
    Double_t closureDenominatorSumWeights = 0.0;
    Double_t closureFraction = 0.0;
    Double_t closureWeightedFraction = 0.0;
    Int_t closureFractionDefined = 0;
    Int_t closureWeightedFractionDefined = 0;
    closureTree.Branch("closure_schema", &closureSchema);
    closureTree.Branch("tune", &closureTune);
    closureTree.Branch("sector", &closureSector);
    closureTree.Branch("trigger_species", &closureTriggerSpecies);
    closureTree.Branch("category_name", &closureCategoryLabel);
    closureTree.Branch("hard_channel", &closureHardChannel,
                       "hard_channel/I");
    closureTree.Branch("multiplicity_nch", &closureMultiplicity,
                       "multiplicity_nch/I");
    closureTree.Branch("trigger_pdg", &closureTriggerPdg,
                       "trigger_pdg/I");
    closureTree.Branch("category", &closureCategory, "category/I");
    closureTree.Branch("count", &closureCount, "count/l");
    closureTree.Branch("denominator_count", &closureDenominatorCount,
                       "denominator_count/l");
    closureTree.Branch("sum_weights", &closureSumWeights,
                       "sum_weights/D");
    closureTree.Branch("denominator_sum_weights",
                       &closureDenominatorSumWeights,
                       "denominator_sum_weights/D");
    closureTree.Branch("fraction", &closureFraction, "fraction/D");
    closureTree.Branch("weighted_fraction", &closureWeightedFraction,
                       "weighted_fraction/D");
    closureTree.Branch("fraction_defined", &closureFractionDefined,
                       "fraction_defined/I");
    closureTree.Branch("weighted_fraction_defined",
                       &closureWeightedFractionDefined,
                       "weighted_fraction_defined/I");
    for (const auto& [base, denominator] : closureDenominators) {
      std::tie(closureHardChannel, closureMultiplicity,
               closureTriggerPdg) = base;
      const auto* state =
          Hadronization::FindGroundState(closureTriggerPdg);
      if (!state) {
        throw std::runtime_error(
            "closure trigger disappeared from species registry");
      }
      closureSector = std::string(state->sector);
      closureTriggerSpecies = std::string(state->name);
      closureDenominatorCount = denominator.candidates;
      closureDenominatorSumWeights = denominator.sumWeights;
      ULong64_t categoryCountSum = 0;
      double categoryWeightSum = 0.0;
      for (closureCategory = 0;
           closureCategory <=
           static_cast<int>(ClosureCategory::kUnresolvedCompanion);
           ++closureCategory) {
        closureCategoryLabel =
            ClosureCategoryName(closureCategory);
        const auto found = closureSummary.find(
            {closureHardChannel, closureMultiplicity,
             closureTriggerPdg, closureCategory});
        closureCount =
            found == closureSummary.end() ? 0 : found->second.candidates;
        closureSumWeights =
            found == closureSummary.end() ? 0.0 : found->second.sumWeights;
        categoryCountSum += closureCount;
        categoryWeightSum += closureSumWeights;
        closureFractionDefined =
            closureDenominatorCount > 0 ? 1 : 0;
        closureWeightedFractionDefined =
            closureDenominatorSumWeights != 0.0 ? 1 : 0;
        closureFraction =
            closureFractionDefined
                ? static_cast<double>(closureCount) /
                      static_cast<double>(closureDenominatorCount)
                : std::numeric_limits<double>::quiet_NaN();
        closureWeightedFraction =
            closureWeightedFractionDefined
                ? closureSumWeights / closureDenominatorSumWeights
                : std::numeric_limits<double>::quiet_NaN();
        closureTree.Fill();
      }
      const double closureTolerance =
          1e-10 *
          std::max({1.0, std::abs(categoryWeightSum),
                    std::abs(closureDenominatorSumWeights)});
      if (categoryCountSum != closureDenominatorCount ||
          std::abs(categoryWeightSum -
                   closureDenominatorSumWeights) > closureTolerance) {
        throw std::runtime_error(
            "primary-all-heavy closure categories do not close exactly");
      }
    }
    closureTree.Write();

    TTree auditMetadata("audit_metadata",
                        "origin-resolution audit contract and provenance");
    std::string auditSchema = kAuditSchema;
    std::string rawSchema = contract.rawSchema;
    std::string selector = contract.selector;
    std::string originAlgorithm = contract.originAlgorithm;
    std::string speciesRegistrySchema = contract.speciesRegistrySchema;
    std::string speciesRegistrySha256 = contract.speciesRegistrySha256;
    std::string tune = contract.tune;
    std::string primaryAllHeavyMatchSchema =
        Hadronization::kPrimaryAllHeavyMatchSchema;
    std::string closureAuditSchema = kClosureSchema;
    std::string rawInputSha256 = validationEvidence.rawSha256;
    std::string rawValidationReceiptSha256 =
        validationEvidence.receiptSha256;
    std::string roleDefinition =
        "associate=0;trigger_candidate_before_origin_requirement=1";
    std::string weightDefinition =
        "unweighted=count;weighted=sum(event_weight);sumw2=sum(event_weight^2)";
    std::string axisPolicy =
        "pt<=7000;abs(eta)<=4;0<=Nch<=4095;inclusive physical endpoints";
    auditMetadata.Branch("audit_schema", &auditSchema);
    auditMetadata.Branch("raw_schema", &rawSchema);
    auditMetadata.Branch("selector", &selector);
    auditMetadata.Branch("origin_algorithm", &originAlgorithm);
    auditMetadata.Branch("species_registry_schema",
                         &speciesRegistrySchema);
    auditMetadata.Branch("species_registry_sha256",
                         &speciesRegistrySha256);
    auditMetadata.Branch("tune", &tune);
    auditMetadata.Branch("primary_all_heavy_match_schema",
                         &primaryAllHeavyMatchSchema);
    auditMetadata.Branch("primary_all_heavy_closure_schema",
                         &closureAuditSchema);
    auditMetadata.Branch("raw_input_sha256", &rawInputSha256);
    auditMetadata.Branch("raw_validation_receipt_sha256",
                         &rawValidationReceiptSha256);
    auditMetadata.Branch("role_definition", &roleDefinition);
    auditMetadata.Branch("weight_definition", &weightDefinition);
    auditMetadata.Branch("axis_policy", &axisPolicy);
    auditMetadata.Fill();
    auditMetadata.Write();
    TObjString(
        "This audit is diagnostic. Nonzero unresolved trigger candidates "
        "block full production until explicit owner physics sign-off.")
        .Write("publication_gate_policy");
    output.Write();
    output.Close();

    std::cout << "ORIGIN_RESOLUTION_AUDIT"
              << " schema=" << kAuditSchema << " tune=" << contract.tune
              << " summary_rows=" << summary.size()
              << " output=" << outputPath << "\n";
    for (const auto& [key, aggregate] : aggregates) {
      const int aggregateRole = key.first;
      const std::string& sector = key.second;
      const bool fractionDefined = aggregate.total != 0;
      const double fraction =
          fractionDefined
              ? static_cast<double>(aggregate.unresolved) /
                    static_cast<double>(aggregate.total)
              : std::numeric_limits<double>::quiet_NaN();
      const bool weightedFractionDefined =
          aggregate.weightedTotal != 0.0;
      const double weightedFraction =
          weightedFractionDefined
              ? aggregate.weightedUnresolved / aggregate.weightedTotal
              : std::numeric_limits<double>::quiet_NaN();
      std::cout << "ORIGIN_RESOLUTION_SUMMARY"
                << " tune=" << contract.tune
                << " role=" << RoleName(aggregateRole)
                << " sector=" << sector
                << " candidates=" << aggregate.total
                << " unresolved=" << aggregate.unresolved
                << " unresolved_fraction=" << fraction
                << " unresolved_fraction_defined="
                << (fractionDefined ? 1 : 0)
                << " sum_weights=" << aggregate.weightedTotal
                << " unresolved_sum_weights="
                << aggregate.weightedUnresolved
                << " weighted_unresolved_fraction=" << weightedFraction
                << " weighted_unresolved_fraction_defined="
                << (weightedFractionDefined ? 1 : 0)
                << "\n";
    }
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "ORIGIN_AUDIT_ERROR " << error.what() << "\n";
    return 1;
  }
}
