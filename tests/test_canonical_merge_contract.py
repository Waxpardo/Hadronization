#!/usr/bin/env python3
"""Check dynamic N>=100, equal-tune, ten-block merge sizing."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/canonical_merge_contract.py"
PROVENANCE_PATH = ROOT / "tools/merged_pair_provenance.py"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


def load_module():
    specification = importlib.util.spec_from_file_location(
        "canonical_merge_contract_test", MODULE_PATH
    )
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )


def make_freeze(
    path: Path, jobs_per_tune: int = 110, *, superseding: bool = True
) -> None:
    rows = []
    for tune in TUNES:
        for slot in range(jobs_per_tune):
            if superseding:
                source = "parent_100" if slot < 100 else "extension_10"
                source_slot = slot if slot < 100 else slot - 100
                row = {
                    "schema": "hf_superseding_canonical_raw_manifest_v3",
                    "campaign": source,
                    "final_campaign": "extension_10",
                    "final_campaign_ordinal": 12,
                    "source_production_prefix": source,
                    "source_canonical_slot": source_slot,
                    "source_manifest_sha256":
                        ("1" if source == "parent_100" else "4") * 64,
                    "source_freeze_summary_sha256":
                        ("2" if source == "parent_100" else "5") * 64,
                    "source_freeze_seal_sha256":
                        ("3" if source == "parent_100" else "6") * 64,
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
                    "requested_successes": 1_000_000,
                    "identity": f"{tune}:{slot}",
                }
            )
            rows.append(row)
    write_jsonl(path / "canonical_manifest.jsonl", rows)
    for block in range(10):
        write_jsonl(
            path / f"block_{block + 1:02d}.jsonl",
            [row for row in rows if row["block"] == block],
        )


def main() -> int:
    module = load_module()
    provenance_specification = importlib.util.spec_from_file_location(
        "merged_pair_provenance_test", PROVENANCE_PATH
    )
    assert provenance_specification and provenance_specification.loader
    provenance = importlib.util.module_from_spec(provenance_specification)
    provenance_specification.loader.exec_module(provenance)
    with tempfile.TemporaryDirectory(
        prefix="hadronization_canonical_merge_contract_"
    ) as raw:
        freeze = Path(raw)
        make_freeze(freeze)
        report = module.validate(freeze)
        assert report["jobs_per_tune"] == 110
        assert report["jobs_per_tune_per_block"] == 11
        assert report["successful_events_per_tune"] == 110_000_000
        assert report["campaign"] == "extension_10"
        assert report["source_campaigns"] == ["extension_10", "parent_100"]
        central_scope = provenance.source_manifest_scope(
            freeze / "canonical_manifest.jsonl", "MONASH", 110
        )
        assert central_scope == {
            "source_manifest_scope":
                "all_tunes_with_explicit_tune_filter_v1",
            "source_manifest_total_rows": 330,
            "source_manifest_tune_counts": {
                "MONASH": 110,
                "JUNCTIONS": 110,
                "CLOSEPACKING": 110,
            },
            "selected_tune": "MONASH",
            "selected_tune_input_file_count": 110,
        }
        block_scope = provenance.source_manifest_scope(
            freeze / "block_01.jsonl", "CLOSEPACKING", 11
        )
        assert block_scope["source_manifest_total_rows"] == 33

        block = freeze / "block_01.jsonl"
        rows = [
            json.loads(line)
            for line in block.read_text().splitlines()
            if line.strip()
        ]
        rows[0]["requested_successes"] += 1
        write_jsonl(block, rows)
        try:
            module.validate(freeze)
        except ValueError:
            pass
        else:
            raise AssertionError("unequal/tampered block exposure was accepted")

        first_stage = Path(raw) / "first_stage"
        first_stage.mkdir()
        make_freeze(first_stage, 100, superseding=False)
        first_report = module.validate(first_stage)
        assert first_report["jobs_per_tune"] == 100
        assert first_report["campaign"] == "first_stage_100"
        assert first_report["source_campaigns"] == ["first_stage_100"]
        linked = Path(raw) / "linked_freeze"
        linked.symlink_to(first_stage, target_is_directory=True)
        try:
            module.validate(linked)
        except ValueError as error:
            assert "symbolic link" in str(error)
        else:
            raise AssertionError("symlinked canonical freeze was accepted")

        invalid = Path(raw) / "invalid_source"
        invalid.mkdir()
        make_freeze(invalid)
        central_rows = [
            json.loads(line)
            for line in (invalid / "canonical_manifest.jsonl")
            .read_text()
            .splitlines()
            if line.strip()
        ]
        central_rows[0]["source_freeze_seal_sha256"] = "7" * 64
        write_jsonl(invalid / "canonical_manifest.jsonl", central_rows)
        try:
            module.validate(invalid)
        except ValueError as error:
            assert "source-freeze identity" in str(error)
        else:
            raise AssertionError(
                "inconsistent superseding source provenance was accepted"
            )

        unequal_source = Path(raw) / "unequal_source_exposure"
        unequal_source.mkdir()
        make_freeze(unequal_source)
        central_rows = [
            json.loads(line)
            for line in (unequal_source / "canonical_manifest.jsonl")
            .read_text()
            .splitlines()
            if line.strip()
        ]
        central_rows[0].update(
            {
                "campaign": "extension_10",
                "source_production_prefix": "extension_10",
                "source_canonical_slot": 10,
                "source_manifest_sha256": "4" * 64,
                "source_freeze_summary_sha256": "5" * 64,
                "source_freeze_seal_sha256": "6" * 64,
            }
        )
        write_jsonl(
            unequal_source / "canonical_manifest.jsonl", central_rows
        )
        try:
            module.validate(unequal_source)
        except ValueError as error:
            assert "unequal tune exposure" in str(error)
        else:
            raise AssertionError(
                "unequal leaf-source tune exposure was accepted"
            )

    print("canonical dynamic merge-contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
