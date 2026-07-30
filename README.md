# Hadronization

This repository is the working code base for heavy-flavour hadronization studies in proton-proton collisions with PYTHIA 8 and ROOT. The authoritative publication workflow, exact physics definitions, validation gates, immutable-manifest procedure, and reproduction commands are in [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md). Older commands retained later in this README reproduce legacy studies unless explicitly identified as canonical.

The canonical chain uses the unified producer `SimulationScripts/heavyflavourcorrelations_status.cpp`, raw schema `hf_primary_ground_raw_v3`, origin algorithm `signed_heavy_carrier_explicit_parent_event_unique_v2`, a frozen campaign manifest, and the one-pass signed-pair analysis `AnalysisScripts/status_analysis_THnSparse_qq.C`. Charm and beauty are enabled in the same PYTHIA run. The 50-state signed species registry and 300-pair registry are versioned under `config/`. Per-hadron heavy ancestry is followed through complete PYTHIA mother ranges, then an event-level invariant prevents two final heavy hadrons from claiming the same selected hard-quark carrier; conflicting claims are retained as explicitly audited unresolved origins. The older split production and `hf_mult_pt_analysis_multi.C` remain regression and inclusive-spectrum references; they are not the canonical balancing-analysis reduction.

## Repository Map

`SimulationScripts` contains the PYTHIA producers, settings cards, and Makefile. The important executable for current work is `heavyflavourcorrelations_status`, while `bbbarcorrelations_status`, `bbbarcorrelations_status_JUNCTIONS`, `ccbarcorrelations_status`, and `ccbarcorrelations_status_JUNCTIONS` are the split legacy producers. The `pythiasettings_Hard_Low_ccbb_MONASH.cmnd`, `pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd`, and `pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd` cards are the current combined-HF cards. The split cards remain available as `pythiasettings_Hard_Low_bb*.cmnd` and `pythiasettings_Hard_Low_cc*.cmnd`.

`AnalysisScripts` contains the ROOT reduction macros and shell wrappers. The canonical balancing macro is `status_analysis_THnSparse_qq.C`: each frozen raw file is read once and produces all signed ordered-pair outputs. `hf_mult_pt_analysis_multi.C`, `bb_mult_pt_analysis_multi.C`, and `cc_mult_pt_analysis_multi.C` are retained for legacy/inclusive-spectrum comparisons and must not be mixed into the canonical balancing chain.

`PlottingScripts/PtMultiplicity` contains the current physics plotting macros for pT spectra, multiplicity-dependent spectra, baryon-to-meson ratios, species-resolved spectra, single-particle spectra, and minimum-bias spectra. These macros read the reduced `AnalyzedData` files rather than the raw simulation trees. They prefer the `hf_` file naming scheme and fall back to `bbbar_` or `ccbar_` when an older split sample is being plotted.

`PlottingScripts/FinalAnalysis` contains the final comparison layer. It now has two source macros. `Plot_MultiplicityDistributions_TwoSamples.C` compares multiplicity distributions between two analyzed samples. `Plot_SelectedParticleYields_IndependentVsCombined.C` compares selected charm and beauty yields and draws the independent-over-combined ratio inside the same output canvas.

The top level of `PlottingScripts` contains the paper THnSparse plotting path. `improvedPlotting_THnSparse.C` reads `configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json` and treats MONASH, JUNCTIONS, and CLOSEPACKING as equal tunes. `Plot_MultiplicityDistribution_PercentileBoundaries.C` draws the charged-particle multiplicity distribution with the configured percentile boundaries, and `run_paper_plots.sh` is the preferred entry point for paper plotting targets. The older configurable plotting machinery is still present: `improvedPlotting.C` reads the older JSON configuration files, while `combinedCanvasPlots.C`, `B_Balancing_GeneralPlotting.C`, and `PlottingWizard.C` are earlier plotting macros for balancing and angular-correlation studies. `ListHistos.C` is the small inspection tool used to list objects inside a ROOT file. The `DpDmBpBm_ComparisonStudy` subdirectory keeps the D+/D- and B+/B- origin, same-mother, different-mother, decay-only, and decay-plus-hadronisation comparison macros.

`Balancing_and_Sampling` keeps the older balancing, yield, sampling, and uncertainty machinery. This part of the repository is still useful for reproducing the earlier balancing plots and for batch-yield error studies, but it is not the primary entry point for the current combined-HF production. The scripts under `Balancing_and_Sampling/CalculateErrors` still use the sampling directories from the older `/data/alice/pveen/ProductionsPythia` layout unless those base paths are overridden in the environment.

`RootFiles` is the intended place for raw simulation products. The current local checkout does not contain the large raw ROOT productions, except for descriptive text files and old-production notes. The actual raw ROOT files should be treated as external data and should not be forced into Git. `AnalyzedData`, in contrast, currently stores reduced ROOT outputs for dated samples such as `10-09-2025`, `12-01-2026`, `27-03-2026`, `08-04-2026_100M_Combined`, and `08-04-2026_100M_Separate`.

`Jobs` and `logs` are the Condor work and log areas. They are produced by `runCondorJob.sh` and the submit files. They are not physics inputs by themselves, but they matter for diagnosing Stoomboot submissions.

`Literature` stores the reference bibliography and thesis PDF used for context. It is not part of the executable workflow, but it keeps the project references close to the analysis code.

## Environment

The repository expects ROOT and PYTHIA 8 from the ALICE CVMFS environment. We use `setupEnv.sh` as the shared entry point. It preserves a valid `HADRONIZATION_BASE` override first, then falls back to `base_path.txt` and finally to the checkout location. On Nikhef it loads `VO_ALICE@ROOT::v6-30-01-alice5-2` and `VO_ALICE@pythia::v8315-alice1-23`; non-interactive shells that cannot initialise `alienv` fall back to the equivalent EL9 ROOT package and runtime libraries directly from CVMFS.

```bash
source ./setupEnv.sh
```

On the Nikhef/Stoomboot filesystem, `base_path.txt` currently points to:

```text
/data/alice/ipardoza/Hadronization
```

If the repository is moved, you update that file and then refresh the Condor submit paths:

```bash
echo "/new/absolute/path/to/Hadronization" > base_path.txt
./update_submit_paths.sh
```

## Current Production Workflow

You build the simulation executables from the repository base after loading the environment.

```bash
source ./setupEnv.sh
make -C SimulationScripts
```

For a local combined-HF test, you run the unified producer with a tune mode, an output file, and two seed modifiers.

```bash
./SimulationScripts/heavyflavourcorrelations_status monash RootFiles/HF/MONASH/hf_MONASH_test.root 123 456
./SimulationScripts/heavyflavourcorrelations_status junctions RootFiles/HF/JUNCTIONS/hf_JUNCTIONS_test.root 123 456
./SimulationScripts/heavyflavourcorrelations_status closepacking RootFiles/HF/CLOSEPACKING/hf_CLOSEPACKING_test.root 123 456
```

The unified output tree is named `tree`. It writes `ID`, `HFCLASS`, `PT`, `ETA`, `Y`, `PHI`, `CHARGE`, `STATUS`, `MOTHER`, `MOTHERID`, `MULTIPLICITY`, `PROCESSCODE`, `NCHARM`, `NBEAUTY`, and `NBC`. The `HFCLASS` convention is simple: `5` means beauty, `4` means charm, `45` means Bc, and `0` means pion.

The current combined-HF cards use proton-proton collisions at 14 TeV, `Tune:pp = 14`, `PhaseSpace:pTHatMin = 1.`, and `ParticleDecays:tau0Max = 0.01`. The MONASH card enables `HardQCD:hardccbar` and `HardQCD:hardbbbar`. The JUNCTIONS card uses the same hard processes and adds the QCD-based color-reconnection, junction, fragmentation, and beam-remnant settings. The CLOSEPACKING card uses the same combined-HF output contract and adds the Close Packing T1 parameters.

## Analysis Workflow

The current analysis wrapper reads all raw combined-HF files for the current tunes and writes reduced subsample outputs. The default is ten subsamples and charge-conjugate-combined species histograms.

```bash
./AnalysisScripts/run_hf_analysis.sh 27-03-2026
```

You can choose the number of subsamples and ask the analysis to write extra particle and antiparticle histograms while keeping the combined names for compatibility.

```bash
./AnalysisScripts/run_hf_analysis.sh 27-03-2026 20 separate
```

The output layout is:

```text
AnalyzedData/<tag>/Beauty/hf_MONASH_sub0.root
AnalyzedData/<tag>/Beauty/hf_JUNCTIONS_sub0.root
AnalyzedData/<tag>/Beauty/hf_CLOSEPACKING_sub0.root
AnalyzedData/<tag>/Charm/hf_MONASH_sub0.root
AnalyzedData/<tag>/Charm/hf_JUNCTIONS_sub0.root
AnalyzedData/<tag>/Charm/hf_CLOSEPACKING_sub0.root
```

Each output file contains event-count histograms, tagged-event-count histograms, multiplicity histograms, tagged multiplicity histograms, PDG-versus-multiplicity histograms, aggregate charm or beauty meson and baryon histograms, species-resolved pT-versus-multiplicity histograms, and pion pT histograms. The macros enable `Sumw2` so the plotting layer can propagate statistical errors.

The split analysis wrappers are still available for old independent samples.

```bash
./AnalysisScripts/run_bb_analysis.sh 12-01-2026 10 combined
./AnalysisScripts/run_cc_analysis.sh 12-01-2026 10 combined
```

## Plotting Workflow

The current paper THnSparse plotting workflow uses pair-named ROOT files produced by `AnalysisScripts/status_analysis_THnSparse_qq.C`. The root-level wrappers build the input layout expected by Paul's plotting macro for all three tunes:

```bash
./submit_status_analysis.sh ALL 100 Job700
./merge_root_files.sh ALL Job700 21_06_2026
./make_subsamples.sh
```

For large THnSparse productions, the merge and subsample wrappers can use a hybrid ROOT merge backend. This keeps the object-preserving ROOT merger as the default path and uses chunked `hadd` for the heavy charm-trigger pair files:

```bash
MERGE_BACKEND=hybrid HADD_JOBS=1 HADD_FINAL_JOBS=4 HADD_CHUNK_SIZE=10 ./merge_root_files.sh ALL Job700 21_06_2026
MERGE_BACKEND=hybrid HADD_JOBS=1 HADD_FINAL_JOBS=4 HADD_CHUNK_SIZE=10 ./make_subsamples.sh
```

For a smaller validation pass, replace `100` with the number of available raw files to process per tune. The submit wrapper sorts available files by numeric job id and selects the first N completed files, so this works even if some low job ids are still running. For example, the planned three-tune test run uses:

```bash
./submit_status_analysis.sh ALL 50 Job700
./merge_root_files.sh ALL Job700 21_06_2026_50job
./make_subsamples.sh ALL 8 6 123 Job700 700_50job
```

When using non-default tags like these, copy one of the THnSparse JSON configs and update `bb_bar_complete_root_dir`, `cc_bar_complete_root_dir`, `bb_bar_complete_root_dir_sub_samples`, and `cc_bar_complete_root_dir_sub_samples` to the validation tags. Then pass that config through `THNSPARSE_CONFIG`, `THNSPARSE_COMPLETE_ROOT_CONFIG`, or `MULTIPLICITY_CONFIG` when running `PlottingScripts/run_paper_plots.sh`.

`make_subsamples.sh` uses non-overlapping shuffled partitions by default. With no arguments, it runs the final paper default: all three tunes, ten independent 10-job subsamples per tune, `Job700` input, and `SUBSAMPLES_700` output. This covers all 100 jobs per tune.

The resulting paper THnSparse inputs are:

```text
AnalyzedData/complete_root_<tag>_MONASH
AnalyzedData/complete_root_<tag>_JUNCTIONS
AnalyzedData/complete_root_<tag>_CLOSEPACKING
AnalyzedData/SUBSAMPLES_<tag>/combined_root_subSamples_MONASH
AnalyzedData/SUBSAMPLES_<tag>/combined_root_subSamples_JUNCTIONS
AnalyzedData/SUBSAMPLES_<tag>/combined_root_subSamples_CLOSEPACKING
```

The paper plotting entry point is:

```bash
./PlottingScripts/run_paper_plots.sh validate-inputs
./PlottingScripts/run_paper_plots.sh audit-subsamples
./PlottingScripts/run_paper_plots.sh smoke
./PlottingScripts/run_paper_plots.sh all
```

The full config is `PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json`. The reduced/smoke config is `PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json`; “complete root” refers to the central-value source, not to a no-error mode. Both use central values from `AnalyzedData/complete_root_21_06_2026_<TUNE>` and sample-standard-error uncertainties from the same ten disjoint subsamples under `AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_<TUNE>`. The smoke config reduces the trigger/canvas selection and, for the current production, validates only the universally covered `1-10%` activity class.

For each plotted observable, the uncertainty is the sample standard deviation of the ten subsample results divided by `sqrt(10)`. Baryon/meson ratios are formed inside each subsample before computing the SEM, retaining within-tune correlations. Tune ratios combine independently generated tune uncertainties in quadrature. The integrated angular-correlation figures use a per-`Delta phi`-bin block SEM; OS-minus-SS is formed inside each block before that SEM is calculated, and native ROOT projection errors are not mixed with it. Central and subsample paths, ROOT-object types, job-manifest disjointness, and representative final-pair central-versus-subsample-union consistency can be checked with the `validate-inputs` target; its machine-readable report is written under `PlottingScripts/validation/`.

The current real production does **not** have ten finite trigger normalizations for every configured observable. The exhaustive `audit-subsamples` run records 610 incomplete yield/ratio coverage cases (540 beauty and 70 charm) in `PlottingScripts/validation/final_thnsparse_subsample_coverage.json`. The reduced smoke config therefore validates only the universally supported `1-10%` class. The full config remains strict and intentionally fails instead of publishing partial, zero, or placeholder uncertainties. A larger or differently partitioned beauty production is required before the full THnSparse paper figures can be regenerated and promoted.

The default `all` target runs the multiplicity-boundary plot, inclusive raw kinematic spectra, and the full THnSparse config. Use `./PlottingScripts/run_paper_plots.sh multiplicity-spectrum` to regenerate only the shared raw `N_{ch}` spectrum with the tune/MONASH ratio panel, MONASH percentile-boundary inset, and short energy/acceptance annotation below the legend. Use `./PlottingScripts/run_paper_plots.sh multiplicity-compact` for the standalone compact MONASH percentile-boundary figure.

The canonical tune style is defined only in `PlottingScripts/TunePlotStyle.h`: MONASH is black/marker 20/solid, JUNCTIONS is blue+1/marker 21/dashed, and CLOSEPACKING is magenta+1/marker 22/line style 7. Tune-ratio curves inherit the numerator tune style.

Paper kinematic spectra are inclusive single-particle spectra drawn directly from raw production, not from trigger/associate-conditioned THnSparse pair outputs. Exact PDG-ID matching is used, the raw producer acceptance is preserved, and absolute `phi` is displayed in `[-pi, pi)`. Correlation `Delta phi` plots in Paul's THnSparse macro keep the shifted `[-pi/2, 3pi/2]` convention. For new canonical figures, charged multiplicity means direct charged primary `e`, `mu`, `pi`, `K`, and `p` species, including antiparticles, with positive PYTHIA status `81-89`, `pT > 0.15 GeV/c`, `|eta| <= 4`, in pp at `sqrt(s)=14 TeV`; activity classes are read from low to high multiplicity as `90-100% -> ... -> 0-1%`. “Prompt” is not used as a synonym for this generator-status definition.

The current pT and multiplicity plots are made from `AnalyzedData`, not from `RootFiles`. If no date is passed, the plotting helpers search for the latest dated folder under `AnalyzedData`. In ordinary use, we pass the date explicitly so that no older production is selected by accident.

```bash
root -l -b -q 'PlottingScripts/PtMultiplicity/Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C("27-03-2026",10,0.0,-1.0)'
root -l -b -q 'PlottingScripts/PtMultiplicity/Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples.C("27-03-2026","Charm",10)'
root -l -b -q 'PlottingScripts/PtMultiplicity/Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples.C("27-03-2026","Beauty",10)'
```

The final-analysis comparisons are similarly run from the repository base.

```bash
root -l -b -q 'PlottingScripts/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C("12-01-2026","27-03-2026",10,true)'
root -l -b -q 'PlottingScripts/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C("12-01-2026","27-03-2026",10)'
```

The pT and multiplicity plots are written to `PlottingScripts/PtMultiplicity/Plots`. The final-analysis plots are written to `PlottingScripts/FinalAnalysis/Plots`. Several macros write both PNG and PDF, while older ratio macros still write only PNG.

## Condor Workflow

The Condor execution entry point is `runCondorJob.sh`. Canonical invocations use its `--campaign` form and are rendered from an immutable campaign manifest. Older argument forms are delegated to `runCondorJob_legacy.sh`; the fixed submit files below are historical examples, not publication-production entry points.

```bash
./submit_full_production.sh campaigns/<CAMPAIGN> --dry-run
```

For the canonical path, `submit_full_production.sh` validates a 100/200/200 candidate manifest, rebuilds the producer, renders a no-auto-retry submit file, and requires explicit origin-resolution sign-off before `--submit`. Historical `submitCondor_*.sub` files remain only to reproduce older samples. Canonical partial files are validated and atomically promoted under `Production/<campaign>/raw/<TUNE>`; they are not written into the old discovery-based `RootFiles` pool.

## Data and Versioning

Raw ROOT files are large production artifacts. They belong under `RootFiles` on the machine that runs the production, but they should be excluded from ordinary source synchronization unless the task explicitly concerns data transfer. Reduced analysis ROOT files in `AnalyzedData` are tracked in this working branch because they are the compact products used by the plotting layer.

The three-tune integration branch is `three-tunes`. When synchronizing with the Nikhef copy, the safe rule is that code, scripts, documentation, submit files, and reduced analysis outputs should match, while raw `.root` files under `RootFiles` may differ or remain only on the cluster. This keeps the branch reproducible without moving the heavy raw productions unnecessarily.
