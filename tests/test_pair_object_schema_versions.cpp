// Exercises the schema-keyed pair-object selection against the generated
// contract, at the level where the requirement actually bites: what set a
// consumer gets for a given file.
//
// THE REQUIREMENT. The contract is exact-match in BOTH directions, so a
// contract that has learned a v3 object must NOT fail a correct v2 directory
// that rightly carries six. These cases are the three the design was required
// to satisfy, plus the fail-closed parse.

#include "../contracts/GeneratedPairObjectContract.h"

#include <cstdio>
#include <set>
#include <string>

namespace {

int errors = 0;

void Check(bool condition, const std::string& what) {
  if (!condition) {
    std::printf("FAIL %s\n", what.c_str());
    ++errors;
  }
}

std::set<std::string> ContentObjects(Hadronization::PairSchemaVersion version) {
  return Hadronization::ClosureCheckedContentObjects(version);
}

}  // namespace

int main() {
  using Hadronization::PairSchemaVersion;
  const std::string kSpecies = "hFlavourClosureSpecies";
  const std::string kClosure = "hFlavourClosure";

  // ---------------------------------------------------------------------
  // Fail-closed parsing. An unknown schema must resolve to NO version.
  // ---------------------------------------------------------------------
  PairSchemaVersion parsed = PairSchemaVersion::kV3;
  Check(Hadronization::ParsePairSchemaVersion(
            "paul_pair_objects_primary_ground_v2", parsed),
        "the v2 tag must parse");
  Check(parsed == PairSchemaVersion::kV2, "the v2 tag must parse AS v2");
  Check(Hadronization::ParsePairSchemaVersion(
            "paul_pair_objects_primary_ground_v3", parsed),
        "the v3 tag must parse");
  Check(parsed == PairSchemaVersion::kV3, "the v3 tag must parse AS v3");
  Check(!Hadronization::ParsePairSchemaVersion("", parsed),
        "an empty schema must NOT parse");
  Check(!Hadronization::ParsePairSchemaVersion(
            "paul_pair_objects_primary_ground_v4", parsed),
        "an unknown future schema must NOT parse -- no defaulting to newest");
  Check(!Hadronization::ParsePairSchemaVersion(
            "paul_pair_objects_primary_ground", parsed),
        "a prefix of a known schema must NOT parse");

  // ---------------------------------------------------------------------
  // CASE 1: a correct v2 directory carries six content objects and must be
  // accepted. This is the case the requirement exists to protect.
  // ---------------------------------------------------------------------
  const std::set<std::string> v2Content = ContentObjects(PairSchemaVersion::kV2);
  Check(v2Content.size() == 6,
        "v2 must expect exactly six closure-checked content objects, got " +
            std::to_string(v2Content.size()));
  Check(v2Content.count(kClosure) == 1, "v2 must expect hFlavourClosure");
  Check(v2Content.count(kSpecies) == 0,
        "v2 must NOT expect hFlavourClosureSpecies -- a v3 object demanded of "
        "a v2 directory fails every correct v2 directory");

  // ---------------------------------------------------------------------
  // CASE 2: a v2 directory carrying the v3 object is WRONG and must be
  // rejected. Permissiveness is not the fix for case 1: the object is not in
  // v2's required set and not in its permitted set either, so the allowlist's
  // "unexpected object" arm fires.
  // ---------------------------------------------------------------------
  for (const bool merged : {false, true}) {
    const std::set<std::string> required =
        Hadronization::RequiredPairObjects(merged, PairSchemaVersion::kV2);
    const std::set<std::string> permitted =
        Hadronization::PermittedPairObjects(merged, PairSchemaVersion::kV2);
    Check(required.count(kSpecies) == 0,
          "v2 must not REQUIRE the v3 object");
    Check(permitted.count(kSpecies) == 0,
          "v2 must not PERMIT the v3 object either, or a v2 file carrying it "
          "would pass unnoticed");
  }

  // ---------------------------------------------------------------------
  // CASE 3: a v3 directory MISSING the species object must be rejected. The
  // object is required in v3, so the allowlist's "missing required" arm fires.
  // ---------------------------------------------------------------------
  const std::set<std::string> v3Content = ContentObjects(PairSchemaVersion::kV3);
  Check(v3Content.size() == 7,
        "v3 must expect exactly seven closure-checked content objects, got " +
            std::to_string(v3Content.size()));
  Check(v3Content.count(kSpecies) == 1,
        "v3 must REQUIRE hFlavourClosureSpecies, so a v3 file lacking it fails");
  for (const bool merged : {false, true}) {
    Check(Hadronization::RequiredPairObjects(merged, PairSchemaVersion::kV3)
                  .count(kSpecies) == 1,
          "v3's required set must contain the species object");
  }

  // ---------------------------------------------------------------------
  // The v2 set must be a strict subset of the v3 set: objects are added over
  // time and none has been removed. A v3 set that DROPPED something would
  // silently stop checking it -- which is exactly how hFlavourClosure went
  // unchecked for a generation.
  // ---------------------------------------------------------------------
  for (const auto& name : v2Content) {
    Check(v3Content.count(name) == 1,
          "v3 dropped the v2 content object " + name);
  }
  Check(v3Content.size() == v2Content.size() + 1,
        "v3 must add exactly one content object over v2");

  // The parallel object must not have displaced the original: hFlavourClosure
  // stays, byte-identical, in both versions. That is the ratified design.
  Check(v3Content.count(kClosure) == 1,
        "hFlavourClosure must survive unchanged in v3");

  // Scope is orthogonal to version: the species object is written in both
  // merged and unmerged directories, like the other sparses.
  Check(Hadronization::RequiredPairObjects(true, PairSchemaVersion::kV3)
                .count(kSpecies) == 1 &&
            Hadronization::RequiredPairObjects(false, PairSchemaVersion::kV3)
                    .count(kSpecies) == 1,
        "the species object must be required in both merged and unmerged v3");

  std::printf("PAIR_OBJECT_SCHEMA_VERSIONS errors=%d v2_content=%zu "
              "v3_content=%zu\n",
              errors, v2Content.size(), v3Content.size());
  return errors == 0 ? 0 : 1;
}
