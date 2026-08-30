# HTCondor production

How to submit, watch, and repair a campaign on an authorized HTCondor site.

## Where to run what

| | where |
|---|---|
| build, render submits, `make status` | checkout host with mounted campaign storage |
| `condor_submit`, `condor_q`, `condor_rm`, `condor_release` | authorized HTCondor submit host |

The checkout and selected external storage must resolve to the same bytes on
both hosts. Site login aliases, support channels, and mount paths are local
configuration and do not belong in tracked instructions.

## Submitting

```bash
# from the checkout root
make doctor                       # must report 0 blocking
make submit-full CAMPAIGN=HF_RUN3_V1 ORDINAL=<ordinal>
# ORDINAL has no default. `make submit-full` depends on `require-ordinal`,
# which exits 1 and prints where the live claims are (Makefile:152-177).
# The claim list is config/campaign_ordinals_v1.json; HF_RUN3_V1 is ordinal 3.

# on the authorized submit host, from the same checkout root
OUT=$(condor_submit submit_HF_RUN3_V1_full.sub)
echo "$OUT"
condor_release "$(echo "$OUT" | grep -oE 'cluster [0-9]+' | grep -oE '[0-9]+')"
```

Take the cluster id from `condor_submit`'s own output. Do **not** discover it
with something like `condor_q -af ClusterId | tail -1`: if the submit fails,
that picks up whatever unrelated cluster is still in your queue and releases
it. It has already happened once here.

**Jobs are queued held** (`hold = True` in the template) and do nothing until
released. That is deliberate: it gives you a chance to inspect the queue before
thousands of jobs start consuming slots.

Smaller runs: `make submit-smoke` (10 jobs/tune) and `make submit-prelim`
(50 jobs/tune). Override anything: `CAMPAIGN= ORDINAL= JOBS= EVENTS= TUNES=
MAX_CPU= MAX_RUNTIME=`.

Rendering refuses to proceed if the checkout has tracked modifications, and
refuses any seed the ledger has already burned. That ledger is
`$HADRONIZATION_DATA_ROOT/project/runs/seed_ledgers/burned_seeds.txt`
(`Makefile:35-36`), and it is NOT inside the checkout. A ledger path that
resolves inside the checkout means `setupEnv.sh` was not sourced in this
shell (`Makefile:169-174`).

## Submitted jobs are HELD. Release is a separate act

`render_production_submit.py:327` emits `hold = True` unconditionally, so a
freshly submitted campaign sits **entirely held** and **nothing runs** until:

```bash
condor_q <cluster> -af HoldReasonCode   # expect: every job 15
condor_release <cluster>
condor_q                                # expect: 0 held
```

Check the reasons **before** releasing — a job held at t=0 for anything other
than code 15 has a real problem that a release would mask.

### Two hold classes, identical in a bare `condor_q` count, opposite in meaning

They are told apart by the hold reason, which the recipe above already reads:
`HoldReasonCode` 15 is the submit-time parking brake, and a periodic hold
carries the literal `HF_HANG_GUARD` in its `HoldReason`. That marker string is
what the retry path matches: `tools/resubmit_held.py:55` reads `HoldReason` and
`:271-274` splits the held jobs on whether the marker is present.

| hold | when | means | do |
|---|---|---|---|
| `HoldReasonCode 15` "at user's request" | at submit, **all** jobs | the parking brake | **release** |
| `HF_HANG_GUARD suspected generator hang` | after >3600 s CPU or >14400 s wall | wedged generator; see the rate note below | **retry** |

**The rate is measured, not quoted from here.** `make status` computes the live rate from worker outputs (`tools/campaign_status.py:264`, printed at `:271-274`). The recorded nominal-campaign attrition is in `config/cr_holdout_policy_v1.json`: 0/1000 MONASH, 63/1063 JUNCTIONS (5.93 %), 64/1064 CLOSEPACKING (6.02 %) — 127 of 3,127 attempts, 4.06 % campaign-wide. An earlier form of this table carried an unsourced "~2.7 %", which no artifact in this repository supports and which the recorded observations contradict. `docs/GOLDEN_OUTPUTS.md:1053` row N5 requires the discard rate to be reported rather than corrected away, so it must never be quotable from an unsourced runbook line.

**"N held" is evidence of nothing until you read the reason.**

## While it runs

```bash
# on the submit host -- 1 idle, 2 running, 5 held
condor_q <cluster> -af JobStatus | sort | uniq -c

# on the storage-visible checkout host -- what actually landed on disk
make status CAMPAIGN=HF_RUN3_V1          # smoke/prelim scale
make status-full CAMPAIGN=HF_RUN3_V1     # 1000 jobs/tune
```

`make status` reads only what the worker wrote -- attempt sidecars, validation
receipts, promoted files -- so it cannot drift from reality. It reports, per
tune: started, succeeded, `noverdict`, producer failures, validation failures.

**`noverdict` is not the hang count until the queue has drained.** The attempt
sidecar is written when the producer exits, so a job midway through validation
looks identical on disk to one the guard killed. Once `condor_q` is empty,
`noverdict` *is* the killed count, and that is the hang rate.

## The hang guard

```
periodic_hold = (JobStatus == 2) && ((RemoteUserCpu > 3600) ||
                ((CurrentTime - EnteredCurrentStatus) > 14400))
periodic_hold_reason = "HF_HANG_GUARD suspected generator hang: ..."
```

PYTHIA's junction-splitting hang is an unbounded accept-reject loop in
`StringZ::zLund`. The job never exits, so `on_exit_hold` can never catch it --
four such jobs once burned 34 CPU-hours unnoticed.

**The guard is on CPU time, not wall clock.** A wedged job burns CPU
continuously (the four historical hangs ran at CPU/wall = 0.97); a healthy job
on a contended node does not -- one smoke-test job sat at CPU/wall = 0.33, 1787s
of wall clock for 598s of work, behaving perfectly (a smoke-test observation
with no dated record under `results/validation/` in this repository; read it as
the reason for the design, not as a citable measurement). A wall-clock guard cannot
tell those apart, and killing slow-but-valid jobs would bias the discard rate
toward whichever nodes happen to be busy.

3600s is about 4.7x the slowest normal job (CLOSEPACKING, 762s), and above a
2398s outlier seen in the same smoke test, likewise unrecorded here, that was not a
classic hang. It is
deliberately generous: the hang is unbounded so any threshold catches it, while
a tight cut would also discard slow-but-legitimate jobs -- and dense-junction
events are both slower AND the ones producing the baryons being measured, so
cutting them would bias the observable. The 14400s
wall limit is only a backstop for a job stuck *without* burning CPU -- a dead
mount, hung I/O -- which the CPU guard cannot see.

Site policy does not constrain this: workers advertise `START = true` and
`MaxJobRetirementTime = 345600` (4 days), so the guard sits far inside anything
the site enforces. `+UseOS` and `+JobCategory` in the submit file are not
matched against any worker attribute at this site; they are informational.

## Repairing a campaign

The merge requires **equal exposure per tune**, so any missing job blocks
analysis. Held and failed jobs must be replaced before the campaign is usable.

```bash
# dry run: what would be resubmitted
make resubmit CAMPAIGN=HF_RUN3_V1 ATTEMPT=1

# actually remove guard-held jobs and render the retry
make resubmit CAMPAIGN=HF_RUN3_V1 ATTEMPT=1 APPLY=1 CLUSTER=<cluster>

# on the submit host
condor_submit submit_HF_RUN3_V1_retry1.sub
condor_release <new cluster>
```

Retries use **fresh seeds**. PYTHIA is deterministic given its seed, so
re-running a wedged job unchanged risks wedging in the same place -- which is
also why `periodic_release` is the wrong mechanism. `seed_for(tune, job_index, attempt=0, tunes=ALL_TUNES, *,
campaign_ordinal)` (`tools/campaign.py:111-117`) keeps every attempt reproducible
and non-colliding, and the new seeds are burned to the ledger. The `campaign_ordinal`
argument is what makes non-colliding true ACROSS campaigns rather than only
within one.

Only jobs held by `HF_HANG_GUARD` are auto-resubmitted. Anything held for
another reason is reported and left alone, because resubmitting it blindly
would hide whatever actually went wrong.

## After production

```bash
make manifest CAMPAIGN=HF_RUN3_V1        # refuses unless exposure is equal
```

The manifest builder will not emit unless every tune has the same number of
promoted jobs and that number divides into the ten analysis blocks. If it
refuses, run `make status-full` and `make resubmit`.

## Storage

About 83 MB per 100k-event job, so a full three-tune campaign (3000 jobs,
300M events) is roughly **250 GB**. `make doctor` reports free space at the
production root.

Set `HF_PRODUCTION_ROOT` in `config/dependencies.local.conf`. It defaults to
`<checkout>/Production`, which would put hundreds of gigabytes inside the git
working tree; the worker warns if the resolved root is inside the checkout.

On shared storage, avoid broad directory discovery and concurrent merge scans.
Run `df -h "$HF_PRODUCTION_ROOT"` before a full campaign and apply the site's
capacity policy.

## Two operational rules

**Do not move the checkout while a campaign is running.** Every job verifies at
startup that the checkout is at the commit its submit file recorded, and clean.
A `git checkout`, `reset` or `pull` mid-campaign makes every job that starts
afterwards refuse to run.

Site automounts may disappear when a login session ends. Verify the site's
detached-process and mount policy before starting a long merge or extraction.

## Legacy

The historical `submitCondor_*.sub` files and the `RootFiles/` and `Jobs/`
trees are NOT in this repository: `git ls-files` matches none of them. They
were removed in the 2026-08-22 rebuild and survive only in the history of the
pre-rebuild repository. They used discovery, seed modifiers and retry
conventions this workflow does not accept. `runCondorJob.sh` refuses any invocation that is
not `--campaign`; reconstruct an old run from the commit that produced it.
