# Reproducing the publication analysis

> **Design rationale.** Every physics choice in this repository, its motivation and
> the evidence backing it, is documented in [`docs/DESIGN_AND_RATIONALE.md`](docs/DESIGN_AND_RATIONALE.md).
> Read that first. Changing a physics definition requires updating it in the same commit.

This is the authoritative runbook for the publication pipeline. It describes
the commands that exist in the `full-production` branch; it does not certify
that a gate has passed or that a full campaign has been authorized. Preserve
all immutable evidence and stop at the first failed gate.

Paul Veen's merged THnSparse architecture is the analysis/plotting
compatibility baseline. The publication branch supplies it with a corrected,
versioned producer, one-pass signed-pair outputs, immutable manifests, and ten
disjoint statistical blocks.

## 1. Fixed scientific contracts

The central selector is
`hard_trigger_primary_ground__primary_ground_associate_v1`.

- collisions: pp at 13.6 TeV;
- PYTHIA: 8.315;
- ROOT: 6.30/01 ALICE build;
- processes: `HardQCD:hardccbar = on` and
  `HardQCD:hardbbbar = on`;
- central generator threshold: `PhaseSpace:pTHatMin = 1.0 GeV`;
- tunes: MONASH, JUNCTIONS, CLOSEPACKING as complete configuration bundles;
- raw schema: `hf_primary_ground_raw_v5`;
- origin algorithm:
  `signed_heavy_constituent_complete_mothers_unique_v4`;
- heavy-stability audit: `heavy_stability_audit_v2`;
- exhaustive effective settings:
  `effective_pythia_settings_exhaustive_v2`;
- tune allowlist: `pythia_tune_difference_allowlist_v2`;
- primary-all-heavy closure:
  `primary_all_heavy_constituent_match_v1`;
- trigger: signed registry state, direct primary, generator stable,
  hard-origin resolved, `pT > 1 GeV/c`, `|eta| <= 4`;
- associate: signed registry state, direct primary, generator stable, any
  origin, `pT > 0.15 GeV/c`, `|eta| <= 4`;
- central multiplicity: `NCH_PRIMARY_CHARGED_ETA10_V1`;
- cross-check multiplicity: `NCH_PRIMARY_CHARGED_ETA40_V1`;
- multiplicity definition: `primary_charged_light_hadron_level_v1`;
- pair construction: ordered conditional pairs, self-pairs excluded,
  `same_sign_pair_factor = 1.0`.

Both counters are genuine charged-particle multiplicities: final, charged,
`pT > 0.15 GeV/c`, and inside the stated pseudorapidity window. They are the
hadron-level analogue of the conventional experimental primary-charged-particle
definition, in which a primary is a charged particle with `c*tau0 > 1 cm` that
is produced directly or descends only from particles with `c*tau0 < 1 cm`.

The lifetime condition is enforced by the generator, not reconstructed
afterwards. All three cards set `ParticleDecays:limitTau0 = on` with
`tau0Max = 0.01` mm, so every strong and electromagnetic decay proceeds while
every weakly decaying light hadron stays final. No light hadron has
`0.01 mm < c*tau0 < 10 mm`, so for light flavour the card value is exactly
equivalent to the conventional 1 cm/c threshold;
`Validation/TestPrimaryChargedDefinition.C` asserts that against the installed
PYTHIA ParticleData rather than trusting it, and also recounts both windows
from live events. Because `isFinal()` already means "primary" here, the earlier
ancestry-traversal cross-check has been removed: it reconstructed a condition
the generator already guarantees, so it was not an independent check. The two
pseudorapidity windows are the independent handle instead.

Charm- and beauty-containing hadrons are excluded from both counters. Their
decays are disabled deliberately, so they are final only as an artefact of the
production policy and an experiment would count their decay daughters instead.
Excluding them also removes the autocorrelation that would otherwise exist
between the event-activity classifier and the heavy-flavour observable being
classified. The paper must state this exclusion, and must state that the
central classifier is `|eta| < 1` while trigger and associate acceptance
extends to `|eta| <= 4`.

Each canonical logical output contains exactly 1,000,000 successful
`pythia.next()` events and one tree entry per successful event, including
events without a selected heavy hadron. Attempts equal successes plus
generation failures. Every heavy hadron is retained and made
generator-stable; unrelated light-decay policy remains active.
`heavyBaryonNumber` stores physical integer baryon number (`0`, `+1`, or
`-1`). The validation-only all-primary-heavy uniqueness rule compares distinct
final parent hadrons, so repeated constituents within one multiply-heavy
parent do not create a false duplicate-carrier conflict.

The pair-file-v2 field named `primary_all_heavy_closure_failures` is retained
for schema compatibility. Its precise meaning is the number of selected
events with raw `primary_all_heavy_match_valid != 1`; it is an invariant
failure count, not the category-sum closure table written by
`Validation/AuditOriginResolution.C`. Both the counter (which must be zero)
and the separate closure table are independently validated.

The signed species and pair registries are:

```text
config/heavy_flavour_species_v1.json
config/heavy_flavour_pair_registry_v1.json
```

Generated C++ artifacts must match them:

```bash
python3 tools/generate_registry_artifacts.py --check
```

## 2. Source, worktree, and machine roles

Protected local checkout:

```text
/Users/wax/Documents/Research/Projects/Hadronization
```

This checkout contains unrelated bibliography and working-paper changes.
Never reset, clean, stash, move, overwrite, or stage those changes merely to
synchronize code.

Isolated local implementation worktree:

```text
/private/tmp/hadronization-full-production
```

Canonical Nikhef checkout:

```text
/data/alice/ipardoza/Hadronization
```

Protected, noncanonical Nikhef feature checkout:

```text
/data/alice/ipardoza/Hadronization-main
```

Do not modify the latter as part of this workflow. Create a new clean,
commit-pinned Nikhef execution checkout for gates and production. Do not reuse
an old dirty `Hadronization-full-production*` directory.

Record source state before every canonical run:

```bash
git branch --show-current
git rev-parse HEAD
git remote -v
git status --short
```

Synchronize only with fetch plus fast-forward:

```bash
git fetch origin
git pull --ff-only
```

Never force-push or use a destructive reset. After review and merge, update
canonical Nikhef `main` and the protected local `main` only if the latter can
fast-forward without touching its unrelated work.

## 3. Nikhef environment and HTCondor

On the clean execution checkout:

```bash
cd /data/alice/ipardoza/Hadronization-full-production-run-<N>
source setupEnv.sh
root-config --version
pythia8-config --version
python3 tests/test_pythia_runtime_contract.py
./tools/build_producer.sh "$PWD"
```

`setupEnv.sh` uses ALICE CVMFS and has a pinned noninteractive fallback for
ROOT 6.30/01, PYTHIA 8.315, the required GCC runtime, and
`PYTHIA8DATA=<pinned-package>/share/Pythia8/xmldoc`. The fallback refuses to
continue if `xmldoc/Index.xml` is absent; this prevents PYTHIA from silently
using a stale build-time data path. A ROOT process can return zero after an
ACLiC failure, so canonical logs are also scanned for fatal errors, cling/JIT
errors, unresolved symbols, and segmentation faults.

Submit and monitor Condor jobs from a Stoomboot interactive submit host, for
example `stbc-i2`, not the login node:

```bash
ssh stbc-i2
condor_version
condor_q ipardoza
```

Rendered submits use `getenv = False`, `+UseOS = "el9"`, a quoted mandatory
`+JobCategory`, no automatic retry, and hold on signals or nonzero exit.
`/data/alice` is shared NFS; avoid unnecessary concurrent scanning and
merging. Before any launch:

```bash
df -h /data/alice
du -sh Production/<PILOT_CAMPAIGN>
```

The latest 2026-07-30 `statvfs` snapshot, at
`2026-07-30T17:39:21+02:00`, found capacity
`36,688,187,162,624` bytes and `f_bavail = 1,671,602,503,680` bytes.
The mandatory 5% reserve was `1,834,409,358,131` bytes, leaving a
`162,806,854,451`-byte deficit (about 151.7 GiB) before any new allocation.
Thus Gate D/E storage authorization was blocked at that snapshot; the
approximate free-space display is not usable publication headroom. The state
is volatile and must be remeasured. Gate B must also provide measured per-tune
time, peak RSS, ROOT compression, and raw-byte projections for both the
300-file canonical freeze and all 500 candidates. Include simultaneous
partials, analysis outputs, ten blocks, plots, logs, and preservation of old
production.

## 4. Shared campaign and seed registry

All checkouts must use one absolute shared registry root:

```bash
export HADRONIZATION_SUBMISSION_REGISTRY_ROOT=\
/user/ipardoza/.local/state/hadronization/submission_registry
```

The repository identity is:

```text
github.com/waxpardo/hadronization
```

Its SHA-256 identity directory is:

```text
1442238020041daba768ccebfb260e5516bd697057dfb2ab0ae5aa2f0d84dc02
```

Before the first new claim, build one reviewed immutable baseline from every
historical full and Gate-B campaign directory, including campaigns whose jobs
never ran. Repeat `--campaign-dir` for every historical directory:

```bash
python3 tools/build_submission_registry_baseline.py \
  --repository-identity github.com/waxpardo/hadronization \
  --reviewer "<REAL REVIEWER>" \
  --output \
"${HADRONIZATION_SUBMISSION_REGISTRY_ROOT}/1442238020041daba768ccebfb260e5516bd697057dfb2ab0ae5aa2f0d84dc02/reservation_baseline.json" \
  --campaign-dir campaigns/<HISTORICAL_CAMPAIGN_1> \
  --campaign-dir campaigns/<HISTORICAL_CAMPAIGN_2>
```

Historical collisions are recorded and every involved seed remains burned.
Do not omit a failed, held, killed, abandoned, dry-run-generated, or old pilot
campaign. Do not replace the read-only baseline after claims exist.

## 5. Gate A: static and unit validation

Run from a completely clean checkout at the exact candidate release commit:

```bash
mkdir -p Production/validation/<COMMIT>
./run_publication_gate_a.sh \
  Production/validation/<COMMIT>/gate_a
```

The output directory must not exist. Gate A records a read-only
`hf_publication_gate_a_report_v1`, aggregate log, command logs, environment,
and checksummed inventory. It compiles/builds the changed components and
checks registries, settings, selectors, boundaries, pair combinatorics,
manifest tooling, and plotting contracts.

The independent PDG audit is implemented, but Gate A is intentionally
review-blocked. `Validation/AuditSpeciesRegistry.C` first writes a 50-row
installed-PYTHIA comparison. `tools/pdg_2025_species_audit.py` then compares
that CSV and `config/heavy_flavour_species_v1.json` with the curated,
per-signed-species official-source extract in
`config/pdg_2025_species_reference_v1.json`.

The two official PDG 2025 source snapshots are not committed. Their immutable
bindings are:

| Official source | SHA-256 |
|---|---|
| `https://pdg.lbl.gov/2025/api/pdg-2025-v0.2.3.sqlite` | `4f1ecd7d9a55bc05f61618cc4574053c1edc6188fab07bb4bb7ebed69f9ec6d3` |
| `https://pdg.lbl.gov/2025/mcdata/mass_width_2025.txt` | `24df41d7db48d8be875dbc8f69aab95fdf26a0512cd8c033cef2d73cc92c24ef` |

After downloading those exact files to a read-only location, reproduce and
byte-check the committed extraction without rewriting it:

```bash
python3 tools/pdg_2025_species_audit.py extract \
  --sqlite /absolute/path/to/pdg-2025-v0.2.3.sqlite \
  --mass-width /absolute/path/to/mass_width_2025.txt \
  --registry config/heavy_flavour_species_v1.json \
  --output config/pdg_2025_species_reference_v1.json \
  --check
```

The command verifies both source checksums, reruns the exact SQL and
fixed-width extraction recorded in the reference, and must print
`PDG_REFERENCE_OK state=NEEDS_PHYSICS_REVIEW signed_species=50`.

The canonical command is the Gate-A command above. For a standalone audit in
the supported Nikhef ROOT/PYTHIA environment, run:

```bash
mkdir -p /tmp/hf-pdg-audit-aclic
root -l -b -q -e \
  'gSystem->SetBuildDir("/tmp/hf-pdg-audit-aclic", kTRUE); int s=gROOT->LoadMacro("Validation/AuditSpeciesRegistry.C+"); if (s<0) gSystem->Exit(100); Long_t a=gROOT->ProcessLine("AuditSpeciesRegistry(\"/tmp/hf-pdg-audit-pythia.csv\")"); gSystem->Exit((int)a);'

python3 tools/pdg_2025_species_audit.py check \
  --registry config/heavy_flavour_species_v1.json \
  --reference config/pdg_2025_species_reference_v1.json \
  --pythia-csv /tmp/hf-pdg-audit-pythia.csv \
  --require-pythia \
  --output /tmp/hf-pdg-audit.json
```

The second command must exit 2, not 0: its report state is
`NEEDS_PHYSICS_REVIEW`, `publication_gate_a_pass=false`,
`owner_signoff_present=false`, and it contains no technical failures. The
curated evidence has 44 `CORROBORATED` signed entries and six review-blocked
entries: `+/-5212`, `+/-5312`, and `+/-5322`. Sigma-b-zero has an official
MCID but no measured PDG 2025 mass; Xi-prime-b-minus is measured but its
operational `5312` is not an official MCID; Xi-prime-b-zero has neither an
official `5322` MCID nor a directly listed measured state/mass.

This audit did not change `config/heavy_flavour_species_v1.json` and is not a
physics decision. No physics-review signoff exists. A reviewer must explicitly
decide and document the operational treatment and corresponding paper
wording before Gate A can return PASS or production can be authorized.

For iterative diagnostics only:

```bash
./run_publication_gate_a.sh \
  Production/validation/development/gate_a --development
```

Development evidence is permanently noncanonical and cannot authorize a
launch.

## 6. Gate B: nine deterministic pilots

Gate B is intentionally blocked while
`config/pthat_sensitivity_v1.json` has
`scientific_review_status=PENDING_GATE_B_OWNER_REVIEW`. Its numerical
equivalence margins and aggregate family diagnostic were introduced by the
publication-readiness implementation, not inherited from Paul or the paper.
Before generating or submitting any pilot, a named project owner or
designated physics/statistics reviewer must review the exact pre-data
specification and, in a reviewed commit, set:

```text
scientific_review_status = APPROVED_GATE_B_OWNER_REVIEW
scientific_review.decision = APPROVE_PTHAT_SENSITIVITY_SPEC
scientific_review.reviewer_role =
  project_owner_or_designated_physics_statistics_reviewer
scientific_review.reviewer = <real name>
scientific_review.decision_utc = <timezone-aware UTC timestamp>
scientific_review.rationale = <scientific rationale>
```

The evaluator and campaign tooling reject the checked-in pending state,
placeholder identities, and future/naive timestamps. The resulting file
SHA-256 is bound into the immutable pilot campaign. Never approve or widen
criteria after observing pilots.

Each tune has three exact profiles:

| logical ID | pTHatMin | successful events | purpose |
|---:|---:|---:|---|
| 0 | 1.0 GeV | 1,000,000 | central/resource pilot |
| 1 | 0.5 GeV | 100,000 | sensitivity low |
| 2 | 2.0 GeV | 100,000 | sensitivity high |

Use a globally unused campaign name, ordinal, and seed interval. The
historical audit reserves ordinals through 25 and seeds through the v7 range;
after rebuilding and checking the shared registry, the planned next values
are ordinal 26 and seed base 270000001:

```bash
python3 tools/generate_gate_b_pilots.py \
  --campaign HF_GATEB_primaryGround_pilot_v8 \
  --campaign-ordinal 26 \
  --seed-base 270000001

python3 tools/campaign_manifest.py validate \
  campaigns/HF_GATEB_primaryGround_pilot_v8
```

If the registry already contains another claim by then, stop and allocate new
values; never reuse or edit the example.

Render first:

```bash
./submit_gate_b_pilots.sh \
  campaigns/HF_GATEB_primaryGround_pilot_v8 --dry-run
```

Inspect the exact nine queue rows, settings hashes, job categories, requested
resources, log paths, and seed allocations. Then, from a Stoomboot submit
host:

```bash
./submit_gate_b_pilots.sh \
  campaigns/HF_GATEB_primaryGround_pilot_v8 --submit
```

The submit operation creates an immutable local submission claim, an
append-only global claim, and a scheduler record. Do not release a held job
that may have started; its seed is consumed.

Every promoted raw file must have an immutable
`hf_raw_validation_receipt_v1`. Validation checks raw-v5 schema, exact
successful-event accounting, event IDs, stability v2, settings v2, origin v4,
full heavy content, weights, multiplicities, process channels, resource
metadata, compression, and overflow accounting.

Evaluate the frozen pTHat decision:

```bash
python3 tools/evaluate_pthat_sensitivity.py \
  campaigns/HF_GATEB_primaryGround_pilot_v8 \
  Production/HF_GATEB_primaryGround_pilot_v8 \
  Production/HF_GATEB_primaryGround_pilot_v8/pthat
```

Exit meanings are:

- 0: `PASS`;
- 2: technical failure;
- 3: inconclusive;
- 4: scientific review required.

The command extracts all nine raw-v5 pilots, uses ten
`event_id % 10` blocks, and applies the frozen
`config/pthat_sensitivity_v1.json` familywise decision. Never edit the decision
after observing results.

Aggregate Gate B:

```bash
./run_publication_gate_b.sh \
  campaigns/HF_GATEB_primaryGround_pilot_v8 \
  Production/HF_GATEB_primaryGround_pilot_v8 \
  Production/HF_GATEB_primaryGround_pilot_v8/pthat/pthat_sensitivity_decision.json \
  Production/HF_GATEB_primaryGround_pilot_v8/gate_b
```

Exit meanings are 0 `PASS`, 2 `FAIL`, and 3 `NEEDS_SIGNOFF`. The immutable
`hf_publication_gate_b_report_v1` recomputes the raw-to-pTHat decision,
cross-tune setting audit, origin audit, trigger-resolution counts, and
resource/storage projections. It does not grant physics approval.

The autonomous target is zero unresolved trigger candidates. If any are
nonzero, stop. A project owner must review their tune/species/kinematic
distribution and approve or reject the treatment. A nonzero result requires
a checksum-bound superseding Gate-B PASS before Gate D. An agent must not
author the sign-off or silently convert `NEEDS_SIGNOFF` to `PASS`.

For this route, the owner creates exactly:

```text
campaigns/<GATEB_CAMPAIGN>/GATE_B_PHYSICS_SIGNOFF.json
```

It is a read-only regular file with schema
`hf_gate_b_physics_signoff_v1`, `approved=true`,
`reviewer_role="project owner"`, a real reviewer, a non-placeholder finding
of at least 20 characters, and an explicitly UTC `decision_utc`. It binds the
original report's campaign, ordinal, commit, SHA-256, exact
`reviewed_unresolved_trigger_candidates` nine-sample table, and exact total.
It also declares `supersedes_state=NEEDS_SIGNOFF` and the only accepted
treatment:

```text
Exclude unresolved triggers centrally; retain unresolved associates as a reported origin category
```

The project owner authors and seals this file; the coding agent only verifies
it. First run the read-only validation:

```bash
./resolve_publication_gate_b_signoff.sh --verify-only \
  Production/<GATEB_CAMPAIGN>/gate_b/gate_b_report.json \
  campaigns/<GATEB_CAMPAIGN>/GATE_B_PHYSICS_SIGNOFF.json
```

Then create a new output directory; never reuse or nest it below the original
immutable Gate-B tree:

```bash
./resolve_publication_gate_b_signoff.sh \
  Production/<GATEB_CAMPAIGN>/gate_b/gate_b_report.json \
  campaigns/<GATEB_CAMPAIGN>/GATE_B_PHYSICS_SIGNOFF.json \
  Production/<GATEB_CAMPAIGN>/gate_b_resolved
```

The resolver permits only the narrowly defined scientific-review state:
nonzero unresolved-origin counts, no technical or pTHat blocker, and no
resolved-observable pTHat shift. It rechecks all nine raw files and their
immutable evidence, keeps the original report intact, and emits a separate
read-only `hf_publication_gate_b_report_v1` with
`resolution_kind=owner_physics_signoff_supersession_v1`. Use that report for
Gate D and later authorization. A technical failure, inconclusive pTHat
decision, or other physics shift cannot be waived by this file.

## 7. Gate C: failure and workflow validation

From the same clean release commit:

```bash
mkdir -p Production/validation/<COMMIT>
./run_publication_gate_c.sh \
  Production/validation/<COMMIT>/gate_c
```

The immutable `hf_publication_gate_c_report_v1` proves all ten required
workflow properties, including:

- forced failure and emulated eviction do not promote partials;
- corrupt/nonempty stable output is rejected;
- retry keeps logical ID but uses a new attempt and seed;
- exactly 100/200/200 candidate rows render;
- deterministic 300-row canonical selection and reserve substitution;
- global seed and event-ID collision checks;
- primary/reserve failure-bias diagnostics;
- status analysis, merge, ten blocks, and plotting select the same manifest
  and reject an extra reserve.

`--development` always produces `FAIL`, even if its diagnostic commands pass.

## 8. Gate D: end-to-end pilot analysis and human review

Gate D uses the three one-million-event central Gate-B pilots. It creates one
central analysis and ten disjoint `unsigned_event_id_modulo_v1` analyses per
tune, each with all 300 signed pair files:

```bash
./run_publication_gate_d.sh prepare \
  Production/HF_GATEB_primaryGround_pilot_v8/gate_d_analysis \
  --campaign-dir campaigns/HF_GATEB_primaryGround_pilot_v8 \
  --production-root Production/HF_GATEB_primaryGround_pilot_v8 \
  --gate-b-report \
Production/HF_GATEB_primaryGround_pilot_v8/gate_b/gate_b_report.json
```

`prepare` verifies:

- 900 central and 9,000 block pair files;
- Paul's `summed MULTIPLICITY`, `hTrKinematics`, `hAsKinematics`, and
  `hCorrelations` compatibility objects;
- object and associate-origin closure;
- no implicit upper-pT/multiplicity selection;
- corrected `BzeroSigmabzero.root` with trigger PDG 511;
- all-primary-heavy closure;
- ten-block union, SEM, nonlinear ratios, covariance, and independent-tune
  propagation;
- a representative smoke subset with ten finite block estimates;
- a full-paper-config exhaustive audit and rendered PDF pages;
- one sidecar per PDF/PNG/ROOT macro plus a run receipt that inventories the
  `multiplicity_boundary_receipt_v1.json`, all 900 central and each of the ten
  900-file block input digests, exact pilot manifest, analysis/plot commit,
  command, timestamp, and output hashes (all explicitly pilot-only and
  `publication_eligible=false`);
- measured storage projection and the final capacity-recheck contract.

The exhaustive pilot audit is stored as
`hf_gate_d_exhaustive_subsample_audit_v1`. Exit 2 is accepted only when its
state is exactly `PILOT_INSUFFICIENT_FOR_FULL_PAPER` with
`publication_promotion_allowed=false`: that is a sizing result from the
one-million-event pilots, not a Gate-D technical failure or paper-coverage
PASS. Representative smoke points must still pass. Any other audit failure
fails Gate D.

Preparation cannot certify human review. A physics reviewer must create a
checksum-bound `hf_gate_d_legacy_comparison_v1` report that records the old
dataset/manifests, comparison rows, and all expected correction categories:
heavy stabilization, hard-origin matching, signed species, role-dependent
thresholds, charge-resolved ordered pairs, and removal of 0.5.

A human visual reviewer must inspect every rendered page and create a
checksum-bound `hf_gate_d_visual_review_v1` report. It must explicitly check
finite visible error bars, tune-ratio styles, legends, multiplicity order,
clipping, and empty pads. Reviewer names and UTC timestamps must be real.

Finalize:

```bash
./run_publication_gate_d.sh finalize \
  Production/HF_GATEB_primaryGround_pilot_v8/gate_d_final \
  --analysis-root \
Production/HF_GATEB_primaryGround_pilot_v8/gate_d_analysis \
  --campaign-dir campaigns/HF_GATEB_primaryGround_pilot_v8 \
  --legacy-comparison-report <LEGACY_COMPARISON.json> \
  --visual-review-report <VISUAL_REVIEW.json>
```

Only `finalize` can emit the canonical
`hf_publication_gate_d_report_v1`. Do not claim Gate D from preparation,
development output, a screenshot, or an unchecked PDF inventory.

### Gate-D storage authorization

Preparation also constructs `hf_gate_d_storage_projection_v1` from measured
Gate-B raw bytes and measured Gate-D pair/plot outputs. It accounts for:

- all 100/200/200 candidate raw outputs;
- one additional complete simultaneous-partial raw footprint;
- 300 canonical per-job analysis directories;
- the merged central output;
- all ten merged file blocks;
- full plots, logs, validation, and evidence, with a minimum 10 GiB
  publication-output allowance.

Capacity comes from `os.statvfs(...).f_bavail`, not nominal free blocks or an
old `df` transcript. Production and analysis paths are grouped by actual
device so the requirement is not double-counted when they share a
filesystem. Every filesystem passes only if:

```text
required additional bytes <= 70% of currently available bytes
projected remaining bytes >= max(5% of filesystem capacity, 500 GiB)
```

Gate-D `finalize` rebuilds the projection from immutable measurements and
performs a fresh capacity check. A canonical report must retain both a passing
`preparation_capacity_check` and a passing `final_capacity_recheck`, with
`state=PASS` and `gate_e_storage_authorized=true`. The full-production
authorization validator checks the schema, component arithmetic, policy, both
capacity snapshots, and the Gate-D PASS semantics. If capacity changes enough
to fail between preparation and finalization, stop and resolve storage
without deleting immutable evidence or narrowing the science output.

## 9. Gate E launch authorization

The already-created historical `HF_100M_primaryGround_ccbb_v1` campaign name,
ordinal, and seed interval are immutable and cannot be regenerated under new
code. Choose a new campaign name and globally unused reservation:

```bash
python3 tools/campaign_manifest.py generate \
  --campaign <NEW_FULL_CAMPAIGN> \
  --campaign-ordinal <UNUSED_ORDINAL> \
  --events 1000000 \
  --seed-base <UNUSED_SEED_BASE> \
  --max-attempts 1000

python3 tools/campaign_manifest.py validate \
  campaigns/<NEW_FULL_CAMPAIGN>
```

Generation creates exactly 500 candidates:

- MONASH IDs 000--099: 100 primary;
- JUNCTIONS IDs 000--099 primary and 100--199 reserve;
- CLOSEPACKING IDs 000--099 primary and 100--199 reserve.

Two distinct owner-created files are mandatory:

1. `campaigns/<NEW_FULL_CAMPAIGN>/PHYSICS_ORIGIN_SIGNOFF.json` binds the
   campaign, commit, measured trigger-origin finding, and decision. Its schema
   is `hf_full_production_origin_signoff_v1`; it requires
   `decision=APPROVE_FULL_PRODUCTION`, `approved=true`,
   `reviewer_role=project_owner`, a real reviewer and UTC decision time, the
   exact Gate-B report path/SHA-256/campaign/ordinal, and the complete
   nine-sample tune/threshold-by-sector unresolved table and total. With zero
   unresolved, `allowed_unresolved_treatment` is exactly
   `No unresolved trigger candidates were observed; no special treatment is
   required.` With nonzero unresolved it is exactly
   `Exclude unresolved triggers centrally; retain unresolved associates as a
   reported origin category` and must bind the superseding Gate-B PASS. Seal
   the file as a single-link mode-`0444` regular file; do not use a
   placeholder identity.
2. `campaigns/<NEW_FULL_CAMPAIGN>/FULL_PRODUCTION_GATE_AUTHORIZATION.json`
   uses schema `hf_full_production_gate_authorization_v1`, identifies the real
   project owner and an explicitly UTC, non-future approval time, hashes the
   origin decision, and binds exactly the canonical Gate A, Gate B, pTHat,
   Gate C, and Gate D reports. Seal it as a single-link mode-`0444` regular
   file. Its Gate-D binding is not valid unless the finalized storage
   projection described above passes.

All reports must be canonical PASS artifacts from the exact campaign commit,
with intact logs/checksums. A checksum of a FAIL report is not authorization.
The coding agent must not create either owner approval.

Dry-run and inspect:

```bash
./submit_full_production.sh \
  campaigns/<NEW_FULL_CAMPAIGN> --dry-run
```

Only after the project owner explicitly authorizes Gate E, storage headroom is
verified, and the two files above validate:

```bash
./submit_full_production.sh \
  campaigns/<NEW_FULL_CAMPAIGN> --submit
```

Submission creates immutable local/global claims before `condor_submit`.
Canonical raw data land under:

```text
Production/<NEW_FULL_CAMPAIGN>/raw/MONASH/
Production/<NEW_FULL_CAMPAIGN>/raw/JUNCTIONS/
Production/<NEW_FULL_CAMPAIGN>/raw/CLOSEPACKING/
```

## 10. Failure, retry, and recovery

Do not release or blindly resubmit a held/evicted job. First establish whether
the attempt started. A retry requires producer/validation failure evidence or
an explicit scheduler-loss authorization.

Allocate append-only:

```bash
python3 tools/campaign_manifest.py allocate-retry \
  campaigns/<NEW_FULL_CAMPAIGN> TUNE LOGICAL_ID \
  --reason "reviewed technical failure"
```

For a scheduler record that was lost, use the command's
`--scheduler-loss-approval` option with a real approval file. Never fabricate
it.

Render the already allocated retry:

```bash
./submit_full_retry.sh \
  campaigns/<NEW_FULL_CAMPAIGN> TUNE LOGICAL_ID ATTEMPT --dry-run
```

Then submit from Stoomboot:

```bash
./submit_full_retry.sh \
  campaigns/<NEW_FULL_CAMPAIGN> TUNE LOGICAL_ID ATTEMPT --submit
```

The retry uses the same logical ID, a new attempt and seed, a unique partial
path, and a new immutable claim/record. Invalid partials are retained for
audit or quarantined; a valid stable output is never overwritten.

## 11. Freeze/seal the 100-file first stage or a superseding equal-tune final sample

Validity and reserve selection may inspect only technical evidence. Prefer
valid primary IDs. Replace missing invalid primaries with the lowest valid
reserve under the predeclared rule. Never inspect a physics observable to
choose a reserve.

Freeze:

```bash
python3 tools/canonical_manifest.py freeze \
  campaigns/<NEW_FULL_CAMPAIGN> \
  Production/<NEW_FULL_CAMPAIGN> \
  Production/<NEW_FULL_CAMPAIGN>/freeze \
  --verify-checksums
```

If substitutions are required, use a separately reviewed selection JSON with
`--selection`. Freeze output is not yet sealed. Run the ROOT-level canonical
manifest validator, which creates the validation receipt and seal:

```bash
./Validation/validate_canonical_manifest.sh \
  Production/<NEW_FULL_CAMPAIGN>/freeze \
  Production/<NEW_FULL_CAMPAIGN> \
  Production/<NEW_FULL_CAMPAIGN>/validation/canonical_raw.log

python3 tools/canonical_manifest.py validate \
  Production/<NEW_FULL_CAMPAIGN>/freeze
```

The first-stage sealed contract is:

- `hf_canonical_raw_manifest_v2`;
- `hf_canonical_freeze_summary_v3`;
- `hf_canonical_raw_validation_receipt_v2`;
- `hf_canonical_freeze_seal_v2`;
- exactly 300 rows and unique seeds;
- exactly 100,000,000 successful events per tune;
- ten deterministic `canonical_slot % 10` file manifests, each with ten
  files per tune;
- block union exactly equal to the central manifest.

If the coverage/precision matrix requires a superseding expansion, its final
sealed contract keeps three equal tune subsets with `N >= 100`,
`N % 10 == 0`, `3*N` total rows, and `N/10` files per tune in each of the ten
blocks. All final consumers derive `N` from the sealed summary/manifest.
Do not confuse that variable raw exposure with the fixed registry of 300
signed pair output files.

### Executable equal-tune expansion procedure

An expansion is a new immutable campaign, not a continuation of, mutation of,
or extra directory scan beside the first-stage freeze. Let `P` be the sealed
parent exposure per tune, choose an additional `A` from
`10, 20, ..., 100`, and set `N=P+A`. The technical candidate allocation is
`A` MONASH, `2A` JUNCTIONS, and `2A` CLOSEPACKING; only an equal accepted
subset of `A` files per tune enters the extension. Failed MONASH jobs must be
retried under the append-only retry contract. JUNCTIONS and CLOSEPACKING may
use their lowest technically valid reserves. Physics values must not be used
to select files.

Before generation, preserve the sealed parent unchanged and produce:

- `hf_final_coverage_precision_report_v1`, with
  `state=EXPANSION_REQUIRED`, `publication_promotion_allowed=false`, the
  exact parent canonical-manifest SHA-256, a nonempty list of failing
  predeclared observables, and
  `selection_rule=predeclared_coverage_and_precision_only_v1`;
- a fresh `hf_equal_tune_expansion_storage_projection_v1` PASS for the named
  child campaign, exact parent hash, `A`, `N`, `A/2A/2A` candidate counts,
  positive projected additional bytes, and a passing final capacity recheck.

Generate both artifacts from the sealed parent, the frozen predeclared
specification, the complete final matrix, the child campaign definition, and
measured storage inputs:

```bash
python3 tools/generate_expansion_evidence.py coverage \
  Production/<PARENT_CAMPAIGN>/freeze \
  config/<FROZEN_COVERAGE_SPEC>.json \
  <FINAL_COVERAGE_PRECISION_MATRIX>.json \
  <COVERAGE_PRECISION_REPORT>.json

python3 tools/generate_expansion_evidence.py storage \
  campaigns/<NEW_EXPANSION_CAMPAIGN>/campaign.json \
  Production/<PARENT_CAMPAIGN>/freeze \
  Production \
  AnalysisOutput/<PARENT_CAMPAIGN> \
  AnalyzedData \
  /data/alice \
  <EXPANSION_STORAGE_PROJECTION>.json
```

`tools/generate_expansion_evidence.py` revalidates the sealed parent, derives
the coverage decision and byte projection, writes each artifact once, and
fails closed on incomplete or mismatched evidence. It does not authorize an
expansion. Do not hand-author either machine artifact or proceed by satisfying
only the validator's JSON shape; a separate real-owner expansion
authorization must bind the passing outputs.

Generate from a clean committed checkout, using an unused campaign name,
ordinal, seed range, and output namespace:

```bash
python3 tools/campaign_manifest.py generate-expansion \
  --root "$PWD" \
  --campaign <NEW_EXPANSION_CAMPAIGN> \
  --campaign-ordinal <UNUSED_ORDINAL> \
  --seed-base <UNUSED_SEED_BASE> \
  --parent-freeze Production/<PARENT_CAMPAIGN>/freeze \
  --additional-jobs-per-tune <A>

python3 tools/campaign_manifest.py validate \
  campaigns/<NEW_EXPANSION_CAMPAIGN>
```

The generator revalidates the sealed parent and binds its campaign, ordinal,
manifest, summary, and seal hashes. It rejects an unequal scope, an `A` not
divisible by ten, and attempt-zero seed reuse. The shared submission registry
still provides the cross-checkout, all-attempt seed-range check.

The project owner must then author a new, single-link, mode-`0444`
`campaigns/<NEW_EXPANSION_CAMPAIGN>/EQUAL_TUNE_EXPANSION_AUTHORIZATION.json`
with schema `hf_equal_tune_expansion_authorization_v1`. It must bind the real
owner identity and UTC decision, rationale, child campaign/ordinal/commit,
all three tunes, exact `A` and `N`, `A/2A/2A` candidate counts, campaign and
candidate-manifest hashes, reserved seed intervals, the byte length and
SHA-256 of the immutable initial-allocation prefix of the append-only seed
ledger, the full parent identity, and the exact coverage and storage artifacts
above. Validation recomputes that prefix and permits only structurally valid,
append-ordered retry rows after it; a valid retry therefore cannot invalidate
the owner's earlier decision.
This decision is distinct from Gate E and cannot be inferred or authored by
an agent. The child also requires its own campaign-bound origin sign-off and
`FULL_PRODUCTION_GATE_AUTHORIZATION.json`; the parent's Gate-E authorization
cannot be copied or reused. Submission requires all three owner decisions:

```bash
./submit_full_production.sh \
  campaigns/<NEW_EXPANSION_CAMPAIGN> --dry-run

./submit_full_production.sh \
  campaigns/<NEW_EXPANSION_CAMPAIGN> --submit
```

After all selected extension outputs and their immutable receipts pass,
freeze and seal the extension separately:

```bash
python3 tools/canonical_manifest.py freeze \
  campaigns/<NEW_EXPANSION_CAMPAIGN> \
  Production/<NEW_EXPANSION_CAMPAIGN> \
  Production/<NEW_EXPANSION_CAMPAIGN>/extension_freeze \
  --verify-checksums

./Validation/validate_canonical_manifest.sh \
  Production/<NEW_EXPANSION_CAMPAIGN>/extension_freeze \
  Production/<NEW_EXPANSION_CAMPAIGN> \
  Production/<NEW_EXPANSION_CAMPAIGN>/validation/extension_canonical_raw.log
```

Create a new final union; never alter or replace the parent freeze:

```bash
python3 tools/canonical_manifest.py supersede \
  Production/<PARENT_CAMPAIGN>/freeze \
  Production/<NEW_EXPANSION_CAMPAIGN>/extension_freeze \
  Production \
  Production/<NEW_EXPANSION_CAMPAIGN>/freeze

./Validation/validate_canonical_manifest.sh \
  Production/<NEW_EXPANSION_CAMPAIGN>/freeze \
  Production \
  Production/<NEW_EXPANSION_CAMPAIGN>/validation/superseding_canonical_raw.log

python3 tools/canonical_manifest.py validate \
  Production/<NEW_EXPANSION_CAMPAIGN>/freeze
```

The superseding command re-hashes every parent and extension raw/evidence
file, rejects reused seeds, raw paths, attempt receipts, or event-ID
namespaces, records every immutable source freeze, and derives new final
slots and `canonical_slot % 10` blocks across the complete `P+A` union. For a
superseding manifest, downstream commands receive `Production` as their
production root because rows carry their source-campaign prefix. Re-run the
entire canonical analysis, merge, robustness, plotting, coverage, and paper
workflow from this final union. Never concatenate old and new block errors or
combine stage-level uncertainties. Further expansion repeats this procedure
with the latest sealed superseding freeze as the parent.

The seal also binds the origin decision, full launch authorization, shared
registry baseline, global claim, scheduler record, attempt claims, and raw
validation receipts.

## 12. One-pass canonical analysis and merging

Dry-run and inspect the exact sealed `3*N` queued paths (300 in the first
stage). Set `<FINAL_FREEZE>` to
`Production/<FINAL_CAMPAIGN>/freeze`. Set `<PRODUCTION_ROOT>` to
`Production/<FINAL_CAMPAIGN>` for a first-stage freeze, but to the collection
root `Production` for a superseding union whose rows carry source-campaign
prefixes:

```bash
./submit_status_analysis.sh \
  <FINAL_FREEZE> \
  <PRODUCTION_ROOT> \
  AnalysisOutput/<FINAL_CAMPAIGN> \
  --dry-run
```

Submit from Stoomboot:

```bash
./submit_status_analysis.sh \
  <FINAL_FREEZE> \
  <PRODUCTION_ROOT> \
  AnalysisOutput/<FINAL_CAMPAIGN> \
  --submit
```

Each canonical queue row also carries the exact
`hf_raw_validation_receipt_v1` path and SHA-256 from the sealed manifest.
Before histogram filling, the worker verifies that receipt and its log against
the unchanged raw checksum and campaign/tune/logical identity, then
independently applies `analysis_raw_input_fail_closed_v1`: complete flag,
requested/successful/tree-entry equality, attempts = successes + failures,
all zero-required producer invariant counters, exact consumed branch types,
per-event invariant flags, finite weights/kinematics, vector cardinality, and
weight-sum closure. A PASS receipt is evidence, not a substitute for this
in-process check.

Each raw file is then scanned once and produces all 300 pair files. Per-job
staging is promoted only after pair-directory validation. The sidecar
`hf_analysis_job_metadata_v3` records the receipt path/SHA-256 and
`immutable_receipt_plus_direct_preflight_v1`. Gate-B/Gate-D diagnostics that
do not consume a sealed canonical manifest record
`direct_preflight_only_v1` and null receipt fields; they remain
nonpublication diagnostics. An existing result is reused only if its pair
inventory, clean log, v3 metadata, raw/receipt hashes, implementation, event
filter, and manifest identity all still agree.

Validate the complete set:

```bash
python3 tools/validate_analysis_outputs.py \
  <FINAL_FREEZE>/canonical_manifest.jsonl \
  AnalysisOutput/<FINAL_CAMPAIGN> \
  --production-root <PRODUCTION_ROOT> \
  --checkout "$PWD" \
  --report \
AnalysisOutput/<FINAL_CAMPAIGN>/validation/analysis_outputs.json
```

Merge the central `N` files/tune and ten frozen `N/10`-file/tune blocks. Note
the required `PRODUCTION_ROOT` argument:

```bash
./merge_root_files.sh \
  <FINAL_FREEZE> \
  <PRODUCTION_ROOT> \
  AnalysisOutput/<FINAL_CAMPAIGN> \
  AnalyzedData \
  <OUTPUT_TAG>
```

`make_subsamples.sh` is now only a compatibility entry point to the same
manifest-driven merge:

```bash
./make_subsamples.sh \
  <FINAL_FREEZE> \
  <PRODUCTION_ROOT> \
  AnalysisOutput/<FINAL_CAMPAIGN> \
  AnalyzedData \
  <OUTPUT_TAG>
```

There is no random/bootstrap discovery mode in the publication path. Existing
destinations are validated but never overwritten.

The merge records
`AnalysisOutput/<CAMPAIGN>/validation/canonical_merge_contract.json` and one
`pair_block_closure_<TAG>_<TUNE>.log` per tune. Promotion is incomplete until
`Validation/validate_pair_block_closure.sh` proves all 300 fixed pair
identities across the central directory and ten blocks: five numeric objects
must close in both stored contents and `Sumw2` (1,500 object checks per tune),
the twelve pair metadata fields must agree, and the all-tune source-manifest
plus explicit tune-filter contract must match. The numeric relative tolerance
is `2e-10`.

## 13. Statistical robustness

The central estimator comes from the union, not the mean of block estimates.
For `K` disjoint estimates:

```text
SEM = sqrt(sum((x_k - mean(x))^2) / (K*(K-1)))
```

Subtract OS-minus-SS, integrate yields, and form baryon-to-reference-meson
ratios inside each block. Preserve numerator/denominator covariance within a
tune. Treat tunes as independently generated. Retain negative finite
balancing yields, but fail on zero trigger denominators, zero reference
denominators, NaN, or infinity.

Compare the primary ten-block SEM with the predeclared largest
equal-exposure modulo partition whose divisor of `N` is in `[11,20]`
(falling back to ten) and the manifest-derived `N`-file delete-one robustness
estimators:

```bash
./PlottingScripts/run_paper_plots.sh freeze-boundaries

python3 tools/final_origin_closure.py \
  --canonical-freeze <FINAL_FREEZE> \
  --production-root <PRODUCTION_COLLECTION_ROOT> \
  --output-directory \
AnalysisOutput/<FINAL_CAMPAIGN>/validation/final_origin_closure \
  --checkout "$PWD" \
  --config config/statistical_robustness_v1.json

python3 tools/statistical_robustness.py \
  --config config/statistical_robustness_v1.json \
  --canonical-freeze <FINAL_FREEZE> \
  --per-job-root AnalysisOutput/<FINAL_CAMPAIGN>/per_job \
  --boundary-receipt \
PlottingScripts/Plots/THnSparse/multiplicity_boundary_receipt_v1.json \
  --origin-closure-report \
AnalysisOutput/<FINAL_CAMPAIGN>/validation/final_origin_closure/final_origin_closure_report_v1.json \
  --output-directory \
AnalysisOutput/<FINAL_CAMPAIGN>/validation/statistical_robustness \
  --checkout "$PWD"
```

This check is descriptive and defines no post-hoc pass threshold. Instability
must be reviewed, not hidden. The checked-in fixed-Nch intervals are marked
review-pending because they were not taken from Paul or the paper. Their exact
specification SHA-256 must be accepted by the designated final
physics/statistics reviewer before publication authorization.

## 14. Dataset selection and plotting

Add a new `status: canonical_candidate` dataset to
`config/dataset_selector.json` after freeze, sealing, analysis, and merge
validation. Record campaign, raw schema, selector, manifest, production,
analysis, raw base, complete-root tag, and block base; keep
`publication_eligible=false` and both publication-authorization fields null.
This state breaks the otherwise circular dependency between multiplicity
boundary generation, final origin/robustness evidence, scientific review, and
final publication authorization.

```bash
python3 tools/dataset_selector.py validate
python3 tools/dataset_selector.py show
python3 tools/dataset_selector.py shell
```

The shell form null-safely exports the publication-eligibility flag, canonical
manifest, production root, analysis root, raw base, analyzed-data base,
complete-root tag, and block base. `run_paper_plots.sh` evaluates this single
selection. The checked-in legacy selector is not publication eligible and
canonical targets must refuse it. A `canonical_candidate` may generate only
prepublication validation artifacts, whose provenance is forced to
`publication_eligible=false`; every such artifact must be regenerated after
authorization. In canonical mode, inclusive raw
kinematics reads only sealed manifest membership, verifies each selected
file's size and SHA-256, and does not recursively discover reserves. The
THnSparse input validator and
multiplicity-boundary plot consume the same analyzed-data/tag overrides and
require metadata-v2 selection provenance (or the one exact tagged
metadata-free legacy regression).

The legacy selector remains:

```text
AnalyzedData/complete_root_21_06_2026_<TUNE>
AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_<TUNE>
```

It is regression-only and cannot be relabeled raw-v5.

The full and reduced/smoke paper configs require canonical metadata-v2,
ordered-pair, factor-one inputs. They intentionally fail while the checked-in
legacy selector is active. Use `legacy-regression` only to reproduce/audit
the dated factor-one-half sample; none of its outputs may be promoted.

Validate configs and inputs:

```bash
jq empty \
  PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json \
  PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json

./PlottingScripts/run_paper_plots.sh validate-inputs
./PlottingScripts/run_paper_plots.sh audit-subsamples
```

Run reduced validation before full plotting:

```bash
mkdir -p logs
VERBOSE=true ./PlottingScripts/run_paper_plots.sh smoke \
  2>&1 | tee logs/final_paper_plots_smoke.log

VERBOSE=true ./PlottingScripts/run_paper_plots.sh thnsparse \
  2>&1 | tee logs/final_paper_plots_thnsparse.log

./PlottingScripts/run_paper_plots.sh multiplicity-spectrum
./PlottingScripts/run_paper_plots.sh all
```

`all` and `smoke` first run their matching standalone boundary-freeze entry
point, then THnSparse and the standalone multiplicity plot. The freeze writes
the checksum-bound `multiplicity_boundary_receipt_v1.json`; every later
consumer reopens the exact central histogram and recomputes all thresholds,
achieved fractions, and exhaustive/disjoint class ranges. Its discrete
classes use boundary lines at `threshold+0.5` and assign the next
higher-activity class from `threshold+1`. A multi-class selection such as
0--10% is validated as the exact union of 0--1% and 1--10%.

The reduced `smoke`/`quick` target deliberately omits the full
300-million-event inclusive raw-kinematics scan. Execute `kinematic-spectra`
explicitly, or through `all`, only after smoke passes.

Each output-producing runner stage also invokes
`tools/final_plot_provenance.py`. Promotion requires a complete
PDF/PNG/ROOT-macro triplet and one adjacent provenance sidecar per file. The
shared run receipt binds the exact output and input hashes, current plotting
commit/tree, merged analysis commit, configuration payload/hash, cut and
schema versions, command/target, UTC timestamp, sealed canonical manifest,
all ten deterministic block manifests, and
`multiplicity_boundary_receipt_v1.json`. Canonical pair mode verifies each
configured ROOT file against its merged checksum inventory and copied source
manifest; canonical raw mode re-hashes every manifest-selected raw file.

Before paper promotion, verify each proposed artifact:

```bash
python3 tools/final_plot_provenance.py verify \
  --checkout "$PWD" \
  --sidecar PlottingScripts/Plots/THnSparse/<plot>_PDF.pdf.provenance.json
```

A missing/tampered input, output, manifest, block, boundary receipt, or
sidecar is fatal. Gate-D smoke products use the same contract but are
explicitly marked as ineligible one-million-event pilot artifacts. The
legacy-regression receipt likewise sets `publication_eligible=false` and
records that canonical central/block manifests do not exist.

Both checked-in configs use `calculate_errors=true` and ten blocks. Smoke is
reduced scope, not no-error. For pair-analysis metadata v2, the pT/eta
selection is validated as upstream and not re-applied. The exact metadata-free
`complete_root_21_06_2026` tag alone may use legacy plot recuts. Mixed or
partial metadata, inconsistent thresholds, and upper-pT selections fail.

Validate every verbose statistic:

```bash
./PlottingScripts/validate_subsample_log.py \
  logs/final_paper_plots_thnsparse.log \
  --json-output \
  PlottingScripts/validation/final_thnsparse_uncertainty_validation.json
```

Every final point requires ten finite estimates and a positive SEM unless a
documented deterministic identity proves degeneracy. No placeholder `1e-10`,
zero-error substitution, missing object, or silent denominator failure is
allowed.

Generated outputs live in ignored directories under
`PlottingScripts/Plots/`. Do not commit bulk regenerated PDF, PNG, or ROOT
macros. Promote a paper copy only after numerical provenance and full rendered
visual review.

### Final dataset promotion (human decisions)

After the ineligible candidate plots, final origin closure, statistical
robustness report, species disposition, and paper-claim scope have been
independently reviewed:

1. Copy
   `docs/templates/FINAL_SCIENTIFIC_REVIEW.template.json` to the final
   campaign evidence directory. Replace every angle-bracketed value, remove
   `_template_notice`, bind the exact statistical-specification SHA-256,
   compute `payload_sha256` over all other fields as sorted compact JSON, and
   make the completed file single-link mode `0444`.
2. The project owner separately completes
   `docs/templates/PUBLICATION_DATASET_AUTHORIZATION.template.json`, removes
   `_template_notice`, binds every exact final evidence file, computes its
   payload hash, and makes it single-link mode `0444`.
3. Change the selector row from `canonical_candidate` to `canonical`, set
   `publication_eligible=true`, and record the checkout-relative
   authorization path and file SHA-256.
4. Run `python3 tools/dataset_selector.py validate --checkout "$PWD"`.
   A Boolean alone, a writable/template review, an extra field, a changed
   report, empty closure evidence, or a different campaign/commit/sample is
   rejected.
5. Delete no candidate evidence. Regenerate `smoke`, `thnsparse`,
   `multiplicity-spectrum`, and `all`; only these post-authorization,
   tracked-clean receipts may be promoted.

A coding agent may validate these files but must never fill in either human
approval.

## 15. Final coverage, paper, and release archive

One hundred million successful events per tune is the minimum equal-statistics
stage, not guaranteed coverage. Before promoting paper results, build the
full matrix over tune, signed trigger, associate, multiplicity, and derived
ratio. Every final canvas point needs ten finite block estimates and must pass
the predeclared precision rule. If coverage fails, either:

1. run a new immutable equal-tune expansion and recompute everything; or
2. obtain a pre-result physics decision to revise scope.

Never add statistics only to a tune/species/bin or turn an undefined ratio
into zero.

Archive:

- exact code commit and clean-state evidence;
- cards, generated registries, allowlist, and environment versions;
- campaign/seed ledger, shared registry baseline/global claims, scheduler
  records, origin decision, and launch authorization;
- every attempt/start/submission/raw-validation receipt;
- canonical manifest, ten block manifests, receipt, and seal;
- effective settings and heavy-stability audits;
- analysis and merged-directory manifests/checksums;
- complete Gate A--D reports and logs;
- pTHat and statistical-robustness reports;
- machine-readable results and figure/table provenance;
- final plotting configs, verbose logs, plots, rendered-page review, and paper
  build log.

All paper `includegraphics` entries must map to a generator, command, config,
central and block manifests, generated output, copied paper path, and checksum.
The paper and `REPOSITORY_FILE_CATALOG.md` are finalized only after the code,
production, analysis, and figures stop changing.

## 16. What is not publication evidence

The following do not pass a gate:

- a dirty or `--development` report;
- a historical raw-v3/v4 pilot;
- a checksummed FAIL or `NEEDS_SIGNOFF` report;
- a user-created JSON with no semantic/log validation;
- a nonempty ROOT file without its receipt;
- a Condor queue reaching zero;
- 500 submitted jobs described as 500M analyzed events;
- an unreviewed Gate-D preparation;
- a smoke-only plot;
- the legacy `21_06_2026` full-config failure;
- an agent-authored physics sign-off or launch authorization.
