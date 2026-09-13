#!/usr/bin/env python3
"""One-shot execute-node and POSIX publication qualification probe.

This program is inert until explicitly run with measured paths. Its JSON output
is evidence for an independent admission decision, never an admission receipt.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import time
import uuid


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command):
    result = subprocess.run(command, text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise ValueError("command failed: {}: {}".format(command, result.stderr[-500:]))
    return result.stdout.strip()


def publish_probe(root, label):
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(label + " is not a directory")
    name = "qualification-" + uuid.uuid4().hex
    final = root / name
    payload = os.urandom(1024 * 1024)
    expected = hashlib.sha256(payload).hexdigest()
    fd = os.open(str(final), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        raise
    dir_fd = os.open(str(root), os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)
    if final.stat().st_size != len(payload) or sha(final) != expected:
        raise ValueError(label + " durable readback differs")
    try:
        duplicate = os.open(str(final), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        os.close(duplicate)
        raise ValueError(label + " no-overwrite check failed")
    partial = root / (name + ".partial")
    fd = os.open(str(partial), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(b"INTERRUPTED_QUALIFICATION_ONLY")
        stream.flush()
        os.fsync(stream.fileno())
    if final.stat().st_size != len(payload) or sha(final) != expected:
        raise ValueError(label + " interrupted sibling changed published payload")
    return {"root": str(root), "published": str(final), "bytes": len(payload),
            "sha256": expected, "partial": str(partial),
            "no_overwrite": "PASS", "readback": "PASS"}


def probe(args):
    started = time.monotonic()
    if args.bulk_root.resolve() == args.control_root.resolve() or (
            args.bulk_root.resolve() in args.control_root.resolve().parents or
            args.control_root.resolve() in args.bulk_root.resolve().parents):
        raise ValueError("bulk and protected control roots must be separate")
    if sha(args.input_root) != args.input_sha256:
        raise ValueError("accepted input SHA differs before ROOT open")
    classad = Path(os.environ.get("_CONDOR_JOB_AD", ""))
    if not classad.is_file():
        raise ValueError("execute-node ClassAd is missing")
    ads = classad.read_text(encoding="utf-8")
    for field in ("Arch", "OpSys", "RequestMemory", "RequestDisk"):
        if not any(line.startswith(field + " =") for line in ads.splitlines()):
            raise ValueError("execute-node ClassAd lacks " + field)
    root_version = run([args.root_config, "--version"])
    gcc_version = run([args.cxx, "-dumpfullversion", "-dumpversion"]).splitlines()[0]
    pythia_version = run([args.pythia_config, "--version"])
    if (root_version, gcc_version, pythia_version) != ("6.30.01", "14.2.0", "8.317"):
        raise ValueError("pinned runtime versions differ")
    if platform.machine() != "x86_64":
        raise ValueError("execute-node architecture differs")
    os_release = Path("/etc/os-release").read_text(encoding="utf-8")
    if 'VERSION_ID="9.8"' not in os_release and 'VERSION_ID=9.8' not in os_release:
        raise ValueError("execute-node AlmaLinux 9.8 release differs")
    if 'ID="almalinux"' not in os_release and 'ID=almalinux' not in os_release:
        raise ValueError("execute-node distribution differs")
    if not args.cvmfs_path.is_dir() or not os.access(args.cvmfs_path, os.R_OK):
        raise ValueError("execute-node CVMFS path is unavailable")
    root_binary = Path(args.root_config).with_name("root")
    run([str(root_binary), "-b", "-q", "-e", 'gSystem->Load("libTree");'])
    run([sys.executable, "-c",
         "import ROOT,sys; f=ROOT.TFile.Open(sys.argv[1]); "
         "assert f and not f.IsZombie(); f.Close()", str(args.input_root)])
    bulk = publish_probe(args.bulk_root, "bulk")
    control = publish_probe(args.control_root, "control")
    stat = shutil.disk_usage(args.bulk_root)
    return {"schema": "hadronization_execute_node_site_probe_v1",
            "status": "OBSERVED_ONLY_NOT_ADMISSION", "hostname": platform.node(),
            "architecture": platform.machine(), "platform": platform.platform(),
            "classad_sha256": sha(classad), "classad_path": str(classad),
            "input": {"path": str(args.input_root), "bytes": args.input_root.stat().st_size,
                      "sha256": args.input_sha256},
            "versions": {"root": root_version, "gcc": gcc_version, "pythia": pythia_version},
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
    args = parser.parse_args()
    try:
        print(json.dumps(probe(args), sort_keys=True))
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print("SITE_PROBE_ERROR: " + str(error), file=sys.stderr)
        return 42
    return 0


if __name__ == "__main__":
    sys.exit(main())
