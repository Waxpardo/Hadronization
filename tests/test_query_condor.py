"""Inert 323-node native DAG and immutable local staging contracts."""

import importlib.util
import copy
import errno
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/query_multitune/queries/shard-0000"
spec = importlib.util.spec_from_file_location("tested_condor", ROOT / "pipeline/query/condor.py")
condor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(condor)


class QueryCondorPreparation(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        files = []
        for ordinal in range(323):
            for role, suffix in (("receipt", "json"), ("root_file", "root")):
                files.append({"ordinal": ordinal, "role": role,
                              "path": "inputs/shard-%04d.%s" % (ordinal, suffix),
                              "bytes": 1 if role == "receipt" else 158720142481 // 323 +
                              (1 if ordinal < 158720142481 % 323 else 0),
                              "sha256": "a" * 64})
        manifest = {"schema": "phasea_arch_full_input_acquisition_manifest_v1",
                    "status": "ALL_323_ACCEPTED_INPUT_PAIRS_REVERIFIED",
                    "pair_count": 323, "input_file_count": 646,
                    "accepted_root_bytes": 158720142481, "files": files}
        self.acquisition = self.base / "acquisition.json"
        self.acquisition.write_text(json.dumps(manifest))

    def tearDown(self):
        self.temporary.cleanup()

    def test_inert_dag_has_exact_domain_retry_budget_and_frozen_bootstrap(self):
        dictionary = FIXTURE / "dictionary.json"
        bundle = self.base / "bundle"
        condor.prepare(self.acquisition, condor.r.sha_file(self.acquisition),
                       dictionary, condor.r.sha_file(dictionary), bundle)
        work = condor.r.json_file(bundle / "work.json")
        self.assertEqual(work["state"], "INERT_SITE_BINDING_REQUIRED")
        self.assertEqual(work["expected_source_count"], 3000)
        self.assertEqual(work["expected_event_count"], 300000000)
        self.assertEqual(work["campaign_id"], "HF_RUN3_V1")
        self.assertEqual(work["block_count"], 10)
        self.assertEqual(len(work["work"]), 323)
        dag = (bundle / "workflow.dag").read_text()
        self.assertEqual(dag.count("RETRY q"), 323)
        self.assertEqual(dag.count("ABORT-DAG-ON q"), 323)
        self.assertIn("MAXJOBS query 4", dag)
        self.assertIn("RETRY q0322 2 UNLESS-EXIT 42", dag)
        self.assertIn("__MEASURED_MEMORY_MB__", (bundle / "worker.sub").read_text())
        admission = json.loads((bundle / "SITE_ADMISSION_TEMPLATE.json").read_text())
        self.assertEqual(admission["decision"], "PENDING")
        self.assertEqual(admission["execute_node_canary"], "PENDING")
        self.assertNotIn("query-pack.tar.gz", {p.name for p in bundle.iterdir()})
        self.assertIn("test ! -e workflow.dag", (bundle / "BUILD_LINUX_PACK.sh").read_text())
        self.assertIn("stage-dag", (bundle / "README.txt").read_text())
        command = [sys.executable, "-B", str(bundle / "preflight.py"), "preflight",
                   "--work", str(bundle / "work.json"), "--expected-work-sha256",
                   condor.r.sha_file(bundle / "work.json"), "--source-tar", str(bundle / "source.tar.gz")]
        checked = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertTrue(json.loads(checked.stdout)["source_tar_ok"])
        blocked = subprocess.run(command[:2] + [str(bundle / "worker.py"), "worker",
                                 "--work", str(bundle / "work.json"),
                                 "--expected-work-sha256", condor.r.sha_file(bundle / "work.json"),
                                 "--ordinal", "0", "--attempt", "0",
                                 "--source-tar", str(bundle / "source.tar.gz"),
                                 "--pack-tar", str(bundle / "query-pack.tar.gz")],
                                 capture_output=True, text=True)
        self.assertEqual(blocked.returncode, 42)
        self.assertIn("site/runtime/storage admission is not bound", blocked.stderr)

    def test_no_overwrite_attempt_stage_and_durable_readback(self):
        destination = self.base / "bulk/shard-0000/attempt-00"
        receipt = condor._stage_workspace(FIXTURE, destination, 0, 0, "a" * 64)
        self.assertEqual(receipt["ordinal"], 0)
        self.assertEqual(condor.r.sha_file(destination / "workspace/query.root"),
                         receipt["artifacts"]["query.root"]["sha256"])
        with self.assertRaises(ValueError):
            condor._stage_workspace(FIXTURE, destination, 0, 0, "a" * 64)

    def test_render_collector_keeps_site_bundle_immutable_and_requires_all_pins(self):
        bundle = self.base / "site-bound"
        bulk, control = self.base / "bulk", self.base / "control"
        bundle.mkdir(); (control / "pins").mkdir(parents=True)
        attempt_dir = bulk / "shard-0000/attempt-00"
        attempt_dir.mkdir(parents=True)
        work = {"schema": condor.WORK_SCHEMA, "state": "SITE_BOUND",
                "storage_semantics": "POSIX_NOOVERWRITE_VERIFIED",
                "site_admission_sha256": "a" * 64,
                "prepared_pack_tar_sha256": "b" * 64,
                "input_root": str(self.base / "input"),
                "durable_bulk_root": str(bulk), "durable_control_root": str(control),
                "input_file_count": 2, "input_root_bytes": 1,
                "campaign_id": "TEST_ONLY", "block_count": 1,
                "tune_ordinals": {"TEST": 0},
                "expected_source_count": 1, "expected_event_count": 1,
                "work": [{"ordinal": 0, "root": {"bytes": 1}}]}
        for name, key in (("source.tar.gz", "source_tar_sha256"),
                          ("source-files.json", "source_files_sha256"),
                          ("dictionary.json", "dictionary_sha256"),
                          ("query-pack.tar.gz", "prepared_pack_tar_sha256")):
            (bundle / name).write_text("TEST_ONLY " + name)
            work[key] = condor.r.sha_file(bundle / name)
        (bundle / "work.json").write_text(json.dumps(work))
        work_sha = condor.r.sha_file(bundle / "work.json")
        (bundle / "worker.py").write_text("TEST_ONLY bootstrap")
        (bundle / "worker.sub").write_text(
            "arguments = worker.py --expected-work-sha256 " + work_sha + "\n"
            "transfer_input_files = worker.py,work.json,source.tar.gz,source-files.json,dictionary.json,query-pack.tar.gz\n")
        (bundle / "workflow.dag").write_text(
            "MAXJOBS query 4\nJOB q0000 worker.sub\nRETRY q0000 2 UNLESS-EXIT 42\n"
            "ABORT-DAG-ON q0000 42\n")
        template = ("arguments = collector.py collect --pins "
                    "__EXTERNALLY_ACCEPTED_PINS_PATH__ --expected-pins-sha256 "
                    "__EXTERNALLY_ACCEPTED_PINS_SHA256__\n"
                    "initialdir = " + str(bundle) + "\n")
        (bundle / "collector.sub").write_text(template)
        files = {path.name: {"bytes": path.stat().st_size, "sha256": condor.r.sha_file(path)}
                 for path in bundle.iterdir()}
        (bundle / "bundle-manifest.json").write_text(json.dumps({
            "schema": "hadronization_site_bound_condor_bundle_v1", "state": "SITE_BOUND",
            "work_sha256": work_sha, "files": files}))
        bundle_sha = condor.r.sha_file(bundle / "bundle-manifest.json")
        launch = self.base / "launch"
        workflow = condor.stage_dag(bundle, bundle_sha, launch)
        self.assertEqual(workflow, launch / "workflow.dag")
        self.assertEqual(condor.r.json_file(launch / "launch-receipt.json")["worker_count"], 1)
        self.assertEqual(condor.r.sha_file(bundle / "bundle-manifest.json"), bundle_sha)
        with self.assertRaisesRegex(ValueError, "distinct unused"):
            condor.stage_dag(bundle, bundle_sha, launch)
        content = "c" * 64
        (attempt_dir / "attempt.json").write_text(json.dumps({
            "schema": condor.ATTEMPT_SCHEMA, "ordinal": 0, "attempt": 0,
            "work_sha256": work_sha, "scientific_content_sha256": content}))
        pins_path = control / "pins/accepted.json"
        pins_path.write_text(json.dumps({"schema": condor.PINS_SCHEMA,
                                        "authority": "EXTERNAL_REVIEW",
                                        "pins": [{"ordinal": 0, "attempt": 0,
                                                  "scientific_content_sha256": content}]}))
        pins_sha = condor.r.sha_file(pins_path)
        output = control / "collector-submissions/rendered"
        submit = condor.render_collector(bundle, bundle_sha, pins_path, pins_sha, output)
        self.assertEqual(submit, output / "collector.sub")
        self.assertIn(str(pins_path), submit.read_text())
        self.assertIn(pins_sha, submit.read_text())
        self.assertEqual((bundle / "collector.sub").read_text(), template)
        self.assertEqual(condor.r.json_file(output / "receipt.json")["accepted_attempts"], 1)
        with self.assertRaisesRegex(ValueError, "unused control custody"):
            condor.render_collector(bundle, bundle_sha, pins_path, pins_sha, output)
        (attempt_dir / "attempt.json").unlink()
        with self.assertRaisesRegex(ValueError, "not a regular file"):
            condor.render_collector(bundle, bundle_sha, pins_path, pins_sha,
                                    control / "collector-submissions/missing-attempt")

    def test_interrupted_private_stage_and_failed_attempt_never_publish_success(self):
        interrupted = self.base / "bulk/shard-0000/attempt-00"
        with mock.patch.object(condor.q, "publish_directory", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                condor._stage_workspace(FIXTURE, interrupted, 0, 0, "a" * 64)
        self.assertFalse(interrupted.exists())
        self.assertEqual(len(list(interrupted.parent.glob(".attempt-00.stage-*"))), 1)
        condor._stage_workspace(FIXTURE, interrupted, 0, 0, "a" * 64)
        first_sha = condor.r.sha_file(interrupted / "attempt.json")
        with self.assertRaises(ValueError):
            condor._stage_workspace(FIXTURE, interrupted, 0, 0, "a" * 64)
        self.assertEqual(condor.r.sha_file(interrupted / "attempt.json"), first_sha)
        failed = self.base / "bulk/shard-0000/attempt-01"
        result = subprocess.CompletedProcess([], 75, "partial stdout", "transient stderr")
        condor._stage_failure(failed, 0, 1, "a" * 64, result)
        self.assertFalse((failed / "attempt.json").exists())
        self.assertEqual(condor.r.json_file(failed / "failure.json")["state"],
                         "PRESERVED_FAILED_ATTEMPT")
        with self.assertRaises(ValueError):
            condor._stage_failure(failed, 0, 1, "a" * 64, result)

    def test_generated_bootstrap_classifies_startup_fault_and_two_retry_exhaustion(self):
        dictionary = FIXTURE / "dictionary.json"
        bundle = self.base / "bundle"
        condor.prepare(self.acquisition, condor.r.sha_file(self.acquisition),
                       dictionary, condor.r.sha_file(dictionary), bundle)
        work_sha = condor.r.sha_file(bundle / "work.json")
        dag = (bundle / "workflow.dag").read_text()
        retry = re.search(r"(?m)^RETRY q0000 ([0-9]+) UNLESS-EXIT ([0-9]+)$", dag)
        self.assertIsNotNone(retry)
        self.assertEqual((int(retry[1]), int(retry[2])), (2, 42))
        self.assertIn("ABORT-DAG-ON q0000 42", dag)
        custom = self.base / "sitecustomize"
        custom.mkdir()
        (custom / "sitecustomize.py").write_text(
            "import errno,os,pathlib\n"
            "original=pathlib.Path.read_bytes\n"
            "def injected(self):\n"
            " if self.name=='work.json' and os.environ.get('TEST_ONLY_BOOTSTRAP_EIO')=='1':\n"
            "  raise OSError(errno.EIO,'TEST_ONLY startup read fault')\n"
            " return original(self)\n"
            "pathlib.Path.read_bytes=injected\n")
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(custom)
        environment["TEST_ONLY_BOOTSTRAP_EIO"] = "1"
        command = [sys.executable, "-B", str(bundle / "worker.py"), "worker",
                   "--work", str(bundle / "work.json"), "--expected-work-sha256", work_sha,
                   "--ordinal", "0", "--attempt", "0", "--source-tar", str(bundle / "source.tar.gz"),
                   "--pack-tar", str(bundle / "query-pack.tar.gz")]
        attempts = []
        for attempt in range(int(retry[1]) + 1):
            command[command.index("--attempt")+1] = str(attempt)
            observed = subprocess.run(command, env=environment, text=True, capture_output=True)
            attempts.append(observed.returncode)
            self.assertIn("TEST_ONLY startup read fault", observed.stderr)
        self.assertEqual(attempts, [75, 75, 75])
        self.assertFalse(any((self.base / "bulk").glob("**/attempt.json")))
        environment.pop("TEST_ONLY_BOOTSTRAP_EIO")
        command[command.index("--expected-work-sha256")+1] = "a" * 64
        fatal = subprocess.run(command, env=environment, text=True, capture_output=True)
        self.assertEqual(fatal.returncode, 42)
        self.assertIn("externally pinned work manifest differs", fatal.stderr)

    def test_query_child_transient_errno_is_not_relabelled_as_science_failure(self):
        q = condor.q
        with mock.patch.object(sys, "argv", ["run.py", "prepare-pack", "--output", "unused",
                                             "--work-root", "unused"]):
            with mock.patch.object(q, "prepare_pack", side_effect=OSError(errno.EIO, "transient")):
                self.assertEqual(q.main(), 75)
            with mock.patch.object(q, "prepare_pack", side_effect=ValueError("invalid science")):
                self.assertEqual(q.main(), 2)

    def toy_domain(self, tunes, jobs, events, shards):
        campaign = copy.deepcopy(json.loads((ROOT / "data/campaign.json").read_text()))
        campaign["tune_order"] = tunes
        campaign["logical_jobs_per_tune"] = jobs
        campaign["successful_events_per_logical_job"] = events
        campaign["successful_events_per_tune"] = jobs * events
        campaign["blocks"]["logical_id_domain"] = [0, jobs - 1]
        campaign["seed"]["tune_ordinals"] = {tune: i for i, tune in enumerate(tunes)}
        campaign["accepted_source"]["tune_cards"] = {
            tune: campaign["accepted_source"]["tune_cards"][tune] for tune in tunes}
        original = [json.loads(line) for line in (ROOT / "data/raw_manifest.jsonl").read_text().splitlines()]
        rows = []
        for tune in tunes:
            rows.extend({**row, "successful_events": events} for row in original
                        if row["tune"] == tune and row["logical_id"] < jobs)
        sources = self.base / "toy-sources.jsonl"
        sources.write_text("".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
                                   for row in rows))
        campaign["accepted_source"]["raw_manifest_sha256"] = condor.r.sha_file(sources)
        descriptor = self.base / "toy-campaign.json"
        descriptor.write_text(json.dumps(campaign))
        entries = []
        for ordinal in range(shards):
            for role, suffix in (("receipt", "json"), ("root_file", "root")):
                entries.append({"ordinal": ordinal, "role": role,
                                "path": "inputs/shard-%04d.%s" % (ordinal, suffix),
                                "bytes": 10 if role == "receipt" else 100 + ordinal,
                                "sha256": "a" * 64})
        acquired = {"schema": "hadronization_test_only_query_file_domain_v1",
                    "state": "TEST_ONLY", "pair_count": shards, "input_file_count": 2 * shards,
                    "accepted_root_bytes": sum(100+i for i in range(shards)), "files": entries}
        file_domain = self.base / "toy-files.json"
        file_domain.write_text(json.dumps(acquired))
        return descriptor, sources, file_domain

    def test_validated_test_only_one_tune_and_alternate_factorization_render(self):
        dictionary = FIXTURE / "dictionary.json"
        for name, tunes, jobs, events, shards in (
                ("one", ["MONASH"], 20, 3, 4),
                ("refactored", ["MONASH", "JUNCTIONS", "CLOSEPACKING"], 200, 500000, 17)):
            with self.subTest(name=name):
                descriptor, sources, acquired = self.toy_domain(tunes, jobs, events, shards)
                bundle = self.base / (name + "-bundle")
                condor.prepare(acquired, condor.r.sha_file(acquired), dictionary,
                               condor.r.sha_file(dictionary), bundle, test_only=True,
                               campaign_path=descriptor, source_manifest_path=sources)
                work = condor.r.json_file(bundle / "work.json")
                self.assertEqual(work["state"], "TEST_ONLY_INERT")
                self.assertEqual(len(work["work"]), shards)
                self.assertEqual(work["expected_source_count"], len(tunes) * jobs)
                self.assertEqual(work["expected_event_count"], len(tunes) * jobs * events)
                self.assertEqual(work["tune_ordinals"], {tune: i for i, tune in enumerate(tunes)})
                self.assertEqual((bundle / "workflow.dag").read_text().count("RETRY q"), shards)
                self.assertEqual(condor.r.json_file(bundle / "bundle-manifest.json")["state"],
                                 "TEST_ONLY_INERT")
                with self.assertRaisesRegex(ValueError, "not the inert native bundle"):
                    condor.bind_site(bundle, condor.r.sha_file(bundle / "bundle-manifest.json"),
                                     bundle / "missing-pack", "a" * 64,
                                     bundle / "missing-admission", "a" * 64,
                                     self.base / "must-not-bind")

    def test_invalid_test_only_source_and_file_domains_refuse(self):
        descriptor, sources, acquired = self.toy_domain(["MONASH"], 20, 3, 4)
        manifest = condor.r.json_file(acquired)
        campaign = condor.r.json_file(descriptor)
        original = sources.read_text().splitlines()
        cases = []
        cases.append(("missing_source", campaign, original[:-1], manifest))
        cases.append(("duplicate_source", campaign, original[:-1] + [original[-2]], manifest))
        foreign = json.loads(original[-1]); foreign["tune"] = "FOREIGN"
        cases.append(("foreign_source", campaign, original[:-1] +
                      [json.dumps(foreign, sort_keys=True, separators=(",", ":"))], manifest))
        changed = copy.deepcopy(campaign); changed["successful_events_per_tune"] += 1
        cases.append(("inconsistent_events", changed, original, manifest))
        changed = copy.deepcopy(campaign); changed["blocks"]["logical_id_rule"] = "unsupported"
        cases.append(("unsupported_blocks", changed, original, manifest))
        changed = copy.deepcopy(manifest); changed["files"] = changed["files"][:-1]
        cases.append(("missing_file", campaign, original, changed))
        changed = copy.deepcopy(manifest); changed["files"][-1] = changed["files"][-2]
        cases.append(("duplicate_file", campaign, original, changed))
        changed = copy.deepcopy(manifest); changed["files"][-1]["ordinal"] = 999
        cases.append(("foreign_file", campaign, original, changed))
        changed = copy.deepcopy(manifest); changed["accepted_root_bytes"] += 1
        cases.append(("inconsistent_bytes", campaign, original, changed))
        for name, model, rows, files in cases:
            with self.subTest(name=name):
                descriptor.write_text(json.dumps(model))
                sources.write_text("\n".join(rows) + "\n")
                acquired.write_text(json.dumps(files))
                with self.assertRaises(ValueError):
                    condor._normalized_domain(descriptor, sources, files)


if __name__ == "__main__":
    unittest.main()
