# Full-production change-justification audit — 2026-07-30

Status: **implementation candidate; not authorized for production or
publication**.

This report audits the complete `full-production` change set against live
`origin/main`. It records why each changed path is in scope, the defects found
on stable main, the validation already completed, and the scientific or
operational gates that remain open. It is not a Gate-A--E artifact and does
not substitute for a project-owner decision.

## Audited source state

| Source | State |
|---|---|
| live `origin/main` | `11884cf1ad3613e8e6997bbff32d48a3e7d89570` |
| Paul post-subsampling commit | `10a6f098f80730374d9f827bfdf3ae97a928a030`; confirmed ancestor of `origin/main` |
| pre-audit `full-production` HEAD | `4a8d6ebb9f4fce408868140a4069a9d91b77f6ad` |
| implementation candidate | the commit containing this report |
| protected local `main` | `39c9cf22a723d623cc88ea683a5ea771ee98ea1c`, dirty and intentionally not synchronized |
| canonical Nikhef `main` | `11884cf1ad3613e8e6997bbff32d48a3e7d89570`, clean |
| protected Nikhef seed checkout | `758a53696805231205c6adb027ff4c8cbdf12386`, untouched |

The protected `Literature/References.bib` working copy and the 166-file
untracked `Paper/Heavy_flavour_hadronisation_model_paper/` tree are not part
of the implementation patch. The bibliography SHA-256 is
`9915952201459a5bd1f863b6be51c6053b0a55cea041e3e40bd0b2df515c7f48`
in both the protected checkout and the isolated worktree.

The final intended change union contains 244 paths:

- 166 source, configuration, test, audit, or documentation paths, including
  this report;
- 78 tracked generated THnSparse artifacts removed from version control.

Every removed generated artifact appears exactly once in
`PlottingScripts/validation/removed_tracked_plot_inventory.txt`. The complete
repository-wide file ledger is generated separately as
`REPOSITORY_FILE_CATALOG.md`.

## Stable-main findings

Paul Veen's merged THnSparse architecture is the correct compatibility
baseline. `full-production` preserves grouped trigger configurations,
per-canvas `TriggerToUse`, signed multiple beauty/charm triggers, the three
tunes, config-driven mini/global canvases, OS/SS balancing, the four drawing
paths, and the combined paper canvases.

Stable main nevertheless cannot reproduce the final paper without correction:

1. The full checked-in configuration uses a personal `/Users/...` path, the
   stale `complete_root_09_07_2026` tag, and
   `calculate_errors=false`.
2. The complete-root configuration enables subsampling, but the runner and
   documentation historically described it as a no-error target.
3. The four final drawing functions fall back to `1e-10` bin errors when
   errors are disabled and can return an uninitialized optional mini-pad.
4. The historical analysis applies one effective role threshold, lacks the
   final direct-primary and trigger-hard-origin contract, rescans the raw tree
   for each pair, and contains a B0/Sigma-b trigger/filename defect.
5. The historical producer does not provide exact successful-event,
   deterministic seed, integer identity, weight, stability, origin, registry,
   or immutable provenance contracts required for a publication campaign.
6. The legacy factor `0.5` for identical same-sign pairs conflicts with the
   explicitly tested ordered, trigger-conditional pair estimator. It remains
   available only in the exact tagged Paul regression.
7. The legacy `21_06_2026` central and ten-subsample production is internally
   useful regression evidence, but the exhaustive audit found 610 final
   configured observables without ten finite estimates. It cannot be promoted
   as the corrected raw-v5 result.

Thus no repair belongs on Paul's old branch. The tested changes belong on the
stable-main-derived `full-production` branch.

## Exhaustive changed-path justification

Primary statuses here use the original audit terminology:

- **ACTIVE**: directly or indirectly required by the central
  production-to-paper path;
- **SUPPORTING**: validation, documentation, templates, or reproducibility
  support;
- **GENERATED**: reproducible build/plot output removed from source control;
- **LEGACY**: retained exact regression/compatibility path.

No changed path is orphaned or uncertain.

### Repository-root workflow — 27 paths

**ACTIVE**

`make_subsamples.sh`, `merge_root_files.sh`,
`resolve_publication_gate_b_signoff.sh`, `runCondorJob.sh`,
`run_publication_gate_a.sh`, `run_publication_gate_b.sh`,
`run_publication_gate_c.sh`, `run_publication_gate_d.sh`,
`run_status_analysis.sh`, `setupEnv.sh`, `submit_full_production.sh`,
`submit_full_retry.sh`, `submit_gate_b_analysis.sh`,
`submit_gate_b_pilots.sh`, and `submit_status_analysis.sh`.

These paths implement environment pinning, immutable campaign/seed evidence,
canonical manifest selection, receipt-bound analysis, exact retries, Gates
A--D, and fail-closed launch authorization. Each is covered by shell syntax
validation plus focused campaign, submission, provenance, or gate tests.

**LEGACY**

`make_subsamples_legacy.sh`, `merge_root_files_legacy.sh`,
`runCondorJob_legacy.sh`, `run_status_analysis_legacy.sh`, and
`submit_status_analysis_legacy.sh`.

These are exact compatibility copies of the pre-correction workflow. Their
numerical contents were not modernized. Executable mode was restored so the
documented regression remains runnable.

**SUPPORTING**

`.gitignore`, `Condor_README.md`,
`PUBLICATION_READY_CODING_AGENT_INSTRUCTIONS.md`, `README.md`,
`REPOSITORY_FILE_CATALOG.md`, `REPRODUCIBILITY.md`, and
`plotting_documentation.md`.

The ignore changes cover generated production, campaign, analysis, compiled
producer, ACLiC, and plot outputs. They do not hide source, configurations, or
paper inputs.

### Analysis — 7 paths

**ACTIVE**

`AnalysisScripts/AssociateOriginCategoryContract.h`,
`AnalysisScripts/GeneratedPairRegistry.h`,
`AnalysisScripts/MergeAnalysisObjects.C`,
`AnalysisScripts/MergeCanonicalAnalysis.C`, and
`AnalysisScripts/status_analysis_THnSparse_qq.C`.

These paths implement the single raw scan, 300 signed pair outputs,
role-dependent direct-primary selection, versioned associate-origin
decomposition, exact input preflight, canonical/all-block provenance, typed
metadata, axis-safe merging, and central-versus-ten-block closure.

**LEGACY**

`AnalysisScripts/status_analysis_THnSparse_qq_legacy.C` is the unmodified
Paul-compatible analysis snapshot.

**SUPPORTING**

`AnalysisScripts/Analysis_README.md` documents raw inputs, ROOT objects,
metadata, origin categories, pair identity, and canonical/block invocation.

### Plotting — 18 paths

**ACTIVE**

`PlottingScripts/MultiplicityBoundaryUtils.h`,
`PlottingScripts/PairInputSelectionUtils.h`,
`PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C`,
`PlottingScripts/Plot_MultiplicityDistribution_PercentileBoundaries.C`,
`PlottingScripts/Validate_THnSparse_Production.C`,
`PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json`,
`PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json`,
`PlottingScripts/improvedPlotting_THnSparse.C`,
`PlottingScripts/run_paper_plots.sh`,
`PlottingScripts/summarize_subsample_coverage.py`,
`PlottingScripts/validate_subsample_log.py`, and
`PlottingScripts/validate_thnsparse_inputs.sh`.

The two checked-in configurations are relative, select MONASH/JUNCTIONS/
CLOSEPACKING, require ten blocks, and set `calculate_errors=true`. The reduced
configuration limits triggers, associates, canvases, and drawn activity bins
but retains the same central/block error prescription. The runner's smoke
target no longer repeats the complete 300-million-event raw-kinematics scan.

The plotting changes retain Paul's calculation structure while adding exact
pair/selection identities, legacy-versus-v2 projection policy, shared
multiplicity boundaries, numerator-tune styling, finite-denominator checks,
sample SEM, nonlinear within-block ratios, independent-tune propagation,
per-bin correlation SEM, log-envelope clipping guards, optional-pad safety,
strict coverage, and checksum-bound output provenance. A parity test prevents
the shared selector helper and Paul adapter from drifting across their 12 ROOT
metadata objects and 14 JSON fields.

**SUPPORTING**

`PlottingScripts/FinalAnalysis/README.md`,
`PlottingScripts/PAPER_FIGURE_PROVENANCE.md`,
`PlottingScripts/PtMultiplicity/README.md`,
`PlottingScripts/README.md`,
`PlottingScripts/validation/FINAL_PLOTTING_HANDOFF.md`, and
`PlottingScripts/validation/removed_tracked_plot_inventory.txt`.

Historical validation JSON files named in the 2026-07-29 handoff were not
committed with that branch. The documentation now labels their numerical
summaries as unavailable external historical evidence rather than live
repository provenance.

### Simulation — 12 paths

**ACTIVE**

`SimulationScripts/GeneratedHeavyFlavourRegistry.h`,
`SimulationScripts/GeneratedTuneSettingRegistry.h`,
`SimulationScripts/GeneratedWeakParentRegistry.h`,
`SimulationScripts/HeavyFlavourUtils.h`, `SimulationScripts/Makefile`,
`SimulationScripts/Sha256.h`,
`SimulationScripts/heavyflavourcorrelations_status.cpp`, and the three
`SimulationScripts/pythiasettings_Hard_Low_ccbb_{MONASH,JUNCTIONS,CLOSEPACKING}.cmnd`
cards.

These implement complete signed constituent content, physical baryon number,
direct-primary lifecycle, generator stabilization, the pure graph-based hard
origin matcher, parent-aware carrier uniqueness, weak-transition auditing,
exact success accounting, integer identities, event weights, raw-v5 resource
metadata, settings hashes, deterministic seeds, and strict builds.

Tune-card edits are limited to exact PYTHIA setting spelling, output
suppression, and removal of an incomplete hand-maintained stable-particle
list after complete programmatic stabilization and audit. The tune allowlist
validates 44 effective keys and exactly 28 declared differences.

**SUPPORTING**

`SimulationScripts/Simulation_README.md`.

**GENERATED**

`SimulationScripts/ccbarcorrelations_status` is a tracked compiled executable
deleted from version control and now explicitly ignored. No source program was
removed.

### Validation — 20 paths

**ACTIVE**

`Validation/ValidateCanonicalRawManifest.C`,
`Validation/ValidateGateDPilotAnalysis.C`,
`Validation/ValidatePairBlockClosure.C`,
`Validation/ValidatePairDirectory.C`, `Validation/ValidateRawOutput.C`,
`Validation/validate_canonical_manifest.sh`,
`Validation/validate_pair_block_closure.sh`,
`Validation/validate_pair_directory.sh`, and
`Validation/validate_raw_output.sh`.

These independently validate raw-v5 types and invariants, pair object types,
signed identities, origin metadata, all/block closure, canonical manifests,
receipts, weights, and Gate-D pilot results. `ValidateRawOutput.C` is clean
under `-Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror`.

**SUPPORTING**

`Validation/AuditOriginResolution.C`, `Validation/AuditSpeciesRegistry.C`,
`Validation/AuditTuneSettings.C`, `Validation/ListUnresolvedOrigins.C`,
`Validation/PTHatSensitivity.C`, `Validation/TestAnalysisRawInputContract.C`,
`Validation/TestHardCarrierUniqueness.C`,
`Validation/TestInclusiveRawKinematics.C`,
`Validation/TestPlotProjectionCuts.C`,
`Validation/TestPlotReferenceMultiplicityContracts.C`, and
`ValidationReports/PREPRODUCTION_GATE_REPORT_20260730.md`.

### Configuration — 9 paths

All are **ACTIVE**:

`config/dataset_selector.json`,
`config/heavy_flavour_pair_registry_v1.json`,
`config/heavy_flavour_species_v1.json`,
`config/pair_registry_definition_v1.json`,
`config/pdg_2025_species_reference_v1.json`,
`config/pthat_sensitivity_v1.json`,
`config/statistical_robustness_v1.json`,
`config/tune_difference_allowlist_v1.json`, and
`config/weak_decay_parent_registry_v1.json`.

The PDG, pThat, and statistical specifications deliberately retain pending
review states. A pending file cannot authorize production or publication.

### Audit and owner templates — 4 paths

All are **SUPPORTING**:

`docs/audits/PRE_IMPLEMENTATION_SOURCE_OF_TRUTH_AUDIT.md`, this report,
`docs/templates/FINAL_SCIENTIFIC_REVIEW.template.json`, and
`docs/templates/PUBLICATION_DATASET_AUTHORIZATION.template.json`.

The templates contain explicit invalid placeholder fields and are
intentionally rejected by validators. They cannot be mistaken for approvals.

### Tests — 39 paths

All are **SUPPORTING** and correspond directly to changed contracts:

`tests/test_analysis_boundary_binning.py`,
`tests/test_analysis_raw_input_contract.py`,
`tests/test_associate_origin_category.cpp`,
`tests/test_associate_origin_category_contract.py`,
`tests/test_campaign_manifest.py`,
`tests/test_canonical_merge_contract.py`,
`tests/test_canonical_postproduction_contract.py`,
`tests/test_dataset_selector.py`,
`tests/test_external_header_warning_contract.py`,
`tests/test_final_origin_closure.py`,
`tests/test_final_plot_provenance.py`,
`tests/test_full_submission_contract.py`,
`tests/test_gate_b_analysis_validation.py`,
`tests/test_gate_b_submission_contract.py`,
`tests/test_gate_c_missing_evidence.py`,
`tests/test_heavy_flavour_utils.cpp`,
`tests/test_observable_contract.py`,
`tests/test_pair_block_closure.py`,
`tests/test_pair_selection_contract_parity.py`,
`tests/test_pair_trigger_identity.py`,
`tests/test_pdg_species_audit.py`,
`tests/test_plot_dataset_integration.py`,
`tests/test_plot_reference_multiplicity_contract.py`,
`tests/test_pthat_sensitivity.py`,
`tests/test_publication_eligibility.py`,
`tests/test_publication_gate_b.py`,
`tests/test_publication_gate_c.py`,
`tests/test_publication_gate_d.py`,
`tests/test_pythia_runtime.cpp`,
`tests/test_pythia_runtime_contract.py`,
`tests/test_raw_v5_resource_contract.py`, `tests/test_registry.py`,
`tests/test_setup_environment_contract.py`,
`tests/test_statistical_robustness.py`,
`tests/test_submission_registry_baseline.py`,
`tests/test_submit_rendering.py`,
`tests/test_superseding_canonical_expansion.py`,
`tests/test_validate_raw_output_strict_compile.py`, and
`tests/test_worker_provenance_contract.py`.

No unrelated test was added.

### Tools — 30 paths

**ACTIVE**

`tools/build_producer.sh`, `tools/build_submission_registry_baseline.py`,
`tools/campaign_manifest.py`, `tools/canonical_manifest.py`,
`tools/canonical_merge_contract.py`, `tools/dataset_selector.py`,
`tools/evaluate_pthat_sensitivity.py`, `tools/final_origin_closure.py`,
`tools/final_plot_provenance.py`, `tools/gate_c_workflow_audit.py`,
`tools/generate_expansion_evidence.py`,
`tools/generate_gate_b_pilots.py`,
`tools/generate_registry_artifacts.py`, `tools/merged_pair_provenance.py`,
`tools/pdg_2025_species_audit.py`, `tools/publication_eligibility.py`,
`tools/render_analysis_submit.py`,
`tools/render_gate_b_analysis_submit.py`,
`tools/render_production_submit.py`,
`tools/resolve_publication_gate_b_signoff.py`,
`tools/run_publication_gate_a.py`, `tools/run_publication_gate_b.py`,
`tools/run_publication_gate_c.py`, `tools/run_publication_gate_d.py`,
`tools/statistical_robustness.py`, `tools/validate_analysis_outputs.py`,
`tools/validate_analysis_raw_receipt.py`,
`tools/validate_gate_b_analysis_outputs.py`, and
`tools/validate_tune_cards.py`.

These are the deterministic implementation of the gate, campaign, selector,
merge, provenance, expansion, and validation contracts. Their size is a
reviewability risk—especially the roughly 8,500-line
`tools/campaign_manifest.py`—but their changes are not opportunistic: each
subcommand is exercised by a focused positive and adversarial test.

**SUPPORTING**

`tools/generate_file_catalog.py`.

### Generated plot deletion — 78 paths

All 78 paths are **GENERATED**, not paper sources. They are the stale tracked
PDF, PNG, and generated ROOT-macro products under
`PlottingScripts/Plots/THnSparse` and
`PlottingScripts/Plots/THnSparseCompleteRoot`. The exact exhaustive list and
count are in
`PlottingScripts/validation/removed_tracked_plot_inventory.txt`. No file in
the protected paper tree was deleted or replaced.

## Validation completed before commit

- all Python test entry points under `tests/test_*.py`: PASS;
- C++ heavy-flavour utility and associate-origin tests with strict warnings:
  PASS;
- registry regeneration check: 50 signed states and 300 signed pairs, PASS;
- tune-card allowlist: 44 keys and 28 declared differences, PASS;
- all repository JSON files parsed; both active plotting configurations
  passed `jq`;
- all 36 shell scripts passed `bash -n`;
- 66 Python files passed byte compilation with cache output isolated outside
  the repository;
- 23 ROOT macros compiled/loaded independently with ROOT 6.38.04 from an
  isolated build directory;
- 14 self-contained ROOT test entry points passed;
- manifest-backed plotting integration passed for 100- and 110-file/tune
  fixtures, reserved-file exclusion, and deliberate checksum tampering;
- strict raw validator compilation passed;
- `git diff --check`: PASS.

`Validation/AuditSpeciesRegistry.C` is the sole local compile exception
because the Mac has no PYTHIA headers. It must be compiled and run in the
pinned Nikhef ROOT/PYTHIA environment from the exact candidate commit.
Likewise, the local PYTHIA runtime contract correctly reports a skip rather
than a pass.

## Independent editor findings and unresolved blockers

### Scientific decisions

- Six signed operational species (`+/-5212`, `+/-5312`, `+/-5322`) remain
  `NEEDS_PHYSICS_REVIEW`. Algorithm-versus-registry tests do not independently
  establish their physical truth.
- `config/pthat_sensitivity_v1.json` remains pending owner review. No pThat
  acceptance may be inferred.
- No final origin-resolution decision, Gate-A--D PASS set, or full launch
  authorization exists.

### Storage and production

The latest read-only Nikhef snapshot at
`2026-07-30T17:39:21+02:00` reported:

- capacity: `36,688,187,162,624` bytes;
- `f_bavail`: `1,671,602,503,680` bytes;
- required 5% reserve: `1,834,409,358,131` bytes;
- deficit before new allocation: `162,806,854,451` bytes, about 151.7 GiB.

No full production, Gate-B campaign, or publication analysis may be launched
while the fresh capacity check remains below the reserve floor.

### Protected paper

The paper remains a protected scientific input and has not been edited.
Before publication it must resolve:

- `Model.tex` role-threshold, multiplicity, legacy-yield, and multi-parameter
  tune-package discrepancies;
- `Observables.tex`'s generic electric-charge formula versus the implemented
  identified signed-heavy-flavour, ordered, trigger-conditional, per-trigger
  OS-minus-SS observable and reference-meson ratio;
- the unsupported statement that close packing changes the perturbative
  heavy-quark production probability;
- incorrect D0/D+/Lambda-c/reference-meson and beauty/charm captions;
- stale red/purple style descriptions;
- causal claims inconsistent with the effective tune cards, including the
  `probQQ1toQQ0join` narrative;
- seven duplicate `fig:placeholder` labels, `COMMENTS:` captions,
  `UNDER CONSTRUCTION`, `[check]`, and other drafting language.

No current full-paper figure has sealed raw-v5 provenance. These are release
blockers, not cosmetic follow-up.

## Verdict

The changed executable scope is justified and materially safer than stable
main. No disconnected legacy physics program was opportunistically
modernized, and Paul's active plotting architecture remains the consumer
contract.

The implementation can be committed and subjected to exact-commit Nikhef
validation. The study cannot yet be called publication-ready: physics review,
pThat approval, storage, canonical production, sealed ten-block analysis,
final figures, paper revision, and independent human review remain mandatory.
