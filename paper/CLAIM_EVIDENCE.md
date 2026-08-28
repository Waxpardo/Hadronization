# Manuscript claim-evidence checklist

**Release state:** `PUBLIC-BLOCKED`.

This checklist maps every abstract and summary claim, each numerical claim, and
each planned figure-caption contract to an implementation or committed
artifact. A path is evidence only for the scope stated here. This repository
holds no figure-acceptance authority. Ruling R6 of 2026-08-22 retired
`results/provenance/figure_acceptance_manifest_v1.json`, and session J must
deliver its successor. The repository accepts zero P1-P8 outputs.

## Abstract

| ID | manuscript claim | evidence | release qualification |
|---|---|---|---|
| A1 | PYTHIA 8.317, pp at 13.6 TeV, forced hard-heavy sample | `config/dependencies.conf`; three nominal cards under `generation/cards/`; `config/dataset_selector_hf_run3_v1.json` | Selector authorizes the campaign; raw union remains external. |
| A2 | OS-SS per trigger, factor-one SS, dedicated trigger denominator | `config/heavy_flavour_pair_registry_v1.json`; `config/pair_file_object_contract_v1.json`; `plotting/improvedPlotting_THnSparse.C`; `tests/test_plot_reference_multiplicity_contract.py` | Pair projection is not an admissible trigger count. |
| A3 | Operational narrow counter, tune-local percentile classes, three complete bundles | `generation/producer/HeavyFlavourUtils.h`; `config/multiplicity_percentile_classes_v2.json`; `config/tune_difference_allowlist_v1.json` | Class-dependent evidence is blocked until regeneration with a v2 per-tune boundary receipt. |
| A4 | Activity-dependent beauty redistribution is provisional | `results/systematics/20260819/ratio_trend.json`; `results/systematics/20260820/verdict.json`; `docs/SYSTEMATICS.md` | The two-SEM correction is applied; S4 and the tune-dependent hang-selection bias remain open. |

## Methods, model, and results

| ID | manuscript location | evidence and exact field or contract | status |
|---|---|---|---|
| I1 | Introduction, conditional heavy-flavour observable | `docs/PHYSICS.md`, balancing-yield observable and signed-species sections | Contract statement. |
| I2 | Introduction, 28 differences in nine families | `config/tune_difference_allowlist_v1.json`; `tools/validate_tune_cards.py` | Bundle-to-bundle only. |
| O1 | Signed species and 300 ordered pairs | `config/heavy_flavour_species_v1.json`; `config/heavy_flavour_pair_registry_v1.json`; `tests/test_registry.py` | Generated registries are checked current. |
| O2 | Trigger, associate, origin, self-pair, and shared-parton selections | `generation/producer/HeavyFlavourUtils.h`; `analysis/status_analysis_THnSparse_qq.C`; `tests/test_observable_contract.py` | Status 81-89 is described as direct-primary. |
| O3 | OS, SS, factor one, `hTrKinematics` | `plotting/improvedPlotting_THnSparse.C`; `tests/test_pair_object_contract.py`; `tests/test_plot_reference_multiplicity_contract.py` | Final figure bytes absent. |
| O4 | Full angular axis only | `analysis/status_analysis_THnSparse_qq.C`; `plotting/improvedPlotting_THnSparse.C`; `docs/PHYSICS.md` dated 2026-08-21 scope amendment | Near/away integrals are not claimed; a future regional observable needs a new signed decision and contract. |
| O5 | Signed baryon/reference-meson ratio | Pair-registry `reference_meson_pdg`; `tests/test_baryon_meson_render_contract.py` | Not an inclusive production ratio. |
| O6 | Pooled central and ten-block SEM | `config/statistical_robustness_v1.json`; `docs/STATISTICS.md`; `tests/test_statistical_robustness.py` | Nonlinear quantities are formed inside blocks. |
| M1 | Campaign, energy, PYTHIA, hard processes, threshold | Selector, nominal cards, generated tune registry, and campaign authorization | 13.6 TeV; PYTHIA 8.317; `pTHatMin=2.0`. |
| M2 | 1,000 files x 100,000 events and ten blocks | `config/dataset_selector_hf_run3_v1.json`; `docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md` | External file union cannot be rehashed locally. |
| M3 | Multiplicity counter and decay-policy limitation | `generation/producer/HeavyFlavourUtils.h`; `results/validation/generator/NCH_DECAY_POLICY_BIAS_8317.md`; `results/systematics/20260820/per_class_combination.json`, `S5_class_migration`; `docs/SYSTEMATICS.md` S5 | Exact final/charged/non-heavy/pT/eta predicate; 0.7670% minimum-bias mismatch; exact-zero class migration for current boundaries; forced-sample bias unmeasured. |
| M4 | c1-c11 percentiles and direction | `config/multiplicity_percentile_classes_v2.json`; tune-level merged `summed MULTIPLICITY` histograms | Each tune resolves its own absolute thresholds. |
| M5 | S1-S6 scope and exclusions | `config/systematics_variations_v1.json`; `config/a2_variations_v1.json`; `docs/SYSTEMATICS.md` | S4 missing; S6 separate axis; no detector effects. |
| R1 | Integrated table | `tests/fixtures/integrated_rows_nominal.log` | Labelled validation result; missing `PAIR_COUNTS` blocks exact closure. |
| R2 | Beauty endpoint ratios and contrasts | `results/systematics/20260819/ratio_trend.json`, `endpoint_contrast_c11_minus_c1` | Statistical SEM only in the endpoint table. |
| R3 | Stored total uncertainties on tune contrast differences | `results/systematics/20260820/verdict.json`, `trend` | Provisional; no final significance claim. |
| R4 | No charm ratio trend quoted | Figure-manifest P8 record | Charm matrix and accepted P8 bytes are absent. |
| D1 | External-data boundary | `docs/DATA_AVAILABILITY.md`; `docs/REPRODUCIBILITY.md`, sections 7, 10, and 11 | No public archive or retrieval route. |

## Abstract and conclusion sign-off

- [x] Abstract states generator-level scope and sample identity.
- [x] Abstract names the normalization invariant without implying figure closure.
- [x] Abstract calls the uncertainty-qualified inference provisional.
- [x] Summary attributes differences only to full tune bundles.
- [x] Summary states the missing S4, hang-selection risk, external-data boundary, and zero accepted figures.
- [ ] Release sign-off: blocked until the acceptance manifest records the required accepted outputs and the named scientific blockers close.

## Planned figure-caption contracts

The current PDF emits no scientific figure or caption. These rows are the
checklist a later accepted caption must satisfy. The acceptance manifest
supplies the status ``Candidate''; it does not mean final.

| ID | planned caption claim | required evidence | current result |
|---|---|---|---|
| F0 | No historical or internal image is used | TeX dependency scan; figure manifest `accepted_outputs` | Pass for this build. |
| F1 / P1 | 13.6 TeV shared multiplicity spectrum, narrow counter, common c1-c11 boundaries | P1 manifest record, sealed raw manifest, boundary artifact, receipt, exact bytes | Candidate; not emitted. |
| F2 / P2 | Charm MONASH OS, SS, and OS-SS per-trigger angular correlations with ten-block SEM | P2 record, exact signed channels, `hTrKinematics`, numerical bins, ten blocks, receipt | Candidate; not emitted. |
| F3 / P3 | Beauty MONASH analogue of P2 | P3 record and the same normalization and coverage evidence | Candidate; not emitted. |
| F4 / P4 | Integrated charm balancing yields | V-INTEGRATED source log including `PAIR_COUNTS`, central and ten-block identities, receipt | Candidate; not emitted. |
| F5 / P5 | Charm balancing yields on common classes | V-FULL/V-EXTREMES exact common-point identity and owner/journal layout ruling | Candidate; not emitted. |
| F6 / P6 | Integrated beauty balancing yields | Same accepted V-INTEGRATED closure as P4, with explicit combined/split packaging ruling | Candidate; not emitted. |
| F7 / P7 | Beauty balancing yields on common classes | Same layout and identity requirements as P5 | Candidate; not emitted. |
| F8 / P8 | Signed anti-Lambda-c/D- and Lambda-b/B- balancing-yield ratios | Signed registry, charm and beauty numerical matrices, ten blocks, accepted canvas and receipt | Candidate; not emitted. |
| F9 | Every accepted caption names OS/SS definition, trigger denominator, angular/multiplicity scope, tune scope, and uncertainty | none in this repository; the caption contract is a session-J deliverable | Blocked globally. No figure is accepted, and no caption contract exists here. |

## Bibliography reconciliation

The paper bibliography, `paper/references.bib`, is a six-entry,
DOI-deduplicated subset of the historical draft and of the byte-identical
`References.bib` copy that ruling R23 moved to the project archive. It
contains no `file` fields, local Zotero paths, abstracts, access dates,
undefined keys, or duplicate DOI records. On 2026-08-21, the reconciliation checked the PYTHIA 8.3, Monash,
JUNCTIONS, and CLOSEPACKING primary metadata against the PYTHIA documentation
and publisher or arXiv records.
