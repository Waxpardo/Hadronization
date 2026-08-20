#!/usr/bin/env python3
"""Scan PUBLIC prose for terms docs/TERMS.md rules out, and hold a ratchet.

WHY A RATCHET AND NOT A GATE. The documentation rewrite has 44 documents still
to rewrite, so today's tree violates the registry in hundreds of places. A check
that simply failed would be red from the first commit and switched off by the
second. This one fails on any violation the committed baseline does not already
record: new prose cannot add one, and each rewrite session deletes its
document's rows as it goes. The baseline shrinks to zero over the rewrite, and
progress is a number rather than an impression.

THE MATCH RULE, AND THE ONE TRAP IT CLOSES. Canonical and ruled-out terms are
matched together in one longest-first alternation, and only a ruled-out match is
reported. That is what lets `partner` be ruled out while **balancing partner**
stays canonical: the longer canonical term consumes the text first, so the bare
noun is the only thing left to flag. `configuration` over `config` works the
same way.

CODE IS NOT PROSE. Fenced blocks and inline backticked spans are removed before
matching. Without that, every `config/` path and every `sub-sample` quoted BY
the registry would be a violation of it.

    python3 tools/terms_check.py             # report violations
    python3 tools/terms_check.py --baseline  # rewrite docs/TERMS_BASELINE.tsv
    python3 tools/terms_check.py --check     # exit 1 if the baseline is stale
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "docs" / "TERMS.md"
MANIFEST = REPO / "docs" / "REPO_AUDIT.csv"
BASELINE = REPO / "docs" / "TERMS_BASELINE.tsv"

COLUMNS = ["path", "term", "canonical", "count", "lines"]

# The registry quotes every ruled-out term by definition, so scanning it would
# report the document that defines the rule as the worst offender against it.
SCAN_EXCLUDE = {"docs/TERMS.md", "docs/TERMS_BASELINE.tsv"}

FENCE = re.compile(r"^\s*```", re.M)
INLINE_CODE = re.compile(r"`[^`\n]*`")
ROW = re.compile(r"^\|\s*\*\*(?P<canon>[^*]+)\*\*\s*\|(?P<rest>.*)\|\s*$")


def registry() -> tuple[dict[str, str], list[str]]:
    """Read the table. Returns ruled-out -> canonical, and every canonical term.

    Parsing the committed document rather than a second list is deliberate: a
    registry and a checker that hold their own copies drift, and the drift is
    invisible until someone reads both.
    """
    ruled: dict[str, str] = {}
    canon: list[str] = []
    inside = False
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if line.startswith("## THE REGISTRY"):
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if not inside:
            continue
        m = ROW.match(line)
        if not m:
            continue
        term = m.group("canon").strip()
        canon.append(term)
        cells = [c.strip() for c in m.group("rest").split("|")]
        if len(cells) < 2:
            continue
        for bad in re.findall(r"`([^`]+)`", cells[1]):
            ruled.setdefault(bad.strip(), term)
    return ruled, canon


def public_prose() -> list[str]:
    with MANIFEST.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return sorted(
        r["path"] for r in rows
        if r["class"] == "PUBLIC"
        and r["path"].endswith((".md", ".txt"))
        and r["path"] not in SCAN_EXCLUDE
    )


def strip_code(text: str) -> list[str]:
    """Blank out code, keeping line numbers intact.

    This blanks each line rather than dropping it, so a reported line number
    still points at the line a reader will open.
    """
    out = []
    fenced = False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else INLINE_CODE.sub(" ", line))
    return out


def scanner(ruled: dict[str, str], canon: list[str]) -> re.Pattern[str]:
    terms = sorted(set(ruled) | set(canon), key=lambda t: (-len(t), t))
    body = "|".join(re.escape(t) for t in terms)
    return re.compile(r"(?<![\w-])(" + body + r")(?![\w-])", re.I)


def violations() -> list[dict]:
    ruled, canon = registry()
    scan = scanner(ruled, canon)
    lower = {k.lower(): v for k, v in ruled.items()}
    found: dict[tuple[str, str, str], list[int]] = {}
    for path in public_prose():
        try:
            text = (REPO / path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(strip_code(text), 1):
            for hit in scan.findall(line):
                canonical = lower.get(hit.lower())
                if canonical is None:
                    continue          # a canonical term matched; not a violation
                found.setdefault((path, hit.lower(), canonical), []).append(lineno)
    return [
        {"path": p, "term": t, "canonical": c, "count": str(len(ln)),
         "lines": ",".join(str(n) for n in sorted(set(ln)))}
        for (p, t, c), ln in sorted(found.items())
    ]


def render(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline", action="store_true",
                    help="rewrite docs/TERMS_BASELINE.tsv from the current tree")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed baseline is stale")
    args = ap.parse_args()

    rows = violations()
    total = sum(int(r["count"]) for r in rows)

    if args.baseline:
        BASELINE.write_text(render(rows), encoding="utf-8")
        print(f"wrote {BASELINE.relative_to(REPO)} -- {total} violation(s) "
              f"in {len({r['path'] for r in rows})} file(s)")
        return 0

    if args.check:
        have = BASELINE.read_text(encoding="utf-8") if BASELINE.exists() else ""
        if have != render(rows):
            print("STALE docs/TERMS_BASELINE.tsv -- rerun with --baseline",
                  file=sys.stderr)
            return 1
        print(f"CURRENT docs/TERMS_BASELINE.tsv ({total} violations)")
        return 0

    for r in rows:
        print(f"{r['path']}:{r['lines']}  {r['term']!r} -> {r['canonical']!r} "
              f"({r['count']}x)")
    print(f"{total} violation(s) in {len({r['path'] for r in rows})} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
