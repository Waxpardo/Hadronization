#!/usr/bin/env python3
"""Compile and exercise the schema-keyed pair-object selection.

The contract is exact-match in both directions, so adding an object to a newer
schema is only safe if the object set is chosen by the schema the file itself
declares. The C++ harness covers the three cases the design was required to
satisfy -- a correct v2 directory passes, a v2 directory carrying the v3 object
fails, a v3 directory missing it fails -- plus the fail-closed parse.

It is a C++ test rather than a Python one on purpose: the header is what the
consumers actually compile against, and a Python re-reading of the JSON would
test the contract against itself rather than against the artifact in use.
"""

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
        executable = Path(temporary) / "test_pair_object_schema_versions"
        subprocess.run(
            [
                compiler,
                "-std=c++17",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(ROOT / "tests/test_pair_object_schema_versions.cpp"),
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
        raise AssertionError(
            f"pair-object schema-version test failed:\n{output}")
    # The counts are asserted here as well as in the harness so that a harness
    # that silently stopped checking anything cannot report success.
    if "v2_content=6" not in output or "v3_content=7" not in output:
        raise AssertionError(
            "expected v2 to carry six content objects and v3 seven; the "
            f"harness reported:\n{output}")
    print("pair-object schema-version contract test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
