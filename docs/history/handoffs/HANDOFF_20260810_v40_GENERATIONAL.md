# GENERATIONAL HANDOFF v40 — written for a successor who has read nothing but this repository

**Supersedes `HANDOFF_20260809_v21_GENERATIONAL.md` as the entry point.** Read
this first, then v21 only if you need pre-v3 archaeology. Handoffs v22–v39 are
the intervening detail; you should not need them to act.

---

## 0. STATE, AS OF 2026-08-10 01:36 CEST

| | |
|---|---|
| **Local HEAD** | **`39df2b5`** on `physics-focus`, tree clean |
| **Nikhef HEAD** | **`43e35be`** on `physics-focus`, **attached** (not detached) |
| **Heads match?** | **No.** Local is ahead by this generation's commits |
| **Why Nikhef is frozen** | **The gate, cluster `5399423`, is in flight.** Guard and hook refuse; that is correct |
| **Gate progress** | frontier **MONASH slot_660 / 3000** at 01:36:15, **22.41 s/dir** pooled, **ETA 2026-08-10 ~16:10** |
| **Gate verdict** | **NOT YET — sentinel absent.** Nothing to record |
| **Live PIDs / jobs** | **Exactly one: condor cluster `5399423.0`** on `wn-sate-072.nikhef.nl`. Nothing else. No stray detached processes on the login node |
| **Seed ledger** | **3557/3557 recorded** (`docs/campaigns/HF_RUN3_V1_RECORD.md:753`). **No ledger file exists in this checkout** — the live ledgers are under `/data/alice/ipardoza/Hadronization-full-production/campaigns/*/seed_ledger.jsonl`, a *different* checkout on the same host. **Analysis jobs burn no seeds; the merge burns none.** |
| Suite | **29 / 29** |

**Scratch areas on Nikhef, all retained:** `merge_runs` 4.3 G, `archive` 1.1 G
(the 34 breach partials), `f3_runs` 63 M, `gate_runs` 244 K, `f4_runs` 224 K,
`m7_runs` 840 K.

> **THE MERGE WAS DELIBERATELY NOT LAUNCHED THIS SESSION**, by instruction, so
> that it launches with full context behind it rather than at the end of a
> context window. **It is your first substantive act.** Everything it needs is
> §2.1.

---

## 1. WHAT THIS PROJECT IS, IN ONE SCREEN

A PYTHIA-based study of heavy-flavour hadronisation: whether a heavy baryon's
flavour-balancing partner is itself a baryon, compared across three tunes
(MONASH, JUNCTIONS, CLOSEPACKING) that differ in colour reconnection. A referee
review came back with gaps; closing them is the work.

**The pipeline, in order:**

```
producer (PYTHIA 8.317, pinned)  ->  raw/    3000 files, 300 M events, 3 tunes
one-pass analysis per raw file   ->  per_job/  3000 directories x 300 pair files
the GATE (validate_analysis_outputs.py)  <- YOU ARE HERE, ~16:10 today
merge_root_files.sh              ->  3 centrals (1000 inputs) + 30 blocks (100)
closure at scale                 ->  2100 content / 1500 invariant comparisons
extraction                       ->  species decomposition + block SEMs  <- the paper's number
```

**The campaign, HF_RUN3_V1, is complete and promoted: 3000/3000.** Nothing
upstream of the gate needs re-running.

---

## 2. YOUR FIRST SESSION, AS AN ORDERED QUEUE

### 2.1 Verify state, then LAUNCH THE MERGE

**Verify first** (all read-only):

```bash
ssh -o BatchMode=yes -o RemoteCommand=none -o RequestTTY=no stbc
cd /data/alice/ipardoza/Hadronization && git rev-parse HEAD    # expect 43e35be
cat /data/alice/ipardoza/gate_runs/GATE_3000_DONE              # expect rc=0
python3 tools/queue_probe.py                                    # expect QUEUE_EMPTY
make can-advance                                                # expect ALLOWED
df -h /data/alice                                               # expect >= ~300 GB free
```

**The gate's pre-registered verdict** (`docs/GATE_3000.md` §3):
**`status=PASS directories=3000 missing=0`**, wall ~19.3 h.
**G1 (38–48 s/dir) and G2 (32–40 h) will read as MISSES LOW** — that is expected
and already recorded; §3b predicted it from n=25 and the frontier confirms
22.4 s/dir. **Any failure ⇒ item-STOP: enumerate the failing directories, launch
nothing.**

**On PASS, launch.** `docs/MERGE_V3_PREREGISTRATION.md` is the full pre-flight;
the essentials:

| | |
|---|---|
| invocation | `merge_root_files.sh FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT ANALYZED_DATA_BASE [TAG]` |
| production root | `/data/alice/ipardoza/hadronization_production/HF_RUN3_V1` — **the CAMPAIGN dir, not its parent** (this cost a run) |
| analysis root | `/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1` |
| output base | `/data/alice/ipardoza/hadronization_merged`, tag `HF_RUN3_V1` — **not** the checkout's `AnalyzedData/` |
| shape | 33 `merge_one()` calls: **3 centrals @1000 inputs, 30 blocks @100** |
| disk | 84–108 GB needed; 1078 GB free at last check |

**Pre-registrations to record hit/miss against:**

- **first block `PROMOTED_MERGE` wall: 2643 s ± 30 %** (the anchor's measured
  100-input value). **One bounded check, then walk away.**
- centrals **~7.3 h** each (linear from 89.0 ms/elementary — an extrapolation,
  say so);
- **total 65–77 h** against the **96 h** `MaxJobRetirementTime`;
- per-process ceiling **4.32× headroom**;
- merge-side child RSS **~836 MB** (the anchor's measured value — this
  supersedes 657 MiB for sizing, same program).

**Resume protocol — read from the script, do not improvise:** *re-run the same
command.* Completed directories are skipped by **validation, not a marker**
(`VALIDATED_EXISTING_MERGE`); a directory that exists but fails validation
returns 4 and **refuses to overwrite**; `set -euo pipefail` aborts the run on any
non-zero return. **Every resume re-pays the internal gate (21–33 h)** because
`merge_root_files.sh:80-83` runs it unconditionally. Abandoned `.partial.` stages
accumulate in `hadronization_merged/` — **not** in the gate's scan root, so they
do not block anything.

**Watching it:** **counts only.** Promoted-directory counts are reportable facts.
**No projections** — see the ordered-unit-cost rule in §4.

### 2.2 Beauty M7 — the recorded authorization

`docs/M7_UNRESOLVED_SYSTEMATIC.md` is the **charm** table. Its cuts select
`heavyQc != 0` (`Validation/MeasureUnresolvedSystematic.C:55`), so **the beauty
sector — where the paper's beauty-baryon story lives — has no equivalent
measurement.** I did not notice until writing the limits section.

**Authorized shape:** parametrise the macro by sector (scratch copy, not the
frozen checkout), deploy scratch-side, drive it with the **same ten-block
driver** (`m7_runs/m7_block.sh`, one job per canonical block so the job boundary
and the n=10 SEM boundary coincide), **exact integer counts** with the production
cross-check, and a **structure-only pre-registration** — say what you expect the
*shape* to be, never the values.

Charm sizing for reference: **3.32 s/file (n=1)**, 300 files/block, ~17 min/job,
~2.8 h total.

### 2.3 The second-branch number, with its decision rule

The experiment-comparable grouping chains each species through its **dominant**
decay channel only, so a 60/40 species is assigned **whole** to its 60 %
descendant. `AnalysisScripts/decay_parent_map_v1.json` carries the branching
ratios, so this is a **reader change, not a new measurement**.

**Compute: what fraction of the total weight sits in species whose dominant
branch is below ~80 % (i.e. with a substantial second branch)?**

| result | action |
|---|---|
| **≲ 1 %** | **quote it and keep dominant-only.** Record the number beside the convention |
| **more** | produce the **distribution**, and put the **BR-split option to the owner** — do not switch conventions unilaterally |

---

## 3. THE PAPER PACK — where everything lives

| item | file | state |
|---|---|---|
| **M7 systematic** | `docs/M7_UNRESOLVED_SYSTEMATIC.md` | **complete, charm only** (see 2.2) |
| **F3 virtual-trigger closure** | `docs/F3_VIRTUAL_TRIGGER_CLOSURE.md` | **complete**, §7 table + §8 decomposition + limits |
| **F4 decay-parent map** | `AnalysisScripts/decay_parent_map_v1.json` (+ `tools/f4_probe.cc`, `tools/build_decay_parent_map.py`) | **complete**, hashed `e343fd88…` |
| **Both conventions, side by side** | `docs/EXTRACTION_CONVENTIONS.md` | **complete**, MONASH-only, no SEMs |
| **M2 addendum** | `docs/MODEL_TEX_REWRITE_PACK.md` §§8–12, working in `docs/M2_PROBQQ1TOQQ0JOIN.md` | **complete**, paper untouched |
| **Boundary / translation tables, 2c rewrite pack** | `docs/MODEL_TEX_REWRITE_PACK.md` §§1–7 | pre-existing, unchanged |
| **Scaling verdict** | `docs/SCALING_V3_MEASUREMENT.md` | complete; merge unblocked |
| **Gate pre-registration** | `docs/GATE_3000.md` | verdict pending |
| **Merge pre-flight** | `docs/MERGE_V3_PREREGISTRATION.md` | standing |
| **Closure counts** | `docs/CLOSURE_V3_PREREGISTRATION.md` | pre-registered, not yet run |
| **Validation/ inventory** | `docs/VALIDATION_INVENTORY.md` | **six macros never run**, three on open blockers |

### The remaining physics queue, after the merge

1. **Closure at scale.** **2100 content / 1500 invariant** — these are the **v3**
   numbers. **The table INVERTS from v2's 1800/600.** A v3 run reporting
   1800/600 has resolved against the v2 schema and has **skipped**
   `hFlavourClosureSpecies` and the three species provenance strings. **Check the
   counts before believing the verdict.** Derivation in
   `docs/CLOSURE_V3_PREREGISTRATION.md`.
2. **Blocks → SEMs on the species decomposition.** Ten blocks per tune is the
   n=10 the reader's `--blocks` path needs; it **refuses** today rather than
   fabricating a SEM from one directory. **Both conventions, three tunes.** This
   is the resubmission's central number.

---

## 4. RULINGS AND CONVENTIONS THAT POSTDATE v21

Each is one line plus where it lives. **These are binding.**

| ruling | where |
|---|---|
| **Dual-convention framing, with a standing default: quote the diquark-structure grouping, present the experiment-comparable one alongside, always produce both.** The excluded-fraction problem is severe structurally and largely dissolves experiment-comparably; they answer different questions | `docs/EXTRACTION_CONVENTIONS.md` |
| **M7 is filed as a by-product table** — the review's "no systematics exist" answered with a number and an uncertainty | `docs/M7_UNRESOLVED_SYSTEMATIC.md` |
| **Frontier probe: `atime > job_start`, never `atime > mtime`.** The unfiltered form detects *any* read and will report your own earlier reads as progress | `docs/GATE_3000.md` §4 |
| **Silent tools get a workload-intrinsic progress probe.** Scheduler-reported CPU (`condor_q`) measures ad freshness, not liveness — it returned a false negative across 550 s on a healthy job | `docs/GATE_3000.md` §4 |
| **Invocation manifests:** scratch invocations derive env/args from recorded metadata where it exists, and commit the manifest beside their outputs | `f3_runs/f3_step2.log`, `m7_runs/*/m7_block_*.log` |
| **Prefix-bias rule:** for `merge_one()`-shaped work, unit costs are **ordered, not random** — a prefix is a biased sample by construction and the bias is systematically pessimistic. **Only the final `SCALE`/`PROMOTED_MERGE` line counts.** Progress is reportable, never projectable | `docs/MERGE_V3_PREREGISTRATION.md` §5 |
| **Its positive twin:** *direct measurement holds where extrapolation failed.* The gate's frontier ETA held across five independent readings (22.14/22.56/22.53/22.23/22.41 s/dir) because it measures position rather than extrapolating a prefix | this file, §0 |
| **Escalation urgency matches decision urgency.** A blocking conclusion issues from a settled number unless a deadline forces otherwise; partial-data flags carry an expiry stamp | `docs/GATE_3000.md` §5d |
| **Assertions pin the program (macro sha256), never the environment (checkout HEAD).** Environment assertions are proxies and proxies expire | `docs/GATE_3000.md` §5e |
| **Sizing pre-registrations quote their `n`; bands revise on record at n ≥ 10**, beside the original, never overwriting it | `docs/GATE_3000.md` §5c |
| **Safety mechanisms live outside the object they guard** — `make can-advance` was version-controlled inside the tree whose version it controlled, so restoring a pin deleted it | `docs/WORKSPACE.md` |
| **Retained partial stages are untouchable**; the 34 breach partials were **moved, never deleted**, with a committed manifest | `docs/campaigns/HF_RUN3_V1_PARTIALS_ARCHIVE.md` |

**The checkout invariant, unchanged and mechanised twice over:** *jobs in flight
that pin a commit ⇒ the checkout does not move.* Enforced by `make can-advance`
**and** by a `reference-transaction` git hook on the Nikhef clone (survives
checkout moves; `condor_q` is absent on the **login** node so the probe returns
UNKNOWN there and refuses — **move the checkout from `stbc`**).

---

## 5. WHAT BOTH SIDES GOT WRONG THIS GENERATION, AND HOW IT WAS CAUGHT

**This section is the point.** The working relationship is mutual correction with
evidence; it transfers only if the record shows it running in both directions.
None of these were caught by authority. All were caught by measurement.

### The owner corrected me

- **The merge escalation, twice, and both wrong.** From partial scaling data I
  concluded the merge was 2.1× over the site ceiling, "corrected" to 1.6×, and
  told the owner it must not launch. The finished measurement put it at
  **65–77 h against 96 h — comfortably inside**. Cause: the workload's per-file
  costs are **ordered**, so every prefix over-estimates monotonically. Both
  claims are **left standing in the record** with the withdrawal beside them,
  because the error is the lesson. **The conditional GO meant the wrong
  conclusion never touched anything** — defense in depth absorbed it by design.
- **Edit D's rationale.** I argued a virtual B* trigger's decay daughter would
  contaminate its own compensation sum, and built a descendant walk. The owner
  ruled that decays are **off** for every heavy hadron in this record. **Verified
  against the data before acting:** of 11,440 events containing B*/Σ_b*, **zero**
  had `isFinal==0`, **zero** had a daughter link. The walk guarded a hazard that
  cannot occur here; removing it took the diff from five edits to three.

### I corrected the owner

- **"Size the gate's pool at P = 4–8"** — a category error whose refutation was
  already in the record: `RELEASE_BLOCKERS.md` **B10 calls it "the serial
  checksum gate"** in its own heading. The tool has no pool and cannot acquire
  one without breaking the single-report contract.
- **"The 441 MiB figure is superseded"** — a cross-attribution. The gate's
  `ValidatePairDirectory` measures **442.3 MiB ± 0.9 %, confirmed**; what was
  superseded was the *merge-side* figure. Different programs.
- **B6's "30×"** — I had compared a per-tune figure against a total. The owner's
  correction to **10×** was right and my "3.3 %" was wrong; **the original
  brief's "10 % dataset" had been right all along.**

### I caught myself

- **M7 is charm-only.** The macro cuts on `heavyQc != 0`; the beauty sector has
  no equivalent. **I found it while writing the limits section, not while
  designing the run** — after presenting the table as "the paper's largest
  missing systematic".
- **The atime probe I published in v35 was wrong.** It measured *any* read, not
  the gate's. It was right there by luck and a contradiction exposed it.

### The recurring failure mode, named

**Six invocation failures across four sessions** — a wrong `--production-root`,
an expired pin assertion, ROOT's file-named entry point, a success check that
trusted `rc` alone, a double-escaped newline, and missing provenance env vars.
**Every one was caught in seconds by a fail-closed check; none reached a
number.** The pattern is *design right, invocation wrong.*

> **Countermeasure, and it is the one thing I would most want you to inherit:
> treat every new invocation as guilty until a positive check passes** — not
> until it fails to error. `rc=0` is not evidence: ROOT returns 0 when it cannot
> find a macro's entry point. Check for the expected *output*, the expected
> *file count*, the expected *summary line*.

---

## 6. COLD-READ SELF-REVIEW OF THIS DOCUMENT

I read this back as if I had never seen the project. What I would still have had
to ask, now fixed above: where the merge output goes (§2.1), that
`--production-root` is the campaign directory and not its parent (§2.1 — it cost
a run), that the closure table **inverts** between v2 and v3 (§3), that
`condor_q` is absent on the login node (§4), and where the seed ledger actually
lives (§0 — not in this checkout).

**What I could not fix, and you should know:**

1. **I never verified the gate's verdict.** The sentinel was absent at my last
   read and the ETA is ~14 h out. **Everything in §2.1 downstream of PASS is
   conditional on a result I did not see.**
2. **M7's beauty half does not exist.** §2.2 authorizes it; the table in the pack
   is half the question until it does.
3. **The second-branch number is unquantified.** §2.3 gives the rule; nobody has
   run it.
4. **Six macros in `Validation/` have never run**, three bearing on open blockers
   (C8, B3). I listed them and executed nothing. **I did not check whether any is
   trivially runnable** — M7's took 3.3 s per file, and that is the first thing
   you will want to know.
5. **Everything v3 downstream of the merge is untested at three-tune scale.** The
   extraction reader is exact on four directories — all MONASH, all one tune.
6. **The merge has not launched for seven sessions.** Every deferral was correct.
   The count is still seven, and the resubmission's central number is two steps
   past it.

---

## 7. IF YOU READ ONLY ONE THING

**The gate (`5399423`) finishes ~16:10 today and is the only thing running.
Verify its PASS, then launch the merge — that is your first act and §2.1 has
everything it needs. Watch it by counts, never by projection: this workload's
unit costs are ordered and every prefix lies pessimistically. After it lands:
closure at scale under the INVERTED v3 table (2100/1500, never 1800/600), then
blocks → SEMs on the species decomposition under both conventions, which is the
number the resubmission turns on. M7's beauty half and the second-branch number
are the two known gaps in the paper pack, both authorized and neither started.**
