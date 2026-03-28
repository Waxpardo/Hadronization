# Simulation Scripts

This directory contains the PYTHIA8 producers used to generate heavy-flavour events and store the
selected final-state information in ROOT files for the downstream multiplicity, spectra, balancing,
and angular-correlation studies.

The simulation layer supports two workflows:

1. Unified heavy-flavour generation
   The recommended workflow. Charm and beauty are generated in the same PYTHIA run and saved into
   a common output tree.
2. Legacy split generation
   Charm and beauty are generated independently in separate runs. This is still useful for
   reference samples and direct comparisons to older studies.


## Main files

### Unified heavy-flavour producer

- `heavyflavourcorrelations_status.cpp`

  Single executable that runs a unified heavy-flavour production and stores charm hadrons, beauty
  hadrons, `Bc` hadrons, pions, multiplicity, and per-event heavy-flavour counters in one output
  ROOT file.

Settings cards:

- `pythiasettings_Hard_Low_ccbb_MONASH.cmnd`
- `pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd`

### Legacy split producers

- `bbbarcorrelations_status.cpp`
- `bbbarcorrelations_status_JUNCTIONS.cpp`
- `ccbarcorrelations_status.cpp`
- `ccbarcorrelations_status_JUNCTIONS.cpp`

These generate one heavy-flavour channel per run and are the producers used for the independent
beauty-only and charm-only samples.

Settings cards:

- `pythiasettings_Hard_Low_bb.cmnd`
- `pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd`
- `pythiasettings_Hard_Low_cc.cmnd`
- `pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd`

### Build and helper files

- `Makefile`
  Builds all split and unified simulation executables.
- `Batching_MONASH.sh`
  Helper for regrouping older production outputs into batch directories.


## Recommended workflow

For current production and hadronization studies, use:

1. `heavyflavourcorrelations_status.cpp`
2. `AnalysisScripts/hf_mult_pt_analysis_multi.C`
3. `PlottingScripts/Pt and Multiplicity/...`
4. `PlottingScripts/FinalAnalysis/...`

Use the split producers only when you explicitly want an independent charm-only or beauty-only
sample.


## What the programs store

All simulation programs follow the same broad pattern:

1. Load a `.cmnd` file.
2. Generate events in PYTHIA8.
3. Build an event-level charged-particle multiplicity.
4. Select and store only the final-state particles relevant for the downstream studies.
5. Fill a small set of QA histograms.

### Legacy split outputs

The split producers store:

- the selected heavy-flavour hadrons for the chosen channel
- pions
- event multiplicity

Output structure:

- `TTree` named `tree`
- branches:
  - `ID`
  - `PT`
  - `ETA`
  - `Y`
  - `PHI`
  - `CHARGE`
  - `STATUS`
  - `MOTHER`
  - `MOTHERID`
  - `MULTIPLICITY`
- QA histograms such as:
  - `hMULTIPLICITY`
  - `hidBeauty` or `hidCharm`
  - `hPtTrigger`
  - `hPtAssociate`
  - `hDeltaPhiBB` or `hDeltaPhiDD`
  - `hBeautyPart` or `hCharmPart`

### Unified heavy-flavour outputs

The unified producer stores:

- charm hadrons
- beauty hadrons
- `Bc` hadrons
- pions
- event multiplicity
- event process code
- per-event charm, beauty, and `Bc` counters

Output structure:

- `TTree` named `tree`
- branches:
  - `ID`
  - `HFCLASS`
  - `PT`
  - `ETA`
  - `Y`
  - `PHI`
  - `CHARGE`
  - `STATUS`
  - `MOTHER`
  - `MOTHERID`
  - `MULTIPLICITY`
  - `PROCESSCODE`
  - `NCHARM`
  - `NBEAUTY`
  - `NBC`
- QA histograms such as:
  - `hMULTIPLICITY`
  - `hidCharm`
  - `hidBeauty`
  - `hidBc`
  - `hCharmPart`
  - `hBeautyPart`
  - `hBcPart`
  - `hPtTriggerDD`
  - `hPtAssociateDD`
  - `hDeltaPhiDD`
  - `hPtTriggerBB`
  - `hPtAssociateBB`
  - `hDeltaPhiBB`

Meaning of `HFCLASS`:

- `5`   beauty hadron only
- `4`   charm hadron only
- `45`  `Bc` hadron
- `0`   pion

Important physics note:

The unified workflow does not mean every event contains both a hard `c cbar` and a hard `b bbar`
subprocess. It means the same production configuration allows both channels and the event record
is scanned for both sectors.


## Build instructions

From the repository base:

```bash
source ./setupEnv.sh
make -C SimulationScripts
```

Useful specific targets:

```bash
make -C SimulationScripts heavyflavourcorrelations_status
make -C SimulationScripts bbbarcorrelations_status
make -C SimulationScripts ccbarcorrelations_status
make -C SimulationScripts clean
```

The `Makefile` builds:

- `bbbarcorrelations_status`
- `bbbarcorrelations_status_JUNCTIONS`
- `ccbarcorrelations_status`
- `ccbarcorrelations_status_JUNCTIONS`
- `heavyflavourcorrelations_status`

### Manual build fallback

If `pythia8-config` is not usable on the current machine, load the environment and compile with
the explicit `PYTHIA8` include and library paths:

```bash
source ./setupEnv.sh

PY8_LIBDIR="$PYTHIA8/lib"
if [ -d "$PYTHIA8/lib64" ]; then
  PY8_LIBDIR="$PYTHIA8/lib64"
fi

g++ -O2 -std=c++17 SimulationScripts/heavyflavourcorrelations_status.cpp \
  -I"$PYTHIA8/include" \
  $(root-config --cflags) \
  -L"$PY8_LIBDIR" -Wl,-rpath,"$PY8_LIBDIR" -lpythia8 \
  $(root-config --libs) \
  -o SimulationScripts/heavyflavourcorrelations_status
```


## Running locally

### Unified heavy-flavour producer

Run format:

```bash
./SimulationScripts/heavyflavourcorrelations_status MODE output.root 123 456
```

where:

- `MODE = monash` or `junctions`
- `output.root` is the output ROOT filename
- the final two integers decorrelate the RNG seed

Examples:

```bash
./SimulationScripts/heavyflavourcorrelations_status monash \
  RootFiles/HF/MONASH/hf_MONASH_test.root 123 456

./SimulationScripts/heavyflavourcorrelations_status junctions \
  RootFiles/HF/JUNCTIONS/hf_JUNCTIONS_test.root 123 456
```

### Legacy split producers

Run format:

```bash
./SimulationScripts/bbbarcorrelations_status output.root 123 456
./SimulationScripts/ccbarcorrelations_status output.root 123 456
./SimulationScripts/bbbarcorrelations_status_JUNCTIONS output.root 123 456
./SimulationScripts/ccbarcorrelations_status_JUNCTIONS output.root 123 456
```

Examples:

```bash
./SimulationScripts/bbbarcorrelations_status \
  RootFiles/bbbar/MONASH/bbbar_MONASH_test.root 123 456

./SimulationScripts/ccbarcorrelations_status \
  RootFiles/ccbar/MONASH/ccbar_MONASH_test.root 123 456
```


## PYTHIA settings

### Split settings cards

The split cards enable exactly one hard heavy-flavour process:

- `HardQCD:hardbbbar = on`
- or `HardQCD:hardccbar = on`

### Unified settings cards

The unified cards enable both:

- `HardQCD:hardccbar = on`
- `HardQCD:hardbbbar = on`

Other commonly edited settings include:

- `Main:numberOfEvents`
- `Beams:eCM`
- `PhaseSpace:pTHatMin`
- `ParticleDecays:limitTau0`
- `ParticleDecays:tau0Max`
- `###:mayDecay`

Important note on decay configuration:

For `mayDecay`, use the positive PDG id. Do not rely on separate negative-PDG `mayDecay` lines.

The JUNCTIONS cards modify hadronization relative to MONASH through the color-reconnection,
junction, fragmentation, and beam-remnant settings.


## Condor workflow

The repository root contains the Condor helper scripts:

- `runCondorJob.sh`
- `submitCondor_10M.sub`
- `submitCondor_hf_10M.sub`
- `update_submit_paths.sh`
- `base_path.txt`

Recommended setup:

1. Write the repository path to `base_path.txt`.
2. Run `./update_submit_paths.sh`.
3. Submit the desired workflow.

Unified heavy-flavour submission:

```bash
condor_submit submitCondor_hf_10M.sub
```

Legacy split submission:

```bash
condor_submit submitCondor_10M.sub
```

`runCondorJob.sh` supports both workflows:

- unified:
  - `runCondorJob.sh JOBID TUNE NEVT_PER_JOB`
  - `runCondorJob.sh CLUSTERID JOBID TUNE NEVT_PER_JOB`
- split:
  - `runCondorJob.sh JOBID CHANNEL TUNE NEVT_PER_JOB`
  - `runCondorJob.sh CLUSTERID JOBID CHANNEL TUNE NEVT_PER_JOB`


## Output locations

Typical simulation output directories:

```text
RootFiles/HF/MONASH/
RootFiles/HF/JUNCTIONS/
RootFiles/bbbar/MONASH/
RootFiles/bbbar/JUNCTIONS/
RootFiles/ccbar/MONASH/
RootFiles/ccbar/JUNCTIONS/
```

Typical Condor work directories:

```text
Jobs/HF/MONASH/
Jobs/HF/JUNCTIONS/
Jobs/bbbar/MONASH/
Jobs/bbbar/JUNCTIONS/
Jobs/ccbar/MONASH/
Jobs/ccbar/JUNCTIONS/
```

Typical log directories:

```text
logs/HF/MONASH/
logs/HF/JUNCTIONS/
logs/bbbar/MONASH/
logs/bbbar/JUNCTIONS/
logs/ccbar/MONASH/
logs/ccbar/JUNCTIONS/
```

The downstream analysis outputs are written under:

```text
AnalyzedData/<TAG>/Beauty/
AnalyzedData/<TAG>/Charm/
```


## Notes

- The simulation outputs are written with ROOT file mode `CREATE`, so an existing file with the
  same name will not be overwritten by the producer.
- Only the selected particles needed for the downstream analyses are stored, not the full event
  record.
- If you need to regroup older production outputs into larger batches, use `Batching_MONASH.sh`
  with an explicit base directory instead of editing the script for a new machine.
- The repository base path is resolved from `base_path.txt` or `HADRONIZATION_BASE` by the Condor
  and helper scripts, so those files should be refreshed after moving the project.
