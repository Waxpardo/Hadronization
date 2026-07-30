#!/usr/bin/env python3
"""Focused regression tests for the immutable aggregate Gate-B decision."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import run_publication_gate_b as gate_b  # noqa: E402
import resolve_publication_gate_b_signoff as resolver  # noqa: E402
import run_publication_gate_d as gate_d  # noqa: E402


def valid_raw_log(events: int = 1_000_000, charm: int = 0, beauty: int = 0) -> str:
    return (
        "ROOT startup text\n"
        "RAW_ORIGIN_AUDIT "
        f"unresolved_charm_trigger_candidates={charm} "
        f"unresolved_beauty_trigger_candidates={beauty} "
        "resolved_nonhard_charm_trigger_candidates=12 "
        "resolved_nonhard_beauty_trigger_candidates=13 "
        "duplicate_hard_carrier_groups_charm=2 "
        "duplicate_hard_carrier_groups_beauty=3 "
        "duplicate_hard_carrier_demotions_charm=4 "
        "duplicate_hard_carrier_demotions_beauty=5 "
        "multi_heavy_rejections_charm=6 "
        "multi_heavy_rejections_beauty=7\n"
        f"RAW_VALIDATION_SUMMARY errors=0 entries={events} "
        "process_codes=2 stability_rows=84\n"
    )


def test_raw_log_contract() -> None:
    result = gate_b.parse_raw_log(valid_raw_log(charm=2, beauty=3), 1_000_000, "x")
    assert result["entries"] == 1_000_000
    assert result["stability_rows"] == 84
    assert result["unresolved_charm_trigger_candidates"] == 2
    assert result["unresolved_beauty_trigger_candidates"] == 3
    for changed in (
        valid_raw_log().replace("errors=0", "errors=1"),
        valid_raw_log().replace("RAW_ORIGIN_AUDIT", "RAW_VALIDATION_ERROR"),
        valid_raw_log(events=999_999),
        valid_raw_log() + valid_raw_log(),
    ):
        try:
            gate_b.parse_raw_log(changed, 1_000_000, "changed")
        except gate_b.GateFailure:
            pass
        else:
            raise AssertionError("malformed raw-validation evidence was accepted")


def test_decision_precedence() -> None:
    assert gate_b.decide_state(0, "PASS", []) == ("PASS", None, 0)
    needs_signoff = gate_b.decide_state(
        4, "SCIENTIFIC_REVIEW_REQUIRED", []
    )
    assert needs_signoff[0] == "NEEDS_SIGNOFF"
    assert needs_signoff[2] == 3
    assert "no sign-off was created or inferred" in needs_signoff[1]
    blocked = gate_b.decide_state(
        4, "SCIENTIFIC_REVIEW_REQUIRED", ["resolved pTHat shift"]
    )
    assert blocked[0] == "FAIL"
    assert blocked[2] == 2
    assert gate_b.decide_state(0, "INCONCLUSIVE", [])[0] == "FAIL"


def test_resource_summary_contract() -> None:
    line = (
        "GATE_B_RESOURCE tune=MONASH logical_id=0 "
        "successful_events=1000000 peak_rss_kib=123456 file_bytes=987654 "
        "compression_settings=101 compression_algorithm=1 "
        "compression_level=1 compression_factor=3.25 "
        "stability_schema=heavy_stability_audit_v2 "
        f"stability_sha256={'a' * 64} stability_rows=84 "
        "settings_schema=effective_pythia_settings_exhaustive_v2 "
        f"settings_sha256={'b' * 64}\n"
    )
    matches = gate_b.RESOURCE_SUMMARY.findall(line)
    assert len(matches) == 1
    assert matches[0][0:4] == ("MONASH", "0", "1000000", "123456")
    assert matches[0][6:9] == ("1", "1", "3.25")


def test_origin_summary_marker_contract() -> None:
    origin = (
        "ORIGIN_RESOLUTION_SUMMARY tune=MONASH role=trigger_candidate "
        "sector=charm candidates=42 unresolved=2 "
        "unresolved_fraction=0.047619 unresolved_fraction_defined=1 "
        "sum_weights=41.5 unresolved_sum_weights=1.8 "
        "weighted_unresolved_fraction=0.0433735 "
        "weighted_unresolved_fraction_defined=1\n"
    )
    unresolved = (
        "UNRESOLVED_SUMMARY tune=MONASH "
        "role_sector=trigger_candidate:charm candidates=2 "
        "sum_weights=1.8 sum_weights2=1.7 effective_entries=1.90588 "
        "effective_entries_defined=1\n"
    )
    origin_match = gate_b.ORIGIN_SUMMARY.findall(origin)
    unresolved_match = gate_b.UNRESOLVED_SUMMARY.findall(unresolved)
    assert len(origin_match) == 1
    assert origin_match[0][6] == "1"
    assert origin_match[0][10] == "1"
    assert len(unresolved_match) == 1
    assert unresolved_match[0][6] == "1"


def raw_evidence_fixture(nonzero: bool = False) -> list[dict]:
    rows = []
    for tune in gate_b.TUNES:
        for logical_id, (_, events, _, purpose) in gate_b.PROFILES.items():
            rows.append(
                {
                    "tune": tune,
                    "logical_id": logical_id,
                    "purpose": purpose,
                    "requested_successes": events,
                    "unresolved_charm_trigger_candidates": (
                        1 if nonzero and tune == "JUNCTIONS" and logical_id == 0 else 0
                    ),
                    "unresolved_beauty_trigger_candidates": 0,
                }
            )
    return rows


def test_unresolved_three_way_closure() -> None:
    raw = raw_evidence_fixture(nonzero=True)
    central = {
        tune: {
            "charm": 1 if tune == "JUNCTIONS" else 0,
            "beauty": 0,
        }
        for tune in gate_b.TUNES
    }
    origin = json.loads(json.dumps(central))
    pthat = {
        tune: {"0.5": 0, "1.0": 1 if tune == "JUNCTIONS" else 0, "2.0": 0}
        for tune in gate_b.TUNES
    }
    assert gate_b.reconcile_unresolved(raw, central, origin, pthat) == 1
    pthat["JUNCTIONS"]["1.0"] = 0
    try:
        gate_b.reconcile_unresolved(raw, central, origin, pthat)
    except gate_b.GateFailure:
        pass
    else:
        raise AssertionError("pTHat/raw unresolved-count mismatch was accepted")


def pthat_report_fixture(
    checkout: Path,
    campaign_dir: Path,
    campaign: dict,
    rows: list[dict],
    *,
    unresolved: int = 0,
) -> Path:
    spec = checkout / "config/pthat_sensitivity_v1.json"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text('{"schema":"fixture"}\n')
    comparisons = []
    for index in range(192):
        comparisons.append(
            {
                "tune": gate_b.TUNES[index % 3],
                "alternate_threshold": "0.5" if index % 2 else "2.0",
                "observable": f"fixture:{index}",
                "status": "EQUIVALENT_NO_RESOLVED_SHIFT",
            }
        )
    diagnostics = []
    for tune in gate_b.TUNES:
        for logical_id, (threshold, events, _, _) in gate_b.PROFILES.items():
            diagnostics.append(
                {
                    "identity": {"tune": tune, "pthat_min": threshold},
                    "events": events,
                    "unresolved_trigger_candidates": (
                        unresolved
                        if tune == "JUNCTIONS" and logical_id == 0
                        else 0
                    ),
                    "associate_origin_counts": {
                        "charm": {"0": 0, "1": 60, "2": 30, "3": 10},
                        "beauty": {"0": 0, "1": 70, "2": 20, "4": 10},
                    },
                    "associate_origin_weight_sums": {
                        "charm": {
                            "0": 0.0,
                            "1": 60.0,
                            "2": 30.0,
                            "3": 10.0,
                        },
                        "beauty": {
                            "0": 0.0,
                            "1": 70.0,
                            "2": 20.0,
                            "4": 10.0,
                        },
                    },
                }
            )
    report = {
        "schema": gate_b.PTHAT_REPORT_SCHEMA,
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
        "repository_commit": campaign["repository_commit"],
        "spec_sha256": gate_b.sha256(spec),
        "campaign_sha256": gate_b.sha256(campaign_dir / "campaign.json"),
        "manifest_sha256": gate_b.json_digest(rows),
        "outcome": (
            "SCIENTIFIC_REVIEW_REQUIRED" if unresolved else "PASS"
        ),
        "technical_failures": [],
        "scientific_review_findings": (
            [
                f"('JUNCTIONS', '1.0') has {unresolved} unresolved "
                "publication-trigger candidates"
            ]
            if unresolved
            else []
        ),
        "inconclusive_findings": [],
        "diagnostics": diagnostics,
        "comparisons": comparisons,
        "sigma_nested_closure": [{"passed": True} for _ in range(6)],
        "input_provenance_evidence": [{} for _ in range(9)],
        "extraction_sha256": {
            f"{tune}:{threshold}": "a" * 64
            for tune in gate_b.TUNES
            for threshold in ("0.5", "1.0", "2.0")
        },
    }
    path = checkout / "pthat_decision.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return path


def test_pthat_exact_contract_and_signoff_routing() -> None:
    with tempfile.TemporaryDirectory(
        prefix="hadronization_gate_b_report_test_"
    ) as raw_temporary:
        temporary = Path(raw_temporary)
        checkout = temporary / "checkout"
        campaign_dir = checkout / "campaigns/FIXTURE"
        campaign_dir.mkdir(parents=True)
        campaign = {
            "campaign": "FIXTURE",
            "campaign_ordinal": 26,
            "repository_commit": "c" * 40,
        }
        (campaign_dir / "campaign.json").write_text(
            json.dumps(campaign, sort_keys=True) + "\n"
        )
        rows = []
        for tune in gate_b.TUNES:
            for logical_id, (threshold, events, _, purpose) in gate_b.PROFILES.items():
                rows.append(
                    {
                        "tune": tune,
                        "logical_id": logical_id,
                        "pthat_min_override": threshold,
                        "requested_successes": events,
                        "purpose": purpose,
                    }
                )
        passing_path = pthat_report_fixture(
            checkout, campaign_dir, campaign, rows
        )
        passing, counts, reasons, blockers = gate_b.validate_pthat_report(
            checkout, campaign_dir, campaign, rows, passing_path
        )
        assert passing["outcome"] == "PASS"
        assert reasons == []
        assert blockers == []
        assert counts["MONASH"]["1.0"] == 0
        origins = gate_b.central_associate_origin_evidence(passing)
        assert len(origins) == 6
        assert origins[0]["count_fractions"]["selected_hard"] == 0.6

        review_path = pthat_report_fixture(
            checkout, campaign_dir, campaign, rows, unresolved=2
        )
        review, counts, reasons, blockers = gate_b.validate_pthat_report(
            checkout, campaign_dir, campaign, rows, review_path
        )
        assert review["outcome"] == "SCIENTIFIC_REVIEW_REQUIRED"
        assert counts["JUNCTIONS"]["1.0"] == 2
        assert reasons
        assert blockers == []

        changed = json.loads(review_path.read_text())
        changed["comparisons"][0]["status"] = "RESOLVED_SHIFT"
        review_path.write_text(json.dumps(changed, sort_keys=True) + "\n")
        _, _, _, blockers = gate_b.validate_pthat_report(
            checkout, campaign_dir, campaign, rows, review_path
        )
        assert blockers


def make_writable(path: Path) -> None:
    for candidate in sorted(
        path.rglob("*"), key=lambda item: len(item.parts), reverse=True
    ):
        try:
            os.chmod(candidate, 0o700 if candidate.is_dir() else 0o600)
        except FileNotFoundError:
            pass
    os.chmod(path, 0o700)


def test_sealed_tree_is_read_only() -> None:
    with tempfile.TemporaryDirectory(
        prefix="hadronization_gate_b_seal_test_"
    ) as raw_temporary:
        directory = Path(raw_temporary) / "gate_b"
        nested = directory / "nested"
        nested.mkdir(parents=True)
        evidence = nested / "evidence.txt"
        evidence.write_text("immutable\n")
        gate_b.seal_tree(directory)
        assert stat.S_IMODE(directory.stat().st_mode) == 0o555
        assert stat.S_IMODE(nested.stat().st_mode) == 0o555
        assert stat.S_IMODE(evidence.stat().st_mode) == 0o444
        make_writable(directory)


def test_immutable_input_contract() -> None:
    with tempfile.TemporaryDirectory(
        prefix="hadronization_gate_b_immutable_test_"
    ) as raw_temporary:
        directory = Path(raw_temporary)
        path = directory / "receipt.json"
        path.write_text("{}\n")
        os.chmod(path, 0o444)
        assert gate_b.require_read_only_regular(path, "receipt") == path
        os.chmod(path, 0o644)
        try:
            gate_b.require_read_only_regular(path, "receipt")
        except gate_b.GateFailure:
            pass
        else:
            raise AssertionError("writable receipt was accepted")
        os.chmod(path, 0o444)
        link = directory / "second-link.json"
        os.link(path, link)
        try:
            gate_b.require_read_only_regular(path, "receipt")
        except gate_b.GateFailure:
            pass
        else:
            raise AssertionError("multiply-linked receipt was accepted")


def test_checkout_cleanliness_whitelists_only_operational_evidence() -> None:
    with tempfile.TemporaryDirectory(
        prefix="hadronization_gate_b_checkout_test_"
    ) as raw_temporary:
        checkout = Path(raw_temporary) / "checkout"
        checkout.mkdir()
        tracked = checkout / "tracked.txt"
        tracked.write_text("clean\n")
        subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Gate B Test"],
            cwd=checkout,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "gate-b@example.invalid"],
            cwd=checkout,
            check=True,
        )
        subprocess.run(["git", "add", "."], cwd=checkout, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "fixture"],
            cwd=checkout,
            check=True,
        )
        campaign = checkout / "campaigns/FIXTURE"
        campaign.mkdir(parents=True)
        (campaign / "campaign.json").write_text("{}\n")
        commit, untracked = gate_b.validate_checkout(checkout, [campaign])
        assert gate_b.HEX40.fullmatch(commit)
        assert untracked == ["campaigns/FIXTURE/campaign.json"]

        unrelated = checkout / "unrelated.txt"
        unrelated.write_text("not allowed\n")
        try:
            gate_b.validate_checkout(checkout, [campaign])
        except gate_b.GateFailure:
            pass
        else:
            raise AssertionError("unrelated untracked file was accepted")
        unrelated.unlink()

        tracked.write_text("dirty\n")
        try:
            gate_b.validate_checkout(checkout, [campaign])
        except gate_b.GateFailure:
            pass
        else:
            raise AssertionError("tracked modification was accepted")


def expect_resolution_failure(callback, expected_fragment: str) -> None:
    try:
        callback()
    except resolver.ResolutionFailure as error:
        assert expected_fragment in str(error), str(error)
    else:
        raise AssertionError(
            f"Gate-B sign-off failure was not raised: {expected_fragment}"
        )


def write_read_only_json(path: Path, value: dict) -> None:
    if path.exists():
        os.chmod(path, 0o600)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.chmod(path, 0o444)


def gate_b_signoff_fixture(
    campaign_dir: Path, original_path: Path
) -> tuple[dict, dict]:
    sample_counts = {
        f"{tune}:{threshold}": {"charm": 0, "beauty": 0}
        for tune in gate_b.TUNES
        for threshold in ("0.5", "1.0", "2.0")
    }
    sample_counts["JUNCTIONS:1.0"]["charm"] = 2
    original = {
        "campaign": "FIXTURE",
        "campaign_ordinal": 26,
        "repository_commit": "c" * 40,
        "unresolved_trigger_candidates": {
            "all_samples_by_tune_threshold_and_sector": sample_counts,
            "all_nine_samples_total": 2,
        },
    }
    write_read_only_json(original_path, original)
    signoff = {
        "schema": resolver.SIGNOFF_SCHEMA,
        "approved": True,
        "campaign": "FIXTURE",
        "campaign_ordinal": 26,
        "repository_commit": "c" * 40,
        "gate_b_needs_signoff_report_sha256": gate_b.sha256(original_path),
        "reviewed_unresolved_trigger_candidates": sample_counts,
        "reviewed_unresolved_trigger_candidates_total": 2,
        "allowed_unresolved_treatment": resolver.ALLOWED_TREATMENT,
        "reviewer": "Alice Example",
        "reviewer_role": "project owner",
        "decision_utc": "2026-07-30T10:00:00+00:00",
        "finding": (
            "Reviewed every unresolved trigger candidate and approved the "
            "declared exclusion and reporting treatment."
        ),
        "supersedes_state": "NEEDS_SIGNOFF",
    }
    return original, signoff


def test_gate_b_signoff_is_exact_and_fail_closed() -> None:
    with tempfile.TemporaryDirectory(
        prefix="hadronization_gate_b_signoff_test_"
    ) as raw_temporary:
        checkout = Path(raw_temporary) / "checkout"
        campaign_dir = checkout / "campaigns/FIXTURE"
        campaign_dir.mkdir(parents=True)
        original_path = checkout / "gate_b_original/gate_b_report.json"
        original_path.parent.mkdir()
        original, signoff = gate_b_signoff_fixture(
            campaign_dir, original_path
        )
        signoff_path = campaign_dir / "GATE_B_PHYSICS_SIGNOFF.json"

        expect_resolution_failure(
            lambda: resolver.validate_signoff(
                campaign_dir, signoff_path, original_path, original
            ),
            "absent",
        )

        mismatches = (
            ("gate_b_needs_signoff_report_sha256", "d" * 64),
            ("campaign", "STALE_CAMPAIGN"),
            ("repository_commit", "d" * 40),
            ("reviewed_unresolved_trigger_candidates_total", 3),
            (
                "allowed_unresolved_treatment",
                "Accept every unresolved trigger without exclusion",
            ),
            ("decision_utc", "2026-07-30T10:00:00"),
        )
        for key, changed in mismatches:
            candidate = copy_json(signoff)
            candidate[key] = changed
            write_read_only_json(signoff_path, candidate)
            expect_resolution_failure(
                lambda: resolver.validate_signoff(
                    campaign_dir, signoff_path, original_path, original
                ),
                "differs"
                if key
                not in {"decision_utc"}
                else "not explicitly UTC",
            )

        candidate = copy_json(signoff)
        candidate["reviewed_unresolved_trigger_candidates"][
            "JUNCTIONS:1.0"
        ]["charm"] = 1
        write_read_only_json(signoff_path, candidate)
        expect_resolution_failure(
            lambda: resolver.validate_signoff(
                campaign_dir, signoff_path, original_path, original
            ),
            "reviewed_unresolved_trigger_candidates differs",
        )

        for key, value in (
            ("reviewer", "PROJECT OWNER"),
            ("finding", "TBD"),
        ):
            candidate = copy_json(signoff)
            candidate[key] = value
            write_read_only_json(signoff_path, candidate)
            expect_resolution_failure(
                lambda: resolver.validate_signoff(
                    campaign_dir, signoff_path, original_path, original
                ),
                "placeholder",
            )

        write_read_only_json(signoff_path, signoff)
        validated = resolver.validate_signoff(
            campaign_dir, signoff_path, original_path, original
        )
        assert validated == signoff


def copy_json(value):
    return json.loads(json.dumps(value))


def test_superseding_report_preserves_gate_d_raw_bindings() -> None:
    original = {
        key: {} for key in resolver.PRESERVED_EVIDENCE_FIELDS
    }
    raw = []
    for tune in gate_b.TUNES:
        for logical_id, (_, events, _, _) in gate_b.PROFILES.items():
            raw.append(
                {
                    "tune": tune,
                    "logical_id": logical_id,
                    "raw_sha256": "a" * 64,
                    "entries": events,
                    "requested_successes": events,
                    "validation_receipt_path": (
                        f"raw_validation/{tune}/job_{logical_id:03d}/"
                        "attempt_000/receipt.json"
                    ),
                    "validation_receipt_sha256": "b" * 64,
                }
            )
    original["raw_validation_evidence"] = raw
    original["raw_validation_count"] = 9
    copied = resolver.preserved_downstream_evidence(original)
    assert copied["raw_validation_evidence"] == raw
    assert copied["raw_validation_evidence"] is not raw
    assert len(copied["raw_validation_evidence"]) == 9
    for row in copied["raw_validation_evidence"]:
        assert row["raw_sha256"] == "a" * 64
        assert row["entries"] == row["requested_successes"]
        assert row["validation_receipt_path"].endswith("receipt.json")
        assert row["validation_receipt_sha256"] == "b" * 64
    campaign = {
        "campaign": "FIXTURE",
        "campaign_ordinal": 26,
    }
    report = {
        "schema": gate_b.REPORT_SCHEMA,
        "state": "PASS",
        "canonical": True,
        "repository_commit": "c" * 40,
        **campaign,
        **copied,
    }
    with tempfile.TemporaryDirectory(
        prefix="hadronization_gate_b_gate_d_contract_test_"
    ) as raw_temporary:
        report_path = Path(raw_temporary) / "gate_b_report.json"
        report_path.write_text(json.dumps(report, sort_keys=True) + "\n")
        accepted = gate_d.validate_gate_b(
            report_path, campaign, "c" * 40
        )
        assert accepted["raw_validation_evidence"] == raw


def test_signoff_resolution_end_to_end_fixture() -> None:
    with tempfile.TemporaryDirectory(
        prefix="hadronization_gate_b_resolution_integration_"
    ) as raw_temporary:
        checkout = Path(raw_temporary) / "checkout"
        checkout.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Gate B Test"],
            cwd=checkout,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "gate-b@example.invalid"],
            cwd=checkout,
            check=True,
        )
        (checkout / "tracked.txt").write_text("fixture\n")
        subprocess.run(["git", "add", "."], cwd=checkout, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "fixture"],
            cwd=checkout,
            check=True,
        )
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
        ).strip()
        campaign_dir = checkout / "campaigns/FIXTURE"
        campaign_dir.mkdir(parents=True)
        campaign_json = campaign_dir / "campaign.json"
        candidate_manifest = campaign_dir / "candidate_manifest.jsonl"
        seed_ledger = campaign_dir / "seed_ledger.jsonl"
        campaign_json.write_text(
            json.dumps(
                {
                    "campaign": "FIXTURE",
                    "campaign_ordinal": 26,
                    "repository_commit": commit,
                },
                sort_keys=True,
            )
            + "\n"
        )
        candidate_manifest.write_text("{}\n")
        seed_ledger.write_text("{}\n")
        production = checkout / "Production/FIXTURE"
        raw_rows = []
        sample_counts = {}
        for tune in gate_b.TUNES:
            for logical_id, (
                threshold,
                events,
                _,
                purpose,
            ) in gate_b.PROFILES.items():
                identity = f"{tune}:{threshold}"
                sample_counts[identity] = {
                    "charm": 2 if identity == "JUNCTIONS:1.0" else 0,
                    "beauty": 0,
                }
                prefix = Path("fixture_evidence") / tune / str(logical_id)
                paths = {
                    "raw_path": Path("raw") / tune / f"job_{logical_id}.root",
                    "attempt_start_path": prefix / "attempt_start.json",
                    "attempt_metadata_path": prefix / "attempt_metadata.json",
                    "validation_receipt_path": prefix / "receipt.json",
                    "validation_log_path": prefix / "validation.log",
                }
                for relative in paths.values():
                    path = production / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(f"{tune} {logical_id} {relative.name}\n")
                    os.chmod(path, 0o444)
                raw_path = production / paths["raw_path"]
                raw_rows.append(
                    {
                        "tune": tune,
                        "logical_id": logical_id,
                        "purpose": purpose,
                        "pthat_min": threshold,
                        "requested_successes": events,
                        "entries": events,
                        "raw_path": str(paths["raw_path"]),
                        "raw_bytes": raw_path.stat().st_size,
                        "raw_sha256": gate_b.sha256(raw_path),
                        "attempt_start_path": str(
                            paths["attempt_start_path"]
                        ),
                        "attempt_start_sha256": gate_b.sha256(
                            production / paths["attempt_start_path"]
                        ),
                        "attempt_metadata_path": str(
                            paths["attempt_metadata_path"]
                        ),
                        "attempt_metadata_sha256": gate_b.sha256(
                            production / paths["attempt_metadata_path"]
                        ),
                        "validation_receipt_path": str(
                            paths["validation_receipt_path"]
                        ),
                        "validation_receipt_sha256": gate_b.sha256(
                            production / paths["validation_receipt_path"]
                        ),
                        "validation_log_path": str(
                            paths["validation_log_path"]
                        ),
                        "validation_log_sha256": gate_b.sha256(
                            production / paths["validation_log_path"]
                        ),
                    }
                )
        pthat_dir = campaign_dir / "pthat"
        pthat_dir.mkdir()
        pthat_path = pthat_dir / "pthat_sensitivity_decision.json"
        pthat_path.write_text('{"fixture":true}\n')
        original_dir = campaign_dir / "gate_b_original"
        original_dir.mkdir()
        command_log = original_dir / "pthat_recheck.log"
        command_log.write_text("scientific review required\n")
        aggregate_log = original_dir / "gate_b.log"
        aggregate_log.write_text("immutable Gate-B aggregate\n")
        unresolved = {
            "central_by_tune_and_sector": {},
            "all_samples_by_tune_threshold_and_sector": sample_counts,
            "all_nine_samples_total": 2,
            "policy": "fixture",
        }
        original = {
            "schema": gate_b.REPORT_SCHEMA,
            "state": "NEEDS_SIGNOFF",
            "canonical": True,
            "failure": (
                "2 unresolved publication-trigger candidates require explicit "
                "project-owner physics review; no sign-off was created or "
                "inferred"
            ),
            "repository_commit": commit,
            "campaign": "FIXTURE",
            "campaign_ordinal": 26,
            "commands": [
                {
                    "purpose":
                        "fresh_raw_to_frozen_pthat_decision_recheck",
                    "returncode": 4,
                    "compiler_warning_found": False,
                    "log_path": command_log.name,
                    "log_sha256": gate_b.sha256(command_log),
                }
            ],
            "log_path": aggregate_log.name,
            "log_sha256": gate_b.sha256(aggregate_log),
            "checkout_state": {"tracked_clean": True},
            "campaign_manifest": {
                "path": str(campaign_json.relative_to(checkout)),
                "sha256": gate_b.sha256(campaign_json),
                "candidate_manifest_path": str(
                    candidate_manifest.relative_to(checkout)
                ),
                "candidate_manifest_sha256": gate_b.sha256(
                    candidate_manifest
                ),
                "seed_ledger_path": str(seed_ledger.relative_to(checkout)),
                "seed_ledger_sha256": gate_b.sha256(seed_ledger),
            },
            "submission_evidence": {},
            "raw_validation_evidence": raw_rows,
            "raw_validation_count": 9,
            "resource_metadata_evidence": [],
            "heavy_stability_audit": {},
            "tune_settings_audit": {},
            "origin_resolution_audits": [],
            "central_associate_origin_composition": [],
            "runtime_storage_benchmark": [],
            "full_candidate_resource_projection": {},
            "canonical_300m_resource_projection": {},
            "unresolved_trigger_candidates": unresolved,
            "pthat_sensitivity": {
                "path": str(pthat_path),
                "sha256": gate_b.sha256(pthat_path),
                "outcome": "SCIENTIFIC_REVIEW_REQUIRED",
                "blocking_reasons": [],
            },
        }
        original_path = original_dir / "gate_b_report.json"
        original_path.write_text(
            json.dumps(original, indent=2, sort_keys=True) + "\n"
        )
        inventory_rows = [
            {
                "path": str(path.relative_to(original_dir)),
                "bytes": path.stat().st_size,
                "sha256": gate_b.sha256(path),
            }
            for path in sorted(original_dir.rglob("*"))
            if path.is_file()
        ]
        (original_dir / "evidence_inventory.json").write_text(
            json.dumps(
                {
                    "schema":
                        "hf_publication_gate_b_evidence_inventory_v1",
                    "files": inventory_rows,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        gate_b.seal_tree(original_dir)
        signoff_path = campaign_dir / "GATE_B_PHYSICS_SIGNOFF.json"
        signoff = {
            "schema": resolver.SIGNOFF_SCHEMA,
            "approved": True,
            "campaign": "FIXTURE",
            "campaign_ordinal": 26,
            "repository_commit": commit,
            "gate_b_needs_signoff_report_sha256": gate_b.sha256(
                original_path
            ),
            "reviewed_unresolved_trigger_candidates": sample_counts,
            "reviewed_unresolved_trigger_candidates_total": 2,
            "allowed_unresolved_treatment": resolver.ALLOWED_TREATMENT,
            "reviewer": "Alice Example",
            "reviewer_role": "project owner",
            "decision_utc": "2026-07-30T10:00:00+00:00",
            "finding": (
                "Reviewed the exact unresolved-origin evidence and approved "
                "the declared exclusion and reporting treatment."
            ),
            "supersedes_state": "NEEDS_SIGNOFF",
        }
        write_read_only_json(signoff_path, signoff)
        output_dir = campaign_dir / "gate_b_signoff_resolved"
        try:
            status, report_path = resolver.create_resolution(
                checkout,
                original_path,
                signoff_path,
                output_dir,
            )
            assert status == 0
            resolved = json.loads(report_path.read_text())
            assert resolved["state"] == "PASS"
            assert resolved["canonical"] is True
            assert resolved["failure"] is None
            assert resolved["supersedes"]["sha256"] == gate_b.sha256(
                original_path
            )
            assert resolved["gate_b_physics_signoff"]["sha256"] == (
                gate_b.sha256(signoff_path)
            )
            assert len(resolved["raw_validation_evidence"]) == 9
            gate_d.validate_gate_b(
                report_path,
                {"campaign": "FIXTURE", "campaign_ordinal": 26},
                commit,
            )
            assert stat.S_IMODE(output_dir.stat().st_mode) == 0o555
            assert stat.S_IMODE(report_path.stat().st_mode) == 0o444
        finally:
            make_writable(checkout)


def main() -> int:
    test_raw_log_contract()
    test_decision_precedence()
    test_resource_summary_contract()
    test_origin_summary_marker_contract()
    test_unresolved_three_way_closure()
    test_pthat_exact_contract_and_signoff_routing()
    test_sealed_tree_is_read_only()
    test_immutable_input_contract()
    test_checkout_cleanliness_whitelists_only_operational_evidence()
    test_gate_b_signoff_is_exact_and_fail_closed()
    test_superseding_report_preserves_gate_d_raw_bindings()
    test_signoff_resolution_end_to_end_fixture()
    print("PUBLICATION_GATE_B_TESTS_PASS tests=12")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
