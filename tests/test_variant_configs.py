#!/usr/bin/env python3
"""The variant configurations must stay generated, and must not invert the rank.

Two things are pinned here.

1. `tools/make_variant_configs.py --check` is clean, so a hand-edit to a variant
   configuration is caught the way every other generated artifact's is.

2. The extreme classes carry the rank the AXIS gives them, not the rank their
   label looks like. The percentiles are TOP percentiles, so the lowest-activity
   class carries the LARGEST number: c1 spans 88.2-100.0% and is the LOWEST
   multiplicity class. A legend that read the percentile as the rank would call
   it the highest, and it would look entirely reasonable on the page.

   This test asserts the pairing directly: the class with the SMALLEST
   boundary_nch must be the one whose legend says "lowest", and it must be the
   one carrying the largest percentile.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "tools" / "make_variant_configs.py"
EXTREMES = ROOT / "plotting" / "configuration_multiplicity_HF_RUN3_V1_VEXTREMES.json"
BOUNDARIES = ROOT / "config" / "multiplicity_class_boundaries_v1.json"


def legend_entries(document) -> dict[str, str]:
    found: dict[str, str] = {}

    def walk(node) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "legend_entries" and isinstance(value, list):
                    for entry in value:
                        name = entry.get("object_name")
                        if name:
                            found[name] = entry.get("display_name", "")
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(document)
    return found


def main() -> int:
    if not EXTREMES.exists():
        print(f"missing {EXTREMES.name}; run tools/make_variant_configs.py",
              file=sys.stderr)
        return 1

    check = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    if check.returncode != 0:
        print("variant configurations have drifted from their generator:")
        print(check.stdout.decode(errors="replace"))
        return 1

    document = json.loads(EXTREMES.read_text())

    # The FULL axis is configured; only the DISPLAY is restricted. Asserting
    # two bins here was right for the earlier design, which deleted the other
    # nine -- and which the axis contract correctly refused to render.
    bins = [h["binLabel"] for h in document["histograms_to_analyse"]]
    ignore = set()
    for canvas in document.get("canvases_to_be_drawn", []):
        ignore |= set(canvas.get("bins_to_ignore", []))
    drawn = [h["binLabel"] for h in document["histograms_to_analyse"]
             if h["hDPhi"] not in ignore]
    if len(drawn) != 2:
        print(f"V-EXTREMES must DRAW exactly two classes, draws {len(drawn)}: {drawn}")
        return 1
    if len(bins) < len(drawn):
        print("configured axis smaller than the drawn set")
        return 1

    classes = json.loads(BOUNDARIES.read_text())["classes"]
    lowest_nch = min(c["boundary_nch"] for c in classes)
    highest_nch = max(c["boundary_nch"] for c in classes)
    lowest_index = [c["boundary_nch"] for c in classes].index(lowest_nch) + 1
    highest_index = [c["boundary_nch"] for c in classes].index(highest_nch) + 1

    entries = legend_entries(document)
    by_index = {}
    for name, label in entries.items():
        if not name.startswith("hDPhic"):
            continue
        digits = ""
        for ch in name[len("hDPhic"):]:
            if ch.isdigit():
                digits += ch
            else:
                break
        if digits:
            by_index[int(digits)] = label

    failures = []

    low_label = by_index.get(lowest_index, "")
    high_label = by_index.get(highest_index, "")

    if "lowest" not in low_label:
        failures.append(
            f"class {lowest_index} has the smallest boundary_nch ({lowest_nch}) "
            f"so its legend must say 'lowest'; it says {low_label!r}")
    if "highest" not in high_label:
        failures.append(
            f"class {highest_index} has the largest boundary_nch ({highest_nch}) "
            f"so its legend must say 'highest'; it says {high_label!r}")

    # The inversion itself: the LOWEST-N_ch class must carry the LARGER
    # percentile. If someone ever derives rank from the percentile, this flips.
    def leading_percentile(label: str) -> float:
        tail = label.split(",")[-1].strip().rstrip("%")
        return float(tail.split("-")[-1])

    if low_label and high_label:
        if not leading_percentile(low_label) > leading_percentile(high_label):
            failures.append(
                "top-percentile convention violated: the lowest-N_ch class must "
                f"carry the LARGER percentile, got low={low_label!r} "
                f"high={high_label!r}")

    if failures:
        for line in failures:
            print("FAIL: " + line)
        return 1

    print(f"variant configs current; extremes rank correct "
          f"(c{lowest_index}={low_label!r}, c{highest_index}={high_label!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
