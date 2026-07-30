#!/usr/bin/env python3
"""Regression tests for site-sensitive HTCondor submit rendering."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hadronization_submit_test_") as raw:
        temporary = Path(raw)
        campaign = temporary / "render_test"
        campaign.mkdir()
        (campaign / "campaign.json").write_text(
            json.dumps({"campaign": "render_test", "campaign_ordinal": 999}) + "\n"
        )
        rows = []
        for tune_index, tune in enumerate(
            ("MONASH", "JUNCTIONS", "CLOSEPACKING")
        ):
            rows.append(
                {
                    "campaign": "render_test",
                    "campaign_ordinal": 999,
                    "tune": tune,
                    "logical_id": tune_index,
                    "role": "reserve",
                    "attempt": 0,
                    "seed": 880_000_001 + tune_index,
                    "requested_successes": 10,
                    "category": "long",
                    "pthat_min_override": "1.0",
                    "multiplicity_audit_events": 10,
                }
            )
        (campaign / "candidate_manifest.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in rows)
        )
        output = temporary / "pilot.sub"
        producer = ROOT / "SimulationScripts/heavyflavourcorrelations_status"
        producer_sha = (
            hashlib.sha256(producer.read_bytes()).hexdigest()
            if producer.is_file()
            else "0" * 64
        )
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/render_production_submit.py"),
                str(campaign),
                str(ROOT),
                str(output),
                "--roles",
                "reserve",
                "--producer-executable-sha256",
                producer_sha,
            ],
            check=True,
        )
        text = output.read_text()
        assert '+JobCategory = "$(CATEGORY)"' in text
        assert "+JobCategory = $(CATEGORY)" not in text
        assert "getenv = False" in text
        assert "getenv = True" not in text
        assert "$(PTHAT) $(MULT_AUDIT_EVENTS)" in text
        assert "$(EFFECTIVE_CARD_SHA256)" in text
        assert "$(PRODUCER_EXECUTABLE_SHA256)" in text
        assert text.count("render_test,999,") == 3

        gate_b_campaign = temporary / "gate_b_render_test"
        gate_b_campaign.mkdir()
        (gate_b_campaign / "campaign.json").write_text(
            json.dumps(
                {
                    "schema": "hf_gate_b_pilot_campaign_v1",
                    "campaign": "gate_b_render_test",
                    "raw_schema": "hf_primary_ground_raw_v7",
                    "origin_algorithm":
                        "signed_heavy_constituent_complete_mothers_unique_v4",
                }
            )
            + "\n"
        )
        gate_b_rows = []
        for tune in ("MONASH", "JUNCTIONS", "CLOSEPACKING"):
            for logical_id, category in ((0, "long"), (1, "medium"), (2, "medium")):
                gate_b_rows.append(
                    {
                        "tune": tune,
                        "logical_id": logical_id,
                        "category": category,
                        "purpose": (
                            "one_million_central"
                            if logical_id == 0
                            else "pthat_sensitivity"
                        ),
                        "stable_name": f"hf_{tune}_job{logical_id:03d}.root",
                    }
                )
        (gate_b_campaign / "candidate_manifest.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in gate_b_rows)
        )
        production = temporary / "production"
        for row in gate_b_rows:
            raw_file = (
                production
                / "raw"
                / row["tune"]
                / row["stable_name"]
            )
            raw_file.parent.mkdir(parents=True, exist_ok=True)
            raw_file.write_bytes(
                f"{row['tune']}:{row['logical_id']}\n".encode()
            )
            digest = hashlib.sha256(raw_file.read_bytes()).hexdigest()
            Path(f"{raw_file}.sha256").write_text(
                f"{digest}  {raw_file.name}\n"
            )
        analysis_output = temporary / "gate_b_analysis.sub"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/render_gate_b_analysis_submit.py"),
                str(gate_b_campaign),
                str(ROOT),
                str(production),
                str(temporary / "analysis"),
                str(analysis_output),
            ],
            check=True,
        )
        analysis_text = analysis_output.read_text()
        assert '+JobCategory = "$(CATEGORY)"' in analysis_text
        assert "getenv = False" in analysis_text
        assert "getenv = True" not in analysis_text
        assert (
            "arguments = $(RAW_PATH) $(OUTPUT_DIRECTORY) $(CAMPAIGN) $(TUNE) "
            "$(LOGICAL_ID) $(RAW_SHA256)"
        ) in analysis_text
        assert "HADRONIZATION_BASE=" in analysis_text
        assert 'arguments = "$(RAW_PATH)"' not in analysis_text
        assert analysis_text.count(",job_") == 0
        assert analysis_text.count(".root,") == 9
        assert "per_pthat/MONASH/job_000" in analysis_text
        assert "per_pthat/CLOSEPACKING/job_002" in analysis_text
        sensitivity_output = temporary / "gate_b_sensitivity_analysis.sub"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/render_gate_b_analysis_submit.py"),
                str(gate_b_campaign),
                str(ROOT),
                str(production),
                str(temporary / "analysis"),
                str(sensitivity_output),
                "--scope",
                "sensitivity",
            ],
            check=True,
        )
        sensitivity_text = sensitivity_output.read_text()
        assert sensitivity_text.count(".root,") == 6
        assert "job000.root" not in sensitivity_text

        unsafe = subprocess.run(
            [
                str(ROOT / "runCondorJob.sh"),
                "--campaign",
                "unsafe/name",
                "999",
                "MONASH",
                "0",
                "pilot",
                "0",
                "880000001",
                "10",
                "1.0",
                "10",
                subprocess.check_output(
                    ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
                ).strip(),
                "0" * 64,
                "0" * 64,
                "12345",
                "0",
            ],
            text=True,
            capture_output=True,
        )
        assert unsafe.returncode == 2
        assert "campaign may contain only" in unsafe.stderr

        for submitter in ("submit_gate_b_pilots.sh", "submit_full_production.sh"):
            submitter_text = (ROOT / submitter).read_text()
            assert 'tools/build_producer.sh" "${project_base}"' in submitter_text
    print("submit-rendering tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
