# M7 — the unresolved-origin systematic, measured

> # ⚠ SCOPE — this is an INCLUSIVE-LEVEL diagnostic, NOT a bound on the pair observable
>
> **Relabelled 2026-08-13 (external review finding A2). The measurement is
> sound; the claim attached to it was not.**
>
> `Validation/MeasureUnresolvedSystematic.C` counts **every final open-heavy
> hadron** — its only cut is `heavyIsFinal && q_sector != 0`. It applies
> **none** of the production selection: not direct-primary, not central
> ground-state, not acceptance, not trigger pT, not multiplicity, not pairing,
> not OS−SS. Its "resolved" population is merely `origin != 0`, which includes
> origins that would **not** be accepted as selected-hard triggers.
>
> **What these numbers therefore are:** the inclusive rate of unresolved-origin
> open-heavy hadrons, and the shift in the **inclusive** baryon fraction if
> those hadrons could be recovered. Both are real, both are measured at full
> scale, and both are worth having.
>
> **What they are NOT: a bound on the systematic of the OS−SS pair
> observable.** A global rate cannot bound a multiplicity-localized effect.
> Concretely: if unresolved trigger candidates sit preferentially in the
> highest-multiplicity class and preferentially have same-sign partners, the
> inclusive rate and baryon fraction can stay at the quoted sub-percent level
> while the high-multiplicity OS−SS yield moves substantially. Nothing here
> excludes that.
>
> **➜ THE PAIR-LEVEL MEASUREMENT NOW EXISTS AS A SEPARATE THING, AND IT IS
> MEASURED (2026-08-13).** Pre-registered in
> `docs/A2_PAIR_UNRESOLVED_PREREGISTRATION.md`, run record in
> `docs/A2_PAIR_UNRESOLVED_RUN_RECORD.md`, result and the pre-registration
> scored verbatim in `docs/a2_results_20260813/A2_DELTA_RESULT.md`. It varies
> the duplicate-hard-carrier tie-break (drop-all versus keep-one) and measures
> the OS−SS compensation yield **per multiplicity class**, per tune, with block
> SEMs.
>
> **THE VERDICT — this is the number to quote, and it never comes from this
> document:**
>
> **The shape first, because it is what licenses the rest:** Δ rises **5.9–9.7×**
> across the multiplicity classes, and it does so under **both** tie-break rules
> (`docs/a2_results_20260813/A2_TIEBREAK_ROBUSTNESS.md`). The
> pre-registration named a flat Δ(m) in advance as the outcome that would retire
> A2's concern. It did not occur: **A2's concern is confirmed, not retired**, and
> **an integrated number is wrong about the shape whichever rule is used.**
>
> **The systematic to quote (owner ruling) is the LARGEST-index arm, per class.**
> Per cent, with block SEMs:
>
> | tune | M1 | M2 | M3 | M4 | M5 |
> |---|---|---|---|---|---|
> | MONASH | 0.0004 | 0.0011 | −0.0003 | 0.0017 | 0.0037 — **NEGLIGIBLE** |
> | **JUNCTIONS** | 0.0255 | 0.0691 | 0.1007 | **0.1509** | 0.1369 |
> | **CLOSEPACKING** | 0.0377 | 0.1012 | 0.1571 | 0.1777 | **0.2293** |
>
> **The integrated value must not be substituted for the per-class ones**: it
> understates the worst class by 2.6× (JUNCTIONS) and 2.9× (CLOSEPACKING).
>
> The **smallest-index arm is the cross-check**, not a lower bound. Its job is to
> establish that the magnitude is **rule-dependent** — the two orderings differ by
> **2.0–5.5×** in all ten CR classes, at 2.7–21.6 σ.
>
> **This is not an envelope and must not be called one.** What is quoted is *the
> larger of two extremal orderings of `heavyIndex`*, and **neither bounds the
> space of possible resolutions**: a pT-ordered rule would give a larger Δ than
> either, which is precisely why the pre-registration rejected it as inflating
> the shift by construction.
>
> Everything remains sub-percent — the largest value anywhere is 0.23 %. The
> earlier "nothing exceeds 0.07 %" is **retired**: it held for the pre-registered
> rule only.
>
> ### The exposure comparison, which settles that this document is not a proxy
>
> The A2 campaign measures how many pairs the baseline's tie-break actually
> discards, over 10 M events per tune (2026-08-13):
>
> | | **pair-level** restorations per M events | **inclusive** unresolved rate |
> |---|---|---|
> | MONASH | **6.2** | reference |
> | JUNCTIONS | **1 219.4** | — |
> | CLOSEPACKING | **1 228.7** | — |
> | **CR / MONASH ratio** | **≈ 197×** | **13.6×** (§ below) |
>
> **A restoration count is not Δ**, and must never be quoted as one: it counts
> rows the variation restores, not the shift in the OS−SS observable. But the
> *tune dependence* of the exposure is a like-for-like comparison, and at pair
> level it is more than an order of magnitude larger than the inclusive rate
> ratio this document reports.
>
> **That is direct evidence the inclusive diagnostic was never a proxy for the
> pair-level systematic** — which is what review finding A2 claimed it was. The
> two quantities do not even scale together across tunes.
>
> **The two must never be conflated.** This document is the **inclusive**
> diagnostic. That one is the **pair-level systematic**. If a number is quoted as
> a systematic on the paper's observable, it comes from there, not from here.
>
> **Do not cite this document as the unresolved-origin systematic on the
> observable.** That measurement exists, it is quoted above, and it is quoted
> **per multiplicity class** for the colour-reconnection tunes.
>
> **One number from this page is especially easy to misuse.** The inclusive
> CR/MONASH ratio here is **13.6×**, and it is tempting to read the pair-level
> systematic as "the same, times something". It is not: the pair-level exposure
> ratio is **197×**, and MONASH's pair-level Δ is exactly zero, so the Δ ratio
> is not 13.6, not 197, but **undefined**. The two quantities have different
> scopes, different selections, and no fixed conversion between them.



**The review's "no systematics exist" becomes a number with an uncertainty.**
Measured 2026-08-10 over all **3000 production raw files** (~300 M events,
~276 GB), cluster `5402022`, ten jobs — one per canonical block.

---

## 1. THE TABLE

| tune | unresolved rate % | baryon % (measured) | baryon % (inclusive) | **relative shift %** |
|---|---|---|---|---|
| **MONASH** | 0.0847 ± 0.0003 | 4.6547 ± 0.0013 | 4.6568 ± 0.0013 | **0.0451 ± 0.0008** |
| **JUNCTIONS** | 1.1530 ± 0.0009 | 17.8488 ± 0.0037 | 17.9469 ± 0.0037 | **0.5497 ± 0.0019** |
| **CLOSEPACKING** | 1.1355 ± 0.0008 | 17.2888 ± 0.0038 | 17.3774 ± 0.0036 | **0.5125 ± 0.0024** |

Central values from **pooled counts** over all ten blocks; uncertainties are the
**standard error of the ten per-block values** (`stdev/√10`), the project's
standard machinery.

### The dropped sample, and why it matters

| tune | unresolved n | resolved n | unresolved baryon % | **enrichment** |
|---|---|---|---|---|
| MONASH | 168,003 | 198,163,563 | 7.134 | **1.53×** |
| JUNCTIONS | 2,317,799 | 198,706,525 | 26.358 | **1.48×** |
| CLOSEPACKING | 2,271,517 | 197,779,600 | 25.091 | **1.45×** |

**The dropped sample is baryon-enriched by ~1.5× in every tune** — the enrichment
is remarkably tune-independent (1.45–1.53×), exactly as the macro's header
predicted qualitatively.

---

## 2. WHAT WAS PRE-REGISTERED, AND WHAT IS THE MEASUREMENT

**Structure was pre-registered; values were not.**

- **Pre-registered: CR tunes carry higher unresolved rates than MONASH.**
  **CONFIRMED, and by more than "higher":** 1.15 % and 1.14 % against 0.085 % —
  a factor **13.6×**. Colour reconnection rearranges colour flow, so ancestry is
  ambiguous far more often.
- **The shift's sign and size were the measurement, with no expectation
  stated.** Measured: **positive in every tune** — recovering the dropped
  candidates *raises* the baryon fraction, as a baryon-enriched loss must —
  and **~12× larger in the CR tunes** (0.51 %, 0.55 %) than in MONASH (0.045 %).

### Why the differential is the number that matters

The observable is a **comparison between tunes**. A systematic that shifted all
three equally would largely cancel. This one does not: it moves the CR tunes'
baryon fraction by ~0.5 % relative and MONASH's by ~0.05 %, so **the
tune-to-tune comparison carries a residual of roughly half a percent relative,
in the direction of understating the CR tunes' baryon fractions.**

**It is a bound, not a correction.** The unresolved candidates' origin is
genuinely ambiguous; they cannot be recovered. The inclusive column is what the
answer would be if they could be, which brackets what dropping them costs.

---

## 3. EXCHANGEABILITY — checked, not assumed

The block SEM assumes the ten blocks are exchangeable samples of the same
quantity. **v38's self-review flagged that nobody had checked.** Checked now, by
first-half against second-half:

| tune | quantity | first half | second half | difference | pulls |
|---|---|---|---|---|---|
| CLOSEPACKING | rate | 1.13469 | 1.13625 | +0.00156 | **0.97 σ** |
| CLOSEPACKING | shift | 0.51199 | 0.51292 | +0.00092 | **0.18 σ** |
| JUNCTIONS | rate | 1.15254 | 1.15345 | +0.00091 | **0.50 σ** |
| JUNCTIONS | shift | 0.54776 | 0.55154 | +0.00378 | **1.02 σ** |
| MONASH | rate | 0.08453 | 0.08489 | +0.00036 | **0.59 σ** |
| MONASH | shift | 0.04454 | 0.04570 | +0.00116 | **0.73 σ** |

**All six within ~1 σ. No drift across the campaign; exchangeability holds and
the SEM is doing what it claims.**

Per-block values, so a reader can see the spread rather than trust the summary:

```
CLOSEPACKING rate  1.1378 1.1339 1.1322 1.1328 1.1367 1.1328 1.1345 1.1364 1.1384 1.1391
CLOSEPACKING shift 0.5103 0.5137 0.5118 0.5026 0.5217 0.5254 0.5153 0.5053 0.5152 0.5035
JUNCTIONS    rate  1.1501 1.1524 1.1517 1.1508 1.1576 1.1564 1.1534 1.1490 1.1549 1.1536
JUNCTIONS    shift 0.5488 0.5412 0.5554 0.5458 0.5476 0.5549 0.5480 0.5418 0.5574 0.5556
MONASH       rate  0.0840 0.0856 0.0838 0.0858 0.0835 0.0839 0.0853 0.0842 0.0854 0.0856
MONASH       shift 0.0440 0.0455 0.0404 0.0469 0.0459 0.0419 0.0454 0.0464 0.0486 0.0462
```

---

## 4. THE INTEGER-COUNT DESIGN — ratified, with its rationale

**The block sums are built from exact integers, not from the production macro's
printed percentages**, and that is not fastidiousness.

`Validation/MeasureUnresolvedSystematic.C` prints `unresolved_n` and
`resolved_n` exactly but the baryon splits only as **percentages to two
decimals**. Reconstructing counts as `round(n × pct/100)` loses up to
**±10 candidates per file** at `resolved_n ≈ 2×10⁵` — about **0.1 % of a block
total**, which is **roughly twenty times the MONASH shift being measured
(0.045 %)**. Aggregating printed percentages would have drowned the signal in
print precision.

So the sums use exact integers from a scratch macro that reuses the production
cut strings **verbatim** (`MeasureUnresolvedSystematic.C:55-63`), and the driver
**cross-checks that replication against the production macro itself** on one file
per tune per block — 30 independent checks, **all `XCHECK_OK`**, comparing
`unresolved_n`, `resolved_n` and `measured_baryon_pct` to the production macro's
own print precision. A mismatch aborts the block rather than silently publishing
a different measurement.

---

## 5. LIMITS

- **Charm sector only.** The macro's cuts select `heavyQc != 0`
  (`MeasureUnresolvedSystematic.C:55`). The beauty-sector equivalent is **not
  measured here** and would need the same treatment with `heavyQb`.
- **The inclusive column is a bound, not a correction** — see §2.
- **No kinematic differential.** This is integrated over the full central
  acceptance; whether the unresolved rate varies with pT or multiplicity is
  unmeasured, and a pT-dependent systematic would not be captured by a single
  number.
- **The enrichment's tune-independence (1.45–1.53×) is an observation, not an
  explanation.** Nothing here says why the dropped sample is baryon-enriched by
  the same factor regardless of colour-reconnection setting.

---

## 6. PROVENANCE

- Macro: `Validation/MeasureUnresolvedSystematic.C`, unrun since before the
  review — **this is its first execution at scale**.
- Inputs: all 3000 files under
  `/data/alice/ipardoza/hadronization_production/HF_RUN3_V1/raw/`, grouped by
  the campaign's own `campaigns/HF_RUN3_V1/freeze/block_*.jsonl`.
- Sizing recorded before launch: **3.32 s wall, 284,680 kB maxRSS** on one file
  (**n=1**).
- Aggregation: `extraction/aggregate_m7.py`, fail-closed on fewer than ten blocks.
- Logs retained at `/data/alice/ipardoza/m7_runs/block_*/`.
