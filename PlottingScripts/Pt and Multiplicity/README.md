# Pt and Multiplicity Plotting

This directory contains the plotting macros that read the analyzed heavy-flavor ROOT files and produce PNG plots for charm and beauty baryon-to-meson studies as a function of `pT` and multiplicity.

The macros read analyzed subsamples from:

```text
Hadronization/AnalyzedData/<DATE>/Beauty/
Hadronization/AnalyzedData/<DATE>/Charm/
```

and write plots to:

```text
Hadronization/PlottingScripts/Pt and Multiplicity/Plots/
```

## Workflow

1. Run the analysis macros first so that the subsample ROOT files exist in:
   - `AnalyzedData/<DATE>/Beauty/`
   - `AnalyzedData/<DATE>/Charm/`
2. Go to the Hadronization base directory.
3. Run one or more plotting macros for a specific date such as `12-01-2026`.
4. Collect the PNG outputs from `PlottingScripts/Pt and Multiplicity/Plots/`.

## Input structure

The plotting macros expect files with names like:

```text
AnalyzedData/<DATE>/Beauty/bbbar_MONASH_sub0.root
AnalyzedData/<DATE>/Beauty/bbbar_JUNCTIONS_sub0.root
AnalyzedData/<DATE>/Charm/ccbar_MONASH_sub0.root
AnalyzedData/<DATE>/Charm/ccbar_JUNCTIONS_sub0.root
```

The number of subsamples passed to the plotting macro must match the number of subsamples produced by the analysis step.

## Date handling

- If a date is passed explicitly, the macro reads that folder.
- If no date is passed, the macro looks for the latest dated folder inside `AnalyzedData/`.
- The expected date format is:

```text
DD-MM-YYYY
```

## Output location

All plots are written to:

```text
PlottingScripts/Pt and Multiplicity/Plots/
```

Important: the output file names do not include the date. Running the same macro for a different date will overwrite plots with the same name unless the files are moved or renamed.

## Base path resolution

The plotting macros are not tied to one machine.

They resolve the Hadronization base directory in this order:

1. `HADRONIZATION_BASE` environment variable
2. The location of the loaded macro inside the repo
3. `base_path.txt`
4. The current working directory as a last fallback

In normal use, running the macro from a clone of the repo is enough.

## Convenience wrappers

Each plotting macro also provides a short wrapper that can be called after loading the macro in an interactive ROOT session.

Available wrappers:

```cpp
runBeautyRatios(const char* dateTag = "", int nSub = 10, int rebinFactor = 2);
runCharmRatios(const char* dateTag = "", int nSub = 10, int rebinFactor = 2);
runCharmBeautyRatios(const char* dateTag = "", int nSub = 10, int rebinFactor = 2);
runHFSpectra(const char* dateTag = "", int nSub = 10);
runHFRatios(const char* dateTag = "", int nSub = 10, double ptMin = 0.0, double ptMax = -1.0);
```

Example interactive session:

```bash
root -l
```

```cpp
.L "PlottingScripts/Pt and Multiplicity/Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C"
runBeautyRatios("12-01-2026", 10, 2);

.L "PlottingScripts/Pt and Multiplicity/Plot_Charm_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C"
runCharmRatios("12-01-2026", 10, 2);

.L "PlottingScripts/Pt and Multiplicity/Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C"
runCharmBeautyRatios("12-01-2026", 10, 2);

.L "PlottingScripts/Pt and Multiplicity/Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C"
runHFSpectra("12-01-2026", 10);

.L "PlottingScripts/Pt and Multiplicity/Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C"
runHFRatios("12-01-2026", 10, 0.0, -1.0);
```

## Macros

### 1. Beauty baryon/meson ratios

Macro:

```text
Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C
```

What it makes:

- Beauty baryon / beauty meson ratio vs `pT`
- `Lambda_b / B+` ratio vs `pT`
- One plot per multiplicity percentile class

Default call:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C'
```

Specific date:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C("12-01-2026")'
```

Specific date, subsamples, and rebin:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C("12-01-2026", 10, 2)'
```

Interactive wrapper:

```bash
root -l
```

```cpp
.L "PlottingScripts/Pt and Multiplicity/Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C"
runBeautyRatios("12-01-2026", 10, 2);
```

Main outputs:

```text
Ratio_BeautyBaryonMeson_MONASH_vs_JUNCTIONS_*.png
Ratio_LambdabOverBplus_MONASH_vs_JUNCTIONS_*.png
```

### 2. Charm baryon/meson ratios

Macro:

```text
Plot_Charm_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C
```

What it makes:

- Charm baryon / charm meson ratio vs `pT`
- `Lambda_c / D+` ratio vs `pT`
- One plot per multiplicity percentile class

Default call:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_Charm_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C'
```

Specific date:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_Charm_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C("12-01-2026")'
```

Specific date, subsamples, and rebin:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_Charm_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C("12-01-2026", 10, 2)'
```

Interactive wrapper:

```cpp
.L "PlottingScripts/Pt and Multiplicity/Plot_Charm_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C"
runCharmRatios("12-01-2026", 10, 2);
```

Main outputs:

```text
Ratio_CharmBaryonMeson_MONASH_vs_JUNCTIONS_*.png
Ratio_LambdacOverDplus_MONASH_vs_JUNCTIONS_*.png
```

### 3. Combined charm and beauty baryon/meson ratios

Macro:

```text
Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C
```

What it makes:

- One plot per multiplicity percentile class
- Each plot compares:
  - beauty MONASH
  - beauty JUNCTIONS
  - charm MONASH
  - charm JUNCTIONS

Default call:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C'
```

Specific date:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C("12-01-2026")'
```

Specific date, subsamples, and rebin:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C("12-01-2026", 10, 2)'
```

Interactive wrappers:

```cpp
.L "PlottingScripts/Pt and Multiplicity/Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C"
runCharmBeautyRatios("12-01-2026", 10, 2);
```

or

```cpp
runBaryonMesonCharmBeauty("12-01-2026", 10, 2);
```

Main outputs:

```text
Ratio_BaryonMeson_CharmBeauty_MONASH_vs_JUNCTIONS_*.png
```

### 4. Heavy-flavor pT spectra vs multiplicity

Macro:

```text
Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C
```

What it makes:

- `Lambda_c` spectra by multiplicity percentile
- `D+` spectra by multiplicity percentile
- `Lambda_b` spectra by multiplicity percentile
- `B+` spectra by multiplicity percentile
- Separate plots for MONASH and JUNCTIONS

Default call:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C'
```

Specific date:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C("12-01-2026")'
```

Specific date and subsamples:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C("12-01-2026", 10)'
```

Interactive wrapper:

```cpp
.L "PlottingScripts/Pt and Multiplicity/Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C"
runHFSpectra("12-01-2026", 10);
```

Main outputs:

```text
Spectra_Lambdac_MONASH.png
Spectra_Lambdac_JUNCTIONS.png
Spectra_Dplus_MONASH.png
Spectra_Dplus_JUNCTIONS.png
Spectra_Lambdab_MONASH.png
Spectra_Lambdab_JUNCTIONS.png
Spectra_Bplus_MONASH.png
Spectra_Bplus_JUNCTIONS.png
```

Advanced custom-prefix wrapper:

```cpp
runHFSpectraWithPrefixes("/full/path/to/ccbar_MONASH_sub",
                         "/full/path/to/ccbar_JUNCTIONS_sub",
                         "/full/path/to/bbbar_MONASH_sub",
                         "/full/path/to/bbbar_JUNCTIONS_sub",
                         10);
```

### 5. Heavy-flavor ratios vs multiplicity percentile

Macro:

```text
Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C
```

What it makes:

- `Lambda_c / D+` vs multiplicity percentile
- `Lambda_b / B+` vs multiplicity percentile

Default call:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C'
```

Specific date:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C("12-01-2026")'
```

Specific date, subsamples, and pT range:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C("12-01-2026", 10, 0.0, -1.0)'
```

Notes:

- `ptMin` and `ptMax` define the integrated `pT` range.
- If `ptMax <= ptMin`, the macro integrates all `pT` bins.

Interactive wrapper:

```cpp
.L "PlottingScripts/Pt and Multiplicity/Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C"
runHFRatios("12-01-2026", 10, 0.0, -1.0);
```

Main outputs:

```text
Ratio_Lambdac_over_Dplus_vsMult.png
Ratio_Lambdab_over_Bplus_vsMult.png
```

## Recommended usage

From the Hadronization base directory:

```bash
cd /path/to/Hadronization
```

Beauty ratios:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C("12-01-2026", 10, 2)'
```

Charm ratios:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_Charm_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C("12-01-2026", 10, 2)'
```

Combined charm and beauty:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C("12-01-2026", 10, 2)'
```

Spectra:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C("12-01-2026", 10)'
```

Ratios vs multiplicity:

```bash
root -l -b -q 'PlottingScripts/Pt and Multiplicity/Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C("12-01-2026", 10, 0.0, -1.0)'
```

## Common issues

### Missing files

If a macro reports missing ROOT files, check:

- that the analysis step already ran
- that the date exists under `AnalyzedData/`
- that `nSub` matches the available `sub0`, `sub1`, ..., `subN` files

### Wrong date selected

If no date is passed, the macro will use the latest dated folder it finds. Pass the date explicitly if a specific production must be used.

### Plots overwritten

The plots are always written to the same `Plots/` directory. If multiple productions must be kept, move or rename the files after each run.
