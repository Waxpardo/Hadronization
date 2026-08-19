# pT and Multiplicity Plotting

> Legacy/inclusive comparison path. These date-discovery and
> charge-conjugate-combined macros do not implement the raw-v5 signed
> trigger-conditioned publication balancing observable. Retain them for
> historical and explicitly justified inclusive plots; the active balancing
> workflow is documented in `plotting/README.md`.

This directory contains the plotting macros that read the reduced heavy-flavour analysis files under `AnalyzedData` and make the current pT, multiplicity, species-resolved, minimum-bias, and baryon-to-meson comparison plots. The macros are written for the subsampled analysis outputs, not for the raw PYTHIA trees. We now use them primarily with the combined-HF `hf_` files, while keeping automatic fallbacks for the older split `bbbar_` and `ccbar_` files.

## Inputs and Outputs

The expected input directory is:

```text
AnalyzedData/<DATE>/Beauty
AnalyzedData/<DATE>/Charm
```

The combined-HF naming scheme is:

```text
AnalyzedData/<DATE>/Beauty/hf_MONASH_sub0.root
AnalyzedData/<DATE>/Beauty/hf_JUNCTIONS_sub0.root
AnalyzedData/<DATE>/Charm/hf_MONASH_sub0.root
AnalyzedData/<DATE>/Charm/hf_JUNCTIONS_sub0.root
```

The legacy split naming scheme is:

```text
AnalyzedData/<DATE>/Beauty/bbbar_MONASH_sub0.root
AnalyzedData/<DATE>/Beauty/bbbar_JUNCTIONS_sub0.root
AnalyzedData/<DATE>/Charm/ccbar_MONASH_sub0.root
AnalyzedData/<DATE>/Charm/ccbar_JUNCTIONS_sub0.root
```

For date-based calls, the macros prefer `hf_` files when they exist and otherwise fall back to the split names. The number of subsamples passed to a plotting macro must match the number of files written by the analysis step. If the analysis produced `sub0` through `sub9`, the plotting call should use `nSub = 10`.

Multiplicity-percentile plots use the class order `80-100%`, `60-80%`, `40-60%`, `20-40%`, `0-20%`, so the visible ordering runs from lower to higher charged-particle multiplicity.

The plots are written to:

```text
plotting/PtMultiplicity/Plots
```

Several output names do not include the date. If you run the same macro on several productions, move or rename the outputs between runs or use a separate worktree.

## Path Resolution

The shared helper `PlottingPathUtils.h` resolves the repository base in a machine-independent order. It first uses `HADRONIZATION_BASE`, then the registered macro location, then `base_path.txt`, and finally the current working directory. It also provides the latest-date finder used when a macro is called with an empty date argument. The date parser accepts folder names that begin with `DD-MM-YYYY`, so tags such as `08-04-2026_100M_Combined` can be selected automatically as date-like folders.

We normally run plotting macros from the repository base and pass the date explicitly:

```bash
root -l -b -q 'plotting/PtMultiplicity/Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C("27-03-2026",10,0.0,-1.0)'
```

## Error Convention

The plotting macros assume that the analysis files were produced by the current `*_mult_pt_analysis_multi.C` macros. Those analysis files contain `Sumw2` histograms and explicit event-count histograms. For spectra, the usual convention is to build a normalized spectrum in each subsample and then compute the mean and standard error of the mean bin by bin. For baryon-to-meson ratios, the ratio is built inside each subsample first and then the plotted value and uncertainty are computed from the distribution of subsample ratios. For multiplicity-percentile ratios, each point is again built from per-subsample values.

The macros use `fHistTaggedMultiplicity` when a flavor-tagged multiplicity distribution is needed and fall back to `fHistMultiplicity` for older analysis outputs. For species histograms, they prefer the charge-conjugate-combined histograms such as `fHistPtDplus`, `fHistPtLambdac`, `fHistPtBplus`, and `fHistPtLambdab`. If combined histograms are not present, they look for `Particle` and `Bar` suffixes and combine those internally when the physics object requires the sum.

## Ratio Macros

`Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C` compares MONASH and JUNCTIONS for beauty baryon-to-meson ratios in five multiplicity percentile classes. It writes the inclusive beauty baryon-over-meson ratio and the `Lambdab/Bpm` ratio.

```bash
root -l -b -q 'plotting/PtMultiplicity/Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C("27-03-2026",10,2)'
```

The interactive wrapper is:

```cpp
.L "plotting/PtMultiplicity/Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C"
runBeautyRatios("27-03-2026", 10, 2);
```

`Plot_Charm_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C` does the same for charm and writes the inclusive charm baryon-over-meson ratio and the `Lambdac/Dpm` ratio.

```bash
root -l -b -q 'plotting/PtMultiplicity/Plot_Charm_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C("27-03-2026",10,2)'
```

The interactive wrapper is:

```cpp
.L "plotting/PtMultiplicity/Plot_Charm_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C"
runCharmRatios("27-03-2026", 10, 2);
```

`Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C` draws charm and beauty baryon-to-meson ratios together for each multiplicity class. It is useful when the question is not only the tune dependence but also the relative charm-versus-beauty behavior.

```bash
root -l -b -q 'plotting/PtMultiplicity/Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C("27-03-2026",10,2)'
```

The interactive wrappers are:

```cpp
.L "plotting/PtMultiplicity/Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C"
runCharmBeautyRatios("27-03-2026", 10, 2);
runBaryonMesonCharmBeauty("27-03-2026", 10, 2);
```

`Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C` integrates over pT and plots `Lambdac/Dpm` and `Lambdab/Bpm` as functions of multiplicity percentile. If `ptMax <= ptMin`, the macro integrates the full pT range.

```bash
root -l -b -q 'plotting/PtMultiplicity/Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C("27-03-2026",10,0.0,-1.0)'
```

The wrapper is:

```cpp
.L "plotting/PtMultiplicity/Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C"
runHFRatios("27-03-2026", 10, 0.0, -1.0);
```

## Spectra Macros

`Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C` makes the older focused spectra plots for `Lambdac`, `Dpm`, `Lambdab`, and `Bpm`, separated by tune and multiplicity percentile.

```bash
root -l -b -q 'plotting/PtMultiplicity/Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C("27-03-2026",10)'
```

The wrapper is:

```cpp
.L "plotting/PtMultiplicity/Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C"
runHFSpectra("27-03-2026", 10);
```

`Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples.C` is the broad species-resolved plotting macro. A selector of `Charm` or `Beauty` compares MONASH and JUNCTIONS for that flavor. A selector of `MONASH` or `JUNCTIONS` gives the older single-tune view. The default charm set is D0, D+, D-, Ds, and Lambdac. The default beauty set is B+, B-, B0, Bs, Bc, and Lambdab. The heavier beauty baryons Sigmab, Xib, and Omegab are available when `includeHeavyBeautyExtras` is true.

```bash
root -l -b -q 'plotting/PtMultiplicity/Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples.C("27-03-2026","Charm",10)'
root -l -b -q 'plotting/PtMultiplicity/Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples.C("27-03-2026","Beauty",10,true)'
```

The common wrappers are:

```cpp
.L "plotting/PtMultiplicity/Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples.C"
runHFSpeciesResolvedSpectraCharm("27-03-2026", 10);
runHFSpeciesResolvedSpectraBeauty("27-03-2026", 10, true);
runHFSpeciesResolvedSpectraBothTunes("27-03-2026", 10);
runHFSpeciesResolvedSpectraMonash("27-03-2026", 10);
runHFSpeciesResolvedSpectraJunctions("27-03-2026", 10);
```

`Plot_HF_SingleParticlePtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C` draws the five multiplicity percentile spectra for one selected particle, with MONASH and JUNCTIONS side by side. If the selector is `Charm` or `Beauty`, it loops over the default particle set for that flavor. It understands particle selectors such as `Dzero`, `Dplus`, `Dminus`, `Dsplus`, `Dsminus`, `Lambdac`, `barLambdac`, `Bplus`, `Bminus`, `Bzero`, `barB0`, `Bs0`, `barBs0`, `Bcplus`, `Bcminus`, `Lambdab`, and `barLambdab`, with additional heavy beauty baryons available when the extra switch is enabled.

```bash
root -l -b -q 'plotting/PtMultiplicity/Plot_HF_SingleParticlePtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C("27-03-2026","Dzero",10)'
root -l -b -q 'plotting/PtMultiplicity/Plot_HF_SingleParticlePtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C("27-03-2026","Charm",10)'
```

The wrappers are:

```cpp
.L "plotting/PtMultiplicity/Plot_HF_SingleParticlePtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C"
runHFSingleParticleSpectra("27-03-2026", "Dzero", 10);
runHFSingleParticleSpectraCharm("27-03-2026", 10);
runHFSingleParticleSpectraBeauty("27-03-2026", 10, true);
```

`Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples.C` integrates over the full multiplicity axis and draws minimum-bias spectra. A flavor selector makes the species-overlay comparison and also the single-particle side-by-side canvases. A particle selector makes only that particle.

```bash
root -l -b -q 'plotting/PtMultiplicity/Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples.C("27-03-2026","Charm",10)'
root -l -b -q 'plotting/PtMultiplicity/Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples.C("27-03-2026","Bplus",10)'
```

The wrappers are:

```cpp
.L "plotting/PtMultiplicity/Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples.C"
runHFMinimumBiasSpectraCharm("27-03-2026", 10);
runHFMinimumBiasSpectraBeauty("27-03-2026", 10, true);
runHFMinimumBiasSpectraBoth("27-03-2026", 10);
```

## Combined Plot-Ready ROOT File

`Build_HF_CombinedSubsamplesFile.C` builds a compact ROOT file that stores the same combined observables used by the plotting macros. It reads the subsample files, writes source 2D histograms, minimum-bias spectra, multiplicity-class spectra, mean-and-SEM multiplicity histograms, and aggregate selected-particle sums into one file. The output layout is organized as `<Flavor>/<Tune>/Metadata`, `<Flavor>/<Tune>/Multiplicity`, `<Flavor>/<Tune>/Source2D`, `<Flavor>/<Tune>/Spectra/MinimumBias`, and `<Flavor>/<Tune>/Spectra/ByMultiplicity/<class-tag>`.

The default output path is:

```text
AnalyzedData/<DATE>/hf_combined_plot_histograms.root
```

The call is:

```cpp
.L "plotting/PtMultiplicity/Build_HF_CombinedSubsamplesFile.C"
runHFCombinedSubsamplesFile("27-03-2026", 10);
runHFCombinedSubsamplesFile("27-03-2026", 10, true);
runHFCombinedSubsamplesFile("27-03-2026", 10, false, "AnalyzedData/27-03-2026/custom.root");
```

This builder is useful when the expensive part is not making the plots but repeatedly reopening many subsample files. It does not replace the plotting macros; it packages their derived histogram inputs.

## Practical Checks

If a macro cannot open files, confirm the date and the subsample count. If a macro silently chooses an unexpected folder, pass the date explicitly instead of relying on latest-date detection. If charge-separated antiparticle plots are empty, check whether the analysis was run with `CHARGE_MODE=separate`; combined-only files cannot supply `Bar` histograms for selectors that explicitly request antiparticles.

If ROOT reports that an object is missing, inspect one analyzed file with `rootls`, which ships with ROOT:

```bash
rootls -l AnalyzedData/27-03-2026/Charm/hf_MONASH_sub0.root
```
