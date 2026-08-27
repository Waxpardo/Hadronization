#!/usr/bin/env python3
"""The CLI surface derives, refuses, or names. It never guesses.

WHY THIS FILE EXISTS. The HF_SMOKE3 campaign was the first run to build its own
raw files from the clean repository, so it was the first run to reach several
`./hadronization` surfaces at all. It found a family of defects with one shape:
a surface that guessed a path, took a silent default, or refused while naming
the wrong thing. Each check below drives the real CLI in a sandbox checkout and
requires the derivation, the refusal, or the name.

THE SANDBOX. Every entry symlinks to this checkout except `setupEnv.sh`, which
stands in for the site and dependency planes, and whatever one file the case is
about. That keeps each case fast, identical on every host, and unable to write
into this working tree. `tools/run_tests.sh` fails the whole suite if a test
mutates the resolved `plotting/Plots`, which is the reason the plot cases below
build their own `plotting/` rather than symlinking this one.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIFIED_CLI = ROOT / "hadronization"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
SMOKE_SELECTOR = ROOT / "config/dataset_selector_hf_smoke3.json"

_STUB_SETUP_ENV = """# Sandbox stand-in for setupEnv.sh.
export HADRONIZATION_SITE=local
export HADRONIZATION_DATA_ROOT="${HADRONIZATION_DATA_ROOT:?}"
export HADRONIZATION_RESULTS_ROOT="${HADRONIZATION_DATA_ROOT}/project/results"
export HADRONIZATION_ANALYSIS_ROOT="${HADRONIZATION_DATA_ROOT}/hadronization_analysis"
export HADRONIZATION_MERGED_ROOT="${HADRONIZATION_DATA_ROOT}/hadronization_merged"
export HADRONIZATION_SYSTEMATICS_ROOT="${HADRONIZATION_DATA_ROOT}/systematics_harvest"
export HF_PRODUCTION_ROOT="${HADRONIZATION_DATA_ROOT}/hadronization_production"
"""

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def sandbox(tmp: str, cli_text: str | None = None,
            replace: dict | None = None, git: bool = False) -> Path:
    """A checkout that differs from this one only where the case requires."""
    base = Path(tmp) / "checkout"
    base.mkdir()
    replace = replace or {}
    tops = {rel.split("/")[0] for rel in replace}
    for entry in sorted(ROOT.iterdir()):
        if entry.name not in ({".git", "setupEnv.sh", "hadronization"} | tops):
            (base / entry.name).symlink_to(entry)
    for top in sorted(tops):
        (base / top).mkdir(exist_ok=True)
        dropped = {rel.split("/", 1)[1] for rel in replace
                   if rel.startswith(top + "/") and replace[rel] is None}
        for entry in sorted((ROOT / top).iterdir()):
            if entry.name not in dropped:
                (base / top / entry.name).symlink_to(entry)
    for rel, text in replace.items():
        if text is None:
            continue
        target = base / rel
        if target.is_symlink():
            target.unlink()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        target.chmod(0o755)
    (base / "setupEnv.sh").write_text(_STUB_SETUP_ENV)
    cli = base / "hadronization"
    cli.write_text(cli_text if cli_text is not None
                   else UNIFIED_CLI.read_text())
    cli.chmod(0o755)
    if git:
        # The plot planes read the commit. Never the real repository: a test
        # must not be able to write into it.
        for command in (["init", "-q"],
                        ["-c", "user.name=t", "-c", "user.email=t@t",
                         "commit", "-q", "--allow-empty", "-m", "sandbox"]):
            subprocess.run(["git", "-C", str(base), *command], check=True,
                           capture_output=True)
    return base


def raw_fixture(data: Path, campaign: str, jobs: int = 10) -> Path:
    """A promoted raw tree with the sidecars and metadata the freeze reads."""
    campaign_root = data / "hadronization_production" / campaign
    for tune in TUNES:
        (campaign_root / "raw" / tune).mkdir(parents=True, exist_ok=True)
        (campaign_root / "attempt_metadata" / tune).mkdir(
            parents=True, exist_ok=True)
        for job in range(jobs):
            path = campaign_root / "raw" / tune / f"hf_{tune}_job{job:03d}.root"
            path.write_bytes(f"{campaign}/{tune}/{job}".encode())
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            path.with_suffix(path.suffix + ".sha256").write_text(
                f"{digest}  {path.name}\n")
            # requested_successes and seed come from the promoted attempt's
            # metadata; a row without it is refused as incomplete.
            (campaign_root / "attempt_metadata" / tune
             / f"{tune}_job{job:03d}_attempt000.json").write_text(json.dumps({
                 "tune": tune, "logical_id": job, "attempt": 0,
                 "producer_exit": 0, "requested_successes": 20000,
                 "seed": 100000001 + job, "campaign_ordinal": 11,
                 "role": "primary", "effective_card_sha256": "0" * 64,
                 "producer_executable_sha256": "1" * 64,
                 "repository_commit": "2" * 40,
                 "multiplicity_audit_events": 0, "pthat_min_override": "2.0",
             }))
    return campaign_root


def run_cli(base: Path, data: Path, args: list[str],
            env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(HADRONIZATION_DATA_ROOT=str(data),
               HADRONIZATION_DATASET_SELECTOR=str(SMOKE_SELECTOR))
    for name in ("HADRONIZATION_BASE", "THNSPARSE_COMPLETE_ROOT_CONFIG",
                 "THNSPARSE_CONFIG", "MULTIPLICITY_CONFIG",
                 "HADRONIZATION_MEASUREMENT_CONFIG",
                 "HADRONIZATION_MEASUREMENT_ROOT"):
        env.pop(name, None)
    env.update(env_extra or {})
    return subprocess.run(["bash", str(base / "hadronization"), *args],
                          env=env, text=True, capture_output=True)


# --- Phase 1: the freeze root ---------------------------------------------
#
# THE DEFECT THIS CLOSES. `hadronization:192` passed the selector's
# campaign-scoped HADRONIZATION_PRODUCTION_ROOT to
# tools/build_canonical_manifest.py, whose line 87 joins the campaign on again.
# `./hadronization freeze hf_smoke3` refused with
# `no raw directory: .../HF_SMOKE3/HF_SMOKE3/raw`. Every run before HF_SMOKE3
# reused a pre-rebuild manifest, so no run had reached this surface.
#
# The tool keeps re-joining and the CLI passes the base root, because the tool
# is the side with other callers: `make manifest` (Makefile:239) passes no
# --production-root and relies on the tool's HF_PRODUCTION_ROOT default, which
# is the base root, and the tool's own contract note (:36-39) says manifest
# paths are relative to the campaign directory.

def test_freeze_produces_a_manifest_from_a_raw_tree() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = sandbox(tmp)
        data = Path(tmp) / "data"
        raw_fixture(data, "HF_SMOKE3")
        got = run_cli(base, data, ["freeze", "hf_smoke3"])
        freeze = data / "project/runs/HF_SMOKE3/freeze"
        check("freeze writes a manifest from a raw tree",
              got.returncode == 0, f"rc={got.returncode} {got.stderr[:300]}")
        check("...naming no doubled campaign segment",
              "HF_SMOKE3/HF_SMOKE3" not in got.stderr, got.stderr[:300])
        manifest = freeze / "canonical_manifest.jsonl"
        check("...and the manifest exists", manifest.is_file(), str(manifest))
        if manifest.is_file():
            rows = [json.loads(line) for line in
                    manifest.read_text().splitlines() if line.strip()]
            check("...carrying one row per promoted raw file",
                  len(rows) == 30, f"{len(rows)} rows")
            check("...whose raw paths are relative to the campaign directory",
                  all(row["raw_path"].startswith("raw/") for row in rows),
                  str(rows[0]["raw_path"]) if rows else "no rows")
        check("...and the seal is written",
              (freeze / "freeze_seal.json").is_file(), str(freeze))
        check("...with ten block manifests",
              len(list(freeze.glob("block_*.jsonl"))) == 10,
              str(sorted(p.name for p in freeze.glob("block_*.jsonl"))))


def test_freeze_refuses_a_row_that_is_not_campaign_scoped() -> None:
    """The base root is derived from the row, so the row has to fit."""
    document = json.loads(SMOKE_SELECTOR.read_text())
    row = document["datasets"]["hf_smoke3"]
    row["production_root"] = "${HADRONIZATION_DATA_ROOT}/hadronization_production"
    with tempfile.TemporaryDirectory() as tmp:
        base = sandbox(tmp)
        data = Path(tmp) / "data"
        raw_fixture(data, "HF_SMOKE3")
        selector = Path(tmp) / "selector.json"
        selector.write_text(json.dumps(document))
        got = run_cli(base, data, ["freeze", "hf_smoke3"],
                      {"HADRONIZATION_DATASET_SELECTOR": str(selector)})
    check("freeze refuses a row whose production_root is not campaign-scoped",
          got.returncode != 0, f"rc={got.returncode} {got.stdout[:200]}")
    check("...naming the campaign and the root it was given",
          "HF_SMOKE3" in got.stderr and "hadronization_production" in got.stderr,
          got.stderr[:400])
    check("...and writes no manifest",
          not (data / "project/runs/HF_SMOKE3/freeze"
               / "canonical_manifest.jsonl").is_file(), "a manifest appeared")


def test_freeze_does_not_pass_the_campaign_scoped_root() -> None:
    """Read the source too: the doubled join must not come back."""
    text = UNIFIED_CLI.read_text()
    block = text[text.index("  freeze)"):]
    block = block[:block.index("  render-analysis)")]
    check("the freeze branch passes no campaign-scoped production root",
          '--production-root "${HADRONIZATION_PRODUCTION_ROOT}"' not in block,
          block[-400:])
    check("...and derives the base from the row",
          'freeze_production_base="$(dirname "${HADRONIZATION_PRODUCTION_ROOT}")"'
          in block, block[-400:])


def main() -> int:
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
