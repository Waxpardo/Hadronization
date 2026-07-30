# THnSparse plotting configuration

The final pair-correlation plotting entry point is:

```bash
./PlottingScripts/run_paper_plots.sh thnsparse
```

It loads `PlottingScripts/improvedPlotting_THnSparse.C` and the full paper config,
`PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json`.
The similarly named `_complete_root.json` config is the reduced/smoke selection.
Both configs use complete-root central values and ten-subsample uncertainties.

## Inputs and path resolution

The checked-in configs are portable:

```json
"base_dir": "AnalyzedData",
"bb_bar_complete_root_dir": "complete_root_21_06_2026",
"cc_bar_complete_root_dir": "complete_root_21_06_2026",
"bb_bar_complete_root_dir_sub_samples": "AnalyzedData/SUBSAMPLES_700/combined_root_subSamples",
"cc_bar_complete_root_dir_sub_samples": "AnalyzedData/SUBSAMPLES_700/combined_root_subSamples",
"nSubSamples": 10
```

Relative paths are resolved from `HADRONIZATION_BASE`; when it is unset, the
macro finds the checkout from the current directory. Absolute paths are accepted
for private overrides. Complete-root lookup supports both:

```text
AnalyzedData/complete_root_<tag>_<TUNE>/<pair>.root
AnalyzedData/<TUNE>/complete_root_<tag>_<TUNE>/<pair>.root
AnalyzedData/<TUNE>/complete_root_<tag>/<pair>.root
```

`config/dataset_selector.json` is the authoritative active-dataset switch.
`run_paper_plots.sh` validates it and exports the selected raw base,
AnalyzedData base, complete-root tag, and block base. The checked-in JSON plot
configs define the observable/canvas schema; the dataset selector defines
which validated dataset supplies them. Set `USE_DATASET_SELECTOR=false` only
for an explicitly logged diagnostic.

The checked-in `21_06_2026` Nikhef production is a legacy regression dataset:

```text
/data/alice/ipardoza/Hadronization/AnalyzedData/complete_root_21_06_2026_MONASH
/data/alice/ipardoza/Hadronization/AnalyzedData/complete_root_21_06_2026_JUNCTIONS
/data/alice/ipardoza/Hadronization/AnalyzedData/complete_root_21_06_2026_CLOSEPACKING
/data/alice/ipardoza/Hadronization/AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_MONASH
/data/alice/ipardoza/Hadronization/AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_JUNCTIONS
/data/alice/ipardoza/Hadronization/AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_CLOSEPACKING
```

It remains the default only until the new `hf_primary_ground_raw_v3`
campaign has passed Gates A--D, been frozen, analyzed, and merged. It must not
be described as having the new selector or ordered-pair semantics.

Every pair file must contain `summed MULTIPLICITY` (`TH1D`) and
`hTrKinematics`, `hAsKinematics`, and `hCorrelations` (`THnSparseD`).

## Full and smoke configs

The full config retains Paul's grouped beauty and charm triggers, multiple
trigger choices, all three tunes, config-driven mini/global canvases, combined
beauty/charm correlation handling, and multi-numerator tune-ratio panels.

The reduced config has fewer trigger pairs and final global canvases so it
completes more quickly. It uses the same schema (`configs`, `TriggerToUse`,
`nominator_TUNES`, and `bins_to_ignore`) and the same error prescription. It is
a validation target, not a no-error result.

Both configs order activity classes from low to high:

```text
90-100, 80-90, 70-80, 60-70, 50-60, 40-50,
30-40, 20-30, 10-20, 1-10, 0-1
```

The full config keeps every class active. The real-input coverage audit found
610 incomplete yield/ratio cases (540 beauty and 70 charm), so the strict full
paper run currently fails. The reduced smoke config excludes every class
except `1-10%`, the only class with `n=10` across all reduced pairs and tunes.
It does so with each canvas's `bins_to_ignore`; the macro skips subsample
calculation only when a bin is unused by every output canvas. The checked-in
`subsample_error_bins_to_exclude` list remains empty, so no drawn point can
silently receive an unavailable error.
This makes smoke a plumbing/error-propagation validation, not a substitute
paper result. The complete matrix is stored in
`PlottingScripts/validation/final_thnsparse_subsample_coverage.json`; a larger
or differently partitioned production is needed before full figures can be
promoted.

## Trigger and bin schema

`beauty_correlations_to_analyse` and `charm_correlations_to_analyse` are arrays
of trigger groups. Each group has a display `trigger` and a `configs` array of
OS/SS pairs:

```json
{
  "trigger": "B^{+}",
  "configs": [{
    "trigger": "B^{+}",
    "associateOS": "B-",
    "associateSS": "B^{+}",
    "OS": "BplusBminus.root",
    "SS": "BplusBplus.root"
  }]
}
```

Every canvas selects one group with `TriggerToUse`. `histograms_to_analyse`
defines the THnSparse cuts and multiplicity percentile classes. The macro
computes central values for all configured bins first. All four drawing paths
honor `bins_to_ignore`; ordinary yield canvases additionally select their
requested curves through `legend_entries`.

The canonical upstream selector applies trigger `pT > 1.0 GeV/c`, associate
`pT > 0.15 GeV/c`, and `|eta| <= 4` to both roles. The plotting macro applies
its configured trigger/associate pT and eta ranges symmetrically to the
correlation numerator and trigger denominator. It rejects unsupported
individual non-full phi cuts instead of silently producing inconsistent
normalization.

## Four drawing paths

- `drawBalancingPlots`: ordinary OS-minus-SS balancing yields.
- `drawBalancingPlotsTUNERatios`: one or more numerator tunes divided by one denominator tune.
- `drawBalancingBaryonMesonRatioPlots`: associate baryon yield divided by the matching meson yield within a tune.
- `drawBalancingBaryonMesonRatioPlotsTUNERatios`: ratio of those baryon/meson ratios between tunes.

Mini pads are optional. All four functions return `nullptr` when no mini pad
was requested, and global canvases skip missing/null pads without dereferencing
them.

## Statistical prescription

Both paper configs set `calculate_errors=true`. Central values always come from
the complete-root file. For ten disjoint subsamples:

```text
s = sqrt(sum((x_i - mean(x))^2) / (N - 1))
SEM = s / sqrt(N), N = 10
```

Ordinary balancing-yield errors use the distribution of the ten corresponding
subsample yields. Baryon/meson errors use the ratio formed inside each
subsample, preserving the numerator/denominator correlation within a tune.
Tune-ratio errors combine independently generated tune uncertainties in
quadrature. A baryon/meson tune double ratio uses the matching associate's
baryon/meson uncertainty for both numerator and denominator tunes.

Central and subsample calculations use identical THnSparse cuts, multiplicity
boundaries, and OS/SS normalization. New canonical pair files contain ordered
trigger-associate pairs and use `same_sign_pair_factor = 1.0`; the legacy
identical-species factor of 0.5 is not applied. The macro rejects missing inputs, wrong object
types, non-finite ratios, incomplete finite-subsample sets, and non-positive
uncertainties for final plotted points. A diagnostic config may explicitly set
`calculate_errors=false`; it draws zero-length errors and is not a paper config.

The optional multiplicity-integrated angular-correlation canvas uses the same
ten disjoint blocks, not native ROOT projection errors. OS and SS are
normalised by their matching trigger count inside each block, and every
`Delta phi` bin receives the block SEM. The OS-minus-SS uncertainty is the SEM
of the subtraction formed inside each block, preserving the OS/SS covariance.
The central line remains the full complete-root result. The macro identifies
the integrated class by its explicit `0-100%` bounds rather than by list
position and refuses to draw a final correlation panel without ten finite
block values.

## Tune style

`PlottingScripts/TunePlotStyle.h` is authoritative:

| Tune | Colour | Marker | Line |
|---|---:|---:|---:|
| MONASH | black | 20 | solid |
| JUNCTIONS | blue+1 | 21 | dashed |
| CLOSEPACKING | magenta+1 | 22 | style 7 |

Tune ratios use the numerator tune. A canvas may use line style to distinguish
a species or multiplicity class, but cannot replace the tune colour or marker.
Known-tune JSON colour entries are normalised to the header mapping.

## Validation and regeneration

From the canonical Nikhef checkout:

```bash
source setupEnv.sh
jq empty \
  PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json \
  PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json
./PlottingScripts/run_paper_plots.sh validate-inputs
./PlottingScripts/run_paper_plots.sh audit-subsamples \
  2>&1 | tee logs/final_thnsparse_full_coverage_audit.log
./PlottingScripts/run_paper_plots.sh smoke
./PlottingScripts/run_paper_plots.sh thnsparse
./PlottingScripts/run_paper_plots.sh multiplicity-spectrum
./PlottingScripts/run_paper_plots.sh all
```

`audit-subsamples`, `thnsparse`, and `all` currently exit nonzero because the
real production does not cover every requested observable with ten finite
subsamples. That failure is the intended safety behavior. Summarize the audit
log with:

```bash
./PlottingScripts/summarize_subsample_coverage.py \
  logs/final_thnsparse_full_coverage_audit.log \
  --json-output \
  PlottingScripts/validation/final_thnsparse_subsample_coverage.json
```

Use `VERBOSE=true` in the full config to retain `subsample yield stats`,
`subsample ratio stats`, and `stdError=` lines. The validation manifest is
`PlottingScripts/validation/final_thnsparse_input_validation.json`.

Validate the full verbose log with:

```bash
./PlottingScripts/validate_subsample_log.py \
  logs/final_paper_plots_thnsparse.log \
  --json-output PlottingScripts/validation/final_thnsparse_uncertainty_validation.json
```

Generated outputs live under `PlottingScripts/Plots/` and are ignored by Git.
The full and reduced THnSparse products are separated into `THnSparse/` and
`THnSparseCompleteRoot/`. The full config writes both Paul's integrated
charm/beauty canvases and the canonical combined multiplicity-dependent yield
and baryon/meson canvases. Regenerate them; do not commit ROOT-generated PDF,
PNG, or macro files. See `PlottingScripts/PAPER_FIGURE_PROVENANCE.md` for the
paper-copy mapping.
