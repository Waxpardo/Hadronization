#!/usr/bin/env python3
"""The measurement target, and the three things it must refuse.

WHY IT EXISTS. The publication gate admits `canonical` and `canonical_candidate`
only, which is right: a paper figure must not be drawn from unsealed data. A
systematic variation is honestly neither, so the row that describes the dataset
truthfully was the row the publication plotter refused. The resolution separates
measurement from publication instead of weakening either.

Every assertion below is a MUTATION: it changes one thing and requires the
refusal to appear. A gate never seen to fail is not known to be a gate.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Same directory as this driver, so no path setup is needed.
from sandbox_tree import tracked_names

ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "plotting" / "run_paper_plots.sh"
WRAPPER = ROOT / "tools" / "render_measurement.sh"
RECEIPT_WRITER = ROOT / "tools" / "write_measurement_receipt.py"
UNIFIED_CLI = ROOT / "hadronization"


# The gate reads the dataset STATUS from the selector, not from the
# environment -- an env var cannot spoof it, which is the right design and is
# why these tests drive real selector files.
SEL_CANONICAL = "config/dataset_selector_hf_run3_v1.json"
SEL_VARIATION = "config/dataset_selector_hf_sys_mur_up.json"
SEL_LEGACY = "config/dataset_selector.json"


def _run(target: str, selector: str, env_extra: dict | None = None,
         extra_targets: list[str] | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(
        HADRONIZATION_BASE=str(ROOT),
        DATASET_SELECTOR=selector,
        HADRONIZATION_REQUEST_PREFLIGHT_ONLY="1",
    )
    env.setdefault("HADRONIZATION_DATA_ROOT", "/tmp/hadronization-test-data")
    env.pop("HADRONIZATION_MEASUREMENT_ROOT", None)
    env.update(env_extra or {})
    return subprocess.run(["bash", str(DRIVER), target, *(extra_targets or [])],
                          env=env, text=True, capture_output=True, check=False)


def test_a_publication_target_still_refuses_a_variation() -> None:
    """THE MUTATION THAT MATTERS. The publication gate must not have moved."""
    r = _run("thnsparse-complete-root", SEL_VARIATION)
    assert r.returncode != 0, r.stdout
    assert "canonical plotting/validation is fail-closed" in r.stderr, r.stderr


def test_the_publication_gate_predicate_is_unchanged() -> None:
    """Require the publication gate to retain its two allowed statuses."""
    text = DRIVER.read_text()
    assert ('[[ "${HADRONIZATION_DATASET_STATUS:-}" != "canonical" ]] &&\n'
            '   [[ "${HADRONIZATION_DATASET_STATUS:-}" != "canonical_candidate" ]]'
            ) in text, "the publication gate predicate was modified"


def test_the_measurement_target_accepts_a_variation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        r = _run("measure-balancing", SEL_VARIATION,
                 {"HADRONIZATION_MEASUREMENT_ROOT": f"{tmp}/measurements"})
    assert "MEASUREMENT_TARGET purpose=measurement" in r.stdout, r.stdout + r.stderr
    assert "REQUEST_PREFLIGHT_ONLY status=PASS" in r.stdout, r.stdout + r.stderr
    assert "fail-closed" not in r.stderr, r.stderr


def test_the_measurement_target_refuses_an_unknown_status() -> None:
    # Name the legacy row so the resolver can test and refuse its status.
    with tempfile.TemporaryDirectory() as tmp:
        r = _run("measure-balancing", SEL_LEGACY,
                 {"HADRONIZATION_MEASUREMENT_ROOT": f"{tmp}/m",
                  "HADRONIZATION_DATASET": "legacy_21_06_2026"})
    assert r.returncode != 0, r.stdout
    assert "accepts canonical, canonical_candidate" in r.stderr, r.stderr


def test_a_measurement_may_not_land_in_the_publication_tree() -> None:
    """Require measurement output to remain outside the publication tree."""
    r = _run("measure-balancing", SEL_VARIATION,
             {"HADRONIZATION_MEASUREMENT_ROOT": "plotting/Plots/Sneaky"})
    assert r.returncode != 0, r.stdout
    assert "inside the publication" in r.stderr, r.stderr


def test_the_measurement_root_has_no_default() -> None:
    r = _run("measure-balancing", SEL_VARIATION)
    assert r.returncode != 0, r.stdout
    assert "required and has no default" in r.stderr, r.stderr


def test_measurement_and_publication_cannot_share_a_run() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        r = _run("measure-balancing", SEL_CANONICAL,
                 {"HADRONIZATION_MEASUREMENT_ROOT": f"{tmp}/m"})
        assert "MEASUREMENT_TARGET" in r.stdout, r.stdout + r.stderr
        both = _run("measure-balancing", SEL_CANONICAL,
                    {"HADRONIZATION_MEASUREMENT_ROOT": f"{tmp}/m"},
                    extra_targets=["audit-subsamples"])
    assert both.returncode != 0, both.stdout
    assert "cannot run together" in both.stderr, both.stderr


def test_the_wrapper_captures_the_render_status_with_nothing_in_between() -> None:
    """The rc lesson, asserted on the source rather than trusted.

    Three times in this project a zero exit status has been read from the wrong
    command. Here the assignment must be the statement IMMEDIATELY after the
    render.
    """
    lines = [l.strip() for l in WRAPPER.read_text().splitlines()]
    render = next(i for i, l in enumerate(lines)
                  if l.startswith("bash \"$BASE/plotting/run_paper_plots.sh\""))
    assert lines[render + 1].startswith("RC=$?"), (
        "a statement was inserted between the render and its status capture: "
        f"{lines[render + 1]!r}")


def test_the_receipt_declares_its_purpose() -> None:
    text = RECEIPT_WRITER.read_text()
    assert '"purpose": "measurement"' in text, text[:200]
    assert '"publication_eligible": False' in text
    assert '"render_exit_status": args.render_status' in text


def test_the_wrapper_enforces_the_receipt_status() -> None:
    text = WRAPPER.read_text()
    assert 'RECEIPT_RC=$?' in text
    assert 'exit "$RECEIPT_RC"' in text


def test_the_unified_cli_routes_measurements_through_the_wrapper() -> None:
    text = UNIFIED_CLI.read_text()
    assert '[[ "$#" -eq 1 && "$1" == "measure-balancing" ]]' in text
    assert '"${project_base}/tools/render_measurement.sh"' in text
    assert "HADRONIZATION_MEASUREMENT_ROOT_EXACT=1" in text
    assert "HADRONIZATION_MEASUREMENT_CONFIG" in text
    assert 'MEASUREMENT_WIDEN_AXES="${MEASUREMENT_WIDEN_AXES:-1}"' in text


def test_request_gate_tests_never_start_root() -> None:
    text = DRIVER.read_text()
    preflight = text.index("REQUEST_PREFLIGHT_ONLY status=PASS")
    root_requirement = text.index("if ! command -v root")
    assert preflight < root_requirement


def test_the_unified_cli_uses_a_commit_scoped_exact_measurement_root() -> None:
    cli = UNIFIED_CLI.read_text()
    wrapper = WRAPPER.read_text()
    expected = (
        '"${HADRONIZATION_RESULTS_ROOT}/${HADRONIZATION_CAMPAIGN}/'
        '${commit}/measurements/${HADRONIZATION_DATASET}"'
    )
    assert expected in cli
    assert (
        'if [ "${HADRONIZATION_MEASUREMENT_ROOT_EXACT:-0}" = "1" ]; then'
        in wrapper
    )
    assert 'CAMPAIGN_ROOT="$ROOT"' in wrapper


# --- the measurement configuration the CLI chooses -------------------------
#
# THE DEFECT THESE CLOSE. `measure-balancing` defaulted to
# plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json,
# which draws two canvases. The HF_RUN3_V1 dataset row carries no
# measurement_config, so HADRONIZATION_MEASUREMENT_CONFIG arrived empty and a
# control render of the nominal took that default silently. It produced a FAIL
# 12/132 receipt against a 132-row envelope: a configuration mismatch that read
# as a physics disagreement.
#
# The CLI is driven in a sandbox checkout. Every entry is a symlink to this
# checkout except two files: tools/render_measurement.sh reports the arguments
# the CLI chose and renders nothing, and setupEnv.sh stands in for the site and
# dependency planes, which this choice does not read. Both keep the case fast
# and identical on every host.
CAMPAIGN = "HF_RUN3_V1"
DATASET_KEY = "hf_run3_v1_candidate"
DERIVED_CONFIG = (
    f"plotting/configuration_multiplicity_{CAMPAIGN}"
    "_THREETUNE_THnSparse_complete_root.json")
REDUCED_CONFIG = (
    "plotting/configuration_multiplicity_reduced_JUNCTIONS"
    "_THnSparse_complete_root.json")

_STUB_SETUP_ENV = """# Sandbox stand-in for setupEnv.sh.
export HADRONIZATION_SITE=local
export HADRONIZATION_DATA_ROOT="${HADRONIZATION_DATA_ROOT:?}"
export HADRONIZATION_RESULTS_ROOT="${HADRONIZATION_DATA_ROOT}/project/results"
export HADRONIZATION_ANALYSIS_ROOT="${HADRONIZATION_DATA_ROOT}/analysis"
export HADRONIZATION_MERGED_ROOT="${HADRONIZATION_DATA_ROOT}/merged"
export HADRONIZATION_SYSTEMATICS_ROOT="${HADRONIZATION_DATA_ROOT}/systematics"
export HF_PRODUCTION_ROOT="${HADRONIZATION_DATA_ROOT}/production"
"""

_STUB_RENDER = """#!/bin/bash
# Sandbox stand-in for tools/render_measurement.sh. Report what the CLI chose.
printf 'RENDER_CAMPAIGN=%s\\n' "$1"
printf 'RENDER_CONFIG=%s\\n' "$2"
exit 0
"""


def _cli_sandbox(tmp: str, cli_text: str | None = None,
                 drop_config: str | None = None) -> Path:
    """Build a checkout that differs from this one only where it must.

    tracked_names, never iterdir: `tests/sandbox_tree.py` states the rule and
    the incident behind it. Before that rule this helper mirrored the resolved
    `plotting/Plots` itself, so a sandbox run could reach the real plot plane.
    """
    base = Path(tmp) / "checkout"
    base.mkdir()
    replaced = {"tools", "plotting", "setupEnv.sh", "hadronization"}
    for entry in sorted(tracked_names(ROOT)):
        if entry not in replaced:
            (base / entry).symlink_to(ROOT / entry)
    for name in ("tools", "plotting"):
        (base / name).mkdir()
        for entry in sorted(tracked_names(ROOT, name)):
            if entry in {"render_measurement.sh", drop_config}:
                continue
            (base / name / entry).symlink_to(ROOT / name / entry)
    stub = base / "tools/render_measurement.sh"
    stub.write_text(_STUB_RENDER)
    stub.chmod(0o755)
    (base / "setupEnv.sh").write_text(_STUB_SETUP_ENV)
    cli = base / "hadronization"
    cli.write_text(cli_text if cli_text is not None
                   else UNIFIED_CLI.read_text())
    cli.chmod(0o755)
    # prepare_measurement_output_plane reads the commit, so the sandbox needs a
    # repository of its own. Never the real one: a test must not be able to
    # write into it.
    for command in (["init", "-q"],
                    ["-c", "user.name=t", "-c", "user.email=t@t", "commit",
                     "-q", "--allow-empty", "-m", "sandbox"]):
        subprocess.run(["git", "-C", str(base), *command], check=True,
                       capture_output=True)
    return base


def _run_cli(base: Path,
             env_extra: dict | None = None) -> subprocess.CompletedProcess:
    data = base.parent / "data"
    data.mkdir(exist_ok=True)
    env = dict(os.environ)
    env.update(
        HADRONIZATION_DATA_ROOT=str(data),
        HADRONIZATION_DATASET_SELECTOR=str(ROOT / SEL_CANONICAL),
    )
    for name in ("THNSPARSE_COMPLETE_ROOT_CONFIG",
                 "HADRONIZATION_MEASUREMENT_CONFIG",
                 "HADRONIZATION_MEASUREMENT_ROOT"):
        env.pop(name, None)
    env.update(env_extra or {})
    return subprocess.run(
        ["bash", str(base / "hadronization"), "plot", DATASET_KEY,
         "measure-balancing"],
        env=env, text=True, capture_output=True)


def test_the_sandbox_mirrors_only_what_the_tree_tracks() -> None:
    """The sandbox holds the tracked set, and the repository git init creates.

    Both sides come from the tree, so this states a property of the sandbox on
    every host. It fails on any host that carries untracked state, which is
    when the inheritance can change what the cases below measure.
    """
    with tempfile.TemporaryDirectory() as tmp:
        base = _cli_sandbox(tmp)
        top = {entry.name for entry in base.iterdir()}
        assert top == tracked_names(ROOT) | {".git"}, \
            sorted(top ^ (tracked_names(ROOT) | {".git"}))
        for name in ("tools", "plotting"):
            mirrored = {entry.name for entry in (base / name).iterdir()}
            assert mirrored == tracked_names(ROOT, name), \
                (name, sorted(mirrored ^ tracked_names(ROOT, name)))


def _chosen_config(result: subprocess.CompletedProcess) -> str:
    for line in result.stdout.splitlines():
        if line.startswith("RENDER_CONFIG="):
            return line.split("=", 1)[1]
    return ""


def test_the_measurement_configuration_is_derived_from_the_campaign() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        got = _run_cli(_cli_sandbox(tmp))
    assert got.returncode == 0, got.stdout + got.stderr
    assert _chosen_config(got) == DERIVED_CONFIG, got.stdout + got.stderr


def test_a_missing_derived_configuration_refuses_by_name() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = _cli_sandbox(tmp, drop_config=Path(DERIVED_CONFIG).name)
        got = _run_cli(base)
    assert got.returncode != 0, got.stdout
    assert _chosen_config(got) == "", "the render ran on a refusal"
    # Name the file that is missing and the variable that answers it. A refusal
    # the reader cannot act on costs the same as no refusal.
    assert f"derived: {DERIVED_CONFIG}" in got.stderr, got.stderr
    assert "THNSPARSE_COMPLETE_ROOT_CONFIG" in got.stderr, got.stderr
    assert REDUCED_CONFIG not in got.stderr, "a fallback was offered"


def test_an_explicitly_named_configuration_is_used() -> None:
    """The reduced configuration is reachable, but only by naming it."""
    with tempfile.TemporaryDirectory() as tmp:
        got = _run_cli(_cli_sandbox(tmp),
                       {"THNSPARSE_COMPLETE_ROOT_CONFIG": REDUCED_CONFIG})
    assert got.returncode == 0, got.stdout + got.stderr
    assert _chosen_config(got) == REDUCED_CONFIG, got.stdout + got.stderr


def test_the_cli_carries_no_measurement_configuration_default() -> None:
    """Read the source too: the sandbox cases cannot see a second default."""
    text = UNIFIED_CLI.read_text()
    choice = text[text.index("measurement_config="):]
    choice = choice[:choice.index("measurement_log=")]
    assert REDUCED_CONFIG not in choice, choice


def main() -> int:
    tests = [v for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"measurement target: {len(tests)} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
