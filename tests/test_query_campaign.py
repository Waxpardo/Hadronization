import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from helpers import ROOT


def load_campaign():
    spec = importlib.util.spec_from_file_location(
        "query_campaign_contract", ROOT / "pipeline/query/campaign.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QueryCampaignContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.campaign = load_campaign()

    def plan(self, base, source_ids=(0, 1)):
        return {
            "schema": self.campaign.PLAN_SCHEMA,
            "collection": str(base / "collection"),
            "work_root": str(base / "work"),
            "analysis": {"path": str(base / "analysis.json"), "sha256": "1" * 64},
            "layout": {"path": str(base / "layout.json"), "sha256": "2" * 64},
            "dictionary": {"path": str(base / "dictionary.json"), "sha256": "3" * 64},
            "prepared_pack": str(base / "prepared"),
            "dictionary_body_sha256": "4" * 64,
            "inputs": [{
                "ordinal": 0,
                "root": {"path": str(base / "input.root"), "bytes": 10, "sha256": "5" * 64},
                "receipt": {"path": str(base / "input.json"), "bytes": 20, "sha256": "6" * 64},
                "accepted_receipt_sha256": "6" * 64,
                "source_ids": list(source_ids),
            }],
        }

    def test_worker_argv_is_explicit_prepared_pinned_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            plan = self.plan(base)
            command = self.campaign.worker_argv(plan, 0)
            self.assertEqual(command[3:5], ["query", "build"])
            self.assertEqual(command[command.index("--accepted-receipt-sha256") + 1], "6" * 64)
            self.assertEqual(command[command.index("--prepared-pack") + 1], str(base / "prepared"))
            self.assertEqual(command[command.index("--layout") + 1], str(base / "layout.json"))
            output = base / "collection/shards/shard-0000"
            self.assertEqual(command[command.index("--output") + 1], str(output))
            output.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "verify, never overwrite"):
                self.campaign.worker_argv(plan, 0)

    def test_census_argv_requires_complete_contiguous_source_domain(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            command = self.campaign.census_argv(self.plan(base), base / "census.json")
            self.assertEqual(command[3:5], ["query", "census"])
            self.assertIn("--prepared-pack", command)
            self.assertIn("--accepted-receipt-sha256", command)
            with self.assertRaisesRegex(ValueError, "complete contiguous campaign source domain"):
                self.campaign.census_argv(self.plan(base, (10, 11)), base / "census.json")

    def test_content_pins_require_separate_caller_digest_and_external_authority(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary).resolve() / "pins.json"
            payload = {"schema": self.campaign.PINS_SCHEMA,
                       "scientific_acceptance": "EXTERNAL",
                       "pins": [{"ordinal": 0, "scientific_content_sha256": "a" * 64}]}
            path.write_text(self.campaign.r.canonical(payload), encoding="ascii")
            digest = self.campaign.r.sha_file(path)
            self.assertEqual(self.campaign.read_content_pins(path, digest, [0]), {0: "a" * 64})
            with self.assertRaisesRegex(ValueError, "trusted digest"):
                self.campaign.read_content_pins(path, "b" * 64, [0])
            payload["scientific_acceptance"] = "LOCAL"
            path.write_text(self.campaign.r.canonical(payload), encoding="ascii")
            with self.assertRaisesRegex(ValueError, "external authority"):
                self.campaign.read_content_pins(path, self.campaign.r.sha_file(path), [0])

    def test_close_verifies_first_and_writes_only_manifest_last(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            plan = self.plan(base)
            plan["_trusted_sha256"] = "7" * 64
            (base / "collection/shards").mkdir(parents=True)
            failed = self.campaign.q.create_query_stage(
                base / "collection/shards/shard-9999", base / "work")
            (failed / "partial-query.root").write_text("preserved outside collection")
            self.campaign.q.preserve_query_failure(
                failed, base / "collection/shards/shard-9999", ValueError("synthetic"))
            records = [{"ordinal": 0, "source_ids": [0, 1],
                        "scientific_content_sha256": "a" * 64}]
            with mock.patch.object(self.campaign, "verify_collection", return_value=records) as verify:
                path = self.campaign.close_collection(plan, base / "pins.json", "8" * 64)
            verify.assert_called_once()
            self.assertEqual({item.name for item in (base / "collection").iterdir()},
                             {"shards", "manifest.json"})
            manifest = json.loads(path.read_text())
            self.assertEqual(manifest["state"], "VERIFIED_NONPUBLICATION_COLLECTION")
            self.assertEqual(manifest["scientific_acceptance"], "EXTERNAL_REQUIRED")
            self.assertEqual(manifest["plan_sha256"], "7" * 64)
            self.assertTrue((failed / "partial-query.root").is_file())
            self.assertTrue((failed / "failure.json").is_file())
            with self.assertRaisesRegex(ValueError, "already exists"):
                self.campaign.close_collection(plan, base / "pins.json", "8" * 64)

    def test_public_dispatch_exposes_only_finite_campaign_commands(self):
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "hadronization"), "query", "campaign", "--help"],
            text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("plan", "worker-argv", "census-argv", "verify", "close"):
            self.assertIn(command, result.stdout)
        source = (ROOT / "pipeline/query/campaign.py").read_text()
        self.assertNotIn("pipeline/query/anchors.py", source)
        self.assertNotIn("shutil.rmtree", source)
        self.assertNotIn("ssh", source)


if __name__ == "__main__":
    unittest.main()
