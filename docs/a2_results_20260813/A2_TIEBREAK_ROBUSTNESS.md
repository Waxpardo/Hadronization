# A2 — the tie-break robustness check: the SHAPE survives, the MAGNITUDE does not

**2026-08-13.** The pre-registration picks the winner of a contested hard index
by **smallest** `heavyIndex`. Δ exceeded the negligible threshold for both
colour-reconnection tunes, which triggers the robustness clause: re-run with the
opposite tie-break and see whether the multiplicity dependence is a property of
restoring one claimant or an artefact of *which* claimant was named.

| | |
|---|---|
| variation | `permissive_largest_index`, macro `4e491134d8d3a2b4b6ed4cc2f5dba4c70115e6695de35baae159f080717240f1` |
| derived from | `permissive_smallest_index` (`a4df31e6…`) — the diff is **one comparison operator and its comment**, nothing else |
| regression | **PASS**: 300 files, 300 diffs, every one the single allowed `analysis_macro_sha256` field, zero unexpected |
| campaign | Condor `5489612` (300 jobs, 13 min, 300/300 promoted, zero held); regression `5489016` |
| baseline | the **same committed** `per_job` output as the first arm — not re-run |

Every number below is the analyzer's own output, preserved verbatim in
`tiebreak_robustness/`.

---

## THE ANSWER, IN ONE LINE

> **The multiplicity dependence is REAL and survives the tie-break flip — both
> rules rise 5.9–9.7× across the classes. Its SIZE does not survive: the
> opposite direction is 2.0–5.5× larger, everywhere, in both CR tunes.**

So the check did **not** come back clean, and it did not come back useless
either. **The shape is confirmed and the magnitude is shown to be
rule-dependent**, and the quoted systematic is the larger of the two rules —
see §4.

---

## 1. THE SHAPE — ROBUST

Each arm normalised to its own M1, so this compares *trend* and ignores scale:

| tune | arm | M1 | M2 | M3 | M4 | M5 | rise |
|---|---|---|---|---|---|---|---|
| JUNCTIONS | smallest | 1.00 | 3.54 | 4.49 | 5.17 | 9.68 | **9.7×** |
| JUNCTIONS | **largest** | 1.00 | 2.71 | 3.95 | 5.92 | 5.37 | **5.9×** |
| CLOSEPACKING | smallest | 1.00 | 2.24 | 3.72 | 6.27 | 4.29 | **6.3×** |
| CLOSEPACKING | **largest** | 1.00 | 2.68 | 4.17 | 4.71 | 6.08 | **6.1×** |

**Both arms rise by a factor of 5.9–9.7 across the multiplicity classes.** The
rise is monotonic in three of the four series; in the fourth the M5 point sits
below M4, and M5 carries the largest SEM in every series, in both arms.

> **The tie-break direction does not manufacture the multiplicity trend.** That
> is what this check was for, and on that question the answer is clean. A2's
> concern is confirmed under both rules, not just the pre-registered one.

## 2. THE MAGNITUDE — NOT ROBUST

Δ per class, per cent, both arms:

| tune | class | smallest (pre-registered) | **largest** | ratio | they differ by |
|---|---|---|---|---|---|
| MONASH | M1 | 0.0000 ± 0.0000 | 0.0004 ± 0.0002 | — | 2.0 σ |
| MONASH | M2 | 0.0000 ± 0.0000 | 0.0011 ± 0.0004 | — | 2.8 σ |
| MONASH | M3 | 0.0000 ± 0.0000 | −0.0003 ± 0.0006 | — | 0.5 σ |
| MONASH | M4 | 0.0000 ± 0.0000 | 0.0017 ± 0.0012 | — | 1.4 σ |
| MONASH | M5 | 0.0000 ± 0.0000 | 0.0037 ± 0.0037 | — | 1.0 σ |
| MONASH | **int** | **0.0000** | **0.0006 ± 0.0002** | — | 3.0 σ |
| JUNCTIONS | M1 | 0.0072 ± 0.0010 | 0.0255 ± 0.0024 | 3.54 | **7.0 σ** |
| JUNCTIONS | M2 | 0.0255 ± 0.0012 | 0.0691 ± 0.0029 | 2.71 | **13.9 σ** |
| JUNCTIONS | M3 | 0.0323 ± 0.0060 | 0.1007 ± 0.0094 | 3.12 | **6.1 σ** |
| JUNCTIONS | M4 | 0.0372 ± 0.0045 | 0.1509 ± 0.0196 | 4.06 | **5.7 σ** |
| JUNCTIONS | M5 | 0.0697 ± 0.0124 | 0.1369 ± 0.0215 | 1.96 | **2.7 σ** |
| JUNCTIONS | **int** | **0.0194 ± 0.0014** | **0.0583 ± 0.0026** | 3.01 | **13.2 σ** |
| CLOSEPACKING | M1 | 0.0098 ± 0.0008 | 0.0377 ± 0.0019 | 3.85 | **13.5 σ** |
| CLOSEPACKING | M2 | 0.0220 ± 0.0026 | 0.1012 ± 0.0049 | 4.60 | **14.3 σ** |
| CLOSEPACKING | M3 | 0.0365 ± 0.0046 | 0.1571 ± 0.0130 | 4.30 | **8.7 σ** |
| CLOSEPACKING | M4 | 0.0614 ± 0.0095 | 0.1777 ± 0.0183 | 2.89 | **5.6 σ** |
| CLOSEPACKING | M5 | 0.0420 ± 0.0135 | 0.2293 ± 0.0319 | 5.46 | **5.4 σ** |
| CLOSEPACKING | **int** | **0.0192 ± 0.0007** | **0.0795 ± 0.0027** | 4.14 | **21.6 σ** |

**The largest-index arm is bigger in all ten CR classes**, by 2.0–5.5×, and the
difference is significant in every one of them.

---

## 3. THE METHOD FINDING — a reasoned assumption, measured and falsified

> **This is a result of the study, not a footnote on its scoring.** The
> pre-registration did not pick smallest-`heavyIndex` arbitrarily. It picked it
> on an explicit, reasoned argument: the tie-break must not correlate with the
> observable, a pT-ordered rule would inflate the shift by construction, and the
> event-record index was held to carry no such correlation. That argument was
> written down before any job ran, which is the only reason it could be tested.
>
> **It is false.** Identical restoration counts with 2–5× different Δ can only
> mean the index correlates with trigger survival. The registered text is left
> **unedited**; a marked annotation beside it carries the correction.
>
> The transferable lesson is about method, not about A2: **a tie-break defended
> as neutral is an empirical claim about the data, and it is cheap to check by
> running the other direction.** Within a single arm the choice is invisible, so
> nothing else in the measurement could have surfaced it.

**The two arms restore exactly the same number of rows.** Not approximately —
identically:

| tune | restored charm | restored beauty | contested seen | per M events |
|---|---|---|---|---|
| MONASH | 60 | 2 | 124 | 6.2 |
| JUNCTIONS | 12 016 | 178 | 24 411 | 1 219.4 |
| CLOSEPACKING | 12 114 | 173 | 24 590 | 1 228.7 |

These are the same in both arms, which is exactly as it must be: the rule
restores **one winner per contested hard index**, and flipping the direction
changes *which* row wins, never *how many*.

> **So the entire 2–5.5× difference comes from how often the winner survives the
> trigger selection** — central, ground state, acceptance, pT > 1 GeV. The
> largest-index claimant passes it several times more often than the
> smallest-index one.

That is a direct measurement of a correlation the pre-registration assumed away.
Its own words, in the macro comment that selects the winner:

> *"the row with the SMALLEST heavyIndex — deterministic, and **deliberately
> uncorrelated with pT** so the tie-break cannot inflate the measured shift by
> preferentially restoring rows that pass the trigger pT cut."*

**`heavyIndex` is not uncorrelated with trigger survival.** If it were, both
directions would give the same Δ within errors, and instead they differ by up to
21.6 σ. The rationale for preferring the smallest-index rule does not hold, and
neither direction can now claim to be the neutral one.

**This is the check paying for itself.** The assumption was stated in advance,
in writing, and was wrong; nothing else in the measurement would have revealed
it, because within a single arm the choice is invisible.

---

## 4. WHAT MUST BE QUOTED NOW — owner ruling, 2026-08-13

**Quote the LARGEST-INDEX arm, per multiplicity class.** It is the output of a
real, deterministic rule — not a synthetic bound — and it is the more
conservative of the two measured orderings. Per cent, with block SEMs (dof 9):

| tune | M1 | M2 | M3 | M4 | M5 |
|---|---|---|---|---|---|
| MONASH | 0.0004 ± 0.0002 | 0.0011 ± 0.0004 | −0.0003 ± 0.0006 | 0.0017 ± 0.0012 | 0.0037 ± 0.0037 |
| **JUNCTIONS** | 0.0255 ± 0.0024 | 0.0691 ± 0.0029 | 0.1007 ± 0.0094 | **0.1509 ± 0.0196** | 0.1369 ± 0.0215 |
| **CLOSEPACKING** | 0.0377 ± 0.0019 | 0.1012 ± 0.0049 | 0.1571 ± 0.0130 | 0.1777 ± 0.0183 | **0.2293 ± 0.0319** |

**MONASH is NEGLIGIBLE** — every class is below 0.004 %, ~25× under the
pre-registered threshold. **The CR tunes are quoted per class**; the integrated
values (JUNCTIONS 0.0583, CLOSEPACKING 0.0795) understate the worst class by
**2.6×** and **2.9×** and must not be substituted.

**The smallest-index arm (§2) is reported alongside as the cross-check**, and
its role is to establish that the result is **rule-dependent**: the two
orderings differ by **2.0–5.5×**, significant in all ten CR classes. It is not a
lower bound on anything; it is the second of two measurements.

### ⚠ This is NOT an envelope, and must not be described as one

**What is quoted is the larger of two extremal orderings of `heavyIndex`.** That
is a statement about two specific rules, not about the space of possible
resolutions of a contested hard index.

> **Neither ordering bounds that space.** A **pT-ordered** tie-break would give a
> larger Δ than either — it preferentially restores exactly the hadrons that
> pass the trigger pT cut. The pre-registration rejected it for precisely that
> reason, as inflating the measured shift *by construction*
> (`A2_PAIR_UNRESOLVED_PREREGISTRATION.md` §"Why smallest index"), and that
> rejection still stands: a rule that is wrong on purpose is not a bound.

So "0.1509 %" means *the largest-index rule gives 0.1509 % in JUNCTIONS M4*, not
*the systematic cannot exceed 0.1509 %*. The honest claim is the first one, and
the difference matters if anyone later wants a true bound.

### The shape is what licenses per-class quoting

**Lead with §1, not with the numbers above.** The 5.9–9.7× rise across the
multiplicity classes holds under **both** rules. That is the robust finding, and
it is what makes per-class quoting mandatory rather than stylistic: a single
integrated number is wrong about the shape in a way no choice of tie-break
repairs.

### Three statements from the first arm are now retired

1. **"No class exceeds 0.07 %."** Under the other direction seven of the ten CR
   classes exceed it, and CLOSEPACKING M5 reaches **0.229 %**.
2. **"The integrated value understates JUNCTIONS' top class by 3.6×."** Still
   true in kind, different in size: the largest-index arm understates by 2.6×
   (M4 / integrated), and CLOSEPACKING by 2.9×. **The per-class requirement is
   unchanged and if anything stronger.**
3. **"MONASH is an exact zero."** True of the pre-registered arm only, and this
   check explains it rather than contradicting it — see below.

### The pre-registered negligible threshold

0.1 %. The smallest-index arm sat entirely below it; the largest-index arm
**crosses it** in JUNCTIONS M3/M4/M5 and CLOSEPACKING M2/M3/M4/M5. The
systematic is still sub-percent everywhere — the largest value anywhere is
0.23 % — but it can no longer be described as an order of magnitude below the
threshold that was set for it.

---

## 5. MONASH — the exact zero, explained rather than contradicted

The first arm measured **exactly** 0.0000 with zero variance, and that record
argued at length that this was an **exposure** statement and not a mechanism
one: 62 restored rows in 10 M events, each still required to pass the full
trigger selection, so zero survivors is unremarkable. It warned specifically
against reading it as *"the effect does not exist in MONASH."*

**This arm confirms that reading, independently.** Same 62 restorations,
different winners, and now a non-zero Δ of 0.0006 ± 0.0002 %. The mechanism was
always live; the first arm's winners simply never survived the selection.

The supporting evidence is byte-level: the smallest-index arm's
`permissive_MONASH.csv` is sha `ac6a7898…`, **identical to its baseline** — which
is why Δ was exactly zero. The largest-index arm's is `8a15f9be…`, and differs.

> The mechanical verdict for MONASH-largest prints **MUST BE QUOTED PER
> MULTIPLICITY CLASS**, and that is an artefact worth naming. The pre-registered
> negligible test is a **conjunction**: |Δ| < 0.1 % **and** |Δ| ≤ 2 SEM. MONASH-
> largest passes the magnitude leg by a factor of ~90 and fails the significance
> leg on M2 (0.0011 ± 0.0004, 2.8 σ). With 100 slots the SEMs are small enough
> that a physically trivial 0.001 % becomes statistically resolvable.
> **MONASH remains NEGLIGIBLE on the magnitude that matters**, and the printed
> verdict should be read with the conjunction in mind.

---

## 6. WHAT THIS DOES NOT SETTLE

**Two directions are not a distribution, and they are not a bound.** Smallest
and largest are the two extremal orderings *of `heavyIndex`*. They say nothing
about rules that order by something else: a random-winner rule, or a pT-ordered
one, can sit **outside** the pair, not between them. A pT-ordered rule
demonstrably would — it restores exactly the hadrons that pass the trigger pT
cut, which is why the pre-registration rejected it as inflating by construction.
**§4 quotes the larger of two measured rules; it does not claim an extremum.**

**The correlation in §3 is measured, not explained.** That later-indexed heavy
quarks pass the trigger selection more often is now a fact about this sample; no
mechanism for it is offered here, and finding one would need a study of
`heavyIndex` against pT and ancestry that has not been done.

**Both arms share the same baseline.** The comparison is between two
variations, and any defect in the common baseline cancels in the ratio and would
be invisible to this check.

## PROVENANCE

| | |
|---|---|
| variations registry | `config/a2_variations_v1.json` (both arms, named, sha-pinned) |
| regression sentinels | `docs/a2_regression_pass_permissive_{smallest,largest}_index.json` |
| builder | `tools/a2_make_largest_index_variation.py` (asserts its source sha) |
| submit generator | `tools/a2_make_subs.py --variation permissive_largest_index --deploy-commit 61fe978f…` |
| scratch tree | `/data/alice/ipardoza/a2_variation_largest` (copy of the verified tree; only the macro differs) |
| deploy commit | `61fe978f66c00e8467f88c00d677462292dd5a1c`, injected via `HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT` |
| yields | `a2_runs/yields/permissive_largest_<TUNE>.csv`, 150 001 rows each, 100 distinct slots |
| analyzer outputs | `tiebreak_robustness/{smallest,largest}_<TUNE>.txt`, verbatim |
| ROOT | `/cvmfs/…/ROOT/v6-30-01-alice5-2` on the workers |

**The smallest-index numbers in this document were re-run through the refactored
analyzer**, not copied from the earlier record, and they reproduce it exactly —
which is also the check that the gate refactor changed nothing in the physics
path.
