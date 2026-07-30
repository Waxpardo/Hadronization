# Nikhef HTCondor production

This document covers the immutable publication workflow. Historical
`submitCondor_*.sub`, `runCondorJob_legacy.sh`, `RootFiles/`, and `Jobs/`
remain available for regression only. They use discovery, seed modifiers, and
retry conventions that are not accepted for new publication production.

See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for the complete gate sequence.

## Execution location

Canonical source checkout:

```text
/data/alice/ipardoza/Hadronization
```

Use a separate clean, commit-pinned execution checkout for gates and
production. Do not treat
`/data/alice/ipardoza/Hadronization-main` as canonical `main`, and do not
overwrite an old dirty `Hadronization-full-production*` checkout.

Run `condor_submit`, `condor_q`, and `condor_history` from a Stoomboot
interactive node such as `stbc-i2`, not from the login node:

```bash
ssh stbc-i2
condor_version
condor_q ipardoza
```

The shared `/data/alice/ipardoza` filesystem is visible to workers. It is NFS,
so avoid large directory discovery and many concurrent merge scans. The latest
2026-07-30 read-only `statvfs` snapshot, at
`2026-07-30T17:39:21+02:00`, found capacity `36,688,187,162,624` bytes and
`f_bavail = 1,671,602,503,680` bytes. The mandatory 5% reserve was
`1,834,409,358,131` bytes, so the filesystem was already short by
`162,806,854,451` bytes (about 151.7 GiB) before allocating any new data.
Consequently Gate D/E storage authorization was blocked at that snapshot.
This state is volatile: recheck `df -h /data/alice` and obtain the fresh
Gate-B/Gate-D measured storage evidence before every launch, but do not treat
the approximate free-space display as sufficient headroom.

The launch gate does not rely on this manual observation alone. Gate D stores
`hf_gate_d_storage_projection_v1`, using `os.statvfs(...).f_bavail` on each
actual production/analysis filesystem. Both its preparation snapshot and
fresh finalization recheck must pass: projected use is no more than 70% of
currently available bytes and projected remaining space is at least
`max(5% of capacity, 500 GiB)`. The finalized report must set
`state=PASS` and `gate_e_storage_authorized=true`.

## Publication submit contract

`tools/render_production_submit.py` renders:

- `getenv = False`;
- one CPU;
- bounded requested memory and disk;
- `+UseOS = "el9"`;
- a quoted mandatory `+JobCategory`;
- `should_transfer_files = NO`;
- `max_retries = 0`;
- hold on signal or nonzero exit.

The worker interface is:

```text
runCondorJob.sh --campaign CAMPAIGN CAMPAIGN_ORDINAL TUNE LOGICAL_ID \
  ROLE ATTEMPT SEED REQUESTED_SUCCESSES PTHAT_OVERRIDE \
  MULTIPLICITY_AUDIT_EVENTS REPOSITORY_COMMIT EFFECTIVE_CARD_SHA256 \
  PRODUCER_EXECUTABLE_SHA256 [CLUSTER_ID] [PROCESS_ID]
```

Never invoke it by constructing values manually for publication. The
immutable campaign renderer supplies every argument.

The active producer contract is:

```text
hf_primary_ground_raw_v5
signed_heavy_constituent_complete_mothers_unique_v4
heavy_stability_audit_v2
effective_pythia_settings_exhaustive_v2
pythia_tune_difference_allowlist_v2
```

## Shared seed/submission registry

Every submitting checkout must use the same absolute registry root:

```bash
export HADRONIZATION_SUBMISSION_REGISTRY_ROOT=\
/user/ipardoza/.local/state/hadronization/submission_registry
```

Before the first new submission claim, create the reviewed immutable
`reservation_baseline.json` from every historical campaign with
`tools/build_submission_registry_baseline.py`. Historical failed, held,
abandoned, or overlapping campaigns remain burned. The submission tool
creates an append-only global claim before calling Condor and refuses an
overlapping campaign ordinal or seed range.

Do not copy a private `$HOME` registry between users or use a different
registry root in another checkout.

## Gate-B pilot submission

Generate the exact nine-row pilot campaign from a clean commit:

```bash
python3 tools/generate_gate_b_pilots.py \
  --campaign <GATEB_CAMPAIGN> \
  --campaign-ordinal <UNUSED_ORDINAL> \
  --seed-base <UNUSED_SEED_BASE>

python3 tools/campaign_manifest.py validate \
  campaigns/<GATEB_CAMPAIGN>
```

The manifest contains central 1,000,000-success, pTHat 0.5 GeV
100,000-success, and pTHat 2.0 GeV 100,000-success jobs for each tune.

Render and inspect:

```bash
./submit_gate_b_pilots.sh campaigns/<GATEB_CAMPAIGN> --dry-run
```

Submit from Stoomboot:

```bash
./submit_gate_b_pilots.sh campaigns/<GATEB_CAMPAIGN> --submit
```

The submitter requires a clean checkout at the manifest commit, a validated
shared registry baseline, a reproducible producer build, exact executable and
card hashes, and the nine manifest rows. It writes:

```text
Production/<GATEB_CAMPAIGN>/submit_gate_b.sub
Production/<GATEB_CAMPAIGN>/submission_receipts/
Production/<GATEB_CAMPAIGN>/condor_logs/<TUNE>/
```

Do not edit a pilot manifest after generation. Any implementation change
requires a new campaign name, ordinal, and seed interval.

## Full 100/200/200 candidate submission

Generate a new full campaign only after Gates A--D are ready to bind to the
same exact commit:

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

The candidate manifest contains:

| Tune | primary IDs | reserve IDs | total |
|---|---|---|---:|
| MONASH | 000--099 | none | 100 |
| JUNCTIONS | 000--099 | 100--199 | 200 |
| CLOSEPACKING | 000--099 | 100--199 | 200 |

Reserves replace documented invalid primaries; they do not increase the
canonical sample or permit result-dependent selection.

The historical `HF_100M_primaryGround_ccbb_v1` campaign is already reserved.
Do not regenerate, edit, or overwrite it under a new implementation.

Render and inspect:

```bash
./submit_full_production.sh \
  campaigns/<NEW_FULL_CAMPAIGN> --dry-run
```

`--submit` is additionally fail-closed on:

- clean checkout exactly matching `campaign.json`;
- a validated 500-row first-stage candidate/seed ledger, or the exact dynamic
  `5*A` expansion ledger declared as `A/2A/2A`;
- absolute shared registry and reviewed baseline;
- canonical `PHYSICS_ORIGIN_SIGNOFF.json`;
- canonical `FULL_PRODUCTION_GATE_AUTHORIZATION.json`;
- for an expansion, canonical
  `EQUAL_TUNE_EXPANSION_AUTHORIZATION.json` plus new child-specific origin and
  full-production authorization (parent approvals are not reusable);
- canonical PASS Gate A, Gate B, pTHat, Gate C, and Gate D reports at the
  campaign commit;
- unchanged producer executable and effective cards.

`PHYSICS_ORIGIN_SIGNOFF.json` is a mandatory, read-only project-owner decision
artifact with schema `hf_full_production_origin_signoff_v1`, decision
`APPROVE_FULL_PRODUCTION`, and `reviewer_role=project_owner`. It binds the
exact Gate-B report path/checksum/campaign/ordinal and all nine
tune/threshold-by-sector unresolved counts. With zero unresolved triggers its
exact treatment is `No unresolved trigger candidates were observed; no
special treatment is required.` With a nonzero result its exact treatment is
`Exclude unresolved triggers centrally; retain unresolved associates as a
reported origin category`, and it must bind a superseding Gate-B PASS.
`FULL_PRODUCTION_GATE_AUTHORIZATION.json` separately binds all gate evidence.
Both full-launch owner artifacts must be single-link mode-`0444` regular
files with real explicitly UTC, non-future owner timestamps. An agent cannot
create either approval.

If the original Gate-B report is `NEEDS_SIGNOFF`, there is an earlier,
separate owner-review step. The owner places a read-only
`hf_gate_b_physics_signoff_v1` at
`campaigns/<GATEB_CAMPAIGN>/GATE_B_PHYSICS_SIGNOFF.json`, binding the
original report SHA-256 and exact nonzero nine-sample unresolved table. Verify
it and create a distinct immutable superseding report with:

```bash
./resolve_publication_gate_b_signoff.sh --verify-only \
  Production/<GATEB_CAMPAIGN>/gate_b/gate_b_report.json \
  campaigns/<GATEB_CAMPAIGN>/GATE_B_PHYSICS_SIGNOFF.json

./resolve_publication_gate_b_signoff.sh \
  Production/<GATEB_CAMPAIGN>/gate_b/gate_b_report.json \
  campaigns/<GATEB_CAMPAIGN>/GATE_B_PHYSICS_SIGNOFF.json \
  Production/<GATEB_CAMPAIGN>/gate_b_resolved
```

This does not rewrite or hide the original `NEEDS_SIGNOFF` report and cannot
waive technical failures or pTHat findings. The later full-campaign
`PHYSICS_ORIGIN_SIGNOFF.json` remains mandatory and is not interchangeable
with this Gate-B-specific review file.

Only after explicit owner authorization:

```bash
./submit_full_production.sh \
  campaigns/<NEW_FULL_CAMPAIGN> --submit
```

The 500 submitted candidates are capacity, not analyzed statistics. The
first-stage canonical sample is frozen later at exactly 100 validated files
and 100,000,000 successful events per tune.

## Coverage-driven equal-tune expansion submission

An expansion is a new parent-bound immutable campaign. If the predeclared
coverage/precision report requires more statistics, choose additional `A` as
a multiple of ten in `[10,100]`; the candidate allocation is `A` MONASH,
`2A` JUNCTIONS, and `2A` CLOSEPACKING, while the accepted extension contains
exactly `A` validated files per tune. Generate it with:

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

Submission requires failed predeclared coverage/precision evidence, a fresh
child-bound storage PASS, a new child `PHYSICS_ORIGIN_SIGNOFF.json`, a new
child `FULL_PRODUCTION_GATE_AUTHORIZATION.json`, and a separate single-link
mode-`0444` `EQUAL_TUNE_EXPANSION_AUTHORIZATION.json` with schema
`hf_equal_tune_expansion_authorization_v1`. The latter binds the exact parent,
`A`, final `N`, candidate/campaign bytes, the immutable initial-allocation
prefix of the append-only seed ledger (byte count and SHA-256), evidence
hashes, owner identity, and UTC decision. Valid retry rows may be appended
after that prefix without invalidating the decision; mutation of the prefix or
an invalid suffix is fatal. An agent may verify but never create these
decisions.
Generate the two prerequisite machine artifacts with
`tools/generate_expansion_evidence.py`. It binds and evaluates the frozen
coverage matrix and inventories the sealed parent raw/analysis/analyzed-data
bytes before a live `statvfs` projection. Expansion authorization recomputes
those exact semantics and capacity; do not hand-author look-alike evidence.
Dry-run and submit through the same fail-closed wrapper:

```bash
./submit_full_production.sh \
  campaigns/<NEW_EXPANSION_CAMPAIGN> --dry-run
./submit_full_production.sh \
  campaigns/<NEW_EXPANSION_CAMPAIGN> --submit
```

Freeze the extension separately, then create a new superseding union with
`tools/canonical_manifest.py supersede`; never alter the parent. Exact
freeze/seal/supersede commands and evidence schemas are in
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md#executable-equal-tune-expansion-procedure).

## Worker staging and promotion

Each worker:

1. rejects inherited campaign-control environment variables;
2. validates the exact manifest/ledger/submission claim;
3. pins checkout commit, producer hash, and effective card hash;
4. claims the attempt start immutably;
5. writes to an attempt-unique partial directory;
6. runs the producer with the exact manifest seed;
7. validates the complete raw-v5 ROOT file;
8. records immutable validation log and receipt;
9. atomically promotes to:

```text
Production/<CAMPAIGN>/raw/<TUNE>/hf_<TUNE>_jobNNN.root
```

An existing valid stable file is revalidated and retained. A corrupt or
mismatched stable file is never treated as completed and is never silently
overwritten. An interrupted partial never enters a canonical manifest.

## Monitoring

Queue:

```bash
condor_q ipardoza
condor_q <CLUSTER> -af:j ClusterId ProcId JobStatus HoldReason
```

Idle diagnosis:

```bash
condor_q <CLUSTER>.<PROC> -better-analyze
```

History:

```bash
condor_history <CLUSTER> \
  -af:j ClusterId ProcId ExitCode RemoteWallClockTime ResidentSetSize
```

Inspect all three Condor streams and the immutable receipts:

```bash
find Production/<CAMPAIGN>/condor_logs -type f -maxdepth 3
find Production/<CAMPAIGN>/validation -type f -maxdepth 4
find Production/<CAMPAIGN>/submission_receipts -type f -maxdepth 2
```

Do not infer success from queue disappearance or a nonempty ROOT file. Require
the promoted stable path and matching `hf_raw_validation_receipt_v1`.

Do not remove historical jobs or another checkout's jobs merely because they
are held. `condor_rm` is an intentional destructive scheduler action and
requires an exact reviewed target.

## Retry and scheduler-loss recovery

Automatic retries and manually re-releasing a held or evicted publication
attempt that may already have started are forbidden. The submission wrappers
have one controlled initial-launch step: they submit each new cluster with
`hold = True`, write the immutable submission and scheduler records, and call
`condor_release` once before any attempt runs. Do not call `condor_release`
again as a recovery mechanism. A seed is consumed once an attempt may have
started.

For a producer or raw-validation failure, allocate the next attempt only after
the required prior evidence exists:

```bash
python3 tools/campaign_manifest.py allocate-retry \
  campaigns/<NEW_FULL_CAMPAIGN> TUNE LOGICAL_ID \
  --reason "reviewed technical failure"
```

If scheduler history is unavailable, the allocation requires a real
`hf_scheduler_loss_retry_authorization_v1` file through
`--scheduler-loss-approval`. Do not create one speculatively.

Render:

```bash
./submit_full_retry.sh \
  campaigns/<NEW_FULL_CAMPAIGN> TUNE LOGICAL_ID ATTEMPT --dry-run
```

Submit:

```bash
./submit_full_retry.sh \
  campaigns/<NEW_FULL_CAMPAIGN> TUNE LOGICAL_ID ATTEMPT --submit
```

The retry command never allocates a seed. It accepts only an already appended
ledger allocation and creates its own immutable claim and scheduler record.
Logical ID is unchanged; attempt and seed are new.

## Resource and failure-bias checks

Gate B records, by tune:

- elapsed seconds;
- peak RSS;
- raw bytes;
- ROOT compression settings/algorithm/level/factor;
- bytes per successful event;
- projections for all 500 candidates and the 300-file canonical set.

Before launch, add headroom for simultaneous partials, output validation,
analysis (300 pair files per raw file), central merges, ten block merges,
plots, logs, and preservation of legacy samples.

After execution, compare valid versus failed/reserve cohorts using only
technical metadata: process mix, event rate, output size, multiplicity
diagnostics, and wall time. If missingness may be physics dependent, do not
freeze a convenient subset. Increase resources or redesign recovery.

## Analysis submission

After the canonical freeze is sealed, queue exactly its manifest. The first
stage has 300 rows; a reviewed superseding freeze has `3*N` rows for equal
`N >= 100`, `N % 10 == 0`:

```bash
  ./submit_status_analysis.sh \
  Production/<NEW_FULL_CAMPAIGN>/freeze \
  <PRODUCTION_ROOT> \
  AnalysisOutput/<NEW_FULL_CAMPAIGN> \
  --dry-run

./submit_status_analysis.sh \
  Production/<NEW_FULL_CAMPAIGN>/freeze \
  <PRODUCTION_ROOT> \
  AnalysisOutput/<NEW_FULL_CAMPAIGN> \
  --submit
```

Use `Production/<NEW_FULL_CAMPAIGN>` as `<PRODUCTION_ROOT>` for a first-stage
freeze. A superseding manifest can reference multiple source campaigns, so it
requires the collection root `Production`. The analysis submit also uses
`getenv = False`, EL9, quoted `long` `JobCategory`, no automatic retry, and
hold on failure. It queues exactly the manifest's `3*N` paths and rejects
reserve over-inclusion or directory discovery. Every raw input still produces
the fixed registry of 300 signed pair files.

Gate-B pilot analysis, when needed outside Gate D, uses:

```bash
./submit_gate_b_analysis.sh \
  campaigns/<GATEB_CAMPAIGN> \
  Production/<GATEB_CAMPAIGN> \
  AnalysisOutput/<GATEB_CAMPAIGN> \
  --dry-run
```

Append `--scope=central` or `--scope=sensitivity` only to process that exact
manifest-declared subset while other pilots run. It never discovers files.

## Generated directories

Publication operations write to ignored paths:

```text
campaigns/
Production/
AnalysisOutput/
logs/
Jobs/
```

Ignored does not mean disposable. Campaigns, global registry claims,
submission records, validation receipts, canonical manifests, and release
logs are immutable evidence and must be archived. Never run broad cleanup in
a shared checkout or production directory.

## Legacy workflow

`runCondorJob_legacy.sh`, fixed `submitCondor_*.sub`, split producers, and
`RootFiles/<channel>/<tune>` remain for historical reproduction. Their
time/PID/job-derived seed behavior, directory discovery, charge-combined
analysis, and automatic retry conventions are not compatible with the
publication campaign contract. Do not use them to create or fill a canonical
raw-v5 manifest.
