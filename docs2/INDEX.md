# docs2 — what lives where

Ruling R33 makes this directory the documentation home: short files, one
subject each, every claim carrying a `file:line` citation. `docs/` stays as the
historical record and is not the place to look first.

Read the page whose subject you need. Nothing here repeats another page.

## Running the pipeline

| page | subject |
|---|---|
| [pipeline/PRODUCE.md](pipeline/PRODUCE.md) | campaign generation. Historical record: the campaigns are complete |
| [pipeline/MERGE.md](pipeline/MERGE.md) | the supervised merge (ruling R25) |
| [pipeline/RENDER.md](pipeline/RENDER.md) | the plot launcher, the five V-configurations, the explicit-target rule |
| [pipeline/FIGURES.md](pipeline/FIGURES.md) | G1–G9 and T1: producer, output stem, delivery name |
| [pipeline/VERIFY.md](pipeline/VERIFY.md) | closure and strict CONTROL, and the shapes they assert |
| [pipeline/COUNT.md](pipeline/COUNT.md) | T1: the counting macro and the merged-counter helper |
| [pipeline/STYLE.md](pipeline/STYLE.md) | the five configurations, the generator's style seams, and the recorded debt |

## What the numbers mean

| page | subject |
|---|---|
| [physics/OBSERVABLE.md](physics/OBSERVABLE.md) | `Y_bal`, OS−SS, the factor-one SS term, the trigger denominator |
| [physics/MULTIPLICITY.md](physics/MULTIPLICITY.md) | the `\|eta\| <= 1` heavy-flavour-excluded counter and the per-tune classes |
| [physics/STATISTICS.md](physics/STATISTICS.md) | pooled central, ten blocks, SEM on nine degrees of freedom |
| [physics/SAMPLE_COUNTING.md](physics/SAMPLE_COUNTING.md) | what the generated-sample table counts |

## The paper handoff

| page | subject |
|---|---|
| [paper/CLAIM_MAP.md](paper/CLAIM_MAP.md) | every claim and figure mapped to its producer and contract |
| [paper/DELIVERABLES.md](paper/DELIVERABLES.md) | the byte-exact delivery-name manifest |
| [paper/CAMPAIGN_TRUTH.md](paper/CAMPAIGN_TRUTH.md) | the campaign parameters, as measured from the cards |

## Governance

| page | subject |
|---|---|
| [systematics/STATUS.md](systematics/STATUS.md) | the module is paused under ruling R31 |
| [systematics/REACTIVATION.md](systematics/REACTIVATION.md) | the work list for the session that switches it on |
| [decisions/RULINGS.md](decisions/RULINGS.md) | an index of rulings R19–R47 |

## Two rules that decide where a correction goes

**A pinned document is frozen.** Two files under `docs/` have their sha256
pinned by tracked configuration, so editing one turns the suite red. They are
`docs/SYSTEMATICS_PREREGISTRATION.md` (pinned fourteen times across eight
`config/dataset_selector*.json` files) and
`docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md` (pinned as
`publication_authorization_sha256` in `config/dataset_selector.json` and
`config/dataset_selector_hf_run3_v1.json`). A correction to either lands here,
never there.

**A retired result is labelled, not rewritten.** Every artifact under
`results/systematics/20260819` and `results/systematics/20260820` is
`HISTORICAL_PROVENANCE_ONLY` with `current_or_publication_use: PROHIBITED`
(`results/systematics/20260819/RETIREMENT_STATUS.json`,
`results/systematics/20260820/RETIREMENT_STATUS.json`). `docs/` cites those
trees 54 times across seven files; each cluster carries a retirement note and
the prose around it stays as written.
