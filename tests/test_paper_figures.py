#!/usr/bin/env python3
"""The paper figures must be deterministic and must agree with their sources.

A figure is a claim. These checks stop the two ways a generated figure quietly
becomes a false one:

  1. NON-DETERMINISM -- if the bytes move between runs, the digest pinned in
     GOLDEN_OUTPUTS is meaningless and "regenerate and compare" cannot be a
     check on anything.
  2. DRIFT FROM THE SOURCE -- if the figure's numbers stop matching the
     committed table it claims to plot, the figure is the thing people will
     read. So the structural percentages are recomputed here from the anchors
     and required to appear, to the precision the figure prints them.

Plus the fail-closed case: the OS-SS-versus-multiplicity figure has no data yet
and must REFUSE rather than draw a placeholder.
"""
import hashlib
import re
import statistics
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "plotting/paper/make_paper_figures.py"
DEDUP = REPO / "AnalysisScripts/anchors/merged_monash_dedup"

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def build(out_dir: Path):
    return subprocess.run(
        [sys.executable, str(TOOL), "--out-dir", str(out_dir)],
        capture_output=True, text=True)


def digests(out_dir: Path):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out_dir.glob("*.svg"))}


# ---- expected structural values, recomputed from the committed anchors -----
def structural_means():
    import csv
    cats = {int(r["ordinal"]): r["category_name"]
            for r in csv.DictReader((DEDUP / "central/per_species.csv").open())}
    per_block = []
    for i in range(1, 11):
        rows = list(csv.DictReader((DEDUP / f"block_{i}/per_species.csv").open()))
        grouped = defaultdict(float)
        for r in rows:
            grouped[cats.get(int(r["ordinal"]), "?")] += float(r["total"])
        tot = sum(grouped.values())
        per_block.append({k: 100.0 * v / tot for k, v in grouped.items()})
    return {g: statistics.mean([b.get(g, 0.0) for b in per_block])
            for g in ("kCentralGround", "kExcludedVector", "kExcludedExcited")}


with tempfile.TemporaryDirectory() as td:
    a, b = Path(td) / "a", Path(td) / "b"

    r1 = build(a)
    check("generator exits 0", r1.returncode == 0,
          (r1.stdout + r1.stderr)[-400:])
    check("all three figures produced", len(list(a.glob("*.svg"))) == 3,
          str(sorted(p.name for p in a.glob('*.svg'))))

    r2 = build(b)
    check("second run exits 0", r2.returncode == 0, r2.stderr[-300:])
    da, db = digests(a), digests(b)
    check("DETERMINISTIC across runs", da == db,
          f"{da} != {db}")

    # ---- the figure must show what the table says -------------------------
    fig1 = (a / "fig1_species_decomposition.svg").read_text()
    expected = structural_means()
    for group, value in expected.items():
        shown = f"{value:.2f}"
        check(f"fig1 shows {group} as {shown}", f">{shown}<" in fig1,
              f"expected label {shown}")

    # The SELECTION caveat is the one piece of text that must never be dropped:
    # panel B is routinely misread as a partition.
    check("fig1 carries the SELECTION-not-partition caveat",
          "SELECTION" in fig1 and "not sum to 100" in fig1)

    # ---- all three tunes, since 2026-08-16 --------------------------------
    # The reserved slots filled when the JUNCTIONS and CLOSEPACKING anchors
    # landed. Pinning this stops a future anchor move from silently returning
    # the figure to one tune while its caption still claims three.
    for tune in ("MONASH", "JUNCTIONS", "CLOSEPACKING"):
        check(f"fig1 legend carries {tune}", f">{tune}<" in fig1)
    check("fig1 no longer says any tune is unmerged",
          "not yet merged" not in fig1)
    # The CR tunes' OWN values, from docs/THREE_TUNE_CENTRAL_TABLE.md -- the
    # figure must show the tune it names, not MONASH's number three times.
    for value in ("58.23", "54.17", "39.94", "40.00", "1.78", "5.77"):
        check(f"fig1 panel A shows {value}", f">{value}<" in fig1)
    # Panel B must use the table's COMMON row set. Lambda_c is in the CR tunes'
    # top-8 and NOT in MONASH's, so its presence proves the union was used
    # rather than whichever tune happens to be drawn first.
    for row in ("Lambda_c+", "Lambda_cbar-", "B+", "B-"):
        check(f"fig1 panel B carries the common row {row}", f">{row}<" in fig1)

    fig2 = (a / "fig2_m7_inclusive_shift.svg").read_text()
    check("fig2 is labelled INCLUSIVE on its face", "INCLUSIVE LEVEL" in fig2)
    check("fig2 states it is not a bound on the pair observable",
          "NOT a bound" in fig2)
    check("fig2 warns that its two panels use different scales",
          "different scales" in fig2)

    # ---- fig 3: recomputed percentiles must match the published ruling ----
    # The translation table in PRODUCTION_SHAPE_DECISION is a paper-facing
    # number. The figure recomputes it from the committed MB samples, so this
    # asserts the recomputation still lands on the published values -- and in
    # particular pins the maximum residual, which is the quantity the axis
    # ruling requires be published.
    sys.path.insert(0, str(REPO / "plotting/paper"))
    from make_paper_figures import boundary_percentiles, CLASS_BOUNDARIES  # noqa
    PUBLISHED = {
        "MONASH": [0.00, 11.80, 19.40, 34.06, 40.15, 49.69, 56.97, 65.39,
                   73.85, 82.88, 91.58],
        "JUNCTIONS": [0.00, 11.22, 18.04, 31.49, 37.24, 46.79, 54.18, 63.08,
                      72.11, 81.73, 90.84],
        "CLOSEPACKING": [0.00, 11.86, 19.09, 33.06, 38.93, 48.37, 55.79, 64.62,
                         73.67, 83.26, 92.10],
    }
    pct = boundary_percentiles()
    worst = max(abs(pct[t][i] - PUBLISHED[t][i])
                for t in PUBLISHED for i in range(len(CLASS_BOUNDARIES)))
    check("fig3 percentiles reproduce the published translation table",
          worst < 0.01, f"worst deviation {worst:.4f} pp")
    spread = max(max(pct[t][i] for t in PUBLISHED) - min(pct[t][i] for t in PUBLISHED)
                 for i in range(len(CLASS_BOUNDARIES)))
    check("fig3 max residual is the published 2.91 pp",
          abs(spread - 2.91) < 0.01, f"got {spread:.4f}")

    fig3 = (a / "fig3_multiplicity_classes.svg").read_text()
    check("fig3 states the maximum residual on its face",
          "2.91 pp" in fig3, "")
    check("fig3 says the classes are COMMON absolute bins",
          "common boundary set" in fig3 and "absolute N_ch" in fig3)
    # The residual is easy to misread as the +/-3 pp criterion passing. The
    # ruling is explicit that it is a different test; the figure must say so.
    check("fig3 distinguishes the residual from the ±3 pp criterion",
          "NOT the ±3 pp criterion" in fig3, "")

    # ---- the fail-closed case --------------------------------------------
    r3 = subprocess.run(
        [sys.executable, str(TOOL), "--figure", "ossvsmult",
         "--out-dir", str(a)],
        capture_output=True, text=True)
    out = r3.stdout + r3.stderr
    check("OS-SS-vs-multiplicity refuses rather than inventing data",
          r3.returncode != 0 and "NOT AVAILABLE" in out, out[-300:])
    check("and says why", "invented data" in out, out[-200:])

print()
if failures:
    for f in failures:
        print("FAIL:", f)
    sys.exit(1)
print("PASS test_paper_figures.py")
