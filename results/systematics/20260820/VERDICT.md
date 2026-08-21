# The verdict — does the tune separation survive its systematics?

**2026-08-20; corrected 2026-08-21.** All seven variation campaigns are closed, extracted and
combined. This document answers the two questions the systematics programme was
run to answer: whether the tunes separate class by class, and whether the
multiplicity **trend** in the baryon-to-meson ratio differs between them.

> **2026-08-21 derived-SEM correction.** The v1 artifact used only the
> variation SEM in derived systematic deltas. Schema v2 applies the documented
> independent two-SEM rule to every source, including the measured-zero S5
> shift. Central values and one-sigma classifications are unchanged. Four of
> 77 two-sigma classifications change: both single-bundle contrasts, the
> CLOSEPACKING trend difference, and MONASH−JUNCTIONS B⁺−B⁻ at `c5` are now
> below two sigma. The 2026-08-20 run record is historical and is not rewritten;
> this correction supersedes its derived totals.

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

**The short answer.** At the per-cell two-sigma reporting threshold, the
JUNCTIONS trend remains above the threshold and the CLOSEPACKING trend does
not. Both remain provisional because S4 is absent and the tune-dependent
generator-hang selection risk is unbounded. At one sigma, the per-class
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
`SEM(Δ)=sqrt(SEM(variation)^2+SEM(nominal)^2)`, followed by
`max(|Δ|, SEM(Δ))` per source, continuously, and quadrature across sources.
S5 retains its measured zero central shift while its derived delta carries the
nominal SEM against a zero variation SEM. A2/S6 remains excluded.

**The ratio's uncertainty is the plotter's `ratio_sem`**, formed inside each
block. Λ_b and B⁻ share their triggers and their events, so combining the two
yield SEMs would be wrong.

**`c1` is the LOWEST multiplicity class, N_ch 0 to 2. `c11` is the highest,
N_ch 33 and above.** The window label is a top percentile and runs the other way.

## 2. The trend — the paper's central claim

| quantity | value | stat | syst | total | \|value\|/total | verdict |
|---|---|---|---|---|---|---|
| contrast MONASH | −0.02453 | 0.00739 | 0.08063 | 0.08096 | 0.3 | no |
| contrast JUNCTIONS | +0.32909 | 0.01053 | 0.16821 | 0.16854 | 2.0 | **exceeds** |
| contrast CLOSEPACKING | +0.28719 | 0.01364 | 0.15233 | 0.15294 | 1.9 | **exceeds** |
| **trend JUNCTIONS − MONASH** | **+0.35362** | 0.01287 | 0.16082 | 0.16134 | **2.2** | **EXCEEDS** |
| **trend CLOSEPACKING − MONASH** | **+0.31172** | 0.01551 | 0.15589 | 0.15666 | **2.0** | **EXCEEDS** |

The JUNCTIONS trend is 2.1918 sigma under the corrected incomplete budget. The
CLOSEPACKING trend is 1.9898 sigma and therefore does not clear the two-sigma
bar. Neither is a publication conclusion while S4 and the generator-hang bias
remain open.

**The honest framing is that the systematics dominate.** Statistically the trend
difference is a 27.5 σ effect. With the corrected incomplete systematics it is
a 2.19 σ effect. Anyone
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
| S5 | Δ=0; 3.64% SEM floor | Δ=0; 4.98% SEM floor |
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
| `>2σ` | **35/72** | `c7` (five series), `c8` (one) |

The significance climbs monotonically with multiplicity — for MONASH−JUNCTIONS
on the ratio it runs 0.3, 0.6, 0.9, 0.9, 1.6, 1.8, 2.7, 2.9, 3.7, 4.2, 2.9 from
`c1` to `c11`, and 4.8 integrated — so the boundary moves by two classes when the
bar is doubled and the shape of the conclusion does not change.

The JUNCTIONS trend clears two sigma at 2.1918 sigma. CLOSEPACKING does not,
at 1.9898 sigma. This is a per-cell threshold description, not a global
significance claim or a publication conclusion.

## 4. The full tables

Every cell below carries the separation, its statistical error, the combined
systematic computed on the separation itself, the total, and the ratio.

## MONASH − JUNCTIONS


### B+ - Lambda_b

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | -0.00205741 | 0.000957 | 0.00947 | 0.00952 | 0.2 | no |
| `c2` | -0.00582999 | 0.00126 | 0.0131 | 0.0132 | 0.4 | no |
| `c3` | -0.00571163 | 0.000788 | 0.00794 | 0.00798 | 0.7 | no |
| `c4` | -0.00695148 | 0.00104 | 0.0118 | 0.0119 | 0.6 | no |
| `c5` | -0.00977354 | 0.000854 | 0.00916 | 0.0092 | 1.1 | **EXCEEDS** |
| `c6` | -0.0121015 | 0.00072 | 0.00828 | 0.00831 | 1.5 | **EXCEEDS** |
| `c7` | -0.0141186 | 0.000606 | 0.00533 | 0.00537 | 2.6 | **EXCEEDS** |
| `c8` | -0.0152963 | 0.000415 | 0.00666 | 0.00667 | 2.3 | **EXCEEDS** |
| `c9` | -0.0192503 | 0.000773 | 0.00541 | 0.00547 | 3.5 | **EXCEEDS** |
| `c10` | -0.0222765 | 0.000582 | 0.00396 | 0.004 | 5.6 | **EXCEEDS** |
| `c11` | -0.0245309 | 0.000496 | 0.00746 | 0.00748 | 3.3 | **EXCEEDS** |
| `MB` | -0.0171103 | 0.000321 | 0.00342 | 0.00343 | 5.0 | **EXCEEDS** |

### B+ - B-

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | +0.00510079 | 0.00232 | 0.018 | 0.0182 | 0.3 | no |
| `c2` | +0.00479589 | 0.00274 | 0.0314 | 0.0316 | 0.2 | no |
| `c3` | +0.013979 | 0.00143 | 0.0134 | 0.0134 | 1.0 | **EXCEEDS** |
| `c4` | +0.014543 | 0.00214 | 0.0168 | 0.0169 | 0.9 | no |
| `c5` | +0.0182325 | 0.00238 | 0.00887 | 0.00919 | 2.0 | **EXCEEDS** |
| `c6` | +0.0241203 | 0.00162 | 0.0159 | 0.016 | 1.5 | **EXCEEDS** |
| `c7` | +0.0266671 | 0.00103 | 0.00849 | 0.00856 | 3.1 | **EXCEEDS** |
| `c8` | +0.0283802 | 0.000948 | 0.00649 | 0.00656 | 4.3 | **EXCEEDS** |
| `c9` | +0.0331335 | 0.000974 | 0.00705 | 0.00711 | 4.7 | **EXCEEDS** |
| `c10` | +0.0353962 | 0.000804 | 0.00753 | 0.00758 | 4.7 | **EXCEEDS** |
| `c11` | +0.0376732 | 0.000948 | 0.00602 | 0.0061 | 6.2 | **EXCEEDS** |
| `MB` | +0.0289482 | 0.000439 | 0.00446 | 0.00448 | 6.5 | **EXCEEDS** |

### Lambda_b / B-

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | -0.0276282 | 0.0111 | 0.106 | 0.106 | 0.3 | no |
| `c2` | -0.0625332 | 0.013 | 0.104 | 0.105 | 0.6 | no |
| `c3` | -0.080008 | 0.00831 | 0.087 | 0.0874 | 0.9 | no |
| `c4` | -0.093997 | 0.0119 | 0.103 | 0.104 | 0.9 | no |
| `c5` | -0.131915 | 0.00972 | 0.0844 | 0.0849 | 1.6 | **EXCEEDS** |
| `c6` | -0.171027 | 0.00845 | 0.094 | 0.0944 | 1.8 | **EXCEEDS** |
| `c7` | -0.208985 | 0.00743 | 0.078 | 0.0783 | 2.7 | **EXCEEDS** |
| `c8` | -0.232052 | 0.00559 | 0.0789 | 0.079 | 2.9 | **EXCEEDS** |
| `c9` | -0.297475 | 0.0102 | 0.0803 | 0.081 | 3.7 | **EXCEEDS** |
| `c10` | -0.34638 | 0.00663 | 0.0821 | 0.0824 | 4.2 | **EXCEEDS** |
| `c11` | -0.381248 | 0.00644 | 0.13 | 0.13 | 2.9 | **EXCEEDS** |
| `MB` | -0.251378 | 0.00395 | 0.0522 | 0.0524 | 4.8 | **EXCEEDS** |
## MONASH − CLOSEPACKING


### B+ - Lambda_b

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | -0.00175392 | 0.00116 | 0.0123 | 0.0124 | 0.1 | no |
| `c2` | -0.00160209 | 0.00127 | 0.00809 | 0.00818 | 0.2 | no |
| `c3` | -0.00330771 | 0.000866 | 0.00643 | 0.00648 | 0.5 | no |
| `c4` | -0.00543024 | 0.00111 | 0.0121 | 0.0121 | 0.4 | no |
| `c5` | -0.00790472 | 0.000611 | 0.00541 | 0.00544 | 1.5 | **EXCEEDS** |
| `c6` | -0.0104613 | 0.000743 | 0.00754 | 0.00758 | 1.4 | **EXCEEDS** |
| `c7` | -0.0115252 | 0.000654 | 0.00579 | 0.00583 | 2.0 | **EXCEEDS** |
| `c8` | -0.0138308 | 0.000715 | 0.0041 | 0.00416 | 3.3 | **EXCEEDS** |
| `c9` | -0.0167362 | 0.000607 | 0.00552 | 0.00556 | 3.0 | **EXCEEDS** |
| `c10` | -0.0188878 | 0.000338 | 0.0044 | 0.00441 | 4.3 | **EXCEEDS** |
| `c11` | -0.0201329 | 0.000654 | 0.00589 | 0.00592 | 3.4 | **EXCEEDS** |
| `MB` | -0.0138748 | 0.000242 | 0.002 | 0.00202 | 6.9 | **EXCEEDS** |

### B+ - B-

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | +0.00759446 | 0.00227 | 0.015 | 0.0151 | 0.5 | no |
| `c2` | +0.00688288 | 0.00334 | 0.028 | 0.0282 | 0.2 | no |
| `c3` | +0.0159587 | 0.00151 | 0.0165 | 0.0165 | 1.0 | no |
| `c4` | +0.0170383 | 0.00216 | 0.0185 | 0.0187 | 0.9 | no |
| `c5` | +0.0242379 | 0.00205 | 0.0126 | 0.0128 | 1.9 | **EXCEEDS** |
| `c6` | +0.0265182 | 0.00155 | 0.0135 | 0.0135 | 2.0 | **EXCEEDS** |
| `c7` | +0.0274734 | 0.00107 | 0.0113 | 0.0114 | 2.4 | **EXCEEDS** |
| `c8` | +0.0311181 | 0.00089 | 0.00875 | 0.00879 | 3.5 | **EXCEEDS** |
| `c9` | +0.0348956 | 0.000546 | 0.0121 | 0.0121 | 2.9 | **EXCEEDS** |
| `c10` | +0.0381811 | 0.000786 | 0.00847 | 0.00851 | 4.5 | **EXCEEDS** |
| `c11` | +0.0400678 | 0.00114 | 0.00754 | 0.00762 | 5.3 | **EXCEEDS** |
| `MB` | +0.0307549 | 0.000355 | 0.00612 | 0.00613 | 5.0 | **EXCEEDS** |

### Lambda_b / B-

| class | separation | stat | syst | total | |sep|/total | verdict |
|---|---|---|---|---|---|---|
| `c1` | -0.0297932 | 0.0103 | 0.125 | 0.125 | 0.2 | no |
| `c2` | -0.0269575 | 0.0123 | 0.0683 | 0.0694 | 0.4 | no |
| `c3` | -0.0607361 | 0.00796 | 0.0862 | 0.0865 | 0.7 | no |
| `c4` | -0.0853146 | 0.0111 | 0.112 | 0.113 | 0.8 | no |
| `c5` | -0.130981 | 0.00699 | 0.0696 | 0.07 | 1.9 | **EXCEEDS** |
| `c6` | -0.161741 | 0.00856 | 0.0947 | 0.0951 | 1.7 | **EXCEEDS** |
| `c7` | -0.183029 | 0.00868 | 0.0855 | 0.086 | 2.1 | **EXCEEDS** |
| `c8` | -0.227777 | 0.00824 | 0.057 | 0.0576 | 4.0 | **EXCEEDS** |
| `c9` | -0.276688 | 0.00738 | 0.0727 | 0.0731 | 3.8 | **EXCEEDS** |
| `c10` | -0.321332 | 0.00624 | 0.0648 | 0.0651 | 4.9 | **EXCEEDS** |
| `c11` | -0.341513 | 0.0116 | 0.0896 | 0.0903 | 3.8 | **EXCEEDS** |
| `MB` | -0.222377 | 0.00333 | 0.0412 | 0.0414 | 5.4 | **EXCEEDS** |

## The trend: R(c11) − R(c1) of Λ_b/B⁻

| quantity | value | stat | syst | total | |value|/total | verdict |
|---|---|---|---|---|---|---|
| contrast MONASH | -0.02453 | 0.00739 | 0.08063 | 0.08096 | 0.3 | no |
| contrast JUNCTIONS | +0.32909 | 0.01053 | 0.16821 | 0.16854 | 2.0 | **EXCEEDS** |
| contrast CLOSEPACKING | +0.28719 | 0.01364 | 0.15233 | 0.15294 | 1.9 | **EXCEEDS** |
| **trend JUNCTIONS − MONASH** | +0.35362 | 0.01287 | 0.16082 | 0.16134 | **2.2** | **EXCEEDS** |
| **trend CLOSEPACKING − MONASH** | +0.31172 | 0.01551 | 0.15589 | 0.15666 | **2.0** | **EXCEEDS** |
