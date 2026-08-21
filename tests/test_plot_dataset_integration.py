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
# Deliberately NOT 1_000_000: the retired contract hardcoded that value,
# so a fixture using it could not tell a derived shape from a lucky match.
EVENTS_PER_JOB = 250_000


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
                    "seed": TUNES.index(tune) * 100000 + slot,
                    # The per-job validation evidence the narrowed contract
                    # relies on in place of a campaign-level receipt.
                    "attempt_receipt_path":
                        f"attempt_metadata/{tune}/job{slot:03d}.json",
                    "raw_validation_log_path":
                        f"raw_validation/{tune}/job{slot:03d}/validate.log",
                    "raw_validation_log_sha256": "a" * 64,
                    "raw_validation_receipt_path":
                        f"raw_validation/{tune}/job{slot:03d}/receipt.json",
                    "raw_validation_receipt_sha256": "b" * 64,
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

    # A union freeze's rows carry source-binding fields; the seal records the
    # union digest. Kept because the fixture still exercises that row shape.
    source_freezes = [
        {"campaign": "parent_100", "jobs_in_final_union_per_tune": 100,
         "canonical_manifest_sha256": "1" * 64},
        {"campaign": "extension_10",
         "jobs_in_final_union_per_tune": jobs_per_tune - 100,
         "canonical_manifest_sha256": "4" * 64},
    ]
    source_sha = hashlib.sha256(
        json.dumps(source_freezes, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    supersedes = {
        "parent_campaign": "parent_100",
        "extension_campaign": "extension_10",
    }
    # freeze_summary.json and canonical_raw_validation_receipt.json are NOT
    # written. Nothing in the repository produces them, and the narrowed
    # contract does not ask for them; a fixture that invents them would be
    # testing a ceremony rather than the seal.
    # The seal carries the campaign shape, and the plotting validators read it
    # from here instead of hardcoding one. These are the same fields
    # tools/build_canonical_manifest.py:306-320 writes for a real campaign;
    # the fixture used to omit them, which is why the 100-job/1M-event
    # literals in the validators went unnoticed.
    seal_payload = {
            "schema": "hf_canonical_freeze_seal_v2",
            "state": "SEALED",
            "campaign": "extension_10" if superseding else "first_stage_100",
            "canonical_manifest_sha256": manifest_sha,
            "rows": len(rows),
            "tunes": list(TUNES),
            "jobs_per_tune": jobs_per_tune,
            "blocks": 10,
            "total_requested_successes": len(rows) * EVENTS_PER_JOB,
    }
    if superseding:
        seal_payload.update(
            {
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
            ROOT / "plotting/Plot_InclusiveKinematicSpectra_Raw.C"
        ).read_text()
        assert "kSharedMultiplicityLineStyle" not in inclusive_source
        assert "SetLineStyle(kSharedMultiplicityLineStyle)" not in (
            inclusive_source
        )

        run_root(
            root,
            "plotting/Plot_InclusiveKinematicSpectra_Raw.C",
            "TestInclusiveRawCanonicalManifestSelection("
            f"{json.dumps(str(manifest))},"
            f"{json.dumps(str(production))},{JOBS_PER_TUNE})"
            " || TestInclusiveRawTuneStylePreservation()",
            (
                "INCLUSIVE_RAW_DATASET_SELECTION_TEST errors=0 "
                "files_per_tune=110 reserve_discovery=false",
                # Dense curves use marker 1 while legend proxies retain tune markers.
                # Every tune line remains solid.
                "INCLUSIVE_RAW_TUNE_STYLE_TEST errors=0 "
                "mode=dense_spectrum drawn_marker=1 "
                "legend_markers=20/21/22 all_lines_solid=1",
            ),
        )
        run_root(
            root,
            "plotting/Plot_InclusiveKinematicSpectra_Raw.C",
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
            "plotting/Plot_InclusiveKinematicSpectra_Raw.C",
            "TestInclusiveRawCanonicalManifestSelection("
            f"{json.dumps(str(manifest))},"
            f"{json.dumps(str(production))},{JOBS_PER_TUNE})",
            "Canonical raw file checksum differs from the sealed manifest",
        )
        run_root(
            root,
            "plotting/Validate_THnSparse_Production.C",
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
            "plotting/Validate_THnSparse_Production.C",
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
            "plotting/"
            "Plot_MultiplicityDistribution_PercentileBoundaries.C",
            "TestMultiplicityDatasetSelectorOverrides("
            f"{json.dumps(str(ROOT / 'plotting' / 'configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json'))},"
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
