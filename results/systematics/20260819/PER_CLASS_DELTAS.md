# Per-class and integrated balancing-yield deltas — five closed campaigns

**2026-08-19.** Deliverable 2 of pre-registration section 2, the per-class
OS−SS balancing yield, for the five campaigns that closed. Section 15.6 of the
run record recorded that this deliverable had no chain for a variation campaign.
It has one now.

**These are measurement numbers, not publication numbers.** Every render carries
`purpose=measurement` and `publication_eligible=false`, and nothing here may be
promoted into a figure.

## 1. The quantity, and the estimator

Each `UNCERTAINTY_MATRIX` row carries `central_yield`, the OS−SS balancing yield
per trigger, and `yield_sem`, its standard error over the ten subsample blocks.
The row identity is the five fields `GOLDEN_OUTPUTS` 9.9.1 requires, with the
multiplicity class parsed out of the bin name by the rule in run record 18.2.

```
Delta      = variation - nominal
SEM(Delta) = sqrt(SEM_variation^2 + SEM_nominal^2)
flagged    when |Delta| < 2 * SEM(Delta)
```

**The delta is absolute.** The log gives one mean and one SEM per row and no
block yields, so the per-block relative estimator of pre-registration 2.2 cannot
be formed from it. The relative shift is reported beside the absolute one.

**Every cell can carry a relative shift.** The smallest nominal yield in the 720
cells is 0.0180359 and none is zero, so no cell is named in place of a number.
Two cells carry a relative shift above 25 per cent, both in the smallest series.
`HF_SYS_MUR_UP` MONASH B⁺–Λ_b class c4 moves +41.76 per cent on a nominal of
0.0200214. `HF_SYS_PTHAT_1` CLOSEPACKING B⁺–Λ_b class c1 moves −35.30 per cent
on a nominal of 0.0230079. Both clear 2 SEM, at 2.71 and 3.43. The large
fraction is the small denominator, not a large absolute move.

## 2. The instrument, and the proof it is the same one

| artifact | sha256 |
|---|---|
| nominal, `vintegrated_closure.log` | `f507f6250e63d82c9c34e088abe4ec16b17359e3b0a54fcdb54e17cd67653d7b` |
| control, `render_HF_RUN3_V1.log` | `690f2dc5694fa8639582e7ff2a5dd42f392c66ab2ccdf1268e9e5974e65afe68` |
| `render_HF_SYS_MUR_UP.log` | `e967aa5184b8fb80b72f6d003bb8770d470a42950433e938cd3a9ed355a7458a` |
| `render_HF_SYS_MUR_DOWN.log` | `34f470c4c7d4537e59f5b10236eed772d4e526a947bcfe21bc393d4c0994fb69` |
| `render_HF_SYS_MUF_DOWN.log` | `26c233e86202c1c1a0daf8affa0baeb32a5564688adf9d32f6738009b00dbb29` |
| `render_HF_SYS_PTHAT_1.log` | `06cd8766f6bd43a942f7463540c57306c7cbb2e65104116c44995b759b3a9b77` |
| `render_HF_SYS_PTHAT_4.log` | `7922626e6504e8359b740080a12bf50415a221d19f5268ab21845aa0d6393792` |
| `per_class_deltas.json` | `cac0a757ec7bdca04f2390668334733488d95bba14b3f22be2e0216980ad86c2` |
| `per_class_deltas.csv` | `70e07e49d8feeeda9cef5738b2cfaab4ef467a25db511e95e80caf2e38e4bb78` |

Environment: `stbc-i1.nikhef.nl`, deploy `/data/alice/ipardoza/sys_plot_deploy`,
measurement root `/data/alice/ipardoza/measurements_v3`, render window 16:04 to
16:10 CEST.

**The class windows are identical across all six configurations.** The eleven
`histograms_to_analyse` entries of each variation configuration match the
central's byte for byte. A per-class comparison against a moved window would be
a comparison of two different quantities.

**The integrated bin was added from the sealed source.** The eleven-class
configuration emits 132 rows and no integrated arm. The staging step appends the
`M00_100` entry copied from
`configuration_multiplicity_HF_RUN3_V1_VINTEGRATED_CLOSURE.json`, sha256
`793344f3…`, the configuration that produced the nominal. Each render therefore
emits **144 rows**: twelve classes by twelve series.

**Two plotter builds, and the difference is inert.** The nominal came from the
figure branch's plotter, sha256 `6845553…`; the control and the variations from
this branch's, `6dace20…`. The figure branch adds a staging layer, a
non-integral pair-count guard and canvas polish. **No yield-computation line
differs**, and the control below is the measurement rather than the claim.

## 3. The control

**All 144 rows agree. No disagreement in any field, at the precision the logs
record, with no numeric tolerance.**

| | |
|---|---|
| rows shared between nominal and control | **144** |
| rows only in one of them | **0** |
| disagreeing fields across `central_yield`, `yield_sem`, `central_triggers` | **0** |
| render exit status | 0 |
| output-side assertion | pass, 13 publication trees walked, 0 files touched |
| resolver assertion | pass, `central=['HF_RUN3_V1'] subsample=['HF_RUN3_V1']` |

**The two renders print different digit counts, and the comparison handles it
without a tolerance.** The figure-branch plotter writes the MONASH charm trigger
count as `13656517`; this branch's writes `1.36565e+07`. Both record the same
count at six figures. String equality would report a difference that is not
there; a numeric tolerance would accept one that is. The comparison uses the
figure branch's own method, agreement at the precision of the less precise
value. `tests/test_per_class_control.py` carries that case by name.

**The control ran twice, and the second run is a check on this session's own
intervention.** The first control render, 15:51 to 15:56, used the configuration
as committed and reproduced all 144 rows. The second, 16:04 to 16:09, used the
same configuration with the ratio y-axis widened, and reproduced the same 144
rows. The widening is therefore inert, which is what licenses its use on the
variations.

## 4. Why the axis was widened, and why it cannot move a number

Two variation renders aborted at the drawing stage. The plotter refuses to draw
an uncertainty envelope that the configured y-axis would clip, which is correct
for a publication figure. `HF_SYS_MUR_UP` reaches 2.5949 on a ratio axis that
stops at 2.5, and `HF_SYS_PTHAT_1` reaches down to 0.5469 on one that starts at
0.6. **The axis frames the central campaign, and a variation is under no
obligation to fit inside it.**

The macro emits every `UNCERTAINTY_MATRIX` row at
`plotting/improvedPlotting_THnSparse.C:3739`, and draws the first canvas at
`:4015`. It prints the numbers before it applies any axis. The widening lives in
the staged measurement copy, each receipt records it as `axes_widened`, and this
session did not edit the committed configurations.

## 5. The per-event plausibility check

The E5 defect showed as about 13 counts per event where the truth is order one.
The gate is on the order of magnitude. Exposure is 100 million events per tune
for the nominal and 10 million for each variation, read from the campaign
manifests' `requested_successes`.

| campaign | B⁺ MON | B⁺ JUN | B⁺ CLP | D⁺ MON | D⁺ JUN | D⁺ CLP |
|---|---|---|---|---|---|---|
| *nominal* | *0.01426* | *0.01031* | *0.01010* | *0.13657* | *0.11720* | *0.11922* |
| control | 0.01426 | 0.01031 | 0.01010 | 0.13656 | 0.11721 | 0.11922 |
| `HF_SYS_MUR_UP` | 0.01493 | 0.01083 | 0.01071 | 0.13603 | 0.11684 | 0.11889 |
| `HF_SYS_MUR_DOWN` | 0.01342 | 0.00972 | 0.00948 | 0.13727 | 0.11753 | 0.11962 |
| `HF_SYS_MUF_DOWN` | 0.01759 | 0.01286 | 0.01268 | 0.12683 | 0.11263 | 0.11458 |
| `HF_SYS_PTHAT_1` | **0.00858** | **0.00617** | **0.00602** | 0.11184 | 0.09478 | 0.09768 |
| `HF_SYS_PTHAT_4` | **0.03101** | 0.02321 | 0.02268 | 0.13526 | 0.12041 | 0.12007 |

**All 42 pass.** The range is 0.00602 to 0.13727, so the worst point sits 95
times clear of the failure mode. The ordering is the physically expected one.
`PTHAT_1` sits lowest and `PTHAT_4` highest in beauty, in all three tunes, a
factor of 3.6 between them. Charm moves by a fifth of that. A harder scale
produces beauty far more readily than charm.

**The trigger counts are internally consistent in all 864 rows.** The ten block
counts account for the central count in every row of every render, compared
against the bound the printed precision implies. Six nominal rows fall short by
17, 13 or 14 counts in about 13 million. All six are the integrated bin for
charm. There ROOT prints the block counts as `1.3646e+06`, and ten values
rounded to the nearest hundred cannot sum to an exact total.

## 6. The standing checks

| check | result |
|---|---|
| two physically distinct variations agreeing exactly | **no pair agrees**, across all 144 rows of all five campaigns |
| every render resolved the campaign it was asked for | **5 of 5**, central and subsample resolvers both |
| every render passed the output-side assertion | **6 of 6**, 13 publication trees, 0 files touched |
| rows emitted per render | **144 of 144 expected**, all six |
| `yield_status` on both arms | **PASS** in all 720 delta cells |

## 7. What this does not settle

**This is not a combination.** The combination needs all seven campaigns.
`HF_SYS_MUF_UP` and `HF_SYS_PDF_CTEQ6L1` were still merging when these numbers
were taken, and no envelope, quadrature sum or arm selection appears here.

## The integrated deltas

Multiplicity-integrated bin `M00_100`, 12 series per campaign, 60 cells. **Bold** clears 2 SEM; *italic* falls short of it.


### BEAUTY B^{+} — B-

| campaign | MON | JUN | CLP |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | **-0.00240053 ± 0.000743** | *+0.0011014 ± 0.000979* | **+0.00283652 ± 0.00101** |
| `HF_SYS_MUR_DOWN` | *-0.00168653 ± 0.00103* | *+0.000888995 ± 0.000895* | *+0.000829918 ± 0.00125* |
| `HF_SYS_MUR_UP` | *-0.000657534 ± 0.000725* | *-0.0011412 ± 0.000882* | *+0.000233918 ± 0.000945* |
| `HF_SYS_PTHAT_1` | *-0.00216453 ± 0.00149* | *-0.0021849 ± 0.00142* | *-0.000641082 ± 0.00118* |
| `HF_SYS_PTHAT_4` | **+0.00320147 ± 0.000718** | **+0.0036931 ± 0.00056** | **+0.00440492 ± 0.000591** |

| campaign | MON rel. % | JUN rel. % | CLP rel. % |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | -2.065 | +1.262 | +3.318 |
| `HF_SYS_MUR_DOWN` | -1.451 | +1.018 | +0.9707 |
| `HF_SYS_MUR_UP` | -0.5656 | -1.307 | +0.2736 |
| `HF_SYS_PTHAT_1` | -1.862 | -2.503 | -0.7498 |
| `HF_SYS_PTHAT_4` | +2.754 | +4.23 | +5.152 |

### BEAUTY B^{+} — Lambda_b

| campaign | MON | JUN | CLP |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | *+0.000278561 ± 0.000293* | **-0.0025059 ± 0.000497** | *-0.00121334 ± 0.000652* |
| `HF_SYS_MUR_DOWN` | *-3.56391e-05 ± 0.00022* | *-0.000835996 ± 0.000454* | **+0.000745962 ± 0.000344** |
| `HF_SYS_MUR_UP` | *+0.000451761 ± 0.000242* | *+0.0010915 ± 0.000708* | *-0.000446738 ± 0.000465* |
| `HF_SYS_PTHAT_1` | *+0.000165261 ± 0.000561* | **-0.0014007 ± 0.000609** | *-0.000566238 ± 0.000778* |
| `HF_SYS_PTHAT_4` | **+0.000821661 ± 0.000379** | *-0.000962496 ± 0.000528* | *-0.000134638 ± 0.000388* |

| campaign | MON rel. % | JUN rel. % | CLP rel. % |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | +1.434 | -6.86 | -3.644 |
| `HF_SYS_MUR_DOWN` | -0.1835 | -2.288 | +2.24 |
| `HF_SYS_MUR_UP` | +2.326 | +2.988 | -1.342 |
| `HF_SYS_PTHAT_1` | +0.851 | -3.834 | -1.701 |
| `HF_SYS_PTHAT_4` | +4.231 | -2.635 | -0.4044 |

### CHARM D^{+} — D-

| campaign | MON | JUN | CLP |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | **-0.00230796 ± 0.000322** | **+0.00249823 ± 0.000428** | **+0.0026068 ± 0.000229** |
| `HF_SYS_MUR_DOWN` | *-0.000244957 ± 0.000414* | *-0.000423766 ± 0.000327* | **-0.0010342 ± 0.000239** |
| `HF_SYS_MUR_UP` | *-0.000159957 ± 0.000271* | *-0.000122766 ± 0.000396* | *-0.000583197 ± 0.000355* |
| `HF_SYS_PTHAT_1` | **-0.00737996 ± 0.000365** | **-0.00641277 ± 0.000274** | **-0.0048552 ± 0.000344** |
| `HF_SYS_PTHAT_4` | **+0.00960004 ± 0.000358** | **+0.0103962 ± 0.000498** | **+0.0091528 ± 0.000423** |

| campaign | MON rel. % | JUN rel. % | CLP rel. % |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | -1.193 | +1.436 | +1.503 |
| `HF_SYS_MUR_DOWN` | -0.1266 | -0.2436 | -0.5962 |
| `HF_SYS_MUR_UP` | -0.08269 | -0.07057 | -0.3362 |
| `HF_SYS_PTHAT_1` | -3.815 | -3.686 | -2.799 |
| `HF_SYS_PTHAT_4` | +4.963 | +5.976 | +5.276 |

### CHARM D^{+} — Lambda_c(+)-bar

| campaign | MON | JUN | CLP |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | *-0.000112083 ± 0.000141* | **-0.00158292 ± 0.000141** | **-0.001289 ± 0.000138** |
| `HF_SYS_MUR_DOWN` | *+5.51702e-06 ± 9.9e-05* | *-2.19244e-05 ± 0.000144* | *+0.000200996 ± 0.000124* |
| `HF_SYS_MUR_UP` | *-9.4883e-05 ± 0.000182* | *+0.000309576 ± 0.000162* | *+1.52957e-05 ± 0.000145* |
| `HF_SYS_PTHAT_1` | **-0.000909683 ± 0.000178** | **-0.00153742 ± 0.000208** | **-0.0010582 ± 0.000212** |
| `HF_SYS_PTHAT_4` | **+0.000957517 ± 0.000184** | **+0.00118448 ± 9.55e-05** | **+0.0011753 ± 0.000142** |

| campaign | MON rel. % | JUN rel. % | CLP rel. % |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | -0.5921 | -6.59 | -6.21 |
| `HF_SYS_MUR_DOWN` | +0.02914 | -0.09127 | +0.9683 |
| `HF_SYS_MUR_UP` | -0.5012 | +1.289 | +0.07369 |
| `HF_SYS_PTHAT_1` | -4.805 | -6.4 | -5.098 |
| `HF_SYS_PTHAT_4` | +5.058 | +4.931 | +5.662 |

## The per-class deltas, resolved counts

132 cells per campaign: eleven classes by twelve series. The count is how many clear 2 SEM.

| campaign | resolved / 132 | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `HF_SYS_MUF_DOWN` | **42/132** | 6/12 | 4/12 | 4/12 | 4/12 | 3/12 | 2/12 | 4/12 | 3/12 | 6/12 | 2/12 | 4/12 |
| `HF_SYS_MUR_DOWN` | **7/132** | 0/12 | 1/12 | 1/12 | 0/12 | 3/12 | 1/12 | 1/12 | 0/12 | 0/12 | 0/12 | 0/12 |
| `HF_SYS_MUR_UP` | **13/132** | 0/12 | 0/12 | 1/12 | 2/12 | 3/12 | 1/12 | 0/12 | 0/12 | 4/12 | 1/12 | 1/12 |
| `HF_SYS_PTHAT_1` | **34/132** | 7/12 | 5/12 | 6/12 | 4/12 | 4/12 | 1/12 | 4/12 | 1/12 | 1/12 | 1/12 | 0/12 |
| `HF_SYS_PTHAT_4` | **59/132** | 3/12 | 5/12 | 5/12 | 4/12 | 5/12 | 4/12 | 9/12 | 6/12 | 5/12 | 6/12 | 7/12 |

## The ten largest per-class effects, by significance

| campaign | series | tune | class | Δ ± SEM(Δ) | Δ/SEM | rel. % |
|---|---|---|---|---|---|---|
| `HF_SYS_PTHAT_4` | D^{+}–D- | JUN | c5 | +0.0158073 ± 0.000887 | 17.8 | +9.166 |
| `HF_SYS_PTHAT_4` | D^{+}–D- | JUN | c7 | +0.014697 ± 0.000897 | 16.4 | +8.648 |
| `HF_SYS_PTHAT_1` | D^{+}–D- | JUN | c3 | -0.0106299 ± 0.000744 | 14.3 | -6.017 |
| `HF_SYS_PTHAT_4` | D^{+}–D- | JUN | c3 | +0.0139841 ± 0.00102 | 13.7 | +7.916 |
| `HF_SYS_PTHAT_4` | D^{+}–D- | CLP | c5 | +0.0141429 ± 0.00107 | 13.2 | +8.202 |
| `HF_SYS_PTHAT_4` | D^{+}–D- | CLP | c3 | +0.0132949 ± 0.00113 | 11.8 | +7.557 |
| `HF_SYS_PTHAT_1` | D^{+}–D- | JUN | c1 | -0.00968686 ± 0.000893 | 10.8 | -5.377 |
| `HF_SYS_PTHAT_4` | D^{+}–D- | MON | c3 | +0.0104664 ± 0.000991 | 10.6 | +5.552 |
| `HF_SYS_PTHAT_1` | D^{+}–D- | JUN | c4 | -0.00979269 ± 0.000937 | 10.5 | -5.617 |
| `HF_SYS_PTHAT_1` | D^{+}–D- | CLP | c3 | -0.0101931 ± 0.000977 | 10.4 | -5.794 |
