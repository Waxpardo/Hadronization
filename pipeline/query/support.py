"""Query-owned file, build and admitted analyzed-input helpers."""
import fcntl
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[2]
TRANSIENT_ERRNOS = frozenset((errno.EAGAIN, errno.ESTALE, errno.ETIMEDOUT,
                              errno.ECONNRESET, errno.EIO))

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError("{} field set differs".format(label))


def regular_file(path, label):
    if path.is_symlink() or not path.is_file():
        raise ValueError("{} is not a regular file: {}".format(label, path))


def json_file(path):
    regular_file(path, "JSON input")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("invalid JSON {}: {}".format(path, error)) from error


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def analyzer_module():
    return load_module("hadronization_analyzer_contract",
                       ROOT / "pipeline/analyze/run.py")


def runtime_module():
    return load_module("hadronization_runtime_contract",
                       ROOT / "pipeline/generate/runtime.py")


def reject_symlink_components(path, label):
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if os.path.lexists(str(current)) and current.is_symlink():
            raise ValueError("{} has a symlink component: {}".format(label, current))


def safe_child(parent, child, label, must_exist=False):
    reject_symlink_components(parent, label + " root")
    reject_symlink_components(child, label)
    parent = parent.resolve(strict=parent.exists())
    child = child.resolve(strict=must_exist)
    try:
        child.relative_to(parent)
    except ValueError as error:
        raise ValueError("{} is outside declared root".format(label)) from error
    return child


def fsync_file(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def fsync_directory(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextmanager
def build_lock(path):
    """Serialize one reproducible cache key across cooperating processes."""
    descriptor = os.open(str(path), os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def cached_build(binary, receipt, identity):
    if not binary.is_file() or not receipt.is_file():
        return None
    try:
        current = json_file(receipt)
    except ValueError:
        return None
    if (current.get("build_identity") == identity and
            current.get("binary_sha256") == sha_file(binary)):
        return current
    return None


def atomic_json(path, value, exclusive=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (canonical(value) + "\n").encode("ascii")
    with tempfile.NamedTemporaryFile(prefix="." + path.name + ".",
                                     dir=str(path.parent), delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        if exclusive:
            os.link(str(temporary), str(path))
            fsync_directory(path.parent)
        else:
            os.replace(str(temporary), str(path))
            fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def lower_sha(value, label):
    if (not isinstance(value, str) or len(value) != 64 or
            any(character not in "0123456789abcdef" for character in value)):
        raise ValueError("{} is not a lowercase SHA-256".format(label))


def build_analyzer_admission(analyze, work_root):
    runtime = analyze.runtime_contract.resolve(require_root=True)
    binary_root = work_root / "bin"
    before = {}
    if binary_root.is_dir():
        for path in binary_root.iterdir():
            if path.is_file() and not path.is_symlink():
                stat = path.stat()
                before[path.name] = (stat.st_ino, stat.st_mtime_ns,
                                     stat.st_size)
    analyzer, build = analyze.build_tool(
        runtime, binary_root, analyze.ANALYSIS_SOURCE, "analyze")
    stat = analyzer.stat()
    selected = (stat.st_ino, stat.st_mtime_ns, stat.st_size)
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    return analyzer, environment, build, {
        "build_tool_calls": 1,
        "compiler_processes": int(before.get(analyzer.name) != selected),
        "analyzer_processes_per_full_pass": 2,
    }


def command_tokens(command, argument, environment):
    completed = subprocess.run([command, argument], env=environment, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode or completed.stderr.strip():
        raise ValueError("ROOT configuration failed: {}".format(
            completed.stderr.strip() or completed.stdout.strip()))
    return shlex.split(completed.stdout.strip())
