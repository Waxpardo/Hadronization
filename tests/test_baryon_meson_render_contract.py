#!/usr/bin/env python3
"""Two defects that stopped the baryon/meson figure, and the guards that hold.

DEFECT 1: THE EMPTY-VECTOR READ. Both baryon/meson draw functions decide how
many dependencies to draw. They read `vBinsToIgnore[0]` and compare it against
the sentinels "NONE", "" and "NULL". An empty vector carries no element 0, so
that read goes out of bounds and the process ends with a segmentation violation.

The bug waited for a configuration with an empty list. Every earlier
configuration that reached these functions carried a non-empty one. V-BARYONMESON
draws all eleven classes, so it ignores none, and the first render of it crashed.
The sibling function `drawBalancingPlots` never had the defect, because it asks
`isInVector`, which is safe on an empty vector.

This test reads the plotter and requires an `empty()` guard in the same condition
as every `vBinsToIgnore[0]` read.

DEFECT 2: THE CROPPED DOUBLE RATIO. The first V-BARYONMESON build carried over
the reviewed yield double-ratio window [0.6, 2.5]. The render refused it and
named the point: envelope [2.711630660826422, 2.8484012581559983], associate
Lambda_b, bin hDPhic9_MB17p124_26p154. The baryon/meson enhancement is larger
than the yield enhancement.

The window is now 0.0 to 4.0. A bare 4.0 tells a later reader nothing about what
the number must hold, so the generator keeps the measured envelope beside it.
This test requires the envelope, the source string, and a window that contains
the envelope. It also requires the emitted configuration to use that window.

MUTATION EVIDENCE, recorded 2026-08-18. Both checks were reverted and both
failed:
  - guard removed at one site      -> UNGUARDED READ, 1 site
  - window narrowed to [0.6, 2.5]  -> WINDOW TOO NARROW
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLOTTER = ROOT / "plotting" / "improvedPlotting_THnSparse.C"
GENERATOR = ROOT / "tools" / "make_variant_configs.py"
CONFIG = ROOT / "plotting" / "configuration_multiplicity_HF_RUN3_V1_VBARYONMESON.json"

# The two functions that had the defect. Named so a reader knows the scope.
GUARDED_FUNCTIONS = (
    "drawBalancingBaryonMesonRatioPlots",
    "drawBalancingBaryonMesonRatioPlotsTUNERatios",
)


def check_empty_guard() -> int:
    """Every vBinsToIgnore[0] read sits behind an empty() test."""
    text = PLOTTER.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    # Skip comment lines. The fix left a comment naming the defect, and that
    # comment mentions vBinsToIgnore[0] without reading it.
    reads = [(n, l) for n, l in enumerate(lines, 1)
             if "vBinsToIgnore[0]" in l and not l.lstrip().startswith("//")]
    if not reads:
        print("UNEXPECTED: no vBinsToIgnore[0] read found; the plotter changed "
              "shape and this test needs review")
        return 1

    unguarded = [(n, l.strip()) for n, l in reads
                 if "vBinsToIgnore.empty()" not in l]
    print(f"vBinsToIgnore[0] reads: {len(reads)}; guarded: "
          f"{len(reads) - len(unguarded)}")
    for n, l in reads:
        state = "guarded" if "vBinsToIgnore.empty()" in l else "UNGUARDED"
        print(f"   line {n}: {state}")
    if unguarded:
        print(f"UNGUARDED READ, {len(unguarded)} site(s). An empty "
              f"bins_to_ignore list segfaults the render.")
        for n, l in unguarded:
            print(f"   line {n}: {l[:100]}")
        return 1

    # The guard must protect the functions that had the defect.
    for name in GUARDED_FUNCTIONS:
        if name not in text:
            print(f"MISSING FUNCTION {name}; this test needs review")
            return 1
    return 0


def check_window_records_its_measurement() -> int:
    """The plot window carries the envelope that sets it, and holds it."""
    source = GENERATOR.read_text(encoding="utf-8")
    envelope = re.search(
        r"BARYONMESON_TUNE_RATIO_ENVELOPE = \(([-0-9.e+]+), ([-0-9.e+]+)\)",
        source)
    window = re.search(
        r"BARYONMESON_TUNE_RATIO_WINDOW = \(([-0-9.e+]+), ([-0-9.e+]+)\)",
        source)
    if not envelope or not window:
        print("MISSING CONSTANT: the generator must name both the measured "
              "envelope and the window it sets")
        return 1

    lo_e, hi_e = float(envelope.group(1)), float(envelope.group(2))
    lo_w, hi_w = float(window.group(1)), float(window.group(2))
    print(f"measured envelope: [{lo_e}, {hi_e}]")
    print(f"configured window: [{lo_w}, {hi_w}]")

    if "BARYONMESON_TUNE_RATIO_ENVELOPE_SOURCE" not in source:
        print("MISSING SOURCE: the envelope must name where it was measured")
        return 1

    if not (lo_w <= lo_e and hi_e <= hi_w):
        print("WINDOW TOO NARROW: the window must contain the measured "
              "envelope. SetPlotPointOrThrow refuses a point outside it, so a "
              "narrow window stops the render.")
        return 1

    # The emitted configuration must use the window, not a literal.
    document = json.loads(CONFIG.read_text())
    ratios = [c for c in document["canvases_to_be_drawn"]
              if c["draw_function_to_use"].endswith("TUNERatios")]
    if not ratios:
        print("UNEXPECTED: no tune-ratio canvas in the emitted configuration")
        return 1
    for canvas in ratios:
        if (canvas["y_min_axis"], canvas["y_max_axis"]) != (lo_w, hi_w):
            print(f"CONFIG DISAGREES: {canvas['canvas_name']} uses "
                  f"[{canvas['y_min_axis']}, {canvas['y_max_axis']}]")
            return 1
    print(f"tune-ratio canvases using the window: {len(ratios)}")
    return 0


def main() -> int:
    status = 0
    print("--- empty-vector guard ---")
    status |= check_empty_guard()
    print("--- plot window and its measurement ---")
    status |= check_window_records_its_measurement()
    print("BARYON_MESON_RENDER_CONTRACT status=" + ("PASS" if not status else "FAIL"))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
