# Results

> **Superseded result record.** The class-dependent tables and conclusions in
> this file were produced on the retired common absolute multiplicity axis.
> They remain historical provenance and are not results of the 2026-08-22
> rebuild. Regeneration requires tune-local v2 boundary receipts; see
> `docs/REBUILD_STATUS.md`.

## 1. Scope and claim hierarchy

The primary result is a multiplicity trend in the beauty baryon-to-meson balancing-yield ratio.
The estimator is `R(c11) - R(c1)`, where `c1` has the lowest activity.
The selected campaign is `HF_RUN3_V1`, which the selector marks `canonical` and publication-eligible.
Sources: `config/dataset_selector_hf_run3_v1.json` and `results/systematics/20260819/ratio_trend.json`.

The publication taxonomy separates five artifact roles.

- Scientific results are paper-used values or ROOT-derived figures with accepted inputs and uncertainties.
- Reproduction evidence supports those results through tables, configurations, receipts, hashes, and tests.
- Validations return pass or fail against a declared contract.
- Diagnostics and advisory findings identify patterns without acting as results or gates.
- History records superseded work and is not a runnable dependency.

Incomplete work is not a result class; it limits the published claim.

The final per-class budget excludes S4, the wide event-activity counter variation.
The resulting verdict is provisional until that variation completes.
The `terms_percent` fields contain S1a, S1b, S2, S3, and S5, but no S4.
Source: `results/systematics/20260820/per_class_combination.json`.

Every retained result is also conditioned on generator-job completion. The
campaign record gives 0/1,000 discarded attempts for MONASH, 63/1,063 for
JUNCTIONS, and 64/1,064 for CLOSEPACKING. The hang occurs in
`JunctionSplitting`, while event-content independence remains unmeasured.
Equal retained event counts do not close this tune-dependent selection risk;
no tune comparison in this document is an accepted publication inference.

Cross-class and cross-observable covariance remains unmeasured.
This gap limits endpoint contrasts and combinations across plotted observables.
No covariance estimate enters `extraction/ratio_trend.py` or `extraction/write_verdict.py`.

Each quoted per-class significance is a per-cell value.
The code applies no correction across the 72 comparisons in `verdict.json`.
This document claims no global significance.

## 2. Three-tune species decomposition

The diquark-structure decomposition is a partition of the extracted pair weight.
Each entry gives the mean percentage across ten blocks and its block SEM.

| structural group | MONASH (%) | JUNCTIONS (%) | CLOSEPACKING (%) |
|---|---:|---:|---:|
| `kCentralGround` | 52.4959 +/- 0.0074 | 58.2318 +/- 0.0078 | 54.1697 +/- 0.0112 |
| `kExcludedVector` | 46.4946 +/- 0.0079 | 39.9409 +/- 0.0083 | 39.9976 +/- 0.0105 |
| `kExcludedExcited` | 1.0095 +/- 0.0012 | 1.7821 +/- 0.0015 | 5.7745 +/- 0.0050 |
| `kMultiplyHeavy` | 0.0000 +/- 0.0000 | 0.0452 +/- 0.0004 | 0.0583 +/- 0.0007 |
| sum | 100.0000 | 100.0000 | 100.0000 |

Source: `extraction/three_tune_table.py` applied to the three
`evidence/merged_<tune>_dedup` central and block directories.

The experiment-comparable selection applies decay-map weights to a common ground-state row set.
It is a selection, not a partition, and its rows do not sum to 100 percent.

| selected ground state | MONASH (%) | JUNCTIONS (%) | CLOSEPACKING (%) |
|---|---:|---:|---:|
| D0 | 25.4543 +/- 0.0038 | 22.9720 +/- 0.0067 | 22.8191 +/- 0.0058 |
| anti-D0 | 25.3809 +/- 0.0070 | 22.9102 +/- 0.0056 | 22.7796 +/- 0.0072 |
| D+ | 13.2505 +/- 0.0035 | 12.0333 +/- 0.0034 | 11.9725 +/- 0.0038 |
| D- | 13.2225 +/- 0.0032 | 11.9964 +/- 0.0029 | 11.9557 +/- 0.0045 |
| D_s+ | 4.2720 +/- 0.0015 | 3.4894 +/- 0.0022 | 4.0852 +/- 0.0030 |
| D_s- | 4.2684 +/- 0.0017 | 3.4965 +/- 0.0030 | 4.0529 +/- 0.0032 |
| Lambda_c+ | 1.6401 +/- 0.0019 | 5.6503 +/- 0.0028 | 5.1222 +/- 0.0037 |
| anti-Lambda_c- | 1.6049 +/- 0.0015 | 5.5632 +/- 0.0041 | 5.1018 +/- 0.0036 |
| B+ | 2.1441 +/- 0.0017 | 1.4879 +/- 0.0012 | 1.4048 +/- 0.0015 |
| B- | 2.1431 +/- 0.0024 | 1.4868 +/- 0.0023 | 1.4020 +/- 0.0026 |
| selection total | 93.3808 | 91.0860 | 90.6958 |

Source: the same three anchors, `contracts/decay_parent_map_v2.json`,
and `extraction/three_tune_table.py`.

The integrity artifacts report exact central-to-block addition for all three tunes.
The robust block check reports zero MONASH flags, three JUNCTIONS flags, and one CLOSEPACKING flag.
The anchor manifests identify the flagged bins and retain the closure provenance.
Sources: the three `evidence/merged_<tune>_dedup/MANIFEST.md` files.

Every anchor directory reports exact species-to-category self-checks and conserved regrouping.
The same manifests bind the extractor, species axis, pair registry, and decay-map digests.
`extraction/three_tune_table.py` regenerates both tables directly from these anchors.

## 3. Multiplicity-integrated balancing yields

The integrated result reports pooled balancing yields with block SEMs.
Each row comes from the committed nominal plotting-log fixture.

| sector | tune | reference meson | baryon |
|---|---|---:|---:|
| beauty | MONASH | B- 0.11625 +/- 0.00027 | Lambda_b 0.01942 +/- 0.00010 |
| beauty | JUNCTIONS | B- 0.08730 +/- 0.00035 | Lambda_b 0.03653 +/- 0.00031 |
| beauty | CLOSEPACKING | B- 0.08550 +/- 0.00023 | Lambda_b 0.03330 +/- 0.00022 |
| charm | MONASH | D- 0.19345 +/- 0.00012 | anti-Lambda_c 0.01893 +/- 0.00005 |
| charm | JUNCTIONS | D- 0.17397 +/- 0.00013 | anti-Lambda_c 0.02402 +/- 0.00003 |
| charm | CLOSEPACKING | D- 0.17348 +/- 0.00010 | anti-Lambda_c 0.02076 +/- 0.00004 |

Source: `tests/fixtures/integrated_rows_nominal.log`.
The fixture reports twelve finite-yield rows, each with `finite_yields=10` and `status=PASS`.

The repository cannot reproduce the registered integer-exact closure for these yields.
`tools/vintegrated_closure.py` requires `PAIR_COUNTS` lines, but the source plotting log is absent.
The fixture contains uncertainty rows only.
Thus, this document does not independently verify the integrated closure.

## 4. Multiplicity dependence of balancing yields

The beauty yields change in opposite directions from `c1` to `c11`.
Each cell gives the B- yield and the Lambda_b yield, each with its block SEM.

| class | MONASH B- / Lambda_b | JUNCTIONS B- / Lambda_b | CLOSEPACKING B- / Lambda_b |
|---|---:|---:|---:|
| `c1` | 0.11399 +/- 0.00153 / 0.02125 +/- 0.00069 | 0.10889 +/- 0.00174 / 0.02331 +/- 0.00066 | 0.10640 +/- 0.00168 / 0.02301 +/- 0.00094 |
| `c2` | 0.11164 +/- 0.00234 / 0.01982 +/- 0.00084 | 0.10685 +/- 0.00141 / 0.02565 +/- 0.00094 | 0.10476 +/- 0.00238 / 0.02142 +/- 0.00095 |
| `c3` | 0.11504 +/- 0.00089 / 0.01953 +/- 0.00050 | 0.10106 +/- 0.00112 / 0.02524 +/- 0.00061 | 0.09908 +/- 0.00122 / 0.02284 +/- 0.00071 |
| `c4` | 0.11535 +/- 0.00162 / 0.02002 +/- 0.00065 | 0.10081 +/- 0.00140 / 0.02697 +/- 0.00080 | 0.09831 +/- 0.00143 / 0.02545 +/- 0.00090 |
| `c5` | 0.11515 +/- 0.00182 / 0.01901 +/- 0.00040 | 0.09691 +/- 0.00154 / 0.02879 +/- 0.00075 | 0.09091 +/- 0.00094 / 0.02692 +/- 0.00046 |
| `c6` | 0.11752 +/- 0.00123 / 0.01887 +/- 0.00050 | 0.09340 +/- 0.00105 / 0.03097 +/- 0.00052 | 0.09101 +/- 0.00094 / 0.02933 +/- 0.00055 |
| `c7` | 0.11568 +/- 0.00081 / 0.01945 +/- 0.00024 | 0.08901 +/- 0.00064 / 0.03357 +/- 0.00056 | 0.08820 +/- 0.00071 / 0.03097 +/- 0.00061 |
| `c8` | 0.11530 +/- 0.00062 / 0.01980 +/- 0.00028 | 0.08692 +/- 0.00072 / 0.03510 +/- 0.00031 | 0.08418 +/- 0.00064 / 0.03363 +/- 0.00066 |
| `c9` | 0.11646 +/- 0.00032 / 0.01946 +/- 0.00021 | 0.08333 +/- 0.00092 / 0.03871 +/- 0.00074 | 0.08156 +/- 0.00044 / 0.03620 +/- 0.00057 |
| `c10` | 0.11659 +/- 0.00058 / 0.01926 +/- 0.00011 | 0.08119 +/- 0.00056 / 0.04154 +/- 0.00057 | 0.07841 +/- 0.00053 / 0.03815 +/- 0.00032 |
| `c11` | 0.11802 +/- 0.00070 / 0.01911 +/- 0.00031 | 0.08034 +/- 0.00064 / 0.04364 +/- 0.00039 | 0.07795 +/- 0.00090 / 0.03924 +/- 0.00058 |

Source: `results/systematics/20260819/tune_separation.json`.
The class boundaries come from `config/multiplicity_class_boundaries_v1.json`.

## 5. Baryon-to-meson ratio trend

The measured ratio is the Lambda_b balancing yield divided by the B- balancing yield.
The endpoint contrast is the primary trend estimator.

| class | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---:|---:|---:|
| `c1` | 0.18645 +/- 0.00692 | 0.21408 +/- 0.00873 | 0.21624 +/- 0.00765 |
| `c2` | 0.17754 +/- 0.00759 | 0.24007 +/- 0.01051 | 0.20449 +/- 0.00971 |
| `c3` | 0.16980 +/- 0.00527 | 0.24981 +/- 0.00642 | 0.23054 +/- 0.00596 |
| `c4` | 0.17357 +/- 0.00648 | 0.26757 +/- 0.01000 | 0.25888 +/- 0.00900 |
| `c5` | 0.16513 +/- 0.00539 | 0.29705 +/- 0.00809 | 0.29611 +/- 0.00445 |
| `c6` | 0.16058 +/- 0.00423 | 0.33160 +/- 0.00731 | 0.32232 +/- 0.00745 |
| `c7` | 0.16811 +/- 0.00263 | 0.37710 +/- 0.00695 | 0.35114 +/- 0.00828 |
| `c8` | 0.17172 +/- 0.00252 | 0.40377 +/- 0.00499 | 0.39950 +/- 0.00784 |
| `c9` | 0.16712 +/- 0.00195 | 0.46459 +/- 0.01006 | 0.44381 +/- 0.00712 |
| `c10` | 0.16520 +/- 0.00106 | 0.51158 +/- 0.00655 | 0.48653 +/- 0.00615 |
| `c11` | 0.16192 +/- 0.00258 | 0.54317 +/- 0.00590 | 0.50344 +/- 0.01129 |

| tune | `R(c1)` | `R(c11)` | `R(c11) - R(c1)` |
|---|---:|---:|---:|
| MONASH | 0.18645 +/- 0.00692 | 0.16192 +/- 0.00258 | -0.02453 +/- 0.00739 |
| JUNCTIONS | 0.21408 +/- 0.00873 | 0.54317 +/- 0.00590 | +0.32909 +/- 0.01053 |
| CLOSEPACKING | 0.21624 +/- 0.00765 | 0.50344 +/- 0.01129 | +0.28719 +/- 0.01364 |

Source: `results/systematics/20260819/ratio_trend.json`.
`extraction/ratio_trend.py` forms each contrast from two rows and combines their SEMs in quadrature.

MONASH is not flat.
Its ratio decreases by 0.02453 +/- 0.00739, which differs from zero by 3.3 sigma.
Source: `ratio_trend.json`, field `endpoint_contrast_c11_minus_c1.MONASH`.

The straight-line slope is a diagnostic, not the measurement.
The fit uses class index, although the classes have unequal widths in `N_ch`.
Its chi-squared per degree of freedom is 1.41 for MONASH, 8.18 for JUNCTIONS, and 6.49 for CLOSEPACKING.
Source: `ratio_trend.json`, field `weighted_linear_fit_vs_class_index`.

CLOSEPACKING reaches 87.3 percent of the JUNCTIONS endpoint contrast.
This ratio compares 0.28719 with 0.32909 and does not identify a mechanism.
Source: `ratio_trend.json`, field `endpoint_contrast_c11_minus_c1`.

## 6. Tune separations

The two complete tune comparisons show the same multiplicity pattern.
Each cell gives the separation in B-, Lambda_b, and their ratio, with statistical SEMs.

| class | JUNCTIONS - MONASH: B- / Lambda_b / ratio | CLOSEPACKING - MONASH: B- / Lambda_b / ratio |
|---|---:|---:|
| `c1` | -0.00510 +/- 0.00232 / +0.00206 +/- 0.00096 / +0.02763 +/- 0.01114 | -0.00759 +/- 0.00227 / +0.00175 +/- 0.00116 / +0.02979 +/- 0.01032 |
| `c2` | -0.00480 +/- 0.00274 / +0.00583 +/- 0.00126 / +0.06253 +/- 0.01297 | -0.00688 +/- 0.00334 / +0.00160 +/- 0.00127 / +0.02696 +/- 0.01233 |
| `c3` | -0.01398 +/- 0.00143 / +0.00571 +/- 0.00079 / +0.08001 +/- 0.00831 | -0.01596 +/- 0.00151 / +0.00331 +/- 0.00087 / +0.06074 +/- 0.00796 |
| `c4` | -0.01454 +/- 0.00214 / +0.00695 +/- 0.00104 / +0.09400 +/- 0.01192 | -0.01704 +/- 0.00216 / +0.00543 +/- 0.00111 / +0.08531 +/- 0.01109 |
| `c5` | -0.01823 +/- 0.00238 / +0.00977 +/- 0.00085 / +0.13192 +/- 0.00972 | -0.02424 +/- 0.00205 / +0.00790 +/- 0.00061 / +0.13098 +/- 0.00699 |
| `c6` | -0.02412 +/- 0.00162 / +0.01210 +/- 0.00072 / +0.17103 +/- 0.00845 | -0.02652 +/- 0.00155 / +0.01046 +/- 0.00074 / +0.16174 +/- 0.00856 |
| `c7` | -0.02667 +/- 0.00103 / +0.01412 +/- 0.00061 / +0.20898 +/- 0.00743 | -0.02747 +/- 0.00107 / +0.01153 +/- 0.00065 / +0.18303 +/- 0.00868 |
| `c8` | -0.02838 +/- 0.00095 / +0.01530 +/- 0.00042 / +0.23205 +/- 0.00559 | -0.03112 +/- 0.00089 / +0.01383 +/- 0.00072 / +0.22778 +/- 0.00824 |
| `c9` | -0.03313 +/- 0.00097 / +0.01925 +/- 0.00077 / +0.29747 +/- 0.01025 | -0.03490 +/- 0.00055 / +0.01674 +/- 0.00061 / +0.27669 +/- 0.00738 |
| `c10` | -0.03540 +/- 0.00080 / +0.02228 +/- 0.00058 / +0.34638 +/- 0.00663 | -0.03818 +/- 0.00079 / +0.01889 +/- 0.00034 / +0.32133 +/- 0.00624 |
| `c11` | -0.03767 +/- 0.00095 / +0.02453 +/- 0.00050 / +0.38125 +/- 0.00644 | -0.04007 +/- 0.00114 / +0.02013 +/- 0.00065 / +0.34151 +/- 0.01158 |

Source: `results/systematics/20260819/tune_separation.json`.
`extraction/write_tune_separation.py` computes each difference from the two tune rows.

The seven systematic variations preserve the positive JUNCTIONS-minus-MONASH trend separation.
Their values range from +0.23269 to +0.44463.
Source: `results/systematics/20260820/per_class_deltas_seven.json`, recomputed from each variation's endpoint yields.

## 7. Result after systematic uncertainties

The endpoint trend remains positive after the measured systematic sources.

| comparison | contrast difference | statistical SEM | systematic uncertainty | total uncertainty | statistical significance | result significance |
|---|---:|---:|---:|---:|---:|---:|
| JUNCTIONS - MONASH | +0.35362 | 0.01287 | 0.16082 | 0.16134 | 27.5 sigma | 2.19 sigma |
| CLOSEPACKING - MONASH | +0.31172 | 0.01551 | 0.15589 | 0.15666 | 20.1 sigma | 1.99 sigma |

Source: `results/systematics/20260820/verdict.json`, field `trend`.
`extraction/write_verdict.py` combines statistical and systematic uncertainties in quadrature.

The uncertainty-qualified significance is the result.
The statistical-only value of 27.5 sigma overstates the JUNCTIONS comparison by more than one order of magnitude.
The JUNCTIONS systematic uncertainty is about twelve times its statistical SEM.
This measurement is systematics-dominated.

The JUNCTIONS contrast would need a systematic uncertainty of 0.354 to erase its central difference.
The measured sources reach 0.161, or 46 percent of that threshold.
These values come from the same `verdict.json` trend entry.

The one-sigma per-class verdict passes 49 of 72 cells; 35 of 72 clear two sigma.
All six comparisons pass from `c5` through `c11`, and all six integrated comparisons pass.
One B+-minus-B- comparison also passes at `c3`; no comparison passes at `c1`, `c2`, or `c4`.
Source: the 72 rows in `verdict.json`, field `per_class`.

The separation below `c5` is not generally established.
The Lambda_b separation is smaller there, while its combined systematic uncertainty is larger.
Across `c1` through `c4`, those combined systematic uncertainties span 18.75 to 46.18 percent.
Their integrated values span 6.18 to 8.41 percent.
Source: the Lambda_b rows in `results/systematics/20260820/per_class_combination.json`.

S4 remains absent from these totals.
The per-class result remains provisional until the wide-counter variation lands.
No global significance follows from the 49 passing cells because the code does not correct the 72 tests.

## 8. Auxiliary validation results

The species registry fixes a 202-entry axis and binds it to digest `646f310f78126267`.
The current checkout cannot repeat the earlier species validation because the raw fixtures are absent.
Source for the axis and digest: `contracts/species_ordinals_v2.json`.

Decay map v2 splits two species at the 0.1 percent threshold.
The D*+ and D*- branches use fractions 0.6770 and 0.3230 with conjugate daughters.
On corrected MONASH weights, the remaining species-level assignment risk is 0.0017 percent.
The corresponding JUNCTIONS and CLOSEPACKING risks are 0.0012 and 0.0010 percent.
Sources: `contracts/decay_parent_map_v2.json` and `extraction/second_branch_weight.py` applied to each deduplicated central CSV.

The registered split fractions and species count matched the v2 artifact.
The registered total, D* share, and residual estimates missed by overestimating branches that converge on one ground state.
Sources: `docs/MAP_V2_PREREGISTRATION.md`, `evidence/f4_probe/f4b_probe.out`, and the v2 map.

The auxiliary b-baryon checks form a three-level diagnostic ladder.
Raw generator logs test inclusive production without the analysis chain.
Deduplicated species tables test balancing weights before decay mapping.
The decay map then tests redistribution onto selected ground states.
Sources: `evidence/sigmab_raw`, the three deduplicated central CSV files, and the v2 map.

The inclusive unresolved-origin diagnostic has a deliberately limited scope.
It applies no trigger, acceptance, pairing, multiplicity-class, or opposite-sign-minus-same-sign selection.
The inclusive rates and baryon fractions come from pooled counts.
Their uncertainties are SEMs across ten log blocks.

| sector | tune | unresolved rate (%) | measured baryon (%) | inclusive baryon (%) | relative shift (%) |
|---|---|---:|---:|---:|---:|
| charm | MONASH | 0.0847 +/- 0.0003 | 4.6547 +/- 0.0013 | 4.6568 +/- 0.0013 | 0.0451 +/- 0.0008 |
| charm | JUNCTIONS | 1.1530 +/- 0.0009 | 17.8488 +/- 0.0037 | 17.9469 +/- 0.0037 | 0.5497 +/- 0.0019 |
| charm | CLOSEPACKING | 1.1355 +/- 0.0008 | 17.2888 +/- 0.0038 | 17.3774 +/- 0.0036 | 0.5125 +/- 0.0024 |
| beauty | MONASH | 0.0115 +/- 0.0003 | 4.8715 +/- 0.0037 | 4.8721 +/- 0.0037 | 0.0141 +/- 0.0011 |
| beauty | JUNCTIONS | 0.1023 +/- 0.0011 | 32.0174 +/- 0.0115 | 32.0218 +/- 0.0115 | 0.0140 +/- 0.0008 |
| beauty | CLOSEPACKING | 0.0983 +/- 0.0011 | 32.3720 +/- 0.0068 | 32.3766 +/- 0.0068 | 0.0143 +/- 0.0007 |

Sources: `extraction/aggregate_m7.py` and the twenty block logs under `evidence/m7_blocks` and `m7b_blocks`.

The inclusive diagnostic does not bound the pair observable.
The pair-level unresolved-origin result uses the separate `M1` through `M5` partition and belongs outside the `c1` through `c11` budget.

The raw Sigma_b logs preserve a spin-sorted particle-antiparticle asymmetry.
The table uses pooled counts for the central value and the SEM across ten log blocks.

| group | particle count | antiparticle count | asymmetry (%) | block SEM (percentage points) |
|---|---:|---:|---:|---:|
| spin-1/2 Sigma_b | 105089 | 60943 | 26.59 | 0.18 |
| spin-3/2 Sigma*_b | 150309 | 121723 | 10.51 | 0.17 |
| ground-state Lambda_b and Xi_b | 429761 | 422682 | 0.83 | 0.06 |

Source: the ten `evidence/sigmab_raw/sigmab_block_*.log` files.
The earlier charge-ordering claim is withdrawn; the grouped magnitude remains an auxiliary result.

The b-baryon particle-to-antiparticle pattern is advisory.
`extraction/bbaryon_tune_advisory.py` finds JUNCTIONS and CLOSEPACKING at or above MONASH in zero of thirteen weighted species.
The result compares complete tune configurations and does not isolate colour reconnection or another mechanism.
Source: the advisory script applied to the three deduplicated anchor directories.

The repository cannot reproduce the virtual-trigger comparison.
The prior result names `f3_runs/step2/out/f3_virtual_triggers.root`, but that file and its run output are absent.
This document records the validation as unverified debt and quotes none of its table values.

## 9. Scientific figures and machine-readable tables

`results/provenance/figure_acceptance_manifest_v1.json` is the machine-readable
P1-P8 acceptance record. Its current overall status is `blocked`: all eight
roles are candidates, it accepts none, and `results/figures/main/` contains no
scientific figure bytes. Historical prose that calls a render final or signed
off records the state of an external run; it does not override the manifest.

`plotting/run_paper_plots.sh` produces the scientific figure candidates.
Publication closure places accepted bytes in the canonical destination `results/figures/main/`.
Each balancing yield uses `hTrKinematics` for trigger normalization and the ten disjoint blocks for its statistical uncertainty.
Every three-tune canvas compares the complete MONASH, JUNCTIONS, and CLOSEPACKING bundles.

| role | candidate | machine-readable source | current status |
|---|---|---|---|
| P1, shared event classification | current 13.6 TeV raw-spectrum render | common boundary artifact; external sealed raw manifest | candidate; final bytes and receipt absent |
| P2, charm correlations | current MONASH correlation canvas | external central and ten-block pair files | candidate; final bytes, numerical bins, and receipt absent |
| P3, beauty correlations | current MONASH correlation canvas | external central and ten-block pair files | candidate; final bytes, numerical bins, and receipt absent |
| P4, integrated charm yields | `V-INTEGRATED` | `tests/fixtures/integrated_rows_nominal.log` | candidate; source log lacks integer closure rows and final bytes are absent |
| P5, charm yields versus activity | `V-FULL` or `V-EXTREMES` | `results/systematics/20260819/tune_separation.json` | candidate; common-point logs are absent and presentation choice remains |
| P6, integrated beauty yields | `V-INTEGRATED` | `tests/fixtures/integrated_rows_nominal.log` | candidate; source log lacks integer closure rows and final bytes are absent |
| P7, beauty yields versus activity | `V-FULL` or `V-EXTREMES` | `results/systematics/20260819/tune_separation.json` | candidate; common-point logs are absent and presentation choice remains |
| P8, signed baryon/reference-meson ratios | `V-BARYONMESON` | `results/systematics/20260819/ratio_trend.json` for the beauty trend | candidate; charm numerical matrix, final bytes, and receipt absent |

The audit inspected and rejected the available old-paper role files. The old P1 is
14 TeV with an absolute-pseudorapidity limit of 4. The old P2-P7 files use
legacy selections, axes, tune styling, or incomplete uncertainty annotation.
The old P8 is an inclusive-style baryon/meson ratio rather than the signed
registry quantity. The audit reconstructed no scientific point from those images.

Several gaps still block acceptance. The external inputs are inaccessible, the
plotting runner does not record final sidecars, and the derived-uncertainty
formula remains unresolved. S4 class deltas and V-INTEGRATED closure rows are
also absent. The reduction sidecar mislabels v3 pair files as v2, and the
systematic harvest generator rejects its seven committed plotting
configurations. The manifest records each role's retrieval requirement and
candidate digest.

The result JSON files are the publication tables for the trend and verdict.
`ratio_trend.json`, `tune_separation.json`, `per_class_combination.json`, and `verdict.json` carry the values quoted above.

## 10. Limits on interpretation

These results describe generator-level tune comparisons.
The experiment-comparable selection applies branching-fraction weights only.
It includes no detector model, decay kinematics, acceptance, efficiency, resolution, or class migration.

The three tune cards differ across 28 allowed parameters in nine families.
Eight parameters belong to `ColourReconnection`; other families include `StringFlav` and `StringZ`.
Every tune separation in this document is bundle-to-bundle.
The result measures complete tune configurations and asserts no mechanism.
Sources: `config/tune_difference_allowlist_v1.json` and the three nominal tune cards.

The systematic result excludes S4 and assumes the measured source contributions combine in quadrature.
The repository has not tested independence between those sources.
Cross-class and cross-observable covariance also remains unknown.

The b-baryon comparison remains advisory, and the inclusive M7 values do not bound the pair observable.
The missing virtual-trigger output prevents an independent check of that validation.
The missing integrated plotting log prevents an independent check of integer-exact integrated closure.

The final ROOT-rendered scientific outputs and their receipts are external to this repository.
Their compact numerical inputs and validation evidence travel where the audit
manifest classifies them as publication candidates.
