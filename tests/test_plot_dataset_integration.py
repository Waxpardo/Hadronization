#!/usr/bin/env python3
"""Exercise plotting consumers against a sealed 110-file/tune selector."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
JOBS_PER_TUNE = 110
FIRST_STAGE_JOBS_PER_TUNE = 100
EVENTS_PER_JOB = 1_000_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in rows
        )
    )


def make_sealed_selection(
    directory: Path,
    jobs_per_tune: int,
    *,
    superseding: bool,
) -> tuple[Path, Path, Path]:
    production = directory / "production"
    freeze = production / "freeze"
    freeze.mkdir(parents=True)
    rows: list[dict] = []
    for tune in TUNES:
        tune_dir = production / "raw" / tune
        tune_dir.mkdir(parents=True)
        for slot in range(jobs_per_tune):
            raw = tune_dir / f"canonical_{slot:03d}.root"
            raw.write_bytes(f"{tune}:{slot}\n".encode())
            if superseding:
                source = "parent_100" if slot < 100 else "extension_10"
                row = {
                    "schema": "hf_superseding_canonical_raw_manifest_v3",
                    "campaign": source,
                    "final_campaign": "extension_10",
                    "final_campaign_ordinal": 2,
                    "source_canonical_slot":
                        slot if slot < 100 else slot - 100,
                    "source_manifest_sha256":
                        ("1" if slot < 100 else "4") * 64,
                    "source_freeze_summary_sha256":
                        ("2" if slot < 100 else "5") * 64,
                    "source_freeze_seal_sha256":
                        ("3" if slot < 100 else "6") * 64,
                    "source_production_prefix": source,
                    "source_production_definition_sha256": "7" * 64,
                }
            else:
                row = {
                    "schema": "hf_canonical_raw_manifest_v2",
                    "campaign": "first_stage_100",
                }
            row.update(
                {
                    "tune": tune,
                    "canonical_slot": slot,
                    "block": slot % 10,
                    "block_position": slot // 10,
                    "raw_path": raw.relative_to(production).as_posix(),
                    "raw_bytes": raw.stat().st_size,
                    "raw_sha256": sha256(raw),
                    "raw_schema": "hf_primary_ground_raw_v7",
                    "selector":
                        "hard_trigger_primary_ground__"
                        "primary_ground_associate_v1",
                    "requested_successes": EVENTS_PER_JOB,
                }
            )
            rows.append(row)
        reserve = production / "raw" / tune / "reserve_unselected.root"
        reserve.write_bytes(b"must not be discovered\n")

    manifest = freeze / "canonical_manifest.jsonl"
    block = freeze / "block_01.jsonl"
    write_jsonl(manifest, rows)
    write_jsonl(block, [row for row in rows if row["block"] == 0])
    manifest_sha = sha256(manifest)

    source_freezes = [
        {
            "campaign": "parent_100",
            "production_prefix": "parent_100",
            "jobs_in_final_union_per_tune": 100,
            "canonical_manifest_sha256": "1" * 64,
            "freeze_summary_sha256": "2" * 64,
            "freeze_seal_sha256": "3" * 64,
        },
        {
            "campaign": "extension_10",
            "production_prefix": "extension_10",
            "jobs_in_final_union_per_tune": jobs_per_tune - 100,
            "canonical_manifest_sha256": "4" * 64,
            "freeze_summary_sha256": "5" * 64,
            "freeze_seal_sha256": "6" * 64,
        },
    ]
    source_sha = hashlib.sha256(
        json.dumps(
            source_freezes, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
    supersedes = {
        "parent_campaign": "parent_100",
        "extension_campaign": "extension_10",
    }
    summary = {
            "schema": (
                "hf_superseding_canonical_freeze_summary_v4"
                if superseding
                else "hf_canonical_freeze_summary_v3"
            ),
            "state": "AWAITING_EXHAUSTIVE_RAW_VALIDATION",
            "campaign": "extension_10" if superseding else "first_stage_100",
            "campaign_ordinal": 2 if superseding else 1,
            "canonical_manifest_sha256": manifest_sha,
            "jobs_per_tune": jobs_per_tune,
            "successful_events_per_job": EVENTS_PER_JOB,
            "successful_events_per_tune":
                jobs_per_tune * EVENTS_PER_JOB,
            "block_count": 10,
            "jobs_per_tune_per_block": jobs_per_tune // 10,
    }
    if superseding:
        summary.update(
            {
                "source_freezes": source_freezes,
                "source_freezes_sha256": source_sha,
                "supersedes": supersedes,
            }
        )
    write_json(freeze / "freeze_summary.json", summary)
    receipt = freeze / "canonical_raw_validation_receipt.json"
    receipt_payload = {
            "schema": (
                "hf_superseding_canonical_raw_validation_receipt_v3"
                if superseding
                else "hf_canonical_raw_validation_receipt_v2"
            ),
            "state": "PASS",
            "canonical_manifest_sha256": manifest_sha,
            "canonical_manifest_rows": len(rows),
            "validated_raw_files": len(rows),
            "validated_successful_events": len(rows) * EVENTS_PER_JOB,
    }
    if superseding:
        receipt_payload.update(
            {
                "jobs_per_tune": jobs_per_tune,
                "source_freezes_sha256": source_sha,
                "supersedes": supersedes,
            }
        )
    write_json(receipt, receipt_payload)
    seal_payload = {
            "schema": (
                "hf_superseding_canonical_freeze_seal_v3"
                if superseding
                else "hf_canonical_freeze_seal_v2"
            ),
            "state": "SEALED",
            "canonical_manifest_sha256": manifest_sha,
            "validation_receipt_path":
                "canonical_raw_validation_receipt.json",
            "validation_receipt_sha256": sha256(receipt),
    }
    if superseding:
        seal_payload.update(
            {
                "jobs_per_tune": jobs_per_tune,
                "source_freezes_sha256": source_sha,
                "supersedes": supersedes,
            }
        )
    write_json(freeze / "freeze_seal.json", seal_payload)
    return manifest, block, production


def run_root(
    root: str,
    macro: str,
    expression: str,
    markers: tuple[str, ...],
) -> None:
    result = subprocess.run(
        [
            root,
            "-l",
            "-b",
            "-q",
            "-e",
            f".L {macro}",
            "-e",
            f"gSystem->Exit({expression});",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr
    if result.returncode != 0 or any(marker not in output for marker in markers):
        raise AssertionError(
            f"ROOT plotting-selector integration test failed:\n{output}"
        )


def require_root_failure(
    root: str,
    macro: str,
    expression: str,
    marker: str,
) -> None:
    result = subprocess.run(
        [
            root,
            "-l",
            "-b",
            "-q",
            "-e",
            f".L {macro}",
            "-e",
            f"gSystem->Exit({expression});",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr
    if result.returncode == 0 or marker not in output:
        raise AssertionError(
            "ROOT plotting-selector negative test did not fail as "
            f"expected:\n{output}"
        )


def main() -> int:
    root = shutil.which("root")
    if root is None:
        raise RuntimeError(
            "ROOT is required for the plotting-selector integration test"
        )

    with tempfile.TemporaryDirectory() as temp:
        temporary = Path(temp)
        manifest, block, production = make_sealed_selection(
            temporary / "superseding",
            JOBS_PER_TUNE,
            superseding=True,
        )
        first_manifest, first_block, first_production = make_sealed_selection(
            temporary / "first_stage",
            FIRST_STAGE_JOBS_PER_TUNE,
            superseding=False,
        )
        selected_analyzed = temporary / "selected_analyzed_data"
        selected_subsamples = temporary / "selected_subsamples"
        (
            selected_analyzed
            / "MONASH"
            / "canonical_test_tag_MONASH"
        ).mkdir(parents=True)
        (selected_subsamples / "MONASH").mkdir(parents=True)
        inclusive_source = (
            ROOT / "PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C"
        ).read_text()
        assert "kSharedMultiplicityLineStyle" not in inclusive_source
        assert "SetLineStyle(kSharedMultiplicityLineStyle)" not in (
            inclusive_source
        )

        run_root(
            root,
            "PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C",
            "TestInclusiveRawCanonicalManifestSelection("
            f"{json.dumps(str(manifest))},"
            f"{json.dumps(str(production))},{JOBS_PER_TUNE})"
            " || TestInclusiveRawTuneStylePreservation()",
            (
                "INCLUSIVE_RAW_DATASET_SELECTION_TEST errors=0 "
                "files_per_tune=110 reserve_discovery=false",
                "INCLUSIVE_RAW_TUNE_STYLE_TEST errors=0 "
                "monash_line=1 junctions_line=2 closepacking_line=7",
            ),
        )
        run_root(
            root,
            "PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C",
            "TestInclusiveRawCanonicalManifestSelection("
            f"{json.dumps(str(first_manifest))},"
            f"{json.dumps(str(first_production))},"
            f"{FIRST_STAGE_JOBS_PER_TUNE})",
            (
                "INCLUSIVE_RAW_DATASET_SELECTION_TEST errors=0 "
                "files_per_tune=100 reserve_discovery=false",
            ),
        )
        tampered = production / "raw" / "MONASH" / "canonical_000.root"
        original_bytes = tampered.stat().st_size
        tampered.write_bytes(b"MONASH:X\n")
        assert tampered.stat().st_size == original_bytes
        require_root_failure(
            root,
            "PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C",
            "TestInclusiveRawCanonicalManifestSelection("
            f"{json.dumps(str(manifest))},"
            f"{json.dumps(str(production))},{JOBS_PER_TUNE})",
            "Canonical raw file checksum differs from the sealed manifest",
        )
        run_root(
            root,
            "PlottingScripts/Validate_THnSparse_Production.C",
            "TestTHnSparseCanonicalSourceManifest("
            f"{json.dumps(str(manifest))},"
            f"{json.dumps(str(block))},{JOBS_PER_TUNE})"
            " || TestTHnSparseDatasetSelectorOverrides("
            f"{json.dumps(str(selected_analyzed))},"
            '"canonical_test_tag",'
            f"{json.dumps(str(selected_subsamples))})",
            (
                "THNSPARSE_CANONICAL_MANIFEST_TEST errors=0 "
                "files_per_tune=110 files_per_block=11 "
                "pair_registry_files=300",
                "THNSPARSE_DATASET_SELECTOR_TEST errors=0 "
                "overrides=true nested_layout=true",
            ),
        )
        run_root(
            root,
            "PlottingScripts/Validate_THnSparse_Production.C",
            "TestTHnSparseCanonicalSourceManifest("
            f"{json.dumps(str(first_manifest))},"
            f"{json.dumps(str(first_block))},"
            f"{FIRST_STAGE_JOBS_PER_TUNE})",
            (
                "THNSPARSE_CANONICAL_MANIFEST_TEST errors=0 "
                "files_per_tune=100 files_per_block=10 "
                "pair_registry_files=300",
            ),
        )
        run_root(
            root,
            "PlottingScripts/"
            "Plot_MultiplicityDistribution_PercentileBoundaries.C",
            "TestMultiplicityDatasetSelectorOverrides("
            f"{json.dumps(str(ROOT / 'PlottingScripts' / 'configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json'))},"
            f"{json.dumps(str(selected_analyzed))},"
            '"canonical_test_tag")',
            (
                "MULTIPLICITY_DATASET_SELECTOR_TEST errors=0 "
                "contract_policy_enforced=true",
            ),
        )

    print("plot dataset-integration tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
