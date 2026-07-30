# Pre-production gate report — 2026-07-30

Status: **not authorized for the 300M canonical submission**.

This report records evidence gathered on the isolated `full-production`
branch and isolated Nikhef worktrees. It is not a final publication report.
Canonical `/data/alice/ipardoza/Hadronization`, the separate deterministic-seed
feature checkout, the dirty local bibliography, and the untracked paper draft
were not modified.

## Source state

- verified baseline: `origin/main` at `11884cf1` when the isolated branch was
  created;
- Paul-compatible plotting hardening ancestor: `d8de9b6`;
- first corrected pilot implementation: `9a8e92b`;
- clean Gate A validation commit: `738df28`;
- local implementation worktree:
  `/private/tmp/hadronization-full-production`;
- Nikhef diagnostic/development checkout:
  `/data/alice/ipardoza/Hadronization-full-production`;
- clean v5 pilot checkout:
  `/data/alice/ipardoza/Hadronization-full-production-run-v5`.
- event-unique origin implementation: `c9c24a9`;
- schema-aware pilot-manifest implementation: `3efde0f`;
- clean final pilot checkout:
  `/data/alice/ipardoza/Hadronization-full-production-run-v7`.

## Gate A

Result: **pass at commit `738df28`; rerun only if implementation code changes**.

Evidence on Nikhef:

- `ValidationReports/GateA_20260730/producer_forced_build.log`;
- `ValidationReports/GateA_20260730/compile_and_unit.log`;
- `ValidationReports/GateA/species_registry_pythia_audit.csv`;
- `ValidationReports/HF_DEV_settings_20260730x/effective_tune_differences.csv`;
- clean final-commit transcript:
  `/data/alice/ipardoza/Hadronization-full-production-validate-v6/ValidationReports/GateA_20260730_final/compile_and_unit_738df28.log`.

Observed environment:

- ROOT 6.30/01 ALICE build;
- PYTHIA 8.315;
- 50 signed ground-state registry entries;
- 300 signed ordered pair definitions;
- effective tune audit: 46 compared settings, 29 differences, consisting of
  28 allowlisted tune-bundle differences plus the per-job random seed;
- no project-source compiler warning; external ROOT/PYTHIA headers emit
  conversion warnings under the intentionally strict flags.
- final producer SHA-256:
  `05aa60ab23b638286169ee16272f29aa193500fffed4d5b1c53d007da4e8853e`.

Tests passed:

- species and pair artifact determinism;
- exact trigger/associate and multiplicity pT/eta boundaries;
- event-ID collision toy;
- OS/SS ordered-pair and baryon/reference-meson toy identities;
- tune-card allowlist;
- submit rendering, including quoted `JobCategory` and separate Condor
  environment variables;
- synthetic plotting projection: one selected numerator entry and one matching
  trigger denominator;
- optional mini-pad null safety;
- pair-directory object, overflow, integral, and inclusive/by-origin closure.

All 15 ROOT validation, analysis, merge, and plotting macros loaded or
compiled successfully in a clean detached worktree. The transcript was
explicitly scanned for `fatal error`, `Error in <ACLiC>`, undefined
references, segmentation faults, and cling JIT failures. This scan was added
after ROOT returned status zero for an earlier ACLiC header failure.

Repository accountability is recorded in `REPOSITORY_FILE_CATALOG.md`, which
is generated and checked by `tools/generate_file_catalog.py`. At this report
revision it contains exactly one row for each of 673 tracked paths:
32 authoritative, 52 support, 456 generated, and 133 legacy. Every
authoritative row names a validation path, and the mechanical coverage check
passes. The protected untracked paper tree and stale raw-v2 campaign material
are called out separately rather than silently included in the canonical
pipeline.

The implementation delta at `c9c24a9` was compiled in clean worktree
`/data/alice/ipardoza/Hadronization-full-production-validate-v7`.
`ValidationReports/GateA_20260730_event_unique/compile_and_unit_c9c24a9.log`
records a successful producer build, successful `ValidateRawOutput.C` ACLiC
load, and
`HARD_CARRIER_UNIQUENESS_TEST_PASS conflict_groups=1 demoted_matches=2`.

## Gate B

Result: **in progress and not yet passed**.

Earlier 1,000-success raw-v3 diagnostics, after correcting the trigger audit
to the publication trigger registry, found:

| Tune | publication trigger candidates | unresolved | fraction |
|---|---:|---:|---:|
| MONASH | 544 | 0 | 0 |
| JUNCTIONS | 470 | 6 | 0.012765957 |
| CLOSEPACKING | 450 | 4 | 0.008888889 |

All ten unresolved cases were charm triggers with
`MatchResolution::kAmbiguous`. Exact candidates were inspected with
`Validation/ListUnresolvedOrigins.C`. The validated pilot goal is zero. If a
statistically adequate final pilot still has a nonzero fraction, the project
owner must explicitly approve the exclusion of unresolved triggers from the
central sample while retaining unresolved associates as an origin category.
`submit_full_production.sh --submit` enforces that decision with
`PHYSICS_ORIGIN_SIGNOFF.json`.

The larger v5 sensitivity pilots confirm that this is a physical
event-record ambiguity, not a missing object. For example, JUNCTIONS local
success 59 in the `pTHatMin=0.5` sample (process code 121,
`pTHat=2.8624 GeV`) contains accepted D+ and D*+ states with the same explicit
fragmentation mother range 712--718. That range contains two same-sign charm
carriers, indices 715 and 716, whose ancestry traces respectively to the
selected hard charm and a shower charm. There is no unique event-record
assignment of either hadron to one carrier. The conservative matcher therefore
returns `kAmbiguous` rather than choosing a convenient lineage. Since the
observed ambiguity fraction is tune dependent, excluding these triggers may
bias a tune comparison and must not be silently accepted.

They also exposed a separate event-level defect. Five of the six one-pass
sensitivity analyses aborted on their hard-carrier uniqueness invariant:
MONASH low-pThat had 1 conflicting ordered pair, JUNCTIONS low/high had 17/19,
and CLOSEPACKING low/high had 10/32. Only MONASH high-pThat had zero. In
CLOSEPACKING low-pThat event 13615, final D0 and D+ both have mother range
916--918, containing the same selected hard charm at index 918; in event
15614, final anti-Sigma_c++ and D- both have mother range 119--120, containing
the same selected hard anticharm at index 120. The old matcher called each
per-hadron walk unique but did not enforce uniqueness across the event.

Commit `c9c24a9` adds the missing event-level constraint. Every final
open-heavy claim in a duplicate group is conservatively demoted to unresolved
with `MatchResolution::kDuplicateHardCarrier`; the original conflicting hard
index and aggregate group/demotion counts remain auditable. The one-pass
analysis keeps its fatal same-carrier invariant, so a producer or validator
regression still stops the reduction.

Submission history:

- v2 never reached Condor because `+JobCategory` was unquoted;
- v3 cluster `5200389` held before generation because two environment
  assignments were joined with a semicolon; its nine attempt-0 seeds are
  permanently consumed and must not be reused or released;
- v4 never reached Condor because the login-node batch environment lacked
  PYTHIA;
- v5 cluster `5200390` was submitted from Stoomboot with nine fresh seeds and
  separate environment variables: one 1,000,000-success central job plus
  100,000-success `pTHatMin=0.5` and `2.0` jobs for each tune.
- v6 was generated before the event-unique implementation and was never
  submitted. Its ordinal and seeds remain reserved and will not be reused.
- v7 was generated at `3efde0f` with ordinal 25 and fresh seed interval
  beginning at 260000001. Its nine-job schema, hashes, origin algorithm, exact
  implementation commit, and seed ledger validated before dry-run and
  submission to cluster `5200393`.

The clean v5 producer was built with GCC 14.2, ROOT 6.30/01 and PYTHIA 8.315;
its SHA-256 was
`4ec3818f9ac698eb3f526793df794d2b871ec713c21cd464d16da510b9872184`.
The v5 run is diagnostic because the later weak-parent-registry commit changes
the strong/EM cross-check definition. A fresh-seed final pilot from the final
implementation commit is required before Gate B can pass.

## Gate C

Result: **pass; rerun final smoke at the release commit**.

Demonstrated:

- forced producer failure does not promote a partial file;
- interrupted/aborted attempt does not promote;
- corrupt stable output is rejected and not overwritten;
- a retry requires a new ledger seed;
- a valid stable output is reused only after validation;
- unauthorized seed/attempt is rejected;
- synthetic canonical freeze has exactly 300 unique rows and seeds;
- each of ten blocks has ten jobs per tune;
- block union equals the central manifest;
- 100M successful events per tune are represented;
- a 500-candidate 100/200/200 submit render is deterministic.

## Gate D

Result: **not complete**.

The one-pass analysis and pair-directory validator have passed on development
raw-v3 input, but Gate D still requires a final-commit pilot to complete:

1. exhaustive raw validation for all three tunes;
2. origin, stability, multiplicity, process, settings, runtime and storage
   reports;
3. pTHat sensitivity comparison;
4. one-pass analysis of the validated pilots;
5. central/block merge and provenance validation;
6. reduced THnSparse smoke with finite block SEM;
7. one raw-event-to-final-bin trace;
8. final-commit macro compilation and visual inspection.

## Correctness defects found and resolved

1. Origin audits originally counted every stored heavy species as a trigger;
   publication triggers now come from the pair registry.
2. The plotting correlation numerator did not apply configured pT/eta cuts
   while the trigger denominator did. Both now use identical initialized cuts.
3. Several plotting cut fields were uninitialized. All are initialized, and
   unsupported individual phi cuts fail explicitly.
4. The legacy same-sign factor 0.5 is incorrect for the new ordered-pair
   estimator. Canonical configs use 1.0.
5. Pair validation did not prove origin-component closure or all-axis overflow
   safety. It now does.
6. Condor `JobCategory` needed quoting.
7. Condor environment assignments needed spaces, not a semicolon.
8. Non-interactive Nikhef login shells could lose PYTHIA when `alienv` Tcl
   initialization failed. A pinned CVMFS fallback and ABI-compatible GCC 14.2
   runtime were added.
9. Generic `root-config --libs` introduced unrelated Arrow linkage. The
   producer now links only Tree, Hist, RIO, and Core.
10. The strong/EM multiplicity cross-check lacked a machine-readable weak
    parent table and omitted the neutral-kaon flavour state. The new registry
    is generated into the C++ build and unit tested.
11. Production and analysis formerly depended on directory discovery. The
    canonical path now uses immutable candidate, seed, freeze and block
    manifests only.
12. Plot inputs lacked a single dataset switch. `config/dataset_selector.json`
    now labels the old dataset as regression-only and controls raw, central and
    block roots.
13. Independent origin walks could assign one hard carrier to several final
    hadrons sharing a PYTHIA string/junction mother range. An event-level
    uniqueness post-pass now demotes every conflicting claim to an auditable
    unresolved subtype, and raw validation proves no duplicate survives.
14. The campaign validator assumed every manifest was a 500-candidate
    production and rejected nine-job Gate-B manifests. Validation is now
    schema-aware and additionally rejects a pilot generated from a different
    implementation commit or physics-contract hash.

## Blocking decisions and work

- Complete and exhaustively validate final fresh-seed v7 pilots from
  `3efde0f`, including event-unique demotion counts, runtime, and pTHat
  evidence.
- Obtain explicit project-owner origin sign-off if the final unresolved
  trigger fraction is nonzero.
- Only then create and submit the immutable 300M campaign.
- The paper figures and prose cannot be finalized until the canonical freeze,
  ten-block analysis, strict uncertainty audit, figure provenance map, and
  five independent reviews are complete.

No production-scale submission is authorized by this report.
