#!/usr/bin/env python3
"""Declare a shared card setting once, and propagate it everywhere.

config/tune_difference_allowlist_v1.json already lists, under
`common_required_card_values`, every PYTHIA setting that must be identical
across the tune cards -- beam energy, the hard processes, the decay policy,
PhaseSpace:pTHatMin. Until now that list was only ever *checked*: to change one
of those values you edited four cards by hand, then the allowlist, then
discovered the generated registry had gone stale, then discovered the
statistical spec pinned the allowlist's checksum. Each failure was caught, but
only one at a time.

This makes the list the source. Change a value here, run this, and the cards,
the generated registry and the pinned checksum all follow in one step.

  # what would change
  tools/apply_card_config.py --check

  # change the generator threshold everywhere
  tools/apply_card_config.py --set PhaseSpace:pTHatMin=2.5 --apply

Settings NOT in `common_required_card_values` are the ones tunes are allowed
to differ on; this tool will not touch them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "config/tune_difference_allowlist_v1.json"
STATISTICAL_SPEC = ROOT / "config/statistical_robustness_v1.json"
CARD_GLOB = "generation/cards/pythiasettings_Hard_Low_ccbb_*.cmnd"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rewrite_card(card: Path, values: dict[str, str], apply: bool) -> list[str]:
    """Set each declared setting in one card, preserving comments and layout."""
    changes: list[str] = []
    lines = card.read_text().splitlines(keepends=True)
    for index, raw in enumerate(lines):
        body, _, comment = raw.partition("!")
        if "=" not in body:
            continue
        key = body.split("=", 1)[0].strip()
        if key not in values:
            continue
        current = body.split("=", 1)[1].strip()
        wanted = values[key]
        if current == wanted:
            continue
        newline = "\n" if raw.endswith("\n") else ""
        rebuilt = f"{key} = {wanted}"
        if comment:
            # Keep the original column so annotated cards stay readable.
            pad = max(1, len(body.rstrip("\n")) - len(rebuilt))
            rebuilt = rebuilt + " " * pad + "!" + comment.rstrip("\n")
        lines[index] = rebuilt + newline
        changes.append(f"{card.name}: {key} {current} -> {wanted}")
    if changes and apply:
        card.write_text("".join(lines))
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--set", action="append", dest="settings", metavar="KEY=VALUE",
        help="update a common card value in the allowlist, then propagate",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="write the changes; without this, only report them",
    )
    parser.add_argument("--check", action="store_true",
                        help="exit nonzero if any card disagrees")
    args = parser.parse_args()

    allowlist = json.loads(ALLOWLIST.read_text())
    values = dict(allowlist["common_required_card_values"])

    for assignment in args.settings or []:
        key, separator, value = assignment.partition("=")
        key, value = key.strip(), value.strip()
        if not separator or not key or not value:
            raise SystemExit(f"--set expects KEY=VALUE, got {assignment!r}")
        if key not in values:
            raise SystemExit(
                f"{key} is not a common required card value. Settings the "
                "tunes are allowed to differ on are deliberately not managed "
                "here; edit the cards directly."
            )
        if values[key] != value:
            print(f"allowlist: {key} {values[key]} -> {value}")
            values[key] = value

    changes: list[str] = []
    for card in sorted(ROOT.glob(CARD_GLOB)):
        changes.extend(rewrite_card(card, values, args.apply))

    allowlist_changed = values != allowlist["common_required_card_values"]
    if allowlist_changed and args.apply:
        allowlist["common_required_card_values"] = values
        ALLOWLIST.write_text(json.dumps(allowlist, indent=2, sort_keys=True) + "\n")

    for change in changes:
        print(change)
    if not changes and not allowlist_changed:
        print("CARD_CONFIG_CURRENT every card matches the declared values")
        return 0
    if not args.apply:
        print(f"\n{len(changes)} card change(s) pending; re-run with --apply")
        return 1 if args.check else 0

    # The generated registry embeds the card settings, and the statistical spec
    # pins the allowlist's checksum. Both go stale the moment a value changes,
    # and each was previously discovered separately, one test failure at a time.
    subprocess.run(
        [sys.executable, str(ROOT / "tools/generate_registry_artifacts.py")],
        check=True,
    )
    digest = sha256(ALLOWLIST)
    spec = json.loads(STATISTICAL_SPEC.read_text())
    stale = re.sub(
        r'"tune_difference_allowlist_sha256": "[0-9a-f]{64}"',
        f'"tune_difference_allowlist_sha256": "{digest}"',
        STATISTICAL_SPEC.read_text(),
    )
    if stale != STATISTICAL_SPEC.read_text():
        STATISTICAL_SPEC.write_text(stale)
        print(f"statistical spec: allowlist checksum -> {digest}")
    del spec

    print(
        "\nCARD_CONFIG_APPLIED rebuild the producer before submitting: "
        "it embeds the registry checksums."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
