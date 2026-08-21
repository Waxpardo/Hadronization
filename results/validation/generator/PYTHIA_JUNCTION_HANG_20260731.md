# PYTHIA junction-splitting infinite loop — Gate-B pilot v8

**Date:** 2026-07-31
**Campaign:** `HF_GATEB_primaryGround_pilot_v8` (ordinal 26, cluster `5208884`)
**Producer commit:** `68a43517f750db26f9f8b6107841bc5f2c0d99f0`
**PYTHIA:** 8.315, CVMFS `alice/el9-x86_64/Packages/pythia/v8315-alice1-23`
**Status:** BLOCKER — Gate-B pilot cannot be evaluated; 300 M campaign cannot proceed

---

## 1. Summary

Four of the nine Gate-B pilot jobs entered an **unbounded rejection loop inside
PYTHIA** and will never terminate. They are not slow — they are wedged. Each has
consumed 8.5 h of CPU at ~97 % efficiency while writing **zero** bytes of output.

The loop is reached only under the junction tune settings. All three MONASH jobs
completed normally; four of the six JUNCTIONS/CLOSEPACKING jobs hung.

This is a **liveness** failure. Every guardrail in the pipeline validates output
*correctness*; none validates that a job is still making progress. A hung job
never exits, so `on_exit_hold` never fires and the job is invisible to the
existing failure machinery.

## 2. Evidence

### 2.1 Jobs are alive and burning CPU, not blocked on I/O

At 11:45 CEST (8 h 40 m after execute):

| Proc | Tune | pTHat | `RemoteUserCpu` | CPU/wall | Proc state |
|---|---|---|---|---|---|
| 3 | JUNCTIONS | 1.0 | 30649 s | 0.97 | `R (running)`, 1 thread |
| 4 | JUNCTIONS | 0.5 | 30644 s | 0.97 | `R (running)`, 1 thread |
| 7 | CLOSEPACKING | 0.5 | 30351 s | 0.97 | `R (running)`, 1 thread |
| 8 | CLOSEPACKING | 2.0 | 30355 s | 0.97 | `R (running)`, 1 thread |

`/proc/<pid>/wchan` is `0` and state is `R` — the process is on-CPU, not
sleeping in a syscall. This rules out a hung filesystem or a dead worker node.

### 2.2 No output since 03:06–04:04

The producer writes its ROOT file **directly** to the shared partial path
(confirmed: fd 3 of the producer process points at
`partial/<TUNE>/hf_<TUNE>_job<NNN>_attempt000_<cluster>_<proc>.partial.root`).
Partial-file mtimes have not advanced in 7.5–8.5 h:

```
03:06    4713832  partial/CLOSEPACKING/hf_CLOSEPACKING_job001_attempt000_5208884_7.partial.root
03:35  433072394  partial/JUNCTIONS/hf_JUNCTIONS_job000_attempt000_5208884_3.partial.root
03:37  491851136  partial/JUNCTIONS/hf_JUNCTIONS_job001_attempt000_5208884_4.partial.root
04:04  493190373  partial/CLOSEPACKING/hf_CLOSEPACKING_job002_attempt000_5208884_8.partial.root
```

Condor image-size updates also stopped (last at 06:04–06:16); resident set size
is flat.

### 2.3 Stack traces — identical loop in all four

Sampled with `eu-stack` via `condor_ssh_to_job`, three samples 5 s apart on
proc 7 and one sample each on procs 3, 4, 8. Every sample lands in the same
two frames:

```
#0  Pythia8::Rndm::flat()                     [or pow / __math_invalid]
#1  Pythia8::StringZ::zLund(double, double, double, double, double,
                            int, bool, bool, bool, bool)
#2  Pythia8::JunctionSplitting::splitJunGluons(Event&, vector<vector<int>>&,
                                               vector<vector<int>>&)
#3  Pythia8::JunctionSplitting::checkColours(Event&)
#4  Pythia8::PartonLevel::next(Event&, Event&)        [proc 4: via
                                                       BeamRemnants::addNew]
#5  Pythia8::Pythia::next(int)
#6  main
```

`StringZ::zLund` is sampled by accept–reject. `splitJunGluons` calls it inside
a `do { ... } while (...)` that retries until the sampled `z` falls in an
allowed window. When the junction-leg kinematics are degenerate the window is
empty and the loop cannot terminate.

The appearance of `__math_invalid` beneath `pow` in one sample shows `pow` is
being called with a domain-invalid argument and returning NaN. A NaN `z` fails
every comparison, so the acceptance test can never succeed — the loop is
provably non-terminating once that state is reached, not merely slow.

`JunctionSplitting` has a retry cap `NTRYJNREST` for the *junction rest frame*
iteration, but the gluon-splitting `z` sampling in `splitJunGluons` is not
covered by it.

### 2.4 The trigger is tune configuration, not the node

All nine jobs ran on the same worker (`wn-lot-002.nikhef.nl`), including all
five that completed — so the node is not implicated.

Non-default settings, from the PYTHIA changed-settings dumps:

| Setting | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| `ColourReconnection:mode` | 0 (default) | **1** | **1** |
| `ColourReconnection:allowDoubleJunRem` | on (default) | **off** | **off** |
| `BeamRemnants:remnantMode` | 0 (default) | **1** | **1** |

MONASH sets none of these and hung 0/3. The two tunes that set all three hung
4/6.

`allowDoubleJunRem = off` is the most directly implicated: with it disabled,
PYTHIA cannot dissolve a connected double-junction system by the cheap removal
path and must instead separate the junction chains by splitting gluons — which
is precisely `splitJunGluons`, the looping function. Note this is a deliberate
physics setting from the QCD-CR tune, **not** a configuration error.

## 3. Rate estimate

Events completed before each hang, estimated from partial size against the
per-event byte rate of the completed job at the same tune and pTHat (±5 %
cross-tune scaling). ROOT buffers in memory, so partial size **lags** true
event count — these are lower bounds on events, hence an **upper bound** on the
hang rate.

| Proc | Tune | pTHat | Events before hang |
|---|---|---|---|
| 3 | JUNCTIONS | 1.0 | ~510 k |
| 4 | JUNCTIONS | 0.5 | ~590 k |
| 7 | CLOSEPACKING | 0.5 | ~5.7 k |
| 8 | CLOSEPACKING | 2.0 | ~520 k |
| 5 | JUNCTIONS | 2.0 | 1 M (completed) |
| 6 | CLOSEPACKING | 1.0 | 1 M (completed) |

Total junction-tune exposure ≈ **3.63 M events, 4 hangs → ≈ 1.1 hangs per
million events.**

Consistency check: P(a 1 M-event job survives) = exp(−1.1) ≈ 33 %. Observed
2/6 = 33 %.

MONASH: 3 M events, 0 hangs — rate below ~3 × 10⁻⁷/event, consistent with the
junction path being unreachable in that tune.

**Implication for the 300 M campaign:** with ~200 M events in junction tunes,
expect **~220 hangs**. At 1 M events/job, roughly two-thirds of all
junction-tune jobs would wedge. The campaign cannot run without a fix.

## 4. Consequences

1. **Gate-B pilot v8 cannot be evaluated.** `evaluate_pthat_sensitivity.py`
   requires all 9 points (the statistical contract is frozen around 9 degrees
   of freedom, t₉ crit 5.797, Bonferroni 192). Only 5 exist, and the 4 missing
   are exactly the junction-tune points the tune comparison depends on. The
   **pTHat 1.0 vs 2.0 decision remains blocked.**
2. **The 300 M campaign is blocked**, harder than by storage or pTHat.
3. The 4 seeds (270010001, 270011001, 270021001, 270022001) are **burned** —
   events were generated with them. They must stay in the ledger regardless of
   whether the jobs are voided.
4. ~34 CPU-hours consumed with no usable output, and 4 slots held indefinitely.

## 5. Recommended response

**Immediate:** remove the wedged jobs — they will not terminate on their own and
are holding slots. Requires operator authorisation:

```bash
ssh -o BatchMode=yes -o RemoteCommand=none -o RequestTTY=no stbc 'condor_rm 5208884.3 5208884.4 5208884.7 5208884.8'
```

### 5.1 Upstream status — no fix exists

Checked against the PYTHIA update history through 8.317 (20 Jan 2026):

- The entry *"Bug fix in the QCD Colour-Reconnection model
  (`ColourReconnection:mode = 1`) to prevent infinite recursions when handling
  junction-junction connections"* is under **8.313**, not 8.315. It is therefore
  **already in this build**, and it addresses infinite *recursion* in
  `ColourReconnection`, not the accept–reject loop in `zLund`. Different bug.
- Neither 8.316 nor 8.317 contains any fix to `splitJunGluons` or `zLund`.
- CVMFS carries nothing newer than 8.315 in any case.

**Conclusion: upgrading does not fix the hang.** The route that would have been
unbiased by construction — the event completes and is kept — is closed.

### 5.2 Mechanism — why the loop cannot terminate

`StringZ::zLund` samples z by accept–reject with **no iteration cap**:

```cpp
do {
  z = rndmPtr->flat();
  ...
  if (z > 0 && z < 1) {
    double fExp = b * (1./zMax - 1./z) + c * log(zMax/z);
    if (!aIsZero) fExp += a * log( (1.-z) / (1.-zMax) );
    fVal = exp( max( -EXPMAX, min( EXPMAX, fExp) ) );
  } else fVal = 0.;
} while (fVal < rndmPtr->flat() * fPrel);
```

Termination requires `fVal >= flat() * fPrel`. For the degenerate junction-leg
kinematics that `splitJunGluons` hands in, `fExp` saturates at `-EXPMAX` for
essentially all z, so `fVal ≈ exp(-EXPMAX) ≈ 0` and the acceptance probability
collapses to ~0. The loop is not literally infinite — it is unbounded in
practice, which is worse, because it never trips any error path.

The caller's own retry loop in `splitJunGluons` is likewise uncapped:

```cpp
do {
  double zTemp = zSel.zFrag( idQ, 0, m2Temp);
  xPos = 1. - zTemp;
  xNeg = m2Temp / (zTemp * m2Reg);
} while (xNeg > 1.);
```

(Source read from the `alisw/pythia8` mirror at `master`; structure matches the
8.315 stack traces.)

**Consequence for the fix: there is no correct event waiting at the end of the
loop.** PYTHIA cannot generate these events. No fix can include them, so
"unbiased" can only mean *lose as few as possible, and make the loss exactly
countable* — not *lose none*.

### 5.3 Recommended fix — bounded retry into PYTHIA's own abort channel

Patch PYTHIA from source: add an iteration cap to the `zLund` accept–reject
loop; on exhaustion return a sentinel (`z <= 0`, physically impossible) and have
`splitJunGluons` return `false`. That propagates to
`JunctionSplitting::checkColours` → `PartonLevel::next` → `Pythia::next()`
returning `false`, which is PYTHIA's **existing, documented** "event could not be
generated" path. The event is aborted before any output is written and is
counted automatically by `pythia.stat()`.

Why this over the SIGALRM watchdog previously suggested here — the watchdog is
**strictly worse** and is withdrawn:

| | bounded retry | SIGALRM watchdog |
|---|---|---|
| Trigger | iteration count — deterministic given seed | wall-clock — **non-deterministic** |
| Reproducibility | preserved | destroyed; same seed ≠ same sample |
| False positives | none — fires only on a collapsed loop | fires on merely-slow-but-valid events, biasing against exactly the dense-junction topologies under study |
| Generator state | unwinds cleanly | `siglongjmp` leaves PYTHIA state undefined, allocations leaked |
| Counting | exact, via `pythia.stat()` | manual counter |

Determinism is the decisive argument: the entire provenance apparatus assumes
seed → sample is reproducible. A wall-clock trigger breaks that on a loaded
batch node.

Requirements on the patched build:

- Record base version **and patch hash** in provenance; the CVMFS pin is left
  behind, so `PYTHIA8` alone no longer identifies the generator.
- Report the abort rate per tune. At ~1.1 × 10⁻⁶ the residual bias sits orders
  of magnitude below every quoted precision target (±5 % / ±10 % / ±15 % /
  ±20 %) and is defensible in print — but it must be stated, not silent. If the
  rate exceeds ~10⁻⁴ this argument fails and the approach must be revisited.
- Report the bug upstream with the reproducer; this is a genuine PYTHIA defect.

### 5.4 Version choice is now live — and 8.316 fixes a close-packing bug

Patching means building from source, so the CVMFS pin is abandoned regardless.
That makes the base version a live choice, and 8.316 contains:

> "Fix trial hadron generation in `StringFragmentation::kinematicsHadronTmp`
> used in the **closepacking** and thermal string breaking frameworks. Previous
> version only generated trial hadrons from string endpoints, which has now been
> fixed to generate trial hadrons given the present state of the fragmenting
> string."

CLOSEPACKING is one of the three tunes under comparison. On 8.315 it runs with
**known-buggy trial-hadron generation that upstream has since fixed.** This is a
physics-correctness issue independent of the hang and is arguably more serious
than the hang itself.

8.316 also adds `StringFragmentation:eJunctionCutoff` / `mJunctionCutoff` to
modify junction-leg fragmentation stopping conditions, which may bear on the
degenerate kinematics feeding the loop.

Cost of moving to 8.316/8.317: `StringFragmentation:stopMass` default changes
1.0 → 0.8, so **all three tunes must be revalidated and the N_ch calibration
redone**, and all existing pilot output is invalidated. That is real work, but
far cheaper now than after 300 M events.

### 5.5 Liveness guardrail — required regardless

Add `periodic_hold` on stalled progress to the submit template. No job should be
able to burn a slot indefinitely without being surfaced. The absence of any
wall-time or progress check is what let this run 8.5 h unnoticed; `on_exit_hold`
cannot catch a job that never exits.

## 6. Reproduction

```bash
# job state — CPU climbing, output frozen
ssh -o BatchMode=yes -o RemoteCommand=none -o RequestTTY=no stbc \
  'condor_q 5208884 -af:h ProcId JobStatus RemoteUserCpu RemoteHost'

# stack trace of a wedged job
ssh -o BatchMode=yes -o RemoteCommand=none -o RequestTTY=no stbc \
  "condor_ssh_to_job 5208884.7 'eu-stack -p 178'"
```
