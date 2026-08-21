# Species-axis validation evidence — all three tunes

The species axis (`hFlavourClosureSpecies`, 202 ordinals) replaces the 6-bin
`heavyStateCategory` axis with one that names the compensating hadron. This
file is the evidence record: what was run, on what, and what came back.

**The ordinal table under test:** 202 species, digest **`646f310f78126267`**,
derived by `tools/GenerateSpeciesOrdinals.C` from **one JUNCTIONS**
`heavy_stability_audit` tree (`HF_PT2_INT` job001). Whether a table derived
from one tune is complete for the others is the question §2 answers.

---

## 1. The two checks

| # | check | tolerance |
|---|---|---|
| 1 | flavour-closure sum rule closes to 1 | **1e-9**, enforced by the producer itself, which throws |
| 2 | species axis summed by category reproduces the category axis **bin for bin** | 1e-12 relative |
| 2b | the same, after integrating the fine axes away, so the sum is genuinely **many-to-one** | 1e-11 relative |

**Why check 2 is not tautological.** The two labelings share their *rules* —
`ClassifyHeavyStateDetailed` — but not their *inputs*. `hFlavourClosure`'s
category is the producer's runtime `heavy_state_category`, computed per particle
as the event was analysed. The species axis's category comes from the ordinal
table, derived offline from `heavy_stability_audit`. Agreement tests the ordinal
mapping and the fill.

**Why 2b exists.** At fixture statistics the correlation space is
100 x 100 x nPt x 4096, so a filled 5D cell almost always holds a **single**
species: `category_bins == species_bins` in every run below. Check 2 alone would
therefore be comparing one-term "sums" — a copy, not an aggregation. Integrating
the fine axes away forces thousands of ordinals into six totals, which is the
aggregation the axis actually performs downstream.

---

## 2. Results

Each run: one raw job, 100,000 events, 300 pair files. **900 files total.**

| tune | raw fixture | bytes | sha256 |
|---|---|---|---|
| JUNCTIONS | `HF_PT2_INT/raw/JUNCTIONS/hf_JUNCTIONS_job001.root` | 96,578,417 | `49657c2c9a25e319513be5cda659a4d5e53bb3944f33bef51702b5660aaa3651` |
| MONASH | `HF_RUN3_V1/raw/MONASH/hf_MONASH_job000.root` | 92,200,782 | `6f88248017cb6b8c4a333c541787d66401379fe8e2350e529f6db01da361f30d` |
| CLOSEPACKING | `HF_RUN3_V1/raw/CLOSEPACKING/hf_CLOSEPACKING_job000.root` | 95,664,577 | `eafd1c40da675d6df8e0c05073880918b6ede155213b45ff2776b1124bc9cfce` |

The CLOSEPACKING hash equals the `partial_sha256` in that job's
`attempt_metadata` sidecar — an unplanned provenance cross-check that the
promoted raw file is byte-identical to what the producer recorded.

| tune | files | total_errors | **unmapped** | worst content | worst Sumw2 | worst marginal | max aggregation | closure sum rule |
|---|---|---|---|---|---|---|---|---|
| JUNCTIONS | 300 | **0** | **0** | 0.000e+00 | 0.000e+00 | 0.000e+00 | 7013 | 1.000000000000000 |
| MONASH | 300 | **0** | **0** | 0.000e+00 | 0.000e+00 | 0.000e+00 | **7397** | 1.000000000000000 |
| CLOSEPACKING | 300 | **0** | **0** | 0.000e+00 | 0.000e+00 | 0.000e+00 | 6469 | 1.000000000000000 |

**All three pre-registrations held for every tune**, and the aggregation depth
(6469–7397 ordinals summed into one category total) shows check 2b exercised the
many-to-one path it exists for.

---

## 3. Tune-independence: MEASURED, no longer reasoned

Handoff v24's cold-read flagged that the axis had only ever run on JUNCTIONS,
and that tune-independence was **reasoned from `open_heavy == 1` being a
property of PYTHIA's particle data, not measured**. It is now measured.

> **The 202-species table derived from a single JUNCTIONS job maps every
> sector-charged hadron produced by MONASH and CLOSEPACKING as well. Zero
> unmapped species across 900 files and 300,000 events, spanning all three
> tunes.**

The mapping is **fail-closed** — an absent PDG aborts the run with a named
error, no overflow bin — so "zero unmapped" is a real observation and not a
silent default. A firing would have been a genuine discovery: it would mean the
admissible species set depends on the colour-reconnection model, which the
derivation assumes it does not.

**What this does NOT establish.** These are single jobs, ~100k events each. A
species produced at a rate below roughly 1 per 100k events in a given tune could
still be absent from all three samples and appear at full campaign scale. The
fail-closed abort is the protection: at scale it fails loudly rather than
mis-binning. **It is a guard, not a proof of completeness.**

---

## 4. Reproducing

Scratch-deploy pattern, frozen checkout untouched:

```
/data/alice/ipardoza/species_axis_fixture/
  AnalysisScripts/{status_analysis_THnSparse_qq.C,GeneratedSpeciesOrdinals.h,
                   GeneratedPairObjectContract.h,GeneratedPairRegistry.h,
                   AssociateOriginCategoryContract.h}
  SimulationScripts/{HeavyFlavourUtils.h,GeneratedHeavyFlavourRegistry.h,
                     GeneratedTuneSettingRegistry.h}
  Validation/ValidateSpeciesAxisClosure.C
```

Environment (the analysis contract's four variables, read from the macro's own
`RequiredEnvironment` calls at `status_analysis_THnSparse_qq.C:753-759`):

```
HADRONIZATION_ANALYSIS_COMMIT
HADRONIZATION_ANALYSIS_MACRO_SHA256    sha256 of the deployed macro
HADRONIZATION_ANALYSIS_PROFILE         central_primary_ground_v1
HADRONIZATION_RAW_INPUT_SHA256         sha256 of the raw input
```

Then `ValidateSpeciesAxisClosure(<pair file>)` per output file; it returns the
error count and prints one `SPECIES_AXIS_CLOSURE` line each.
