import re
from collections import defaultdict
import copy
import json
from pathlib import PurePosixPath
import unittest

from helpers import ROOT, TUNES, TUNE_INDEX, csv_rows, load_json, sha256


def validate_attempt_topology(manifest, attempts):
    raw = {(row["tune"], int(row["logical_id"])): row for row in manifest}
    if len(raw) != 3000:
        raise AssertionError("raw logical identity is not unique/complete")
    identities = [(row["tune"], int(row["logical_id"]), int(row["attempt"]))
                  for row in attempts]
    if len(identities) != len(set(identities)):
        raise AssertionError("attempt identity is not unique")
    if {row["outcome"] for row in attempts} != {"accepted", "discarded"}:
        raise AssertionError("attempt outcome label is unsupported")
    allowed_evidence = {"accepted_manifest_and_scheduler_log_confirmed",
                        "accepted_manifest_confirmed", "scheduler_log_confirmed",
                        "inferred_from_accepted_attempt_ordinal"}
    if {row["evidence_status"] for row in attempts} - allowed_evidence:
        raise AssertionError("attempt evidence label is unsupported")
    groups = defaultdict(list)
    for row in attempts:
        tune, logical_id, attempt = row["tune"], int(row["logical_id"]), int(row["attempt"])
        key = (tune, logical_id)
        if key not in raw:
            raise AssertionError("attempt lies outside raw identity domain")
        expected_seed = 130000001 + TUNE_INDEX[tune] * 1000000 + attempt * 100000 + logical_id
        if int(row["seed"]) != expected_seed:
            raise AssertionError("attempt seed formula mismatch")
        if row["outcome"] == "discarded" and row["raw_storage_key"]:
            raise AssertionError("discarded attempt carries a raw storage key")
        groups[key].append(row)
    if set(groups) != set(raw):
        raise AssertionError("attempt coverage is not exactly all 3000 identities")
    for key, source in raw.items():
        group = groups[key]
        accepted_attempt = int(source["accepted_attempt"])
        if [int(row["attempt"]) for row in group] != list(range(accepted_attempt + 1)):
            raise AssertionError("attempt sequence is not exactly 0..accepted_attempt")
        accepted = [row for row in group if row["outcome"] == "accepted"]
        if len(accepted) != 1 or accepted[0] is not group[-1]:
            raise AssertionError("accepted attempt is not unique and final")
        final = accepted[0]
        if (int(final["attempt"]), int(final["seed"]), final["raw_storage_key"]) != (
                accepted_attempt, int(source["accepted_seed"]), source["raw_storage_key"]):
            raise AssertionError("accepted attempt does not join the raw manifest")


class CampaignContract(unittest.TestCase):
    def test_canonical_manifest_membership_order_and_hash(self):
        path = ROOT / "data/raw_manifest.jsonl"
        self.assertEqual(
            sha256(path),
            "5f354cbc9e0bdfb7ead07adb341d74e4c98f14709d873f8f247585912e2df247")
        lines = path.read_text(encoding="utf-8").splitlines()
        rows = [json.loads(line) for line in lines]
        self.assertEqual(len(rows), 3000)
        self.assertEqual(
            [(row["tune"], row["logical_id"]) for row in rows],
            [(tune, logical_id) for tune in TUNES for logical_id in range(1000)])
        for row, serialized in zip(rows, lines):
            self.assertEqual(
                json.dumps(row, sort_keys=True, separators=(",", ":")),
                serialized)
            self.assertEqual(row["block"], row["logical_id"] % 10 + 1)
            self.assertEqual(row["successful_events"], 100000)
            self.assertFalse(row["raw_storage_key"].startswith("/"))
            self.assertNotIn("..", row["raw_storage_key"].split("/"))
            self.assertEqual(PurePosixPath(row["raw_storage_key"]).parts[0], row["tune"])
            expected = (130000001 + TUNE_INDEX[row["tune"]] * 1000000
                        + row["accepted_attempt"] * 100000
                        + row["logical_id"])
            self.assertEqual(row["accepted_seed"], expected)

    def test_attempt_order_counts_and_final_join(self):
        rows = csv_rows("data/attempts.csv")
        self.assertEqual(len(rows), 3127)
        self.assertEqual(
            sha256(ROOT / "data/attempts.csv"),
            "c550fffb652d0ff71945ee128cfc8fe475d9b1d64433454e9073fd2076c5d8d9")
        order = [(TUNE_INDEX[row["tune"]], int(row["logical_id"]),
                  int(row["attempt"])) for row in rows]
        self.assertEqual(order, sorted(order))
        accepted = [row for row in rows if row["outcome"] == "accepted"]
        discarded = [row for row in rows if row["outcome"] == "discarded"]
        self.assertEqual((len(accepted), len(discarded)), (3000, 127))
        self.assertEqual(
            {tune: sum(row["tune"] == tune for row in discarded) for tune in TUNES},
            {"MONASH": 0, "JUNCTIONS": 63, "CLOSEPACKING": 64})
        manifest = [__import__("json").loads(line) for line in
                    (ROOT / "data/raw_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
        validate_attempt_topology(manifest, rows)
        accepted_by_key = {(row["tune"], int(row["logical_id"])): row
                           for row in accepted}
        for raw in manifest:
            attempt = accepted_by_key[(raw["tune"], raw["logical_id"])]
            self.assertEqual(int(attempt["attempt"]), raw["accepted_attempt"])
            self.assertEqual(int(attempt["seed"]), raw["accepted_seed"])
            self.assertEqual(attempt["raw_storage_key"], raw["raw_storage_key"])

    def test_topology_gate_rejects_broken_sequence_and_duplicate_acceptance(self):
        manifest = [json.loads(line) for line in
                    (ROOT / "data/raw_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
        attempts = csv_rows("data/attempts.csv")
        broken = copy.deepcopy(attempts)
        target = next(index for index, row in enumerate(broken)
                      if row["tune"] == "JUNCTIONS" and row["logical_id"] == "3" and
                      row["attempt"] == "0")
        del broken[target]
        with self.assertRaisesRegex(AssertionError, "sequence"):
            validate_attempt_topology(manifest, broken)
        duplicate = copy.deepcopy(attempts)
        target = next(row for row in duplicate if row["tune"] == "JUNCTIONS" and
                      row["logical_id"] == "3" and row["attempt"] == "0")
        target["outcome"] = "accepted"
        with self.assertRaisesRegex(AssertionError, "unique and final"):
            validate_attempt_topology(manifest, duplicate)

    def test_campaign_facts_and_current_definition_digests(self):
        campaign = load_json("data/campaign.json")
        self.assertEqual(campaign["tune_order"], list(TUNES))
        self.assertEqual(campaign["logical_jobs_per_tune"], 1000)
        self.assertEqual(campaign["successful_events_per_logical_job"], 100000)
        self.assertEqual(campaign["runtime"]["pythia_version"], "8.317")
        self.assertEqual(campaign["held_attempt_policy"],
                         "record_and_disclose_no_correction")
        self.assertEqual(campaign["systematic_uncertainties"], "disabled")
        for entry in campaign["current_interpretation_definitions"]["files"]:
            path = ROOT / entry["path"]
            self.assertTrue(path.is_file(), entry["path"])
            self.assertEqual(path.stat().st_size, entry["bytes"])
            self.assertEqual(sha256(path), entry["sha256"])


if __name__ == "__main__":
    unittest.main()
