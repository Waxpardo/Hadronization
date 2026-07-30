#include "../SimulationScripts/HeavyFlavourUtils.h"
#include "../SimulationScripts/GeneratedHeavyFlavourRegistry.h"
#include "../AnalysisScripts/GeneratedPairRegistry.h"

#include "TBranch.h"
#include "TFile.h"
#include "TH1.h"
#include "TTree.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <set>
#include <string>
#include <vector>

namespace {

bool IsPublicationTrigger(int pdg) {
  return std::any_of(
      Hadronization::kPairDefinitions.begin(),
      Hadronization::kPairDefinitions.end(),
      [pdg](const Hadronization::PairDefinition& pair) {
        return pair.triggerPdg == pdg;
      });
}

template <typename T>
bool ReadScalar(TTree* tree, const char* name, T& value) {
  if (!tree || !tree->GetBranch(name)) return false;
  tree->SetBranchAddress(name, &value);
  const bool ok = tree->GetEntry(0) > 0;
  tree->ResetBranchAddresses();
  return ok;
}

bool ReadString(TTree* tree, const char* name, std::string& value) {
  if (!tree || !tree->GetBranch(name)) return false;
  std::string* pointer = nullptr;
  tree->SetBranchAddress(name, &pointer);
  if (tree->GetEntry(0) <= 0 || !pointer) {
    tree->ResetBranchAddresses();
    return false;
  }
  value = *pointer;
  tree->ResetBranchAddresses();
  return true;
}

}  // namespace

int ValidateRawOutput(const char* fileName, const char* expectedCampaign,
                      const char* expectedTune, int expectedLogicalId,
                      unsigned long long expectedSuccesses,
                      int expectedAttempt = -1, int expectedSeed = -1,
                      bool exhaustive = true) {
  int errors = 0;
  auto fail = [&](const std::string& message) {
    std::cerr << "RAW_VALIDATION_ERROR " << message << "\n";
    ++errors;
  };

  TFile file(fileName, "READ");
  if (file.IsZombie()) {
    fail("file is missing, zombie, or unreadable");
    return errors;
  }
  auto* tree = dynamic_cast<TTree*>(file.Get("tree"));
  auto* metadata = dynamic_cast<TTree*>(file.Get("job_metadata"));
  auto* stability = dynamic_cast<TTree*>(file.Get("heavy_stability_audit"));
  auto* processCounts = dynamic_cast<TTree*>(file.Get("process_counts"));
  auto* effectiveSettings =
      dynamic_cast<TTree*>(file.Get("effective_settings"));
  auto* multiplicity = dynamic_cast<TH1*>(file.Get("hMULTIPLICITY"));
  if (!tree) fail("missing tree");
  if (!metadata || metadata->GetEntries() != 1) fail("missing/sized job_metadata");
  if (!stability || stability->GetEntries() == 0) fail("missing heavy_stability_audit");
  if (!processCounts || processCounts->GetEntries() == 0) fail("missing process_counts");
  if (!effectiveSettings || effectiveSettings->GetEntries() == 0) {
    fail("missing effective_settings");
  }
  if (!multiplicity) fail("missing hMULTIPLICITY");
  if (errors) return errors;

  std::string campaign, tune, role, schema, selector, originAlgorithm;
  std::string registrySha, configSha;
  std::string executableSha, repositoryCommit, repositoryDirty;
  int logicalId = -1, attempt = -1, seed = -1, complete = 0;
  unsigned long long requested = 0, attempts = 0, successes = 0, failures = 0;
  unsigned long long entries = 0, decodeFailures = 0;
  unsigned long long duplicateConflictGroupsC = 0;
  unsigned long long duplicateConflictGroupsB = 0;
  unsigned long long duplicateDemotionsC = 0;
  unsigned long long duplicateDemotionsB = 0;
  unsigned long long multiplicityOverflow = 0;
  unsigned long long multiplicityStrongEmOverflow = 0;
  unsigned long long multiplicityAuditEvents = 0;
  double sumw = 0.0, sumw2 = 0.0;
  if (!ReadString(metadata, "campaign", campaign) ||
      !ReadString(metadata, "tune", tune) ||
      !ReadString(metadata, "role", role) ||
      !ReadString(metadata, "raw_schema", schema) ||
      !ReadString(metadata, "selector", selector) ||
      !ReadString(metadata, "origin_algorithm", originAlgorithm) ||
      !ReadString(metadata, "species_registry_sha256", registrySha) ||
      !ReadString(metadata, "config_sha256", configSha) ||
      !ReadString(metadata, "executable_sha256", executableSha) ||
      !ReadString(metadata, "repository_commit", repositoryCommit) ||
      !ReadString(metadata, "repository_dirty", repositoryDirty)) {
    fail("missing string metadata");
  }
  ReadScalar(metadata, "logical_id", logicalId);
  ReadScalar(metadata, "attempt", attempt);
  ReadScalar(metadata, "seed", seed);
  ReadScalar(metadata, "complete", complete);
  ReadScalar(metadata, "requested_successes", requested);
  ReadScalar(metadata, "attempts", attempts);
  ReadScalar(metadata, "successful_events", successes);
  ReadScalar(metadata, "failed_attempts", failures);
  ReadScalar(metadata, "tree_entries", entries);
  ReadScalar(metadata, "content_decode_failures", decodeFailures);
  if (!ReadScalar(metadata, "duplicate_hard_carrier_conflict_groups_charm",
                  duplicateConflictGroupsC) ||
      !ReadScalar(metadata, "duplicate_hard_carrier_conflict_groups_beauty",
                  duplicateConflictGroupsB) ||
      !ReadScalar(metadata, "duplicate_hard_carrier_demotions_charm",
                  duplicateDemotionsC) ||
      !ReadScalar(metadata, "duplicate_hard_carrier_demotions_beauty",
                  duplicateDemotionsB)) {
    fail("missing duplicate-hard-carrier metadata");
  }
  ReadScalar(metadata, "multiplicity_overflow", multiplicityOverflow);
  ReadScalar(metadata, "multiplicity_strong_em_overflow",
             multiplicityStrongEmOverflow);
  ReadScalar(metadata, "multiplicity_audit_events",
             multiplicityAuditEvents);
  ReadScalar(metadata, "sum_weights", sumw);
  ReadScalar(metadata, "sum_weights2", sumw2);

  if (campaign != expectedCampaign) fail("campaign mismatch");
  if (tune != expectedTune) fail("tune mismatch");
  if (schema != Hadronization::kRawSchema) fail("raw schema mismatch");
  if (selector != Hadronization::kSelectorVersion) fail("selector mismatch");
  if (originAlgorithm != Hadronization::kOriginAlgorithmVersion) {
    fail("origin-algorithm mismatch");
  }
  if (registrySha != Hadronization::kSpeciesRegistrySha256) {
    fail("species-registry checksum mismatch");
  }
  if (configSha.empty() || configSha == "UNRECORDED") fail("config checksum missing");
  if (executableSha.empty() || executableSha == "UNRECORDED") fail("executable checksum missing");
  if (repositoryCommit.empty() || repositoryCommit == "UNRECORDED") fail("repository commit missing");
  if (repositoryDirty == "true" && role != "pilot") {
    fail("dirty non-pilot production build is not canonical");
  }
  if (logicalId != expectedLogicalId) fail("logical ID mismatch");
  if (expectedAttempt >= 0 && attempt != expectedAttempt) fail("attempt mismatch");
  if (expectedSeed >= 0 && seed != expectedSeed) fail("seed mismatch");
  if (requested != expectedSuccesses || successes != expectedSuccesses ||
      entries != expectedSuccesses ||
      static_cast<unsigned long long>(tree->GetEntries()) != expectedSuccesses) {
    fail("exact-success/tree-entry contract mismatch");
  }
  if (attempts != successes + failures) fail("attempt accounting identity failed");
  if (!complete) fail("producer did not mark output complete");
  if (!std::isfinite(sumw) || !std::isfinite(sumw2) || sumw2 < 0.0) {
    fail("invalid weight sums");
  }
  if (decodeFailures != 0) fail("heavy-content decode failures are nonzero");
  if (multiplicityOverflow != 0 || multiplicityStrongEmOverflow != 0) {
    fail("multiplicity overflow is nonzero");
  }
  if (static_cast<unsigned long long>(multiplicity->GetEntries()) != expectedSuccesses) {
    fail("multiplicity entries do not equal successful events");
  }

  int stabilityFinalMayDecay = 0;
  stability->SetBranchAddress("final_may_decay", &stabilityFinalMayDecay);
  for (Long64_t row = 0; row < stability->GetEntries(); ++row) {
    stability->GetEntry(row);
    if (stabilityFinalMayDecay != 0) fail("heavy hadron remains decay enabled");
  }

  int code = 0;
  unsigned long long count = 0;
  unsigned long long processTotal = 0;
  processCounts->SetBranchAddress("code", &code);
  processCounts->SetBranchAddress("count", &count);
  for (Long64_t row = 0; row < processCounts->GetEntries(); ++row) {
    processCounts->GetEntry(row);
    processTotal += count;
  }
  if (processTotal != expectedSuccesses) fail("process-code counts do not sum to successes");

  const std::vector<const char*> requiredIntegerVectors = {
      "heavyIndex", "heavyPdg", "heavyStatus", "heavyStatusAbs",
      "heavyIsFinal", "heavyIsMeson", "heavyIsBaryon", "heavyCharge3",
      "heavyMother1", "heavyMother2", "heavyDaughter1", "heavyDaughter2",
      "heavyMotherOffsets", "heavyMothers", "heavyNc", "heavyNcbar",
      "heavyNb", "heavyNbbar", "heavyQc", "heavyQb", "heavyCentral",
      "heavyOriginC", "heavyOriginB", "heavyMatchResolutionC",
      "heavyMatchResolutionB", "heavyMatchedHardC", "heavyMatchedHardB",
      "heavyConflictingHardC", "heavyConflictingHardB",
      "ancestryIndex", "ancestryPdg", "ancestryStatus", "ancestryMother1",
      "ancestryMother2", "multAuditPdg", "multAuditStatus",
      "multAuditHasWeakAncestor"};
  for (const char* name : requiredIntegerVectors) {
    TBranch* branch = tree->GetBranch(name);
    if (!branch || std::string(branch->GetClassName()) != "vector<int>") {
      fail(std::string("missing or non-integer vector branch ") + name);
    }
  }
  if (errors || !exhaustive) {
    std::cout << "RAW_VALIDATION_SUMMARY errors=" << errors
              << " exhaustive=" << exhaustive << "\n";
    return errors;
  }

  ULong64_t eventId = 0;
  Double_t eventWeight = 0.0;
  Int_t multiplicityDirect = 0;
  Int_t multiplicityStrongEm = 0;
  Int_t multiplicityDirectBySpecies[5] = {0, 0, 0, 0, 0};
  Int_t multiplicityStrongEmBySpecies[5] = {0, 0, 0, 0, 0};
  std::vector<int>* heavyPdg = nullptr;
  std::vector<int>* heavyStatus = nullptr;
  std::vector<int>* heavyIsFinal = nullptr;
  std::vector<int>* heavyCentral = nullptr;
  std::vector<int>* heavyQc = nullptr;
  std::vector<int>* heavyQb = nullptr;
  std::vector<int>* heavyOriginC = nullptr;
  std::vector<int>* heavyOriginB = nullptr;
  std::vector<int>* heavyMatchResolutionC = nullptr;
  std::vector<int>* heavyMatchResolutionB = nullptr;
  std::vector<int>* heavyMatchedHardC = nullptr;
  std::vector<int>* heavyMatchedHardB = nullptr;
  std::vector<int>* heavyConflictingHardC = nullptr;
  std::vector<int>* heavyConflictingHardB = nullptr;
  std::vector<int>* heavyMotherOffsets = nullptr;
  std::vector<int>* heavyMothers = nullptr;
  std::vector<int>* ancestryIndex = nullptr;
  std::vector<int>* ancestryPdg = nullptr;
  std::vector<int>* ancestryStatus = nullptr;
  std::vector<int>* ancestryMother1 = nullptr;
  std::vector<int>* ancestryMother2 = nullptr;
  std::vector<int>* multAuditPdg = nullptr;
  std::vector<int>* multAuditStatus = nullptr;
  std::vector<int>* multAuditHasWeakAncestor = nullptr;
  std::vector<double>* multAuditPt = nullptr;
  std::vector<double>* multAuditEta = nullptr;
  std::vector<double>* heavyPt = nullptr;
  std::vector<double>* heavyEta = nullptr;
  std::vector<double>* heavyPhi = nullptr;
  tree->SetBranchAddress("event_id", &eventId);
  tree->SetBranchAddress("event_weight", &eventWeight);
  tree->SetBranchAddress("multiplicity_hadronisation_v1",
                         &multiplicityDirect);
  tree->SetBranchAddress("multiplicity_final_strong_em_v1",
                         &multiplicityStrongEm);
  tree->SetBranchAddress("multiplicity_direct_by_species",
                         multiplicityDirectBySpecies);
  tree->SetBranchAddress("multiplicity_strong_em_by_species",
                         multiplicityStrongEmBySpecies);
  tree->SetBranchAddress("heavyPdg", &heavyPdg);
  tree->SetBranchAddress("heavyStatus", &heavyStatus);
  tree->SetBranchAddress("heavyIsFinal", &heavyIsFinal);
  tree->SetBranchAddress("heavyCentral", &heavyCentral);
  tree->SetBranchAddress("heavyQc", &heavyQc);
  tree->SetBranchAddress("heavyQb", &heavyQb);
  tree->SetBranchAddress("heavyOriginC", &heavyOriginC);
  tree->SetBranchAddress("heavyOriginB", &heavyOriginB);
  tree->SetBranchAddress("heavyMatchResolutionC", &heavyMatchResolutionC);
  tree->SetBranchAddress("heavyMatchResolutionB", &heavyMatchResolutionB);
  tree->SetBranchAddress("heavyMatchedHardC", &heavyMatchedHardC);
  tree->SetBranchAddress("heavyMatchedHardB", &heavyMatchedHardB);
  tree->SetBranchAddress("heavyConflictingHardC", &heavyConflictingHardC);
  tree->SetBranchAddress("heavyConflictingHardB", &heavyConflictingHardB);
  tree->SetBranchAddress("heavyMotherOffsets", &heavyMotherOffsets);
  tree->SetBranchAddress("heavyMothers", &heavyMothers);
  tree->SetBranchAddress("ancestryIndex", &ancestryIndex);
  tree->SetBranchAddress("ancestryPdg", &ancestryPdg);
  tree->SetBranchAddress("ancestryStatus", &ancestryStatus);
  tree->SetBranchAddress("ancestryMother1", &ancestryMother1);
  tree->SetBranchAddress("ancestryMother2", &ancestryMother2);
  tree->SetBranchAddress("multAuditPdg", &multAuditPdg);
  tree->SetBranchAddress("multAuditStatus", &multAuditStatus);
  tree->SetBranchAddress("multAuditHasWeakAncestor",
                         &multAuditHasWeakAncestor);
  tree->SetBranchAddress("multAuditPt", &multAuditPt);
  tree->SetBranchAddress("multAuditEta", &multAuditEta);
  tree->SetBranchAddress("heavyPt", &heavyPt);
  tree->SetBranchAddress("heavyEta", &heavyEta);
  tree->SetBranchAddress("heavyPhi", &heavyPhi);

  std::set<ULong64_t> eventIds;
  unsigned long long unresolvedCharmTriggerCandidates = 0;
  unsigned long long unresolvedBeautyTriggerCandidates = 0;
  unsigned long long resolvedNonhardCharmTriggerCandidates = 0;
  unsigned long long resolvedNonhardBeautyTriggerCandidates = 0;
  unsigned long long observedDuplicateDemotionsC = 0;
  unsigned long long observedDuplicateDemotionsB = 0;
  for (Long64_t entry = 0; entry < tree->GetEntries(); ++entry) {
    tree->GetEntry(entry);
    if (!eventIds.insert(eventId).second) fail("duplicate event ID");
    if (!std::isfinite(eventWeight)) fail("non-finite event weight");
    int directComponentSum = 0;
    int strongEmComponentSum = 0;
    for (int species = 0; species < 5; ++species) {
      directComponentSum += multiplicityDirectBySpecies[species];
      strongEmComponentSum += multiplicityStrongEmBySpecies[species];
    }
    if (directComponentSum != multiplicityDirect ||
        strongEmComponentSum != multiplicityStrongEm) {
      fail("multiplicity component sum mismatch");
    }
    const std::size_t auditSize = multAuditPdg ? multAuditPdg->size() : 0;
    const bool auditSizesMatch =
        multAuditStatus && multAuditStatus->size() == auditSize &&
        multAuditHasWeakAncestor &&
        multAuditHasWeakAncestor->size() == auditSize &&
        multAuditPt && multAuditPt->size() == auditSize &&
        multAuditEta && multAuditEta->size() == auditSize;
    if (!auditSizesMatch) {
      fail("multiplicity audit vector-size mismatch");
    } else if (static_cast<unsigned long long>(entry) <
               multiplicityAuditEvents) {
      int auditDirect = 0;
      int auditStrongEm = 0;
      for (std::size_t row = 0; row < auditSize; ++row) {
        if ((*multAuditPt)[row] > 0.15 &&
            std::abs((*multAuditEta)[row]) <= 4.0) {
          if (Hadronization::IsDirectPrimaryStatus(
                  (*multAuditStatus)[row])) {
            ++auditDirect;
          }
          if ((*multAuditHasWeakAncestor)[row] == 0) ++auditStrongEm;
        }
      }
      if (auditDirect != multiplicityDirect ||
          auditStrongEm != multiplicityStrongEm) {
        fail("independent pilot multiplicity recomputation mismatch");
      }
    } else if (auditSize != 0) {
      fail("multiplicity audit data present beyond declared pilot range");
    }
    const std::size_t size = heavyPdg ? heavyPdg->size() : 0;
    const bool sizesMatch =
        heavyStatus && heavyStatus->size() == size &&
        heavyIsFinal && heavyIsFinal->size() == size &&
        heavyCentral && heavyCentral->size() == size &&
        heavyQc && heavyQc->size() == size &&
        heavyQb && heavyQb->size() == size &&
        heavyOriginC && heavyOriginC->size() == size &&
        heavyOriginB && heavyOriginB->size() == size &&
        heavyMatchResolutionC && heavyMatchResolutionC->size() == size &&
        heavyMatchResolutionB && heavyMatchResolutionB->size() == size &&
        heavyMatchedHardC && heavyMatchedHardC->size() == size &&
        heavyMatchedHardB && heavyMatchedHardB->size() == size &&
        heavyConflictingHardC && heavyConflictingHardC->size() == size &&
        heavyConflictingHardB && heavyConflictingHardB->size() == size &&
        heavyPt && heavyPt->size() == size &&
        heavyEta && heavyEta->size() == size &&
        heavyPhi && heavyPhi->size() == size &&
        heavyMotherOffsets && heavyMotherOffsets->size() == size + 1 &&
        heavyMotherOffsets && !heavyMotherOffsets->empty() &&
        heavyMothers &&
        static_cast<std::size_t>(heavyMotherOffsets->back()) ==
            heavyMothers->size() &&
        ancestryIndex && ancestryPdg &&
        ancestryIndex->size() == ancestryPdg->size() &&
        ancestryStatus && ancestryIndex->size() == ancestryStatus->size() &&
        ancestryMother1 && ancestryIndex->size() == ancestryMother1->size() &&
        ancestryMother2 && ancestryIndex->size() == ancestryMother2->size();
    if (!sizesMatch) {
      fail("per-event heavy vector lengths are inconsistent");
      continue;
    }
    std::set<int> selectedFinalHardC;
    std::set<int> selectedFinalHardB;
    for (std::size_t index = 0; index < size; ++index) {
      if (!std::isfinite((*heavyPt)[index]) ||
          !std::isfinite((*heavyEta)[index]) ||
          !std::isfinite((*heavyPhi)[index])) {
        fail("non-finite heavy-hadron kinematics");
      }
      const auto validateCarrier =
          [&](int charge, int origin, int resolution, int matchedHard,
              int conflictingHard,
              std::set<int>& selectedFinalHard,
              unsigned long long& observedDuplicateDemotions,
              const char* sector) {
            if (!(*heavyIsFinal)[index] || charge == 0) return;
            if (resolution == static_cast<int>(
                                  Hadronization::MatchResolution::
                                      kDuplicateHardCarrier)) {
              ++observedDuplicateDemotions;
              if (origin !=
                      static_cast<int>(Hadronization::Origin::kUnresolved) ||
                  matchedHard != -1) {
                fail(std::string("invalid duplicate-carrier demotion in ") +
                     sector);
              }
              if (conflictingHard < 0) {
                fail(std::string("missing conflicting hard carrier in ") +
                     sector);
              }
            } else if (conflictingHard != -1) {
              fail(std::string("spurious conflicting hard carrier in ") +
                   sector);
            }
            if (origin ==
                static_cast<int>(Hadronization::Origin::kSelectedHard)) {
              if (resolution != static_cast<int>(
                                    Hadronization::MatchResolution::kUnique) ||
                  matchedHard < 0) {
                fail(std::string("invalid selected-hard metadata in ") +
                     sector);
              } else if (!selectedFinalHard.insert(matchedHard).second) {
                fail(std::string("duplicate surviving selected hard carrier in ") +
                     sector);
              }
            }
          };
      validateCarrier((*heavyQc)[index], (*heavyOriginC)[index],
                      (*heavyMatchResolutionC)[index],
                      (*heavyMatchedHardC)[index],
                      (*heavyConflictingHardC)[index], selectedFinalHardC,
                      observedDuplicateDemotionsC, "charm");
      validateCarrier((*heavyQb)[index], (*heavyOriginB)[index],
                      (*heavyMatchResolutionB)[index],
                      (*heavyMatchedHardB)[index],
                      (*heavyConflictingHardB)[index], selectedFinalHardB,
                      observedDuplicateDemotionsB, "beauty");
      if ((*heavyCentral)[index] && (*heavyIsFinal)[index] &&
          Hadronization::IsDirectPrimaryStatus((*heavyStatus)[index]) &&
          Hadronization::IsCentralKinematic((*heavyPt)[index],
                                            (*heavyEta)[index], true)) {
        const auto* state = Hadronization::FindGroundState((*heavyPdg)[index]);
        if (state && IsPublicationTrigger((*heavyPdg)[index]) &&
            state->sector == "charm" && (*heavyQc)[index] != 0) {
          if ((*heavyOriginC)[index] ==
                  static_cast<int>(Hadronization::Origin::kUnresolved) &&
              (*heavyMatchResolutionC)[index] ==
                  static_cast<int>(
                      Hadronization::MatchResolution::kUnique)) {
            fail("unresolved charm origin marked uniquely resolved");
          }
          if ((*heavyOriginC)[index] ==
              static_cast<int>(Hadronization::Origin::kUnresolved)) {
            ++unresolvedCharmTriggerCandidates;
          } else if ((*heavyOriginC)[index] !=
                     static_cast<int>(Hadronization::Origin::kSelectedHard)) {
            ++resolvedNonhardCharmTriggerCandidates;
          }
        }
        if (state && IsPublicationTrigger((*heavyPdg)[index]) &&
            state->sector == "beauty" && (*heavyQb)[index] != 0) {
          if ((*heavyOriginB)[index] ==
                  static_cast<int>(Hadronization::Origin::kUnresolved) &&
              (*heavyMatchResolutionB)[index] ==
                  static_cast<int>(
                      Hadronization::MatchResolution::kUnique)) {
            fail("unresolved beauty origin marked uniquely resolved");
          }
          if ((*heavyOriginB)[index] ==
              static_cast<int>(Hadronization::Origin::kUnresolved)) {
            ++unresolvedBeautyTriggerCandidates;
          } else if ((*heavyOriginB)[index] !=
                     static_cast<int>(Hadronization::Origin::kSelectedHard)) {
            ++resolvedNonhardBeautyTriggerCandidates;
          }
        }
      }
    }
  }
  if (observedDuplicateDemotionsC != duplicateDemotionsC ||
      observedDuplicateDemotionsB != duplicateDemotionsB) {
    fail("duplicate-carrier demotion metadata mismatch");
  }
  if ((duplicateDemotionsC == 0) != (duplicateConflictGroupsC == 0) ||
      (duplicateDemotionsB == 0) != (duplicateConflictGroupsB == 0) ||
      duplicateConflictGroupsC > duplicateDemotionsC / 2 ||
      duplicateConflictGroupsB > duplicateDemotionsB / 2) {
    fail("duplicate-carrier group/demotion accounting is inconsistent");
  }
  std::cout << "RAW_ORIGIN_AUDIT unresolved_charm_trigger_candidates="
            << unresolvedCharmTriggerCandidates
            << " unresolved_beauty_trigger_candidates="
            << unresolvedBeautyTriggerCandidates
            << " resolved_nonhard_charm_trigger_candidates="
            << resolvedNonhardCharmTriggerCandidates
            << " resolved_nonhard_beauty_trigger_candidates="
            << resolvedNonhardBeautyTriggerCandidates
            << " duplicate_hard_carrier_groups_charm="
            << duplicateConflictGroupsC
            << " duplicate_hard_carrier_groups_beauty="
            << duplicateConflictGroupsB
            << " duplicate_hard_carrier_demotions_charm="
            << duplicateDemotionsC
            << " duplicate_hard_carrier_demotions_beauty="
            << duplicateDemotionsB << "\n";
  std::cout << "RAW_VALIDATION_SUMMARY errors=" << errors
            << " entries=" << tree->GetEntries()
            << " process_codes=" << processCounts->GetEntries()
            << " stability_rows=" << stability->GetEntries() << "\n";
  return errors;
}
