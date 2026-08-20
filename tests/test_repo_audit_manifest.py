"""The publication audit manifest must cover every tracked path, exactly.

`docs/REPO_AUDIT.csv` decides what a future export publishes. Its failure mode
is not a wrong ruling -- a wrong ruling is one line to correct -- but a MISSING
ROW. Nothing reports a missing path as unclassified. It is absent, and the
reader of the manifest has no way to notice. The export then works from a list
that looks complete and is not.

So the completeness check is set equality against `git ls-files`, and it FAILS
CLOSED in both directions:

  * a tracked path with no row means the audit did not see a file;
  * a row with no tracked path means the manifest kept a stale ruling after a
    file moved or left the tree, which is how a name that no longer exists
    reaches the export as if it did.

`class=PENDING` is a VALID value and this test accepts it. The file carries
"unclassified" as a value rather than as a gap, which is what makes the audit
resumable. `test_every_row_carries_prose_once_classified`
covers the other half: once a row leaves PENDING it must say what and why.

The round-trip test exists because both prose columns contain commas, quotes
and em-dashes. A hand-rolled writer shifts a column, and a shifted column
silently changes a file's class. Only a read-back of the committed bytes with
the csv module proves that the file a human reads is the file the tool wrote.
"""
from __future__ import annotations

import csv
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "REPO_AUDIT.csv"

EXPECTED_HEADER = [
    "path", "class", "what", "why", "refs",
    "entrypoint", "voice", "dead", "grouped",
]
VALID_CLASSES = {"PUBLIC", "INTERNAL", "OWNER", "PENDING"}
VALID_VOICE = {"clean", "needs-rewrite", ""}
VALID_DEAD = {"yes", "no", "n/a", ""}

# Documents and data artifacts get dead=n/a. Marking 236 documents dead would
# be noise dressed as a finding, so the column is restricted to code.
CODE_SUFFIXES = {".py", ".sh", ".C", ".cpp", ".h", ".cc"}


def tracked_paths() -> set[str]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        check=True, capture_output=True, text=True,
    ).stdout
    return {p for p in out.split("\0") if p}


def rows() -> list[dict]:
    with MANIFEST.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_header_is_exactly_the_nine_columns() -> None:
    with MANIFEST.open(encoding="utf-8", newline="") as fh:
        header = next(csv.reader(fh))
    assert header == EXPECTED_HEADER, f"header drifted: {header}"


def test_manifest_covers_the_tracked_set_exactly() -> None:
    tracked = tracked_paths()
    listed = {r["path"] for r in rows()}
    missing = sorted(tracked - listed)
    stale = sorted(listed - tracked)
    assert not missing, f"{len(missing)} tracked path(s) have no row: {missing[:10]}"
    assert not stale, f"{len(stale)} row(s) name no tracked path: {stale[:10]}"


def test_row_count_equals_the_tracked_file_count() -> None:
    """Set equality already implies this unless a path appears twice."""
    all_rows = rows()
    assert len(all_rows) == len(tracked_paths())
    paths = [r["path"] for r in all_rows]
    assert len(paths) == len(set(paths)), "a path appears on more than one row"


def test_every_class_voice_and_dead_value_is_from_its_vocabulary() -> None:
    for r in rows():
        assert r["class"] in VALID_CLASSES, f"{r['path']}: class {r['class']!r}"
        assert r["voice"] in VALID_VOICE, f"{r['path']}: voice {r['voice']!r}"
        assert r["dead"] in VALID_DEAD, f"{r['path']}: dead {r['dead']!r}"


def test_every_row_carries_prose_once_classified() -> None:
    for r in rows():
        if r["class"] == "PENDING":
            continue
        assert r["what"].strip(), f"{r['path']}: classified with no what"
        assert r["why"].strip(), f"{r['path']}: classified with no why"


def test_dead_is_restricted_to_code() -> None:
    for r in rows():
        is_code = Path(r["path"]).suffix in CODE_SUFFIXES
        if r["class"] == "PENDING":
            continue
        if is_code:
            assert r["dead"] in {"yes", "no"}, f"{r['path']}: code row dead={r['dead']!r}"
        else:
            assert r["dead"] == "n/a", f"{r['path']}: non-code row dead={r['dead']!r}"


def test_the_committed_file_round_trips_through_the_csv_module() -> None:
    """Re-serialise the parsed rows and compare bytes with the committed file."""
    import io
    parsed = rows()
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=EXPECTED_HEADER, lineterminator="\n")
    writer.writeheader()
    writer.writerows(parsed)
    assert buf.getvalue() == MANIFEST.read_text(encoding="utf-8"), (
        "the committed CSV does not round-trip: a prose field carries "
        "different quoting from what the csv module writes"
    )


def test_the_manifest_is_current_against_the_tool() -> None:
    """tools/repo_audit.py --check rebuilds and compares, so a stale CSV fails."""
    result = subprocess.run(
        ["python3", str(ROOT / "tools" / "repo_audit.py"), "--check"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"docs/REPO_AUDIT.csv is stale or invalid:\n"
        f"{result.stdout}\n{result.stderr}"
    )


def main() -> int:
    test_header_is_exactly_the_nine_columns()
    test_manifest_covers_the_tracked_set_exactly()
    test_row_count_equals_the_tracked_file_count()
    test_every_class_voice_and_dead_value_is_from_its_vocabulary()
    test_every_row_carries_prose_once_classified()
    test_dead_is_restricted_to_code()
    test_the_committed_file_round_trips_through_the_csv_module()
    test_the_manifest_is_current_against_the_tool()
    print(f"repo-audit manifest tests passed ({len(rows())} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
