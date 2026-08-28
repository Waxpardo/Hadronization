#!/usr/bin/env python3
"""What a test sandbox may mirror: the tracked tree, and nothing else.

THE DEFECT THIS CLOSES. The pinned check on the cluster reported three
failures in `test_cli_surface.py`, and every observed list named
`plotting/Plots.HF_RUN3_V1-4d309e9f99e4.superseded-20260827`. That entry is
the pointer `./hadronization plot-slot` moves aside, and the deploy is
required to keep it. The sandbox helper mirrored every entry of the real
`plotting/` and dropped only `Plots`, so the `Plots.*` siblings rode into the
sandbox and appeared in the assertions. The code under test was correct on
both hosts. The two hosts differed only in untracked state.

THE RULE. A sandbox mirrors what the tree tracks. Nothing else. `git ls-files`
is the authority on that, as it already is for the tracked-directory audit in
`test_no_source_directory_is_ignored.py` and for the tracked-output check in
`test_cli_surface.py`.

WHY THE TRACKED SET AND NOT A NAME PATTERN. Measured on this checkout on
2026-08-28, the helpers inherited more than the superseded pointer:
`.DS_Store`, `.local-data` (a symlink to the real data plane), nine ROOT
build products in `plotting/`, `tools/__pycache__`, and the resolved
`plotting/Plots` itself. A `Plots*` rule excludes one of the twelve names the
helper in `test_cli_surface.py` inherited and leaves eleven. The tracked set
excludes all twelve, and excludes the next one nobody has met yet.

WHAT A CASE DOES INSTEAD. A case that needs a file the tree does not track
writes that file into its own sandbox. The failure mode is loud: the file is
absent and the case fails. It is never a case that passes for a reason that
belongs to one host.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def tracked_files(root: Path, relative: str = ".") -> list[str]:
    """The paths git tracks under `relative`, stated relative to it."""
    listed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", relative],
        capture_output=True, text=True, check=True).stdout
    prefix = "" if relative in ("", ".") else relative.rstrip("/") + "/"
    paths = [path[len(prefix):] for path in listed.split("\0") if path]
    if not paths:
        # An empty allowlist builds an empty sandbox, and an empty sandbox
        # certifies nothing while every case in the file still reports PASS.
        raise AssertionError(
            f"git tracks nothing under {root}/{relative}; a sandbox built "
            f"from an empty allowlist would certify nothing")
    return sorted(paths)


def tracked_names(root: Path, relative: str = ".") -> set[str]:
    """The names git tracks directly inside `relative`."""
    return {path.split("/")[0] for path in tracked_files(root, relative)}
