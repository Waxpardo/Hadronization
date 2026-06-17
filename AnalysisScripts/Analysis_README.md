# Analysis Scripts

This directory contains the ROOT macros and shell wrappers that reduce simulation ROOT trees into the subsampled histogram files used by the plotting layer. We now treat the unified heavy-flavour analysis as the normal path and the split bbbar/ccbar analysis as the reference path for older independent samples.

## Base Path and Environment

The wrappers resolve the repository base from `base_path.txt` when it exists and otherwise from the local directory structure. They export `HADRONIZATION_BASE`, move to the repository base, source `setupEnv.sh`, and then call ROOT with ACLiC compilation. This means that in ordinary use you run the wrappers from the repository base and do not need to load ROOT separately, although direct ROOT calls still require the environment to be available.

```bash
./AnalysisScripts/run_hf_analysis.sh 27-03-2026
```

The wrappers accept the output tag, the number of subsamples, and the charge mode. The number of subsamples defaults to ten. The charge mode defaults to `combined`. The order of the last two arguments is intentionally flexible.

```bash
./AnalysisScripts/run_hf_analysis.sh 27-03-2026 10 combined
./AnalysisScripts/run_hf_analysis.sh 27-03-2026 combined 10
./AnalysisScripts/run_hf_analysis.sh 27-03-2026 10 separate
```

The `separate` mode writes additional `Particle` and `Bar` histograms for charge-separated plotting while keeping the charge-conjugate-combined histograms. The `combined` mode writes only the combined names. The plotting layer always prefers the combined names and only sums split histograms when a combined histogram is absent.

## Unified Heavy-Flavour Analysis

The current macro is `hf_mult_pt_analysis_multi.C`. It reads the combined-HF simulation files from:

```text
RootFiles/HF/MONASH
RootFiles/HF/JUNCTIONS
RootFiles/HF/CLOSEPACKING
```

It expects a `tree` with at least `ID`, `PT`, `MULTIPLICITY`, and preferably `HFCLASS`. The intended classification comes from `HFCLASS`, where beauty is `5`, charm is `4`, Bc is `45`, and pions are `0`. The macro can still use PDG information in parts of the logic, but the unified tree format is the correct input format for new productions.

The macro reads each raw ROOT file once. During that pass it fills beauty and charm histogram sets separately, assigns each event to a subsample by deterministic round-robin event index, and writes one output file per tune, flavor, and subsample. For the default ten-subsample run, the output layout is:

```text
AnalyzedData/<OUTPUT_TAG>/Beauty/hf_MONASH_sub0.root
AnalyzedData/<OUTPUT_TAG>/Beauty/hf_MONASH_sub1.root
AnalyzedData/<OUTPUT_TAG>/Beauty/hf_JUNCTIONS_sub0.root
AnalyzedData/<OUTPUT_TAG>/Beauty/hf_CLOSEPACKING_sub0.root
AnalyzedData/<OUTPUT_TAG>/Charm/hf_MONASH_sub0.root
AnalyzedData/<OUTPUT_TAG>/Charm/hf_JUNCTIONS_sub0.root
AnalyzedData/<OUTPUT_TAG>/Charm/hf_CLOSEPACKING_sub0.root
```

The wrapper call is:

```bash
./AnalysisScripts/run_hf_analysis.sh <OUTPUT_TAG> [NSUB] [CHARGE_MODE]
```

The direct ROOT call is:

```bash
root -l -b -q 'AnalysisScripts/hf_mult_pt_analysis_multi.C+(10,"27-03-2026","combined")'
```

There is also `hf_mult_pt_analysis_multi_100M` inside the macro as a convenience entry point. It uses the same analysis logic and only changes the intended tag convention.

The unified macro counts Bc hadrons with the beauty output by default and does not also count them in charm. This avoids double counting when charm and beauty summaries are later compared. If a later study needs Bc to contribute to charm as well, that is a physics choice and must be changed deliberately in the macro.

## Split Analysis

The split macros are `bb_mult_pt_analysis_multi.C` and `cc_mult_pt_analysis_multi.C`. They read the old independent production layout:

```text
RootFiles/bbbar/MONASH
RootFiles/bbbar/JUNCTIONS
RootFiles/ccbar/MONASH
RootFiles/ccbar/JUNCTIONS
```

The beauty wrapper is:

```bash
./AnalysisScripts/run_bb_analysis.sh 12-01-2026 10 combined
```

The charm wrapper is:

```bash
./AnalysisScripts/run_cc_analysis.sh 12-01-2026 10 combined
```

The split input tree is expected to contain `ID`, `PT`, and `MULTIPLICITY`, with the other kinematic and ancestry branches available from the producer. Since the split files do not have `HFCLASS`, the macros classify particles from the absolute PDG id. They write `bbbar_<TUNE>_sub<i>.root` into `AnalyzedData/<OUTPUT_TAG>/Beauty` and `ccbar_<TUNE>_sub<i>.root` into `AnalyzedData/<OUTPUT_TAG>/Charm`.

## Status Analysis Macros

`status_analysis_bb.C`, `status_analysis_cc.C`, and `status_analysis_qq.C` are older status-code and ancestry inspection macros. They work closer to the angular-correlation studies than to the current pT-versus-multiplicity reduction. The bb and cc versions inspect the split beauty and charm style inputs. The qq version includes broader ancestry tracing and sphericity-related helper logic. These macros are useful when the question is about production origin, mother relationships, status codes, and older correlation objects rather than the reduced `AnalyzedData` files used by the current plotting layer.

The Condor helper `submit_status_analysis.sh` submits `status_analysis_qq.C` over the combined-HF raw files. By default it covers `MONASH`, `JUNCTIONS`, and `CLOSEPACKING`; a single tune can be selected explicitly when only one production needs the status pass.

```bash
./submit_status_analysis.sh 100 all
./submit_status_analysis.sh 100 CLOSEPACKING
```

## Subsamples

All three analysis macros use round-robin event assignment. With ten subsamples, event zero goes to subsample zero, event one to subsample one, and event ten returns to subsample zero. This keeps event counts nearly equal and makes the split reproducible without depending on file boundaries.

The subsamples are the statistical unit used later by the plotting macros. Spectra are usually built once per subsample, normalized at the subsample level, and then combined as a mean with a standard error of the mean. Ratio plots follow the same principle by constructing a ratio per subsample before computing the plotted mean and error.

## Histograms Written

Every current analysis output writes `fHistEventCount`, `fHistTaggedEventCount`, `fHistMultiplicity`, `fHistTaggedMultiplicity`, and `fHistPDGMult`. The event count is the total number of events processed for that subsample. The tagged event count is the number of events relevant for the output flavor. The tagged multiplicity histogram is what the final-analysis multiplicity comparison prefers, because it compares charm-tagged or beauty-tagged event multiplicities rather than all events in a combined-HF file.

Beauty outputs write aggregate histograms called `fHistPtBeautyMesons` and `fHistPtBeautyBaryons`. The main species histograms are `fHistPtBplus`, `fHistPtBzero`, `fHistPtBs0`, `fHistPtBcplus`, `fHistPtLambdab`, `fHistPtSigmabPlus`, `fHistPtSigmabZero`, `fHistPtSigmabMinus`, `fHistPtXibZero`, `fHistPtXibMinus`, and `fHistPtOmegabMinus`. Pion histograms are `fHistPtPionsCharged`, `fHistPtPiPlus`, `fHistPtPiMinus`, and `fHistPtPi0`.

Charm outputs write aggregate histograms called `fHistPtCharmMesons` and `fHistPtCharmBaryons`. The main species histograms are `fHistPtDplus`, `fHistPtDzero`, `fHistPtDsplus`, `fHistPtLambdac`, `fHistPtLambdacPlus`, `fHistPtSigmacPlusPlus`, `fHistPtSigmacPlus`, `fHistPtSigmacZero`, `fHistPtXicPlus`, `fHistPtXicZero`, and `fHistPtOmegacZero`. The macro writes `fHistPtLambdac` as the canonical current name and keeps `fHistPtLambdacPlus` for compatibility with older plotting code.

In `separate` charge mode, the species histograms acquire additional names with `Particle` and `Bar` suffixes. For example, `fHistPtDplusParticle` and `fHistPtDplusBar` are written alongside `fHistPtDplus`. The same pattern is used for the supported beauty and charm species.

## Output Tags and Present Samples

The `OUTPUT_TAG` is simply the directory name under `AnalyzedData`. The current checkout includes older independent split samples dated `10-09-2025` and `12-01-2026`, a combined-HF sample dated `27-03-2026`, and the larger `08-04-2026_100M_Combined` and `08-04-2026_100M_Separate` reduced outputs. Pure date tags are interpreted by downstream plotting helpers when they sort folders of the form `DD-MM-YYYY`; descriptive tags remain valid analysis directories but are not part of the automatic latest-date ordering unless the plotting helper explicitly accepts them.

```text
AnalyzedData/10-09-2025
AnalyzedData/12-01-2026
AnalyzedData/27-03-2026
AnalyzedData/08-04-2026_100M_Combined
AnalyzedData/08-04-2026_100M_Separate
```

## Count Events Utility

`AnalysisScripts/CountEvents/count_events.sh` runs `count_events_bb_cc.C` from the repository base and then removes the ACLiC artifacts produced by that macro. It counts the current combined-HF raw files in `RootFiles/HF/MONASH`, `RootFiles/HF/JUNCTIONS`, and `RootFiles/HF/CLOSEPACKING`, and also keeps the old split bbbar and ccbar counts for reference productions.

```bash
./AnalysisScripts/CountEvents/count_events.sh
```

## Failure Modes

If a wrapper reports that `root` is missing, `setupEnv.sh` either could not be sourced or the ALICE CVMFS environment is unavailable on that machine. If a wrapper reports that an input directory is missing, check whether the raw production files are present under `RootFiles` on that host. If ROOT prints histogram replacement warnings during a large run, they are usually in-memory name reuse warnings and not output-file overwrites; the current macros use `TH1::AddDirectory(kFALSE)` style handling where needed and write each subsample to a separate file.

If a plotting macro later reports missing histograms, first check whether the analysis was run with the same `NSUB` that the plot is trying to read, and then check whether the sample is an `hf_` combined sample or a `bbbar_`/`ccbar_` split sample. The plotting layer can handle both naming schemes, but the files must be present for every requested subsample.
