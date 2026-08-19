# THnSparse plotting contract

This document records the implementation-level contract for
`PlottingScripts/improvedPlotting_THnSparse.C`. The operational overview is in
[`PlottingScripts/README.md`](PlottingScripts/README.md), and the full
reproduction sequence is in [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

Paul Veen's grouped-trigger, per-canvas, multi-tune architecture remains the
baseline. New code validates and adapts inputs; it does not replace the
observable with a parallel plotting pipeline.

## Entry points and configurations

Full paper selection:

```bash
./PlottingScripts/run_paper_plots.sh thnsparse
```

Reduced validation selection:

```bash
./PlottingScripts/run_paper_plots.sh thnsparse-complete-root
```

Configs:

```text
PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json
PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json
```

Both use:

```json
"calculate_errors": true,
"nSubSamples": 10
```

“Complete root” identifies the full-union central-value source. It does not
mean “without subsampling errors.” The reduced config keeps B+/D+ trigger
groups, the signed reference mesons, Lambda-b/Lambda-c associates, all three
tunes, and the 1--10% class. Its 16 mini canvases feed two global canvases.
Sigma-b and duplicate standalone canvases are intentionally absent. All 11
ordered activity definitions remain in the config so boundary freezing still
tests the full partition. The reduced config has the same `TriggerToUse`
schema, scientific selection, and SEM prescription as the full config.

## Path resolution

Checked-in paths are checkout-relative:

```json
"base_dir": "AnalyzedData",
"bb_bar_complete_root_dir": "complete_root_21_06_2026",
"cc_bar_complete_root_dir": "complete_root_21_06_2026",
"bb_bar_complete_root_dir_sub_samples": "AnalyzedData/SUBSAMPLES_700/combined_root_subSamples",
"cc_bar_complete_root_dir_sub_samples": "AnalyzedData/SUBSAMPLES_700/combined_root_subSamples"
```

The resolver accepts:

```text
AnalyzedData/complete_root_<TAG>_<TUNE>/<PAIR>.root
AnalyzedData/<TUNE>/complete_root_<TAG>_<TUNE>/<PAIR>.root
AnalyzedData/<TUNE>/complete_root_<TAG>/<PAIR>.root
```

Relative paths resolve from `HADRONIZATION_BASE`, or from the checkout when
unset. Absolute paths are allowed only as explicit private overrides; no
checked-in paper config requires `/Users/...` or a username-specific
`/data/...` path.

`config/dataset_selector.json` controls the active raw, analyzed, complete
root, and block roots:

```bash
python3 tools/dataset_selector.py validate
python3 tools/dataset_selector.py show
python3 tools/dataset_selector.py shell
```

`run_paper_plots.sh` evaluates the shell form. It exports the selected
publication-eligibility flag, canonical manifest, production root, analysis
root, raw base, analyzed-data base, complete-root tag, and block base.
Missing legacy-only fields are empty, not the text `None`. All plotting
consumers therefore resolve the same dataset rather than independently
guessing paths.

The current checked-in selector is `legacy_21_06_2026` with
`status: legacy_regression_default`. On canonical Nikhef it resolves to:

```text
/data/alice/ipardoza/Hadronization/AnalyzedData/complete_root_21_06_2026_<TUNE>
/data/alice/ipardoza/Hadronization/AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_<TUNE>
```

It is not raw-v5 and cannot support new-selector claims. A new
`canonical_candidate` selector entry is switched after manifest freeze/seal,
one-pass analysis, central/block merging, and validation. It remains
publication-ineligible while boundary, origin, robustness, plot, and human
review evidence is generated. Only the exact final scientific-review and
project-owner authorization can promote the row to `canonical`; candidate
figures must be regenerated afterward.
This active legacy row has `publication_eligible: false`; canonical paper
targets fail closed and direct users to the explicit `legacy-regression`
target.
The checked-in full and reduced/smoke configs are metadata-v2, ordered-pair,
factor-one contracts and therefore cannot be run against that selector.
Legacy-regression plots preserve the historical factor-one-half convention
only for comparison and are not promotable.

In canonical mode, `Plot_InclusiveKinematicSpectra_Raw.C` consumes only the
sealed canonical-manifest rows. It verifies the bound summary, raw-validation
receipt, seal, raw file size, unique contiguous slots, and ten equal
`canonical_slot % 10` blocks. It accepts an equal-tune final exposure
`N >= 100` with `N % 10 == 0`, so a reviewed expansion is not truncated to
the 100-file/tune first stage. It never recursively discovers unlisted reserve
files, and it requires every selected file's size and SHA-256 to match the
sealed row. Recursive discovery is retained only under the explicit
`legacy_recursive_diagnostic` mode.

The THnSparse validator and multiplicity-boundary macro honor
`HADRONIZATION_ANALYZED_DATA_BASE` and
`HADRONIZATION_COMPLETE_ROOT_TAG`. Canonical merged directories must carry
the immutable all-tune source manifest: `3*N` rows centrally and `3*N/10`
rows in each block. Their provenance binds the full bytes and the explicit
selected-tune filter. The 300 ROOT files in every merged directory are the
fixed signed pair registry, not a requirement that the final raw manifest
contain 300 rows.

## Pair-file schema

Every configured OS and SS file must contain:

| Object | ROOT type | Meaning |
|---|---|---|
| `summed MULTIPLICITY` | `TH1D` | all successful input events |
| `hTrKinematics` | `THnSparseD` | eligible triggers |
| `hAsKinematics` | `THnSparseD` | pair-conditioned associates |
| `hCorrelations` | `THnSparseD` | ordered accepted pairs |

New pair files have analysis schema
`paul_pair_objects_primary_ground_v2`, raw schema
`hf_primary_ground_raw_v5`, and selector
`hard_trigger_primary_ground__primary_ground_associate_v1`.

`hAsKinematics` is not an inclusive single-particle spectrum.

## Exactly-once pT/eta selection

Both configs contain `pair_input_selection_contract` with mode:

```text
v2_metadata_or_tagged_legacy_recuts_v1
```

The decision for each central and block file is:

### Metadata v2

Require the complete metadata set and exact values:

```text
trigger pT min exclusive     1.0 GeV/c
associate pT min exclusive   0.15 GeV/c
trigger |eta| max inclusive  4
associate |eta| max inclusive 4
upper-pT selection           none
```

The pT/eta cuts were applied upstream by
`status_analysis_THnSparse_qq.C`. The plotter validates metadata and does not
re-cut these axes. It applies the requested multiplicity projection only.

### Tagged metadata-free legacy input

Only a metadata-free file whose complete-root tag exactly equals:

```text
complete_root_21_06_2026
```

may be read, and only when the standalone `legacy-regression` target derives
its explicit `tagged_legacy_recuts_only_v1`,
`legacy_identical_ss_half_v1`, factor-`0.5` diagnostic config. Matching Paul’s
stable main, the configured trigger and associate pT/eta cuts are applied to
the correlation numerator, and the configured trigger cuts are applied to the
trigger-normalization denominator. The checked-in factor-one paper configs
reject the same metadata-free files. The canonical metadata-v2 path is
unchanged by this diagnostic. This keeps the old Paul result reproducible
without allowing arbitrary unversioned input or silently changing its
definition.

### Rejected inputs

The macro rejects:

- partial metadata;
- a mixture of metadata-v2 and legacy fallback within one result;
- thresholds or inclusivity that differ from the config contract;
- any trigger/associate upper-pT selection;
- an untagged metadata-free file;
- unsupported individual phi recuts;
- central/block selection-provenance disagreement.

The executable regression is `Validation/TestPlotProjectionCuts.C`.

## Grouped triggers and canvas selection

`beauty_correlations_to_analyse` and
`charm_correlations_to_analyse` contain trigger groups. Each group declares
one displayed trigger and multiple OS/SS configurations:

```json
{
  "trigger": "B^{+}",
  "configs": [
    {
      "trigger": "B^{+}",
      "associateOS": "B-",
      "associateSS": "B^{+}",
      "OS": "BplusBminus.root",
      "SS": "BplusBplus.root"
    }
  ]
}
```

Every canvas selects a trigger group explicitly with `TriggerToUse`. Yield
calculations may compute all configured bins before a canvas selects the
display subset. `legend_entries` selects ordinary yield curves;
`bins_to_ignore` selects canvas scope. A bin ignored by one canvas may still
be required by another.

Multi-tune ratios use `nominator_TUNES` over one denominator tune. The
spelling is retained for configuration compatibility.

## Multiplicity bins

Nonintegrated activity classes are ordered low to high:

```text
90-100, 80-90, 70-80, 60-70, 50-60, 40-50,
30-40, 20-30, 10-20, 1-10, 0-1
```

The integrated 0--100% class is identified from explicit bounds, never array
position. New canonical pair metadata must bind tune-specific discrete
boundaries whose integer classes are mutually exclusive and exhaustive. The
same boundaries are used in the central union and all blocks.

`MultiplicityBoundaryUtils.h` is the common quantile implementation. It
rejects invalid/negative bins, nonconsecutive integer centers, nonzero
underflow/overflow, nonpositive regular-bin totals, and failed threshold
lookups. The THnSparse run writes a checksum-bound
`multiplicity_boundary_receipt_v1.json` with the configuration digest,
per-tune source/hash, full histogram identity, thresholds, achieved
fractions, and partition proof. The standalone boundary plot consumes and
revalidates that receipt in strict mode. Drawn lines sit at
`threshold+0.5`; the neighboring higher-activity class starts at
`threshold+1`, matching the ROOT projection ranges exactly.

## Observable paths

The four balancing drawing functions are:

1. `drawBalancingPlots`;
2. `drawBalancingPlotsTUNERatios`;
3. `drawBalancingBaryonMesonRatioPlots`;
4. `drawBalancingBaryonMesonRatioPlotsTUNERatios`.

The first two draw ordinary integrated OS-minus-SS balancing yields and their
tune ratios. The latter two draw a configured signed associate balancing
yield divided by the signed reference-meson balancing yield, then tune ratios
of that quantity.

This is a baryon-to-reference-meson balancing-yield ratio. It is not an
inclusive particle-yield ratio and not a sum over every baryon divided by
every meson.

Central ordered pairs use:

```text
same_sign_pair_factor = 1.0
```

The identical-species legacy 0.5 factor is available only in an explicitly
named legacy mode and is not a central-paper convention.

## Central and block estimator

Central values come from the complete-root union. For `K=10` disjoint blocks:

```text
x_bar = sum(x_k)/K
SEM = sqrt(sum((x_k - x_bar)^2)/(K*(K-1)))
```

This is the sample standard deviation divided by `sqrt(K)`.

Within every block:

1. project identical selection/multiplicity ranges;
2. normalize OS and SS by their matching trigger populations;
3. subtract OS-minus-SS;
4. integrate a yield;
5. form a baryon/reference-meson ratio when requested.

Forming the nonlinear quantity inside the block preserves OS/SS and
numerator/denominator covariance. Independently generated tune uncertainties
are combined as independent quantities. A tune double ratio uses the matching
associate ratio uncertainty from each tune.

The macro rejects:

- fewer than ten finite estimates for a final point;
- zero trigger normalization;
- zero/non-finite reference or tune denominator;
- NaN or infinity;
- placeholder `1e-10` errors;
- nonpositive SEM for a nondegenerate final point;
- missing ROOT files/objects/types.

Negative finite OS-minus-SS values are not automatically invalid; they must be
retained and interpreted with their uncertainty.

Before drawing, all four paths also validate the full
`value +/- uncertainty` envelope. The envelope must be finite, must remain
strictly positive for a logarithmic y axis, and must fit inside the configured
y-axis bounds. A clipped error bar is a configuration failure, not an
acceptable publication rendering.

## Angular correlations

Integrated angular-correlation panels use the same block estimator per
Delta-phi bin:

- OS and SS are normalized inside each block;
- OS-minus-SS is subtracted inside the block;
- the bin error is the SEM of the ten block results.

Native ROOT projection errors are not mixed with block SEM in final panels.
Paul's correlation convention remains:

```text
Delta phi = phi_trigger - phi_associate
range = [-pi/2, 3pi/2)
```

## Tune styling

`PlottingScripts/TunePlotStyle.h` is the sole source of truth:

| Tune | Colour | Marker | Line |
|---|---|---:|---|
| MONASH | black | 20 | solid |
| JUNCTIONS | blue+1 | 21 | dashed |
| CLOSEPACKING | magenta+1 | 22 | style 7 |

A tune-ratio curve uses its numerator tune. Species or multiplicity may use a
dedicated secondary line distinction but cannot override tune colour or
marker. Legends display line and marker. Known tune colours in stale JSON are
normalized/rejected rather than allowed to contradict the header.

## Optional mini pads

Every optional mini-pad pointer is initialized:

```cpp
TPad* cMiniPad = nullptr;
```

A drawing function returns `nullptr` if no mini pad was requested. Global
canvas composition checks required pads and fails closed instead of
dereferencing a missing pointer or silently leaving an empty publication pad.
The common point guard rejects nonfinite, log-incompatible, or axis-clipped
uncertainty envelopes before a canvas can be promoted.

## Validation sequence

Validate JSON:

```bash
jq empty \
  PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json \
  PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json
```

Validate dataset and files:

```bash
python3 tools/dataset_selector.py validate
./PlottingScripts/run_paper_plots.sh validate-inputs
./PlottingScripts/run_paper_plots.sh audit-subsamples
```

Run reduced validation, then full:

```bash
mkdir -p logs
VERBOSE=true ./PlottingScripts/run_paper_plots.sh smoke \
  2>&1 | tee logs/final_paper_plots_smoke.log

VERBOSE=true ./PlottingScripts/run_paper_plots.sh thnsparse \
  2>&1 | tee logs/final_paper_plots_thnsparse.log

./PlottingScripts/run_paper_plots.sh multiplicity-spectrum
./PlottingScripts/run_paper_plots.sh all
```

The reduced `smoke` target covers the reduced pair configuration and matching
multiplicity boundary; it intentionally does not repeat the full inclusive
raw-kinematics scan. That scan is an explicit `kinematic-spectra` stage and is
also included in `all`.

Every output stage is provenance-wrapped. A successful ROOT return is not
enough: each regenerated canvas must have PDF, PNG, and ROOT-macro forms.
`tools/final_plot_provenance.py` writes an adjacent sidecar for each form and
a shared run receipt containing the exact configured input hashes, analysis
and plotting commits, configuration and generator hashes, selection/cut
versions, sealed central manifest, all ten block manifests, command/target,
UTC timestamp, output checksum, and the explicitly required
`multiplicity_boundary_receipt_v1.json` binding. The verifier re-hashes the
output, run receipt, exact inputs, and multiplicity receipt:

```bash
python3 tools/final_plot_provenance.py verify \
  --checkout "$PWD" --sidecar <plot-file>.provenance.json
```

Canonical mode rejects missing or stale merge provenance/manifests.
Canonical-candidate validation uses the same numerical/input contract but its
sidecars are forced to `publication_eligible=false`.
`legacy-regression` remains usable as a diagnostic, but its receipts record
`publication_eligible=false` and
`NOT_AVAILABLE_FOR_LEGACY_INPUT` for central/block manifests.

Parse verbose statistical evidence:

```bash
./PlottingScripts/validate_subsample_log.py \
  logs/final_paper_plots_thnsparse.log \
  --json-output \
PlottingScripts/validation/final_thnsparse_uncertainty_validation.json
```

Require the expected count of `subsample yield stats`,
`subsample ratio stats`, and `stdError=` records; each final statistic must
have `n=10`, finite values, and nonzero SEM unless documented degenerate.

The old `21_06_2026` audit found 610 incomplete configured yield/ratio cases.
Therefore its historical full-config audit is expected to fail, while the
reduced 1--10% `legacy-regression` diagnostic is validation-only. Canonical
`smoke` does not accept the legacy selector. Do not weaken the validator or
promote the diagnostic canvas.

## Outputs

Generated files are written below ignored directories:

```text
PlottingScripts/Plots/THnSparse/
PlottingScripts/Plots/THnSparseCompleteRoot/
PlottingScripts/Plots/MultiplicityDistribution/
PlottingScripts/Plots/KinematicSpectra/
```

Canonical full outputs include:

```text
global_balancing_plots_multiplicity_{PDF,PNG,MACRO}
global_balancing_baryon_over_meson_ratio_multiplicity_{PDF,PNG,MACRO}
configured OS/SS correlation panels
```

Reduced equivalents are smoke evidence only. Do not commit regenerated bulk
plot files. Keep a checksummed provenance row for generator, command, config,
code commit, central and block manifests, output, copied paper path, and
`includegraphics` consumer.

Every final PDF page requires human inspection for visible finite error bars,
tune mapping, legends, units, charge labels, activity order, clipping, and
empty pads. Gate-D `prepare` renders pages but does not claim review;
`finalize` requires a real `hf_gate_d_visual_review_v1` report.
