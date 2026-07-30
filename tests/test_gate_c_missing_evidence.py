#!/usr/bin/env python3
"""Executable failure injections for the publication Gate-C requirements."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from test_gate_b_submission_contract import (
    prepare_checkout,
    run,
    write_submission_classads,
)
from test_worker_provenance_contract import worker_arguments


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "tools/gate_c_workflow_audit.py"
MANIFEST = ROOT / "tools/campaign_manifest.py"
GATE_B_GENERATOR = ROOT / "tools/generate_gate_b_pilots.py"
PRODUCTION_RENDERER = ROOT / "tools/render_production_submit.py"
ANALYSIS_RENDERER = ROOT / "tools/render_analysis_submit.py"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


def load_audit():
    specification = importlib.util.spec_from_file_location(
        "gate_c_workflow_audit_test",
        AUDIT_PATH,
    )
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )


def prepare_registry(test_root: Path) -> None:
    registry_root = test_root / "shared_registry"
    registry_root.mkdir()
    os.environ["HADRONIZATION_SUBMISSION_REGISTRY_ROOT"] = str(
        registry_root
    )
    identity = "github.com/waxpardo/hadronization"
    registry = (
        registry_root
        / hashlib.sha256(identity.encode()).hexdigest()
    )
    registry.mkdir()
    baseline = registry / "reservation_baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "schema": "hf_submission_registry_baseline_v1",
                "repository_identity": identity,
                "reviewer": "Gate-C Eviction Contract Test",
                "historical_reservations": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    baseline.chmod(0o444)


def prepare_eviction_checkout(checkout: Path) -> None:
    prepare_checkout(checkout)
    (checkout / "tools").mkdir(exist_ok=True)
    (checkout / "Validation").mkdir(exist_ok=True)
    (checkout / "AnalysisScripts").mkdir(exist_ok=True)
    shutil.copy2(MANIFEST, checkout / "tools/campaign_manifest.py")
    shutil.copy2(ROOT / "runCondorJob.sh", checkout / "runCondorJob.sh")
    (checkout / "setupEnv.sh").write_text("#!/bin/bash\n:\n")
    (checkout / "Validation/validate_raw_output.sh").write_text(
        "#!/bin/bash\n"
        "set -euo pipefail\n"
        "echo 'RAW_VALIDATION_SUMMARY errors=0 entries=1 successes=1'\n"
    )
    (checkout / "Validation/ValidateRawOutput.C").write_text(
        "int ValidateRawOutput() { return 0; }\n"
    )
    for name in (
        "HeavyFlavourUtils.h",
        "GeneratedHeavyFlavourRegistry.h",
        "GeneratedTuneSettingRegistry.h",
        "Sha256.h",
    ):
        source = ROOT / "SimulationScripts" / name
        if source.exists():
            shutil.copy2(source, checkout / "SimulationScripts" / name)
        else:
            (checkout / "SimulationScripts" / name).write_text(
                "#pragma once\n"
            )
    shutil.copy2(
        ROOT / "AnalysisScripts/GeneratedPairRegistry.h",
        checkout / "AnalysisScripts/GeneratedPairRegistry.h",
    )
    producer = checkout / "SimulationScripts/heavyflavourcorrelations_status"
    producer.write_text(
        "#!/bin/bash\n"
        "set -euo pipefail\n"
        "output=\"$2\"\n"
        "printf 'KILLED_PARTIAL\\n' > \"${output}\"\n"
        "while :; do sleep 1; done\n"
    )
    for executable in (
        checkout / "runCondorJob.sh",
        checkout / "setupEnv.sh",
        checkout / "Validation/validate_raw_output.sh",
        producer,
        checkout / "tools/campaign_manifest.py",
    ):
        executable.chmod(0o755)
    run(
        "git",
        "add",
        "runCondorJob.sh",
        "setupEnv.sh",
        "tools",
        "Validation",
        "AnalysisScripts",
        "SimulationScripts",
        cwd=checkout,
    )
    run("git", "commit", "-q", "-m", "eviction worker fixture", cwd=checkout)


def test_started_then_evicted_partial(test_root: Path) -> None:
    checkout = test_root / "eviction_checkout"
    checkout.mkdir()
    prepare_eviction_checkout(checkout)
    prepare_registry(test_root)
    campaign = "HF_GATEB_started_then_evicted_contract"
    run(
        sys.executable,
        str(GATE_B_GENERATOR),
        "--root",
        str(checkout),
        "--campaign",
        campaign,
        "--campaign-ordinal",
        "901",
        "--seed-base",
        "510000001",
    )
    campaign_dir = checkout / "campaigns" / campaign
    rows = [
        json.loads(line)
        for line in (
            campaign_dir / "candidate_manifest.jsonl"
        ).read_text().splitlines()
    ]
    row = next(
        item
        for item in rows
        if item["tune"] == "MONASH" and item["logical_id"] == 0
    )
    producer = checkout / "SimulationScripts/heavyflavourcorrelations_status"
    producer_sha = digest(producer)
    campaign_root = checkout / "Production" / campaign
    submit = campaign_root / "submit_gate_b.sub"
    run(
        sys.executable,
        str(PRODUCTION_RENDERER),
        str(campaign_dir),
        str(checkout),
        str(submit),
        "--roles",
        "pilot",
        "--producer-executable-sha256",
        producer_sha,
    )
    claim = run(
        sys.executable,
        str(MANIFEST),
        "claim-submission",
        str(campaign_dir),
        "--checkout-root",
        str(checkout),
        "--production-root",
        str(checkout / "Production"),
        "--submit-file",
        str(submit),
        "--producer",
        str(producer),
        "--producer-executable-sha256",
        producer_sha,
        "--submission-kind",
        "gate_b",
    )
    fake_scheduler = test_root / "fake_scheduler"
    fake_scheduler.mkdir()
    classad_fixture = test_root / "submission_classads.json"
    condor_q = fake_scheduler / "condor_q"
    condor_q.write_text(
        "#!/usr/bin/env python3\n"
        "import os\n"
        "print(open(os.environ['HF_TEST_CLASSADS_PATH']).read(), end='')\n"
    )
    condor_q.chmod(0o755)
    os.environ["HF_TEST_CLASSADS_PATH"] = str(classad_fixture)
    os.environ["PATH"] = (
        str(fake_scheduler)
        + os.pathsep
        + os.environ.get("PATH", "")
    )
    write_submission_classads(
        classad_fixture,
        Path(claim.stdout.strip()),
        checkout.resolve(),
        61234,
    )
    run(
        sys.executable,
        str(MANIFEST),
        "record-submission",
        claim.stdout.strip(),
        "61234.0 - 61234.8",
        "--checkout-root",
        str(checkout),
    )

    process = subprocess.Popen(
        worker_arguments(
            checkout,
            campaign_dir,
            row,
            producer_sha,
            "61234",
            "0",
        ),
        cwd=checkout,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    partials: list[Path] = []
    deadline = time.monotonic() + 15.0
    try:
        while time.monotonic() < deadline:
            partials = sorted(
                (campaign_root / "partial/MONASH").glob("*.partial.root")
            )
            if partials and partials[0].read_bytes() == b"KILLED_PARTIAL\n":
                break
            if process.poll() is not None:
                output = process.communicate()[0]
                raise AssertionError(
                    "eviction fixture worker exited before termination:\n"
                    f"{output}"
                )
            time.sleep(0.05)
        else:
            raise AssertionError("worker partial did not appear before timeout")
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate(timeout=5)
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate(timeout=5)

    stable = campaign_root / "raw/MONASH/hf_MONASH_job000.root"
    assert not stable.exists()
    assert len(partials) == 1
    assert partials[0].read_bytes() == b"KILLED_PARTIAL\n"
    attempt_start = (
        campaign_root
        / "attempt_starts/MONASH/job_000/attempt_000.json"
    )
    assert attempt_start.is_file()
    assert json.loads(attempt_start.read_text())["state"] == (
        "claimed_before_producer_execution"
    )
    assert not list(
        (campaign_root / "raw_validation/MONASH").glob("**/receipt.json")
    )
    print(
        "GATE_C_EVIDENCE requirement=2 state=PASS "
        "started_then_evicted_partial_not_promoted=true"
    )


def candidate_rows() -> list[dict]:
    rows = []
    for tune in TUNES:
        count = 100 if tune == "MONASH" else 200
        for logical_id in range(count):
            rows.append(
                {
                    "campaign": "gate_c_synthetic_full",
                    "tune": tune,
                    "logical_id": logical_id,
                    "role": (
                        "primary" if logical_id < 100 else "reserve"
                    ),
                }
            )
    return rows


def status_rows(audit, candidates: list[dict]) -> list[dict]:
    rows = []
    for row in candidates:
        invalid = (
            (row["tune"] == "JUNCTIONS" and row["logical_id"] == 7)
            or (
                row["tune"] == "CLOSEPACKING"
                and row["logical_id"] == 12
            )
        )
        valid = not invalid
        rows.append(
            {
                "schema": audit.SELECTION_STATUS_SCHEMA,
                "campaign": row["campaign"],
                "tune": row["tune"],
                "logical_id": row["logical_id"],
                "attempt": 0,
                "valid": valid,
                "terminal_state": (
                    "VALIDATED" if valid else "EVICTED_OR_LOST"
                ),
                "raw_path": (
                    f"raw/{row['tune']}/"
                    f"hf_{row['tune']}_job{row['logical_id']:03d}.root"
                    if valid else None
                ),
                "raw_sha256": (
                    hashlib.sha256(
                        f"{row['tune']}:{row['logical_id']}".encode()
                    ).hexdigest()
                    if valid else None
                ),
                "validation_receipt_sha256": (
                    hashlib.sha256(
                        f"receipt:{row['tune']}:{row['logical_id']}".encode()
                    ).hexdigest()
                    if valid else None
                ),
            }
        )
    return rows


def test_deterministic_selection_and_event_ids(audit) -> tuple[
    list[dict], list[dict]
]:
    candidates = candidate_rows()
    statuses = status_rows(audit, candidates)
    first, report = audit.deterministic_canonical_selection(
        candidates,
        statuses,
    )
    second, second_report = audit.deterministic_canonical_selection(
        list(reversed(candidates)),
        list(reversed(statuses)),
    )
    assert audit.digest_rows(first) == audit.digest_rows(second)
    assert report["selection_sha256"] == second_report["selection_sha256"]
    substitutions = {
        (
            row["tune"],
            row["canonical_slot"],
            row["replacement_logical_id"],
        )
        for row in report["substitutions"]
    }
    assert ("JUNCTIONS", 7, 100) in substitutions
    assert ("CLOSEPACKING", 12, 100) in substitutions
    assert len(report["substitutions"]) == 2

    contaminated = copy.deepcopy(statuses)
    contaminated[0]["balancing_yield"] = 123.0
    try:
        audit.deterministic_canonical_selection(candidates, contaminated)
    except ValueError as error:
        assert "physics-sensitive" in str(error)
    else:
        raise AssertionError("physics-sensitive canonical selection accepted")

    canonical = []
    candidate_lookup = {
        (row["tune"], row["logical_id"]): row
        for row in candidates
    }
    status_lookup = {
        (row["tune"], row["logical_id"]): row
        for row in statuses
    }
    for choice in first:
        tune = choice["tune"]
        logical_id = choice["logical_id"]
        status = status_lookup[(tune, logical_id)]
        canonical.append(
            {
                "schema": "hf_canonical_raw_manifest_v2",
                "campaign": "gate_c_synthetic_full",
                "campaign_ordinal": 902,
                "tune": tune,
                "canonical_slot": choice["canonical_slot"],
                "block": choice["canonical_slot"] % 10,
                "logical_id": logical_id,
                "role": candidate_lookup[(tune, logical_id)]["role"],
                "attempt": choice["attempt"],
                "seed": (
                    700000001
                    + TUNES.index(tune) * 100000
                    + logical_id * 100
                ),
                "requested_successes": 1_000_000,
                "raw_path": status["raw_path"],
                "raw_sha256": status["raw_sha256"],
            }
        )
    event_report = audit.audit_manifest_event_ranges(canonical)
    assert event_report["total_event_ids_proved"] == 300_000_000
    assert event_report["unique_prefixes"] == 300
    event_rows = []
    for canonical_row in canonical[:5]:
        for local_success in (0, 999_999):
            event_rows.append(
                {
                    "schema": audit.EVENT_ROW_SCHEMA,
                    "campaign_ordinal": canonical_row["campaign_ordinal"],
                    "tune": canonical_row["tune"],
                    "logical_id": canonical_row["logical_id"],
                    "attempt": canonical_row["attempt"],
                    "local_success": local_success,
                    "event_id": audit.event_id(
                        canonical_row["campaign_ordinal"],
                        TUNES.index(canonical_row["tune"]),
                        canonical_row["logical_id"],
                        canonical_row["attempt"],
                        local_success,
                    ),
                }
            )
    assert audit.audit_event_rows(event_rows)["unique_event_ids"] == 10
    duplicate = copy.deepcopy(event_rows)
    duplicate.append(copy.deepcopy(event_rows[0]))
    try:
        audit.audit_event_rows(duplicate)
    except ValueError as error:
        assert "duplicate global event ID" in str(error)
    else:
        raise AssertionError("duplicate global event ID was accepted")

    duplicate_prefix = copy.deepcopy(canonical)
    duplicate_prefix[1]["logical_id"] = duplicate_prefix[0]["logical_id"]
    duplicate_prefix[1]["attempt"] = duplicate_prefix[0]["attempt"]
    try:
        audit.audit_manifest_event_ranges(duplicate_prefix)
    except ValueError as error:
        assert "duplicate global event-ID prefix" in str(error)
    else:
        raise AssertionError("duplicate global event-ID prefix was accepted")
    print(
        "GATE_C_EVIDENCE requirement=7 state=PASS "
        "lowest_valid_reserve_deterministic=true"
    )
    print(
        "GATE_C_EVIDENCE requirement=8 state=PASS "
        "duplicate_global_event_id_rejected=true"
    )
    return candidates, canonical


def diagnostic_rows(audit, candidates: list[dict], source: str) -> list[dict]:
    rows = []
    selected = [
        row
        for row in candidates
        if (
            row["tune"] == "MONASH" and row["logical_id"] < 6
        )
        or (
            row["tune"] != "MONASH"
            and (
                row["logical_id"] < 6
                or 100 <= row["logical_id"] < 106
            )
        )
    ]
    for index, row in enumerate(selected):
        failure = row["logical_id"] in {2, 102}
        charm_fraction = (
            0.85 if failure else 0.45 + 0.01 * (index % 3)
        )
        values = {
            "elapsed_seconds": 100.0 + index,
            "completed_attempts": 1_000_000.0 if not failure else 500_000.0,
            "event_rate_hz": 10_000.0 - 5.0 * index,
            "output_bytes": 2_000_000.0 + 1000.0 * index,
            "process_charm_fraction": charm_fraction,
            "process_beauty_fraction": 1.0 - charm_fraction,
            "mean_nch_hadronisation": 20.0 + 0.2 * (index % 4),
        }
        rows.append(
            {
                "schema": audit.DIAGNOSTIC_ROW_SCHEMA,
                "source": source,
                "campaign": row["campaign"],
                "tune": row["tune"],
                "logical_id": row["logical_id"],
                "role": row["role"],
                "attempt": 0,
                "outcome": "PRODUCER_FAILURE" if failure else "VALID",
                **values,
            }
        )
    return rows


def test_failure_bias_diagnostic(audit, candidates: list[dict]) -> None:
    synthetic = audit.failure_bias_diagnostic(
        candidates,
        diagnostic_rows(audit, candidates, "synthetic"),
        input_kind="synthetic",
    )
    pilot = audit.failure_bias_diagnostic(
        candidates,
        diagnostic_rows(audit, candidates, "pilot"),
        input_kind="pilot",
    )
    for report in (synthetic, pilot):
        assert report["state"] == "DIAGNOSTIC_COMPLETE"
        assert report["requires_human_review"] is True
        assert report["complete_metric_comparisons"] > 0
    junctions = next(
        row
        for row in synthetic["comparisons"]
        if row["comparison"] == "JUNCTIONS:valid_vs_failed"
    )
    charm = junctions["metrics"]["process_charm_fraction"]
    assert charm["status"] == "COMPLETE"
    assert charm["mean_difference"] < -0.2

    missing_metric = diagnostic_rows(audit, candidates, "synthetic")
    missing_metric[0]["event_rate_hz"] = float("nan")
    try:
        audit.failure_bias_diagnostic(
            candidates,
            missing_metric,
            input_kind="synthetic",
        )
    except ValueError as error:
        assert "non-finite" in str(error)
    else:
        raise AssertionError("non-finite failure-bias metric was accepted")
    print(
        "GATE_C_EVIDENCE requirement=9 state=PASS "
        "synthetic_and_pilot_metadata_bias_diagnostic=true"
    )


def prepare_analysis_checkout(path: Path) -> None:
    (path / "AnalysisScripts").mkdir(parents=True)
    (path / "AnalysisScripts/status_analysis_THnSparse_qq.C").write_text(
        "// Gate-C workflow fixture\n"
    )
    (path / "run_status_analysis.sh").write_text("#!/bin/sh\nexit 0\n")
    (path / "run_status_analysis.sh").chmod(0o755)
    run("git", "init", "-q", cwd=path)
    run("git", "config", "user.name", "Gate C Workflow", cwd=path)
    run(
        "git",
        "config",
        "user.email",
        "gate-c-workflow@example.invalid",
        cwd=path,
    )
    run("git", "add", ".", cwd=path)
    run("git", "commit", "-q", "-m", "workflow fixture", cwd=path)


def test_one_manifest_workflow(
    audit,
    test_root: Path,
    candidates: list[dict],
    canonical: list[dict],
) -> None:
    workflow = test_root / "manifest_workflow"
    workflow.mkdir()
    candidate_path = workflow / "candidate_manifest.jsonl"
    canonical_path = workflow / "canonical_manifest.jsonl"
    write_jsonl(candidate_path, candidates)
    write_jsonl(canonical_path, canonical)

    status_path = workflow / "status_submission_manifest.jsonl"
    write_jsonl(status_path, canonical)
    central_paths = {}
    for tune in TUNES:
        path = workflow / f"central_{tune}.jsonl"
        write_jsonl(path, [
            row for row in canonical if row["tune"] == tune
        ])
        central_paths[tune] = path.name
    block_paths = {}
    block_merge_paths = {}
    block_tune_hashes = {}
    for block_index in range(1, 11):
        name = f"block_{block_index:02d}"
        rows = [
            row for row in canonical
            if row["block"] == block_index - 1
        ]
        block_path = workflow / f"{name}.jsonl"
        merge_path = workflow / f"{name}_merge_inputs.jsonl"
        write_jsonl(block_path, rows)
        write_jsonl(merge_path, rows)
        block_paths[name] = block_path.name
        block_merge_paths[name] = merge_path.name
        block_tune_hashes[name] = {
            tune: audit.digest_rows([
                row for row in rows if row["tune"] == tune
            ])
            for tune in TUNES
        }
    plot_contract = {
        "schema": "hf_plot_selection_contract_v1",
        "canonical_manifest_sha256": digest(canonical_path),
        "canonical_rows": 300,
        "complete_root_input_sha256": {
            tune: audit.digest_rows([
                row for row in canonical if row["tune"] == tune
            ])
            for tune in TUNES
        },
        "subsample_input_sha256": block_tune_hashes,
        "block_count": 10,
    }
    plot_path = workflow / "plot_selection_contract.json"
    plot_path.write_text(
        json.dumps(plot_contract, indent=2, sort_keys=True) + "\n"
    )
    specification = {
        "schema": audit.WORKFLOW_SPEC_SCHEMA,
        "canonical_manifest": canonical_path.name,
        "candidate_manifest": candidate_path.name,
        "block_manifests": block_paths,
        "status_submission_manifest": status_path.name,
        "complete_root_merge_manifests": central_paths,
        "subsample_merge_manifests": block_merge_paths,
        "plot_selection_contract": plot_path.name,
    }
    report = audit.validate_manifest_workflow(
        specification,
        base=workflow,
    )
    assert report["state"] == "PASS"
    assert report["canonical_rows"] == 300
    assert report["unselected_reserve_count"] == 198

    reserve = next(
        row
        for row in candidates
        if row["tune"] == "JUNCTIONS"
        and row["logical_id"] == 101
    )
    extra = {
        **canonical[100],
        "canonical_slot": 100,
        "logical_id": reserve["logical_id"],
        "role": "reserve",
        "raw_path": "raw/JUNCTIONS/hf_JUNCTIONS_job101.root",
        "raw_sha256": hashlib.sha256(b"extra reserve").hexdigest(),
    }
    for label, source_key, source_path in (
        ("status", "status_submission_manifest", status_path),
        (
            "central",
            "complete_root_merge_manifests",
            workflow / central_paths["JUNCTIONS"],
        ),
        (
            "subsample",
            "subsample_merge_manifests",
            workflow / block_merge_paths["block_01"],
        ),
    ):
        mutation = workflow / f"mutated_{label}.jsonl"
        existing = [
            json.loads(line)
            for line in source_path.read_text().splitlines()
        ]
        write_jsonl(mutation, [*existing, extra])
        mutated_spec = copy.deepcopy(specification)
        if label == "status":
            mutated_spec[source_key] = mutation.name
        elif label == "central":
            mutated_spec[source_key]["JUNCTIONS"] = mutation.name
        else:
            mutated_spec[source_key]["block_01"] = mutation.name
        try:
            audit.validate_manifest_workflow(
                mutated_spec,
                base=workflow,
            )
        except ValueError as error:
            assert (
                "differs from canonical manifest" in str(error)
                or "does not contain 30 rows" in str(error)
            )
        else:
            raise AssertionError(
                f"extra reserve was accepted by {label} workflow"
            )

    mutated_plot = copy.deepcopy(plot_contract)
    mutated_plot["complete_root_input_sha256"]["JUNCTIONS"] = (
        audit.digest_rows([
            *[row for row in canonical if row["tune"] == "JUNCTIONS"],
            extra,
        ])
    )
    mutated_plot_path = workflow / "mutated_plot_contract.json"
    mutated_plot_path.write_text(
        json.dumps(mutated_plot, indent=2, sort_keys=True) + "\n"
    )
    mutated_spec = copy.deepcopy(specification)
    mutated_spec["plot_selection_contract"] = mutated_plot_path.name
    try:
        audit.validate_manifest_workflow(mutated_spec, base=workflow)
    except ValueError as error:
        assert "plot selection contract" in str(error)
    else:
        raise AssertionError("extra-reserve plot contract was accepted")

    analysis_checkout = test_root / "analysis_checkout"
    analysis_checkout.mkdir()
    prepare_analysis_checkout(analysis_checkout)
    production = test_root / "analysis_production"
    for row in canonical:
        raw = production / row["raw_path"]
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_bytes(
            f"{row['tune']}:{row['logical_id']}\n".encode()
        )
        row["raw_sha256"] = digest(raw)
        evidence = (
            production
            / "raw_validation"
            / row["tune"]
            / f"job_{row['logical_id']:03d}"
            / "attempt_000"
        )
        evidence.mkdir(parents=True, exist_ok=True)
        log = evidence / "validate_raw_output.log"
        log.write_text(
            "RAW_VALIDATION_SUMMARY errors=0 entries=1\n"
        )
        receipt = evidence / "receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "schema": "hf_raw_validation_receipt_v1",
                    "result": "PASS",
                    "validated_utc": "2026-07-30T00:00:00+00:00",
                    "validator_exit_status": 0,
                    "validator_wrapper_sha256": "1" * 64,
                    "validator_macro_sha256": "2" * 64,
                    "validator_dependency_sha256": {
                        "fixture.h": "3" * 64,
                    },
                    "validation_log_name": log.name,
                    "validation_log_sha256": digest(log),
                    "output_sha256": digest(raw),
                    "output_bytes": raw.stat().st_size,
                    "expected_provenance": {
                        "campaign": row["campaign"],
                        "tune": row["tune"],
                        "logical_id": row["logical_id"],
                    },
                },
                sort_keys=True,
            )
            + "\n"
        )
        row["raw_validation_receipt_path"] = str(
            receipt.relative_to(production)
        )
        row["raw_validation_receipt_sha256"] = digest(receipt)
        row["raw_validation_log_path"] = str(
            log.relative_to(production)
        )
        row["raw_validation_log_sha256"] = digest(log)
    # Re-emit after real fixture bytes are known, then rerender all workflow
    # manifests so every consumer binds the identical rows.
    write_jsonl(canonical_path, canonical)
    analysis_output = test_root / "analysis_output"
    submit = test_root / "canonical_analysis.sub"
    run(
        sys.executable,
        str(ANALYSIS_RENDERER),
        str(canonical_path),
        str(analysis_checkout),
        str(production),
        str(analysis_output),
        str(submit),
    )
    submit_text = submit.read_text()
    assert submit_text.count("\ngate_c_synthetic_full,") == 300
    assert digest(canonical_path) in submit_text
    overfull_manifest = test_root / "overfull_canonical.jsonl"
    write_jsonl(overfull_manifest, [*canonical, extra])
    rejected = subprocess.run(
        [
            sys.executable,
            str(ANALYSIS_RENDERER),
            str(overfull_manifest),
            str(analysis_checkout),
            str(production),
            str(analysis_output),
            str(test_root / "overfull.sub"),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected.returncode != 0
    assert "canonical analysis requires equal N>=100, N%10=0 tune exposure" in (
        rejected.stdout + rejected.stderr
    )

    submit_source = (ROOT / "submit_status_analysis.sh").read_text()
    merge_source = (ROOT / "merge_root_files.sh").read_text()
    subsample_source = (ROOT / "make_subsamples.sh").read_text()
    plot_source = (
        ROOT / "PlottingScripts/improvedPlotting_THnSparse.C"
    ).read_text()
    assert "canonical_manifest.jsonl" in submit_source
    assert "canonical_manifest.jsonl" in merge_source
    assert "block_%02d.jsonl" in merge_source
    assert 'exec "${script_dir}/merge_root_files.sh" "$@"' in (
        subsample_source
    )
    assert "ValidatePairInputSelectionContract" in plot_source
    print(
        "GATE_C_EVIDENCE requirement=10 state=PASS "
        "same_manifest_all_stages_extra_reserve_rejected=true"
    )


def main() -> int:
    audit = load_audit()
    with tempfile.TemporaryDirectory(
        prefix="hadronization_gate_c_missing_evidence_"
    ) as raw:
        test_root = Path(raw).resolve()
        test_started_then_evicted_partial(test_root)
        candidates, canonical = (
            test_deterministic_selection_and_event_ids(audit)
        )
        test_failure_bias_diagnostic(audit, candidates)
        test_one_manifest_workflow(
            audit,
            test_root,
            candidates,
            canonical,
        )
    print("Gate-C missing-evidence regression tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
