# Paul's plotting stack on v3 — the enumerated delta

**Read-only enumeration, 2026-08-13. Committed before any code was edited**, per
the owner ruling: this list is the justification for every subsequent diff line,
and anything not on it is not a licensed change.

**Principle in force:** Paul's stack is the base and stays the base. Every diff
line must be (a) v3 schema compatibility, (b) a dataset/selector change the new
campaign requires, or (c) removal of something demonstrably outdated. **A large
diff is a failure even if every line is individually defensible.**

---

## 0. E5 EXPOSURE — the stack is NOT exposed. Verified, not assumed.

**The answer is no, and it holds for a better reason than "it reads
`hCorrelations`".**

The analysis macro's per-pair-file write loop
(`analysis/status_analysis_THnSparse_qq.C:1179-1191`) writes **three classes of
object** into every one of the 300 pair files:

| object | ownership | replication |
|---|---|---|
| `summed MULTIPLICITY` | **event-level** | identical in all **300** files |
| `hTrKinematics`, `hFlavourClosure`, `hFlavourClosureSpecies`, `hFlavourClosureSummary` | **trigger**-owned | **24× charm / 26× beauty** |
| `hCorrelations`, `hAsKinematics`, `hCorrelationsByOrigin` | genuinely per-pair | none |

The stack handles all three correctly:

1. **The observable is per-pair.** OS−SS comes from `hCorrelations`
   (`improvedPlotting_THnSparse.C:3164-3167`, subtraction at `:2910`
   `hCorr->Add(hDPhiSS, -1.)`). Not replicated.
2. **`hTrKinematics` is read one file at a time** (`:3168-3171`, from that pair's
   own OS/SS files) and used for that pair's projection. **Never summed** — no
   `Add`, `hadd` or `TFileMerger` touches it anywhere in `plotting/`.
3. **`summed MULTIPLICITY` is treated as an IDENTITY INVARIANT, not as data.**
   `:1786-1800` captures one file as `central_reference` and verifies every other
   file matches, emitting `MULTIPLICITY_IDENTITY … status=PASS`. **This is
   exactly the right handling for a replicated object** and it is the reason the
   stack cannot fall into E5 by accident.
4. **`Plot_FlavourClosure.C` reads a SINGLE pair file** (`:63` takes one
   `pairFilePath`, `:74-75`) and forms its ratio within that file, refusing to
   draw if the sum rule deviates from 1 by more than 1e-6 (`:86-91`). A
   trigger's own closure in its own file is correct; the defect only appears on
   summation.

> **⚠ WORTH RECORDING SEPARATELY: E5's entry names only the closure histograms,
> but `hTrKinematics` and `summed MULTIPLICITY` are replicated by the same write
> loop.** The extractor bug happened to be about the closure. Anyone who writes
> new tooling that sums `hTrKinematics` across pair files, or divides by a summed
> `MULTIPLICITY`, reproduces the identical defect — and E5 as written would not
> warn them. Annotated into `ERROR_RECORD.md` E5.

---

## 1. THE BLOCKERS, with file and line

### B1 — the contract's schema string. **One value.**

| | |
|---|---|
| config | `plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json`, `pair_input_selection_contract.v2_analysis_schema = paul_pair_objects_primary_ground_v2` |
| merged v3 declares | `paul_pair_objects_primary_ground_v3` |
| enforced at | `improvedPlotting_THnSparse.C:914-915`, exact-match `RequireSelectionMetadataString(file, "analysis_schema", …)` |

**Measured against the merged product** (`complete_root_HF_RUN3_V1_MONASH/DplusDplus.root`),
**this is the only contract value that differs**:

| contract field | file key | v2 contract | merged v3 | differs? |
|---|---|---|---|---|
| analysisSchema | `analysis_schema` | …_v2 | **…_v3** | **YES** |
| analysisImplementation | `analysis_implementation` | one_pass_primary_ground_pair_analysis_v2 | same | no |
| analysisVersion | `analysis_version` | status_analysis_THnSparse_qq_v2 | same | no |
| analysisProfile | `analysis_profile` | central_primary_ground_v1 | same | no |
| selectorVersion | `selector_version` | hard_trigger_primary_ground__primary_ground_associate_v1 | same | no |
| pairCombinatoricsMode | `pair_combinatorics_mode` | ordered_conditional_v1 | same | no |

### B2 — the contract MODE forbids v3

`improvedPlotting_THnSparse.C:908-912` throws when
`!PairSelectionContractAllowsV2(contract)`; the configured mode is
`v2_metadata_or_tagged_legacy_recuts_v1`, and `:1625` throws on any mode string
the code does not know. **The admissible mode set is code-side**, so a v3 mode
cannot be introduced by configuration alone.

### B3 — contract keys are `v2_`-prefixed AND exact-checked

`PairInputSelectionUtils.h:100-140` and `improvedPlotting_THnSparse.C:1590-1620`
read `v2_analysis_schema`, `v2_selector_version`, `v2_trigger_pt_min_exclusive`
… and `RequireExactKeys` **rejects any key not in the expected set**.

**Consequence for the minimal-diff principle:** a v3 configuration cannot simply
add `v3_*` keys beside the v2 ones. Either the v3 values go into the existing
`v2_*`-named keys — zero code change, misleading names — or the code learns a
`v3_` prefix. **This is a genuine design choice and is flagged for the owner
rather than decided here.**

### B4 — no HF_RUN3_V1 dataset entry exists

`config/dataset_selector.json` carries only `legacy_21_06_2026` (active),
`hf_pt2_candidate`, `hf_pt2_int_candidate`. **There is no HF_RUN3_V1 entry at
all.**

`plotting/run_paper_plots.sh:223-232` refuses publication targets unless status
is `canonical` or `canonical_candidate`; `:239-243` requires
`canonical_candidate` to be **publication-ineligible**. So the additive path is a
new `hf_run3_v1_candidate` entry with `status=canonical_candidate`,
`publication_eligible=false`.

### B5 — data paths point at the legacy product

Config: `base_dir=AnalyzedData`, `complete_root_21_06_2026`,
`AnalyzedData/SUBSAMPLES_700/combined_root_subSamples`.
v3 product: `/data/alice/ipardoza/hadronization_merged/complete_root_HF_RUN3_V1_<TUNE>`
and `…/SUBSAMPLES_HF_RUN3_V1/combined_root_subSamples_<TUNE>`.

### B6 — ⚠ THE MULTIPLICITY AXIS. The only blocker that is not configuration.

`improvedPlotting_THnSparse.C:1770,1811` builds
`thresholdsByTune[tune][percentile]` — **per-tune percentile thresholds, derived
from each tune's own MULTIPLICITY histogram**, with a per-tune partition check at
`:2003-2008`.

**That is the per-tune percentile scheme the axis ruling REJECTED.**
`docs/PRODUCTION_SHAPE_DECISION.md` adopted **common absolute N_ch boundaries,
one set shared by all three tunes, with labels defined as percentiles of the
MONASH MB distribution and the per-tune residual published** (max 2.91 pp) —
precisely because per-tune classes fold each tune's activity distribution into
the class definition, confounding *how a tune hadronises at fixed activity* with
*how it distributes activity*.

**This cannot be fixed by adding a configuration file.** It changes how the
stack derives its classes, which is a behavioural change to Paul's code and
therefore needs an owner decision about scope before it is written.

---

## 2. NOT BLOCKERS — checked and cleared

| candidate | finding |
|---|---|
| **the 7-vs-5 object set** | **already solved.** `config/pair_file_object_contract_v1.json` declares `schema_version_tags {v2, v3}`, keys the object set on the file's own `analysis_schema`, and **fails closed** on an unlisted tag. `hFlavourClosureSpecies` is documented there as v3-only. **No strict object enumeration was found in `plotting/`** |
| E5 replication | §0 — not exposed |
| `summed MULTIPLICITY` identity | already verified as an invariant by the stack itself |

---

## 2b. ⚠ THE v2 DATASET NO LONGER EXISTS — this changes both rulings

**Measured 2026-08-13, after the rulings were given.**

| path the v2 config points at | local | Nikhef |
|---|---|---|
| `AnalyzedData/complete_root_21_06_2026` | **ABSENT** | **ABSENT** |
| `AnalyzedData/SUBSAMPLES_700/combined_root_subSamples` | **ABSENT** | **ABSENT** |

Two stated premises do not hold:

- **B3's acceptance test is unrunnable as written.** "Run the v2 config before
  and after the loader change and get identical output" needs the v2 data, and
  there is none. **The data-free equivalent** — and what
  `tests/test_pair_selection_contract_parity.py` already does — is to assert at
  **source and config level** that a v2 config resolves to the identical key set
  and contract values before and after. That is a real regression test and needs
  neither ROOT nor data, but it is a *different* test from the one specified and
  should be accepted explicitly rather than substituted silently.
- **B6's rationale is weakened.** Option 1 (add a mode alongside) was chosen to
  keep the per-tune path intact so **the old figures remain regenerable**. They
  are not regenerable — their inputs are gone. The per-tune path's remaining
  value is as a readable record of what was done, which a config file and this
  document already provide.

> **This is put back to the owner rather than decided here.** If the reason for
> the larger diff was regenerability, and regenerability is already lost, then
> Option 2 (replace the derivation) is both the smaller diff and the better match
> for "a large diff is a failure even if every line is defensible."
> **No code was written against the weakened premise.**

## 3. THE SHAPE OF THE MINIMAL CHANGE

Additive wherever possible, so the v2 configuration survives as the provenance
record of the old figures:

1. **new** dataset-selector entry `hf_run3_v1_candidate` (B4) — pure addition.
2. **new** v3 plotting configuration file pointing at the merged v3 product
   (B1, B5) — pure addition.
3. **code**, unavoidable: a v3-admitting contract mode (B2), and whichever
   resolution the owner picks for the `v2_`-prefixed keys (B3).
4. **code, scoped by owner decision**: the multiplicity axis (B6).

**Tunes are added by configuration, not code** — the tune loop already keys
everything by tune name.

**Items 1–3 are small and mechanical. Item 4 is the real work**, and it is the
one that determines whether this stays a small diff.

---

## 4. IMPLEMENTATION STATUS — 2026-08-13

**Landed and verified (suite 41/41, macro compiles under ACLiC):**

| item | state |
|---|---|
| **B2** mode | `v3_metadata_only_v1` added to both metadata-admitting predicates. The predicate NAME (`AllowsV2`) was left alone deliberately — it means "metadata-bearing, not metadata-free legacy", it is internal, and renaming ripples through both implementations and the parity test for no behavioural gain. The lying-name concern that drove B3 is about **config** keys, which get copied and adapted; this does not |
| **B3** prefix | Both parsers resolve the prefix from the config's own content — never defaulted. Both families present, or neither, is fatal. A prefix disagreeing with the schema it carries is fatal, **judged through `ParsePairSchemaVersion`** rather than a retyped literal, because `test_pair_object_contract.py` forbids pinning a schema string in consumer code — **it caught the first attempt, which did retype both literals** |
| **the axis definition** | `config/multiplicity_class_boundaries_v1.json` is now the ONE definition. `plotting/paper/make_paper_figures.py` reads it instead of its former literal, and **figure 3 regenerates byte-identically** (`9bf61215…96a8e109`), which proves the artifact carries exactly what the literal did |
| tests | `tests/test_pair_contract_schema_prefix.py`, 22 checks, both directions. Its docstring states exactly what it establishes and **what it cannot** — that a full plotting run is unchanged, which is unprovable now |

## 5. B6 AND THE MECHANICAL ITEMS — LANDED 2026-08-13, commit `47d6396`

**All five remaining blockers are closed and the stack runs on v3 data.**

**B6 — the derivation replaced, keyed exactly as before.** The owner ruling was
to keep the shape and change only the source, and that is what the diff does:
`thresholdsByTune[tune][percentile]` is still keyed by the configured percentile
labels, so `MULTIPLICITY_BOUNDARY` emission, the `integerThresholds`
construction, `RequireDiscretePartitionCoverage` and the class records needed
**no edits at all**. The population site is one call instead of a loop over
`ThresholdForPercentile`.

The mapping, in `plotting/CommonMultiplicityBoundaries.h` — a new header because
**two** consumers resolve the artifact and a duplicated mapping would be the
second definition the artifact forbids:

| percentile key | resolved inclusive N_ch | source |
|---|---|---|
| `100.0` | first class's lower edge + 0.5 | artifact |
| ordered class *i*'s low edge | class *i+1*'s lower edge − 0.5 | artifact |
| `0.0` | last regular bin of the axis | **binning**, not the tune |

`thresholds[0.0]` is the one value not in the artifact, because the ruled top
class is **open-ended**. Taking it from the axis rather than from
`ThresholdForPercentile(identity, 0.0)` is what keeps the resolved set identical
across tunes: the latter is the last *populated* bin and is tune-dependent.

**The three conditions, each demonstrated rather than asserted in prose:**

| condition | how it was shown |
|---|---|
| fail closed on class-count mismatch | a 10-class configuration against the 11-class artifact exits 1 with *"Configured multiplicity class count (10) does not match the 11 classes defined in … ; refusing to truncate or pad the axis"* |
| boundaries identical across tunes | a **two-tune** run (MONASH + JUNCTIONS central) emits `MULTIPLICITY_COMMON_BOUNDARIES … tunes_compared=2 identical_across_tunes=PASS`, and all 12 `MULTIPLICITY_BOUNDARY` lines agree tune-for-tune. A one-tune run satisfies the assertion vacuously, which is why the two-tune run was done |
| label provenance in the receipt | `policy.percentile_label_provenance` states the labels are MONASH-MB percentiles and **not** the labelled tune's own, and `boundary_source` carries the artifact path, its SHA-256, the class names and lower edges, and the `33c9a8c` sha |

**Two consequences that were not optional.** The receipt's `algorithm` field
named `ascending_discrete_weighted_quantile_v1`, which is no longer what
happens; it is now `common_absolute_nch_class_boundaries_v1`, which cost two
lines in `tools/statistical_robustness.py` and its fixture. And
`Plot_MultiplicityDistribution_PercentileBoundaries.C` cross-checked the frozen
receipt by **recomputing per-tune quantiles**, which would now disagree by
construction; it resolves the artifact instead. Both are the same defect class:
a stale statement about how a number was made.

**B1 / B4 / B5.** New v3 plotting configuration; `hf_run3_v1_candidate` rows in
`config/dataset_selector.json` and a matching single-dataset selector.
**`run_paper_plots.sh` needed no edit** — its `canonical_candidate` branch
already forces `publication_eligible=false`, and the plotting configuration is
chosen by `THNSPARSE_COMPLETE_ROOT_CONFIG`. Measured against the merged product,
`analysis_schema` was the only contract value that differed, exactly as §1
predicted.

> **The per-tune derivation remains readable at `33c9a8c30fa97c9281e26ecbd6d1becc1afb9c21`.**
> Recorded here per the ruling, in advance of the removal, so the sha is fixed
> before the branch disappears. Git history is sufficient preservation for code;
> it was not for the data, which is why the original rationale collapsed.

### What the v3 configuration is NOT

The v2 file it descends from is a **reduced** diagnostic: every one of its 16
canvases lists ten of the eleven classes in `bins_to_ignore`, so each draws a
single activity class. The v3 configuration drops nothing, because the figure
being asked for **is** the multiplicity dependence. The first run reproduced the
v2 behaviour faithfully and drew one class; that was a fault in the inherited
canvas, found by looking at the rendered output.
