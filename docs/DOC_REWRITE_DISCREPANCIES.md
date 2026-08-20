# Documentation rewrite discrepancies

This table records disagreements found by deriving current claims from code, configuration, and committed artifacts.
The verdict column states which source controls the replacement document.

| replacement document | earlier document | current artifact | earlier claim | derived claim | verdict and check |
|---|---|---|---|---|---|
| `docs/PHYSICS.md` | `docs/DESIGN_AND_RATIONALE.md` | `config/multiplicity_class_boundaries_v1.json` | Each tune used percentiles from its own sample. | All tunes use common absolute `N_ch` boundaries with MONASH minimum-bias labels. | The boundary artifact is right. The plotting header reads it directly, and the committed MONASH distribution reproduces its labels. |
| `docs/PHYSICS.md` | `docs/REGISTRY_AND_MAPPING_PROPOSAL.md` | `config/tune_difference_allowlist_v1.json` | The tune dependence flows through diquark and junction parameters. | The cards differ in 28 parameters across nine families, so no mechanism is isolated. | The allowlist is right. `tools/validate_tune_cards.py` reports all 28 permitted differences and rejects any extra difference. |
| `docs/PHYSICS.md` | `docs/EXTRACTION_CONVENTIONS.md` | `extraction/apply_decay_map.py` | The experiment-comparable grouping states what a detector would reconstruct. | The code only applies branching-fraction weights to ground-state rows. | The code is right. It implements no decay kinematics, acceptance, efficiency, resolution, bin migration, or detector response. |
| `docs/PHYSICS.md` | `docs/EXTRACTION_CONVENTIONS.md` | `AnalysisScripts/decay_parent_map_v2.json` | The displayed version 1.1 table says CURRENT, although a later annotation names version 2. | Published extraction uses version 2 with two branching-fraction splits. | Version 2 is right. `extraction/three_tune_table.py` loads it directly and labels the output as split. |
| `docs/PHYSICS.md` | `docs/SECOND_BRANCH_WEIGHT.md` | `extraction/second_branch_weight.py` | The branching-fraction split remained an undecided option after a 12.8400 percent bound. | Version 2 applies the split and leaves 0.0017 percent risk on corrected weights. | The current code and artifacts are right. The calculator reproduces both the historical bound and the corrected residual. |

Version 1's unconjugated antiparticle products were also cross-checked.
The v1 artifact yields D0 and anti-D0 weights of 59,678,352 and 13,298,376.
Version 1.1 yields 36,539,688 and 36,437,040 with the same anchor weights.
This is a confirmed historical defect, not an unresolved disagreement.
