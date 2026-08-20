"""Every absolute script the pipeline drivers invoke must exist.

`docs/NIKHEF_CLEANUP_PLAN.md` §5.1 recorded the defect this closes: the
2026-08-17 consolidation moved `tune_extract.sh` into
`hadronization/scratch/deploys/`, updated the translation table, and left the
caller alone. `extraction/pipeline/tune_chain.sh` then named a path that was not
there.

**Why a missing callee is worse than a crash here.** The chain invokes it as
`bash <path> ... >> "$LOG" 2>&1`. A missing file writes one line into a log
nobody reads, `$?` is captured into a comment, and the chain prints
TUNE_CHAIN_DONE. The extraction step "ran" and produced nothing.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "extraction" / "pipeline" / "tune_chain.sh"

# Paths under /data/alice are on the cluster, not in the checkout. What this
# test can assert from here is that the caller names the CONSOLIDATED location
# rather than the pre-consolidation one, and that the guard which checks
# existence at run time is still in the script.
MOVED_AWAY = "/data/alice/ipardoza/tune_extract.sh"
CONSOLIDATED = "/data/alice/ipardoza/hadronization/scratch/deploys/tune_extract.sh"


def invoked_absolute_paths(script: Path) -> list[str]:
    return re.findall(r"^\s*bash\s+(/\S+)", script.read_text(), re.M)


def test_the_chain_names_the_consolidated_path() -> None:
    paths = invoked_absolute_paths(CHAIN)
    assert paths, "no absolute `bash <path>` invocation found in tune_chain.sh"
    assert CONSOLIDATED in paths, f"tune_chain.sh does not call {CONSOLIDATED}: {paths}"


def test_the_chain_no_longer_names_the_pre_consolidation_path() -> None:
    """The mutation guard. Reverting the path must fail this test."""
    text = CHAIN.read_text()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("bash ") and MOVED_AWAY in stripped:
            raise AssertionError(
                f"tune_chain.sh still invokes the moved path: {stripped}"
            )


def test_the_chain_asserts_its_callees_exist_before_it_runs() -> None:
    """A correct path today is not a guard against the next move.

    §11.1 specifies the test as `assert that every absolute path tune_chain.sh
    invokes exists`. The chain now does that itself, at start, so the next
    consolidation that moves a callee stops the chain instead of emptying it.
    """
    text = CHAIN.read_text()
    assert "assert_invoked_paths_exist" in text, \
        "tune_chain.sh has no path-existence assertion"
    assert "TUNE_CHAIN_MISSING_CALLEE" in text, \
        "the assertion does not name the missing path"
    assert "TUNE_CHAIN_REFUSED" in text, \
        "the assertion does not refuse; it must exit non-zero"
    body = text.split("assert_invoked_paths_exist()", 1)[1]
    assert "exit 3" in body.split("\n}", 1)[0], \
        "the assertion warns but does not stop the chain"


def test_the_assertion_runs_before_any_stage() -> None:
    """A guard that runs after the work it protects is not a guard."""
    text = CHAIN.read_text()
    call = text.index("\nassert_invoked_paths_exist\n")
    first_stage = min(
        text.index(marker) for marker in ("=== CLOSURE", "=== EXTRACTION")
        if marker in text
    )
    assert call < first_stage, \
        "the path assertion is invoked after a pipeline stage has started"


def main() -> int:
    test_the_chain_names_the_consolidated_path()
    test_the_chain_no_longer_names_the_pre_consolidation_path()
    test_the_chain_asserts_its_callees_exist_before_it_runs()
    test_the_assertion_runs_before_any_stage()
    print("invoked-script-path tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
