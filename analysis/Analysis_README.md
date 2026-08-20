# Analysis scripts

> **Design rationale:** [`../docs/DESIGN_AND_RATIONALE.md`](../docs/DESIGN_AND_RATIONALE.md) explains why each choice was made.

The publication analysis is the one-pass, manifest-driven
`status_analysis_THnSparse_qq.C`. It converts one validated raw-v5 logical
output into all 300 signed ordered-pair files while preserving the ROOT object
names and filenames consumed by Paul Veen's THnSparse plotting architecture.
It deliberately rejects text-file lists of independent raw jobs: the
effective-settings digest contains each job's random seed. Analyze one
manifest row at a time, then combine only through the manifest-bound
`MergeCanonicalAnalysis.C` path.

`hf_mult_pt_analysis_multi.C`, split bbbar/ccbar reductions, and older status
macros are retained as legacy/inclusive regressions. They are not inputs to
new central balancing results.

See [`../REPRODUCIBILITY.md`](../REPRODUCIBILITY.md) for the complete gate and
production sequence.

## Input contract

Canonical input must validate:

```text
raw schema       hf_primary_ground_raw_v7
selector         hard_trigger_primary_ground__primary_ground_associate_v1
origin           signed_heavy_constituent_complete_mothers_unique_v4
stability        heavy_stability_audit_v2
settings         effective_pythia_settings_exhaustive_v2
```

The analysis also binds signed species/pair registries, tune allowlist,
campaign, raw checksum, commit, and one successful-event entry per event.
Legacy schemas require an explicitly labeled regression reader; they cannot
enter the canonical path.

## Central selector and pair convention

Both roles require:

- signed ground-state registry membership;
- direct-primary positive PYTHIA status 81--89;
- generator stability;
- `|eta| <= 4`.

Triggers additionally require resolved selected-hard origin and
`pT > 1 GeV/c`. Associates retain hard, shower, MPI, other, and unresolved
origins and require `pT > 0.15 GeV/c`.

Pairs are ordered and trigger conditioned. Every eligible trigger is paired
with every distinct eligible associate; self-pairs are excluded by event
record index. OS/SS uses signed net charm or beauty, never electric charge.
The canonical same-sign factor is 1.0. The legacy 0.5 convention is not
applied.

The pair macro fills associate-origin components in parallel and validates
that their bin-by-bin sum equals the inclusive object. It also retains the
validation-only all-primary-heavy closure needed to quantify central
ground-state coverage.

In pair-file schema v2, the historical
`primary_all_heavy_closure_failures` `TParameter` specifically counts selected
events for which raw `primary_all_heavy_match_valid != 1`. It is therefore an
invariant-failure counter, not the multi-category closure table emitted by
`Validation/AuditOriginResolution.C`. The name is retained to avoid silently
changing Paul's pair-file contract; publication validation requires the value
to be zero.

## Per-pair ROOT compatibility

Every pair file contains:

```text
summed MULTIPLICITY
hTrKinematics
hAsKinematics
hCorrelations
hCorrelationsByOrigin
associate_origin_category_schema
associate_origin_category_labels
```

Their established meanings are:

- `summed MULTIPLICITY`: all successful input events, independent of whether
  the selected pair occurs;
- `hTrKinematics`: one entry per eligible trigger, independent of whether the
  configured associate occurs;
- `hAsKinematics`: one entry per accepted trigger-associate pair; it is not
  an inclusive single-particle spectrum;
- `hCorrelations`: one entry per accepted ordered pair;
- `hCorrelationsByOrigin`: the same entries with an eighth, versioned
  associate-origin category axis. Categories 1--6 are selected-hard companion,
  selected-hard noncompanion, shower, MPI, other resolved, and
  unresolved/ambiguous. The two adjacent `TObjString` objects pin the exact
  schema and label mapping so a downstream projection cannot silently
  reinterpret an integer category.

Each file also stores versioned analysis/selection metadata, trigger and
associate thresholds, pair identity, raw checksum, campaign/manifest binding,
event/trigger/pair accounting, same-sign factor, event-filter contract, and
axis-flow diagnostics.

The physical THnSparse axes provide headroom rather than an analysis upper
selection. Underflow/overflow is audited. A populated unexpected flow or
undeclared pT/multiplicity truncation fails validation.

## Single-file worker

The wrapper is:

```text
run_status_analysis.sh RAW_ROOT_FILE FINAL_PAIR_DIRECTORY \
  [CAMPAIGN TUNE LOGICAL_ID RAW_SHA256 ANALYSIS_COMMIT MACRO_SHA256 \
   PURPOSE [CANONICAL_MANIFEST_SHA256 RAW_VALIDATION_RECEIPT \
   RAW_VALIDATION_RECEIPT_SHA256]]
```

Publication jobs always use the full provenance arguments rendered by the
submit tools. The wrapper:

1. requires a tracked-clean analysis checkout;
2. pins macro, raw, commit, and optional manifest hashes;
3. for canonical jobs, verifies the manifest-selected immutable
   `hf_raw_validation_receipt_v1`, its validation log, the raw checksum, and
   the exact campaign/tune/logical identity;
4. independently applies `analysis_raw_input_fail_closed_v1` before filling:
   `complete=1`, requested = successful = metadata/tree entries, attempts =
   successes + failures, all zero-required producer invariant counters,
   exact consumed scalar/vector types, finite weights and kinematics, vector
   cardinality, per-event invariant flags, and weight-sum closure;
5. creates an attempt-unique staging directory;
6. scans the raw file once and writes all 300 pairs;
7. validates the full directory;
8. writes `hf_analysis_job_metadata_v3`, including the raw-validation
   evidence mode and receipt path/SHA-256 (or explicit nulls for a
   noncanonical direct-preflight diagnostic);
9. atomically promotes the directory.

An existing directory is reused only if its pair inventory, clean analysis
log, v3 job metadata, raw checksum, commit, macro, event filter, manifest, and
receipt binding all validate exactly; it is never silently overwritten.

### Event-filter modes

Normal canonical per-file analysis uses all events:

```text
event_filter_schema = all_events_v1
modulo = 0
remainder = -1
```

Gate D uses ten disjoint pilot blocks by setting:

```bash
export HADRONIZATION_EVENT_FILTER_MODULO=10
export HADRONIZATION_EVENT_FILTER_REMAINDER=<0..9>
```

The macro then accepts unsigned `event_id % 10 == remainder` and writes
`unsigned_event_id_modulo_v1`. Remainders 0--9 must be disjoint and their
histogram union must reproduce the all-event pilot. This is Gate-D pilot
validation. The first-stage 100M/tune freeze instead defines ten deterministic
file-level block manifests, each containing ten complete files per tune. A
reviewed superseding freeze keeps the same ten blocks with `N/10` complete
files per tune, where equal `N >= 100` is read from the sealed manifest.

## Canonical sealed-manifest analysis

The sealed freeze is the only source of queued raw paths:

```bash
./generation/submit/submit_status_analysis.sh \
  Production/<CAMPAIGN>/freeze \
  <PRODUCTION_ROOT> \
  AnalysisOutput/<CAMPAIGN> \
  --dry-run
```

Inspect `AnalysisOutput/<CAMPAIGN>/submit_canonical_analysis.sub`, then submit
from a Stoomboot interactive host:

```bash
./generation/submit/submit_status_analysis.sh \
  Production/<CAMPAIGN>/freeze \
  <PRODUCTION_ROOT> \
  AnalysisOutput/<CAMPAIGN> \
  --submit
```

The renderer queues exactly the `3*N` rows from
`canonical_manifest.jsonl`: 300 rows in the 100-file/tune first stage, or the
full equal-tune superseding exposure with `N >= 100` and `N % 10 == 0`.
Directory discovery, “first N,” and unlisted reserve files are forbidden. For
a first-stage freeze, `<PRODUCTION_ROOT>` is
`Production/<CAMPAIGN>`. A superseding manifest can contain rows from several
immutable source campaigns, so its production root is the collection root
`Production`. The submit pins:

- raw path and SHA-256;
- campaign/tune/logical ID/canonical slot;
- analysis commit;
- macro SHA-256;
- canonical-manifest SHA-256;
- output directory.

Condor does not inherit the submitter environment.

After completion:

```bash
python3 tools/validate_analysis_outputs.py \
  Production/<CAMPAIGN>/freeze/canonical_manifest.jsonl \
  AnalysisOutput/<CAMPAIGN> \
  --production-root <PRODUCTION_ROOT> \
  --checkout "$PWD" \
  --report AnalysisOutput/<CAMPAIGN>/validation/analysis_outputs.json
```

The `hf_analysis_output_validation_v2` report requires all `3*N` canonical
per-raw-file directories, one exact raw checksum per directory, and all 300
fixed signed-pair files inside each directory. Extra directories or missing
pairs fail. Here 300 is the pair-registry size, not the number of final raw
inputs.

## Gate-B pilot analysis

For the exact nine Gate-B rows outside the automated Gate-D preparation:

```bash
./submit_gate_b_analysis.sh \
  campaigns/<GATEB_CAMPAIGN> \
  Production/<GATEB_CAMPAIGN> \
  AnalysisOutput/<GATEB_CAMPAIGN> \
  --dry-run
```

Use `--submit` on Stoomboot after inspection. Optional
`--scope=central` and `--scope=sensitivity` restrict processing to that exact
manifest-declared subset; they do not discover files. The validator is:

```bash
python3 tools/validate_gate_b_analysis_outputs.py \
  campaigns/<GATEB_CAMPAIGN> \
  Production/<GATEB_CAMPAIGN> \
  AnalysisOutput/<GATEB_CAMPAIGN> \
  --report AnalysisOutput/<GATEB_CAMPAIGN>/validation/outputs.json
```

## Canonical merging and ten blocks

The freeze contains:

```text
canonical_manifest.jsonl
block_01.jsonl ... block_10.jsonl
```

Each block has `N/10` complete files per tune (ten in the first stage). The ten
manifests are disjoint and their union is exactly the central manifest.
Assignment is frozen before analysis as
`block = canonical_slot % 10`; it is not random and does not depend on any
physics observable.

Merge both central and block products:

```bash
HADRONIZATION_EXPECTED_PAIR_SCHEMA=v3 \
./merging/merge_root_files.sh \
  Production/<CAMPAIGN>/freeze \
  <PRODUCTION_ROOT> \
  AnalysisOutput/<CAMPAIGN> \
  AnalyzedData \
  <OUTPUT_TAG>
```

Arguments are, in order: freeze directory, production root, analysis root,
analyzed-data base, and optional output tag. Do not omit the production root.

`HADRONIZATION_EXPECTED_PAIR_SCHEMA` is **required and has no default**. It is
the schema this campaign demands of its merged pair files, and the driver hands
it to the closure gate as `EXPECTED_SCHEMA` (review finding A4: a gate whose
expectations come from the thing under test cannot fail it). Use `v3` for the
Run-3 production and for every systematic variation; `v2` only for a
deliberately re-run legacy campaign. The driver resolves the tag against
`config/pair_file_object_contract_v1.json` before it starts work, so a missing
or unknown value is refused in the first seconds rather than eleven hours later
at the gate.
Use `Production/<CAMPAIGN>` for a first-stage freeze and the `Production`
collection root for a superseding union whose manifest rows carry their source
campaign prefixes.

Outputs are:

```text
AnalyzedData/complete_root_<OUTPUT_TAG>_MONASH/
AnalyzedData/complete_root_<OUTPUT_TAG>_JUNCTIONS/
AnalyzedData/complete_root_<OUTPUT_TAG>_CLOSEPACKING/
AnalyzedData/SUBSAMPLES_<OUTPUT_TAG>/combined_root_subSamples_<TUNE>/combined_root_1/
...
AnalyzedData/SUBSAMPLES_<OUTPUT_TAG>/combined_root_subSamples_<TUNE>/combined_root_10/
```

Every merged directory is staged, object/provenance validated, checksummed,
and promoted only if the destination is absent. An existing destination is
accepted only if its contents and provenance validate exactly.

`make_subsamples.sh` is a compatibility entry point to the same canonical
merge command:

```bash
./merging/make_subsamples.sh \
  Production/<CAMPAIGN>/freeze \
  <PRODUCTION_ROOT> \
  AnalysisOutput/<CAMPAIGN> \
  AnalyzedData \
  <OUTPUT_TAG>
```

It no longer offers random/bootstrap discovery for publication inputs.

## Multiplicity classes

The central counter is `NCH_PRIMARY_CHARGED_ETA10_V1`: final charged
non-heavy-flavour particles with `pT > 0.15 GeV/c` and `|eta| <= 1`.
`NCH_PRIMARY_CHARGED_ETA40_V1` is the `|eta| <= 4` cross-check.
Percentiles are derived separately for each tune from every event in the
frozen canonical sample, before trigger selection. They are hard-heavy-sample
percentiles, not minimum-bias centrality.

Integer classes must be mutually exclusive and exhaustive. Boundaries,
inequalities, achieved fractions, and overflow handling are provenance, and
the same full-sample boundaries are used for all ten blocks. Plot order is:

```text
90-100, 80-90, 70-80, 60-70, 50-60, 40-50,
30-40, 20-30, 10-20, 1-10, 0-1
```

## Statistical estimators

Central values come from the complete sealed `N`-file union per tune
(`N=100` in the first stage). They are not the mean of block estimators. With
`K=10`:

```text
SEM = sqrt(sum((x_k - mean(x))^2) / (K*(K-1)))
```

Compute inside every block:

- OS and SS per-trigger normalization;
- OS-minus-SS subtraction;
- integration;
- baryon-to-reference-meson balancing-yield ratio.

This retains OS/SS and numerator/denominator covariance. Tunes are
independently generated, so same-numbered blocks are not treated as paired
events; tune-ratio errors use independent propagation. ROOT `Sumw2` is
retained as input validation, not substituted for the block covariance.

Zero trigger/reference denominators and non-finite values are errors.
Negative finite OS-minus-SS yields are retained and reported. Every final
point needs ten finite estimates and a positive SEM unless a documented
deterministic identity proves degeneracy.

Run the predeclared ten-block, largest equal-exposure slot-modulo divisor in
`[11,20]` (falling back to ten), and manifest-derived `N`-file delete-one
comparison:

```bash
python3 tools/statistical_robustness.py \
  --canonical-freeze Production/<CAMPAIGN>/freeze \
  --per-job-root AnalysisOutput/<CAMPAIGN>/per_job \
  --output-directory \
AnalysisOutput/<CAMPAIGN>/validation/statistical_robustness \
  --checkout "$PWD"
```

## Legacy and diagnostic analysis

The following are not canonical balancing inputs:

- `hf_mult_pt_analysis_multi.C`;
- `bb_mult_pt_analysis_multi.C`;
- `cc_mult_pt_analysis_multi.C`;
- `status_analysis_bb.C`, `status_analysis_cc.C`, `status_analysis_qq.C`;
- discovery-based `Job700` commands;
- round-robin event subsamples from older inclusive scripts;
- hybrid/manual merges of unmanifested directories.

They remain useful for historical/inclusive comparisons. In particular,
`hAsKinematics` from the pair path is pair conditioned and cannot be
relabeled as an inclusive spectrum; active inclusive spectra are produced
from raw trees by the dedicated plotting consumer.

The dated:

```text
AnalyzedData/complete_root_21_06_2026_<TUNE>
AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_<TUNE>
```

are metadata-free legacy regression inputs. They retain Paul's old effective
selection and do not demonstrate raw-v5 selector coverage.

## Generated data

Canonical analysis and merged outputs live under ignored paths:

```text
AnalysisOutput/
AnalyzedData/complete_root_*/
AnalyzedData/SUBSAMPLES_*/
```

They are generated but not disposable: preserve the manifests, validation
reports, provenance sidecars, merge logs, and checksums used for a release.
Never broad-clean a shared analysis checkout or overwrite a dated legacy
directory.
