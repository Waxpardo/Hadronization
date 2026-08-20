#!/usr/bin/env python3
"""Regression test for extraction/compare_subset_parent.py.

A COMPARE TOOL THAT CANNOT FAIL ITS KNOWN CASE CERTIFIES NOTHING. The known case
is the anchor incident (docs/ERROR_RECORD.md E4): the committed anchor
extraction against the merged MONASH central, at scale ~10. The tool must
REDISCOVER the recorded flagged set -- 30 bins, concentrated in the baryon
sector, with Sigma_b-bar-minus among the largest.

NOTE the reference set is 30 bins, not one. The first pass at this incident
looked only at the six Sigma_b bins and concluded "one bad bin"; running the
comparison over all 95 ordinals showed the inconsistency is broad and
baryon-sector-wide. The reference set is pinned here so that any change in the
tool's behaviour -- or in either fixture -- fails loudly.

THE NULL IS NAMED EXPLICITLY IN EVERY CALL BELOW, and checks 1-3 deliberately
name `binomial`. That is not the null the project now uses for integrity work --
I2 moved to the robust `mad` null on 2026-08-13 because the binomial one is
misspecified for event-clustered pair counts. It is pinned here because THIS
TEST IS THE AUDIT TRAIL OF A PUBLISHED NUMBER: "30 of 88 at |z| > 4" is quoted
in ERROR_RECORD E4 and elsewhere, and it was computed with the binomial null.
Recomputing history under a new null and keeping the old caption would be a
quiet rewrite. So the historical computation stays pinned, by name, and the
recalibrated count is pinned separately in check 4.

Six checks, and each can fail independently:
  1. the known case          -- reproduces the recorded 30-bin flagged set;
  2. a negative control      -- parent against itself flags nothing;
  3. an injected positive    -- a synthetic 10 sigma bin is caught;
  4. the same case under MAD -- reproduces the recalibrated flagged set, and
                                the E4 headline bins survive the wider null;
  5. MAD negative control    -- parent against itself flags nothing (this one
                                exercises the degenerate sigma^ = 0 branch);
  6. MAD injected positive   -- the synthetic bin is still caught.

Without (2)/(5) a tool that flags everything would pass (1)/(4); without
(3)/(6) a tool that flags nothing would pass (2)/(5).
"""
import csv
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "extraction"))
from compare_subset_parent import compare  # noqa: E402

ANCHOR = REPO / "AnalysisScripts/anchors/extraction_dual/per_species.csv"
PARENT = REPO / "AnalysisScripts/anchors/merged_monash_replicated/per_species.csv"
MAP = REPO / "AnalysisScripts/decay_parent_map_v1_1.json"

# The bin the anchor incident is named for: Sigma_b-bar-minus, pdg -5222.
KNOWN_BAD_PDG = -5222

# The recorded flagged set at |z| > 4, binomial model, measured 2026-08-11.
# Pinned so a behaviour change fails rather than passing quietly.
REFERENCE_FLAGGED = {
    40, 41, 43, 44, 48, 49, 55, 67, 71, 73, 77, 81, 84, 87, 94, 99, 100,
    102, 108, 113, 114, 117, 126, 128, 135, 151, 153, 158, 160, 161,
}

# The recalibrated set under the robust MAD null, measured 2026-08-13: EMPTY.
# sigma^ = 4.3990 on this comparison and the largest bin reaches |z| = 2.83.
# This is pinned as a known blind spot -- see check 4 for why an empty set is
# the correct answer here and why it does NOT exonerate the anchor. Checks 5, 6
# and 7 are what stop an empty reference from being vacuous.
MAD_REFERENCE_FLAGGED: set[int] = set()
MAD_SIGMA_LO, MAD_SIGMA_HI = 4.35, 4.45
# On genuinely binomial data sigma^ must recover ~1. Band is wide enough to
# absorb sampling noise at n = 300 bins and tight enough to catch a wrong
# 1.4826 or a missing centring.
CAL_SIGMA_LO, CAL_SIGMA_HI = 0.85, 1.15


def load(p):
    return {int(r["ordinal"]): float(r["total"])
            for r in csv.DictReader(p.open())}


def main() -> int:
    for p in (ANCHOR, PARENT, MAP):
        if not p.exists():
            print(f"FAIL: missing fixture {p}")
            return 1

    spec = json.loads(MAP.read_text())["species"]
    ord_of = {int(s["pdg"]): int(s["ordinal"]) for s in spec}
    name_of = {int(s["ordinal"]): s["name"] for s in spec}
    bad_ord = ord_of[KNOWN_BAD_PDG]

    subset, parent = load(ANCHOR), load(PARENT)
    failures = []

    # ---- 1. the known case ------------------------------------------------
    # `null="binomial"` is DELIBERATE: this reproduces the historical E4
    # computation, not the project's current integrity null. See the docstring.
    scale, f, rows, flagged, untestable, missing, _diag = compare(
        subset, parent, null="binomial", z_threshold=4.0, expect_scale=10.0)
    flagged_ords = {r[0] for r in flagged}
    if not 9.9 < scale < 10.1:
        failures.append(f"scale {scale:.3f} not ~10")
    if bad_ord not in flagged_ords:
        failures.append(
            f"KNOWN CASE NOT REDISCOVERED: ordinal {bad_ord} "
            f"({name_of.get(bad_ord)}) was not flagged")
    if flagged_ords != REFERENCE_FLAGGED:
        missing_ref = REFERENCE_FLAGGED - flagged_ords
        extra_ref = flagged_ords - REFERENCE_FLAGGED
        failures.append(
            f"flagged set changed: missing={sorted(missing_ref)} "
            f"unexpected={sorted(extra_ref)}")
    ok1 = bad_ord in flagged_ords and flagged_ords == REFERENCE_FLAGGED
    print(f"1. known case: scale={scale:.4f} flagged={len(flagged)} "
          f"(reference {len(REFERENCE_FLAGGED)}) {'OK' if ok1 else 'FAIL'}")
    top = sorted(flagged, key=lambda r: -abs(r[4]))[:4]
    for o, k, N, exp, z in top:
        print(f"     ordinal {o} {name_of.get(o,''):<14} subset={k:.0f} "
              f"expected={exp:.1f} z={z:+.2f}")

    # ---- 2. negative control ---------------------------------------------
    _, _, _, flagged2, _, _, _ = compare(
        parent, parent, null="binomial", z_threshold=4.0)
    if flagged2:
        failures.append(f"negative control flagged {len(flagged2)} bins")
    print(f"2. negative control (parent vs itself): flagged={len(flagged2)} "
          f"{'OK' if not flagged2 else 'FAIL'}")

    # ---- 3. injected positive --------------------------------------------
    # Perturb one healthy, well-populated bin by ~10 sigma and require a catch.
    healthy = max((o for o in subset if o != bad_ord and parent.get(o, 0) > 1e6),
                  key=lambda o: parent[o])
    N = parent[healthy]
    exp = N * f
    sigma = (N * f * (1 - f)) ** 0.5
    injected = dict(subset)
    injected[healthy] = exp + 10.0 * sigma
    # keep integrality, which the tool fail-closes on
    injected[healthy] = float(int(round(injected[healthy])))
    _, _, _, flagged3, _, _, _ = compare(
        injected, parent, null="binomial", z_threshold=4.0)
    caught = healthy in {r[0] for r in flagged3}
    if not caught:
        failures.append(f"injected 10 sigma deviation at ordinal {healthy} NOT caught")
    print(f"3. injected 10-sigma at ordinal {healthy} ({name_of.get(healthy,'')}): "
          f"{'CAUGHT -- OK' if caught else 'MISSED -- FAIL'}")

    # ---- 4. the same case under the recalibrated MAD null ------------------
    # MEASURED 2026-08-13, and it is NOT what the standing ruling predicted.
    # The ruling reasoned from a ~2.2x sigma inflation and expected the two
    # largest bins to survive at z ~ 5. That 2.2x is the BLOCK-vs-central
    # overdispersion (38bf707); this is the ANCHOR-vs-parent comparison, whose
    # pull distribution is far wider -- sigma^ = 4.399, cross-checked against
    # plain stdev 4.426 and IQR/1.349 4.364, so the width is real and not a MAD
    # artifact. At that width the largest bin reaches |z| = 2.83 and NOTHING
    # crosses 4.
    #
    # WHY THAT IS THE CORRECT ANSWER AND NOT A BROKEN TOOL. MAD asks "does any
    # bin stand out from the bulk of this comparison?". The anchor's defect is
    # not one bin standing out -- it is the whole baryon sector displaced
    # together, 30 of 88 bins. A robust scale estimated FROM the contaminated
    # sample absorbs that displacement into the width. The instrument is
    # answering its question correctly; its question is the wrong one for a
    # broad defect.
    #
    # This is pinned as a KNOWN BLIND SPOT, not as reassurance. If a future
    # change makes this flag something, the test fails and the record must be
    # re-read before the count is quoted.
    _, _, _, flagged4, _, _, diag4 = compare(
        subset, parent, null="mad", z_threshold=4.0, expect_scale=10.0)
    mad_ords = {r[0] for r in flagged4}
    if mad_ords != MAD_REFERENCE_FLAGGED:
        failures.append(
            f"MAD flagged set changed: missing="
            f"{sorted(MAD_REFERENCE_FLAGGED - mad_ords)} "
            f"unexpected={sorted(mad_ords - MAD_REFERENCE_FLAGGED)}")
    if not (MAD_SIGMA_LO < diag4["sigma_hat"] < MAD_SIGMA_HI):
        failures.append(
            f"MAD sigma^ = {diag4['sigma_hat']:.4f} outside the pinned band "
            f"({MAD_SIGMA_LO}, {MAD_SIGMA_HI})")
    ok4 = mad_ords == MAD_REFERENCE_FLAGGED and (
        MAD_SIGMA_LO < diag4["sigma_hat"] < MAD_SIGMA_HI)
    print(f"4. known case under MAD: sigma^={diag4['sigma_hat']:.3f} "
          f"flagged={len(flagged4)} (reference {len(MAD_REFERENCE_FLAGGED)}, "
          f"the pinned blind spot) {'OK' if ok4 else 'FAIL'}")

    # ---- 5. MAD negative control ------------------------------------------
    # Also the only exercise of the degenerate branch: parent against itself has
    # zero dispersion, so sigma^ = 0 and the code must not divide by it.
    _, _, _, flagged5, _, _, _ = compare(parent, parent, null="mad", z_threshold=4.0)
    if flagged5:
        failures.append(f"MAD negative control flagged {len(flagged5)} bins")
    print(f"5. MAD negative control (parent vs itself): flagged={len(flagged5)} "
          f"{'OK' if not flagged5 else 'FAIL'}")

    # ---- 6. MAD injected positive -----------------------------------------
    # Injected at 10x the MEASURED width, not 10x the binomial sigma. Under a
    # null whose sigma^ is 4.4, a 10-binomial-sigma bin is a 2.3-sigma event and
    # SHOULD NOT be flagged -- testing it at the binomial scale would be testing
    # the wrong instrument and would fail for the right reason, which is a
    # confusing test. What must be true is that a bin standing out from the
    # comparison's own spread IS caught.
    N_h = parent[healthy]
    binom_sigma = (N_h * f * (1 - f)) ** 0.5
    target_pull = diag4["centre"] + 10.0 * diag4["sigma_hat"]
    injected_mad = dict(subset)
    injected_mad[healthy] = float(int(round(N_h * f + target_pull * binom_sigma)))
    _, _, _, flagged6, _, _, _ = compare(
        injected_mad, parent, null="mad", z_threshold=4.0)
    caught6 = healthy in {r[0] for r in flagged6}
    if not caught6:
        failures.append(
            f"MAD missed a deviation injected at 10x its own sigma^ "
            f"at ordinal {healthy}")
    print(f"6. MAD injected 10x-sigma^ at ordinal {healthy}: "
          f"{'CAUGHT -- OK' if caught6 else 'MISSED -- FAIL'}")

    # ---- 7. the calibration check -----------------------------------------
    # THE CHECK THAT MAKES THE MAD MODE MEANINGFUL RATHER THAN ARBITRARY. On
    # data that really is binomial, sigma^ must come out at ~1 -- that is what
    # the 1.4826 constant is for, and it is what makes "sigma^ = 4.4" readable
    # as "4.4x overdispersed" instead of as an unscaled number. Fixed seed, so
    # this is deterministic.
    # At N ~ 1e6 and p = 0.1 the binomial is indistinguishable from its normal
    # approximation (np(1-p) ~ 1e5), so drawing from the latter is a faithful
    # generator here and is fast.
    rng = random.Random(20260813)
    synth_parent = {o: float(rng.randint(200_000, 2_000_000)) for o in range(300)}
    synth_subset = {}
    for o, n in synth_parent.items():
        mean, sd = n * 0.10, (n * 0.10 * 0.90) ** 0.5
        synth_subset[o] = float(int(round(rng.gauss(mean, sd))))
    _, _, _, flagged7, _, _, diag7 = compare(
        synth_subset, synth_parent, null="mad", z_threshold=4.0)
    calibrated = CAL_SIGMA_LO < diag7["sigma_hat"] < CAL_SIGMA_HI
    if not calibrated:
        failures.append(
            f"MAD is not calibrated: on genuinely binomial data sigma^ = "
            f"{diag7['sigma_hat']:.4f}, expected ~1.0 "
            f"({CAL_SIGMA_LO}, {CAL_SIGMA_HI})")
    if flagged7:
        failures.append(
            f"MAD flagged {len(flagged7)} bins on clean binomial data")
    print(f"7. calibration on synthetic binomial data: sigma^="
          f"{diag7['sigma_hat']:.3f} (expect ~1.0) flagged={len(flagged7)} "
          f"{'OK' if calibrated and not flagged7 else 'FAIL'}")

    # ---- 8. the counting floor --------------------------------------------
    # A DETERMINISTIC split is not a sample. Building blocks by exact division
    # gives residuals that are pure integer rounding, so the empirical width
    # collapses to ~0.002 -- three orders below the counting floor. Without the
    # floor, dividing rounding residue by that width manufactures significance:
    # this exact fixture produced 9 flags per block, 90 across a run, on data
    # whose binomial pulls never exceed 0.06. The floor must hold sigma at 1.
    det_parent = {o: float(v) for o, v in
                  ((o, int(parent[o])) for o in parent) if v > 0}
    det_subset = {o: float(int(v) // 10) for o, v in det_parent.items()}
    _, _, rows8, flagged8, _, _, diag8 = compare(
        det_subset, det_parent, null="mad", z_threshold=4.0)
    _, _, rows8b, flagged8b, _, _, _ = compare(
        det_subset, det_parent, null="binomial", z_threshold=4.0)
    floor_held = (diag8["sigma_hat"] < 0.5 and diag8["floored"]
                  and diag8["sigma_eff"] == 1.0 and not flagged8)
    if not floor_held:
        failures.append(
            f"counting floor failed: sigma^={diag8['sigma_hat']:.5f} "
            f"sigma_eff={diag8['sigma_eff']:.5f} flagged={len(flagged8)} "
            f"(binomial flags the same fixture {len(flagged8b)} times, so the "
            f"data is clean and any MAD flag here is manufactured)")
    print(f"8. counting floor on a deterministic split: sigma^="
          f"{diag8['sigma_hat']:.5f} -> sigma_eff={diag8['sigma_eff']:.1f}, "
          f"flagged={len(flagged8)} (binomial: {len(flagged8b)}) "
          f"{'OK' if floor_held else 'FAIL'}")

    print()
    if failures:
        for f_ in failures:
            print("FAIL:", f_)
        return 1
    print("PASS test_compare_subset_parent.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
