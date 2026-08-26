#!/usr/bin/env python3
"""One record of every claimed campaign ordinal, and a render that reads it.

Origin. The ordinal is packed into every event identifier and it keys the seed
band `SEED_BASE + ordinal * CAMPAIGN_STRIDE` (tools/campaign.py), so a re-used
ordinal draws seeds another campaign has burned and stamps identifiers two
campaigns share. Neither is correctable after the jobs have run. Until this
registry existed the claims lived in four places that could not be reconciled:
a hand-list in the Makefile, `campaign_ordinals_claimed` in
config/systematics_variations_v1.json, a test docstring, and an owner ruling
recorded nowhere in the repository. The Makefile hand-list was then rewritten,
which deleted the only record of what held ordinal 1.

What this test pins:

  1. the registry parses, declares its schema, and holds each ordinal once;
  2. no campaign appears under two ordinals, and no ordinal is recorded twice
     -- in the registry or in any tracked config file that claims one;
  3. ordinals 4 to 10 agree with config/systematics_variations_v1.json in both
     directions, so neither file can drift from the other;
  4. every row carries a date, the evidence for that date, and a scope note,
     because an ordinal claim is provenance and an unsourced claim is not;
  5. tools/render_production_submit.py refuses a claimed ordinal taken by a
     different campaign, and refuses when it cannot read the registry at all --
     fail-closed at render time, before a seed is burned;
  6. the Makefile names the registry first among the sources it points at.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/campaign_ordinals_v1.json"
VARIATIONS = ROOT / "config/systematics_variations_v1.json"
RENDERER = ROOT / "tools/render_production_submit.py"
MAKEFILE = ROOT / "Makefile"
SCHEMA = "hadronization_campaign_ordinals_v1"
FAKE_SHA = "a" * 64

# The ordinals this registry undertakes to cover. Stated here as well as in the
# file so that a row quietly dropped from one of them fails rather than
# narrowing the registry's coverage in silence.
COVERED = tuple(range(0, 12))

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def registry():
    return json.loads(REGISTRY.read_text())


def renderer_module():
    """The renderer as a module, so its registry loader can be driven."""
    spec = importlib.util.spec_from_file_location(
        "render_production_submit_under_test", RENDERER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render(*extra, project_base=None):
    """Run the renderer far enough to pass or fail the ordinal check.

    The check sits above every access to the checkout, so a directory that
    holds nothing is enough to reach it. A run that gets past the check dies
    lower down for an unrelated reason, which is what the callers below read.
    """
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(project_base) if project_base else Path(tmp)
        return subprocess.run(
            [sys.executable, str(RENDERER), str(base), f"{tmp}/out.sub",
             "--jobs", "1", "--events", "1000",
             "--producer-executable-sha256", FAKE_SHA, *extra],
            text=True, capture_output=True, check=False)


# --- 1, 2. the file itself --------------------------------------------------

def test_the_registry_declares_its_schema_and_covers_its_range():
    data = registry()
    check("the registry declares its schema",
          data.get("schema") == SCHEMA, repr(data.get("schema")))
    for field in ("purpose", "coverage", "authority", "uniqueness_rule",
                  "date_note"):
        check(f"the registry explains its {field}",
              isinstance(data.get(field), str) and data[field].strip(),
              repr(data.get(field)))

    ordinals = [entry["ordinal"] for entry in data["ordinals"]]
    check("every ordinal is an integer",
          all(isinstance(value, int) and not isinstance(value, bool)
              for value in ordinals), str(ordinals))
    check("no ordinal is recorded twice",
          len(set(ordinals)) == len(ordinals),
          f"{sorted(value for value in ordinals if ordinals.count(value) > 1)}")
    check("the rows are in ordinal order", ordinals == sorted(ordinals),
          str(ordinals))
    check("the registry covers exactly the ordinals it claims to",
          tuple(sorted(ordinals)) == COVERED,
          f"{sorted(ordinals)} != {list(COVERED)}")


def test_no_campaign_holds_two_ordinals():
    """A campaign under two ordinals means two seed bands and two identifier
    spaces for one dataset, which no downstream tool can reconcile."""
    holders = {}
    for entry in registry()["ordinals"]:
        for campaign in entry["campaigns"]:
            holders.setdefault(campaign, []).append(entry["ordinal"])
    doubled = {name: found for name, found in holders.items() if len(found) > 1}
    check("no campaign name appears under two ordinals", not doubled,
          str(doubled))
    check("no campaign name is repeated inside one row",
          all(len(entry["campaigns"]) == len(set(entry["campaigns"]))
              for entry in registry()["ordinals"]),
          str([entry["campaigns"] for entry in registry()["ordinals"]]))


def test_every_row_carries_its_provenance():
    for entry in registry()["ordinals"]:
        ordinal = entry["ordinal"]
        claimed = entry.get("claimed", "")
        check(f"ordinal {ordinal} carries an ISO claim date",
              isinstance(claimed, str) and len(claimed) == 10
              and claimed[4] == claimed[7] == "-"
              and claimed.replace("-", "").isdigit(), repr(claimed))
        for field in ("claimed_evidence", "scope", "seed_derivation"):
            value = entry.get(field, "")
            check(f"ordinal {ordinal} carries a {field}",
                  isinstance(value, str) and value.strip(), repr(value))
        check(f"ordinal {ordinal} names a known seed derivation",
              entry.get("seed_derivation") in
              ("seed_derivation_v1", "seed_derivation_v2"),
              repr(entry.get("seed_derivation")))


# --- 3. the two files must agree -------------------------------------------

def test_the_variations_and_the_registry_agree():
    variations = json.loads(VARIATIONS.read_text())
    declared = {row["campaign"]: row["campaign_ordinal"]
                for row in variations["variations"]}
    claimed_list = variations["campaign_ordinals_claimed"]
    check("campaign_ordinals_claimed matches the per-variation ordinals",
          sorted(claimed_list) == sorted(declared.values()),
          f"{sorted(claimed_list)} != {sorted(declared.values())}")

    rows = {entry["ordinal"]: entry for entry in registry()["ordinals"]}
    for campaign, ordinal in sorted(declared.items(), key=lambda item: item[1]):
        entry = rows.get(ordinal)
        check(f"the registry holds variation ordinal {ordinal}",
              entry is not None, f"{ordinal} is absent")
        if entry is not None:
            check(f"...bound to {campaign} and to nothing else",
                  entry["campaigns"] == [campaign], str(entry["campaigns"]))

    # The other direction. Without it the registry could carry a variation
    # ordinal the variations file has since dropped, and nothing would say so.
    registered_variations = {
        entry["ordinal"] for entry in registry()["ordinals"]
        if any(name.startswith("HF_SYS_") for name in entry["campaigns"])}
    check("the registry claims no variation ordinal the variations file lost",
          registered_variations == set(declared.values()),
          f"{sorted(registered_variations)} != {sorted(set(declared.values()))}")


def test_no_tracked_config_claims_an_ordinal_the_registry_contradicts():
    """Any other config file that binds a campaign to an ordinal must agree.

    config/systematics_variations_v1.json is the only such file today. The scan
    is over the directory rather than over that name, so a second one added
    later is checked rather than ignored.
    """
    rows = {entry["ordinal"]: entry["campaigns"]
            for entry in registry()["ordinals"]}
    scanned, disagreements = [], []
    for path in sorted((ROOT / "config").glob("*.json")):
        if path == REGISTRY:
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        stack, found = [data], []
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                if "campaign_ordinal" in node and "campaign" in node:
                    found.append((node["campaign"], node["campaign_ordinal"]))
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
        if not found:
            continue
        scanned.append(path.name)
        for campaign, ordinal in found:
            if campaign not in rows.get(ordinal, ()):
                disagreements.append((path.name, campaign, ordinal))
    check("every tracked config that binds an ordinal agrees with the registry",
          not disagreements, str(disagreements))
    check("the scan found the file it is meant to find",
          "systematics_variations_v1.json" in scanned, str(scanned))


# --- 5. the renderer refuses, fail-closed ----------------------------------

def test_the_renderer_refuses_a_claimed_ordinal():
    rows = {entry["ordinal"]: entry["campaigns"]
            for entry in registry()["ordinals"]}
    ordinal, holders = next(
        (value, names) for value, names in sorted(rows.items())
        if value >= 1 and names)
    got = render("--campaign", "NOT_THE_HOLDER", "--campaign-ordinal",
                 str(ordinal))
    # The status alone is weak here: the run would fail anyway on the empty
    # checkout. The refusal has to be this one.
    check("the renderer refuses an ordinal another campaign holds",
          got.returncode != 0 and "is already claimed by" in got.stderr,
          f"rc={got.returncode} err={got.stderr[-300:]}")
    check("...and names the ordinal, the holder and the registry",
          str(ordinal) in got.stderr and holders[0] in got.stderr
          and "config/campaign_ordinals_v1.json" in got.stderr,
          got.stderr[-400:])


def test_the_renderer_accepts_the_campaign_that_holds_the_ordinal():
    """The refusal must be about the pairing, not about the ordinal.

    The run still fails, lower down and for an unrelated reason: this test
    hands it a checkout that holds nothing. What it reads is that the ordinal
    message is absent.
    """
    rows = {entry["ordinal"]: entry["campaigns"]
            for entry in registry()["ordinals"]}
    ordinal, holders = next(
        (value, names) for value, names in sorted(rows.items())
        if value >= 1 and names)
    got = render("--campaign", holders[0], "--campaign-ordinal", str(ordinal))
    check("the holder is not refused for its own ordinal",
          "is already claimed by" not in got.stderr, got.stderr[-400:])

    spare = max(rows) + 1
    got = render("--campaign", "SOMETHING_NEW", "--campaign-ordinal",
                 str(spare))
    check("an ordinal the registry does not hold is not refused",
          "is already claimed by" not in got.stderr, got.stderr[-400:])


def test_the_renderer_refuses_when_it_cannot_read_the_registry():
    """Fail-closed: an unreadable registry cannot answer, so nothing proceeds."""
    module = renderer_module()
    original = module.REPOSITORY
    try:
        with tempfile.TemporaryDirectory() as tmp:
            module.REPOSITORY = Path(tmp)
            try:
                module.claimed_campaign_ordinals()
                check("a missing registry refuses", False, "it returned")
            except ValueError as error:
                check("a missing registry refuses",
                      "missing" in str(error), str(error))

            broken = Path(tmp) / "config/campaign_ordinals_v1.json"
            broken.parent.mkdir(parents=True)
            broken.write_text("{ not json")
            try:
                module.claimed_campaign_ordinals()
                check("a registry that does not parse refuses", False,
                      "it returned")
            except ValueError as error:
                check("a registry that does not parse refuses",
                      "does not parse" in str(error), str(error))

            broken.write_text(json.dumps(
                {"schema": "something_else", "ordinals": []}))
            try:
                module.claimed_campaign_ordinals()
                check("a registry with the wrong schema refuses", False,
                      "it returned")
            except ValueError as error:
                check("a registry with the wrong schema refuses",
                      "expected" in str(error), str(error))

            broken.write_text(json.dumps({
                "schema": SCHEMA,
                "ordinals": [{"ordinal": 7, "campaigns": ["A"]},
                             {"ordinal": 7, "campaigns": ["B"]}]}))
            try:
                module.claimed_campaign_ordinals()
                check("a registry that records one ordinal twice refuses",
                      False, "it returned")
            except ValueError as error:
                check("a registry that records one ordinal twice refuses",
                      "more than once" in str(error), str(error))
    finally:
        module.REPOSITORY = original


# --- 6. the Makefile points at it first ------------------------------------

def test_the_makefile_names_the_registry_first():
    text = MAKEFILE.read_text()
    start = text.index("require-ordinal:")
    message = text[start:text.index("\nsubmit-smoke:", start)]
    check("the require-ordinal message names the registry",
          "config/campaign_ordinals_v1.json" in message, message[:400])
    check("...before the systematics variations file",
          message.index("config/campaign_ordinals_v1.json")
          < message.index("config/systematics_variations_v1.json"),
          "the registry must be the first source the reader is sent to")
    check("...and no longer hand-lists the claims it holds",
          "Already in use:" not in message and "is assigned 11" not in message,
          "a hand-list beside the registry is a second source that drifts")


def main():
    print(f"campaign ordinal registry {REGISTRY}")
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
