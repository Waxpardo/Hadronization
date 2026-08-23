#!/usr/bin/env python3
"""The systematics envelope: its shape, its refusals, and its arithmetic.

WHY THE ARITHMETIC IS CHECKED AGAINST HAND-COMPUTED NUMBERS. Comparing a tool
against itself proves agreement, not correctness. The numbers below were
worked out by hand from PRACTICE section 5 before the tool ran, and the
synthetic fixture is built so the per-cent and absolute routes coincide
exactly: the nominal yield is 100, so a scale of 100/nominal is one.

WHY EVERY REFUSAL IS A MUTATION. A gate never seen to fail is not known to be
a gate. Each fail-closed test changes exactly one thing about a fixture that
otherwise completes, and requires a nonzero exit with the reason recorded in
the envelope's `missing` list.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "systematics_envelope.py"
ENVELOPE_CONTRACT = ROOT / "config" / "systematics_envelope_v1.json"
SOURCES_CONTRACT = ROOT / "config" / "systematics_sources_v1.json"
CLASS_CONTRACT = ROOT / "config" / "multiplicity_percentile_classes_v2.json"

CAMPAIGN = "HF_RUN3_V1"
DATASET = "hf_run3_v1_candidate"
CLASSES = [f"c{i}" for i in range(1, 12)]

# campaign -> (variation_yield, variation_sem). Nominal is 100.0 +- 3.0.
# Chosen so that D2 and A1 both give exact values:
#   S1a  MUR_UP    delta +4, SEM(delta) = sqrt(4^2 + 3^2) = 5   -> SEM binds, 5
#   S1b  MUF_UP    delta +8, SEM(delta) = sqrt(0^2 + 3^2) = 3   -> |delta| binds, 8
#   S2   PDF       delta +6, SEM(delta) = sqrt(4^2 + 3^2) = 5   -> |delta| binds, 6
#   S3   PTHAT_4   delta +12, SEM(delta) = sqrt(4^2 + 3^2) = 5  -> |delta| binds, 12
# Section 9.1 then drops S2 because |muf| = 8 >= |pdf| = 6 and both exceed 0.1.
# Combined = sqrt(5^2 + 8^2 + 12^2) = sqrt(233).
ARMS = {
    "HF_SYS_MUR_UP": (104.0, 4.0),
    "HF_SYS_MUR_DOWN": (97.0, 4.0),
    "HF_SYS_MUF_UP": (108.0, 0.0),
    "HF_SYS_MUF_DOWN": (94.0, 0.0),
    "HF_SYS_PDF_CTEQ6L1": (106.0, 4.0),
    "HF_SYS_PTHAT_4": (112.0, 4.0),
    "HF_SYS_PTHAT_1": (88.0, 4.0),
}
NOMINAL_YIELD, NOMINAL_SEM = 100.0, 3.0
EXPECTED_COMBINED = math.sqrt(233.0)
BOUNDARY_SHA = "b" * 64


def resolver_tags() -> dict[str, str]:
    return {c: f"complete_root_{c}" for c in ARMS}


def delta_report(classes: list[str] = None) -> dict:
    rows = []
    for campaign, (v_y, v_s) in ARMS.items():
        for cls in (classes if classes is not None else CLASSES):
            rows.append({
                "campaign": campaign,
                "flavour": "BEAUTY", "trigger": "B^{+}", "tune": "MONASH",
                "associate": "Lambda_b", "class": cls,
                "nominal_yield": NOMINAL_YIELD, "nominal_sem": NOMINAL_SEM,
                "variation_yield": v_y, "variation_sem": v_s,
                "delta": v_y - NOMINAL_YIELD,
                "delta_sem": math.sqrt(v_s ** 2 + NOMINAL_SEM ** 2),
                "significance": 0.0, "flagged_below_2sem": False,
                "relative_shift_percent": 0.0,
                "relative_shift_undefined": False,
                "nominal_status": "PASS", "variation_status": "PASS",
            })
    return {
        "schema": "hadronization_per_class_delta_v1",
        "control_comparison": {"agree": True},
        "deltas": rows,
        "trigger_consistency": [],
        "trigger_consistency_failures": [],
        "identical_campaign_pairs": [],
        "campaigns": sorted(ARMS),
    }


def receipt(campaign: str, status: str = "PASS",
            tags: list[str] | None = None) -> dict:
    return {
        "schema": "hadronization_measurement_receipt_v3",
        "completion_status": status,
        "failure_reasons": [] if status == "PASS" else ["synthetic failure"],
        "purpose": "measurement",
        "publication_eligible": False,
        "campaign": campaign,
        "expected_complete_root_tag": f"complete_root_{campaign}",
        "resolved_complete_root_tags":
            tags if tags is not None else [f"complete_root_{campaign}"],
    }


def run(tmp: Path, *, report: dict | None = None,
        skip: set[str] | None = None,
        fail: set[str] | None = None,
        bad_tag: str | None = None) -> tuple[subprocess.CompletedProcess, dict]:
    """Write a fixture tree, run the tool, return (process, envelope)."""
    report_path = tmp / "per_class_deltas.json"
    report_path.write_text(json.dumps(report or delta_report()))
    tags_path = tmp / "resolver_tags.json"
    tags_path.write_text(json.dumps(resolver_tags()))
    out = tmp / "systematics_envelope.json"

    args = [sys.executable, str(TOOL), "--report", str(report_path),
            "--campaign", CAMPAIGN, "--nominal-dataset", DATASET,
            "--resolver-tags", str(tags_path),
            "--boundary-receipt-sha", BOUNDARY_SHA, "--out", str(out)]
    for campaign in ARMS:
        if skip and campaign in skip:
            continue
        body = receipt(
            campaign,
            "FAIL" if fail and campaign in fail else "PASS",
            ["complete_root_SOMETHING_ELSE"] if bad_tag == campaign else None)
        path = tmp / f"{campaign}_receipt.json"
        path.write_text(json.dumps(body))
        args += ["--receipt", f"{campaign}={path}"]

    proc = subprocess.run(args, capture_output=True, text=True, check=False)
    envelope = json.loads(out.read_text()) if out.is_file() else {}
    return proc, envelope


# ---- the contract itself --------------------------------------------------

def test_the_envelope_contract_declares_its_schema_and_method_tags() -> None:
    contract = json.loads(ENVELOPE_CONTRACT.read_text())
    assert contract["schema"] == "hadronization_systematics_envelope_v1"
    assert set(contract["method_tags"]) == {
        "d2_quadrature", "a1_max_rule", "a2_s6_excluded"}
    assert set(contract["status_values"]) == {"COMPLETE", "INCOMPLETE", "FAIL"}
    for key in ("campaign", "tune", "observable", "class"):
        assert key in contract["row_identity"]["fields"], key
    for key in ("delta", "sem_var", "sem_nominal", "sem_delta",
                "contribution"):
        assert key in contract["term_fields"], key
    for key in ("producing_commit", "measurement_receipts", "resolver_tags",
                "nominal_boundary_receipt_sha256"):
        assert key in contract["provenance_fields"], key


def test_the_source_contract_keeps_pthat_1_included() -> None:
    """The fail-closed state is deliberate: excluding it is an owner decision."""
    sources = json.loads(SOURCES_CONTRACT.read_text())
    assert sources["schema"] == "hadronization_systematics_sources_v1"
    by_name = {row["source"]: row for row in sources["sources"]}
    assert by_name["S3_pthat"]["included"] is True
    assert "HF_SYS_PTHAT_1" in by_name["S3_pthat"]["campaigns"]
    assert all(row["included"] for row in sources["sources"])
    absent = {row["source"] for row in sources["declared_absent"]}
    assert {"S4_counter_window", "S6_unresolved_origin",
            "tune_bundle_spread"} <= absent


def test_the_source_contract_agrees_with_the_arithmetic() -> None:
    sys.path.insert(0, str(ROOT / "extraction"))
    from combine_per_class import SOURCES  # noqa: E402
    sources = json.loads(SOURCES_CONTRACT.read_text())
    declared = {row["source"]: tuple(row["campaigns"])
                for row in sources["sources"] if row["campaigns"]}
    assert declared == SOURCES, (declared, SOURCES)


# ---- the arithmetic -------------------------------------------------------

def test_a_complete_envelope_matches_the_hand_computed_quadrature() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert envelope["status"] == "COMPLETE", envelope["missing"]
    assert envelope["missing"] == []
    assert len(envelope["rows"]) == len(CLASSES)

    row = next(r for r in envelope["rows"] if r["class"] == "c1")
    assert row["campaign"] == CAMPAIGN
    assert row["tune"] == "MONASH"
    assert row["observable"] == "balancing_yield"
    assert math.isclose(row["combined_percent"], EXPECTED_COMBINED,
                        rel_tol=0, abs_tol=1e-12), row["combined_percent"]
    assert math.isclose(row["combined_absolute"], EXPECTED_COMBINED,
                        rel_tol=0, abs_tol=1e-12)
    assert row["dropped"] == ["S2_pdf"], row["dropped"]


def test_d2_quadrature_is_the_retained_delta_error() -> None:
    """SEM(Delta) = sqrt(SEM_var^2 + SEM_nominal^2), with both terms kept."""
    with tempfile.TemporaryDirectory() as tmp:
        _, envelope = run(Path(tmp))
    row = next(r for r in envelope["rows"] if r["class"] == "c1")
    term = row["terms"]["S1a_mur"]
    assert term["campaign"] == "HF_SYS_MUR_UP"
    assert math.isclose(term["sem_var"], 4.0, abs_tol=1e-12)
    assert math.isclose(term["sem_nominal"], 3.0, abs_tol=1e-12)
    assert math.isclose(term["sem_delta"], 5.0, abs_tol=1e-12)
    assert math.isclose(term["sem_delta"],
                        math.hypot(term["sem_var"], term["sem_nominal"]),
                        abs_tol=1e-12)


def test_a1_takes_the_larger_of_the_shift_and_its_error() -> None:
    """One term where the error binds, one where the shift binds."""
    with tempfile.TemporaryDirectory() as tmp:
        _, envelope = run(Path(tmp))
    terms = next(r for r in envelope["rows"] if r["class"] == "c1")["terms"]

    # |delta| = 4 < SEM(delta) = 5, so A1 takes 5.
    assert math.isclose(terms["S1a_mur"]["delta"], 4.0, abs_tol=1e-12)
    assert math.isclose(terms["S1a_mur"]["contribution"], 5.0, abs_tol=1e-12)

    # |delta| = 12 > SEM(delta) = 5, so A1 takes 12.
    assert math.isclose(terms["S3_pthat"]["delta"], 12.0, abs_tol=1e-12)
    assert math.isclose(terms["S3_pthat"]["contribution"], 12.0, abs_tol=1e-12)

    # The larger arm is quoted, not half the spread (pre-registration 2.5).
    assert terms["S3_pthat"]["campaign"] == "HF_SYS_PTHAT_4"

    for name, term in terms.items():
        assert math.isclose(
            term["contribution"],
            max(abs(term["delta"]), term["sem_delta"]), abs_tol=1e-12), name


def test_a2_keeps_s6_out_of_the_per_class_quadrature() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        _, envelope = run(Path(tmp))
    assert envelope["method"]["a2_s6_excluded"]
    for row in envelope["rows"]:
        for name in row["terms"]:
            assert "S6" not in name and name != "A2", name


def test_s5_is_a_measured_zero_and_not_an_absent_source() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        _, envelope = run(Path(tmp))
    term = next(r for r in envelope["rows"]
                if r["class"] == "c1")["terms"]["S5_class_migration"]
    assert term["delta"] == 0.0
    assert term["contribution"] == 0.0


# ---- the refusals ---------------------------------------------------------

def test_a_missing_receipt_refuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp), skip={"HF_SYS_PTHAT_1"})
    assert proc.returncode != 0, proc.stdout
    assert envelope["status"] == "INCOMPLETE", envelope["status"]
    assert any("HF_SYS_PTHAT_1" in r for r in envelope["missing"]), envelope
    assert envelope["rows"] == [] or envelope["status"] != "COMPLETE"


def test_a_fail_receipt_refuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp), fail={"HF_SYS_PTHAT_1"})
    assert proc.returncode != 0, proc.stdout
    assert envelope["status"] == "FAIL", envelope["status"]
    assert any("not PASS" in r for r in envelope["missing"]), envelope["missing"]


def test_a_receipt_that_resolved_another_tag_refuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp), bad_tag="HF_SYS_MUR_UP")
    assert proc.returncode != 0, proc.stdout
    assert envelope["status"] == "FAIL", envelope["status"]
    assert any("complete_root_SOMETHING_ELSE" in r
               for r in envelope["missing"]), envelope["missing"]


def test_an_unknown_class_refuses() -> None:
    report = delta_report()
    report["deltas"][0]["class"] = "c99"
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp), report=report)
    assert proc.returncode != 0, proc.stdout
    assert envelope["status"] == "FAIL", envelope["status"]
    assert any("unknown classes" in r for r in envelope["missing"]), \
        envelope["missing"]


def test_a_partition_that_omits_a_class_refuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp),
                             report=delta_report(classes=CLASSES[:-1]))
    assert proc.returncode != 0, proc.stdout
    assert envelope["status"] == "FAIL", envelope["status"]
    assert any("no input row for classes" in r
               for r in envelope["missing"]), envelope["missing"]


def test_the_classes_checked_are_the_v2_contract_classes() -> None:
    contract = json.loads(CLASS_CONTRACT.read_text())
    assert [row["class"] for row in contract["classes"]] == CLASSES


def test_a_refusal_still_writes_an_auditable_envelope() -> None:
    """A refusal with no artifact is a refusal nobody can audit."""
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp), skip={"HF_SYS_PTHAT_1"})
        assert (Path(tmp) / "systematics_envelope.json").is_file()
        assert not list(Path(tmp).glob("*.staging")), "a staging file survived"
    assert envelope["schema"] == "hadronization_systematics_envelope_v1"
    assert envelope["missing"], "a refusal must record its reason"
    assert proc.returncode != 0


def test_the_envelope_refuses_a_plotting_output_plane() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        report = base / "per_class_deltas.json"
        report.write_text(json.dumps(delta_report()))
        tags = base / "tags.json"
        tags.write_text(json.dumps(resolver_tags()))
        proc = subprocess.run(
            [sys.executable, str(TOOL), "--report", str(report),
             "--campaign", CAMPAIGN, "--nominal-dataset", DATASET,
             "--resolver-tags", str(tags),
             "--out", str(base / "plotting" / "envelope.json")],
            capture_output=True, text=True, check=False)
    assert proc.returncode != 0, proc.stdout
    assert "may not be written under a plotting" in proc.stderr, proc.stderr


def main() -> int:
    tests = [v for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"systematics envelope: {len(tests)} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
