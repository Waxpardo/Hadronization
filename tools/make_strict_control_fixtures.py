#!/usr/bin/env python3
"""Generate the strict-CONTROL fixture logs from one source of arithmetic.

The fixtures under `tests/fixtures/strict_control/` are synthetic
`UNCERTAINTY_MATRIX` renders that `tests/test_strict_control_boundary.py`
drives the production comparator with. Every row satisfies the whole shared v2
contract: schema, block_count, block_yields with a matching sample SEM,
per-block ratios taken against the group's reference row, and block trigger
counts summing to the central count.

WHY THIS GENERATOR IS COMMITTED AND NOT A ONE-OFF SCRIPT (CON-1B item 2;
architect acceptance review of CON-1, finding #1). The first fixture set was
built by a scratch script that computed each summary itself. Its block ratios
came out CONSTANT to within one ulp -- numerator and denominator carried the
same per-block profile, so the profile divided out exactly -- and the recorded
`ratio_sem` was 2.3405556457178006e-17, pure cancellation noise. CPython 3.12
changed `sum()` over floats to compensated (Neumaier) summation. `sample_sem`
sums twice, so the same vector recomputes to 2.8665835232995051e-17 on 3.11 and
2.3405556457178006e-17 on 3.14: a 22% disagreement against the validator's
`rel_tol=5e-15` at `extraction/harvest_class_axis.py:163`. The gate was
therefore green on one interpreter and red on another, and the deployment's
pinned Python decided which. Under ruling R30(2) a gate that fragile is itself
the defect; the rel-tol contract is correct for physical logs and the
PRODUCTION VALIDATOR IS NOT EDITED HERE.

The two properties that close it, both enforced below rather than hoped for:

1. PHYSICAL SCALE. Block yields and block ratios carry real block-to-block
   variation, so the sums that form a SEM are not cancellation. `assert_scale`
   refuses any vector whose recomputed SEM falls under `SEM_FLOOR`; the set
   this file writes today runs four to five orders of magnitude above it.
2. BUILDER AND VALIDATOR ARE COMPARED, PER VECTOR. Every ratio is written with
   the same `numerator / denominator` expression
   `_validate_ratios_against_reference` checks, and every trigger sum is
   checked with `trigger_consistency`. The two SEMs are formed by `stable_sem`
   -- exactly-rounded summation, so the committed bytes do not depend on which
   interpreter generated them -- and `assert_summation_robust` then asserts,
   for EVERY vector this file writes, that the validator's own `sample_sem`
   agrees with what is written, both in block order and reversed, inside the
   validator's own tolerance. See `stable_sem` for why that is stronger than
   computing both sides the same way and never comparing them.

`assert_summation_robust` measures the sensitivity that caused the defect
directly. That is the same class of change CPython made, applied here at build
time, so the fixtures do not need every interpreter present to be shown robust
on them -- though this set was in fact checked on 3.9.6, 3.11.15 and 3.14.7,
which bracket the change.

THE SEED IS A FUNCTION OF THE IDENTITY, never of emission order: the control
drops the MB bin, and a running counter would shift every number after it so
the two renders could not reproduce each other's shared rows.

THE IDENTITIES COME FROM THE PINNED CONFIGURATION
(`tests/fixtures/vintegrated_closure/closure_config_12keys.json`), which is the
configuration the boundary driver passes to the tool, not the tracked closure
configuration. The fixture logs and the configuration they are checked against
therefore move together or not at all.

`--check` reports drift and writes nothing, in the same shape as the
repository's other generators.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / "fixtures" / "strict_control"
CONFIG = (ROOT / "tests" / "fixtures" / "vintegrated_closure"
          / "closure_config_12keys.json")
CLASS_CONTRACT = ROOT / "config" / "multiplicity_percentile_classes_v2.json"

sys.path.insert(0, str(ROOT / "extraction"))
from harvest_class_axis import sample_sem  # noqa: E402
from harvest_yield_deltas import trigger_consistency  # noqa: E402

# The validator's own tolerance, quoted from harvest_class_axis.py:163. The
# robustness check below is made against THIS number, so tightening the
# validator tightens the fixture requirement with it.
VALIDATOR_REL_TOL = 5e-15

# No recomputed SEM may fall below this. The defect it exists to catch recorded
# 2.3e-17; the set written today runs from ~1e-4 upward, and `main` prints the
# observed minimum so the margin is read from the run rather than asserted here.
SEM_FLOOR = 1e-6

INTEGRATED = ("MB", "hDPhiM00_100")
REFERENCE = {"BEAUTY": "B-", "CHARM": "D-"}
NBLOCK = 10

# Block-to-block scatter of a yield vector, as a fraction of its central. Three
# percent over ten blocks puts a yield SEM near 5e-3 of the central and a ratio
# SEM near 8e-3 of its own, which is the physical scale the brief asks for and
# fourteen orders of magnitude clear of the cancellation regime.
YIELD_AMPLITUDE = 0.03


def class_bins() -> list[tuple[str, str]]:
    contract = json.loads(CLASS_CONTRACT.read_text())["classes"]
    return [(row["class"], "hDPhi" + row["bin"]) for row in contract]


def groups(config: dict) -> list[tuple[str, str, list[str]]]:
    """(flavour, trigger, associates in configured order)."""
    out = []
    for flavour, key in (("BEAUTY", "beauty_correlations_to_analyse"),
                         ("CHARM", "charm_correlations_to_analyse")):
        for group in config[key]:
            out.append((flavour, group["trigger"],
                        [c["associateOS"] for c in group["configs"]]))
    return out


def g17(value: float) -> str:
    """Seventeen significant figures round-trips a double exactly.

    `_validate_ratios_against_reference` compares each ratio to
    `numerator / denominator` with `!=`, so anything that loses a bit in
    printing is refused by the validator, not tolerated by it.
    """
    return f"{value:.17g}"


def block_shape(seed: int, block: int, nblock: int) -> float:
    """A per-block wiggle in [-1, 1], from integer arithmetic only.

    Deliberately not a PRNG: the fixtures must be byte-reproducible, and a
    generator's stream is a library guarantee this does not need. Integer
    mixing and one division by a constant give the same double everywhere
    IEEE-754 doubles are.

    A yield vector is a RAMP plus that wiggle, and the ramp's WEIGHT turns with
    the seed. That is what keeps a ratio from going flat: a numerator and its
    reference carry different weights, so the ramp does not divide out, which
    is exactly how the first fixture set came to record a SEM of 2.3e-17.
    """
    ramp = (2.0 * block / (nblock - 1)) - 1.0 if nblock > 1 else 0.0
    mixed = (seed * 1103515245 + block * 12345 + 7) % 2147483647
    mixed = (mixed * 1103515245 + 12345) % 2147483647
    wiggle = ((mixed % 2001) - 1000) / 1000.0
    weight = 0.35 + 0.30 * ((seed % 7) / 6.0)
    return weight * ramp + (1.0 - weight) * wiggle


def block_yields(seed: int, nblock: int, scale: float, level: float
                 ) -> list[float]:
    """One identity's block yields, centred on `level` and scaled by campaign."""
    base = level * scale
    return [base * (1.0 + YIELD_AMPLITUDE * block_shape(seed, i, nblock))
            for i in range(nblock)]


def reference_level(seed: int) -> float:
    """Central yield of a reference row: O(0.1-1), and seed-dependent."""
    return 0.30 + 0.0015 * seed


def stable_mean(values: list[float]) -> float:
    """The mean by exactly-rounded summation."""
    return math.fsum(values) / len(values)


def stable_sem(values: list[float]) -> float:
    """The block SEM, formed with exactly-rounded summation.

    WHY NOT `sample_sem` DIRECTLY, when one source of arithmetic is this
    file's whole point. `sample_sem` sums with `sum()`, and CPython 3.12
    changed `sum()` over floats to compensated summation, so its LAST BIT
    moves with the interpreter. Regenerating this set on Python 3.9 and on
    3.14 gave yield_sem, ratio_sem and central_yield values differing by about
    2e-16 relative -- harmless to the validator, whose rel_tol is 5e-15, but
    enough that the COMMITTED fixture bytes would depend on whoever generated
    them. `tests/test_generator_check_exit_status.py` requires every
    generator's --check to exit 0 in the committed tree, and it caught exactly
    that: 95/96 on 3.9 and 3.11, 96/96 on 3.14.

    `math.fsum` is correctly rounded, so what this writes is a property of the
    input and not of the interpreter. The validator's own routine remains the
    definition of correct: `assert_summation_robust` asserts, for every vector
    this file writes, that `sample_sem` agrees with this value inside the
    validator's own tolerance -- which is a stronger statement than computing
    both the same way and never comparing them.
    """
    mean = stable_mean(values)
    return math.sqrt(
        math.fsum((value - mean) ** 2 for value in values)
        / (len(values) * (len(values) - 1)))


def assert_scale(context: str, values: list[float], sem: float) -> None:
    """Physical scale, not floating-point dust."""
    central = stable_mean(values)
    if not math.isfinite(sem) or sem < SEM_FLOOR:
        raise SystemExit(
            f"{context}: recomputed SEM {sem:.17g} is below the {SEM_FLOOR:g} "
            f"floor; a fixture in the cancellation regime is the defect this "
            f"generator exists to prevent")
    if central == 0.0 or abs(sem / central) < 1e-6:
        raise SystemExit(
            f"{context}: SEM {sem:.17g} is {abs(sem / central):.3g} of its "
            f"central {central:.17g}; the block vector is effectively constant")


def assert_summation_robust(context: str, values: list[float],
                            written: float) -> None:
    """What is written must survive any interpreter's summation.

    The VALIDATOR's own routine is called two ways on the same vector -- as it
    calls it, and on the reversed vector -- and both must agree with the value
    this generator writes, inside the validator's own tolerance. CPython
    3.12's move to compensated summation in `sum()` is a change of exactly
    this kind, so a vector that survives here recomputes acceptably on either
    side of it. The old fixture set failed this by twenty-two percent.
    """
    for name, other in (("as the validator sums it", sample_sem(values)),
                        ("summed in reverse", sample_sem(list(reversed(values))))):
        if not math.isclose(written, other, rel_tol=VALIDATOR_REL_TOL,
                            abs_tol=0.0):
            raise SystemExit(
                f"{context}: SEM is summation-sensitive -- {written:.17g} "
                f"written, {other:.17g} {name}; the validator's rel_tol is "
                f"{VALIDATOR_REL_TOL:g}")


def render_row(flavour: str, trigger: str, tune: str, associate: str,
               binname: str, blocks: list[float], ratios: list[float],
               triggers: list[float], reference: bool, observed: list) -> str:
    """One UNCERTAINTY_MATRIX line, every summary from the validator's own code."""
    context = f"{tune}/{flavour}/{trigger}/{associate}/{binname}"
    yield_sem = stable_sem(blocks)
    assert_scale(f"{context} block_yields", blocks, yield_sem)
    assert_summation_robust(f"{context} block_yields", blocks, yield_sem)
    observed.append(yield_sem)

    central_triggers = math.fsum(triggers)
    check = trigger_consistency(central_triggers, triggers,
                                [g17(t) for t in triggers])
    if not check["agrees_exactly"]:
        raise SystemExit(
            f"{context} block_triggers: the blocks sum to "
            f"{check['block_trigger_sum']:.17g}, not to the central "
            f"{central_triggers:.17g}")

    fields = [
        "UNCERTAINTY_MATRIX",
        "schema=hadronization_uncertainty_matrix_v2",
        f"flavour={flavour}", f"trigger={trigger}", f"tune={tune}",
        f"associate={associate}", f"bin={binname}",
        f"is_reference={'true' if reference else 'false'}",
        f"block_count={len(blocks)}",
        "block_yields=" + ",".join(g17(v) for v in blocks),
        f"yield_sem={g17(yield_sem)}",
        f"central_yield={g17(stable_mean(blocks))}",
        f"central_triggers={g17(central_triggers)}",
        "block_triggers=" + ",".join(g17(v) for v in triggers),
        f"finite_yields={len(blocks)}",
    ]
    if reference:
        fields += ["block_ratios=NA", "ratio_sem=NA", "finite_ratios=NA"]
    else:
        ratio_sem = stable_sem(ratios)
        assert_scale(f"{context} block_ratios", ratios, ratio_sem)
        assert_summation_robust(f"{context} block_ratios", ratios, ratio_sem)
        observed.append(ratio_sem)
        fields += ["block_ratios=" + ",".join(g17(v) for v in ratios),
                   f"ratio_sem={g17(ratio_sem)}",
                   f"finite_ratios={len(ratios)}"]
    fields += ["yield_status=PASS", "ratio_status=PASS", "status=PASS"]
    return " ".join(fields)


def resolver(campaign: str, tunes: list[str]) -> list[str]:
    lines = []
    for sector in ("Beauty", "Charm"):
        for tune in tunes:
            lines.append(f"{sector} central resolver {tune}: "
                         f"base=/data/alice/ipardoza/hadronization_merged, "
                         f"tag=complete_root_{campaign}")
            lines.append(f"{sector} subsample resolver {tune}: "
                         f"base=/data/alice/ipardoza/hadronization_merged/"
                         f"SUBSAMPLES_{campaign}/combined_root_subSamples")
    return lines


def build(config: dict, campaign: str, note: str, observed: list,
          integrated: bool = True, nblock: int = NBLOCK, scale: float = 1.0,
          only: set | None = None, intruder: tuple | None = None) -> str:
    """One synthetic render.

    `intruder` is an (associate, tune) pair added to the beauty meson-trigger
    group -- one extra IDENTITY, sharing the group's reference row so the log
    stays contract-valid and the only thing wrong with it is that the
    configuration does not register it.
    """
    all_bins = class_bins()
    group_list = groups(config)
    tunes = list(config["PYTHIA_TUNES"])
    order = [cls for cls, _bin in all_bins + [INTEGRATED]]
    bins = list(all_bins) + ([INTEGRATED] if integrated else [])

    lines = [f"# {note}"] + resolver(campaign, tunes)
    for flavour, trigger, associates in group_list:
        group_index = group_list.index((flavour, trigger, associates))
        for tune in tunes:
            for cls, binname in bins:
                seed = (1 + group_index * 100 + tunes.index(tune) * 20
                        + order.index(cls))
                triggers = [142000.0 + 100 * i + seed for i in range(nblock)]
                reference_name = REFERENCE[flavour]
                reference_blocks = block_yields(
                    seed, nblock, scale, reference_level(seed))
                drawn = list(associates)
                if (intruder is not None and flavour == "BEAUTY"
                        and trigger == group_list[0][1] and tune == intruder[1]):
                    drawn = drawn + [intruder[0]]
                for index, associate in enumerate(drawn):
                    if only is not None and (
                            flavour, trigger, tune, associate, cls) not in only:
                        continue
                    is_ref = associate == reference_name
                    if is_ref:
                        blocks, ratios = reference_blocks, []
                    else:
                        blocks = block_yields(
                            seed + 40 * index, nblock, scale,
                            reference_level(seed) * (0.45 + 0.22 * index))
                        # The same expression the validator checks each ratio
                        # against, block for block.
                        ratios = [numerator / denominator
                                  for numerator, denominator
                                  in zip(blocks, reference_blocks)]
                    lines.append(render_row(
                        flavour, trigger, tune, associate, binname, blocks,
                        ratios, triggers, is_ref, observed))
    return "\n".join(lines) + "\n"


def fixtures(config: dict, observed: list) -> dict[str, str]:
    """Filename -> content, for every fixture the boundary driver reads."""
    group_list = groups(config)
    tunes = list(config["PYTHIA_TUNES"])
    first = (group_list[0][0], group_list[0][1], tunes[0], group_list[0][2][0],
             class_bins()[0][0])

    def make(**kwargs) -> str:
        return build(config, observed=observed, **kwargs)

    return {
        "nominal_144.log": make(
            campaign="HF_RUN3_V1",
            note="Synthetic v2 nominal: 12 identities x (11 classes + MB) = "
                 "144 rows."),
        "control_132.log": make(
            campaign="HF_RUN3_V1",
            note="Synthetic v2 control: the same 12 identities x 11 classes = "
                 "132 rows.",
            integrated=False),
        "control_one_shared_row.log": make(
            campaign="HF_RUN3_V1",
            note="Round-2 measured 144v132_only_one_shared: a control sharing "
                 "ONE row with the nominal. compare_rows reports agree=True "
                 "on it.",
            integrated=False, only={first}),
        "nominal_thirteenth_identity.log": make(
            campaign="HF_RUN3_V1",
            note="A thirteenth identity -- MONASH B^{+} -> B_s^0-bar -- which "
                 "the closure configuration does not register.",
            intruder=("B_s^0-bar", tunes[0])),
        "nominal_two_blocks.log": make(
            campaign="HF_RUN3_V1",
            note="DA1-030: a syntactically complete TWO-block nominal. The "
                 "shared parser accepts block_count >= 2 and recomputes the "
                 "SEM from two values.",
            nblock=2),
        "control_two_blocks.log": make(
            campaign="HF_RUN3_V1",
            note="The two-block nominal's own control, so the pair AGREES on "
                 "every shared row and only the block count is wrong. This is "
                 "the shape DA1-030 names: the SEM is correctly recomputed "
                 "from two values, so the arithmetic is not malformed -- the "
                 "admission condition is.",
            integrated=False, nblock=2),
        "variation_wrong_resolver.log": make(
            campaign="HF_RUN3_V1",
            note="DA1-031: requested as HF_SYS_MUR_UP, resolved HF_RUN3_V1.",
            scale=1.05),
        "variation_right_resolver.log": make(
            campaign="HF_SYS_MUR_UP",
            note="The same variation shape, resolving the campaign it is "
                 "labelled with.",
            scale=1.05),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="report drift and exit non-zero; write nothing")
    args = parser.parse_args()

    config = json.loads(CONFIG.read_text())
    observed: list[float] = []
    wanted = fixtures(config, observed)

    print("STRICT_FIXTURE_SOURCE config=%s identities=%d tunes=%d"
          % (CONFIG.name,
             len(list(config["PYTHIA_TUNES"]))
             * sum(len(a) for _f, _t, a in groups(config)),
             len(list(config["PYTHIA_TUNES"]))))
    print("STRICT_FIXTURE_SCALE sems=%d min=%.3g max=%.3g floor=%.3g"
          % (len(observed), min(observed), max(observed), SEM_FLOOR))

    drift = []
    for name, text in wanted.items():
        path = OUT / name
        if path.exists() and path.read_text() == text:
            continue
        drift.append(f"{name}: "
                     f"{'differs from' if path.exists() else 'missing'} "
                     f"a fresh generation")
        if not args.check:
            path.write_text(text)

    # Read every fixture back through the PRODUCTION validator, so this
    # generator cannot leave behind a log the repository's own parser refuses.
    # On-disk bytes, not the in-memory text: under --check that is the state
    # the test drivers will actually read.
    from harvest_class_axis import parse_log  # noqa: E402
    for name in wanted:
        rows = parse_log((OUT / name).read_text())
        print("  %-38s %4d rows validated" % (name, len(rows)))

    if not drift:
        print("STRICT_CONTROL_FIXTURES_CURRENT files=%d" % len(wanted))
        return 0
    for line in drift:
        print("  " + line)
    if args.check:
        print("STRICT_CONTROL_FIXTURES_STALE count=%d; run without --check to "
              "regenerate" % len(drift))
        return 1
    print("STRICT_CONTROL_FIXTURES_WRITTEN count=%d" % len(drift))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
