# Hadronization

The execution repository for a heavy-flavour balancing study in PYTHIA 8.317,
comparing three hadronization tunes — **MONASH**, **JUNCTIONS** and
**CLOSEPACKING** — in pp collisions at **√s = 13.6 TeV**.

The measured quantity is a balancing yield: for a heavy-flavour trigger, the
opposite-sign minus same-sign associate yield per trigger, resolved against
event activity. The comparison is a ratio of tunes, so the three share the
generator, the cuts, the counter and the class definition.

**This repository holds the code, the contracts and the delivered figures. It
does not hold the data.** See *The data plane* below.

## Read these four, in this order

1. **[docs2/INDEX.md](docs2/INDEX.md)** — what every documentation page covers.
   Ruling R33 makes `docs2/` the documentation home; `docs/` is the historical
   record and is not the place to look first.
2. **The architecture map** — `PIPELINE_MAP_20260827.md`, held in the project
   archive outside this repository. One entry per tracked file: what it does,
   what it feeds, how to run it. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
   is the in-repository summary of ownership and dataflow.
3. **[docs2/paper/CLAIM_MAP.md](docs2/paper/CLAIM_MAP.md)** — every claim and
   every figure mapped to what produces it and what contract holds it.
4. **[docs2/decisions/DEFERRED.md](docs2/decisions/DEFERRED.md)** — the
   post-paper work list: what the repository audit found and deliberately did
   not do, with the reason for each.

Then, if you are deciding something:
[docs2/decisions/OPEN_QUESTIONS.md](docs2/decisions/OPEN_QUESTIONS.md) lists
what is unresolved and who owns each decision, and
[docs2/decisions/RULINGS.md](docs2/decisions/RULINGS.md) indexes rulings
R19–R50.

## The campaign

`HF_RUN3_V1`, campaign ordinal 3, sealed and publication-eligible
(`config/campaign_ordinals_v1.json`, the ordinal-3 row).

**1,000 canonical slots per tune × 100,000 successful events per job × 3
tunes = 3 × 10⁸ events.** Small jobs are a deliberate choice: they bound the
work lost to a generator hang.

Event-activity classes are **tune-local percentiles**. The `90-100 %` through
`0-1 %` windows are resolved independently from each tune's own merged
`summed MULTIPLICITY` histogram, so absolute `N_ch` thresholds differ between
tunes and are allowed to. The definition is
[`config/multiplicity_percentile_classes_v2.json`](config/multiplicity_percentile_classes_v2.json);
the physics is [docs2/physics/MULTIPLICITY.md](docs2/physics/MULTIPLICITY.md).

**Attrition is disclosed, not corrected away** (ruling R41). 63 of 1,063
JUNCTIONS attempts and 64 of 1,064 CLOSEPACKING attempts were discarded — 127
of 3,127, **4.06 %**, none in MONASH. The campaign record attributes the
mechanism to a PYTHIA junction-splitting hang; the per-attempt termination
metadata is not in this repository (`docs/REPRODUCIBILITY.md:147`). The policy
is [`config/cr_holdout_policy_v1.json`](config/cr_holdout_policy_v1.json).
Whether that can bias the measurement is argued, as an unratified draft, in
[docs2/physics/DISCARD_BIAS.md](docs2/physics/DISCARD_BIAS.md).

## What is delivered

**Ten deliverable rows: G1–G9 and T1**, described one per row in
[docs2/pipeline/FIGURES.md](docs2/pipeline/FIGURES.md) with producer, output
stem and delivery name. G9 is thirty figures on its own — ten species × {pT,
η, φ}.

The assembled package is **`deliverables/20260901/`**, 48 tracked files: 38
figures, 7 tables, and three prose files that explain the package
(`MANIFEST.md`, `REPRODUCE.md`, `EDITORIAL_NOTES.md`). The manifest names 45
of them with a sha256 each, and `tests/test_handoff_package.py` checks every
row byte for byte, checks that the directory holds nothing the manifest omits,
and refuses any citation of a retired systematics tree in the package or in
`docs2/paper/`.

Two figures the current draft includes are **not** produced here; that and the
rest of what is unresolved are in
[docs2/decisions/OPEN_QUESTIONS.md](docs2/decisions/OPEN_QUESTIONS.md).

## Two shells, and what each can do

| | the bench | the deployment |
|---|---|---|
| where | a local checkout, e.g. this one | Nikhef, `/data/alice/ipardoza/…` |
| runtime | any local ROOT | the pinned PYTHIA 8.317 / ROOT 6.30.01 |
| can | the full 97-driver suite, every generator `--check`, every source contract | everything the bench can, plus render, merge and campaign |
| cannot | reach the data plane, so it renders no figure and merges nothing | — |

Only the deployment certifies a render, a merge or a campaign (ruling R29).
Work moves bench → deployment by verified bundle, fast-forward only.

`setupEnv.sh` picks `config/sites/nikhef.conf` when Nikhef storage and CVMFS
are present and `config/sites/local.conf` otherwise. Machine-specific overrides
go in ignored files:

```bash
cp config/site.local.conf.example config/site.local.conf
```

## The command surface

Every command down to `make cards` was run on the bench at this commit and is
reported as it behaved. The commands below that need the data plane, so the
bench cannot run them; they are given because the deployment runs them, and
they are marked.

```bash
make help
```

```bash
./hadronization help
```

```bash
./hadronization site
```

```bash
make test
```

`make test` runs `tools/run_tests.sh`, which sources `setupEnv.sh` once and
then runs all **97** drivers in that one shell. It reads **97/97** on a
ROOT-equipped shell and **89/97** without ROOT — the eight misses are the
ROOT-dependent drivers, which fail rather than skip by design.

```bash
HF_ALLOW_UNPINNED_ENV=1 make check
```

`check` is doctor + cards + registry + test, and it ends with the environment
verdict. On a bench whose ROOT and PYTHIA are off the pin — which is normal for
laptop work — plain `make check` runs the suite green and then **refuses at the
verdict**, exit 2, telling you to declare the concession. The form above is
that declaration, and it exits 0 while printing "This run is NOT a
pinned-runtime certification".
`./hadronization check --portable` is the same concession under another name.

**What a green `make check` does not certify.** It does not certify the pinned
production runtime — a bench ROOT is not ROOT 6.30.01 with PYTHIA 8.317. It
does not certify any external campaign bytes, because the bench cannot reach
the data plane. And it does not certify a scientific render, because it renders
nothing. A green suite says the contracts in this repository hold; it does not
say a figure is right. `tools/environment_verdict.sh` runs last in `check` and
says the same thing in the transcript, and `HF_ALLOW_UNPINNED_ENV=1` — which
`--portable` sets — makes the concession explicit rather than silent.

```bash
make registry
```

```bash
make cards
```

**Rendering is by explicit target. `all` is not runnable for this campaign**
(finding F57): it expands to a `thnsparse` target that derives a configuration
which does not exist, so the run exits 2 at preflight. The paper figures are
invoked by name, and which name produces which figure is
[docs2/pipeline/RENDER.md](docs2/pipeline/RENDER.md).

```bash
./hadronization plot hf_run3_v1_candidate multiplicity-spectrum
```

That render is a deployment command; on the bench it refuses, because the
dataset's roots are not there.

**`HADRONIZATION_DATASET` is required to render and must be unset to test.**
Exporting it turns exactly three drivers red. Use two shells; the trap is
documented in [docs2/pipeline/RENDER.md](docs2/pipeline/RENDER.md).

**Not runnable on the bench.** The production and analysis chain needs the
data plane mounted, so the three commands below run only on the deployment:

```bash
./hadronization freeze hf_run3_v1_candidate
```

```bash
./hadronization render-analysis hf_run3_v1_candidate
```

```bash
./hadronization merge hf_run3_v1_candidate v3
```

Submitting a **new** campaign needs an owner-approved campaign name and an
ordinal recorded in `config/campaign_ordinals_v1.json`. There is no default and
nobody may invent one: `tools/render_production_submit.py` refuses an
unclaimed pair before it writes a submit file, and every rendered job starts
held. The completed campaign's own command is in
[docs2/pipeline/PRODUCE.md](docs2/pipeline/PRODUCE.md).

Commands fail closed on unnamed datasets, missing manifests, dirty production
checkouts, wrong schemas, off-pin runtimes, incomplete blocks and changed input
digests.

## The data plane

Large data always live outside Git, under `${HADRONIZATION_DATA_ROOT}`, which
`setupEnv.sh` derives from the site profile. Tracked selectors use that
variable and contain no account-specific absolute path.

```text
${HADRONIZATION_DATA_ROOT}/
  project/runs/               seed ledger and sealed campaign freezes
  project/results/            campaign/commit plots, receipts and measurements
  hadronization_production/   promoted raw campaign files
  hadronization_analysis/     per-job reductions and validation
  hadronization_merged/       central and ten-block pair products
  systematics_harvest/        variation manifests and harvested outputs
```

**How it is sealed.** The raw campaign is 3,000 files and 284,750,292,184 bytes
(≈265 GiB). Three things hold it: the campaign ordinal is packed into every
event identifier and into the seed band, and is not correctable after the jobs
run; the **canonical manifest** names exactly which promoted files enter
reduction, and only files it names are read; and the dataset row records the
campaign as sealed with `publication_eligible` true. A render is bound to its
inputs by digest, so a changed input is a refusal rather than a different
number.

**One copy exists.** It is regenerable in principle — the seeds are recorded
and PYTHIA is deterministic, at 562.5 CPU-hours for event generation plus the
merge and analysis chain — but that is a recoverable position, not a safe one.
It is recorded as an open question.

## Pipeline

```text
generation -> canonical manifest -> reduction -> central + 10 blocks
           -> extraction/systematics -> plotting -> selected results
```

The code mirrors that flow in `generation/`, `analysis/`, `merging/`,
`extraction/` and `plotting/`. Scientific registries and selectors live in
`config/`; fail-closed checks live in `Validation/`, `tools/` and `tests/`.

Systematics are **paused** under ruling R31. The module is intact and
toggleable; see [docs2/systematics/STATUS.md](docs2/systematics/STATUS.md).

## Provenance and status

Authoritative decision records are held in the project archive outside this
repository; [docs2/decisions/RULINGS.md](docs2/decisions/RULINGS.md) indexes
them and says which ledger to open.

Commit `4a007f2` of 2026-08-22 moved two records out of this repository:
`git show 4a007f2^:docs/MIGRATION.md` states the relationship to the archived
working repositories and the Nikhef data, and
`git show 4a007f2^:docs/REBUILD_STATUS.md` separates the contracts current at
that date from retained historical evidence.

`CITATION.cff` records that authorship, author order, affiliations, release
identity **and licensing** are provisional and require approval. **This
repository carries no LICENSE file yet**, which is recorded as an open
question.
