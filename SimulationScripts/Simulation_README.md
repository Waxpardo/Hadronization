# Simulation Scripts (bbbar/ccbar correlations)

This directory contains four C++ simulation programs that generate heavy-flavor events with PYTHIA8 and store the final-state information in a ROOT file for azimuthal angular correlation studies.

## What each script does

All four scripts follow the same workflow:

1. Configure PYTHIA8 from a `.cmnd` file.
2. Generate events.
3. Build event-level multiplicity from charged primaries.
4. Save final-state heavy-flavor hadrons and pions into a TTree.
5. Fill QA histograms (multiplicity, PDG content, pT spectra, and DeltaPhi correlations).

### MONASH (baseline tune)
- `bbbarcorrelations_status.cpp`  
  Uses `pythiasettings_Hard_Low_bb.cmnd` and generates **bbbar** events.

- `ccbarcorrelations_status.cpp`  
  Uses `pythiasettings_Hard_Low_cc.cmnd` and generates **ccbar** events.

### JUNCTIONS (modified tune with junctions and CR changes)
- `bbbarcorrelations_status_JUNCTIONS.cpp`  
  Uses `pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd` and generates **bbbar** events.

- `ccbarcorrelations_status_JUNCTIONS.cpp`  
  Uses `pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd` and generates **ccbar** events.

## Output structure

Each script writes a ROOT file with:

**TTree:** `tree`  
Branches (per selected particle):
- `ID`, `PT`, `ETA`, `Y`, `PHI`, `CHARGE`, `STATUS`
- `MOTHER` (mother index), `MOTHERID` (mother PDG)
- `MULTIPLICITY` (event-level charged multiplicity)

**QA histograms:**
- `hMULTIPLICITY` (charged multiplicity)
- `hidBeauty` / `hidCharm` (PDG distributions)
- `hPtTrigger`, `hPtAssociate`
- `hDeltaPhiBB` / `hDeltaPhiDD`
- `hBeautyPart` / `hCharmPart` (per-event heavy-flavor counts)

## Build and run

Example build command:

```bash
g++ -O2 -std=c++17 bbbarcorrelations_status.cpp \
  $(pythia8-config --cxxflags --libs) $(root-config --cflags --libs) \
  -o bbbarcorrelations_status
```

Run:

```bash
./bbbarcorrelations_status output.root 123 456
```

The two integer arguments are used to decorrelate the RNG seed.

## PYTHIA settings (what is configured)

Each `.cmnd` file controls:

- **Number of events:**  
  `Main:numberOfEvents = 1000000`

- **Beams and energy:**  
  `Beams:eCM = 14000` (14 TeV), `Beams:idA = 2212`, `Beams:idB = 2212`

- **Tune:**  
  `Tune:pp = 14` (MONASH baseline)

- **Hard processes:**  
  `HardQCD:hardbbbar = on` or `HardQCD:hardccbar = on`

- **Low-pT cutoff:**  
  `PhaseSpace:pTHatMin = 1.` (avoids divergence at low pT)

- **Decay suppression:**  
  `ParticleDecays:limitTau0 = on`  
  `ParticleDecays:tau0Max = 0.01`  
  plus explicit `mayDecay = off` for heavy-flavor hadrons to keep them stable.

### JUNCTIONS-specific settings

The JUNCTIONS `.cmnd` files add extra parameters on top of MONASH, including:

- String fragmentation parameters (`StringPT:sigma`, `StringZ:aLund`, `StringZ:bLund`)
- Diquark and strange suppression (`StringFlav:*`)
- MPI scale (`MultiPartonInteractions:pT0Ref`)
- Beam remnants (`BeamRemnants:*`)
- Color reconnection with junctions enabled:
  - `ColourReconnection:allowJunctions = on`
  - related CR controls (`mode`, `m0`, `junctionCorrection`, `timeDilation*`)

These modify hadronization and baryon production relative to the baseline tune.

## How to change settings

### Change event count or beam energy
Edit the `.cmnd` files:

- `Main:numberOfEvents`
- `Beams:eCM`, `Beams:idA`, `Beams:idB`

### Change the heavy-flavor process
Toggle the hard process:

- For bbbar: `HardQCD:hardbbbar = on`
- For ccbar: `HardQCD:hardccbar = on`

### Change the low-pT cutoff
Edit:

```
PhaseSpace:pTHatMin = <value>
```

### Control decays
Two layers affect decays:

1. Global lifetime cut:
   - `ParticleDecays:limitTau0 = on`
   - `ParticleDecays:tau0Max = <value>`

2. Explicit per-particle stability:
   - `###:mayDecay = off` to keep a given hadron stable
   - Set to `on` if decay products are needed

### Modify JUNCTIONS tune
The JUNCTIONS files include additional fragmentation and color-reconnection parameters. Any of these can be tuned directly in the `.cmnd` file, e.g.:

- `StringZ:aLund`, `StringZ:bLund`
- `StringFlav:probQQtoQ`
- `ColourReconnection:allowJunctions`
- `ColourReconnection:timeDilationPar`

### Change acceptance or multiplicity definition
These are controlled in the C++ source, not the `.cmnd` files:

- Acceptance:
  - `pTmin` and `etamax` in each `.cpp`
- Multiplicity definition:
  - `IsChargedPrimaryForMult()` and `IsPromptByStatus()`

## Notes

- The scripts only store final-state heavy-flavor hadrons and pions.  
  If other species are needed, adjust the particle-selection logic in the C++.
- The output ROOT files are created with mode `CREATE`, so existing files with the
  same name will not be overwritten.

## Base path

The Hadronization base path is defined in `base_path.txt` (or via the
`HADRONIZATION_BASE` environment variable). Condor and analysis tools use this
base to locate:

```
SimulationScripts/
RootFiles/<CHANNEL>/<TUNE>/
Jobs/<CHANNEL>/<TUNE>/
```
