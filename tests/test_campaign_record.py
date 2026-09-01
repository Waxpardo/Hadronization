#!/usr/bin/env python3
"""Independent contract checks for the canonical HF_RUN3_V1 campaign record."""

from __future__ import annotations

import csv
import json
import os
import re
from collections import Counter
from pathlib import Path, PurePosixPath


ROOT = Path(os.environ.get("RESULTS1_ROOT", Path(__file__).resolve().parents[1]))
DATA = ROOT / "data"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
TUNE_INDEX = {tune: index for index, tune in enumerate(TUNES)}
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    raise AssertionError(message)


campaign = json.loads((DATA / "campaign.json").read_text(encoding="utf-8"))
raw_lines = (DATA / "raw_manifest.jsonl").read_text(encoding="utf-8").splitlines()
raw = [json.loads(line) for line in raw_lines]
with (DATA / "attempts.csv").open(encoding="utf-8", newline="") as handle:
    attempts = list(csv.DictReader(handle))

assert campaign["schema"] == "hadronization_campaign_record_v1"
assert campaign["campaign"] == "HF_RUN3_V1"
assert campaign["tune_order"] == list(TUNES)
assert campaign["logical_jobs_per_tune"] == 1000
assert campaign["successful_events_per_logical_job"] == 100_000
assert campaign["successful_events_per_tune"] == 100_000_000
assert campaign["blocks"] == {"count": 10, "logical_id_domain": [0, 999],
                              "logical_id_rule": "block=(logical_id%10)+1"}
assert campaign["systematic_uncertainties"] == "disabled"
assert campaign["held_attempt_policy"] == "record_and_disclose_no_correction"

if len(raw) != 3000:
    fail(f"raw-manifest row count: {len(raw)} != 3000")
raw_identity = {(row["tune"], row["logical_id"]) for row in raw}
if len(raw_identity) != 3000:
    fail("raw-manifest tune/logical_id identity is not unique")
if Counter(row["tune"] for row in raw) != Counter({tune: 1000 for tune in TUNES}):
    fail("raw-manifest tune distribution differs from 1000/1000/1000")
if Counter((row["tune"], row["block"]) for row in raw) != Counter(
        {(tune, block): 100 for tune in TUNES for block in range(1, 11)}):
    fail("raw-manifest block distribution differs from 100 per tune/block")

for row, serialized in zip(raw, raw_lines):
    tune = row["tune"]
    logical_id = row["logical_id"]
    attempt = row["accepted_attempt"]
    expected_seed = 100_000_001 + 3 * 10_000_000 + TUNE_INDEX[tune] * 1_000_000 + attempt * 100_000 + logical_id
    assert row["block"] == logical_id % 10 + 1
    if row["accepted_seed"] != expected_seed:
        fail(f"accepted attempt ordinal/seed mismatch: {tune}/{logical_id}")
    assert isinstance(row["bytes"], int) and row["bytes"] > 0
    assert row["successful_events"] == 100_000
    for key in ("raw_sha256", "validation_log_sha256", "validation_receipt_sha256"):
        assert SHA256.fullmatch(row[key]), (tune, logical_id, key)
    key = PurePosixPath(row["raw_storage_key"])
    assert not key.is_absolute() and ".." not in key.parts and key.parts[0] == tune
    if any(fragment in serialized for fragment in ("/data/alice", "/Users/", "deploys/", "6729b3f0b7b9/")):
        fail(f"nonportable source path leaked into raw manifest: {tune}/{logical_id}")

if len(attempts) != 3127:
    fail(f"attempt row count: {len(attempts)} != 3127")
attempt_identity = {(row["tune"], int(row["logical_id"]), int(row["attempt"])) for row in attempts}
if len(attempt_identity) != 3127:
    fail("attempt identity is not unique")
allowed_evidence = {"accepted_manifest_and_scheduler_log_confirmed", "accepted_manifest_confirmed",
                    "scheduler_log_confirmed", "inferred_from_accepted_attempt_ordinal"}
if {row["evidence_status"] for row in attempts} - allowed_evidence:
    fail("unsupported discard mechanism/evidence label")
if {row["outcome"] for row in attempts} != {"accepted", "discarded"}:
    fail("attempt outcome is not accepted/discarded")

accepted = [row for row in attempts if row["outcome"] == "accepted"]
discarded = [row for row in attempts if row["outcome"] == "discarded"]
if len(accepted) != 3000:
    fail("accepted attempt count differs from raw-manifest count")
discard_distribution = Counter(row["tune"] for row in discarded)
if discard_distribution != Counter({"JUNCTIONS": 63, "CLOSEPACKING": 64}):
    fail(f"discard distribution differs from 0/63/64: {discard_distribution}")

raw_join = {(row["tune"], row["logical_id"]): row for row in raw}
for row in attempts:
    tune, logical_id, attempt = row["tune"], int(row["logical_id"]), int(row["attempt"])
    expected_seed = 100_000_001 + 3 * 10_000_000 + TUNE_INDEX[tune] * 1_000_000 + attempt * 100_000 + logical_id
    if int(row["seed"]) != expected_seed:
        fail(f"attempt seed mismatch: {tune}/{logical_id}/{attempt}")
    if row["outcome"] == "accepted":
        source = raw_join[(tune, logical_id)]
        if attempt != source["accepted_attempt"]:
            fail(f"accepted attempt ordinal does not join raw manifest: {tune}/{logical_id}")
        assert int(row["seed"]) == source["accepted_seed"]
        assert row["raw_storage_key"] == source["raw_storage_key"]
    elif row["raw_storage_key"]:
        fail(f"discarded attempt has a raw storage key: {tune}/{logical_id}/{attempt}")

print("PASS test_campaign_record.py")
