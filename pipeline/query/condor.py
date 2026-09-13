"""Prepare an inert native DAG, then run pinned query attempts and exact collection.

The submit template intentionally contains site placeholders. Binding an execute
node, durable POSIX destination and externally held acceptance pins is separate.
"""

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


q = _load("condor_query", "run.py")
c = _load("condor_collection", "collection.py")
r = q.reduce
WORK_SCHEMA = "hadronization_condor_query_work_v1"
PINS_SCHEMA = "hadronization_external_query_content_pins_v1"
ATTEMPT_SCHEMA = "hadronization_condor_query_attempt_v1"
FAILURE_SCHEMA = "hadronization_condor_query_failed_attempt_v1"
ADMISSION_SCHEMA = "hadronization_query_site_admission_v1"
# Narrow legacy acceptance adapter for the current, independently reviewed
# Phase-A source/data snapshot. These are identity pins, not scheduler sizes.
CURRENT_CAMPAIGN_SHA256 = "cc2c0593d8b48103560bed7ba46fa7f81a8137bae24994c6ef2316dd9265005d"
CURRENT_SOURCE_MANIFEST_SHA256 = "5f354cbc9e0bdfb7ead07adb341d74e4c98f14709d873f8f247585912e2df247"
TRANSIENT_ERRNOS = r.TRANSIENT_ERRNOS
SOURCE_FILES = (
    "hadronization", "config/analysis.json", "config/query.json", "config/study.json",
    "pipeline/analyze/run.py", "pipeline/generate/runtime.py", "pipeline/generate/sha256.hpp",
    "pipeline/query/model.py", "pipeline/query/support.py", "pipeline/query/run.py",
    "pipeline/query/campaign.py", "pipeline/query/collection.py", "pipeline/query/merge.py",
    "pipeline/query/condor.py", "pipeline/query/query.cpp", "pipeline/query/selection.hpp",
    "pipeline/query/row_schema.hpp", "pipeline/query/sparse.hpp",
)
BOOTSTRAP = '''#!/usr/bin/env python3
"""Start the hash-frozen query program from a transferred source tar."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

TRANSIENT_ERRNOS = set(__TRANSIENT_ERRNOS__)

def option(name):
    return Path(sys.argv[sys.argv.index(name) + 1])

try:
    work_path = option("--work")
    expected = sys.argv[sys.argv.index("--expected-work-sha256") + 1]
    source_tar = option("--source-tar")
    raw = work_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("externally pinned work manifest differs")
    work = json.loads(raw)
    if hashlib.sha256(source_tar.read_bytes()).hexdigest() != work["source_tar_sha256"]:
        raise ValueError("frozen source tar differs")
    with tempfile.TemporaryDirectory(prefix="hadronization-frozen-source-") as temporary:
        root = Path(temporary)
        with tarfile.open(source_tar, "r:gz") as archive:
            members = archive.getmembers()
            for member in members:
                destination = root / member.name
                if (not member.isfile() or member.name.startswith("/") or
                        ".." in Path(member.name).parts or root not in destination.parents):
                    raise ValueError("unsafe frozen source member")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.extractfile(member).read())
        result = subprocess.run([sys.executable, "-B", str(root / "pipeline/query/condor.py"), *sys.argv[1:]])
        sys.exit(result.returncode)
except OSError as error:
    print("BOOTSTRAP ERROR: " + str(error), file=sys.stderr)
    sys.exit(75 if error.errno in TRANSIENT_ERRNOS else 42)
except (ValueError, KeyError, IndexError, tarfile.TarError) as error:
    print("BOOTSTRAP ERROR: " + str(error), file=sys.stderr)
    sys.exit(42)
'''.replace("__TRANSIENT_ERRNOS__", repr(sorted(TRANSIENT_ERRNOS)))


class TransientError(Exception):
    pass


def _sha(value):
    return hashlib.sha256(r.canonical(value).encode("ascii")).hexdigest()


def _fact(path):
    path = Path(path)
    r.regular_file(path, "Condor artifact")
    return {"path": str(path.absolute()), "bytes": path.stat().st_size,
            "sha256": r.sha_file(path)}


def _source_tar(path):
    source_facts = {}
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        for relative in SOURCE_FILES:
            source = ROOT / relative
            if not source.is_file() or source.is_symlink():
                raise ValueError("frozen source file is missing: " + relative)
            content = source.read_bytes()
            source_facts[relative] = {"bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
            info = tarfile.TarInfo(relative)
            info.size = len(content)
            info.mode = 0o755 if relative == "hadronization" else 0o644
            info.mtime = 0
            archive.addfile(info, io.BytesIO(content))
    path.write_bytes(gzip.compress(buffer.getvalue(), mtime=0))
    return source_facts


def _accepted_files(path, expected_sha256):
    r.lower_sha(expected_sha256, "accepted acquisition manifest pin")
    if r.sha_file(path) != expected_sha256:
        raise ValueError("accepted acquisition manifest differs")
    manifest = r.json_file(path)
    if (manifest.get("schema") != "phasea_arch_full_input_acquisition_manifest_v1" or
            manifest.get("status") != "ALL_323_ACCEPTED_INPUT_PAIRS_REVERIFIED" or
            manifest.get("pair_count") != 323 or manifest.get("input_file_count") != 646 or
            manifest.get("accepted_root_bytes") != 158720142481):
        raise ValueError("accepted 323 manifest schema/accounting differs")
    entries = manifest.get("files")
    if not isinstance(entries, list) or len(entries) != 646:
        raise ValueError("accepted manifest file set differs")
    files = {}
    for item in entries:
        ordinal, role = item.get("ordinal"), item.get("role")
        if (type(ordinal) is not int or not 0 <= ordinal < 323 or
                role not in {"receipt", "root_file"} or (ordinal, role) in files):
            raise ValueError("accepted manifest ordinal/role differs")
        suffix = "json" if role == "receipt" else "root"
        if (item.get("path") != "inputs/shard-%04d.%s" % (ordinal, suffix) or
                type(item.get("bytes")) is not int or item["bytes"] <= 0):
            raise ValueError("accepted manifest path/size differs")
        r.lower_sha(item.get("sha256"), "accepted input SHA")
        files[ordinal, role] = item
    if set(files) != {(ordinal, role) for ordinal in range(323)
                     for role in ("receipt", "root_file")}:
        raise ValueError("accepted manifest exact ordinal domain differs")
    if sum(files[i, "root_file"]["bytes"] for i in range(323)) != manifest["accepted_root_bytes"]:
        raise ValueError("accepted ROOT byte accounting differs")
    return files, manifest


def _normalized_domain(campaign_path, source_manifest_path, acquisition):
    """Use the admitted analyzer's campaign/source validator once for all dimensions."""
    analyzer = r.analyzer_module()
    campaign = r.json_file(campaign_path)
    adapter = analyzer.campaign_adapter(campaign)
    rows = analyzer.load_manifest(source_manifest_path, campaign, adapter)
    pair_count, file_count, root_bytes = (acquisition.get(key) for key in
                                          ("pair_count", "input_file_count", "accepted_root_bytes"))
    entries = acquisition.get("files")
    if (type(pair_count) is not int or pair_count <= 0 or pair_count > len(rows) or
            type(file_count) is not int or file_count != pair_count * 2 or
            type(root_bytes) is not int or root_bytes <= 0 or
            not isinstance(entries, list) or len(entries) != file_count):
        raise ValueError("campaign file-domain counts are inconsistent")
    files = {}
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("campaign file-domain entry differs")
        ordinal, role = item.get("ordinal"), item.get("role")
        if (type(ordinal) is not int or not 0 <= ordinal < pair_count or
                role not in {"receipt", "root_file"} or (ordinal, role) in files):
            raise ValueError("campaign file-domain ordinal/role differs")
        suffix = "json" if role == "receipt" else "root"
        if (item.get("path") != "inputs/shard-%04d.%s" % (ordinal, suffix) or
                type(item.get("bytes")) is not int or item["bytes"] <= 0):
            raise ValueError("campaign file-domain path/size differs")
        r.lower_sha(item.get("sha256"), "campaign input SHA")
        files[ordinal, role] = item
    if (set(files) != {(i, role) for i in range(pair_count)
                      for role in ("root_file", "receipt")} or
            sum(files[i, "root_file"]["bytes"] for i in range(pair_count)) != root_bytes):
        raise ValueError("campaign file-domain coverage/ROOT bytes differ")
    tunes = adapter["tune_ordinals"]
    expected = [{"source_id": i, "tune": row["tune"], "tune_ordinal": tunes[row["tune"]],
                 "logical_id": row["logical_id"], "block": row["block"],
                 "events": row["successful_events"]}
                for i, row in enumerate(rows)]
    work = [{"ordinal": i,
             "root": {"name": "shard-%04d.root" % i, "bytes": files[i, "root_file"]["bytes"],
                      "sha256": files[i, "root_file"]["sha256"]},
             "receipt": {"name": "shard-%04d.json" % i, "bytes": files[i, "receipt"]["bytes"],
                         "sha256": files[i, "receipt"]["sha256"]}}
            for i in range(pair_count)]
    return {"campaign_sha256": r.sha_file(campaign_path),
            "campaign_id": campaign["campaign"],
            "source_manifest_sha256": r.sha_file(source_manifest_path),
            "block_count": adapter["block_count"],
            "tune_ordinals": tunes,
            "expected_sources": expected,
            "expected_source_count": len(expected),
            "expected_event_count": sum(row["events"] for row in expected),
            "input_file_count": file_count, "input_root_bytes": root_bytes,
            "work": work}


def prepare(acquisition, acquisition_sha, dictionary, dictionary_sha, output,
            *, test_only=False, campaign_path=None, source_manifest_path=None):
    if test_only:
        if r.sha_file(acquisition) != acquisition_sha:
            raise ValueError("TEST_ONLY file-domain manifest differs")
        manifest = r.json_file(acquisition)
        if (manifest.get("schema") != "hadronization_test_only_query_file_domain_v1" or
                manifest.get("state") != "TEST_ONLY"):
            raise ValueError("toy file domain is not explicitly TEST_ONLY")
    else:
        _, manifest = _accepted_files(acquisition, acquisition_sha)
        if campaign_path is not None or source_manifest_path is not None:
            raise ValueError("production preparation uses canonical campaign/source anchors")
    campaign_path = Path(campaign_path or ROOT / "data/campaign.json")
    source_manifest_path = Path(source_manifest_path or ROOT / "data/raw_manifest.jsonl")
    if not test_only and (r.sha_file(campaign_path) != CURRENT_CAMPAIGN_SHA256 or
                          r.sha_file(source_manifest_path) != CURRENT_SOURCE_MANIFEST_SHA256):
        raise ValueError("current accepted Phase-A campaign/source anchor differs")
    domain = _normalized_domain(campaign_path, source_manifest_path, manifest)
    r.lower_sha(dictionary_sha, "accepted campaign dictionary pin")
    if r.sha_file(dictionary) != dictionary_sha:
        raise ValueError("accepted campaign dictionary differs")
    q.read_dictionary(dictionary)
    if output.exists():
        raise ValueError("Condor launch bundle already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="."+output.name+".stage-", dir=str(output.parent)))
    try:
        source_facts = _source_tar(stage / "source.tar.gz")
        shutil.copy2(dictionary, stage / "dictionary.json")
        r.atomic_json(stage / "source-files.json", source_facts, exclusive=True)
        expected = domain["expected_sources"]
        r.atomic_json(stage / "expected-sources.json", expected, exclusive=True)
        work = {"schema": WORK_SCHEMA, "state": "TEST_ONLY_INERT" if test_only else "INERT_SITE_BINDING_REQUIRED",
                "acquisition_manifest_sha256": acquisition_sha,
                "campaign_sha256": domain["campaign_sha256"],
                "campaign_id": domain["campaign_id"],
                "source_manifest_sha256": domain["source_manifest_sha256"],
                "block_count": domain["block_count"],
                "tune_ordinals": domain["tune_ordinals"],
                "analysis_sha256": r.sha_file(ROOT / "config/analysis.json"),
                "layout_sha256": r.sha_file(ROOT / "config/query.json"),
                "source_tar_sha256": r.sha_file(stage / "source.tar.gz"),
                "source_files_sha256": r.sha_file(stage / "source-files.json"),
                "dictionary_sha256": dictionary_sha,
                "prepared_pack_tar_sha256": "__LINUX_PREPARED_PACK_SHA256__",
                "site_admission_sha256": "__EXTERNAL_SITE_ADMISSION_SHA256__",
                "input_root": "__NIKHEF_ACCEPTED_ANALYZED_ROOT__",
                "durable_bulk_root": "__NIKHEF_POSIX_BULK_ROOT__",
                "durable_control_root": "__INDEPENDENT_POSIX_CONTROL_ROOT__",
                "storage_semantics": "POSIX_NOOVERWRITE_PENDING_SITE_TEST",
                "expected_source_count": domain["expected_source_count"],
                "expected_event_count": domain["expected_event_count"],
                "input_file_count": domain["input_file_count"],
                "input_root_bytes": domain["input_root_bytes"],
                "expected_sources_sha256": r.sha_file(stage / "expected-sources.json"),
                "work": domain["work"]}
        r.atomic_json(stage / "work.json", work, exclusive=True)
        for script in ("worker.py", "collector.py", "preflight.py"):
            (stage / script).write_text(BOOTSTRAP)
        work_sha = r.sha_file(stage / "work.json")
        submit = ("universe = vanilla\nexecutable = /usr/bin/python3\n"
                  "arguments = worker.py worker --work work.json --expected-work-sha256 " + work_sha +
                  " --ordinal $(ordinal) --attempt $(RETRY) --source-tar source.tar.gz"
                  " --pack-tar query-pack.tar.gz\n"
                  "should_transfer_files = YES\nwhen_to_transfer_output = ON_EXIT\n"
                  "transfer_input_files = worker.py,work.json,source.tar.gz,source-files.json,dictionary.json,query-pack.tar.gz\n"
                  "transfer_output_files = \"\"\n"
                  "request_cpus = 1\nrequest_memory = __MEASURED_MEMORY_MB__\n"
                  "request_disk = __MEASURED_SCRATCH_KB__\n"
                  "output = logs/$(JOB).$(RETRY).out\nerror = logs/$(JOB).$(RETRY).err\n"
                  "log = logs/worker.events\nqueue 1\n")
        (stage / "worker.sub").write_text(submit)
        dag = ["# Inert until site binding, execute-node canary and L1 admission.",
               "MAXJOBS query 4"]
        for ordinal in range(len(domain["work"])):
            name = "q%04d" % ordinal
            dag.extend(["JOB %s worker.sub" % name, "VARS %s ordinal=\"%d\"" % (name, ordinal),
                        "CATEGORY %s query" % name, "RETRY %s 2 UNLESS-EXIT 42" % name,
                        "ABORT-DAG-ON %s 42" % name])
        (stage / "workflow.dag").write_text("\n".join(dag)+"\n")
        collector = ("# Template only: render-collector publishes a separately pinned submit file after accepted attempts.\n"
                     "universe = local\nexecutable = /usr/bin/python3\n"
                     "arguments = collector.py collect --work work.json --expected-work-sha256 " + work_sha +
                     " --expected-sources expected-sources.json --source-tar source.tar.gz"
                     " --pins __EXTERNALLY_ACCEPTED_PINS_PATH__"
                     " --expected-pins-sha256 __EXTERNALLY_ACCEPTED_PINS_SHA256__\n"
                     "should_transfer_files = NO\ninitialdir = __BUNDLE_DIRECTORY__\n"
                     "output = logs/collector.out\n"
                     "error = logs/collector.err\nlog = logs/collector.events\nqueue 1\n")
        (stage / "collector.sub").write_text(collector)
        (stage / "BUILD_LINUX_PACK.sh").write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\n"
            "# Run in a fresh external build directory, never inside a sealed bundle.\n"
            "test ! -e bundle-manifest.json && test ! -e workflow.dag && test ! -e source && test ! -e prepared-pack && test ! -e query-pack.tar.gz\n"
            "# Run on a qualified AlmaLinux 9.8 submit/build node after L1 admission.\n"
            "mkdir -p source && tar -xzf source.tar.gz -C source\n"
            "python3 -B source/hadronization query prepare-pack --output \"$PWD/prepared-pack\" --work-root \"$PWD/build-scratch\"\n"
            "tar -czf query-pack.tar.gz -C prepared-pack .\nsha256sum query-pack.tar.gz\n")
        (stage / "PREFLIGHT.txt").write_text(
            "Read-only before submission: python3 preflight.py preflight --work work.json"
            " --expected-work-sha256 " + work_sha + " --source-tar source.tar.gz\n"
            "After site binding add --pack-tar query-pack.tar.gz --full-input-hash"
            " to verify all " + str(domain["input_file_count"]) + " accepted input files (" +
            str(domain["input_root_bytes"]) + " ROOT bytes read).\n"
            "Measure execute-node ROOT 6.30.01/GCC 14.2.0/PYTHIA 8.317, scratch/RSS/CPU,"
            " input readability, bulk/control quota/free bytes/inodes, retention,"
            " credentials and ClassAds. Demonstrate POSIX no-overwrite/readback or"
            " select a measured non-POSIX adapter before site binding.\n")
        r.atomic_json(stage / "SITE_ADMISSION_TEMPLATE.json", {
            "schema": ADMISSION_SCHEMA, "decision": "PENDING",
            "authority": "PENDING_INDEPENDENT_L1_AND_SITE_REVIEW",
            "inert_bundle_manifest_sha256": "__INERT_BUNDLE_MANIFEST_SHA256__",
            "qualified_pack_sha256": "__LINUX_PREPARED_PACK_SHA256__",
            "maxjobs": 4, "memory_mb": 0, "scratch_kb": 0,
            "input_root": "__NIKHEF_ACCEPTED_ANALYZED_ROOT__",
            "durable_bulk_root": "__NIKHEF_POSIX_BULK_ROOT__",
            "durable_control_root": "__INDEPENDENT_POSIX_CONTROL_ROOT__",
            "execute_node_canary": "PENDING", "runtime_versions": "PENDING",
            "input_readback": "PENDING", "posix_nooverwrite": "PENDING",
            "posix_readback": "PENDING", "quota": "PENDING", "retention": "PENDING"}, exclusive=True)
        (stage / "README.txt").write_text(
            ("TEST_ONLY INERT DOMAIN. " if test_only else "TEST/LAUNCH STATUS: INERT. ") +
            str(len(domain["work"])) + " input pairs and source topology"
            " derive from the independently pinned acquisition manifest and campaign.\n"
            "Do not submit workflow.dag or collector.sub before L1 scientific/runtime/storage admission.\n"
            "After qualified Linux pack build and readback, use bind-site with an"
            " independently pinned L1/site admission record to produce a new"
            " immutable site-bound bundle. Do not hand-edit the inert bundle."
            " Populate SITE_ADMISSION_TEMPLATE.json only in independent control"
            " custody, record its SHA-256, then run source/pipeline/query/condor.py"
            " bind-site --bundle B --expected-bundle-sha256 H --pack P"
            " --expected-pack-sha256 H --admission A --expected-admission-sha256 H"
            " --output NEW_BUNDLE."
            " Run one execute-node canary, then stage-dag into a separate"
            " no-overwrite launch directory. Run condor_submit_dag -no_submit"
            " workflow.dag there, review it, and submit there. Never run DAGMan"
            " inside the immutable site-bound bundle. Build the Linux pack in"
            " a fresh external directory after copying the frozen source tar"
            " and BUILD_LINUX_PACK.sh there."
            " Query DAG nodes are limited to four; deterministic exit 42 aborts,"
            " transient exit 75 retries twice. Empty queue is not completion.\n"
            "The independent control owner writes exact pins for all " + str(len(domain["work"])) + " accepted"
            " attempts; then run render-collector into separate control custody"
            " and submit that rendered file. Collector verifies exact"
            " contiguous ordinals and source IDs, " + str(domain["expected_event_count"]) +
            " events and the immutable"
            " query collection; physical merge follows exact closure.\n")
        (stage / "logs").mkdir()
        contents = {p.name: {"bytes": p.stat().st_size, "sha256": r.sha_file(p)}
                    for p in stage.iterdir() if p.is_file()}
        r.atomic_json(stage / "bundle-manifest.json", {"schema": "hadronization_inert_condor_bundle_v1",
                                                       "state": "TEST_ONLY_INERT" if test_only else "INERT",
                                                       "files": contents}, exclusive=True)
        for p in stage.iterdir():
            if p.is_file(): r.fsync_file(p)
        r.fsync_directory(stage)
        q.publish_directory(stage, output)
        r.fsync_directory(output.parent)
        return output / "bundle-manifest.json"
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def bind_site(bundle, bundle_sha, pack, pack_sha, admission, admission_sha, output):
    """Bind only after independently recorded L1, runtime and storage acceptance."""
    r.lower_sha(bundle_sha, "inert bundle manifest pin")
    if r.sha_file(bundle / "bundle-manifest.json") != bundle_sha:
        raise ValueError("inert bundle manifest differs")
    manifest = r.json_file(bundle / "bundle-manifest.json")
    if manifest.get("schema") != "hadronization_inert_condor_bundle_v1" or manifest.get("state") != "INERT":
        raise ValueError("source bundle is not the inert native bundle")
    if {p.name for p in bundle.iterdir() if p.is_file()} != set(manifest["files"]) | {"bundle-manifest.json"}:
        raise ValueError("inert bundle fileset differs")
    for name, fact in manifest["files"].items():
        path = bundle / name
        if path.stat().st_size != fact["bytes"] or r.sha_file(path) != fact["sha256"]:
            raise ValueError("inert bundle file differs: " + name)
    r.lower_sha(pack_sha, "qualified Linux pack pin")
    if r.sha_file(pack) != pack_sha:
        raise ValueError("qualified Linux pack differs")
    with tempfile.TemporaryDirectory(prefix="hadronization-pack-check-",
                                     dir=os.environ.get("TMPDIR")) as temporary:
        _extract_pack(pack, Path(temporary))
        q.load_prepared_pack(Path(temporary))
    r.lower_sha(admission_sha, "external L1/site admission pin")
    if r.sha_file(admission) != admission_sha:
        raise ValueError("external L1/site admission differs")
    record = r.json_file(admission)
    if (record.get("schema") != ADMISSION_SCHEMA or record.get("decision") != "ADMITTED" or
            record.get("authority") != "INDEPENDENT_L1_AND_SITE_REVIEW" or
            record.get("inert_bundle_manifest_sha256") != bundle_sha or
            record.get("qualified_pack_sha256") != pack_sha or
            record.get("maxjobs") != 4 or
            any(record.get(key) != "PASS" for key in
                ("execute_node_canary", "runtime_versions", "input_readback",
                 "posix_nooverwrite", "posix_readback", "quota", "retention"))):
        raise ValueError("independent L1/site admission is incomplete")
    memory, scratch = record.get("memory_mb"), record.get("scratch_kb")
    if (type(memory) is not int or memory <= 0 or type(scratch) is not int or scratch <= 0):
        raise ValueError("site resource requests are not measured positive integers")
    paths = ("input_root", "durable_bulk_root", "durable_control_root")
    if any(not isinstance(record.get(key), str) or not Path(record[key]).is_absolute()
           for key in paths):
        raise ValueError("site paths are not absolute")
    inert_work_sha = r.sha_file(bundle / "work.json")
    work = _work(bundle / "work.json", inert_work_sha)
    if work["state"] != "INERT_SITE_BINDING_REQUIRED":
        raise ValueError("work manifest is already bound")
    if output.exists():
        raise ValueError("site-bound bundle already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="."+output.name+".stage-", dir=str(output.parent)))
    try:
        for name in manifest["files"]:
            shutil.copy2(bundle / name, stage / name)
        (stage / "logs").mkdir()
        shutil.copy2(pack, stage / "query-pack.tar.gz")
        work.update({key: record[key] for key in paths})
        work.update({"state": "SITE_BOUND", "storage_semantics": "POSIX_NOOVERWRITE_VERIFIED",
                     "prepared_pack_tar_sha256": pack_sha,
                     "site_admission_sha256": admission_sha})
        _resolved(work)
        (stage / "work.json").unlink()
        r.atomic_json(stage / "work.json", work, exclusive=True)
        bound_sha = r.sha_file(stage / "work.json")
        for name in ("worker.sub", "collector.sub", "PREFLIGHT.txt"):
            path = stage / name
            contents = path.read_text().replace(inert_work_sha, bound_sha)
            if name == "worker.sub":
                contents = contents.replace("__MEASURED_MEMORY_MB__", str(memory))
                contents = contents.replace("__MEASURED_SCRATCH_KB__", str(scratch))
            elif name == "collector.sub":
                contents = contents.replace("__BUNDLE_DIRECTORY__", str(output))
            path.write_text(contents)
        facts = {p.name: {"bytes": p.stat().st_size, "sha256": r.sha_file(p)}
                 for p in stage.iterdir() if p.is_file() and p.name != "bundle-manifest.json"}
        r.atomic_json(stage / "bundle-manifest.json", {
            "schema": "hadronization_site_bound_condor_bundle_v1", "state": "SITE_BOUND",
            "inert_bundle_manifest_sha256": bundle_sha, "site_admission_sha256": admission_sha,
            "work_sha256": bound_sha, "files": facts}, exclusive=True)
        for path in stage.iterdir():
            if path.is_file(): r.fsync_file(path)
        r.fsync_directory(stage)
        q.publish_directory(stage, output)
        r.fsync_directory(output.parent)
        return output / "bundle-manifest.json"
    finally:
        if stage.exists(): shutil.rmtree(stage)


def _work(path, expected_sha):
    r.lower_sha(expected_sha, "trusted work manifest")
    if r.sha_file(path) != expected_sha:
        raise ValueError("work manifest differs from external pin")
    work = r.json_file(path)
    if work.get("schema") != WORK_SCHEMA or not isinstance(work.get("work"), list):
        raise ValueError("work schema differs")
    ordinals = [x["ordinal"] for x in work["work"]]
    if ordinals != list(range(len(ordinals))):
        raise ValueError("work ordinal domain differs")
    if (not ordinals or work.get("input_file_count") != 2 * len(ordinals) or
            work.get("input_root_bytes") != sum(item["root"]["bytes"] for item in work["work"]) or
            not isinstance(work.get("campaign_id"), str) or not work["campaign_id"] or
            type(work.get("block_count")) is not int or work["block_count"] <= 0 or
            not isinstance(work.get("tune_ordinals"), dict) or not work["tune_ordinals"] or
            type(work.get("expected_source_count")) is not int or work["expected_source_count"] <= 0 or
            type(work.get("expected_event_count")) is not int or work["expected_event_count"] <= 0):
        raise ValueError("work normalized domain accounting differs")
    return work


def _resolved(work):
    if work["state"] != "SITE_BOUND" or work["storage_semantics"] != "POSIX_NOOVERWRITE_VERIFIED":
        raise ValueError("site/runtime/storage admission is not bound")
    r.lower_sha(work["site_admission_sha256"], "accepted site admission")
    for key in ("input_root", "durable_bulk_root", "durable_control_root"):
        if not Path(work[key]).is_absolute() or "__" in work[key]:
            raise ValueError("unresolved site path " + key)
    bulk = Path(work["durable_bulk_root"]).resolve()
    control = Path(work["durable_control_root"]).resolve()
    if bulk == control or bulk in control.parents or control in bulk.parents:
        raise ValueError("bulk and external control roots must be distinct")
    r.lower_sha(work["prepared_pack_tar_sha256"], "qualified Linux pack SHA")


def preflight(work_path, work_sha, source_tar, pack_tar=None, full_input_hash=False):
    work = _work(work_path, work_sha)
    report = {"schema": "hadronization_condor_readonly_preflight_v1", "work_sha256": work_sha,
              "source_tar_ok": r.sha_file(source_tar) == work["source_tar_sha256"],
              "state": work["state"], "input_pairs": len(work["work"]),
              "site_checks": {}}
    if pack_tar is not None and work["state"] == "SITE_BOUND":
        report["prepared_pack_ok"] = r.sha_file(pack_tar) == work["prepared_pack_tar_sha256"]
    if work["state"] == "SITE_BOUND":
        input_root = Path(work["input_root"])
        input_count, root_bytes, input_errors = 0, 0, []
        for item in work["work"]:
            for role in ("root", "receipt"):
                fact = item[role]
                path = input_root / fact["name"]
                try:
                    r.regular_file(path, "accepted analyzed input")
                    if path.stat().st_size != fact["bytes"]:
                        raise ValueError("size differs")
                    if full_input_hash and r.sha_file(path) != fact["sha256"]:
                        raise ValueError("SHA-256 differs")
                    input_count += 1
                    if role == "root": root_bytes += fact["bytes"]
                except (OSError, ValueError) as error:
                    input_errors.append({"ordinal": item["ordinal"], "role": role, "error": str(error)})
        report["site_checks"]["accepted_inputs"] = {
            "stat_readback_count": input_count, "expected_count": 2 * len(work["work"]),
            "root_bytes": root_bytes, "full_sha256_checked": full_input_hash,
            "errors": input_errors[:20], "total_errors": len(input_errors)}
        for key in ("input_root", "durable_bulk_root", "durable_control_root"):
            path = Path(work[key])
            try:
                info = os.statvfs(path)
                report["site_checks"][key] = {"readable": os.access(path, os.R_OK),
                    "free_bytes": info.f_bavail * info.f_frsize, "free_inodes": info.f_favail}
            except OSError as error:
                report["site_checks"][key] = {"error": str(error)}
    print(r.canonical(report))
    good = report["source_tar_ok"] and report.get("prepared_pack_ok", True)
    if work["state"] == "SITE_BOUND":
        good = good and not report["site_checks"]["accepted_inputs"]["total_errors"]
        good = good and all("error" not in report["site_checks"][key]
                            for key in ("input_root", "durable_bulk_root", "durable_control_root"))
        good = good and all(report["site_checks"][key].get("readable", False)
                            for key in ("input_root", "durable_bulk_root", "durable_control_root"))
    return 0 if good else 42


def _extract_frozen(source_tar, source_facts, destination):
    facts = r.json_file(source_facts)
    if set(facts) != set(SOURCE_FILES):
        raise ValueError("frozen source fileset differs")
    with tarfile.open(source_tar, "r:gz") as archive:
        names = [member.name for member in archive.getmembers()]
        if names != list(SOURCE_FILES) or any(not member.isfile() for member in archive.getmembers()):
            raise ValueError("frozen source tar fileset/type differs")
        for member in archive.getmembers():
            path = destination / member.name
            path.parent.mkdir(parents=True, exist_ok=True)
            content = archive.extractfile(member).read()
            if (len(content) != facts[member.name]["bytes"] or
                    hashlib.sha256(content).hexdigest() != facts[member.name]["sha256"]):
                raise ValueError("frozen source member differs")
            path.write_bytes(content)


def _extract_pack(pack_tar, destination):
    with tarfile.open(pack_tar, "r:gz") as archive:
        members = archive.getmembers()
        names = {member.name.removeprefix("./") for member in members if member.isfile()}
        if names != {"query", "build-receipt.json", "manifest.json"} or any(
                member.issym() or member.islnk() for member in members):
            raise ValueError("prepared Linux pack fileset/type differs")
        for member in members:
            if not member.isfile(): continue
            name = member.name.removeprefix("./")
            path = destination / name
            path.write_bytes(archive.extractfile(member).read())
            if name == "query": path.chmod(0o755)


def _checked_input(path, fact):
    if path.name != fact["name"] or path.stat().st_size != fact["bytes"] or r.sha_file(path) != fact["sha256"]:
        raise ValueError("accepted input differs from frozen work manifest")


def _stage_workspace(workspace, destination, ordinal, attempt, work_sha):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise ValueError("attempt destination already exists")
    stage = Path(tempfile.mkdtemp(prefix="."+destination.name+".stage-", dir=str(destination.parent)))
    # Interrupted private stages are retained for custody/review.
    shutil.copytree(workspace, stage / "workspace")
    artifacts = {p.name: {"bytes": p.stat().st_size, "sha256": r.sha_file(p)}
                 for p in (stage / "workspace").iterdir()}
    metadata = r.json_file(stage / "workspace/metadata.json")
    receipt = {"schema": ATTEMPT_SCHEMA, "ordinal": ordinal, "attempt": attempt,
               "work_sha256": work_sha, "scientific_content_sha256": metadata["query_content_sha256"],
               "artifacts": artifacts}
    r.atomic_json(stage / "attempt.json", receipt, exclusive=True)
    for p in (stage / "workspace").iterdir(): r.fsync_file(p)
    r.fsync_directory(stage / "workspace")
    r.fsync_file(stage / "attempt.json")
    r.fsync_directory(stage)
    q.publish_directory(stage, destination)
    r.fsync_directory(destination.parent)
    for name, fact in artifacts.items():
        path = destination / "workspace" / name
        if path.stat().st_size != fact["bytes"] or r.sha_file(path) != fact["sha256"]:
            raise ValueError("durable attempt readback differs")
    return receipt


def _stage_failure(destination, ordinal, attempt, work_sha, result):
    """Retain a bounded non-acceptance receipt for a failed child attempt."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise ValueError("immutable attempt path already exists")
    stage = Path(tempfile.mkdtemp(prefix="."+destination.name+".failed-", dir=str(destination.parent)))
    failure = {"schema": FAILURE_SCHEMA, "state": "PRESERVED_FAILED_ATTEMPT",
               "ordinal": ordinal, "attempt": attempt, "work_sha256": work_sha,
               "child_exit": result.returncode, "stderr_tail": result.stderr[-4096:],
               "stdout_tail": result.stdout[-4096:]}
    r.atomic_json(stage / "failure.json", failure, exclusive=True)
    r.fsync_file(stage / "failure.json")
    r.fsync_directory(stage)
    q.publish_directory(stage, destination)
    r.fsync_directory(destination.parent)
    if r.json_file(destination / "failure.json") != failure:
        raise ValueError("durable failure evidence readback differs")
    return failure


def worker(work_path, expected_work_sha, ordinal, attempt, source_tar, source_facts, pack_tar):
    work = _work(work_path, expected_work_sha)
    _resolved(work)
    if type(attempt) is not int or attempt not in (0, 1, 2):
        raise ValueError("attempt is outside bounded retry domain")
    if type(ordinal) is not int or not 0 <= ordinal < len(work["work"]):
        raise ValueError("worker ordinal is foreign")
    if (r.sha_file(source_tar) != work["source_tar_sha256"] or
            r.sha_file(source_facts) != work["source_files_sha256"] or
            r.sha_file(pack_tar) != work["prepared_pack_tar_sha256"] or
            r.sha_file(Path("dictionary.json")) != work["dictionary_sha256"]):
        raise ValueError("frozen source or Linux pack identity differs")
    item = work["work"][ordinal]
    input_root = Path(work["input_root"])
    root = input_root / item["root"]["name"]
    receipt = input_root / item["receipt"]["name"]
    _checked_input(root, item["root"])
    _checked_input(receipt, item["receipt"])
    attempt_dir = Path(work["durable_bulk_root"]) / ("shard-%04d" % ordinal) / ("attempt-%02d" % attempt)
    if attempt_dir.exists():
        raise ValueError("immutable attempt path already exists")
    with tempfile.TemporaryDirectory(prefix="hadronization-query-", dir=os.environ.get("TMPDIR")) as temporary:
        scratch = Path(temporary)
        source_dir = scratch / "source"; pack_dir = scratch / "pack"
        source_dir.mkdir(); pack_dir.mkdir()
        _extract_frozen(source_tar, source_facts, source_dir)
        _extract_pack(pack_tar, pack_dir)
        command = [sys.executable, "-B", str(source_dir / "hadronization"), "query", "build",
                   "--input", str(root), "--receipt", str(receipt),
                   "--accepted-receipt-sha256", item["receipt"]["sha256"],
                   "--dictionary", str(Path("dictionary.json").absolute()),
                   "--analysis", str(source_dir / "config/analysis.json"),
                   "--layout", str(source_dir / "config/query.json"),
                   "--prepared-pack", str(pack_dir), "--output", str(scratch / "query"),
                   "--work-root", str(scratch / "work")]
        result = subprocess.run(command, text=True, capture_output=True)
        if result.returncode:
            _stage_failure(attempt_dir, ordinal, attempt, expected_work_sha, result)
            if result.returncode == 75:
                raise TransientError("query child reported classified transient failure")
            raise ValueError("deterministic query build/verification failure: " + result.stderr[-2000:])
        stage = _stage_workspace(scratch / "query", attempt_dir, ordinal, attempt, expected_work_sha)
        print("STAGED_ATTEMPT="+str(attempt_dir)+" CONTENT="+stage["scientific_content_sha256"])


def _external_pins(path, expected_sha, ordinals):
    r.lower_sha(expected_sha, "independent accepted content pin file")
    if r.sha_file(path) != expected_sha:
        raise ValueError("external accepted content pins differ")
    payload = r.json_file(path)
    if payload.get("schema") != PINS_SCHEMA or payload.get("authority") != "EXTERNAL_REVIEW":
        raise ValueError("content pins lack external review authority")
    pins = payload.get("pins")
    if not isinstance(pins, list) or [x.get("ordinal") for x in pins] != list(range(ordinals)):
        raise ValueError("external accepted pin ordinal domain differs")
    for item in pins:
        if type(item.get("attempt")) is not int or item["attempt"] not in (0, 1, 2):
            raise ValueError("accepted attempt number differs")
        r.lower_sha(item.get("scientific_content_sha256"), "accepted query content")
    return pins


def collect(work_path, expected_work_sha, expected_sources, source_tar, pins_path, pins_sha):
    work = _work(work_path, expected_work_sha)
    _resolved(work)
    control = Path(work["durable_control_root"]).resolve()
    pins_path = Path(pins_path).resolve()
    if control not in pins_path.parents or pins_path.parent == control / "collections":
        raise ValueError("external pins are not separately held in control custody")
    if r.sha_file(expected_sources) != work["expected_sources_sha256"]:
        raise ValueError("expected source manifest differs")
    if r.sha_file(source_tar) != work["source_tar_sha256"]:
        raise ValueError("frozen source tar differs")
    pins = _external_pins(pins_path, pins_sha, len(work["work"]))
    workspaces, contents = [], []
    for pin in pins:
        ordinal, attempt = pin["ordinal"], pin["attempt"]
        directory = Path(work["durable_bulk_root"]) / ("shard-%04d" % ordinal) / ("attempt-%02d" % attempt)
        attempt_receipt = r.json_file(directory / "attempt.json")
        if (attempt_receipt.get("schema") != ATTEMPT_SCHEMA or
                attempt_receipt.get("ordinal") != ordinal or attempt_receipt.get("attempt") != attempt or
                attempt_receipt.get("work_sha256") != expected_work_sha or
                attempt_receipt.get("scientific_content_sha256") != pin["scientific_content_sha256"]):
            raise ValueError("attempt receipt differs from independent accepted pin")
        workspace = directory / "workspace"
        if {p.name for p in workspace.iterdir()} != set(attempt_receipt["artifacts"]):
            raise ValueError("attempt workspace fileset differs")
        for name, fact in attempt_receipt["artifacts"].items():
            path = workspace / name
            if path.stat().st_size != fact["bytes"] or r.sha_file(path) != fact["sha256"]:
                raise ValueError("accepted attempt durable readback differs")
        workspaces.append(workspace)
        contents.append(pin["scientific_content_sha256"])
    output = control / "collections" / ("collection-" + expected_work_sha[:16])
    if output.exists():
        raise ValueError("collection publication already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="."+output.name+".stage-", dir=str(output.parent)))
    try:
        index_path = stage / "index.json"
        index = c.create(workspaces, contents, r.json_file(expected_sources), index_path,
                         stage / "verify-work", test_only=False)
        if (index["campaign"] != work["campaign_id"] or
                index["manifest_sha256"] != work["source_manifest_sha256"] or
                index["block_count"] != work["block_count"] or
                index["tune_ordinals"] != work["tune_ordinals"] or
                index["analysis_sha256"] != work["analysis_sha256"] or
                index["layout_sha256"] != work["layout_sha256"] or
                len(index["sources"]) != work["expected_source_count"] or
                sum(s["events"] for s in index["sources"]) != work["expected_event_count"]):
            raise ValueError("full campaign source/event closure differs")
        manifest = {"schema": "hadronization_query_collection_closure_v1", "state": "EXTERNALLY_PINNED",
                    "work_sha256": expected_work_sha, "external_pins_sha256": pins_sha,
                    "index_sha256": r.sha_file(index_path),
                    "scientific_identity_sha256": index["scientific_identity_sha256"],
                    "source_count": len(index["sources"]),
                    "event_count": sum(s["events"] for s in index["sources"])}
        r.atomic_json(stage / "manifest.json", manifest, exclusive=True)
        for p in stage.iterdir():
            if p.is_file(): r.fsync_file(p)
        r.fsync_directory(stage)
        q.publish_directory(stage, output)
        r.fsync_directory(output.parent)
        if r.sha_file(output / "index.json") != manifest["index_sha256"]:
            raise ValueError("published collection readback differs")
        print("COLLECTION_CLOSED="+str(output / "index.json"))
    finally:
        if stage.exists(): shutil.rmtree(stage)


def _checked_site_bundle(bundle, bundle_sha):
    bundle = Path(bundle).absolute()
    r.reject_symlink_components(bundle, "site-bound bundle")
    r.lower_sha(bundle_sha, "site-bound bundle pin")
    if r.sha_file(bundle / "bundle-manifest.json") != bundle_sha:
        raise ValueError("site-bound bundle manifest differs")
    manifest = r.json_file(bundle / "bundle-manifest.json")
    if (manifest.get("schema") != "hadronization_site_bound_condor_bundle_v1" or
            manifest.get("state") != "SITE_BOUND" or
            set(manifest.get("files", {})) !=
            {path.name for path in bundle.iterdir() if path.is_file() and
             path.name != "bundle-manifest.json"}):
        raise ValueError("site-bound bundle fileset/state differs")
    for name, fact in manifest["files"].items():
        path = bundle / name
        if path.stat().st_size != fact["bytes"] or r.sha_file(path) != fact["sha256"]:
            raise ValueError("site-bound bundle file differs: " + name)
    work_sha = manifest["work_sha256"]
    work = _work(bundle / "work.json", work_sha)
    _resolved(work)
    return bundle, manifest, work_sha, work


def stage_dag(bundle, bundle_sha, output):
    """Copy checked worker inputs to a disposable no-overwrite DAGMan launch root."""
    bundle, manifest, work_sha, work = _checked_site_bundle(bundle, bundle_sha)
    output = Path(output).absolute()
    r.reject_symlink_components(output, "DAG launch destination")
    if (not output.is_absolute() or output == bundle or bundle in output.parents or
            output in bundle.parents or output.exists()):
        raise ValueError("DAG launch requires a distinct unused directory")
    names = ("workflow.dag", "worker.sub", "worker.py", "work.json", "source.tar.gz",
             "source-files.json", "dictionary.json", "query-pack.tar.gz")
    if any(name not in manifest["files"] for name in names):
        raise ValueError("site-bound bundle omits a required DAG input")
    for name, key in (("source.tar.gz", "source_tar_sha256"),
                      ("source-files.json", "source_files_sha256"),
                      ("dictionary.json", "dictionary_sha256"),
                      ("query-pack.tar.gz", "prepared_pack_tar_sha256")):
        if manifest["files"][name]["sha256"] != work[key]:
            raise ValueError("DAG input differs from bound work: " + name)
    submit = (bundle / "worker.sub").read_text()
    if (work_sha not in submit or re.search(r"__[A-Z][A-Z0-9_]*__", submit) or
            "transfer_input_files = worker.py,work.json,source.tar.gz,source-files.json,dictionary.json,query-pack.tar.gz" not in submit):
        raise ValueError("worker submit is not fully bound to staged inputs")
    dag = (bundle / "workflow.dag").read_text()
    if (dag.count("JOB q") != len(work["work"]) or
            dag.count("RETRY q") != len(work["work"]) or
            dag.count("ABORT-DAG-ON q") != len(work["work"]) or
            "MAXJOBS query 4\n" not in dag):
        raise ValueError("DAG worker domain differs from bound work")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="."+output.name+".stage-", dir=str(output.parent)))
    try:
        for name in names:
            shutil.copy2(bundle / name, stage / name)
            fact = manifest["files"][name]
            if (stage / name).stat().st_size != fact["bytes"] or r.sha_file(stage / name) != fact["sha256"]:
                raise ValueError("staged DAG input readback differs: " + name)
        (stage / "logs").mkdir()
        receipt = {"schema": "hadronization_staged_query_dag_v1", "state": "READY_FOR_NO_SUBMIT_REVIEW",
                   "site_bound_bundle_manifest_sha256": bundle_sha,
                   "work_sha256": work_sha,
                   "worker_count": len(work["work"]),
                   "files": {name: manifest["files"][name] for name in names}}
        r.atomic_json(stage / "launch-receipt.json", receipt, exclusive=True)
        for name in names: r.fsync_file(stage / name)
        r.fsync_file(stage / "launch-receipt.json")
        r.fsync_directory(stage / "logs")
        r.fsync_directory(stage)
        q.publish_directory(stage, output)
        r.fsync_directory(output.parent)
        for name, fact in receipt["files"].items():
            if r.sha_file(output / name) != fact["sha256"]:
                raise ValueError("published DAG input readback differs: " + name)
        return output / "workflow.dag"
    finally:
        if stage.exists(): shutil.rmtree(stage)


def render_collector(bundle, bundle_sha, pins_path, pins_sha, output):
    """Publish a separate pinned submit file after all attempts are accepted.

    The site-bound bundle remains immutable; the independent control owner
    supplies exact content pins only after the worker DAG has finished.
    """
    bundle, manifest, work_sha, work = _checked_site_bundle(bundle, bundle_sha)
    pins_path, output = (Path(path).absolute() for path in (pins_path, output))
    control = Path(work["durable_control_root"]).resolve()
    r.reject_symlink_components(pins_path, "external accepted pins")
    r.reject_symlink_components(output, "rendered collector destination")
    if (control not in pins_path.parents or control / "collections" in pins_path.parents or
            control not in output.parents or control / "collections" in output.parents or
            output.exists()):
        raise ValueError("collector pins/output require separate unused control custody")
    if any(character.isspace() or character in {'"', "'"} for character in str(pins_path)):
        raise ValueError("collector pin path cannot be represented in submit arguments")
    pins = _external_pins(pins_path, pins_sha, len(work["work"]))
    for pin in pins:
        directory = (Path(work["durable_bulk_root"]) /
                     ("shard-%04d" % pin["ordinal"]) /
                     ("attempt-%02d" % pin["attempt"]))
        attempt = r.json_file(directory / "attempt.json")
        if (attempt.get("schema") != ATTEMPT_SCHEMA or
                attempt.get("ordinal") != pin["ordinal"] or
                attempt.get("attempt") != pin["attempt"] or
                attempt.get("work_sha256") != work_sha or
                attempt.get("scientific_content_sha256") != pin["scientific_content_sha256"]):
            raise ValueError("accepted attempt receipt differs from external pin")
    template = (bundle / "collector.sub").read_text()
    path_token, sha_token = ("__EXTERNALLY_ACCEPTED_PINS_PATH__",
                             "__EXTERNALLY_ACCEPTED_PINS_SHA256__")
    if template.count(path_token) != 1 or template.count(sha_token) != 1:
        raise ValueError("collector submit pin template differs")
    submit = template.replace(path_token, str(pins_path)).replace(sha_token, pins_sha)
    if re.search(r"__[A-Z][A-Z0-9_]*__", submit):
        raise ValueError("collector submit template has unresolved site placeholder")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="." + output.name + ".stage-", dir=str(output.parent)))
    try:
        (stage / "collector.sub").write_text(submit)
        receipt = {"schema": "hadronization_rendered_collector_submit_v1",
                   "site_bound_bundle_manifest_sha256": bundle_sha,
                   "work_sha256": work_sha, "external_pins_sha256": pins_sha,
                   "collector_submit_sha256": r.sha_file(stage / "collector.sub"),
                   "accepted_attempts": len(pins)}
        r.atomic_json(stage / "receipt.json", receipt, exclusive=True)
        for path in stage.iterdir(): r.fsync_file(path)
        r.fsync_directory(stage)
        q.publish_directory(stage, output)
        r.fsync_directory(output.parent)
        if r.sha_file(output / "collector.sub") != receipt["collector_submit_sha256"]:
            raise ValueError("rendered collector submit readback differs")
        return output / "collector.sub"
    finally:
        if stage.exists(): shutil.rmtree(stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare", help="create an inert native query DAG bundle")
    prepare_parser.add_argument("--acquisition", type=Path, required=True)
    prepare_parser.add_argument("--expected-acquisition-sha256", required=True)
    prepare_parser.add_argument("--dictionary", type=Path, required=True)
    prepare_parser.add_argument("--expected-dictionary-sha256", required=True)
    prepare_parser.add_argument("--output", type=Path, required=True)
    bind_parser = commands.add_parser("bind-site", help="bind an admitted immutable site bundle")
    for option in ("bundle", "pack", "admission", "output"):
        bind_parser.add_argument("--"+option, type=Path, required=True)
    for option in ("bundle", "pack", "admission"):
        bind_parser.add_argument("--expected-"+option+"-sha256", required=True)
    preflight_parser = commands.add_parser("preflight", help="read-only local/site facts")
    preflight_parser.add_argument("--work", type=Path, required=True)
    preflight_parser.add_argument("--expected-work-sha256", required=True)
    preflight_parser.add_argument("--source-tar", type=Path, required=True)
    preflight_parser.add_argument("--pack-tar", type=Path)
    preflight_parser.add_argument("--full-input-hash", action="store_true")
    worker_parser = commands.add_parser("worker")
    worker_parser.add_argument("--work", type=Path, required=True)
    worker_parser.add_argument("--expected-work-sha256", required=True)
    worker_parser.add_argument("--ordinal", type=int, required=True)
    worker_parser.add_argument("--attempt", type=int, required=True)
    worker_parser.add_argument("--source-tar", type=Path, required=True)
    worker_parser.add_argument("--source-facts", type=Path, default=Path("source-files.json"))
    worker_parser.add_argument("--pack-tar", type=Path, required=True)
    collector_parser = commands.add_parser("collect")
    collector_parser.add_argument("--work", type=Path, required=True)
    collector_parser.add_argument("--expected-work-sha256", required=True)
    collector_parser.add_argument("--expected-sources", type=Path, required=True)
    collector_parser.add_argument("--source-tar", type=Path, required=True)
    collector_parser.add_argument("--pins", type=Path, required=True)
    collector_parser.add_argument("--expected-pins-sha256", required=True)
    render_parser = commands.add_parser("render-collector", help="pin a separate collector submit file after accepted attempts")
    render_parser.add_argument("--bundle", type=Path, required=True)
    render_parser.add_argument("--expected-bundle-sha256", required=True)
    render_parser.add_argument("--pins", type=Path, required=True)
    render_parser.add_argument("--expected-pins-sha256", required=True)
    render_parser.add_argument("--output", type=Path, required=True)
    stage_parser = commands.add_parser("stage-dag", help="copy bound worker inputs to a separate DAGMan launch directory")
    stage_parser.add_argument("--bundle", type=Path, required=True)
    stage_parser.add_argument("--expected-bundle-sha256", required=True)
    stage_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            path = prepare(args.acquisition, args.expected_acquisition_sha256,
                           args.dictionary, args.expected_dictionary_sha256, args.output)
            print("INERT_CONDOR_BUNDLE="+str(path.parent)+" SHA256="+r.sha_file(path))
        elif args.command == "bind-site":
            path = bind_site(args.bundle, args.expected_bundle_sha256,
                             args.pack, args.expected_pack_sha256,
                             args.admission, args.expected_admission_sha256, args.output)
            print("SITE_BOUND_CONDOR_BUNDLE="+str(path.parent)+" SHA256="+r.sha_file(path))
        elif args.command == "preflight":
            return preflight(args.work, args.expected_work_sha256, args.source_tar,
                             args.pack_tar, args.full_input_hash)
        elif args.command == "worker":
            worker(args.work, args.expected_work_sha256, args.ordinal, args.attempt,
                   args.source_tar, args.source_facts, args.pack_tar)
        elif args.command == "render-collector":
            path = render_collector(args.bundle, args.expected_bundle_sha256,
                                    args.pins, args.expected_pins_sha256, args.output)
            print("RENDERED_COLLECTOR="+str(path)+" SHA256="+r.sha_file(path))
        elif args.command == "stage-dag":
            path = stage_dag(args.bundle, args.expected_bundle_sha256, args.output)
            print("STAGED_DAG="+str(path)+" SHA256="+r.sha_file(path))
        else:
            collect(args.work, args.expected_work_sha256, args.expected_sources,
                    args.source_tar, args.pins, args.expected_pins_sha256)
    except TransientError as error:
        print("ERROR: "+str(error), file=sys.stderr)
        return 75
    except OSError as error:
        print("ERROR: "+str(error), file=sys.stderr)
        return 75 if error.errno in TRANSIENT_ERRNOS else 42
    except (ValueError, KeyError, TypeError, tarfile.TarError) as error:
        print("ERROR: "+str(error), file=sys.stderr)
        return 42
    return 0


if __name__ == "__main__":
    sys.exit(main())
