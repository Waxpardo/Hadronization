#!/usr/bin/env python3
"""Hand-computed anchors for the UNCERTAINTY_MATRIX class-parsing rule."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extraction"))

from harvest_class_axis import (  # noqa: E402
    agrees_at_recorded_precision, assert_resolved_campaign, class_order,
    parse_bin, parse_log, percentile, resolved_campaigns,
    significant_figures,
)


def test_percentile() -> None:
    # `p` is the decimal point: 88p197 is 88.197, and 100 stays 100.0.
    assert percentile("88p197") == 88.197
    assert percentile("8p422") == 8.422
    assert percentile("100") == 100.0
    assert percentile("0") == 0.0


def test_parse_bin() -> None:
    assert parse_bin("hDPhiM90_100") == ("c1", 90.0, 100.0)
    assert parse_bin("hDPhiM0_1") == ("c11", 0.0, 1.0)
    assert parse_bin("hDPhiM1_10") == ("c10", 1.0, 10.0)
    # Archived pre-rebuild logs remain readable, but current configs do not
    # emit the legacy MONASH-MB spelling.
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
    text = "\n".join([
        "noise",
        "UNCERTAINTY_MATRIX flavour=BEAUTY trigger=Bp tune=MONASH associate=Bm "
        "bin=hDPhic1_MB88p197_100 central_yield=0.5 yield_sem=0.01",
        "UNCERTAINTY_MATRIX flavour=BEAUTY trigger=Bp tune=MONASH associate=Bm "
        "bin=hDPhiM00_100 central_yield=0.6 yield_sem=0.02",
    ])
    rows = parse_log(text)
    assert len(rows) == 2, rows
    assert rows[("BEAUTY", "Bp", "MONASH", "Bm", "c1")]["central_yield"] == "0.5"
    assert rows[("BEAUTY", "Bp", "MONASH", "Bm", "MB")]["mb_high"] == 100.0
    dup = text + "\n" + text.splitlines()[1]
    try:
        parse_log(dup)
    except ValueError:
        pass
    else:
        raise AssertionError("a duplicate identity must fail closed")


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
Beauty central resolver MONASH: base=/data/alice/ipardoza/hadronization_merged, tag=complete_root_HF_RUN3_V1
Beauty subsample resolver MONASH: base=/data/alice/ipardoza/hadronization_merged/SUBSAMPLES_HF_RUN3_V1/combined_root_subSamples
Charm central resolver MONASH: base=/data/alice/ipardoza/hadronization_merged, tag=complete_root_HF_RUN3_V1
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

    The window is a TOP percentile. c1 is the 90-100% lowest-activity class and
    c11 is the 0-1% highest-activity class. Absolute N_ch thresholds are
    tune-dependent and therefore are not part of this static contract test.
    """
    contract = json.loads(
        (ROOT / "config/multiplicity_percentile_classes_v2.json").read_text())
    _, c1_low, c1_high = parse_bin("hDPhiM90_100")
    _, c11_low, c11_high = parse_bin("hDPhiM0_1")

    assert c1_low > c11_high, (c1_low, c1_high, c11_low, c11_high)
    assert [row["class"] for row in contract["classes"]] == [
        f"c{i}" for i in range(1, 12)]
    assert class_order("c1") < class_order("c11")


def main() -> int:
    tests = [v for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"class axis: {len(tests)} hand-anchored checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
