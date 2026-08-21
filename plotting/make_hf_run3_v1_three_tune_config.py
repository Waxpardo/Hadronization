#!/usr/bin/env python3
"""Generate the three-tune HF_RUN3_V1 configuration from the MONASH source.

The generated configuration repeats ten canvases with controlled differences.
It preserves the selection, classes, labels, styles, paths, and empty ignored-bin list.

The generator requires `bins_to_ignore` to remain empty.

THE PAD LAYOUT is the proven 5-row x 2-column stack from the v2 reduced
configuration -- yields for the three tunes on the upper three rows, the two
CR/MONASH ratios beneath them, beauty left and charm right.

Usage:
  plotting/make_hf_run3_v1_three_tune_config.py [--out <path>] [--check]
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / ("plotting/configuration_multiplicity_HF_RUN3_V1_MONASH"
              "_THnSparse_complete_root.json")
DST = REPO / ("plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE"
              "_THnSparse_complete_root.json")

TUNES = ["MONASH", "JUNCTIONS", "CLOSEPACKING"]
FLAVOURS = [("beauty", "BEAUTY"), ("charm", "CHARM")]

# Place beauty left, charm right, tune yields above, and ratios below.
XPAD = {"beauty": (0.05, 0.5), "charm": (0.501, 0.95)}
YPAD_YIELD = {"MONASH": (0.38, 0.569), "JUNCTIONS": (0.57, 0.759),
              "CLOSEPACKING": (0.76, 0.95)}
YPAD_RATIO = {"JUNCTIONS": (0.0, 0.189), "CLOSEPACKING": (0.19, 0.379)}
SHORT = {"JUNCTIONS": "JUN", "CLOSEPACKING": "CLP"}

# The ratio panels' range is MEASURED, not defaulted. Over the four ratio panels
# the 88 drawn bins span 0.6605 to 2.2837 with median 0.9561 (read off the
# canvas macro of the 2026-08-16 run). The first cut of this configuration used
# 0.2-5.0 on a log axis, which spent 61 % of the axis on empty space.
RATIO_Y_MIN, RATIO_Y_MAX = 0.6, 2.5
RATIO_LOG_Y = False

# Exactly one panel carries the legend. The eleven multiplicity classes are the
# same series in all ten panels, so ten copies of the same key is ten times the
# clutter for no extra information. It goes on the top-left panel and is laid
# out in columns so it is a few lines deep rather than eleven.
LEGEND_PANEL = "mini_beauty_balancing_CLOSEPACKING"
LEGEND_COLUMNS = 4
LEGEND_RECT = dict(x_min_legend=0.14, x_max_legend=0.99,
                   y_min_legend=0.70, y_max_legend=0.90)
NO_LEGEND = dict(x_min_legend=-1, x_max_legend=-1,
                 y_min_legend=-1, y_max_legend=-1)

# Every panel names its tune. `canvas_title` is already plumbed to
# hYieldsTemplate->SetTitle, so this needs no drawing-code change: it was empty
# in every canvas, which is why the panels were anonymous.
RATIO_TITLE = {"JUNCTIONS": "JUNCTIONS / MONASH",
               "CLOSEPACKING": "CLOSEPACKING / MONASH"}

# ROOT draws the title at the top of the PAD while the frame is inset by the
# pad margins, so a title needs the top margin to make room for it. The
# inherited 0.03 is ~12 px in a 387 px pad: the first render put the titles on
# the frame line with the top ticks cutting through the lettering.
TOP_MARGIN = 0.10

# The yield panels keep MONASH's log range apart from the floor: at 0.013 the
# Lambda_b series in MONASH sat on the axis line. The data spans 0.0180 to
# 0.2087 across all six yield panels, so 0.010 gives it room underneath without
# changing what is drawn.
YIELD_Y_MIN = 0.010


def build() -> dict:
    src = json.loads(SRC.read_text())
    beauty = next(c for c in src["canvases_to_be_drawn"]
                  if c["FLAVOUR"] == "BEAUTY")
    charm = next(c for c in src["canvases_to_be_drawn"]
                 if c["FLAVOUR"] == "CHARM")
    template = {"beauty": beauty, "charm": charm}

    for name, canvas in template.items():
        if canvas["bins_to_ignore"]:
            raise SystemExit(
                f"FAIL-CLOSED: the {name} template has a non-empty "
                f"bins_to_ignore ({len(canvas['bins_to_ignore'])} entries). "
                "That is the defect that drew a single multiplicity class and "
                "looked correct; refusing to propagate it to ten canvases.")

    out = copy.deepcopy(src)
    out["PYTHIA_TUNES"] = list(TUNES)
    canvases: list[dict] = []

    for low, up in FLAVOURS:
        base = template[low]
        for tune in TUNES:
            c = copy.deepcopy(base)
            c["canvas_name"] = f"mini_{low}_balancing_{tune}"
            c["TUNES"] = [tune]
            c["denominator_TUNE"] = "NONE"
            c["nominator_TUNES"] = []
            c["x_min_mini_pad"], c["x_max_mini_pad"] = XPAD[low]
            c["y_min_mini_pad"], c["y_max_mini_pad"] = YPAD_YIELD[tune]
            c["y_axis_title"] = "yield"
            c["canvas_title"] = tune
            c["top_margin_mini_pad"] = TOP_MARGIN
            c["y_min_axis"] = YIELD_Y_MIN
            c.update(LEGEND_RECT if c["canvas_name"] == LEGEND_PANEL else NO_LEGEND)
            c["legend_columns"] = (LEGEND_COLUMNS
                                   if c["canvas_name"] == LEGEND_PANEL else 1)
            canvases.append(c)
        for tune in ("JUNCTIONS", "CLOSEPACKING"):
            c = copy.deepcopy(base)
            c["canvas_name"] = f"mini_{low}_balancing_{tune}_over_MONASH"
            c["draw_function_to_use"] = "drawBalancingPlotsTUNERatios"
            c["TUNES"] = ["MONASH", tune]
            c["denominator_TUNE"] = "MONASH"
            c["nominator_TUNES"] = [tune]
            c["x_min_mini_pad"], c["x_max_mini_pad"] = XPAD[low]
            c["y_min_mini_pad"], c["y_max_mini_pad"] = YPAD_RATIO[tune]
            c["y_axis_title"] = f"{SHORT[tune]}/MON"
            c["y_min_axis"], c["y_max_axis"] = RATIO_Y_MIN, RATIO_Y_MAX
            c["set_log_y"] = RATIO_LOG_Y
            c["canvas_title"] = RATIO_TITLE[tune]
            c["top_margin_mini_pad"] = TOP_MARGIN
            c.update(NO_LEGEND)
            c["legend_columns"] = 1
            canvases.append(c)

    out["canvases_to_be_drawn"] = canvases
    out["global_canvases_to_be_drawn"] = [{
        "canvas_name": "global_balancing_plots",
        "canvas_title": "balancing in beauty and charm, three tunes",
        "mini_canvases": [c["canvas_name"] for c in canvases],
        "write": True,
        "write_path": "plotting/Plots/THnSparseCompleteRoot_HF_RUN3_V1",
        "write_name": ("global_balancing_plots_multiplicity_HF_RUN3_V1"
                       "_THREETUNE"),
        "x_size_canvas": 2200,
        "y_size_canvas": 2050,
    }]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DST)
    ap.add_argument("--check", action="store_true",
                    help="regenerate and compare rather than write")
    args = ap.parse_args()

    payload = json.dumps(build(), indent=1) + "\n"
    if args.check:
        if not args.out.exists():
            print(f"THREE_TUNE_CONFIG_STALE missing {args.out}")
            return 1
        if args.out.read_text() != payload:
            print(f"THREE_TUNE_CONFIG_STALE {args.out} differs from generated")
            return 1
        print("THREE_TUNE_CONFIG_OK")
        return 0
    args.out.write_text(payload)
    canvases = json.loads(payload)["canvases_to_be_drawn"]
    ratios = [c for c in canvases
              if c["draw_function_to_use"] == "drawBalancingPlotsTUNERatios"]
    print(f"THREE_TUNE_CONFIG_WRITTEN {args.out.name} "
          f"tunes={len(TUNES)} canvases={len(canvases)} ratios={len(ratios)} "
          f"classes={len(canvases[0]['legend_entries'])} "
          f"bins_to_ignore={len(canvases[0]['bins_to_ignore'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
