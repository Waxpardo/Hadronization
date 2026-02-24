# Hadronization Condor Jobs

This README explains how to submit Condor jobs for the bbbar/ccbar simulations, how to adjust job specifications, and how to keep paths consistent when the directory is moved.

## Quick start (submit jobs)

From the Hadronization base on the shared filesystem (after updating submit paths):

```bash
./update_submit_paths.sh
condor_submit submitCondor.sub
```

For the 100M-per-combo preset:

```bash
./update_submit_paths.sh
condor_submit submitCondor_100M.sub
```

## What gets executed

The submit files call `runCondorJob.sh` using the base path in `base_path.txt`.

`runCondorJob.sh` selects the correct executable based on:
- `CHANNEL`: `bbbar` or `ccbar`
- `TUNE`: `MONASH` or `JUNCTIONS`

Executables must exist at:

```
Hadronization/SimulationScripts/{bb,cc}barcorrelations_status[_JUNCTIONS]
```

Each job:
1. Creates a per-job `.cmnd` file with `Main:numberOfEvents = NEVT_PER_JOB`.
2. Runs the executable with seeds derived from `JOBID`.
3. Moves output to:
   ```
   Hadronization/RootFiles/<CHANNEL>/<TUNE>/
   ```
4. Uses a working directory under:
   ```
   Hadronization/Jobs/<CHANNEL>/<TUNE>/job_<JOBID>
   ```

Logs go to:

```
Hadronization/logs/
```

## Adjust job specifications

Edit `submitCondor.sub` (or `submitCondor_100M.sub`):

**Events per job**
```
NEVT_PER_JOB = 1000000
```

**Number of jobs per block**
```
NJOBS = 100
```

**Channels / tunes**
```
CHANNEL = bbbar
TUNE    = MONASH
queue $(NJOBS)
```

Repeat blocks as needed. The `arguments` line already passes:

```
JOBID CHANNEL TUNE NEVT_PER_JOB
```

## Base path configuration

The base path is stored in:

```
base_path.txt
```

Scripts resolve the base path in this order:
1. `HADRONIZATION_BASE` (environment variable)
2. `base_path.txt`
3. script directory

### Updating Condor submit files

Condor submit files cannot read `base_path.txt` directly. Use:

```bash
./update_submit_paths.sh
```

This rewrites `submitCondor.sub` and `submitCondor_100M.sub` so that:

```
executable = <BASE>/runCondorJob.sh
initialdir = <BASE>
```

## Minimal preflight checklist

- `SimulationScripts/` contains compiled executables.
- `setupEnv.sh` exists in the Hadronization base.
- `logs/` directory exists in the base.
- `base_path.txt` points to the same base path as the code.
- Submit files were updated with `./update_submit_paths.sh`.
