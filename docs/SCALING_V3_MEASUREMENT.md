# The v3 species scaling measurement — pre-registration and harvest

**This measurement gates the merge.** Standing ruling from v30 §4: the merge does
not run until this is read, either way.

---

## 0. What happened to the first attempt, and why it is not a harvest

The v3 series (`/data/alice/ipardoza/scaling_series_v3.sh`) ran **detached on the
login node**. It did not finish.

| point | state |
|---|---|
| MONASH 10 | **complete** — `SCALE … rc=0 time_v=[45.01 34.19 2.38 481476]` |
| MONASH 25 | **complete** — `SCALE … rc=0 time_v=[135.10 116.97 4.17 548724]` |
| MONASH 50 | **DIED** — no `SCALE` line, `t.txt` **0 bytes**, `out/` holds **69 of 300** pair files |

All three recorded PIDs (`1110563`, `1110606`, `1110688`) are gone and the
`SCALING_DONE` sentinel was never written.

**The cause is documented in `docs/WORKSPACE.md`:**

> A detached process on `/data/alice` loses the autofs mount when its SSH session
> ends **if it opens new files**.

`MergeCanonicalAnalysis.C` opens **300 new files**, one per pair. The 10- and
25-input points survived only because they completed in 45 s and 135 s, inside
the session's lifetime. The 50-input point needed roughly half an hour: its last
output is stamped `18:41:40`, about seven minutes in.

**This is the point the merge decision actually turns on, and it is the one that
was lost.** The 25→50 interval is where v2's step switched on; without 50 there
is no v3 comparison at all.

**Remedy:** re-run the 50-input point **on a batch node**, whose lifetime is the
schedd's business rather than an SSH session's. `stage_MONASH_50` is a retained
partial stage and is **not touched**; the re-run writes to
`stage_MONASH_50_batch` and **reads** the retained `slots.txt` so it consumes the
byte-identical input set.

---

## 1. Normalisation, stated so the comparison is not silently wrong

From v8 §2b, and re-derived here rather than inherited:

```
cost per elementary merge = wall / (300 pair files x (N - 1) input merges)
```

`MergeCanonicalAnalysis.C:51` loops pairs; `MergeAnalysisObjects.C:322` loops
inputs. The denominator is `N-1`, **not `N`** — checked against v2's own numbers:
v2 MONASH at 50 inputs took 4498.15 s, and 4498150 / (300 x 49) = **306.0 ms**,
which is the published figure. The normalisation reproduces exactly.

### The two completed v3 points, normalised

| inputs | wall (s) | CPU/wall | per-elementary (ms) | v2 per-elementary (ms) | **v3/v2** |
|---|---|---|---|---|---|
| 10 | 45.01 | 0.813 | **16.67** | 13.55 | **1.230** |
| 25 | 135.10 | 0.897 | **18.76** | 12.72 | **1.475** |
| 50 | *pending* | | | 306.0 | |

Both completed points sit in the **normal CPU/wall regime** (0.70–0.93), not the
anomalous 0.989 v2 showed at 50 and 100. The anomaly is off at 10 and 25 exactly
as it was in v2, so the series starts from a comparable place.

---

## 2. PRE-REGISTRATION — recorded before the batch re-run returned

The brief carries two expectations. I record my own predictions against them,
including where I expect to disagree.

**Evidence available to me:** the killed run wrote 69 pair files with mtimes
spanning 407 s — a mean of **5.99 s per pair file**, steady (first-half mean
5.21 s, second-half 6.76 s; a mild drift, not a collapse). Extrapolating to 300
files gives a wall of roughly **1800 s**.

| # | prediction | basis |
|---|---|---|
| **P1** | **The cliff reproduces.** Per-elementary at 50 exceeds 25 (18.76 ms) by a factor **> 3**; point estimate **~122 ms, a 6.5x step**. | 5.99 s/pair-file / 49 = 122 ms |
| **P2** | **The v3/v2 ratio at 50 is `< 1` — I expect the brief's `1 < ratio < 10` to MISS on the low side.** Point estimate **0.40**. | 122.2 / 306.0 |
| **P3** | Wall time in **1500–2400 s**. | 300 x 5.99 s, +/- drift |
| **P4** | maxRSS in **600,000–730,000 kB**. | v3 trend +67,248 kB per step; v2 went 509,732 → 617,928 over the same interval |

**P2 is the interesting one.** The brief treats `ratio >= 10` as the escalation
threshold — the case where the 202-bin species object multiplies the anomaly.
My reading of the partial run says the opposite: v3 at 50 inputs looks
**cheaper** than v2 at 50, because v2's 306.0 ms is itself the anomalous number
and v3's step is smaller. If P2 holds, the merge-strategy escalation is **not**
triggered, but a second question opens — *why was v2's 50-input point so
expensive* — and that is a characterisation question, not a blocker.

**If P2 misses and the ratio is `>= 10`, that is an owner escalation with the
numbers, not a decision to improvise.**

---

## 2b. THE HOST IS NOT NEUTRAL — found mid-flight, and it changes the plan

Moving the 50-input point to a batch node fixed the autofs problem and
introduced a different one: **the 10- and 25-input points were measured on the
login node, and the two hosts do not merge at the same speed.**

Measured on the same macro, same manifest, same 50 slots — the killed login-node
run against the batch re-run, per pair file written:

| host | mean | median | tail |
|---|---|---|---|
| login (`lvp036login`) | **5.99 s** | 5.0 s | steady; 5.2 s → 6.8 s across halves |
| batch (`wn-pijl-007`) | **11.8 s** | 8.0 s | heavy — individual gaps of 35, 46, 23 s |

**Roughly 2x, with a much heavier tail.** A 25-versus-50 comparison across that
boundary would be measuring the hosts, not the merge — and that comparison **is**
the primary pre-registration.

**Remedy, submitted as cluster `5398815`:** re-measure the 10- and 25-input
points on a batch node as well, into `stage_MONASH_{10,25}_batch`, reading the
retained `slots.txt` files so the input sets stay byte-identical. Those points
cost about 45 s and 135 s, so internal comparability is nearly free.

**Consequences for the pre-registrations:**

- **P1 (the cliff) is now tested batch-vs-batch** — 25_batch against 50_batch.
  This is the version that decides anything, and it is unaffected by the host.
- **P2 (the v3/v2 ratio) carries an unavoidable host caveat.** v2's 306.0 ms at
  50 inputs was measured on the login node and cannot be re-measured — v2 data
  is gone. If the batch host is ~2x slower, a v3 batch number compared against a
  v2 login number is **biased upward by roughly that factor**, which pushes the
  ratio *toward* the brief's expected band and *away* from my P2 prediction of
  0.40. **The honest form of P2 is therefore a range**, and the v3 login-node
  points (10 and 25, already in hand) are what bound the host correction.

**P5, recorded now:** the batch 10- and 25-input walls will exceed their
login-node values (45.01 s, 135.10 s) by a factor **between 1.3 and 2.5**. If
they come back at parity instead, the per-file rate difference was contention
rather than a host property, and P2's caveat mostly dissolves.

### The 10/25 re-run was REMOVED, and why — my own mistake

Cluster `5398815` was scheduled onto **`wn-pijl-007`, the same node already
running the 50-input job** (`slot1_221` beside `slot1_223`). Two merges
contending for the same node's `/data/alice` I/O contaminates both — and one of
them is the measurement that gates the merge.

**Removed with `condor_rm 5398815`** about four minutes in. The effect was
already visible in the 50-input job's own file timings:

| window | files | mean | median |
|---|---|---|---|
| before co-residency | 37 | **14.7 s** | 9.0 s |
| during co-residency | 3 | **31.3 s** | 32.0 s |

Roughly **2× again**, on three files. Removing it promptly bounded the damage;
the successor should **discard those three intervals** rather than the run.

**The 10/25 re-measurement still needs doing — run it AFTER `5398767` finishes,
with nothing else of ours on the node**, and check `RemoteHost` before trusting
the numbers. The script is `/data/alice/ipardoza/scaling_1025_batch.sh` and its
submit file is beside it; both are idempotent and write to `*_batch` directories.

### The 10/25 re-run produced NO DATA, and is closed unrun

Cluster `5399189` started and aborted on its own first assertion:

```
ABORT checkout moved off the pin: 43e35be876dd5d881a931cb845ab490ab9b97509
```

**A guard firing correctly on a premise that had expired.** The script asserted
`HEAD == 61fe978f` — right while the freeze held, meaningless once the campaign
converged and the checkout legitimately advanced. It gated on the *checkout*
when what comparability needs is the *program*:

```
merging/MergeCanonicalAnalysis.C   61fe978 == 43e35be   dc09b67102d715fb…
merging/MergeAnalysisObjects.C     61fe978 == 43e35be   ec361cb174f60612…
git diff --stat 61fe978 43e35be -- AnalysisScripts/   (empty)
```

**Nothing in the merge path changed**, so the measurement would have been
comparable. The assertion was simply asking the wrong question.

> **CLOSED UNRUN, by owner ruling: "no third re-run."** The 10/25 points stand
> at their original login-node values, and the cycles go to the **100-input
> anchor** instead — the block size the merge actually uses, and worth more than
> a cleaner version of a point already in hand. The 100-anchor asserts the
> **macro sha256**, not the checkout, so it cannot fail this way.

**Note for anyone reading `stage_MONASH_10_batch/`:** it holds 33 pair files
from the run removed mid-flight last session, and `t.txt` is empty. **Not a
measurement.** The abort above happened before the merge loop, so nothing was
added to it.

### The 100-input anchor — cluster `5399458`

The real block size: `merge_root_files.sh:190-194` runs **30 block merges at 100
inputs** against 3 centrals. Submitted with

```
Requirements = (Machine != "wn-sate-072.nikhef.nl")
```

— an **explicit exclusion of the node the gate is running on**, which is the
answer to the isolation problem that the previous two attempts only flagged.
Retention unconditional, own directory, macro-sha asserted.

### The per-file rate is NOT stationary

A third observation, and it undercuts the normalisation itself. The 50-input
run's mean per-file cost, excluding the co-resident window, has climbed as the
run progresses:

| after N files | mean so far |
|---|---|
| 27 | 11.8 s |
| 41 | **14.7 s** |

`wall / (300 × (N−1))` is an **average over a process that is not stationary**,
so a single per-elementary-merge number compresses a rising curve into a point.
That is fine for comparing like with like — v2's numbers were computed the same
way — but **the cliff may be partly a within-run drift rather than a step
between input counts**, and nothing measured so far separates those. Worth
recording as an open question rather than resolving from this data.

---

## 3. HARVEST — the 50-input point, and the merge is not blocked

```
SCALE tune=MONASH inputs=50 rc=0 time_v=[1591.88 1100.46 38.76 672728] RETAINED
host=wn-pijl-007  pair_files_written=300  18:58:49 -> 19:25:22
```

`rc=0`, **300 of 300** pair files, `CANONICAL_MERGE_SUMMARY tune=MONASH slots=50
files=300`. The point that was lost is measured.

| | v2 @50 (login) | **v3 @50 (batch)** |
|---|---|---|
| wall | 4498.15 s | **1591.88 s** |
| per elementary merge | 306.0 ms | **108.29 ms** |
| CPU/wall | **0.989** (anomalous) | **0.716** (normal) |
| maxRSS | 617,928 kB | **672,728 kB** |

`1591880 ms / (300 × 49) = 108.29 ms`.

### Against the pre-registration

| # | prediction | actual | |
|---|---|---|---|
| **P1** | cliff reproduces, > 3×; point est. ~122 ms / 6.5× | **108.29 ms, 5.77×** over 25's 18.76 ms | **HIT** |
| **P2** | v3/v2 **< 1**, point est. 0.40 | **0.354** | **HIT** |
| **P3** | wall 1500–2400 s | **1591.88 s** | **HIT** |
| **P4** | maxRSS 600,000–730,000 kB | **672,728 kB** | **HIT** |

**P2 was the contested one and it holds.** The brief expected `1 < ratio < 10`;
the measured ratio is **0.354**, below the band rather than above it. **v3 at 50
inputs is roughly three times CHEAPER than v2 at 50**, despite carrying an extra
202-bin sparse.

> **NO OWNER ESCALATION IS TRIGGERED.** The escalation condition was `ratio ≥ 10`
> — the 202-bin species object multiplying the anomaly. It does not. **The merge
> strategy does not have to change.**

### The real result: v2's anomaly does not reproduce

The three constraints v8 set for any mechanism were that the excess is **pure
CPU** (CPU/wall 0.989 at 50), scales as **√N**, and is **MONASH-only**. **v3's
50-input point sits at CPU/wall 0.716 — squarely normal, and 0.273 below v2's.**
All three v3 points are now in the normal band: 0.813, 0.897, 0.716.

**So the 49× step is not a property of merging 50 MONASH inputs. It was a
property of the v2 merge**, and whatever produced it is absent from v3. The v3
cliff is 5.77×, not 24×, and it is a cost increase without the CPU signature
that defined the anomaly.

**A caveat that has to travel with P1:** this compares **25 on the login node**
against **50 on a batch node**, and the hosts differ. The 10/25 batch re-run
(§2b) is what removes it. Direction of the bias is known — the batch host is
slower — so a same-host comparison would show a **smaller** step than 5.77×,
not a larger one. **The cliff is therefore an upper bound, and P1's "> 3×" is
not yet safe against the host correction.**

### Correcting two things recorded mid-flight

1. **"P3 is already missing" was wrong.** I wrote that from an extrapolation of
   the first 27 files (11.8 s each → ~3550 s). The run finished at 1591.88 s,
   inside the predicted band. **P3 hit.**
2. **"The per-file rate is not stationary — and rising" had the sign wrong.**
   The full run averages **5.31 s/file** against **14.7 s** over the first 41.
   The early window is the slow one — cold cache and startup — and the run
   **accelerated**. The rate is indeed non-stationary, but it *falls*. Any
   projection from an early window overestimates; mine did, by 2.2×.

---

## 4. POOL SIZING — to be re-derived from v3, not inherited

The `~441 MiB/child` and `~571 MiB` merge-side figures are **superseded as
load-bearing**: v3 shows **481,476 kB ≈ 470 MiB at only ten inputs**, already
above 441 MiB, and 548,724 kB ≈ 536 MiB at 25.

The derivation is also **constraint-dependent, and the constraint should change**:
441 MiB/child was divided into a **2048 MiB login-node cap**. The gate should run
on a **batch node**, where the ceiling is `request_memory` and is chosen rather
than inherited. Re-deriving a pool size against the login cap would be answering
a question we should stop asking.

### Measured v3 RSS

| inputs | maxRSS (kB) | MiB |
|---|---|---|
| 10 | 481,476 | 470.2 |
| 25 | 548,724 | 535.9 |
| 50 | **672,728** | **657.0** |

Growth is **sub-linear in inputs** — a 5× input increase costs 1.40× RSS — so
the 100-input merge should land near 750–800 MiB, close to v2's 732,052 kB.

### What this licenses, and what it does not

**Supersedes the merge-side `~571 MiB` figure: use 657 MiB/child**, measured at
50 inputs, for **merge** pool arithmetic.

> **It does NOT re-derive the gate's `~441 MiB/child`.** That figure describes
> `ValidatePairDirectory` — a *different process* doing a *different job*. This
> series measured `MergeCanonicalAnalysis.C` only. **Sizing the gate's pool from
> a merge measurement would be the same category error as sizing it from the
> login cap.** The brief asked for all pool sizing to be re-derived from v3
> numbers; the v3 numbers in hand only cover the merge side, and the honest
> answer is that **the gate still needs its own measurement.**

**Derivation, stated so it can be checked:**

```
merge pool on a batch node = floor(request_memory_MiB / 657 MiB) - 1 for headroom
  request_memory =  4 GiB (4096) -> floor(6.23) - 1 =  5 children
  request_memory =  8 GiB (8192) -> floor(12.5) - 1 = 11 children
  request_memory = 16 GiB        -> floor(24.9) - 1 = 23 children
```

Against the old **2048 MiB login cap** the same arithmetic gives
`floor(3.11) - 1 = 2` children, down from the 4 that `441 MiB` implied.
**That halving is the practical reason to stop sizing against the login node**:
`request_memory` is free to choose and the cap is not. The 50-input job ran
comfortably under `request_memory = 4GB` with 657 MiB peak.
