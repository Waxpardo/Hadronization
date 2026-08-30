# Hadronization

This is the clean execution repository for the heavy-flavour balancing study
across the PYTHIA 8.317 MONASH, JUNCTIONS, and CLOSEPACKING tune bundles at
13.6 TeV.

Nikhef is the authoritative execution environment. A local clone is a
development convenience: every production, reduction, merge, extraction, and
plotting step can run from a Nikhef checkout with external data under the
selected site root. No workflow stage requires files from a developer laptop.

## Scientific decisions

- Event-activity classes are tune-local percentiles. The `90-100, ..., 1-10,
  0-1%` windows are resolved independently from each tune's own merged
  `summed MULTIPLICITY` histogram. Absolute `N_ch` thresholds are allowed to
  differ between tunes.
- The implementation follows the multiplicity definition used in Paul Veen's
  PR 13 while retaining later validation: exact histogram identity, explicit
  flow-bin policy, disjoint integer ranges, full partition coverage, and a
  per-run boundary receipt.
- The observed nominal-campaign CR attrition—63/1063 JUNCTIONS attempts and
  64/1064 CLOSEPACKING attempts—is accepted. Failed attempts remain wholly
  excluded and are retried with independent deterministic seeds; the measured
  attrition is reported, not corrected away.

The authoritative records are the internal DECISIONS.md, held in the project
archive outside this repository,
[`multiplicity_percentile_classes_v2.json`](config/multiplicity_percentile_classes_v2.json),
and [`cr_holdout_policy_v1.json`](config/cr_holdout_policy_v1.json). The two
tracked files carry the tune-local class definition and the accepted CR
attrition in full. `config/systematics_envelope_v1.json` and
`config/systematics_sources_v1.json` cite the same internal record for owner
rulings R7 and R9 to R11.

## One workflow

```bash
./hadronization site
./hadronization check --portable        # local source-development check
./hadronization check                   # pinned Nikhef certification
./hadronization build                   # pinned producer build on Nikhef/STBC
./hadronization dataset hf_run3_v1_candidate
```

The full Nikhef chain uses the same command:

The first line below is illustrative of the command SHAPE only. `HF_RUN3_V2`
is not a claimed campaign, and ordinal 4 is held by `HF_SYS_MUR_UP`
(`config/campaign_ordinals_v1.json`), so
`tools/render_production_submit.py` refuses that pair before it writes a
submit file. A real run names an owner-approved campaign and an ordinal
recorded in that file first; nobody may invent one here. The completed
campaign's own command is in `docs2/pipeline/PRODUCE.md`.

```bash
./hadronization render-production HF_RUN3_V2 4 1000 100000
condor_submit submit_HF_RUN3_V2_full.sub

./hadronization freeze hf_run3_v1_candidate
./hadronization render-analysis hf_run3_v1_candidate
condor_submit submit_analysis_HF_RUN3_V1.sub

./hadronization merge hf_run3_v1_candidate v3
# `all` is NOT runnable for HF_RUN3_V1: it expands to a `thnsparse` target
# that derives configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse.json,
# which does not exist, so the run exits 2 at preflight. The paper figures are
# invoked by explicit target -- see docs2/pipeline/RENDER.md.
./hadronization plot hf_run3_v1_candidate multiplicity-spectrum

# Non-publication systematic measurement; staged config, log, figures,
# output assertion, and receipt all stay in its commit-scoped measurement root.
# Its staged audit canvas gets a wider display frame than the nominal paper
# figure; the measured uncertainty rows are unchanged and must be complete.
./hadronization plot hf_sys_mur_up_variation measure-balancing
```

The portable check does not certify the pinned production runtime, external
campaign bytes, or a scientific render. Commands fail closed on unnamed
datasets, missing manifests, dirty production
checkouts, wrong schemas, off-pin runtimes, incomplete blocks, or changed input
digests. Run `./hadronization help` for the command contract.

## Site configuration

`setupEnv.sh` selects `config/sites/nikhef.conf` when Nikhef storage and CVMFS
are available; otherwise it selects `config/sites/local.conf`. Tracked dataset
selectors use `${HADRONIZATION_DATA_ROOT}` and contain no account-specific
absolute path.

Optional machine overrides belong in ignored files:

```bash
cp config/site.local.conf.example config/site.local.conf
cp config/dependencies.local.conf.example config/dependencies.local.conf
```

Large data always live outside Git:

```text
${HADRONIZATION_DATA_ROOT}/
  project/runs/                 seed ledger and sealed campaign freezes
  project/results/            campaign/commit plots, receipts, and measurements
  hadronization_production/   promoted raw campaign files
  hadronization_analysis/     per-job reductions and validation
  hadronization_merged/       central and ten-block pair products
  systematics_harvest/        variation manifests and harvested outputs
```

## Pipeline

```text
generation -> canonical manifest -> reduction -> central + 10 blocks
           -> extraction/systematics -> plotting -> selected results
```

The code mirrors that flow in `generation/`, `analysis/`, `merging/`,
`extraction/`, and `plotting/`. Scientific registries and selectors live in
`config/`; fail-closed checks live in `Validation/`, `tools/`, and `tests/`.

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for ownership and dataflow. Commit
4a007f2 of 2026-08-22 moved two records out of this repository.
`git show 4a007f2^:docs/MIGRATION.md` states the relationship to the archived
working repositories and Nikhef data.
`git show 4a007f2^:docs/REBUILD_STATUS.md` separates the contracts current at
that date from retained historical evidence.
