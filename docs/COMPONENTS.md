# Component catalog

This catalog maps executable code to its input, output, and enforcing contract.
It separates publication entrypoints from libraries, generators, validators, and diagnostics.

## How to read the catalog

An **entrypoint** starts a complete task from a documented command.
A **library** supplies shared code and does not start work alone.
A **generator** writes source, configuration, or a report from another declared input.
A **validator** returns failure when an input violates a contract.
A **diagnostic** measures or compares data without producing a publication target.
A **generated artifact** records derived definitions that consumers read directly.

The contract column names the independent check that detects drift.
A source test checks logic without campaign data.
A gate checks real input before promotion or publication.
A `digest` binds a generated file to its definition or run record.

PUBLIC status does not mean that a program participates in the published chain.
Section 11 identifies retained diagnostics and unusable compatibility paths.

The PUBLIC file set spans fourteen top-level directories.
This map assigns one reader-facing role to each directory before the detailed catalog.

| Directory | Reader-facing role |
|---|---|
| `AnalysisScripts/` | Frozen generated contracts, decay maps, and committed anchors. |
| `paper/` | PUBLIC-BLOCKED manuscript sources, bibliography, claim checklist, and build record. |
| `references/` | The PUBLIC bibliography. |
| `Validation/` | ROOT validators and fail-closed boundary checks. |
| `results/` | Machine-readable results, systematics products, and validation evidence; accepted scientific figures enter `results/figures/main/` only with receipts. |
| `analysis/` | Reduction code and pair-level diagnostics. |
| `config/` | Scientific contracts, selectors, registries, and dependency pins. |
| `docs/` | Spine documents and retained evidence. |
| `extraction/` | Table, trend, and uncertainty programs. |
| `generation/` | Producer code, tune cards, registries, and campaign submission. |
| `merging/` | Central and block merge programs. |
| `plotting/` | ROOT plotting, configuration generation, and input/coverage validation. |
| `tests/` | Source, schema, statistics, output, and documentation contract checks. |
| `tools/` | Campaign, environment, generation, validation, and repository tools. |

The catalog treats scientific results, reproduction evidence, validation, diagnostics, and history as separate roles.
No diagnostic or historical component is a publication result or a required runnable dependency.

## Generation components

The generation stage writes the only raw event files in the chain.
Downstream stages read those files and never generate PYTHIA events.

| Component | Role and data flow | Enforcing contract |
|---|---|---|
| `generation/producer/heavyflavourcorrelations_status.cpp` | Entrypoint that initializes PYTHIA, generates events, and writes raw trees and audit metadata. | `Validation/validate_raw_output.sh` runs `ValidateRawOutput.C`; `tests/test_raw_v5_resource_contract.py` checks stored metadata. |
| `generation/producer/HeavyFlavourUtils.h` | Library for heavy content, ancestry, event activity, species roles, and uniqueness handling. | Producer and mapping tests compare its constants and sign rules with generated contracts. |
| `generation/producer/Sha256.h` | Library that computes file digests inside the producer. | Worker-side binary and card checks compare its output with rendered values. |
| `generation/producer/Makefile` | Build entrypoint for the producer binary. | `tools/build_producer.sh` supplies the pinned environment; `make check` runs the source contracts. |
| `generation/submit/runCondorJob.sh` | Batch entrypoint that checks identity, runs one job, validates it, and promotes its raw file. | It checks the commit, card `digest`, producer `digest`, seed, and raw-validation receipt before promotion. |
| `tools/render_production_submit.py` | Generator for immutable Condor submit files and deterministic job rows. | Campaign tests cover seed burning, attempt limits, card identity, and write-once output. |
| `tools/campaign.py` | Library for tune lists, paths, campaign ordinals, attempts, seeds, and the seed ledger. | `tests/test_seed_derivation.py` and `tests/test_submit_rendering.py` recompute the same identities. |
| `generation/submit/submit_status_analysis.sh` | Reduction submit entrypoint over a sealed raw manifest. | It validates the manifest and existing analysis outputs before rendering jobs. |
| `tools/render_analysis_submit.py` | Generator for manifest-only reduction submit files. | It verifies each raw file and validation receipt against the manifest before writing. |
| `generation/run_hf.sh` | Compatibility runner intended to start one local producer job. | No gate can run because its four producer arguments do not match the current eight-argument interface. |

The nominal cards are the complete `generation/cards/pythiasettings_Hard_Low_ccbb_{MONASH,JUNCTIONS,CLOSEPACKING}.cmnd` tune bundles.
The `JUNCTIONS_MATCHED` card is a retained comparison card, not a publication tune.
The 21 files under `generation/cards/systematics/` cover seven variations for each tune.
`tools/validate_tune_cards.py` and `tests/test_systematics_variation_cards.py` enforce their setting and inheritance rules.

`generation/registries/GeneratedHeavyFlavourRegistry.h` fixes species roles for the producer.
`generation/registries/GeneratedTuneSettingRegistry.h` fixes audited tune settings.
`tools/generate_registry_artifacts.py` generates both headers from their editable registries.
`make registry` fails when either generated header drifts.

## Reduction components

The publication reduction reads each raw file once and writes 300 pair files.
The wrapper stages all files, validates the complete `pair directory`, and then promotes it.

| Component | Role and data flow | Enforcing contract |
|---|---|---|
| `analysis/status_analysis_THnSparse_qq.C` | Frozen one-pass reduction macro for the publication pair schema. | Its stored source `digest`, `ValidatePairDirectory.C`, and the pair-object contract bind its output. |
| `analysis/run_status_analysis.sh` | Entrypoint that runs the macro, writes staging output, validates all 300 files, and promotes atomically. | `Validation/validate_pair_directory.sh` and output-side tests reject incomplete or mismatched output. |
| `tools/render_analysis_submit.py` | Generator that maps each canonical manifest row to one reduction job. | Raw file, receipt, commit, macro `digest`, and logical identifier must match before rendering. |
| `analysis/a2_pair_yield.C` | Diagnostic reducer that writes one slot's baseline or permissive A2 yields. | A2 regression sentinels and `analysis/a2_block_shift.py` bind each accepted variation. |
| `analysis/a2_block_shift.py` | Entrypoint that combines A2 slot CSV files into block shifts. | It requires PASS evidence for the named variation `digest` in `config/a2_variations_v1.json`. |
| `tools/a2_make_subs.py` | Generator for A2 reduction submit files. | A2 tests require complete slot coverage and injected provenance for archived deployments. |
| `tools/a2_make_largest_index_variation.py` | Generator for the alternate A2 tie-break source. | It checks the expected source edit and records the produced `digest`. |
| `tools/a2_record_regression.py` | Generator for an A2 regression sentinel. | The analyzer validates its PASS status, variation name, and source `digest`. |
| `tools/a2_extract_yields.sh` | Entrypoint that runs `a2_pair_yield.C` across produced slot directories. | The A2 analyzer rejects absent, duplicate, or unregistered rows. |
| `tools/a2_quarantine_outputs.py` | Diagnostic that moves invalid A2 outputs out of the consumable set. | Tests check the quarantine inventory and refuse ambiguous restoration evidence. |
| `analysis/hf_mult_pt_analysis_multi.C` | Legacy combined reduction for transverse-momentum and multiplicity diagnostics. | Its wrapper checks three input directories, ROOT, and the requested charge mode. |
| `analysis/run_hf_analysis.sh` | Entrypoint for the legacy combined reduction. | It refuses absent tune directories, invalid block counts, and invalid charge modes. |

## Merging components

The merge driver creates one central `merged product` and ten `block` products per tune.
The driver derives file counts from the canonical manifest rather than a fixed campaign size.

| Component | Role and data flow | Enforcing contract |
|---|---|---|
| `merging/MergeAnalysisObjects.C` | Library that merges declared ROOT objects and metadata from an input list. | The generated pair-object contract defines merge semantics and expected types. |
| `merging/MergeCanonicalAnalysis.C` | Entrypoint that merges registered pair files for one tune and scope. | `ValidatePairDirectory.C` checks the result before promotion. |
| `merging/merge_root_files.sh` | Stage entrypoint that creates three central products and 30 blocks, then runs closure. | It requires `HADRONIZATION_EXPECTED_PAIR_SCHEMA`; directory, provenance, and closure gates must pass. |
| `tools/validate_analysis_outputs.py` | Pre-merge validator over every canonical per-job `pair directory`. | It checks the manifest, raw receipt, metadata, pair registry, and pair-object schema. |
| `tools/merged_pair_provenance.py` | Generator and validator for merged inventories and source manifests. | It recomputes file `digest` values and rejects missing, extra, or rebound inputs. |
| `merging/make_subsamples.sh` | Compatibility entrypoint that claims to delegate to the merge driver. | It currently resolves `merging/merging/merge_root_files.sh`, so it cannot reach the gate. |

`tools/merge_supervisor.sh` restarts an interrupted variation merge after its prechecks.
`tools/supervisor_eol_watch.sh` stops that supervisor after a clean completion marker.
`tools/harvest_launch_merge.sh` adds six refusal checks, a host-bound lock, and an identity record.
`tools/campaign_closure_status.py` counts closure markers across merge and rerun logs.

## Extraction and statistics components

The extraction programs transform validated `merged product` inputs into committed tables and reports.
They do not modify the ROOT inputs.

| Components | Role and data flow | Enforcing contract |
|---|---|---|
| `extract_species_decomposition.py`, `apply_decay_map.py` | Project the fixed species axis and map species onto terminal ground states. | The species-axis `digest`, pair registry, and explicit decay-map argument must agree. |
| `decompose_with_block_sems.py`, `three_tune_table.py` | Form structural and experiment-comparable tables with ten-block standard errors. | Integrity checks compare central, block, category, and species totals; tests use independent fixtures. |
| `second_branch_weight.py`, `compare_subset_parent.py` | Measure dominant-map exposure and compare a subset with its parent under a named null. | Both refuse missing maps or an unnamed statistical model; anchor tests supply mutations. |
| `bbaryon_tune_advisory.py`, `aggregate_m7.py` | Produce the beauty-baryon advisory and inclusive unresolved-origin summaries. | Their tests fix the input columns, tune coverage, and block arithmetic. |
| `harvest_class_axis.py`, `harvest_class_report.py` | Parse class identities from plot logs and write class-resolved reports. | Parser tests enforce `c1` through `c11`, integrated rows, and unique five-field identities. |
| `harvest_deltas.py`, `harvest_yield_deltas.py` | Join nominal and variation logs into category and yield shifts. | Harvest tests reject incomplete tune, source, class, and observable coverage. |
| `systematics_delta.py`, `combine_per_class.py` | Calculate block deltas, choose arms, apply the SEM floor, and combine sources. | Independent arithmetic tests enforce policies and exclude S6 from the class sum. |
| `combine_derived.py`, `ratio_trend.py` | Calculate tune separations, endpoint contrasts, slopes, and fit diagnostics. | Tests check independent-campaign propagation, weights, and class ordering. |
| `write_per_class_report.py`, `write_combination_report.py` | Render per-class and combined systematic tables from machine-readable results. | Schema and snapshot tests compare headings, rows, status, and numeric formatting. |
| `write_ratio_trend.py`, `write_tune_separation.py`, `write_verdict.py` | Write trend, separation, and final uncertainty verdict artifacts. | Tests recompute the source JSON and require complete tune and class coverage. |
| `extraction/pipeline/harvest_tune.py` | Site harvest driver for closure, extraction, integrity, and decomposition. | It requires the v3 counts 2,100 and 1,500 and checks all three tune products. |
| `extraction/pipeline/tune_extract.sh` | Portable entrypoint for one central and ten block extractions with explicit external roots. | Its preflight requires 300 ROOT files in each directory and records source and contract `digest` values. |
| `extraction/pipeline/tune_chain.sh` | Orchestration for wait, closure, and extraction. | It requires the schema and external roots, checks the tracked callee before waiting, and stops on either stage failure. |

`tools/reconstruct_deduplicated_decomposition.py` rebuilds corrected decomposition tables from committed inputs.
`tools/vintegrated_closure.py` checks multiplicity-integrated closure.
`tools/systematic_class_migration.py` measures boundary migration under a changed counter.
`tools/evaluate_pthat_sensitivity.py` interprets the registered hard-process threshold scan.

## Plotting components

The publication plotting entrypoint is `plotting/run_paper_plots.sh`.
It creates ROOT-rendered candidates without final-plot provenance sidecars.
The THnSparse macro stages output and promotes it only after its multiplicity-boundary receipt passes.
Accepted scientific bytes enter `results/figures/main/`; the external central and ten-block campaign products and final accepted bytes are absent here.
The balancing plots obtain trigger normalization from `hTrKinematics`.
Tune comparisons are bundle-to-bundle across the three complete nominal cards.

| Components | Role and data flow | Enforcing contract |
|---|---|---|
| `improvedPlotting_THnSparse.C` | Frozen main macro for balancing-yield canvases and uncertainty-matrix logs. | Its `digest`, pair-object schema checks, dataset selector, and boundary receipts bind each render. |
| `Plot_InclusiveKinematicSpectra_Raw.C` | Plots inclusive raw spectra and the common multiplicity axis. | Raw manifest, seal, input-contract, style, and output-side tests run before promotion. |
| `Plot_KinematicSpectra_THnSparse.C` | Projects kinematic spectra from pair files with ten-block uncertainties. | Projection-cut, input-schema, and complete-block tests guard each selection. |
| `Plot_MultiplicityDistribution_PercentileBoundaries.C` | Draws the minimum-bias spectrum and fixed class boundaries. | Boundary utilities, the boundary artifact `digest`, and plotting receipts must agree. |
| `Plot_FlavourClosure.C` | Diagnostic plot of category and species closure. | It reads committed extraction tables; closure tests check the same totals independently. |
| `Validate_THnSparse_Production.C` | Plot-input validator for manifests, objects, schemas, and union consistency. | `plotting/validate_thnsparse_inputs.sh` converts its summary into a fail-closed gate. |
| `make_hf_run3_v1_three_tune_config.py` | Generates the ten-panel three-tune configuration from the MONASH source. | `tests/test_three_tune_plot_config.py` rejects generated drift. |
| `summarize_subsample_coverage.py`, `validate_subsample_log.py` | Report and validate ten-block coverage in plot logs. | Tests reject missing blocks, low coverage, duplicate rows, and wrong expected counts. |
| `validate_thnsparse_inputs.sh` | Shell gate for central, block, manifest, and selector input validation. | The plotting driver requires its PASS result before ROOT rendering. |
| `results/provenance/figure_acceptance_manifest_v1.json` | Records the P1-P8 candidate, rejection, acceptance, input, output, and retrieval state. | `tests/test_plot_reference_multiplicity_contract.py` rehashes every tracked contract it names and requires zero accepted roles while blockers remain. |

`HistogramErrorUtils.h` implements block standard errors for plots.
`PairInputSelectionUtils.h` resolves pair files by role and signed identity.
`StagedOutputs.h` implements stage-then-promote output handling.
`TunePlotStyle.h` fixes tune colours, markers, draw order, and class line styles.

`CommonMultiplicityBoundaries.h`, `MultiplicityBoundaryUtils.h`, and `GeneratedClassLabelPrecision.h` implement the shared class axis.
Their source and artifact `digest` values appear in the boundary receipts.
`PtMultiplicity/PlottingPathUtils.h` resolves legacy diagnostic inputs without defining a publication dataset.

The JSON files under `plotting/` select live, diagnostic, or variation renders.
`tools/apply_class_labels.py`, `make_variant_configs.py`, and `make_harvest_plot_configs.py` own different generated configurations.
Generator-owner fields and `--check` modes prevent one generator from rewriting another generator's file.

## Validation components

Automated validators run inside a worker, merge, plot, or test entrypoint.

| Validator | What it checks | Direct caller or contract |
|---|---|---|
| `ValidateRawOutput.C`, `validate_raw_output.sh` | Raw schema, metadata, event accounting, species, and origin audit. | The production worker requires its receipt before promotion. |
| `AuditOriginResolution.C`, `ListUnresolvedOrigins.C` | Aggregate and row-level origin-resolution evidence. | The production worker runs both after raw validation. |
| `ValidateCanonicalRawManifest.C`, `validate_canonical_manifest.sh` | Every manifest row, raw `digest`, seed, and event count. | Reduction submission and canonical manifest tests invoke it. |
| `ValidatePairDirectory.C`, `validate_pair_directory.sh` | Exact 300-file registry, types, metadata, and duplicate trigger-owned histograms. | Reduction and merge promotion require its PASS line. |
| `ValidatePairBlockClosure.C`, `validate_pair_block_closure.sh` | Central-to-block content, identity, metadata, and source-filter closure. | The merge driver and site extraction chain require its schema-specific result. |
| `AuditSpeciesRegistry.C` | Generated species registry against installed PYTHIA particle data. | Registry tests compile and invoke it with the pinned environment. |
| `TestAnalysisRawInputContract.C` | Raw reader compatibility for the reduction macro. | The source suite runs it with synthetic ROOT fixtures. |
| `TestPlotReferenceMultiplicityContracts.C` | Reference multiplicity and plot-input assumptions. | Plot contract tests invoke it in memory. |

Measured-manual validators have committed result records but do not run in every pipeline execution.

| Validator | Recorded measurement | Scope |
|---|---|---|
| `CalibrateMultiplicityAgainstMinBias.C` | PYTHIA 8.315 and 8.317 multiplicity calibrations and threshold scans. | It derives a class calibration from a separate minimum-bias sample. |
| `CalibrateBothCountersAgainstMinBias.C` | The narrow and wide counter comparison. | Its source `digest` is pinned by the systematics run record. |
| `CompareNominalReproduction.C` | Nominal-versus-rebuilt generator control. | It compares trees and metadata for registered variation work. |
| `MeasureUnresolvedSystematic.C` | Inclusive unresolved-origin effect by sector. | It measures an auxiliary validation quantity, not the pair-level S6 result. |
| `PTHatSensitivity.C` | Hard-process threshold scan inputs. | `evaluate_pthat_sensitivity.py` applies the registered decision rules. |
| `ValidateSpeciesAxisClosure.C` | Exact closure between 202 species and six categories. | The species-axis validation record supplies the measured result. |

Five validators have no live caller and no committed run output: `AuditTuneSettings.C`, `TestHardCarrierUniqueness.C`, `TestInclusiveRawKinematics.C`, `TestPlotProjectionCuts.C`, and `TestPrimaryChargedDefinition.C`.
Their source tests check structure where possible, but the repository does not establish a campaign run.

## Contracts, registries, and generated files

Editable JSON contracts under `config/` define identities before code consumes them.
Generators write headers or derived JSON, and drift tests compare both forms.

| Editable definition | Generated consumer or artifact | Drift enforcement |
|---|---|---|
| `config/heavy_flavour_species_v1.json` | `generation/registries/GeneratedHeavyFlavourRegistry.h` | `generate_registry_artifacts.py --check`; species-registry tests. |
| `config/heavy_flavour_pair_registry_v1.json` | `AnalysisScripts/GeneratedPairRegistry.h` | Registry generator and exact 300-pair tests. |
| `config/tune_difference_allowlist_v1.json` | `generation/registries/GeneratedTuneSettingRegistry.h` | Tune-card validator and registry `digest` checks. |
| `config/pair_file_object_contract_v1.json` | `AnalysisScripts/GeneratedPairObjectContract.h` | `generate_pair_object_contract.py --check`; schema-prefix tests. |
| `AnalysisScripts/species_ordinals_v2.json` | `AnalysisScripts/GeneratedSpeciesOrdinals.h` | `generate_species_ordinals_header.py --check`; fixed count and `digest` test. |
| Associate-origin category definitions | `AnalysisScripts/AssociateOriginCategoryContract.h` | Compile tests compare its labels and indices with the producer definition. |
| Species ordinals and PYTHIA decay channels | `AnalysisScripts/decay_parent_map_v1_1.json` and v2 | Map builders enforce sign, conjugation, terminal, and weight invariants. |
| `config/multiplicity_class_boundaries_v1.json` | Plot headers and receipts | Boundary tests recompute edges, labels, and the artifact `digest`. |
| `config/systematics_variations_v1.json` | Cards, selectors, harvest configurations | Variant generators and identity tests require exact source rows. |

`AnalysisScripts/` holds frozen artifacts, and its name is historical because `digest` pins forbid moving it.

`tools/GenerateSpeciesOrdinals.C`, `f4_probe.cc`, `build_decay_parent_map.py`, and `build_decay_parent_map_v2.py` generate the species and decay artifacts.
`pdg_2025_species_audit.py` compares the selected species with the stated PDG source.
`generate_pair_object_contract.py`, `generate_registry_artifacts.py`, and `generate_species_ordinals_header.py` generate compiled consumers.

## Campaign and environment tools

Campaign tools divide into rendering, monitoring, recovery, environment, and configuration generation.

| Tools | Purpose | Contract |
|---|---|---|
| `render_production_submit.py`, `campaign.py`, `resubmit_held.py` | Render first attempts and bounded retries with deterministic seeds. | Seed-ledger, attempt, dirty-checkout, and write-once tests. |
| `campaign_status.py`, `campaign_closure_status.py`, `queue_probe.py` | Count filesystem results, closure markers, and queue state. | They distinguish EMPTY, NONEMPTY, and UNKNOWN and never infer success from queue absence. |
| `build_canonical_manifest.py` | Select successful canonical slots and bind raw validation evidence. | Manifest validator and selector tests check each row and freeze seal. |
| `checkout_advance_guard.py`, `install_checkout_guard_hook.sh` | Prevent checkout movement while pinned jobs remain. | Guard tests simulate live, empty, and unavailable queue states. |
| `doctor.sh`, `environment_verdict.sh`, `build_producer.sh` | Inspect dependencies, state runtime scope, and build with pinned versions. | `make check` prints the environment verdict last. |
| `dataset_selector.py` | Resolve one named dataset and export its paths and identity. | Selector tests reject an unnamed dataset, invalid status, missing fields, and publication misuse. |
| `apply_card_config.py`, `make_systematic_cards.py`, `add_variation_selector_rows.py` | Generate variation cards and selector rows from the variation registry. | `--check` modes and identity tests reject drift. |
| `make_harvest_configs.py`, `make_harvest_plot_configs.py` | Generate extraction and plotting configuration for seven campaigns. | Source-row and selected-dataset tests bind campaign, variation, and tune. |
| `apply_class_labels.py`, `class_label_format.py`, `make_variant_configs.py` | Generate consistent class labels and diagnostic plot configurations. | Generator ownership and boundary tests reject cross-generator edits. |
| `render_measurement.sh`, `render_balancing_variant.sh` | Run a measurement target or a diagnostic balancing variant. | Output-side assertions keep measurement artifacts outside publication targets. |
| `assert_measurement_outputs.py`, `assert_variant_identity.py` | Validate measurement representations and selected variation identity. | The plotting driver requires both before promotion. |
| `check_panel_caption_collisions.py`, `anchor_width_control.py` | Check figure geometry and the quarantined anchor's block-scale behaviour. | Geometry and anchor mutation tests supply independent controls. |
| `docs_check.sh`, `run_tests.sh` | Run documentation ownership advice and all Python test drivers. | The Makefile invokes both; `run_tests.sh` discovers tests by `test_*.py`. |

`tools/apply_card_config.py` also implements `make set-pthat`.
`tools/harvest_launch_merge.sh` needs site storage, a clean checkout, free disk, and an explicit schema.
`tools/merge_supervisor.sh` and `supervisor_eol_watch.sh` need the same site workspace and log layout.

## Manuscript components

The nine-file `paper/` package is the synchronized manuscript source closure.
The case-insensitive macOS work volume displays its physical parent with the
pre-existing `Paper/` spelling, while Git records the requested lowercase
path. The ignored historical paper subtree supplies structure only and is not
a build dependency.

| Component | Role and data flow | Enforcing contract |
|---|---|---|
| `paper/hfBalancingModelPaper.tex` and five section files | Build the contract-aligned review draft from committed result, systematic, and labelled validation evidence. | `paper/CLAIM_EVIDENCE.md` maps abstract, conclusion, numerical, and planned caption claims to evidence. |
| `paper/references.bib` | Supplies the six cited, DOI-deduplicated primary references without personal filesystem metadata. | The clean BibTeX build has no undefined keys or bibliography warnings. |
| `paper/BUILD_RECORD.md` | Records the exact build command, dependency closure, warnings, PDF digest, page review, and blockers. | A clean temporary-directory build and full-page visual review produced the recorded digest. |

The package includes no scientific image. The figure acceptance manifest marks
P1--P8 as candidates and accepts zero outputs, so the title page and build
record classify the draft PUBLIC-BLOCKED.

## Tests and enforced contracts

`tools/run_tests.sh` discovers the Python test drivers present in the selected
tree. A release record states the exact portable count run inside each export.
Some drivers compile or execute ROOT macros, so the script sources `setupEnv.sh` once.

| Guarded class | What the tests establish | Representative enforcement |
|---|---|---|
| Schema and registries | Raw, pair, species, tune, selector, map, and generated-header definitions agree. | Generator `--check` modes, negative schema fixtures, fixed counts, and fixed `digest` values. |
| Path resolution and identity | Repository roots, selector paths, deployed commits, source files, and campaign paths resolve without fallback drift. | Tests use relocated temporary checkouts, absent paths, symlinks, and mismatched `digest` values. |
| Closure and statistics | Central-to-block addition, species-to-category closure, estimators, deltas, trends, and source combinations match independent arithmetic. | Synthetic mutations must fail; hand-computed anchors must pass. |
| Output-side assertions | Staging, promotion, measurement isolation, and representation contracts fail closed where implemented. The figure manifest exposes the absent final sidecar recorder. | Tests mutate output trees, publication status, campaign identity, expected files, and figure-acceptance state. |
| Prose and repository contracts | Public citations, terminology, documentation classes, executable recipes, and generated audits remain current. | Dedicated documentation tests run the required prose, terms, and repository-audit checks. |

A passing source suite does not certify external campaign data or a production runtime.
`environment_verdict.sh` states that boundary and requires an explicit unpinned declaration elsewhere.

## Diagnostic and non-entrypoint components

The repository retains the `plotting/PtMultiplicity/` macros as diagnostics over legacy analyzed ROOT inputs.
No publication target invokes these files, and the required `AnalyzedData` inputs are absent from this checkout.

| Diagnostic | Function |
|---|---|
| `Build_HF_AllHistogramSubsampleFile.C` | Packages a broad set of legacy block histograms into one ROOT file. |
| `Build_HF_CombinedSubsamplesFile.C` | Packages the combined observables used by the legacy plotting macros. |
| `Plot_BaryonMesonRatio_CharmBeauty_MONASH_vs_JUNCTIONS_subsamples.C` | Compares charm and beauty baryon-to-meson ratios across two tunes. |
| `Plot_Beauty_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C` | Draws the beauty baryon-to-meson ratio across two tunes. |
| `Plot_Charm_BaryonMesonRatio_MONASH_vs_JUNCTIONS_subsamples.C` | Draws the charm baryon-to-meson ratio across two tunes. |
| `Plot_HF_MinimumBiasPtSpectra_MONASH_JUNCTIONS_subsamples.C` | Draws minimum-bias heavy-flavour spectra with block errors. |
| `Plot_HF_PtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C` | Draws the older focused spectra in five percentile classes. |
| `Plot_HF_Ratios_vsMultiplicityPercentile_subsamples.C` | Draws integrated baryon-to-meson ratios across five percentile classes. |
| `Plot_HF_SingleParticlePtSpectra_vsMultiplicity_MONASH_JUNCTIONS_subsamples.C` | Draws single-particle spectra by tune and percentile class. |
| `Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples.C` | Draws species-resolved spectra by tune and percentile class. |

These macros read `AnalyzedData/<DATE>/{Charm,Beauty}` block files.
They prefer combined `hf_` files and retain fallbacks for split `ccbar_` and `bbbar_` files.
`PlottingPathUtils.h` resolves the base from `HADRONIZATION_BASE`, macro location, `base_path.txt`, or the working directory.

The spectra normalize inside each block and use the standard error across blocks.
The ratio macros form each ratio inside its block before calculating the standard error.
The macros prefer `fHistTaggedMultiplicity` and fall back to `fHistMultiplicity` for older inputs.

The plot macros write under `plotting/PtMultiplicity/Plots`.
Several output names omit the date, so a later run can replace an earlier diagnostic.
`Build_HF_CombinedSubsamplesFile.C` defaults to `AnalyzedData/<DATE>/hf_combined_plot_histograms.root`.

`Plot_MultiplicityDistributions_TwoSamples.C` compares multiplicity distributions from two dated legacy samples.
`Plot_SelectedParticleYields_IndependentVsCombined.C` compares selected yields from independent and combined samples.
They need external `AnalyzedData` directories and do not satisfy the sealed selector contract.
The plotting driver labels both targets noncanonical.

Both macros write under `plotting/FinalAnalysis/Plots`.
The multiplicity macro normalizes each block before calculating its mean and standard error.
The yield macro prefers `fHistTaggedEventCount`, then `fHistEventCount`, then the multiplicity integral.
It forms the independent-to-combined ratio from block means and propagates both standard errors.

`statistical_robustness.py` and `final_origin_closure.py` have never run on a campaign in this project.
The first requires an origin-closure report that has never existed.
The second declares readiness only when `unresolved_trigger_candidate_count` equals zero.

That zero is structurally unreachable for the produced campaigns.
`HeavyFlavourUtils.h` demotes every duplicate hard-carrier claimant to `kUnresolved`.
The publication reduction accepts only `kSelectedHard` triggers and never tie-breaks ambiguous ancestry.
Committed A2 summaries record 124, 24,411, and 24,590 contested candidates across the three tunes.
Therefore, these tools cannot act as live publication gates despite their complete implementations and tests.

`AuditTuneSettings.C` and the four unrun `Test*.C` validators remain available diagnostics.
Presence in the tree does not establish that any campaign passed them.

`generation/run_hf.sh` and `merging/make_subsamples.sh` are executable but unusable compatibility paths.
The first supplies too few producer arguments.
The second duplicates `merging/` while resolving its merge driver.

## Entrypoint index

The environment column lists what must exist before the command can start useful work.

| Task | Authoritative command | Required environment and inputs |
|---|---|---|
| Inspect the checkout | `make doctor` | Python 3; no ROOT requirement for the report itself. |
| Run source contracts | `HF_ALLOW_UNPINNED_ENV=1 make check` | Python 3; ROOT and PYTHIA for the full pinned-runtime scope. |
| Build the producer | `make build` | `setupEnv.sh`, pinned ROOT, pinned PYTHIA, compiler, and generated registries. |
| Render production | `make submit-smoke ORDINAL=N` or another submit target | Clean checkout, built producer, campaign configuration, explicit ordinal, and writable seed ledger. |
| Run one production job | `generation/submit/runCondorJob.sh --campaign ...` | Rendered arguments, clean pinned checkout, CVMFS/runtime, card, producer, and storage root. |
| Build the canonical raw manifest | `make manifest FREEZE_DIR=...` | Completed raw files, validation receipts, production root, and writable freeze directory. |
| Render reduction | `generation/submit/submit_status_analysis.sh ... --dry-run` | Sealed manifest, production and analysis roots, clean checkout, ROOT, and Condor tools for submission. |
| Reduce one raw file | `analysis/run_status_analysis.sh RAW FINAL ...` | ROOT, raw file, clean or injected commit, macro, validator, and optional receipt binding. |
| Merge central and blocks | `HADRONIZATION_EXPECTED_PAIR_SCHEMA=v3 merging/merge_root_files.sh ...` | Sealed manifest, all per-job pair directories, ROOT, storage, clean checkout, and explicit schema. |
| Extract one tune | `extraction/pipeline/harvest_tune.py TUNE ...` | Validated central and blocks, closure log, Python 3, ROOT, registries, maps, and writable result directory. |
| Plot publication targets | `plotting/run_paper_plots.sh TARGET` | ROOT, selected dataset, validated inputs, plotting configuration, and writable staging directory. |
| Build the blocked manuscript draft | `latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error hfBalancingModelPaper.tex` from a clean copy of `paper/` | TeX Live with latexmk, pdfTeX, BibTeX, the seven TeX/BibTeX inputs, and no figure inputs. |
| Name a dataset | `HADRONIZATION_DATASET=KEY plotting/run_paper_plots.sh TARGET` | A selector containing `KEY`; alternatively set `DATASET_SELECTOR` to a one-campaign selector. |

The dataset selector has no active default in the combined file.
A caller must set `HADRONIZATION_DATASET` or select a per-campaign selector.
`HADRONIZATION_EXPECTED_PAIR_SCHEMA` is also required and has no default.
