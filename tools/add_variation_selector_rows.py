#!/usr/bin/env python3
"""Add one dataset-selector row per closed variation campaign.

WHY THIS EXISTS. On 2026-08-19 five variation renders read the CENTRAL
campaign's data. The configurations were right; the sealed dataset selector
exports HADRONIZATION_COMPLETE_ROOT_TAG and the driver hands it to the macro,
where it wins. The selector is the authority, so a variation needs a row of its
own. Bypassing it with a direct environment override is forbidden: that is the
guard, and disabling a guard to get past it is how the central data got read in
the first place.

THE VARIATION ROWS ARE NOT PUBLICATION DATASETS. `publication_eligible` is
false and `status` says so. They are inputs to a systematic.

THE SEALED ROW MUST NOT MOVE. Its canonical digest is taken before and after,
and a difference aborts before anything is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SEALED = "hf_run3_v1_candidate"
# All seven registered variation campaigns. MUF_UP and PDF_CTEQ6L1 joined on
# 2026-08-20, when their merges closed at 3/3 markers.
CAMPAIGNS = ["HF_SYS_MUR_UP", "HF_SYS_MUR_DOWN",
             "HF_SYS_MUF_UP", "HF_SYS_MUF_DOWN",
             "HF_SYS_PTHAT_1", "HF_SYS_PTHAT_4",
             "HF_SYS_PDF_CTEQ6L1"]
BASE = "/data/alice/ipardoza"


def row_digest(row: dict) -> str:
    return hashlib.sha256(
        json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def key_for(campaign: str) -> str:
    return campaign.lower() + "_variation"


def build_row(campaign: str, template: dict, prereg_sha: str) -> dict:
    return {
        "campaign": campaign,
        "status": "systematic_variation",
        "publication_eligible": False,
        "complete_root_tag": f"complete_root_{campaign}",
        "subsample_base":
            f"{BASE}/hadronization_merged/SUBSAMPLES_{campaign}/combined_root_subSamples",
        "analyzed_data_base": f"{BASE}/hadronization_merged",
        "production_root": f"{BASE}/hadronization_production/{campaign}",
        "analysis_root": f"{BASE}/hadronization_analysis/{campaign}",
        "raw_base": f"{BASE}/hadronization_production/{campaign}/raw",
        "canonical_manifest":
            f"{BASE}/systematics_harvest/manifests/{campaign}/canonical_manifest.jsonl",
        # REQUIRED BY THE LOADER for every row, eligible or not
        # (tools/dataset_selector.py:56). The document these rows answer to is
        # the pre-registration that designed them, not a publication
        # authorization -- and `publication_eligible: false` above carries that
        # claim. Citing a real, hash-matching document is stricter than the
        # row-agreement test demands of a non-eligible row.
        "publication_authorization": "docs/SYSTEMATICS_PREREGISTRATION.md",
        "publication_authorization_sha256": prereg_sha,
        "block_count": template["block_count"],
        "raw_schema": template["raw_schema"],
        "selector": template["selector"],
        "interpretation": (
            f"{campaign} is a systematic variation of the sealed HF_RUN3_V1 "
            "physics campaign, at one tenth its exposure (10 M events per tune "
            "against 100 M). It exists to measure a systematic shift and is NOT "
            "a publication dataset: publication_eligible is false and no "
            "authorization is cited, deliberately. Its merged products carry "
            "three closure PASSes and 33 promoted legs. Added 2026-08-19 "
            "because the dataset selector, not the plotting configuration, is "
            "what the resolver reads -- see the run record's plumbing entry."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config-dir", type=Path, default=Path("config"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    combined_path = args.config_dir / "dataset_selector.json"
    combined = json.loads(combined_path.read_text())
    sealed_before = row_digest(combined["datasets"][SEALED])
    print(f"sealed row digest BEFORE: {sealed_before}")
    print(f"combined file sha256 BEFORE: "
          f"{hashlib.sha256(combined_path.read_bytes()).hexdigest()}")

    prereg = Path("docs/SYSTEMATICS_PREREGISTRATION.md")
    prereg_sha = hashlib.sha256(prereg.read_bytes()).hexdigest()
    print(f"pre-registration sha256: {prereg_sha}")
    template = combined["datasets"][SEALED]
    written = []
    for campaign in CAMPAIGNS:
        key = key_for(campaign)
        if key in combined["datasets"]:
            print(f"  {key}: already present, left alone")
            continue
        combined["datasets"][key] = build_row(campaign, template, prereg_sha)
        written.append(key)

    sealed_after = row_digest(combined["datasets"][SEALED])
    if sealed_after != sealed_before:
        raise SystemExit(
            f"ABORT: the sealed row changed.\n  before {sealed_before}\n"
            f"  after  {sealed_after}")
    print(f"sealed row digest AFTER:  {sealed_after}  UNCHANGED")

    if args.dry_run:
        print("dry run; nothing written")
        return 0

    combined_path.write_text(json.dumps(combined, indent=2) + "\n")
    print(f"combined file sha256 AFTER:  "
          f"{hashlib.sha256(combined_path.read_bytes()).hexdigest()}")

    for campaign in CAMPAIGNS:
        key = key_for(campaign)
        path = args.config_dir / f"dataset_selector_{campaign.lower()}.json"
        doc = {"schema": combined["schema"], "active_dataset": key,
               "datasets": {key: combined["datasets"][key]}}
        path.write_text(json.dumps(doc, indent=2) + "\n")
        print(f"  wrote {path.name} sha256="
              f"{hashlib.sha256(path.read_bytes()).hexdigest()[:16]}")
    print(f"rows added: {len(written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
