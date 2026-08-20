# Nikhef deletion proposal — post-consolidation

**Proposed 2026-08-20 from the pre-move top-level census. Nothing in this
document has been deleted.** Paths below use the new `hf/` layout; exact sizes
are allocated bytes from
[`nikhef_consolidation_20260820/census_20260820.tsv`](nikhef_consolidation_20260820/census_20260820.tsv).

The proposal deliberately excludes `tune_runs_e5fix/` and `tune_runs_three/`.
Despite their scratch-like names, they are the run roots behind the published
MONASH and JUNCTIONS/CLOSEPACKING per-tune tables. It also excludes `m7_runs/`,
`f3_runs/`, `species_axis_fixture/`, `sigmab_runs/task22`, `merge_runs/`, both
history/seed archives, and every protected or permanent data tree.

## Deletable now — 32 paths, 385,056,768 bytes

These paths are caches, exact duplicates, zero-byte output, superseded output,
or closed one-off investigations whose evidence has already been committed.
The owner may accept or reject each row independently.

| path | bytes | why nothing needs it |
|---|---:|---|
| `hf/project/scratch/.vscodium-server/` | 346,640,384 | Editor-server cache regenerates on the next connection and carries no project evidence. |
| `hf/project/archive/AnalysisScripts/` | 188,416 | Both JSON files are byte-identical to the checkout copies and no live path names this directory. |
| `hf/project/scratch/a2_config/` | 4,096 | It contains no regular files. |
| `hf/project/runs/a2_multiplicity/` | 77,824 | This exploratory run was superseded by the recorded A2 variation and re-analysis outputs. |
| `hf/project/scratch/b4_mapping/` | 151,552 | The one-off mapping result was incorporated into tracked artifacts. |
| `hf/project/runs/b6_run/` | 4,468,736 | This closed one-off run is superseded by later gate and closure evidence. |
| `hf/project/archive/campaign_closure_status.py` | 4,096 | It is byte-identical to tracked `tools/campaign_closure_status.py`. |
| `hf/project/scratch/chain_path_proof/` | 20,480 | The path defect and its fix are now enforced by a tracked test. |
| `hf/project/runs/closure_runs/` | 28,672 | These exploratory closure runs are superseded by canonical closure logs and manifests. |
| `hf/project/archive/config/` | 139,264 | Both JSON files are byte-identical to checkout copies and no live path names this directory. |
| `hf/project/scratch/contract_compile_check/` | 479,232 | This was a one-off compile check; the contract and tests are tracked. |
| `hf/project/scratch/determinism_control/` | 8,736,768 | The determinism investigation is closed and its conclusion is recorded in the repository. |
| `hf/project/archive/docs/` | 8,192 | Its sole JSON file is byte-identical to the checkout copy and no live path names this directory. |
| `hf/project/archive/extract_final_two.out` | 0 | It is an empty completed-command output. |
| `hf/project/scratch/extractor_e5fix/` | 413,696 | The E5 fix is tracked and the superseded implementation is separately retained in the attic. |
| `hf/project/runs/f4_runs/` | 229,376 | This closed F4 investigation was superseded by later validation. |
| `hf/project/runs/f4b_runs/` | 499,712 | This closed F4b follow-up was superseded by later validation. |
| `hf/project/scratch/first_contact/` | 294,912 | It is an exploratory first-contact run with no live path dependency. |
| `hf/project/runs/gate_runs/` | 2,760,704 | The gate outcome is committed; this deployed test run has no live consumer. |
| `hf/project/scratch/guard_hook_src/` | 28,672 | The guard source is tracked and this fixture has no live consumer. |
| `hf/project/scratch/guard_hook_test/` | 196,608 | The hook harness is superseded by tracked tests and has no live consumer. |
| `hf/project/runs/m7b_runs/` | 884,736 | The beauty-M7 logs are already committed as anchors. |
| `hf/project/runs/measurements_v3/` | 4,001,792 | Version 4 supersedes this measurement root. |
| `hf/project/runs/poolrss_run01/` | 16,384 | The pool-sizing investigation is closed and recorded. |
| `hf/project/runs/poolsweep_run01/` | 16,384 | The pool-sizing investigation is closed and recorded. |
| `hf/project/runs/proj6iii_run01/` | 20,480 | The projection investigation is closed and superseded. |
| `hf/project/scratch/proj6iii_v2/` | 24,576 | The projection follow-up is closed and superseded. |
| `hf/project/scratch/pythia_hang_repro/` | 569,344 | The reproduction attempt and its negative result are recorded under release blocker B7. |
| `hf/project/scratch/registry_baseline_build/` | 327,680 | The generated registry is tracked; this build workspace has no live consumer. |
| `hf/project/scratch/rehash_run/` | 9,822,208 | The one-off rehash investigation is closed and has no live consumer. |
| `hf/project/scratch/species_ordinals_build/` | 110,592 | The generated species-ordinal artifact is tracked; this build workspace is redundant. |
| `hf/project/runs/sys_runs_plot5/` | 3,891,200 | Plot version 6 supersedes this output root. |

## After acceptance — 17 paths, 27,266,199,552 bytes

These paths still support review, re-rendering, regression evidence, or the A2
systematic. Acceptance is the event that makes those operational copies
unnecessary; until then they stay.

| path | bytes | why it can wait for acceptance |
|---|---:|---|
| `hf/project/runs/a2_runs/` | 26,426,851,328 | It is the re-analysis evidence behind a published systematic. |
| `hf/project/deploys/a2_tools/` | 225,280 | It preserves the deployed helpers used to produce the A2 evidence. |
| `hf/project/runs/a2_variation/` | 9,068,544 | It is a configured A2 variation workspace that a reviewer may ask to inspect. |
| `hf/project/runs/a2_variation_largest/` | 9,068,544 | It is the companion largest-index A2 variation workspace. |
| `hf/project/deploys/figure_deploy_20260817/` | 55,742,464 | It contains the current reference render and its boundary receipt. |
| `hf/project/runs/fixcheck_20260818/` | 80,252,928 | It is the recent post-fix validation evidence. |
| `hf/project/deploys/hadronization_v3_plotting_run/` | 28,237,824 | Boundary receipts name this plotting run as their origin. |
| `hf/project/runs/measurements_v4/` | 1,998,848 | It is the current measurement output root. |
| `hf/project/deploys/pythia_stock_8317/` | 332,103,680 | It is the exact installed generator dependency used by the campaign. |
| `hf/project/archive/render_measure_v4.sh` | 4,096 | It is the only exact wrapper recording how the current v4 render was launched. |
| `hf/project/runs/s4_run/` | 147,456 | It is recent S4 evidence from the final systematics pass. |
| `hf/project/deploys/sys_plot_deploy/` | 84,770,816 | It is the current systematics plotting deploy. |
| `hf/project/runs/sys_runs/` | 4,849,664 | It is the current systematics extraction output root. |
| `hf/project/runs/sys_runs_plot6/` | 1,949,696 | It is the current systematics plot output root. |
| `hf/project/deploys/systematics_deploy/` | 138,240,000 | It is the producer deploy pinned by the systematics record. |
| `hf/project/deploys/systematics_regression/` | 92,676,096 | It is the only artifact proving the rebuilt producer reproduced nominal slot zero. |
| `hf/project/archive/quarantine/` | 12,288 | It is superseded material, retained conservatively until review closes. |
