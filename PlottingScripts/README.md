# Plotting scripts

> **Design rationale:** [`../docs/DESIGN_AND_RATIONALE.md`](../docs/DESIGN_AND_RATIONALE.md) explains why each choice was made.

The publication plotting path preserves Paul Veen's merged THnSparse
architecture and adds fail-closed input, selection, uncertainty, styling, and
provenance checks. New central plots must start with
`improvedPlotting_THnSparse.C`; `improvedPlotting.C` and earlier plotting
macros remain legacy.

The complete production-to-paper runbook is
[`../REPRODUCIBILITY.md`](../REPRODUCIBILITY.md). A rendered canvas is not
publication evidence unless its central and block inputs, numerical records,
and visual review all pass.

## Active components

- `improvedPlotting_THnSparse.C`: balancing yields, tune ratios,
  baryon-to-reference-meson ratios, tune double ratios, and configured
  OS/SS/correlation canvases.
- `TunePlotStyle.h`: sole tune-style source.
- `configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json`: full paper
  selection.
- `configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json`:
  reduced/smoke selection with the same scientific and error contracts.
- `run_paper_plots.sh`: supported command-line entry point.
- `Plot_InclusiveKinematicSpectra_Raw.C`: inclusive raw-v5 kinematics.
- `Plot_MultiplicityDistribution_PercentileBoundaries.C`: multiplicity
  distribution and class boundaries.
- `validate_subsample_log.py` and input/coverage validators: machine-readable
  statistical and provenance checks.

`Plot_KinematicSpectra_THnSparse.C` is diagnostic because its objects are
trigger/pair conditioned. It is not an inclusive single-particle spectrum.

The full and reduced/smoke configurations are canonical metadata-v2,
ordered-pair, factor-one configurations. They are not compatible with the
checked-in legacy selector. Until a sealed canonical selector is activated,
canonical `all`, `paper`, `smoke`, and THnSparse targets must fail closed;
only the explicitly named `legacy-regression` target may read the dated
metadata-free sample, and its products are never paper candidates.

## Pair input contract

The macro reads Paul-compatible pair files containing:

```text
summed MULTIPLICITY        TH1D
hTrKinematics              THnSparseD
hAsKinematics              THnSparseD
hCorrelations              THnSparseD
```

For the new pipeline, those objects are produced once per raw file for all
300 signed pair definitions by
`AnalysisScripts/status_analysis_THnSparse_qq.C`, then merged from a sealed
canonical manifest.

Canonical merged layout:

```text
AnalyzedData/complete_root_<TAG>_MONASH/
AnalyzedData/complete_root_<TAG>_JUNCTIONS/
AnalyzedData/complete_root_<TAG>_CLOSEPACKING/
AnalyzedData/SUBSAMPLES_<TAG>/combined_root_subSamples_<TUNE>/combined_root_1/
...
AnalyzedData/SUBSAMPLES_<TAG>/combined_root_subSamples_<TUNE>/combined_root_10/
```

The macro also supports the established nested tune layouts. Relative paths
resolve from `HADRONIZATION_BASE` or the checkout; absolute paths are accepted
only for explicit private diagnostics.

## Dataset selector

`../config/dataset_selector.json` is the single active data switch. Validate
and show it:

```bash
python3 tools/dataset_selector.py validate
python3 tools/dataset_selector.py show
python3 tools/dataset_selector.py shell
```

The runner evaluates the `shell` output. It null-safely exports
`HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE`,
`HADRONIZATION_CANONICAL_MANIFEST`, `HADRONIZATION_PRODUCTION_ROOT`,
`HADRONIZATION_ANALYSIS_ROOT`, `HADRONIZATION_RAW_BASE`,
`HADRONIZATION_ANALYZED_DATA_BASE`, `HADRONIZATION_COMPLETE_ROOT_TAG`, and
`HADRONIZATION_SUBSAMPLE_BASE`. Canonical entries must populate the manifest
and production/analysis roots; legacy entries export empty values for fields
that do not exist rather than the literal string `None`.

The checked-in active dataset is still the regression-only:

```text
/data/alice/ipardoza/Hadronization/AnalyzedData/complete_root_21_06_2026_MONASH
/data/alice/ipardoza/Hadronization/AnalyzedData/complete_root_21_06_2026_JUNCTIONS
/data/alice/ipardoza/Hadronization/AnalyzedData/complete_root_21_06_2026_CLOSEPACKING
/data/alice/ipardoza/Hadronization/AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_MONASH
/data/alice/ipardoza/Hadronization/AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_JUNCTIONS
/data/alice/ipardoza/Hadronization/AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_CLOSEPACKING
```

These paths are shown only to identify the real Nikhef regression data. The
JSON configs themselves remain checkout-relative:

```json
"base_dir": "AnalyzedData",
"bb_bar_complete_root_dir": "complete_root_21_06_2026",
"cc_bar_complete_root_dir": "complete_root_21_06_2026",
"bb_bar_complete_root_dir_sub_samples": "AnalyzedData/SUBSAMPLES_700/combined_root_subSamples",
"cc_bar_complete_root_dir_sub_samples": "AnalyzedData/SUBSAMPLES_700/combined_root_subSamples",
"nSubSamples": 10
```

The `21_06_2026` sample is structurally coherent legacy evidence, not raw-v5.
Do not describe it as using the new trigger-origin selector or no-0.5
semantics. Add a publication-ineligible `status: canonical_candidate`
selector entry after a new campaign has been sealed, analyzed, merged, and
validated. Use it to generate boundary, robustness, and review evidence.
Switch it to `status: canonical` only after the exact final scientific review
and project-owner authorization validate; all candidate plots must then be
regenerated.
The legacy selector has `publication_eligible: false`; canonical paper
targets must refuse it and direct the operator to the explicitly named legacy
regression target.

`USE_DATASET_SELECTOR=false` is diagnostic-only and must be recorded in the
run log.

## Selection contract: apply every cut exactly once

Both JSON configs declare:

```text
v2_metadata_or_tagged_legacy_recuts_v1
```

The rule is:

1. New `paul_pair_objects_primary_ground_v2` pair files already contain the
   exact trigger `pT > 1 GeV/c`, associate `pT > 0.15 GeV/c`, and
   `|eta| <= 4` selection from upstream analysis. The plotter validates the
   complete metadata and does not re-cut pT/eta. It applies only the requested
   multiplicity projection.
2. Metadata-free files are accepted only when their complete-root tag exactly
   equals `complete_root_21_06_2026`, under the standalone
   `legacy-regression` diagnostic with `tagged_legacy_recuts_only_v1`,
   `legacy_identical_ss_half_v1`, and factor `0.5`. Matching Paul’s stable
   main, the configured trigger and associate pT/eta cuts are applied to the
   correlation numerator and the configured trigger cuts are applied to the
   trigger-normalization denominator. The checked-in factor-one paper configs
   reject all metadata-free files.
3. Partial/mixed metadata, inconsistent role thresholds, inactive-looking
   config fields, or any undeclared upper-pT selection are fatal.

This prevents double selection in raw-v5 while keeping Paul’s exact historical
projection reproducible. The diagnostic does not change the canonical
metadata-v2 central-value path. The executable test is
`Validation/TestPlotProjectionCuts.C`.

Individual non-full phi recuts are rejected when they would make the
correlation numerator and trigger denominator inconsistent.

## Full and reduced configs

The full config retains:

- grouped beauty and charm triggers;
- multiple trigger choices;
- `TriggerToUse` per canvas;
- MONASH, JUNCTIONS, CLOSEPACKING;
- config-driven mini and global canvases;
- combined beauty/charm layouts;
- several numerator tunes over one denominator;
- ordinary yields and baryon-to-reference-meson ratios.

The complete-root config is a deliberately small validation subset: B+ and D+
trigger groups, their signed reference mesons, Lambda-b/Lambda-c associates,
all three tunes, and the 1--10% activity class. It contains 16 mini canvases
feeding two global canvases. Sigma-b and duplicate standalone canvases are
excluded; Sigma-b remains review-blocked and is not evidence needed by this
smoke test. The config retains all 11 ordered activity definitions so the
percentile partition and frozen-boundary contract are still validated. It
has the same grouped schema, `TriggerToUse`, selection contract, and ten-block
error prescription as the full config. It is not a no-error target and it is
not a substitute for the full paper run.

Both set:

```json
"calculate_errors": true,
"nSubSamples": 10
```

## Final-plot provenance

Every output-producing `run_paper_plots.sh` target is wrapped by
`tools/final_plot_provenance.py`. The wrapper snapshots the declared output
roots before ROOT runs and accepts only regenerated canvases with a complete
PDF/PNG/ROOT-macro triplet. It then writes:

- one adjacent `<output>.provenance.json` sidecar for every PDF, PNG, and
  generated ROOT macro; and
- one run receipt under the output root's `provenance/` directory.

The run receipt binds the exact command and target, UTC timestamp, plotting
commit/tree, generator/configuration hashes and payload, selection/cut/schema
versions, analysis commit, canonical-manifest hash, all ten block-manifest
hashes, every configured ROOT-input hash, the
`multiplicity_boundary_receipt_v1.json` hash, and every output checksum.
Canonical pair inputs must carry valid
`hf_merged_pair_directory_provenance_v2` and checksum inventories whose
copied source manifests match the sealed central or corresponding block
manifest. Canonical raw plots recheck every sealed-manifest file size and
SHA-256. Missing inputs, stale hashes, incomplete output triplets, a missing
boundary receipt, or a tracked-dirty release checkout fail the plotting
command after ROOT and prevent promotion.

`canonical_candidate` uses the same sealed canonical inputs and numerical
checks but records `canonical-validation-pair` or
`canonical-validation-raw` provenance with
`publication_eligible=false`. This is the required non-circular review stage,
not a way to promote an unauthorised result.

Verify any artifact before copying it into the paper:

```bash
python3 tools/final_plot_provenance.py verify \
  --checkout "$PWD" \
  --sidecar PlottingScripts/Plots/THnSparse/<plot>_PDF.pdf.provenance.json
```

`legacy-regression` receives the same output checks, but its sidecars always
set `publication_eligible=false` and explicitly state that canonical and
block manifests are unavailable.
`PLOT_PROVENANCE_DEVELOPMENT=true` permits a tracked-dirty checkout for
development diagnostics only; it is recorded and is not the release
procedure.

Both order nonintegrated activity classes from low to high:

```text
90-100, 80-90, 70-80, 60-70, 50-60, 40-50,
30-40, 20-30, 10-20, 1-10, 0-1
```

The THnSparse stage freezes these tune-specific integer thresholds in
`multiplicity_boundary_receipt_v1.json` under its configured output
directory. The receipt binds the config SHA-256, central source path/hash,
complete histogram identity (edges, contents, errors, and `Sumw2`),
thresholds, achieved fractions, and disjoint/exhaustive integer partition.
The standalone multiplicity-boundary plot requires and revalidates this
receipt in strict mode, so run the matching THnSparse target first. It rejects
nonfinite/negative bins, nonconsecutive integer centers, nonzero
underflow/overflow, and failed quantiles. Visual boundaries are drawn at
`threshold+0.5`; the adjacent higher-activity class begins at
`threshold+1`.

The old regression sample does not have ten finite trigger normalizations for
every full-config observable. Its exhaustive audit found 610 incomplete
yield/ratio cases (540 beauty, 70 charm). The explicit noncanonical
`legacy-regression` overlay uses the reduced selection whose 1--10% class
historically proved input/error plumbing; it does not prove full-paper
coverage. Canonical full/smoke targets refuse the legacy selector before ROOT
runs.

A new canonical dataset must rerun the exhaustive matrix. Every point
reachable from a final canvas needs ten finite estimates; an excluded smoke
bin cannot support a paper statement.

## Statistics

Central values come from the full complete-root union. For ten disjoint block
estimates:

```text
SEM = sqrt(sum((x_k - mean(x))^2) / (10*9))
```

Equivalently, SEM is the sample standard deviation using `N-1`, divided by
`sqrt(10)`.

The four drawing paths are:

- `drawBalancingPlots`;
- `drawBalancingPlotsTUNERatios`;
- `drawBalancingBaryonMesonRatioPlots`;
- `drawBalancingBaryonMesonRatioPlotsTUNERatios`.

Their common rules are:

- normalize OS and SS with the matching trigger count inside each block;
- subtract OS-minus-SS inside each block;
- integrate a block before estimating yield SEM;
- form a baryon/reference-meson ratio inside each block;
- retain within-tune numerator/denominator covariance;
- propagate independently generated tune uncertainties independently;
- in tune double ratios, use the matching associate ratio uncertainty for
  both numerator and denominator tunes;
- canonical ordered-pair inputs use same-sign factor 1.0;
- reject zero/non-finite denominators, NaN, infinity, incomplete finite
  blocks, and placeholder `1e-10` errors.

Multiplicity-integrated angular-correlation panels also use per-Delta-phi-bin
block SEM. OS-minus-SS is formed inside a block before the bin SEM. Native
ROOT projection errors are not mixed into the final panels.

ROOT `Sumw2` remains useful for input validation but is not the covariance
estimator for normalized or nonlinear observables.

## Tune style

`TunePlotStyle.h` is authoritative:

| Tune | Colour | Marker | Line |
|---|---|---:|---|
| MONASH | black | 20 | solid |
| JUNCTIONS | blue+1 | 21 | dashed |
| CLOSEPACKING | magenta+1 | 22 | style 7 |

Tune ratios use the numerator tune style. Species or multiplicity line styles
may add a distinction but cannot override tune colour/marker. Legends show
both line and marker. Stale JSON colours for known tunes cannot contradict
the header.

## Supported runner

List targets:

```bash
./PlottingScripts/run_paper_plots.sh list
```

Key targets:

- `validate-inputs`: validate configured pairs, ROOT object types,
  central/block inventories, provenance, disjointness, and all configured
  final-pair block-union consistency;
- `audit-subsamples`: scan the full configured observable space without
  silently dropping deficient points;
- `smoke` / `quick`: reduced-scope pair and multiplicity-boundary plots with
  the same ten-block SEM; this target deliberately omits the full
  300-million-event inclusive raw-kinematics scan;
- `thnsparse-complete-root`: reduced THnSparse selection;
- `thnsparse`: strict full THnSparse selection;
- `multiplicity-boundaries`: percentile boundary plot;
- `multiplicity-spectrum`: shared raw multiplicity spectrum and tune/MONASH
  ratios;
- `kinematic-spectra`: inclusive raw-tree pT, eta, phi, and multiplicity;
- `legacy-regression`: exact, nonpublication stable-main Paul recut
  projection;
- `all` / `paper`: current complete paper suite.

The `final-multiplicity` and `final-yields` targets are retained
`legacy-unsealed` comparisons. Their provenance is always
`publication_eligible=false`; despite the historical “FinalAnalysis” directory
name, they are not canonical paper targets.

Run in this order:

```bash
mkdir -p logs
jq empty \
  PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json \
  PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json

./PlottingScripts/run_paper_plots.sh validate-inputs
./PlottingScripts/run_paper_plots.sh audit-subsamples

VERBOSE=true ./PlottingScripts/run_paper_plots.sh smoke \
  2>&1 | tee logs/final_paper_plots_smoke.log

VERBOSE=true ./PlottingScripts/run_paper_plots.sh thnsparse \
  2>&1 | tee logs/final_paper_plots_thnsparse.log

./PlottingScripts/run_paper_plots.sh multiplicity-spectrum
./PlottingScripts/run_paper_plots.sh all
```

Do not treat smoke success as full success. If the full run fails the
coverage gate, stop promotion.

For a canonical dataset, input validation requires the immutable all-tune
source manifests and explicit selected-tune merge provenance, checks every
configured final OS/SS pair, and confirms its central values close against
the ten blocks. The upstream canonical merge must also retain
`canonical_merge_contract.json` and the per-tune
`pair_block_closure_<TAG>_<TUNE>.log` evidence from
`Validation/validate_pair_block_closure.sh`; those logs cover all 300 pair
identities and stored contents plus `Sumw2`, not merely the plotted subset.

## Log validation

The verbose log contains:

```text
subsample yield stats
subsample ratio stats
stdError=
```

Validate it:

```bash
./PlottingScripts/validate_subsample_log.py \
  logs/final_paper_plots_thnsparse.log \
  --json-output \
PlottingScripts/validation/final_thnsparse_uncertainty_validation.json
```

Require the expected record count, `n=10`, finite estimates, and positive SEM
for every nondegenerate final point. Investigate a genuinely zero observable;
do not silently accept, hide, or replace it.

## Inclusive raw kinematics

The active inclusive single-particle macro reads raw production directly:

```bash
./PlottingScripts/run_paper_plots.sh kinematic-spectra
```

It uses exact signed-PDG matching and raw-v5 provenance. It is not
trigger/associate conditioned. The producer retains the central acceptance;
the plotting macro does not add a hidden upper-pT selection. Absolute phi is
displayed in `[-pi, pi)`, while Paul's correlation Delta-phi convention is
`[-pi/2, 3pi/2)`.

For `status: canonical`, the macro reads file membership only from the
checksum-bound, sealed canonical manifest and verifies its freeze summary,
raw-validation receipt, seal, file sizes, unique contiguous slots, and ten
equal modulo blocks. It supports equal tune exposure `N >= 100` when
`N % 10 == 0`; an expanded final campaign is therefore not silently truncated
to the initial 100-file/tune stage. Unlisted reserves or other ROOT files
under the production tree are not discovered, and every selected file's size
and SHA-256 must match its sealed manifest row. Recursive tune-directory
discovery remains available only as the explicitly requested
`legacy_recursive_diagnostic` mode and must not be used for a canonical paper
result.

`Validate_THnSparse_Production.C` and the multiplicity-boundary macro consume
the same selected analyzed-data base and complete-root tag. Metadata-v2
central/block files are accepted only with the exact upstream selection
contract. Metadata-free files are accepted only for the exact configured
legacy tag. Canonical merged directories contain the immutable all-tune
source manifest (`3*N` central rows, `3*N/10` block rows); merge provenance
records the explicit selected-tune filter. The fixed 300 count in this stage
is the generated pair-file registry, not the number of selected raw inputs.

The shared multiplicity plot uses `NCH_PRIMARY_CHARGED_ETA10_V1`. This is a
real charged-particle multiplicity, but it is measured on a hard-heavy sample,
so it is still not a minimum-bias multiplicity. Never label it “prompt”. A display-axis limit is not an event
selection and must be distinguishable from ROOT overflow accounting.

## Optional pads and global canvases

Every optional mini-pad pointer starts as `nullptr`. A drawing function returns
`nullptr` if no mini pad was requested. Global composition must fail closed on
a required missing pad and never dereference it. Every plotted
`value +/- uncertainty` envelope must be finite, must stay positive on a
logarithmic y axis, and must fit inside the configured y-axis range.
Empty or clipped one-bin smoke pads are validation defects, not final layouts.

## Outputs and provenance

Generated outputs are ignored:

```text
PlottingScripts/Plots/THnSparse/
PlottingScripts/Plots/THnSparseCompleteRoot/
PlottingScripts/Plots/MultiplicityDistribution/
PlottingScripts/Plots/KinematicSpectra/
```

Do not commit bulk PDF, PNG, or ROOT-generated macro files. The 78 stale
tracked July validation artifacts remain removed and are inventoried in
`validation/removed_tracked_plot_inventory.txt`.

The full deliverables include:

```text
global_balancing_plots_multiplicity_{PDF,PNG,MACRO}
global_balancing_baryon_over_meson_ratio_multiplicity_{PDF,PNG,MACRO}
configured final OS/SS correlation outputs
```

Reduced equivalents are validation only. Every promoted plot needs a
sidecar/index row with code/config/input/manifest/block hashes, exact command,
timestamp, generated checksum, paper-copy path, and paper consumer. Inspect
every rendered PDF page for error bars, tune styles, legends, multiplicity
order, clipping, and empty pads before promotion.

## Legacy plotting

The following remain historical/diagnostic:

- `improvedPlotting.C`;
- `combinedCanvasPlots.C`;
- `B_Balancing_GeneralPlotting.C`;
- `PlottingWizard.C`;
- old pT JSON configs with personal absolute paths;
- `Balancing_and_Sampling/` plot/error code.

Their old absolute paths, charge combinations, native errors, or sampling
rules are not silently upgraded. Retain them for reproduction and label any
paper figure that still depends on them until it has a validated active
replacement.
