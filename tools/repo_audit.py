#!/usr/bin/env python3
"""Build the per-file publication audit manifest at docs/REPO_AUDIT.csv.

The repository at github.com/Waxpardo/Hadronization becomes the INTERNAL tree.
A separate repository will later be built from one initial commit holding only
the files this manifest marks PUBLIC. This script does not perform that export
and it does not decide what belongs in it.

WHAT THIS SCRIPT DOES AND DOES NOT DO. It measures. For every tracked path it
reports size, last-commit date, how many other tracked files name it, and
whether a named driver invokes it. Those four numbers are evidence. The ruling
that turns evidence into PUBLIC or INTERNAL is judgement, it is not derivable
from any of them, and it lives in a separate hand-written file:

    tools/repo_audit_rulings.json

The split matters because the evidence goes stale on every commit and the
judgement does not. Re-running this script after a merge refreshes every
measured column and preserves every ruling.

A PATH WITH NO RULING IS NOT AN ERROR. The tool writes it with class=PENDING,
so the manifest holds a row for every tracked path from the first run onward.
Coverage is therefore mechanical: the set of paths in the CSV equals the set
git ls-files reports, always, and "not yet classified" is a value in the file
rather than a silent gap. tests/test_repo_audit_manifest.py enforces that
equality and fails closed.

    python3 tools/repo_audit.py              # rewrite docs/REPO_AUDIT.csv
    python3 tools/repo_audit.py --check      # exit 1 if the CSV is stale
    python3 tools/repo_audit.py --evidence   # dump evidence as JSON, write nothing
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RULINGS = REPO / "tools" / "repo_audit_rulings.json"
MANIFEST = REPO / "docs" / "REPO_AUDIT.csv"
CITATIONS = REPO / "docs" / "REPO_AUDIT_CITATIONS.tsv"

COLUMNS = [
    "path", "class", "what", "why", "refs",
    "entrypoint", "voice", "dead", "grouped",
]

VALID_CLASSES = {"PUBLIC", "INTERNAL", "OWNER", "PENDING"}

# The dead column applies to CODE ONLY. Almost nothing references a document,
# so marking 236 of them dead would be noise dressed as a finding. The rule is
# mechanical, so it is applied here rather than restated in every ruling: a
# group that covers macros and PYTHIA cards together gets it right either way.
CODE_SUFFIXES = {".py", ".sh", ".C", ".cpp", ".h", ".cc"}

# THE AUDIT'S OWN ARTIFACTS ARE NOT REFERENCES, and excluding them is required
# rather than tidy. Both files name every path in the tree, so counting them
# would add one to all 790 reference counts -- and because the manifest holds
# those counts, writing it would change them, which would change the manifest.
# The count would never reach a fixed point and --check could never pass.
# An inventory is not a consumer: nothing in it reads the file it lists.
SCAN_EXCLUDE = {"docs/REPO_AUDIT.csv", "tools/repo_audit_rulings.json",
                "docs/REPO_AUDIT_CITATIONS.tsv"}

CITATION_COLUMNS = ["citing", "cited", "token", "count", "lines"]
VALID_VOICE = {"clean", "needs-rewrite", ""}
VALID_DEAD = {"yes", "no", "n/a", ""}

# The drivers named in the session brief. Entry-point membership means one of
# these files names the path, either literally or through a glob it expands.
# Makefile needs no transitive walk here: every tool it delegates to that
# matters is either in this list already (tools/run_tests.sh) or is named in
# the Makefile body directly, which the literal scan catches.
DRIVERS = [
    "Makefile",
    "generation/submit/runCondorJob.sh",
    "merging/merge_root_files.sh",
    "analysis/run_status_analysis.sh",
    "plotting/run_paper_plots.sh",
    "extraction/pipeline/tune_chain.sh",
    "tools/run_tests.sh",
]

# Shell and make globs written inside a driver. tools/run_tests.sh:38 globs
# tests/test_*.py, so 80 live tests are invoked by pattern and are named
# nowhere. Counting them as unreferenced would invert the strongest signal in
# the tree, which is the failure mode docs/REPO_FILE_CENSUS.md 0.1 warned about.
GLOB_TOKEN = re.compile(r"[A-Za-z0-9_./\-]*\*[A-Za-z0-9_./\-]*")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        check=True, capture_output=True, text=True,
    ).stdout


def tracked_paths() -> list[str]:
    out = git("ls-files", "-z")
    return sorted(p for p in out.split("\0") if p)


def last_commit_dates(paths: set[str]) -> dict[str, str]:
    """Date each path was last touched, from one walk of the history.

    git log emits newest first, so the first time a path appears is its last
    commit. One walk replaces 786 per-path git log calls.
    """
    out = git("log", "--no-renames", "--date=short", "--format=@%ad", "--name-only")
    dates: dict[str, str] = {}
    current = ""
    for line in out.splitlines():
        if line.startswith("@"):
            current = line[1:]
        elif line and current and line in paths and line not in dates:
            dates[line] = current
    return dates


def read_text(path: Path) -> str | None:
    """Return decoded text, or None when the file is binary.

    A binary file contributes no references. ROOT files, PDFs and compiled
    dictionaries are read by name from elsewhere, never by grepping them.
    """
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def build_basename_scanner(paths: list[str]) -> tuple[re.Pattern[str], dict[str, set[str]]]:
    """Compile one alternation over every tracked basename, longest first.

    Longest-first is the correct reading, not an optimisation. When a document
    writes run_campaign.py, it refers to run_campaign.py and not to
    campaign.py, and a longest-first alternation consumes the whole token so
    only the longer basename scores.
    """
    by_base: dict[str, set[str]] = {}
    for p in paths:
        by_base.setdefault(os.path.basename(p), set()).add(p)
    ordered = sorted(by_base, key=lambda b: (-len(b), b))
    pattern = re.compile("|".join(re.escape(b) for b in ordered))
    return pattern, by_base


def reference_counts(paths: list[str]) -> tuple[dict[str, int], dict[str, set[str]]]:
    """For each basename, how many OTHER tracked files contain it.

    THE COUNT IS PER BASENAME, NOT PER PATH. Twelve files carry the name
    MANIFEST.md and they share one score. The number is a proxy for attention,
    it is not a proxy for liveness, and docs/REPO_FILE_CENSUS.md 0.1 records it
    lying in both directions. No ruling rests on it alone.
    """
    scanner, by_base = build_basename_scanner(paths)
    hits: dict[str, set[str]] = {b: set() for b in by_base}
    for p in paths:
        if p in SCAN_EXCLUDE:
            continue
        text = read_text(REPO / p)
        if text is None:
            continue
        for base in set(scanner.findall(text)):
            hits[base].add(p)
    counts = {}
    for base, owners in by_base.items():
        # Subtract self-mentions: a file naming itself is not a reference to it.
        counts[base] = len(hits[base] - owners)
    return counts, hits


def entrypoint_map(paths: list[str]) -> dict[str, str]:
    """Which driver, if any, invokes each path.

    Two mechanisms, because the drivers use two. A literal basename in the
    driver body is the common one. A glob is the other, and it is the one that
    carries the test suite.
    """
    scanner, by_base = build_basename_scanner(paths)
    found: dict[str, list[str]] = {}
    path_set = set(paths)
    for driver in DRIVERS:
        dpath = REPO / driver
        if not dpath.exists():
            continue
        text = read_text(dpath)
        if text is None:
            continue
        named: set[str] = set()
        for base in set(scanner.findall(text)):
            named |= by_base.get(base, set())
        for token in set(GLOB_TOKEN.findall(text)):
            if "*" not in token or len(token) < 4:
                continue
            cleaned = token.lstrip("./")
            for p in path_set:
                if fnmatch.fnmatch(p, cleaned) or fnmatch.fnmatch(os.path.basename(p), cleaned):
                    named.add(p)
        for p in named:
            if p == driver:
                continue
            found.setdefault(p, []).append(driver)
    return {p: ";".join(sorted(d)) for p, d in found.items()}


def citation_hits(rows: list[dict]) -> list[dict]:
    """Every place a PUBLIC file names an INTERNAL path.

    THIS IS THE EXPORT'S CENTRAL PROMISE, and until now nothing measured it. A
    published file that cites an excluded one sends its reader to a 404 in the
    best case and, in the worst, quotes a superseded number by reference.

    Two needles per INTERNAL path. The full repo-relative path always. The bare
    basename only when exactly one tracked file carries it -- twelve files
    carry the name MANIFEST.md, and matching that would flag every anchor
    directory for naming its own manifest. Uniqueness is the whole test for
    "distinctive", and it runs against the WHOLE tree rather than against the
    internal set, so a basename a PUBLIC file shares never becomes a needle.

    Longest-first alternation, for the same reason reference_counts uses it:
    text naming docs/PRODUCTION_SHAPE_DECISION.md refers to that path, not
    separately to its basename.
    """
    cls = {r["path"]: r["class"] for r in rows}
    owners: dict[str, int] = {}
    for p in cls:
        owners[os.path.basename(p)] = owners.get(os.path.basename(p), 0) + 1
    needles: dict[str, str] = {}
    for p in sorted(cls):
        if cls[p] != "INTERNAL":
            continue
        needles[p] = p
        base = os.path.basename(p)
        if owners[base] == 1:
            needles.setdefault(base, p)
    if not needles:
        return []
    ordered = sorted(needles, key=lambda n: (-len(n), n))
    scan = re.compile("|".join(re.escape(n) for n in ordered))

    found: dict[tuple[str, str, str], list[int]] = {}
    for p in sorted(cls):
        if cls[p] != "PUBLIC" or p in SCAN_EXCLUDE:
            continue
        text = read_text(REPO / p)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for token in set(scan.findall(line)):
                found.setdefault((p, needles[token], token), []).append(lineno)
    return [
        {"citing": c, "cited": t, "token": tok,
         "count": str(len(lines)), "lines": ",".join(str(n) for n in sorted(lines))}
        for (c, t, tok), lines in sorted(found.items())
    ]


def render_citations(hits: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CITATION_COLUMNS,
                            delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(hits)
    return buf.getvalue()


def load_rulings() -> dict:
    if not RULINGS.exists():
        return {"groups": {}, "paths": {}}
    with RULINGS.open(encoding="utf-8") as fh:
        data = json.load(fh)
    data.setdefault("groups", {})
    data.setdefault("paths", {})
    data.setdefault("voice_rewrite", [])
    return data


def resolve_ruling(path: str, rulings: dict) -> dict:
    """Ruling for one path: an explicit row wins over its group.

    Group membership is a glob. An explicit entry for a path inside a group
    overrides the group and keeps the group name. That is how an exception
    carries itself: it still reports which group it came out of.
    """
    row = {"class": "PENDING", "what": "", "why": "", "voice": "", "dead": "", "grouped": ""}
    for name, group in rulings["groups"].items():
        for pattern in group.get("match", []):
            if fnmatch.fnmatch(path, pattern):
                row.update({k: v for k, v in group.items() if k in row})
                row["grouped"] = name
                break
    explicit = rulings["paths"].get(path)
    if explicit:
        keep_group = row["grouped"] if explicit.get("keep_group", True) else ""
        row.update({k: v for k, v in explicit.items() if k in row})
        if "grouped" not in explicit:
            row["grouped"] = keep_group
    # The voice list marks a file whose PROSE addresses a session, an agent, a
    # review finding or an internal document, without touching what the file IS.
    # It is kept separate from the group so one flagged member does not force
    # every sibling out of the group's shared sentence.
    if path in rulings["voice_rewrite"] and row["class"] != "PENDING":
        row["voice"] = "needs-rewrite"
    if os.path.splitext(path)[1] not in CODE_SUFFIXES:
        row["dead"] = "n/a" if row["class"] != "PENDING" else row["dead"]
    return row


def build_rows() -> list[dict]:
    paths = tracked_paths()
    counts, _ = reference_counts(paths)
    entry = entrypoint_map(paths)
    rulings = load_rulings()
    rows = []
    for p in paths:
        row = resolve_ruling(p, rulings)
        row["path"] = p
        row["refs"] = counts[os.path.basename(p)]
        row["entrypoint"] = entry.get(p, "")
        rows.append({c: row[c] for c in COLUMNS})
    return rows


def validate(rows: list[dict]) -> list[str]:
    problems = []
    for r in rows:
        if r["class"] not in VALID_CLASSES:
            problems.append(f"{r['path']}: class {r['class']!r}")
        if r["voice"] not in VALID_VOICE:
            problems.append(f"{r['path']}: voice {r['voice']!r}")
        if r["dead"] not in VALID_DEAD:
            problems.append(f"{r['path']}: dead {r['dead']!r}")
        if r["class"] != "PENDING" and not r["what"].strip():
            problems.append(f"{r['path']}: classified with empty what")
        if r["class"] != "PENDING" and not r["why"].strip():
            problems.append(f"{r['path']}: classified with empty why")
    return problems


def render(rows: list[dict]) -> str:
    """Serialise with the csv module.

    Never join these fields by hand. Both prose columns carry commas, quotes
    and the odd semicolon, and a hand-rolled writer turns one of them into a
    column shift that no reader notices until the export uses the wrong class.
    """
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed CSV differs from a fresh build")
    ap.add_argument("--evidence", action="store_true",
                    help="print the measured columns as JSON and write nothing")
    ap.add_argument("--citations", action="store_true",
                    help="rewrite docs/REPO_AUDIT_CITATIONS.tsv and exit")
    args = ap.parse_args()

    rows = build_rows()
    problems = validate(rows)
    if problems:
        for p in problems[:40]:
            print(f"INVALID {p}", file=sys.stderr)
        print(f"{len(problems)} invalid row(s)", file=sys.stderr)
        return 2

    if args.evidence:
        paths = tracked_paths()
        dates = last_commit_dates(set(paths))
        evidence = [
            {
                "path": r["path"],
                "bytes": (REPO / r["path"]).stat().st_size,
                "last_commit": dates.get(r["path"], ""),
                "refs": r["refs"],
                "entrypoint": r["entrypoint"],
            }
            for r in rows
        ]
        json.dump(evidence, sys.stdout, indent=1)
        print()
        return 0

    if args.citations:
        hits = citation_hits(rows)
        CITATIONS.write_text(render_citations(hits), encoding="utf-8")
        total = sum(int(h["count"]) for h in hits)
        print(f"wrote {CITATIONS.relative_to(REPO)} -- "
              f"{total} reference(s) from {len({h['citing'] for h in hits})} file(s)")
        return 0

    text = render(rows)
    if args.check:
        current = MANIFEST.read_text(encoding="utf-8") if MANIFEST.exists() else ""
        if current != text:
            print("STALE docs/REPO_AUDIT.csv -- rerun tools/repo_audit.py", file=sys.stderr)
            return 1
        cit = render_citations(citation_hits(rows))
        have = CITATIONS.read_text(encoding="utf-8") if CITATIONS.exists() else ""
        if have != cit:
            print("STALE docs/REPO_AUDIT_CITATIONS.tsv -- rerun with --citations",
                  file=sys.stderr)
            return 1
        print(f"CURRENT docs/REPO_AUDIT.csv ({len(rows)} rows) and its citation ledger")
        return 0

    MANIFEST.write_text(text, encoding="utf-8")
    by_class: dict[str, int] = {}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    print(f"wrote {MANIFEST.relative_to(REPO)} -- {len(rows)} rows")
    for k in sorted(by_class):
        print(f"  {k:<8} {by_class[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
