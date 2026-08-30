#!/usr/bin/env python3
"""Generate balancing-yield variants from the tune-local percentile contract.

Three variants of the same observable are under evaluation, and none is a
down-selection of another:

  V-FULL        every multiplicity class overlaid (the canvas as it stands)
  V-EXTREMES    the lowest and highest N_ch classes only
  V-INTEGRATED  multiplicity-integrated, one point per species per tune

THE INVERSION TRAP, and why rank is derived from N_ch and never from the label.
The class percentiles are TOP percentiles: the fraction of the tune's own
events AT OR ABOVE the boundary. A low-activity class therefore carries a LARGE
number. c1 spans 90.0-100.0% and is the LOWEST multiplicity class; c11 spans
0.0-1.0% and is the HIGHEST. Reading "90.0-100.0%" as "the high one" is the
natural misreading, and a legend that hand-labels the extremes will make it
eventually.

The contract stores c1 through c11 in ascending activity.  Plain-language rank
and percentile text are both derived from that order, so neither can drift from
the configured tune-local axis.

`--check` reports drift and writes nothing, in the same shape as the
repository's other generators.

TWO EMITTED BLOCKS ARE INERT AND STAY THAT WAY. Every canvas carries
`TUNE_colours` and `dependency_line_styles`. Both are PARSED and neither is
READ. `TUNE_colours` is parsed into `colourTUNEMap`
(improvedPlotting_THnSparse.C:2685-2696), which nothing reads, and a known
tune's value is overwritten by the compiled constant before it is even stored
(`:2689-2691`); the palette lives in `plotting/TunePlotStyle.h:24-27`.
`dependency_line_styles` is parsed into `lineStyleDependencyMap` (`:2697-2705`)
and copied into a local at `:4341` and `:4608` that no later line reads: the
class line-style ladder moved into `TunePlotStyle.h` because the configuration's
copy had drifted and gave c1 and c11 the same style (`:3169-3174`). The blocks
are still EMITTED because the parse sites index them with nlohmann's const
`operator[]`, which asserts the key is present -- absence is an assertion
failure or undefined behaviour, not a tolerated default. So they are carried
verbatim and nothing is ever routed through them. Changing a tune colour is a
header edit that re-renders every three-tune figure; it is not a configuration
tweak (owner decision O3).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOUNDARIES = ROOT / "config" / "multiplicity_percentile_classes_v2.json"
PAIR_REGISTRY = ROOT / "config" / "heavy_flavour_pair_registry_v1.json"
PLOTTING = ROOT / "plotting"
BASE_CONFIG = PLOTTING / "configuration_multiplicity_HF_RUN3_V1_THREETUNE_POLISH_PROPOSAL.json"
LABEL_TUNE = "PER_TUNE"

# The single precision constant and the single formatting function, shared with
# apply_class_labels.py so two owners cannot render the same percentile
# differently. See tools/class_label_format.py.
sys.path.insert(0, str(ROOT / "tools"))
from class_label_format import (  # noqa: E402
    LABEL_DECIMALS, OWNER_KEY, OWNER_VARIANTS, class_percentile_range,
    format_percentile_range, top_percentiles)


def class_names() -> list[str]:
    """Class names in ascending event activity."""
    artifact = json.loads(BOUNDARIES.read_text())
    return [row["class"] for row in artifact["classes"]]


# ---------------------------------------------------------------------------
# THE TRIGGER GROUPS AND THE ASSOCIATE SET (ruling R40, corrected 2026-08-30).
#
# R40 restricts the TRIGGERS, not the associates: lightest meson and lightest
# baryon per flavour. Beauty triggers B+ and Lambda_b-bar; charm triggers D+ and
# Lambda_c(+). Each per-flavour balancing figure therefore carries two trigger
# columns, meson left and baryon right, which is what the owner's target
# captions state and what the legacy `*_lambda_trigger` minis composed.
#
# The ASSOCIATES default to the legacy set, taken from
# `plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json`: five
# for beauty, three for charm, identical in both trigger groups of a flavour.
# `ASSOCIATE_SETS` carries the switch so a wider set emits as a new
# configuration version without touching the paper configurations.
#
# EVERY ROUTING NAME BELOW IS A KEY, NOT NOTATION. `associateOS` reaches
# `SetBinLabel` through `DisplayLabelForAssociatePdg`, which is keyed on the PDG
# code the pair registry carries (improvedPlotting_THnSparse.C:1535-1553), so
# the axis text has one source and these strings only have to route.
#
# TWO OF THE LEGACY BEAUTY ASSOCIATES HAVE NO ENTRY IN THAT TABLE. It carries
# 411, 421, 431, 521, 511, 4122 and 5122 with their conjugates, and Sigma_b^0.
# It does NOT carry 531 (B_s^0) or 541 (B_c). Those two associates therefore
# reach the axis as the raw routing keys `B_s^0-bar` and `Bc-`, and the render
# writes one "WARNING: no physics notation for associate PDG" line per point --
# visible in the log, deliberately, rather than silently ugly on a paper figure.
# The repair is two rows in that table, which is a C++ edit and re-render: it is
# outside this generator and outside the consolidation's scope, and it is
# recorded here so the next reader of the axis knows why two bins differ.
MISSING_ASSOCIATE_NOTATION_PDGS = (-531, -541)
#
# THE PROHIBITION AT build_correlations, AND WHY THIS IS NOT IT. That function's
# docstring records a mid-campaign decision: registering pairs changes the
# analysed pair set, which feeds `ResolveReferenceAssociateSelection` and the
# reference meson the block uncertainties are built on, so the correlation
# configuration was isolated rather than allowed to touch the signed-off
# balancing family. Ruling R40 is the owner's later decision that the balancing
# family itself gains the baryon-trigger groups: "the generated balancing
# configurations gain the baryon-trigger pair registrations, per-trigger minis,
# and trigger-column composites". This is that re-authoring, under that ruling.
# The accepted hand-maintained configurations are still not edited, and
# V-CORRELATIONS still builds on the base's own pair set.
TRIGGER_GROUPS = {
    "BEAUTY": (
        {"role": "meson", "trigger": "B^{+}", "prefix": "Bplus",
         "column": "meson_trigger"},
        {"role": "baryon", "trigger": "Lambda_b-bar", "prefix": "Lbbar",
         "column": "baryon_trigger"},
    ),
    "CHARM": (
        {"role": "meson", "trigger": "D^{+}", "prefix": "Dplus",
         "column": "meson_trigger"},
        {"role": "baryon", "trigger": "Lambda_c(+)", "prefix": "Lambdacplus",
         "column": "baryon_trigger"},
    ),
}

# associate routing name -> (OS file stem, SS file stem, SS routing name), per
# trigger prefix. The stems are the legacy short filenames the freeze holds.
_BEAUTY_LEGACY = (
    ("B-", "Bminus", "B^{+}", "Bplus"),
    ("B^{0}-bar", "Bzerobar", "B^{0}", "Bzero"),
    ("B_s^0-bar", "Bszerobar", "B_s^0", "Bszero"),
    ("Bc-", "Bcminus", "Bc+", "Bcplus"),
    ("Lambda_b", "Lb", "Lambda_b-bar", "Lbbar"),
)
_CHARM_LEGACY = (
    ("D-", "Dminus", "D^{+}", "Dplus"),
    ("D^{0}-bar", "Dzerobar", "D^{0}", "Dzero"),
    ("Lambda_c(+)-bar", "Lambdacplusbar", "Lambda_c(+)", "Lambdacplus"),
)

# Beauty Sigma_b, meson trigger only. `docs/GOLDEN_OUTPUTS.md` §9.8 establishes
# `BplusSigmabzero.root` and its conjugate in the freeze, in the short trigger
# form; the Lambda_b-bar trigger's Sigma_b rows carry `legacy_filename: false`
# in the registry, so the freeze does not hold them under a short name. Charm
# Sigma_c is trigger-blocked: the D+ trigger has no Sigma_c counterpart.
_BEAUTY_SIGMA = (("Sigma_b^0", "Sigmabzero", "Sigma_b^0-bar", "Sigmabzerobar"),)

ASSOCIATE_SETS = {
    "legacy": {
        "BEAUTY": {"meson": _BEAUTY_LEGACY, "baryon": _BEAUTY_LEGACY},
        "CHARM": {"meson": _CHARM_LEGACY, "baryon": _CHARM_LEGACY},
    },
    "legacy_sigma": {
        "BEAUTY": {"meson": _BEAUTY_LEGACY + _BEAUTY_SIGMA,
                   "baryon": _BEAUTY_LEGACY},
        "CHARM": {"meson": _CHARM_LEGACY, "baryon": _CHARM_LEGACY},
    },
}
DEFAULT_ASSOCIATE_SET = "legacy"

FLAVOUR_SECTION = {
    "BEAUTY": "beauty_correlations_to_analyse",
    "CHARM": "charm_correlations_to_analyse",
}


def registry_rows() -> dict[str, dict]:
    """Pair-registry rows by filename, refusing a filename registered twice."""
    rows: dict[str, dict] = {}
    for row in json.loads(PAIR_REGISTRY.read_text())["pairs"]:
        name = row["filename"]
        if name in rows:
            raise SystemExit(
                f"pair registry carries {name!r} more than once; a configured "
                f"file must resolve to exactly one row")
        rows[name] = row
    return rows


def trigger_group_configs(flavour: str, group: dict, associates,
                          registry: dict[str, dict]) -> list[dict]:
    """The configured pairs of one trigger group, validated against the registry.

    `ResolveReferenceAssociateSelection` throws unless exactly one configured
    associate carries the group's signed `referenceMesonPdg`
    (improvedPlotting_THnSparse.C:597-644), so the invariant is asserted HERE,
    at emission, rather than discovered by a render that has already started.
    """
    configs, reference_hits = [], []
    reference_pdg = None
    for associate_os, os_stem, associate_ss, ss_stem in associates:
        os_file = f"{group['prefix']}{os_stem}.root"
        ss_file = f"{group['prefix']}{ss_stem}.root"
        for name, sign in ((os_file, "OS"), (ss_file, "SS")):
            row = registry.get(name)
            if row is None:
                raise SystemExit(
                    f"{flavour} trigger group {group['trigger']!r}: "
                    f"{name} is not a pair-registry filename")
            if row["heavy_sign"] != sign:
                raise SystemExit(
                    f"{flavour} trigger group {group['trigger']!r}: {name} is "
                    f"registered {row['heavy_sign']}, configured as {sign}")
        os_row = registry[os_file]
        if reference_pdg is None:
            reference_pdg = os_row["reference_meson_pdg"]
        elif os_row["reference_meson_pdg"] != reference_pdg:
            raise SystemExit(
                f"{flavour} trigger group {group['trigger']!r}: {os_file} "
                f"disagrees with the group on reference_meson_pdg")
        if os_row["associate_pdg"] == reference_pdg:
            reference_hits.append(associate_os)
        configs.append({
            "trigger": group["trigger"],
            "associateOS": associate_os,
            "associateSS": associate_ss,
            "OS": os_file,
            "SS": ss_file,
        })
    if len(reference_hits) != 1:
        raise SystemExit(
            f"{flavour} trigger group {group['trigger']!r} configures "
            f"{len(reference_hits)} associates carrying the signed reference "
            f"meson PDG {reference_pdg}; exactly one is required, and the "
            f"render throws otherwise")
    return configs


def apply_trigger_groups(document: dict, associate_set: str) -> None:
    """Register both trigger groups per flavour, with the selected associates."""
    if associate_set not in ASSOCIATE_SETS:
        raise SystemExit(
            f"unknown associate set {associate_set!r}; "
            f"known: {', '.join(sorted(ASSOCIATE_SETS))}")
    registry = registry_rows()
    chosen = ASSOCIATE_SETS[associate_set]
    for flavour, groups in TRIGGER_GROUPS.items():
        document[FLAVOUR_SECTION[flavour]] = [
            {
                "trigger": group["trigger"],
                "configs": trigger_group_configs(
                    flavour, group, chosen[flavour][group["role"]], registry),
            }
            for group in groups
        ]


def percentile_label(index: int, percentiles: list[float]) -> str:
    """Delegates to the shared primitive; see tools/class_label_format.py."""
    return class_percentile_range(index, percentiles)


def rank_words(index: int, total: int) -> str | None:
    """Plain-language rank, derived from position in ascending N_ch."""
    if index == 1:
        return "lowest #it{N}_{ch} class"
    if index == total:
        return "highest #it{N}_{ch} class"
    return None


def extremes_indices(total: int) -> tuple[int, int]:
    return 1, total


def nch_of_percentile(percentiles: list[float], value: float) -> float:
    """Compatibility helper returning the contract's ascending class rank."""
    best, best_gap = None, None
    for rank, pct in enumerate(percentiles, 1):
        gap = abs(pct - value)
        if best_gap is None or gap < best_gap:
            best, best_gap = float(rank), gap
    return float(best)


def axis_declaration(base_classes: list[dict], drawn: list[dict],
                     percentiles: list[float]) -> str:
    """The line a filtered figure carries about its own axis.

    A figure that shows a subset of the axis must say so ON the figure. The
    numbers come from the boundary artifact and the count from the configuration,
    so the declaration cannot describe an axis the figure does not have.
    """
    total = len(base_classes)
    integrated = [b for b in drawn
                  if b["multiplicityMin"] == 0.0 and b["multiplicityMax"] == 100.0]
    classes = [b for b in drawn if b not in integrated]

    if integrated and not classes:
        lo, hi = 0.0, percentiles[0]
        return (f"multiplicity integrated, "
                f"{lo:.{LABEL_DECIMALS}f}-{hi:.{LABEL_DECIMALS}f}%")

    # Rank each drawn class by the N_ch its low-activity edge maps to, and take
    # the RANGE from the artifact -- never from the config's multiplicityMin /
    # multiplicityMax, which are transcribed labels. Reading them was this
    # function's first version, and it printed 59.9 for a boundary the artifact
    # puts at 59.8: E9's exact defect, regenerated by a generator.
    def index_of(b: dict) -> int:
        label = b.get("binLabel", "")
        by_bin = {
            row["bin"]: index
            for index, row in enumerate(
                json.loads(BOUNDARIES.read_text())["classes"], 1)
        }
        if label not in by_bin:
            raise SystemExit(f"cannot read a class index from binLabel {label!r}")
        return by_bin[label]

    ranked = sorted(classes, key=index_of)
    words = []
    for b in ranked:
        rng = percentile_label(index_of(b), percentiles)
        if b is ranked[0] and len(ranked) > 1:
            words.append(f"lowest ({rng})")
        elif b is ranked[-1] and len(ranked) > 1:
            words.append(f"highest ({rng})")
        else:
            words.append(rng)
    return (f"{len(classes)} of {total} #it{{N}}_{{ch}} classes shown: "
            + ", ".join(words))


def hdphi_names(bins: list[dict]) -> list[str]:
    return [b["hDPhi"] for b in bins]


# ---------------------------------------------------------------------------
# TRIGGER-COLUMN COMPOSITES (ruling R40 as amended; finding F54).
#
# THE LAYOUT. Per flavour, one composite of two columns by four rows: meson
# trigger left, baryon trigger right; from the bottom, one combined-ratio panel
# and then the MONASH, JUNCTIONS and CLOSEPACKING tune panels.
#
# THE COMBINED-RATIO PANEL IS A TEMPLATE COPY, NOT NEW PLOTTING CODE. The legacy
# `mini_*_JUNCTIONS_CLOSEPACKING_over_MONASH` block sets `nominator_TUNES` to a
# LIST and `denominator_TUNE` to MONASH. The parse site reads the list
# (improvedPlotting_THnSparse.C:2616-2626) and the draw loop iterates it,
# colouring each numerator through `ApplyTuneVisualStyle` and writing one legend
# entry per numerator (`:4694-4746`). Both ratios therefore land in one pad with
# the tunes distinguishable, and the macro is not touched.
#
# THE PAD RECTANGLES ARE COMPUTED HERE. The base's ten minis are authored for a
# two-column by five-row layout in which the columns are the two FLAVOURS. A
# per-flavour composite of two TRIGGER columns is a different geometry, and
# reusing the inherited rectangles would place four panels of one column on top
# of each other. The arithmetic is the generator's own, the same shape
# `build_baryonmeson` uses.
#
# THE INCUMBENT GLOBAL IS REPLACED, NEVER SUPPLEMENTED. The macro holds one
# `TPad*` per mini name and `Draw()` RE-PARENTS it, so a mini named by two
# globals renders on the last one and leaves the first canvas empty -- silently,
# with no error. Keeping `global_balancing_plots` beside the per-flavour
# composites would produce exactly that.
TUNE_PANEL_ORDER = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
COMBINED_RATIO_NUMERATORS = ["JUNCTIONS", "CLOSEPACKING"]
COMBINED_RATIO_DENOMINATOR = "MONASH"

COLUMN_X = {
    "meson_trigger": (0.05, 0.5),
    "baryon_trigger": (0.501, 0.95),
}
COMPOSITE_TOP, COMPOSITE_ROWS = 0.95, 4

# Y WINDOWS ARE PER TRIGGER COLUMN, because baryon-trigger yields differ in
# magnitude from meson-trigger yields. The meson column keeps the window the
# signed-off base carries. The baryon column starts from the legacy
# `*_lambda_trigger` minis' own windows
# (plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json).
#
# THESE ARE HARD REFUSALS, NOT DECORATION. `SetPlotPointOrThrow` refuses a point
# outside `[y_min_axis, y_max_axis]`, so a window that does not hold the data
# stops the render and names the point instead of cropping a paper figure. A
# clipped-envelope throw at the deployment is therefore owned by RUN-N under the
# F63 protocol: widen the range HERE, regenerate, re-render -- one iteration, and
# the data is never cropped to the window.
BARYON_COLUMN_YIELD_WINDOW = (0.0001, 0.8)
BARYON_COLUMN_RATIO_WINDOW = (0.0, 2.5)


TRIGGER_COLUMN_COMMENT = (
    "TWO TRIGGER COLUMNS PER FLAVOUR under ruling R40 as amended: meson "
    "trigger left, baryon trigger right, each column carrying the three tune "
    "panels and one combined tune/MONASH ratio panel. Associates are the "
    "legacy set in both columns. The pad rectangles are computed by the "
    "generator, because the base's are authored for a two-column layout whose "
    "columns are the FLAVOURS. The incumbent combined global is REPLACED, not "
    "kept: the macro holds one TPad per mini name and Draw() re-parents, so a "
    "mini named by two globals leaves the first canvas blank without an error. "
    "Y windows are set PER TRIGGER COLUMN; they are hard refusals through "
    "SetPlotPointOrThrow, and a clipped-envelope throw at the deployment is "
    "repaired by widening the range in the generator and re-rendering (the "
    "RUN-N F63 protocol), never by cropping the data.")


def column_rectangles() -> dict[int, tuple[float, float]]:
    """Row index (0 at the bottom) -> (y_min, y_max) of the mini pad."""
    height = COMPOSITE_TOP / COMPOSITE_ROWS
    return {row: (round(row * height, 3), round((row + 1) * height, 3))
            for row in range(COMPOSITE_ROWS)}


def _template_canvases(base: dict) -> dict[str, dict]:
    """One tune panel and one ratio panel from the base, by draw function."""
    templates: dict[str, dict] = {}
    for canvas in base.get("canvases_to_be_drawn", []):
        function = canvas.get("draw_function_to_use")
        if function in ("drawBalancingPlots", "drawBalancingPlotsTUNERatios"):
            templates.setdefault(function, canvas)
    missing = {"drawBalancingPlots", "drawBalancingPlotsTUNERatios"} - set(templates)
    if missing:
        raise SystemExit(
            "the base configuration carries no template canvas for "
            + ", ".join(sorted(missing)))
    return templates


def build_trigger_column_canvases(base: dict) -> list[dict]:
    """Sixteen minis: two flavours, two trigger columns, four rows each."""
    templates = _template_canvases(base)
    rows = column_rectangles()
    canvases: list[dict] = []

    for flavour, groups in TRIGGER_GROUPS.items():
        for group in groups:
            column = group["column"]
            x_min, x_max = COLUMN_X[column]
            baryon = group["role"] == "baryon"

            for row, tune in enumerate(TUNE_PANEL_ORDER, start=1):
                canvas = json.loads(json.dumps(templates["drawBalancingPlots"]))
                canvas["canvas_name"] = (
                    f"mini_{flavour.lower()}_balancing_{tune.lower()}_{column}")
                canvas["FLAVOUR"] = flavour
                canvas["TriggerToUse"] = group["trigger"]
                canvas["TUNES"] = [tune]
                canvas["canvas_title"] = (
                    f"{tune}, {group['trigger']} trigger, "
                    f"pp #sqrt{{s}} = 13.6 TeV")
                canvas["x_min_mini_pad"], canvas["x_max_mini_pad"] = x_min, x_max
                canvas["y_min_mini_pad"], canvas["y_max_mini_pad"] = rows[row]
                if baryon:
                    canvas["y_min_axis"] = BARYON_COLUMN_YIELD_WINDOW[0]
                    canvas["y_max_axis"] = BARYON_COLUMN_YIELD_WINDOW[1]
                canvases.append(canvas)

            ratio = json.loads(
                json.dumps(templates["drawBalancingPlotsTUNERatios"]))
            numerators = "_".join(COMBINED_RATIO_NUMERATORS)
            ratio["canvas_name"] = (
                f"mini_{flavour.lower()}_balancing_{numerators.lower()}"
                f"_over_{COMBINED_RATIO_DENOMINATOR.lower()}_{column}")
            ratio["FLAVOUR"] = flavour
            ratio["TriggerToUse"] = group["trigger"]
            ratio["nominator_TUNES"] = list(COMBINED_RATIO_NUMERATORS)
            ratio["denominator_TUNE"] = COMBINED_RATIO_DENOMINATOR
            # The draw loop reads vTUNES by index, so every tune the panel
            # divides must be configured on it.
            ratio["TUNES"] = [COMBINED_RATIO_DENOMINATOR] + list(
                COMBINED_RATIO_NUMERATORS)
            ratio["canvas_title"] = (
                f"{' and '.join(COMBINED_RATIO_NUMERATORS)} / "
                f"{COMBINED_RATIO_DENOMINATOR}, {group['trigger']} trigger")
            ratio["y_axis_title"] = (
                f"tune / {COMBINED_RATIO_DENOMINATOR} balancing yield")
            ratio["x_min_mini_pad"], ratio["x_max_mini_pad"] = x_min, x_max
            ratio["y_min_mini_pad"], ratio["y_max_mini_pad"] = rows[0]
            if baryon:
                ratio["y_min_axis"] = BARYON_COLUMN_RATIO_WINDOW[0]
                ratio["y_max_axis"] = BARYON_COLUMN_RATIO_WINDOW[1]
            canvases.append(ratio)

    return canvases


def composite_globals(base: dict, write_names: dict[str, str],
                      write_path: str, title: str) -> list[dict]:
    """One global per flavour, each naming only its own eight minis.

    Every configuration's composites share ONE `write_path`: the macro collects
    the distinct output directories of the writing globals and throws "Exactly
    one global-canvas output directory is required to store the
    multiplicity-boundary receipt" on anything but one
    (improvedPlotting_THnSparse.C:2756-2766).
    """
    template = base["global_canvases_to_be_drawn"][0]
    minis = [c["canvas_name"] for c in build_trigger_column_canvases(base)]
    globals_out = []
    for flavour in TRIGGER_GROUPS:
        prefix = f"mini_{flavour.lower()}_"
        owned = [name for name in minis if name.startswith(prefix)]
        if len(owned) != len(TRIGGER_GROUPS[flavour]) * COMPOSITE_ROWS:
            raise SystemExit(
                f"{flavour} composite would carry {len(owned)} minis, expected "
                f"{len(TRIGGER_GROUPS[flavour]) * COMPOSITE_ROWS}")
        canvas = json.loads(json.dumps(template))
        canvas["canvas_name"] = f"global_balancing_plots_{flavour.lower()}"
        canvas["canvas_title"] = title % flavour.lower()
        canvas["mini_canvases"] = owned
        canvas["write"] = True
        canvas["write_path"] = write_path
        canvas["write_name"] = write_names[flavour]
        globals_out.append(canvas)

    shared = {canvas["write_path"] for canvas in globals_out}
    if len(shared) != 1:
        raise SystemExit(
            f"composites of one configuration must share one write_path, "
            f"got {sorted(shared)}")
    names = [canvas["write_name"] for canvas in globals_out]
    if len(set(names)) != len(names):
        raise SystemExit(f"composite write_names are not distinct: {names}")
    return globals_out


def apply_display_filter(document: dict, drawn: list[dict],
                         declaration: str) -> None:
    """Keep the whole axis; ignore the rest for DISPLAY only.

    The axis contract validates the full configured axis before anything is
    drawn -- all eleven artifact classes must be present and tile without gap --
    and it keeps refusing a config that removes one. What changes here is only
    which of the validated bins the canvas draws, through the SAME
    `bins_to_ignore` mechanism the other canvas families already use.
    """
    everything = document["histograms_to_analyse"]
    drawn_names = set(hdphi_names(drawn))
    ignore = [b["hDPhi"] for b in everything if b["hDPhi"] not in drawn_names]
    if not drawn_names:
        raise SystemExit("display filter would leave no bins drawn")
    for canvas in document.get("canvases_to_be_drawn", []):
        canvas["bins_to_ignore"] = list(ignore)
    document["axis_declaration"] = declaration
    # Declared, so apply_class_labels.py can tell whose file this is instead of
    # inferring ownership from a filename glob.
    document[OWNER_KEY] = OWNER_VARIANTS


def build_extremes(base: dict, percentiles: list[float],
                   associate_set: str = DEFAULT_ASSOCIATE_SET) -> dict:
    """V-EXTREMES: the whole axis configured, the two extreme classes drawn."""
    total = len(percentiles)
    lowest, highest = extremes_indices(total)
    keep = {lowest, highest}

    document = json.loads(json.dumps(base))
    apply_trigger_groups(document, associate_set)
    document["canvases_to_be_drawn"] = build_trigger_column_canvases(base)
    classes = document["histograms_to_analyse"]

    class_index = {
        row["bin"]: index
        for index, row in enumerate(
            json.loads(BOUNDARIES.read_text())["classes"], 1)
    }

    def class_index_of(name: str) -> int | None:
        return class_index.get(name)

    drawn = [h for h in classes if class_index_of(h.get("binLabel", "")) in keep]
    if len(drawn) != 2:
        raise SystemExit(f"expected exactly 2 extreme classes, got {len(drawn)}")

    # Legend text for the drawn classes, both halves derived.
    def rewrite_legend(node) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "legend_entries" and isinstance(value, list):
                    for entry in value:
                        name = entry.get("object_name", "")
                        if name not in {"hDPhi" + key for key in class_index}:
                            continue
                        index = class_index[name[len("hDPhi"):]]
                        words = rank_words(index, total)
                        pct = percentile_label(index, percentiles)
                        entry["display_name"] = (
                            f"{words}, {pct}" if words else pct)
                else:
                    rewrite_legend(value)
        elif isinstance(node, list):
            for item in node:
                rewrite_legend(item)

    rewrite_legend(document)
    apply_display_filter(document, drawn,
                         axis_declaration(classes, drawn, percentiles))

    document["global_canvases_to_be_drawn"] = composite_globals(
        base,
        {"BEAUTY": "global_balancing_plots_multiplicity_beauty",
         "CHARM": "global_balancing_plots_multiplicity_charm"},
        "plotting/Plots/VariantExtremes",
        "%s balancing yield in the lowest and highest #it{N}_{ch} classes, "
        "meson and baryon triggers, three tunes -- pp #sqrt{s} = 13.6 TeV")
    document["_comment_variant"] = (
        "V-EXTREMES. The FULL eleven-class axis is configured and validated; "
        "only the lowest and highest N_ch classes are DRAWN, through the same "
        "bins_to_ignore mechanism the other canvas families use. Removing a "
        "class from histograms_to_analyse would still be refused by the axis "
        "contract, and that refusal is deliberate. Rank comes from the contract "
        "order, not from comparing percentile magnitudes. "
        + TRIGGER_COLUMN_COMMENT + " GENERATED; do not hand-edit.")
    return document


def build_integrated(base: dict, percentiles: list[float], closure: bool,
                     associate_set: str | None = DEFAULT_ASSOCIATE_SET) -> dict:
    """V-INTEGRATED: one bin spanning the whole multiplicity axis.

    The integration is done by the SELECTION, not by arithmetic afterwards. A
    bin with multiplicityMin=0 and multiplicityMax=100 makes
    GetCorrelationHistograms project the THnSparse over the full multiplicity
    range, so the macro sums N_OS, N_SS and N_trig first and
    calculateOneYield forms the ratio exactly once. That is the pre-registered
    definition reached through the same code path as every published number --
    no new estimator, and structurally impossible to average per-class ratios.

    `closure=True` keeps the eleven classes alongside the integrated bin so the
    macro emits both sides of the closure in one pass. That configuration is for
    verification only and is not a figure, so it takes the trigger groups -- the
    closure must cover the pair set the figure renders -- and keeps the single
    incumbent global rather than the per-flavour composites.

    `associate_set=None` leaves the base's own pair registrations and canvases
    alone. V-CORRELATIONS builds on this function and then adds its own two
    baryon-triggered groups; registering them here as well would make that
    function refuse its own input.
    """
    document = json.loads(json.dumps(base))
    if associate_set is not None:
        apply_trigger_groups(document, associate_set)
        document["canvases_to_be_drawn"] = build_trigger_column_canvases(base)
    classes = document["histograms_to_analyse"]

    # The integrated bin must differ from the classes in the multiplicity range
    # and in NOTHING else, or it would not be their sum.
    varying = [k for k in classes[0]
               if k not in ("binLabel", "hDPhi", "hTrPt",
                            "multiplicityMin", "multiplicityMax")
               and any(c[k] != classes[0][k] for c in classes)]
    if varying:
        raise SystemExit(
            "class bins disagree on %s; the integrated bin cannot be their sum"
            % ", ".join(sorted(varying)))

    integrated = json.loads(json.dumps(classes[0]))
    integrated["binLabel"] = "M00_100"
    integrated["hDPhi"] = "hDPhiM00_100"
    integrated["hTrPt"] = "hTrPtM00_100"
    integrated["multiplicityMin"] = 0.0
    integrated["multiplicityMax"] = 100.0

    # The axis stays whole in BOTH configurations. The figure differs only
    # in what it draws.
    document["histograms_to_analyse"] = classes + [integrated]

    # The span is derived, not written: the top class's own upper percentile.
    span = format_percentile_range(0.0, percentiles[0])
    label = f"multiplicity integrated, {span}"

    def rewrite_legend(node) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "legend_entries" and isinstance(value, list):
                    template = json.loads(json.dumps(value[0]))
                    template["object_name"] = "hDPhiM00_100"
                    template["display_name"] = label
                    node[key] = value + [template]
                else:
                    rewrite_legend(value)
        elif isinstance(node, list):
            for item in node:
                rewrite_legend(item)

    rewrite_legend(document)

    drawn = classes + [integrated] if closure else [integrated]
    apply_display_filter(document, drawn,
                         axis_declaration(classes, drawn, percentiles))

    if closure or associate_set is None:
        tag = "VINTEGRATED_CLOSURE" if closure else "VINTEGRATED"
        drawn_names = [c["canvas_name"] for c in document["canvases_to_be_drawn"]]
        for canvas in document.get("global_canvases_to_be_drawn", []):
            canvas["write_name"] = canvas["write_name"].replace(
                "THREETUNE", "THREETUNE_" + tag)
            canvas["write_path"] = ("plotting/Plots/VariantIntegratedClosure"
                                    if closure
                                    else "plotting/Plots/VariantIntegrated")
            # write stays True even for the closure configuration: the receipt
            # machinery requires exactly one write path and throws on zero, and
            # running the identical path is the point. Its canvas is a
            # verification artifact, not a figure.
            canvas["write"] = True
            if closure:
                # The closure keeps ONE global, and it must name the minis this
                # configuration actually carries. The trigger-column authoring
                # renamed every one of them, and an inherited list would name
                # ten canvases that no longer exist.
                canvas["mini_canvases"] = list(drawn_names)
    else:
        document["global_canvases_to_be_drawn"] = composite_globals(
            base,
            {"BEAUTY": "global_balancing_plots_integrated_beauty",
             "CHARM": "global_balancing_plots_integrated_charm"},
            "plotting/Plots/VariantIntegrated",
            "multiplicity-integrated %s balancing yield, meson and baryon "
            "triggers, three tunes -- pp #sqrt{s} = 13.6 TeV")

    document["_comment_variant"] = (
        "V-INTEGRATED%s. ONE bin spanning multiplicityMin=0 to "
        "multiplicityMax=100, so the counts are integrated by the SELECTION and "
        "calculateOneYield forms the ratio exactly once -- never an average of "
        "per-class ratios. %sGENERATED by tools/make_variant_configs.py; do not "
        "hand-edit."
        % (" closure configuration (verification only, not a figure): carries "
           "the eleven classes AND the integrated bin so one pass emits both "
           "sides of the integer-exact closure" if closure else "",
           "" if closure else TRIGGER_COLUMN_COMMENT + " "))
    return document


# The baryon whose yield is the NUMERATOR of each flavour's ratio. The
# DENOMINATOR is never named here: `ResolveReferenceAssociateSelection`
# (improvedPlotting_THnSparse.C) resolves it from the pair registry's signed
# `referenceMesonPdg` and throws unless exactly one configured associate carries
# it, so the reference meson is derived from the same registry the yields are,
# not chosen in a configuration file.
BARYON_NUMERATOR = {"BEAUTY": "Lambda_b", "CHARM": "Lambda_c(+)-bar"}

# Physics notation for the legend, in the same style the species panels use
# (#Lambda_{b}^{0}, #bar{#Lambda}_{c}^{-}) rather than the routing identifiers
# the legacy baryon/meson canvas printed. The DENOMINATOR is deliberately absent:
# it is resolved at run time from the registry, so naming it here would be a
# transcription that could drift from the quantity actually divided. The y-axis
# title already says the panel shows a baryon/meson ratio.
BARYON_LEGEND_LABEL = {"BEAUTY": "#Lambda_{b}^{0}", "CHARM": "#bar{#Lambda}_{c}^{-}"}

# Use only the four registered associates.
# Beauty Sigma files exist, but the charm Sigma files use a different trigger.
# Adding either family would change the registered pair selection.
BARYONMESON_DEFERRED_SIGMA = True

# The tune double-ratio window, and the measurement that sets it.
#
# The first build carried over the reviewed yield double-ratio window
# [0.6, 2.5]. The render refused it and named the point:
#
#   ERROR: Plotted uncertainty envelope [2.711630660826422, 2.8484012581559983]
#   is clipped by configured y-axis [0.6, 2.5]: BEAUTY baryon/meson tune double
#   ratio JUNCTIONS/MONASH, associate=Lambda_b, bin=hDPhic9_MB17p124_26p154
#
# The baryon/meson enhancement is larger than the yield enhancement. So the
# window holds the data; the data is not cropped to the window. The envelope
# stays here as a number with a source, because a bare 4.0 tells a later reader
# nothing about what it must contain.
#
# PROVENANCE AND STATUS. The render measured this envelope on the retired class
# axis, in bin hDPhic9_MB17p124_26p154. That bin name belongs to the retired
# axis and has no counterpart in the tune-local percentile contract. The two
# values are a display-only bound: they size the y-axis window and enter no
# result. A re-measurement waits for the first accepted percentile-axis render.
BARYONMESON_TUNE_RATIO_ENVELOPE = (2.711630660826422, 2.8484012581559983)
BARYONMESON_TUNE_RATIO_ENVELOPE_SOURCE = (
    "JUNCTIONS/MONASH, associate=Lambda_b, bin=hDPhic9_MB17p124_26p154, "
    "vbaryonmeson2.log")
BARYONMESON_TUNE_RATIO_WINDOW = (0.0, 4.0)

if not (BARYONMESON_TUNE_RATIO_WINDOW[0] <= BARYONMESON_TUNE_RATIO_ENVELOPE[0]
        and BARYONMESON_TUNE_RATIO_ENVELOPE[1] <= BARYONMESON_TUNE_RATIO_WINDOW[1]):
    raise SystemExit(
        "baryon/meson tune-ratio window %s does not contain the measured "
        "envelope %s (%s)" % (BARYONMESON_TUNE_RATIO_WINDOW,
                              BARYONMESON_TUNE_RATIO_ENVELOPE,
                              BARYONMESON_TUNE_RATIO_ENVELOPE_SOURCE))


def build_baryonmeson(base: dict, percentiles: list[float]) -> dict:
    """V-BARYONMESON: the baryon/meson balancing-yield ratio vs multiplicity class.

    Derived from the signed-off base rather than authored, so pad geometry,
    legend placement and the eleven class entries are the ones already reviewed;
    what changes is the quantity drawn and the axis it needs.

    The y-range is NOT a free hand. `SetPlotPointOrThrow` refuses a point outside
    `[y_min_axis, y_max_axis]`, so a range that does not contain the data fails
    the render loudly instead of silently clipping a paper figure. The linear
    0-1 window is the one the legacy baryon/meson canvas used
    (the excluded legacy two-tune configuration), and the multiplicity-integrated ratios
    measured on V-INTEGRATED sit between roughly 0.1 and 0.42, so it holds them
    with room; if a class ever leaves it, the render says so.
    """
    document = json.loads(json.dumps(base))

    # ONE yield panel per flavour, not one per tune. drawBalancingPlots filters
    # its tunes with `isInVector(TUNE, vCanvasTUNES)`; the baryon/meson function
    # has no such filter and draws every configured tune on whatever canvas it is
    # given. Deriving three per-tune panels from the base therefore produced
    # three IDENTICAL all-tune panels, each captioned with a different tune --
    # a caption that disagreed with its own contents. The function's shape is one
    # panel carrying all three, which is also how the legacy canvas was built.
    # TWO ROWS PER FLAVOUR (F60). The base yields three: one ratio panel and two
    # SEPARATE tune-ratio panels. The content contract asks for one ratio panel
    # above ONE combined tune-ratio panel carrying both numerators, exactly as
    # G4-G7 do, so the second tune-ratio panel is dropped and the first is
    # re-authored to the list form the draw loop already handles.
    keep, seen_yield, seen_ratio = [], set(), set()
    for canvas in document.get("canvases_to_be_drawn", []):
        function = canvas.get("draw_function_to_use")
        flavour = canvas.get("FLAVOUR", "")
        if function == "drawBalancingPlots":
            if flavour in seen_yield:
                continue
            seen_yield.add(flavour)
            canvas["canvas_name"] = f"mini_{flavour.lower()}_balancing_baryon_meson_ratio"
            canvas["TUNES"] = list(document["PYTHIA_TUNES"])
            canvas["canvas_title"] = "pp #sqrt{s} = 13.6 TeV"
        elif function == "drawBalancingPlotsTUNERatios":
            if flavour in seen_ratio:
                continue
            seen_ratio.add(flavour)
            numerators = "_".join(COMBINED_RATIO_NUMERATORS)
            canvas["canvas_name"] = (
                f"mini_{flavour.lower()}_balancing_baryon_meson_ratio_"
                f"{numerators.lower()}_over_"
                f"{COMBINED_RATIO_DENOMINATOR.lower()}")
            canvas["nominator_TUNES"] = list(COMBINED_RATIO_NUMERATORS)
            canvas["denominator_TUNE"] = COMBINED_RATIO_DENOMINATOR
            canvas["TUNES"] = [COMBINED_RATIO_DENOMINATOR] + list(
                COMBINED_RATIO_NUMERATORS)
            canvas["canvas_title"] = (
                f"{' and '.join(COMBINED_RATIO_NUMERATORS)} / "
                f"{COMBINED_RATIO_DENOMINATOR}")
        keep.append(canvas)
    document["canvases_to_be_drawn"] = keep

    # Two retained rows per flavour, spread over the original extent.
    TOP, ROWS = 0.95, 2
    for flavour_x in sorted({c["x_min_mini_pad"] for c in keep}):
        column = sorted((c for c in keep if c["x_min_mini_pad"] == flavour_x),
                        key=lambda c: c["y_min_mini_pad"])
        if len(column) != ROWS:
            raise SystemExit(
                f"expected {ROWS} baryon/meson panels per flavour, got {len(column)}")
        height = TOP / ROWS
        for row, canvas in enumerate(column):
            canvas["y_min_mini_pad"] = round(row * height, 3)
            canvas["y_max_mini_pad"] = round((row + 1) * height, 3)

    # Rebuild the panel list in flavour blocks -- ratio panel of a flavour
    # directly beneath its yield panel -- rather than filtering the base's order
    # and patching, which left charm's panel above beauty's.
    for global_canvas in document.get("global_canvases_to_be_drawn", []):
        names = [c["canvas_name"] for c in keep]
        ordered = []
        for flavour in ("beauty", "charm"):
            ordered += [n for n in names
                        if n == f"mini_{flavour}_balancing_baryon_meson_ratio"]
            ordered += [n for n in names
                        if n.startswith(f"mini_{flavour}_") and "_over_" in n]
        if sorted(ordered) != sorted(names):
            raise SystemExit("baryon/meson panel ordering dropped or duplicated a canvas")
        global_canvas["mini_canvases"] = ordered

    for canvas in document.get("canvases_to_be_drawn", []):
        flavour = canvas.get("FLAVOUR", "")
        baryon = BARYON_NUMERATOR.get(flavour)
        if baryon is None:
            raise SystemExit(f"no baryon numerator registered for {flavour!r}")
        canvas["baryons_to_plot_in_baryon/meson_ratio"] = [baryon]

        function = canvas.get("draw_function_to_use")
        if function == "drawBalancingPlots":
            canvas["draw_function_to_use"] = "drawBalancingBaryonMesonRatioPlots"
            canvas["y_axis_title"] = "baryon / meson balancing yield"
            canvas["y_min_axis"] = 0.0
            canvas["y_max_axis"] = 1.0
            canvas["set_log_y"] = False
            # The x axis is the multiplicity class, not the associate species --
            # the inherited title described the base canvas, where each point was
            # a different associate. Here every point is a class and the single
            # associate is the one named in the legend.
            canvas["x_axis_title"] = "multiplicity class"
            # This function keys its legend on the ASSOCIATE name, while the
            # inherited entries are keyed on bin names, so the lookup missed and
            # the panel printed "Not drawing legend" -- three tunes on one pad
            # with nothing to tell them apart. One entry per drawn baryon; the
            # function appends " (TUNE)" itself, which is what identifies them.
            # APPEND, never replace. The same map is read twice for two
            # different purposes: this function looks up the ASSOCIATE name to
            # build the legend, and DisplayLabelForMultiplicityBin looks up the
            # BIN name to label the x axis. Replacing the eleven class entries
            # with the one baryon entry produced a correct legend and sent the
            # axis back to printing c1_MB88p197_100.
            canvas["legend_entries"] = list(canvas.get("legend_entries", [])) + [{
                "object_name": baryon,
                "display_name": BARYON_LEGEND_LABEL[flavour],
            }]
            canvas["x_min_legend"] = 0.20
            canvas["x_max_legend"] = 0.52
            canvas["y_min_legend"] = 0.62
            canvas["y_max_legend"] = 0.88
        elif function == "drawBalancingPlotsTUNERatios":
            canvas["draw_function_to_use"] = \
                "drawBalancingBaryonMesonRatioPlotsTUNERatios"
            denominator = canvas.get("denominator_TUNE", "?")
            # One pad now carries both numerators, so the axis names the
            # denominator and the legend identifies each numerator.
            canvas["y_axis_title"] = \
                f"tune / {denominator} baryon/meson ratio"
            # The window comes from the measured envelope. See
            # BARYONMESON_TUNE_RATIO_ENVELOPE above for the render that set it.
            canvas["y_min_axis"] = BARYONMESON_TUNE_RATIO_WINDOW[0]
            canvas["y_max_axis"] = BARYONMESON_TUNE_RATIO_WINDOW[1]
            canvas["x_axis_title"] = "multiplicity class"
        else:
            raise SystemExit(f"unexpected draw function {function!r}")

    globals_out = document.get("global_canvases_to_be_drawn", [])
    if len(globals_out) != 1:
        raise SystemExit(
            f"V-BARYONMESON expects one global canvas, got {len(globals_out)}")
    for canvas in globals_out:
        canvas["canvas_title"] = (
            "baryon/meson balancing-yield ratio in beauty and charm, "
            "three tunes -- pp #sqrt{s} = 13.6 TeV")
        canvas["write_name"] = "global_balancing_baryon_over_meson_ratio_multiplicity"
        canvas["write_path"] = "plotting/Plots/VariantBaryonMeson"
        canvas["write"] = True

    # Every class is drawn, so the declaration is a count taken from the axis
    # itself rather than a sentence about a subset.
    document["axis_declaration"] = (
        f"all {len(percentiles)} #it{{N}}_{{ch}} classes shown")
    # Declare the generator so apply_class_labels.py does not infer it from the filename.
    document[OWNER_KEY] = OWNER_VARIANTS
    document["_comment_variant"] = (
        "V-BARYONMESON. The baryon/meson balancing-yield ratio per multiplicity "
        "class: Lambda_b / B- and Lambda_c-bar / D-. The DENOMINATOR is resolved "
        "from the pair registry's signed referenceMesonPdg, never named here. "
        "MESON TRIGGER ONLY: ruling R40 gives the balancing figures two trigger "
        "columns and leaves this one on the meson trigger, matching the target "
        "figure. FOUR REGISTERED ASSOCIATES ONLY -- Sigma channels deferred by "
        "recorded decision; beauty is buildable from the freeze today and "
        "charm is trigger-blocked. TWO ROWS PER FLAVOUR: the ratio panel above "
        "ONE combined tune-ratio panel carrying both numerators, which is the "
        "shape the content contract asks for and the same template copy the "
        "integrated and extremes composites use. The file's earlier 'PROPOSAL "
        "awaiting physics sign-off' status is RESOLVED: ruling R40 of "
        "2026-08-30 is the supervisor sign-off, relayed by the owner. "
        "GENERATED by tools/make_variant_configs.py; do not hand-edit.")
    return document


# The four OS files that the fixed MONASH correlation canvas draws.
# (improvedPlotting_THnSparse.C, the drawThisCorrelation gate). Two are already
# registered for the balancing family; the two baryon-TRIGGERED ones are not,
# and without them the canvas's baryon pads draw nothing while the render still
# reports success.
CORRELATION_OS_FILES = (
    "BplusBminus.root", "LbbarBminus.root",
    "DplusDminus.root", "LambdacplusDminus.root",
)

# The baryon-triggered groups to add. Trigger and associate are read off the
# pair filenames the gate names -- Lambda_c(+) against D-, Lambda_b-bar against
# B- -- which is the direction 3.2's input line states and the OPPOSITE of the
# balancing family's D+ -> Lambda_c-bar registration.
CORRELATION_EXTRA_GROUPS = {
    "charm_correlations_to_analyse": {
        "trigger": "Lambda_c(+)",
        "configs": [{
            "trigger": "Lambda_c(+)",
            "associateOS": "D-", "associateSS": "D^{+}",
            "OS": "LambdacplusDminus.root", "SS": "LambdacplusDplus.root",
        }],
    },
    "beauty_correlations_to_analyse": {
        "trigger": "Lambda_b-bar",
        "configs": [{
            "trigger": "Lambda_b-bar",
            "associateOS": "B-", "associateSS": "B^{+}",
            "OS": "LbbarBminus.root", "SS": "LbbarBplus.root",
        }],
    },
}


def build_correlations(base: dict, percentiles: list[float]) -> dict:
    """V-CORRELATIONS: an ISOLATED configuration for the Delta-phi canvases.

    Separate by design. The correlation canvas is hard-coded in the macro -- pad
    layout, log-y and the output stem `<FLAVOUR>Correlations_MONASH`, which is
    exactly the manuscript's filename -- and needs nothing authored. What it does
    need is two extra registered pairs, and registering pairs changes the
    analysed pair set, which feeds `ResolveReferenceAssociateSelection` and the
    reference meson the block uncertainties are built on. That must not touch the
    signed-off balancing family, so it lives in its own file and its own output
    directory and the balancing configurations are left exactly as they are.

    The macro's own gate requires an INTEGRATED multiplicity bin, so this is
    built on the integrated shape rather than the eleven-class one.

    Built with `associate_set=None`, so the base's own pair registrations and
    canvases arrive untouched and the two groups added below are the only ones
    this configuration carries. Ruling R40 gave the BALANCING configurations
    their baryon-trigger groups; this one keeps its own isolated pair set, which
    is the four OS files the hard-coded correlation gate names and nothing else.
    """
    document = build_integrated(base, percentiles, closure=False,
                                associate_set=None)
    document["draw_correlation_plots"] = True

    for key, group in CORRELATION_EXTRA_GROUPS.items():
        groups = document.get(key, [])
        existing = {entry.get("trigger") for entry in groups}
        if group["trigger"] in existing:
            raise SystemExit(f"{group['trigger']} already registered in {key}")
        groups.append(json.loads(json.dumps(group)))
        document[key] = groups

    # Fail here rather than after a render that quietly drew half a figure.
    registered = set()
    for key in ("charm_correlations_to_analyse", "beauty_correlations_to_analyse"):
        for entry in document.get(key, []):
            for configured in entry.get("configs", []):
                registered.add(configured["OS"])
    missing = [name for name in CORRELATION_OS_FILES if name not in registered]
    if missing:
        raise SystemExit(
            "correlation configuration does not register: " + ", ".join(missing))

    for canvas in document.get("global_canvases_to_be_drawn", []):
        canvas["write_name"] = canvas["write_name"].replace(
            "THREETUNE_VINTEGRATED", "THREETUNE_VCORRELATIONS")
        canvas["write_path"] = "plotting/Plots/VariantCorrelations"
        canvas["write"] = True
    document["_comment_variant"] = (
        "V-CORRELATIONS. Delta-phi angular correlations, MONASH only -- the "
        "macro gates the draw on TUNE == MONASH, so the hard-coded "
        "<FLAVOUR>Correlations_MONASH stem is honest. Registers exactly the four "
        "OS pair files that gate names, which means TWO BARYON-TRIGGERED PAIRS "
        "the balancing family does not carry; that is why this configuration is "
        "separate and why the balancing files are untouched. Its balancing "
        "canvases are a by-product of the same pass and are written to their own "
        "directory. GENERATED by tools/make_variant_configs.py; do not hand-edit.")
    return document


def variant_documents(base: dict, percentiles: list[float],
                      associate_set: str) -> dict[Path, dict]:
    """Path -> document for one associate set.

    The DEFAULT set emits the five tracked configurations. Any other set emits
    under a version-suffixed filename and is otherwise unused, so a wider
    associate axis is a new configuration version rather than an edit to the
    paper's own files (ruling R40's switch).
    """
    suffix = ("" if associate_set == DEFAULT_ASSOCIATE_SET
              else "_" + associate_set)

    def path(stem: str) -> Path:
        return PLOTTING / f"configuration_multiplicity_HF_RUN3_V1_{stem}{suffix}.json"

    return {
        path("VEXTREMES"): build_extremes(base, percentiles, associate_set),
        path("VINTEGRATED"):
            build_integrated(base, percentiles, False, associate_set),
        path("VINTEGRATED_CLOSURE"):
            build_integrated(base, percentiles, True, associate_set),
        path("VBARYONMESON"): build_baryonmeson(base, percentiles),
        path("VCORRELATIONS"): build_correlations(base, percentiles),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="report drift and exit non-zero; write nothing")
    parser.add_argument("--associate-set", default=DEFAULT_ASSOCIATE_SET,
                        choices=sorted(ASSOCIATE_SETS),
                        help="associate axis for the balancing configurations; "
                             "the default emits the tracked files, any other "
                             "value emits a new configuration version")
    args = parser.parse_args()

    if not BASE_CONFIG.exists():
        raise SystemExit(f"missing base configuration {BASE_CONFIG}")

    percentiles = top_percentiles()
    names = class_names()
    total = len(percentiles)
    lowest, highest = extremes_indices(total)

    print("VARIANT_AXIS_SOURCE contract=%s scope=%s classes=%d decimals=%d"
          % (BOUNDARIES.name, LABEL_TUNE, total, LABEL_DECIMALS))
    print("VARIANT_EXTREMES lowest=%s(%s) highest=%s(%s)  "
          "[rank derived from the contract's ascending-activity order]"
          % (names[lowest - 1], percentile_label(lowest, percentiles),
             names[highest - 1], percentile_label(highest, percentiles)))
    print("VARIANT_ASSOCIATE_SET name=%s beauty=%d charm=%d triggers=%s"
          % (args.associate_set,
             len(ASSOCIATE_SETS[args.associate_set]["BEAUTY"]["meson"]),
             len(ASSOCIATE_SETS[args.associate_set]["CHARM"]["meson"]),
             ",".join(group["trigger"]
                      for groups in TRIGGER_GROUPS.values()
                      for group in groups)))

    base = json.loads(BASE_CONFIG.read_text())
    wanted = variant_documents(base, percentiles, args.associate_set)

    drift: list[str] = []
    for path, document in wanted.items():
        text = json.dumps(document, indent=4) + "\n"
        if path.exists() and path.read_text() == text:
            continue
        drift.append(f"{path.name}: "
                     f"{'differs from' if path.exists() else 'missing'} "
                     f"a fresh generation")
        if not args.check:
            path.write_text(text)

    if not drift:
        print("VARIANT_CONFIGS_CURRENT files=%d" % len(wanted))
        return 0
    for line in drift:
        print("  " + line)
    if args.check:
        print("VARIANT_CONFIGS_STALE count=%d; run without --check to "
              "regenerate" % len(drift))
        return 1
    print("VARIANT_CONFIGS_WRITTEN count=%d" % len(drift))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
