#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/dataset_selector.py"
SELECTOR = ROOT / "config/dataset_selector.json"


def main() -> int:
    result = subprocess.run(
        # The combined selector declares no active_dataset by design, so the
        # dataset must be named. See tests/test_dataset_selector_requires_a_named_dataset.py.
        [sys.executable, str(TOOL), "validate", "--selector", str(SELECTOR),
         "--dataset", "legacy_21_06_2026"],
        check=True,
        text=True,
        capture_output=True,
    )
    assert "active=legacy_21_06_2026" in result.stdout
    shell = subprocess.run(
        [sys.executable, str(TOOL), "shell", "--selector", str(SELECTOR),
         "--dataset", "legacy_21_06_2026"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    assert "HADRONIZATION_COMPLETE_ROOT_TAG=complete_root_21_06_2026" in shell
    assert "HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE=false" in shell
    assert "HADRONIZATION_SUBSAMPLE_BASE=" in shell
    assert "HADRONIZATION_CANONICAL_MANIFEST=''" in shell
    assert "HADRONIZATION_PRODUCTION_ROOT=''" in shell
    assert "HADRONIZATION_ANALYSIS_ROOT=''" in shell

    payload = json.loads(SELECTOR.read_text())
    canonical = {
        **payload["datasets"]["legacy_21_06_2026"],
        "status": "canonical",
        "publication_eligible": True,
        "campaign": "HF_PUBLICATION_TEST",
        "raw_schema": "hf_primary_ground_raw_v7",
        "selector":
            "hard_trigger_primary_ground__primary_ground_associate_v1",
        "canonical_manifest":
            "Production/HF_PUBLICATION_TEST/freeze/canonical_manifest.jsonl",
        "production_root": "Production/HF_PUBLICATION_TEST",
        "analysis_root": "AnalysisOutput/HF_PUBLICATION_TEST",
        "raw_base": "Production/HF_PUBLICATION_TEST",
        "complete_root_tag": "HF_PUBLICATION_TEST",
        "subsample_base":
            "AnalyzedData/SUBSAMPLES_HF_PUBLICATION_TEST/"
            "combined_root_subSamples",
    }
    payload["datasets"]["canonical_test"] = canonical
    payload["active_dataset"] = "canonical_test"
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "canonical.json"
        path.write_text(json.dumps(payload))
        # The publication-authorization assertions that stood here tested
        # the gate layer's authorisation chain, which has been removed.
        # A canonical row must still validate on schema and selector.
        subprocess.run(
            [sys.executable, str(TOOL), "validate", "--selector", str(path)],
            check=True, text=True, capture_output=True,
        )

        candidate_payload = json.loads(json.dumps(payload))
        candidate_payload["datasets"]["canonical_test"].update(
            {
                "status": "canonical_candidate",
                "publication_eligible": False,
                "publication_authorization": None,
                "publication_authorization_sha256": None,
            }
        )
        candidate = Path(directory) / "candidate.json"
        candidate.write_text(json.dumps(candidate_payload))
        candidate_result = subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "shell",
                "--selector",
                str(candidate),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        assert "HADRONIZATION_DATASET_STATUS=canonical_candidate" in (
            candidate_result.stdout
        )
        assert "HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE=false" in (
            candidate_result.stdout
        )

    payload = json.loads(SELECTOR.read_text())
    payload["datasets"]["bad"] = {
        **payload["datasets"]["legacy_21_06_2026"],
        "status": "canonical",
        "publication_eligible": True,
        "campaign": None,
    }
    payload["active_dataset"] = "bad"
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "bad.json"
        path.write_text(json.dumps(payload))
        failed = subprocess.run(
            [sys.executable, str(TOOL), "validate", "--selector", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        assert failed.returncode != 0

    payload = json.loads(SELECTOR.read_text())
    payload["datasets"]["bad_legacy"] = {
        **payload["datasets"]["legacy_21_06_2026"],
        "publication_eligible": True,
    }
    payload["active_dataset"] = "bad_legacy"
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "bad-legacy.json"
        path.write_text(json.dumps(payload))
        failed = subprocess.run(
            [sys.executable, str(TOOL), "validate", "--selector", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        assert failed.returncode != 0
    print("dataset-selector tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
