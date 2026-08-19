# Campaign record — HF_RUN3_V1

**Full production. Rendered, submitted, and RELEASED 2026-08-09. RUNNING.**

| event | UTC |
|---|---|
| rendered + submitted | **2026-08-09T04:17:14Z** |
| **released** | **2026-08-09T04:23:55Z** |

**Release pre-condition verified before acting:** all **3000/3000** holds were
`HoldReasonCode 15` — zero jobs held for any other reason at t=0.
`condor_release 5390385` → *"All jobs in cluster 5390385 have been released"*.

**Queue immediately after release:** **0 held**, 2999 idle, 1 running. Job 0
(MONASH) took a slot and began PYTHIA 8.317 initialisation.

## `PRODUCTION_START` VERIFICATION — DONE 2026-08-09, and v2 is confirmed live

**This is the first confirmation that `seed_derivation_v2` reached the jobs.
Everything before it was pre-submission checking.**

From completed job logs:

```
PRODUCTION_START campaign=HF_RUN3_V1 tune=MONASH logical_id=0 role=primary attempt=0 seed=130000001 requested_successes=100000
PRODUCTION_START campaign=HF_RUN3_V1 tune=MONASH logical_id=2 role=primary attempt=0 seed=130000003 requested_successes=100000
PRODUCTION_END attempts=100000 successful_events=100000 failed_attempts=0 tree_entries=100000
```

From `attempt_metadata/MONASH/hf_MONASH_job000_attempt000_5390385_0.json`:

| field | value |
|---|---|
| `campaign` | **HF_RUN3_V1** |
| **`campaign_ordinal`** | **3** |
| `tune` | MONASH |
| `logical_id` | 0 |
| **`seed`** | **130000001** |
| `attempt` | **0** |

**`seed = 130000001` is exactly the hand-computed v2 value**
(`SEED_BASE + 3*CAMPAIGN_STRIDE + 0 + 0 + 0`), and `logical_id=2 → 130000003`
increments correctly. **Attempt 0 — the axis B15b freed is being used as
intended.**

**Early-completion sanity, same date:** `PRODUCTION_END` shows
`successful_events=100000 failed_attempts=0`; promoted
`hf_MONASH_job000.root` is 92,200,782 B (88 MiB, matching the 88.0 MiB/job
budget) with its `.sha256` sidecar, mode `-r--r--r--` (write-once);
**no validator failures in any receipt.**

## TUNE-INDEX SEED VERIFICATION — CLOSED for JUNCTIONS, 2026-08-09

**The last unverified term of `seed_derivation_v2`, outstanding across five
sessions because the jobs genuinely had not run.**

```
PRODUCTION_START campaign=HF_RUN3_V1 tune=JUNCTIONS logical_id=0 role=primary attempt=0 seed=131000001
```

`attempt_metadata/JUNCTIONS/hf_JUNCTIONS_job000_attempt000_5390385_1000.json`:

| field | value |
|---|---|
| `campaign` | HF_RUN3_V1 |
| **`campaign_ordinal`** | **3** |
| `tune` | JUNCTIONS |
| `logical_id` | 0 |
| **`seed`** | **131000001** |
| `attempt` | **0** |

**`131000001` is exactly the predicted value:**
`SEED_BASE + 3*CAMPAIGN_STRIDE + 1*TUNE_STRIDE`
`= 100000001 + 30,000,000 + 1,000,000`.

**This is the term MONASH could not exercise.** With MONASH at
`+0*TUNE_STRIDE` (130000001) and JUNCTIONS at `+1*TUNE_STRIDE` (131000001),
**every factor of the v2 formula except the CLOSEPACKING tune index is now
confirmed against live production data.**

**REMAINING: CLOSEPACKING, expected `132000001`** (`+2*TUNE_STRIDE`). Jobs
2000+ have not started.

## MILESTONE — the MONASH block is complete

**1000 / 1000 MONASH jobs promoted, with ZERO hang-guard holds.**

That is the flag worth recording explicitly: **no MONASH job in this campaign,
or in any campaign in project history, has ever tripped the 3600 s CPU guard.**
Consistent with MONASH's 377 s measured mean — a 9.5x margin. **The ~2.7 % hang
expectation is carried almost entirely by the CR tunes** (means 659 s and
989 s), which have only just begun, so the guard's window is opening now rather
than having been survived.

**~1182 of 3000 complete. Zero holds at every snapshot to date.**

**STILL OUTSTANDING — per-tune verification for CLOSEPACKING.** Jobs 2000+
have not started. **CLOSEPACKING job 0 must show `132000001`**
(`+2*TUNE_STRIDE`). That is the only remaining unverified factor of the v2
formula.

## FIRST HANG-GUARD HOLD — 2026-08-09. Documented, NOT acted on

**The first genuine hang-guard hold of the campaign, and the first real
instance in project history.**

| field | value |
|---|---|
| job | **`5390385.1003`** = **JUNCTIONS logical_id 3** |
| `RemoteUserCpu` | **3607.0 s** |
| `RemoteWallClockTime` | 3616.0 s |
| **CPU / wall** | **0.9975** |
| `NumJobStarts` | 1 (first attempt) |
| `EnteredCurrentStatus` | 1786258820 |
| `HoldReason` | `HF_HANG_GUARD suspected generator hang: cpu>3600s or wall>14400s` |

**This is a genuine hang, not the parking brake.** CPU 3607 s sits just past the
3600 s threshold and **CPU/wall = 0.9975** is the documented wedged-generator
signature — a hung generator burns CPU at ~97 %+ while a slow-but-healthy job on
a contended node shows a low ratio (`Makefile:38-40`). Compare
`HoldReasonCode 15`, the submit-time parking brake, which was cleared at
release.

**It is JUNCTIONS, not MONASH.** The loud-flag rule — any MONASH hang would be
the first in project history — is **not** triggered. Consistent with the CR
tunes carrying essentially the whole hang history.

**NOT ACTED ON, by owner ruling: no retry rounds at end-of-context.** Held jobs
wait; a botched first batch test of `resubmit_held.py` does not undo. **This is
the successor's first retry, and it is a batch of one — the gentlest possible
first exercise of a tool that has never run on more than one job.**

**Rate so far: 1 hold in ~1545 completed = 0.06 %**, well under the ~2.7 %
budget, but the CR tunes have only just begun and carry the expectation.

## Progress log

| date (UTC) | queue | promoted | holds |
|---|---|---|---|
| 2026-08-09 ~04:24 | 2999 idle / 1 running | 0 | 0 |
| 2026-08-09 ~04:5x | 2961 idle / 18 running | **22 MONASH** | **0** |
| 2026-08-09 ~05:0x | 2866 idle / 72 running | **62 MONASH** | **0** |
| 2026-08-09 ~05:1x | **2829 idle / 82 running** | **89 MONASH**, 0 JUNCTIONS, 0 CLOSEPACKING | **0** |

**Tune-index seed verification: STILL OUTSTANDING as of the last snapshot.**
89 completed + 82 running puts the campaign at roughly job 171 of MONASH's
1000. **JUNCTIONS starts at job 1000 and CLOSEPACKING at 2000**, so neither has
begun and neither can be checked yet. **This is the last unverified part of the
v2 seed formula** — MONASH exercises `SEED_BASE + ordinal*CAMPAIGN_STRIDE` but
not the tune term. Check on first sighting: **JUNCTIONS job 0 ⇒ `131000001`**,
**CLOSEPACKING job 0 ⇒ `132000001`**.

**Holds: zero, read by reason** (`condor_q -constraint "JobStatus==5"` empty) at
every snapshot. **No retry round has been earned.** The hang guard fires only
above 3600 s CPU and MONASH's mean job is ~377 s; **the CR tunes carry
essentially the whole hang history (means 659 s and 989 s), so holds should be
expected once jobs 1000+ start, not before.**

**No hang-guard holds have appeared yet.** Expected ~2.7 % and they can only
appear after >3600 s CPU, so their absence this early is uninformative rather
than reassuring.

**Checkout freeze in force:** the Nikhef checkout stays at `e6429b7` until this
campaign completes — jobs verify their commit at startup. Local commits
accumulate; anything that must run on Nikhef with new code uses the
scratch-deploy pattern.

## Identity

| | |
|---|---|
| Campaign | **HF_RUN3_V1** |
| Campaign ordinal | **3** |
| Seed derivation | **`seed_derivation_v2`** (B15b, `12b1f1a`) |
| Submit attempt | **0** — the attempt axis is retry-only again under v2 |
| Cluster ID | **`5390385`** (single cluster, procs `0-2999`) |
| Submitted (UTC) | **2026-08-09T04:17:14Z** |
| Local HEAD at submit | **`e6429b7`** |
| Nikhef HEAD at submit | **`e6429b7`** |
| Producer sha256 | **`e54b27bb9e3fcfd42d70193e08e2eacf965cc5081eabb5c42a9971203f130659`** |

**Cluster ID taken from the `condor_submit` response itself** — "3000 job(s)
submitted to cluster 5390385" — never from a `condor_q` discovery query.

## Shape

| | |
|---|---|
| Tunes | MONASH, JUNCTIONS, CLOSEPACKING |
| Jobs per tune | **1000** |
| Events per job | **100000** |
| Total jobs | **3000** (`PRODUCTION_SUBMIT_RENDERED rows=3000 attempt=0`) |
| Total events | 3 x 10^8 |

## Seeds

| | |
|---|---|
| Ledger before | **430** lines, 430 unique |
| Ledger after | **3430** lines, **3430 unique** |
| Burned this campaign | **3000** |
| Seed range | **130000001 .. 132001000** |
| Max seed vs PYTHIA domain | 132001000 ≤ 900000000 |

**Per-tune first seeds, hand-verified against the v2 formula before submitting**
(`SEED_BASE + ordinal*CAMPAIGN_STRIDE + tune*TUNE_STRIDE + attempt*ATTEMPT_STRIDE + job`):

| tune | job 0, attempt 0 | expected | present |
|---|---|---|---|
| MONASH | 130000001 | `100000001 + 3e7 + 0` | yes |
| JUNCTIONS | 131000001 | `100000001 + 3e7 + 1e6` | yes |
| CLOSEPACKING | 132000001 | `100000001 + 3e7 + 2e6` | yes |

**Pre-registered render checks, all green before `condor_submit`:** exactly 3000
new seeds; ledger 430 → 3430 all unique; every seed ≤ 9x10^8; **disjoint from
the prior 430**; three hand-computed seeds present.

## Budget

| | |
|---|---|
| Generation | **562.5 CPU-hours** (`REPRODUCIBILITY.md` §6, measured means) |
| Retry overhead | **~2.7 %** hang rate, two-to-three rounds |
| Attempt budget | `MAX_ATTEMPTS = 10`, **all ten available** — v2 freed the attempt axis, which v1 had consumed to 8/10 |
| Raw output | ~264 GB at 88.0 MiB/job, against 1442 GB free |

## Release — REQUIRED BEFORE ANY WORK HAPPENS

**All 3000 jobs are held with `HoldReasonCode 15`, "submitted on hold at user's
request".** This is deliberate:
`tools/render_production_submit.py:286` emits `hold = True` unconditionally, and
it appears at `submit_HF_RUN3_V1_full.sub:14`.

**Submission and starting are two separate acts.** The jobs are queued, their
seeds are burned, and their provenance is fixed — but **nothing runs until they
are explicitly released.** That was not done in the submitting session and is
not an oversight.

**Distinguish these two holds, because they look identical in `condor_q`:**

| hold | when | meaning |
|---|---|---|
| `HoldReasonCode 15`, "at user's request" | **at submit, all 3000** | the deliberate `hold = True` parking. Cleared by release |
| `HF_HANG_GUARD suspected generator hang` | after >3600 s CPU or >14400 s wall | the real hang guard (`:17-18`), ~2.7 % expected, retry work |

**A held job is not a failed job in either case.**

## Provenance chain

- Producer rebuilt on Nikhef immediately before submission, **byte-identical**
  to the SHA carried by HF_PT2_INT — so this campaign's producer is the same
  binary that produced the validated intermediate campaign.
- `make check` bare on Nikhef: **25/25** at `e6429b7`.
- Ordinal 3 verified unused on disk before submission (1, 1, 1, 2 in use).

---

## Session 2026-08-09 (v22): seed derivation CLOSED; first retry STOPPED

### `seed_derivation_v2` — live verification COMPLETE

CLOSEPACKING started 2026-08-09 09:07:47. Its logical job 0 (proc 2000,
`condor_logs/CLOSEPACKING/job_0_5390385_2000.out:101`) reports:

```
 | Random:seed                                   |                132000001 |           -1               900000000 |
```

**Pre-registered before looking: `132000001`. Observed: `132000001`.** This was
the last unverified factor of the v2 formula.

| tune | expected | observed | evidence |
|---|---|---|---|
| MONASH | 130000001 | 130000001 | prior session |
| JUNCTIONS | 131000001 | 131000001 | prior session |
| CLOSEPACKING | **132000001** | **132000001** | **PYTHIA banner, this session** |

**All three tune factors of `SEED_BASE + ordinal*CAMPAIGN_STRIDE +
tune*TUNE_STRIDE + attempt*ATTEMPT_STRIDE + job` are now live-verified.** The
attempt term remains unexercised in production because no retry has been
rendered (below).

**Non-result, reported as one:** the brief asked for *sidecar* confirmation.
`attempt_metadata/CLOSEPACKING` holds **0** sidecars — they are written on job
completion and no CLOSEPACKING job has finished. Sidecar confirmation is
**pending**, not obtained. The PYTHIA banner is the stronger evidence in any
case: it is the generator reporting the seed it actually initialised with,
where a sidecar records the renderer's intent.

### ITEM-STOP: the batch-of-one retry is not expressible with this tool

**Nothing was applied. `--apply` was never passed. The ledger is untouched.**

The brief and handoff v21 both direct a "batch of one" retry of `5390385.1003`
via `tools/resubmit_held.py`. **That is not executable while the campaign is in
flight**, for a reason in the tool's own design rather than any misbehaviour.

`tools/resubmit_held.py:179-184` builds its work list as *every job slot with no
promoted output*:

```python
missing = [f"{tune}:{job}" for tune in tunes for job in range(args.jobs)
           if (tune, job) not in done]
```

The hang-guard reason gates **only the `condor_rm`** (`:191`, `:221-223`). It
does not gate the render: `:240` passes `--only-jobs ",".join(missing)`. There
is **no per-job or per-jobid selection flag** — `--help` confirms the full
option list. The tool's docstring states the design intent plainly:
*"Resubmit jobs that produced no output … a campaign with any job missing cannot
be merged."* **It is built to run once, after the campaign drains**, when "no
promoted output" and "failed" are the same set.

**Measured, dry run (the default; read-only, returns at `:219` before any
action):**

```
job slots with no promoted output: 1244
held in queue: 13 (13 by the hang guard)
would render attempt 1 for 1244 jobs
```

**Pre-registered before running: ~1303 (= 3000 − promoted), matching the queue
count, not 9.** Observed 1244 — the structural claim held exactly; the
arithmetic difference is jobs promoting during the interval.

**What `--apply` would have done:** `condor_rm` the 13 guard-held jobs
(intended), then render a **1244-job** retry submit file duplicating ~1231 jobs
**currently running or idle in the queue**, and with `--seed-ledger
--burn-seeds` burn **1244 seeds**, taking the ledger 3430 → 4674 irreversibly.

**Ledger verified intact after the dry run:** 3430 lines, 3430 unique,
min `100000001`, max `132001000`, mtime `2026-08-09 06:16:49` (pre-session).
The pre-registered retry seed `131100004` is **not** burned.

**Pre-registration retained for whoever runs the retry:** JUNCTIONS,
logical_id 3, attempt 1, ordinal 3 ⇒ **`131100004`**
(`100000001 + 3e7 + 1e6 + 1e5 + 3`), computed from `campaign.seed_for` before
any render.

**Recommendation — owner decision, not taken here:** leave the guard-held jobs
in the queue until the campaign drains, then run `resubmit_held.py` **once**,
which is its design. They hold 14 of 3000 slots and are not limiting throughput
against 906 idle jobs. The alternative — a `--only-jobs` selection flag — is a
tool change during a live campaign and is governed by `RELEASE_BLOCKERS.md`.

### Campaign state at time of writing

| tune | promoted | in queue | held | note |
|---|---|---|---|---|
| MONASH | **1000 / 1000** | 0 | **0** | complete, zero hang holds across all 1000 |
| JUNCTIONS | ~773 | ~213 | **14** | all holds are JUNCTIONS |
| CLOSEPACKING | 0 | 1000 | 0 | **started 09:07:47**, 108 jobs running |

Queue by status: **906 idle, 308 running, 14 held** (= 1228; 3000 − 1228 = 1772
promoted).

**Hold reasons read individually, never by count** — all 14 carry
`HF_HANG_GUARD suspected generator hang`. CPU/wall for all: **0.976 – 0.998**,
`NumJobStarts 1` — the wedged-generator signature per `Makefile:38-40`. **No
hold is anything other than the hang guard. No MONASH hold** — the loud flag did
not fire.

**Hang rate:** 14 / ~787 JUNCTIONS attempts = **1.8 %**, inside the ~2.7 %
budget. Holds rose 9 → 13 → 14 over ~40 min of this session, consistent with
JUNCTIONS carrying the hang history as predicted.

### Frozen-checkout freeze: intact

Nikhef `/data/alice/ipardoza/Hadronization` verified at **`e6429b7`**,
unmoved. Untracked `submit_HF_PT2_INT_intermediate.sub` is pre-existing and does
not affect HEAD.

---

## Session 2026-08-09 (v24): not drained; the CLOSEPACKING rate corrected

### Status — retry round 1 NOT run, by the brief's own condition

| status | count |
|---|---|
| idle (1) | **0** |
| running (2) | **25**, all CLOSEPACKING |
| held (5) | **94**, every one `HF_HANG_GUARD` |

**Not drained.** The brief authorises retry round 1 only on a drained queue
("If NOT drained, record status and skip"). 25 jobs are still running, so
nothing was run. **The ledger is untouched at 3430 / 3430 unique.**

| tune | promoted | running | held | hang rate |
|---|---|---|---|---|
| MONASH | **1000 / 1000** | 0 | **0** | **0.0 %** — final |
| JUNCTIONS | 940 | 0 | **60** | **6.0 %** — final |
| CLOSEPACKING | 941 | **25** | **34** | **≥3.4 %, ≤5.9 %** — not final |

All three tunes account exactly: 1000 / 1000 / 1000.

### CORRECTION: the CLOSEPACKING hang rate, and what it does to the ruling

**Handoff v23 recorded CLOSEPACKING at "~1.2 %". That was an early-sample
underestimate and it is wrong.** At that reading CLOSEPACKING had 11 holds
against ~917 promoted; it now has **34** against 941, and 25 jobs are still
running. The rate did not converge early because holds accrue only after the
3600 s CPU guard fires, so a tune that has just started is systematically
under-counted. **This is exactly why the blocker instructs that the bounds be
recomputed at drain, and why the 2.7 % sentence never carries forward.**

**Bounded, since the tune has not finished** — preferring a bound to a
measurement, as the practice says:

- **lower bound** (all 25 remaining promote): 34 / 1000 = **3.4 %**
- **upper bound** (all 25 remaining hang): 59 / 1000 = **5.9 %**

**Consequence for the production note the brief asks to record.** The ruling
states CLOSEPACKING has "five times fewer hangs" than JUNCTIONS, concluding the
hang is junction-CR-specific rather than CPU exposure. **That ratio came from
the stale 1.2 % figure** (6.0 / 1.2 = 5). Against the measured rate the ratio is

> **JUNCTIONS : CLOSEPACKING = 6.0 % : [3.4 %, 5.9 %] = between 1.02x and
> 1.76x** — **not 5x.**

**So the counterpoint as stated is not supported by the data.** The two CR tunes
hang at rates that may be within a factor of 1.02 of each other. What survives
is the far stronger and unchanged contrast: **MONASH, 0 hangs in 1000 jobs,
against both CR tunes at several per cent.** That still separates CR from
non-CR. It does **not** separate junction-CR from close-packing-CR, and the
"not CPU exposure" conclusion loses the evidence it rested on — CLOSEPACKING is
the slower tune per event and now also hangs at a comparable rate, which is the
pattern CPU exposure would produce.

**The origin of the error is this record's own previous entry, not the owner's
reading.** Recorded here so the corrected number, not the stale one, is what
carries forward.

**The final per-tune table and the recomputed discard-bias bounds are still
owed** and must be taken at drain, when CLOSEPACKING's rate is final.

### Frozen-checkout freeze: still intact

Nikhef verified at **`e6429b7`**, unmoved.

---

## DRAIN, and RETRY ROUND 1 — executed and verified

### Final attempt-0 table

| tune | promoted | held | **final hang rate** |
|---|---|---|---|
| MONASH | **1000 / 1000** | **0** | **0.0 %** |
| JUNCTIONS | 940 | 60 | **6.0 %** |
| CLOSEPACKING | 941 | 59 | **5.9 %** |
| **total** | **2881 / 3000** | **119** | **4.0 %** |

Every one of the 119 holds carried `HF_HANG_GUARD`. **No MONASH hold in the
whole campaign** — the loud flag never fired.

### The CLOSEPACKING bound closed at its ceiling, and it settles the ruling

The previous entry bounded CLOSEPACKING at **[3.4 %, 5.9 %]** with 25 jobs still
running: 3.4 % if all 25 promoted, 5.9 % if all 25 hung. **All 25 hung.** The
rate is **5.9 %**, the exact upper bound.

| claim | value |
|---|---|
| owner ruling as briefed | CLOSEPACKING has **5x fewer** hangs than JUNCTIONS |
| from the stale 1.2 % figure | 6.0 / 1.2 = 5 |
| **measured, both tunes final** | **6.0 % vs 5.9 % = 1.02x** |

**The two CR tunes hang at rates that are indistinguishable.** The
junction-CR-specific reading is not supported; what survives is the far
stronger **MONASH 0 / 1000 against both CR tunes near 6 %**, which separates CR
from non-CR and says nothing about which CR.

**A mechanism the last 25 jobs make visible.** They were the slowest-finishing
jobs in the campaign, and *all* of them hung. The guard fires on CPU > 3600 s,
so the jobs most likely to trip it are by construction the slowest — the tail
of the runtime distribution is selected into the hold set. CLOSEPACKING is the
slower tune per event and hangs at essentially JUNCTIONS' rate. **That is the
pattern CPU exposure produces**, and it is the opposite of the recorded
"not CPU exposure" reading. Recorded as a production note, not a conclusion:
distinguishing a genuine wedge from guard-tripping slowness needs the retry
rates, which round 1 will supply.

### Retry round 1 — every pre-registration matched

**Pre-registered before any command:** rendered count = 3000 − 2881 = **119**;
the rendered set = exactly the unpromoted slots; **JUNCTIONS logical_id 3 draws
`131100004`**.

**Dry run (default, read-only):**

```
job slots with no promoted output: 119
held in queue: 119 (119 by the hang guard)
would render attempt 1 for 119 jobs
```

**missing == held == 119.** That equality is precisely what makes the tool safe
post-drain and unsafe before it (v22 §2): once drained, "no promoted output"
and "failed" are the same set by construction.

**Applied.** 119 guard-held jobs removed;
`PRODUCTION_SUBMIT_RENDERED rows=119 attempt=1`.

| verification | pre-registered | observed |
|---|---|---|
| ledger lines | 3430 + 119 = **3549** | **3549** |
| ledger unique | **3549** | **3549** |
| JUNCTIONS logical_id 3 seed | **`131100004`** | **`131100004`** (ledger line 3431) |
| attempt tag | attempt1 | all 119 tagged `# HF_RUN3_V1 attempt1` |
| JUNCTIONS band `1311…` | 60 | **60** |
| CLOSEPACKING band `1321…` | 59 | **59** |
| seed range | — | `131100004 … 132100998` |

**A false alarm worth recording**, because it nearly read as a mismatch:
`grep -c "^131100004$"` returned **0**, and the pre-registration looked broken.
The seed was present all along — ledger lines carry a trailing comment
(`131100004  # HF_RUN3_V1 attempt1`), so the `$` anchor could never match.
**The check was wrong, not the seed.** Verify the shape of a file before
concluding from a pattern that fails on it.

### `seed_derivation_v2` — the attempt term is now live-verified

`131100004 = 100000001 + 3x10^7 + 1x10^6 + 1x10^5 + 3`
(`SEED_BASE + ordinal*CAMPAIGN_STRIDE + tune*TUNE_STRIDE +
attempt*ATTEMPT_STRIDE + job`). **Every factor of the formula — campaign, tune,
attempt and job — has now been verified against live production output.**

### Requeued

`condor_submit` → **119 jobs to cluster `5393672`**, all arriving
`HoldReasonCode 15 "submitted on hold at user's request"` — the parking brake,
by design. `condor_release 5393672` → **119 idle, 0 held**. Cluster `5390385`
is fully gone from the queue.

**The freeze still applies to the new cluster:** these 119 jobs verify their
commit at startup and were rendered from the frozen checkout, so
`/data/alice/ipardoza/Hadronization` stays at **`e6429b7`** until they finish.

### Round 2 projection

At the measured attempt-0 rates, round 1 should leave:

| tune | retried | rate | expected residual |
|---|---|---|---|
| JUNCTIONS | 60 | 6.0 % | **~4** |
| CLOSEPACKING | 59 | 5.9 % | **~3** |
| total | 119 | — | **~7** |

**This projection assumes the hang rate is a property of the tune and not of
the seed**, which retry round 1 is the first opportunity to test: a retry draws
a *fresh* seed, so if hangs are seed-specific the residual will be far below 7,
and if they track slow events it will be near it. **Record the actual residual
against this number** — it is the cleanest discriminator available between the
two mechanisms, and it costs nothing to observe.

---

## Session 2026-08-09 (v25): rulings recorded; round 1 measured; round 2 applied

### Owner rulings, recorded

**1. The CLOSEPACKING production note is RETRACTED** (owner's error, built on
this record's own v23 early sample). The supported statement replacing it:

> **MONASH: 0 hangs across ~2100 jobs over three campaigns. Both CR tunes near
> 6 %.** The hang is **CR-specific**. The **JUNCTIONS-vs-CLOSEPACKING
> distinction is not supported.**

**2. The "budget exceeded" alarm is dissolved, per tune.** HF_PT2_INT's per-tune
rates were **5 % / 3 % on n=100 each**; 6.0 % / 5.9 % on n=1000 is compatible
with those within counting statistics. **The 2.7 % aggregate was never the right
comparison** — it averages a 0 % tune with two ~6 % tunes and describes none of
them. Recorded here beside the rates so the alarm does not refire.

**3. Discard-bias bounds are recomputed per tune at CONVERGENCE**, all attempts
summed — not at attempt 0, and not now.

### Retry round 1 — the residual, against both pre-registered hypotheses

| | |
|---|---|
| pre-registered under a ~6 % seed lottery | **~7 of 119** |
| pre-registered under seed-specific hangs | **much lower than 7** |
| **observed** | **exactly 7** |

| tune | retried | succeeded | residual | attempt-1 rate |
|---|---|---|---|---|
| JUNCTIONS | 60 | 58 | **2** | 3.3 % |
| CLOSEPACKING | 59 | 54 | **5** | 8.5 % |
| **total** | **119** | **112** | **7** | **5.9 %** |

Split taken from `attempt_metadata` sidecars, not from proc-order arithmetic;
the proc ranges agree independently.

**The lottery hypothesis is the one that survives.** Attempt-1's aggregate CR
rate is **5.9 %** against attempt-0's **5.95 %** — reproduced under *fresh*
seeds. **Hangs are not seed-specific.** A retry does not "fix" a bad draw; it
re-enters the same lottery.

**The per-tune split is not significant at these counts.** 2/60 = 3.3 % ± 2.4 %
against 5/59 = 8.5 % ± 3.8 % (Poisson) — a difference of 5.2 % ± 4.5 %, about
1.2 sigma. **Consistent with one common CR rate**, which is what ruling 1 says.

### Retry round 2 — applied, every pre-registration matched

**Pre-registered:** missing = 3000 − 2993 = **7**; `missing == held == 7`
(re-verified for this round, not assumed from round 1); split **2 JUNCTIONS /
5 CLOSEPACKING**; and the seven exact seeds, computed from `campaign.seed_for`
before rendering.

Dry run returned exactly that, naming `JUNCTIONS:239, JUNCTIONS:535,
CLOSEPACKING:{27,33,136,213,745}`.

**Applied.** `PRODUCTION_SUBMIT_RENDERED rows=7 attempt=2`. Ledger
**3549 → 3556, all unique**. All seven pre-registered seeds present and tagged
`attempt2`:

```
131200240  131200536  132200028  132200034  132200137  132200214  132200746
```

Requeued as cluster **`5396679`**, parked on code 15 by design, released.

**The freeze therefore still applies:** these jobs verify `e6429b7` at startup.

### Bimodality measurement — LAUNCHED, NOT HARVESTED

`condor_history 5390385` detached on the login node, **PID `895623`**, writing
`/data/alice/ipardoza/bimodality_5390385.txt`, with
`/data/alice/ipardoza/bimodality.done` as the completion sentinel.

**It stalled at 2641 rows and did not advance over ~2.5 hours**, process still
alive. The brief warned this scan is slow on this pool; it is slower than that.
**Reported as a non-result: no per-tune completed-CPU distribution was
obtained, and the bimodality question is untouched.** Do not relaunch — check
the PID and the sentinel first.

---

## BIMODALITY — MEASURED. The hangs are genuine wedges.

**The pre-registration:** a clean empty gap between each CR tune's completed
maximum and the 3600 s guard would mean genuine wedges; **absence** of the gap
would mean the guard is clipping a real slow tail — a different problem with
different remedies.

**The gap is there, and it is enormous.**

### Route 1 — `condor_history 5390385`, 3000 rows, attempt 0

| tune | n completed | n guard-removed | **completed max CPU** | removed min CPU | **GAP** | completed mean |
|---|---|---|---|---|---|---|
| MONASH | 1000 | 0 | **758.0 s** | — | — | 489.7 s |
| JUNCTIONS | 940 | 60 | **1339.0 s** | 3601.0 s | **2262 s** | 920.2 s |
| CLOSEPACKING | 941 | 59 | **1597.0 s** | 3601.0 s | **2004 s** | 1200.3 s |

**Zero completed jobs above 3000 s in any tune.** Above 3300 s: zero. The
busiest tune's slowest healthy job finishes at **1597 s**, less than half the
guard.

### Route 2 — `attempt_metadata` sidecars, all attempts, independent

`elapsed_seconds` is the producer's own wall measurement, a different quantity
from `RemoteUserCpu` and recorded by different software:

| tune | n | max wall | p99 | mean | n > 3000 s |
|---|---|---|---|---|---|
| MONASH | 1000 | 731 s | 692 s | 461.8 s | **0** |
| JUNCTIONS | 999 | 1316 s | 1282 s | 887.5 s | **0** |
| CLOSEPACKING | 1000 | 1578 s | 1524 s | 1168.0 s | **0** |

**The two routes agree** — maxima within ~3 % (758/1339/1597 CPU against
731/1316/1578 wall), means consistently ~5 % lower in wall, which is the
CPU/wall ratio plus job setup that condor counts and the producer does not.
**Both give the same answer: nothing completes near the guard.**

### Reading

**The runtime distribution is bimodal with an empty 2 ks band between the
modes.** A healthy population topping out at 1.3–1.6 ks, and a wedged
population that runs until the guard kills it at 3601 s. **There is no
continuum between them**, so the guard is not clipping a slow tail — there is
no slow tail within 2000 s of it to clip.

**The wall ≈ CPU caveat, measured:** guard-removed jobs run at CPU/wall
**0.989–0.991 mean** (min 0.967, max 0.999). They are spinning, not blocked on
I/O and not descheduled. Wall and CPU are interchangeable for these jobs, which
is why the two routes above agree.

> ### THIS CORRECTS A READING IN HANDOFF v24
> v24 recorded that the last 25 CLOSEPACKING jobs all hanging was "the pattern
> CPU exposure would produce", and that CLOSEPACKING being the slower tune while
> hanging at JUNCTIONS' rate supported exposure over a tune-specific mechanism.
> **The gap refutes the exposure reading.** Under CPU exposure the completed
> distribution would run up toward 3600 s and the guard would bite the tail of a
> continuum; instead it stops dead at 1597 s.
>
> **The last-25 observation has a simpler explanation that is not about runtime
> at all.** A wedged job runs until a guard kills it, so wedged jobs are
> *always* the last to leave a queue, whatever the tune's speed. That is a
> selection effect on **exit order**, not evidence about the **runtime
> distribution**. v24 conflated the two.

**What the mechanism is remains unknown** — that a job wedges is now
established; why is not. What is settled is that **it is not the guard
mis-firing on legitimately slow jobs**, so the guard's threshold needs no
revision and the retried jobs were correctly identified.

### Per-tune completed means, at 10x the previous statistics

Earlier campaigns cited 377 / 659 / 989 s. Measured here over 1000 jobs each:
**489.7 / 920.2 / 1200.3 s** (CPU). Same ordering, all higher. **The 3600 s
guard sits at 3.0x CLOSEPACKING's mean and 7.4x MONASH's** — comfortable for
every tune.

### Provenance

The `condor_history` scan launched last session as PID 895623 **did complete**,
at 15:09, writing all 3000 rows and its sentinel. Handoff v25 recorded it as
stalled with no result; that was true when written and is **superseded here**.
The PID was already gone, so nothing was killed.

---

# CAMPAIGN CLOSED — 3000 / 3000

**Converged after three retry rounds.** Verified by the success-verified probe
landed this session (`tools/queue_probe.py`): `QUEUE_EMPTY count=0`, exit 0,
**with the schedd banner present** — an answered question, not an unanswered
one.

| tune | promoted |
|---|---|
| MONASH | **1000 / 1000** |
| JUNCTIONS | **1000 / 1000** |
| CLOSEPACKING | **1000 / 1000** |

## Final per-tune table, across all attempts

**Derived from the seed ledger, not inherited.** Every HF_RUN3_V1 seed encodes
its tune and attempt, so the attempt counts are read directly:

| tune | att 0 | att 1 | att 2 | att 3 | **total attempts** | **hangs** | **hang rate** |
|---|---|---|---|---|---|---|---|
| MONASH | 1000 | — | — | — | **1000** | **0** | **0.00 %** |
| JUNCTIONS | 1000 | 60 | 2 | 1 | **1063** | **63** | **5.93 %** |
| CLOSEPACKING | 1000 | 59 | 5 | — | **1064** | **64** | **6.02 %** |
| **all** | 3000 | 119 | 7 | 1 | **3127** | **127** | **4.06 %** |

**Arithmetic checks, both closing:** attempts at each level equal the previous
level's hangs (60+59 = 119; 2+5 = 7; 1 = 1). Ledger 3557 − 430 pre-existing
= **3127**, matching the attempt total exactly.

## The two CR tunes are indistinguishable

**5.93 % against 6.02 %.** Poisson uncertainties are ±0.75 pp and ±0.75 pp, so
the difference is **0.09 ± 1.06 pp** — consistent with zero.

> **The settled statement:** MONASH **0 hangs in 1000 attempts** here, and 0
> across ~2100 jobs over three campaigns. Both CR tunes at **~6 %**. **The hang
> is CR-specific. The JUNCTIONS-vs-CLOSEPACKING distinction is not supported**,
> and this final table is the strongest evidence yet that there is none to
> support.

**The 2.7 % aggregate is dead and is not replaced by 4.06 %.** The aggregate
averages a 0 % tune with two ~6 % tunes and describes none of them. **The
per-tune rates above are the numbers that mean anything.**

## Per-tune discard-bias bounds

A hung attempt is discarded and redrawn with a fresh seed. The bias question is
whether discarding correlates with event content.

| tune | logical jobs whose first attempt was discarded | **bound on affected jobs** | attempts discarded | **bound on discarded work** |
|---|---|---|---|---|
| MONASH | 0 / 1000 | **0.00 %** | 0 / 1000 | **0.00 %** |
| JUNCTIONS | 60 / 1000 | **6.00 %** | 63 / 1063 | **5.93 %** |
| CLOSEPACKING | 59 / 1000 | **5.90 %** | 64 / 1064 | **6.02 %** |

**These bounds are the absent-event-class WORST CASE**, per the original
methodology: they assume every missing event could have fallen in one bin. **They
stand as stated. Do not soften them.**

> ### RETRACTION — an overclaim I made in this record, corrected by owner ruling
>
> This paragraph previously argued the true bias was "far smaller" than the
> bound, on the reasoning that a wedged job produces no events at all rather
> than an unrepresentative sample, so **"a wedge is a lost draw, not a skewed
> one."** **That is retracted.**
>
> **It does not follow.** The argument shows a wedged job contributes no *biased
> events*; it says nothing about whether the *set of jobs that wedge* is
> correlated with event content. A job that wedges partway through has already
> sampled a region of phase space, and **whether wedging is content-independent
> is precisely the open question** — which the argument assumed rather than
> established.
>
> **The decisive fact, which I did not have:** the hang mechanism sits in
> **`JunctionSplitting`**. That is **plausibly correlated with exactly the
> junction topologies this study measures**, and it is consistent with the
> per-tune pattern: MONASH 0 %, both CR tunes ~6 %.
>
> **What the lottery evidence does and does not show.** A fresh seed reproduces
> the same ~6 % rate, so the hang is not a property of a particular seed. That is
> **consistent with** content-independence; it does **not establish** it, because
> a content-correlated mechanism firing on ~6 % of *event sequences* would
> reproduce the same per-round rate under fresh draws. **The two hypotheses are
> not distinguished by the retry data.**
>
> The bimodality result stands unchanged on its own claim — the hangs are genuine
> wedges and the guard never mis-fired. **It carries no implication about
> discard bias**, and I over-extended it.

**No further round is needed.** `MAX_ATTEMPTS = 10`; the deepest attempt reached
was **3**.

## Cross-reference: bimodality, and why the retries were correct

The bimodality measurement (recorded above) established gaps of **2004–2262 s**
between each CR tune's completed maximum and the 3600 s guard, with **zero
completed jobs above 3000 s in any tune**, confirmed by two independent routes.

**It then made a live prediction and passed it.** A job observed at
`RemoteUserCpu 2400 s` — inside the empty band — was called wedged; it was held
at **3897 s** about twenty minutes later.

**Two consequences for this close-out:**

1. **Every one of the 127 discarded attempts was a genuine wedge**, not a slow
   job clipped by a threshold. The guard did not mis-fire once.
2. **Operationally:** a running CR job past **~1600 s CPU** is already wedged and
   will not finish. That is a usable early signal, and the measured case for a
   lower guard folds into the existing per-tune-guard entry in
   `POST_SUBMISSION.md` as basis. **No guard change now** — the current
   threshold cost nothing but wall time, since wedged jobs hold slots rather
   than consuming useful throughput.

**The mechanism of the wedge itself remains unknown.**

## Authorization status

`config/statistical_robustness_v1.json` was authorized for edit this generation.
**The contract-driven fix made the edit unnecessary**, so the grant is recorded
**closed-unused** rather than spent. `config/` was not touched.

---

# THE FREEZE IS OVER — SYNC COMPLETE, all verifications green

**Preconditions, none waived:**

| precondition | result |
|---|---|
| 3000/3000, queue empty | ✅ `QUEUE_EMPTY count=0`, **schedd banner present** — verified with `tools/queue_probe.py`, not a bare count |
| first contact green | ✅ both validators, below |
| pre-flight clean | ✅ 43 commits, **no producer TU, tune card, Makefile, `*.cmnd` or `setupEnv.sh`** |

## FIRST CONTACT — fully green against real promoted v2 data

**The fourth-generation debt, discharged.** Both run read-only against
`complete_root_HF_PT2_INT_MONASH` and its ten subsample blocks.

**Block closure**, wrapper exit **0**:

```
PAIR_BLOCK_CLOSURE errors=0 analysis_schema=paul_pair_objects_primary_ground_v2
central_pair_files=300 block_pair_files=3000
object_content_sumw2_closure_checks=1800 additive_metadata_closure_checks=3600
invariant_metadata_checks=600 source_filter_contract_checks=300
expected_central_events=-1 relative_tolerance=2e-10
```

**Every pre-registration matched:** schema resolved to **v2** (not guessed);
`object_content_sumw2_closure_checks=`**`1800`** = 6 × 300, **not 2100**;
`invariant_metadata_checks=`**`600`** = 2 × 300, **not 1500**.

**The wrapper exit of 0 is the stronger result.** The wrapper builds its
expected summary by reading the schema out of the macro's own output and
deriving both counts *for that schema* from the contract. Its exact-match
passing means **the whole derivation chain — schema tag → version → derived
counts — worked end-to-end against production**, not merely that the macro
found no errors.

**Pair-directory allowlist**, exit **0**:

```
PAIR_DIRECTORY_VALIDATION errors=0 expected_files=300 found_root_files=300
raw_campaign=HF_PT2_INT raw_tune=MONASH merge_input_files=100
upstream_executable_sha256=e54b27bb9e3fcfd42d70193e08e2eacf965cc5081eabb5c42a9971203f130659
```

`fatal error` count 0 (the macro genuinely ran) and `PAIR_VALIDATION_ERROR`
count 0. **The deleted `kRequiredAnalysisSchema` and the schema-keyed object set
resolved v2 correctly on production and did not demand
`hFlavourClosureSpecies`** — the exact-match-in-both-directions risk retired
against real data.

**Promoted data byte-identical**, checked before, during and after:
`1d49d2f82802f6716b907a1e4a6f6f68bdd18e551eb4b6337746910d03c917ff` unchanged
throughout. This matters more here than for raw production, because the merged
files are `-rw-r--r--` rather than write-once.

## The sync

| step | result |
|---|---|
| Nikhef advanced | `e6429b7` → `de8857c` → **`5da9dd9`** (ff-only, two bundles) |
| **`make check` bare** | **28 / 28** — pre-registered 28 before leaving the local machine |
| **producer rebuild** | **`sha256=e54b27bb9e3fcfd42d70193e08e2eacf965cc5081eabb5c42a9971203f130659`**, `forced_rebuild=true` |

**The producer SHA is byte-identical to the pre-registration**, and
`forced_rebuild=true` means it was genuinely recompiled rather than a cached
binary reported back — so this is a reproducibility result, not a no-op. It also
agrees with the `upstream_executable_sha256` the allowlist read independently
out of promoted provenance.

> ## BOTH HEADS MATCH: `5da9dd9`
>
> **The first time in six generations.** The checkout freeze, in force since
> HF_RUN3_V1 was submitted, is over. Nikhef will now drift behind local again as
> normal development resumes — that drift is no longer a hazard, because no jobs
> are in flight verifying a commit.

---

## The determinism control — run RETROACTIVELY, and why that is still sound

**The control was ratified as going BEFORE the advance. The advance had already
happened**, in the previous session, so it could not be run as specified. It was
recovered afterwards instead, and the recovered form answers the same question.

**What the control is for:** to establish the build is deterministic in the
current environment, so that a post-sync SHA comparison measures **the code**
rather than **environment drift**.

**Method** — no live state touched: `git archive e6429b7 | tar -x` into
`/data/alice/ipardoza/determinism_control/`, then `make build` there. The live
checkout's HEAD was verified `5da9dd9` before and after the extract.

| evidence | producer sha256 |
|---|---|
| original HF_PT2_INT production build, read from **promoted provenance** by the allowlist | `e54b27bb9e3f…` |
| post-sync build at **`5da9dd9`** (previous session, `forced_rebuild=true`) | `e54b27bb9e3f…` |
| **control build at `e6429b7`, today's environment**, `forced_rebuild=true` | **`e54b27bb9e3f…`** |

**Three independent points agree.** And the producer translation unit is
**byte-identical** across the two commits —
`heavyflavourcorrelations_status.cpp` = `e222a7fb585ce7fefce18816e9fa41ea65b72d8297fa8778c0d2caf7f4ba8ccc`
at both `e6429b7` and `5da9dd9`.

**Conclusion, and its limit.** The environment has not drifted, and the 43
commits did not touch the producer. **The post-sync comparison therefore did
measure the code.** The control is weaker than it would have been run in
advance only in one respect: had it *failed*, the advance would already have
happened and the SESSION-STOP would have been a rollback rather than a
prevention. It did not fail. **The ordering ruling stands for next time.**

---

## RAW REVALIDATION — 3000 files rehashed, promoted data verified byte-for-byte

The canonical manifest was first built **trusting** the `.sha256` sidecars, then
rebuilt with `--rehash`, which recomputes every checksum from the file bytes.

**Pre-registered before running: identical 3000 rows and the SAME manifest
sha256.** A different hash would mean a sidecar disagrees with its file — a
finding about promoted production data, not about the tool.

| | trusting sidecars | **`--rehash`** |
|---|---|---|
| rows | 3000 | **3000** |
| tunes | 3 | **3** |
| events | 300,000,000 | **300,000,000** |
| manifest sha256 | `fcd96eaebd4dc11f071a2c8db8849f6a4cc19b764622a796664e524b27d0fc80` | **identical** |
| blocks | 10 × 300 | 10 × 300 |
| wall | 8.7 s | **11 m 27.85 s** |
| peak RSS | — | **51,708 kB** |

**Every one of the 3000 promoted raw files' bytes agrees with its recorded
checksum.** ~270 GB read and hashed. **This is the first time the promoted
production data of this campaign has been verified against its own provenance
rather than assumed** — and it is the strongest form of that check available,
because the manifest digest is taken over the per-row hashes, so a single
disagreeing byte anywhere would have moved it.

**Resource note, measured not predicted:** 51.7 MB peak RSS, single process,
I/O-bound at ~390 MB/s effective. **The ~441 MiB/child pool arithmetic does not
apply to this tool** — `build_canonical_manifest.py` takes no pool argument and
never holds more than one file's stream. That sizing belongs to the *gate* over
analysis **directories**, a different tool on different inputs.

**The manifest now in `campaigns/HF_RUN3_V1/freeze/` is the sidecar-trusting
build**, which is byte-for-byte the same content; the rehash wrote its own copy
under `/data/alice/ipardoza/rehash_run/freeze/` and the two digests match.

---

# THE v3 ANALYSIS CAMPAIGN — SUBMITTED

**The first production analysis carrying the species axis.**

| | |
|---|---|
| **Cluster** | **`5398658`** — taken from the `condor_submit` response only |
| **Jobs** | **3000**, all arriving idle (status 1) |
| Submitted | 2026-08-09, after a verified-empty pre-submit probe |
| Parking brake | **none** — unlike production, the analysis submit does not park held, so no release step |

## The render, and the cross-check it carries

```
ANALYSIS_SUBMIT_RENDERED rows=3000
  commit=61fe978f66c00e8467f88c00d677462292dd5a1c
  macro_sha256=a101a0a1084a1e0a369e8bd637c1aa982641db26ba3fafa8c70bc5093b620f00
  manifest_sha256=fcd96eaebd4dc11f071a2c8db8849f6a4cc19b764622a796664e524b27d0fc80
```

**Three provenance anchors, each independently meaningful:**

| field | why it matters |
|---|---|
| `manifest_sha256=fcd96eae…` | the manifest whose every row was **rehash-verified against file bytes** this session |
| `macro_sha256=a101a0a1…` | **identical to the v3 macro hash recorded when the species axis was validated** on the JUNCTIONS/MONASH/CLOSEPACKING fixtures. The synced checkout is running the macro that passed both closure checks |
| `commit=61fe978f…` | the synced HEAD, matching Nikhef at render time |

**The render is the dry run.** It validated all 3000 raw receipts before writing
the submit file — which is why it took over ten minutes — and `condor_submit`
was only invoked after it returned cleanly.

**Analysis jobs burn no seeds and are re-runnable**, so the ceremony here is
lighter than production's: no ledger, no attempt axis, no parking brake. The
discipline is not lighter — the pre-submit probe was success-verified, the
cluster id comes from the submit response rather than from a queue scan, and the
three anchors above are recorded before any job finishes.

## What this campaign produces

3000 pair directories under
`/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1`, each carrying
**`hFlavourClosureSpecies`** — the 202-bin species axis — alongside the
unchanged 6-bin `hFlavourClosure`, and declaring
`analysis_schema=paul_pair_objects_primary_ground_v3`.

**This is the first v3 data in the project.** Every version-aware change made
over the last several generations — the schema-keyed object contract, the
fail-closed species mapping, the v2-pin sweep across six judging consumers —
exists so that these outputs can be validated and plotted without breaking the
v2 data that precedes them. **Nothing v3 has yet been through the plotting
layer; that remains the last untested claim.**

## FIRST v3 JOB VERIFIED — the design lands intact on production data

`per_job/MONASH/slot_001`, promoted, read back directly:

```
analysis_schema=paul_pair_objects_primary_ground_v3
hFlavourClosureSpecies=PRESENT bins=202
hFlavourClosure=PRESENT bins=6
species_ordinal_digest=646f310f78126267
```

**Every element of the ratified design is present and correct:**

| element | evidence |
|---|---|
| v3 schema tag | `…_v3`, so every version-aware consumer selects the seven-object set |
| the species axis | **202 bins**, matching the ratified ordinal table |
| **`hFlavourClosure` unchanged** | still **6 bins**, side by side — the **parallel-object** design, not a widening |
| legibility | digest **`646f310f78126267`**, the ratified table, travelling in the file |
| fail-closed mapping | **never fired** — every sector-charged PDG in real production MONASH data has an ordinal |
| closure sum rule | `FLAVOUR_CLOSURE … full_phase_space=1` for every trigger |

**And the version-aware allowlist validated it:**
`PAIR_DIRECTORY_VALIDATION errors=0 expected_files=300 found_root_files=300`.

> **This is the both-directions proof, on production data.** The same
> `ValidatePairDirectory` — the one whose `kRequiredAnalysisSchema` literal was
> deleted — **accepted v2 merged directories (six objects) in first contact, and
> now accepts a v3 directory (seven objects) here.** The exact-match-in-both-
> directions risk that the whole version-aware programme was built to retire is
> retired against real data in both directions.

Provenance chain intact in the same line: `upstream_commit=e6429b7` (raw
produced under the freeze), `upstream_executable_sha256=e54b27bb9e3f…`,
`analysis_macro_sha256=a101a0a1…`.

---

# ITEM-STOP — I broke the analysis campaign's checkout freeze

**Self-inflicted, fully diagnosed, no data lost. Recorded plainly because the
rule it breaks was one I had just spent a session enforcing.**

## What happened

The analysis submit was rendered pinning `commit=61fe978f`. **While the 3000
jobs were in flight I advanced the Nikhef checkout four times** — the rehash
record, two campaign records, and the B6 fix — pushing each per "normal flow,
the freeze is over."

**The analysis jobs verify their pinned commit at promotion, exactly as
production jobs verify theirs at startup.** Every job that finished after the
first push failed at the promotion step:

```
ERROR: analysis checkout changed after worker provenance was pinned
ERROR: retained stage after checkout-provenance failure:
       .../per_job/MONASH/slot_298.partial.1gPJss
```

`condor_q` holds them under `OnExitHold` / `HoldReasonCode 3` — a **non-zero
exit**, not a hang guard. **1045 held** at the last reading and climbing as more
jobs finish.

## The error in reasoning, exactly

**The freeze that ended was HF_RUN3_V1 *production*'s.** I generalised it to the
checkout as a whole. **It was never a property of the checkout — it is a
property of having jobs in flight that pin a commit**, and the analysis campaign
has precisely that property. Submitting 3000 analysis jobs *re-created* the
condition the freeze exists for, in the same session in which I recorded the old
one ending.

**The v27/v28 handoffs both state the freeze's reason correctly** — "jobs verify
their commit at startup" — and I still read the conclusion rather than the
reason.

## What is NOT damaged

- **The analysis work itself succeeded.** The failing jobs show
  `ONE_PASS_ANALYSIS_SUMMARY … pairs_written=300`,
  `PAIR_DIRECTORY_VALIDATION errors=0`, and `(int) 0` from both the macro and
  the validator. **Only promotion was refused.**
- **Every partial stage is retained**, by design, at
  `per_job/<TUNE>/slot_NNN.partial.<suffix>`.
- **Analysis jobs burn no seeds and are re-runnable.** Nothing is consumed by
  redoing them.
- **332 directories promoted** before the first push, and those are valid v3
  outputs — one of them is the verified `slot_001` above.

## The remedy — for the next session, not improvised now

1. **Stop pushing to Nikhef.** The checkout must hold at whatever commit the
   next render pins. **Local commits accumulate; that is the intended pattern
   and it is what the production freeze did for weeks.**
2. Decide between: **(a)** hold the checkout and release the held jobs so they
   re-run against the pinned commit, or **(b)** re-render the submit at the
   current HEAD and resubmit the unpromoted slots. **(b)** is cleaner if the
   checkout has already moved past what any in-flight job pinned — which it has.
3. **Then do not advance the checkout again until the campaign drains.**

**Commits made after this point in the session are LOCAL ONLY.** Nikhef stays at
`367de7d3` so that the state a successor inherits is stable and diagnosable.

## The rule, restated so it cannot be misread again

> **The checkout freeze is not about a campaign. It is about jobs in flight that
> pin a commit.** Production jobs verify at startup; **analysis jobs verify at
> promotion.** Any campaign of either kind re-imposes the freeze for its own
> duration. **"The freeze is over" is only ever true of a specific campaign, and
> only until the next submission.**

---

# RECOVERY BY RESTORED PIN — complete. **A NEW FREEZE IS DECLARED.**

> ## THE FREEZE IS IN FORCE
>
> **Nikhef is DETACHED at `61fe978f66c00e8467f88c00d677462292dd5a1c`** — the
> commit every job of analysis cluster `5398658` pins and verifies at promotion.
>
> **It does not move until the campaign converges.** Branch `physics-focus`
> is untouched at `367de7d3`, so the detach is reversible by construction.
> **Local commits accumulate; scratch-deploy covers anything on Nikhef needing
> newer code.** `make can-advance` now refuses while jobs are in flight.

## Why restored pin rather than re-render

Detaching to `61fe978` **restores exactly the state every in-flight job already
verifies.** A released `OnExitHold` job re-runs from scratch either way, so
re-rendering and resubmitting would have bought nothing and burned a submission.

## Single-job verification first, then the batch

**Pre-registered: one released job re-runs and promotes cleanly against the
restored checkout.**

| step | result |
|---|---|
| baseline | 299 promoted, `slot_298` **absent** |
| released **exactly one**, `5398658.298` | re-ran, **promoted** |
| after | `slot_298` **present**, count **298 → 299** |

**Only then** the batch: **2701 held → released → 2701 idle**, with HEAD
re-verified still at `61fe978f`.

**That ordering is the point.** Had the restored pin been wrong, one job would
have failed and 2700 would still have been held, diagnosable. The single-job
check cost one job's runtime and bounded the blast radius of being wrong.

## The guard, so this cannot recur by memory

`tools/checkout_advance_guard.py`, `make can-advance`. Refuses while the queue
is non-empty; refuses when the probe returns UNKNOWN, on the same fail-closed
principle as `queue_probe.py`. **Verified live in both directions** — it refused
naming "2702 job(s) in flight", and accepted the detach override echoing its
reason.

**The override is for restoring a pin, not for ignoring the guard**, and
requires `--override-reason` so the justification is recorded rather than
implied. `OVERRIDE` and `ALLOW` are distinct verdicts.

## Expected end state

**3000/3000 v3 directories, all pinned `61fe978`.** Residual failures, if any,
go through the normal unpromoted-slot flow next session. **Do not babysit.**

**Note for the successor:** all promoted directories so far are **MONASH**, because
the submit is tune-major and the breach happened partway through MONASH's block.
JUNCTIONS and CLOSEPACKING v3 outputs appear as the released jobs work through.
