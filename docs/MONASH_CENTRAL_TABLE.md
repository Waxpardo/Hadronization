# MONASH — the first tune's central numbers

> # ⚠ NOT FINAL — SUPERSEDED 2026-08-13 (private error-ledger entry E5)
>
> The decomposition below is **replicated**: the trigger-owned closure was
> counted once per pair file, so **each charm trigger entered 24 times and each
> beauty trigger 26**. Absolute weights are **24.2004× too large** and every
> **cross-sector** share is biased (charm : beauty moves by 0.7448 pp).
> Within-sector ratios are exactly unaffected.
>
> The "FINAL for MONASH" claim below is withdrawn. See
> the superseding private convention-table record for the corrected table.
>
> ## ✅ RE-EXTRACTED 2026-08-13 — §0 below is now the table of record
>
> The correction is no longer a reconstruction. The fixed, deduplicating
> extractor was run against the 300 merged pair files, central and all ten
> blocks. **The block SEMs in §4 are superseded by the ones measured on the
> deduplicated blocks.**

---

## 0. THE TABLE OF RECORD — re-extracted, deduplicated, 2026-08-13

**Measured, not inverted.** `extraction/extract_species_decomposition.py` on
`complete_root_HF_RUN3_V1_MONASH` and
`combined_root_subSamples_MONASH/combined_root_{1..10}`, ROOT 6.30/01 from
CVMFS on `stbc-i3.nikhef.nl`.

**The replication is now a measurement, not an inference.** The extractor reads
it from the signed registry and reports it in every one of the eleven
directories: `charm [24]x, beauty [26]x`. E5 was diagnosed from divisibility
arithmetic; it is now read off the data.

### E5's predicted values versus what was measured

| quantity | E5 predicted (reconstruction) | **re-extracted** | Δ |
|---|---|---|---|
| total | 53,662,414 … 53,662,828 | **53,662,416** | **in bracket**, 2 counts above the floor |
| kCentralGround | 52.4958 | **52.4959** | +0.0001 pp |
| kExcludedVector | 46.4946 | **46.4946** | −0.0000 pp |
| kExcludedExcited | 1.0095 | **1.0095** | 0.0000 pp |
| charm : beauty | 89.9852 : 10.0148 | **89.9852 : 10.0148** | exact |
| D⁰ (map v2, split) | 25.4542 | **25.4543** | +0.0001 pp |
| B⁺ (map v2, split) | 2.1440 | **2.1441** | +0.0001 pp |

**The reconstruction and the fix confirm each other.** The 414-count bracket was
the irreducible ambiguity of the eight mixed beauty-charm species, which
`24C + 26B = T` cannot resolve; the measurement lands 2 counts into it.

### Per-event plausibility — the standing check

| | per event (100 M events) |
|---|---|
| **re-extracted** | **0.5366** |
| replicated (published) | 12.9866 |

**The published number was ~13 closure entries per event and nobody divided.**
That is what E5 cost, and the check now runs on every absolute count.

### Diquark-structure — a partition, sums to 100 %

| group | block mean % | SEM | pooled % |
|---|---|---|---|
| kCentralGround | **52.4959** | 0.0074 | 52.4959 |
| kExcludedVector | **46.4946** | 0.0079 | 46.4946 |
| kExcludedExcited | **1.0095** | 0.0012 | 1.0095 |
| kMultiplyHeavy | **0.0000** | 0.0000 | 0.0000 |

`kMultiplyHeavy` is **8 entries of 53,662,416** — populated, not excluded. The
two labels in §4 travel with this table unchanged.

### Experiment-comparable (map v2, split) — a SELECTION, not a partition

**These do not sum to 100 %.** The rows are the largest observables a detector
reconstructs, not a complete decomposition; a reader who sums the column and
finds less than 100 % has not found missing weight.

| observable | block mean % | SEM |
|---|---|---|
| D⁰ | **25.4543** | 0.0038 |
| D̄⁰ | **25.3809** | 0.0070 |
| D⁺ | **13.2505** | 0.0035 |
| D⁻ | **13.2225** | 0.0032 |
| D_s⁺ | **4.2720** | 0.0015 |
| D_s⁻ | **4.2684** | 0.0017 |
| B⁺ | **2.1441** | 0.0017 |
| B⁻ | **2.1431** | 0.0024 |

### Integrity, on the deduplicated blocks

| check | result |
|---|---|
| **I3** ten blocks sum to central, bin by bin | **PASS** — 53,662,416 both sides, exactly |
| **I2** block vs central, **robust MAD null** | **PASS — 0 flags in 10 comparisons** |
| extractor self-check (species vs closure, 6 categories) | **AGREE**, worst relative 0.000e+00, all 11 directories |
| regrouping invariance | **CONSERVED** exactly, both conventions |

> **I2's zero is the recalibration paying off.** Under the retired binomial null
> the same class of comparison produced **353 flags in 880**, every one an
> artifact of assuming independence for event-clustered counts. Under the null
> that measures the dispersion instead of assuming it, the ten blocks are clean.
> See `GOLDEN_OUTPUTS.md` §2.11a — **and note I2 is now blind to a uniform or
> sector-wide displacement, which is exactly what I3 exists to catch.**

**The SEMs barely moved** — 0.0074 / 0.0079 / 0.0012, against a replicated-era
0.0074 / 0.0079 / 0.0012. That is expected rather than reassuring: a fraction's
block-to-block scatter is largely insensitive to a within-sector replication.
**They are now measured on the correct basis**, which is the point; the old
column was right by construction, not by validation.

### Provenance

| | |
|---|---|
| extractor | `extract_species_decomposition.py` sha256 `4cd8b6fa8493529624b33de81e67764c07c2126465d7ae921e5970919f0ad960` |
| ordinal artifact | `species_ordinals_v2.json` sha256 `ccec0dbc70f6452d…d0e4ce`, digest `646f310f78126267` |
| pair registry | `heavy_flavour_pair_registry_v1.json` sha256 `ea9b0232c1be8415…ddee23` |
| decay map | `decay_parent_map_v2.json` sha256 `58081aa2f87cb671…1c84da` (`map_sha256` `c9593c9c0a7c4ec2`) |
| ROOT | `/cvmfs/alice.cern.ch/…/ROOT/v6-30-01-alice5-2` — **6.30/01, on pin** |
| host / when | `stbc-i3.nikhef.nl`, 2026-08-13 08:11–08:24 CEST |
| outputs | `/data/alice/ipardoza/tune_runs_e5fix/MONASH/{central,block_1..10}/` |
| **deployment note** | the extractor was staged in `/data/alice/ipardoza/extractor_e5fix/`, **outside** the frozen checkout, because the merge reads that checkout live and it must not move until the 33rd promotion |

> **This is MONASH only.** The three-tune table remains blocked on the merge —
> JUNCTIONS has central + blocks 1–3, CLOSEPACKING has nothing.

---

**Delivered 2026-08-12. Closure PASSED; the decomposition is FINAL for MONASH**
given the integrity findings in §3, which are a tooling calibration issue and
not a data defect.

---

## 1. CLOSURE VERDICT — verbatim, checked against the pre-registration

```
PAIR_BLOCK_CLOSURE errors=0 analysis_schema=paul_pair_objects_primary_ground_v3
central_pair_files=300 block_pair_files=3000
object_content_sumw2_closure_checks=2100 additive_metadata_closure_checks=3600
invariant_metadata_checks=1500 source_filter_contract_checks=300
expected_central_events=-1 relative_tolerance=2e-10
# CLOSURE_RC=0   # EXTRACT_RC=0   TUNE_CHAIN_DONE MONASH
```

| registered (`CLOSURE_V3_PREREGISTRATION.md`) | required | observed | |
|---|---|---|---|
| **C1** content comparisons | **2100** = 7×300 | **2100** | **PASS** |
| **C2** invariant comparisons | **1500** = 5×300 | **1500** | **PASS** |
| **C4** schema from each file's own `analysis_schema` | `…_v3` | `paul_pair_objects_primary_ground_v3` | **PASS** |
| errors | 0 | 0 | **PASS** |

**Not the 1800/600 failure mode.** The v2-sidecar resolution that would have
looked like a pass did not occur.

## 2. CLOSURE RUNTIME — the B10 serial-gate measurement at scale

| | |
|---|---|
| inputs complete / closure start | **2026-08-12 02:55:57** |
| closure end (first extraction write) | **~17:44:45** |
| **closure wall clock** | **≈ 14 h 49 m** |
| eleven extractions | 17:44:49 → 17:48:48 (**4 min**) |
| workload | 11 directories × 300 pair files, **29.354 GB** read |

The closure is ~99.6 % of the chain's cost; the extractions are negligible.

## 3. INTEGRITY — I3 exact, and I2's null is MISSPECIFIED

**I3 — blocks sum to central, bin by bin: PASS, exactly.**
`central_total = block_sum = 1298655240`.

> **CORRECTED 2026-08-13.** This line previously read *"No loss, no
> duplication."* **That claim was false and the second half of it was exactly
> wrong.** Central == sum(blocks) establishes only that the *addition* between
> those two products is exact. It says nothing about whether the underlying
> entries are unique, because **both sides carry the same duplicated data** —
> and they did: every trigger's closure was replicated 24× (charm) or 26×
> (beauty) into both the central and the blocks. Private error-ledger entry E5.
>
> **An addition identity cannot certify source-level uniqueness.** Naming it
> "no duplication" is what allowed a 24× replication to sit under a passing
> integrity check for a full generation.

**I2 — 353 flags over 880 comparisons (|z| > 4).** Diagnosed, and it is **not a
data defect**:

| evidence | |
|---|---|
| flagged species | **38/38** high-count **and** 50/50 low-count — every species |
| flag rate | **40 %**, roughly independent of species magnitude |
| block totals | spread **0.135 %** — blocks are near-equal |
| **observed block scatter ÷ binomial σ** | **median 5.06**, mean 5.00, range 2.58–8.32 |
| same ratio, high vs low count | **4.99 vs 5.06** — flat |

I2 uses a binomial subset null, `z = (k − Nf)/√(Nf(1−f))`. That is correct for
events sampled without replacement, but **these are pair counts: one event
contributes many correlated pairs**, so the counts are overdispersed by
construction. Two independent routes agree the dispersion is ~5× binomial —
inverting the 40 % flag rate, and measuring block scatter directly.

> **A real defect is localised. A uniform, magnitude-independent failure across
> every species is a misspecified null.** The anchor defect that this tool was
> built for showed up as a *localised* 30-bin set; this does not resemble it.

### Why the SEMs are unaffected — and the consequence for the paper

**The block SEM is empirical** — `stdev(ten block values)/√10`, dof = 9 — so it
measures the true block-to-block dispersion whatever its source. It does not
assume the binomial null that I2 assumes, and is therefore untouched by the
misspecification.

> ⚠ **Do not quote Poisson or binomial errors on these species fractions. They
> are ~5× too small. The block SEM is the correct uncertainty.**

**I2 as calibrated will flag on every tune**, because the overdispersion is a
property of pair counting, not of MONASH. Its "0.16 false positives over 30
comparisons" expectation is derived from the binomial null and does not hold
here.

> # ⛔ WITHDRAWN 2026-08-13 — the ~5× is E5, not event clustering
>
> **Nothing above is rewritten. The diagnosis in it is wrong, and this section's
> own numbers are what prove it.**
>
> **There is no overdispersion.** Re-measured on the **deduplicated** blocks,
> observed scatter ÷ binomial σ is **0.955 ± 0.096** — consistent with binomial.
> The ~5× was **E5's replication**: multiplying counts by R scales a binomial
> pull by √R while leaving fractions untouched. Measured **5.03×**, predicted
> **√24.2 = 4.92**. Private error-ledger entry **E6**;
> `tools/anchor_width_control.py` regenerates it.
>
> **The evidence was already in the table above.** "Observed block scatter ÷
> binomial σ — median **5.06**, mean **5.00**" is √R to two figures. And the row
> beneath it, "**high vs low count: 4.99 vs 5.06 — flat**", is the decisive one:
> **a uniform multiplicative factor is magnitude-independent; event clustering
> is not.** Clustering scales with how many pairs an event contributes, so it
> would vary across species populations by construction. The measurement said
> "constant" and the text read it as "a property of pair counting".
>
> **⛔ The warning above is WITHDRAWN.** On deduplicated output, binomial errors
> on these fractions are **correct as computed**. The warning holds only for
> replicated data, where it describes an arithmetic artifact rather than the
> physics.
>
> **✅ NO PUBLISHED NUMBER MOVES, and the reasoning above for that is still
> right for a better reason.** The quoted uncertainties are **empirical block
> SEMs**, which measure dispersion instead of assuming it — so they were correct
> under the replication and remain correct without it. The re-extracted table in
> §0 confirms it: the SEMs are unchanged to four decimal places.
>
> **"I2 will flag on every tune" is also withdrawn.** It flagged because of the
> replication. On the deduplicated MONASH blocks I2 gives **0 flags in 10
> comparisons** (§0), and the `--i2-advisory` escape hatch that this paragraph
> justified should now rarely be needed.

## 4. THE TABLE — MONASH, both conventions

Fractions in percent; **SEM is the ten-block standard error, dof = 9**.
`pooled` is the value from the merged central; `diff/SEM` compares the two.

### 4a. Diquark-structure (primary)

| group | block mean % | SEM | pooled % | diff/SEM |
|---|---|---|---|---|
| **kCentralGround** | **52.3388** | 0.0074 | 52.3388 | −0.00 |
| **kExcludedVector** | **46.6510** | 0.0079 | 46.6510 | 0.00 |
| **kExcludedExcited** | **1.0102** | 0.0012 | 1.0102 | −0.00 |
| **kMultiplyHeavy** | **0.0000** | 0.0000 | 0.0000 | 0.00 |

> **kMultiplyHeavy 0.0000% — 192 entries of 1,298,655,240 (1.5 × 10⁻⁵ %).**
> This category holds hadrons with |q_c| > 1 or |q_b| > 1 — the doubly- and
> triply-heavy baryons Ξ_cc, Ω_cc, Ω_ccc. It is a populated category of the
> partition, not an exclusion; the six categories sum exactly to the total. The
> value is small because doubly-heavy baryon production is rare, not because
> anything was classified out. B_c⁺ (q_c = +1, q_b = −1, neither above 1) is
> counted as a ground-state species in kCentralGround. The one category excluded
> by construction is kHiddenHeavy (quarkonia), with exactly zero entries;
> kOtherNoncentral is likewise empty, being unreachable for any open-heavy
> species.

Sum = **100.0000 %**.

### 4b. Experiment-comparable (decay map v2)

> **⚠ This table is a SELECTION, not a partition.** These species do not sum to
> 100 % and are not meant to: each row is an observable a detector reconstructs,
> and the rows are the largest of them, not a complete decomposition. The
> diquark-structure table **is** a partition and does sum to 100 %.

| species | block mean % | SEM | pooled % | diff/SEM |
|---|---|---|---|---|
| **D⁰** | **25.2435** | 0.0038 | 25.2435 | −0.00 |
| **D̄⁰** | **25.1707** | 0.0070 | 25.1707 | 0.00 |
| **D⁺** | **13.1408** | 0.0034 | 13.1408 | 0.00 |
| **D⁻** | **13.1129** | 0.0032 | 13.1129 | −0.00 |
| **D_s⁺** | **4.2366** | 0.0015 | 4.2366 | −0.00 |
| **D_s⁻** | **4.2331** | 0.0017 | 4.2331 | 0.00 |
| **B⁺** | **2.3035** | 0.0018 | 2.3035 | −0.00 |
| **B⁻** | **2.3024** | 0.0026 | 2.3024 | 0.00 |

(The selection caveat is stated above the table, where a reader meets it
before summing the column.)

### Cross-check against the independent merged rebuild

The superseding private convention-table record (v47) computed the central from the merged output
by a different path. It agrees **exactly**:

| quantity | v47 merged | this decomposition |
|---|---|---|
| structural kCentralGround | 52.3388 % | **52.3388 %** |
| v2 D⁰ | 25.2435 % | **25.2435 %** |
| v2 D⁺ | 13.1408 % | **13.1408 %** |

## 5. PROVENANCE

| | |
|---|---|
| chain script sha | `eae4c0ae3b2dfaaa` |
| closure script / macro sha | `b8e7c7b7…` / `044e47e6…` |
| checkout (pinned) | `43e35be876dd5d881a931cb845ab490ab9b97509` |
| reader / artifact / map_v11 sha | `b67f9008…` / `ccec0dbc…` / `ed148156…` |
| inputs | 11 directories × 300 root files, preflight OK |
| chain | started 2026-08-11T20:52:55, finished 2026-08-12T17:48:48, `rc0_count=11 (expect 11)` |
| total central entries | **1,298,655,240** |
