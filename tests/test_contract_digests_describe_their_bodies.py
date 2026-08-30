#!/usr/bin/env python3
"""A stored self-describing digest must describe the body it sits in.

THE DEFECT THIS CLOSES. `contracts/decay_parent_map_v2.json` stored
`map_sha256 = c9593c9c…` while its body hashed to `12a8e62d…`, and
`contracts/decay_parent_map_v1_1.json` stored `dd502a10…` against `68834dd4…`.
Both digests were correct when written on 2026-08-11. Two prose commits then
rewrote one string inside each map and left the digest field untouched:
`2f572d5` on v2, and `c629642` on v2 and v1.1. From that day to 2026-08-28 the
field described no committed body. Nothing in the tree noticed, because no tool
recomputes the value and no test read it. `extraction/apply_decay_map.py:163`
prints the stored string and never checks it.

THE RULE. A digest field whose writer removes that key and hashes the rest is a
claim about the artifact it sits in. The claim must hold. This file recomputes
every such field from the body beside it and fails on any that has parted from
it.

THE TWO RECIPES ARE NOT INTERCHANGEABLE, and each is the one its own writer
uses:

  `map_sha256`      indent=2, sorted   docs/GOLDEN_OUTPUTS.md:30, and the
                                       builders at build_decay_parent_map.py:354
                                       and build_decay_parent_map_v2.py:217
  `payload_sha256`  compact, sorted    tools/statistical_robustness.py:62, and
                                       the reader that enforces it at
                                       Plot_MultiplicityDistribution_PercentileBoundaries.C:396

Hashing one under the other's recipe reproduces nothing, so the recipe travels
with the field name rather than with the file.

DISCOVERY IS OVER THE SET, NOT OVER TWO NAMES. The scan walks every tracked
JSON file and reads the field names, so a third decay map, or a second boundary
receipt, is checked on the day it is committed rather than on the day someone
remembers to extend a list. The walk is intersected with `git ls-files` through
`sandbox_tree.tracked_paths`, for the reason that helper records: an untracked
local file must not fail this gate falsely, and must not hide inside a passing
one.

MOST `*_sha256` FIELDS NAME SOMETHING ELSE, and those must not be recomputed
from the body they sit beside. `definition_sha256` and `species_sha256` name the
two input files of the pair registry
(`tools/generate_registry_artifacts.py:357-358`). `variation_sha256` names the
variation the sentinel compared (`tools/a2_record_regression.py:180`).
`configuration_sha256`, `plotter_source_sha256` and `boundary_utility_sha256`
name source and configuration files that the plotting stage digests by path
(`plotting/improvedPlotting_THnSparse.C:1352-1359` and `:1928`). Recomputing
any of these from the enclosing body would assert something nobody claimed.

WHAT A NEW FIELD MUST DO. The classification below is required to be complete:
a top-level `*_sha256` field that is in neither table fails
`test_every_top_level_digest_field_name_is_classified`. That is the part that
closes the class. A new field is either self-describing, and then it is checked
here from its first commit, or it names something else, and then it is recorded
here as doing so.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import cast

# Same directory as this driver, so no path setup is needed.
from sandbox_tree import tracked_paths

ROOT = Path(__file__).resolve().parents[1]

SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")


def _indent_two(body: dict) -> str:
    """The decay maps' recipe: docs/GOLDEN_OUTPUTS.md:30."""
    return hashlib.sha256(
        json.dumps(body, indent=2, sort_keys=True).encode()).hexdigest()


def _compact(body: dict) -> str:
    """The receipts' recipe: tools/statistical_robustness.py:62."""
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"),
                   allow_nan=False).encode("utf-8")).hexdigest()


# A field here covers the body it sits in, minus itself. The value is the recipe
# its own writer uses, and the writer is cited in this file's opening text.
SELF_DESCRIBING = {
    "map_sha256": _indent_two,
    "payload_sha256": _compact,
}

# A field here names a different object, so the body beside it says nothing
# about the value. Each reason is cited in this file's opening text.
NAMES_SOMETHING_ELSE = {
    "boundary_utility_sha256": "plotting/MultiplicityBoundaryUtils.h",
    "common_boundary_utility_sha256": "a boundary utility of an earlier plotter",
    "configuration_sha256": "the plotting configuration at configuration_path",
    "definition_sha256": "the pair-definition input of the registry",
    "plotter_source_sha256": "plotting/improvedPlotting_THnSparse.C",
    "species_sha256": "the species-table input of the registry",
    "variation_sha256": "the variation the A2 sentinel compared",
}


def tracked_json_objects() -> list[tuple[Path, dict]]:
    """Every tracked JSON file that parses to an object, in path order.

    The walk stays over the whole tree so a contract added in a directory
    nobody has thought of yet is still read. A file that does not parse is not
    silently dropped: it fails here, because an artifact this repository cannot
    read is not one it can certify either.
    """
    tracked = tracked_paths(ROOT)
    documents: list[tuple[Path, dict]] = []
    for path in sorted(p for p in ROOT.rglob("*.json") if p in tracked):
        try:
            document = json.loads(path.read_text())
        except json.JSONDecodeError as error:
            raise AssertionError(
                f"{path.relative_to(ROOT)} is tracked but does not parse as "
                f"JSON: {error}") from error
        if isinstance(document, dict):
            documents.append((path, document))
    return documents


def digest_fields(document: dict) -> dict[str, object]:
    """Every top-level `*sha256` field of one document, before validation.

    Only the top level. A self-describing digest covers the document its key
    belongs to, and a nested key belongs to a member rather than to the file.
    Measured 2026-08-30, session CON-1B, over the tracked JSON of this
    checkout: all TWENTY-FOUR distinct nested `*sha256` names -- among them
    `publication_authorization_sha256`, `receipt_sha256` and `macro_sha256` --
    name a separate object, and none is self-describing. The count was written
    as fourteen and had been stale since (ledger DA1-A083); it is dated here
    the way docs/GOLDEN_OUTPUTS.md dates its digest table, because it is a
    measurement of a tree that grows and not an invariant.
    """
    return {name: value for name, value in document.items()
            if name.endswith("sha256")}


def top_level_digest_fields() -> list[tuple[Path, dict, str, object]]:
    """Discover the complete tracked top-level field inventory first.

    Value validation is deliberately separate. A malformed value must remain
    in the inventory so it cannot disappear before classification.
    """
    found = []
    for path, document in tracked_json_objects():
        for name, value in digest_fields(document).items():
            found.append((path, document, name, value))
    return found


def canonical_digest_fields() -> list[tuple[Path, dict, str, str]]:
    """Validate every value only after discovery has enumerated every field."""
    found = top_level_digest_fields()
    malformed = [(path, name, value) for path, _document, name, value in found
                 if not isinstance(value, str) or not SHA256_HEX.fullmatch(value)]
    assert not malformed, "\n".join(
        ["top-level digest fields must store 64 lowercase hexadecimal "
         "characters:"] +
        [f"  {path.relative_to(ROOT)}: {name} stores {value!r} "
         f"({type(value).__name__})"
         for path, name, value in malformed]
    )
    return [(path, document, name, cast(str, value))
            for path, document, name, value in found]


def self_describing_fields() -> list[tuple[Path, str, str, str]]:
    """Every stored self-describing digest, with the value its body produces."""
    found = []
    for path, document, name, stored in canonical_digest_fields():
        recipe = SELF_DESCRIBING.get(name)
        if recipe is None:
            continue
        body = {key: value for key, value in document.items()
                if key != name}
        found.append((path, name, stored, recipe(body)))
    return found


def test_every_self_describing_digest_matches_its_body() -> None:
    parted = [(path, name, stored, computed)
              for path, name, stored, computed in self_describing_fields()
              if stored != computed]
    assert not parted, "\n".join(
        [f"{len(parted)} stored digest(s) do not describe their own body:"] +
        [f"  {path.relative_to(ROOT)}: {name} stores {stored}, "
         f"body hashes to {computed}"
         for path, name, stored, computed in parted] +
        ["Rebuild the artifact with its builder rather than editing the field."]
    )


def test_every_top_level_digest_field_name_is_classified() -> None:
    """A new `*sha256` field is checked or recorded, never ignored.

    Without this the class stays open: the next contract could carry a
    self-describing digest under a name this file has never met, and the check
    above would pass by skipping it.
    """
    classified = set(SELF_DESCRIBING) | set(NAMES_SOMETHING_ELSE)
    unclassified: dict[str, list[str]] = {}
    for path, _document, name, _value in canonical_digest_fields():
        if name not in classified:
            unclassified.setdefault(name, []).append(
                str(path.relative_to(ROOT)))
    assert not unclassified, "\n".join(
        ["these top-level digest fields are classified nowhere:"] +
        [f"  {name}: {', '.join(sorted(paths))}"
         for name, paths in sorted(unclassified.items())] +
        ["Add each to SELF_DESCRIBING, and it is checked from now on, or to "
         "NAMES_SOMETHING_ELSE with the object it names."]
    )


def test_the_scan_reaches_the_carriers_this_repository_has() -> None:
    """An empty scan certifies nothing while both cases above still report PASS.

    The same failure `sandbox_tree.tracked_files` guards against: a discovery
    step that silently finds nothing turns a contract test into a green light.
    """
    found = self_describing_fields()
    assert found, (
        "the scan found no self-describing digest at all; discovery has "
        "broken, and the two cases above are certifying an empty set")
    carriers = {path.relative_to(ROOT).as_posix() for path, _n, _s, _c in found}
    for known in ("contracts/decay_parent_map_v1_1.json",
                  "contracts/decay_parent_map_v2.json"):
        assert known in carriers, (
            f"{known} carries a self-describing digest and the scan missed "
            f"it; found {sorted(carriers)}")


def main() -> int:
    test_every_self_describing_digest_matches_its_body()
    test_every_top_level_digest_field_name_is_classified()
    test_the_scan_reaches_the_carriers_this_repository_has()
    print(f"self-describing digest tests passed "
          f"({len(self_describing_fields())} carriers checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
