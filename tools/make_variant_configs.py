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
(improvedPlotting_THnSparse.C:3326-3337), which nothing reads, and a known
tune's value is overwritten by the compiled constant before it is even stored
(`:2747-2749`); the palette lives in `plotting/TunePlotStyle.h:24-27`.
`dependency_line_styles` is parsed into `lineStyleDependencyMap` (`:2755-2763`)
and copied into a local at `:4401` and `:4668` that no later line reads: the
class line-style ladder moved into `TunePlotStyle.h` because the configuration's
copy had drifted and gave c1 and c11 the same style (`:3229-3234`). The blocks
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


DEPENDENCIES_CONF = ROOT / "config" / "dependencies.conf"
TUNE_CARD_DIR = ROOT / "generation" / "cards"


def class_names() -> list[str]:
    """Class names in ascending event activity."""
    artifact = json.loads(BOUNDARIES.read_text())
    return [row["class"] for row in artifact["classes"]]


# THE INFORMATION BLOCK'S FIRST LINE IS DERIVED, NEVER TYPED (ruling R46,
# item 2). It states the generator, the collision system and the beam energy
# once per figure, and each of those three facts is READ from the artifact
# that already owns it:
#
#   generator version  config/dependencies.conf, `HF_PYTHIA8_VERSION`
#   beam energy        generation/cards/pythiasettings_*.cmnd, `Beams:eCM`
#
# WHY READ RATHER THAN TYPE. Before R46 the string `pp #sqrt{s} = 13.6 TeV`
# was typed into three separate title templates in this file. Three copies of
# a number that the cards own is three chances to disagree with the campaign
# that produced the points. The block is now the ONE place the figures state
# it, and it cannot state an energy the cards do not carry.
#
# THE THREE CARDS MUST AGREE, and disagreement is a refusal rather than a
# choice: the tunes differ in hadronisation, not in beam. A fourth card added
# with a different `Beams:eCM` stops the generator instead of silently
# labelling every figure with one tune's beam.

def pythia_version() -> str:
    """The generator version the campaign pins, from the dependency file."""
    for line in DEPENDENCIES_CONF.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "HF_PYTHIA8_VERSION" not in stripped:
            continue
        _, _, tail = stripped.partition("HF_PYTHIA8_VERSION")
        version = tail.strip().lstrip(":=").strip().strip('"}').strip()
        if version:
            return version
    raise SystemExit(
        f"{DEPENDENCIES_CONF.name}: no HF_PYTHIA8_VERSION; the information "
        f"block cannot state a generator version this repository does not pin")


def beam_energy_tev() -> str:
    """`Beams:eCM` from the tune cards, in TeV, with the tunes required equal."""
    cards = sorted(TUNE_CARD_DIR.glob("pythiasettings_Hard_Low_ccbb_*.cmnd"))
    if not cards:
        raise SystemExit(f"{TUNE_CARD_DIR}: no tune cards to read Beams:eCM from")
    energies: dict[str, str] = {}
    for card in cards:
        for line in card.read_text().splitlines():
            head = line.split("!", 1)[0].strip()
            if not head.startswith("Beams:eCM"):
                continue
            _, _, value = head.partition("=")
            energies[card.name] = value.strip()
            break
    if len(energies) != len(cards):
        missing = sorted(c.name for c in cards if c.name not in energies)
        raise SystemExit(f"tune cards carry no Beams:eCM: {', '.join(missing)}")
    distinct = set(energies.values())
    if len(distinct) != 1:
        raise SystemExit(
            f"tune cards disagree on Beams:eCM ({energies}); the information "
            f"block states one beam energy for the whole figure and will not "
            f"choose between them")
    gev = float(distinct.pop())
    tev = gev / 1000.0
    # 13600 GeV prints as 13.6, not 13.60: the trailing zero is not measured.
    return f"{tev:g}"


def information_block_line() -> str:
    """Line 1 of every figure's information block: generator, system, energy."""
    return (f"PYTHIA {pythia_version()}, "
            f"pp #sqrt{{s}} = {beam_energy_tev()} TeV")


def information_block(coverage: str) -> list[str]:
    """The whole block, top-left of a canvas, one line per element.

    Line 1 identifies the campaign; line 2 is the axis-coverage sentence the
    figure already carried, unchanged. The macro draws the list as a stack at
    the anchor the single line used (`improvedPlotting_THnSparse.C:2137-2167`)
    and echoes every line on `AXIS_DECLARATION`, so a style-delta proof still
    reads the coverage sentence it read before.
    """
    return [information_block_line(), coverage]


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
# code the pair registry carries (improvedPlotting_THnSparse.C:1570-1588), so
# the axis text has one source and these strings only have to route.
#
# TWO OF THE LEGACY BEAUTY ASSOCIATES ONCE HAD NO ENTRY IN THAT TABLE, and now
# do. At the R40 extension it carried 411, 421, 431, 521, 511, 4122 and 5122
# with their conjugates, and Sigma_b^0, but not 531 (B_s^0) or 541 (B_c), so
# those two reached the axis as the raw routing keys `B_s^0-bar` and `Bc-` with
# one "WARNING: no physics notation for associate PDG" line per point. CON-1B
# item 3 added the four rows (+-531, +-541) in TLatex, and
# `tests/test_associate_display_labels.py` now asserts that every associateOS
# PDG a tracked configuration registers has an entry -- so a future associate
# set cannot reintroduce the raw-key axis silently.
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
#
# `trigger` IS A ROUTING KEY. `label` IS NOTATION. They are separate fields
# because they have different jobs and only one of them may change.
#
# `trigger` reaches the render as `TriggerToUse`
# (`build_trigger_column_canvases`, the `canvas["TriggerToUse"]` assignment),
# which selects the trigger. Two of the four values are not notation --
# `Lambda_b-bar` and `Lambda_c(+)` -- and until FIG-1 the panel TITLE was built
# from the same value, so G4 to G7 printed "Lambda_c(+) trigger" in plain text
# on eight panel titles per composite (ruling R45, checklist item 2).
#
# The routing key is NOT renamed. It is the selector, and the delivered
# configurations, the pair registry and the render logs all spell it this way.
# The title takes `label` instead, so notation is fixed where notation is read
# and the selector stays byte-identical.
#
# The labels are the same strings the AXIS already uses, so a panel title and
# its own axis cannot disagree: they are the `DisplayLabelForAssociatePdg`
# entries of the trigger's PDG code
# (`plotting/improvedPlotting_THnSparse.C:1571-1591`) -- 521, -5122, 411, 4122.
# The two meson labels are equal to the routing key by coincidence of it
# already being notation; they are written out anyway so every group carries
# both fields and a later reader does not have to know which is which.
TRIGGER_GROUPS = {
    "BEAUTY": (
        {"role": "meson", "trigger": "B^{+}", "label": "B^{+}",
         "prefix": "Bplus", "column": "meson_trigger"},
        {"role": "baryon", "trigger": "Lambda_b-bar",
         "label": "#bar{#Lambda}_{b}^{0}",
         "prefix": "Lbbar", "column": "baryon_trigger"},
    ),
    "CHARM": (
        {"role": "meson", "trigger": "D^{+}", "label": "D^{+}",
         "prefix": "Dplus", "column": "meson_trigger"},
        {"role": "baryon", "trigger": "Lambda_c(+)",
         "label": "#Lambda_{c}^{+}",
         "prefix": "Lambdacplus", "column": "baryon_trigger"},
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

# THE CLOSURE CONFIGURATION STAYS ON THE BASE PAIR SET (architect ledger #11).
#
# R40 widened the FIGURE configurations to two trigger groups and the legacy
# associate set. It does not widen the CLOSURE configuration, and that is a
# design decision rather than an omission: the closure and CONTROL instruments
# verify the class axis against the accepted J-c1.1 log -- 132 rows over twelve
# identities -- and the boundary receipts they certify are shared by every
# figure render, so the wider figure scope loses nothing. A widened closure
# derives 48 identities and a 576-row render instead, a shape no accepted log
# carries, and the 144/132 contract that licenses the published arithmetic
# stops being checkable at all.
#
# `None` is the value that leaves the base document's registrations and
# canvases untouched, and the base document IS the four series: B+ -> B-,
# B+ -> Lambda_b, D+ -> D-, D+ -> Lambda_c(+)-bar. V-CORRELATIONS passes the
# same value for a different reason (see build_correlations), so the two
# decisions are named separately rather than sharing one bare literal.
CLOSURE_ASSOCIATE_SET = None

# What the generated closure configuration says about its own pair set, for a
# reader who opens it beside a figure configuration and finds four series where
# the figure has sixteen.
CLOSURE_PAIR_SET_COMMENT = (
    "THE BASE PAIR SET, NOT THE FIGURES' R40 SET: four series -- B+ -> B-, "
    "B+ -> Lambda_b, D+ -> D-, D+ -> Lambda_c(+)-bar -- so three tunes give "
    "twelve identities, and with the integrated bin that is 144 nominal rows "
    "against a 132-row CONTROL. The closure and CONTROL instruments verify the "
    "class axis against the accepted J-c1.1 log, which carries those same 132 "
    "rows over those same twelve identities, and the boundary receipts they "
    "certify are shared by every figure render -- so the wider figure scope "
    "loses nothing here, while a widened closure would assert a shape no "
    "accepted log has.")

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
    (improvedPlotting_THnSparse.C:632-679), so the invariant is asserted HERE,
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


def without_associates(associates, excluded, where: str):
    """`associates` minus the routing names in `excluded`, refusing a miss.

    An exclusion that matches nothing is a typo, not a no-op: it would leave
    the associate it meant to drop in the configuration and say nothing. So a
    name that is not in the set stops the generator.
    """
    names = {row[0] for row in associates}
    unknown = sorted(set(excluded) - names)
    if unknown:
        raise SystemExit(
            f"{where}: cannot exclude {', '.join(unknown)}; the associate set "
            f"carries {', '.join(sorted(names))}")
    return tuple(row for row in associates if row[0] not in excluded)


def apply_trigger_groups(document: dict, associate_set: str,
                         exclude: dict[str, tuple[str, ...]] | None = None) -> None:
    """Register both trigger groups per flavour, with the selected associates.

    `exclude` drops routing names from ONE configuration without touching
    `ASSOCIATE_SETS`, which every builder shares. It applies to both roles of
    the named flavour, so the two trigger columns keep the same associates and
    the composite's two halves stay comparable.
    """
    if associate_set not in ASSOCIATE_SETS:
        raise SystemExit(
            f"unknown associate set {associate_set!r}; "
            f"known: {', '.join(sorted(ASSOCIATE_SETS))}")
    registry = registry_rows()
    chosen = ASSOCIATE_SETS[associate_set]
    exclude = exclude or {}
    for flavour, groups in TRIGGER_GROUPS.items():
        dropped = exclude.get(flavour, ())
        document[FLAVOUR_SECTION[flavour]] = [
            {
                "trigger": group["trigger"],
                "configs": trigger_group_configs(
                    flavour, group,
                    without_associates(
                        chosen[flavour][group["role"]], dropped,
                        f"{flavour} {group['trigger']!r}")
                    if dropped else chosen[flavour][group["role"]],
                    registry),
            }
            for group in groups
        ]


def percentile_label(index: int, percentiles: list[float]) -> str:
    """Delegates to the shared primitive; see tools/class_label_format.py."""
    return class_percentile_range(index, percentiles)


def legend_wording(index: int, total: int, percentiles: list[float]) -> str:
    """The one spelling of a drawn class, used wherever a class is named.

    Both the panel entries `build_extremes` rewrites and the canvas legend
    L1 introduced take this function, so the figure cannot carry two wordings
    of the same class.
    """
    words = rank_words(index, total)
    pct = percentile_label(index, percentiles)
    return f"{words}, {pct}" if words else pct


def rank_words(index: int, total: int) -> str | None:
    """Plain-language rank, derived from position in ascending N_ch.

    THE WORDS ARE SHORT BECAUSE THEY NOW GO IN A PANEL (ruling R45, checklist
    item 1). Until FIG-1 these labels were written into `legend_entries` and
    never drawn: every V-EXTREMES panel carried `legend=(-1,-1,-1,-1)`, which
    is the macro's switch for "no legend on this canvas", so the two classes
    reached the reader with no name at all.

    A legend that names them has to fit inside a mini pad of a four-row
    composite. Measured against the delivered geometry, the band below the
    lowest drawn point is 0.147 of the pad, and two rows of legend at the
    label metric need more than that; two SHORT entries side by side in one
    row need 0.08 and fit with room to spare. "lowest #it{N}_{ch} class,
    90-100%" is 30 characters and does not fit a half-width column; "lowest,
    90-100%" is 15 and does.

    NOTHING IS LOST FROM THE FIGURE. The canvas header states the long form
    in full -- "2 of 11 #it{N}_{ch} classes shown: lowest (90-100%), highest
    (0-1%)" -- and item 11 keeps that line. The legend's job is to bind a
    marker to a class, and the short form does that.

    The shape stays what `tests/test_variant_configs.py` pins: the word
    "lowest" or "highest" is present, and the percentile is the last
    comma-separated field, which is what its inversion check parses.
    """
    if index == 1:
        return "lowest"
    if index == total:
        return "highest"
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
# (improvedPlotting_THnSparse.C:3257-3267) and the draw loop iterates it,
# colouring each numerator through `ApplyTuneVisualStyle` and writing one legend
# entry per numerator (`:4754-4806`). Both ratios therefore land in one pad with
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

# A RATIO LABEL NEVER ENUMERATES ITS NUMERATORS (ruling L2, owner,
# 2026-09-01). A combined-ratio panel draws two numerator tunes against
# MONASH, and the label used to join their names: `JUNCTIONS and CLOSEPACKING
# / MONASH`, 36 characters that grow with every tune added. The generic form
# names the ROLE, and the canvas legend names which tunes fill it -- one entry
# per series, each naming its own tune, which is not the enumerated form and
# is what a reader needs to tell two curves apart.
#
# THE Y AXIS IS UNCHANGED. It already reads `ratio to MONASH` (FIG-1B,
# `RATIO_PANEL_Y_TITLE`), so the denominator is stated by the axis and the
# panel label states only the numerator role.
#
# THIS CONSTANT IS SWEPT, NOT SPOT-FIXED. The two label sites that joined the
# names are the trigger-column composites' combined-ratio panel and G8's; both
# take this constant now. The `_`-joined CANVAS NAMES keep the enumeration
# because they are routing keys, not labels: renaming one renames a delivered
# mini. Titles-off already silences both labels, and they are corrected anyway
# so that switching titles back on cannot bring the enumerated form back.
RATIO_PANEL_GENERIC_NUMERATOR = "tune"

# THE RATIO PANELS' Y TITLE, AND THE ONE PLACE IT IS WRITTEN (owner ruling
# 2026-08-31). Every balancing ratio panel in every configuration takes this
# string. The wording the panels carried before was 29 to 37 characters --
# `tune / MONASH balancing yield` where a builder authored it, and
# `CLOSEPACKING / MONASH balancing yield` where the panel was inherited from
# the base -- and no ratio pad can render that at the publication text metric.
# Measured on the replayed certified canvases: the 37-character wording is
# complete only to about 18 px, the metric is 33 px, and at 33 px the panel
# lost 237 px of its own title
# (`FIG1B_EVIDENCE_34708a5_20260831/replay/MEASUREMENTS.md`, sections 1, 3, 4).
# The shorter string loses nothing. Each panel's own title already names its
# numerators (`JUNCTIONS and CLOSEPACKING / MONASH, ...`), so the y axis has
# only the denominator left to name.
RATIO_PANEL_Y_TITLE = "ratio to MONASH"

# The ratio family, named by the macro's OWN dispatch key and never by title
# text, so the pass below cannot drift onto matching wording. These two values
# are every ratio panel in all five configurations; the macro dispatches on
# them at improvedPlotting_THnSparse.C:6546 and :5739.
RATIO_PANEL_DRAW_FUNCTIONS = (
    "drawBalancingPlotsTUNERatios",
    "drawBalancingBaryonMesonRatioPlotsTUNERatios",
)

# PANEL TITLES ARE SWITCHABLE, AND THEY ARE NOW OFF (ruling R46, owner,
# 2026-09-01). Every figure embeds in the paper under a caption, so a title
# drawn inside the panel repeats the caption beside it. `false` blanks every
# panel title the balancing macro draws -- its four template sites and its
# correlation canvas -- and the identification is stated once instead.
#
# WHAT A TITLE STATED SIX TIMES NOW STATES ONCE. An eight-panel composite
# carried `TUNE, TRIGGER trigger, pp #sqrt{s} = 13.6 TeV` in every panel, so
# it printed the beam energy six times, the trigger eight and the tune six.
# Under R46 each fact has exactly one home: the beam energy and the generator
# go to the information block (`INFORMATION_BLOCK_LINE`), the trigger or the
# flavour to a column header (`column_headers`), the tune to an in-frame row
# label (`panel_label`) and to the one canvas legend (`canvas_legend`), and
# the rest to the caption. The Phase-A map of
# `FIG1D_EVIDENCE_0e98a5b_20260901/phaseA/INFORMATION_LOSS_MAP.md` lists every
# fact and its destination; no fact was dropped.
#
# THE SWITCH STAYS. FIG-1C built it so the decision is one constant, and R46
# flips that constant rather than deleting the five title sites.
#
# THE MACRO DEFAULTS THE KEY TO `true` WHEN IT IS ABSENT, so the frozen base
# and the four hand-maintained configurations -- none of which this generator
# writes -- parse and render exactly as they do today.
DRAW_CANVAS_TITLES = False

COLUMN_X = {
    "meson_trigger": (0.05, 0.5),
    "baryon_trigger": (0.501, 0.95),
}
COMPOSITE_TOP, COMPOSITE_ROWS = 0.95, 4

# Y WINDOWS ARE PER TRIGGER COLUMN, because baryon-trigger yields differ in
# magnitude from meson-trigger yields. The baryon column starts from the legacy
# `*_lambda_trigger` minis' own windows
# (plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json).
#
# THESE ARE HARD REFUSALS, NOT DECORATION. `SetPlotPointOrThrow` refuses a point
# outside `[y_min_axis, y_max_axis]`, so a window that does not hold the data
# stops the render and names the point instead of cropping a paper figure. A
# clipped-envelope throw at the deployment is therefore owned by RUN-N under the
# F63 protocol: widen the range HERE, regenerate, re-render -- one iteration, and
# the data is never cropped to the window.
#
# THE MESON COLUMN NO LONGER INHERITS. Until RUN-N it carried the base's own
# `(0.01, 0.42)` yield and `(0.6, 2.5)` ratio windows by omission, and RUN-N
# refused two renders on exactly those two inherited numbers (report §5.1 and
# §5.2). Both columns now name their windows here, so no window reaches a
# render without a measured envelope beside it.
#
# EVERY WINDOW BELOW CARRIES THREE THINGS, in the style
# `BARYONMESON_TUNE_RATIO_WINDOW` established: the measured envelope, the
# source that measured it, and a guard that the window contains it. A bare
# number tells a later reader nothing about what it must hold.

# --- the meson trigger column ------------------------------------------------
#
# THE YIELD FLOOR, and the measurement that sets it (RUN-N refusal §5.2).
# The V-INTEGRATED render refused the inherited floor 0.01 and named the point:
#
#   ERROR: Plotted uncertainty envelope [0.00023709204475633864,
#   0.00026345126205427503] is clipped by configured y-axis [0.01, 0.42]:
#   BEAUTY yield, tune=MONASH, associate=Bc-, bin=hDPhiM00_100
#
# Ruling R40 widened the figure configurations to the legacy associate set,
# which adds B_c-. B_c- is orders of magnitude rarer than the other beauty
# associates, and the inherited window was tuned before it. The envelope below
# is the minimum and maximum over ALL 48 logged rows of that render, not just
# the refused one, so the floor is set once rather than by bounces.
MESON_COLUMN_YIELD_ENVELOPE = (0.0001576469004, 0.1935681066)
MESON_COLUMN_YIELD_ENVELOPE_SOURCE = (
    "RUNN_EVIDENCE_fe3262c_20260830/verify/f63_measured_extremes.txt, "
    "VINTEGRATED block, BEAUTY/B^{+} and CHARM/D^{+} rows unioned; minimum "
    "at JUNCTIONS BEAUTY B^{+} associate=Bc- bin=hDPhiM00_100")
MESON_COLUMN_YIELD_WINDOW = (5e-05, 0.42)

# THE RATIO CEILING, and the measurement that sets it (RUN-N refusal §5.1).
# The V-INTEGRATED_CLOSURE render refused the inherited ceiling 2.5:
#
#   ERROR: Plotted uncertainty envelope [2.3705630324775111,
#   2.5314256389680088] is clipped by configured y-axis [0.6, 2.5]: BEAUTY
#   tune ratio JUNCTIONS/MONASH, associate=Lambda_b, bin=hDPhiM0_1
#
# `hDPhiM0_1` is c11, the HIGHEST-activity class, not c1. The contract stores
# c1 through c11 in ascending activity and the percentiles are TOP percentiles,
# so 0.0-1.0 % is the top class; this file's header states the trap.
#
# 3.0 was checked before it was locked (brief CON-1C item 1.2). Over the 96
# tune-ratio comparisons of the closure render, the largest value of the
# conservative cross-tune bound (Y_tune + SEM)/(Y_MONASH - SEM) is
# 2.5671199529898105, at the same identity as the refusal. No bound exceeds
# 3.0, so 3.0 holds the base series with a factor 1.17 in hand.
#
# THE FLOOR IS 0.0, AND THAT IS THE POLICY FOR EVERY RATIO PANEL (ruling R45,
# checklist item 3). One composite draws two trigger columns side by side. A
# reader compares them, so the two columns must share one y-range or the
# comparison is a reading error waiting to happen: until FIG-1 this column
# drew [0.6, 3.0] beside the baryon column's [0.0, 3.0], and G4 and G6 were
# delivered with mismatched ratio panels.
#
# THE POLICY, stated once for all four ratio windows this file holds: every
# combined-ratio panel of every composite draws [0.0, 3.0]. 0.0 is the
# physical floor of a yield ratio, so the floor costs no resolution that a
# measurement could occupy; 3.0 is the ceiling all three ratio windows already
# shared. `BARYON_COLUMN_RATIO_WINDOW` and
# `EXTREMES_MESON_COLUMN_RATIO_WINDOW` were already (0.0, 3.0), so this
# constant is the only one that moves and the policy holds across G4/G6 and
# G5/G7 with no other edit.
#
# THIS WIDENS THE WINDOW; IT CANNOT CROP DATA. The window is a hard refusal
# through `SetPlotPointOrThrow`, and lowering a floor can only admit points
# that the old floor would have refused. The guard below still checks this
# window against its own measured envelope, whose lower edge 0.6215702019 is
# unchanged and still inside.
MESON_COLUMN_RATIO_ENVELOPE = (0.6215702019, 2.5314256389680088)
MESON_COLUMN_RATIO_ENVELOPE_SOURCE = (
    "CON1C_EVIDENCE_fe3262c_20260831/derive/window_bounds.out; upper edge is "
    "the RUN-N §5.1 throw, JUNCTIONS/MONASH associate=Lambda_b bin=hDPhiM0_1, "
    "render.log; lower edge is JUNCTIONS BEAUTY B^{+} associate=Bc- "
    "bin=hDPhiM00_100, render_VINTEGRATED.log")
MESON_COLUMN_RATIO_WINDOW = (0.0, 3.0)

# --- the baryon trigger column -----------------------------------------------
#
# The floor 0.0001 already held the baryon column's measured minimum when RUN-N
# ran: 0.0001248414791, at CLOSEPACKING BEAUTY Lambda_b-bar associate=Bc-
# bin=hDPhiM00_100. RUN-N refused nothing in this column, so the window stands.
BARYON_COLUMN_YIELD_ENVELOPE = (0.0001248414791, 0.1931479021)
BARYON_COLUMN_YIELD_ENVELOPE_SOURCE = (
    "RUNN_EVIDENCE_fe3262c_20260830/verify/f63_measured_extremes.txt, "
    "VINTEGRATED block, BEAUTY/Lambda_b-bar and CHARM/Lambda_c(+) rows unioned")
BARYON_COLUMN_YIELD_WINDOW = (0.0001, 0.8)

# THE RATIO CEILING RISES WITH THE MESON COLUMN'S, from 2.5 to 3.0. The two
# columns render the same eleven classes over the same three tunes, and the
# meson column measured 2.5314256389680088 in c11. A baryon ceiling below the
# meson column's measured maximum is a window that happens not to have been
# hit yet. The window's job is refusing broken data, and 3.0 still does that:
# this column's own measured maximum is 2.062089884, so 3.0 holds it by 1.45.
BARYON_COLUMN_RATIO_ENVELOPE = (0.4025148267, 2.062089884)
BARYON_COLUMN_RATIO_ENVELOPE_SOURCE = (
    "CON1C_EVIDENCE_fe3262c_20260831/derive/window_bounds.out, "
    "render_VINTEGRATED.log baryon column; maximum at JUNCTIONS BEAUTY "
    "Lambda_b-bar associate=Lambda_b bin=hDPhiM00_100, minimum at "
    "CLOSEPACKING BEAUTY Lambda_b-bar associate=Bc- bin=hDPhiM00_100")
BARYON_COLUMN_RATIO_WINDOW = (0.0, 3.0)

# --- V-EXTREMES takes its own windows -----------------------------------------
#
# WHY THIS CONFIGURATION IS SEPARATE. V-EXTREMES draws the two extreme classes
# of the legacy associate set. V-INTEGRATED draws one integrated bin of the
# same set. Integrating over the whole multiplicity axis averages away the
# class-to-class spread, so the extreme classes reach yields and ratios the
# integrated bin never shows, and one shared window cannot hold both without
# being loose where the integrated figure needs it tight.
#
# THE FLOORS ARE MEASURED. This is the record of the replacement; they were
# provisional through exactly one render.
#
# CON-1C set both to 1e-06 because the only log it had was truncated.
# `render_VEXTREMES.log` at RUN-N held 46 `UNCERTAINTY_MATRIX` rows and
# stopped: the render aborted inside the beauty baryon column on the
# structurally empty Lambda_b-bar -> B_c- cell of RUN-N report §5.3. Of the
# rows the R43 exclusion leaves, 38 of 84 were measured and 46 were not, and
# CHARM was absent from both columns. Both minima that log showed belong to
# B_c- rows R43 removes:
#
#   meson  column  1.567022511e-05  MONASH BEAUTY B^{+}        Bc- hDPhiM90_100
#   baryon column  7.092474723e-06  MONASH BEAUTY Lambda_b-bar Bc- hDPhiM90_100
#
# A floor from the surviving beauty rows alone, with charm unrendered, would
# have been a guess wearing a measurement's clothes. 1e-06 sat far below
# anything the render could produce, so it refused broken data and nothing
# else.
#
# RUN-N2 RENDERED ONCE ON THOSE FLOORS and delivered G5 and G7 as candidates,
# `status=candidate_pending_axis_approval`. That render completed. It measures
# all 84 surviving rows -- 24+24 beauty, 18+18 charm -- with zero
# `SUBSAMPLE_COVERAGE_FAILURE` lines and no row at central zero
# (`RUNN2_EVIDENCE_e6bd02b_20260831/extremes/vextremes_measured_range.txt`).
# The charm rows are the new information. They raise both measured maxima from
# about 0.127 to about 0.217, and they sit above the beauty minima, so each
# column's floor is still its beauty edge.
#
# THE OWNER RULED ON 2026-08-31 to tighten now; the ruling of record is in
# `ARCHITECT_REVIEW_RUNN2_20260831.md`. The surviving data spans about one
# decade, and the provisional meson axis spanned 5.62, so two-thirds of a
# published log axis would have been empty. Each floor becomes its measured
# envelope edge over 3 -- the margin CON-1C set for
# `MESON_COLUMN_YIELD_WINDOW` (this file, `:691`), whose floor 5e-05 sits
# 3.15x below `MESON_COLUMN_YIELD_ENVELOPE` (this file, `:686`). The
# quotient stays at full precision, so each floor below is exactly the
# `_ENVELOPE[0] / 3` of the constant above it, recomputed in one division. The
# meson panel goes from 5.62 decades to 1.93 and the baryon panel from 5.90 to
# 2.27. Neither ceiling moves. RUN-N3 re-renders V-EXTREMES on these floors,
# and its records supersede the candidates.
#
# THE ENVELOPES RECORDED HERE ARE THE SURVIVING ONES, not the logged ones. The
# B_c- rows leave V-EXTREMES with R43, so a guard against a B_c- envelope would
# guard a row this configuration no longer draws.
EXTREMES_MESON_COLUMN_YIELD_ENVELOPE = (0.014682368941172011, 0.21695803533110744)
EXTREMES_MESON_COLUMN_YIELD_ENVELOPE_SOURCE = (
    "RUNN2_EVIDENCE_e6bd02b_20260831/extremes/vextremes_measured_range.txt, "
    "render_VEXTREMES.log meson column with associate=Bc- excluded per R43; "
    "complete log, 84 of 84 surviving rows read, zero coverage failures; this "
    "column is 24 of 24 surviving BEAUTY rows and 18 of 18 CHARM rows; lower "
    "edge JUNCTIONS BEAUTY B^{+} associate=B_s^0-bar bin=hDPhiM0_1, upper "
    "edge MONASH CHARM D^{+} associate=D^{0}-bar bin=hDPhiM0_1")
EXTREMES_MESON_COLUMN_YIELD_WINDOW = (0.0048941229803906704, 0.42)

EXTREMES_BARYON_COLUMN_YIELD_ENVELOPE = (0.012778871747754926, 0.21691162789358753)
EXTREMES_BARYON_COLUMN_YIELD_ENVELOPE_SOURCE = (
    "RUNN2_EVIDENCE_e6bd02b_20260831/extremes/vextremes_measured_range.txt, "
    "render_VEXTREMES.log baryon column with associate=Bc- excluded per R43; "
    "complete log, 84 of 84 surviving rows read, zero coverage failures; 24 "
    "of 24 surviving BEAUTY rows and 18 of 18 CHARM rows measured; lower edge "
    "JUNCTIONS BEAUTY Lambda_b-bar associate=B_s^0-bar bin=hDPhiM0_1, upper "
    "edge MONASH CHARM Lambda_c(+) associate=D- bin=hDPhiM0_1")
EXTREMES_BARYON_COLUMN_YIELD_WINDOW = (0.004259623915918309, 0.8)

# THE MESON RATIO FLOOR CANNOT BE 0.6 HERE, and this one is not provisional.
# The BEAUTY meson column of `render_VEXTREMES.log` is COMPLETE at 30 of 30
# rows, so its measurements are final. Four surviving rows carry a ratio
# envelope whose lower edge falls below 0.6, and one of them is in this column:
#
#   JUNCTIONS BEAUTY B^{+} associate=B_s^0-bar bin=hDPhiM0_1
#   JUNCTIONS central_yield=0.015639725922718357 yield_sem=0.00095735698154634607
#   MONASH    central_yield=0.027041881939100801 yield_sem=0.00091119728725690575
#   ratio=0.57835197853239395 error=0.040412097763219836
#   envelope=[0.53793988076917409, 0.61876407629561381]
#
# `MESON_COLUMN_RATIO_WINDOW`'s floor of 0.6 would refuse that point. The floor
# is 0.0 here, which is the physical floor of a yield ratio and the value
# `BARYON_COLUMN_RATIO_WINDOW` already uses for the same reason. The ceiling
# stays 3.0, shared with both other ratio windows; this column's measured
# surviving maximum is 2.531425639, so 3.0 holds it by 1.19.
#
# The extremes BARYON ratio panel needs no entry of its own:
# `BARYON_COLUMN_RATIO_WINDOW` is already (0.0, 3.0), and this configuration's
# measured surviving baryon envelope is [0.4628089817, 0.9088271401], inside it.
EXTREMES_MESON_COLUMN_RATIO_ENVELOPE = (0.53793988076917409, 2.5314256389680088)
EXTREMES_MESON_COLUMN_RATIO_ENVELOPE_SOURCE = (
    "CON1C_EVIDENCE_fe3262c_20260831/derive/window_bounds.out, "
    "render_VEXTREMES.log meson column with associate=Bc- excluded per R43; "
    "lower edge JUNCTIONS associate=B_s^0-bar bin=hDPhiM0_1, upper edge "
    "JUNCTIONS associate=Lambda_b bin=hDPhiM0_1; BEAUTY complete at 30/30 rows")
EXTREMES_MESON_COLUMN_RATIO_WINDOW = (0.0, 3.0)


# ONE YIELD WINDOW PER FIGURE (architect finding F5, 2026-09-01).
#
# THE DEFECT. G4 and G6 put their two trigger columns side by side on
# DIFFERENT y windows for the same quantity: the meson column ran
# 5e-05 to 0.42 and the baryon column 1e-04 to 0.8. A reader comparing the
# left panel with the right one was comparing two scales, and nothing on the
# figure said so. The windows were per COLUMN because baryon-trigger yields
# were expected to differ in magnitude from meson-trigger ones; the measured
# envelopes say they do not.
#
# THE MEASUREMENT, from the delivered macros of RUN-N4's mirror
# (`DELIVERABLES_REVIEW_20260901/G4_G6/*_MACRO.C`), over every drawn point of
# both columns including its error bar:
#
#   BEAUTY  meson  [0.00015764688, 0.1168291368]
#           baryon [0.00012484148, 0.1172078342]   both columns: 1.25e-04 .. 0.1172
#   CHARM   meson  [0.0188761542,  0.1935681496]
#           baryon [0.0197802746,  0.1931478546]   both columns: 1.888e-02 .. 0.1936
#
# The two columns of one flavour agree to better than 1 % at the top and
# within a factor 1.3 at the bottom. The two FLAVOURS do not: beauty reaches
# two decades lower, because B_c- is in the integrated associate set (R43) and
# charm has no comparable rare associate. So the window is harmonized PER
# FIGURE, which is what F5 asks and what the flavours support; one window
# across both flavours would put charm's whole decade in the top quarter of a
# four-decade axis, which is the defect F8 names on G8.
#
# THE FLOORS AND CEILINGS ARE ROUND NUMBERS THAT CONTAIN THE ENVELOPE, not the
# envelope itself: a window equal to its data crops the error bar of the
# extreme point at the frame. Beauty takes 5e-05, 2.5x below its measured
# floor; charm takes 1e-02, 1.9x below its own. Both take 0.4, about 2x above
# the higher of the two measured ceilings. `COLUMN_WINDOW_GUARDS` checks each
# against its envelope at import.
#
# WHAT DECADE-ONLY LABELLING THEN GIVES (ruling L3). Beauty spans 3.9 decades
# and labels four. CHARM SPANS 1.6 DECADES AND LABELS TWO, below the three the
# brief asks for, because charm's data spans one decade and no honest window
# around it spans three. The alternative is recorded rather than taken: a
# charm floor of 1e-03 labels three decades and leaves the lower half of the
# panel empty. The report states this and proposes it; it is the owner's call,
# not a number this generator should guess.
INTEGRATED_BEAUTY_YIELD_ENVELOPE = (0.00012484148, 0.1172078342)
INTEGRATED_CHARM_YIELD_ENVELOPE = (0.0188761542, 0.1935681496)
INTEGRATED_YIELD_ENVELOPE_SOURCE = (
    "RUN-N4 delivered macros, DELIVERABLES_REVIEW_20260901/G4_G6, measured "
    "over both trigger columns by FIG-1D's replay probe")
INTEGRATED_BEAUTY_YIELD_WINDOW = (5e-05, 0.4)
INTEGRATED_CHARM_YIELD_WINDOW = (1e-02, 0.4)

# EVERY WINDOW IS GUARDED AGAINST ITS OWN MEASUREMENT, here, at import. A
# window edited below its envelope raises before any document is built, so the
# generator cannot write a configuration whose window crops its own recorded
# data. The three-tuple per row is (window, measured envelope, source).
COLUMN_WINDOW_GUARDS = (
    ("MESON_COLUMN_YIELD_WINDOW",
     MESON_COLUMN_YIELD_WINDOW, MESON_COLUMN_YIELD_ENVELOPE,
     MESON_COLUMN_YIELD_ENVELOPE_SOURCE),
    ("MESON_COLUMN_RATIO_WINDOW",
     MESON_COLUMN_RATIO_WINDOW, MESON_COLUMN_RATIO_ENVELOPE,
     MESON_COLUMN_RATIO_ENVELOPE_SOURCE),
    ("BARYON_COLUMN_YIELD_WINDOW",
     BARYON_COLUMN_YIELD_WINDOW, BARYON_COLUMN_YIELD_ENVELOPE,
     BARYON_COLUMN_YIELD_ENVELOPE_SOURCE),
    ("BARYON_COLUMN_RATIO_WINDOW",
     BARYON_COLUMN_RATIO_WINDOW, BARYON_COLUMN_RATIO_ENVELOPE,
     BARYON_COLUMN_RATIO_ENVELOPE_SOURCE),
    ("EXTREMES_MESON_COLUMN_YIELD_WINDOW",
     EXTREMES_MESON_COLUMN_YIELD_WINDOW,
     EXTREMES_MESON_COLUMN_YIELD_ENVELOPE,
     EXTREMES_MESON_COLUMN_YIELD_ENVELOPE_SOURCE),
    ("EXTREMES_BARYON_COLUMN_YIELD_WINDOW",
     EXTREMES_BARYON_COLUMN_YIELD_WINDOW,
     EXTREMES_BARYON_COLUMN_YIELD_ENVELOPE,
     EXTREMES_BARYON_COLUMN_YIELD_ENVELOPE_SOURCE),
    ("EXTREMES_MESON_COLUMN_RATIO_WINDOW",
     EXTREMES_MESON_COLUMN_RATIO_WINDOW,
     EXTREMES_MESON_COLUMN_RATIO_ENVELOPE,
     EXTREMES_MESON_COLUMN_RATIO_ENVELOPE_SOURCE),
    ("INTEGRATED_BEAUTY_YIELD_WINDOW",
     INTEGRATED_BEAUTY_YIELD_WINDOW, INTEGRATED_BEAUTY_YIELD_ENVELOPE,
     INTEGRATED_YIELD_ENVELOPE_SOURCE),
    ("INTEGRATED_CHARM_YIELD_WINDOW",
     INTEGRATED_CHARM_YIELD_WINDOW, INTEGRATED_CHARM_YIELD_ENVELOPE,
     INTEGRATED_YIELD_ENVELOPE_SOURCE),
)

for _name, _window, _envelope, _source in COLUMN_WINDOW_GUARDS:
    if not (_window[0] <= _envelope[0] and _envelope[1] <= _window[1]):
        raise SystemExit(
            "%s %s does not contain the measured envelope %s (%s)"
            % (_name, _window, _envelope, _source))


# WHICH WINDOW SET A CONFIGURATION USES. `build_trigger_column_canvases` reads
# one of these two, so the choice is named at the call site rather than decided
# inside the loop that writes the canvases.
INTEGRATED_COLUMN_WINDOWS = {
    ("meson_trigger", "yield"): MESON_COLUMN_YIELD_WINDOW,
    ("meson_trigger", "ratio"): MESON_COLUMN_RATIO_WINDOW,
    ("baryon_trigger", "yield"): BARYON_COLUMN_YIELD_WINDOW,
    ("baryon_trigger", "ratio"): BARYON_COLUMN_RATIO_WINDOW,
    # The per-flavour entries take precedence for `yield`; see `window_for`.
    ("BEAUTY", "yield"): INTEGRATED_BEAUTY_YIELD_WINDOW,
    ("CHARM", "yield"): INTEGRATED_CHARM_YIELD_WINDOW,
}


def window_for(windows: dict, flavour: str, column: str,
               kind: str) -> tuple[float, float]:
    """The window for one panel: per FIGURE where one is given, else per column.

    A configuration that harmonizes a quantity across its columns registers
    `(FLAVOUR, kind)`; one that still separates them registers
    `(column, kind)`. V-EXTREMES keeps per-column yield windows because its
    two columns carry different associate sets under R43.
    """
    return windows.get((flavour, kind)) or windows[(column, kind)]
# V-EXTREMES KEEPS PER-COLUMN YIELD WINDOWS, and the spread below drops the
# per-FIGURE entries F5 added rather than inheriting them. The two columns of
# an extremes canvas do not carry the same associates -- R43 removes B_c- from
# both beauty columns and charm never had it -- and their floors are each that
# column's own measured envelope minimum over three. Inheriting a per-flavour
# yield window here would silently replace two measured floors with one.
EXTREMES_COLUMN_WINDOWS = {
    **{key: value for key, value in INTEGRATED_COLUMN_WINDOWS.items()
       if key[0] not in FLAVOUR_SECTION},
    ("meson_trigger", "yield"): EXTREMES_MESON_COLUMN_YIELD_WINDOW,
    ("meson_trigger", "ratio"): EXTREMES_MESON_COLUMN_RATIO_WINDOW,
    ("baryon_trigger", "yield"): EXTREMES_BARYON_COLUMN_YIELD_WINDOW,
}


TRIGGER_COLUMN_COMMENT = (
    "TWO TRIGGER COLUMNS PER FLAVOUR under ruling R40 as amended: meson "
    "trigger left, baryon trigger right, each column carrying the three tune "
    "panels and one combined tune/MONASH ratio panel. Associates are the "
    "legacy set in both columns, less any exclusion this configuration names "
    "above. The pad rectangles are computed by the "
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


def apply_window(canvas: dict, window: tuple[float, float]) -> None:
    """Write one y window onto one canvas.

    Every panel this generator emits is given its window HERE. Before CON-1C
    the meson column inherited the base's, which is how RUN-N met two windows
    that no measurement had ever been checked against (report §5.1, §5.2).
    """
    canvas["y_min_axis"], canvas["y_max_axis"] = window


# PAD MARGINS FOR THE COMPOSITE PANELS (ruling R45, checklist items 5 and 12).
#
# The inherited margins are 0.13 left and 0.12 bottom, authored for text at
# ROOT's pad-relative default. The macro now sizes text against the FINAL
# canvas width (`kPublicationLabelFraction`), which on a 2200 px composite is
# 33 px where the default gave about 19, and a label that is 1.7x taller needs
# the band it is drawn in to grow with it. Left unchanged, the enlarged y title
# overprints the y tick labels and the enlarged x title leaves the pad.
#
# 0.20 was measured, not guessed: the delivered G5 and G7 canvases were
# replayed on the bench with this metric and these margins, and the y title
# clears the widest tick label while the centred x title sits inside the pad
# below the species labels (`FIG1_EVIDENCE_1db46d9_20260831/audit/`).
#
# The top and right margins do not move. The top carries the panel title,
# which is unchanged in position, and the right carries nothing.
COMPOSITE_PAD_MARGINS = {
    "left_margin_mini_pad": 0.20,
    "right_margin_mini_pad": 0.03,
    "bottom_margin_mini_pad": 0.20,
    "top_margin_mini_pad": 0.10,
}


def apply_composite_margins(canvas: dict) -> None:
    """Give one composite mini pad the margins its text size needs."""
    canvas.update(COMPOSITE_PAD_MARGINS)


def build_trigger_column_canvases(
        base: dict,
        windows: dict[tuple[str, str], tuple[float, float]] | None = None,
) -> list[dict]:
    """Sixteen minis: two flavours, two trigger columns, four rows each.

    `windows` maps (column, panel kind) to the y window that column's panels
    take. `composite_globals` calls this function only to read canvas NAMES,
    which no window affects, so the default keeps that call site unchanged.
    """
    if windows is None:
        windows = INTEGRATED_COLUMN_WINDOWS
    templates = _template_canvases(base)
    rows = column_rectangles()
    canvases: list[dict] = []

    for flavour, groups in TRIGGER_GROUPS.items():
        for group in groups:
            column = group["column"]
            x_min, x_max = COLUMN_X[column]

            for row, tune in enumerate(TUNE_PANEL_ORDER, start=1):
                canvas = json.loads(json.dumps(templates["drawBalancingPlots"]))
                canvas["canvas_name"] = (
                    f"mini_{flavour.lower()}_balancing_{tune.lower()}_{column}")
                canvas["FLAVOUR"] = flavour
                canvas["TriggerToUse"] = group["trigger"]
                canvas["TUNES"] = [tune]
                canvas["canvas_title"] = (
                    f"{tune}, {group['label']} trigger, "
                    f"pp #sqrt{{s}} = 13.6 TeV")
                canvas["x_min_mini_pad"], canvas["x_max_mini_pad"] = x_min, x_max
                canvas["y_min_mini_pad"], canvas["y_max_mini_pad"] = rows[row]
                apply_window(canvas,
                             window_for(windows, flavour, column, "yield"))
                apply_composite_margins(canvas)
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
                f"{RATIO_PANEL_GENERIC_NUMERATOR} / "
                f"{COMBINED_RATIO_DENOMINATOR}, {group['label']} trigger")
            ratio["x_min_mini_pad"], ratio["x_max_mini_pad"] = x_min, x_max
            ratio["y_min_mini_pad"], ratio["y_max_mini_pad"] = rows[0]
            apply_window(ratio,
                         window_for(windows, flavour, column, "ratio"))
            apply_composite_margins(ratio)
            canvases.append(ratio)

    return canvases


# THE COLUMN HEADER AND THE CANVAS LEGEND, THE TWO CANVAS-LEVEL LABELS
# (ruling R46 items 3 and 5, refined by L1).
#
# A HEADER IS A RECTANGLE, NOT AN X POSITION. The macro centres the text in
# the band this gives it, so the header follows the column when a rectangle
# moves and no second copy of the layout has to be kept in step.
#
# THE CANVAS LEGEND CARRIES CONVENTIONS, NOT SERIES (L1). A convention every
# panel of the canvas shares is named ONCE, on the global canvas, top-right,
# opposite the information block -- outside every pad, so it cannot overlap
# data and no clearance has to be measured against the points. The entries
# name TUNES rather than colours: the palette lives in
# `plotting/TunePlotStyle.h` (owner decision O3) and the macro resolves each
# tune's colour and marker from that header, so a colour change stays a header
# edit and this configuration never carries a second copy of it.

def column_header(text: str, column: str) -> dict:
    """One header above one column, spanning that column's FRAME.

    THE RECTANGLE IS THE FRAME, NOT THE PAD. A composite pad carries a 0.20
    left margin for its y title and 0.03 on the right, so its rectangle's
    centre sits 0.038 of the canvas -- 83 px at the delivered width -- to the
    left of the plot the header names. The macro centres the text in whatever
    band it is given, so the band is the data area and the header lands over
    the panel rather than over the panel's y axis.
    """
    x_min, x_max = COLUMN_X[column]
    span = x_max - x_min
    return {
        "text": text,
        "x_min": round(x_min + COMPOSITE_PAD_MARGINS["left_margin_mini_pad"] * span, 4),
        "x_max": round(x_max - COMPOSITE_PAD_MARGINS["right_margin_mini_pad"] * span, 4),
    }


def flavour_column_headers() -> list[dict]:
    """Headers for the canvases whose columns are the two FLAVOURS.

    G8 and the closure and correlation composites put beauty in the left
    column and charm in the right, in the order `FLAVOUR_SECTION` iterates.
    Those canvases state the flavour nowhere else once titles are off.
    """
    columns = ("meson_trigger", "baryon_trigger")
    return [column_header(flavour.lower(), column)
            for flavour, column in zip(FLAVOUR_SECTION, columns)]


def canvas_legend_entries(class_fills: list[tuple[str, str]] | None = None
                          ) -> list[dict]:
    """The conventions the panels of one canvas share.

    Always the three tunes, which every composite draws. The extremes
    canvases add the marker FILL that separates the two N_ch classes -- the
    one convention a reader cannot infer, and the reason R46 item 5 asked for
    a legend at all. The class wording is PASSED IN rather than written here,
    because `build_extremes` derives it from the boundary contract and the
    figure must not carry a second spelling of a class label.
    """
    entries = [{"kind": "tune", "tune": tune} for tune in TUNE_PANEL_ORDER]
    for fill, label in (class_fills or []):
        entries.append({"kind": "class_fill", "fill": fill, "label": label})
    return entries


def composite_globals(base: dict, write_names: dict[str, str],
                      write_path: str, title: str,
                      class_fills: list[tuple[str, str]] | None = None
                      ) -> list[dict]:
    """One global per flavour, each naming only its own eight minis.

    Every configuration's composites share ONE `write_path`: the macro collects
    the distinct output directories of the writing globals and throws "Exactly
    one global-canvas output directory is required to store the
    multiplicity-boundary receipt" on anything but one
    (improvedPlotting_THnSparse.C:3397-3407).
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
        # THE COLUMN HEADERS ARE BUILT FROM THE COLUMNS (R46 item 3). They are
        # read out of the SAME `TRIGGER_GROUPS` entry and the SAME `COLUMN_X`
        # rectangle that placed the panels of that column, in the order the
        # loop above placed them, so a header cannot name a column the canvas
        # does not draw and cannot drift out of left-to-right order.
        canvas["column_headers"] = [
            column_header(f"{group['label']} trigger", group["column"])
            for group in TRIGGER_GROUPS[flavour]
        ]
        canvas["canvas_legend"] = canvas_legend_entries(class_fills)
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
    document["axis_declaration"] = information_block(declaration)
    # Declared, so apply_class_labels.py can tell whose file this is instead of
    # inferring ownership from a filename glob.
    document[OWNER_KEY] = OWNER_VARIANTS


# B_C- LEAVES THE EXTREME-CLASS BEAUTY COLUMNS (ruling R43, owner, 2026-08-31).
#
# RUN-N's V-EXTREMES render refused a structurally empty cell (report §5.3):
#
#   SUBSAMPLE_COVERAGE_FAILURE kind=yield flavour=BEAUTY trigger=Lambda_b-bar
#   tune=JUNCTIONS pair=LbbarBcminus.root bin=hDPhiM90_100 message=yield zero
#   in all blocks (coverage complete): central=0 n=10/10 stdDev=0 stdError=0
#   positive_required=true
#
# In 10^8 JUNCTIONS events no Lambda_b-bar trigger has a B_c- associate in the
# lowest-activity class. Coverage is complete and the yield is exactly zero, so
# the cell is empty by physics and no y-window edit reaches it. The gate that
# requires a positive yield is correct and is NOT weakened: R43 removes the
# associate instead of admitting the empty cell, and no empty-cell admission
# code is written (R35).
#
# THE SCOPE IS THIS CONFIGURATION ONLY. `ASSOCIATE_SETS` is untouched, because
# `build_integrated` shares it and R43 keeps B_c- in the integrated figures
# with a lowered yield floor. The exclusion covers BOTH beauty trigger columns
# so the two halves of each composite carry the same associates. CHARM is
# untouched.
#
# THE REFERENCE-MESON INVARIANT STILL RESOLVES. B- carries the signed
# `reference_meson_pdg` and stays in the set, so `trigger_group_configs` still
# finds exactly one reference associate per group and
# `ResolveReferenceAssociateSelection` still has one to resolve
# (improvedPlotting_THnSparse.C:632-679). The exclusion is checked by that
# function on the FILTERED set, at emission.
EXTREMES_EXCLUDED_ASSOCIATES = {"BEAUTY": ("Bc-",)}
EXTREMES_EXCLUSION_COMMENT = (
    "B_c- IS OMITTED FROM BOTH BEAUTY COLUMNS under ruling R43: in 10^8 "
    "JUNCTIONS events the Lambda_b-bar trigger has no B_c- associate in the "
    "90-100 % class, so that cell holds zero counts with coverage complete and "
    "the render's positive-yield gate refuses it. The cell is empty by physics, "
    "not by configuration. The gate is not weakened and no empty-cell "
    "admission is written; the associate leaves these two columns instead. The "
    "integrated configurations keep B_c- with a lowered yield floor. Charm is "
    "unchanged. The omission is disclosed in the figure captions, which are "
    "editorial and live in docs2/paper/DELIVERABLES.md, not here.")


def build_extremes(base: dict, percentiles: list[float],
                   associate_set: str = DEFAULT_ASSOCIATE_SET) -> dict:
    """V-EXTREMES: the whole axis configured, the two extreme classes drawn."""
    total = len(percentiles)
    lowest, highest = extremes_indices(total)
    keep = {lowest, highest}

    document = json.loads(json.dumps(base))
    apply_trigger_groups(document, associate_set,
                         exclude=EXTREMES_EXCLUDED_ASSOCIATES)
    document["canvases_to_be_drawn"] = build_trigger_column_canvases(
        base, EXTREMES_COLUMN_WINDOWS)
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
                        entry["display_name"] = legend_wording(
                            index, total, percentiles)
                else:
                    rewrite_legend(value)
        elif isinstance(node, list):
            for item in node:
                rewrite_legend(item)

    rewrite_legend(document)
    apply_display_filter(document, drawn,
                         axis_declaration(classes, drawn, percentiles))

    # The fill convention, worded from the SAME contract helpers that wrote
    # the panels' own entries before L1 removed them: the lowest-activity
    # class draws the open marker, the highest the filled one
    # (`plotting/TunePlotStyle.h`, ruling R45 checklist item 1).
    class_fills = [
        ("open", legend_wording(lowest, total, percentiles)),
        ("filled", legend_wording(highest, total, percentiles)),
    ]
    document["global_canvases_to_be_drawn"] = composite_globals(
        base,
        {"BEAUTY": "global_balancing_plots_multiplicity_beauty",
         "CHARM": "global_balancing_plots_multiplicity_charm"},
        "plotting/Plots/VariantExtremes",
        "%s balancing yield in the lowest and highest #it{N}_{ch} classes, "
        "meson and baryon triggers, three tunes -- pp #sqrt{s} = 13.6 TeV",
        class_fills=class_fills)
    document["_comment_variant"] = (
        "V-EXTREMES. The FULL eleven-class axis is configured and validated; "
        "only the lowest and highest N_ch classes are DRAWN, through the same "
        "bins_to_ignore mechanism the other canvas families use. Removing a "
        "class from histograms_to_analyse would still be refused by the axis "
        "contract, and that refusal is deliberate. Rank comes from the contract "
        "order, not from comparing percentile magnitudes. "
        + EXTREMES_EXCLUSION_COMMENT + " "
        "THIS CONFIGURATION'S TWO YIELD FLOORS ARE MEASURED. The RUN-N2 "
        "render completed and measured all 84 surviving rows across both "
        "columns, charm included, with zero coverage failures. Each floor is "
        "now that column's measured envelope minimum over 3 -- meson "
        "0.0048941229803906704, baryon 0.004259623915918309 -- which replaces "
        "the 1e-06 pair that a single candidate render used, under the "
        "owner's ruling of 2026-08-31. "
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
    verification only and is not a figure, and it keeps the single incumbent
    global rather than the per-flavour composites. `variant_documents` emits it
    with `CLOSURE_ASSOCIATE_SET`, not with the figures' R40 set; that constant
    records why the closure stays on the base four series.

    `associate_set=None` leaves the base's own pair registrations and canvases
    alone. Two callers ask for that: the closure configuration, for the reason
    `CLOSURE_ASSOCIATE_SET` gives, and V-CORRELATIONS, which builds on this
    function and then adds its own two baryon-triggered groups -- registering
    them here as well would make that function refuse its own input.
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

    # THE CLOSURE'S PANELS ARE MESON-COLUMN PANELS, so they take the meson
    # column's windows. It builds with `associate_set=None`, which keeps the
    # base's own canvases, and the base pair set is meson-triggered throughout:
    # B+ -> B-, B+ -> Lambda_b, D+ -> D-, D+ -> Lambda_c(+)-bar. Those
    # inherited canvases carried the base's `(0.01, 0.42)` and `(0.6, 2.5)`,
    # and RUN-N refused this configuration on the second of them (report §5.1).
    #
    # THE CONDITION IS `closure`, NOT `associate_set is None`. V-CORRELATIONS
    # takes the same None and inherits the same canvases, and it is a delivered
    # configuration whose bytes are pinned by an acceptance record. Its own
    # measured envelopes, [0.01887615718, 0.1935681066] in yield and
    # [0.7328185643, 1.899396585] in ratio, sit inside the base windows it
    # already carries, so it needs no widening and must not be given one.
    if closure:
        for canvas in document.get("canvases_to_be_drawn", []):
            function = canvas.get("draw_function_to_use")
            if function == "drawBalancingPlots":
                apply_window(canvas, MESON_COLUMN_YIELD_WINDOW)
            elif function == "drawBalancingPlotsTUNERatios":
                apply_window(canvas, MESON_COLUMN_RATIO_WINDOW)

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
           CLOSURE_PAIR_SET_COMMENT + " " if closure
           else TRIGGER_COLUMN_COMMENT + " "))
    return document


# The baryon whose yield is the NUMERATOR of each flavour's ratio. The
# DENOMINATOR is never named here: `ResolveReferenceAssociateSelection`
# (improvedPlotting_THnSparse.C) resolves it from the pair registry's signed
# `referenceMesonPdg` and throws unless exactly one configured associate carries
# it, so the reference meson is derived from the same registry the yields are,
# not chosen in a configuration file.
BARYON_NUMERATOR = {"BEAUTY": "Lambda_b", "CHARM": "Lambda_c(+)-bar"}

# G8'S GEOMETRY AND ITS COMMON YIELD WINDOW (architect findings F7 and F8,
# measured on the replayed delivered canvas 2026-09-01).
#
# F8 -- THE YIELD ROW RAN 0 TO 1 and left the charm panel's data in the lowest
# 17 % of its frame. The two flavours keep ONE window, because the whole point
# of the canvas is to compare them, and it is tightened to what the pair
# needs. Measured over every drawn point and error bar of the delivered
# macros:
#
#   BEAUTY  0.142951885 .. 0.55330896
#   CHARM   0.0939992324 .. 0.16895974      the pair: 0.0940 .. 0.5533
#
# (0.08, 0.58) holds both with margin. Charm's data then spans 15 % of the
# frame instead of 7.5 %, and the empty band below it falls from 9.4 % to
# 2.8 %. Charm still sits in the lower part of the frame, and that is the
# measurement rather than a defect: its baryon/meson ratio is about four times
# beauty's, which is what the shared window exists to show.
#
# THE TUNE-RATIO ROW IS NOT CHANGED HERE. Its measured pair is
# 0.959618567 .. 3.8073786 against a (0, 4) window, so it too has an empty
# lower quarter. F8 names the 0-1 range only, and the report states the
# measurement and proposes (0.8, 4.0) rather than taking a range decision the
# brief did not ask for.
BARYONMESON_YIELD_ENVELOPE = (0.0939992324, 0.55330896)
BARYONMESON_YIELD_ENVELOPE_SOURCE = (
    "RUN-N4 delivered macro, DELIVERABLES_REVIEW_20260901/G8, measured over "
    "both flavour columns by FIG-1D's replay probe")
BARYONMESON_YIELD_WINDOW = (0.08, 0.58)

# F7 -- THE PADS FILL THE CANVAS. The rows stop at 0.93 rather than 0.95 so the
# column headers and the canvas legend have a band of their own above them,
# and the bottom margin drops from 0.32 to 0.22 because the labels below it
# are now vertical rather than slanted (the macro's `LabelsOption` ordering
# defect, R3). Measured on the replay: the blank band between the rows falls
# from 240 px to 86 px and the one below the lower row from 221 px to 66 px,
# on a 2022 px canvas.
BARYONMESON_ROW_TOP = 0.93
BARYONMESON_BOTTOM_MARGIN = 0.24
BARYONMESON_TOP_MARGIN = 0.06

# Guarded at import, like every other window in this file: a tightened window
# that no longer holds its own measurement raises before a document is built.
if not (BARYONMESON_YIELD_WINDOW[0] <= BARYONMESON_YIELD_ENVELOPE[0]
        and BARYONMESON_YIELD_ENVELOPE[1] <= BARYONMESON_YIELD_WINDOW[1]):
    raise SystemExit(
        "BARYONMESON_YIELD_WINDOW %s does not contain the measured envelope "
        "%s (%s)" % (BARYONMESON_YIELD_WINDOW, BARYONMESON_YIELD_ENVELOPE,
                     BARYONMESON_YIELD_ENVELOPE_SOURCE))

# THE BARYON SPECIES IS A CAPTION ITEM NOW (ruling R46 item 3, refined by L1).
# It used to be the display name of G8's per-panel legend entry
# (#Lambda_{b}^{0}, #bar{#Lambda}_{c}^{-}). L1 removed that legend, and R46
# item 3 gives this canvas the FLAVOUR as its column header, not the species,
# so nothing on the figure states which baryon the numerator is. The notation
# is kept HERE, unread by the generator, as the record the caption is written
# from: `FIG1D_EVIDENCE_0e98a5b_20260901/phaseA/INFORMATION_LOSS_MAP.md`
# lists it among G8's caption items, and HANDOFF's editorial notes take it
# from there. Deleting it would leave the caption writer to re-derive the
# notation from the routing keys in `BARYON_NUMERATOR` above, which is exactly
# the transcription this pair of constants exists to prevent.
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
                f"{RATIO_PANEL_GENERIC_NUMERATOR} / "
                f"{COMBINED_RATIO_DENOMINATOR}")
        keep.append(canvas)
    document["canvases_to_be_drawn"] = keep

    # THE BOTTOM BAND IS RE-MEASURED AGAINST LABELS THAT ARE ACTUALLY VERTICAL
    # (architect finding F7, with regression R3).
    #
    # This canvas puts the multiplicity CLASS on the x axis, so it carries
    # eleven labels where the others carry three to five, and the macro draws
    # them vertically because eleven slanted labels overprint one another at
    # the publication text size. FIG-1 sized this band at 0.32 for a vertical
    # label band -- but the macro's `LabelsOption("v")` ran before the labels
    # existed and did nothing, so the delivered figure has SLANTED labels and a
    # band sized for vertical ones. That is most of the 461 px of blank canvas
    # F7 measured: 240 px between the rows and 221 px below the lower one.
    #
    # With the macro's ordering repaired the labels are vertical, and the band
    # they need is measured again on the replayed canvas: 0.24 holds the eleven
    # vertical labels and the axis title, with the title 35 px clear of the
    # labels above it and 24 px clear of the pad edge below. The blank bands
    # fall from 240 px and 221 px to about 100 px and 60 px.
    for canvas in keep:
        apply_composite_margins(canvas)
        canvas["bottom_margin_mini_pad"] = BARYONMESON_BOTTOM_MARGIN
        canvas["top_margin_mini_pad"] = BARYONMESON_TOP_MARGIN

    # Two retained rows per flavour. The rows stop below the canvas top to
    # leave the band the column headers and the canvas legend now use; the
    # rest of the height goes to the pads (F7).
    TOP, ROWS = BARYONMESON_ROW_TOP, 2
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
            canvas["y_min_axis"] = BARYONMESON_YIELD_WINDOW[0]
            canvas["y_max_axis"] = BARYONMESON_YIELD_WINDOW[1]
            canvas["set_log_y"] = False
            # The x axis is the multiplicity class, not the associate species --
            # the inherited title described the base canvas, where each point was
            # a different associate. Here every point is a class and the single
            # associate is the one named in the legend.
            canvas["x_axis_title"] = "multiplicity class"
            # THE PER-PANEL LEGEND IS GONE FROM THIS CANVAS (ruling L1). FIG-1
            # gave both G8 rows a legend keyed on the ASSOCIATE name, and both
            # rendered their marker samples with no text at all -- three
            # markers floating at y = 0.9, 0.74 and 0.60 INSIDE the data area,
            # which a reader takes for data (architect regression R1). The
            # cause was never the rectangle; it is diagnosed and repaired in
            # the macro. The convention those legends carried, colour and
            # marker per tune, is now named once on the global canvas.
            #
            # The appended baryon row goes with them: it existed only to give
            # that legend a species name. The eleven CLASS entries stay,
            # because DisplayLabelForMultiplicityBin reads the same map by BIN
            # name for the x axis and dropping them sends it back to printing
            # c1_MB88p197_100. The baryon species is a caption item; the
            # Phase-A map records it.
        elif function == "drawBalancingPlotsTUNERatios":
            canvas["draw_function_to_use"] = \
                "drawBalancingBaryonMesonRatioPlotsTUNERatios"
            # The window comes from the measured envelope. See
            # BARYONMESON_TUNE_RATIO_ENVELOPE above for the render that set it.
            canvas["y_min_axis"] = BARYONMESON_TUNE_RATIO_WINDOW[0]
            canvas["y_max_axis"] = BARYONMESON_TUNE_RATIO_WINDOW[1]
            canvas["x_axis_title"] = "multiplicity class"
            # THE SAME REMOVAL, for the same reason, on the ratio row: its
            # two floating markers sat at 0.67 and 0.30 above the 90-100 % bin.
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
    document["axis_declaration"] = information_block(
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


def normalize_ratio_titles(document: dict) -> None:
    """Give every ratio panel of one configuration the one ratio y title.

    ONE MECHANISM WHERE THERE WERE THREE. The inline assignments this replaces
    each reached only the canvases their own builder authored, so the two
    configurations that INHERIT their ratio panels -- the closure and
    V-CORRELATIONS, both built by `build_integrated` with `associate_set=None`
    -- kept the base's 34- and 37-character wording and were clipped in the
    delivered renders, on a path no title site in this file could see. Running
    over the emitted document covers inherited and authored panels by one rule.

    The frozen base is not touched. Every builder deep-copies it
    (`json.loads(json.dumps(base))`), so this writes only on emitted copies and
    `tests/test_vfull_base_config.py` stays green.
    """
    for canvas in document.get("canvases_to_be_drawn", []):
        if canvas.get("draw_function_to_use") in RATIO_PANEL_DRAW_FUNCTIONS:
            canvas["y_axis_title"] = RATIO_PANEL_Y_TITLE


# THE THREE CANVAS-LEVEL PASSES R46 AND L1 ADD, and the one they replace.
#
# Until this session a composite identified itself panel by panel. Every
# panel carried a ROOT title, and a legend appeared wherever a builder had
# measured room for one -- which on the delivered set meant all six yield
# panels of G5/G7, one panel of ten on the closure and correlation canvases,
# all four of G8, and none at all on G4/G6. That is four different answers to
# one question. R46 states each fact once per canvas and L1 states each shared
# convention once per canvas, so the three passes below are canvas-level and
# the per-panel legend goes away.

# THE CANVAS-LABEL BAND (ruling R46 with L1), and why it costs plot height.
#
# R46 puts three things on the canvas that no composite carried before: the
# information block, the column headers and the one canvas legend. The pads
# used to reach 0.95 and the band above them, 0.05 of the height, held the
# single-line axis declaration and nothing else.
#
# THE THREE DO NOT FIT IN 0.05, AND THE MEASUREMENT SAYS SO. At the
# publication metric a line of the block is 33 px on a 2022 px canvas and the
# stack is two lines, 78 px -- 0.039 of the height by itself. The canvas
# legend of an extremes canvas carries five entries and measures 0.66 of the
# WIDTH, so it cannot share a row with the coverage line, which reaches 0.46
# on V-EXTREMES and further on the closure. Replayed at 0.05 the three
# overprint one another; the crop is in the evidence store.
#
# SO THE BAND IS 0.10 AND THE PADS STOP AT 0.90. L1 asks for a legend that
# costs no plot height, and a horizontal legend is what makes 0.10 enough
# rather than 0.20 -- but it is not free, and saying it is would be false.
# The cost is 5 % of the height, taken once per canvas, against identification
# that was previously repeated in every panel.
#
# ONE PASS RESCALES EVERY CONFIGURATION, because the five do not agree on
# where their rows end: the composites author 0.95, the baryon/meson canvas
# computes its own, and the closure and correlation canvases inherit the
# base's. The pass reads each document's own maximum and scales to the band,
# so a configuration added later is covered and none of them carries a second
# copy of this number.
CANVAS_LABEL_BAND_TOP = 0.90


def reserve_canvas_label_band(document: dict) -> None:
    """Scale the mini pads so they end at `CANVAS_LABEL_BAND_TOP`."""
    canvases = document.get("canvases_to_be_drawn", [])
    tops = [c["y_max_mini_pad"] for c in canvases if "y_max_mini_pad" in c]
    if not tops:
        return
    highest = max(tops)
    if highest <= 0:
        raise SystemExit("mini pads have no positive extent to rescale")
    scale = CANVAS_LABEL_BAND_TOP / highest
    for canvas in canvases:
        if "y_min_mini_pad" not in canvas or "y_max_mini_pad" not in canvas:
            continue
        canvas["y_min_mini_pad"] = round(canvas["y_min_mini_pad"] * scale, 4)
        canvas["y_max_mini_pad"] = round(canvas["y_max_mini_pad"] * scale, 4)


PANEL_LEGEND_RECTANGLE_KEYS = (
    "x_min_legend", "x_max_legend", "y_min_legend", "y_max_legend",
    "legend_columns",
)


def strip_panel_legends(document: dict) -> None:
    """No panel claims a legend, because no panel draws one (ruling L1).

    THE RECTANGLES GO, NOT JUST THEIR VALUES. Leaving `-1` behind would say
    "a legend was considered here and declined", which is not what happened:
    the convention moved to the canvas. A reader of the configuration should
    not have to know the macro's sentinel to learn that.

    `legend_entries` STAYS. It is read twice for two purposes -- this macro
    builds a legend from it by ASSOCIATE name and labels the multiplicity axis
    from it by BIN name (`DisplayLabelForMultiplicityBin`) -- so removing it
    would blank G8's x axis. Only the rectangles are legend-only.
    """
    for canvas in document.get("canvases_to_be_drawn", []):
        for key in PANEL_LEGEND_RECTANGLE_KEYS:
            canvas.pop(key, None)


def apply_panel_labels(document: dict) -> None:
    """The in-frame row label: the tune alone, where the row IS one tune.

    DERIVED FROM THE PANEL'S OWN TUNE LIST, never from its name or title. A
    yield panel configured with exactly one tune is that tune's row; a ratio
    panel with exactly one numerator is that numerator's row. Anything else --
    the combined-ratio row, which draws two numerators, and G8's yield row,
    which overlays all three tunes -- does not vary by tune, so it takes no
    row label and the canvas legend carries the tune identity instead. R46
    item 4 asks for the label; this rule is why some panels have none.
    """
    for canvas in document.get("canvases_to_be_drawn", []):
        tunes = canvas.get("TUNES", [])
        numerators = canvas.get("nominator_TUNES", [])
        if numerators:
            label = numerators[0] if len(numerators) == 1 else ""
        else:
            label = tunes[0] if len(tunes) == 1 else ""
        canvas["panel_label"] = label


def apply_canvas_identification(document: dict) -> None:
    """Every global canvas states its columns and its shared conventions.

    The composites set their own headers in `composite_globals`, from the
    trigger groups that built their columns. Every other global in this
    repository puts the two FLAVOURS side by side -- G8, the closure canvas
    and the V-CORRELATIONS composite -- so a global that has not already been
    given headers takes the flavour pair. The default is stated here rather
    than in three builders.

    The canvas legend defaults to the three tunes, which every one of these
    canvases draws. Only the extremes canvases add the marker-fill convention,
    and `build_extremes` has already put it on theirs.
    """
    for canvas in document.get("global_canvases_to_be_drawn", []):
        canvas.setdefault("column_headers", flavour_column_headers())
        canvas.setdefault("canvas_legend", canvas_legend_entries())


def variant_documents(base: dict, percentiles: list[float],
                      associate_set: str) -> dict[Path, dict]:
    """Path -> document for one associate set.

    The DEFAULT set emits the five tracked configurations. Any other set emits
    under a version-suffixed filename and is otherwise unused, so a wider
    associate axis is a new configuration version rather than an edit to the
    paper's own files (ruling R40's switch).

    `associate_set` moves the FIGURE configurations only. The closure takes
    `CLOSURE_ASSOCIATE_SET` whatever is asked for, so a suffixed run emits a
    closure identical to the tracked one: its shape answers to the accepted
    control log, not to the associate axis under evaluation.
    """
    suffix = ("" if associate_set == DEFAULT_ASSOCIATE_SET
              else "_" + associate_set)

    def path(stem: str) -> Path:
        return PLOTTING / f"configuration_multiplicity_HF_RUN3_V1_{stem}{suffix}.json"

    documents = {
        path("VEXTREMES"): build_extremes(base, percentiles, associate_set),
        path("VINTEGRATED"):
            build_integrated(base, percentiles, False, associate_set),
        path("VINTEGRATED_CLOSURE"):
            build_integrated(base, percentiles, True, CLOSURE_ASSOCIATE_SET),
        path("VBARYONMESON"): build_baryonmeson(base, percentiles),
        path("VCORRELATIONS"): build_correlations(base, percentiles),
    }

    # THE ONE PLACE THE IDENTIFICATION DECISIONS ARE WRITTEN, for every
    # configuration this function emits: the ratio y title on every ratio
    # panel each of them carries, authored or inherited; the document-level
    # switch that keeps or blanks every panel title; and, under R46 and L1,
    # the three canvas-level replacements for the titles that go off.
    # Everything `main` writes or checks comes through here.
    #
    # THESE PASSES ARE CENTRAL, NOT PER-BUILDER, because the five documents do
    # not build their canvases the same way: two author trigger-column
    # composites, two inherit the base's ten panels, and one rewrites the
    # base's four. A rule applied in each builder would be four rules that can
    # disagree. Applied here it is one rule over whatever each builder
    # produced, and a configuration added later is covered the day it is
    # emitted.
    for document in documents.values():
        normalize_ratio_titles(document)
        document["draw_canvas_titles"] = DRAW_CANVAS_TITLES
        strip_panel_legends(document)
        apply_panel_labels(document)
        apply_canvas_identification(document)
        reserve_canvas_label_band(document)
    return documents


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
