#!/usr/bin/env python3
"""The figure-4 inset must take its boundaries from the artifact, not from a quantile.

THE DEFECT THIS PINS. `Plot_InclusiveKinematicSpectra_Raw.C` drew its MONASH
percentile inset from `CalculateMultiplicityThreshold(hist, p)` -- a running
-integral quantile of whatever histogram it was handed. That is a per-tune
derivation of an axis that `docs/PRODUCTION_SHAPE_DECISION.md` ruled is absolute
and shared, and it was wrong on two independent counts:

  1. The histogram it quantised is the PRODUCTION sample (HardQCD, pTHatMin = 2),
     while the percentile labels are defined on the MONASH MINIMUM-BIAS
     distribution. Boundaries from one distribution, labels from another.
  2. `config/multiplicity_class_boundaries_v1.json` states in its own text that
     it is the one definition and that no consumer may carry a copy, "because
     two definitions drift, and the axis is the thing every per-multiplicity
     number is conditioned on". The macro was a third consumer that never read
     it -- the boundaries macro had been updated, this one had not.

What is pinned here is not "the include exists" but the property that makes the
figure correct: the drawn boundaries are the committed artifact's, and the drawn
labels are recomputed from the committed MB anchor by the same rule, reproducing
the frozen receipt. A future edit that reintroduces a quantile fails here rather
than in a figure nobody re-derives.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MACRO = ROOT / "plotting" / "Plot_InclusiveKinematicSpectra_Raw.C"
ARTIFACT = ROOT / "config" / "multiplicity_class_boundaries_v1.json"
MB_ANCHOR = ROOT / "AnalysisScripts" / "anchors" / "b4_multiplicity_mb"
RECEIPT = (ROOT / "results" / "validation" / "plotting" /
           "hf_run3_v1_threetune_20260816" /
           "multiplicity_boundary_receipt_v1_polished.json")
MODEL = ROOT / "paper" / "Model.tex"
PHYSICS = ROOT / "docs" / "PHYSICS.md"

# The receipt stores percentiles to three decimals, so agreement is asserted at
# the receipt's own precision and no tighter.
TOLERANCE = 0.001


def boundaries() -> list[float]:
    artifact = json.loads(ARTIFACT.read_text())
    return [c["boundary_nch"] for c in artifact["classes"]]


def mb_top_percentiles() -> list[float]:
    """100 - (fraction strictly below), the receipt's 'top p%' convention."""
    dist = {int(r["nch"]): float(r["count"])
            for r in csv.DictReader((MB_ANCHOR / "nch_mb_MONASH.csv").open())}
    total = sum(dist.values())
    return [100.0 - 100.0 * sum(c for n, c in dist.items() if n < b) / total
            for b in boundaries()]


def code_without_comments() -> str:
    """The macro's source with `//` comments stripped.

    The assertions below are about CODE. The comment block that records why the
    quantile helper was removed necessarily names it, and a bare substring test
    would read that explanation as the defect returning.
    """
    lines = []
    for line in MACRO.read_text().splitlines():
        marker = line.find("//")
        lines.append(line if marker < 0 else line[:marker])
    return "\n".join(lines)


def test_macro_reads_the_artifact_and_not_a_quantile() -> None:
    source = MACRO.read_text()
    assert "CommonMultiplicityBoundaries.h" in source, \
        "the macro must include the shared boundary reader"
    assert "LoadCommonBoundaries" in source, \
        "the macro must resolve the committed artifact"
    # The quantile helper is the defect itself. Its absence from the CODE is
    # the fix; the comment that explains the removal may still name it.
    code = code_without_comments()
    assert "CalculateMultiplicityThreshold" not in code, \
        ("the per-tune quantile helper is back; the inset would again draw "
         "production-sample quantiles under minimum-bias labels")
    assert "MultiplicityThresholds(" not in code, \
        "the quantile threshold map is back in the code path"


def test_labels_are_recomputed_not_transcribed() -> None:
    """A literal percentile table in the macro would be a second definition.

    Checked against code only: the comment recording the verification against
    the frozen receipt quotes a percentile, and that is documentation, not a
    second definition.
    """
    code = code_without_comments()
    for literal in ("8.422", "17.124", "26.154", "34.614", "43.03"):
        assert literal not in code, \
            f"percentile {literal} is transcribed into the macro; recompute it"


def test_recomputed_labels_reproduce_the_frozen_receipt() -> None:
    """The closed loop: artifact boundaries + MB anchor == the frozen receipt.

    The receipt carries ONE more row than the artifact has boundaries. The
    artifact defines 11 classes by their 11 lower edges and leaves the top class
    open-ended; the receipt additionally stores that open end as percentile 0.0
    with the overflow sentinel 4095. So the 11 recomputed percentiles must be a
    subset of the receipt's 12, and the single uncovered row must be that
    sentinel -- not some boundary that quietly failed to match.
    """
    receipt = json.loads(RECEIPT.read_text())
    stored = {t["percentile"]: t["nch_threshold"]
              for t in receipt["tunes"]["MONASH"]["thresholds"]}
    computed = mb_top_percentiles()
    assert len(stored) == len(computed) + 1, (len(stored), len(computed))

    matched = set()
    for got in computed:
        near = min(stored, key=lambda p: abs(p - got))
        assert abs(near - got) < TOLERANCE, \
            f"percentile {got} does not reproduce any frozen value (nearest {near})"
        matched.add(near)

    leftover = set(stored) - matched
    assert len(leftover) == 1, f"expected exactly one uncovered row, got {leftover}"
    only = leftover.pop()
    assert only == 0.0 and stored[only] == 4095, \
        (f"the uncovered receipt row should be the open-ended sentinel "
         f"(0.0%, 4095); it is ({only}, {stored[only]})")


def test_thresholds_are_the_boundary_minus_a_half() -> None:
    """Each boundary's inclusive upper N_ch is that boundary minus 0.5.

    Half-integer edges exist so no integer N_ch is ambiguous about its class;
    this is what makes the receipt's integer thresholds and the artifact's
    half-integer boundaries the same statement.

    One edge case, and it is physical rather than a fudge: the lowest boundary
    is -0.5, whose formal inclusive upper is -1. N_ch cannot be negative, so the
    receipt clamps it to 0. That clamp is asserted explicitly instead of being
    skipped, so a change to it fails here.
    """
    receipt = json.loads(RECEIPT.read_text())
    by_pct = {t["percentile"]: t["nch_threshold"]
              for t in receipt["tunes"]["MONASH"]["thresholds"]}
    for boundary, pct in zip(boundaries(), mb_top_percentiles()):
        match = min(by_pct, key=lambda p: abs(p - pct))
        assert abs(match - pct) < TOLERANCE, (boundary, pct, match)
        expected = max(int(boundary - 0.5), 0)
        assert by_pct[match] == expected, \
            (f"boundary {boundary} should give inclusive upper {expected}, "
             f"receipt says {by_pct[match]}")


def test_public_definition_discloses_predicate_and_measured_limitation() -> None:
    model = MODEL.read_text()
    physics = PHYSICS.read_text()
    prose = " ".join((model + physics).split())
    for required in (
        "final charged non-heavy",
        "0.7670",
        "exactly zero",
        "forced hard-heavy sample",
        "does not correct the percentile labels",
    ):
        assert required in prose, required
    for predicate in (
        "isFinal",
        "isCharged",
        "!hasHeavyConstituent",
        "pT > 0.15",
        "abs(eta) <= 1",
    ):
        assert predicate in " ".join(physics.split()), predicate
    assert "Event activity counts final charged primary particles" not in model


def main() -> int:
    test_macro_reads_the_artifact_and_not_a_quantile()
    test_labels_are_recomputed_not_transcribed()
    test_recomputed_labels_reproduce_the_frozen_receipt()
    test_thresholds_are_the_boundary_minus_a_half()
    test_public_definition_discloses_predicate_and_measured_limitation()
    print("multiplicity inset boundary-source tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
