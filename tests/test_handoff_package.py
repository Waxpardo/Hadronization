#!/usr/bin/env python3
"""The handoff package describes itself, and describes itself correctly.

`deliverables/<date>/` is what the owner drops into Overleaf. It is the one
directory in this repository whose contents ARE the deliverable, so the thing
worth guarding is not that some code path works but that the package and its
own MANIFEST.md still agree (ruling R30: a gate earns its place by guarding a
deliverable).

Three assertions, and each one catches a different way the package can rot:

  1. EVERY MANIFEST ROW RESOLVES, BYTE FOR BYTE. A row names a path and a
     sha256; the file must exist and hash to that value. This catches a figure
     replaced, truncated or re-rendered without the manifest being rewritten.
  2. THE DIRECTORY HOLDS NOTHING THE MANIFEST DOES NOT NAME. Set equality, not
     containment. This catches a figure added by hand, or one deleted while its
     row stayed behind.
  3. NO PROHIBITED-SCOPE PATH APPEARS IN THE PACKAGE OR IN `docs2/paper/`. The
     two retired systematics trees are `HISTORICAL_PROVENANCE_ONLY` with
     `current_or_publication_use: PROHIBITED`. A citation of either would
     license a paper claim on a retired axis.

     THE SECOND SCOPE IS THE POINT OF THE WIDENING (session WRAP). Until now
     this scan read only `deliverables/<date>/`, so nothing in the suite stopped
     a later session reintroducing a retired-tree citation into
     `docs2/paper/` -- which is where the claim map, the deliverables manifest
     and the campaign-truth page live, and which a referee reads. The package is
     assembled from those pages; guarding the output and not the source guards
     the wrong end.

     NO FILE IS EXEMPT, AND THAT IS DELIBERATE. `docs2/paper/CLAIM_MAP.md`
     states this very rule, and a rule that spelled out the paths it forbids
     would be the scan's first hit. Session HANDOFF had already rewritten that
     statement to name the trees by DATE -- "the ones dated 2026-08-19 and
     2026-08-20" -- and not by path, and it says so in its own text. So the
     widened scan needs no carve-out: measured at WRAP, `docs2/paper/` contains
     no literal retired-tree path. If a later session writes one into the rule
     statement, this gate goes red, and that is the correct outcome rather than
     a false positive to be suppressed.

THE DIRECTORY IS ENUMERATED FROM THE FILESYSTEM, NEVER FROM `git ls-files`
(finding F58). An earlier delivery check listed a directory and compared it
with `git ls-files`; no figure was tracked and the plot directory was ignored,
so both sides were empty and the check passed vacuously on every commit. Here
the package IS tracked, but the lesson stands: the question is what the
directory holds, so the directory is what gets read.

The package is discovered rather than named, so a later dated package is
covered the day it is added.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DELIVERABLES = ROOT / "deliverables"

# The two retired trees. Written as fragments and joined at runtime so that this
# file does not itself contain a literal citation for a scanner to find.
PROHIBITED = tuple(
    "results/systematics/" + stamp for stamp in ("20260819", "20260820")
)

# Directories inside a package whose every file the manifest must name.
MANIFESTED = ("figures", "tables")

# The second PROHIBITED-scope scope, relative to the repository root. The
# package scan below enumerates a package directory; this one is a fixed tree
# and is scanned whether or not a package exists.
PROHIBITED_SCOPE_TREES = ("docs2/paper",)

# Top-level package files that are prose about the package, not package content.
PROSE = {"MANIFEST.md", "EDITORIAL_NOTES.md", "REPRODUCE.md"}

SHA256 = re.compile(r"^[0-9a-f]{64}$")
CODESPAN = re.compile(r"`([^`]+)`")

# Text extensions worth scanning for a prohibited citation. A PDF or PNG cannot
# carry a repository path a reader would follow.
TEXT_SUFFIXES = {".md", ".tex", ".json", ".txt"}

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_rows(manifest: Path) -> dict[str, str]:
    """{package-relative path: sha256} read from MANIFEST.md's tables.

    A row is any table line carrying both a code span that is a bare sha256 and
    a code span that starts with one of the manifested directories. Reading the
    row this way keeps the manifest human-first: its column order can change
    without silently disabling this gate.
    """
    rows: dict[str, str] = {}
    for line in manifest.read_text().splitlines():
        if not line.startswith("|"):
            continue
        spans = CODESPAN.findall(line)
        digests = [s for s in spans if SHA256.match(s)]
        paths = [s for s in spans
                 if s.split("/", 1)[0] in MANIFESTED and not s.endswith("/")]
        if len(digests) == 1 and len(paths) == 1:
            rows[paths[0]] = digests[0]
    return rows


def prohibited_offenders(base: Path) -> list[str]:
    """Every `<file> -> <token>` under `base` that cites a retired tree.

    One predicate for both scopes, so the package and `docs2/paper/` cannot
    drift apart on what counts as a citation. Only text suffixes are read: a
    PDF or PNG cannot carry a repository path a reader would follow.
    """
    offenders: list[str] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(errors="replace")
        for token in PROHIBITED:
            if token in text:
                offenders.append(f"{path.relative_to(base)} -> {token}")
    return offenders


def check_package(package: Path) -> None:
    name = package.name
    manifest = package / "MANIFEST.md"

    check(f"{name}: MANIFEST.md is present", manifest.is_file(), str(manifest))
    if not manifest.is_file():
        return

    rows = manifest_rows(manifest)
    check(f"{name}: MANIFEST.md names at least one file", bool(rows))
    if not rows:
        return

    # 1. every manifest row resolves, byte for byte
    missing = sorted(p for p in rows if not (package / p).is_file())
    check(f"{name}: every file the manifest names exists",
          not missing, f"{len(missing)} missing: {missing[:5]}")

    wrong = []
    for rel, expected in sorted(rows.items()):
        path = package / rel
        if path.is_file() and sha256_of(path) != expected:
            wrong.append(rel)
    check(f"{name}: every file matches its manifest sha256",
          not wrong, f"{len(wrong)} differ: {wrong[:5]}")

    # 2. the directory holds nothing the manifest does not name
    on_disk = set()
    for directory in MANIFESTED:
        base = package / directory
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.name != ".DS_Store":
                on_disk.add(path.relative_to(package).as_posix())

    unlisted = sorted(on_disk - set(rows))
    check(f"{name}: the package holds no file the manifest omits",
          not unlisted, f"{len(unlisted)} unlisted: {unlisted[:5]}")

    check(f"{name}: manifest and directory are the same set",
          on_disk == set(rows),
          f"disk={len(on_disk)} manifest={len(rows)}")

    # every figure named by the manifest exists, stated on its own
    figures = {p for p in rows if p.startswith("figures/")}
    absent = sorted(p for p in figures if not (package / p).is_file())
    check(f"{name}: every figure named by the manifest exists",
          not absent, f"{len(absent)} absent: {absent[:5]}")
    check(f"{name}: the manifest names figures at all", bool(figures))

    # 3. no PROHIBITED-scope citation anywhere in the package
    offenders = prohibited_offenders(package)
    check(f"{name}: cites no PROHIBITED-scope systematics tree",
          not offenders, f"{len(offenders)}: {offenders[:3]}")

    # the prose files exist; they are the package's own explanation
    for prose in sorted(PROSE):
        check(f"{name}: {prose} is present", (package / prose).is_file())


def main() -> int:
    check("deliverables/ exists", DELIVERABLES.is_dir(), str(DELIVERABLES))
    if not DELIVERABLES.is_dir():
        print("\nFAIL: no handoff package to check")
        return 1

    packages = sorted(p for p in DELIVERABLES.iterdir()
                      if p.is_dir() and (p / "MANIFEST.md").is_file())
    check("at least one dated package carries a MANIFEST.md",
          bool(packages), str(sorted(p.name for p in DELIVERABLES.iterdir())))

    for package in packages:
        check_package(package)

    # the same rule, applied to the pages the package is assembled from
    for tree in PROHIBITED_SCOPE_TREES:
        base = ROOT / tree
        check(f"{tree}/ exists", base.is_dir(), str(base))
        if not base.is_dir():
            continue
        offenders = prohibited_offenders(base)
        check(f"{tree}/ cites no PROHIBITED-scope systematics tree",
              not offenders, f"{len(offenders)}: {offenders[:3]}")

    print()
    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    total = sum(len(manifest_rows(p / "MANIFEST.md")) for p in packages)
    print(f"handoff package intact: {len(packages)} package(s), "
          f"{total} manifested files, all sha256-matched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
