# Configuration

[Documentation index](../README.md#documentation)

## Configuration authority

| File | Consumer and role | Change policy |
| --- | --- | --- |
| [analysis.json](../config/analysis.json) | Query construction and numerical reduction | Change supported profiles or percentiles in a separately hashed copy |
| [query.json](../config/query.json) | Query builder, verifier and collection reader | Fixed schema, not a free-form layout selector |
| [plot.json](../config/plot.json) | Default renderer presentation | Change only supported display fields |
| [plot-dplus.json](../config/plot-dplus.json) | D+ presentation | Pair with `reduce run --charm-trigger 411` |
| [plot-all-tune.json](../config/plot-all-tune.json) | All-tune correlation presentation | Same default D0 scientific recipe |
| [study.json](../config/study.json) | Raw compatibility, generated C++ registry and source checks | Keep exact checksum-bound bytes for accepted inputs |
| [campaign.json](../data/campaign.json) | Generation inventory, analysis planning and accounting | Keep accepted source identities and exposure fixed |
| [site.example.conf](../config/site.example.conf) | Template for untracked `config/site.conf` | Set paths for the intended machine |
| [Tune cards](../config/tunes) | PYTHIA producer and raw validators | Treat each card as one complete fixed bundle |

Configuration validation checks exact keys in scientific contracts. Unknown keys are not an extension mechanism. A changed hash can invalidate query compatibility, input acceptance or a prepared build pack.

The tables below distinguish user choices from fixed metadata. A fixed field has no independent user-adjustable default. Its shipped value belongs to the linked contract. Long registries and descriptor text remain in that exact source instead of a second editable copy.

## Analysis choices

| Choice | Type, units and default | Constraints and effect |
| --- | --- | --- |
| `profiles` | Array, default one `inclusive` profile | 1–16 entries. Inclusive must be first. Changes pair and trigger selection during reduction. |
| `profiles[].id` | String, default `inclusive` | Unique `[a-z][a-z0-9_]{0,63}` identifier. The first profile must be `inclusive`. |
| `profiles[].trigger_pt` | Null or object, GeV/c, default null | Inclusive uses null. A rectangle requires `operator: ">="` and a finite nonnegative `value`. Its minimum must be at least the associate minimum. |
| `profiles[].associate_pt` | Null or object, GeV/c, default null | Inclusive uses null. A rectangle requires `operator: ">="` and a finite nonnegative `value`. Both rectangle cuts must be present. |
| `profiles[].relative_pt` | Null, fixed | Non-null values fail. This model has no event-wise diagonal pT cut. |
| `percentile_intervals` | Array of integer pairs, percent | Default 0–1, 1–10, then ten-percent intervals through 100. Must partition 0–100 in order without gaps. |
| `integrated_interval` | Integer pair `[0,100]`, fixed | Defines the full-activity class. |
| CLI `--profile-id` | String, default `inclusive` | Selects one named profile in the numerical request. |
| CLI `--activity-id` | String, default first nominal activity | Selects one of the two fixed activity definitions. |
| CLI `--reference-tune` | String, default `MONASH` | Changes comparison denominators and shared-reference covariance. |
| CLI `--charm-trigger` | Integer, default 421 | Accepts 421 or 411. Changes correlated charm references and signed-spectrum species coherently. |
| CLI `--tunes` | List of tune strings, default collection domain | Full research reduction requires the complete three-tune domain. |

Both rectangle minima must be exact regular-bin lower edges in the query pT axis. Do not select 7000 as a lower edge because it is the final upper edge. Overflow above that edge remains included.

This JSON value can replace `profiles` in a copy of `analysis.json`:

```json
[
  {"id":"inclusive","trigger_pt":null,"associate_pt":null,"relative_pt":null},
  {"id":"pt_1_0p15","trigger_pt":{"operator":">=","value":1.0},
   "associate_pt":{"operator":">=","value":0.15},"relative_pt":null},
  {"id":"pt_2p5_0p5","trigger_pt":{"operator":">=","value":2.5},
   "associate_pt":{"operator":">=","value":0.5},"relative_pt":null}
]
```

The unchanged query can support all three profiles. Post-construction compatibility permits changes only to `profiles` and `percentile_intervals`. The charm CLI derives its coherent recipe separately. Other scientific changes need a new compatible data construction and source review.

Class changes affect boundaries, deletions, covariance, labels and plots. The renderer has eleven noninclusive line patterns. A numerical partition beyond its display capacity does not automatically yield readable paper pages. The paper renderer accepts inclusive and supported rectangular profiles. It reads each selection from the numerical archive.

### Fixed analysis fields

| Field group | Meaning and consumer |
| --- | --- |
| `schema`, `version` | Downstream request contract. Public numerical reduction requires version 2.2.0. |
| `paper_defaults` | Charm choice, selectable identities and signed baryon/reference tuple |
| `base_study`, `lossless_input` | Exact raw-study, analyzed-schema and structural-registry SHA-256 bindings |
| `axes` | Sparse coordinates and numerical output domains |
| `pair_acceptance` | Ordered pair roles, inclusive eta acceptance and azimuth sign |
| `activities` | Physical fields and exact charged-light predicates |
| `activity_policy` | Weighted percentile threshold, tie and deletion rules |
| `pair_query_registry` | Signed triggers, associates and reference-meson identities |
| `correlations` | Configured identified-pair channels and OS/SS components |
| `projection_recipes` | Required scientific capabilities, including origin and closure information |
| `g9_species_pdgs` | Signed heavy-hadron spectrum identities. The literal key names that spectrum domain. |
| `estimator_policy` | Pooled center, ten-block jackknife, denominator resolution and status rules |
| `compact_domain_registries`, `compact_storage` | Bound compatibility descriptors. They do not select another production science engine. |

The nominal activity ID is `charged_light_sector_activity_a15_v1_eta4`. The alternate ID ends in `eta1`. Their physical fields are `a15_eta4` and `a15_eta1` respectively. Their `raw_definition_id` is an input metadata identifier, not an additional experimental-primary selection.

| Axis | Default coordinates | Units and endpoints |
| --- | --- | --- |
| Activity | 4096 integer bins, 0–4095 | Particle count |
| Delta phi | 100 equal bins, -pi/2 to 3pi/2 | Radians, lower inclusive and upper exclusive |
| Eta | 100 equal bins, -4 to 4 | Dimensionless, both physical endpoints inclusive |
| Phi | 100 equal bins, -pi to pi | Radians, both physical endpoints inclusive |
| Query pT | 0, 0.15, then 0.5-GeV/c edges through 50, followed by 60, 75, 100, 150, 250, 500, 1000, 2000, 4000, 7000 | GeV/c, inclusive physical endpoints and retained overflow |
| Spectrum pT | 0.5-GeV/c bins from 0 through 50, then the same upper edges | GeV/c, no fixed floor. No bin-width normalization. |

The field `phase_a_t9_two_sided_quantile` is the literal key for the fixed nine-degree-of-freedom t quantile. Its value is 2.2621571628540993. It supports the denominator and class-boundary resolution policy. It is not a user-selectable uncertainty method.

## Presentation settings

| Key | Default, constraint and effect |
| --- | --- |
| `schema`, `version` | `hadronization_plot_presentation_v3`, `3.2.0`. Exact contract |
| `families` | Eleven signed-species groups. Nonempty, unique PDGs with conjugate completeness. Controls facets, not particle science. |
| `presets.all_central.selector` | `all_central`. Fixed selector name |
| `presets.all_registered.selector` | `all_registered`. Fixed selector name |
| `presets.paper_default.families` | D, LambdaC, B, LambdaB. Display families |
| `presets.paper_default.trigger_pdgs` | 421, 4122, 521, 5122. Must match numerical charm recipe |
| `presets.paper_default.baryon_meson_trigger_pdgs` | 421, 521. Trigger columns for the canonical Lambda comparison. Additional baryon pages use both saved triggers in each sector |
| `layout.axis_padding_fraction` | 0.08. Number from 0 to 1. Adds display range padding. |
| `layout.facet_dimension` | `associate_family`. Fixed |
| `layout.grid_columns_maximum` | 3. Positive integer. Layout column limit. |
| `layout.maximum_panels_per_page` | 8. Positive integer. Controls page splitting. |
| `layout.shared_legend_reservation` | `page_top`. Fixed reservation for the multiplicity-class key. Tune keys appear inside a plot frame. |
| `layout.text_pixel_size` | 18. Positive integer. ROOT drawing text scale. |
| `layout.physical_width_cm` | 18. Fixed cm width |
| `layout.minimum_body_text_pt` | 8. Fixed typographic point minimum |
| `layout.categorical_tune_dodge` | Upper: -0.08, 0, 0.08. Lower: -0.04, 0.04. Fixed compatibility map. Current scientific category positions coincide. |
| `layout.p1_inset_geometry` | `[0.18,0.05,0.65,0.48]`. Fixed normalized rectangle for the multiplicity inset |
| `layout.correlation_view` | `monash_pair_sign`. Also accepts `monash_balance` and `all_tune_ratio` |
| `layout.activity_category_dividers` | false. Boolean. Adds vertical category dividers when true. |
| `style_identities.class_line_style_rule` | Integrated style 1, others by class order. Fixed mapping |
| `style_identities.class_line_patterns` | One solid and eleven distinct dash patterns. Exact ROOT style IDs, dash strings and inclusive role |
| `style_identities.species_encoding` | `facet_only`. Fixed |
| `style_identities.tunes` | MONASH black circle, JUNCTIONS blue square, CLOSEPACKING orange triangle. Fixed IDs, RGB colors, markers and solid tune lines |
| `style_identities.unity_reference` | Neutral gray, dotted. Fixed reference-only role |

Tune keys use one vertical column in the top-right panel where available.
The renderer selects a position clear of curves and error bars.
Scientific captions sit inside the upper plot frames.
Their first lines align with the corresponding legend entries.
The three selected activity intervals have a separate line-style key inside a right-hand panel.
It sits beside the tune key when space permits, or in the next row.

Signed heavy-hadron spectra gain display headroom when their scientific text or tune key needs it.
This adjustment preserves all numerical values and the ratio-panel range.
Their titles sit just above the absolute-panel frame.
Three-row balancing pages have one shared yield title.
One associate-species title sits beneath the center of both columns.

The supplemental activity pages select the saved 0-1%, 40-50% and 80-90% intervals. Long dashes, dots and short separated dashes distinguish these classes. Multi-class balancing pages omit markers. Tune colors remain unchanged. The renderer does not substitute another interval when one is absent. The main activity pages retain all requested classes.

`p1_inset_geometry` is the literal configuration key for the multiplicity percentile inset. The renderer transforms its normalized rectangle to preserve the intended physical aspect. It is not a scientific axis or a percentile definition.

`monash_pair_sign` shows identified OS/SS pairs above and the inclusive heavy-flavour sign difference below. `monash_balance` shows the MONASH OS, SS and net components. `all_tune_ratio` shows tune comparisons. The selected numerical recipe remains authoritative in each case.

`plot-dplus.json` changes the charm trigger preset to 411. `plot-all-tune.json` changes only `correlation_view`. Neither file changes uncertainty calculation or acceptance.

## Site settings

The resolver reads explicit keys from `config/site.conf`. It uses executable discovery and the current Python when a corresponding key is absent. Relative raw and work roots resolve against the repository. Do not add unknown site keys. They have no documented consumer.

| Key | Type and default without a site file | Consumer and effect |
| --- | --- | --- |
| `RAW_ROOT` | Path, `data/raw` | Generation input/output inventory |
| `WORK_ROOT` | Path, `data/work` | Generation builds, reservations and scratch |
| `ROOT_PREFIX` | Optional installation path | Locates ROOT executables and libraries |
| `ROOT_CONFIG` | Executable path, `root-config` on PATH | ROOT flags and version |
| `ROOT` | Executable path, `root` on PATH or prefix | ROOT interpreter |
| `ROOT_VERSION` | Optional exact version string | Refuses a different reported version |
| `ROOT_GCC_PREFIX` | Optional compiler-runtime prefix | Adds runtime libraries needed by ROOT |
| `ROOT_RUNTIME_LIB_DIRS` | Colon-separated library paths | Adds ROOT dependencies to loader search |
| `PYTHIA8_PREFIX` | Optional installation path | Must match `pythia8-config --prefix` |
| `PYTHIA8_CONFIG` | Executable path, `pythia8-config` on PATH | PYTHIA version, include and link flags |
| `PYTHIA8_VERSION` | Version string, `8.317` | Exact reported/header version check |
| `PYTHIA8_GCC_PREFIX` | Optional compiler-runtime prefix | Adds PYTHIA runtime libraries |
| `PYTHIA8DATA` | Path, prefix plus `share/Pythia8/xmldoc` | Must contain `Index.xml` |
| `CXX` | Executable, resolved C++ compiler | Compiles native code |
| `PYTHON` | Executable, current Python or PATH fallback | Setup and development suite interpreter |
| `SCHEDULER_SUBMIT` | Optional executable path | Required for explicit generation submission |

`TMPDIR` selects temporary disk storage through the standard environment. Use an existing writable directory. Query CLI `--work-root` and plot CLI `--work-dir` select their own caches. The `WORK_ROOT` setting does not override every stage-specific command option.

## Cluster resource record

`condor prepare` writes a site admission template. All paths must be absolute and nonsymlinked. Bulk and control storage must remain separate. Each evidence record contains a path, byte count and SHA-256.

| Field | Type and constraint | Effect |
| --- | --- | --- |
| `decision`, `authority` | Fixed admitted decision and reviewed authority strings | Enables site binding only after supporting evidence |
| `inert_bundle_manifest_sha256`, `qualified_pack_sha256` | SHA-256 strings | Bind source bundle and Linux executable pack |
| `maxjobs` | Integer, exactly 4 | Total query concurrency |
| `memory_mb`, `scratch_kb` | Positive integers, scheduler MB memory and KB disk requests | Worker resource requests |
| `input_root`, `durable_bulk_root`, `durable_control_root` | Absolute paths | Accepted inputs, immutable attempts and acceptance records |
| `execute_node_canary`, `runtime_versions`, `input_readback`, `posix_nooverwrite`, `posix_readback`, `quota`, `retention` | Required `PASS` records | Site qualification checks |
| `evidence` | Exact map of file facts | Also includes `classads`, `capacity`, `control_custody`, `pair_population`, `resource_budget` |
| `resource_envelope.query_peak_rss_mb` | Positive integer | Measured query memory peak |
| `resource_envelope.query_peak_scratch_kb` | Positive integer | Measured scratch peak |
| `resource_envelope.merge_peak_rss_mb` | Positive integer | Measured physical-merge memory peak |
| `resource_envelope.reduce_peak_rss_mb` | Positive integer | Measured numerical-reduction memory peak |
| `resource_envelope.render_peak_rss_mb` | Positive integer | Measured renderer memory peak |
| `resource_envelope.postprocess_limit_mb` | Positive integer | Allocated postprocessing memory |
| `resource_envelope.bulk_projected_peak_bytes` | Positive integer, bytes | Projected peak persistent usage |
| `resource_envelope.bulk_allocated_bytes` | Positive integer, bytes | Available allocation for this run |
| `resource_envelope.query_occupied_cells` | Positive integer | Measured query sparse population |
| `resource_envelope.merged_occupied_cells` | Positive integer | Measured merged sparse population |
| `resource_envelope.screened_input_pairs` | Positive integer, at most input-pair count | Measurement coverage |
| `resource_envelope.covered_tune_blocks` | Integer, complete tune-by-block domain | Required coverage of every original block |

Worker memory, scratch, postprocessing memory and bulk allocation must each provide at least 25% headroom over the corresponding peak. The immutable DAG fixes retries at two and deterministic failure at exit 42. These are not free-form configuration switches.

## Tune command values

The table lists every active assignment in the three shipped tune cards. A dash means that the card does not override that PYTHIA setting. It does not mean zero or disabled. PYTHIA applies the selected baseline tune and its own setting validation.

Generation consumes all card values. The worker replaces `Main:numberOfEvents` with the campaign's successful-event request and appends deterministic seed controls. The producer disables recognized heavy-hadron decays and records effective settings. A card change does not change accepted event bytes.

| Setting | MONASH | JUNCTIONS | CLOSEPACKING | Type or units |
| --- | --- | --- | --- | --- |
| `BeamRemnants:remnantMode` | `—` | `1` | `1` | integer |
| `BeamRemnants:saturation` | `—` | `5` | `5` | integer |
| `Beams:eCM` | `13600` | `13600` | `13600` | integer (GeV) |
| `Beams:idA` | `2212` | `2212` | `2212` | integer |
| `Beams:idB` | `2212` | `2212` | `2212` | integer |
| `ClosePacking:PT0` | `—` | `—` | `2.0` | number |
| `ClosePacking:baryonSup` | `—` | `—` | `0.928` | number |
| `ClosePacking:doClosePacking` | `—` | `—` | `on` | boolean switch |
| `ClosePacking:doEnhanceDiquark` | `—` | `—` | `off` | boolean switch |
| `ClosePacking:enhancePT` | `—` | `—` | `0.014` | number |
| `ClosePacking:enhanceStrange` | `—` | `—` | `0.014` | number |
| `ClosePacking:parallelBaryonSup` | `—` | `—` | `0` | integer |
| `ColourReconnection:allowDoubleJunRem` | `—` | `off` | `off` | boolean switch |
| `ColourReconnection:allowJunctions` | `—` | `on` | `on` | boolean switch |
| `ColourReconnection:junctionCorrection` | `—` | `1.20` | `1.349` | number |
| `ColourReconnection:m0` | `—` | `0.3` | `0.618` | number |
| `ColourReconnection:mPseudo` | `—` | `—` | `0.403` | number |
| `ColourReconnection:mode` | `—` | `1` | `1` | integer |
| `ColourReconnection:timeDilationMode` | `—` | `2` | `2` | integer |
| `ColourReconnection:timeDilationPar` | `—` | `0.18` | `0.18` | number |
| `HardQCD:hardbbbar` | `on` | `on` | `on` | boolean switch |
| `HardQCD:hardccbar` | `on` | `on` | `on` | boolean switch |
| `Init:showChangedParticleData` | `off` | `off` | `off` | boolean switch |
| `Init:showMultipartonInteractions` | `off` | `off` | `off` | boolean switch |
| `Main:numberOfEvents` | `1000000` | `1000000` | `1000000` | integer |
| `MultipartonInteractions:pT0Ref` | `—` | `2.15` | `2.194` | number (GeV) |
| `Next:numberCount` | `0` | `0` | `0` | integer |
| `Next:numberShowEvent` | `0` | `0` | `0` | integer |
| `Next:numberShowInfo` | `0` | `0` | `0` | integer |
| `Next:numberShowProcess` | `0` | `0` | `0` | integer |
| `ParticleDecays:limitTau0` | `on` | `on` | `on` | boolean switch |
| `ParticleDecays:tau0Max` | `0.01` | `0.01` | `0.01` | number (mm) |
| `PhaseSpace:pTHatMin` | `2.` | `2.` | `2.` | number (GeV) |
| `Ropewalk:RopeHadronization` | `—` | `—` | `off` | boolean switch |
| `StringFlav:probQQ1toQQ0join` | `—` | `0.0275, 0.0275, 0.0275, 0.0275` | `0.5, 0.7, 0.9, 1.0` | numeric vector |
| `StringFlav:probQQtoQ` | `—` | `0.078` | `0.081` | number |
| `StringFlav:probStoUD` | `—` | `0.2` | `0.217` | number |
| `StringFragmentation:doStrangeJunctions` | `—` | `—` | `on` | boolean switch |
| `StringFragmentation:enhanceStrangeJunction` | `—` | `—` | `0.540` | number |
| `StringPT:sigma` | `—` | `0.335` | `0.335` | number (GeV) |
| `StringZ:aLund` | `—` | `0.36` | `0.68` | number |
| `StringZ:bLund` | `—` | `0.56` | `0.98` | number |
| `StringZ:useOldAExtra` | `—` | `—` | `off` | boolean switch |
| `Tune:pp` | `14` | `14` | `14` | integer |

Beam and hard-process settings define the collision and heavy-flavour bias. `StringZ` and `StringPT` configure string fragmentation. `StringFlav` controls flavour production parameters. `MultipartonInteractions` sets the MPI scale.

`BeamRemnants` and `ColourReconnection` configure remnants and color reconnection. `ClosePacking` and `StringFragmentation` configure the additional close-packing and junction settings. `Ropewalk` controls the listed rope switch. `Init` and `Next` settings control generator output.

The raw contract requires common values and permits only its listed tune differences. Use the effective-settings record in raw ROOT to inspect resolved generator values. Card comments do not configure downstream pT cuts, activity classes or statistical estimators.

## Campaign constraints

The analysis campaign adapter derives exposure and block membership from the descriptor. Its supported bounds do not make every downstream stage campaign-independent. The supplied generation identity and full reduction route impose the additional restrictions in the workflow.

| Field | Adapter constraint |
| --- | --- |
| `tune_order` | One to four unique nonempty tune names |
| `logical_jobs_per_tune` | Integer from 1 through 16,384 |
| `successful_events_per_logical_job` | Integer from 1 through 1,048,575 |
| `successful_events_per_tune` | Exactly jobs per tune times successful events per job |
| `blocks.count` | Positive divisor of jobs per tune |
| `blocks.logical_id_domain` | Exactly zero through jobs per tune minus one |
| `blocks.logical_id_rule` | Exactly `block=(logical_id%K)+1`, with the declared block count replacing `K` |
| `seed.campaign_ordinal` | Integer from 1 through 65,535 |
| `seed.tune_ordinals` | Consecutive zero-based ordinals in declared tune order |
| `seed.attempt_domain` | Ordered integer endpoints from 0 through 4,095, with at most ten consecutive attempts |

## Fixed JSON field inventory

The following field inventory accounts for nested keys in shipped scientific JSON. `[]` denotes each array element. `{key}` denotes each key of a repeated mapping. Types and compact scalar values describe the shipped files, not permission to edit a fixed field.

For long arrays, hashes and descriptor strings, follow the linked source for exact bytes. The group descriptions above define consumers and scientific effects. Repeated registry objects share the enumerated field schema.

### config/analysis.json

| Field | Type and shipped value or source |
| --- | --- |
| `schema` | string: [fixed text or digest in source](../config/analysis.json) |
| `version` | string: `"2.2.0"` |
| `paper_defaults.charm_meson_pdg` | integer: `421` |
| `paper_defaults.selectable_charm_meson_pdgs` | array: `[421,411]` |
| `paper_defaults.historical_charm_meson_pdg` | integer: `411` (fixed compatibility identity) |
| `paper_defaults.p8_charm_tuple` | array: `[421,-4122,-421]` |
| `base_study.schema` | string: [exact value](../config/analysis.json) |
| `base_study.sha256` | string: [fixed text or digest in source](../config/analysis.json) |
| `lossless_input.schema` | string: [exact value](../config/analysis.json) |
| `lossless_input.schema_digest` | string: [fixed text or digest in source](../config/analysis.json) |
| `lossless_input.structural_registries_digest` | string: [fixed text or digest in source](../config/analysis.json) |
| `axes.activity.bins` | integer: `4096` |
| `axes.activity.integer_domain` | array: `[0,4095]` |
| `axes.activity.endpoint_rule` | string: [fixed text or digest in source](../config/analysis.json) |
| `axes.dphi.bins` | integer: `100` |
| `axes.dphi.low` | number: `-1.5707963267948966` |
| `axes.dphi.high` | number: `4.71238898038469` |
| `axes.dphi.endpoint_rule` | string: [exact value](../config/analysis.json) |
| `axes.dphi.semantic` | string: [fixed text or digest in source](../config/analysis.json) |
| `axes.eta.bins` | integer: `100` |
| `axes.eta.low` | number: `-4.0` |
| `axes.eta.high` | number: `4.0` |
| `axes.eta.endpoint_rule` | string: [fixed text or digest in source](../config/analysis.json) |
| `axes.phi.bins` | integer: `100` |
| `axes.phi.low` | number: `-3.141592653589793` |
| `axes.phi.high` | number: `3.141592653589793` |
| `axes.phi.endpoint_rule` | string: [fixed text or digest in source](../config/analysis.json) |
| `axes.pt.edges` | array: [112 entries in source](../config/analysis.json) |
| `axes.pt.endpoint_rule` | string: [fixed text or digest in source](../config/analysis.json) |
| `profiles` | array: `1 records` |
| `profiles[].id` | string: Record-specific value in the linked source |
| `profiles[].trigger_pt` | null: Record-specific value in the linked source |
| `profiles[].associate_pt` | null: Record-specific value in the linked source |
| `profiles[].relative_pt` | null: Record-specific value in the linked source |
| `pair_acceptance.eta.operator` | string: `"abs<="` |
| `pair_acceptance.eta.value` | number: `4.0` |
| `pair_acceptance.roles` | string: [exact value](../config/analysis.json) |
| `pair_acceptance.dphi_sign` | string: [exact value](../config/analysis.json) |
| `activities` | array: `2 records` |
| `activities[].id` | string: Record-specific value in the linked source |
| `activities[].semantic_id` | string: Record-specific value in the linked source |
| `activities[].physical_field` | string: Record-specific value in the linked source |
| `activities[].eta_window` | number: Record-specific value in the linked source |
| `activities[].role` | string: Record-specific value in the linked source |
| `activities[].raw_definition_id` | string: Record-specific value in the linked source |
| `activities[].predicate` | string: Record-specific value in the linked source |
| `percentile_intervals` | array: [11 entries in source](../config/analysis.json) |
| `integrated_interval` | array: `[0,100]` |
| `activity_policy.threshold` | string: [fixed text or digest in source](../config/analysis.json) |
| `activity_policy.tie_rule` | string: [fixed text or digest in source](../config/analysis.json) |
| `activity_policy.weight_convention` | string: [fixed text or digest in source](../config/analysis.json) |
| `activity_policy.complement_rule` | string: [fixed text or digest in source](../config/analysis.json) |
| `pair_query_registry.expansion` | string: [fixed text or digest in source](../config/analysis.json) |
| `pair_query_registry.trigger_pdgs` | array: [exact value](../config/analysis.json) |
| `pair_query_registry.associate_pdgs.charm` | array: [24 entries in source](../config/analysis.json) |
| `pair_query_registry.associate_pdgs.beauty` | array: [26 entries in source](../config/analysis.json) |
| `pair_query_registry.reference_meson_by_trigger.-5122` | integer: `-521` |
| `pair_query_registry.reference_meson_by_trigger.-4122` | integer: `421` |
| `pair_query_registry.reference_meson_by_trigger.-521` | integer: `521` |
| `pair_query_registry.reference_meson_by_trigger.-511` | integer: `511` |
| `pair_query_registry.reference_meson_by_trigger.-421` | integer: `421` |
| `pair_query_registry.reference_meson_by_trigger.-411` | integer: `411` |
| `pair_query_registry.reference_meson_by_trigger.411` | integer: `-411` |
| `pair_query_registry.reference_meson_by_trigger.421` | integer: `-421` |
| `pair_query_registry.reference_meson_by_trigger.511` | integer: `-511` |
| `pair_query_registry.reference_meson_by_trigger.521` | integer: `-521` |
| `pair_query_registry.reference_meson_by_trigger.4122` | integer: `-421` |
| `pair_query_registry.reference_meson_by_trigger.5122` | integer: `521` |
| `pair_query_registry.expected_count` | integer: `300` |
| `pair_query_registry.central_eligibility_source` | string: [fixed text or digest in source](../config/analysis.json) |
| `correlations.tunes` | string: `"all admitted tunes"` |
| `correlations.identities` | array: [exact value](../config/analysis.json) |
| `correlations.components` | array: `["OS","SS"]` |
| `correlations.difference_recipe` | string: `"OS-SS"` |
| `projection_recipes` | array: [9 entries in source](../config/analysis.json) |
| `g9_species_pdgs` | array: [exact value](../config/analysis.json) |
| `estimator_policy.id` | string: [fixed text or digest in source](../config/analysis.json) |
| `estimator_policy.release_block_count` | integer: `10` |
| `estimator_policy.variance_dof` | integer: `9` |
| `estimator_policy.center` | string: [exact value](../config/analysis.json) |
| `estimator_policy.covariance` | string: [fixed text or digest in source](../config/analysis.json) |
| `estimator_policy.bias_correction` | boolean: `false` |
| `estimator_policy.denominator_resolution_alpha` | number: `0.05` |
| `estimator_policy.phase_a_t9_two_sided_quantile` | number: `2.2621571628540993` |
| `estimator_policy.quantile_algorithm` | string: [fixed text or digest in source](../config/analysis.json) |
| `estimator_policy.cancelled_parent_rule` | string: [fixed text or digest in source](../config/analysis.json) |
| `estimator_policy.class_boundary_statuses` | array: [exact value](../config/analysis.json) |
| `estimator_policy.display_label` | string: [fixed text or digest in source](../config/analysis.json) |
| `compact_domain_registries.projection_ids` | array: `10 records` |
| `compact_domain_registries.projection_ids[].id` | integer: Record-specific value in the linked source |
| `compact_domain_registries.projection_ids[].name` | string: Record-specific value in the linked source |
| `compact_domain_registries.projection_ids[].scope_family` | string: Record-specific value in the linked source |
| `compact_domain_registries.origin_ids` | array: `5 records` |
| `compact_domain_registries.origin_ids[].id` | integer: Record-specific value in the linked source |
| `compact_domain_registries.origin_ids[].label` | string: Record-specific value in the linked source |
| `compact_domain_registries.closure_category_ids` | array: `4 records` |
| `compact_domain_registries.closure_category_ids[].id` | integer: Record-specific value in the linked source |
| `compact_domain_registries.closure_category_ids[].label` | string: Record-specific value in the linked source |
| `compact_domain_registries.correlation_component_ids` | array: `2 records` |
| `compact_domain_registries.correlation_component_ids[].id` | integer: Record-specific value in the linked source |
| `compact_domain_registries.correlation_component_ids[].label` | string: Record-specific value in the linked source |
| `compact_domain_registries.closure_full_visible_component_ids` | array: `2 records` |
| `compact_domain_registries.closure_full_visible_component_ids[].id` | integer: Record-specific value in the linked source |
| `compact_domain_registries.closure_full_visible_component_ids[].label` | string: Record-specific value in the linked source |
| `compact_domain_registries.g9_axis_ids` | array: `3 records` |
| `compact_domain_registries.g9_axis_ids[].id` | integer: Record-specific value in the linked source |
| `compact_domain_registries.g9_axis_ids[].label` | string: Record-specific value in the linked source |
| `compact_domain_registries.g9_axis_ids[].flow` | string: Record-specific value in the linked source |
| `compact_domain_registries.t1_component_ids` | array: `3 records` |
| `compact_domain_registries.t1_component_ids[].id` | integer: Record-specific value in the linked source |
| `compact_domain_registries.t1_component_ids[].label` | string: Record-specific value in the linked source |
| `compact_domain_registries.gram_component_kinds` | array: `2 records` |
| `compact_domain_registries.gram_component_kinds[].id` | integer: Record-specific value in the linked source |
| `compact_domain_registries.gram_component_kinds[].label` | string: Record-specific value in the linked source |
| `compact_domain_registries.gram_component_kinds[].source` | string: Record-specific value in the linked source |
| `compact_storage.schema` | string: [exact value](../config/analysis.json) |
| `compact_storage.tables` | array: `["cells","event_gram"]` |
| `compact_storage.metadata_objects` | array: `["metadata","receipt"]` |
| `compact_storage.compression.algorithm` | string: `"ZSTD"` |
| `compact_storage.compression.level` | integer: `5` |
| `compact_storage.maximum_complete_default_bytes` | integer: `89128960` |
| `compact_storage.sparse_rule` | string: [fixed text or digest in source](../config/analysis.json) |
| `compact_storage.pooled_copy` | boolean: `false` |
| `compact_storage.summation` | string: [fixed text or digest in source](../config/analysis.json) |
### config/query.json

| Field | Type and shipped value or source |
| --- | --- |
| `schema` | string: [exact value](../config/query.json) |
| `compression.algorithm` | string: `"ZSTD"` |
| `compression.level` | integer: `5` |
| `row_authority` | string: [fixed text or digest in source](../config/query.json) |
| `source_identity` | string: [fixed text or digest in source](../config/query.json) |
| `dictionary` | string: [fixed text or digest in source](../config/query.json) |
| `sparse_exactness` | string: [fixed text or digest in source](../config/query.json) |
| `flows` | string: [fixed text or digest in source](../config/query.json) |
| `trees.events` | array: [8 entries in source](../config/query.json) |
| `trees.heavy` | array: [18 entries in source](../config/query.json) |
| `trees.triggers` | array: [exact value](../config/query.json) |
| `trees.pairs` | array: [13 entries in source](../config/query.json) |
| `trees.origins` | array: [8 entries in source](../config/query.json) |
| `trees.closure` | array: [6 entries in source](../config/query.json) |
| `trees.constituents` | array: [9 entries in source](../config/query.json) |
| `trees.event_compatibility` | array: [exact value](../config/query.json) |
| `trees.event_ranges` | array: [exact value](../config/query.json) |
| `trees.source_blocks` | array: [exact value](../config/query.json) |
| `trees.sources` | array: [9 entries in source](../config/query.json) |
| `trees.source_counts` | array: [exact value](../config/query.json) |
| `sparse.activity` | array: [exact value](../config/query.json) |
| `sparse.triggers` | array: [7 entries in source](../config/query.json) |
| `sparse.pairs` | array: [15 entries in source](../config/query.json) |
| `sparse.kinematics` | array: [exact value](../config/query.json) |
| `sparse.closure` | array: [12 entries in source](../config/query.json) |
### config/study.json

This file binds raw compatibility and the signed-state registry. Its selection, activity bounds and statistics descriptors do not override downstream analysis.

| Field | Type and shipped value or source |
| --- | --- |
| `activity.class_scope` | string: [exact value](../config/study.json) |
| `activity.classes` | array: `12 records` |
| `activity.classes[].id` | string: Record-specific value in the linked source |
| `activity.classes[].kind` | string: Record-specific value in the linked source |
| `activity.classes[].percentile_high` | string: Record-specific value in the linked source |
| `activity.classes[].percentile_low` | string: Record-specific value in the linked source |
| `activity.id` | string: [exact value](../config/study.json) |
| `activity.predicate.abs_eta_max` | string: `"1.0"` |
| `activity.predicate.abs_eta_relation` | string: `"inclusive"` |
| `activity.predicate.charged` | boolean: `true` |
| `activity.predicate.final` | boolean: `true` |
| `activity.predicate.heavy_constituent` | string: `"none"` |
| `activity.predicate.pt_min_gev` | string: `"0.15"` |
| `activity.predicate.pt_min_relation` | string: `"exclusive"` |
| `activity.tie_rule` | string: [fixed text or digest in source](../config/study.json) |
| `observables.balancing.estimators` | array: [11 entries in source](../config/study.json) |
| `observables.balancing.ids` | array: [4 entries in source](../config/study.json) |
| `observables.correlations.delta_phi.bins` | integer: `100` |
| `observables.correlations.delta_phi.high` | string: `"4.712389"` |
| `observables.correlations.delta_phi.kind` | string: `"uniform"` |
| `observables.correlations.delta_phi.low` | string: `"-1.570796"` |
| `observables.correlations.pairs` | array: `4 records` |
| `observables.correlations.pairs[].activity_id` | string: Record-specific value in the linked source |
| `observables.correlations.pairs[].associate` | string: Record-specific value in the linked source |
| `observables.correlations.pairs[].contexts` | array: Record-specific value in the linked source |
| `observables.correlations.pairs[].flavour` | string: Record-specific value in the linked source |
| `observables.correlations.pairs[].id` | string: Record-specific value in the linked source |
| `observables.correlations.pairs[].trigger` | string: Record-specific value in the linked source |
| `observables.correlations.tunes` | array: `["MONASH"]` |
| `observables.inclusive_kinematics.axes.eta.bins` | integer: `100` |
| `observables.inclusive_kinematics.axes.eta.high` | string: `"4.0"` |
| `observables.inclusive_kinematics.axes.eta.kind` | string: `"uniform"` |
| `observables.inclusive_kinematics.axes.eta.low` | string: `"-4.0"` |
| `observables.inclusive_kinematics.axes.phi.bins` | integer: `100` |
| `observables.inclusive_kinematics.axes.phi.high` | string: `"3.141593"` |
| `observables.inclusive_kinematics.axes.phi.kind` | string: `"uniform"` |
| `observables.inclusive_kinematics.axes.phi.low` | string: `"-3.141593"` |
| `observables.inclusive_kinematics.axes.pt.edges` | array: [111 entries in source](../config/study.json) |
| `observables.inclusive_kinematics.axes.pt.kind` | string: `"variable"` |
| `observables.inclusive_kinematics.species` | array: `10 records` |
| `observables.inclusive_kinematics.species[].id` | string: Record-specific value in the linked source |
| `observables.inclusive_kinematics.species[].pdg` | integer: Record-specific value in the linked source |
| `observables.multiplicity.activity_id` | string: [exact value](../config/study.json) |
| `observables.multiplicity.binning.bins` | integer: `4096` |
| `observables.multiplicity.binning.high` | string: `"4095.5"` |
| `observables.multiplicity.binning.kind` | string: `"uniform"` |
| `observables.multiplicity.binning.low` | string: `"-0.5"` |
| `observables.sample_counts.quantities` | array: [4 entries in source](../config/study.json) |
| `observables.sample_counts.signed_species` | array: `8 records` |
| `observables.sample_counts.signed_species[].id` | string: Record-specific value in the linked source |
| `observables.sample_counts.signed_species[].label` | string: Record-specific value in the linked source |
| `observables.sample_counts.signed_species[].pdg` | integer: Record-specific value in the linked source |
| `pair_observable.balancing_pairs` | array: `16 records` |
| `pair_observable.balancing_pairs[].flavour` | string: Record-specific value in the linked source |
| `pair_observable.balancing_pairs[].id` | string: Record-specific value in the linked source |
| `pair_observable.balancing_pairs[].os_associate` | string: Record-specific value in the linked source |
| `pair_observable.balancing_pairs[].os_associate_pdg` | integer: Record-specific value in the linked source |
| `pair_observable.balancing_pairs[].ss_associate` | string: Record-specific value in the linked source |
| `pair_observable.balancing_pairs[].ss_associate_pdg` | integer: Record-specific value in the linked source |
| `pair_observable.balancing_pairs[].trigger` | string: Record-specific value in the linked source |
| `pair_observable.balancing_pairs[].trigger_pdg` | integer: Record-specific value in the linked source |
| `pair_observable.formula` | string: [exact value](../config/study.json) |
| `pair_observable.integration` | string: `"full_delta_phi"` |
| `pair_observable.missing_quantities` | string: [exact value](../config/study.json) |
| `pair_observable.ordered_conditional_pairs` | boolean: `true` |
| `pair_observable.os_ss_trigger_denominators` | string: `"must_match"` |
| `pair_observable.same_sign_factor` | string: `"1.0"` |
| `pair_observable.sign_definition` | string: `"heavy_flavour_sign"` |
| `raw_input_contract.compatibility` | string: [exact value](../config/study.json) |
| `raw_input_contract.metadata.species_registry_schema` | string: [exact value](../config/study.json) |
| `raw_input_contract.metadata.species_registry_sha256` | string: [fixed text or digest in source](../config/study.json) |
| `raw_input_contract.metadata.tune_difference_allowlist_schema` | string: [exact value](../config/study.json) |
| `raw_input_contract.metadata.tune_difference_allowlist_schema_branch` | string: [exact value](../config/study.json) |
| `raw_input_contract.metadata.tune_difference_allowlist_sha256` | string: [fixed text or digest in source](../config/study.json) |
| `raw_input_contract.metadata.tune_difference_allowlist_sha256_branch` | string: [exact value](../config/study.json) |
| `raw_input_contract.multiplicity.central_branch` | string: [exact value](../config/study.json) |
| `raw_input_contract.multiplicity.central_object_value` | string: [exact value](../config/study.json) |
| `raw_input_contract.multiplicity.definition` | string: [exact value](../config/study.json) |
| `raw_input_contract.multiplicity.semantics` | string: [fixed text or digest in source](../config/study.json) |
| `raw_input_contract.multiplicity.wide_branch` | string: [exact value](../config/study.json) |
| `raw_input_contract.multiplicity.wide_object_value` | string: [exact value](../config/study.json) |
| `raw_input_contract.schema` | string: [exact value](../config/study.json) |
| `schema` | string: [exact value](../config/study.json) |
| `scope.held_attempts` | string: [exact value](../config/study.json) |
| `scope.research_question` | string: [fixed text or digest in source](../config/study.json) |
| `scope.systematic_uncertainty` | string: `"disabled_and_absent"` |
| `scope.uncertainty` | string: `"statistical_only"` |
| `scope.variation_selection` | boolean: `false` |
| `selected_states` | array: `50 records` |
| `selected_states[].pair_analysis_eligible` | boolean: Record-specific value in the linked source |
| `selected_states[].charge3` | integer: Record-specific value in the linked source |
| `selected_states[].id` | string: Record-specific value in the linked source |
| `selected_states[].kind` | string: Record-specific value in the linked source |
| `selected_states[].name` | string: Record-specific value in the linked source |
| `selected_states[].pdg` | integer: Record-specific value in the linked source |
| `selected_states[].qb` | integer: Record-specific value in the linked source |
| `selected_states[].qc` | integer: Record-specific value in the linked source |
| `selected_states[].sector` | string: Record-specific value in the linked source |
| `selected_states[].spin2j1` | integer: Record-specific value in the linked source |
| `selected_states[].status` | string: Record-specific value in the linked source |
| `selected_states[].valence` | string: Record-specific value in the linked source |
| `selected_states[].reason` | string: Record-specific value in the linked source |
| `selection.associate.abs_eta_max` | string: `"4.0"` |
| `selection.associate.abs_eta_relation` | string: `"inclusive"` |
| `selection.associate.final` | boolean: `true` |
| `selection.associate.origin` | string: `"unrestricted"` |
| `selection.associate.pt_min_gev` | string: `"0.15"` |
| `selection.associate.pt_min_relation` | string: `"exclusive"` |
| `selection.associate.pythia_status_abs_max` | integer: `89` |
| `selection.associate.pythia_status_abs_min` | integer: `81` |
| `selection.associate.selected_state` | boolean: `true` |
| `selection.inclusive_kinematics.abs_eta_max` | string: `"4.0"` |
| `selection.inclusive_kinematics.abs_eta_relation` | string: `"inclusive"` |
| `selection.inclusive_kinematics.direct_hadronization_selected_state` | boolean: `true` |
| `selection.inclusive_kinematics.final` | boolean: `true` |
| `selection.inclusive_kinematics.pt_min_gev` | string: `"0.15"` |
| `selection.inclusive_kinematics.pt_min_relation` | string: `"exclusive"` |
| `selection.inclusive_kinematics.selected_hard_origin_required` | boolean: `false` |
| `selection.inclusive_kinematics.signed_pdg_exact` | boolean: `true` |
| `selection.t1.final_stored_heavy_hadron` | boolean: `true` |
| `selection.t1.hidden_heavy_content_counts_twice` | boolean: `true` |
| `selection.t1.kinematic_acceptance` | string: `"none"` |
| `selection.t1.signed_pdg_exact` | boolean: `true` |
| `selection.trigger.abs_eta_max` | string: `"4.0"` |
| `selection.trigger.abs_eta_relation` | string: `"inclusive"` |
| `selection.trigger.final` | boolean: `true` |
| `selection.trigger.origin` | string: [exact value](../config/study.json) |
| `selection.trigger.pt_min_gev` | string: `"1.0"` |
| `selection.trigger.pt_min_relation` | string: `"exclusive"` |
| `selection.trigger.pythia_status_abs_max` | integer: `89` |
| `selection.trigger.pythia_status_abs_min` | integer: `81` |
| `selection.trigger.selected_state` | boolean: `true` |
| `statistics.block_assignment` | string: [exact value](../config/study.json) |
| `statistics.blocks` | integer: `10` |
| `statistics.central` | string: [exact value](../config/study.json) |
| `statistics.equal_exposure` | boolean: `true` |
| `statistics.independent_tune_difference` | string: [exact value](../config/study.json) |
| `statistics.nonlinear_ratios` | string: [exact value](../config/study.json) |
| `statistics.systematic_uncertainty` | string: `"absent"` |
| `statistics.uncertainty` | string: [exact value](../config/study.json) |
| `tune_card_contract.allowed_tune_differences` | array: [28 entries in source](../config/study.json) |
| `tune_card_contract.common_required_values.Beams:eCM` | string: `"13600"` |
| `tune_card_contract.common_required_values.Beams:idA` | string: `"2212"` |
| `tune_card_contract.common_required_values.Beams:idB` | string: `"2212"` |
| `tune_card_contract.common_required_values.HardQCD:hardbbbar` | string: `"on"` |
| `tune_card_contract.common_required_values.HardQCD:hardccbar` | string: `"on"` |
| `tune_card_contract.common_required_values.Init:showChangedParticleData` | string: `"off"` |
| `tune_card_contract.common_required_values.Init:showMultipartonInteractions` | string: `"off"` |
| `tune_card_contract.common_required_values.Next:numberCount` | string: `"0"` |
| `tune_card_contract.common_required_values.Next:numberShowEvent` | string: `"0"` |
| `tune_card_contract.common_required_values.Next:numberShowInfo` | string: `"0"` |
| `tune_card_contract.common_required_values.Next:numberShowProcess` | string: `"0"` |
| `tune_card_contract.common_required_values.ParticleDecays:limitTau0` | string: `"on"` |
| `tune_card_contract.common_required_values.ParticleDecays:tau0Max` | string: `"0.01"` |
| `tune_card_contract.common_required_values.PhaseSpace:pTHatMin` | string: `"2."` |
| `tune_card_contract.common_required_values.Tune:pp` | string: `"14"` |
| `tune_card_contract.interpretation` | string: [fixed text or digest in source](../config/study.json) |
| `tunes` | array: `3 records` |
| `tunes[].card` | string: Record-specific value in the linked source |
| `tunes[].id` | string: Record-specific value in the linked source |
| `tunes[].name` | string: Record-specific value in the linked source |
| `version` | integer: `1` |

`activity.canonical_realized_nch_bounds` maps each tune and each listed class to integer `nch_low` and `nch_high` fields. These fixed compatibility bounds do not supply the current tune-local percentiles. The reducer derives current boundaries from the input activity distribution.
### data/campaign.json

| Field | Type and shipped value or source |
| --- | --- |
| `accepted_source.origin_algorithm` | string: [fixed text or digest in source](../data/campaign.json) |
| `accepted_source.producer_executable_sha256` | string: [fixed text or digest in source](../data/campaign.json) |
| `accepted_source.producer_repository_commit` | string: [fixed text or digest in source](../data/campaign.json) |
| `accepted_source.raw_manifest_schema` | string: [exact value](../data/campaign.json) |
| `accepted_source.raw_manifest_sha256` | string: [fixed text or digest in source](../data/campaign.json) |
| `accepted_source.raw_schema` | string: [exact value](../data/campaign.json) |
| `accepted_source.selector` | string: [fixed text or digest in source](../data/campaign.json) |
| `accepted_source.tune_cards.CLOSEPACKING.accepted_effective_sha256` | string: [fixed text or digest in source](../data/campaign.json) |
| `accepted_source.tune_cards.CLOSEPACKING.current_definition_sha256` | string: [fixed text or digest in source](../data/campaign.json) |
| `accepted_source.tune_cards.JUNCTIONS.accepted_effective_sha256` | string: [fixed text or digest in source](../data/campaign.json) |
| `accepted_source.tune_cards.JUNCTIONS.current_definition_sha256` | string: [fixed text or digest in source](../data/campaign.json) |
| `accepted_source.tune_cards.MONASH.accepted_effective_sha256` | string: [fixed text or digest in source](../data/campaign.json) |
| `accepted_source.tune_cards.MONASH.current_definition_sha256` | string: [fixed text or digest in source](../data/campaign.json) |
| `accepted_source.tune_difference_allowlist.schema` | string: [exact value](../data/campaign.json) |
| `accepted_source.tune_difference_allowlist.sha256` | string: [fixed text or digest in source](../data/campaign.json) |
| `attempt_evidence_inventory.file_count` | integer: `3127` |
| `attempt_evidence_inventory.sha256` | string: [fixed text or digest in source](../data/campaign.json) |
| `blocks.count` | integer: `10` |
| `blocks.logical_id_domain` | array: `[0,999]` |
| `blocks.logical_id_rule` | string: [exact value](../data/campaign.json) |
| `campaign` | string: `"HF_RUN3_V1"` |
| `current_interpretation_definitions.files` | array: `8 records` |
| `current_interpretation_definitions.files[].bytes` | integer: Record-specific value in the linked source |
| `current_interpretation_definitions.files[].path` | string: Record-specific value in the linked source |
| `current_interpretation_definitions.files[].sha256` | string: Record-specific value in the linked source |
| `current_interpretation_definitions.role` | string: [fixed text or digest in source](../data/campaign.json) |
| `held_attempt_policy` | string: [exact value](../data/campaign.json) |
| `logical_jobs_per_tune` | integer: `1000` |
| `physics.beam` | string: `"pp"` |
| `physics.hard_processes` | array: `["ccbar","bbbar"]` |
| `physics.heavy_hadron_decays` | string: `"disabled"` |
| `physics.pthat_min_gev` | number: `2.0` |
| `physics.sqrt_s_gev` | integer: `13600` |
| `runtime.pythia_version` | string: `"8.317"` |
| `schema` | string: [exact value](../data/campaign.json) |
| `seed.attempt_domain` | array: `[0,9]` |
| `seed.campaign_ordinal` | integer: `3` |
| `seed.formula` | string: [fixed text or digest in source](../data/campaign.json) |
| `seed.schema` | string: `"seed_derivation_v2"` |
| `seed.tune_ordinals.CLOSEPACKING` | integer: `2` |
| `seed.tune_ordinals.JUNCTIONS` | integer: `1` |
| `seed.tune_ordinals.MONASH` | integer: `0` |
| `successful_events_per_logical_job` | integer: `100000` |
| `successful_events_per_tune` | integer: `100000000` |
| `systematic_uncertainties` | string: `"disabled"` |
| `tune_order` | array: [exact value](../data/campaign.json) |
| `version` | integer: `1` |

### Fixture JSON

Fixture JSON files are test inputs, not user configuration. [The file reference](file-reference.md#fixtures) enumerates each path. Their schema groups are:

- `expected-sources.json`: ordered records with `source_id`, `tune`, `tune_ordinal`, `logical_id`, `block` and `events`.

- Query `analysis.json` and `layout.json`: construction models with the scientific and query keys above.

- Query `dictionary.json`: signed-PDG census body, schema and digest.

- Query `metadata.json`: input receipt, construction identities, retained-row facts and sparse facts.

- Query `manifest.json`: exact workspace member sizes, hashes and scientific-content digest.

- Pair-population `expected.json`: source and mutator hashes, expected signed pairs, origin identities and refusal text.

- Pair-population `positive-source.json`: analyzed PASS receipt, source membership, contract, ROOT bytes and provenance.

Do not edit immutable fixtures to make a failed verification pass. Construct a separate synthetic input when a new test requires different data.
