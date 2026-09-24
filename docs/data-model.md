# Data model

[Documentation index](../README.md#documentation)

## Object chain

| Object | Producer and input | Required interpretation |
| --- | --- | --- |
| Campaign record | Supplied JSON descriptor | Tune order, runtime, source factorization, seed and block rules |
| Raw ROOT | PYTHIA producer | Event vectors, scalar diagnostics and generator metadata |
| Analyzed shard | `analyze run` from accepted raw sources | Typed event and particle rows plus embedded contract and PASS receipt |
| Query workspace | `query build` from an analyzed pair | Exact support rows, sparse histograms, dictionary and manifest |
| Sharded collection | Collector or `collection create` | One checked locator across exact global source membership |
| Merged collection | `merge build` | Sparse partitions by tune and block, with original support-file references |
| Numerical package | `reduce run` | Typed ROOT values, covariance, missing states, provenance and exports |
| Figure directory | `plot render-cold` | PDFs, ROOT canvases, drawing record and exact manifest |
| Collaboration package | `package build` | Required numerical and figure files with relative locators |

## Source and event identities

A natural source key contains tune and logical job ID. An accepted attempt supplies its attempt ID and seed. Global source IDs enumerate the canonical manifest order. `source_id` columns inside individual ROOT shards remain local. Receipt mappings connect local IDs to the global domain.

The event identifier uses a 64-bit unsigned integer. Its fields contain 16 campaign bits, 2 tune bits, 14 logical-job bits, 12 attempt bits and 20 successful-event bits. The event index identifies successful events within the source. It is not a generator trial count.

The raw manifest stores one canonical JSON object per line. Its fields are `tune`, `logical_id`, `accepted_attempt`, `accepted_seed`, `block`, `successful_events`, `bytes`, `raw_sha256`, `raw_storage_key`, `validation_log_sha256` and `validation_receipt_sha256`. The validator requires exact membership, ordering and coherent seed/block identities.

The attempt CSV stores `tune`, `logical_id`, `attempt`, `seed`, `outcome`, `evidence_status` and `raw_storage_key`. Its join with accepted sources distinguishes job outcomes from generator event trials. The campaign also pins the evidence inventory and accepted producer identity.

## Raw and analyzed ROOT

Raw ROOT uses schema `hf_primary_ground_raw_v7`. The event tree contains heavy-particle vectors, ancestry, selected hard roots, activity and generator diagnostics. Additional objects record settings, particle stability, process counts, weights and source metadata. [validate_raw.cpp](../pipeline/generate/validate_raw.cpp) defines required branches and cross-checks.

The analyzer writes the following tables:

| Table | Meaning |
| --- | --- |
| `events` | Event ID, weight, both activity counts, process code, pTHat, hard scale and MPI count |
| `heavy` | Signed species, status, flags, heavy valence and particle four-vectors |
| `hard` | Selected hard-process roots |
| `ancestry`, `ancestry_mothers`, `heavy_mothers` | Complete retained mother relationships and ancestry identities |
| `origins`, `constituents` | Resolved or unresolved origin decisions for hadrons and heavy constituents |
| `triggers` | Structural trigger candidates and rejection masks |
| `pairs` | Ordered trigger–associate pairs, signs, kinematics and origin categories |
| `closure` | Full and visible heavy-flavour closure terms |
| `event_compatibility` | Event-level compatibility diagnostics |
| `event_ranges` | Contiguous source event-ID ranges |
| `sources`, `source_blocks`, `source_counts` | Local source identities, original blocks, event exposure and table counts |

The embedded `contract` object binds schemas, registries, metadata and scientific row digests. The adjacent JSON receipt binds physical ROOT SHA-256 and size to source and execution records. Verification checks natural keys, foreign keys, row order and scientific semantics.

The analyzer preserves the retained raw information, not the complete PYTHIA event record. It uses ZSTD level 5, bounded baskets and periodic event flushing. Its schema digest fixes branch names, types and order.

## Query workspace

A complete workspace has exactly these seven files:

| File | Contract |
| --- | --- |
| `query.root` | Support TTrees, five THnSparseD objects, `query_spec` and `metadata` |
| `query.tsv` | Exact construction specification for the native query executable |
| `analysis.json` | Construction-time downstream model |
| `layout.json` | Exact query schema |
| `dictionary.json` | Campaign-wide signed-PDG census and digest |
| `metadata.json` | Input receipt, identities, retained rows, sparse facts and pair-population proof |
| `manifest.json` | Exact file hashes, sizes and scientific-content identity |

A dictionary ordinal is meaningful only with its dictionary digest. Every query shard in a collection must use the same dictionary body. The builder refuses observed PDGs outside that dictionary.

Sparse contents use weighted additive counts. Sumw2 stores squared-weight accumulation. These stored sums do not replace the block jackknife covariance of nonlinear observables. The query retains both activity definitions simultaneously and has no sparse replica for each pT profile.

New workspaces use sparse-content digest v2, query metadata v4 and workspace manifest v3. The digest binds the declared axis order, names, titles, regular edges, endpoint policy, flow-bin policy, labels, entries, occupied coordinates, contents and Sumw2. Verification first compares each stored variable-edge axis with the declared layout. The digest does not use ROOT-computed underflow or overflow edge values.

Older metadata v3 workspaces keep their recorded v1 scientific identity. Verification accepts only the runtime v1 encoding or the defined ROOT 6.40 phi-overflow encoding, after the same exact semantic checks. It reports a separate v2 canonical comparison identity but does not replace or re-sign the recorded v1 identity. Collections cannot mix v1 and v2 query identities.

### Sparse axes

The following order is part of [query.json](../config/query.json):

- `sparse_activity`: `tune`, `block`, `a15_eta4`, `a15_eta1`.

- `sparse_triggers`: `tune`, `block`, `a15_eta4`, `a15_eta1`, `trigger_pdg`, `trigger_pt`, `trigger_eta`.

- `sparse_pairs`: `tune`, `block`, `a15_eta4`, `a15_eta1`, `trigger_pdg`, `associate_pdg`, `sign`, `trigger_pt`, `associate_pt`, `trigger_eta`, `associate_eta`, `dphi`, `deta`, `origin`, `category`.

- `sparse_kinematics`: `tune`, `block`, `a15_eta4`, `a15_eta1`, `pdg`, `pt`, `eta`, `phi`.

- `sparse_closure`: `tune`, `block`, `a15_eta4`, `a15_eta1`, `trigger_pdg`, `associate_pdg`, `trigger_pt`, `associate_pt`, `trigger_eta`, `associate_eta`, `dphi`, `category`.

Tune and block axes retain source membership. Species axes use the common signed-PDG dictionary. Kinematic axes use the normalized analysis model. Physical inclusive high endpoints occupy the final regular bin. The pT overflow remains distinct.

### Exact support rows

The support trees retain these columns. Their scalar C++ types appear in [row_schema.hpp](../pipeline/query/row_schema.hpp).

- `events`: `event_id`, `weight`, `a15_eta1`, `a15_eta4`, `process_code`, `pthat`, `hard_scale`, `n_mpi`.

- `heavy`: `event_id`, `heavy_index`, `pdg`, `status`, `final`, `selected`, `pair_eligible`, `category`, `nc`, `ncbar`, `nb`, `nbbar`, `qc`, `qb`, `pt`, `eta`, `rapidity`, `phi`.

- `triggers`: `event_id`, `heavy_index`, `sector`, `rejection_mask`.

- `pairs`: `event_id`, `trigger_heavy_index`, `associate_heavy_index`, `sign`, `dphi`, `deta`, `trigger_pt`, `associate_pt`, `a15_eta1`, `a15_eta4`, `associate_origin`, `associate_category`, `weight`.

- `origins`: `event_id`, `heavy_index`, `sector`, `origin`, `resolution`, `matched_hard`, `rejected_hard`, `depth`.

- `closure`: `event_id`, `trigger_heavy_index`, `associate_heavy_index`, `coefficient`, `visible`, `dense_category`.

- `constituents`: `event_id`, `heavy_index`, `signed_flavour`, `constituent_ordinal`, `origin`, `resolution`, `matched_hard`, `rejected_hard`, `depth`.

- `event_compatibility`: `event_id`, `diagnostic_id`, `cell_id`, `value`.

- `event_ranges`: `first_id`, `count`, `source_id`.

- `source_blocks`: `source_id`, `assignment_id`, `block`.

- `sources`: `source_id`, `tune`, `logical_id`, `attempt`, `events`, `attempted_events`, `sumw`, `sumw2`, `sumabsw`.

- `source_counts`: `source_id`, `family_id`, `rows`.

`n_mpi`, `process_code`, `pthat` and `hard_scale` remain event-level fields. The query omits some analyzed four-vector and ancestry information. Retain analyzed files when those details could support another measurement. Neither format contains individual light-pion momenta for a pion-spectrum-versus-activity measurement.

## Collection and merge

A collection index uses schema `hadronization_query_collection_v1`. Its `layout` is `SHARDED` or `MERGED`. Its state is `TEST_ONLY` or `EXTERNAL_ACCEPTANCE_REQUIRED`. The latter requests separate acceptance checks and is not itself an acceptance claim.

The index contains `analysis_sha256`, `layout_sha256`, `dictionary_body_sha256`, campaign and manifest identities, tune ordinals, block count, sources, shards and partitions. File facts contain an absolute path, byte count and SHA-256. Scientific identity excludes physical locators and physical checksums.

Each shard record binds query ROOT, metadata and workspace manifest to its source members and content identity. Duplicate natural or global source identities fail. The expected-source check refuses missing or foreign sources.

A merged collection contains one `tune-NN.root` file per tune. Each family has one object per original block, named `sparse_FAMILY__block_NN`. The implementation limits each serialized sparse object to 512 MiB. It never combines all blocks into one oversized object.

Merge receipts bind parent lineage, object counts, cell digests and resulting files. Exhaustive comparison checks the occupied domain, contents and Sumw2. It allows 1e-12 absolute or relative tolerance for summation order. It does not allow missing cells.

The merged index still points to original query workspaces. Reduction uses their exact support rows for event moments, origin diagnostics, boundary handling and natural-heavy accounting. Removal of query shards breaks this collection.

The numerical contract `projection_formulas_v4` checks all selected-state pairs against the retained event rows before reduction. This check uses heavy-flavour signs, structural triggers and the exact associate registry. It rejects missing pairs, duplicate pairs and inconsistent cached kinematics. It also counts eligible triggers with no accepted associate. The native run receipt binds the check to the collection digest and reports counts by source block and signed species.

The retained `pair_eligible` field records the input interpretation. It does not exclude selected states from formula contract `projection_formulas_v4`. Archived numerical contracts retain their original species scope.

## Numerical ROOT

`numerics.root` uses `hadronization_self_contained_typed_root_v4`. It contains a typed value graph named `nodes`, metadata named `v4_metadata` and direct TTrees. The reader compares each direct table with the typed graph. It rejects missing objects, extra objects and duplicate key cycles.

The graph retains the complete numerical request and result. It includes point keys, physical axes, units, resolved selections, boundaries, source identities, deletion families and provenance. It needs no input collection to interpret stored numbers.

Direct tables use signed or unsigned 64-bit integers, binary64 numbers, booleans and strings. The table schema below uses `i`, `u`, `d`, `b` and `s` respectively. The type code follows each field name.

- `bindings`: `schema:s`, `request_sha256:s`, `science_content_sha256:s`, `collection_kind:s`, `collection_state:s`, `collection_index_sha256:s`, `collection_index_bytes:u`, `collection_scientific_identity_sha256:s`, `member_files_sha256:s`, `source_members_sha256:s`, `admission_qualification:s`, `admission_expected_sources_sha256:s`, `admission_natural_members_sha256:s`, `campaign_scope:s`, `campaign_attempts:u`, `campaign_successful_events:u`.

- `points`: `index:u`, `semantic_id:s`, `point_key_sha256:s`, `role:s`, `tune:s`, `quantity:s`, `component:s`, `axis:s`, `bin:i`, `units:s`, `center_status:s`, `center_present:b`, `center:d`, `uncertainty_status:s`, `variance_present:b`, `variance:d`, `error_present:b`, `error:d`.

- `event_moments`: `tune:s`, `block:u`, `source_members_sha256:s`, `scope:s`, `events:u`, `sumw:d`, `sumw2:d`, `sumabsw:d`, `event_weight_terms:u`, `content_sha256:s`.

- `support_diagnostics`: `tune:s`, `block:u`, `event_moments_sha256:s`, `natural_final_hadrons:u`, `natural_final_weighted_sum:d`, `charm_constituents:u`, `charm_constituent_weighted_sum:d`, `beauty_constituents:u`, `beauty_constituent_weighted_sum:d`, `strict_selected_final_hadrons:u`, `strict_selected_final_weighted_sum:d`, `pthat_sum:d`, `hard_scale_sum:d`, `content_sha256:s`.

- `diagnostic_activity`: `tune:s`, `block:u`, `activity_bin:u`, `events:u`.

- `diagnostic_n_mpi`: `tune:s`, `block:u`, `n_mpi:u`, `events:u`.

- `diagnostic_process`: `tune:s`, `block:u`, `process_code:i`, `events:u`.

- `diagnostic_origin`: `tune:s`, `block:u`, `origin:i`, `category:i`, `sign:i`, `rows:u`, `weighted_sum:d`.

- `diagnostic_closure`: `tune:s`, `block:u`, `category:i`, `visible:b`, `coefficient:i`, `rows:u`, `weighted_sum:d`.

- `block_values`: `point:u`, `tune:s`, `block:u`, `events:u`, `sumw:d`, `sumw2:d`, `sumabsw:d`, `event_weight_terms:u`, `event_moments_sha256:s`.

- `block_components`: `point:u`, `tune:s`, `block:u`, `component_id:s`, `value:d`.

- `denominator_parents`: `point:u`, `ordinal:u`, `natural_key:s`, `status:s`, `retained_after_algebra:b`, `pooled_present:b`, `pooled_value:d`, `policy_id:s`.

- `denominator_deletions`: `point:u`, `parent_ordinal:u`, `block:u`, `status:s`.

- `covariance_points`: `group_id:s`, `slot:u`, `point:u`, `valid:b`, `units:s`.

- `covariance_factors`: `group_id:s`, `slot:u`, `tune:s`, `source_family_sha256:s`, `block:u`, `finite:b`, `valid:b`, `leaf:d`, `leave_mean:d`, `centered_factor:d`.

- `class_boundaries`: `tune:s`, `activity:s`, `class_id:i`, `low:i`, `high:i`, `events:u`, `event_weight:d`, `empty:b`, `status:s`, `content_sha256:s`.

- `class_boundary_deletions`: `tune:s`, `class_id:i`, `omitted_block:u`, `source_family_sha256:s`, `status:s`, `low_present:b`, `low:i`, `high_present:b`, `high:i`, `empty:b`, `weight_present:b`, `weighted_measure:d`, `content_sha256:s`.

- `collection_members`: `file_id:s`, `role:s`, `shard_present:b`, `shard_ordinal:u`, `tune_present:b`, `tune:s`, `sha256:s`, `bytes:u`.

- `campaign_tunes`: `tune:s`, `sources:u`, `successful_events:u`, `submitted_attempts:u`, `accepted_attempts:u`, `discarded_attempts:u`.

- `campaign_trials`: `tune:s`, `scope:s`, `count_present:b`, `count:u`, `status:s`, `reason_codes:s`.

- `campaign_attempt_evidence`: `outcome:s`, `evidence_status:s`, `count:u`.

- `selected_tune_exposure`: `tune:s`, `successful_events:u`.

- `materialization`: `point:u`, `status:s`, `reason_codes:s`.

- `g9_science`: `metadata_json:s`, `metadata_sha256:s`.

The literal `g9_science` table contains the signed heavy-hadron spectrum selection and normalization. `covariance_points` maps factor slots to numerical points. `covariance_factors` retains tune, original block, family digest, deletion value, mean and centered factor.

A numeric branch can contain zero when its corresponding presence flag is false. Always inspect `center_present`, `variance_present`, `error_present` or the relevant field-specific flag. A stored placeholder is not an observed zero.

## Status semantics

| Field or state | Meaning |
| --- | --- |
| Materialization `PRESENT` | The requested point belongs to the materialized domain |
| `NOT_MATERIALIZED` | No result exists for that requested domain element |
| `UNSUPPORTED_QUERY` | The requested point is outside the supported query contract |
| Center `AVAILABLE` | A finite center passed its required checks |
| `UNDEFINED` | The estimator cannot provide a center |
| `UNSTABLE_DENOMINATOR` | A denominator fails a required stability condition. A pooled center can still exist. |
| Uncertainty `AVAILABLE` | Finite variance and standard error passed prerequisites |
| `AVAILABLE_ZERO_DISPERSION` | Valid deletion values have exactly zero dispersion |
| `WITHHELD_UNCERTAINTY` | A center can remain available, but no usable uncertainty is supplied |
| `EMPTY_CLASS` | The selected integer interval contains no usable class exposure |
| `INCOMPLETE_BLOCK_COVERAGE` | Required original source-block exposure is missing |
| `CLASS_BOUNDARY_UNSTABLE` | Deletion changes a tune-local integer boundary |
| `CLASS_BOUNDARY_UNRESOLVED` | A boundary or its statistical margin cannot be resolved |
| Covariance `valid_mask` | Identifies points with usable joint covariance |
| `PARTIAL_SAMPLE` | The result does not establish full accepted-campaign closure |

Reason codes explain missing or withheld quantities. Finite deletion values can remain stored when covariance validity is false. Consumers must not reinterpret those values as valid uncertainty factors.

## Exports and figures

CSV exports include point values, missing states and accounting. Binary64 fields use hexadecimal floating-point strings for exact round trips. Use Python `float.fromhex` to decode them. Unavailable values use empty fields, not numeric zero.

The literal filenames `t1.csv` and `t1.tex` contain natural-heavy accounting. TeX tables preserve integer counts and carry missing states. `overleaf-preamble.tex`, `overleaf-tables.tex` and the table check source support document assembly.

Figure directories contain PDFs, `canvases.root`, `drawing-record.tsv.gz` and `manifest.json`. Canvas graph identities retain point semantics and statuses. The drawing record contains coordinates, styles, panel geometry and display decisions. It does not define scientific formulas.

The final package contains `numerical/`, `figures/`, the selected `config/*.json` and a root manifest. Its exact file set excludes computation scratch and the native execution binary. The numerical report still records external execution references.

## Lifetimes and retention

| Material | Lifetime and reason |
| --- | --- |
| Raw ROOT and independent inventory | Preserve when generator diagnostics or information omitted downstream remain useful |
| Analyzed ROOT and PASS receipts | Preserve four-vectors, ancestry and accepted input authority beyond the query subset |
| Query workspaces | Required for exact support and for current merged-collection reduction |
| Merged ROOT, index and merge receipts | Required for sparse projection and parent verification |
| External acceptance pins and site records | Preserve separately from mutable attempts and adjacent manifests |
| Numerical ROOT, reports, exports and manifests | Preserve with every scientific result |
| Canvases, PDFs, drawing record and selected configuration | Preserve the exact scientific presentation |
| Build pack and execution receipts | Preserve while execution provenance or restart depends on them |
| Build caches and temporary scratch | Reconstructible after successful output verification and retention review |
| Failed attempts and ambiguous publication stages | Preserve until failure and publication state are resolved |

## Publication behavior

Analysis publishes files with exclusive hard links after validation. Query and package publication use a no-replace directory operation. Darwin and Linux have separate implementations. The Linux fallback requires owned, private staging and exclusive destination reservation.

The publisher checks path confinement, file types, symlinks, hard links and filesystem boundaries where its contract requires them. It hashes readback after publication. A collision or ambiguous result fails closed. No storage protocol inherits POSIX guarantees without a successful site probe.
