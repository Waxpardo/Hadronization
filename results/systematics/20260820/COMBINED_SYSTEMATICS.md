# The combined systematic — seven campaigns, four of six sources

**2026-08-20.** Per class, per tune, per series. The first combination this
pipeline has been able to produce: `extraction/combine_per_class.py` refused
until all seven campaigns existed, because pre-registration §9 closes with the
rule that a partial quadrature sum understates.

> ### The title said "all seven sources" and that was wrong — corrected 2026-08-20
>
> **Seven is the campaign count, not the source count.**
> `docs/SYSTEMATICS_PREREGISTRATION.md` registers **six** sources, S1 to S6, and
> the seven `HF_SYS_*` campaigns measure **four** of them: S1a, S1b, S2 and S3.
> S5 is measured by re-projection and contributes an exact zero. S6 is excluded
> from this sum by owner ruling A2. **S4 is registered and is not in this sum**,
> and the old title concealed that by counting campaigns as though they were
> sources.
>
> §9.5's rule is **"listed rather than omitted"**, and it applied to S5 from the
> first version of this document. It applies to S4 in exactly the same way. The
> source inventory below now lists every registered source and its disposition,
> so the sum's coverage is readable without counting campaigns.

## THE SOURCE INVENTORY — all six registered sources and where each one is

| source | what it varies | in this sum? | status |
|---|---|---|---|
| **S1a** | `μ_R` | **yes** | measured, `HF_SYS_MUR_{UP,DOWN}` |
| **S1b** | `μ_F` | **yes** | measured, `HF_SYS_MUF_{UP,DOWN}` |
| **S2** | parton distribution | **yes** | measured, `HF_SYS_PDF_CTEQ6L1` |
| **S3** | `PhaseSpace:pTHatMin` | **yes** | measured, `HF_SYS_PTHAT_{1,4}` |
| **S4** | **event-activity counter window**, `\|η\| < 1` against the stored `\|η\| < 4` | **NO** | **registered; a bounded run is under way, `SYSTEMATICS_HARVEST_RUN_RECORD.md` §25.** The bound lands here when it is collected |
| **S5** | decay-daughter class migration | **yes, as an exact zero** | measured 2026-08-17, structurally zero |
| **S6** | pair-level unresolved origin | **no, by ruling A2** | measured; lives on the `M1…M5` partition and is never summed into a `c1…c11` total |

> **S4 is the one gap in this table, and it is stated rather than left to
> inference.** Every number below is a quadrature sum over four measured sources
> plus a measured zero. It is not a six-source total, and it must not be quoted
> as one until S4's bound is in it.

## The rules, none of them chosen here

| rule | source | what it does |
|---|---|---|
| A1 | owner, 2026-08-18 | each source contributes `max(\|Δ\|, SEM(Δ))`, continuously, no threshold cliff |
| A2 | owner, 2026-08-18 | S6/A2 lives on the `M1…M5` partition and is **never** summed into a `c1…c11` total |
| §9.1 | pre-registration | μ_F and PDF act on the same object: if both are non-negligible, quote the larger and drop the other |
| §2.5 | pre-registration | a two-sided source quotes the arm with the larger `\|Δ\|` |
| §9.5 | measured 2026-08-17 | S5 contributes exactly zero, and is listed rather than omitted |
| §9.5, applied to S4 | 2026-08-20 | S4 is registered, is not yet measured, and is listed rather than omitted — see the source inventory above |

**The 2 SEM flag is presentational.** It marks a cell for the reader and gates
nothing; the arithmetic never branches on resolution.

**The tune-bundle spread is not a systematic and is not here.**

**Machine-readable:** `per_class_combination.json`, and
`per_class_combination.csv` which carries `|Δ|`, `SEM(Δ)` and the contribution
for **every source in every one of the 144 cells** — 720 rows.

## The combined systematic, per class per tune

Per cent of the nominal yield in that cell. Every source contributes `max(|Δ|, SEM(Δ))`, continuously; S5 is a measured zero; A2/S6 is not in this sum; **S4 is not yet in this sum**.


### BEAUTY B^{+} — B-

| class | MON | JUN | CLP |
|---|---|---|---|
| `c1` | 10.1% | 10.7% | 11.4% |
| `c2` | 27.8% | 19.1% | 13.9% |
| `c3` | 12.6% | 6.51% | 11.5% |
| `c4` | 8.97% | 19% | 13.6% |
| `c5` | 7.36% | 10.3% | 13.5% |
| `c6` | 10.2% | 9.1% | 10.1% |
| `c7` | 7.28% | 8.62% | 8.07% |
| `c8` | 5% | 8.2% | 7.71% |
| `c9` | 6.62% | 7.05% | 10.6% |
| `c10` | 4.7% | 8.98% | 8.87% |
| `c11` | 5.5% | 11.8% | 10.3% |
| `MB` | 3.77% | 4.6% | 6.3% |

### BEAUTY B^{+} — Lambda_b

| class | MON | JUN | CLP |
|---|---|---|---|
| `c1` | 34.5% | 23.8% | 41.6% |
| `c2` | 39.8% | 36.8% | 25% |
| `c3` | 18.7% | 24.1% | 27.5% |
| `c4` | 46.2% | 26.6% | 23.4% |
| `c5` | 29.3% | 17% | 11.6% |
| `c6` | 19.9% | 19.4% | 16.3% |
| `c7` | 15.2% | 16.9% | 14.6% |
| `c8` | 12.1% | 15.7% | 9.25% |
| `c9` | 11.5% | 13.1% | 11.3% |
| `c10` | 9.92% | 8.99% | 12.8% |
| `c11` | 13.8% | 11.6% | 12.9% |
| `MB` | 6.49% | 8.41% | 6.18% |

### CHARM D^{+} — D-

| class | MON | JUN | CLP |
|---|---|---|---|
| `c1` | 6.04% | 5.82% | 4.88% |
| `c2` | 6.22% | 8.44% | 9.3% |
| `c3` | 5.84% | 8.05% | 7.84% |
| `c4` | 6.01% | 9.03% | 6.39% |
| `c5` | 3.74% | 9.26% | 8.57% |
| `c6` | 4.75% | 8.42% | 9.32% |
| `c7` | 3.83% | 9.42% | 8.01% |
| `c8` | 3.62% | 8.21% | 8.09% |
| `c9` | 3.13% | 8.34% | 6.45% |
| `c10` | 2.33% | 6.51% | 7.74% |
| `c11` | 2.52% | 7.59% | 8.44% |
| `MB` | 5.11% | 6.15% | 5.52% |

### CHARM D^{+} — Lambda_c(+)-bar

| class | MON | JUN | CLP |
|---|---|---|---|
| `c1` | 10.4% | 8.84% | 6.96% |
| `c2` | 13.9% | 9.31% | 14.8% |
| `c3` | 11.9% | 8% | 7.69% |
| `c4` | 12.6% | 10.3% | 6.16% |
| `c5` | 10.9% | 6.48% | 6.6% |
| `c6` | 6.88% | 6.26% | 8.31% |
| `c7` | 10.6% | 9.27% | 8.46% |
| `c8` | 4.59% | 8.98% | 10.1% |
| `c9` | 7.99% | 10.9% | 8.52% |
| `c10` | 6.66% | 6.61% | 16.3% |
| `c11` | 11.5% | 11.7% | 20.7% |
| `MB` | 5.34% | 9.28% | 8.46% |

## The source breakdown, integrated bin

|Δ| and SEM(Δ) per source, per cent of the nominal. `contribution` is the ruled `max` of the two; a dropped source is section 9.1's μ_F-against-PDF choice.


**B^{+}–B-, MONASH** — combined **3.77%**

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 1.451 | 0.8873 | 1.451 | HF_SYS_MUR_DOWN |
| S1b_muf | 2.065 | 0.6393 | 2.065 | HF_SYS_MUF_DOWN |
| S2_pdf | 0.09852 | 0.5089 | 0.5089 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 2.754 | 0.618 | 2.754 | HF_SYS_PTHAT_4 |
| S5_class_migration | 0 | 0 | 0 | — |

**B^{+}–B-, JUNCTIONS** — combined **4.6%**, dropped S2_pdf

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 1.307 | 1.01 | 1.307 | HF_SYS_MUR_UP |
| S1b_muf | 1.262 | 1.121 | 1.262 | HF_SYS_MUF_DOWN |
| S2_pdf | 1.169 | 0.7735 | 1.169 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 4.23 | 0.6414 | 4.23 | HF_SYS_PTHAT_4 |
| S5_class_migration | 0 | 0 | 0 | — |

**B^{+}–B-, CLOSEPACKING** — combined **6.3%**, dropped S2_pdf

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 0.9707 | 1.466 | 1.466 | HF_SYS_MUR_DOWN |
| S1b_muf | 3.318 | 1.179 | 3.318 | HF_SYS_MUF_DOWN |
| S2_pdf | 0.3064 | 0.6154 | 0.6154 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 5.152 | 0.6914 | 5.152 | HF_SYS_PTHAT_4 |
| S5_class_migration | 0 | 0 | 0 | — |

**B^{+}–Lambda_b, MONASH** — combined **6.49%**, dropped S1b_muf

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 2.326 | 1.248 | 2.326 | HF_SYS_MUR_UP |
| S1b_muf | 3.644 | 1.741 | 3.644 | HF_SYS_MUF_UP |
| S2_pdf | 4.343 | 1.663 | 4.343 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 4.231 | 1.95 | 4.231 | HF_SYS_PTHAT_4 |
| S5_class_migration | 0 | 0 | 0 | — |

**B^{+}–Lambda_b, JUNCTIONS** — combined **8.41%**, dropped S2_pdf

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 2.988 | 1.937 | 2.988 | HF_SYS_MUR_UP |
| S1b_muf | 6.86 | 1.361 | 6.86 | HF_SYS_MUF_DOWN |
| S2_pdf | 6.189 | 1.49 | 6.189 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 3.834 | 1.668 | 3.834 | HF_SYS_PTHAT_1 |
| S5_class_migration | 0 | 0 | 0 | — |

**B^{+}–Lambda_b, CLOSEPACKING** — combined **6.18%**, dropped S1b_muf

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 2.24 | 1.032 | 2.24 | HF_SYS_MUR_DOWN |
| S1b_muf | 3.644 | 1.958 | 3.644 | HF_SYS_MUF_DOWN |
| S2_pdf | 5.264 | 3.043 | 5.264 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 1.701 | 2.336 | 2.336 | HF_SYS_PTHAT_1 |
| S5_class_migration | 0 | 0 | 0 | — |

**D^{+}–D-, MONASH** — combined **5.11%**, dropped S2_pdf

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 0.1266 | 0.2139 | 0.2139 | HF_SYS_MUR_DOWN |
| S1b_muf | 1.193 | 0.1665 | 1.193 | HF_SYS_MUF_DOWN |
| S2_pdf | 0.5133 | 0.1673 | 0.5133 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 4.963 | 0.1849 | 4.963 | HF_SYS_PTHAT_4 |
| S5_class_migration | 0 | 0 | 0 | — |

**D^{+}–D-, JUNCTIONS** — combined **6.15%**, dropped S2_pdf

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 0.2436 | 0.1879 | 0.2436 | HF_SYS_MUR_DOWN |
| S1b_muf | 1.436 | 0.2459 | 1.436 | HF_SYS_MUF_DOWN |
| S2_pdf | 0.1726 | 0.2745 | 0.2745 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 5.976 | 0.286 | 5.976 | HF_SYS_PTHAT_4 |
| S5_class_migration | 0 | 0 | 0 | — |

**D^{+}–D-, CLOSEPACKING** — combined **5.52%**, dropped S2_pdf

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 0.5962 | 0.138 | 0.5962 | HF_SYS_MUR_DOWN |
| S1b_muf | 1.503 | 0.1319 | 1.503 | HF_SYS_MUF_DOWN |
| S2_pdf | 0.3728 | 0.2446 | 0.3728 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 5.276 | 0.2438 | 5.276 | HF_SYS_PTHAT_4 |
| S5_class_migration | 0 | 0 | 0 | — |

**D^{+}–Lambda_c(+)-bar, MONASH** — combined **5.34%**, dropped S1b_muf

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 0.5012 | 0.9638 | 0.9638 | HF_SYS_MUR_UP |
| S1b_muf | 1.042 | 0.5882 | 1.042 | HF_SYS_MUF_UP |
| S2_pdf | 1.43 | 0.6359 | 1.43 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 5.058 | 0.9704 | 5.058 | HF_SYS_PTHAT_4 |
| S5_class_migration | 0 | 0 | 0 | — |

**D^{+}–Lambda_c(+)-bar, JUNCTIONS** — combined **9.28%**, dropped S2_pdf

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 1.289 | 0.6724 | 1.289 | HF_SYS_MUR_UP |
| S1b_muf | 6.59 | 0.5851 | 6.59 | HF_SYS_MUF_DOWN |
| S2_pdf | 1.794 | 0.7216 | 1.794 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 6.4 | 0.864 | 6.4 | HF_SYS_PTHAT_1 |
| S5_class_migration | 0 | 0 | 0 | — |

**D^{+}–Lambda_c(+)-bar, CLOSEPACKING** — combined **8.46%**, dropped S2_pdf

| source | \|Δ\| | SEM(Δ) | contribution | arm |
|---|---|---|---|---|
| S1a_mur | 0.9683 | 0.5958 | 0.9683 | HF_SYS_MUR_DOWN |
| S1b_muf | 6.21 | 0.6656 | 6.21 | HF_SYS_MUF_DOWN |
| S2_pdf | 1.445 | 0.7401 | 1.445 | HF_SYS_PDF_CTEQ6L1 |
| S3_pthat | 5.662 | 0.6844 | 5.662 | HF_SYS_PTHAT_4 |
| S5_class_migration | 0 | 0 | 0 | — |
