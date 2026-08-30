#!/usr/bin/env python3
"""The V-INTEGRATED closure gate refuses every log it cannot actually close.

The tool is the only assertion that the eleven multiplicity classes tile the
sample, and it is quoted as evidence for the integrated arm of every balancing
figure. Before the repairs recorded here it reported `EXACT` on six shapes it
had not checked, so this driver holds one case per shape.

The assertions are on the REFUSAL TYPE and the EXIT CODE, never on message
text: Python 3.10 and 3.11 word the same builtin exception differently, and a
test that pins wording fails on the interpreter rather than on the defect.

The fixture logs are written against a PINNED copy of the closure configuration
(tests/fixtures/vintegrated_closure/closure_config_12keys.json), not against the
tracked one. The tool derives its expected identity set from whichever
configuration it is given, so pinning the fixture's configuration keeps these
cases meaning what they meant when they were written while the tracked
configuration's pair set grows.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "vintegrated_closure"
CONFIG = FIXTURES / "closure_config_12keys.json"

sys.path.insert(0, str(ROOT / "tools"))
import vintegrated_closure as closure  # noqa: E402


class Devnull:
    def write(self, _text: str) -> int:
        return 0


def refuses(log_name: str) -> None:
    """The named log raises ClosureRefusal, and the CLI exits non-zero."""
    log = FIXTURES / log_name
    raised = False
    try:
        closure.run(log, CONFIG, closure.PAIR_REGISTRY, closure.CLASS_CONTRACT,
                    stream=Devnull())
    except closure.ClosureRefusal:
        raised = True
    assert raised, f"{log_name}: no ClosureRefusal was raised"

    stdout, stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = Devnull()
    try:
        code = closure.main([str(log), "--config", str(CONFIG)])
    finally:
        sys.stdout, sys.stderr = stdout, stderr
    assert code != 0, f"{log_name}: CLI exit code was {code}"


def test_the_expected_identity_set_is_derived_from_the_configuration() -> None:
    """Twelve identities, named -- three tunes times four configured associates.

    The reviewer's objection to a count was that eleven arbitrary bin names
    satisfy a count of eleven, so the identities are asserted as a set.
    """
    keys = closure.expected_keys(CONFIG, closure.PAIR_REGISTRY)
    assert keys == {
        (tune, flavour, trigger, associate, os_file)
        for tune in ("MONASH", "JUNCTIONS", "CLOSEPACKING")
        for flavour, trigger, associate, os_file in (
            ("BEAUTY", "B^{+}", "B-", "BplusBminus.root"),
            ("BEAUTY", "B^{+}", "Lambda_b", "BplusLb.root"),
            ("CHARM", "D^{+}", "D-", "DplusDminus.root"),
            ("CHARM", "D^{+}", "Lambda_c(+)-bar", "DplusLambdacplusbar.root"),
        )
    }, sorted(keys)


def test_the_expected_bin_set_comes_from_the_class_contract() -> None:
    """R10: the class set is read from the contract, never enumerated in code."""
    bins = closure.expected_bins(closure.CLASS_CONTRACT)
    assert closure.INTEGRATED_BIN in bins
    assert len(bins) == 12
    assert {"M90_100", "M0_1"} <= bins


def test_a_complete_log_closes() -> None:
    """Twelve identities times twelve bins, closing exactly."""
    checked = closure.run(FIXTURES / "positive_12keys_12bins.log", CONFIG,
                          closure.PAIR_REGISTRY, closure.CLASS_CONTRACT,
                          stream=Devnull())
    assert checked == 12, checked

    stdout = sys.stdout
    sys.stdout = Devnull()
    try:
        code = closure.main([str(FIXTURES / "positive_12keys_12bins.log"),
                             "--config", str(CONFIG)])
    finally:
        sys.stdout = stdout
    assert code == 0, code


def test_an_eleven_class_render_is_refused_and_never_raises_nameerror() -> None:
    """Ledger D3. The real render shape crashed on a leaked loop variable."""
    refuses("eleven_class_no_integrated.log")


def test_an_integrated_only_row_is_refused() -> None:
    """Ledger D4. `keys=0` printed EXACT and exited 0."""
    refuses("integrated_only_one_row.log")


def test_the_crafted_incomplete_identity_is_refused() -> None:
    """Reviewer crafted A: one complete identity carried the whole verdict."""
    refuses("crafted_complete_plus_incomplete.log")


def test_the_crafted_renamed_class_bin_is_refused() -> None:
    """Reviewer crafted B: eleven arbitrary bin names satisfied a count."""
    refuses("crafted_c11_renamed_junk.log")


def test_an_identity_short_of_the_integrated_bin_is_refused() -> None:
    """The crafted-A defect with the whole key set present.

    Both crafted logs above are short of identities, so the key-set refusal
    fires first and the per-identity bin check stays untested. This log carries
    all twelve identities and drops M00_100 from one, which is the shape the old
    tool skipped while still reporting EXACT.
    """
    refuses("full_set_one_identity_missing_integrated.log")


def test_an_identity_carrying_an_unregistered_bin_is_refused() -> None:
    """The crafted-B defect with the whole key set present."""
    refuses("full_set_one_bin_renamed_junk.log")


def test_a_duplicate_key_bin_row_is_refused() -> None:
    """Ledger DA1-017. The dictionary assignment took the last occurrence."""
    refuses("duplicate_key_bin.log")


def test_a_duplicate_that_hid_a_corrupt_row_is_refused() -> None:
    """Ledger DA1-017, the dangerous direction.

    With the corrupt repeat FIRST, last-wins kept the correct row: the old tool
    reported EXACT on a log carrying a corrupt duplicate. Order decided whether
    the corruption was visible, so the refusal is on the duplicate itself.
    """
    refuses("duplicate_key_bin_corrupt_first.log")


def test_half_integer_per_class_counts_are_refused() -> None:
    """Ledger DA1-016. +0.5 and -0.5 cancelled inside the sum."""
    refuses("half_integer_per_class.log")


def test_a_multi_row_log_with_no_integrated_bin_is_refused() -> None:
    """The no-integrated-bin path, on a shape smaller than a real render."""
    refuses("no_integrated_bin_multirow.log")


def main() -> int:
    test_the_expected_identity_set_is_derived_from_the_configuration()
    test_the_expected_bin_set_comes_from_the_class_contract()
    test_a_complete_log_closes()
    test_an_eleven_class_render_is_refused_and_never_raises_nameerror()
    test_an_integrated_only_row_is_refused()
    test_the_crafted_incomplete_identity_is_refused()
    test_the_crafted_renamed_class_bin_is_refused()
    test_an_identity_short_of_the_integrated_bin_is_refused()
    test_an_identity_carrying_an_unregistered_bin_is_refused()
    test_a_duplicate_key_bin_row_is_refused()
    test_a_duplicate_that_hid_a_corrupt_row_is_refused()
    test_half_integer_per_class_counts_are_refused()
    test_a_multi_row_log_with_no_integrated_bin_is_refused()
    print("V-INTEGRATED closure gate: 12x12 closes, ten crafted shapes refused")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
