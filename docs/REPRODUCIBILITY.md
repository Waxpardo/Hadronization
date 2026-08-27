# Reproducibility

## 1. What reproducible means here

This repository supports two different reproduction scopes. Committed anchors support local checks, while the full campaign needs external cluster data.

| scope | available input | supported result |
|---|---|---|
| Committed evidence | Code, configurations, anchors, receipts, and digests | Recompute selected tables, class labels, and validation records. |
| Full regeneration | The pinned runtime and external campaign data | Regenerate raw files, reduction outputs, merged products, tables, and figures. |

A matching digest establishes byte identity. It does not establish that the bytes encode the correct measurement.

A passing recipe establishes derivability only for its named inputs. It does not replace validation of earlier stages.

Scientific results, reproduction evidence, validation, diagnostics, and history are distinct roles.
Only a scientific result may enter the manuscript.
Evidence supports it, validation checks a contract, and diagnostics investigate it.
History records superseded work without becoming a runnable dependency.

## 2. Runtime and build inputs

`environment/ROOT_PYTHIA.md` is the compact runtime contract. It records the
pinned identities, portable setup commands, off-pin limitations, and external
inputs without embedding a personal path in live instructions.

The runtime contract pins PYTHIA 8.317 and ROOT 6.30.01. `config/dependencies.conf` records both versions and their installation paths.

PYTHIA uses the unmodified official 8.317 tarball. The recorded SHA-256 is `1ae551d14dac495ddfe6b344792035ebe410fe6c6004d44a335e0ece0e745adf`.

ROOT uses the ALICE package `v6-30-01-alice5-2`. Its `root-config --version` value is `6.30.01`, while the package name uses `6.30/01`.

Use `config/dependencies.local.conf` for machine-specific paths. `make setup` copies the tracked example when the local file is absent.

`setupEnv.sh` checks both reported versions only when ALICE CVMFS is available. It returns before completing setup when either reported version differs.

`setupEnv.sh` does not leave the caller's environment unchanged on mismatch. It exports `HADRONIZATION_BASE` and changes runtime paths before its version checks.

Without CVMFS, `setupEnv.sh` warns and exports configured values without checking either executable. `tools/environment_verdict.sh` independently checks both the ROOT and PYTHIA version strings against the exact pins.

`setupEnv.sh` still does not enforce the stronger export-nothing-on-mismatch contract. The environment verdict and artifact exporter refuse either runtime-version mismatch, including on a non-CVMFS host.

`make check` runs the environment verdict last. Set `HF_ALLOW_UNPINNED_ENV=1` only for source-contract checks on an off-pin host.

The build commands have different failure meanings:

| command | result meaning |
|---|---|
| `make doctor` | Reports missing dependencies and paths, but always returns success. |
| `make build` | Refuses when the compiler, ROOT, PYTHIA, or required paths do not resolve. |
| `make check` | Checks source contracts, then refuses an off-pin runtime unless the caller declares the limitation. |

The repository has no portable, tested PYTHIA build recipe. It also has no container that rebuilds the recorded stock installation.

## 3. Fixed scientific contracts

The scientific contracts use generated headers, validators, and digests. Each contract has one controlling artifact.

| contract | controlling artifact | failing check |
|---|---|---|
| Signed species and 300 pairs | `config/heavy_flavour_species_v1.json` and `config/heavy_flavour_pair_registry_v1.json` | `tools/generate_registry_artifacts.py --check` |
| Pair-file objects | `config/pair_file_object_contract_v1.json` | `tools/generate_pair_object_contract.py --check` |
| Species axis | `contracts/species_ordinals_v2.json` | The generated-header check and merged-file digest check |
| Multiplicity classes | `config/multiplicity_percentile_classes_v2.json` | Plot tests and each v2 per-tune multiplicity boundary receipt |
| Tune differences | `config/tune_difference_allowlist_v1.json` | `tools/validate_tune_cards.py` |
| Systematic variations | `config/systematics_variations_v1.json` | `tools/make_systematic_cards.py --check` |
| Decay regrouping | `contracts/decay_parent_map_v2.json` | Map builders, extraction tests, and the species-axis pin |

The species axis has 202 entries. Its FNV-1a digest is `646f310f78126267`, which each v3 merged file must carry.

The multiplicity contract fixes percentile windows `90-100, 80-90, ...,
1-10, 0-1%`. For every tune, plotting initialization loads that tune's merged
`summed MULTIPLICITY` histogram, resolves all percentile thresholds, and
requires a disjoint, exhaustive integer partition. Thresholds may differ
between tunes. The source histogram identity, thresholds, achieved fractions,
class-contract digest, and validation verdict are written to a v2 receipt.

The retained MONASH minimum-bias CSV is calibration evidence only. It does not
define another tune's class boundaries.

## 4. Dataset identity and campaign provenance

The dataset selector names a campaign and its sealed inputs. `config/dataset_selector_hf_run3_v1.json` selects `HF_RUN3_V1` and names its external freeze.

`HADRONIZATION_CAMPAIGN` binds each consumer to the selector's campaign. Another campaign's valid sealed freeze cannot satisfy that identity check.

Each generation job records these identities before production:

- repository commit;
- effective tune-card digest;
- producer-binary digest;
- campaign and campaign ordinal;
- tune, logical identifier, attempt, and seed.

`generation/submit/runCondorJob.sh` recomputes the commit and both digests before generation. It refuses a mismatch or tracked checkout change.

The worker validates a partial raw file before promotion. The validation receipt binds the verdict to the raw-file digest and validation dependencies.

The campaign record reports 3,000 promoted raw files and 300 million requested successes. It reports manifest digest `fcd96eaebd4dc11f071a2c8db8849f6a4cc19b764622a796664e524b27d0fc80`.

This checkout cannot rehash that union. The selector's manifest and every selected raw file remain on the cluster filesystem.

## 5. Seeds, attempts, and discard accounting

`tools/campaign.py` derives one seed from four recorded coordinates:

```text
seed = 100000001
     + 10000000 * campaign_ordinal
     +  1000000 * tune_index
     +   100000 * attempt
     +              job_index
```

The 10,000,000-seed campaign band prevents overlap between campaign ordinals. The code permits ordinals 0 through 79 within PYTHIA's seed range.

For campaign ordinal 3, attempt 0 uses these 1,000-seed ranges:

| tune | first seed | last seed |
|---|---:|---:|
| MONASH | 130000001 | 130001000 |
| JUNCTIONS | 131000001 | 131001000 |
| CLOSEPACKING | 132000001 | 132001000 |

The renderer requires an explicit ordinal. It also rejects any seed already present in the append-only burned-seed ledger.

The renderer burns seeds when it writes a submit file. This rule prevents two rendered files from reserving the same seed.

The historical burned-seed ledger does not travel with this repository. Therefore, this checkout cannot prove that historical campaigns used disjoint seeds.

The canonical campaign uses 100,000 successful events per job and 1,000 canonical slots per tune. Smaller jobs limit work lost to a generator hang.

The pilot record reports four wedged jobs after about 3.63 million junction-tune events. A repeat with one recorded seed and card did not reproduce its wedge.

The retained pilot inputs cannot establish the wedge mechanism. The final campaign record also leaves event-content correlation unmeasured.

The current renderer submits the same number of primary slots for every tune. It does not implement the earlier two-times over-submission design.

The hang guard holds a job after 3,600 CPU seconds or 14,400 wall seconds. `tools/resubmit_held.py` retries only missing slots with a new attempt seed.

The manifest builder orders promoted logical identifiers before assigning canonical slots. It never selects the first jobs to finish.

The campaign record reports 3,127 attempts and 127 discarded attempts. It reports 0, 63, and 64 discarded attempts for the three tunes.

The external ledger and attempt metadata are absent. This checkout cannot independently derive those discard counts or rates.

## 6. Anchors, golden outputs, and digests

An anchor is a run output copied into the repository. A golden output adds a recorded recipe and expected digest.

`docs/GOLDEN_OUTPUTS.md` distinguishes three checks:

- a file SHA-256 covers all bytes;
- a map's internal digest excludes its digest field;
- a content invariant checks a count or equality.

The registry prevents silent byte drift. A regeneration recipe also detects broken paths, missing inputs, and changed serialization.

Some important committed checks are:

| object | expected value |
|---|---|
| Species-axis table | 202 entries; FNV-1a `646f310f78126267` |
| Current decay map | file SHA-256 `58081aa2f87cb67141259f2b74a5057777a6c8eaa5049446fd3f47b13a1c84da` |
| Three-tune table output | SHA-256 `a46a7f6b96f668177ee600746e51eadf1dfaabdaceac07c1265ef5d7d0fc930d` |

ROOT-generated PDF, PNG, and macro files are not byte-stable. Their contract uses pinned inputs, pinned ROOT, a recorded command, and a numeric receipt.
Accepted scientific bytes have the canonical destination `results/figures/main/`.
They compare the three complete tune bundles, obtain `N_trig` from `hTrKinematics`, and carry ten-block uncertainties.

The plotting stage writes into a staging directory. It promotes outputs only after the multiplicity boundary receipt passes.

The repository quarantines `evidence/extraction_dual` for charge-resolved use. Its provenance is incomplete, and later traceable anchors contradict its charge result.

Recorded receipt and anchor paths predate the storage consolidation. They are historical paths and need not exist at their recorded locations.

A file move does not change its content. Therefore, every recorded digest remains valid after a byte-preserving move.

## 7. Reproduce from committed evidence

The following procedure checks one published number without external campaign data. It regenerates the final three-tune decomposition from committed anchors.

1. Create a temporary output file.

   ```bash
   table_output="$(mktemp)"
   ```

2. Run the table extractor on all three committed anchors.

   ```bash
   python3 extraction/three_tune_table.py \
     MONASH=evidence/merged_monash_dedup \
     JUNCTIONS=evidence/merged_junctions_dedup \
     CLOSEPACKING=evidence/merged_closepacking_dedup \
     > "$table_output"
   ```

3. Compute the output digest.

   ```bash
   shasum -a 256 "$table_output"
   ```

4. Require digest `a46a7f6b96f668177ee600746e51eadf1dfaabdaceac07c1265ef5d7d0fc930d`.

5. Read the JUNCTIONS `kCentralGround` cell.

   ```bash
   grep kCentralGround "$table_output"
   ```

The output must contain `58.2318 ± 0.0078` for JUNCTIONS. The script computes the percentage and block standard error from 11 CSV files.

Run the table contract test after the direct check:

```bash
python3 tests/test_three_tune_tables.py
```

This procedure starts at committed extraction anchors. It does not reproduce their absent raw, reduction, or merged inputs.

The current decay maps also rebuild from committed probe anchors:

```bash
python3 tools/build_decay_parent_map.py \
  evidence/f4_probe/f4_probe_v1.out \
  --ordinals contracts/species_ordinals_v2.json --out /tmp/map_v1_1.json
python3 tools/build_decay_parent_map_v2.py \
  evidence/f4_probe/f4b_probe.out \
  --ordinals contracts/species_ordinals_v2.json \
  --v1 /tmp/map_v1_1.json \
  --weights evidence/extraction_dual/per_species.csv \
  --out /tmp/map_v2.json
```

The second command must report internal map digest `c9593c9c0a7c4ec2ed6b53462255d4f04dcb4a5f5bd029217f479e5eecbb85fb`.

The committed result JSON files rebuild the integrated and class-resolved systematics tables:

```bash
python3 extraction/write_per_class_report.py \
  --report results/systematics/20260820/per_class_deltas_seven.json \
  --out-markdown /tmp/per_class.md --out-csv /tmp/per_class.csv
python3 extraction/write_combination_report.py \
  --combination results/systematics/20260820/per_class_combination.json \
  --out-markdown /tmp/combination.md --out-csv /tmp/combination.csv
```

These commands render committed results. They cannot rederive the variation deltas without the external render logs and merged products.

The final scientific figures do not rebuild from compact evidence alone.
They are ROOT-derived outputs of `plotting/run_paper_plots.sh` and require the
named external central and ten-block campaign products.
The runner currently creates candidates but does not write final-plot
provenance sidecars. Publication closure must separately supply the accepted
figure bytes and their checksum-bound final receipts.
It places those bytes under `results/figures/main/`;
this checkout currently carries only result tables and validation records for
that path.

`results/provenance/figure_acceptance_manifest_v1.json` records the current
fail-closed state. For each P1-P8 role, it lists the producer, configuration,
selector, inputs, numerical source, candidate digests, visual finding, and
retrieval requirement. It classifies all eight roles as candidates and accepts
none.

Check the machine record and its source pins locally:

```bash
python3 -m json.tool \
  results/provenance/figure_acceptance_manifest_v1.json >/dev/null
python3 tests/test_plot_reference_multiplicity_contract.py
```

The second command rehashes each tracked producer, configuration, selector,
registry, boundary artifact, and compact numerical source named by the
manifest. It cannot rehash the external ROOT inputs or absent candidate bytes.

The multiplicity boundaries also reproduce from committed evidence. Sum the MONASH CSV cumulatively and apply the procedure in Section 3.

The cumulative crossings reproduce all 11 boundaries exactly. The CSV SHA-256 is `6027dc0076cf48eb9b0e13c12014c20228ee63a8a2e0acba424bda7ed409475e`.

## 8. Regenerate the full chain

Full regeneration needs a cluster host, external storage, ROOT, PYTHIA, HTCondor, and the burned-seed ledger. Configure those dependencies before production.

The retained campaign record reports 562.5 CPU-hours for event generation.
The scheduler history and per-job CPU evidence do not travel, so this checkout cannot repeat that total.

Restore the authoritative burned-seed ledger before rendering. An empty replacement cannot detect reuse of a historical seed.

1. Create and edit the local dependency file.

   ```bash
   make setup
   ```

2. Source the runtime and inspect its resolution.

   ```bash
   source ./setupEnv.sh
   make doctor
   ```

3. Build and check the pinned checkout.

   ```bash
   make build
   make check
   ```

4. Render the full campaign with a registered ordinal.

   ```bash
   make submit-full CAMPAIGN=HF_RUN3_V1 ORDINAL=3 JOBS=1000 EVENTS=100000
   ```

5. Submit the rendered file in its held state.

6. Inspect the submit description, then release the jobs.

7. Wait for the queue to drain, then inspect campaign status.

   ```bash
   make status-full CAMPAIGN=HF_RUN3_V1
   ```

8. Dry-run each retry before applying it.

   ```bash
   python3 tools/resubmit_held.py HF_RUN3_V1 \
     --jobs 1000 --events 100000 --attempt 1 \
     --checkout "$PWD" \
     --seed-ledger "$HADRONIZATION_DATA_ROOT/project/runs/seed_ledgers/burned_seeds.txt"
   ```

9. Build the write-once canonical manifest after all slots exist.

   ```bash
   make manifest CAMPAIGN=HF_RUN3_V1
   ```

10. Dry-run the reduction submission from the sealed manifest.

    ```bash
    bash generation/submit/submit_status_analysis.sh \
      FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT --dry-run
    ```

11. Submit the reduction after the dry run passes.

    ```bash
    bash generation/submit/submit_status_analysis.sh \
      FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT --submit
    ```

12. Validate every pair directory before promotion.

13. Merge the central and ten blocks with the required schema.

   ```bash
   HADRONIZATION_EXPECTED_PAIR_SCHEMA=v3 \
     bash merging/merge_root_files.sh \
     FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT ANALYZED_DATA_BASE
   ```

14. Extract each central and block with the current decay map.

    ```bash
    python3 extraction/extract_species_decomposition.py MERGED_PRODUCT \
      --decay-map contracts/decay_parent_map_v2.json --out OUTPUT_DIR
    ```

15. Select the campaign explicitly before plotting.

   ```bash
   DATASET_SELECTOR=config/dataset_selector_hf_run3_v1.json \
     bash plotting/run_paper_plots.sh TARGET
   ```

Use workload output to assess progress. Do not infer a stall from one unchanged scheduler snapshot.

For raw-file readers, compare file access times with the job start. For active merged-file readers, inspect `/proc/PID/fd` and `/proc/PID/io`.

Use `rchar`, not `read_bytes`, for cached reads. Confirm the final positive verdict after the process exits.

Two compatibility entrypoints cannot run the current chain. `generation/run_hf.sh` supplies too few producer arguments, so use the canonical submit renderer.

`merging/make_subsamples.sh` resolves a nonexistent nested driver path. Call `merging/merge_root_files.sh` directly.

The tracked extraction chain requires explicit external merged and output
roots but contains no site-specific default. It resolves the tracked extraction
entrypoint from the checkout and stops when closure or extraction fails. Its
`DONE` line is valid only after both recorded return codes are zero.

## 9. Gates, receipts, and expected verdicts

Every gate protects a named stage boundary. A zero exit code alone is insufficient when ROOT can report an error without failing the shell.

| boundary | fail-closed evidence | failure caught |
|---|---|---|
| Submit rendering | Clean commit, exact digests, unused seed, explicit ordinal | The seed ledger rejected a cross-campaign seed collision. |
| Job start | Commit, card, and producer digest equality | Jobs refuse a checkout or binary that moved after rendering. |
| Raw promotion | Raw validator and immutable receipt | An invalid partial never receives the stable raw filename. |
| Reduction promotion | Pair-directory validator | The first reduction exposed unexpected closure objects before promotion. |
| Full reduction gate | One serial validation over the complete union | A wrong production root failed on the first directory in 0.75 seconds. |
| Merge start | Required pair schema and sealed manifest | The driver refuses a missing expected schema. |
| Merged-product promotion | Object, provenance, and manifest checks | A stale existing directory cannot be overwritten. |
| Closure | Expected counts plus the positive closure marker | A wrong object schema cannot pass with a smaller comparison count. |
| Plot promotion | Selector identity and boundary receipt | Five variation renders exposed a central-dataset selection error. |

The merge run record gives `status=PASS directories=3000 missing=0`. Its full gate report does not travel with this checkout.

The gate must process the union serially because it checks uniqueness across all directories. A split run would weaken that identity check.

The merge-scaling record gives these retained measurements:

| merge inputs | wall seconds | peak memory | elementary merge cost |
|---:|---:|---:|---:|
| 10 | 45.01 | 481,476 kB | 16.67 ms |
| 25 | 135.10 | 548,724 kB | 18.76 ms |
| 50 | 1,591.88 | 672,728 kB | 108.29 ms |

At 50 inputs, the v3 elementary cost was 0.354 times the recorded v2 cost. The 50-input result removed the registered merge-strategy escalation.

The recorded validator process used 442.3 MiB. The underlying measurement files are absent, so this checkout cannot repeat either measurement.

Closure must emit `CANONICAL_PAIR_BLOCK_CLOSURE_PASS` with the expected comparison counts. The wrapper must inspect that marker and not only the return code.

The retained fixture cannot reproduce exact integrated closure. `tests/fixtures/integrated_rows_nominal.log` omits the required `PAIR_COUNTS` lines.

The repository cannot reproduce the virtual-trigger closure. The named ROOT output and run record do not travel with the repository.

## 10. Storage and data availability

The repository holds code, configurations, receipts, digests, anchors, and
result JSON files. These files support the local checks in Section 7.

The raw campaign data lives on a cluster filesystem. The campaign record reports about 270 GB across the selected 3,000 raw files.

The selected manifests, reduction outputs, merged products, and most final ROOT-rendered outputs also remain external.

Without those files, a reader can do the following work:

- Inspect every stage and contract.
- Regenerate selected tables from anchors.
- Reproduce the multiplicity boundaries.
- Inspect the planned figure programme, its blocked acceptance manifest, and
  the committed numerical inputs that are present.
- Verify committed digests and source-contract tests.

Without those files, a reader cannot do the following work:

- Recount or rehash the selected 3,000 raw files.
- Rerun reduction, merging, or closure on the publication dataset.
- Rebuild extraction anchors from their immediate inputs.
- Reproduce exact integrated closure or virtual-trigger closure.
- Recover every final ROOT-rendered figure and its receipt.

No tracked file exists under `AnalyzedData/`. Therefore, the legacy FinalAnalysis and PtMultiplicity diagnostics remain source-only and are not publicly reproducible.

The repository gives no public download route for the external data. It also gives no preservation service, archive identifier, or recovery authority.

`docs/DATA_AVAILABILITY.md` is the release-facing statement for this boundary.
It distinguishes committed compact evidence, external reduced and merged
products, external raw campaign data, and what Git alone can reproduce.

## 11. Known irreproducibility and recovery boundaries

Public data access remains unresolved. The repository does not state how an external reader can obtain the sealed raw and downstream campaign products.

Long-term preservation remains unresolved. No public archive binds the external files, manifests, and receipts into one preserved object.

Archive identity remains unresolved. The repository has no DOI or release
archive identifier. `CITATION.cff` is a provisional draft whose author order
and metadata require owner approval, and no license file exists.

The runtime remains site-dependent. The repository records an official PYTHIA tarball digest but provides no portable, tested build procedure.

The historical seed evidence remains external. Loss of the burned-seed ledger would prevent an independent collision audit across past campaigns.

The full-gate result and scaling measurements remain record-only. Their external reports and measurement inputs are unavailable from this checkout.

The final ROOT-rendered figure set remains incomplete here. This checkout
tracks no accepted scientific figure-byte set with complete final receipts.
The acceptance manifest records zero accepted roles. It fails closed on the
unavailable external storage, absent final bytes, disabled sidecar recorder,
derived-uncertainty mismatch, missing S4 deltas, and missing integrated closure
rows. It also records the v3-file/v2-sidecar disagreement and the seven stale
systematic harvest configurations.

The legacy generated heavy-flavour summary is not recoverable from current inputs. Its retained table came from a superseded raw schema whose untracked inputs are absent.

The old counting macro cannot read raw-v7 files. A replacement must count all 3,000 raw files again.

The site-bound extraction wrapper weakens recovery. A portable rebuild must replace its external path and stop on every failed stage.
