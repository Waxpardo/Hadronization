# Nikhef disk inventory — `/data/alice/ipardoza`, metadata only

**Walked 2026-08-12 from branch `restructure-prep`.** Evidence for
`docs/RESTRUCTURE_PLAN.md` §10. **The disk consolidation is a separate operation
from the repository restructure and is not authorised by this document.**

> **⚠ READ §7 FIRST.** The owner ruled on these findings the same day and the
> consolidation was **reshaped from a move into a mapping**: no physical
> checkout move, big trees stay put, `b-hadron-fractions` out of scope. **The
> "MOVE" tags in §2 and §3 below predate that ruling and are superseded by §7.**
> They are left in place because they are what the measurements supported before
> the ruling, and overwriting them would hide why the ruling was made.

---

## 0. METHOD, AND WHAT WAS DELIBERATELY NOT DONE

**Stat-only.** Four `ssh stbc` invocations, all foreground, all bounded:
one `find -maxdepth 1 -printf`, three `du -s` batches, one `df`. **No file
contents were read. Nothing was checksummed. No process was left running.**

| deliberately NOT done | why |
|---|---|
| **`hadronization_analysis/**/per_job/` was not walked, at any depth** | `per_job/JUNCTIONS` and `per_job/CLOSEPACKING` are the **live merge's progress instrument**. A `du` there does `readdir` on every one of ~3000 slot directories, stamping fresh atimes under `relatime` — which both **corrupts the frontier probe** and **reports this walk as merge progress**. `docs/PROGRESS_PROBE_METHOD.md` §4 correction 1 names exactly this failure |
| **nothing was checksummed remotely** | checksums belong to the move itself, where they have a before/after pair to compare. A checksum taken five sessions early is a number with nothing to check against — and computing one requires reading contents |
| **no recursion below `HF_RUN3_V1/` in the production and analysis trees** | the top two levels answer the layout question; deeper adds NFS metadata load to a contended node for nothing |

**Consequence, stated rather than papered over:** `hadronization_analysis/` has
**no size in this inventory**. It is the one tree whose size is genuinely
unknown here, and that is a choice, not an oversight.

**Filesystem:** `data-02:/alice`, **32 T, 31 T used, 1.1 T available, 97 %**.
NFS4, `relatime`.

---

## 1. THE HEADLINE

| rank | item | size | is it this project? |
|---|---|---|---|
| 1 | **`b-hadron-fractions/`** | **1.2 T** | **no — a different project** |
| 2 | `Hadronization/` (the frozen checkout) | **445 G** | yes |
| 3 | `hadronization_production/` | **304 G** | yes |
| 4 | `HRP/` | 73 G | no |
| 5 | `hadronization_merged/` | 41 G | yes |
| 6 | `Axions/` | 33 G | no |
| — | `hadronization_analysis/` | **not walked** | yes |

**Measured total ≥ 2.1 T**, excluding `hadronization_analysis/`.

### 1.1 Two findings that change the shape of the consolidation

**Finding 1 — the largest single item under this directory is not this
project.** `b-hadron-fractions/` is **1.2 TB**, more than half the measured
total, on a filesystem at 97 %. Nothing in the Hadronization record references
it. **Whether it can be archived is an owner question that has nothing to do
with the restructure and is worth more free space than everything else here
combined.**

**Finding 2 — 423 GB of gitignored working data lives inside the frozen git
checkout.**

| inside `Hadronization/` | size | tracked? |
|---|---|---|
| `RootFiles/` | **409 G** | **no** — `.gitignore:3` ignores `/RootFiles/**/*.root` |
| `AnalyzedData/` | 6.0 G | **no** — `.gitignore:14,23,24` |
| `AnalysisResults/` | 5.7 G | **no** — `.gitignore:22` |
| `Production/` | 2.4 G | **no** — `.gitignore:18` |
| **subtotal, gitignored working data** | **≈ 423 G** | |
| `.git/` | **23 G** | the object store |
| `logs/` + `Logs/` | 188 M | no |
| tracked source and docs | ≈ 25 M | yes |

> **This is why "advance the checkout" and "move the checkout" are operations of
> completely different cost.** Advancing is a ref update on a 23 GB object store.
> Moving is 445 GB across NFS. **The guard hook, the pinfile and `make
> can-advance` all govern the cheap one.** Any consolidation plan that treats
> "relocate the checkout" as a routine step has mispriced it by four orders of
> magnitude.

---

## 2. THE PROJECT'S OWN TREES

| path | size | mtime | class | note |
|---|---|---|---|---|
| `Hadronization/` | **445 G** | 2026-08-09 20:01 | **KEEP — DO NOT MOVE YET** | the frozen checkout. Guard-pinned; `tune_extract.sh` `cd`s here and sources `./setupEnv.sh`. **Three chains are running against it right now** |
| `Hadronization-full-production/` | 5.6 G | 2026-07-30 23:34 | **KEEP** | **holds the seed ledgers** — `campaigns/*/seed_ledger.jsonl`, 3557/3557 burned. Nothing re-derives historical seeds; orphaning this forfeits campaign provenance |
| `hadronization_production/HF_RUN3_V1/` | 304 G total | 2026-08-09 06:24 | **MOVE → `campaign/`** | `raw/`, `attempt_metadata/`, `raw_validation/`, `partial/`, `work/`. Also holds HF_SMOKE, HF_SMOKE2, HF_PT2, HF_PT2_INT eras |
| `hadronization_analysis/HF_RUN3_V1/` | **not walked** | 2026-08-10 22:32 | **MOVE → `campaign/`** | contains `per_job/` — **the live instrument**. Move only when nothing runs |
| `hadronization_merged/` | 41 G | 2026-08-12 02:55 | **MOVE → `merged/`** | see §2.1 |
| `tune_runs/` | 24 K | 2026-08-11 20:51 | **KEEP — LIVE** | the three chains' outputs. 24 K because closure has not returned yet |
| `pythia_stock_8317/` | 317 M | 2026-08-01 20:50 | **MOVE → `software/`** | the pinned generator. `REPRODUCIBILITY.md` §4 calls this the biggest portability weakness |
| `archive/` | 1.1 G | 2026-08-09 20:18 | **KEEP AS ARCHIVE — UNTOUCHABLE** | the 34 breach partials. *Moved, never deleted*, with a committed manifest |
| `quarantine/` | 12 K | 2026-08-05 02:08 | **KEEP AS ARCHIVE** | |
| `merge_runs/` | **4.3 G** | 2026-08-10 22:32 | ⚠ **FREEZE — do not clear** | **the merge timing evidence is filesystem mtimes here.** `GOLDEN_OUTPUTS.md` §5 N2: the merge log carries no timestamps, so clearing this destroys the only basis for scoring the 65–77 h band |
| `seed_ledger_archive/` | 296 K | 2026-07-30 21:28 | **KEEP AS ARCHIVE** | |

### 2.1 Inside `hadronization_merged/` — one entry is live

| entry | mtime | class |
|---|---|---|
| `complete_root_HF_RUN3_V1_MONASH` | 2026-08-11 14:57 | **KEEP** — the merged central behind every current number |
| `SUBSAMPLES_HF_RUN3_V1` | 2026-08-11 16:07 | **KEEP** — the ten MONASH blocks |
| **`complete_root_HF_RUN3_V1_JUNCTIONS.partial.iHJ4n3`** | **2026-08-12 12:20** | ⚠ **LIVE — the merge is writing it now** |
| `complete_root_HF_PT2_INT_{MONASH,JUNCTIONS,CLOSEPACKING}`, `SUBSAMPLES_HF_PT2_INT` | 2026-08-05 | **ARCHIVE** — previous campaign |
| `complete_root_HF_PT2_{MONASH,JUNCTIONS,CLOSEPACKING}`, `SUBSAMPLES_HF_PT2` | 2026-08-03 | **ARCHIVE** — previous campaign |

> **The `.partial.` directory is not junk.** `MERGE_V3_PREREGISTRATION` notes
> that abandoned `.partial.` stages accumulate — but this one's mtime is
> **minutes old**. It is the JUNCTIONS central being merged. **A cleanup sweep
> that pattern-matches `*.partial.*` would delete a running merge's output.**

---

## 3. SCRATCH — one directory per investigation

All **MOVE → `scratch/<name>/`** unless noted. Sizes measured 2026-08-12.

| directory | size | mtime | note |
|---|---|---|---|
| `f3_runs` | 63 M | 2026-08-10 01:21 | F3 virtual-trigger closure; **held `extraction_dual/` before it was committed** |
| `species_axis_fixture` | 89 M | 2026-08-09 15:03 | the 900 files behind `SPECIES_AXIS_VALIDATION.md` |
| `rehash_run` | 9.4 M | 2026-08-09 17:47 | |
| `determinism_control` | 8.4 M | 2026-08-09 17:27 | |
| `sigmab_runs` | 6.2 M | 2026-08-11 19:32 | **Task 2 + the deployed reader** (`sigmab_runs/task22`, which `tune_extract.sh` still reads). **KEEP until the chains finish** |
| `b6_run` | 4.3 M | 2026-08-09 18:16 | |
| `gate_runs` | 2.7 M | 2026-08-10 15:26 | holds `GATE_3000_DONE` |
| `m7b_runs` | 864 K | 2026-08-10 22:31 | beauty M7; its logs **are** committed as anchors |
| `m7_runs` | 840 K | 2026-08-10 01:07 | **charm M7 — its logs are NOT committed** (`GOLDEN_OUTPUTS.md` §5 N7). ⚠ **the highest-value 840 K on this disk** |
| `pythia_hang_repro` | 556 K | 2026-08-01 21:36 | evidence for B7 |
| `f4b_runs` | 488 K | 2026-08-10 23:16 | |
| `contract_compile_check` | 468 K | 2026-08-09 10:08 | |
| `registry_baseline_build` | 320 K | 2026-07-31 01:36 | |
| `first_contact` | 288 K | 2026-08-09 17:16 | |
| `f4_runs` | 224 K | 2026-08-10 01:03 | |
| `guard_hook_test` | 192 K | 2026-08-10 23:06 | the E2 harness that deleted its own hook |
| `b4_mapping` | 148 K | 2026-08-09 06:49 | |
| `species_ordinals_build` | 108 K | 2026-08-09 09:55 | where G1 was built |
| `a2_multiplicity` | 76 K | 2026-08-04 21:02 | |
| `guard_hook_src` | 28 K | 2026-08-10 23:07 | |
| `proj6iii_v2` | 24 K | 2026-08-09 07:31 | |
| `proj6iii_run01` | 20 K | 2026-08-09 05:03 | |
| `poolrss_run01`, `poolsweep_run01` | 16 K each | 2026-08-09 | the pool-sizing investigation the owner and agent disagreed about |
| `__pycache__`, `lib`, `tmp`, `pthat_scan_8317` | 4–12 K | — | **ARCHIVE or delete** — empty or byte-code |

> **`m7_runs` is 840 KB and holds the only copy of the charm-M7 block logs.**
> `m7b_runs`' beauty logs were anchored into the repository; the charm ones were
> not. **If one thing on this disk gets copied into git before anything moves, it
> is this.**

---

## 4. LOOSE FILES AT THE TOP LEVEL — ~70 of them

**Nothing here is unique data**, but the count is the problem: seventy loose
files sitting beside 2 TB of trees.

| group | count | class | note |
|---|---|---|---|
| `*.bundle` (`physics-focus`, `hf_sync`, `hf_43e35be`, `docs`, `b6`, `rec`, `topup`, `pilot`, `closure`, `void`, `guardrail`, `rawv7`, `nch-calib`, `energy-136-fixed`, `final`, `b6fix`) | 16 | **ARCHIVE → `archive/bundles/`** | git bundles used to ship commits to Nikhef. Their content is in the object store |
| scratch-deployed copies of committed tools (`extract_species_decomposition.py`, `tune_chain.sh`, `tune_extract.sh`, `queue_probe.py`, `checkout_advance_guard.py`, `install_checkout_guard_hook.sh`, `archive_breach_partials.sh`) | 7 | **MOVE → `scratch/deploys/`** | ⚠ **this pattern is deliberate**: the frozen checkout is read, never written, so tools deploy to scratch with their sha recorded. **Do not "consolidate" these back into the checkout** |
| investigation scripts (`scaling_series*.sh`, `scaling_*_batch.sh`, `poolrss.sh`, `poolsweep_p1.sh`, `proj6iii*.sh`, `run_gate.sh`, `f3_gate.sh`, `f3_step2.sh`, `validate_one.sh`, `validate_34.sh`, `verify_merge.sh`, `rerun_closure.sh`, `run_closures.sh`, `diag_closure.sh`, `rss_curve.sh`, `run_merge_instrumented.sh`, `summarize_merge.py`) | ~18 | **MOVE → `scratch/misc/`** | several are cited by name in `docs/` as provenance for a measurement |
| `*.sub` Condor submit files | 7 | **MOVE → `scratch/misc/`** | |
| outputs (`bimodality_5390385.txt`, `bimodality.done`, `bimodality.err`, `hf_pt2_int_cpu.txt`, `condor_queue_evidence_*.txt`, `condor_submit_HF_PT2_INT.out`, `merge_launch.out`, `compile_hf.log`, `FlavourClosure_Dplus.png`) | 9 | **ARCHIVE** | `hf_pt2_int_cpu.txt` is the basis of the **562.5 CPU-hours** figure in `REPRODUCIBILITY.md` §6 — **keep it** |
| `producer_e54b27bb_HF_PT2.bak` | 1 | **KEEP AS ARCHIVE** | the producer binary whose sha `e54b27bb9e3f…` is contract **C-3**. **A backup of a pinned binary is evidence** |

---

## 5. NOT THIS PROJECT

Inventoried because they are under the same directory and dominate the space.
**Classified UNKNOWN — the owner decides; none of it is the restructure's
business.**

| path | size | mtime | class |
|---|---|---|---|
| **`b-hadron-fractions/`** | **1.2 T** | 2026-05-10 11:01 | **UNKNOWN** — *see §1.1 finding 1* |
| `HRP/` | 73 G | 2025-12-01 12:53 | **UNKNOWN** — untouched for 8 months |
| `Axions/` | 33 G | 2026-06-08 12:49 | **UNKNOWN** |
| `.vscodium-server/` | 1.1 G | 2026-08-12 11:21 | **UNKNOWN** — an editor server cache, active today |
| `Hadronization-Tune-Integration/` | 13 M | 2026-06-26 21:42 | **UNKNOWN** — a checkout of the `Tune-Integration` branch |
| `HRP_clean/` | 12 M | 2026-02-24 12:43 | **UNKNOWN** |
| `nikhef_stale_fullprod_20260730/` | 4.8 M | 2026-07-30 21:06 | **ARCHIVE** — the name says stale, and the record agrees |
| `Axions_pre_update_conflicts_…/` | 100 K | 2026-06-07 18:41 | **ARCHIVE** |
| `EDMs/` | 4.0 K | 2025-10-02 13:23 | **ARCHIVE** — effectively empty |
| `.vscode/` | 4.0 K | 2026-03-27 23:17 | **UNKNOWN** |

> **`HRP/` at 73 G and `Axions/` at 33 G have not been touched in 8 and 2 months
> respectively.** Together with `b-hadron-fractions/` that is **1.3 TB of cold
> data on a filesystem with 1.1 TB free.** Stated as an observation; the decision
> is not this project's.

---

## 6. WHAT MUST NOT MOVE, AND WHEN

Ordered by how expensive the mistake would be.

| # | item | rule |
|---|---|---|
| **1** | `hadronization_analysis/**/per_job/` | **do not even walk it while the merge runs.** Reading it corrupts the frontier probe and misreports itself as progress |
| **2** | `merge_runs/` | **freeze until the band is scored.** The evidence is mtimes; clearing it destroys them irrecoverably |
| **3** | `hadronization_merged/*.partial.*` | **not junk while a merge runs** — one is being written right now |
| **4** | `archive/` (34 breach partials) | untouchable; *moved, never deleted*, with a committed manifest |
| **5** | `Hadronization/` (frozen checkout) | pinned by the guard hook and the pinfile; the probe returns **UNKNOWN** on the login node and refuses. 445 G — see §1.1. ⚠ **The pinfile's recorded removal protocol is INVALID** — `ERROR_RECORD.md` **E8**. Operative condition: the `CLOSEPACKING` closure marker present **and** PID `315689` exited. The gate session refreshes the file before any removal |
| **6** | `sigmab_runs/task22` | holds the **deployed reader** the running chains execute |
| **7** | `Hadronization-full-production/campaigns/*/seed_ledger.jsonl` | 3557/3557 burned seeds; nothing re-derives historical seeds |

### 6.1 ➕ ADDED 2026-08-17 — the systematics artifacts are LIVE, not archivable

**Owner ruling, Consolidation A addendum:** the new systematics deploy and pilot
outputs on `stbc-i1` join the scratch-reconciliation task, **inventoried and
LIVE — not archivable until the campaigns converge and are harvested.**

Seven campaigns (Condor `5519094`–`5519100`, 2100 jobs) were queued 2026-08-17
and were still running when this was written. Measured, not estimated:

| path | size now | at convergence | rule |
|---|---|---|---|
| `systematics_deploy/Hadronization` | **132 M** | unchanged | ⛔ **DO NOT TOUCH.** All in-flight jobs verify its HEAD `72ca4e39` at startup and refuse a tree with tracked modifications. Checking out, pulling or editing a tracked file here fails every remaining job. Pinned in `docs/SYSTEMATICS.md` §9 |
| `systematics_deploy/nch_recal_8317/` | 16 K | unchanged | the 8.317 decay-policy re-measurement log; **evidence** for `ValidationReports/NCH_DECAY_POLICY_BIAS_8317.md`. Keep |
| `systematics_regression/` | **89 M** | unchanged | the nominal-reproduction gate's output plus its comparison macro — **evidence** that the rebuilt producer reproduces the nominal (36.9 M values, identical digest). Keep; it is one raw file and is deliberately outside the production root so it can never be merged |
| `hadronization_production/HF_SYS_*` | **13 G** (137 of 2100 files) | **≈ 193 G** | ⛔ live production output. Not archivable, not movable |
| `systematics_20260817{,b,c}.bundle` | 3 × **56 M** | unchanged | git bundles used to transfer the branch. `…c` is the newest. **These ARE archivable** once the campaigns finish — they are reconstructible from the repo — and belong in `archive/bundles/` per §4 |

**The 193 GB is the number that matters for the merge-target headroom line in
§7.** Measured 2026-08-17 12:0x: **995 G available, 97 % used.** The systematics
program will consume roughly **19 %** of that headroom, which is what promotes
§7.1's physical consolidation from optional to load-bearing.

**One thing that must not be swept up**, in the spirit of §7.1's existing two:
`systematics_regression/HF_RUN3_V1/` looks like a stray duplicate of a promoted
campaign file and is not. It is a deliberate re-run of `MONASH` slot 0 at its
original seed, under a throwaway `HF_PRODUCTION_ROOT`, and it is the *evidence*
for the deployment gate. **Deleting it destroys the only artifact showing the
rebuilt producer is sound.**

---

## 7. WHAT THE OWNER RULED ON THESE FINDINGS — 2026-08-12

**The findings above reshaped the consolidation.** The rulings, and what each
does to this inventory:

| ruling | effect here |
|---|---|
| **no physical checkout move** | §1.1 finding 2 is answered by a **document**, not a `mv`. The 445 GB stays where it is; §2's "MOVE" tags on the big trees are **withdrawn** |
| **code/data separation by mapping** | the deliverable is a role → path table, not a directory tree. `docs/RESTRUCTURE_PLAN.md` §10.2 carries it |
| **big trees stay put** | `hadronization_production/` (304 G), `hadronization_analysis/`, `hadronization_merged/` (41 G), both checkouts: **no move** |
| **`b-hadron-fractions` out of scope** | §5's 1.2 TB finding is recorded and closed. Not this project's decision |
| **charm M7 logs** | **main line `scp`s `m7_runs/` after the MONASH harvest**, sha recorded beside the beauty anchors — closes `GOLDEN_OUTPUTS.md` N7 |
| **merge-target headroom** | **main line runs one `df`, records one line.** ~60 GB remains to be written. This session's reading, offered as a prior only: **1.1 T available, 97 % used**, 2026-08-12 |

### 7.1 What is left to do physically — under 1 GB

The whole physical component of the consolidation is now §4: the ~70 loose
top-level files into `scratch/misc/`, `scratch/deploys/` and `archive/bundles/`.

**Two things that must not be swept up in it:**

- the seven **scratch-deployed copies of committed tools** — that deploy pattern
  is deliberate, because the frozen checkout is read and never written;
- `producer_e54b27bb_HF_PT2.bak`, the backup of the binary whose sha is
  contract **C-3**.

### 7.2 What stays frozen regardless

1. `merge_runs/` — **until the band is scored.** The timing evidence is
   mtimes; clearing it destroys them (`GOLDEN_OUTPUTS.md` §5, N2).
2. `archive/` — the 34 breach partials, *moved, never deleted*.
3. `hadronization_analysis/**/per_job/` — do not walk it while the merge runs.
4. `sigmab_runs/task22` — holds the deployed reader the live chains execute.
5. `hadronization_merged/*.partial.*` — one is being written right now.

> **The reshape is the right outcome of the walk, and worth stating plainly:
> the inventory's job was to price the move, and the price is what killed it.**
> A 445 GB relocation across a 97 %-full NFS volume to make a directory listing
> more legible was never a good trade. A table that says which path is code and
> which is data costs nothing and buys the same thing.

---

## 8. ➕ REFRESHED 2026-08-17 — Consolidation A

**This document is now history plus a pointer.** The live layout is
[`docs/DATA_LAYOUT.md`](DATA_LAYOUT.md), which carries the consolidated root, the
path translation table and the current sizes. What changed since the 2026-08-12
walk:

### 8.1 The one gap in §0 is closed

§0 recorded, as a choice rather than an oversight, that `hadronization_analysis/`
had **no size**: walking it meant `readdir` on ~3000 live slot directories, which
under `relatime` would have corrupted the merge's frontier probe *and* reported
the walk itself as merge progress.

**The merge completed 2026-08-17 16:16 CEST. The walk is now safe, and it was
done: `hadronization_analysis/` is 94 G.**

### 8.2 What the numbers did

| tree | 2026-08-12 | 2026-08-17 | why |
|---|---|---|---|
| `hadronization_production/` | 304 G | **495 G** | +195 G of `HF_SYS_*`, against 193 G costed in advance |
| `hadronization_merged/` | 41 G | **88 G** | the JUNCTIONS and CLOSEPACKING merges landed |
| `hadronization_analysis/` | *not walked* | **94 G** | §8.1 |
| `Hadronization/` | 445 G | 445 G | unchanged — the checkout does not grow |
| free / used | 1.1 T / 97 % | **784–788 G / 98 %** | the systematics campaigns, in real time |

### 8.3 §7.1's physical component is DONE

§7.1 scoped the whole physical consolidation to "the ~70 loose top-level files,
under 1 GB". **Executed 2026-08-17: 79 files moved into
`/data/alice/ipardoza/hadronization/`,** with a before/after sha256 manifest pair
in which **all 82 files hash identically** — zero lost, zero altered.

Both of §7.1's "must not be swept up" items were respected: the seven
scratch-deployed tool copies went to `hadronization/scratch/deploys/` **as a
group, still outside the checkout**, and `producer_e54b27bb_HF_PT2.bak` (contract
**C-3**) went to `hadronization/archive/binaries/`. The three
`systematics_*.bundle` were deliberately **left at the top level** — §6.1 makes
them archivable only after the campaigns converge.

### 8.4 What §2.1 predicted, and what actually happened

§2.1 flagged `complete_root_HF_RUN3_V1_JUNCTIONS.partial.iHJ4n3` as **LIVE — the
merge is writing it now**, and warned that a sweep pattern-matching `*.partial.*`
would delete a running merge's output.

**The warning was never tested, because the merge finished the job properly:**
that partial no longer exists, `complete_root_HF_RUN3_V1_JUNCTIONS` does, and all
three tunes plus `SUBSAMPLES_HF_RUN3_V1` are complete. The rule stands for the
next merge; there was nothing to archive this time.

### 8.5 Still true, still frozen

`merge_runs/` (**N2** — the evidence is mtimes), `archive/` (the 34 breach
partials), `a2_runs/` (**25 G**, the E7 held evidence), the seed ledgers, and
`b-hadron-fractions/` at 1.2 T (**out of scope, untouched**).
