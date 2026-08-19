# Final Analysis Plotting

> Legacy independent-versus-combined comparison path. These macros consume
> dated charge-combined analysis files and are not the raw-v5
> charge-resolved publication balancing pipeline. A paper figure from this
> directory must remain explicitly labeled legacy/inclusive until its
> provenance and scientific role are reviewed.

This directory contains the final comparison macros that read the reduced analysis outputs under `AnalyzedData` and write the summary plots under `plotting/FinalAnalysis/Plots`. The current directory has two source macros. `Plot_MultiplicityDistributions_TwoSamples.C` compares multiplicity distributions between two analyzed samples. `Plot_SelectedParticleYields_IndependentVsCombined.C` compares selected per-event particle yields and draws the independent-over-combined ratio in the same canvas.

## Inputs

Both macros read the same analyzed directory structure:

```text
AnalyzedData/<DATE>/Charm
AnalyzedData/<DATE>/Beauty
```

They support the split independent naming scheme:

```text
ccbar_MONASH_sub0.root
ccbar_JUNCTIONS_sub0.root
bbbar_MONASH_sub0.root
bbbar_JUNCTIONS_sub0.root
```

They also support the combined-HF naming scheme:

```text
hf_MONASH_sub0.root
hf_JUNCTIONS_sub0.root
```

Sample kind is inferred from the file names. A folder with `hf_` files is treated as a combined sample. A folder with `bbbar_` or `ccbar_` files is treated as an independent sample. The current checkout contains independent samples dated `10-09-2025` and `12-01-2026`, a combined-HF sample dated `27-03-2026`, and reduced 100M outputs named `08-04-2026_100M_Combined` and `08-04-2026_100M_Separate`.

## Multiplicity Comparison

`Plot_MultiplicityDistributions_TwoSamples.C` produces four comparisons: charm MONASH, charm JUNCTIONS, beauty MONASH, and beauty JUNCTIONS. Each plot overlays two analyzed folders. The macro prefers `fHistTaggedMultiplicity`, because that histogram describes the flavor-tagged event population. If it is absent, the macro falls back to `fHistMultiplicity` for older files.

When normalization is enabled, each subsample multiplicity histogram is normalized to unit integral first. The plotted bin content is the mean across subsamples and the plotted uncertainty is the standard error of that mean. When normalization is disabled, the macro uses the same subsample spread method but scales back to the summed-event convention.

The fully explicit call is:

```bash
root -l -b -q 'plotting/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C("12-01-2026","27-03-2026",10,true)'
```

The interactive wrapper is:

```cpp
.L "plotting/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C"
runFinalMultiplicityComparison("12-01-2026", "27-03-2026", 10, true);
```

If both date arguments are empty, the macro scans `AnalyzedData` for folders whose names begin with a parsable `DD-MM-YYYY` date, sorts them by calendar date, and compares the two newest dated folders. Tags such as `08-04-2026_100M_Combined` are therefore date-like for the automatic resolver even though they carry extra descriptive text. If only one date is given, the macro stops because a one-sided comparison is ambiguous.

The output names are:

```text
MultiplicityComparison_Charm_MONASH_<DATEA>_vs_<DATEB>.png
MultiplicityComparison_Charm_JUNCTIONS_<DATEA>_vs_<DATEB>.png
MultiplicityComparison_Beauty_MONASH_<DATEA>_vs_<DATEB>.png
MultiplicityComparison_Beauty_JUNCTIONS_<DATEA>_vs_<DATEB>.png
```

The same base names are also saved as PDF and ROOT canvas macro files.

## Selected Particle Yields

`Plot_SelectedParticleYields_IndependentVsCombined.C` compares selected charge-conjugate-combined yields between an independent sample and a combined sample. The macro resolves the latest independent and latest combined dated folders automatically when no arguments are given, but in normal analysis we pass both folders explicitly.

```bash
root -l -b -q 'plotting/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C("12-01-2026","27-03-2026",10)'
```

The interactive wrapper is:

```cpp
.L "plotting/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C"
runSelectedParticleYieldPlots("12-01-2026", "27-03-2026", 10);
```

The beauty species are `Bpm`, `B0/barB0`, and `Lambdab/barLambdab`. The charm species are `Dpm`, `D0/barD0`, and `Lambdac/barLambdac`. The macro reads `fHistPtBplus`, `fHistPtBzero`, `fHistPtLambdab`, `fHistPtDplus`, `fHistPtDzero`, and `fHistPtLambdac`, with `fHistPtLambdacPlus` kept as a compatibility fallback.

The per-event yield is the integral of the species histogram divided by the event count. The preferred normalization is `fHistTaggedEventCount`, then `fHistEventCount`, and finally the multiplicity integral for old files that do not contain event-count histograms. For combined-HF outputs, the tagged event count gives the number of flavor-tagged events in the corresponding charm or beauty file, which is the intended normalization for the independent-versus-combined comparison.

The macro computes one yield per subsample and reports the mean and standard error across the loaded subsamples. It also computes the independent-over-combined ratio and propagates the independent and combined SEM uncertainties into the ratio error. This ratio is drawn in the right-hand pad of the same output canvas; there is no separate source file named `Plot_SelectedParticleYieldRatios_IndependentVsCombined.C` in the current repository.

The output names are:

```text
SelectedParticleYields_Beauty_MONASH_<INDEPENDENT>_vs_<COMBINED>.png
SelectedParticleYields_Beauty_JUNCTIONS_<INDEPENDENT>_vs_<COMBINED>.png
SelectedParticleYields_Charm_MONASH_<INDEPENDENT>_vs_<COMBINED>.png
SelectedParticleYields_Charm_JUNCTIONS_<INDEPENDENT>_vs_<COMBINED>.png
```

The same base names are also saved as PDF and ROOT canvas macro files.

## Output Directory

Both macros create the output directory when needed:

```text
plotting/FinalAnalysis/Plots
```

The current repository already contains final-analysis plots comparing `12-01-2026` with `27-03-2026`. Re-running a macro with the same date pair overwrites plots with the same names.

## Practical Checks

If automatic sample selection picks the wrong folders, pass both tags explicitly. If a macro cannot resolve a prefix, check that the requested flavor and tune have a `sub0.root` file in the selected date folder. If a yield point is zero or missing, inspect the corresponding analyzed file and confirm that the expected species histogram exists. `rootls` ships with ROOT and lists a file's objects directly.

```bash
rootls -l AnalyzedData/27-03-2026/Beauty/hf_MONASH_sub0.root
```
