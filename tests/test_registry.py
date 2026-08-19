#!/usr/bin/env python3
import copy
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import generate_registry_artifacts as registry_generator  # noqa: E402


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "tools/generate_registry_artifacts.py"), "--check"],
        check=True,
    )
    species = json.loads((ROOT / "config/heavy_flavour_species_v1.json").read_text())
    pairs = json.loads((ROOT / "config/heavy_flavour_pair_registry_v1.json").read_text())
    states = {int(row["pdg"]): row for row in species["signed_states"]}
    definition = json.loads(
        (ROOT / "config/pair_registry_definition_v1.json").read_text()
    )
    validated_states = registry_generator.validate_species(
        species["signed_states"]
    )

    assert len(states) == 50
    assert states[4312]["name"] != states[4132]["name"]
    assert states[5322]["name"] != states[5232]["name"]
    assert states[541]["qc"] == 1 and states[541]["qb"] == -1
    assert states[-541]["qc"] == -1 and states[-541]["qb"] == 1
    assert all(abs(row["spin2j1"]) in {1, 2} for row in states.values())

    expanded = pairs["pairs"]
    assert pairs["pair_count"] == len(expanded) == 300
    assert len({row["filename"] for row in expanded}) == len(expanded)
    corrected = next(
        row for row in expanded
        if row["trigger_pdg"] == 511 and row["associate_pdg"] == 5212
    )
    assert corrected["filename"] == "BzeroSigmabzero.root"
    assert corrected["heavy_sign"] == "OS"
    assert any(row["trigger_pdg"] == -411 for row in expanded)
    assert any(row["associate_pdg"] == 4322 for row in expanded)
    assert any(row["associate_pdg"] == 5322 for row in expanded)
    duplicate_trigger = copy.deepcopy(definition)
    duplicate_trigger["central_triggers"]["charm"].append(411)
    try:
        registry_generator.expanded_pairs(
            duplicate_trigger, validated_states
        )
    except ValueError as error:
        assert "duplicate charm central trigger" in str(error)
    else:
        raise AssertionError("duplicate central trigger was accepted")

    wrong_reference = copy.deepcopy(definition)
    wrong_reference["reference_mesons"]["411"] = -521
    try:
        registry_generator.expanded_pairs(
            wrong_reference, validated_states
        )
    except ValueError as error:
        assert "missing signed reference meson" in str(error)
    else:
        raise AssertionError("cross-sector reference meson was accepted")

    same_sign_reference = copy.deepcopy(definition)
    same_sign_reference["reference_mesons"]["411"] = 411
    try:
        registry_generator.expanded_pairs(
            same_sign_reference, validated_states
        )
    except ValueError as error:
        assert "opposite signed charm content" in str(error)
    else:
        raise AssertionError("same-sign reference meson was accepted")
    registry_filenames = {row["filename"] for row in expanded}
    for config_name in (
        "configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json",
        "configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json",
    ):
        config = json.loads((ROOT / "plotting" / config_name).read_text())
        referenced: set[str] = set()

        def collect(value: object) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    if key in {"OS", "SS"} and isinstance(item, str):
                        referenced.add(item)
                    collect(item)
            elif isinstance(value, list):
                for item in value:
                    collect(item)

        collect(config)
        missing = referenced - registry_filenames
        assert not missing, f"{config_name} references unregistered files: {missing}"
        assert config["pair_combinatorics_mode"] == "ordered_conditional_v1"
        assert config["same_sign_pair_factor"] == 1.0
        assert config["calculate_errors"] is True
        assert config["nSubSamples"] == 10
        assert config["subsample_error_bins_to_exclude"] == []
    print("registry tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
