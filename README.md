# Hadronization

This is a generator-level study of heavy-flavour balancing in pp collisions at
13.6 TeV across the MONASH, JUNCTIONS and CLOSEPACKING PYTHIA 8 tune bundles.
The accepted sample is deliberately biased toward hard charm/beauty production
(`PhaseSpace:pTHatMin=2 GeV`); it is neither minimum bias nor detector matched.
Uncertainties are finite-Monte-Carlo statistical uncertainties only.

The current source flow is `generate` → `analyze` → `query` → `collection` →
`merge` → `reduce` → `plot`. Query keeps exact per-shard support and a mandatory
v2.2 pair-population proof. The physical merged collection has one ROOT file per
tune, each with five block-resolved THnSparse families; the exact query shards
remain linked for source and diagnostic readback. Statistics writes a
self-contained typed `numerics.root`, and Plotting renders only its verified
values, errors and availability states. The eight paper roles include the
multiplicity figure; signed-heavy spectra are supporting G9 plots.

The paper default is a signed D⁰ (`+421`) trigger; D⁺ (`+411`) is an explicit
alternate. Inclusive pair observables have no final-hadron pT floor and no
event-wise trigger/associate pT ordering. Optional named rectangular
selections apply independent inclusive minima to each particle, with
`pT_min_trigger >= pT_min_associate`, including equality. The nominal
event-activity proxy is charged light/nonheavy final particles with
`pT > 0.15 GeV/c` and `|eta| <= 4`; that threshold is not a pair cut. G9 is a
separate all-origin signed-heavy marginal without a pT floor. The exact current
request is `config/analysis.json` v2.2.0; `config/plot.json` is the D⁰/Monash
identified-pair and inclusive heavy-flavour-sign correlation presentation
default. The historical OS−SS balance teaching view remains selectable with
`monash_balance`.
On the default charm and beauty correlation pages, the upper row compares
identified hadron–antihadron and same-hadron pairs; the lower row sums all
registered associates by heavy-flavour sign. The native estimator sums pair
primitives before dividing by the common trigger count and propagates the
joint ten-block uncertainty. The default correlation PDFs omit statistical
error bars for display and say so; K10 errors and covariance remain in ROOT.
Neutral D⁰ and Λᵦ⁰ use heavy-flavour sign,
not electric charge.

The multiplicity page keeps zero on the main linear x axis and uses a compact
lower-left log–log inset for positive multiplicities. The inset repeats the
MONASH histogram as a black step line, with grey dashed class boundaries and
vertical percentile labels centered geometrically within their intervals.
Both its distribution and tune-local class intervals come from numerical ROOT;
the renderer does not compute percentile thresholds.

For a local source check, use a real, nonsymlink scratch directory:

```sh
mkdir -p data/work/tmp
export TMPDIR="$(pwd -P)/data/work/tmp"
./hadronization doctor
./hadronization verify
./hadronization query --help
./hadronization collection --help
./hadronization merge --help
./hadronization reduce --help
./hadronization plot --help
```

The bounded nonzero interface fixture can be regenerated without contacting a
site or producing new PYTHIA events. Choose a fresh path under ignored work
storage; the builder creates the chain and the oracle checks it:

```sh
export NONZERO_CHAIN_BASE="$(pwd -P)/data/work/nonzero-v22"
python3 tests/fixtures/nonzero_chain_v22/build.py
python3 tests/fixtures/nonzero_chain_v22/oracle.py
```

The builder executes the actual analyze, query, collection and physical merge
commands for 30 explicitly synthetic sources. It requires a new, nonsymlink
directory and refuses to replace an existing fixture. The oracle likewise
refuses to replace `oracle.json`; set `NONZERO_CHAIN_REPORT` to a fresh absolute
filename for another audit of the same fixture. For a public current numerical
run, pin that merged index, its independently enumerated source list and the
shipped v2.2 analysis before choosing a new output directory:

```sh
INDEX="$NONZERO_CHAIN_BASE/merged/index.json"
SOURCES="$NONZERO_CHAIN_BASE/expected-sources.json"
INDEX_SHA="$(shasum -a 256 "$INDEX" | awk '{print $1}')"
SOURCES_SHA="$(shasum -a 256 "$SOURCES" | awk '{print $1}')"
ANALYSIS_SHA="$(shasum -a 256 config/analysis.json | awk '{print $1}')"
./hadronization reduce run \
  --collection-index "$INDEX" --collection-index-sha "$INDEX_SHA" \
  --expected-sources "$SOURCES" --expected-sources-sha "$SOURCES_SHA" \
  --analysis-sha "$ANALYSIS_SHA" --representative \
  --work-root "$(pwd -P)/data/work/tmp" \
  --output-dir "$(pwd -P)/data/work/nonzero-v4"
```

`--representative` is a small TEST_ONLY diagnostic domain. Omit it to request
the full current paper numerical domain, or pass a separately pinned
`--request` and `--request-sha` for a reviewed subset. The explicit
`--charm-trigger 411` selects the D⁺ alternate; the
default is D⁰.

Query, collection, merge, reduction and plotting require independently pinned
input paths and SHA-256 values; see their command help before running them on
an accepted campaign. Keep the work/output directories outside source control
and never reuse an output path. A small explicitly `TEST_ONLY` fixture verifies
the local interfaces; it is not a physical PYTHIA prediction. No current
result is tracked in `results/`. Full paper numerics require the authenticated
physically merged 323-query-shard/3,000-source collection and its site/admission
receipts. The Nikhef runtime, storage and scheduler gates have not been passed
by a local verification run.

`./hadronization generate` inventories deterministic nominal work by default.
Only an explicit continuation submission with a configured site may contact a
scheduler. Accepted raw files live under ignored `data/raw/`; attempt evidence
and scratch live under ignored `data/work/`. `./hadronization clean` is dry-run
by default and does not remove raw files or durable attempt evidence.

## Accepted-input to portable-result commands

The source-controlled campaign, source manifest, analysis and query model are
read-only inputs. An independent custodian supplies the accepted analyzed-input
manifest, a dictionary from accepted shards, and physical SHA-256 pins. Query
workers hash each analyzed ROOT and receipt before opening ROOT. One frozen
source tar and one qualified Linux query pack serve all workers; workers never
rebuild independently.

`./hadronization condor prepare --help` creates an inert native DAG. Its bundle
contains `BUILD_LINUX_PACK.sh`, `site-canary.sub`, preflight and a PENDING
admission template. Copy the build script and source tar to a fresh external
build directory. `SITE_CONF` must name a measured site.conf. The build checks
ROOT 6.30.01, GCC 14.2.0 and PYTHIA 8.317. Bind a copy of the canary template
to an actual execute node only after choosing allocated endpoints. Its probe
checks x86_64 and the selected AlmaLinux 9.6 image, CVMFS and ROOT libraries,
separate hashed job and matched-machine ClassAds, full accepted input SHA and
ROOT open. A real 9.6 worker passed the pinned ROOT/GCC/PYTHIA and PyROOT
runtime smoke checks; accepted-input and durable-storage admission remain
separate gates. At each allocated bulk/control root it stages and fsyncs a
directory, invokes the same
no-replace directory publisher as query, reopens and hashes the result, rejects
existing empty and nonempty destinations, and retains an interrupted private
stage. An unsupported directory rename is a failed probe even if exclusive file
creation works. These observations do not grant admission.
The probe is observation, not admission. `condor bind-site` requires an
independent record with hashed evidence for every PASS, including quota,
capacity, retention, custody, all-tune pair population and resource budget.
Before binding, run `./hadronization condor screen-plan --work
"$INERT_BUNDLE/work.json" --expected-work-sha256 "$INERT_WORK_SHA"
--expected-sources "$INERT_BUNDLE/expected-sources.json" --input-root
"$ACCEPTED_ANALYZED_ROOT"`. It reads every pinned analyzed receipt and selects
real shard ordinals covering all tunes/original blocks. Query-build and verify
these selected accepted inputs with the frozen pack to establish pair
population before site admission. After binding, rerun screen-plan against the
bound work (without --input-root); independently pin that plan and selected
attempts. `condor collect-screen` uses the same collector/publisher checks but
marks its partial index TEST_ONLY. Merge, reduce and render that representative
index before staging the full DAG. A plan alone does not prove pair population;
a real omission holds for a retained-input/scientific ruling.

For each prebinding screen ordinal, the direct pair-proof command is:

```sh
./hadronization query build --input "$ACCEPTED_ANALYZED_ROOT/shard-$SCREEN_ORDINAL.root" \
  --receipt "$ACCEPTED_ANALYZED_ROOT/shard-$SCREEN_ORDINAL.json" \
  --accepted-receipt-sha256 "$PINNED_SCREEN_RECEIPT_SHA" \
  --dictionary "$DICTIONARY" --analysis config/analysis.json \
  --layout config/query.json --prepared-pack "$FRESH_BUILD/prepared-pack" \
  --work-root "$SCREEN_WORK" --output "$SCREEN_QUERY_OUTPUT"
./hadronization query verify --workspace "$SCREEN_QUERY_OUTPUT" \
  --expected-content-sha256 "$SCREEN_CONTENT_SHA" \
  --prepared-pack "$FRESH_BUILD/prepared-pack" --work-root "$SCREEN_WORK"
```

Use four-digit zero-padded ordinal text, a fresh output per shard and the
receipt SHA from the accepted acquisition manifest. Independently pin the
workspace's scientific content digest before verification. The current
pair-population proof fails closed per input; no synthetic screen can qualify
the other accepted shards.

The publisher currently supports allocated writable POSIX storage. On Linux
filesystems without atomic no-replace rename, it reserves an absent destination
with exclusive mode-000 mkdir, then replaces only that pinned reservation with
the complete private stage. This requires owned parents without group/other write
access, no symlinks or foreign mounts, and cooperating processes under the same
owner. A visible empty reservation is never a completed artifact: readers require
the existing manifests and content pins. Interrupted publication retains stages
and reservations for review; do not remove or retry them automatically. dCache has
no adapter in this release. Retain the original query shards after merge:
their exact support and source ranges remain numerical inputs. One merged ROOT
partition per tune is the physical layout; measure occupancy, RSS and scratch
and refuse admission if it cannot fit. The DAG defaults to four workers and
at most two retries per classified transient failure. Deterministic identity,
schema or pair-population errors hold the campaign. An independent custodian
pins accepted attempt contents. The collector alone closes the sharded index;
it loads the bound Linux query pack for verification and PyROOT. `merge build`
separately pins the physical transformation.

After independent admission, use fresh paths and independently read-back SHAs:

```sh
./hadronization condor prepare --acquisition "$ACQUISITION" \
  --expected-acquisition-sha256 "$ACQUISITION_SHA" \
  --dictionary "$DICTIONARY" --expected-dictionary-sha256 "$DICTIONARY_SHA" \
  --output "$INERT_BUNDLE"
# Copy source.tar.gz and BUILD_LINUX_PACK.sh from that bundle to $FRESH_BUILD.
(cd "$FRESH_BUILD" && SITE_CONF="$MEASURED_SITE_CONF" bash BUILD_LINUX_PACK.sh)
./hadronization condor bind-site --bundle "$INERT_BUNDLE" \
  --expected-bundle-sha256 "$INERT_MANIFEST_SHA" --pack "$QUERY_PACK" \
  --expected-pack-sha256 "$QUERY_PACK_SHA" --admission "$ADMISSION" \
  --expected-admission-sha256 "$ADMISSION_SHA" --output "$BOUND_BUNDLE"
./hadronization condor preflight --work "$BOUND_BUNDLE/work.json" \
  --expected-work-sha256 "$WORK_SHA" --source-tar "$BOUND_BUNDLE/source.tar.gz" \
  --pack-tar "$BOUND_BUNDLE/query-pack.tar.gz" --full-input-hash
# Persist and independently pin the bound representative screen plan.
./hadronization condor screen-plan --work "$BOUND_BUNDLE/work.json" \
  --expected-work-sha256 "$WORK_SHA" \
  --expected-sources "$BOUND_BUNDLE/expected-sources.json" > "$SCREEN_PLAN"
./hadronization condor stage-screen-dag --bundle "$BOUND_BUNDLE" \
  --expected-bundle-sha256 "$BOUND_MANIFEST_SHA" --screen-plan "$SCREEN_PLAN" \
  --expected-screen-plan-sha256 "$SCREEN_PLAN_SHA" --output "$SCREEN_LAUNCH"
(cd "$SCREEN_LAUNCH" && condor_submit_dag -no_submit workflow.dag)
# Submit this TEST_ONLY screen after separate authorization and review.
(cd "$SCREEN_LAUNCH" && condor_submit_dag workflow.dag)
# Independent review writes pins only for the screened ordinals.
python3 "$BOUND_BUNDLE/collector.py" collect-screen \
  --work "$BOUND_BUNDLE/work.json" \
  --expected-work-sha256 "$WORK_SHA" \
  --expected-sources "$BOUND_BUNDLE/expected-sources.json" \
  --source-tar "$BOUND_BUNDLE/source.tar.gz" \
  --pack-tar "$BOUND_BUNDLE/query-pack.tar.gz" --pins "$SCREEN_PINS" \
  --expected-pins-sha256 "$SCREEN_PINS_SHA" --screen-plan "$SCREEN_PLAN" \
  --expected-screen-plan-sha256 "$SCREEN_PLAN_SHA"
# Merge, reduce and render the resulting TEST_ONLY screen index for resource proof.
# The full DAG below remains pending that separate vertical review.
./hadronization condor stage-dag --bundle "$BOUND_BUNDLE" \
  --expected-bundle-sha256 "$BOUND_MANIFEST_SHA" --output "$FRESH_LAUNCH"
(cd "$FRESH_LAUNCH" && condor_submit_dag -no_submit workflow.dag)
# Submission below is only after separate authorization and review.
(cd "$FRESH_LAUNCH" && condor_submit_dag workflow.dag)
# Independent review writes the all-ordinal accepted-pins file.
./hadronization condor render-collector --bundle "$BOUND_BUNDLE" \
  --expected-bundle-sha256 "$BOUND_MANIFEST_SHA" --pins "$ACCEPTED_PINS" \
  --expected-pins-sha256 "$ACCEPTED_PINS_SHA" --output "$FRESH_COLLECTOR"
condor_submit "$FRESH_COLLECTOR/collector.sub"
```

After manifest-last collector closure, the downstream chain is:

```sh
./hadronization collection admit --index "$SHARDED_INDEX" \
  --expected-index-sha256 "$SHARDED_SHA" \
  --expected-sources "$EXPECTED_SOURCES" --expected-sources-sha256 "$SOURCES_SHA" \
  --site-work "$BOUND_BUNDLE/work.json" --site-work-sha256 "$WORK_SHA" \
  --collector-closure "$COLLECTOR_CLOSURE" --collector-closure-sha256 "$CLOSURE_SHA"
./hadronization merge build --index "$SHARDED_INDEX" \
  --expected-index-sha256 "$SHARDED_SHA" --output "$MERGED_DIR"
# Build performs the one exhaustive source-to-merged cell/Sumw2 proof and
# publishes merge-verification.json only after that proof passes. Independently
# pin its SHA-256; later stages authenticate the receipt without repeating the
# exhaustive sparse comparison.
# `reduce run` performs and packages the authenticated collection admission;
# `collection admit` remains available as an optional standalone preflight.
./hadronization reduce run --collection-index "$MERGED_DIR/index.json" \
  --collection-index-sha "$MERGED_SHA" \
  --expected-sources "$EXPECTED_SOURCES" --expected-sources-sha "$SOURCES_SHA" \
  --analysis config/analysis.json --analysis-sha "$ANALYSIS_SHA" \
  --site-work "$BOUND_BUNDLE/work.json" --site-work-sha "$WORK_SHA" \
  --collector-closure "$COLLECTOR_CLOSURE" --collector-closure-sha "$CLOSURE_SHA" \
  --merge-receipt "$MERGED_DIR/merge-receipt.json" \
  --merge-receipt-sha "$MERGE_RECEIPT_SHA" \
  --merge-verification "$MERGED_DIR/merge-verification.json" \
  --merge-verification-sha "$MERGE_VERIFICATION_SHA" \
  --work-root "$REDUCE_WORK" --output-dir "$RESULT"
./hadronization reduce verify --mode producer --root "$RESULT/numerics.root" \
  --report "$RESULT/report.json" --report-sha "$REPORT_SHA"
./hadronization plot render-cold --numerics-root "$RESULT/numerics.root" \
  --expected-root-sha256 "$NUMERICS_SHA" --expected-value-sha256 "$VALUE_SHA" \
  --plot-config "$SELECTED_PLOT_CONFIG" --work-dir "$PLOT_WORK" --output "$FIGURES"
./hadronization plot verify-render-cold --numerics-root "$RESULT/numerics.root" \
  --expected-root-sha256 "$NUMERICS_SHA" --expected-value-sha256 "$VALUE_SHA" \
  --expected-manifest-sha256 "$FIGURE_MANIFEST_SHA" \
  --plot-config "$SELECTED_PLOT_CONFIG" --work-dir "$PLOT_WORK" --output "$FIGURES"
./hadronization reduce verify --mode portable --package-dir "$COPIED_RESULT" \
  --package-manifest-sha "$PACKAGE_MANIFEST_SHA"
./hadronization package build --numerical "$RESULT" \
  --numerical-manifest-sha256 "$PACKAGE_MANIFEST_SHA" --figures "$FIGURES" \
  --figure-manifest-sha256 "$FIGURE_MANIFEST_SHA" \
  --plot-config "$SELECTED_PLOT_CONFIG" --output "$COLLAB_PACKAGE"
./hadronization package verify --package "$COPIED_COLLAB_PACKAGE" \
  --manifest-sha256 "$COLLAB_MANIFEST_SHA" --work-dir "$PACKAGE_VERIFY_WORK"
```

The default full request yields P1–P8, G9 signed-heavy marginals, conditional
activity supplements, T1/diagnostics, compact CSV/TeX exports and a typed
numerical ROOT. Exact counts derive from the request and data. This ROOT stores
separate materialization, center, uncertainty and covariance validity. Negative
centers may be valid; an unavailable error is not zero. Nonlinear full-sample
centers use pooled additive primitives. K=10 delete-one original blocks per
tune and independent tune-deletion covariance factors preserve shared point
keys and masks across observables and references. Balancing is `(OS−SS)/T`
with eligible zero-partner triggers in the denominator. The result is a
conditional generator-level complete tune-bundle comparison with finite-MC
statistical uncertainty; it is not a systematic or detector-level prediction.

`package-manifest.json` pins the exact relative typed ROOT, receipts and compact
exports with SHA/size. Portable verification works from a copied directory
without the producer checkout or binary and explicitly reports external
execution as unchecked. Keep large analyzed/query/support/merged ROOT, build
packs and execution evidence in immutable external custody with scientific and
physical IDs, locator, custodian, retention and dependency pins. Only current,
owner-reviewed compact products belong in the collaboration release. Synthetic
fixtures must remain labelled TEST_ONLY.
Use `config/plot.json` as `SELECTED_PLOT_CONFIG` for the default presentation,
or pass the same checked-in alternative (for example `config/plot-all-tune.json`)
to render, figure verification and package build. The collaboration package
pins and carries those selected config bytes at a relative `config/` locator;
relocated verification reads that included file.
