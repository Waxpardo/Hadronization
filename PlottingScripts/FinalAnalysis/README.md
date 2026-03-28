# FinalAnalysis Plotting

This directory contains the final-analysis plotting macro(s) that compare analyzed heavy-flavour outputs stored in:

```text
Hadronization/AnalyzedData/<DATE>/
```

At the moment, the main macros in this directory are:

```text
Plot_MultiplicityDistributions_TwoSamples.C
Plot_SelectedParticleYields_IndependentVsCombined.C
```

## What the macro does

`Plot_MultiplicityDistributions_TwoSamples.C` compares the multiplicity distributions of two analyzed samples and produces four plots:

- Charm MONASH
- Charm JUNCTIONS
- Beauty MONASH
- Beauty JUNCTIONS

For each plot, the macro overlays two samples:

- `Independent Sample`
- `Combined Sample`

The plot title is centered and the output is written in multiple formats.

## Automatic sample selection

If the macro is run with no date arguments, it automatically:

1. scans `AnalyzedData/`
2. finds dated folders matching the format `DD-MM-YYYY`
3. sorts them by date
4. picks the two most recent folders

This means the default behavior is:

```bash
root -l -b -q 'PlottingScripts/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C'
```

and the macro will compare the latest two dated analysis folders automatically.

## Explicit sample selection

If you want to compare two specific folders instead, pass both date tags explicitly:

```bash
root -l -b -q 'PlottingScripts/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C("12-01-2026","27-03-2026",10,true)'
```

Arguments are:

- `dateA`: first analysis folder name inside `AnalyzedData`
- `dateB`: second analysis folder name inside `AnalyzedData`
- `nSub`: number of subsamples to read
- `normalize`: if `true`, normalize each summed multiplicity histogram to unit integral before plotting

If only one date is given and the other is omitted, the macro stops with an error. You should provide either:

- both dates, or
- no dates

## How sample type detection works

The macro determines whether a folder corresponds to an independent or combined sample from the file names it finds.

### Independent sample

Legacy split analyses are detected through files such as:

```text
AnalyzedData/<DATE>/Charm/ccbar_MONASH_sub0.root
AnalyzedData/<DATE>/Beauty/bbbar_MONASH_sub0.root
```

If these are found, the folder is labeled:

```text
Independent Sample
```

### Combined sample

Unified heavy-flavour analyses are detected through files such as:

```text
AnalyzedData/<DATE>/Charm/hf_MONASH_sub0.root
AnalyzedData/<DATE>/Beauty/hf_MONASH_sub0.root
```

If these are found, the folder is labeled:

```text
Combined Sample
```

## Supported input naming schemes

The macro supports both the older split analysis output and the newer unified heavy-flavour output.

### Legacy split files

Charm:

```text
ccbar_MONASH_sub0.root
ccbar_JUNCTIONS_sub0.root
```

Beauty:

```text
bbbar_MONASH_sub0.root
bbbar_JUNCTIONS_sub0.root
```

### Unified heavy-flavour files

Charm:

```text
hf_MONASH_sub0.root
hf_JUNCTIONS_sub0.root
```

Beauty:

```text
hf_MONASH_sub0.root
hf_JUNCTIONS_sub0.root
```

For both schemes, the macro reads the histogram:

```text
fHistMultiplicity
```

from each subsample ROOT file and sums the subsamples before drawing.

## Output files

The macro writes plots to:

```text
Hadronization/PlottingScripts/FinalAnalysis/Plots/
```

For each of the four comparisons, it saves:

- `.png`
- `.pdf`
- `.C`

The `.C` file is a ROOT canvas macro created by `SaveAs`, not the source plotting macro itself.

Typical output names look like:

```text
MultiplicityComparison_Charm_MONASH_<DATEA>_vs_<DATEB>.png
MultiplicityComparison_Charm_MONASH_<DATEA>_vs_<DATEB>.pdf
MultiplicityComparison_Charm_MONASH_<DATEA>_vs_<DATEB>.C
```

## Wrapper function

The macro also provides a small wrapper function:

```cpp
runFinalMultiplicityComparison(const char* dateA = "",
                               const char* dateB = "",
                               int nSub = 10,
                               bool normalize = true);
```

Example interactive ROOT session:

```bash
root -l
```

```cpp
.L "PlottingScripts/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C"
runFinalMultiplicityComparison();
runFinalMultiplicityComparison("12-01-2026", "27-03-2026", 10, true);
```

## Selected particle yields

The second macro in this directory is:

```text
Plot_SelectedParticleYields_IndependentVsCombined.C
```

It plots per-event yields for the following charge-conjugate-combined species:

- `B±`
- `B0 / anti-B0`
- `lambda b / anti-lambda b`
- `D±`
- `D0 / anti-D0`
- `lambda c / anti-lambda c`

The macro produces four plots:

- Beauty MONASH
- Beauty JUNCTIONS
- Charm MONASH
- Charm JUNCTIONS

Each plot compares:

- `Independent Sample`
- `Combined Sample`

### Default folder resolution

If no folder names are passed, the macro automatically looks for:

- the latest independent analyzed folder
- the latest combined analyzed folder

under:

```text
AnalyzedData/
```

### Explicit folder selection

You can also choose the two folders explicitly:

```bash
root -l -b -q 'PlottingScripts/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C("12-01-2026","27-03-2026",10)'
```

Arguments are:

- `independentTag`: independent sample folder name in `AnalyzedData`
- `combinedTag`: combined sample folder name in `AnalyzedData`
- `nSub`: number of subsamples

### Important note on charge-conjugate states

The analyzed ROOT files store these species using charge-conjugate-combined histograms because the analysis macros fill with `abs(PDG)`.

This means:

- `B±` is read from `fHistPtBplus`
- `D±` is read from `fHistPtDplus`
- `B0 / anti-B0`, `D0 / anti-D0`, `Lambdab / anti-Lambdab`, and `Lambdac / anti-Lambdac` are also charge-conjugate combined

The macro therefore uses the full combined analyzed histogram yield:

```text
histogram integral / N_events
```

### Input histogram mapping

The macro reads from the analyzed species histograms written by the analysis macros:

- Beauty:
  - `fHistPtBplus`
  - `fHistPtBzero`
  - `fHistPtLambdab`
- Charm:
  - `fHistPtDplus`
  - `fHistPtDzero`
  - `fHistPtLambdac` as the canonical charge-conjugate-combined histogram name
  - `fHistPtLambdacPlus` as a legacy compatibility fallback

### Wrapper function

The macro also provides:

```cpp
runSelectedParticleYieldPlots(const char* independentTag = "",
                              const char* combinedTag = "",
                              int nSub = 10);
```

Example interactive ROOT session:

```cpp
.L "PlottingScripts/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C"
runSelectedParticleYieldPlots();
runSelectedParticleYieldPlots("12-01-2026", "27-03-2026", 10);
```

## Notes

- The macro resolves the Hadronization base path from `HADRONIZATION_BASE`, the macro location, `base_path.txt`, or the current working directory.
- If fewer than two dated folders exist in `AnalyzedData/`, the automatic mode cannot run.
- If the `Plots/` directory does not exist, the macro creates it automatically.
