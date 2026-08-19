# Final coding-agent instructions: publication-ready heavy-flavour balancing analysis

These instructions supersede the earlier large-statistics instructions. They
incorporate the repository, Nikhef, paper, production, subsample, plotting,
and thesis audits and the subsequent physics decisions. Follow them as a
specification, not as suggestions.

The thesis is legacy motivation and a regression reference. It is not
authoritative. The paper is an improved study and must use the definitions
below consistently in production, analysis, figures, captions, and prose.

The latest stable `main` containing Paul Veen's merged THnSparse work is the
closest existing implementation of the complete paper pipeline. It is the
executable baseline, not disposable legacy code. When documentation, naming,
or an unimplemented proposal is ambiguous, preserve Paul's behavior. Deviate
only when a reproducible test establishes a physics, statistical,
methodological, or software-correctness defect, or when the project owner
approves a newly stated scientific definition. Keep a runnable compatibility
mode and quantify the effect of every approved numerical change.

## 1. Non-negotiable scientific definition

The study compares the MONASH, JUNCTIONS, and CLOSEPACKING PYTHIA
configurations at generator level. It asks how the signed charm and beauty
quantum numbers of a selected hard subprocess are distributed among heavy
hadrons made directly in hadronisation.

The central trigger objects are:

- directly produced heavy hadrons, identified by positive PYTHIA
  hadronisation status 81--89;
- matched to the selected hard-process heavy quark of the relevant flavour and
  sign;
- members of the versioned ground-state registry in Section 4;
- final in the event because every heavy-hadron decay has been disabled;
- within the role-dependent kinematic acceptance;
- charge resolved: particles and antiparticles are never averaged in central
  results.

The central associate objects obey the same direct-primary, ground-state,
generator-stability, acceptance, and charge-resolution requirements, but they
are not required to match the selected hard pair. They include resolved hard,
shower, MPI, other, and unresolved origins. This is necessary for the
trigger-conditioned OS/SS balancing construction used by the repository:
same-sign associates arise from additional heavy-flavour production and would
be removed by requiring both particles to match the single selected hard
quark-antiquark pair.

The authoritative central analysis mode is:

`hard_trigger_primary_ground__primary_ground_associate_v1`

Use the following terminology everywhere:

- **direct primary**: created directly by hadronisation, with positive status
  81--89;
- **hard origin**: the relevant heavy constituent is ancestry-matched to the
  selected hard-subprocess quark or antiquark; this is required for central
  triggers and retained as an associate-origin category;
- **ground state**: membership in the explicit operational registry below;
- **generator-stable**: final only because its PYTHIA decay was disabled;
- **open heavy flavour**: nonzero signed net charm and/or beauty;
- **hidden heavy flavour**: contains a heavy quark-antiquark pair but has zero
  net heavy flavour.

Do not use `prompt` as a synonym for status 81--89, direct primary, hard
origin, or generator-stable. If the paper uses `prompt`, define it in the
conventional decay-inclusive sense and state that it is not the central
observable here.

This is a model-level primary-hadron observable. It is not an experimental,
decay-inclusive ground-state yield. The paper must say so.

## 2. Worktree, branch, and source-of-truth safety

Perform all implementation on a dedicated branch created from the latest
verified stable `origin/main`, named:

`full-production`

If that branch already exists, inspect its ancestry and worktree before
deciding whether to continue it or create a dated successor. Never recreate
it destructively. This unprefixed name is intentional: the project owner
explicitly requested `full-production`, overriding the default Codex branch
prefix.

Before editing:

1. Fetch the live remote.
2. Record the hashes of local `main`, live `origin/main`, Nikhef `main`, and
   every branch or worktree relevant to production or final plotting.
3. Inspect existing local and remote `full-production` branches and any dated
   successors.
4. Create a separate clean worktree from the latest verified `origin/main`.
5. Inspect `codex/final-paper-plotting-20260729` (audited at `7f17356`) or its
   merged successor. Port only its still-unmerged validated plotting,
   validation, provenance, portability, and generated-artifact changes. Do not
   duplicate them if they have already reached `main`.
6. Record the starting commit, every integrated source commit, and the
   provenance of the working paper copied into that worktree.

The existing local `main`, uncommitted bibliography and paper files,
final-paper plotting branch/worktree, completed 100M files, analyzed ROOT
files, and plots are read-only inputs. Do not reset, clean, overwrite, or move
them.

The current working draft may be untracked in the local worktree. If so, copy
it byte-for-byte into the clean worktree, record its source path and checksum,
and leave the original untouched before making reviewed edits.

Do not assume that a stale `origin/main` value inside the Nikhef clone is the
live remote. Compare actual commit hashes. Do not use the older Nikhef
seed/Condor branch as a source of truth; port only changes that survive the
requirements and tests below.

Before changing code, complete and save a source-of-truth audit covering:

- the entire working paper and bibliography, including Introduction,
  Observables, Model, Results, Summary, every table, figure, and caption;
- the thesis sections that motivated the balancing study, labeled as legacy;
- every repository README and operational document;
- all active and candidate producers and three combined-heavy tune cards;
- correlation, multiplicity, pT, merge, block/subsample, plotting, and
  paper-build code;
- Paul’s merged plotting/configuration work and the protected
  `codex/final-paper-plotting-20260729` branch/worktree;
- current complete-root/smoke configurations;
- legacy 100M files, manifests, logs, recoverable seeds, and ROOT contracts;
- all HTCondor submit, wrapper, retry, and path-update files;
- the installed PYTHIA and ROOT headers/documentation needed for status,
  process, ParticleData, ancestry, decay, weight, and settings semantics;
- local and Nikhef build/runtime environments.

Record the audited commits/checksums, active contracts, contradictions, and
decisions in a versioned pre-edit report. The post-implementation file catalog
in Section 20 is a second audit, not a substitute for this initial one.

Current-state reference from the 2026-07-30 re-audit, to be reverified before
implementation:

- live `origin/main`: `11884cf1`;
- local dirty `main`: `39c9cf22`, fourteen commits behind, with protected
  bibliography and untracked paper work;
- live plotting-hardening branch:
  `codex/final-paper-plotting-20260729` at `7f173565`;
- no live remote `full-production` branch was present at the instant of that
  pre-implementation audit; the branch was subsequently created as required,
  so this bullet is historical source-state evidence, not an instruction to
  recreate it;
- Nikhef `/data/alice/ipardoza/Hadronization`: clean `main` at `11884cf1`,
  while its local `origin/main` reference is stale;
- Nikhef `/data/alice/ipardoza/Hadronization-main`:
  `codex/nikhef-seed-condor-ready-20260724` at `758a5369`.

The `7f17356` changes are plotting, validation, documentation, portability,
and generated-artifact hardening; the active pair-analysis physics code on
`main` remains unchanged. Do not infer that its successful smoke validation
resolved the selector, pair-combinatoric, species, production, or coverage
issues below.

Paul's plotting history includes PRs `#10` (`detailed-changes`) and `#11`
(`before-fixing-subsampling`) and commit
`10a6f098f80730374d9f827bfdf3ae97a928a030` after the subsampling fix. Before
porting or asking Paul to rebase again, run an ancestry check against the
latest stable `main`. The 2026-07-30 audit found `10a6f098` already reachable
from stable `main`; if that remains true, no corrective change belongs on
Paul's old branch. Work from stable `main` and preserve the merged behavior.

### 2.1 Paul-compatibility hierarchy

Paul’s active paper path is the scientific consumer that production and
analysis must serve:

`raw PYTHIA -> status_analysis_THnSparse_qq.C-compatible pair objects -> complete_root -> ten disjoint subsamples -> improvedPlotting_THnSparse.C -> paper`

Preserve these parts unless an executable regression proves they are wrong:

- signed, species-resolved OS and SS pair configurations;
- trigger-conditioned ordered pairs with self-pairs excluded;
- `DeltaPhi` wrapped to `[-pi/2, 3pi/2)`;
- per-trigger normalization followed by OS-minus-SS;
- full-DeltaPhi integrated balancing yields;
- pair filenames and `summed MULTIPLICITY`, `hTrKinematics`,
  `hAsKinematics`, `hCorrelations`, and the versioned
  `hCorrelationsByOrigin` decomposition;
- central values from complete-root inputs and uncertainties from ten disjoint
  partitions of the same canonical files;
- tune-ratio treatment for independent tune samples;
- current tune styles, runner, strict input/coverage validation, portable path
  resolution, provenance, and generated-artifact policy from `7f17356`.

Do not treat every line of the legacy analysis as authoritative. Classify each
disagreement before editing:

1. **Physics/correctness defect**: the code contradicts the declared
   per-trigger observable, selected particle definition, or reproducibility
   contract. Make the smallest tested correction.
2. **Ambiguous convention**: more than one definition could be valid. Write a
   toy test and derivation, compare with the paper and configuration, and do
   not change it until the intended convention is fixed.
3. **Standardization mismatch**: the calculation is valid but names,
   metadata, paths, or configuration do not expose the definition clearly.
   Prefer an adapter, assertion, explicit field, or documentation change over
   rewriting working code.

The currently known classification is:

- commented-out trigger status selection: physics defect; both roles require
  the common direct-primary ground-state base selector;
- no trigger hard-origin match despite hard-origin paper language: physics
  defect; add the trigger-only match while keeping associates inclusive in
  origin;
- associate `pT >= 1 GeV` in the legacy pair producer: approved definition
  change, not evidence that Paul’s old calculation was internally wrong; the
  new associate threshold is `pT > 0.15 GeV`;
- pT/eta fields exist in Paul’s plotting JSON and stable main applies the
  corresponding trigger/associate recuts to `hCorrelations` as well as the
  trigger recuts to `hTrKinematics` (for example
  `improvedPlotting_THnSparse.C` at stable commit `39c9cf2`, lines 409--427 and
  461--474): confirmed behavior, not a missing-cut defect. Preserve that
  exact Paul-compatible projection path in `legacy-regression`. The canonical
  v2 pair-analysis contract applies the approved role-dependent acceptance
  once upstream and records it in metadata; canonical plotting must assert
  the contract and must not recut it. Do not invent a second
  “corrected-consistent legacy” mode: the premise for that distinction was
  disproved by direct source inspection;
- Paul’s THnSparse axes stop at `pT = 50 GeV` and `Nch = 400` while the paper
  declares no such upper selections: potential correctness defect only if
  accepted entries overflow; measure every under/overflow count and change the
  axis/projection policy only if required;
- Paul’s percentile thresholds are integer-bin centers subsequently passed to
  inclusive `SetRangeUser` calls: ambiguity that can assign the boundary Nch
  value to two adjacent classes; the central discrete classes must form an
  exhaustive, non-overlapping partition while retaining Paul’s percentile
  labels and low-to-high plotting order;
- same-sign factor `0.5`: ambiguous in its legacy comment but inconsistent
  with the implemented ordered-pair/per-trigger definition; Section 12
  requires the toy proof and removes it only in the new central mode;
- “baryon/meson ratio” naming: standardization mismatch; Paul’s code forms a
  species balancing yield divided by one configured reference-meson balancing
  yield, not a sum over all baryons divided by all mesons;
- repeated raw scan for every pair: numerically compatible but impractical
  after the required species expansion; optimize to one pass while writing
  byte/number-compatible consumer objects;
- strict ten-partition coverage failures: production/statistics limitation,
  not a plotting defect; never weaken the validator or fabricate errors.

### 2.2 Stable-main baseline and burden of proof

Start all implementation from the latest verified stable `origin/main` that
contains Paul's merged commits. In particular, first verify that Paul's
subsampling, grouped triggers, per-canvas `TriggerToUse`, multiple charm and
beauty triggers, MONASH/JUNCTIONS/CLOSEPACKING handling, config-driven mini
and global canvases, OS/SS yield construction, same-sign handling, combined
yield canvases, and baryon/reference-meson canvases are present. Record the
symbols, configuration fields, and regression artifacts that demonstrate
this. Do not replace that architecture with a parallel pipeline.

Use this authority order when sources disagree:

1. a project-owner-approved and explicitly defined paper observable;
2. a physics/statistical/methodological requirement supported by a derivation,
   primary reference where applicable, and an executable validation;
3. Paul's behavior on stable `main`;
4. current repository documentation and plotting-hardening branches;
5. thesis and older macros, which are regression evidence only.

Items 1 and 2 may override Paul only for the specific proven defect. They do
not authorize opportunistic redesign. For every numerical departure from
Paul, create a compatibility matrix containing:

- Paul's exact behavior and the file/symbol implementing it;
- the conflicting paper statement or correctness invariant;
- classification as demonstrated defect or unresolved convention;
- derivation and a hand-calculable toy test;
- legacy-versus-corrected regression output on the same immutable input;
- affected figures, tables, captions, and conclusions;
- reviewer and project-owner decision where the choice is not uniquely fixed
  by correctness.

An unresolved convention stays in Paul-compatible mode and blocks final
publication promotion. Do not silently select the convention preferred by the
coding agent. Standardization changes must use metadata, validation, adapters,
or documentation whenever they can preserve working numerical behavior.

The plotting-hardening work at `7f17356` is a validated source of portability,
input validation, uncertainty, styling, pointer-safety, provenance, and
generated-artifact fixes. It is not a replacement scientific pipeline and is
not automatically authoritative over later stable-main changes. Port or reuse
each still-needed change individually, with a regression against current
stable `main`.

### 2.3 Known state of the legacy production and plotting workflow

Preserve the following audited facts as regression fixtures, and revalidate
them rather than assuming that directory completeness implies publication
readiness:

- each tune has 56 central pair ROOT files;
- each tune has ten subsample directories with 56 pair ROOT files each;
- each subsample manifest has ten jobs and the ten manifests cover job IDs
  0--99 exactly once;
- the required `summed MULTIPLICITY`, `hTrKinematics`, `hAsKinematics`, and
  `hCorrelations` objects were present with the expected ROOT types;
- 72 representative central-versus-ten-subsample union comparisons agreed
  exactly or within ROOT merging tolerance;
- the strict full-config audit nevertheless reported 610 configured
  observables without ten finite subsample estimates: 540 beauty and 70
  charm, comprising 342 yields and 268 baryon/reference-meson ratios;
- only 468 of 1152 expected final statistical records were emitted with
  `n=10`, and 1,781 zero-trigger-normalization warnings were observed;
- the historical reduced 1--10% legacy-regression selection produced 30 of
  30 records with `n=10` and finite positive SEM values and no missing inputs,
  non-finite values, placeholder errors, or zero-normalization warnings;
- that legacy-regression run proves that error bars work for supported dated
  observables. It does not prove full-paper coverage, and its one-bin global
  yield canvas has empty/clipped pads that must never be promoted as a final
  figure. Canonical `smoke` must refuse the legacy selector;
- 78 tracked generated plotting artifacts were stale. They may remain removed
  from version control and regenerated into ignored/provenance-controlled
  output locations; unrelated paper figures must remain untouched.

The observed legacy coverage pattern included beauty B+ only in the
integrated and 1--10% selections, no complete anti-Lambda_b trigger coverage,
charm D+ from integrated through 1--10% except 0--1%, and Lambda_c in the
integrated, 30--40%, 20--30%, and 1--10% selections. Treat this only as a
regression description of the audited sample, not as an approved final scope.

The current complete-root production is therefore structurally coherent and
valuable for regression, but not statistically sufficient for the full
configured paper scope. Do not silently discard it, silently regenerate it
from a different job set, weaken the validator, replace missing errors with
placeholders, or promote smoke-only plots. Record a non-destructive central
and subsample source manifest before using it for any comparison.

## 3. Scope and change-control rule

Fix only what is needed to make this study correct, reproducible, and
publication ready. Do not add a decay-derived campaign, detector simulation,
new conserved-charge program, or unrelated analysis extension.

Before changing a component:

1. Document its current inputs, outputs, callers, and paper consumers.
2. State the concrete physics, correctness, reproducibility, or scaling defect.
3. Add a regression or toy test where feasible.
4. Make the smallest coherent fix.
5. Verify the supported legacy path when it remains scientifically meaningful.

The default decision for a working file is **no change**. Before implementation
write a change budget listing each proposed file, the exact behavioral defect
or required new contract, why documentation/configuration/adapter-only
resolution is insufficient, and the regression test. Do not touch a file that
has no approved entry. Do not resolve unrelated TODOs, modernize style,
reformat macros, rename internal objects, or consolidate legacy scripts merely
because it would make the repository look cleaner.

Preserve established ROOT object names and pair filenames through a
compatibility writer where possible. Scientific correctness takes priority
over silent compatibility: never preserve a wrong factor, selector, or
normalisation merely because an old plot depended on it.

Do not rewrite the validated plotting infrastructure from `7f17356`. Reuse
its strict file/object checks, ten-subsample coverage audit, SEM calculation,
independent-tune propagation, memory cleanup, path resolution, runner,
provenance, tune styling, and refusal to promote incomplete plots. Modify
Paul’s plotting macro only where a changed scientific contract cannot be
provided upstream or where a proven defect such as the central-mode factor
`0.5` must be corrected. Preserve an exact legacy mode for old results.

Do not restore the stale generated plot files removed and inventoried by that
branch. This does not authorize deleting user plots or untracked paper
figures; it preserves the branch’s deliberate policy that regenerated plot
artifacts are outputs, not source.

## 4. Operational ground-state registry

### 4.1 Uniform rule

For this paper, `ground state` means the lowest-radial (`n=1`), zero-orbital
angular momentum (`L=0`), lowest-spin state for each physically distinct
valence-flavour/light-diquark configuration included in the registry.

Consequences:

- pseudoscalar D, Ds, B, Bs, and Bc mesons are central;
- vector D*, Ds*, B*, Bs*, and Bc* states are not central;
- spin-1/2 Lambda, Sigma, Xi, Xi-prime, and Omega states are central;
- spin-3/2 starred partners are not central;
- Xi and Xi-prime are distinct states and must be stored, analyzed, and
  reported separately;
- every charge state is distinct;
- every antiparticle is distinct;
- there is no spin averaging and no charge-conjugation averaging.

This is an operational paper definition, not a claim that all communities use
the phrase `ground state` identically. State the definition in the paper.

### 4.2 Initial signed-PDG registry

Create one machine-readable, versioned registry and generate or validate all
selectors, pair definitions, labels, and documentation from it. It must
contain the positive and negative signed PDG entries corresponding to:

Charm mesons:

- D0, D+, Ds+ (`421`, `411`, `431`);

Charm baryons:

- Lambda_c+ (`4122`);
- Sigma_c0, Sigma_c+, Sigma_c++ (`4112`, `4212`, `4222`);
- Xi_c0, Xi_c+ (`4132`, `4232`);
- Xi-prime_c0, Xi-prime_c+ (`4312`, `4322`);
- Omega_c0 (`4332`);

Beauty mesons:

- B0, B+, Bs0, Bc+ (`511`, `521`, `531`, `541`);

Beauty baryons:

- Lambda_b0 (`5122`);
- Sigma_b-, Sigma_b0, Sigma_b+ (`5112`, `5212`, `5222`);
- Xi_b-, Xi_b0 (`5132`, `5232`);
- Xi-prime_b-, Xi-prime_b0 (`5312`, `5322`);
- Omega_b- (`5332`).

The numeric table is a required hypothesis to validate, not permission to
trust a hand-written list. Before production, query the installed PYTHIA
ParticleData table and corroborate names, antiparticles, spin type, mass,
charge, hadron type, and quark content against an authoritative PDG source.
Fail if an entry is missing or inconsistent. Do not silently substitute a
starred state, daughter, family sum, or nearby PDG code.

Implementation status (2026-07-30): independent corroboration now exists.
`AuditSpeciesRegistry` writes the installed-PYTHIA comparison, while
`tools/pdg_2025_species_audit.py` and the generated
`config/pdg_2025_species_reference_v1.json` bind the exact official PDG 2025
SQLite and mass/width URLs, their SHA-256 checksums, the extraction SQL, the
fixed-width parse, and all 50 signed per-species comparisons. The result is
44 `CORROBORATED` entries and six `NEEDS_PHYSICS_REVIEW` entries
(`+/-5212`, `+/-5312`, `+/-5322`). The audit exits 2 by design and Gate A
propagates that review-blocked state.

This is not a physics approval. The official 2025 PDG database does not
assign official MCIDs `5312`/`5322`; it does not directly list a measured
Xi-prime-b-zero state/mass, and Sigma-b-zero remains an
unmeasured/model-prediction state. The audit has not changed the operational
registry, and no physics-review signoff exists. Do not describe those entries
as experimentally established PDG states merely because PYTHIA provides
them. Gate A must remain blocked until a reviewer explicitly documents the
operational registry treatment and associated paper wording. The exact
source bindings plus `extract --check` and combined audit commands are in
`REPRODUCIBILITY.md`.

Store all physically distinct Xi states separately. Family-level Xi summaries
may be derived only in addition to the individual results, with their exact
membership printed. Never combine Xi with Xi-prime or particle with
antiparticle invisibly.

### 4.3 Noncentral heavy states

All other recognized charm- or beauty-containing hadrons, including vector,
spin-excited, radial/orbital, hidden-heavy, and multiply heavy states, are
stabilized and retained in raw data for validation. They are not part of the
central registry and must not leak into central denominators or numerators.

Do not implement a decay/feed-down extension in this task. Because the
canonical sample disables heavy decays, feed-down cannot be recovered by an
analysis flag. Document that limitation.

Produce a validation-only `primary_all_heavy` closure diagnostic from the raw
collection. For each tune, sector, hard channel, multiplicity class, and
trigger species, report what fraction of the resolved companion hard flavour
is carried by central ground-state associates versus excluded vectors,
excited states, hidden-heavy states, or other categories. This diagnostic is
not a second central result. It prevents the ground-state-restricted
OS-minus-SS integral from being misrepresented as complete heavy-flavour
closure.

## 5. PYTHIA generation contract

### 5.1 Common event definition

Use one combined heavy-flavour producer and one raw dataset per tune. All
three tune cards must share:

- proton-proton collisions at 13.6 TeV;
- `Tune:pp = 14` as the common base;
- `HardQCD:hardccbar = on`;
- `HardQCD:hardbbbar = on`;
- `PhaseSpace:pTHatMin = 1.0` GeV;
- identical heavy-stability, light-decay, event-accounting, seed, schema,
  origin, and analysis policies.

The mixed sample contains both enabled subprocess classes. A single selected
hard event ordinarily belongs to either a hard-ccbar or hard-bbbar subprocess;
do not describe every event as containing both selected hard pairs.

Verify the actual PYTHIA process-code mapping in the installed version.
Record the hard process code and test the expected charm and beauty channels
(historically 121/122 and 123/124) rather than treating those numbers as
unverified constants.

The noninteractive Nikhef environment must bind both the PYTHIA libraries and
their XML data. When `alienv` falls back to a pinned CVMFS package, export
`PYTHIA8DATA=<PYTHIA8>/share/Pythia8/xmldoc`, require
`xmldoc/Index.xml` to exist, and instantiate PYTHIA in a runtime smoke test.
Setting only `PYTHIA8`, `PATH`, and `LD_LIBRARY_PATH` is insufficient: PYTHIA
8.315 may otherwise abort while resolving a stale build-time `xmldoc` path.

The `pTHatMin` cut regulates and defines the generated hard-heavy sample. It is
not a detector cut and must not be hidden. The paper must report it. Before
full submission, compare otherwise identical pilots at `pTHatMin = 0.5`,
`1.0`, and `2.0` GeV. Generate at least 100,000 successful events per tune and
threshold, and extend the pilots if the inclusive trigger spectra and broad
OS/SS yields do not have enough precision to resolve a material change. If the
central observables change beyond pilot statistical precision, stop for a
scientific decision; do not tune away or conceal the dependence.

### 5.2 Tune fidelity

Treat MONASH, JUNCTIONS, and CLOSEPACKING as three full configuration bundles.
Make a machine-generated table of every effective PYTHIA setting that differs
between them, including fragmentation, MPI, beam remnants, colour
reconnection, junction, and close-packing settings.

Create an allowlist of settings permitted to differ. Compare the post-init
effective settings, not only the text cards. Fail the pilot if a production,
decay, beam, process, acceptance, seed, or accounting setting differs outside
the allowlist.

The paper must not attribute a tune difference uniquely to junctions, close
packing, diquark production, or another single switch when the compared
bundles differ in multiple parameters. Use wording such as “difference between
the full configurations,” followed by physically cautious interpretation.

Verify setting names and capitalization against the installed PYTHIA version;
in particular, do not leave a potentially ignored MPI setting undetected.
Fail on unknown, misspelled, or ignored settings.

### 5.3 Disable every heavy-hadron decay

After reading the tune card and before `pythia.init()`, programmatically set
`mayDecay = false` for every ParticleData entry that is both a hadron and
contains charm and/or beauty. Cover:

- particles and antiparticles;
- open- and hidden-heavy hadrons;
- ground and excited states;
- Bc and multiply heavy states.

Do not rely on the current incomplete card lists. Do not use
`HadronLevel:Decay = off`, because unrelated light decays must remain enabled.

Write a machine-readable stabilization audit with signed PDG ID, name, hadron
classification, quark content, open/hidden classification, spin type, mass,
original and final `mayDecay`, `canDecay`, central-registry membership, and
antiparticle verification. Store its checksum in every output.

Initialization fails if any recognized heavy hadron remains decay-enabled.
Pilots must prove that representative D*, Sigma, Xi/Xi-prime, Omega, B*, Bc,
and hidden-heavy entries remain final when produced, while unrelated light
decays retain their intended policy.

### 5.4 Exact successful-event accounting

Each valid logical output contains exactly 1,000,000 events for which
`pythia.next()` returned true. The loop target is successful events, not
attempts.

Use 64-bit counters and require:

`attempts = successful_events + failed_attempts`

`successful_events = event_tree_entries = 1,000,000`

Fill one event-tree entry for every successful event, including events with no
selected or stored heavy hadron. Use a configurable attempt ceiling and fail
the job if it is exceeded.

Record `pythia.stat()` and cross-section information, but never report
attempted events or submitted capacity as analyzed statistics.

## 6. New coverage-gated equal-statistics campaign

The historical campaign tag `HF_100M_primaryGround_ccbb_v1` has already been
created and reserved. Do not regenerate it, rely on it as a command default,
or overwrite any production carrying that name. For the first immutable
100M-per-tune stage under the corrected implementation, choose a new globally
unused campaign name, campaign ordinal, seed interval, and output namespace
after checking the shared submission registry. Record the chosen values in the
release evidence. The event-count and equal-statistics contract below is
unchanged by using a new tag.

One hundred million successful events per tune is the approved minimum
equal-statistics stage, not an a priori proof of sufficient precision. The
legacy coverage audit already demonstrates that 100M can be inadequate for
rare beauty trigger/multiplicity combinations. Before describing this stage
as the final paper sample, run the exhaustive central-definition coverage
audit in Section 14.

If any predeclared final observable lacks ten finite block estimates or fails
the precision criterion, take one of only two routes:

1. generate additional, unbiased, equal statistics for all three tunes under
   a new immutable campaign/manifest version and rerun all boundaries,
   central values, blocks, and plots from the enlarged union; or
2. obtain an explicit physics decision to reduce or merge the reported
   observable scope, update the configuration and paper before looking at
   tune-dependent conclusions, and label the omitted scope.

Never add events only to a tune, species, multiplicity class, or block because
its measured result is inconvenient. Never reuse the `HF_100M...` tag for an
expanded union. The final event target is coverage and precision driven and
must be equal between tunes; storage and runtime projections must include a
predeclared expansion plan.

### 6.1 Candidate jobs

Prepare exactly these logical candidate slots:

- MONASH: 100 jobs, IDs `000`--`099`;
- JUNCTIONS: 200 jobs, IDs `000`--`199`;
- CLOSEPACKING: 200 jobs, IDs `000`--`199`.

Each logical job targets exactly one million successful events.

For JUNCTIONS and CLOSEPACKING, IDs `000`--`099` are primary and
`100`--`199` are reserve capacity for their higher wall-time/failure rate.
Reserve capacity does not grant additional statistical weight. MONASH uses
its 100 primary slots; failed attempts are retried under the same logical ID.

A retry retains its logical ID but receives a new attempt number and a new
seed. Invalid attempts never enter a canonical manifest. A later valid retry
supersedes the invalid attempt; it does not create a second logical output.

### 6.2 Canonical equal-statistics manifests

For the first stage, freeze exactly 100 validated logical outputs per tune:

- 100,000,000 successful events per tune;
- 300,000,000 successful events total.

For JUNCTIONS and CLOSEPACKING, prefer valid primary IDs and replace missing
primaries with the lowest valid reserve IDs using a deterministic,
predeclared rule. Record every substitution. Once frozen, do not change the
manifest. A statistically required expansion is a new, superseding campaign
and manifest version with a recorded parent, never an in-place edit.

Extra valid reserve outputs remain outside all first-stage central values, multiplicity
boundaries, subsamples, uncertainties, and paper event totals. The paper
reports 100M analyzed events per tune only after the manifests exist. The
100/200/200 submission strategy belongs in operational documentation, not as
if 500M events had been analyzed.

Validity and reserve selection must never inspect a heavy-hadron yield,
correlation, multiplicity distribution, or other paper observable. Audit
whether job failure or wall time correlates with process mix, event rate,
output size, multiplicity diagnostics, or other physics-sensitive quantities.
Compare valid primary and reserve cohorts before freezing. If missingness is
not demonstrably technical and ignorable, increase resources or redesign the
recovery procedure; do not select a convenient 100-file subset.

#### Executable equal-tune expansion

An expansion is a new immutable child campaign, not additional directory
discovery beside the first-stage freeze and not an in-place edit. Let `P` be
the sealed parent exposure per tune, choose an additional `A` that is a
multiple of ten in `[10,100]`, and define `N=P+A`. Generate exactly `A`
MONASH, `2A` JUNCTIONS, and `2A` CLOSEPACKING candidates. Freeze an equal
technically selected extension of `A` files per tune; reserves do not add
statistical weight.

Before the child can be submitted, require all of the following:

- a parent-bound `hf_final_coverage_precision_report_v1` with
  `state=EXPANSION_REQUIRED`, `publication_promotion_allowed=false`, at least
  one failing predeclared observable, and
  `selection_rule=predeclared_coverage_and_precision_only_v1`;
- a fresh child-bound `hf_equal_tune_expansion_storage_projection_v1` with
  `state=PASS`, `gate_e_storage_authorized=true`, the exact parent hash,
  `A`, `N`, `A/2A/2A` candidate counts, positive projected bytes, and a
  passing final capacity recheck;
- a new child-specific `PHYSICS_ORIGIN_SIGNOFF.json`;
- a new child-specific `FULL_PRODUCTION_GATE_AUTHORIZATION.json`; and
- a distinct owner-authored, single-link, mode-`0444`
  `EQUAL_TUNE_EXPANSION_AUTHORIZATION.json` with schema
  `hf_equal_tune_expansion_authorization_v1`, decision
  `APPROVE_EQUAL_TUNE_EXPANSION`, `reviewer_role=project_owner`, a real UTC
  decision, rationale, child campaign/ordinal/commit, exact `A`, `N`,
  candidate and reserved-seed records, immutable parent identity, and
  checksum bindings to the coverage and storage artifacts.

Generate both machine artifacts with
`tools/generate_expansion_evidence.py`; do not hand-author them. Its coverage
path must bind a frozen specification, the complete parent-bound matrix, the
sealed parent, and its own source checksum, and must recompute every
predeclared criterion. Its storage path must inventory every parent raw file
and the complete parent analysis/analyzed-data trees, project the exact
`A/2A/2A` candidate scope, retained retry partials, full superseding derived
outputs and merge staging, add the documented contingency, and probe live
`statvfs` capacity. Authorization validation must recompute those semantics,
verify every bound byte, and perform a fresh live capacity check; a
handwritten look-alike report must fail.

The parent's launch authorizations cannot be copied or reused. A coding agent
may validate all three child owner decisions but must never author them.
Generate, validate, and dry-run the child with:

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
./submit_full_production.sh \
  campaigns/<NEW_EXPANSION_CAMPAIGN> --dry-run
```

After owner authorization, submission, validation, and technical selection,
freeze and seal `Production/<NEW_EXPANSION_CAMPAIGN>/extension_freeze`.
Create the new union with
`tools/canonical_manifest.py supersede`, passing the parent freeze, extension
freeze, the `Production` collection root, and the child `freeze` output. Never
alter the parent. Revalidate and seal the union, rederive all ten blocks over
the complete `P+A` sample, and rerun analysis, merging, robustness, plotting,
coverage, and paper generation. Superseding rows can reference more than one
source campaign, so downstream commands use the production collection root
(`Production`), not only `Production/<NEW_EXPANSION_CAMPAIGN>`. The exact
command sequence is maintained in `REPRODUCIBILITY.md`.

The superseding manifest/summary/seal schemas are first-class downstream
inputs, not an archival annotation. Analysis validation, canonical merging,
raw-inclusive plots, final plot provenance, and every later expansion must
accept both a sealed v2 leaf and a sealed v3 union, verify every leaf
manifest/hash/source campaign, derive the exact final `N`, and support chained
unions without a three-digit slot cap. Superseding promotion is atomic:
failure may leave neither a partial final freeze nor an altered parent.

### 6.3 Seeds

The producer receives one exact seed from the campaign manifest. Remove all
time-, PID-, hostname-, and modulo-based seed modification.

Before submission:

1. Verify the installed PYTHIA seed domain.
2. Reserve a campaign-specific contiguous seed block.
3. Use an injective mapping from `(global candidate ID, attempt slot)` to seed.
4. Give pilots and tests a disjoint reserved range.
5. Preallocate initial seeds in an immutable manifest.
6. Allocate retry seeds centrally and append-only under a file lock or other
   atomic mechanism.

An owner authorization must bind the immutable initial-allocation prefix of
the seed ledger by exact byte count and SHA-256, not the hash of the whole
mutable append-only file. Validation must prove that prefix is unchanged and
that every suffix record is an authorized, injective retry inside the
campaign's reserved intervals. Appending a valid retry must not invalidate
the original owner decision; changing an initial byte or adding an invalid
suffix must.

For the first-stage 100/200/200 campaign, global candidate ordinals are MONASH
`0`--`99`, JUNCTIONS `100`--`299`, and CLOSEPACKING `300`--`499`. An expansion
derives nonoverlapping child-local offsets from its dynamic `A/2A/2A` slot
counts and separately proves that its full reserved seed intervals do not
overlap the sealed parent or shared registry. The maximum attempts per logical
ID must be bounded so the mapping is provably injective and remains within the
verified PYTHIA range.

Never recycle a seed from a failed, killed, abandoned, pilot, or valid
attempt. The final validator compares the allocation ledger, logs, and ROOT
metadata and requires zero duplicates and zero undocumented seeds.

### 6.4 HTCondor and recovery

Use campaign-specific raw, partial, log, manifest, analysis, subsample, plot,
and validation directories. Stable final names are based on tune and logical
ID; attempt-specific files remain traceable.

Write to an attempt-unique partial path. Promote atomically to the stable
logical filename only after full validation. Quarantine, do not overwrite, a
corrupt or mismatched existing file.

Do not skip a job because a file is merely nonempty. Validate it against
Section 15 first.

Benchmark all three tunes at Nikhef. Disable automatic retries. A submission
wrapper may submit a new cluster held, record the immutable scheduler evidence,
and release that never-started cluster once; manually releasing a held or
evicted attempt that may already have started is forbidden. Nonzero exits,
holds, evictions, and wall-time termination require reviewed failure evidence
and an append-only retry allocation with a new seed. Verify actual Nikhef
policy rather than assuming generic HTCondor semantics. A killed partial
output is invalid.

Do not trust only the rendered submit text or terse `condor_submit` output.
Before release, read the held jobs' real ClassAds and require the exact cluster,
complete process set/cardinality, arguments, campaign/logical/attempt identity,
executable and manifest checksums, hold state, and `JobStatus=5`. Store
immutable raw `condor_q -json` evidence. Later scheduler-loss reconciliation
must bind exact `condor_q`/`condor_history` JSON and terminal identity/state;
no attempt that may have started can be released or silently reclassified as
never started.

Resource requests must leave measured safety margin above the one-million
successful-event pilot requirements. Record failure reason, completed
attempts, elapsed time, event rate, and partial diagnostic counters where a
termination-safe sidecar permits it. Use these only to diagnose failure bias,
never to salvage a partial file into the canonical sample.

Prepare and dry-run the 100/200/200 submissions. Do not launch the full
campaign without the required pilot gates and the project owner’s explicit
go-ahead.

Project raw, partial, metadata, analysis, block, and plot storage from measured
pilots for both the 300M canonical set and the possible 500M valid candidate
capacity. Verify Nikhef quota and scratch headroom before submission, including
concurrent partial files and preservation of the legacy production. Record the
projection and actual usage; do not respond to storage pressure by silently
narrowing the raw schema.

Also estimate the statistics required by the rarest predeclared final trigger
and multiplicity selections. The estimate must use pilot trigger counts and
ten-block occupancy, not only inclusive event totals. Reserve a reviewed
equal-tune expansion strategy before the first stage is declared final.

## 7. Versioned raw-data contract

Provide a reader for the legacy schema and a new schema for the canonical
campaign. Use integer branch types for PDG ID, status, indices, counts, and
charge-in-thirds; do not store these as floating point.

### 7.1 Job metadata

Store or accompany each file with:

- campaign, schema, registry, selector, multiplicity, stabilization, and tune
  configuration versions and checksums;
- repository commit and dirty-state flag;
- executable checksum;
- full settings text, effective-settings digest, PYTHIA version, ROOT version;
- tune, logical ID, primary/reserve role, attempt, exact seed;
- requested successes, attempts, successes, failures, tree entries;
- process-code counts, sum of event weights and squared weights;
- start/end time, host/site, HTCondor cluster/proc identifiers;
- generator cross-section summary;
- validation result and validator version.

Full production requires a clean, recorded commit. Dirty builds are allowed
only for labeled development pilots and cannot enter a canonical manifest.

### 7.2 Event record

Store:

- globally unique event ID derived without collision from campaign, tune,
  logical ID, successful local-event index, and valid attempt provenance;
- process code, hard-flavour channel, event weight, pTHat, and available hard
  scales;
- number of MPI and the hard outgoing heavy-quark indices/final-copy indices
  and four-vectors needed for origin matching;
- both versioned multiplicity counters;
- counts by heavy flavour, species, lifecycle, origin, and match resolution;
- heavy-flavour conservation and origin-validation flags.

If event weights are not identically one, every production, percentile,
normalisation, central-value, and uncertainty calculation must use the stored
weights consistently. Store `sumw` and `sumw2`; never silently switch between
weighted and unweighted estimates.

### 7.3 Heavy-particle collection

Retain every recognized charm- or beauty-containing hadron over full
generator phase space, independent of central-registry membership,
acceptance, status, and origin. Also retain the minimal heavy-parton/ancestry
information required to reproduce each classification.

For each heavy hadron store:

- event-record index and signed PDG ID;
- signed status and absolute status;
- `isFinal`, `isHadron`, meson/baryon flags;
- `px`, `py`, `pz`, `E`, `pT`, `eta`, rapidity, `phi`, and mass;
- integer charge in thirds;
- `mother1`, `mother2`, daughter bounds, and complete mother list or an
  equivalent flattened representation;
- the selected ancestry path, depth, matched hard-quark index and sign;
- match resolution/confidence enum and origin enum;
- central-registry flag and noncentral-state category;
- open/hidden-heavy flags;
- signed constituent counts `n_c`, `n_cbar`, `n_b`, `n_bbar`;
- signed net charm `q_c = n_c - n_cbar`;
- signed net beauty `q_b = n_b - n_bbar`;
- baryon number, strangeness, and electric charge where available.

Store physical baryon number as exactly `0`, `+1`, or `-1`. In the installed
PYTHIA 8.315 API, `baryonNumberType()` returns three times the physical baryon
number (`+3` for a baryon and `-3` for an antibaryon); divide by three only
after asserting exact divisibility and reject any other result. Test mesons,
baryons, antibaryons, and antiparticles independently.

Bc is not “charm only” or “beauty only.” Store and use both constituent
contents and sector-specific matches.

Do not store every final light particle merely for hypothetical future
extensions. The two multiplicity counters and the ancestry needed to validate
them are in scope. A deterministic pilot-only sample may retain full PYTHIA
records for debugging; it is not required in every production event.

## 8. Hard-origin matching

Replace the current digit-only heavy test and `mother1()` logic with a tested
hadron/quark-content classifier and full ancestry traversal.

Identify the selected outgoing hard c/cbar or b/bbar using verified process
information and status/copy-chain semantics. Traverse complete mother lists
and heavy-quark copies, including multi-mother junction/reconnection
topologies. Match the heavy constituent of the hadron to the hard quark of the
same flavour and sign.

Enforce uniqueness globally within each event after all per-hadron ancestry
walks. A selected outgoing hard c, cbar, b, or bbar is a physical constituent
of at most one final open-heavy hadron. PYTHIA string and junction records may
give several final hadrons the same expanded mother range; therefore two
locally unique walks can still double-assign one hard carrier. If multiple
final hadrons claim the same hard carrier, mark every conflicting claim
unresolved with a dedicated duplicate-carrier resolution code. Do not choose
one based on iteration order, species, pT, or tune. Preserve the conflicting
hard index in a separate audit branch, clear the authoritative matched-hard
field, record conflict-group and demotion totals in job metadata, and make the
raw validator prove that no selected-hard duplicate survives.

The uniqueness unit is the distinct final parent hadron, not an individual
constituent row in the validation-only all-primary-heavy table. Repeated
heavy-constituent rows belonging to one multiply-heavy final parent may share
its carrier without self-conflict; claims made by two distinct final parents
must be demoted together.

For a central charm-sector trigger, require a resolved match of the hadron’s
charm content to the selected hard c or cbar. For a central beauty-sector
trigger, require the analogous b or bbar match. Bc may be a trigger in either
sector only under the corresponding resolved constituent match.

Classify, at minimum:

- selected hard origin;
- shower origin;
- MPI origin;
- other resolved origin;
- unresolved/ambiguous, including a dedicated duplicate-hard-carrier
  resolution subtype.

Never guess an unresolved origin. An unresolved candidate cannot be a central
trigger. A direct-primary ground-state associate remains in the inclusive
associate population with origin `unresolved`; otherwise the associate sample
would acquire an origin-dependent acceptance that differs between tunes.
Report unresolved trigger candidates and associates separately by tune, hard
channel, signed species, multiplicity, and kinematics.

The pilot goal is zero unresolved trigger candidates. If the unresolved
trigger-candidate fraction is nonzero after documented algorithm validation,
stop and obtain an explicit physics sign-off before production. Do not invent
a post-hoc acceptance threshold. For associates, quantify the unresolved
fraction and repeat representative results with unresolved associates removed
as an origin-classification systematic check. The paper must report trigger
resolution efficiency, associate origin fractions, and the sensitivity to the
unresolved-associate category.

For every pair, expose an origin decomposition of the associate. In
particular, identify whether an OS associate is matched to the companion
outgoing hard antiquark/quark. This decomposition validates the interpretation
of the balancing peak, but the central OS and SS distributions use the full
direct-primary ground-state associate population.

Test charm from beauty ancestry even though heavy decays are disabled, and
prove that it cannot contaminate the central direct-charm selection.

Extract the graph/matching decision into a behavior-preserving pure helper so
tests do not merely repeat private producer logic. Cover hard-quark copy
chains, shower and MPI contamination, junction/diquark multi-mother ranges,
equal-depth ambiguity, duplicate ancestry endpoints, Bc in both sectors, and
charm-from-beauty. Gate-B real-event audits remain required because a toy
graph alone cannot prove PYTHIA event-record coverage.

## 9. Multiplicity

### 9.1 Central paper counter

Define and version:

`NCH_PRIMARY_CHARGED_ETA10_V1`

This is a genuine charged-particle multiplicity, not a count of directly
produced hadronisation products. Count every particle that is:

- final;
- electrically charged, as reported by the generator's ParticleData;
- free of charm and beauty constituents, again from ParticleData;
- `pT > 0.15 GeV/c`;
- `|eta| <= 1.0`.

Do not use a hand-written species list and do not use PYTHIA status. Charge
and heavy content must come from the generator so that species the
conventional definition includes -- Sigma+-, Xi-, Omega- -- are neither
silently dropped nor mis-signed.

This is the hadron-level analogue of the conventional experimental
primary-charged-particle definition: a charged particle with `c*tau0 > 1 cm`
that is produced directly or descends only from particles with
`c*tau0 < 1 cm`. That lifetime condition is enforced at generation time by
`ParticleDecays:limitTau0 = on` with `tau0Max = 0.01` mm. No light hadron has
`0.01 mm < c*tau0 < 10 mm`, so for light flavour the card threshold is exactly
equivalent to 1 cm/c. `Validation/TestPrimaryChargedDefinition.C` must assert
that equivalence against the installed PYTHIA ParticleData; it is not to be
asserted by documentation alone.

Charm and beauty hadrons are excluded because their decays are disabled
deliberately, so they are final only as an artefact of the production policy
and an experiment would count their decay daughters instead. The exclusion
also removes the autocorrelation that would otherwise exist between the
event-activity classifier and the heavy-flavour observable it classifies.

The counter remains a hard-heavy-sample multiplicity, not a minimum-bias one,
because the sample is generated with `HardQCD:hardccbar` and
`HardQCD:hardbbbar` at `pTHatMin = 1 GeV`. The paper must say so. It must also
state that the classifier window is `|eta| < 1` while trigger and associate
acceptance extends to `|eta| <= 4`.

Implement it once, unit test it at the exact boundaries, store it per event,
and use it identically in production, percentile construction, analysis,
plots, captions, and paper.

### 9.2 Required cross-check counter

Also define and store:

`NCH_PRIMARY_CHARGED_ETA40_V1`

Identical in every respect except `|eta| <= 4.0`. Because the generator card
already guarantees that no weak-decay daughter is final, an ancestry-based
"exclude weak daughters" counter would reconstruct a condition that already
holds and would therefore not be an independent check. The pseudorapidity
window is the independent handle instead: it probes how strongly the
conclusions depend on the rapidity range used to classify event activity,
which is a real and reviewable systematic.

Report both counters. Every predeclared observable that is differential in
multiplicity must be reproduced with the cross-check classifier, and any
qualitative change must be reported, not suppressed.

### 9.3 Percentile construction

Derive central multiplicity classes separately for each tune from every event
in that tune’s frozen final mixed-hard-flavour canonical manifest, before
trigger tagging. The first-stage manifest contains 100M events per tune; if
coverage requires an expanded superseding campaign, recompute the boundaries
from that complete enlarged union. Use event weights if needed.

Store:

- integer boundaries;
- exact inequality/tie and underflow/overflow rules;
- achieved weighted event fractions, since integer Nch makes exact requested
  percentiles impossible in general;
- convention that 0--1% is highest activity and 90--100% is lowest.

Assign each integer Nch value to exactly one non-integrated percentile class.
The classes must be mutually exclusive and their union must equal the
canonical event sample, apart from explicitly reported histogram overflow.
Use bin-index ranges or half-bin numerical edges so a boundary value cannot be
selected twice by inclusive ROOT range calls. Preserve a separate integrated
0--100% selection. Add a toy multiplicity spectrum with ties at every
boundary and prove unique class ownership and the published achieved
fractions.

Use those full-sample boundaries unchanged in all ten subsamples. Quantify
boundary stability with leave-one-block-out or equivalent validation. Also
produce fixed-Nch comparisons as a cross-check, because equal percentiles in
different tunes need not mean equal absolute activity.

Use one shared, fail-closed discrete-quantile implementation in the THnSparse
analysis and standalone multiplicity plot. Reject non-finite/negative bins,
nonconsecutive integer centers, nonzero underflow/overflow, a nonpositive
regular-bin integral, and any failed threshold lookup; never fall back to the
first or last bin. Persist a checksum-bound
`multiplicity_boundary_receipt_v1.json` containing the configuration hash,
per-tune histogram identity, central source path/checksum, thresholds,
achieved fractions, and exhaustive/disjoint integer class ranges. Draw the
boundary between integer bins at `threshold+0.5`; for every nonterminal class
the higher-activity lower bound is `threshold+1`. Publication-mode standalone
plots must consume and revalidate that receipt rather than recompute an
unbound second definition.

Receipt validation must reopen the checksum-bound source histogram and
recompute every threshold, achieved before/through fraction, and class
fraction; comparing only stored labels or hashes is insufficient. A named
selection that spans multiple percentile classes (for example 0--10%) must be
the exact contiguous, disjoint union of the frozen 0--1% and 1--10% classes,
not a failed single-label lookup or an inclusive boundary overlap.

Any fixed-Nch intervals used for the statistical-robustness cross-check are a
predeclared scientific convention, not an implementation default. Bind the
frozen specification hash in the final robustness report and require a named
physics/statistics reviewer to approve that exact definition before it can
support paper promotion. Until then, mark the checked-in candidate intervals
as review-pending and descriptive only.

The paper must call these percentiles of the generated hard-heavy-flavour
sample, not minimum-bias pp percentiles or experimental centrality.

## 10. Unified selection and kinematic policy

Implement one common eligibility function for trigger and associate lifecycle,
registry, generator stability, and signed-heavy content. Apply role cuts as
explicit parameters. Add the resolved hard-origin requirement only in the
trigger selector. Do not duplicate or comment out the common status/lifecycle
logic in one role.

Compatibility with Paul’s balancing study means preserving its
trigger-conditioned, ordered-pair OS/SS construction and output contracts. It
does not mean preserving the current accidental trigger/associate status
asymmetry: both roles must pass the common direct-primary ground-state base
selector.

Central cuts are:

- trigger: `pT > 1.0 GeV/c`, `|eta| <= 4`;
- associate: `pT > 0.15 GeV/c`, `|eta| <= 4`.

The harder trigger defines a sufficiently hard reference direction and
preserves continuity with the original analysis. The lower associate
threshold retains the soft balancing partners through which hadronisation can
redistribute the compensating heavy flavour. Different role thresholds are
therefore intentional. The common lifecycle/registry definition is identical;
the trigger-only hard-origin condition is the deliberate origin asymmetry that
keeps the SS reference meaningful.

Keep `pT > 1.0 GeV/c` for both roles as a named legacy-regression
configuration only. Do not use `pT > 0.15` triggers centrally.

Make the exact strict inequalities configuration-driven, persist them in
analyzed ROOT metadata, and print them in logs. Add boundary tests. With
identical role cuts, prove that the common direct-primary ground-state
eligibility is role symmetric; separately prove that only the trigger layer
adds the hard-origin requirement.

## 11. Charge-resolved pair registry

Create one machine-readable signed-PDG pair registry. It defines:

- heavy sector (charm or beauty);
- signed trigger PDG ID;
- signed associate PDG ID or explicit signed family member;
- OS or SS expectation from signed heavy content;
- display label and stable compatibility filename;
- meson/baryon category;
- central/noncentral status.

Every particle and antiparticle trigger is analyzed separately. Do not average
charge-conjugate triggers or associates. Use CP-conjugate comparisons as a
validation test, with differences reported against statistical precision,
but do not merge them into central points.

Support the existing paper pairs through compatibility filenames, correct the
known B0/Sigma_b filename-trigger bug, and extend coverage to all signed
ground-state Lambda, Sigma, Xi, Xi-prime, Omega, Ds, Bs, and Bc species. The
main text may show a focused subset, but all configured central species must
be available and documented.

Preserve Paul’s existing Bc beauty-sector pairs. Because Bc carries both charm
and beauty, raw content and matching remain correct in both sectors, but do
not add a separate charm-sector Bc paper observable unless it is explicitly
selected in the pair registry and motivated in the paper. Validate the
sector-dependent sign in toy tests either way.

Generate all configured pairs in one event/file pass. Do not rescan the raw
campaign once per pair. Write the established per-pair ROOT contract from the
single-pass accumulators.

## 12. Observable and combinatorics

For sector `Q` in `{c,b}`, use the signed net quantity stored on each hadron:

`q_c = n_c - n_cbar`

`q_b = n_b - n_bbar`

For a trigger and associate with nonzero sector charge:

- OS if `q_Q(trigger) * q_Q(associate) < 0`;
- SS if `q_Q(trigger) * q_Q(associate) > 0`;
- neither if either signed net quantity is zero.

Do not use electric charge to classify heavy-flavour sign. State explicitly
which constituent of Bc is balanced in each sector.

For each signed trigger species and multiplicity class define:

`C_OS(DeltaEta, DeltaPhi) = (1/N_trig) d2N_OS/dDeltaEta dDeltaPhi`

`C_SS(DeltaEta, DeltaPhi) = (1/N_trig) d2N_SS/dDeltaEta dDeltaPhi`

`B_Q(DeltaEta, DeltaPhi) = C_OS - C_SS`

Calculate each signed-trigger/multiplicity denominator once and reuse it for
every OS and SS associate channel. Assert that paired OS and SS outputs carry
the same trigger count, weighted trigger sum, and trigger-selection digest.
Never normalize OS and SS to associate-dependent trigger subsets.

The trigger population in all three expressions is the resolved hard-origin
trigger population. The OS and SS associate populations contain all
direct-primary ground-state associates, independent of origin. Fill parallel
associate-origin components (`selected_hard_companion`,
`selected_hard_noncompanion`, `shower`, `MPI`, `other`, `unresolved`) whose sum
reproduces the inclusive central histogram bin by bin. A distinct associate
must not be matched to the same unique hard constituent as the trigger; test
this explicitly.

For weighted events, replace counts by the consistently weighted pair and
trigger sums. Preserve Paul’s geometry:

- `DeltaPhi = phi_trigger - phi_associate`, wrapped to
  `[-pi/2, 3pi/2)`;
- `DeltaEta = eta_trigger - eta_associate`;
- full-DeltaPhi integration for the balancing yield;
- the established THnSparse axis order, ranges, and binning unless a
  separately versioned rebinning is required only at the final reporting
  layer.

Persist the wrapping, bin edges, overflow policy, and integration measure in
metadata and verify exact boundary behavior with toy inputs.

Audit underflow and overflow for every THnSparse axis and `summed
MULTIPLICITY`, centrally and in each tune/block. No undocumented `pT < 50 GeV`
or `Nch < 400` selection is permitted. If the relevant overflows are empty,
retain Paul’s existing axes. If they are populated, minimally expand the
versioned axes or include overflow consistently in both pair numerators and
trigger denominators, then regression-test the plotting consumer.

Use ordered conditional pairs: every eligible trigger is a reference and
every distinct eligible associate is counted once for that trigger. Exclude
self-pairs by event-record index. In the general case the count is the sum,
over trigger indices, of all accepted associate indices other than the same
particle. In the special toy case where the same `N` particles are eligible in
both roles, the directed count is `N(N-1)` and the per-trigger conditional
yield is `N-1`. In the central mode the hard-origin triggers are a subset of
the inclusive direct-primary associate population, but the ordered convention
still introduces no factor of one half.

For the new central mode, remove the plotting macro’s
identical-trigger/SS-associate factor of `0.5` from both central and subsample
paths. Retain it only inside an explicitly named exact legacy mode. Before
changing the central path, preserve the executable proof of Paul’s actual pair
loop and verify with hand-calculable toy events:

- one trigger and one OS associate;
- one trigger and one SS associate;
- two and three identical eligible particles;
- neutral heavy hadrons;
- Bc in charm and beauty sectors;
- particle and antiparticle trigger reversal.

Include the decisive charge-symmetric counting test: for `n` eligible
positive-sign and `n` eligible negative-sign particles, Paul’s ordered loop
gives `N_OS = n^2` and `N_SS = n(n-1)` for the positive-sign trigger sample.
After division by `N_trigger = n`, OS-minus-SS integrates to one partner. A
factor `0.5` on SS instead gives `(n+1)/2`, demonstrating that it is
incompatible with the declared conditional ordered-pair observable.

OS-minus-SS is a conditional heavy-sign excess. Same-sign pairs can contain
physical multi-pair, shower, and MPI correlations; SS is not guaranteed to be
pure combinatorial background. Finite acceptance also prevents an integrated
unit-normalisation interpretation. The paper must not call this a fully
normalized conserved-charge balance function unless that stronger statement
is separately proved.

The central registry is also not exhaustive: a companion hard quark may
hadronize into a stabilized vector or excited state that is intentionally
excluded. Quote the ground-state coverage from the `primary_all_heavy`
diagnostic wherever an integrated central balancing yield is interpreted.

Paul’s central derived ratio is species resolved. For a fixed trigger, sector,
cuts, and multiplicity class, define:

`R_(h/Mref) = Integral(B_Q for signed associate h) / Integral(B_Q for the signed reference meson Mref)`

For Paul-compatible D+ and Lambda_c+ trigger groups, `Mref` is the D- balancing
channel. For B+ and anti-Lambda_b trigger groups, `Mref` is the B- balancing
channel. Particle-conjugate trigger groups require the corresponding signed
conjugate reference and remain separate.

Make the reference meson an explicit signed-PDG/configuration field; do not
infer it silently from associate index zero. Validate that it exists and is
computed before any ratio. Compute numerator, denominator, and ratio inside
each statistical block so their within-tune covariance is retained.

Label this quantity a “baryon-to-reference-meson balancing-yield ratio,” or
give its explicit species ratio such as Lambda_c-bar/D-. It is not an
all-baryon/all-meson family ratio and is not an inclusive single-particle
baryon/meson yield ratio. Do not add an aggregated family ratio unless the
paper separately defines and motivates it.

## 13. Analysis outputs and compatibility

Preserve or provide a compatibility writer for:

- `summed MULTIPLICITY`;
- `hTrKinematics`;
- `hAsKinematics`;
- `hCorrelations`;
- `hCorrelationsByOrigin`;
- established OS and SS filenames used by the plotting code.

Preserve Paul’s object semantics:

- `summed MULTIPLICITY` represents the full canonical event sample, not only
  events containing the pair;
- `hTrKinematics` is filled once per eligible trigger and is independent of
  whether a particular associate is found;
- `hAsKinematics` is pair conditioned and is filled once per accepted
  trigger-associate pair;
- `hCorrelations` is filled once per accepted ordered pair.

`hCorrelationsByOrigin` must have the same first seven axes and entries as
`hCorrelations`, plus one six-bin associate-origin axis. Store immutable
`associate_origin_category_schema` and `associate_origin_category_labels`
strings next to it, validate their exact values in every central and block
file, and prove bin-by-bin closure to the inclusive histogram. No consumer may
project integer category 6 as “unresolved” without first validating that
mapping.

Do not relabel `hAsKinematics` as an inclusive single-particle spectrum. A
separate raw-tree consumer supplies genuinely inclusive spectra when the paper
needs them.

Every analyzed output also stores:

- campaign and canonical-manifest digest;
- raw schema and input checksums;
- selection and registry version/checksum;
- heavy-stability and origin-policy checksums;
- pair-registry checksum;
- trigger/associate cuts;
- multiplicity definition and boundaries;
- event/trigger/pair weighted and unweighted accounting;
- analysis commit and executable/macro checksum.

Implement the one-pass pair filling behind this consumer contract. Regression
tests must compare the new and legacy macros on the same toy/legacy inputs for
every preserved pair object and prove that differences arise only from an
approved selector, threshold, origin, species, or factor-`0.5` correction.
Do not redesign Paul’s output layer merely to expose the one-pass internal
architecture.

Write one identical `summed MULTIPLICITY` object into every pair file for a
given tune/manifest and assert identity across the inventory. Derive the
versioned integer percentile boundaries once per tune from the canonical
event sample. Paul’s plotting code may recompute the same boundaries from a
pair file for compatibility only if a validator proves exact agreement with
the authoritative boundary artifact.

The existing submission, merge, and subsample scripts work for a directory
containing exactly the intended 100 legacy jobs, but their default “first N”
or “all available jobs” discovery is unsafe when JUNCTIONS and CLOSEPACKING
contain 200 candidates. Add the smallest backwards-compatible
canonical-manifest input to:

- `submit_status_analysis.sh`;
- `merge_root_files.sh`;
- `make_subsamples.sh`;
- the `7f17356` input/coverage validators.

For the new campaign, those paths must read exactly the frozen signed manifest
and reject any unlisted reserve, duplicate attempt, or missing logical output.
Do not stage a convenient directory whose membership is undocumented. Preserve
the legacy discovery behavior only behind an explicit legacy mode.

Audit `hf_mult_pt_analysis_multi.C` before touching it. If an inclusive
single-particle result from that macro directly feeds an active paper
figure/table, minimally adapt its active path to the new raw schema and label
its lifecycle/origin definition exactly. If it does not feed the paper,
classify it as diagnostic/legacy and leave working code unchanged. Inclusive
final or feed-down-contaminated outputs cannot be relabeled as the central
direct-primary balancing result.

Keep an explicitly labeled `legacy_status` reader/selection only to reproduce
the completed legacy 100M outputs and quantify expected changes. Legacy
results are not permitted in new central figures.

## 14. Statistics and ten-subsample errors

Partition each frozen final tune manifest into ten deterministic, disjoint,
approximately equal-exposure blocks. For the first 100-file stage this means
ten blocks of ten files:

- 10,000,000 successful events per block and 100,000,000 in the union for the
  first stage;
- each canonical file appears exactly once;
- no invalid attempt or noncanonical reserve appears.

For a superseding expanded campaign, retain `K=10`, assign every final
canonical file exactly once by a deterministic data-independent rule, and
make block event totals equal. Do not combine errors from the 100M stage and
an extension as if they were independent published measurements; recompute
every block estimator from the final union.

The sealed canonical freeze assigns blocks before analysis by
`block = canonical_slot % 10`. This deterministic, data-independent rule
creates equal-exposure blocks because the final equal-tune `N` is divisible
by ten. Store the ordered central manifest, all ten block manifests, their
checksums, and a proof that the blocks are disjoint and their union is exactly
the central manifest. No partition seed applies to this modulo rule.
`make_subsamples.sh` is a compatibility entry point to the same
manifest-driven merge; it must not reshuffle, bootstrap, or rediscover files.
The same frozen blocks must be used for OS, SS, their difference, spectra,
yields, ratios, and all plots.

The central estimator is calculated from the union of all `N` files in the
sealed final tune manifest (`N=100` only for the first stage). Require equal
tune exposure, `N >= 100`, `N % 10 == 0`, and ten blocks of `N/10` files per
tune. Do not substitute the mean of nonlinear block estimators for the
full-sample estimator.

For `K=10` block estimates `x_k`, estimate the standard error as:

`SEM = sqrt[ sum_k (x_k - x_bar)^2 / (K*(K-1)) ]`

Use the sample standard deviation only as an intermediate diagnostic. Plot the
SEM, not the block standard deviation.

Compute nonlinear quantities within each block before estimating their
uncertainty:

- OS-minus-SS is subtracted within a block;
- integrated yields are integrated within a block;
- baryon-to-reference-meson ratios are formed within a block;
- within-tune tune-normalized quantities retain their block covariance.

For ratios or differences between independently generated tunes, do not pair
same-numbered blocks as if the events were correlated. Propagate independent
tune covariance or use a deterministic bootstrap that resamples each tune’s
blocks independently. Document the method and seed.

Retain histogram `Sumw2` information, but do not treat per-bin ROOT errors as
a substitute for the block covariance of normalized and derived observables.

With only ten blocks, the variance estimate has nine degrees of freedom. As a
required robustness check, compare representative errors with an alternative
data-independent partition (for example twenty blocks of five million events)
and a file-level jackknife or independent bootstrap. If conclusions or quoted
uncertainties are unstable, do not hide the instability; revise the
statistical treatment before publication.

Require finite, nonnegative errors everywhere and finite, nonzero errors for
representative populated bins. Define behavior for zero denominators and
negative OS-minus-SS integrals; do not silently set their errors to zero or
drop points.

Preserve the strict coverage behavior added in `7f17356`. Its audit of the
legacy production found 610 observables with fewer than ten finite subsample
values, dominated by zero trigger normalization in beauty blocks. This is
evidence that directory completeness is not statistical coverage. The new
campaign must rerun the exhaustive audit. Every point on a final canvas
requires ten finite central-definition block estimates. Coverage exclusions
are allowed only in a clearly labeled smoke/validation configuration; an
excluded bin cannot be referenced by a final canvas or paper claim.

Treat coverage as a production-sizing gate, not a post-plot cosmetic check.
Before freezing the final event total, produce a machine-readable matrix for
every tune, trigger, associate, multiplicity class, and derived ratio with:
central trigger count, ten block trigger counts, finite estimator count,
denominator status, central estimate, SEM, and pass/fail reason. Require
`n=10` for every point reachable from a final canvas. A full configuration
that logs only a subset of expected records has failed even when ROOT exits
zero and produces canvases.

Predeclare minimum reporting criteria for rare species. If Xi-prime, Omega, or
Bc block estimates are too sparse for a defensible uncertainty, retain their
machine-readable outputs but merge bins, quote an appropriate interval/limit,
or omit the numerical claim with an explicit precision statement. Do not
convert a statistically undefined ratio into a plotted zero.

Label Monte Carlo statistical uncertainties as such. Do not call the spread
between MONASH, JUNCTIONS, and CLOSEPACKING a statistical or systematic
uncertainty: those are distinct model predictions. Treat origin,
multiplicity-definition, pTHat, binning, and selection cross-checks according
to their documented role rather than combining them into an unjustified band.

## 15. Output validator

A logical output is valid only if all of the following pass:

- producer exit status is zero;
- ROOT file exists, is nonempty, opens, and is not a zombie;
- required trees, branches, objects, and metadata exist;
- campaign, tune, logical ID, role, attempt, seed, schema, and checksums match
  the submission manifest;
- seed appears exactly once and is ledger-authorized;
- successes and event entries equal exactly 1,000,000;
- attempts equal successes plus generation failures;
- process-code counts sum to successes;
- event IDs are unique globally;
- vector branch lengths are consistent;
- required integer fields use integer types;
- required kinematics are finite;
- every histogram/THnSparse underflow and overflow count is recorded and
  consistent with the declared acceptance;
- weight sums are consistent;
- every recognized heavy hadron obeys the stability policy;
- every central trigger is final, status 81--89, registry-valid,
  acceptance-valid, and resolved hard origin;
- every central associate is final, status 81--89, registry-valid, and
  acceptance-valid, with a stored origin category but no hard-origin
  requirement;
- multiplicity implementations pass independent recomputation on the pilot;
- origin and heavy-flavour conservation diagnostics are present;
- file checksum and validation report are recorded.

The pair-analysis reader must not trust a raw file merely because it has the
right name and a few provenance strings. Before filling any histogram it must
independently require `complete=1`, requested successes = successful events =
tree entries, attempts = successes + failures, all invariant-failure counters
zero, exact required scalar/vector branch types, and finite event weights.
Where a sealed raw-validation receipt is supplied, bind its path and SHA-256
and still reject a changed raw file; do not use a receipt as a substitute for
the in-process data-contract checks.

The implemented canonical interface passes
`CANONICAL_MANIFEST_SHA256 RAW_VALIDATION_RECEIPT
RAW_VALIDATION_RECEIPT_SHA256` to `run_status_analysis.sh`. The renderer and
worker both verify the `hf_raw_validation_receipt_v1` PASS semantics, bound
validation log, raw bytes/checksum, and campaign/tune/logical identity. The
worker records `hf_analysis_job_metadata_v3` with
`raw_input_validation_contract=analysis_raw_input_fail_closed_v1` and
`raw_validation_evidence_mode=immutable_receipt_plus_direct_preflight_v1`.
Gate-B/Gate-D or manual diagnostics without a sealed canonical receipt must
record `direct_preflight_only_v1` plus null receipt fields and must never be
promoted as publication evidence.

The canonical-manifest validator additionally proves:

- the declared equal number of unique valid logical outputs per tune;
- at least 100M successful events per tune and exactly the frozen declared
  event count;
- documented primary-to-reserve substitutions;
- no extra reserve in the canonical set;
- ten disjoint complete block manifests;
- union of blocks equals the canonical manifest;
- duplicate seed count is zero.

The publication-output validator additionally proves that every configured
final point has ten finite block estimates, a finite uncertainty, a nonzero
uncertainty unless a documented deterministic/degenerate observable proves
otherwise, and no missing object, placeholder error, NaN, infinity, or silent
zero-denominator result.

## 16. Required validation sequence

Do not advance past a failed gate.

### Gate A: static and unit validation

1. Build every changed producer, validator, analysis, merge, and plotting
   component with warnings treated seriously.
2. Validate all PYTHIA settings and the tune-difference allowlist.
3. Validate the signed species registry independently against PYTHIA and a
   checksum-bound official PDG 2025 snapshot. Gate A must fail until the
   `5312`/`5322`, Xi-prime-b-zero, and Sigma-b-zero discrepancies have an
   explicit reviewed treatment.
4. Unit-test heavy-content decoding, hidden/open separation, antiparticles,
   Bc, Xi versus Xi-prime, and starred-state exclusion.
5. Unit-test exact kinematic boundaries and both multiplicity counters.
6. Run selection-symmetry and pair-combinatorics toy tests.
7. Reproduce Paul’s ordered pair counts, per-trigger normalization,
   reference-meson ratios, and legacy factor-`0.5` output on toy inputs; then
   prove the approved central-mode differences.
8. Validate deterministic, injective seed allocation.

### Gate B: deterministic tune pilots

Do not generate or submit these pilots while the checked-in pTHat
specification says `PENDING_GATE_B_OWNER_REVIEW`. Its numerical equivalence
margins and aggregate family diagnostic are implementation proposals, not
Paul/paper definitions. Before seeing pilot data, a named project owner or
designated physics/statistics reviewer must approve the exact specification,
role, rationale, and timezone-aware decision in a reviewed commit. Campaign
generation, submission, evaluation, and Gate-B aggregation must all reject a
pending/placeholder/future review and bind the approved spec SHA-256.

For all three tunes:

1. Run at least one reproducible full one-million-success logical-job pilot
   using a reserved pilot seed; use additional smaller deterministic samples
   for unit-level diagnostics.
2. Prove exact successful-event and one-entry-per-event accounting.
3. Observe and validate hard-charm and hard-beauty process channels.
4. Produce and inspect the complete heavy-stability audit.
5. Confirm representative ground and excited heavy species remain final.
6. Confirm unrelated light-decay policy is unchanged.
7. Validate hard-origin matching in string, junction, and close-packing
   topologies; report unresolved trigger candidates and associate origin
   fractions separately.
8. Recompute multiplicities independently for selected events.
9. Test event weights and process/cross-section accounting.
10. Run the pTHat-threshold sensitivity pilot.
11. Benchmark time, peak memory, output size, and compression by tune.

If the aggregate Gate-B report is `NEEDS_SIGNOFF` solely because unresolved
publication-trigger candidates are nonzero, stop for the project owner. The
owner—not the coding agent—may create the read-only
`campaigns/<GATEB_CAMPAIGN>/GATE_B_PHYSICS_SIGNOFF.json` with schema
`hf_gate_b_physics_signoff_v1`, bound to the original report SHA-256 and exact
nine-sample unresolved table. The implementation must first support
read-only verification and must then emit a separate immutable superseding
`hf_publication_gate_b_report_v1`; it must never rewrite the original
`NEEDS_SIGNOFF` tree. This narrow resolution cannot waive technical failures,
an inconclusive pTHat result, or resolved-observable pTHat shifts. The
Gate-B-specific sign-off is distinct from the mandatory full-launch
`PHYSICS_ORIGIN_SIGNOFF.json`.

### Gate C: failure and workflow validation

Machine gate authorization must validate the exact report schema, frozen
command inventory, implementation-source hashes, command/log checksums,
expected scientific outputs, and absence of unresolved findings. A JSON object
whose state says `PASS`, a successful `/usr/bin/true`, or a checksummed
handwritten report is not gate evidence. Gate A must also prove the release
commit is reachable from freshly fetched live origin refs.

1. Force a generation failure.
2. Emulate eviction/wall-time termination.
3. Prove partial files are not promoted.
4. Retry with the same logical ID, a new attempt, and a new seed.
5. Present a corrupt/nonempty file and prove it is not skipped.
6. Dry-run exactly 100/200/200 candidate slots.
7. Demonstrate deterministic canonical selection and reserve substitution on
   a synthetic manifest.
8. Run global seed and event-ID collision checks.
9. Demonstrate the primary/reserve and failure-bias diagnostic using synthetic
   and pilot job metadata.
10. Prove that status submission, complete-root merge, subsample creation, and
    plotting validation all consume the same synthetic canonical manifest and
    reject extra reserve files.

### Gate D: end-to-end analysis smoke test

1. Run one-pass charge-resolved analysis for all central pairs.
   For Gate-B pilots, render this from the immutable nine-row pilot manifest;
   do not use a hand-written Condor submit file.
2. Verify legacy ROOT compatibility objects.
3. Audit every ROOT axis underflow/overflow and prove that no implicit upper
   pT or multiplicity cut enters the observable.
4. Verify the corrected B0/Sigma_b trigger and filename.
5. Compare the legacy selector with existing 100M results.
6. Confirm expected differences from heavy stabilization, hard matching,
   species registry, role thresholds, charge separation, and removal of 0.5.
7. Verify the all-primary-heavy closure diagnostic and central ground-state
   coverage accounting.
8. Build central and ten-block outputs from a pilot manifest.
9. Validate SEM, covariance, nonlinear ratios, and independent-tune
   propagation.
10. Run the `7f17356` strict input and exhaustive subsample-coverage
    validators. Representative smoke points must pass. The exhaustive
    full-paper pilot audit may return exit 2 only with the versioned state
    `PILOT_INSUFFICIENT_FOR_FULL_PAPER` and
    `publication_promotion_allowed=false`; preserve it as a production-sizing
    result, not a coverage PASS. Any other audit failure fails Gate D.
11. Regenerate representative plots and render/visually inspect every PDF.
12. Produce `hf_gate_d_storage_projection_v1` from the measured raw,
    simultaneous-partial, per-job analysis, merged-central, ten-block, plot,
    log, and evidence footprints. Use `os.statvfs(...).f_bavail` per actual
    filesystem. Require projected use to be no more than 70% of current
    available bytes and projected remaining space to be at least
    `max(5% of capacity, 500 GiB)`.
13. At finalization, recompute the capacity snapshot and require both
    preparation and final checks to pass with `state=PASS` and
    `gate_e_storage_authorized=true`.

Reprobe the same filesystem identities and policy at every production claim,
retry claim, scheduler-evidence record, and held-cluster release. Include all
retained `partial/` and `quarantine/` bytes and the declared staging
contingency in the live requirement. Reject a stale timestamp, changed device
or geometry, unsafe link, insufficient reserve, or report whose arithmetic
cannot be reconstructed.

The 2026-07-30 read-only snapshot was already below this reserve floor:
capacity `36,688,187,162,624` bytes, `f_bavail`
`1,730,683,666,432` bytes, required 5% reserve
`1,834,409,358,131` bytes, and deficit `103,725,691,699` bytes
(about 96.6 GiB) before any new allocation. Treat this as a volatile but
explicit Gate-D/E blocker. Recompute it at execution time; do not reinterpret
the approximate free-space display as authorization.

A later live check at `2026-07-30T16:41:35+02:00` found only
`1,678,909,767,680` bytes available on the same
`36,688,187,162,624`-byte filesystem: about `155,499,590,451` bytes
(144.8 GiB) below the 5% reserve before any new allocation. This worsened
snapshot supersedes the earlier free-space number operationally but remains
diagnostic rather than an authorization artifact.

The most recent read-only check in this implementation audit, at
`2026-07-30T17:39:21+02:00`, found `1,671,602,503,680` bytes available on the
same filesystem, a `162,806,854,451`-byte (about 151.7 GiB) deficit relative
to the 5% reserve before any new allocation. This latest diagnostic snapshot
supersedes both earlier values operationally; it still does not substitute
for the fresh checksum-bound Gate-D capacity artifact.

### Gate E: full campaign and publication outputs

Only after an explicit go-ahead:

Before first-stage submission, require two separate read-only owner artifacts.
An expansion additionally requires the distinct third owner artifact specified
in Section 6.2, and both of the ordinary launch artifacts must be newly bound
to the child campaign; no parent authorization is reusable. The mandatory
origin-decision file uses schema
`hf_full_production_origin_signoff_v1`, decision
`APPROVE_FULL_PRODUCTION`, `reviewer_role=project_owner`, and binds the exact
Gate-B report plus its complete nine-sample unresolved-trigger table. A zero
finding records the predeclared no-special-treatment decision; a nonzero
finding records the predeclared trigger-exclusion/associate-retention policy
and a superseding Gate-B PASS. The separate
`hf_full_production_gate_authorization_v1` binds the canonical Gate A--D and
pTHat reports at the exact campaign commit. Both files are single-link
mode-`0444` regular files with real explicitly UTC, non-future owner
timestamps. The bound Gate-D report must carry the passing storage projection
and fresh final capacity recheck above. A coding agent may validate these
files but must never author any of these approvals.

1. Submit the first-stage 100/200/200 candidate strategy.
2. Reconcile and validate every attempt.
3. Complete and approve the failure/missingness-bias audit.
4. Freeze exactly 100 first-stage outputs per tune.
5. Freeze ten first-stage blocks per tune and run the exhaustive coverage and
   precision matrix.
6. If the matrix fails, stop paper promotion and execute the reviewed
   equal-tune expansion or approved pre-result scope revision in Section 6;
   then freeze a superseding final manifest and ten final blocks.
7. Run the canonical central and block analyses from the final manifests.
8. Regenerate every paper table and figure from recorded commands.
9. Numerically and visually validate all promoted artifacts.

Repository implementation can be reported as “ready for production” after
Gates A--D. It cannot be reported as “publication complete” until Gate E,
paper review, and the final audits below pass.

## 17. Plotting

The active plotting implementation and documentation surface is:

- `PlottingScripts/improvedPlotting_THnSparse.C`;
- `PlottingScripts/TunePlotStyle.h`;
- `PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json`;
- `PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json`;
- `PlottingScripts/run_paper_plots.sh`;
- `PlottingScripts/README.md`;
- `plotting_documentation.md`;
- `README.md`.

Treat the first JSON file as the full paper configuration and the
`complete_root` JSON file as the reduced/smoke selection. Keep Paul's reduced
trigger/canvas scope, grouped-trigger schema, and per-canvas
`TriggerToUse`. Update the runner `--help` and all three documentation files
whenever their semantics, paths, commands, errors, or outputs change. Remove
obsolete instructions that invoke `improvedPlotting.C` as the current paper
path.

Use one authoritative dataset selector resolving campaign, manifest, schema,
selection, pair registry, multiplicity boundaries, central analysis,
subsamples, and output directory. Eliminate scattered absolute user paths.
Keep the legacy dataset as the default until the new canonical manifest is
validated, then switch through one documented selector.

Its shell interface must null-safely export a machine-readable
publication-eligibility flag, the canonical manifest, production root,
analysis root, raw base, analyzed-data base, complete-root tag, and block
base. Every active plotting consumer must use those same values. Legacy rows
must set the flag false; canonical paper targets must fail closed rather than
silently run canonical/factor-one configurations on a legacy/factor-one-half
sample. In canonical mode, inclusive raw kinematics must consume only the
checksum-bound sealed manifest and verify each selected raw file's size and
SHA-256; recursive tune-directory discovery can remain only as an explicitly
named legacy diagnostic and must never admit unlisted reserves into a paper
result. Canonical consumers must derive the equal-tune raw count `N` from the
sealed manifest/summary rather than hard-code 100 or 300.

Use `status=canonical_candidate`, `publication_eligible=false`, and null
authorization fields for the sealed sample while generating boundary,
origin, robustness, candidate-plot, and human-review evidence. These outputs
must carry ineligible canonical-validation provenance and must be regenerated
after promotion. This explicit state breaks the evidence/authorization
dependency without weakening final plotting.

The selector's `publication_eligible=true` value is only a pointer, never an
approval. A canonical row must also bind a single-link mode-`0444`
`hf_publication_dataset_eligibility_v1` project-owner authorization. That
authorization must checksum-bind the exact canonical manifest, freeze
summary/seal and validation log/receipt, nonempty final origin/closure report,
descriptive statistical-robustness report, and a separate single-link
mode-`0444` `hf_final_scientific_review_v1`. The latter must bind the frozen
statistical-specification hash and explicitly review the fixed-Nch
definition, unresolved species-registry disposition, and paper claim scope.
Reject extra/template fields, placeholder identities, changed evidence,
empty coverage arrays, a different commit/campaign/sample, or a Boolean with
no authorization. Coding agents may provide intentionally invalid templates
and validators but may not author either approval.

For regression against the real audited Nikhef production, resolve these
checkout-relative paths under canonical
`/data/alice/ipardoza/Hadronization`:

- `AnalyzedData/complete_root_21_06_2026_MONASH`;
- `AnalyzedData/complete_root_21_06_2026_JUNCTIONS`;
- `AnalyzedData/complete_root_21_06_2026_CLOSEPACKING`;
- `AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_MONASH`;
- `AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_JUNCTIONS`;
- `AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_CLOSEPACKING`.

The two checked-in THnSparse paper configurations must use:

- `"base_dir": "AnalyzedData"`;
- `"bb_bar_complete_root_dir": "complete_root_21_06_2026"`;
- `"cc_bar_complete_root_dir": "complete_root_21_06_2026"`;
- subsample `"base"`:
  `"AnalyzedData/SUBSAMPLES_700/combined_root_subSamples"`;
- `"nSubSamples": 10`;
- MONASH, JUNCTIONS, and CLOSEPACKING.

Support `HADRONIZATION_BASE` and absolute paths as explicit resolver
overrides, but never require a username-specific `/Users/...` or `/data/...`
path in checked-in JSON. Preserve both the flat
`AnalyzedData/complete_root_<tag>_<TUNE>` layout and the already supported
nested tune layout.

The legacy central directories currently have no `jobs_used.txt`-style
provenance. Create a non-destructive validation manifest that records every
central file, the ten block source manifests, job IDs where recoverable,
sizes, checksums, required object/type validation, and
central-versus-block-union comparison. New canonical merged directories must
instead store an immutable byte-copy of the all-tune source manifest
(`3*N` central rows and `3*N/10` rows per block), with provenance binding the
full manifest hash and the explicit selected-tune filter/count. The fixed 300
files per merged directory are the pair registry, not a fixed raw exposure.
Do not imply that missing legacy seed metadata has been recovered, and do not
regenerate central files from a different raw set under the same tag.

Canonical merging must retain a machine-readable merge contract and one
central-versus-ten-block closure log per tune. Require all 300 fixed pair
identities, all five numeric pair objects, stored contents and `Sumw2`, the
twelve metadata fields, and the all-tune source-manifest/explicit-tune-filter
contract to close before promotion. The implemented closure tolerance is
`2e-10`; a missing or differing closure artifact is a release blocker.

Use Paul's plotting architecture on the latest stable `main` as the
implementation baseline. Port or reuse the still-unmerged compatible
hardening at `7f17356`; do not redo it, override later stable-main behavior,
or treat that branch as a separate scientific pipeline. Its full
configuration remains strict and its reduced configuration remains
smoke-only.

Apply central trigger/associate pT, eta, lifecycle, and origin cuts exactly
once in the one-pass pair analysis. Preserve Paul’s plotting projections as
consumers of already-selected pair objects unless a regression-tested
downstream cut is required. Configuration fields must either be enforced or
explicitly validated against upstream metadata; they must never be silently
inactive.

Reconcile normal, complete-root, and smoke configurations. They may vary only
in explicitly named runtime scope, not scientific definitions. Enable
statistical errors in every final configuration.

The checked-in full and reduced paper configurations must both use portable
checkout-relative inputs, `calculate_errors=true`, ten subsamples, grouped
triggers, and `TriggerToUse`. The reduced/complete-root target is a
reduced-scope validation with subsample errors, not a no-error result. If a
no-error diagnostic is retained, give it an explicit debug-only name and
prevent paper promotion from it. Validate both JSON files mechanically and
keep the multiplicity labels ordered:

`90-100, 80-90, 70-80, 60-70, 50-60, 40-50, 30-40, 20-30, 10-20, 1-10, 0-1`.

Use `PlottingScripts/TunePlotStyle.h` as the single source of truth:

- MONASH: black, marker 20, solid line;
- JUNCTIONS: blue+1, marker 21, dashed line;
- CLOSEPACKING: magenta+1, marker 22, line style 7.

Style a tune ratio by its numerator tune. Preserve species/multiplicity
distinctions through their own line attributes without overriding tune color
or marker, show line and marker in legends, and reject contradictory stale
JSON colors. Apply this to the active THnSparse macro and every other macro
that directly produces a current paper figure, including
`Plot_InclusiveKinematicSpectra_Raw.C`,
`Plot_KinematicSpectra_THnSparse.C`, and
`Plot_MultiplicityDistribution_PercentileBoundaries.C`. Do not modernize an
unreferenced legacy plot macro merely for visual consistency.

Initialize every optional mini-pad pointer to `nullptr` in all four balancing
drawing paths, return `nullptr` when no mini pad is requested, and null-check
before global-canvas composition. Do not overwrite legacy figures.

The four final uncertainty paths are:

- `drawBalancingPlots`;
- `drawBalancingPlotsTUNERatios`;
- `drawBalancingBaryonMesonRatioPlots`;
- `drawBalancingBaryonMesonRatioPlotsTUNERatios`.

Central values come from the complete-root union. Balancing-yield errors come
from the ten corresponding block yields. Form baryon/reference-meson ratios
inside each block. Combine independently generated tune uncertainties in
quadrature, and use the matching associate's uncertainty for both tunes in a
tune double ratio. Apply identical OS/SS choices, cuts, normalization,
integration, and the approved same-sign convention to central and block
paths. Explicitly reject non-finite/zero denominators and `1e-10` placeholder
errors. If correlation panels show native ROOT projection errors, label them
as distinct from block SEM; do not visually mix the two meanings without an
explicit legend/caption.

Run the reduced smoke workflow first and then the full workflow on the
canonical Nikhef checkout using the real central and subsample manifests.
Save complete ROOT logs with verbose statistical diagnostics. Parse every
`subsample yield stats`, `subsample ratio stats`, and `stdError=` record and
require the expected record count, `n=10`, finite values, and positive SEM for
each nondegenerate final point. Include representative MONASH, JUNCTIONS, and
CLOSEPACKING records for charm and beauty, for both yields and
baryon/reference-meson ratios, in the validation report.

At minimum record these invocations and their environment:

```sh
./PlottingScripts/run_paper_plots.sh smoke
./PlottingScripts/run_paper_plots.sh thnsparse
./PlottingScripts/run_paper_plots.sh multiplicity-spectrum
./PlottingScripts/run_paper_plots.sh all
```

Compile/load every touched ROOT macro in batch mode before those runs. Ensure
temporary `TFile`, histogram/projection, graph, legend, canvas, and pad
objects have explicit ownership and cleanup so the exhaustive full
configuration completes without unbounded memory growth. A successful smoke
run is not a substitute for a completed full run.

Before drawing on logarithmic axes, compute a finite positive envelope that
includes central values and their complete error extents. Fail if configured
limits clip any nondegenerate point/error bar or if no positive lower extent
exists. Never hide an uncertainty by silently clipping it below a log-axis
minimum.

Every final canvas must be regenerated as a complete PDF, PNG, and ROOT-macro
triplet. Each file receives an adjacent checksum-bound provenance sidecar, and
the run receives a shared immutable receipt. The receipt must bind the exact
input inventory and hashes, analysis and plotting commits, tracked-clean
release state, generator and configuration payloads/hashes, selection/cut
versions, sealed central manifest, all ten block manifests, multiplicity
boundary receipt where applicable, exact command/target, UTC timestamp, and
every output checksum. Canonical plotting must fail closed on a missing,
stale, or tampered binding or incomplete triplet. Legacy and Gate-D pilot
receipts must set `publication_eligible=false`; embedded metadata alone is not
a substitute for these sidecars and receipt. Verify every proposed paper
artifact with `tools/final_plot_provenance.py verify` before copying it.

Before paper promotion:

- compare plotted numbers with machine-readable tables;
- confirm central and block inputs are identical except for manifest subset;
- confirm nonzero errors;
- check axes, units, legends, tune mapping, charge labels, multiplicity order,
  and captions;
- render and inspect the complete PDF, not only ROOT canvases.

The canonical THnSparse deliverables include
`global_balancing_plots_multiplicity_{PDF,PNG,MACRO}`,
`global_balancing_baryon_over_meson_ratio_multiplicity_{PDF,PNG,MACRO}`, and
every configured final OS/SS correlation panel. Smoke equivalents are
validation artifacts only. Generate into a clean staging directory where
practical, promote only after all numerical and visual gates pass, and never
commit bulk generated `PlottingScripts/Plots/` output as source.

## 18. Paper and source requirements

Update the complete working draft, not isolated snippets. Make the
Introduction, Observables, Model, Results, Summary, captions, tables,
bibliography, and supplementary/reproducibility text agree with the exact
implemented contracts.

Parse every `\includegraphics` entry in the active `Results.tex` and create a
one-to-one provenance row containing figure/panel and paper label, generator
file and symbol, exact command, configuration digest, central and block
manifest digests, source dataset, generated output, copied paper path, and
checksum. A paper graphic with no established current generator is a release
blocker or must be explicitly labeled as a justified legacy input. Replace a
stale paper copy only when it is the same observable and the regenerated
artifact passes validation; otherwise document the scientific difference
instead of overwriting it.

Recheck captions that predate the canonical tune styling and the current
beauty trigger/associate definitions. The audit found stale color language
and at least one beauty caption inconsistent with the plotted content. No
caption may be corrected by prose alone while retaining a plot whose curves
or provenance disagree.

The paper must explicitly state:

- the model-level physics objective and limitations;
- mixed hard-ccbar/hard-bbbar generation semantics;
- collision energy, hard processes, pTHat threshold, PYTHIA/ROOT versions;
- that every heavy-hadron decay is disabled programmatically;
- the operational ground-state registry and separate Xi/Xi-prime treatment;
- that particles and antiparticles remain separate;
- direct-primary, hard-origin, generator-stable, open/hidden definitions;
- that hard origin is required for triggers, while the direct-primary
  associate population includes all origins so the SS reference remains
  defined;
- the associate-origin decomposition and companion-hard-partner validation;
- validation-only all-primary-heavy closure and central ground-state coverage;
- exact trigger and associate cuts and their physical rationale;
- both multiplicity definitions and which one is central;
- tune-specific hard-heavy-sample percentile construction;
- tune bundles and every effective difference relevant to interpretation;
- hard-origin algorithm, resolution efficiency, and unresolved treatment;
- signed-heavy OS/SS definition;
- ordered-pair convention and absence of a factor 0.5;
- per-trigger normalization and OS-minus-SS equation;
- why OS-minus-SS is a conditional balancing proxy, not automatically pure
  background subtraction or a unit-normalized balance function;
- exact baryon-to-reference-meson balancing-yield ratios and signed reference
  mapping;
- the final equal canonical event count per tune, the 100M minimum stage, any
  coverage-driven expansion, and reserve exclusion;
- ten-block SEM and cross-tune uncertainty method;
- generator-level, stable-heavy, no-detector limitations;
- commit, campaign, manifest, registry, configuration, and artifact
  provenance needed for reproduction.

Electric-charge, baryon-number, and strangeness balancing may be discussed as
motivation, but the paper must not claim to measure them unless an explicitly
defined, validated observable is actually in the central pipeline. Species
composition and baryon/meson heavy-flavour balancing do not by themselves
constitute a separately normalized baryon-number balance function.

Provide a compact table of all central signed species and a compact table of
all tune settings that differ. Put long machine-readable tables and manifests
in the repository or supplementary material.

Use primary sources for PYTHIA semantics and tune definitions and an
authoritative PDG source for particles. Cite the thesis only for historical
motivation or comparison. Do not cite it as authority for the corrected
selector or statistics.

Fix bibliography duplication, missing active citations, broken keys, and
absolute Zotero file paths. Every scientific statement about a model setting,
status convention, species, or statistical method must have an appropriate
source or a derivation.

Remove placeholder figures, duplicate labels, missing bibliography resources,
stale colors, contradicted captions, speculative causal claims, and
under-construction text. Do not insert the new event totals or physics claims
until regenerated validated outputs support them.

Compile the final source from a clean build directory. Require zero undefined
references/citations, zero duplicate labels, and zero missing figure or
bibliography inputs. Review every remaining warning rather than accepting a
successful exit code alone.

## 19. Reproducibility and operational documentation

Create or update:

- a top-level reproducibility guide;
- simulation, HTCondor, analysis, subsampling, plotting, and paper READMEs;
- machine-readable campaign, tune-allowlist, species, pair, canonical, block,
  and seed manifests;
- environment/build lock information;
- exact local and Nikhef commands;
- validation reports and expected checksums;
- a figure/table provenance index mapping every paper artifact to its command
  and inputs.

A clean user with the documented PYTHIA and ROOT versions must be able to:

1. build;
2. run a deterministic small pilot;
3. validate it;
4. analyze it;
5. construct block errors;
6. regenerate representative plots and paper tables;
7. compile the paper.

No step may depend on an undocumented shell state, username, absolute personal
path, manual ROOT click, or file that is absent from the repository/manifests.

Provide one noninteractive smoke-test command suitable for continuous
integration or an equivalent clean-environment runner. Prepare a release
bundle or archival plan containing the exact code commit, cards, environment,
registries, manifests, validation reports, machine-readable result tables, and
checksums. Include a raw/derived data-availability statement sufficient for an
independent researcher to obtain or verify the inputs.

## 20. Mandatory final file-by-file architecture audit

After implementation and end-to-end validation, audit the repository again
file by file and create or update:

`REPOSITORY_FILE_CATALOG.md`

Account for every path returned by `git ls-files`, plus intentional untracked
paper inputs and operational files needed on Nikhef. For generated/binary
data, catalog the directory or manifest rather than enumerating every large
file, while retaining manifest-level traceability.

For every catalogued file record:

- path;
- type and purpose;
- active owner/component;
- direct callers and consumers;
- pipeline stage;
- whether it feeds a paper figure, table, or statement;
- authoritative, support, generated, legacy, stale, or deprecated status;
- replacement path if stale/deprecated;
- compatibility reason if retained;
- tests/validation covering it;
- local/Nikhef portability notes.

Use these definitions:

- **authoritative**: part of the central production-to-paper path;
- **support**: needed to build, validate, submit, or reproduce that path;
- **generated**: reproducible output, with generating command and manifest;
- **legacy**: intentionally retained for regression/history, not central;
- **stale**: no current validated consumer or inconsistent with the central
  contract;
- **deprecated**: replaced and blocked from central use.

Do not delete stale or legacy files merely to make the catalog cleaner.
Prevent them from being selected accidentally, label them in their own
catalog/authoritative READMEs, and document the reason for retention. Do not
edit every legacy file merely to add a banner; change an individual header only
when accidental central use is a demonstrated risk and the file is in the
approved change budget.

Add a mechanical coverage check proving that every tracked file appears
exactly once in the catalog and every authoritative file has at least one
documented consumer and validation path. Re-run the catalog audit after the
last code or paper change.

## 21. Required independent final reviews

Perform all five reviews from a clean checkout/worktree. Record reviewer date,
commit, inputs, commands, findings, and resolution. A checklist tick without
evidence is not a review.

### Review 1: physics definitions

Verify heavy stability, operational ground states, Xi/Xi-prime separation,
charge resolution, trigger hard-origin matching, inclusive associate origins,
Bc content, multiplicity meaning, role cuts, tune-bundle interpretation, and
paper terminology.

### Review 2: observable and combinatorics

Re-derive OS/SS from signed charm/beauty, hand-check ordered pairs, prove no
factor 0.5 in the central ordered convention, verify per-trigger
normalization, integration, signed-species mapping, and
the distinction among Paul’s baryon-to-reference-meson balancing-yield ratio,
an aggregated family ratio, and an inclusive single-particle baryon/meson
ratio. Verify that the all-primary-heavy closure decomposition accounts for
companion hard flavour excluded by the central registry.

### Review 3: statistics

Trace one central value and uncertainty from raw events through canonical and
block manifests to the plotted point. Check weights, covariance, nonlinear
block estimators, SEM, independent-tune propagation, zero-denominator policy,
and robustness to block partition.

### Review 4: production and reproducibility

Trace tune settings, seed, event ID, success accounting, retry, validation,
manifest freezing, dataset selection, paths, ROOT contracts, build
environment, and figure provenance. Reproduce the smoke workflow from the
written instructions. For every touched code or script file, cite its
physics-defect, ambiguity-resolution, manifest-safety, or required-schema
reason and the regression evidence. Revert unnecessary refactors from the
proposed patch; preserve validated `7f17356` behavior and working legacy
adapters.

### Review 5: adversarial journal/editor review

Attempt to falsify the analysis. At minimum challenge:

- whether status 81--89 is being mistaken for hard origin;
- whether origin inefficiency can bias tune comparisons;
- whether the trigger-only hard-origin requirement and inclusive-associate
  origin policy are implemented consistently;
- whether the sum of associate-origin components exactly reproduces the
  central OS and SS distributions;
- whether heavy stabilization changes the observable relative to experiment;
- whether the pTHat threshold sculpts the trigger region;
- whether mixed hard-flavour sample percentiles are misrepresented;
- whether tune differences are over-attributed to one mechanism;
- whether SS contains real physics rather than pure background;
- whether finite acceptance invalidates normalization claims;
- whether charge-conjugate disagreement is hidden;
- whether rare Xi-prime/Omega/Bc results have adequate precision;
- whether ten blocks support the quoted uncertainty precision;
- whether reserve selection or failures introduce bias;
- whether any legacy/stale file can silently enter the paper path;
- whether every result and plot can be regenerated from immutable inputs.

Resolve every correct criticism in code, documentation, or scoped scientific
language. If resolution requires changing an authoritative physics choice,
stop and ask the project owner rather than guessing.

## 22. Explicit known limitations that must remain visible

Unless later evidence justifies a stronger statement, retain these
limitations:

- generator-stable primary heavy species are not experimental
  decay-inclusive yields;
- there is no detector response or reconstruction efficiency;
- the sample is hard-heavy-flavour enriched, not minimum bias;
- `pTHatMin = 1 GeV` is part of the generated phase-space definition;
- tune bundles differ in several parameters, limiting single-mechanism causal
  interpretation;
- trigger-origin matching can introduce a selection efficiency that must be
  measured, while unresolved associate origins require a sensitivity check;
- OS-minus-SS is not automatically a pure-background subtraction;
- finite pT/eta acceptance means integrated balancing need not equal one;
- stabilized noncentral heavy states make the central ground-state registry
  intentionally non-exhaustive, so its integrated balancing yield is not full
  heavy-flavour closure;
- separate particle and antiparticle results reduce rare-species precision;
- ten-block uncertainty estimates themselves have finite precision;
- final-primary multiplicity cross-checks are altered by disabled heavy
  decays.

Do not turn a limitation into an unsupported claim. Quantify it where the
available sample permits.

## 23. Completion criteria and final report

The repository is ready for production only when Gates A--D pass and all
identified defects have tests or explicit documented resolutions.

The analysis is publication complete only when:

- an equal validated final event count of at least 100M is frozen per tune;
- duplicate seeds and global event IDs are zero;
- all canonical and block manifests validate;
- central charge-resolved results use
  `hard_trigger_primary_ground__primary_ground_associate_v1`;
- every heavy hadron is generator-stable;
- trigger hard-origin matching, associate-origin decomposition, and unresolved
  treatment are approved;
- central and block calculations share definitions and inputs;
- representative errors are finite, nonzero, and robust;
- every point reachable from a final canvas has ten finite block estimates
  and passes the predeclared coverage/precision rule;
- all paper figures/tables are regenerated and visually/numerically checked;
- paper text and sources match the implementation;
- the full repository catalog has complete mechanical coverage;
- all five final reviews have no unresolved correctness contradiction;
- the existing legacy data and unrelated work remain untouched.

The final coding-agent report must include:

- branch, start commit, final commit, and worktree;
- final local `main`, live `origin/main`, and canonical Nikhef `main` hashes,
  with an explicit statement if protected dirty work prevented a safe
  fast-forward;
- every changed file and its reason;
- Paul-compatibility matrix classifying every behavioral difference as a
  physics defect, resolved ambiguity, or standardization mismatch, plus the
  active files deliberately left unchanged;
- campaign/schema/registry/selector/multiplicity versions;
- exact effective tune-difference table;
- stabilization audit summary and checksum;
- species-registry validation;
- origin-resolution results;
- candidate, attempt, failure, retry, valid, reserve, and canonical counts;
- successful events and weights per hard channel and tune;
- seed-ledger and event-ID collision results;
- runtime/storage benchmarks;
- canonical and block manifest hashes;
- legacy regression and expected-difference report;
- toy combinatorics and selector tests;
- statistical robustness report;
- plots/tables/paper provenance;
- complete smoke/full ROOT log paths and representative nonzero SEM records;
- generated, replaced, and stale-removed plot inventories;
- file-catalog coverage result;
- findings and resolutions from all five final reviews;
- remaining scientific or Nikhef operational risks.

Do not claim completion because jobs were submitted, a queue emptied, files
are nonempty, or plots were produced. Completion requires validated physics
definitions, equal canonical statistics, reproducible uncertainties, and a
paper whose claims are supported by the exact pipeline.

After the publication-ready branch is reviewed and merged, fetch and
fast-forward the canonical Nikhef `main` with `--ff-only`. Fast-forward the
local `main` only after proving that the protected bibliography and untracked
paper work have been isolated without loss and that Git can update without
overwriting them. Never stash, reset, clean, force-push, or silently move that
work merely to make hashes match. If safe synchronization is blocked, report
the exact hashes and blocker rather than claiming completion.

## 24. Defect-to-requirement corroboration checklist

Use this checklist during implementation. Every item is a release blocker.

- The superseded 5B-candidate/3B-canonical design conflicts with the approved
  100/200/200 candidate first stage:
  Section 6 replaces it while making 100M per tune a minimum rather than an
  unsupported guarantee of rare-channel coverage.
- Derived heavy-decay campaigns and broad light-particle storage are not
  immediately relevant to the central study:
  Sections 3, 4.3, and 7.3 explicitly keep them out of scope while documenting
  the stable-heavy limitation.
- Digit-based heavy classification misidentifies hidden/non-hadrons:
  Sections 4, 7, 8, 16.
- Local `main`, live `origin/main`, and Nikhef clones/worktrees are not all at
  one commit and include protected dirty work:
  Sections 2 and 20.
- The older Nikhef deterministic-seed helper remains modulo based and is not a
  proved collision-free campaign ledger:
  Sections 2 and 6.3.
- Incomplete hand-written decay lists omit Sigma/Xi/Omega/excitations:
  Sections 4 and 5.3.
- Time/PID/modulo seeds and absent metadata:
  Sections 6.3, 7.1, 15.
- Attempts counted instead of exact successful events:
  Sections 5.4 and 15.
- Raw pair analysis previously checked only a subset of provenance/shape
  fields and could accept an incomplete file, inconsistent
  requested/success/tree counts, nonzero producer invariant failures, or a
  non-finite event weight:
  Sections 7, 13, and 15 require an independent fail-closed raw-to-analysis
  contract.
- Empty-heavy events omitted from the tree:
  Sections 5.4 and 15.
- Floating status/mother/index branches:
  Section 7.
- PYTHIA's noninteractive CVMFS fallback can bind the library while omitting
  `PYTHIA8DATA`, causing a constructor to follow a stale build-time XML path:
  Sections 5.1, 16, and 19 require `xmldoc/Index.xml` and a runtime
  constructor smoke test.
- PYTHIA 8.315 `baryonNumberType()` is three times physical baryon number:
  Section 7.3 requires exact conversion and meson/baryon/antibaryon tests.
- `mother1()`-only and status-only origin:
  Sections 8 and 16.
- Parent-blind hard-carrier uniqueness can falsely demote repeated
  constituents of one multiply-heavy final parent, while an unextracted
  private matcher is only circularly tested:
  Section 8 requires parent-aware grouping and independent pure-graph tests.
- Trigger status selection is omitted while associate status is applied:
  Sections 10 and 16 require one common direct-primary base selector; the
  trigger-only hard-origin layer is intentional and separately tested.
- Both roles hard-coded above 1 GeV:
  Section 10.
- Incomplete/asymmetric central species and missing Xi-prime:
  Section 4.
- Particle/antiparticle averaging:
  Sections 4, 11, 18.
- Bc assigned to only one heavy sector:
  Sections 7.3, 8, 11, 12.
- One raw rescan per pair:
  Sections 11 and 13.
- The active status/merge/subsample scripts discover the first N or all
  available files and would accidentally admit/exclude reserve candidates:
  Sections 6.2, 13, 14, and 16 require one canonical manifest without
  replacing their working merge/partition algorithms.
- B0/Sigma_b output uses the B+ trigger ID:
  Sections 11 and 16.
- Undocumented identical-species factor 0.5:
  Section 12.
- OS/SS described as electric-charge or pure-background subtraction:
  Sections 12, 18, 22.
- Paul’s species/reference-meson ratio confused with an aggregated balancing
  family ratio or inclusive baryon/meson yield:
  Sections 12, 13, 18.
- Multiplicity definition confused with prompt/final/minimum-bias:
  Section 9.
- Inclusive ROOT percentile ranges can double-count the integer Nch boundary
  between adjacent Paul-style classes:
  Sections 2.1, 9.3, 13, and 16 require a unique discrete partition while
  preserving labels/order.
- Tune cards differ beyond the claimed mechanisms:
  Sections 5.2 and 18.
- Potentially ignored/misspelled tune setting:
  Sections 5.2 and 16.
- 100/200/200 candidate jobs confused with analyzed statistics:
  Section 6.
- Nonempty corrupt files skipped:
  Sections 6.4, 15, 16.
- Seed uniqueness cannot be proved from outputs:
  Sections 6.3, 7.1, 15.
- The legacy 100M logs do not prove all 300 seeds and the ROOT files lack seed
  metadata:
  Sections 2, 6.3, 7.1, and 13 keep that sample regression-only rather than
  retroactively claiming provenance.
- Central and subsample definitions diverge:
  Sections 9.3, 13, 14.
- Integer associate-origin categories lacked an immutable label contract and
  could be silently reinterpreted by downstream sensitivity projections:
  Sections 12--15 require exact schema/label metadata and central/block
  closure.
- Block standard deviation was previously used as the final error, nonlinear
  ratio errors were inconsistent, and independent tunes were mishandled:
  these are resolved on `7f17356`; Sections 2.1, 3, 14, and 17 require reuse
  and regression validation, not another rewrite.
- Absolute paths, inconsistent plotting configurations, uninitialized pads,
  missing input checks, and placeholder/disabled errors:
  these are resolved on `7f17356`; Sections 2.1, 3, and 17 require integrating
  and preserving that work.
- Paul’s plotting JSON exposes pT/eta fields and stable main applies them to
  both the correlation and trigger-normalization projections:
  Sections 2.1, 10, 13, and 17 preserve that exact path in the sole
  `legacy-regression` mode, prohibit an invented “corrected legacy” fork, and
  require canonical v2 plotting to validate its upstream selection metadata
  without recutting.
- Paul’s finite THnSparse pT/multiplicity axes can create undocumented upper
  cuts if overflow is populated:
  Sections 2.1, 12, 15, and 16 require measured overflow accounting and a
  change only when necessary.
- The strict `7f17356` audit found 610 legacy observables without ten finite
  subsample values:
  Sections 2.3, 6, 14, 16, and 17 preserve the failure, make it a
  production-sizing gate, and prohibit promoting smoke-only coverage
  exclusions.
- The structurally complete legacy production can be mistaken for a
  statistically complete paper sample:
  Sections 2.3, 14, and 15 distinguish file/object/union integrity from
  per-observable ten-block coverage.
- Paul-compatible stable `main` can be displaced by a parallel rewrite or by
  treating a hardening branch as the scientific source of truth:
  Sections 2.1--2.2, 3, 13, and 17 require minimal adapters, executable
  regressions, and a documented burden of proof for every numerical change.
- `7f17356` removed and inventoried stale tracked generated plots:
  Sections 2.1, 3, 17, and 20 prohibit restoring them while preserving user
  data and paper figures.
- Paper says prompt/weak-stable/all-final while code differs:
  Sections 1, 5.3, 18.
- Paper tune descriptions, captions, labels, and bibliography are stale:
  Section 18.
- Paper results/summary/placeholders are incomplete:
  Section 18.
- Active `Results.tex` graphics lack a mechanically complete
  figure-to-generator/config/input/output provenance map and include stale
  color/beauty-caption language:
  Sections 17--19 require one-to-one provenance and regenerated validated
  replacements.
- Full ROOT plotting can terminate or degrade through accumulated temporary
  object ownership even when smoke succeeds:
  Sections 3, 16, and 17 preserve the validated memory cleanup and require a
  completed full run.
- Active paper citations and bibliography sources are incomplete or
  nonportable:
  Section 18.
- Working paper is untracked and not commit-reproducible:
  Sections 2, 18, 19.
- Existing legacy 100M support is at risk:
  Sections 2, 3, 13.
- Repository contains overlapping stale and legacy pipelines:
  Section 20.
- A checksummed JSON `PASS` or `/usr/bin/true` command could previously satisfy
  a launch gate:
  Section 16 now requires exact implementation, command, log, result, and
  finding semantics and live-origin reachability.
- Rendered Condor text and a terse cluster ID could previously be trusted
  without proving what was held:
  Sections 6.4 and 16 require immutable raw ClassAds, exact process/argument
  coverage, and verified held-state release.
- A stale Gate-D storage report could authorize a later claim while retained
  partials consumed the reserve:
  Sections 6.4 and 16 require live filesystem/identity/arithmetic rechecks at
  every claim, evidence record, retry, and release.
- A selector Boolean could previously self-assert publication eligibility:
  Section 17 requires separate exact-byte scientific-review and project-owner
  authorizations and rejects template or empty evidence.
- Whole-file hashing of an append-only seed ledger made a valid retry
  invalidate an expansion authorization:
  Sections 6.2--6.3 bind the immutable initial prefix and validate every retry
  suffix instead.
- Superseding v3 manifests were not accepted consistently by merge, analysis,
  and final plot consumers, and arbitrary reserve selection or chained
  expansion could alter the sample:
  Sections 6.2, 13--17 require lowest-valid deterministic selection, atomic
  chained union promotion, exact leaf hashes, dynamic `N`, and unbounded
  decimal slot names.
- Stored multiplicity fractions and a multi-class 0--10% request could pass
  without recomputation or exact union:
  Section 9.3 requires source-histogram recomputation and contiguous,
  disjoint frozen-class unions.
- Fixed-Nch and pTHat numerical margins were implementation proposals rather
  than owner-approved scientific conventions:
  Sections 9.3, 16, and 23 bind their frozen specifications and keep
  publication promotion review-blocked until named scientific review.
- A final log-axis range could clip the lower error extent while the point
  remained visible:
  Section 17 requires a finite positive error envelope and rejects clipping.
- Thesis inconsistencies (prompt terminology, hard-origin assumption,
  status/multiplicity mismatch, 0.5 factor, and block-SD errors):
  Sections 1, 8, 9, 12, 14, and 18.

If a previously observed defect is absent from this checklist, add it and map
it to an implemented requirement before declaring the specification
fulfilled.
