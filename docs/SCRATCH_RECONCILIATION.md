# Scratch reconciliation — every deployed copy, sha-verified

**Walked 2026-08-17, Consolidation A.** Every deployed or scratch copy on
`/data/alice/ipardoza` compared by sha256 against tracked content, and disposed
of by the rule: **MATCHES tracked → archive with a manifest; DIFFERS → commit if
it produced published results, else archive with the diff recorded.**

**Nothing was deleted.** Content reads only; the one write is the anchor commit
`56e013a`.

> **Method note.** "MATCHES tracked" is checked against *content*, not path. The
> 2026-08-12 restructure moved most of these files, and the Nikhef checkout was
> still at the pre-restructure `43e35be8` while this ran, so a path-based
> comparison would have reported almost everything missing. Each deployed file
> was therefore hashed and looked up against every blob at `HEAD`, at
> `43e35be8`, and — where neither matched — across the last 400 commits.

---

## 0. "BOTH NODES" IS ONE FILESYSTEM — checked, not assumed

The brief asked for every deployed copy **on both nodes**. Measured:

| | `stbc-i1` | `stbc-i3` |
|---|---|---|
| `/data/alice` | `data-02:/alice`, 32 T | **the same NFS mount** |
| `$HOME` | `/user/ipardoza` | `/user/ipardoza` — also shared |
| node-local project data | none | none |
| node-local leftovers | none | `/tmp/ipardoza_hadd_test` — **empty**, dir only, Jul 15 |

**There is one scratch area, not two**, so this reconciliation covers both nodes
by covering `/data/alice/ipardoza` once. The only node-local artifact anywhere is
an empty directory on `i3`'s `/tmp`, which a reboot clears anyway.

> **Reaching `i1` is not the same invocation as `i3`.** The `stbc` alias resolves
> to `stbc-i3` and carries a `RemoteCommand`; `i1` has no alias, is not
> resolvable by short name, and `ssh i1` *from* `i3` is refused by publickey.
> What works:
> `ssh -o ProxyJump=nikhef -o RemoteCommand=none ipardoza@stbc-i1.nikhef.nl`.

---

## 1. THE HEADLINE

**Of everything deployed to scratch, exactly two files differ from tracked
content in a way that is not explained by a commit, and neither is a defect.**
Eleven further files matched *nothing* tracked; all eleven sat behind published
numbers and are now committed as anchors (`56e013a`).

| verdict | count | disposition |
|---|---|---|
| matches tracked content exactly | 40 files + 2 full trees | archive with manifest |
| matches an **older** tracked version, superseded by the advance | 2 | archive; the advance supersedes them |
| differs, but the difference is **comment-only** | 1 | archive with the diff recorded |
| differs — a superseded first version, its successor tracked | 1 | archive with the diff recorded |
| matched nothing tracked, behind published numbers | 10 | **committed** as `56e013a` |
| differs by a single pre-restructure include line | 1 | archive with the diff recorded — see §4.3 |
| matched nothing tracked, genuinely scratch-only | 6 | archive with manifest |

### 1.1 One expected artifact is gone, and that is correct

`hadronization_merged/complete_root_HF_RUN3_V1_JUNCTIONS.partial.iHJ4n3` — the
"stale JUNCTIONS partial" this session was authorised to archive — **no longer
exists.** The merge consumed and promoted it: `complete_root_HF_RUN3_V1_JUNCTIONS`
is present with mtime 2026-08-12 19:28, and all three tunes plus
`SUBSAMPLES_HF_RUN3_V1` are complete. **There is nothing to archive, and the
absence is evidence the merge finished rather than evidence something was lost.**

---

## 2. MATCHES TRACKED — sha-verified, archive with manifest

### 2.1 The scratch-deployed tools

The deploy pattern is deliberate — the frozen checkout is read, never written —
so these are expected to exist and expected to match.

| deployed path | sha256 (16) | matches |
|---|---|---|
| `queue_probe.py` | `ade4eec0d07b486d` | tracked at **both** `43e35be8` and `HEAD` |
| `extract_species_decomposition.py` | `4cd8b6fa84935296` | `extraction/…` at `HEAD` — the **deduplicating** reader |
| `tune_chain.sh` | `eae4c0ae3b2dfaaa` | `extraction/pipeline/tune_chain.sh` at `HEAD` |
| `archive_breach_partials.sh` | `64d2b723cc6e5e36` | `tools/…` at `HEAD` |
| `a2_make_largest_index_variation.py` | `f6ce7a3bb0e5b1fe` | `tools/…` at `HEAD` |
| `sigmab_runs/task22/extract_species_decomposition.py` | `4cd8b6fa84935296` | the deployed reader the chains executed — **the deduplicating one** |

### 2.2 The M7 charm block logs — N7 re-verified against disk

**All ten `m7_runs/block_NN/m7_block_NN.log` match anchors G36–G45 byte for
byte.** N7 was closed at `b74e588` on 2026-08-12; this is the first time the
committed anchors have been checked back against the scratch originals.

```
01 a457c2b7e4ce36ba  02 5732372cbcef4316  03 22b7e018dc45bc56  04 fd51911bfd602feb
05 fa5a471f39cba439  06 a8b3f08879e2abcd  07 86eefbced0a685bd  08 499dbe9f6d4a8bec
09 d66c9b28d08f5805  10 339ef575a5b21025
```

### 2.3 The A2 variation trees — verified against the committed registry

| tree | macro sha256 | registry entry |
|---|---|---|
| `a2_variation/AnalysisScripts/status_analysis_THnSparse_qq.C` | `a4df31e6b6da5098…` | `permissive_smallest_index` — **pre-registered**, the arm the quoted systematic is measured on |
| `a2_variation_largest/…/status_analysis_THnSparse_qq.C` | `4e491134d8d3a2b4…` | `permissive_largest_index` — robustness |

Both are **admissible** entries in `config/a2_variations_v1.json`. The registry
is the gate: a variation not in it cannot be analysed.

### 2.4 The E5 extractor trees

| file | verdict |
|---|---|
| `extractor_e5fix/extraction/extract_species_decomposition.py` | `4cd8b6fa…` = tracked `HEAD` |
| `extractor_e5fix/extraction/decompose_with_block_sems.py` | `f05a011f…` = tracked `HEAD` |
| `extractor_e5fix/extraction/apply_decay_map.py` | `79d4e22e…` = tracked `HEAD` |
| `extractor_e5fix/extraction/compare_subset_parent.py` | `fa565a42…` = tracked `HEAD` |
| `attic_e5_replicating_extractor_20260813/` (both copies) | `b67f9008…` — the **defective replicating** reader, tracked at `003da54b`, so recoverable from history |

The attic holds two copies, both identical, exactly as `tune_extract.sh`'s own
comment says: the top-level one and the `sigmab_runs/task22` one, swapped out
together when E5 was fixed.

### 2.5 The plotting run directory — an archived tree with no `.git`

`hadronization_v3_plotting_run/` is a `git archive` deploy: **no `.git`, and no
injected commit marker.** That is the A2 provenance gap
(`HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT`) recurring in a tree that predates the
rule being written down. Its commit was therefore recovered **by content**:

| result | detail |
|---|---|
| 93 tracked-path files hashed | across `plotting/ extraction/ analysis/ merging/ config/` |
| 80 match | `e0b9aba` (2026-08-16, "Record the verdicts-and-figures session") |
| 3 match **current `HEAD`** | `improvedPlotting_THnSparse.C`, `make_hf_run3_v1_three_tune_config.py`, and the THREETUNE configuration json — edited after the snapshot, and those edits **were** committed |
| 10 absent | all build products and generated output: `__pycache__`, ACLiC `.d/.so/.pcm`, the `Plots/` figures, two variant configs |

**Zero locally-modified source.** The tree is `e0b9aba` plus three files that
moved forward into `HEAD`.

**Its live output is the committed one, and specifically the polished pair:**

| deployed | sha256 (16) | committed as |
|---|---|---|
| `Plots/…THREETUNE_PNG.png` | `545499157bf7d4a2` | `…THREETUNE_**POLISHED**_PNG.png` |
| `Plots/…multiplicity_boundary_receipt_v1.json` | `65da0282067c7a7f` | `…receipt_v1_**polished**.json` |

The un-suffixed committed pair (`1b2984c6…`, `eed87b25…`) is the **pre-polish**
version, which is what `plot_archive/…_prepolish_212544/` holds. The naming is
inverted between the two locations — the deploy's *plain* name is the repository's
*polished* file — and that is worth knowing before anyone compares them by
filename.

---

## 3. MATCHES AN OLDER TRACKED VERSION — superseded by the advance

Both matched `43e35be8` exactly and differ from `HEAD`. **Neither is a
modification; both are simply older.** The checkout advance is what supersedes
them.

| deployed | deployed sha (16) | `HEAD` sha (16) |
|---|---|---|
| `checkout_advance_guard.py` | `aad9b9adf796a5b8` | `3d00494d74b0216c` |
| `install_checkout_guard_hook.sh` | `38e6e0a0f2dfaf09` | `453e3bf6b0e6dc74` |

> **The installer one matters operationally.** The deployed copy is the
> pre-fix installer. The hook-sha verification that runs immediately after the
> advance is the fixed installer's first real test, and it must be run against
> the **advanced** checkout, not against this scratch copy.

---

## 4. DIFFERS — the two real cases, and why neither is committed

### 4.1 `tune_extract.sh` — the difference is entirely commentary

Deployed `d6166302283d5658`, tracked `HEAD` `3ad2723a07e3cf53`, matching **no**
commit in the last 400.

**19 changed lines. Every one of them is a comment.** Filtering the diff to
non-comment lines returns nothing:

```
diff tracked deployed | grep '^[+-][^+-]' | grep -v '^[+-]\s*#'   ->   (empty)
```

The executable content — the `--registry` flag, the `--decay-map v2` selection,
the reader path at `$T` — is **identical**. The two versions differ only in how
the E5 fix is narrated, and the tracked wording is the better of the two: it
records that the Nikhef copy was corrected in place first and the repository copy
second, which is the fact a future reader needs and the deployed comment drops.

**Disposition: archive with the diff recorded. Not committed** — committing it
would replace the more informative comment with the less informative one, and
the behaviour that produced the published table is already tracked, verified
line for line.

### 4.2 `a2_make_subs.py` — the superseded first version

Deployed `496723e63f014de0`, tracked `HEAD` `21e0d44a0ffdb1e6`, matching no
commit.

The deployed copy is the **pre-parameterization** generator: no `argparse`, no
registry lookup, constants hard-coded at module level —

```python
SCRATCH       = BASE / "a2_variation"
VARIATION_SHA = "22120383b07eb3572660f9a2aa7c895dd260ee23c7bc349a5a2e4f76262256de"
N_SLOTS       = 100
```

**That hard-coded sha is the decisive fact.** `22120383…` is registered in
`config/a2_variations_v1.json` under **`superseded`**, as
`permissive_smallest_index_guarded` — the arm carrying the per-job throw that
selected on the outcome variable and discarded 49 of 100 MONASH jobs
(`ERROR_RECORD.md` **E7**). Entries under `superseded` are explicitly **not
admissible**; the analyzer reads only `variations`.

So the deployed script is the generator of an arm whose results are inadmissible
by design, and its successor — parameterized, registry-backed,
`--deploy-commit`-requiring — **is** tracked, and its docstring already records
this version's existence and defect verbatim.

**Disposition: archive with the diff recorded. Not committed** — it produced no
admissible published result, and the tracked successor is the better record of it
than the file itself.

### 4.3 `b4_mapping/macro/CalibrateMultiplicityAgainstMinBias.C` — one include line

**Found matching no tracked content, briefly anchored on that basis, and that was
wrong.** It differs from the tracked `Validation/CalibrateMultiplicityAgainstMinBias.C`
by **exactly one line**:

```
-#include "../generation/producer/HeavyFlavourUtils.h"   (tracked, post-restructure)
+#include "../SimulationScripts/HeavyFlavourUtils.h"     (deployed, pre-restructure)
```

The restructure moved `SimulationScripts/` to `generation/producer/`; the b4 run
(2026-08-09) predates it. So this is the **pre-restructure form of a tracked
file**, not an unanchored macro. Anchoring it would place a second, older copy of
a tracked macro under a second path where the two can drift.

**Disposition: archive in place with the diff recorded.** The anchor was removed
in the follow-up commit; `AnalysisScripts/anchors/b4_multiplicity_mb/MANIFEST.md`
carries the reason.

> **What the copy does establish, and it is not small: the macro is not unrun.**
> `b4_mapping/logs/` holds six completed runs — `{mb,hard} × {MONASH, JUNCTIONS,
> CLOSEPACKING}` — each ending `B4_RUN_EXIT=0`, with six `nch_*.root` outputs.
> The MONASH mb run produced **51.201** (|η|<4) and **12.948** (|η|<1), the
> counters `NCH_DECAY_POLICY_BIAS_8317.md` reports as agreeing to 1.1 % per unit
> η — the measured input S4 needs.
>
> **`STATE.md` lists this macro under "WRITTEN — UNRUN — AVAILABLE".** That entry
> is stale; the run predates it.

### 4.4 A note on the loose A2 macro

> The loose `status_analysis_THnSparse_qq_A2.C` at the top level is that same
> superseded macro (`22120383…`), and its outputs are preserved at
> `a2_runs/permissive_guarded_22120383/`. **Its identity is in git even though
> its content is not** — the registry pins it by sha. Archive, never delete: the
> registry entry says the outputs are the E7 evidence.

---

## 5. MATCHED NOTHING TRACKED — committed as `56e013a`

Eleven files, all behind published numbers, all now anchored. See
`AnalysisScripts/anchors/{closure_v3_verdicts,e5fix_drivers}/MANIFEST.md`.

| group | why it had to be committed rather than archived |
|---|---|
| `closure_runs/` — 2 closure logs, 2 verdict lines, waiter + its log | the two `CANONICAL_PAIR_BLOCK_CLOSURE_PASS` verdicts **gate the three-tune central table**. The verdicts were quoted in session records; the logs were not committed anywhere |
| `extractor_e5fix/run_{extract,blocks,three_tune}.sh`, `verify_e5.py` | the extractor was tracked, but not **how it was invoked** — run root, subsample directory, tune order |

*(A eleventh file, `b4_mapping/macro/CalibrateMultiplicityAgainstMinBias.C`, was
committed in `56e013a` and then removed: it is a tracked macro with one
pre-restructure include line, not an unanchored one. See §4.3.)*

---

## 6. SCRATCH-ONLY — archive with manifest, nothing published depends on them

| file | note |
|---|---|
| `chain_path_proof.sh` | one-off path proof |
| `patch_variation.py` | A2 variation patcher, superseded by `a2_make_largest_index_variation.py` (tracked) |
| `summarize_merge.py` | merge log summarizer |
| `status_analysis_THnSparse_qq_A2.C` | **the superseded guarded macro** — see §4.2; registry-pinned by sha |
| `hadronization_v3_plotting_run/plotting/variant_{logratio,monashfirst}.json` | the two **rejected** plotting variants' configs. Their outputs *are* committed, as `REJECTED_variantA_log_ratio_panels.png` and `REJECTED_variantB_monash_first_ordering.png` |

---

## 7. LIVE — inventoried, NOT archived

**Owner ruling, Consolidation A addendum.** These are live until the systematics
campaigns converge and are harvested; that harvest is a separate session.

| path | size | rule |
|---|---|---|
| `systematics_deploy/Hadronization` | 132 M | ⛔ **DO NOT TOUCH** — pinned at `72ca4e39`; in-flight jobs verify it at startup and refuse a tree with tracked modifications |
| `systematics_regression/` | 89 M | the nominal-reproduction gate's evidence — 36.9 M values, identical digest. Deliberately outside the production root so it can never be merged |
| `hadronization_production/HF_SYS_*` | growing toward ≈ 193 G | live production output |
| `systematics_20260817{,b,c}.bundle` | 3 × 56 M | archivable **after** convergence — reconstructible from the repo |

## 8. FROZEN — untouched by this reconciliation

| path | size | why |
|---|---|---|
| `merge_runs/` | 4.3 G | **N2** — the merge timing evidence is filesystem mtimes; reading or clearing it destroys them |
| `archive/` | 1.1 G | the 34 breach partials — moved, never deleted |
| `a2_runs/` | **25 G** | holds `held_evidence_20260813/` and `permissive_guarded_22120383/` — the E7 evidence the registry points at |
| `Hadronization-full-production/campaigns/*/seed_ledger.jsonl` | — | nothing re-derives historical seeds |
| `b-hadron-fractions/` | 1.2 T | **out of scope** — a different project |
