#!/usr/bin/env python3
"""A tiny, dependency-free, byte-deterministic SVG writer for paper figures.

WHY NOT MATPLOTLIB. The project digest-pins its outputs and regenerates them
from recipes. Matplotlib's bytes move with its own version, with freetype, and
with which fonts happen to be installed, so a pinned digest would fail on a
different machine for reasons that have nothing to do with the physics. This
emits plain SVG with no external dependency, so the bytes are a pure function of
the input numbers and this file.

DETERMINISM RULES, enforced here rather than left to callers:
  * every coordinate is formatted through `n()` at fixed precision, so
    floating-point noise cannot reach the file;
  * no timestamps, no hostnames, no random ids, no dict-order dependence;
  * fonts are named as generic families, never resolved.

It is not a plotting library and should not grow into one. It draws what the two
paper figures need.
"""
from __future__ import annotations

from typing import Iterable

# Colour-blind-safe, and distinguishable in greyscale by luminance ordering.
TUNE_COLOURS = {
    "MONASH": "#3b6fb0",
    "JUNCTIONS": "#d1712a",
    "CLOSEPACKING": "#4f9a5f",
}
INK = "#1a1a1a"
MUTED = "#6b6b6b"
GRID = "#d8d8d8"


def n(value: float) -> str:
    """Fixed-precision coordinate formatting -- the determinism chokepoint."""
    text = f"{value:.3f}"
    if text == "-0.000":
        text = "0.000"
    return text


def esc(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


class Canvas:
    def __init__(self, width: float, height: float, title: str):
        self.w, self.h = width, height
        self.title = title
        self.parts: list[str] = []

    # ---- primitives -------------------------------------------------------
    def rect(self, x, y, w, h, fill, stroke="none", stroke_width=0.0, opacity=1.0):
        self.parts.append(
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{n(stroke_width)}" '
            f'opacity="{n(opacity)}"/>')

    def line(self, x1, y1, x2, y2, stroke=INK, width=1.0, dash=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" '
            f'stroke="{stroke}" stroke-width="{n(width)}"{d}/>')

    def text(self, x, y, content, size=11.0, anchor="start", fill=INK,
             weight="normal", family="Helvetica, Arial, sans-serif", rotate=None):
        transform = ""
        if rotate is not None:
            transform = f' transform="rotate({n(rotate)} {n(x)} {n(y)})"'
        self.parts.append(
            f'<text x="{n(x)}" y="{n(y)}" font-family="{family}" '
            f'font-size="{n(size)}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{transform}>{esc(content)}</text>')

    def errorbar_v(self, x, ylo, yhi, cap=3.0, stroke=INK, width=1.2):
        self.line(x, ylo, x, yhi, stroke=stroke, width=width)
        self.line(x - cap, ylo, x + cap, ylo, stroke=stroke, width=width)
        self.line(x - cap, yhi, x + cap, yhi, stroke=stroke, width=width)

    # ---- output -----------------------------------------------------------
    def render(self) -> str:
        head = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(self.w)}" '
            f'height="{n(self.h)}" viewBox="0 0 {n(self.w)} {n(self.h)}">\n'
            f'<title>{esc(self.title)}</title>\n'
            f'<rect width="{n(self.w)}" height="{n(self.h)}" fill="#ffffff"/>\n')
        return head + "\n".join(self.parts) + "\n</svg>\n"


class LinearAxis:
    """Value <-> pixel mapping with a chosen, not computed, range.

    The range is an argument rather than derived from the data: a figure whose
    axis silently rescales when a number changes is a figure whose two versions
    cannot be compared by eye.
    """

    def __init__(self, lo: float, hi: float, px_lo: float, px_hi: float):
        if hi <= lo:
            raise ValueError(f"degenerate axis range [{lo}, {hi}]")
        self.lo, self.hi = lo, hi
        self.px_lo, self.px_hi = px_lo, px_hi

    def __call__(self, value: float) -> float:
        frac = (value - self.lo) / (self.hi - self.lo)
        return self.px_lo + frac * (self.px_hi - self.px_lo)


def ticks(lo: float, hi: float, step: float) -> Iterable[float]:
    """Inclusive tick sequence built by integer counting, not accumulation."""
    count = int(round((hi - lo) / step))
    for i in range(count + 1):
        yield lo + i * step
