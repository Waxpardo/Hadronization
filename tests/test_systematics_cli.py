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

THE THIRD GATE IS THE EXIT STATUS. A refusal that reaches its caller as
status 0 is indistinguishable from success, which is the incident class
PRACTICE 3.5 exists for. The envelope probe of 2026-08-25 reported exactly
that on the chain's receipt-absence path, so
`test_the_systematics_command_exits_nonzero_when_the_chain_refuses` runs the
real refusal on a fixture tree and reads the status.

WHERE AN INPUT COMES FROM. Results are commit-scoped and an accepted result is
immutable, so the request tool resolves the current commit root first and the
digest pin in `config/accepted_measurements_v1.json` second. The pin holds the
digests of artifacts that live on the cluster, which no fixture can forge, so
the pin-hit and digest-drift paths are exercised at the function, where the
pin map is a parameter, and the resolution order is exercised end to end.

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
PIN_FILE = ROOT / "config" / "accepted_measurements_v1.json"
CHAIN = ROOT / "extraction" / "pipeline" / "systematics_chain.sh"
SELECTOR = ROOT / "config" / "dataset_selector.json"
NOMINAL = "hf_run3_v1_candidate"
VARIATION = "hf_sys_mur_up_variation"
ACCEPTED_ROOT = "33451a28fdff"
NOMINAL_ROOT = "4d309e9f99e4"
RECEIPT_NAME = "measurement_receipt.json"


def request_module():
    """The request tool as a module, so the pin map can be a parameter."""
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))
    import systematics_request  # noqa: E402

    return systematics_request


def request(results_root: Path, *extra: str,
            commit: str = "aaaaaaaaaaaa") -> subprocess.CompletedProcess:
    """Run the request tool against a results root that holds no data."""
    return subprocess.run(
        [sys.executable, str(REQUEST_TOOL), "--selector", str(SELECTOR),
         "--checkout", str(ROOT), "--dataset", NOMINAL,
         "--results-root", str(results_root), "--commit", commit, *extra],
        env={**os.environ,
             "HADRONIZATION_DATA_ROOT": "/tmp/hadronization-test-data"},
        text=True, capture_output=True, check=False)


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


# ---- the accepted measurement roots ---------------------------------------

def test_the_pin_file_declares_every_included_campaign() -> None:
    """The pin and the arithmetic must want the same campaigns."""
    pins = json.loads(PIN_FILE.read_text())
    assert pins["schema"] == "hadronization_accepted_measurements_v1"
    sys.path.insert(0, str(ROOT / "extraction"))
    from combine_per_class import required_campaigns  # noqa: E402
    assert set(pins["campaigns"]) == required_campaigns(), sorted(pins["campaigns"])
    assert "HF_SYS_PTHAT_1" not in pins["campaigns"], (
        "R9 excludes that arm; a pin would offer the envelope a ruled-out input")
    for campaign, row in pins["campaigns"].items():
        assert row["accepted_root"] == ACCEPTED_ROOT, row
        assert row["receipt_path"].startswith(
            f"{campaign}/{ACCEPTED_ROOT}/measurements/"), row
        assert row["receipt_path"].endswith(RECEIPT_NAME), row
        assert len(row["receipt_sha256"]) == 64, row
        assert row["receipt_sha256"] == row["receipt_sha256"].lower().strip()
    assert pins["nominal"]["accepted_root"] == NOMINAL_ROOT, pins["nominal"]
    assert len(pins["nominal"]["boundary_receipt_sha256"]) == 64


def test_the_pin_file_holds_no_site_specific_path() -> None:
    """A tracked absolute path would freeze one cluster's layout in the repo."""
    text = PIN_FILE.read_text()
    assert "/data/" not in text, "the pin file carries a site-specific path"
    assert "/cvmfs/" not in text


def test_the_request_reads_the_pin_when_the_current_root_is_empty() -> None:
    """Resolution order, end to end: current commit root first, then the pin."""
    with tempfile.TemporaryDirectory() as tmp:
        result = request(Path(tmp) / "results", "--out", f"{tmp}/plan.json")
        assert result.returncode == 0, result.stdout + result.stderr
        plan = json.loads(Path(f"{tmp}/plan.json").read_text())
    pins = json.loads(PIN_FILE.read_text())
    for campaign, row in plan["accepted_roots"].items():
        assert row["source"] == "accepted_pin", (campaign, row)
        assert row["root"] == ACCEPTED_ROOT, (campaign, row)
        assert row["receipt_sha256"] == \
            pins["campaigns"][campaign]["receipt_sha256"], campaign
        assert f"/{ACCEPTED_ROOT}/" in plan["receipts"][campaign], campaign
    assert plan["nominal_boundary"]["root"] == NOMINAL_ROOT, plan
    assert plan["nominal_boundary"]["source"] == "accepted_pin", plan
    assert plan["accepted_measurements_sha256"] == hashlib.sha256(
        PIN_FILE.read_bytes()).hexdigest()


def test_the_current_commit_root_wins_over_the_pin() -> None:
    """A newer commit that HAS the input never reaches for an accepted root."""
    campaign, commit = "HF_SYS_MUR_UP", "aaaaaaaaaaaa"
    with tempfile.TemporaryDirectory() as tmp:
        results = Path(tmp) / "results"
        here = (results / campaign / commit / "measurements"
                / f"{campaign.lower()}_variation")
        here.mkdir(parents=True)
        (here / RECEIPT_NAME).write_text('{"campaign": "HF_SYS_MUR_UP"}')
        result = request(results, "--out", f"{tmp}/plan.json", commit=commit)
        assert result.returncode == 0, result.stdout + result.stderr
        plan = json.loads(Path(f"{tmp}/plan.json").read_text())
        digest = hashlib.sha256((here / RECEIPT_NAME).read_bytes()).hexdigest()
    row = plan["accepted_roots"][campaign]
    assert row["source"] == "current_commit_root", row
    assert row["root"] == commit, row
    assert row["receipt_sha256"] == digest, row
    assert row["verified"] is True, row
    others = {c for c, r in plan["accepted_roots"].items()
              if r["source"] == "accepted_pin"}
    assert campaign not in others and others, plan["accepted_roots"]


def test_a_pinned_receipt_that_does_not_hash_refuses_by_name() -> None:
    """A pin is a digest. A file at the pinned path is not enough."""
    with tempfile.TemporaryDirectory() as tmp:
        results = Path(tmp) / "results"
        pins = json.loads(PIN_FILE.read_text())
        row = pins["campaigns"]["HF_SYS_PTHAT_4"]
        planted = results / row["receipt_path"]
        planted.parent.mkdir(parents=True)
        planted.write_text("this is not the accepted receipt")
        result = request(results)
    assert result.returncode != 0, result.stdout
    assert "HF_SYS_PTHAT_4" in result.stderr, result.stderr
    assert "accepted_measurements_v1.json" in result.stderr, result.stderr
    assert row["receipt_sha256"] in result.stderr, result.stderr


def test_a_campaign_the_pin_does_not_declare_refuses_by_name() -> None:
    """No pin and no current root is a refusal, never a guessed path."""
    module = request_module()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            module.resolve_receipt(
                Path(tmp), "HF_SYS_PTHAT_1", "hf_sys_pthat_1_variation",
                "aaaaaaaaaaaa", {"campaigns": {}})
        except module.RequestRefused as error:
            message = str(error)
        else:
            raise AssertionError("an undeclared campaign resolved")
    assert "HF_SYS_PTHAT_1" in message, message
    assert "accepted_measurements_v1.json" in message, message


def test_a_pinned_receipt_that_hashes_correctly_resolves() -> None:
    """The pin hit: the artifact is present and carries the pinned digest."""
    module = request_module()
    with tempfile.TemporaryDirectory() as tmp:
        results = Path(tmp)
        relative = (f"HF_SYS_MUF_UP/{ACCEPTED_ROOT}/measurements/"
                    f"hf_sys_muf_up_variation/{RECEIPT_NAME}")
        planted = results / relative
        planted.parent.mkdir(parents=True)
        planted.write_text('{"campaign": "HF_SYS_MUF_UP"}')
        digest = hashlib.sha256(planted.read_bytes()).hexdigest()
        pins = {"campaigns": {"HF_SYS_MUF_UP": {
            "accepted_root": ACCEPTED_ROOT, "receipt_path": relative,
            "receipt_sha256": digest}}}
        resolved = module.resolve_receipt(
            results, "HF_SYS_MUF_UP", "hf_sys_muf_up_variation",
            "aaaaaaaaaaaa", pins)
    assert resolved["source"] == "accepted_pin", resolved
    assert resolved["root"] == ACCEPTED_ROOT, resolved
    assert resolved["receipt_sha256"] == digest, resolved
    assert resolved["verified"] is True, resolved


def test_an_accepted_root_is_never_a_destination() -> None:
    """Nothing writes into a root the pin names. Ruling R7's fail-closed frame."""
    with tempfile.TemporaryDirectory() as tmp:
        result = request(Path(tmp) / "results", commit=ACCEPTED_ROOT)
    assert result.returncode != 0, result.stdout
    assert ACCEPTED_ROOT in result.stderr, result.stderr
    assert "accepted root" in result.stderr, result.stderr


# ---- a refusal must be nonzero --------------------------------------------

def test_the_systematics_command_exits_nonzero_when_the_chain_refuses() -> None:
    """The Phase 1b gate. Run the real refusal and read the status.

    The probe of 2026-08-25 reported this refusal reaching its caller as 0. A
    caller cannot tell that from a completed envelope, so the status is the
    thing under test, not the message.
    """
    with tempfile.TemporaryDirectory() as tmp:
        results = Path(tmp) / "results"
        results.mkdir()
        result = cli("systematics", NOMINAL, env_extra={
            "HADRONIZATION_REQUEST_PREFLIGHT_ONLY": "0",
            "HADRONIZATION_RESULTS_ROOT": str(results),
            "HADRONIZATION_DATA_ROOT": "/tmp/hadronization-test-data"})
    assert result.returncode != 0, (
        "the chain refused and the command reported success: "
        + result.stdout + result.stderr)
    assert "SYSTEMATICS_CHAIN_REFUSED" in result.stderr, result.stderr
    assert "SYSTEMATICS_REFUSED" in result.stderr, result.stderr
    # The refusal must name the accepted root it looked in, not a path under
    # the current commit that never held these results.
    assert ACCEPTED_ROOT in result.stderr, result.stderr


def test_the_chain_script_exits_nonzero_on_a_missing_receipt() -> None:
    """The same gate one layer down, with no environment in the way."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        out_dir = base / "systematics"
        out_dir.mkdir()
        plan = base / "plan.json"
        plan.write_text(json.dumps({
            "nominal_campaign": "HF_RUN3_V1",
            "nominal_dataset": NOMINAL,
            "envelope": str(out_dir / "systematics_envelope.json"),
            "resolver_tags": {"HF_SYS_MUR_UP": "complete_root_HF_SYS_MUR_UP"},
            "receipts": {"HF_SYS_MUR_UP": str(base / "absent" / RECEIPT_NAME)},
            "accepted_roots": {"HF_SYS_MUR_UP": {
                "root": ACCEPTED_ROOT, "source": "accepted_pin",
                "receipt_sha256": "0" * 64, "verified": False}},
            "nominal_boundary": {"root": NOMINAL_ROOT,
                                 "source": "accepted_pin",
                                 "boundary_receipt_sha256": "0" * 64,
                                 "verified": False},
        }))
        result = subprocess.run(
            ["bash", str(CHAIN), str(plan), str(out_dir)],
            text=True, capture_output=True, check=False)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "SYSTEMATICS_CHAIN_MISSING_RECEIPT" in result.stderr, result.stderr
    assert "SYSTEMATICS_CHAIN_REFUSED" in result.stderr, result.stderr


def test_every_chain_refusal_leaves_through_one_door() -> None:
    """`refuse` is the only writer of the refusal marker, and it exits nonzero."""
    text = CHAIN.read_text()
    body = text[text.index("refuse() {"):text.index("\n}\n", text.index("refuse() {"))]
    assert 'echo "SYSTEMATICS_CHAIN_REFUSED $*" >&2' in body, body
    assert 'exit "${status}"' in body, body
    others = [line for line in text.splitlines()
              if "SYSTEMATICS_CHAIN_REFUSED" in line
              and 'echo "SYSTEMATICS_CHAIN_REFUSED $*"' not in line]
    assert others == [], others
    assert "exit $?" not in text, "a discarded status is how a refusal reads as 0"


def test_the_systematics_arm_never_discards_a_status() -> None:
    """The CLI carries the chain's status out; it does not rely on set -e."""
    text = CLI.read_text()
    arm = text[text.index("\n  systematics)"):text.index("\n  plot)")]
    assert "chain_status=0" in arm, arm
    assert 'exit "${chain_status}"' in arm, arm
    assert "request_status=0" in arm, arm
    assert 'exit "${request_status}"' in arm, arm
    assert "exit $?" not in arm, "a discarded status is how a refusal reads as 0"


def main() -> int:
    tests = [v for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"systematics CLI: {len(tests)} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
