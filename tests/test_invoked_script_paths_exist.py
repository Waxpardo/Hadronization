"""Require the extraction pipeline callee to be portable and fail closed."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "extraction" / "pipeline" / "tune_chain.sh"

def test_the_chain_has_no_site_specific_callee() -> None:
    text = CHAIN.read_text()
    assert "/data/" not in text, "tune_chain.sh contains a site-specific path"
    assert "HADRONIZATION_TUNE_EXTRACT" in text
    assert "${CHECKOUT}/extraction/pipeline/tune_extract.sh" in text


def test_the_chain_asserts_its_callee_exists_before_it_runs() -> None:
    text = CHAIN.read_text()
    assert "TUNE_CHAIN_MISSING_CALLEE" in text, \
        "the assertion does not name the missing path"
    assert "TUNE_CHAIN_REFUSED" in text, \
        "the assertion does not refuse; it must exit non-zero"
    assert '[[ ! -f "${TUNE_EXTRACT}" ]]' in text
    assert "exit 3" in text


def test_the_assertion_runs_before_any_stage() -> None:
    """A guard that runs after the work it protects is not a guard."""
    text = CHAIN.read_text()
    call = text.index('[[ ! -f "${TUNE_EXTRACT}" ]]')
    first_stage = min(
        text.index(marker) for marker in ("=== CLOSURE", "=== EXTRACTION")
        if marker in text
    )
    assert call < first_stage, \
        "the path assertion is invoked after a pipeline stage has started"


def main() -> int:
    test_the_chain_has_no_site_specific_callee()
    test_the_chain_asserts_its_callee_exists_before_it_runs()
    test_the_assertion_runs_before_any_stage()
    print("invoked-script-path tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
