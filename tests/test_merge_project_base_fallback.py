"""`merge_root_files.sh` must resolve its project base without the environment.

A run record held in the internal repository shows how close this came to
stopping a merge: *"`/proc/108654/environ` confirms `HADRONIZATION_BASE` **is**
exported. That, and only that, is what keeps the `merge_root_files.sh:27`
`project_base` fallback from killing this run."*

The `:27` in that quotation is the run record's own, and stays: the quote is
verbatim. The line has since moved, and a line number is what went stale here
(ledger DA1-B059), so the anchor below is the assignment TEXT rather than a
number -- `project_base="${HADRONIZATION_BASE:-$(cd "${script_dir}/.." &&
pwd)}"`, which `test_the_fallback_line_is_present_and_uses_the_parent` matches
exactly. It sat at :33 when this note was written on 2026-08-30.

The fallback read `${HADRONIZATION_BASE:-${script_dir}}`. The script lives in
`merging/`, so `${script_dir}` is `merging/`, and the next line sources
`${project_base}/setupEnv.sh` -- `merging/setupEnv.sh`, which does not exist.
Every merge that has ever run survived because the variable happened to be
exported. The fallback was never exercised, and it was wrong.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MERGE = ROOT / "merging" / "merge_root_files.sh"


def test_the_fallback_resolves_to_the_repository_root() -> None:
    """Run the resolution in isolation, with HADRONIZATION_BASE unset."""
    script = (
        'script_dir="%s"\n'
        'project_base="${HADRONIZATION_BASE:-$(cd "${script_dir}/.." && pwd)}"\n'
        'echo "${project_base%%/}"\n' % (ROOT / "merging")
    )
    out = subprocess.run(
        ["bash", "-c", script], text=True, capture_output=True,
        env={"PATH": "/usr/bin:/bin"}, check=True,
    ).stdout.strip()
    assert out == str(ROOT), f"fallback resolved to {out}, expected {ROOT}"
    assert (Path(out) / "setupEnv.sh").is_file(), \
        f"{out}/setupEnv.sh does not exist, so the source would fail"


def test_the_script_does_not_fall_back_to_its_own_directory() -> None:
    """The mutation guard. Restoring `:-${script_dir}` must fail this test."""
    text = MERGE.read_text()
    bad = re.search(
        r'project_base="\$\{HADRONIZATION_BASE:-\$\{script_dir\}\}"', text)
    assert bad is None, (
        "merge_root_files.sh fell back to its own directory again; "
        "merging/setupEnv.sh does not exist"
    )


def test_the_fallback_line_is_present_and_uses_the_parent() -> None:
    text = MERGE.read_text()
    assert 'project_base="${HADRONIZATION_BASE:-$(cd "${script_dir}/.." && pwd)}"' \
        in text, "the corrected fallback is not in merge_root_files.sh"


def test_setup_env_is_sourced_from_the_resolved_base() -> None:
    """The reason the fallback matters at all."""
    text = MERGE.read_text()
    assert 'source "${project_base}/setupEnv.sh"' in text, \
        "merge_root_files.sh no longer sources setupEnv.sh from project_base"


def main() -> int:
    test_the_fallback_resolves_to_the_repository_root()
    test_the_script_does_not_fall_back_to_its_own_directory()
    test_the_fallback_line_is_present_and_uses_the_parent()
    test_setup_env_is_sourced_from_the_resolved_base()
    print("merge project_base fallback tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
