#!/usr/bin/env python3
"""Hand-computed anchors for the UNCERTAINTY_MATRIX class-parsing rule."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/multiplicity_percentile_classes_v2.json"
sys.path.insert(0, str(ROOT / "extraction"))

from harvest_class_axis import (  # noqa: E402
    agrees_at_recorded_precision, assert_resolved_campaign, class_order,
    parse_bin, parse_log, percentile, resolved_campaigns, sample_sem,
    significant_figures,
)


def vector(values: list[float]) -> str:
    return ",".join(format(value, ".17g") for value in values)


def current_rows() -> list[str]:
    reference = [1.0, 2.0, 4.0, 8.0]
    numerator = [2.0, 6.0, 8.0, 24.0]
    ratios = [value / denominator
              for value, denominator in zip(numerator, reference)]
    common = (
        "schema=hadronization_uncertainty_matrix_v2 block_count=4 "
        "flavour=BEAUTY trigger=Bp tune=MONASH bin=hDPhiM90_100 ")
    return [
        "UNCERTAINTY_MATRIX " + common
        + "associate=Bm is_reference=true "
        + f"block_yields={vector(reference)} block_ratios=NA "
        + f"yield_sem={sample_sem(reference):.17g} ratio_sem=NA",
        "UNCERTAINTY_MATRIX " + common
        + "associate=Lb is_reference=false "
        + f"block_yields={vector(numerator)} block_ratios={vector(ratios)} "
        + f"yield_sem={sample_sem(numerator):.17g} "
        + f"ratio_sem={sample_sem(ratios):.17g}",
    ]


def test_percentile() -> None:
    # `p` is the decimal point: 88p197 is 88.197, and 100 stays 100.0.
    assert percentile("88p197") == 88.197
    assert percentile("8p422") == 8.422
    assert percentile("100") == 100.0
    assert percentile("0") == 0.0


def test_parse_bin() -> None:
    # Ruling R10: the current-axis anchors come from the contract. A second
    # copy of the class set here would have to be edited alongside it.
    for row in json.loads(CONTRACT.read_text())["classes"]:
        assert parse_bin("hDPhi" + row["bin"]) == (
            row["class"], row["percentile_min"], row["percentile_max"])
    # Archived pre-rebuild logs remain readable, but current configs do not
    # emit the legacy MONASH-MB spelling. Those names carry the RETIRED
    # absolute axis and stay literal: they are historical data, not this
    # repository's class set.
    assert parse_bin("hDPhic1_MB88p197_100") == ("c1", 88.197, 100.0)
    assert parse_bin("hDPhic11_MB0_8p422") == ("c11", 0.0, 8.422)
    assert parse_bin("hDPhic10_MB8p422_17p124") == ("c10", 8.422, 17.124)
    assert parse_bin("hDPhiM00_100") == ("MB", 0.0, 100.0)
    for bad in ("hDPhi", "hDPhic1", "hDPhiX1_MB0_1", "", "c1_MB0_1"):
        try:
            parse_bin(bad)
        except ValueError:
            continue
        raise AssertionError(f"{bad!r} must not parse")


def test_class_order() -> None:
    # String order puts c10 and c11 before c2; the rule must not.
    names = ["c10", "c2", "c1", "MB", "c11"]
    assert sorted(names, key=class_order) == ["c1", "c2", "c10", "c11", "MB"]


def test_parse_log() -> None:
    text = "\n".join(["noise", *current_rows()])
    rows = parse_log(text)
    assert len(rows) == 2, rows
    reference = rows[("BEAUTY", "Bp", "MONASH", "Bm", "c1")]
    assert reference["block_count"] == 4
    assert reference["block_yields"] == [1.0, 2.0, 4.0, 8.0]
    assert reference["block_ratios"] is None
    assert rows[("BEAUTY", "Bp", "MONASH", "Lb", "c1")][
        "block_ratios"] == [2.0, 3.0, 2.0, 3.0]
    dup = text + "\n" + current_rows()[0]
    try:
        parse_log(dup)
    except ValueError:
        pass
    else:
        raise AssertionError("a duplicate identity must fail closed")


def test_archived_log_requires_an_explicit_noncurrent_opt_out() -> None:
    archived = (
        "UNCERTAINTY_MATRIX flavour=BEAUTY trigger=Bp tune=MONASH "
        "associate=Bm bin=hDPhic1_MB88p197_100 central_yield=0.5 "
        "yield_sem=0.01")
    try:
        parse_log(archived)
    except ValueError as error:
        assert "MONASH/c1 schema" in str(error), error
    else:
        raise AssertionError("an old log silently passed the current contract")
    legacy = parse_log(archived, validate_block_contract=False)
    assert legacy[("BEAUTY", "Bp", "MONASH", "Bm", "c1")][
        "central_yield"] == "0.5"


def test_mis_sized_vector_names_tune_class_and_field() -> None:
    lines = current_rows()
    lines[1] = lines[1].replace(
        "block_ratios=2,3,2,3", "block_ratios=2,3,2")
    try:
        parse_log("\n".join(lines))
    except ValueError as error:
        message = str(error)
        assert "MONASH/c1" in message, message
        assert "block_ratios" in message, message
        assert "expected 4 elements, got 3" in message, message
        return
    raise AssertionError("a removed block element passed the vector contract")


def test_nonreference_vectors_fail_closed_on_na_malformed_and_nonfinite() -> None:
    for replacement, reason in (
            ("NA", "NA is forbidden"),
            ("2,3,broken,3", "malformed numeric vector"),
            ("2,3,nan,3", "non-finite value")):
        lines = current_rows()
        lines[1] = lines[1].replace(
            "block_ratios=2,3,2,3", f"block_ratios={replacement}")
        try:
            parse_log("\n".join(lines))
        except ValueError as error:
            message = str(error)
            assert "MONASH/c1 block_ratios" in message, message
            assert reason in message, message
            continue
        raise AssertionError(
            f"non-reference block_ratios={replacement!r} passed")


def test_same_block_ratio_is_reconstructed() -> None:
    lines = current_rows()
    changed = [2.5, 3.0, 2.0, 3.0]
    lines[1] = lines[1].replace(
        "block_ratios=2,3,2,3", f"block_ratios={vector(changed)}")
    old_sem = f"ratio_sem={sample_sem([2.0, 3.0, 2.0, 3.0]):.17g}"
    lines[1] = lines[1].replace(
        old_sem, f"ratio_sem={sample_sem(changed):.17g}")
    try:
        parse_log("\n".join(lines))
    except ValueError as error:
        assert "MONASH/c1 block_ratios: block 1" in str(error), error
        return
    raise AssertionError("a ratio not formed from its same-block yields passed")


def test_producer_contract_derives_the_accepted_11_by_10_shape() -> None:
    class_contract = json.loads(CONTRACT.read_text())
    plot_config = json.loads((
        ROOT / "plotting/configuration_multiplicity_HF_RUN3_V1_"
               "THREETUNE_THnSparse_complete_root.json").read_text())
    producer = (ROOT / "plotting/improvedPlotting_THnSparse.C").read_text()
    assert len(class_contract["classes"]) == 11
    assert plot_config["nSubSamples"] == 10
    assert 'block_count=" << nSubSamples' in producer
    assert 'FormatBlockVector17(subYieldValues)' in producer
    assert 'FormatBlockVector17(subRatioValues)' in producer
    assert 'std::setprecision(17)' in producer


def test_significant_figures() -> None:
    # 0.106397 records 6; the leading zeros before the first non-zero digit
    # are not significant. 9.35056e-05 records 6, not 8.
    assert significant_figures("0.106397") == 6
    assert significant_figures("9.35056e-05") == 6
    assert significant_figures("0.10639730639730641") == 17
    assert significant_figures("0.000531587") == 6
    assert significant_figures("0") == 1


def test_agrees_at_recorded_precision() -> None:
    # The real case: a 6-figure log against a 17-figure one, same number.
    assert agrees_at_recorded_precision("0.106397", "0.10639730639730641")
    assert agrees_at_recorded_precision("0.0016767", "0.0016767013662127941")
    # A real disagreement at the recorded precision still fails.
    assert not agrees_at_recorded_precision("0.106397", "0.106398")
    assert not agrees_at_recorded_precision("0.106397", "0.10650")
    # But a genuinely less precise value that ROUNDS to the same digits agrees,
    # and that is the point: 0.10640 records 5 figures, and at 5 figures
    # 0.106397 is 0.1064 too. Comparing beyond a log's precision would invent
    # a disagreement the log cannot support.
    assert agrees_at_recorded_precision("0.106397", "0.10640")
    # Identical strings agree without any rounding.
    assert agrees_at_recorded_precision("NA", "NA")


CENTRAL_LOG = """
    config: plotting/harvest_configs/configuration_multiplicity_HF_SYS_MUR_UP_x.json
Beauty central resolver MONASH: base=${HADRONIZATION_MERGED_ROOT}, tag=complete_root_HF_RUN3_V1
Beauty subsample resolver MONASH: base=${HADRONIZATION_MERGED_ROOT}/SUBSAMPLES_HF_RUN3_V1/combined_root_subSamples
Charm central resolver MONASH: base=${HADRONIZATION_MERGED_ROOT}, tag=complete_root_HF_RUN3_V1
"""

VARIATION_LOG = CENTRAL_LOG.replace("HF_RUN3_V1", "HF_SYS_MUR_UP")


def test_resolved_campaigns() -> None:
    found = resolved_campaigns(CENTRAL_LOG)
    assert found["central"] == {"HF_RUN3_V1"}, found
    assert found["subsample"] == {"HF_RUN3_V1"}, found


def test_resolver_assertion_accepts_the_right_campaign() -> None:
    found = assert_resolved_campaign(VARIATION_LOG, "HF_SYS_MUR_UP")
    assert found["central"] == {"HF_SYS_MUR_UP"}, found


def test_resolver_assertion_catches_the_2026_08_19_defect() -> None:
    """THE MUTATION. A log naming the wrong campaign must fail.

    This is the real log from that day: the configuration asked for
    HF_SYS_MUR_UP and the resolver answered HF_RUN3_V1.
    """
    try:
        assert_resolved_campaign(CENTRAL_LOG, "HF_SYS_MUR_UP")
    except ValueError as error:
        assert "RESOLVER ASSERTION FAILED" in str(error), error
        assert "HF_RUN3_V1" in str(error), error
        return
    raise AssertionError(
        "MUTATION SURVIVED: a render that read the central campaign passed an "
        "assertion asking for a variation")


def test_resolver_assertion_fails_closed_on_a_silent_log() -> None:
    try:
        assert_resolved_campaign("no resolver lines here\n", "HF_SYS_MUR_UP")
    except ValueError as error:
        assert "no resolver line" in str(error), error
        return
    raise AssertionError("a log that cannot answer must not count as an answer")


def test_the_percentile_axis_runs_opposite_to_the_multiplicity_axis() -> None:
    """A high percentile is a LOW N_ch, and the label invites the opposite read.

    The window is a TOP percentile. The first contract class is the
    lowest-activity one and the last is the highest. Absolute N_ch thresholds
    are tune-dependent and therefore are not part of this static contract test.
    """
    contract = json.loads(CONTRACT.read_text())
    rows = contract["classes"]
    # Ruling R10: the first and last class come from the contract, so this
    # check follows any class set rather than one written down here.
    _, c1_low, c1_high = parse_bin("hDPhi" + rows[0]["bin"])
    _, top_low, top_high = parse_bin("hDPhi" + rows[-1]["bin"])

    assert c1_low > top_high, (c1_low, c1_high, top_low, top_high)
    names = [row["class"] for row in contract["classes"]]
    assert names == [f"c{i}" for i in range(1, len(names) + 1)], names
    assert class_order(rows[0]["class"]) < class_order(rows[-1]["class"])


def main() -> int:
    tests = [v for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"class axis: {len(tests)} hand-anchored checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
