# Verdicts not due yet — status, and the apparent stall that was not one — 2026-08-15 (eighteenth session)

**Suite 45/45, unchanged. Wall clock 22:50–23:00 CEST — this session opened
five minutes after the seventeenth closed.** The closures were 42 minutes into
a ~15 h run, so **no verdict could land in this window and none did.** Per the
brief: status, waiters confirmed, end. Nothing was promoted, nothing changed on
the remote.

---

## 1. No reboot, nothing to relaunch

`stbc-i3` up **2 d 23 h 43 m**, boot **2026-08-12 23:07** — the same boot as the
previous session. All six guarded processes alive by PID:

| | PID | |
|---|---|---|
| merge | 315689 | ALIVE (1 d 08 h) |
| supervisor | 316182 | ALIVE |
| EOL watcher | 2566164 | ALIVE |
| closure waiter | 2572403 | ALIVE (+ both subshells) |
| closure JUNCTIONS | 2563461 | ALIVE |
| closure CLOSEPACKING | 2563536 | ALIVE |

**The brief's relaunch contingency did not apply.**

## 2. An apparent stall, measured and withdrawn

**First reading: JUNCTIONS and CLOSEPACKING read 0.0 MB over 90 s, and the
merge's MONASH closure had dropped from 33 MB/min to 3.0 MB/min.** On `rchar`
alone that looks like three processes stalling together, which would point at
the filesystem.

**It was not a stall, and the check that settled it was CPU time, not reads.**
Over a 60 s window all three advanced **~5,970 ticks**, i.e. **99.6–99.7 ticks
per second — 100 % of one core each**, in state `R`, `wchan` 0. Cumulatively
JUNCTIONS had consumed **2,665 s of CPU in 2,658 s of wall clock**: it has been
pegged since launch and has never blocked. The filesystem answered a directory
listing in **5 ms**, and exactly **1** process on the node was in `D` state.

> **This failure mode was already documented, and it still misled me.**
> `docs/PROGRESS_PROBE_METHOD.md` §2 has said since it was written that `rchar`
> is *"flat during CPU phases — it is a step function, not a ramp."* **Knowing
> that is not the same as sampling correctly: a 90 s window is short enough to
> land wholly inside one step.** The closure's per-object comparisons — the
> 202-bin species sparse above all — are exactly such a step.
>
> **The lesson is about the window, not the instrument**, and it is recorded in
> that document rather than here: when `rchar` reads flat, widen the window past
> a step or ask CPU time instead. **Do not escalate to the filesystem on a
> narrow `rchar` sample.** `PROGRESS_PROBE_METHOD.md` §2 gains a row for
> CPU-time advance — the one probe that is phase-independent — with the explicit
> note that it answers liveness and **not** position, since a spinning process
> advances it too.

## 3. Refined ETAs — a modest slip

Sustained rates, measured over the run so far rather than over an early window:

| | read so far | sustained | ETA |
|---|---|---|---|
| JUNCTIONS | 1.45 GB | 31 MB/min | **~14:20 Aug 16** |
| CLOSEPACKING | 1.46 GB | 31 MB/min | **~14:10 Aug 16** |
| MONASH (merge's own pass) | 2.15 GB | 33 MB/min | **~13:20 Aug 16** |

The seventeenth session's 12:45/13:15 came from a 33-minute early window; the
sustained figure is slightly lower under three-way contention. **Both estimates
assume the ~29.35 GB workload measured on MONASH**, so they carry that tune's
file sizes, not JUNCTIONS' and CLOSEPACKING's.

## 4. Both waiters confirmed armed and correct

**Closure waiter** (2572403, plus subshells 2572406/2572407):

- watches **2563461** and **2563536** — each PID's `/proc/cmdline` re-read this
  session and confirmed to carry `complete_root_HF_RUN3_V1_JUNCTIONS` and
  `…_CLOSEPACKING` respectively, so it is watching the tunes it names;
- both hardcoded log paths **exist** (492 bytes each — the environment banner,
  no summary line yet, as expected mid-run).

**EOL watcher** (2566164) — every trigger condition still correctly *disarmed*:

| check | required now | observed |
|---|---|---|
| newest merge log resolves to | the live one | `merge_v6.log` |
| `CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=CLOSEPACKING` | absent | **0 files** |
| any tune's closure pass in the merge | absent | **0** |
| supervisor identifiable at 316182 | yes | **YES** |
| supervisor restarts | 0 | **0** |

**The merge is still inside its MONASH closure** — 18 `PROMOTED_MERGE` lines in
`merge_v6.log` and no closure pass line yet.

## 5. Nothing was done that the brief gates

Task 1 (verdicts) has no input. Task 2 (supervisor end-of-life) needs the merge
to complete. **Task 3 (the figure set) is gated on FINAL and was not started** —
not even preparation, because the gate is the point. No pinfile removal, no
checkout advance, no disk cleanup, no `Paper/**`. The stale JUNCTIONS partial
untouched. The b-baryon dilution hypothesis remains recorded, not measured.

`docs/THREE_TUNE_CENTRAL_TABLE.md` is unchanged and still ⛔ PROVISIONAL.

## 6. For the next session

**Open after ~14:20 CEST 2026-08-16.** Then, in order:

1. `closure_runs/verdict_line_{JUNCTIONS,CLOSEPACKING}.txt` and
   `closure_waiter.log` carry the outcome. Run
   `extraction/pipeline/harvest_tune.py <TUNE> --stage closure --closure-log <log>`
   — do not eyeball the counts.
2. **If a closure produced no summary line**, the waiter says so explicitly:
   that means killed or crashed, not failed, and the two are not the same
   finding. Relaunch from the invocation in
   `THREE_TUNE_PROVISIONAL_SESSION_20260815.md` §2.
3. **Use CPU-time advance, not `rchar`, to judge a closure's liveness** (§2).
