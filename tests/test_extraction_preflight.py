#!/usr/bin/env python3
"""Require species extraction input to match the registry exactly.

The ROOT projector continues after `PROJ_ERROR`, so Python must check every filename and success count.

The failure that gets through: a directory holds all 300 expected filenames but
one is corrupt. A count-based preflight sees 300. ROOT skips the corrupt file.
The extractor sums 299. Species-vs-category agreement still passes -- both views
lose the same file -- and the run exits 0 with a quietly low total. **Every
self-check downstream is computed from the surviving rows, so a common omission
is invisible to all of them.**

The test also requires a valid `--decay-map` for experiment-comparable grouping.

Six checks:
  1. the exact registry filename set is required -- a MISSING file is caught;
  2. ... and an UNEXPECTED extra file is caught too (count alone would not:
     299 correct + 1 stray also counts 300);
  3. a non-directory argument is caught;
  4. PROJ_ERROR in the projector output is fatal;
  5. a short successful-projection count is fatal;
  6. a non-existent --decay-map is fatal, not a skip.

These run against the real functions with synthetic inputs; none needs ROOT.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "extraction"))
from extract_species_decomposition import load_registry, preflight, project  # noqa: E402

REGISTRY = REPO / "config/heavy_flavour_pair_registry_v1.json"
TOOL = REPO / "extraction/extract_species_decomposition.py"

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


trigger_of, _sector_of = load_registry(REGISTRY)
expected = set(trigger_of)

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)

    # A complete, correct directory is the baseline: if this rejected, every
    # check below would pass for the wrong reason.
    complete = root / "complete"
    complete.mkdir()
    for name in expected:
        (complete / name).write_bytes(b"")
    try:
        preflight(complete, expected)
        check("a complete directory is accepted", True)
    except SystemExit as exc:
        check("a complete directory is accepted", False, str(exc)[:160])

    # --- 1. a missing file --------------------------------------------------
    missing = root / "missing"
    missing.mkdir()
    victim = sorted(expected)[0]
    for name in expected - {victim}:
        (missing / name).write_bytes(b"")
    try:
        preflight(missing, expected)
        check("a MISSING pair file is rejected", False, "accepted")
    except SystemExit as exc:
        check("a MISSING pair file is rejected",
              "missing=1" in str(exc) and victim in str(exc), str(exc)[:160])

    # --- 2. an unexpected extra file (count alone would not catch this) -----
    stray = root / "stray"
    stray.mkdir()
    for name in expected - {victim}:
        (stray / name).write_bytes(b"")
    (stray / "NotInTheRegistry.root").write_bytes(b"")
    n_root = len(list(stray.glob("*.root")))
    try:
        preflight(stray, expected)
        check("an UNEXPECTED file is rejected", False, "accepted")
    except SystemExit as exc:
        check("an UNEXPECTED file is rejected",
              "unexpected=1" in str(exc) and "NotInTheRegistry.root" in str(exc),
              str(exc)[:160])
    check("...and a naive count would NOT have caught it",
          n_root == len(expected), f"{n_root} vs {len(expected)}")

    # --- 3. a non-directory -------------------------------------------------
    afile = root / "not_a_dir"
    afile.write_bytes(b"")
    try:
        preflight(afile, expected)
        check("a non-directory argument is rejected", False, "accepted")
    except SystemExit as exc:
        check("a non-directory argument is rejected",
              "not a directory" in str(exc), str(exc)[:160])

    # --- 4/5. PROJ_ERROR and a short count, via a stub 'root' binary --------
    def stub(body: str) -> str:
        path = root / f"stub_{abs(hash(body))}.sh"
        path.write_text("#!/bin/sh\n" + body + "\n")
        path.chmod(0o755)
        return str(path)

    erroring = stub(
        'out=$(echo "$*" | sed \'s/.*,"//; s/").*//\')\n'
        'printf "pair,kind,bin,content\\n" > "$out"\n'
        'echo "PROJ_ERROR open Broken.root"\n'
        'echo "PROJ_DONE pairs=299"')
    with tempfile.TemporaryDirectory() as work:
        try:
            project(complete, erroring, Path(work), expected=300)
            check("PROJ_ERROR is fatal", False, "accepted")
        except SystemExit as exc:
            check("PROJ_ERROR is fatal",
                  "PROJ_ERROR" in str(exc) and "FAIL-CLOSED" in str(exc),
                  str(exc)[:160])

    short = stub(
        'out=$(echo "$*" | sed \'s/.*,"//; s/").*//\')\n'
        'printf "pair,kind,bin,content\\n" > "$out"\n'
        'echo "PROJ_DONE pairs=299"')
    with tempfile.TemporaryDirectory() as work:
        try:
            project(complete, short, Path(work), expected=300)
            check("a short projection count is fatal", False, "accepted")
        except SystemExit as exc:
            check("a short projection count is fatal",
                  "projected 299" in str(exc), str(exc)[:160])

    # --- 6. a non-existent decay map is fatal, not a skip -------------------
    result = subprocess.run(
        [sys.executable, str(TOOL), str(complete),
         "--decay-map", str(root / "does_not_exist.json")],
        capture_output=True, text=True)
    check("a non-existent --decay-map is fatal, not a silent skip",
          result.returncode != 0 and "does not exist" in (result.stdout + result.stderr),
          f"rc={result.returncode} {(result.stdout + result.stderr)[-200:]}")

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
