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
# attributed to junction formation. The paper states that limit rather than
# separating the two effects: ruling R32 of 2026-08-30 removed the matched
# fourth tune that would have isolated them, and the check that compared it
# with MONASH went with it.


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
