# Hadronization Condor Jobs

This README explains how to submit Condor jobs for the Hadronization simulations, both for the **legacy split-channel producers** (`bbbar` / `ccbar`) and for the **new unified heavy-flavour producer** (`HF`, i.e. charm and beauty together in one PYTHIA run). It also explains how to adjust job specifications, how output is organized, and how to keep paths consistent when the directory is moved.

The repository currently supports **two Condor workflows**:

1. **Legacy split production**
   - separate jobs for `bbbar` and `ccbar`
   - separate MONASH and JUNCTIONS executables
   - outputs written under `RootFiles/<CHANNEL>/<TUNE>/`

2. **Unified heavy-flavour production**
   - one executable generates both charm and beauty in a single run
   - tune selected as `MONASH` or `JUNCTIONS`
   - outputs written under `RootFiles/HF/<TUNE>/`

The unified workflow is the recommended setup for the current balancing and hadronization studies.

---

## Quick start

## Legacy split workflow

From the Hadronization base on the shared filesystem:

´´´bash
./update_submit_paths.sh
condor_submit submitCondor_10M.sub
´´´

This submits `10 x 1,000,000` jobs for each of:
- `bbbar MONASH`
- `bbbar JUNCTIONS`
- `ccbar MONASH`
- `ccbar JUNCTIONS`

---

## Unified heavy-flavour workflow

From the Hadronization base on the shared filesystem:

´´´bash
condor_submit submitCondor_hf_10M.sub
´´´

This submits jobs for the unified heavy-flavour executable, typically for:
- `MONASH`
- `JUNCTIONS`

Example:
- `10 jobs × 1,000,000 events = 10M events per tune`
- or `20 jobs × 500,000 events = 10M events per tune`

---

## What gets executed

Both submit files call `runCondorJob.sh` from the Hadronization base.

The wrapper script:
1. resolves the Hadronization base path
2. sources `setupEnv.sh`
3. creates a per-job working directory
4. copies a `.cmnd` template into the job directory
5. replaces `Main:numberOfEvents` with the per-job event count
6. runs the selected executable
7. moves the output ROOT file into the final output directory

---

## Legacy split workflow

In the legacy split setup, `runCondorJob.sh` selects the correct executable based on:
- `CHANNEL`: `bbbar` or `ccbar`
- `TUNE`: `MONASH` or `JUNCTIONS`

Typical executables:

´´´text
Hadronization/SimulationScripts/bbbarcorrelations_status
Hadronization/SimulationScripts/bbbarcorrelations_status_JUNCTIONS
Hadronization/SimulationScripts/ccbarcorrelations_status
Hadronization/SimulationScripts/ccbarcorrelations_status_JUNCTIONS
´´´

Typical `.cmnd` templates:

´´´text
Hadronization/SimulationScripts/pythiasettings_Hard_Low_bb.cmnd
Hadronization/SimulationScripts/pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd
Hadronization/SimulationScripts/pythiasettings_Hard_Low_cc.cmnd
Hadronization/SimulationScripts/pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd
´´´

Each legacy job typically:
1. creates a per-job `.cmnd` file
2. runs the chosen split executable
3. writes output under:
   ´´´text
   Hadronization/RootFiles/<CHANNEL>/<TUNE>/
   ´´´
4. uses a working directory under:
   ´´´text
   Hadronization/Jobs/<CHANNEL>/<TUNE>/...
   ´´´

---

## Unified heavy-flavour workflow

In the unified setup, `runCondorJob.sh` selects the executable based on:
- `TUNE`: `MONASH` or `JUNCTIONS`

Typical executable:

´´´text
Hadronization/SimulationScripts/heavyflavourcorrelations_status
´´´

Typical `.cmnd` templates:

´´´text
Hadronization/SimulationScripts/pythiasettings_Hard_Low_ccbb_MONASH.cmnd
Hadronization/SimulationScripts/pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd
´´´

Each unified job typically:
1. creates a per-job `.cmnd` file
2. runs the unified heavy-flavour executable in either `monash` or `junctions` mode
3. writes output under:
   ´´´text
   Hadronization/RootFiles/HF/<TUNE>/
   ´´´
4. uses a working directory under:
   ´´´text
   Hadronization/Jobs/HF/<TUNE>/...
   ´´´

---

## Naming and collisions

The current Condor submit files pass `CLUSTERID` into `runCondorJob.sh`, so batch jobs are separated by cluster automatically.

Typical Condor-managed paths now look like:

´´´text
Jobs/HF/JUNCTIONS/cluster_<CLUSTERID>/job_<JOBID>/
RootFiles/HF/JUNCTIONS/hf_JUNCTIONS_cluster<CLUSTERID>_job<JOBID>.root
Jobs/bbbar/MONASH/cluster_<CLUSTERID>/job_<JOBID>/
RootFiles/bbbar/MONASH/bbbar_MONASH_cluster<CLUSTERID>_job<JOBID>.root
´´´

This prevents collisions between different Condor submissions for the same workflow and tune.

For manual runs without a cluster id, the wrapper still uses the simpler `job_<JOBID>` naming, so clean old manual outputs before reusing the same job id.

---

## Expected arguments passed to `runCondorJob.sh`

## Legacy split workflow

Current legacy argument layout:

´´´text
CLUSTERID JOBID CHANNEL TUNE NEVT_PER_JOB
´´´

where:
- `CLUSTERID` = Condor cluster id
- `JOBID` = per-job index
- `CHANNEL` = `bbbar` or `ccbar`
- `TUNE` = `MONASH` or `JUNCTIONS`
- `NEVT_PER_JOB` = events per job

---

## Unified heavy-flavour workflow

Current unified argument layout:

´´´text
CLUSTERID JOBID TUNE NEVT_PER_JOB
´´´

where:
- `CLUSTERID` = Condor cluster id
- `JOBID` = per-job index
- `TUNE` = `MONASH` or `JUNCTIONS`
- `NEVT_PER_JOB` = events per job

---

## Output locations

## Legacy split workflow

Outputs are written to:

´´´text
Hadronization/RootFiles/bbbar/MONASH/
Hadronization/RootFiles/bbbar/JUNCTIONS/
Hadronization/RootFiles/ccbar/MONASH/
Hadronization/RootFiles/ccbar/JUNCTIONS/
´´´

Working directories are typically under:

´´´text
Hadronization/Jobs/bbbar/MONASH/cluster_<CLUSTERID>/job_<JOBID>/
Hadronization/Jobs/bbbar/JUNCTIONS/cluster_<CLUSTERID>/job_<JOBID>/
Hadronization/Jobs/ccbar/MONASH/cluster_<CLUSTERID>/job_<JOBID>/
Hadronization/Jobs/ccbar/JUNCTIONS/cluster_<CLUSTERID>/job_<JOBID>/
´´´

---

## Unified heavy-flavour workflow

Outputs are written to:

´´´text
Hadronization/RootFiles/HF/MONASH/
Hadronization/RootFiles/HF/JUNCTIONS/
´´´

Working directories are typically under:

´´´text
Hadronization/Jobs/HF/MONASH/cluster_<CLUSTERID>/job_<JOBID>/
Hadronization/Jobs/HF/JUNCTIONS/cluster_<CLUSTERID>/job_<JOBID>/
´´´

Logs go to:

´´´text
Hadronization/logs/HF/MONASH/
Hadronization/logs/HF/JUNCTIONS/
Hadronization/logs/bbbar/MONASH/
Hadronization/logs/bbbar/JUNCTIONS/
Hadronization/logs/ccbar/MONASH/
Hadronization/logs/ccbar/JUNCTIONS/
´´´

---

## Example job lifecycle

A Condor job typically does the following:

1. Create a work directory for the job.
2. Copy the relevant `.cmnd` template into the work directory.
3. Replace `Main:numberOfEvents` with the requested number of events.
4. Derive seeds from job metadata.
5. Run the executable.
6. Write the ROOT file in the work directory first.
7. Move the finished ROOT file into the final `RootFiles/...` directory.

### Important note
While a job is still running, the final output directory may remain empty, because the move usually happens only **after successful completion**.

If you want to inspect a running job, check the work directory first.

---

## Adjusting job specifications

## Legacy split submit files

Typical variables in a legacy submit file:

´´´text
NEVT_PER_JOB = 1000000
CHANNEL = bbbar
TUNE = MONASH
´´´

Typical arguments line:

´´´text
arguments = $(Cluster) $(JOBID) $(CHANNEL) $(TUNE) $(NEVT_PER_JOB)
´´´

Typical queue blocks:

´´´text
CHANNEL = bbbar
TUNE = MONASH
queue JOBID from (
0
1
...
9
)

CHANNEL = bbbar
TUNE = JUNCTIONS
queue JOBID from (
0
1
...
9
)

CHANNEL = ccbar
TUNE = MONASH
queue JOBID from (
0
1
...
9
)

CHANNEL = ccbar
TUNE = JUNCTIONS
queue JOBID from (
0
1
...
9
)
´´´

---

## Unified heavy-flavour submit files

Typical variables in a unified submit file:

´´´text
NEVT_PER_JOB = 1000000
NJOBS = 10
TUNE = MONASH or JUNCTIONS
´´´

Recommended arguments line:

´´´text
arguments = $(Cluster) $(JOBID) $(TUNE) $(NEVT_PER_JOB)
´´´

Example for `10M` per tune using `10 jobs × 1M`:

´´´text
NEVT_PER_JOB = 1000000
´´´

Example for `10M` per tune using `20 jobs × 500k`:

´´´text
NEVT_PER_JOB = 500000
´´´

### Example queue itemdata block for a unified submit file

´´´text
queue JOBID, TUNE from (
0, MONASH
1, MONASH
2, MONASH
3, MONASH
4, MONASH
5, MONASH
6, MONASH
7, MONASH
8, MONASH
9, MONASH
0, JUNCTIONS
1, JUNCTIONS
2, JUNCTIONS
3, JUNCTIONS
4, JUNCTIONS
5, JUNCTIONS
6, JUNCTIONS
7, JUNCTIONS
8, JUNCTIONS
9, JUNCTIONS
)
´´´

Or for a JUNCTIONS-only test run:

´´´text
queue JOBID, TUNE from (
0, JUNCTIONS
1, JUNCTIONS
2, JUNCTIONS
...
9, JUNCTIONS
)
´´´

---

## Base path configuration

The base path is stored in:

´´´text
base_path.txt
´´´

Scripts resolve the base path in this order:
1. `HADRONIZATION_BASE` environment variable
2. `base_path.txt`
3. script directory
4. optional hardcoded fallback path in the wrapper

---

## Updating submit files when paths move

Condor submit files cannot read `base_path.txt` directly.

If you use submit files with hardcoded:
- `executable = ...`
- `initialdir = ...`

you must update them when the base path changes.

In the older workflow, this was done with:

´´´bash
./update_submit_paths.sh
´´´

This typically rewrites submit files such as:
- `submitCondor_10M.sub`
- `submitCondor_hf_10M.sub`

so that:

´´´text
executable = <BASE>/runCondorJob.sh
initialdir = <BASE>
´´´

If your newer submit files already use the correct absolute base path, no rewrite step is needed.

---

## Monitoring jobs

## Check the queue

To see your current jobs:

´´´bash
condor_q <username>
´´´

Example:

´´´bash
condor_q ipardoza
´´´

This shows:
- `DONE`
- `RUN`
- `IDLE`
- `HOLD`
- `TOTAL`

---

## Analyze why a job is idle

For one specific job:

´´´bash
condor_q <cluster>.<proc> -better-analyze
´´´

Example:

´´´bash
condor_q 4174875.0 -better-analyze
´´´

---

## Check held jobs

To see all held jobs:

´´´bash
condor_q <username> -hold
´´´

To print hold reasons:

´´´bash
condor_q <cluster> -af:j ClusterId ProcId HoldReason
´´´

Example:

´´´bash
condor_q 4174992 -af:j ClusterId ProcId HoldReason
´´´

---

## Remove jobs

To remove an entire cluster:

´´´bash
condor_rm <clusterid>
´´´

Example:

´´´bash
condor_rm 4174875
´´´

To remove one specific job:

´´´bash
condor_rm <clusterid>.<procid>
´´´

Example:

´´´bash
condor_rm 4174875.0
´´´

---

## Check history after completion

To inspect completed jobs:

´´´bash
condor_history <clusterid>
´´´

Example:

´´´bash
condor_history 4174875
´´´

---

## Inspecting logs

Logs are written under:

´´´text
Hadronization/logs/HF/<TUNE>/
Hadronization/logs/<CHANNEL>/<TUNE>/
´´´

Typical filenames include:
- cluster id
- job id
- tune
- optionally channel

Examples:

´´´text
logs/HF/MONASH/job_4174875_0.out
logs/HF/MONASH/job_4174875_0.err
logs/bbbar/JUNCTIONS/job_4175667_7.out
logs/ccbar/JUNCTIONS/job_4175667_7.err
´´´

Use:

´´´bash
tail -n 50 logs/HF/<TUNE>/job_<CLUSTER>_<JOBID>.out
tail -n 50 logs/HF/<TUNE>/job_<CLUSTER>_<JOBID>.err
tail -n 50 logs/<CHANNEL>/<TUNE>/job_<CLUSTER>_<JOBID>.out
tail -n 50 logs/<CHANNEL>/<TUNE>/job_<CLUSTER>_<JOBID>.err
´´´

Empty `.err` files are usually a good sign.

Healthy `.out` logs typically show:
- selected mode / tune
- working directory
- output name
- generated event count
- file move completion
- `Done.`

---

## Checking outputs

## Legacy split outputs

Check output directories with:

´´´bash
ls -lh RootFiles/bbbar/MONASH
ls -lh RootFiles/bbbar/JUNCTIONS
ls -lh RootFiles/ccbar/MONASH
ls -lh RootFiles/ccbar/JUNCTIONS
´´´

---

## Unified heavy-flavour outputs

Check output directories with:

´´´bash
ls -lh RootFiles/HF/MONASH
ls -lh RootFiles/HF/JUNCTIONS
´´´

Count how many ROOT files are present:

´´´bash
find RootFiles/HF/MONASH -maxdepth 1 -name '*.root' | wc -l
find RootFiles/HF/JUNCTIONS -maxdepth 1 -name '*.root' | wc -l
´´´

### Important note
If jobs are still running, the output directory may not yet contain files, because files are often moved there only at the end of a successful job.

In that case, inspect the work directory:

´´´bash
ls -lh Jobs/HF/MONASH
ls -lh Jobs/HF/JUNCTIONS
´´´

---

## Common problems

## 1. Output collisions between submissions
If two different Condor submissions write to:
- the same work directory name
- the same output filename

then jobs can overwrite each other.

This usually happens when only `JOBID` is used in naming.

### Fix
Use a fresh output/work directory namespace for the resubmission, or extend the wrapper to include a submission-specific tag in:
- `WORKDIR`
- `OUTBASENAME`

---

## 2. Executable not found
If logs show:
´´´text
ERROR: Executable not found or not executable
´´´
then:
- the executable was not compiled
- or the path in `runCondorJob.sh` is wrong

Check:

´´´bash
ls -l SimulationScripts/heavyflavourcorrelations_status
´´´

or the corresponding legacy executable.

---

## 3. `.cmnd` template not found
If logs show:
´´´text
ERROR: Config template not found
´´´
check that the required `.cmnd` file exists in `SimulationScripts/`.

---

## 4. `root` or PYTHIA environment not found
If an analysis or build step says:
´´´text
root: command not found
´´´
or
´´´text
pythia8-config: command not found
´´´
then the environment was not loaded.

Load it with:

´´´bash
source ./setupEnv.sh
´´´

---

## 5. Terminal closes on nonzero exit
If your terminal/session is configured to close when a command exits nonzero, errors may look like “the terminal just died”.

In that case:
- redirect output to a log file
- use `tmux`
- or append `|| true` for diagnostic commands

---

## Minimal preflight checklist

Before submitting jobs, check:

- `SimulationScripts/` contains the required compiled executable(s)
- the required `.cmnd` files exist
- `setupEnv.sh` exists in the Hadronization base
- workflow-specific `logs/...` directories exist
- `base_path.txt` points to the correct Hadronization base
- submit files point to the correct `runCondorJob.sh`
- work/output directories exist or can be created
- old outputs from the same sample family will not be overwritten

Recommended checks:

´´´bash
ls -l SimulationScripts/
ls -l SimulationScripts/pythiasettings_Hard_Low_ccbb_MONASH.cmnd
ls -l SimulationScripts/pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd
./update_submit_paths.sh
´´´

For unified heavy-flavour production:

´´´bash
mkdir -p RootFiles/HF/MONASH RootFiles/HF/JUNCTIONS
mkdir -p Jobs/HF/MONASH Jobs/HF/JUNCTIONS
´´´

---

## Summary

## Legacy split workflow
Use:
- `submitCondor_10M.sub`
- split executables
- outputs under `RootFiles/<CHANNEL>/<TUNE>/`

## Unified heavy-flavour workflow
Use:
- `submitCondor_hf_10M.sub`
- `runCondorJob.sh` in unified mode
- `heavyflavourcorrelations_status`
- outputs under `RootFiles/HF/<TUNE>/`

The unified workflow is the recommended path for the current charm+beauty balancing and hadronization studies.
