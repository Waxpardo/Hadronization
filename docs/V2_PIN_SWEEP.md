# The v2-pin sweep — every site that treats the analysis schema as a constant

**Why this exists.** `analysis/status_analysis_THnSparse_qq.C:57` now
writes `paul_pair_objects_primary_ground_v3`. The pair-object contract is
version-aware and accepts both. **Every other place that compared the schema
against a single pinned string would have rejected a correct v3 directory at
its own layer, after the object contract had already accepted it** — the
one-consumer blindness that `RELEASE_BLOCKERS`' defect pattern 2 names.

Handoff v23 listed seven sites from grepping **one** string and warned the list
was a floor. **It was: the expansion found three more.**

---

## The grep patterns, recorded

A "nothing further found" result means nothing without the patterns that
produced it. All run over `plotting/ tools/ Validation/ AnalysisScripts/
config/ tests/`, with `--include='*.C' --include='*.h' --include='*.py'
--include='*.json' --include='*.sh'`:

| # | pattern | rationale |
|---|---|---|
| P1 | `paul_pair_objects_primary_ground_v[23]` | the literal itself, both versions |
| P2 | `paul_pair_objects` minus P1's hits | any other suffix in use — **zero hits**, so v2/v3 are the only ones |
| P3 | `kRequired[A-Za-z]*` | named constants that pin a contract value |
| P4 | `"[A-Za-z_]*_v2"`, `v2_analysis`, `_v2\b` | bare version literals and version-named keys |

**P2 returning zero is a real result:** there is no v1, v4 or unversioned
spelling of the schema anywhere in the tree.

---

## Classified table

### Needs version-awareness — **FIXED this session**

| site | what it did | fix |
|---|---|---|
| `plotting/PairInputSelectionUtils.h:161` | `supportedV2` conjunction pinned `analysisSchema == "…_v2"`; the whole plotting layer enters through here | accepts any schema the contract declares, via `ParsePairSchemaVersion`, **fail-closed** on unknown |
| `plotting/improvedPlotting_THnSparse.C:1622` | the same conjunction, independently written | same |
| `tools/validate_analysis_outputs.py:31` | `ANALYSIS_SCHEMA` single constant, compared in `expected_metadata` | now `ANALYSIS_SCHEMAS`, **derived from the contract's `schema_version_tags`** so it cannot drift; the directory is judged against the schema it declares, unknown fails closed |

Already fixed in `73dbec7`, recorded here for completeness:

| site | fix |
|---|---|
| `Validation/ValidatePairDirectory.C:34` | `kRequiredAnalysisSchema` **deleted**; admissible schemas are the contract's list |

### Correctly pinned — **no change, with the reason**

| site | why it is correct |
|---|---|
| `analysis/status_analysis_THnSparse_qq.C:57` | **the producer.** It writes exactly one schema; that is its job. It is the thing the axis is *about* |
| `AnalysisScripts/GeneratedPairObjectContract.h:46,50` | generated; these two literals **are** the version table, emitted from `config/pair_file_object_contract_v1.json` |
| `config/pair_file_object_contract_v1.json:18-19` | the source of truth for the tag ↔ version mapping |
| `plotting/PairInputSelectionUtils.h:33` `kRequiredV2MetadataObjectCount = 12` | **NOT v3-sensitive**, and this was worth checking. The 12 are `analysis_{schema,implementation,version,profile}`, `associate_origin_category_{schema,labels}`, `selector_version`, `pair_combinatorics_mode`, and four selection scalars. **A v3 file carries all 12** — v3 *adds* objects and removes none — so the count stays 12. It is a presence probe distinguishing metadata-carrying files from legacy metadata-free ones, not a contract size |
| `…_v2` strings that are **other** schemas | `hf_canonical_freeze_seal_v2`, `hf_canonical_raw_manifest_v2`, `hf_merged_pair_directory_provenance_v2`, `canonical_300_pair_metadata_v2`, `upstream_selected_v2` — unrelated to `analysis_schema`; their versions did not move |
| `analysis_implementation` / `analysis_version` pins everywhere | **the producer did not move them.** `one_pass_primary_ground_pair_analysis_v2` and `status_analysis_THnSparse_qq_v2` are unchanged by the species axis. Sweeping them along with the schema would have been wrong |
| `v2_analysis_*` **config key names** | naming convention for the metadata-v2-era block. They are keys, not schema values; the value they carry is what matters |

### Config values — correct for v2 data, switch when v3 data is plotted

| site | note |
|---|---|
| `plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json:13` | `v2_analysis_schema` value declares which schema the run expects. **No code change needed:** the gates now accept either, and the file-vs-config check (`PairInputSelectionUtils.h:285`) still enforces agreement. Set to v3 when plotting v3 data |
| `…_complete_root.json:13` | same |

### **CLOSED — and the authorization turned out to be unnecessary**

| site | resolution |
|---|---|
| `tools/statistical_robustness.py` `exact_strings` | **FIXED.** `analysis_schema` is removed from the exact-match dict and checked for **membership** in the contract's declared tags, fail-closed. The accepted set is **derived** from `config/pair_file_object_contract_v1.json`, so it cannot drift |
| `config/statistical_robustness_v1.json:16` | **NOT EDITED, and no edit is needed.** Once the tool stopped exact-matching on it, that key is no longer consulted when judging a data file; it survives only as the value `tests/test_statistical_robustness.py:708` uses to *construct* a v2 fixture, which is correct. **The authorization went unused** |
| `tools/statistical_robustness.py:177` | **correctly pinned, no change.** This literal lives in `validate_spec`'s `expected_contracts` and asserts what the **spec file** declares, not what a data file carries. It is not a v3 gate |

**Pre-condition verified before touching anything** (the authorization's own
requirement): the config's sha256
`9a86d7f865f84969582e5618447510b3848290e07316a0a57e78147d6f415a71` is pinned in
**none** of 6720 provenance-bearing files under the production root, and the
string `statistical_robustness` appears in **no** promoted provenance at all.

### Test fixtures — v2 by construction; owe a v3 case

| site | note |
|---|---|
| `Validation/TestPlotProjectionCuts.C:20,38,239` | builds v2 fixture files. **Correct as v2** — but there is no v3 fixture case, so the plotting gate's v3 path is unit-tested only through the parity test below |
| `tests/test_pair_selection_contract_parity.py` | **UPDATED.** It pinned the v2 literal in *both* parsers. It now asserts the parity property one level up: both parsers must reach the schema through `ParsePairSchemaVersion` **and** must not re-pin the literal |

### Dead

None found. Every hit is live.

---

## Negative tests

`tests/test_pair_object_contract.py::test_no_consumer_pins_a_single_analysis_schema_literal`
now covers **six** judging consumers, up from three:
`ValidatePairDirectory.C`, `ValidatePairBlockClosure.C`,
`Validate_THnSparse_Production.C`, **`PairInputSelectionUtils.h`**,
**`improvedPlotting_THnSparse.C`**, **`validate_analysis_outputs.py`**.
A judge that re-pins the literal in code fails there.

`test_pair_selection_contract_parity.py` additionally forbids either parser
regressing, which is the drift that file exists to catch.

---

## What this sweep does NOT establish

- **No v3 data has been through the plotting layer.** The gates now *accept*
  v3; nothing has *exercised* them with a v3 file. That waits for a v3 analysis
  campaign.
- **The two 12-name metadata lists are duplicated**, in
  `PairInputSelectionUtils.h:278-292` and
  `improvedPlotting_THnSparse.C:838-851`. Not v3-gating, so out of scope here,
  but it is the same shape of duplication that produced the original
  three-divergent-copies problem. Worth folding into the contract eventually.
- **`statistical_robustness` is unswept** pending the config authorization
  above, so a v3 directory would still fail there.
