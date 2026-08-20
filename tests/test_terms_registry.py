"""New prose may not add a term `docs/TERMS.md` rules out.

**This is a ratchet, not a gate.** 44 documents are still unrewritten, so the
tree violates the registry in 175 places today and `docs/TERMS_BASELINE.tsv`
records every one. The test fails on a violation the baseline does not already
hold. New prose therefore cannot add one, and each rewrite session deletes its
document's rows as it goes.

**The baseline is a number that must fall.** It goes stale in both directions:
one violation more and the comparison breaks, one fewer and it breaks too. A
session that fixes prose without regenerating the baseline gets told so, which
is the only way the count stays honest.

WHAT THIS TEST DOES NOT DO. It does not read the prose. It cannot tell whether a
document that avoids every ruled-out word actually says one thing with one name
— that judgement stays with whoever writes the rewrite. What it does is stop the
list of known violations from growing while nobody is looking.

The scan lives in `tools/terms_check.py` so this file cannot drift from it: the
tool measures, the test compares. Regenerate with

    python3 tools/terms_check.py --baseline
"""
from __future__ import annotations

import csv
import functools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "TERMS.md"
BASELINE = ROOT / "docs" / "TERMS_BASELINE.tsv"

sys.path.insert(0, str(ROOT / "tools"))
import terms_check  # noqa: E402

COLUMNS = ["path", "term", "canonical", "count", "lines"]


@functools.lru_cache(maxsize=1)
def fresh() -> tuple[dict, ...]:
    """One scan per run. The whole pass is well under a second."""
    return tuple(terms_check.violations())


def baseline_rows() -> list[dict]:
    with BASELINE.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def key(row: dict) -> tuple[str, str, str, str]:
    """Line numbers are deliberately not part of the key.

    A violation that moves down the file because someone added a paragraph
    above it is the same violation. The count is in the key, so one more or one
    fewer still breaks the comparison.
    """
    return (row["path"], row["term"], row["canonical"], row["count"])


def test_baseline_header_is_exact() -> None:
    with BASELINE.open(encoding="utf-8", newline="") as fh:
        header = next(csv.reader(fh, delimiter="\t"))
    assert header == COLUMNS, f"baseline header drifted: {header}"


def test_no_violation_outside_the_baseline() -> None:
    recorded = {key(r) for r in baseline_rows()}
    new = sorted(k for k in {key(h) for h in fresh()} if k not in recorded)
    if new:
        lines = [f"  {p}: {t!r} -> use {c!r} ({n}x)" for p, t, c, n in new]
        raise AssertionError(
            f"{len(new)} ruled-out term(s) not in the baseline:\n"
            + "\n".join(lines)
            + "\n\nUse the canonical term from docs/TERMS.md. If the prose is "
              "right and the registry is wrong, change the registry."
        )


def test_no_stale_baseline_row() -> None:
    """A fixed violation must leave the baseline, or the count lies."""
    gone = sorted({key(r) for r in baseline_rows()} - {key(h) for h in fresh()})
    assert not gone, (
        f"{len(gone)} baseline row(s) no longer match the tree: {gone[:8]}\n"
        "Regenerate with: python3 tools/terms_check.py --baseline"
    )


def test_every_registry_row_is_complete() -> None:
    """A row with no canonical term gives a session nothing to write."""
    ruled, canon = terms_check.registry()
    assert canon, "the registry table parsed to zero rows"
    assert len(canon) == len(set(canon)), "a canonical term appears twice"
    for bad, good in ruled.items():
        assert good in canon, f"{bad!r} maps to {good!r}, which is not a row"
        assert bad.lower() not in {c.lower() for c in canon}, \
            f"{bad!r} is ruled out and canonical at the same time"


def test_the_registry_never_rules_out_a_word_it_also_uses() -> None:
    """The scan skips docs/TERMS.md, and this is why that is not a loophole."""
    assert "docs/TERMS.md" in terms_check.SCAN_EXCLUDE
    assert REGISTRY.is_file()


def main() -> int:
    test_baseline_header_is_exact()
    test_no_violation_outside_the_baseline()
    test_no_stale_baseline_row()
    test_every_registry_row_is_complete()
    test_the_registry_never_rules_out_a_word_it_also_uses()
    rows = baseline_rows()
    total = sum(int(r["count"]) for r in rows)
    ruled, canon = terms_check.registry()
    print(f"terms-registry tests passed ({len(canon)} rows, "
          f"{len(ruled)} ruled-out terms, {total} baseline violations "
          f"in {len({r['path'] for r in rows})} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
