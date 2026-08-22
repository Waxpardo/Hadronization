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
    env.update(HADRONIZATION_BASE=str(ROOT), DATASET_SELECTOR=selector)
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


def main() -> int:
    tests = [v for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"measurement target: {len(tests)} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
