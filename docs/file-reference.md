# File reference

[Documentation index](../README.md#documentation)

This inventory identifies every tracked file. The release includes generated scientific products described by the [data model](data-model.md). Paths below link to their exact repository contents.

## Entry points and metadata

| Path | Caller or reader | Role or output |
| --- | --- | --- |
| [.gitattributes](../.gitattributes) | Git | Preserves checksum-bound result bytes and recognizes CSV record endings. |
| [.gitignore](../.gitignore) | Git | Excludes local site configuration, bulk output, caches and build residue. |
| [CITATION.cff](../CITATION.cff) | Citation software and readers | Supplied software title, authors and citation message. |
| [README.md](../README.md) | Repository readers | Purpose, entry commands, limits and guide navigation. |
| [hadronization](../hadronization) | User command line | Dispatches stages, reports environment, runs tests and lists or applies cleanup. |
| [setup.sh](../setup.sh) | Bash or zsh | Resolves the common runtime and exports its environment. |

## Public documentation

| Path | Caller or reader | Role or output |
| --- | --- | --- |
| [docs/atlas.html](../docs/atlas.html) | Researchers using a web browser | Self-contained scientific guide, command reference, worked examples and searchable file dependencies. |
| [docs/cli-reference.md](../docs/cli-reference.md) | Repository readers | All public commands, parser options and side effects. |
| [docs/configuration.md](../docs/configuration.md) | Repository readers | Scientific, presentation, runtime and resource settings. |
| [docs/data-model.md](../docs/data-model.md) | Repository readers | ROOT structures, identities, statuses and retention. |
| [docs/file-reference.md](../docs/file-reference.md) | Repository readers | Complete tracked file inventory and consumer mapping. |
| [docs/installation.md](../docs/installation.md) | Repository readers | Dependencies, environment and first checks. |
| [docs/reproducibility.md](../docs/reproducibility.md) | Repository readers | Independent hashes, cold verification and output copying. |
| [docs/science.md](../docs/science.md) | Repository readers | Sample, selections, formulas and statistical interpretation. |
| [docs/workflow.md](../docs/workflow.md) | Repository readers | Ordered execution, required external inputs and restart rules. |

## Configuration

| Path | Caller or reader | Role or output |
| --- | --- | --- |
| [config/analysis.json](../config/analysis.json) | Query model and reducer | Downstream selections, axes, registry references, classes and statistical policy. |
| [config/plot-all-tune.json](../config/plot-all-tune.json) | Renderer | All-tune correlation presentation with comparison panels. |
| [config/plot-dplus.json](../config/plot-dplus.json) | Renderer | Presentation for the explicit D+ numerical recipe. |
| [config/plot.json](../config/plot.json) | Renderer | D0 default figure selection, layout and identities. |
| [config/query.json](../config/query.json) | Query builder and verifier | Exact support-tree columns and sparse-axis families. |
| [config/site.example.conf](../config/site.example.conf) | User copying site settings | Example runtime, storage and submission paths. |
| [config/study.json](../config/study.json) | Generator contract and raw validators | Checksum-bound raw compatibility and signed selected-state registry. |
| [config/tunes/close_packing.cmnd](../config/tunes/close_packing.cmnd) | Generator | Complete CLOSEPACKING PYTHIA command card. |
| [config/tunes/junctions.cmnd](../config/tunes/junctions.cmnd) | Generator | Complete JUNCTIONS PYTHIA command card. |
| [config/tunes/monash.cmnd](../config/tunes/monash.cmnd) | Generator | Complete MONASH PYTHIA command card. |

## Public data

| Path | Caller or reader | Role or output |
| --- | --- | --- |
| [data/README.md](../data/README.md) | Data users | Inventory scope, acquisition requirements and storage policy. |
| [data/attempts.csv](../data/attempts.csv) | Planner and accounting | Ordered job-attempt outcomes and evidence classifications. |
| [data/campaign.json](../data/campaign.json) | Planner, analyzer and accounting | Accepted campaign identity, source factorization and provenance. |
| [data/raw_manifest.jsonl](../data/raw_manifest.jsonl) | Source validators | Canonical accepted raw-file membership, hashes, sizes and original blocks. |

## Generation

| Path | Caller or reader | Role or output |
| --- | --- | --- |
| [pipeline/generate/physics.hpp](../pipeline/generate/physics.hpp) | Producer, raw validator and analyzer | Particle valence, status, origin, activity, seed and event-ID rules. |
| [pipeline/generate/producer.cpp](../pipeline/generate/producer.cpp) | Reserved generation worker | Runs PYTHIA and writes raw event, stability, settings and accounting objects. |
| [pipeline/generate/runtime.py](../pipeline/generate/runtime.py) | Setup, builders and worker wrappers | Resolves and checks compiler, ROOT and PYTHIA installations. |
| [pipeline/generate/sha256.hpp](../pipeline/generate/sha256.hpp) | Native producer and analyzer | Streaming SHA-256 for immutable metadata and file digests. |
| [pipeline/generate/study_contract.hpp](../pipeline/generate/study_contract.hpp) | Native generation and analysis | Generated signed-state registry and raw compatibility constants. |
| [pipeline/generate/study_contract.py](../pipeline/generate/study_contract.py) | Header generation and check command | Validates study definitions and generates the exact C++ contract. |
| [pipeline/generate/submit.py](../pipeline/generate/submit.py) | Generation CLI | Plans, builds, reserves, submits and runs generation attempts. |
| [pipeline/generate/validate_raw.cpp](../pipeline/generate/validate_raw.cpp) | Generation worker and analyzer | Checks raw schema, source authority, kinematics, ancestry and metadata. |

## Analysis

| Path | Caller or reader | Role or output |
| --- | --- | --- |
| [pipeline/analyze/analyze.cpp](../pipeline/analyze/analyze.cpp) | Analysis wrapper | Writes, inspects and verifies typed analyzed rows and embedded contracts. |
| [pipeline/analyze/run.py](../pipeline/analyze/run.py) | Analysis CLI and query support | Validates campaign inputs, plans shards, builds native tools and manages receipts. |

## Query and storage

| Path | Caller or reader | Role or output |
| --- | --- | --- |
| [pipeline/query/collection.py](../pipeline/query/collection.py) | Collection CLI, merge and reduction | Checked collection locator, source admission, sparse iteration and exact support access. |
| [pipeline/query/condor.py](../pipeline/query/condor.py) | Condor CLI and generated wrappers | Prepares immutable bundles, runs attempts and collects exact accepted closure. |
| [pipeline/query/merge.py](../pipeline/query/merge.py) | Merge CLI | Writes bounded sparse objects by original block in one file per tune. |
| [pipeline/query/merge_sparse.hpp](../pipeline/query/merge_sparse.hpp) | PyROOT merge helper | Native cell addition and serialized-size preflight. |
| [pipeline/query/model.py](../pipeline/query/model.py) | Query and reduction | Normalizes the scientific request and validates profile, registry and compatibility rules. |
| [pipeline/query/publication.py](../pipeline/query/publication.py) | Query, bundle and package writers | No-replace publication, Linux reservation fallback and readback checks. |
| [pipeline/query/query.cpp](../pipeline/query/query.cpp) | Query wrapper | Builds support trees and sparse families and verifies complete pair populations. |
| [pipeline/query/row_schema.hpp](../pipeline/query/row_schema.hpp) | Native query executable | Exact retained scalar branch types and schema macros. |
| [pipeline/query/run.py](../pipeline/query/run.py) | Query CLI and collection modules | Build packs, dictionary census, query construction and exact verification. |
| [pipeline/query/selection.hpp](../pipeline/query/selection.hpp) | Query and sparse readers | Common endpoint-inclusive kinematic predicates. |
| [pipeline/query/site_probe.py](../pipeline/query/site_probe.py) | Execute-node canary | Measures runtime, input readability, ClassAds and storage publication semantics. |
| [pipeline/query/sparse.hpp](../pipeline/query/sparse.hpp) | Native query executable | Sparse construction, axes, signed dictionaries and flow behavior. |
| [pipeline/query/support.py](../pipeline/query/support.py) | Query modules | Shared JSON, hashing, path and analyzer-loading helpers. |

## Numerical reduction

| Path | Caller or reader | Role or output |
| --- | --- | --- |
| [pipeline/reduce/accounting.py](../pipeline/reduce/accounting.py) | Reducer | Joins campaign, raw manifest and attempts into source and trial accounting. |
| [pipeline/reduce/archive.py](../pipeline/reduce/archive.py) | Cold renderer and package reader | Public import facade for the numerical ROOT reader. |
| [pipeline/reduce/archive_v4.py](../pipeline/reduce/archive_v4.py) | Numerical writer and reader | Writes and checks direct ROOT tables, typed graph and CSV/TeX exports. |
| [pipeline/reduce/native.py](../pipeline/reduce/native.py) | Native runner | Reads sparse additive primitives and exact support through checked collection APIs. |
| [pipeline/reduce/native_engine.cpp](../pipeline/reduce/native_engine.cpp) | Native runner | Evaluates requested observables and emits values, deletion factors and primitive receipts. |
| [pipeline/reduce/native_runner.py](../pipeline/reduce/native_runner.py) | Public reducer | Builds the estimator, maps exact inputs and checks native output streams. |
| [pipeline/reduce/native_v4.py](../pipeline/reduce/native_v4.py) | Numerical result assembly | Binds source files, admissions, accounting, event moments and primitive routes. |
| [pipeline/reduce/native_v4_result.py](../pipeline/reduce/native_v4_result.py) | Public reducer | Assembles native values and factors into the typed result contract. |
| [pipeline/reduce/projection.py](../pipeline/reduce/projection.py) | Reducer and renderer reader | Typed numerical schemas, natural point keys, request construction and result validation. |
| [pipeline/reduce/public_v4.py](../pipeline/reduce/public_v4.py) | Reduce CLI | Admits complete inputs, runs native reduction and verifies producer or portable packages. |
| [pipeline/reduce/statistics.hpp](../pipeline/reduce/statistics.hpp) | Native estimator | Pooled ratios, denominator checks, class-boundary resolution and jackknife covariance. |
| [pipeline/reduce/support_scan.cpp](../pipeline/reduce/support_scan.cpp) | Native primitive reader | One-pass support scan for event moments, origins, closure and natural-heavy counts. |
| [pipeline/reduce/typed_nodes.py](../pipeline/reduce/typed_nodes.py) | ROOT archive writer | Encodes a deduplicated typed value graph. |

## Figures and package

| Path | Caller or reader | Role or output |
| --- | --- | --- |
| [pipeline/plot/render.cpp](../pipeline/plot/render.cpp) | Plot wrapper | Draws ROOT canvases and PDFs and checks reopened graph, pad, axis and text semantics. |
| [pipeline/plot/run.py](../pipeline/plot/run.py) | Plot CLI and package verification | Checks numerical ROOT, builds presentation plans and verifies figure files and canvases. |
| [pipeline/release.py](../pipeline/release.py) | Package CLI | Assembles and verifies the exact relative numerical and figure file set. |

## Tests

| Path | Caller or reader | Role or output |
| --- | --- | --- |
| [tests/helpers.py](../tests/helpers.py) | Test modules | Repository-relative imports and shared source references. |
| [tests/test_analysis.py](../tests/test_analysis.py) | Development suite | Analyzed schema, planning, identity, regrouping, publication and row corruption. |
| [tests/test_campaign.py](../tests/test_campaign.py) | Development suite | Canonical manifest and attempt joins, domain ordering and definition hashes. |
| [tests/test_cli.py](../tests/test_cli.py) | Development suite | Public dispatch, environment setup, cleanup confinement and cold imports. |
| [tests/test_generator.py](../tests/test_generator.py) | Development suite | Native particle rules, seed/card materialization and optional producer linkage. |
| [tests/test_hygiene.py](../tests/test_hygiene.py) | Development suite | Tracked topology, permitted file families, include resolution and output exclusions. |
| [tests/test_nonzero_chain_fixture.py](../tests/test_nonzero_chain_fixture.py) | Development suite | Explicit fresh destinations for synthetic builder and oracle. |
| [tests/test_plot_cold.py](../tests/test_plot_cold.py) | Development suite | Numerical-only drawing, signed labels, statuses, axes, inset, page layouts and canvas behavior. |
| [tests/test_projection_interface.py](../tests/test_projection_interface.py) | Development suite | Exact point domains, request identity, source routes and independent validity states. |
| [tests/test_public_v4_cli.py](../tests/test_public_v4_cli.py) | Development suite | External-fixture public numerical round trips, selection changes and immutable outputs. |
| [tests/test_publication.py](../tests/test_publication.py) | Development suite | No-replace behavior, contention, interruption, unsafe paths and readback failures. |
| [tests/test_query.py](../tests/test_query.py) | Development suite | Retained rows, endpoint predicates, dictionary consistency, pair completeness and sparse verification. |
| [tests/test_query_collection.py](../tests/test_query_collection.py) | Development suite | Source closure, physical merge equality, block partitions, serialization bounds and relocation. |
| [tests/test_query_condor.py](../tests/test_query_condor.py) | Development suite | Site admission, sealed bundles, retries, classified failures and exact collection. |
| [tests/test_query_model.py](../tests/test_query_model.py) | Development suite | D0/D+ recipes, aligned rectangular minima and compatible post-query configuration. |
| [tests/test_release.py](../tests/test_release.py) | Development suite | Selected presentation configuration, package hashes, source binding and publication failure. |
| [tests/test_sparse_lifetime.py](../tests/test_sparse_lifetime.py) | Development suite | PyROOT ownership and sparse allocation lifetime. |
| [tests/test_statistics_accounting.py](../tests/test_statistics_accounting.py) | Development suite | Accepted-source and job-attempt accounting. |
| [tests/test_statistics_compiler.py](../tests/test_statistics_compiler.py) | Development suite | Configured compiler selection and build identity. |
| [tests/test_statistics_native.py](../tests/test_statistics_native.py) | Development suite | Sparse primitives, exact support, no-floor spectra and source-block exposure. |
| [tests/test_statistics_native_engine.py](../tests/test_statistics_native_engine.py) | Development suite | Native signs, zero-associate denominators, class reclassification and independent-tune covariance. |
| [tests/test_statistics_reclassification.py](../tests/test_statistics_reclassification.py) | Development suite | Boundary and membership recomputation after block deletion. |
| [tests/test_statistics_runner.py](../tests/test_statistics_runner.py) | Development suite | Bound request transport and complete primitive, denominator and deletion streams. |
| [tests/test_statistics_v4.py](../tests/test_statistics_v4.py) | Development suite | Typed ROOT, validity masks, shared-reference factors, accounting and source closure. |
| [tests/test_study.py](../tests/test_study.py) | Development suite | Study schema, signed registry, generated header and exact definition consistency. |
| [tests/test_submission.py](../tests/test_submission.py) | Development suite | Raw validation, vector and metadata corruption, reservations, no-overwrite and scheduler contracts. |
| [tests/test_tunes.py](../tests/test_tunes.py) | Development suite | Exact tune-card hashes, common settings and permitted bundle differences. |

## Fixtures

Every fixture path appears below. Each query workspace follows the same seven-file schema. These files contain synthetic data and cannot establish research-sample closure.

| Path | Caller or reader | Role or output |
| --- | --- | --- |
| [tests/fixtures/nonzero_chain_v22/build.py](../tests/fixtures/nonzero_chain_v22/build.py) | Explicit synthetic example | Constructs nonzero raw fixtures, analyzed rows, queries and a merged test collection. |
| [tests/fixtures/nonzero_chain_v22/mutate_merge.cpp](../tests/fixtures/nonzero_chain_v22/mutate_merge.cpp) | Development suite | Makes isolated sparse coordinate, content, Sumw2 and entry-count mutants for oracle refusal tests. |
| [tests/fixtures/nonzero_chain_v22/oracle.py](../tests/fixtures/nonzero_chain_v22/oracle.py) | Explicit synthetic check | Checks synthetic rows, classes and the complete block-partitioned sparse merge. |
| [tests/fixtures/query_multitune/TEST_ONLY.md](../tests/fixtures/query_multitune/TEST_ONLY.md) | Fixture readers | Explains synthetic scope and input-version limits. |
| [tests/fixtures/query_multitune/expected-sources.json](../tests/fixtures/query_multitune/expected-sources.json) | Collection tests | Exact synthetic global source membership and original blocks. |
| [tests/fixtures/query_multitune/queries/shard-0000/analysis.json](../tests/fixtures/query_multitune/queries/shard-0000/analysis.json) | Query verifier | Immutable construction-time analysis contract. |
| [tests/fixtures/query_multitune/queries/shard-0000/dictionary.json](../tests/fixtures/query_multitune/queries/shard-0000/dictionary.json) | Query verifier | Shared signed-PDG census and digest. |
| [tests/fixtures/query_multitune/queries/shard-0000/layout.json](../tests/fixtures/query_multitune/queries/shard-0000/layout.json) | Query verifier | Exact sparse and support-tree layout. |
| [tests/fixtures/query_multitune/queries/shard-0000/manifest.json](../tests/fixtures/query_multitune/queries/shard-0000/manifest.json) | Query verifier | Exact fixture file facts and scientific-content identity. |
| [tests/fixtures/query_multitune/queries/shard-0000/metadata.json](../tests/fixtures/query_multitune/queries/shard-0000/metadata.json) | Query verifier | Embedded analyzed receipt, construction facts and scientific bindings. |
| [tests/fixtures/query_multitune/queries/shard-0000/query.root](../tests/fixtures/query_multitune/queries/shard-0000/query.root) | Collection and sparse tests | Synthetic support TTrees and five sparse families. |
| [tests/fixtures/query_multitune/queries/shard-0000/query.tsv](../tests/fixtures/query_multitune/queries/shard-0000/query.tsv) | Query verifier | Exact native construction specification. |
| [tests/fixtures/query_multitune/queries/shard-0001/analysis.json](../tests/fixtures/query_multitune/queries/shard-0001/analysis.json) | Query verifier | Immutable construction-time analysis contract. |
| [tests/fixtures/query_multitune/queries/shard-0001/dictionary.json](../tests/fixtures/query_multitune/queries/shard-0001/dictionary.json) | Query verifier | Shared signed-PDG census and digest. |
| [tests/fixtures/query_multitune/queries/shard-0001/layout.json](../tests/fixtures/query_multitune/queries/shard-0001/layout.json) | Query verifier | Exact sparse and support-tree layout. |
| [tests/fixtures/query_multitune/queries/shard-0001/manifest.json](../tests/fixtures/query_multitune/queries/shard-0001/manifest.json) | Query verifier | Exact fixture file facts and scientific-content identity. |
| [tests/fixtures/query_multitune/queries/shard-0001/metadata.json](../tests/fixtures/query_multitune/queries/shard-0001/metadata.json) | Query verifier | Embedded analyzed receipt, construction facts and scientific bindings. |
| [tests/fixtures/query_multitune/queries/shard-0001/query.root](../tests/fixtures/query_multitune/queries/shard-0001/query.root) | Collection and sparse tests | Synthetic support TTrees and five sparse families. |
| [tests/fixtures/query_multitune/queries/shard-0001/query.tsv](../tests/fixtures/query_multitune/queries/shard-0001/query.tsv) | Query verifier | Exact native construction specification. |
| [tests/fixtures/query_multitune/queries/shard-0002/analysis.json](../tests/fixtures/query_multitune/queries/shard-0002/analysis.json) | Query verifier | Immutable construction-time analysis contract. |
| [tests/fixtures/query_multitune/queries/shard-0002/dictionary.json](../tests/fixtures/query_multitune/queries/shard-0002/dictionary.json) | Query verifier | Shared signed-PDG census and digest. |
| [tests/fixtures/query_multitune/queries/shard-0002/layout.json](../tests/fixtures/query_multitune/queries/shard-0002/layout.json) | Query verifier | Exact sparse and support-tree layout. |
| [tests/fixtures/query_multitune/queries/shard-0002/manifest.json](../tests/fixtures/query_multitune/queries/shard-0002/manifest.json) | Query verifier | Exact fixture file facts and scientific-content identity. |
| [tests/fixtures/query_multitune/queries/shard-0002/metadata.json](../tests/fixtures/query_multitune/queries/shard-0002/metadata.json) | Query verifier | Embedded analyzed receipt, construction facts and scientific bindings. |
| [tests/fixtures/query_multitune/queries/shard-0002/query.root](../tests/fixtures/query_multitune/queries/shard-0002/query.root) | Collection and sparse tests | Synthetic support TTrees and five sparse families. |
| [tests/fixtures/query_multitune/queries/shard-0002/query.tsv](../tests/fixtures/query_multitune/queries/shard-0002/query.tsv) | Query verifier | Exact native construction specification. |
| [tests/fixtures/query_pair_population/corrupt_origin.cpp](../tests/fixtures/query_pair_population/corrupt_origin.cpp) | Pair-population tests | Creates malformed mandatory origin provenance. |
| [tests/fixtures/query_pair_population/dictionary.json](../tests/fixtures/query_pair_population/dictionary.json) | Query verifier | Shared signed-PDG census and digest. |
| [tests/fixtures/query_pair_population/expected.json](../tests/fixtures/query_pair_population/expected.json) | Pair-population tests | Pins mutators and controls and defines expected signs and refusal messages. |
| [tests/fixtures/query_pair_population/make_positive_ss_unresolved.cpp](../tests/fixtures/query_pair_population/make_positive_ss_unresolved.cpp) | Pair-population tests | Creates a same-sign unresolved-origin control pair. |
| [tests/fixtures/query_pair_population/omit_pair.cpp](../tests/fixtures/query_pair_population/omit_pair.cpp) | Pair-population tests | Removes a required in-domain pair. |
| [tests/fixtures/query_pair_population/positive-source.json](../tests/fixtures/query_pair_population/positive-source.json) | Pair-population tests | PASS receipt for the synthetic analyzed ROOT control. |
| [tests/fixtures/query_pair_population/positive-source.root](../tests/fixtures/query_pair_population/positive-source.root) | Pair-population tests | Synthetic analyzed rows for pair-completeness checks. |
| [tests/fixtures/query_pair_population/selected_hard_noncompanion.cpp](../tests/fixtures/query_pair_population/selected_hard_noncompanion.cpp) | Pair-population tests | Creates an invalid selected-hard companion assignment. |

## Distributed scientific results and data access

The package manifest binds every numerical and figure file. These groups identify each tracked artifact and its purpose.

### `data`

Data users read these inventories. The downloader consumes the transfer manifest.

| File | Purpose |
| --- | --- |
| [analyzed-inventory.json](../data/analyzed-inventory.json) | All 323 accepted analyzed ROOT files and receipts with their physical identities. |
| [bulk-storage.json](../data/bulk-storage.json) | Bulk storage locators, checksum inventories, access and retention policy. |
| [fetch-merged.py](../data/fetch-merged.py) | Download, verify and concatenate byte parts without repeating the sparse merge. |
| [merged-download.json](../data/merged-download.json) | Complete ROOT and transfer-part identities, tune mapping and GitHub asset locations. |

### `data/merged`

Collection and projection users read these original merge records and the signed-PDG dictionary.

| File | Purpose |
| --- | --- |
| [dictionary.json](../data/merged/dictionary.json) | Campaign-wide signed-PDG ordinal dictionary and census binding. |
| [index.json](../data/merged/index.json) | Original collection identity, sources, query support locators and merged sparse objects. |
| [merge-receipt.json](../data/merged/merge-receipt.json) | Parent and merged collection hashes plus partition identities. |
| [merge-verification.json](../data/merged/merge-verification.json) | Recorded full sparse-domain and parent-lineage verification. |

### `data/results`

The package verifier reads the complete relative fileset.

| File | Purpose |
| --- | --- |
| [manifest.json](../data/results/manifest.json) | Exact relative fileset, hashes, numerical identity and selected presentation. |

### `data/results/config`

The renderer and package verifier read the selected display settings.

| File | Purpose |
| --- | --- |
| [plot.json](../data/results/config/plot.json) | Frozen display configuration for the distributed figures. |

### `data/results/figures`

Readers use the PDFs and canvases. The figure verifier checks the manifest and drawing record.

| File | Purpose |
| --- | --- |
| [G9_-4122_eta.pdf](../data/results/figures/G9_-4122_eta.pdf) | Signed heavy-hadron eta spectrum for PDG -4122. |
| [G9_-4122_phi.pdf](../data/results/figures/G9_-4122_phi.pdf) | Signed heavy-hadron phi spectrum for PDG -4122. |
| [G9_-4122_pt.pdf](../data/results/figures/G9_-4122_pt.pdf) | Signed heavy-hadron pt spectrum for PDG -4122. |
| [G9_-421_eta.pdf](../data/results/figures/G9_-421_eta.pdf) | Signed heavy-hadron eta spectrum for PDG -421. |
| [G9_-421_phi.pdf](../data/results/figures/G9_-421_phi.pdf) | Signed heavy-hadron phi spectrum for PDG -421. |
| [G9_-421_pt.pdf](../data/results/figures/G9_-421_pt.pdf) | Signed heavy-hadron pt spectrum for PDG -421. |
| [G9_-5122_eta.pdf](../data/results/figures/G9_-5122_eta.pdf) | Signed heavy-hadron eta spectrum for PDG -5122. |
| [G9_-5122_phi.pdf](../data/results/figures/G9_-5122_phi.pdf) | Signed heavy-hadron phi spectrum for PDG -5122. |
| [G9_-5122_pt.pdf](../data/results/figures/G9_-5122_pt.pdf) | Signed heavy-hadron pt spectrum for PDG -5122. |
| [G9_-5212_eta.pdf](../data/results/figures/G9_-5212_eta.pdf) | Signed heavy-hadron eta spectrum for PDG -5212. |
| [G9_-5212_phi.pdf](../data/results/figures/G9_-5212_phi.pdf) | Signed heavy-hadron phi spectrum for PDG -5212. |
| [G9_-5212_pt.pdf](../data/results/figures/G9_-5212_pt.pdf) | Signed heavy-hadron pt spectrum for PDG -5212. |
| [G9_-521_eta.pdf](../data/results/figures/G9_-521_eta.pdf) | Signed heavy-hadron eta spectrum for PDG -521. |
| [G9_-521_phi.pdf](../data/results/figures/G9_-521_phi.pdf) | Signed heavy-hadron phi spectrum for PDG -521. |
| [G9_-521_pt.pdf](../data/results/figures/G9_-521_pt.pdf) | Signed heavy-hadron pt spectrum for PDG -521. |
| [G9_4122_eta.pdf](../data/results/figures/G9_4122_eta.pdf) | Signed heavy-hadron eta spectrum for PDG 4122. |
| [G9_4122_phi.pdf](../data/results/figures/G9_4122_phi.pdf) | Signed heavy-hadron phi spectrum for PDG 4122. |
| [G9_4122_pt.pdf](../data/results/figures/G9_4122_pt.pdf) | Signed heavy-hadron pt spectrum for PDG 4122. |
| [G9_421_eta.pdf](../data/results/figures/G9_421_eta.pdf) | Signed heavy-hadron eta spectrum for PDG 421. |
| [G9_421_phi.pdf](../data/results/figures/G9_421_phi.pdf) | Signed heavy-hadron phi spectrum for PDG 421. |
| [G9_421_pt.pdf](../data/results/figures/G9_421_pt.pdf) | Signed heavy-hadron pt spectrum for PDG 421. |
| [G9_5122_eta.pdf](../data/results/figures/G9_5122_eta.pdf) | Signed heavy-hadron eta spectrum for PDG 5122. |
| [G9_5122_phi.pdf](../data/results/figures/G9_5122_phi.pdf) | Signed heavy-hadron phi spectrum for PDG 5122. |
| [G9_5122_pt.pdf](../data/results/figures/G9_5122_pt.pdf) | Signed heavy-hadron pt spectrum for PDG 5122. |
| [G9_5212_eta.pdf](../data/results/figures/G9_5212_eta.pdf) | Signed heavy-hadron eta spectrum for PDG 5212. |
| [G9_5212_phi.pdf](../data/results/figures/G9_5212_phi.pdf) | Signed heavy-hadron phi spectrum for PDG 5212. |
| [G9_5212_pt.pdf](../data/results/figures/G9_5212_pt.pdf) | Signed heavy-hadron pt spectrum for PDG 5212. |
| [G9_521_eta.pdf](../data/results/figures/G9_521_eta.pdf) | Signed heavy-hadron eta spectrum for PDG 521. |
| [G9_521_phi.pdf](../data/results/figures/G9_521_phi.pdf) | Signed heavy-hadron phi spectrum for PDG 521. |
| [G9_521_pt.pdf](../data/results/figures/G9_521_pt.pdf) | Signed heavy-hadron pt spectrum for PDG 521. |
| [balancing.activity.beauty.pdf](../data/results/figures/balancing.activity.beauty.pdf) | Rendered balancing activity beauty page. |
| [balancing.activity.charm.pdf](../data/results/figures/balancing.activity.charm.pdf) | Rendered balancing activity charm page. |
| [balancing.baryon_meson.activity.pdf](../data/results/figures/balancing.baryon_meson.activity.pdf) | Rendered balancing baryon meson activity page. |
| [balancing.integrated.beauty.pdf](../data/results/figures/balancing.integrated.beauty.pdf) | Rendered balancing integrated beauty page. |
| [balancing.integrated.charm.pdf](../data/results/figures/balancing.integrated.charm.pdf) | Rendered balancing integrated charm page. |
| [canvases.root](../data/results/figures/canvases.root) | All rendered canvases with graphs, errors, labels and layout. |
| [correlations.beauty.pdf](../data/results/figures/correlations.beauty.pdf) | Rendered correlations beauty page. |
| [correlations.charm.pdf](../data/results/figures/correlations.charm.pdf) | Rendered correlations charm page. |
| [drawing-record.tsv.gz](../data/results/figures/drawing-record.tsv.gz) | Compressed exact coordinates, statuses, uncertainties and presentation records. |
| [manifest.json](../data/results/figures/manifest.json) | Exact PDFs, canvas archive, drawing records, source and runtime bindings. |
| [multiplicity.composite.pdf](../data/results/figures/multiplicity.composite.pdf) | Rendered multiplicity composite page. |
| [supplemental.balancing.activity.beauty.extremes.pdf](../data/results/figures/supplemental.balancing.activity.beauty.extremes.pdf) | Rendered supplemental balancing activity beauty extremes page. |
| [supplemental.balancing.activity.charm.extremes.pdf](../data/results/figures/supplemental.balancing.activity.charm.extremes.pdf) | Rendered supplemental balancing activity charm extremes page. |
| [supplemental.balancing.baryon_meson.activity.by_tune.pdf](../data/results/figures/supplemental.balancing.baryon_meson.activity.by_tune.pdf) | Rendered supplemental balancing baryon meson activity by tune page. |

### `data/results/numerical`

The numerical reader and verifier consume these typed values and provenance records.

| File | Purpose |
| --- | --- |
| [admission-closure.json](../data/results/numerical/admission-closure.json) | Accepted source, event, block and query-collection closure. |
| [native-run-receipt.json](../data/results/numerical/native-run-receipt.json) | Persisted native estimator request, run identity and numerical bindings. |
| [numerics.root](../data/results/numerical/numerics.root) | Typed values, statistical covariance factors, validity masks and provenance. |
| [package-manifest.json](../data/results/numerical/package-manifest.json) | Numerical package files, hashes and external execution locators. |
| [report.json](../data/results/numerical/report.json) | Numerical point inventory, statuses, hashes and execution references. |
| [source-build-ledger.json](../data/results/numerical/source-build-ledger.json) | Original numerical producer source, configuration and build identities. |

### `data/results/numerical/exports`

Table users read these exports. The numerical verifier checks their byte identities.

| File | Purpose |
| --- | --- |
| [accounting.csv](../data/results/numerical/exports/accounting.csv) | Generated sample and attempt accounting. |
| [accounting.tex](../data/results/numerical/exports/accounting.tex) | Formatted sample accounting table. |
| [missing.csv](../data/results/numerical/exports/missing.csv) | Explicit unavailable numerical and uncertainty states. |
| [overleaf-check.tex](../data/results/numerical/exports/overleaf-check.tex) | Standalone TeX document for table compilation. |
| [overleaf-preamble.tex](../data/results/numerical/exports/overleaf-preamble.tex) | Required TeX packages for the exported tables. |
| [overleaf-tables.tex](../data/results/numerical/exports/overleaf-tables.tex) | Table include list. |
| [points.csv](../data/results/numerical/exports/points.csv) | Round-trip numerical values and statuses. |
| [receipt.json](../data/results/numerical/exports/receipt.json) | Exact export hashes and numerical input identity. |
| [t1.csv](../data/results/numerical/exports/t1.csv) | Species-resolved natural final-heavy counts. |
| [t1.tex](../data/results/numerical/exports/t1.tex) | Formatted species counts. |

### `tests`

The verification suite exercises the distribution helper.

| File | Purpose |
| --- | --- |
| [test_data_release.py](../tests/test_data_release.py) | Checks byte restoration, restart, read-only verification and refusal of corrupt or conflicting files. |
