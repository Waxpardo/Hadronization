************************************************************************************
** Heavy-flavour hadronization studies in pp collisions with PYTHIA8 and ROOT     **
************************************************************************************

This repository contains the simulation, analysis, and plotting code used for heavy-flavour
hadronization studies in pp collisions. The current workflow supports both:

1. A recommended unified heavy-flavour chain where charm and beauty are generated in the same
   PYTHIA run.
2. A legacy split chain where charm and beauty are generated and analysed independently.


***********************
** Repository layout **
***********************

- SimulationScripts
  PYTHIA8 producers, settings cards, and the simulation Makefile.

- AnalysisScripts
  ROOT macros and shell wrappers that convert simulation ROOT trees into analysed histograms.

- PlottingScripts/Pt and Multiplicity
  Multiplicity, spectra, and baryon-to-meson plotting macros for the analysed outputs.

- PlottingScripts/FinalAnalysis
  Comparison plots between analysed samples, including multiplicity and selected-particle-yield
  summaries.

- Balancing_and_Sampling
  Additional balancing, sampling, and uncertainty-processing scripts.

- RootFiles
  Raw simulation outputs, typically grouped by workflow and tune.

- AnalyzedData
  Analysed ROOT outputs written by the `*_mult_pt_analysis_multi.C` macros.

- Jobs and logs
  Condor work directories and log files.

- setupEnv.sh
  Local environment setup for ROOT and PYTHIA8.

- runCondorJob.sh, submitCondor_10M.sub, submitCondor_hf_10M.sub, update_submit_paths.sh
  Condor entrypoints for the split and unified workflows.


**************************
** Recommended workflow **
**************************

The recommended production chain is:

1. Generate unified heavy-flavour events with
   `SimulationScripts/heavyflavourcorrelations_status.cpp`.
2. Analyse them with `AnalysisScripts/hf_mult_pt_analysis_multi.C` through
   `AnalysisScripts/run_hf_analysis.sh`.
3. Plot the analysed results with the macros under `PlottingScripts/Pt and Multiplicity` and
   `PlottingScripts/FinalAnalysis`.

The legacy split workflow remains available through:

- `SimulationScripts/bbbarcorrelations_status*.cpp`
- `SimulationScripts/ccbarcorrelations_status*.cpp`
- `AnalysisScripts/bb_mult_pt_analysis_multi.C`
- `AnalysisScripts/cc_mult_pt_analysis_multi.C`

This split chain is still useful for independent charm-only and beauty-only reference samples.


************************
** Analysis outputs   **
************************

The current analysis macros write analysed ROOT files under:

- `AnalyzedData/<TAG>/Beauty/`
- `AnalyzedData/<TAG>/Charm/`

Important conventions:

- The analysed files contain an explicit `fHistEventCount` histogram for event normalization.
- Species-resolved histograms are charge-conjugate combined by default.
- The wrappers accept an optional `CHARGE_MODE` argument:
  - `combined` (default)
  - `separate`
- In `separate` mode, the combined histograms are still written and additional split
  `Particle` / `Bar` histograms are saved as well.
- Plotting macros assume combined histograms first and fall back to the split histograms if the
  combined ones are absent.


************************
** Local quick start  **
************************

From the repository base:

1. Load the environment

   source ./setupEnv.sh

2. Build the simulation executables

   make -C SimulationScripts

3. Run a small unified heavy-flavour test sample

   ./SimulationScripts/heavyflavourcorrelations_status monash \
     RootFiles/HF/MONASH/hf_MONASH_test.root 123 456

4. Analyse the current sample set

   ./AnalysisScripts/run_hf_analysis.sh 28-03-2026 10 combined

5. Produce the FinalAnalysis comparison plots

   root -l -b -q 'PlottingScripts/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C'
   root -l -b -q 'PlottingScripts/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C'

Legacy split examples:

   ./SimulationScripts/ccbarcorrelations_status RootFiles/ccbar/MONASH/ccbar_test.root 123 456
   ./SimulationScripts/bbbarcorrelations_status RootFiles/bbbar/MONASH/bbbar_test.root 123 456
   ./AnalysisScripts/run_cc_analysis.sh 28-03-2026 10 combined
   ./AnalysisScripts/run_bb_analysis.sh 28-03-2026 10 combined


************************
** Condor quick start **
************************

1. Set the repository base path

   echo "/absolute/path/to/Hadronization" > base_path.txt

2. Refresh the submit files and standard directory structure

   ./update_submit_paths.sh

3. Submit the recommended unified heavy-flavour production

   condor_submit submitCondor_hf_10M.sub

4. Submit the legacy split production if needed

   condor_submit submitCondor_10M.sub

For more detail on the Condor interface and argument formats, see `Condor_README.md`.


********************
** Where to look  **
********************

The most relevant documentation files are:

- `SimulationScripts/Simulation_README.md`
  Details of the simulation executables, settings cards, and Condor job layout.

- `AnalysisScripts/Analysis_README.md`
  Details of the analysed outputs, wrapper scripts, and histogram conventions.

- `PlottingScripts/Pt and Multiplicity/README.md`
  Multiplicity, spectra, and baryon-to-meson plotting macros.

- `PlottingScripts/FinalAnalysis/README.md`
  Final comparison plots between analysed samples.


***************
** Notes     **
***************

- The repository still contains older angular-correlation scripts and study macros. They remain
  useful for archival comparisons, but they are not the primary workflow for the current
  balancing and hadronization studies.
- Existing generated ROOT files and plots may reflect earlier conventions. When in doubt, prefer
  regenerating them with the current scripts and wrappers.
