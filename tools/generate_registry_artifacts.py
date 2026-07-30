#!/usr/bin/env python3
"""Generate C++ registry headers and the expanded signed-pair registry.

The two JSON definition files are the only hand-maintained registry sources.
Generated artifacts are deterministic and carry the source SHA-256 digests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cpp_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def validate_species(states: list[dict]) -> dict[int, dict]:
    by_pdg: dict[int, dict] = {}
    required = {"pdg", "name", "sector", "kind", "spin2j1", "charge3", "qc", "qb", "valence"}
    for state in states:
        missing = required - state.keys()
        if missing:
            raise ValueError(f"state is missing {sorted(missing)}: {state}")
        pdg = int(state["pdg"])
        if pdg == 0 or pdg in by_pdg:
            raise ValueError(f"invalid or duplicate signed PDG ID: {pdg}")
        if state["sector"] not in {"charm", "beauty"}:
            raise ValueError(f"invalid sector for {pdg}")
        if state["kind"] not in {"meson", "baryon"}:
            raise ValueError(f"invalid kind for {pdg}")
        by_pdg[pdg] = state

    for pdg, state in by_pdg.items():
        conjugate = by_pdg.get(-pdg)
        if not conjugate:
            raise ValueError(f"missing explicit charge conjugate for {pdg}")
        for field in ("charge3", "qc", "qb"):
            if int(conjugate[field]) != -int(state[field]):
                raise ValueError(f"{field} is not conjugated for {pdg}")
        for field in ("sector", "kind", "spin2j1"):
            if conjugate[field] != state[field]:
                raise ValueError(f"{field} differs across conjugates for {pdg}")
    return by_pdg


def expanded_pairs(definition: dict, by_pdg: dict[int, dict]) -> list[dict]:
    overrides = definition["legacy_filename_overrides"]
    references = {int(key): int(value) for key, value in definition["reference_mesons"].items()}
    pairs: list[dict] = []
    used_names: dict[str, tuple[int, int]] = {}
    for sector in ("charm", "beauty"):
        associates = sorted(
            (state for state in by_pdg.values() if state["sector"] == sector),
            key=lambda state: (abs(int(state["pdg"])), int(state["pdg"]) < 0),
        )
        for trigger in definition["central_triggers"][sector]:
            trigger = int(trigger)
            if trigger not in by_pdg or by_pdg[trigger]["sector"] != sector:
                raise ValueError(f"invalid {sector} trigger {trigger}")
            reference = references.get(trigger)
            if reference not in by_pdg:
                raise ValueError(f"missing signed reference meson for trigger {trigger}")
            trigger_charge = int(by_pdg[trigger]["qc" if sector == "charm" else "qb"])
            if trigger_charge == 0:
                raise ValueError(f"trigger {trigger} has zero {sector} content")
            for associate in associates:
                associate_pdg = int(associate["pdg"])
                associate_charge = int(associate["qc" if sector == "charm" else "qb"])
                if associate_charge == 0:
                    continue
                key = f"{trigger},{associate_pdg}"
                filename = overrides.get(
                    key,
                    f"pair_{sector}_trig_{by_pdg[trigger]['name']}_assoc_{associate['name']}.root",
                )
                previous = used_names.get(filename)
                if previous and previous != (trigger, associate_pdg):
                    raise ValueError(f"filename collision: {filename}: {previous} and {(trigger, associate_pdg)}")
                used_names[filename] = (trigger, associate_pdg)
                pairs.append(
                    {
                        "sector": sector,
                        "trigger_pdg": trigger,
                        "associate_pdg": associate_pdg,
                        "heavy_sign": "OS" if trigger_charge * associate_charge < 0 else "SS",
                        "filename": filename,
                        "trigger_label": by_pdg[trigger]["name"],
                        "associate_label": associate["name"],
                        "associate_kind": associate["kind"],
                        "reference_meson_pdg": reference,
                        "central": True,
                        "legacy_filename": key in overrides,
                    }
                )
    return pairs


def render_species_header(schema: str, sha: str, states: list[dict]) -> str:
    rows = "\n".join(
        "  {%d, %s, %s, %s, %d, %d, %d, %d},"
        % (
            state["pdg"],
            cpp_string(state["name"]),
            cpp_string(state["sector"]),
            cpp_string(state["kind"]),
            state["spin2j1"],
            state["charge3"],
            state["qc"],
            state["qb"],
        )
        for state in states
    )
    return f"""// Generated by tools/generate_registry_artifacts.py. Do not edit.
#ifndef HADRONIZATION_GENERATED_HEAVY_FLAVOUR_REGISTRY_H
#define HADRONIZATION_GENERATED_HEAVY_FLAVOUR_REGISTRY_H

#include <array>
#include <string_view>

namespace Hadronization {{
inline constexpr std::string_view kSpeciesRegistrySchema = {cpp_string(schema)};
inline constexpr std::string_view kSpeciesRegistrySha256 = {cpp_string(sha)};

struct GroundState {{
  int pdg;
  std::string_view name;
  std::string_view sector;
  std::string_view kind;
  int spin2j1;
  int charge3;
  int qc;
  int qb;
}};

inline constexpr std::array<GroundState, {len(states)}> kGroundStates{{{{
{rows}
}}}};

inline const GroundState* FindGroundState(int pdg) {{
  for (const auto& state : kGroundStates) {{
    if (state.pdg == pdg) return &state;
  }}
  return nullptr;
}}
}}  // namespace Hadronization
#endif
"""


def render_pair_header(schema: str, source_sha: str, pair_sha: str, pairs: list[dict]) -> str:
    rows = "\n".join(
        "  {%s, %d, %d, %s, %s, %s, %d, %s},"
        % (
            cpp_string(pair["sector"]),
            pair["trigger_pdg"],
            pair["associate_pdg"],
            cpp_string(pair["heavy_sign"]),
            cpp_string(pair["filename"]),
            cpp_string(pair["associate_kind"]),
            pair["reference_meson_pdg"],
            "true" if pair["legacy_filename"] else "false",
        )
        for pair in pairs
    )
    return f"""// Generated by tools/generate_registry_artifacts.py. Do not edit.
#ifndef HADRONIZATION_GENERATED_PAIR_REGISTRY_H
#define HADRONIZATION_GENERATED_PAIR_REGISTRY_H

#include <array>
#include <string_view>

namespace Hadronization {{
inline constexpr std::string_view kPairRegistrySchema = {cpp_string(schema)};
inline constexpr std::string_view kPairDefinitionSha256 = {cpp_string(source_sha)};
inline constexpr std::string_view kPairRegistrySha256 = {cpp_string(pair_sha)};

struct PairDefinition {{
  std::string_view sector;
  int triggerPdg;
  int associatePdg;
  std::string_view heavySign;
  std::string_view filename;
  std::string_view associateKind;
  int referenceMesonPdg;
  bool legacyFilename;
}};

inline constexpr std::array<PairDefinition, {len(pairs)}> kPairDefinitions{{{{
{rows}
}}}};
}}  // namespace Hadronization
#endif
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail instead of updating stale artifacts")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    species_path = root / "config/heavy_flavour_species_v1.json"
    definition_path = root / "config/pair_registry_definition_v1.json"
    pair_path = root / "config/heavy_flavour_pair_registry_v1.json"
    species_header_path = root / "SimulationScripts/GeneratedHeavyFlavourRegistry.h"
    pair_header_path = root / "AnalysisScripts/GeneratedPairRegistry.h"

    species = json.loads(species_path.read_text())
    definition = json.loads(definition_path.read_text())
    states = species["signed_states"]
    by_pdg = validate_species(states)
    pairs = expanded_pairs(definition, by_pdg)

    expanded = {
        "schema": "heavy_flavour_pair_registry_v1",
        "definition_sha256": digest(definition_path),
        "species_sha256": digest(species_path),
        "pair_count": len(pairs),
        "pairs": pairs,
    }
    pair_text = json.dumps(expanded, indent=2, sort_keys=True) + "\n"
    pair_sha = hashlib.sha256(pair_text.encode()).hexdigest()
    outputs = {
        pair_path: pair_text,
        species_header_path: render_species_header(species["schema"], digest(species_path), states),
        pair_header_path: render_pair_header(expanded["schema"], digest(definition_path), pair_sha, pairs),
    }
    stale = []
    for path, text in outputs.items():
        if not path.exists() or path.read_text() != text:
            stale.append(path)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
    if stale:
        action = "stale" if args.check else "updated"
        print(f"{action}: " + ", ".join(str(path.relative_to(root)) for path in stale))
        return 1 if args.check else 0
    print(f"registry artifacts current: {len(states)} signed states, {len(pairs)} signed pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
