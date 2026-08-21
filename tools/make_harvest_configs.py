#!/usr/bin/env python3
"""Generate one plotting configuration per variation campaign, from the central.

WHY THIS EXISTS. The five configurations under `plotting/harvest_configs/` were
produced by hand substitution and no generator was committed, so nothing checked
that they still agree with the central configuration they derive from. A
sixth and seventh campaign made that a live risk rather than a tidiness point:
a per-class delta compares a variation against the sealed nominal, and if the
two configurations differ anywhere except the campaign name, the comparison is
between two different quantities.

THE DERIVATION IS ROUTE-BOUND. Everything except the campaign route and output
names -- the eleven class windows, their evidence-derived labels, the canvases,
the pair contract, and the subsample count -- is copied from
`configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse_complete_root.json`
unchanged. Storage locations and complete-root tags come from each campaign's
active `config/dataset_selector_<campaign>.json` row. The nominal template is
checked against its own selector before any derived file is built. This makes
the selectors authoritative for routes and the central configuration
authoritative for the common observable and display contract.

    base_dir                              selector analyzed_data_base
    bb/cc complete_root_dir               selector complete_root_tag
    bb/cc complete_root_dir_sub_samples   selector subsample_base
    global write_path/write_name          <CAMPAIGN> substitution

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

def output_path(campaign: str) -> Path:
    return OUT_DIR / (f"configuration_multiplicity_{campaign}_THREETUNE"
                      "_THnSparse_complete_root.json")


def selected_dataset(campaign: str) -> dict:
    path = ROOT / "config" / f"dataset_selector_{campaign.lower()}.json"
    document = json.loads(path.read_text())
    key = document.get("active_dataset")
    datasets = document.get("datasets", {})
    if not isinstance(key, str) or key not in datasets:
        raise ValueError(f"{path}: active_dataset does not select one row")
    dataset = datasets[key]
    if dataset.get("campaign") != campaign:
        raise ValueError(
            f"{path}: selected campaign {dataset.get('campaign')!r} "
            f"does not match {campaign!r}"
        )
    return dataset


def expected_route(campaign: str) -> dict[str, str]:
    dataset = selected_dataset(campaign)
    return {
        "base_dir": dataset["analyzed_data_base"],
        "bb_bar_complete_root_dir": dataset["complete_root_tag"],
        "cc_bar_complete_root_dir": dataset["complete_root_tag"],
        "bb_bar_complete_root_dir_sub_samples": dataset["subsample_base"],
        "cc_bar_complete_root_dir_sub_samples": dataset["subsample_base"],
    }


def validate_route(config: dict, campaign: str) -> None:
    expected = expected_route(campaign)
    mismatches = {
        key: (config.get(key), value)
        for key, value in expected.items()
        if config.get(key) != value
    }
    if mismatches:
        raise ValueError(
            f"{campaign} plotting route differs from its active dataset "
            f"selector: {mismatches}"
        )


def build(campaign: str, central: dict) -> dict:
    """Copy the observable contract and bind the campaign's selected route."""
    config = json.loads(json.dumps(central))
    for key, value in expected_route(campaign).items():
        config[key] = value
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
    validate_route(central, NOMINAL)
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
