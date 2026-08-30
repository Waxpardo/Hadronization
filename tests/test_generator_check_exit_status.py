#!/usr/bin/env python3
"""Every generator's --check must be SEEN to fail, not merely fail.

THE FIRST DEFECT THIS CLOSES. `--check` returns non-zero correctly, but every
place it was read did so through a pipe:

    python3 tools/apply_class_labels.py --check | tail -3   # $? is tail's

`$?` after a pipeline is the LAST command's status, so a failing check reported
success three separate times. A check that cannot be observed to fail is not a
check, and the shape is easy to reintroduce because the pipeline reads
naturally.

THE SECOND DEFECT (ledger DA1-046). This driver's docstring claimed it ran
"each generator" while GENERATORS was a fixed two-entry list. The deep audit
measured ELEVEN project generators that accept a bare `--check`; nine of them
had no negative control here, so one whose `--check` silently stopped detecting
drift would have stayed green.

HOW THE SCOPE IS NOW HELD. `GENERATORS` below is the one declared inventory, and
`discover_generators()` finds every tracked tool that declares a `--check`
argparse flag. The two sets are asserted EQUAL, so a new generator fails this
test until it is declared with a mutation, and a retired one fails until it is
removed. The tool that declares `--check` only under a subcommand is named in
the declared exclusion, with the reason.

Each generator carries ONE mutation, chosen as a real drift in an artifact that
generator owns, and each must move `--check` from 0 to non-zero.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The declared inventory: name -> (generator, owned artifact, mutation, why).
#
# The mutation is a substring replacement in the artifact's RAW TEXT, so a
# reformat cannot masquerade as the edit. Each target is a value the generator
# derives, so restoring it is the generator's job and detecting it is --check's.
GENERATORS: dict[str, dict] = {
    "make_hf_run3_v1_three_tune_config": {
        "generator": "plotting/make_hf_run3_v1_three_tune_config.py",
        "artifact": ("plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE"
                     "_THnSparse_complete_root.json"),
        "find": '"y_min_axis"',
        "replace": '"y_min_axis_DRIFTED"',
        "why": "a physics-facing key the generator writes on every canvas",
    },
    "make_variant_configs": {
        "generator": "tools/make_variant_configs.py",
        "artifact": "plotting/configuration_multiplicity_HF_RUN3_V1_VEXTREMES.json",
        "find": '"TriggerToUse"',
        "replace": '"TriggerToUse_DRIFTED"',
        "why": "the trigger each variant mini selects on",
    },
    "apply_class_labels": {
        "generator": "tools/apply_class_labels.py",
        "artifact": ("plotting/configuration_multiplicity_HF_RUN3_V1_MONASH"
                     "_THnSparse_complete_root.json"),
        "find": '"display_name"',
        "replace": '"display_name_DRIFTED"',
        "why": "the class label field this generator owns",
    },
    "apply_per_tune_multiplicity_contract": {
        "generator": "tools/apply_per_tune_multiplicity_contract.py",
        "artifact": "config/multiplicity_percentile_classes_v2.json",
        "find": '"percentile_min"',
        "replace": '"percentile_min_DRIFTED"',
        "why": "the per-tune class contract this tool propagates",
    },
    "apply_card_config": {
        "generator": "tools/apply_card_config.py",
        "artifact": "config/tune_difference_allowlist_v1.json",
        "find": '"common_required_card_values"',
        "replace": '"common_required_card_values_DRIFTED"',
        "why": "the declared common-value list this tool is the source of",
    },
    "make_systematic_cards": {
        "generator": "tools/make_systematic_cards.py",
        "artifact": ("generation/cards/systematics/"
                     "pythiasettings_Hard_Low_ccbb_MONASH__mur_up.cmnd"),
        "find": "SigmaProcess:renormMultFac",
        "replace": "SigmaProcess:renormMultFac_DRIFTED",
        "why": "the one setting this variation card exists to change",
    },
    "make_harvest_configs": {
        "generator": "tools/make_harvest_configs.py",
        "artifact": ("plotting/harvest_configs/configuration_multiplicity_"
                     "HF_SYS_MUR_UP_THREETUNE_THnSparse_complete_root.json"),
        "find": '"PYTHIA_TUNES"',
        "replace": '"PYTHIA_TUNES_DRIFTED"',
        "why": "the tune list each harvest configuration is derived with",
    },
    "generate_registry_artifacts": {
        "generator": "tools/generate_registry_artifacts.py",
        "artifact": "config/heavy_flavour_pair_registry_v1.json",
        "find": '"reference_meson_pdg"',
        "replace": '"reference_meson_pdg_DRIFTED"',
        "why": "the signed reference meson every pair identity resolves through",
    },
    "generate_pair_object_contract": {
        "generator": "tools/generate_pair_object_contract.py",
        "artifact": "config/pair_file_object_contract_v1.json",
        "find": '"schema"',
        "replace": '"schema_DRIFTED"',
        "why": "the contract's own schema declaration",
    },
    "generate_species_ordinals_header": {
        "generator": "tools/generate_species_ordinals_header.py",
        "artifact": "contracts/GeneratedSpeciesOrdinals.h",
        "find": "HADRONIZATION_GENERATED_SPECIES_ORDINALS_H",
        "replace": "HADRONIZATION_GENERATED_SPECIES_ORDINALS_H_DRIFTED",
        "why": "the include guard of the generated header the macro includes",
    },
    "make_strict_control_fixtures": {
        "generator": "tools/make_strict_control_fixtures.py",
        "artifact": "tests/fixtures/strict_control/nominal_144.log",
        "find": "tag=complete_root_HF_RUN3_V1",
        "replace": "tag=complete_root_HF_SYS_MUR_UP",
        "why": ("the campaign tag this generator writes into every resolver "
                "line, and the line DA1-031's resolver assertion reads"),
    },
    "normalize_site_paths": {
        "generator": "tools/normalize_site_paths.py",
        "artifact": "plotting/configuration_multiplicity_HF_RUN3_V1_VINTEGRATED.json",
        "find": "${HADRONIZATION_DATA_ROOT}",
        "replace": "/data/alice/ipardoza/hf",
        "why": ("a site-portable path put back to the Nikhef absolute form "
                "this tool exists to remove"),
    },
}

# Declares a `--check` flag only under a subcommand, so a bare `--check` is an
# argparse usage error rather than a currency report. Named here so the
# discovery stays exact instead of being loosened to let it through.
NOT_BARE_CHECK = {"tools/pdg_2025_species_audit.py"}

CHECK_FLAG = re.compile(r'add_argument\(\s*\n?\s*"--check"')


def discover_generators() -> set[str]:
    """Every tracked Python tool that declares a `--check` argparse flag."""
    listed = subprocess.run(["git", "ls-files", "*.py"], cwd=str(ROOT),
                            text=True, capture_output=True, check=True)
    return {name for name in listed.stdout.split()
            if CHECK_FLAG.search((ROOT / name).read_text())}


def check_status(generator: Path, cwd: Path) -> int:
    """Status taken straight from the process. No pipe, no shell."""
    completed = subprocess.run(
        [sys.executable, str(generator), "--check"],
        cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    return completed.returncode


def piped_status(generator: Path, cwd: Path) -> int:
    """The WRONG way, kept so the hazard is demonstrated and not just described."""
    completed = subprocess.run(
        f"{sys.executable} {generator} --check | tail -1",
        cwd=str(cwd), shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    return completed.returncode


def test_the_tested_set_is_the_whole_inventory() -> list[str]:
    """DA1-046: the scope this driver claims must be the scope it has."""
    declared = {entry["generator"] for entry in GENERATORS.values()}
    discovered = discover_generators() - NOT_BARE_CHECK
    failures = []
    for missing in sorted(discovered - declared):
        failures.append(
            f"{missing} declares --check and is not covered here; add it to "
            f"GENERATORS with a mutation, or to NOT_BARE_CHECK with a reason")
    for stale in sorted(declared - discovered):
        failures.append(
            f"{stale} is declared here but no longer declares --check")
    for name in sorted(NOT_BARE_CHECK):
        if not (ROOT / name).exists():
            failures.append(f"{name} is excluded here but is not in the tree")
    return failures


def test_every_generator_is_clean_in_the_committed_tree() -> list[str]:
    failures = []
    for name, entry in sorted(GENERATORS.items()):
        rc = check_status(ROOT / entry["generator"], ROOT)
        if rc != 0:
            failures.append(
                f"{name} --check exits {rc} in the committed tree; expected 0")
    return failures


def mutate_and_check(name: str, entry: dict, sandbox: Path) -> list[str]:
    """One justified drift per generator; --check must go non-zero on it."""
    failures: list[str] = []
    generator = sandbox / entry["generator"]
    target = sandbox / entry["artifact"]

    if not target.exists():
        return [f"{name}: owned artifact {entry['artifact']} is absent"]
    if check_status(generator, sandbox) != 0:
        failures.append(
            f"{name}: the sandbox is not clean before the mutation, so the "
            f"detection below would be meaningless")

    original = target.read_text()
    if entry["find"] not in original:
        return failures + [
            f"{name}: {entry['artifact']} no longer carries "
            f"{entry['find']!r} ({entry['why']}); pick a live mutation target"]

    target.write_text(original.replace(entry["find"], entry["replace"], 1))
    try:
        direct = check_status(generator, sandbox)
        if direct == 0:
            failures.append(
                f"{name}: --check exited 0 on a mutated {entry['artifact']}; a "
                f"failing check that reports success is the whole defect")

        # THE POINT. The same failing check, read through a pipe, reports
        # success, so any caller that pipes is blind to it.
        piped = piped_status(generator, sandbox)
        if direct != 0 and piped == direct:
            failures.append(
                f"{name}: expected the piped status ({piped}) to differ from "
                f"the direct one ({direct}); if they now agree this test no "
                f"longer demonstrates the hazard it exists for")
        elif direct != 0 and piped != 0:
            failures.append(
                f"{name}: piped status was {piped}, expected 0 (tail's success)")
    finally:
        target.write_text(original)
    return failures


CLASS_LABEL = re.compile(
    r'("display_name"\s*:\s*")(?P<value>[^"]*?\d[^"]*%)(")')


def corrupt_text(text: str) -> str | None:
    """Hand-edit the first class label IN THE RAW TEXT, preserving formatting.

    A JSON round-trip would reformat the file, and this test has to be able to
    tell a reformat from a label edit. So the corruption is a substitution
    inside one line and nothing else moves.
    """
    match = CLASS_LABEL.search(text)
    if not match:
        return None
    return text[:match.start()] + match.group(1) + "99.9-99.9%" + \
        match.group(3) + text[match.end():]


def rewrites_only_labels(name: str, gen: Path, sandbox: Path,
                         target: Path) -> list[str]:
    """Correcting a label must restore the file BYTE FOR BYTE, not reformat it.

    THE DEFECT THIS CLOSES. `apply_class_labels.py` wrote every file it touched
    with `indent=4`, while the configurations it owns are committed at 1, 2 and
    4 spaces. Correcting twenty-four labels therefore rewrote 4456 lines,
    changed every configuration's sha256 -- which the multiplicity boundary
    receipts record -- and made `make_hf_run3_v1_three_tune_config.py --check`
    fail, because that generator writes the same file at `indent=1`.

    NEITHER `--check` NOR A CLEAN-TREE RUN CATCHES THIS. The labels were right,
    so `--check` exits 0; and the generator writes only when it finds drift, so
    on a clean tree it never opens the file for writing at all. The defect lives
    exactly in the write path, and only a run that HAS something to correct
    reaches it.

    So: hand-edit one label, run the generator for real, and require the file to
    come back identical to what it was. Any reformatting shows up as a
    difference even though every label is once again correct.
    """
    original = target.read_bytes()
    damaged = corrupt_text(original.decode())
    if damaged is None:
        return [f"{name}: could not find a class label to corrupt"]
    target.write_text(damaged)

    subprocess.run([sys.executable, str(gen)], cwd=str(sandbox),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    restored = target.read_bytes()
    target.write_bytes(original)

    if restored == original:
        return []
    if json.loads(restored) == json.loads(original):
        return [f"{name}: the generator restored every label but REFORMATTED "
                f"{target.name} ({len(original)} bytes in, {len(restored)} "
                f"out); a label correction must move labels and nothing else"]
    return [f"{name}: the generator did not restore {target.name}"]


# The two label-owning generators, where the byte-for-byte rewrite check
# applies. The other nine own artifacts that carry no class labels.
LABEL_OWNERS = {
    "apply_class_labels":
        "plotting/configuration_multiplicity_HF_RUN3_V1_MONASH"
        "_THnSparse_complete_root.json",
    "make_variant_configs":
        "plotting/configuration_multiplicity_HF_RUN3_V1_VEXTREMES.json",
}


def main() -> int:
    failures: list[str] = []
    failures += test_the_tested_set_is_the_whole_inventory()
    failures += test_every_generator_is_clean_in_the_committed_tree()

    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp) / "repo"
        subprocess.run(["cp", "-R", str(ROOT), str(sandbox)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for name, entry in sorted(GENERATORS.items()):
            failures += mutate_and_check(name, entry, sandbox)
        for name, artifact in sorted(LABEL_OWNERS.items()):
            failures += rewrites_only_labels(
                name,
                sandbox / GENERATORS[name]["generator"],
                sandbox,
                sandbox / artifact)

    if failures:
        for line in failures:
            print("FAIL: " + line)
        return 1
    print(f"check statuses: {len(GENERATORS)} generators -- the whole "
          f"discovered inventory -- each clean in the committed tree and each "
          f"detecting one justified drift directly (non-zero) while a pipe "
          f"MASKS it (0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
