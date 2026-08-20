#!/usr/bin/env python3
"""Generate one plotting configuration per variation campaign, from the central.

WHY THIS EXISTS. The five configurations under `plotting/harvest_configs/` were
produced by hand substitution and no generator was committed, so nothing checked
that they still agree with the central configuration they derive from. A
sixth and seventh campaign made that a live risk rather than a tidiness point:
a per-class delta compares a variation against the sealed nominal, and if the
two configurations differ anywhere except the campaign name, the comparison is
between two different quantities.

THE DERIVATION IS SIX FIELDS. Everything else -- the eleven class windows, the
canvases, the pair contract, the subsample count -- is copied from
`configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse_complete_root.json`
unchanged, which is what makes the class axis identical across campaigns.

    bb_bar_complete_root_dir              complete_root_<CAMPAIGN>
    cc_bar_complete_root_dir              complete_root_<CAMPAIGN>
    bb_bar_complete_root_dir_sub_samples  .../SUBSAMPLES_<CAMPAIGN>/...
    cc_bar_complete_root_dir_sub_samples  .../SUBSAMPLES_<CAMPAIGN>/...
    global write_path                     plotting/Plots/THnSparseCompleteRoot_<CAMPAIGN>
    global write_name                     global_balancing_plots_multiplicity_<CAMPAIGN>_THREETUNE

`--check` regenerates and compares, so a hand-edit of a derived configuration is
a suite failure rather than a discovery months later.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENTRAL = ROOT / ("plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE"
                  "_THnSparse_complete_root.json")
OUT_DIR = ROOT / "plotting/harvest_configs"
NOMINAL = "HF_RUN3_V1"

CAMPAIGNS = [
    "HF_SYS_MUR_UP", "HF_SYS_MUR_DOWN",
    "HF_SYS_MUF_UP", "HF_SYS_MUF_DOWN",
    "HF_SYS_PTHAT_1", "HF_SYS_PTHAT_4",
    "HF_SYS_PDF_CTEQ6L1",
]

# The committed derived files carry one-space indentation, the same as the
# central configuration they come from. Preserved so a regeneration is a no-op.
INDENT = 1

SUBSTITUTED_KEYS = ("bb_bar_complete_root_dir", "cc_bar_complete_root_dir",
                    "bb_bar_complete_root_dir_sub_samples",
                    "cc_bar_complete_root_dir_sub_samples")


def output_path(campaign: str) -> Path:
    return OUT_DIR / (f"configuration_multiplicity_{campaign}_THREETUNE"
                      "_THnSparse_complete_root.json")


def build(campaign: str, central: dict) -> dict:
    """The central configuration with the campaign name substituted, and only that."""
    config = json.loads(json.dumps(central))
    for key in SUBSTITUTED_KEYS:
        config[key] = central[key].replace(NOMINAL, campaign)
    for canvas in config["global_canvases_to_be_drawn"]:
        canvas["write_path"] = canvas["write_path"].replace(NOMINAL, campaign)
        canvas["write_name"] = canvas["write_name"].replace(NOMINAL, campaign)
    return config


def rendered(campaign: str, central: dict) -> str:
    return json.dumps(build(campaign, central), indent=INDENT) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="regenerate and compare rather than write")
    args = ap.parse_args()

    central = json.loads(CENTRAL.read_text())
    stale, written = [], []
    for campaign in CAMPAIGNS:
        path, payload = output_path(campaign), rendered(campaign, central)
        if args.check:
            if not path.exists():
                stale.append(f"{path.name}: missing")
            elif path.read_text() != payload:
                stale.append(f"{path.name}: differs from generated")
        else:
            if not path.exists() or path.read_text() != payload:
                path.write_text(payload)
                written.append(path.name)

    if args.check:
        if stale:
            for line in stale:
                print(f"HARVEST_CONFIG_STALE {line}")
            return 1
        print(f"HARVEST_CONFIGS_CURRENT files={len(CAMPAIGNS)}")
        return 0
    print(f"HARVEST_CONFIGS_WRITTEN files={len(written)}/{len(CAMPAIGNS)}"
          + (" " + " ".join(written) if written else " (all already current)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
