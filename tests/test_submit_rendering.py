#!/usr/bin/env python3
"""Regression tests for site-sensitive HTCondor submit rendering."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hadronization_submit_test_") as raw:
        temporary = Path(raw)
        campaign = temporary / "campaign"
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
                    "tune": tune,
                    "logical_id": tune_index,
                    "role": "pilot",
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
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/render_production_submit.py"),
                str(campaign),
                str(ROOT),
                str(output),
                "--roles",
                "pilot",
            ],
            check=True,
        )
        text = output.read_text()
        assert '+JobCategory = "$(CATEGORY)"' in text
        assert "+JobCategory = $(CATEGORY)" not in text
        assert (
            "HADRONIZATION_PTHAT_MIN_OVERRIDE=$(PTHAT) "
            "HADRONIZATION_STORE_MULTIPLICITY_AUDIT_EVENTS="
            "$(MULT_AUDIT_EVENTS)"
        ) in text
        assert "PTHAT);HADRONIZATION" not in text
        assert text.count("render_test,999,") == 3

        gate_b_campaign = temporary / "gate_b_campaign"
        gate_b_campaign.mkdir()
        (gate_b_campaign / "campaign.json").write_text(
            json.dumps(
                {
                    "schema": "hf_gate_b_pilot_campaign_v1",
                    "campaign": "gate_b_render_test",
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
        analysis_output = temporary / "gate_b_analysis.sub"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/render_gate_b_analysis_submit.py"),
                str(gate_b_campaign),
                str(ROOT),
                str(temporary / "production"),
                str(temporary / "analysis"),
                str(analysis_output),
            ],
            check=True,
        )
        analysis_text = analysis_output.read_text()
        assert '+JobCategory = "$(CATEGORY)"' in analysis_text
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
                str(temporary / "production"),
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
