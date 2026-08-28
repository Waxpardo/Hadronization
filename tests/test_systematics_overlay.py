#!/usr/bin/env python3
"""The systematic overlay: what it draws, what it refuses, where it writes.

ROOT is required for the canvas leg of this test.

THREE PROPERTIES, each of which a wrong renderer would break silently:

  it draws          a COMPLETE envelope and a nominal render log produce a
                    canvas, a macro and a manifest, every one of them stamped
                    with the envelope sha256 and the producing commit
  it refuses        an INCOMPLETE envelope, a wrong schema, a mixed
                    observable, and a ratio band asked for from yield rows
  it stays inside   nothing is written outside the plotting-syst plane, and
                    the plane name itself is checked rather than trusted

WHY THE OBSERVABLE MATTERS. Lambda_b and B- share their triggers and their
events, so a per-class yield systematic may not be propagated into their
ratio. The renderer draws the observable the envelope declares and refuses to
mix two, which is the only way this cannot go wrong quietly.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "plotting" / "render_systematics_overlay.py"
PLOTTER = ROOT / "plotting" / "improvedPlotting_THnSparse.C"

# Ruling R10: the class set and its bin names come from the contract, so this
# fixture cannot drift from the axis the renderer will meet.
CLASS_CONTRACT = ROOT / "config" / "multiplicity_percentile_classes_v2.json"
_CLASS_ROWS = json.loads(CLASS_CONTRACT.read_text())["classes"]
CLASSES = [row["class"] for row in _CLASS_ROWS]
BINS = {row["class"]: "hDPhi" + row["bin"] for row in _CLASS_ROWS}
TUNES = ("MONASH", "JUNCTIONS")
COMMIT = "1234567890abcdef1234567890abcdef12345678"


def nominal_log(path: Path) -> None:
    lines = []
    shifts = [0.001 * (index - 4.5) for index in range(10)]

    def encoded(values: list[float]) -> str:
        return ",".join(format(value, ".17g") for value in values)

    def sem(values: list[float]) -> float:
        mean = sum(values) / len(values)
        return math.sqrt(sum((value - mean) ** 2 for value in values)
                         / (len(values) * (len(values) - 1)))

    for tune_index, tune in enumerate(TUNES):
        for index, cls in enumerate(CLASSES):
            value = 1.0 + 0.05 * index + 0.1 * tune_index
            reference_blocks = [1.0 + shift for shift in shifts]
            desired_ratios = [value + shift for shift in shifts]
            numerator_blocks = [ratio * reference for ratio, reference in zip(
                desired_ratios, reference_blocks)]
            # Match the producer: the emitted ratio is the division of the
            # two stored double-precision block yields, not a separately
            # rounded desired value.
            ratio_blocks = [numerator / reference for numerator, reference in zip(
                numerator_blocks, reference_blocks)]
            common = (
                "UNCERTAINTY_MATRIX "
                "schema=hadronization_uncertainty_matrix_v2 block_count=10 "
                f"flavour=BEAUTY trigger=B^{{+}} tune={tune} bin={BINS[cls]} ")
            lines.append(
                common + "associate=B- is_reference=true "
                f"central_yield=1 reference_yield=1 "
                f"block_yields={encoded(reference_blocks)} block_ratios=NA "
                f"yield_sem={sem(reference_blocks):.17g} ratio_sem=NA "
                "status=NOT_APPLICABLE ratio_status=NOT_APPLICABLE")
            lines.append(
                common + f"associate=Lambda_b is_reference=false "
                f"central_yield={value} reference_yield=1 "
                f"block_yields={encoded(numerator_blocks)} "
                f"block_ratios={encoded(ratio_blocks)} "
                f"yield_sem={sem(numerator_blocks):.17g} "
                f"ratio_sem={sem(ratio_blocks):.17g} central_triggers=1000 "
                f"block_triggers=100,100,100,100,100,100,100,100,100,100 "
                f"status=PASS ratio_status=PASS")
    path.write_text("\n".join(lines) + "\n")


def envelope(path: Path, *, status: str = "COMPLETE",
             observable: str = "balancing_yield",
             classes: list[str] | None = None,
             mixed: bool = False, schema: str | None = None) -> None:
    rows = []
    for tune_index, tune in enumerate(TUNES):
        for index, cls in enumerate(classes if classes is not None else CLASSES):
            value = 1.0 + 0.05 * index + 0.1 * tune_index
            rows.append({
                "campaign": "HF_RUN3_V1", "tune": tune, "flavour": "BEAUTY",
                "trigger": "B^{+}", "associate": "Lambda_b",
                "observable": ("balancing_ratio"
                               if mixed and index == 0 else observable),
                "class": cls, "nominal_yield": value, "nominal_sem": 0.02,
                "terms": {"S1a_mur": {"contribution_percent": 3.0},
                          "S3_pthat": {"contribution_percent": 4.0}},
                "quoted_arm": {"S1a_mur": "HF_SYS_MUR_UP"},
                "dropped": [], "combined_percent": 5.0,
                "combined_absolute": 0.05 * value,
            })
    path.write_text(json.dumps({
        "schema": schema or "hadronization_systematics_envelope_v1",
        "status": status,
        "missing": [] if status == "COMPLETE" else ["HF_SYS_PTHAT_1: no PASS receipt"],
        "method": {"d2_quadrature": "", "a1_max_rule": "", "a2_s6_excluded": ""},
        "sources": [], "rows": rows,
        "provenance": {"nominal_boundary_receipt_sha256": "a" * 64},
    }))


def render(tmp: Path, *, plane_name: str = "plotting-syst",
           **envelope_kwargs) -> subprocess.CompletedProcess:
    log = tmp / "nominal.log"
    nominal_log(log)
    env_path = tmp / "envelope.json"
    envelope(env_path, **envelope_kwargs)
    plane = tmp / "out" / plane_name
    return subprocess.run(
        [sys.executable, str(RENDERER), "--envelope", str(env_path),
         "--output-plane", str(plane), "--campaign", "HF_RUN3_V1",
         "--commit", COMMIT, "--nominal-log", str(log)],
        text=True, capture_output=True, check=False)


def pdf_text(pdf: bytes) -> bytes:
    """The drawn text of a ROOT PDF. Its content streams are deflated."""
    out = b""
    for match in re.finditer(rb"stream\r?\n(.*?)endstream", pdf, re.S):
        try:
            out += zlib.decompress(match.group(1))
        except zlib.error:
            out += match.group(1)
    return out


def test_a_complete_envelope_renders_headless() -> None:
    root = shutil.which("root")
    if root is None:
        raise RuntimeError("ROOT is required for the systematics overlay test")
    with tempfile.TemporaryDirectory() as tmp:
        result = render(Path(tmp))
        plane = Path(tmp) / "out" / "plotting-syst"
        written = sorted(p.name for p in plane.rglob("*") if p.is_file())
        outside = [p for p in (Path(tmp) / "out").rglob("*")
                   if p.is_file() and "plotting-syst" not in p.parts]
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OVERLAY_RENDERED" in result.stdout, result.stdout
    assert outside == [], f"the overlay wrote outside its plane: {outside}"
    suffixes = {name.rsplit(".", 1)[-1] for name in written}
    assert {"C", "pdf", "png", "json"} <= suffixes, written


def test_every_output_carries_the_envelope_digest_and_the_commit() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        result = render(Path(tmp))
        assert result.returncode == 0, result.stdout + result.stderr
        plane = Path(tmp) / "out" / "plotting-syst"
        digest = hashlib.sha256(
            (Path(tmp) / "envelope.json").read_bytes()).hexdigest()
        macro = next(plane.glob("*.C")).read_text()
        manifest = json.loads(next(plane.glob("*_manifest.json")).read_text())
        pdf = next(plane.glob("*.pdf")).read_bytes()
    assert digest in macro and COMMIT in macro, "the macro carries no stamp"
    assert manifest["envelope_sha256"] == digest
    assert manifest["producing_commit"] == COMMIT
    # The canvas itself carries the stamp, not only the files beside it.
    drawn = pdf_text(pdf)
    assert digest[:16].encode() in drawn, "the canvas carries no envelope digest"
    assert COMMIT[:12].encode() in drawn, "the canvas carries no commit"


def test_an_incomplete_envelope_refuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        result = render(Path(tmp), status="INCOMPLETE")
        plane = Path(tmp) / "out" / "plotting-syst"
        assert not plane.exists() or not list(plane.iterdir()), (
            "a refused overlay must write nothing")
    assert result.returncode != 0, result.stdout
    assert "OVERLAY_REFUSED" in result.stderr, result.stderr
    assert "INCOMPLETE" in result.stderr


def test_a_wrong_schema_refuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        result = render(Path(tmp), schema="hadronization_something_v2")
    assert result.returncode != 0
    assert "OVERLAY_REFUSED" in result.stderr, result.stderr


def test_two_observables_in_one_envelope_refuse() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        result = render(Path(tmp), mixed=True)
    assert result.returncode != 0
    assert "exactly one observable" in result.stderr, result.stderr


def test_the_overlay_writes_only_under_a_plotting_syst_plane() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        result = render(Path(tmp), plane_name="plotting")
    assert result.returncode != 0, result.stdout
    assert "writes only under a plotting-syst plane" in result.stderr, \
        result.stderr


def test_a_class_the_envelope_omits_is_labelled_statistical_only() -> None:
    """A reader must never guess which points carry a band."""
    # Ruling R10: which two classes the envelope omits follows the contract's
    # own class list, so this test does not name them a second time.
    omitted = set(CLASSES[-2:])
    with tempfile.TemporaryDirectory() as tmp:
        result = render(Path(tmp), classes=CLASSES[:-2])
        assert result.returncode == 0, result.stdout + result.stderr
        plane = Path(tmp) / "out" / "plotting-syst"
        manifest = json.loads(next(plane.glob("*_manifest.json")).read_text())
        macro = next(plane.glob("*.C")).read_text()
        drawn = pdf_text(next(plane.glob("*.pdf")).read_bytes())
    labelled = {row["class"] for row in manifest["statistical_only_points"]}
    assert labelled == omitted, labelled
    for point in manifest["points"]:
        if point["class"] in omitted:
            assert point["statistical_only"] is True
            assert point["systematic"] == 0.0
            assert point["label"] == "STAT-ONLY"
    assert "STAT-ONLY" in macro, "the canvas does not say which points lack a band"
    assert f"stat_only={len(omitted) * len(TUNES)}" in result.stdout, \
        result.stdout
    assert b"STAT-ONLY" in drawn, "the drawn canvas omits the label"


def test_per_source_rendering_is_a_code_level_switch_default_off() -> None:
    text = RENDERER.read_text()
    assert "DRAW_PER_SOURCE = False" in text
    assert "--per-source" not in text, (
        "presentation is an owner decision; no caller may set it")
    with tempfile.TemporaryDirectory() as tmp:
        result = render(Path(tmp))
        plane = Path(tmp) / "out" / "plotting-syst"
        manifest = json.loads(next(plane.glob("*_manifest.json")).read_text())
    assert manifest["draw_per_source"] is False
    assert "owner decisions" in manifest["presentation"]


def test_the_overlay_does_not_touch_the_nominal_plotter() -> None:
    """Ruling R7: the overlay is a separate composition step."""
    text = RENDERER.read_text()
    assert "improvedPlotting_THnSparse" not in text.replace(
        "improvedPlotting_THnSparse.C`", ""), (
        "the overlay must not drive the nominal plotter")
    assert PLOTTER.is_file()


def test_the_renderer_refuses_an_absent_nominal_log() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        env_path = Path(tmp) / "envelope.json"
        envelope(env_path)
        result = subprocess.run(
            [sys.executable, str(RENDERER), "--envelope", str(env_path),
             "--output-plane", str(Path(tmp) / "out" / "plotting-syst"),
             "--campaign", "HF_RUN3_V1", "--commit", COMMIT,
             "--nominal-log", str(Path(tmp) / "absent.log")],
            text=True, capture_output=True, check=False)
    assert result.returncode != 0
    assert "no nominal render log" in result.stderr, result.stderr


def main() -> int:
    tests = [v for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"systematics overlay: {len(tests)} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
