import re
import unittest

from helpers import ROOT, TUNES, TUNE_INDEX, csv_rows, load_json, sha256


class CampaignContract(unittest.TestCase):
    def test_canonical_manifest_membership_order_and_hash(self):
        path = ROOT / "data/raw_manifest.jsonl"
        self.assertEqual(
            sha256(path),
            "5f354cbc9e0bdfb7ead07adb341d74e4c98f14709d873f8f247585912e2df247")
        rows = [load for load in map(__import__("json").loads,
                                     path.read_text(encoding="utf-8").splitlines())]
        self.assertEqual(len(rows), 3000)
        self.assertEqual(
            [(row["tune"], row["logical_id"]) for row in rows],
            [(tune, logical_id) for tune in TUNES for logical_id in range(1000)])
        for row in rows:
            self.assertEqual(row["block"], row["logical_id"] % 10 + 1)
            self.assertEqual(row["successful_events"], 100000)
            self.assertFalse(row["raw_storage_key"].startswith("/"))
            self.assertNotIn("..", row["raw_storage_key"].split("/"))
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
        accepted_by_key = {(row["tune"], int(row["logical_id"])): row
                           for row in accepted}
        for raw in manifest:
            attempt = accepted_by_key[(raw["tune"], raw["logical_id"])]
            self.assertEqual(int(attempt["attempt"]), raw["accepted_attempt"])
            self.assertEqual(int(attempt["seed"]), raw["accepted_seed"])
            self.assertEqual(attempt["raw_storage_key"], raw["raw_storage_key"])

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
