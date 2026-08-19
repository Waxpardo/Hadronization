# Repository file census — what is live, what is history, what the owner should rule on

**Written 2026-08-12 on branch `restructure-prep`, against `9426f38`.**
Companion to `docs/RESTRUCTURE_PLAN.md`; input to it, not a substitute.

**Nothing here is a deletion.** No file was moved, renamed or removed by this
session. `deletion-candidate` means **"the owner should decide"** and nothing
more. The project has done this before and recorded how
(`CLEANUP_REPORT.md`, 291 paths, two revertible commits, nothing classified
UNSURE touched); this document is the equivalent inventory for the next round.

---

## 0. CLASSIFICATION AND METHOD

| tag | meaning |
|---|---|
| **KEEP** | on a live path — an entry point, a pipeline stage, a test, an active contract or an active doc |
| **HISTORY** | not live, but **evidence**. Moves to `docs/history/`; **never deleted** |
| **DEL?** | no live consumer found and no evidence value identified. **Owner decides** |
| **UNKNOWN** | classification needs knowledge this session does not have. The question is stated |

### 0.1 What the evidence is, and what it is not

Three signals, all mechanical:

1. **Reference count** — how many *other* tracked files contain the basename.
2. **Last-commit date** — from `git log --name-only` over full history.
3. **Entry-point membership** — whether a named driver invokes it
   (`Makefile`, `runCondorJob.sh`, `merge_root_files.sh`, `run_status_analysis.sh`,
   `tools/run_tests.sh`, `plotting/run_paper_plots.sh`,
   `extraction/pipeline/tune_chain.sh`).

> **⚠ Reference count is a proxy and it lies in both directions.** Three tests
> have **zero** references and are **live**: `tools/run_tests.sh:38` globs
> `tests/test_*.py`, so membership is by pattern, not by name. Conversely a file
> can have twenty references that are all prose in superseded handoffs.
> **No file below is classified on reference count alone.**

**A second-order check was NOT run.** `CLEANUP_REPORT.md` §1 records the right
one: an explicit read-pattern sweep (`TFile`, `Open(`, `Get(`, `.L`, `source`,
`import`) over every candidate basename across every `.C/.h/.cpp/.py/.sh`.
**That sweep is a precondition of acting on any DEL? below**, and it is
deliberately left to the execution session rather than done here — its value is
that it runs immediately before the deletion, not five sessions earlier.

### 0.2 Totals

| | |
|---|---|
| tracked files at `9426f38` | **374** |
| classified KEEP | **~232** |
| classified HISTORY | **~118** |
| classified DEL? | **13** — **with the owner, being ruled on now** |
| classified UNKNOWN | **11** — four closed by the 2026-08-12 rulings |

Counts are approximate at the margin because `docs/handoffs/` (47 files) is
classified as one block.

---

## 1. `tools/` — 38 files

**Almost entirely live.** This directory survived the 2026-08-03 cleanup and has
been the active workspace since.

| file | class | reason |
|---|---|---|
| `campaign.py` | KEEP | single source of the tune list; 25 referencing files |
| `campaign_status.py` | KEEP | reconstructs a campaign from receipts alone |
| `render_production_submit.py`, `render_analysis_submit.py` | KEEP | Condor renderers; refuse a dirty tree |
| `resubmit_held.py` | KEEP | live retry path |
| `validate_analysis_outputs.py` | KEEP | **the gate**; 39 referencing files, the highest in `tools/` |
| `build_canonical_manifest.py` | KEEP | writes the ten `block_NN.jsonl` |
| `merged_pair_provenance.py` | KEEP | restored byte-identical in the last cleanup (`CLEANUP_REPORT.md` §5.2) |
| `checkout_advance_guard.py`, `install_checkout_guard_hook.sh` | KEEP | the checkout invariant; guard fix pending deployment |
| `queue_probe.py` | KEEP | `QUEUE_EMPTY` precondition |
| `doctor.sh`, `run_tests.sh`, `build_producer.sh` | KEEP | `make` delegates |
| `apply_card_config.py`, `validate_tune_cards.py` | KEEP | `make cards`, `make cards-current` |
| `generate_registry_artifacts.py`, `generate_species_ordinals_header.py`, `generate_pair_object_contract.py` | KEEP | golden-output generators, SELF-CHECKING |
| `GenerateSpeciesOrdinals.C` | KEEP | source of G1 |
| `f4_probe.cc` | KEEP | source of the probe anchors |
| `build_decay_parent_map.py`, `build_decay_parent_map_v2.py` | KEEP | golden recipes R5/R6 |
| `apply_decay_map.py`, `second_branch_weight.py` | KEEP | golden recipes R7/R8 |
| `extract_species_decomposition.py` | KEEP | **carries finding F1** — its `--decay-map` default is the defective v1. **RULED 2026-08-12 a reproduction hazard**; the default is removed and the argument made required in the restructure session |
| `decompose_with_block_sems.py` | KEEP | the harvest tool; I3 + I2 before numbers |
| `compare_subset_parent.py` | KEEP | E4's mechanism; pinned regression test |
| `aggregate_m7.py` | KEEP | golden recipe R9 |
| `pipeline/tune_chain.sh`, `pipeline/tune_extract.sh` | KEEP | **live on Nikhef right now** (three chains) |
| `statistical_robustness.py` | KEEP | 112 KB, 25 refs; reader of `block_NN.jsonl` |
| `evaluate_pthat_sensitivity.py` | KEEP | 80 KB; drives `PTHatSensitivity.C` |
| `pdg_2025_species_audit.py` | KEEP | driven by `tests/test_pdg_species_audit.py` |
| `dataset_selector.py`, `final_origin_closure.py` | KEEP | both under test |
| `archive_breach_partials.sh` | **HISTORY** | one-shot; its run is recorded in `docs/campaigns/HF_RUN3_V1_PARTIALS_ARCHIVE.md`. **Keep the script beside the manifest** — the partials rule is "moved, never deleted" and the script is how |
| `docs_check.sh` | UNKNOWN | advisory-only (`make docs-check`, never fails). Whether anyone uses it is not determinable from the tree. **Q:** keep as a hint, or retire? |

**Zero DEL? in `tools/`.**

---

## 2. `Validation/` — 22 files

The authority here is `docs/VALIDATION_INVENTORY.md` (2026-08-10), which is
already an evidence-based census. **This section defers to it and adds nothing.**

| group | files | class |
|---|---|---|
| on an automated path | `ValidateRawOutput.C`+`.sh`, `AuditOriginResolution.C`, `ListUnresolvedOrigins.C`, `ValidatePairDirectory.C`+`.sh`, `ValidatePairBlockClosure.C`+`.sh`, `ValidateCanonicalRawManifest.C`, `validate_canonical_manifest.sh`, `AuditSpeciesRegistry.C`, `PTHatSensitivity.C`, `TestAnalysisRawInputContract.C`, `TestPlotReferenceMultiplicityContracts.C` | **KEEP** |
| run at scale, first time 2026-08-10 | `MeasureUnresolvedSystematic.C` | **KEEP** — produced M7 charm **and** beauty |
| manual run recorded | `ValidateSpeciesAxisClosure.C` | **KEEP** — `docs/SPECIES_AXIS_VALIDATION.md` is its record |
| **no invoker, no recorded run** | `AuditTuneSettings.C`, `CalibrateMultiplicityAgainstMinBias.C`, `TestPrimaryChargedDefinition.C`, `TestHardCarrierUniqueness.C`, `TestInclusiveRawKinematics.C`, `TestPlotProjectionCuts.C` | **KEEP — explicitly NOT deletion-candidates** |

> **The six unrun macros are the most valuable files in this directory and the
> easiest to mistake for dead ones.** Three bear on **open blockers** (C8's
> per-tune percentile offsets, B3's inclusive spectra). **This is the same shape
> as M7**: a macro written to answer a review question, never run, so the
> question stayed open — and M7 took one session to become a table with an
> uncertainty. A dead-file sweep that deletes an unrun measurement deletes the
> answer to a referee.

> ### ✅ RULED 2026-08-12
>
> **They stay in the tree, and `STATE.md` lists them as *written — unrun —
> available*.** That is a category of its own: not live, not dead, not planned,
> and runnable if a question makes it worth doing. Draft entry:
> `docs/RESTRUCTURE_PLAN.md` §6.3.

---

## 3. `AnalysisScripts/` — the split between the live chain and the legacy one

| file | class | reason |
|---|---|---|
| `status_analysis_THnSparse_qq.C` | KEEP | **the one-pass reduction**; 33 refs; named in README §Repository roles |
| `MergeCanonicalAnalysis.C`, `MergeAnalysisObjects.C` | KEEP | merge stage |
| `GeneratedPairRegistry.h`, `GeneratedPairObjectContract.h`, `GeneratedSpeciesOrdinals.h`, `AssociateOriginCategoryContract.h` | KEEP | golden outputs G2–G4 |
| `species_ordinals_v2.json` | KEEP | golden output G1 — the spine |
| `decay_parent_map_v1_1.json`, `_v2.json` | KEEP | G6, G7 |
| **`decay_parent_map_v1.json`** | **HISTORY — never delete** | the E1 artifact. Deleting it deletes the evidence for the project's most instructive error. **Also a live hazard (F1)** |
| `anchors/**` (33 files) | **KEEP** | the review's provenance chain; frozen by `docs/GOLDEN_OUTPUTS.md`. **Treat as binary** — C7 depends on byte-identical probe lines |
| `hf_mult_pt_analysis_multi.C`, `run_hf_analysis.sh` | KEEP | the unified HF chain, which `README.txt` calls "the preferred production" |
| `status_analysis_qq.C` | KEEP | 8 refs; the non-THnSparse qq reduction |
| `qq_draw_2D_correlations.C` | UNKNOWN | 2 refs, 2026-05-13. **Q:** superseded by the THnSparse path, or still the 2D correlation view? |
| `bb_mult_pt_analysis_multi.C`, `cc_mult_pt_analysis_multi.C`, `status_analysis_bb.C`, `status_analysis_cc.C`, `run_bb_analysis.sh`, `run_cc_analysis.sh` | **UNKNOWN** | the **split bb/cc chain**. `README.txt` says it *"remains available for independent reference samples and comparisons to older productions"* — an explicit owner statement of intent, so **not** DEL?. But nothing in the current pipeline calls them and they last moved 2026-04/05. **Q:** does the resubmission still need the split chain, or is it history now? |
| `CountEvents/count_events.sh`, `count_events_bb_cc.C`, `generated_heavy_flavor_summary.C` | **DEL?** ×3 | 2–3 refs, last touched 2026-02-24 / 2026-07-15, no entry point. Event counting is now reconstructed by `tools/campaign_status.py` from receipts |
| `Analysis_README.md` | KEEP | directory doc |

---

## 4. `plotting/` — the largest concentration of legacy

The live paper-figure path is **`run_paper_plots.sh`**, and it names exactly
five macros: `Plot_InclusiveKinematicSpectra_Raw.C`,
`Plot_MultiplicityDistribution_PercentileBoundaries.C`,
`FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C`,
`FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C`,
`improvedPlotting_THnSparse.C`.

`PAPER_FIGURE_PROVENANCE.md` names two (`improvedPlotting_THnSparse.C` ×6,
`Plot_InclusiveKinematicSpectra_Raw.C`);
`validation/FINAL_PLOTTING_HANDOFF.md` adds `Plot_KinematicSpectra_THnSparse.C`.

| file | class | reason |
|---|---|---|
| `run_paper_plots.sh` + the five macros it names | KEEP | the figure path |
| `Plot_KinematicSpectra_THnSparse.C` | KEEP | named by the plotting handoff |
| `Plot_FlavourClosure.C` | KEEP | 4 refs, 2026-07-31 — current generation |
| `Validate_THnSparse_Production.C`, `validate_thnsparse_inputs.sh`, `validate_subsample_log.py`, `summarize_subsample_coverage.py` | KEEP | input validation for the figure path |
| `TunePlotStyle.h`, `HistogramErrorUtils.h`, `MultiplicityBoundaryUtils.h`, `PairInputSelectionUtils.h`, `PtMultiplicity/PlottingPathUtils.h` | KEEP | headers, 8–16 refs each |
| `configuration_multiplicity_reduced_JUNCTIONS_THnSparse*.json` | KEEP | 13–17 refs; live configs |
| `PtMultiplicity/*.C` (10 macros) + `README.md` | KEEP | 2026-07-24 generation, subsample plots |
| `README.md`, `FinalAnalysis/README.md`, `PAPER_FIGURE_PROVENANCE.md` | KEEP | docs |
| **`improvedPlotting.C`** | **DEL?** | superseded by `improvedPlotting_THnSparse.C` (30 refs vs 9). **Not in any entry point.** Every surviving reference is prose — `plotting/README.md`, `POST_SUBMISSION.md`, two audits, three handoffs. **If deleted, README must be corrected in the same commit** |
| **`PlottingWizard.C`**, **`combinedCanvasPlots.C`**, **`ListHistos.C`** | **DEL?** ×3 | 2026-02-24/28, 5–6 refs, no entry point, no doc claims them as current |
| **`B_Balancing_GeneralPlotting.C`** | **DEL?** | **a byte-level duplicate question**: a file of the same name exists at `Balancing_and_Sampling/B_Balancing_GeneralPlotting.C`. Two copies of one macro in two directories is a navigation hazard whichever is live. **Owner: keep one, and say which** |
| `configuration_pT.json`, `configuration_pseudorapidity.json`, `configuration_rapidity.json` | **DEL?** ×3 | 1 ref each, 2026-02-24; the live config is the multiplicity/THnSparse pair |
| `configuration_multiplicity.json` | UNKNOWN | 2 refs, 2026-05-14. **Q:** superseded by the `_reduced_JUNCTIONS_THnSparse` variants, or still the base? |
| `DpDmBpBm_ComparisonStudy/` (6 macros) | **HISTORY** | a self-contained 2026-02-24 study. Not deletion-candidates: a *study* is a result, and `RootFiles/OlderProductions/DpDmBpBm_Comparison_RootFiles/DESCRIPTIONS.txt` documents its inputs. **Move to `docs/history/studies/`, keep intact** |
| `validation/removed_tracked_plot_inventory.txt` | **HISTORY** | the inventory of the 264 plot artifacts deleted in `d799ae3` — the record of a deletion, which is exactly what must survive it |
| `validation/FINAL_PLOTTING_HANDOFF.md` | **HISTORY** | session handoff; belongs with the others |

---

## 5. `Balancing_and_Sampling/` — 19 files, ruled on already

**`docs/WORKSPACE.md` "Known non-portable leftovers" already decided this
directory**, and the ruling is quoted rather than re-derived:

> Three legacy scripts contain hardcoded paths under `/data/alice/pveen/...`, a
> *different user's* directory … They are not part of the production, analysis,
> or plotting pipeline and nothing in the current chain calls them. They are
> left untouched rather than half-fixed; **treat them as historical.**

| file | class | reason |
|---|---|---|
| `GenerateOutputs.sh`, `CalculateErrors/GenerateOutputs.sh` | **HISTORY** | owner-ruled above; hardcoded `/data/alice/pveen/` |
| `B_Balancing.C`, `B_Balancing_CompareSimulationSettings.C`, `B_Balancing_GeneralPlotting.C`, `B_Balancing_MakeOutputYields.C`, `CalculateErrors/*` | **HISTORY** | the balancing study, 2026-02-24/03-28 |
| `v*Yields*.txt` (8 files) | **HISTORY** | committed numeric outputs of that study |
| `ATTENTION.txt` | **HISTORY — read before touching** | records that double-counting is **not** implemented from 23 Dec onwards and results "will have to be divided by 2 manually". **An unresolved correctness caveat, not a note.** It ends *"remains to be checked"* and nothing in the tree says it was |
| `containsExcitedD.C` | **HISTORY** | small study macro |
| **`reproduceCanvasPadError.C`** | **DEL?** | a bug-reproduction scratch file for a ROOT canvas/pad error. The bug is not referenced anywhere as open |

> **`ATTENTION.txt` deserves an owner decision on its own, separate from the
> restructure.** Either the double-counting factor is irrelevant here (the note
> guesses the trigger normalisation cancels it) or it is a live factor-of-two on
> anything derived from this directory. **The file says nobody checked.**

---

## 6. `SimulationScripts/`, `config/`, `tests/`, `RootFiles/`

| file | class | reason |
|---|---|---|
| `heavyflavourcorrelations_status.cpp`, `HeavyFlavourUtils.h`, `Sha256.h`, `Makefile`, `GeneratedHeavyFlavourRegistry.h`, `GeneratedTuneSettingRegistry.h` | KEEP | the producer and its registries |
| `pythiasettings_Hard_Low_ccbb_{MONASH,JUNCTIONS,CLOSEPACKING}.cmnd` | KEEP | the three published tunes |
| `pythiasettings_Hard_Low_ccbb_JUNCTIONS_MATCHED.cmnd` | KEEP | the fourth card; deliberately **not** in `PUBLISHED_TUNES` (`CLEANUP_REPORT.md` §5.5 — adding it would have changed the embedded registry) |
| `bbbarcorrelations_status.cpp`, `ccbarcorrelations_status.cpp`, `qqbarcorrelations_status.cpp`, and the four `*_JUNCTIONS.cpp` / split `.cmnd` cards | **UNKNOWN** | the split producers, mirror of §3's split chain. Same owner question, same answer required |
| `Batching_MONASH.sh` | **HISTORY** | owner-ruled non-portable (`/data/alice/pveen/`) |
| `run_hf.sh`, `Simulation_README.md` | KEEP | |
| `config/*` (13 files) | **KEEP, all** | every one is a signed registry, contract or selector with 3–17 referencing files. `pair_file_object_contract_v1.json` is the derivation source for the 2100/1500 closure counts |
| `tests/*` (35 files: 30 `.py`, 5 `.cpp`) | **KEEP, all** | the suite is the acceptance gate |
| `RootFiles/*DESCRIPTIONS.txt` (3 files) | **HISTORY** | descriptions of ROOT files that live elsewhere; 20 KB total, no data |

---

## 7. Root-level and `docs/`

| file | class | reason |
|---|---|---|
| `README.md`, `REPRODUCIBILITY.md`, `RELEASE_BLOCKERS.md`, `POST_SUBMISSION.md`, `Condor_README.md`, `Makefile`, `setupEnv.sh`, `runCondorJob.sh`, `merge_root_files.sh`, `run_status_analysis.sh`, `submit_status_analysis.sh`, `make_subsamples.sh` | KEEP | entry points and top docs |
| **`README.txt`** | **DEL?** | self-describing compatibility shim: *"The canonical repository description is now written in README.md."* 1 KB, four references, all prose. **But it carries one fact nothing else states as plainly** — that the split bb/cc chain "remains available for independent reference samples". **Fold that sentence into README.md in the same commit, or keep the file** |
| `plotting_documentation.md` | UNKNOWN | 17 KB at root; overlaps `plotting/README.md` (21 KB). **Q:** which is authoritative? |
| **`CLEANUP_REPORT.md`** | **HISTORY** | the record of the 2026-08-03 cleanup. Belongs in `docs/history/`, and is the template for the next one |
| **`PUBLICATION_READY_CODING_AGENT_INSTRUCTIONS.md`** | **HISTORY** | 128 KB — the largest text file in the tree and **not physics**. Agent working instructions from 2026-07-30 |
| `docs/` active set — `ERROR_RECORD`, `GOLDEN_OUTPUTS`, `WORKSPACE`, `DESIGN_AND_RATIONALE`, `PROGRESS_PROBE_METHOD`, `NIKHEF_BRINGUP`, `VALIDATION_INVENTORY`, the `*_PREREGISTRATION` set, all result docs | KEEP | |
| **`docs/CONTENTION_RECURRENCE_PREREGISTRATION.md`** | **KEEP — mark superseded** | **RULED 2026-08-12: superseded-marked in the restructure pass, never scored.** It predicted a *scheduling* effect, gated no number, and the pivot ended operational forecasting. **Marked, not deleted** — a prediction registered in advance is a record even when it is never scored, and deleting it would be deleting the honest half |
| `docs/handoffs/` (47 files, ~600 KB) | **HISTORY, as one block** | session archaeology. **v40 and v21 are the generational entry points and stay reachable**; the rest are the chain |
| `docs/audit/` (`REPO_AUDIT_c1bb0d9.md`, `deletion_candidates.txt`, `repo_inventory.csv`) | **HISTORY** | the previous census. **Read it before acting on §1–7 above** |
| `docs/audits/` (2 files, 2026-07-30) | **HISTORY** | |
| `ValidationReports/` (5 files) | KEEP | `PTHAT_MULTIPLICITY_SCAN_8317.md` is cited by `REPRODUCIBILITY.md` §1; `PYTHIA_JUNCTION_HANG_20260731.md` is the record for B7 |
| `Literature/` | KEEP | untouched |
| `Paper/` | **out of scope** | not examined, by instruction |

> **`docs/audit/` and `docs/audits/` are two directories whose names differ by
> one character and whose contents are unrelated.** Whatever else the
> restructure does, it should not preserve that.

---

## 8. DOCUMENTATION DRIFT FOUND WHILE COUNTING

Recorded, **not fixed** — these are main-line documents and this is a docs-only
side branch.

### D1 — `README.md` §Tests is stale in four ways

| README says | measured at `9426f38` |
|---|---|
| "`tests/`: 24 files" | **35** |
| "the 21 `test_*.py`" | **30** |
| "The other three are `.cpp`" | **five** |
| "(`Makefile:117` globs them)" | the Makefile delegates to `tools/run_tests.sh`; **`run_tests.sh:38`** globs |
| "`make check` … 21 contract tests" | the suite is **30/30** |

### D2 — `README.md` contradicts `tools/run_tests.sh` on ROOT, in the dangerous direction

README: *"The Python tests are standard-library only and run anywhere,
including with no ROOT installed."*

`tools/run_tests.sh:6-7,32-34`: five tests **compile or run a ROOT macro and
raise "ROOT is required" rather than skipping**, and the script prints
*"This is expected off-cluster; it is **NOT** a green run."*

> **The failure this creates is the one the script was written to prevent:** a
> reader who trusts README runs `make check` on a laptop, sees a smaller
> denominator pass, and calls it green. The script already knows better; the
> README has not caught up. **D2 is worth fixing before the external review
> regardless of whether any restructure happens.**

### D3 — `AnalysisScripts/anchors/MANIFEST.md` §3 lists Task 2 outputs as "in flight"

`sigmab_runs/` outputs are listed as "anchor them when harvested". They **are**
anchored — `anchors/sigmab_raw/` holds all ten block logs. The manifest's own
gap list is one session behind its own directory.

---

## 9. THE ELEVEN UNKNOWNS, AS QUESTIONS

Only the owner can answer these. Each blocks a classification, not the plan.

| # | question |
|---|---|
| **Q1** | Is the **split bb/cc/qq chain** (6 files in `AnalysisScripts/`, 7 in `SimulationScripts/`) still needed for reference samples, or is it history? `README.txt` says available; nothing calls it |
| **Q2** | `qq_draw_2D_correlations.C` — superseded by the THnSparse path? |
| **Q3** | `plotting/configuration_multiplicity.json` — base config or superseded? |
| **Q4** | `plotting_documentation.md` (root) vs `plotting/README.md` — which is authoritative? |
| **Q5** | `tools/docs_check.sh` — keep the advisory hint or retire it? |
| **Q6** | `B_Balancing_GeneralPlotting.C` exists in **two** directories. Which one is live? |
| **Q7** | `ATTENTION.txt`'s double-counting factor of 2 — still unchecked. Does it affect anything published? |

Four further UNKNOWNs are file-level members of Q1 and are not restated.

---

## 10. WHAT THIS CENSUS DELIBERATELY DID NOT DO

1. **No read-pattern sweep** (§0.1) — it belongs immediately before deletion.
2. **No `Paper/**`** — out of scope.
3. **No size-based judgement.** The 128 KB agent-instructions file is HISTORY
   because of what it *is*, not because it is large; `RELEASE_BLOCKERS.md` is
   105 KB and KEEP.
4. **No deletions, no moves, no renames.** 13 DEL? entries, zero executed.
