#!/usr/bin/env python3
"""The systematics seam on ./hadronization: two gates and one guarantee.

THE GUARANTEE FIRST. `plot DATASET_KEY [TARGET ...]` must behave exactly as it
did before the seam existed. Systematics are OFF by default, and every
accepted output was produced that way. `test_plot_without_the_flag_never_reads_
a_systematics_path` proves it the only way worth proving: it runs the same
command against two result trees that differ ONLY in whether a systematics
envelope exists, makes the envelope unreadable in the tree that has one, and
requires the two transcripts to be identical. A missing envelope must be
irrelevant, and an unreadable one must be equally irrelevant.

THE TWO GATES. `systematics` answers its request before any extraction runs;
`plot --systematics` validates the envelope before any renderer starts. Both
are exercised through HADRONIZATION_REQUEST_PREFLIGHT_ONLY, which is what
makes them testable on a host that holds no campaign data.

Every refusal below is a MUTATION of a fixture that otherwise passes, and each
must name the field it refused on.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "hadronization"
ASSERT_TOOL = ROOT / "tools" / "assert_systematics_envelope.py"
REQUEST_TOOL = ROOT / "tools" / "systematics_request.py"
CHAIN = ROOT / "extraction" / "pipeline" / "systematics_chain.sh"
NOMINAL = "hf_run3_v1_candidate"
VARIATION = "hf_sys_mur_up_variation"


def cli(*args: str, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["HADRONIZATION_REQUEST_PREFLIGHT_ONLY"] = "1"
    env.pop("HADRONIZATION_DATASET", None)
    env.update(env_extra or {})
    return subprocess.run(["bash", str(CLI), *args], cwd=str(ROOT), env=env,
                          text=True, capture_output=True, check=False)


def assert_tool(envelope: Path, plane: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ASSERT_TOOL), "--envelope", str(envelope),
         "--nominal-plot-plane", str(plane)],
        text=True, capture_output=True, check=False)


def short_commit() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--short=12", "HEAD"],
        text=True, capture_output=True, check=True).stdout.strip()


def fixture(tmp: Path, *, status: str = "COMPLETE", schema: str | None = None,
            boundary_sha: str | None = None, rows: list | None = None,
            commit: str = "aaaaaaaaaaaa") -> tuple[Path, Path]:
    """(envelope path, nominal plotting plane) that validates by default."""
    plane = tmp / "results" / "HF_RUN3_V1" / commit / "plotting"
    canvas = plane / "GlobalCanvas"
    canvas.mkdir(parents=True, exist_ok=True)
    receipt = canvas / "multiplicity_boundary_receipt_v2.json"
    receipt.write_text(json.dumps(
        {"schema": "hadronization_multiplicity_boundary_receipt_v2",
         "completion_status": "PASS"}))
    real_sha = hashlib.sha256(receipt.read_bytes()).hexdigest()
    envelope = tmp / "systematics_envelope.json"
    envelope.write_text(json.dumps({
        "schema": schema or "hadronization_systematics_envelope_v1",
        "status": status,
        "missing": [] if status == "COMPLETE" else ["HF_SYS_PTHAT_4: no PASS receipt"],
        "method": {"d2_quadrature": "", "a1_max_rule": "", "a2_s6_excluded": ""},
        "sources": [],
        "rows": [{"class": "c1", "combined_percent": 1.0}] if rows is None else rows,
        "provenance": {
            "nominal_boundary_receipt_sha256": boundary_sha or real_sha},
    }))
    return envelope, plane


# ---- the guarantee --------------------------------------------------------

def test_plot_without_the_flag_never_reads_a_systematics_path() -> None:
    """Two result trees, differing only in a systematics envelope. Identical."""
    transcripts = []
    for with_envelope in (False, True):
        with tempfile.TemporaryDirectory() as tmp:
            results = Path(tmp) / "results"
            (results / "HF_RUN3_V1" / "aaaaaaaaaaaa" / "plotting").mkdir(
                parents=True)
            if with_envelope:
                systematics = results / "HF_RUN3_V1" / "aaaaaaaaaaaa" / "systematics"
                systematics.mkdir(parents=True)
                poisoned = systematics / "systematics_envelope.json"
                poisoned.write_text("THIS IS NOT JSON AND MUST NEVER BE READ")
                # Unreadable: any attempt to open it raises rather than
                # silently succeeding, so "no access" is enforced and not
                # merely hoped for.
                poisoned.chmod(0o000)
            result = cli("plot", NOMINAL,
                         env_extra={"HADRONIZATION_RESULTS_ROOT": str(results)})
            if with_envelope:
                poisoned.chmod(stat.S_IRUSR | stat.S_IWUSR)
            transcripts.append(
                (result.returncode,
                 result.stdout.replace(tmp, "TMP"),
                 result.stderr.replace(tmp, "TMP")))
    assert transcripts[0] == transcripts[1], (
        "plot without --systematics behaved differently when an envelope "
        f"existed: {transcripts[0]} vs {transcripts[1]}")
    assert "systematics" not in transcripts[0][1].lower()


def test_the_plot_arm_has_no_default_for_the_flag() -> None:
    """Fail-closed rule 1: no default, no discovery, no environment fallback."""
    text = CLI.read_text()
    arm = text[text.index("\n  plot)"):text.index("\n  *)")]
    assert 'systematics_envelope=""' in arm, "the flag must start empty"
    assert 'if [[ -n "${systematics_envelope}" ]]; then' in arm
    assert "HADRONIZATION_SYSTEMATICS_ENVELOPE:-" not in arm, (
        "an environment fallback would let an envelope arrive unnamed")
    assert "systematics_envelope=${" not in arm


def test_the_overlay_never_uses_the_nominal_plot_plane() -> None:
    text = CLI.read_text()
    arm = text[text.index("\n  plot)"):text.index("\n  *)")]
    start = arm.index('if [[ -n "${systematics_envelope}" ]]; then')
    # The branch ends at its own `fi`, four spaces deep. Nested blocks close
    # deeper, so this terminator cannot match one of them.
    guarded = arm[start:arm.index("\n    fi\n", start)]
    assert "prepare_plot_output_plane" not in guarded, (
        "the overlay branch must not prepare the nominal plotting plane")
    assert "prepare_systematics_plot_output_plane" in guarded
    assert "plotting-syst" in text


# ---- the systematics request gate -----------------------------------------

def test_systematics_preflight_passes_for_the_nominal_dataset() -> None:
    result = cli("systematics", NOMINAL)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SYSTEMATICS_PREFLIGHT_ONLY status=PASS" in result.stdout, result.stdout
    assert "extraction=false outputs_written=false" in result.stdout


def test_systematics_refuses_a_variation_as_its_nominal() -> None:
    result = cli("systematics", VARIATION)
    assert result.returncode != 0, result.stdout
    assert "an envelope attaches to a nominal render" in result.stderr, result.stderr


def test_systematics_refuses_more_than_one_dataset() -> None:
    result = cli("systematics", NOMINAL, "extra")
    assert result.returncode == 2, result.stdout + result.stderr


def test_the_envelope_destination_is_never_a_plotting_plane() -> None:
    text = CLI.read_text()
    assert "*/plotting/*|*/plotting)" in text, (
        "the envelope destination must be checked against a plotting plane")
    chain = CHAIN.read_text()
    assert "*/plotting/*|*/plotting|*/plotting-syst/*|*/plotting-syst)" in chain
    assert "SYSTEMATICS_CHAIN_REFUSED" in chain


def test_the_chain_asserts_receipts_before_it_extracts() -> None:
    """Order is the contract: a FAILED variation must never reach extraction."""
    chain = CHAIN.read_text()
    receipts = chain.index("SYSTEMATICS_CHAIN_MISSING_RECEIPT")
    extraction = chain.index("harvest_class_report.py")
    envelope = chain.index("systematics_envelope.py")
    assert receipts < extraction < envelope, (receipts, extraction, envelope)


def test_the_request_tool_resolves_every_declared_campaign() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, str(REQUEST_TOOL),
             "--selector", str(ROOT / "config" / "dataset_selector.json"),
             "--checkout", str(ROOT), "--dataset", NOMINAL,
             "--results-root", tmp, "--commit", "aaaaaaaaaaaa",
             "--out", f"{tmp}/plan.json"],
            env={**os.environ,
                 "HADRONIZATION_DATA_ROOT": "/tmp/hadronization-test-data"},
            text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
        plan = json.loads(Path(f"{tmp}/plan.json").read_text())
    sys.path.insert(0, str(ROOT / "extraction"))
    from combine_per_class import required_campaigns  # noqa: E402
    assert set(plan["resolver_tags"]) == required_campaigns(), plan["resolver_tags"]
    assert set(plan["receipts"]) == required_campaigns()
    assert "HF_SYS_PTHAT_1" not in plan["resolver_tags"], (
        "R9 excludes the PTHAT_1 arm; a request must not demand its receipt")
    assert "HF_SYS_PTHAT_4" in plan["resolver_tags"], plan["resolver_tags"]
    assert "/systematics" in plan["out_dir"]
    assert "/plotting" not in plan["out_dir"]


# ---- the flag validation gate ---------------------------------------------

def test_a_complete_envelope_validates() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        envelope, plane = fixture(Path(tmp))
        result = assert_tool(envelope, plane)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ENVELOPE_VALID" in result.stdout


def test_an_absent_envelope_names_the_path_field() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        _, plane = fixture(Path(tmp))
        result = assert_tool(Path(tmp) / "absent.json", plane)
    assert result.returncode != 0
    assert "field=path" in result.stderr, result.stderr


def test_a_wrong_schema_names_the_schema_field() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        envelope, plane = fixture(Path(tmp), schema="hadronization_something_v9")
        result = assert_tool(envelope, plane)
    assert result.returncode != 0
    assert "field=schema" in result.stderr, result.stderr


def test_an_incomplete_envelope_names_the_status_field() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        envelope, plane = fixture(Path(tmp), status="INCOMPLETE")
        result = assert_tool(envelope, plane)
    assert result.returncode != 0
    assert "field=status" in result.stderr, result.stderr
    assert "HF_SYS_PTHAT_4" in result.stderr, result.stderr


def test_a_boundary_receipt_mismatch_names_its_field() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        envelope, plane = fixture(Path(tmp), boundary_sha="0" * 64)
        result = assert_tool(envelope, plane)
    assert result.returncode != 0
    assert "field=provenance.nominal_boundary_receipt_sha256" in result.stderr


def test_an_absent_nominal_plane_refuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        envelope, plane = fixture(Path(tmp))
        shutil.rmtree(plane)
        result = assert_tool(envelope, plane)
    assert result.returncode != 0
    assert "field=provenance.nominal_boundary_receipt_sha256" in result.stderr
    assert "plotting plane is absent" in result.stderr, result.stderr


def test_a_nominal_plane_without_a_receipt_refuses() -> None:
    """The plane exists but nothing was rendered into it."""
    with tempfile.TemporaryDirectory() as tmp:
        envelope, plane = fixture(Path(tmp))
        for found in plane.rglob("multiplicity_boundary_receipt_v2.json"):
            found.unlink()
        result = assert_tool(envelope, plane)
    assert result.returncode != 0
    assert "field=provenance.nominal_boundary_receipt_sha256" in result.stderr
    assert "render the nominal figures first" in result.stderr, result.stderr


def test_two_boundary_receipts_refuse() -> None:
    """The plotter writes exactly one. Two means the plane is not what it claims."""
    with tempfile.TemporaryDirectory() as tmp:
        envelope, plane = fixture(Path(tmp))
        second = plane / "OtherCanvas"
        second.mkdir()
        (second / "multiplicity_boundary_receipt_v2.json").write_text("{}")
        result = assert_tool(envelope, plane)
    assert result.returncode != 0
    assert "exactly one is required" in result.stderr, result.stderr


def test_an_empty_complete_envelope_refuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        envelope, plane = fixture(Path(tmp), rows=[])
        result = assert_tool(envelope, plane)
    assert result.returncode != 0
    assert "field=rows" in result.stderr, result.stderr


def test_the_flag_requires_a_path() -> None:
    result = cli("plot", NOMINAL, "--systematics")
    assert result.returncode == 2, result.stdout + result.stderr
    assert "--systematics requires an envelope path" in result.stderr, result.stderr


def test_the_flag_exports_the_envelope_and_its_digest() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        # The CLI derives the plane from the checkout's own commit, so the
        # fixture must be built at that commit rather than at a stand-in.
        envelope, _ = fixture(Path(tmp), commit=short_commit())
        results = Path(tmp) / "results"
        result = cli("plot", NOMINAL, "--systematics", str(envelope),
                     env_extra={"HADRONIZATION_RESULTS_ROOT": str(results)})
        digest = hashlib.sha256(envelope.read_bytes()).hexdigest()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SYSTEMATICS_OVERLAY_PREFLIGHT_ONLY status=PASS" in result.stdout
    assert "HADRONIZATION_PLOT_SYST_OUTPUT=" in result.stdout
    assert "plotting-syst" in result.stdout
    assert f"HADRONIZATION_SYSTEMATICS_ENVELOPE_SHA256={digest}" in result.stdout
    assert "/plotting/" not in result.stdout.split(
        "HADRONIZATION_PLOT_SYST_OUTPUT=")[1].splitlines()[0]


def main() -> int:
    tests = [v for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"systematics CLI: {len(tests)} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
