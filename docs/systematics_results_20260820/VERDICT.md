# The verdict — does the tune separation survive its systematics?

**2026-08-20.** All seven variation campaigns are closed, extracted and
combined. This document answers the two questions the systematics programme was
run to answer: whether the tunes separate class by class, and whether the
multiplicity **trend** in the baryon-to-meson ratio differs between them.

> ### ⚠ ONE REGISTERED SOURCE IS NOT IN THIS BUDGET — S4
>
> **Seven campaigns is not six sources.**
> `docs/SYSTEMATICS_PREREGISTRATION.md` registers six sources, S1 to S6. The
> seven `HF_SYS_*` campaigns measure four of them; S5 is a measured exact zero;
> S6 is excluded by owner ruling A2 because it lives on a different class
> partition. **S4, the event-activity counter window, is registered and is not
> in any number below.**
>
> §9.5's rule is *"listed rather than omitted"*. It governed S5's zero from the
> start and it governs S4 now, so S4 is named here rather than left to a reader
> to notice. **A bounded S4 run is under way** —
> `SYSTEMATICS_HARVEST_RUN_RECORD.md` §25 declares its subset in advance and
> §25.2 gives the argument that a 10 % subset bounds rather than estimates.
>
> **What this means for the verdict as it stands.** The totals below are
> quadrature sums over four measured sources plus a measured zero. The trend
> difference clears its total by a factor of about two. A sixth source enters in
> quadrature, so it can only enlarge the total and can only reduce that factor.
> **The verdict is therefore provisional against S4 and is not restated as final
> until S4's bound is folded in.**

**The short answer.** The trend claim **holds**, for both reconnection tunes,
but at a far smaller margin than the statistics alone suggest. Per class, the
separation is established from `c5` upward and is not established in the four
lowest-multiplicity classes.

## 1. How the systematic on a *difference* is computed

**It is not borrowed from one tune, and it is not propagated.** A variation
moves MONASH and JUNCTIONS in the same direction, so part of it cancels in their
difference. Taking one tune's per-class systematic and applying it to the
difference would double-count what cancels.

For every source, the quantity is **recomputed from that source's own render**
and differenced against the nominal:

```
Delta_source = Q(variation) - Q(nominal)
```

Whatever cancels inside `Q` has already cancelled before the combination sees
it, because `Q` is one number computed twice. Then ruling A1's
`max(|Δ|, SEM(Δ))` per source, continuously, and quadrature across sources with
S5 a measured zero and A2/S6 excluded.

**The ratio's uncertainty is the plotter's `ratio_sem`**, formed inside each
block. Λ_b and B⁻ share their triggers and their events, so combining the two
yield SEMs would be wrong.

**`c1` is the LOWEST multiplicity class, N_ch 0 to 2. `c11` is the highest,
N_ch 33 and above.** The window label is a top percentile and runs the other way.

## 2. The trend — the paper's central claim

| quantity | value | stat | syst | total | \|value\|/total | verdict |
|---|---|---|---|---|---|---|
| contrast MONASH | −0.02453 | 0.00739 | 0.07621 | 0.07657 | 0.3 | no |
| contrast JUNCTIONS | +0.32909 | 0.01053 | 0.15987 | 0.16022 | 2.1 | **exceeds** |
| contrast CLOSEPACKING | +0.28719 | 0.01364 | 0.14003 | 0.14069 | 2.0 | **exceeds** |
| **trend JUNCTIONS − MONASH** | **+0.35362** | 0.01287 | 0.15999 | 0.16051 | **2.2** | **EXCEEDS** |
| **trend CLOSEPACKING − MONASH** | **+0.31172** | 0.01551 | 0.15434 | 0.15512 | **2.0** | **EXCEEDS** |

**THE CLAIM HOLDS, AT ABOUT 2 SIGMA.** The recorded erase threshold was 0.354 —
the whole of the effect. The combined systematic reaches 0.160, which is 45 per
cent of it, so the trend difference survives with roughly a factor of two to
spare.

**The honest framing is that the systematics dominate.** Statistically the trend
difference is a 27.5 σ effect. With systematics it is a 2.2 σ effect. Anyone
quoting the statistical figure alone would overstate the result by an order of
magnitude.

### The strongest form of the result needs no combination at all

**The trend difference is positive in every one of the seven variation renders**,
and no single source brings it near zero:

| campaign | trend JUNCTIONS − MONASH | shift from nominal |
|---|---|---|
| *nominal* | *+0.35362* | — |
| `HF_SYS_MUF_DOWN` | **+0.23269** | −0.12093 (−34.20%) |
| `HF_SYS_MUF_UP` | +0.39090 | +0.03728 (+10.54%) |
| `HF_SYS_PDF_CTEQ6L1` | +0.42153 | +0.06791 (+19.20%) |
| `HF_SYS_PTHAT_1` | +0.40549 | +0.05187 (+14.67%) |
| `HF_SYS_MUR_UP` | +0.44463 | +0.09101 (+25.74%) |

The largest single excursion, `MUF_DOWN`, still leaves the trend at **+0.233**.
A referee who distrusts the quadrature can read this table instead. Neither the
sign nor the order of magnitude of the effect depends on the combination rule.

### What dominates the budget

| source | JUNCTIONS − MONASH | CLOSEPACKING − MONASH |
|---|---|---|
| S1b μ_F | **34.20%** (quoted DOWN) | 25.59% (dropped by §9.1) |
| S1a μ_R | 25.74% | 16.24% (SEM floor) |
| S2 PDF | 19.20% (dropped by §9.1) | **36.03%** |
| S3 pT-hat | 14.67% | 29.83% |
| S5 | 0 (measured) | 0 (measured) |
| **S4** | **not in this budget** | **not in this budget** |

**§9.1 fires in opposite directions for the two tunes**, and that is the rule
working rather than an inconsistency: μ_F and PDF act on the same object, so the
larger is quoted and the other dropped. For JUNCTIONS μ_F is larger; for
CLOSEPACKING the PDF is.

## 3. The per-class verdict

**49 of 72 cells exceed their total uncertainty**, and the boundary is sharp and
consistent:

| pair | observable | cells | classes that exceed |
|---|---|---|---|
| MONASH − JUNCTIONS | B⁺–Λ_b | 8/12 | c5 … c11, MB |
| MONASH − JUNCTIONS | B⁺–B⁻ | 9/12 | c3, c5 … c11, MB |
| MONASH − JUNCTIONS | Λ_b/B⁻ | 8/12 | c5 … c11, MB |
| MONASH − CLOSEPACKING | B⁺–Λ_b | 8/12 | c5 … c11, MB |
| MONASH − CLOSEPACKING | B⁺–B⁻ | 8/12 | c5 … c11, MB |
| MONASH − CLOSEPACKING | Λ_b/B⁻ | 8/12 | c5 … c11, MB |

**THE BOUNDARY FALLS AT `c5` in five of the six series**, and at `c3` in the
sixth. Below it — `c1` to `c4`, N_ch 0 to about 6 — the separation is **not
established**. Above it, and in the multiplicity-integrated bin, it is.

**Two things push the same way at low multiplicity.** The separation itself is
smallest there, and the combined systematic is largest: 23 to 46 per cent in
`c1`–`c4` against 6 to 13 per cent in the integrated bin. The classes where the
physics effect is weakest are also the classes measured worst.

### The bar this table applies, and a stricter one

**"Exceeds its total uncertainty" means `|separation| > total`, which is one
sigma.** That is the question as posed, and it is a weak bar. A reader who wants
two sigma can have it from the same numbers:

| bar | cells | boundary class |
|---|---|---|
| `>1σ` | **49/72** | `c5` (five series), `c3` (one) |
| `>2σ` | **36/72** | `c7` (four series), `c5` (one), `c8` (one) |

The significance climbs monotonically with multiplicity — for MONASH−JUNCTIONS
on the ratio it runs 0.3, 0.6, 0.9, 0.9, 1.6, 1.8, 2.7, 3.0, 3.7, 4.2, 2.9 from
`c1` to `c11`, and 4.8 integrated — so the boundary moves by two classes when the
bar is doubled and the shape of the conclusion does not change.

**The trend clears both bars**, at 2.20 σ for JUNCTIONS and 2.01 σ for
CLOSEPACKING. CLOSEPACKING clears two sigma by 0.01, and this
document does not claim more than that.

## 4. The full tables

Every cell below carries the separation, its statistical error, the combined
systematic computed on the separation itself, the total, and the ratio.

## MONASH − JUNCTIONS


### B+ - Lambda_b

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | -0.00205741 | 0.000957 | 0.00938 | 0.00942 | 0.2 | no |
| `c2` | -0.00582999 | 0.00126 | 0.013 | 0.0131 | 0.4 | no |
| `c3` | -0.00571163 | 0.000788 | 0.0079 | 0.00794 | 0.7 | no |
| `c4` | -0.00695148 | 0.00104 | 0.0118 | 0.0118 | 0.6 | no |
| `c5` | -0.00977354 | 0.000854 | 0.00912 | 0.00916 | 1.1 | **EXCEEDS** |
| `c6` | -0.0121015 | 0.00072 | 0.00822 | 0.00825 | 1.5 | **EXCEEDS** |
| `c7` | -0.0141186 | 0.000606 | 0.0053 | 0.00533 | 2.6 | **EXCEEDS** |
| `c8` | -0.0152963 | 0.000415 | 0.00663 | 0.00665 | 2.3 | **EXCEEDS** |
| `c9` | -0.0192503 | 0.000773 | 0.0053 | 0.00536 | 3.6 | **EXCEEDS** |
| `c10` | -0.0222765 | 0.000582 | 0.00388 | 0.00392 | 5.7 | **EXCEEDS** |
| `c11` | -0.0245309 | 0.000496 | 0.00744 | 0.00746 | 3.3 | **EXCEEDS** |
| `MB` | -0.0171103 | 0.000321 | 0.0034 | 0.00342 | 5.0 | **EXCEEDS** |

### B+ - B-

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | +0.00510079 | 0.00232 | 0.0177 | 0.0179 | 0.3 | no |
| `c2` | +0.00479589 | 0.00274 | 0.0313 | 0.0314 | 0.2 | no |
| `c3` | +0.013979 | 0.00143 | 0.0131 | 0.0132 | 1.1 | **EXCEEDS** |
| `c4` | +0.014543 | 0.00214 | 0.0163 | 0.0165 | 0.9 | no |
| `c5` | +0.0182325 | 0.00238 | 0.00786 | 0.00821 | 2.2 | **EXCEEDS** |
| `c6` | +0.0241203 | 0.00162 | 0.0157 | 0.0158 | 1.5 | **EXCEEDS** |
| `c7` | +0.0266671 | 0.00103 | 0.00824 | 0.0083 | 3.2 | **EXCEEDS** |
| `c8` | +0.0283802 | 0.000948 | 0.00635 | 0.00642 | 4.4 | **EXCEEDS** |
| `c9` | +0.0331335 | 0.000974 | 0.00698 | 0.00705 | 4.7 | **EXCEEDS** |
| `c10` | +0.0353962 | 0.000804 | 0.00749 | 0.00753 | 4.7 | **EXCEEDS** |
| `c11` | +0.0376732 | 0.000948 | 0.00572 | 0.00579 | 6.5 | **EXCEEDS** |
| `MB` | +0.0289482 | 0.000439 | 0.00442 | 0.00444 | 6.5 | **EXCEEDS** |

### Lambda_b / B-

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | -0.0276282 | 0.0111 | 0.105 | 0.106 | 0.3 | no |
| `c2` | -0.0625332 | 0.013 | 0.103 | 0.104 | 0.6 | no |
| `c3` | -0.080008 | 0.00831 | 0.0866 | 0.087 | 0.9 | no |
| `c4` | -0.093997 | 0.0119 | 0.102 | 0.103 | 0.9 | no |
| `c5` | -0.131915 | 0.00972 | 0.0831 | 0.0837 | 1.6 | **EXCEEDS** |
| `c6` | -0.171027 | 0.00845 | 0.0936 | 0.094 | 1.8 | **EXCEEDS** |
| `c7` | -0.208985 | 0.00743 | 0.0776 | 0.078 | 2.7 | **EXCEEDS** |
| `c8` | -0.232052 | 0.00559 | 0.0785 | 0.0787 | 3.0 | **EXCEEDS** |
| `c9` | -0.297475 | 0.0102 | 0.0797 | 0.0803 | 3.7 | **EXCEEDS** |
| `c10` | -0.34638 | 0.00663 | 0.0818 | 0.0821 | 4.2 | **EXCEEDS** |
| `c11` | -0.381248 | 0.00644 | 0.13 | 0.13 | 2.9 | **EXCEEDS** |
| `MB` | -0.251378 | 0.00395 | 0.0521 | 0.0522 | 4.8 | **EXCEEDS** |

## MONASH − CLOSEPACKING


### B+ - Lambda_b

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | -0.00175392 | 0.00116 | 0.0122 | 0.0123 | 0.1 | no |
| `c2` | -0.00160209 | 0.00127 | 0.00778 | 0.00789 | 0.2 | no |
| `c3` | -0.00330771 | 0.000866 | 0.00631 | 0.00637 | 0.5 | no |
| `c4` | -0.00543024 | 0.00111 | 0.012 | 0.0121 | 0.5 | no |
| `c5` | -0.00790472 | 0.000611 | 0.00534 | 0.00537 | 1.5 | **EXCEEDS** |
| `c6` | -0.0104613 | 0.000743 | 0.0075 | 0.00754 | 1.4 | **EXCEEDS** |
| `c7` | -0.0115252 | 0.000654 | 0.00576 | 0.00579 | 2.0 | **EXCEEDS** |
| `c8` | -0.0138308 | 0.000715 | 0.00397 | 0.00404 | 3.4 | **EXCEEDS** |
| `c9` | -0.0167362 | 0.000607 | 0.00549 | 0.00552 | 3.0 | **EXCEEDS** |
| `c10` | -0.0188878 | 0.000338 | 0.00436 | 0.00437 | 4.3 | **EXCEEDS** |
| `c11` | -0.0201329 | 0.000654 | 0.00585 | 0.00589 | 3.4 | **EXCEEDS** |
| `MB` | -0.0138748 | 0.000242 | 0.00199 | 0.002 | 6.9 | **EXCEEDS** |

### B+ - B-

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | +0.00759446 | 0.00227 | 0.0145 | 0.0146 | 0.5 | no |
| `c2` | +0.00688288 | 0.00334 | 0.0277 | 0.0279 | 0.2 | no |
| `c3` | +0.0159587 | 0.00151 | 0.0163 | 0.0164 | 1.0 | no |
| `c4` | +0.0170383 | 0.00216 | 0.0181 | 0.0183 | 0.9 | no |
| `c5` | +0.0242379 | 0.00205 | 0.0122 | 0.0123 | 2.0 | **EXCEEDS** |
| `c6` | +0.0265182 | 0.00155 | 0.0133 | 0.0134 | 2.0 | **EXCEEDS** |
| `c7` | +0.0274734 | 0.00107 | 0.0112 | 0.0112 | 2.4 | **EXCEEDS** |
| `c8` | +0.0311181 | 0.00089 | 0.00861 | 0.00865 | 3.6 | **EXCEEDS** |
| `c9` | +0.0348956 | 0.000546 | 0.012 | 0.0121 | 2.9 | **EXCEEDS** |
| `c10` | +0.0381811 | 0.000786 | 0.0084 | 0.00844 | 4.5 | **EXCEEDS** |
| `c11` | +0.0400678 | 0.00114 | 0.00736 | 0.00745 | 5.4 | **EXCEEDS** |
| `MB` | +0.0307549 | 0.000355 | 0.0061 | 0.00611 | 5.0 | **EXCEEDS** |

### Lambda_b / B-

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | -0.0297932 | 0.0103 | 0.124 | 0.124 | 0.2 | no |
| `c2` | -0.0269575 | 0.0123 | 0.0637 | 0.0649 | 0.4 | no |
| `c3` | -0.0607361 | 0.00796 | 0.0854 | 0.0858 | 0.7 | no |
| `c4` | -0.0853146 | 0.0111 | 0.112 | 0.112 | 0.8 | no |
| `c5` | -0.130981 | 0.00699 | 0.0689 | 0.0693 | 1.9 | **EXCEEDS** |
| `c6` | -0.161741 | 0.00856 | 0.0943 | 0.0947 | 1.7 | **EXCEEDS** |
| `c7` | -0.183029 | 0.00868 | 0.0846 | 0.0851 | 2.2 | **EXCEEDS** |
| `c8` | -0.227777 | 0.00824 | 0.0552 | 0.0558 | 4.1 | **EXCEEDS** |
| `c9` | -0.276688 | 0.00738 | 0.072 | 0.0724 | 3.8 | **EXCEEDS** |
| `c10` | -0.321332 | 0.00624 | 0.0642 | 0.0645 | 5.0 | **EXCEEDS** |
| `c11` | -0.341513 | 0.0116 | 0.0881 | 0.0888 | 3.8 | **EXCEEDS** |
| `MB` | -0.222377 | 0.00333 | 0.0411 | 0.0412 | 5.4 | **EXCEEDS** |

## The trend: R(c11) − R(c1) of Λ_b/B⁻

| quantity | value | stat | syst | total | |value|/total | verdict |
|---|---|---|---|---|---|---|
| contrast MONASH | -0.02453 | 0.00739 | 0.07621 | 0.07657 | 0.3 | no |
| contrast JUNCTIONS | +0.32909 | 0.01053 | 0.15987 | 0.16021 | 2.1 | **EXCEEDS** |
| contrast CLOSEPACKING | +0.28719 | 0.01364 | 0.14003 | 0.14069 | 2.0 | **EXCEEDS** |
| **trend JUNCTIONS − MONASH** | +0.35362 | 0.01287 | 0.15999 | 0.16051 | **2.2** | **EXCEEDS** |
| **trend CLOSEPACKING − MONASH** | +0.31172 | 0.01551 | 0.15434 | 0.15512 | **2.0** | **EXCEEDS** |
