#!/usr/bin/env python3
"""Instantiate the configured PYTHIA and require its runtime XML data."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    pythia = os.environ.get("PYTHIA8")
    compiler = shutil.which("g++") or shutil.which("c++")
    configured = shutil.which("pythia8-config")
    if not pythia and configured:
        raise RuntimeError(
            "pythia8-config is present but PYTHIA8 is unset; the pinned "
            "runtime root is not reproducibly bound"
        )
    if not pythia or compiler is None:
        print("PYTHIA runtime test skipped: configured PYTHIA8/compiler absent")
        return 0
    pythia_root = Path(pythia).resolve()
    data = os.environ.get("PYTHIA8DATA")
    if not data:
        raise RuntimeError("PYTHIA8DATA is unset in a configured PYTHIA environment")
    index = Path(data).resolve() / "Index.xml"
    if not index.is_file():
        raise RuntimeError(f"PYTHIA8DATA has no Index.xml: {index}")

    with tempfile.TemporaryDirectory() as temporary:
        executable = Path(temporary) / "test_pythia_runtime"
        build = subprocess.run(
            [
                compiler,
                "-std=c++17",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Wconversion",
                "-Wshadow",
                "-Werror",
                "-isystem",
                str(pythia_root / "include"),
                str(ROOT / "tests/test_pythia_runtime.cpp"),
                "-L",
                str(pythia_root / "lib"),
                "-lpythia8",
                "-o",
                str(executable),
            ],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if build.returncode != 0 or "warning:" in build.stdout.lower():
            raise AssertionError(f"PYTHIA runtime test build failed:\n{build.stdout}")
        run = subprocess.run(
            [str(executable)],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    if run.returncode != 0 or "PYTHIA_RUNTIME_TEST valid=true" not in run.stdout:
        raise AssertionError(f"PYTHIA runtime initialization failed:\n{run.stdout}")
    print(run.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
