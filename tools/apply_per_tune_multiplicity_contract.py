#!/usr/bin/env python3
"""Apply/check the authoritative per-tune percentile class contract.

This is a mechanical configuration generator.  It replaces the superseded
MONASH-minimum-bias class names and windows with the PR-13 percentile classes,
and updates every reference to the corresponding histogram object name.

WHAT IT CAN AND CANNOT CHANGE. Ruling R10 makes
`config/multiplicity_percentile_classes_v2.json` the one source of the class
set. This tool applies a changed LABEL, a changed WINDOW and a changed BIN name
to every tracked configuration. It does NOT change the class COUNT: it rewrites
one configuration entry per contract class and cannot invent the style, the
axis range or the legend slot a new entry would need. A count mismatch is
refused by name, never applied in part and never reported as CURRENT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# The THIRD writer of display_name on these documents. The precision constant
# and the formatting function live in one module so two owners cannot render the
# same percentile differently (ledger DA1-A021): this file used to carry its own
# ':g' expression, which agrees with the shared '%.0f' on every integral edge
# and disagrees on a non-integral one -- 59.8 prints as '59.8' under ':g' and
# '60' under the contract's own precision. Every contract edge is integral
# today, so the two never diverged in the tree; the import removes the way they
# could.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from class_label_format import format_percentile_range  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config" / "multiplicity_percentile_classes_v2.json"
# The statistical spec pins the sha256 of one plotting configuration this tool
# rewrites. A pin left stale after a class change stops the suite one test
# later, in a file that names no class, so this tool carries the pin.
STATISTICAL_SPEC = ROOT / "config" / "statistical_robustness_v1.json"
PIN_KEY = "boundary_configuration_sha256"
PATH_KEY = "boundary_configuration_path"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned_configuration_drift(apply: bool) -> list[str]:
    """Keep the statistical spec's boundary-configuration pin current.

    Returns the drift it found. With `apply` false it only reports, so
    `--check` can fail on a stale pin rather than leave it for a later test.
    """
    if not STATISTICAL_SPEC.is_file():
        return []
    raw = STATISTICAL_SPEC.read_text()
    spec = json.loads(raw)
    relative = spec.get("contracts", {}).get(PATH_KEY)
    recorded = spec.get("contracts", {}).get(PIN_KEY)
    if not relative or not recorded:
        return []
    target = ROOT / relative
    if not target.is_file():
        return [f"{STATISTICAL_SPEC.name}: {PATH_KEY} names no file: {relative}"]
    current = sha256(target)
    if current == recorded:
        return []
    if apply:
        STATISTICAL_SPEC.write_text(
            re.sub(f'"{PIN_KEY}": "[0-9a-f]{{64}}"',
                   f'"{PIN_KEY}": "{current}"', raw))
    return [f"{STATISTICAL_SPEC.name}: {PIN_KEY} is {recorded[:12]}..., "
            f"{relative} hashes to {current[:12]}..."]


def indent_of(text: str) -> int:
    for line in text.splitlines()[1:]:
        stripped = line.lstrip(" ")
        if stripped and stripped != "}":
            return len(line) - len(stripped)
    return 2


class ClassCountMismatch(Exception):
    """The document holds a different number of classes than the contract.

    This generator RENAMES and RE-WINDOWS a class entry; it does not create or
    delete one. A count change therefore needs one hand-authored entry per new
    class in the configuration before this tool can run. Returning the document
    unchanged would have reported CURRENT for a configuration the contract no
    longer describes, so the mismatch is a refusal.
    """


def class_rows(document: dict) -> list[dict]:
    """The class entries of a configuration, the integrated bin excluded."""
    bins = document.get("histograms_to_analyse", [])
    return [row for row in bins if row.get("hDPhi") != "hDPhiM00_100"]


def replacement_table(document: dict, classes: list[dict]) -> dict[str, str]:
    class_bins = class_rows(document)
    if not class_bins:
        return {}
    if len(class_bins) != len(classes):
        raise ClassCountMismatch(
            f"the configuration carries {len(class_bins)} classes and "
            f"{CONTRACT.name} declares {len(classes)}. This tool renames "
            "classes; it does not add or remove them.")
    replacements: dict[str, str] = {}
    for old, new in zip(class_bins, classes):
        replacements[str(old["binLabel"])] = str(new["bin"])
        replacements[str(old["hDPhi"])] = "hDPhi" + str(new["bin"])
        replacements[str(old["hTrPt"])] = "hTrPt" + str(new["bin"])
    return replacements


def replace_strings(value, replacements: dict[str, str]):
    if isinstance(value, dict):
        return {key: replace_strings(item, replacements)
                for key, item in value.items()}
    if isinstance(value, list):
        return [replace_strings(item, replacements) for item in value]
    if isinstance(value, str):
        return replacements.get(value, value)
    return value


def build(document: dict, classes: list[dict]) -> dict:
    replacements = replacement_table(document, classes)
    if not replacements:
        return document
    result = replace_strings(document, replacements)
    result["_comment_axis"] = (
        "Multiplicity classes are tune-local top-percentile classes from "
        "config/multiplicity_percentile_classes_v2.json. Each tune resolves "
        "multiplicityMin/multiplicityMax from its own merged summed "
        "MULTIPLICITY histogram. Absolute N_ch thresholds may differ across "
        "tunes; no MONASH minimum-bias sample defines this axis."
    )
    if result.get("label_owner") != "tools/make_variant_configs.py":
        result["label_owner"] = (
            "tools/apply_per_tune_multiplicity_contract.py")
    class_by_bin = {row["bin"]: row for row in classes}
    for row in result["histograms_to_analyse"]:
        if row.get("hDPhi") == "hDPhiM00_100":
            continue
        contract = class_by_bin[row["binLabel"]]
        row["multiplicityMin"] = contract["percentile_min"]
        row["multiplicityMax"] = contract["percentile_max"]

    labels = {
        "hDPhi" + row["bin"]: format_percentile_range(
            row["percentile_min"], row["percentile_max"])
        for row in classes
    }

    def update_labels(node) -> None:
        if isinstance(node, dict):
            if node.get("object_name") in labels:
                node["display_name"] = labels[node["object_name"]]
            for item in node.values():
                update_labels(item)
        elif isinstance(node, list):
            for item in node:
                update_labels(item)

    if result.get("label_owner") != "tools/make_variant_configs.py":
        update_labels(result)
    return result


def candidate_paths() -> list[Path]:
    paths = sorted((ROOT / "plotting").glob("configuration_*.json"))
    paths += sorted((ROOT / "plotting" / "harvest_configs").glob("*.json"))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()
    classes = json.loads(CONTRACT.read_text())["classes"]
    stale: list[Path] = []
    changed: list[Path] = []
    for path in args.paths or candidate_paths():
        raw = path.read_text()
        document = json.loads(raw)
        try:
            generated = build(document, classes)
        except ClassCountMismatch as error:
            print(f"PER_TUNE_MULTIPLICITY_REFUSED {path.relative_to(ROOT)}: "
                  f"{error}")
            return 2
        payload = json.dumps(generated, indent=indent_of(raw)) + "\n"
        if payload == raw:
            continue
        if args.check:
            stale.append(path)
        else:
            path.write_text(payload)
            changed.append(path)
    pin = pinned_configuration_drift(apply=not args.check)
    if stale or (pin and args.check):
        for path in stale:
            print(f"PER_TUNE_MULTIPLICITY_STALE {path.relative_to(ROOT)}")
        for line in pin:
            print(f"PER_TUNE_MULTIPLICITY_STALE_PIN {line}")
        return 1
    for line in pin:
        print(f"PER_TUNE_MULTIPLICITY_PIN_REFRESHED {line}")
    print(
        "PER_TUNE_MULTIPLICITY_CURRENT"
        if args.check else
        f"PER_TUNE_MULTIPLICITY_APPLIED files={len(changed)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
