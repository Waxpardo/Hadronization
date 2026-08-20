# Documentation rebuild plan — INTERNAL

This file is the execution map for the documentation rebuild. It is not part of
the published documentation.

The nine-document prose set is sound. The set needs no tenth prose document.
`LICENSE` and `CITATION.cff` remain necessary release metadata, but they sit
outside the prose spine. A later release session must add them.

The inventory has five dispositions:

- **SPINE** means rewrite the current file in place.
- **ABSORB — PROCESS PROSE** means move durable substance into the named spine
  section because the current file is an after-the-fact measurement or decision.
- **KEEP — DATED EVIDENCE** preserves a record whose chronology or separate
  tables would be lost. It covers registrations, paired run records,
  authorizations, and directed evidence-set records.
- **KEEP — MACHINERY** means preserve a path named by a digest registry,
  configuration field, or other operational contract.
- **DROP** means no current claim should descend from the file.

For both keep classes, the spine owns interpretation and citation. It does not
copy the record's tables or replace its provenance.

## 1. Section outlines

Each source cell names code, an anchor, or a measured record. A
writer must verify the source directly and must not treat this plan as evidence.

### `README.md`

| Section | What it must establish | Direct sources |
|---|---|---|
| What this study does | State the scientific question, the generator-level scope, and the comparison across three tunes. | `generation/cards/*.cmnd`; `generation/producer/heavyflavourcorrelations_status.cpp`; `config/heavy_flavour_pair_registry_v1.json` |
| Results in one page | Give the central decomposition, the multiplicity trend, and the uncertainty-qualified conclusion without duplicating evidence tables. | `AnalysisScripts/anchors/merged_*_dedup/central/*.csv`; `docs/systematics_results_20260820/verdict.json`; `plotting/paper/figures/*.svg` |
| Observable and analysis scope | Define trigger, associate, opposite-sign, same-sign, balancing yield, acceptance, and event activity. | `analysis/status_analysis_THnSparse_qq.C`; `plotting/improvedPlotting_THnSparse.C`; `config/multiplicity_class_boundaries_v1.json` |
| Repository map and evidence model | Distinguish source code, configuration, anchors, receipts, and derived result artifacts. | Tracked directory tree; `config/dataset_selector.json`; `AnalysisScripts/anchors/`; `docs/systematics_results_*` |
| Requirements and environment check | Name supported versions, local overrides, build checks, and the meaning of each failure. | `config/dependencies.conf`; `config/dependencies.local.conf.example`; `setupEnv.sh`; `Makefile`; `tools/doctor.sh` |
| Fast path from committed evidence | Rebuild the decay maps, decomposition, integrated yields, systematics tables, and paper figures without a new campaign. | `tools/build_decay_parent_map.py`; `tools/build_decay_parent_map_v2.py`; `extraction/`; `plotting/paper/make_paper_figures.py`; anchors and result JSON |
| End-to-end reproduction | Give the shortest safe route through generation, reduction, merging, extraction, and plotting. | `Makefile`; `generation/submit/runCondorJob.sh`; `analysis/run_status_analysis.sh`; `merging/merge_root_files.sh`; `extraction/pipeline/tune_chain.sh`; `plotting/run_paper_plots.sh` |
| Verification and expected outputs | State the commands, verdict lines, output locations, and acceptance conditions for a successful rebuild. | `tools/run_tests.sh`; validators in `Validation/`; closure receipts; result writers in `extraction/` |
| Known limits and incomplete work | Separate generator-level limits, missing portable runtime support, incomplete S4, and non-regenerable legacy outputs. | Source-code selections; `config/systematics_variations_v1.json`; measured records assigned below |
| Data availability, citation, and license | State what ships, what remains external, how it can be obtained, and how the release must be cited and licensed. | Git tree and artifact sizes; storage paths in configuration; future archive DOI, `LICENSE`, and `CITATION.cff` |
| Documentation and evidence index | Route each reader question to one spine document or a retained measurement record. | The directed set; evidence directories; content map in this plan |

### `docs/PHYSICS.md`

| Section | What it must establish | Direct sources |
|---|---|---|
| Scientific question and scope | Define the heavy-flavour balancing-partner question and limit every claim to generator-level proton-proton events. | Pair registry; producer event record; published figure and result artifacts |
| Collision system and PYTHIA comparison | State the energy, PYTHIA version, hard-process selection, and exact role of each tune. | `config/dependencies.conf`; nominal tune cards; `config/tune_difference_allowlist_v1.json` |
| Heavy-flavour signs, species, and roles | Explain signed heavy-quark content, sector assignment, trigger choice, associate choice, and charge conjugation. | `generation/producer/HeavyFlavourUtils.h`; `AnalysisScripts/species_ordinals_v2.json`; `config/heavy_flavour_species_v1.json`; pair-registry definition |
| Event and pair selection | Establish hard-origin requirements, uniqueness, status rules, transverse-momentum cuts, and role-dependent acceptance. | `generation/producer/HeavyFlavourUtils.h`; producer; reduction macro; pair registry |
| Balancing-yield observable | Give the opposite-sign minus same-sign yield per trigger and distinguish angular, integrated, and ratio forms. | Reduction histograms; plotter normalization code; `extraction/combine_derived.py` |
| Event activity and multiplicity classes | Define the charged-particle counter, eleven absolute class boundaries, class direction, and MONASH minimum-bias labels. | `config/multiplicity_class_boundaries_v1.json`; producer counter; `AnalysisScripts/anchors/b4_multiplicity_mb/` |
| Structural and experiment-comparable decompositions | Define the category partition and the branching-ratio-weighted ground-state view without treating the latter as a partition. | `AnalysisScripts/species_ordinals_v2.json`; `AnalysisScripts/AssociateOriginCategoryContract.h`; `extraction/apply_decay_map.py` |
| Decay maps and ground-state mapping | Explain v1.1 charge conjugation, v2 branching splits, unmapped states, and the map used by published results. | `AnalysisScripts/decay_parent_map_v1_1.json`; `AnalysisScripts/decay_parent_map_v2.json`; map builders and checks |
| Interpretation of tune differences | State what a full-configuration comparison can establish and what it cannot attribute to one PYTHIA switch. | Tune cards; allowlist; M2 source inspection; final tune-separation artifacts |
| Physics limitations and literature context | Place the observable beside prior balance-function and junction studies, then state selection and detector limitations. | Primary papers keyed in `Literature/References.bib`; producer and reduction selections; result artifacts |

### `docs/PIPELINE.md`

| Section | What it must establish | Direct sources |
|---|---|---|
| Dataflow and sources of truth | Show the five stages, their input and output schemas, and the authoritative artifact at every boundary. | Stage entrypoints; schema fields; generated contracts; dataset selector |
| Configuration and generated registries | Explain editable definitions, generated headers, embedded digests, and drift checks. | `config/*.json`; generated headers; `tools/generate_registry_artifacts.py`; registry tests |
| Event generation and raw schema | Describe producer initialization, event acceptance, heavy-particle vectors, metadata, and raw-file naming. | Producer source; `generation/producer/Makefile`; nominal tune cards |
| Campaign rendering, seeds, and attempts | Define campaign ordinals, deterministic seeds, release, retry attempts, and attempt metadata. | `tools/campaign.py`; `tools/render_production_submit.py`; `tools/resubmit_held.py`; worker script |
| Raw validation and canonical manifests | Establish raw validation, receipts, ordered inputs, and the ban on directory discovery for publication work. | `Validation/validate_raw_output.sh`; `tools/build_canonical_manifest.py`; manifest validators |
| Reduction to pair directories | Explain one-pass reduction, canonical slots, staging, validation, and atomic promotion. | `analysis/status_analysis_THnSparse_qq.C`; `analysis/run_status_analysis.sh`; pair-directory validator |
| Merging centrals and blocks | Define thirty-three merge legs, block assignment, object-aware merging, resumability, and closure inputs. | `merging/merge_root_files.sh`; merge macros; pair-object contract |
| Extraction and result products | Trace merged products into per-species, per-category, per-class, and three-tune artifacts. | `extraction/pipeline/tune_chain.sh`; extraction scripts; committed CSV and JSON products |
| Systematic variation processing | Show how one changed card setting becomes a signed dataset, common render, delta, and combined result. | Variation registry; variation cards; harvest configurations; extraction systematics scripts |
| Plotting and figure production | Separate ROOT diagnostic plots from deterministic paper SVG generation and name their input contracts. | `plotting/run_paper_plots.sh`; ROOT macros; plotting configurations; `plotting/paper/` |
| Promotion, failure, and schema evolution | State fail-closed promotion, version negotiation, receipt checks, and the rules for adding a schema or tune. | Validators; `config/pair_file_object_contract_v1.json`; selector checks; negative tests |

### `docs/STATISTICS.md`

| Section | What it must establish | Direct sources |
|---|---|---|
| Quantities and units | List the count, fraction, yield, ratio, relative delta, and absolute-difference quantities with their units. | Extraction and plotting outputs; `extraction/systematics_delta.py`; result JSON schemas |
| Pooled central estimators | Establish that central values come from pooled counts and not from the mean of block ratios. | Plotter aggregation; `extraction/decompose_with_block_sems.py`; integrated-yield artifacts |
| Ten-block uncertainty design | Define block construction, sample standard deviation, standard error, and nine degrees of freedom. | Merge block rule; extraction statistics code; block manifests |
| Nonlinear observables and covariance | Explain why yields, ratios, and integrated values form inside each block before their standard error. | Plotter uncertainty matrix; `extraction/combine_per_class.py`; block-level result artifacts |
| Differences between independent campaigns | Define uncertainty propagation for tune differences and independently generated variations. | `extraction/combine_derived.py`; `extraction/ratio_trend.py`; `extraction/write_verdict.py` |
| Systematic delta estimators | Define the registered per-block relative delta and identify the means-first form as a cross-check. | `extraction/systematics_delta.py`; systematics result JSON |
| Sparse classes and coverage rules | Define zero-yield handling, undefined denominators, LOW-STAT, finite-block requirements, and refusal conditions. | Plotter coverage logic; statistical tests; systematics pre-registration artifacts |
| Trend summaries and fit diagnostics | Define endpoint contrasts, weighted slopes, chi-square diagnostics, and the direction from `c1` to `c11`. | `extraction/ratio_trend.py`; `ratio_trend.json`; multiplicity boundary artifact |
| Closure and integrity checks | Separate exact accounting checks, plausibility checks, and statistical uncertainty. | Closure scripts; `extraction/compare_subset_parent.py`; closure and integrity receipts |
| Combination, reporting, and inferential limits | Define quadrature, correlated-source choices, total uncertainty, rounding, and the limited meaning of quoted sigma values. | `extraction/systematics_delta.py`; `extraction/combine_derived.py`; final verdict JSON; gap work below |

### `docs/SYSTEMATICS.md`

| Section | What it must establish | Direct sources |
|---|---|---|
| Scope, status, and notation | Give the six registered sources, their current status, their axes, and the distinction between delta and uncertainty. | `config/systematics_variations_v1.json`; final systematics JSON; S4 receipts |
| Common variation and control design | Define one-setting changes, sample sizes, nominal reproduction, block estimators, and positive checks. | Variation cards; selector rows; harvest tools; control logs |
| S1: renormalization and factorization scales | State both scale pairs, arm selection, measured shifts, and the observed factorization-scale shape. | Variation registry; seven-campaign delta artifacts; final-two category table |
| S2: parton distribution | State the CTEQ6L1 comparison, measured size, and correlation rule with factorization scale. | Variation card; final-two results; combination code |
| S3: hard-process threshold | Connect the 1 and 4 GeV variations to the nominal 2 GeV choice and report their effect. | Threshold scan; variation cards; per-class and per-category deltas |
| S4: event-activity counter window | State the registered wide-counter design, completed control, missing final measurement, and publication consequence. | Wide-counter configuration; stage-one receipts; pending stages and gap below |
| S5: decay-daughter class migration | Explain the counter-policy variation, the measured structural zero, and its limited scope. | Counter code; decay-policy measurement; nominal and variation comparison |
| S6: pair-level unresolved origin | State the permissive-origin variations, tie-break dependence, multiplicity shape, and separate axis. | A2 configuration, regression sentinels, A2 result records |
| Source selection and combination | Define larger-arm selection, `max(abs(delta), SEM)`, the S1b/S2 choice, quadrature, and S6 exclusion. | `extraction/systematics_delta.py`; `extraction/combine_per_class.py`; combination JSON |
| Effect on tune separations and trend | Compute systematics on differences before comparing them with nominal tune separations. | `extraction/write_verdict.py`; `verdict.json`; final verdict tables |
| Coverage limits and evidence index | State incomplete sources, untested correlation assumptions, and the retained evidence for every source. | Evidence directories listed in Part 2; final result artifacts; gap work below |

### `docs/RESULTS.md`

| Section | What it must establish | Direct sources |
|---|---|---|
| Scope and claim hierarchy | Separate central results, uncertainty-qualified claims, validation results, advisory findings, and incomplete work. | Authorized selector row; final tables; validation records; systematics status artifacts |
| Three-tune species decomposition | Summarize structural and experiment-comparable decompositions on one common row set. | Deduplicated central and block CSV files; `extraction/three_tune_table.py` |
| Multiplicity-integrated balancing yields | Report the integrated beauty and charm yields with block standard errors and exact closure. | Integrated plotting logs; integrated configuration; integrated result record |
| Multiplicity dependence of balancing yields | Report the class-resolved yields that underlie the paper comparisons. | Nominal uncertainty-matrix log; class-axis harvester output; paper figures |
| Baryon-to-meson ratio trend | Lead with the endpoint contrast, then give the slope only as a diagnostic summary. | `ratio_trend.json`; `extraction/ratio_trend.py`; boundary artifact |
| Tune separations | Report MONASH-to-reconnection differences by class for yields and the baryon-to-meson ratio. | `tune_separation.json`; `extraction/write_tune_separation.py` |
| Result after systematic uncertainties | State where separations exceed total uncertainty and where they do not. | `verdict.json`; combined systematics JSON; `extraction/write_verdict.py` |
| Auxiliary validation results | Summarize species-axis checks, map corrections, unresolved-origin diagnostics, Sigma-b ordering, and virtual-trigger closure. | Retained measurement records and their committed anchors |
| Published figures and machine-readable tables | Index each final figure to its input table, generator, receipt, and machine-readable result. | `plotting/paper/`; plotting receipts; result JSON and CSV files |
| Limits on interpretation | State generator-only scope, incomplete S4, covariance limits, advisory boundaries, and non-attribution to one tune switch. | Code selections; systematic gaps; final evidence records |

### `docs/REPRODUCIBILITY.md`

| Section | What it must establish | Direct sources |
|---|---|---|
| What reproducible means here | Define source, configuration, data, result, and figure reproducibility as separate claims. | Git tree; dataset selector; anchors; golden outputs; plotting receipts |
| Runtime and build inputs | State dependency versions, digest pins, environment checks, local overrides, and missing portable bootstrap. | Dependency configuration; setup scripts; producer build; runtime verdict |
| Fixed scientific contracts | Inventory species, pair, schema, multiplicity, tune, and variation contracts with their generators. | `config/*.json`; generated headers; contract tests |
| Dataset identity and campaign provenance | Bind published results to campaign, manifest, schema, authorization, and selector status. | Dataset selector row; canonical manifest; authorization receipt; campaign record |
| Seeds, attempts, and discard accounting | Explain deterministic seeds, retry seeds, held jobs, success counting, and discard-bias bounds. | Campaign tools; seed ledger; attempt metadata; campaign measurement record |
| Anchors, golden outputs, and digests | Explain which committed outputs anchor claims, what each digest means, and what can regenerate each artifact. | `AnalysisScripts/anchors/`; golden-output recipes; digest tests |
| Reproduce from committed evidence | Give ordered commands that need no new generation and state their expected comparisons. | Map builders; extraction scripts; systematics writers; paper figure generator |
| Regenerate the full chain | Give the safe campaign-to-figure path, resource scale, site assumptions, and stop conditions. | Make targets; stage entrypoints; campaign and merge measurements |
| Gates, receipts, and expected verdicts | Name each validation boundary, receipt schema, pass line, and failure interpretation. | Validators; pair-object contract; closure verdicts; plotting receipts |
| Storage and data availability | State committed versus external data, sizes, retention, access method, and archive identity. | Tracked artifacts; measured storage inventory; future public archive metadata |
| Known irreproducibility and recovery boundaries | Name missing legacy inputs, non-portable dependencies, unrecoverable tables, and acceptable substitutes. | A9 assessment; golden-output limits; workspace measurements; gap work below |

### `docs/COMPONENTS.md`

| Section | What it must establish | Direct sources |
|---|---|---|
| How to read the catalog | Define entrypoint, library, generator, validator, diagnostic, and generated-artifact roles. | Call graph from drivers, imports, build files, and tests |
| Generation components | Catalog producer code, registries, tune cards, local runner, worker, and submit renderer. | `generation/`; Make targets; callers and outputs |
| Reduction components | Catalog the one-pass macro, wrapper, A2 measurement path, and auxiliary kinematic reduction. | `analysis/`; submit wrapper; validators |
| Merging components | Catalog object mergers, merge driver, block builder, and their schemas. | `merging/`; pair-object contract; invocation sites |
| Extraction and statistics components | Catalog every extraction, mapping, systematics, trend, and result writer with inputs and outputs. | `extraction/`; imports; tests; generated artifacts |
| Plotting components | Catalog ROOT macros, shared headers, configurations, deterministic SVG code, and receipt tools. | `plotting/`; runner; configuration references |
| Validation components | Catalog automated, measured-manual, and available-unrun validators without overstating coverage. | `Validation/`; driver invocations; retained receipts |
| Contracts, registries, and generated files | Link editable definitions to generated consumers and drift tests. | `config/`; `AnalysisScripts/`; `generation/registries/`; generators |
| Campaign and environment tools | Catalog rendering, seeds, status, retry, environment, deployment, and progress tools. | `tools/`; Makefile; shell callers; tests |
| Tests and enforced contracts | Group tests by scientific or pipeline invariant rather than listing unexplained filenames. | `tools/run_tests.sh`; `tests/test_*`; targeted source files |
| Diagnostic and non-entrypoint components | Identify retained PUBLIC diagnostics and state why no published result invokes them. | Call graph; audit classifications; diagnostic outputs |
| Entrypoint index | Give one command-oriented index from common task to authoritative executable. | Makefile and the six stage drivers |

### `docs/TERMS.md`

`TERMS.md` is already written. Keep its current structure and change it only
when an identifier or a directed spine section requires a new ruling.

| Section | What it must establish | Direct sources |
|---|---|---|
| The direction of multiplicity classes | Fix `c1` as lowest activity and `c11` as highest, while percentile labels run oppositely. | Boundary artifact; histogram names; class-label generator |
| The canonical term registry | Give one name and one meaning for every term that has drifted. | Field names, schema tags, filenames, and executable identifiers |
| Identifier-fixed disagreements | Preserve deliberate differences such as block versus subsample directory and mixed spelling rules. | Code identifiers and configuration keys |
| Distinct terms that look synonymous | Distinguish partner, variant, arm, leg, and consistency check where measurement shows separate meanings. | Repository-wide occurrence audit; named identifiers |

## 2. Complete content map

The denominator is every tracked `.md` path whose audit class is PUBLIC. It has
78 members at commit `42930d6`.

The map uses one primary destination. A row can cite other spine sections, but
the named destination owns the rewrite decision.

<!-- CONTENT_MAP_BEGIN -->
| Current PUBLIC document | Disposition | Spine destination | Treatment |
|---|---|---|---|
| `ARCHITECTURE.md` | ABSORB — PROCESS PROSE | `README.md` — End-to-end reproduction | Preserve the accessible five-stage explanation; move detailed mechanics to `PIPELINE.md`. |
| `AnalysisScripts/anchors/MANIFEST.md` | KEEP — MACHINERY | `docs/REPRODUCIBILITY.md` — Anchors, golden outputs, and digests | Keep its identity because the golden-output contract points to this internal anchor index and its provenance gaps. |
| `AnalysisScripts/anchors/b4_multiplicity_mb/MANIFEST.md` | KEEP — MACHINERY | `docs/PHYSICS.md` — Event activity and multiplicity classes | Keep it beside the named multiplicity anchor because the recomputation receipt and bin-centre warning qualify those bytes. |
| `AnalysisScripts/anchors/closure_v3_verdicts/MANIFEST.md` | KEEP — MACHINERY | `docs/REPRODUCIBILITY.md` — Gates, receipts, and expected verdicts | Keep it beside the contracted verdict anchors because it fixes their waiter provenance and registered counts. |
| `AnalysisScripts/anchors/e5fix_drivers/MANIFEST.md` | KEEP — MACHINERY | `docs/PIPELINE.md` — Extraction and result products | Keep it because the exact anchored drivers, rather than a prose summary, identify the deduplicated extraction inputs. |
| `AnalysisScripts/anchors/extraction_dual/MANIFEST.md` | KEEP — MACHINERY | `docs/REPRODUCIBILITY.md` — Anchors, golden outputs, and digests | Keep it with the old named anchor because its quarantine status and missing provenance determine whether those bytes may be used. |
| `AnalysisScripts/anchors/merged_closepacking_dedup/MANIFEST.md` | KEEP — MACHINERY | `docs/RESULTS.md` — Three-tune species decomposition | Keep it beside the contracted CLOSEPACKING product because it binds values, integrity flags, closure, and regeneration details to that anchor. |
| `AnalysisScripts/anchors/merged_junctions_dedup/MANIFEST.md` | KEEP — MACHINERY | `docs/RESULTS.md` — Three-tune species decomposition | Keep it beside the contracted JUNCTIONS product because it binds values, integrity flags, closure, and regeneration details to that anchor. |
| `AnalysisScripts/anchors/merged_monash_dedup/MANIFEST.md` | KEEP — MACHINERY | `docs/RESULTS.md` — Three-tune species decomposition | Keep it beside the contracted MONASH product because it binds the E5 correction and integrity data to that anchor. |
| `README.md` | SPINE | `README.md` — all sections | Rebuild in place as the comprehensive front door. |
| `REPRODUCIBILITY.md` | SPINE | `docs/REPRODUCIBILITY.md` — all sections | Move to `docs/` and rebuild from contracts, tools, and receipts. |
| `STATE.md` | DROP | None | Drop transient branch state; derive any durable result from its assigned evidence instead. |
| `ValidationReports/NCH_CALIBRATION_20260730.md` | ABSORB — PROCESS PROSE | `docs/PHYSICS.md` — Event activity and multiplicity classes | Preserve the superseded 8.315 calibration only as provenance for why the published-version calibration replaced it. |
| `ValidationReports/NCH_CALIBRATION_PYTHIA8317_20260801.md` | ABSORB — PROCESS PROSE | `docs/PHYSICS.md` — Event activity and multiplicity classes | Preserve the published-version calibration values, method, and resulting class-boundary claim. |
| `ValidationReports/NCH_DECAY_POLICY_BIAS_8317.md` | ABSORB — PROCESS PROSE | `docs/SYSTEMATICS.md` — S5: decay-daughter class migration | Preserve the paired-counter measurement, null result, and limits without retaining the after-the-fact report. |
| `ValidationReports/PTHAT_MULTIPLICITY_SCAN_8317.md` | ABSORB — PROCESS PROSE | `docs/SYSTEMATICS.md` — S3: hard-process threshold | Preserve the scan values, method, and decision point without retaining the after-the-fact report. |
| `ValidationReports/PYTHIA_JUNCTION_HANG_20260731.md` | ABSORB — PROCESS PROSE | `docs/REPRODUCIBILITY.md` — Seeds, attempts, and discard accounting | Preserve the measured wedge evidence and bounded-retry rationale; its date does not confer a separate evidentiary role. |
| `analysis/Analysis_README.md` | ABSORB — PROCESS PROSE | `docs/PIPELINE.md` — Reduction to pair directories | Preserve input contracts, canonical slots, promotion, blocks, and estimator links. |
| `docs/A2_PAIR_UNRESOLVED_PREREGISTRATION.md` | KEEP — DATED EVIDENCE | `docs/SYSTEMATICS.md` — S6: pair-level unresolved origin | Keep its committed-before-results identity; absorption would destroy evidence that the variation, thresholds, and positive checks were fixed in advance. |
| `docs/A2_PAIR_UNRESOLVED_RUN_RECORD.md` | KEEP — DATED EVIDENCE | `docs/SYSTEMATICS.md` — S6: pair-level unresolved origin | Keep the paired run record because its chronology ties provenance failures, executed variations, and checks to that registration. |
| `docs/A9_PAPER_TABLE_REGENERATION.md` | ABSORB — PROCESS PROSE | `docs/REPRODUCIBILITY.md` — Known irreproducibility and recovery boundaries | Preserve why the legacy table cannot be rebuilt from current inputs. |
| `docs/B_BARYON_ADVISORY_DIAGNOSTIC.md` | ABSORB — PROCESS PROSE | `docs/RESULTS.md` — Auxiliary validation results | Preserve the diagnostic ladder, corrected values, and advisory scope; it is an after-the-fact measurement, not a separately dated contract. |
| `docs/CLOSURE_V3_PREREGISTRATION.md` | KEEP — DATED EVIDENCE | `docs/REPRODUCIBILITY.md` — Gates, receipts, and expected verdicts | Keep its pre-run identity because the closure counts and failure condition derive value from having been fixed before the verdicts. |
| `docs/COMPONENTS.md` | SPINE | `docs/COMPONENTS.md` — all sections | Rebuild the catalog against current callers and PUBLIC components. |
| `docs/DESIGN_AND_RATIONALE.md` | ABSORB — PROCESS PROSE | `docs/PHYSICS.md` — all sections | Preserve implemented physics choices; remove session history and superseded decisions. |
| `docs/EXTRACTION_CONVENTIONS.md` | ABSORB — PROCESS PROSE | `docs/PHYSICS.md` — Structural and experiment-comparable decompositions | Preserve definitions and invariants; leave superseded numeric tables in evidence. |
| `docs/F3_VIRTUAL_TRIGGER_CLOSURE.md` | ABSORB — PROCESS PROSE | `docs/RESULTS.md` — Auxiliary validation results | Preserve the exact closure, table values, and scope limits; the combined setup-and-result write-up has no independent machinery or dated-record role. |
| `docs/FIGURE_INVENTORY.md` | ABSORB — PROCESS PROSE | `docs/RESULTS.md` — Published figures and machine-readable tables | Preserve final dispositions and provenance; drop the chronological deliberation. |
| `docs/GATE_3000.md` | ABSORB — PROCESS PROSE | `docs/REPRODUCIBILITY.md` — Gates, receipts, and expected verdicts | Preserve the gate definition, harvest result, resource observations, and corrections; the combined process narrative does not retain pre-registration value as a separate record. |
| `docs/GOLDEN_OUTPUTS.md` | KEEP — MACHINERY | `docs/REPRODUCIBILITY.md` — Anchors, golden outputs, and digests | Keep its exact path and identity because it is the digest registry and recipe contract for named artifacts, including non-regenerable items. |
| `docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md` | KEEP — DATED EVIDENCE | `docs/REPRODUCIBILITY.md` — Dataset identity and campaign provenance | Keep the signed authorization because its dated identity fixes the publication boundary and exclusions and is named by dataset selectors. |
| `docs/M2_PROBQQ1TOQQ0JOIN.md` | ABSORB — PROCESS PROSE | `docs/PHYSICS.md` — Interpretation of tune differences | Preserve the source-derived parameter meaning and its interpretive limit. |
| `docs/M7_BEAUTY_PREREGISTRATION.md` | KEEP — DATED EVIDENCE | `docs/RESULTS.md` — Auxiliary validation results | Keep its committed-before-run identity because it proves the beauty measurement design and checks preceded the result. |
| `docs/M7_BEAUTY_UNRESOLVED_SYSTEMATIC.md` | ABSORB — PROCESS PROSE | `docs/RESULTS.md` — Auxiliary validation results | Preserve the measured beauty table and inclusive-level scope; this is the after-the-fact result paired with the retained pre-registration. |
| `docs/M7_UNRESOLVED_SYSTEMATIC.md` | ABSORB — PROCESS PROSE | `docs/RESULTS.md` — Auxiliary validation results | Preserve the measured charm table and inclusive-level scope; its separateness carries no additional contract or chronology. |
| `docs/MAP_V1_1_PREREGISTRATION.md` | KEEP — DATED EVIDENCE | `docs/PHYSICS.md` — Decay maps and ground-state mapping | Keep its committed-before-builder-change identity because it proves the predicted diff and fail-closed checks were fixed in advance. |
| `docs/MAP_V1_CONJUGATION_BUG.md` | ABSORB — PROCESS PROSE | `docs/PHYSICS.md` — Decay maps and ground-state mapping | Preserve the arithmetic proof, impact boundary, and supersession ruling; this retrospective bug account has no continuing separate contract. |
| `docs/MAP_V2_PREREGISTRATION.md` | KEEP — DATED EVIDENCE | `docs/PHYSICS.md` — Decay maps and ground-state mapping | Keep its pre-probe identity because it fixes branching splits, thresholds, and mandatory checks before the v2 result. |
| `docs/MAP_V2_RESULT.md` | ABSORB — PROCESS PROSE | `docs/RESULTS.md` — Auxiliary validation results | Preserve the measured residual, exact splits, and scorecard; this is the after-the-fact result paired with the retained registration. |
| `docs/MONASH_CENTRAL_TABLE.md` | ABSORB — PROCESS PROSE | `docs/RESULTS.md` — Three-tune species decomposition | Preserve the corrected MONASH values, closure, integrity, and provenance in the consolidated three-tune result. |
| `docs/PER_TUNE_PROCESSING_PREREGISTRATION.md` | KEEP — DATED EVIDENCE | `docs/STATISTICS.md` — Ten-block uncertainty design | Keep its committed-before-other-tunes identity because it proves the common estimator and checks were fixed before processing. |
| `docs/PRODUCTION_SHAPE_DECISION.md` | KEEP — MACHINERY | `docs/PHYSICS.md` — Event activity and multiplicity classes | Keep its exact path because `config/multiplicity_class_boundaries_v1.json` names it in `ruling`, and that configuration is pinned by three receipts. |
| `docs/PROGRESS_PROBE_METHOD.md` | ABSORB — PROCESS PROSE | `docs/REPRODUCIBILITY.md` — Regenerate the full chain | Preserve validated liveness rules and remove session-specific corrections. |
| `docs/REGISTRY_AND_MAPPING_PROPOSAL.md` | ABSORB — PROCESS PROSE | `docs/PHYSICS.md` — Heavy-flavour signs, species, and roles | Preserve implemented registry and mapping rules; drop rejected options and open design history. |
| `docs/SCALING_V3_MEASUREMENT.md` | ABSORB — PROCESS PROSE | `docs/REPRODUCIBILITY.md` — Gates, receipts, and expected verdicts | Preserve the measured scaling points, gate implication, and resource bounds; the combined registration-and-harvest narrative is process prose. |
| `docs/SECOND_BRANCH_WEIGHT.md` | ABSORB — PROCESS PROSE | `docs/PHYSICS.md` — Decay maps and ground-state mapping | Preserve both definitions, affected species, measured bound, and chosen invocation; the post hoc ruling needs no separate identity. |
| `docs/SIGMA_B_ORDERING_AND_ADJUDICATION.md` | ABSORB — PROCESS PROSE | `docs/RESULTS.md` — Auxiliary validation results | Preserve the retraction, raw-count ordering, and final ten-block values; the adjudication is an after-the-fact decision. |
| `docs/SPECIES_AXIS_VALIDATION.md` | ABSORB — PROCESS PROSE | `docs/PHYSICS.md` — Heavy-flavour signs, species, and roles | Preserve the all-tune ordinal and tune-independence measurements; their date and separateness add no evidentiary information. |
| `docs/SYSTEMATICS.md` | SPINE | `docs/SYSTEMATICS.md` — all sections | Rebuild in place from variation code and result artifacts. |
| `docs/SYSTEMATICS_HARVEST_RUN_RECORD.md` | KEEP — DATED EVIDENCE | `docs/SYSTEMATICS.md` — Coverage limits and evidence index | Keep the paired run record because its chronology binds command provenance, deviations, and coverage to the retained systematics registration. |
| `docs/SYSTEMATICS_PREREGISTRATION.md` | KEEP — DATED EVIDENCE | `docs/SYSTEMATICS.md` — Common variation and control design | Keep its committed-before-campaign identity because the registered sources, estimators, checks, and combination rulings derive value from precedence. |
| `docs/TERMS.md` | SPINE | `docs/TERMS.md` — all sections | Keep the existing registry and validate future prose against it. |
| `docs/THREE_TUNE_CENTRAL_TABLE.md` | ABSORB — PROCESS PROSE | `docs/RESULTS.md` — Three-tune species decomposition | Preserve the final tables, closure, integrity, advisory, and regeneration provenance in the consolidated result; this post-harvest compilation has no separate contract. |
| `docs/V2_PIN_SWEEP.md` | ABSORB — PROCESS PROSE | `docs/PIPELINE.md` — Promotion, failure, and schema evolution | Preserve version-aware consumers and negative tests; drop migration-session detail. |
| `docs/VALIDATION_INVENTORY.md` | ABSORB — PROCESS PROSE | `docs/COMPONENTS.md` — Validation components | Preserve which validators run, which have measured runs, and which remain unrun. |
| `docs/V_INTEGRATED_PREREGISTRATION.md` | KEEP — DATED EVIDENCE | `docs/RESULTS.md` — Multiplicity-integrated balancing yields | Keep the document because its registered estimator predates the appended result; splitting or absorbing it would destroy that chronology. |
| `docs/WORKSPACE.md` | ABSORB — PROCESS PROSE | `docs/REPRODUCIBILITY.md` — Runtime and build inputs | Preserve portable setup, local overrides, site roles, and non-portable limits. |
| `docs/a2_results_20260813/A2_DELTA_RESULT.md` | KEEP — DATED EVIDENCE | `docs/SYSTEMATICS.md` — S6: pair-level unresolved origin | Keep it in the directed dated evidence set because its separate first-result table and supersession warning would be flattened by absorption. |
| `docs/a2_results_20260813/A2_TIEBREAK_ROBUSTNESS.md` | KEEP — DATED EVIDENCE | `docs/SYSTEMATICS.md` — S6: pair-level unresolved origin | Keep it in the directed dated evidence set because its separate robustness table, owner ruling, and limits qualify the A2 measurement. |
| `docs/campaigns/HF_RUN3_V1_RECORD.md` | KEEP — DATED EVIDENCE | `docs/REPRODUCIBILITY.md` — Dataset identity and campaign provenance | Keep this paired campaign run record because its chronology preserves releases, retries, seeds, hangs, recovery, and final closure behind the authorization. |
| `docs/plotting_validation/hf_run3_v1_kinematics_20260817/RUN_RECORD.md` | KEEP — DATED EVIDENCE | `docs/RESULTS.md` — Published figures and machine-readable tables | Keep the dated plotting receipt because its separate identity binds selections, the boundary closed loop, and the energy label to the rendered artifact. |
| `docs/plotting_validation/hf_run3_v1_monash_20260813/RUN_RECORD.md` | KEEP — DATED EVIDENCE | `docs/RESULTS.md` — Published figures and machine-readable tables | Keep the dated plotting receipt because its separate identity binds the first MONASH render command, checks, warning, and figure. |
| `docs/plotting_validation/hf_run3_v1_threetune_20260816/RUN_RECORD.md` | KEEP — DATED EVIDENCE | `docs/RESULTS.md` — Published figures and machine-readable tables | Keep the dated plotting receipt because its separate identity binds the three-tune render, bug finding, guard, and polish decisions. |
| `docs/systematics_results_20260819/PER_CATEGORY_DELTAS.md` | KEEP — DATED EVIDENCE | `docs/SYSTEMATICS.md` — S1 and S3 sections | Keep it in the directed dated evidence set because its separate five-campaign table and unresolved rows are the measurement record. |
| `docs/systematics_results_20260819/PER_CLASS_DELTAS.md` | KEEP — DATED EVIDENCE | `docs/SYSTEMATICS.md` — Effect on tune separations and trend | Keep it in the directed dated evidence set because its integrated and per-class tables preserve the 2026-08-19 measurement state. |
| `docs/systematics_results_20260819/RATIO_TREND.md` | KEEP — DATED EVIDENCE | `docs/RESULTS.md` — Baryon-to-meson ratio trend | Keep it in the directed dated evidence set because the class values, contrasts, and diagnostics form a separate measured table. |
| `docs/systematics_results_20260819/TUNE_SEPARATION.md` | KEEP — DATED EVIDENCE | `docs/RESULTS.md` — Tune separations | Keep it in the directed dated evidence set because its two reconnection-comparison tables are the dated measurement record. |
| `docs/systematics_results_20260820/COMBINED_SYSTEMATICS.md` | KEEP — DATED EVIDENCE | `docs/SYSTEMATICS.md` — Source selection and combination | Keep it in the directed dated evidence set because its source inventory and per-class totals record the final combination separately from interpretation. |
| `docs/systematics_results_20260820/PER_CATEGORY_FINAL_TWO.md` | KEEP — DATED EVIDENCE | `docs/SYSTEMATICS.md` — S1 and S2 sections | Keep it in the directed dated evidence set because its control and final-two source tables preserve the measured inputs to combination. |
| `docs/systematics_results_20260820/PER_CLASS_DELTAS_SEVEN.md` | KEEP — DATED EVIDENCE | `docs/SYSTEMATICS.md` — Effect on tune separations and trend | Keep it in the directed dated evidence set because the seven-campaign tables preserve the final per-class harvest. |
| `docs/systematics_results_20260820/VERDICT.md` | KEEP — DATED EVIDENCE | `docs/RESULTS.md` — Result after systematic uncertainties | Keep it in the directed dated evidence set because its full verdict tables and separation arithmetic are the dated final measurement record. |
| `generation/Simulation_README.md` | ABSORB — PROCESS PROSE | `docs/PIPELINE.md` — Event generation and raw schema | Preserve build, producer interface, contracts, event content, matching, and accounting. |
| `generation/submit/Condor_README.md` | ABSORB — PROCESS PROSE | `docs/REPRODUCIBILITY.md` — Regenerate the full chain | Preserve release, monitoring, hang guard, retry, and storage rules. |
| `plotting/FinalAnalysis/README.md` | ABSORB — PROCESS PROSE | `docs/COMPONENTS.md` — Diagnostic and non-entrypoint components | Preserve inputs, outputs, and practical checks for the two retained macros. |
| `plotting/PAPER_FIGURE_PROVENANCE.md` | ABSORB — PROCESS PROSE | `docs/RESULTS.md` — Published figures and machine-readable tables | Preserve the final figure-to-generator map and uncertainty provenance. |
| `plotting/PtMultiplicity/README.md` | ABSORB — PROCESS PROSE | `docs/COMPONENTS.md` — Diagnostic and non-entrypoint components | Preserve macro families, path resolution, error rules, and combined inputs. |
| `plotting/README.md` | ABSORB — PROCESS PROSE | `docs/PIPELINE.md` — Plotting and figure production | Preserve selector, cut, statistics, style, runner, validation, and output contracts. |
| `plotting/paper/README.md` | ABSORB — PROCESS PROSE | `docs/PIPELINE.md` — Plotting and figure production | Preserve deterministic SVG rationale, final figure list, and mandatory labels. |
<!-- CONTENT_MAP_END -->

### Coverage proof

Define `P` as tracked PUBLIC Markdown from `docs/REPO_AUDIT.csv`. Define `M` as the
first column of the content map. The measured equality is:

| Set measure | Value |
|---|---:|
| `|P|` | 78 |
| `|M|` | 78 |
| `|P - M|` | 0 |
| `|M - P|` | 0 |

Run this proof after any edit to the map:

```bash
python3 - <<'PY'
import csv
import re
import subprocess
from pathlib import Path

tracked = set(subprocess.run(
    ["git", "ls-files"], check=True, capture_output=True, text=True
).stdout.splitlines())
with Path("docs/REPO_AUDIT.csv").open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
public = {
    row["path"] for row in rows
    if row["class"] == "PUBLIC"
    and row["path"].endswith(".md")
    and row["path"] in tracked
}
text = Path("docs/DOC_PLAN.md").read_text(encoding="utf-8")
body = text.split("<!-- CONTENT_MAP_BEGIN -->", 1)[1]
body = body.split("<!-- CONTENT_MAP_END -->", 1)[0]
mapped = set(re.findall(r"^\| `([^`]+\.md)` \|", body, re.MULTILINE))
print(f"PUBLIC={len(public)} MAPPED={len(mapped)}")
print("PUBLIC_MINUS_MAP", sorted(public - mapped))
print("MAP_MINUS_PUBLIC", sorted(mapped - public))
raise SystemExit(0 if public == mapped else 1)
PY
```

### Disposition counts

| Disposition | Count | Meaning |
|---|---:|---|
| absorbed process prose | 37 | Durable substance moves to a named spine section; the current identity carries no unique contract or chronology |
| kept dated evidence | 25 | Twelve pre-registrations, paired run records, or authorizations outside the directed evidence families, plus thirteen dated records inside those families |
| kept machinery | 10 | `GOLDEN_OUTPUTS.md`, `PRODUCTION_SHAPE_DECISION.md`, and eight anchor manifests whose exact paths qualify contracted artifacts |
| current spine files | 5 | Current members of the directed nine-document set |
| dropped | 1 | `STATE.md` |
| later reclassified INTERNAL | 38 | Thirty-seven absorbed files plus the dropped transient file |

This lands on twelve dated records in the top-level record set: eleven direct
`docs/*.md` files plus `docs/campaigns/HF_RUN3_V1_RECORD.md`. The thirteen
additional dated records remain only because the mandate separately preserves
`docs/a2_results_*/`, `docs/plotting_validation/`, and
`docs/systematics_results_*/`. The two top-level machinery documents are also
mandated exceptions, while the other eight machinery documents live beside
anchors. The result is therefore not materially above the target of nine spine
documents plus about a dozen dated records at top level.

No mapped document resists the three categories.

The mixed registration/result files ordered into the spine are process prose:
their identity is neither advance-only nor named by machinery.

`V_INTEGRATED_PREREGISTRATION.md` is the exception because its registered
estimator predates the result appended to that record.

## 3. Reclass list

Do not apply these rulings in this session. Reclass each file only after the
named destination lands and the content-map row passes its check.

| File | Trigger for reclassification |
|---|---|
| `ARCHITECTURE.md` | `README.md` and `docs/PIPELINE.md` carry its accessible architecture. |
| `STATE.md` | The spine derives current status from evidence and no PUBLIC file cites this snapshot. |
| `ValidationReports/NCH_CALIBRATION_20260730.md` | `docs/PHYSICS.md` carries the superseded calibration only as provenance for the published-version result. |
| `ValidationReports/NCH_CALIBRATION_PYTHIA8317_20260801.md` | `docs/PHYSICS.md` carries the published-version calibration and class-boundary claim. |
| `ValidationReports/NCH_DECAY_POLICY_BIAS_8317.md` | `docs/SYSTEMATICS.md` carries the S5 measurement and its limits. |
| `ValidationReports/PTHAT_MULTIPLICITY_SCAN_8317.md` | `docs/SYSTEMATICS.md` carries the S3 scan and decision point. |
| `ValidationReports/PYTHIA_JUNCTION_HANG_20260731.md` | `docs/REPRODUCIBILITY.md` carries the measured wedge and bounded-retry rationale. |
| `analysis/Analysis_README.md` | `docs/PIPELINE.md` owns reduction and block mechanics. |
| `docs/A9_PAPER_TABLE_REGENERATION.md` | `docs/REPRODUCIBILITY.md` states the non-regenerable boundary and evidence. |
| `docs/B_BARYON_ADVISORY_DIAGNOSTIC.md` | `docs/RESULTS.md` carries the diagnostic ladder, corrected values, and advisory scope. |
| `docs/DESIGN_AND_RATIONALE.md` | `docs/PHYSICS.md`, `docs/STATISTICS.md`, and `docs/PIPELINE.md` own all implemented choices. |
| `docs/EXTRACTION_CONVENTIONS.md` | `docs/PHYSICS.md` defines both decomposition conventions from artifacts. |
| `docs/F3_VIRTUAL_TRIGGER_CLOSURE.md` | `docs/RESULTS.md` carries the exact auxiliary closure and its scope. |
| `docs/FIGURE_INVENTORY.md` | `docs/RESULTS.md` indexes only final figures and retained receipts. |
| `docs/GATE_3000.md` | `docs/REPRODUCIBILITY.md` carries the gate, harvest outcome, resource observations, and corrections. |
| `docs/M2_PROBQQ1TOQQ0JOIN.md` | `docs/PHYSICS.md` derives the parameter meaning from pinned PYTHIA source. |
| `docs/M7_BEAUTY_UNRESOLVED_SYSTEMATIC.md` | `docs/RESULTS.md` carries the measured beauty table and its inclusive-level scope. |
| `docs/M7_UNRESOLVED_SYSTEMATIC.md` | `docs/RESULTS.md` carries the measured charm table and its inclusive-level scope. |
| `docs/MAP_V1_CONJUGATION_BUG.md` | `docs/PHYSICS.md` carries the arithmetic proof, impact boundary, and supersession ruling. |
| `docs/MAP_V2_RESULT.md` | `docs/RESULTS.md` carries the measured residual, splits, and scorecard. |
| `docs/MONASH_CENTRAL_TABLE.md` | `docs/RESULTS.md` carries the corrected MONASH values within the three-tune decomposition. |
| `docs/PROGRESS_PROBE_METHOD.md` | `docs/REPRODUCIBILITY.md` carries the validated liveness method. |
| `docs/REGISTRY_AND_MAPPING_PROPOSAL.md` | `docs/PHYSICS.md` and `docs/PIPELINE.md` describe only the implemented design. |
| `docs/SCALING_V3_MEASUREMENT.md` | `docs/REPRODUCIBILITY.md` carries the measured scaling law, gate implication, and resource bounds. |
| `docs/SECOND_BRANCH_WEIGHT.md` | `docs/PHYSICS.md` carries the two definitions, affected species, measured bound, and ruling. |
| `docs/SIGMA_B_ORDERING_AND_ADJUDICATION.md` | `docs/RESULTS.md` carries the retraction, raw-count ordering, and final ten-block values. |
| `docs/SPECIES_AXIS_VALIDATION.md` | `docs/PHYSICS.md` carries the all-tune ordinal and tune-independence measurements. |
| `docs/THREE_TUNE_CENTRAL_TABLE.md` | `docs/RESULTS.md` carries the consolidated final tables, closure, integrity, and advisory. |
| `docs/V2_PIN_SWEEP.md` | `docs/PIPELINE.md` states current schema negotiation and its tests. |
| `docs/VALIDATION_INVENTORY.md` | `docs/COMPONENTS.md` classifies every validator by invocation and evidence. |
| `docs/WORKSPACE.md` | `docs/REPRODUCIBILITY.md` owns setup, site roles, storage, and portability. |
| `generation/Simulation_README.md` | `docs/PIPELINE.md` owns producer mechanics and raw schema. |
| `generation/submit/Condor_README.md` | `docs/REPRODUCIBILITY.md` owns campaign operations and retry rules. |
| `plotting/FinalAnalysis/README.md` | `docs/COMPONENTS.md` records both macros as diagnostics. |
| `plotting/PAPER_FIGURE_PROVENANCE.md` | `docs/RESULTS.md` maps every final figure to code, data, and receipt. |
| `plotting/PtMultiplicity/README.md` | `docs/COMPONENTS.md` records this retained diagnostic family. |
| `plotting/README.md` | `docs/PIPELINE.md` owns the plotting input and output contracts. |
| `plotting/paper/README.md` | `docs/PIPELINE.md` owns deterministic paper-figure generation. |

The 25 dated evidence documents and ten machinery documents do not enter this
list. Later sessions may rewrite their prose, but they remain PUBLIC records
with stable identities.

## 4. Gap list

These gaps have no complete answer in a current document. A writer must not
invent an answer where the required measurement or owner decision is absent.

| Gap | Spine owner | Required resolution |
|---|---|---|
| Public data access and preservation | `README.md` — Data availability, citation, and license; `docs/REPRODUCIBILITY.md` — Storage and data availability | State how an external reader obtains non-committed raw and merged data, how long they persist, and which archive identity fixes them. |
| Software license and citation metadata | `README.md` — Data availability, citation, and license | Add `LICENSE` and `CITATION.cff` later, then link them; neither belongs in the nine-document prose set. |
| Portable PYTHIA build bootstrap | `docs/REPRODUCIBILITY.md` — Runtime and build inputs | Supply a tested build recipe or container for the pinned source, compiler, flags, and patches; until then, state the unsupported boundary. |
| Final S4 wide-counter measurement | `docs/SYSTEMATICS.md` — S4: event-activity counter window; `docs/RESULTS.md` — Result after systematic uncertainties | Complete the declared subset analysis and delta harvest, or state that the final uncertainty excludes S4. |
| Cross-class and cross-observable covariance | `docs/STATISTICS.md` — Nonlinear observables and covariance; `docs/RESULTS.md` — Scope and claim hierarchy | This is a physics limitation. A writer may not invent covariance: measure or bound it, or state plainly that cross-class and cross-observable covariance is unknown and limits endpoint contrasts and combined plots. |
| Inferential status and multiple comparisons | `docs/STATISTICS.md` — Combination, reporting, and inferential limits; `docs/RESULTS.md` — Scope and claim hierarchy | This is a physics limitation. Unless a correction is computed, both sections must state that quoted sigma values are per-cell and uncorrected across 72 comparisons; a writer may not invent a global significance or trial correction. |
| Systematic-source correlation sensitivity | `docs/SYSTEMATICS.md` — Source selection and combination | This is a physics limitation. A writer may not invent source independence: test alternatives to quadrature beyond the S1b/S2 rule, or name the unmeasured correlation sensitivity and the quadrature assumption explicitly. |

## Writing order

1. **`docs/TERMS.md`** stays first because every later writer uses its names and
   class direction.

2. **`docs/PHYSICS.md`** comes next because it fixes the observable, selection,
   tune scope, and decomposition meanings.

3. **`docs/STATISTICS.md`** follows because results and systematics must cite one
   estimator and uncertainty contract.

4. **`docs/PIPELINE.md`** then connects those scientific contracts to actual
   schemas, stages, and artifacts.

5. **`docs/COMPONENTS.md`** follows the pipeline so its catalog uses stable stage
   names and does not redefine architecture.

6. **`docs/SYSTEMATICS.md`** comes after physics, statistics, and pipeline because
   it depends on all three.

7. **`docs/RESULTS.md`** follows systematics so every headline has a final scope
   and uncertainty status.

8. **`docs/REPRODUCIBILITY.md`** then binds the settled methods and results to
   commands, anchors, receipts, and known limits.

9. **`README.md`** is last because it summarizes and links every other spine
   document without creating new authority.

## Hardest placements

| Document | Why placement was difficult | Ruling |
|---|---|---|
| `docs/GOLDEN_OUTPUTS.md` | It mixes artifact contracts, result tables, figure history, correction records, and non-regenerable limits. | Keep it as machinery because it is the digest registry; `docs/REPRODUCIBILITY.md` owns the contract explanation. |
| `docs/SYSTEMATICS_HARVEST_RUN_RECORD.md` | It interleaves commands, concurrency incidents, tool defects, intermediate results, final results, and an unfinished S4 handoff. | Retain the run record; `docs/SYSTEMATICS.md` owns method and interpretation. |
| `docs/PRODUCTION_SHAPE_DECISION.md` | It combines campaign shape, beauty statistics, class-boundary measurements, and the binding event-activity ruling. | Keep it as machinery because the boundary configuration names it and three receipts pin that configuration; `docs/PHYSICS.md` owns the final scientific design. |
