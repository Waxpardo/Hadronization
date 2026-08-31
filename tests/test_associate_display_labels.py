#!/usr/bin/env python3
"""Every configured associate reaches the axis as physics notation.

THE OBSERVED DEFECT (CON-1, executor-found; architect acceptance review of
CON-1, finding #3). Ruling R40 gave the balancing figure configurations the
legacy associate set, which registers B_s^0-bar and Bc-. The macro's
`DisplayLabelForAssociatePdg` table carried no entry for 531 or 541, so those
two bins reached `SetBinLabel` as the RAW ROUTING KEYS `B_s^0-bar` and `Bc-`,
one "WARNING: no physics notation for associate PDG" line per point. Routing
keys are not notation, and these are paper-figure axes.

WHAT THIS ASSERTS. The label table is parsed out of the macro source, and every
`associateOS` a tracked V-configuration registers must have an entry in it. The
PDG is the key on both sides: `improvedPlotting_THnSparse.C:618` sets
`associateOSPdg` from the OS file's pair-registry row, and both `SetBinLabel`
call sites (`:5288`, `:5577`) hand exactly that to the table. So this test
walks the same path the render does -- configuration to OS filename, filename
to registry row, row to `associate_pdg` -- instead of matching on the
identifier strings, which are routing keys and would be a second spelling of
the species set.

THE CONFIGURATION LIST IS DERIVED, not written down here: `variant_documents`
in `tools/make_variant_configs.py` names the tracked set, so a sixth
configuration is covered the day it is generated. The COMMITTED bytes at those
paths are what is read, not the generator's in-memory documents; staleness
between the two is `tests/test_variant_configs.py`'s subject, not this one's.

The parser refuses to report success on an empty or unfound table: a coverage
test that silently parses nothing passes vacuously for every input.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MACRO = ROOT / "plotting" / "improvedPlotting_THnSparse.C"

sys.path.insert(0, str(ROOT / "tools"))
import make_variant_configs as variants  # noqa: E402

# One `{PDG, "label"}` pair of the initializer. The label may hold escapes, so
# the string body is matched as "anything but an unescaped quote".
LABEL_ENTRY = re.compile(r'\{\s*(-?\d+)\s*,\s*"((?:[^"\\]|\\.)*)"\s*\}')

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def parse_label_table(source: str) -> dict[int, str]:
    """The `kLabels` initializer of `DisplayLabelForAssociatePdg`, as a dict.

    Bounded to that one initializer by walking braces from `kLabels = {`, so a
    later map in the same file cannot be read as part of this table.
    """
    function = source.find("std::string DisplayLabelForAssociatePdg")
    if function < 0:
        raise SystemExit(
            f"{MACRO.name}: DisplayLabelForAssociatePdg is not defined; the "
            f"label table this test exists to check is gone")
    opening = source.find("kLabels = {", function)
    if opening < 0:
        raise SystemExit(
            f"{MACRO.name}: DisplayLabelForAssociatePdg carries no `kLabels = "
            f"{{` initializer")
    start = source.index("{", opening + len("kLabels = ") - 1)
    depth, end = 0, None
    for index in range(start, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                end = index
                break
    if end is None:
        raise SystemExit(f"{MACRO.name}: the kLabels initializer is unbalanced")

    table: dict[int, str] = {}
    for pdg, label in LABEL_ENTRY.findall(source[start:end + 1]):
        code = int(pdg)
        if code in table:
            raise SystemExit(
                f"{MACRO.name}: PDG {code} is listed twice in kLabels")
        table[code] = label
    if not table:
        raise SystemExit(
            f"{MACRO.name}: parsed an EMPTY kLabels table; this test would "
            f"pass vacuously and is refusing to")
    return table


def configured_associates() -> dict[int, set[tuple[str, str]]]:
    """PDG -> {(configuration stem, associateOS routing name)}.

    Resolved the way the render resolves it: the configured OS filename to its
    pair-registry row, and the row's `associate_pdg`.
    """
    registry = {row["filename"]: row
                for row in json.loads(variants.PAIR_REGISTRY.read_text())["pairs"]}
    base = json.loads(variants.BASE_CONFIG.read_text())
    paths = variants.variant_documents(
        base, variants.top_percentiles(), variants.DEFAULT_ASSOCIATE_SET)

    needed: dict[int, set[tuple[str, str]]] = {}
    for path in sorted(paths, key=lambda p: p.name):
        if not path.exists():
            raise SystemExit(
                f"{path.name}: the generator names this configuration and it "
                f"is not committed; run tools/make_variant_configs.py")
        document = json.loads(path.read_text())
        stem = path.stem.split("_V1_", 1)[1]
        for section in variants.FLAVOUR_SECTION.values():
            for group in document.get(section, []):
                for configured in group.get("configs", []):
                    row = registry.get(configured["OS"])
                    if row is None:
                        raise SystemExit(
                            f"{path.name}: configured OS file "
                            f"{configured['OS']!r} is not a pair-registry "
                            f"filename")
                    needed.setdefault(row["associate_pdg"], set()).add(
                        (stem, configured["associateOS"]))
    return needed


def main() -> int:
    table = parse_label_table(MACRO.read_text())
    needed = configured_associates()

    check("the label table parses and is non-empty", bool(table),
          f"({len(table)} entries)")
    check("at least one configuration registers an associate", bool(needed))

    for pdg in sorted(needed):
        where = sorted({name for _stem, name in needed[pdg]})
        configurations = sorted({stem for stem, _name in needed[pdg]})
        check(f"associate PDG {pdg} ({', '.join(where)}) has a display label",
              pdg in table,
              f"-- configured in {', '.join(configurations)}; without an entry "
              f"the axis prints the routing key and the render warns per point")

    print()
    print(f"associate display labels: {len(needed)} configured PDGs, "
          f"{len(table)} table entries, {len(failures)} uncovered")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
