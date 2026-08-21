// GENERATED FILE -- DO NOT EDIT.
//
// Regenerate with:
//   python3 tools/generate_pair_object_contract.py
//
// Source of truth: config/pair_file_object_contract_v1.json
//
// This header is the single definition of what a pair file
// contains. Three hand-maintained copies of this list had drifted,
// and the copy that drifted was the ten-block closure's, which is
// why hFlavourClosure went unchecked. Consumers must filter this
// array rather than restate any part of it.
#ifndef HADRONIZATION_GENERATED_PAIR_OBJECT_CONTRACT_H
#define HADRONIZATION_GENERATED_PAIR_OBJECT_CONTRACT_H

#include <array>
#include <set>
#include <string>

namespace Hadronization {

enum class PairObjectPresence { kRequired, kConditional };
enum class PairObjectScope { kBoth, kUnmergedOnly, kMergedOnly };
enum class PairObjectMergeSemantics {
  kAdditiveContent,
  kAdditiveScalar,
  kInvariant
};

// The analysis schema a pair file was written under. The contract is
// exact-match in both directions, so a directory can only be judged
// against the version it actually carries: a v3-aware contract must
// not fail a correct v2 directory, and vice versa.
enum class PairSchemaVersion : unsigned {
  kV2 = 0,
  kV3 = 1
};

// Maps a file's analysis_schema string to a version. Returns false on
// anything unrecognised -- FAIL CLOSED. There is deliberately no
// default: silently treating an unknown schema as the newest (or the
// oldest) is how a contract change gets taught to one consumer and
// not its siblings.
inline bool ParsePairSchemaVersion(const std::string& analysisSchema,
                                   PairSchemaVersion& version) {
  if (analysisSchema == "paul_pair_objects_primary_ground_v2") {
    version = PairSchemaVersion::kV2;
    return true;
  }
  if (analysisSchema == "paul_pair_objects_primary_ground_v3") {
    version = PairSchemaVersion::kV3;
    return true;
  }
  return false;
}

struct PairObjectDefinition {
  const char* name;
  const char* rootClass;
  PairObjectPresence presence;
  PairObjectScope scope;
  PairObjectMergeSemantics mergeSemantics;
  bool closureChecked;
  bool identityChecked;
  unsigned schemaVersionMask;
};

inline constexpr std::array<PairObjectDefinition, 66>
    kPairObjects = {{
        {"analysis_implementation",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"analysis_macro_sha256",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"analysis_profile",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"analysis_repository_commit",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"analysis_schema",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"analysis_version",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"associate_origin_category_labels",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         true,
         0b11},
        {"associate_origin_category_schema",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         true,
         0b11},
        {"associate_pdg",
         "TParameter<int>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"associate_pt_min_exclusive",
         "TParameter<double>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"centralEligible",
         "TParameter<bool>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"central_ground_state_count",
         "TParameter<Long64_t>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveScalar,
         true,
         false,
         0b11},
        {"central_hard_trigger_count",
         "TParameter<Long64_t>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveScalar,
         true,
         false,
         0b11},
        {"direct_primary_heavy_count",
         "TParameter<Long64_t>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveScalar,
         true,
         false,
         0b11},
        {"eta_abs_max_inclusive",
         "TParameter<double>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"event_filter_modulo",
         "TParameter<int>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"event_filter_remainder",
         "TParameter<int>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"event_filter_schema",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"hAsKinematics",
         "THnSparse",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveContent,
         true,
         false,
         0b11},
        {"hCorrelations",
         "THnSparse",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveContent,
         true,
         false,
         0b11},
        {"hCorrelationsByOrigin",
         "THnSparse",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveContent,
         true,
         false,
         0b11},
        {"hFlavourClosure",
         "THnSparse",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveContent,
         true,
         false,
         0b11},
        {"hFlavourClosureSpecies",
         "THnSparse",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveContent,
         true,
         false,
         0b10},
        {"hFlavourClosureSummary",
         "TH1D",
         PairObjectPresence::kConditional,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveContent,
         false,
         false,
         0b11},
        {"hTrKinematics",
         "THnSparse",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveContent,
         true,
         false,
         0b11},
        {"heavy_sector",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"heavy_sign",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"input_events",
         "TParameter<Long64_t>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveScalar,
         true,
         false,
         0b11},
        {"input_file_count",
         "TParameter<int>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"input_sum_weights",
         "TParameter<double>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveScalar,
         true,
         false,
         0b11},
        {"merge_input_file_count",
         "TParameter<Long64_t>",
         PairObjectPresence::kRequired,
         PairObjectScope::kMergedOnly,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"merge_input_manifest_sha256",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kMergedOnly,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"pair_combinatorics_mode",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"pair_count",
         "TParameter<Long64_t>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveScalar,
         true,
         false,
         0b11},
        {"pair_registry_sha256",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"pair_sum_weights",
         "TParameter<double>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveScalar,
         true,
         false,
         0b11},
        {"primary_all_heavy_closure_failures",
         "TParameter<Long64_t>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveScalar,
         true,
         false,
         0b11},
        {"reference_meson_pdg",
         "TParameter<int>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"same_sign_pair_factor",
         "TParameter<double>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"selector_version",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"source_input_events",
         "TParameter<Long64_t>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"species_ordinal_digest",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         true,
         0b10},
        {"species_ordinal_labels",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         true,
         0b10},
        {"species_ordinal_schema",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         true,
         0b10},
        {"species_registry_sha256",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"summed MULTIPLICITY",
         "TH1D",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveContent,
         true,
         false,
         0b11},
        {"trigger_count",
         "TParameter<Long64_t>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveScalar,
         true,
         false,
         0b11},
        {"trigger_pdg",
         "TParameter<int>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"trigger_pt_min_exclusive",
         "TParameter<double>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"trigger_sum_weights",
         "TParameter<double>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kAdditiveScalar,
         true,
         false,
         0b11},
        {"upstream_campaign",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_effective_settings_schema",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_effective_settings_sha256",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kUnmergedOnly,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_executable_sha256",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_heavy_flavour_conservation_failures",
         "TParameter<Long64_t>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_heavy_stability_audit_schema",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_heavy_stability_audit_sha256",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_origin_algorithm",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_origin_classification_failures",
         "TParameter<Long64_t>",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_raw_schema",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_raw_sha256",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kUnmergedOnly,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_repository_commit",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_selector_version",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_tune",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_tune_difference_allowlist_schema",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
        {"upstream_tune_difference_allowlist_sha256",
         "TObjString",
         PairObjectPresence::kRequired,
         PairObjectScope::kBoth,
         PairObjectMergeSemantics::kInvariant,
         false,
         false,
         0b11},
}};

// True when the object belongs in a directory of the given kind.
inline bool PairObjectInScope(const PairObjectDefinition& object,
                              bool merged) {
  if (object.scope == PairObjectScope::kBoth) return true;
  return merged ? object.scope == PairObjectScope::kMergedOnly
                : object.scope == PairObjectScope::kUnmergedOnly;
}

// True when the object exists in the given schema version.
inline bool PairObjectInSchema(const PairObjectDefinition& object,
                               PairSchemaVersion version) {
  return (object.schemaVersionMask &
          (1u << static_cast<unsigned>(version))) != 0u;
}

// Objects that must be present. Absence is an error.
inline std::set<std::string> RequiredPairObjects(
    bool merged, PairSchemaVersion version) {
  std::set<std::string> names;
  for (const auto& object : kPairObjects) {
    if (!PairObjectInScope(object, merged)) continue;
    if (!PairObjectInSchema(object, version)) continue;
    if (object.presence != PairObjectPresence::kRequired) continue;
    names.insert(object.name);
  }
  return names;
}

// Objects that may be present. Absence is not an error.
inline std::set<std::string> PermittedPairObjects(
    bool merged, PairSchemaVersion version) {
  std::set<std::string> names;
  for (const auto& object : kPairObjects) {
    if (!PairObjectInScope(object, merged)) continue;
    if (!PairObjectInSchema(object, version)) continue;
    if (object.presence != PairObjectPresence::kConditional) {
      continue;
    }
    names.insert(object.name);
  }
  return names;
}

// Objects whose contents the ten-block closure must sum-check,
// restricted to one ROOT class.
inline std::set<std::string> ClosureCheckedObjects(
    const std::string& rootClass, PairSchemaVersion version) {
  std::set<std::string> names;
  for (const auto& object : kPairObjects) {
    if (!object.closureChecked) continue;
    if (!PairObjectInSchema(object, version)) continue;
    if (rootClass != object.rootClass) continue;
    names.insert(object.name);
  }
  return names;
}

// Every closure-checked object with summable contents, whatever
// its ROOT class. This is the count the closure reports.
inline std::set<std::string> ClosureCheckedContentObjects(
    PairSchemaVersion version) {
  std::set<std::string> names;
  for (const auto& object : kPairObjects) {
    if (!object.closureChecked) continue;
    if (!PairObjectInSchema(object, version)) continue;
    if (object.mergeSemantics !=
        PairObjectMergeSemantics::kAdditiveContent) {
      continue;
    }
    names.insert(object.name);
  }
  return names;
}

// Objects whose value the ten-block closure must assert IDENTICAL
// across the central file and all ten blocks. Distinct from the sum
// closure: an invariant has nothing to sum, but blocks disagreeing
// about a contract string means the sum is over objects that do not
// mean the same thing. Derived here rather than hand-listed in the
// closure, because a hand-listed pair is exactly how an object gets
// added to the contract and silently never checked.
inline std::set<std::string> IdentityCheckedObjects(
    PairSchemaVersion version) {
  std::set<std::string> names;
  for (const auto& object : kPairObjects) {
    if (!object.identityChecked) continue;
    if (!PairObjectInSchema(object, version)) continue;
    names.insert(object.name);
  }
  return names;
}

// Closure-checked scalars of one ROOT class, summed across blocks.
inline std::set<std::string> ClosureCheckedScalars(
    const std::string& rootClass, PairSchemaVersion version) {
  std::set<std::string> names;
  for (const auto& object : kPairObjects) {
    if (!object.closureChecked) continue;
    if (!PairObjectInSchema(object, version)) continue;
    if (object.mergeSemantics !=
        PairObjectMergeSemantics::kAdditiveScalar) {
      continue;
    }
    if (rootClass != object.rootClass) continue;
    names.insert(object.name);
  }
  return names;
}

}  // namespace Hadronization

#endif  // HADRONIZATION_GENERATED_PAIR_OBJECT_CONTRACT_H
