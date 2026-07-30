#!/usr/bin/env python3
"""Generate the immutable one-million and pTHat Gate-B pilot manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
ORIGIN_ALGORITHM = "signed_heavy_carrier_explicit_parent_event_unique_v2"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--campaign", default="HF_GATEB_primaryGround_pilot_v1")
    parser.add_argument("--campaign-ordinal", type=int, default=2)
    parser.add_argument("--seed-base", type=int, default=220_000_001)
    args = parser.parse_args()
    root = args.root.resolve()
    output = root / "campaigns" / args.campaign
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"refusing to alter nonempty pilot campaign: {output}")
    commit = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    dirty = bool(
        subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain"], text=True
        ).strip()
    )
    if dirty:
        raise SystemExit("refusing to generate Gate-B campaign from dirty repository")
    rows = []
    seeds = set()
    profiles = (
        (0, "1.0", 1_000_000, "long", "one_million_central"),
        (1, "0.5", 100_000, "medium", "pthat_sensitivity_low"),
        (2, "2.0", 100_000, "medium", "pthat_sensitivity_high"),
    )
    for tune_index, tune in enumerate(TUNES):
        for logical_id, pthat, events, category, purpose in profiles:
            seed = args.seed_base + tune_index * 10_000 + logical_id * 1_000
            if not 1 <= seed <= 900_000_000:
                raise ValueError(f"pilot seed outside PYTHIA domain: {seed}")
            if seed in seeds:
                raise AssertionError("pilot seed collision")
            seeds.add(seed)
            rows.append(
                {
                    "campaign": args.campaign,
                    "campaign_ordinal": args.campaign_ordinal,
                    "tune": tune,
                    "logical_id": logical_id,
                    "role": "pilot",
                    "attempt": 0,
                    "seed": seed,
                    "requested_successes": events,
                    "pthat_min_override": pthat,
                    "category": category,
                    "purpose": purpose,
                    "multiplicity_audit_events": 100,
                    "stable_name": f"hf_{tune}_job{logical_id:03d}.root",
                }
            )
    campaign = {
        "schema": "hf_gate_b_pilot_campaign_v1",
        "campaign": args.campaign,
        "campaign_ordinal": args.campaign_ordinal,
        "repository_implementation_commit": commit,
        "raw_schema": "hf_primary_ground_raw_v3",
        "selector": "hard_trigger_primary_ground__primary_ground_associate_v1",
        "origin_algorithm": ORIGIN_ALGORITHM,
        "species_registry_sha256": sha256(root / "config/heavy_flavour_species_v1.json"),
        "pair_registry_sha256": sha256(root / "config/heavy_flavour_pair_registry_v1.json"),
        "tune_allowlist_sha256": sha256(root / "config/tune_difference_allowlist_v1.json"),
        "card_sha256": {
            tune: sha256(
                root / "SimulationScripts" / f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
            )
            for tune in TUNES
        },
        "pilot_jobs": len(rows),
        "seed_base": args.seed_base,
        "purpose": "Gate B one-million logical pilots and pTHat threshold sensitivity",
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "campaign.json").write_text(
        json.dumps(campaign, indent=2, sort_keys=True) + "\n"
    )
    (output / "candidate_manifest.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )
    (output / "seed_ledger.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "campaign": row["campaign"],
                    "tune": row["tune"],
                    "logical_id": row["logical_id"],
                    "attempt": row["attempt"],
                    "seed": row["seed"],
                    "allocation": "gate_b_pilot",
                },
                sort_keys=True,
            )
            + "\n"
            for row in rows
        )
    )
    print(f"GATE_B_PILOT_MANIFEST jobs={len(rows)} unique_seeds={len(seeds)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
