# Nikhef cleanup plan — `/data/alice/ipardoza`

**Walked 2026-08-19 from branch `systematics-harvest`. Owner rulings and the
seed-collision check applied the same day.**
This document is a plan. **This session deleted, moved, renamed and created
nothing on Nikhef.** The execution session runs the commands in §9 after the
preconditions in §2 hold.

This supersedes the classification in
[`docs/NIKHEF_DISK_INVENTORY.md`](NIKHEF_DISK_INVENTORY.md), which walked the
same volume on 2026-08-12, and which a later session refreshed on 2026-08-17.
That document stays as the history of how the consolidation got its price.
Sizes below are new measurements, not copies.

---

## 0. METHOD

**One `find` walk per tree.** Each walk reads `%b` (512-byte blocks) and `%T@`
(mtime) in a single pass, then aggregates size, file count, and the oldest and
newest mtime. One pass gives all four numbers, so each tree took one walk.

| deliberately done | why |
|---|---|
| **`hadronization_analysis/**/per_job/` WAS walked** | `docs/NIKHEF_DISK_INVENTORY.md` §0 refused this walk because `per_job` was the live merge's frontier probe. **It is not the live instrument now.** `per_job` for both running campaigns was last written **2026-08-18 09:49** and **09:53**; both merges are past the merging phase at 33/33 products and write only into `validation/`. The walk cost is NFS metadata load, and the merges are CPU-bound |
| walks run one at a time | the two merges hold `stbc-i3` and `stbc-i2`. No two heavy walks ran together |
| process queries scoped by user | `ps -u ipardoza`. The login nodes are shared — an unscoped query inventories other people's processes |

**Filesystem: `data-02:/alice`, 32 T, 914 G available, 98 % used.**

**Nothing was checksummed.** A checksum belongs to the move itself, where it has
a before/after pair. The exception is §8, where a checksum answered a question
about an archive that already exists.

---

## 1. THE HEADLINE

| class | size | what it is |
|---|---|---|
| **KEEP-PERMANENT** | **797.5 G** | raw campaign data, merged products behind published numbers, sealed evidence |
| **KEEP-UNTIL-ACCEPTED** | **410.6 G** | inputs a reviewer could ask us to regenerate from |
| **ARCHIVE-THEN-REMOVE-AFTER-ACCEPTANCE** | **67.3 G** | `RootFiles/{bbbar,ccbar}` — §4.3 |
| **ARCHIVE-THEN-REMOVE** | **17.7 G** | superseded outputs with provenance value |
| **REMOVE** | **1.1 G** | caches, empty directories, zero-byte files |
| **BLOCKED** | *(overlaps the above)* | held by the two running merges — §6 |
| *not this project* | *1305.6 G* | out of scope by the 2026-08-12 ruling, reaffirmed 2026-08-19 — §7.4 |

**Recoverable once the preconditions hold: 18.8 G.**
**Recoverable after acceptance: 496.7 G.**

**No entry is unclassified.** The owner answered every open question on
2026-08-19; §10 records the rulings.

### 1.1 The three findings that matter more than the space

**Finding 1 — a live script calls a path that does not exist.**
`extraction/pipeline/tune_chain.sh:63` runs
`bash /data/alice/ipardoza/tune_extract.sh`. The 2026-08-17 consolidation moved
that file into `hadronization/scratch/deploys/`. **It updated the translation
table and left the caller alone.** §5.1.

**Finding 2 — the seed gate does not record an archived campaign, and two of
its seeds were reissued. Neither reissue touches the paper.**
`config/burned_seeds.txt` holds **none** of the 500 seeds of
`HF_100M_primaryGround_ccbb_v1`. Two of those seeds were reissued, to
`HF_SMOKE2` and `HF_PT2`. **The sealed publication campaign `HF_RUN3_V1` and
all seven `HF_SYS_*` variations share no seed with it — the intersection is
empty for all eight.** §8.

**Finding 3 — the largest single reclaim candidate is contract-named and must
be kept.** `Hadronization/RootFiles/HF/` is **326.6 G** and is the `raw_base` of
`config/dataset_selector.json`'s **active** dataset row. The brief's rule
applies: a path named by a recipe is never a removal candidate. §4.2.

---

## 2. PRECONDITIONS — ALL FOUR MUST HOLD

Do not run any command in §9 until every line below is true. Check them in
order. Stop at the first that fails.

1. **Both campaigns closed.** `HF_SYS_MUF_UP` and `HF_SYS_PDF_CTEQ6L1` each read
   **33/33 products and 3/3 closure markers**. At 20:09 CEST on 2026-08-19 they
   read 33/33 with **1/3** and **0/3**. **Read the marker count, not the product
   count** — a campaign at 33/33 with 0 markers has not closed.
2. **The combination is complete.** `extraction/combine_per_class.py` exits 0.
   It refuses while any of the seven campaigns is missing.
3. **No live process holds the path.** Run the probe in §9.1. A PID gone without
   three markers is a death, not a completion.
4. ~~**The owner has answered the seed question in §8.**~~ **✅ MET
   2026-08-20.** Ruled: the collision is closed and no action is taken; §10.4
   carries the ruling and its basis. Nothing in §9 touches a seed ledger.
   **This precondition is discharged and does not need re-checking.**

---

## 3. THE INVENTORY

Sizes in GB, measured 2026-08-19. Counts are files plus directories.

### 3.1 The project's large trees

| path | size | files | oldest | newest | class |
|---|---|---|---|---|---|
| `hadronization_production/` | **495.4 G** | 64 077 | 2026-08-03 | 2026-08-17 | split — §3.2 |
| `Hadronization/` | **444.6 G** | 34 468 | 2026-03-28 | 2026-08-18 | **BLOCKED** — §3.3 |
| `hadronization_merged/` | **161.3 G** | 128 013 | 2026-08-03 | 2026-08-19 | split — §3.2 |
| `hadronization_analysis/` | **154.7 G** | 1 573 704 | 2026-08-03 | 2026-08-19 | split — §3.2 |
| `a2_runs/` | 24.6 G | 261 682 | 2026-08-13 | 2026-08-13 | **KEEP-UNTIL-ACCEPTED** — it holds the re-analysis behind a published systematic, whatever E7's disposition (owner ruling, §10.2) |
| `Hadronization-full-production/` | 5.5 G | 3 757 | 2026-07-30 | 2026-08-01 | **KEEP-PERMANENT** — holds the seed ledgers |
| `merge_runs/` | 4.3 G | 1 603 | 2026-08-05 | 2026-08-17 | **KEEP-PERMANENT** — the timing evidence is mtimes (N2) |
| `.vscodium-server/` | 1.08 G | 14 477 | 2024-07-24 | 2026-08-19 | **REMOVE** — editor cache, regenerates |
| `archive/` | 1.02 G | 10 270 | 2026-08-09 | 2026-08-09 | **KEEP-PERMANENT** — the 34 breach partials |

### 3.2 Inside the three campaign trees, by campaign

Every campaign appears in all three trees. The class follows the campaign, not
the tree.

| campaign | production | analysis | merged | total | class |
|---|---|---|---|---|---|
| `HF_RUN3_V1` | 271.4 G | 86.5 G | 79.5 G | **437.4 G** | **KEEP-PERMANENT** — the sealed nominal |
| `HF_SYS_*` (7) | 191.7 G | 61.1 G | 74.1 G | **326.9 G** | **KEEP-PERMANENT** — the systematics program |
| `HF_PT2_INT` | 27.0 G | 6.4 G | 6.7 G | **40.1 G** | **KEEP-UNTIL-ACCEPTED** — a selector row |
| `HF_PT2` | 2.7 G | 0.65 G | 1.0 G | **4.4 G** | **KEEP-UNTIL-ACCEPTED** — a selector row |
| `HF_SMOKE2` | 2.5 G | 0.0 G | — | **2.5 G** | **ARCHIVE-THEN-REMOVE** |
| `PTHAT2` | 0.09 G | — | — | **0.09 G** | **ARCHIVE-THEN-REMOVE** |
| `HF_SMOKE` | 0.0005 G | — | — | **0.0005 G** | **ARCHIVE-THEN-REMOVE** |

**The seven `HF_SYS_*` campaigns cost 326.9 G against 193 G costed in advance
for production alone.** The production figure was accurate: 191.7 G measured
against 193 G predicted. The prediction did not cover the analysis and merged
trees, which added 135.2 G.

**No `.partial.*` staging directory exists anywhere in `hadronization_merged/`.**
The 2026-08-12 warning about a sweep deleting a running merge's output has
nothing to match this time.

### 3.3 Inside the frozen checkout

| subtree | size | files | oldest | newest | class |
|---|---|---|---|---|---|
| `RootFiles/HF/` | **326.6 G** | 304 | 2026-06-26 | 2026-07-08 | **KEEP-UNTIL-ACCEPTED** — §4.2 |
| `RootFiles/bbbar/` | 46.9 G | 23 | 2026-03-28 | 2026-04-01 | **ARCHIVE-THEN-REMOVE-AFTER-ACCEPTANCE** — §4.3 |
| `RootFiles/ccbar/` | 20.4 G | 23 | 2026-03-28 | 2026-03-29 | **ARCHIVE-THEN-REMOVE-AFTER-ACCEPTANCE** — §4.3 |
| `RootFiles/Previous/` | 14.5 G | 7 | 2026-03-30 | 2026-04-01 | **ARCHIVE-THEN-REMOVE** |
| `.git/` | 22.0 G | 159 | 2026-03-28 | 2026-08-18 | **KEEP-PERMANENT** — the object store |
| `AnalyzedData/` | 6.0 G | 2 845 | 2026-03-28 | 2026-07-15 | **KEEP-UNTIL-ACCEPTED** — §4.2 |
| `AnalysisResults/` | 5.7 G | 25 207 | 2026-07-08 | 2026-07-14 | **KEEP-UNTIL-ACCEPTED** |
| `Production/` | 2.3 G | 290 | 2026-08-03 | 2026-08-03 | **KEEP-UNTIL-ACCEPTED** |
| `logs/` + `Logs/` | 0.18 G | 2 418 | 2026-03-28 | 2026-07-15 | **ARCHIVE-THEN-REMOVE** |
| tracked source and docs | 0.03 G | ~900 | 2026-05-01 | 2026-08-18 | **KEEP-PERMANENT** |

> **Advancing this checkout and moving it are operations of different cost.**
> Advancing is a ref update on a 22 G object store. Moving is 444.6 G across a
> 98 %-full NFS volume. The 2026-08-12 ruling killed the move for that reason
> and the reason has not changed.

### 3.4 The deploys and their outputs

| path | size | newest | class | identified in |
|---|---|---|---|---|
| `systematics_deploy/` | 0.13 G | 2026-08-17 17:16 | **KEEP-UNTIL-ACCEPTED** | §5.2 |
| `sys_plot_deploy/` | 0.079 G | 2026-08-19 16:03 | **KEEP-UNTIL-ACCEPTED** | §5.2 |
| `figure_deploy_20260817/` | 0.052 G | **2026-08-19 18:32** | **KEEP-UNTIL-ACCEPTED** | §5.2 |
| `hadronization_v3_plotting_run/` | 0.026 G | 2026-08-16 22:28 | **KEEP-UNTIL-ACCEPTED** | §5.2 |
| `systematics_harvest/` | 0.065 G | 2026-08-19 20:09 | **BLOCKED**, then KEEP-PERMANENT | §6 |
| `systematics_regression/` | 0.086 G | 2026-08-17 11:52 | **KEEP-UNTIL-ACCEPTED** | §5.3 |
| `sys_runs/` | 0.003 G | 2026-08-19 10:00 | **KEEP-UNTIL-ACCEPTED** | §4.1 |
| `measurements_v3/`, `sys_runs_plot5/` | 0.008 G | 2026-08-19 16:09 | **KEEP-UNTIL-ACCEPTED** | §4.1 |
| `measurements/`, `measurements_v2/`, `sys_runs_plot`…`plot4/` | 0.011 G | 2026-08-19 15:59 | **ARCHIVE-THEN-REMOVE** | superseded by `_v3`/`plot5` |

### 3.5 The scratch investigations

**All are ARCHIVE-THEN-REMOVE except the five named below.** Together they hold
**0.19 G** across 30 directories. Their value is provenance, not size: several
are cited by name in `docs/` as the basis for a measurement.

| keep this one | size | why |
|---|---|---|
| `m7_runs/` | 0.8 M | **the only copy of the charm-M7 block logs.** `GOLDEN_OUTPUTS.md` §5 N7. The beauty logs in `m7b_runs/` were anchored into git; these were not |
| `sigmab_runs/task22` | 6.6 M | held the deployed reader the tune chains execute |
| `species_axis_fixture/` | 88.4 M | the 900 files behind `SPECIES_AXIS_VALIDATION.md` |
| `f3_runs/` | 62.9 M | F3 virtual-trigger closure evidence |
| `fixcheck_20260818/` | 76.5 M | 2026-08-19 outputs, newer than this plan's survey of superseded work |

**`m7_runs/` is 840 KB and is the highest-value 840 KB on this disk.** Copy it
into git before anything else runs.

### 3.6 Loose files at the top level — 28 of them, 0.56 G

The 2026-08-17 consolidation moved 79 loose files into `hadronization/`. **28
new ones have accumulated since**, all from the systematics and plotting work of
2026-08-17 to 2026-08-19.

| group | count | size | class |
|---|---|---|---|
| `hadronization-history-20260819.bundle` | 1 | 399.0 M | **KEEP-PERMANENT** — the history bundle; §9.3 stores archives beside it |
| `systematics_20260817{,b,c}.bundle` | 3 | 167.0 M | **ARCHIVE-THEN-REMOVE** — reconstructible from the repo; §6.1 of the old inventory made them archivable only after convergence |
| `*.tgz` transfer bundles | 9 | 2.4 M | **ARCHIVE-THEN-REMOVE** |
| `tip2.bundle`, `tip3.bundle`, `harvest_tip.bundle` | 3 | 0.3 M | **ARCHIVE-THEN-REMOVE** |
| `render_*.sh` | 4 | 6 K | **ARCHIVE-THEN-REMOVE** — cited by GOLDEN_OUTPUTS §2.16 as the render path |
| `sys_runs_plot4_*.out` | 6 | **0 bytes** | **REMOVE** |
| `hadronization-campaign-…-20260819.tar.gz` | 1 | 11 K | **KEEP-PERMANENT** — §8 |

### 3.7 Empty and generated

| path | size | class | evidence |
|---|---|---|---|
| `ipardoza/` | **0 files** | **REMOVE** | a nested `/data/alice/ipardoza/ipardoza`, created 2026-08-19 20:00, empty. Almost certainly a relative-path accident from the same minute the campaign archive was written |
| `__pycache__/`, `tmp/`, `lib/`, `pthat_scan_8317/` | 4–12 K | **REMOVE** | byte-code or empty |
| `.vscodium-server/` | 1.08 G | **REMOVE** | editor server cache, active 2026-08-19 19:07, regenerates on next connect |

---

## 4. THE CONTRACT CROSS-CHECK

**Method.** This session extracted every `/data/alice/ipardoza/…` path from the
repository's `.md`, `.py`, `.sh`, `.json`, `.jsonl`, `.C`, `.yaml`, `.cfg` and
`.txt` files, with the file that names each one. That gives **271 unique
paths**. An existence check ran on Nikhef for all 271. **192 exist. 79 do not.**

**Most of the 79 are not broken contracts.** They fall into four groups.

| group | count | verdict |
|---|---|---|
| prose fragments my extraction truncated (`…/complete_root_HF_RUN3_V1_`, `…/m7_runs/block_`) | 14 | not a path |
| the 34 breach partials under `per_job/MONASH/slot_298…331.partial.*` | 34 | **correct.** `docs/campaigns/HF_RUN3_V1_PARTIALS_ARCHIVE.md` is the manifest that records moving them. Their absence is what the manifest asserts |
| files the 2026-08-17 consolidation moved, cited at their old path by **historical** handoffs | 15 | **correct.** `docs/DATA_LAYOUT.md` §3 is the translation table. Every one was found at its documented new location |
| **live references to paths that do not exist** | **2** | **§4.1 and §5.1** |

### 4.1 Every path a live recipe names, and whether it exists

| path | named by | exists |
|---|---|---|
| `hadronization_merged/` products for the 5 closed campaigns | `config/dataset_selector*.json`, 5 rows | **yes** |
| `sys_runs/HF_SYS_*/`, "165 directories" | `GOLDEN_OUTPUTS.md` §2.15 | **yes — exactly 165**, 5 campaigns × 33 |
| `sys_plot_deploy` as `HADRONIZATION_BASE` | `GOLDEN_OUTPUTS.md` §2.16 | **yes** |
| `measurements_v3` as the measurement root | `GOLDEN_OUTPUTS.md` §2.16 | **yes** |
| `Hadronization-full-production/campaigns/*/seed_ledger.jsonl` | `GOLDEN_OUTPUTS.md` | **yes**, 2 ledgers |
| `hadronization_v3_plotting_run` | all 3 committed boundary receipts | **yes** |
| `hadronization_merged/…/BplusBminus.root`, 11 paths | the 2026-08-13 MONASH receipt | **yes** |
| `Hadronization/config/burned_seeds.txt` | `tools/campaign.py` | **yes** — but see §8 |
| **`/data/alice/ipardoza/tune_extract.sh`** | **`extraction/pipeline/tune_chain.sh:63`** | **NO — §5.1** |
| `Hadronization/.git/checkout_pin` | `docs/ERROR_RECORD.md` E8 | **no, and correctly so** — the pin was retired when the checkout advance was taken on 2026-08-17. `hadronization/archive/gate_artifacts/checkout_pin.refreshed` holds the last copy |

**The dataset-selector rows are not broken.** They name the stem
`…/SUBSAMPLES_<CAMPAIGN>/combined_root_subSamples`, to which the resolver
appends the tune. All 30 resolved forms
(`combined_root_subSamples_{MONASH,JUNCTIONS,CLOSEPACKING}`) exist. A literal
`-e` test on the stem fails and means nothing.

**Two selector rows do not yet exist.** `HF_SYS_MUF_UP` and
`HF_SYS_PDF_CTEQ6L1` have no `config/dataset_selector_*.json`. That is expected
— they have not closed — and it is step 2 of the extraction work, not a cleanup
concern.

#

`config/dataset_selector.json` declares `"active_dataset":
"legacy_21_06_2026"`. That row sets `"raw_base": "RootFiles/HF"` and
`"subsample_base": "AnalyzedData/SUBSAMPLES_700/combined_root_subSamples"`,
both relative to the checkout. `analysis/run_hf_analysis.sh:72-74` and
`analysis/hf_mult_pt_analysis_multi.C:1127-1139` read
`${PROJECT_BASE}/RootFiles/HF/{MONASH,JUNCTIONS,CLOSEPACKING}`.

**All three tune directories exist and hold 326.6 G in 303 files.**
`AnalyzedData/SUBSAMPLES_700` exists.

### 4.2 The 326.6 G that a recipe protects

**The active dataset row protects the largest reclaim candidate on this disk.**
The row sets `publication_eligible` to `false`. Its `interpretation` field calls
the data a regression-only input, held as the default until a new canonical
manifest and Gates A-D validate. **The class is KEEP-UNTIL-ACCEPTED, not
REMOVE.** The 326.6 G becomes recoverable when the default selector moves off
the legacy row, and not before.

---

### 4.3 What reaches `RootFiles/{bbbar,ccbar}` — 67.3 G traced

**Searched: every GOLDEN_OUTPUTS recipe, every committed receipt, every
dataset-selector row, every freeze manifest, and the whole tracked tree.**

| source | result |
|---|---|
| `docs/GOLDEN_OUTPUTS.md` | **no mention of `bbbar` or `ccbar` anywhere in the file** |
| the three committed boundary receipts | name `hadronization_merged` and `hadronization_v3_plotting_run` only |
| `config/dataset_selector*.json` | every row's `raw_base` is `RootFiles/HF` or an absolute campaign path. **No row names `bbbar` or `ccbar`** |
| the four freeze manifests | name `raw/<TUNE>/…` under a campaign production root. **None reaches `RootFiles/`** |

**Four files read those directories, and all four are in the attic.**

| file | line |
|---|---|
| `attic/split_chain/cc_mult_pt_analysis_multi.C` | `:847`, `:853` — `RootFiles/ccbar/{MONASH,JUNCTIONS}` |
| `attic/split_chain/run_cc_analysis.sh` | `:66-67` |
| `attic/split_chain/run_bb_analysis.sh` | `:64-65` — `RootFiles/bbbar/{MONASH,JUNCTIONS}` |
| `analysis/Analysis_README.md` | `:14` — names the split reductions as superseded |

`README.md:238` and `RENAMES.md:106` both record why: **the split bbbar/ccbar
chain lives in `attic/split_chain/` and stays available for independent
reference.** The chain was superseded by `hf_mult_pt_analysis_multi.C`, which
reads `RootFiles/HF`.

**Verdict: no published number traces to `RootFiles/bbbar/` or
`RootFiles/ccbar/`.** Retaining the attic code is a decision about *code*; it
does not make 67.3 G of raw ROOT input a publication dependency.

**Reclassified ARCHIVE-THEN-REMOVE-AFTER-ACCEPTANCE.** They are not recoverable
now — acceptance could still send a reviewer to the superseded chain — and they
are recoverable then. This adds 67.3 G to §7.3.

## 5. THE DEPLOYS

### 5.1 The broken caller, and what depends on it

**`extraction/pipeline/tune_chain.sh:63` runs a file that does not exist.**

```
bash /data/alice/ipardoza/tune_extract.sh "$TUNE" >> "$LOG" 2>&1
```

`ls` on that path returns `No such file or directory`. **The deployed copy
carries the same dead path**, at line 50 of
`hadronization/scratch/deploys/tune_chain.sh`. So the chain is broken at both
the committed and the deployed location.

**The move preserved the bytes, and the consolidation's own manifests prove
it.** `MANIFEST_premove_20260817.sha256` records
`d6166302…  tune_extract.sh`; `MANIFEST_20260817.sha256` records
`d6166302…  scratch/deploys/tune_extract.sh`. **Same digest before and after —
only the path changed.** `tune_chain.sh` is `eae4c0ae…` in both.

**The deployed and committed copies of `tune_extract.sh` differ, and only in
comments.** Their file digests are `d6166302…` and `3ad2723a…`. With comments
and blank lines stripped, both hash to
**`5a7bc2391cf6121f4df815eed84cc57bb0ae9ea8f959d2775fffdb6f16e2a974`**. The
executable code is identical; the committed copy's E5 comment block was
reworded after the Nikhef copy was corrected in place.

#### What depends on the chain

**No regeneration recipe does, and that is stated in the contract rather than
inferred.** `GOLDEN_OUTPUTS.md` §2.9c records, for the three-tune central
table:

> inputs | **committed anchors** — the table regenerates from the repository
> alone. The remote run roots (`tune_runs_e5fix/MONASH/`,
> `tune_runs_three/{JUNCTIONS,CLOSEPACKING}/` on `stbc-i3`) produce the **same
> digest**, byte for byte, and are the origin rather than a dependency

`docs/COMPONENTS.md:177,181` draws the same line: `tune_extract.sh` is
**measurement-provenance** with its name frozen by `GOLDEN_OUTPUTS.md`, and
`tune_chain.sh` is an **operational tool**.

| question | answer |
|---|---|
| does a GOLDEN_OUTPUTS recipe re-run the chain? | **no** — `THREE_TUNE_CENTRAL_TABLE` and `MONASH_CENTRAL_TABLE` regenerate from committed anchors |
| does a receipt name a file the chain produced? | **no** — the boundary receipts name `hadronization_merged` and `hadronization_v3_plotting_run` |
| did the chain produce published numbers? | **yes** — it is their origin. `tune_runs_e5fix/MONASH/` and `tune_runs_three/…` are the run roots behind the per-tune tables |
| can a reviewer regenerate those numbers today? | **yes**, from the anchors, without the chain |
| can a reviewer re-run the extraction from the merged ROOT files? | **no** — that path invokes `tune_chain.sh` and fails at line 63 |

**So the defect is real and bounded.** Every published number regenerates
without the chain, so no result is unreproducible today. **But the route from
merged ROOT files back to those numbers cannot run as written, and that route is
the one a reviewer takes when the anchors themselves are the thing in
question.** It is a reproducibility defect at the second level of checking, not
untidiness, and §11.1 specifies the one-line correction.

**`tune_extract.sh` invoked directly is unaffected.** Only the
`tune_chain.sh` → `tune_extract.sh` hop uses the dead absolute path. `STATE.md`
§11's planned per-tune `tune_extract.sh` runs call it directly and still work.

### 5.2 What each deploy is

**Read `.git/HEAD` and the ref file directly. Do not run `git rev-parse`, and do
not trust a deploy's HEAD to describe its working files** — §20.11 of the run
record recorded exactly that trap.

| deploy | commit | pinned by a receipt? | reproducible by redeploy? | class |
|---|---|---|---|---|
| `systematics_deploy/Hadronization` | **`72ca4e39`** on `physics-focus` | yes — `docs/SYSTEMATICS.md` §9 pins this sha; every in-flight job verified it at startup | yes, from `systematics_20260817c.bundle` | **KEEP-UNTIL-ACCEPTED** |
| `sys_plot_deploy` | **`769e351`** on branch `tip3` | named by `GOLDEN_OUTPUTS.md` §2.16 as `HADRONIZATION_BASE` | yes, from `tip3.bundle` | **KEEP-UNTIL-ACCEPTED** |
| `figure_deploy_20260817` | **no `.git`** — unpacked from `figdeploy2.tgz` | its `plotting/Plots/…/multiplicity_boundary_receipt_v1.json` is the receipt | no — a tarball deploy carries no commit | **KEEP-UNTIL-ACCEPTED** |
| `hadronization_v3_plotting_run` | **no `.git`** | **yes — all three committed boundary receipts name this path** | no | **KEEP-UNTIL-ACCEPTED** |
| `measurements`, `_v2`, `_v3` | not a code deploy — measurement outputs | `_v3` is the §2.16 measurement root | yes, by re-render | `_v3` keep; `_v1`/`_v2` archive |

**`figure_deploy_20260817` was written during this read-only window, and the
owner has explained it.** Its `plotting/Plots/THnSparseCompleteRoot_HF_RUN3_V1/`
was rebuilt at **2026-08-19 18:32**, with a new
`multiplicity_boundary_receipt_v1.json` and a `.prelabelfix_20260819T182643`
backup of the previous directory.

**The merge session did this, working its own checklist.** It ran the
polished-reference re-render after the label corrections, and it produced
`8776a1ff…` and the new receipt. **That session has finished. It was not a
concurrent executor**, and this plan records no contention with it.

**So the 18:32 render is the reference figure, and the deploy is
KEEP-UNTIL-ACCEPTED.** Its `.prelabelfix_20260819T182643` backup holds the
superseded pre-label-fix render and is **ARCHIVE-THEN-REMOVE**.

### 5.3 The one deploy output that looks like a duplicate and is not

`systematics_regression/HF_RUN3_V1/` looks like a stray copy of a promoted
campaign file. **It is a deliberate re-run of `MONASH` slot 0, at its original
seed, under a throwaway production root.** It is the evidence that the rebuilt
producer reproduces the nominal. **Deleting it destroys the only artifact that
shows the deployment gate passed.** 88.4 M, 23 files.

---

## 6. BLOCKED — WHAT THE RUNNING MERGES HOLD

Verified from `/proc/<pid>/fd` on each merge's own host at 20:1x CEST.

| path | held by | evidence |
|---|---|---|
| `Hadronization/merging/merge_root_files.sh` | **both** merges, PIDs 3953522 and 642060 | open fd on both hosts |
| `Hadronization/Validation/validate_pair_block_closure.sh` | the closure legs | open fd, PID 2225131 |
| `systematics_harvest/merge_runs/merge_HF_SYS_MUF_UP.log` | PID 3953522 | open write fd |
| `systematics_harvest/merge_runs/merge_HF_SYS_PDF_CTEQ6L1.log` | PID 642060 | open write fd |
| `hadronization_merged/complete_root_HF_SYS_PDF_CTEQ6L1_MONASH/*` | PID 2225197 | open read fds on `pair_charm_trig_Dplus_assoc_Xiczero.root` |
| `hadronization_merged/SUBSAMPLES_HF_SYS_PDF_CTEQ6L1/…/combined_root_{1..10}/*` | PID 2225197 | open read fds |
| `hadronization_analysis/HF_SYS_PDF_CTEQ6L1/validation/.pair_block_closure_…9BYAUc` | PID 2225131 | **a live hidden staging file** |

> **⚠ A sweep that matches hidden or temporary names would break a running
> closure.** The closure validator stages its report as
> `validation/.pair_block_closure_<CAMPAIGN>_<TUNE>.XXXXXX` and promotes it at
> the end. This is the same class of mistake as deleting a `.partial.*`
> directory during a merge. **Match nothing by pattern while a merge runs.**

**`Hadronization/` is BLOCKED in whole** because both merges execute scripts
from it. Its subtree classification in §3.3 applies **after** both close.

**No directory is blocked by permissions.** `find -maxdepth 1 -type d
! -readable` returned nothing. The brief anticipated permission-blocked scratch
directories from an earlier run record; none exist on this volume now.

---

## 7. THE SPACE

### 7.1 By class

| class | size | share of the project's 1294.2 G |
|---|---|---|
| KEEP-PERMANENT | 797.5 G | 61.6 % |
| KEEP-UNTIL-ACCEPTED | 410.6 G | 31.7 % |
| ARCHIVE-THEN-REMOVE-AFTER-ACCEPTANCE | 67.3 G | 5.2 % |
| ARCHIVE-THEN-REMOVE | 17.7 G | 1.4 % |
| REMOVE | 1.1 G | 0.1 % |

### 7.2 Recoverable now

**18.8 G**, once §2's preconditions hold. That is **2.1 % of the 914 G
currently free** and it does not change the headroom picture.

| item | size |
|---|---|
| `RootFiles/Previous/` | 14.5 G |
| `hadronization_production/{HF_SMOKE2,HF_SMOKE,PTHAT2}` | 2.6 G |
| `.vscodium-server/` | 1.08 G |
| the 3 `systematics_*.bundle` | 0.17 G |
| `Hadronization/{logs,Logs}/` | 0.18 G |
| 30 scratch investigation directories | 0.19 G |
| loose `.tgz`, `.bundle`, `.sh`, `.out` | 0.01 G |
| `nikhef_stale_fullprod_20260730/`, `Hadronization-Tune-Integration/`, `HRP_clean/` | 0.03 G |
| superseded `measurements*`, `sys_runs_plot*` | 0.01 G |
| `ipardoza/`, `__pycache__/`, `tmp/`, `lib/`, `pthat_scan_8317/` | 0 G |

### 7.3 Recoverable after acceptance

**496.7 G** — the 18.8 G above, plus 410.6 G of KEEP-UNTIL-ACCEPTED, plus the
67.3 G of `RootFiles/{bbbar,ccbar}`. **`RootFiles/HF/` alone is 326.6 G**, which
is 65.8 % of everything acceptance unlocks. `RootFiles/` in total — `HF`,
`bbbar`, `ccbar` and `Previous` — is **408.4 G**, or 82.2 %.

**Acceptance is the only event that matters for space on this volume.** Every
cleanup short of it recovers under 2 % of free space.

### 7.4 Not this project

| path | size | files | newest |
|---|---|---|---|
| `b-hadron-fractions/` | **1200.9 G** | 51 517 | 2026-06-04 |
| `HRP/` | 72.7 G | 1 697 | 2025-12-01 |
| `Axions/` | 32.0 G | 343 700 | 2026-06-08 |

**1305.6 G, untouched for 2 to 20 months, on a volume with 914 G free.** The
2026-08-12 ruling put `b-hadron-fractions` out of scope. **The owner reaffirmed
that ruling on 2026-08-19.** These trees and the other users' trees stay out of
scope. They appear here to account for the volume, and for no other reason.
**No command in §9 touches them.**

---

## 8. THE SEED CHECK — THE PAPER IS CLEAN, THE GATE IS NOT

### 8.1 What was compared, and how

**Three sources, read three different ways.**

| source | what it is | extraction |
|---|---|---|
| `hadronization-campaign-…-20260819.tar.gz` | the archived campaign's ledger | `tar -xzOf` to stdout, then `grep -o '"seed": *[0-9]*'`. **Nothing was written to disk on Nikhef** |
| `Hadronization/campaigns/*/freeze/canonical_manifest.jsonl` | **the record of what ran** for `HF_RUN3_V1`, `HF_PT2_INT`, `HF_PT2`, `HF_SMOKE2` | the same `grep -o` on the `seed` field |
| `systematics_harvest/manifests/*/canonical_manifest.jsonl` | **the record of what ran** for the seven `HF_SYS_*` | the same |

**The manifests are the record. `burned_seeds.txt` is the gate.** They answer
different questions and §8.4 measures how far apart they are. The collision
check below uses the manifests, never the gate.

**The archived ledger is a faithful copy.** Its `seed_ledger.jsonl` is
byte-identical to the live copy under
`Hadronization-full-production/campaigns/HF_100M_primaryGround_ccbb_v1/` — both
sha256 `657dfab6b5016527bd1f056f070bc9b5fa86dd376cc9eae02b539f7cbe1fa02f`.

It records **500 seeds**: 100 MONASH, 200 JUNCTIONS, 200 CLOSEPACKING, matching
`campaign.json`'s `candidate_slots`. They run from **100000001 to 100499001**.

### 8.2 The intersection, per campaign

| campaign | seeds in its manifest | seed range | **shared with the archive** |
|---|---|---|---|
| **`HF_RUN3_V1`** — the sealed publication campaign | 3 000 | 130000001–132200746 | **0** |
| `HF_SYS_MUR_UP` | 300 | 140000001–142100071 | **0** |
| `HF_SYS_MUR_DOWN` | 300 | 150000001–152100072 | **0** |
| `HF_SYS_MUF_UP` | 300 | 160000001–162100100 | **0** |
| `HF_SYS_MUF_DOWN` | 300 | 170000001–172100093 | **0** |
| `HF_SYS_PDF_CTEQ6L1` | 300 | 180000001–182100005 | **0** |
| `HF_SYS_PTHAT_1` | 300 | 190000001–192100084 | **0** |
| `HF_SYS_PTHAT_4` | 300 | 200000001–202100098 | **0** |
| *`HF_PT2_INT`* | 300 | 100600001–102700084 | **0** |
| *`HF_PT2`* | 30 | 100400001–102400010 | **1** |
| *`HF_SMOKE2`* | 30 | 100200001–102300005 | **1** |

### 8.3 The verdict

**No published or variation campaign shares a seed with the archived campaign.**
`HF_RUN3_V1` and all seven `HF_SYS_*` return an empty intersection. That is the
answer to the question that touches the paper.

**Two early campaigns do share a seed. Both collisions are named below.**

| seed | archived campaign | the campaign that reissued it |
|---|---|---|
| **100200001** | `logical_id` 100, tune **JUNCTIONS**, attempt 0 | **`HF_SMOKE2`** `logical_id` 0, tune **MONASH**, attempt **2**, `raw/MONASH/hf_MONASH_job000.root`, cluster `5282987` |
| **100400001** | `logical_id` 100, tune **CLOSEPACKING**, attempt 0 | **`HF_PT2`** `logical_id` 0, tune **MONASH**, attempt **4**, `raw/MONASH/hf_MONASH_job000.root`, cluster `5290145` |

**Two further seeds, 100000001 and 100100001, appear in `burned_seeds.txt` under
`HF_SMOKE` and `HF_SMOKE2` but in no canonical manifest.** The gate burned them
at render; no job promoted them. They record superseded attempts, not data.

**This session does not assess the physics impact of either collision.** The
owner rules on impact. The thread stops here.

**The cause is measured, not guessed: three campaigns share one
`campaign_ordinal`.**

| ordinal | campaigns | first seed |
|---|---|---|
| **1** | **`HF_100M_primaryGround_ccbb_v1`, `HF_PT2`, `HF_SMOKE2`** | 100000001, 100400001, 100200001 |
| 2 | `HF_PT2_INT` | 100600001 |
| 3 | `HF_RUN3_V1` | 130000001 |
| 4–10 | the seven `HF_SYS_*` | 140000001 … 200000001 |

**The ordinal selects the seed band, so a shared ordinal is a shared band.**
Campaigns at ordinals 1 and 2 all allocate inside `1000xxxxx`. There, the
archived campaign put `logical_id` in the same digits the smoke campaigns used
for `attempt`. **From ordinal 3 onward each campaign holds its own ten-million
band.** No campaign from `HF_RUN3_V1` forward can collide with anything before
it, so construction closes the defect for every campaign the paper uses.

### 8.4 The gap between the gate and the record

| | seeds |
|---|---|
| the gate — `config/burned_seeds.txt` | **5 727**, all unique, across **12 campaigns** |
| the record — the 11 canonical manifests | **5 460** |
| **burned but never promoted** | **267** |
| the archived campaign, in the record | 500 |
| **the archived campaign, in the gate** | **0** |

Per campaign, the burned count minus the promoted count:

| campaign | gate | record | burned, not promoted |
|---|---|---|---|
| `HF_RUN3_V1` | 3 127 | 3 000 | 127 |
| `HF_SMOKE2` | 61 | 30 | 31 |
| `HF_SMOKE` | 30 | *no manifest* | 30 |
| `HF_SYS_MUR_DOWN` | 315 | 300 | 15 |
| `HF_SYS_PTHAT_1` | 313 | 300 | 13 |
| `HF_SYS_MUF_UP` | 312 | 300 | 12 |
| `HF_SYS_MUR_UP` | 310 | 300 | 10 |
| `HF_SYS_MUF_DOWN` | 310 | 300 | 10 |
| `HF_SYS_PTHAT_4` | 309 | 300 | 9 |
| `HF_PT2_INT` | 308 | 300 | 8 |
| `HF_SYS_PDF_CTEQ6L1` | 301 | 300 | 1 |
| `HF_PT2` | 31 | 30 | 1 |

**The 267 are retries, and the gate is right to hold them.** A seed burned at
render must never be reissued, whether or not its job succeeded.

**The gate under-records in one direction only: it has no entry for the archived
campaign at all.** 500 seeds sit in the record and none in the gate. §10.4
carries the owner's ruling on what to do about that.

---

## 9. THE COMMANDS THE EXECUTION SESSION RUNS

**Run §9.1 first. If it fails, stop.**

### 9.1 The precondition probe

```bash
M=/data/alice/ipardoza/hadronization_merged
W=/data/alice/ipardoza/systematics_harvest
for C in HF_SYS_MUF_UP HF_SYS_PDF_CTEQ6L1; do
  n=0
  for T in MONASH JUNCTIONS CLOSEPACKING; do
    [ -d "$M/complete_root_${C}_${T}" ] && n=$((n+1))
    for i in $(seq 1 10); do
      [ -d "$M/SUBSAMPLES_${C}/combined_root_subSamples_${T}/combined_root_${i}" ] && n=$((n+1))
    done
  done
  echo "$C products=$n/33 markers=$(grep -c CANONICAL_PAIR_BLOCK_CLOSURE_PASS $W/merge_runs/merge_${C}.log)"
done
ps -u ipardoza -o pid,pgid,stat,etime,args | grep -E 'merge_root_files|validate_pair_block' | grep -v grep
```

**Proceed only when both campaigns read `products=33/33 markers=3`.** The `ps`
line must also come back empty on `stbc-i1`, `stbc-i2` and `stbc-i3`.

**Count by these exact names, never by a glob.** A glob also matches
`.partial.XXXXXX` staging directories, and reports unpromoted work as complete.

### 9.2 Copy the irreplaceable thing into git first

```bash
scp -J nikhef -r ipardoza@stbc-i1.nikhef.nl:/data/alice/ipardoza/m7_runs /tmp/m7_runs
```

Then commit it under `docs/history/` beside the beauty anchors, with its
sha256 recorded. **This closes `GOLDEN_OUTPUTS.md` §5 N7 and must happen before
any removal.**

### 9.3 Archive, then verify, then remove

**The archive destination is `/data/alice/ipardoza/hadronization/archive/`**,
the root the 2026-08-17 consolidation established. §10.3 records the one
question this raises.

For each ARCHIVE-THEN-REMOVE item, in this order:

```bash
cd /data/alice/ipardoza
A=hadronization/archive/superseded_20260820
mkdir -p "$A"

# 1. archive
tar -czf "$A/rootfiles_previous.tar.gz" -C Hadronization/RootFiles Previous
# 2. checksum the archive AND its source
sha256sum "$A/rootfiles_previous.tar.gz" > "$A/rootfiles_previous.tar.gz.sha256"
find Hadronization/RootFiles/Previous -type f -exec sha256sum {} \; > "$A/rootfiles_previous.premove.sha256"
# 3. verify the archive reads back
tar -tzf "$A/rootfiles_previous.tar.gz" > /dev/null && echo ARCHIVE_READABLE
# 4. only then remove
rm -rf Hadronization/RootFiles/Previous
```

Repeat for `hadronization_production/{HF_SMOKE,HF_SMOKE2,PTHAT2}`,
`Hadronization/{logs,Logs}`, the 30 scratch directories, the three
`systematics_*.bundle`, the loose `.tgz` and `.sh` files, and the superseded
`measurements`, `measurements_v2`, `sys_runs_plot`…`sys_runs_plot4`.

**Do not compress the ROOT trees expecting a gain.** ROOT files are already
compressed. The archive is for provenance, not for space, and
`RootFiles/Previous` will occupy roughly its 14.5 G inside the tarball. **Write
the tarball only if the owner answers §10.2 with "archive it"; otherwise remove
without archiving and record the removal in a manifest.**

### 9.4 After acceptance only

**Do not run this step with §9.3.** `RootFiles/{bbbar,ccbar}` are
ARCHIVE-THEN-REMOVE-**AFTER-ACCEPTANCE** (§4.3): no published number traces to
them, but a reviewer could still be sent to the superseded split chain before
acceptance.

```bash
cd /data/alice/ipardoza
A=hadronization/archive/superseded_after_acceptance
mkdir -p "$A"
for d in bbbar ccbar; do
  find "Hadronization/RootFiles/$d" -type f -exec sha256sum {} \; > "$A/rootfiles_$d.premove.sha256"
  tar -czf "$A/rootfiles_$d.tar.gz" -C Hadronization/RootFiles "$d"
  tar -tzf "$A/rootfiles_$d.tar.gz" > /dev/null && rm -rf "Hadronization/RootFiles/$d"
done
```

**`attic/split_chain/` stays in git.** The ruling retires the 67.3 G of input,
not the code that reads it.

### 9.5 Remove without archiving

No item in this step carries provenance value.

```bash
cd /data/alice/ipardoza
rmdir ipardoza                      # empty, created 2026-08-19 20:00
rm -f sys_runs_plot4_*.out          # six zero-byte files
rm -rf __pycache__ tmp lib pthat_scan_8317
rm -rf .vscodium-server             # editor cache; regenerates on next connect
```

### 9.6 What must not be swept up

| item | why |
|---|---|
| `hadronization/scratch/deploys/` | the deploy pattern is deliberate — the frozen checkout is read, never written. **Do not consolidate these back into the checkout** |
| `hadronization/archive/binaries/producer_e54b27bb_HF_PT2.bak` | the backup of the binary whose sha is contract **C-3** |
| `systematics_regression/HF_RUN3_V1/` | §5.3 — not a duplicate |
| `merge_runs/` | the merge timing evidence **is** the mtimes (N2). Clearing it destroys them |
| `archive/` | the 34 breach partials; moved, never deleted |
| `a2_runs/` | E7 held evidence, 24.6 G |
| `hadronization_merged/*.partial.*` and `…/validation/.pair_block_closure_*` | live staging names — §6 |
| `m7_runs/` | until §9.2 has committed it |
| `Hadronization/RootFiles/HF/`, `AnalyzedData/SUBSAMPLES_700` | the active dataset row — §4.2 |

---

## 10. THE OWNER RULINGS, APPLIED

**Every question §10 raised on 2026-08-19 has an answer. None is open.**

### 10.1 The figure deploy — explained

The 18:26–18:32 writes were the merge session working its checklist: the
polished-reference re-render after the label corrections, which produced
`8776a1ff…` and a new receipt. **That session has finished, and it was not a
concurrent executor.** §5.2 records it. `figure_deploy_20260817` is
KEEP-UNTIL-ACCEPTED; its `.prelabelfix_20260819T182643` backup is
ARCHIVE-THEN-REMOVE.

### 10.2 `a2_runs` — KEEP-UNTIL-ACCEPTED

**Ruled: `a2_runs` holds the re-analysis behind a published systematic,
whatever E7's disposition.** It moves from KEEP-PERMANENT to
KEEP-UNTIL-ACCEPTED. 24.6 G, 261 682 files. It is not recoverable now, and it
is recoverable on acceptance.

### 10.3 The archive destination

**Ruled: archives go to `hadronization/archive/` on Nikhef, and
`hadronization-history-20260819.bundle` stays where it is** at the top level.
§9.3 already writes to that destination and needs no change. The history bundle
is KEEP-PERMANENT and no command moves it.

### 10.4 The 496 unburned seeds

§8.3 answers the question the paper cares about. **No publication or variation
campaign shares a seed with the archived campaign.** The two collisions belong
to `HF_SMOKE2` and `HF_PT2`.

**✅ RULED 2026-08-20: the seed collision is CLOSED, and no action is taken.**

The ruling rests on what §8.3 measured, not on a judgement about tolerance:

- **No campaign the paper uses is involved.** `HF_RUN3_V1` and all seven
  `HF_SYS_*` return an **empty** intersection with the archived campaign.
- **The two collisions belong to smoke campaigns.** Seed `100200001`
  (`HF_SMOKE2`, attempt 2) and `100400001` (`HF_PT2`, attempt 4). Neither
  campaign produces a published number.
- **Construction closes it going forward.** `HF_100M`, `HF_PT2` and `HF_SMOKE2`
  share `campaign_ordinal` 1, and the ordinal selects the seed band. **From
  ordinal 3 — `HF_RUN3_V1` — onward each campaign holds its own ten-million
  band**, so no campaign from the sealed one forward can collide with anything
  before it.

**The 500 archived seeds are NOT appended to the gate.** Appending them would
edit a ledger to record something that never burned, and the gate's meaning is
"burned at render". The mechanical point survives the ruling and stays on
record: if a future campaign ever needs those seeds withheld, append them
**through `tools/campaign.py`, never by hand**.

**The defect that caused it is separately recorded**, because closing the
collision does not close the mechanism — see §11.3.

### 10.5 The other users' trees

**Ruled: `b-hadron-fractions/`, `HRP/` and `Axions/` stay out of scope.** §7.4
records their 1305.6 G to account for the volume. No command in §9 touches them.

### 10.6 `RootFiles/{bbbar,ccbar}` — traced and reclassified

See §4.3.

### 10.7 The default dataset-selector row

This is no longer a question. It is a **specified change**, in §11.2.

---

## 11. SPECIFIED CHANGES — WRITTEN OUT, NOT APPLIED

**Neither change is applied. The two merges read the frozen checkout, and this
session is read-only.** Each is specified so a later session executes it without
re-deriving anything.

### 11.1 The broken chain call

**Change.** In `extraction/pipeline/tune_chain.sh`, line 63:

```diff
-bash /data/alice/ipardoza/tune_extract.sh "$TUNE" >> "$LOG" 2>&1
+bash /data/alice/ipardoza/hadronization/scratch/deploys/tune_extract.sh "$TUNE" >> "$LOG" 2>&1
```

**Apply the same one-line change to the deployed copy**,
`hadronization/scratch/deploys/tune_chain.sh` line 50, which carries the same
dead path.

**Rationale.** §5.1. The 2026-08-17 consolidation moved the target and left the
caller alone.

**Test.** Assert that every absolute path `tune_chain.sh` invokes exists in the
deploy layout. A path-existence assertion over the script's `bash <path>` lines
fails today and passes after the change.

**Do not fix it by recreating `/data/alice/ipardoza/tune_extract.sh`.** That
would undo the consolidation the translation table documents.

### 11.2 The default dataset-selector row must refuse

**Change.** `config/dataset_selector.json` currently sets `"active_dataset":
"legacy_21_06_2026"`, a row whose `publication_eligible` is `false`. **Make the
resolver refuse when no dataset is named, instead of falling back to that row.**

**Rationale, and it is not hypothetical.** A silent default is what let five
variation renders read the central campaign.

**A resolver that answers a question nobody asked will answer it wrongly.** The
wrong answer then looks exactly like a right one. The render succeeds, emits all
its rows, and reports the wrong dataset. **A default that cannot be wrong beats
a default that is usually right.**

**Specification.**

1. Remove `active_dataset` as a fallback, or set it to `null`.
2. When `DATASET_SELECTOR` names no dataset, the resolver raises and names
   every dataset key it would accept.
3. The legacy row stays in the file. It stays selectable **by name**. Only the
   silent fallback goes.

**Test.** Two cases, both mutations of the resolver's contract:

- resolving with no dataset named raises. The message lists the valid keys.
- resolving `legacy_21_06_2026` **by name** still succeeds, so the regression
  path stays open.

**Sequencing.** Do not apply this while the merges run. It changes a file the
frozen checkout resolves against.

---

### 11.3 The seed band derives from a non-unique `campaign_ordinal`

**Specified, not implemented, and the reason is that nothing needs it.**

**The defect.** `campaign_ordinal` selects the seed band, and it is not unique.
§8.3 measured three campaigns sharing ordinal 1 —
`HF_100M_primaryGround_ccbb_v1`, `HF_PT2` and `HF_SMOKE2` — and a shared ordinal
is a shared band. That is what produced the two collisions §10.4 closes.

**Why it is specified rather than fixed.** Two reasons, and the second is the
binding one:

1. **Construction already closed it for every campaign the paper uses.** From
   ordinal 3 onward each campaign holds its own ten-million band.
2. **No further production is planned.** `STATE.md` records the campaign as
   sealed and `docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md` promotes it to
   `canonical`. A seed-allocation change with no campaign to allocate for is a
   change with no test that exercises it end to end.

**The change, when a campaign next needs one.** Make the ordinal unique at
allocation rather than trusting a caller to pass a fresh one: derive the band
from a registry of issued ordinals and **refuse** an ordinal already recorded,
in `tools/campaign.py`'s `seed_for()` path, next to the existing
`assert_seeds_unused` guard that caught B15b at render.

**The test, specified with it.** Two cases, both mutations of the guard:

- allocating a band for an ordinal already present in the registry **raises**,
  and the message names the campaign that holds it;
- allocating for a fresh ordinal succeeds and returns a band disjoint from every
  recorded band.

**The mutation that must fail the test:** remove the refusal and allocate the
duplicate ordinal anyway. The second case still passes; the first must not.
Without that mutation the test cannot distinguish a working guard from an absent
one — which is the shape `docs/ERROR_RECORD.md` E8 records for guards that pin
an identity without saying what it means.

**What it unlocks.** The legacy row protects `RootFiles/HF/`'s 326.6 G (§4.2).
**The decision to move the default off that row is what makes the largest
directory on this volume recoverable.**

---

## 12. WHAT THIS SESSION DID AND DID NOT DO

**Did:** 271 path existence checks, 11 tree walks, 2 process probes, 1 archive
read, 12 canonical-manifest seed extractions, and 3 checksum comparisons. All
reads.

**Did not:** delete, move, rename, or create anything on Nikhef. Run no git
command on the Nikhef checkout. Stop, restart or re-plan either merge. Arm no
waiter. Extract nothing. Start no counter re-analysis.

**Processes started on the cluster: none.** Every cluster call was a read.
**Terminated: none.** `pkill -f` was not used, and every process query was
scoped with `ps -u ipardoza`.

**Left alive and not this session's to touch:** the two merges, PIDs 3953522 on
`stbc-i3` and 642060 on `stbc-i2`.

---

## 13. EXECUTED RECORD — 2026-08-20

**The execution session ran §7.2 on 2026-08-20 from `stbc-i1.nikhef.nl`.** It
removed 46 paths and 19 952 443 392 bytes, or 18.58 GiB. It ran no git command
on the Nikhef checkout. Records:
[`removal_manifest_20260820.tsv`](nikhef_cleanup_20260820/removal_manifest_20260820.tsv),
[`removal_log_20260820.tsv`](nikhef_cleanup_20260820/removal_log_20260820.tsv),
[`premove_sha256_20260820.txt`](nikhef_cleanup_20260820/premove_sha256_20260820.txt),
[`targets.txt`](nikhef_cleanup_20260820/targets.txt). The same four files are on
the cluster in `hadronization/archive/cleanup_20260820/`.

### 13.1 The preconditions, measured

| precondition | check | result |
|---|---|---|
| 1 — both campaigns closed | the §9.1 probe on `stbc-i1` | `HF_SYS_MUF_UP products=33/33 markers=3`; `HF_SYS_PDF_CTEQ6L1 products=33/33 markers=3` |
| 2 — the combination is complete | re-ran `extraction/combine_per_class.py` against `docs/systematics_results_20260820/per_class_deltas_seven.json` | exit 0, `COMBINED cells=144 separation_exceeds_systematic=113/144`. The output reproduces sha256 `8a8a26b8e676…0cfc57`, which is §12's recorded digest. All seven campaigns present |
| 3 — no live process holds the path | `ps -u ipardoza` on `stbc-i1`, `stbc-i2`, `stbc-i3`; `condor_q` | no match on any node. Zero condor jobs for `ipardoza` |
| 4 — the seed question | discharged by §10.4 on 2026-08-20 | not re-opened |

**Both merges of §6 have finished.** The marker count is 3 of 3 for each
campaign, so each merge completed rather than died. `Hadronization/` is no
longer BLOCKED, and this session removed its `logs/` and `Logs/` on that basis.

### 13.2 What went, by group

Sizes are `du -sB1` in bytes, measured before the removal.

| group | paths | bytes | GiB | §7.2 predicted | removed |
|---|---|---|---|---|---|
| `Hadronization/RootFiles/Previous` | 1 | 15 558 979 584 | 14.49 | 14.5 G | yes |
| `hadronization_production/{HF_SMOKE,HF_SMOKE2,PTHAT2}` | 3 | 2 813 153 280 | 2.62 | 2.6 G | yes |
| `.vscodium-server` | 1 | 1 163 640 832 | 1.08 | 1.08 G | yes |
| the 3 `systematics_*.bundle` | 3 | 175 775 744 | 0.164 | 0.17 G | yes |
| `Hadronization/{logs,Logs}` | 2 | 196 960 256 | 0.183 | 0.18 G | yes |
| `nikhef_stale_fullprod_20260730`, `Hadronization-Tune-Integration`, `HRP_clean` | 3 | 30 076 928 | 0.028 | 0.03 G | yes |
| superseded `measurements`, `measurements_v2`, `sys_runs_plot`…`plot4` | 6 | 10 981 376 | 0.0102 | 0.01 G | yes |
| loose `.tgz`, `.bundle`, `.sh`, `.out` | 23 | 2 850 816 | 0.0027 | 0.01 G | yes |
| `__pycache__`, `tmp`, `lib`, `pthat_scan_8317` | 4 | 24 576 | 0.00002 | 0 G | yes |
| `ipardoza` | 1 | 0 | 0 | 0 G | **no — absent before the session started** |
| **30 scratch investigation directories** | 0 | — | — | 0.19 G | **no — §13.4** |
| **total** | **46** | **19 952 443 392** | **18.58** | 18.8 G | |

**18.58 GiB removed plus 0.19 G not removed equals 18.77 G**, which is §7.2's
18.8 G headline. Every group matches its §7.2 figure.

### 13.3 The loose files, and the count §3.6 got wrong

**§3.6 counts 9 `*.tgz` transfer bundles. The disk held 10.** §3.6's own total
of 28 loose files proves 10 is right. Its other groups account for 18:

- 1 history bundle;
- 3 `systematics_*` bundles;
- 3 tip bundles;
- 4 `render_*.sh`;
- 6 `sys_runs_plot4_*.out`;
- 1 campaign `.tar.gz`.

28 minus 18 is 10. The session removed all 10.

**Three loose files postdate the 2026-08-19 walk and stayed.**
`campaign_closure_status.py`, `extract_final_two.out` and
`render_measure_v4.sh` carry 2026-08-20 mtimes. They are not in §7.2. A
wildcard sweep of `render_*.sh` would have destroyed `render_measure_v4.sh`,
which is work from the day of execution.

### 13.4 The 30 scratch directories were not removed

**§7.2 asks for 30 scratch investigation directories at 0.19 G, and no document
names them.** §3.5 defines the set as every scratch investigation except five,
but it does not list the members. The superseded
[`NIKHEF_DISK_INVENTORY.md`](NIKHEF_DISK_INVENTORY.md) §3 names 24 scratch
directories that total about 0.029 G, of which 20 fall outside §3.5's five
keeps. **Neither document yields 30 directories or 0.19 G.**

**Building the list needs a judgement this session was not authorised to make.**
The unclassified candidates include `tune_runs_e5fix/` and `tune_runs_three/`,
which §5.1 identifies as the run roots behind the published per-tune tables, and
`seed_ledger_archive/`. The session left all of them and reports the gap.

**To close this, name the 30 directories in §7.2.** A later session can then
remove them without re-deriving the set.

### 13.5 The space did not come back

**The volume reported no reclaim.** `df -B1 /data/alice` read
1 035 838 947 328 bytes available at 12:29 CEST, before the first removal. It
read 1 035 647 909 888 bytes at 12:52 CEST, after the last. **Available space
fell by 191 037 440 bytes. It did not rise by 18.58 GiB.**

**Other users' writes explain the fall, and they do not explain the missing
18.58 GiB.** Eight `df` samples at 45-second spacing between 12:45 and 12:50
show available space falling at about 9 MB per minute, with no step. Over the
23 minutes of the session that drift is about 200 MB, which matches the observed
191 MB. **No sample shows the 18.58 GiB returning.**

**The removal is verified in the namespace.** All 46 targets read absent after
the session. `Hadronization/RootFiles/` now measures 422 971 912 192 bytes, or
393.9 GiB, which is exactly §3.3's `HF` plus `bbbar` plus `ccbar` and no
`Previous`.

**Three client-side causes were tested and eliminated:**

- `/data/alice` exposes no `.snapshot` directory;
- `find -name '.nfs*'` returns nothing, so no silly-renamed file stays open;
- no `ipardoza` process runs on any login node, so nothing holds a deleted
  inode.

**The most likely cause is server-side deferred reclaim on the `data-02` filer**,
either through snapshots that hide their directory from clients or through
asynchronous accounting. **This session could not confirm it from the client.**
**Re-read `df` after 24 to 48 hours. If the 18.58 GiB has not appeared, ask the
Nikhef storage administrators whether a snapshot holds it.**

### 13.6 The guards held

| guard | before | after |
|---|---|---|
| `hadronization-history-20260819.bundle` | 418 360 432 bytes, sha256 `483ac5e9dc7a685b32c65ee05a71c8cceab2846e2e982f15783486e767d7525a` | **identical, both** |
| `b-hadron-fractions/` | 1 251 767 451 648 bytes | **1 251 767 451 648 — unchanged** |
| `HRP/` | 78 076 895 232 bytes | **78 076 895 232 — unchanged** |
| `Axions/` | 34 386 669 568 bytes | **34 386 669 568 — unchanged** |

**`HRP_clean/` went and `HRP/` stayed.** The two names differ by one token. The
session named every target literally and expanded no wildcard across either
name. The tripwire group reclaimed 30 076 928 bytes, or 0.028 G, against a limit
of 1 G.

**Every KEEP class survives.** `Hadronization/RootFiles/{HF,bbbar,ccbar}`,
`measurements_v3`, `measurements_v4`, `sys_runs_plot5`, `sys_runs_plot6`,
`m7_runs`, `sigmab_runs`, `species_axis_fixture`, `f3_runs`,
`fixcheck_20260818` and all ten remaining `hadronization_production/` campaigns
read present after the session.

### 13.7 Dead and out of scope — reported, not touched

**The session removed none of the following.** Each is a candidate for a later
§7.2 revision. §7.2 authorises none of them now.

| path | why it looks dead | why it stayed |
|---|---|---|
| the 30 scratch investigation directories | §3.5 classes them ARCHIVE-THEN-REMOVE | §13.4 — no document names them |
| `figure_deploy_20260817/plotting/Plots/…/.prelabelfix_20260819T182643` | §5.2 classes the pre-label-fix render ARCHIVE-THEN-REMOVE | §7.2 does not list it |
| `measurements_v3/`, `sys_runs_plot5/` | `measurements_v4/` and `sys_runs_plot6/` appeared on 2026-08-20 and supersede them | §7.2 lists them as the current roots. The plan predates them |
| `extract_final_two.out` | zero bytes, the same shape as the six `sys_runs_plot4_*.out` files | written 2026-08-20, after the walk. Not in §7.2 |
| `Axions_pre_update_conflicts_20260607_5cfe918/` | a conflict backup from 2026-06-07 | §10.5 puts the Axions trees out of scope |

### 13.8 What this session did not do

**Did not:** remove the 30 scratch directories. Archive anything — the brief
selected §9.3's manifest branch, so the session recorded every removed file
instead of writing tarballs. Run §9.2, which copies `m7_runs/` into git; the
directory is a §3.5 keep and no removal touched it. Run §9.4, which needs
acceptance. Apply §11.1, §11.2 or §11.3. Run any git command on the Nikhef
checkout. Touch `b-hadron-fractions/`, `HRP/` or `Axions/`.

**Processes started on the cluster: none beyond the reads, removals and `df`
samples above. Terminated: none.**
