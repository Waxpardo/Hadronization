# Analysis Scripts

This directory contains the ROOT macros and shell wrappers that reduce simulation ROOT trees into histogram files used by the plotting layer. The canonical publication balancing path is manifest-driven and uses `status_analysis_THnSparse_qq.C`. The `hf_mult_pt_analysis_multi.C` and split bbbar/ccbar workflows documented later are legacy or inclusive-spectrum references, not the canonical balancing reduction. See the top-level `REPRODUCIBILITY.md`.

## Canonical one-pass balancing analysis

`submit_status_analysis.sh` accepts a validated freeze directory, production
root, and analysis output root. It queues only the 300 raw paths enumerated in
`canonical_manifest.jsonl`; directory discovery and “first N files” selection
are forbidden.

```bash
./submit_status_analysis.sh \
  Production/<CAMPAIGN>/freeze \
  Production/<CAMPAIGN> \
  AnalysisOutput/<CAMPAIGN> \
  --dry-run

./submit_status_analysis.sh \
  Production/<CAMPAIGN>/freeze \
  Production/<CAMPAIGN> \
  AnalysisOutput/<CAMPAIGN> \
  --submit
```

Each job invokes `run_status_analysis.sh`, which reads one canonical raw file
once and writes all 300 signed ordered-pair ROOT files to a unique staging
directory. The directory is promoted only after
`Validation/validate_pair_directory.sh` passes. Each pair file contains
`summed MULTIPLICITY`, `hTrKinematics`, `hAsKinematics`, `hCorrelations`, and
the origin-decomposed correlation object plus immutable metadata.

The selector is
`hard_trigger_primary_ground__primary_ground_associate_v1`. Triggers satisfy
`pT > 1.0 GeV/c`, associates satisfy `pT > 0.15 GeV/c`, both satisfy
`|eta| <= 4`, and both are direct-primary generator-stable registry states.
Triggers additionally require resolved matching to the selected hard heavy
quark. Associates retain all origin categories. Pairs are ordered, so the
canonical analysis does not apply the legacy same-sign factor of 0.5.

After all analysis jobs validate, merge only the frozen central and block
manifests:

```bash
python3 tools/validate_analysis_outputs.py \
  Production/<CAMPAIGN>/freeze/canonical_manifest.jsonl \
  AnalysisOutput/<CAMPAIGN> \
  --report AnalysisOutput/<CAMPAIGN>/validation/analysis_outputs.json

./merge_root_files.sh \
  Production/<CAMPAIGN>/freeze \
  AnalysisOutput/<CAMPAIGN> \
  AnalyzedData \
  <OUTPUT_TAG>
```

The merge produces one complete-root directory and ten disjoint block
directories per tune. Existing final directories are never overwritten.

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

## Legacy unified inclusive analysis

The legacy/inclusive macro is `hf_mult_pt_analysis_multi.C`. It reads the combined-HF simulation files from:

```text
RootFiles/HF/MONASH
RootFiles/HF/JUNCTIONS
```

It expects a `tree` with at least `ID`, `PT`, `MULTIPLICITY`, and preferably `HFCLASS`. The intended classification comes from `HFCLASS`, where beauty is `5`, charm is `4`, Bc is `45`, and pions are `0`. The macro can still use PDG information in parts of the logic, but the unified tree format is the correct input format for new productions.

The macro reads each raw ROOT file once. During that pass it fills beauty and charm histogram sets separately, assigns each event to a subsample by deterministic round-robin event index, and writes one output file per tune, flavor, and subsample. For the default ten-subsample run, the output layout is:

```text
AnalyzedData/<OUTPUT_TAG>/Beauty/hf_MONASH_sub0.root
AnalyzedData/<OUTPUT_TAG>/Beauty/hf_MONASH_sub1.root
AnalyzedData/<OUTPUT_TAG>/Beauty/hf_JUNCTIONS_sub0.root
AnalyzedData/<OUTPUT_TAG>/Charm/hf_MONASH_sub0.root
AnalyzedData/<OUTPUT_TAG>/Charm/hf_JUNCTIONS_sub0.root
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

## Status-analysis history and compatibility

`status_analysis_bb.C`, `status_analysis_cc.C`, and `status_analysis_qq.C` are older status-code and ancestry inspection macros. They work closer to the angular-correlation studies than to the current pT-versus-multiplicity reduction. The bb and cc versions inspect the split beauty and charm style inputs. The qq version includes broader ancestry tracing and sphericity-related helper logic. These macros are useful when the question is about production origin, mother relationships, status codes, and older correlation objects rather than the reduced `AnalyzedData` files used by the current plotting layer.

`status_analysis_THnSparse_qq.C` is the canonical converter used by Paul's THnSparse plotting pipeline. It reads canonical raw HF production ROOT files and writes the signed-pair contract consumed by `PlottingScripts/improvedPlotting_THnSparse.C`.

The following discovery-based commands describe the legacy `Job700` production only and must not be used for a new canonical campaign:

```bash
./submit_status_analysis.sh ALL 100 Job700
./merge_root_files.sh ALL Job700 21_06_2026
./make_subsamples.sh
```

For large THnSparse outputs, `merge_root_files.sh` and `make_subsamples.sh` also support a hybrid merge backend. This is the recommended production setting when the charm-trigger pair files are large:

```bash
MERGE_BACKEND=hybrid HADD_JOBS=1 HADD_FINAL_JOBS=4 HADD_CHUNK_SIZE=10 ./merge_root_files.sh ALL Job700 21_06_2026
MERGE_BACKEND=hybrid HADD_JOBS=1 HADD_FINAL_JOBS=4 HADD_CHUNK_SIZE=10 ./make_subsamples.sh
```

For a single tune, replace `ALL` with `MONASH`, `JUNCTIONS`, or `CLOSEPACKING`. The submit wrapper reads raw files from `RootFiles/HF/<TUNE>` by default on the production filesystem and selects the first requested number of available files sorted by numeric job id. The merge wrapper writes `AnalyzedData/complete_root_21_06_2026_<TUNE>`, and the subsample wrapper writes `AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_<TUNE>`.

Subsamples are non-overlapping shuffled partitions by default. With no arguments, `make_subsamples.sh` runs the final paper default: all three tunes, ten independent 10-job subsamples per tune, `Job700` input, and `SUBSAMPLES_700` output. This covers all 100 jobs per tune.

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

`AnalysisScripts/CountEvents/count_events.sh` runs `count_events_bb_cc.C` from the repository base and then removes the ACLiC artifacts produced by that macro. It is written for the old split bbbar and ccbar layout.

```bash
./AnalysisScripts/CountEvents/count_events.sh
```

For the current combined-HF raw files, use `generated_heavy_flavor_summary.C`. It recursively scans one raw ROOT file or a directory of raw ROOT files, counts total processed events, reports the requested B, D, `Lambda_b`, and `Lambda_c` particle and antiparticle yields, prints a table, and writes the same table to CSV. In the default `auto` backend it uses the producer-level histograms, which are filled from the same stored final-state particles as the tree and are much faster for full 100M samples. Use the optional fifth argument `"tree"` if you specifically need a tree scan.

```bash
root -l -b -q 'AnalysisScripts/CountEvents/generated_heavy_flavor_summary.C++("RootFiles/HF/MONASH","monash_generated_hf_summary.csv")'
root -l -b -q 'AnalysisScripts/CountEvents/generated_heavy_flavor_summary.C++("RootFiles/HF/JUNCTIONS","junctions_generated_hf_summary.csv")'
root -l -b -q 'AnalysisScripts/CountEvents/generated_heavy_flavor_summary.C++("RootFiles/HF/CLOSEPACKING","closepacking_generated_hf_summary.csv")'
root -l -b -q 'AnalysisScripts/CountEvents/generated_heavy_flavor_summary.C++("RootFiles/HF/MONASH","monash_tree_scan.csv","tree","stored","tree")'
```

For the paper-ready table across all three tunes, call the LaTeX-table entry point after loading the macro:

```bash
root -l -b <<'ROOTCMDS'
.L AnalysisScripts/CountEvents/generated_heavy_flavor_summary.C+
generated_heavy_flavor_summary_latex_table("RootFiles/HF", "Paper/Tables/generated_heavy_flavor_summary.tex");
.q
ROOTCMDS
```

The current generated tree stores accepted final-state heavy hadrons and pions, not the full PYTHIA parton-level event record. Because of that, this macro normalizes the species yields to the accepted final-hadron heavy-flavour valence content available in the tree: each beauty-only hadron contributes one `b` or `bbar` unit, each charm-only hadron contributes one `c` or `cbar` unit, and each `Bc` hadron contributes one unit to both. A true generated pre-hadronization `b` or `c` quark count would require adding dedicated quark counters to the producer.

## Failure Modes

If a wrapper reports that `root` is missing, `setupEnv.sh` either could not be sourced or the ALICE CVMFS environment is unavailable on that machine. If a wrapper reports that an input directory is missing, check whether the raw production files are present under `RootFiles` on that host. If ROOT prints histogram replacement warnings during a large run, they are usually in-memory name reuse warnings and not output-file overwrites; the current macros use `TH1::AddDirectory(kFALSE)` style handling where needed and write each subsample to a separate file.

If a plotting macro later reports missing histograms, first check whether the analysis was run with the same `NSUB` that the plot is trying to read, and then check whether the sample is an `hf_` combined sample or a `bbbar_`/`ccbar_` split sample. The plotting layer can handle both naming schemes, but the files must be present for every requested subsample.
