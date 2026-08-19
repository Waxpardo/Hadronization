#!/usr/bin/env python3
"""Generate the species-ordinal header from the derived ordinal artifact.

WHY A HEADER AND NOT A RUNTIME READ. The artifact is JSON and the analysis
macro has no JSON parser -- it is ROOT-only by design, and adding one to the
producer's translation unit to read a table that never changes during a run
would be a dependency for nothing. Generating a header instead follows what
every other table in this tree already does (GeneratedHeavyFlavourRegistry.h,
GeneratedPairRegistry.h, GeneratedTuneSettingRegistry.h,
GeneratedPairObjectContract.h), and buys three things the runtime read does not:
the lookup is fail-closed at compile time, `make check` catches a stale header,
and jobs need no artifact file shipped alongside them.

WHY THE LABELS STRING. F5's legibility condition: a reader of an output file
must be able to decode the species axis without this repository. The ordinal
-> PDG map is written into every output as an object, following the
associate_origin_category_labels precedent.

Usage:
  python3 tools/generate_species_ordinals_header.py            # write
  python3 tools/generate_species_ordinals_header.py --check    # verify current
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "AnalysisScripts/species_ordinals_v2.json"
HEADER = ROOT / "AnalysisScripts/GeneratedSpeciesOrdinals.h"
SCHEMA = "hf_species_ordinal_table_v2"


def load() -> dict:
    payload = json.loads(ARTIFACT.read_text())
    if payload.get("schema") != SCHEMA:
        raise ValueError(
            f"{ARTIFACT} declares schema {payload.get('schema')!r}, expected "
            f"{SCHEMA!r}")
    species = payload["species"]
    if not species:
        raise ValueError("the ordinal table is empty")
    if len(species) != payload["species_count"]:
        raise ValueError(
            f"species_count {payload['species_count']} disagrees with "
            f"{len(species)} rows")
    # Ordinals must be dense, zero-based and in ascending-PDG order: the
    # generated lookup is a binary search over PDG that returns the index, so
    # any gap or misordering would silently return the wrong ordinal.
    for index, row in enumerate(species):
        if row["ordinal"] != index:
            raise ValueError(
                f"row {index} carries ordinal {row['ordinal']}; ordinals must "
                "be dense and zero-based")
    pdgs = [row["pdg"] for row in species]
    if pdgs != sorted(pdgs):
        raise ValueError("rows are not in ascending PDG order")
    if len(set(pdgs)) != len(pdgs):
        raise ValueError("the table repeats a PDG")
    for row in species:
        if not 0 <= row["category"] <= 5:
            raise ValueError(
                f"pdg {row['pdg']} carries category {row['category']}, "
                "outside [0,5]")
    return payload


def render(payload: dict) -> str:
    species = payload["species"]
    lines: list[str] = []
    add = lines.append
    add("// GENERATED FILE -- DO NOT EDIT.")
    add("//")
    add("// Regenerate with:")
    add("//   python3 tools/generate_species_ordinals_header.py")
    add("//")
    add("// Source of truth: AnalysisScripts/species_ordinals_v2.json,")
    add("// itself derived from a raw file's heavy_stability_audit tree by")
    add("// tools/GenerateSpeciesOrdinals.C. The axis's index space comes from")
    add("// PYTHIA's own recorded state, never from a hand-written list.")
    add("//")
    add("// FAIL-CLOSED (F6). This table is the COMPLETE admissible set. Any")
    add("// sector-charged PDG absent from it must FAIL the run. There is")
    add("// deliberately no overflow bin: an overflow bin is how 152 species")
    add("// became invisible in the first place.")
    add("#ifndef HADRONIZATION_GENERATED_SPECIES_ORDINALS_H")
    add("#define HADRONIZATION_GENERATED_SPECIES_ORDINALS_H")
    add("")
    add("#include <array>")
    add("#include <cstddef>")
    add("")
    add("namespace Hadronization {")
    add("")
    add(f'inline constexpr const char* kSpeciesOrdinalSchema =')
    add(f'    "{payload["schema"]}";')
    add("// FNV-1a over the canonical ordinal:pdg serialisation. Identifies the")
    add("// AXIS, so it is unchanged by adding annotation columns.")
    add(f'inline constexpr const char* kSpeciesOrdinalDigest =')
    add(f'    "{payload["table_digest_fnv1a64"]}";')
    add(f"inline constexpr int kSpeciesOrdinalCount = {len(species)};")
    add("")
    add("// Category as the PRODUCER's own ClassifyHeavyStateDetailed assigns")
    add("// it, computed from heavy_stability_audit's recorded columns rather")
    add("// than from the runtime particle record. Summing the species axis by")
    add("// this column must reproduce the 6-category axis bin for bin; the two")
    add("// labelings share their rules but not their inputs, which is what")
    add("// makes that check mean something.")
    add("struct SpeciesOrdinalRow {")
    add("  int pdg;")
    add("  int category;")
    add("};")
    add("")
    add("// Indexed BY ORDINAL, in ascending signed PDG order.")
    add(f"inline constexpr std::array<SpeciesOrdinalRow, {len(species)}>")
    add("    kSpeciesOrdinals = {{")
    for row in species:
        add(f'    {{{row["pdg"]}, {row["category"]}}},'
            f'  // {row["ordinal"]} {row["category_name"]}')
    add("}};")
    add("")
    add("// Fail-closed lookup. Returns false for any PDG absent from the")
    add("// table; callers must abort rather than substitute a bin.")
    add("inline bool SpeciesOrdinalFor(int pdg, int& ordinal) {")
    add("  std::size_t low = 0;")
    add("  std::size_t high = kSpeciesOrdinals.size();")
    add("  while (low < high) {")
    add("    const std::size_t middle = low + (high - low) / 2;")
    add("    const int candidate = kSpeciesOrdinals[middle].pdg;")
    add("    if (candidate == pdg) {")
    add("      ordinal = static_cast<int>(middle);")
    add("      return true;")
    add("    }")
    add("    if (candidate < pdg) {")
    add("      low = middle + 1;")
    add("    } else {")
    add("      high = middle;")
    add("    }")
    add("  }")
    add("  return false;")
    add("}")
    add("")
    add("// The producer category for an ordinal, for the summation check.")
    add("inline int SpeciesCategoryForOrdinal(int ordinal) {")
    add("  if (ordinal < 0 || ordinal >= kSpeciesOrdinalCount) return -1;")
    add("  return kSpeciesOrdinals[static_cast<std::size_t>(ordinal)].category;")
    add("}")
    add("")
    add("// F5 LEGIBILITY. Written into every output file so the axis can be")
    add("// decoded without this repository.")
    add("inline constexpr const char* kSpeciesOrdinalLabels =")
    chunks: list[str] = []
    current = '{'
    for index, row in enumerate(species):
        piece = f'"{row["ordinal"]}":{row["pdg"]}'
        if index + 1 < len(species):
            piece += ","
        if len(current) + len(piece) > 66:
            chunks.append(current)
            current = ""
        current += piece
    current += "}"
    chunks.append(current)
    for index, chunk in enumerate(chunks):
        escaped = chunk.replace("\\", "\\\\").replace('"', '\\"')
        terminator = ";" if index + 1 == len(chunks) else ""
        add(f'    "{escaped}"{terminator}')
    add("")
    add("}  // namespace Hadronization")
    add("")
    add("#endif  // HADRONIZATION_GENERATED_SPECIES_ORDINALS_H")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = load()
    text = render(payload)
    if args.check:
        if not HEADER.exists():
            print(f"SPECIES_ORDINALS_STALE missing {HEADER}", file=sys.stderr)
            return 1
        if HEADER.read_text() != text:
            print(f"SPECIES_ORDINALS_STALE {HEADER} differs from a fresh "
                  "generation", file=sys.stderr)
            return 1
        print("SPECIES_ORDINALS_CURRENT "
              f"species={payload['species_count']} "
              f"digest={payload['table_digest_fnv1a64']}")
        return 0
    HEADER.write_text(text)
    print(f"SPECIES_ORDINALS_WRITTEN {HEADER} "
          f"species={payload['species_count']} "
          f"digest={payload['table_digest_fnv1a64']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
