#!/usr/bin/env python3
"""The V-FULL base configuration is the unguarded root of the generated tree.

WHAT THIS GUARDS, AND THE MEASUREMENT BEHIND IT (ledger DA1-015, BLOCKS_PAPER).

`plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE_POLISH_PROPOSAL.json`
is hand-maintained, 1668 lines, and every generated figure configuration is a
copy of it. No test in the repository named the file. The deep audit poisoned
its eleven class entries -- `triggerPtMin` 1.0 -> 0.5 -- regenerated the five
outputs, and ran every gate: `make_variant_configs.py --check` returned rc=0
`VARIANT_CONFIGS_CURRENT files=5` and the full suite returned 91/91 with zero
FAIL. `--check` compares the outputs against a fresh generation FROM THE SAME
BASE, so it cannot judge the base; with the poison in place but the outputs NOT
regenerated it correctly reported `VARIANT_CONFIGS_STALE count=1`, which is the
control that shows what it does measure. Evidence:
`DA1_EVIDENCE_2751e08_20260829/probes/C_vfull_base_config_unguarded.sh`.

WHAT IS ASSERTED. Two things, because either alone is passable.

  (a) CROSS-ENTRY AGREEMENT. The base repeats one selection block once per
      multiplicity class. Nothing in the ROOT stack requires the eleven to agree,
      so a hand-edit that gave one class a different pT or eta window would
      render and would look plausible. Every physics-facing key must therefore
      carry ONE value across all entries -- everything except the multiplicity
      window and the names derived from it.

  (b) PINNED VALUES. Agreement alone is satisfied by eleven identically wrong
      entries, which is exactly what the poison produced. The values are
      asserted literally, against the analysis constants the producer writes
      (analysis/status_analysis_THnSparse_qq.C:1314-1317) and the class contract
      ruling R10 makes the single source of the class set.

THE TWO PT MINIMA ARE DIFFERENT QUANTITIES, and conflating them would make this
test wrong. `associate_pt_min_exclusive` = 0.15 is the ANALYSIS selection; it
reaches the configuration through `pair_input_selection_contract`. The per-entry
`assocPtMin` is a PLOTTING re-cut over histograms already filled under that
selection (`histogram_pt_eta_fields: legacy_recuts_only_v1`), and it sits at 0.0
because a wider re-cut selects everything the analysis kept. What must never
happen is a re-cut TIGHTER than the analysis selection, which would silently
drop pairs the receipts still count, so that is the direction asserted.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = (ROOT / "plotting"
        / "configuration_multiplicity_HF_RUN3_V1_THREETUNE_POLISH_PROPOSAL.json")
CONTRACT = ROOT / "config" / "multiplicity_percentile_classes_v2.json"
ANALYSIS = ROOT / "analysis" / "status_analysis_THnSparse_qq.C"

# The analysis constants, pinned. The producer writes them into every merged
# object as TParameters, so a drift here is a drift from the data.
TRIGGER_PT_MIN = 1.0
ASSOCIATE_PT_MIN = 0.15
ETA_ABS_MAX = 4.0
SAME_SIGN_PAIR_FACTOR = 1.0

# Keys that must agree across all eleven class entries. The multiplicity window
# and the three names derived from it are what a class entry exists to vary.
PER_CLASS_KEYS = {"binLabel", "hDPhi", "hTrPt",
                  "multiplicityMin", "multiplicityMax"}

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def main() -> int:
    check("the V-FULL base configuration is committed", BASE.exists(), str(BASE))
    if not BASE.exists():
        return 1

    document = json.loads(BASE.read_text())
    entries = document["histograms_to_analyse"]
    contract_classes = json.loads(CONTRACT.read_text())["classes"]

    # --- the class set comes from the contract, in contract order ----------
    check("the base carries exactly the contract's classes",
          [e["binLabel"] for e in entries] == [c["bin"] for c in contract_classes],
          f"{[e['binLabel'] for e in entries]}")
    check(f"the base carries {len(contract_classes)} class entries",
          len(entries) == len(contract_classes), str(len(entries)))

    # --- (a) cross-entry agreement on every physics-facing key -------------
    shared = sorted(set(entries[0]) - PER_CLASS_KEYS)
    for key in shared:
        values = {json.dumps(entry[key], sort_keys=True) for entry in entries}
        check(f"all class entries agree on {key}", len(values) == 1,
              f"{len(values)} distinct: {sorted(values)[:4]}")

    # --- (b) the pinned values ---------------------------------------------
    first = entries[0]
    check("trigger pT minimum is the analysis constant",
          first["triggerPtMin"] == TRIGGER_PT_MIN,
          f"{first['triggerPtMin']} != {TRIGGER_PT_MIN}")
    check("the plotting re-cut never tightens the associate pT selection",
          first["assocPtMin"] <= ASSOCIATE_PT_MIN,
          f"{first['assocPtMin']} > {ASSOCIATE_PT_MIN}")
    for key in ("triggerEtaMin", "assocEtaMin"):
        check(f"{key} is -|eta| max", first[key] == -ETA_ABS_MAX, str(first[key]))
    for key in ("triggerEtaMax", "assocEtaMax"):
        check(f"{key} is +|eta| max", first[key] == ETA_ABS_MAX, str(first[key]))
    check("trigger pT window is ordered",
          first["triggerPtMin"] < first["triggerPtMax"],
          f"{first['triggerPtMin']}..{first['triggerPtMax']}")
    check("associate pT window is ordered",
          first["assocPtMin"] < first["assocPtMax"],
          f"{first['assocPtMin']}..{first['assocPtMax']}")

    check("the same-sign pair factor is 1.0",
          document["same_sign_pair_factor"] == SAME_SIGN_PAIR_FACTOR,
          str(document["same_sign_pair_factor"]))

    contract = document["pair_input_selection_contract"]
    for key, expected in (
        ("v3_trigger_pt_min_exclusive", TRIGGER_PT_MIN),
        ("v3_associate_pt_min_exclusive", ASSOCIATE_PT_MIN),
        ("v3_eta_abs_max_inclusive", ETA_ABS_MAX),
        ("v3_same_sign_pair_factor", SAME_SIGN_PAIR_FACTOR),
    ):
        check(f"the selection contract's {key} is the analysis constant",
              contract.get(key) == expected,
              f"{contract.get(key)!r} != {expected!r}")

    # --- the constants are the producer's own, not a second copy -----------
    analysis = ANALYSIS.read_text()
    for name, value in (("trigger_pt_min_exclusive", TRIGGER_PT_MIN),
                        ("associate_pt_min_exclusive", ASSOCIATE_PT_MIN),
                        ("eta_abs_max_inclusive", ETA_ABS_MAX),
                        ("same_sign_pair_factor", SAME_SIGN_PAIR_FACTOR)):
        check(f"the analysis writes {name} = {value}",
              f'"{name}", {value}' in analysis, name)

    # --- nothing is excluded from the drawn axis ---------------------------
    for canvas in document["canvases_to_be_drawn"]:
        check(f"{canvas['canvas_name']} ignores no multiplicity class",
              canvas["bins_to_ignore"] == [],
              str(canvas["bins_to_ignore"]))

    print()
    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    print(f"V-FULL base guarded: {len(entries)} class entries agree and carry "
          f"the analysis constants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
