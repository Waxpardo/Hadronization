#!/usr/bin/env python3
"""Tests for reviewed historical seed-reservation baseline generation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/build_submission_registry_baseline.py"


def write_campaign(
    root: Path, name: str, ordinal: int, schema: str, seeds: list[int]
) -> Path:
    directory = root / name
    directory.mkdir()
    config = {
        "schema": schema,
        "campaign": name,
        "campaign_ordinal": ordinal,
    }
    if schema == "hf_campaign_v1":
        config.update(
            {
                "candidate_slots": {
                    "MONASH": 1,
                    "JUNCTIONS": 1,
                    "CLOSEPACKING": 1,
                },
                "max_attempts_per_logical_id": 10,
                "seed_base": seeds[0],
            }
        )
    rows = []
    for index, seed in enumerate(seeds):
        rows.append(
            {
                "campaign": name,
                "campaign_ordinal": ordinal,
                "tune": ("MONASH", "JUNCTIONS", "CLOSEPACKING")[
                    index % 3
                ],
                "logical_id": index // 3,
                "attempt": 0,
                "seed": seed,
            }
        )
    if schema == "hf_gate_b_pilot_campaign_v1":
        assert len(rows) == 9
    (directory / "campaign.json").write_text(
        json.dumps(config, sort_keys=True) + "\n"
    )
    text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    (directory / "candidate_manifest.jsonl").write_text(text)
    (directory / "seed_ledger.jsonl").write_text(text)
    return directory


def main() -> int:
    with tempfile.TemporaryDirectory(
        prefix="hadronization_registry_baseline_"
    ) as raw:
        temporary = Path(raw)
        full = write_campaign(
            temporary,
            "full_history",
            1,
            "hf_campaign_v1",
            [100, 110, 120],
        )
        gate = write_campaign(
            temporary,
            "gate_history",
            2,
            "hf_gate_b_pilot_campaign_v1",
            [100 + index for index in range(9)],
        )
        output = temporary / "registry" / "reservation_baseline.json"
        result = subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "--repository-identity",
                "github.com/waxpardo/hadronization",
                "--reviewer",
                "Baseline contract test",
                "--output",
                str(output),
                "--campaign-dir",
                str(full),
                "--campaign-dir",
                str(gate),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        assert "campaigns=2 overlaps=1" in result.stdout
        baseline = json.loads(output.read_text())
        assert baseline["historical_reservations"][0][
            "reserved_seed_intervals"
        ] == [[100, 129]]
        assert baseline["documented_historical_overlaps"] == [
            {
                "campaign_a": "full_history",
                "campaign_b": "gate_history",
                "overlap_intervals": [[100, 100], [101, 101], [102, 102],
                                      [103, 103], [104, 104], [105, 105],
                                      [106, 106], [107, 107], [108, 108]],
                "disposition":
                    "historical_collision_burn_all_overlapping_seeds",
            }
        ]
        second = subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "--repository-identity",
                "github.com/waxpardo/hadronization",
                "--reviewer",
                "Baseline contract test",
                "--output",
                str(output),
                "--campaign-dir",
                str(full),
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        assert second.returncode != 0
        assert "refusing to replace baseline" in second.stderr
    print("submission-registry baseline tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
