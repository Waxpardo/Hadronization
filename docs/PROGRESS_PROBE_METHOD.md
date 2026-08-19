# How to measure the progress of a long, silent job — the consolidated method

**This supersedes the progress-probe material accreted in `GATE_3000.md` §4.**
That section grew by amendment across four sessions; the method is now used for
the gate, the merge and the per-tune closures, so it lives here.

Every instrument below has a **validity condition**. Three of the four failures
this project has recorded were not wrong readings — they were **readings taken
outside an instrument's validity condition, which returned a plausible number**.
Two of them returned *zero*, which reads as "stalled".

> **The governing rule: an instrument that is blind returns zero, not an error.
> Establish validity before you believe a number, especially a reassuring or an
> alarming one.**

---

## 1. THE DECISION TREE

```
Do you have the PID?
├─ NO ──▶ You have no workload-intrinsic signal.
│         Do NOT substitute a scheduler-reported one (§4, correction 0).
│         Get the PID: pgrep / ps --ppid / the chain log.
│
└─ YES ─▶ Has the pipeline ITSELF read or written these files
          within the relatime window (24 h)?
          │
          ├─ YES (merged outputs; anything the merge or its
          │       ValidatePairDirectory pass just produced)
          │   ──▶ ⛔ atime frontier is INVALID. It returns a SILENT ZERO.
          │       Use  /proc/<pid>/fd     → position (exact ordinal)
          │       and  /proc/<pid>/io rchar → bytes (fraction)
          │
          └─ NO  (raw per_job/ inputs an ordered walk is reading
                  for the first time)
              ──▶ ✅ atime frontier is VALID, with both corrections:
                  • compare against job_start, NOT mtime
                  • take the MAXIMUM INDEX, never the COUNT
```

---

## 2. THE INSTRUMENTS

| instrument | measures | valid when | how it fails |
|---|---|---|---|
| **atime frontier** (max index, vs `job_start`) | how far an ordered walk has got | files **not** read or written by the pipeline in the last 24 h | **silent ZERO** |
| **`/proc/<pid>/fd`** | the file open **right now** → exact ordinal position | process alive, PID known | — (direct observation) |
| **`/proc/<pid>/io` `rchar`** | cumulative bytes **requested** → progress fraction | always; immune to relatime **and** to page cache | **flat during CPU phases** — it is a step function, not a ramp |
| **`/proc/<pid>/io` `read_bytes`** | bytes fetched from the **block layer** → cache-vs-disk | local block storage only | **~ZERO on NFS / cache hits.** Not a progress counter |
| **scheduler CPU** (`condor_q`) | freshness of the schedd's job ad | never, for liveness under ~900 s | **false negative** (flat on a working job) |
| **process state + `%CPU`** | corroboration only | always | — |
| **CPU-time advance** (`/proc/<pid>/stat` fields 14+15, sampled twice) | **liveness, phase-independently** — ticks/s against wall clock | always; the one probe that does not care which phase the job is in | — (it answers liveness, **not** position: a spinning process also advances) |

---

## 3. TURNING A POSITION INTO A VALIDATED FRACTION

`rchar` gives a fraction only against a **validated denominator**. Do not assume
one. The procedure, and it is cheap:

1. **Get the workload's ordered unit list from the code**, not from a directory
   listing. The closure iterates `Hadronization::kPairDefinitions`
   (`ValidatePairBlockClosure.C:321`) — **contract order**.
2. Sum the bytes of every unit across every directory the job reads → the
   denominator.
3. **Cross-check**: cumulative bytes through the unit currently open in
   `/proc/<pid>/fd` should equal measured `rchar`. If it does, the read model
   ("each unit read once, in this order, negligible other I/O") is validated and
   the fraction is real.

**Worked, 2026-08-12 11:21 CEST, MONASH closure (PID `2077149`):**

| | |
|---|---|
| open unit (`fd`) | `pair_charm_trig_D0_assoc_Xicprimezero.root` |
| its **contract** rank | **67 / 300** |
| its **alphabetical** rank | 191 / 300 — *the wrong list gives the wrong answer* |
| predicted cumulative through rank 67 | **16.593 GB** |
| measured `rchar` | **16.543 GB** |
| agreement | **0.3 %** → model validated |
| denominator (all 300 units × 11 dirs) | **29.354 GB** |

The denominator independently reproduces the 29.36 GB carried since v47, which
had been asserted without this cross-check.

> **Had the alphabetical list been used, the same reading would have implied
> 37.8 % instead of 56.5 %** — a self-consistent, entirely wrong answer, with no
> symptom. Take the order from the code.

**And the step function bites in practice — 2026-08-15 23:00 CEST.** Three
concurrent closures sampled over 90 s read **0.0 MB, 0.0 MB and 3.0 MB/min**
against a sustained ~31 MB/min. On `rchar` alone that is three processes
stalling together, which points at the filesystem and is wrong. **CPU-time
advance settled it in one sample**: all three at **99.6–99.7 ticks/s**, i.e.
100 % of a core, JUNCTIONS having consumed **2,665 s of CPU in 2,658 s of wall
clock** — pegged since launch, never blocked. The filesystem answered a listing
in 5 ms.

> The row above is already in the table: *"flat during CPU phases — it is a step
> function, not a ramp."* **The failure mode was documented and still misled,
> because a 90 s window is short enough to land wholly inside one step.** When
> `rchar` reads flat, either widen the window past a step or ask CPU time
> instead — do not escalate to the filesystem on a narrow `rchar` sample alone.

---

## 4. THE CORRECTIONS, IN THE ORDER THEY WERE MEASURED

**Correction 0 — scheduler CPU is not liveness.** `condor_q` CPU stayed flat
across 550 s on a job demonstrably completing a directory every 22 s; it reads
the schedd's copy of the ad, refreshed on `STARTER_UPDATE_INTERVAL` (300 s) and
propagated slower still. Prefer a workload-intrinsic signal. Where none exists,
sample over **≥ 3× the update interval (≥ 900 s)** before flatness means
anything.

**Correction 1 — compare to `job_start`, not `mtime`.** The unfiltered form
detects *any* read, and will report **your own earlier probes** as progress.

**Correction 2 — the frontier is the MAXIMUM INDEX, never the COUNT.** Measured
2026-08-11 03:30: **934 directories carried a fresh atime while the frontier was
`slot_972`** — a 38-directory shortfall. Under `relatime` a directory whose atime
is already ≥ its mtime and under 24 h old is not re-stamped, so anything an
earlier pass touched is invisible to a count.

**Correction 3 — the atime frontier is INVALID on merged outputs, and fails as a
silent zero.** Measured with MONASH closure 7.3 h into a healthy run:
`atime > start` returned **0 of 300 files in all eleven directories**, while
`/proc/<pid>/fd` showed those exact files open and being read. **Why:** every
merged pair file is written and then read by the merge's own
`ValidatePairDirectory` pass before promotion, so its atime already equals mtime
and is minutes old; under `relatime` a later read updates nothing. The probe's
validity condition — *files not read recently* — is **violated by construction**
for anything the merge just produced.

**Correction 4 — `read_bytes` is not the replacement, and §4 prescribed it in
error.** GATE_3000 §4 named `/proc/<pid>/io` `read_bytes` as the relatime-immune
substitute. Measured 2026-08-12 11:26 on the same closure:

| PID | role | `rchar` | `read_bytes` |
|---|---|---|---|
| `2077149` | **closure** | **16.68 GB** | **16 KB** (static across 8.5 h) |
| `2077042` | merge | 13.31 GB | 7.86 GB |

`/data/alice` is **NFS4** (`data-02:/alice`, `relatime`). The closure's
`read_bytes` is a flat near-zero for the entire run — **it would have failed
exactly as the atime probe did, one correction later.** The merge's counter is
non-zero (it stages through local `/tmp`), which is very likely why the figure
quoted in correction 3 — "`read_bytes` climbing 2.9 MB in 40 s" — looked healthy:
it was read during the window in which that session records having had the merge
and closure PIDs **swapped**.

> **`rchar` (bytes requested) is the progress counter. `read_bytes` (block-layer
> fetches) answers a different question — cache vs disk — and on NFS answers it
> as zero.**

**Correction 6 — the same failure outside `/proc`: `git ls-files --others
--ignored --exclude-standard` does not descend into a wholly-ignored
directory.** Measured 2026-08-13 while sweeping for the `/Analysis/` trap. It
reports such a directory only with `--directory`, and lists nothing inside it
otherwise.

> **So the natural sweep command is blind to precisely the failure mode it would
> be reached for.** Asking "what is git ignoring that it should not be?" with
> that command returns a tidy list of build artifacts and `__pycache__` — a
> plausible, reassuring answer — while a source directory swallowed whole is
> exactly what it cannot show. It is correction 3's shape on a different tool:
> **the instrument's blind spot coincides with the thing being looked for, and
> it fails as a quiet, well-formed answer rather than an error.**

**The method: test directories DIRECTLY.** Enumerate every directory and ask
`git check-ignore -v <dir>` about each. `-v` names the rule and the line number,
so the answer is actionable rather than a bare boolean.

**The corollary, which is what makes the trap durable.** Git applies ignore
rules **only to untracked paths**. So the moment any file in the directory is
committed, the rule stops applying to it and every symptom disappears — `git
status` is clean, the tracked files behave normally, and the directory looks
entirely healthy. **The trap stays armed for the next NEW file**, which is
silently dropped by `git add`.

> This is why the guard test (`tests/test_no_source_directory_is_ignored.py`)
> checks for a **case-only collision between an ignore rule and a real
> directory** and not merely for "is anything ignored that shouldn't be". When
> the original defect was reinstated as a test, the tracked-file check **passed**
> — the files were tracked by then — and only the case-collision check fired.
> **A probe that can only see the symptom will report the armed trap as
> healthy.**

**Correction 5 — `rchar` is a step function; short flatness is not a stall.**
Measured on the same process: `rchar` advanced 16.543 → 16.682 GB as it moved
from contract unit 67 to 68, then held **perfectly flat for 123 s** with the same
11 files open, at 99.6 % CPU in state `R`. The closure reads a unit's 11 files,
then compares bin-by-bin with no I/O at all.

> **Sample `rchar` across at least one full unit period** (here ~4 min) before
> treating flatness as meaningful, and corroborate with process state and %CPU.
> This is correction 0's lesson recurring on a different instrument.

**Correction 7 — a checker can hold a stale constant and report a plausible
number.** Measured 2026-08-18 on the species-panel caption check.

`tools/check_panel_caption_collisions.py` answers one question: do data pixels
fall inside the caption's own boxes? It located those boxes from four constants,
the caption baselines 0.400, 0.356, 0.312 and 0.268. That held while every panel
put its caption in one place.

Render #6 moved four panels. The anchor ladder placed two captions at 0.346 and
two at 0.302. The checker went on measuring the boxes at the old baselines, which
those panels had vacated. It reported six strikes. Four of the six were empty
space that the spectrum happens to cross.

**The failure was hard to catch because the number was plausible.** The tool did
not crash. It did not print a zero, and it did not print nonsense. It printed six
strikes on the same six panels as the previous render, at pixel counts within a
few percent. A reader comparing the two renders would conclude that the fix had
not worked.

An eyes-on check of one relocated panel settled it. Render #6's pT Σb⁰ panel
carries its caption at 0.302 and clears the data. The tool now reads the
baselines from each panel's own generated `.C`. It takes the four `TLatex` calls
at the caption anchor that carry the caption strings. Re-run, render #6 reads 28
clean and 2 struck, and the two are the panels the render logged as
`NO_CLEAR_BASELINE`. Render #5 is the control, because every panel there shares
one caption position, and it does not move.

> **This is the third case in this project where the eyes and the mechanics
> caught different things, and the first where the eyes caught the mechanics.**
>
> | case | what the mechanics saw | what the eyes saw |
> |---|---|---|
> | E10, figure 4's η caption | nothing — the text primitive was present and correct in form | the defect. `ERROR_RECORD.md` E10 records it as the one defect of that session that looking caught |
> | E9, the twice-rounded class label | the defect, from the derive-don't-transcribe audit of the generator's source | nothing — 59.9 against 59.8 is invisible on the canvas |
> | this one | a wrong answer, stated with confidence | the defect **in the mechanics** |
>
> **A checker is an instrument, and §2's rule applies to it.** Establish validity
> before believing a number, especially a reassuring or an alarming one. This
> instrument's validity condition was never written down: it holds only while
> every panel places its caption identically. The ladder broke that condition,
> and nothing in the tool noticed.

---

## 5. POSITION IS NOT TIME

A validated position gives **no ETA** when unit costs are non-uniform, and this
project has twice escalated on exactly that error. The ordered-unit-cost rule
stands: **a prefix of an ordered workload is never an estimate.**

The closure is the sharpest available illustration. At unit 68 of 300:

| model | basis | remaining | finish |
|---|---|---|---|
| **byte-proportional** | 16.68 GB in 8.52 h = 1.96 GB/h; 12.67 GB left | **6.5 h** | ~17:55 Aug 12 |
| **per-unit-cost** | 68 units in 8.52 h = 451 s/unit; 232 units left | **29.1 h** | ~16:35 Aug 13 |

**These differ by 4.5×, from the same validated position.** The contract
front-loads the high-statistics charm-meson pairs: the first 67 units carry
16.68 GB in 737 file-opens (~22.6 MB each); the remaining 233 carry 12.67 GB in
**2563** file-opens (~4.9 MB each). Byte-rate flatters the tail; per-unit cost
punishes it. The truth depends on the fixed-vs-byte cost split, which is **not
yet measured**.

> **The resolution is measurement, not arithmetic:** sample the contract rank
> from `fd` at intervals once the job is inside the small-file regime, and read
> units/hour directly. Do not publish either bound as an ETA.

---

## 6. HOW TO WAIT — event-driven re-invocation, not polling (house method)

**Owner ruling, 2026-08-12.** Polling a multi-hour job from the session burns
the scarcest resource in the room — context — on samples that almost always say
"still running". Use two processes with different jobs:

| | **the waiter** | **the sampler** |
|---|---|---|
| job | **wake the session, once** | build a rate time-series |
| pattern | blocks until the target PID exits, then exits | appends one line per interval |
| interval | poll ~300 s internally | ~600 s |
| tracked by | the harness — its exit **re-invokes the session** | nothing; it is fire-and-forget |
| if it dies | **the wake signal is lost** — this is the one that matters | you lose resolution, nothing else |

**The waiter is the wake signal. The sampler is never the wake signal.** Keeping
that separation is the whole point: the sampler is a convenience whose loss is
survivable, so it can be cheap and unsupervised.

### Rules

1. **Record the sampler's PID and own it.** It is a local process on the
   session's own machine. **It dies with that machine, and that is acceptable** —
   by rule 2 nothing depends on it. Kill it yourself when done; do not leave
   strays.
2. **Never put the sampler on the shared node.** It would add a process to the
   very node whose contention is being measured. Sample *from* the workstation,
   over SSH, read-only against `/proc`.
3. **Bound the waiter.** Give it a hard deadline (10 h was used here) so a job
   that never finishes cannot leave it running forever.
4. **Wait on the outermost process.** Here that is the *chain* PID (closure plus
   its eleven extractions), not the closure PID — so a chain that aborts wakes
   the session just as a chain that succeeds does. **Waiting on the inner process
   would sleep through the failure case.**
5. **Have the waiter print the evidence at exit**, not just the fact of exit —
   the verdict lines and an output inventory — so the first look after
   re-invocation is already the harvest check.

> Both processes are **read-only**: `/proc` inspection and log reads. Neither
> renices, signals, or restages anything. Measuring the collision must never
> perturb it.

---

## 7. IDENTIFYING THE JOB — added 2026-08-18

Rules 1–5 above assume you know *which* process to watch. Adopting renders left
by two overlapping sessions showed that step is where it goes wrong.

### 7.1 `argv` is not identity

The renders run as `root -l -b <<ROOTCMDS`, so the macro arrives on **stdin**.
The worker's command line carries no macro name and no target:

```
/cvmfs/.../ROOT/v6-30-01-alice5-2/bin/root.exe -splash -l -b
```

Every ROOT job on the host is indistinguishable this way. `pgrep -f <macro>`
matches **nothing**, and returns exactly what it returns when no job is running.
**A search that cannot succeed is silent in the same way as a search that found
nothing.**

Identify from these instead, all read-only:

| signal | probe | answers |
|---|---|---|
| lineage | `ps -o pid,ppid,pgid` | which processes are ONE job |
| working tree | `readlink /proc/<pid>/cwd` | which deploy it renders from |
| **stdout** | `readlink /proc/<pid>/fd/1` | **which log — hence which target** |
| current input | `readlink /proc/<pid>/fd/5` | which raw file — hence progress |
| CPU accumulation | `ps -o time=` | *working*, not merely *present* |

`fd/1` is usually the decisive one: the log path names the run even when nothing
else does.

### 7.2 Wrapper and worker die separately

`bash run_paper_plots.sh` forks `root`, which forks `root.exe`. Killing the
wrapper leaves the worker running, re-parented to `init`, still holding its
compiled ACLiC library and still writing the same output paths. A relaunch that
kills only the wrapper produces **two workers racing for one output file**, the
older running pre-fix code.

> Signal the **process group** (`kill -TERM -<pgid>`), then verify the group is
> empty. Never infer that children went with the parent. Never `pkill -f` — see
> 7.1 for why the pattern would not mean what you think.

### 7.3 A liveness probe needs three states, not two

```
until ! ssh host 'kill -0 <pid>'; do sleep 90; done      # WRONG
```

`ssh` exits non-zero when the **transport** fails, not only when the remote
predicate fails. An unreachable login node therefore announces that the job
finished. This exact waiter was found already exited while its render was still
running with 24 minutes of CPU behind it.

Report three states and let only an affirmative absence end the wait:

```sh
out=$(ssh host 'if kill -0 <pid> 2>/dev/null; then echo ALIVE; else echo GONE; fi')
case "$out" in
  ALIVE) ;;                       # keep waiting
  GONE)  break ;;                 # the probe SUCCEEDED and reported absence
  *)     ;;                       # transport failure: inconclusive, keep waiting
esac
```

Measured immediately: the replacement waiter logged **five consecutive
inconclusive probes** against a healthy render and kept waiting correctly. The
two-state form would have declared that render finished five times over.

> **Absence of an answer is not an answer.** This is E8's shape one level out —
> the earlier instances conflated *process absent* with *work finished*; this one
> conflates *no reply* with *process absent*.
