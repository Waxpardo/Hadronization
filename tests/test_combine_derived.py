#!/usr/bin/env python3
"""Systematics on derived quantities, on hand-computed anchors.

The combination anchors use a nominal of 100, so a per-cent contribution is
numerically the absolute one and the arithmetic can be checked by eye. The
contributions are a 3-4-5 triangle, so every total is exact in binary floating
point.
"""
import copy
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extraction"))

from combine_derived import (combined_systematic, endpoint_contrast,  # noqa: E402
                             ratio_at, trend_difference, verdict)
from combine_per_class import load_source_contract  # noqa: E402

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def block_sem(values):
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values)
                     / (len(values) * (len(values) - 1)))


def row(yield_, sem, reference, blocks):
    return {"central_yield": str(yield_), "yield_sem": str(sem),
            "reference_yield": str(reference),
            "ratio_sem": str(block_sem(blocks)),
            "block_ratios": blocks,
            "ratio_status": "PASS"}


# --- the ratio comes from the plotter, not from propagation ---------------
# 0.05 / 0.25 = 0.2 exactly, and the SEM is the plotter's, NOT sqrt-combined
# from the two yield SEMs -- numerator and denominator share their triggers.
MONASH_LOW = [1.0, 2.0, 3.0, 4.0]
MONASH_HIGH = [3.0, 4.0, 5.0, 6.0]
JUNCTIONS_LOW = [1.0, 2.0, 3.0, 4.0]
JUNCTIONS_HIGH = [4.0, 4.0, 8.0, 8.0]
ROWS = {("BEAUTY", "B^{+}", "MONASH", "Lambda_b", "c1"):
            row(0.05, 9.9, 0.25, MONASH_LOW),
        ("BEAUTY", "B^{+}", "MONASH", "Lambda_b", "c11"):
            row(0.09, 9.9, 0.30, MONASH_HIGH),
        ("BEAUTY", "B^{+}", "JUNCTIONS", "Lambda_b", "c1"):
            row(0.10, 9.9, 0.25, JUNCTIONS_LOW),
        ("BEAUTY", "B^{+}", "JUNCTIONS", "Lambda_b", "c11"):
            row(0.24, 9.9, 0.30, JUNCTIONS_HIGH)}

value, sem = ratio_at(ROWS, "MONASH", "c1")
check("the ratio divides yield by reference yield", value == 0.2, str(value))
check("its SEM is the plotter's block-ratio SEM, not the yield SEMs",
      sem == block_sem(MONASH_LOW), str(sem))

# c11 0.09/0.30 = 0.3;  c1 = 0.2;  contrast = 0.1
# The aligned block differences are [2,2,2,2], so their sample SEM is zero.
# The old independent-endpoint quadrature is positive and therefore decisive.
contrast, contrast_sem = endpoint_contrast(ROWS, "MONASH")
check("the endpoint contrast is R(c11) - R(c1)",
      abs(contrast - 0.1) < 1e-15, "%.17g" % contrast)
check("its SEM is formed from aligned block endpoint differences",
      contrast_sem == 0.0, "%.17g" % contrast_sem)
old_quadrature = math.hypot(block_sem(MONASH_HIGH), block_sem(MONASH_LOW))
check("seen to fail: replacing the aligned calculation with old quadrature",
      old_quadrature != contrast_sem,
      f"old={old_quadrature:.17g} aligned={contrast_sem:.17g}")

# JUNCTIONS: 0.24/0.30 = 0.8, 0.10/0.25 = 0.4, contrast 0.4.
# trend = 0.4 - 0.1 = 0.3. MONASH's aligned endpoint SEM is zero;
# JUNCTIONS uses the SEM of [3,2,5,4]. Separate tune campaigns then combine.
trend, trend_sem = trend_difference(ROWS, "JUNCTIONS")
check("the trend difference subtracts the two contrasts",
      abs(trend - 0.3) < 1e-15, "%.17g" % trend)
check("and its SEM combines independent tune-level endpoint SEMs",
      abs(trend_sem - block_sem([3.0, 2.0, 5.0, 4.0])) < 1e-18,
      "%.17g" % trend_sem)

for bad, why in (
        ({**ROWS, ("BEAUTY", "B^{+}", "MONASH", "Lambda_b", "c1"):
          {**ROWS[("BEAUTY", "B^{+}", "MONASH", "Lambda_b", "c1")],
           "ratio_status": "FAIL"}}, "a non-PASS ratio_status is refused"),
        ({**ROWS, ("BEAUTY", "B^{+}", "MONASH", "Lambda_b", "c1"):
          row(0.05, 1, 0.0, MONASH_LOW)}, "a zero reference yield is refused")):
    try:
        ratio_at(bad, "MONASH", "c1")
        check(why, False, "no exception")
    except (ValueError, ZeroDivisionError):
        check(why, True)

missing_block = copy.deepcopy(ROWS)
missing_block[("BEAUTY", "B^{+}", "MONASH", "Lambda_b", "c1")][
    "block_ratios"].pop()
try:
    ratio_at(missing_block, "MONASH", "c1")
    check("a perturbed MONASH/c1 block_ratios vector is refused", False,
          "no exception")
except ValueError as error:
    check("a perturbed MONASH/c1 block_ratios vector is refused",
          "MONASH c1" in str(error) and "ratio_sem" in str(error), str(error))

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
# equal. S1a contributes 10, S2 contributes 12 while S1b is dropped, and S3 has
# variation SEM 3 and nominal SEM 4 so contributes 5. Total=sqrt(269).
#
# RULING R16 (2026-08-23) MOVED THIS TOTAL. Before it, this route added a fifth
# term for S5_class_migration -- exact shift zero plus the same nominal SEM, so
# a contribution of 4 -- from a constant, whatever the source contract said.
# R11 had already excluded S5, so the total was sqrt(285) here and sqrt(269) on
# the per-class route for the same declared sources. Under R16 the derived
# route reads the contract, S5 contributes nothing, and the two agree:
# sqrt(285) - 4^2 = sqrt(269). The demonstration value below moved from 34 to
# 33 for the same reason; see the comment there.
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
check("R16: an excluded source contributes no term",
      "S5_class_migration" not in two_sem["terms_percent"],
      str(sorted(two_sem["terms_percent"])))
check("the full corrected derived systematic is sqrt(269)",
      two_sem["combined_absolute"] == math.sqrt(269.0),
      "%.17g" % two_sem["combined_absolute"])
# Amendment D2 still flips a classification, and this pins it. The value is 33,
# not the 34 this fixture used before R16: with S5 out of the derived budget,
# both totals fell, and 34 now sits above two sigma on BOTH. 33 straddles them
# again -- variation-only 2.012, two-SEM 1.955 -- so the check still measures
# what D2 does rather than passing by luck.
check("the former variation-only total lies above the two-sigma threshold",
      verdict(33.0, 4.0, variation_only["combined_absolute"])["significance"] > 2.0,
      str(verdict(33.0, 4.0, variation_only["combined_absolute"])["significance"]))
check("the corrected full total changes that two-sigma classification",
      verdict(33.0, 4.0, two_sem["combined_absolute"])["significance"] < 2.0,
      str(verdict(33.0, 4.0, two_sem["combined_absolute"])["significance"]))

# --- R16: the contract decides, and the floor rule survives ---------------
# The measured-zero floor is gated, not deleted. A synthetic contract that
# INCLUDES a re-measured S5 must bring the term back with no code change, which
# is what "the rule applies to the new measurement" has to mean in practice.
tracked = load_source_contract()
check("the tracked contract excludes S5",
      not next(row for row in tracked["sources"]
               if row["source"] == "S5_class_migration")["included"])
excluded_by_source = {row["source"]: row["reason"] for row in two_sem["exclusions"]}
check("R16: the exclusion is recorded in the output with its reason",
      excluded_by_source.get("S5_class_migration", "").startswith("R11:"),
      str(two_sem["exclusions"]))
check("R16: the excluded ARM is recorded in the same list",
      any(row["source"] == "S3_pthat"
          and row["campaign"] == "HF_SYS_PTHAT_1"
          and row["reason"].startswith("R9:")
          for row in two_sem["exclusions"]),
      str(two_sem["exclusions"]))

RE_MEASURED = copy.deepcopy(tracked)
for row in RE_MEASURED["sources"]:
    if row["source"] == "S5_class_migration":
        row["included"] = True
        row.pop("exclusion_reason", None)
        row["reason"] = "synthetic: re-measured as an exact zero on the v2 axis"
restored = combined_systematic(100.0, 4.0, TWO_SEM, sources=RE_MEASURED)
check("R16: an INCLUDED measured zero brings the floor term back",
      restored["terms_percent"]["S5_class_migration"]["contribution"] == 4.0,
      str(restored["terms_percent"].get("S5_class_migration")))
check("its shift is exactly zero and its variation SEM is zero",
      restored["terms_percent"]["S5_class_migration"]["delta"] == 0.0
      and restored["terms_percent"]["S5_class_migration"]["variation_sem"] == 0.0,
      str(restored["terms_percent"]["S5_class_migration"]))
check("and the total returns to sqrt(285)",
      restored["combined_absolute"] == math.sqrt(285.0),
      "%.17g" % restored["combined_absolute"])
check("a re-included S5 is no longer listed as excluded",
      all(row["source"] != "S5_class_migration"
          for row in restored["exclusions"]),
      str(restored["exclusions"]))

# An exclusion with no recorded reason is refused, not combined.
UNREASONED = copy.deepcopy(tracked)
for row in UNREASONED["sources"]:
    if row["source"] == "S5_class_migration":
        row["exclusion_reason"] = "   "
try:
    combined_systematic(100.0, 4.0, TWO_SEM, sources=UNREASONED)
    check("an exclusion with no reason is refused", False, "no raise")
except ValueError as error:
    check("an exclusion with no reason is refused",
          "exclusion_reason" in str(error), str(error))

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
