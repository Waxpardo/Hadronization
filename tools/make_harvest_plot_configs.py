#!/usr/bin/env python3
"""Generate one plotting configuration per closed variation campaign.

Generated, never hand-written. The central eleven-class configuration is the
template; only the campaign tag moves. Three assertions run on every generated
file, and any failure refuses to write it:

  1. the class windows are IDENTICAL to the central's, compared value by value
  2. the boundary artifact's sha256 is the frozen one
  3. every bin name the windows imply parses under the class rule
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "extraction"))
from harvest_class_axis import parse_bin  # noqa: E402

FROZEN_BOUNDARY_SHA = (
    "3b0554fe6c291a26ba03b0524975892754e9a0e75896b203c24d05e853d195b5")
CENTRAL_TAG = "HF_RUN3_V1"


def windows(config_text: str) -> list[tuple[float, float]]:
    lows = [float(m) for m in re.findall(r'"multiplicityMin"\s*:\s*([-\d.]+)', config_text)]
    highs = [float(m) for m in re.findall(r'"multiplicityMax"\s*:\s*([-\d.]+)', config_text)]
    if len(lows) != len(highs) or not lows:
        raise ValueError("multiplicityMin/Max do not pair up")
    return list(zip(lows, highs))


def token(value: float) -> str:
    """The plotter's own percentile spelling: `p` for the decimal point."""
    text = ("%g" % value)
    return text.replace(".", "p")


def implied_bin_names(win: list[tuple[float, float]]) -> list[str]:
    return [f"hDPhic{i}_MB{token(lo)}_{token(hi)}" for i, (lo, hi) in enumerate(win, 1)]


def generate(central: Path, campaign: str, boundary: Path, out_dir: Path) -> Path:
    text = central.read_text()
    central_windows = windows(text)

    digest = hashlib.sha256(boundary.read_bytes()).hexdigest()
    if digest != FROZEN_BOUNDARY_SHA:
        raise SystemExit(
            f"REFUSING: boundary artifact sha256 is {digest}, "
            f"expected {FROZEN_BOUNDARY_SHA}")

    variant = text.replace(CENTRAL_TAG, campaign)
    if variant == text:
        raise SystemExit(f"REFUSING: template carries no {CENTRAL_TAG} tag to replace")
    if campaign in text:
        raise SystemExit(f"REFUSING: template already mentions {campaign}")

    variant_windows = windows(variant)
    if variant_windows != central_windows:
        raise SystemExit(
            "REFUSING: class windows moved.\n"
            f"  central   {central_windows}\n  variant   {variant_windows}")

    for name in implied_bin_names(variant_windows):
        cls, low, high = parse_bin(name)
        if (low, high) not in variant_windows:
            raise SystemExit(f"REFUSING: {name} does not parse back to a window")

    json.loads(variant)          # it must still be valid JSON
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"configuration_multiplicity_{campaign}_THREETUNE_THnSparse_complete_root.json"
    path.write_text(variant)
    print(f"  {campaign:22s} windows={len(variant_windows)} "
          f"sha256={hashlib.sha256(variant.encode()).hexdigest()[:16]} -> {path.name}")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--central", type=Path, required=True)
    ap.add_argument("--boundary", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--campaigns", nargs="+", required=True)
    args = ap.parse_args()
    print(f"template {args.central.name}, {len(windows(args.central.read_text()))} class windows")
    print(f"boundary artifact sha256 asserted: {FROZEN_BOUNDARY_SHA[:16]}...")
    for campaign in args.campaigns:
        generate(args.central, campaign, args.boundary, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
