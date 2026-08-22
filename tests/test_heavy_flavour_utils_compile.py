#!/usr/bin/env python3
"""Compile and execute the dependency-free producer utility contracts."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hadronization-hf-utils-") as tmp:
        executable = Path(tmp) / "test_heavy_flavour_utils"
        subprocess.run(
            [
                "c++",
                "-std=c++17",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Werror",
                str(ROOT / "tests/test_heavy_flavour_utils.cpp"),
                "-o",
                str(executable),
            ],
            cwd=ROOT,
            check=True,
        )
        subprocess.run([str(executable)], cwd=ROOT, check=True)
    print("heavy-flavour utility compile/run contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
