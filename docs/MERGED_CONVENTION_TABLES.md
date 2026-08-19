# The convention tables, rebuilt from MERGED weights

> # ⚠ SUPERSEDED 2026-08-13 — every absolute and cross-sector number below is inflated
>
> **`docs/ERROR_RECORD.md` E5.** The trigger-owned flavour closure was written
> into every pair file sharing that trigger, and the extractor summed all 300
> files. **Each charm trigger was counted 24 times, each beauty trigger 26.**
> The total below is **24.2004× too large**, and because the two sectors
> replicate unequally the error **does not cancel in any cross-sector share**.
>
> | | published below | corrected |
> |---|---|---|
> | total | 1,298,655,240 | **53,662,414 … 53,662,828** |
> | kCentralGround | 52.3388 % | **52.4958 %** (+0.1570 pp) |
> | kExcludedVector | 46.6510 % | **46.4946 %** (−0.1563 pp) |
> | kExcludedExcited | 1.0102 % | **1.0095 %** (−0.0007 pp) |
> | charm : beauty | 89.2404 : 10.7596 | **89.9852 : 10.0148** (±0.7448 pp) |
>
> **What is unaffected: RATIOS taken within one sector.** The replication
> factor is common to a sector and cancels exactly — verified, ratio-of-ratios
> = 1.000000 for D⁰/D⁺, D̄⁰/D⁻, Λ_c⁺/D⁰, B⁺/B⁰, Λ_b⁰/B⁰, B⁻/B̄⁰.
>
> **What IS affected: every absolute weight, and every share of the grand
> total — including the experiment-comparable tables in §2 and §3**, whose
> rows are shares of a charm+beauty total and therefore cross-sector.
> Measured on the map-v2 (split) table:
>
> | observable | published | corrected | Δ pp |
> |---|---|---|---|
> | D⁰ | 25.2435 | **25.4542** | +0.2107 |
> | D⁺ | 13.1408 | **13.2505** | +0.1097 |
> | D_s⁺ | 4.2366 | **4.2720** | +0.0354 |
> | B⁺ | 2.3035 | **2.1440** | **−0.1595** |
> | B⁰ | 2.3012 | **2.1419** | **−0.1593** |
>
> Charm rows move up and beauty rows down, by the 26/24 ratio — the beauty
> sector was over-weighted relative to charm by 8.3 %.
>
> Corrected artifact: `anchors/merged_monash_central/per_category_deduplicated.csv`,
> regenerable with `tools/reconstruct_deduplicated_decomposition.py`.
> **A live re-extraction against the merged product is still outstanding**
> (`STATE.md` pending).

**These supersede every table derived from the quarantined anchor extraction.**
After this document, **no published number traces to the anchor**.

| | |
|---|---|
| weights | `AnalysisScripts/anchors/merged_monash_central/per_species.csv` (sha256 `74ecfb6ee659e737…`) |
| source | merged MONASH central, **1000 inputs**, 300 pair files, promoted by the v3 merge |
| total | **1,298,655,240** |
| tune | **MONASH only** — the three-tune table is Task 4 and needs the other two tunes' merges |

Why the rebuild: `docs/ERROR_RECORD.md` **E4**. The anchor is bin-inconsistent
with its parent across the baryon sector — 30 of 88 bins at |z| > 4, 16 above
2 % and up to 33 %. **Its aggregates were sound, which is precisely why this
needed doing deliberately rather than being assumed safe.**
*(2026-08-13: "30 of 88" is the retired binomial null. The robust null flags
0 of 88 on the same comparison — a blind spot for broad defects, not a
clearance. §5's annotation carries the measurement; the quarantine stands.)*

---

## 1. STRUCTURAL (diquark-structure) — the primary convention

| category | weight | share % | anchor share % | Δ pp |
|---|---|---|---|---|
| kCentralGround | 679,701,042 | **52.3388** | 52.3308 | +0.008 |
| kExcludedVector | 605,835,226 | **46.6510** | 46.6572 | −0.006 |
| kExcludedExcited | 13,118,780 | **1.0102** | 1.0120 | −0.002 |
| kMultiplyHeavy | 192 | 0.0000 | 0.0000 | — |

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

**This convention never consults the decay map**, so it was never exposed to the
conjugation defect either. **Unchanged to 0.008 pp.**

## 2. EXPERIMENT-COMPARABLE, map v1.1 (`dd502a10c5932fff…`)

> **⚠ This table is a SELECTION, not a partition.** These species do not sum to
> 100 % and are not meant to: each row is an observable a detector reconstructs,
> and the rows are the largest of them, not a complete decomposition. The
> diquark-structure table **is** a partition and does sum to 100 %.

| observable | weight | share % | anchor share % | Δ pp |
|---|---|---|---|---|
| **D⁰** | 365,313,576 | **28.1301** | 28.1326 | −0.003 |
| **D̄⁰** | 364,229,448 | **28.0467** | 28.0536 | −0.007 |
| D⁺ | 133,165,248 | 10.2541 | 10.2640 | −0.010 |
| D⁻ | 132,942,888 | 10.2370 | 10.2477 | −0.011 |
| D_s⁺ | 55,018,752 | 4.2366 | 4.2277 | +0.009 |
| D_s⁻ | 54,972,744 | 4.2331 | 4.2232 | +0.010 |
| B⁺ | 29,914,300 | 2.3035 | — | — |
| B⁰ | 29,884,660 | 2.3012 | 2.2994 | +0.002 |

## 3. EXPERIMENT-COMPARABLE, map v2 (`c9593c9c0a7c4ec2…`) — CURRENT

> **⚠ This table is a SELECTION, not a partition.** These species do not sum to
> 100 % and are not meant to: each row is an observable a detector reconstructs,
> and the rows are the largest of them, not a complete decomposition. The
> diquark-structure table **is** a partition and does sum to 100 %.

| observable | weight | share % | anchor share % | Δ pp |
|---|---|---|---|---|
| **D⁰** | 327,825,702.5 | **25.2435** | 25.2425 | +0.001 |
| **D̄⁰** | 326,880,505.8 | **25.1707** | 25.1718 | −0.001 |
| **D⁺** | 170,653,121.5 | **13.1408** | 13.1541 | −0.013 |
| **D⁻** | 170,291,830.2 | **13.1129** | 13.1295 | −0.017 |
| D_s⁺ | 55,018,752 | 4.2366 | 4.2277 | +0.009 |
| D_s⁻ | 54,972,744 | 4.2331 | 4.2232 | +0.010 |

**Invariance CONSERVED** on every table.

## 4. THE SECOND-BRANCH NUMBER

| | anchor | **merged** | Δ pp |
|---|---|---|---|
| (A) single-hop | 12.8400 % | **12.8341 %** | 0.006 |
| **(C) chained** | 12.8451 % | **12.8396 %** | **0.006** |
| (B) exposed | 35.7910 % | 35.7708 % | 0.020 |

---

## 5. WHAT MOVED, AND WHAT THAT CONFIRMS

**Nothing headline moved.** Every meson-dominated share shifts by **≤ 0.017 pp**,
and the largest published figures — D⁰ at 25.24 %, the 12.84 % second-branch
bound, the structural 52.34 / 46.65 split — are **unchanged to three decimal
places**.

> **That is the expected result and it is worth stating plainly, because it is
> the same fact that made the anchor defect invisible for a generation.** The
> affected sector carries ~2 % of total weight against charm mesons' ~90 %, so
> aggregate agreement was never evidence that the bins agreed. **E4's lesson,
> now demonstrated from the other side: the aggregates really were fine, and
> the bins really were not.**

**The bin-level record of exactly what differs** is
`extraction/compare_subset_parent.py` on anchor vs this parent — **30 of 88 bins at
|z| > 4**, reproduced as a pinned regression test in
`tests/test_compare_subset_parent.py`. That is the audit trail for what the
anchor got wrong, kept as a test rather than as prose.

> **ANNOTATED 2026-08-13 — recalibrated null; "30 of 88" is NOT rewritten.**
> That count is the binomial null, retired for pair counts on 2026-08-13. The
> same comparison under the robust null (median-centred, MAD-scaled σ) flags
> **0 of 88**, at a measured width of **σ̂ = 4.399** binomial sigmas with the
> largest bin at **|z| = 2.83**. **The anchor quarantine STANDS**: a robust width
> estimated from the sample absorbs a *broad* defect, and 30 of 88 bins displaced
> together is exactly that, so the zero measures the instrument's blind spot
> rather than the anchor's health. The verdict rests on the localized, physically
> large deviations — 16 bins above 2 %, up to 33 % — which are unchanged. Both
> counts are pinned, by name, as checks 1 and 4 of the same regression test.

## 6. STATUS

- **MONASH only.** The three-tune table with block SEMs is the resubmission's
  central number and is **not this document** — see the per-tune pre-registration.
- **No SEMs here.** These are pooled single-directory tables; SEMs require the
  ten blocks.
- **The anchor is now cited nowhere for a number**, only as history and as the
  regression fixture.
