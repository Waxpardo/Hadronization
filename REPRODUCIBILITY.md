# Reproducing the publication analysis

What must be true for a number from this repository to be reproducible, and
how each of those things is enforced.

For *how to run* the pipeline see [`README.md`](README.md),
[`Condor_README.md`](Condor_README.md), [`docs/WORKSPACE.md`](docs/WORKSPACE.md)
and [`docs/NIKHEF_BRINGUP.md`](docs/NIKHEF_BRINGUP.md). For *why* each physics
choice is what it is, see
[`docs/DESIGN_AND_RATIONALE.md`](docs/DESIGN_AND_RATIONALE.md).

## 1. Fixed scientific contracts

The central selector is
`hard_trigger_primary_ground__primary_ground_associate_v1`.

- collisions: pp at 13.6 TeV (LHC Run 3);
- PYTHIA: 8.317, stock upstream, built from the official pythia.org tarball
  (`sha256 1ae551d1...45adf`), unmodified, `-std=c++20`;
- ROOT: 6.30/01 ALICE CVMFS build (`root-config --version` reports `6.30.01`);
- processes: `HardQCD:hardccbar = on`, `HardQCD:hardbbbar = on`;
- central generator threshold: `PhaseSpace:pTHatMin = 2.0 GeV`, chosen so the
  sample is minimum-bias-like in charged multiplicity and the event-activity
  percentiles are interpretable (see
  `ValidationReports/PTHAT_MULTIPLICITY_SCAN_8317.md`);
- tunes: MONASH, JUNCTIONS, CLOSEPACKING as complete configuration bundles;
- raw schema: `hf_primary_ground_raw_v7`;
- origin algorithm: `signed_heavy_constituent_complete_mothers_unique_v4`;
- heavy-stability audit: `heavy_stability_audit_v2`;
- exhaustive effective settings: `effective_pythia_settings_exhaustive_v2`;
- tune allowlist: `pythia_tune_difference_allowlist_v2`;
- primary-all-heavy closure: `primary_all_heavy_constituent_match_v1`;
- trigger: signed registry state, direct primary, generator stable,
  hard-origin resolved, `pT > 1 GeV/c`, `|eta| <= 4`;
- associate: signed registry state, direct primary, generator stable, any
  origin, `pT > 0.15 GeV/c`, `|eta| <= 4`;
- central multiplicity: `NCH_PRIMARY_CHARGED_ETA10_V1`;
- cross-check multiplicity: `NCH_PRIMARY_CHARGED_ETA40_V1`;
- multiplicity definition: `primary_charged_light_hadron_level_v1`;
- pair construction: ordered conditional pairs, self-pairs excluded,
  `same_sign_pair_factor = 1.0`;
- statistics: ten disjoint **FILE** blocks, `block = canonical_slot % 10`
  (`tools/build_canonical_manifest.py`), every nonlinear quantity formed
  **inside** a block; **central value from the pooled union**, uncertainty =
  **SEM across the ten block estimators**; `conservative_degrees_of_freedom = 9`.

> **CORRECTED 2026-08-13 (review findings A3 and A10).** This line previously
> said "`event_id`-modulo blocks" and "before averaging". Both were wrong.
>
> **Blocks are FILE/JOB blocks, not event-ID blocks.** Each job processes every
> event in its assigned input file; the event-modulo filter is off by default
> (`run_status_analysis.sh`: modulo 0, remainder −1). File blocking retains
> job-level effects as **between-block scatter** rather than distributing them
> across all ten, which makes it the **conservative** choice — and it is the one
> implemented. A third party following the old text would build different blocks
> and could obtain different errors from identical data.
>
> **The published central value is POOLED, not the mean of block ratios.**
> `analysis/Analysis_README.md` says so explicitly ("They are not the mean of
> block estimators"), `extraction/aggregate_m7.py` pools its counts, and the
> plotter computes the pooled yield; the top-level contract disagreed with all
> three. With unequal block denominators the two estimators genuinely differ, so
> the ambiguity was not cosmetic. `decompose_with_block_sems.py` prints both, so
> a material divergence is visible rather than assumed absent.

Trigger requires hard-origin ancestry and the associate does not. That
asymmetry is deliberate: requiring both would delete the same-sign term by
construction. Ambiguous origin is never tie-broken -- it becomes
`kUnresolved` and is dropped, because a permissive tie-break would bias the
tune comparison itself.

Heavy flavour is signed by **quark content, not charge**: `q_c = n_c - n_cbar`.
`B+` (521) has `q_b = -1` while `Lambda_b0` (5122) has `q_b = +1`, so they are
an opposite-sign pair. This is easy to get backwards.

## 2. What makes a run reproducible

Five things are pinned, and each is checked rather than assumed.

**The generator.** `setupEnv.sh` asserts `pythia8-config --version` against
`HF_PYTHIA8_VERSION` and `root-config --version` against `HF_ROOT_VERSION`, and
exports nothing on a mismatch. A CVMFS package path used to encode its own
version; a locally built prefix does not, so a rebuild in place could otherwise
change the generator while every recorded string stayed byte-identical.
`Validation/ValidateRawOutput.C` re-checks the version recorded in each raw
file against the same pin -- it previously hardcoded `8.315` and kept demanding
it after the migration, which nothing caught until a job was actually run.

**The code.** Every job records the commit it was submitted against and
refuses to run if the checkout has moved or has tracked modifications.

**The binary.** The producer's SHA-256 is recorded at submission and re-checked
by the worker. A rebuild between submission and execution stops the job.

**The configuration.** The card the worker actually runs is materialised from
the tracked card plus the requested event count, and its SHA-256 must match
what the submit file recorded. A job cannot silently run a configuration
nobody queued.

**The seeds.** `seed_for(campaign_ordinal, tune, job, attempt)` is
deterministic, so the same command always produces the same submit file. A
ledger records every burned seed and rendering refuses to reuse one -- a real
duplicate-seed collision once voided two pilot campaigns.

**Derivation version: `seed_derivation_v2`, from 2026-08-09.** The formula is

```
seed = SEED_BASE + ordinal*CAMPAIGN_STRIDE + tune*TUNE_STRIDE
     + attempt*ATTEMPT_STRIDE + job_index
```

with `SEED_BASE = 100_000_001`, `CAMPAIGN_STRIDE = 10_000_000`,
`TUNE_STRIDE = 1_000_000`, `ATTEMPT_STRIDE = 100_000`. Campaign ordinals are
capped at **79**, derived from PYTHIA's `1 .. 900000000` seed domain, and an
ordinal past the cap **raises rather than truncating**.

**Why it changed.** **v1 had no campaign term**: `seed_for(tune, job, attempt)`
gave every campaign at attempt 0 the same sequence from `SEED_BASE`. It stayed
latent because each campaign quietly advanced the *attempt* index instead —
HF_SMOKE at 0, HF_SMOKE2 at 1–3, HF_PT2 at 4–5, HF_PT2_INT at 6–7 — which
consumed **eight of the ten** slots reserved for hang retries. The next campaign
rendered at attempt 0 collided; `assert_seeds_unused` refused it at render
before anything was burned. **v2 makes campaigns disjoint by construction and
returns the attempt axis to retry-only use.** Full record: `RELEASE_BLOCKERS.md`
B15b.

**Reading historical campaigns.** Ordinals 1 and 2 (HF_SMOKE through
HF_PT2_INT) were drawn under v1. **Nothing re-derives their seeds** — every
consumer reads the recorded seed from `attempt_metadata`, so their provenance is
unaffected by the change.

## 3. Provenance recorded per job

- `attempt_metadata/<TUNE>/*.json` -- one per attempt started: seed, requested
  successes, commit, card and binary checksums, producer exit, elapsed time.
- `raw_validation/<TUNE>/jobNNN/attemptNNN/receipt.json` -- validator verdict,
  output and log checksums.
- `raw/<TUNE>/hf_<TUNE>_jobNNN.root` plus a `.sha256` sidecar -- one per
  success.

`tools/campaign_status.py` reconstructs the whole campaign from these alone,
so the accounting cannot drift from what actually happened.

## 4. Known limits on reproducibility

- **The PYTHIA install is a personal directory.** The tarball checksum is
  recorded but nothing rebuilds it automatically. A third party must build
  PYTHIA themselves; there is no container.
- **The junction hang is not reproducible.** 1M events on 8.315 with a
  byte-identical card and the exact seed of a job that hung did not hang.
  Identical inputs, different behaviour. The mechanism is unexplained; the
  remaining untested hypothesis is node dependence.
- **Discarded jobs are a non-random loss.** The hang occurs on dense-junction
  topologies, which are exactly the configurations under study, and PYTHIA
  cannot generate those events at all. The discard rate must be reported, not
  corrected away.

## 5. Open questions that block publication

1. **Systematics — nothing is computed, and nothing is applied.**
   `Validation/MeasureUnresolvedSystematic.C` **exists**, but **no recorded run
   and no artifact exists**, and **no systematic uncertainty is computed or
   propagated anywhere in the analysis.** PDF and scale variation are not
   addressed either. **The tool is not the measurement.**

   *Corrected 2026-08-08.* This entry previously read "The `kUnresolved`
   systematic is measured", which asserted a result from the existence of a
   macro. It now agrees with `docs/NIKHEF_BRINGUP.md` — *"No systematic
   uncertainties are computed anywhere. The unresolved-fraction sensitivity is
   tune-dependent and currently unpropagated"* — which was the accurate
   statement all along. *Method: the macro's mentions across `*.md`/`*.json`/
   `*.txt` are prose only; there is no `ValidationReports` entry and no
   artifact.*
2. **The tune-bundle confound.** JUNCTIONS retunes the parameters that set
   baryon production, so a MONASH-vs-JUNCTIONS difference in a baryon
   observable cannot be attributed to junction formation alone.

## 6. What a full production run costs

**Measured 2026-08-04** from `condor_history` over the 292 completed jobs of
campaign **HF_PT2_INT**, cluster **5319282** — 100k events per job, PYTHIA
8.317, the same producer binary full production will use. Scaled to the
configured full-production shape, `JOBS = 1000` per tune at
`EVENTS = 100000` (`Makefile:25-26`).

| Tune | measured mean CPU/job | CPU-hours at 1000 jobs |
|---|---|---|
| MONASH | 377 s | 104.7 |
| JUNCTIONS | 659 s | 183.1 |
| CLOSEPACKING | 989 s | 274.7 |
| **Total** | | **562.5 CPU-hours** |

**Quote 562.5, not 390.** The 390 figure has circulated verbally and appears
nowhere in the tracked tree, so there has never been anything to correct in
place — which is precisely how it survived being wrong. It descends from the
older per-job medians of **247 / 480 / 677 s**, which understate the measured
means by 1.4–1.5x.

*Cross-reference corrected 2026-08-08.* This previously said those medians were
"still quoted at `Makefile:35-37`". **Both halves were stale.** The medians were
superseded in the Makefile by commit `82285ae`: `Makefile:41-46` now carries the
measured means, states that they supersede the old medians, and points back at
this section. `Makefile:35-37` is the `ORDINAL` block; the guard comment is
`Makefile:38-53`.

**Excludes retry overhead.** 2.7 % of jobs hit the hang guard and must be
regenerated (`RELEASE_BLOCKERS.md`, B7), converging in two to three rounds,
so budget a few percent on top of the figure above.

## 7. What is not publication evidence

None of the following is evidence that a result is sound:

- a dirty or `--development` report;
- a historical raw-v3/v4/v5 pilot;
- a validation receipt whose state is FAIL;
- a user-created JSON with no semantic/log validation;
- a nonempty ROOT file without its receipt;
- a Condor queue reaching zero;
- 500 submitted jobs described as 500M analyzed events;
- a smoke-only plot;
- the legacy `21_06_2026` full-config failure;
- an agent-authored physics sign-off.

## 8. Nikhef path consolidation

On 2026-08-20 the project's Nikhef trees moved from
`/data/alice/ipardoza/<name>` to `/data/alice/ipardoza/hf/<name>` (with run,
deploy, scratch, and archive material grouped below `hf/project/`). Runtime
selectors and unpinned plotting configurations use the new roots.

Receipts, anchors, and history artifacts deliberately retain the absolute paths
that were true when their inputs were read. Those pre-move paths are provenance,
not runtime resolvers. A same-filesystem move does not change file content, so
their recorded content digests remain valid. In particular, do not rewrite an
old receipt merely because its recorded path no longer exists.
