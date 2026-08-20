# The three-tune central table — **FINAL**

> # ✅ PROMOTED TO FINAL — 2026-08-16
>
> **Both outstanding closures PASSED.** JUNCTIONS returned 2026-08-16 11:58:20
> CEST after 13 h 50 m, CLOSEPACKING 11:37:27 after 13 h 29 m, each at
> `errors=0`, **2100 content / 1500 invariant**, schema
> `paul_pair_objects_primary_ground_v3`. **Both lines are recorded verbatim in
> §0b** and were checked with
> `extraction/pipeline/harvest_tune.py --stage closure`, not by eye.
>
> **The ⛔ that stood here from 2026-08-15 is struck.** The provisional caveats
> below are struck with it; no number moved on promotion, because the numbers
> were measured before the verdicts and the verdicts did not touch them.
>
> **MONASH's column was already final** — closure PASSED 2026-08-12, table of
> record `docs/MONASH_CENTRAL_TABLE.md` §0 — and is **reused, not re-run**. The
> reproduction below is a control on the instrument.
>
> ### ✅ RULED 2026-08-20 — the I2 flags are a DEVIATION, not an amendment
>
> `docs/PER_TUNE_PROCESSING_PREREGISTRATION.md` step 2 registers **I2 = zero
> flagged bins**, and says a step-2 failure stops that tune's step 3.
> **JUNCTIONS has 3 flags and CLOSEPACKING 1** (§3d).
>
> **Owner ruling: record the departure, do not edit the registration.** The
> registered expectation of zero flagged bins stands exactly as written, and the
> four flags are reported against it as a deviation. The pre-registration is
> **not** amended, because a registration edited after the result is no longer a
> registration.
>
> **The measured basis, unchanged by the ruling** (§3d, §3e):
>
> - all three JUNCTIONS flags sit in `kMultiplyHeavy`, a category contributing
>   **12 of 116** testable bins where MONASH contributed **0 of 88**;
> - that subpopulation's block scatter is **1.60×** binomial against ~1.0
>   elsewhere, so a pooled single-σ̂ null tests those bins against a scale ~1.4×
>   too small; rescaled, the three flags are **|z| ≈ 2.5, 2.5, 2.7**;
> - the CLOSEPACKING flag is **1 in ~2 960 comparisons** against ~0.19 expected,
>   p ≈ 0.17, and is isolated in block, conjugate and neighbourhood;
> - jackknifing the flagged blocks moves **no quoted row by more than 1.19 SEM
>   or 0.006 pp**.
>
> **What is still not established** is *why* `kMultiplyHeavy` is overdispersed.
> A category-aware null is the obvious follow-up and is deliberately not made
> here: retuning a null until it stops flagging is how a real defect gets
> normalised away.
>
> **The table's FINAL status stands on this ruling plus the closure verdicts.**

---

## 0. What is established

| | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| blocks merged | 10 / 10 | 10 / 10 | 10 / 10 |
| **closure verdict** | **PASS** (2026-08-12) | **PASS** (2026-08-16) | **PASS** (2026-08-16) |
| extraction | done | done | done |
| **I3** blocks sum to central, bin by bin | **PASS exact** | **PASS exact** | **PASS exact** |
| **I2** block-vs-central, MAD null | **0 flags / 10** | **3 flags / 10** ⚠ | **1 flag / 10** ⚠ |
| status of the numbers below | **FINAL** | **FINAL** | **FINAL** |

---

## 0b. The closure verdicts, verbatim

**JUNCTIONS** — `closure_runs/closure_HF_RUN3_V1_JUNCTIONS_20260815_220840.log`,
finished 2026-08-16 11:58:20 CEST:

```
PAIR_BLOCK_CLOSURE errors=0 analysis_schema=paul_pair_objects_primary_ground_v3 central_pair_files=300 block_pair_files=3000 object_content_sumw2_closure_checks=2100 additive_metadata_closure_checks=3600 invariant_metadata_checks=1500 source_filter_contract_checks=300 expected_central_events=100000000 relative_tolerance=2e-10
```

**CLOSEPACKING** — `closure_runs/closure_HF_RUN3_V1_CLOSEPACKING_20260815_220842.log`,
finished 2026-08-16 11:37:27 CEST:

```
PAIR_BLOCK_CLOSURE errors=0 analysis_schema=paul_pair_objects_primary_ground_v3 central_pair_files=300 block_pair_files=3000 object_content_sumw2_closure_checks=2100 additive_metadata_closure_checks=3600 invariant_metadata_checks=1500 source_filter_contract_checks=300 expected_central_events=100000000 relative_tolerance=2e-10
```

**The two lines are identical field for field**, and identical to MONASH's
except for `expected_central_events`, which is `-1` in MONASH's recorded line
because that run took the chains' weak argument. **These two took the strong
`100000000`**, so the central's event count was asserted rather than accepted.

| registered (`CLOSURE_V3_PREREGISTRATION.md`) | required | JUNCTIONS | CLOSEPACKING | |
|---|---|---|---|---|
| **C1** content comparisons | **2100** = 7×300 | 2100 | 2100 | **PASS** |
| **C2** invariant comparisons | **1500** = 5×300 | 1500 | 1500 | **PASS** |
| **C3** closure + identity failures | **0** | 0 | 0 | **PASS** |
| **C4** schema from each file's own `analysis_schema` | `…_v3` | `…_v3` | `…_v3` | **PASS** |
| tolerance | as registered | 2e-10 | 2e-10 | **PASS** |

**Not the 1800/600 failure mode.** The v2-sidecar resolution that would have
looked like a pass did not occur in either tune.

> **How the schema was verified, and why it is worth stating.** The A4
> expected-schema argument **does not exist on the frozen Nikhef tree** — that
> wrapper takes `CENTRAL BLOCK_BASE [EXPECTED_CENTRAL_EVENTS]`, and A4's fix
> lives only in the local checkout, which cannot advance while the merge reads
> the frozen one. **The schema was therefore verified by reading the emitted
> `analysis_schema=` value against the pre-registration**, which is exactly what
> `harvest_tune.py`'s `closure_verdict()` was written to do. Checked by reading,
> deliberately, not overlooked.
>
> **The wrapper's own gate is corroborating evidence.** Its failure branch
> unconditionally writes `RETAINED closure log for diagnosis` to stderr, and
> both runs had stderr redirected into these logs. **Neither log contains that
> line**, so both took the success path — an independent confirmation of exit 0
> for two detached processes whose exit status no shell held.

### Independently confirmed by the merge

The merge's own sequential closure pass — a **separate process reading the same
directories** — reached `CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=MONASH` at
2026-08-16 12:39 with a summary line identical to the two above. Its JUNCTIONS
pass was still running at the time of writing.

---

> ## ✅ RULED 2026-08-20 — THE PAPER QUOTES BOTH, AND EXPERIMENT-COMPARABLE IS PRIMARY
>
> **The observable definition adopts the experiment-comparable convention.** The
> diquark-structure partition is quoted beside it, as the mechanism-level
> decomposition that explains the primary number.
>
> **The reasoning.** The experiment-comparable convention is the number a
> measurement can confront. That is what makes this work a **proposed
> observable** rather than a model-internal comparison between three tunes — a
> quantity nobody can measure cannot be a proposal, however clean its
> decomposition. The diquark-structure partition answers a different and
> necessary question, *what the generator made*, and it is what turns the primary
> number from a result into an explanation. Neither is dropped, and the order is
> the claim.
>
> **What follows from the order.** The excluded-fraction problem is severe in the
> structural framing and largely dissolves in the experiment-comparable one,
> because the vectors' weight is reassigned to the ground states they decay into
> rather than left in a category the analysis does not count. Making the
> experiment-comparable table primary therefore means the paper's headline
> quantity does **not** carry a large unexplained residual — and the structural
> table, quoted beside it, is where that residual is shown and accounted for.
>
> **What travels with the ruling.** The primary number now depends on
> decay-parent map **v2**, and inherits its provenance: residual misassignment
> **0.0018 %** (`docs/MAP_V2_RESULT.md` §1), built on the v1.1 conjugation fix.
> **The experiment-comparable table is a SELECTION, not a partition** — it sums
> to ~91 % deliberately, and must never be normalised.

> **Note on the section headings below.** §1 is headed "(primary)" because it was
> written before this ruling and its heading is left as it stands rather than
> silently rewritten. **The ruling above governs**: §2, experiment-comparable, is
> the paper's primary convention, and §1 is the mechanism-level decomposition
> quoted beside it. `docs/EXTRACTION_CONVENTIONS.md` §3 carries the same ruling
> and the reasoning in full.

## 1. DIQUARK-STRUCTURE (primary) — a PARTITION, sums to 100 %

Fractions in percent. **SEM is the ten-block standard error, dof = 9**;
fractions are formed inside each block and then averaged, never as a ratio of
summed numerators to summed denominators.

| group | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| **kCentralGround** | **52.4959** ± 0.0074 | **58.2318** ± 0.0078 | **54.1697** ± 0.0112 |
| **kExcludedVector** | **46.4946** ± 0.0079 | **39.9409** ± 0.0083 | **39.9976** ± 0.0105 |
| **kExcludedExcited** | **1.0095** ± 0.0012 | **1.7821** ± 0.0015 | **5.7745** ± 0.0050 |
| **kMultiplyHeavy** | **0.0000** ± 0.0000 | **0.0452** ± 0.0004 | **0.0583** ± 0.0007 |
| **sum** | 100.0000 | 100.0000 | 100.0000 |

## 2. EXPERIMENT-COMPARABLE (decay map v2, split)

> ### ⚠ This table is a **SELECTION, not a partition.**
> **These rows do not sum to 100 % and are not meant to.** Each row is an
> observable a detector reconstructs; the rows are the largest of them, not a
> complete decomposition. A reader who sums the column and finds ~91 % has not
> found missing weight. The diquark-structure table above **is** a partition
> and does sum to 100 %.

| observable | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| **D⁰** | **25.4543** ± 0.0038 | **22.9720** ± 0.0067 | **22.8191** ± 0.0058 |
| **D̄⁰** | **25.3809** ± 0.0070 | **22.9102** ± 0.0056 | **22.7796** ± 0.0072 |
| **D⁺** | **13.2505** ± 0.0035 | **12.0333** ± 0.0034 | **11.9725** ± 0.0038 |
| **D⁻** | **13.2225** ± 0.0032 | **11.9964** ± 0.0029 | **11.9557** ± 0.0045 |
| **D_s⁺** | **4.2720** ± 0.0015 | **3.4894** ± 0.0022 | **4.0852** ± 0.0030 |
| **D_s⁻** | **4.2684** ± 0.0017 | **3.4965** ± 0.0030 | **4.0529** ± 0.0032 |
| **Λ_c⁺** | **1.6401** ± 0.0019 | **5.6503** ± 0.0028 | **5.1222** ± 0.0037 |
| **Λ̄_c⁻** | **1.6049** ± 0.0015 | **5.5632** ± 0.0041 | **5.1018** ± 0.0036 |
| **B⁺** | **2.1441** ± 0.0017 | **1.4879** ± 0.0012 | **1.4048** ± 0.0015 |
| **B⁻** | **2.1431** ± 0.0024 | **1.4868** ± 0.0023 | **1.4020** ± 0.0026 |
| selection total | 93.3808 | 91.0860 | 90.6958 |

**The row set is common to all three columns by construction.** Each tune's own
top-8 is a *different* set — MONASH's carries B±, the CR tunes' carries Λ_c —
so a table built from three top-8 lists would not be comparable column to
column. The union of the two is used, and every cell is measured, not blank.

**Pooled agrees with the block mean everywhere:** worst
|block mean − pooled| / SEM over all 42 cells and both conventions is **0.001**.

---

## 3. Integrity

### 3a. I3 — exact for all three tunes

| tune | central total | block sum | verdict |
|---|---|---|---|
| MONASH | 53,662,416 | 53,662,416 | **PASS, exactly** |
| JUNCTIONS | 46,311,148 | 46,311,148 | **PASS, exactly** |
| CLOSEPACKING | 46,678,201 | 46,678,201 | **PASS, exactly** |

> **What this does and does not establish** — the correction carried from
> `MONASH_CENTRAL_TABLE.md` §3 stands. Central == sum(blocks) establishes that
> the *addition* is exact. It does **not** certify source-level uniqueness,
> because both sides carry the same data. That is what the deduplication line
> and the closure are for.

### 3b. Per-event plausibility — every absolute count, all 33 directories

The standing check that caught E5. **~0.54/event is the MONASH-calibrated
scale; the replicated era read 12.9866.**

| tune | central | ten blocks (min–max) |
|---|---|---|
| MONASH | **0.5366** | 0.5363 – 0.5370 |
| JUNCTIONS | **0.4631** | 0.4625 – 0.4634 |
| CLOSEPACKING | **0.4668** | 0.4664 – 0.4672 |

**All 33 counts are plausible.** Nothing is within an order of magnitude of the
replicated signature.

### 3c. Deduplication, read from the data in every directory

All **22** newly extracted directories report
`DEDUPLICATION … replication in this directory: beauty [26]x, charm [24]x`, and
all 22 report `SELF_CHECK AGREE worst_relative=0.000e+00` — the sum rule at
**1e-9**, met exactly. Regrouping invariance CONSERVED in every directory.

### 3d. I2 — **4 flags across the two new tunes, and they are reported, not waved through**

`docs/PER_TUNE_PROCESSING_PREREGISTRATION.md` says **"any flag at all is
notable; two or more is a finding."** JUNCTIONS has three and CLOSEPACKING one,
so both are recorded here for the owner's ruling. **Neither was downgraded with
`--i2-advisory`**; the tool exits 4 for both and that status is reported.

**JUNCTIONS — 3 flags, all in one newly-testable category.**

| block | ordinal | species | category | block | expected | z |
|---|---|---|---|---|---|---|
| 4 | 58 | Ω*_ccbar⁻ | kMultiplyHeavy | 2 | 24.4 | −4.02 |
| 7 | 139 | Ξ*_cc⁺ | kMultiplyHeavy | 214 | 159.0 | +4.04 |
| 7 | 143 | Ω*_cc⁺ | kMultiplyHeavy | 50 | 26.4 | +4.25 |

Three facts, measured:

1. **The category is testable for the first time in this tune.** MONASH's
   kMultiplyHeavy holds **8 entries in 3 ordinals** and contributes **0 of its
   88 testable bins**. JUNCTIONS holds **20,935 entries in 29 ordinals** and
   contributes **12 of 116**. The flags are in bins MONASH could not test.
2. **All three flags land in that 12-bin subset**, which under flags falling
   uniformly across bins has probability (12/116)³ ≈ **1.1 × 10⁻³**.
3. **That subset's dispersion is genuinely different.** Observed block scatter ÷
   binomial σ, by category: kCentralGround **1.11**, kExcludedVector **0.98**,
   kExcludedExcited **1.07**, **kMultiplyHeavy 1.60**. I2's MAD null estimates
   **one** σ̂ (1.12) pooled over all bins, so bins drawn from a 1.6×-dispersed
   subpopulation are tested against a scale ~1.4× too small. Rescaled to their
   own subpopulation the three flags are **|z| ≈ 2.5, 2.5, 2.7** — unremarkable.

> **Stated with its limit.** A pooled single-σ̂ null being misspecified for a
> subpopulation is a *measured* property here, not an inference. What is **not**
> established is *why* kMultiplyHeavy is overdispersed. Doubly-heavy baryon
> production being event-clustered is the natural reading, but with 12 species
> and ten blocks each ratio carries ~24 % uncertainty, and the low/high count
> split is 2 species against 10 — **too thin to claim magnitude dependence.**
> `docs/ERROR_RECORD.md` E6 is the standing warning against reading a scale
> factor as physics on this project, and it applies to this paragraph.

**CLOSEPACKING — 1 flag, and it is a different shape.**

| block | ordinal | species | category | block | expected | z |
|---|---|---|---|---|---|---|
| 2 | 128 | Σ*_c⁺ | kExcludedExcited | 30,174 | 30,890.1 | −4.28 |

Not the kMultiplyHeavy story: a **high-count** species (308,901 entries,
0.66 % of total) reading 2.3 % low in one block. **It is isolated in both
directions**, which is what separates it from E4's shape:

- its **conjugate** Σ*_cbar⁻ in the same block is **+1.16** — no sector effect;
- **block_2's total** (4,667,129) sits mid-pack among the ten
  (4,664,009–4,671,798) — no block effect;
- the **next largest** pull anywhere in block_2 is **+2.54** — it stands alone.

Setting the kMultiplyHeavy subpopulation aside, this is **1 flag in ~2,960
comparisons** across the three tunes against ~0.19 expected — p ≈ 0.17, i.e.
consistent with the false-positive rate. **E4's defect was 30 of 88 bins
displaced together. One isolated bin does not resemble it.**

### 3e. Materiality — jackknife

Dropping the flagged blocks and recomputing every structural row:

| tune | largest shift in pp | largest shift in SEM |
|---|---|---|
| JUNCTIONS (drop blocks 4, 7) | **0.0056 pp** (kExcludedVector, 0.67 SEM) | **1.19 SEM** (kExcludedExcited, 0.0017 pp) |
| CLOSEPACKING (drop block 2) | **0.0026 pp** (kCentralGround, 0.24 SEM) | **0.57 SEM** (kMultiplyHeavy, 0.0004 pp) |

*(The two columns are maxima over different rows — no single row shows both.)*

**No quoted row moves by as much as 1.2 SEM or 0.006 pp.** The flags are real
enough to report and too small to matter to this table.

---

## 4. Sanity read — JUNCTIONS against MONASH

**The brief's expectation is met and then some: the baryon share more than
triples.**

| | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| **baryon share of total pair weight** | **4.6093** ± 0.0028 | **16.5586** ± 0.0041 | — |

> **The raw category split understates it, and this is worth stating carefully.**
> kCentralGround rises 52.4959 → 58.2318, a net **+5.74 pp**. Split by
> baryon/meson, that net figure is the sum of two much larger opposing moves:

| component (% of total weight) | MONASH | JUNCTIONS | Δ |
|---|---|---|---|
| kCentralGround / **baryon** | 3.5997 ± 0.0024 | 14.7313 ± 0.0041 | **+11.13** |
| kCentralGround / meson | 48.8962 ± 0.0065 | 43.5006 ± 0.0072 | −5.40 |
| kExcludedVector / meson | 46.4946 ± 0.0079 | 39.9409 ± 0.0083 | −6.55 |
| kExcludedExcited / **baryon** | 1.0095 ± 0.0012 | 1.7821 ± 0.0015 | +0.77 |
| kMultiplyHeavy / **baryon** | 0.0000 | 0.0452 ± 0.0004 | +0.05 |

**Baryons gain +11.95 pp and mesons lose exactly that.** kExcludedVector is
entirely mesonic and kExcludedExcited entirely baryonic in both tunes, so the
kCentralGround/kExcludedVector shift the brief points at is real — but the
mechanism is legible only once kCentralGround is split, because that category
holds both.

> ### ⚠ The tune-bundle confound stands, unchanged
> JUNCTIONS re-tunes `StringFlav` and `StringZ` alongside `ColourReconnection`
> — **28 allowed differences across nine families, only 8 of them CR.** A
> MONASH-vs-JUNCTIONS difference in a baryon observable **cannot be attributed
> to junction formation alone.** This is a reason to finish the harvest, not a
> finding about junctions.

---

## 5. b-baryon particle/antiparticle advisory — **it reverses its own pre-registration**

Step 2 of the ladder in `docs/B_BARYON_ADVISORY_DIAGNOSTIC.md` §2, which that
document records as *blocked* on exactly this three-tune output. Raw weights,
**no map applied** — the basis step 1 used. Ratios formed inside each block,
then averaged; SEM over ten blocks, dof = 9.

**Loose pre-registration: CR ≥ MONASH** (junction baryon-number transport
should carry at least MONASH's asymmetry).

| species | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| Λ_b⁰ | 1.0124 ± 0.0052 | 0.9965 ± 0.0047 | 0.9849 ± 0.0053 |
| Ξ_b⁰ | 1.0491 ± 0.0138 | 1.0077 ± 0.0111 | 1.0077 ± 0.0138 |
| Ξ_b⁻ | 1.0455 ± 0.0112 | 0.9984 ± 0.0120 | 1.0135 ± 0.0117 |
| Σ*_b⁰ | 1.2188 ± 0.0187 | 1.0073 ± 0.0107 | 0.9945 ± 0.0045 |
| Σ*_b⁺ | 1.2104 ± 0.0187 | 0.9968 ± 0.0122 | 0.9960 ± 0.0041 |
| Σ*_b⁻ | 1.1687 ± 0.0260 | 1.0014 ± 0.0083 | 0.9998 ± 0.0042 |
| **Σ_b⁺** | **1.6377** ± 0.0244 | 1.0332 ± 0.0043 | 1.0236 ± 0.0060 |
| **Σ_b⁻** | **1.5950** ± 0.0288 | 1.0138 ± 0.0039 | 1.0221 ± 0.0072 |
| **Σ_b⁰** | **1.5858** ± 0.0357 | 1.0168 ± 0.0035 | 1.0057 ± 0.0061 |
| Ξ*_b⁰ | 1.3620 ± 0.0432 | 1.0214 ± 0.0273 | 1.0177 ± 0.0073 |
| Ξ*_b⁻ | 1.3204 ± 0.0264 | 0.9955 ± 0.0238 | 1.0192 ± 0.0090 |
| **Ξ'_b⁰** | **1.7572** ± 0.0759 | 1.0193 ± 0.0090 | 1.0325 ± 0.0103 |
| **Ξ'_b⁻** | **1.7766** ± 0.0736 | 1.0287 ± 0.0094 | 1.0522 ± 0.0081 |

> ## The pre-registration fails, in the opposite direction, 0 of 13 in both CR tunes
>
> **MONASH — the tune with no colour reconnection and no junctions — carries the
> asymmetry** (Σ_b and Ξ'_b at **1.59–1.78**, tens of SEM from unity). **Both CR
> tunes are consistent with symmetric** (0.98–1.05).
>
> This is the discriminator the diagnostic asked for, and it answers more
> sharply than the question anticipated. §2 of that document had already
> observed that the asymmetry "does not require the junction transport
> mechanism, because that mechanism is not active in this sample". With three
> tunes, junction transport is not merely unnecessary — **the CR tunes wash the
> asymmetry out.**
>
> **The confound in §4 applies here with full force and is not a footnote.** The
> CR tunes also re-tune `StringFlav` and `StringZ`, so "CR removes it" is **not**
> established; "the CR *tunes* do not show it" is. The CR tunes also carry far
> more b-baryon statistics (Σ_b⁺: 130,011 and 68,419 against MONASH's 6,402), so
> the near-unity values are the better-measured ones.
>
> **Advisory only. It is not a gate and it fails nothing.** Both closures have
> since PASSED (§0b), so it is no longer provisional — but it remains an
> advisory, and the confound above is the reason it cannot be read as a result
> about colour reconnection.

### ✅ RULED 2026-08-20 — REPORT it, as a short subsection, not a headline

**The paper reports this measurement.** It is a real, sharp and unexpected
result: the pre-registration expected CR ≥ MONASH and got the reverse in **0 of
13** species, in both reconnection tunes.

**Placement: a short subsection or an appendix, and not a headline claim.** The
reason is the confound, and the ruling requires it stated in the same paragraph
as the result rather than in a footnote.

**The paragraph the manuscript must carry**, recorded here as the ruling and
**not executed against `Paper/**`**:

> MONASH — the tune with neither colour reconnection nor junctions — carries a
> particle/antiparticle asymmetry in the b-baryons, with Σ_b and Ξ'_b at
> **1.59–1.78**, tens of SEM from unity. Both reconnection tunes are consistent
> with symmetric, at **0.98–1.05**. **Two things prevent reading this as an
> effect of colour reconnection.** First, the reconnection tunes also re-tune
> `StringFlav` and `StringZ`, so what is established is that *these tune bundles*
> do not show the asymmetry, and not that colour reconnection removes it.
> Second, the samples differ roughly **twenty-fold** in b-baryon statistics —
> Σ_b⁺ at 130 011 and 68 419 entries against MONASH's 6 402 — so the near-unity
> values are the better-measured ones and the asymmetry sits in the sparsest
> sample.

**Why report it despite the confound.** The confound limits the *attribution*,
not the *observation*. That MONASH shows the asymmetry and the two CR tunes do
not is measured, reproducible from the committed anchors, and would be found by
anyone repeating the analysis. Withholding it because its cause is ambiguous
would leave a reader to rediscover it and wonder why it went unmentioned.

**What must not appear:** any sentence of the form "colour reconnection removes
the b-baryon asymmetry". `STATE.md` records the tune-bundle confound under NOT
PLANNED as *"Documented, not resolved"*, and resolving it needs a tune that
varies reconnection alone — a production no plan in this repository contains.

---

## 6. Provenance

| | |
|---|---|
| extractor | `extract_species_decomposition.py` sha256 `4cd8b6fa8493529624b33de81e67764c07c2126465d7ae921e5970919f0ad960` |
| ordinal artifact | `species_ordinals_v2.json` sha256 `ccec0dbc70f6452d…d0e4ce` |
| pair registry | `heavy_flavour_pair_registry_v1.json` sha256 `ea9b0232c1be8415…ddee23` — **`--registry` present, the corrected chain path** |
| decay map | `decay_parent_map_v2.json` sha256 `58081aa2f87cb671…1c84da` |
| decomposition tool | `decompose_with_block_sems.py` sha256 `f05a011fbc1d6d10…936963` |
| **all four shas** | **identical to `MONASH_CENTRAL_TABLE.md` §0's provenance** — the same instrument, not a re-implementation |
| ROOT | `/cvmfs/…/ROOT/v6-30-01-alice5-2` — 6.30/01, **on pin**, `stbc-i3.nikhef.nl` |
| extraction window | 2026-08-15 **22:12:39 → 22:32:01** CEST, 22 directories, 0 failures |
| outputs | `/data/alice/ipardoza/tune_runs_three/{JUNCTIONS,CLOSEPACKING}/{central,block_1..10}/` |
| MONASH outputs | `/data/alice/ipardoza/tune_runs_e5fix/MONASH/` — **2026-08-13, reused unchanged** |
| merged inputs | all three centrals: `analysis_commit 61fe978f…`, freeze seal `e03fb1e7…`, **1000 input files each** — identical merge machinery |
| local decomposition | pure Python under `HF_ALLOW_UNPINNED_ENV=1`; suite **44/44** |

### Two controls on the instrument, both passed

1. **MONASH re-run reproduces its committed table to the last digit** — every
   structural and experiment-comparable value in §0 of
   `MONASH_CENTRAL_TABLE.md`, I3 exact at 53,662,416, I2 0 flags. The reuse of
   MONASH's column is therefore corroborated rather than assumed.
2. **JUNCTIONS central re-extracted byte-identical** to the independent
   2026-08-13 extraction (`per_species.csv` and `per_category.csv` both `cmp`
   clean), two days apart into a different run root.

---

## 7. Closed on promotion, and the one item still open

**Closed 2026-08-16:**

1. ~~JUNCTIONS and CLOSEPACKING closures return and are checked verbatim~~ —
   **done, both PASS**, §0b.
2. ~~A FAIL stops that tune~~ — **did not arise.**

**Closed 2026-08-20 — the last one:**

3. ~~**The owner's ruling on §3d.**~~ **RULED: a deviation, not an amendment.**
   The registration stands as written and the four flags are reported against
   it. See the ruling box in §0. The paragraph below is the state as it stood
   before the ruling, kept because the reasoning it records is what the ruling
   rests on.

   **The owner's ruling on §3d.** `PER_TUNE_PROCESSING_PREREGISTRATION.md` step 2
   registers **I2 = zero flagged bins** and states that a step-2 failure stops
   that tune's step 3. **Four flags exist across the two new tunes** and this
   document was promoted on the closure verdicts regardless, because that is
   what the 2026-08-16 brief gated promotion on. **That is a scoping decision,
   not a measurement**, and it is the one place where this table's FINAL status
   rests on a judgement rather than on a check.
   **What is measured, and is not in doubt:** the flags are confined to bins the
   step-2 framing predates (kMultiplyHeavy was 0 of MONASH's 88 testable bins),
   the subpopulation's dispersion is 1.6× binomial against ~1.0 elsewhere, and
   jackknifing the flagged blocks moves **no row by more than 1.19 SEM**.
   **What is not established** is why that subpopulation is overdispersed.
   The obvious follow-up is a category-aware null — and it is **not** a change
   to make quietly, because retuning a null until it stops flagging is how a
   real defect gets normalised away.

> **Every item in §7 is now closed.** The table is FINAL on the closure verdicts
> and on the 2026-08-20 deviation ruling, and nothing in this document waits on
> a decision.

### The regeneration recipe

```bash
extraction/three_tune_table.py \
  MONASH=AnalysisScripts/anchors/merged_monash_dedup \
  JUNCTIONS=AnalysisScripts/anchors/merged_junctions_dedup \
  CLOSEPACKING=AnalysisScripts/anchors/merged_closepacking_dedup
```

**stdout sha256 `a46a7f6b96f668177ee600746e51eadf1dfaabdaceac07c1265ef5d7d0fc930d`.**

**This runs from the repository alone** — the three anchors are committed, so
the table no longer depends on directories that exist only on `stbc-i3`. The
remote run roots in §6 give the **same digest byte for byte**; they are the
origin, not a dependency. `tests/test_three_tune_tables.py` asserts every
structural cell and that digest, so `make check` catches a table that moved
without this document moving.

> **On the closure's third argument.** `docs/PER_TUNE_PROCESSING_PREREGISTRATION.md`
> step 1 calls for the expected-schema argument (review finding A4). **That
> argument does not exist on Nikhef**: the frozen checkout's wrapper takes
> `CENTRAL BLOCK_BASE [EXPECTED_CENTRAL_EVENTS]`, and A4's fix lives only in the
> local checkout, which cannot be advanced while the merge reads the frozen tree
> (`docs/history/MERGE_SUPERVISOR_SESSION_20260814a.md` §2). **Schema
> verification is therefore by reading the emitted `analysis_schema=` value
> against the pre-registration**, which is exactly what `harvest_tune.py`'s
> `closure_verdict()` exists to do and why it was written. **This was checked
> that way deliberately, not overlooked.** The strong
> `expected_central_events=100000000` was passed, matching the merge's own
> invocation rather than the chains' `-1`.
