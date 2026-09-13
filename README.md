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
`--request` and `--request-sha` for a reviewed subset. `reduce verify` and
`reduce explain` require the written ROOT and report paths plus the report's
SHA-256. The explicit `--charm-trigger 411` selects the D⁺ alternate; the
default is D⁰.

Query, collection, merge, reduction and plotting require independently pinned
input paths and SHA-256 values; see their command help before running them on
an accepted campaign. Keep the work/output directories outside source control
and never reuse an output path. A small explicitly `TEST_ONLY` fixture verifies
the local interfaces; it is not a physical PYTHIA prediction. The tracked
`results/` material predates the current v2.2 selection and THnSparse/v4
contract. It is preserved as historical evidence, **not** a completed current
P1–P8 or 300-million-event result. Full paper numerics require the authenticated
physically merged 323-query-shard/3,000-source collection and its site/admission
receipts. The Nikhef runtime, storage and scheduler gates have not been passed
by a local verification run.

`./hadronization generate` inventories deterministic nominal work by default.
Only an explicit continuation submission with a configured site may contact a
scheduler. Accepted raw files live under ignored `data/raw/`; attempt evidence
and scratch live under ignored `data/work/`. `./hadronization clean` is dry-run
by default and does not remove raw files or durable attempt evidence.
