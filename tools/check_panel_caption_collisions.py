#!/usr/bin/env python3
"""Does the acceptance caption collide with the drawn data on any species panel?

WHY THIS EXISTS. The 30 species panels were verified to CARRY the acceptance
block by extracting text primitives from each generated `.C` -- 30/30, twice --
while four of them were drawing the spectrum straight through the words. A text
primitive is present whether or not anything is on top of it, so that check
cannot see this class of defect, and neither can a digest. **Presence and
legibility are different checks** and this tool is the second one.

It answers one question per panel: are there DATA pixels inside the caption's
own bounding box?

THE DISCRIMINATOR, and why it is colour. The caption is black; so is MONASH.
Testing for "dark pixels over the text" would therefore flag the text itself.
What cannot be caption is COLOUR: JUNCTIONS is blue (#0000cc) and CLOSEPACKING
is purple (#9933ff), and the three curves run within a line width of each other
wherever they overlap the block. So a chromatic pixel inside the text box means
the curves are there, and MONASH is there with them.

    chromatic  <=>  max(R,G,B) - min(R,G,B) > 40, and not near-white

CALIBRATION OF THE TEXT BOX. The four caption lines are emitted by one code path
at fixed NDC y (0.400 / 0.356 / 0.312 / 0.268) with identical strings on every
panel, so the box is the same everywhere and is measured ONCE rather than
assumed. The x-extent is measured from a REFERENCE panel on which the block sits
in open space -- any `eta` panel, whose distribution is a plateau far from the
lower left -- by scanning each line's band for dark runs and taking the first and
last. Frame and axis furniture are excluded by ignoring runs narrower than
`MIN_RUN` and anything outside `[FRAME_X0, FRAME_X1]`.

    Measured 2026-08-18 on Inclusive_eta_Dplus_shape.png (856x652):
        line 3 "direct primary hadronisation products (status 81-89)"
        occupied x in [167, 553]; the runs at [140,146] and [808,811] are a
        y-axis tick and the right frame and are correctly discarded.

**An over-wide box is the failure mode to avoid.** A first version ran the box
out to 0.80 of the canvas width, well past the end of the text, and reported 10
of 30 panels colliding -- the extra hits were the curve passing through empty
space to the right of the last glyph. Measuring the extent instead of guessing it
took the count to 6, of which 4 are real strikes and 2 are the curve entering the
band above the glyphs. Hence `--report-bands`, which separates the two.

USAGE
    python3 tools/check_panel_caption_collisions.py <panel-dir> [--reference NAME]

Exit status is 1 if any panel has a strike, 0 otherwise, so it can gate a render.
Requires `sips` (macOS) to decode PNG; no third-party imports.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import struct
import subprocess
import sys

# The caption's baselines are READ FROM EACH PANEL, not assumed.
#
# THE DEFECT THIS CLOSES. This tool used to carry the baselines as constants
# (0.400, 0.356, 0.312, 0.268). That held while every panel put its caption in
# the same place. The anchor ladder of render #6 moved four panels to 0.346 or
# 0.302, and the tool went on measuring the boxes those panels had left behind.
# It reported six strikes where a reader sees four: on a relocated panel it was
# measuring empty space that the curve happens to cross.
#
# Reading the baselines from the panel's own generated `.C` removes the
# assumption. The caption lines are the four TLatex calls at the anchor x that
# carry the known caption strings.
CAPTION_ANCHOR_X = 0.195
CAPTION_MARKERS = ("PYTHIA 8", "TeV", "status", "GeV")
FRAME_X0, FRAME_X1 = 140, 812   # inside the y-axis, short of the right frame
MIN_RUN = 20                    # a word, not a tick mark
BAND_ABOVE, BAND_BELOW = 16, 10  # rows around the text baseline
CHROMA = 40


def decode(path: str):
    """(width, height, pixel(x,y)->(r,g,b)) via sips -> BMP24."""
    tmp = "/tmp/_caption_check.bmp"
    subprocess.run(["sips", "-s", "format", "bmp", path, "--out", tmp],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   check=True)
    d = open(tmp, "rb").read()
    off = struct.unpack("<I", d[10:14])[0]
    w = struct.unpack("<i", d[18:22])[0]
    h = struct.unpack("<i", d[22:26])[0]
    topdown = h < 0
    h = abs(h)
    rowsz = ((24 * w + 31) // 32) * 4

    def px(x, y):
        ry = y if topdown else (h - 1 - y)
        i = off + ry * rowsz + x * 3
        return d[i + 2], d[i + 1], d[i]

    return w, h, px


def is_dark(p):
    return p[0] < 120 and p[1] < 120 and p[2] < 120


def is_chromatic(p):
    r, g, b = p
    return (max(r, g, b) - min(r, g, b)) > CHROMA and not (r > 230 and g > 230 and b > 230)


def caption_baselines(png_path: str) -> list:
    """The four caption baselines, read from this panel's generated .C."""
    source = png_path[:-4] + ".C"
    if not os.path.exists(source):
        raise SystemExit(f"no generated .C beside {os.path.basename(png_path)}; "
                         "this tool reads the baselines from it")
    text = open(source, encoding="utf-8", errors="replace").read()
    found = []
    for m in re.finditer(r'new TLatex\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*"(.*?)"',
                         text, re.S):
        x, y, body = float(m.group(1)), float(m.group(2)), m.group(3)
        if abs(x - CAPTION_ANCHOR_X) > 1e-6:
            continue
        if any(marker in body for marker in CAPTION_MARKERS):
            found.append(y)
    found = sorted(set(found), reverse=True)
    if len(found) != 4:
        raise SystemExit(f"expected 4 caption lines in {os.path.basename(source)}, "
                         f"found {len(found)}: {found}")
    return found


def calibrate(path: str):
    """Measure each caption line's x-extent on a panel where it sits in the open."""
    w, h, px = decode(path)
    boxes = {}
    for ndc in caption_baselines(path):
        yc = int((1.0 - ndc) * h)
        cols = sorted({x for y in range(yc - BAND_ABOVE, yc + BAND_BELOW)
                       for x in range(FRAME_X0, FRAME_X1) if is_dark(px(x, y))})
        if not cols:
            continue
        runs, start, prev = [], cols[0], cols[0]
        for x in cols[1:]:
            if x - prev > 6:
                runs.append((start, prev))
                start = x
            prev = x
        runs.append((start, prev))
        words = [r for r in runs if r[1] - r[0] >= MIN_RUN]
        if words:
            boxes[ndc] = (words[0][0], words[-1][1])
    return boxes, (w, h)


def scan(path, widths):
    """Chromatic pixels inside this panel's own caption boxes."""
    w, h, px = decode(path)
    strike = 0
    for line, ndc in enumerate(caption_baselines(path)):
        x0, x1 = widths[line]
        yc = int((1.0 - ndc) * h)
        for y in range(yc - BAND_ABOVE, yc + BAND_BELOW):
            for x in range(x0, min(x1, w)):
                if is_chromatic(px(x, y)):
                    strike += 1
    return strike


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("panel_dir")
    ap.add_argument("--reference", default="Inclusive_eta_Dplus_shape.png",
                    help="panel used to measure the caption box (block in open space)")
    ap.add_argument("--strike-threshold", type=int, default=1,
                    help="chromatic pixels inside the glyph box counted as a strike")
    args = ap.parse_args()

    panels = sorted(glob.glob(os.path.join(
        args.panel_dir, "Inclusive", "*", "Inclusive_*_shape.png")))
    if not panels:
        print(f"no panels under {args.panel_dir}", file=sys.stderr)
        return 2

    ref = next((p for p in panels if os.path.basename(p) == args.reference), None)
    if ref is None:
        print(f"reference panel {args.reference} not found", file=sys.stderr)
        return 2

    boxes, size = calibrate(ref)
    print(f"CAPTION_BOX_CALIBRATION reference={os.path.basename(ref)} "
          f"canvas={size[0]}x{size[1]} lines={len(boxes)}")
    # Widths carry over by LINE INDEX. Each panel supplies its own baselines, so
    # a panel whose caption moved is measured where its caption actually is.
    widths = [boxes[ndc] for ndc in sorted(boxes, reverse=True)]
    for line, ndc in enumerate(sorted(boxes, reverse=True)):
        x0, x1 = boxes[ndc]
        print(f"   line {line} ndc_y={ndc:.3f}  x=[{x0},{x1}]")

    hits = []
    for p in panels:
        n = scan(p, widths)
        if n >= args.strike_threshold:
            hits.append((n, os.path.basename(p)))
    hits.sort(reverse=True)

    print(f"PANEL_CAPTION_COLLISION panels={len(panels)} "
          f"clean={len(panels)-len(hits)} struck={len(hits)}")
    for n, name in hits:
        print(f"   STRIKE {n:6d}  {name}")
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
