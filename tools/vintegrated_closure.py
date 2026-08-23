#!/usr/bin/env python3
"""Assert the V-INTEGRATED closure: summed per-class counts == integrated counts.

Reads the `PAIR_COUNTS` lines the plotting macro emits for every (tune, species,
bin) and checks, per species per tune:

    sum over the eleven classes of N_OS   ==   N_OS of the M00_100 bin
    sum over the eleven classes of N_SS   ==   N_SS of the M00_100 bin
    sum over the eleven classes of N_trig ==   N_trig of the M00_100 bin

The two sides come from DIFFERENT routes -- eleven restricted THnSparse
projections summed, against one unrestricted projection -- so agreement is a
real check that the classes tile the multiplicity axis, not an identity.

INTEGER-EXACT, no tolerance. The counts are unweighted for this campaign
(measured over 1.2M events), so
the contents are exact integers in doubles and exact equality is the right
comparison. A mismatch means the classes do not tile the sample -- a dropped
class, a bins_to_ignore entry, an off-by-one on a boundary bin -- and the fix is
the axis, never an epsilon.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

INTEGRATED_BIN = "M00_100"
LINE = re.compile(r"^PAIR_COUNTS\s+(.*)$")


def parse(path: Path):
    rows = []
    for raw in path.read_text(errors="replace").splitlines():
        m = LINE.match(raw.strip())
        if not m:
            continue
        fields = {}
        for token in m.group(1).split():
            if "=" in token:
                k, v = token.split("=", 1)
                fields[k] = v
        rows.append(fields)
    return rows


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: vintegrated_closure.py <log>", file=sys.stderr)
        return 2
    rows = parse(Path(sys.argv[1]))
    if not rows:
        print("no PAIR_COUNTS lines found", file=sys.stderr)
        return 1

    # key -> bin -> counts
    by_key: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for r in rows:
        key = (r.get("tune"), r.get("flavour"), r.get("trigger"),
               r.get("associate"), r.get("os_file"))
        by_key[key][r.get("bin")] = r

    print(f"{'tune':<13}{'trigger':<8}{'associate':<20}"
          f"{'sum(class) OS-SS':>20}{'integrated OS-SS':>20}{'exact':>7}")
    failures = []
    checked = 0
    non_integral = []

    for key in sorted(by_key, key=lambda k: (k[0] or "", k[3] or "")):
        bins = by_key[key]
        if INTEGRATED_BIN not in bins:
            continue
        classes = {b: v for b, v in bins.items() if b != INTEGRATED_BIN}
        if not classes:
            continue

        def total(field: str) -> float:
            return sum(float(v[field]) for v in classes.values())

        sums = {f: total(f) for f in ("n_os", "n_ss", "n_trig")}
        integ = {f: float(bins[INTEGRATED_BIN][f]) for f in sums}

        for f, v in list(sums.items()) + list(integ.items()):
            if v != int(v):
                non_integral.append((key, f, v))

        ok = all(sums[f] == integ[f] for f in sums)
        checked += 1
        tune, _flav, trig, assoc, _osf = key
        print(f"{tune:<13}{trig:<8}{assoc:<20}"
              f"{sums['n_os'] - sums['n_ss']:>20.0f}"
              f"{integ['n_os'] - integ['n_ss']:>20.0f}"
              f"{'YES' if ok else 'NO':>7}")
        if not ok:
            for f in sums:
                if sums[f] != integ[f]:
                    failures.append(
                        f"{tune} {trig}->{assoc} {f}: "
                        f"sum(classes)={sums[f]:.17g} integrated={integ[f]:.17g} "
                        f"delta={sums[f]-integ[f]:.17g}")

    print()
    print(f"classes per key: {len(classes)}   keys checked: {checked}")
    if non_integral:
        print("NON-INTEGRAL COUNTS (unit-weight precondition violated):")
        for key, f, v in non_integral[:10]:
            print(f"   {key} {f} = {v!r}")
        return 1
    if failures:
        print("CLOSURE FAILED:")
        for line in failures:
            print("   " + line)
        return 1
    print(f"V_INTEGRATED_CLOSURE=EXACT keys={checked} "
          f"(integer-exact, no tolerance applied)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
