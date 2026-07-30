# Simulation Scripts

This directory contains the PYTHIA 8 event producers, settings cards, and build rules for the hadronization study. We now keep two simulation paths. The active path is the unified heavy-flavour producer, which generates charm and beauty in the same PYTHIA run. The older split path generates bbbar and ccbar samples separately, and it remains in the repository because the independent samples are still needed for reference comparisons.

## Build

The build uses ROOT, PYTHIA 8, and a C++17 compiler. The intended environment is loaded from the repository base with:

```bash
source ./setupEnv.sh
```

After the environment is present, the executables are built from the repository base with:

```bash
make -C SimulationScripts
```

The Makefile builds `heavyflavourcorrelations_status`, `bbbarcorrelations_status`, `bbbarcorrelations_status_JUNCTIONS`, `ccbarcorrelations_status`, and `ccbarcorrelations_status_JUNCTIONS`. It prefers the `PYTHIA8` environment path when that variable is present and otherwise falls back to `pythia8-config`. It deliberately allows `make clean` to run without ROOT or PYTHIA being loaded.

```bash
make -C SimulationScripts clean
```

## Unified Heavy-Flavour Producer

The current producer is `heavyflavourcorrelations_status.cpp`. It scans one
combined-hard-process configuration for charm, beauty, and Bc hadrons in a
single event record. The authoritative campaign interface is documented in
the repository-level `REPRODUCIBILITY.md`; the short commands below are
legacy development examples and do not create publication-authorized data.

The raw-v3 producer follows the signed heavy constituent through complete
PYTHIA mother ranges. Its
`signed_heavy_carrier_explicit_parent_event_unique_v2` post-pass enforces that
one selected hard quark is claimed by at most one final open-heavy hadron. If
several final hadrons share a fragmenting string/junction mother range and
claim the same hard carrier, all such assignments are marked unresolved with
`kDuplicateHardCarrier`. The conflicting index is retained in
`heavyConflictingHardC/B`, and the job metadata records conflict-group and
demotion counts for independent validation.

```bash
./SimulationScripts/heavyflavourcorrelations_status monash RootFiles/HF/MONASH/hf_MONASH_test.root 123 456
./SimulationScripts/heavyflavourcorrelations_status junctions RootFiles/HF/JUNCTIONS/hf_JUNCTIONS_test.root 123 456
./SimulationScripts/heavyflavourcorrelations_status closepacking RootFiles/HF/CLOSEPACKING/hf_CLOSEPACKING_test.root 123 456
```

The mode chooses between `pythiasettings_Hard_Low_ccbb_MONASH.cmnd`, `pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd`, and `pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd`. All three cards use proton-proton collisions at 14 TeV, `Tune:pp = 14`, `HardQCD:hardccbar = on`, `HardQCD:hardbbbar = on`, `PhaseSpace:pTHatMin = 1.`, and a weak-decay suppression through `ParticleDecays:limitTau0 = on` with `ParticleDecays:tau0Max = 0.01`. The JUNCTIONS card adds the string, beam-remnant, and color-reconnection parameters used for the junction comparison, including `ColourReconnection:allowJunctions = on`. The CLOSEPACKING card keeps the same combined-HF output contract and adds the Close Packing T1 settings.

The unified output is a ROOT file opened in `CREATE` mode, so an existing file with the same name is not silently overwritten by the producer. The tree is named `tree`. It contains vectors called `ID`, `HFCLASS`, `PT`, `ETA`, `Y`, `PHI`, `CHARGE`, `STATUS`, `MOTHER`, and `MOTHERID`, and event-level branches called `MULTIPLICITY`, `PROCESSCODE`, `NCHARM`, `NBEAUTY`, and `NBC`. The class code is `5` for beauty, `4` for charm, `45` for Bc, and `0` for pions. The multiplicity is the event charged-primary multiplicity used by the downstream analysis.

The program also writes QA histograms. The main ones are `hMULTIPLICITY`, `hidCharm`, `hidBeauty`, `hidBc`, `hCharmPart`, `hBeautyPart`, `hBcPart`, `hPtTriggerDD`, `hPtAssociateDD`, `hDeltaPhiDD`, `hPtTriggerBB`, `hPtAssociateBB`, and `hDeltaPhiBB`. These histograms are used mainly as production checks; the later physics plots are made from the reduced files in `AnalyzedData`.

The phrase unified heavy flavour should not be read as meaning that every event contains both a hard ccbar and a hard bbbar scattering. It means that the configuration allows both hard channels and the program scans the resulting event record for both sectors in one output format.

## Split Producers

The split producers are `bbbarcorrelations_status.cpp`, `bbbarcorrelations_status_JUNCTIONS.cpp`, `ccbarcorrelations_status.cpp`, and `ccbarcorrelations_status_JUNCTIONS.cpp`. They are the older production path. We keep them because the independent samples dated `10-09-2025` and `12-01-2026` were reduced from this layout and are still used in the final independent-versus-combined comparisons.

The beauty programs read `pythiasettings_Hard_Low_bb.cmnd` or `pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd` and enable `HardQCD:hardbbbar = on`. The charm programs read `pythiasettings_Hard_Low_cc.cmnd` or `pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd` and enable `HardQCD:hardccbar = on`. The run interface is:

```bash
./SimulationScripts/bbbarcorrelations_status RootFiles/bbbar/MONASH/bbbar_MONASH_test.root 123 456
./SimulationScripts/bbbarcorrelations_status_JUNCTIONS RootFiles/bbbar/JUNCTIONS/bbbar_JUNCTIONS_test.root 123 456
./SimulationScripts/ccbarcorrelations_status RootFiles/ccbar/MONASH/ccbar_MONASH_test.root 123 456
./SimulationScripts/ccbarcorrelations_status_JUNCTIONS RootFiles/ccbar/JUNCTIONS/ccbar_JUNCTIONS_test.root 123 456
```

The split tree is also named `tree`. It contains `ID`, `PT`, `ETA`, `Y`, `PHI`, `CHARGE`, `STATUS`, `MOTHER`, `MOTHERID`, and `MULTIPLICITY`. The split files do not contain `HFCLASS`, so the split analysis macros classify species from the PDG id.

## Settings Cards

The combined MONASH, JUNCTIONS, and CLOSEPACKING cards stabilize the selected weakly decaying charm and beauty hadrons using positive PDG ids in the present cards. The split cards still contain both positive and negative `mayDecay` lines in places because they preserve the older production configuration. The current combined-HF cards make D+, D0, Ds+, Lambdac+, Xic0, Xic+, Omegac0, B+, B0, Bs, Bc+, Lambdab, Sigmab-, Sigmab0, and Sigmab+ stable enough for the selected-particle studies. Pions are stored by the C++ selection code rather than by a special decay rule.

The older `pythiasettings_Hard_Low_qq.cmnd` and `pythiasettings_Hard_Low_qq_JUNCTIONS.cmnd` cards remain in the directory with `qqbarcorrelations_status.cpp`. They belong to the earlier broader hard-QCD studies and are not the current recommended path for the combined-HF analysis.

`qqbarcorrelations_status.cpp` is the older broad heavy-quark correlation producer. It stores both charm and beauty information in a pre-unified format and also records MPI information. It is useful for understanding the history of the code base, but it is not the same as the current `heavyflavourcorrelations_status.cpp` format because it does not write the present `HFCLASS`, `PROCESSCODE`, `NCHARM`, `NBEAUTY`, and `NBC` contract in the same way.

`SimulationScripts/run_hf.sh` is a small local helper that runs the unified executable from inside `SimulationScripts` with a timestamped output name and random seed modifiers. It is convenient for ad hoc local checks after the binary has already been built, but the repository-level examples use explicit paths so that the output lands in `RootFiles/HF/<TUNE>`.

`Batching_MONASH.sh` belongs to older production management. It groups existing production output directories into fixed-size batch directories and renames the copied groups. It accepts an optional base directory, source subdirectory, and target subdirectory. It is not part of the current Condor submission path.

`Makefile.old`, `test_bb`, `test_cc`, and any tracked historical executable artifacts should be treated as legacy material. The maintained build rule is the current `Makefile`, and the maintained source files are the `.cpp` producers.

## Condor Interface

The cluster workflow is controlled outside this directory by `runCondorJob.sh` and the submit files at the repository root. The wrapper resolves the repository base, sources `setupEnv.sh`, copies the selected `.cmnd` card into a per-job work directory, rewrites `Main:numberOfEvents`, runs the correct executable, and moves the completed ROOT file into the final `RootFiles` directory only after success.

For the present combined workflow, the submit files call:

```text
runCondorJob.sh CLUSTERID JOBID TUNE NEVT_PER_JOB
```

For the older split workflow, they call:

```text
runCondorJob.sh CLUSTERID JOBID CHANNEL TUNE NEVT_PER_JOB
```

The current 10M combined-HF submit file writes to `RootFiles/HF/MONASH` and `RootFiles/HF/JUNCTIONS`. The 90M submit file uses the same executable and layout but queues ninety one-million-event jobs per tune. The Close Packing 100M submit file writes to `RootFiles/HF/CLOSEPACKING`. The split 10M submit file writes to `RootFiles/bbbar/MONASH`, `RootFiles/bbbar/JUNCTIONS`, `RootFiles/ccbar/MONASH`, and `RootFiles/ccbar/JUNCTIONS`.

## Output Contract

Raw simulation ROOT files belong under `RootFiles`, grouped by workflow and tune. The analysis layer expects the combined files under `RootFiles/HF/MONASH`, `RootFiles/HF/JUNCTIONS`, and `RootFiles/HF/CLOSEPACKING`, while the split analysis expects the older channel directories. The analysis layer then writes compact reduced ROOT files under `AnalyzedData/<tag>/Beauty` and `AnalyzedData/<tag>/Charm`.

This separation matters for synchronization. The raw files are large and machine-local by design. The source files, settings cards, scripts, submit descriptions, and reduced analysis files can be synchronized normally, but raw `.root` production files under `RootFiles` should be excluded unless a data-transfer task explicitly asks for them.
