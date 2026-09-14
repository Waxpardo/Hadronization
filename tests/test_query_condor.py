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
import tarfile
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/query_multitune/queries/shard-0000"
spec = importlib.util.spec_from_file_location("tested_condor", ROOT / "pipeline/query/condor.py")
condor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(condor)
site_spec = importlib.util.spec_from_file_location(
    "query_site_probe", ROOT / "pipeline/query/site_probe.py")
site_probe = importlib.util.module_from_spec(site_spec)
site_spec.loader.exec_module(site_probe)


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

    def test_site_probe_requires_exact_selected_almalinux_minor(self):
        release = 'NAME="AlmaLinux"\nID="almalinux"\nVERSION_ID="9.6"\n'
        observed = site_probe.check_almalinux_release(release, "9.6")
        self.assertEqual(observed["version"], "9.6")
        self.assertEqual(observed["os_release_sha256"],
                         site_probe.hashlib.sha256(release.encode()).hexdigest())
        with self.assertRaisesRegex(ValueError, "selected pin"):
            site_probe.check_almalinux_release(release, "9.8")
        with self.assertRaisesRegex(ValueError, "explicit EL9 pin"):
            site_probe.check_almalinux_release(release, "9")
        with self.assertRaisesRegex(ValueError, "distribution differs"):
            site_probe.check_almalinux_release(
                release.replace('ID="almalinux"', 'ID="debian"'), "9.6")

    def test_site_probe_preserves_unique_publication_and_interrupted_sibling(self):
        bulk = self.base / "bulk"
        bulk.mkdir()
        receipt = site_probe.publish_probe(bulk, "TEST_ONLY bulk")
        self.assertEqual(receipt["no_overwrite"], "PASS")
        self.assertEqual(receipt["directory_publish"], "PASS")
        self.assertEqual(receipt["readback"], "PASS")
        self.assertEqual(site_probe.sha(Path(receipt["payload"])), receipt["sha256"])
        self.assertEqual((Path(receipt["interrupted_stage"]) / "payload.bin").read_bytes(),
                         b"INTERRUPTED_QUALIFICATION_ONLY")
        for kind in ("empty", "nonempty"):
            self.assertEqual(receipt["existing_destinations"][kind]["refused"], "PASS")
            self.assertTrue(Path(receipt["existing_destinations"][kind]["stage"]).is_dir())

    def test_site_probe_uses_production_publication_and_refuses_unsupported_or_corrupt(self):
        bulk = self.base / "bulk"
        bulk.mkdir()
        with mock.patch.object(site_probe.publication, "publish_directory",
                               side_effect=OSError(errno.ENOTSUP, "TEST_ONLY unsupported")) as publish:
            with self.assertRaises(OSError) as error:
                site_probe.publish_probe(bulk, "TEST_ONLY bulk")
        self.assertEqual(error.exception.errno, errno.ENOTSUP)
        self.assertEqual(publish.call_count, 1)
        self.assertEqual(len(list(bulk.glob(".qualification-*.stage"))), 1)
        self.assertEqual(list(bulk.glob("qualification-*")), [])
        with mock.patch.object(site_probe, "sha", return_value="0" * 64):
            with self.assertRaisesRegex(ValueError, "durable readback differs"):
                site_probe.publish_probe(bulk, "TEST_ONLY bulk")

    def test_site_probe_reads_separate_job_and_machine_classads(self):
        job = self.base / "job.ad"
        machine = self.base / "machine.ad"
        job.write_text('MyType = "Job"\nRequestMemory = 1024\nRequestDisk = 1048576\n'
                       'SingularityImage = "/cvmfs/pinned-image"\n')
        machine.write_text('MyType = "Machine"\nArch = "X86_64"\nOpSys = "LINUX"\n'
                           'Memory = 2048\nDisk = 2097152\n')
        with mock.patch.dict(os.environ, {"_CONDOR_JOB_AD": str(job),
                                       "_CONDOR_MACHINE_AD": str(machine)}):
            facts = site_probe.classad_evidence()
            self.assertEqual(facts["job"]["sha256"], site_probe.sha(job))
            self.assertEqual(facts["machine"]["sha256"], site_probe.sha(machine))
            self.assertNotEqual(facts["job"]["sha256"], facts["machine"]["sha256"])
            self.assertEqual(facts["job"]["request_memory_mb"], 1024)
            self.assertEqual(
                site_probe.classad_evidence("/cvmfs/pinned-image")["job"]["container_image"],
                "/cvmfs/pinned-image")
            with self.assertRaisesRegex(ValueError, "container image differs"):
                site_probe.classad_evidence("/cvmfs/other-image")
            self.assertEqual(facts["machine"]["arch"], "X86_64")
            for wrong_job, wrong_machine, reason in (
                    ('MyType = "Machine"\nRequestMemory = 1024\nRequestDisk = 1048576\n',
                     None, "wrong MyType"),
                    ('MyType = "Job"\nRequestMemory = 0\nRequestDisk = 1048576\n',
                     None, "positive integer"),
                    ('MyType = "Job"\nRequestMemory = 1024\n', None, "lacks RequestDisk"),
                    (None, 'MyType = "Job"\nArch = "X86_64"\nOpSys = "LINUX"\n',
                     "wrong MyType"),
                    (None, 'MyType = "Machine"\nArch = "ARM64"\nOpSys = "LINUX"\n',
                     "architecture/OS differs"),
                    (None, 'MyType = "Machine"\nArch = "X86_64"\n',
                     "lacks OpSys"),
                    (None, 'MyType = "Machine"\nArch = "X86_64"\nOpSys = "LINUX"\n'
                     'Memory = 100\n', "cannot satisfy")):
                original_job, original_machine = job.read_text(), machine.read_text()
                if wrong_job is not None:
                    job.write_text(wrong_job)
                if wrong_machine is not None:
                    machine.write_text(wrong_machine)
                with self.assertRaisesRegex(ValueError, reason):
                    site_probe.classad_evidence()
                job.write_text(original_job); machine.write_text(original_machine)
        with mock.patch.dict(os.environ, {"_CONDOR_JOB_AD": str(job),
                                       "_CONDOR_MACHINE_AD": str(self.base / "missing")}) :
            with self.assertRaisesRegex(ValueError, "machine ClassAd is missing"):
                site_probe.classad_evidence()
        with mock.patch.dict(os.environ, {"_CONDOR_JOB_AD": str(self.base / "missing"),
                                       "_CONDOR_MACHINE_AD": str(machine)}):
            with self.assertRaisesRegex(ValueError, "job ClassAd is missing"):
                site_probe.classad_evidence()
        with mock.patch.dict(os.environ, {"_CONDOR_JOB_AD": str(job),
                                       "_CONDOR_MACHINE_AD": str(job)}):
            with self.assertRaisesRegex(ValueError, "not distinct"):
                site_probe.classad_evidence()

    def test_screen_plan_covers_every_tune_block_from_pinned_receipts(self):
        input_root = self.base / "inputs"
        input_root.mkdir()
        sources = [{"source_id": i, "tune": tune, "block": block}
                   for i, (tune, block) in enumerate((
                       ("MONASH", 1), ("MONASH", 2),
                       ("JUNCTIONS", 1), ("JUNCTIONS", 2),
                       ("CLOSEPACKING", 1), ("CLOSEPACKING", 2)))]
        source_path = self.base / "sources.json"
        source_path.write_text(json.dumps(sources))
        items = []
        for ordinal in range(3):
            receipt_path = input_root / ("shard-%04d.json" % ordinal)
            receipt_path.write_text(json.dumps({"state": "PASS", "shard_ordinal": ordinal,
                "storage_identity": {"source_ids": [ordinal * 2, ordinal * 2 + 1]}}))
            items.append({"ordinal": ordinal,
                          "root": {"name": "shard-%04d.root" % ordinal, "bytes": 1,
                                   "sha256": "a" * 64},
                          "receipt": {"name": receipt_path.name,
                                      "bytes": receipt_path.stat().st_size,
                                      "sha256": condor.r.sha_file(receipt_path)}})
        work = {"schema": condor.WORK_SCHEMA, "state": "SITE_BOUND",
                "storage_semantics": "POSIX_NOOVERWRITE_VERIFIED",
                "site_admission_sha256": "a" * 64,
                "prepared_pack_tar_sha256": "b" * 64,
                "input_root": str(input_root),
                "durable_bulk_root": str(self.base / "bulk"),
                "durable_control_root": str(self.base / "control"),
                "expected_sources_sha256": condor.r.sha_file(source_path),
                "input_file_count": 6, "input_root_bytes": 3,
                "campaign_id": "TEST_ONLY", "block_count": 2,
                "tune_ordinals": {tune: i for i, tune in
                                  enumerate(("MONASH", "JUNCTIONS", "CLOSEPACKING"))},
                "expected_source_count": 6, "expected_event_count": 6,
                "work": items}
        work_path = self.base / "work.json"
        work_path.write_text(json.dumps(work))
        plan = condor.screen_plan(work_path, condor.r.sha_file(work_path), source_path)
        self.assertEqual(plan["ordinals"], [0, 1, 2])
        self.assertEqual(len(plan["coverage"]), 6)
        sources[-1]["block"] = 1
        source_path.write_text(json.dumps(sources))
        work["expected_sources_sha256"] = condor.r.sha_file(source_path)
        work_path.write_text(json.dumps(work))
        with self.assertRaisesRegex(ValueError, "coverage differs"):
            condor.screen_plan(work_path, condor.r.sha_file(work_path), source_path)

    def test_collector_shaped_screen_stays_test_only_on_all_tune_blocks(self):
        fixture = ROOT / "tests/fixtures/query_multitune"
        sources_path = fixture / "expected-sources.json"
        sources = json.loads(sources_path.read_text())
        metadata = json.loads((fixture / "queries/shard-0000/metadata.json").read_text())
        binding = metadata["input_receipt"]["binding"]
        input_root = self.base / "inputs"
        bulk = self.base / "bulk"
        control = self.base / "control"
        input_root.mkdir(); (control / "pins").mkdir(parents=True)
        work_items, pins = [], []
        work_sha_placeholder = "a" * 64
        for ordinal in range(3):
            receipt = input_root / ("shard-%04d.json" % ordinal)
            receipt.write_text(json.dumps({"state": "PASS", "shard_ordinal": ordinal,
                "storage_identity": {"source_ids": list(range(ordinal * 10, ordinal * 10 + 10))}}))
            work_items.append({"ordinal": ordinal,
                "root": {"name": "shard-%04d.root" % ordinal, "bytes": 1,
                         "sha256": "b" * 64},
                "receipt": {"name": receipt.name, "bytes": receipt.stat().st_size,
                            "sha256": condor.r.sha_file(receipt)}})
        source_tar = self.base / "source.tar.gz"
        source_tar.write_bytes(b"TEST_ONLY source pin")
        work = {"schema": condor.WORK_SCHEMA, "state": "SITE_BOUND",
                "storage_semantics": "POSIX_NOOVERWRITE_VERIFIED",
                "site_admission_sha256": work_sha_placeholder,
                "prepared_pack_tar_sha256": "c" * 64,
                "input_root": str(input_root),
                "durable_bulk_root": str(bulk),
                "durable_control_root": str(control),
                "expected_sources_sha256": condor.r.sha_file(sources_path),
                "source_tar_sha256": condor.r.sha_file(source_tar),
                "input_file_count": 6, "input_root_bytes": 3,
                "campaign_id": binding["campaign"],
                "source_manifest_sha256": binding["manifest_sha256"],
                "analysis_sha256": metadata["analysis_sha256"],
                "layout_sha256": metadata["layout_sha256"],
                "block_count": 10, "tune_ordinals": binding["tune_ordinals"],
                "expected_source_count": 30, "expected_event_count": 90,
                "work": work_items}
        work_path = self.base / "work.json"
        work_path.write_text(json.dumps(work))
        work_sha = condor.r.sha_file(work_path)
        for ordinal in range(3):
            workspace = fixture / "queries" / ("shard-%04d" % ordinal)
            attempt = condor._stage_workspace(
                workspace, bulk / ("shard-%04d" % ordinal) / "attempt-00",
                ordinal, 0, work_sha)
            pins.append({"ordinal": ordinal, "attempt": 0,
                         "scientific_content_sha256": attempt["scientific_content_sha256"]})
        plan_path = self.base / "screen.json"
        plan_path.write_text(json.dumps(condor.screen_plan(work_path, work_sha, sources_path)))
        pins_path = control / "pins/selected.json"
        pins_path.write_text(json.dumps({"schema": condor.PINS_SCHEMA,
                                        "authority": "EXTERNAL_REVIEW", "pins": pins}))
        condor.collect(work_path, work_sha, sources_path, source_tar,
                       pins_path, condor.r.sha_file(pins_path),
                       plan_path, condor.r.sha_file(plan_path))
        published = control / "screens" / ("screen-" + work_sha[:16] + "-" +
                                            condor.r.sha_file(pins_path)[:12])
        self.assertEqual(condor.r.json_file(published / "manifest.json")["state"],
                         "TEST_ONLY_REPRESENTATIVE_SCREEN")
        self.assertEqual(condor.r.json_file(published / "index.json")["state"], "TEST_ONLY")
        with self.assertRaisesRegex(ValueError, "publication already exists"):
            condor.collect(work_path, work_sha, sources_path, source_tar,
                           pins_path, condor.r.sha_file(pins_path),
                           plan_path, condor.r.sha_file(plan_path))

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
        forged = dict(admission)
        pack = self.base / "fake-pack.tar.gz"
        pack.write_bytes(b"TEST_ONLY_NOT_A_LINUX_PACK")
        forged.update(decision="ADMITTED", authority="INDEPENDENT_L1_AND_SITE_REVIEW",
                      inert_bundle_manifest_sha256=condor.r.sha_file(bundle / "bundle-manifest.json"),
                      qualified_pack_sha256=condor.r.sha_file(pack),
                      memory_mb=1024, scratch_kb=1024)
        for key in ("execute_node_canary", "runtime_versions", "input_readback",
                    "posix_nooverwrite", "posix_readback", "quota", "retention"):
            forged[key] = "PASS"
        forged_path = self.base / "forged-admission.json"
        forged_path.write_text(json.dumps(forged))
        with mock.patch.object(condor, "_extract_pack"), mock.patch.object(
                condor.q, "load_prepared_pack"):
            with self.assertRaisesRegex(ValueError, "evidence fact is incomplete"):
                condor.bind_site(bundle, forged["inert_bundle_manifest_sha256"],
                                 pack, forged["qualified_pack_sha256"],
                                 forged_path, condor.r.sha_file(forged_path),
                                 self.base / "forged-bound")
        observed = self.base / "observed.json"
        observed.write_text('{"status":"TEST_ONLY"}')
        fact = {"path": str(observed), "bytes": observed.stat().st_size,
                "sha256": condor.r.sha_file(observed)}
        forged["evidence"] = {key: dict(fact) for key in admission["evidence"]}
        forged["resource_envelope"] = {key: 1 for key in (
            "query_peak_rss_mb", "query_peak_scratch_kb", "merge_peak_rss_mb",
            "reduce_peak_rss_mb", "render_peak_rss_mb", "postprocess_limit_mb",
            "bulk_projected_peak_bytes", "bulk_allocated_bytes",
            "query_occupied_cells", "merged_occupied_cells",
            "screened_input_pairs", "covered_tune_blocks")}
        forged["resource_envelope"]["query_peak_rss_mb"] = 1000
        forged_path.write_text(json.dumps(forged))
        with mock.patch.object(condor, "_extract_pack"), mock.patch.object(
                condor.q, "load_prepared_pack"):
            with self.assertRaisesRegex(ValueError, "resource envelope does not fit"):
                condor.bind_site(bundle, forged["inert_bundle_manifest_sha256"],
                                 pack, forged["qualified_pack_sha256"],
                                 forged_path, condor.r.sha_file(forged_path),
                                 self.base / "forged-bound")
        self.assertNotIn("query-pack.tar.gz", {p.name for p in bundle.iterdir()})
        self.assertIn("test ! -e workflow.dag", (bundle / "BUILD_LINUX_PACK.sh").read_text())
        self.assertIn('cp "$SITE_CONF" source/config/site.conf',
                      (bundle / "BUILD_LINUX_PACK.sh").read_text())
        self.assertEqual(subprocess.run(["bash", "-n", str(bundle / "BUILD_LINUX_PACK.sh")],
                                        capture_output=True).returncode, 0)
        self.assertIn("__ACCEPTED_ANALYZED_SAMPLE_ROOT__",
                      (bundle / "site-canary.sub").read_text())
        self.assertIn("--expected-almalinux-version 9.6",
                      (bundle / "site-canary.sub").read_text())
        self.assertIn("--expected-image-path " + condor.PINNED_EL9_IMAGE,
                      (bundle / "site-canary.sub").read_text())
        for submit_name in ("site-canary.sub", "worker.sub"):
            submit = (bundle / submit_name).read_text()
            self.assertIn('+SingularityImage = "' + condor.PINNED_EL9_IMAGE + '"',
                          submit)
            self.assertIn("+JobCategory = ", submit)
        self.assertIn('+JobCategory = "long"',
                      (bundle / "collector.sub").read_text())
        self.assertIn("transfer_input_files = site_probe.py,publication.py,runtime.py",
                      (bundle / "site-canary.sub").read_text())
        self.assertIn("--site-conf __PINNED_SITE_CONF__",
                      (bundle / "site-canary.sub").read_text())
        self.assertEqual((bundle / "runtime.py").read_bytes(),
                         (ROOT / "pipeline/generate/runtime.py").read_bytes())
        self.assertIn("transfer_executable = False",
                      (bundle / "site-canary.sub").read_text())
        self.assertIn("transfer_executable = False",
                      (bundle / "worker.sub").read_text())
        self.assertEqual((bundle / "publication.py").read_bytes(),
                         (ROOT / "pipeline/query/publication.py").read_bytes())
        self.assertIn("pipeline/query/publication.py", condor.SOURCE_FILES)
        helper = (ROOT / "pipeline/query/publication.py").read_bytes()
        source_facts = json.loads((bundle / "source-files.json").read_text())
        self.assertEqual(source_facts["pipeline/query/publication.py"], {
            "bytes": len(helper), "sha256": condor.r.sha_file(
                ROOT / "pipeline/query/publication.py")})
        with tarfile.open(bundle / "source.tar.gz", "r:gz") as archive:
            self.assertEqual(archive.extractfile("pipeline/query/publication.py").read(),
                             helper)
        bundle_files = json.loads((bundle / "bundle-manifest.json").read_text())["files"]
        self.assertEqual(bundle_files["publication.py"]["sha256"],
                         condor.r.sha_file(bundle / "publication.py"))
        self.assertEqual(subprocess.run([sys.executable, str(bundle / "site_probe.py"),
                                         "--help"], capture_output=True).returncode, 0)
        self.assertEqual(admission["evidence"]["resource_budget"], "PENDING")
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
        input_root = self.base / "input"
        input_root.mkdir()
        analyzed_receipt = input_root / "shard-0000.json"
        analyzed_receipt.write_text(json.dumps({"state": "PASS", "shard_ordinal": 0,
            "storage_identity": {"source_ids": [0]}}))
        attempt_dir = bulk / "shard-0000/attempt-00"
        attempt_dir.mkdir(parents=True)
        work = {"schema": condor.WORK_SCHEMA, "state": "SITE_BOUND",
                "storage_semantics": "POSIX_NOOVERWRITE_VERIFIED",
                "site_admission_sha256": "a" * 64,
                "prepared_pack_tar_sha256": "b" * 64,
                "input_root": str(input_root),
                "durable_bulk_root": str(bulk), "durable_control_root": str(control),
                "input_file_count": 2, "input_root_bytes": 1,
                "campaign_id": "TEST_ONLY", "block_count": 1,
                "tune_ordinals": {"TEST": 0},
                "expected_source_count": 1, "expected_event_count": 1,
                "work": [{"ordinal": 0, "root": {"name": "shard-0000.root", "bytes": 1},
                          "receipt": {"name": analyzed_receipt.name,
                                      "bytes": analyzed_receipt.stat().st_size,
                                      "sha256": condor.r.sha_file(analyzed_receipt)}}]}
        expected_source = bundle / "expected-sources.json"
        expected_source.write_text(json.dumps([{"source_id": 0, "tune": "TEST",
                                                "block": 1, "events": 1}]))
        work["expected_sources_sha256"] = condor.r.sha_file(expected_source)
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
        plan_path = self.base / "screen-plan.json"
        plan_path.write_text(json.dumps(condor.screen_plan(
            bundle / "work.json", work_sha, expected_source)))
        screen_launch = self.base / "screen-launch"
        condor.stage_dag(bundle, bundle_sha, screen_launch,
                         plan_path, condor.r.sha_file(plan_path))
        self.assertIn("TEST_ONLY representative screen",
                      (screen_launch / "workflow.dag").read_text())
        self.assertEqual(condor.r.json_file(screen_launch / "launch-receipt.json")[
            "state"], "TEST_ONLY_SCREEN_READY_FOR_NO_SUBMIT_REVIEW")
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
