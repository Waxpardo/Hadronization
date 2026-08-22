# Production shape — combined vs split charm/beauty

> **Historical decision, superseded 2026-08-22.** The common MONASH-derived
> absolute axis discussed below is no longer the project definition. The active
> contract is `config/multiplicity_percentile_classes_v2.json`, with thresholds
> resolved independently for every tune. This file is retained only to explain
> archived outputs that used the former decision.

Every number below carries its method. **Nothing here is a paper number** — no
category fraction lacking block SEM appears, and the statistics projection
(§4) is **deferred, not estimated**.

---

## 1. What was measured

**Source:** HF_PT2_INT raw, `/data/alice/ipardoza/hadronization_production/HF_PT2_INT/raw/<TUNE>/`.
**Method:** `TChain` over the first **10 jobs per tune** = **1,000,000 events
per tune**, read-only, ROOT over ssh. Expectations were pre-registered before
each run and are reported whether or not they held.

### 1.1 Event mixture — pre-registered ~10:1, **measured 6.39:1**

From `process_counts`, weighted `Draw` over process codes:

| tune | charm (121+122) | beauty (123+124) | cc̄ : bb̄ | beauty fraction |
|---|---|---|---|---|
| MONASH | 864,887 | 135,113 | 6.401 : 1 | **13.51 %** |
| JUNCTIONS | 864,539 | 135,461 | 6.382 : 1 | **13.55 %** |
| CLOSEPACKING | 864,632 | 135,368 | 6.387 : 1 | **13.54 %** |

**Tune-independent, as it must be.** **The pre-registered ~10:1 was wrong;
beauty is ~35 % more abundant than assumed.** This matters below: it changes
the headline advantage of a split.

**Where the wrong ratio came from, recorded so it cannot resurface with its old
authority:** the ~10:1 descends from the **superseded C6 table**, whose
*accepted-quark* counts were read as an *event* ratio. That is a
measurement-scope error of the catalogued class — comparing two numbers before
establishing they measure the same thing — this time on the design side rather
than in the pipeline. **6.39:1 is the event ratio; any quark-level ratio is a
different quantity and must be labelled as one.**

### 1.2 The channels are exactly disjoint — verified, not assumed

Cross-check of the `hard_channel` encoding against `process_code`, per tune:

```
hard_channel==4 & code in {121,122} = 864,887     hard_channel==4 & code in {123,124} = 0
hard_channel==5 & code in {123,124} = 135,113     hard_channel==5 & code in {121,122} = 0
```

**Zero cross-contamination in either direction, in all three tunes.** Charm-hard
and beauty-hard events are mutually exclusive populations sharing a file.

### 1.3 N_ch by hard channel — beauty sits at ~2.05x charm

`multiplicity_primary_charged_eta10_v1`, split by `hard_channel`:

| tune | charm mean | beauty mean | ratio |
|---|---|---|---|
| MONASH | 9.675 | 20.172 | **2.085** |
| JUNCTIONS | 10.685 | 21.725 | **2.033** |
| CLOSEPACKING | 10.053 | 20.289 | **2.018** |

**Pre-registered expectation (beauty higher) confirmed; the magnitude is a
factor of two, not a shift.**

---

## 2. M6 made quantitative — the pooled axis is a beauty-enrichment axis

**11 equal-population percentile classes derived from each tune's own pooled
`multiplicity_primary_charged_eta10_v1`**, then beauty occupancy read per class.

| class | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| c01 (lowest) | **3.45 %** | **3.02 %** | **3.31 %** |
| c02 | 3.64 % | 3.67 % | 3.66 % |
| c03 | 3.85 % | 4.30 % | 4.06 % |
| c04 | 4.62 % | 5.00 % | 4.88 % |
| c05 | 5.74 % | 6.02 % | 6.08 % |
| c06 | 7.01 % | 7.26 % | 7.82 % |
| c07 | 9.31 % | 9.56 % | 10.06 % |
| c08 | 12.64 % | 13.48 % | 13.56 % |
| c09 | 18.27 % | 19.37 % | 19.14 % |
| c10 | 28.76 % | 29.21 % | 29.06 % |
| c11 (highest) | **45.31 %** | **44.89 %** | **43.97 %** |
| **swing** | **13.1x** | **14.9x** | **13.3x** |

**This is the mechanism, stated plainly.** The activity axis is built from a
sample that is 86.5 % charm-hard with mean N_ch ~10, while beauty-hard events
sit at mean ~20. **A pooled percentile class is therefore not a common axis for
the two sectors** — it is a variable-composition mixture, running from ~3 %
beauty at the bottom to ~45 % at the top, and the composition itself is what
changes across the axis.

**Method caveat, stated because it affects any boundary scheme.** `N_ch` is
discrete, so equal-population percentile classes are unattainable — quantile
boundaries collapse onto integers and realised class sizes range from ~53,000
to ~153,000 rather than the nominal ~91,000. **Any 11-class percentile scheme
on this observable inherits that, including the paper's.**

---

## 3. B_c accounting

`NBC > 0` split by `hard_channel`:

| tune | charm-hard | beauty-hard | total / 10⁶ events | beauty-hard share |
|---|---|---|---|---|
| MONASH | 7 | 260 | 267 | **97.38 %** |
| JUNCTIONS | 15 | 632 | 647 | **97.68 %** |
| CLOSEPACKING | 32 | 702 | 734 | **95.64 %** |

**Pre-registered expectation confirmed:** B_c lives dominantly in bb̄-hard
events — shower `g -> cc̄` inside a beauty event outweighs shower `g -> bb̄`
inside a charm event, by roughly 30:1 to 40:1.

**Consequences:**

- **A bb̄-only arm carries ~96–98 % of B_c statistics.** Splitting costs almost
  nothing in B_c.
- **Per-event-class B_c physics is identical under either shape** — B_c is
  produced in beauty-hard events either way; only how many such events exist
  changes.
- **The per-sector closure sum rules are unaffected.** B_c is beauty-sector by
  registry, carries both `q_c` and `q_b`, and legitimately enters both sector
  closures; that is a property of the state, not of the production shape.
- **B_c is rare either way** — 2.7 to 7.3 x 10⁻⁴ per event. Note the ~2.7x
  spread across tunes, which is a hadronisation effect and not a shape question.

---

## 4. Beauty per-class, per-block projection — MEASURED 2026-08-09

**This is the decision number. It was deferred once; it is now measured.**

### Method

Per tune, per promoted block directory (10 blocks), per pair file: project that
block's `hCorrelations` onto its **N_ch axis (axis 6)** and integrate within the
realised class boundaries recorded in §4.1. Entries summed over each species
group's pair files, then **x10 for 1000 jobs** (the campaign is 100 jobs/tune =
10 inputs x 10 blocks; full production is 1000). **Exact per-class per-block pair
entries — no occupancy proxy.** Read-only; artifact retained at
`/data/alice/ipardoza/proj6iii_run01/proj.out` (150 lines = 3 tunes x 5 groups x
10 blocks).

**Two defects in this run, both stated:**

1. **Ten classes, not eleven.** The boundary list held 11 values, giving 10
   intervals, so the last bin is `[18,inf)` — the memo's **c10 and c11 merged**.
   Classes c1–c9 are exact. **The merged class is the least starved, so the
   starvation verdict is unaffected**, but the top-class numbers below are the
   sum of two classes.
2. **`min x 10` degenerates on an observed zero.** The rule is about *expected*
   entries per block, so **means are the decision statistic**; minima are
   reported only as a spread indicator.

### 4.1 The realised class boundaries (from the `bd811d0` measurement)

**These were measured but not written into this memo; recorded now so the
projection is reproducible.** `multiplicity_primary_charged_eta10_v1`, lower
edges:

| tune | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MONASH | 0 | 2 | 3 | 4 | 6 | 7 | 9 | 11 | 14 | 18 | 26 |
| JUNCTIONS | 0 | 2 | 4 | 5 | 7 | 8 | 10 | 13 | 16 | 20 | 28 |
| CLOSEPACKING | 0 | 2 | 3 | 5 | 6 | 8 | 10 | 12 | 15 | 19 | 26 |

### 4.2 Result — mean entries per block at 1000 jobs

| tune | group | c1 | c2 | c3 | c5 | c7 | c9 | c10+11 | classes < 10 |
|---|---|---|---|---|---|---|---|---|---|
| MONASH | B-meson ctrl | 1801 | 2348 | 3095 | 3870 | 8547 | 17721 | 81394 | **none** |
| MONASH | Λ_b | 156 | 217 | 258 | 328 | 755 | 1460 | 6672 | **none** |
| MONASH | **Σ_b^±** | **20** | 31 | 32 | 37 | 93 | 229 | 1289 | **none** |
| MONASH | Σ_b⁰ *(not quoted)* | 7 | 15 | 15 | 23 | 51 | 90 | 621 | c1 |
| MONASH | **B_c** | **0** | 1 | 1 | 2 | 6 | 22 | 100 | **c1–c7** |
| JUNCTIONS | Λ_b | 167 | 426 | 303 | 392 | 1504 | 2287 | 11235 | none |
| JUNCTIONS | **Σ_b^±** | 161 | 582 | 487 | 900 | 3792 | 6395 | 31982 | **none** |
| JUNCTIONS | B_c | 1 | 3 | 0 | 2 | 4 | 7 | 65 | c1–c7, c9 |
| CLOSEPACKING | Λ_b | 217 | 185 | 548 | 717 | 931 | 2144 | 9626 | none |
| CLOSEPACKING | **Σ_b^±** | 125 | 180 | 629 | 1104 | 1512 | 3652 | 16120 | **none** |
| CLOSEPACKING | B_c | 0 | 1 | 7 | 4 | 4 | 3 | 48 | c1–c9 |

**MONASH is the binding arm on every beauty species, by a factor of ~8 against
JUNCTIONS on Σ_b^±** — consistent with MONASH producing the fewest baryons.

### 4.3 Verdict against the pre-registered decision rule

**Rule as pre-registered:** all *quoted* classes ≥10 entries/block at 1000 jobs
under the 11-class scheme ⇒ **Option A viable as-is**; rescued only by a coarser
4-class beauty scheme ⇒ **A viable with coarsening**; neither ⇒ **B/C
shortlisted**.

**Quoted beauty observables are Λ_b, Σ_b^± and the B-meson control.** (Σ_b⁰ is
`centralEligible = false` — measured, never quoted. B_c was included so the
shape decision sees it, not as a headline observable.)

> **VERDICT: Option A is viable as-is for the quoted beauty observables.**
> Every quoted species clears ≥10 entries per block in every class, in all three
> tunes. **The binding value is MONASH Σ_b^± in c1 at 20** — it clears the bar
> by 2x, which is *thin but passing*.

**Three qualifications the verdict does not cover:**

1. **MONASH's low classes are marginal, not comfortable** — Σ_b^± runs 20 / 31 /
   32 / 37 across c1–c5. A modest downward revision in any assumption puts c1
   under the bar. **Per-class MONASH Σ_b^± error bars will be large and should
   be shown, not smoothed.**
2. **Σ_b⁰ fails c1 (7).** It is not quoted, so it does not gate — **but it is
   measured, and any completeness table including it inherits the gap.**
3. **B_c per-class is not viable under ANY scheme.** It fails c1–c7 at 11
   classes and still fails coarse classes 1–2 at the 4-class variant (MONASH
   0 / 8 / 15 / 137). **B_c is a top-class-only observable in combined
   production.** That is the one place the shape decision genuinely bites — see
   §3: a bb̄-only arm carries 95.6–97.7 % of B_c.

**4-class coarse variant** (0–10 / 10–40 / 40–70 / 70–100 %), for reference —
it rescues nothing that was failing among quoted species because nothing was:
MONASH Σ_b^± 20 / 131 / 220 / 1687; Σ_b⁰ 7 / 77 / 116 / 791; B_c 0 / 8 / 15 /
137.

### 4.3b RE-CHECK UNDER THE COMMON BOUNDARIES — 2026-08-09. Option A STANDS

**Required by the axis ruling: new boundaries move the class windows, so the
Option-A verdict had to be re-evaluated rather than assumed.** Same extraction
as `5ed3bc9`, new cuts, **11 proper classes this time** (the earlier run merged
c10/c11 through a boundary-list error; that is fixed here).

**Pre-registered:** Option A stands; every quoted species stays ≥10 mean
entries/block in every class. **Confirmed.**

**Binding values, mean entries per block at 1000 jobs:**

| tune | Λ_b | **Σ_b^±** | B-meson ctrl |
|---|---|---|---|
| MONASH | 258 | **32** | 3095 |
| JUNCTIONS | 241 | 344 | 2211 |
| CLOSEPACKING | 242 | 268 | 2139 |

**The binding value improved from 20 to 32** — MONASH Σ_b^± in class 1. Common
c1 is `[−0.5, 2.5)`, wider than MONASH's own former `[0, 2)`, so the sparsest
class gained population. **The axis change made the statistics case stronger,
not weaker.**

**Two other movements worth recording:**

- **Σ_b⁰ now passes everywhere** (MONASH min 22, was 7 and failing c1). It is
  still `centralEligible = false` and still not quoted — **but a completeness
  table that includes it no longer inherits a starved class.**
- **B_c is unchanged in kind**: fails c1–c8 for every tune. **Still a
  multiplicity-integrated / top-class-only observable**, exactly as G2 declared.
  The axis change does not rescue it and was never expected to.

**No flag to owner is required** — the pre-registered failure branch (a quoted
species falling below 10, reopening the coarsening decision) did not trigger.

### 4.4 Pre-registration scorecard

| pre-registered | outcome |
|---|---|
| low-multiplicity classes are the starved ones | **too pessimistic** — they are the *marginal* ones, but every quoted species clears 10 |
| MONASH Σ_b^± is the binding species | **confirmed** — 20 at c1, the tightest quoted value anywhere |
| B_c thin everywhere | **confirmed, strongly** — 0–7 entries below the top class in all tunes |

What is needed: per-block `hCorrelations` entries from the ten promoted block
directories for the headline beauty observables — B⁺/B⁰/Λ_b triggers with Λ_b
and **Σ_b^±** associates — with class occupancies from the `hTrKinematics` N_ch
projections, projected per-class per-block to 1000 jobs, **flagging every class
with a projected < 10 entries per block**.

**Σ_b⁰ (`5212`) is `centralEligible = false`** and must be measured but never
the quoted species; whatever the paper calls "Σ_b" reads **Σ_b^±**.

**What can be said without it, as a bound only.** At 1000 jobs (100x this
sample), beauty *events* per class run from ~188,000 (c01) to ~4,170,000 (c11)
for MONASH. **That is an upper bound on any beauty observable's statistics and
is not the quantity that matters** — the observables are per-trigger-species
pair entries within a class, which are sparser by orders of magnitude.
**The starved-class question cannot be answered from the numbers above.**

---

## 5. The three options

### Option A — combined as-is, coarsen starved classes at plotting time

- **Cost: free.** `N_ch` is stored as a full-resolution axis, so class
  boundaries are a plotting-stage choice, not a production one. Merging c01–c04
  for beauty observables needs no regeneration.
- **Keeps:** one campaign, one ledger, one manifest, one provenance chain.
- **Does not fix:** the composition gradient itself. A coarsened class is still
  a charm-dominated mixture; it just has more entries.
- **Honest framing:** this treats the symptom. It is legitimate if the observable
  is reported per sector and never as a charm-vs-beauty comparison at fixed
  class.

### Option B — combined, plus a bb̄-only top-up as its own chain

- **Mixed provenance is forbidden**, so the top-up **cannot share a merge** with
  the combined campaign. It is a separate chain end-to-end: own manifest, own
  merge, own promoted directories, own closure.
- **Cost:** a second campaign's bookkeeping and its own ordinal, plus every
  downstream consumer learning that two datasets exist.
- **Buys:** beauty statistics without discarding the combined sample's pooled
  axis.
- **Risk, stated:** two datasets with different mixtures invite exactly the
  confound §3.2 was corrected to stop claiming — they must never be pooled.

### Option C — full split: cc̄-only and bb̄-only at chosen event counts

- **Beauty statistics per CPU-hour improve by at most `1 / 0.1354 = 7.4x`**, not
  the ~10x that circulated — that figure descends from the superseded ~10:1
  mixture. **And 7.4x is an upper bound**: beauty-hard events carry ~2x the
  multiplicity (§1.3) and cost more CPU each, so the realised gain is lower.
  **The true per-CPU-hour factor is not yet measured.**
- **Cost:** a second campaign's bookkeeping, its own ordinal, and card/producer
  mode work. **The split-card ancestors already exist** in `SimulationScripts/`
  (`pythiasettings_Hard_Low_cc*.cmnd`, `..._bb*.cmnd`), so this is not
  greenfield.
- **Buys:** statistics allocated by need rather than by cross-section, and each
  sector gets its own activity axis for free.

---

## 5b. B4 MAPPING MEASUREMENT — MEASURED 2026-08-09. **CRITERION FAILS. ESCALATION.**

**Pre-registered criterion: all 11 boundary→MB-percentile mappings within ±3
percentage points across tunes ⇒ MB-anchored convention ratified. Any boundary
outside ⇒ owner escalation with the full table, no convention change, no
further action.**

> ## **5 of 11 boundaries fall outside ±3 pp. The MB-anchored convention is NOT
> ratified. No convention change has been made and no follow-up work started.**

### Difference check — run FIRST, and it passes

**The anti-null-measurement guard, evaluated before any agreement statement.**
Six runs, 200k events each, each reading its own production card (confirmed by
`B4_TUNE_CARD` per run), all exit 0, all overflow 0.

| tune | MB ⟨N_ch⟩ | hard ⟨N_ch⟩ |
|---|---|---|
| MONASH | 12.9482 ± 0.0290 | 11.2041 ± 0.0218 |
| JUNCTIONS | 13.5746 ± 0.0300 | 12.3250 ± 0.0232 |
| CLOSEPACKING | 12.9152 ± 0.0283 | 11.5931 ± 0.0218 |

| pair | MB | hard |
|---|---|---|
| MONASH ↔ JUNCTIONS | 15.0σ | 35.2σ |
| MONASH ↔ CLOSEPACKING | **0.8σ** | 12.6σ |
| JUNCTIONS ↔ CLOSEPACKING | 16.0σ | 23.0σ |

**The guard's purpose is satisfied: no two tunes produced identical output.**
Every pair separates decisively on at least one arm, and the cards are provably
distinct. **The `Tune:pp = 14` failure mode is excluded.**

**But stated plainly: MONASH ↔ CLOSEPACKING MB is only 0.8σ**, so the *literal*
MB-only form of the check is marginal for that pair. **That is physics, not
plumbing** — their `pT0Ref` values (2.28, 2.194) are close while JUNCTIONS
(2.15) is the outlier, and the MB means order accordingly. **The escalation
below is therefore a real result, not an artifact.**

### The mapping table — MB percentile of each class boundary, per tune

| class | MONASH | JUNCTIONS | CLOSEPACKING | spread (pp) | |
|---|---|---|---|---|---|
| c1 | 0.00 % (n=0) | 0.00 % (n=0) | 0.00 % (n=0) | 0.00 | ok |
| c2 | 5.29 % (n=2) | 5.28 % (n=2) | 5.48 % (n=2) | 0.20 | ok |
| **c3** | 11.80 % (n=3) | 18.04 % (n=4) | 11.86 % (n=3) | **6.24** | **OUTSIDE** |
| **c4** | 19.40 % (n=4) | 24.99 % (n=5) | 26.32 % (n=5) | **6.92** | **OUTSIDE** |
| **c5** | 34.06 % (n=6) | 37.24 % (n=7) | 33.06 % (n=6) | **4.18** | **OUTSIDE** |
| **c6** | 40.15 % (n=7) | 42.33 % (n=8) | 44.02 % (n=8) | **3.87** | **OUTSIDE** |
| c7 | 49.69 % (n=9) | 50.65 % (n=10) | 52.23 % (n=10) | 2.54 | ok |
| **c8** | 56.97 % (n=11) | 60.35 % (n=13) | 59.01 % (n=12) | **3.38** | **OUTSIDE** |
| c9 | 65.39 % (n=14) | 67.92 % (n=16) | 67.13 % (n=15) | 2.53 | ok |
| c10 | 73.85 % (n=18) | 75.78 % (n=20) | 75.52 % (n=19) | 1.93 | ok |
| c11 | 85.26 % (n=26) | 86.34 % (n=28) | 85.74 % (n=26) | 1.08 | ok |

*Method: percentile = fraction of that tune's MB sample strictly below the
boundary, where boundaries are the realised per-tune values in §4.1. Artifacts
retained at `/data/alice/ipardoza/b4_mapping/`; deployed macro `884f76e`,
sha256 `3be7a09…`.*

### What the failure looks like — a structural reading, not a conclusion

**The failures are concentrated in the low-to-middle classes (c3–c6, c8) and
the extremes agree well** (c1, c2, c10, c11 all under 2 pp). **The discreteness
of N_ch is the visible driver:** at low N_ch a boundary moves by one integer
between tunes (n=3 vs n=4 at c3, n=4 vs n=5 at c4) and one integer is worth
~6 pp of MB population there, while at c11 the same one-integer step is worth
~1 pp. **Two tunes cannot land on the same percentile when the axis only
admits integers and their distributions differ.**

**This is not offered as a resolution.** It says the ±3 pp criterion may be
unachievable *in principle* for the low classes on a discrete axis, which is a
different problem from "the tunes disagree" — and which of those it is is an
owner call, not one to make inside the escalation.

**Per the pre-registration: no convention change, no further action taken** by
the measuring session. **The owner ruled on the escalation; see §5c.**

## 5c. THE AXIS DECISION — owner ruling 2026-08-09. Common absolute boundaries

**The escalation is accepted as a RESULT, not an artifact.** The owner's reading:
the failures concentrate exactly where the MB density peaks, JUNCTIONS is the
outlier on both arms, and the ordering follows `pT0Ref` (2.15 lowest → most MPI
→ highest MB mean) with MONASH↔CLOSEPACKING nearly degenerate at 0.8σ, coherent
with 2.28 vs 2.194. **The tunes' MB distributions differ in the bulk, so any
per-tune percentile convention disagrees across tunes by 4–7 pp there. That is a
measurement, not a failed prerequisite.**

**The 0.8σ qualification is accepted as an owner judgement**, on the grounds
recorded in §5b: hard arms at 12.6σ, provably distinct cards, and a physically
coherent `pT0Ref` ordering. **Recorded here beside the qualification rather than
in place of it.**

### THE RULING

> **Adopt common absolute N_ch boundaries — one set, shared by all three tunes
> and both sectors. Labels are defined as percentiles of the MONASH MB
> distribution. The per-tune MB-percentile translations are PUBLISHED as a
> table.**

**The reason is physics, not convenience.** Per-tune percentile classes fold
each tune's *activity distribution* into the class *definition*, confounding
**"how the tune hadronises at fixed activity"** with **"how the tune distributes
activity"** — the two things this study exists to separate. Common absolute
boundaries condition every tune on an identical event selection, and the
residual is **quoted rather than hidden.**

**Rejected alternative: per-tune MB anchoring.** Rejected for the reason above,
not because it failed the ±3 pp gate. **Had it passed, it would still confound
the two effects** — the gate failing is what surfaced the question, not what
decided it.

**Consequences:** **M5 closes by construction** with the residual published;
**M6's cross-sector axis closes the same way** — one boundary set serves charm
and beauty alike, so the 13–15× occupancy swing is no longer hidden inside a
per-sector class definition but visible in the published translation.

### The common boundary set — derived from MONASH MB, 172,429 events

| class | target %ile | realised %ile | ± stat | **boundary** |
|---|---|---|---|---|
| c1 | 0.000 | 0.000 | — | **−0.5** |
| c2 | 9.091 | 11.803 | 0.078 | **2.5** |
| c3 | 18.182 | 19.403 | 0.095 | **3.5** |
| c4 | 27.273 | 34.063 | 0.114 | **5.5** |
| c5 | 36.364 | 40.150 | 0.118 | **6.5** |
| c6 | 45.455 | 49.692 | 0.120 | **8.5** |
| c7 | 54.545 | 56.970 | 0.119 | **10.5** |
| c8 | 63.636 | 65.386 | 0.115 | **13.5** |
| c9 | 72.727 | 73.846 | 0.106 | **17.5** |
| c10 | 81.818 | 82.876 | 0.091 | **23.5** |
| c11 | 90.909 | 91.578 | 0.067 | **32.5** |

**Half-integer boundaries** so no integer N_ch value is ambiguous about which
class it falls in. **Realised percentiles overshoot their targets** — by up to
6.8 pp at c4 — because N_ch is discrete and no integer sits at the target. **The
realised value is the one that means anything; the target is only how the
boundary was chosen.**

### THE PAPER-FACING TRANSLATION TABLE

**Where each common boundary sits in each tune's own MB distribution.** This is
the residual the ruling requires be published.

| class | boundary | MONASH | JUNCTIONS | CLOSEPACKING | spread (pp) |
|---|---|---|---|---|---|
| c1 | −0.5 | 0.00 % | 0.00 % | 0.00 % | 0.00 |
| c2 | 2.5 | 11.80 % | 11.22 % | 11.86 % | 0.64 |
| c3 | 3.5 | 19.40 % | 18.04 % | 19.09 % | 1.36 |
| c4 | 5.5 | 34.06 % | 31.49 % | 33.06 % | 2.57 |
| c5 | 6.5 | 40.15 % | 37.24 % | 38.93 % | **2.91** |
| c6 | 8.5 | 49.69 % | 46.79 % | 48.37 % | 2.90 |
| c7 | 10.5 | 56.97 % | 54.18 % | 55.79 % | 2.79 |
| c8 | 13.5 | 65.39 % | 63.08 % | 64.62 % | 2.31 |
| c9 | 17.5 | 73.85 % | 72.11 % | 73.67 % | 1.73 |
| c10 | 23.5 | 82.88 % | 81.73 % | 83.26 % | 1.53 |
| c11 | 32.5 | 91.58 % | 90.84 % | 92.10 % | 1.26 |

**Maximum residual: 2.91 pp.** Every class is inside 3 pp — **but this is a
different test from §5b's and must not be reported as "the criterion now
passes".** §5b asked whether *per-tune* boundaries coincide (they do not);
this asks how far a *common* boundary's meaning drifts between tunes. **The
first question is settled negatively and the second is the published residual.**

**An off-by-one was found and fixed in this table before it was recorded.**
`FindBin(2.5)` returns the bin *above* a half-integer edge, so the first
computation counted one N_ch value too many and read MONASH c2 as 19.40 %
against the boundary derivation's 11.803 % — the same quantity. **The corrected
table reproduces 11.803 % exactly**, which is the consistency check that caught
it.

**Named and NON-GATING follow-up:** tail-label precision for the 0–1 % class
would justify a boundary-grade MB reference run per tune, with a **settings
echo** added to the macro first (closing the HardQCD direct-read qualification
from v17). **That gates figures, not the farm.**

### THE REALISED CLASS FRACTIONS — what a reader actually gets

**Measured on the HF_RUN3_V1 merged product, 2026-08-13, 100 M events per tune.**
Emitted by the plotting stack itself as `tunes[…].realised_class_fractions` in
`multiplicity_boundary_receipt_v1.json`, so this is a run output and not a
transcription.

> **The two tables answer different questions and must not be confused.**
> The translation table above records **where the labels came from** — each
> common boundary's position in that tune's *minimum-bias* distribution. The
> table below records **what fraction of the analysed sample actually lands in
> each class.** The label is provenance; this is population.

| class | N_ch | MB label width | MONASH | resid (pp) | JUNCTIONS | resid (pp) |
|---|---|---|---|---|---|---|
| c1 | 0–2 | 11.803 % | 11.776 % | −0.03 | 10.479 % | −1.32 |
| c2 | 3 | 7.600 % | 7.801 % | +0.20 | 6.345 % | −1.26 |
| c3 | 4–5 | 14.660 % | 15.283 % | +0.62 | 13.299 % | −1.36 |
| c4 | 6 | 6.087 % | 6.493 % | +0.41 | 6.096 % | +0.01 |
| c5 | 7–8 | 9.542 % | 10.837 % | +1.29 | 10.700 % | +1.16 |
| c6 | 9–10 | 7.278 % | 8.732 % | +1.45 | 9.011 % | +1.73 |
| c7 | 11–13 | 8.416 % | 10.051 % | +1.64 | 10.822 % | +2.41 |
| c8 | 14–17 | 8.460 % | 9.223 % | +0.76 | 10.311 % | +1.85 |
| c9 | 18–23 | 9.030 % | 8.569 % | −0.46 | 9.683 % | +0.65 |
| c10 | 24–32 | 8.702 % | 6.764 % | −1.94 | 7.665 % | −1.04 |
| **c11** | **≥33** | **8.422 %** | **4.472 %** | **−3.95** | **5.588 %** | **−2.83** |

Both columns sum to exactly 1.0 over 100,000,000 events, with underflow and
overflow exactly zero.

**Why the high classes are thin, and it is not a defect.** The campaign sample
sits about **36 % below minimum bias in ⟨N_ch⟩** (`Model.tex:126`), so
MB-derived *absolute* boundaries necessarily under-populate the high-activity
classes: the boundary was placed where 8.42 % of MB events sit, and only 4.47 %
of MONASH campaign events reach it. The mass moves into the middle — c5 through
c8 all run fatter than their labels.

> **⚠ WHERE THIS BITES: the top classes are the thinnest, and OS−SS subtraction
> is least stable exactly where statistics are thinnest.** c11 carries roughly
> half the events its label implies. Any per-class number quoted from c10 or c11
> should be read with that in mind, and the block-to-block spread there is the
> quantity to check before such a number is published.

**JUNCTIONS is not MONASH shifted uniformly.** It is thinner at the bottom
(c1–c3, all ≈1.3 pp below label) and fatter through c6–c8, while remaining less
depleted than MONASH at the very top. That is a genuine difference in how the
tune distributes activity — precisely the effect common absolute boundaries
exist to keep *out* of the class definition, so that it surfaces here, in the
published population, rather than silently inside the axis.

CLOSEPACKING is absent because it is not merged.

## 6. The interaction with the axis decision — this is the real coupling

**The production shape and the activity-axis definition are not independent, and
choosing them separately is how this gets locked in wrongly.**

- **MB-anchored class boundaries (B4's machinery) decouple the axis from the
  production shape entirely.** If classes are defined against a minimum-bias
  reference rather than the hard sample's own percentiles, then a charm-only and
  a beauty-only run are classified on the *same* boundaries, and **a split
  becomes clean** — the sectors remain comparable at fixed class.
- **Pooled-hard-sample percentiles do not survive a split unchanged.** They are
  defined by the mixture, so splitting redefines every boundary and nothing is
  comparable across the two shapes or against the existing HF_PT2_INT data.

**So B4 is upstream of this decision.** Settling MB-anchored boundaries makes
Option C low-risk; leaving pooled percentiles in place makes Option C a
redefinition of the observable.

---

## 7. Summary table

| | **A: combined as-is** | **B: combined + bb̄ top-up** | **C: full split** |
|---|---|---|---|
| production cost | none | +1 campaign | 2 campaigns, replaces current |
| bookkeeping | unchanged | +1 ordinal, separate chain, no shared merge | +1 ordinal, card/producer mode work |
| beauty statistics gain | none | scales with top-up size | **≤7.39x per event (BOUND, = 1/0.1354)**; **~4x per CPU-hour (ESTIMATE**, assumes per-event CPU scales like N_ch, which is unmeasured — a small pilot would settle it, worth costing only if B/C are shortlisted) |
| fixes composition gradient? | **no** — treats the symptom | no — top-up has its own axis | **only if B4 lands** |
| B_c impact | none | ~96–98 % of B_c in the top-up | none — B_c follows beauty |
| survives a pooled-percentile axis? | yes | yes | **no** |
| survives MB-anchored axis? | yes | yes | **yes** |
| existing HF_PT2_INT data | fully reusable | fully reusable | boundaries redefined |

**Recommendation:** *(left blank for the owner)*

---

## 8. What is NOT established

1. **The per-CPU-hour split advantage** — §5C's 7.4x is an event-count upper
   bound; the CPU-weighted figure needs measuring.
2. **The beauty statistics projection** (§4) — deferred, and it is the number
   that decides whether Option A's coarsening is sufficient.
3. **Whether any class is actually starved for the headline observables** —
   unanswerable without §4.
4. **The 11-class scheme used here is equal-population percentiles derived by
   me**, not read from the paper's definition. **The occupancy *gradient* is
   robust to the scheme** — it follows from the 2.05x mean separation — but the
   per-class numbers would shift under different boundaries.
