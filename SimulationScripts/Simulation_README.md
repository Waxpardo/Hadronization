# Simulation scripts

This directory contains the PYTHIA 8 producers, three combined-heavy tune
cards, generated physics registries, and build rules. The publication producer
is `heavyflavourcorrelations_status.cpp`. Split bbbar/ccbar and broad-qq
producers are retained only for historical regression.

The complete operational sequence is in
[`../REPRODUCIBILITY.md`](../REPRODUCIBILITY.md).

## Build

The supported Nikhef environment is ROOT 6.30/01 and PYTHIA 8.315:

```bash
cd /data/alice/ipardoza/Hadronization-full-production-run-<N>
source setupEnv.sh
python3 tests/test_pythia_runtime_contract.py
./tools/build_producer.sh "$PWD"
```

The runtime test requires `PYTHIA8DATA` to contain the pinned
`share/Pythia8/xmldoc/Index.xml` and instantiates `Pythia8::Pythia`; a linked
library without its matching XML data is not a valid environment.

The maintained Makefile can also be used after the environment is loaded:

```bash
make -C SimulationScripts
```

`tools/build_producer.sh` is preferred for gates because it records the exact
component build and avoids unrelated ROOT libraries. A canonical producer
must be built from a tracked-clean checkout and its executable SHA-256 is
bound into the campaign submit.

Generated headers are checked, not hand edited:

```bash
python3 tools/generate_registry_artifacts.py --check
```

They are derived from:

```text
config/heavy_flavour_species_v1.json
config/heavy_flavour_pair_registry_v1.json
config/weak_decay_parent_registry_v1.json
config/tune_difference_allowlist_v1.json
```

The filename of the allowlist is retained for compatibility; its internal
schema is `pythia_tune_difference_allowlist_v2`.

## Independent PDG species audit

The central registry is now checked independently against official PDG 2025
data as well as the installed PYTHIA ParticleData table. The committed
`../config/pdg_2025_species_reference_v1.json` is a complete 50-signed-entry
curated extract produced by `../tools/pdg_2025_species_audit.py`. Its official
inputs are deliberately not committed:

| Official source | SHA-256 |
|---|---|
| `https://pdg.lbl.gov/2025/api/pdg-2025-v0.2.3.sqlite` | `4f1ecd7d9a55bc05f61618cc4574053c1edc6188fab07bb4bb7ebed69f9ec6d3` |
| `https://pdg.lbl.gov/2025/mcdata/mass_width_2025.txt` | `24df41d7db48d8be875dbc8f69aab95fdf26a0512cd8c033cef2d73cc92c24ef` |

Verify the committed extract from those exact downloaded snapshots:

```bash
python3 tools/pdg_2025_species_audit.py extract \
  --sqlite /absolute/path/to/pdg-2025-v0.2.3.sqlite \
  --mass-width /absolute/path/to/mass_width_2025.txt \
  --registry config/heavy_flavour_species_v1.json \
  --output config/pdg_2025_species_reference_v1.json \
  --check
```

Run the installed-PYTHIA and official-source comparison in one immutable
evidence directory with:

```bash
./run_publication_gate_a.sh Production/validation/<COMMIT>/gate_a
```

Gate A compiles and runs `../Validation/AuditSpeciesRegistry.C`, writes
`species_registry_pythia_audit.csv`, and then runs:

```bash
python3 tools/pdg_2025_species_audit.py check \
  --registry config/heavy_flavour_species_v1.json \
  --reference config/pdg_2025_species_reference_v1.json \
  --pythia-csv Production/validation/<COMMIT>/gate_a/species_registry_pythia_audit.csv \
  --require-pythia \
  --output Production/validation/<COMMIT>/gate_a/species_registry_pdg_audit.json
```

The current expected exit status is 2 and the state is
`NEEDS_PHYSICS_REVIEW`, not PASS. Forty-four signed entries are corroborated;
six (`+/-5212`, `+/-5312`, `+/-5322`) remain review-blocked. This is a
successful mechanical audit with no technical failure, but it is not a
physics signoff. The audit made no change to
`../config/heavy_flavour_species_v1.json`, and no registry-treatment signoff
exists. Production stays blocked until a physics reviewer records that
decision.

## Publication producer interface

The executable accepts exactly:

```text
heavyflavourcorrelations_status \
  MODE OUTPUT SEED CAMPAIGN CAMPAIGN_ORDINAL LOGICAL_ID ROLE ATTEMPT
```

- `MODE`: `monash`, `junctions`, or `closepacking`;
- `SEED`: exact integer in the verified PYTHIA range 1--900000000;
- `ROLE`: `primary`, `reserve`, or `pilot`;
- `ATTEMPT`: append-only attempt number.

A small direct development example is:

```bash
./SimulationScripts/heavyflavourcorrelations_status \
  monash /tmp/hf_dev.root 123456789 HF_DEV 65000 0 pilot 0
```

The number of successful events comes from the selected card. Direct commands
do not create campaign, submission, attempt, or validation receipts and are
therefore never publication inputs. Canonical runs are rendered from an
immutable manifest and executed through `../runCondorJob.sh --campaign`.

The producer opens the output with ROOT `CREATE` and refuses an existing path.
The worker writes an attempt-unique partial, validates it, and atomically
promotes it only after success.

## Fixed producer contracts

| Contract | Value |
|---|---|
| raw schema | `hf_primary_ground_raw_v5` |
| selector | `hard_trigger_primary_ground__primary_ground_associate_v1` |
| origin algorithm | `signed_heavy_constituent_complete_mothers_unique_v4` |
| heavy-stability audit | `heavy_stability_audit_v2` |
| effective settings | `effective_pythia_settings_exhaustive_v2` |
| tune allowlist | `pythia_tune_difference_allowlist_v2` |
| all-primary-heavy match | `primary_all_heavy_constituent_match_v1` |
| central multiplicity | `NCH_PRIMARY_CHARGED_ETA10_V1` |
| cross-check multiplicity | `NCH_PRIMARY_CHARGED_ETA40_V1` |
| weak-transition rule | `weak_decay_transition_pythia_status_v1` |

The job metadata stores the schema/algorithm/checksum identities. A validator
must reject a missing, old, or inconsistent contract rather than guessing
compatibility.

## Common generation definition

All three combined cards use:

- pp at 14 TeV;
- `Tune:pp = 14`;
- `HardQCD:hardccbar = on`;
- `HardQCD:hardbbbar = on`;
- central `PhaseSpace:pTHatMin = 1.0 GeV`;
- identical beam, process, event-accounting, stability, multiplicity, and
  seed policies.

The cards are:

```text
pythiasettings_Hard_Low_ccbb_MONASH.cmnd
pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd
pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd
```

The mixed configuration allows both hard channels; it does not imply that
each selected event contains both a hard ccbar and hard bbbar subprocess.
The hard process code and channel are stored per event and audited.

MONASH, JUNCTIONS, and CLOSEPACKING are full configuration bundles. The
producer records every effective PYTHIA setting after initialization in an
exhaustive canonical snapshot. Gate B compares the aligned snapshots and
allows differences only in the generated v2 allowlist. Do not attribute a
tune difference to a single switch when several effective parameters differ.

The pTHat sensitivity samples use 0.5, 1.0, and 2.0 GeV only through an
immutable Gate-B manifest. The frozen decision in
`../config/pthat_sensitivity_v1.json` determines whether the 1.0 GeV central
definition is accepted, inconclusive, or requires scientific review.

## Heavy stability

After reading the tune card and before `pythia.init()`, the producer scans the
PYTHIA ParticleData table and disables decay for every recognized
charm/beauty hadron:

- particle and antiparticle;
- open and hidden heavy flavour;
- ground, vector, excited, and multiply heavy states;
- Bc and states outside the central registry.

It does not disable all hadron decays. The intended unrelated light-decay
policy remains active.

The `heavy_stability_audit` tree and canonical serialized object record signed
PDG ID, name, hadron/meson/baryon classification, spin, charge, heavy
constituents, open/hidden category, central-registry membership, antiparticle
checks, mass/lifetime, and original/final decay flags. Metadata stores the
v2 schema and SHA-256. Initialization or raw validation fails if a recognized
heavy hadron remains decay-enabled.

## Raw-v5 event and particle content

The `tree` has one entry for every successful event, including empty-heavy
events. Important event fields include:

- collision-unique `event_id`;
- local successful-event index;
- process code and hard-flavour channel;
- event weight, pTHat, hard scales, and MPI count;
- selected outgoing/final-copy hard-heavy indices and four-vectors;
- `multiplicity_hadronisation_v1`;
- `multiplicity_final_strong_em_v1`;
- per-species multiplicity audit counts;
- heavy/origin/conservation diagnostics.

The particle vectors retain recognized charm- and beauty-containing hadrons
with integer PDG/status/index/charge fields, four-vectors, lifecycle flags,
complete mother information, signed constituent counts, net charm/beauty,
state category, origin, resolution, matched/rejected hard carrier, and
central-registry membership. `heavyBaryonNumber` stores the physical integer
baryon number exactly (`0` for mesons, `+1` for baryons, `-1` for
antibaryons), not PYTHIA's three-times-baryon-number type code. Bc retains both
charm and beauty content.

Compatibility branches such as `ID`, `PT`, `ETA`, `PHI`, `STATUS`, and
`MULTIPLICITY` remain available, but consumers must validate `raw_schema`
before assigning their historical meaning. In raw-v5, `ID`, `STATUS`,
`MOTHER`, and `MOTHERID` are integer vectors; their older floating-point
encoding belongs only to legacy schemas and must not be inferred from the
branch name.

## Origin matching and uniqueness

The v4 algorithm:

1. identifies the selected outgoing hard c/cbar or b/bbar;
2. follows complete mother lists and copy chains for the corresponding signed
   constituent;
3. classifies selected hard, shower, MPI, other resolved, or unresolved;
4. enforces event-global uniqueness of the selected hard carrier;
5. rejects a single carrier assignment for multi-heavy same-sector content.

The deterministic traversal is implemented by the generator-independent
`MatchHeavyOriginGraph` helper. Gate-A unit fixtures cover status-23 hard-copy
chains, shower and MPI sources, junction/diquark mother ranges, equal-depth
ambiguity, duplicate ancestry endpoints, sector-specific Bc matching, and
charm produced below a beauty lineage. The producer adapter supplies PYTHIA's
expanded and deduplicated mother lists; the raw validator retains a separate
reconstruction rather than trusting the stored match.

When multiple final hadrons claim one selected hard carrier, every claim is
demoted to unresolved with
`MatchResolution::kDuplicateHardCarrier`. The algorithm never chooses a
hadron by iteration order, species, tune, or pT. The rejected/conflicting
index and group/demotion counters remain auditable.

`primary_all_heavy_match` supplies a validation-only constituent-level
closure diagnostic. It includes central and noncentral heavy states. Carrier
uniqueness is enforced between distinct final parent hadrons: repeated
constituent rows within one multiply-heavy parent do not conflict with one
another, while all claims from distinct conflicting parents are demoted. It is
not a second central selector.

Unresolved candidates cannot be central triggers. Direct-primary,
ground-state associates remain in the inclusive associate population with
their unresolved category. Gate B requires zero unresolved trigger candidates
for autonomous PASS; a nonzero result needs an explicit owner decision and
superseding PASS before production.

## Multiplicity

`NCH_PRIMARY_CHARGED_ETA10_V1` counts every final, charged, non-heavy-flavour
particle with:

- `pT > 0.15 GeV/c`;
- `|eta| <= 1.0`.

`NCH_PRIMARY_CHARGED_ETA40_V1` is identical except `|eta| <= 4.0`.

Charge and heavy content come from PYTHIA ParticleData, not from a hand-written
species list, so Sigma+-, Xi- and Omega- are counted as the conventional
primary-charged definition requires. PYTHIA status is not used: with
`ParticleDecays:limitTau0 = on` and `tau0Max = 0.01` mm every weakly decaying
light hadron stays final, so `isFinal()` already means "primary". No light
hadron has `0.01 mm < c*tau0 < 10 mm`, so this is exactly equivalent to the
conventional 1 cm/c threshold; `Validation/TestPrimaryChargedDefinition.C`
proves that against the installed ParticleData and recounts both windows from
live events.

Charm and beauty hadrons are excluded: their decays are disabled, so they are
final only as an artefact of the production policy, and counting them would
correlate the event-activity classifier with the observable it classifies.

A six-bucket species breakdown (e, mu, pi, K, p, other charged) is stored for
the central window so the composition can be audited.

## Successful-event and resource accounting

The event loop targets successful events. It records 64-bit attempts,
successes, failures, entries, process counts, weight sums, and cross-section
information. The invariant is:

```text
attempts = successful_events + failed_attempts
tree_entries = successful_events = requested_successes
```

The attempt ceiling is bounded. Failure injection and early abort are
pilot-only. A canonical one-million-event logical output must have exactly
1,000,000 successes.

Job metadata also records elapsed time, peak RSS, output size/compression,
host, commit/dirty state, executable/config checksums, campaign/role/attempt,
seed, ROOT/PYTHIA versions, and Condor identifiers. Gate B uses the central
million-event jobs to project both the 300-file canonical set and all 500
candidates.

## Validation

Publication raw validation is:

```bash
./Validation/validate_raw_output.sh \
  <RAW_ROOT> <CAMPAIGN> <TUNE> <LOGICAL_ID> <REQUESTED_SUCCESSES> \
  <ATTEMPT> <SEED> <ROLE> <CAMPAIGN_ORDINAL> <PTHAT_MIN> \
  <AUDIT_EVENTS> <CONFIG_SHA256> <EXECUTABLE_SHA256> <REPOSITORY_COMMIT>
```

Canonical workers provide the exact full argument contract and create the
immutable `hf_raw_validation_receipt_v1`; do not improvise a receipt from a
manual run. Additional audit macros under `../Validation/` inspect stability,
effective tune settings, origin resolution, unresolved candidates, hard
carrier uniqueness, pTHat sensitivity, and raw object/types.

## Legacy sources

The following are not publication producers:

- `bbbarcorrelations_status*.cpp`;
- `ccbarcorrelations_status*.cpp`;
- `qqbarcorrelations_status.cpp`;
- split/broad-QCD `.cmnd` files;
- `run_hf.sh`;
- `Batching_MONASH.sh`;
- `Makefile.old` and historical binaries.

They are retained to reproduce old samples and compare expected changes.
Their schemas, hand-written decay lists, seed modifiers, process definitions,
and output branches must not be relabeled raw-v5 or merged into a canonical
campaign.
