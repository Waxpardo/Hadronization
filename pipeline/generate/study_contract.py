#!/usr/bin/env python3
"""Generate or check the C++ view of the frozen study definition."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "config/study.json"
OUTPUT = ROOT / "pipeline/generate/study_contract.hpp"
REQUIRED_STATE_FIELDS = (
    "pdg", "id", "name", "sector", "kind", "spin2j1", "charge3",
    "qc", "qb", "valence", "pair_analysis_eligible", "status",
)


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def cpp(value):
    return json.dumps(str(value), ensure_ascii=True)


def parse_card(path):
    settings = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].split("!", 1)[0].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in settings:
            raise ValueError("duplicate or empty setting in {}: {}".format(path, key))
        settings[key] = value.strip()
    return settings


def validate(study):
    if study.get("schema") != "hadronization_study_v1":
        raise ValueError("unsupported study schema")
    scope = study.get("scope", {})
    if (scope.get("variation_selection") is not False or
            scope.get("systematic_uncertainty") != "disabled_and_absent"):
        raise ValueError("study must remain nominal and statistical-only")
    states = study.get("selected_states", [])
    if len(states) != 50:
        raise ValueError("selected-state registry must contain 50 states")
    by_id = {}
    by_pdg = {}
    for state in states:
        missing = [field for field in REQUIRED_STATE_FIELDS if field not in state]
        if missing:
            raise ValueError("state is missing fields {}: {}".format(missing, state))
        if state["id"] in by_id or state["pdg"] in by_pdg:
            raise ValueError("selected-state ID/PDG is not unique: {}".format(state))
        by_id[state["id"]] = state
        by_pdg[state["pdg"]] = state
        eligible = state["pair_analysis_eligible"]
        if not isinstance(eligible, bool):
            raise ValueError("pair_analysis_eligible must be boolean")
        expected_status = "pair_analysis" if eligible else "inclusive_only"
        if state["status"] != expected_status:
            raise ValueError("selected-state eligibility/status mismatch: {}".format(state["id"]))
        if not eligible and not state.get("reason"):
            raise ValueError("inclusive-only state lacks a reason: {}".format(state["id"]))

    references = []
    for pair in study["pair_observable"]["balancing_pairs"]:
        for name in ("trigger", "os_associate", "ss_associate"):
            references.append((pair[name], pair[name + "_pdg"], pair["flavour"], "balancing"))
    for species in study["observables"]["inclusive_kinematics"]["species"]:
        references.append((species["id"], species["pdg"], None, "inclusive"))
    for identifier, pdg, flavour, owner in references:
        state = by_id.get(identifier)
        if state is None or state["pdg"] != pdg:
            raise ValueError("dangling or mis-PDG {} state reference: {}/{}".format(
                owner, identifier, pdg))
        if flavour is not None and state["sector"] != flavour:
            raise ValueError("mis-flavour state reference: {}/{}".format(identifier, flavour))
        if owner == "balancing" and not state["pair_analysis_eligible"]:
            raise ValueError("balancing pair uses an ineligible state: {}".format(identifier))

    raw = study.get("raw_input_contract", {})
    expected_raw = {
        "schema": "hf_primary_ground_raw_v7",
        "central_branch": "multiplicity_primary_charged_eta10_v1",
        "wide_branch": "multiplicity_primary_charged_eta40_v1",
        "definition": "primary_charged_light_hadron_level_v1",
        "allowlist_schema": "tune_difference_allowlist_schema",
        "allowlist_sha": "tune_difference_allowlist_sha256",
        "allowlist_schema_value": "pythia_tune_difference_allowlist_v2",
        "allowlist_sha_value": "2b35e52a589ddb488ed4230592203578228425ecac42733f685f90bdd20283c9",
        "species_schema": "heavy_flavour_species_registry_v1",
        "species_sha": "946828956f1b30ae7cb4d28c0c0687e8522b7349db127a067311c77bc3e21529",
    }
    measured = {
        "schema": raw.get("schema"),
        "central_branch": raw.get("multiplicity", {}).get("central_branch"),
        "wide_branch": raw.get("multiplicity", {}).get("wide_branch"),
        "definition": raw.get("multiplicity", {}).get("definition"),
        "allowlist_schema": raw.get("metadata", {}).get(
            "tune_difference_allowlist_schema_branch"),
        "allowlist_sha": raw.get("metadata", {}).get(
            "tune_difference_allowlist_sha256_branch"),
        "allowlist_schema_value": raw.get("metadata", {}).get(
            "tune_difference_allowlist_schema"),
        "allowlist_sha_value": raw.get("metadata", {}).get(
            "tune_difference_allowlist_sha256"),
        "species_schema": raw.get("metadata", {}).get("species_registry_schema"),
        "species_sha": raw.get("metadata", {}).get("species_registry_sha256"),
    }
    if measured != expected_raw:
        raise ValueError("raw-v7 frozen interface drift: {}".format(measured))


def render():
    payload = STUDY.read_bytes()
    study = json.loads(payload.decode("utf-8"))
    validate(study)
    raw = study["raw_input_contract"]
    multiplicity = raw["multiplicity"]
    metadata = raw["metadata"]
    tunes = []
    audited = set()
    for row in study["tunes"]:
        card = ROOT / row["card"]
        settings = parse_card(card)
        audited.update(settings)
        tunes.append((row, sha256_bytes(card.read_bytes())))
    common = study["tune_card_contract"]["common_required_values"]
    allowed_tune = study["tune_card_contract"]["allowed_tune_differences"]
    allowed_job = ("Main:numberOfEvents", "PhaseSpace:pTHatMin",
                   "Random:seed", "Random:setSeed")
    audited.update(common)
    audited.update(allowed_tune)
    audited.update(allowed_job)

    lines = [
        "// Generated by study_contract.py from the exact config/study.json bytes.",
        "// Do not edit; run: python3 pipeline/generate/study_contract.py generate",
        "#ifndef HADRONIZATION_GENERATED_STUDY_CONTRACT_HPP",
        "#define HADRONIZATION_GENERATED_STUDY_CONTRACT_HPP",
        "",
        "#include <array>",
        "#include <string_view>",
        "",
        "namespace Hadronization {",
        "inline constexpr std::string_view kStudyDefinitionSchema = {};".format(
            cpp(study["schema"])),
        "inline constexpr std::string_view kStudyDefinitionSha256 = {};".format(
            cpp(sha256_bytes(payload))),
        "inline constexpr std::string_view kRawSchema = {};".format(cpp(raw["schema"])),
        "inline constexpr std::string_view kRawMultiplicityEta10Branch = {};".format(
            cpp(multiplicity["central_branch"])),
        "inline constexpr std::string_view kRawMultiplicityEta40Branch = {};".format(
            cpp(multiplicity["wide_branch"])),
        "inline constexpr std::string_view kMultiplicityCentral = {};".format(
            cpp(multiplicity["central_object_value"])),
        "inline constexpr std::string_view kMultiplicityCrossCheck = {};".format(
            cpp(multiplicity["wide_object_value"])),
        "inline constexpr std::string_view kMultiplicityDefinitionVersion = {};".format(
            cpp(multiplicity["definition"])),
        "inline constexpr std::string_view kRawTuneAllowlistSchemaBranch = {};".format(
            cpp(metadata["tune_difference_allowlist_schema_branch"])),
        "inline constexpr std::string_view kRawTuneAllowlistSha256Branch = {};".format(
            cpp(metadata["tune_difference_allowlist_sha256_branch"])),
        "inline constexpr std::string_view kTuneDifferenceAllowlistSchema = {};".format(
            cpp(metadata["tune_difference_allowlist_schema"])),
        "inline constexpr std::string_view kTuneDifferenceAllowlistSha256 = {};".format(
            cpp(metadata["tune_difference_allowlist_sha256"])),
        "inline constexpr std::string_view kSpeciesRegistrySchema = {};".format(
            cpp(metadata["species_registry_schema"])),
        "inline constexpr std::string_view kSpeciesRegistrySha256 = {};".format(
            cpp(metadata["species_registry_sha256"])),
        "",
        "struct SelectedState {",
        "  int pdg;",
        "  std::string_view id;",
        "  std::string_view name;",
        "  std::string_view sector;",
        "  std::string_view kind;",
        "  int spin2j1;",
        "  int charge3;",
        "  int qc;",
        "  int qb;",
        "  std::string_view valence;",
        "  bool pairAnalysisEligible;",
        "  std::string_view status;",
        "  std::string_view reason;",
        "};",
        "inline constexpr std::array<SelectedState, {}> kSelectedStates{{{{".format(
            len(study["selected_states"])),
    ]
    for state in study["selected_states"]:
        lines.append("  {{{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}}},".format(
            state["pdg"], cpp(state["id"]), cpp(state["name"]), cpp(state["sector"]),
            cpp(state["kind"]), state["spin2j1"], state["charge3"], state["qc"],
            state["qb"], cpp(state["valence"]),
            "true" if state["pair_analysis_eligible"] else "false",
            cpp(state["status"]), cpp(state.get("reason", ""))))
    lines.extend([
        "}};",
        "inline const SelectedState* FindSelectedState(int pdg) {",
        "  for (const auto& state : kSelectedStates) if (state.pdg == pdg) return &state;",
        "  return nullptr;",
        "}",
        "inline bool IsPairAnalysisEligible(int pdg) {",
        "  const auto* state = FindSelectedState(pdg);",
        "  return state != nullptr && state->pairAnalysisEligible;",
        "}",
        "",
        "struct TuneDefinition { std::string_view name, id, card, sha256; };",
        "inline constexpr std::array<TuneDefinition, {}> kTuneDefinitions{{{{".format(len(tunes)),
    ])
    for row, digest in tunes:
        lines.append("  TuneDefinition{{{}, {}, {}, {}}},".format(
            cpp(row["name"]), cpp(row["id"]), cpp(row["card"]), cpp(digest)))
    lines.append("}};")

    def string_array(name, values):
        lines.append("inline constexpr std::array<std::string_view, {}> {}{{{{".format(
            len(values), name))
        lines.extend("  {},".format(cpp(value)) for value in values)
        lines.append("}};")

    string_array("kAuditedPythiaSettingKeys", sorted(audited))
    string_array("kAllowedTuneDifferenceKeys", allowed_tune)
    string_array("kAllowedPerJobDifferenceKeys", allowed_job)
    lines.extend([
        "struct TuneSettingValue { std::string_view name, value; };",
        "inline constexpr std::array<TuneSettingValue, {}> kCommonRequiredCardValues{{{{".format(
            len(common)),
    ])
    for name in sorted(common):
        lines.append("  TuneSettingValue{{{}, {}}},".format(cpp(name), cpp(common[name])))
    lines.extend(["}};", "}  // namespace Hadronization", "#endif", ""])
    return "\n".join(lines).encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "check"))
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        expected = render()
        if args.command == "generate":
            args.output.write_bytes(expected)
            print("GENERATED {} sha256={}".format(
                args.output.relative_to(ROOT), sha256_bytes(expected)))
            return 0
        actual = args.output.read_bytes()
        if actual != expected:
            print("ERROR: generated study contract is stale: {}".format(args.output),
                  file=sys.stderr)
            return 1
        embedded = re.search(rb'kStudyDefinitionSha256 = "([0-9a-f]{64})"', actual)
        if not embedded or embedded.group(1).decode("ascii") != sha256_bytes(STUDY.read_bytes()):
            print("ERROR: embedded study digest does not match exact bytes", file=sys.stderr)
            return 1
        print("STUDY_CONTRACT_OK study_sha256={}".format(
            sha256_bytes(STUDY.read_bytes())))
        return 0
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
