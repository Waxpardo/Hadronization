#!/usr/bin/env python3
"""Compile and exercise the shared associate-origin category contract."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    compiler = shutil.which("c++")
    if compiler is None:
        raise RuntimeError("a C++17 compiler is required")
    with tempfile.TemporaryDirectory() as temporary:
        executable = Path(temporary) / "test_associate_origin_category"
        subprocess.run(
            [
                compiler,
                "-std=c++17",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(ROOT / "tests/test_associate_origin_category.cpp"),
                "-o",
                str(executable),
            ],
            cwd=ROOT,
            check=True,
        )
        result = subprocess.run(
            [str(executable)],
            check=False,
            text=True,
            capture_output=True,
        )
    output = result.stdout + result.stderr
    if result.returncode != 0 or "errors=0" not in output:
        raise AssertionError(f"associate-origin category test failed:\n{output}")
    print("associate-origin category contract test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
