# Systematics — the pre-registration, six sources

> **Rebuild amendment (2026-08-22).** Generation-variation choices remain
> recorded, but every class-axis prescription and class-dependent result below
> is superseded by tune-local percentile classes. Re-harvest each campaign with
> a v2 per-tune boundary receipt before combining any systematic uncertainty.

**Written 2026-08-17, before any variation job was rendered or queued.** Wall
clock at the first line: 10:38 CEST. The first `condor_submit` of this program
must not precede this document being committed; if the git history shows
otherwise, this document is void and every number derived from it must be
withdrawn.

**What this is.** The paper quotes per-class, per-tune numbers and currently
propagates **no** systematic uncertainty (private branch-state record, *NOT PLANNED*: "PDF and
scale variation are **not addressed**, and no systematic uncertainty is
propagated anywhere in the analysis"). This document registers six sources, the
variation that probes each, its magnitude, its sample size, the estimator, the
decision thresholds, and — for each — **the expectation stated in advance so
that it can be wrong**. It follows the shape of
`docs/A2_PAIR_UNRESOLVED_PREREGISTRATION.md`, which is the template the project
has already scored once.

**The living result document is `docs/SYSTEMATICS.md`.** This one is frozen at
commit time and annotated, never rewritten — the A2 precedent: "Registered text
unedited; the annotation carries it."

---

## ✅ OWNER AMENDMENT — 2026-08-18, ruled BEFORE any variation Δ existed

**Two questions this document left open were put to the owner and answered. Both
answers are recorded here, dated, and neither is retrofitted to a result.**

> ### The precondition, checked at commit time rather than asserted
>
> **No Δ from any variation source existed anywhere in the repository when this
> amendment was committed.** Verified, not claimed: the four variation cells in
> `docs/SYSTEMATICS.md` (S1a, S1b, S2, S3) all read `PENDING`; the only file under
> `docs/systematics_results_*` is `s5_class_migration.json`, which is **S5's
> structural zero measured 2026-08-17** — a different source, exactly zero by
> construction, published before this ruling and unaffected by it; and
> `config/systematics_variations_v1.json` is the variation *declaration*, not
> results. The analysis stage had completed 2100/2100 jobs but **no extraction, no
> merge product, and therefore no per-class number of any kind** had been produced.
>
> This matters because both rulings change what the eventual numbers mean, and a
> rule chosen with the answers visible is not a rule.

### A1 — how an UNRESOLVED per-class Δ enters the combination

**This document was silent** (§2.4's ladder is an all-or-nothing verdict over a
whole source; §9 then sums every class with no provision for one whose Δ is
noise). **Ruled:**

> **Each variation source contributes `max( |Δ(c)| , SEM(Δ(c)) )` per class,
> applied continuously — no threshold cliff.**

- **Both `|Δ|` and `SEM(Δ)` are tabulated for every class**, always.
- The **`|Δ| < 2·SEM` flag is presentational only.** It marks a class for the
  reader; it does not gate, clip, or zero anything, and it must never be used as a
  branch in the arithmetic.

**The rationale, on record:** *a systematic cannot be claimed below the resolution
of the measurement, and a potentially real shift cannot be zeroed.* The rule takes
whichever of those two floors binds. Continuity is the point — a threshold rule
would make the quoted systematic jump discontinuously as a Δ drifts across
2 σ, which is an artefact of the sample size and not of the physics.

**Superseded by this:** nothing in the registered text, which was silent. The
three options this gap generated — *as-is*, *zero*, *SEM* — are recorded in
`docs/SYSTEMATICS_HARVEST_RUN_RECORD.md` §7.1 with the worked example that
motivated the ruling. **`max(|Δ|, SEM)` is none of those three**: it is *as-is*
where the measurement resolves and *SEM* where it does not, with no discontinuity
between.

### A2 — the A2/S6 partition conflict

**§9.6 STANDS, unchanged.** A session brief instructed that the A2 term be summed
in quadrature into the per-class total; **that instruction is overruled, and the
owner has recorded it as their own error.**

> **A2/S6 remains a separate systematic on its own five-class partition
> (`M1…M5`). Nothing is summed across incompatible partitions, and no mapping
> between them is invented.**

The reason is the one §9.6 already gave: `M1…M5` (`N_ch` 1–9, 10–19, 20–29,
30–39, ≥ 40) and `c1…c11` (half-integer boundaries −0.5 … 32.5) are different
partitions of the same axis, so there is no class-by-class correspondence to add
along.

**How a total is presented in the manuscript is an owner decision at writing
time**, not a computation this pipeline performs.

### What this changes in the tooling

Both rulings are encoded as **explicit required policy flags** on
`extraction/systematics_delta.py::combine_quadrature`, which refuses to run
without them, so neither can be silently re-decided by a caller.

---

## 1. THE SIX SOURCES

| # | source | probes | needs generation? | this session |
|---|---|---|---|---|
| **S1** | **Renormalisation & factorisation scale** | the hard-process scale choice | **yes**, 4 campaigns | **pre-registered + LAUNCHED** |
| **S2** | **Parton distribution** | the initial-state parton flux | **yes**, 1 campaign | **pre-registered + LAUNCHED** |
| **S3** | **`PhaseSpace:pTHatMin`** | whether the conclusion survives the sample definition | **yes**, 2 campaigns | **pre-registered + LAUNCHED** |
| **S4** | **Event-activity counter window** | `\|η\| < 1` vs the stored `\|η\| < 4` cross-check counter | no — re-analysis of existing raw | **pre-registered, DELIBERATELY NOT LAUNCHED** (§6) |
| **S5** | **Decay-daughter class migration** | the 1.33 % decay-policy bias on `N_ch` | no — re-projection only | **pre-registered + MEASURED** (§7) |
| **S6** | **Pair-level unresolved origin** | duplicate hard-carrier tie-break | already run | **DONE** — `docs/a2_results_20260813/` |

**Two things are deliberately absent, and their absence is a claim.**

- **The tune bundle is the measurement, not a systematic.** MONASH / JUNCTIONS /
  CLOSEPACKING is the comparison the paper is *about*. The spread between them
  is the result. It is not folded into an uncertainty band, and doing so would
  destroy the very quantity being reported. The known confound inside it — that
  JUNCTIONS re-tunes the fragmentation parameters that set baryon production, so
  a MONASH-vs-JUNCTIONS baryon difference cannot be attributed to junctions
alone — is documented in the private branch-state record and is **not** a systematic either. It is
  a limit on interpretation, and `JUNCTIONS_MATCHED` exists to address it.
- **Detector response is out of scope.** This is a generator-level study. There
  is no unfolding, no efficiency, no resolution model, and no acceptance beyond
  the stated `|η| ≤ 4` / `pT` cuts. Nothing in this program estimates what a
  detector would do to these numbers, and no combination of these six sources
  may be presented as a total uncertainty on a measurable quantity.

---

## 2. THE TWO DELIVERABLES — both, from every variation

Each variation must yield **both**, or it is not scored:

1. **The decomposition fractions** — the diquark-structure partition
   (`kCentralGround`, `kExcludedVector`, `kExcludedExcited`, `kMultiplyHeavy`),
   per tune, as in `docs/THREE_TUNE_CENTRAL_TABLE.md`. A partition: it sums to
   100 %, so a systematic on it is a systematic on *how weight moves between
   categories*, not on a normalisation.
2. **The per-class OS−SS balancing yield** — per multiplicity class, per tune,
   on the production class axis.

**Reporting both is not redundancy.** The fractions are normalisation-free by
construction and the OS−SS yield is not, so a source that moves one and not the
other localises itself. A source that moves both by the same relative amount is
acting on the overall trigger rate; a source that moves only the fractions is
acting on hadronisation; a source that moves only OS−SS is acting on the pairing
or on the class assignment.

### 2.1 The class axis — the production eleven, not A2's five

`config/multiplicity_class_boundaries_v1.json`, the single definition of the
axis: eleven classes `c1…c11` on **common absolute** `N_ch` boundaries at
half-integers −0.5, 2.5, 3.5, 5.5, 6.5, 8.5, 10.5, 13.5, 17.5, 23.5, 32.5, on
`NCH_PRIMARY_CHARGED_ETA10_V1`.

> **S6 (A2) is on a DIFFERENT axis** — its own five classes `M1…M5` at `N_ch`
> 1–9, 10–19, 20–29, 30–39, ≥ 40. **That mismatch is registered here rather
> than discovered later.** A2's numbers may not be added in quadrature to
> per-`c` values without re-binning, and §9's combination rule says what to do
> about it.

### 2.2 The estimator — identical for every source

For a per-class quantity `Y` and a variation `v`:

```
Δ_v(c) = [ Y_v(c) − Y_nom(c) ] / Y_nom(c)
```

formed **inside each block** and then averaged over the ten blocks, with the
**SEM over those ten values**. Forming the ratio inside the block before
averaging is the project's standing estimator rule for nonlinear quantities
(A2 §6). Reported in **per cent**.

**Blocks: `slot % 10`, ten blocks, dof 9.** The same construction as everywhere
else in the project. For the generation-dependent sources the variation and the
nominal are *independent generations*, so block `k` of the variation is not the
same events as block `k` of the nominal; the pairing is by block **index**, and
the resulting SEM is therefore the SEM of a difference of two independent
means, dominated by the thinner arm (the variation, at 1/10 the nominal
statistics). This is stated because it is the one place the estimator differs
in meaning from A2, where both arms were the same events.

### 2.3 `LOW-STAT` — reused verbatim from A2 §6

**Any class whose nominal yield is below 10³ weighted pairs in a block is
reported but flagged `LOW-STAT` and excluded from the per-class-vs-integrated
comparison.** A class too sparse to measure cannot falsify flatness. For the
decomposition fractions the same rule applies with 10³ entries in a block.

**On the production axis, `c11` (`N_ch ≥ 32.5`) and `c10` are the tail classes**
— ⟨N_ch⟩ is ~12.9 in MONASH minimum bias — and are the ones expected to trip
this flag at 10 M events per tune. That is registered as expected, not as a
surprise.

### 2.4 The thresholds — reused verbatim from A2 §8

Let `Δ_int` be the multiplicity-integrated relative shift and `Δ(c)` the
per-class values, each with block SEM `σ(c)`.

| verdict | condition |
|---|---|
| **NEGLIGIBLE** — need not be quoted | \|Δ(c)\| < **0.1 %** in every non-`LOW-STAT` class **and** every Δ(c) within **2 σ(c)** of zero |
| **QUOTABLE AS ONE NUMBER** | not negligible, **and** every non-`LOW-STAT` Δ(c) within **2 σ(c)** of Δ_int |
| **MUST BE QUOTED PER MULTIPLICITY CLASS** | any non-`LOW-STAT` Δ(c) differs from Δ_int by **> 2 σ(c)**, **or** max Δ(c) − min Δ(c) exceeds **50 % of Δ_int** |

> **See the 2026-08-18 OWNER AMENDMENT A1 above.** This ladder remains the
> per-SOURCE reporting verdict. It does **not** govern how an individual
> unresolved class enters the combination; that is `max(|Δ|, SEM)`, applied
> continuously, and the 2 σ flag here is presentational only.

**This threshold ladder is reused unchanged and that is a deliberate choice, not
laziness.** It was fixed before A2 measured anything, it produced a verdict that
was acted on, and re-deriving a threshold now — after seeing that A2's effect
was 0.02–0.23 % — would be choosing a threshold with knowledge of the answers.
The 0.1 % negligibility floor will make several of these sources non-negligible
by a wide margin. **That is the correct behaviour of an honest threshold**, and
the consequence must be quoted rather than the threshold moved.

### 2.5 Two-sided variations — which arm is quoted

S1, S3 and S5 are two-sided. **The quoted systematic is the arm with the larger
`|Δ(c)|`, per class**, with the other arm reported beside it as the cross-check.
This is the A2 owner ruling applied to a new case ("the systematic to quote is
the LARGEST-index arm, per class … the smallest-index arm is the cross-check,
not a lower bound").

**Not half the spread, and not the envelope.** Half-spread understates whenever
the response is one-sided, which it will be for any observable that is not
locally linear in the varied parameter. Calling the pair an *envelope* would
claim the two arms bracket the space of scale choices, and they do not: a
7-point or 9-point variation reaches further, and the two-point diagonal is a
convention, not a bound. The word "envelope" is not to be used for any of these.

---

## 3. S1 — RENORMALISATION AND FACTORISATION SCALE

### The variation

`SigmaProcess:renormMultFac` and `SigmaProcess:factorMultFac`, each **×2 and
×0.5**, as **four separate campaigns** — the two scales varied **independently**,
not coherently.

Both settings are PYTHIA parameters with default `1.`, `min 0.1`, `max 10.`
(verified against the installed 8.317 `xmldoc/CouplingsAndScales.xml`, lines 196
and 306), so both requested values are inside the sanctioned range. The nominal
cards set neither, so the nominal is the default `1.` in both.

### Why ×2 / ×0.5, and why independently

The factor-of-two two-point variation is the standard convention for a
leading-order calculation, and this is LO 2→2 `HardQCD:hardccbar` +
`hardbbbar`. There is no argument here for a different magnitude, and inventing
one would be worse than following the convention.

**Independently, not coherently, and this is the load-bearing choice.** A
coherent variation would be two campaigns instead of four and would give a
larger single number — the diagonal of the 9-point grid — so it is the cheaper
and more conservative option. It is rejected because **`μ_F` and the PDF (S2)
act through the same object**: the initial-state parton flux. If `μ_F` were
folded into a combined scale number, S1 and S2 would be entangled, and §9's
quadrature combination would rest on an independence assumption that could not
even be inspected. Varying `μ_F` on its own makes that correlation
**measurable**: if `μ_F`'s effect is negligible while the PDF's is not, the
independence assumption is safe; if both are comparable, §9's rule for
correlated sources applies and the reader can see why.

The card structure makes this exactly as cheap per campaign as `μ_R` alone —
one more generated card per tune, same tool, same submit path — which is the
condition the design brief set for taking the extra pair.

### Sample size

**100 jobs × 100 000 events per tune per campaign** = 10 M events per tune,
300 files per campaign. The A2 precedent at exactly this scale ("**100 files per
tune**, not 1000 — this is a systematic, not a central value") produced per-class
block SEMs of 0.001–0.014 % on a 0.02–0.23 % effect, i.e. the effect was
resolved at 5–20 σ. This is one tenth of the central campaign's 100 M events per
tune, so per-class SEMs scale up by ~√10 ≈ 3.2 from the central table's values.

### Expectation — stated so it can be wrong

1. **Sign and bracketing.** `μ ↓` raises `α_s(μ²)` and therefore the hard cross
   section and the average string activity; `μ ↑` lowers both. **The two arms
   are expected to bracket the nominal with opposite signs in every class.**
   **A same-sign response in both arms** would mean the observable is not
   monotonic in the scale over this range — a legitimate outcome, and one that
   would mean the two-point variation *understates* the band and must be said
   to.
2. **The fractions are expected to be nearly inert: ≲ 0.5 % relative.** The
   diquark-structure partition is set by the `StringFlav` parameters and the
   colour topology, and the hard scale does not enter hadronisation. Its only
   route to the fractions is through the string-length and multiplicity mix.
   **A fractions shift above 2 % would falsify the claim that the decomposition
   is a hadronisation observable** and would be the most important result of
   this program.
3. **Per-class OS−SS is expected to move more than the fractions but still
   modestly: ≲ 5 % relative.** The scale shifts the trigger `pT` spectrum and
   the event activity, but the observable is **conditioned on `N_ch`**, and the
   classes are common absolute boundaries, so most of the activity change should
   be absorbed by the conditioning rather than appearing in the observable.
   **This is the falsifiable claim: conditioning on `N_ch` absorbs the scale
   change.** It is testable against a quantity the run already produces — if the
   per-class OS−SS shift is comparable to the shift in the *inclusive* trigger
   rate rather than much smaller than it, the conditioning is not absorbing the
   change, and the multiplicity classes are not doing what the analysis assumes
   they do.
4. **`μ_R` is expected to dominate `μ_F`.** `μ_R` enters as `α_s²` for a 2→2 QCD
   process; `μ_F` enters through the gluon PDF's slope in `x` at
   `x ~ 2 p_T/√s ≈ 3 × 10⁻⁴`, where the LO gluon is already steep and a
   factor-two scale change moves it by ~10 %. If **`μ_F` exceeds `μ_R`**, the
   observable is driven by the initial state rather than by the coupling, and S2
   must then be treated as correlated with S1 rather than independent.

### Campaigns

| campaign | ordinal | card variant | setting |
|---|---|---|---|
| `HF_SYS_MUR_UP` | 4 | `mur_up` | `SigmaProcess:renormMultFac = 2.0` |
| `HF_SYS_MUR_DOWN` | 5 | `mur_down` | `SigmaProcess:renormMultFac = 0.5` |
| `HF_SYS_MUF_UP` | 6 | `muf_up` | `SigmaProcess:factorMultFac = 2.0` |
| `HF_SYS_MUF_DOWN` | 7 | `muf_down` | `SigmaProcess:factorMultFac = 0.5` |

---

## 4. S2 — PARTON DISTRIBUTION

### The variation

`PDF:pSet`, **13 → 8**. One alternate set, PYTHIA-internal, no LHAPDF
dependency.

**Named from the installed generator, not from memory.** Read out of
`pythia_stock_8317/install/share/Pythia8/xmldoc/PDFSelection.xml`:

| | `PDF:pSet` | set | `α_s(M_Z)` |
|---|---|---|---|
| **nominal** | **13** (the PYTHIA default, and what `Tune:pp = 14` resolves to) | NNPDF2.3 QCD+QED LO | **0.130** |
| **alternate** | **8** | CTEQ6L1, LO | **0.1298** |

The nominal cards do not set `PDF:pSet`; it arrives via `Tune:pp = 14` (Monash),
which is why the nominal value is stated as the resolved default and will be
confirmed against the producer's own exhaustive post-init
`effective_settings` snapshot rather than asserted from the card.

### Why CTEQ6L1 specifically

**Because its `α_s(M_Z)` is 0.1298 against the nominal 0.130 — a 0.15 %
difference — so the variation isolates the PDF *shape* and does not smuggle in an
`α_s` variation.** That is the whole reason for this choice over the obvious
alternatives inside the same file: `pSet = 14` is the same NNPDF2.3 LO fit at
`α_s = 0.119`, which is an 8 % coupling change wearing a PDF costume and would be
double-counting S1's `μ_R` arm; `pSet = 17` (NNPDF3.1 LO) is a newer fit from the
same collaboration and lineage, so it probes fit vintage rather than fit
methodology.

CTEQ6L1 is a **different collaboration, a different fit methodology, and a
genuinely used tune baseline** (it underpins several ATLAS and CMS tunes), so
"what if the PDF had been the other conventional choice" is a question a
reviewer can recognise. It is LO with an LO coupling, matching the LO nature of
the Monash tune, so there is no perturbative-order mismatch.

### Sample size

**100 jobs × 100 000 events per tune** = 10 M events per tune. Same as S1, same
justification.

### Expectation — stated so it can be wrong

1. **Smallest of the three generation-dependent sources.** ≲ 1 % relative on
   per-class OS−SS, ≲ 0.2 % on the fractions. The two sets differ mainly in the
   low-`x` gluon, which changes the *rate* of `gg → QQ̄` and slightly the
   `gg` : `qq̄` mix; the hadronisation that follows is untouched.
2. **The direction is not predicted, and that is stated rather than hidden.**
   CTEQ6L1's gluon is harder than NNPDF2.3 LO's at some `x` and softer at
   others; without evaluating both at this exact `(x, Q²)` there is no honest
   sign prediction. **No sign is registered for S2**, and any sign found is
   therefore not evidence of anything.
3. **If S2 exceeds S1's `μ_R` arm, that is the headline.** It would mean the
   observable is sensitive to the initial state at a level the hadronisation
   interpretation does not admit, and the paper's framing — that these are
   hadronisation observables — would need qualifying.

### Campaign

| campaign | ordinal | card variant | setting |
|---|---|---|---|
| `HF_SYS_PDF_CTEQ6L1` | 8 | `pdf_cteq6l1` | `PDF:pSet = 8` |

---

## 5. S3 — `PhaseSpace:pTHatMin`

### The nominal, read rather than assumed

**`PhaseSpace:pTHatMin = 2.` — read from
`generation/cards/pythiasettings_Hard_Low_ccbb_MONASH.cmnd:47`**, with 12 lines
of card comment recording why, and ratified as a decision in
`results/validation/generator/PTHAT_MULTIPLICITY_SCAN_8317.md`
§*Decision, 2026-08-03*:
"`PhaseSpace:pTHatMin` is set to 2.0 GeV in all tune cards."

### The variation points — taken FROM the scan, not invented

The scan measured four points on 8.317. All of them, with the nominal marked:

| `pTHatMin` | `dN_ch/dη`, MB convention | vs minimum bias | status |
|---|---|---|---|
| 0.5 | 4.613 | −33.8 % | measured, not used here |
| **1.0** | 4.973 | **−28.6 %** | **variation, down arm** |
| **2.0** | 6.678 | **−4.2 %** | **NOMINAL** |
| **4.0** | 10.492 | **+50.6 %** | **variation, up arm** |

**1.0 and 4.0 are the scan's own adjacent measured points**, and they are the
×0.5 / ×2 pair about the nominal, which matches S1's convention. 0.5 is
excluded: it is two steps away, its MB deficit (−33.8 %) is barely distinguishable
from 1.0's (−28.6 %), and it therefore buys almost no new information for a
whole campaign.

### Why this is a systematic at all — and the scan says so

The scan's own §*Limits* names this measurement as the thing it did **not** do:
"This measures *what the sample is*. It does not answer whether the physics
conclusion is robust to the threshold, which is a separate comparison of the
balancing observables at different `pTHatMin` values." **S3 is that comparison.**
It is registered here as closing a limitation the project wrote down for itself
seventeen days before this document.

**The asymmetry is registered in advance.** 1.0 and 4.0 are symmetric in
`pTHatMin` but wildly asymmetric in what they do to the sample: 2.0 → 1.0 moves
the MB comparison by −24.4 points, 2.0 → 4.0 by +54.8 points. **So the two arms
are not expected to be symmetric in the observable either**, and §2.5's
larger-arm rule will very likely select the 4.0 arm. Saying so now prevents the
asymmetry from being reported later as a discovery.

### Sample size

**100 jobs × 100 000 events per tune per arm** = 10 M events per tune. Note the
per-file cost is not identical to the other sources: at a higher threshold the
trigger yield per event rises (the scan measured charm triggers per event
0.990 → 1.196 from 1.0 → 2.0, +20.8 %; beauty +68.1 %), so the 4.0 arm will have
*more* triggers per event than nominal and the 1.0 arm fewer. **The 1.0 arm is
therefore the one at risk of `LOW-STAT` in the tail classes**, and that is
expected, not a failure.

### Expectation — stated so it can be wrong

1. **This is expected to be the largest of the six sources**, and the only one
   large enough that it might not belong in a systematic band at all. ≳ 10 %
   relative on per-class OS−SS at the 4.0 arm.
2. **The falsifiable claim, and it is the important one: per-class OS−SS is
   invariant under the threshold once conditioned on `N_ch`, to within 10 %.**
   The classes are common absolute `N_ch` boundaries shared by all three tunes
   precisely so that conditioning removes the sample's overall activity. If that
   works, S3 is a modest systematic. **If it does not — if the per-class numbers
   move by much more than 10 % — then `pTHatMin` is part of the *definition* of
   the paper's per-class observable and must be quoted as such, not folded into
   an uncertainty.** Those are materially different papers, and this is the
   measurement that decides which one is being written.
3. **The fractions are expected to move less than OS−SS but more than under S1**,
   because the threshold changes the hard-parton `pT` and therefore the string
   configurations that hadronise, not merely the coupling.
4. **A near-null result would be the strongest possible outcome** — it would
   retire the entire `pTHatMin` concern, which has been open since
   `NCH_CALIBRATION_20260730.md` §*OPEN ISSUE*. It is named here as a legitimate
   outcome so it cannot later be presented as a foregone conclusion.

### Campaigns

| campaign | ordinal | card variant | setting |
|---|---|---|---|
| `HF_SYS_PTHAT_1` | 9 | `pthat_1p0` | `PhaseSpace:pTHatMin = 1.0` |
| `HF_SYS_PTHAT_4` | 10 | `pthat_4p0` | `PhaseSpace:pTHatMin = 4.0` |

**Not routed through the `--pthat-min` override.** `campaign.py`'s
`PTHAT_OVERRIDES` admits only `{0.5, 1.0, 2.0}` — so 4.0 is outside it — and
`runCondorJob.sh:121` restricts any override to `role = pilot`, while the
renderer emits `role = primary` unconditionally. Both arms therefore go through
the same generated-card mechanism as S1 and S2, so all seven campaigns share one
code path instead of two. Recorded because a reader will reasonably ask why the
purpose-built override was not used.

---

## 6. S4 — EVENT-ACTIVITY COUNTER WINDOW

### The variation

Re-analyse with the event-activity classifier taken from the **`|η| < 4`**
counter instead of the nominal **`|η| < 1`** (`NCH_PRIMARY_CHARGED_ETA10_V1`).
`docs/DESIGN_AND_RATIONALE.md` §3.5: "A second counter at `|η| < 4` is stored as
a cross-check." It is already in every raw file, so **no generation is
required** — this is a re-analysis of the existing 3000 files.

### The boundary convention for the wide counter — fixed now

The wide counter's mean is roughly 4× the narrow one, so the eleven boundaries
cannot be reused as absolute numbers. **Pre-registered choice:
percentile-preserving boundaries** — recompute each boundary as the wide-counter
value at the same MONASH-minimum-bias percentile the narrow boundary sits at,
from the committed MB samples in `evidence/b4_multiplicity_mb`,
keeping the half-integer convention so no integer `N_ch` is ambiguous.

**Why percentile-preserving and not the same absolute numbers.** The class
*labels* are percentiles of the MONASH MB distribution
(`config/multiplicity_class_boundaries_v1.json`); reusing absolute boundaries
would compare class `c7` of one axis with a completely different percentile of
the other, and the resulting shift would be dominated by the relabelling rather
than by the physics. The percentile-preserving choice isolates the question
actually being asked: **does widening the rapidity window over which activity is
measured change the physics conclusion, at fixed percentile?**

### Sample size

The full existing campaign — 3000 files, 100 M events per tune. No new
generation, so there is no reason to subset.

### Expectation — stated so it can be wrong

1. **A wider window measures the same underlying activity with less relative
   fluctuation** (more particles per event, so smaller Poisson smearing relative
   to the mean), so at fixed percentile the classes should be *better* resolved,
   and **the per-class observable should shift only slightly: ≲ 3 %.**
2. **The shift is expected to grow toward the tail classes**, because the narrow
   counter's tail is the one most contaminated by fluctuation — an event in
   narrow-`c11` may be an ordinary event that fluctuated upward in `|η| < 1`.
   **A flat shift across classes would mean the two counters are
   interchangeable**, which would be a clean and reportable simplification.
3. **A large shift would indict the narrow counter**, not the wide one, and
   would mean the paper's multiplicity axis is fluctuation-dominated.

### ⛔ REGISTERED NOW, DELIBERATELY NOT LAUNCHED

**S4's jobs must not be queued in this session.** They are analysis jobs, and an
analysis job pins the repository commit it was rendered against
(`runCondorJob.sh` and the analysis worker both refuse to run if the checkout has
moved). The Nikhef checkout is frozen at `43e35be8`, read live by the running
merge, and private branch-state pending item 5 records the checkout advance as **still
blocked**. Queuing S4 now would pin the old head and re-block the advance the
moment it is finally possible.

**Launch condition, stated so nobody has to re-derive it:** after the merge exits,
the campaign is recorded COMPLETE, and the checkout advance in private branch-state pending
#5 has happened. Then render S4 against the new head.

---

## 7. S5 — DECAY-DAUGHTER CLASS MIGRATION

### The variation

Shift the eleven class boundaries by **±1.33 %** and re-project the per-class
observable from the existing merged product. **Re-projection only** — no
generation, no re-analysis, no new event loop.

### The magnitude, and where it comes from

**1.33 %**, measured, not chosen: `results/validation/generator/NCH_CALIBRATION_20260730.md`
records `dN_ch/dη` = **7.007** under the experimental decay convention
(`tau0Max = 10 mm`, heavy decays on) against **6.914** under the exact
production policy (`tau0Max = 0.01 mm`, heavy decays off) — a deficit of
(7.007 − 6.914)/7.007 = **1.327 %**. `docs/DESIGN_AND_RATIONALE.md` §3.5 states
it as the one consequence of the decay policy that must appear in the paper:
"The production decay policy costs 1.3 %, because the experimental primary
definition counts charm/beauty decay daughters … and we disable those decays."

The production counter therefore **undercounts** `N_ch` by 1.33 % relative to an
experimental primary definition. Correcting for it means shifting `N_ch` up by
1.33 %, equivalently shifting the class boundaries **down** by 1.33 %. **Both
signs are run**, because the bias is a mean shift with an unmeasured spread and
the sign of its effect on a class edge is not the sign of the bias.

### Expectation — a prediction of exact structural zero

> **Every class is expected to be structurally insensitive, in both arms.**

`N_ch` is an integer and the boundaries are at half-integers, so a boundary move
changes class membership **only if it crosses an integer** — i.e. only if the
shift exceeds 0.5. The largest boundary is 32.5, and 1.33 % of 32.5 is **0.432 <
0.5**. Every smaller boundary moves less. **So no integer `N_ch` changes class
under either sign, and Δ(c) = 0 exactly for all eleven classes.**

**This is a prediction, not an excuse prepared in advance.** It is arithmetic on
two committed numbers, it is stated before the re-projection is run, and it is
falsifiable in the cleanest possible way: **if any class moves at all, the
arithmetic above is wrong**, and the re-projection has found an error in this
document rather than a systematic in the analysis.

The design brief anticipated this outcome and ruled on how to report it:
a class whose shifted boundary lands on the same integer edge is recorded as
**structurally insensitive** — a result, not a failure.

### What the null does and does not mean

- **It does mean** the 1.33 % counter bias cannot migrate a single event between
  classes, so it contributes **exactly zero** to the per-class systematic, and
  the source can be closed rather than bounded.
- **It does not mean** the bias is harmless in general. It still shifts the
  *percentile labels* the classes carry — the MONASH-MB percentile of a fixed
  `N_ch` boundary changes when the distribution shifts — and it still means the
  paper's classes correspond to slightly different experimental percentiles than
  their labels claim. **That is a labelling caveat, and it must be stated in the
  paper text**; it is not a per-class uncertainty, and this source must not be
  reported as covering it.
- **It does not survive a granularity change.** The null holds *because* of the
  half-integer convention and the specific boundary values. Registered
  consequence: **if the class axis is ever re-binned with a boundary above 38.5**
  (where 1.33 % first exceeds 0.5), this source stops being zero and must be
  re-measured. Written down so a future re-binning does not silently inherit a
  null that no longer applies.

---

## 8. S6 — PAIR-LEVEL UNRESOLVED ORIGIN (already run)

Complete, pre-registered separately in
`docs/A2_PAIR_UNRESOLVED_PREREGISTRATION.md`, measured and scored in
`docs/a2_results_20260813/A2_DELTA_RESULT.md` and `A2_TIEBREAK_ROBUSTNESS.md`.
Verdict: **MUST BE QUOTED PER MULTIPLICITY CLASS** for the CR tunes, negligible
for MONASH; quote the **largest-`heavyIndex`** arm. Values in
`docs/SYSTEMATICS.md`. Its differing class axis is flagged in §2.1 and handled in
§9.

---

## 9. THE COMBINATION RULE — and its independence assumptions

**Quadrature, per class, per tune**, over the sources that are not NEGLIGIBLE by
§2.4, using the larger arm per §2.5:

```
σ_sys(c, tune) = sqrt( Σ_s Δ_s(c, tune)² )
```

**The independence assumptions, stated because quadrature is only valid if they
hold:**

1. **S1 `μ_F` and S2 (PDF) are NOT independent.** Both act on the initial-state
   parton flux. **Registered rule: if both are non-negligible, quote the larger
   of the two and drop the other from the sum**, rather than adding them. If one
   is negligible, the other enters alone and the question does not arise. The
   measurement in §3 is what decides which case applies, and it must be reported
   either way.
2. **S1 `μ_R` and S1 `μ_F` are treated as independent** and both enter the sum.
   They act through different objects — the coupling and the parton density —
   and the whole reason for running them separately (§3) is to be able to say
   this rather than assume it.
3. **S3 (`pTHatMin`) is treated as independent of S1**, and this is the weakest
   of the assumptions. A threshold cut and a scale choice both change the
   hard-parton `pT` mix. **It is flagged rather than resolved**, and if S3 turns
   out to be large (§5's expectation 2), the correct response is not to add it in
   quadrature but to reconsider whether it is an uncertainty at all.
4. **S4 (counter) is independent of everything else** — it is a re-analysis of
   identical events with a different classifier, so it shares no generation-level
   input with any other source.
5. **S5 contributes exactly zero** (§7), so it drops out of the sum
   arithmetically. It is still listed in the table, because a zero that was
   measured is a different object from a source that was never examined.
6. **S6 is on a different class axis** (§2.1). **Registered rule: S6 is not
   added in quadrature to per-`c` values.** Until it is re-binned onto `c1…c11`
   it is quoted as a separate line in the systematics table, with its own
   `M1…M5` axis named in the row. Re-binning it is a known piece of future work,
   not a thing to be fudged by assuming its classes map onto these.

**No total is to be quoted for a tune until every non-negligible source in that
tune's column has a measured value.** A partial quadrature sum understates, and
an understated systematic is worse than an absent one.

---

## 10. POSITIVE CHECKS — required before any number is reported

`rc = 0` is not evidence. Each is a check that can fail:

1. **The nominal-reproduction check, per deployment.** The variation deployment
   rebuilds the producer (the allowlist change in §11 forces it). Built from that
   deployment, a job run with the **nominal** card must reproduce a committed
   nominal raw output's physics content. **A deployment that cannot reproduce the
   nominal is not a variation of it.** This is A2's regression gate, which
   "stops everything" on failure, applied to the generation side.
2. **The variation must do something.** Each variation's effective card sha must
   differ from the nominal's, the difference must be exactly the registered
   setting, and the producer's own exhaustive post-init `effective_settings`
   snapshot must show the varied value — not the card, the resolved value. A
   variation that resolves to the nominal value silently is the failure mode this
   check exists for, and it is the one that would look like a null result.
3. **`PhaseSpace:pTHatMin` must match authorisation.** `ValidateRawOutput.C:603`
   already fails closed on this; for S3 it is the check that the varied threshold
   actually took effect end to end.
4. **Seeds: no reuse, ever.** Every campaign's seeds drawn by `tools/campaign.py`
   at a fresh campaign ordinal, asserted against the authoritative ledger
   (`/data/alice/ipardoza/Hadronization/config/burned_seeds.txt`, 3557 burned at
   ordinals 0 and 3) and burned at render time. Ordinals 4–10 are claimed by this
   document.
5. **The frozen tree is never written.** All seven campaigns run from a separate
   deployment; the merge's checkout at `43e35be8` is read for nothing and written
   for nothing except the append-only, git-ignored seed ledger.
6. **First-output verification before bulk release.** The submit files are
   rendered with `hold = True`, so one job per campaign is released and its
   promoted output inspected before the remaining 299 are released.

---

## 11. WHAT THIS PROGRAM REQUIRES OF THE CODE — registered, because it is not zero

> ### ✏ ANNOTATION 2026-08-17, after implementation — §11.2's route was improved on
>
> **The registered text below is unedited.** It says the varied keys would be
> added to `config/tune_difference_allowlist_v1.json`, and registers the
> consequence that this would move `kTuneDifferenceAllowlistSha256` and leave
> the 3000 central raw files **not cross-validatable** by the rebuilt validator.
>
> **Implementation found that consequence avoidable, and avoided it.** That
> file's digest turned out to be pinned three ways, not one: by the **frozen**
> Gate-B spec `config/statistical_robustness_v1.json`, by a suite test that
> asserts the spec pins the checked-out file (`test_statistical_robustness.py`
> — it failed, which is how the third pin was found), and in the metadata of
> every one of the 3000 raw files. So the three keys live in a **new** artifact,
> `config/systematic_variation_settings_v1.json`, which feeds only the audited-key
> union that the producer checks against.
>
> **What that buys:** the tune-allowlist digest is **unchanged** at
> `2b35e52a…`, the frozen spec still pins the file it was frozen against, and
> the variation campaigns' raw files carry the **same** allowlist digest as the
> central campaign — so they **are** cross-validatable, which the registered
> plan said they would not be. The rebuild is still forced (the generated header
> changed, so `kAuditedPythiaSettingKeys` went 46 → 49), so §10.1's
> nominal-reproduction check is still required and is not weakened.
>
> **What it costs:** a second configuration file feeding one union. It is pinned
> in the generated header as `kSystematicVariationSettingsSha256`, so the binary
> identifies it, and the keys are deliberately **not** added to
> `allowed_tune_differences` — the cross-tune audit therefore still requires one
> varied value shared by all three tunes, which is what a variation is. A card
> varying the scale for JUNCTIONS alone is still rejected.


Three things had to change before any of this could run, and each is a change to
a guarded path. They are listed here so that the pre-registration and the
implementation cannot drift apart.

1. **The production worker could not run at all from the restructured tree.**
   `generation/submit/runCondorJob.sh` derives `project_base` from
   `dirname $0`, which was correct when the script sat at the repository root
   and has been wrong since the 2026-08-12 restructure moved it two levels down
   (private rename record, Section 1.1). It resolves to `<base>/generation/submit` and every job
   exits 3 at "required component missing". **Latent, never hit, because the
   Nikhef checkout is still at the pre-restructure commit `43e35be8`** — no
   production job has ever been launched from the restructured layout.
2. **The producer rejects any card key outside the tune allowlist.**
   `heavyflavourcorrelations_status.cpp:311` throws "configured setting is
   absent from tune allowlist" for a configured key not in
   `kAuditedPythiaSettingKeys`. `SigmaProcess:renormMultFac`,
   `SigmaProcess:factorMultFac` and `PDF:pSet` are not among the 46, so S1 and
   S2 require them added to `config/tune_difference_allowlist_v1.json`, the
   registry artifacts regenerated, and the pinned allowlist checksum in
   `config/statistical_robustness_v1.json` updated — **which changes
   `kTuneDifferenceAllowlistSha256` and therefore forces a rebuild of both the
   producer and the raw validator.** Registered consequence: raw files from this
   deployment carry a different `tune_difference_allowlist_sha256` than the 3000
   central files, so the two sets are **not** cross-validatable by each other's
   validator. That is a bookkeeping fact, not a physics difference, and check
   §10.1 is what establishes it is not a physics difference.
3. **The variation cards need a selection mechanism.** The worker derives the
   card name from the tune alone, so a variation card is unreachable. A
   `--card-variant` argument is threaded through the renderer, the submit row,
   the ClassAd and the worker, defaulting to the nominal path so the central
   campaign's rendering is unchanged.

**Cards are generated by tool** (`tools/make_systematic_cards.py`), never
hand-edited, and each variation's effective card sha256 is recorded in
`docs/SYSTEMATICS.md`.

---

## 12. THE COST — stated before it is spent

| | |
|---|---|
| campaigns | **7** (S1 × 4, S2 × 1, S3 × 2) |
| jobs | **2100** (7 × 3 tunes × 100) |
| events | **210 M** (10 M per tune per campaign) |
| **raw disk** | **≈ 193 GB**, at the measured 92.2 MB per 100 k-event file |
| `/data/alice` headroom measured 2026-08-17 10:44 CEST | **1009 GB free, 97 % used** |

**19 % of remaining headroom on a filesystem already at 97 %.** It fits, and it
is not comfortable. Registered consequences: private branch-state pending item 7
(disk consolidation, private cluster-disk inventory Section 7) becomes load-bearing rather
than optional if all seven campaigns land; and if the owner wants the program
cheaper, **the honest lever is dropping the `μ_F` pair (§3) back to a coherent
scale variation** — 55 GB and 600 jobs saved, at the cost of the S1/S2
independence check in §9.1. Reducing events per job is *not* an equivalent
lever: it degrades every per-class SEM at exactly the tail classes where the
measurement is thinnest.

---

## 13. WHAT WOULD MAKE THIS PROGRAM WRONG

Registered failure modes, so that they are recognised rather than explained:

1. **A variation that resolves to the nominal.** Caught by §10.2. Would appear as
   a null result and would be believed.
2. **A rebuild that changes the nominal.** Caught by §10.1. Would contaminate
   every Δ with a producer difference and would look like a systematic.
3. **Comparing block `k` to block `k`** as though they were the same events.
   §2.2 states they are not. Treating them as paired would understate every SEM.
4. **Quoting a total before every column is filled.** §9's closing rule.
5. **Calling the two-point pair an envelope.** §2.5. It is a convention, and the
   space of scale choices is not bounded by it.
6. **Presenting a quadrature sum as a total uncertainty on a measurable
   quantity.** §1. There is no detector response anywhere in this program.
