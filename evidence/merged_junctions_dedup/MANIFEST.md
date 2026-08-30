# Anchor `merged_junctions_dedup` — JUNCTIONS, closure PASSED

**Part of the three-tune table of record.** That document went internal on
2026-08-22. `docs/GOLDEN_OUTPUTS.md` §2.9c carries the same closure counts and
digests in the tree. The fuller dated record is preserved in the internal
archive.
Central plus all ten canonical blocks, extracted from the merged pair files with
the **trigger-deduplicating** extractor on 2026-08-15, and promoted to FINAL on
2026-08-16 when this tune's closure returned.

## The closure verdict, verbatim

Finished 2026-08-16 11:58:20 CEST after 13 h 50 m:

```
PAIR_BLOCK_CLOSURE errors=0 analysis_schema=paul_pair_objects_primary_ground_v3 central_pair_files=300 block_pair_files=3000 object_content_sumw2_closure_checks=2100 additive_metadata_closure_checks=3600 invariant_metadata_checks=1500 source_filter_contract_checks=300 expected_central_events=100000000 relative_tolerance=2e-10
```

**2100 / 1500 as pre-registered, schema v3, errors 0** — not the 1800/600
v2-sidecar failure mode. `expected_central_events=100000000` is the **strong**
argument, asserting the central's event count rather than accepting it.

**The A4 expected-schema argument does not exist on the frozen Nikhef tree**, so
the schema was verified by *reading* the emitted `analysis_schema=` value, via
`extraction/pipeline/harvest_tune.py --stage closure`.

## Deduplication, read from the data

Every one of the eleven directories reports:

```
DEDUPLICATION trigger-owned closures counted once each; replication in this
directory: beauty [26]x, charm [24]x
```

and `SELF_CHECK AGREE worst_relative=0.000e+00` — the sum rule at 1e-9, met
exactly, with regrouping invariance CONSERVED.

## The numbers

| | |
|---|---|
| total entries | **46,311,148** |
| per event (100 M events) | **0.4631** — plausible against the MONASH-calibrated ~0.54 |
| kCentralGround | **58.2318 %** |
| kExcludedVector | **39.9409 %** |
| kExcludedExcited | **1.7821 %** |
| kMultiplyHeavy | **0.0452 %** |

## Integrity

| check | result |
|---|---|
| I3, ten blocks sum to central bin by bin | **PASS**, exactly |
| I2, block vs central, robust MAD null | **3 flags** in 10 comparisons — see below |
| extractor self-check, species vs closure | **AGREE**, worst relative 0.000e+00, all 11 |
| regrouping invariance | **CONSERVED** exactly, both conventions |

## The I2 flags — recorded here because an anchor must not look cleaner than it is

Three bins flag at |z| > 4, **all three in `kMultiplyHeavy`**:
Ω*_ccbar⁻ (block 4), Ξ*_cc⁺ and Ω*_cc⁺ (block 7). MONASH contributes **0 of its
88** testable bins to that category; this tune contributes **12 of 116**, so the
flags are in bins MONASH could not test. The subpopulation's dispersion is
**1.60× binomial** against 0.98–1.11 for the other three categories, while I2's
MAD null estimates one pooled σ̂ of 1.12.

**`decompose_with_block_sems.py` therefore exits 4, not 0, on this anchor** —
that is correct and expected, and the regenerate command below says so. Do not
pass `--i2-advisory` to make it quiet. Section 3d of the retired three-tune
table carries the full diagnosis and the open ruling. That fuller record is
preserved in the internal archive.

## Provenance

| | |
|---|---|
| extractor | `extract_species_decomposition.py`, sha256 `4cd8b6fa8493529624b33de81e67764c07c2126465d7ae921e5970919f0ad960` |
| ordinal artifact | `species_ordinals_v2.json`, sha256 `ccec0dbc70f6452d…d0e4ce`, digest `646f310f78126267` |
| pair registry | `heavy_flavour_pair_registry_v1.json`, sha256 `ea9b0232c1be8415…ddee23` |
| decay map | `decay_parent_map_v2.json`, sha256 `58081aa2f87cb671…1c84da` — the DEPLOYED copy at `/data/alice/ipardoza/extractor_e5fix/AnalysisScripts/`, not `contracts/decay_parent_map_v2.json`. No commit in this repository's history has ever held that digest for the tracked file; see `evidence/e5fix_drivers/run_extract.sh:6-9`, which records the same deployed layout |
| **all four** | **identical to `merged_monash_dedup`'s** — the same instrument, not a re-implementation |
| sources | `hadronization_merged/complete_root_HF_RUN3_V1_JUNCTIONS`, `…/combined_root_subSamples_JUNCTIONS/combined_root_{1..10}` |
| merged inputs | `analysis_commit 61fe978f…`, freeze seal `e03fb1e7…`, **1000 input files** |
| ROOT | 6.30/01, ALICE CVMFS build — **on pin** |
| host, when | `stbc-i3.nikhef.nl`, 2026-08-15 22:12–22:32 CEST |
| remote outputs | `/data/alice/ipardoza/tune_runs_three/JUNCTIONS/` |

The extractor was staged at `/data/alice/ipardoza/extractor_e5fix/`, **outside**
the frozen `Hadronization` checkout, which the canonical merge reads live.

## Regenerate

```bash
extraction/decompose_with_block_sems.py \
  evidence/merged_junctions_dedup --tune JUNCTIONS
```

Expect `I3 … PASS` and the values above. **It exits 4, not 0** — the I2 flags
above are real and reported rather than suppressed.

The input path above is the tracked one. Ruling R19 moved the anchors from
`AnalysisScripts/anchors/` to `evidence/`, and the old path this command
carried no longer exists in the tree.
