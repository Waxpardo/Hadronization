#!/usr/bin/env python3
"""The generated composites carry the delivery names byte-exactly.

The repository's obligation ends at producing every figure ready for the owner
to drop into Overleaf: correct content, correct statistics, and BYTE-EXACT
filenames (ruling R38). The names below are the content contract's own list.

THIS TEST COMPARES STRINGS FROM THE JSON, NEVER THE FILESYSTEM (finding F58).
An earlier form of this check listed the delivery directory and compared it with
`git ls-files`. No figure is tracked and `plotting/Plots` is git-ignored, so both
sides were empty and the check passed vacuously on every commit. A name that the
generator has not yet written is not evidence that the name is right; the
generator's own output is.

WHY THE COMPOSITES ARE PER FLAVOUR AND EACH NAMES ITS OWN MINIS. The macro holds
one `TPad*` per mini name and `Draw()` re-parents it, so a mini named by two
globals renders on the last canvas and leaves the first one blank with no error.
Disjointness is therefore asserted here as a property of the delivery, not left
to the generator's internal check alone.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLOTTING = ROOT / "plotting"

# The content contract's delivery list, section 1: G4/G6, G5/G7, G8.
DELIVERY_NAMES = {
    "VINTEGRATED": {
        "global_balancing_plots_integrated_beauty",
        "global_balancing_plots_integrated_charm",
    },
    "VEXTREMES": {
        "global_balancing_plots_multiplicity_beauty",
        "global_balancing_plots_multiplicity_charm",
    },
    "VBARYONMESON": {
        "global_balancing_baryon_over_meson_ratio_multiplicity",
    },
}

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def main() -> int:
    delivered: set[str] = set()

    for stem, expected in DELIVERY_NAMES.items():
        path = PLOTTING / f"configuration_multiplicity_HF_RUN3_V1_{stem}.json"
        check(f"{stem} is generated", path.exists(), str(path))
        if not path.exists():
            continue

        document = json.loads(path.read_text())
        globals_out = document["global_canvases_to_be_drawn"]
        written = [g for g in globals_out if g.get("write")]

        names = {g["write_name"] for g in written}
        check(f"{stem} delivers exactly its contracted names",
              names == expected, f"{sorted(names)} != {sorted(expected)}")
        delivered |= names

        # One write_path per configuration: the macro collects the distinct
        # output directories of the writing globals and throws "Exactly one
        # global-canvas output directory is required to store the
        # multiplicity-boundary receipt" on anything but one.
        paths = {g["write_path"] for g in written}
        check(f"{stem} writes to exactly one directory", len(paths) == 1,
              str(sorted(paths)))

        # No mini may be named by two globals.
        used: list[str] = []
        for canvas in globals_out:
            used += canvas["mini_canvases"]
        duplicated = sorted({name for name in used if used.count(name) > 1})
        check(f"{stem} shares no mini between globals", not duplicated,
              str(duplicated))

        # Every named mini must exist.
        present = {c["canvas_name"] for c in document["canvases_to_be_drawn"]}
        missing = sorted(set(used) - present)
        check(f"{stem} names only minis it carries", not missing, str(missing))

    check("the five delivery names are distinct",
          len(delivered) == sum(len(v) for v in DELIVERY_NAMES.values()),
          str(sorted(delivered)))

    print()
    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    print(f"delivery names exact: {len(delivered)} composites over "
          f"{len(DELIVERY_NAMES)} configurations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
