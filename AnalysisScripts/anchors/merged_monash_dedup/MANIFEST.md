# Anchor `merged_monash_dedup` — MONASH re-extracted with the E5 fix

**The table of record for MONASH.** Central plus all ten canonical blocks,
extracted from the merged pair files with the **trigger-deduplicating**
extractor on 2026-08-13. This supersedes the arithmetic reconstruction that
stood between 2026-08-13 morning and this run.

## What makes it different from `merged_monash_replicated/`

That anchor is the **replicated** extraction: the trigger-owned closure
histograms were summed once per pair file, so each charm trigger entered 24
times and each beauty trigger 26 (private error-ledger entry E5). Its total is
1,298,655,240. This one counts each trigger once and totals **53,662,416**.

**The replication is recorded here as a measurement, not an inference.** The
extractor reads the pairing from the signed registry and reports, in every one
of the eleven directories:

```
DEDUPLICATION trigger-owned closures counted once each; replication in this
directory: beauty [26]x, charm [24]x
```

## The E5 check this run was made to settle

| quantity | predicted by reconstruction | measured here |
|---|---|---|
| total | 53,662,414 … 53,662,828 | **53,662,416** |
| kCentralGround % | 52.4958 | **52.4959** |
| kExcludedVector % | 46.4946 | **46.4946** |
| kExcludedExcited % | 1.0095 | **1.0095** |
| charm : beauty | 89.9852 : 10.0148 | **89.9852 : 10.0148** |

The 414-count bracket is the irreducible ambiguity of the eight mixed
beauty-charm species, which `24C + 26B = T` cannot resolve on its own. The
measurement lands two counts above its floor.

**Per-event plausibility**, the standing check: **0.5366** entries per event
over the campaign's 100 M events, against the replicated **12.9866**. The
published number was ~13 closure entries per event and nobody divided.

## Integrity

| check | result |
|---|---|
| I3, ten blocks sum to central bin by bin | **PASS**, 53,662,416 both sides |
| I2, block vs central, robust MAD null | **PASS**, 0 flags in 10 comparisons |
| extractor self-check, species vs closure | **AGREE**, worst relative 0.000e+00, all 11 |
| regrouping invariance | **CONSERVED** exactly, both conventions |

## Provenance

| | |
|---|---|
| extractor | `extraction/extract_species_decomposition.py`, sha256 `4cd8b6fa8493529624b33de81e67764c07c2126465d7ae921e5970919f0ad960` |
| ordinal artifact | `species_ordinals_v2.json`, sha256 `ccec0dbc70f6452d…d0e4ce`, digest `646f310f78126267` |
| pair registry | `heavy_flavour_pair_registry_v1.json`, sha256 `ea9b0232c1be8415…ddee23` |
| decay map | `decay_parent_map_v2.json`, sha256 `58081aa2f87cb671…1c84da` |
| sources | `hadronization_merged/complete_root_HF_RUN3_V1_MONASH`, `…/combined_root_subSamples_MONASH/combined_root_{1..10}` |
| ROOT | 6.30/01, ALICE CVMFS build — **on pin** |
| host, when | `stbc-i3.nikhef.nl`, 2026-08-13 08:11–08:24 CEST |
| remote outputs | `/data/alice/ipardoza/tune_runs_e5fix/MONASH/` |

The extractor was staged at `/data/alice/ipardoza/extractor_e5fix/`, **outside**
the frozen `Hadronization` checkout, because the canonical merge reads that
checkout live and it must not move until its 33rd promotion.

## Regenerate

```bash
extraction/decompose_with_block_sems.py \
  AnalysisScripts/anchors/merged_monash_dedup --tune MONASH
```

Expect `I3 … PASS`, `I2 … PASS (0 flags in 10 comparisons)`, `status=0`, and the
tables in `docs/MONASH_CENTRAL_TABLE.md` §0.
