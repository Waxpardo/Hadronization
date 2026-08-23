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
# Ruling R10: the fixture's class set is the contract's, so this test measures
# the tool against the contract rather than against a second copy of it.
CLASSES = [row["class"] for row in
           json.loads(CLASS_CONTRACT.read_text())["classes"]]

# campaign -> (variation_yield, variation_sem). Nominal is 100.0 +- 3.0.
# Chosen so that D2 and A1 both give exact values:
#   S1a  MUR_UP    delta +4, SEM(delta) = sqrt(4^2 + 3^2) = 5   -> SEM binds, 5
#   S1b  MUF_UP    delta +8, SEM(delta) = sqrt(0^2 + 3^2) = 3   -> |delta| binds, 8
#   S2   PDF       delta +6, SEM(delta) = sqrt(4^2 + 3^2) = 5   -> |delta| binds, 6
#   S3   PTHAT_4   delta +12, SEM(delta) = sqrt(4^2 + 3^2) = 5  -> |delta| binds, 12
# Section 9.1 then drops S2 because |muf| = 8 >= |pdf| = 6 and both exceed 0.1.
# Combined = sqrt(5^2 + 8^2 + 12^2) = sqrt(233).
#
# HF_SYS_PTHAT_1 is NOT here. Ruling R9 excludes that arm, so a fixture that
# supplied it would prove the tool works on inputs the contract forbids.
# EXCLUDED_ARM below is used only where a test needs the excluded name itself.
ARMS = {
    "HF_SYS_MUR_UP": (104.0, 4.0),
    "HF_SYS_MUR_DOWN": (97.0, 4.0),
    "HF_SYS_MUF_UP": (108.0, 0.0),
    "HF_SYS_MUF_DOWN": (94.0, 0.0),
    "HF_SYS_PDF_CTEQ6L1": (106.0, 4.0),
    "HF_SYS_PTHAT_4": (112.0, 4.0),
}
EXCLUDED_ARM = "HF_SYS_PTHAT_1"
EXCLUDED_SOURCE = "S5_class_migration"
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


def test_ruling_r9_excludes_one_arm_and_keeps_the_other() -> None:
    """S3 stays a source. One of its two arms leaves, with a reason."""
    sources = json.loads(SOURCES_CONTRACT.read_text())
    assert sources["schema"] == "hadronization_systematics_sources_v1"
    by_name = {row["source"]: row for row in sources["sources"]}
    s3 = by_name["S3_pthat"]
    assert s3["included"] is True
    by_campaign = {arm["campaign"]: arm for arm in s3["campaigns"]}
    assert by_campaign["HF_SYS_PTHAT_4"]["included"] is True
    assert by_campaign[EXCLUDED_ARM]["included"] is False
    assert by_campaign[EXCLUDED_ARM]["exclusion_reason"] == (
        "R9: empty 80-90% class from a discrete tie on the percentile axis; "
        "S3 quoted one-sided as measured")
    absent = {row["source"] for row in sources["declared_absent"]}
    assert {"S4_counter_window", "S6_unresolved_origin",
            "tune_bundle_spread"} <= absent


def test_ruling_r11_excludes_s5_and_does_not_delete_it() -> None:
    """An excluded source with a recorded reason, still declared."""
    sources = json.loads(SOURCES_CONTRACT.read_text())
    by_name = {row["source"]: row for row in sources["sources"]}
    assert EXCLUDED_SOURCE in by_name, "R11 excludes S5; it does not delete it"
    assert by_name[EXCLUDED_SOURCE]["included"] is False
    assert by_name[EXCLUDED_SOURCE]["exclusion_reason"] == (
        "R11: unresolved; re-derivation on the percentile axis pending")


def test_every_exclusion_records_a_reason() -> None:
    """The rule the builder enforces, asserted on the tracked contract."""
    sources = json.loads(SOURCES_CONTRACT.read_text())
    for row in sources["sources"]:
        if not row["included"]:
            assert row.get("exclusion_reason", "").strip(), row["source"]
        for arm in row["campaigns"]:
            assert isinstance(arm, dict), row["source"]
            if not arm["included"]:
                assert arm.get("exclusion_reason", "").strip(), arm["campaign"]


def test_the_source_contract_agrees_with_the_arithmetic() -> None:
    """Per arm. The included arms are exactly what the arithmetic quotes."""
    sys.path.insert(0, str(ROOT / "extraction"))
    from combine_per_class import CAMPAIGNLESS_TERMS, SOURCES  # noqa: E402
    sources = json.loads(SOURCES_CONTRACT.read_text())
    declared = {
        row["source"]: tuple(a["campaign"] for a in row["campaigns"]
                             if a["included"])
        for row in sources["sources"] if row["included"]
    }
    campaignless = {name for name, kept in declared.items() if not kept}
    assert {n: k for n, k in declared.items() if k} == SOURCES, (declared,
                                                                 SOURCES)
    assert campaignless == set(CAMPAIGNLESS_TERMS), campaignless
    assert SOURCES["S3_pthat"] == ("HF_SYS_PTHAT_4",), (
        "R9 quotes S3 one-sided as measured")


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


def test_the_envelope_records_its_exclusions_with_their_reasons() -> None:
    """R9 and R11 must be readable in the artifact, not only in a commit."""
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert envelope["status"] == "COMPLETE", envelope["missing"]
    by_key = {(e["source"], e["campaign"]): e["reason"]
              for e in envelope["exclusions"]}
    assert by_key[("S3_pthat", EXCLUDED_ARM)].startswith("R9:"), by_key
    assert by_key[(EXCLUDED_SOURCE, None)].startswith("R11:"), by_key
    assert all(reason.strip() for reason in by_key.values()), by_key


def test_an_excluded_source_produces_no_term() -> None:
    """R11: S5 enters no budget, so no row may carry a number for it."""
    with tempfile.TemporaryDirectory() as tmp:
        _, envelope = run(Path(tmp))
    for row in envelope["rows"]:
        assert EXCLUDED_SOURCE not in row["terms"], row["class"]
        assert EXCLUDED_SOURCE not in row["quoted_arm"], row["class"]


def test_an_excluded_arm_is_never_quoted() -> None:
    """R9: S3 is one-sided as measured, from HF_SYS_PTHAT_4 alone."""
    with tempfile.TemporaryDirectory() as tmp:
        _, envelope = run(Path(tmp))
    for row in envelope["rows"]:
        for name, term in row["terms"].items():
            assert term["campaign"] != EXCLUDED_ARM, (row["class"], name)
        assert row["quoted_arm"]["S3_pthat"] == "HF_SYS_PTHAT_4", row["class"]


def test_the_excluded_arm_needs_no_receipt() -> None:
    """The envelope completes without any HF_SYS_PTHAT_1 input at all."""
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert envelope["status"] == "COMPLETE", envelope["missing"]
    assert EXCLUDED_ARM not in envelope["provenance"]["measurement_receipts"]
    assert not any(EXCLUDED_ARM in reason for reason in envelope["missing"])


# ---- the refusals ---------------------------------------------------------

def test_a_missing_receipt_for_an_INCLUDED_source_still_refuses() -> None:
    """Excluding one arm must not soften the gate on the arms that remain."""
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp), skip={"HF_SYS_PTHAT_4"})
    assert proc.returncode != 0, proc.stdout
    assert envelope["status"] == "INCOMPLETE", envelope["status"]
    assert any("HF_SYS_PTHAT_4" in r for r in envelope["missing"]), envelope
    assert envelope["rows"] == [] or envelope["status"] != "COMPLETE"


def test_every_included_arm_is_gated_one_at_a_time() -> None:
    """One mutation per arm. A gate never seen to fail is not known to be one."""
    for campaign in ARMS:
        with tempfile.TemporaryDirectory() as tmp:
            proc, envelope = run(Path(tmp), skip={campaign})
        assert proc.returncode != 0, (campaign, proc.stdout)
        assert envelope["status"] == "INCOMPLETE", (campaign, envelope["status"])
        assert any(campaign in r for r in envelope["missing"]), campaign


def test_a_fail_receipt_refuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp), fail={"HF_SYS_PTHAT_4"})
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


def test_the_class_labels_follow_the_c_number_convention() -> None:
    """The count comes from the contract; the naming convention is pinned."""
    contract = json.loads(CLASS_CONTRACT.read_text())
    names = [row["class"] for row in contract["classes"]]
    assert names == [f"c{i}" for i in range(1, len(names) + 1)], names


def test_the_envelope_derives_its_row_count_from_the_class_contract() -> None:
    """R10: no constant may stand in for the class count."""
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    provenance = envelope["provenance"]
    assert provenance["class_contract_classes"] == CLASSES
    assert provenance["expected_rows"] == len(CLASSES)
    assert len(envelope["rows"]) == provenance["expected_rows"]


def test_two_complete_series_give_twice_the_rows() -> None:
    """The derived count follows the series, not a number written down."""
    report = delta_report()
    report["deltas"] += [{**row, "associate": "B-"}
                         for row in list(report["deltas"])]
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp), report=report)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert envelope["provenance"]["expected_rows"] == 2 * len(CLASSES)
    assert len(envelope["rows"]) == 2 * len(CLASSES)


def test_one_series_short_of_one_class_refuses() -> None:
    """A second series missing one class. The whole-report check cannot see it."""
    dropped = CLASSES[-1]
    report = delta_report()
    report["deltas"] += [{**row, "associate": "B-"}
                         for row in list(report["deltas"])
                         if row["class"] != dropped]
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp), report=report)
    assert proc.returncode != 0, proc.stdout
    assert envelope["status"] == "FAIL", envelope["status"]
    assert any(dropped in reason and "B-" in reason
               for reason in envelope["missing"]), envelope["missing"]


def test_a_refusal_still_writes_an_auditable_envelope() -> None:
    """A refusal with no artifact is a refusal nobody can audit."""
    with tempfile.TemporaryDirectory() as tmp:
        proc, envelope = run(Path(tmp), skip={"HF_SYS_PTHAT_4"})
        assert (Path(tmp) / "systematics_envelope.json").is_file()
        assert not list(Path(tmp).glob("*.staging")), "a staging file survived"
    assert envelope["schema"] == "hadronization_systematics_envelope_v1"
    assert envelope["missing"], "a refusal must record its reason"
    assert proc.returncode != 0


def _builder():
    sys.path.insert(0, str(ROOT / "tools"))
    sys.path.insert(0, str(ROOT / "extraction"))
    import systematics_envelope  # noqa: E402
    return systematics_envelope


def test_an_exclusion_that_records_no_reason_is_refused() -> None:
    """Synthetic contract. An unreasoned exclusion is the failure to prevent."""
    builder = _builder()
    for contract, expected in (
            ({"sources": [{"source": "S9", "included": False,
                           "campaigns": []}]}, "source S9 is excluded"),
            ({"sources": [{"source": "S9", "included": True, "campaigns": [
                {"campaign": "HF_SYS_A", "included": True},
                {"campaign": "HF_SYS_B", "included": False}]}]},
             "arm HF_SYS_B of source S9 is excluded")):
        recorded, unreasoned = builder.exclusions(contract)
        assert recorded, contract
        assert any(expected in problem for problem in unreasoned), unreasoned

    ok = {"sources": [{"source": "S9", "included": False, "campaigns": [],
                       "exclusion_reason": "R99: because the owner said so"}]}
    recorded, unreasoned = builder.exclusions(ok)
    assert unreasoned == [], unreasoned
    assert recorded == [{"source": "S9", "campaign": None,
                         "reason": "R99: because the owner said so"}]


def test_a_source_whose_every_arm_is_excluded_is_refused() -> None:
    """An included source with no measured arm cannot contribute a term."""
    builder = _builder()
    problems = builder.agrees_with_combination_map(
        {"sources": [{"source": "S3_pthat", "included": True, "campaigns": [
            {"campaign": "HF_SYS_PTHAT_4", "included": False,
             "exclusion_reason": "synthetic"},
            {"campaign": "HF_SYS_PTHAT_1", "included": False,
             "exclusion_reason": "synthetic"}]}]})
    assert any("every one of its arms is excluded" in p for p in problems), \
        problems


def test_a_contract_that_readmits_the_excluded_arm_is_refused() -> None:
    """The drift check is per arm, so a two-sided S3 no longer agrees."""
    builder = _builder()
    problems = builder.agrees_with_combination_map(
        {"sources": [
            {"source": "S1a_mur", "included": True, "campaigns": [
                {"campaign": "HF_SYS_MUR_UP", "included": True},
                {"campaign": "HF_SYS_MUR_DOWN", "included": True}]},
            {"source": "S1b_muf", "included": True, "campaigns": [
                {"campaign": "HF_SYS_MUF_UP", "included": True},
                {"campaign": "HF_SYS_MUF_DOWN", "included": True}]},
            {"source": "S2_pdf", "included": True, "campaigns": [
                {"campaign": "HF_SYS_PDF_CTEQ6L1", "included": True}]},
            {"source": "S3_pthat", "included": True, "campaigns": [
                {"campaign": "HF_SYS_PTHAT_4", "included": True},
                {"campaign": EXCLUDED_ARM, "included": True}]}]})
    assert any("S3_pthat maps to" in p for p in problems), problems


def test_the_tracked_contract_passes_its_own_drift_check() -> None:
    builder = _builder()
    contract = json.loads(SOURCES_CONTRACT.read_text())
    assert builder.agrees_with_combination_map(contract) == []
    _, unreasoned = builder.exclusions(contract)
    assert unreasoned == []


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
