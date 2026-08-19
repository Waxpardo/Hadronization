# Repository restructure — PLAN FOR A SINGLE APPROVAL PASS

> # ⛔ AWAITING OWNER APPROVAL. NOTHING HERE HAS BEEN EXECUTED.
>
> Written on branch `restructure-prep` by a session that made **no mutations of
> any kind** — no renames, no moves, no deletions, no `.gitignore` edits, no
> remote writes, no pipeline runs. The renames table in §5 is a proposal.
> **It was executed by nobody.**

**Written 2026-08-12 against `9426f38`.** Revised the same day to the owner's
pivot directive: *development is over; this is freeze preparation.*

**This document gets one approval pass.** Every open decision is in **§8** as a
numbered choice **with a recommended default**, so approval can be a single
"take the defaults except N" rather than a round trip. There will be no second
draft.

Companions: `docs/GOLDEN_OUTPUTS.md` (the freeze contract and the acceptance
gate), `docs/REPO_FILE_CENSUS.md` (what is live), `docs/NIKHEF_DISK_INVENTORY.md`
(the disk side's evidence).

---

## 1. MANDATE AND SCOPE

**Per the owner's directive, the restructure is ONE session.** Its contents are
fixed:

1. `git mv` per the approved table (§5);
2. handoffs → `docs/history/`;
3. dead tools → `attic/`;
4. the three entry documents written (§6);
5. **six ruled tasks** (§1.2) — **all six ready**;
6. **acceptance gate: suite green + derived artifacts regenerate to recorded
   digests — R5/R6 *are* that gate for the maps.**

### 1.1 Timing and approval status — owner rulings, 2026-08-12

| | |
|---|---|
| **execution window** | ✅ **OPEN — RUN NOW.** The MONASH harvest is committed (`b74e588`); precondition 1 is met |
| **ordering** | **SERIALIZED: restructure first, JUNCTIONS harvest second, on the post-restructure layout.** Both touch `compare_subset_parent.py`; this removes the collision rather than managing it |
| **§8 decision sheet** | **with the owner. Nothing moves before that ruling returns** |
| **the 13 deletion-candidates** (`REPO_FILE_CENSUS.md`) | **same ruling pass** |
| **amendments to the brief** | **none.** It executes as written |

### 1.1a New material to absorb — same treatment as everything else

Landed on `physics-focus` after this branch was cut, in `df078ad`, `38bf707`,
`b74e588`:

| new/changed | target |
|---|---|
| `docs/MONASH_CENTRAL_TABLE.md` | **`docs/`, active** — the first tune's numbers; carries the two paper-facing labels (§6.3) |
| **the overdispersion note** | **not a separate file** — it is **§3 of `MONASH_CENTRAL_TABLE.md`** ("I3 exact, and I2's null is MISSPECIFIED"). It moves with its parent; **do not go looking for a file that does not exist** |
| `AnalysisScripts/anchors/m7_blocks/` (10 charm logs) | **`artifacts/anchors/m7_blocks/`** — beside `m7b_blocks/`, exactly as §5 row 11 already routes the anchors tree. **Binary; digests are frozen in `GOLDEN_OUTPUTS.md` §2.7** |
| `docs/MERGE_V3_BAND_VALIDATION.md` (modified) | **`docs/`, active** — now also carries the merge-target headroom line (1040 G avail) |
| `AnalysisScripts/anchors/MANIFEST.md` (modified) | **`artifacts/anchors/`** — ⚠ still stale, see §9 R7 |

**No new rename rows are needed.** Every item lands inside a directory §5
already routes, which is what "absorb like everything else" means in practice.

### 1.2 Two fixes folded into the session, ruled and scoped

| # | change | ruling |
|---|---|---|
| **F-a** | `extraction/extract_species_decomposition.py` — **remove the `--decay-map` default and make the argument required** | the v1 default is **ruled a reproduction hazard**. *"One line + suite. No separate ceremony."* |
| **F-b** | `docs/CONTENTION_RECURRENCE_PREREGISTRATION.md` — **add a superseded mark** | **never scored.** It predicted a *scheduling* effect, gated no number, and the pivot ended operational forecasting. Marked, not deleted — it is a record of a prediction made in advance |
| **F-c** | `docs/MONASH_CENTRAL_TABLE.md` §4a — **kMultiplyHeavy footnote at point of use** | ✅ **UNBLOCKED 2026-08-12.** Corrected wording approved verbatim, plus one authorized closing sentence. **Commit the text in §1.3 exactly as written** |
| **F-d** | `docs/MONASH_CENTRAL_TABLE.md` §4b — **promote the SELECTION caveat ABOVE the table** | it currently trails the table as a closing sentence, where the reader meets it after adding the column up |
| **F-e** | `AnalysisScripts/anchors/MANIFEST.md` §3 — **"in flight" → anchored** | stale in two ways: it still lists `sigmab_runs/` as *"in flight this session"* while `anchors/sigmab_raw/` holds all ten logs, and it predates the charm-M7 anchoring in `b74e588`. **One edit while the file is already being moved** |
| **F-f** | **merge this branch at its current seven-document state** | the prep branch adds seven files under `docs/` and modifies nothing. `git diff --name-status physics-focus...restructure-prep` must print seven `A` lines and nothing else |

### 1.3 ✅ F-c — APPROVED TEXT, commit verbatim

**History of this footnote, because it is the useful part.** The ruling required
*"verify the 192 and the mechanism from the code path before committing the
words."* The verification was done read-only, **the number was exact and the
mechanism was not what the words said**, and the wording was replaced before it
reached a committed document. **The requirement caught its own text.**

#### The approved footnote — `MONASH_CENTRAL_TABLE.md` §4a, at point of use

> kMultiplyHeavy 0.0000% — 192 entries of 1,298,655,240 (1.5 × 10⁻⁵ %).
> This category holds hadrons with |q_c| > 1 or |q_b| > 1 — the doubly-
> and triply-heavy baryons Ξ_cc, Ω_cc, Ω_ccc. It is a populated category
> of the partition, not an exclusion; the six categories sum exactly to
> the total. The value is small because doubly-heavy baryon production
> is rare, not because anything was classified out.
>
> B_c⁺ (q_c = +1, q_b = −1, neither above 1) is counted as a ground-state
> species in kCentralGround; the one category excluded by construction is
> kHiddenHeavy (quarkonia), with exactly zero entries.

#### Every claim in it, checked against the artifacts

| claim | evidence |
|---|---|
| 192 of 1,298,655,240 | `per_category.csv` row 2: `kMultiplyHeavy,192.0,192.0,0.0,0.0`; the six categories sum to **exactly** 1,298,655,240 |
| 1.5 × 10⁻⁵ % | computed: 1.478 × 10⁻⁵ % |
| `|q_c| > 1 \|\| |q_b| > 1` | `generation/producer/HeavyFlavourUtils.h:357-359`, verbatim |
| Ξ_cc, Ω_cc, Ω_ccc | pdg 4412, 4422, 4432, 4444 carry `category_name: kMultiplyHeavy` in `species_ordinals_v2.json` |
| "populated category, not an exclusion" | **36 species** in the ordinal table are `kMultiplyHeavy`; they collectively caught **192 entries**. The axis represents them; the physics is simply rare |
| B_c⁺ is `kCentralGround` | pdg 541 → ordinal 119, `q_c: 1`, `q_b: -1`, `central_registry: 1`, `category_name: kCentralGround` |
| kHiddenHeavy has exactly zero entries | `per_category.csv` row 1 reads `0.0`; **0 species** carry it in the table, and `hidden_heavy_excluded = 17` |

**All seven check out. Commit the text as written.**

#### One optional precision, for the executor to take or leave

**Two of the six rows read exactly zero, and they are zero for different
reasons.** `kHiddenHeavy` is zero because its 17 species were **removed from the
ordinal table** at build time. `kOtherNoncentral` is zero because it is
**unreachable**: every species in the table carries charm or beauty, so
`ClassifyHeavyStateDetailed`'s final fallthrough can never be taken.

The approved sentence says *"the one category excluded by construction is
kHiddenHeavy"* — **which is true**, since only kHiddenHeavy is *excluded*. But a
referee reading the table sees two zero rows and one sentence about one of them.
**If a half-clause is wanted:** *"…(quarkonia), with exactly zero entries;
kOtherNoncentral is likewise empty, being unreachable for any open-heavy
species."* **Optional — the sentence is correct without it.**

#### Ownership of the error, recorded with both sources

**"By construction" reached the approved wording by two independent routes:** it
was proposed in `HANDOFF_20260812_prep_v3.md` §3.1 from reading the two tables
without opening the classifier, **and it entered the owner's addendum
independently of that handoff.** Neither source derived it from the code.

> **Two independent parties reached the same wrong framing, and no amount of
> mutual agreement would have caught it — which is the E1 lesson exactly: a
> reimplementation check proves agreement, not correctness.** What caught it was
> a **mechanical requirement to read the code path**, imposed by the same ruling
> that carried the error. **Recorded with both sources, per the owner's note,
> because attributing it to one of them would misdescribe how it was caught.**

**On F-a, one piece of engineering information the executing session should have
before it opens the file.** The ruled change lives at `:203`
(`default=DECAY_MAP` → `required=True`; the help string still says
`decay_parent_map_v1.json` and should go too). That closes the hazard the owner
named — *silently using v1*.

A **different** residual sits four lines of context away, at `:278`:

```python
if args.decay_map.exists():
```

With the argument required, a path that is mistyped or stale still takes the
false branch: `decay_verdict` stays `"SKIPPED"`, the tool exits **0**, and the
experiment-comparable convention is silently absent. **Same argparse call, same
function, no extra ceremony to fix while already there** — making that call
unconditional turns a silent skip into a fail-closed read. **Executor's call;
flagged, not mandated.**

> **NOTHING ELSE. No additional verification may be invented for this — the
> owner's explicit ruling.** This plan therefore proposes no new gate, no new
> instrument, no new pre-registration and no phased rollout. Where it flags a
> risk it does so as **information for the executing session**, not as a
> checkpoint that session must satisfy.

**Two-tier rigor applies.** The restructure is an *operation*, not a result the
paper quotes. It gets ordinary engineering care: do it, record it, move on.

---

## 2. THE TWO THINGS A RESTRUCTURE MUST NOT COST

| # | invariant | enforced by |
|---|---|---|
| **I** | **Every published number still regenerates to its recorded digest.** | `docs/GOLDEN_OUTPUTS.md` — the acceptance gate |
| **II** | **Every piece of evidence survives, including evidence of error.** | `REPO_FILE_CENSUS.md`: HISTORY and `attic/` are destinations, never deletions |

**Invariant II is the one a tidy-up threatens.** `decay_parent_map_v1.json` is
defective and superseded — and it is the evidence for **E1**, the project's most
instructive published error. `anchors/extraction_dual/per_observable.csv` is
superseded — and it is the only committed artifact carrying the pre-fix table
that shows E1's size. **"Superseded" is not "deletable" in this repository**,
and a restructure is exactly when that distinction gets lost.

---

## 3. TARGET LAYOUT

Named for the pipeline's order, so the directory listing teaches the workflow.

```
Hadronization/
├── README.md                 rebuild guide — see §6
├── ARCHITECTURE.md           for a reader with no ROOT/PYTHIA — see §6
├── STATE.md                  frozen / pending / not-planned — see §6
├── REPRODUCIBILITY.md        unchanged, stays at root
├── RELEASE_BLOCKERS.md       unchanged, stays at root
├── POST_SUBMISSION.md        unchanged, stays at root
├── Makefile                  unchanged: the command surface stays stable
├── setupEnv.sh               unchanged: the frozen Nikhef checkout sources it
│
├── generation/               PYTHIA producer, tune cards, Condor submission
│   ├── producer/               heavyflavourcorrelations_status.cpp, HeavyFlavourUtils.h,
│   │                           Sha256.h, Makefile
│   ├── cards/                  pythiasettings_*.cmnd
│   ├── registries/             GeneratedHeavyFlavourRegistry.h, GeneratedTuneSettingRegistry.h
│   └── submit/                 runCondorJob.sh, submit_status_analysis.sh, Condor_README.md
│
├── analysis/                 the one-pass reduction: raw/ -> per_job/
│   ├── status_analysis_THnSparse_qq.C, run_status_analysis.sh
│   └── contracts/              GeneratedPairRegistry.h, GeneratedPairObjectContract.h,
│                               GeneratedSpeciesOrdinals.h, AssociateOriginCategoryContract.h
│
├── merging/                  per_job/ -> centrals + blocks
│   └── merge_root_files.sh, MergeCanonicalAnalysis.C, MergeAnalysisObjects.C,
│       make_subsamples.sh
│
├── extraction/               merged -> the paper's numbers
│   └── extract_species_decomposition.py, decompose_with_block_sems.py,
│       apply_decay_map.py, second_branch_weight.py, aggregate_m7.py,
│       compare_subset_parent.py, pipeline/
│
├── plotting/                 (was plotting/, contents unchanged)
├── validation/               (was Validation/) ROOT audits and gates  ⚠ see R2
├── tests/                    unchanged — 30 .py + 5 .cpp, the acceptance suite
├── tools/                    campaign management, guards, renderers, doctor
├── config/                   unchanged: signed registries and contracts
│
├── artifacts/                ⚠ THE FROZEN SET — see §4.2
│   ├── species_ordinals_v2.json
│   ├── decay_parent_map_v1.json      (HISTORY — the E1 evidence, never delete)
│   ├── decay_parent_map_v1_1.json
│   ├── decay_parent_map_v2.json
│   └── anchors/                       f4_probe/, extraction_dual/,
│                                      merged_monash_central/, m7b_blocks/,
│                                      sigmab_raw/, MANIFEST.md
│
├── attic/                    ⚠ dead code, kept not deleted — see §5.3
│   ├── plotting/               improvedPlotting.C, PlottingWizard.C,
│   │                           combinedCanvasPlots.C, ListHistos.C, stale configs
│   ├── count_events/           AnalysisScripts/CountEvents/
│   └── split_chain/            bb/cc/qq producers + reductions  (pending D2)
│
├── docs/
│   ├── (the active documents, unchanged)
│   └── history/
│       ├── handoffs/           47 files
│       ├── audits/             docs/audit/ + docs/audits/, merged
│       ├── cleanups/           CLEANUP_REPORT.md
│       ├── agent_instructions/ PUBLICATION_READY_CODING_AGENT_INSTRUCTIONS.md
│       └── studies/            Balancing_and_Sampling/, DpDmBpBm_ComparisonStudy/,
│                               RootFiles/ descriptions
│
├── ValidationReports/        unchanged: cited by REPRODUCIBILITY.md
├── Literature/               unchanged
└── Paper/                    UNTOUCHED, out of scope
```

**Top-level items: 30 → 18** (13 dirs + 5 root docs + Makefile + setupEnv.sh).
Root-level prose: 9 files → 6, three of which are the new entry documents.

**`attic/` vs `docs/history/`:** code goes to `attic/`, evidence goes to
`docs/history/`. A study with results is evidence; a superseded plotting macro is
code. `Balancing_and_Sampling/` is judged evidence — it has committed numeric
outputs and an unresolved correctness note (`ATTENTION.txt`).

---

## 4. EXECUTION, IN ORDER — ONE SESSION

### 4.1 The order

| # | step | note |
|---|---|---|
| 1 | record `git rev-parse HEAD`, `shasum -a 256` of the golden set, and the suite count **before touching anything** | this is the baseline the gate compares against; it is a measurement, not a new gate |
| 2 | `git mv` per §5 | history is preserved for all of it |
| 3 | fix the path references the moves break (§4.2) | the bulk of the work |
| 4 | **F-a** — `--decay-map` becomes required (§1.2) | one argparse call |
| 5 | **F-b** — superseded mark on `CONTENTION_RECURRENCE_PREREGISTRATION.md` (§1.2) | one banner |
| 6 | write the three entry documents (§6) | |
| 7 | **gate:** `make check` green at 30/30 **with ROOT present**, the `GOLDEN_OUTPUTS.md` digests unchanged, **and R5/R6 run** | the owner's gate, verbatim. **R5/R6 are the gate for the maps, not an addition to it** |
| 8 | one commit, or one commit per §5 group — executor's choice | |

**On step 7.** R5 and R6 rebuild the decay maps from committed probe anchors
with committed builders; they are pure Python, take seconds, and need neither
ROOT nor PYTHIA. Running them at the gate is what converts the maps' status from
**DETERMINISTIC-BY-CONSTRUCTION** to measured — and it is the only way the gate
can distinguish "the file still has the right bytes" from "the file is still
derivable from its inputs". Expected lines, verbatim:

```
DECAY_PARENT_MAP … map_sha256=dd502a10c5932fff
CONJUGATION artifact_rows_changed=101 table_affecting_rows=60 … I1=PASS I2=PASS
MAP_V2_BUILT species=202 split=2 threshold=0.1% sha256=c9593c9c0a7c4ec2
```

### 4.2 The path-coupling reality — the honest cost estimate

Measured at `9426f38`:

| measure | count |
|---|---|
| distinct quoted repo-relative paths in `tools/`, `tests/`, root `*.sh`, `Makefile` | **63** |
| total occurrences | **138** |
| further `.C` / `.h` / `.cpp` / `.sh` files with unquoted `Dir/...` forms | **~30** |

The pattern is uniform: `REPO = Path(__file__).resolve().parents[1]` followed by
a **hardcoded subdirectory string**. Nine tools and at least eight tests name
`AnalysisScripts/` explicitly, including every golden-output generator and every
golden-output recipe.

**Most of these fail loudly** — a `--check` prints `*_STALE`, a builder raises,
a test errors. **One is known to fail quietly**, and the executing session
should know about it before it starts:

> `extraction/extract_species_decomposition.py:278` guards its decay-map read with
> `if args.decay_map.exists():`. **A moved map makes the file not exist, the
> branch is skipped, `decay_verdict` stays `"SKIPPED"`, and the tool exits 0
> having silently dropped the entire experiment-comparable convention.**
> That is a `rc=0` with a missing output — the project's own recurring failure
> mode. **Grep for `.exists()` guards around artifact paths before moving
> `artifacts/`.**

**This is information, not a checkpoint.** The gate stays as the owner set it.

---

## 5. THE DRAFT RENAMES TABLE

**Proposal only. Executed by nobody.** `git mv` preserves history throughout.

### 5.1 Pipeline directories

| # | from | to |
|---|---|---|
| 1 | `SimulationScripts/` | `generation/` (split into `producer/`, `cards/`, `registries/`) |
| 2 | `runCondorJob.sh`, `submit_status_analysis.sh`, `Condor_README.md` | `generation/submit/` ⚠ `runCondorJob.sh` is named in 21 files |
| 3 | `analysis/status_analysis_THnSparse_qq.C`, `status_analysis_qq.C`, `hf_mult_pt_analysis_multi.C`, `run_hf_analysis.sh`, `Analysis_README.md` | `analysis/` |
| 4 | `run_status_analysis.sh` | `analysis/` |
| 5 | `AnalysisScripts/Generated*.h`, `AssociateOriginCategoryContract.h` | `analysis/contracts/` |
| 6 | `AnalysisScripts/Merge*.C` | `merging/` |
| 7 | `merge_root_files.sh`, `make_subsamples.sh` | `merging/` ⚠ `merge_root_files.sh` is named in **33** files |
| 8 | the eight extraction tools + `extraction/pipeline/` | `extraction/` |
| 9 | `plotting/` | `plotting/` |
| 10 | `Validation/` | `validation/` ⚠ **case-only — see R2; recommended default is NOT to do this** |

### 5.2 Artifacts and history

| # | from | to |
|---|---|---|
| 11 | `AnalysisScripts/*.json`, `AnalysisScripts/anchors/` | `artifacts/` ⚠ the expensive one, §4.2 |
| 12 | `docs/handoffs/` | `docs/history/handoffs/` |
| 13 | `docs/audit/` **+** `docs/audits/` | `docs/history/audits/` — **merges two directory names that differ by one letter** |
| 14 | `CLEANUP_REPORT.md` | `docs/history/cleanups/` |
| 15 | `PUBLICATION_READY_CODING_AGENT_INSTRUCTIONS.md` | `docs/history/agent_instructions/` — 128 KB, not physics |
| 16 | `Balancing_and_Sampling/` | `docs/history/studies/balancing/` — owner already ruled it historical (`WORKSPACE.md`) |
| 17 | `plotting/DpDmBpBm_ComparisonStudy/` | `docs/history/studies/dpdm_bpbm/` |
| 18 | `RootFiles/` (3 description files, no data) | `docs/history/studies/rootfile_descriptions/` |
| 19 | `plotting/validation/` | `docs/history/` (plotting handoff + removed-plot inventory) |

### 5.3 To `attic/` — dead code, kept not deleted

| # | from | to | reason |
|---|---|---|---|
| 20 | `plotting/improvedPlotting.C` | `attic/plotting/` | superseded by `improvedPlotting_THnSparse.C`; in no entry point |
| 21 | `plotting/{PlottingWizard,combinedCanvasPlots,ListHistos}.C` | `attic/plotting/` | 2026-02 generation, no entry point |
| 22 | `plotting/configuration_{pT,pseudorapidity,rapidity}.json` | `attic/plotting/` | 1 reference each, superseded by the THnSparse configs |
| 23 | `plotting/B_Balancing_GeneralPlotting.C` | `attic/plotting/` | **duplicate basename** with `Balancing_and_Sampling/`; keep one — D6 |
| 24 | `AnalysisScripts/CountEvents/` | `attic/count_events/` | superseded by `tools/campaign_status.py` |
| 25 | `Balancing_and_Sampling/reproduceCanvasPadError.C` | `attic/` | ROOT bug-repro scratch |
| 26 | the split bb/cc/qq chain (6 files in `AnalysisScripts/`, 7 in `SimulationScripts/`) | `attic/split_chain/` | **pending D2** |
| 27 | `README.txt` | `attic/` **or** delete | **pending D3** — fold its unique sentence into `README.md` first |

### 5.4 What does NOT move

`Makefile`, `setupEnv.sh`, `README.md`, `REPRODUCIBILITY.md`,
`RELEASE_BLOCKERS.md`, `POST_SUBMISSION.md`, `config/`, `tests/`, `tools/`
(minus the extraction tools), `ValidationReports/`, `Literature/`, `Paper/`,
`.gitignore`.

> **`.gitignore` stays untouched.** Its 92 lines encode which submit files and
> ROOT outputs are ignored — including `/RootFiles/**/*.root`, `/Production/`,
> `/AnalysisResults/` and `/AnalyzedData/`, which on Nikhef hold **423 GB**
> (§10). A path change there silently changes what gets committed. **If the
> restructure appears to require a `.gitignore` edit, stop and ask.**

---

## 6. THE THREE ENTRY DOCUMENTS

Written in the restructure session, per the directive. Outlines below so the
approval pass can rule on content, not just existence.

### 6.1 `ARCHITECTURE.md` — for a reader with no ROOT and no PYTHIA background

Audience: a referee, a co-author, or a successor who knows particle physics but
not this software stack. **No command in it should need to be run to follow it.**

| § | content |
|---|---|
| 1 | **The question in one page.** Whether a heavy baryon's flavour-balancing partner is itself a baryon, compared across three tunes that differ in colour reconnection |
| 2 | **What PYTHIA and ROOT are, in four sentences each**, and why the analysis is two programs rather than one |
| 3 | **The pipeline as a diagram**: producer → raw (3000 files, 300 M events) → one-pass reduction → `per_job/` (3000 dirs × 300 pair files) → gate → merge (3 centrals @1000 + 30 blocks @100) → closure → extraction |
| 4 | **Why ten blocks.** The n=10 disjoint `event_id`-modulo blocks are the SEM machinery; every nonlinear quantity is formed *inside* a block before averaging, `conservative_degrees_of_freedom = 9` |
| 5 | **The two conventions**, side by side, and that they answer different questions — structural (what the generator made) vs experiment-comparable (what a detector would see) |
| 6 | **What is signed how.** `q_c = n_c − n_cbar`, not charge. `B+` has `q_b = −1`. *"This is easy to get backwards"* — quote `REPRODUCIBILITY.md` |
| 7 | **Where the numbers live**: pointer to `GOLDEN_OUTPUTS.md` |

### 6.2 `README.md` — as a rebuild guide

Rewritten from "what this repository is" to **"how to rebuild every number in
it"**, in the order a newcomer would do it.

| § | content |
|---|---|
| 1 | prerequisites: PYTHIA 8.317 (tarball sha `1ae551d1…45adf`, built by you — there is no container), ROOT 6.30/01, `setupEnv.sh` asserts both and exports nothing on mismatch |
| 2 | `make doctor`, `make check` — and **the ROOT trap**: without ROOT the suite reports a smaller denominator and looks green. A green run shows `ROOT: /path/to/root` |
| 3 | **the ~2 h smoke path** (§7) — do this before anything long |
| 4 | the repo-only regeneration: recipes R1–R11 of `GOLDEN_OUTPUTS.md`, none of which need Nikhef |
| 5 | the full pipeline, with its real costs: **562.5 CPU-hours** for a full production (not 390), merge 33 objects, closure 2100/1500 |
| 6 | **what you cannot rebuild and why** — `GOLDEN_OUTPUTS.md` §5, N1–N7 |
| 7 | where each document is authoritative (keep the existing "Which document owns what") |

**Fix in the same pass** (`REPO_FILE_CENSUS.md` §8): the stale test counts
(24/21/3 → 35/30/5), the stale `Makefile:117` pointer, and the claim that the
Python tests are standard-library only and run anywhere — which
`tools/run_tests.sh` directly contradicts.

### 6.3 `STATE.md` — frozen / pending / not-planned

The one-screen answer to *"where is this project?"* **Draft content, for the
approval pass to correct:**

**FROZEN** — recorded, digest-pinned, not to be recomputed:

- the species axis: 202 ordinals, digest `646f310f78126267`;
- decay maps v1 (history), v1.1, v2 — with their recipes;
- M7 charm: 0.0451 / 0.5497 / 0.5125 % relative shift;
- M7 beauty: 0.0141 / 0.0140 / 0.0143 % — **flat across tunes**;
- Σ_b raw-count leg: 26.59 ± 0.24, 10.51 ± 0.19, 0.83 ± 0.11 — **the physics
  gate is passed**;
- the second-branch number: **0.0018 %** (12.84 % survives as history);
- the MONASH convention tables from merged weights;
- **the MONASH central table** (`MONASH_CENTRAL_TABLE.md`, 2026-08-12): closure
  **2100/1500, errors=0**, I3 exact, block-SEM decomposition in both conventions.
  **Two labels travel with it and must be stated prominently wherever it is
  quoted:**
  - **`kMultiplyHeavy` is ~0 because doubly-heavy baryons are RARE, not because
    anything is excluded** — 192 entries of 1,298,655,240. It is a populated
    category **inside** the partition (Ξ_cc, Ω_cc, Ω_ccc; `|q_c| > 1 || |q_b| > 1`),
    and `0.0000 ± 0.0000` is neither a measured zero nor a bug. **B_c⁺ is NOT
    here — it is `kCentralGround`, inside the primary bin.** The category that
    *is* excluded by construction is `kHiddenHeavy` (17 species). **Verified from
    the code path 2026-08-12; see §1.3 — this supersedes the wording first
    proposed**;
  - **the experiment-comparable table is a SELECTION, not a partition** — its
    eight species **do not sum to 100 %** and are not meant to, while the
    diquark-structure table beside it **is** a partition and does;
- closure at v3 scale: **2100 / 1500**, and that 1800/600 is failure;
- campaign HF_RUN3_V1: **3000/3000**; seed ledger **3557/3557**.

**PENDING** — known, in flight, nobody needs to plan it:

- **the three-tune cross-tune table with block SEMs — the resubmission's central
  number.** **MONASH is delivered**; JUNCTIONS and CLOSEPACKING are not merged;
- **the I2 null recalibration** — MAD-based cross-block σ, |z| > 4 retained,
  ruled for the JUNCTIONS harvest. **See §9 R8: it lands on the same function
  the pinned E4 regression test uses**;
- the merge's wall clock scored against the 65–77 h band — **one line, no
  analysis** (owner's ruling);
- the Nikhef checkout advance, which deploys the guard/installer fix;
- advisory step 2: per-tune b-baryon ratios, one table.

**WRITTEN, UNRUN, AVAILABLE** — a category of its own, by owner ruling
2026-08-12. **These stay in the tree.** Each is a measurement that exists as
code and has no recorded run; none is dead, none is planned, and any of them can
be run if a question makes it worth doing:

| macro | bears on |
|---|---|
| `CalibrateMultiplicityAgainstMinBias.C` | **C8** — per-tune percentile offsets |
| `TestPrimaryChargedDefinition.C` | **C8**, generator-side counterpart |
| `TestInclusiveRawKinematics.C` | **B3** — the blocked inclusive-spectra path |
| `AuditTuneSettings.C` | tune-settings audit |
| `TestHardCarrierUniqueness.C` | hard-carrier uniqueness |
| `TestPlotProjectionCuts.C` | plotting projection cuts |

> **This is the same shape as M7**, which sat unrun until the review asked and
> then took one session to become a table with an uncertainty. Listing them here
> keeps that visible rather than accidental — which is what
> `VALIDATION_INVENTORY.md` was written for.

**NOT PLANNED** — deliberate, so nobody re-opens them:

- systematics beyond M7 — PDF and scale variation are **not addressed**;
- a kinematic-differential unresolved systematic (M7 is integrated);
- the tune-bundle confound: JUNCTIONS retunes baryon-production parameters, so a
  MONASH-vs-JUNCTIONS baryon difference **cannot** be attributed to junction
  formation alone;
- the junction hang's mechanism — not reproducible, node dependence untested;
- a container or automated PYTHIA build;
- **the contention recurrence** — pre-registered 2026-08-12, **superseded and
  never scored** by ruling. It predicted scheduling, not physics, and gated no
  number.

---

## 7. THE SMALL-N SMOKE PATH — what a newcomer runs first

**Purpose: prove the chain end to end on a laptop-plus-one-cluster-hour, before
committing to anything long.** Ships as `docs/SMOKE_PATH.md` or a `README.md`
section — D7.

### 7.1 Stage A — repo only, no ROOT, no PYTHIA, no Nikhef

Pure Python over committed inputs. **This is the whole extraction chain and it
runs anywhere:**

```bash
tools/build_decay_parent_map.py    <anchors>/f4_probe/f4_probe_v1.out ...   # R5
tools/build_decay_parent_map_v2.py <anchors>/f4_probe/f4b_probe.out  ...   # R6
extraction/apply_decay_map.py --map ... --weights <merged_monash_central>       # R7
extraction/second_branch_weight.py --per-species ...                            # R8
extraction/aggregate_m7.py <anchors>/m7b_blocks/*.log                           # R9
extraction/compare_subset_parent.py <subset> <parent> --null binomial ...       # R10
extraction/compare_subset_parent.py <subset> <parent> --null mad ...            # R10b
```

Each has a named positive check in `GOLDEN_OUTPUTS.md` §4. **A newcomer who gets
`map_sha256=dd502a10c5932fff` and 30 flagged bins has reproduced the decay-map
correction and the E4 anchor defect from scratch.**

### 7.2 Stage B — the pipeline in miniature, on the cluster

Ten jobs, one tune, small event count — **ten because ten is the block count**,
so the smoke path exercises the real SEM boundary rather than a degenerate one.

| step | what |
|---|---|
| B1 | `make check` with ROOT present |
| B2 | render + submit **10 jobs × small N**, one tune (MONASH: cheapest at 377 s/job for 100 k) |
| B3 | per-job raw validation — the production gate runs on every raw file anyway |
| B4 | the one-pass reduction → 10 directories × 300 pair files |
| B5 | `validate_pair_directory.sh` on one directory |
| B6 | merge: one central @10 inputs + the blocks |
| B7 | `validate_pair_block_closure.sh` — **and the count table still reads 2100 / 1500** |
| B8 | `extract_species_decomposition.py` on the small central, **passing `--decay-map` explicitly** |

> **B7 is the point of the whole design.** The closure counts are
> `n_objects × 300 pair files`, and the 300 comes from the pair registry, not
> from statistics. **A ten-job smoke run produces the same 2100/1500 as the
> 3000-file production**, so the newcomer sees the real verdict table — including
> that 1800/600 would be failure — on a run that costs an hour.

**Sizing is not pre-registered.** Per the two-tier rule, whoever runs it first
records the wall clock and puts the number in the doc. No forecast is made here.

---

## 8. THE DECISION SHEET — one pass

> **STATUS 2026-08-12: with the owner, being ruled on now, together with the 13
> deletion-candidates in `REPO_FILE_CENSUS.md`. Nothing moves until that ruling
> returns.**

**Each row has a recommended default. Approving the plan means taking the
defaults unless a row is overridden.**

| # | decision | recommended default | why |
|---|---|---|---|
| **D1** | Numeric prefixes (`1_generation/`) or plain names? | **plain names** — `generation/`, `analysis/`, `merging/`, `extraction/`, `plotting/` | ordering is a nice-to-have; unusual paths in a physics repo are a lasting cost |
| **D2** | The split bb/cc/qq chain — live or attic? | **`attic/split_chain/`** | nothing calls it; `README.txt` says it "remains available", which `attic/` satisfies. **Override if the paper needs a reference sample from it** |
| **D3** | `README.txt` — delete or attic? | **delete, folding its split-chain sentence into `README.md`** | it exists only to say `README.md` supersedes it |
| **D4** | Move golden artifacts to `artifacts/`? | **YES** | it is the clearest legibility win; §4.2 states the cost honestly. **Override to "leave them in `AnalysisScripts/`" if the one-session budget looks tight** — that single override removes the largest risk in the plan |
| **D5** | `plotting_documentation.md` (root, 17 KB) vs `plotting/README.md` (21 KB) | **fold into `plotting/README.md`, attic the root copy** | two overlapping plotting docs is a navigation cost |
| **D6** | `B_Balancing_GeneralPlotting.C` exists in **two** directories | **keep the `Balancing_and_Sampling/` copy** (it goes to `docs/history/studies/`), attic the `plotting/` one | the study copy is the one with context |
| **D7** | Does the smoke path ship as its own `docs/SMOKE_PATH.md` or a `README.md` section? | **`README.md` §3** | a newcomer should not need to find a second file |
| **D8** | `tools/docs_check.sh` — keep or attic? | **keep** | advisory, never fails, costs nothing |
| **D9** | Does the restructure land on `physics-focus`, or wait for the `main` ↔ `physics-focus` decision (**B8**)? | **land on `physics-focus`** | `WORKSPACE.md` establishes both are refs in one object store, so B8 stays a ref operation either way. **This plan does not resolve B8** |
| **D10** | `Validation/` → `validation/` (case-only) | **DO NOT DO IT** | macOS is case-insensitive, Nikhef is not; a case-only `git mv` is a known corruption. Keep `Validation/`, or pick a genuinely different name |

### 8.1 Two questions that are not mine to default

**Still open.** The 2026-08-12 rulings closed four of my questions (the v1
default, the charm-M7 logs, the contention pre-registration, the unrun macros)
and reshaped the disk plan. These two were not among them:

| # | question |
|---|---|
| **Q1** | **`Balancing_and_Sampling/ATTENTION.txt`** records that double-counting is *not* implemented from 23 Dec onwards and results "will have to be divided by 2 manually", ending *"remains to be checked"*. **Nothing in the tree says it was checked.** Does this affect anything published? A physics question, separate from the restructure |
| **Q2** | **Are the paper figures digest-pinned anywhere?** `PAPER_FIGURE_PROVENANCE.md` exists; whether any figure *output* has a recorded digest was **not established**. If not, the freeze contract has a hole on the figure side that `GOLDEN_OUTPUTS.md` cannot close by itself |

---

## 9. RISKS, NAMED

| # | risk | mitigation |
|---|---|---|
| **R1** | **Quiet-fail paths** (§4.2) — a tool exits 0 with an output silently missing | grep `.exists()` guards before moving `artifacts/`; the gate checks digests, which catches a missing regeneration |
| **R2** | **Case-only rename** `Validation/` → `validation/` | **D10 default: do not do it** |
| **R3** | **The frozen Nikhef checkout resolves paths.** `extraction/pipeline/tune_extract.sh` `cd`s to `/data/alice/ipardoza/Hadronization` and sources `./setupEnv.sh`; the guard hook pins the commit | the restructure lands when the pipeline is done — **not a new gate, a scheduling fact**. Per directive item 6, nobody touches the live pipeline |
| **R4** | **Line-ending or whitespace normalisation on `anchors/**`** breaks C7 (probe lines byte-identical) and every digest in `GOLDEN_OUTPUTS.md` §7 | mark `anchors/**` binary; the digest gate catches it |
| **R5** | **Doc links rot.** ~118 history files cross-reference each other and the active docs | accept prose rot in `docs/history/`; fix links only in the active set |
| **R6** | **Restructuring during external review** changes the paths a reviewer was given | do it **before** the review pack ships, or **after** it is accepted — never during |
| **R7** | **`anchors/MANIFEST.md` §3 is stale in two places** and the restructure will carry it forward verbatim: it still lists Task 2 (`sigmab_runs/`) as *"in flight this session; anchor them when harvested"* when `anchors/sigmab_raw/` holds all ten logs, and it predates the charm-M7 anchoring in `b74e588` | **one edit while the file is already being moved.** It is the manifest a reviewer reads to check provenance, so a stale gap list reads as a missing anchor |
| ~~**R8**~~ | ✅ **RULED AND CLOSED 2026-08-12.** The collision I raised — `decompose_with_block_sems.py:84` imports `compare` from `compare_subset_parent`, so I2 and the pinned E4 test share one function — is resolved by making the **null mode a REQUIRED argument with no default**: I2 passes MAD, the pinned test passes binomial **explicitly**, commented as deliberately pinning the historical computation | **not this session.** JUNCTIONS harvest, first item, one commit + suite. The ruling is a **better answer than either option I offered** — see `GOLDEN_OUTPUTS.md` §2.11a |

---

## 10. THE DISK SIDE — RESHAPED BY THE FINDINGS. IT IS A MAP, NOT A MOVE

> **Owner ruling, 2026-08-12, after the metadata walk:** *no physical checkout
> move; code/data separation by mapping; big trees stay put;
> `b-hadron-fractions` out of scope.*

**The earlier draft of this section proposed physically relocating everything
into a `hadronization/` root. The inventory killed that proposal, and the ruling
records it.** Moving the frozen checkout means moving **445 GB across NFS** on a
volume at **97 %** — to achieve a legibility goal that a **document** achieves
for free. **The consolidation is now a mapping exercise. Nothing large moves.**

### 10.1 What the inventory found, and why it changed the shape

| finding | measure |
|---|---|
| the frozen checkout `Hadronization/`, total | **445 GB** |
| — of which `RootFiles/` | **409 GB**, gitignored (`.gitignore:3`) |
| — of which `.git/` | **23 GB** |
| — gitignored working data in total (`RootFiles`, `Production`, `AnalysisResults`, `AnalyzedData`) | **≈ 423 GB** |
| — tracked source and docs | **≈ 25 MB** |
| `hadronization_production/` | 304 GB |
| `hadronization_merged/` | 41 GB |
| `b-hadron-fractions/` — a different project | **1.2 TB** — **out of scope by ruling** |
| `/data/alice` | 32 T, **97 % used, 1.1 T free** (measured 2026-08-12) |

> **The checkout is 0.006 % source code by volume.** "Advance the checkout" is a
> ref update on a 23 GB object store; "move the checkout" is 445 GB of data that
> is not in the repository and never was. **The problem was never that the data
> is in the wrong place — it is that nothing says which is which.**

### 10.2 The deliverable: a logical map over the physical layout

A single committed document — the natural home is a section of
`docs/WORKSPACE.md`, which already owns the Nikhef workspace — stating **role →
physical path**, so a newcomer can tell code from data without moving a byte:

| logical role | physical path | class |
|---|---|---|
| frozen analysis checkout (**code**) | `Hadronization/` — tracked files only | code |
| campaign-control checkout (**code + the seed ledgers**) | `Hadronization-full-production/` | code |
| **working data inside the frozen checkout** | `Hadronization/{RootFiles,Production,AnalysisResults,AnalyzedData}/` | **data — gitignored, not part of the repository** |
| campaign inputs | `hadronization_production/HF_RUN3_V1/` | data |
| analysis outputs | `hadronization_analysis/HF_RUN3_V1/` | data |
| merged outputs | `hadronization_merged/` | data |
| per-tune results | `tune_runs/` | results |
| pinned generator | `pythia_stock_8317/` | software |
| retained partials | `archive/` | **archive — untouchable** |
| per-investigation scratch | ~25 directories, `NIKHEF_DISK_INVENTORY.md` §3 | scratch |
| out of project | `b-hadron-fractions/`, `HRP/`, `Axions/`, `EDMs/` | **out of scope** |

**What may still physically move, because it is small and has no live reader:**
the ~70 loose top-level files (`NIKHEF_DISK_INVENTORY.md` §4) into
`scratch/misc/`, `scratch/deploys/` and `archive/bundles/`. **Total well under
1 GB.** That is the whole physical component now.

### 10.3 Rules that survive the reshape

1. **Retained partials are untouchable** — *moved, never deleted*, with a
   committed manifest.
2. **The seed ledger stays with its checkout.** `3557/3557` burned seeds are
   recorded under `Hadronization-full-production/campaigns/*/seed_ledger.jsonl`;
   nothing re-derives historical seeds.
3. **Merge scratch is frozen until the band is scored** (`GOLDEN_OUTPUTS.md` §5,
   N2 — the timing evidence *is* the mtimes).
4. **Checksums belong to a move.** With almost nothing moving, almost nothing
   needs one — which is itself an argument for the reshape.
5. **Nothing is deleted.**
6. **`hadronization_merged/*.partial.*` is not junk while a merge runs.** One
   such directory had an mtime of minutes old during this walk: the JUNCTIONS
   central being written.

### 10.4 The one live disk question — assigned to the main line

**Headroom on the merge target volume, for the ~60 GB the merge still has to
write.** Owner's ruling: **main line runs one `df`, records one line.**

**Not run here** — it is assigned, and it is a live-pipeline observation.
**A prior data point, offered so that check is a confirmation rather than a
discovery:** `df -h /data/alice` during this session's metadata walk returned
**32 T total, 31 T used, 1.1 T available, 97 %**, at 2026-08-12. `/data/alice`
is the volume `hadronization_merged/` sits on. **1.1 T against ~60 GB is
comfortable — but that reading is hours old on a shared 97 %-full filesystem
with another user active, which is exactly why the ruling asks for a fresh
one.**

---

## 11. WHAT THIS PLAN IS NOT

1. **Not approved.** §5 is a proposal; §8 is the approval sheet.
2. **Not a new gate.** The acceptance gate is the owner's: suite green +
   digests. No verification is invented here.
3. **Not a physics change.** No analysis, no re-running, no verification jobs
   were performed by the session that wrote it.
4. **Not a resolution of B8** (`main` vs `physics-focus`) — D9.
5. **Not a licence to delete.** Everything dead goes to `attic/` or
   `docs/history/`.
6. **Not applicable to `Paper/`**, which was not examined.
