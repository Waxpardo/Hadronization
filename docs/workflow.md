# Workflow

[Documentation index](../README.md#documentation)

## Choose an entry point

Start from raw ROOT, accepted analyzed ROOT or an existing verified query collection. Do not regenerate an accepted source to replace unavailable bytes. Obtain the original files and independent checksum records from the data custodian.

Commands below use shell variables for external paths and hashes. Set them from allocated storage and separately trusted records. A variable ending in `SHA256` contains 64 lowercase hexadecimal characters. Do not obtain a trust pin solely from an adjacent mutable manifest.

Set `RUN_ROOT` to a new absolute directory whose parent exists. Use nonsymlink paths with sufficient disk space. Each example writes only its named output or scratch directory, unless it explicitly submits work.

```sh
export RUN_ROOT="$PWD/data/work/example-run"
mkdir -p "$RUN_ROOT/tmp"
export TMPDIR="$RUN_ROOT/tmp"
```

The [CLI reference](cli-reference.md) lists every option. `--help` requires no external scientific input.

## Raw inventory and generation

Inventory the shipped campaign without contacting a scheduler:

```sh
./hadronization generate --purpose inventory
```

The inventory joins the campaign, raw manifest, attempt ledger and any local reservations. The inventory reports absent accepted files without scheduling their regeneration. Size observation alone does not verify their SHA-256.

With all raw files available under `RAW_ROOT`, verify accepted bytes explicitly:

```sh
python3 pipeline/generate/submit.py plan --purpose inventory \
  --raw-root "${RAW_ROOT:?}" --work-root "$RUN_ROOT/generate" \
  --verify-accepted-sha256
```

Generation requires PYTHIA, ROOT, configured storage and scheduler authority. The shipped campaign already has a complete accepted source domain. Its continuation plan therefore has no new work. The `new` purpose refuses this frozen campaign identity.

For an incomplete compatible campaign, `continuation` plans only eligible unaccepted jobs. `recovery` refuses to regenerate missing accepted bytes. `--build` compiles needed executables only when the plan contains work. The direct build command can compile a validator or producer:

```sh
python3 pipeline/generate/submit.py build --component validator
```

Only run this scheduler-contacting command after reviewing the continuation plan and configuring `SCHEDULER_SUBMIT`:

```sh
./hadronization generate --purpose continuation --submit
```

Generation submission reserves unique attempts and submits held jobs. The worker checks source identity, binary hashes, cards and reservations. It writes local scratch, validates raw ROOT and publishes without replacing accepted output. The generator requests successful events, subject to its attempt ceiling.

## Analyze raw ROOT

This stage requires every selected raw file, its manifest record and ROOT. Analysis preserves structured event, heavy-particle, ancestry, origin and pair information. It does not impose the downstream inclusive pair profile.

Create an immutable analysis plan with a byte target:

```sh
./hadronization analyze plan \
  --raw-root "${RAW_ROOT:?}" --work-root "$RUN_ROOT/analyze-work" \
  --output-root "$RUN_ROOT/analyzed" --plan "$RUN_ROOT/analysis-plan.json" \
  --target-bytes 500000000
./hadronization analyze explain --plan "$RUN_ROOT/analysis-plan.json"
./hadronization analyze run --plan "$RUN_ROOT/analysis-plan.json" --jobs 1
./hadronization analyze verify --plan "$RUN_ROOT/analysis-plan.json"
```

The byte target controls deterministic whole-source packing. It is an estimate, not a hard limit on resulting ROOT file size. Optional measured rates refine the estimate. Every output shard has a ROOT file and a matching PASS receipt.

The plan binds source order, original blocks, configuration and build identity. Workers hash raw inputs before and after processing. They close, reopen and semantically verify output before publication.

## Build a reusable query

This stage requires analyzed ROOT files and their matching accepted receipts. First create one signed-PDG dictionary across the entire selected campaign. A separate dictionary for each shard is not merge-safe.

Repeat the three input arguments in matching order for every analyzed pair:

```sh
./hadronization query census \
  --input "${ANALYZED_ROOT:?}" --receipt "${ANALYZED_RECEIPT:?}" \
  --accepted-receipt-sha256 "${RECEIPT_SHA256:?}" \
  --expected-source-count 3000 --output "$RUN_ROOT/dictionary.json" \
  --work-root "$RUN_ROOT/query-work"
```

A single shard cannot satisfy the example's full source count. Supply all pairs before running it. The census refuses incomplete source coverage. The dictionary records signed PDG values and one common digest. Unknown observed identities cause refusal.

For a local query build, use the complete dictionary and one input pair:

```sh
./hadronization query build \
  --input "${ANALYZED_ROOT:?}" --receipt "${ANALYZED_RECEIPT:?}" \
  --accepted-receipt-sha256 "${RECEIPT_SHA256:?}" \
  --dictionary "$RUN_ROOT/dictionary.json" \
  --work-root "$RUN_ROOT/query-work" --output "$RUN_ROOT/query-0000"
./hadronization query verify --workspace "$RUN_ROOT/query-0000" \
  --expected-content-sha256 "${QUERY_CONTENT_SHA256:?}" \
  --work-root "$RUN_ROOT/query-verify-work"
```

The query stores five sparse families and exact support rows. Its pair-population check includes zero-associate triggers and rejects missing in-domain pairs. The verifier compares sparse contents and Sumw2 with retained rows. It also checks the exact workspace file set.

`query prepare-pack` creates a fixed binary pack for repeated execution. Supply `--prepared-pack` to census, build, verify or scan to use that pack. A pack mismatch fails without a worker-side rebuild.

## Cluster query construction

This route requires HTCondor authority, execute-node credentials, CVMFS, bulk allocation and separate durable control storage. It requires an externally supplied acquisition manifest and independently reviewed site records. The repository supplies templates, not an admitted site or storage allocation.

The production adapter expects 323 ROOT/receipt pairs with ordinals 0–322. It checks 3,000 sources, 300 million successful events and 158,720,142,481 analyzed ROOT bytes. This adapter does not expose a general campaign-replacement option.

The acquisition manifest uses schema `phasea_arch_full_input_acquisition_manifest_v1`. This literal schema name identifies the accepted analyzed-input inventory. Its status is `ALL_323_ACCEPTED_INPUT_PAIRS_REVERIFIED`. It contains `pair_count`, `input_file_count`, `accepted_root_bytes` and `files`.

Each file record contains `ordinal`, `role`, `path`, `bytes` and `sha256`. Roles are `root_file` and `receipt`. Relative paths are `inputs/shard-NNNN.root` and `inputs/shard-NNNN.json`. The manifest's external hash must match the supplied file.

Prepare an inert bundle:

```sh
./hadronization condor prepare \
  --acquisition "${ACQUISITION:?}" \
  --expected-acquisition-sha256 "${ACQUISITION_SHA256:?}" \
  --dictionary "${DICTIONARY:?}" \
  --expected-dictionary-sha256 "${DICTIONARY_SHA256:?}" \
  --output "$RUN_ROOT/condor-inert"
```

The bundle contains source and dictionary pins, expected sources, worker scripts, DAG files, build instructions and site templates. Preparation does not submit jobs. Build its Linux binary pack once on the specified runtime. Preserve the pack receipt and tar SHA-256.

Run the generated preflight canary on an actual execute node before admitting the site. It checks the OS, architecture, libraries, ClassAds, input readability and destination write/readback behavior. The probe creates small files and collision-check directories. It is not read-only.

Complete `SITE_ADMISSION_TEMPLATE.json` from measured results and independently retained evidence. The required literal authority is `INDEPENDENT_L1_AND_SITE_REVIEW`. This value identifies a reviewed runtime, scientific-input and storage decision. Do not turn `PENDING` into `PASS` without the associated measurements.

The current route requires POSIX storage with tested no-replace publication. It supplies no dCache or object-store adapter. The site record must also establish quota, capacity, retention and custody of control hashes.

Bind the site into a new bundle:

```sh
./hadronization condor bind-site --bundle "$RUN_ROOT/condor-inert" \
  --expected-bundle-sha256 "${INERT_BUNDLE_SHA256:?}" \
  --pack "${LINUX_PACK:?}" --expected-pack-sha256 "${LINUX_PACK_SHA256:?}" \
  --admission "${SITE_ADMISSION:?}" \
  --expected-admission-sha256 "${SITE_ADMISSION_SHA256:?}" \
  --output "$RUN_ROOT/condor-bound"
```

The admitted resource envelope requires measurements across every tune/block combination. Memory, scratch, postprocessing capacity and bulk allocation must exceed their measured peaks by at least 25%. `maxjobs` must equal four. Each query worker requests one CPU. The [configuration reference](configuration.md#cluster-resource-record) lists units and fields.

Stage the sealed DAG into a fresh writable launch directory:

```sh
./hadronization condor stage-dag --bundle "$RUN_ROOT/condor-bound" \
  --expected-bundle-sha256 "${BOUND_BUNDLE_SHA256:?}" \
  --output "$RUN_ROOT/condor-launch"
```

The next command contacts the scheduler. Run it only after site admission and launch-directory review:

```sh
(cd "$RUN_ROOT/condor-launch" && condor_submit_dag workflow.dag)
```

Each attempt uses a unique persistent path. Workers verify accepted input bytes before ROOT open, build in execute-node scratch and verify persistent readback. The DAG permits two retries except for deterministic exit 42. Deterministic scientific, schema or identity errors abort the DAG. Classified transient failures use exit 75.

After construction, independently review accepted attempts and preserve their content pins outside mutable output directories. `render-collector` creates a separate submit file from those pins. Submit that file explicitly with native HTCondor tools. The collector closes the exact expected source domain and publishes its manifest last. An empty queue is not completion.

`screen-plan`, `stage-screen-dag` and `collect-screen` support bounded synthetic or partial checks. Their outputs retain `TEST_ONLY` qualification. They cannot authorize full research results.

## Collection and physical merge

A collection index binds workspace locations to source identities and independently supplied content pins. Obtain `EXPECTED_SOURCES` and its hash independently of the query outputs. Repeat workspace and content-pin options in matching order:

```sh
./hadronization collection create \
  --workspace "${QUERY_WORKSPACE:?}" \
  --expected-content-sha256 "${QUERY_CONTENT_SHA256:?}" \
  --expected-sources "${EXPECTED_SOURCES:?}" \
  --expected-sources-sha256 "${EXPECTED_SOURCES_SHA256:?}" \
  --output "$RUN_ROOT/sharded.json" --work-root "$RUN_ROOT/collection-work"
./hadronization collection verify --index "$RUN_ROOT/sharded.json" \
  --expected-index-sha256 "${SHARDED_INDEX_SHA256:?}"
./hadronization merge build --index "$RUN_ROOT/sharded.json" \
  --expected-index-sha256 "${SHARDED_INDEX_SHA256:?}" \
  --output "$RUN_ROOT/merged"
```

Use the collector's collection index when following the cluster route. A manually created collection alone does not establish full site acceptance. `collection admit` checks the independent expected-source, site, collector and merge records.

The merge writes one ROOT file per tune. Each file contains separate sparse objects for every original block and family. It refuses an object above its serialization limit. It compares every occupied cell and Sumw2 against the original shards.

Verify the merge with independent pins:

```sh
./hadronization merge verify --index "$RUN_ROOT/merged/index.json" \
  --expected-index-sha256 "${MERGED_INDEX_SHA256:?}" \
  --merge-receipt "$RUN_ROOT/merged/merge-receipt.json" \
  --merge-receipt-sha256 "${MERGE_RECEIPT_SHA256:?}"
```

Keep the generated merge verification receipt. Its independent hash can avoid repeating the exhaustive sparse comparison during reduction. Physical hashes and source lineage still undergo checks.

## Numerical reduction

Full research reduction requires a complete merged three-tune collection, original query support, ten blocks per tune and a clean committed source. It also requires independent expected-source, site-work, collector-closure and merge pins. A collection with `TEST_ONLY` state remains partial in numerical output.

Create the reducer scratch directory before execution:

```sh
mkdir -p "$RUN_ROOT/reduce-work"
./hadronization reduce run \
  --collection-index "${MERGED_INDEX:?}" \
  --collection-index-sha "${MERGED_INDEX_SHA256:?}" \
  --expected-sources "${EXPECTED_SOURCES:?}" \
  --expected-sources-sha "${EXPECTED_SOURCES_SHA256:?}" \
  --analysis config/analysis.json --analysis-sha "${ANALYSIS_SHA256:?}" \
  --site-work "${SITE_WORK:?}" --site-work-sha "${SITE_WORK_SHA256:?}" \
  --collector-closure "${COLLECTOR_CLOSURE:?}" \
  --collector-closure-sha "${COLLECTOR_CLOSURE_SHA256:?}" \
  --merge-receipt "${MERGE_RECEIPT:?}" \
  --merge-receipt-sha "${MERGE_RECEIPT_SHA256:?}" \
  --work-root "$RUN_ROOT/reduce-work" --output-dir "$RUN_ROOT/numerical"
```

The default request covers multiplicity, correlations, balancing, signed spectra and natural-heavy accounting. The center and uncertainty come from the native estimator. The reducer writes `numerics.root`, `report.json`, provenance receipts, exports and `package-manifest.json`.

Add `--charm-trigger 411` to select the coherent D+ recipe. Add `--analysis` with a separately hashed compatible copy to change profiles or percentile classes. Optional rectangular profiles reuse the query bytes. Both profiles pass through the same numerical estimator and renderer.

### Compare inclusive and rectangular selections

Keep the shipped analysis configuration unchanged. Create a separate request with the [profile example](configuration.md#analysis-choices), and record its SHA-256.

For the inclusive result, use `--profile-id inclusive`. For the 1.0/0.15 GeV/c result, use `--profile-id pt_1_0p15` with the compatible request and its hash. Run reduction twice with distinct output and scratch directories. Use each numerical package to render and package its own figures.

The rectangular selection requires trigger pT >= 1.0 GeV/c and associate pT >= 0.15 GeV/c. Both endpoints pass. An associate can have larger pT than its trigger. The cuts apply to all pair observables.

The trigger threshold also selects eligible singles for each trigger denominator. A trigger needs no qualifying associate. Multiplicity distributions and standalone spectra keep their separate selections.

The inclusive figures omit an inclusive-pT annotation. The rectangular figures show the numerical thresholds. Their centers, statistical errors and tune ratios come from their own numerical ROOT file.

Producer verification needs the original inputs and source identity:

```sh
./hadronization reduce verify --mode producer \
  --root "$RUN_ROOT/numerical/numerics.root" \
  --report "$RUN_ROOT/numerical/report.json" --report-sha "${REPORT_SHA256:?}"
```

Portable verification checks the numerical package without reopening external execution inputs:

```sh
./hadronization reduce verify --mode portable \
  --package-dir "$RUN_ROOT/numerical" \
  --package-manifest-sha "${NUMERICAL_MANIFEST_SHA256:?}"
```

## Figures and tables

The renderer requires PyROOT, ROOT libraries, a compiler, numerical ROOT and its independent physical and logical hashes. These hashes identify different objects. Obtain both from the verified numerical report.

```sh
./hadronization plot render-cold \
  --numerics-root "$RUN_ROOT/numerical/numerics.root" \
  --expected-root-sha256 "${NUMERICS_ROOT_SHA256:?}" \
  --expected-value-sha256 "${NUMERICS_VALUE_SHA256:?}" \
  --plot-config config/plot.json \
  --work-dir "$RUN_ROOT/plot-work" --output "$RUN_ROOT/figures"
./hadronization plot verify-render-cold \
  --numerics-root "$RUN_ROOT/numerical/numerics.root" \
  --expected-root-sha256 "${NUMERICS_ROOT_SHA256:?}" \
  --expected-value-sha256 "${NUMERICS_VALUE_SHA256:?}" \
  --expected-manifest-sha256 "${FIGURE_MANIFEST_SHA256:?}" \
  --plot-config config/plot.json \
  --work-dir "$RUN_ROOT/plot-verify-work" --output "$RUN_ROOT/figures"
```

The renderer writes PDFs, `canvases.root`, a compressed drawing record and `manifest.json`. It reopens canvases and checks coordinates, errors, statuses, axes, pads, styles, legends and reference lines. The PDF exporter embeds all fonts through Ghostscript. The verifier checks the exported fonts with Poppler. These checks do not replace visual inspection at publication size.

Each figure contains a compact sample description in its upper panel. It states the generator, collision system, energy, hard heavy-flavour processes and applicable acceptance. Activity figures identify N_ch and its particle cuts. The [scientific reference](science.md) gives the complete selections, observable definitions and statistical method. A reserved area separates the sample description from data.

Bands show pointwise statistical standard errors. They do not represent systematic uncertainty or a simultaneous confidence region. Histogram bands stop at nonpositive log bins, unavailable errors and gaps between bin edges. The numerical archive retains these bins and their statuses.

Use the three-class activity views for compact comparisons. They show 0–1%, 40–50% and 80–90%. The full-class views retain all classes. Use full-width placement for dense figures. Check label sizes after placing each figure in the manuscript.

The multiplicity inset identifies MONASH class boundaries. Other tunes have their own boundaries. The lower-panel limit of five hides some low-multiplicity ratios. The saved numerical values remain unchanged.

Correlation views distinguish identified pairs from sums over eligible associates. Opposite and same sign refer to heavy-flavour content. Horizontal segments on species axes mark categories; they are not horizontal measurement uncertainties. Equal-width percentile slots can represent unequal percentile intervals.

| Product | Presentation |
| --- | --- |
| Multiplicity distribution | Logarithmic y, linear x, lower tune ratios and a lower-left logarithmic percentile inset |
| Charm and beauty correlations | Default MONASH identified OS/SS and inclusive heavy-flavour sign difference |
| Integrated balancing | Species categories and lower tune/reference ratios |
| Activity-dependent balancing | Every requested class, tune rows and one shared comparison row |
| Baryon-to-meson ratios | Class categories, absolute ratios and lower tune/reference ratios |
| Signed heavy-hadron spectra | Separate pT, eta and phi pages for each signed species |
| Supporting views | Selected activity intervals, tune-separated Lambda ratios and two-trigger Lambda, Sigma and Xi comparisons |
| Sample tables | Generated numerical CSV/TeX exports, not plot-derived values |

The multiplicity display ends at the last occupied MONASH bin edge. Other tunes can have farther-tail bins in `numerics.root`. The inset shows positive MONASH support and its class boundaries. Numerical distributions retain the complete activity domain.

The default correlation view shows MONASH identified pairs with statistical bands. Solid and dotted lines distinguish opposite and same heavy-flavour signs. The alternative `config/plot-all-tune.json` uses tune colors and comparison panels. Neither presentation changes the numerical uncertainties.

For tune comparisons, MONASH uses black circles, JUNCTIONS blue squares and CLOSEPACKING orange triangles. Inclusive multiplicity uses a solid line. Other classes use distinct configured line patterns. Undefined values and withheld errors retain explicit statuses.

Use `config/plot-dplus.json` with D+ numerical results. Keep the selected configuration with the figures. A mismatched charm recipe fails before rendering.

## Assemble and verify the package

This step requires verified numerical and figure manifests and their independent hashes. It copies the required files into a fresh package:

```sh
./hadronization package build --numerical "$RUN_ROOT/numerical" \
  --numerical-manifest-sha256 "${NUMERICAL_MANIFEST_SHA256:?}" \
  --figures "$RUN_ROOT/figures" \
  --figure-manifest-sha256 "${FIGURE_MANIFEST_SHA256:?}" \
  --plot-config config/plot.json --output "$RUN_ROOT/package"
./hadronization package verify --package "$RUN_ROOT/package" \
  --manifest-sha256 "${PACKAGE_MANIFEST_SHA256:?}" \
  --work-dir "$RUN_ROOT/package-verify-work"
```

Package construction checks file bindings. The separate verification command also runs numerical and canvas checks. Package verification requires matching renderer source and runtime identity. It does not revalidate unavailable external execution inputs.

## Restart and failure rules

| Stage | Restart or failure behavior |
| --- | --- |
| Generation | Unique reservations and attempt paths. Never reuse an accepted identity or overwrite accepted bytes. |
| Analysis | Resume verifies existing ROOT/receipt pairs. An intact embedded contract can recover a missing receipt. Receipt-only or conflicting output fails. |
| Query | New output path required. Failed scratch and failure records can remain for diagnosis. |
| Collection and merge | New destination required. Changed hashes, source domains, dictionaries or sparse cells fail verification. |
| Reduction | New output directory required. Missing closure, dirty source or unsupported request blocks full results. |
| Rendering | New output directory required. Missing numerical roles, mismatched configuration or canvas disagreement fails. |
| Package | Exact required file set. Missing, extra, changed or unsafe paths fail verification. |

Preserve ambiguous publication stages and reservations until their state is understood. A failed process may have completed a filesystem operation before losing its response. Verify durable bytes before selecting a new attempt. Never repair acceptance by rewriting a checksum beside the disputed file.

`./hadronization clean` is a dry run. `./hadronization clean --apply` deletes listed compiler residue, caches and eligible aged accepted-attempt scratch. Review the list first. It does not implement bulk research-data retention.
