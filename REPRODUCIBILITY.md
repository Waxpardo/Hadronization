# Reproducing the publication analysis

This is the authoritative operational guide for the publication pipeline.
Paul Veen's THnSparse plotting architecture remains the plotting baseline.
The canonical production and analysis path below supplies it with versioned,
charge-resolved inputs and ten disjoint statistical blocks.

The central observable is a generator-level primary-hadron observable, not a
decay-inclusive experimental yield.  Triggers are hard-origin-matched,
direct-primary, generator-stable ground-state heavy hadrons.  Associates use
the same primary/stability/species definition but may have hard, shower, MPI,
other, or unresolved origin.  The selector is
`hard_trigger_primary_ground__primary_ground_associate_v1`.

## Immutable physics and software inputs

- pp at 14 TeV with PYTHIA 8.315;
- `HardQCD:hardccbar = on` and `HardQCD:hardbbbar = on`;
- `PhaseSpace:pTHatMin = 1.0` GeV for the central campaign;
- MONASH, JUNCTIONS, and CLOSEPACKING are complete configuration bundles;
- ROOT 6.30/01 (ALICE build);
- successful-event accounting: each logical job contains exactly 1,000,000
  successful PYTHIA events;
- 100 canonical logical jobs per tune, hence 100,000,000 successful events per
  tune;
- signed species registry: `config/heavy_flavour_species_v1.json`;
- signed pair registry: `config/heavy_flavour_pair_registry_v1.json`;
- raw schema: `hf_primary_ground_raw_v3`;
- trigger acceptance: `pT > 1.0 GeV/c`, `|eta| <= 4`;
- associate acceptance: `pT > 0.15 GeV/c`, `|eta| <= 4`;
- multiplicity: direct charged primary e, mu, pi, K, p and antiparticles with
  positive status 81--89, `pT > 0.15 GeV/c`, and `|eta| <= 4`;
- ten blocks assigned by `canonical_slot % 10`, with ten one-million-event
  files from each tune in every block.

The generated campaign records hashes of the cards, species registry, pair
registry, repository commit, schema, selector, event count, seed allocation,
and candidate role.  Never edit a campaign directory after submission.  A
changed scientific definition requires a new campaign name and ordinal.

## Worktree and environment

Use a clean checkout of the exact implementation commit on Nikhef:

```bash
cd /data/alice/ipardoza/Hadronization-full-production-run-<N>
git status --short
source setupEnv.sh
root-config --version
pythia8-config --version
./tools/build_producer.sh "$PWD"
```

`setupEnv.sh` first uses ALICE `alienv`.  For non-interactive Nikhef shells
where `alienv` cannot initialise Tcl, it pins the same ROOT 6.30/01 and PYTHIA
8.315 CVMFS installations and the GCC 14.2 runtime required by PYTHIA.  The
producer links only the ROOT Tree, Hist, RIO, and Core components it uses.

The Condor commands must run on a Stoomboot submit host.  The shared
`/data/alice/ipardoza` filesystem is visible to both the login and worker
nodes.

## Gates before full production

Do not submit the 300M canonical campaign until Gates A--D pass and the project
owner has signed the origin-resolution decision.

1. Gate A: compile the producer and ROOT macros; validate both registries,
   exact boundary semantics, tune-card allowlist, ordered-pair combinatorics,
   plotting cuts, and JSON syntax.
2. Gate B: for each tune, run one one-million-success central pilot plus
   smaller `pTHatMin = 0.5` and `2.0` sensitivity pilots.  Validate schema,
   event count, stability, settings, process composition, multiplicity
   definitions, trigger origin, storage, and runtime.
3. Gate C: prove failed and interrupted attempts are never promoted, retries
   use a new ledger seed, stable valid outputs are not overwritten, and a
   synthetic 300-row freeze has ten exact disjoint blocks.
4. Gate D: run raw validation, one-pass analysis, pair-directory validation,
   central/block merging, plotting smoke tests, and one event-to-figure
   provenance trace.

The pilot goal is zero unresolved trigger candidates.  If the validated
fraction is nonzero, `submit_full_production.sh --submit` requires
`PHYSICS_ORIGIN_SIGNOFF.json` in the campaign directory with:

```json
{
  "approved": true,
  "reviewer": "PROJECT OWNER NAME",
  "date": "YYYY-MM-DD",
  "finding": "Measured per-tune unresolved-trigger fractions and review",
  "allowed_unresolved_treatment": "Exclude unresolved triggers centrally; retain unresolved associates as a reported origin category"
}
```

This file records a scientific decision; an agent must not invent it.

## Create and submit an immutable campaign

Choose a globally unused seed interval, campaign name, and ordinal.  From a
clean committed worktree:

```bash
python3 tools/campaign_manifest.py generate \
  --campaign HF_100M_primaryGround_ccbb_v2 \
  --campaign-ordinal <UNUSED_ORDINAL> \
  --events 1000000 \
  --seed-base <UNUSED_SEED_BASE> \
  --max-attempts 1000

python3 tools/campaign_manifest.py validate \
  campaigns/HF_100M_primaryGround_ccbb_v2

./submit_full_production.sh \
  campaigns/HF_100M_primaryGround_ccbb_v2 --dry-run

# Only after Gates A--D and the required owner sign-off:
./submit_full_production.sh \
  campaigns/HF_100M_primaryGround_ccbb_v2 --submit
```

The manifest contains 100 MONASH, 200 JUNCTIONS, and 200 CLOSEPACKING
candidates.  The first 100 per tune are primary; the additional candidates are
coverage-gated reserves.  Automatic retries are disabled.

For a failed logical attempt, allocate a new seed before rendering a dedicated
retry submission:

```bash
python3 tools/campaign_manifest.py allocate-retry \
  campaigns/HF_100M_primaryGround_ccbb_v2 TUNE LOGICAL_ID \
  --reason "documented failure reason"
```

Never release a held job whose attempt may have started, never reuse a seed,
and never replace a valid primary merely because its measured result is
inconvenient.  `runCondorJob.sh` writes to a unique partial name, validates the
ROOT file, then atomically promotes it to
`Production/<campaign>/raw/<TUNE>/hf_<TUNE>_jobNNN.root`.  A promoted file is
never silently overwritten.

## Freeze the equal-statistics sample

After all primary outputs validate, freeze the default primary selection:

```bash
python3 tools/canonical_manifest.py freeze \
  campaigns/HF_100M_primaryGround_ccbb_v2 \
  Production/HF_100M_primaryGround_ccbb_v2 \
  Production/HF_100M_primaryGround_ccbb_v2/freeze \
  --verify-checksums

python3 tools/canonical_manifest.py validate \
  Production/HF_100M_primaryGround_ccbb_v2/freeze

./Validation/validate_canonical_manifest.sh \
  Production/HF_100M_primaryGround_ccbb_v2/freeze \
  Production/HF_100M_primaryGround_ccbb_v2 \
  Production/HF_100M_primaryGround_ccbb_v2/validation/canonical_raw.log
```

If a documented failed primary must be replaced, pass a reviewed selection
JSON to `freeze --selection`.  The replacement must be an already declared
reserve with a ledger-authorized attempt.  The freeze contains exactly 300
rows, 300 unique seeds and raw paths, and ten block manifests whose union is
exactly the central manifest.

## One-pass charge-resolved analysis

Submit only the frozen paths:

```bash
./submit_status_analysis.sh \
  Production/HF_100M_primaryGround_ccbb_v2/freeze \
  Production/HF_100M_primaryGround_ccbb_v2 \
  AnalysisOutput/HF_100M_primaryGround_ccbb_v2 \
  --dry-run

./submit_status_analysis.sh \
  Production/HF_100M_primaryGround_ccbb_v2/freeze \
  Production/HF_100M_primaryGround_ccbb_v2 \
  AnalysisOutput/HF_100M_primaryGround_ccbb_v2 \
  --submit
```

`AnalysisScripts/status_analysis_THnSparse_qq.C` reads each raw file once and
writes all 300 signed ordered-pair files.  It applies the same role cuts to
central and block inputs, counts ordered associates, and does not apply the
legacy same-sign factor of 0.5.  Each per-job directory is promoted only after
all 300 pair files validate.

After all 300 analysis jobs finish:

```bash
python3 tools/validate_analysis_outputs.py \
  Production/HF_100M_primaryGround_ccbb_v2/freeze/canonical_manifest.jsonl \
  AnalysisOutput/HF_100M_primaryGround_ccbb_v2 \
  --report AnalysisOutput/HF_100M_primaryGround_ccbb_v2/validation/analysis_outputs.json

./merge_root_files.sh \
  Production/HF_100M_primaryGround_ccbb_v2/freeze \
  AnalysisOutput/HF_100M_primaryGround_ccbb_v2 \
  AnalyzedData \
  HF_100M_primaryGround_ccbb_v2
```

This creates one validated complete-root directory per tune and ten validated
block directories per tune.  Existing destinations are never overwritten.
Every promoted directory contains its source manifest and merge provenance.

## Plotting and uncertainty prescription

Point a copy of the checked-in THnSparse configs at the new
`complete_root_HF_100M_primaryGround_ccbb_v2_<TUNE>` and
`SUBSAMPLES_HF_100M_primaryGround_ccbb_v2/combined_root_subSamples_<TUNE>`
directories.  Keep `calculate_errors=true` and `nSubSamples=10`.

```bash
jq empty PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json
jq empty PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json

VERBOSE=true THNSPARSE_COMPLETE_ROOT_CONFIG=<NEW_SMOKE_CONFIG> \
  ./PlottingScripts/run_paper_plots.sh smoke

VERBOSE=true THNSPARSE_CONFIG=<NEW_FULL_CONFIG> \
  ./PlottingScripts/run_paper_plots.sh all
```

Central values use the union of all 100 canonical files per tune.  Errors use
the sample standard error of the ten disjoint block estimates,
`SEM = sample_standard_deviation / sqrt(10)`.  Baryon/meson ratios are formed
inside each block before their SEM is computed.  Independent tune-ratio
uncertainties are combined in quadrature.  Zero or non-finite denominators
are fatal.  The run log must show `n=10`, finite nonzero `stdError` for every
non-degenerate final point, no missing files or objects, and no placeholder
errors.

The canonical tune style comes only from
`PlottingScripts/TunePlotStyle.h`: MONASH black/20/solid, JUNCTIONS
blue+1/21/dashed, CLOSEPACKING magenta+1/22/style 7.  Tune ratios inherit the
numerator tune style.

## Required publication archive

Archive, without modifying the immutable raw files:

- implementation commit and clean/dirty state;
- campaign, seed ledger, candidate manifest, origin sign-off, and Condor
  cluster IDs;
- executable, card, registry, and configuration SHA-256 hashes;
- promoted raw-file checksums and attempt metadata;
- freeze summary, canonical manifest, and ten block manifests;
- raw, pair-directory, merged-directory, and analysis-output validation
  reports;
- complete stdout/stderr/Condor logs;
- ROOT and PYTHIA versions and effective tune settings;
- plotting configs, verbose uncertainty log, final PDF/PNG/macro outputs, and
  machine-readable numerical tables;
- a paper-figure map giving generator, config, inputs, output path, and paper
  `includegraphics` consumer.

The legacy `21_06_2026` complete-root and `SUBSAMPLES_700` inputs remain
regression references until a new canonical freeze and all validation gates
pass.  They must not be relabelled as outputs of the new selector.

`config/dataset_selector.json` is the single active-dataset switch used by
`run_paper_plots.sh`. It currently labels `legacy_21_06_2026` as
`legacy_regression_default`. After a new campaign is frozen and merged, add a
fully populated `status: canonical` entry containing its campaign, raw schema,
selector, manifest, production root, analysis root, raw base, complete-root
tag, and block base; validate it with:

```bash
python3 tools/dataset_selector.py validate
python3 tools/dataset_selector.py show
```

Change `active_dataset` only in a reviewed commit after the recorded paths and
manifests pass validation. `USE_DATASET_SELECTOR=false` is diagnostic-only and
must be recorded in the run log.
