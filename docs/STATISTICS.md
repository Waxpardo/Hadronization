# Statistical estimators

This document defines the estimators that connect merged counts to published values and uncertainties.
The cited code and machine-readable artifacts fix each definition.

## Quantities and units

The analysis reports six statistical quantity types.

| quantity | definition | unit |
|---|---|---|
| count | A histogram sum, such as `N_OS`, `N_SS`, or `N_trig` | entries |
| fraction | One selected count divided by a complete count | unitless or percent |
| balancing yield | `(N_OS - N_SS) / N_trig` | per trigger |
| yield ratio | One balancing yield divided by a reference balancing yield | unitless |
| relative delta | A variation shift divided by its nominal value | percent |
| absolute difference | One estimator minus an independent estimator | the estimator's unit |

The plotter emits counts, balancing yields, and yield ratios in its `UNCERTAINTY_MATRIX` rows.
The implementations are `plotting/improvedPlotting_THnSparse.C` and `extraction/harvest_yield_deltas.py`.

Species and category fractions use extracted weighted counts.
The script `extraction/decompose_with_block_sems.py` calculates these fractions and reports percent.

The symbol `SEM` means the standard error of the mean across block estimators.
It does not mean a native ROOT projection error.

## Pooled central estimators

The complete union of selected input files supplies every published central value.
The central balancing yield is

\[
Y=\frac{\sum N_{\mathrm{OS}}-\sum N_{\mathrm{SS}}}
        {\sum N_{\mathrm{trig}}}.
\]

The plotter calculates this value once from the central merged histograms.
Its implementation is `calculateOneYield` in `plotting/improvedPlotting_THnSparse.C`.

A pooled fraction divides the summed category count by the summed total count.
The decomposition script reports this value as `pooled` beside the block mean.

A pooled yield ratio divides two central balancing yields.
The plotter reports the reference yield and the ratio's block standard error in the same row.

The pooled ratio is not the unweighted mean of the ten block ratios.
Unequal block denominators give the two estimators different weights and potentially different values.

Block means remain diagnostics for imbalance and estimator checks.
They do not replace the full-union central value.
`extraction/decompose_with_block_sems.py` prints both values and their difference in standard-error units.

Multiplicity integration follows the same rule.
The integrated configuration selects the full multiplicity range, then calculates one pooled ratio from those selected counts.
The pre-registration record, recoverable with `git show 4a007f2^:docs/V_INTEGRATED_PREREGISTRATION.md`, records this calculation and its block coverage.

## Ten-block uncertainty design

The canonical sample uses ten deterministic blocks of complete input files.
`tools/build_canonical_manifest.py` assigns each row by `canonical_slot % 10` before analysis.

Normal canonical analysis processes all events in each assigned file.
Its event-modulo filter has `modulo = 0` and `remainder = -1` by default.
`analysis/run_status_analysis.sh` implements this default and the separate Gate-D pilot mode.

The published blocks are not event-modulo subsets.
The Gate-D pilot alone accepts `event_id % 10 == remainder` within each file.

File blocking keeps every job's events together.
A seed family, host effect, or tune-initialization effect therefore contributes to between-block scatter.
This scatter increases the reported standard error when such a job-level effect exists.

Event-modulo blocking would distribute each job-level effect across all blocks.
That distribution would reduce the apparent block scatter without removing the effect.
File blocking is therefore conservative against effects shared within a job.

For `K = 10` finite block estimates, the analysis calculates

\[
\bar{x}=\frac{1}{K}\sum_{k=1}^{K}x_k,
\qquad
s^2=\frac{1}{K-1}\sum_{k=1}^{K}(x_k-\bar{x})^2,
\qquad
\operatorname{SEM}(x)=\frac{s}{\sqrt{K}}.
\]

The sample standard deviation has nine degrees of freedom.
`calculateSubsampleStatistics` in `plotting/improvedPlotting_THnSparse.C` implements these equations.

Each block repeats the complete estimator on a disjoint input-file subset.
The ten results measure the estimator's observed between-block spread.

Under a normal-sampling approximation, nine degrees of freedom give about 24 percent relative uncertainty on the reported standard error.
This value follows from `1 / sqrt(2 * 9)` and the degrees of freedom above.

## Nonlinear observables and covariance

The analysis forms each nonlinear quantity inside every block before calculating its standard error.
This order retains covariance created by shared events and counts.

Each block first calculates its balancing yield from its own OS, SS, and trigger counts.
The OS-minus-SS subtraction therefore precedes every yield error calculation.

This order retains the covariance between the two sign counters.
The analysis does not propagate separate OS and SS histogram errors into the balancing-yield error.

Each block also divides its baryon yield by its own reference-meson yield.
The ratio's standard error comes from the ten resulting ratios.
`extraction/combine_per_class.py` reads this `ratio_sem` instead of propagating two yield errors.

The integrated observable follows the same order inside each block.
It integrates the selected counts, forms one yield or ratio, and then enters that block value into the standard-error calculation.

Native ROOT projection errors do not supply published error bars.
The plotter replaces final correlation-bin errors with block standard errors and stores yield standard errors from block values.

The repository has not measured cross-class or cross-observable covariance.
Consequently, endpoint contrasts and combined plots do not include measured covariance terms.

Within one tune, multiplicity classes contain disjoint event sets.
Their shared file-block construction could still correlate the class estimators.

If that correlation is positive, quadrature overstates the variance of a class difference.
This statement is conditional because the repository has not measured the covariance.

## Differences between independent campaigns

Separate tune and variation campaigns use independent generated events and seeds.
Same-numbered blocks therefore provide labels, not paired events.

For independent estimates `A` and `B`, the analysis uses

\[
\Delta=A-B,
\qquad
\operatorname{SEM}(\Delta)=
\sqrt{\operatorname{SEM}(A)^2+\operatorname{SEM}(B)^2}.
\]

Tune separations use this equation for yields, ratios, contrasts, and slopes.
The implementations are `extraction/combine_per_class.py`, `extraction/ratio_trend.py`, and `extraction/write_verdict.py`.

The class-resolved variation harvest defines `Delta = variation - nominal`.
`extraction/harvest_yield_deltas.py` adds the independent nominal and variation standard errors in quadrature.

The derived-combination code calculates each systematic on the difference itself.
Each variation recomputes the complete derived quantity before comparison with nominal.
`extraction/combine_derived.py` therefore retains cancellations that occur inside the derived quantity.

## Systematic delta estimators

The registered category estimator forms a relative delta inside every block.
For variation `v`, nominal `n`, and block `k`, it is

\[
D_k=100\,\frac{Y_{v,k}-Y_{n,k}}{Y_{n,k}}.
\]

The reported `D` is the mean of the ten `D_k` values.
Its standard error is the sample standard deviation of those values divided by `sqrt(10)`.
`extraction/systematics_delta.py` implements this registered estimator.

The means-first relative form is a cross-check.
It first calculates the variation and nominal means, then divides their difference by the nominal mean.
Its propagated standard error treats the two campaign means as independent.

The class-resolved harvest has only each row's central value and standard error.
Its committed logs do not retain the ten block yields needed for `D_k`.

That harvest therefore uses the absolute means-first difference from the preceding section.
It reports a relative shift beside the difference when the nominal value is nonzero.
`results/systematics/20260820/per_class_deltas_seven.json` records this estimator's outputs.

The two delta estimators are not algebraically equivalent when block denominators differ.
The class-resolved artifact does not verify the registered block-relative estimator.

Each included source contributes

\[
u_s=\max\left(|\Delta_s|,\operatorname{SEM}(\Delta_s)\right)
\]

in each compatible class.
A shift smaller than its standard error has not established that the source effect is zero.
The standard error therefore supplies a floor.

This maximum is continuous at `|Delta| = SEM(Delta)`.
It avoids a discontinuous contribution when a presentational significance flag changes state.
`extraction/systematics_delta.py` implements the rule without consulting its two-standard-error flag.

## Sparse classes and coverage rules

A finite zero-yield block is a measured zero and remains in the block sample.
The estimator retains that block because its removal would raise the block mean.

A zero denominator is different from a zero numerator.
It makes a ratio undefined, so the code returns no finite ratio for that block.

Final class-resolved points require ten finite yield estimates.
Ratios also require ten finite ratios and a nonzero central reference yield.
`EvaluateSubsampleTechnicalCoverage` in `plotting/improvedPlotting_THnSparse.C` enforces these requirements.

A missing or non-finite block does not reduce the denominator of the standard error silently.
The coverage check rejects any final row whose finite count differs from ten.

The systematics registration marks a class `LOW-STAT` below 1,000 weighted pairs in a nominal block.
The registration reports such a class but excludes it from its per-class-versus-integrated flatness verdict.
`docs/SYSTEMATICS_PREREGISTRATION.md` defines this reporting threshold.

Final plotted points retain their measured block error bars.
The plotter rejects a required point with an invalid error or a nonzero value with zero standard error.

An explicit multiplicity scope defines exceptions; observed emptiness does not define them after inspection.
The reduced configuration restricts `B_c` observables to the integrated and highest multiplicity bins.

The plotter treats other `B_c` bins as outside the declared observable.
`plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json` records this scope, and the plotter enforces it.

## Trend summaries and fit diagnostics

The endpoint contrast is the primary trend estimator:

\[
C=R(c11)-R(c1).
\]

This central estimator imposes no curve model.
It subtracts two rows and uses quadrature because no measurement supplies their covariance.

Class `c1` is the lowest-activity percentile class, and `c11` is the highest.
`config/multiplicity_percentile_classes_v2.json` fixes this direction while
each tune supplies its own absolute thresholds.

The diagnostic fit uses a weighted straight line in class index.
It assigns indices one through eleven and weights each ratio by the inverse squared standard error.
`extraction/write_ratio_trend.py` and `extraction/ratio_trend.py` implement the fit.

The fit reports slope, slope standard error, intercept, chi-square, and degrees of freedom.
Its chi-square per degree of freedom measures whether a straight line fairly summarizes the points.

Class index is a convention, not a physical multiplicity coordinate.
The classes can have unequal widths in `N_ch`, and the highest class has no
finite upper boundary; the absolute widths are tune-dependent.

A slope per class is therefore not a physical derivative `d(ratio)/dN_ch`.
The artifact `results/systematics/20260819/ratio_trend.json` records both the endpoint and fit summaries.

## Closure and integrity checks

Exact extracted-count closure establishes accounting by addition.
The extractor requires each central count to equal the ten-block sum exactly.

The ROOT closure checks object contents and stored `Sumw2` values within its fixed merge tolerance.
It also checks additive and invariant metadata.
`Validation/validate_pair_block_closure.sh` implements these checks.
The committed closure receipts under `evidence/closure_v3_verdicts/` record successful comparisons.

The closure driver requires the expected pair-object schema from its caller.
It derives the required comparison counts for that schema and checks the emitted summary exactly.

This schema requirement closes a specific false-pass route.
A run against the wrong schema could otherwise report internally consistent but different comparison counts.

Exact block closure does not prove that stored entries are unique.
A duplicate entry in the central and corresponding block leaves the equality unchanged.

The E5 regression demonstrates this limit with trigger-owned objects repeated across pair files.
`tests/test_closure_trigger_deduplication.py` shows that both replicated and deduplicated views pass block addition.

Closure therefore establishes exact addition, not uniqueness.
Object ownership rules, deduplication, and plausibility checks must establish uniqueness separately.

The class harvest also checks that block trigger counts account for the central trigger count.
It applies a bound when text formatting rounds large counts.
`extraction/harvest_yield_deltas.py` implements this check.

These integrity checks license the estimator inputs.
They do not replace the empirical standard error or establish a probability model.

## Combination, reporting, and inferential limits

Compatible systematic sources combine in quadrature:

\[
u_{\mathrm{syst}}=\sqrt{\sum_s u_s^2}.
\]

For factorization scale and parton distribution, the code applies a correlated-source rule.
If both effects are non-negligible, it keeps the larger and drops the other from the sum.

The S6 unresolved-origin result uses the `M1` through `M5` partition.
It does not use the `c1` through `c11` partition.

The code reports S6 separately and refuses to add it to a per-class quadrature sum.
Different partitions do not define addable cells.

The tune-bundle spread is not a systematic source.
It does not enter the uncertainty budget in `results/systematics/20260820/per_class_combination.json` or `verdict.json`.

The total reported uncertainty combines statistical and included systematic terms:

\[
u_{\mathrm{total}}=\sqrt{u_{\mathrm{stat}}^2+u_{\mathrm{syst}}^2}.
\]

`extraction/combine_derived.py` calculates this total for each verdict.

Quadrature across systematic sources assumes their independence after the explicit factorization-scale and parton-distribution rule.
The repository has not tested that remaining independence assumption.

Machine-readable JSON retains the calculation values.
The Markdown writers round only their displayed tables, as `extraction/write_verdict.py` and `extraction/write_ratio_trend.py` show.

The final verdict contains 72 per-cell comparisons.
The length of `per_class` in `results/systematics/20260820/verdict.json` establishes this count.

Quoted sigma values apply to individual cells and have no correction across those 72 comparisons.
The repository claims no global significance or trial-corrected probability.

Cross-class and cross-observable covariance remains unmeasured.
Systematic-source independence also remains untested.
These limits apply to every combined or trend-level interpretation.
