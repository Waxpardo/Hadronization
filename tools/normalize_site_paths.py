#!/usr/bin/env python3
"""Remove account-specific Nikhef paths from tracked JSON configuration."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLACEMENTS = {
    "/data/alice/ipardoza/hf": "${HADRONIZATION_DATA_ROOT}",
    "/data/alice/ipardoza/a2_variation_largest":
        "${HADRONIZATION_DATA_ROOT}/scratch/a2_variation_largest",
    "/data/alice/ipardoza/a2_variation":
        "${HADRONIZATION_DATA_ROOT}/scratch/a2_variation",
    "campaigns/HF_RUN3_V1/freeze/canonical_manifest.jsonl":
        "${HADRONIZATION_DATA_ROOT}/project/runs/HF_RUN3_V1/freeze/"
        "canonical_manifest.jsonl",
    "campaigns/HF_PT2_INT/freeze/canonical_manifest.jsonl":
        "${HADRONIZATION_DATA_ROOT}/project/runs/HF_PT2_INT/freeze/"
        "canonical_manifest.jsonl",
    "campaigns/HF_PT2/freeze/canonical_manifest.jsonl":
        "${HADRONIZATION_DATA_ROOT}/project/runs/HF_PT2/freeze/"
        "canonical_manifest.jsonl",
    "freeze at campaigns/HF_RUN3_V1/freeze/":
        "freeze under HADRONIZATION_DATA_ROOT/project/runs/HF_RUN3_V1/freeze/",
    "The four cluster-resident paths are absolute because the merged product "
    "lives outside the checkout; this row is therefore Nikhef-specific by "
    "construction.":
        "The data routes are resolved through HADRONIZATION_DATA_ROOT by the "
        "selected site profile.",
    "The four cluster-resident paths are absolute because the merged product "
    "lives outside the checkout, so this row is Nikhef-specific by "
    "construction.":
        "The data routes are resolved through HADRONIZATION_DATA_ROOT by the "
        "selected site profile.",
    "The four paths are absolute because the merged product lives outside the "
    "checkout, so this row is Nikhef-specific by construction.":
        "The data routes are resolved through HADRONIZATION_DATA_ROOT by the "
        "selected site profile.",
}


def paths() -> list[Path]:
    result = sorted((ROOT / "config").glob("*.json"))
    result += sorted((ROOT / "plotting").glob("configuration_*.json"))
    result += sorted((ROOT / "plotting" / "harvest_configs").glob("*.json"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale: list[Path] = []
    changed: list[Path] = []
    for path in paths():
        before = path.read_text()
        after = before
        for old, new in REPLACEMENTS.items():
            after = after.replace(old, new)
        if after == before:
            continue
        if args.check:
            stale.append(path)
        else:
            path.write_text(after)
            changed.append(path)
    if stale:
        for path in stale:
            print(f"SITE_PATH_STALE {path.relative_to(ROOT)}")
        return 1
    print("SITE_PATHS_CURRENT" if args.check
          else f"SITE_PATHS_NORMALIZED files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
