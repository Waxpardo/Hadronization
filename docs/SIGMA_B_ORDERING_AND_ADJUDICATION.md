# Σ_b asymmetry — Task 1 ordering test, and the Task 2 adjudication pre-registration

> # ⚠ ANNOTATED 2026-08-13 — EVERY σ HERE COMPUTED ON EXTRACTION WEIGHTS IS ~5× TOO LARGE
>
> **Nothing below is rewritten or re-derived.** `docs/ERROR_RECORD.md` **E6**:
> E5's replication scales a binomial pull by **√R**, measured **5.03×**. Every
> significance in this document that comes from `per_species.csv` weights — the
> anchor's and the merged central's alike — divides by that. Fractions, ratios
> and asymmetry percentages are **unchanged**; only the σ values move.
>
> | claim in this document | as recorded | **deflated ÷ 5.03** | verdict now |
> |---|---|---|---|
> | Σ_b ordering, anchor: −6.17 % ± 0.86 % | **−7.2 σ** | **−1.43 σ** | **null** |
> | Σ*_b ordering, anchor: −0.57 % ± 0.67 % | −0.8 σ | −0.16 σ | null |
> | anchor, 91 ordinals (verdict table) | **−7.4 σ** | **−1.47 σ** | **null** |
> | merged MONASH central: +1.35 % ± 0.27 % | **+5.1 σ, HIT** | **+1.01 σ** | **null** |
> | anchor vs merged disagreement | 8.6 σ | 1.71 σ | not significant |
> | the Σ̄_b⁻ bin "~10 σ high" | ~10 σ | ~2.0 σ | ordinary |
>
> **UNAFFECTED — measured on raw generator records, no analysis chain:**
> **R1** (spin-sorted magnitudes, 1000 files), **R2** (forward growth), and
> **R3 at 400 files** (+0.7 σ, +1.9 σ), which the verdict table itself labels
> "raw counts, no chain". The **Σ*_b +3.2 σ at 1000 files** likewise stands.
>
> ## What stands, and what does not
>
> - ✅ **R1 and R2 STAND.** The spin-sorted asymmetry and its growth toward the
>   beam are in PYTHIA's own output, independent of the extraction chain. The
>   physics conclusion of "The verdict" below is unaffected.
> - ⛔ **The charge-ordering question is UNRESOLVED.** Both readings used to
>   settle it are null after deflation: the anchor's **−7.2 σ MISS** and the
>   merged central's **+5.1 σ HIT**. The retraction of Task 1's MISS below
>   **remains correct**, but for a different reason than it gives — it is now
>   correct because **neither dataset resolves the ordering**, not because the
>   merged central confirmed the prediction.
> - **No further investigation** — owner ruling, 2026-08-13.
>
> The retraction's *other* grounds are untouched: the anchor is unprovenanced,
> and its bin-level scatter is what any tenth of this data looks like
> (`ERROR_RECORD.md` E4's 2026-08-13 control).

**Task 1 verdict: MISS. For Σ_b the predicted ordering is EXACTLY REVERSED at
−7.2 σ.** Task 2 is pre-registered below, **before** any of its measurements
are run.

Background: `docs/B_BARYON_ADVISORY_DIAGNOSTIC.md`. The asymmetry is in the raw
extraction weights, not introduced by the decay map.

---

## 1. TASK 1 — the ordering test

**Pre-registered mechanism (owner's).** Fragmentation suppresses spin-1
diquarks; proton beam-remnant string ends are spin-1-rich (uu is pure spin-1,
ud is ¾ spin-0) and build baryons only. Under it the asymmetry must order by
valence-remnant feeding:

> **Σ_b⁺ (uub) > Σ_b⁰ (udb) > Σ_b⁻ (ddb)**, and identically for Σ*_b.

The logic that makes this a real test: **a counting error has no reason to know
proton valence structure.**

### Result — committed anchor `per_species.csv`, MONASH

| state | quarks | particle | anti | ratio | *A* |
|---|---|---|---|---|---|
| Σ_b⁺ | uub | 16,484 | 11,232 | 1.468 | **18.95 % ± 0.60** |
| Σ_b⁰ | udb | 16,510 | 9,932 | 1.662 | 24.88 % ± 0.61 |
| Σ_b⁻ | ddb | 16,640 | 9,958 | **1.671** | **25.12 % ± 0.61** |
| Σ*_b⁺ | uub | 23,556 | 21,502 | 1.096 | 4.56 % ± 0.47 |
| Σ*_b⁰ | udb | 24,180 | 20,358 | **1.188** | 8.58 % ± 0.47 |
| Σ*_b⁻ | ddb | 23,738 | 21,424 | 1.108 | 5.12 % ± 0.47 |

| | predicted | measured | verdict |
|---|---|---|---|
| **Σ_b** | Σ_b⁺ > Σ_b⁰ > Σ_b⁻ | **Σ_b⁻ > Σ_b⁰ > Σ_b⁺** | **MISS — exactly reversed** |
| **Σ*_b** | Σ*_b⁺ > Σ*_b⁰ > Σ*_b⁻ | Σ*_b⁰ > Σ*_b⁻ > Σ*_b⁺ | **MISS — no ordering** |

**The discriminating statistic:** *A*(uub) − *A*(ddb), which the mechanism
requires to be **positive**.

- **Σ_b: −6.17 % ± 0.86 % — −7.2 σ.** Wrong sign, decisively.
- Σ*_b: −0.57 % ± 0.67 % — **−0.8 σ**, consistent with **no ordering at all**,
  where the mechanism predicts one.

### The structural detail that sharpens it

**The particle counts are isospin-symmetric** — 16,484 / 16,510 / 16,640, a
0.9 % spread. **The entire asymmetry lives on the ANTIparticle side**, where
ūūb̄ (11,232) is ~13 % above ūd̄b̄ (9,932) and d̄d̄b̄ (9,958).

> That is the opposite of what valence feeding does. A proton remnant carries
> **uud**, so it can enhance **uub** production — the particle side. It has no
> anti-valence content, so it has no route to enhance **ūūb̄** specifically.
> **The observed enhancement is on the side the mechanism cannot reach, and
> absent on the side it should act.**

**What this does and does not establish.** It **refutes this mechanism** as the
explanation. It does **not** by itself prove machinery: absence of a predicted
ordering is not presence of a bug. That is what Task 2 measures.

---

## 2. TASK 2 — PRE-REGISTRATION (written before either measurement is run)

Two complementary measurements, bounded. **No further investigation beyond
these two**, per instruction.

### 2.1 Physics side — inclusive raw counts, bypassing the whole analysis chain

A scratch macro counting `heavyPdg` == ±5222 / ±5212 / ±5112 / ±5224 / ±5214 /
±5114 / ±5122 **directly from the raw event records**, with `heavyIsFinal`, in
|η| slices. **No pair construction, no compensation weighting, no decay map, no
extraction reader** — a different quantity measured by a different program.

**Registered predictions:**

| # | if the REMNANT MECHANISM holds | if it does not |
|---|---|---|
| R1 | raw shows the **spin-sorted** pattern (Σ_b ≫ Σ*_b ≫ Λ_b) | — |
| R2 | asymmetry **grows toward forward \|η\|** | flat in \|η\| |
| R3 | raw shows the **uub > udb > ddb** ordering | — |

**Decision rule, registered now:**

| raw result | reading |
|---|---|
| raw reproduces the extraction's pattern **including the reversed ordering** | the extraction faithfully reflects the generator record; **the machinery is exonerated for this observable** and the mechanism is simply wrong |
| raw shows the **predicted** ordering while the extraction shows it reversed | **the extraction distorted it ⇒ MACHINERY. STOP and report.** |
| raw shows **no asymmetry at all** | **the asymmetry is introduced downstream ⇒ MACHINERY. STOP and report.** |

### 2.2 Machinery side — independent projection

Re-project the species axis with a **minimal independent reader** and compare
the b-baryon bins against `extraction/extract_species_decomposition.py`'s weights.

**Run on the same input, which the anchor cannot supply.** The anchor's inputs
are unrecorded (`AnalysisScripts/anchors/extraction_dual/MANIFEST.md`), so the
comparison is run on the **now-promoted merged MONASH central** — a known,
fixed, 1000-input object. Agreement or disagreement there is about the readers,
not about which directories someone used months ago.

**Registered expectation: exact agreement**, bin for bin. Any disagreement is a
machinery finding by itself.

### Verdicts, as instructed

| outcome | action |
|---|---|
| both agree with the extraction | **physics confirmed**; record the mechanism note; **Task 5 numbers final** |
| direct counts disagree with extraction | **MACHINERY — STOP EVERYTHING and report** |
| ambiguous | report both tables, **Task 5 held at provisional**, call goes to the owner |

**Task 1's MISS does not pre-judge this.** It refutes one mechanism; Task 2
measures whether the number itself is trustworthy.

---

## 2b. RESULTS — **VERDICT: PHYSICS CONFIRMED.** And Task 1's MISS is **RETRACTED**

### Task 2.2 — the readers agree EXACTLY

Independent sparse-walk vs the extraction reader, **same input** (merged MONASH
central, 300 pair files, 1000 merged inputs):

| | |
|---|---|
| ordinals | 95 vs 95, **same set** |
| totals | 1,298,655,240 both, **equal** |
| **bins differing (exact comparison)** | **0** |
| b-baryon bins | **all equal**, bin for bin |

**The projection machinery is exonerated.** `THnSparse::Projection()` and an
explicit sparse-cell walk give identical numbers on every ordinal.

### Task 2.1 — the raw record, 400 MONASH files, no analysis chain at all

| # | prediction | result |
|---|---|---|
| **R1** | spin-sorted Σ_b ≫ Σ*_b ≫ ground | **HIT, decisive** |
| **R2** | asymmetry grows toward forward \|η\| | **HIT, decisive** |
| **R3** | uub > ddb ordering | **NULL** — right sign, not resolved |

**R1**, straight from `heavyPdg`:

| group | p | a | ratio | *A* |
|---|---|---|---|---|
| spin-½ Σ_b | 42,146 | 24,316 | 1.733 | **26.83 % ± 0.37** |
| spin-3/2 Σ*_b | 60,067 | 48,789 | 1.231 | **10.36 % ± 0.30** |
| ground (Λ_b, Ξ_b) | 171,674 | 169,166 | 1.015 | **0.74 % ± 0.17** |

**R2** — every species grows monotonically toward the beam:

| species | \|η\|<1 | 1–2 | ≥2 |
|---|---|---|---|
| Σ_b⁺ | 18.04 | 21.89 | **31.13** |
| Σ_b⁰ | 20.16 | 22.31 | **30.40** |
| Σ_b⁻ | 18.34 | 19.59 | **30.78** |
| Σ*_b⁰ | 4.28 | 7.56 | **13.83** |
| Λ_b⁰ | 0.43 | 0.43 | 1.09 |

> **R2 is the beam-remnant signature, and it is unambiguous.** Beam-remnant
> effects grow toward the beam; the asymmetry roughly **doubles** from central
> to forward for every Σ_b state. **This is what the mechanism predicts and it
> is present in the generator record itself.**

**R3** at 400 files: Σ_b **+0.65 % ± 0.92 %** (+0.7 σ), Σ*_b +1.44 % ± 0.74 %
(+1.9 σ). **Right sign, not significant** — the ordering is a small effect on
top of a large one, and 400 files does not resolve it.

### The verdict

**The raw record shows the same spin-sorted asymmetry, at the same magnitudes,
as the extraction reports** (raw 26.8 / 10.4 / 0.74 % against the merged
extraction's ~23 / ~10 / ~0.6 %). Two readers agree exactly. **The asymmetry is
real in PYTHIA's output and the machinery transmits it faithfully.**

**⇒ Physics confirmed. Task 5's numbers may be recorded as final.**

### ⚠ Task 1's MISS is RETRACTED — it was an ANCHOR defect

The discriminating statistic, on three datasets:

| dataset | A(uub) − A(ddb) | |
|---|---|---|
| **anchor** (unknown provenance, 91 ordinals) | **−6.17 % ± 0.84 %** | −7.4 σ, **MISS** |
| **merged MONASH central** (1000 inputs, both readers) | **+1.35 % ± 0.27 %** | **+5.1 σ, HIT** |
| **raw counts** (400 files, no chain) | +0.65 % ± 0.92 % | +0.7 σ, same sign |

**The anchor disagrees with the merged central at 8.6 σ**, and the disagreement
localises to **one bin**: scaling anchor→merged is 9.76–10.33 for five of the
six Σ_b bins and **9.06 for Σ̄_b⁻ alone**. With the anchor at almost exactly
1/10 of the merged total (**scale factor 9.999**), that bin sits **~10 σ high**.

> **Task 1 was computed on the only dataset in the project with no recorded
> provenance, and it is the dataset that disagrees.** The two datasets that can
> be traced — the merged central and the raw event record — both give the
> predicted sign. **The MISS is withdrawn. It is left in §1 because the error is
> the lesson: an unprovenanced anchor produced a 7.4 σ result that better data
> contradicts.**

### The anchor's AGGREGATES are nonetheless sound

Recomputed on the merged central, the headline numbers barely move:

| quantity | anchor | merged central | Δ |
|---|---|---|---|
| second-branch (C) | 12.8451 % | **12.8396 %** | 0.006 pp |
| second-branch (A) | 12.8400 % | 12.8341 % | 0.006 pp |
| map-v2 D⁰ | 25.2425 % | **25.2435 %** | 0.001 pp |
| map-v2 D̄⁰ | 25.1718 % | 25.1707 % | 0.001 pp |

**Nothing published from the anchor needs revision.** The defect is confined to
a low-weight b-baryon bin (~0.06 % of total weight) that no published number
depends on. **But the anchor should not be used for anything charge-resolved
again**, and Task 5's fresh extraction supersedes it regardless.

---

## 3. WHY BOTH MEASUREMENTS MUST BE HARVESTED BEFORE THE CHECKOUT ADVANCE

Any Condor jobs launched for §2.1 **pin commit `43e35be`**. The freeze protocol
and `make can-advance` both key on in-flight jobs, so the advance in Task 3
cannot proceed until these are harvested. **Launch early, harvest before the
advance.**

---

## 4. ADDENDUM — the same measurement at 800 files (8 of 10 blocks)

Six more blocks landed after §2b was written. **The verdict does not change; the
numbers tighten.** Raw counts, `AnalysisScripts/anchors/sigmab_raw/`:

| group | p | a | *A* (400 files) | ***A* (800 files)** |
|---|---|---|---|---|
| spin-½ Σ_b | 84,201 | 48,705 | 26.83 ± 0.37 | **26.71 % ± 0.26** |
| spin-3/2 Σ*_b | 120,248 | 97,156 | 10.36 ± 0.30 | **10.62 % ± 0.21** |
| ground | 343,694 | 338,034 | 0.74 ± 0.17 | **0.83 % ± 0.12** |

**R1 stands, more sharply.** The three-tier separation is now ~100 σ between
tiers.

**R3 moves for Σ*_b:** A(uub) − A(ddb) = **+1.60 % ± 0.52 % (+3.1 σ) — HIT**.
Σ_b remains null (+0.24 % ± 0.65 %, +0.4 σ).

> **So the valence ordering is now positively detected in the spin-3/2 states**,
> in the predicted direction, in raw counts, with no analysis chain involved.
> **Σ_b — the state where the ANCHOR claimed a −7.4 σ reversal — shows no
> ordering at all in 800 raw files.** That is a third independent dataset
> declining to reproduce the anchor's result.

### FINAL — all ten blocks, 1000 MONASH files

| group | p | a | ratio | ***A*** |
|---|---|---|---|---|
| spin-½ Σ_b | 105,089 | 60,943 | 1.724 | **26.59 % ± 0.24** |
| spin-3/2 Σ*_b | 150,309 | 121,723 | 1.235 | **10.51 % ± 0.19** |
| ground | 429,761 | 422,682 | 1.017 | **0.83 % ± 0.11** |

**R1: HIT.** **R3: Σ*_b +1.47 % ± 0.47 (+3.2 σ) HIT**; Σ_b +0.52 % ± 0.58
(+0.9 σ) null — three datasets now decline to reproduce the anchor's −7.4 σ.

**R2, full statistics** — |η|<1 → 1–2 → ≥2:

| species | <1 | 1–2 | ≥2 |
|---|---|---|---|
| Σ_b⁺ | 18.68 ± 1.01 | 21.44 ± 0.92 | **30.67 ± 0.51** |
| Σ_b⁰ | 19.86 ± 1.01 | 20.51 ± 0.92 | **30.62 ± 0.51** |
| Σ_b⁻ | 18.83 ± 1.02 | 20.60 ± 0.93 | **30.10 ± 0.52** |
| Σ*_b⁰ | 6.93 ± 0.79 | 7.58 ± 0.72 | **13.16 ± 0.42** |
| Λ_b⁰ | 0.83 ± 0.29 | 0.37 ± 0.27 | 0.86 ± 0.16 |

**Every state that carries an asymmetry grows toward the beam, by ~1.6×.**
Λ_b⁰ is the exception and it is the expected one: with *A* = 0.83 % overall
there is essentially nothing to grow, and its three slices agree within ~2 σ.
**R2 holds where it is testable.**

**This is the final table for the raw-count leg.** The ten block logs are
committed under `AnalysisScripts/anchors/sigmab_raw/`.
