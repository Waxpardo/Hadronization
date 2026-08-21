#!/usr/bin/env python3
"""S5: the decay-daughter class-migration systematic, by re-projection.

The production decay policy disables heavy-hadron decays, whose daughters an
experimental primary definition would count. Measured cost on the PRODUCTION
generator: 0.767 % (results/validation/generator/NCH_DECAY_POLICY_BIAS_8317.md -- dN_ch/deta
7.040 under the experimental convention against 6.986 under the production
policy, 200k events per arm, paired on one seed). So the production counter
UNDERCOUNTS N_ch by that much, and the question this answers is what that does to
a per-class observable.

WHY THE INPUT WAS RE-MEASURED. The 8.315 value was 1.327 % (7.007 vs 6.914,
NCH_CALIBRATION_20260730.md), and against the 1.538 % that would move c11's edge
at N_ch = 32.5 that left a margin of only 1.16 -- a 16 % margin, on a superseded
generator version, carrying an entire systematic source. Re-measured on 8.317 the
bias is 42 % smaller and the margin is a factor of 2.01. The superseded values are
kept below so the change is visible rather than silently absorbed.

  tools/systematic_class_migration.py

THE TRANSFORMATION. A relative bias delta on N_ch is equivalent, at fixed
class definition, to dividing every boundary by (1 + delta): an event the
experiment would call N*(1+delta) is called N here, so the boundary that would
have sat at b sits at b/(1+delta). Both signs are run, because the bias is a
measured MEAN shift whose spread is unmeasured and the sign of its effect on a
class edge is not the sign of the bias itself.

WHY THIS IS A RE-PROJECTION AND NOT A RE-ANALYSIS. Class membership is a
function of N_ch alone, and N_ch is a COUNT -- an integer, necessarily. The
committed boundaries sit at half-integers, which the boundary artifact states is
deliberate: "half-integer, so no integer N_ch is ambiguous about which class it
falls in". A per-class observable is therefore a sum over a set of integer N_ch
bins, and moving a boundary changes that observable ONLY if the move crosses an
integer. That makes the systematic exactly computable rather than estimable, and
this tool computes it and then checks the answer against real committed data.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BOUNDARY_ARTIFACT = REPO / "config/multiplicity_class_boundaries_v1.json"
MB_ANCHORS = REPO / "AnalysisScripts/anchors/b4_multiplicity_mb"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")

# results/validation/generator/NCH_DECAY_POLICY_BIAS_8317.md, recomputed from the two
# measured figures rather than transcribed as a percentage. PYTHIA 8.317, which
# is what production runs.
NCH_EXPERIMENTAL_CONVENTION = 7.040
NCH_PRODUCTION_POLICY = 6.986

# The PYTHIA 8.315 comparison gave 1.327% bias and only 1.16 margin at c11.
SUPERSEDED_8315_EXPERIMENTAL_CONVENTION = 7.007
SUPERSEDED_8315_PRODUCTION_POLICY = 6.914


def measured_bias() -> float:
    return (
        NCH_EXPERIMENTAL_CONVENTION - NCH_PRODUCTION_POLICY
    ) / NCH_EXPERIMENTAL_CONVENTION


def superseded_8315_bias() -> float:
    return (
        SUPERSEDED_8315_EXPERIMENTAL_CONVENTION
        - SUPERSEDED_8315_PRODUCTION_POLICY
    ) / SUPERSEDED_8315_EXPERIMENTAL_CONVENTION


def boundaries() -> list[float]:
    return [
        float(entry["boundary_nch"])
        for entry in json.loads(BOUNDARY_ARTIFACT.read_text())["classes"]
    ]


def class_labels() -> list[str]:
    return [
        str(entry["class"])
        for entry in json.loads(BOUNDARY_ARTIFACT.read_text())["classes"]
    ]


def mb_distribution(tune: str) -> dict[int, int]:
    with (MB_ANCHORS / f"nch_mb_{tune}.csv").open() as stream:
        return {
            int(row["nch"]): int(float(row["count"]))
            for row in csv.DictReader(stream)
        }


def assign(nch: int, edges: list[float]) -> int:
    """Class index for one integer N_ch. Class k spans [edge_k, edge_k+1)."""
    index = -1
    for position, edge in enumerate(edges):
        if nch >= edge:
            index = position
        else:
            break
    return index


def integer_partition(edges: list[float], nch_max: int) -> dict[int, int]:
    return {nch: assign(nch, edges) for nch in range(0, nch_max + 1)}


def populations(dist: dict[int, int], edges: list[float]) -> list[int]:
    counts = [0] * len(edges)
    for nch, count in dist.items():
        index = assign(nch, edges)
        if index >= 0:
            counts[index] += count
    return counts


def crossing_margin(edge: float) -> float:
    """The smallest |relative shift| of this edge that crosses an integer.

    An edge at a half-integer is 0.5 from each neighbouring integer, so it must
    move by 0.5 in absolute terms. Relative to the edge that is 0.5/|edge|.
    """
    if edge == 0.0:
        return 0.0
    return 0.5 / abs(edge)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        help="write the machine-readable result here as JSON",
    )
    args = parser.parse_args()

    delta = measured_bias()
    edges = boundaries()
    labels = class_labels()
    # b -> b/(1+delta) is the down arm: an experimental boundary expressed in
    # production N_ch. b/(1-delta) is the up arm.
    arms = {
        "down": [edge / (1.0 + delta) for edge in edges],
        "up": [edge / (1.0 - delta) for edge in edges],
    }

    nch_max = max(max(mb_distribution(tune)) for tune in TUNES)

    print(f"MEASURED BIAS delta = {delta:.6f}  ({100 * delta:.4f} %)  [PYTHIA 8.317]")
    print(f"  from dN_ch/deta {NCH_EXPERIMENTAL_CONVENTION} (experimental "
          f"convention) vs {NCH_PRODUCTION_POLICY} (production policy)")
    print(f"  superseded 8.315 value was {100 * superseded_8315_bias():.4f} % "
          f"-- see results/validation/generator/NCH_DECAY_POLICY_BIAS_8317.md")
    print(f"integer N_ch range covered by the committed MB samples: 0..{nch_max}")
    print()

    print("BOUNDARY MOVES, and the margin to the nearest integer")
    print(f"{'class':>6} {'nominal':>9} {'down':>9} {'up':>9} "
          f"{'move':>7} {'margin':>8} {'crosses?':>9}")
    rows = []
    for index, edge in enumerate(edges):
        down, up = arms["down"][index], arms["up"][index]
        move = max(abs(down - edge), abs(up - edge))
        margin = crossing_margin(edge)
        crosses = (
            math.floor(down) != math.floor(edge)
            or math.floor(up) != math.floor(edge)
        )
        rows.append(
            {
                "class": labels[index],
                "nominal": edge,
                "down": down,
                "up": up,
                "absolute_move": move,
                "relative_margin_to_integer": margin,
                "crosses_an_integer": crosses,
            }
        )
        print(f"{labels[index]:>6} {edge:>9.4f} {down:>9.4f} {up:>9.4f} "
              f"{move:>7.4f} {100 * margin:>7.2f}% {str(crosses):>9}")
    print()

    # ---- the exact statement: does the integer partition change at all? ----
    nominal_partition = integer_partition(edges, nch_max)
    identical = {}
    for arm, shifted in arms.items():
        shifted_partition = integer_partition(shifted, nch_max)
        moved = {
            nch: (nominal_partition[nch], shifted_partition[nch])
            for nch in nominal_partition
            if nominal_partition[nch] != shifted_partition[nch]
        }
        identical[arm] = not moved
        print(
            f"ARM {arm:>4}: integers reassigned = {len(moved)}"
            + ("" if not moved else f"  {sorted(moved)}")
        )
    print()

    # ---- the check on real data: per-class populations, nominal vs shifted --
    print("PER-CLASS POPULATIONS from the committed MB samples "
          "(the check, not the argument)")
    per_tune = {}
    for tune in TUNES:
        dist = mb_distribution(tune)
        nominal_counts = populations(dist, edges)
        arm_counts = {
            arm: populations(dist, shifted) for arm, shifted in arms.items()
        }
        deltas = {
            arm: [
                0.0
                if nominal_counts[index] == 0
                else (counts[index] - nominal_counts[index])
                / nominal_counts[index]
                for index in range(len(edges))
            ]
            for arm, counts in arm_counts.items()
        }
        per_tune[tune] = {
            "total_events": sum(dist.values()),
            "nominal": nominal_counts,
            "arms": arm_counts,
            "relative_delta": deltas,
        }
        worst = max(
            abs(value) for values in deltas.values() for value in values
        )
        moved_classes = [
            labels[index]
            for index in range(len(edges))
            if any(
                arm_counts[arm][index] != nominal_counts[index] for arm in arms
            )
        ]
        print(
            f"  {tune:>13}: {sum(dist.values())} events, "
            f"classes whose population moved = {len(moved_classes)}"
            + (f" {moved_classes}" if moved_classes else "")
            + f", max |relative delta| = {worst:.3e}"
        )
    print()

    structural_null = all(identical.values()) and all(
        arm_counts[index] == payload["nominal"][index]
        for payload in per_tune.values()
        for arm_counts in payload["arms"].values()
        for index in range(len(edges))
    )

    smallest_margin = min(crossing_margin(edge) for edge in edges)
    largest_edge = max(edges)
    bias_that_would_move_something = crossing_margin(largest_edge)

    print("VERDICT")
    if structural_null:
        print("  Every class is STRUCTURALLY INSENSITIVE. Delta(c) = 0 exactly,")
        print("  in every class, in both arms, for all three tunes -- because")
        print("  the shifted boundaries select an IDENTICAL set of integer N_ch")
        print("  bins, so the projection operator is unchanged.")
        print("  Block SEMs are exactly zero: the per-block difference is")
        print("  identically zero for any block decomposition, since the same")
        print("  operator is applied to the same events. This is an exact zero,")
        print("  not an estimate consistent with zero.")
    else:
        print("  NOT a structural null -- at least one class moved. The "
              "prediction in the pre-registration is FALSIFIED and the "
              "re-projection must be carried through with block SEMs.")
    print()
    print(f"  The null holds by a margin: the widest boundary is "
          f"{largest_edge:g}, which needs a relative shift of "
          f"{100 * bias_that_would_move_something:.2f} % to cross an integer,")
    print(f"  against the measured {100 * delta:.4f} % -- a factor "
          f"{bias_that_would_move_something / delta:.2f}.")
    print(f"  The tightest class edge needs {100 * smallest_margin:.2f} %.")
    print(f"  A boundary above {0.5 / delta:.1f} would be moved by this bias, "
          "so a future re-binning must re-measure S5.")

    payload = {
        "schema": "hadronization_systematic_class_migration_v1",
        "source": "S5",
        "preregistration": "docs/SYSTEMATICS_PREREGISTRATION.md",
        "measured_bias": delta,
        "bias_provenance": {
            "document": "ValidationReports/NCH_DECAY_POLICY_BIAS_8317.md",
            "pythia_version": "8.317",
            "events_per_arm": 200000,
            "paired_on_seed": 20260730,
            "experimental_convention_dndeta": NCH_EXPERIMENTAL_CONVENTION,
            "production_policy_dndeta": NCH_PRODUCTION_POLICY,
            "superseded_8315_bias": superseded_8315_bias(),
            "superseded_8315_document":
                "ValidationReports/NCH_CALIBRATION_20260730.md",
        },
        "boundary_artifact_sha256_source": str(
            BOUNDARY_ARTIFACT.relative_to(REPO)
        ),
        "transformation": "boundary -> boundary / (1 +- delta)",
        "boundaries": rows,
        "integer_partition_identical": identical,
        "per_tune": per_tune,
        "structural_null": structural_null,
        "nch_max_covered": nch_max,
        "relative_shift_that_would_move_the_widest_boundary":
            bias_that_would_move_something,
        "boundary_above_which_this_bias_would_migrate": 0.5 / delta,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )
        print(f"\nwrote {args.output}")
    return 0 if structural_null else 2


if __name__ == "__main__":
    raise SystemExit(main())
