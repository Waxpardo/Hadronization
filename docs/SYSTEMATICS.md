# Systematic uncertainties

This document defines six systematic sources and reports their measured status.
The sources test theory inputs, one generation cut, and conventions chosen by this project.

The current combined values exclude S4.
Therefore, S4's absence makes every total and verdict in this document provisional.

> **RULINGS R9 AND R11 OF 2026-08-23 ARE NOT YET FOLDED INTO THIS TEXT.**
> Two statements below disagree with the executable contract, and the
> contract is authoritative:
>
> - **S3 is measured ONE-SIDED, not two-sided.** `HF_SYS_PTHAT_1` is
>   `included: false` under R9 in `config/systematics_sources_v1.json`
>   (source `S3_pthat`), because the MONASH p80 and p90 quantiles both
>   resolve to `N_ch = 2` and the 80–90 % class would need the empty range
>   [3,2]. `extraction/combine_per_class.py:72` carries the one-element
>   tuple `('HF_SYS_PTHAT_4',)`. S3 is quoted as measured and is never
>   symmetrised.
> - **S5 is EXCLUDED, not a retained exact zero.** `S5_class_migration` is
>   `included: false` under R11, `exclusion_reason` "unresolved;
>   re-derivation on the percentile axis pending". Its structural zero was
>   measured on the RETIRED common absolute axis and does not carry to the
>   v2 percentile axis. `CAMPAIGNLESS_TERMS` is the empty tuple
>   (`extraction/combine_per_class.py:80`), so `combine_cell` adds no S5
>   term at all.
>
> The paused-module status is `docs2/systematics/STATUS.md`; the reactivation
> work list is `docs2/systematics/REACTIVATION.md`.

## Scope, status, and notation

The six sources test distinct choices in the generator and analysis chain.
S1 has separate renormalisation-scale and factorisation-scale components.

| source | kind | varied choice | question | status and axis |
|---|---|---|---|---|
| S1a | theory input | `SigmaProcess:renormMultFac`, 1.0 to 2.0 and 0.5 | How strongly does the leading-order scale for the coupling affect the result? | measured on `c1` through `c11` |
| S1b | theory input | `SigmaProcess:factorMultFac`, 1.0 to 2.0 and 0.5 | How strongly does the factorisation scale affect the initial-state parton flux? | measured on `c1` through `c11` |
| S2 | theory input | `PDF:pSet`, NNPDF2.3 LO to CTEQ6L1 | How strongly does the chosen parton distribution affect the result? | measured on `c1` through `c11` |
| S3 | generation cut | `PhaseSpace:pTHatMin`, 2.0 GeV to 1.0 and 4.0 GeV, **registered two-sided, measured ONE-SIDED under R9** | Does the selected hard-process threshold define the observed result? | measured on `c1` through `c11`, `HF_SYS_PTHAT_4` arm only |
| S4 | analysis convention | event-activity counter, `|η| <= 1` to `|η| <= 4` | Does a wider activity window change class-resolved results? | boundary calibration complete; per-class measurement absent |
| S5 | analysis convention | include the measured decay-daughter bias in class assignment | Does the production decay policy move events between multiplicity classes? | **EXCLUDED under R11**: the exact zero was measured on the retired common absolute axis and awaits re-derivation on the percentile axis |
| S6 | analysis convention | resolve duplicate hard-carrier claimants by two deterministic orderings | How much does the strict unresolved-origin rule suppress the pair yield? | measured separately on `M1` through `M5` |

Generated events do not determine scale and parton-distribution choices.
S1 and S2 vary those external theory inputs.

S3 varies a cut that defines which hard events the generator produces.
It tests a generation choice rather than a theory uncertainty inferred from the sample.

S4, S5, and S6 test conventions that this project chose.
This group exists because the project defined the classifier, decay policy, and ambiguous-ancestry treatment.

A delta is the signed change caused by one variation:

```text
Delta = variation - nominal
SEM(Delta) = sqrt(SEM(variation)^2 + SEM(nominal)^2)
```

A source contribution is non-negative.
The combination uses `max(|Delta|, SEM(Delta))` for each source and multiplicity class.

## Common variation and control design

> **RETIRED PROVENANCE.** The `results/systematics/20260819` artifacts cited in this
> section are `HISTORICAL_PROVENANCE_ONLY` with
> `current_or_publication_use: PROHIBITED` per their
> `RETIREMENT_STATUS.json`. Current successors land under the RUN-N result
> roots.

The generation-dependent method repeats the complete measurement with one setting changed.
It regenerates events, reduces them to pair files, merges central and block products, and repeats extraction and plotting.

The method does not apply a correction factor to nominal events.
Each variation is a separate campaign with independent events and seeds.

`config/systematics_variations_v1.json` registers seven campaigns for S1a, S1b, S2, and S3.
`tools/make_systematic_cards.py --check` confirms that each card changes exactly one setting.

The retained run record reports 2,100 raw files across the seven campaigns.
Each campaign contains 300 files, with 100 files and 10 million events per tune.

The seven external manifests and raw-file unions do not travel with this repository.
This checkout can inspect their retained results but cannot recount the 2,100 raw files.

The producer stores one event weight from `pythia.info.weight()`.
It does not consume PYTHIA's automated scale or parton-distribution variation weights.
Separate S1 and S2 campaigns keep the full event selection and analysis response in the measurement.

Each variation has one tenth of the nominal campaign's exposure.
Each multiplicity class contains only a fraction of those events.
Therefore, the class-resolved variation measurements are statistics-limited.

Each render assigns input files to ten blocks by `canonical_slot % 10`.
It forms the balancing yield inside each block before calculating the standard error across the ten estimators.

The class harvest subtracts the pooled nominal yield from the pooled variation yield.
It combines their standard errors in quadrature because the campaigns use independent events.
The retained render logs do not contain the block yields needed for a block-relative delta.

The first five-campaign artifact contains 720 class and integrated cells.
Only 182 cells clear two `SEM(Delta)`, as recorded in `results/systematics/20260819/per_class_deltas.json`.

The final seven-campaign artifact contains 1,008 cells.
It records 236 cells above two `SEM(Delta)` and 772 below that threshold.

The two-SEM flag only describes precision.
It does not decide whether a source contributes to the combined uncertainty.

The controls check the chain before any delta enters a result.
The committed artifacts record these checks:

- The card generator finds seven variations across three tunes and one changed setting per card.
- The nominal control render reproduces all 144 rows without a disagreement.
- Each variation render contains all 144 expected rows.
- Trigger counts close in all 1,152 recorded rows.
- No pair of distinct variations agrees on all 144 yields.

`docs/SYSTEMATICS_PREREGISTRATION.md` fixes the design before the campaign results.
`git show 4a007f2^:docs/SYSTEMATICS_HARVEST_RUN_RECORD.md` records the execution and its deviations.

## S1: renormalization and factorization scales

> **RETIRED PROVENANCE.** The `results/systematics/20260820` artifacts cited in this
> section are `HISTORICAL_PROVENANCE_ONLY` with
> `current_or_publication_use: PROHIBITED` per their
> `RETIREMENT_STATUS.json`. Current successors land under the RUN-N result
> roots.

S1 varies both scales independently by factors of two and one half.
`config/systematics_variations_v1.json` records this leading-order two-point convention.

Independent variations separate the coupling-scale response from the parton-flux response.
They also expose the relation between factorisation scale and the S2 parton distribution.

The integrated charm `D+`-`D-` balancing yield shows the relative scale of both components.
The values below come from `results/systematics/20260820/per_class_deltas_seven.json`.

| variation | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---:|---:|---:|
| S1a, renormalisation ×2 | -0.000160 ± 0.000271 | -0.000123 ± 0.000396 | -0.000583 ± 0.000355 |
| S1a, renormalisation ×0.5 | -0.000245 ± 0.000414 | -0.000424 ± 0.000327 | -0.001034 ± 0.000239 |
| S1b, factorisation ×2 | +0.002109 ± 0.000363 | -0.001317 ± 0.000444 | -0.001599 ± 0.000283 |
| S1b, factorisation ×0.5 | -0.002308 ± 0.000322 | +0.002498 ± 0.000428 | +0.002607 ± 0.000229 |

The factorisation variations move this integrated observable more than the renormalisation variations.
The measured result reverses the registered expectation that S1a would dominate S1b.

The S1b decomposition response is two-sided in all 11 comparable category cells.
The two variations have opposite signs in every one of those cells.

Among resolved categories, the ×0.5 magnitude is 1.245 to 1.829 times the ×2 magnitude.
The two `kMultiplyHeavy` exceptions are `LOW-STAT` and do not resolve that asymmetry.

The class and integrated combination selects the larger magnitude in each cell.
It selects S1a ×0.5 in 80 cells and ×2 in 64 cells.
It selects S1b ×0.5 in 81 cells and ×2 in 63 cells.

`results/systematics/20260820/PER_CATEGORY_FINAL_TWO.md` contains the S1b category table.
`results/systematics/20260820/per_class_combination.json` records every class-resolved selection.

## S2: parton distribution

> **RETIRED PROVENANCE.** The `results/systematics/20260820` artifacts cited in this
> section are `HISTORICAL_PROVENANCE_ONLY` with
> `current_or_publication_use: PROHIBITED` per their
> `RETIREMENT_STATUS.json`. Current successors land under the RUN-N result
> roots.

S2 changes `PDF:pSet` from 13 to 8.
The settings identify NNPDF2.3 QCD+QED LO as nominal and CTEQ6L1 as the variation.

`config/systematics_variations_v1.json` records the reason for this choice.
The two sets have similar `alpha_s(M_Z)`, so the variation primarily tests parton-distribution shape.

The largest resolved decomposition shifts are -1.2749%, +1.2494%, and +2.2649% for the three tunes.
All three values occur in `kExcludedExcited` in `results/systematics/20260820/per_category_final_two.json`.

The class and integrated S2 artifact clears two `SEM(Delta)` in 22 of 144 cells.
The integrated charm `D+`-`D-` shifts are +0.000993, +0.000300, and +0.000647 across the three tunes.

S2 is small on the category partition but can be large for a derived quantity.
For example, it supplies a 36.03% contribution to the CLOSEPACKING-minus-MONASH trend uncertainty.

S1b and S2 both alter the initial-state parton flux.
The combination compares them per quantity and drops the smaller contribution when both are non-negligible.

## S3: hard-process threshold

S3 varies `PhaseSpace:pTHatMin` around the nominal 2.0 GeV cut.
The two variations use 1.0 GeV and 4.0 GeV, which are factor-two changes.

The production cut selects the hard-scattering sample rather than correcting it afterward.
S3 asks whether the balancing observable remains stable after this generation choice changes.

The PYTHIA 8.317 scan measured `dN_ch/dη = 4.973` at 1.0 GeV.
That sample was 28.6% below the minimum-bias value.

The scan measured `dN_ch/dη = 10.492` at 4.0 GeV.
That sample was 50.6% above the minimum-bias value.

The project selected the nominal 2.0 GeV point because its activity was close to minimum bias.
The configuration records both adjacent scan points and their relation to that choice.

The integrated charm `D+`-`D-` result shows a strong, opposite-signed response:

| variation | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---:|---:|---:|
| 1.0 GeV | -0.007380 ± 0.000365 | -0.006413 ± 0.000274 | -0.004855 ± 0.000344 |
| 4.0 GeV | +0.009600 ± 0.000358 | +0.010396 ± 0.000498 | +0.009153 ± 0.000423 |

The 1.0 GeV variation clears two `SEM(Delta)` in 41 of 144 cells.
The 4.0 GeV variation clears that threshold in 69 cells.

The class and integrated combination selects 4.0 GeV in 92 cells and 1.0 GeV in 52 cells.
Therefore, neither variation can replace the required per-cell selection.

## S4: event-activity counter window

> **RETIRED PROVENANCE.** The `results/systematics/20260820` artifacts cited in this
> section are `HISTORICAL_PROVENANCE_ONLY` with
> `current_or_publication_use: PROHIBITED` per their
> `RETIREMENT_STATUS.json`. Current successors land under the RUN-N result
> roots.

S4 changes the operational final-charged-non-heavy event-activity counter from `|η| <= 1` to `|η| <= 4`.
The raw schema stores both counters for every event.

Both counters use the same `isFinal && isCharged && !hasHeavyConstituent && pT > 0.15` rule.
Only the pseudorapidity window changes.

The project chose the narrow counter as its activity classifier.
S4 tests whether that convention makes the class-resolved balancing yield sensitive to local activity fluctuations.

The variation keeps the MONASH minimum-bias percentiles fixed.
It maps each narrow boundary to a half-integer wide boundary at the same percentile.

Stage 1 produced `results/systematics/20260820/s4/s4_wide_boundaries_v1.json`.
Fresh narrow distributions reproduced all three committed minimum-bias anchors bin for bin.

The wide axis has a maximum cross-tune percentile residual of 3.537 percentage points.
The narrow axis has 2.912 percentage points, so the wide axis is 1.21 times worse by this measure.

This residual compares class labels, not the balancing-yield shift.
It does not supply an S4 uncertainty.

The declared per-class work has not run.
It needs 100 nominal files per tune for both the wide classifier and a narrow-classifier control.
It then needs both merges and the class-resolved render.

The configuration registers S4, but every combined value in this document excludes it.
The current systematic budget and every verdict that uses it are provisional until S4 lands.

## S5: decay-daughter class migration

S5 tests the class effect of keeping heavy hadrons stable during production.
An experimental primary definition counts some heavy-hadron decay daughters, so the production counter undercounts activity.

The PYTHIA 8.317 calibration measured a 0.7670% bias.
`results/validation/generator/NCH_DECAY_POLICY_BIAS_8317.md` records 200,000 events per convention and one shared seed.

The S5 tool divides every class boundary by `1 + delta` and `1 - delta`.
It then compares the selected integer `N_ch` values with the nominal selection.

No shifted half-integer boundary crosses an integer.
Both transformations therefore select exactly the same events in every multiplicity class.

S5 is exactly zero in all 11 classes and all three tunes.
Its block standard errors are also exactly zero because the class-selection operator does not change.

The tightest boundary needs a 1.5385% relative shift before it crosses an integer.
That margin is 2.01 times the measured bias.

The exact zero applies only to the current boundaries and the measured minimum-bias bias.
A boundary above 65.2 would not inherit this result.

The calibration used MONASH minimum-bias events.
No artifact measures the corresponding bias in the forced hard-heavy-flavour sample.

S5 also does not correct the percentile labels for decay daughters.
It establishes unchanged class membership, not unchanged experimental labels.

## S6: pair-level unresolved origin

S6 tests how ambiguous hard ancestry affects pair-level yields.
The strict production rule demotes every duplicate hard-carrier claimant to `kUnresolved`.

`config/a2_variations_v1.json` registers two deterministic alternatives.
One restores the claimant with the smallest `heavyIndex`; the other restores the largest.

The quoted source is the larger result in each class across those two extremal orderings.
It is not an envelope over all possible ancestry rules.

The larger-index result is larger in every JUNCTIONS and CLOSEPACKING class:

| tune | M1 | M2 | M3 | M4 | M5 |
|---|---:|---:|---:|---:|---:|
| MONASH | 0.0004 ± 0.0002 | 0.0011 ± 0.0004 | -0.0003 ± 0.0006 | 0.0017 ± 0.0012 | 0.0037 ± 0.0037 |
| JUNCTIONS | 0.0255 ± 0.0024 | 0.0691 ± 0.0029 | 0.1007 ± 0.0094 | 0.1509 ± 0.0196 | 0.1369 ± 0.0215 |
| CLOSEPACKING | 0.0377 ± 0.0019 | 0.1012 ± 0.0049 | 0.1571 ± 0.0130 | 0.1777 ± 0.0183 | 0.2293 ± 0.0319 |

The values come from `largest_MONASH.txt`, `largest_JUNCTIONS.txt`, and `largest_CLOSEPACKING.txt` in `results/a2/20260813/results/tiebreak_robustness/`.
The smallest-index and largest-index results differ by factors from 2.0 to 5.5
across the ten JUNCTIONS and CLOSEPACKING bundle classes.

Report S6 per multiplicity class.
The integrated JUNCTIONS value is 0.0583%, while its largest class value is 0.1509%, a factor of 2.6 larger.

The integrated CLOSEPACKING value is 0.0795%.
Its largest class value is 0.2293%, a factor of 2.9 larger.

The S6 axis differs from the production class axis.
`M1` through `M5` cover `N_ch` ranges 1-9, 10-19, 20-29, 30-39, and 40 or more.

The `c1` through `c11` quadrature excludes S6.
A sum across different partitions would combine quantities that do not refer to the same event classes.

## Source selection and combination

> **RETIRED PROVENANCE.** The `results/systematics/20260820` artifacts cited in this
> section are `HISTORICAL_PROVENANCE_ONLY` with
> `current_or_publication_use: PROHIBITED` per their
> `RETIREMENT_STATUS.json`. Current successors land under the RUN-N result
> roots. The 107 / 30 / 7 cell counts below describe
> `results/systematics/20260820` and carry the same status.

Two-sided sources select the variation with the larger `|Delta|` in each class.
The method does not use half the variation spread and does not call two points an envelope.

Each selected source contributes:

```text
u_s(c) = max(|Delta_s(c)|, SEM(Delta_s(c)))
```

The standard error is a floor because a noisy small delta does not establish that the source has no effect.
The continuous maximum also avoids a jump at the two-SEM reporting threshold.

The per-class combination applies a special S1b-S2 rule.
It drops S2 in 107 cells, drops S1b in 30 cells, and drops neither in seven cells.

The current sum contains S1a, the one-sided S3, and the retained S1b and S2 terms. It contains NO S5 term: R11 removed it, and `CAMPAIGNLESS_TERMS` is the empty tuple.
It can retain both S1b and S2 when the special drop rule does not apply.

The sum excludes S4 because no per-class delta exists.
It excludes S6 because its partition differs.

The tune spread is the measured comparison and is not a systematic source.
No tune-difference term enters this budget.

The retained contributions combine in quadrature:

```text
systematic(c) = sqrt(sum_s u_s(c)^2)
```

Quadrature assumes independence between the retained sources.
The project has not tested that independence.

The S1b-S2 rule handles one known overlap but does not establish independence elsewhere.
The unmeasured source correlations limit every combined value.

## Effect on tune separations and trend

> **RETIRED PROVENANCE.** The `results/systematics/20260820` artifacts cited in this
> section are `HISTORICAL_PROVENANCE_ONLY` with
> `current_or_publication_use: PROHIBITED` per their
> `RETIREMENT_STATUS.json`. Current successors land under the RUN-N result
> roots.

The code recomputes each tune separation and trend inside every variation render.
It then subtracts the corresponding nominal derived quantity before source selection.

This order retains cancellations shared by two tunes or two multiplicity classes.
It avoids borrowing one tune's uncertainty for a difference between tunes.

The committed provisional verdict contains 72 class and integrated comparisons.
It reports 49 comparisons larger than their combined statistical and systematic uncertainty.

The following trend values also use the provisional budget without S4 or S6:

| quantity | value | statistical SEM | systematic | total | `|value| / total` |
|---|---:|---:|---:|---:|---:|
| JUNCTIONS minus MONASH trend | +0.35362 | 0.01287 | 0.16082 | 0.16134 | 2.19 |
| CLOSEPACKING minus MONASH trend | +0.31172 | 0.01551 | 0.15589 | 0.15666 | 1.99 |

These numbers come from `results/systematics/20260820/verdict.json`.
Under the current quadrature rule, any nonzero S4 contribution would increase these totals.

The quoted sigma values are per-cell and uncorrected across the 72 comparisons.
No global significance follows from them.

The 2026-08-21 correction brings the derived combiner into the documented
two-SEM rule. `results/systematics/20260820/verdict.json` schema v2 records the
variation SEM, nominal SEM, combined SEM, and contribution for every selected
term. The correction changes four of 77 two-sigma classifications while leaving
central values and all one-sigma classifications unchanged.

## Coverage limits and evidence index

> **RETIRED PROVENANCE.** The `results/systematics/20260819` and
> `results/systematics/20260820` artifacts cited in this
> section are `HISTORICAL_PROVENANCE_ONLY` with
> `current_or_publication_use: PROHIBITED` per their
> `RETIREMENT_STATUS.json`. Current successors land under the RUN-N result
> roots. The evidence table below is an
> index of how each retired artifact was produced, and stays as written.

The evidence for each source remains separate from this summary.

| source | definition and method | result artifacts |
|---|---|---|
| S1-S3 | `config/systematics_variations_v1.json`; `extraction/systematics_delta.py` | `results/systematics/20260819/`; `results/systematics/20260820/` |
| S4 | `git show 4a007f2^:docs/SYSTEMATICS_HARVEST_RUN_RECORD.md` sections 25-27 | `results/systematics/20260820/s4/` |
| S5 | `git show b1c4c12^:tools/systematic_class_migration.py` | `git show b1c4c12^:results/systematics/20260817/s5_class_migration.json` |
| S6 | `config/a2_variations_v1.json`; `analysis/a2_block_shift.py` | `results/a2/20260813/results/` |
| combination | `extraction/combine_per_class.py`; `extraction/combine_derived.py` | `results/systematics/20260820/per_class_combination.json`; `verdict.json` |

The current coverage has five material limits.

- S4 has no class-resolved delta and remains outside every total.
- The retained variation raw files and manifests are external, so this checkout cannot reproduce their 2,100-file count.
- S5 does not measure decay-daughter bias in the forced hard-heavy-flavour sample.
- S6 uses a different multiplicity partition and cannot enter the class budget.
- Quadrature assumes untested independence between systematic sources.

These sources cover generator and analysis choices only.
They do not include detector acceptance, efficiency, resolution, or unfolding uncertainties.
