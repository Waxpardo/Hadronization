#!/usr/bin/env python3
"""Control comparison and per-class deltas from measurement render logs.

INPUTS. One new nominal measurement log, one accepted historical control log,
and one log per variation campaign. New numerical inputs require the v2 block
contract. The historical log is parsed only for shared-field reproduction.
Every log is keyed on (flavour, trigger, tune, associate, class).

THE CONTROL LICENSES THE ARITHMETIC. Every shared row must agree at the
precision the logs record, with NO tolerance. The historical control supplies
no endpoint, covariance, count, or systematic arithmetic.

THE DELTAS follow the registered definition: Delta = variation - nominal, SEMs in
quadrature, flagged below 2 SEM. See `harvest_yield_deltas`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest_class_axis import (agrees_at_recorded_precision, class_order,  # noqa: E402
                                parse_log)
from harvest_yield_deltas import (identical_row_sets, is_unresolved,  # noqa: E402
                                  relative_shift, significance,
                                  trigger_consistency, yield_delta)

COMPARED_FIELDS = ("central_yield", "yield_sem", "central_triggers")


def compare_rows(nominal: dict, control: dict) -> dict:
    """Row-by-row agreement between two renders of the same sealed data."""
    shared = sorted(set(nominal) & set(control), key=lambda k: (k[:4], class_order(k[4])))
    disagreements = []
    for key in shared:
        for field in COMPARED_FIELDS:
            a, b = nominal[key][field], control[key][field]
            if not agrees_at_recorded_precision(a, b):
                disagreements.append({"key": list(key), "field": field,
                                      "nominal": a, "control": b})
    return {
        "nominal_rows": len(nominal),
        "control_rows": len(control),
        "shared_rows": len(shared),
        "only_in_nominal": [list(k) for k in sorted(set(nominal) - set(control))],
        "only_in_control": [list(k) for k in sorted(set(control) - set(nominal))],
        "disagreements": disagreements,
        "agree": bool(shared) and not disagreements,
    }


def deltas_for(nominal: dict, variation: dict, campaign: str) -> list[dict]:
    """One delta row per shared identity."""
    shared = sorted(set(nominal) & set(variation),
                    key=lambda k: (k[:4], class_order(k[4])))
    rows = []
    for key in shared:
        n, v = nominal[key], variation[key]
        n_y, n_s = float(n["central_yield"]), float(n["yield_sem"])
        v_y, v_s = float(v["central_yield"]), float(v["yield_sem"])
        delta, sem = yield_delta(v_y, v_s, n_y, n_s)
        rel = relative_shift(delta, n_y)
        rows.append({
            "campaign": campaign,
            "flavour": key[0], "trigger": key[1], "tune": key[2],
            "associate": key[3], "class": key[4],
            "nominal_yield": n_y, "nominal_sem": n_s,
            "variation_yield": v_y, "variation_sem": v_s,
            "delta": delta, "delta_sem": sem,
            "significance": significance(delta, sem),
            "flagged_below_2sem": is_unresolved(delta, sem),
            "relative_shift_percent": rel,
            "relative_shift_undefined": rel is None,
            "nominal_status": n["status"], "variation_status": v["status"],
        })
    return rows


def count_checks(rows: dict, campaign: str) -> list[dict]:
    """Trigger-count consistency for every row of one render."""
    out = []
    for key, row in rows.items():
        tokens = row["block_triggers"].split(",")
        blocks = [float(x) for x in tokens]
        check = trigger_consistency(float(row["central_triggers"]), blocks,
                                    tokens)
        check.update({"campaign": campaign, "key": list(key),
                      "finite_yields": row.get("finite_yields")})
        out.append(check)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nominal", type=Path, required=True)
    ap.add_argument("--control", type=Path, required=True)
    ap.add_argument("--variation", action="append", default=[],
                    metavar="CAMPAIGN=LOG")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    nominal_path = args.nominal.resolve()
    control_path = args.control.resolve()
    nominal_digest = hashlib.sha256(nominal_path.read_bytes()).hexdigest()
    control_digest = hashlib.sha256(control_path.read_bytes()).hexdigest()
    if nominal_path == control_path or nominal_digest == control_digest:
        raise ValueError(
            "the new nominal numerical source and historical reproduction "
            "control must be different files with different digests"
        )
    # New arithmetic requires the v2 block-vector contract. The accepted
    # historical render is parsed only for the three shared comparison fields.
    nominal = parse_log(nominal_path.read_text(errors="replace"))
    control = parse_log(
        control_path.read_text(errors="replace"),
        validate_block_contract=False,
    )
    comparison = compare_rows(nominal, control)

    variations, delta_rows, checks = {}, [], count_checks(nominal, "NOMINAL")
    for spec in args.variation:
        campaign, _, path = spec.partition("=")
        rows = parse_log(Path(path).read_text(errors="replace"))
        variations[campaign] = rows
        delta_rows += deltas_for(nominal, rows, campaign)
        checks += count_checks(rows, campaign)

    payload = {
        "schema": "hadronization_per_class_delta_v1",
        "control_comparison": comparison,
        "deltas": delta_rows,
        "trigger_consistency": checks,
        "trigger_consistency_failures":
            [c for c in checks if not c["agrees"]],
        "identical_campaign_pairs": identical_row_sets(variations),
        "campaigns": sorted(variations),
    }
    args.out.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")

    flagged = sum(1 for r in delta_rows if r["flagged_below_2sem"])
    undefined = sum(1 for r in delta_rows if r["relative_shift_undefined"])
    print(f"CONTROL shared={comparison['shared_rows']} "
          f"agree={comparison['agree']} "
          f"disagreements={len(comparison['disagreements'])}")
    print(f"DELTAS rows={len(delta_rows)} campaigns={len(variations)} "
          f"flagged_below_2sem={flagged} relative_undefined={undefined}")
    print(f"TRIGGER_CONSISTENCY failures="
          f"{len(payload['trigger_consistency_failures'])}/{len(checks)}")
    print(f"IDENTICAL_CAMPAIGN_PAIRS {payload['identical_campaign_pairs']}")
    return 0 if comparison["agree"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
