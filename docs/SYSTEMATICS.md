# Systematic uncertainties — the living document

> ## HARVEST IN PROGRESS — 2026-08-18
>
> The seven variation campaigns are **complete at 2100/2100 raw files**, preflighted
> at full rigour (exact-filename presence, sidecar↔receipt cross-check, byte
> re-hash — all 2100 clean), and the analysis stage is running.
> **Run record: [`docs/SYSTEMATICS_HARVEST_RUN_RECORD.md`](SYSTEMATICS_HARVEST_RUN_RECORD.md).**
>
> **The PENDING cells below are still PENDING** — the chain from raw to per-class
> numbers is a multi-day pipeline whose cost is measured in that record §6. **Two
> combination-stage decisions are blocked on the owner** (§7 there): how an
> unresolved per-class Δ enters the quadrature (the pre-registration is silent,
> and the three options differ by 20 % on a worked example), and whether S6/A2
> enters the per-class sum at all (the brief says yes; pre-registration §9.6
> registers a rule that it does not, because it is on a five-class axis).
>
> **One thing that could have invalidated every Δ was checked and is clean:** the
> analysis macro's sha differs from the central campaign's, and the difference is
> six `#include` path rewrites from the restructure move, with the one changed
> header symbol not referenced by the macro. Details in that record §4.1.

**Status 2026-08-17.** The design is frozen in
[`docs/SYSTEMATICS_PREREGISTRATION.md`](SYSTEMATICS_PREREGISTRATION.md), written
and committed before any variation job was rendered. **This** document is where
results land. Empty cells say `PENDING` and carry the cluster id of the jobs that
will fill them, so a reader can tell "not measured yet" from "measured and
small".

**Two of six sources have numbers today: S6 (complete, 2026-08-13) and S5
(complete, and an exact zero). Three are queued, all 2100 jobs released and their
first outputs verified. One is deliberately not launched.**

**The deployment gate is PASSED** — the rebuilt producer reproduces the nominal
event tree value for value (§9), so variation numbers from it may be believed.

---

## 0. THE TABLE

Per cent, per multiplicity class, per tune. Block SEMs over ten blocks
(`slot % 10`, dof 9).

| # | source | variation | method | status | verdict |
|---|---|---|---|---|---|
| **S1a** | renormalisation scale | `SigmaProcess:renormMultFac` ×2 / ×0.5 | D1 per-block relative (§2.2); D2 absolute Δ, SEMs in quadrature | ✅ **BOTH ARMS DONE, BOTH DELIVERABLES 2026-08-19** | §7, §9 |
| **S1b** | factorisation scale | `SigmaProcess:factorMultFac` ×2 / ×0.5 | as S1a | ✅ **BOTH ARMS DONE, BOTH DELIVERABLES 2026-08-20** | §7, §9, §12 |
| **S2** | parton distribution | `PDF:pSet` 13 → 8 (NNPDF2.3 LO → CTEQ6L1) | as S1a, one-sided | ✅ **DONE, BOTH DELIVERABLES 2026-08-20** | §9, §12 |
| **S3** | `PhaseSpace:pTHatMin` | 2.0 → 1.0 and → 4.0 | as S1a | ✅ **BOTH ARMS DONE, BOTH DELIVERABLES 2026-08-19** | §7, §9 |
| **S4** | event-activity counter | `\|η\| < 1` → `\|η\| < 4`, percentile-preserving | not applicable, never launched | **NOT LAUNCHED, deliberately** (§5) | — |
| **S5** | decay-daughter class migration | boundaries × 1/(1 ± 0.00767) | structural, boundary shift applied to the sealed sample | ✅ **DONE 2026-08-17** | **EXACTLY ZERO — structurally insensitive, every class** |
| **S6** | pair-level unresolved origin | duplicate hard-carrier tie-break | tie-break flip on the `M1…M5` axis, never summed into `c1…c11` (A2) | ✅ **DONE 2026-08-13** | **MUST BE QUOTED PER CLASS** (CR tunes); MONASH negligible |

**Deliverable 1 (D1)** is the diquark-structure decomposition, §7. **Deliverable
2 (D2)** is the per-class and integrated balancing yield, §9. The two use
different estimators for the reason §9 gives, and they agree on the ordering of
the sources.

**THE COMBINATION IS DONE.** All seven campaigns closed on 2026-08-20 and
`extraction/combine_per_class.py`, which had refused since it was written, ran.
The combined systematic per class per tune is §12 and
[`COMBINED_SYSTEMATICS.md`](systematics_results_20260820/COMBINED_SYSTEMATICS.md).

**S4 is the only source with no measurement, and that is deliberate** (§5). The
pre-registration §9 rule that a partial quadrature sum understates is satisfied
for the six live sources; S4 was never launched and is quoted nowhere.

---

## 1. S6 — pair-level unresolved origin ✅

**The measurement to quote is the LARGEST-`heavyIndex` arm, per class** (owner
ruling 2026-08-13). Per cent, block SEMs, dof 9. Source of record:
[`docs/a2_results_20260813/A2_TIEBREAK_ROBUSTNESS.md`](a2_results_20260813/A2_TIEBREAK_ROBUSTNESS.md)
§4.

| tune | M1 | M2 | M3 | M4 | M5 |
|---|---|---|---|---|---|
| MONASH | 0.0004 ± 0.0002 | 0.0011 ± 0.0004 | −0.0003 ± 0.0006 | 0.0017 ± 0.0012 | 0.0037 ± 0.0037 |
| **JUNCTIONS** | 0.0255 ± 0.0024 | 0.0691 ± 0.0029 | 0.1007 ± 0.0094 | **0.1509 ± 0.0196** | 0.1369 ± 0.0215 |
| **CLOSEPACKING** | 0.0377 ± 0.0019 | 0.1012 ± 0.0049 | 0.1571 ± 0.0130 | 0.1777 ± 0.0183 | **0.2293 ± 0.0319** |

**MONASH is NEGLIGIBLE** — every class under 0.004 %, ~25× below the
pre-registered 0.1 % threshold.

**The cross-check arm** is the smallest-`heavyIndex` ordering
([`A2_DELTA_RESULT.md`](a2_results_20260813/A2_DELTA_RESULT.md)). Its role is
**not** to be a lower bound: it establishes that the result is **rule-dependent**,
the two orderings differing by 2.0–5.5× in all ten CR classes at 2.7–21.6 σ. That
rule dependence is what makes per-class quoting mandatory — an integrated number
is wrong about the shape under either rule.

> ### ⚠ Three things a reader must carry with this row
>
> 1. **It is NOT an envelope.** What is quoted is the larger of two extremal
>    orderings of `heavyIndex`. A pT-ordered tie-break would give more, and the
>    pre-registration rejected that rule as inflating by construction. "0.1509 %"
>    means *the largest-index rule gives 0.1509 % in JUNCTIONS M4*, not *the
>    systematic cannot exceed it*.
> 2. **The integrated values must not be substituted.** JUNCTIONS 0.0583,
>    CLOSEPACKING 0.0795 — they understate the worst class by **2.6×** and
>    **2.9×**.
> 3. **⚠ THIS ROW IS ON A DIFFERENT CLASS AXIS FROM THE REST OF THE TABLE.**
>    S6's `M1…M5` are `N_ch` 1–9, 10–19, 20–29, 30–39, ≥ 40 — five classes.
>    Every other source is on the production eleven, `c1…c11`, at half-integer
>    boundaries −0.5 … 32.5. **They are not the same partition and S6 may not be
>    added in quadrature to per-`c` values** until it is re-binned. §6 states the
>    rule; re-binning it is known future work, not something to be assumed away.

---

## 2. S5 — decay-daughter class migration ✅ **EXACTLY ZERO**

> **Every one of the eleven classes is STRUCTURALLY INSENSITIVE, in both arms,
> for all three tunes. Δ(c) = 0 exactly — not "consistent with zero".**

Machine-readable result:
[`docs/systematics_results_20260817/s5_class_migration.json`](systematics_results_20260817/s5_class_migration.json).
Tool: `tools/systematic_class_migration.py`.

**The bias: 0.767 %, re-measured on the production generator this session.**
`dN_ch/dη` = 7.040 under the experimental decay convention against 6.986 under
the exact production policy — PYTHIA **8.317**, 200 000 events per arm, both arms
**paired on one seed** so the shared event content cancels
(`ValidationReports/NCH_DECAY_POLICY_BIAS_8317.md`). The production counter
**undercounts** `N_ch` by that much, because the experimental primary definition
counts charm/beauty decay daughters and production disables those decays.

> **The 8.315 value was 1.327 % and it was carrying this entire source.** Against
> the 1.538 % that moves `c11`'s edge it left a margin of only **1.16**, on a
> superseded generator version. **Re-measured, the bias is 42 % smaller and the
> margin is a factor of 2.01** — the null is comfortable rather than fragile. Both
> arms rose from 8.315 (7.007 → 7.040 and 6.914 → 6.986), but the production-policy
> arm rose four times as much, which is what closed the gap.
>
> **Consequence beyond S5:** `docs/DESIGN_AND_RATIONALE.md` §3.5 and
> `NCH_CALIBRATION_20260730.md` both state the policy "costs 1.3 %", and the paper
> is required to state it. **On the production generator it is 0.77 %.**

**The transformation.** A relative bias δ on `N_ch` is equivalent, at fixed class
definition, to dividing every boundary by (1 + δ). Both signs are run.

**Why it is exactly zero.** `N_ch` is a count, so it is an integer; the committed
boundaries sit at half-integers, which the boundary artifact states is deliberate
("half-integer, so no integer `N_ch` is ambiguous about which class it falls
in"). A per-class observable is therefore a sum over a set of integer `N_ch`
bins, and a boundary move changes it **only if the move crosses an integer**. No
boundary does:

| class | nominal | ↓ arm | ↑ arm | move | shift needed to cross |
|---|---|---|---|---|---|
| c1 | -0.5 | -0.4962 | -0.5039 | 0.0039 | 100.00 % |
| c2 | 2.5 | 2.4810 | 2.5193 | 0.0193 | 20.00 % |
| c3 | 3.5 | 3.4734 | 3.5271 | 0.0271 | 14.29 % |
| c4 | 5.5 | 5.4581 | 5.5425 | 0.0425 | 9.09 % |
| c5 | 6.5 | 6.4505 | 6.5502 | 0.0502 | 7.69 % |
| c6 | 8.5 | 8.4353 | 8.5657 | 0.0657 | 5.88 % |
| c7 | 10.5 | 10.4201 | 10.5812 | 0.0812 | 4.76 % |
| c8 | 13.5 | 13.3972 | 13.6044 | 0.1044 | 3.70 % |
| c9 | 17.5 | 17.3668 | 17.6353 | 0.1353 | 2.86 % |
| c10 | 23.5 | 23.3211 | 23.6816 | 0.1816 | 2.13 % |
| **c11** | **32.5** | **32.2526** | **32.7512** | **0.2512** | **1.54 %** |

**Checked on real data, not only argued.** Re-projecting the three committed
minimum-bias samples (MONASH 172 429 events, JUNCTIONS 170 389, CLOSEPACKING
170 261; integer `N_ch` 0–175) under both shifted boundary sets moves **zero**
integers between classes and changes **zero** class populations, in all three
tunes. Maximum |relative Δ| = 0.000e+00.

**Block SEMs are exactly zero**, and that is the correct treatment rather than a
missing number: the same projection operator is applied to the same events, so
the per-block difference is identically zero for *any* block decomposition. An
exact zero has no sampling uncertainty.

> ### The null holds by a factor of 2.01 — after the input was re-measured
>
> `c11` needs a **1.538 %** shift to cross an integer; the bias is **0.767 %**.
> Two things still travel with this row:
>
> 1. **Any boundary above 65.2 would be migrated by this bias**, so a future
>    re-binning of the class axis does **not** inherit this null and must
>    re-measure S5. `tests/test_systematic_class_migration.py` asserts the
>    per-boundary margin exceeds the measured bias, so a re-binning that breaks the
>    null fails the suite rather than leaving a stale "exactly zero" here.
> 2. **The bias is measured on minimum bias, not on the production sample.** The
>    hard-heavy-flavour sample has far more heavy-hadron content per event, so its
>    bias is plausibly *larger*. Not measured. It is a real open edge rather than a
>    conservative choice, and it would become material only if the axis were
>    re-binned above `N_ch ≈ 65`.

**What the zero does not cover.** The bias still shifts the *percentile labels*
the classes carry — the MONASH-MB percentile of a fixed `N_ch` boundary changes
when the distribution shifts — so the paper's classes correspond to slightly
different experimental percentiles than their labels claim. **That is a labelling
caveat for the paper text, and this source must not be presented as covering
it.**

---

## 3. S1 — renormalisation and factorisation scale — PENDING

**Method.** Four campaigns, `SigmaProcess:renormMultFac` and
`SigmaProcess:factorMultFac` each at ×2 and ×0.5, varied **independently**. The
factor-of-two two-point variation is the standard convention for a
leading-order calculation, and this is LO 2→2 `HardQCD:hardccbar` + `hardbbbar`.
Both settings default to `1.` with range `0.1 … 10.` in the installed 8.317, so
both requested values are inside the sanctioned range, and the nominal cards set
neither.

**Why independently, when coherently would have been cheaper and given a bigger
number.** `μ_F` and the PDF (S2) act through the same object: the initial-state
parton flux. Folding `μ_F` into a combined scale number would entangle S1 with S2
and leave §6's independence assumption uninspectable. Varying `μ_F` alone makes
that correlation **measurable** — and §6 states in advance what to do in either
outcome.

**Sample size.** 100 jobs × 100 000 events per tune per campaign = 10 M events
per tune, 300 files. The A2 precedent at exactly this scale resolved a
0.02–0.23 % effect at 5–20 σ.

**Registered expectations** (pre-registration §3, stated so they can be wrong):
the two arms bracket the nominal with opposite signs in every class; the
decomposition fractions are nearly inert (≲ 0.5 %, and a shift above 2 % would
falsify the claim that the decomposition is a hadronisation observable);
per-class OS−SS moves more but still modestly (≲ 5 %) **because conditioning on
`N_ch` absorbs the activity change** — that is the falsifiable claim; and `μ_R`
dominates `μ_F`.

| deliverable | S1a ×2 | S1a ×0.5 | S1b ×2 | S1b ×0.5 |
|---|---|---|---|---|
| decomposition fractions | PENDING `5519094` | PENDING `5519095` | PENDING `5519096` | PENDING `5519097` |
| per-class OS−SS | PENDING `5519094` | PENDING `5519095` | PENDING `5519096` | PENDING `5519097` |

---

## 4. S2 — parton distribution — PENDING

**Method.** `PDF:pSet` 13 → 8, one alternate PYTHIA-internal set, no LHAPDF
dependency. Both named from the installed generator's own
`xmldoc/PDFSelection.xml`, not from memory:

| | `PDF:pSet` | set | `α_s(M_Z)` |
|---|---|---|---|
| **nominal** | 13 (the PYTHIA default, which `Tune:pp = 14` resolves to) | NNPDF2.3 QCD+QED LO | 0.130 |
| **alternate** | 8 | CTEQ6L1, LO | 0.1298 |

**Why CTEQ6L1.** Because `α_s(M_Z)` differs by 0.15 %, so the variation isolates
PDF **shape** and does not smuggle in an `α_s` change. `pSet = 14` — the same
NNPDF2.3 fit at `α_s = 0.119` — was rejected for exactly that reason: an 8 %
coupling change in a PDF costume, double-counting S1's `μ_R` arm. `pSet = 17`
(NNPDF3.1 LO) probes fit vintage rather than methodology. CTEQ6L1 is a different
collaboration, a different methodology, LO with an LO coupling, and a genuinely
used tune baseline.

**Registered expectation.** Smallest of the three generation-dependent sources
(≲ 1 % on per-class OS−SS, ≲ 0.2 % on the fractions). **No sign is registered** —
CTEQ6L1's gluon is harder than NNPDF2.3 LO's at some `x` and softer at others, so
an honest prediction is not available and any sign found is not evidence of
anything. **If S2 exceeds S1's `μ_R` arm, that is the headline**, and the paper's
framing of these as hadronisation observables would need qualifying.

| deliverable | status |
|---|---|
| decomposition fractions | PENDING `5519098` |
| per-class OS−SS | PENDING `5519098` |

---

## 5. S3 — `PhaseSpace:pTHatMin` — PENDING

**Nominal: 2.0**, read from
`generation/cards/pythiasettings_Hard_Low_ccbb_MONASH.cmnd:47` and ratified in
`ValidationReports/PTHAT_MULTIPLICITY_SCAN_8317.md`.

**Variation points taken FROM that scan**, its own adjacent measured points, which
are also the ×0.5 / ×2 pair matching S1's convention:

| `pTHatMin` | `dN_ch/dη` | vs minimum bias | |
|---|---|---|---|
| 1.0 | 4.973 | −28.6 % | **down arm** |
| **2.0** | **6.678** | **−4.2 %** | **NOMINAL** |
| 4.0 | 10.492 | +50.6 % | **up arm** |

0.5 was excluded: two steps away, and its −33.8 % is barely distinguishable from
1.0's −28.6 %, so it buys almost no information for a whole campaign.

**This closes a limitation the project wrote down for itself.** The scan's own
*Limits* section: "This measures *what the sample is*. It does not answer whether
the physics conclusion is robust to the threshold, which is a separate comparison
of the balancing observables at different `pTHatMin` values." S3 is that
comparison.

**The asymmetry is registered in advance.** The arms are symmetric in `pTHatMin`
and wildly asymmetric in what they do to the sample: 2.0 → 1.0 moves the MB
comparison by −24.4 points, 2.0 → 4.0 by +54.8. So the larger-arm rule will very
likely select 4.0, and the asymmetry is not a discovery.

**Registered expectation, and it is the one that matters.** Expected to be the
**largest** of the six. The falsifiable claim: **per-class OS−SS is invariant
under the threshold once conditioned on `N_ch`, to within 10 %.** If it is not,
`pTHatMin` is part of the **definition** of the paper's per-class observable and
must be quoted as such, not folded into an uncertainty. Those are materially
different papers, and this measurement decides which one is being written. A
near-null would be the strongest outcome — it would retire a concern open since
`NCH_CALIBRATION_20260730.md`.

| deliverable | 1.0 arm | 4.0 arm |
|---|---|---|
| decomposition fractions | PENDING `5519099` | PENDING `5519100` |
| per-class OS−SS | PENDING `5519099` | PENDING `5519100` |

The 1.0 arm is the one at risk of `LOW-STAT` in the tail classes: the scan
measured trigger yield per event *rising* with the threshold (charm +20.8 %,
beauty +68.1 % from 1.0 to 2.0), so the low arm has fewer usable triggers per
event. Registered as expected.

---

## 6. S4 — event-activity counter window — ⚠ BOUNDED RUN LAUNCHED, STAGE 1 OF 4 DONE

> ### STATUS 2026-08-20
>
> **Owner ruling: bound S4, do not run it at full campaign scale.** The subset
> is declared in advance in `SYSTEMATICS_HARVEST_RUN_RECORD.md` §25 — all three
> tunes, 100 of 1000 files each, named by logical id, with a narrow-classifier
> control arm on the same files. §25.2 gives the argument that a 10 % subset
> **bounds** rather than estimates: ruling A1 makes each source contribute
> `max(|Δ|, SEM(Δ))`, and at 10 % of the events `SEM` is about **√10 ≈ 3.2×**
> larger, so the subset can only inflate S4's contribution.
>
> **Recorded as a DEVIATION, not an amendment** (§25.4). The registered method
> was a full evaluation; this is a bound, and the registration below stands as
> written.
>
> **Stage 1 of 4 is done — the wide axis exists** (§26.4). Every control is
> exact: the fresh MB run reproduces the committed narrow anchor **bin for bin**
> in all three tunes, the two counters agree on `dN_ch/dη` to 0.6 %, and the
> narrow per-tune residual recomputes to the published 2.91 pp.
> Artifact: `systematics_results_20260820/s4/s4_wide_boundaries_v1.json`.
>
> **Stages 2 to 4 are not run**, so **S4's bound does not exist yet and S4 is
> not in the combination.** `systematics_results_20260820/COMBINED_SYSTEMATICS.md`
> and `VERDICT.md` both name the omission, under §9.5's rule *"listed rather
> than omitted"*.
>
> **⚠ The registration named a boundary source that cannot supply one** (§25.5).
> It derives the wide boundaries *"from the committed MB samples in
> `AnalysisScripts/anchors/b4_multiplicity_mb`"*, and those samples hold the
> narrow counter only — their producer,
> `Validation/CalibrateMultiplicityAgainstMinBias.C:177`, refuses any other
> counter and generates its own events. So the registration's *"no new
> generation"* does not hold for the boundary derivation. That is deviation D2,
> and it is a defect in the registration rather than a choice.
>
> **⚠ An unregistered finding, against the expected direction** (§26.5). Both
> axes recomputed through one code path: the per-tune MB residual is **2.912 pp**
> on the narrow axis — reproducing the published 2.91 exactly — and **3.537 pp**
> on the wide one. **The wide axis is 1.21× worse**, and every JUNCTIONS class is
> further from its label on it. The wide counter separates the tunes' activity
> distributions *more*, not less. This is the MB residual and not the per-class
> observable shift, so it does not settle expectation 1 below — but the reasoning
> behind that expectation does not hold for the one axis property now measured on
> both counters.

**Method.** Re-analyse with the classifier taken from the `|η| < 4` counter
instead of the nominal `|η| < 1`. Both are already stored in every raw file
(`docs/DESIGN_AND_RATIONALE.md` §3.5), so **no generation is needed** — this is a
re-analysis of the existing 3000 files at full statistics.

**Boundary convention, fixed now: percentile-preserving.** Each boundary is
recomputed as the wide-counter value at the same MONASH-minimum-bias percentile
the narrow boundary sits at, from the committed MB samples, keeping the
half-integer convention. Reusing the absolute numbers would compare class `c7` of
one axis against a different percentile of the other, and the shift would be
dominated by relabelling rather than physics.

**Registered expectation.** A wider window measures the same activity with less
relative fluctuation, so at fixed percentile the per-class observable should shift
only slightly (≲ 3 %), growing toward the tail classes where the narrow counter's
population is most fluctuation-contaminated. A flat shift would mean the two
counters are interchangeable — a clean simplification. A large shift would indict
the **narrow** counter and mean the paper's multiplicity axis is
fluctuation-dominated.

> **Why it is not queued.** An analysis job pins the repository commit it was
> rendered against. The Nikhef analysis checkout is frozen at `43e35be8`, read
> live by the running merge, and `STATE.md` PENDING #5 records the checkout
> advance as still blocked. Queuing S4 now would pin the old head and re-block
> the advance the moment it becomes possible.
>
> **Launch condition:** after the merge exits, the campaign is recorded COMPLETE,
> and the `STATE.md` PENDING #5 checkout advance has happened. Then render S4
> against the new head.

---

## 7. COMBINATION — and the assumptions that make it valid

Quadrature, per class, per tune, over the sources that are not NEGLIGIBLE, using
the larger arm per source:

```
σ_sys(c, tune) = sqrt( Σ_s Δ_s(c, tune)² )
```

**Quadrature is only valid if these hold, so they are stated rather than
assumed:**

1. **S1b (`μ_F`) and S2 (PDF) are NOT independent** — both act on the
   initial-state parton flux. **Rule: if both are non-negligible, quote the
   larger and drop the other from the sum.** If one is negligible the question
   does not arise. §3's measurement decides which case applies, and it must be
   reported either way.
2. **S1a (`μ_R`) and S1b (`μ_F`) are treated as independent** and both enter.
   They act through different objects — the coupling and the parton density — and
   running them separately is what lets this be said rather than assumed.
3. **S3 and S1 are treated as independent, and this is the weakest assumption.**
   A threshold cut and a scale choice both change the hard-parton `pT` mix.
   Flagged, not resolved. If S3 is large, the right response is not quadrature
   but reconsidering whether it is an uncertainty at all.
4. **S4 is independent of everything** — identical events, different classifier,
   no shared generation-level input.
5. **S5 contributes exactly zero**, so it drops out arithmetically. It stays in
   the table because a zero that was *measured* is a different object from a
   source never examined.
6. **S6 is not added in quadrature to per-`c` values** — different class axis
   (§1). It is quoted as a separate line with its own `M1…M5` axis named, until
   re-binned.

**No total until every non-negligible source in a tune's column has a measured
value.**

### Two-sided sources: which arm

**The larger `|Δ(c)|`, per class**, with the other reported beside it as the
cross-check — the A2 owner ruling applied to new cases. **Not half the spread**
(which understates whenever the response is one-sided) and **never called an
envelope** (the two-point diagonal is a convention; a 7- or 9-point variation
reaches further).

---

## 8. WHAT IS DELIBERATELY NOT HERE

**The tune bundle is the measurement, not a systematic.** MONASH / JUNCTIONS /
CLOSEPACKING is the comparison the paper is *about*; the spread between them is
the result. Folding it into an uncertainty band would destroy the quantity being
reported. The known confound inside it — JUNCTIONS re-tunes the fragmentation
parameters that set baryon production, so a MONASH-vs-JUNCTIONS baryon difference
cannot be attributed to junctions alone — is a **limit on interpretation**,
documented in `STATE.md`, and `JUNCTIONS_MATCHED` exists to address it. It is not
a systematic either.

**Detector response is out of scope.** This is a generator-level study: no
unfolding, no efficiency, no resolution model, no acceptance beyond the stated
`|η| ≤ 4` and `pT` cuts. **No combination of these six sources may be presented
as a total uncertainty on a measurable quantity.**

---

## 9. PROVENANCE OF THE QUEUED CAMPAIGNS

| | |
|---|---|
| deploy | `/data/alice/ipardoza/systematics_deploy/Hadronization`, a real git clone, **tracked-clean** |
| deploy commit | `72ca4e3913da25be675dc2f968151ea68f9b8b87` |
| producer | rebuilt in the deploy, sha256 `379b449d56f8b3837c3ead142e33a814e6a350b1bdc5e93592368f358052f19b`, **zero warnings** |
| PYTHIA / ROOT | 8.317 (`pythia_stock_8317`) / 6.30.01 on pin, both asserted by `doctor` |
| seeds | `tools/campaign.py`, ordinals **4–10**, burned at render into `/data/alice/ipardoza/Hadronization/config/burned_seeds.txt` (untracked, git-ignored, so the frozen checkout stays clean) — 3557 → 5657 |
| card shas | 21 distinct effective card sha256, **none equal to any nominal** |
| submission | all seven `hold = True`, one pilot released per campaign before bulk release |

### First-output verification — passed, from the generator's own mouth

**The strongest available form of pre-registration §10.2**: not the card, the
value PYTHIA resolved. Each pilot's own settings dump, current value against
PYTHIA's default:

```
HF_SYS_MUR_UP        SigmaProcess:renormMultFac   2.00000  (default 1.00000)
HF_SYS_MUR_DOWN      SigmaProcess:renormMultFac   0.50000  (default 1.00000)
HF_SYS_MUF_UP        SigmaProcess:factorMultFac   2.00000  (default 1.00000)
HF_SYS_MUF_DOWN      SigmaProcess:factorMultFac   0.50000  (default 1.00000)
HF_SYS_PDF_CTEQ6L1   PDF:pSet                     8        (default 13)
HF_SYS_PTHAT_1       PhaseSpace:pTHatMin          1.00000  (nominal 2.00000)
HF_SYS_PTHAT_4       PhaseSpace:pTHatMin          4.00000  (nominal 2.00000)
```

**All seven pilots promoted `state = PASS`, `validator_status = 0`,
`errors=0 entries=100000 process_codes=4 stability_rows=219`, and all 2100 jobs
are released.** Seeds `140000001 … 200000001` — ordinal × 10⁷ + base, as
`seed_derivation_v2` requires.

The PDF line confirms **both** ends of S2 at once — the alternate is 8 and
PYTHIA's own default is 13, exactly as pre-registered.

First promoted outputs: `state = PASS`, `validator_status = 0`,
`RAW_VALIDATION_SUMMARY errors=0 entries=100000 process_codes=4
stability_rows=219`, with the full chain in the receipt — the **variant's** card
sha, the **rebuild's** producer sha, the **deploy's** commit. **The rebuilt raw
validator accepts output from the rebuilt producer**, which is the first
end-to-end evidence that the 46 → 49 audited-key change is self-consistent.

**The release was staged on the real risk, not uniformly.** The five
nominal-pTHat campaigns were bulk-released once two had promoted PASS; the pTHat
campaigns were held beyond their pilots because `ValidateRawOutput.C:603` fails
closed on "PhaseSpace:pTHatMin does not match authorization" — the one check that
could reject a whole campaign, and it had never been exercised away from 2.0.
**Both arms have since cleared it** (`phase_space_pthat_min` 1.0 and 4.0, PASS)
and were released. The 299 jobs held per arm in the meantime carried
`HoldReason = "submitted on hold at user's request"` — no faults anywhere in the
2100.

### ⛔ THE DEPLOY MUST NOT MOVE

`/data/alice/ipardoza/systematics_deploy/Hadronization` is pinned at
`72ca4e39` and **every one of the 2100 jobs verifies that commit at startup and
refuses to run if the tree has tracked modifications.** Do not check out, pull,
or edit tracked files there until the campaigns finish. Later commits on
`physics-focus` are fine — they are simply not in this deploy, which is the
point. A standalone macro needed during the campaign was copied to
`/data/alice/ipardoza/systematics_regression/` rather than added to the deploy,
for exactly this reason.

### Pre-registration §10.1 — the nominal-reproduction gate

**Required before any variation number is reported**: the rebuilt producer must
reproduce a committed **nominal** raw output's physics content. "A deployment
that cannot reproduce the nominal is not a variation of it."

**The bar is not byte identity, and choosing that bar would fail for legitimate
reasons** — the two files carry different `executable_sha256` and
`repository_commit`, and the audited-settings snapshot has three more rows. What
must match is the physics. **The nominal MONASH card and the producer translation
unit are byte-identical between the campaign commit `61fe978f` and the deploy
commit `72ca4e39`** (verified in git), so any difference in the event tree would
mean the registry-header change reached the event loop, which it must not.

> ## ✅ PASS — 2026-08-17. The event tree is identical, value for value.
>
> ```
> event tree entries: reference 100000, candidate 100000
> event tree leaves:  reference 110, candidate 110
> values compared:    36900000 vs 36900000
> event tree digest:  a6683ddd8ccae257 vs a6683ddd8ccae257
> EVENT TREE IDENTICAL -- every value, every entry
> NOMINAL_REPRODUCTION PASS metadata_fields_differing=7
> ```
>
> **36.9 million values across 110 leaves and 100 000 events, one digest.** The
> registry-header change did not reach the event loop.
>
> **All seven metadata differences are expected, and nothing else differs:**
>
> | field | reference → candidate | why |
> |---|---|---|
> | `executable_sha256` | `e54b27bb…` → `379b449d…` | the rebuild |
> | `repository_commit` | `e6429b77…` → `72ca4e39…` | the deploy |
> | `condor_cluster` | `5390385` → `0` | run by hand, not under Condor |
> | `elapsed_seconds` | 352 → 370 | timing |
> | `start_unix_seconds`, `end_unix_seconds` | — | timing |
> | `peak_rss_kib` | 543 580 → 548 348 | memory |
>
> **`tune_difference_allowlist_sha256` is NOT in that list, and that is the
> point.** The decision to put the three varied keys in a separate config file
> instead of the tune allowlist (§ the pre-registration's §11 annotation) is
> confirmed end to end: the variation campaigns' raw files carry the **same**
> allowlist digest as the central campaign's 3000, so the two sets remain
> cross-validatable. Neither `effective_settings_sha256` nor
> `effective_settings_entries` differs either — the exhaustive post-init snapshot
> is over PYTHIA's own settings, not over the audited-key list, so the 46 → 49
> change writes nothing into the raw metadata at all.
>
> Method: `Validation/CompareNominalReproduction.C`, leaf by leaf, entry by entry,
> on a job at campaign `HF_RUN3_V1`, ordinal 3, `MONASH` slot 0, its original seed
> `130000001`, with `HF_PRODUCTION_ROOT` pointed at a throwaway root so nothing
> was overwritten. **The two files are NOT byte-identical** — 92 200 277 against
> 92 200 782 bytes — which is exactly why the bar is content and not a checksum:
> the differing strings alone move the file size.

**Why a git clone and not an archive with the commit injected by environment.**
The A2 analysis deploy was an archive with no `.git`, which is why it needed
`HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT`. The production worker's commit check is
a **verification**, not a label — it compares `git rev-parse HEAD` against the
value the submit file recorded and refuses a tree with tracked modifications. A
clone keeps that guard doing its job; env injection would have reduced it to an
assertion. Nothing was weakened to run these campaigns.

**The merge was not touched.** It ran throughout on `stbc-i3` from
`/data/alice/ipardoza/Hadronization` at `43e35be8`; every step of this program
ran on `stbc-i1` against a separate deploy. The only write anywhere near the
frozen checkout is the append-only, git-ignored seed ledger.

---

## 7. S1a, S1b-down and S3 — the decomposition deltas ✅ (deliverable 1 only)

**2026-08-19.** Diquark-structure partition, per cent, against the sealed
`HF_RUN3_V1` nominal. Method: the registered estimator of
pre-registration 2.2. It forms the relative shift inside each block, then
averages over ten blocks, with the SEM over those ten and dof 9. Blocks are `canonical_slot % 10`.

**Full tables, all 60 cells:**
[`docs/systematics_results_20260819/PER_CATEGORY_DELTAS.md`](systematics_results_20260819/PER_CATEGORY_DELTAS.md).
Run record: [`SYSTEMATICS_HARVEST_RUN_RECORD.md`](SYSTEMATICS_HARVEST_RUN_RECORD.md) §15.

The largest shift per campaign and tune, in per cent:

| campaign | source | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|---|
| `HF_SYS_MUR_UP` | S1a up | 0.2854 ± 0.0565 | 0.1654 ± 0.4682 | 0.5870 ± 0.1774 |
| `HF_SYS_MUR_DOWN` | S1a down | −0.2181 ± 0.0845 | −0.5148 ± 0.1276 | −0.5875 ± 0.2155 |
| `HF_SYS_MUF_DOWN` | S1b down | 1.4540 ± 0.0719 | −7.0113 ± 0.4200 | −13.0501 ± 0.2818 |
| `HF_SYS_PTHAT_1` | S3 → 1.0 | −1.0648 ± 0.0581 | −5.0172 ± 0.3729 | −8.5373 ± 0.2810 |
| `HF_SYS_PTHAT_4` | S3 → 4.0 | 4.1877 ± 0.0447 | 5.4002 ± 0.3180 | 6.8655 ± 0.1624 |

Each cell is the largest `|Δ|` among the four categories, excluding
`kMultiplyHeavy`, whose blocks are LOW-STAT in every campaign.

**55 deltas quoted, 12 unresolved at 2 sigma, 5 not quotable.** The five are
every campaign's MONASH `kMultiplyHeavy`: the sealed nominal holds 8 counts in
total and individual blocks hold zero, so a relative shift has no meaning.

**No verdict on the 2.4 ladder appears here.** That ladder compares per-class
values against the multiplicity-integrated shift, and these numbers are on the
category partition rather than the class axis. §8 says why the class axis is
missing.

**No total, and no quadrature.** The combination needs all seven campaigns and
the pre-registration's closing rule forbids a partial sum.

---

## 8. What is still missing, and why

**Deliverable 2 is DELIVERED for the five closed campaigns, 2026-08-19.** See
§9. The paragraph below records why it was blocked and what unblocked it, because
the block was real and the reasoning that lifted it matters more than the fact.

**The blocked route, and why it stayed blocked.** The deduplicated reader writes
`per_species.csv`, `per_category.csv` and `per_observable.csv`, and none of them
carries the multiplicity class axis. Earlier sessions took the per-class observable to come
from `tools/statistical_robustness.py`. That tool needs a PASS boundary receipt
and a PASS final-origin closure report **for the same sealed manifest**. No variation
campaign has either, and neither does the sealed central. That route is still
shut, and `COMPONENTS.md` still marks the tool SUPERSEDED. Run record §15.6, §16.

**The route that works needs no certificate.** The plotter emits the per-class
balancing yield itself, on the `UNCERTAINTY_MATRIX` line, with the class encoded
in the bin name (run record §17.4 as corrected by §18.1). One render of the
eleven-class configuration emits every class at once. It reads the merged
products and their ten subsample directories, and asks for no closure report.
The instrument was in the tree the whole time; §17.4 named it and §18 settled
its class axis.

**And neither has the sealed central campaign.** Investigated 2026-08-19 under
an owner ruling to open the boundary requirement. This session did not apply
the ruling, because relaxation would not have opened the chain.

The final-origin closure report is a second, independent requirement, and **no
such report exists for `HF_RUN3_V1` or for any variation**.
`tools/statistical_robustness.py` has therefore never run on any campaign here.
`COMPONENTS.md` now marks it and `final_origin_closure.py` **SUPERSEDED**.

The gate they rest on is unreachable by construction. Production demotes every
duplicate hard-carrier claimant to `Origin::kUnresolved`.

A2 measured 124 / 24,411 / 24,590 such contested rows in MONASH / JUNCTIONS /
CLOSEPACKING, over 100 of the sealed campaign's 1000 slots. The project measures
unresolved origin as a systematic, not as a gate. Run record §17.
The certificate costs an `AuditOriginResolution.C` pass over every canonical
raw file, 4500 audits for the five closed campaigns alone. Run record §16.

> ✅ **CLOSED 2026-08-20.** Both campaigns finished. `HF_SYS_MUF_UP` closed at
> 22:00:56 on 2026-08-19 and `HF_SYS_PDF_CTEQ6L1` at 03:08:39 on 2026-08-20,
> each 3/3 markers with every leg `errors=0`. Both are extracted, and §12 holds
> the combination they unblocked. The paragraph below is the state at the time it
> was written.

**Two campaigns are still merging.** At 16:48:11 CEST on 2026-08-19,
`HF_SYS_MUF_UP` (S1b up) holds **33 of 33 products** and is running the first of
its three closure passes. `HF_SYS_PDF_CTEQ6L1` (S2) holds 22 of 33 and is still
merging. **Both hold 0 of 3 closure markers. Neither has closed.** Both merge
processes are alive on their own launch hosts at 24 h 47 m elapsed. PID
3953522 runs on `stbc-i3` and PID 642060 on `stbc-i2`.

**Closure costs 2 h 04 m to 2 h 22 m per tune**, measured (run record §14.2), so
`MUF_UP` needs about six more hours from 16:24 and `PDF_CTEQ6L1` longer still. Each is about a day into a
CLOSEPACKING leg that the five closed campaigns
finished in 7 to 40 minutes. The cause is open. Both burn CPU in user space, the storage
benchmarks clean, and a filled-bin census puts them within 1.28x of the closed
campaigns. Run record §15.7 and §15.8.

---

## 9. S1a, S1b-down and S3 — the per-class and integrated balancing yields ✅ (deliverable 2)

**2026-08-19.** Per-class and multiplicity-integrated OS−SS balancing yield,
against the sealed `HF_RUN3_V1` nominal, for the five closed campaigns.

**Full tables, all 720 cells:**
[`docs/systematics_results_20260819/PER_CLASS_DELTAS.md`](systematics_results_20260819/PER_CLASS_DELTAS.md).
Run record: [`SYSTEMATICS_HARVEST_RUN_RECORD.md`](SYSTEMATICS_HARVEST_RUN_RECORD.md) §20.

**The estimator is the 2026-08-19 brief's, and it is absolute.** Δ = variation −
nominal, SEM(Δ) = √(SEM_var² + SEM_central²), flagged below 2 SEM. The log gives
one mean and one SEM per row and no block yields, so the per-block relative
estimator of pre-registration 2.2 cannot be formed from it. §7 above uses that
registered estimator on the category partition; this section cannot, and says so
rather than implying the two are the same arithmetic.

**The control licenses the arithmetic.** The measurement target re-rendering the
sealed central reproduces the nominal on **all 144 rows**, no disagreement in
any compared field, at the precision the logs record and with no tolerance.

### The integrated arm, charm D⁺–D⁻, absolute Δ ± SEM(Δ)

| campaign | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| `HF_SYS_MUR_UP` | −0.000160 ± 0.000271 | −0.000123 ± 0.000396 | −0.000583 ± 0.000355 |
| `HF_SYS_MUR_DOWN` | −0.000245 ± 0.000414 | −0.000424 ± 0.000327 | **−0.001034 ± 0.000239** |
| `HF_SYS_MUF_DOWN` | **−0.002308 ± 0.000322** | **+0.002498 ± 0.000428** | **+0.002607 ± 0.000229** |
| `HF_SYS_PTHAT_1` | **−0.007380 ± 0.000365** | **−0.006413 ± 0.000274** | **−0.004855 ± 0.000344** |
| `HF_SYS_PTHAT_4` | **+0.009600 ± 0.000358** | **+0.010396 ± 0.000498** | **+0.009153 ± 0.000423** |

Bold clears 2 SEM. The same table for the other three series is in the results
document.

### Resolved cells per campaign, per-class arm

| campaign | source | resolved / 132 |
|---|---|---|
| `HF_SYS_MUR_DOWN` | S1a down | 7 |
| `HF_SYS_MUR_UP` | S1a up | 13 |
| `HF_SYS_PTHAT_1` | S3 → 1.0 | 34 |
| `HF_SYS_MUF_DOWN` | S1b down | 42 |
| `HF_SYS_PTHAT_4` | S3 → 4.0 | 59 |

**The ordering agrees with §7 on the category axis.** The two scale arms are the
quietest and the two `pTHatMin` arms the loudest, on both axes, from two
different instruments and two different estimators.

**182 of 720 cells clear 2 SEM.** The per-class arm is statistics-limited: each
variation carries a tenth of the nominal's exposure and each class a fraction of
that campaign again.

**Every cell carries a relative shift.** The smallest nominal yield among the 720
is 0.0180359 and none is zero, so no cell is named in place of a number. Two
cells exceed 25 per cent relative, both in the B⁺–Λ_b series, and there the large
fraction is the small denominator.

**No verdict on the 2.4 ladder appears here.** The ladder compares per-class
values against the integrated shift, and both arms now exist on one axis for the
first time. A verdict on it needs its own pass and its own pre-registered rule.

**No total, and no quadrature.** The combination needs all seven campaigns.

---

## 10. THE TUNE SEPARATION — the half of the headline comparison that needs no variation

**2026-08-19.** Full tables:
[`docs/systematics_results_20260819/TUNE_SEPARATION.md`](systematics_results_20260819/TUNE_SEPARATION.md).
Machine-readable `tune_separation.json`, sha256 `37aae5bd…`.

**No systematic appears in that document, and no row in it is a verdict.** The
separation between two tunes is a property of the sealed nominal alone, so it is
available while the combination is not.

**`c1` is the LOWEST multiplicity class and `c11` the highest.** The window label
is a top percentile, so a high percentile is a low `N_ch`. This inverts every
per-class trend if read the other way, and §10 of the results document carries
the render log's own mapping.

| observable | c1, stat. σ | c11, stat. σ | c1, % of MONASH to erase | c11, % of MONASH to erase |
|---|---|---|---|---|
| B⁺–B⁻ balancing yield | 2.2 | 39.7 | 4.5 | 31.9 |
| B⁺–Λ_b balancing yield | 2.2 | 49.4 | 9.7 | 128.4 |
| Λ_b/B⁻ ratio | 2.5 | 59.2 | 14.8 | 235.5 |

**The separation grows monotonically from low to high multiplicity in all three
observables.** MONASH's Λ_b/B⁻ ratio declines gently, from 0.1865 at `c1` to
0.1619 at `c11`: a contrast of −0.02453 ± 0.00739, 3.3 σ from zero. JUNCTIONS
rises over the same axis, from 0.2141 at `c1` to 0.5432 at `c11`. That is the shape
a junction-driven baryon enhancement would produce, and this document does not
claim more than the shape until the systematic is in the denominator.

**The verdict is deferred, deliberately.** It needs the combined systematic per
class, which needs all seven campaigns.

---

## 11. THE TREND — the paper's central claim, measured on the nominal

**2026-08-19.** Full tables:
[`docs/systematics_results_20260819/RATIO_TREND.md`](systematics_results_20260819/RATIO_TREND.md).
Machine-readable `ratio_trend.json`, sha256 `b1b59548…`.

**The claim is a trend, and per-class gaps do not establish one.** §10 says the
tunes differ in a given class. This section says the Λ_b/B⁻ ratio **rises with
multiplicity** under colour reconnection and does not under MONASH.

**The model-free number, R(c11) − R(c1):**

| tune | contrast | stat. σ | difference vs MONASH | stat. σ |
|---|---|---|---|---|
| MONASH | −0.02453 ± 0.00739 | 3.3 | — | — |
| JUNCTIONS | +0.32909 ± 0.01053 | 31.2 | +0.35362 ± 0.01287 | 27.5 |
| CLOSEPACKING | +0.28719 ± 0.01364 | 21.1 | +0.31172 ± 0.01551 | 20.1 |

**MONASH declines gently rather than sitting flat**, at 3.3 σ. The word "flat"
overstates what was measured.

**A straight line in class index summarises but does not fit the reconnection
tunes**: χ²/ndf is 8.18 and 6.49 against MONASH's 1.41. The slopes are
+0.034804 ± 0.000709 and +0.032760 ± 0.000741 against −0.001210 ± 0.000369, so
the slope difference is 45.1 σ and 41.0 σ. **Quote the endpoint contrast as the
measurement and the slope as shorthand.**

**Statistical uncertainty only.** The verdict needs the combined systematic,
which needs all seven campaigns. To erase the JUNCTIONS trend the systematic
would have to reach 0.354 in the endpoint contrast, the whole of the effect.

---

## 12. THE COMBINATION AND THE VERDICT ✅ — all seven sources

**2026-08-20.** Full tables:
[`COMBINED_SYSTEMATICS.md`](systematics_results_20260820/COMBINED_SYSTEMATICS.md)
and [`VERDICT.md`](systematics_results_20260820/VERDICT.md). Machine-readable
`per_class_combination.json` sha256 `8a8a26b8…`, `verdict.json` `7f6e9c65…`.

**The rules are the pre-registration's and the dated amendment's**, and the
driver adds none of its own: A1's `max(|Δ|, SEM(Δ))` applied continuously, A2
keeping S6 on its own `M1…M5` partition and out of the sum, §9.1's
μ_F-against-PDF choice, §2.5's larger arm, and S5's measured zero. The
tune-bundle spread is not a systematic and is not in it.

### The trend — the central claim

| quantity | value | stat | syst | total | σ | holds? |
|---|---|---|---|---|---|---|
| trend JUNCTIONS − MONASH | **+0.35362** | 0.01287 | 0.15999 | 0.16051 | **2.2** | **yes** |
| trend CLOSEPACKING − MONASH | **+0.31172** | 0.01551 | 0.15434 | 0.15512 | **2.0** | **yes** |

**The claim holds, at about 2 σ.** The erase threshold was 0.354, the whole of
the effect; the combined systematic reaches 0.160, 45 per cent of it.

**Statistically the trend difference is 27.5 σ. With systematics it is 2.2 σ.**
Quoting the statistical figure alone would overstate the result by an order of
magnitude.

**The result does not depend on the combination rule.** The trend difference is
positive in every one of the seven variation renders, from +0.233 (`MUF_DOWN`,
the largest excursion) to +0.445 (`MUR_UP`), against a nominal of +0.354.

### The per-class verdict

**49 of 72 cells exceed their total uncertainty. The boundary falls at `c5`** in
five of six series and at `c3` in the sixth. Below it, `c1`–`c4` at N_ch 0 to
about 6, the separation is **not established**; above it, and in the integrated
bin, it is.

Two effects push the same way there: the separation is smallest at low
multiplicity, and the combined systematic is largest — 23 to 46 per cent in
`c1`–`c4` against 6 to 13 per cent integrated.

### S1b's shape, which the UP arm settled

**Two-sided and opposite-signed in all eleven comparable cells, and
systematically asymmetric**, the DOWN arm larger by 1.245 to 1.829 in every
resolved category. §2.5 quotes the larger arm, so S1b is governed by DOWN
throughout and the budget is unchanged from what `MUF_DOWN` alone implied. The
UP arm established the shape rather than enlarging the total. See
[`PER_CATEGORY_FINAL_TWO.md`](systematics_results_20260820/PER_CATEGORY_FINAL_TWO.md).
