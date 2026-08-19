#!/usr/bin/env python3
"""Validate explicit card keys against the versioned tune-difference allowlist."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from campaign import PUBLISHED_TUNES  # noqa: E402

TUNES = PUBLISHED_TUNES

# JUNCTIONS retunes the Lund and diquark parameters away from Monash, which is
# why a MONASH/JUNCTIONS difference in a baryon observable cannot on its own be
# attributed to junction formation.
#
# JUNCTIONS_MATCHED carries the QCD-CR junction machinery on Monash
# fragmentation, so that a MONASH-vs-JUNCTIONS_MATCHED difference is
# attributable to colour reconnection rather than to the fragmentation retune
# the published JUNCTIONS tune also applies.
#
# The card is built by DELETING the JUNCTIONS fragmentation overrides, not by
# restating Monash numbers, so both cards inherit those values from
# Tune:pp = 14. The check below is therefore the real one: MONASH and
# JUNCTIONS_MATCHED must differ by nothing except these keys.
MATCHED_TUNE = "JUNCTIONS_MATCHED"
MATCHED_ALLOWED_DIFFERENCES = {
    "BeamRemnants:remnantMode",
    "BeamRemnants:saturation",
    "ColourReconnection:mode",
    "ColourReconnection:allowDoubleJunRem",
    "ColourReconnection:m0",
    "ColourReconnection:allowJunctions",
    "ColourReconnection:junctionCorrection",
    "ColourReconnection:timeDilationMode",
    "ColourReconnection:timeDilationPar",
}


def parse_card(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.split("!", 1)[0].strip()
        if not line:
            continue
        if "=" not in line:
            raise ValueError(f"{path}:{number}: non-comment line lacks '='")
        key, value = (part.strip() for part in line.split("=", 1))
        if key in values:
            raise ValueError(f"{path}:{number}: duplicate key {key}")
        values[key] = value
    return values


def check_matched_tune(root: Path) -> None:
    """MONASH and JUNCTIONS_MATCHED may differ only in the CR machinery."""
    def card(name: str) -> dict[str, str]:
        return parse_card(
            root / "generation" / "cards" / f"pythiasettings_Hard_Low_ccbb_{name}.cmnd"
        )

    monash, matched = card("MONASH"), card(MATCHED_TUNE)
    keys = set(monash) | set(matched)
    differing = {key for key in keys if monash.get(key) != matched.get(key)}
    unexpected = differing - MATCHED_ALLOWED_DIFFERENCES
    if unexpected:
        raise ValueError(
            f"{MATCHED_TUNE} differs from MONASH outside the colour-reconnection "
            f"machinery: {sorted(unexpected)}. The attribution argument for this "
            "card depends on that set being empty."
        )
    # Anything the published JUNCTIONS tune retunes must be ABSENT here, so it
    # is inherited from Tune:pp = 14 exactly as MONASH inherits it.
    junctions = card("JUNCTIONS")
    retuned = {
        key
        for key in junctions
        if key.startswith(("StringZ:", "StringPT:", "StringFlav:"))
        or key == "MultipartonInteractions:pT0Ref"
    }
    leaked = retuned & set(matched)
    if leaked:
        raise ValueError(
            f"{MATCHED_TUNE} restates tuned parameters instead of inheriting them "
            f"from Tune:pp: {sorted(leaked)}"
        )
    print(
        f"TUNE_MATCHED_OK {MATCHED_TUNE} differs from MONASH only in "
        f"{len(differing)} colour-reconnection/beam-remnant keys; "
        f"{len(retuned)} tuned parameters inherited from Tune:pp"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    allowlist = json.loads(
        (root / "config/tune_difference_allowlist_v1.json").read_text()
    )
    cards = {
        tune: parse_card(
            root
            / "generation" / "cards"
            / f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
        )
        for tune in TUNES
    }
    for key, expected in allowlist["common_required_card_values"].items():
        observed = {tune: cards[tune].get(key) for tune in TUNES}
        if any(value != expected for value in observed.values()):
            raise ValueError(f"required common setting {key}: {observed}, expected {expected}")
    allowed = set(allowlist["allowed_tune_differences"])
    all_keys = set().union(*(card.keys() for card in cards.values()))
    actual_differences: set[str] = set()
    for key in all_keys:
        values = tuple(cards[tune].get(key, "<PYTHIA_DEFAULT>") for tune in TUNES)
        if len(set(values)) > 1:
            actual_differences.add(key)
            if key not in allowed:
                raise ValueError(f"non-allowlisted tune difference {key}: {values}")
    unused = allowed - actual_differences
    if unused:
        raise ValueError(f"allowlist entries are not actual card differences: {sorted(unused)}")
    check_matched_tune(root)
    print(
        "TUNE_CARD_ALLOWLIST_VALID "
        f"keys={len(all_keys)} differences={len(actual_differences)}"
    )
    for key in sorted(actual_differences):
        print(
            "TUNE_CARD_DIFFERENCE "
            + key
            + " "
            + " ".join(f"{tune}={cards[tune].get(key, '<PYTHIA_DEFAULT>')}" for tune in TUNES)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
