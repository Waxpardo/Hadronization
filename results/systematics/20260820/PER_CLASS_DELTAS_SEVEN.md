# Per-class and integrated deltas — all seven campaigns

**2026-08-20.** 1008 cells: seven campaigns, twelve classes, twelve series. The
five extracted on 2026-08-19 are unchanged; `HF_SYS_MUF_UP` and
`HF_SYS_PDF_CTEQ6L1` join them here.

**Estimator:** Δ = variation − nominal, SEM(Δ) = √(SEM_var² + SEM_central²),
flagged below 2 SEM. **772 of 1008 cells fall short of 2 SEM.**

**Every cell carries a relative shift.** No nominal in the 1008 is zero, so no
cell is named in place of a number.

## The controls

| control | result |
|---|---|
| the control render reproduces the sealed nominal | **144 of 144 rows, zero disagreements** |
| cross-session instrument check | the 2026-08-20 control is **byte-identical** to the 2026-08-19 control on all 144 rows |
| every render's resolver assertion | **7 of 7**, central and subsample |
| every render's output-side assertion | **8 of 8**, 13 publication trees, 0 files touched |
| rows per render | **144 of 144 expected**, all eight |
| trigger-count consistency | **0 failures in 1152 rows** |
| two distinct variations agreeing exactly | **no pair**, across all 144 rows of all seven |

**Machine-readable:** `per_class_deltas_seven.json`, flat
`per_class_deltas_seven.csv`.

## The integrated deltas

Multiplicity-integrated bin `M00_100`, 12 series per campaign, 60 cells. **Bold** is resolved at 2 SEM; *italic* falls short of it.


### BEAUTY B^{+} — B-

| campaign | MON | JUN | CLP |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | **-0.00240053 ± 0.000743** | *+0.0011014 ± 0.000979* | **+0.00283652 ± 0.00101** |
| `HF_SYS_MUF_UP` | *+0.00133347 ± 0.00108* | *+0.000674495 ± 0.000948* | *+0.000788118 ± 0.00101* |
| `HF_SYS_MUR_DOWN` | *-0.00168653 ± 0.00103* | *+0.000888995 ± 0.000895* | *+0.000829918 ± 0.00125* |
| `HF_SYS_MUR_UP` | *-0.000657534 ± 0.000725* | *-0.0011412 ± 0.000882* | *+0.000233918 ± 0.000945* |
| `HF_SYS_PDF_CTEQ6L1` | *-0.000114534 ± 0.000592* | *-0.0010204 ± 0.000675* | *-0.000261982 ± 0.000526* |
| `HF_SYS_PTHAT_1` | *-0.00216453 ± 0.00149* | *-0.0021849 ± 0.00142* | *-0.000641082 ± 0.00118* |
| `HF_SYS_PTHAT_4` | **+0.00320147 ± 0.000718** | **+0.0036931 ± 0.00056** | **+0.00440492 ± 0.000591** |

| campaign | MON rel. % | JUN rel. % | CLP rel. % |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | -2.065 | +1.262 | +3.318 |
| `HF_SYS_MUF_UP` | +1.147 | +0.7726 | +0.9218 |
| `HF_SYS_MUR_DOWN` | -1.451 | +1.018 | +0.9707 |
| `HF_SYS_MUR_UP` | -0.5656 | -1.307 | +0.2736 |
| `HF_SYS_PDF_CTEQ6L1` | -0.09852 | -1.169 | -0.3064 |
| `HF_SYS_PTHAT_1` | -1.862 | -2.503 | -0.7498 |
| `HF_SYS_PTHAT_4` | +2.754 | +4.23 | +5.152 |

### BEAUTY B^{+} — Lambda_b

| campaign | MON | JUN | CLP |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | *+0.000278561 ± 0.000293* | **-0.0025059 ± 0.000497** | *-0.00121334 ± 0.000652* |
| `HF_SYS_MUF_UP` | **+0.000707761 ± 0.000338** | *+0.000461804 ± 0.000902* | *+0.00111456 ± 0.000772* |
| `HF_SYS_MUR_DOWN` | *-3.56391e-05 ± 0.00022* | *-0.000835996 ± 0.000454* | **+0.000745962 ± 0.000344** |
| `HF_SYS_MUR_UP` | *+0.000451761 ± 0.000242* | *+0.0010915 ± 0.000708* | *-0.000446738 ± 0.000465* |
| `HF_SYS_PDF_CTEQ6L1` | **+0.000843361 ± 0.000323** | **+0.0022609 ± 0.000544** | *+0.00175256 ± 0.00101* |
| `HF_SYS_PTHAT_1` | *+0.000165261 ± 0.000561* | **-0.0014007 ± 0.000609** | *-0.000566238 ± 0.000778* |
| `HF_SYS_PTHAT_4` | **+0.000821661 ± 0.000379** | *-0.000962496 ± 0.000528* | *-0.000134638 ± 0.000388* |

| campaign | MON rel. % | JUN rel. % | CLP rel. % |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | +1.434 | -6.86 | -3.644 |
| `HF_SYS_MUF_UP` | +3.644 | +1.264 | +3.348 |
| `HF_SYS_MUR_DOWN` | -0.1835 | -2.288 | +2.24 |
| `HF_SYS_MUR_UP` | +2.326 | +2.988 | -1.342 |
| `HF_SYS_PDF_CTEQ6L1` | +4.343 | +6.189 | +5.264 |
| `HF_SYS_PTHAT_1` | +0.851 | -3.834 | -1.701 |
| `HF_SYS_PTHAT_4` | +4.231 | -2.635 | -0.4044 |

### CHARM D^{+} — D-

| campaign | MON | JUN | CLP |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | **-0.00230796 ± 0.000322** | **+0.00249823 ± 0.000428** | **+0.0026068 ± 0.000229** |
| `HF_SYS_MUF_UP` | **+0.00210904 ± 0.000363** | **-0.00131677 ± 0.000444** | **-0.0015992 ± 0.000283** |
| `HF_SYS_MUR_DOWN` | *-0.000244957 ± 0.000414* | *-0.000423766 ± 0.000327* | **-0.0010342 ± 0.000239** |
| `HF_SYS_MUR_UP` | *-0.000159957 ± 0.000271* | *-0.000122766 ± 0.000396* | *-0.000583197 ± 0.000355* |
| `HF_SYS_PDF_CTEQ6L1` | **+0.000993043 ± 0.000324** | *+0.000300234 ± 0.000477* | *+0.000646803 ± 0.000424* |
| `HF_SYS_PTHAT_1` | **-0.00737996 ± 0.000365** | **-0.00641277 ± 0.000274** | **-0.0048552 ± 0.000344** |
| `HF_SYS_PTHAT_4` | **+0.00960004 ± 0.000358** | **+0.0103962 ± 0.000498** | **+0.0091528 ± 0.000423** |

| campaign | MON rel. % | JUN rel. % | CLP rel. % |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | -1.193 | +1.436 | +1.503 |
| `HF_SYS_MUF_UP` | +1.09 | -0.7569 | -0.9218 |
| `HF_SYS_MUR_DOWN` | -0.1266 | -0.2436 | -0.5962 |
| `HF_SYS_MUR_UP` | -0.08269 | -0.07057 | -0.3362 |
| `HF_SYS_PDF_CTEQ6L1` | +0.5133 | +0.1726 | +0.3728 |
| `HF_SYS_PTHAT_1` | -3.815 | -3.686 | -2.799 |
| `HF_SYS_PTHAT_4` | +4.963 | +5.976 | +5.276 |

### CHARM D^{+} — Lambda_c(+)-bar

| campaign | MON | JUN | CLP |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | *-0.000112083 ± 0.000141* | **-0.00158292 ± 0.000141** | **-0.001289 ± 0.000138** |
| `HF_SYS_MUF_UP` | *+0.000197317 ± 0.000111* | **+0.00125318 ± 0.000197** | **+0.0012697 ± 0.000152** |
| `HF_SYS_MUR_DOWN` | *+5.51702e-06 ± 9.9e-05* | *-2.19244e-05 ± 0.000144* | *+0.000200996 ± 0.000124* |
| `HF_SYS_MUR_UP` | *-9.4883e-05 ± 0.000182* | *+0.000309576 ± 0.000162* | *+1.52957e-05 ± 0.000145* |
| `HF_SYS_PDF_CTEQ6L1` | **+0.000270617 ± 0.00012** | **+0.000430976 ± 0.000173** | *+0.000299896 ± 0.000154* |
| `HF_SYS_PTHAT_1` | **-0.000909683 ± 0.000178** | **-0.00153742 ± 0.000208** | **-0.0010582 ± 0.000212** |
| `HF_SYS_PTHAT_4` | **+0.000957517 ± 0.000184** | **+0.00118448 ± 9.55e-05** | **+0.0011753 ± 0.000142** |

| campaign | MON rel. % | JUN rel. % | CLP rel. % |
|---|---|---|---|
| `HF_SYS_MUF_DOWN` | -0.5921 | -6.59 | -6.21 |
| `HF_SYS_MUF_UP` | +1.042 | +5.217 | +6.117 |
| `HF_SYS_MUR_DOWN` | +0.02914 | -0.09127 | +0.9683 |
| `HF_SYS_MUR_UP` | -0.5012 | +1.289 | +0.07369 |
| `HF_SYS_PDF_CTEQ6L1` | +1.43 | +1.794 | +1.445 |
| `HF_SYS_PTHAT_1` | -4.805 | -6.4 | -5.098 |
| `HF_SYS_PTHAT_4` | +5.058 | +4.931 | +5.662 |

## The per-class deltas, resolved counts

132 cells per campaign: eleven classes by twelve series. The count is how many are resolved at 2 SEM.

| campaign | resolved / 132 | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `HF_SYS_MUF_DOWN` | **42/132** | 6/12 | 4/12 | 4/12 | 4/12 | 3/12 | 2/12 | 4/12 | 3/12 | 6/12 | 2/12 | 4/12 |
| `HF_SYS_MUF_UP` | **26/132** | 2/12 | 4/12 | 2/12 | 2/12 | 1/12 | 4/12 | 1/12 | 2/12 | 1/12 | 3/12 | 4/12 |
| `HF_SYS_MUR_DOWN` | **7/132** | 0/12 | 1/12 | 1/12 | 0/12 | 3/12 | 1/12 | 1/12 | 0/12 | 0/12 | 0/12 | 0/12 |
| `HF_SYS_MUR_UP` | **13/132** | 0/12 | 0/12 | 1/12 | 2/12 | 3/12 | 1/12 | 0/12 | 0/12 | 4/12 | 1/12 | 1/12 |
| `HF_SYS_PDF_CTEQ6L1` | **17/132** | 4/12 | 2/12 | 1/12 | 1/12 | 1/12 | 0/12 | 1/12 | 2/12 | 1/12 | 4/12 | 0/12 |
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
