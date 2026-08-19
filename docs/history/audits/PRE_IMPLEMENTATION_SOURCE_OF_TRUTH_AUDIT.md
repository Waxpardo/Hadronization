# Pre-implementation source-of-truth audit

**Audit date:** 2026-07-30
**Implementation branch:** `full-production`
**Clean worktree:** `/private/tmp/hadronization-full-production`
**Scope:** central publication mode
`hard_trigger_primary_ground__primary_ground_associate_v1`

This report freezes the evidence and change budget before implementation. It
does not certify the legacy production for publication. Relationships below
are marked **confirmed**, **inferred**, or **unknown**.

## 1. Immutable starting state and protected inputs

| Item | Audited state |
|---|---|
| Live `origin/main` and implementation base | `11884cf1ad3613e8e6997bbff32d48a3e7d89570` |
| Paul's post-subsampling commit | `10a6f098f80730374d9f827bfdf3ae97a928a030`; confirmed ancestor of live `origin/main` |
| Dirty local `main` | `39c9cf22a723d623cc88ea683a5ea771ee98ea1c`; protected and unmodified |
| Nikhef canonical `main` | `/data/alice/ipardoza/Hadronization`, clean at `11884cf1ad3613e8e6997bbff32d48a3e7d89570` |
| Protected Nikhef seed checkout | `/data/alice/ipardoza/Hadronization-main`, `codex/nikhef-seed-condor-ready-20260724` at `758a53696805231205c6adb027ff4c8cbdf12386`; read only |
| Plot-hardening source | `codex/final-paper-plotting-20260729` at `7f1735656d344887b2d60a3780e8a993898caaf6` |
| Attached instructions SHA-256 | `b254e4b37edd9afbcf609d3508ed9d7f8df6c3251096d8cac9cde5acd13d28ca` |
| Protected modified bibliography SHA-256 | `9915952201459a5bd1f863b6be51c6053b0a55cea041e3e40bd0b2df515c7f48` |
| Working-paper copy | 166 files, copied byte-for-byte from the protected local worktree before editing |

The original modified `Literature/References.bib` and untracked
`Paper/Heavy_flavour_hadronisation_model_paper/` remain untouched. Their
copies in this worktree are intentional paper inputs.

Nikhef's configured GitHub deploy key cannot fetch the repository
(`Permission denied to deploy key`). A read-only fetch from the public HTTPS
URL successfully updated the remote-tracking reference used to fast-forward
only the new worktree. The canonical and protected checkouts were not reset or
modified.

## 2. Evidence hierarchy and active contract

The authority order for this implementation is:

1. the owner-approved observable in
   `PUBLICATION_READY_CODING_AGENT_INSTRUCTIONS.md`;
2. a uniquely determined physics/statistical correction supported by a
   derivation and executable test;
3. Paul's merged behavior on stable `main`;
4. current documentation and the plotting-hardening commit;
5. the thesis and older macros as legacy regression evidence only.

The confirmed consumer contract is:

```text
PYTHIA raw event record
  -> signed species-resolved, ordered OS/SS pairs
  -> 56 Paul-compatible ROOT pair files/tune/block
  -> complete-root central union + ten disjoint block inputs
  -> improvedPlotting_THnSparse.C
  -> paper figures and numerical review ledger
```

The compatibility writer must retain these object names and types:

- `summed MULTIPLICITY`: `TH1`;
- `hTrKinematics`: `TH2`;
- `hAsKinematics`: `TH2`;
- `hCorrelations`: `THnSparse`;
- existing signed pair filenames and `DeltaPhi` wrapping to
  `[-pi/2, 3pi/2)`.

The central scientific definition is a model-level primary-hadron observable:

- all heavy-hadron decays are disabled before generation;
- trigger and associate both satisfy the direct-primary ground-state registry
  and `abs(status) in [81,89]`;
- trigger additionally has an ancestry match to the configured hard heavy
  quark;
- associate origin is inclusive;
- trigger `pT > 1 GeV/c`, associate `pT > 0.15 GeV/c`, and both
  `|eta| < 4`;
- multiplicity counts direct-primary charged `pi`, `K`, `p`, `e`, and `mu`
  with `pT > 0.15 GeV/c` and `|eta| < 4`;
- particles and antiparticles remain separate;
- ordered conditional pairs exclude only the same event-record index.

The observable is per trigger, OS minus SS, integrated over full `DeltaPhi`.
In this ordered conditional definition no universal `0.5` factor applies to
the SS term. The legacy factor remains available only in an explicitly
labelled legacy mode.

## 3. Paper and thesis audit

### 3.1 Working paper

The complete copied paper was read, including `main.tex`, Introduction,
Observables, Model, Results, Summary, commands, bibliography, every caption,
and every `includegraphics` reference.

Confirmed publication blockers:

- `Results.tex` is still a proposed-figure list with placeholder prose,
  duplicate labels, stale thesis text, and conclusions not backed by a frozen
  production.
- `Summary.tex` is incomplete.
- the Model section states 100 million events per tune without a machine
  manifest proving the exact successful-event set.
- “prompt” and “final” are used where the implemented definition is actually
  a PYTHIA event-record status selection.
- legacy captions state stale tune colours and at least one beauty caption
  describes charm species.
- current figures do not have a complete generator/config/input/output
  provenance map.
- some statements treat association as causal balancing or treat LS as
  physical background; the code establishes neither interpretation.
- the bibliography contains machine-specific Zotero attachment paths and
  requires duplicate/reference-integrity review.

The paper must be rewritten only after validated outputs exist. Until then,
claims and figures are regression material, not final results.

### 3.2 Thesis, explicitly legacy

`Literature/pveen_*.pdf` was text-extracted and pages covering the observable,
multiplicity, and thesis results were rendered and visually inspected.
Confirmed useful legacy conventions are the per-trigger yield, full-azimuth
integration, signed OS/SS comparison, and baryon/reference-meson ratio.

The thesis is not authoritative for the central publication because it:

- calls status-selected particles “prompt”;
- treats LS as background without proving that interpretation;
- uses a different charged-multiplicity wording;
- applies trigger-like `pT` cuts to associates;
- reports subsample standard deviations rather than the required SEM;
- contains earlier limited species and tune coverage.

## 4. Documentation and operational audit

All repository README and operational documents were read. Confirmed
contradictions include:

- `README.md`, `AnalysisScripts/README.md`, `Condor_README.md`,
  `SimulationScripts/README.md`, `PlottingScripts/README.md`,
  `plotting_documentation.md`, `FinalAnalysis/README.md`, and
  `PtMultiplicity/README.md` describe multiple partially overlapping
  pipelines without one immutable central-mode run manifest.
- the smoke/complete-root plotting target is described as running without
  subsampling even though its checked-in configuration requests errors.
- old documentation still points to `improvedPlotting.C` and describes
  `1e-10` placeholder errors.
- production instructions describe time/PID seed mixing and discovery-based
  job selection.
- analysis and merge defaults include Paul-specific absolute paths.
- legacy pT/multiplicity and charge-combined macros are not clearly separated
  from the current THnSparse paper path.

These documents must be updated from generated manifests and executable
commands, not by copying legacy prose.

## 5. Producer and tune-card audit

### 5.1 Current producer

`SimulationScripts/heavyflavourcorrelations_status.cpp` was read completely.
Confirmed defects:

- seed = time + process ID + two caller values modulo the PYTHIA range;
- the event loop counts attempts, not successful `pythia.next()` calls;
- events with no stored selected particle do not get a tree entry;
- status, identity, and ancestry indices are stored as floating-point vectors;
- only `mother1` and its PDG ID are retained, preventing a reliable full
  ancestry audit;
- only a hand-listed subset of heavy hadrons and pions is stored;
- no run/tune/job/seed/config/weight/success/attempt metadata is written;
- decay disabling depends on incomplete tune-card lists;
- the producer has no machine-readable stabilization audit.

These are reproducibility or selector defects and require a new compatible raw
contract; documentation alone is insufficient.

### 5.2 Protected deterministic-seed commit

Commit `758a536` was inspected read-only. Its `SeedUtils.h` removes time and PID
mixing and hashes two inputs with SplitMix64. This is an improvement but is not
the final contract: `runCondorJob.sh` still derives inputs from Condor cluster
ID and retry attempt. The same logical job therefore changes seed across a
new submission campaign or retry. The seed hash is also not accompanied by a
complete collision-tested production manifest.

### 5.3 Combined-heavy tune cards

The MONASH, JUNCTIONS, and CLOSEPACKING cards all configure 14 TeV pp,
hard-ccbar and hard-bbbar production, `pTHatMin = 1`, and the same nominal
proper-time limit. The tune bundles intentionally differ.

Confirmed problems:

- their explicit `mayDecay = off` lists are incomplete for the operational
  ground-state registry;
- settings equality outside the declared tune bundle is not machine-audited;
- the CLOSEPACKING card contains a capitalization spelling that must be
  checked against `Settings::isParm`/PYTHIA warnings rather than assumed;
- no canonical configuration digest is embedded in output.

The central producer will disable all heavy-hadron decays programmatically
and audit every affected ParticleData entry after card loading.

## 6. Pair analysis, merging, blocks, and plotting

### 6.1 Pair analysis

`AnalysisScripts/status_analysis_THnSparse_qq.C` was read completely.
Confirmed defects:

- the raw tree is reopened and rescanned once for every pair file (56 passes);
- trigger direct-primary status selection is commented out;
- trigger hard-origin matching is absent;
- associate threshold is `pT >= 1 GeV/c`, not the central definition;
- species registry is incomplete;
- two B0/Sigma entries use trigger PDG 521 instead of 511;
- percentile boundaries can overlap because integer values are reused with
  inclusive range calls;
- `pT=50` and `Nch=400` axis maxima can silently overflow;
- the raw float identity/status branches prevent exact integer semantics.

The replacement must scan each raw event once while emitting the same
Paul-compatible pair filenames and objects.

### 6.2 Merge and block scripts

`merge_root_files.sh` and `make_subsamples.sh` enumerate discovered directories
and infer the file set from a first usable job. That is unsuitable for a
frozen final campaign because an extra, missing, stale, or partially analyzed
directory can silently alter the union. Central and block merges must consume
an explicit validated manifest and fail closed on missing/extra inputs.

`run_status_analysis.sh` defaults to a user-specific checkout and copies
unscoped current-directory outputs. It needs a central-mode manifest-aware
entry point.

### 6.3 Paul's plotting path

Stable `main` contains grouped triggers, `TriggerToUse`, multiple charm and
beauty triggers, all three tunes, config-driven mini/global canvases,
OS-minus-SS construction, combined yield canvases, and
baryon/reference-meson canvases. This architecture is preserved.

Confirmed stable-main defects:

- the full JSON contains a `/Users/...` base path, a stale central tag, and
  `calculate_errors=false`;
- four drawing paths use `1e-10` placeholder errors;
- four optional `TPad*` values are uninitialized;
- central and subsample calculations contain an unconditional SS factor
  `0.5`;
- some tune-ratio styling falls back to stale/hard-coded colours;
- full-production uncertainty coverage is not enforced before promotion.

The `7f17356` branch provides validated portability, strict input/object and
coverage checks, SEM and ratio propagation, pointer safety, tune styling,
provenance, and generated-artifact policy. Those changes will be ported
selectively and re-regressed against this central mode. Its successful smoke
run is not evidence of full coverage.

## 7. Legacy production inventory and limitations

Read-only Nikhef inventory:

| Tune | Raw files | Raw size | Central pair files | Ten block directories |
|---|---:|---:|---:|---:|
| MONASH | 100 | 104.64 GiB | 56 | 10 x 56 |
| JUNCTIONS | 100 | 113.79 GiB | 56 | 10 x 56 |
| CLOSEPACKING | 100 | 106.89 GiB | 56 | 10 x 56 |

Each tune's ten `jobs_used.txt` files contain 100 unique job-directory names,
each exactly once. This confirms a disjoint legacy partition by directory
name. It does not prove reproducible seeds, exact successful events, uniform
settings, or the central selector.

The existing production is about 327 GiB raw, 87 GiB in work areas, and 6 GiB
analyzed. `/data/alice` is 97% full with about 1.1 TiB available. A new
campaign must not be submitted until pilot-measured output size plus a safety
margin fits and a retention/staging plan is recorded.

The previously audited plotting-hardening run found 610 configured legacy
observables without ten finite subsample estimates. The reduced smoke
selection proved that error bars work when all ten estimates exist; it did not
establish full-paper statistical coverage.

## 8. Installed runtime evidence

The login node is not a valid execution environment: `alienv` fails there with
`Cannot initialize TCL`, and ROOT/Condor are unavailable. The Stoomboot submit
host `stbc-i3.nikhef.nl` is the execution authority:

- HTCondor: `/bin/condor_submit`;
- ROOT: 6.30.01 from the ALICE CVMFS package;
- PYTHIA: 8.315 from the ALICE CVMFS package;
- `setupEnv.sh` succeeds on that host.

Installed PYTHIA 8.315 evidence confirms:

- `Particle::statusAbs()` and `isFinal()` semantics in `Event.h`;
- status 81--89 means primary hadrons produced by hadronization in
  `ParticleProperties.xml`;
- status 91--99 covers decay/Bose--Einstein products;
- `motherList()` is available for full ancestry traversal;
- `ParticleData::mayDecay()` and `setMayDecay()` are available;
- `Info::nTried()`, `nAccepted()`, `code()`, and weight accounting are
  available.

The implementation must record these runtime versions and config digests in
each output and campaign manifest.

## 9. Contradiction and decision ledger

| Topic | Existing behavior | Decision | Status |
|---|---|---|---|
| Trigger selector | status cut commented out | require registry + abs(status) 81--89 | correctness defect |
| Trigger origin | no ancestry requirement | require configured hard-heavy ancestor | correctness defect; ancestry test required |
| Associate origin | inclusive | retain inclusive origin | owner-approved |
| Associate threshold | 1 GeV/c | use strict `>0.15 GeV/c` | owner-approved definition change |
| Pair ordering | ordered trigger-to-associate | retain | Paul-compatible |
| Self pair | possible only by index equality | exclude same event-record index | owner-approved |
| SS factor | unconditional `0.5` | remove in central mode; preserve explicit legacy mode | derivation + toy test required |
| “B/M ratio” | one species yield / configured reference-meson yield | retain calculation; rename precisely | standardization |
| Errors | mixed placeholders/partial subsampling | 10 disjoint blocks; sample SD/sqrt(10) | statistical requirement |
| Tune ratio | tune numerator / common denominator | independent-tune quadrature; numerator style | statistical/style requirement |
| Multiplicity bins | inclusive range ambiguity | discrete exhaustive non-overlapping classes | correctness test required |
| Axes | hard maxima 50 and 400 | measure overflows, then expand/fail | unresolved until pilot |
| Failed events | reduce output event count | generate until exact successful count | reproducibility requirement |
| Event weights | not stored/checked | store and verify; define weighted handling before promotion | unresolved until pilot |
| Empty events | no tree entry | one entry per successful event | reproducibility requirement |
| Seeds | time/PID or Condor identity | run/tune/job deterministic mapping + collision audit | reproducibility requirement |

No unresolved convention may be silently promoted. Where a pilot exposes
non-unit weights, overflow, unexpected hard-origin topology, or an ambiguous
ParticleData classification, final production is blocked until the definition
is explicitly resolved.

## 10. Approved change budget

Only the following components may be changed before a budget amendment is
recorded here.

| Component | Required change | Why an adapter/doc-only fix is insufficient | Regression/acceptance |
|---|---|---|---|
| `SimulationScripts/heavyflavourcorrelations_status.cpp` and new focused headers | exact-success loop, integer/raw metadata, full ancestry/origin fields, programmatic heavy-decay disabling, complete registry, weights and overflow counters | source event contract is incomplete | unit tests, two-repeat hash test, tiny three-tune pilots, ROOT schema audit |
| three combined-heavy `.cmnd` cards | remove incomplete decay responsibility; validate only declared tune differences/settings | ignored/unknown settings can change physics | PYTHIA settings audit and cross-tune diff |
| `SimulationScripts/Makefile` | build central producer/tests reproducibly | current targets do not cover new helpers | clean compile with warnings |
| `runCondorJob.sh`, a new canonical submit template, manifest/seed tools | logical-job deterministic seeds, immutable run IDs, atomic validation/promotion | Condor IDs/retries are not scientific identifiers | collision test; same logical job byte/content reproducibility; retry test |
| `AnalysisScripts/status_analysis_THnSparse_qq.C` or a compatibility replacement | one-pass central selector, complete registry, fixed pair map, overflow accounting, unchanged object contract | legacy selector and scale are scientifically wrong/impractical | toy pairs; legacy compatibility mode; representative ROOT comparison |
| `run_status_analysis.sh`, `merge_root_files.sh`, `make_subsamples.sh` and validation helpers | consume a frozen manifest and ten declared blocks; fail closed | discovery changes the dataset silently | missing/extra/duplicate tests; central=block-union checks |
| `PlottingScripts/improvedPlotting_THnSparse.C`, two paper JSON files, `TunePlotStyle.h`, runner and validators | central-mode no-0.5 behavior, strict ten-block SEM, ratio propagation, portable inputs, null pads, styles, complete coverage gate | plotting must know statistical mode and reject unsupported outputs | four-path toy/ROOT tests; smoke and full verbose audits |
| `.gitignore` and tracked stale `PlottingScripts/Plots/**` artifacts | adopt generated-output policy from `7f17356` | stale binaries currently masquerade as sources | exact removal inventory; no user-paper deletion |
| `setupEnv.sh` | document/enforce submit-host runtime and version logging | login and submit hosts differ materially | environment preflight on Stoomboot |
| paper TeX/bibliography and figure copies | replace placeholders/stale claims only from frozen reviewed outputs | publication claims are currently unsupported | clean build, link/citation/figure provenance checks, rendered visual review |
| repository READMEs and new reproducibility/provenance/audit documents | one exact central workflow, definitions, commands, manifests, limitations | current docs conflict | command lint; clean-room rehearsal from manifest |
| final architecture catalog and review reports | account for every file and each final claim/output | required audit evidence does not exist | discovered count equals classified count |

Legacy split-channel producers, old pT/multiplicity macros, exploratory plots,
and unrelated literature files are read-only unless a final paper figure is
proven to depend on them. Any additional edit requires an explicit amendment
to this table with its defect and test.

## 11. Pre-implementation gate

The branch/worktree safety gate passes. The scientific implementation gate is
open only for the budgeted changes above. Full HTCondor submission remains
closed until:

1. static/unit tests and settings/stability audits pass;
2. deterministic tiny repeats pass for all three tunes;
3. pilot outputs prove schema, selectors, exact success counts, unit-weight
   treatment, no material overflow, and estimated storage/runtime;
4. the one-pass analysis and plotting smoke tests pass;
5. the measured storage plan fits safely within Nikhef capacity.
