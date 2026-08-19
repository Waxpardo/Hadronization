# Phase 4 — full-production submission checklist

**Written 2026-08-06.** Read this before deciding whether to submit.
Every item is either **VERIFIED** with the evidence beside it, or **PENDING**
with what would close it. Nothing is asserted from memory.

**Do not run `make submit-full` without the owner's explicit go.**

---

## A. The post-production expectation — TWO terms, not one number

**Stating this as a single wall-clock figure hides the fact that only one of
the two is a problem, and only one has a remedy pending.**

### Term 1 — the checksum gate. A REAL floor until the pool exists

| | |
|---|---|
| what | `tools/validate_analysis_outputs.py`, run by `merge_root_files.sh:81` **and** by `submit_status_analysis.sh` before a single job is queued |
| measured | **4156.96 s at 300 directories** (~29 GB) — standalone P=1 reference, `/usr/bin/time`, unmodified gate, `--report` omitted, uncontended on `stbc-i3`. Artifact `poolsweep_run01/p1_time.txt`. (Supersedes an in-run 4354 s, which it agrees with to 4.5 %) |
| profile | **CPU-bound, CPU/wall = 0.919** — `user 3612.88 + sys 205.17 = 3818.05 s` |
| projected | **~41,570 s ≈ 11.5 h at 3000 directories**, linear in wall |
| CPU against ceiling | tree CPU **~38,200 s at 3000** — but `ulimit -t` is **per process** and the correct comparand is **one ROOT child**, which is far below 115,200 s. **The ceiling does not bind; blocking wall-clock is still the problem** |
| remedy | **bounded pool** — **NOT measured, and the earlier ~1.5 h costing needs re-baselining**: it assumed latency-bound scaling, so speed-up is bounded by **core count**, not by outstanding I/O. **Its RSS column may also be understated ~24x** — see the caution below |
| status | **PENDING.** This is the one genuine defect left in B10 |

**Pool sizing — MEASURED 2026-08-09, and the old table inverts.** A dedicated
`/usr/bin/time -v` run of one `validate_pair_directory.sh` on a promoted
directory, batch node, uncontended
(`/data/alice/ipardoza/poolrss_run01/time_v.txt`):

```
Maximum resident set size (kbytes): 584452       # 570.8 MiB
User 650.08 s  System 0.84 s  Elapsed 10:54.07  Percent of CPU 99%
```

**A single ROOT directory validator uses 570.8 MiB at 99 % CPU.** The 18.4 MB
figure is the Python orchestrator, not a worker. Per-worker footprints:
**gate child 440.9 MiB** (from the P=1 `maxrssKB=451480`), **merge-side
570.8 MiB**.

**Against the 2048 MiB login-node cap:**

| pool | P=4 | P=8 |
|---|---|---|
| gate | 1764 MiB — fits | **3527 MiB — EXCEEDS** |
| merge-side | **2283 MiB — EXCEEDS** | 4566 MiB — exceeds |

**Corrected sizing: on the login node, P≤4 for the gate and P≤3 for the
merge-side validations. B10's "P=8 fits even under the 2.00 GiB login cap" is
wrong.** **Prefer a batch node**, where the cap is 128 GiB and neither binds.

### Term 2 — the merge phase. NOT a floor, and needs no split

| | |
|---|---|
| what | 33 independent `merge_one()` invocations, each its own `root.exe` |
| measured | **15,900 s = 4 h 25 m** across 33 directories at 100 inputs (run01) |
| largest single process | **the macro, 6362.98 s CPU** (`/usr/bin/time`, MONASH 100 inputs, single-threaded 98.9 %) |
| projected at 1000 inputs — **pessimistic**, all-linear | **63,630 s = 17.7 h CPU — 55 % of the 32 h per-process ceiling** |
| projected at 1000 inputs — **measured**, baseline-linear + excess as sqrt(N) | **22,468 s = 6.2 h — 19 %** |
| status | **VERIFIED. The ceiling does not bind under either model. No split required** |

**Both models are given deliberately.** The conclusion does not depend on
choosing between them, and this project's recurring failure mode has been
numbers quoted without their basis.

### HAZARD — re-running the gate for timing invalidates ALL promoted directories

**Whoever runs the gate at full production will be tempted to re-run it to time
it. Doing that in place breaks every promoted merge directory, and the failure
surfaces hours later looking like a Condor fault.**

`analysis_output_manifest_validation.json` has its sha256 recorded as
`analysis_output_validation_sha256` inside **every** promoted directory's
`merge_provenance.json` (`merged_pair_provenance.py:146`, compared key-by-key at
`:205-210`). **Rewrite the report and all 33 directories fail `validate`.**

> ## ⚠ CLARIFICATION 2026-08-11 — the ban is on STANDALONE invocation only
>
> **`merge_root_files.sh:80-83` runs `validate_analysis_outputs.py` WITH
> `--report`, unconditionally, as its first step. That is the DESIGNED PATH and
> it is not a violation.** The merge's internal call is what *creates* the
> report whose sha256 every promoted directory then records.
>
> **What is prohibited is invoking it yourself**, which would rewrite that
> report out from under the promoted directories.
>
> **Consequences that follow, and both have nearly cost a session:**
> - **Resuming the merge = re-running the same merge command.** Correct, and
>   not a violation, even though it re-runs the gate with `--report`. Every
>   resume re-pays ~19 h for exactly this reason.
> - **A merge whose log is silent for ~19 h is in this internal gate**, not
>   stalled.
>
> Read together with the standing prohibition list, this rule and the merge
> look like a head-on conflict. They are not. **Do not stop the merge over it.**

**The safe form — `--report` OMITTED.** It is optional
(`validate_analysis_outputs.py:292`); with it absent the gate does the entire
validation and **writes nothing**:

```bash
python3 tools/validate_analysis_outputs.py \
  "$FREEZE/canonical_manifest.jsonl" "$ANALYSIS_ROOT" \
  --production-root "$PRODUCTION_ROOT" --checkout "$PWD"
```

Confirm before trusting it: `tr '\0' ' ' < /proc/<pid>/cmdline | grep -c -- --report`
must print `0`.

**`:570-576` refuses to overwrite a report whose content differs. That is a
guard that catches the mistake — it is not a licence to attempt it.**

### THE ONE SENTENCE MOST LIKELY TO BE LOST IN A TABLE

> **The gate's 12.1 h is a wall-clock floor until the pool is built. The merge
> phase's 4 h 25 m is NOT a floor — it is 33 independent units that fan out to
> roughly the cost of the single largest directory.**

### Both fan out, for the SAME reason: their units are independent

**An earlier version of this checklist said they fan out for *opposite* reasons
— gate latency-bound, merge CPU-bound. That was wrong on the gate half and is
now corrected. Both stages are CPU-bound, and both parallelise because their
units are independent, not because fan-out hides I/O waits.**

| | **Gate** | **Merge** |
|---|---|---|
| unit | one directory validation (300, later 3000) | one `merge_one()` directory (33) |
| profile | **CPU-bound, 0.919** | **CPU-bound** — its two directory validations are 0.982 and are 79 % of each window |
| why it fans out | **units are independent** | **units are independent** |
| what parallelism buys | removes serialisation between units; **bounded by cores** | removes serialisation between units; **bounded by cores** |
| shape of the fix | a bounded pool — **but `validate_analysis_outputs.py` writes the single report `merge_root_files.sh:80-84` consumes, so *sharding* CHANGES A CONTRACT** (pooling does not) | **no contract change at all** — `merge_one()` is already self-contained; see B10 |

**The one asymmetry that remains is the contract, not the profile.** That is the
real reason to start the gate with a pool rather than a Condor shard, and it is
the only line in this table that distinguishes the two stages.

**The trap, named — and it is the opposite of what this section used to say.**
Both stages were predicted at CPU/wall 0.050 and **both measured CPU-bound**:
the gate at **0.919** (`3818.05 s` CPU vs `4156.96 s` wall) and
`validate_pair_directory.sh` at **0.982** (`623.22 s` vs `634.46 s`). The 0.050
figure came from reading a **single PID's `/proc`** while the real work ran in
spawned ROOT children. **The lesson is not "these two tools differ" — it is that
a single-PID sample is not a measurement of a process tree.** Sample the tree,
or use `/usr/bin/time` on the top process, and record which you did.

### Why "no split required" is UNCONDITIONAL

**The CPU-ceiling blocker was closed, and it was closed properly — not dropped.**
It rested on one open condition, and that condition was **discharged by audit on
2026-08-06**, not left outstanding: `merged_pair_provenance.py` holds **no
cross-directory state** (no writes outside its own directory, no other merged
directory ever read, no ordering dependency), verified both by reading and by
running two `validate` invocations concurrently on different promoted
directories with byte-identical before/after sidecar mtimes.
**See `RELEASE_BLOCKERS.md` B10, "AUDIT DONE 2026-08-06".**

**A reader who remembers the CPU-ceiling scare should be able to see here that
it was resolved rather than forgotten.** It was: the retraction is lifted, the
merge half is a note, and the closure was by measurement and bound with **no
code change** — the pipeline was always fine, the number describing it was not.

---

## B. Pre-submission gates

| # | item | status |
|---|---|---|
| B1 | **Both trees clean and agreeing** | **PENDING** — local `physics-focus` @ `6988970` carries uncommitted v8 handoff + blocker edits; Nikhef frozen at `e690e17`. Closes at the sync step |
| B2 | **Producer SHA** matches `e54b27bb9e3f…` | **VERIFIED** — `upstream_executable_sha256=e54b27bb9e3fcfd42d70193e08e2eacf965cc5081eabb5c42a9971203f130659` present in all 300 analysis outputs, re-confirmed in this session's validation output |
| B3 | **`make check` green, bare, on Nikhef** | **PENDING** — last known 24/24 locally. **Never run bare on Nikhef**; blocked by the freeze until sync |
| B4 | **Campaign registered with `ORDINAL=3` explicitly** | **MECHANISM VERIFIED, registration PENDING** — `Makefile:36` is `ORDINAL ?=` with **no default**, and `:167-173` refuses with `ERROR: ORDINAL is not set, and there is deliberately no default.` / `Re-run as: make <target> ORDINAL=3`. B11 is implemented. Ordinals 1 (HF_PT2, HF_SMOKE2, PTHAT2) and 2 (HF_PT2_INT) are used; **3 is the next free value** |
| B5 | **`JOBS` / `EVENTS` shape, no fossil** | **VERIFIED** — `Makefile:25-26`, `JOBS ?= 1000`, `EVENTS ?= 100000`. The fossil shape is in the **paper**, not the Makefile — that is B1, a separate blocker |
| B6 | **Dry render inspected** | **PENDING** — render and read the submit file before queueing |
| B7 | **CPU budget** | **VERIFIED as 562.5 CPU-hours**, measured means with per-tune breakdown, housed in `REPRODUCIBILITY.md` §6 because `RELEASE_BLOCKERS.md` disappears at submission |
| B8 | **Fair-share expectation** | **OBSERVED, not fixed** — farm load varies materially: **6554 jobs (4600 running)** on 2026-08-05, **3740 (2663 running, 796 idle, 281 held)** on 2026-08-06. Treat ~5460 as a mid-range observation, **not a planning constant**; re-read `condor_q` at submission time |
| B9 | **Seed ledger** | 430 lines, 430 unique, verified. **Never touch it outside `tools/campaign.py`** |
| B10 | **Quarantine** | `submit_HF_PT2_INT_retry7.sub` stays until after full production is submitted. **Never submit from `/data/alice/ipardoza/quarantine/`** |

---

## B2. THE READINESS WALK — 2026-08-09, post-sync

**Every line is evidenced with its artifact, or listed outstanding.**

| # | precondition | status | evidence |
|---|---|---|---|
| 1 | **Both trees synced and agreeing** | **✅ EVIDENCED** | Nikhef advanced `e690e17` → **`31badd6`**, `git merge --ff-only`, branch `physics-focus`. Only untracked file remains `submit_HF_PT2_INT_intermediate.sub`. 46 commits, 24 files |
| 2 | **`make check` green, bare, on Nikhef** | **✅ EVIDENCED** | **24/24 passed**, run bare via `bash -lc "make check"`. Pre-registered 24/24; **23/23 would have meant B9's test did not carry** — `test_resubmit_held_ordinal.py` is present and PASS |
| 3 | **Producer SHA unchanged** | **✅ EVIDENCED** | `PRODUCER_BUILD_READY … sha256=e54b27bb9e3fcfd42d70193e08e2eacf965cc5081eabb5c42a9971203f130659 forced_rebuild=true` — byte-identical from a genuine recompile. Pre-flight confirmed no `SimulationScripts/*.cpp|h` and no build-flag change in `e690e17..HEAD` |
| 4 | **Seeds recorded on submit** | **✅ EVIDENCED** | B2 landed `81a350c`. **All three targets pass `--burn-seeds`** (`Makefile:183,210,221`), burning at **render** time by documented contract (`tools/campaign.py burn_seeds`) |
| 5 | **Seed ledger clean** | **✅ EVIDENCED** | **430 lines, 430 unique** — no duplicates |
| 6 | **Ordinal 3 unused** | **✅ EVIDENCED** | On-disk attempt metadata: HF_PT2 = 1, HF_SMOKE2 = 1, PTHAT2 = 1, HF_PT2_INT = 2. **3 is free** |
| 7 | **`require-ordinal` fails closed** | **✅ EVIDENCED** | `Makefile:166-175` — no default, exits 1, and names the used ordinals in the error |
| 8 | **Retry tooling correct** | **✅ EVIDENCED** | B9 **closed**, `e403853`: derivation `resubmit_held.py:71-89`, `--campaign-ordinal` defaults `None`, multi-ordinal refusal, test in the 24 |
| 9 | **Retry batch size at scale** | **⚠️ RESIDUAL RISK, NAMED** | The **~80-held-job batch is exercised only by production itself** (B7 item 3). Budget: **~2.7 % hang rate, two-to-three rounds**, `MAX_ATTEMPTS = 10` (`campaign.py:69`) — ample rounds |
| 10 | **Closure failures are diagnosable** | **✅ EVIDENCED** | B13 landed `f44b3c1` — failure path retains the log and echoes its location |
| 11 | **F1 variation weights** | **✅ RECORDED OFF** | Signed 2026-08-09; `DESIGN_AND_RATIONALE.md` §3.15, F1 gate closed |
| 12 | **Guard demotion** | **✅ STRUCK FROM G1** | Antecedent identified (per-tune CPU guard) and recorded; remains post-production hygiene |
| 13 | **B6 rung-6 targets** | **❌ OUTSTANDING** | **`thnsparse` and `audit-subsamples` do not exist as Makefile targets.** The root Makefile has 21 targets and neither is among them; no occurrence anywhere; no `plotting/Makefile`. B6 cites "v4 section 4", which predates the current Makefile. **Not run. Not guessed at.** |
| 14 | **Disk** | **✅ EVIDENCED** | **1442 GB free** on `/data/alice` against **~264 GB** raw at 3000 jobs (88.0 MiB/job measured). ~5.5x headroom |
| 15 | **Campaign shape** | **✅ EVIDENCED** | `JOBS = 1000`, `EVENTS = 100000` (`Makefile:25-26`), three tunes. **562.5 CPU-h** (`REPRODUCIBILITY.md` §6) **plus ~2.7 % retry overhead** |

### THE STATEMENT

> **READY, with one outstanding item that does not block: B6.**

**Why B6 does not block.** v4 precondition 12 requires **owner sign-off** if the
two rung-6 targets are first exercised for real by full production. That is a
**sign-off decision, not a code gate** — and it cannot be discharged by running
them, because **the targets named in B6 do not exist under those names.**
Resolving B6 means either locating what they were renamed to, or striking the
entry — both owner calls, neither a precondition on the generator.

**Everything that gates what the farm writes is evidenced.** The producer is
byte-identical, the tests are green on the machine that will run it, seeds burn,
the ordinal is free and fails closed, and disk has 5.5x headroom.

**One residual risk carried forward, not resolved:** item 9 — the retry batch
size at production scale. It is a property of the run, and the retry budget
covers it.

---

## B3. AFTER SUBMISSION — the jobs are HELD. Release is a separate act

**Render, submit, and start are three deliberate acts, not one.** A rendered
`.sub` reserves seeds; `condor_submit` queues the jobs; **`condor_release`
starts them.** Nothing runs until the third.

**`tools/render_production_submit.py:286` emits `hold = True` unconditionally**,
so every campaign lands entirely held. This is the design, not a fault: it means
a submitted campaign can be inspected — rows, seeds, provenance, queue shape —
before a single CPU-second is spent, and a mis-rendered submission costs nothing
but a `condor_rm`.

**The step, stated so it is not discovered:**

```bash
condor_q <cluster> -af HoldReasonCode   # expect: every job 15
condor_release <cluster>
condor_q                                # expect: 0 held
```

**Verify the hold reasons BEFORE releasing.** If any job is held at t=0 for a
reason other than code 15, releasing masks whatever put it there.

### THE TWO HOLD CLASSES — identical in `condor_q`, opposite in meaning

| hold | when it appears | what it means | action |
|---|---|---|---|
| **`HoldReasonCode 15`** — "submitted on hold at user's request" | **at submit, ALL jobs** | the deliberate parking brake | **release** |
| **`HF_HANG_GUARD suspected generator hang`** | after **>3600 s CPU** or **>14400 s wall** | a genuinely wedged generator, ~2.7 % expected | **retry** (`resubmit_held.py`) |

> **A queue showing "N held" is evidence of nothing until the hold reason is
> read.** The two classes are indistinguishable in a summary line, and treating
> the parking brake as a hang — or a hang as the parking brake — sends the
> operator to entirely the wrong work.

**Worked example, HF_RUN3_V1:** submitted 2026-08-09T04:17:14Z, all 3000 jobs
held at code 15; verified; released 04:23:55Z; queue went to 0 held / 2999 idle
/ 1 running. See `docs/campaigns/HF_RUN3_V1_RECORD.md`.

---

## C. Order of operations at submission

1. Sync — lift the freeze, land the deferred commits (B2 `--burn-seeds`, B9
   ordinal derivation, the guard demotion).
2. `make check` bare on Nikhef — must be green **on Nikhef**, not locally.
3. Register the campaign with an **explicit `ORDINAL=3`**.
4. Render the submit file and **read it** before queueing.
5. Re-read `condor_q` for the live fair-share picture.
6. **Stop. Get the owner's explicit go.**
7. Only then `make submit-full`.

**The gate runs before the first job is queued and takes ~12.1 h.** Budget for
it, or build the pool first — that decision is the last open question in B10.

---

## D. PAPER FIGURES — what must be true before a figure goes in

**Added 2026-08-17.** These are not production gates; they are the conditions a
figure has to satisfy to be quoted. Each one exists because it was violated once.

### D1. Every class label is generated, never transcribed ⚑ blocks the affected figure

- [ ] **`tools/apply_class_labels.py --check` passes on every plotting
      configuration.** Class percentiles are generated from
      `config/multiplicity_class_boundaries_v1.json` and the committed MB
      anchor, rounded **once** from full precision.
- [ ] **The manuscript figure that carries the `59.9 %` label has been
      regenerated from generator-produced configs.** It currently reads
      `59.9-65.9%` and `50.3-59.9%`; the axis definition gives **59.8**.
      `ERROR_RECORD.md` **E9**.
- [ ] The corrections have owner sign-off. Until then they stay in the
      polish-proposal config and the committed reference is byte-identical.

### D2. Spectra captions use the run record's selections, verbatim

`docs/plotting_validation/hf_run3_v1_kinematics_20260817/RUN_RECORD.md` §1 holds
both, read from the filling code rather than from the previous figure's label.

- [ ] **Multiplicity counter:** primary charged, `isFinal && isCharged &&
      !hasHeavyConstituent`, **pT > 0.15 GeV/c**, **|η| ≤ 1.0** — the η cut is
      **inclusive**, and **heavy flavour is excluded**.
- [ ] **Spectra acceptance:** **direct primary hadronisation products**
      (status 81–89), **pT > 0.15 GeV/c**, **|η| ≤ 4.0**.
- [ ] **Status 81–89 is never called "prompt."** `PAPER_FIGURE_PROVENANCE.md`
      records `Model.tex:53` and `:129` doing exactly that; a figure caption must
      not inherit it.
- [ ] The acceptance is presented as the spectrum's **domain**, not as cuts
      overlaid on an unrestricted distribution — the histograms already begin at
      the cut. Only the **trigger** threshold (pT > 1 GeV/c) sits inside the
      drawn range and can honestly be drawn as a marker.

### D3. Provenance, per figure

- [ ] Rendered from a `canonical` + `publication_eligible` dataset, with the
      authorization cited by sha256.
- [ ] **Pinned ROOT 6.30/01**, recorded with the command and inputs.
- [ ] sha256 of every output in `docs/GOLDEN_OUTPUTS.md`, with its recipe.
- [ ] **Energy label reads 13.6 TeV.** No plotting source contains "14 TeV"; a 14
      on any figure means the file predates the current generator.
- [ ] **Someone looked at the render.** Every figure in this project that was
      wrong was wrong in a way a glance would not have caught — which is why
      looking is necessary and not sufficient.
