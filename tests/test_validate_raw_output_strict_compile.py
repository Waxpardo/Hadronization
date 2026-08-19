#!/usr/bin/env python3
"""Compile the raw-output validator with the publication warning contract."""

from __future__ import annotations

import shlex
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "Validation" / "ValidateRawOutput.C"
# No -std= here. The standard comes from `root-config --cflags` below, so the
# validator is warning-checked under the same standard it is actually compiled
# with everywhere else. Pinning -std=c++17 here while stripping ROOT's own flag
# made this test fail on any C++20 ROOT build: RConfigure.h emits
#   "The C++ standard in this build does not match ROOT configuration (202002L)"
# and -Werror promoted that to an error, so the test failed on the ROOT header
# rather than on anything in ValidateRawOutput.C. The zero-warning contract is
# unchanged -- only the standard it is enforced under.
STRICT_FLAGS = (
    "-Wall",
    "-Wextra",
    "-Wpedantic",
    "-Wconversion",
    "-Wshadow",
    "-Werror",
)


def root_cflags_as_system_includes(root_config: str) -> list[str]:
    raw_flags = subprocess.check_output(
        [root_config, "--cflags"], text=True
    ).strip()
    normalized: list[str] = []
    for flag in shlex.split(raw_flags):
        if flag.startswith("-I") and len(flag) > 2:
            normalized.extend(("-isystem", flag[2:]))
        else:
            # ROOT's -std= is kept deliberately; see STRICT_FLAGS.
            normalized.append(flag)
    return normalized


def main() -> int:
    root_config = shutil.which("root-config")
    if root_config is None:
        print("strict raw-validator compile test skipped: ROOT headers unavailable")
        return 0

    configured_cxx = subprocess.check_output(
        [root_config, "--cxx"], text=True
    ).strip()
    compiler_command = shlex.split(configured_cxx)
    if not compiler_command or shutil.which(compiler_command[0]) is None:
        raise AssertionError(
            f"ROOT-configured C++ compiler is unavailable: {configured_cxx!r}"
        )

    command = [
        *compiler_command,
        *root_cflags_as_system_includes(root_config),
        *STRICT_FLAGS,
        "-fsyntax-only",
        str(VALIDATOR),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "ValidateRawOutput.C violates the strict publication warning "
            f"contract:\n{completed.stdout}"
        )
    print("strict raw-validator compile test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
