#!/usr/bin/env python3
"""Filesystem-enumerated gate for the canonical migration result package."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath


ROOT = Path(os.environ.get("RESULTS1_ROOT", Path(__file__).resolve().parents[1]))
RESULTS = ROOT / "results"
MANIFEST = RESULTS / "manifest.json"
SUBTREES = ("measurement", "plots", "tables")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
assert manifest["schema"] == "hadronization_result_package_v1"
assert manifest["status"] == "migration_baseline"
assert manifest["systematics"] == "disabled_not_included"
assert manifest["discarded_attempts"] == "recorded_no_correction"
assert manifest["import_commit"]["manifest_self_hash"] is None

declared_rows = manifest["artifacts"]
declared = {row["path"]: row for row in declared_rows}
if len(declared) != len(declared_rows):
    raise AssertionError("result manifest artifact path is not unique")
on_disk = {path.relative_to(ROOT).as_posix() for subtree in SUBTREES
           for path in (RESULTS / subtree).rglob("*") if path.is_file()}
if set(declared) != on_disk:
    missing = sorted(set(declared) - on_disk)
    unlisted = sorted(on_disk - set(declared))
    raise AssertionError(f"manifest/filesystem set mismatch: missing={missing[:4]} unlisted={unlisted[:4]}")

for rel, row in declared.items():
    pure = PurePosixPath(rel)
    if pure.is_absolute() or ".." in pure.parts or pure.parts[:2] not in {
            ("results", "measurement"), ("results", "plots"), ("results", "tables")}:
        raise AssertionError(f"consumer cannot resolve repository-relative result path: {rel}")
    path = ROOT / rel
    if path.stat().st_size != row["bytes"]:
        raise AssertionError(f"manifest byte count mismatch: {rel}")
    if sha256(path) != row["sha256"]:
        raise AssertionError(f"manifest SHA-256 mismatch: {rel}")
    if not row.get("producer") or not row.get("consumer"):
        raise AssertionError(f"producer/consumer role missing: {rel}")

plots = sorted((RESULTS / "plots").glob("*.pdf"))
if len(plots) != 38:
    raise AssertionError(f"canonical PDF count: {len(plots)} != 38")
tables = sorted((RESULTS / "tables").glob("*.tex"))
if [path.name for path in tables] != ["sample_counts.tex"]:
    raise AssertionError(f"canonical TeX table set differs: {[path.name for path in tables]}")
mapping = manifest["plot_name_mapping"]
if len(mapping) != 38 or {row["new_name"] for row in mapping} != {
        path.relative_to(ROOT).as_posix() for path in plots}:
    raise AssertionError("old-name/new-name mapping does not cover exactly 38 canonical plots")

for path in plots:
    payload = path.read_bytes()
    if not payload.startswith(b"%PDF-") or b"%%EOF" not in payload[-1024:]:
        raise AssertionError(f"invalid PDF header/trailer: {path.name}")
    page_count = len(re.findall(rb"/Type\s*/Page(?!s)", payload))
    if page_count != 1:
        raise AssertionError(f"accepted canonical PDF is not one page: {path.name} pages={page_count}")

prohibited_suffixes = {".c", ".so", ".d", ".pcm", ".log", ".png", ".bak", ".backup"}
commit_directory = re.compile(r"^[0-9a-f]{7,40}$")
date_directory = re.compile(r"^20\d{6}$")
for subtree in SUBTREES:
    for path in (RESULTS / subtree).rglob("*"):
        relative = path.relative_to(RESULTS)
        if path.is_file() and path.suffix.lower() in prohibited_suffixes:
            raise AssertionError(f"prohibited generated/source artifact in canonical result: {relative}")
        for part in relative.parts:
            if part.startswith("superseded-") or commit_directory.fullmatch(part) or date_directory.fullmatch(part):
                raise AssertionError(f"prohibited dated/commit/superseded path in canonical result: {relative}")

data_files = manifest["campaign"]["data_files"]
for rel, identity in data_files.items():
    path = ROOT / rel
    if path.stat().st_size != identity["bytes"] or sha256(path) != identity["sha256"]:
        raise AssertionError(f"campaign data digest mismatch in result manifest: {rel}")

print("PASS test_results_package.py")
