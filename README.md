# Hadronization

This repository contains the PYTHIA 8 and ROOT workflow for the
publication-level heavy-flavour balancing analysis in pp collisions at
13.6 TeV. The active implementation is developed on the explicitly requested
`full-production` branch. Paul Veen's merged THnSparse analysis and plotting
architecture on stable `main` is the compatibility baseline; changes in this
branch are limited to demonstrated physics, statistical, scaling, or
reproducibility defects.

The authoritative operational guide is
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md). The complete scientific
specification is
[`PUBLICATION_READY_CODING_AGENT_INSTRUCTIONS.md`](PUBLICATION_READY_CODING_AGENT_INSTRUCTIONS.md).
No production is publication-authorized merely because a ROOT file exists, a
Condor job completed, or a plot rendered.

## Active physics contract

The central selector is:

```text
hard_trigger_primary_ground__primary_ground_associate_v1
```

The active producer is
`SimulationScripts/heavyflavourcorrelations_status.cpp`. Its immutable
contracts are:

| Contract | Version |
|---|---|
| raw ROOT schema | `hf_primary_ground_raw_v6` |
| origin algorithm | `signed_heavy_constituent_complete_mothers_unique_v4` |
| heavy-stability audit | `heavy_stability_audit_v2` |
| exhaustive post-init settings snapshot | `effective_pythia_settings_exhaustive_v2` |
| tune-difference allowlist | `pythia_tune_difference_allowlist_v2` |
| all-primary-heavy constituent match | `primary_all_heavy_constituent_match_v1` |
| central multiplicity | `NCH_PRIMARY_CHARGED_ETA10_V1` |
| multiplicity cross-check | `NCH_PRIMARY_CHARGED_ETA40_V1` |
| multiplicity definition | `primary_charged_light_hadron_level_v1` |

Triggers are signed, direct-primary, generator-stable ground-state heavy
hadrons with `pT > 1 GeV/c`, `|eta| <= 4`, and a resolved match to the selected
hard heavy quark. Associates use the same lifecycle and registry definition
with `pT > 0.15 GeV/c`, `|eta| <= 4`, but retain all resolved and unresolved
origin categories. Pairs are ordered and conditional on the trigger; the
canonical same-sign factor is 1, not 0.5. Particles and antiparticles remain
separate.

Event activity is classified by a genuine charged-particle multiplicity:
final, charged, non-heavy-flavour particles with `pT > 0.15 GeV/c`. The
central counter uses `|eta| < 1` and the cross-check uses `|eta| < 4`. This is
the hadron-level analogue of the conventional primary-charged-particle
definition (`c*tau0 > 1 cm`, or descended only from shorter-lived parents),
which the tune cards enforce through `ParticleDecays:limitTau0`. Charm and
beauty hadrons are excluded because their decays are disabled here, so an
experiment would count their daughters instead; the exclusion also keeps the
classifier from correlating with the observable it classifies.

The observable is model-level and generator-stable. It is not a
decay-inclusive experimental yield, a detector-level measurement, a
minimum-bias multiplicity analysis, or automatically a unit-normalized
conserved-charge balance function.

## Repository roles

- `SimulationScripts/`: unified producer, tune cards, generated registries,
  and build rules. Split bbbar/ccbar producers are legacy regressions.
- `Validation/`: raw, origin, tune, pair-directory, canonical-manifest,
  pTHat, and Gate-D ROOT audits.
- `config/`: signed species and pair registries, tune allowlist, statistical
  specifications, and the dataset selector.
- `tools/`: immutable campaign/seed/registry tooling, Condor renderers,
  canonical freeze/seal logic, Gate A--D runners, and output validators.
- `AnalysisScripts/status_analysis_THnSparse_qq.C`: one-pass, charge-resolved
  300-pair reduction that preserves Paul's ROOT object and filename contract.
- `PlottingScripts/improvedPlotting_THnSparse.C`: active paper balancing and
  correlation plotting path.
- `PlottingScripts/TunePlotStyle.h`: sole tune-style authority.
- `Balancing_and_Sampling/`, split analysis macros, `improvedPlotting.C`, and
  dated `21_06_2026` data: retained legacy/regression material, never a source
  of new central claims.

## Local and Nikhef roles

The protected local checkout is:

```text
/Users/wax/Documents/Research/Projects/Hadronization
```

It contains unrelated bibliography and working-paper changes. Do not clean,
stash, reset, overwrite, or include them in production commits. The isolated
implementation worktree is:

```text
/private/tmp/hadronization-full-production
```

The canonical Nikhef checkout is:

```text
/data/alice/ipardoza/Hadronization
```

Nikhef supplies the CVMFS ROOT/PYTHIA environment, HTCondor execution, and
large raw/derived data storage. The separate checkout
`/data/alice/ipardoza/Hadronization-main` is a protected deterministic-seed
feature checkout and is not canonical `main`. Use a clean, commit-pinned
execution checkout for each gate/campaign; do not repurpose an old dirty
`Hadronization-full-production*` directory.

After review and merge, synchronize code with `git fetch` and fast-forward
only. Never force-push or destructively reset either repository.

## Build and immutable gates

On a clean Nikhef execution checkout:

```bash
cd /data/alice/ipardoza/Hadronization-full-production-run-<N>
source setupEnv.sh
python3 tests/test_pythia_runtime_contract.py
./tools/build_producer.sh "$PWD"
```

The release sequence is fail-closed:

```bash
mkdir -p Production/validation
./run_publication_gate_a.sh Production/<GATEA_EVIDENCE>

python3 tools/evaluate_pthat_sensitivity.py \
  campaigns/<GATEB_CAMPAIGN> \
  Production/<GATEB_CAMPAIGN> \
  Production/<GATEB_CAMPAIGN>/pthat

./run_publication_gate_b.sh \
  campaigns/<GATEB_CAMPAIGN> \
  Production/<GATEB_CAMPAIGN> \
  Production/<GATEB_CAMPAIGN>/pthat/pthat_sensitivity_decision.json \
  Production/<GATEB_CAMPAIGN>/gate_b

./run_publication_gate_c.sh Production/<GATEC_EVIDENCE>

./run_publication_gate_d.sh prepare \
  Production/<GATED_ANALYSIS> \
  --campaign-dir campaigns/<GATEB_CAMPAIGN> \
  --production-root Production/<GATEB_CAMPAIGN> \
  --gate-b-report Production/<GATEB_CAMPAIGN>/gate_b/gate_b_report.json
```

Gate A is presently blocked on physics review, not on missing audit code.
`Validation/AuditSpeciesRegistry.C` checks the installed PYTHIA table and
`tools/pdg_2025_species_audit.py` independently checks the operational
registry against the checksum-bound official PDG 2025 extract in
`config/pdg_2025_species_reference_v1.json`. Of 50 signed entries, 44 are
corroborated and six (`+/-5212`, `+/-5312`, and `+/-5322`) remain
`NEEDS_PHYSICS_REVIEW`. The audit therefore exits 2 and Gate A retains the
same review-blocked state. No physics signoff or operational-registry change
exists: Sigma-b-zero remains unmeasured/model-predicted, `5312`/`5322` have no
official PDG MCID assignment, and Xi-prime-b-zero has no directly listed
measured state/mass. See `REPRODUCIBILITY.md` for the official URLs,
checksums, and exact extraction/audit commands. No full production is
authorized.

Gate D is not complete after `prepare`. A human must review the rendered PDFs,
and a physics reviewer must compare the corrected selector with the legacy
100M result. `finalize` requires both checksum-bound JSON reports:

Preparation also runs the full-paper-config exhaustive ten-block audit. A
one-million-event pilot may return only the explicit
`PILOT_INSUFFICIENT_FOR_FULL_PAPER` coverage state, with publication
promotion disabled, while representative smoke points still pass. Any other
audit failure fails Gate D; the coverage-only state is a production-sizing
result, not evidence that the paper plots are complete.

```bash
./run_publication_gate_d.sh finalize \
  Production/<GATED_FINAL> \
  --analysis-root Production/<GATED_ANALYSIS> \
  --campaign-dir campaigns/<GATEB_CAMPAIGN> \
  --legacy-comparison-report <LEGACY_REVIEW.json> \
  --visual-review-report <VISUAL_REVIEW.json>
```

The finalized Gate-D PASS must also contain
`hf_gate_d_storage_projection_v1` with `state=PASS` and
`gate_e_storage_authorized=true`. Preparation measures the 100/200/200 raw
candidate and simultaneous-partial footprint, canonical per-job analysis,
central and ten-block merges, and publication-output allowance. Finalization
repeats the capacity check from `os.statvfs(...).f_bavail`. On each involved
filesystem the projection may consume at most 70% of currently available
space and must leave at least the larger of 5% of capacity or 500 GiB.

The latest 2026-07-30 read-only snapshot, at
`2026-07-30T17:39:21+02:00`, is already storage-blocking: capacity was
`36,688,187,162,624` bytes, `f_bavail` was `1,671,602,503,680` bytes, and the
5% reserve was `1,834,409,358,131` bytes. The filesystem was therefore short
by `162,806,854,451` bytes (about 151.7 GiB) before adding any production
data. This volatile measurement must be repeated, but Gate D/E cannot pass
while the fresh snapshot remains below the reserve floor.

Development mode can diagnose a dirty checkout but is permanently
noncanonical and cannot authorize production.

If Gate B observes any unresolved publication-trigger candidate, it must stop
at `NEEDS_SIGNOFF`. The project owner—not an agent—must decide the treatment
and record it at
`campaigns/<GATEB_CAMPAIGN>/GATE_B_PHYSICS_SIGNOFF.json`. The
`resolve_publication_gate_b_signoff.sh` workflow revalidates the sealed
original report, raw files, receipts, pTHat evidence, exact nine-sample count
table, and read-only owner file before writing a separate immutable
superseding PASS; it never alters the original `NEEDS_SIGNOFF` tree.

Every full launch also requires a distinct read-only
`PHYSICS_ORIGIN_SIGNOFF.json` with schema
`hf_full_production_origin_signoff_v1`, decision
`APPROVE_FULL_PRODUCTION`, and `reviewer_role=project_owner`. It binds the
exact Gate-B path/checksum/campaign/ordinal and all nine tune/threshold
unresolved counts. For a zero finding it must record exactly “No unresolved
trigger candidates were observed; no special treatment is required.” For a
nonzero finding it must record exactly “Exclude unresolved triggers
centrally; retain unresolved associates as a reported origin category” and
bind the superseding Gate-B PASS. `FULL_PRODUCTION_GATE_AUTHORIZATION.json`
is a separate owner artifact that binds the canonical Gate A--D and pTHat
reports. Both full-launch owner artifacts must be single-link mode-`0444`
regular files with real explicitly UTC, non-future owner timestamps.

## Candidate campaign and canonical sample

The first-stage launch has exactly:

- 100 MONASH candidates;
- 200 JUNCTIONS candidates;
- 200 CLOSEPACKING candidates.

Each logical job contains exactly 1,000,000 successful events. JUNCTIONS and
CLOSEPACKING IDs 100--199 are reserves. After validation, the deterministic
first-stage freeze contains exactly 100 files per tune: 300 files and
300,000,000 successful events total. Reserve files never add statistical
weight. If the predeclared coverage/precision audit requires an expansion,
the superseding final freeze must retain equal tune exposure with
`N >= 100`, `N % 10 == 0`, three tunes, and ten blocks of `N/10` files per
tune. Consumers derive `N` from the sealed manifest; 300 is the fixed number
of pair definitions, not a fixed final raw-file count.

Expansion is fail-closed and executable: it uses a new parent-bound
`A/2A/2A` candidate campaign, a separately sealed equal-tune extension, and a
new superseding `P+A` freeze whose ten blocks are rederived over the complete
union. It requires failing predeclared coverage/precision evidence, a fresh
storage PASS, a new child-specific Gate-E authorization, and a distinct
owner-authored `EQUAL_TUNE_EXPANSION_AUTHORIZATION.json`; the parent's launch
authorization cannot be reused. See
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md#executable-equal-tune-expansion-procedure)
for the exact generation, submission, freeze, supersede, validation, and
downstream commands.

`tools/generate_expansion_evidence.py` deterministically generates both the
parent-bound coverage/precision decision and the fresh child-specific storage
projection from measured inputs. The generator is tested and write-once, but
it does not authorize an expansion: the resulting machine artifacts must pass
their validators and be bound by a separate real-owner expansion
authorization. They must never be hand-authored.

Campaign directories, candidate manifests, seed ledgers, submission claims,
scheduler records, raw-validation receipts, freeze manifests, and seals are
write-once evidence. A cross-checkout shared submission registry prevents
campaign ordinal or seed-range reuse. Retries preserve the logical ID but
require a new append-only attempt, new seed, and explicit evidence of the
failed/lost prior attempt.

Do not create or submit a full campaign until Gates A--D, storage projections,
the mandatory origin decision, and the full-production owner authorization
are complete. See [`Condor_README.md`](Condor_README.md).

## Analysis, blocks, and uncertainty

The final analysis queues only the sealed canonical manifest (three equal
tune subsets, `3*N` rows):

```bash
./submit_status_analysis.sh \
  Production/<CAMPAIGN>/freeze \
  Production/<CAMPAIGN> \
  AnalysisOutput/<CAMPAIGN> \
  --dry-run
```

Every canonical analysis row binds the selected raw file and its immutable
raw-validation receipt/log hashes. The worker still reopens the ROOT file and
applies the independent `analysis_raw_input_fail_closed_v1` contract before
any fill: exact completion and event-count identities, attempts = successes +
failures, zero producer invariant-failure counters, exact consumed branch
types, per-event invariant flags, finite weights/kinematics, vector
cardinality, and weight-sum closure. The resulting
`hf_analysis_job_metadata_v3` records
`immutable_receipt_plus_direct_preflight_v1`; diagnostic runs without a sealed
canonical receipt are explicitly marked `direct_preflight_only_v1` and are
not publication evidence.

The canonical freeze defines ten deterministic file blocks by
`canonical_slot % 10`; each contains `N/10` one-million-event files per tune
(ten in the initial 100-file/tune stage).
Gate D uses a distinct pilot-only mechanism: the three central
one-million-event pilots are each analyzed once in full and ten more times
with `unsigned_event_id_modulo_v1` remainders 0--9. Both methods are disjoint
and their union must reproduce the corresponding central input.

For block estimates `x_k`, with `K=10`:

```text
SEM = sqrt(sum((x_k - mean(x))^2) / (K*(K-1)))
```

OS-minus-SS, integrations, and baryon-to-reference-meson ratios are formed
inside each block before the SEM is calculated. This retains within-tune
covariance. Independently generated tune uncertainties are propagated as
independent quantities, not paired by block number. ROOT `Sumw2` is retained
for validation but is not substituted for block covariance.

## Plotting

The checked-in full and smoke configs are:

```text
PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json
PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json
```

Both use complete-root central values, ten disjoint subsamples, and
`calculate_errors=true`. The complete-root config is reduced scope with the
same uncertainty prescription; it is not a no-error result. The dated
`complete_root_21_06_2026` and `SUBSAMPLES_700` inputs remain a
metadata-free, explicitly tagged legacy regression. They prove supported
error propagation but failed exhaustive paper coverage and cannot be promoted
as new-selector results.

These checked-in full/smoke configurations are canonical metadata-v2,
ordered-pair, factor-one contracts. With the current
`legacy_21_06_2026` selector they intentionally refuse to run. The separate
`legacy-regression` target is the only supported dated-data path and cannot
produce a promotable paper artifact.

```bash
./PlottingScripts/run_paper_plots.sh validate-inputs
./PlottingScripts/run_paper_plots.sh smoke
./PlottingScripts/run_paper_plots.sh thnsparse
./PlottingScripts/run_paper_plots.sh all
```

`smoke` exercises the reduced pair selection and its matching multiplicity
boundary without repeating the full inclusive raw-kinematics scan. Run
`kinematic-spectra` explicitly, or through `all`, after the reduced gate
passes.

For raw-v5/v2 pair metadata, trigger/associate pT and eta selections were
already applied upstream and the plotting macro validates them without
re-cutting. Only the exact tagged metadata-free `21_06_2026` regression uses
the JSON pT/eta fields as legacy recuts. Partial/mixed selection metadata and
any undeclared upper-pT selection are rejected.

Tune style is fixed:

| Tune | Colour | Marker | Line |
|---|---|---:|---|
| MONASH | black | 20 | solid |
| JUNCTIONS | blue+1 | 21 | dashed |
| CLOSEPACKING | magenta+1 | 22 | style 7 |

Tune ratios inherit the numerator tune style. See
[`PlottingScripts/README.md`](PlottingScripts/README.md) and
[`plotting_documentation.md`](plotting_documentation.md).

`run_paper_plots.sh` loads `config/dataset_selector.json` and exports its
publication-eligibility flag, canonical manifest, production root, analysis
root, analyzed-data base, complete-root tag, and block base. The checked-in
legacy row is explicitly `publication_eligible: false`; canonical paper
targets must refuse it. Canonical inclusive raw plots consume only the sealed
manifest membership and require the selected files' sizes and SHA-256 values
to match. Recursive tune-directory discovery is available solely through the
explicitly named `legacy_recursive_diagnostic` mode and is not publication
evidence.

The prepublication lifecycle uses `status: canonical_candidate` with
`publication_eligible: false` and null authorization fields. It may produce
checksum-bound validation plots, boundary/origin/robustness evidence, and
human-review material, but every receipt is forced ineligible. Promotion to
`status: canonical` requires the exact immutable scientific-review and
project-owner authorization described in `REPRODUCIBILITY.md`; a selector
Boolean alone is rejected. Final figures must then be regenerated.

Every regenerated PDF, PNG, and ROOT macro receives an adjacent
checksum-bound sidecar from `tools/final_plot_provenance.py`. Its shared run
receipt records the exact input inventory, canonical and ten block manifest
hashes, analysis/plot commits, selection/cut versions, command, timestamp,
configuration, multiplicity-boundary receipt, and output checksums.
Canonical runs fail closed if any binding is missing or stale; legacy and
Gate-D pilot products are explicitly `publication_eligible=false`.

## Generated and protected data

The following are generated and ignored:

```text
Production/
campaigns/
AnalysisOutput/
AnalysisResults/
AnalyzedData/complete_root_*/
AnalyzedData/SUBSAMPLES_*/
PlottingScripts/Plots/
logs/
Jobs/
```

Do not commit bulk ROOT, PDF, PNG, ROOT-generated macro, Condor log, campaign,
or receipt output. Archive final immutable evidence and result tables through
the reviewed release process. Do not delete or overwrite legacy raw data,
tracked paper figures, the protected working paper, or bibliography work.

## Current release status

The repository implementation remains pre-production until canonical
release-commit Gates A--D pass. The old `21_06_2026` sample is structurally
useful but lacks ten finite estimates for every full-config observable.
No 300M launch, final figure, physics sign-off, or publication completion
should be inferred from historical pilots or development reports. The current
evidence ledger is
[`ValidationReports/PREPRODUCTION_GATE_REPORT_20260730.md`](ValidationReports/PREPRODUCTION_GATE_REPORT_20260730.md).
