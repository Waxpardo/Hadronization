#!/usr/bin/env python3
"""The three-tune v3 plotting configuration is generated, not hand-edited.

WHAT THIS GUARDS. The configuration repeats one canvas block ten times with only
the tune, the pad rectangle and the ratio denominator changing. Nothing in the
ROOT stack validates that the ten agree about anything else, so a hand-edit that
gave one canvas a different y-range or a stale `bins_to_ignore` would render, and
would look plausible.

The test requires `bins_to_ignore` to stay empty in every canvas.
The v2 reduced configuration lists ten of the eleven multiplicity classes there.
A canvas built by copying it draws ONE class, faithfully, and nothing in the
stack complains. A source check prevents this copied exclusion from recurring.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GEN = REPO / "plotting/make_hf_run3_v1_three_tune_config.py"
CFG = REPO / ("plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE"
              "_THnSparse_complete_root.json")
MONASH_CFG = REPO / ("plotting/configuration_multiplicity_HF_RUN3_V1_MONASH"
                     "_THnSparse_complete_root.json")

TUNES = ["MONASH", "JUNCTIONS", "CLOSEPACKING"]
failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


check("the generated configuration is committed", CFG.exists(), str(CFG))

# --- it must be exactly what the generator produces -----------------------
r = subprocess.run([sys.executable, str(GEN), "--check"],
                   capture_output=True, text=True)
check("committed configuration matches the generator (--check)",
      r.returncode == 0 and "THREE_TUNE_CONFIG_OK" in r.stdout,
      (r.stdout + r.stderr)[-300:])

cfg = json.loads(CFG.read_text())
canvases = cfg["canvases_to_be_drawn"]

check("all three tunes are configured", cfg["PYTHIA_TUNES"] == TUNES,
      str(cfg["PYTHIA_TUNES"]))
check("ten canvases: three yields plus two ratios, per flavour",
      len(canvases) == 10, str(len(canvases)))

ratios = [c for c in canvases
          if c["draw_function_to_use"] == "drawBalancingPlotsTUNERatios"]
check("four tune-ratio canvases", len(ratios) == 4, str(len(ratios)))
check("every ratio is against MONASH",
      all(c["denominator_TUNE"] == "MONASH" for c in ratios))
check("no ratio takes MONASH as its own numerator",
      all("MONASH" not in c["nominator_TUNES"] for c in ratios))
for tune in ("JUNCTIONS", "CLOSEPACKING"):
    for flavour in ("beauty", "charm"):
        name = f"mini_{flavour}_balancing_{tune}_over_MONASH"
        check(f"ratio canvas {name} exists",
              any(c["canvas_name"] == name for c in ratios))

# --- the B6 defect, pinned -------------------------------------------------
for c in canvases:
    check(f"{c['canvas_name']} ignores no multiplicity class",
          c["bins_to_ignore"] == [], str(len(c["bins_to_ignore"])))
check("every canvas carries all eleven classes",
      {len(c["legend_entries"]) for c in canvases} == {11},
      str({len(c["legend_entries"]) for c in canvases}))

# --- the contract must be v3, not the v2 the reduced configuration carries --
contract = cfg["pair_input_selection_contract"]
check("the selection contract is v3",
      contract.get("v3_analysis_schema") == "paul_pair_objects_primary_ground_v3",
      str(contract.get("v3_analysis_schema")))
check("and carries no v2 schema key",
      "v2_analysis_schema" not in contract)

# --- the pad rectangles must tile, not overlap -----------------------------
# Ten canvases stacked in two columns; two panels sharing a rectangle would
# silently draw over each other.
rects = {}
for c in canvases:
    key = (c["x_min_mini_pad"], c["x_max_mini_pad"],
           c["y_min_mini_pad"], c["y_max_mini_pad"])
    rects.setdefault(key, []).append(c["canvas_name"])
overlapping = {k: v for k, v in rects.items() if len(v) > 1}
check("no two canvases share a pad rectangle", not overlapping,
      str(overlapping))
check("the global canvas draws all ten",
      set(cfg["global_canvases_to_be_drawn"][0]["mini_canvases"])
      == {c["canvas_name"] for c in canvases})

# --- the data paths are inherited from the MONASH v3 configuration ---------
monash = json.loads(MONASH_CFG.read_text())
for key in ("base_dir", "bb_bar_complete_root_dir", "cc_bar_complete_root_dir",
            "bb_bar_complete_root_dir_sub_samples",
            "cc_bar_complete_root_dir_sub_samples", "nSubSamples"):
    check(f"{key} matches the MONASH v3 configuration",
          cfg[key] == monash[key], f"{cfg[key]!r} vs {monash[key]!r}")

print()
if failures:
    for f in failures:
        print("FAIL:", f)
    sys.exit(1)
print("PASS test_three_tune_plot_config.py")
