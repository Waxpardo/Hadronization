# AnalysisScripts (Multiplicity vs pT)

This directory contains the multi-file analysis macros and small wrappers for bbbar and ccbar production. These tools aggregate the ROOT files produced by the simulation/Condor jobs and build pT–multiplicity histograms for hadrons and pions.

All scripts resolve the base path from `base_path.txt` (located at the Hadronization root) or from the environment variable `HADRONIZATION_BASE`.

## What each file does

### `bb_mult_pt_analysis_multi.C`
- Reads all ROOT files under:
  - `RootFiles/bbbar/MONASH/*.root`
  - `RootFiles/bbbar/JUNCTIONS/*.root`
- Each input file must contain a TTree named `tree` with branches:
  - `vector<int> ID`
  - `vector<double> PT`
  - `int MULTIPLICITY`
- Splits the full statistics into **N subsamples** (round‑robin by event).
- Writes one output ROOT file per subsample per tune to `AnalysisScripts/AnalyzedData/`:
  - `bbbar_MONASH_sub0.root ... bbbar_MONASH_sub(N-1).root`
  - `bbbar_JUNCTIONS_sub0.root ... bbbar_JUNCTIONS_sub(N-1).root`

### `cc_mult_pt_analysis_multi.C`
Same structure as the bbbar macro, but reads from:
- `RootFiles/ccbar/MONASH/*.root`
- `RootFiles/ccbar/JUNCTIONS/*.root`

Outputs (written to `AnalysisScripts/AnalyzedData/`):
- `ccbar_MONASH_sub0.root ... ccbar_MONASH_sub(N-1).root`
- `ccbar_JUNCTIONS_sub0.root ... ccbar_JUNCTIONS_sub(N-1).root`

### `run_bb_analysis.sh`
Small wrapper that runs `bb_mult_pt_analysis_multi.C` from the Hadronization base.
It sets a configurable number of subsamples (`NSUB`).

### `run_cc_analysis.sh`
Same as the bbbar wrapper, but for `cc_mult_pt_analysis_multi.C`.

## How to run

From the Hadronization base directory:

```bash
./AnalysisScripts/run_bb_analysis.sh
```

```bash
./AnalysisScripts/run_cc_analysis.sh
```

## Changing the number of subsamples

Edit `NSUB` inside the wrapper script:

```bash
NSUB=10
```

Each subsample is written to its own ROOT file under `AnalysisScripts/AnalyzedData/`, which is useful for statistical uncertainty estimates (jackknife‑style or subsample comparisons).

## Direct ROOT usage (no wrapper)

From the Hadronization base:

```bash
root -l -b -q 'AnalysisScripts/bb_mult_pt_analysis_multi.C+(10)'
root -l -b -q 'AnalysisScripts/cc_mult_pt_analysis_multi.C+(10)'
```

## Input requirements

Make sure the simulation outputs exist in:

```
RootFiles/bbbar/MONASH/
RootFiles/bbbar/JUNCTIONS/
RootFiles/ccbar/MONASH/
RootFiles/ccbar/JUNCTIONS/
```

and that each `.root` file contains the `tree` with `ID`, `PT`, and `MULTIPLICITY`.

## Output location

All analysis output ROOT files are written to:

```
AnalysisScripts/AnalyzedData/

## Count events utilities

The count scripts are in:

```
AnalysisScripts/CountEvents/
```

To run:

```bash
./AnalysisScripts/CountEvents/count_events.sh
```

This prints total event counts in:

```
RootFiles/bbbar/MONASH
RootFiles/bbbar/JUNCTIONS
RootFiles/ccbar/MONASH
RootFiles/ccbar/JUNCTIONS
```
```
