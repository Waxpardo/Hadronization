#!/usr/bin/env python3
"""Strict CONTROL mode states the shape the control comparison must have.

The default comparator answers "did the rows we happened to share agree?".
That is the right question for an integrity check over archived logs and the
wrong one for the control that licenses the published arithmetic: a nominal of
144 rows and a control of 132 sharing ONE row satisfy it. Strict mode answers
"is this the 144/132 reproduction the analysis is defined on?" and refuses
anything else by name.

Each case below is a shape that reached the numerical-source boundary at the
pin. The seen-to-fail direction is asserted too: for the shapes the default
comparator ACCEPTS, this driver asserts that it accepts them, so the test fails
if the defect is ever reintroduced under a different name.

The assertions are on the refusal TYPE and on the CLI exit code, never on
message text.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "strict_control"

sys.path.insert(0, str(ROOT / "extraction"))
import harvest_class_report as report  # noqa: E402
from harvest_class_axis import parse_log  # noqa: E402

NOMINAL = FIXTURES / "nominal_144.log"
CONTROL = FIXTURES / "control_132.log"

# The four-associate pair set the 144/132 shape belongs to, pinned beside the
# fixture logs. Ruling R40 gave the BALANCING FIGURE configurations a second
# trigger group and the legacy associate set; the closure configuration stays on
# the base four series, because the shape it certifies is the accepted J-c1.1
# control's (see CLOSURE_ASSOCIATE_SET in tools/make_variant_configs.py). Tracked
# and pinned therefore derive the same twelve identities today, and
# `test_the_tracked_configuration_derives_the_same_shape` asserts exactly that.
# The fixture stays a separate file anyway: strict mode takes whichever
# configuration it is given, and these crafted logs must keep meaning what they
# meant when they were written even if the tracked pair set is revisited.
PINNED_CONFIG = (ROOT / "tests" / "fixtures" / "vintegrated_closure"
                 / "closure_config_12keys.json")
STRICT_CONFIG = ["--strict-config", str(PINNED_CONFIG)]


class Devnull:
    def write(self, _text: str) -> int:
        return 0


def run_cli(*argv: str) -> int:
    """The tool's own entry point, with a scratch output path."""
    with tempfile.TemporaryDirectory() as scratch:
        saved, sys.argv = sys.argv, ["harvest_class_report.py", *argv,
                                     "--out", str(Path(scratch) / "out.json")]
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = Devnull()
        try:
            return report.main()
        except SystemExit as exit_code:      # argparse
            return int(exit_code.code or 0)
        except Exception:                    # a named refusal propagates
            return 1
        finally:
            sys.argv = saved
            sys.stdout, sys.stderr = stdout, stderr


def refuses(expected: type, *argv: str) -> None:
    """The named arguments raise `expected`, and the CLI exits non-zero."""
    saved, sys.argv = sys.argv, ["harvest_class_report.py", *argv]
    raised = None
    with tempfile.TemporaryDirectory() as scratch:
        sys.argv = sys.argv + ["--out", str(Path(scratch) / "out.json")]
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = Devnull()
        try:
            report.main()
        except Exception as error:
            raised = error
        finally:
            sys.argv = saved
            sys.stdout, sys.stderr = stdout, stderr
    assert isinstance(raised, expected), (
        f"expected {expected.__name__}, got {type(raised).__name__}")
    assert run_cli(*argv) != 0, "the CLI exited zero on a refused input"


def test_the_strict_shape_is_derived_and_is_the_recorded_144_132() -> None:
    """The identity set is named; the counts follow from it and the contract.

    Deriving rather than hard-coding is what keeps the expectation true when the
    configuration's pair set changes. At the pin the derivation reproduces the
    recorded shape exactly, so both facts are asserted together.
    """
    shape = report.strict_control_shape(PINNED_CONFIG)
    assert len(shape["identities"]) == 12, sorted(shape["identities"])
    assert shape["classes"] == 11
    assert shape["nominal_rows"] == 144
    assert shape["control_rows"] == 132
    assert shape["shared_rows"] == 132
    assert len(shape["only_in_nominal"]) == 12
    assert all(identity[-1] == "MB" for identity in shape["only_in_nominal"])
    assert shape["identities"] == {
        (flavour, trigger, tune, associate)
        for tune in ("MONASH", "JUNCTIONS", "CLOSEPACKING")
        for flavour, trigger, associate in (
            ("BEAUTY", "B^{+}", "B-"),
            ("BEAUTY", "B^{+}", "Lambda_b"),
            ("CHARM", "D^{+}", "D-"),
            ("CHARM", "D^{+}", "Lambda_c(+)-bar"),
        )
    }


def test_a_correct_pair_passes_in_both_modes() -> None:
    """144 against 132, every shared row reproducing."""
    assert run_cli("--nominal", str(NOMINAL), "--control", str(CONTROL)) == 0
    assert run_cli("--nominal", str(NOMINAL), "--control", str(CONTROL),
                   "--strict-control", *STRICT_CONFIG) == 0


def test_one_shared_row_is_accepted_by_default_and_refused_by_strict() -> None:
    """Round-1 finding 3, measured in round 2 as `144v132_only_one_shared`."""
    one_shared = FIXTURES / "control_one_shared_row.log"
    assert run_cli("--nominal", str(NOMINAL), "--control", str(one_shared)) == 0
    refuses(report.StrictControlRefusal,
            "--nominal", str(NOMINAL), "--control", str(one_shared),
            "--strict-control", *STRICT_CONFIG)


def test_a_thirteenth_identity_is_refused() -> None:
    """An identity the closure configuration does not register.

    `only_in_nominal` is compared as a SET, so an intruder cannot be absorbed by
    a count that still comes out right.
    """
    refuses(report.StrictControlRefusal,
            "--nominal", str(FIXTURES / "nominal_thirteenth_identity.log"),
            "--control", str(CONTROL), "--strict-control", *STRICT_CONFIG)


def test_the_tracked_configuration_derives_the_same_shape() -> None:
    """The TRACKED closure configuration derives 12 identities and 144/132/132.

    Ruling R40 gave the balancing FIGURE configurations a second trigger group
    and the legacy associate set. It does not reach the closure configuration:
    the closure and CONTROL instruments answer to the accepted J-c1.1 log, which
    carries 132 rows over these twelve identities, so widening them would assert
    a shape no accepted log has (architect ledger #11; the design rationale is
    recorded at CLOSURE_ASSOCIATE_SET in tools/make_variant_configs.py).

    Asserted on the TRACKED file, not on PINNED_CONFIG, so a builder change that
    let R40 reach the closure again fails here rather than at RUN-N's boundary.
    The identity SET is compared as well as the counts: twelve wrong identities
    also count to twelve.
    """
    shape = report.strict_control_shape()
    pinned = report.strict_control_shape(PINNED_CONFIG)
    assert len(shape["identities"]) == 12, sorted(shape["identities"])
    assert shape["nominal_rows"] == 144
    assert shape["control_rows"] == 132
    assert shape["shared_rows"] == 132
    assert len(shape["only_in_nominal"]) == 12
    assert shape["identities"] == pinned["identities"], sorted(
        shape["identities"] ^ pinned["identities"])


def test_a_two_block_pair_is_accepted_by_default_and_refused_by_strict() -> None:
    """DA1-030. The shared parser admits `block_count >= 2`.

    The pair agrees on every shared row and the SEM is correctly recomputed from
    two values, so nothing about the arithmetic is malformed: the admission
    condition is. Ruling R39 fixes ten blocks with SEM on dof 9.
    """
    nominal = FIXTURES / "nominal_two_blocks.log"
    control = FIXTURES / "control_two_blocks.log"
    assert run_cli("--nominal", str(nominal), "--control", str(control)) == 0
    refuses(report.StrictControlRefusal,
            "--nominal", str(nominal), "--control", str(control),
            "--strict-control", *STRICT_CONFIG)


def test_the_generic_two_block_parser_still_accepts_two_blocks() -> None:
    """The `>= 2` helper stays for explicitly non-publication utilities.

    Strict mode is the boundary; widening the shared parser would refuse the
    archived logs it exists to read.
    """
    rows = parse_log((FIXTURES / "nominal_two_blocks.log").read_text())
    assert {row["block_count"] for row in rows.values()} == {2}


def test_a_variation_that_resolved_another_campaign_is_refused() -> None:
    """DA1-031. The configuration is a request; the resolver line is the answer."""
    wrong = FIXTURES / "variation_wrong_resolver.log"
    assert run_cli("--nominal", str(NOMINAL), "--control", str(CONTROL),
                   "--variation", f"HF_SYS_MUR_UP={wrong}") == 0
    refuses(ValueError,
            "--nominal", str(NOMINAL), "--control", str(CONTROL),
            "--variation", f"HF_SYS_MUR_UP={wrong}", "--strict-control", *STRICT_CONFIG)


def test_a_variation_that_resolved_its_own_campaign_passes() -> None:
    """The resolver assertion is a boundary, not a blanket refusal."""
    right = FIXTURES / "variation_right_resolver.log"
    assert run_cli("--nominal", str(NOMINAL), "--control", str(CONTROL),
                   "--variation", f"HF_SYS_MUR_UP={right}",
                   "--strict-control", *STRICT_CONFIG) == 0


def test_the_default_comparator_is_unchanged_for_existing_callers() -> None:
    """`compare_rows` keeps its two-argument shape.

    extraction/write_verdict.py imports it, and that module is inside the paused
    systematics boundary (ruling R31), so its caller must not move.
    """
    nominal = parse_log(NOMINAL.read_text())
    control = parse_log(CONTROL.read_text(), validate_block_contract=False)
    comparison = report.compare_rows(nominal, control)
    assert comparison["agree"] is True
    assert comparison["shared_rows"] == 132
    assert json.dumps(comparison, sort_keys=True)   # stays serialisable


def main() -> int:
    test_the_strict_shape_is_derived_and_is_the_recorded_144_132()
    test_a_correct_pair_passes_in_both_modes()
    test_one_shared_row_is_accepted_by_default_and_refused_by_strict()
    test_a_thirteenth_identity_is_refused()
    test_the_tracked_configuration_derives_the_same_shape()
    test_a_two_block_pair_is_accepted_by_default_and_refused_by_strict()
    test_the_generic_two_block_parser_still_accepts_two_blocks()
    test_a_variation_that_resolved_another_campaign_is_refused()
    test_a_variation_that_resolved_its_own_campaign_passes()
    test_the_default_comparator_is_unchanged_for_existing_callers()
    print("strict CONTROL boundary: 144/132 derived, five shapes refused")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
