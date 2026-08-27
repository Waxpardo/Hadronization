#!/usr/bin/env python3
"""Generate contracts/GeneratedPairObjectContract.h from the contract.

The pair-file object contract used to exist as three hand-maintained lists
that had drifted apart:

  Validation/ValidatePairDirectory.C        the allowlist  (58 names)
  Validation/ValidatePairBlockClosure.C     4 sparse names, missing
                                            hFlavourClosure
  plotting/Validate_THnSparse_Production.C
                                            4 names, missing both
                                            hFlavourClosure and
                                            hCorrelationsByOrigin

Because the closure list was the one that drifted, the ten-block closure
silently skipped hFlavourClosure. This generator makes
config/pair_file_object_contract_v1.json the single source of truth, in the
same style tools/generate_registry_artifacts.py already uses for the species
and pair registries.

Usage:
  python3 tools/generate_pair_object_contract.py            # write
  python3 tools/generate_pair_object_contract.py --check    # verify current
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/pair_file_object_contract_v1.json"
HEADER = ROOT / "contracts/GeneratedPairObjectContract.h"
SCHEMA = "hf_pair_file_object_contract_v1"

PRESENCE = {"required": "kRequired", "conditional": "kConditional"}
SCOPE = {
    "both": "kBoth",
    "unmerged_only": "kUnmergedOnly",
    "merged_only": "kMergedOnly",
}
SEMANTICS = {
    "additive_content": "kAdditiveContent",
    "additive_scalar": "kAdditiveScalar",
    "invariant": "kInvariant",
}


def load_versions() -> tuple[list[str], dict[str, str]]:
    """The schema versions this contract knows, oldest first, and their tags."""
    payload = json.loads(CONTRACT.read_text())
    versions = payload["schema_versions"]
    tags = payload["schema_version_tags"]
    if not versions:
        raise ValueError("schema_versions must not be empty")
    if len(set(versions)) != len(versions):
        raise ValueError(f"schema_versions has duplicates: {versions}")
    if set(tags) != set(versions):
        raise ValueError(
            f"schema_version_tags keys {sorted(tags)} do not match "
            f"schema_versions {sorted(versions)}")
    if len(set(tags.values())) != len(tags):
        raise ValueError(
            "two schema versions share one analysis_schema tag, so a file "
            f"could not be attributed to one of them: {tags}")
    return versions, tags


def load() -> list[dict]:
    payload = json.loads(CONTRACT.read_text())
    if payload.get("schema") != SCHEMA:
        raise ValueError(f"unsupported contract schema in {CONTRACT}")
    versions, _ = load_versions()
    objects = payload["objects"]
    seen: set[str] = set()
    for row in objects:
        since = row.get("since_schema", versions[0])
        if since not in versions:
            raise ValueError(
                f"{row['name']}: since_schema {since!r} is not one of "
                f"{versions}")
        name = row["name"]
        if name in seen:
            raise ValueError(f"duplicate object in contract: {name}")
        seen.add(name)
        if row["presence"] not in PRESENCE:
            raise ValueError(f"{name}: bad presence {row['presence']!r}")
        if row["scope"] not in SCOPE:
            raise ValueError(f"{name}: bad scope {row['scope']!r}")
        if row["merge_semantics"] not in SEMANTICS:
            raise ValueError(f"{name}: bad merge_semantics")
        if row["closure"] not in ("checked", "exempt"):
            raise ValueError(f"{name}: bad closure {row['closure']!r}")
        if not row.get("closure_reason"):
            raise ValueError(f"{name}: closure_reason must be nonempty")
        # A closure check only means something for something that is summed.
        if row["closure"] == "checked" and row["merge_semantics"] == "invariant":
            raise ValueError(
                f"{name}: an invariant object cannot be closure-checked")
        # An object that is not always written cannot be unconditionally
        # required by a closure that reads all ten blocks.
        if row["closure"] == "checked" and row["presence"] == "conditional":
            raise ValueError(
                f"{name}: a conditional object cannot be closure-checked "
                "unconditionally")
        # Identity across blocks only means something for something that is
        # NOT summed: an additive object's blocks differ by design.
        if row.get("identity_checked"):
            if row["merge_semantics"] != "invariant":
                raise ValueError(
                    f"{name}: only an invariant object can be "
                    "identity_checked; an additive object's blocks differ by "
                    "design")
            if row["presence"] != "required":
                raise ValueError(
                    f"{name}: a conditional object cannot be unconditionally "
                    "identity-checked")
    return sorted(objects, key=lambda r: r["name"])


def cxx_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def version_mask(row: dict, versions: list[str]) -> int:
    """Bit i set when the object belongs to versions[i].

    An object exists from its since_schema onward. Objects are added to the
    contract over time and none has ever been removed; if one ever is, this is
    where an until_schema would go, and it must land with the negative test
    that proves the removal is seen.
    """
    since = row.get("since_schema", versions[0])
    first = versions.index(since)
    mask = 0
    for index in range(first, len(versions)):
        mask |= 1 << index
    return mask


def render(objects: list[dict], versions: list[str],
           tags: dict[str, str]) -> str:
    lines: list[str] = []
    add = lines.append
    add("// GENERATED FILE -- DO NOT EDIT.")
    add("//")
    add("// Regenerate with:")
    add("//   python3 tools/generate_pair_object_contract.py")
    add("//")
    add("// Source of truth: config/pair_file_object_contract_v1.json")
    add("//")
    add("// This header is the single definition of what a pair file")
    add("// contains. Three hand-maintained copies of this list had drifted,")
    add("// and the copy that drifted was the ten-block closure's, which is")
    add("// why hFlavourClosure went unchecked. Consumers must filter this")
    add("// array rather than restate any part of it.")
    add("#ifndef HADRONIZATION_GENERATED_PAIR_OBJECT_CONTRACT_H")
    add("#define HADRONIZATION_GENERATED_PAIR_OBJECT_CONTRACT_H")
    add("")
    add("#include <array>")
    add("#include <set>")
    add("#include <string>")
    add("")
    add("namespace Hadronization {")
    add("")
    add("enum class PairObjectPresence { kRequired, kConditional };")
    add("enum class PairObjectScope { kBoth, kUnmergedOnly, kMergedOnly };")
    add("enum class PairObjectMergeSemantics {")
    add("  kAdditiveContent,")
    add("  kAdditiveScalar,")
    add("  kInvariant")
    add("};")
    add("")
    add("// The analysis schema a pair file was written under. The contract is")
    add("// exact-match in both directions, so a directory can only be judged")
    add("// against the version it actually carries: a v3-aware contract must")
    add("// not fail a correct v2 directory, and vice versa.")
    add("enum class PairSchemaVersion : unsigned {")
    for index, version in enumerate(versions):
        comma = "," if index + 1 < len(versions) else ""
        add(f"  k{version.upper()} = {index}{comma}")
    add("};")
    add("")
    add("// Maps a file's analysis_schema string to a version. Returns false on")
    add("// anything unrecognised -- FAIL CLOSED. There is deliberately no")
    add("// default: silently treating an unknown schema as the newest (or the")
    add("// oldest) is how a contract change gets taught to one consumer and")
    add("// not its siblings.")
    add("inline bool ParsePairSchemaVersion(const std::string& analysisSchema,")
    add("                                   PairSchemaVersion& version) {")
    for vname in versions:
        add(f"  if (analysisSchema == {cxx_string(tags[vname])}) {{")
        add(f"    version = PairSchemaVersion::k{vname.upper()};")
        add("    return true;")
        add("  }")
    add("  return false;")
    add("}")
    add("")
    add("struct PairObjectDefinition {")
    add("  const char* name;")
    add("  const char* rootClass;")
    add("  PairObjectPresence presence;")
    add("  PairObjectScope scope;")
    add("  PairObjectMergeSemantics mergeSemantics;")
    add("  bool closureChecked;")
    add("  bool identityChecked;")
    add("  unsigned schemaVersionMask;")
    add("};")
    add("")
    add(f"inline constexpr std::array<PairObjectDefinition, {len(objects)}>")
    add("    kPairObjects = {{")
    for row in objects:
        add("        {" + cxx_string(row["name"]) + ",")
        add("         " + cxx_string(row["root_class"]) + ",")
        add(f"         PairObjectPresence::{PRESENCE[row['presence']]},")
        add(f"         PairObjectScope::{SCOPE[row['scope']]},")
        add("         PairObjectMergeSemantics::"
            f"{SEMANTICS[row['merge_semantics']]},")
        add(f"         {'true' if row['closure'] == 'checked' else 'false'},")
        add(f"         {'true' if row.get('identity_checked') else 'false'},")
        add(f"         0b{version_mask(row, versions):0{len(versions)}b}}},")
    add("}};")
    add("")
    add("// True when the object belongs in a directory of the given kind.")
    add("inline bool PairObjectInScope(const PairObjectDefinition& object,")
    add("                              bool merged) {")
    add("  if (object.scope == PairObjectScope::kBoth) return true;")
    add("  return merged ? object.scope == PairObjectScope::kMergedOnly")
    add("                : object.scope == PairObjectScope::kUnmergedOnly;")
    add("}")
    add("")
    add("// True when the object exists in the given schema version.")
    add("inline bool PairObjectInSchema(const PairObjectDefinition& object,")
    add("                               PairSchemaVersion version) {")
    add("  return (object.schemaVersionMask &")
    add("          (1u << static_cast<unsigned>(version))) != 0u;")
    add("}")
    add("")
    add("// Objects that must be present. Absence is an error.")
    add("inline std::set<std::string> RequiredPairObjects(")
    add("    bool merged, PairSchemaVersion version) {")
    add("  std::set<std::string> names;")
    add("  for (const auto& object : kPairObjects) {")
    add("    if (!PairObjectInScope(object, merged)) continue;")
    add("    if (!PairObjectInSchema(object, version)) continue;")
    add("    if (object.presence != PairObjectPresence::kRequired) continue;")
    add("    names.insert(object.name);")
    add("  }")
    add("  return names;")
    add("}")
    add("")
    add("// Objects that may be present. Absence is not an error.")
    add("inline std::set<std::string> PermittedPairObjects(")
    add("    bool merged, PairSchemaVersion version) {")
    add("  std::set<std::string> names;")
    add("  for (const auto& object : kPairObjects) {")
    add("    if (!PairObjectInScope(object, merged)) continue;")
    add("    if (!PairObjectInSchema(object, version)) continue;")
    add("    if (object.presence != PairObjectPresence::kConditional) {")
    add("      continue;")
    add("    }")
    add("    names.insert(object.name);")
    add("  }")
    add("  return names;")
    add("}")
    add("")
    add("// Objects whose contents the ten-block closure must sum-check,")
    add("// restricted to one ROOT class.")
    add("inline std::set<std::string> ClosureCheckedObjects(")
    add("    const std::string& rootClass, PairSchemaVersion version) {")
    add("  std::set<std::string> names;")
    add("  for (const auto& object : kPairObjects) {")
    add("    if (!object.closureChecked) continue;")
    add("    if (!PairObjectInSchema(object, version)) continue;")
    add("    if (rootClass != object.rootClass) continue;")
    add("    names.insert(object.name);")
    add("  }")
    add("  return names;")
    add("}")
    add("")
    add("// Every closure-checked object with summable contents, whatever")
    add("// its ROOT class. This is the count the closure reports.")
    add("inline std::set<std::string> ClosureCheckedContentObjects(")
    add("    PairSchemaVersion version) {")
    add("  std::set<std::string> names;")
    add("  for (const auto& object : kPairObjects) {")
    add("    if (!object.closureChecked) continue;")
    add("    if (!PairObjectInSchema(object, version)) continue;")
    add("    if (object.mergeSemantics !=")
    add("        PairObjectMergeSemantics::kAdditiveContent) {")
    add("      continue;")
    add("    }")
    add("    names.insert(object.name);")
    add("  }")
    add("  return names;")
    add("}")
    add("")
    add("// Objects whose value the ten-block closure must assert IDENTICAL")
    add("// across the central file and all ten blocks. Distinct from the sum")
    add("// closure: an invariant has nothing to sum, but blocks disagreeing")
    add("// about a contract string means the sum is over objects that do not")
    add("// mean the same thing. Derived here rather than hand-listed in the")
    add("// closure, because a hand-listed pair is exactly how an object gets")
    add("// added to the contract and silently never checked.")
    add("inline std::set<std::string> IdentityCheckedObjects(")
    add("    PairSchemaVersion version) {")
    add("  std::set<std::string> names;")
    add("  for (const auto& object : kPairObjects) {")
    add("    if (!object.identityChecked) continue;")
    add("    if (!PairObjectInSchema(object, version)) continue;")
    add("    names.insert(object.name);")
    add("  }")
    add("  return names;")
    add("}")
    add("")
    add("// Closure-checked scalars of one ROOT class, summed across blocks.")
    add("inline std::set<std::string> ClosureCheckedScalars(")
    add("    const std::string& rootClass, PairSchemaVersion version) {")
    add("  std::set<std::string> names;")
    add("  for (const auto& object : kPairObjects) {")
    add("    if (!object.closureChecked) continue;")
    add("    if (!PairObjectInSchema(object, version)) continue;")
    add("    if (object.mergeSemantics !=")
    add("        PairObjectMergeSemantics::kAdditiveScalar) {")
    add("      continue;")
    add("    }")
    add("    if (rootClass != object.rootClass) continue;")
    add("    names.insert(object.name);")
    add("  }")
    add("  return names;")
    add("}")
    add("")
    add("}  // namespace Hadronization")
    add("")
    add("#endif  // HADRONIZATION_GENERATED_PAIR_OBJECT_CONTRACT_H")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    versions, tags = load_versions()
    text = render(load(), versions, tags)
    if args.check:
        if not HEADER.exists():
            print(f"PAIR_OBJECT_CONTRACT_STALE missing {HEADER}",
                  file=sys.stderr)
            return 1
        if HEADER.read_text() != text:
            print("PAIR_OBJECT_CONTRACT_STALE "
                  f"{HEADER} differs from a fresh generation", file=sys.stderr)
            return 1
        print("PAIR_OBJECT_CONTRACT_CURRENT "
              f"objects={len(load())}")
        return 0
    HEADER.write_text(text)
    print(f"PAIR_OBJECT_CONTRACT_WRITTEN {HEADER} objects={len(load())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
