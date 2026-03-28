# Simulation Scripts (bbbar/ccbar correlations and unified heavy-flavour generation)

This directory contains the simulation programs used to generate heavy-flavour events with PYTHIA8 and store final-state information in ROOT files for multiplicity, pT, balancing, and azimuthal angular-correlation studies.

The directory now supports **two workflows**:

1. **Legacy split generation**
   - separate **bbbar** and **ccbar** producers
   - each run generates only one hard heavy-flavour channel at a time

2. **Unified heavy-flavour generation**
   - a single producer generates **both charm and beauty in the same PYTHIA run**
   - the event record is scanned once and both heavy-flavour sectors are saved together
   - this is the recommended setup for the current balancing and hadronization studies

---

## Overview of available scripts

## Legacy split generation scripts

These four scripts generate one heavy-flavour channel per run.

### MONASH (baseline tune)
- `bbbarcorrelations_status.cpp`  
  Uses `pythiasettings_Hard_Low_bb.cmnd` and generates **bbbar** events.

- `ccbarcorrelations_status.cpp`  
  Uses `pythiasettings_Hard_Low_cc.cmnd` and generates **ccbar** events.

### JUNCTIONS (modified tune with junctions / CR changes)
- `bbbarcorrelations_status_JUNCTIONS.cpp`  
  Uses `pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd` and generates **bbbar** events.

- `ccbarcorrelations_status_JUNCTIONS.cpp`  
  Uses `pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd` and generates **ccbar** events.

These scripts are still useful when a clean single-channel reference sample is needed.

---

## Unified heavy-flavour generation script

### Single executable with tune selector
- `heavyflavourcorrelations_status.cpp`

This program:
1. Loads either a MONASH or JUNCTIONS settings card from a command-line mode argument.
2. Runs a **single PYTHIA generation**.
3. Enables **both hard charm and hard beauty production** in that same run through the `.cmnd` file.
4. Builds event-level charged multiplicity from charged primaries.
5. Saves final-state charm hadrons, beauty hadrons, `Bc` hadrons, and pions into one ROOT TTree.
6. Fills QA histograms for charm and beauty observables.

The two settings files used by this executable are:
- `pythiasettings_Hard_Low_ccbb_MONASH.cmnd`
- `pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd`

This unified script is the recommended production mode for:
- charm vs beauty balancing comparisons
- MONASH vs JUNCTIONS hadronization comparisons
- shared-event analyses where both sectors should come from the same production sample

---

## Common workflow of the simulation scripts

All scripts follow the same general structure:

1. Configure PYTHIA8 from a `.cmnd` file.
2. Generate events.
3. Compute event-level multiplicity from charged primaries.
4. Save selected final-state particles into a `TTree`.
5. Fill QA histograms for multiplicity, PDG content, pT, and angular correlations.

---

## What each type of script stores

## Legacy split scripts

The legacy split scripts store:
- final-state heavy-flavour hadrons of the relevant channel
- pions (`pi+`, `pi-`, `pi0`)
- event multiplicity

### Legacy output structure

Each script writes a ROOT file with:

**TTree:** `tree`

Branches:
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

**QA histograms:**
- `hMULTIPLICITY`
- `hidBeauty` or `hidCharm`
- `hPtTrigger`
- `hPtAssociate`
- `hDeltaPhiBB` or `hDeltaPhiDD`
- `hBeautyPart` or `hCharmPart`

---

## Unified heavy-flavour script

The unified script stores:
- charm hadrons
- beauty hadrons
- `Bc` hadrons
- pions
- event multiplicity
- event process code
- per-event heavy-flavour counts

### Unified output structure

Each unified heavy-flavour run writes a ROOT file with:

**TTree:** `tree`

Branches:
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

### Meaning of `HFCLASS`
- `5`  = beauty hadron only
- `4`  = charm hadron only
- `45` = `Bc` hadron
- `0`  = pion

### Unified QA histograms
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

---

## How to build the scripts

## Legacy split scripts

Example build command:

´´´bash
g++ -O2 -std=c++17 bbbarcorrelations_status.cpp \
  $(pythia8-config --cxxflags --libs) $(root-config --cflags --libs) \
  -o bbbarcorrelations_status
'''

Similarly:
'''bash
g++ -O2 -std=c++17 ccbarcorrelations_status.cpp \
  $(pythia8-config --cxxflags --libs) $(root-config --cflags --libs) \
  -o ccbarcorrelations_status

g++ -O2 -std=c++17 bbbarcorrelations_status_JUNCTIONS.cpp \
  $(pythia8-config --cxxflags --libs) $(root-config --cflags --libs) \
  -o bbbarcorrelations_status_JUNCTIONS

g++ -O2 -std=c++17 ccbarcorrelations_status_JUNCTIONS.cpp \
  $(pythia8-config --cxxflags --libs) $(root-config --cflags --libs) \
  -o ccbarcorrelations_status_JUNCTIONS
'''

## Unified heavy-flavour script

Example build command:

'''bash
g++ -O2 -std=c++17 heavyflavourcorrelations_status.cpp \
  $(pythia8-config --cxxflags --libs) $(root-config --cflags --libs) \
  -o heavyflavourcorrelations_status
'''

### Manual build on environments where `pythia8-config` does not work
If the environment provides `PYTHIA8` but `pythia8-config` is not usable, compile manually:

'''bash
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
'''

---

## How to run the scripts

## Legacy split scripts

Run format:

'''bash
./bbbarcorrelations_status output.root 123 456
./ccbarcorrelations_status output.root 123 456
./bbbarcorrelations_status_JUNCTIONS output.root 123 456
./ccbarcorrelations_status_JUNCTIONS output.root 123 456
'''

The two integer arguments are used to decorrelate the RNG seed.

### Examples
'''bash
./bbbarcorrelations_status bbbar_MONASH.root 123 456
./ccbarcorrelations_status ccbar_MONASH.root 123 456
./bbbarcorrelations_status_JUNCTIONS bbbar_JUNCTIONS.root 123 456
./ccbarcorrelations_status_JUNCTIONS ccbar_JUNCTIONS.root 123 456
'''

---

## Unified heavy-flavour script

Run format:

'''bash
./heavyflavourcorrelations_status MODE output.root 123 456
'''

where:
- `MODE = monash` or `junctions`
- `output.root` is the ROOT output filename
- the two integers are used to decorrelate the RNG seed

### Examples
'''bash
./heavyflavourcorrelations_status monash hf_MONASH.root 123 456
./heavyflavourcorrelations_status junctions hf_JUNCTIONS.root 123 456
'''

### What the mode argument does
The mode selects the `.cmnd` file:
- `monash`     → `pythiasettings_Hard_Low_ccbb_MONASH.cmnd`
- `junctions`  → `pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd`

This keeps the executable identical between tunes and changes only the settings card.

---

## How the PYTHIA settings are configured

## Legacy split `.cmnd` files

The split `.cmnd` files control:

- **Number of events**  
  `Main:numberOfEvents = 1000000`

- **Beams and energy**  
  `Beams:eCM = 14000`  
  `Beams:idA = 2212`  
  `Beams:idB = 2212`

- **Tune**  
  `Tune:pp = 14`

- **Hard process**
  - `HardQCD:hardbbbar = on` for beauty-only runs
  - `HardQCD:hardccbar = on` for charm-only runs

- **Low-pT cutoff**  
  `PhaseSpace:pTHatMin = 1.`

- **Decay suppression**
  - `ParticleDecays:limitTau0 = on`
  - `ParticleDecays:tau0Max = 0.01`
  - explicit `mayDecay = off` for selected heavy-flavour hadrons

## Unified heavy-flavour `.cmnd` files

The unified `.cmnd` files use the same beam/tune logic, but enable **both** hard heavy-flavour channels:

- `HardQCD:hardccbar = on`
- `HardQCD:hardbbbar = on`

This means the run can generate events from both hard charm and hard beauty production channels in the same production job.

### Important physics note
This does **not** mean every event contains both a hard `c cbar` and a hard `b bbar` subprocess. It means the same production run allows both channels, and the resulting event record is scanned for both charm and beauty hadrons.

---

## JUNCTIONS-specific settings

The JUNCTIONS `.cmnd` files modify hadronization relative to the MONASH baseline. Typical settings include:

- String fragmentation parameters:
  - `StringPT:sigma`
  - `StringZ:aLund`
  - `StringZ:bLund`

- Diquark and strange suppression:
  - `StringFlav:probQQtoQ`
  - `StringFlav:ProbStoUD`
  - `StringFlav:probQQ1toQQ0join`

- MPI scale:
  - `MultipartonInteractions:pT0Ref`

- Beam remnants:
  - `BeamRemnants:remnantMode`
  - `BeamRemnants:saturation`

- Color reconnection and junctions:
  - `ColourReconnection:mode`
  - `ColourReconnection:allowDoubleJunRem`
  - `ColourReconnection:allowJunctions`
  - `ColourReconnection:junctionCorrection`
  - `ColourReconnection:timeDilationMode`
  - `ColourReconnection:timeDilationPar`

These parameters change hadronization and baryon production relative to the MONASH baseline.

---

## How to change the settings

## Change event count or beam energy
Edit the relevant `.cmnd` file:

- `Main:numberOfEvents`
- `Beams:eCM`
- `Beams:idA`
- `Beams:idB`

## Change the hard process

### Legacy split production
Use one of:
- `HardQCD:hardbbbar = on`
- `HardQCD:hardccbar = on`

### Unified production
Use both:
- `HardQCD:hardccbar = on`
- `HardQCD:hardbbbar = on`

## Change the low-pT cutoff
Edit:

'''text
PhaseSpace:pTHatMin = <value>
'''

## Control decays

Two layers affect decays:

1. Global lifetime cut:
   - `ParticleDecays:limitTau0 = on`
   - `ParticleDecays:tau0Max = <value>`

2. Explicit per-particle stability:
   - `###:mayDecay = off` to keep a given hadron stable
   - set to `on` if decay products are needed

### Important note on PDG sign
For `mayDecay`, use the **positive PDG id** only. Do not rely on separate negative-PDG `mayDecay` lines.

## Change acceptance or multiplicity definition
These are controlled in the C++ source, not the `.cmnd` file.

Examples:
- acceptance cuts:
  - `pTmin`
  - `etamax`

- multiplicity definition:
  - `IsChargedPrimaryForMult()`
  - `IsPromptByStatus()`

## Change how `Bc` hadrons are treated
In the unified script, `Bc` hadrons are tagged separately with:
- `HFCLASS = 45`

This allows the downstream analysis to:
- include them with beauty only
- include them with charm too
- exclude them from one side to avoid double counting

---

## Recommended generation workflow

## When to use the legacy split scripts
Use the split scripts when you want:
- a clean charm-only or beauty-only reference sample
- direct continuity with older `bbbar` / `ccbar` studies
- compatibility with older analysis pipelines built around split channels

## When to use the unified heavy-flavour script
Use the unified script when you want:
- one consistent charm+beauty production sample
- balancing studies comparing charm and beauty from the same run
- direct MONASH vs JUNCTIONS hadronization comparisons in a shared framework
- the newer `HFCLASS`-based analysis chain

This is the preferred setup for the current heavy-flavour balancing and hadronization studies.

---

## Output locations and directory structure

## Legacy split workflow
Typical outputs are organized under:

'''text
RootFiles/bbbar/MONASH/
RootFiles/bbbar/JUNCTIONS/
RootFiles/ccbar/MONASH/
RootFiles/ccbar/JUNCTIONS/
'''

## Unified heavy-flavour workflow
Typical outputs are organized under:

'''text
RootFiles/HF/MONASH/
RootFiles/HF/JUNCTIONS/
'''

Temporary per-job working directories are usually placed under:

'''text
Jobs/HF/MONASH/
Jobs/HF/JUNCTIONS/
Jobs/bbbar/MONASH/
Jobs/bbbar/JUNCTIONS/
Jobs/ccbar/MONASH/
Jobs/ccbar/JUNCTIONS/
'''

Condor logs are typically organized under:

'''text
logs/HF/MONASH/
logs/HF/JUNCTIONS/
logs/bbbar/MONASH/
logs/bbbar/JUNCTIONS/
logs/ccbar/MONASH/
logs/ccbar/JUNCTIONS/
'''

Analysis outputs are written under:

'''text
AnalyzedData/<TAG>/Beauty/
AnalyzedData/<TAG>/Charm/
'''

---

## Notes

- The scripts only store selected final-state particles, not the full event record.
- The legacy split scripts store only the chosen heavy-flavour sector plus pions.
- The unified script stores charm hadrons, beauty hadrons, `Bc` hadrons, and pions in the same tree.
- The output ROOT files are created with mode `CREATE`, so existing files with the same name are not overwritten.
- When using batch production, it is strongly recommended to include the **Condor cluster id** in work-directory names and output filenames to avoid collisions between different submissions.
- In ROOT-based analyses, if many histogram sets are created with identical histogram names in memory, ROOT may warn about replacing existing histograms. This is typically harmless in batch analysis if outputs are written to separate files, but can be avoided by calling:
  '''cpp
  TH1::AddDirectory(kFALSE);
  '''

---

## Base path

The Hadronization base path is defined in `base_path.txt` or via the `HADRONIZATION_BASE` environment variable. Condor and analysis tools use this base to locate:

'''text
SimulationScripts/
RootFiles/
Jobs/
AnalyzedData/
AnalysisScripts/
logs/
'''
