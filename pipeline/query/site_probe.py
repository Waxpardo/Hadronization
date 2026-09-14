#!/usr/bin/env python3
"""One-shot execute-node and POSIX publication qualification probe.

This program is inert until explicitly run with measured paths. Its JSON output
is evidence for an independent admission decision, never an admission receipt.
"""

import argparse
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import subprocess
import sys
import time
import uuid


def _publication():
    path = Path(__file__).with_name("publication.py")
    spec = importlib.util.spec_from_file_location("site_publication", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publication = _publication()


def _runtime():
    local = Path(__file__).with_name("runtime.py")
    path = local if local.is_file() else Path(__file__).parents[1] / "generate/runtime.py"
    spec = importlib.util.spec_from_file_location("site_runtime", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command, environment=None):
    result = subprocess.run(command, text=True, capture_output=True, timeout=30,
                            env=environment)
    if result.returncode:
        raise ValueError("command failed: {}: {}".format(command, result.stderr[-500:]))
    return result.stdout.strip()


def check_almalinux_release(os_release, expected_version):
    if not re.fullmatch(r"9\.[0-9]+", expected_version):
        raise ValueError("expected AlmaLinux minor version is not an explicit EL9 pin")
    fields = {}
    for line in os_release.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            fields[key] = value.strip().strip('"')
    if fields.get("ID") != "almalinux":
        raise ValueError("execute-node distribution differs")
    if fields.get("VERSION_ID") != expected_version:
        raise ValueError("execute-node AlmaLinux version differs from selected pin")
    return {"distribution": "almalinux", "version": expected_version,
            "os_release_sha256": hashlib.sha256(os_release.encode("utf-8")).hexdigest()}


def _ad(path, role, required):
    if not path.is_file() or path.is_symlink():
        raise ValueError("execute-node " + role + " ClassAd is missing or unsafe")
    raw = path.read_bytes()
    fields = {}
    for line in raw.decode("utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.*?)\s*", line)
        if not match:
            raise ValueError("execute-node " + role + " ClassAd has an invalid line")
        key = match.group(1).lower()
        if key in fields:
            raise ValueError("execute-node " + role + " ClassAd repeats " + match.group(1))
        fields[key] = match.group(2)
    for field in required:
        if field.lower() not in fields:
            raise ValueError("execute-node " + role + " ClassAd lacks " + field)
    return fields, hashlib.sha256(raw).hexdigest()


def classad_evidence(expected_image=None):
    job = Path(os.environ.get("_CONDOR_JOB_AD", ""))
    machine = Path(os.environ.get("_CONDOR_MACHINE_AD", ""))
    if job == machine or (job.is_file() and machine.is_file() and job.samefile(machine)):
        raise ValueError("job and machine ClassAd paths are not distinct")
    requests, job_sha = _ad(job, "job", ("RequestMemory", "RequestDisk"))
    matched, machine_sha = _ad(machine, "machine", ("Arch", "OpSys"))
    if expected_image is not None and requests.get("singularityimage") != (
            '"' + expected_image + '"'):
        raise ValueError("job ClassAd container image differs from selected pin")
    for role, fields in (("job", requests), ("machine", matched)):
        my_type = fields.get("mytype")
        if my_type is not None and my_type != '"' + role.capitalize() + '"':
            raise ValueError("execute-node " + role + " ClassAd has wrong MyType")
    if matched["arch"] != '"X86_64"' or matched["opsys"] != '"LINUX"':
        raise ValueError("matched machine ClassAd architecture/OS differs")
    values = {}
    for field in ("RequestMemory", "RequestDisk"):
        raw = requests[field.lower()]
        if not re.fullmatch(r"[1-9][0-9]*", raw):
            raise ValueError("job ClassAd " + field + " is not a positive integer")
        values[field] = int(raw)
    for field, request in (("Memory", "RequestMemory"), ("Disk", "RequestDisk")):
        raw = matched.get(field.lower())
        if raw is not None and (not re.fullmatch(r"[1-9][0-9]*", raw) or
                                int(raw) < values[request]):
            raise ValueError("matched machine ClassAd " + field + " cannot satisfy job request")
    return {"job": {"path": str(job), "sha256": job_sha,
                    "container_image": expected_image,
                    "request_memory_mb": values["RequestMemory"],
                    "request_disk_kb": values["RequestDisk"]},
            "machine": {"path": str(machine), "sha256": machine_sha,
                        "arch": "X86_64", "opsys": "LINUX",
                        "memory_mb": int(matched["memory"]) if "memory" in matched else None,
                        "disk_kb": int(matched["disk"]) if "disk" in matched else None}}


def _fsync_directory(path):
    fd = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_closed(path, payload):
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def publish_probe(root, label):
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(label + " is not a directory")
    name = "qualification-" + uuid.uuid4().hex
    stage = root / ("." + name + ".stage")
    stage.mkdir(mode=0o700)
    final = root / name
    payload = os.urandom(1024 * 1024)
    expected = hashlib.sha256(payload).hexdigest()
    _write_closed(stage / "payload.bin", payload)
    _fsync_directory(stage)
    _fsync_directory(root)
    published_by = publication.publish_directory(stage, final)
    _fsync_directory(root)
    payload_path = final / "payload.bin"
    if payload_path.stat().st_size != len(payload) or sha(payload_path) != expected:
        raise ValueError(label + " durable readback differs")
    collisions = {}
    for kind in ("empty", "nonempty"):
        destination = root / (name + ".existing-" + kind)
        destination.mkdir(mode=0o700)
        sentinel = b"EXISTING_QUALIFICATION_ONLY"
        if kind == "nonempty":
            _write_closed(destination / "sentinel.bin", sentinel)
        contender = root / ("." + name + ".contender-" + kind)
        contender.mkdir(mode=0o700)
        _write_closed(contender / "payload.bin", payload)
        _fsync_directory(contender)
        _fsync_directory(destination)
        _fsync_directory(root)
        try:
            publication.publish_directory(contender, destination)
        except OSError as error:
            if error.errno not in (errno.EEXIST, errno.ENOTEMPTY):
                raise
        else:
            raise ValueError(label + " existing " + kind + " directory was overwritten")
        if (not contender.is_dir() or not (contender / "payload.bin").is_file() or
                (kind == "empty" and list(destination.iterdir())) or
                (kind == "nonempty" and
                 (not (destination / "sentinel.bin").is_file() or
                  (destination / "sentinel.bin").read_bytes() != sentinel))):
            raise ValueError(label + " existing " + kind + " directory changed")
        collisions[kind] = {"destination": str(destination), "stage": str(contender),
                            "refused": "PASS"}
    partial = root / ("." + name + ".interrupted-stage")
    partial.mkdir(mode=0o700)
    partial_content = b"INTERRUPTED_QUALIFICATION_ONLY"
    _write_closed(partial / "payload.bin", partial_content)
    _fsync_directory(partial)
    _fsync_directory(root)
    if (not partial.is_dir() or sha(partial / "payload.bin") !=
            hashlib.sha256(partial_content).hexdigest() or
            payload_path.stat().st_size != len(payload) or sha(payload_path) != expected):
        raise ValueError(label + " interrupted stage or published payload differs")
    return {"root": str(root), "published": str(final), "payload": str(payload_path),
            "bytes": len(payload), "sha256": expected, "interrupted_stage": str(partial),
            "interrupted_sha256": hashlib.sha256(partial_content).hexdigest(),
            "existing_destinations": collisions, "directory_publish": "PASS",
            "no_overwrite": "PASS", "readback": "PASS",
            "publication": published_by}


def probe(args):
    started = time.monotonic()
    if args.bulk_root.resolve() == args.control_root.resolve() or (
            args.bulk_root.resolve() in args.control_root.resolve().parents or
            args.control_root.resolve() in args.bulk_root.resolve().parents):
        raise ValueError("bulk and protected control roots must be separate")
    if sha(args.input_root) != args.input_sha256:
        raise ValueError("accepted input SHA differs before ROOT open")
    classads = classad_evidence(str(args.expected_image_path))
    resolver = _runtime()
    resolved = resolver.resolve(resolver.site_values(args.site_conf),
                                require_root=True, require_pythia=True)
    environment = dict(os.environ, **resolved["environment"])
    if (environment["ROOT_CONFIG"], environment["CXX"],
            environment["PYTHIA8_CONFIG"]) != (
            args.root_config, args.cxx, args.pythia_config):
        raise ValueError("execute-node site runtime paths differ from selected pin")
    root_version = run([args.root_config, "--version"], environment)
    gcc_version = run([args.cxx, "-dumpfullversion", "-dumpversion"],
                      environment).splitlines()[0]
    pythia_version = run([args.pythia_config, "--version"], environment)
    if (root_version, gcc_version, pythia_version) != ("6.30.01", "14.2.0", "8.317"):
        raise ValueError("pinned runtime versions differ")
    if platform.machine() != "x86_64":
        raise ValueError("execute-node architecture differs")
    os_release = Path("/etc/os-release").read_text(encoding="utf-8")
    operating_system = check_almalinux_release(
        os_release, args.expected_almalinux_version)
    if not args.cvmfs_path.is_dir() or not os.access(args.cvmfs_path, os.R_OK):
        raise ValueError("execute-node CVMFS path is unavailable")
    root_binary = Path(args.root_config).with_name("root")
    run([str(root_binary), "-b", "-q", "-e", 'gSystem->Load("libTree");'],
        environment)
    run([sys.executable, "-c",
         "import ROOT,sys; f=ROOT.TFile.Open(sys.argv[1]); "
         "assert f and not f.IsZombie(); f.Close()", str(args.input_root)],
        environment)
    bulk = publish_probe(args.bulk_root, "bulk")
    control = publish_probe(args.control_root, "control")
    stat = shutil.disk_usage(args.bulk_root)
    return {"schema": "hadronization_execute_node_site_probe_v1",
            "status": "OBSERVED_ONLY_NOT_ADMISSION", "hostname": platform.node(),
            "architecture": platform.machine(), "platform": platform.platform(),
            "operating_system": operating_system,
            "classads": classads,
            "input": {"path": str(args.input_root), "bytes": args.input_root.stat().st_size,
                      "sha256": args.input_sha256},
            "versions": {"root": root_version, "gcc": gcc_version, "pythia": pythia_version},
            "site_conf_sha256": sha(args.site_conf),
            "cvmfs_path": str(args.cvmfs_path.resolve()),
            "bulk": bulk, "control": control,
            "bulk_free_bytes_observed": stat.free,
            "max_rss_kib_observed": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "scratch_free_bytes_observed": shutil.disk_usage(Path.cwd()).free,
            "elapsed_seconds": round(time.monotonic() - started, 3)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--bulk-root", type=Path, required=True)
    parser.add_argument("--control-root", type=Path, required=True)
    parser.add_argument("--root-config", required=True)
    parser.add_argument("--cxx", required=True)
    parser.add_argument("--pythia-config", required=True)
    parser.add_argument("--cvmfs-path", type=Path, required=True)
    parser.add_argument("--site-conf", type=Path, required=True)
    parser.add_argument("--expected-almalinux-version", required=True,
                        help="exact EL9 minor version selected for this canary")
    parser.add_argument("--expected-image-path", type=Path, required=True,
                        help="exact container image path pinned in the job ClassAd")
    args = parser.parse_args()
    try:
        print(json.dumps(probe(args), sort_keys=True))
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print("SITE_PROBE_ERROR: " + str(error), file=sys.stderr)
        return 42
    return 0


if __name__ == "__main__":
    sys.exit(main())
