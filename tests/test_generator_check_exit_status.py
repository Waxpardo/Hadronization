#!/usr/bin/env python3
"""A generator's --check must be SEEN to fail, not merely fail.

THE DEFECT THIS CLOSES. `--check` returns non-zero correctly, but every place it
was read during this work read it through a pipe:

    python3 tools/apply_class_labels.py --check | tail -3   # $? is tail's

`$?` after a pipeline is the LAST command's status, so a failing check reported
success three separate times in three sessions. It is the E2 shape once more --
a check that cannot be observed to fail is not a check - and it is easy to
reintroduce, because the pipeline reads naturally.

This test runs each generator's --check the way a caller must: status captured
DIRECTLY from the process, never through a pipe. It asserts both directions --
clean tree exits 0, and a deliberately corrupted configuration exits non-zero -
so it fails if the generator ever stops detecting drift.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GENERATORS = [
    ("apply_class_labels", ROOT / "tools" / "apply_class_labels.py"),
    ("make_variant_configs", ROOT / "tools" / "make_variant_configs.py"),
]

# One configuration each generator owns, for the hand-edit mutation. Ownership
# is declared in the file itself by `label_owner`; these are the files that
# declaration resolves to.
OWNED_CONFIG = {
    "apply_class_labels":
        "configuration_multiplicity_HF_RUN3_V1_MONASH_THnSparse_complete_root.json",
    "make_variant_configs":
        "configuration_multiplicity_HF_RUN3_V1_VEXTREMES.json",
}


def check_status(generator: Path, cwd: Path) -> int:
    """Status taken straight from the process. No pipe, no shell."""
    completed = subprocess.run(
        [sys.executable, str(generator), "--check"],
        cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    return completed.returncode


def piped_status(generator: Path, cwd: Path) -> int:
    """The WRONG way, kept here so the hazard is demonstrated and not just described."""
    completed = subprocess.run(
        f"{sys.executable} {generator} --check | tail -1",
        cwd=str(cwd), shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    return completed.returncode


def main() -> int:
    failures: list[str] = []

    # 1. BOTH generators own their own configurations and must be clean in the
    #    committed tree. `apply_class_labels` was expected non-zero until the
    #    E9 labels were corrected; that correction has landed, so the waiver is
    #    gone and the tree state is pinned alongside the detection.
    for name, generator in GENERATORS:
        rc = check_status(generator, ROOT)
        if rc != 0:
            failures.append(f"{name} --check exits {rc} in the committed tree; "
                            f"expected 0")

    # 2. Detection, in a sandbox, for each generator in turn.
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp) / "repo"
        subprocess.run(["cp", "-R", str(ROOT), str(sandbox)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for name, real in GENERATORS:
            gen = sandbox / real.relative_to(ROOT)
            target = sandbox / "plotting" / OWNED_CONFIG[name]
            failures.extend(
                rewrites_only_labels(name, gen, sandbox, target))
            failures.extend(mutate_and_check(name, gen, sandbox, target))

    if failures:
        for line in failures:
            print("FAIL: " + line)
        return 1
    print("check statuses: both generators clean in the committed tree; a "
          "hand-edited label detected directly (non-zero) by each and MASKED "
          "through a pipe (0) - capture directly")
    return 0


CLASS_LABEL = re.compile(
    r'("display_name"\s*:\s*")(?P<value>[^"]*?\d[^"]*%)(")')


def corrupt_text(text: str) -> str | None:
    """Hand-edit the first class label IN THE RAW TEXT, preserving formatting.

    A JSON round-trip would reformat the file, and this test has to be able to
    tell a reformat from a label edit. So the corruption is a substitution
    inside one line and nothing else moves.
    """
    match = CLASS_LABEL.search(text)
    if not match:
        return None
    return text[:match.start()] + match.group(1) + "99.9-99.9%" + \
        match.group(3) + text[match.end():]


def rewrites_only_labels(name: str, gen: Path, sandbox: Path,
                         target: Path) -> list[str]:
    """Correcting a label must restore the file BYTE FOR BYTE, not reformat it.

    THE DEFECT THIS CLOSES. `apply_class_labels.py` wrote every file it touched
    with `indent=4`, while the configurations it owns are committed at 1, 2 and
    4 spaces. Correcting twenty-four labels therefore rewrote 4456 lines,
    changed every configuration's sha256 -- which the multiplicity boundary
    receipts record -- and made `make_hf_run3_v1_three_tune_config.py --check`
    fail, because that generator writes the same file at `indent=1`.

    NEITHER `--check` NOR A CLEAN-TREE RUN CATCHES THIS. The labels were right,
    so `--check` exits 0; and the generator writes only when it finds drift, so
    on a clean tree it never opens the file for writing at all. The defect lives
    exactly in the write path, and only a run that HAS something to correct
    reaches it.

    So: hand-edit one label, run the generator for real, and require the file to
    come back identical to what it was. Any reformatting shows up as a
    difference even though every label is once again correct.
    """
    original = target.read_bytes()
    damaged = corrupt_text(original.decode())
    if damaged is None:
        return [f"{name}: could not find a class label to corrupt"]
    target.write_text(damaged)

    subprocess.run([sys.executable, str(gen)], cwd=str(sandbox),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    restored = target.read_bytes()
    target.write_bytes(original)

    if restored == original:
        return []
    if json.loads(restored) == json.loads(original):
        return [f"{name}: the generator restored every label but REFORMATTED "
                f"{target.name} ({len(original)} bytes in, {len(restored)} "
                f"out); a label correction must move labels and nothing else"]
    return [f"{name}: the generator did not restore {target.name}"]


def mutate_and_check(name: str, gen: Path, sandbox: Path,
                     target: Path) -> list[str]:
    """Hand-edit one label the generator owns; its --check must go non-zero."""
    failures: list[str] = []
    if check_status(gen, sandbox) != 0:
        failures.append(
            f"{name}: sandbox is not clean before the corruption, so the "
            f"corruption test below would be meaningless")
    original = target.read_text()

    damaged = corrupt_text(original)
    if damaged is None:
        failures.append(f"{name}: could not find a class label to corrupt")
        return failures

    target.write_text(damaged)
    direct = check_status(gen, sandbox)
    if direct == 0:
        failures.append(
            f"{name}: --check exited 0 on a hand-edited label; a failing check "
            f"that reports success is the whole defect")

    # THE POINT. The same failing check, read through a pipe, reports success --
    # so any caller that pipes is blind to it.
    piped = piped_status(gen, sandbox)
    if piped == direct:
        failures.append(
            f"{name}: expected the piped status ({piped}) to differ from the "
            f"direct one ({direct}); if they now agree this test no longer "
            f"demonstrates the hazard it exists for")
    elif piped != 0:
        failures.append(
            f"{name}: piped status was {piped}, expected 0 (tail's success)")

    target.write_text(original)
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
