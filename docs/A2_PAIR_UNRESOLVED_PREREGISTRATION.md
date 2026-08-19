# A2 — the pair-level unresolved-origin systematic: PRE-REGISTRATION

**Written and committed 2026-08-13, before the variation was built and before
any job ran.** Nothing below was chosen after seeing a result.

---

## 1. WHY THIS EXISTS

The external review (finding **A2**) established that
`Validation/MeasureUnresolvedSystematic.C` applies **no** trigger, ground-state,
acceptance, pair, multiplicity or OS−SS selection: its only cut is
`heavyIsFinal && q_sector != 0`. It measures an **inclusive** rate and an
**inclusive** baryon fraction. Those numbers are real and are now labelled as
inclusive everywhere.

**They cannot bound the observable.** The paper's observable is a *directed,
conditional, multiplicity-binned OS−SS yield* after the full trigger/associate
selection. A global rate cannot bound a multiplicity-localized effect: a
systematic that is 0.1 % integrated can be several percent in the highest
multiplicity class and still average to 0.1 %.

**This measures the real thing.**

## 2. WHAT IS ALREADY KNOWN (inclusive level, for calibration only)

| tune | inclusive unresolved rate % | inclusive baryon-fraction relative shift % |
|---|---|---|
| MONASH | **0.085** | 0.045 |
| JUNCTIONS | **1.15** | 0.55 |
| CLOSEPACKING | **1.13** | 0.51 |

The CR tunes carry ~13.5× MONASH's unresolved rate. **These are the inclusive
numbers and are not predictions for the pair level.**

## 3. THE MECHANISM BEING VARIED — stated exactly

In the producer (`generation/producer/heavyflavourcorrelations_status.cpp:1217`),
`EnforceUniqueFinalHardCarrier` groups final, sector-charged hadrons by the
selected hard quark each claims (`matchedHard`). Where **two or more** hadrons
claim the **same** hard quark, the assignment is not distinguishable from the
event record, and **production demotes every claimant** to
`Origin::kUnresolved` with `MatchResolution::kDuplicateHardCarrier` and
`matchedHard = -1`.

The analysis then drops such candidates as **triggers**
(`analysis/status_analysis_THnSparse_qq.C:993,1002` — `origin != kSelectedHard`,
or `triggerHard < 0`). **Associates are unaffected**: they are never required to
be `kSelectedHard`.

**The variation is possible without re-generating anything** because the
producer preserves the discarded claim: it snapshots `originalMatchedHard`
before enforcement and writes it to `heavyRejectedHardC/B` for exactly the
demoted rows (`:1229-1239`). The raw record therefore states, per hadron, which
hard quark it contested.

## 4. THE PERMISSIVE RULE — the variation, stated precisely

Applied per event, and **independently per sector** (charm, beauty), to local
copies of the branch vectors. Production output is never modified.

A row `i` is **eligible for restoration** iff all of:

1. `heavyIsFinal[i] == 1`
2. `sectorCharge_s(i) != 0`
3. **`|sectorCharge_s(i)| == 1`**
4. `heavyMatchResolution_s[i] == kDuplicateHardCarrier`
5. `heavyRejectedHard_s[i] >= 0`

**Condition 3 is not cosmetic.** `RejectFinalMultiHeavyCarrier` independently
rejects any final hadron carrying more than one same-sign quark of that sector,
for a reason that has nothing to do with the tie-break. Restoring those would
measure a different variation than the one declared.

Eligible rows are grouped by `heavyRejectedHard_s[i]`. Within each group,
**exactly one winner** is restored:

> **The winner is the row with the smallest `heavyIndex`** (the PYTHIA
> event-record index), which is unique within an event.

For the winner: `heavyOrigin_s = kSelectedHard` and
`heavyMatchedHard_s = heavyRejectedHard_s`. Every other member of the group is
left exactly as production left it — unresolved, `matchedHard = -1`.

**Why smallest index and not, say, highest pT.** The tie-break must not
correlate with the observable. A pT-ordered rule preferentially restores hadrons
that pass the trigger pT cut, which would inflate the measured shift by
construction. The event-record index carries no such correlation. **The choice
of winner is a sub-leading ambiguity inside the bracket**; the bracket's
endpoints are "drop all claimants" (production) and "keep one" (this variation),
and that is what is being measured.

> ### ⚠ POST-HOC ANNOTATION, 2026-08-13 — the paragraph above is FALSIFIED
>
> **Nothing registered above has been altered, and it must not be.** This note
> records what the measurement then found, which is the whole point of writing
> the reasoning down in advance where it could be checked.
>
> **Both of its claims are wrong**, measured by running the opposite tie-break
> (`docs/a2_results_20260813/A2_TIEBREAK_ROBUSTNESS.md`):
>
> 1. *"The event-record index carries no such correlation."* It does. The
>    largest-index rule yields Δ **2.0–5.5× larger** than the smallest-index
>    rule in all ten CR classes, at 2.7–21.6 σ. Since both arms restore an
>    **identical** number of rows, that difference is entirely in how often the
>    winner survives the trigger selection.
> 2. *"The choice of winner is a sub-leading ambiguity inside the bracket."* It
>    is the **dominant** uncertainty on the magnitude — larger than every block
>    SEM in the measurement.
>
> **What survives:** the multiplicity SHAPE, which rises 5.9–9.7× across the
> classes in *both* directions. The trend A2 is about is real and is not a
> tie-break artefact.
>
> **Consequence (owner ruling):** the systematic is quoted from the
> **largest-index** rule, per class; the smallest-index rule is reported beside
> it as the cross-check that establishes rule dependence. The smallest-index
> rule is no longer treated as the neutral choice, because there isn't one.
>
> **This pair is not an envelope**, and the paragraph above is the reason. Both
> are extremal orderings *of `heavyIndex`*; a **pT-ordered** rule would exceed
> them, and the argument above for rejecting it — that it inflates the shift by
> construction — **still stands**. What was wrong was the claim that
> `heavyIndex` avoids that problem, not the claim that pT ordering has it.

**The rule preserves hard-carrier uniqueness by construction** — exactly one row
per contested index is restored, and a contested index cannot also be held by a
non-conflicted row (such a row would have been in the conflict group). So the
analysis's own fail-closed check on duplicate hard constituents
(`:1155`, `throw` on `sameHardConstituentPairs != 0`) remains a **live** check
against this variation rather than being disabled by it.

## 5. SCOPE, SLOTS, BLOCKS

| | |
|---|---|
| slots | **`slot_000` … `slot_099`** per tune — the first 100 canonical slots |
| tunes | MONASH, JUNCTIONS, CLOSEPACKING → **300 jobs** |
| baseline | the **committed** `per_job` outputs for those same slots — not re-run |
| blocks | **`canonical_slot % 10`**, ten blocks of ten slots |
| SEM | `stdev(ten block values)/√10`, **dof = 9** |

**Blocking is by `canonical_slot % 10`** to match the project's canonical block
construction (`ERROR_RECORD`/A3: blocks are FILE/JOB blocks, not event-modulo),
so these SEMs are formed the same way as every other SEM in the project.

## 6. THE OBSERVABLE

For each tune, each multiplicity class **m**:

```
Y(m) = Σ_OS-pairs N(m)  −  Σ_SS-pairs N(m)
```

integrated over the full Δφ/Δη acceptance of `hCorrelations` (axis 6 is
`multiplicity_primary_charged_eta10_v1`), summed over the pair registry's OS and
SS files respectively. The reported quantity is the **relative shift**

```
Δ(m) = [ Y_permissive(m) − Y_baseline(m) ] / Y_baseline(m)
```

formed **inside each block** and then averaged over the ten blocks, with the SEM
over those ten values. Forming the ratio inside the block before averaging is
the project's standing estimator rule for nonlinear quantities.

**Multiplicity classes**, on primary charged multiplicity in |η| < 1.0, fixed in
advance:

| class | N_ch |
|---|---|
| **M1** | 1–9 |
| **M2** | 10–19 |
| **M3** | 20–29 |
| **M4** | 30–39 |
| **M5** | ≥ 40 |

⟨N_ch⟩ is ~12.9 (MONASH MB), so M4 and M5 are tail classes. **Any class whose
baseline yield is below 10³ weighted pairs in a block is reported but flagged
`LOW-STAT` and excluded from the per-class-vs-integrated comparison** — a class
too sparse to measure cannot falsify flatness.

## 7. WHAT IS EXPECTED — stated so it can be wrong

1. **Sign.** The permissive rule can only **add** triggers, so it can only add
   pairs. `Δ(m) ≥ 0` is expected in every class. **A negative Δ outside 2 SEM
   would mean the variation is not doing what this document says**, and is a
   STOP-and-diagnose, not a result.
2. **Scale.** The pair-level shift is expected to be **at or below the inclusive
   unresolved rate** — ≲0.09 % for MONASH, ≲1.2 % for the CR tunes — because the
   trigger selection (central, ground state, acceptance, pT) is far tighter than
   the inclusive `isFinal && q≠0`, and only the duplicate-carrier subset of
   unresolved candidates can be restored at all.
3. **Ordering across tunes.** **CR ≫ MONASH**, tracking the inclusive rates
   (~13× ). If the CR tunes do *not* exceed MONASH substantially, the pair-level
   effect is not driven by the same mechanism as the inclusive one, which is
   itself reportable.
4. **Multiplicity dependence — the reason this measurement exists.**
   Duplicate hard-carrier claims arise when one fragmenting string or junction
   system feeds several final heavy hadrons. That is a **dense-string**
   configuration, so it should be **more common at high multiplicity**.
   **Δ(m) is expected to increase with m**, and most steeply in the CR tunes,
   where junction/reconnection topologies are exactly what is being added.
   **A flat Δ(m) is a real possible outcome and would be reported as such** — it
   would mean the integrated number does bound the observable after all, and
   would retire the concern A2 raised.

## 8. THE THRESHOLDS — fixed before measuring

Let Δ_int be the multiplicity-integrated relative shift and Δ(m) the per-class
values, each with block SEM σ(m).

| verdict | condition |
|---|---|
| **NEGLIGIBLE** — need not be quoted | \|Δ(m)\| < **0.1 %** in every non-LOW-STAT class **and** every Δ(m) within **2 σ(m)** of zero |
| **QUOTABLE AS ONE NUMBER** | not negligible, **and** every non-LOW-STAT Δ(m) within **2 σ(m)** of Δ_int |
| **MUST BE QUOTED PER MULTIPLICITY CLASS** | any non-LOW-STAT Δ(m) differs from Δ_int by **> 2 σ(m)**, **or** max Δ(m) − min Δ(m) exceeds **50 % of Δ_int** |

**The falsification statement.** "The systematic is negligible" is falsified if
**any** non-LOW-STAT class shows \|Δ(m)\| ≥ 0.1 % at ≥ 2 σ. **"The integrated
number bounds the observable" is falsified** if the per-class condition above is
met — which is precisely the claim A2 said had never been tested.

## 9. POSITIVE CHECKS — required before any number is reported

1. **The regression check.** Built with the permissive rule **disabled**, the
   variation must reproduce a committed `per_job` output **byte-identical** for
   at least one slot. *A variation that cannot reproduce the baseline is not a
   variation.* Failure here stops everything.
2. **The rule must do something.** With the rule enabled, the count of restored
   rows must be **> 0** and must be **reported per tune**. A silent zero would
   make every Δ trivially zero and would look like a clean null.
3. **Uniqueness holds.** The analysis's `sameHardConstituentPairs` throw must
   **not** fire on any variation job. It is the independent check that the
   restoration did not create a double-counted carrier.
4. **Scratch deploy, sha-pinned.** The variation runs from a scratch tree with
   its own macro sha recorded in the job manifest; **the frozen checkout is read
   for `setupEnv.sh` only and never written** (the M7b pattern).

## 10. WHAT THIS MEASUREMENT DOES NOT DO

- It does **not** decide which tie-break is physically right. It brackets
  drop-versus-keep. The winner rule is stated so the bracket is reproducible,
  not because it is correct.
- It does **not** replace the inclusive M7 numbers; both are reported, labelled.
- It does **not** cover any other unresolved-origin cause. `kUnresolved` also
  arises from failed ancestry walks and multi-heavy rejection; **only the
  duplicate-hard-carrier subset is variable from the committed raw record**, and
  the others are out of scope and stated as such.
- **100 slots, not 1000.** This is a systematic, not a central value.
