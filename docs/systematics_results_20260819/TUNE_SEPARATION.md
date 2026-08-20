# The reconnection tunes against MONASH, per multiplicity class

**2026-08-19.** The first half of the headline comparison. **It carries no
systematic**, and no row here is a verdict on whether the tunes separate.

## What this is, and what it is not

**Both JUNCTIONS and CLOSEPACKING are compared against MONASH.**

The tune separation is a property of the **sealed nominal campaign alone**:
three tunes, three sets of raw files, three sets of seeds, one hundred million
events each. It needs no variation campaign, so it can be computed now. The combined
systematic cannot: `HF_SYS_MUF_UP` and `HF_SYS_PDF_CTEQ6L1` are still merging,
and pre-registration §9 forbids a partial quadrature sum.

`extraction/combine_per_class.py` **refuses to run** while either is missing, and
names them. The verdict belongs to the session that has all seven.

## Three things about the numbers, before the numbers

**`c1` is the LOWEST multiplicity and `c11` the highest.** The window label is a
**top** percentile — the fraction of minimum-bias events above the boundary — so
a high percentile is a low `N_ch`. The render log states the mapping:

```
MULTIPLICITY_BOUNDARY percentile=100     nch=0
MULTIPLICITY_BOUNDARY percentile=88.197  nch=2
MULTIPLICITY_BOUNDARY percentile=8.422   nch=32
MULTIPLICITY_BOUNDARY percentile=0       nch=4095
```

The label `MB88p197_100` belongs to `c1`, which holds `N_ch` 0 to 2. The label
`MB0_8p422` belongs to `c11`, which holds `N_ch` 33 and above. That agrees with
`config/multiplicity_class_boundaries_v1.json`, where `c1` spans `[-0.5, 2.5)`
and `c11` is open-ended above 32.5. **Reading the label as an ordinary
percentile inverts every trend below**, and
`tests/test_harvest_class_axis.py` now holds the two statements together.

**The SEM of the difference is the two SEMs in quadrature**, because the three
tunes are separate generation campaigns rather than three analyses of one
sample.

**The ratio's uncertainty comes from the plotter, not from propagation.** Λ_b
and B⁻ share their triggers and their events, so adding the two yield SEMs in
quadrature would be wrong. The plotter forms the ratio inside each block and
reports `ratio_sem` over the ten.

## How to read the last column

**`% of MONASH to erase`** is `|difference| / MONASH × 100`: the size a combined
systematic would have to reach, relative to the MONASH value, to close the gap.
It is arithmetic on the nominal and quotes no systematic. It is here so the
next session can see at a glance which classes the systematic could still
overturn and which it could not.

### MONASH − JUNCTIONS — B+ - B- balancing yield

| class | MONASH | JUNCTIONS | difference | stat. σ | % of MONASH to erase |
|---|---|---|---|---|---|
| `c1` | 0.113992 ± 0.00153 | 0.108891 ± 0.00174 | +0.00510079 ± 0.00232 | 2.2 | 4.5 |
| `c2` | 0.111642 ± 0.00234 | 0.106846 ± 0.00141 | +0.00479589 ± 0.00274 | 1.8 | 4.3 |
| `c3` | 0.115035 ± 0.000889 | 0.101056 ± 0.00112 | +0.013979 ± 0.00143 | 9.8 | 12.2 |
| `c4` | 0.115351 ± 0.00162 | 0.100808 ± 0.0014 | +0.014543 ± 0.00214 | 6.8 | 12.6 |
| `c5` | 0.115146 ± 0.00182 | 0.096913 ± 0.00154 | +0.0182325 ± 0.00238 | 7.6 | 15.8 |
| `c6` | 0.117525 ± 0.00123 | 0.0934044 ± 0.00105 | +0.0241203 ± 0.00162 | 14.9 | 20.5 |
| `c7` | 0.115677 ± 0.000811 | 0.0890099 ± 0.000643 | +0.0266671 ± 0.00103 | 25.8 | 23.1 |
| `c8` | 0.115299 ± 0.00062 | 0.0869188 ± 0.000716 | +0.0283802 ± 0.000948 | 30.0 | 24.6 |
| `c9` | 0.11646 ± 0.000323 | 0.0833265 ± 0.000919 | +0.0331335 ± 0.000974 | 34.0 | 28.5 |
| `c10` | 0.11659 ± 0.000579 | 0.0811934 ± 0.000557 | +0.0353962 ± 0.000804 | 44.0 | 30.4 |
| `c11` | 0.118017 ± 0.000695 | 0.0803441 ± 0.000645 | +0.0376732 ± 0.000948 | 39.7 | 31.9 |
| `MB` | 0.116252 ± 0.000268 | 0.0873033 ± 0.000347 | +0.0289482 ± 0.000439 | 66.0 | 24.9 |

### MONASH − JUNCTIONS — B+ - Lambda_b balancing yield

| class | MONASH | JUNCTIONS | difference | stat. σ | % of MONASH to erase |
|---|---|---|---|---|---|
| `c1` | 0.0212539 ± 0.000694 | 0.0233113 ± 0.000659 | -0.00205741 ± 0.000957 | 2.2 | 9.7 |
| `c2` | 0.0198204 ± 0.00084 | 0.0256504 ± 0.000943 | -0.00582999 ± 0.00126 | 4.6 | 29.4 |
| `c3` | 0.0195332 ± 0.000496 | 0.0252449 ± 0.000612 | -0.00571163 ± 0.000788 | 7.3 | 29.2 |
| `c4` | 0.0200214 ± 0.000655 | 0.0269729 ± 0.000804 | -0.00695148 ± 0.00104 | 6.7 | 34.7 |
| `c5` | 0.019014 ± 0.000402 | 0.0287876 ± 0.000754 | -0.00977354 ± 0.000854 | 11.4 | 51.4 |
| `c6` | 0.0188718 ± 0.000503 | 0.0309733 ± 0.000516 | -0.0121015 ± 0.00072 | 16.8 | 64.1 |
| `c7` | 0.0194467 ± 0.000236 | 0.0335653 ± 0.000558 | -0.0141186 ± 0.000606 | 23.3 | 72.6 |
| `c8` | 0.0197992 ± 0.000281 | 0.0350954 ± 0.000306 | -0.0152963 ± 0.000415 | 36.8 | 77.3 |
| `c9` | 0.0194627 ± 0.000208 | 0.038713 ± 0.000744 | -0.0192503 ± 0.000773 | 24.9 | 98.9 |
| `c10` | 0.0192601 ± 0.000113 | 0.0415366 ± 0.000571 | -0.0222765 ± 0.000582 | 38.3 | 115.7 |
| `c11` | 0.0191096 ± 0.00031 | 0.0436405 ± 0.000388 | -0.0245309 ± 0.000496 | 49.4 | 128.4 |
| `MB` | 0.0194202 ± 9.65e-05 | 0.0365305 ± 0.000307 | -0.0171103 ± 0.000321 | 53.2 | 88.1 |

### MONASH − JUNCTIONS — Lambda_b / B- balancing-yield ratio

| class | MONASH | JUNCTIONS | difference | stat. σ | % of MONASH to erase |
|---|---|---|---|---|---|
| `c1` | 0.186451 ± 0.00692 | 0.21408 ± 0.00873 | -0.0276282 ± 0.0111 | 2.5 | 14.8 |
| `c2` | 0.177535 ± 0.00759 | 0.240068 ± 0.0105 | -0.0625332 ± 0.013 | 4.8 | 35.2 |
| `c3` | 0.169802 ± 0.00527 | 0.24981 ± 0.00642 | -0.080008 ± 0.00831 | 9.6 | 47.1 |
| `c4` | 0.173569 ± 0.00648 | 0.267566 ± 0.01 | -0.093997 ± 0.0119 | 7.9 | 54.2 |
| `c5` | 0.165131 ± 0.00539 | 0.297046 ± 0.00809 | -0.131915 ± 0.00972 | 13.6 | 79.9 |
| `c6` | 0.160577 ± 0.00423 | 0.331604 ± 0.00731 | -0.171027 ± 0.00845 | 20.2 | 106.5 |
| `c7` | 0.168112 ± 0.00263 | 0.377097 ± 0.00695 | -0.208985 ± 0.00743 | 28.1 | 124.3 |
| `c8` | 0.17172 ± 0.00252 | 0.403773 ± 0.00499 | -0.232052 ± 0.00559 | 41.5 | 135.1 |
| `c9` | 0.167119 ± 0.00195 | 0.464594 ± 0.0101 | -0.297475 ± 0.0102 | 29.0 | 178.0 |
| `c10` | 0.165195 ± 0.00106 | 0.511575 ± 0.00655 | -0.34638 ± 0.00663 | 52.2 | 209.7 |
| `c11` | 0.161922 ± 0.00258 | 0.54317 ± 0.0059 | -0.381248 ± 0.00644 | 59.2 | 235.5 |
| `MB` | 0.167054 ± 0.000784 | 0.418432 ± 0.00388 | -0.251378 ± 0.00395 | 63.6 | 150.5 |

### MONASH − CLOSEPACKING — B+ - B- balancing yield

| class | MONASH | CLOSEPACKING | difference | stat. σ | % of MONASH to erase |
|---|---|---|---|---|---|
| `c1` | 0.113992 ± 0.00153 | 0.106397 ± 0.00168 | +0.00759446 ± 0.00227 | 3.3 | 6.7 |
| `c2` | 0.111642 ± 0.00234 | 0.104759 ± 0.00238 | +0.00688288 ± 0.00334 | 2.1 | 6.2 |
| `c3` | 0.115035 ± 0.000889 | 0.0990766 ± 0.00122 | +0.0159587 ± 0.00151 | 10.6 | 13.9 |
| `c4` | 0.115351 ± 0.00162 | 0.0983132 ± 0.00143 | +0.0170383 ± 0.00216 | 7.9 | 14.8 |
| `c5` | 0.115146 ± 0.00182 | 0.0909076 ± 0.000944 | +0.0242379 ± 0.00205 | 11.8 | 21.0 |
| `c6` | 0.117525 ± 0.00123 | 0.0910064 ± 0.000939 | +0.0265182 ± 0.00155 | 17.1 | 22.6 |
| `c7` | 0.115677 ± 0.000811 | 0.0882036 ± 0.000706 | +0.0274734 ± 0.00107 | 25.6 | 23.8 |
| `c8` | 0.115299 ± 0.00062 | 0.0841808 ± 0.000638 | +0.0311181 ± 0.00089 | 35.0 | 27.0 |
| `c9` | 0.11646 ± 0.000323 | 0.0815644 ± 0.00044 | +0.0348956 ± 0.000546 | 64.0 | 30.0 |
| `c10` | 0.11659 ± 0.000579 | 0.0784085 ± 0.000532 | +0.0381811 ± 0.000786 | 48.6 | 32.7 |
| `c11` | 0.118017 ± 0.000695 | 0.0779495 ± 0.000902 | +0.0400678 ± 0.00114 | 35.2 | 34.0 |
| `MB` | 0.116252 ± 0.000268 | 0.0854967 ± 0.000233 | +0.0307549 ± 0.000355 | 86.5 | 26.5 |

### MONASH − CLOSEPACKING — B+ - Lambda_b balancing yield

| class | MONASH | CLOSEPACKING | difference | stat. σ | % of MONASH to erase |
|---|---|---|---|---|---|
| `c1` | 0.0212539 ± 0.000694 | 0.0230079 ± 0.000935 | -0.00175392 ± 0.00116 | 1.5 | 8.3 |
| `c2` | 0.0198204 ± 0.00084 | 0.0214225 ± 0.000949 | -0.00160209 ± 0.00127 | 1.3 | 8.1 |
| `c3` | 0.0195332 ± 0.000496 | 0.022841 ± 0.000709 | -0.00330771 ± 0.000866 | 3.8 | 16.9 |
| `c4` | 0.0200214 ± 0.000655 | 0.0254516 ± 0.000902 | -0.00543024 ± 0.00111 | 4.9 | 27.1 |
| `c5` | 0.019014 ± 0.000402 | 0.0269188 ± 0.00046 | -0.00790472 ± 0.000611 | 12.9 | 41.6 |
| `c6` | 0.0188718 ± 0.000503 | 0.029333 ± 0.000547 | -0.0104613 ± 0.000743 | 14.1 | 55.4 |
| `c7` | 0.0194467 ± 0.000236 | 0.0309719 ± 0.00061 | -0.0115252 ± 0.000654 | 17.6 | 59.3 |
| `c8` | 0.0197992 ± 0.000281 | 0.03363 ± 0.000657 | -0.0138308 ± 0.000715 | 19.3 | 69.9 |
| `c9` | 0.0194627 ± 0.000208 | 0.0361989 ± 0.00057 | -0.0167362 ± 0.000607 | 27.6 | 86.0 |
| `c10` | 0.0192601 ± 0.000113 | 0.0381479 ± 0.000319 | -0.0188878 ± 0.000338 | 55.9 | 98.1 |
| `c11` | 0.0191096 ± 0.00031 | 0.0392425 ± 0.000576 | -0.0201329 ± 0.000654 | 30.8 | 105.4 |
| `MB` | 0.0194202 ± 9.65e-05 | 0.033295 ± 0.000222 | -0.0138748 ± 0.000242 | 57.4 | 71.4 |

### MONASH − CLOSEPACKING — Lambda_b / B- balancing-yield ratio

| class | MONASH | CLOSEPACKING | difference | stat. σ | % of MONASH to erase |
|---|---|---|---|---|---|
| `c1` | 0.186451 ± 0.00692 | 0.216245 ± 0.00765 | -0.0297932 ± 0.0103 | 2.9 | 16.0 |
| `c2` | 0.177535 ± 0.00759 | 0.204493 ± 0.00971 | -0.0269575 ± 0.0123 | 2.2 | 15.2 |
| `c3` | 0.169802 ± 0.00527 | 0.230538 ± 0.00596 | -0.0607361 ± 0.00796 | 7.6 | 35.8 |
| `c4` | 0.173569 ± 0.00648 | 0.258883 ± 0.009 | -0.0853146 ± 0.0111 | 7.7 | 49.2 |
| `c5` | 0.165131 ± 0.00539 | 0.296111 ± 0.00445 | -0.130981 ± 0.00699 | 18.7 | 79.3 |
| `c6` | 0.160577 ± 0.00423 | 0.322318 ± 0.00745 | -0.161741 ± 0.00856 | 18.9 | 100.7 |
| `c7` | 0.168112 ± 0.00263 | 0.351141 ± 0.00828 | -0.183029 ± 0.00868 | 21.1 | 108.9 |
| `c8` | 0.17172 ± 0.00252 | 0.399497 ± 0.00784 | -0.227777 ± 0.00824 | 27.7 | 132.6 |
| `c9` | 0.167119 ± 0.00195 | 0.443807 ± 0.00712 | -0.276688 ± 0.00738 | 37.5 | 165.6 |
| `c10` | 0.165195 ± 0.00106 | 0.486527 ± 0.00615 | -0.321332 ± 0.00624 | 51.5 | 194.5 |
| `c11` | 0.161922 ± 0.00258 | 0.503435 ± 0.0113 | -0.341513 ± 0.0116 | 29.5 | 210.9 |
| `MB` | 0.167054 ± 0.000784 | 0.389431 ± 0.00324 | -0.222377 ± 0.00333 | 66.7 | 133.1 |
