# What changed since Paul's pull request — a report for the supervisors

**Audience.** Physicists who last saw this project at Paul Veen's pull request
#13. You know the physics. You do not know this repository.

**The anchor.** Every change in this report is measured from commit
`11884cf1ad3613e8e6997bbff32d48a3e7d89570` — *"Merge pull request #13 from
ppoava/main"*, **2026-07-28 19:29:23 +0200**. That is the last state the
supervisors saw.

**The window.** 2026-07-28 to 2026-08-19, **22 days**, with commits on **18**
of them (`git log --format=%ad --date=short 11884cf..systematics-harvest`).

**The two heads measured.** `main` at `0fa14de` (2026-08-19 18:39:22 +0200) and
`systematics-harvest` at `859bde6` (2026-08-19 21:00:45 +0200). `main` carries
**2** commits past the anchor, the second a squashed rebuild;
`systematics-harvest` carries **432** in their original sequence, and its
merge-base with `main` is the anchor itself. **434 commits total.**

| measure | anchor → `main` | anchor → `systematics-harvest` |
|---|---|---|
| files changed | 1306 | **1331** |
| insertions | 205,580 | **239,271** |
| deletions | 73,365 | **73,359** |

Change types on the longer line, with rename detection: **640 added, 607
deleted, 4 modified, 80 renamed** (`git diff --name-status -M`).

**Authorship in the window:** 432 commits, all by Iñaki Pardo Zambrana (420
under one spelling of the name and 12 under another; `6a3ddb4` adds a
`.mailmap` that unifies them).

---

## 1. Summary

The physics question, the observable and the objective did not change. One
external adversarial review and eight internal defects showed that the
apparatus behind the pull-request numbers could not support them. The largest
defect counted every trigger 24 or 26 times, so the published decomposition
total of **1,298,655,240** entries is really **53,662,416**. The rebuild
answers it with a pipeline-ordered layout, a digest-pinned reproducibility
contract, a suite that grew from **nothing** to **62 of 62 passing**, and a
pre-registered systematics programme. Two campaigns finished in the window: the
sealed three-tune central campaign at **100 M events per tune**, and seven
variation campaigns at **30 M each**. The three-tune central table is
**FINAL**, while the tune separation and the multiplicity trend stay
**provisional** — both rest on the sealed nominal, and two variation campaigns
are still merging.

---

## 2. What has not changed

**The physics question is the same.** When a heavy quark is produced with its
antiquark partner, and one of the two ends up inside a baryon, what does the
other end up in — a baryon or a meson? `ARCHITECTURE.md` §1 states it in that
form and states nothing else.

**The observable is the same.** The OS−SS partnering yield, formed from
trigger–associate pairs, per multiplicity class, per tune.

**The tune comparison is the same three tunes.** MONASH, JUNCTIONS,
CLOSEPACKING (`ARCHITECTURE.md` §1).

**The objective is the same.** Quantify the size of the bundle-to-bundle
difference in that observable.

**The manuscript is untouched.** `Paper/**` holds exactly one tracked file at
both ends of the window, `Paper/Tables/generated_heavy_flavor_summary.tex`.
`git diff 11884cf systematics-harvest -- Paper` returns nothing, so not one
byte changed.

**This work is a rebuild of the apparatus, not a redefinition of the goal.**
One interpretive claim was withdrawn, and the withdrawal narrows a claim rather
than changing the question. `ARCHITECTURE.md` §1 previously said the tunes
"differ in exactly that machinery" and then conceded that the result could not
be attributed to junctions. Review finding **A13.4** caught the contradiction.
Measured from `config/tune_difference_allowlist_v1.json`: **28 allowed tune
differences across nine parameter families, of which 8 are
`ColourReconnection`**. `StringFlav` (3) and `StringZ` (3) set baryon
production directly, so they are alternative explanations rather than
incidental. The comparison is bundle-to-bundle, and the claim of an isolated
junction mechanism is withdrawn.

---

## 3. Why anything changed

Eight defects are recorded in `docs/ERROR_RECORD.md`, all found inside this
window — the file itself was created on 2026-08-11 in commit `e3c6083`. Each
entry names the defect, how it was caught, and the mechanism that now prevents
it. They are ordered here by what each would have done to a published number.

### 3.1 E5 — the published decomposition counted every trigger 24 or 26 times

**Found by external adversarial review of `f0e67dc`, finding A1. CONFIRMED.**
This is the largest defect in the record and the reason for most of the
rebuild.

**The mechanism, read from the code.** `hFlavourClosure` and
`hFlavourClosureSpecies` are owned by the **trigger**, not by the
trigger–associate pair. The analysis builds one accumulator per distinct
trigger PDG (`analysis/status_analysis_THnSparse_qq.C:870-879`) and writes that
same object into **every pair file sharing that trigger** (`:1179-1191`).
`extraction/extract_species_decomposition.py` iterated all 300 files and summed
every projection. It built `per_pair_species` and never read it.

**Measured from the committed registry, not assumed.** Each of the six charm
triggers appears in **24** pair files and each of the six beauty triggers in
**26**; 144 + 156 = 300.

**The published product carries the defect, not merely the code.** Under
replication every charm-only species total must divide by 24 and every
beauty-only one by 26. Measured in
`anchors/merged_monash_central/per_species.csv`: **45 of 45** charm-only
species divide by 24, and **42 of 42** beauty-only ones divide by 26. The gcd
of all 94 nonzero totals is **exactly 2** = gcd(24, 26). The two negative
controls do not reproduce it. Only 5 of 45 charm-only totals also divide by 26,
and only 2 of 42 beauty-only ones also divide by 24. Under a
correct extraction that pattern has probability ≈ 10⁻¹²¹.

**The corrected event count.**

| quantity | published (replicated) | corrected |
|---|---|---|
| total entries | **1,298,655,240** | **53,662,416** |
| kCentralGround | 679,701,042 — 52.3388 % | **52.4959 ± 0.0074 %** |
| kExcludedVector | 605,835,226 — 46.6510 % | **46.4946 ± 0.0079 %** |
| kExcludedExcited | 13,118,780 — 1.0102 % | **1.0095 ± 0.0012 %** |
| charm share of sector total | 89.2404 % | **89.9852 %** |
| beauty share of sector total | 10.7596 % | **10.0148 %** |

The ratio is **÷ 24.2004**. Two steps produced that corrected total. An
arithmetic inversion of the committed replicated CSV first bracketed it at
53,662,414 … 53,662,828. A **live re-extraction on 2026-08-13** then measured
it — central plus ten blocks, fixed extractor, ROOT 6.30/01 on pin — at
**53,662,416**, two counts above the predicted floor (`STATE.md`, MONASH
section).

**The shape of the error matters for what survives.** Within-sector ratios are
**exactly unchanged**, because the common factor cancels: D⁰/D⁺, D̄⁰/D⁻,
Λ_c⁺/D⁰, B⁺/B⁰, Λ_b⁰/B⁰ and B⁻/B̄⁰ all give ratio-of-ratios = 1.000000.
**Cross-sector and absolute quantities were wrong. Within-sector ratios never
were.**

**Had it survived**, the paper would have quoted an absolute entry count 24×
too large, a charm/beauty split wrong by 0.74 pp, and category shares wrong by
0.16 pp — with every self-check passing.

**Why nothing caught it.** Every self-check was replication-blind.
`from_species == from_closure` holds exactly, because both views carry the same
duplication. `MONASH_CENTRAL_TABLE.md` read that identity as *"No loss, no
duplication"*, which it establishes neither. `DESIGN_AND_RATIONALE.md` had
called the duplication a "storage wart, not a correctness problem" and quoted a
stale factor of 18.

**The replication is wider than the closure histograms.** A later annotation to
E5 records three classes of replicated object.

- `summed MULTIPLICITY` is **event-level** and identical in **all 300** files.
- `hTrKinematics` and the four closure objects are **trigger-owned**, at
**24× charm and 26× beauty**.
- Only the `hCorrelations` family is genuinely per-pair.

**The rule now reads: in a v3 merged pair directory, only the `hCorrelations`
family is additive across files.** Anything trigger-owned or event-level must
come from one file, or be verified identical across files.

### 3.2 E1 — the decay map did not conjugate antiparticle decays

**17.8 percentage points on D⁰**, the largest number in the
experiment-comparable table: published as **45.95 %** when it is **28.13 %**.
PYTHIA stores one decay table per particle and derives the antiparticle by
conjugation, so `particleDataEntryPtr(-413)` returns the `+413` entry.
`tools/f4_probe.cc` recorded the products verbatim, and
`decay_parent_map_v1.json` carried them verbatim, mapping **D\*⁻ and D̄\*⁰ to
D⁰ instead of D̄⁰**.

**Had it survived**, the table's charge-separated rows would have been wrong by
that much. A 4.49× D⁰/D̄⁰ asymmetry would have reached publication in a sector
that prompt charm produces charge-symmetrically to within a few per cent.

**How it was caught.** By a check on the physics rather than on internal
consistency: **C2 — every split product must carry the parent's heavy-quark
sign** — specified by the owner for the v2 build. It fired on the first split
it examined and refused to write an artifact.

**The generalisable lesson, in the record's own words.** A reimplementation
check proves agreement, not correctness. The v1 re-derivation reproduced the
table exactly and correctly; both implementations were faithfully consuming the
same wrong artifact.

### 3.3 E4 and E6 — one arithmetic mistake wearing three disguises

**E4 (2026-08-11).** An unprovenanced extraction anchor,
`AnalysisScripts/anchors/extraction_dual/per_species.csv`, produced a
pre-registered ordering test result of **MISS, "exactly reversed", −7.4 σ**,
stated with full statistical confidence. The merged central gave **+1.35 % ±
0.27 % (+5.1 σ)**, the predicted sign. The MISS was retracted the same session.

**E6 (2026-08-13) dissolves both numbers.** Multiplying every count by a factor
**R** leaves fractions and fractional deviations exactly unchanged but scales a
binomial pull by **√R**. E5's replication therefore inflated every binomial
significance computed on extraction outputs. **Measured: 5.03×** across ten
block-vs-central comparisons (replicated 4.800 ± 0.519 against deduplicated
0.955 ± 0.096). **Predicted: √24.2 = 4.92.**

Divide by 5.03: **−7.4 σ becomes −1.47 σ** and **+5.1 σ becomes +1.01 σ**. Both
are null, so the retraction stands but the confirmation does not. **The
charge-ordering question is unresolved rather than settled either way** — owner
ruling, no further investigation.

**One invented mechanism was retired with it.** A "~4.75× overdispersion from
event clustering" had been proposed, accepted, and used to justify an
`--i2-advisory` escape hatch and a replacement null. Deduplicated blocks sit at
**0.955 ± 0.096**, consistent with binomial. **There is no overdispersion.**
The record's lesson: a mechanism that explains your artifact is not evidence
for the mechanism.

**Had E6 not been found**, the paper would have carried a withdrawn warning
that "Poisson/binomial errors on these fractions are ~5× too small" as a
property of the physics, when it is a property of counting each trigger 24 or
26 times. **No published number moves**, because the paper's uncertainties are
empirical block SEMs, which measure dispersion rather than assuming it.

**The E4 quarantine stands** on grounds that need no statistics: the anchor is
unprovenanced, and its physics result was contradicted by two traceable
datasets.

### 3.4 E7 — a correctness guard that selected on the outcome variable

The A2 permissive variation threw when a job restored nothing, to stop a silent
no-op passing as a clean null. The intent was sound. The restoration rates are
tune-dependent by three orders of magnitude:

| tune | restored per M events | zero-restoration jobs, of 100 |
|---|---|---|
| MONASH | **6.2** | **49** |
| JUNCTIONS | 1 219.4 | 0 |
| CLOSEPACKING | 1 228.7 | 0 |

At 6.2 per million a 100,000-event job restores 0.62 on average, so zero is the
modal outcome — Poisson gives e⁻⁰·⁶² = 54 %, and 49 % was observed. **The guard
discarded roughly half the MONASH sample and none of the other two, and the
discarded half was exactly the jobs where the variation changed least.**

**Had it survived**, one arm of the comparison would have been selected on the
outcome variable in the direction that inflates the measured shift. **Nothing
entered a calculation**: the guard blocked promotion, so the held jobs never
became inputs. The assertion moved to `check_campaign_restoration()` in
`analysis/a2_block_shift.py`, at the level where zero restorations really is a
defect.

**The rule this yields.** Provenance and physics are different questions, and
one check must not answer both. *"Did the right code run?"* is answered per job
by identity. *"How much did it find?"* has zero among its answers, and zero is
data.

### 3.5 E8 — two guards keyed on a process identity, neither saying what it meant

Two guards watched a PID as a proxy for completion, and they failed in opposite
directions. The checkout pinfile read **absence as completion**. A scheduled
reboot killed PID `3675829`, and that satisfied both clauses of a removal
protocol while the merge it protects was still reading the tree.
`tools/merge_supervisor.sh` read **absence as death**, so it would have
restarted a cleanly completed merge into another 12 h 42 m preamble, up to
`MAX_RESTARTS=6`.

**Had the pinfile been acted on**, the freeze would have lifted under a live
merge and a 65 h run would have been invalidated. **Nothing was removed and
nothing was invalidated**: the trap was found before an advance, which is the
only place it could be found for free.

**The remedy already existed and had not been carried across.**
`tools/supervisor_eol_watch.sh` (2026-08-15) keys on a content marker —
`CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=CLOSEPACKING`, the last line of
`merge_root_files.sh`. That is exactly what the pinfile needed, invented five
days after the pinfile was written, for the mirror-image guard. **E8 is a
recurrence of E3.**

### 3.6 E2 and E3 — the two smaller entries

**E2 (2026-08-10).** The test script for the checkout-guard hook ran `rm -rf`
on the directory the candidate hook had been copied into. **No hook was
installed and the test printed "CORRECT" twice** — the "refused" direction
passed because nothing was there to permit it. It was about to certify a safety
mechanism guarding a 65 h run. A test that cannot fail is not a test.

**E3 (2026-08-11).** A mechanism was found and then not applied where it also
held. Three of five registered numbers were missed (V1 5.83 % predicted against
5.7737 % actual; V5 0.054 % against 0.0018 %). **All erred in the safe
direction**, so nothing downstream was harmed. E8 is this same shape again.

### 3.7 The external review, and what it disposed of

**Input: an external adversarial review of `f0e67dc`.** The session that
answered it worked under one rule — *verify before fixing* — and produced
**nine commits, `f0e67dc..80d84fd`**, taking the suite **30/30 → 37/37** with
seven tests added and none removed or skipped
(`docs/history/POST_REVIEW_TIER1_SESSION_20260813.md`).

| finding | disposition |
|---|---|
| **A1** | **CONFIRMED** — the 24×/26× replication. Recorded as **E5** |
| **A2** | **CORRECTED** — M7 relabelled everywhere as an inclusive-level diagnostic. Its only cut is `heavyIsFinal && q_sector != 0`. The claim that unresolved hadrons are "dropped" is corrected: only trigger candidates are |
| **A3** | **CORRECTED** — blocks are FILE/JOB blocks (`canonical_slot % 10`), not `event_id % 10`. File blocking retains job-level effects as between-block scatter, which makes it the conservative choice and the implemented one |
| **A4** | **FIXED** — the closure gate takes a required expected-schema argument, enforced in wrapper and macro. Pre-fix a two-argument invocation was valid |
| **A5** | **FIXED** — extraction requires the exact registry filename set, zero `PROJ_ERROR`, an exact projection count, and an existing decay map. A directory of 299 correct files plus one stray now fails |
| **A6** | **ACTED ON** — `plotting/PAPER_FIGURE_PROVENANCE.md` is one of the three sources of the figure census |
| **A7** | **FIXED** — `make check` ends with an environment verdict and fails off-pin unless `HF_ALLOW_UNPINNED_ENV=1` |
| **A8** | **FIXED** — four scripts made executable; R7 gains `--mode split`; R8 relabelled. Pre-fix R6/R7/R10 exited 126 |
| **A10** | **DECLARED** — the published central estimator is pooled union for the central and block SEM for the uncertainty, *not* the mean of block ratios. Only the top-level contract had disagreed |
| **A11** | **FIXED, and found a second defect while being fixed** — the beauty sign convention was inverted; the helper also sliced the decimal string by length and read five-digit excited baryons as mesons, so I2 skipped both rows of ±14122 entirely. Coverage 200 → **202**. **No committed map value changed**, verified by byte-identical rebuild before and after |
| **A12** | **FIXED** — `decompose_with_block_sems.py` reports I2 as well as I3; `--i2-advisory` is the explicit opt-out. Pre-fix rc=0 on three failures; post-fix rc=4 |
| **A13.4** | **WITHDRAWN** — the tune-causality contradiction, §2 above |
| **A13.6** | **WITHDRAWN** — "what a detector would reconstruct". "Experiment-comparable" is now defined at first use as a branching-weighted particle-level regrouping, with what is not modelled listed |
| **B2, B3** | **CORRECTED** — the stale 18× duplication note, the v2 schema-of-record row, the "No loss, no duplication" claim, and README's "entire extraction chain" |

**Two recipes were wrong rather than merely unrunnable.** **R7** defaulted to
`dominant` mode and reproduced the v1.1 shares (D⁰ 28.1301) while claiming the
v2 split shares (25.2435). **R8** does not compute what it was cited for: the
**0.0018 %** declared as THE NUMBER has **no committed derivation**, and it was
deliberately not reverse-engineered from its rounded value.

**What that session recorded as NOT established**, quoted because a correction
record that reads as a clean bill of health is worth less than none:

- The corrected table had not yet been re-extracted. **It has been since**;
  see §3.1.
- The block SEMs in `MONASH_CENTRAL_TABLE.md` were still the replicated ones.
- The pair-level unresolved systematic did not yet exist.

---

## 4. What was rebuilt

### 4.1 The layout, first, because everything else moves through it

At the anchor the repository held **693 tracked files** in ten top-level
directories. Five directories held almost all of them: `PlottingScripts/`
(**341** files), `AnalyzedData/` (**213**), `Balancing_and_Sampling/` (**75**),
`SimulationScripts/` (**23**) and `AnalysisScripts/` (**16**). **18** loose
files sat at the root, including six `submitCondor_*.sub` variants.

Today it holds **726 tracked files** in a pipeline-ordered layout:

| directory | files | stage |
|---|---|---|
| `docs/` | 215 | records, contracts, pre-registrations, run records |
| `AnalysisScripts/` | 184 | contracts, generated headers, committed anchors |
| `tests/` | 70 | the acceptance suite |
| `plotting/` | 49 | figures |
| `tools/` | 48 | operational |
| `generation/` | 36 | make the events |
| `attic/` | 25 | kept, not live |
| `config/` | 24 | signed configuration |
| `Validation/` | 23 | ROOT audits and closure |
| `extraction/` | 21 | histograms → the paper's numbers |
| `analysis/` | 8 | events → pair counts |
| `merging/` | 4 | 3000 directories → 33 objects |

**The move itself.** One session on 2026-08-12 moved **186 paths by `git mv`**,
history preserved throughout, with **one deletion** (`README.txt`, its unique
sentence folded into `README.md`). Top level went from **30 items to 23**, not
the 18 the plan projected, because two owner overrides kept `AnalysisScripts/`
and `Validation/` under their existing names
(`docs/history/RESTRUCTURE_SESSION_20260812.md` §2).

**Two overrides were correct and are worth stating.** Moving
`AnalysisScripts/*.json` and `anchors/` would have broken **63 distinct
repo-relative paths across 138 occurrences**, including every golden-output
generator and every regeneration recipe. A move from `Validation/` to
`validation/` differs only in case, and a case-only rename corrupts a macOS or
NFS tree rather than cleaning it.

**The path-coupling cost was measured before the move, not discovered after.**
On `9426f38`: 63 distinct quoted repo-relative paths, 138 occurrences, and ~30
further files carrying unquoted `Dir/...` forms (`docs/GOLDEN_OUTPUTS.md`
§1.2).

### 4.2 Generation — `generation/`

**Was:** `SimulationScripts/` plus six `submitCondor_*.sub` files at the
repository root and an `update_submit_paths.sh` script to rewrite them.

**Is:** `generation/{producer,cards,registries,submit}`, with the submit files
**rendered** rather than edited. `tools/render_production_submit.py` (354
lines) and `tools/render_analysis_submit.py` (334 lines) generate them from a
manifest; `update_submit_paths.sh` is deleted.

**Why:** the producer `heavyflavourcorrelations_status.cpp` embeds the registry
checksums, the card sha, the producer sha and the commit into every job, and
**refuses to start if any has moved**. Its binary sha `e54b27bb9e3f…` is
contract **C-3**. Generated headers compile the species and tune-setting tables
*into* the producer, so a job cannot run against a table it was not built for.
`make registry` fails on drift (`docs/COMPONENTS.md` §1).

### 4.3 Production — the campaign machinery

**Was:** hand-edited submit files and a hand-tracked queue.

**Is:** a seed ledger, per-attempt metadata sidecars, a canonical manifest
carrying the schema `hf_canonical_freeze_seal_v2`, and a burned-seed gate at
`config/burned_seeds.txt`. A success-verified queue probe
(`tools/queue_probe.py`) reports `QUEUE_EMPTY count=0` **with the schedd banner
present** — an answered question rather than an unanswered one.

**Why:** the seed is the provenance. `seed = 130000001` for HF_RUN3_V1 MONASH
job 0 is the hand-computable value `SEED_BASE + 3*CAMPAIGN_STRIDE + 0 + 0 + 0`,
verified live from the job's own metadata sidecar
(`docs/campaigns/HF_RUN3_V1_RECORD.md`). Retries are expressible and counted
rather than improvised.

### 4.4 Analysis — `analysis/`

**Was:** `AnalysisScripts/` mixed with generated headers and anchors.

**Is:** the one-pass reduction `status_analysis_THnSparse_qq.C`, its wrapper,
and the A2 systematic's observable, separated from the contracts they consume.

**Why, and what changed inside it:** the reduction is where the physics
definitions live — the trigger requires resolved hard ancestry and the
associate does not, deliberately, because requiring it of both deletes the
same-sign term by construction. Its object list is now **generated from the
contract** rather than hand-maintained, after three hand-kept copies drifted
(`tests/test_pair_object_contract.py`). The wrapper **states its commit rather
than discovering it**: all 301 A2 jobs had died on `ExitCode 128` when it tried
to discover one (`tests/test_analysis_commit_provenance.py`).

### 4.5 Merging — `merging/`

**Was:** `merge_root_files.sh` and `make_subsamples.sh` at the repository root.

**Is:** the same drivers in `merging/`, with the closure gate repaired and the
supervisor re-keyed.

**Why, and what the repair found:** the closure gate's call site had been
**broken since 2026-08-13**, and repairing it found **two** broken call sites,
not one — and the test that was supposed to cover it watched neither
(`docs/SYSTEMATICS_HARVEST_RUN_RECORD.md` §9.4, §10.1). The gate now takes an
input with no default, checked at minute zero rather than after hours of
merging. The merge is resumable by construction. It re-validates promoted legs
rather than redoing them, and that is why the 2026-08-12 reboot at 15 of 33
legs cost hours rather than the campaign.

**The statistical design lives here.** `block = canonical_slot % 10`, ten
disjoint exhaustive subsets of the *input files*, giving the SEM at dof 9. The
driver refuses a tune set that is not equal-exposure and not divisible by ten.
`make_subsamples.sh` records that **no random or bootstrap partition is
permitted for paper inputs** and names the two files that enforce it.

### 4.6 Extraction — `extraction/`

**Was:** extraction scripts inside `AnalysisScripts/`, summing all 300 pair
files.

**Is:** `extraction/` with **21 files**, the densest concentration of
measurement provenance in the tree.

**The load-bearing change is `deduplicate_by_trigger()`.** It sums each
trigger's closure once, keyed by the signed registry. It **fails closed if two
files carrying the same trigger disagree in any bin**. That refusal is the
point: if the files are not copies, the premise of deduplication no longer
holds, and choosing either one is a guess.

**Three further tools exist because of specific defects.**
`extraction/compare_subset_parent.py` gives per-bin z-scores against an
expected scale factor (E4). `tools/reconstruct_deduplicated_decomposition.py`
verifies the E5 fingerprint before inverting and **refuses to "correct" a table
that does not carry the defect**. `extraction/combine_per_class.py` applies the
pre-registered combination rule and refuses on incomplete input.

### 4.7 Plotting — `plotting/`

**Was:** `PlottingScripts/`, 341 tracked files.

**Is:** `plotting/`, 49 tracked files, with two distinct paths.

**The paper-figure path is deterministic by construction.**
`plotting/paper/make_paper_figures.py` builds three SVGs from committed anchors
with no hand steps. `--figure ossvsmult` **fails closed rather than drawing a
placeholder**, because a figure with invented data travels further than its
caption. `plotting/paper/svgkit.py` has **no dependencies at all**,
deliberately: every coordinate goes through one fixed-precision formatter, so
the bytes are a pure function of the input numbers. Figure 3 *recomputes* the
published percentile table rather than displaying it, and agrees to < 0.01 pp
on all eleven classes.

**The ROOT path is contracted differently, and deliberately so.** A ROOT canvas
embeds a creation timestamp and a version string, and a PDF stream responds to
the font and the graphics backend. Byte-identity across two runs is therefore
not a property this project can promise. Those figures are contracted on
**pinned inputs + pinned ROOT + the recorded command**, with a JSON receipt
(`multiplicity_boundary_receipt_v1.json`) that carries its own `payload_sha256`
and *is* digest-contracted (`docs/GOLDEN_OUTPUTS.md` §0.3). **The numbers are
the contract; the rendering is not.**

### 4.8 Validation — `Validation/`

**Was:** validation macros scattered across the old tree.

**Is:** `Validation/` with 23 files, split into those on an automated path and
those written but not yet run.

**Why the unrun ones are kept and labelled.** `STATE.md` gives them a category
of their own: *written, unrun, available*. `docs/COMPONENTS.md` §6 calls them
the most valuable files in the directory and the easiest to mistake for dead
ones. M7 had the same shape: it sat unrun until a reviewer asked, and then took
one session to become a table with an uncertainty.

**The closure gate is the load-bearing one.** `ValidatePairBlockClosure.C`
performs **2100 content and 1500 invariant comparisons** per tune.

---

## 5. What was deleted or retired

### 5.1 Code — the criterion, and the count

**The criterion, quoted from `docs/REMOVALS.md`:** a file was deleted when *"no
defensible answer to 'why does this exist?' survived being written down"*.
Nothing was deleted to save space.

**The pass and its result**
(`docs/history/TRIAGE_DOCUMENT_PRUNE_SESSION_20260817.md` §1):

| | |
|---|---|
| tracked executables walked | **219** |
| documented in `docs/COMPONENTS.md` | **213** |
| **removed from HEAD** | **6** |
| renamed | **0** |
| marked UNSURE | **6** — all location or disposition, none an existence question |

**The six removed** all lived in `attic/`, all authored 2026-02, and none was
modified after that.

- `PlottingWizard.C`, 209 lines — a pre-THnSparse plot driver with no entry
  point and no recorded run.
- `combinedCanvasPlots.C`, 1562 lines — its job now runs inside
  `improvedPlotting_THnSparse.C` and `plotting/paper/svgkit.py`.
- `ListHistos.C`, 39 lines — `rootls -l` ships with ROOT and does the same.
- `reproduceCanvasPadError.C`, 128 lines — reproduces a bug that no document
  records as open.
- `count_events.sh` and `count_events_bb_cc.C`, 34 + 110 lines — superseded by
  `tools/campaign_status.py`, which reconstructs the same accounting from the
  receipts the worker wrote.

**Zero renames is the finding, not an omission.** Of 219 executables, **67**
are named inside a `GOLDEN_OUTPUTS.md` recipe, a run record, an anchor
`MANIFEST.md`, a signed `config/*.json`, `REPRODUCIBILITY.md`, `Paper/**` or
the `Makefile` — renaming them falsifies the record. Not one of the **134**
eligible files carries a banned qualifier. The single convention violation,
`plotting/improvedPlotting_THnSparse.C`, is the one name that cannot change
without invalidating a receipt for a figure rendered the day before. It is
priced and deferred rather than performed.

**Four near-misses were kept**, and `docs/REMOVALS.md` §2 records them because
a near-miss is the part of a deletion record that teaches something. In each
case the written entry surfaced a live consumer.

### 5.2 What was archived rather than deleted

**`attic/` holds 25 tracked files.** Each has a recorded reason
(`docs/COMPONENTS.md` §10):

- **`attic/split_chain/`** (18 files) — the bb/cc/qq producers, their six
  `.cmnd` cards and reductions. `README.md` §6 states the chain *"remains
  available for independent reference samples"*.
- **`attic/count_events/CountEvents/generated_heavy_flavor_summary.C`** —
**measurement provenance for a table published right now**,
  `Paper/Tables/generated_heavy_flavor_summary.tex`. It cannot be re-pointed: it
  reads histograms and a tree that do not exist in raw schema v7.
- **`attic/plotting/improvedPlotting.C`** — reads `complete_root`, the same
  merge product the live path consumes, making it an independent cross-check.
- **`attic/plotting/B_Balancing_GeneralPlotting.C`** — flagged as a byte-level
  duplicate and **measured not to be one**: 2217 lines against 3051, different
  headers, `c41b52dc…` against `d6e6b74d…`. It carries the original author's
  30-line explanatory header, which the other copy replaced with a TODO.
- **Three `configuration_*.json` files** — the only readable record of the
  v2-era single-axis plot configurations, whose figures are permanently not
  regenerable.

**Git history is the archive for the rest.** Every deleted file is reachable
with `git log --follow -- <path>` and restorable with `git show
<commit>:<path>`.

**`decay_parent_map_v1.json` is frozen as history and must not be deleted.** It
is the artifact E1 is about, and deleting it would delete the evidence for the
project's most instructive published error (`docs/GOLDEN_OUTPUTS.md` §2.2).

**One deletion landed in the wrong commit, and the record says so.** The six
`git rm`s were swept into `fc59491` — a commit about the systematics
pre-registration — because a concurrent session in the same worktree committed
while the manifest was being written. Nothing was lost. History was
deliberately not rewritten, because rebasing shared history under a live worker
trades a cosmetic problem for a real one (`docs/REMOVALS.md` §1).

### 5.3 Figures

**Census taken 2026-08-17** from three sources: the manuscript's own
`\includegraphics` list, the `Paper/**/figures/` tree, and
`plotting/PAPER_FIGURE_PROVENANCE.md` (review finding A6). **Every figure gets
exactly one disposition.**

| disposition | count | meaning |
|---|---|---|
| **REGENERATE** | **8** | the manuscript needs it; rebuild from merged v3 |
| **BUILD** | **2 families** (32 files) | the kinematic panels, promoted by the addendum |
| **OWNER-DECIDE** ⚑ | **4** | genuinely ambiguous; the question is stated |
| **SUPERSEDED** | **6** | role served by a named new-era figure |
| **RETIRE** ⚑ | **106** | observable or claim is gone |
| total catalogued | **148** | 146 under `figures/` + 2 at the paper root |

**The 106 retirements break down as 10 + 95 + 1.** Ten `.eps` files belong to a
**chiral-magnetic-effect / AVFD analysis** and are template leftovers, never
referenced by any `\includegraphics`. Ninety-five are superseded exploratory
plots. Thirty of those are **two-tune** ratios in 20 %-wide multiplicity
slices. They fail on two counts. The analysis is now three-tune, and the class
axis is the committed 11-class common-absolute partition rather than 20 %
slices. The last one is `runningCouplingQCD.png`, already commented out at
`Introduction.tex:20`.

**The manuscript is not broken today.** It carries **10 active
`\includegraphics` and 1 commented out, and all 10 resolve to files that
exist**. The problem is that those files come from the dead dataset.

---

## 6. What is new

### 6.1 The sealed campaign — HF_RUN3_V1

**Sealed and authorized 2026-08-17**: `canonical`, `publication_eligible:
true`, on facts re-measured at seal time rather than inherited
(`docs/history/CAMPAIGN_SEAL_SESSION_20260817c.md` §1,
`docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md`).

| | |
|---|---|
| jobs promoted | **3000 / 3000** — 1000 per tune |
| events | **100 M per tune**, 300 M total |
| seal schema | `hf_canonical_freeze_seal_v2` |
| rows / per tune / blocks | 3000 / 1000 / 10 |
| manifest digest vs seal | **identical**, `fcd96eae…` |
| ten `block_*.jsonl` summed vs manifest rows | **3000 = 3000** |
| 12-row sha256 spot-check against disk | **12 / 12 MATCH** |
| merged products | **33 / 33** |
| closure verdicts | **PASS on all three tunes** |

**The convergence cost is recorded rather than smoothed.** 3127 attempts
produced 3000 promoted jobs across three retry rounds. **127 hangs**: MONASH
**0 of 1000 (0.00 %)**, JUNCTIONS **63 of 1063 (5.93 %)**, CLOSEPACKING **64 of
1064 (6.02 %)**. The two CR tunes are indistinguishable — 0.09 ± 1.06 pp — so
**the hang is CR-specific and the JUNCTIONS-vs-CLOSEPACKING distinction is not
supported**. The old 2.7 % aggregate is dead, and 4.06 % does not replace it.
An aggregate that averages a 0 % tune with two 6 % tunes describes none of
them.

**The discard-bias bound is reported, not corrected away.** Worst case on
affected jobs: MONASH 0.00 %, JUNCTIONS 6.00 %, CLOSEPACKING 5.90 %. An earlier
argument put the true bias "far smaller", on the reasoning that *"a wedge is a
lost draw, not a skewed one"*. **Owner ruling retracted it.** The argument
shows that a wedged job contributes no biased events. It says nothing about
whether the set of jobs that wedge correlates with event content, and that is
the open question.

### 6.2 The reproducibility contract — `docs/GOLDEN_OUTPUTS.md`

**The claim it makes on the project's behalf**, quoted:

> Every published number in this repository is either (a) regenerable from
> committed inputs with committed tools, or (b) explicitly recorded as not
> regenerable, with the reason. There is no third category.

**Category (b) is real, and §5 lists all six entries.**

| # | item | why it cannot be regenerated |
|---|---|---|
| **N1** | the `extraction_dual/` anchors | the source directory held three CSVs and nothing else — no log, manifest or invocation record |
| **N2** | the merge timing band | the merge log carries no timestamps; every timing is reconstructed from filesystem mtimes |
| **N3** | the PYTHIA install | a personal directory with no container; the tarball checksum is recorded, and nothing rebuilds it |
| **N4** | the junction hang | 1 M events on 8.315 with a byte-identical card and the exact seed of a hung job **did not hang** |
| **N5** | the discarded jobs | the hang hits dense-junction topologies, which are the configurations under study |
| **N6** | G1's source fixture | one JUNCTIONS raw file on Nikhef; the digest is recorded and the bytes are not committed |

**N2 outranks the rest, because doing nothing still destroys it.** The evidence
is filesystem metadata on a scratch area, so no consolidation may touch merge
scratch until the band is scored.

A seventh entry **closed** on 2026-08-12. It stays on the table struck through
rather than deleted. A gap that closed is part of the provenance story, and a
reader of an older handoff needs to find its resolution.

**The gate is exactly two conditions**, set by the owner and quoted rather than
extended:

| # | condition |
|---|---|
| **G-1** | `make check` green at its pre-restructure count, **with no test skipped or deleted** to achieve it |
| **G-2** | **every file sha256 in §2 unchanged**, and every derived artifact regenerates to it — under whatever path the new layout gives the file |

**Both halves are necessary.** `git mv` preserves every byte and can still
break every recipe that names a directory; the suite is what notices.

**What it covers: thirty-seven digest-pinned entries**, G1–G25 and G36–G45 plus
the two bracket variants G14d and G15d, across the nineteen subsections of §2.

- The species axis, the spine everything else pins to.
- The three decay-parent maps, including the defective v1 kept as evidence.
- The probe anchors, which are the maps' raw material.
- The extraction anchors and the convention tables.
- The second-branch number, and the Σ_b raw-count leg.
- The M7 charm and beauty block logs, ten each.
- The MONASH central table, and the three-tune central table.
- Closure at v3 scale, the bin-level audit trail, and the paper figures.
- Added 2026-08-19: the five closed variation campaigns, the tune separation,
  the combination, and the ratio trend.

**The machine-checkable form in §7 is a 51-line digest manifest**, of which 30
lines are the three ten-block log families (`m7_blocks`, `m7b_blocks`,
`sigmab_raw`). It is keyed on digests rather than on paths, because a
restructure changes paths by definition.

**The document names its own traps.** It distinguishes three kinds of digest,
and confusing them is a live trap. A reviewer who runs `sha256sum
decay_parent_map_v1_1.json` gets `ed148156…` rather than the quoted
`dd502a10…`, and has **not** found a discrepancy. One digest covers the file,
the other covers the JSON body. A vocabulary of five verification tags is used
strictly, and **no entry is tagged VERIFIED by the session that wrote the
contract**, which ran no pipelines by instruction.

**G-1 has a trap of its own, and it is stated.** Without ROOT the suite reports
a smaller denominator and passes, so **the machine that cannot run the pipeline
is the one that looks healthy**. A green run must print `ROOT: /path/to/root`.

### 6.3 The pre-registered systematics programme

**`docs/SYSTEMATICS_PREREGISTRATION.md` was written on 2026-08-17, wall clock
10:38 CEST at the first line.** No variation job had been rendered or queued at
that point. The document sets its own void condition: *"if the git history
shows otherwise, this document is void and every number derived from it must be
withdrawn"*.

**What it registers, for each of six sources:** the variation, its magnitude,
its sample size, the estimator, the decision thresholds, and **the expectation
stated in advance so that it can be wrong**.

| # | source | variation |
|---|---|---|
| **S1a** | renormalisation scale | `SigmaProcess:renormMultFac` ×2 / ×0.5 |
| **S1b** | factorisation scale | `SigmaProcess:factorMultFac` ×2 / ×0.5 |
| **S2** | parton distribution | `PDF:pSet` 13 → 8 (NNPDF2.3 LO → CTEQ6L1) |
| **S3** | `PhaseSpace:pTHatMin` | 2.0 → 1.0 and → 4.0 |
| **S4** | event-activity counter | \|η\| < 1 → \|η\| < 4, percentile-preserving. **Deliberately not launched** |
| **S5** | decay-daughter class migration | boundaries × 1/(1 ± 0.00767) |
| **S6** | pair-level unresolved origin | duplicate hard-carrier tie-break |

**Two absences are claims.** The tune bundle is **the measurement, not a
systematic** — folding the MONASH/JUNCTIONS/CLOSEPACKING spread into an
uncertainty band would destroy the quantity being reported. Detector response
is **out of scope**: this is a generator-level study with no unfolding, no
efficiency and no resolution model.

**The dated amendment.** On **2026-08-18** the owner ruled on two questions the
registered text left open. The amendment records its own precondition, and
verifies it rather than claiming it. **No Δ from any variation source existed
anywhere in the repository at commit time.** The four variation cells all read
`PENDING`. The only file under `docs/systematics_results_*` held S5's
structural zero, which is a different source, measured the day before and
unaffected by the ruling.

- **A1 — how an unresolved per-class Δ enters the combination.** The registered
  text was silent. **Ruled: each source contributes `max(|Δ(c)|, SEM(Δ(c)))`
  per class, applied continuously, with no threshold cliff.** The `|Δ| < 2·SEM`
  flag marks a class for the reader. It must never act as a branch in the
  arithmetic. The rationale on record: no one may claim a systematic below the
  resolution of the measurement, and no one may zero a potentially real shift.
- **A2 — the A2/S6 partition conflict.** A session brief had instructed that
  the A2 term be summed into the per-class total. **The owner overruled that
  instruction and recorded it as their own error.** S6 stays on its own
  five-class `M1…M5` partition. `M1…M5` and `c1…c11` partition the same axis
  differently, so no class-by-class correspondence exists to add along.

**Both rulings are encoded as required policy flags** on
`extraction/systematics_delta.py::combine_quadrature`, which refuses to run
without them, so neither can be silently re-decided by a caller.

### 6.4 The variation campaigns

**Seven campaigns, complete at 2100/2100 raw files**, preflighted at full
rigour — exact-filename presence with no globs, sidecar↔receipt cross-check
between two independent writers, and byte-level re-hash, all 2100 clean
(`docs/SYSTEMATICS_HARVEST_RUN_RECORD.md` §2).

| campaign | rows | tunes | events | manifest sha256 (first 16) |
|---|---|---|---|---|
| `HF_SYS_MUR_UP` | 300 | 3 | 30 M | `01b5dbccfeec942b` |
| `HF_SYS_MUR_DOWN` | 300 | 3 | 30 M | `2d894a482a0e5509` |
| `HF_SYS_MUF_UP` | 300 | 3 | 30 M | `6e81b9dbb3fcff58` |
| `HF_SYS_MUF_DOWN` | 300 | 3 | 30 M | `e3ab8af8d0d7362d` |
| `HF_SYS_PDF_CTEQ6L1` | 300 | 3 | 30 M | `29472cbb6c600cdf` |
| `HF_SYS_PTHAT_1` | 300 | 3 | 30 M | `1188f65f22c8ace2` |
| `HF_SYS_PTHAT_4` | 300 | 3 | 30 M | `b58ffa8fdd8cc191` |

**The block rule was verified against the estimator's definition, not
assumed:** every one of the 300 rows satisfies `block == canonical_slot % 10`,
and each tune carries slots 0–99 with 100 distinct values.

**One check that could have invalidated every Δ came back clean.** The analysis
macro's sha differs from the sealed central campaign's. The difference is **six
`#include` path rewrites from the restructure move**, and the one changed
header symbol is not referenced by the macro (§4.1 of the run record).

### 6.5 The test suite

**At the anchor there was no test suite.** `git ls-tree -r 11884cf` returns no
`tests/` directory and no test file; the two matches for "test" are
`SimulationScripts/test_bb` and `test_cc`, which are ROOT data files.

**Today: 62 Python test files and 5 C++ files.** Measured by running `bash
tools/run_tests.sh` on `859bde6`: **`ROOT: /opt/homebrew/bin/root`, 62/62
passed, zero FAIL lines.**

**The recorded progression through the window:** 30/30 at `9426f38` → **37/37**
after the post-review fixes (seven added, none removed) → 46/46 at the triage
pass → 50/50 → 51/51 at the campaign seal → 61/61 → **62/62**.

**What the suite pins is the error record.** Most docstrings open with `THE
DEFECT THIS CLOSES` or `THE DEFECT (review finding A_n)`. That makes the suite
a second, executable copy of `ERROR_RECORD.md`, and it is why deleting a test
deletes evidence (`docs/COMPONENTS.md` §9).

| test | the defect class it pins |
|---|---|
| `test_closure_trigger_deduplication.py` | **E5** — measures the 24×/26× replication from the registry rather than assuming it, exercises the fail-closed path, and pins the sector-divisibility fingerprint of the published table so it cannot be quietly re-labelled as never having happened |
| `test_compare_subset_parent.py` | **E4** — eight checks: the historical binomial 30-of-88, the MAD null's 0-of-88, both negative controls, both injected positives, the σ̂ calibration and the counting floor |
| `test_a2_regression_gate.py`, `test_a2_campaign_restoration.py` | **E7** — the guard that selected on the outcome variable, and the campaign-level assertion that replaced it |
| `test_closure_schema_requirement.py` | **A4** — the closure gate's required schema argument |
| `test_heavy_sign_production_convention.py` | **A11** — the beauty sign convention, validated against production `q_c`/`q_b` before I2 runs |
| `test_decompose_exit_status.py` | **A12** — I2 reported in the exit status |
| `test_environment_verdict.py` | **A7** — the environment pin |
| `test_recipe_scripts_executable.py` | **A8** — mode bits and shebangs |
| `test_systematic_class_migration.py` | **S5** — asserts the per-boundary margin exceeds the measured bias, so a re-binning that breaks the null fails the suite rather than leaving a stale "exactly zero" |
| `test_harvest_class_axis.py` | the class-axis inversion — `c1` is lowest multiplicity, against `config/multiplicity_class_boundaries_v1.json` |
| `test_per_class_control.py` | the per-class control agreement, on twelve real `UNCERTAINTY_MATRIX` rows held as fixtures |
| `test_combine_per_class.py` | the combination rule, 25 hand-computed checks |
| `test_ratio_trend.py` | the trend arithmetic, 22 hand-computed checks |

### 6.6 The figure family, and the writing standard

**Three paper figures are generated from committed tables by script with no
hand steps:** `fig1_species_decomposition.svg`, `fig2_m7_inclusive_shift.svg`,
`fig3_multiplicity_classes.svg`.

**A repository writing standard was added** (`b598ce7`):
`docs/writing_standard/STANDARD.md` applies ASD-STE100 Simplified Technical
English Issue 9 and Orwell's rules. It adds two substance requirements: every
paragraph must add facts, and every fact must come from a file, an artifact or
a measurement. `tools/prose_check.py` runs the mechanical subset.

---

## 7. Results

### 7.1 The three-tune central table — FINAL

**Promoted to FINAL 2026-08-16** (`docs/THREE_TUNE_CENTRAL_TABLE.md`). Both
outstanding closures passed. JUNCTIONS returned at 11:58:20 CEST after 13 h 50
m and CLOSEPACKING at 11:37:27 after 13 h 29 m. Each reported `errors=0`,
**2100 content and 1500 invariant** comparisons, and schema
`paul_pair_objects_primary_ground_v3`. **No number moved on promotion**,
because the numbers were measured before the verdicts.

**Diquark-structure partition, per cent. SEM is the ten-block standard error,
dof = 9.** Fractions are formed inside each block and then averaged, never as a
ratio of summed numerators to summed denominators.

| group | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| **kCentralGround** | **52.4959** ± 0.0074 | **58.2318** ± 0.0078 | **54.1697** ± 0.0112 |
| **kExcludedVector** | **46.4946** ± 0.0079 | **39.9409** ± 0.0083 | **39.9976** ± 0.0105 |
| **kExcludedExcited** | **1.0095** ± 0.0012 | **1.7821** ± 0.0015 | **5.7745** ± 0.0050 |
| **kMultiplyHeavy** | **0.0000** ± 0.0000 | **0.0452** ± 0.0004 | **0.0583** ± 0.0007 |
| **sum** | 100.0000 | 100.0000 | 100.0000 |

**Integrity, and one unmet expectation stated at the top rather than buried.**
I3 — blocks sum to the central bin by bin — **PASS exact** for all three tunes.
I2 — block against central under the MAD null — gives **MONASH 0 flags of 10,
JUNCTIONS 3, CLOSEPACKING 1**. `docs/PER_TUNE_PROCESSING_PREREGISTRATION.md`
step 2 registers **I2 = zero flagged bins**. The four flags are diagnosed,
bounded and jackknifed immaterial — **no row moves by more than 1.19 SEM** —
and **the owner's ruling on them is still outstanding**. The promotion rests on
the closure verdicts, which is what the 2026-08-16 brief gated it on.

**MONASH's column was reused, not re-run.** Its closure passed 2026-08-12 and
its table of record is `docs/MONASH_CENTRAL_TABLE.md` §0. The reproduction in
the three-tune table is a control on the instrument.

### 7.2 The systematics status

Six sources, per `docs/SYSTEMATICS.md` §0. **Two of six have final numbers, two
arms of two more are delivered, one source is still merging, and one was
deliberately never launched.**

| # | source | status |
|---|---|---|
| **S1a** | renormalisation scale | ✅ **both arms, both deliverables**, 2026-08-19 |
| **S1b** | factorisation scale | ⚠ **DOWN arm done, both deliverables; UP arm still merging** |
| **S2** | parton distribution | **PENDING — merge still running** |
| **S3** | `PhaseSpace:pTHatMin` | ✅ **both arms, both deliverables**, 2026-08-19 |
| **S4** | event-activity counter | **not launched, deliberately** |
| **S5** | decay-daughter class migration | ✅ **EXACTLY ZERO** — structurally insensitive, every class |
| **S6** | pair-level unresolved origin | ✅ done 2026-08-13 — **must be quoted per class** |

**S5 is exactly zero, and the reason is structural rather than statistical.**
`N_ch` is an integer count and the committed class boundaries sit at
half-integers, so a boundary move changes a per-class observable **only if it
crosses an integer**. The bias is **0.767 %**, re-measured on the production
generator: PYTHIA 8.317, 200,000 events per arm, both arms paired on one seed
so the shared event content cancels. `dN_ch/dη` = 7.040 under the experimental
decay convention against 6.986 under the exact production policy. `c11`'s
boundary needs a **1.538 %** shift to cross an integer, so **the null holds by
a factor of 2.01**. The argument was also checked on real data. Re-projecting
the three committed minimum-bias samples under both shifted boundary sets moves
**zero** integers between classes, in all three tunes.

**Two things travel with S5.** Any boundary above `N_ch` 65.2 *would* be
migrated, so a future re-binning does not inherit this null. The bias also
comes from minimum bias rather than from the production sample. The production
sample carries more heavy-hadron content per event, so its bias is plausibly
larger. **Nobody has measured it**, and the record calls this a real open edge
rather than a conservative choice. **The zero does not cover the percentile
labels**, which do shift. That is a labelling caveat for the paper text.

**S6 must be quoted per class, and it is not an envelope.** The
largest-`heavyIndex` arm puts every MONASH class under 0.004 %, which is
**negligible — ~25× below the pre-registered 0.1 % threshold**. JUNCTIONS
reaches **0.1509 ± 0.0196 %** at M4 and CLOSEPACKING **0.2293 ± 0.0319 %** at
M5. The integrated values (JUNCTIONS 0.0583, CLOSEPACKING 0.0795) **understate
the worst class by 2.6× and 2.9×** and must not be substituted. The two
extremal tie-break orderings differ by **2.0–5.5× in all ten CR classes at
2.7–21.6 σ**, and that rule dependence is what makes per-class quoting
mandatory.

**Deliverable 1 — the decomposition deltas, five closed campaigns.** Largest
shift per campaign and tune, per cent, against the sealed nominal, using the
registered per-block relative estimator:

| campaign | source | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|---|
| `HF_SYS_MUR_UP` | S1a up | 0.2854 ± 0.0565 | 0.1654 ± 0.4682 | 0.5870 ± 0.1774 |
| `HF_SYS_MUR_DOWN` | S1a down | −0.2181 ± 0.0845 | −0.5148 ± 0.1276 | −0.5875 ± 0.2155 |
| `HF_SYS_MUF_DOWN` | S1b down | 1.4540 ± 0.0719 | −7.0113 ± 0.4200 | −13.0501 ± 0.2818 |
| `HF_SYS_PTHAT_1` | S3 → 1.0 | −1.0648 ± 0.0581 | −5.0172 ± 0.3729 | −8.5373 ± 0.2810 |
| `HF_SYS_PTHAT_4` | S3 → 4.0 | 4.1877 ± 0.0447 | 5.4002 ± 0.3180 | 6.8655 ± 0.1624 |

**55 deltas quoted, 12 unresolved at 2 σ, 5 not quotable.** The five are every
campaign's MONASH `kMultiplyHeavy`, where the sealed nominal holds **8 counts
in total** and individual blocks hold zero, so a relative shift has no meaning.

**Deliverable 2 — the per-class and integrated balancing yields, five closed
campaigns. 182 of 720 cells clear 2 SEM.** The per-class arm is
statistics-limited. Each variation carries a tenth of the nominal's exposure,
and each class a fraction of that again.

**The control licenses the arithmetic.** The measurement target re-renders the
sealed central and reproduces the nominal on **all 144 rows**. No compared
field disagrees, and no tolerance is applied.

**The two deliverables agree on ordering from two different instruments and two
different estimators.** The two scale arms are the quietest and the two
`pTHatMin` arms the loudest, on both the category axis and the class axis.
Resolved cells per campaign on the per-class arm, of 132: `MUR_DOWN` 7,
`MUR_UP` 13, `PTHAT_1` 34, `MUF_DOWN` 42, `PTHAT_4` 59.

**No total, and no quadrature.** The combination needs all seven campaigns, and
the pre-registration's closing rule forbids a partial sum.

### 7.3 The tune separation — provisional

**This is the half of the headline comparison that needs no variation
campaign**, because the separation between two tunes is a property of the
sealed nominal alone (`docs/systematics_results_20260819/TUNE_SEPARATION.md`,
`tune_separation.json` sha256 `37aae5bd…`). **It carries no systematic, and no
row in it is a verdict.**

**Read the class axis in the stated direction.** `c1` is the **lowest**
multiplicity, `N_ch` 0 to 2; `c11` is the **highest**, `N_ch` 32 and above. The
window label is a *top* percentile and runs the other way. A reader who takes
the label as an ordinary percentile inverts every trend, and
`tests/test_harvest_class_axis.py` holds the two statements together.

| observable | c1, stat. σ | c11, stat. σ | c1, % of MONASH to erase | c11, % of MONASH to erase |
|---|---|---|---|---|
| B⁺–B⁻ balancing yield | 2.2 | 39.7 | 4.5 | 31.9 |
| B⁺–Λ_b balancing yield | 2.2 | 49.4 | 9.7 | 128.4 |
| Λ_b/B⁻ ratio | 2.5 | 59.2 | 14.8 | 235.5 |

**The separation grows monotonically from low to high multiplicity in all three
observables.** MONASH's Λ_b/B⁻ ratio is flat across the axis, 0.1619 to 0.1865,
while JUNCTIONS rises from **0.2141 at `c1` to 0.5432 at `c11`**. At minimum
bias the MONASH−JUNCTIONS ratio difference is **−0.251378 ± 0.00395, 63.6 σ**,
which is 150.5 % of the MONASH value. **That is the shape a junction-driven
baryon enhancement would produce, and this is a statement about shape and
nothing more until the systematic is in the denominator.**

### 7.4 The trend — the paper's central claim, provisional

**The claim is a trend, and per-class gaps do not establish one**
(`docs/systematics_results_20260819/RATIO_TREND.md`, `ratio_trend.json` sha256
`b1b59548…`). **This quantifies the rise on the sealed nominal alone. It quotes
no systematic and is therefore not yet a verdict.**

**The model-free estimator leads, because it assumes nothing:** `R(c11) −
R(c1)` subtracts two rows, with SEMs in quadrature.

| tune | contrast | stat. σ | difference vs MONASH | stat. σ |
|---|---|---|---|---|
| MONASH | **−0.02453 ± 0.00739** | 3.3 | — | — |
| JUNCTIONS | **+0.32909 ± 0.01053** | 31.2 | **+0.35362 ± 0.01287** | 27.5 |
| CLOSEPACKING | **+0.28719 ± 0.01364** | 21.1 | **+0.31172 ± 0.01551** | 20.1 |

**MONASH declines gently rather than sitting flat**, at 3.3 σ from zero. The
word "flat" is not exact and the record says so.

**Both reconnection tunes rise by more than an order of magnitude more**, and
the enhancement grows monotonically: JUN/MON from **1.148 at `c1` to 3.355 at
`c11`**, CLP/MON from **1.160 to 3.109**.

**A straight line does not describe the reconnection tunes, and the slope is
therefore a summary rather than a model.** The weighted straight line in class
index gives χ²/ndf of **1.41 for MONASH, 8.18 for JUNCTIONS and 6.49 for
CLOSEPACKING**. Two further conventions travel with it. The x-axis is the class
*index*, which is not equally spaced in `N_ch`: `c1` spans three units and
`c11` is open above 32. A slope "per class" is therefore not a physical
`d(ratio)/dN_ch`. **A referee should read the endpoint contrast as the
measurement and the slope as shorthand.**

**The threshold the verdict will turn on is stated in advance.** To erase the
JUNCTIONS-minus-MONASH trend, a combined systematic must reach **0.354 in the
endpoint contrast** or **0.036 per class in the slope**. That is the whole of
the measured effect, correlated in the one direction that cancels it. For
CLOSEPACKING the two figures are **0.312** and **0.034**.

### 7.5 What is final and what is in flight

| result | status |
|---|---|
| the three-tune central table, diquark partition | **FINAL** 2026-08-16, one owner ruling outstanding on the four I2 flags |
| the corrected decomposition total, 53,662,416 | **FINAL** — measured by re-extraction 2026-08-13 |
| S5 = exactly zero | **FINAL** for the current class axis |
| S6 per-class | **FINAL**, on its own `M1…M5` partition |
| S1a, S1b-down, S3 — both deliverables | **MEASURED**, five of seven campaigns |
| S1b-up, S2 | **IN FLIGHT** — merging |
| the tune separation | **MEASURED on the nominal, PROVISIONAL** — no systematic |
| the trend | **MEASURED on the nominal, PROVISIONAL** — no systematic |
| the combined systematic | **DOES NOT EXIST.** The tool refuses: `COMBINATION_REFUSED missing=HF_SYS_MUF_UP,HF_SYS_PDF_CTEQ6L1` |
| the verdict | **NOT GIVEN.** It needs all seven campaigns |

---

## 8. What it cost

**Elapsed: 22 days**, 2026-07-28 to 2026-08-19, with commits on 18 of them.
**434 commits**, 432 of them on the line that carries the incremental history.

**Events generated in the window: 510 M.** The sealed campaign produced 300 M
(3000 jobs × 100,000 events, 100 M per tune) and the seven variation campaigns
210 M (2100 jobs, 30 M per campaign).

**Convergence overhead on the sealed campaign: 127 wasted attempts of 3127**,
concentrated entirely in the two CR tunes at ~6 % each.

**Merge and closure, measured rather than estimated.** These are the dominant
cost and the reason the systematics harvest is a multi-day pipeline:

| stage | measured |
|---|---|
| central-campaign closure, per tune | **13 h 29 m – 13 h 50 m** |
| variation-campaign closure, per tune | **2 h 04 m – 2 h 22 m**, mean **2 h 11 m** |
| variation-campaign closure, three tunes | **6 h 32 m** |
| manifest validation, per variation campaign | **1 h 30 m** |
| three tunes of merging, per variation campaign | **3 h 45 m – 6 h 00 m** |
| **per variation campaign, total** | **≈ 11 h** |
| **seven variation campaigns** | **≈ 77 h sequential**, ≈ 22–30 h at the planned two-node parallelism |

**Two cost estimates were wrong, and the record says so in both cases.** The
first projection of ≈ 2.5 h per campaign came in **low by about 4×** (run
record §9.5). The extrapolated closure cost of ~1 h 50 m per tune came in at 2
h 11 m, **low by about 19 %** (§14.2). That second one was a factor-of-seven
extrapolation, and it landed close.

**One 6.2× spread between two identical merge legs has no explanation**, and it
is why the projection is a band rather than a number. `stbc-i2` stood at load
2.3 when the measurement ran, so contention is the likeliest cause.

**Disk.** A variation campaign's products are 11.7 G, so seven need **≈ 82 G**.
`/data/alice` stood at **98 %, 660 G free** when the projection was made (run
record §9.5). It read **928 G free** later in the harvest (§14.3). The volume is
shared with other users.
`docs/NIKHEF_CLEANUP_PLAN.md` maps **1294.2 G of project data** beside 1305.6 G
belonging to other users. It identifies **18.8 G recoverable once the merges
close, and 496.7 G after acceptance**. `RootFiles/HF/` alone accounts for 326.6
G of the second figure.

**What was regenerated rather than reused.**

- **The MONASH decomposition was re-extracted, not reconstructed.** The E5
  correction began as an arithmetic inversion of the committed replicated CSV. A
  live re-extraction with the fixed extractor followed on 2026-08-13, over the
  central and ten blocks with ROOT 6.30/01 on pin. It landed at 53,662,416,
  inside the predicted bracket.
- **The 0.767 % decay-policy bias was re-measured on the production
  generator.** The value carrying S5 had been **1.327 %**, measured on PYTHIA
  8.315. That left a margin of only 1.16 against the 1.538 % that moves `c11`'s
  edge. On 8.317 the bias is **42 % smaller** and the margin is **2.01**. The
  consequence reaches beyond S5. `DESIGN_AND_RATIONALE.md` §3.5 and
  `NCH_CALIBRATION_20260730.md` both state that the policy "costs 1.3 %", and
  the paper must state the figure. **On the production generator it is
  0.77 %.**
- **The decay maps rebuild from committed probe anchors in seconds**, with
  neither ROOT nor PYTHIA, and both rebuilt byte-identically before and after
  the A11 parsing change.
- **MONASH's central column was reused rather than re-run**, deliberately: its
  closure had already passed and the reproduction serves as a control on the
  instrument.
- **The restructure re-generated nothing on the cluster.** That session
  contacted Nikhef not at all: no ssh, no remote read, no job touched.

---

## 9. What remains

**Dates below are the projections the artifacts record, with the time they were
made. No artifact in this repository records the two outstanding campaigns as
closed.**

### 9.1 The last two campaigns

**`HF_SYS_MUF_UP` (S1b up) and `HF_SYS_PDF_CTEQ6L1` (S2) are still merging.**
At **17:16 CEST on 2026-08-19** (run record §22.8), `MUF_UP` held **33/33
products** and was on **closure leg 1 of 3, projected to close near 22:45**.
`PDF_CTEQ6L1` held **22/33 products with closure not started, later still**. At
21:0x the same day, §23 records both merges as still reading the frozen
checkout.

**Both are load-bearing and neither can be dropped.** `MUF_UP` is S1b's up arm
and `CTEQ6L1` is the whole of S2. Neither is a source that could be called
negligible without measuring it.

**Why the two lag is an open question.** Each is about a day into a
CLOSEPACKING leg that the five closed campaigns finished in 7 to 40 minutes.
Both burn CPU in user space, the storage benchmarks clean, and a filled-bin
census puts them within 1.28× of the closed campaigns. **The cause is not
established.**

**One caution that has already cost time: 33 of 33 products is not closure.**
The marker count is the answer.

### 9.2 The combination and the verdict

**`extraction/combine_per_class.py` is written, tested with 25 hand-computed
checks, and refuses to run**, naming what it lacks: `COMBINATION_REFUSED
missing=HF_SYS_MUF_UP,HF_SYS_PDF_CTEQ6L1`. It applies owner amendment A1 and
A2, pre-registration §9.1 and §2.5, and S5's measured zero. **It adds no rule
of its own.** `GOLDEN_OUTPUTS.md` §2.15 records it as an absence on purpose. A
tool that exists and produces nothing is easy to mistake for a tool nobody
wrote.

**The verdict then joins three artifacts that already exist** —
`per_class_deltas.json` for the cells, `tune_separation.json` for the per-class
gaps, `ratio_trend.json` for the trend. **Nothing else needs building.**

### 9.3 Figures

**The dispositions below are the 2026-08-17 census.** One render has landed since: the
three-tune multiplicity canvas, on pinned ROOT 6.30/01 from the sealed
`canonical` dataset. Its PNG came back **byte-identical** to the 2026-08-16
committed version, across a different session and a different deploy tree
(`FIGURE_INVENTORY.md` §3.1b).

**8 REGENERATE and 2 BUILD families (32 files) are still owed**, and **4
OWNER-DECIDE questions need a paper-side answer**: whether the two multiplicity
panels become one combined canvas, and what happens to the two `_215` global
canvases. **106 retirements and 6 supersessions carry the ⚑ owner mark and have
not been executed against the manuscript**, because `Paper/**` is read-only in
this work.

One figure is blocked rather than merely owed: **the B6 boundary-artifact update
did not reach the figure-4 macro** (`FIGURE_INVENTORY.md` §6.2).

### 9.4 Documentation and open rulings

- **The I2 flags on JUNCTIONS and CLOSEPACKING — RULED 2026-08-20: a
  DEVIATION, not an amendment.** Three flags on JUNCTIONS and one on
  CLOSEPACKING, against step 2's registered zero. The registered expectation
  stands exactly as written and the flags are reported against it; the
  pre-registration is not edited, because a registration changed after the
  result stops being one. Measured basis: the three JUNCTIONS flags sit in
  `kMultiplyHeavy`, **12 of 116** testable bins against MONASH's **0 of 88**,
  a subpopulation whose block scatter is **1.60×** binomial, so rescaled the
  flags are **|z| ≈ 2.5–2.7**; the CLOSEPACKING flag is **1 in ~2 960**
  comparisons at p ≈ 0.17; the jackknife moves no quoted row by more than
  **1.19 SEM or 0.006 pp**. `THREE_TUNE_CENTRAL_TABLE.md` §7 now has no open
  item.
- **A9, the stale paper table.** `STATE.md` 7b records it as **answered and
  deliberately not submitted**. The table is *not* regenerable from existing
  artifacts. It needs a counting pass over all 3000 raw files, about 10 Condor
  jobs of ~15 min, and it sits behind A2 in a full queue.
- **Six UNSURE dispositions** sit in `docs/COMPONENTS.md` §11, and none is an
  existence question. Q4 is the substantive one. Plan D5 ruled that
  `plotting_documentation.md` fold into `plotting/README.md`, and **nothing
  records the fold**.
- **Two changes are specified and deliberately not applied**, because the live
  merges read the frozen checkout (run record §23.4).
  1. `extraction/pipeline/tune_chain.sh:63` invokes a script that the
     2026-08-17 consolidation moved. Every published number still regenerates
     from committed anchors, so nothing is unreproducible today. But **the route
     from merged ROOT files back to those numbers cannot run as written**. That
     is the route a reviewer takes when the anchors are the thing in question.
  2. The default dataset-selector row must refuse rather than fall back. A
     silent default is what let five variation renders read the central
     campaign.
- **A seed collision exists in the ledger and does not touch the paper.**
  `HF_RUN3_V1` and all seven `HF_SYS_*` share no seed with the archived
  campaign. Two early campaigns do collide — `100200001` and `100400001` —
  because `HF_100M`, `HF_PT2` and `HF_SMOKE2` all carry `campaign_ordinal` 1.
  **From ordinal 3 onward each campaign holds its own band.** The impact ruling
  is the owner's and has not been made.

### 9.5 External review and publication export

**A second external review has not run.** The first covered `f0e67dc`; the
window's work is 432 commits past it.

**`docs/GOLDEN_OUTPUTS.md` §8 names four things the contract does not cover**,
and one of them has since been filled. §8 called the three-tune cross-tune
table "the most important entry in this document and it is not here yet". It is
now §2.9c. The other three stand:

- `Paper/**` is out of scope by instruction, untouched and unexamined.
- Whether the paper figures are digest-pinned anywhere is **UNKNOWN**.
- The session that wrote the contract ran no recipe, by instruction.

**Publication export has a started exclusion list.**
`docs/PUBLICATION_EXPORT_EXCLUSIONS.md` was created 2026-08-18, seeded with the
ASD-STE100 PDF, whose licence does not permit redistribution. **The publication
disposition of `docs/history/**` is flagged as an owner decision and not acted
on** (`COMPONENTS.md` §11 Q6).

---

## 10. Working method

Coding agents did the execution, in bounded sessions against written briefs: one
session per task, a stated scope, and a record committed at the end. Every
physics judgement, every ruling and every sign-off in this report is mine, and
the agents were instructed to state an open question rather than resolve one.

The verification discipline the briefs impose is why §3 has four entries. E5, E1,
E4/E6 and E7 were each found by a check that compared a claim against the
artifact behind it, not by reading code and not by a reviewer's eye. Three of
them were found before any number reached the manuscript, and E7 was found in the
gap between running a campaign and consuming it.

---

## Appendix — how to check any number in this report

| section | primary source |
|---|---|
| the anchor and the window | `git log`, `git diff --shortstat 11884cf..<head>` |
| the defects | `docs/ERROR_RECORD.md`, entries E1–E8 |
| the external review | `docs/history/POST_REVIEW_TIER1_SESSION_20260813.md` |
| the layout | `docs/history/RESTRUCTURE_SESSION_20260812.md`, `RENAMES.md`, `docs/COMPONENTS.md` |
| deletions | `docs/REMOVALS.md`, `docs/history/TRIAGE_DOCUMENT_PRUNE_SESSION_20260817.md` |
| figures | `docs/FIGURE_INVENTORY.md` |
| the reproducibility contract | `docs/GOLDEN_OUTPUTS.md` |
| the systematics design | `docs/SYSTEMATICS_PREREGISTRATION.md` and its 2026-08-18 amendment |
| the systematics results | `docs/SYSTEMATICS.md`, `docs/systematics_results_20260819/` |
| the sealed campaign | `docs/campaigns/HF_RUN3_V1_RECORD.md`, `docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md` |
| the variation campaigns | `docs/SYSTEMATICS_HARVEST_RUN_RECORD.md` |
| the central table | `docs/THREE_TUNE_CENTRAL_TABLE.md` |
| the suite | `bash tools/run_tests.sh` — a green run must print `ROOT: <path>` |
