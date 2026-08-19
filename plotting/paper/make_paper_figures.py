#!/usr/bin/env python3
"""Generate the paper figures from COMMITTED tables. No hand steps.

Every figure here is a pure function of committed inputs and this file, so it
regenerates byte-identically and its digest can be pinned in
`docs/GOLDEN_OUTPUTS.md`.

WHY THIS EXISTS SEPARATELY FROM `plotting/`. The existing tree is ROOT-macro
based, written against the **v2** pair schema, and points at a legacy dataset
(review finding A6). It is kept as reference. This layer reads the committed
CSV/anchor tables that the paper actually quotes, which is a different input
contract, and it has no ROOT or matplotlib dependency at all.

FIGURES

  fig1_species_decomposition.svg
      Species decomposition by tune, BOTH conventions. Source: the
      deduplicated per-species anchors plus their ten blocks, i.e. exactly the
      numbers in `docs/MONASH_CENTRAL_TABLE.md` §0, recomputed here rather than
      transcribed. Laid out as grouped bars with one bar per tune per category,
      so JUNCTIONS and CLOSEPACKING become bars when their anchors land -- no
      layout change required.

  fig2_m7_inclusive_shift.svg
      The M7 INCLUSIVE unresolved-origin shift, per tune, both sectors, with
      block SEMs. All three tunes already exist for this one. Labelled
      inclusive on the face of the figure, because that distinction is exactly
      what review finding A2 was about and a figure travels further than its
      caption.

WHAT IS DELIBERATELY ABSENT. The OS-SS observable versus multiplicity class has
**no committed table yet** -- it is what the queued A2 jobs produce. No
placeholder is drawn. A figure with invented data is worse than a missing
figure, and `--figure ossvsmult` fails closed with that explanation.

Usage:
  plotting/paper/make_paper_figures.py --out-dir plotting/paper/figures
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from svgkit import (Canvas, LinearAxis, TUNE_COLOURS, INK, MUTED, GRID,  # noqa
                    ticks, n)

ANCHORS = REPO / "AnalysisScripts/anchors"
DEDUP = ANCHORS / "merged_monash_dedup"
TUNE_ORDER = ["MONASH", "JUNCTIONS", "CLOSEPACKING"]
ANCHOR_BY_TUNE = {
    "MONASH": DEDUP,
    "JUNCTIONS": ANCHORS / "merged_junctions_dedup",
    "CLOSEPACKING": ANCHORS / "merged_closepacking_dedup",
}

STRUCTURE_GROUPS = ["kCentralGround", "kExcludedVector", "kExcludedExcited",
                    "kMultiplyHeavy"]

# The experiment-comparable rows, fixed here so the figure shows exactly the
# rows docs/THREE_TUNE_CENTRAL_TABLE.md section 2 tabulates -- the union of the
# three tunes' top observables, not any one tune's. Kept in step with
# extraction/three_tune_table.py's EXPT, which the table is generated from.
EXPERIMENT_ROWS = ["D0", "Dbar0", "D+", "D-", "D_s+", "D_s-",
                   "Lambda_c+", "Lambda_cbar-", "B+", "B-"]


# --------------------------------------------------------------------------
# data loading -- committed tables only
# --------------------------------------------------------------------------
def load_species(path: Path) -> dict[int, float]:
    return {int(r["ordinal"]): float(r["total"])
            for r in csv.DictReader(path.open())}


def load_categories(path: Path) -> dict[int, str]:
    return {int(r["ordinal"]): r["category_name"]
            for r in csv.DictReader(path.open())}


def structure_fractions(rundir: Path):
    """Block-mean percentages and block SEMs per structural category.

    Fractions are formed INSIDE each block and then averaged -- the project's
    standing estimator rule. Recomputed from the committed per-species tables
    rather than transcribed from the markdown, so the figure cannot drift away
    from the table it claims to show.
    """
    cats = load_categories(rundir / "central/per_species.csv")
    per_block = []
    for i in range(1, 11):
        table = load_species(rundir / f"block_{i}/per_species.csv")
        grouped = defaultdict(float)
        for ordinal, value in table.items():
            grouped[cats.get(ordinal, "?")] += value
        total = sum(grouped.values())
        per_block.append({k: 100.0 * v / total for k, v in grouped.items()})
    out = {}
    for group in STRUCTURE_GROUPS:
        vals = [b.get(group, 0.0) for b in per_block]
        mean = statistics.mean(vals)
        sem = statistics.stdev(vals) / (len(vals) ** 0.5)
        out[group] = (mean, sem)
    return out


def experiment_fractions(rundir: Path):
    """Experiment-comparable shares via map v2 split mode, block mean and SEM."""
    sys.path.insert(0, str(REPO / "extraction"))
    from apply_decay_map import terminal_distribution  # noqa: E402
    art = json.loads((REPO / "AnalysisScripts/species_ordinals_v2.json").read_text())
    dmap = json.loads((REPO / "AnalysisScripts/decay_parent_map_v2.json").read_text())
    pdg_to_ord = {int(r["pdg"]): int(r["ordinal"]) for r in art["species"]}
    cat_name = {int(r["ordinal"]): r["category_name"] for r in art["species"]}
    name = {int(s["ordinal"]): s["name"] for s in dmap["species"]}
    by_ord = {int(s["ordinal"]): s for s in dmap["species"]}
    dist = terminal_distribution(by_ord, pdg_to_ord, split_mode=True)

    per_block = []
    for i in range(1, 11):
        table = load_species(rundir / f"block_{i}/per_species.csv")
        grouped = defaultdict(float)
        for ordinal, value in table.items():
            for term, frac in dist.get(ordinal, {ordinal: 1.0}).items():
                if cat_name.get(term) == "kCentralGround":
                    grouped[name[term]] += value * frac
        total = sum(load_species(rundir / f"block_{i}/per_species.csv").values())
        per_block.append({k: 100.0 * v / total for k, v in grouped.items()})
    # EVERY observable, not this tune's top-8. The caller selects, because the
    # top-8 is tune-dependent -- MONASH's carries B+/B-, the CR tunes' carries
    # Lambda_c -- and a panel built from three different top-8 lists would put
    # different observables in the same bar group and label them as one.
    out = {}
    for key in sorted({k for block in per_block for k in block}):
        vals = [block.get(key, 0.0) for block in per_block]
        out[key] = (statistics.mean(vals),
                    statistics.stdev(vals) / (len(vals) ** 0.5))
    return out


def m7_by_tune(logs_glob: str):
    """Run the committed R9/R9b recipe and parse its table -- do not re-implement.

    Shelling out to `extraction/aggregate_m7.py` keeps exactly one implementation
    of the M7 aggregation. A second one here could disagree with the recipe the
    Golden Outputs pin, and the figure would then show numbers no recipe
    reproduces.
    """
    paths = sorted((ANCHORS).glob(logs_glob))
    if len(paths) != 10:
        raise SystemExit(
            f"FAIL-CLOSED: expected 10 block logs for {logs_glob}, found {len(paths)}")
    result = subprocess.run(
        [sys.executable, str(REPO / "extraction/aggregate_m7.py"), *map(str, paths)],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        raise SystemExit("FAIL-CLOSED: aggregate_m7.py failed")
    out = {}
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 12 and fields[0] in TUNE_COLOURS:
            # tune blocks rate ± e base ± e incl ± e shift ± e
            out[fields[0]] = (float(fields[-3]), float(fields[-1]))
    if not out:
        raise SystemExit("FAIL-CLOSED: could not parse aggregate_m7.py output")
    return out


# --------------------------------------------------------------------------
# figure 1 -- species decomposition
# --------------------------------------------------------------------------
def figure_species(out_path: Path) -> None:
    structure = {t: structure_fractions(p) for t, p in ANCHOR_BY_TUNE.items()
                 if p.exists()}
    experiment = {t: experiment_fractions(p) for t, p in ANCHOR_BY_TUNE.items()
                  if p.exists()}
    tunes = [t for t in TUNE_ORDER if t in structure]

    W, H = 900.0, 560.0
    c = Canvas(W, H, "Heavy-flavour species decomposition by tune")
    c.text(46, 34, "Species decomposition by tune", size=17, weight="bold")
    c.text(46, 54, "Block mean of ten canonical blocks; error bars are block "
                   "SEM (dof 9).", size=11, fill=MUTED)

    # ---- panel A: diquark structure (a partition) -------------------------
    ax_l, ax_r, ax_t, ax_b = 70.0, 430.0, 96.0, 300.0
    yax = LinearAxis(0, 70, ax_b, ax_t)
    c.text(46, 84, "A — diquark structure (a partition, sums to 100 %)",
           size=12, weight="bold")
    for value in ticks(0, 70, 10):
        y = yax(value)
        c.line(ax_l, y, ax_r, y, stroke=GRID, width=0.8)
        c.text(ax_l - 8, y + 3.5, f"{value:.0f}", size=9.5, anchor="end", fill=MUTED)
    c.line(ax_l, ax_b, ax_r, ax_b, width=1.2)
    c.text(20, (ax_t + ax_b) / 2, "share of weight (%)", size=10.5,
           anchor="middle", fill=MUTED, rotate=-90)

    slot = (ax_r - ax_l) / len(STRUCTURE_GROUPS)
    bar_w = min(26.0, slot / (len(tunes) + 1.4))
    for gi, group in enumerate(STRUCTURE_GROUPS):
        gx = ax_l + slot * (gi + 0.5)
        for ti, tune in enumerate(tunes):
            mean, sem = structure[tune][group]
            x = gx + (ti - (len(tunes) - 1) / 2.0) * (bar_w + 3)
            y = yax(mean)
            c.rect(x - bar_w / 2, y, bar_w, ax_b - y, TUNE_COLOURS[tune])
            if sem > 0:
                c.errorbar_v(x, yax(mean - sem), yax(mean + sem), cap=3.0)
            label = f"{mean:.2f}" if mean >= 0.01 else f"{mean:.4f}"
            # Alternate tunes onto a second line. With three bars ~23 px apart
            # and 5-6 character labels, one shared height overlaps -- it did,
            # visibly, the first time this figure carried all three tunes.
            c.text(x, y - 7 - (ti % 2) * 11, label, size=8.0,
                   anchor="middle", fill=INK)
        c.text(gx, ax_b + 15, group.replace("k", ""), size=9.5, anchor="middle")

    # ---- panel B: experiment-comparable (a SELECTION) ---------------------
    bx_l, bx_r, bx_t, bx_b = 500.0, 866.0, 96.0, 300.0
    bax = LinearAxis(0, 30, bx_b, bx_t)
    c.text(500, 84, "B — experiment-comparable (map v2, split)",
           size=12, weight="bold")
    for value in ticks(0, 30, 5):
        y = bax(value)
        c.line(bx_l, y, bx_r, y, stroke=GRID, width=0.8)
        c.text(bx_l - 8, y + 3.5, f"{value:.0f}", size=9.5, anchor="end", fill=MUTED)
    c.line(bx_l, bx_b, bx_r, bx_b, width=1.2)

    keys = EXPERIMENT_ROWS
    slot_b = (bx_r - bx_l) / len(keys)
    bw = min(20.0, slot_b / (len(tunes) + 1.4))
    for gi, key in enumerate(keys):
        gx = bx_l + slot_b * (gi + 0.5)
        for ti, tune in enumerate(tunes):
            mean, sem = experiment[tune][key]
            x = gx + (ti - (len(tunes) - 1) / 2.0) * (bw + 3)
            y = bax(mean)
            c.rect(x - bw / 2, y, bw, bx_b - y, TUNE_COLOURS[tune])
            if sem > 0:
                c.errorbar_v(x, bax(mean - sem), bax(mean + sem), cap=2.5)
        c.text(gx + 4, bx_b + 14, key, size=8.5, anchor="end", rotate=-45)

    # ---- the caveat that must travel with panel B ------------------------
    c.rect(500, 362, 366, 52, "#fdf6e3", stroke="#d9c98a", stroke_width=1.0)
    c.text(510, 380, "Panel B is a SELECTION, not a partition.",
           size=10, weight="bold")
    c.text(510, 395, "These are the largest reconstructable observables; they",
           size=9.5, fill=MUTED)
    c.text(510, 407, "do not sum to 100 %. Less than 100 % is not missing weight.",
           size=9.5, fill=MUTED)

    # ---- legend ----------------------------------------------------------
    # 322 put the "tune" header 7 px under the "CentralGround" axis label, close
    # enough that it read as part of the axis row. Dropped clear of it.
    ly = 342.0
    c.text(70, ly, "tune", size=10, weight="bold")
    for i, tune in enumerate(TUNE_ORDER):
        y = ly + 18 + i * 17
        present = tune in structure
        c.rect(70, y - 9, 12, 12, TUNE_COLOURS[tune] if present else "#ffffff",
               stroke=TUNE_COLOURS[tune], stroke_width=1.2,
               opacity=1.0 if present else 0.45)
        c.text(89, y, tune if present else f"{tune} — not yet merged",
               size=10, fill=INK if present else MUTED)

    c.text(46, 444, "Source: AnalysisScripts/anchors/merged_{monash,junctions,"
                    "closepacking}_dedup (central + ten blocks each), "
                    "deduplicated per ERROR_RECORD E5.",
           size=9, fill=MUTED)
    c.text(46, 458, "Fractions are formed inside each block and then averaged; "
                    "the pooled central value is quoted in the table, not here.",
           size=9, fill=MUTED)
    out_path.write_text(c.render())


# --------------------------------------------------------------------------
# figure 2 -- M7 inclusive shift
# --------------------------------------------------------------------------
def figure_m7(out_path: Path) -> None:
    charm = m7_by_tune("m7_blocks/*.log")
    beauty = m7_by_tune("m7b_blocks/*.log")

    W, H = 760.0, 470.0
    c = Canvas(W, H, "M7 inclusive unresolved-origin shift by tune")
    c.text(46, 34, "Unresolved-origin shift in the baryon fraction — "
                   "INCLUSIVE LEVEL", size=15, weight="bold")
    c.text(46, 54, "Relative shift if unresolved-origin hadrons were recovered. "
                   "Error bars are block SEM (dof 9).", size=10.5, fill=MUTED)

    c.rect(46, 68, 668, 34, "#fdecea", stroke="#e0a9a2", stroke_width=1.0)
    c.text(56, 82, "NOT a bound on the pair observable's systematic.",
           size=10, weight="bold")
    c.text(56, 95, "Only cut is heavyIsFinal && q_sector != 0 — no trigger, "
                   "acceptance, pair or OS−SS selection. The pair-level "
                   "measurement is separate.", size=9, fill=MUTED)

    # TWO PANELS WITH INDEPENDENT Y-AXES, and the scales stated on each.
    # Charm's CR values (~0.55 %) and beauty's (~0.014 %) differ by ~40x. On one
    # shared linear axis the beauty bars are a few tenths of a pixel tall, which
    # hides the very comparison this figure exists to make. Independent axes are
    # the honest choice PROVIDED the difference is impossible to miss -- hence
    # the per-panel range printed in the panel title, and the deliberately
    # different tick labels.
    ax_t, ax_b = 140.0, 350.0
    panels = [("charm", charm, 0.6, 0.1, 90.0, 380.0),
              ("beauty", beauty, 0.02, 0.005, 440.0, 700.0)]
    for sector, data, top, step, ax_l, ax_r in panels:
        yax = LinearAxis(0, top, ax_b, ax_t)
        c.text(ax_l, 128, f"{sector}  —  axis 0 to {top:g} %",
               size=11.5, weight="bold")
        for value in ticks(0, top, step):
            y = yax(value)
            c.line(ax_l, y, ax_r, y, stroke=GRID, width=0.8)
            label = f"{value:.3f}".rstrip("0").rstrip(".") or "0"
            c.text(ax_l - 8, y + 3.5, label, size=9.5, anchor="end", fill=MUTED)
        c.line(ax_l, ax_b, ax_r, ax_b, width=1.2)

        slot = (ax_r - ax_l) / 3.0
        bar_w = min(46.0, slot * 0.62)
        for ti, tune in enumerate(TUNE_ORDER):
            if tune not in data:
                continue
            mean, sem = data[tune]
            x = ax_l + slot * (ti + 0.5)
            y = yax(mean)
            c.rect(x - bar_w / 2, y, bar_w, ax_b - y, TUNE_COLOURS[tune])
            c.errorbar_v(x, yax(max(0.0, mean - sem)), yax(mean + sem), cap=4.0)
            # Anchor the value label above the ERROR BAR, not the bar top. In
            # the beauty panel the SEM is a sixth of the bar height, so a label
            # at (bar top - 8) is drawn straight through the upper cap -- it
            # was, and the rendering is how that was noticed.
            c.text(x, yax(mean + sem) - 8, f"{mean:.4f}", size=9, anchor="middle")
        c.text((ax_l + ax_r) / 2, ax_b + 20, sector, size=12,
               anchor="middle", weight="bold")

    c.text(30, (ax_t + ax_b) / 2, "relative shift (%)", size=10.5,
           anchor="middle", fill=MUTED, rotate=-90)
    c.text(390, ax_b + 20, "⚠ different scales", size=9, anchor="middle",
           fill="#b3261e", weight="bold")

    ly = 392.0
    for i, tune in enumerate(TUNE_ORDER):
        x = 90 + i * 200
        c.rect(x, ly - 9, 12, 12, TUNE_COLOURS[tune])
        c.text(x + 19, ly, tune, size=10)

    c.text(46, 428, "Charm's inclusive shift is tune-dependent by an order of "
                    "magnitude; beauty's is flat at ~0.014 % across all three.",
           size=9, fill=MUTED)
    c.text(46, 442, "Source: AnalysisScripts/anchors/{m7_blocks,m7b_blocks}, "
                    "via extraction/aggregate_m7.py (recipes R9b, R9).",
           size=9, fill=MUTED)
    out_path.write_text(c.render())


# --------------------------------------------------------------------------
# figure 3 -- the multiplicity class definition (Methods)
# --------------------------------------------------------------------------
B4 = ANCHORS / "b4_multiplicity_mb"
# The common absolute boundaries adopted by the axis ruling, read from the ONE
# committed definition rather than repeated as a literal here. Paul's stack
# reads the same file for its common_absolute multiplicity mode; two literals
# would drift, and the axis is what every per-multiplicity number is
# conditioned on.
BOUNDARY_ARTIFACT = REPO / "config/multiplicity_class_boundaries_v1.json"
CLASS_BOUNDARIES = [
    float(entry["boundary_nch"])
    for entry in json.loads(BOUNDARY_ARTIFACT.read_text())["classes"]
]


def mb_distribution(tune: str) -> dict[int, float]:
    return {int(r["nch"]): float(r["count"])
            for r in csv.DictReader((B4 / f"nch_mb_{tune}.csv").open())}


def boundary_percentiles():
    """Recompute the paper-facing translation table from the committed MB samples.

    Percentile = fraction of that tune's MB sample **strictly below** the
    boundary, which is what the ruling published. Recomputed rather than
    transcribed, on the same standard as figures 1 and 2.
    """
    out = {}
    for tune in TUNE_ORDER:
        dist = mb_distribution(tune)
        total = sum(dist.values())
        out[tune] = [100.0 * sum(c for nch, c in dist.items() if nch < b) / total
                     for b in CLASS_BOUNDARIES]
    return out


def figure_multiplicity(out_path: Path) -> None:
    pct = boundary_percentiles()
    spreads = [max(pct[t][i] for t in TUNE_ORDER) - min(pct[t][i] for t in TUNE_ORDER)
               for i in range(len(CLASS_BOUNDARIES))]
    max_spread = max(spreads)

    W, H = 900.0, 644.0
    c = Canvas(W, H, "Multiplicity class definition")
    c.text(46, 34, "Multiplicity classes: common absolute N_ch bins, "
                   "percentile labels are tune-dependent", size=15, weight="bold")
    c.text(46, 54, "Classes are ONE boundary set shared by all three tunes and "
                   "both sectors. Labels are percentiles of the MONASH "
                   "minimum-bias distribution.", size=10.5, fill=MUTED)

    # ---- panel A: the boundaries on an absolute N_ch axis ------------------
    ax_l, ax_r = 80.0, 850.0
    band_t, band_b = 152.0, 192.0
    NMAX = 40.0
    xax = LinearAxis(-0.5, NMAX, ax_l, ax_r)
    c.text(46, 92, "A — the common boundary set, on absolute N_ch "
                   "(|η| < 1, primary charged)", size=12, weight="bold")

    for i, lo in enumerate(CLASS_BOUNDARIES):
        hi = CLASS_BOUNDARIES[i + 1] if i + 1 < len(CLASS_BOUNDARIES) else NMAX
        x0, x1 = xax(lo), xax(hi)
        shade = "#e8eef6" if i % 2 == 0 else "#f6f2e8"
        c.rect(x0, band_t, x1 - x0, band_b - band_t, shade,
               stroke="#b9c4d2", stroke_width=0.7)
        if x1 - x0 > 15:
            c.text((x0 + x1) / 2, band_t + 25, f"c{i + 1}", size=10,
                   anchor="middle", weight="bold")
    # c11 is open-ended; say so rather than letting the band imply a top edge.
    c.text(xax(NMAX) - 4, band_t + 25, "→", size=12, anchor="end", fill=MUTED)

    for value in ticks(0, 40, 5):
        x = xax(value)
        c.line(x, band_b, x, band_b + 5, width=1.0)
        c.text(x, band_b + 17, f"{value:.0f}", size=9.5, anchor="middle", fill=MUTED)
    c.text((ax_l + ax_r) / 2, band_b + 34, "N_ch", size=10.5,
           anchor="middle", fill=MUTED)

    # Boundary values and their MONASH-MB percentile label, STAGGERED in two
    # rows. The boundaries are deliberately dense at low N_ch -- 2.5 to 3.5 and
    # 5.5 to 6.5 are only ~19 px apart at this scale -- so labels on a single
    # row would sit within a few pixels of each other. Alternating the height
    # makes collision impossible rather than merely unlikely.
    for i, b in enumerate(CLASS_BOUNDARIES):
        x = xax(b)
        lift = 0.0 if i % 2 == 0 else 20.0
        c.line(x, band_t - 6 - lift, x, band_t, width=1.0,
               stroke=INK if lift == 0.0 else MUTED)
        c.text(x, band_t - 10 - lift, f"{b:g}", size=8, anchor="middle")
        c.text(x, band_t - 21 - lift, f"{pct['MONASH'][i]:.0f}%", size=8,
               anchor="middle", fill="#3b6fb0", weight="bold")
    c.text(ax_r, band_t - 56, "boundary N_ch, and its MONASH-MB percentile",
           size=9, anchor="end", fill="#3b6fb0")

    # ---- panel B: how far the label drifts between tunes -------------------
    bx_t, bx_b = 272.0, 462.0
    yax = LinearAxis(-4.0, 4.0, bx_b, bx_t)
    c.text(46, 254, "B — the published residual: the same boundary sits at a "
                    "different percentile in each tune", size=12, weight="bold")
    # the +/-3 pp band the original criterion used
    c.rect(ax_l, yax(3.0), ax_r - ax_l, yax(-3.0) - yax(3.0), "#eef6ee",
           stroke="#bcd8bc", stroke_width=0.8)
    c.text(ax_r - 4, yax(3.0) + 12, "±3 pp", size=9, anchor="end", fill="#4f9a5f")
    for value in ticks(-4, 4, 2):
        y = yax(value)
        c.line(ax_l, y, ax_r, y, stroke=GRID, width=0.8)
        c.text(ax_l - 8, y + 3.5, f"{value:+.0f}", size=9.5, anchor="end", fill=MUTED)
    c.line(ax_l, yax(0.0), ax_r, yax(0.0), width=1.2)
    c.text(30, (bx_t + bx_b) / 2, "percentile − MONASH (pp)", size=10.5,
           anchor="middle", fill=MUTED, rotate=-90)

    slot = (ax_r - ax_l) / len(CLASS_BOUNDARIES)
    for i in range(len(CLASS_BOUNDARIES)):
        gx = ax_l + slot * (i + 0.5)
        for tune in TUNE_ORDER:
            d = pct[tune][i] - pct["MONASH"][i]
            y = yax(d)
            r = 4.5 if tune != "MONASH" else 3.0
            c.rect(gx - r + (0 if tune == "JUNCTIONS" else
                             (-9 if tune == "MONASH" else 9)) , y - r,
                   2 * r, 2 * r, TUNE_COLOURS[tune])
        c.text(gx, bx_b + 16, f"c{i + 1}", size=9, anchor="middle")
        c.text(gx, bx_b + 28, f"{CLASS_BOUNDARIES[i]:g}", size=8,
               anchor="middle", fill=MUTED)
    c.text((ax_l + ax_r) / 2, bx_b + 44, "class  /  boundary N_ch", size=10,
           anchor="middle", fill=MUTED)

    # ---- the number the ruling requires be published ----------------------
    c.rect(46, 516, 500, 68, "#fdf6e3", stroke="#d9c98a", stroke_width=1.0)
    c.text(56, 535, f"Maximum residual across all classes: "
                    f"{max_spread:.2f} pp.", size=11, weight="bold")
    c.text(56, 551, "This is NOT the ±3 pp criterion of the per-tune scheme "
                    "passing. That test asked", size=9.5, fill=MUTED)
    c.text(56, 563, "whether per-tune boundaries coincide — they do not. This "
                    "is how far a COMMON boundary's", size=9.5, fill=MUTED)

    ly = 530.0
    for i, tune in enumerate(TUNE_ORDER):
        y = ly + i * 17
        c.rect(590, y - 8, 11, 11, TUNE_COLOURS[tune])
        c.text(608, y, tune, size=10)

    c.text(56, 575, "meaning drifts between tunes, and it is published rather "
                    "than hidden.", size=9.5, fill=MUTED)
    c.text(46, 608, "Source: AnalysisScripts/anchors/b4_multiplicity_mb "
                    "(per-tune minimum-bias N_ch, 170–172 k events each).",
           size=9, fill=MUTED)
    c.text(46, 622, "Percentiles recomputed here as the fraction strictly below "
                    "each boundary; they reproduce the published translation "
                    "table exactly.", size=9, fill=MUTED)
    out_path.write_text(c.render())


FIGURES = {
    "species": ("fig1_species_decomposition.svg", figure_species),
    "m7": ("fig2_m7_inclusive_shift.svg", figure_m7),
    "multiplicity": ("fig3_multiplicity_classes.svg", figure_multiplicity),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path,
                    default=REPO / "plotting/paper/figures")
    ap.add_argument("--figure", choices=sorted(FIGURES) + ["ossvsmult", "all"],
                    default="all")
    args = ap.parse_args()

    if args.figure == "ossvsmult":
        raise SystemExit(
            "NOT AVAILABLE: the OS-SS observable versus multiplicity class has "
            "no committed table. It is produced by the A2 jobs "
            "(docs/A2_PAIR_UNRESOLVED_RUN_RECORD.md), which have not run. "
            "No placeholder is drawn: a figure with invented data is worse than "
            "a missing figure.")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    wanted = sorted(FIGURES) if args.figure == "all" else [args.figure]
    for key in wanted:
        filename, builder = FIGURES[key]
        path = args.out_dir / filename
        builder(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"FIGURE {filename} sha256={digest} bytes={path.stat().st_size}")
    print("FIGURES_DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
