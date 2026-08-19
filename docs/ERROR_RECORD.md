# Error record — what went wrong, who caught it, and what changed

**Consolidated 2026-08-11.** Until now this lived only in handoff
"what both sides got wrong" sections, which means it aged out of reach as the
chain grew. It is bidirectional on purpose: the working relationship is mutual
correction with evidence, and that only transfers if the record shows it running
in **both** directions.

**Entries are added, never edited.** Each names the error, how it was caught, and
the mechanism that now prevents it.

---

## E1 — 2026-08-11: the decay map did not conjugate antiparticle decays

**The defect.** PYTHIA stores one decay table per particle and derives the
antiparticle by conjugation, so `particleDataEntryPtr(-413)` returns the `+413`
entry. `tools/f4_probe.cc` recorded the products **verbatim**, and
`decay_parent_map_v1.json` carried them verbatim, mapping **D\*⁻ and D̄\*⁰ to D⁰
instead of D̄⁰**. Effect: **17.8 percentage points on D⁰**, the largest number in
the experiment-comparable table, published as 45.95 % when it is 28.13 %.

### Agent side

**The probe was written to read what PYTHIA reports, and it did — but reading a
generator's API verbatim is not the same as reading it correctly.** PYTHIA's
per-particle storage is documented behaviour, not a trap; the probe simply never
asked what a negative id would return. The map was then built, checked,
published, and consumed by two independent implementations for a full
generation.

### Owner side

**The published table's D⁰/D̄⁰ = 4.49 passed review without a charge-symmetry
check being requested.** Prompt charm at 13.6 TeV is produced essentially
charge-symmetrically, and a 4.5× asymmetry in a charge-separated table is
visible on inspection to anyone who asks the question. **It was not asked**, of
that table or of the D_s (2.74×) or B (5.39×) rows beside it.

### Why every existing check missed it

- **The reader's invariance check cannot see it.** It asserts total weight is
  conserved; conjugation errors move weight *between* bins and conserve the
  total exactly.
- **The self-check compares against `hFlavourClosure`'s six-bin projection**,
  which is the *structural* convention — the one that never consults the map.
- **The v1 re-derivation check reproduced the table exactly, and correctly.** It
  proved a reimplementation agreed with the reader. **Both were faithfully
  consuming the same wrong artifact.**

> **The lesson, and it generalises: a reimplementation check proves agreement,
> not correctness.** Two implementations of the same misreading agree perfectly.

**How it was actually caught.** By **C2 — "every split product must carry the
parent's heavy-quark sign"** — a check on the *physics* rather than on internal
consistency, **specified by the owner** for the v2 build. It fired on the first
split it examined and refused to write an artifact.

### Mechanisms added

| mechanism | where | behaviour |
|---|---|---|
| **Involution check** | `tools/build_decay_parent_map.py` | **fail-closed**, every future build: an antiparticle row must store exactly the conjugation of its particle row |
| **Heavy-quark sign check** | same | **fail-closed**, now on **every** row, not only split ones; distinguishes a legitimate flavour change (b→c) from a sign flip |
| **Particle/antiparticle ratio report** | `extraction/apply_decay_map.py` | **advisory**, on every species-level table; flags \|ratio−1\| > 10 % |
| **Base-map guard** | `tools/build_decay_parent_map_v2.py` | refuses to build on the defective v1 |

**The ratio report is deliberately NOT a gate.** A hard gate at 1.00 would be
wrong physics — real few-percent baryon asymmetries exist, and Λ_c sits at
1.026. A check that refused those would be refusing a result. 10 % catches the
4.49 × class and leaves physics alone.

---

## E2 — 2026-08-10: a hook-certification harness that deleted its own hook

The test script for the checkout-guard hook ran `rm -rf` on the directory the
candidate hook had just been copied into. **No hook was installed, and the test
printed "CORRECT" twice** — the "refused" direction passed because nothing was
there to permit it. The only evidence was a stray `cp` error in the output.

**Caught by reading the output rather than the exit status.** Fixed with a
fail-fast install check (`PREFLIGHT_FAIL` if the hook is absent or not
executable) before any direction runs, then re-run.

> **A test that cannot fail is not a test** — and this one was about to certify
> a safety mechanism guarding a 65 h run.

---

## E3 — 2026-08-11: a mechanism found, then not applied where it also held

Building map v2, the pre-registration correctly identified that **all of D\*⁰'s
channels land on the same ground state**, so its apparent misassignment
evaporates under species-level accounting. It then **assumed the remaining small
species would keep theirs.** They do not: Ξ*_c decays to π⁰ and γ **on the same
daughter — precisely D\*⁰'s structure** — and all four states collapse to a
single branch.

Three of five registered numbers missed as a result (V1 5.83 % vs 5.7737 %
actual, V5 0.054 % vs 0.0018 %). **All erred in the safe direction**, so nothing
downstream was harmed.

> **Having found a mechanism, check where else it applies before predicting.**

---

## E4 — 2026-08-11: an unprovenanced anchor produced a 7.4 σ result that was wrong

**The defect.** `AnalysisScripts/anchors/extraction_dual/per_species.csv` — the
weights behind every pre-merge table — is **bin-inconsistent with the merged
MONASH central across the baryon sector**.

> **CORRECTED 2026-08-11, same day, by better measurement.** This entry first
> said "one bin, Σ̄_b⁻, ~10 σ". That came from examining only the six Σ_b bins.
> Running `extraction/compare_subset_parent.py` over **all 95 ordinals** flags
> **30 of 88 testable bins at |z| > 4**, robust across three variance models
> (binomial 30, Poisson 27, independent-samples 26). **The inconsistency is
> broad, not local.** The original claim is left here because narrowing an
> investigation to the bins you already suspect is the error worth recording.

> **ANNOTATED 2026-08-13 — the null was recalibrated; the count above is NOT
> rewritten.** I2's binomial null was retired for pair counts and replaced by a
> robust empirical one (median-centred, MAD-scaled σ). Re-running the *same*
> comparison under it gives **0 of 88 bins at |z| > 4**, because the measured
> width of this comparison is **σ̂ = 4.399** binomial sigmas — cross-checked
> against plain stdev 4.426 and IQR/1.349 4.364, so the width is real and not a
> MAD artifact — and the largest bin reaches only **|z| = 2.83**.
>
> **Zero is not exoneration, and the standing ruling's arithmetic was wrong.**
> The ruling (`GOLDEN_OUTPUTS.md` §2.11a) predicted σ inflated ~2.2× with the two
> largest bins surviving near z ≈ 5. That 2.2× is the **block-vs-central**
> overdispersion (`38bf707`), measured on *clean* comparisons; it does not
> describe this one. A robust scale estimated **from the contaminated sample
> itself** absorbs the contamination: the anchor's defect is not one bin standing
> out, it is **30 of 88 bins displaced together**, so the bulk *is* the defect and
> nothing stands out from it. This is a known blind spot of the robust null —
> **it sees localized defects and is blind to broad ones** — and it is pinned as
> check 4 of `tests/test_compare_subset_parent.py` so it cannot be rediscovered
> as a surprise.
>
> **THE QUARANTINE STANDS.** It never rested on a flag count. It rests on
> deviations that are localized and physically large — the sixteen bins below, up
> to 33 %, almost entirely baryons — and those are unchanged. The binomial count
> of 30 remains the historical computation of record, still pinned by name as
> check 1 of the same test.

> # ⚠ ANNOTATED 2026-08-13, LATER THE SAME DAY — THE CONTROL WAS RUN, AND IT DOES NOT SUPPORT THE STATISTICAL CASE
>
> **Nothing above is rewritten. What follows is a measurement that was asked for
> to strengthen the quarantine and did the opposite.**
>
> **The missing control.** Every statement above compares the anchor to its
> parent and stops. It was never compared to a **genuine 1/10 subset of the same
> parent**, processed identically. The ten canonical MONASH blocks are exactly
> that, and they were available all along.
>
> **The comparison must be like-for-like on replication.** The anchor and its
> parent are both **replicated-era** products (E5). Replication multiplies every
> count by ~R, which inflates a binomial pull by √R and leaves fractional
> deviations untouched — measured here as a **5.03×** inflation of σ̂ against
> √24.2 = 4.92 predicted. So the anchor's peer group is the **replicated** block
> sweep, not the deduplicated one.
>
> | metric | ten genuine 1/10 subsets | **the anchor** | verdict |
> |---|---|---|---|
> | σ̂ (MAD width) | 4.800 ± 0.519 | **4.399** | 0.8 sd **below** the mean |
> | binomial flags at \|z\| > 4 | mean 35.3, range [32, 40] | **30** | **below the whole range** |
> | bins deviating > 2 % | mean 31.8, range [25, 37] | **29** | inside |
> | largest deviation | mean 27.50 %, up to **38.02 %** | **32.99 %** | inside |
> | median deviation | 0.76 – 1.34 % | **1.00 %** | typical |
>
> **On every metric this entry cites, the anchor is indistinguishable from — or
> quieter than — a real 1/10 subset of the same data.** "30 of 88 at \|z\| > 4"
> is not an anomaly: genuine blocks give 32–40. "Up to 33 %" is not an anomaly:
> genuine blocks reach 38 %. A 33 % swing in a bin whose expectation is ~10
> counts is ordinary counting noise, not a defect.
>
> **What this does and does not overturn.**
> - It **removes the bin-level statistical evidence** for the quarantine. The
>   sentence "the inconsistency is broad, not local" describes what a 1/10 sample
>   of this data looks like.
> - It does **not** lift the quarantine, and this annotation does not lift it.
>   Two independent grounds are untouched: the anchor is **unprovenanced**, and
>   the physics result it produced was **contradicted by two traceable datasets**.
>   Quarantining an unprovenanced artifact is a process decision that needs no
>   statistics.
> - **It raises a question this annotation deliberately does not answer.** If the
>   anchor is statistically ordinary, the **−7.4 σ** Σ_b result it produced needs
>   another explanation. One candidate is arithmetic rather than physical: a
>   significance computed on replicated counts is inflated by the same ~5×, which
>   would turn a ~1.5 σ fluctuation into a 7.4 σ claim. **That is a hypothesis,
>   not a finding — it was not checked**, and it is an owner decision whether to
>   check it. **E4 and E5 may be one defect seen twice.**
>
> > **✅ CLOSED 2026-08-13, owner-ruled: the hypothesis is confirmed and the
> > "may be" is now "is".** −7.4 σ ÷ 5.03 = **−1.47 σ**, which is the "~1.5 σ"
> > guessed above, reached independently. **E4 and E5 are one defect seen
> > twice**, and the unification is recorded as **E6** with the two other
> > findings that share the cause. The merged central's countervailing **+5.1 σ**
> > deflates to **+1.01 σ**, so the charge-ordering question is **unresolved**
> > rather than settled either way. **No further investigation** — owner ruling.
>
> Measured with `extraction/compare_subset_parent.py` (both nulls) over
> `tune_runs/MONASH` (replicated, the old chain's own output) and
> `anchors/merged_monash_dedup` (deduplicated), 88 testable bins throughout.

**Sixteen flagged bins deviate by more than 2 %, up to 33 %**, median 3.1 % —
these are not sub-percent differences inflated by large N. **The large ones are
almost entirely baryons** (Ω_b, Ω*_b, Ξ'_b, Ξ*_b, Σ_b, Σ*_b, Ξ*_c, Ξ'_c, Σ*_c);
flagged *mesons* deviate sub-percent. Σ̄_b⁻ (+10.4 %, z = +11.0) is among the
largest but **Ξ*_c⁺ (+6.3 %, z = +11.6) is comparable**.

> *Deflated 2026-08-13 (**E6**, ÷5.03): z = +11.0 → **+2.19**, z = +11.6 →
> **+2.31**. The percentages are unchanged — a uniform factor cancels in a
> ratio. Cross-check: the robust MAD null, computed independently, puts the same
> two bins at +2.70 and +2.83.*

**What it cost.** A pre-registered ordering test (Task 1 of the v46 brief) was
run on it and returned **MISS, "exactly reversed", −7.4 σ** — a result stated
with full statistical confidence. The merged central gives **+1.35 % ± 0.27 %
(+5.1 σ)**, the predicted sign; 1000 files of raw counts agree in sign.
**The MISS was retracted the same session.**

> *Deflated 2026-08-13 (**E6**, ÷5.03): −7.4 σ → **−1.47 σ**, +5.1 σ →
> **+1.01 σ**. **Both are null**, so the retraction stands but the confirmation
> does not: the charge-ordering question is **unresolved**, not settled in favour
> of the prediction. The sign agreement of the raw counts is unaffected — those
> are generator records, not extraction weights.
> `SIGMA_B_ORDERING_AND_ADJUDICATION.md` carries the full table.*

### Agent side

**The measurement was correct; the dataset was not.** No check compared the
anchor against the parent it was drawn from, and its provenance was already
known to be unrecoverable — that was recorded on 2026-08-11 and treated as a
documentation gap rather than as a reason to distrust the numbers.

### Owner side

The anchor had been the basis of every extraction table for several
generations, and **no subset-vs-parent consistency check was ever specified**
for it. The provenance gap was known and accepted.

### Why nothing caught it

- **Aggregates hide it.** The anchor's totals, species shares, second-branch
  number and map-v2 table all agree with the merged parent to **< 0.02 pp**.
  Every check the project ran was an aggregate check — and they still agree,
  because the affected sector carries ~2 % of total weight while charm mesons
  carry ~90 %.
- **It was found by accident**: Task 1 ran on the anchor and Task 2 ran on the
  merged central, and the two disagreed. **Had both run on the anchor, the bin
  would have reached external review inside a committed artifact.**

### Mechanism added

**`extraction/compare_subset_parent.py`** — per-bin z-scores against an expected
scale factor, flagging |z| > 4, with the anchor case as its regression test.
**A compare tool that cannot fail its known case certifies nothing**, so the
test asserts it *rediscovers* Σ̄_b⁻ and flags nothing else.

> **The lesson: aggregate agreement is not bin agreement.** Four independent
> aggregate checks passed on a dataset with a 10 σ bin defect.

---

## E5 — 2026-08-13: the published decomposition counted every trigger 24 or 26 times

**Found by external adversarial review of `f0e67dc` (finding A1). CONFIRMED.**

**The defect.** `hFlavourClosure` and `hFlavourClosureSpecies` are owned by the
**trigger**, not by the trigger-associate pair. The analysis builds one
accumulator per distinct trigger PDG
(`analysis/status_analysis_THnSparse_qq.C:870-879`) and then writes that same
object into **every pair file sharing that trigger** (`:1179-1191`).
`extraction/extract_species_decomposition.py` iterated all 300 files and summed
every projection into `species_tot`. It built `per_pair_species` and never read
it.

**Measured, not assumed.** From the committed 300-pair registry: each of the six
charm triggers appears in **24** pair files, each of the six beauty triggers in
**26**; 144 + 156 = 300. So the published total is

    T[b] = 24 * C[b] + 26 * B[b]

**The proof that the published product carries it.** The closure loop weights an
associate by `-q_trig * q_assoc` with the charge taken **in the trigger's own
sector**, and skips associates whose charge in that sector is zero
(`:1026-1032`). A charm trigger therefore only ever fills charm-carrying
species, and a beauty trigger only beauty-carrying ones. Under replication every
charm-only species total must be divisible by 24 and every beauty-only one by
26. In `anchors/merged_monash_central/per_species.csv`:

| test | result |
|---|---|
| 45 charm-only species divisible by 24 | **45 of 45**, zero violations |
| 42 beauty-only species divisible by 26 | **42 of 42**, zero violations |
| control: charm-only *also* divisible by 26 | only 5 of 45 — the divisibility is sector-specific, not universal |
| control: beauty-only *also* divisible by 24 | only 2 of 42 |
| 8 mixed-sector (B_c, Ξ_bc, Ω_bc) species | mixed remainders, exactly as `24C + 26B` predicts |
| gcd of all 94 nonzero totals | **exactly 2** = gcd(24, 26) |

Under a correct extraction the probability of that pattern is ≈ 24⁻⁴⁵ · 26⁻⁴²
≈ 10⁻¹²¹. **The defect is in the published numbers, not merely in the code.**

### The correction

| quantity | published (replicated) | corrected (deduplicated) | Δ |
|---|---|---|---|
| total entries | **1,298,655,240** | **53,662,414 … 53,662,828** | ÷ 24.2004 |
| kCentralGround | 679,701,042 — 52.3388 % | 28,170,632 — **52.4958 %** | **+0.1570 pp** |
| kExcludedVector | 605,835,226 — 46.6510 % | 24,950,243 — **46.4946 %** | **−0.1563 pp** |
| kExcludedExcited | 13,118,780 — 1.0102 % | 541,738 — **1.0095 %** | −0.0007 pp |
| kMultiplyHeavy | 192 — 0.0000 % | 8 — 0.0000 % | — |
| charm share of sector total | 89.2404 % | **89.9852 %** | **+0.7448 pp** |
| beauty share of sector total | 10.7596 % | **10.0148 %** | **−0.7448 pp** |

**Within-sector ratios are exactly unchanged** — the common factor cancels.
D⁰/D⁺, D̄⁰/D⁻, Λ_c⁺/D⁰, B⁺/B⁰, Λ_b⁰/B⁰, B⁻/B̄⁰ all give ratio-of-ratios
= 1.000000. **Cross-sector and absolute quantities are wrong; within-sector
ratios were never affected.** That is the whole shape of the error.

**The residual ambiguity is stated, not hidden.** The eight beauty-charm species
are fed by both sectors, so `24C + 26B = T` does not determine `C + B` for them.
Their combined weight is 129,164 of 1,298,655,240 (0.0099 %), and the resulting
bracket on the corrected total is **414 counts out of 53.66 million —
0.00077 %**. Every corrected figure above is quoted at the bracket midpoint;
the bracket is carried per-row in the artifact.

> **This is a reconstruction, not a re-extraction.** The corrected table is an
> exact arithmetic inversion of the committed replicated CSV, regenerable with
> `tools/reconstruct_deduplicated_decomposition.py`. **A live re-extraction with
> the fixed extractor still has to be run against the 300 merged pair files on
> the cluster**, and until it is, these numbers stand as reconstruction.

### Why nothing caught it

- **Every self-check was replication-blind.** `from_species == from_closure`
  holds exactly, because both views are duplicated *identically*. Central ==
  sum(blocks) holds, because both sides carry the same duplicated data.
  `MONASH_CENTRAL_TABLE.md` read that identity as **"No loss, no duplication"** —
  it establishes neither. An invariant that cannot distinguish one copy from
  twenty-four cannot certify uniqueness.
- **The duplication was known and misjudged.** `DESIGN_AND_RATIONALE.md` called
  it a "storage wart, not a correctness problem" and quoted a stale factor of
  **18**. It was a correctness problem the moment an extractor summed the files,
  and the factor was 24/26.
- **It survived E4's remedy.** `compare_subset_parent.py` compares a subset to
  its parent at an *expected scale factor* — both sides replicated identically,
  so it cannot see this.

### Mechanism added

- **`deduplicate_by_trigger()`** in the extractor: sums each trigger's closure
  once, keyed by the signed registry, and **fails closed if two files carrying
  the same trigger disagree in any bin** — because if they are not copies, the
  premise of deduplication is broken and choosing either is a guess.
- **`tests/test_closure_trigger_deduplication.py`**: measures the 24×/26×
  replication from the registry rather than assuming it, checks the arithmetic
  against a negative control, exercises the fail-closed path, and pins the
  sector-divisibility fingerprint of the published table so this cannot be
  quietly re-labelled as never having happened.
- **`tools/reconstruct_deduplicated_decomposition.py`**: verifies the
  fingerprint before inverting, and **refuses to "correct" a table that does not
  carry the defect**.

> **The lesson: a self-check built from two views of the same file cannot
> detect anything the file does to both of them.** Species and category agreed
> to 1e-9 through a 24× error.

> ### ⚠ ANNOTATED 2026-08-13 — the closure histograms are NOT the only replicated objects
>
> **Nothing above changes.** This entry describes the defect that happened, which
> was about `hFlavourClosure` / `hFlavourClosureSpecies`. But the per-pair-file
> write loop (`analysis/status_analysis_THnSparse_qq.C:1179-1191`) replicates
> **three classes of object**, and an entry naming only one of them will not warn
> the next person:
>
> | object | ownership | written into |
> |---|---|---|
> | `summed MULTIPLICITY` | **event-level** | **all 300** pair files, identically |
> | `hTrKinematics`, `hFlavourClosure`, `hFlavourClosureSpecies`, `hFlavourClosureSummary` | **trigger**-owned | every pair file sharing that trigger — **24× charm, 26× beauty** |
> | `hCorrelations`, `hAsKinematics`, `hCorrelationsByOrigin` | genuinely per-pair | one file each |
>
> **So `hTrKinematics` carries the same 24×/26× replication as the closure, and
> `summed MULTIPLICITY` carries a 300× one.** Summing either across pair files
> reproduces E5 exactly: a trigger-count normalisation built from summed
> `hTrKinematics` is inflated ~24×, and a per-event normalisation from summed
> `MULTIPLICITY` is inflated 300×.
>
> **The rule, stated generally:** *in a v3 merged pair directory, only the
> `hCorrelations` family is additive across files.* Anything trigger-owned or
> event-level must be read from **one** file, or verified identical across files
> — never summed.
>
> Found while checking whether the plotting stack was E5-exposed
> (`docs/PLOTTING_V3_DELTA.md` §0). **It is not**: it reads `hTrKinematics` one
> file at a time and treats `summed MULTIPLICITY` as an identity invariant with a
> `central_reference`, which is the correct handling and the reason it cannot
> fall into this by accident.

---

## E6 — 2026-08-13: three "findings" that were one arithmetic mistake

**Not a new defect. A unification.** Three separately-recorded, separately-explained
findings turn out to share a single cause: **E5's replication inflated every
binomial significance computed on extraction outputs by ~5×.**

### The arithmetic, which is the whole entry

Multiplying every count in a comparison by a factor **R** leaves fractions and
fractional deviations **exactly unchanged**, but scales a binomial pull by
**√R**:

```
(Rk − RNf) / sqrt(RNf(1−f))  =  sqrt(R) · (k − Nf) / sqrt(Nf(1−f))
```

**Measured: 5.03×** across ten block-vs-central comparisons (replicated
4.800 ± 0.519 against deduplicated 0.955 ± 0.096). **Predicted: √24.2 = 4.92.**
`tools/anchor_width_control.py` regenerates both sweeps.

### The three findings it dissolves

| recorded as | recorded cause | actual cause |
|---|---|---|
| **E4** — the anchor is "bin-inconsistent with its parent", 30 of 88 bins at \|z\| > 4 | a corrupt/unprovenanced extraction | genuine 1/10 subsets of the same replicated data give **32–40** flags. The anchor's 30 is **below** that range |
| **I2's 353 flags in 880 comparisons** | a real integrity concern, then a "misspecified null" | √R inflation. Deduplicated, I2 gives **0 flags in 10** |
| **"~4.75× overdispersion from event clustering"** | pair counts are event-clustered, so binomial variance understates | **there is no overdispersion.** Deduplicated blocks sit at **0.955 ± 0.096** — consistent with binomial |

**The third is the one worth dwelling on.** A plausible physical story — pair
counts are event-clustered, one event contributing many correlated pairs — was
invented to explain a number that arithmetic already explained. It was accepted
because it *sounded* right for the observable, and it then justified an
`--i2-advisory` escape hatch and a null replacement. **A mechanism that explains
your artifact is not evidence for the mechanism.**

### ⛔ WITHDRAWN: "Poisson/binomial errors on these fractions are ~5× too small"

**That warning is withdrawn. It holds only for replicated data**, where it is
not a property of the physics but of counting each trigger 24 or 26 times. On
deduplicated extraction output, binomial errors on these fractions are
**correct as computed**.

**No published number moves.** The paper's uncertainties are **empirical block
SEMs** — the spread of ten independently-formed block values — which are
correct under either variance structure because they measure the dispersion
rather than assuming it. The replication cancelled in them exactly as it
cancels in any fraction.

### What this does NOT overturn

- **The E4 quarantine stands** on its non-statistical grounds: the anchor is
  **unprovenanced**, and its physics result was contradicted by two traceable
  datasets. Quarantining an artifact with no recorded provenance needs no
  statistics.
- **The E5 defect itself is untouched.** The counts really were replicated; the
  corrected decomposition really is the measured one.
- **I2 and I3 remain non-redundant.** The MAD null's blindness to a broad or
  uniform displacement is a real property of median-centring, demonstrated by
  the A12 fixture, independent of any of this.

### The sweep of 2026-08-13 — what was annotated, and what was CLEARED

One pass over every tracked `.md` outside `docs/history/`. **Annotated beside
the original, never rewritten, never re-derived:**

| document | what deflated |
|---|---|
| `SIGMA_B_ORDERING_AND_ADJUDICATION.md` | −7.2, −0.8, −7.4, **+5.1**, 8.6, ~10 σ — the full table, at the head of the file |
| `B_BARYON_ADVISORY_DIAGNOSTIC.md` §3 | the whole σ column, 2.1 → 0.4 through 41 → 8.2 |
| `ERROR_RECORD.md` E4 (this file) | z = +11.0 → +2.19, z = +11.6 → +2.31, −7.4 → −1.47, +5.1 → +1.01 |
| `anchors/extraction_dual/MANIFEST.md` | the same three |
| `MONASH_CENTRAL_TABLE.md` §3 | the "~5× too small" warning **withdrawn** |

**CLEARED — checked and found unaffected**, recorded so the next reader does not
re-open them:

| document | why it is unaffected |
|---|---|
| `PRODUCTION_SHAPE_DECISION.md` (15.0, 35.2, 0.8, 12.6, 16.0, 23.0 σ) | ⟨N_ch⟩ from **six 200 k-event generator runs reading production cards directly**. No pair extraction, no closure histograms, no replication |
| `RELEASE_BLOCKERS.md` (0.8 σ, 12.6 σ) | the same multiplicity measurement, quoted |
| Σ_b **R1**, **R2**, **R3 at 400 files** | **raw generator records, no analysis chain** — the verdict table labels them so |
| Σ*_b **+3.2 σ at 1000 files** | raw counts |
| every **block SEM** in the project | empirical, measures dispersion instead of assuming it |

### The countermeasure

**Any significance quoted on extraction counts must name the basis** —
replicated or deduplicated — because the same statistic differs by 5× between
them.

> **The lesson: when three unrelated results all need a ~5× fudge, the fudge is
> the finding.** Each was explained locally and plausibly, and no local
> explanation was wrong enough to notice. What found it was dividing.

---

## E7 — 2026-08-13: a correctness guard that selected on the outcome variable

**The guard was right about the failure it feared and wrong about the sample
size, and the combination made it a bias.**

The A2 permissive variation threw when a job restored nothing:

```
ONE_PASS_ANALYSIS_ERROR A2 permissive mode restored nothing -- a silent zero
would make every measured shift trivially zero and look like a clean null
```

The intent is sound: a patch that silently no-ops turns a "variation" into a
re-run of the baseline, and that must not pass quietly.

### What made it a defect

The measured restoration rates are wildly tune-dependent:

| tune | restored per M events | zero-restoration jobs, of 100 |
|---|---|---|
| MONASH | **6.2** | **49** |
| JUNCTIONS | 1 219.4 | 0 |
| CLOSEPACKING | 1 228.7 | 0 |

At 6.2 per million a 100 000-event job restores **0.62 on average**, so zero is
the *modal* outcome — Poisson gives e^−0.62 = 54 %, and 49 % was observed.
**The guard therefore discarded roughly half the MONASH sample and none of the
other two.**

> **The discarded half was not random: it was exactly the jobs where the
> variation changed least.** The surviving MONASH sample was selected on the
> outcome variable, in one arm of the comparison, in the direction that inflates
> the measured shift. A guard against a spurious null had become a generator of
> a spurious signal.

### The rule this yields

> **Provenance and physics are different questions, and one check must not
> answer both.**
>
> - *"Did the right code run?"* is **provenance**. It is answered per job, by
>   identity — here `analysis_macro_sha256` in the job metadata, plus the
>   regression gate. It is a property of the executable, not of the data.
> - *"How much did it find?"* is **physics**. Its answer includes **zero**, and
>   zero is data.
>
> A per-job assertion on a physics quantity is a filter on the result. Where a
> did-it-work assertion is genuinely needed, it belongs at the level where the
> quantity is no longer sampling noise — here **campaign** level, at which zero
> restorations across the whole sample really is a defect.

**The fix.** The throw is gone; the count is emitted as a recorded value with
`contested_seen_charm/beauty` beside it, so a legitimate zero is legible — it
says contested rows existed and were declined for the pre-registered reasons,
rather than that the branch never ran. The assertion moved to
`check_campaign_restoration()` in `analysis/a2_block_shift.py`. Macro
`22120383…` → `a4df31e6…`; the superseded outputs are preserved, not deleted.

> **What did NOT go wrong: nothing entered a calculation.** The guard blocked
> *promotion*, so no biased number was ever computed — the held jobs simply
> never became inputs. It was caught in the gap between running the campaign and
> consuming it, which is the last place it could still be caught for free.

---

## E8 — 2026-08-17: two guards keyed on a process identity, neither saying what the identity means

**A guard that watches a PID is watching a proxy.** What it cares about is
whether some work has *finished*; what it can cheaply observe is whether a
process *exists*. Those differ on exactly one event — a restart — and both of
this project's process-keyed guards were written without saying which reading
they intended. **They fail in opposite directions, which is why neither was a
warning about the other.**

### Instance 1 — the pinfile reads ABSENCE as completion

`/data/alice/ipardoza/Hadronization/.git/checkout_pin` (created 2026-08-10 23:07)
carries the removal protocol for the checkout freeze:

> *Remove this file ONLY after BOTH are verified: 1. the log contains 33
> `PROMOTED_MERGE` lines, and 2. PID `3675829` has exited.*

The 2026-08-12 scheduled reboot killed `3675829`. The merge was restarted twice
and is alive as `315689`; the log the file names, `merge_v3.log`, froze at 15
`PROMOTED_MERGE`, while the live run writes `merge_v6.log` with 18.

| clause | literal check | what it actually means |
|---|---|---|
| PID `3675829` exited | **absent → reads as satisfied** | killed by a reboot, not by finishing |
| named log holds 33 | `merge_v3.log` has **15** | 15 + 18 = 33 only when summed across a log the file does not name |

**Both clauses of a protocol written to prevent removal read as satisfied while
the run it protects is still reading the tree** — in its redundant closure phase,
which emits no further `PROMOTED_MERGE` lines, so the log clause would never
advance again either.

**The file anticipated the wrong trap.** It argues at length that *time* is not
the condition — *"If the date above has passed and the merge is still running,
the merge wins"* — and then keys the condition to a PID and a log path, both of
which a restart invalidates.

### Instance 2 — the supervisor reads ABSENCE as death

`tools/merge_supervisor.sh` detects the merge by process presence
(`pgrep -f "merge_root_files.sh ${FREEZE}"`) and **nothing downstream
distinguishes an exit 0 from a crash**. On a *cleanly completed* merge all five
pre-checks still pass, so it would restart a finished merge into another
12 h 42 m preamble, up to `MAX_RESTARTS=6`
(`docs/history/THREE_TUNE_PROVISIONAL_SESSION_20260815.md` §1,
`docs/COMPONENTS.md`).

### The two are mirror images, and that is the finding

| | absence of the PID is taken to mean | cost of being wrong |
|---|---|---|
| pinfile | **"the work finished"** | the freeze lifts under a live merge; a 65 h run is invalidated |
| supervisor | **"the work died"** | a completed merge is restarted; 12 h of preamble burned |

**One reads absence as success, the other as failure, and neither states which.**
A reviewer of either would have found the other by asking one question: *what
does this identity's absence mean?*

### ⚠ The remedy already existed — this is E3's shape again

`tools/supervisor_eol_watch.sh` (2026-08-15) fixed instance 2 by keying on a
**content marker** rather than a process state:
`CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=CLOSEPACKING`, chosen because it is *the
last statement in* `merge_root_files.sh`. Its own design note states the
principle exactly: *"Once that line is printed the merge has done all its work,
so stopping the supervisor is correct whether the merge then exits 0 or is
killed."*

**That is precisely the condition the pinfile needed** — invented five days after
the pinfile was written, for the mirror-image guard, and never carried across.
E3 in this record is *"a mechanism found, then not applied where it also held"*;
**E8 is a recurrence of E3, with a five-day gap and two files.**

### The rule this yields

> **A guard that pins a process identity must state what the identity means, and
> a restart must invalidate it LOUDLY rather than satisfy it silently.**
>
> - Prefer a **completion fact** to a process state. A marker emitted by the work
>   itself — the last line of the script, a promotion receipt, a closure verdict —
>   survives restarts, reboots and renumbering, because it records that something
>   *happened* rather than that something *is*.
> - Where a PID is genuinely needed it must be **paired** with a completion fact,
>   and the protocol must say which clause is authoritative when they disagree.
>   Absence of the PID with the marker also absent is a **death**, not a
>   completion, and must read as "still pinned".
> - **Never name a mutable path as evidence.** `merge_v3.log` was right when
>   written and wrong three restarts later. Name the *invariant* — the newest log
>   for this run, resolved at read time — as the EOL watcher's own newest-log
>   resolution already does.
> - **A PID is meaningless without its host.** Added the same day, from a
>   near-miss by the session that wrote this entry: a check of `ps -p 315689` run
>   on `stbc-i1` returned **absent** while the merge was alive on `stbc-i3`, and
>   for about a minute that read as the death case this very rule describes. The
>   pinfile gets this right — it records `host = stbc-i3.nikhef.nl` — and the
>   check dropped it. **An identity checked in the wrong context is
>   indistinguishable from an identity that has exited**, which is the same defect
>   as the reboot case wearing different clothes. Any protocol naming a PID must
>   name its host, and any check of one must assert it is on that host.

### The fix

**Owner ruling, 2026-08-17 (second Consolidation A addendum): the recorded
protocol is INVALID.** The operative condition is
`CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=CLOSEPACKING` **present** *and* PID
`315689` **exited cleanly** — a completion fact paired with the live identity, in
that order of authority. **The gate session refreshes the pinfile to say so,
superseded content preserved and dated, before any removal**; removal only under
the corrected condition.

### How it was caught, and what did NOT go wrong

**Caught by testing each clause of a stated protocol against reality instead of
reading the protocol.** The systematics session needed to know whether its 2100
in-flight jobs blocked the checkout advance; establishing that they did not led to
the guard, and asking *why* the guard would still refuse led to the pinfile, whose
named PID proved absent while the merge it protects was alive.

> **Nothing was removed and nothing was invalidated.** The pinfile was still in
> place, the checkout still at `43e35be8`, the merge still running. The trap was
> found **before** an advance — the only place it could be found for free. The
> next place would have been 33 merged legs and a closure pass needing to be
> re-run.

---

### Third facet — 2026-08-18: argv is not identity, and a wrapper is not its worker

Two more ways a process-keyed check reads the wrong thing, both met while
adopting a render left running by a previous session.

**1. `argv` says nothing about what a heredoc-fed interpreter is doing.** The
renders are launched as `root -l -b <<ROOTCMDS`, so the macro arrives on
**stdin**. The worker's command line is:

```
/cvmfs/.../bin/root.exe -splash -l -b
```

There is no macro name in it, and there is no target name. Every ROOT job on the
host looks identical. A check written as `pgrep -f Plot_InclusiveKinematic`
therefore matches **nothing at all** — and its silence is indistinguishable from
"no such job is running". **A search that cannot succeed reports the same thing
as a search that found nothing.**

What does identify a process, all of it read-only:

| signal | where | what it settled here |
|---|---|---|
| lineage | `pgid`, `ppid` | `1060713 → 1060896 → 1060897` was ONE job, not three |
| cwd | `/proc/<pid>/cwd` | which deploy tree it renders from |
| stdout | `/proc/<pid>/fd/1` | **which log, hence which target** — the only thing that named it |
| open input | `/proc/<pid>/fd/5` | which raw file, hence how far along |
| CPU accumulation | `ps -o time=` | that it is *working*, not merely *present* |

`fd/1` did the work `argv` could not: the worker held
`fig4_render2.log` open, which is what identified it as the figure-4 re-render.

**2. Killing a wrapper does not kill its worker.** An earlier session relaunched
a render by killing the `bash run_paper_plots.sh` wrapper and starting a new one.
The `root.exe` under it kept running, re-parented to `init`, still holding the
old ACLiC library and still writing the same output paths — a **pre-fix worker
racing a post-fix one for the same paper figure**. It was found only because its
`cwd` and `fd` matched the new render's. Signal the **process group**, and then
verify the group is empty; never assume the children went with the parent.

### Fourth facet — 2026-08-18: a liveness probe that cannot distinguish "gone" from "could not ask"

A waiter inherited from a previous session was:

```
until ! ssh stbc 'kill -0 1060713 2>/dev/null'; do sleep 90; done
echo "RE-RENDER EXITED"
```

`ssh` exits non-zero when the **transport** fails, not only when the remote
`kill -0` fails. So an unreachable login node — and `stbc-i3` had been
unreachable earlier the same night — makes the loop announce that the job
finished. The waiter was found already exited while its target was still running
with 24 minutes of CPU behind it. **It reported completion of a job that had not
completed.**

This is the E8 shape once more, one level out: the probe conflated *the answer
is no* with *there was no answer*. A three-state probe is required —

```
ALIVE | GONE | INCONCLUSIVE
```

— and only an affirmative `GONE`, from a probe that itself succeeded, may end
the wait. The replacement waiter written this session logged **five consecutive
inconclusive probes** against a healthy render and correctly kept waiting; the
old form would have declared that render dead five times over.

> **Rule.** A remote liveness check must separate the transport's exit status
> from the predicate's. Absence of an answer is not an answer.

---

## Earlier entries, held in the handoff chain

Not restated here; `HANDOFF_20260809_v21_GENERATIONAL.md` §5 and
`HANDOFF_20260810_v40_GENERATIONAL.md` §5 carry them in full.

- **Owner → agent:** the withdrawn merge escalation (twice), built from a
  *prefix* of an ordered workload; Edit D's descendant walk, guarding a hazard
  that cannot occur when decays are disabled.
- **Agent → owner:** the gate's pool sizing (it has none, by design); the
  441 MiB cross-attribution; B6's "30×" against a per-tune figure.
- **Agent → self:** M7 was charm-only, found while writing the limits section;
  the v35 atime probe measured *any* read, not the gate's.
- **The recurring mode:** six invocation failures across four sessions, every
  one caught by a fail-closed check, none reaching a number. **Design right,
  invocation wrong.** Countermeasure: **`rc=0` is not evidence** — check for the
  expected output, count, or summary line.

---

## E9 — 2026-08-17: a published class label rounded twice, and read 59.9 % for 59.8 %

**The smallest error in this record, and it reached a rendered figure.** The
multiplicity-class legend on the committed reference canvas says **59.9 %** where
the axis definition gives **59.8 %**.

### The arithmetic

`config/multiplicity_class_boundaries_v1.json` puts class boundary c5 at
`N_ch = 6.5`. Its MONASH minimum-bias percentile, recomputed from the committed
anchor `AnalysisScripts/anchors/b4_multiplicity_mb/nch_mb_MONASH.csv`
(172 429 events) as the fraction strictly below, is

```
59.849561 %      ->  59.8 %   at one decimal
```

The frozen boundary receipt stores percentiles to **three** decimals, so it holds
`59.850`. The plotting configurations were written by transcribing **from the
receipt**, and `59.850` rounds to `59.9`. **Two roundings, and the second one
crossed a boundary the first had already moved.**

| | value |
|---|---|
| full precision | 59.849561 % |
| correct, rounded once | **59.8 %** |
| receipt, 3 dp | 59.850 % |
| configs, rounded a second time | **59.9 %** ← wrong |

### Where it reached

Two label positions per config — the upper edge of c4's range and the lower edge
of c5's — in **at least two committed configurations**
(`configuration_multiplicity_HF_RUN3_V1_{MONASH,THREETUNE}_THnSparse_complete_root.json`),
20 label corrections in total. **It is on the rendered reference figure**, whose
legend reads `59.9-65.9%` and `50.3-59.9%`.

### Why it happened, and why it is not merely a typo

The boundary artifact says in its own text that it is the ONE definition of the
axis and that **no consumer may carry a literal copy**, "because two definitions
drift, and the axis is the thing every per-multiplicity number is conditioned
on". A hand-written percentile in a plotting config is exactly such a copy.
Nothing compared it to the artifact, so nothing could notice.

The error is small — 0.05 percentage points on a label — and that is the point.
**A transcription that is nearly right is the kind that survives review.** The
defect is not the digit; it is that a display value had a second, unchecked
definition.

### Standing rule

> **Display values are rounded ONCE, from full precision, and generated from the
> boundary artifact. Never transcribed, and never rounded from an
> already-rounded intermediate.**

### Fix

`tools/apply_class_labels.py` regenerates every class label from
`config/multiplicity_class_boundaries_v1.json` and the committed MB anchor, by
the published rule, and is `--check`-able in the same shape as the repository's
other generators. **The corrections are staged in the polish-proposal config and
land at merge, gated on owner sign-off** — the committed reference stays
byte-identical until then.

### How it was found

By the single-axis-definition check, the **B6** family: asking whether every
consumer of the multiplicity axis resolves the artifact rather than holding a
copy. The same question that found the figure-4 inset computing its own
quantiles found this. **Neither was found by looking at the figure**, which is
why both had survived.

---

### Addendum, 2026-08-18 — the defect re-emerged inside the generator built to prevent it

The axis self-declaration that V-EXTREMES and V-INTEGRATED carry is produced by
`tools/make_variant_configs.py`, written precisely so a figure cannot describe an
axis it does not have. Its first version took each class's range from the
configuration's own `multiplicityMin` / `multiplicityMax` — and those are the
transcribed labels E9 is about, still carrying the stale `59.85`. It therefore
printed **59.9** where the artifact says **59.8**, on the very sentence meant to
guarantee the figure's honesty, and it would have gone onto both new paper
figures. Caught by derive-don't-transcribe review of the generator's own source
**before any render was spent**, and fixed in `67552fc` to read
`percentile_label()` against the boundary artifact.
`tests/test_display_filter.py` now pins both directions: 59.8 must appear in the
declaration and 59.9 must not. **The lesson is that "generated" is not the
property that matters — generated FROM WHAT is.** A generator reading a
transcribed value launders a transcription into something that looks derived.

## E10 — 2026-08-17: figure 4 captioned a |η| ≤ 1 counter as |η| ≤ 4

**A constant that was correct somewhere else on the same canvas family.** The
shared charged-multiplicity spectrum printed an η acceptance **four times wider
than the number it drew**.

### The two constants, and which one the histogram uses

The quantity plotted is `hMULTIPLICITY`. The producer fills it from
`multiplicityCentral`, counted by `CountsNchPrimaryChargedV1`
(`generation/producer/HeavyFlavourUtils.h:539`, called at
`generation/producer/heavyflavourcorrelations_status.cpp:1058`):

```
isFinal && isCharged && !hasHeavyConstituent &&
    IsMultiplicityKinematic(pt, eta, kMultiplicityEtaCentral)
```

`IsMultiplicityKinematic` (`:533`) is `pt > kMultiplicityPtMin && |eta| <= etaMax`,
and the counter passes **`kMultiplicityEtaCentral = 1.0`**.

The caption hardcoded `"|#eta| #leq 4"`. **4.0 is a real constant in this code**
— `kMultiplicityEtaWide`, and `IsCentralKinematic`'s limit (`:467`) — but it is
the **ASSOCIATE** acceptance, the one that governs the pT/η/φ spectra drawn by
the *same macro*, in the *same run*, onto the *same canvas family*.

| | value | governs |
|---|---|---|
| `kMultiplicityEtaCentral` | **1.0** | the counter that fills `hMULTIPLICITY` ← figure 4 |
| `kMultiplicityEtaWide` / `IsCentralKinematic` | 4.0 | the pT/η/φ associate spectra |
| printed on figure 4 | **4** | ← wrong by a factor of 4 |

### Why it happened, and why it is a transcription error

This is not a typo and not a wrong cut — **the histogram was always right**. A
number was copied into a caption from the neighbouring context in which that
same number is correct. Nothing connected the caption to the counter, so the
caption could not notice that it had been given the other figure's acceptance.

**E9 and E10 are the same defect wearing different clothes.** E9 transcribed a
display value from an already-rounded intermediate; E10 transcribed a display
value from the adjacent selection. In both the drawn quantity was correct and
only the words about it were wrong, and in both the wrong words were *plausible*
— 59.9 is nearly 59.8, and 4.0 is genuinely one of this macro's η limits. That
is exactly what makes them survive review.

### Standing rule — unified, and it now covers E9, E10 and the B6 family

> **Every constant in presentation text DERIVES, in code, from the constants
> that fill the histogram it describes. Nothing is transcribed — not from a
> receipt, not from a rounded intermediate, and not from the selection next
> door.**

E9's rule (round once, from full precision, generated from the artifact) and
B6's rule (every consumer resolves the axis artifact, no consumer holds a copy)
are the same rule applied to a percentile and to an axis. E10 extends it from
*values* to *the selection a caption asserts*.

> **Refinement, 2026-08-18 — same value is not same symbol.** Deriving from a
> named constant that merely *equals* what the predicate evaluates is still
> transcription: `IsCentralKinematic` carried `0.15` and `4.0` as literals while
> identically-valued `kMultiplicityPtMin` and `kMultiplicityEtaWide` sat further
> down the same header, so a caption built from those names would have agreed
> with the cut only by coincidence and would have drifted silently the moment
> either was edited. **Derive from the same symbol the filling code evaluates**,
> or make it the same symbol first. Fixed in `5f3f381`, which refactored the
> predicates onto `kCentralPtMinAssociate`, `kCentralPtMinTrigger`,
> `kCentralEtaAbsMax` and `kDirectPrimaryStatus{Min,Max}` before the species
> captions were allowed to read them. **Caught in review, before any wrong
> output existed** — the only entry in this record with no defective artifact
> behind it.

### Fix

`MultiplicityDefinitionLine2()` and `MultiplicityDefinitionLine3()`
(`plotting/Plot_InclusiveKinematicSpectra_Raw.C`) now build their strings from
`Hadronization::kMultiplicityPtMin` and `Hadronization::kMultiplicityEtaCentral`
— the counter's own constants. **Change the cut and the caption moves with it;
the label is now unable to disagree with the histogram.** Line 3 additionally
states the two qualifiers a bare cut omits: *primary charged*, *heavy flavour
excluded* (`!hasHeavyConstituent`).

### Consequence

The render that exposed it is superseded. `MultiplicitySpectrum_Shared_shape.png`
sha256 `4d7ab97ebd19729858e5b63e1dc9de3ff81b2e6f2c18c19560d416c92aa4ac52`
carries the wrong η label and is **not caption-ready**; its digest was
deliberately withheld from `GOLDEN_OUTPUTS.md` §9.2 rather than entered. The
re-render costs another full 3000-file checksum pass (~40 min), which is the
ruled cost of the contract and is not to be cached around.

### How it was found

**By looking at the rendered figure.** E10 is the one defect of this session
that looking caught — and the only one it caught: E9 and the figure-4 inset both
came from the single-definition audit and were invisible on the canvas. The two
methods are not substitutes.

> Looking finds what is *stated wrongly*. Auditing definitions finds what is
> *derived wrongly*. Figure 4 needed both, and had one.
