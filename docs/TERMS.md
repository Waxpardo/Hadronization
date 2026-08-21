# Terms — one word, one meaning

**The rule this file exists to hold.** One thing has one name, and that name
does not change between documents. Where the code has already named something,
the prose adopts the code's name rather than improving on it.

**Read the `fixed by` column first.** A term with an identifier in that column is
not a style preference. It is the name a field, a class label, a schema or a
filename already carries, and changing it in prose puts the document out of step
with the thing it describes.

**This registry covers terms that drift.** A word earns a row here when the tree
already uses two or more names for one thing, or when getting it wrong inverts a
meaning. It is not a dictionary of every noun in the project.

---

## THE ONE ENTRY THAT IS NOT A NAMING CHOICE

> ### `c1` is the LOWEST multiplicity class. `c11` is the HIGHEST.
>
> **The percentile labels run the other way, and that is the trap.**
>
> | class | N_ch range | percentile label |
> |---|---|---|
> | **`c1`** | **lowest** activity, from `boundary_nch = -0.5` | **`88.2-100.0%`** |
> | **`c11`** | **highest** activity, from `boundary_nch = 32.5` | **`0.0-8.4%`** |
>
> The labels are percentiles of the MONASH minimum-bias distribution counted
> from the **most active** end, so `0.0-8.4%` means *the top 8.4 % by activity*
> — the busiest events, not the quietest. The class index and the percentile
> number move in opposite directions.
>
> **A trend quoted against the wrong direction is reported backwards.** Every
> statement of the form "the ratio rises with multiplicity" depends on this, and
> the histogram names carry both halves at once: `hDPhic1_MB88p197_100` and
> `hDPhic11_MB0_8p422`.
>
> **Say which end you mean.** Write "from `c1` (lowest activity) to `c11`
> (highest)" rather than "across the classes", and never quote a percentile label
> without saying that it counts from the active end.

---

## THE REGISTRY

| canonical term | what it means | do not use | fixed by |
|---|---|---|---|
| **block** | one of the ten equal partitions of a campaign's analysed files, used to compute the standard error on every published number | `sub-block`, `chunk` | `block_count: 10`, `block_NN.jsonl`, `block_1`…`block_10` |
| **subsample directory** | the plotting chain's name for the same ten-way partition, as it exists on disk | `sub-sample` | `subsample_base`, `combined_root_subSamples_<TUNE>` |
| **central** | the merge over a campaign's whole file set, as opposed to one block | `full merge`, `total merge` | `complete_root_<TAG>_<TUNE>`, `central_reference_path` |
| **merge leg** | one unit of merge work: three centrals plus thirty blocks make thirty-three | — | prose only; disambiguates the PYTHIA string sense of "leg" |
| **multiplicity class** | one of the eleven ranges of primary charged multiplicity that every per-activity number is conditioned on | `multiplicity bin`, `centrality class`, `activity class`, `multiplicity percentile` | `"class": "c1"`…`"c11"`, `boundary_nch` |
| **class boundary** | the half-integer N_ch value that separates two adjacent classes | — | `boundary_nch`, `nch_min_inclusive`, `nch_max_inclusive` |
| **trigger** | the heavy-flavour hadron a pair is counted from | — | `trigger_pdg` |
| **associate** | the second hadron of a registered pair, the one whose flavour is compared with the trigger's | — | `associate_pdg` |
| **balancing partner** | the physics concept: the hadron carrying the compensating heavy quark. Not the registry role | — | prose; the study's own question |
| **pair** | one registered trigger-and-associate combination | — | `heavy_flavour_pair_registry_v1.json` |
| **pair file** | one ROOT file holding the objects for one registered pair | `pair root`, `pair output` | `pair_file_object_contract_v1.json` |
| **pair directory** | the three hundred pair files a single analysed input produces | `pair set`, `pair folder` | `validate_pair_directory.sh` |
| **canonical slot** | the position of one analysed input in a campaign's ordered file set | `logical file`, `slot index` | `canonical_slot` |
| **job** | one submitted unit of generation or analysis work on the cluster | — | `runCondorJob.sh`, `job<NNN>` |
| **campaign** | one named, seeded production of events under one configuration | `production run` | `"campaign"`, `HF_RUN3_V1` |
| **production** | the act of generating events, not a countable thing | — | prose |
| **dataset** | a named, selectable set of merged inputs the plotting chain resolves | `data set` | `"datasets"`, `active_dataset`, `dataset_selector.json` |
| **tune** | one of the three PYTHIA parameter sets under comparison: MONASH, JUNCTIONS, CLOSEPACKING | `bundle` | `"tune"`, `PUBLISHED_TUNES` |
| **arm** | one of the three tunes considered as a leg of the comparison design | — | prose; **not** the A2 tie-break sense, which is a `variation` |
| **tune card** | the `.cmnd` file holding one tune's PYTHIA settings | `parameter file` | `pythiasettings_Hard_Low_ccbb_<TUNE>.cmnd` |
| **configuration** | a plotting or measurement input file naming objects, classes and display settings | `config` | `configuration_path`, `configuration_sha256` |
| **variation** | one systematic campaign: the nominal card with exactly one setting changed | — | `systematics_variations_v1.json`, `systematic_variation_settings_v1.json` |
| **variant** | a display-filtered view of one observable — `V-FULL`, `V-EXTREMES`, `V-INTEGRATED`, `V-BARYONMESON`. **Not a systematic variation** | — | `make_variant_configs.py`, `assert_variant_identity.py` |
| **nominal** | the unvaried campaign a variation is measured against | `reference sample` | `dataset_selector` rows, `integrated_rows_nominal.log` |
| **source** | one named contributor to the combined systematic uncertainty | — | `docs/SYSTEMATICS_PREREGISTRATION.md` S-numbering |
| **delta** | the signed difference a variation moves a quantity by | — | `per_class_deltas_seven.json`, `harvest_deltas.py` |
| **sector** | charm or beauty | `flavour sector` | `"sector": "charm"`, `"sector": "beauty"` |
| **species** | one signed hadron state on the 202-entry axis | — | `hFlavourClosureSpecies`, `species_ordinals_v2.json` |
| **ordinal** | a species' index on that axis | `bin number`, `species id` | `species_ordinals_v2.json`, `GeneratedSpeciesOrdinals.h` |
| **ground state** | the lowest-mass state of a valence-flavour combination, which excited states map onto | `stable state` | `ground_state_rule` |
| **raw file** | one ROOT file the producer writes, before any reduction | — | `hf_primary_ground_raw_v7`, `raw_base` |
| **reduction** | the one-pass stage that turns a raw file into three hundred pair files | `analysis pass` | `run_status_analysis.sh` |
| **merged product** | the directory a merge writes, central or block | `merge product`, `merged directory`, `merge output` | `complete_root_tag` |
| **extraction** | the stage that projects a merged product into per-species and per-category tables | — | `extract_species_decomposition.py` |
| **decomposition** | the table extraction produces, not the act | — | `per_species.csv`, `decompose_with_block_sems.py` |
| **closure** | the check that a central and its blocks account for the same objects and counts | — | `validate_pair_block_closure.sh`, `CANONICAL_PAIR_BLOCK_CLOSURE_PASS` |
| **gate** | a check that refuses to let the next stage start | — | `GATE_3000`, `validate_analysis_outputs.py` |
| **guard** | a check that refuses an action rather than a stage | — | `checkout_advance_guard.py`, hang guard |
| **receipt** | the file a stage writes to record that it ran and what it saw | `attestation`, `certificate` | `receipt.json`, `multiplicity_boundary_receipt_v1.json` |
| **verdict** | the single line a gate emits stating PASS or FAIL | — | `verdict_line_<TUNE>.txt`, `verdict.json` |
| **digest** | the sha256 of a file's bytes | `checksum`, `hash`, `fingerprint` | `*_sha256` fields throughout `config/` |
| **pin** | a digest recorded in one artifact to fix the content of another | — | `plotter_source_sha256`, `FROZEN_BOUNDARY_SHA` |
| **anchor** | a run output copied into the repository so a published number's provenance is readable from the tree alone | `frozen artifact`, `committed artifact` | `anchors/`, `anchors/MANIFEST.md` |
| **golden output** | an artifact whose digest and regeneration recipe are contracted | — | `docs/GOLDEN_OUTPUTS.md` G-numbering |
| **pre-registration** | a method statement committed before the run it governs | `preregistration` | `*_PREREGISTRATION.md` |
| **run record** | the account of what one run did, written after it | — | `*_RUN_RECORD.md` |
| **seed** | the deterministic PYTHIA random seed for one attempt | — | `seed_for(campaign_ordinal, tune, job, attempt)` |
| **attempt** | one try at a job, which may be killed and re-run under a fresh seed | — | `attempt_metadata/`, `attempt<N>` |
| **opposite-sign** | a pair whose two heavy quarks carry opposite flavour charge | — | `"os"` |
| **same-sign** | a pair whose two heavy quarks carry the same flavour charge | — | `"ss"` |
| **balancing yield** | the opposite-sign minus same-sign yield per trigger | `net yield` | `central_yield`, `yield_sem` |
| **flavour** | the quark quantum number, and every compound of it | `flavor` | `HeavyFlavourUtils.h`, `hFlavourClosureSpecies` |
| **colour** | the QCD charge, and `colour reconnection` | `color` | PYTHIA's `ColourReconnection:` settings |
| **hadronization** | the process by which quarks become hadrons | `hadronisation` | `HADRONIZATION_BASE` and every `HADRONIZATION_*` variable |
| **analyzed** | processed by the reduction stage | `analysed` | `AnalyzedData`, `analyzed_data_base` |
| **normalization** | the rule by which a distribution is scaled | `normalisation` | `policy/normalization` |
| **runtime** | the installed ROOT and PYTHIA a command runs against | `run-time` | `HF_ALLOW_UNPINNED_ENV`, `env-verdict` |
| **behaviour** | how a component acts | `behavior` | prose; matches `flavour` and `colour` |

---

## WHERE THE CODE AND THE PROSE DISAGREE

**Three disagreements are recorded rather than resolved, because resolving them
would mean renaming an identifier.**

**1. The ten-way partition has two identifier-fixed names.** The extraction and
merge stages call it a `block`; the plotting chain calls it a `subsample`. Both names
are in field names and filenames, on opposite sides of the same chain. **Prose
says "block" for the statistical object and "subsample directory" for the
plotting input**, and a document that needs both says so once.

**2. The spelling is not one dialect, and it cannot be made one.** `flavour` and
`colour` are British because `HeavyFlavourUtils.h` and PYTHIA's
`ColourReconnection` fixed them. `hadronization`, `analyzed` and `normalization`
are American because `HADRONIZATION_BASE`, `AnalyzedData` and the receipt's
`policy/normalization` fixed them. **Each word follows its own identifier.**

**3. "arm" carries two senses and only one is canonical here.** In the
comparison design an arm is one of the three tunes. The A2 tie-break study also
says "arm" for its two directions; **those are variations**, and prose should
call them that.

---

## FOUR WORDS THAT LOOK LIKE DRIFT AND ARE NOT

**Each of these reached the ruled-out column, and a measurement pulled it back
out.** This list exists so the next session does not rule them out again.

- **`partner`** reads like a loose synonym for `associate`. Every occurrence in
  the tree is the physics concept instead — *antiquark partner*,
  *flavour-balancing partner*, *opposite-sign partner*. Ruling it out would flag
  the study's own question.
- **`variant`** reads like a loose synonym for `variation`. It is a separate
  object with its own identifiers, and it has its own row above.
- **`arm`** and **`leg`** read like synonyms for each other. An arm is one of the
  three tunes. A leg is one of the thirty-three units of merge work. And `leg`
  carries a third sense inside PYTHIA's string fragmentation.
- **`consistency check`** reads like a synonym for `closure`. It is ordinary
  English, used in the tree for several unrelated checks.
