# A2 — Δ measured, and the pre-registration scored

**2026-08-13. The pair-level unresolved-origin systematic on the OS−SS
observable, per multiplicity class, per tune.** Variation macro
`a4df31e6b6da5098d40b793a0c3616957457b326bcef48538bbe271b05f38553`, campaign
`5486752`, 100 slots × 3 tunes, 10 M events per tune.

Every number below is the analyzer's own output, preserved verbatim in
`a2_delta_<TUNE>.txt`. Nothing here is retyped from a screen.

---

## THE RESULT

Δ(m) = [Y_permissive(m) − Y_baseline(m)] / Y_baseline(m), formed **inside each
block** and averaged over the ten blocks (blocks = `slot % 10`, dof 9).

| class | N_ch | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|---|
| M1 | 1–9 | 0.0000 ± 0.0000 | 0.0072 ± 0.0010 | 0.0098 ± 0.0008 |
| M2 | 10–19 | 0.0000 ± 0.0000 | 0.0255 ± 0.0012 | 0.0220 ± 0.0026 |
| M3 | 20–29 | 0.0000 ± 0.0000 | 0.0323 ± 0.0060 | 0.0365 ± 0.0046 |
| M4 | 30–39 | 0.0000 ± 0.0000 | 0.0372 ± 0.0045 | 0.0614 ± 0.0095 |
| M5 | ≥ 40 | 0.0000 ± 0.0000 | **0.0697 ± 0.0124** | 0.0420 ± 0.0135 |
| **integrated** | | **0.0000** | **0.0194 ± 0.0014** | **0.0192 ± 0.0007** |

All figures are **per cent**. No class was flagged `LOW-STAT`.

| tune | verdict, by the pre-registered thresholds |
|---|---|
| MONASH | **NEGLIGIBLE — need not be quoted** |
| JUNCTIONS | **MUST BE QUOTED PER MULTIPLICITY CLASS** |
| CLOSEPACKING | **MUST BE QUOTED PER MULTIPLICITY CLASS** |

**JUNCTIONS rises monotonically, M1 → M5, by a factor of 9.7.** CLOSEPACKING
rises by 6.3 from M1 to M4 and its M5 sits below M4 by 1.2 σ — consistent with
the same rise, with the tail class's larger SEM.

---

## MONASH's exact zero — what it is and what it is not

The two MONASH arms are **byte-identical**: `baseline_MONASH.csv` and
`permissive_MONASH.csv` share the sha256 `ac6a7898742ed717…d71d11ea8`, zero of
150 000 rows differ, and both total 3 232 913 pairs. A permissive slot that
restored two rows compares **content-identical** to its baseline slot across all
300 pair files, the only difference being the macro sha.

**This was checked rather than assumed, because an exact zero is the shape of a
plumbing failure.** The mutated `heavyOriginC` *is* read downstream at the
trigger selection, which tests `triggerOrigin != Origin::kSelectedHard` —
exactly the value the restoration writes. The rule is wired in.

> **So the zero is a STATISTICS statement, not a mechanism statement.** MONASH
> restored **62 rows in 10 M events**. A restored row must still pass the full
> trigger selection — central, ground state, acceptance, pT > 1 GeV — before it
> can add a pair. At 62 candidates, an observed zero survivors is unremarkable.
> **Do not read MONASH's zero as "the effect does not exist in MONASH."** Read
> it as "MONASH's exposure is too small to measure it here."

The CR tunes carry **197×** the exposure, which is why they are where the
measurement happens.

---

## THE PRE-REGISTRATION, SCORED VERBATIM

### §7 expectations

| # | expectation | outcome |
|---|---|---|
| 1 | **Sign.** Δ(m) ≥ 0 everywhere; a negative Δ beyond 2 SEM is STOP-and-diagnose | **HIT.** Every Δ ≥ 0 in all three tunes; the analyzer's own sign check reports OK for each |
| 2 | **Scale.** ≲ 0.09 % MONASH, ≲ 1.2 % CR | **HIT.** Largest value anywhere is 0.0697 % (JUNCTIONS M5), inside both bounds by a wide margin |
| 3 | **Ordering.** CR ≫ MONASH, tracking the inclusive ~13× | **HIT in direction, MISS in magnitude.** CR ≫ MONASH holds emphatically. But the ratio is not ~13×: MONASH is *exactly* zero, so the ratio is undefined, and the underlying **exposure** ratio is **197×**, not 13.6×. The pre-registration's own words apply — "if the CR tunes do not exceed MONASH substantially … that is itself reportable"; the opposite happened, and the amount by which they exceed it is far larger than predicted |
| 4 | **Multiplicity dependence.** Δ(m) increases with m, most steeply in the CR tunes; **a flat Δ(m) would retire the concern A2 raised** | **HIT, and this is the result.** JUNCTIONS 0.0072 → 0.0697 monotonically across M1–M5; CLOSEPACKING 0.0098 → 0.0614 across M1–M4. **The flat outcome named in advance as legitimate did NOT occur, so A2's concern is not retired — it is confirmed** |

### §9 positive checks

| # | check | outcome |
|---|---|---|
| 1 | regression: rule disabled reproduces a committed `per_job` output | **PASS.** 300 files, 300 diffs, every one the single allowed `analysis_macro_sha256` field, zero unexpected. Sentinel `regression_sentinel_a4df31e6.json` |
| 2 | the rule restores > 0 rows, reported per tune | **PASS**, now at campaign level (ERROR_RECORD E7): MONASH 62, JUNCTIONS 12 194, CLOSEPACKING 12 287 restorations; `contested_seen` 124 / 24 411 / 24 590 |
| 3 | `sameHardConstituentPairs` must not fire | **PASS.** It is a `throw`; all 300 jobs promoted, so it fired on none |
| 4 | scratch deploy, sha-pinned, frozen tree never written | **PASS.** `a2_variation`, macro sha in every job manifest; the frozen checkout is read for `setupEnv.sh` only |

---

## THE VERDICT ON THE SYSTEMATIC

> **It must be quoted PER MULTIPLICITY CLASS for the colour-reconnection tunes,
> and it is negligible for MONASH.**
>
> It is **small** — no class exceeds **0.07 %** — but it is **not flat**, and
> its multiplicity dependence is significant at up to 5.6 σ. A single
> integrated number (0.019 %) understates the highest-activity class by a
> factor of 3.6 in JUNCTIONS.

**This is precisely the claim review finding A2 said had never been tested.**
The inclusive M7 diagnostic could not have found it: M7's CR/MONASH ratio is
13.6×, the pair-level exposure ratio is 197×, and the two do not scale
together. **A global rate did not bound a multiplicity-localized effect**, which
is what M7's own scope caveat warned.

---

## ⚠ THE TIE-BREAK ROBUSTNESS CHECK HAS SINCE RUN — READ IT BEFORE QUOTING THIS

**`docs/a2_results_20260813/A2_TIEBREAK_ROBUSTNESS.md`**, same day. Everything
in *this* document is the **smallest-`heavyIndex`** arm and reproduces exactly.
But it is **one of two directions**, and the two do not agree on magnitude:

> **The SHAPE survives the flip — both arms rise by 5.9–9.7× across the
> multiplicity classes, so the trend is not an artefact of the tie-break. The
> MAGNITUDE does not: the largest-index arm is 2.0–5.5× larger in every one of
> the ten CR classes, at 2.7–21.6 σ.**

Three claims above are consequently amended:

| claim here | status |
|---|---|
| "no class exceeds **0.07 %**" | **RETIRED.** True of this arm only; the other reaches **0.229 %** (CLOSEPACKING M5), and seven of ten CR classes exceed 0.07 % |
| "integrated understates JUNCTIONS' top class by **3.6×**" | **amended to 2.6×** on the other arm (2.9× CLOSEPACKING). The per-class requirement is unchanged, and stronger |
| "MONASH is an exact zero" | **explained, not contradicted.** Same 62 restorations, different winners, Δ = 0.0006 ± 0.0002 %. Confirms this document's own reading that the zero was an *exposure* statement |

**The systematic to quote is the LARGEST-index arm, per class** (owner ruling) —
see §4 of the robustness document, **not the table above**. This document's
numbers are the **cross-check** that establishes rule dependence; they are not a
lower bound, and the pair is **not an envelope**. Neither ordering bounds the
space of resolutions: a pT-ordered rule would give more, which is why the
pre-registration rejected it as inflating by construction.

**And a pre-registered assumption was falsified.** The winner rule was chosen
because `heavyIndex` was believed *"deliberately uncorrelated with pT"*. Both
arms restore an **identical** number of rows, so the 2–5.5× difference is
entirely in how often the winner survives the trigger selection: `heavyIndex`
**is** correlated with trigger survival, and neither direction is the neutral
one.

## PROVENANCE

| | |
|---|---|
| variation macro | `a4df31e6b6da5098d40b793a0c3616957457b326bcef48538bbe271b05f38553` |
| superseded macro | `22120383b07eb3572660f9a2aa7c895dd260ee23c7bc349a5a2e4f76262256de` (guard-only diff; outputs preserved in `a2_runs/permissive_guarded_22120383`) |
| deploy commit | `61fe978f66c00e8467f88c00d677462292dd5a1c`, injected via `HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT` |
| campaign | Condor `5486752` (permissive, 300), `5486605` (regression, 1) |
| baseline | committed `per_job/<TUNE>/slot_000…099`, not re-run |
| ROOT | `/cvmfs/alice.cern.ch/…/ROOT/v6-30-01-alice5-2` on the workers; LCG 105 (6.30/02) for extraction and analysis |
| yields | `a2_runs/yields/{baseline,permissive}_<TUNE>.csv`, sha256 recorded in the session record |
