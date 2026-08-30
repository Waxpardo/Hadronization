# Systematics — PAUSED

**Ruling R31 pauses systematics development.** The module is not on the paper's
critical path. It stays in the tree, its tests stay green, and it must be
possible to finish and switch it on later without touching the rest of the
pipeline.

The paper's figures therefore carry **ten-block statistical uncertainties
only** (see [../physics/STATISTICS.md](../physics/STATISTICS.md)).

## What the pause means in practice

**No session edits the paused files.** The boundary is a list, not a judgement
call:

`tools/systematics_*.py`, `tools/statistical_robustness.py`, `tools/a2_*.py`,
`tools/assert_systematics_envelope.py`,
`plotting/render_systematics_overlay.py`, `extraction/write_verdict.py`,
`extraction/combine_per_class.py`, `extraction/combine_derived.py`,
`extraction/write_tune_separation.py`, `extraction/write_per_class_report.py`,
`extraction/write_combination_report.py`, `analysis/a2_*`,
`config/systematics_*.json`, `config/verdict_v3.json`,
`config/a2_variations_v1.json`, `config/accepted_measurements_v1.json`,
`tools/evaluate_pthat_sensitivity.py`.

`docs/SYSTEMATICS_PREREGISTRATION.md` stays byte-identical: its sha256
`a42ef9915cf555d637f66f56aef1f120113aaa27e0a6d9a9b3dfe1e5f72d2826` is pinned
fourteen times across eight `config/dataset_selector*.json` files.

**Documentation about the module is not the module.** Writing down what the
paused code does, and recording a ruling that will apply when it reopens, is
documentation work and stays in `docs2/`. That is why this page exists.

**No session gold-plates a paused module.** The DA-1 deep audit dispositioned
38 rows `SYS-DORMANT` on exactly this ground.

## What exists

The machinery is complete enough to run and is not switched on: variation
campaigns, envelope, verdict, overlay, robustness cross-check, A2 licensing,
and the report writers.

Seven variation campaigns hold ordinals 4 to 10
(`config/campaign_ordinals_v1.json`): `HF_SYS_MUR_UP`, `HF_SYS_MUR_DOWN`,
`HF_SYS_MUF_UP`, `HF_SYS_MUF_DOWN`, `HF_SYS_PDF_CTEQ6L1`, `HF_SYS_PTHAT_1`,
`HF_SYS_PTHAT_4`.

## What is retired, and stays retired

Every artifact under `results/systematics/20260819` and
`results/systematics/20260820` was produced on the **retired common absolute
multiplicity axis**. Both trees carry
`"status": "HISTORICAL_PROVENANCE_ONLY"` and
`"current_or_publication_use": "PROHIBITED"`
(`results/systematics/20260819/RETIREMENT_STATUS.json`,
`results/systematics/20260820/RETIREMENT_STATUS.json`).

`docs/` cites those two trees 54 times across seven files. Those citations are
historical and are **labelled, not rewritten**: each cluster carries a
retirement note. A reader who follows one of them is reading provenance, not a
current result.

## The work list

[REACTIVATION.md](REACTIVATION.md) is the checklist for the session that
switches the module on. It is not rewritten by documentation sessions and it is
not worked before the pause lifts.
