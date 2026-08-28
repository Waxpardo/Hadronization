#!/usr/bin/env python3
"""Synthetic source-contract tests for the exhaustive settings receipt."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import write_effective_settings_receipt as receipt_tool  # noqa: E402
from write_effective_settings_receipt import (  # noqa: E402
    EFFECTIVE_SETTINGS_SCHEMA, TUNES, compare_effective_settings,
    effective_settings_digest, serialize_effective_settings,
)

ALLOWLIST_PATH = ROOT / "config/tune_difference_allowlist_v1.json"
ALLOWLIST_BYTES = ALLOWLIST_PATH.read_bytes()
ALLOWLIST = json.loads(ALLOWLIST_BYTES)
ALLOWLIST_SHA = hashlib.sha256(ALLOWLIST_BYTES).hexdigest()


def source(tune: str, values: dict[str, str]) -> dict:
    rows = sorted(values.items())
    canonical = serialize_effective_settings(rows).decode()
    digest = effective_settings_digest(rows)
    return {
        "expected_tune": tune,
        "observed_tune": tune,
        "basename": f"raw_{tune}.root",
        "sha256": {"MONASH": "1", "JUNCTIONS": "2", "CLOSEPACKING": "3"}[
            tune] * 64,
        "raw_schema": "hf_primary_ground_raw_v7",
        "tune_difference_allowlist_schema": receipt_tool.ALLOWLIST_SCHEMA,
        "tune_difference_allowlist_sha256": ALLOWLIST_SHA,
        "effective_settings_schema": EFFECTIVE_SETTINGS_SCHEMA,
        "effective_settings_sha256": digest,
        "effective_settings_entries": len(rows),
        "repository_commit": "a" * 40,
        "repository_dirty": "false",
        "complete": 1,
        "settings": rows,
        "effective_settings_canonical_object": canonical,
        "effective_settings_sha256_object": digest,
    }


def passing_sources() -> dict[str, dict]:
    common = dict(ALLOWLIST["common_required_card_values"])
    sources = {}
    for index, tune in enumerate(TUNES, start=1):
        values = {
            **common,
            "Random:seed": str(100 + index),
            "StringZ:aLund": {"MONASH": "0.68", "JUNCTIONS": "0.36",
                              "CLOSEPACKING": "0.68"}[tune],
            "Synthetic:common": "same",
        }
        sources[tune] = source(tune, values)
    return sources


def assert_failure(receipt: dict, fragment: str) -> None:
    assert receipt["status"] == "FAIL", receipt
    assert any(fragment in error for error in receipt["errors_refusals"]), receipt


def test_pass_records_allowed_and_per_job_differences() -> None:
    receipt = compare_effective_settings(passing_sources(), ALLOWLIST, ALLOWLIST_SHA)
    assert receipt["status"] == "PASS", receipt["errors_refusals"]
    assert receipt["schema"] == "hadronization_effective_tune_settings_receipt_v1"
    assert receipt["effective_setting_count"] == len(
        passing_sources()["MONASH"]["settings"])
    classifications = {row["name"]: row["classification"]
                       for row in receipt["differences"]}
    assert classifications["StringZ:aLund"] == "allowed_tune_difference"
    assert classifications["Random:seed"] == "excluded_per_job_difference"
    assert receipt["resolved_tune_difference_count"] == 1
    assert all(row["status"] == "PASS"
               for row in receipt["required_common_value_checks"])


def test_forbidden_difference_writes_failure_evidence() -> None:
    sources = passing_sources()
    for index, tune in enumerate(TUNES):
        values = dict(sources[tune]["settings"])
        values["Synthetic:forbidden"] = str(index)
        sources[tune] = source(tune, values)
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(receipt, "forbidden resolved setting difference: Synthetic:forbidden")
    row = next(row for row in receipt["differences"]
               if row["name"] == "Synthetic:forbidden")
    assert row["classification"] == "forbidden_difference"
    assert set(row["values"]) == set(TUNES)


def test_forbidden_difference_returns_nonzero_and_writes_failure_receipt() -> None:
    sources = passing_sources()
    for index, tune in enumerate(TUNES):
        values = dict(sources[tune]["settings"])
        values["Synthetic:forbidden"] = str(index)
        sources[tune] = source(tune, values)
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "receipt.json"
        with mock.patch.object(
                receipt_tool, "load_root_source",
                side_effect=lambda _path, tune: sources[tune]):
            status = receipt_tool.main([
                "--monash", "MONASH.root",
                "--junctions", "JUNCTIONS.root",
                "--closepacking", "CLOSEPACKING.root",
                "--allowlist", str(ALLOWLIST_PATH),
                "--output", str(output),
            ])
        written = json.loads(output.read_text())
    assert status != 0
    assert written["status"] == "FAIL"
    assert any("Synthetic:forbidden" in error
               for error in written["errors_refusals"])


def test_missing_catalogue_entry_is_refused() -> None:
    sources = passing_sources()
    values = dict(sources["CLOSEPACKING"]["settings"])
    del values["Synthetic:common"]
    sources["CLOSEPACKING"] = source("CLOSEPACKING", values)
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(receipt, "CLOSEPACKING: catalogue missing")
    assert receipt["effective_setting_count"] is None


def test_duplicate_key_is_refused_even_with_matching_digest() -> None:
    sources = passing_sources()
    broken = copy.deepcopy(sources["JUNCTIONS"])
    broken["settings"].append(broken["settings"][0])
    broken["effective_settings_entries"] = len(broken["settings"])
    canonical = serialize_effective_settings(broken["settings"]).decode()
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    broken["effective_settings_canonical_object"] = canonical
    broken["effective_settings_sha256"] = digest
    broken["effective_settings_sha256_object"] = digest
    sources["JUNCTIONS"] = broken
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(receipt, "JUNCTIONS: duplicate effective_settings name")


def test_bad_digest_is_refused() -> None:
    sources = passing_sources()
    sources["MONASH"]["effective_settings_sha256"] = "f" * 64
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(
        receipt, "MONASH: effective_settings_sha256 does not match reconstructed digest")


def test_missing_embedded_allowlist_schema_is_refused() -> None:
    sources = passing_sources()
    del sources["MONASH"]["tune_difference_allowlist_schema"]
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(receipt, "MONASH: embedded allowlist pin schema is absent")
    assert receipt["inputs"]["MONASH"]["tune_difference_allowlist_schema"] is None


def test_wrong_embedded_allowlist_schema_is_refused() -> None:
    sources = passing_sources()
    sources["JUNCTIONS"]["tune_difference_allowlist_schema"] = "wrong_schema"
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(receipt, "JUNCTIONS: embedded allowlist pin schema")
    assert_failure(receipt, "raw embedded allowlist pin schemas disagree across tunes")


def test_malformed_embedded_allowlist_digest_is_refused() -> None:
    sources = passing_sources()
    sources["CLOSEPACKING"]["tune_difference_allowlist_sha256"] = "ABC123"
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(receipt, "CLOSEPACKING: embedded allowlist pin SHA-256 is malformed")


def test_missing_embedded_allowlist_digest_is_refused() -> None:
    sources = passing_sources()
    del sources["CLOSEPACKING"]["tune_difference_allowlist_sha256"]
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(receipt, "CLOSEPACKING: embedded allowlist pin SHA-256 is absent")


def test_different_well_formed_embedded_digest_is_refused() -> None:
    sources = passing_sources()
    sources["MONASH"]["tune_difference_allowlist_sha256"] = "e" * 64
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(
        receipt,
        "MONASH: embedded allowlist pin SHA-256 does not match the supplied allowlist file")


def test_one_tune_embedded_digest_disagreement_is_refused() -> None:
    sources = passing_sources()
    sources["JUNCTIONS"]["tune_difference_allowlist_sha256"] = "d" * 64
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(receipt, "raw embedded allowlist pin SHA-256 values disagree across tunes")


def test_all_embedded_digests_agree_but_not_with_supplied_file_is_refused() -> None:
    sources = passing_sources()
    for source_record in sources.values():
        source_record["tune_difference_allowlist_sha256"] = "c" * 64
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(
        receipt,
        "MONASH: embedded allowlist pin SHA-256 does not match the supplied allowlist file")
    assert not any("values disagree across tunes" in error
                   for error in receipt["errors_refusals"])


def test_seen_to_fail_architect_wrong_embedded_pin_mutation_is_refused() -> None:
    sources = passing_sources()
    for source_record in sources.values():
        source_record["tune_difference_allowlist_schema"] = "wrong_schema"
        source_record["tune_difference_allowlist_sha256"] = "f" * 64
    receipt = compare_effective_settings(sources, ALLOWLIST, ALLOWLIST_SHA)
    assert_failure(receipt, "embedded allowlist pin schema")
    assert_failure(receipt, "embedded allowlist pin SHA-256")
    assert all(
        "tune_difference_allowlist_schema" in receipt["inputs"][tune]
        and "tune_difference_allowlist_sha256" in receipt["inputs"][tune]
        for tune in TUNES)


def test_wrong_embedded_pin_returns_nonzero_and_writes_failure_receipt() -> None:
    sources = passing_sources()
    for source_record in sources.values():
        source_record["tune_difference_allowlist_schema"] = "wrong_schema"
        source_record["tune_difference_allowlist_sha256"] = "f" * 64
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "receipt.json"
        with mock.patch.object(
                receipt_tool, "load_root_source",
                side_effect=lambda _path, tune: sources[tune]):
            status = receipt_tool.main([
                "--monash", "MONASH.root",
                "--junctions", "JUNCTIONS.root",
                "--closepacking", "CLOSEPACKING.root",
                "--allowlist", str(ALLOWLIST_PATH),
                "--output", str(output),
            ])
        written = json.loads(output.read_text())
    assert status != 0
    assert_failure(written, "embedded allowlist pin schema")
    assert_failure(written, "embedded allowlist pin SHA-256")


def main() -> int:
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"effective settings receipt: {len(tests)} synthetic checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
