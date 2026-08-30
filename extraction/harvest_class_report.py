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

STRICT CONTROL (`--strict-control`, default off).

`compare_rows` reports `agree: True` on any nonempty intersection with no
disagreement in a shared field. A nominal of 144 rows and a control of 132 that
share ONE row therefore agree, which is not what the control licenses. Strict
mode states the shape instead of inferring it: the identity set is DERIVED from
the closure configuration, the row counts follow from it and the class contract,
and `only_in_nominal` must be exactly the integrated-bin identities -- named,
not counted. Strict mode also closes the two boundary conditions the deep audit
found open at this seam:

  DA1-030  every row that feeds arithmetic carries block_count == 10 and ten
           block values. The shared parser accepts `>= 2` for non-publication
           utilities; ten blocks with SEM on dof 9 is the owner-fixed scheme
           (ruling R39) and belongs at the numerical-source boundary.
  DA1-031  `assert_resolved_campaign` runs on the nominal and on every variation
           log BEFORE any row is parsed. A log requested as one campaign and
           resolved from another was labelled by the request, not by the answer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest_class_axis import (INTEGRATED, agrees_at_recorded_precision,  # noqa: E402
                                assert_resolved_campaign, class_names,
                                class_order, parse_log)
from harvest_yield_deltas import (identical_row_sets, is_unresolved,  # noqa: E402
                                  relative_shift, significance,
                                  trigger_consistency, yield_delta)

ROOT = Path(__file__).resolve().parents[1]
CLOSURE_CONFIG = (ROOT / "plotting" /
                  "configuration_multiplicity_HF_RUN3_V1_VINTEGRATED_CLOSURE.json")
PAIR_REGISTRY = ROOT / "config" / "heavy_flavour_pair_registry_v1.json"
NOMINAL_CAMPAIGN = "HF_RUN3_V1"

COMPARED_FIELDS = ("central_yield", "yield_sem", "central_triggers")

# Ruling R39: pooled central, ten blocks, SEM on dof 9.
REQUIRED_BLOCK_COUNT = 10


class StrictControlRefusal(Exception):
    """A named refusal from strict CONTROL mode."""


def expected_identities(config: Path = CLOSURE_CONFIG,
                        registry: Path = PAIR_REGISTRY) -> set[tuple]:
    """(flavour, trigger, tune, associate) the render must carry.

    Derived exactly as the closure gate derives its identity set: PYTHIA_TUNES
    times every configured (trigger, associateOS) of both flavour blocks, with
    every configured OS filename resolved to exactly one pair-registry row. A
    count of twelve is satisfied by twelve wrong identities; this is the set.
    """
    document = json.loads(config.read_text())
    tunes = list(document["PYTHIA_TUNES"])
    if not tunes:
        raise StrictControlRefusal(f"{config.name} declares no PYTHIA_TUNES")

    rows_per_filename: dict[str, int] = {}
    for row in json.loads(registry.read_text())["pairs"]:
        name = row["filename"]
        rows_per_filename[name] = rows_per_filename.get(name, 0) + 1

    sections = {"BEAUTY": "beauty_correlations_to_analyse",
                "CHARM": "charm_correlations_to_analyse"}
    identities: set[tuple] = set()
    for flavour, section in sections.items():
        for group in document.get(section, []):
            for configured in group.get("configs", []):
                os_file = configured["OS"]
                found = rows_per_filename.get(os_file, 0)
                if found != 1:
                    raise StrictControlRefusal(
                        f"configured OS file {os_file!r} of {section} resolves "
                        f"to {found} pair-registry rows; exactly one is required")
                for tune in tunes:
                    identities.add((flavour, configured["trigger"], tune,
                                    configured["associateOS"]))
    if not identities:
        raise StrictControlRefusal(
            f"{config.name} registers no trigger/associate pair")
    return identities


def strict_control_shape(config: Path = CLOSURE_CONFIG,
                         registry: Path = PAIR_REGISTRY) -> dict:
    """The row counts and integrated identities strict mode requires.

    Every number here follows from the configuration and the class contract, so
    extending the pair set moves the expectation with it instead of leaving a
    literal behind. At the pin the configuration carries twelve identities and
    the contract eleven classes, which is the recorded 144 / 132 / 132 shape.
    """
    identities = expected_identities(config, registry)
    classes = len(class_names())
    return {
        "identities": identities,
        "classes": classes,
        "nominal_rows": len(identities) * (classes + 1),
        "control_rows": len(identities) * classes,
        "shared_rows": len(identities) * classes,
        "only_in_nominal": {identity + (INTEGRATED,) for identity in identities},
    }


def assert_strict_control(comparison: dict, shape: dict) -> None:
    """Refuse a control comparison that does not have the required shape."""
    complaints = []
    for field in ("nominal_rows", "control_rows", "shared_rows"):
        if comparison[field] != shape[field]:
            complaints.append(
                f"{field}: expected {shape[field]}, got {comparison[field]}")
    if comparison["disagreements"]:
        complaints.append(
            f"disagreements: expected 0, got {len(comparison['disagreements'])}")
    if comparison["only_in_control"]:
        complaints.append(
            f"only_in_control: expected none, got "
            f"{len(comparison['only_in_control'])}")
    observed = {tuple(key) for key in comparison["only_in_nominal"]}
    if observed != shape["only_in_nominal"]:
        missing = sorted(shape["only_in_nominal"] - observed)
        extra = sorted(observed - shape["only_in_nominal"])
        if missing:
            complaints.append(
                f"only_in_nominal is missing {len(missing)} integrated "
                f"identities, first {missing[0]}")
        if extra:
            complaints.append(
                f"only_in_nominal carries {len(extra)} identities the "
                f"configuration does not register, first {extra[0]}")
    if complaints:
        raise StrictControlRefusal("; ".join(complaints))


def assert_ten_blocks(rows: dict, campaign: str) -> None:
    """DA1-030: every row feeding arithmetic carries exactly ten blocks."""
    for key, row in rows.items():
        count = row.get("block_count")
        if count != REQUIRED_BLOCK_COUNT:
            raise StrictControlRefusal(
                f"{campaign} {key}: block_count is {count!r}, and the fixed "
                f"analysis requires {REQUIRED_BLOCK_COUNT}")
        for field in ("block_yields", "block_ratios"):
            values = row.get(field)
            if values is None:          # a reference row carries NA ratios
                continue
            if len(values) != REQUIRED_BLOCK_COUNT:
                raise StrictControlRefusal(
                    f"{campaign} {key}: {field} carries {len(values)} values, "
                    f"and {REQUIRED_BLOCK_COUNT} are required")
        triggers = str(row.get("block_triggers", "")).split(",")
        if len(triggers) != REQUIRED_BLOCK_COUNT:
            raise StrictControlRefusal(
                f"{campaign} {key}: block_triggers carries {len(triggers)} "
                f"values, and {REQUIRED_BLOCK_COUNT} are required")


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
    ap.add_argument("--strict-control", action="store_true",
                    help="require the derived CONTROL shape, ten blocks on "
                         "every arithmetic row, and a resolver assertion on "
                         "every input log")
    ap.add_argument("--strict-config", type=Path, default=CLOSURE_CONFIG,
                    help="configuration the strict identity set is derived "
                         "from (default: the tracked V-INTEGRATED closure "
                         "configuration)")
    ap.add_argument("--nominal-campaign", default=NOMINAL_CAMPAIGN,
                    help="campaign tag the nominal render must have resolved")
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
    nominal_text = nominal_path.read_text(errors="replace")
    # DA1-031. The configuration is a request; the resolver line is the answer.
    # Read the answer before parsing a single row, so a log that resolved
    # another campaign is refused rather than relabelled.
    if args.strict_control:
        assert_resolved_campaign(nominal_text, args.nominal_campaign)
    # New arithmetic requires the v2 block-vector contract. The accepted
    # historical render is parsed only for the three shared comparison fields.
    nominal = parse_log(nominal_text)
    control = parse_log(
        control_path.read_text(errors="replace"),
        validate_block_contract=False,
    )
    comparison = compare_rows(nominal, control)

    variations, delta_rows, checks = {}, [], count_checks(nominal, "NOMINAL")
    for spec in args.variation:
        campaign, _, path = spec.partition("=")
        variation_text = Path(path).read_text(errors="replace")
        if args.strict_control:
            assert_resolved_campaign(variation_text, campaign)
        rows = parse_log(variation_text)
        variations[campaign] = rows
        delta_rows += deltas_for(nominal, rows, campaign)
        checks += count_checks(rows, campaign)

    if args.strict_control:
        # The control is an accepted historical artifact parsed without the v2
        # contract, so the ten-block requirement lands on the rows that carry
        # arithmetic: the nominal and every variation.
        assert_ten_blocks(nominal, "NOMINAL")
        for campaign, rows in variations.items():
            assert_ten_blocks(rows, campaign)
        assert_strict_control(
            comparison, strict_control_shape(args.strict_config, PAIR_REGISTRY))

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
          f"disagreements={len(comparison['disagreements'])} "
          f"strict={'true' if args.strict_control else 'false'}")
    print(f"DELTAS rows={len(delta_rows)} campaigns={len(variations)} "
          f"flagged_below_2sem={flagged} relative_undefined={undefined}")
    print(f"TRIGGER_CONSISTENCY failures="
          f"{len(payload['trigger_consistency_failures'])}/{len(checks)}")
    print(f"IDENTICAL_CAMPAIGN_PAIRS {payload['identical_campaign_pairs']}")
    return 0 if comparison["agree"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
