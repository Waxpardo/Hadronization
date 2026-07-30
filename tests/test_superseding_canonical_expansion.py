#!/usr/bin/env python3
"""Synthetic end-to-end checks for immutable equal-tune expansion."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


def load(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


canonical = load("superseding_canonical_test", ROOT / "tools/canonical_manifest.py")
campaign_contract = load(
    "superseding_campaign_test", ROOT / "tools/campaign_manifest.py"
)
analysis_contract = load(
    "superseding_analysis_test", ROOT / "tools/validate_analysis_outputs.py"
)
merge_contract = load(
    "superseding_merge_test", ROOT / "tools/canonical_merge_contract.py"
)
evidence_generator = load(
    "superseding_evidence_test",
    ROOT / "tools/generate_expansion_evidence.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return sha(path)


def approve_pthat_spec_for_fixture(path: Path) -> None:
    payload = json.loads(path.read_text())
    payload["scientific_review_status"] = "APPROVED_GATE_B_OWNER_REVIEW"
    payload["scientific_review"] = {
        "decision": "APPROVE_PTHAT_SENSITIVITY_SPEC",
        "reviewer": "Independent Physics Reviewer",
        "reviewer_role":
            "project_owner_or_designated_physics_statistics_reviewer",
        "decision_utc": datetime.now(timezone.utc).isoformat(),
        "rationale":
            "Synthetic approval exists only inside an isolated test checkout.",
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def create_source_freeze(
    collection: Path,
    campaign: str,
    ordinal: int,
    jobs_per_tune: int,
    seed_base: int,
    *,
    extension: bool,
) -> Path:
    production = collection / campaign
    freeze = production / ("extension_freeze" if extension else "freeze")
    freeze.mkdir(parents=True)
    rows = []
    for tune_ordinal, tune in enumerate(TUNES):
        for slot in range(jobs_per_tune):
            raw_relative = (
                Path("raw") / tune / f"hf_{tune}_job{slot:03d}.root"
            )
            raw = production / raw_relative
            raw_sha = write(raw, f"{campaign}:{tune}:{slot}".encode())
            Path(f"{raw}.sha256").write_text(f"{raw_sha}  {raw.name}\n")
            evidence = {
                "attempt_start_claim_path":
                    Path("attempt_starts") / tune / f"start_{slot:03d}.json",
                "attempt_receipt_path":
                    Path("attempt_metadata") / tune / f"attempt_{slot:03d}.json",
                "raw_validation_log_path":
                    Path("raw_validation") / tune / f"log_{slot:03d}.txt",
                "raw_validation_receipt_path":
                    Path("raw_validation") / tune / f"receipt_{slot:03d}.json",
                "allocation_authorization_path":
                    Path("submission_receipts") / f"claim_{tune}_{slot:03d}.json",
                "submission_record_path":
                    Path("submission_receipts") / f"record_{tune}_{slot:03d}.json",
            }
            evidence_sha = {}
            for key, relative in evidence.items():
                path = production / relative
                if key == "raw_validation_log_path":
                    value = (
                        "RAW_VALIDATION_SUMMARY errors=0 entries=1\n"
                    ).encode()
                elif key == "raw_validation_receipt_path":
                    log = production / evidence["raw_validation_log_path"]
                    value = (
                        json.dumps(
                            {
                                "schema": "hf_raw_validation_receipt_v1",
                                "result": "PASS",
                                "validated_utc":
                                    "2026-07-30T00:00:00+00:00",
                                "validator_exit_status": 0,
                                "validator_wrapper_sha256": "1" * 64,
                                "validator_macro_sha256": "2" * 64,
                                "validator_dependency_sha256": {
                                    "fixture.h": "3" * 64,
                                },
                                "validation_log_name": log.name,
                                "validation_log_sha256": sha(log),
                                "output_sha256": raw_sha,
                                "output_bytes": raw.stat().st_size,
                                "expected_provenance": {
                                    "campaign": campaign,
                                    "tune": tune,
                                    "logical_id": slot,
                                },
                            },
                            sort_keys=True,
                        )
                        + "\n"
                    ).encode()
                else:
                    value = f"{key}:{campaign}:{tune}:{slot}".encode()
                evidence_sha[key.replace("_path", "_sha256")] = write(
                    path, value
                )
            row = {
                "schema": (
                    canonical.EXTENSION_ROW_SCHEMA
                    if extension
                    else canonical.ROW_SCHEMA
                ),
                "campaign": campaign,
                "campaign_ordinal": ordinal,
                "tune": tune,
                "tune_ordinal": tune_ordinal,
                "canonical_slot": slot,
                "block": slot % 10,
                "block_position": slot // 10,
                "logical_id": slot,
                "role": "primary",
                "attempt": 0,
                "seed": seed_base + tune_ordinal * 10_000 + slot,
                "requested_successes": 1_000_000,
                "pthat_min_override": "NONE",
                "effective_pthat_min": 1.0,
                "multiplicity_audit_events": 0,
                "effective_card_sha256": f"{tune_ordinal + 1:x}" * 64,
                "producer_executable_sha256": "4" * 64,
                "repository_commit": "5" * 40,
                "raw_schema": canonical.RAW_SCHEMA,
                "origin_algorithm": canonical.ORIGIN_ALGORITHM,
                "selector": canonical.SELECTOR,
                "species_registry_sha256": "6" * 64,
                "pair_registry_sha256": "7" * 64,
                "tune_difference_allowlist_schema":
                    canonical.TUNE_ALLOWLIST_SCHEMA,
                "tune_difference_allowlist_sha256": "8" * 64,
                "raw_path": raw_relative.as_posix(),
                "raw_bytes": raw.stat().st_size,
                "raw_sha256": raw_sha,
                **{key: value.as_posix() for key, value in evidence.items()},
                **evidence_sha,
                "producing_cluster_id": f"cluster{tune_ordinal}",
                "producing_process_id": str(slot),
                "validation_receipt_path":
                    canonical.VALIDATION_RECEIPT_NAME,
                "selection_reason": "lowest_valid_primary_logical_id",
                "selection_approval": "technical_evidence_only",
            }
            row["production_definition_sha256"] = (
                canonical.production_definition(row)
            )
            rows.append(row)
    manifest = freeze / "canonical_manifest.jsonl"
    manifest.write_text(canonical.jsonl_text(rows))
    block_hashes = {}
    for block in range(10):
        block_path = freeze / f"block_{block + 1:02d}.jsonl"
        block_path.write_text(
            canonical.jsonl_text(
                [row for row in rows if row["block"] == block]
            )
        )
        block_hashes[block_path.name] = sha(block_path)
    summary = {
        "schema": (
            canonical.EXTENSION_SUMMARY_SCHEMA
            if extension
            else canonical.SUMMARY_SCHEMA
        ),
        "state": "AWAITING_EXHAUSTIVE_RAW_VALIDATION",
        "campaign": campaign,
        "campaign_ordinal": ordinal,
        "canonical_manifest_sha256": sha(manifest),
        "block_manifest_sha256": block_hashes,
        "jobs_per_tune": jobs_per_tune,
        "successful_events_per_job": 1_000_000,
        "successful_events_per_tune": jobs_per_tune * 1_000_000,
        "block_count": 10,
        "jobs_per_tune_per_block": jobs_per_tune // 10,
        "raw_schema": canonical.RAW_SCHEMA,
        "origin_algorithm": canonical.ORIGIN_ALGORITHM,
        "selector": canonical.SELECTOR,
        "species_registry_sha256": "6" * 64,
        "pair_registry_sha256": "7" * 64,
        "tune_difference_allowlist_schema": canonical.TUNE_ALLOWLIST_SCHEMA,
        "tune_difference_allowlist_sha256": "8" * 64,
        "submission_claim_path":
            "submission_receipts/full_candidates_attempt0_submission_claim.json",
        "submission_claim_sha256": "9" * 64,
        "submission_record_path":
            "submission_receipts/full_candidates_attempt0_submitted.json",
        "submission_record_sha256": "a" * 64,
        "physics_origin_signoff_sha256": "b" * 64,
        "full_production_gate_authorization_sha256": "c" * 64,
        "registry_baseline_sha256": "d" * 64,
        "global_submission_claim_sha256": "e" * 64,
        "campaign_json_sha256": "1" * 64,
        "candidate_manifest_sha256": "2" * 64,
        "seed_ledger_sha256": "3" * 64,
        "repository_implementation_commit": "5" * 40,
        "validation_receipt_path": canonical.VALIDATION_RECEIPT_NAME,
        "seal_path": canonical.SEAL_NAME,
    }
    if extension:
        summary.update(
            {
                "campaign_kind": canonical.EXPANSION_CAMPAIGN_KIND,
                "primary_logical_ids_per_tune": jobs_per_tune,
                "planned_final_jobs_per_tune": 100 + jobs_per_tune,
                "supersedes": {"synthetic": True},
                "equal_tune_expansion_authorization_sha256": "f" * 64,
            }
        )
    summary_path = freeze / "freeze_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    log = freeze / canonical.VALIDATION_LOG_NAME
    log.write_text(
        "CANONICAL_RAW_VALIDATION errors=0 "
        f"files={len(rows)} unique_seeds={len(rows)} "
        f"total_events={len(rows) * 1_000_000}\n"
    )
    receipt = {
        "schema": (
            canonical.EXTENSION_VALIDATION_RECEIPT_SCHEMA
            if extension
            else canonical.VALIDATION_RECEIPT_SCHEMA
        ),
        "state": "PASS",
        "canonical_manifest_sha256": sha(manifest),
        "canonical_manifest_rows": len(rows),
        "validation_log_sha256": sha(log),
        "submission_claim_sha256": summary["submission_claim_sha256"],
        "submission_record_sha256": summary["submission_record_sha256"],
        "physics_origin_signoff_sha256":
            summary["physics_origin_signoff_sha256"],
        "full_production_gate_authorization_sha256":
            summary["full_production_gate_authorization_sha256"],
        "registry_baseline_sha256": summary["registry_baseline_sha256"],
        "global_submission_claim_sha256":
            summary["global_submission_claim_sha256"],
    }
    if extension:
        receipt["equal_tune_expansion_authorization_sha256"] = (
            summary["equal_tune_expansion_authorization_sha256"]
        )
    receipt_path = freeze / canonical.VALIDATION_RECEIPT_NAME
    receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n")
    seal = {
        "schema": (
            canonical.EXTENSION_SEAL_SCHEMA
            if extension
            else canonical.SEAL_SCHEMA
        ),
        "state": "SEALED",
        "canonical_manifest_sha256": sha(manifest),
        "validation_receipt_path": canonical.VALIDATION_RECEIPT_NAME,
        "validation_receipt_sha256": sha(receipt_path),
        "validation_log_path": canonical.VALIDATION_LOG_NAME,
        "validation_log_sha256": sha(log),
        "physics_origin_signoff_sha256":
            summary["physics_origin_signoff_sha256"],
        "full_production_gate_authorization_sha256":
            summary["full_production_gate_authorization_sha256"],
        "registry_baseline_sha256": summary["registry_baseline_sha256"],
        "global_submission_claim_sha256":
            summary["global_submission_claim_sha256"],
    }
    if extension:
        seal["equal_tune_expansion_authorization_sha256"] = (
            summary["equal_tune_expansion_authorization_sha256"]
        )
    (freeze / canonical.SEAL_NAME).write_text(
        json.dumps(seal, sort_keys=True) + "\n"
    )
    canonical.validate_directory(freeze, require_seal=True)
    return freeze


def rebuild_freeze(freeze: Path, rows: list[dict]) -> None:
    manifest = freeze / "canonical_manifest.jsonl"
    manifest.write_text(canonical.jsonl_text(rows))
    summary_path = freeze / "freeze_summary.json"
    summary = json.loads(summary_path.read_text())
    summary["canonical_manifest_sha256"] = sha(manifest)
    for block in range(10):
        path = freeze / f"block_{block + 1:02d}.jsonl"
        path.write_text(
            canonical.jsonl_text(
                [row for row in rows if row["block"] == block]
            )
        )
        summary["block_manifest_sha256"][path.name] = sha(path)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    receipt_path = freeze / canonical.VALIDATION_RECEIPT_NAME
    receipt = json.loads(receipt_path.read_text())
    receipt["canonical_manifest_sha256"] = sha(manifest)
    receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n")
    seal_path = freeze / canonical.SEAL_NAME
    seal = json.loads(seal_path.read_text())
    seal["canonical_manifest_sha256"] = sha(manifest)
    seal["validation_receipt_sha256"] = sha(receipt_path)
    seal_path.write_text(json.dumps(seal, sort_keys=True) + "\n")
    canonical.validate_directory(freeze, require_seal=True)


def seal_superseding_fixture(freeze: Path) -> None:
    rows = canonical.read_jsonl(freeze / "canonical_manifest.jsonl")
    summary = json.loads((freeze / "freeze_summary.json").read_text())
    log = freeze / canonical.VALIDATION_LOG_NAME
    log.write_text(
        "CANONICAL_RAW_VALIDATION errors=0 "
        f"files={len(rows)} unique_seeds={len(rows)} "
        f"total_events={len(rows) * 1_000_000}\n"
    )
    receipt = {
        "schema": canonical.SUPERSEDING_VALIDATION_RECEIPT_SCHEMA,
        "state": "PASS",
        "canonical_manifest_sha256": sha(
            freeze / "canonical_manifest.jsonl"
        ),
        "canonical_manifest_rows": len(rows),
        "validation_log_sha256": sha(log),
        "submission_claim_sha256": summary["submission_claim_sha256"],
        "submission_record_sha256": summary["submission_record_sha256"],
        "physics_origin_signoff_sha256":
            summary["physics_origin_signoff_sha256"],
        "full_production_gate_authorization_sha256":
            summary["full_production_gate_authorization_sha256"],
        "registry_baseline_sha256": summary["registry_baseline_sha256"],
        "global_submission_claim_sha256":
            summary["global_submission_claim_sha256"],
        "equal_tune_expansion_authorization_sha256":
            summary["equal_tune_expansion_authorization_sha256"],
        "jobs_per_tune": summary["jobs_per_tune"],
        "source_freezes_sha256": summary["source_freezes_sha256"],
        "supersedes": summary["supersedes"],
    }
    receipt_path = freeze / canonical.VALIDATION_RECEIPT_NAME
    receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n")
    seal = {
        "schema": canonical.SUPERSEDING_SEAL_SCHEMA,
        "state": "SEALED",
        "canonical_manifest_sha256": sha(
            freeze / "canonical_manifest.jsonl"
        ),
        "validation_receipt_path": canonical.VALIDATION_RECEIPT_NAME,
        "validation_receipt_sha256": sha(receipt_path),
        "validation_log_path": canonical.VALIDATION_LOG_NAME,
        "validation_log_sha256": sha(log),
        "physics_origin_signoff_sha256":
            summary["physics_origin_signoff_sha256"],
        "full_production_gate_authorization_sha256":
            summary["full_production_gate_authorization_sha256"],
        "registry_baseline_sha256": summary["registry_baseline_sha256"],
        "global_submission_claim_sha256":
            summary["global_submission_claim_sha256"],
        "equal_tune_expansion_authorization_sha256":
            summary["equal_tune_expansion_authorization_sha256"],
        "jobs_per_tune": summary["jobs_per_tune"],
        "source_freezes_sha256": summary["source_freezes_sha256"],
        "supersedes": summary["supersedes"],
    }
    (freeze / canonical.SEAL_NAME).write_text(
        json.dumps(seal, sort_keys=True) + "\n"
    )
    canonical.validate_directory(freeze, require_seal=True)


def create_child_campaign(
    checkout: Path,
    parent: Path,
    extension: Path,
    additional: int,
) -> Path:
    parent_identity = canonical.source_freeze_identity(parent)
    extension_summary = json.loads((extension / "freeze_summary.json").read_text())
    campaign = extension_summary["campaign"]
    campaign_dir = checkout / "campaigns" / campaign
    campaign_dir.mkdir(parents=True)
    config = {
        "schema": "hf_campaign_v1",
        "campaign_kind": canonical.EXPANSION_CAMPAIGN_KIND,
        "campaign": campaign,
        "campaign_ordinal": extension_summary["campaign_ordinal"],
        "repository_commit": "5" * 40,
        "planned_additional_jobs_per_tune": additional,
        "planned_final_jobs_per_tune":
            parent_identity["jobs_per_tune"] + additional,
        "candidate_slots": {
            "MONASH": additional,
            "JUNCTIONS": 2 * additional,
            "CLOSEPACKING": 2 * additional,
        },
        "global_offsets": {
            "MONASH": 0,
            "JUNCTIONS": additional,
            "CLOSEPACKING": 3 * additional,
        },
        "supersedes": {
            "campaign": parent_identity["campaign"],
            "campaign_ordinal": parent_identity["campaign_ordinal"],
            "jobs_per_tune": parent_identity["jobs_per_tune"],
            "canonical_manifest_sha256":
                parent_identity["canonical_manifest_sha256"],
            "freeze_summary_sha256":
                parent_identity["freeze_summary_sha256"],
            "freeze_seal_sha256": parent_identity["freeze_seal_sha256"],
            "freeze_path":
                f"Production/{parent_identity['campaign']}/freeze",
        },
    }
    (campaign_dir / "campaign.json").write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n"
    )
    (campaign_dir / "candidate_manifest.jsonl").write_text("{}\n")
    (campaign_dir / "seed_ledger.jsonl").write_text("{}\n")
    return campaign_dir


def initialize_checkout(checkout: Path) -> None:
    (checkout / "AnalysisScripts").mkdir(parents=True)
    (checkout / "AnalysisScripts/status_analysis_THnSparse_qq.C").write_text(
        "// synthetic analysis macro\n"
    )
    (checkout / "run_status_analysis.sh").write_text("#!/bin/sh\n")
    subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Expansion Contract"],
        cwd=checkout,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "expansion@example.invalid"],
        cwd=checkout,
        check=True,
    )
    subprocess.run(["git", "add", "."], cwd=checkout, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "fixture"], cwd=checkout, check=True
    )


def build_union(base: Path, additional: int) -> tuple[Path, Path, Path]:
    checkout = base / "checkout"
    initialize_checkout(checkout)
    collection = checkout / "Production"
    parent = create_source_freeze(
        collection, "parent_100", 31, 100, 10_000_000, extension=False
    )
    extension = create_source_freeze(
        collection,
        f"extension_{additional}",
        32 + additional,
        additional,
        20_000_000 + additional * 100,
        extension=True,
    )
    create_child_campaign(checkout, parent, extension, additional)
    canonical.REPOSITORY_ROOT = checkout
    canonical.require_clean_checkout = lambda: "5" * 40
    canonical.require_ancestor = lambda ancestor, descendant: None
    output = collection / f"extension_{additional}" / "freeze"
    canonical.supersede(
        Namespace(
            parent_freeze=parent,
            extension_freeze=extension,
            production_collection_root=collection,
            output_dir=output,
        )
    )
    return checkout, collection, output


def test_dynamic_campaign_contract() -> None:
    config = {
        "schema": "hf_campaign_v1",
        "campaign_kind": campaign_contract.EQUAL_TUNE_EXPANSION_KIND,
        "planned_additional_jobs_per_tune": 10,
        "candidate_slots": {
            "MONASH": 10,
            "JUNCTIONS": 20,
            "CLOSEPACKING": 20,
        },
        "global_offsets": {
            "MONASH": 0,
            "JUNCTIONS": 10,
            "CLOSEPACKING": 30,
        },
        "seed_base": 600_000_001,
        "max_attempts_per_logical_id": 100,
    }
    slots, offsets, primary = campaign_contract.campaign_slot_contract(config)
    assert slots == config["candidate_slots"]
    assert offsets == config["global_offsets"]
    assert primary == 10
    seeds = {
        campaign_contract.campaign_logical_seed(config, tune, logical_id, 0)
        for tune in TUNES
        for logical_id in range(slots[tune])
    }
    assert len(seeds) == 50
    bad = dict(config)
    bad["candidate_slots"] = dict(config["candidate_slots"], JUNCTIONS=19)
    try:
        campaign_contract.campaign_slot_contract(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("unequal/tampered expansion candidate scope accepted")


def test_lowest_valid_selection_policy() -> None:
    rows: list[dict] = []
    technically_valid: dict[str, set[int]] = {}
    for tune in TUNES:
        valid_primary = set(range(10)) - {2, 6}
        valid_reserve = {10, 11, 12}
        technically_valid[tune] = valid_primary | valid_reserve
        for logical_id in sorted(valid_primary):
            rows.append(
                {
                    "tune": tune,
                    "canonical_slot": logical_id,
                    "logical_id": logical_id,
                    "role": "primary",
                }
            )
        rows.extend(
            [
                {
                    "tune": tune,
                    "canonical_slot": 2,
                    "logical_id": 10,
                    "role": "reserve",
                },
                {
                    "tune": tune,
                    "canonical_slot": 6,
                    "logical_id": 11,
                    "role": "reserve",
                },
            ]
        )
    canonical.validate_lowest_valid_selection(
        rows, technically_valid, 10, 10
    )

    nonlowest = [dict(row) for row in rows]
    replacement = next(
        row
        for row in nonlowest
        if row["tune"] == "JUNCTIONS" and row["canonical_slot"] == 6
    )
    replacement["logical_id"] = 12
    try:
        canonical.validate_lowest_valid_selection(
            nonlowest, technically_valid, 10, 10
        )
    except ValueError as error:
        assert "lowest-valid" in str(error)
    else:
        raise AssertionError("non-lowest valid reserve was accepted")

    reordered = [dict(row) for row in rows]
    primary = next(
        row
        for row in reordered
        if row["tune"] == "MONASH" and row["logical_id"] == 3
    )
    primary["canonical_slot"] = 4
    try:
        canonical.validate_lowest_valid_selection(
            reordered, technically_valid, 10, 10
        )
    except ValueError as error:
        assert "reordered" in str(error)
    else:
        raise AssertionError("valid primary was reordered")


def test_generated_expansion_candidate_scope(base: Path) -> None:
    checkout = base / "generated_expansion_checkout"
    (checkout / "config").mkdir(parents=True)
    (checkout / "SimulationScripts").mkdir()
    (checkout / "tools").mkdir()
    for name in (
        "heavy_flavour_species_v1.json",
        "heavy_flavour_pair_registry_v1.json",
        "tune_difference_allowlist_v1.json",
        "pthat_sensitivity_v1.json",
    ):
        shutil.copy2(ROOT / "config" / name, checkout / "config" / name)
    approve_pthat_spec_for_fixture(
        checkout / "config/pthat_sensitivity_v1.json"
    )
    for tune in TUNES:
        card = f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
        shutil.copy2(
            ROOT / "SimulationScripts" / card,
            checkout / "SimulationScripts" / card,
        )
    shutil.copy2(
        ROOT / "tools/canonical_manifest.py",
        checkout / "tools/canonical_manifest.py",
    )
    shutil.copy2(
        ROOT / "tools/evaluate_pthat_sensitivity.py",
        checkout / "tools/evaluate_pthat_sensitivity.py",
    )
    shutil.copy2(
        ROOT / "tools/generate_expansion_evidence.py",
        checkout / "tools/generate_expansion_evidence.py",
    )
    initialize_checkout(checkout)
    parent = create_source_freeze(
        checkout / "Production",
        "generated_parent_100",
        81,
        100,
        50_000_000,
        extension=False,
    )
    subprocess.run(["git", "add", "Production"], cwd=checkout, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "sealed parent fixture"],
        cwd=checkout,
        check=True,
    )
    campaign_name = "generated_extension_10"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/campaign_manifest.py"),
            "generate-expansion",
            "--root",
            str(checkout),
            "--campaign",
            campaign_name,
            "--campaign-ordinal",
            "82",
            "--seed-base",
            "600000001",
            "--max-attempts",
            "100",
            "--parent-freeze",
            str(parent),
            "--additional-jobs-per-tune",
            "10",
        ],
        check=True,
    )
    campaign_dir = checkout / "campaigns" / campaign_name
    config = json.loads((campaign_dir / "campaign.json").read_text())
    rows = canonical.read_jsonl(
        campaign_dir / "candidate_manifest.jsonl"
    )
    assert len(rows) == 50
    assert [row["global_candidate_ordinal"] for row in rows] == list(
        range(50)
    )
    assert len({row["seed"] for row in rows}) == 50
    for row in rows:
        assert row["seed"] == campaign_contract.campaign_logical_seed(
            config,
            row["tune"],
            row["logical_id"],
            row["attempt"],
        )
    rows[-1]["global_candidate_ordinal"] = 300
    (campaign_dir / "candidate_manifest.jsonl").write_text(
        canonical.jsonl_text(rows)
    )
    rejected = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/campaign_manifest.py"),
            "validate",
            str(campaign_dir),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected.returncode != 0
    assert "global_candidate_ordinal" in (
        rejected.stdout + rejected.stderr
    )


def test_owner_expansion_authorization(base: Path) -> None:
    checkout = (base / "authorization_checkout").resolve()
    (checkout / "tools").mkdir(parents=True)
    for name in (
        "canonical_manifest.py",
        "generate_expansion_evidence.py",
    ):
        shutil.copy2(ROOT / "tools" / name, checkout / "tools" / name)
    initialize_checkout(checkout)
    checkout_commit = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    collection = checkout / "Production"
    parent = create_source_freeze(
        collection, "authorization_parent_100", 76, 100, 70_000_000,
        extension=False,
    )
    parent_identity = canonical.source_freeze_identity(parent)
    campaign_dir = checkout / "campaigns" / "expansion_auth"
    evidence = checkout / "ValidationReports"
    campaign_dir.mkdir(parents=True)
    evidence.mkdir()
    config = {
        "schema": "hf_campaign_v1",
        "campaign_kind": campaign_contract.EQUAL_TUNE_EXPANSION_KIND,
        "campaign": "expansion_auth",
        "campaign_ordinal": 77,
        "repository_commit": checkout_commit,
        "planned_additional_jobs_per_tune": 10,
        "planned_final_jobs_per_tune": 110,
        "candidate_slots": {
            "MONASH": 10,
            "JUNCTIONS": 20,
            "CLOSEPACKING": 20,
        },
        "global_offsets": {
            "MONASH": 0,
            "JUNCTIONS": 10,
            "CLOSEPACKING": 30,
        },
        "seed_base": 700_000_001,
        "max_attempts_per_logical_id": 100,
        "supersedes": {
            "campaign": parent_identity["campaign"],
            "campaign_ordinal": parent_identity["campaign_ordinal"],
            "jobs_per_tune": parent_identity["jobs_per_tune"],
            "canonical_manifest_sha256":
                parent_identity["canonical_manifest_sha256"],
            "freeze_summary_sha256":
                parent_identity["freeze_summary_sha256"],
            "freeze_seal_sha256": parent_identity["freeze_seal_sha256"],
            "freeze_path":
                "Production/authorization_parent_100/freeze",
        },
    }
    campaign_json = campaign_dir / "campaign.json"
    candidate = campaign_dir / "candidate_manifest.jsonl"
    ledger = campaign_dir / "seed_ledger.jsonl"
    campaign_json.write_text(json.dumps(config) + "\n")
    candidates = []
    initial_allocations = []
    for tune in TUNES:
        for logical_id in range(config["candidate_slots"][tune]):
            seed = campaign_contract.campaign_logical_seed(
                config, tune, logical_id, 0
            )
            candidates.append(
                {
                    "campaign": config["campaign"],
                    "tune": tune,
                    "logical_id": logical_id,
                    "attempt": 0,
                    "seed": seed,
                }
            )
            initial_allocations.append(
                {
                    "campaign": config["campaign"],
                    "tune": tune,
                    "logical_id": logical_id,
                    "attempt": 0,
                    "seed": seed,
                    "allocation": "initial",
                }
            )
    candidate.write_text(canonical.jsonl_text(candidates))
    ledger.write_text(canonical.jsonl_text(initial_allocations))
    initial_ledger_bytes = ledger.read_bytes()
    coverage_spec = evidence / "coverage_spec.json"
    coverage_spec.write_text(
        json.dumps(
            {
                "schema": evidence_generator.COVERAGE_SPEC_SCHEMA,
                "frozen": True,
                "selection_rule": evidence_generator.SELECTION_RULE,
                "observables": [
                    {
                        "name": "beauty:0-1",
                        "minimum_finite_subsamples": 10,
                        "minimum_effective_entries": 100,
                        "maximum_relative_sem": 0.2,
                    },
                    {
                        "name": "charm:0-1",
                        "minimum_finite_subsamples": 10,
                        "minimum_effective_entries": 100,
                        "maximum_relative_sem": 0.2,
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    coverage_matrix = evidence / "coverage_matrix.json"
    coverage_matrix.write_text(
        json.dumps(
            {
                "schema": evidence_generator.COVERAGE_MATRIX_SCHEMA,
                "state": "COMPLETE",
                "canonical_manifest_sha256":
                    parent_identity["canonical_manifest_sha256"],
                "jobs_per_tune": 100,
                "observations": [
                    {
                        "name": "beauty:0-1",
                        "central_value": 1.0,
                        "std_error": 0.3,
                        "finite_subsamples": 10,
                        "effective_entries": 200,
                    },
                    {
                        "name": "charm:0-1",
                        "central_value": 1.0,
                        "std_error": 0.1,
                        "finite_subsamples": 10,
                        "effective_entries": 200,
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    coverage_spec.chmod(0o444)
    coverage_matrix.chmod(0o444)
    coverage = evidence / "coverage.json"
    coverage_report = evidence_generator.generate_coverage(
        parent, coverage_spec, coverage_matrix, coverage
    )
    assert coverage_report["state"] == "EXPANSION_REQUIRED"
    assert coverage_report["failing_predeclared_observables"] == [
        "beauty:0-1"
    ]
    assert (coverage.stat().st_mode & 0o777) == 0o444
    assert coverage.stat().st_nlink == 1
    linked_spec = evidence / "linked_coverage_spec.json"
    linked_spec.symlink_to(coverage_spec)
    try:
        evidence_generator.generate_coverage(
            parent,
            linked_spec,
            coverage_matrix,
            evidence / "linked_coverage.json",
        )
    except ValueError as error:
        assert "symbolic link" in str(error)
    else:
        raise AssertionError("symlinked coverage specification was accepted")
    incomplete_matrix = json.loads(coverage_matrix.read_text())
    incomplete_matrix["observations"] = incomplete_matrix["observations"][:1]
    incomplete_path = evidence / "incomplete_coverage_matrix.json"
    incomplete_path.write_text(json.dumps(incomplete_matrix) + "\n")
    try:
        evidence_generator.generate_coverage(
            parent,
            coverage_spec,
            incomplete_path,
            evidence / "invalid_coverage.json",
        )
    except ValueError as error:
        assert "exactly cover" in str(error)
    else:
        raise AssertionError(
            "incomplete final coverage matrix was accepted"
        )

    parent_analysis = checkout / "AnalysisOutput" / "authorization_parent_100"
    parent_analyzed = checkout / "AnalyzedData" / "authorization_parent_100"
    write(parent_analysis / "per_job" / "slot_000.root", b"analysis-fixture")
    write(parent_analyzed / "complete.root", b"analyzed-data-fixture")
    storage = evidence / "storage.json"
    storage_report = evidence_generator.generate_storage(
        campaign_json,
        parent,
        collection,
        parent_analysis,
        parent_analyzed,
        checkout,
        storage,
    )
    assert storage_report["state"] == "PASS"
    assert storage_report["projected_required_additional_bytes"] > 0
    assert sum(storage_report["projection_components"].values()) == (
        storage_report["projected_required_additional_bytes"]
    )
    assert storage_report["final_capacity_recheck"]["state"] == "PASS"
    assert (storage.stat().st_mode & 0o777) == 0o444
    assert storage.stat().st_nlink == 1
    original_statvfs = evidence_generator.os.statvfs
    evidence_generator.os.statvfs = lambda path: Namespace(
        f_blocks=100,
        f_bavail=0,
        f_frsize=1,
    )
    try:
        failed_storage = evidence_generator.generate_storage(
            campaign_json,
            parent,
            collection,
            parent_analysis,
            parent_analyzed,
            checkout,
            evidence / "storage_capacity_failure.json",
        )
    finally:
        evidence_generator.os.statvfs = original_statvfs
    assert failed_storage["state"] == "FAIL"
    assert failed_storage["gate_e_storage_authorized"] is False
    expected_intervals = campaign_contract.reserved_seed_intervals(
        config, [{}]
    )
    authorization = {
        "schema": campaign_contract.EXPANSION_AUTHORIZATION_SCHEMA,
        "decision": "APPROVE_EQUAL_TUNE_EXPANSION",
        "approved": True,
        "reviewer": "Alice Example",
        "reviewer_role": "project_owner",
        "decision_utc": datetime.now(timezone.utc).isoformat(),
        "rationale": "Predeclared rare-beauty coverage requires equal exposure.",
        "campaign": config["campaign"],
        "campaign_ordinal": config["campaign_ordinal"],
        "repository_commit": config["repository_commit"],
        "equal_tune_scope": list(TUNES),
        "additional_jobs_per_tune": 10,
        "final_jobs_per_tune": 110,
        "candidate_slots": config["candidate_slots"],
        "campaign_json_sha256": sha(campaign_json),
        "candidate_manifest_sha256": sha(candidate),
        "initial_seed_ledger_prefix_bytes": len(initial_ledger_bytes),
        "initial_seed_ledger_prefix_sha256":
            hashlib.sha256(initial_ledger_bytes).hexdigest(),
        "reserved_seed_intervals": expected_intervals,
        "parent": config["supersedes"],
        "evidence_generator_sha256": sha(
            ROOT / "tools/generate_expansion_evidence.py"
        ),
        "coverage_precision_report": {
            "path": str(coverage.relative_to(checkout)),
            "sha256": sha(coverage),
        },
        "storage_projection": {
            "path": str(storage.relative_to(checkout)),
            "sha256": sha(storage),
        },
    }
    path = campaign_dir / "EQUAL_TUNE_EXPANSION_AUTHORIZATION.json"
    path.write_text(json.dumps(authorization, indent=2, sort_keys=True) + "\n")
    path.chmod(0o444)
    campaign_contract.validate_expansion_authorization(path, checkout, config)

    retry_evidence = (
        checkout
        / "Production"
        / config["campaign"]
        / "raw_validation"
        / "MONASH"
        / "job_000"
        / "attempt_000"
        / "receipt.json"
    )
    retry_evidence.parent.mkdir(parents=True)
    retry_evidence.write_text('{"result":"FAIL"}\n')
    retry_evidence.chmod(0o444)
    retry = {
        "campaign": config["campaign"],
        "tune": "MONASH",
        "logical_id": 0,
        "attempt": 1,
        "seed": campaign_contract.campaign_logical_seed(
            config, "MONASH", 0, 1
        ),
        "allocation": "retry",
        "reason": "Synthetic terminal raw-validation failure.",
        "prior_attempt_evidence": {
            "kind": "raw_validation_fail",
            "path": str(retry_evidence.relative_to(checkout)),
            "sha256": sha(retry_evidence),
        },
    }
    with ledger.open("a") as stream:
        stream.write(json.dumps(retry, sort_keys=True) + "\n")
    validated_authorization = (
        campaign_contract.validate_expansion_authorization(
            path, checkout, config
        )
    )
    expansion_claim = {
        "equal_tune_expansion_authorization_sha256": sha(path),
        "expansion_live_storage_recheck":
            campaign_contract.live_recheck_expansion_storage(
                validated_authorization, checkout, config
            ),
    }
    campaign_contract.recheck_expansion_storage_from_claim(
        expansion_claim, checkout, config
    )
    stale_claim = json.loads(json.dumps(expansion_claim))
    stale_claim["expansion_live_storage_recheck"]["checked_utc"] = (
        "2000-01-01T00:00:00+00:00"
    )
    try:
        campaign_contract.recheck_expansion_storage_from_claim(
            stale_claim, checkout, config
        )
    except ValueError as error:
        assert "stale" in str(error)
    else:
        raise AssertionError(
            "stale expansion claim-time capacity check was accepted"
        )

    original_statvfs = campaign_contract.os.statvfs
    actual_statvfs = original_statvfs(checkout)
    campaign_contract.os.statvfs = lambda target: Namespace(
        f_blocks=actual_statvfs.f_blocks,
        f_bavail=0,
        f_frsize=actual_statvfs.f_frsize,
        f_bsize=actual_statvfs.f_bsize,
    )
    try:
        campaign_contract.validate_expansion_authorization(
            path, checkout, config
        )
    except ValueError as error:
        assert "headroom" in str(error)
    else:
        raise AssertionError(
            "failed live expansion capacity was accepted"
        )
    finally:
        campaign_contract.os.statvfs = original_statvfs

    partial_budget = storage_report["projection_components"][
        "one_full_candidate_batch_retry_partial_contingency_bytes"
    ]
    retained_partial = (
        checkout
        / "Production"
        / config["campaign"]
        / "partial"
        / "MONASH"
        / "retained.partial.root"
    )
    retained_partial.parent.mkdir(parents=True)
    retained_partial.write_bytes(b"x" * (partial_budget + 1))
    try:
        campaign_contract.validate_expansion_authorization(
            path, checkout, config
        )
    except ValueError as error:
        assert "exceed frozen budgets" in str(error)
    else:
        raise AssertionError(
            "over-budget retained expansion partial was accepted"
        )
    retained_partial.unlink()

    original_ledger = ledger.read_bytes()
    mutated_prefix = bytearray(original_ledger)
    mutated_prefix[0] = ord("[")
    ledger.write_bytes(mutated_prefix)
    try:
        campaign_contract.validate_expansion_authorization(
            path, checkout, config
        )
    except ValueError as error:
        assert "prefix differs" in str(error)
    else:
        raise AssertionError("mutated expansion ledger prefix was accepted")
    ledger.write_bytes(original_ledger)

    handwritten_coverage = evidence / "handwritten_coverage.json"
    handwritten_payload = json.loads(coverage.read_text())
    handwritten_payload["evaluations"][0]["state"] = "PASS"
    handwritten_coverage.write_text(
        json.dumps(handwritten_payload, indent=2, sort_keys=True) + "\n"
    )
    handwritten_coverage.chmod(0o444)
    original_coverage_binding = dict(
        authorization["coverage_precision_report"]
    )
    authorization["coverage_precision_report"] = {
        "path": str(handwritten_coverage.relative_to(checkout)),
        "sha256": sha(handwritten_coverage),
    }
    path.chmod(0o644)
    path.write_text(
        json.dumps(authorization, indent=2, sort_keys=True) + "\n"
    )
    path.chmod(0o444)
    try:
        campaign_contract.validate_expansion_authorization(
            path, checkout, config
        )
    except ValueError as error:
        assert "machine-reproduced" in str(error)
    else:
        raise AssertionError("handwritten expansion evaluations were accepted")
    authorization["coverage_precision_report"] = original_coverage_binding

    stale_storage = evidence / "stale_storage.json"
    stale_payload = json.loads(storage.read_text())
    stale_payload["final_capacity_recheck"]["checked_utc"] = (
        "2000-01-01T00:00:00+00:00"
    )
    stale_storage.write_text(
        json.dumps(stale_payload, indent=2, sort_keys=True) + "\n"
    )
    stale_storage.chmod(0o444)
    original_storage_binding = dict(authorization["storage_projection"])
    authorization["storage_projection"] = {
        "path": str(stale_storage.relative_to(checkout)),
        "sha256": sha(stale_storage),
    }
    path.chmod(0o644)
    path.write_text(
        json.dumps(authorization, indent=2, sort_keys=True) + "\n"
    )
    path.chmod(0o444)
    try:
        campaign_contract.validate_expansion_authorization(
            path, checkout, config
        )
    except ValueError as error:
        assert "stale" in str(error)
    else:
        raise AssertionError("stale expansion capacity evidence was accepted")
    authorization["storage_projection"] = original_storage_binding
    path.chmod(0o644)
    path.write_text(
        json.dumps(authorization, indent=2, sort_keys=True) + "\n"
    )
    path.chmod(0o444)

    inventory_file = parent_analysis / "per_job" / "slot_000.root"
    original_inventory = inventory_file.read_bytes()
    inventory_file.write_bytes(original_inventory + b"-tampered")
    try:
        campaign_contract.validate_expansion_authorization(
            path, checkout, config
        )
    except ValueError as error:
        assert "inventory" in str(error)
    else:
        raise AssertionError("changed expansion source inventory was accepted")
    inventory_file.write_bytes(original_inventory)

    path.chmod(0o644)
    authorization["final_jobs_per_tune"] = 120
    path.write_text(json.dumps(authorization) + "\n")
    path.chmod(0o444)
    try:
        campaign_contract.validate_expansion_authorization(path, checkout, config)
    except ValueError:
        pass
    else:
        raise AssertionError("tampered expansion owner authorization accepted")


def test_union_and_consumers(base: Path, additional: int) -> None:
    checkout, collection, union = build_union(base, additional)
    rows = canonical.read_jsonl(union / "canonical_manifest.jsonl")
    expected_n = 100 + additional
    assert len(rows) == 3 * expected_n
    assert analysis_contract.canonical_jobs_per_tune(rows) == expected_n
    canonical.validate_directory(union, require_seal=False)
    if additional == 10:
        output = base / "expanded_analysis.sub"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/render_analysis_submit.py"),
                str(union / "canonical_manifest.jsonl"),
                str(checkout),
                str(collection),
                str(base / "AnalysisOutput"),
                str(output),
            ],
            check=True,
        )
        assert output.read_text().count("\nparent_100,MONASH,") == 100
        assert output.read_text().count("\nextension_10,MONASH,") == 10


def test_chained_expansion(base: Path) -> None:
    checkout, collection, parent = build_union(base, 10)
    seal_superseding_fixture(parent)
    extension = create_source_freeze(
        collection,
        "extension_chain_10",
        88,
        10,
        80_000_000,
        extension=True,
    )
    create_child_campaign(checkout, parent, extension, 10)
    canonical.REPOSITORY_ROOT = checkout
    canonical.require_clean_checkout = lambda: "5" * 40
    canonical.require_ancestor = lambda ancestor, descendant: None
    output = collection / "extension_chain_10" / "freeze"
    canonical.supersede(
        Namespace(
            parent_freeze=parent,
            extension_freeze=extension,
            production_collection_root=collection,
            output_dir=output,
        )
    )
    canonical.validate_directory(output, require_seal=False)
    rows = canonical.read_jsonl(output / "canonical_manifest.jsonl")
    summary = json.loads((output / "freeze_summary.json").read_text())
    assert len(rows) == 360
    assert summary["jobs_per_tune"] == 120
    assert [
        source["campaign"] for source in summary["source_freezes"]
    ] == ["parent_100", "extension_10", "extension_chain_10"]
    assert [
        source["jobs_in_final_union_per_tune"]
        for source in summary["source_freezes"]
    ] == [100, 10, 10]
    assert {row["final_campaign"] for row in rows} == {
        "extension_chain_10"
    }
    assert merge_contract.validate(output)["source_campaigns"] == [
        "extension_10",
        "extension_chain_10",
        "parent_100",
    ]


def test_atomic_supersede_promotion(base: Path) -> None:
    output = base / "freeze"
    try:
        canonical.promote_freeze_artifacts(
            output,
            {
                "canonical_manifest.jsonl": "",
                "freeze_summary.json": "{}\n",
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError("invalid staged freeze was promoted")
    assert not output.exists()
    assert not list(base.glob(".freeze.partial.*"))


def test_reuse_rejected(base: Path) -> None:
    checkout = base / "reuse_checkout"
    initialize_checkout(checkout)
    collection = checkout / "Production"
    parent = create_source_freeze(
        collection, "parent_100", 41, 100, 30_000_000, extension=False
    )
    extension = create_source_freeze(
        collection, "extension_10", 42, 10, 40_000_000, extension=True
    )
    rows = canonical.read_jsonl(extension / "canonical_manifest.jsonl")
    parent_seed = canonical.read_jsonl(
        parent / "canonical_manifest.jsonl"
    )[0]["seed"]
    rows[0]["seed"] = parent_seed
    rows[0]["production_definition_sha256"] = canonical.production_definition(
        rows[0]
    )
    rebuild_freeze(extension, rows)
    create_child_campaign(checkout, parent, extension, 10)
    canonical.REPOSITORY_ROOT = checkout
    canonical.require_clean_checkout = lambda: "5" * 40
    canonical.require_ancestor = lambda ancestor, descendant: None
    try:
        canonical.supersede(
            Namespace(
                parent_freeze=parent,
                extension_freeze=extension,
                production_collection_root=collection,
                output_dir=collection / "extension_10" / "freeze",
            )
        )
    except ValueError as error:
        assert "reuses a seed" in str(error)
    else:
        raise AssertionError("parent/extension seed reuse was accepted")


def test_production_contract_mismatch_rejected(base: Path) -> None:
    checkout = base / "contract_mismatch_checkout"
    initialize_checkout(checkout)
    collection = checkout / "Production"
    parent = create_source_freeze(
        collection, "parent_100", 51, 100, 50_000_000, extension=False
    )
    extension = create_source_freeze(
        collection, "extension_10", 52, 10, 60_000_000, extension=True
    )
    rows = canonical.read_jsonl(extension / "canonical_manifest.jsonl")
    rows[0]["effective_pthat_min"] = 2.0
    rows[0]["production_definition_sha256"] = canonical.production_definition(
        rows[0]
    )
    rebuild_freeze(extension, rows)
    create_child_campaign(checkout, parent, extension, 10)
    canonical.REPOSITORY_ROOT = checkout
    canonical.require_clean_checkout = lambda: "5" * 40
    canonical.require_ancestor = lambda ancestor, descendant: None
    try:
        canonical.supersede(
            Namespace(
                parent_freeze=parent,
                extension_freeze=extension,
                production_collection_root=collection,
                output_dir=collection / "extension_10" / "freeze",
            )
        )
    except ValueError as error:
        assert "scientific production definitions differ" in str(error)
    else:
        raise AssertionError(
            "parent/extension production-definition mismatch was accepted"
        )


def main() -> int:
    test_dynamic_campaign_contract()
    test_lowest_valid_selection_policy()
    assert analysis_contract.SLOT_DIRECTORY.fullmatch("slot_1000")
    assert not analysis_contract.SLOT_DIRECTORY.fullmatch("slot_1000_extra")
    with tempfile.TemporaryDirectory(
        prefix="hadronization_superseding_expansion_"
    ) as raw:
        base = Path(raw)
        test_generated_expansion_candidate_scope(base)
        test_owner_expansion_authorization(base)
        test_union_and_consumers(base / "n110", 10)
        test_union_and_consumers(base / "n120", 20)
        test_chained_expansion(base / "chained")
        (base / "atomic").mkdir()
        test_atomic_supersede_promotion(base / "atomic")
        test_reuse_rejected(base / "reuse")
        test_production_contract_mismatch_rejected(
            base / "production_contract"
        )
    print("superseding equal-tune expansion contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
