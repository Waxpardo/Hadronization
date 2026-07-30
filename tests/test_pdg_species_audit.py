#!/usr/bin/env python3
import csv
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/pdg_2025_species_audit.py"
REGISTRY = ROOT / "config/heavy_flavour_species_v1.json"
REFERENCE = ROOT / "config/pdg_2025_species_reference_v1.json"


def run_check(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), "check", *arguments],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def make_pythia_csv(path: Path) -> None:
    registry = json.loads(REGISTRY.read_text())
    reference = json.loads(REFERENCE.read_text())
    states = {int(row["pdg"]): row for row in registry["signed_states"]}
    evidence = {
        int(row["signed_pdg"]): row for row in reference["signed_species"]
    }
    fields = [
        "pdg",
        "registry_name",
        "pythia_name",
        "pythia_conjugate_name",
        "sector",
        "kind",
        "charge3",
        "spin2j1",
        "is_hadron",
        "is_meson",
        "is_baryon",
        "has_antiparticle",
        "n_down_in_code",
        "n_up_in_code",
        "n_strange_in_code",
        "n_charm_in_code",
        "n_beauty_in_code",
        "decoded_qc",
        "decoded_qb",
        "mass_gev",
        "pythia_result",
    ]
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for pdg in states:
            state = states[pdg]
            mass = evidence[pdg]["mass"]["value_gev"]
            constituents = evidence[pdg]["operational_numbering"]["constituents"]
            counts = {
                flavour: sum(
                    token.removesuffix("bar") == flavour
                    for token in constituents
                )
                for flavour in ("d", "u", "s", "c", "b")
            }
            writer.writerow(
                {
                    "pdg": pdg,
                    "registry_name": state["name"],
                    "pythia_name": state["name"],
                    "pythia_conjugate_name": states[-pdg]["name"],
                    "sector": state["sector"],
                    "kind": state["kind"],
                    "charge3": state["charge3"],
                    "spin2j1": state["spin2j1"],
                    "is_hadron": 1,
                    "is_meson": int(state["kind"] == "meson"),
                    "is_baryon": int(state["kind"] == "baryon"),
                    "has_antiparticle": 1,
                    "n_down_in_code": counts["d"],
                    "n_up_in_code": counts["u"],
                    "n_strange_in_code": counts["s"],
                    "n_charm_in_code": counts["c"],
                    "n_beauty_in_code": counts["b"],
                    "decoded_qc": state["qc"],
                    "decoded_qb": state["qb"],
                    "mass_gev": mass if mass is not None else 5.9,
                    "pythia_result": "PASS",
                }
            )


def load_gate_module():
    path = ROOT / "tools/run_publication_gate_a.py"
    spec = importlib.util.spec_from_file_location("run_publication_gate_a", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def restore_permissions(path: Path) -> None:
    for item in sorted(path.rglob("*"), key=lambda value: len(value.parts)):
        if item.is_dir():
            os.chmod(item, 0o700)
        else:
            os.chmod(item, 0o600)
    os.chmod(path, 0o700)


def main() -> int:
    reference = json.loads(REFERENCE.read_text())
    assert reference["schema"] == "pdg_2025_heavy_flavour_species_reference_v1"
    assert reference["sources"]["sqlite"]["sha256"] == (
        "4f1ecd7d9a55bc05f61618cc4574053c1edc6188fab07bb4bb7ebed69f9ec6d3"
    )
    assert reference["sources"]["mass_width"]["sha256"] == (
        "24df41d7db48d8be875dbc8f69aab95fdf26a0512cd8c033cef2d73cc92c24ef"
    )
    rows = {
        int(row["signed_pdg"]): row for row in reference["signed_species"]
    }
    assert len(rows) == 50
    assert rows[5212]["official_particle"]["official_mcid"] == 5212
    assert rows[5212]["mass"]["status"] == "NO_MEASURED_PDG_2025_MASS"
    assert rows[5212]["classification"]["experimental_state_status"] == (
        "UNMEASURED_MODEL_PREDICTION"
    )
    assert rows[5212]["classification"]["generator_mass_status"] == (
        "QUARK_MODEL_OR_PYTHIA_ONLY"
    )
    assert rows[5312]["official_particle"]["official_mcid"] is None
    assert rows[5312]["official_particle"]["pdgid"] == "B169"
    assert rows[5312]["mass"]["status"] == "MEASURED_PDG_2025"
    assert rows[5312]["classification"]["official_mcid_status"] == (
        "NO_OFFICIAL_MCID"
    )
    assert rows[5322]["official_particle"] is None
    assert rows[5322]["mass"]["status"] == "NO_MEASURED_PDG_2025_MASS"
    assert rows[5322]["classification"]["experimental_state_status"] == (
        "NO_DIRECTLY_LISTED_MEASURED_STATE"
    )

    static = run_check()
    assert static.returncode == 2, static.stderr
    static_report = json.loads(static.stdout)
    assert static_report["state"] == "NEEDS_PHYSICS_REVIEW"
    assert static_report["publication_gate_a_pass"] is False
    assert static_report["owner_signoff_present"] is False
    assert static_report["technical_failures"] == []
    assert {
        int(row["abs_pdg"]) for row in static_report["review_issues"]
    } == {5212, 5312, 5322}

    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        protected_reference = temporary / "protected-reference.json"
        protected_bytes = b'{"sentinel":"must-not-change"}\n'
        protected_reference.write_bytes(protected_bytes)
        failed_extract = subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "extract",
                "--sqlite",
                str(temporary / "missing.sqlite"),
                "--mass-width",
                str(temporary / "missing-mass-width.txt"),
                "--output",
                str(protected_reference),
                "--check",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        assert failed_extract.returncode == 1
        assert protected_reference.read_bytes() == protected_bytes

        pythia_csv = temporary / "pythia.csv"
        report_path = temporary / "report.json"
        make_pythia_csv(pythia_csv)
        result = run_check(
            "--pythia-csv",
            str(pythia_csv),
            "--require-pythia",
            "--output",
            str(report_path),
        )
        assert result.returncode == 2, result.stderr
        report = json.loads(report_path.read_text())
        assert report["state"] == "NEEDS_PHYSICS_REVIEW"
        assert report["technical_failures"] == []
        assert all(
            row["state"] in {"PASS", "NEEDS_PHYSICS_REVIEW"}
            for row in report["signed_species"]
        )

        csv_rows = list(csv.DictReader(pythia_csv.open(newline="")))
        next(row for row in csv_rows if int(row["pdg"]) == 421)["charge3"] = "3"
        with pythia_csv.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=csv_rows[0].keys())
            writer.writeheader()
            writer.writerows(csv_rows)
        failed = run_check(
            "--pythia-csv", str(pythia_csv), "--require-pythia"
        )
        assert failed.returncode == 1
        failed_report = json.loads(failed.stdout)
        assert failed_report["state"] == "FAIL"
        assert any(
            "PYTHIA audit charge3 mismatch" in failure
            for failure in failed_report["technical_failures"]
        )

        tampered_reference = temporary / "reference.json"
        tampered = json.loads(REFERENCE.read_text())
        tampered["sources"]["sqlite"]["sha256"] = "0" * 64
        tampered_reference.write_text(json.dumps(tampered) + "\n")
        failed = run_check("--reference", str(tampered_reference))
        assert failed.returncode == 1
        assert json.loads(failed.stdout)["state"] == "FAIL"

    gate = load_gate_module()
    assert (
        "Validation/TestPlotReferenceMultiplicityContracts.C",
        "TestPlotReferenceMultiplicityContracts()",
    ) in gate.ROOT_TESTS
    with tempfile.TemporaryDirectory() as directory:
        report_path = Path(directory) / "pdg_report.json"
        try:
            gate.validate_species_pdg_report(
                report_path, review_required=True
            )
        except RuntimeError as error:
            assert "did not create" in str(error)
        else:
            raise AssertionError("missing PDG report was accepted")
        exact_review = {
            "schema": "hf_species_registry_pdg_audit_v1",
            "state": "NEEDS_PHYSICS_REVIEW",
            "publication_gate_a_pass": False,
            "physics_review_required": True,
            "owner_signoff_present": False,
            "owner_signoff_authored_or_inferred": False,
            "technical_failures": [],
        }
        report_path.write_text(json.dumps(exact_review) + "\n")
        gate.validate_species_pdg_report(
            report_path, review_required=True
        )
        del exact_review["publication_gate_a_pass"]
        report_path.write_text(json.dumps(exact_review) + "\n")
        try:
            gate.validate_species_pdg_report(
                report_path, review_required=True
            )
        except RuntimeError as error:
            assert "exact NEEDS_PHYSICS_REVIEW" in str(error)
        else:
            raise AssertionError("incomplete PDG review report was accepted")
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "gate"
        output.mkdir()
        runner = gate.GateRunner(output, development=True)
        try:
            with redirect_stdout(StringIO()):
                runner.run(
                    "synthetic-review",
                    [sys.executable, "-c", "raise SystemExit(2)"],
                    review_returncode=2,
                )
        except gate.PhysicsReviewRequired as error:
            runner.physics_review_required = str(error)
        else:
            raise AssertionError("review return code was not fail-closed")
        with redirect_stdout(StringIO()):
            returncode = runner.finish()
        report = json.loads((output / "gate_a_report.json").read_text())
        assert returncode == 2
        assert report["state"] == "NEEDS_PHYSICS_REVIEW"
        assert report["publication_gate_a_pass"] is False
        restore_permissions(output)

    macro = (ROOT / "Validation/AuditSpeciesRegistry.C").read_text()
    assert "pythia_conjugate_name" in macro
    assert "mass_gev" in macro
    print("PDG species audit tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
