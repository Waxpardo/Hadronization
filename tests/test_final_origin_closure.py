#!/usr/bin/env python3
"""Focused aggregation tests for sealed-final origin/closure evidence."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/final_origin_closure.py"
SPEC = importlib.util.spec_from_file_location(
    "final_origin_closure", MODULE_PATH
)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def payload(tune: str, slot: int, unresolved_triggers: int = 0) -> dict:
    metadata = {
        "audit_schema": module.EXPECTED_AUDIT_SCHEMA,
        "raw_schema": "hf_primary_ground_raw_v6",
        "selector": "hard_trigger_primary_ground__primary_ground_associate_v1",
        "origin_algorithm":
            "signed_heavy_constituent_complete_mothers_unique_v4",
        "species_registry_schema": "heavy_flavour_species_v1",
        "species_registry_sha256": "a" * 64,
        "tune": tune,
        "primary_all_heavy_match_schema": "primary_all_heavy_match_v1",
        "primary_all_heavy_closure_schema":
            module.EXPECTED_CLOSURE_SCHEMA,
        "raw_input_sha256": f"{slot + 1:064x}",
        "raw_validation_receipt_sha256": f"{slot + 2:064x}",
        "role_definition":
            "associate=0;trigger_candidate_before_origin_requirement=1",
        "weight_definition":
            "unweighted=count;weighted=sum(event_weight);sumw2=sum(event_weight^2)",
        "axis_policy":
            "pt<=7000;abs(eta)<=4;0<=Nch<=4095;inclusive physical endpoints",
    }
    origin_rows = [
        {
            "tune": tune,
            "sector": "charm",
            "species": "Dplus",
            "role_name": "trigger_candidate",
            "origin_name": "selected_hard",
            "resolution_name": "unique",
            "role": 1,
            "hard_channel": 4,
            "pdg": 411,
            "origin": 1,
            "resolution": 1,
            "candidates": 10,
            "sum_weights": 10.0,
            "sum_weights2": 10.0,
        }
    ]
    if unresolved_triggers:
        origin_rows.append(
            {
                "tune": tune,
                "sector": "charm",
                "species": "Dplus",
                "role_name": "trigger_candidate",
                "origin_name": "unresolved",
                "resolution_name": "missing_carrier",
                "role": 1,
                "hard_channel": 4,
                "pdg": 411,
                "origin": 0,
                "resolution": 3,
                "candidates": unresolved_triggers,
                "sum_weights": float(unresolved_triggers),
                "sum_weights2": float(unresolved_triggers),
            }
        )
    closure_rows = []
    for category, label in module.CLOSURE_CATEGORIES.items():
        count = 10 if category == 0 else 0
        closure_rows.append(
            {
                "closure_schema": module.EXPECTED_CLOSURE_SCHEMA,
                "tune": tune,
                "sector": "charm",
                "trigger_species": "Dplus",
                "category_name": label,
                "hard_channel": 4,
                "multiplicity_nch": 20,
                "trigger_pdg": 411,
                "category": category,
                "count": count,
                "denominator_count": 10,
                "sum_weights": float(count),
                "denominator_sum_weights": 10.0,
            }
        )
    return {
        "input": {
            "tune": tune,
            "canonical_slot": slot,
            "raw_path": f"/production/{tune}/{slot}.root",
            "raw_sha256": metadata["raw_input_sha256"],
            "raw_validation_receipt_path":
                f"/production/{tune}/{slot}.json",
            "raw_validation_receipt_sha256":
                metadata["raw_validation_receipt_sha256"],
            "audit_path": f"/audit/{tune}/{slot}.root",
            "audit_sha256": "b" * 64,
            "audit_log_path": f"/audit/{tune}/{slot}.log",
            "audit_log_sha256": "c" * 64,
        },
        "metadata": metadata,
        "origin_rows": origin_rows,
        "closure_rows": closure_rows,
    }


class FinalOriginClosureAggregationTest(unittest.TestCase):
    def freeze(self) -> dict:
        return {
            "canonical_manifest_sha256": "d" * 64,
            "freeze_seal_sha256": "e" * 64,
            "jobs_per_tune": 1,
            "repository_commit": subprocess.check_output(
                ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                text=True,
            ).strip(),
        }

    def materialize_inputs(
        self, rows: list[dict], directory: Path
    ) -> None:
        contracts = json.loads(
            (ROOT / "config/statistical_robustness_v1.json").read_text()
        )["contracts"]
        for row in rows:
            tune = row["input"]["tune"]
            slot = row["input"]["canonical_slot"]
            row["metadata"]["species_registry_sha256"] = contracts[
                "species_registry_sha256"
            ]
            for path_key, hash_key in (
                ("raw_path", "raw_sha256"),
                (
                    "raw_validation_receipt_path",
                    "raw_validation_receipt_sha256",
                ),
                ("audit_path", "audit_sha256"),
                ("audit_log_path", "audit_log_sha256"),
            ):
                suffix = Path(str(row["input"][path_key])).suffix
                artifact = (
                    directory
                    / tune
                    / f"slot_{slot:03d}_{path_key}{suffix}"
                )
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_text(f"{tune}/{slot}/{path_key}\n")
                row["input"][path_key] = artifact.resolve().as_posix()
                row["input"][hash_key] = module.robustness.sha256(artifact)
            row["metadata"]["raw_input_sha256"] = row["input"][
                "raw_sha256"
            ]
            row["metadata"]["raw_validation_receipt_sha256"] = row[
                "input"
            ]["raw_validation_receipt_sha256"]

    def test_complete_zero_unresolved_final_manifest_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            rows = [
                payload(tune, 0)
                for tune in module.robustness.EXPECTED_TUNES
            ]
            self.materialize_inputs(rows, directory)
            freeze = self.freeze()
            report = module.aggregate_payloads(
                rows,
                freeze,
                module.robustness.sha256(
                    ROOT / "Validation/AuditOriginResolution.C"
                ),
                freeze["repository_commit"],
            )
            self.assertEqual(report["completion_state"], "PASS")
            self.assertEqual(report["publication_readiness"], "READY")
            self.assertEqual(report["audited_job_count"], 3)
            self.assertEqual(report["closure_base_count"], 3)
            self.assertEqual(
                report["unresolved_trigger_candidate_count"], 0
            )
            body = dict(report)
            claimed = body.pop("payload_sha256")
            self.assertEqual(claimed, module.robustness.json_sha256(body))

            path = directory / "report.json"
            path.write_text(json.dumps(report))
            binding = (
                module.robustness.validate_final_origin_closure_report(
                    path,
                    freeze,
                    ROOT,
                    json.loads(
                        (
                            ROOT
                            / "config/statistical_robustness_v1.json"
                        ).read_text()
                    ),
                )
            )
            self.assertEqual(binding["audited_job_count"], 3)

    def test_nonzero_final_trigger_unresolved_blocks_readiness(self) -> None:
        rows = [
            payload(tune, 0, unresolved_triggers=1 if tune == "MONASH" else 0)
            for tune in module.robustness.EXPECTED_TUNES
        ]
        report = module.aggregate_payloads(
            rows, self.freeze(), "f" * 64, "1" * 40
        )
        self.assertEqual(
            report["completion_state"], "NEEDS_FINAL_PHYSICS_REVIEW"
        )
        self.assertEqual(report["publication_readiness"], "BLOCKED")
        self.assertEqual(report["unresolved_trigger_candidate_count"], 1)

    def test_missing_canonical_slot_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "every canonical tune/slot"):
            module.aggregate_payloads(
                [payload("MONASH", 0)],
                self.freeze(),
                "f" * 64,
                "1" * 40,
            )


if __name__ == "__main__":
    unittest.main()
