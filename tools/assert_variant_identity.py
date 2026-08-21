#!/usr/bin/env python3
"""A variant figure must draw the SAME numbers as the source it is a view of.

V-EXTREMES and V-INTEGRATED are display-filtered views. Filtering must change
what is shown and nothing else, so every point they draw is compared -- exactly,
on the printed 17-significant-digit value, no tolerance -- against the same
quantity in the run it is a view of:

  V-EXTREMES   vs V-FULL          for classes c1 and c11
  V-INTEGRATED vs the closure run for the integrated bin

Comparing the drawn figure against a differently-configured run is the point: if
filtering perturbed the computation, these would differ.
"""

from __future__ import annotations

import sys
from pathlib import Path


def matrix(path: Path) -> dict[tuple, dict]:
    out = {}
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("UNCERTAINTY_MATRIX"):
            continue
        f = dict(t.split("=", 1) for t in line.split() if "=" in t)
        key = (f.get("tune"), f.get("trigger"), f.get("associate"), f.get("bin"))
        out[key] = f
    return out


def compare(name: str, variant: Path, source: Path, bins: set[str]) -> int:
    v, s = matrix(variant), matrix(source)
    keys = [k for k in v if k[3] in bins]
    if not keys:
        print(f"FAIL {name}: no drawn points found for bins {sorted(bins)}")
        return 1
    bad, checked = [], 0
    for k in sorted(keys):
        if k not in s:
            bad.append(f"{k} present in variant, absent from source")
            continue
        for field in ("central_yield", "yield_sem"):
            a, b = v[k].get(field), s[k].get(field)
            if a != b:
                bad.append(f"{k} {field}: variant={a} source={b}")
        checked += 1
    print(f"{name}: {checked} drawn points compared against {source.name}")
    for k in sorted(keys)[:4]:
        print(f"    {k[0]:<13}{k[2]:<18}{k[3]:<24}"
              f"yield={v[k]['central_yield']} sem={v[k]['yield_sem']}")
    if bad:
        print(f"FAIL {name}:")
        for line in bad[:10]:
            print("   " + line)
        return 1
    print(f"{name}: IDENTICAL on every drawn point "
          f"(exact string equality of the 17-digit values)")
    return 0


def main() -> int:
    base = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp")
    rc = 0
    extreme_bins = {"hDPhic1_MB88p197_100", "hDPhic11_MB0_8p422"}
    # Exact leg: both logs come from the current macro at 17 significant digits.
    rc |= compare("V-EXTREMES vs the 11-class closure run",
                  base / "vextremes.log", base / "vint.log", extreme_bins)
    print()
    # THE DIRECT LEG, EXACT SINCE THE STYLING RE-RENDER.
    #
    # V-FULL was rendered before the macro printed at 17 significant figures, so
    # its log recorded ROOT's default 6. That was a property of the LOG and not
    # of the number, and it was the only reason this leg could not be a string
    # comparison. It ran through a `compare_rounded` helper that re-printed each
    # variant value at the source's precision -- no numeric tolerance, but a
    # weaker statement than the other two legs make.
    #
    # The styled re-render of 2026-08-18 logs 17 significant figures, so the
    # comparison is now exact string equality like the rest. The rounded helper
    # is deleted rather than left unused: it would otherwise stand as a
    # ready-made way to make this assertion weaker again.
    rc |= compare("V-EXTREMES vs V-FULL (signed off)",
                  base / "vextremes.log", base / "polish_render3.log",
                  extreme_bins)
    print()
    rc |= compare("V-INTEGRATED vs closure run",
                  base / "vintegrated.log", base / "vint.log",
                  {"hDPhiM00_100"})
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
