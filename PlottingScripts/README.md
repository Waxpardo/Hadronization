# Plotting Scripts

This directory contains the plotting layer for the hadronization analysis. The current paper workflow combines Paul's THnSparse plotting macro for the pair-correlation analysis with a raw-tree inclusive macro for single-particle kinematic spectra, and treats `MONASH`, `JUNCTIONS`, and `CLOSEPACKING` as equal tunes.

## Paper THnSparse Inputs

Paul's plotting macro does not read the raw PYTHIA ROOT trees directly. It reads pair-named ROOT files produced by:

```text
AnalysisScripts/status_analysis_THnSparse_qq.C
```

Those pair files contain:

```text
summed MULTIPLICITY
hTrKinematics
hAsKinematics
hCorrelations
```

The root-level scripts create the expected input layout:

```bash
./submit_status_analysis.sh ALL 100 Job700
./merge_root_files.sh ALL Job700 21_06_2026
./make_subsamples.sh
```

For the full 100-job THnSparse inputs, use the hybrid merge backend if plain `hadd` or serial object merging is too slow. It applies chunked `hadd` only to the heavy charm-trigger pair files and leaves the rest on the object-preserving merger:

```bash
MERGE_BACKEND=hybrid HADD_JOBS=1 HADD_FINAL_JOBS=4 HADD_CHUNK_SIZE=10 ./merge_root_files.sh ALL Job700 21_06_2026
MERGE_BACKEND=hybrid HADD_JOBS=1 HADD_FINAL_JOBS=4 HADD_CHUNK_SIZE=10 ./make_subsamples.sh
```

For a smaller validation run, change the number of raw files passed to `submit_status_analysis.sh` and use distinct output tags when merging and subsampling. The submit wrapper sorts available files by numeric job id and selects the first N completed files for each tune; it does not require the selected files to be exactly job ids `0` through `N-1`.

`make_subsamples.sh` uses non-overlapping shuffled partitions by default. With no arguments, it runs the final paper default: all three tunes, ten independent 10-job subsamples per tune, `Job700` input, and `SUBSAMPLES_700` output. This covers all 100 jobs per tune.

When using distinct validation tags, copy one of the JSON configs and update:

```text
bb_bar_complete_root_dir
cc_bar_complete_root_dir
bb_bar_complete_root_dir_sub_samples
cc_bar_complete_root_dir_sub_samples
```

Then run the paper runner with the copied config through `THNSPARSE_CONFIG`, `THNSPARSE_COMPLETE_ROOT_CONFIG`, or `MULTIPLICITY_CONFIG`.

Expected complete-root inputs:

```text
AnalyzedData/complete_root_21_06_2026_MONASH
AnalyzedData/complete_root_21_06_2026_JUNCTIONS
AnalyzedData/complete_root_21_06_2026_CLOSEPACKING
```

Expected subsample inputs when `calculate_errors` is enabled:

```text
AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_MONASH
AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_JUNCTIONS
AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_CLOSEPACKING
```

The plotting macro accepts both this flat layout and a nested tune layout.

## Main Paper Runner

Use the paper runner from the repository root:

```bash
./PlottingScripts/run_paper_plots.sh list
./PlottingScripts/run_paper_plots.sh smoke
./PlottingScripts/run_paper_plots.sh
```

Targets:

- `smoke`: multiplicity-boundary plot, kinematic spectra, plus complete-root THnSparse plots without subsampling.
- `thnsparse-complete-root`: Paul's THnSparse plots without subsampling.
- `thnsparse`: Paul's full THnSparse plots with subsampling if enabled in the config.
- `multiplicity-boundaries`: charged-particle multiplicity distribution with percentile boundary lines.
- `multiplicity-compact`: MONASH-only compact multiplicity-percentile plot.
- `multiplicity-spectrum`: shared raw `N_{ch}` spectrum with `JUNCTIONS/MONASH` and `CLOSEPACKING/MONASH` ratio panel plus a MONASH percentile-boundary inset.
- `kinematic-spectra`: inclusive raw-tree pT, eta, phi, and multiplicity spectra.
- `all` / `paper`: multiplicity boundaries, kinematic spectra, plus the full THnSparse config.

The runner resolves the repository root from `HADRONIZATION_BASE` or from its own location, sources `setupEnv.sh` when present, and runs ROOT in batch mode.

The kinematic spectra target reads the generated raw HF files by default:

```bash
./PlottingScripts/run_paper_plots.sh kinematic-spectra
./PlottingScripts/run_paper_plots.sh multiplicity-spectrum
./PlottingScripts/run_paper_plots.sh multiplicity-compact
```

Useful overrides:

```bash
KINEMATIC_RAW_BASE=RootFiles/HF \
KINEMATIC_OUTPUT_DIR=PlottingScripts/Plots/KinematicSpectraFull \
./PlottingScripts/run_paper_plots.sh kinematic-spectra
```

The default kinematic output is shape-normalized. Set `KINEMATIC_NORMALIZE=false` to draw bin-width-normalized counts. Set `KINEMATIC_STRICT=false` to skip missing tunes instead of treating them as errors.

The paper kinematic spectra are inclusive single-particle spectra. They are filled directly from the generated raw tree with exact PDG-ID matching and no trigger/associate pair conditioning. The raw producer already applied its final-state particle acceptance (`pT >= 0.15 GeV/c`, `|eta| <= 4`); the plotting macro adds no extra kinematic cuts. Absolute `phi` is wrapped to `[-pi, pi)`.

`Plot_KinematicSpectra_THnSparse.C` is kept for diagnostic trigger/associate and correlation checks, but those spectra are pair-conditioned by construction and are not the final inclusive single-particle kinematic spectra.

Kinematic spectra are written into subdirectories by plot family:

```text
PlottingScripts/Plots/KinematicSpectra/Multiplicity
PlottingScripts/Plots/KinematicSpectra/Inclusive/pT
PlottingScripts/Plots/KinematicSpectra/Inclusive/eta
PlottingScripts/Plots/KinematicSpectra/Inclusive/phi
```

Event-level spectra that are independent of the selected heavy-flavour species are intentionally drawn once. In particular, charged multiplicity comes from the same HF event sample for charm and beauty, so the paper macro writes one shared multiplicity plot per tune rather than duplicate charm and beauty versions. The shared multiplicity spectrum is limited to `N_{ch} <= 170` and includes a lower ratio panel for `JUNCTIONS/MONASH` and `CLOSEPACKING/MONASH`. Its main panel also carries a compact MONASH percentile-boundary inset and a short energy/acceptance annotation below the legend.

Across the current production plots, `N_{ch}` means prompt charged primary `e^{+-}`, `mu^{+-}`, `pi^{+-}`, `K^{+-}`, and `p`/anti-`p` with PYTHIA status `81-89`, `pT >= 0.15 GeV/c`, and `|eta| <= 4` in pp at `sqrt(s)=14 TeV`. Multiplicity percentile labels are interpreted from low to high activity as `90-100% -> ... -> 0-1%`.

## THnSparse Configs

Full config with subsampling:

```text
PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json
```

Complete-root-only config for smoke tests:

```text
PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json
```

Both configs use the same tunes and event-activity percentile classes, ordered
from lowest to highest multiplicity:

```text
90-100, 80-90, 70-80, 60-70, 50-60, 40-50,
30-40, 20-30, 10-20, 1-10, 0-1
```

All paths in the configs are relative to the Hadronization checkout unless they are absolute paths or `NONE`.

## Direct ROOT Commands

Complete-root smoke test:

```bash
root -l -b <<'ROOT'
.L PlottingScripts/improvedPlotting_THnSparse.C+
improvedPlotting_THnSparse("PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json")
.q
ROOT
```

Full THnSparse plotting:

```bash
root -l -b <<'ROOT'
.L PlottingScripts/improvedPlotting_THnSparse.C+
improvedPlotting_THnSparse("PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json")
.q
ROOT
```

Multiplicity-boundary plot:

```bash
root -l -b -q 'PlottingScripts/Plot_MultiplicityDistribution_PercentileBoundaries.C'
```

Kinematic spectra:

```bash
root -l -b <<'ROOT'
.L PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C+
Plot_InclusiveKinematicSpectra_Raw("RootFiles/HF",
                                   "PlottingScripts/Plots/KinematicSpectra",
                                   true, true)
.q
ROOT
```

Raw multiplicity spectrum only:

```bash
./PlottingScripts/run_paper_plots.sh multiplicity-spectrum
```

Compact MONASH percentile-boundary plot:

```bash
./PlottingScripts/run_paper_plots.sh multiplicity-compact
```

## Outputs

The current paper runner writes under:

```text
PlottingScripts/Plots/THnSparse
PlottingScripts/Plots/THnSparseCompleteRoot
PlottingScripts/Plots/MultiplicityDistribution
PlottingScripts/Plots/KinematicSpectra
```

These are generated artifacts and are ignored by Git. Regenerate them from the macros instead of committing them.

## Older Plotting Code

The directory still contains older plotting macros such as `improvedPlotting.C`, `combinedCanvasPlots.C`, `B_Balancing_GeneralPlotting.C`, and `PlottingWizard.C`. They are kept for reference and older studies, but the current paper pipeline should start from `run_paper_plots.sh` and the THnSparse configs above.
