# Claim map

The successor of `paper/CLAIM_EVIDENCE.md`. One row per current claim and per
deliverable: what produces it, what contract holds it, and — after RUN-N —
which acceptance record carries its bytes.

**Three rules govern this file.**

1. **No PROHIBITED-scope citation.** Nothing here cites
   `results/systematics/20260819` or `results/systematics/20260820`. Both trees
   are `HISTORICAL_PROVENANCE_ONLY` with
   `current_or_publication_use: PROHIBITED`, so a citation of either would
   license a paper claim on a retired axis.
2. **No absent file.** Every path was checked to exist at HEAD `f44e038`.
3. **A test is evidence only for what it actually asserts.** A test that pins a
   definition in its own arithmetic is not evidence about the code that
   implements it.

`paper/CLAIM_EVIDENCE.md` breaks both rules and is **superseded, not edited**.
Four of its rows — A4, M3, R2 and R3 — take their evidence from the two retired
systematics trees, and three of its cited paths do not exist at HEAD (one
bibliography copy the archive holds, one the owner's Overleaf state removed, and
the figure-acceptance manifest ruling R6 retired). Those paths are named in the
DOC-1 session report rather than repeated here, so that a scan of this file
finds no retired-tree citation to follow.

## Claims

| id | claim | producer or source | contract | source-contract test |
|---|---|---|---|---|
| C1 | pp at 13.6 TeV, PYTHIA 8.317, ROOT 6.30.01 | three nominal cards, `generation/cards/…:17` | `config/dependencies.conf:36,:47` | `tests/test_pythia_runtime_contract.py`; `tests/test_registry.py` |
| C2 | Forced hard-heavy sample, `pTHatMin = 2.0` | nominal cards `:24-25,:47` (MONASH) | `config/tune_difference_allowlist_v1.json` | `tests/test_registry.py` |
| C3 | Species roles and heavy-flavour signs follow signed quark content | `generation/producer/HeavyFlavourUtils.h` | `config/heavy_flavour_species_v1.json`; `contracts/GeneratedSpeciesOrdinals.h` | `tests/test_heavy_sign_production_convention.py`; `tests/test_registry.py` |
| C4 | Trigger and associate selections; direct-primary status 81–89 | `EligibleBase`, `analysis/status_analysis_THnSparse_qq.C` | `generation/producer/HeavyFlavourUtils.h:477-481` | `tests/test_heavy_flavour_utils.cpp` (pins the kinematic boundaries) |
| C5 | Trigger ancestry resolves to the selected hard process; associate origin is unrestricted, in six categories | `analysis/status_analysis_THnSparse_qq.C:993` | `contracts/AssociateOriginCategoryContract.h` | `tests/test_associate_origin_category_contract.py`; `tests/test_final_origin_closure.py` |
| C6 | Self-pairs and shared-hard-parton pairs are excluded | `analysis/status_analysis_THnSparse_qq.C:1081-1083`, `:1107-1121` | pair identity and selected-hard indices in the raw contract | **none pins these two predicates.** The nearest gate is `tests/test_pthat_sensitivity.py:549-554`, which asserts a nonzero `same_hard_pairs` diagnostic is a finding |
| C7 | `OS`, `SS`, `OS−SS` are registry-selected ordered conditional pairs; the SS factor is exactly 1 | `analysis/status_analysis_THnSparse_qq.C:1317`; `calculateOneYield` | `config/heavy_flavour_pair_registry_v1.json`; `contracts/GeneratedPairRegistry.h` | `tests/test_plot_reference_multiplicity_contract.py`; `tests/test_pair_selection_contract_parity.py` |
| C8 | Trigger normalization comes only from `hTrKinematics`; OS and SS denominators must match | `plotting/improvedPlotting_THnSparse.C:3812-3816` | `config/pair_file_object_contract_v1.json` requires `hTrKinematics` and permits `hFlavourClosureSummary` | `tests/test_pair_object_contract.py` |
| C9 | The reported integrated yield covers the full stored angular axis | `plotting/improvedPlotting_THnSparse.C:3824-3826` | the pair-object contract declares no regional boundary | `tests/test_pair_object_contract.py` |
| C10 | Event activity counts final charged non-heavy primaries, `pT > 0.15`, `\|η\| <= 1` | `generation/producer/HeavyFlavourUtils.h:557-562` | `config/multiplicity_percentile_classes_v2.json`, `counter` | `tests/test_multiplicity_inset_boundary_source.py`; `tests/test_supervisor_decisions.py` |
| C11 | Eleven percentile classes, resolved independently per tune | `plotting/improvedPlotting_THnSparse.C:2505-2507` | `config/multiplicity_percentile_classes_v2.json`, `definition` | `tests/test_harvest_class_axis.py`; `tests/test_plot_reference_multiplicity_contract.py` |
| C12 | Pooled central value; SEM across ten blocks on nine degrees of freedom; nonlinear quantities formed inside blocks | `extraction/harvest_class_axis.py:114-121`; `tools/build_canonical_manifest.py:281-287` | `config/statistical_robustness_v1.json`, `method` | `tests/test_statistical_robustness.py`; `tests/test_decompose_exit_status.py`; `tests/test_observable_contract.py` (arithmetic anchors only — see the correction below) |
| C13 | A species/reference-meson ratio divides two signed balancing yields | pair-registry `reference_meson_pdg` | `contracts/GeneratedPairRegistry.h` | `tests/test_baryon_meson_render_contract.py` |
| C14 | Tune differences compare complete bundles, never one setting | `tools/validate_tune_cards.py` | `config/tune_difference_allowlist_v1.json` | `tests/test_three_tune_plot_config.py`; `tests/test_registry.py` |
| C15 | The class axis closes: eleven classes sum to the integrated bin | `tools/vintegrated_closure.py` | `plotting/configuration_multiplicity_HF_RUN3_V1_VINTEGRATED_CLOSURE.json` | `tests/test_vintegrated_closure.py` |
| C16 | The control comparison has the 144 / 132 / 132 shape | `extraction/harvest_class_report.py:108-126` | derived from the closure configuration and the class contract | `tests/test_strict_control_boundary.py` |

## Deliverables

Every row's acceptance record is written by RUN-N. Until then the column reads
`pending RUN-N`, and that is a statement of fact, not a placeholder.

| id | producer | contract | acceptance record |
|---|---|---|---|
| G1 | `plotting/Plot_InclusiveKinematicSpectra_Raw.C:1795`, target `multiplicity-spectrum` | stem `MultiplicitySpectrum_Shared_shape` (`:2192`) | pending RUN-N |
| G2, G3 | the V-CORRELATIONS canvas, `plotting/improvedPlotting_THnSparse.C:4831-4833` | `plotting/configuration_multiplicity_HF_RUN3_V1_VCORRELATIONS.json` | pending RUN-N |
| G4, G6 | V-INTEGRATED globals | `tests/test_delivery_names.py`, `VINTEGRATED` | pending RUN-N |
| G5, G7 | V-EXTREMES globals | `tests/test_delivery_names.py`, `VEXTREMES` | pending RUN-N |
| G8 | V-BARYONMESON global | `tests/test_delivery_names.py`, `VBARYONMESON` | pending RUN-N |
| G9 | `plotting/Plot_InclusiveKinematicSpectra_Raw.C:2196-2221`, target `kinematic-spectra` | thirty stems, ten species × three observables | pending RUN-N |
| T1 | `tools/count_generated_sample.C`; `tools/read_merged_event_counts.C` | `hadronization_generated_sample_count_v1` (`tools/count_generated_sample.C:232`) | pending RUN-N |
| V1 | `tools/vintegrated_closure.py`; `extraction/harvest_class_report.py --strict-control` | 12 identities; 144 / 132 / 132 | pending RUN-N |

Delivery names are in [DELIVERABLES.md](DELIVERABLES.md).

## Three corrections this map carries

**The observable-contract test is not evidence for the selection claims**
(ledger DA1-B093). `tests/test_observable_contract.py` imports only `math` and
`statistics`, opens no file, and imports no repository module. Its five
assertions are arithmetic anchors computed in the file itself, so it stays green
if the C++ OS/SS arithmetic drifts. Its own docstring now says so
(`tests/test_observable_contract.py:9-16`). It is cited above under **C12
only**, for the SEM and ratios-inside-blocks anchors, which is what it actually
pins.

**`hFlavourClosureSummary` is permitted, not required** (ledger DA1-A052,
DA1-A080). `config/pair_file_object_contract_v1.json` marks it
`"presence": "conditional"`, rendered as `PairObjectPresence::kConditional`,
and `PermittedPairObjects` documents absence as not an error. It is written only
when `trigger.weightedTriggers > 0`, so requiring it would fail every rare
species. Row C8 says *permits*.

**Nothing under `tests/` pins the self-pair and shared-parton exclusions**
(ledger DA1-B070). `docs/PHYSICS.md:266` names
`generation/producer/HeavyFlavourUtils.h` as their contract and
`tests/test_heavy_flavour_utils.cpp` as their test; neither file contains either
predicate. Row C6 states the gap instead of citing a test that does not test it.
