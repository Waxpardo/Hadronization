#!/usr/bin/env python3
"""Generate the balancing-yield variant configurations from the one axis source.

Three variants of the same observable are under owner evaluation, and none is a
down-selection of another:

  V-FULL        every multiplicity class overlaid (the canvas as it stands)
  V-EXTREMES    the lowest and highest N_ch classes only
  V-INTEGRATED  multiplicity-integrated, one point per species per tune

THE INVERSION TRAP, and why rank is derived from N_ch and never from the label.
The class percentiles are TOP percentiles: the fraction of minimum-bias events
AT OR ABOVE the boundary. A low-activity class therefore carries a LARGE number.
c1 spans 88.2-100.0% and is the LOWEST multiplicity class; c11 spans 0.0-8.4%
and is the HIGHEST. Reading "88.2-100.0%" as "the high one" is the natural
misreading, and a legend that hand-labels the extremes will make it eventually.

So the plain-language rank is derived from `boundary_nch` in
config/multiplicity_class_boundaries_v1.json -- the classes ascend in N_ch, so
the first is lowest and the last is highest -- and the percentile range is
derived, at the one precision constant, by the same rule apply_class_labels.py
uses. Neither half of the legend is transcribed, so neither can drift from the
axis and they cannot disagree with each other.

`--check` reports drift and writes nothing, in the same shape as the
repository's other generators.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOUNDARIES = ROOT / "config" / "multiplicity_class_boundaries_v1.json"
MB_ANCHOR = ROOT / "AnalysisScripts" / "anchors" / "b4_multiplicity_mb"
PLOTTING = ROOT / "plotting"
BASE_CONFIG = PLOTTING / "configuration_multiplicity_HF_RUN3_V1_THREETUNE_POLISH_PROPOSAL.json"
LABEL_TUNE = "MONASH"

# The single precision constant and the single formatting function, shared with
# apply_class_labels.py so two owners cannot render the same percentile
# differently. See tools/class_label_format.py.
sys.path.insert(0, str(ROOT / "tools"))
from class_label_format import (  # noqa: E402
    LABEL_DECIMALS, OWNER_KEY, OWNER_VARIANTS, class_percentile_range,
    format_percentile_range, top_percentiles)


def class_names() -> list[str]:
    """Class names in ASCENDING N_ch, straight from the artifact's own order."""
    artifact = json.loads(BOUNDARIES.read_text())
    classes = artifact["classes"]
    ordered = sorted(classes, key=lambda c: c["boundary_nch"])
    if [c["boundary_nch"] for c in classes] != [c["boundary_nch"] for c in ordered]:
        raise SystemExit(
            "multiplicity_class_boundaries_v1.json is not stored in ascending "
            "boundary_nch order; the rank derivation assumes it is")
    return [c.get("name", f"c{i}") for i, c in enumerate(ordered, 1)]


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
    """The boundary N_ch a class's low-activity percentile edge corresponds to.

    Rank is derived through the ARTIFACT, not from the percentile's magnitude.
    The two orderings are inverses under the top-percentile convention, and
    saying so in code is what stops the inversion being reintroduced by someone
    who reads 88.2% as 'the high one'.
    """
    boundaries = [c["boundary_nch"]
                  for c in json.loads(BOUNDARIES.read_text())["classes"]]
    best, best_gap = None, None
    for pct, nch in zip(percentiles, boundaries):
        gap = abs(pct - value)
        if best_gap is None or gap < best_gap:
            best, best_gap = nch, gap
    return best


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
        digits = ""
        for ch in label[1:]:
            if ch.isdigit():
                digits += ch
            else:
                break
        if not digits:
            raise SystemExit(f"cannot read a class index from binLabel {label!r}")
        return int(digits)

    ranked = sorted(classes,
                    key=lambda b: nch_of_percentile(percentiles,
                                                    b["multiplicityMax"]))
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


def build_extremes(base: dict, percentiles: list[float]) -> dict:
    """V-EXTREMES: the whole axis configured, the two extreme classes drawn."""
    total = len(percentiles)
    lowest, highest = extremes_indices(total)
    keep = {lowest, highest}

    document = json.loads(json.dumps(base))
    classes = document["histograms_to_analyse"]

    def class_index_of(name: str) -> int | None:
        if not name.startswith("c"):
            return None
        digits = ""
        for ch in name[1:]:
            if ch.isdigit():
                digits += ch
            else:
                break
        return int(digits) if digits else None

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
                        if not name.startswith("hDPhic"):
                            continue
                        digits = ""
                        for ch in name[len("hDPhic"):]:
                            if ch.isdigit():
                                digits += ch
                            else:
                                break
                        if not digits:
                            continue
                        index = int(digits)
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

    for canvas in document.get("global_canvases_to_be_drawn", []):
        canvas["write_name"] = canvas["write_name"].replace(
            "THREETUNE", "THREETUNE_VEXTREMES")
        canvas["write_path"] = "plotting/Plots/VariantExtremes"
    document["_comment_variant"] = (
        "V-EXTREMES. The FULL eleven-class axis is configured and validated; "
        "only the lowest and highest N_ch classes are DRAWN, through the same "
        "bins_to_ignore mechanism the other canvas families use. Removing a "
        "class from histograms_to_analyse would still be refused by the axis "
        "contract, and that refusal is deliberate. Rank comes from the position "
        "in ascending boundary_nch, NOT from the percentile: these are TOP "
        "percentiles, so the lowest-multiplicity class carries the largest "
        "number (c1 = 88.2-100.0%). GENERATED; do not hand-edit.")
    return document


def build_integrated(base: dict, percentiles: list[float], closure: bool) -> dict:
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
    verification only and is not a figure.
    """
    document = json.loads(json.dumps(base))
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

    tag = "VINTEGRATED_CLOSURE" if closure else "VINTEGRATED"
    for canvas in document.get("global_canvases_to_be_drawn", []):
        canvas["write_name"] = canvas["write_name"].replace("THREETUNE", "THREETUNE_" + tag)
        canvas["write_path"] = ("plotting/Plots/VariantIntegratedClosure"
                                if closure else "plotting/Plots/VariantIntegrated")
        # write stays True even for the closure configuration: the receipt
        # machinery requires exactly one write path and throws on zero, and
        # running the identical path is the point. Its canvas is a
        # verification artifact, not a figure.
        canvas["write"] = True
    document["_comment_variant"] = (
        "V-INTEGRATED%s. ONE bin spanning multiplicityMin=0 to "
        "multiplicityMax=100, so the counts are integrated by the SELECTION and "
        "calculateOneYield forms the ratio exactly once -- never an average of "
        "per-class ratios. GENERATED by tools/make_variant_configs.py; do not "
        "hand-edit. See docs/V_INTEGRATED_PREREGISTRATION.md."
        % (" closure configuration (verification only, not a figure): carries "
           "the eleven classes AND the integrated bin so one pass emits both "
           "sides of the integer-exact closure" if closure else ""))
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

# Owner ruling 2026-08-18: FOUR REGISTERED ASSOCIATES ONLY. Sigma channels are
# deferred, and the deferral is asymmetric rather than a blanket exclusion --
# see docs/FIGURE_INVENTORY.md 3.3b. Beauty could be built today
# (`BplusSigmabzero.root` and its conjugate sit in the freeze in exactly the
# short trigger form this configuration consumes); charm could not, because the
# D+ trigger has no Sigma_c counterpart and the 36 Sigma_c pairs that do exist
# are D0-triggered, which would be a different figure. Adding either also means
# registering new correlations, which changes the analysed pair set.
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
    (`configuration_multiplicity.json`), and the multiplicity-integrated ratios
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
    keep, seen = [], set()
    for canvas in document.get("canvases_to_be_drawn", []):
        function = canvas.get("draw_function_to_use")
        flavour = canvas.get("FLAVOUR", "")
        if function == "drawBalancingPlots":
            if flavour in seen:
                continue
            seen.add(flavour)
            canvas["canvas_name"] = f"mini_{flavour.lower()}_balancing_baryon_meson_ratio"
            canvas["TUNES"] = list(document["PYTHIA_TUNES"])
            canvas["canvas_title"] = "pp #sqrt{s} = 13.6 TeV"
        keep.append(canvas)
    document["canvases_to_be_drawn"] = keep
    # Re-lay the rows. The base stacks FIVE bands of 0.19 from y=0 to 0.95; this
    # variant keeps three per flavour, so inheriting the coordinates unchanged
    # left the top two bands of the canvas empty. The rows are re-spread over the
    # same extent, in ascending original y, which keeps the two tune-ratio panels
    # ADJACENT AT THE BOTTOM -- the property the 2026-08-16 ruling refused to give
    # up when it rejected variant B, because ratio-against-ratio is the
    # comparison the paper makes.
    TOP, ROWS = 0.95, 3
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
            numerator = (canvas.get("nominator_TUNES") or ["?"])[0]
            denominator = canvas.get("denominator_TUNE", "?")
            canvas["y_axis_title"] = \
                f"{numerator} / {denominator} baryon/meson ratio"
            # The window comes from the measured envelope. See
            # BARYONMESON_TUNE_RATIO_ENVELOPE above for the render that set it.
            canvas["y_min_axis"] = BARYONMESON_TUNE_RATIO_WINDOW[0]
            canvas["y_max_axis"] = BARYONMESON_TUNE_RATIO_WINDOW[1]
            canvas["x_axis_title"] = "multiplicity class"
        else:
            raise SystemExit(f"unexpected draw function {function!r}")

    for canvas in document.get("global_canvases_to_be_drawn", []):
        canvas["canvas_title"] = (
            "baryon/meson balancing-yield ratio in beauty and charm, "
            "three tunes -- pp #sqrt{s} = 13.6 TeV")
        canvas["write_name"] = canvas["write_name"].replace(
            "THREETUNE", "THREETUNE_VBARYONMESON")
        canvas["write_path"] = "plotting/Plots/VariantBaryonMeson"
        canvas["write"] = True

    # Every class is drawn, so the declaration is a count taken from the axis
    # itself rather than a sentence about a subset.
    document["axis_declaration"] = (
        f"all {len(percentiles)} #it{{N}}_{{ch}} classes shown")
    # Declared so apply_class_labels.py can tell whose file this is instead of
    # inferring ownership from a filename glob -- the collision that blocked
    # MERGE_CHECKLIST items A and B.
    document[OWNER_KEY] = OWNER_VARIANTS
    document["_comment_variant"] = (
        "V-BARYONMESON. The baryon/meson balancing-yield ratio per multiplicity "
        "class: Lambda_b / B- and Lambda_c-bar / D-. The DENOMINATOR is resolved "
        "from the pair registry's signed referenceMesonPdg, never named here. "
        "FOUR REGISTERED ASSOCIATES ONLY -- Sigma channels deferred by owner "
        "ruling; beauty is buildable from the freeze today and charm is "
        "trigger-blocked, see docs/FIGURE_INVENTORY.md 3.3b. PROPOSAL awaiting "
        "owner sign-off, not a committed reference. GENERATED by "
        "tools/make_variant_configs.py; do not hand-edit.")
    return document


# The FOUR OS files the hard-coded MONASH correlation canvas draws
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
    """
    document = build_integrated(base, percentiles, closure=False)
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="report drift and exit non-zero; write nothing")
    args = parser.parse_args()

    if not BASE_CONFIG.exists():
        raise SystemExit(f"missing base configuration {BASE_CONFIG}")

    percentiles = top_percentiles()
    names = class_names()
    total = len(percentiles)
    lowest, highest = extremes_indices(total)

    print("VARIANT_AXIS_SOURCE boundaries=%s anchor=nch_mb_%s.csv classes=%d "
          "decimals=%d" % (BOUNDARIES.name, LABEL_TUNE, total, LABEL_DECIMALS))
    print("VARIANT_EXTREMES lowest=%s(%s) highest=%s(%s)  "
          "[rank derived from ascending boundary_nch, not from the percentile]"
          % (names[lowest - 1], percentile_label(lowest, percentiles),
             names[highest - 1], percentile_label(highest, percentiles)))

    base = json.loads(BASE_CONFIG.read_text())
    wanted = {
        PLOTTING / "configuration_multiplicity_HF_RUN3_V1_VEXTREMES.json":
            build_extremes(base, percentiles),
        PLOTTING / "configuration_multiplicity_HF_RUN3_V1_VINTEGRATED.json":
            build_integrated(base, percentiles, closure=False),
        PLOTTING / "configuration_multiplicity_HF_RUN3_V1_VINTEGRATED_CLOSURE.json":
            build_integrated(base, percentiles, closure=True),
        PLOTTING / "configuration_multiplicity_HF_RUN3_V1_VBARYONMESON.json":
            build_baryonmeson(base, percentiles),
        PLOTTING / "configuration_multiplicity_HF_RUN3_V1_VCORRELATIONS.json":
            build_correlations(base, percentiles),
    }

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
