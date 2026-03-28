# AnalysisScripts (Multiplicity vs pT / unified heavy-flavour analysis)

This directory contains the analysis macros and wrapper scripts used to process the ROOT files produced by the simulation jobs. The main purpose of these scripts is to build **pT vs multiplicity histograms** for heavy-flavour hadrons and pions, split the total statistics into **subsamples**, and write the resulting histograms to organized output files for later ratio, uncertainty, and comparison studies.

The directory currently supports **two analysis workflows**:

1. **Legacy split-channel analysis**
   - separate analysis for **bbbar** and **ccbar** production
   - input files come from the old split simulation layout
   - useful for continuity with older analyses

2. **Unified heavy-flavour analysis**
   - a single analysis pass over the new combined heavy-flavour sample
   - reads ROOT files that contain **both charm and beauty** in the same `tree`
   - writes Beauty and Charm outputs separately, but fills them in one pass
   - this is the recommended workflow for the current balancing and hadronization studies

All scripts resolve the Hadronization base path from:
- `HADRONIZATION_BASE` if set
- otherwise `base_path.txt` at the project root
- otherwise the local directory structure

---

## Directory overview

The main files in this directory are:

### Legacy split analysis
- `bb_mult_pt_analysis_multi.C`
- `cc_mult_pt_analysis_multi.C`
- `run_bb_analysis.sh`
- `run_cc_analysis.sh`

### Unified heavy-flavour analysis
- `hf_mult_pt_analysis_multi.C`
- `run_hf_analysis.sh`

### Utilities
- `CountEvents/`
- any additional helper scripts/macros placed in subdirectories

---

## Analysis concepts

All analysis macros in this directory follow the same broad logic:

1. Read many simulation ROOT files from one or more input directories.
2. Access the `tree` in each file.
3. Read event-level multiplicity and per-particle kinematics / IDs.
4. Split all events into `N` subsamples using **round-robin assignment**:
   - event 0 → subsample 0
   - event 1 → subsample 1
   - ...
   - event `N` → subsample 0 again
5. Fill histograms separately for each subsample.
6. Write one ROOT output file per subsample and per tune.

This structure is designed so that:
- the total statistics are distributed evenly across subsamples
- the subsamples can be used later for statistical comparisons and uncertainty propagation
- MONASH and JUNCTIONS can be analyzed with the same code path

All three `*_mult_pt_analysis_multi.C` macros now also write:
- `fHistEventCount` for explicit event normalization

By default, species-resolved histograms are charge-conjugate combined. The macros can also optionally write additional `Particle` and `Bar` split histograms while keeping the combined histogram names for compatibility.

---

## Legacy split analysis scripts

These scripts analyze the older **split simulation output**, where beauty and charm were generated in separate jobs.

## `bb_mult_pt_analysis_multi.C`

This macro:
- reads all ROOT files from:
  - `RootFiles/bbbar/MONASH/*.root`
  - `RootFiles/bbbar/JUNCTIONS/*.root`
- expects each file to contain a TTree named `tree`
- builds multiplicity and pT histograms for:
  - beauty mesons
  - beauty baryons
  - specific beauty species
  - pions
- splits the full event sample into `N` subsamples using round-robin event assignment
- writes one ROOT file per subsample and per tune into:
  - `AnalyzedData/<OUTPUT_TAG>/Beauty/`

### Expected input branches
The legacy beauty macro expects the input `tree` to contain:
- `vector<int> ID`
- `vector<double> PT`
- `int MULTIPLICITY`

### Main output histograms
Examples of histograms written by the beauty macro:
- `fHistEventCount`
- `fHistMultiplicity`
- `fHistPDGMult`
- `fHistPtBeautyMesons`
- `fHistPtBeautyBaryons`
- `fHistPtBplus`
- `fHistPtBzero`
- `fHistPtBs0`
- `fHistPtBcplus`
- `fHistPtLambdab`
- `fHistPtSigmabPlus`
- `fHistPtSigmabZero`
- `fHistPtSigmabMinus`
- `fHistPtXibZero`
- `fHistPtXibMinus`
- `fHistPtOmegabMinus`
- `fHistPtPionsCharged`
- `fHistPtPiPlus`
- `fHistPtPiMinus`
- `fHistPtPi0`

---

## `cc_mult_pt_analysis_multi.C`

This macro:
- reads all ROOT files from:
  - `RootFiles/ccbar/MONASH/*.root`
  - `RootFiles/ccbar/JUNCTIONS/*.root`
- expects each file to contain a TTree named `tree`
- builds multiplicity and pT histograms for:
  - charm mesons
  - charm baryons
  - specific charm species
  - pions
- splits the full event sample into `N` subsamples using round-robin event assignment
- writes one ROOT file per subsample and per tune into:
  - `AnalyzedData/<OUTPUT_TAG>/Charm/`

### Expected input branches
The legacy charm macro expects the input `tree` to contain:
- `vector<int> ID`
- `vector<double> PT`
- `int MULTIPLICITY`

### Main output histograms
Examples of histograms written by the charm macro:
- `fHistEventCount`
- `fHistMultiplicity`
- `fHistPDGMult`
- `fHistPtCharmMesons`
- `fHistPtCharmBaryons`
- `fHistPtDplus`
- `fHistPtDzero`
- `fHistPtDsplus`
- `fHistPtLambdac`
- `fHistPtPionsCharged`
- `fHistPtPiPlus`
- `fHistPtPiMinus`
- `fHistPtPi0`

---

## Legacy wrapper scripts

## `run_bb_analysis.sh`

This is a shell wrapper for `bb_mult_pt_analysis_multi.C`.

It:
- resolves the Hadronization base path
- exports `HADRONIZATION_BASE`
- moves to the Hadronization base directory
- sources `setupEnv.sh` so that `root` is available
- calls the ROOT macro with the requested number of subsamples and charge mode

### Usage
```bash
./AnalysisScripts/run_bb_analysis.sh OUTPUT_TAG [NSUB] [CHARGE_MODE]
./AnalysisScripts/run_bb_analysis.sh OUTPUT_TAG [CHARGE_MODE] [NSUB]
```

Example:
```bash
./AnalysisScripts/run_bb_analysis.sh 12-01-2026
./AnalysisScripts/run_bb_analysis.sh 12-01-2026 20
./AnalysisScripts/run_bb_analysis.sh 12-01-2026 20 separate
```

---

## `run_cc_analysis.sh`

This is a shell wrapper for `cc_mult_pt_analysis_multi.C`.

It:
- resolves the Hadronization base path
- exports `HADRONIZATION_BASE`
- moves to the Hadronization base directory
- sources `setupEnv.sh` so that `root` is available
- calls the ROOT macro with the requested number of subsamples and charge mode

### Usage
```bash
./AnalysisScripts/run_cc_analysis.sh OUTPUT_TAG [NSUB] [CHARGE_MODE]
./AnalysisScripts/run_cc_analysis.sh OUTPUT_TAG [CHARGE_MODE] [NSUB]
```

Example:
```bash
./AnalysisScripts/run_cc_analysis.sh 12-01-2026
./AnalysisScripts/run_cc_analysis.sh 12-01-2026 20
./AnalysisScripts/run_cc_analysis.sh 12-01-2026 20 separate
```

---

## Unified heavy-flavour analysis scripts

These scripts analyze the newer **combined heavy-flavour simulation output**, where charm and beauty are stored in the same `tree`.

This is the preferred workflow for the current heavy-flavour balancing and hadronization studies.

## `hf_mult_pt_analysis_multi.C`

This macro:
- reads all ROOT files from:
  - `RootFiles/HF/MONASH/*.root`
  - `RootFiles/HF/JUNCTIONS/*.root`
- reads each input file only once
- fills **both Beauty and Charm histogram sets in the same pass**
- writes Beauty and Charm outputs separately
- splits the total event sample into `N` subsamples using round-robin event assignment

### Why this macro is preferred
Compared with separate charm/beauty macros, the unified macro:
- reads each file only once
- keeps charm and beauty subsample assignment perfectly aligned
- avoids duplicated file traversal
- matches the new unified simulation format directly

### Expected input branches
The unified macro expects the input `tree` to contain:
- `vector<int> ID`
- `vector<int> HFCLASS`
- `vector<double> PT`
- `int MULTIPLICITY`

It can also fall back to PDG-based classification if needed in some parts of the logic, but the intended classification comes from `HFCLASS`.

### Meaning of `HFCLASS`
- `5`  = beauty hadron only
- `4`  = charm hadron only
- `45` = `Bc` hadron
- `0`  = pion

### Default treatment of `Bc`
By default:
- Beauty output includes `HFCLASS == 5` and `HFCLASS == 45`
- Charm output includes only `HFCLASS == 4`

So `Bc` hadrons are counted with Beauty only by default, to avoid double counting.

If you want `Bc` included in Charm too, this can be changed in the macro logic.

### Input directories
The unified macro reads from:
```text
RootFiles/HF/MONASH/
RootFiles/HF/JUNCTIONS/
```

### Output directories
The unified macro writes to:
```text
AnalyzedData/<OUTPUT_TAG>/Beauty/
AnalyzedData/<OUTPUT_TAG>/Charm/
```

### Output filenames
Beauty outputs:
```text
AnalyzedData/<OUTPUT_TAG>/Beauty/hf_MONASH_sub0.root
AnalyzedData/<OUTPUT_TAG>/Beauty/hf_MONASH_sub1.root
...
AnalyzedData/<OUTPUT_TAG>/Beauty/hf_JUNCTIONS_sub0.root
...
```

Charm outputs:
```text
AnalyzedData/<OUTPUT_TAG>/Charm/hf_MONASH_sub0.root
AnalyzedData/<OUTPUT_TAG>/Charm/hf_MONASH_sub1.root
...
AnalyzedData/<OUTPUT_TAG>/Charm/hf_JUNCTIONS_sub0.root
...
```

### Main Beauty histograms written
Examples:
- `fHistEventCount`
- `fHistMultiplicity`
- `fHistPDGMult`
- `fHistPtBeautyMesons`
- `fHistPtBeautyBaryons`
- `fHistPtBplus`
- `fHistPtBzero`
- `fHistPtBs0`
- `fHistPtBcplus`
- `fHistPtLambdab`
- `fHistPtSigmabPlus`
- `fHistPtSigmabZero`
- `fHistPtSigmabMinus`
- `fHistPtXibZero`
- `fHistPtXibMinus`
- `fHistPtOmegabMinus`
- pion histograms

### Main Charm histograms written
Examples:
- `fHistEventCount`
- `fHistMultiplicity`
- `fHistPDGMult`
- `fHistPtCharmMesons`
- `fHistPtCharmBaryons`
- `fHistPtDplus`
- `fHistPtDzero`
- `fHistPtDsplus`
- `fHistPtLambdac`
- pion histograms

---

## Unified wrapper script

## `run_hf_analysis.sh`

This is the wrapper for the unified heavy-flavour analysis macro.

It:
- resolves the Hadronization base path
- exports `HADRONIZATION_BASE`
- changes into the Hadronization base directory
- sources `setupEnv.sh` so that `root` is available
- runs:
  - `AnalysisScripts/hf_mult_pt_analysis_multi.C`
- accepts an optional charge mode for writing extra split `Particle` and `Bar` histograms

### Usage
```bash
./AnalysisScripts/run_hf_analysis.sh OUTPUT_TAG [NSUB] [CHARGE_MODE]
./AnalysisScripts/run_hf_analysis.sh OUTPUT_TAG [CHARGE_MODE] [NSUB]
```

### Examples
```bash
./AnalysisScripts/run_hf_analysis.sh 27-03-2026
./AnalysisScripts/run_hf_analysis.sh 27-03-2026 20
./AnalysisScripts/run_hf_analysis.sh 27-03-2026 20 separate
```

### Meaning of `OUTPUT_TAG`
`OUTPUT_TAG` is simply the output folder name under `AnalyzedData/`.

For example:

```bash
./AnalysisScripts/run_hf_analysis.sh 27-03-2026
```

creates outputs in:

```text
AnalyzedData/27-03-2026/Beauty/
AnalyzedData/27-03-2026/Charm/
```

You can also use more descriptive tags, e.g.

```bash
./AnalysisScripts/run_hf_analysis.sh 27-03-2026_HF_10M
```

which creates:

```text
AnalyzedData/27-03-2026_HF_10M/Beauty/
AnalyzedData/27-03-2026_HF_10M/Charm/
```

---

## How to run the analyses

## Legacy split analyses

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

To also write split charge-conjugate histograms:

```bash
./AnalysisScripts/run_bb_analysis.sh 12-01-2026 20 separate
./AnalysisScripts/run_cc_analysis.sh 12-01-2026 20 separate
```

---

## Unified heavy-flavour analysis

From the Hadronization base:

```bash
./AnalysisScripts/run_hf_analysis.sh 27-03-2026
```

With a different number of subsamples:

```bash
./AnalysisScripts/run_hf_analysis.sh 27-03-2026 20
```

To also write split charge-conjugate histograms:

```bash
./AnalysisScripts/run_hf_analysis.sh 27-03-2026 20 separate
```

---

## Direct ROOT usage

## Legacy split macros
From the Hadronization base:

```bash
root -l -b -q 'AnalysisScripts/bb_mult_pt_analysis_multi.C+(10, "12-01-2026", "combined")'
root -l -b -q 'AnalysisScripts/cc_mult_pt_analysis_multi.C+(10, "12-01-2026", "combined")'
```

## Unified heavy-flavour macro
From the Hadronization base:

```bash
root -l -b -q 'AnalysisScripts/hf_mult_pt_analysis_multi.C+(10, "27-03-2026", "combined")'
```

---

## Input requirements

## Legacy split inputs

The legacy split analysis expects simulation outputs in:

```text
RootFiles/bbbar/MONASH/
RootFiles/bbbar/JUNCTIONS/
RootFiles/ccbar/MONASH/
RootFiles/ccbar/JUNCTIONS/
```

Each `.root` file must contain a `tree` with at least:
- `ID`
- `PT`
- `MULTIPLICITY`

## Unified heavy-flavour inputs

The unified analysis expects simulation outputs in:

```text
RootFiles/HF/MONASH/
RootFiles/HF/JUNCTIONS/
```

Each `.root` file must contain a `tree` with at least:
- `ID`
- `PT`
- `MULTIPLICITY`

and ideally:
- `HFCLASS`

---

## Output structure

If `AnalyzedData/<OUTPUT_TAG>/` does not exist, the macros create the needed directories automatically.

Typical structure:

```text
AnalyzedData/<OUTPUT_TAG>/
AnalyzedData/<OUTPUT_TAG>/Beauty/
AnalyzedData/<OUTPUT_TAG>/Charm/
```

### Legacy split outputs
- Beauty outputs are written to:
  ```text
  AnalyzedData/<OUTPUT_TAG>/Beauty/
  ```
- Charm outputs are written to:
  ```text
  AnalyzedData/<OUTPUT_TAG>/Charm/
  ```

### Unified outputs
- Beauty outputs are written to:
  ```text
  AnalyzedData/<OUTPUT_TAG>/Beauty/
  ```
- Charm outputs are written to:
  ```text
  AnalyzedData/<OUTPUT_TAG>/Charm/
  ```

The directory layout is the same; only the input source and analysis logic differ.

---

## Subsamples and round-robin assignment

All macros in this directory use **round-robin subsample assignment**.

If `NSUB = 10`, then:
- event 0 goes to subsample 0
- event 1 goes to subsample 1
- ...
- event 9 goes to subsample 9
- event 10 goes to subsample 0 again

This ensures:
- nearly equal event counts per subsample
- deterministic splitting
- reproducibility independent of file boundaries

This is useful when later building:
- statistical uncertainties
- subsample-based ratios
- significance estimates
- tune comparisons

---

## Common warnings and notes

## ROOT histogram replacement warnings
When many histogram sets are created in a single ROOT session with identical histogram names, ROOT may print warnings like:

```text
Warning in <TROOT::Append>: Replacing existing TH1: ...
```

These warnings are usually harmless in this workflow, because:
- the histogram sets belong to different subsamples and/or different output files
- the actual output files are written separately

They can be avoided by disabling automatic histogram registration in memory:

```cpp
TH1::AddDirectory(kFALSE);
```

This is recommended for large batch analyses.

## Missing `root` command
If a wrapper script fails with:

```text
root: command not found
```

then the environment was not loaded. The wrappers in this repo now source `setupEnv.sh` automatically, but for direct ROOT usage you should still do:

```bash
source ./setupEnv.sh
```

before running the wrapper manually.

## Empty input directory
If no `.root` files are found in the expected input directory, the macro will not produce outputs. Always check that the corresponding `RootFiles/...` directory exists and contains finished simulation outputs before running the analysis.

## Pion checks
Some macros include warnings if zero pion entries are found in the input TTrees. This typically indicates that the producer did not save pions in the particle branches.

---

## Count events utilities

The event-count scripts are in:

```text
AnalysisScripts/CountEvents/
```

Run them with:

```bash
./AnalysisScripts/CountEvents/count_events.sh
```

The legacy count scripts are typically organized for the old split layout:
- `RootFiles/bbbar/MONASH`
- `RootFiles/bbbar/JUNCTIONS`
- `RootFiles/ccbar/MONASH`
- `RootFiles/ccbar/JUNCTIONS`

If you are working with the new unified heavy-flavour production, adapt the count scripts or create a new one for:

```text
RootFiles/HF/MONASH
RootFiles/HF/JUNCTIONS
```

---

## Recommended workflow

## Use the legacy split analysis when:
- you are processing older `bbbar` / `ccbar` samples
- you need direct continuity with previous analyses
- you want separate single-channel studies

## Use the unified heavy-flavour analysis when:
- you are processing the new `HF` production
- you want charm and beauty analyzed in one consistent pass
- you want the same subsample assignment for both sectors
- you are doing balancing and hadronization studies with the new unified sample

For the current combined charm+beauty production, the recommended entry point is:

```bash
./AnalysisScripts/run_hf_analysis.sh <OUTPUT_TAG> [NSUB] [CHARGE_MODE]
```

---

## Summary

### Legacy split analysis
- Inputs:
  - `RootFiles/bbbar/...`
  - `RootFiles/ccbar/...`
- Wrappers:
  - `run_bb_analysis.sh`
  - `run_cc_analysis.sh`
- Macros:
  - `bb_mult_pt_analysis_multi.C`
  - `cc_mult_pt_analysis_multi.C`

### Unified heavy-flavour analysis
- Inputs:
  - `RootFiles/HF/MONASH`
  - `RootFiles/HF/JUNCTIONS`
- Wrapper:
  - `run_hf_analysis.sh`
- Macro:
  - `hf_mult_pt_analysis_multi.C`

The unified heavy-flavour analysis is the preferred workflow for the current generation setup.
