# Pre-production gate report — 2026-07-30

Status: **not authorized for full production**.

This is a human-readable evidence ledger, not a machine gate artifact. It does
not substitute for the immutable JSON reports produced by
`run_publication_gate_{a,b,c,d}.sh`, a project-owner physics decision, or the
full-production launch authorization.

## Protected source state

- implementation branch: `full-production`;
- verified stable-main baseline when the isolated worktree was created:
  `11884cf1ad3613e8e6997bbff32d48a3e7d89570`;
- isolated local implementation:
  `/private/tmp/hadronization-full-production`;
- protected dirty local checkout:
  `/Users/wax/Documents/Research/Projects/Hadronization`;
- canonical Nikhef checkout:
  `/data/alice/ipardoza/Hadronization`;
- protected, noncanonical Nikhef deterministic-seed checkout:
  `/data/alice/ipardoza/Hadronization-main`.

The local bibliography change and untracked paper directory remain outside
the plotting/production commits. The protected Nikhef feature checkout must
not be reset, merged, or repurposed for this task. Old
`/data/alice/ipardoza/Hadronization-full-production*` execution checkouts are
diagnostic evidence, not canonical `main`.

Paul Veen's merged THnSparse architecture on stable `main` remains the
scientific-consumer baseline. The publication branch changes it only where a
test establishes a physics/statistical/methodological or fail-closed
reproducibility defect.

## Current implementation contracts

The release candidate must use:

| Contract | Version |
|---|---|
| raw schema | `hf_primary_ground_raw_v6` |
| central selector | `hard_trigger_primary_ground__primary_ground_associate_v1` |
| origin algorithm | `signed_heavy_constituent_complete_mothers_unique_v4` |
| heavy-stability audit | `heavy_stability_audit_v2` |
| effective settings | `effective_pythia_settings_exhaustive_v2` |
| tune allowlist | `pythia_tune_difference_allowlist_v2` |
| all-primary-heavy match | `primary_all_heavy_constituent_match_v1` |
| pair analysis schema | `paul_pair_objects_primary_ground_v2` |
| analysis metadata | `hf_analysis_job_metadata_v3` (raw receipt plus independent fail-closed preflight binding) |
| canonical manifest | `hf_canonical_raw_manifest_v2` |
| canonical summary | `hf_canonical_freeze_summary_v3` |
| canonical validation receipt | `hf_canonical_raw_validation_receipt_v2` |
| canonical seal | `hf_canonical_freeze_seal_v2` |

Any older raw-v3/v4 pilot is historical diagnostic evidence and cannot pass
the current gates.

## Amendment 2026-07-30b: charged-particle multiplicity redefinition

The event-activity classifier was `NCH_HADRONISATION_V1`, which counted only
`e, mu, pi, K, p` carrying PYTHIA hadronisation status 81--89. Measured on the
existing `27-03-2026` reduction that counter has mean 13.8 over `|eta| <= 4`,
roughly a quarter of the true charged-particle multiplicity over the same
range, because every pion from rho, K*, Delta or omega decay was excluded. It
was therefore not a charged-particle multiplicity and could not support the
draft's claim of a connection to measured multiplicity-dependent hadronisation.

It is replaced by `NCH_PRIMARY_CHARGED_ETA10_V1` (central, `|eta| < 1`) and
`NCH_PRIMARY_CHARGED_ETA40_V1` (cross-check, `|eta| < 4`): final, charged,
non-heavy-flavour particles above `pT > 0.15 GeV/c`, with charge and heavy
content taken from PYTHIA ParticleData.

The superseded `NCH_FINAL_STRONG_EM_V1` cross-check has been deleted with its
weak-parent registry, generated header, ancestry traversal, per-event mother
graph and validator reimplementation. Under `ParticleDecays:limitTau0` no
weak-decay daughter is ever final, so that counter reconstructed a condition
the generator already guarantees and was never independent. The two
pseudorapidity windows replace it as a genuine systematic handle.

Consequences that are not yet discharged:

- the raw schema is now `hf_primary_ground_raw_v6`; every raw-v5 pilot is
  historical evidence only and cannot satisfy any gate;
- percentile boundaries, every multiplicity-differential figure, and every
  associated caption must be regenerated;
- `Validation/TestPrimaryChargedDefinition.C` must be run on Nikhef for all
  three tunes as part of Gate A; it is the machine check that the card
  lifetime threshold is equivalent to the conventional 1 cm/c primary
  definition, and it cannot run where PYTHIA is unavailable.

## Gate status

| Gate | Current status | Why |
|---|---|---|
| A | **blocked; must rerun** | Historical passes predate raw-v5 and the final gate/registry contracts. The independent checksum-bound PDG 2025 audit now exists and mechanically corroborates 44/50 signed entries, but six return `NEEDS_PHYSICS_REVIEW`; no physics signoff or registry decision exists. |
| B | **not passed** | No final fresh-seed raw-v5 nine-pilot campaign has been completed and sealed. pTHat, origin, stability, settings, resource, and compression evidence remain required. |
| C | **must rerun canonically** | Earlier synthetic/failure tests are useful, but the new immutable ten-requirement runner must pass at the exact release commit. Development mode is always noncanonical FAIL. |
| D | **not run to completion; storage blocked** | Requires canonical Gate-B PASS, three central raw-v5 pilots, 33 all/block analyses, passing representative smoke points, the versioned exhaustive full-config coverage/sizing audit, a real legacy comparison, measured storage/final capacity evidence, and human visual review. The current volatile read-only storage snapshot is already below the reserve floor. |
| E | **not authorized; storage blocked** | No owner-created origin decision, no owner-created Gates A--D/pTHat authorization, no approved storage projection, and no final launch go-ahead; current available storage cannot satisfy the 5% reserve even before new allocation. |

Historical Gate-A evidence at commits such as `738df28` and `c9c24a9`
demonstrated useful producer, ROOT macro, registry, and hard-carrier tests.
Those artifacts must not be cited as a PASS for a later commit.

### Independent-PDG audit implemented; physics decision still blocked

`Validation/AuditSpeciesRegistry.C`,
`tools/pdg_2025_species_audit.py`, and
`config/pdg_2025_species_reference_v1.json` now establish both installed-
PYTHIA consistency and an independent, per-signed-species comparison against
official PDG 2025 sources:

- `https://pdg.lbl.gov/2025/api/pdg-2025-v0.2.3.sqlite`, SHA-256
  `4f1ecd7d9a55bc05f61618cc4574053c1edc6188fab07bb4bb7ebed69f9ec6d3`;
- `https://pdg.lbl.gov/2025/mcdata/mass_width_2025.txt`, SHA-256
  `24df41d7db48d8be875dbc8f69aab95fdf26a0512cd8c033cef2d73cc92c24ef`.

The exact non-mutating extraction check is:

```bash
python3 tools/pdg_2025_species_audit.py extract \
  --sqlite /absolute/path/to/pdg-2025-v0.2.3.sqlite \
  --mass-width /absolute/path/to/mass_width_2025.txt \
  --registry config/heavy_flavour_species_v1.json \
  --output config/pdg_2025_species_reference_v1.json \
  --check
```

The canonical combined PYTHIA/PDG audit is run by:

```bash
./run_publication_gate_a.sh \
  Production/validation/<COMMIT>/gate_a
```

Its underlying official-source command is
`python3 tools/pdg_2025_species_audit.py check --pythia-csv
<GATE_A>/species_registry_pythia_audit.csv --require-pythia --output
<GATE_A>/species_registry_pdg_audit.json`. The audit deliberately exits 2
with state `NEEDS_PHYSICS_REVIEW`: 44 signed entries are corroborated and six
(`+/-5212`, `+/-5312`, `+/-5322`) are review-blocked. It records no technical
failure and explicitly records `owner_signoff_present=false`.

The evidence establishes that the 2025 PDG database:

- does not assign official MCIDs `5312` or `5322`;
- does not directly list a measured Xi-prime-b-zero state/mass;
- treats Sigma-b-zero as an unmeasured/model-prediction state.

The implementation is complete, but the scientific decision is not. The
audit did not change `config/heavy_flavour_species_v1.json`; no reviewed
treatment, owner signoff, or paper-text decision exists. Gate A must therefore
remain blocked until physics review decides how the operational PYTHIA
entries are represented in production and the paper. Do not silently remove,
relabel, or claim these states as experimentally established.

Historical Gate-C demonstrations showed partial-file rejection, corrupt-file
rejection, new-seed retry, a synthetic 300-row freeze, ten blocks, and a
deterministic 100/200/200 render. The current
`hf_publication_gate_c_report_v1` must reproduce all ten Section-16
requirements in one immutable canonical run.

## Historical pilot findings

Earlier 1,000-success diagnostics, before the final raw-v5 contract, found:

| Tune | publication trigger candidates | unresolved | fraction |
|---|---:|---:|---:|
| MONASH | 544 | 0 | 0 |
| JUNCTIONS | 470 | 6 | 0.012765957 |
| CLOSEPACKING | 450 | 4 | 0.008888889 |

These numbers are not final rates. They established that:

- unresolved cases can be tune dependent;
- status 81--89 is not equivalent to selected-hard origin;
- a permissive or iteration-order tie break could bias tune comparisons;
- final million-event pilots must report trigger and associate origin
  resolution separately.

Several earlier sensitivity analyses also exposed an event-level duplicate
hard-carrier defect: multiple final hadrons could claim one selected hard
quark through a shared string/junction mother range. The implementation now
demotes every conflicting claim to unresolved and retains rejected indices and
group/demotion counters. Raw validation independently requires that no
authoritative duplicate survives.

Raw-v5 adds further closure:

- complete signed constituent content, including Bc and multi-heavy states;
- constituent-level all-primary-heavy matching;
- multi-heavy single-carrier rejection;
- exhaustive heavy-stability v2 serialization and hash;
- exhaustive post-init effective-settings v2 serialization and hash;
- resource/compression metadata needed for Gate-B projections.

Only a fresh raw-v5 campaign at the final commit can validate these fixes.

## Historical campaign/seed ledger

Known immutable operational history includes:

- the old full `HF_100M_primaryGround_ccbb_v1` reservation;
- Gate-B pilot versions through v7;
- historical pilot ordinals through 25;
- a v7 seed range beginning at 260000001;
- earlier failed/held/unsubmitted attempts whose ordinals and seeds remain
  burned.

The next planned corrected Gate-B allocation is:

```text
campaign ordinal: 26
seed base:         270000001
```

This plan is valid only after a reviewed shared-registry baseline confirms no
new claim. If the global registry has advanced, allocate a new range; never
edit or reuse the example.

The shared registry root must be absolute and common to every checkout:

```text
/user/ipardoza/.local/state/hadronization/submission_registry
```

Repository identity:

```text
github.com/waxpardo/hadronization
```

Identity SHA-256 directory:

```text
1442238020041daba768ccebfb260e5516bd697057dfb2ab0ae5aa2f0d84dc02
```

Before the next submission, create one immutable
`hf_submission_registry_baseline_v1` from every historical full/Gate-B
campaign. Preserve and burn historical overlaps; do not omit unsuccessful
campaigns.

## HTCondor and storage findings

Read-only Nikhef inspection established:

- Condor submission must occur on a Stoomboot interactive host such as
  `stbc-i2`, not the login node;
- rendered jobs need a quoted `+JobCategory` and EL9;
- `getenv = False` plus explicit environment prevents accidental shell-state
  inheritance;
- no automatic retry or release is allowed;
- `/data/alice` is shared NFS and requires cautious merge/read concurrency;
- the latest 2026-07-30 read-only Nikhef snapshot, at
  `2026-07-30T17:39:21+02:00`, reported capacity
  `36,688,187,162,624` bytes and available space (`f_bavail`)
  `1,671,602,503,680` bytes. The required 5% reserve is
  `1,834,409,358,131` bytes, so the filesystem was already short by
  `162,806,854,451` bytes (about 151.7 GiB) before allocating any new
  production data.

This storage snapshot is volatile read-only evidence, not a canonical Gate-D
projection artifact. It is nevertheless an explicit Gate-D/E blocker:
available space cannot satisfy the reserve rule even for a zero-byte new
allocation. Gate B must record, per tune, one-million-event elapsed time, peak
RSS, raw bytes, ROOT compression, and projections for:

- exact 300-file canonical data;
- all 500 possible candidate outputs;
- simultaneous partials;
- 90,000 per-job pair files before merging;
- central plus ten block merges;
- plots, logs, receipts, and preserved legacy production.

No full launch is allowed until measured need plus safety margin fits current
headroom.

Historical queue inspection also found old held/running diagnostic jobs from
pre-final implementations. They are noncanonical, but they must not be
removed or released without a deliberate owner decision. Their seeds remain
burned regardless of disposition.

## Correctness and reproducibility defects addressed in code

The branch contains or is integrating tests/fixes for:

1. exact one-million-success accounting rather than attempt counting;
2. one event-tree entry for empty-heavy successful events;
3. integer branch types and globally collision-free event IDs;
4. complete heavy-hadron stabilization and v2 audit;
5. signed constituent-aware complete-mother origin v4;
6. global duplicate-hard-carrier and multi-heavy rejection;
7. trigger-only hard-origin requirement with inclusive associate origins;
8. common direct-primary lifecycle selector for both roles;
9. trigger `pT > 1` and associate `pT > 0.15 GeV/c`;
10. signed charge-conjugate separation and complete 50-state/300-pair
    registries;
11. one raw scan for all pairs;
12. corrected B0/Sigma_b trigger/filename;
13. ordered conditional pair counting without central factor 0.5;
14. canonical-manifest-only analysis/merge/block selection;
15. append-only exact seed and retry evidence;
16. cross-checkout submission registry and historical baseline;
17. semantic validation of canonical Gate A--D and pTHat reports;
18. complete launch-provenance binding through freeze and seal;
19. event-ID-modulo Gate-D pilot blocks;
20. ten-block SEM, nonlinear within-block ratios, and independent-tune
    propagation;
21. raw-v5 upstream selection metadata with no downstream double recut;
22. exact tagged legacy recuts only for `complete_root_21_06_2026`;
23. fail-closed upper-pT/axis-flow, missing-object, and coverage checks;
24. canonical tune styling and numerator-tune ratio style;
25. optional mini-pad null safety and required-pad composition checks.

This list describes intended implementation coverage. Each item still needs
its final-release Gate-A/D regression evidence.

## Legacy plotting evidence

The real Nikhef regression inputs are:

```text
AnalyzedData/complete_root_21_06_2026_MONASH
AnalyzedData/complete_root_21_06_2026_JUNCTIONS
AnalyzedData/complete_root_21_06_2026_CLOSEPACKING
AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_MONASH
AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_JUNCTIONS
AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_CLOSEPACKING
```

They contain the expected 56 pair files centrally and in each of ten
subsamples. Prior validation found required ROOT objects and representative
central-versus-subsample-union agreement.

The exhaustive statistical audit nevertheless found:

- 610 configured observables without ten finite subsample estimates;
- 540 beauty and 70 charm incomplete cases;
- 468 of 1,152 expected final statistical records with `n=10`;
- 1,781 zero-trigger-normalization warnings.

The historical reduced 1--10% legacy-regression selection produced 30/30
finite positive SEM records. That proves error propagation for supported
legacy inputs, not full-paper coverage. The explicit full legacy-regression
audit must continue to fail its coverage gate. Canonical full/smoke targets
must refuse the legacy selector; do not promote a reduced legacy-regression
canvas or label it as raw-v5.

The new plotting selection contract uses pT/eta recuts only for this exact
metadata-free legacy tag. New pair metadata v2 is selected upstream and is
validated without a downstream recut.

## Owner decisions

Every full launch requires two distinct real-owner artifacts:

1. `PHYSICS_ORIGIN_SIGNOFF.json`: mandatory, read-only schema
   `hf_full_production_origin_signoff_v1` with
   `decision=APPROVE_FULL_PRODUCTION`,
   `reviewer_role=project_owner`, a real UTC decision, the exact Gate-B
   path/checksum/campaign/ordinal, and the complete nine-sample
   tune/threshold-by-sector unresolved table and total. With zero, its exact
   policy is `No unresolved trigger candidates were observed; no special
   treatment is required.` With nonzero, its exact policy is `Exclude
   unresolved triggers centrally; retain unresolved associates as a reported
   origin category` and it binds a superseding Gate-B PASS.
2. `FULL_PRODUCTION_GATE_AUTHORIZATION.json`: schema
   `hf_full_production_gate_authorization_v1`, binding exact canonical Gate A,
   Gate B, pTHat, Gate C, and Gate D reports, their checksums/logs, the
   campaign, commit, and origin-decision checksum. Both owner files must be
   single-link mode-`0444` regular files with real explicitly UTC, non-future
   owner timestamps.

The bound Gate-D report must include
`hf_gate_d_storage_projection_v1`, `state=PASS`, and
`gate_e_storage_authorized=true`. Its preparation and fresh finalization
capacity checks use `os.statvfs(...).f_bavail`; each filesystem may allocate
at most 70% of current available space and must retain at least
`max(5% of capacity, 500 GiB)` after the complete raw, partial, analysis,
merged-block, plot, log, and evidence projection.

A checksummed FAIL or `NEEDS_SIGNOFF` report is not a PASS. A coding agent
must not create, backdate, or infer either approval.

## Required next actions

1. Finish code/schema reconciliation and commit the exact release candidate.
2. Run canonical Gate A from a new clean Nikhef execution checkout.
3. Build/review the shared historical reservation baseline.
4. Generate a fresh raw-v5 Gate-B pilot at an unused ordinal/seed interval.
5. Dry-run, inspect, submit, and monitor exactly nine pilot rows.
6. Validate every raw file and receipt; run pTHat and aggregate Gate B.
7. If unresolved triggers are nonzero, stop for owner review and a
   read-only `campaigns/<GATEB_CAMPAIGN>/GATE_B_PHYSICS_SIGNOFF.json`;
   verify it with `resolve_publication_gate_b_signoff.sh --verify-only`, then
   emit a separate immutable superseding Gate-B PASS. Do not alter the
   original `NEEDS_SIGNOFF` report.
8. Run canonical Gate C at the same commit.
9. Run Gate-D preparation, produce the legacy comparison, inspect every
   rendered PDF page, verify the measured storage projection, and finalize
   Gate D with a fresh passing capacity recheck.
10. Recheck `/data/alice` headroom using Gate-B measurements.
11. Generate a new full campaign; do not reuse historical v1.
12. Obtain the mandatory origin decision and full Gate-E authorization.
13. Only then submit 100/200/200 candidates.
14. Reconcile attempts and failure bias; freeze exactly 100 files/tune.
15. Seal the 300-file manifest and ten deterministic file blocks.
16. Run canonical analysis, merging, robustness, strict plotting, exhaustive
    coverage, figure provenance, paper build, and five final reviews.

## Release blockers

- no canonical raw-v5 Gate-A report at the final commit;
- no fresh nine-job raw-v5 Gate-B result;
- no accepted pTHat decision at the final commit;
- no final origin-resolution decision;
- no canonical Gate-C report at the final commit;
- no finalized Gate-D legacy/visual review;
- no measured storage authorization;
- no full-production owner authorization;
- no 300-file canonical freeze/seal;
- no complete ten-block coverage/precision matrix;
- no regenerated and reviewed final paper artifacts.

Therefore no production-scale submission or publication-complete claim is
authorized by this report.
