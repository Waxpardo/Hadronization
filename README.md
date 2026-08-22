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

The authoritative records are [DECISIONS.md](docs/DECISIONS.md),
[`multiplicity_percentile_classes_v2.json`](config/multiplicity_percentile_classes_v2.json),
and [`cr_holdout_policy_v1.json`](config/cr_holdout_policy_v1.json).

## One workflow

```bash
./hadronization site
./hadronization check --portable        # local source-development check
./hadronization check                   # pinned Nikhef certification
./hadronization build                   # pinned producer build on Nikhef/STBC
./hadronization dataset hf_run3_v1_candidate
```

The full Nikhef chain uses the same command:

```bash
./hadronization render-production HF_RUN3_V2 4 1000 100000
condor_submit submit_HF_RUN3_V2_full.sub

./hadronization freeze hf_run3_v1_candidate
./hadronization render-analysis hf_run3_v1_candidate
condor_submit submit_analysis_HF_RUN3_V1.sub

./hadronization merge hf_run3_v1_candidate v3
./hadronization plot hf_run3_v1_candidate all
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
  project/results/              plots, receipts, and measurements by commit
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

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for ownership and dataflow, and
[MIGRATION.md](docs/MIGRATION.md) for the relationship to the archived working
repositories and Nikhef data. [REBUILD_STATUS.md](docs/REBUILD_STATUS.md)
separates current contracts from retained historical evidence.
