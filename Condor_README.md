# Condor Jobs

This file documents the Condor interface for running the Hadronization simulations on the shared Nikhef/Stoomboot filesystem. The canonical publication path is immutable-campaign driven. `runCondorJob.sh --campaign` validates each logical attempt against the campaign and seed ledger, writes a unique partial file, validates it, and atomically promotes it under `Production/<campaign>/raw/<TUNE>`. Older argument forms are delegated to `runCondorJob_legacy.sh`; the fixed `submitCondor_*.sub`, `RootFiles`, and `Jobs` descriptions later in this document are retained only for legacy reproducibility.

## Canonical campaign submission

Use a clean committed execution worktree and generate a new immutable campaign:

```bash
source setupEnv.sh
python3 tools/campaign_manifest.py generate \
  --campaign <CAMPAIGN> \
  --campaign-ordinal <UNUSED_ORDINAL> \
  --events 1000000 \
  --seed-base <UNUSED_SEED_BASE> \
  --max-attempts 1000
python3 tools/campaign_manifest.py validate campaigns/<CAMPAIGN>
./submit_full_production.sh campaigns/<CAMPAIGN> --dry-run
```

Run `condor_submit` only from a Stoomboot submit node. `--submit` is
fail-closed: it requires the validated 100/200/200 candidate manifest, an exact
recorded implementation commit, no tracked source changes, a successful
producer build, and `PHYSICS_ORIGIN_SIGNOFF.json`. The sign-off is mandatory
when the validated pilots show any nonzero unresolved-trigger fraction.

```bash
./submit_full_production.sh campaigns/<CAMPAIGN> --submit
```

The first 100 candidates per tune are primary; JUNCTIONS and CLOSEPACKING also
have 100 predeclared reserves each. Exactly 100 successful one-million-event
jobs per tune enter the final frozen sample. Reserve selection is allowed only
to replace a documented invalid primary, never to improve a measured result.

Automatic Condor retries are disabled. After a failed attempt, allocate a
fresh seed in the locked ledger and render an explicit retry:

```bash
python3 tools/campaign_manifest.py allocate-retry \
  campaigns/<CAMPAIGN> TUNE LOGICAL_ID \
  --reason "documented failure"
```

Never release a held attempt that may have started and never reuse its seed.
Stable validated outputs are never overwritten. Failed partials and attempt
metadata remain available for audit.

## Legacy fixed-path workflow

The submit files contain absolute paths because Condor does not read `base_path.txt` by itself. The present cluster path is:

```text
/data/alice/ipardoza/Hadronization
```

When the repository is moved, first update `base_path.txt` and then rewrite the submit-file `executable` and `initialdir` entries.

```bash
echo "/data/alice/ipardoza/Hadronization" > base_path.txt
./update_submit_paths.sh
```

The helper also creates the standard output, work, and log directories under the configured base. This matters because the submit files use paths such as `logs/HF/MONASH/job_$(Cluster)_$(JOBID).out` directly.

## Unified Heavy-Flavour Submission

The current production path is the unified HF submission. It runs `SimulationScripts/heavyflavourcorrelations_status` and writes raw ROOT files under `RootFiles/HF/MONASH`, `RootFiles/HF/JUNCTIONS`, and `RootFiles/HF/CLOSEPACKING`.

For a ten-million-event production per tune, submit:

```bash
./update_submit_paths.sh
condor_submit submitCondor_hf_10M.sub
```

The 10M submit file queues ten one-million-event jobs for MONASH and ten one-million-event jobs for JUNCTIONS. MONASH jobs are assigned the `short` category and JUNCTIONS jobs are assigned the `long` category, because the junction configuration usually takes longer.

For a ninety-million-event production per tune, submit:

```bash
./update_submit_paths.sh
condor_submit submitCondor_hf_90M.sub
```

The 90M submit file queues ninety one-million-event jobs for MONASH and ninety one-million-event jobs for JUNCTIONS. It uses `medium` for MONASH and `long` for JUNCTIONS in the current file.

For a 100M Close Packing production, submit:

```bash
./update_submit_paths.sh
condor_submit submitCondor_hf_CLOSEPACKING_100M.sub
```

The Close Packing submit file queues one hundred one-million-event jobs for `CLOSEPACKING` and uses the `long` category.

The legacy unified HF submit files retry non-zero exits up to five times. This covers
Stoomboot walltime/draining evictions, which can leave a partial ROOT file in
the job work directory. On each retry, `runCondorJob.sh` removes only the stale
workdir output, keeps any already-moved final output untouched, and folds the
cluster id, job id, tune, and retry counter into the seed modifiers before
calling the PYTHIA executable. That prevents a retried production job from
reusing the same seed path as the failed attempt.

The file `submitCondor_hf_90M_resubmit_4181781_held38.sub` is a preserved resubmission file for held JUNCTIONS jobs from cluster `4181781`. It is not the generic production template; it is useful only when one wants to reproduce or inspect that specific held-job recovery.

The argument layout for the combined workflow is:

```text
CLUSTERID JOBID TUNE NEVT_PER_JOB
```

A typical output file name is:

```text
RootFiles/HF/JUNCTIONS/hf_JUNCTIONS_cluster<CLUSTERID>_job<JOBID>.root
```

## Split Submission

The split submit file is still present for independent reference samples. It runs the older beauty and charm executables separately for MONASH and JUNCTIONS, and writes to `RootFiles/bbbar/MONASH`, `RootFiles/bbbar/JUNCTIONS`, `RootFiles/ccbar/MONASH`, and `RootFiles/ccbar/JUNCTIONS`.

```bash
./update_submit_paths.sh
condor_submit submitCondor_10M.sub
```

The split argument layout is:

```text
CLUSTERID JOBID CHANNEL TUNE NEVT_PER_JOB
```

The channel is `bbbar` or `ccbar`, and the tune is `MONASH` or `JUNCTIONS`. A typical split output file name is:

```text
RootFiles/bbbar/MONASH/bbbar_MONASH_cluster<CLUSTERID>_job<JOBID>.root
```

## What the Wrapper Does

`runCondorJob.sh` accepts both the combined and split argument layouts. It prefers the directory where the wrapper itself lives as the repository base, then tries `base_path.txt`, then `HADRONIZATION_BASE`, and finally the fixed fallback `/data/alice/ipardoza/Hadronization`. After the base is resolved, it exports `HADRONIZATION_BASE`, sources `setupEnv.sh`, and re-anchors all paths because external environment scripts may reuse generic variable names.

For combined HF jobs, the wrapper selects `heavyflavourcorrelations_status` and chooses `pythiasettings_Hard_Low_ccbb_MONASH.cmnd`, `pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd`, or `pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd` from the tune. For split jobs, it selects one of the four split executables and one of the split settings cards from the channel and tune. It copies the card into the work directory, replaces `Main:numberOfEvents` when that line exists, and appends it when it does not.

The wrapper uses deterministic seed modifiers derived from the job id. It writes the ROOT output in the work directory first. Only after the executable finishes and the expected output file exists does the wrapper move the file into the final `RootFiles` directory. Therefore a running job may have no file in `RootFiles` yet even though its work directory already contains partial job state.

## Directory Layout

The combined workflow uses:

```text
Jobs/HF/MONASH/cluster_<CLUSTERID>/job_<JOBID>
Jobs/HF/JUNCTIONS/cluster_<CLUSTERID>/job_<JOBID>
Jobs/HF/CLOSEPACKING/cluster_<CLUSTERID>/job_<JOBID>
logs/HF/MONASH
logs/HF/JUNCTIONS
logs/HF/CLOSEPACKING
RootFiles/HF/MONASH
RootFiles/HF/JUNCTIONS
RootFiles/HF/CLOSEPACKING
```

The split workflow uses:

```text
Jobs/bbbar/MONASH/cluster_<CLUSTERID>/job_<JOBID>
Jobs/bbbar/JUNCTIONS/cluster_<CLUSTERID>/job_<JOBID>
Jobs/ccbar/MONASH/cluster_<CLUSTERID>/job_<JOBID>
Jobs/ccbar/JUNCTIONS/cluster_<CLUSTERID>/job_<JOBID>
logs/bbbar/MONASH
logs/bbbar/JUNCTIONS
logs/ccbar/MONASH
logs/ccbar/JUNCTIONS
RootFiles/bbbar/MONASH
RootFiles/bbbar/JUNCTIONS
RootFiles/ccbar/MONASH
RootFiles/ccbar/JUNCTIONS
```

## Monitoring

You inspect the queue with:

```bash
condor_q ipardoza
```

A specific idle job can be examined with:

```bash
condor_q <cluster>.<proc> -better-analyze
```

Held jobs are inspected with:

```bash
condor_q ipardoza -hold
condor_q <cluster> -af:j ClusterId ProcId HoldReason
```

Completed jobs can be checked with:

```bash
condor_history <cluster>
```

Jobs can be removed with:

```bash
condor_rm <cluster>
condor_rm <cluster>.<proc>
```

Use removal only when you really want to stop those jobs. Removing a running production is not a diagnostic step.

## Logs and Output Checks

The `.out` log should show the resolved workflow, job id, tune, base directory, work directory, output directory, copied settings card, executable command, file move, and final `Done.` line. The `.err` log is normally empty or close to empty. The most useful checks after submission are:

```bash
tail -n 80 logs/HF/MONASH/job_<CLUSTER>_<JOBID>.out
tail -n 80 logs/HF/JUNCTIONS/job_<CLUSTER>_<JOBID>.err
find RootFiles/HF/MONASH -maxdepth 1 -name '*.root' | wc -l
find RootFiles/HF/JUNCTIONS -maxdepth 1 -name '*.root' | wc -l
```

If `RootFiles` is empty while jobs are still running, inspect `Jobs/HF/<TUNE>/cluster_<CLUSTERID>/job_<JOBID>` before assuming the job failed. The file is moved to `RootFiles` only at the end.

## Common Failures

If a log says that an executable is missing, build the simulation programs on the same filesystem and check that the binary is executable. The current Makefile builds all required programs after `setupEnv.sh` has loaded ROOT and PYTHIA.

```bash
source ./setupEnv.sh
make -C SimulationScripts
```

If a log says that a config template is missing, check the corresponding `.cmnd` file under `SimulationScripts`. If a log says that `/cvmfs/alice.cern.ch/etc/login.sh` is missing, the job is not running in an environment where the ALICE CVMFS stack is visible. If a job is held, use the hold reason command above rather than resubmitting blindly.

If two submissions use the same job id without a cluster id in the output name, files may collide. The current submit files pass `$(Cluster)` into the wrapper, so standard Condor submissions use cluster-aware work and output paths. Manual wrapper calls without a cluster id still use simpler names and should be treated as local tests.

## After Production

The raw outputs from this workflow are the input to the analysis scripts. For a combined-HF production, the next step is:

```bash
./AnalysisScripts/run_hf_analysis.sh <OUTPUT_TAG> 10 combined
```

For a split production, the next step is:

```bash
./AnalysisScripts/run_bb_analysis.sh <OUTPUT_TAG> 10 combined
./AnalysisScripts/run_cc_analysis.sh <OUTPUT_TAG> 10 combined
```

Raw ROOT files under `RootFiles` are large and should be excluded from normal code synchronization unless the task is explicitly about data transfer. The reduced files under `AnalyzedData` are the compact objects consumed by the plotting layer and are the correct objects to compare when checking analysis reproducibility.
