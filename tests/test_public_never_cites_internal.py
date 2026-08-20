"""No PUBLIC file may name an INTERNAL path unless the ledger records it.

**This is the export's central promise, and before this test nothing measured
it.** The export builds a new repository from the PUBLIC rows alone. A PUBLIC
file that names an INTERNAL one sends its reader to a path the export does not
contain -- and the worse case is not the missing file. It is a live document
citing a superseded number by reference. The reader sees a citation, finds
nothing to check it against, and never learns that the audit excluded the cited
document because its numbers no longer hold.

WHAT A PASS MEANS, AND WHAT IT DOES NOT. A pass does not say the tree is
clean. It says the ledger WRITES DOWN every such reference, in
`docs/REPO_AUDIT_CITATIONS.tsv`, and that the manifest marks every file
carrying one `voice: needs-rewrite`. That is the remedy the audit records:
the rewrite is a later phase, and this test makes the debt exact rather than
approximate so the rewrite has a list to work from.

**The test does not soften on a needs-rewrite file.** A new reference in a file
that already has recorded ones still fails, because the ledger keys on
(citing, cited, token) with an exact count. One more reference raises the count and breaks
the comparison; one fewer lowers it and breaks the comparison too. So a ledger
cannot rot into a permanent excuse: it goes stale the moment the tree stops
matching it, either way.

THE THREE FAILURES THIS RAISES, each a different defect:

  * an UNRECORDED reference -- a PUBLIC file gained a citation to an INTERNAL
    path, or a file's class changed and dragged one in with it;
  * a STALE ledger row -- the reference is gone and the ledger still claims it,
    which would let a later real reference hide inside a stale count;
  * a citing file marked `voice: clean` -- the manifest contradicts itself,
    because a file that cites excluded content is not clean by definition.

The scan lives in `tools/repo_audit.py` so this file cannot drift from it: the
tool measures, the test compares. Regenerate with

    python3 tools/repo_audit.py --citations
"""
from __future__ import annotations

import csv
import functools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "REPO_AUDIT.csv"
LEDGER = ROOT / "docs" / "REPO_AUDIT_CITATIONS.tsv"

sys.path.insert(0, str(ROOT / "tools"))
import repo_audit  # noqa: E402

LEDGER_COLUMNS = ["citing", "cited", "token", "count", "lines"]


@functools.lru_cache(maxsize=1)
def manifest_rows() -> tuple[dict, ...]:
    with MANIFEST.open(encoding="utf-8", newline="") as fh:
        return tuple(csv.DictReader(fh))


@functools.lru_cache(maxsize=1)
def fresh_hits() -> tuple[dict, ...]:
    """One scan per run.

    The scan reads every PUBLIC file and matches a 190-branch alternation
    against each line. Three of the checks below need it, and re-scanning per
    check took 44 seconds of a suite that runs 77 tests -- slow enough that
    someone eventually stops running it, which is the only way a contract test
    truly fails.
    """
    return tuple(repo_audit.citation_hits(list(manifest_rows())))


def ledger_rows() -> list[dict]:
    with LEDGER.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def key(row: dict) -> tuple[str, str, str, str]:
    """Line numbers are deliberately NOT part of the key.

    A reference that moves down the file because someone added a paragraph
    above it is the same reference, and this check says so: it reports a NEW or
    a REMOVED reference, not a moved one. The count IS in the key, so one more
    or one fewer still breaks the comparison.

    THE LEDGER IS STILL BYTE-EXACT, and the strictness lives elsewhere.
    `repo_audit.py --check` compares the whole file including the lines column,
    and `test_repo_audit_manifest.py` runs it. So a line shift does fail the
    suite -- it just fails there, with "regenerate", rather than here with
    "you added a reference". The split keeps this file's failure message true.
    """
    return (row["citing"], row["cited"], row["token"], row["count"])


def test_ledger_header_is_exact() -> None:
    with LEDGER.open(encoding="utf-8", newline="") as fh:
        header = next(csv.reader(fh, delimiter="\t"))
    assert header == LEDGER_COLUMNS, f"ledger header drifted: {header}"


def test_no_unrecorded_reference() -> None:
    fresh = {key(h): h for h in fresh_hits()}
    recorded = {key(r) for r in ledger_rows()}
    new = sorted(set(fresh) - recorded)
    if new:
        lines = [
            f"  {c} -> {t}  (as {tok!r}, {n}x, line(s) {fresh[(c, t, tok, n)]['lines']})"
            for c, t, tok, n in new
        ]
        raise AssertionError(
            f"{len(new)} PUBLIC-to-INTERNAL reference(s) are not in the ledger:\n"
            + "\n".join(lines)
            + "\n\nEither remove the reference, or reclass the file, or record it "
              "with: python3 tools/repo_audit.py --citations"
        )


def test_no_stale_ledger_row() -> None:
    fresh = {key(h) for h in fresh_hits()}
    gone = sorted({key(r) for r in ledger_rows()} - fresh)
    assert not gone, (
        f"{len(gone)} ledger row(s) no longer match the tree: {gone[:8]}\n"
        "Regenerate with: python3 tools/repo_audit.py --citations"
    )


def test_every_citing_file_is_marked_needs_rewrite() -> None:
    voice = {r["path"]: r["voice"] for r in manifest_rows()}
    bad = sorted({r["citing"] for r in ledger_rows()
                  if voice.get(r["citing"]) != "needs-rewrite"})
    assert not bad, (
        "the manifest contradicts itself -- these PUBLIC files cite an INTERNAL "
        f"path and are still marked voice=clean: {bad}"
    )


def test_the_ledger_never_lists_a_non_public_citer() -> None:
    """A guard on the scan, not on the tree.

    If a citing file is not PUBLIC, the ledger is recording a reference that
    does not matter, and the count it contributes would mask a real one.
    """
    cls = {r["path"]: r["class"] for r in manifest_rows()}
    wrong = sorted({r["citing"] for r in ledger_rows()
                    if cls.get(r["citing"]) != "PUBLIC"})
    assert not wrong, f"ledger lists non-PUBLIC citing file(s): {wrong}"


def main() -> int:
    test_ledger_header_is_exact()
    test_no_unrecorded_reference()
    test_no_stale_ledger_row()
    test_every_citing_file_is_marked_needs_rewrite()
    test_the_ledger_never_lists_a_non_public_citer()
    rows = ledger_rows()
    total = sum(int(r["count"]) for r in rows)
    print(f"public-cites-internal tests passed "
          f"({total} recorded reference(s) from {len({r['citing'] for r in rows})} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
