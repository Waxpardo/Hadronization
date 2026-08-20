# The last two campaigns — decomposition deltas, and the shape of S1b

**2026-08-20.** `HF_SYS_MUF_UP` (S1b up) and `HF_SYS_PDF_CTEQ6L1` (S2), the two
campaigns whose merges finished on 2026-08-19 and 2026-08-20. With these the
programme has all seven, and the combination is possible for the first time.

## The controls

| control | result |
|---|---|
| closure | 33/33 products and **3/3 markers** each, every leg `errors=0`, 300 central and 3000 block pair files |
| extraction | **33/33 directories `rc=0`** for each campaign |
| instrument | the same reader, artifact, decay map v2 and signed registry the five used |
| preflight | exact filenames from the signed registry, never a glob |

## The per-event plausibility check

The E5 defect showed as about 13 counts per event where the truth is order one.
Exposure is 10 million events per tune.

| campaign | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| `HF_SYS_MUF_UP` | 0.5589 | 0.4759 | 0.4775 |
| `HF_SYS_PDF_CTEQ6L1` | 0.5695 | 0.4898 | 0.4936 |
| *`HF_RUN3_V1` nominal* | *0.5366* | *0.4631* | *0.4668* |
| *range across the five extracted earlier* | *0.4105 – 0.6223* | *0.3496 – 0.5534* | *0.3572 – 0.5458* |

**All six pass.** Every value sits inside the range the five already spanned, and
the worst point is more than twenty times clear of the failure mode.

## S1b — the μ_F pair, and its shape

**This is the largest single systematic in the budget, so its shape matters.**
`MUF_DOWN` (×0.5) was measured on 2026-08-19; `MUF_UP` (×2) is measured here.

| tune | category | DOWN (×0.5) | UP (×2) | signs | \|D\|/\|U\| |
|---|---|---|---|---|---|
| MONASH | kCentralGround | −1.2707 ± 0.0642 | +0.7778 ± 0.0540 | opposite | 1.634 |
| MONASH | kExcludedVector | +1.4540 ± 0.0719 | −0.8936 ± 0.0611 | opposite | 1.627 |
| MONASH | kExcludedExcited | −0.8834 ± 0.3520 | +0.7093 ± 0.3144 | opposite | 1.245 |
| JUNCTIONS | kCentralGround | −2.0139 ± 0.0445 | +1.3775 ± 0.0245 | opposite | 1.462 |
| JUNCTIONS | kExcludedVector | +3.3070 ± 0.0637 | −2.3015 ± 0.0451 | opposite | 1.437 |
| JUNCTIONS | kExcludedExcited | **−7.0113 ± 0.4200** | **+5.1564 ± 0.3069** | opposite | 1.360 |
| JUNCTIONS | kMultiplyHeavy | −50.9630 ± 2.3174 | +56.0742 ± 5.7513 | opposite | 0.909 (LOW-STAT) |
| CLOSEPACKING | kCentralGround | −1.0105 ± 0.0532 | +0.5525 ± 0.0461 | opposite | 1.829 |
| CLOSEPACKING | kExcludedVector | +3.3215 ± 0.0859 | −2.2730 ± 0.0559 | opposite | 1.461 |
| CLOSEPACKING | kExcludedExcited | **−13.0501 ± 0.2818** | **+10.0895 ± 0.1768** | opposite | 1.293 |
| CLOSEPACKING | kMultiplyHeavy | −47.1988 ± 1.9252 | +47.2161 ± 5.0150 | opposite | 1.000 (LOW-STAT) |

**The pair is two-sided and opposite-signed in all eleven comparable cells.** It
is not one-sided and it is not same-signed. MONASH's `kMultiplyHeavy` is not
comparable in either arm: the sealed nominal holds 8 counts in total and
individual blocks hold zero, so a relative shift against it has no meaning and
none is quoted.

**It is also systematically ASYMMETRIC, and the DOWN arm is the larger one in
every resolved category** — by factors of 1.245 to 1.829. Halving μ_F moves the
decomposition more than doubling it does. That is the shape a logarithmic scale
dependence produces, and it is a physics result rather than a fault: the two
arms probe different parts of the same evolution.

**The two LOW-STAT `kMultiplyHeavy` cells are the only ones near unity**, at
0.909 and 1.000, and their errors are large enough that the asymmetry seen
elsewhere would not be resolvable there.

**What follows for the budget.** Pre-registration §2.5 quotes the arm with the
larger `|Δ|`, so S1b is governed by the DOWN arm throughout, and the S1b
contribution is unchanged from what `MUF_DOWN` alone implied. The UP arm did not
enlarge the budget; it established the shape.

## S2 — the parton distribution, and it is small

| tune | category | Δ (%) | SEM | flag |
|---|---|---|---|---|
| MONASH | kCentralGround | +0.0025 | 0.0331 | unresolved |
| MONASH | kExcludedVector | +0.0249 | 0.0339 | unresolved |
| MONASH | kExcludedExcited | −1.2749 | 0.3729 | |
| JUNCTIONS | kCentralGround | +0.1915 | 0.0308 | |
| JUNCTIONS | kExcludedVector | −0.3510 | 0.0421 | |
| JUNCTIONS | kExcludedExcited | +1.2494 | 0.3253 | |
| JUNCTIONS | kMultiplyHeavy | +14.2345 | 3.8434 | LOW-STAT |
| CLOSEPACKING | kCentralGround | +0.0044 | 0.0334 | unresolved |
| CLOSEPACKING | kExcludedVector | −0.3501 | 0.0437 | |
| CLOSEPACKING | kExcludedExcited | +2.2649 | 0.3007 | |
| CLOSEPACKING | kMultiplyHeavy | +12.2892 | 3.9350 | LOW-STAT |

**S2 is the smallest of the four live sources on this axis.** Its largest
resolved shift is +2.2649 per cent, against S1b's −13.05. Three of its eleven
cells do not clear 2 SEM, and MONASH is insensitive to the PDF swap at the level
this sample can measure.

**That does not make it negligible in the combination.** On the *trend* the PDF
term is the largest contributor for CLOSEPACKING, at 36.03 per cent. A source
can be small on the category axis and large on a derived quantity. That is why
§9.1's μ_F-against-PDF choice runs per quantity rather than once.
