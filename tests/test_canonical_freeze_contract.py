#!/usr/bin/env python3
"""The canonical-freeze contract describes the seal, and stays fail-closed.

THE DEFECT THIS PINS. The contract in Plot_InclusiveKinematicSpectra_Raw.C used
to hardcode one campaign's arithmetic -- `jobs_per_tune == 100` and
`requested_successes == 1000000`, which is HF_100M_primaryGround_ccbb_v1. When
HF_RUN3_V1 arrived at 1000 jobs x 100000 events -- the SAME 100M per tune,
differently divided -- a correct, sealed, fully validated freeze was refused for
having the wrong shape. It also demanded two artifacts, freeze_summary.json and
canonical_raw_validation_receipt.json, that nothing in the repository writes
outside test fixtures.

What is pinned here is the property that replaced it: **the shape is derived
from the manifest and the seal is required to agree with it**, so no campaign
decomposition is privileged. The positive case therefore uses a shape the old
contract would have refused on BOTH counts, which is the only way to tell a
derivation from a coincidence.

And the gate must not have become permissive in the process. Every negative case
below is a freeze that is unsealed, incomplete, tampered with, or internally
inconsistent, and every one of them must still refuse to render.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MACRO = "plotting/Plot_InclusiveKinematicSpectra_Raw.C"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")

# A shape the retired contract would have rejected twice over: not 100 jobs per
# tune, and not 1000000 events per job.
JOBS_PER_TUNE = 20
EVENTS_PER_JOB = 50_000
BLOCKS = 10


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_freeze(directory: Path, *, mutate=None) -> tuple[Path, Path]:
    """A minimal sealed freeze. `mutate(rows, seal)` may break it on purpose."""
    production = directory / "production"
    freeze = production / "freeze"
    freeze.mkdir(parents=True)

    rows: list[dict] = []
    for tune_index, tune in enumerate(TUNES):
        tune_dir = production / "raw" / tune
        tune_dir.mkdir(parents=True)
        for slot in range(JOBS_PER_TUNE):
            raw = tune_dir / f"canonical_{slot:03d}.root"
            raw.write_bytes(f"{tune}:{slot}\n".encode())
            rows.append({
                "schema": "hf_canonical_raw_manifest_v2",
                "campaign": "contract_test",
                "tune": tune,
                "canonical_slot": slot,
                "block": slot % BLOCKS,
                "block_position": slot // BLOCKS,
                "raw_path": raw.relative_to(production).as_posix(),
                "raw_bytes": raw.stat().st_size,
                "raw_sha256": sha256_file(raw),
                "raw_schema": "hf_primary_ground_raw_v7",
                "selector": "hard_trigger_primary_ground__"
                            "primary_ground_associate_v1",
                "requested_successes": EVENTS_PER_JOB,
                "seed": tune_index * 100000 + slot,
                "attempt_receipt_path": f"attempt_metadata/{tune}/{slot}.json",
                "raw_validation_log_path": f"raw_validation/{tune}/{slot}.log",
                "raw_validation_log_sha256": "a" * 64,
                "raw_validation_receipt_path": f"raw_validation/{tune}/{slot}.json",
                "raw_validation_receipt_sha256": "b" * 64,
            })

    seal = {
        "schema": "hf_canonical_freeze_seal_v2",
        "state": "SEALED",
        "campaign": "contract_test",
        "rows": len(rows),
        "tunes": list(TUNES),
        "jobs_per_tune": JOBS_PER_TUNE,
        "blocks": BLOCKS,
        "total_requested_successes": len(rows) * EVENTS_PER_JOB,
    }

    if mutate is not None:
        mutate(rows, seal)

    manifest = freeze / "canonical_manifest.jsonl"
    manifest.write_text("".join(
        json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n" for r in rows))
    seal.setdefault("canonical_manifest_sha256", sha256_file(manifest))
    (freeze / "freeze_seal.json").write_text(
        json.dumps(seal, indent=2, sort_keys=True) + "\n")
    return manifest, production


def run_selection(root: str, manifest: Path, production: Path,
                  files_per_tune: int,
                  promoted_campaign: str = "") -> subprocess.CompletedProcess:
    expression = (
        f"TestInclusiveRawCanonicalManifestSelection("
        f"{json.dumps(str(manifest))},{json.dumps(str(production))},"
        f"{files_per_tune},{json.dumps(promoted_campaign)})")
    return subprocess.run(
        [root, "-l", "-b", "-q", "-e", f".L {MACRO}",
         "-e", f"gSystem->Exit({expression});"],
        cwd=ROOT, text=True, capture_output=True, check=False)


def expect_refusal(root: str, temp: Path, name: str, mutate, marker: str) -> None:
    manifest, production = build_freeze(temp / name, mutate=mutate)
    result = run_selection(root, manifest, production, JOBS_PER_TUNE)
    output = result.stdout + result.stderr
    if result.returncode == 0 or marker not in output:
        raise AssertionError(
            f"[{name}] the contract accepted a freeze it must refuse "
            f"(looking for {marker!r}):\n{output}")
    print(f"  refused as required: {name}")


def test_derived_shape_is_accepted(root: str, temp: Path) -> None:
    """The positive case, at a shape both retired literals would have refused."""
    manifest, production = build_freeze(temp / "good")
    result = run_selection(root, manifest, production, JOBS_PER_TUNE)
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "INCLUSIVE_RAW_DATASET_SELECTION_TEST errors=0" in output, output
    # The contract must announce what it derived, not what it assumed.
    expected = (f"tunes=3 jobs_per_tune={JOBS_PER_TUNE} "
                f"events_per_job={EVENTS_PER_JOB} "
                f"events_per_tune={JOBS_PER_TUNE * EVENTS_PER_JOB} "
                f"rows={len(TUNES) * JOBS_PER_TUNE} blocks={BLOCKS}")
    assert expected in output, f"derived shape not reported:\n{output}"
    assert "shape=derived" in output, output
    # Absent campaign-level validation is reported as absent, never as passed.
    assert "validation_log=absent" in output, output
    print("  accepted, and reported a derived shape:", expected)


def test_a_freeze_from_another_campaign_is_refused(root: str, temp: Path) -> None:
    """The identity chain: selector -> campaign -> these rows.

    Rows agreeing with each other is not the same as belonging to the dataset
    the selector promoted. HADRONIZATION_CANONICAL_MANIFEST is only a path, so
    without this check any OTHER campaign's correctly sealed freeze -- correct
    seal, correct digests, internally consistent, every assertion above
    satisfied -- would render under this dataset's publication authorization.

    This is the one case the other eight cannot catch, because nothing about
    the freeze is malformed. It is simply the wrong freeze.
    """
    manifest, production = build_freeze(temp / "other_campaign")
    result = run_selection(root, manifest, production, JOBS_PER_TUNE,
                           promoted_campaign="HF_RUN3_V1")
    output = result.stdout + result.stderr
    if result.returncode == 0 or "but the selector promoted" not in output:
        raise AssertionError(
            "a valid freeze from a different campaign was accepted under this "
            f"dataset's authorization:\n{output}")
    print("  refused as required: freeze_from_another_campaign")


def main() -> int:
    root = shutil.which("root")
    if root is None:
        raise RuntimeError("ROOT is required for the freeze-contract test")

    with tempfile.TemporaryDirectory() as tmp:
        temp = Path(tmp)
        test_derived_shape_is_accepted(root, temp)
        test_a_freeze_from_another_campaign_is_refused(root, temp)

        def drop_seal(rows, seal):
            seal.clear()          # written, but empty: no schema, no digests
        expect_refusal(root, temp, "empty_seal", drop_seal,
                       "Canonical freeze seal disagrees with its own manifest")

        def tamper_seal_digest(rows, seal):
            seal["canonical_manifest_sha256"] = "0" * 64
        expect_refusal(root, temp, "tampered_seal_digest", tamper_seal_digest,
                       "Canonical freeze seal disagrees with its own manifest")

        def wrong_row_count(rows, seal):
            seal["rows"] = len(rows) + 1
        expect_refusal(root, temp, "seal_row_count", wrong_row_count,
                       "Canonical freeze seal disagrees with its own manifest")

        def wrong_exposure(rows, seal):
            seal["total_requested_successes"] = 1
        expect_refusal(root, temp, "seal_exposure", wrong_exposure,
                       "Canonical freeze seal disagrees with its own manifest")

        def non_uniform_events(rows, seal):
            rows[0]["requested_successes"] = EVENTS_PER_JOB * 2
        expect_refusal(root, temp, "non_uniform_events", non_uniform_events,
                       "non-uniform requested_successes")

        def unequal_tunes(rows, seal):
            del rows[-1]          # one tune is now one job short
        expect_refusal(root, temp, "unequal_tunes", unequal_tunes,
                       "unequal per-tune exposure")

        def missing_per_job_evidence(rows, seal):
            rows[5]["raw_validation_receipt_sha256"] = ""
        expect_refusal(root, temp, "no_per_job_evidence", missing_per_job_evidence,
                       "Invalid or duplicate canonical manifest row")

        def duplicate_slot(rows, seal):
            rows[1]["canonical_slot"] = rows[0]["canonical_slot"]
            rows[1]["block"] = rows[0]["block"]
        expect_refusal(root, temp, "duplicate_slot", duplicate_slot,
                       "Invalid or duplicate canonical manifest row")

        def tampered_raw_digest(rows, seal):
            rows[0]["raw_sha256"] = "c" * 64
        expect_refusal(root, temp, "tampered_raw_digest", tampered_raw_digest,
                       "checksum differs from the sealed manifest")

    print("canonical freeze-contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
