#!/usr/bin/env python3
"""Generate the systematics variation cards from the nominal tune cards.

A variation is the nominal card with EXACTLY ONE setting changed. That is the
whole contract, and this tool exists to enforce it rather than to save typing:
a hand-edited variation card is a card whose difference from the nominal nobody
has checked, and the failure mode -- a variation that quietly also changed
something else, or that quietly changed nothing -- looks exactly like a physics
result.

  tools/make_systematic_cards.py --check    # are the cards on disk current?
  tools/make_systematic_cards.py            # write them

Declared in config/systematics_variations_v1.json. Nothing here decides what
gets varied; this file decides only how the card is written and what must be
true of it afterwards.

The checks, each of which can fail:

  * the varied key must be one the producer will accept -- either declared in
    config/systematic_variation_settings_v1.json or already classified by the
    tune allowlist. Otherwise the producer throws "configured setting is absent
    from tune allowlist" on a worker node, 300 jobs into a campaign;
  * EVERY key in the generated card must be in the audited union, for the same
    reason;
  * the generated card must differ from its nominal in exactly one key, and
    that key must carry the declared value. This is the pre-registration's
    positive check 10.2 enforced at generation time instead of after the fact;
  * the declared value must differ from what the nominal resolves to, so a
    "variation" that varies nothing cannot be written at all.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from campaign import (  # noqa: E402
    CARD_VARIANT_TOKEN,
    PUBLISHED_TUNES,
    resolve_card_path,
)

BANNER_RULE = "! " + "=" * 68


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_card(text: str, label: str) -> dict[str, str]:
    """Key -> value for every non-comment assignment. Duplicates are fatal."""
    values: dict[str, str] = {}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.split("!", 1)[0].strip()
        if not line:
            continue
        if "=" not in line:
            raise ValueError(f"{label}:{number}: non-comment line lacks '='")
        key, value = (part.strip() for part in line.split("=", 1))
        if key in values:
            raise ValueError(f"{label}:{number}: duplicate key {key}")
        values[key] = value
    return values


def audited_keys(root: Path) -> set[str]:
    """The keys the producer will accept in a card.

    Read from the same two JSON files the generated registry header is built
    from, so this tool cannot disagree with the binary about what is legal.
    """
    allowlist = json.loads(
        (root / "config/tune_difference_allowlist_v1.json").read_text()
    )
    variations = json.loads(
        (root / "config/systematic_variation_settings_v1.json").read_text()
    )
    return (
        set(allowlist["common_required_card_values"])
        | set(allowlist["allowed_tune_differences"])
        | set(allowlist["allowed_per_job_differences"])
        | {str(entry["name"]) for entry in variations["settings"]}
    )


def variation_settings(root: Path) -> set[str]:
    variations = json.loads(
        (root / "config/systematic_variation_settings_v1.json").read_text()
    )
    return {str(entry["name"]) for entry in variations["settings"]}


def render_card(
    nominal_text: str,
    nominal_sha: str,
    nominal_name: str,
    variation: dict,
) -> str:
    """The nominal card, with one setting set, under a generated banner."""
    setting = str(variation["setting"])
    value = str(variation["value"])

    lines = nominal_text.splitlines(keepends=True)
    replaced = False
    for index, raw in enumerate(lines):
        body, separator, comment = raw.partition("!")
        if "=" not in body:
            continue
        if body.split("=", 1)[0].strip() != setting:
            continue
        if replaced:
            raise ValueError(f"{nominal_name}: {setting} appears twice")
        newline = "\n" if raw.endswith("\n") else ""
        rebuilt = f"{setting} = {value}"
        if separator:
            # Keep the nominal's own comment: it documents the NOMINAL choice,
            # and the banner says so. Deleting it would erase the reasoning
            # this variation is a variation OF.
            rebuilt = f"{rebuilt}   !{comment.rstrip()}"
        lines[index] = rebuilt + newline
        replaced = True

    banner = [
        BANNER_RULE,
        "! GENERATED SYSTEMATICS VARIATION -- DO NOT EDIT",
        "!",
        "! tools/make_systematic_cards.py, from",
        f"!   generation/cards/{nominal_name}",
        f"!   sha256 {nominal_sha}",
        "!",
        f"! variation : {variation['name']}   ({variation['source']})",
        f"! setting   : {setting} = {value}",
        f"! nominal   : {variation['nominal_value']}",
        "!",
        "! This card differs from the nominal by EXACTLY ONE setting, which the"
        " generator",
        "! asserts rather than assumes. Registered in"
        " docs/SYSTEMATICS_PREREGISTRATION.md",
        f"! {variation['source']}. Where the nominal card carried a comment on"
        " the changed",
        "! setting, that comment is left in place and describes the NOMINAL"
        " choice.",
        BANNER_RULE,
        "",
    ]

    body_text = "".join(lines)
    if not replaced:
        # Absent from the nominal, so the nominal is the PYTHIA default and the
        # setting is appended. Mirrors campaign.py's append-if-missing rewrite.
        if not body_text.endswith("\n"):
            body_text += "\n"
        body_text += (
            f"\n! --- systematics variation {variation['name']}:"
            f" absent from the nominal card, so the nominal is the PYTHIA"
            f" default ---\n"
            f"{setting} = {value}\n"
        )
    return "\n".join(banner) + body_text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--check", action="store_true",
        help="exit nonzero if any card is stale or absent, and write nothing",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    declared = json.loads(
        (root / "config/systematics_variations_v1.json").read_text()
    )
    legal = audited_keys(root)
    variation_only = variation_settings(root)

    names = [str(entry["name"]) for entry in declared["variations"]]
    if len(set(names)) != len(names):
        raise ValueError("duplicate variation name")
    ordinals = [int(entry["campaign_ordinal"]) for entry in declared["variations"]]
    if len(set(ordinals)) != len(ordinals):
        raise ValueError("two variations claim the same campaign ordinal")
    campaigns = [str(entry["campaign"]) for entry in declared["variations"]]
    if len(set(campaigns)) != len(campaigns):
        raise ValueError("two variations claim the same campaign name")

    stale: list[Path] = []
    written = 0
    for variation in declared["variations"]:
        name = str(variation["name"])
        setting = str(variation["setting"])
        value = str(variation["value"])
        if not CARD_VARIANT_TOKEN.fullmatch(name):
            raise ValueError(f"variation name is not a valid token: {name!r}")
        if setting not in legal:
            raise ValueError(
                f"{name}: {setting} is not a key the producer will accept. Add "
                "it to config/systematic_variation_settings_v1.json and "
                "regenerate the registry artifacts."
            )
        for tune in PUBLISHED_TUNES:
            nominal_path = resolve_card_path(root, tune, None)
            nominal_text = nominal_path.read_text()
            nominal = parse_card(nominal_text, nominal_path.name)

            if setting in nominal and nominal[setting] == value:
                raise ValueError(
                    f"{name}/{tune}: {setting} already is {value} in the "
                    "nominal card, so this varies nothing"
                )
            if setting not in nominal and setting not in variation_only:
                raise ValueError(
                    f"{name}/{tune}: {setting} is absent from the nominal card "
                    "and is not declared a systematic variation setting, so "
                    "the nominal value it varies is unrecorded"
                )

            text = render_card(
                nominal_text, sha256(nominal_path), nominal_path.name, variation
            )
            varied = parse_card(text, f"{name}/{tune}")

            unaudited = set(varied) - legal
            if unaudited:
                raise ValueError(
                    f"{name}/{tune}: keys the producer would reject: "
                    + ", ".join(sorted(unaudited))
                )
            differing = {
                key
                for key in set(nominal) | set(varied)
                if nominal.get(key) != varied.get(key)
            }
            if differing != {setting}:
                raise ValueError(
                    f"{name}/{tune}: differs from the nominal in "
                    f"{sorted(differing)}, expected exactly [{setting!r}]"
                )
            if varied[setting] != value:
                raise ValueError(
                    f"{name}/{tune}: {setting} is {varied[setting]!r}, "
                    f"expected {value!r}"
                )

            target = resolve_card_path(root, tune, name)
            if not target.exists() or target.read_text() != text:
                stale.append(target)
                if not args.check:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(text)
                    written += 1

    if stale:
        if args.check:
            print(
                "stale or absent: "
                + ", ".join(str(path.relative_to(root)) for path in stale)
            )
            return 1
        print(f"SYSTEMATIC_CARDS_WRITTEN {written}")
        return 0
    print(
        f"SYSTEMATIC_CARDS_CURRENT {len(names)} variations x "
        f"{len(PUBLISHED_TUNES)} tunes, each differing from its nominal in "
        "exactly one setting"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
