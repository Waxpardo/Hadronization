# Heavy-flavour balancing across three PYTHIA tunes

This repository measures how a heavy-flavour balancing partner changes with event activity in generator-level proton-proton collisions.
It compares the complete MONASH, JUNCTIONS, and CLOSEPACKING tune configurations in PYTHIA 8.317 at 13.6 TeV.

The primary estimator is the change in the `Lambda_b` to `B-` balancing-yield ratio from `c1` to `c11`.
Class `c1` has the lowest multiplicity, while `c11` has the highest.

| comparison with MONASH | trend difference | total uncertainty | result significance |
|---|---:|---:|---:|
| JUNCTIONS | +0.35362 | 0.16134 | 2.19 sigma |
| CLOSEPACKING | +0.31172 | 0.15666 | 1.99 sigma |

These are provisional validation values, not publication conclusions.
The JUNCTIONS statistical-only value is 27.5 sigma, but quoting it alone overstates the result by more than one order of magnitude.
The measurement is systematics-dominated, and its current uncertainty excludes the unfinished S4 source.
[Results](docs/RESULTS.md#7-result-after-systematic-uncertainties) establishes the values and their scope.

The comparison is bundle-to-bundle among complete tune configurations.
It attributes no measured difference to colour reconnection, junctions, close packing, or another individual mechanism.
[Physics](docs/PHYSICS.md#interpretation-of-tune-differences) defines this interpretation limit.

## What this study does

The study asks which heavy hadrons carry compensating charm or beauty around a hard heavy-flavour trigger.
It resolves 300 signed trigger-associate pairs by species, relative azimuth, and multiplicity class.

PYTHIA forces hard-heavy production, so the sample is not minimum bias.
Each successful event contains one hard charm or beauty pair by construction.
The multiplicity labels instead come from a separate MONASH minimum-bias sample.

The publication scope is generator level.
The experiment-comparable selection applies branching-fraction weights, but it has no detector model.
[Physics](docs/PHYSICS.md) defines the observable, sample, selections, and decomposition meanings.

Most readers can use the repository in this order:

| priority | task |
|---:|---|
| 1 | Check one published number from committed evidence. |
| 2 | Read the method and uncertainty definitions. |
| 3 | Rebuild the committed result tables and validation reports. |
| 4 | Rerun the analysis with the external campaign data and pinned runtime. |

The first three tasks need only files that travel with this repository.
The fourth task needs external data, cluster storage, and the recorded runtime.
[Reproducibility](docs/REPRODUCIBILITY.md#1-what-reproducible-means-here) defines both scopes.

## Results in one page

The endpoint contrast measures the trend without fitting a curve.
For each tune, it subtracts the ratio at `c1` from the ratio at `c11`.

| tune | central-ground share (%) | `R(c1)` | `R(c11)` | `R(c11) - R(c1)` |
|---|---:|---:|---:|---:|
| MONASH | 52.4959 +/- 0.0074 | 0.18645 +/- 0.00692 | 0.16192 +/- 0.00258 | -0.02453 +/- 0.00739 |
| JUNCTIONS | 58.2318 +/- 0.0078 | 0.21408 +/- 0.00873 | 0.54317 +/- 0.00590 | +0.32909 +/- 0.01053 |
| CLOSEPACKING | 54.1697 +/- 0.0112 | 0.21624 +/- 0.00765 | 0.50344 +/- 0.01129 | +0.28719 +/- 0.01364 |

The central-ground share belongs to the complete four-category structural partition.
The ratio columns use the `Lambda_b` balancing yield divided by the `B-` balancing yield.
[Results](docs/RESULTS.md#2-three-tune-species-decomposition) provides the full tables and artifact sources.

MONASH declines gently rather than remaining flat.
Its endpoint contrast differs from zero by 3.3 sigma before systematic comparison between tunes.

The two other configurations rise strongly with multiplicity.
Their straight-line fits have poor chi-square values, so the endpoint contrast remains the measurement.
[Statistics](docs/STATISTICS.md#trend-summaries-and-fit-diagnostics) defines the contrast and diagnostic fit.

The measured tune separations remain positive in all seven generation-dependent variation renders.
The JUNCTIONS-minus-MONASH trend separation ranges from +0.23269 to +0.44463 across those renders.

The provisional budget finds 49 of 72 per-cell comparisons larger than their total uncertainty.
The budget generally establishes the separation from `c5` through `c11`.
It does not establish the separation below `c5`.
[Results](docs/RESULTS.md#7-result-after-systematic-uncertainties) states the complete verdict.

## Observable and analysis scope

A trigger is the heavy hadron from which the analysis counts a pair.
An associate is the second hadron in that registered pair.

Heavy-flavour sign follows quark content, not electric charge.
For beauty, $q_b=n_b-n_{\bar b}$.
`B+` has `q_b = -1`, while `Lambda_b` has `q_b = +1`.
The `B+` and `Lambda_b` pair is therefore opposite-sign.

Only the trigger needs resolved ancestry from the selected hard process.
If both particles needed that ancestry, the selection would remove same-sign pairs by construction.
The `kUnresolved` category removes trigger candidates only.

For one trigger and associate pair, the integrated balancing yield is

```text
Y_bal = (N_OS - N_SS) / N_trig
```

Uncorrelated combinatorial associates fill both sign counters equally in expectation.
The subtraction cancels that contribution without identifying the trigger's true balancing partner.
The denominator comes from the dedicated trigger object `hTrKinematics`, never from a pair-correlation projection.

Triggers require `pT > 1.0 GeV/c`.
Associates require `pT > 0.15 GeV/c`.
Both roles require `|eta| <= 4`.

The operational event-activity counter requires a final, charged particle with
no heavy constituent, `pT > 0.15 GeV/c`, and `|eta| <= 1`.
It defines eleven absolute multiplicity classes with half-integer boundaries.
Class `c1` contains `N_ch` from 0 through 2.
Class `c11` contains `N_ch` of 33 or more.

The top-percentile labels run opposite to the class index.
The `0.0-8.4%` label denotes the most active events and belongs to `c11`.
[Terms](docs/TERMS.md#the-one-entry-that-is-not-a-naming-choice) fixes this direction.

The production decay policy undercounts the paired MONASH minimum-bias
experimental-decay convention by 0.7670%. Propagating that measured shift
through the current boundaries changes no class membership, but the bias has
not been measured in the forced hard-heavy sample and the percentile labels
are not corrected by this result.

The structural decomposition partitions all species and sums to 100 percent.
The experiment-comparable selection does not form a partition and does not sum to 100 percent.

That selection only regroups species onto ground states with branching-fraction weights.
It includes no decay kinematics, acceptance, efficiency, resolution, or multiplicity-class migration.
[Physics](docs/PHYSICS.md#structural-and-experiment-comparable-decompositions) gives both definitions.

## Repository map and evidence model

The PUBLIC file set spans thirteen top-level directories.
Each directory has one reader-facing role.

| directory | role |
|---|---|
| `AnalysisScripts/` | Frozen generated contracts, decay maps, and committed anchors under its historical name. |
| `references/` | The PUBLIC bibliography. |
| `Validation/` | ROOT validators and fail-closed boundary checks. |
| `results/` | Machine-readable results, systematics products, and validation evidence; accepted scientific figures enter `results/figures/main/` only with their receipts. |
| `analysis/` | Stage 2 reduction code and pair-level diagnostic reducers. |
| `config/` | Editable scientific contracts, selectors, registries, and dependency pins. |
| `docs/` | The eight spine documents and retained records. |
| `extraction/` | Stage 4 table, trend, and uncertainty programs. |
| `generation/` | Stage 1 producer code, tune cards, registries, and campaign submission. |
| `merging/` | Stage 3 central and block merge programs. |
| `plotting/` | Stage 5 ROOT plotting, configuration generation, and input or coverage validation. |
| `tests/` | Source, schema, statistics, output, and documentation contract tests. |
| `tools/` | Campaign, environment, generation, validation, and repository tools. |

[Components](docs/COMPONENTS.md#how-to-read-the-catalog) establishes this directory map.

`AnalysisScripts/` retains its historical name because digest pins forbid moving its published anchors.
Treat it as immutable published artifacts, not the active analysis stage.
[Components](docs/COMPONENTS.md#contracts-registries-and-generated-files) explains that exception.

The evidence model separates five object types:

| object | function |
|---|---|
| Source code | Defines what each executable calculates or validates. |
| Configuration | Defines scientific choices, schemas, registries, selectors, and runtime pins. |
| Anchor | Preserves a run output needed to check a published value. |
| Receipt | Records what one stage saw and whether its boundary passed. |
| Derived result | Stores a table, delta, trend, or verdict in CSV or JSON. |

A digest proves byte identity, not scientific correctness.
A gate checks a declared boundary before the next stage starts.
[Pipeline](docs/PIPELINE.md#dataflow-and-sources-of-truth) maps the authorities across all five stages.

Publication meaning is separate from storage type:

| role | meaning |
|---|---|
| Scientific result | A paper-used value or ROOT-derived figure with accepted inputs, uncertainties, receipt, and visual review. |
| Reproduction evidence | A portable table, configuration, digest, receipt, or test that supports a result. |
| Validation | A pass or fail check of a declared contract. |
| Diagnostic | An exploratory or investigative measurement that is not automatically a result. |
| History | A superseded record retained for provenance, never a runnable PUBLIC dependency. |

The ROOT entrypoint is `plotting/run_paper_plots.sh`.
Its selected central and ten-block campaign inputs remain external, and this checkout contains no complete accepted figure-byte set under `results/figures/main/`.

## Requirements and environment check

The runtime contract pins PYTHIA 8.317 and ROOT 6.30.01.
The PYTHIA source is the unmodified official tarball with its SHA-256 recorded in `config/dependencies.conf`.

The repository has no portable, tested PYTHIA build recipe or container.
A full pipeline run therefore needs a compatible local installation or the recorded cluster environment.

Create a local dependency file before changing machine-specific paths:

```bash
make setup
```

Edit `config/dependencies.local.conf`, then inspect the runtime:

```bash
source ./setupEnv.sh
make doctor
```

Build the producer and run the repository checks:

```bash
make build
make check
```

`make doctor` reports missing dependencies but always returns success.
`make build` refuses unresolved compilers, ROOT, PYTHIA, or required paths.
`make check` runs source contracts and then evaluates the runtime.

`setupEnv.sh` checks both versions only when ALICE CVMFS is available.
Off CVMFS, the final verdict independently checks both ROOT and PYTHIA against
their exact version pins.

Use the following declaration only for source-contract work on an off-pin host:

```bash
HF_ALLOW_UNPINNED_ENV=1 make check
```

That command does not certify external campaign data, a production runtime, or a published extraction.
[Reproducibility](docs/REPRODUCIBILITY.md#2-runtime-and-build-inputs) records these runtime limits.
[Runtime](environment/ROOT_PYTHIA.md) gives the portable setup boundary and
the exact pinned identities in one place.

## Fast path from committed evidence

This procedure checks one published decomposition value from the committed extraction anchors.
It needs Python 3 but does not need ROOT, PYTHIA, or cluster data.

### Fast-path step 1

Create a temporary output file.

   ```bash
   table_output="$(mktemp)"
   ```

### Fast-path step 2

Run the table extractor on the three tune anchors.

   ```bash
   python3 extraction/three_tune_table.py \
     MONASH=AnalysisScripts/anchors/merged_monash_dedup \
     JUNCTIONS=AnalysisScripts/anchors/merged_junctions_dedup \
     CLOSEPACKING=AnalysisScripts/anchors/merged_closepacking_dedup \
     > "$table_output"
   ```

### Fast-path step 3

Calculate the output digest.

   ```bash
   shasum -a 256 "$table_output"
   ```

### Fast-path step 4

Require this SHA-256:

   ```text
   a46a7f6b96f668177ee600746e51eadf1dfaabdaceac07c1265ef5d7d0fc930d
   ```

### Fast-path step 5

Read the central-ground rows.

   ```bash
   grep kCentralGround "$table_output"
   ```

The JUNCTIONS row must contain `58.2318 ± 0.0078` percent.
The extractor derives that value from one central and ten block tables.

### Fast-path step 6

Run the independent table contract.

   ```bash
   python3 tests/test_three_tune_tables.py
   ```

This path starts at committed extraction anchors.
It does not recreate the absent raw, reduction, or merged campaign inputs.
[Reproducibility](docs/REPRODUCIBILITY.md#7-reproduce-from-committed-evidence) defines that boundary.

Use a separate temporary directory for the other committed-evidence rebuilds:

```bash
evidence_output="$(mktemp -d)"
python3 tools/build_decay_parent_map.py \
  AnalysisScripts/anchors/f4_probe/f4_probe_v1.out \
  --ordinals AnalysisScripts/species_ordinals_v2.json \
  --out "$evidence_output/map_v1_1.json"
python3 tools/build_decay_parent_map_v2.py \
  AnalysisScripts/anchors/f4_probe/f4b_probe.out \
  --ordinals AnalysisScripts/species_ordinals_v2.json \
  --v1 "$evidence_output/map_v1_1.json" \
  --weights AnalysisScripts/anchors/extraction_dual/per_species.csv \
  --out "$evidence_output/map_v2.json"
```

The second map builder must report internal digest `c9593c9c0a7c4ec2ed6b53462255d4f04dcb4a5f5bd029217f479e5eecbb85fb`.

Check the committed integrated-yield rows and rebuild the systematics reports:

```bash
python3 tests/test_per_class_control.py
python3 extraction/write_per_class_report.py \
  --report results/systematics/20260820/per_class_deltas_seven.json \
  --out-markdown "$evidence_output/per_class.md" \
  --out-csv "$evidence_output/per_class.csv"
python3 extraction/write_combination_report.py \
  --combination results/systematics/20260820/per_class_combination.json \
  --out-markdown "$evidence_output/combination.md" \
  --out-csv "$evidence_output/combination.csv"
```

The test checks twelve retained integrated-yield rows, but the source plotting log is absent.
The report writers render committed results and cannot rederive the external variation inputs.

The final scientific figures are ROOT-derived outputs of
`plotting/run_paper_plots.sh`. Their full campaign inputs and final accepted
bytes are external to this checkout.
This repository therefore does not claim to rebuild a scientific figure from compact evidence alone.
The committed tables and validation records remain reproducible with the commands above.

## End-to-end reproduction

The pipeline has five stages and one immutable raw-file boundary.
Generation writes raw files once, while every downstream stage reads them without modification.

```text
tune card -> generation -> raw file -> reduction -> pair directory
          -> merging -> merged product -> extraction -> tables -> plotting -> figures
```

| stage | authoritative entrypoint | output |
|---|---|---|
| 1. Generation | `generation/submit/runCondorJob.sh` | One validated raw file per job. |
| 2. Reduction | `analysis/run_status_analysis.sh` | One validated 300-file pair directory per raw file. |
| 3. Merging | `merging/merge_root_files.sh` | One central and ten blocks per tune. |
| 4. Extraction | `extraction/extract_species_decomposition.py` | Species, category, and observable tables. |
| 5. Plotting | `plotting/run_paper_plots.sh` | Staged and promoted publication figures. |

The selected campaign record reports 1,000 raw files and 100 million events per tune.
The external manifest and raw files do not travel with this repository.
This checkout therefore cannot recount or rehash the reported 3,000-file union.

The retained campaign record reports 562.5 CPU-hours for event generation.
The scheduler evidence does not travel, so this is a record-only planning value.

Full regeneration needs the pinned runtime, HTCondor, cluster storage, and the historical burned-seed ledger.
Restore that ledger before rendering any campaign.

Start with generation and reduction:

| order | action |
|---:|---|
| 1 | Configure, build, and check the pinned runtime. |
| 2 | Render generation with an explicit campaign ordinal. |
| 3 | Submit held jobs, inspect them, and release them. |
| 4 | Retry only missing slots with a new attempt seed. |
| 5 | Seal the promoted raw files in a canonical manifest. |

Continue with downstream processing:

| order | action |
|---:|---|
| 6 | Reduce every manifest row into one pair directory. |
| 7 | Merge each tune into one central and ten blocks. |
| 8 | Run schema-specific closure before extraction. |
| 9 | Extract each central and block with decay map v2. |
| 10 | Select the campaign explicitly before plotting. |

The principal commands are:

```bash
make submit-full CAMPAIGN=HF_RUN3_V1 ORDINAL=3 JOBS=1000 EVENTS=100000
make manifest CAMPAIGN=HF_RUN3_V1
bash generation/submit/submit_status_analysis.sh \
  FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT --dry-run
HADRONIZATION_EXPECTED_PAIR_SCHEMA=v3 \
  bash merging/merge_root_files.sh \
  FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT ANALYZED_DATA_BASE
python3 extraction/extract_species_decomposition.py MERGED_PRODUCT \
  --decay-map AnalysisScripts/decay_parent_map_v2.json --out OUTPUT_DIR
DATASET_SELECTOR=config/dataset_selector_hf_run3_v1.json \
  bash plotting/run_paper_plots.sh TARGET
```

The merge selector `HADRONIZATION_EXPECTED_PAIR_SCHEMA` has no default.
The plotting selector also has no default dataset in the combined file.
These refusals prevent plausible outputs from using the wrong schema or campaign.

With this checkout alone, the full route stops before reduction of the published dataset.
The selected raw files, manifest, pair directories, and merged products remain external.
[Pipeline](docs/PIPELINE.md) defines every boundary, and [Reproducibility](docs/REPRODUCIBILITY.md#8-regenerate-the-full-chain) gives the complete procedure.

## Verification and expected outputs

Use positive verdicts and expected digests, not only process exit codes.
ROOT can report an error while its shell process still returns success.

| check | expected result |
|---|---|
| Registry generation | Each generator `--check` command reports no drift. |
| Three-tune table | SHA-256 `a46a7f6b96f668177ee600746e51eadf1dfaabdaceac07c1265ef5d7d0fc930d`. |
| JUNCTIONS central-ground row | `58.2318 ± 0.0078` percent. |
| Decay map v2 | Internal digest `c9593c9c0a7c4ec2ed6b53462255d4f04dcb4a5f5bd029217f479e5eecbb85fb`. |
| Pair-block closure | `CANONICAL_PAIR_BLOCK_CLOSURE_PASS` with schema-derived comparison counts. |

Run the source-contract suite with the pinned runtime:

```bash
make check
```

Closure proves exact central-to-block addition.
It does not prove that the entries are unique.
Object ownership, deduplication, and plausibility checks provide separate protection.
[Statistics](docs/STATISTICS.md#closure-and-integrity-checks) explains this limit.

## Known limits and incomplete work

Four limits qualify the headline result:

- The corrected incomplete budget gives 2.19 sigma and 1.99 sigma for the two tune comparisons.
- The tune cards differ in 28 parameters across nine families, so the comparison identifies no individual mechanism.
- The code applies no correction to quoted per-cell sigma values across 72 comparisons.
- The configuration registers S4, but every current total and verdict excludes it.

Four method boundaries also limit interpretation:

- The repository has not measured cross-class or cross-observable covariance.
- Quadrature assumes untested independence between the retained systematic sources.
- The 2026-08-21 derived-SEM correction changes four two-sigma classifications; S4 and the campaign hang-selection bias remain open.
- The result is generator level and includes no detector response.

The S4 omission makes each current total provisional.
Any nonzero S4 contribution would increase the quoted total uncertainty under the current combination rule.

The per-cell significance values do not define a global significance.
The repository claims no trial-corrected probability across the 72 comparisons.

The experiment-comparable selection is not a detector-level prediction.
It omits decay kinematics, acceptance, efficiency, resolution, and bin migration.

Several auxiliary claims also lack their immediate inputs.
The repository cannot repeat exact integrated closure or the virtual-trigger comparison.
The all-tune species validation also lacks its original raw fixtures.

[Systematics](docs/SYSTEMATICS.md#coverage-limits-and-evidence-index) defines uncertainty coverage.
[Results](docs/RESULTS.md#10-limits-on-interpretation) defines the publication limits.

## Data availability, citation, and license

The repository ships code, configurations, receipts, digests, committed
anchors, and result JSON files.
These files support the fast path and source-contract checks.

The selected raw campaign data lives on a cluster filesystem.
The campaign record reports about 270 GB across 3,000 raw files.
This checkout cannot independently verify that external union.

The selected manifests, reduction outputs, merged products, and most ROOT-rendered figures also remain external.
No public download route, preservation service, or archive identifier exists in this repository.

The repository contains no `LICENSE` file because the owner has not selected
software, documentation, data, or figure licences. It therefore states no
general reuse terms.

`CITATION.cff` is present as a parseable, visibly provisional draft. The owner
has not approved authorship order, affiliations, identifiers, release identity,
or licensing, and no DOI or release archive identifier exists.

A reader can check selected published values and validation records from committed evidence.
A reader cannot reproduce the publication dataset from raw files without external access.
[Reproducibility](docs/REPRODUCIBILITY.md#10-storage-and-data-availability) gives the exact supported and unsupported work.
[Data availability](docs/DATA_AVAILABILITY.md) separates committed evidence,
external merged products, raw campaign data, and the Git-only boundary.
[Release metadata](docs/RELEASE_METADATA.md) records the owner decisions that
still block citation and licensing.

## Documentation and evidence index

The eight documents answer separate reader questions:

| document | question answered |
|---|---|
| [Physics](docs/PHYSICS.md) | What does the observable measure, and what physics scope does it have? |
| [Statistics](docs/STATISTICS.md) | How are central values, block errors, trends, and uncertainty combinations calculated? |
| [Pipeline](docs/PIPELINE.md) | How do raw files become validated tables and figures? |
| [Components](docs/COMPONENTS.md) | What does each executable do, and which contract enforces it? |
| [Systematics](docs/SYSTEMATICS.md) | Which choices were varied, how were they combined, and what remains incomplete? |
| [Results](docs/RESULTS.md) | What are the central values, trend result, figures, and interpretation limits? |
| [Reproducibility](docs/REPRODUCIBILITY.md) | Which claims can this checkout reproduce, and which need external data? |
| [Terms](docs/TERMS.md) | Which exact term and class direction does every document use? |

Machine-readable result artifacts live under `results/systematics/20260819/` and `results/systematics/20260820/`.
The digest registry, `docs/GOLDEN_OUTPUTS.md`, records expected bytes and recipes for named artifacts.

Use the spine documents for interpretation.
Use retained run records and anchors to inspect the evidence behind their claims.
