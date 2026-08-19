#!/usr/bin/env python3
"""A2: the pair-level unresolved-origin systematic, per multiplicity class.

Pre-registration: docs/A2_PAIR_UNRESOLVED_PREREGISTRATION.md. Every choice here
is fixed there; this file implements, it does not decide.

INPUT: two CSVs per tune from analysis/a2_pair_yield.C -- baseline (the
committed per_job outputs) and permissive (the variation) -- with rows
`slot,pair_file,mclass,yield`.

THE OBSERVABLE

    Y(m) = sum over OS pair files - sum over SS pair files

OS/SS comes from the SIGNED pair registry, joined on filename, and a filename
absent from the registry is a hard error rather than a dropped row.

THE ESTIMATOR, per the project's standing rule: the ratio is formed INSIDE each
block and the ten block ratios are then averaged. A ratio of summed numerators
to summed denominators is a different estimator with a smaller, wrong variance.

    Delta_b(m) = [ Y_perm_b(m) - Y_base_b(m) ] / Y_base_b(m)
    Delta(m)   = mean over the ten blocks
    sigma(m)   = stdev(ten values) / sqrt(10),  dof = 9

Blocks are `slot % 10`, matching the project's canonical FILE/JOB blocking.

VERDICT thresholds are the pre-registered ones and are applied mechanically.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "config/heavy_flavour_pair_registry_v1.json"

# ---------------------------------------------------------------------------
# THE CONSUMPTION GATE. Mechanized 2026-08-13 by owner ruling.
#
# The pre-registration makes the regression check a gate: the permissive output
# may not be used until the variation has been shown to reproduce the baseline
# with its rule disabled. Between submission and now that gate lived only in a
# paragraph, and a paragraph does not stop a script. Well-formed permissive
# output sitting on disk, protected only by prose, is exactly the shape of
# accident this project keeps recording.
#
# So: this analyzer REFUSES TO RUN unless a sentinel exists recording a PASSED
# regression for the exact variation sha that produced the output. There is
# deliberately no --force and no --skip-gate. The sentinel path can be
# redirected (so the gate itself is testable), but it cannot be waived.
# ---------------------------------------------------------------------------
# GENERALIZED 2026-08-13 by owner ruling, for the tie-break robustness arm.
#
# The gate used to pin ONE sha in this file. A second legitimate variation --
# the largest-heavyIndex tie-break the pre-registration's robustness clause
# asks for -- then had no way in except editing the constant, which is exactly
# the shape of change that should not be quiet. The obvious alternative, an
# override flag, is worse: it admits ANY sha, including a wrong one.
#
# So the pin becomes a committed NAMED SET, config/a2_variations_v1.json, and
# the gate now requires THREE things to agree:
#
#   1. the sentinel records a PASS,
#   2. the sha it verifies is a REGISTERED variation, and
#   3. the caller NAMES the variation it believes it is analysing, and that
#      name resolves to the same sha.
#
# Requirement 3 is the one that earns its keep. Without it, a sentinel left
# over from the smallest-index arm would silently certify a largest-index
# measurement -- both shas are registered, so membership alone would pass, and
# the mislabelled result would look perfect. The caller's claim and the
# evidence must match, and disagreement is a hard failure that names both.
#
# Adding a variation is a reviewable commit to the registry. Each variation
# still needs its OWN regression sentinel: membership is necessary, never
# sufficient.
VARIATIONS_REGISTRY = REPO / "config/a2_variations_v1.json"


def default_sentinel(variation: str) -> Path:
    """One sentinel FILE per variation, named after it.

    A single shared sentinel path would mean the largest-index arm reading the
    smallest-index arm's evidence by default. The name check below would catch
    it -- but a design where the safe outcome depends on a later check firing
    is worse than one where the two arms never share a file in the first place.
    """
    return REPO / f"docs/a2_regression_pass_{variation}.json"

CLASSES = ["M1", "M2", "M3", "M4", "M5"]
CLASS_LABEL = {"M1": "1-9", "M2": "10-19", "M3": "20-29",
               "M4": "30-39", "M5": ">=40"}
N_BLOCKS = 10
LOW_STAT_PAIRS = 1000.0          # per block, per the pre-registration
NEGLIGIBLE_PCT = 0.1             # |Delta| below this, and consistent with 0
FLATNESS_SIGMA = 2.0
SPREAD_FRACTION = 0.5


def load_variations(registry: Path) -> dict:
    """The frozen named set of admissible variations.

    Only entries under `variations` are admissible. `superseded` exists so a
    retired macro's sha stays greppable with the reason it was retired, and
    reading it here would defeat the point of retiring it.
    """
    if not registry.exists():
        raise SystemExit(
            f"GATE: refusing to run. No variation registry at {registry}. "
            "The set of admissible variations is committed, not inferred.")
    try:
        payload = json.loads(registry.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"GATE: variation registry {registry} is not valid "
                         f"JSON: {exc}")
    variations = payload.get("variations")
    if not isinstance(variations, dict) or not variations:
        raise SystemExit(
            f"GATE: variation registry {registry} declares no variations.")
    for name, entry in variations.items():
        sha = entry.get("macro_sha256") if isinstance(entry, dict) else None
        if not isinstance(sha, str) or len(sha) != 64:
            raise SystemExit(
                f"GATE: variation {name!r} in {registry} has no valid "
                "macro_sha256. A registry entry that does not pin a macro "
                "pins nothing.")
    return variations


def check_regression_gate(sentinel: Path, variation: str,
                          registry: Path = VARIATIONS_REGISTRY) -> dict:
    """Refuse to proceed unless the regression has PASSED for THIS variation.

    Every failure below is a hard exit with a stated reason. In particular a
    sentinel that exists but records a FAIL, or records a variation sha that is
    not registered, or records a REGISTERED sha that is not the one the caller
    named, is treated as worse than a missing one: it means somebody has an
    answer already and it is not the answer this analyzer needs.
    """
    variations = load_variations(registry)

    if variation not in variations:
        raise SystemExit(
            f"GATE: {variation!r} is not a registered variation.\n"
            f"  registered: {', '.join(sorted(variations))}\n"
            f"  registry:   {registry}\n"
            "Adding a variation is a reviewable commit to the registry. There "
            "is deliberately no flag that admits an unregistered macro.")
    expected_sha = variations[variation]["macro_sha256"]

    if not sentinel.exists():
        raise SystemExit(
            f"GATE: refusing to run. No regression sentinel at {sentinel}.\n"
            "The A2 permissive output may not be consumed until the variation "
            "has been shown to reproduce the baseline with its rule disabled "
            "(docs/A2_PAIR_UNRESOLVED_PREREGISTRATION.md, positive check 1).\n"
            "Produce it with tools/a2_record_regression.py after comparing "
            "a2_runs/regression/MONASH/slot_000 against the committed "
            "per_job/MONASH/slot_000. There is no override.")
    try:
        payload = json.loads(sentinel.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"GATE: sentinel {sentinel} is not valid JSON: {exc}")

    for key in ("verdict", "variation_sha256", "compared", "recorded"):
        if key not in payload:
            raise SystemExit(
                f"GATE: sentinel {sentinel} is missing required key {key!r}. "
                "A sentinel that does not say what it verified is not evidence.")

    if payload["verdict"] != "PASS":
        raise SystemExit(
            f"GATE: the regression verdict is {payload['verdict']!r}, not PASS. "
            "The permissive output must not be consumed, and it should be "
            "quarantined -- see tools/a2_quarantine_outputs.py.")

    sentinel_sha = payload["variation_sha256"]

    # Requirement 2: the sentinel certifies a REGISTERED macro at all.
    registered = {sha: name for name, entry in variations.items()
                  for sha in [entry["macro_sha256"]]}
    if sentinel_sha not in registered:
        raise SystemExit(
            "GATE: the sentinel verifies an UNREGISTERED variation.\n"
            f"  sentinel: {sentinel_sha}\n"
            f"  registry: {registry}\n"
            f"  registered: {', '.join(sorted(variations))}\n"
            "A regression pass certifies one specific macro, not the idea of a "
            "macro, and this analyzer consumes only macros the registry names.")

    # Requirement 3: the caller's CLAIM and the evidence agree. Both shas can
    # be registered and still be the wrong pair -- that is precisely the
    # mislabelling this check exists to catch.
    if sentinel_sha != expected_sha:
        raise SystemExit(
            "GATE: the sentinel does not certify the variation you named.\n"
            f"  you named:      {variation}  ({expected_sha})\n"
            f"  sentinel is for: {registered[sentinel_sha]}  ({sentinel_sha})\n"
            "Both are registered, so this is not an unknown macro -- it is the "
            "WRONG one, which is worse, because the output would look correct. "
            "Re-run the regression against the variation that produced the "
            "output being analysed, or correct --variation.")

    print(f"GATE PASSED  variation={variation}  sha={sentinel_sha[:16]}...  "
          f"compared={payload['compared']}  recorded={payload['recorded']}")
    return payload


def check_campaign_restoration(permissive_root: Path, tune: str) -> dict:
    """The did-it-work assertion, made ONCE at campaign level.

    This replaces a per-job throw that fired when a job restored nothing. That
    guard was right about the failure it feared and wrong about the sample
    size: at MONASH's measured ~6 restorations per million events a
    100k-event job restores 0.6 on average, so zero is the MODAL outcome, and
    throwing on it discarded 49 of 100 MONASH jobs while never firing for
    JUNCTIONS or CLOSEPACKING at ~1220 per million. That is selection on the
    outcome variable, in one arm of the comparison only.

    Two questions are kept apart:
      "did the RIGHT CODE run?" is PROVENANCE, answered per job by
      analysis_macro_sha256 in the job metadata and by the regression gate;
      "how much did it FIND?" is PHYSICS, and its answer includes zero.

    Zero across the WHOLE campaign is still a defect, and is what this checks.
    """
    pattern = re.compile(
        r"A2_PERMISSIVE\s+restored_charm=(\d+)\s+restored_beauty=(\d+)"
        r"(?:\s+contested_seen_charm=(\d+)\s+contested_seen_beauty=(\d+))?")
    charm = beauty = contested = jobs = zero_jobs = 0
    for log in sorted(permissive_root.glob("slot_*/analysis.log")):
        match = pattern.search(log.read_text(errors="replace"))
        if match is None:
            raise SystemExit(
                f"FAIL-CLOSED: {log} carries no A2_PERMISSIVE line. The "
                "permissive arm must record what it restored, in every job.")
        jobs += 1
        rc, rb = int(match.group(1)), int(match.group(2))
        charm += rc
        beauty += rb
        if match.group(3) is not None:
            contested += int(match.group(3)) + int(match.group(4))
        if rc + rb == 0:
            zero_jobs += 1
    if jobs == 0:
        raise SystemExit(
            f"FAIL-CLOSED: no permissive job logs under {permissive_root}")
    if charm + beauty == 0:
        raise SystemExit(
            f"FAIL-CLOSED: the {tune} permissive campaign restored NOTHING "
            f"across all {jobs} jobs. A silent zero would make every measured "
            "shift trivially zero and look like a clean null. This is the "
            "campaign-level form of the check that used to run per job.")
    print(f"CAMPAIGN_RESTORATION tune={tune} jobs={jobs} "
          f"restored_charm={charm} restored_beauty={beauty} "
          f"contested_seen={contested} zero_restoration_jobs={zero_jobs} "
          f"per_Mevt={(charm + beauty) / (jobs * 0.1):.1f} status=PASS")
    return {"jobs": jobs, "charm": charm, "beauty": beauty,
            "contested_seen": contested, "zero_restoration_jobs": zero_jobs}


def load_signs() -> dict[str, str]:
    payload = json.loads(REGISTRY.read_text())
    signs = {row["filename"]: row["heavy_sign"] for row in payload["pairs"]}
    if len(signs) != int(payload["pair_count"]):
        raise SystemExit(
            f"FAIL-CLOSED: registry declares {payload['pair_count']} pairs but "
            f"carries {len(signs)} filenames")
    return signs


def load_yields(path: Path, signs: dict[str, str]):
    """-> {block: {mclass: [os_sum, ss_sum]}}, and the per-block pair totals."""
    per_block = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
    totals = defaultdict(lambda: defaultdict(float))
    seen_slots = set()
    with path.open() as fh:
        for row in csv.DictReader(fh):
            name = row["pair_file"]
            sign = signs.get(name)
            if sign is None:
                raise SystemExit(
                    f"FAIL-CLOSED: {name} in {path} is not in the signed pair "
                    "registry, so its OS/SS assignment is unknown")
            slot = int(row["slot"])
            seen_slots.add(slot)
            block = slot % N_BLOCKS
            value = float(row["yield"])
            mclass = row["mclass"]
            per_block[block][mclass][0 if sign == "OS" else 1] += value
            totals[block][mclass] += value
    return per_block, totals, seen_slots


def compensation(entry) -> float:
    return entry[0] - entry[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--permissive", type=Path, required=True)
    ap.add_argument("--tune", default="?")
    ap.add_argument("--variation", required=True,
                    help="the variation whose output this is, by NAME, as "
                         "registered in config/a2_variations_v1.json. Required: "
                         "the caller must state which arm it believes it is "
                         "analysing, so the gate can refuse when that "
                         "disagrees with the sentinel.")
    ap.add_argument("--variations-registry", type=Path,
                    default=VARIATIONS_REGISTRY,
                    help="the committed set of admissible variations. "
                         "Redirectable so the gate itself can be tested.")
    ap.add_argument("--regression-sentinel", type=Path, default=None,
                    help="path to the regression-pass sentinel; defaults to "
                         "docs/a2_regression_pass_<variation>.json. "
                         "Redirectable so the gate itself can be tested; there "
                         "is deliberately no way to waive it.")
    ap.add_argument("--permissive-run-root", type=Path, required=True,
                    help="the permissive run directory for this tune, holding "
                         "slot_NNN/analysis.log. Read for the CAMPAIGN-level "
                         "restoration assertion that replaced the per-job "
                         "guard; --permissive is the yield CSV, not this.")
    args = ap.parse_args()

    # THE GATE, before any input is even opened.
    sentinel = args.regression_sentinel or default_sentinel(args.variation)
    check_regression_gate(sentinel, args.variation, args.variations_registry)
    # The campaign-level did-it-work assertion, which replaced the per-job one.
    check_campaign_restoration(args.permissive_run_root, args.tune)

    signs = load_signs()
    base, base_tot, base_slots = load_yields(args.baseline, signs)
    perm, perm_tot, perm_slots = load_yields(args.permissive, signs)

    if base_slots != perm_slots:
        raise SystemExit(
            "FAIL-CLOSED: baseline and permissive cover different slots. "
            f"only-baseline={sorted(base_slots - perm_slots)[:5]} "
            f"only-permissive={sorted(perm_slots - base_slots)[:5]}")
    if len(base_slots) == 0:
        raise SystemExit("FAIL-CLOSED: no slots found")

    print(f"TUNE {args.tune}   slots={len(base_slots)}   blocks={N_BLOCKS}")
    print()
    print(f"{'class':<7}{'N_ch':<9}{'Delta %':>10}{'SEM':>9}"
          f"{'blocks':>8}  flag")

    results = {}
    for mclass in CLASSES:
        deltas = []
        low_stat = False
        for block in range(N_BLOCKS):
            yb = compensation(base[block][mclass])
            yp = compensation(perm[block][mclass])
            if base_tot[block][mclass] < LOW_STAT_PAIRS:
                low_stat = True
            if yb == 0.0:
                low_stat = True
                continue
            deltas.append(100.0 * (yp - yb) / yb)
        if len(deltas) < 2:
            print(f"{mclass:<7}{CLASS_LABEL[mclass]:<9}{'--':>10}{'--':>9}"
                  f"{len(deltas):>8}  LOW-STAT (excluded)")
            results[mclass] = None
            continue
        mean = statistics.mean(deltas)
        sem = statistics.stdev(deltas) / (len(deltas) ** 0.5)
        results[mclass] = (mean, sem, low_stat)
        print(f"{mclass:<7}{CLASS_LABEL[mclass]:<9}{mean:>10.4f}{sem:>9.4f}"
              f"{len(deltas):>8}  {'LOW-STAT' if low_stat else ''}")

    # ---- the multiplicity-integrated value --------------------------------
    int_deltas = []
    for block in range(N_BLOCKS):
        yb = sum(compensation(base[block][m]) for m in CLASSES)
        yp = sum(compensation(perm[block][m]) for m in CLASSES)
        if yb != 0.0:
            int_deltas.append(100.0 * (yp - yb) / yb)
    d_int = statistics.mean(int_deltas)
    s_int = statistics.stdev(int_deltas) / (len(int_deltas) ** 0.5)
    print()
    print(f"{'INTEGRATED':<16}{d_int:>10.4f}{s_int:>9.4f}")

    # ---- the pre-registered verdict, applied mechanically -----------------
    usable = {m: v for m, v in results.items() if v and not v[2]}
    if not usable:
        print("\nVERDICT: UNDETERMINED -- every class is LOW-STAT")
        return 2

    negligible = all(abs(mean) < NEGLIGIBLE_PCT
                     and abs(mean) <= FLATNESS_SIGMA * sem
                     for mean, sem, _ in usable.values())
    off_int = [m for m, (mean, sem, _) in usable.items()
               if abs(mean - d_int) > FLATNESS_SIGMA * sem]
    means = [v[0] for v in usable.values()]
    spread = max(means) - min(means)
    wide = abs(d_int) > 0 and spread > SPREAD_FRACTION * abs(d_int)

    print()
    if negligible:
        verdict = "NEGLIGIBLE -- need not be quoted"
    elif off_int or wide:
        verdict = "MUST BE QUOTED PER MULTIPLICITY CLASS"
    else:
        verdict = "QUOTABLE AS ONE NUMBER"
    print(f"VERDICT: {verdict}")
    print(f"  classes off the integrated value by >2 SEM: "
          f"{sorted(off_int) if off_int else 'none'}")
    print(f"  spread across classes = {spread:.4f} pp "
          f"({'>' if wide else '<='} 50% of |integrated|)")
    print(f"  sign check (pre-registered: Delta >= 0): "
          f"{'OK' if all(m >= -2 * s for m, s, _ in usable.values()) else 'VIOLATED -- STOP'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
