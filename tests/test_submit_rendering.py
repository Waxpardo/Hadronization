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
        assert text.count("render_test,999,") == 3

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
