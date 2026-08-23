#!/usr/bin/env python3
"""The per-class combination, on hand-computed anchors.

The anchors use a nominal of 100.0 so that a delta of 3.0 is 3 per cent and the
arithmetic can be checked by eye. The contributions are chosen to make 3-4-5
triangles, so every total below is exact in binary floating point and can be
verified without running anything.

THE REGISTERED CASE IS THE FIRST ONE: a cell where one source is
resolved and contributes its |Delta|, and another is NOT resolved and
contributes its SEM. Ruling A1 is continuous, so no branch on resolution appears
anywhere in the arithmetic, and this test is what holds that true.
"""
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "extraction"))

from combine_per_class import (SOURCES, SourcesIncomplete, as_percent,  # noqa: E402
                               combine_cell, headline_ratio,
                               missing_campaigns, tune_separation)
from systematics_delta import (CombinationPolicyRequired,  # noqa: E402
                               UNRESOLVED_MAX_ABS_OR_SEM, Delta,
                               combine_quadrature, contribution_of)

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def row(campaign, delta, sem, nominal=100.0):
    return {"campaign": campaign, "class": "c1", "delta": delta,
            "delta_sem": sem, "nominal_yield": nominal}


# --- THE MIXED RESOLVED AND UNRESOLVED CELL -------------------------------
# S1a  up +3.0 +/- 0.5, down -1.0 +/- 0.5 -> quotes UP, |D| = 3 >= 2*0.5,
#                                            RESOLVED, contributes |D| = 3
# S3   +1.0 +/- 4.0, ONE-SIDED under R9    -> quotes PTHAT_4, |D| = 1 < 2*4.0,
#                                            UNRESOLVED, contributes SEM = 4
# S1b  and S2 are exactly zero, so neither is "non-negligible" and section 9.1
#      does not fire.
# total = sqrt(3^2 + 4^2) = 5, exactly.
MIXED = {
    "HF_SYS_MUR_UP": row("HF_SYS_MUR_UP", 3.0, 0.5),
    "HF_SYS_MUR_DOWN": row("HF_SYS_MUR_DOWN", -1.0, 0.5),
    "HF_SYS_MUF_UP": row("HF_SYS_MUF_UP", 0.0, 0.0),
    "HF_SYS_MUF_DOWN": row("HF_SYS_MUF_DOWN", 0.0, 0.0),
    "HF_SYS_PDF_CTEQ6L1": row("HF_SYS_PDF_CTEQ6L1", 0.0, 0.0),
    "HF_SYS_PTHAT_4": row("HF_SYS_PTHAT_4", 1.0, 4.0),
}
mixed = combine_cell(MIXED)
check("the mixed cell combines to exactly 5 per cent",
      mixed["combined_percent"] == 5.0, "%.17g" % mixed["combined_percent"])
check("the resolved source contributes its |Delta|, 3",
      mixed["terms_percent"]["S1a_mur"]["contribution"] == 3.0,
      str(mixed["terms_percent"]["S1a_mur"]))
check("the UNRESOLVED source contributes its SEM, 4, not its |Delta| of 1",
      mixed["terms_percent"]["S3_pthat"]["contribution"] == 4.0,
      str(mixed["terms_percent"]["S3_pthat"]))
check("the larger arm is quoted for the scale source",
      mixed["quoted_arm"]["S1a_mur"] == "HF_SYS_MUR_UP",
      str(mixed["quoted_arm"]))
check("the larger arm is quoted for the pT-hat source",
      mixed["quoted_arm"]["S3_pthat"] == "HF_SYS_PTHAT_4",
      str(mixed["quoted_arm"]))
check("nothing is dropped when mu_F and PDF are both negligible",
      mixed["dropped"] == [], str(mixed["dropped"]))
# Ruling R11 (2026-08-23) holds S5 unresolved on the v2 percentile axis, so it
# contributes NO term. Its old contribution was max(|0|, 0) = 0, so the removal
# changes no combined value -- the total above is still exactly 5.
check("R11: S5 contributes no term at all",
      "S5_class_migration" not in mixed["terms_percent"],
      str(sorted(mixed["terms_percent"])))
# Ruling R9 (2026-08-23) makes S3 one-sided. The excluded arm is quoted nowhere.
check("R9: S3 is quoted from HF_SYS_PTHAT_4 alone",
      mixed["quoted_arm"]["S3_pthat"] == "HF_SYS_PTHAT_4"
      and "HF_SYS_PTHAT_1" not in set(mixed["quoted_arm"].values()),
      str(mixed["quoted_arm"]))

# --- RULING A1 IS CONTINUOUS ---------------------------------------------
# max(|D|, SEM) has no cliff. At |D| = SEM the two expressions agree, and
# crossing 2*SEM changes nothing at all.
sem = 2.0
below = contribution_of(Delta(1.999, sem, 10, "t"), UNRESOLVED_MAX_ABS_OR_SEM)
at = contribution_of(Delta(2.0, sem, 10, "t"), UNRESOLVED_MAX_ABS_OR_SEM)
above = contribution_of(Delta(2.001, sem, 10, "t"), UNRESOLVED_MAX_ABS_OR_SEM)
check("the contribution is flat at the SEM floor either side of it",
      below == 2.0 and at == 2.0, f"{below} {at}")
check("and it rises continuously once |Delta| passes the SEM",
      abs(above - 2.001) < 1e-12, str(above))
# The 2 SEM flag is presentational: a delta at 3.9 with SEM 2.0 is UNRESOLVED
# (3.9 < 4.0) and still contributes its full |Delta|, because |D| > SEM.
check("an unresolved delta above the SEM still contributes its |Delta|",
      contribution_of(Delta(3.9, 2.0, 10, "t"),
                      UNRESOLVED_MAX_ABS_OR_SEM) == 3.9)

# --- SECTION 9.1, mu_F AND PDF ON THE SAME OBJECT -------------------------
# Both non-negligible: quote the larger, drop the other. |PDF| = 4 > |muF| = 3,
# so S1b_muf is dropped and the total is 4, not 5.
NINE_ONE = dict(MIXED)
NINE_ONE.update({
    "HF_SYS_MUR_UP": row("HF_SYS_MUR_UP", 0.0, 0.0),
    "HF_SYS_MUR_DOWN": row("HF_SYS_MUR_DOWN", 0.0, 0.0),
    "HF_SYS_MUF_UP": row("HF_SYS_MUF_UP", 3.0, 0.5),
    "HF_SYS_MUF_DOWN": row("HF_SYS_MUF_DOWN", -1.0, 0.5),
    "HF_SYS_PDF_CTEQ6L1": row("HF_SYS_PDF_CTEQ6L1", -4.0, 0.5),
    "HF_SYS_PTHAT_4": row("HF_SYS_PTHAT_4", 0.0, 0.0),
})
nine_one = combine_cell(NINE_ONE)
check("mu_F is dropped when PDF is the larger of the two",
      nine_one["dropped"] == ["S1b_muf"], str(nine_one["dropped"]))
check("and the total is the PDF term alone, 4",
      nine_one["combined_percent"] == 4.0,
      "%.17g" % nine_one["combined_percent"])

# --- RULING A2, S6 IS NEVER SUMMED IN ------------------------------------
try:
    combine_quadrature({"S1a_mur": Delta(1.0, 0.1, 10, "t"),
                        "S6": Delta(9.0, 0.1, 10, "t")},
                       unresolved_policy=UNRESOLVED_MAX_ABS_OR_SEM,
                       s6_policy="separate")
    check("an S6 term in a per-class sum is refused", False, "no raise")
except CombinationPolicyRequired:
    check("an S6 term in a per-class sum is refused", True)

try:
    combine_quadrature({"S1a_mur": Delta(1.0, 0.1, 10, "t")},
                       unresolved_policy=UNRESOLVED_MAX_ABS_OR_SEM,
                       s6_policy="merged")
    check("any s6_policy other than 'separate' is refused", False, "no raise")
except CombinationPolicyRequired:
    check("any s6_policy other than 'separate' is refused", True)

# --- UNITS COMMUTE --------------------------------------------------------
# Every source in one cell shares one nominal, so rescaling to per cent is a
# common positive factor. Combining in per cent and multiplying back must equal
# combining in the absolute units directly.
NOMINAL = 0.5
SCALED = {c: row(c, r["delta"] * NOMINAL / 100.0,
                 r["delta_sem"] * NOMINAL / 100.0, NOMINAL)
          for c, r in MIXED.items()}
scaled = combine_cell(SCALED)
check("rescaling to per cent leaves the per-cent total unchanged",
      abs(scaled["combined_percent"] - 5.0) < 1e-12,
      "%.17g" % scaled["combined_percent"])
check("and the absolute total is the per-cent total times the nominal",
      abs(scaled["combined_absolute"] - 5.0 * NOMINAL / 100.0) < 1e-15,
      "%.17g" % scaled["combined_absolute"])

try:
    combine_cell({**MIXED, "HF_SYS_MUF_UP": row("HF_SYS_MUF_UP", 1.0, 1.0,
                                                nominal=0.0)})
    check("a zero nominal is refused rather than divided by", False, "no raise")
except ZeroDivisionError:
    check("a zero nominal is refused rather than divided by", True)

# --- SECTION 9, NO PARTIAL SUM -------------------------------------------
partial = {c: r for c, r in MIXED.items()
           if c not in ("HF_SYS_MUF_UP", "HF_SYS_PDF_CTEQ6L1")}
check("the two campaigns still merging are named as missing",
      missing_campaigns(set(partial)) == ["HF_SYS_MUF_UP",
                                          "HF_SYS_PDF_CTEQ6L1"],
      str(missing_campaigns(set(partial))))
try:
    combine_cell(partial)
    check("a partial source set is refused", False, "no raise")
except SourcesIncomplete:
    check("a partial source set is refused", True)
# Seven campaigns were registered. R9 excludes HF_SYS_PTHAT_1, so six are
# required. The seventh stays declared, excluded, in the source contract.
check("six campaigns are required after R9", len(
    {c for arms in SOURCES.values() for c in arms}) == 6,
    str(sorted({c for arms in SOURCES.values() for c in arms})))
check("and HF_SYS_PTHAT_1 is not one of them",
      "HF_SYS_PTHAT_1" not in {c for arms in SOURCES.values() for c in arms})

# --- THE TUNE SEPARATION --------------------------------------------------
# 0.12 - 0.10 = 0.02;  sqrt(0.003^2 + 0.004^2) = 0.005.
sep = tune_separation({
    "MONASH": {"nominal_yield": 0.12, "nominal_sem": 0.003},
    "JUNCTIONS": {"nominal_yield": 0.10, "nominal_sem": 0.004}})
check("the tune separation is MONASH minus JUNCTIONS",
      "%.6g" % sep["difference"] == "0.02", "%.17g" % sep["difference"])
check("its SEM adds the two tune SEMs in quadrature",
      "%.6g" % sep["difference_sem"] == "0.005",
      "%.17g" % sep["difference_sem"])
check("the headline ratio divides separation by systematic",
      headline_ratio(0.02, 0.005) == 4.0)
check("a zero systematic with a real separation is infinite",
      headline_ratio(0.02, 0.0) == math.inf)
check("a zero separation on a zero systematic is not",
      headline_ratio(0.0, 0.0) == 0.0)

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'ALL CHECKS PASS'}")
sys.exit(1 if failures else 0)
