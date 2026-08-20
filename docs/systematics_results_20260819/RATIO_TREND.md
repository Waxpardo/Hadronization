# The Λ_b/B⁻ ratio against multiplicity — the trend, per tune

**2026-08-19.** The paper's central claim is a **trend**: the baryon-to-meson
balancing-yield ratio rises with multiplicity under colour reconnection and does
not under MONASH. This document quantifies that rise on the **sealed nominal
alone**. It quotes no systematic, and it is therefore not yet a verdict.

## Why a trend needs its own numbers

A set of per-class differences between tunes says the tunes differ somewhere.
It does not establish that one rises and the other does not. Two estimators
answer the trend question, and the model-free one leads.

| estimator | what it assumes |
|---|---|
| **R(c11) − R(c1)** | nothing. Two rows, subtracted, SEMs in quadrature. |
| weighted straight line in class index | that a line is a fair summary. The χ²/ndf below says how fair. |

**`c1` is the LOWEST multiplicity, N_ch 0 to 2. `c11` is the highest, N_ch 32
and above.** The window label is a top percentile and runs the other way.

**The x-axis of the fit is the class INDEX, and that is a convention.** The
classes are not equally spaced in N_ch: `c1` spans three units and `c11` is
open-ended. A slope "per class" summarises a monotone trend; it is not a
physical d(ratio)/dN_ch. This is why the endpoint contrast leads.

**Correlation is stated, not assumed.** Within one tune the classes are disjoint
sets of events. If the ten-block resampling correlates them positively, then
Var(A−B) is smaller than the quadrature sum, so the uncertainties here are
conservative in that direction.

**The ratio's uncertainty is the plotter's `ratio_sem`**, formed inside each
block, because Λ_b and B⁻ share their triggers and their events.

## The Λ_b/B⁻ ratio against multiplicity, per tune

| class | MONASH | JUNCTIONS | CLOSEPACKING | JUN/MON | CLP/MON |
|---|---|---|---|---|---|
| `c1` | 0.186451 ± 0.006920 | 0.214080 ± 0.008725 | 0.216245 ± 0.007655 | 1.148 | 1.160 |
| `c2` | 0.177535 ± 0.007590 | 0.240068 ± 0.010513 | 0.204493 ± 0.009714 | 1.352 | 1.152 |
| `c3` | 0.169802 ± 0.005273 | 0.249810 ± 0.006425 | 0.230538 ± 0.005964 | 1.471 | 1.358 |
| `c4` | 0.173569 ± 0.006484 | 0.267566 ± 0.010002 | 0.258883 ± 0.009001 | 1.542 | 1.492 |
| `c5` | 0.165131 ± 0.005391 | 0.297046 ± 0.008094 | 0.296111 ± 0.004450 | 1.799 | 1.793 |
| `c6` | 0.160577 ± 0.004228 | 0.331604 ± 0.007312 | 0.322318 ± 0.007445 | 2.065 | 2.007 |
| `c7` | 0.168112 ± 0.002627 | 0.377097 ± 0.006948 | 0.351141 ± 0.008278 | 2.243 | 2.089 |
| `c8` | 0.171720 ± 0.002519 | 0.403773 ± 0.004986 | 0.399497 ± 0.007843 | 2.351 | 2.326 |
| `c9` | 0.167119 ± 0.001950 | 0.464594 ± 0.010061 | 0.443807 ± 0.007115 | 2.780 | 2.656 |
| `c10` | 0.165195 ± 0.001057 | 0.511575 ± 0.006548 | 0.486527 ± 0.006146 | 3.097 | 2.945 |
| `c11` | 0.161922 ± 0.002581 | 0.543170 ± 0.005904 | 0.503435 ± 0.011286 | 3.355 | 3.109 |

### The model-free trend: R(c11) − R(c1)

| tune | contrast | stat. σ |
|---|---|---|
| MONASH | -0.02453 ± 0.00739 | 3.3 |
| JUNCTIONS | +0.32909 ± 0.01053 | 31.2 |
| CLOSEPACKING | +0.28719 ± 0.01364 | 21.1 |

### The weighted straight line in class index

| tune | slope per class | intercept | χ²/ndf |
|---|---|---|---|
| MONASH | -0.001210 ± 0.000369 | 0.17720 | 12.7/9 = 1.41 |
| JUNCTIONS | +0.034804 ± 0.000709 | 0.14349 | 73.6/9 = 8.18 |
| CLOSEPACKING | +0.032760 ± 0.000741 | 0.14051 | 58.5/9 = 6.49 |

### The trend difference against MONASH

| tune | slope difference | stat. σ | endpoint-contrast difference | stat. σ |
|---|---|---|---|---|
| JUNCTIONS | +0.036014 ± 0.000799 | 45.1 | +0.35362 ± 0.01287 | 27.5 |
| CLOSEPACKING | +0.033970 ± 0.000828 | 41.0 | +0.31172 ± 0.01551 | 20.1 |

## What these numbers say, and what they do not

**MONASH is flat and slightly falling.** Its ratio moves from 0.1865 at `c1` to
0.1619 at `c11`, a contrast of −0.02453 ± 0.00739. That is 3.3 σ from zero, so
MONASH is not perfectly flat; it declines gently.

**Both reconnection tunes rise, and by more than an order of magnitude more.**
JUNCTIONS gains +0.32909 ± 0.01053 across the same span, 31.2 σ. CLOSEPACKING
gains +0.28719 ± 0.01364, 21.1 σ.

**The difference in trend is the claim, and statistically it is not close.**
JUNCTIONS minus MONASH is +0.35362 ± 0.01287 on the endpoint contrast, 27.5 σ,
and +0.036014 ± 0.000799 on the slope, 45.1 σ. CLOSEPACKING gives 20.1 σ and
41.0 σ on the same two.

**A straight line does not describe the reconnection tunes.** χ²/ndf is 8.18 for
JUNCTIONS and 6.49 for CLOSEPACKING against 1.41 for MONASH. The rise is real
and monotone but not linear in class index, so **the slope is a summary and not
a model**. A referee should read the endpoint contrast as the measurement and
the slope as shorthand.

**The enhancement grows monotonically**, from 1.148 at `c1` to 3.355 at `c11`
for JUNCTIONS and from 1.160 to 3.109 for CLOSEPACKING.

## What is missing, and what it would have to be

**The combined systematic does not exist.** `HF_SYS_MUF_UP` and
`HF_SYS_PDF_CTEQ6L1` are still merging, and `extraction/combine_per_class.py`
refuses on five of seven sources.

**The threshold is stated so the next session can check it in one step.** To
erase the JUNCTIONS-minus-MONASH trend, a combined systematic would have to
reach **0.354 in the endpoint contrast** or **0.036 per class in the slope**.
That is the whole of the measured effect, correlated in the direction that
cancels it. For CLOSEPACKING the figures are 0.312 and 0.034.

**No verdict is given here.** The verdict is task 3 and task 4 of the next
brief, and it needs all seven campaigns.
