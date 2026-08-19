# Hadronization — heavy-flavour baryon partnering across three PYTHIA tunes

**A study of whether a heavy baryon's flavour-balancing partner is itself a
baryon**, compared across MONASH, JUNCTIONS and CLOSEPACKING — three PYTHIA
8.317 tunes that differ in colour reconnection. pp at 13.6 TeV.

**This README is a rebuild guide.** It is ordered by what you would actually do,
starting from nothing. For *what the pipeline is and why*, read
[`ARCHITECTURE.md`](ARCHITECTURE.md) — it assumes no ROOT or PYTHIA background.
For *where the project stands right now*, read [`STATE.md`](STATE.md).

---

## 1. PREREQUISITES

| | |
|---|---|
| **PYTHIA** | **8.317**, stock upstream, built from the official pythia.org tarball (`sha256 1ae551d1…45adf`), unmodified, `-std=c++20` |
| **ROOT** | **6.30/01** — the ALICE CVMFS build; `root-config --version` must report `6.30.01` |
| **Python** | 3.9+; the tooling is standard-library only |

**There is no container and nothing rebuilds PYTHIA for you.** The tarball
checksum is recorded; a third party must build it themselves. This is the
project's largest portability limitation and it is recorded as such in
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) §4.

```bash
source ./setupEnv.sh
```

`setupEnv.sh` asserts both versions and **exports nothing on a mismatch** — so a
silent environment drift cannot reach a number.

---

## 2. CHECK THE CHECKOUT

```bash
make check
```

Runs `doctor` (environment), `cards` and `cards-current` (the tune cards match
the shared configuration), `registry` (the generated headers are current), the
**36 Python contract tests**, and finally `env-verdict`.

> ### `make check` is a SOURCE-CONTRACT suite. Here is what it does NOT certify.
>
> It does **not** run: the 300-file merged product, the closure gate against
> real data, the current plotting chain, the PYTHIA runtime, or the published
> extraction. A green run says the committed source, generated headers, tune
> cards and registry agree with each other and with their fixtures. **It says
> nothing about any published number.**
>
> **This was a live defect, not a hypothetical** (`docs/ERROR_RECORD.md`,
> review finding A7): on `f0e67dc` the suite reported 30/30 and exited 0 on a
> host with Homebrew ROOT 6.38.04 against a pinned 6.30.01, no PYTHIA and no
> CVMFS — while `doctor` in the *same run* reported two blocking findings.
> Every part behaved as designed; the emergent result was a fully green check
> on a machine that cannot run the pipeline at all.
>
> **So `check` now ends with an environment verdict and fails on an off-pin
> runtime.** Laptop work is still expected — declare it:
>
> ```bash
> HF_ALLOW_UNPINNED_ENV=1 make check
> ```
>
> which prints, and records, that the run is not a pinned-runtime
> certification.

> ### ⚠ Without ROOT, `make check` is not green — it is *smaller*
>
> **Five of the tests compile or run a ROOT macro and raise rather than skip.**
> A machine with no ROOT reports a pass over a reduced denominator, so the
> machine that *cannot* run the pipeline is the one that looks healthiest.
>
> **A green run prints `ROOT: /path/to/root` at the top.** If it prints
> `ROOT: not found`, the result is not a pass. `tools/run_tests.sh:13-15` says
> so too.

---

## 3. THE SMOKE PATH — do this before anything long

**Prove the chain end to end before committing to a 562-CPU-hour campaign.**
Two stages: the first needs nothing but Python, the second needs a cluster hour.

### 3a. Repo only — no ROOT, no PYTHIA, no cluster

Every one of these reads committed inputs with committed tools and finishes in
seconds.

> **CORRECTED 2026-08-13 — this used to say "This is the entire extraction
> chain." It is not** (review finding B2). These commands rebuild the decay
> maps and re-aggregate committed logs. They do **not** project any ROOT input,
> perform the block decomposition, produce the observable, or plot anything.
> The real chain starts at a 300-file merged directory that this repository
> does not commit. Call this what it is: **the map-and-aggregate smoke path.**

```bash
# rebuild decay-parent map v1.1 from the committed probe output
tools/build_decay_parent_map.py \
  AnalysisScripts/anchors/f4_probe/f4_probe_v1.out \
  --ordinals AnalysisScripts/species_ordinals_v2.json --out /tmp/v11.json

# rebuild map v2 (the species-level splits) on top of v1.1
tools/build_decay_parent_map_v2.py \
  AnalysisScripts/anchors/f4_probe/f4b_probe.out \
  --ordinals AnalysisScripts/species_ordinals_v2.json \
  --v1 AnalysisScripts/decay_parent_map_v1_1.json \
  --weights AnalysisScripts/anchors/extraction_dual/per_species.csv \
  --out /tmp/v2.json

# the M7 INCLUSIVE-LEVEL unresolved-origin diagnostic, both sectors, from the
# committed block logs. NOT a bound on the pair observable -- see
# docs/M7_UNRESOLVED_SYSTEMATIC.md's scope banner (review finding A2).
extraction/aggregate_m7.py AnalysisScripts/anchors/m7_blocks/*.log
extraction/aggregate_m7.py AnalysisScripts/anchors/m7b_blocks/*.log

# the anchor-vs-parent bin comparison that found the E4 defect.
# --null is REQUIRED and has no default: 'binomial' is the historical
# computation behind "30 of 88"; 'mad' is the robust null used for integrity
# work since 2026-08-13, under which the same comparison flags 0 of 88 -- a
# blind spot for BROAD defects (docs/ERROR_RECORD.md E4), not a clearance.
extraction/compare_subset_parent.py \
  AnalysisScripts/anchors/extraction_dual/per_species.csv \
  AnalysisScripts/anchors/merged_monash_central/per_species.csv \
  --null binomial --expect-scale 9.9986

# the three-tune table, both conventions on a COMMON row set. Each tune's own
# top-8 differs -- MONASH's carries B+/B-, the CR tunes' carries Lambda_c -- so
# three top-8 lists would not be comparable column to column. Run here on the
# committed MONASH anchor alone, which reproduces docs/MONASH_CENTRAL_TABLE.md
# section 0; add JUNCTIONS=<dir> CLOSEPACKING=<dir> for the full table.
extraction/three_tune_table.py \
  MONASH=AnalysisScripts/anchors/merged_monash_dedup

# the per-tune b-baryon particle/antiparticle advisory -- step 2 of the ladder
# in docs/B_BARYON_ADVISORY_DIAGNOSTIC.md. RAW weights, no map applied, which
# is the basis step 1 used to exonerate the map. Advisory only: it reports a
# direction and never fails, so do not read its exit status as a verdict.
extraction/bbaryon_tune_advisory.py \
  MONASH=AnalysisScripts/anchors/merged_monash_dedup
```

**Check the named output line, never the exit status.** `rc=0` is not evidence —
ROOT returns 0 when it cannot even find a macro's entry point. The expected
lines are in [`docs/GOLDEN_OUTPUTS.md`](docs/GOLDEN_OUTPUTS.md) §4; the two that
matter most are `map_sha256=dd502a10c5932fff` and
`sha256=c9593c9c0a7c4ec2`.

> **Get those two digests and 30 flagged bins, and you have independently
> reproduced the decay-map conjugation fix and the anchor defect from scratch.**

### 3b. The pipeline in miniature — ten jobs, one tune

**Ten jobs, because ten is the block count** — the smoke run then exercises the
real statistical boundary rather than a degenerate one.

| step | command |
|---|---|
| render + submit 10 small jobs, MONASH | `make submit-smoke ORDINAL=<n>` |
| watch | `make status` |
| reduce each raw file | `analysis/run_status_analysis.sh` |
| validate one pair directory | `Validation/validate_pair_directory.sh <dir>` |
| merge central + blocks | `merging/merge_root_files.sh …` |
| **closure** | `Validation/validate_pair_block_closure.sh <central> <block_base> v3` |
| extract | `extraction/extract_species_decomposition.py <central> --decay-map AnalysisScripts/decay_parent_map_v1_1.json` |

> **The closure step is why the smoke path is worth an hour.** Its counts are
> `n_objects × 300 pair files`, and the 300 comes from the pair registry, **not
> from statistics**. So a ten-job toy run returns the **same 2100 content /
> 1500 invariant** verdict as the 3000-file production — including the trap that
> **1800 / 600 is a failure that looks like a pass** (it means the run resolved
> against the v2 schema and never checked the species objects at all).

**Sizing is not pre-registered.** Whoever runs it first records the wall clock
here.

---

## 4. REBUILDING A PUBLISHED NUMBER

Every published number is either regenerable from committed inputs, or recorded
as not regenerable with the reason. **There is no third category**, and the list
is [`docs/GOLDEN_OUTPUTS.md`](docs/GOLDEN_OUTPUTS.md):

- **§2** — every frozen artifact with its sha256 and its regeneration recipe;
- **§4** — the recipes as one ordered list, each with its positive check;
- **§5** — the seven things that **cannot** be regenerated, and why. The
  extraction anchor's provenance is unrecoverable; the merge timing exists only
  as filesystem mtimes; PYTHIA is a personal build.

---

## 5. THE FULL PIPELINE, AND WHAT IT COSTS

```
generation/  →  raw/        3000 files, 300M events, 3 tunes
analysis/    →  per_job/    3000 directories × 300 pair files
merging/     →  3 centrals (1000 inputs) + 30 blocks (100 each)
Validation/  →  closure at scale: 2100 content / 1500 invariant
extraction/  →  species decomposition + block SEMs  ← the paper's number
plotting/    →  figures
```

| | |
|---|---|
| full production | **562.5 CPU-hours** (MONASH 104.7, JUNCTIONS 183.1, CLOSEPACKING 274.7) |
| | **quote 562.5, not 390** — the 390 figure circulates verbally and descends from superseded medians |
| retry overhead | ~2.7 % of jobs hit the hang guard and regenerate; budget a few percent |
| merge | 33 objects; measured against a 65–77 h pre-registered band |

**Seeds are deterministic and ledgered.** `seed_for(campaign_ordinal, tune, job,
attempt)` always renders the same submit file, and rendering **refuses** a seed
the ledger has already burned — a real duplicate-seed collision once voided two
pilot campaigns.

---

## 6. LAYOUT

| path | what |
|---|---|
| `generation/` | producer, tune cards, generated registries, Condor submission |
| `analysis/` | the one-pass reduction, raw → 300 pair files |
| `merging/` | merge driver and ROOT macros |
| `extraction/` | species decomposition, decay maps, block SEMs, M7 aggregation |
| `plotting/` | figure macros, configurations, `run_paper_plots.sh` |
| `AnalysisScripts/` | **frozen artifacts** — species axis, decay maps, `anchors/` |
| `Validation/` | ROOT audits, pair-directory and closure gates |
| `tools/` | campaign management, renderers, guards, `doctor` |
| `config/` | signed registries and contracts |
| `tests/` | 37 Python contract tests, 5 C++ |
| `docs/` | the active record; `docs/history/` the archaeology |
| `attic/` | code with no live consumer, kept rather than deleted |

**The split bbbar/ccbar chain lives in `attic/split_chain/`.** It remains
available for independent reference samples and comparisons to older
productions; nothing in the current pipeline calls it.

---

## 7. WHICH DOCUMENT OWNS WHAT

| Area | Owner |
|---|---|
| What the project is, for a non-specialist | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Where the project stands — frozen / pending / not planned | [`STATE.md`](STATE.md) |
| Every published number, its digest and its recipe | [`docs/GOLDEN_OUTPUTS.md`](docs/GOLDEN_OUTPUTS.md) |
| The physics contract — schemas, selectors, thresholds, pinned versions | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) |
| Why each choice is what it is, and the evidence | [`docs/DESIGN_AND_RATIONALE.md`](docs/DESIGN_AND_RATIONALE.md) |
| What went wrong, who caught it, what now prevents it | [`docs/ERROR_RECORD.md`](docs/ERROR_RECORD.md) |
| **What each executable is for, and how they connect** | [`docs/COMPONENTS.md`](docs/COMPONENTS.md) |
| What was removed from `HEAD`, and why | [`docs/REMOVALS.md`](docs/REMOVALS.md) |
| What was renamed or moved, and what was deliberately not | [`RENAMES.md`](RENAMES.md) |
| Cluster operations — submitting, monitoring, the hang guard | [`generation/submit/Condor_README.md`](generation/submit/Condor_README.md) |
| Machine setup, dependencies, storage | [`docs/WORKSPACE.md`](docs/WORKSPACE.md) |
| A subsystem's own mechanics | that directory's `README.md` |

**A code change and its documentation change land in the same commit.** The rule
has teeth because it has failed before: `PhaseSpace:pTHatMin = 2.0` shipped with
no design section, and the pair-file object contract behind a 900-error analysis
failure lived only in a C++ comment. Both are written up now in
`docs/DESIGN_AND_RATIONALE.md` §§3.12–3.13.

---

## 8. WHAT IS NOT EVIDENCE

None of these is evidence that a result is sound, and each has been mistaken for
it at least once:

- a dirty or `--development` report;
- a validation receipt whose state is FAIL;
- a nonempty ROOT file without its receipt;
- a Condor queue reaching zero;
- 500 submitted jobs described as 500M analysed events;
- `rc=0` from a ROOT macro;
- a `make check` pass with no ROOT;
- an agent-authored physics sign-off.
