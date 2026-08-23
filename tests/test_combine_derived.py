#!/usr/bin/env python3
"""Systematics on derived quantities, on hand-computed anchors.

The combination anchors use a nominal of 100, so a per-cent contribution is
numerically the absolute one and the arithmetic can be checked by eye. The
contributions are a 3-4-5 triangle, so every total is exact in binary floating
point.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extraction"))

from combine_derived import (combined_systematic, endpoint_contrast,  # noqa: E402
                             ratio_at, trend_difference, verdict)

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def row(yield_, sem, reference, ratio_sem):
    return {"central_yield": str(yield_), "yield_sem": str(sem),
            "reference_yield": str(reference), "ratio_sem": str(ratio_sem),
            "ratio_status": "PASS"}


# --- the ratio comes from the plotter, not from propagation ---------------
# 0.05 / 0.25 = 0.2 exactly, and the SEM is the plotter's, NOT sqrt-combined
# from the two yield SEMs -- numerator and denominator share their triggers.
ROWS = {("BEAUTY", "B^{+}", "MONASH", "Lambda_b", "c1"): row(0.05, 9.9, 0.25, 0.004),
        ("BEAUTY", "B^{+}", "MONASH", "Lambda_b", "c11"): row(0.09, 9.9, 0.30, 0.003),
        ("BEAUTY", "B^{+}", "JUNCTIONS", "Lambda_b", "c1"): row(0.10, 9.9, 0.25, 0.006),
        ("BEAUTY", "B^{+}", "JUNCTIONS", "Lambda_b", "c11"): row(0.24, 9.9, 0.30, 0.008)}

value, sem = ratio_at(ROWS, "MONASH", "c1")
check("the ratio divides yield by reference yield", value == 0.2, str(value))
check("its SEM is the plotter's ratio_sem, not the yield SEMs",
      sem == 0.004, str(sem))

# c11 0.09/0.30 = 0.3;  c1 = 0.2;  contrast = 0.1
# sqrt(0.003^2 + 0.004^2) = 0.005 exactly.
contrast, contrast_sem = endpoint_contrast(ROWS, "MONASH")
check("the endpoint contrast is R(c11) - R(c1)",
      abs(contrast - 0.1) < 1e-15, "%.17g" % contrast)
check("its SEM adds the two class SEMs in quadrature",
      contrast_sem == 0.005, "%.17g" % contrast_sem)

# JUNCTIONS: 0.24/0.30 = 0.8, 0.10/0.25 = 0.4, contrast 0.4.
# trend = 0.4 - 0.1 = 0.3.  SEM = sqrt(0.005^2 + sqrt(0.008^2+0.006^2)^2)
#       = sqrt(0.005^2 + 0.01^2)
trend, trend_sem = trend_difference(ROWS, "JUNCTIONS")
check("the trend difference subtracts the two contrasts",
      abs(trend - 0.3) < 1e-15, "%.17g" % trend)
check("and its SEM combines them in quadrature",
      abs(trend_sem - math.sqrt(0.005 ** 2 + 0.01 ** 2)) < 1e-18,
      "%.17g" % trend_sem)

for bad, why in (
        ({**ROWS, ("BEAUTY", "B^{+}", "MONASH", "Lambda_b", "c1"):
          {**ROWS[("BEAUTY", "B^{+}", "MONASH", "Lambda_b", "c1")],
           "ratio_status": "FAIL"}}, "a non-PASS ratio_status is refused"),
        ({**ROWS, ("BEAUTY", "B^{+}", "MONASH", "Lambda_b", "c1"):
          row(0.05, 1, 0.0, 0.004)}, "a zero reference yield is refused")):
    try:
        ratio_at(bad, "MONASH", "c1")
        check(why, False, "no exception")
    except (ValueError, ZeroDivisionError):
        check(why, True)

# --- the combination over the included arms -------------------------------
# nominal 100, so per cent equals absolute.
#   S1a  up +3 (sem 0.5), down -1  -> quotes UP,   contributes |3| = 3
#   S3   +1 (sem 4), ONE-SIDED     -> quotes PTHAT_4, UNRESOLVED, contributes 4
#   S1b, S2 exactly zero            -> negligible, section 9.1 does not fire
# total = sqrt(3^2 + 4^2) = 5.
# Seven campaigns were registered. Ruling R9 excludes HF_SYS_PTHAT_1, so this
# fixture supplies six and the arm the contract forbids appears nowhere.
INCLUDED = {
    "HF_SYS_MUR_UP": (103.0, 0.5), "HF_SYS_MUR_DOWN": (99.0, 0.5),
    "HF_SYS_MUF_UP": (100.0, 0.0), "HF_SYS_MUF_DOWN": (100.0, 0.0),
    "HF_SYS_PDF_CTEQ6L1": (100.0, 0.0),
    "HF_SYS_PTHAT_4": (101.0, 4.0),
}
combined = combined_systematic(100.0, 0.0, INCLUDED)
check("the included-arm combination totals exactly 5 per cent",
      combined["combined_percent"] == 5.0, "%.17g" % combined["combined_percent"])
check("R9: the derived route quotes S3 one-sided too",
      combined["quoted_arm"]["S3_pthat"] == "HF_SYS_PTHAT_4",
      str(combined["quoted_arm"]))
check("and 5 in absolute units on a nominal of 100",
      combined["combined_absolute"] == 5.0, str(combined["combined_absolute"]))
check("the resolved source contributes its |Delta|",
      combined["terms_percent"]["S1a_mur"]["contribution"] == 3.0)
check("the UNRESOLVED source contributes its SEM, not its |Delta| of 1",
      combined["terms_percent"]["S3_pthat"]["contribution"] == 4.0)
check("the larger arm is quoted", combined["quoted_arm"]["S1a_mur"] == "HF_SYS_MUR_UP")
check("nothing is dropped when mu_F and PDF are negligible",
      combined["dropped"] == [], str(combined["dropped"]))

# A NEGATIVE nominal must give the same absolute answer: the rescaling uses the
# magnitude, and MONASH's own endpoint contrast is negative.
# Mirroring about zero: with nominal -100, value -v gives Delta' = -Delta, so
# every |Delta| is unchanged and the total must be identical.
negative = combined_systematic(-100.0, 0.0, {c: (-v, s)
                                        for c, (v, s) in INCLUDED.items()})
check("a negative nominal gives the same absolute systematic",
      abs(negative["combined_absolute"] - 5.0) < 1e-12,
      str(negative["combined_absolute"]))

try:
    combined_systematic(100.0, 0.0,
                        {k: v for k, v in list(INCLUDED.items())[:5]})
    check("a partial source set is refused", False, "no exception")
except ValueError:
    check("a partial source set is refused", True)
try:
    combined_systematic(0.0, 0.0, INCLUDED)
    check("a zero nominal is refused rather than divided by", False, "no raise")
except ZeroDivisionError:
    check("a zero nominal is refused rather than divided by", True)

# --- unequal nonzero nominal/variation SEM regression --------------------
# This fixture distinguishes the audited two-SEM method from the former
# variation-only implementation and asserts the full derived total plus the
# classification it controls. Nominal=100 keeps per cent and absolute units
# equal. S1a contributes 10, S2 contributes 12 while S1b is dropped, S3 has
# variation SEM 3 and nominal SEM 4 so contributes 5, and S5 has exact shift
# zero plus the same nominal SEM so contributes 4. Total=sqrt(285).
TWO_SEM = {
    "HF_SYS_MUR_UP": (110.0, 1.0), "HF_SYS_MUR_DOWN": (99.0, 2.0),
    "HF_SYS_MUF_UP": (111.0, 1.0), "HF_SYS_MUF_DOWN": (101.0, 2.0),
    "HF_SYS_PDF_CTEQ6L1": (112.0, 1.0),
    "HF_SYS_PTHAT_4": (100.0, 3.0),
}
variation_only = combined_systematic(100.0, 0.0, TWO_SEM)
two_sem = combined_systematic(100.0, 4.0, TWO_SEM)
check("unequal nonzero SEMs use sqrt(variation^2 + nominal^2)",
      two_sem["terms_percent"]["S3_pthat"]["sem"] == 5.0,
      str(two_sem["terms_percent"]["S3_pthat"]))
check("the structural-zero source retains the nominal SEM",
      two_sem["terms_percent"]["S5_class_migration"]["contribution"] == 4.0,
      str(two_sem["terms_percent"]["S5_class_migration"]))
check("the full corrected derived systematic is sqrt(285)",
      two_sem["combined_absolute"] == math.sqrt(285.0),
      "%.17g" % two_sem["combined_absolute"])
check("the former variation-only total lies above the two-sigma threshold",
      verdict(34.0, 4.0, variation_only["combined_absolute"])["significance"] > 2.0)
check("the corrected full total changes that two-sigma classification",
      verdict(34.0, 4.0, two_sem["combined_absolute"])["significance"] < 2.0)

for bad_sem in (-1.0, math.inf, math.nan):
    try:
        combined_systematic(100.0, bad_sem, INCLUDED)
        check(f"nominal SEM {bad_sem!r} is refused", False, "no raise")
    except ValueError:
        check(f"nominal SEM {bad_sem!r} is refused", True)

# --- the verdict ----------------------------------------------------------
# 3-4-5 again: stat 3, syst 4 -> total 5.
v = verdict(10.0, 3.0, 4.0)
check("the total uncertainty adds stat and syst in quadrature", v["total"] == 5.0)
check("significance is |value| / total", v["significance"] == 2.0)
check("a value at twice its total uncertainty EXCEEDS", v["survives"] is True)
check("a value below its total uncertainty does not",
      verdict(4.0, 3.0, 4.0)["survives"] is False)
check("a value exactly at its total uncertainty does not exceed it",
      verdict(5.0, 3.0, 4.0)["survives"] is False)

# The real trend figure, at the precision the tool prints.
real = verdict(0.35362, 0.01287, 0.15999)
check("the real trend total is 0.160507",
      "%.6g" % real["total"] == "0.160507", "%.17g" % real["total"])
check("its significance is 2.2", round(real["significance"], 1) == 2.2,
      str(real["significance"]))
check("and it EXCEEDS its total uncertainty", real["survives"] is True)

# --- committed verdict v2 is synchronized with the corrected method -------
artifact = json.loads(
    (ROOT / "results/systematics/20260820/verdict.json").read_text()
)
rows = artifact["per_class"] + artifact["trend"]
check("the committed verdict uses the two-SEM schema",
      artifact["schema"] == "hadronization_verdict_v2" and len(rows) == 77,
      f"schema={artifact.get('schema')} rows={len(rows)}")
artifact_errors = []
for index, item in enumerate(rows):
    value = item.get("separation", item.get("value"))
    nominal_pct = item["stat"] / abs(value) * 100.0
    for name, term in item["terms_percent"].items():
        expected_sem = math.hypot(term["variation_sem"], nominal_pct)
        expected_contribution = max(abs(term["delta"]), expected_sem)
        if not math.isclose(term["nominal_sem"], nominal_pct, rel_tol=1e-14):
            artifact_errors.append(f"row {index} {name}: nominal SEM")
        if not math.isclose(term["sem"], expected_sem, rel_tol=1e-14):
            artifact_errors.append(f"row {index} {name}: combined SEM")
        if not math.isclose(term["contribution"], expected_contribution,
                            rel_tol=1e-14):
            artifact_errors.append(f"row {index} {name}: contribution")
    kept = [
        term["contribution"]
        for name, term in item["terms_percent"].items()
        if name not in item.get("dropped", [])
    ]
    syst = math.sqrt(sum(value_ ** 2 for value_ in kept)) * abs(value) / 100.0
    total = math.hypot(item["stat"], syst)
    if not math.isclose(item["syst"], syst, rel_tol=1e-14):
        artifact_errors.append(f"row {index}: systematic")
    if not math.isclose(item["total"], total, rel_tol=1e-14):
        artifact_errors.append(f"row {index}: total")
check("all 77 committed rows recompute from their two-SEM terms",
      not artifact_errors, "; ".join(artifact_errors[:5]))
check("the corrected per-class two-sigma count is 35 of 72",
      sum(item["significance"] > 2.0 for item in artifact["per_class"]) == 35)
headline = next(item for item in artifact["trend"]
                if item["quantity"] == "trend CLOSEPACKING - MONASH")
check("the corrected CLOSEPACKING headline is below two sigma",
      math.isclose(headline["significance"], 1.9897812393049878,
                   rel_tol=1e-14) and headline["significance"] < 2.0,
      str(headline["significance"]))

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'ALL CHECKS PASS'}")
sys.exit(1 if failures else 0)
