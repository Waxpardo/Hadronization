# AnalysisScripts (Multiplicity vs pT)

This directory contains the multi-file analysis macros and wrappers for bbbar and ccbar production. They read the ROOT files produced by the simulation jobs and build pT vs multiplicity histograms for heavy-flavor hadrons and pions.

All scripts resolve the Hadronization base path from `base_path.txt` at the project root, or from the environment variable `HADRONIZATION_BASE`.

## What each file does

### `bb_mult_pt_analysis_multi.C`
- Reads all ROOT files from:
  - `RootFiles/bbbar/MONASH/*.root`
  - `RootFiles/bbbar/JUNCTIONS/*.root`
- Requires each file to contain a TTree named `tree` with:
  - `vector<int> ID`
  - `vector<double> PT`
  - `int MULTIPLICITY`
- Splits the full event sample into `N` subsamples using round-robin event assignment.
- Writes one ROOT file per subsample and per tune into:
  - `AnalyzedData/<OUTPUT_TAG>/Beauty/`

### `cc_mult_pt_analysis_multi.C`
- Reads all ROOT files from:
  - `RootFiles/ccbar/MONASH/*.root`
  - `RootFiles/ccbar/JUNCTIONS/*.root`
- Uses the same `tree`, `ID`, `PT`, and `MULTIPLICITY` inputs.
- Splits the full event sample into `N` subsamples using round-robin event assignment.
- Writes one ROOT file per subsample and per tune into:
  - `AnalyzedData/<OUTPUT_TAG>/Charm/`

### `run_bb_analysis.sh`
- Wrapper for `bb_mult_pt_analysis_multi.C`
- Resolves the Hadronization base path
- Requires an output tag
- Optionally accepts the number of subsamples

### `run_cc_analysis.sh`
- Wrapper for `cc_mult_pt_analysis_multi.C`
- Resolves the Hadronization base path
- Requires an output tag
- Optionally accepts the number of subsamples

## How to run

From the Hadronization base:

```bash
./AnalysisScripts/run_bb_analysis.sh 12-01-2026
./AnalysisScripts/run_cc_analysis.sh 12-01-2026
```

To choose a different number of subsamples:

```bash
./AnalysisScripts/run_bb_analysis.sh 12-01-2026 20
./AnalysisScripts/run_cc_analysis.sh 12-01-2026 20
```

## Direct ROOT usage

From the Hadronization base:

```bash
root -l -b -q 'AnalysisScripts/bb_mult_pt_analysis_multi.C+(10, "12-01-2026")'
root -l -b -q 'AnalysisScripts/cc_mult_pt_analysis_multi.C+(10, "12-01-2026")'
```

## Output structure

If `AnalyzedData/<OUTPUT_TAG>/` does not exist, the macros create:

```text
AnalyzedData/<OUTPUT_TAG>/
AnalyzedData/<OUTPUT_TAG>/Beauty/
AnalyzedData/<OUTPUT_TAG>/Charm/
```

Beauty outputs are written to:

```text
AnalyzedData/<OUTPUT_TAG>/Beauty/
```

Charm outputs are written to:

```text
AnalyzedData/<OUTPUT_TAG>/Charm/
```

## Input requirements

The simulation outputs must exist in:

```text
RootFiles/bbbar/MONASH/
RootFiles/bbbar/JUNCTIONS/
RootFiles/ccbar/MONASH/
RootFiles/ccbar/JUNCTIONS/
```

Each `.root` file must contain the `tree` with `ID`, `PT`, and `MULTIPLICITY`.

## Count events utilities

The count scripts are in:

```text
AnalysisScripts/CountEvents/
```

Run them with:

```bash
./AnalysisScripts/CountEvents/count_events.sh
```

They print total event counts in:

```text
RootFiles/bbbar/MONASH
RootFiles/bbbar/JUNCTIONS
RootFiles/ccbar/MONASH
RootFiles/ccbar/JUNCTIONS
```
