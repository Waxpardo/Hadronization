# Physics observable

## Scientific question and scope

The study measures which heavy hadrons carry compensating charm or beauty around a hard heavy-flavour trigger.
It resolves species, relative azimuth, and multiplicity class for 300 signed trigger-associate combinations.
The pair registry, `config/heavy_flavour_pair_registry_v1.json`, defines those combinations.

The published quantities are angular correlations, integrated balancing yields, yield ratios, and species decompositions.
The artifacts `results/systematics/20260819/tune_separation.json` and `results/systematics/20260819/ratio_trend.json` contain the derived observables.
Accepted scientific canvases are ROOT-derived by `plotting/run_paper_plots.sh` and enter `results/figures/main/` only with exact dataset identity, ten-block uncertainties, a receipt, and visual review.
The required campaign inputs are external, and no complete accepted figure-byte set travels with this checkout.

## Collision system and PYTHIA comparison

All samples simulate proton-proton collisions at 13.6 TeV with PYTHIA 8.317.
The dependency configuration, `config/dependencies.conf`, pins the PYTHIA and ROOT versions.

Each nominal card enables `HardQCD:hardccbar` and `HardQCD:hardbbbar` with `PhaseSpace:pTHatMin = 2.0`.
PYTHIA therefore constructs a hard charm or beauty pair in every successful event.
The producer, `generation/producer/heavyflavourcorrelations_status.cpp`, stops if a successful event lacks exactly one signed hard pair.

PYTHIA forces the sample; the analysis does not filter it from minimum bias.
It is therefore not a minimum-bias sample.
The three nominal cards under `generation/cards/` define the complete MONASH, JUNCTIONS, and CLOSEPACKING tune bundles.

The multiplicity labels come from a separate MONASH minimum-bias sample.
The minimum-bias manifest, `AnalysisScripts/anchors/b4_multiplicity_mb/MANIFEST.md`, records that sample and its generator settings.

## Heavy-flavour signs, species, and roles

Heavy-flavour sign follows quark content, not electric charge:

\[
q_c=n_c-n_{\bar c}, \qquad q_b=n_b-n_{\bar b}.
\]

The utility `generation/producer/HeavyFlavourUtils.h` computes these signed contents from the PYTHIA particle record.

The B⁺ meson contains an anti-bottom quark, so `q_b = -1`.
The Λ_b⁰ baryon contains a bottom quark, so `q_b = +1`.
The B⁺–Λ_b⁰ pair is therefore opposite-sign, despite carrying electric charges +1 and 0.
The files `config/heavy_flavour_species_v1.json` and `config/heavy_flavour_pair_registry_v1.json` encode these signs.

The registry contains 50 signed associate species and 12 signed trigger species.
It lists each charge conjugate explicitly.
All 24 charm associates and 20 of 26 beauty associates meet the central species rule.
The species registry, `config/heavy_flavour_species_v1.json`, records each role and eligibility decision.

## Event and pair selection

The reduction requires final, direct-primary, central-ground heavy hadrons within the role-dependent kinematic limits.
Triggers require `pT > 1.0 GeV/c`; associates require `pT > 0.15 GeV/c`.
Both roles require `|eta| <= 4`.
The reduction macro, `analysis/status_analysis_THnSparse_qq.C`, implements these cuts with `generation/producer/HeavyFlavourUtils.h`.

Only the trigger requires resolved ancestry from the selected hard process.
The associate can come from the selected hard process, shower, MPI, another resolved source, or an unresolved source.
The origin contract, `AnalysisScripts/AssociateOriginCategoryContract.h`, defines these associate categories.

This asymmetry preserves the same-sign term.
The event contains one selected hard quark and one selected hard antiquark, with at most one final carrier for each.
Two distinct selected-hard carriers therefore have opposite signs.
If both roles required selected-hard ancestry, the selection would remove same-sign pairs by construction.
The exact-pair and unique-carrier checks in the producer establish these constraints.

`kUnresolved` removes trigger candidates only.
The reduction retains unresolved candidates as associates because it applies no associate-origin requirement.
The producer and `analysis/status_analysis_THnSparse_qq.C` implement this deliberate difference.

The reduction excludes self-pairs and two hadrons claiming the same selected hard parton.
These checks prevent one physical carrier from contributing twice.
The reduction macro applies both exclusions before filling a pair histogram.

## Balancing-yield observable

For a trigger species and associate species, the angular observable is

\[
B(\Delta\varphi)=\frac{1}{N_{\mathrm{trig}}}
\left(\frac{dN_{\mathrm{OS}}}{d\Delta\varphi}
-\frac{dN_{\mathrm{SS}}}{d\Delta\varphi}\right).
\]

The integrated balancing yield is

\[
Y_{\mathrm{bal}}=\frac{N_{\mathrm{OS}}-N_{\mathrm{SS}}}{N_{\mathrm{trig}}}.
\]

The OS and SS projections use the same trigger count.
The subtraction uses an SS factor of one, not one half.
The plotter `plotting/improvedPlotting_THnSparse.C` performs this normalization after the reduction fills both counters.
It obtains `N_trig` from the dedicated trigger-kinematics object `hTrKinematics`, not from a pair-correlation projection.

Uncorrelated combinatorial associates populate both sign counters equally in expectation.
The subtraction cancels this contribution.
The analysis therefore need not identify which heavy hadron is the trigger's true heavy balancing partner.
The reduction macro supplies the two sign counters used by this cancellation.

A yield ratio divides one balancing yield by another.
It does not change either yield's OS-minus-SS definition.
The derived-combination code, `extraction/combine_derived.py`, keeps that distinction explicit.

## Event activity and multiplicity classes

The event-activity counter is operationally final charged non-heavy, not an
unqualified experimental-primary count. The predicate in
`generation/producer/HeavyFlavourUtils.h` is exactly `isFinal && isCharged &&
!hasHeavyConstituent && pT > 0.15 && abs(eta) <= 1`. The cards set
`ParticleDecays:tau0Max = 0.01` mm; the tested PYTHIA particle table has no
light-hadron state between that cutoff and the conventional 10 mm primary
threshold. Heavy-hadron decays are disabled, and heavy hadrons are excluded
because their artificial stability would create an autocorrelation.

The paired PYTHIA 8.317 MONASH minimum-bias calibration remains useful for
counter studies, but it no longer defines class membership. Its former
zero-migration statement was conditional on a superseded common absolute axis.

Eleven tune-local classes use top-percentile windows `90-100, 80-90, ...,
1-10, 0-1%`. Each tune derives all absolute `N_ch` thresholds from its own
merged `summed MULTIPLICITY` histogram. Integer ranges are disjoint and
exhaustive, so every accepted event belongs to exactly one class. The artifact
`config/multiplicity_percentile_classes_v2.json` is the single class-window
definition; a v2 run receipt records the tune-specific thresholds.

Class `c1` is the lowest-activity class (`90-100%` from the most-active end),
while `c11` is the highest (`0-1%`). Equal percentile labels compare equal
activity fractions across tune bundles, not equal absolute `N_ch` intervals.

The labels derive from 172,429 MONASH minimum-bias events, not from the forced hard-pair sample.
The distribution and manifest under `AnalysisScripts/anchors/b4_multiplicity_mb/` provide the counts.

The 8.317 MONASH distribution has mean `N_ch = 12.948` in the nominal window.
The committed distribution and `config/dependencies.conf` establish the value and generator version.

## Structural and experiment-comparable decompositions

The structural decomposition partitions every species into four ordinal categories.
These categories are central ground, excluded vector, excluded excited, and multiply heavy.
Their shares sum to 100 percent for every tune.
The ordinal table, `AnalysisScripts/species_ordinals_v2.json`, supplies the category for each of its 202 signed species.

The experiment-comparable selection asks which selected ground-state rows receive the species weight after the decay map.
Its ten rows are D0, anti-D0, D+, D-, Ds+, Ds-, Lambda-c+, anti-Lambda-c, B+, and B-.
This row set is a selection, not a partition, and does not sum to 100 percent.
The extractor `extraction/three_tune_table.py` fixes both row sets and checks their different sum rules.

The complete mapped regrouping conserves total weight, including unselected and unmapped rows.
The published experiment-comparable selection shows only its named ten rows.
The map reader, `extraction/apply_decay_map.py`, checks total conservation before reporting any row.

Associate origin provides a separate decomposition.
It distinguishes selected-hard companions, selected-hard noncompanions, shower, MPI, other resolved, and unresolved associates.
The file `AnalysisScripts/AssociateOriginCategoryContract.h` defines those six categories.

## Decay maps and ground-state mapping

Version 1 of the decay map copied unconjugated daughter identities into antiparticle rows.
With the anchor weights, it assigned 59,678,352 units to D0 and 13,298,376 to anti-D0.
Their difference was 46,379,976 units.
The four neutral and charged D-star states contributed 46,362,600 units, leaving only 17,376 units of that difference.
The v1 map, anchor weights, and map reader reproduce these values.

Version 1.1 conjugated every antiparticle product and retained the same total weight.
It changed the D0 and anti-D0 weights to 36,539,688 and 36,437,040.
The historical constants in `extraction/second_branch_weight.py` pin the v1 values.
The v1.1 map and `AnalysisScripts/anchors/extraction_dual/per_species.csv` reproduce the corrected arithmetic through the map reader.

The defect changed charge-separated mapped rows, not the structural partition or total weight.
Version 1.1 supersedes version 1 for dominant-channel comparisons.
Version 2 supersedes both maps for the published branching-fraction-weighted selection.

Version 2 uses branching fractions from PYTHIA 8.317 particle data, not the Particle Data Group tables.
It retains 202 species and splits two D-star species above its registered threshold.
D-star+ maps 0.677 to D0 and 0.323 to D+.
D-star- maps 0.677 to anti-D0 and 0.323 to D-.
The version 2 map, `AnalysisScripts/decay_parent_map_v2.json`, records these fractions and its source.

The earlier dominant-only map supported three risk measures.
The single-hop lost-branch weight was 12.8400 percent, while the recursive value was 12.8451 percent.
Species below a dominant branching fraction of 0.80 carried 35.7910 percent of the total weight.
Four D-star states contributed 97.81 percent of the recursive risk.
The risk calculator reproduces these measures from `AnalysisScripts/anchors/extraction_dual/per_species.csv`.

Version 2 therefore splits the two signed D-star rows that redirect weight between ground states.
On the corrected central extraction, the remaining unsplit risk is 0.0017 percent and comes from Bc+ and Bc-.
The files `extraction/second_branch_weight.py`, `AnalysisScripts/anchors/merged_monash_dedup/central/per_species.csv`, and `AnalysisScripts/decay_parent_map_v2.json` reproduce these results:

```bash
python3 extraction/second_branch_weight.py \
  --per-species AnalysisScripts/anchors/merged_monash_dedup/central/per_species.csv \
  --v2-map AnalysisScripts/decay_parent_map_v2.json
```

The experiment-comparable selection is only a branching-fraction-weighted regrouping onto ground states.
It applies no decay kinematics, acceptance, efficiency, resolution, or bin migration.
The repository applies no detector model.

A species remains under an `UNMAPPED` category when the map cannot reach a central ground state.
The reader retains that weight instead of assigning an unsupported ground state.
The map reader implements this fallback.

## Interpretation of tune differences

The comparison is bundle-to-bundle among three full tune configurations.
The cards differ in 28 parameters across nine setting families.
Eight parameters belong to `ColourReconnection`.
The allowlist `config/tune_difference_allowlist_v1.json` records every permitted difference, and `tools/validate_tune_cards.py` checks the cards.

| setting family | differing parameters |
|---|---:|
| `BeamRemnants` | 2 |
| `ClosePacking` | 7 |
| `ColourReconnection` | 8 |
| `MultipartonInteractions` | 1 |
| `Ropewalk` | 1 |
| `StringFlav` | 3 |
| `StringFragmentation` | 2 |
| `StringPT` | 1 |
| `StringZ` | 3 |

The cards set three `StringFlav` and three `StringZ` parameters, which set baryon production directly.
The comparison does not vary these or any other family independently.
The three nominal cards and allowlist establish these settings.

PYTHIA indexes `StringFlav:probQQ1toQQ0join` by the heavier quark entering the diquark, capped at bottom.
A light up-down diquark therefore uses the first vector entry for both charm and beauty baryons.
The [PYTHIA 8.317 source](https://gitlab.com/Pythia8/releases/-/blob/pythia8317/src/FragmentationFlavZpT.cc) establishes this parameter meaning.
It does not establish how frequently any production path uses that entry.

The artifacts measure differences in yields, ratios, and decompositions between complete configurations.
They do not isolate colour reconnection, junctions, close packing, `StringFlav`, `StringZ`, or any other mechanism.
Any causal attribution would require a controlled configuration that changes only the proposed cause.

## Claim-to-contract matrix

This matrix is the release-facing trace from each main scientific statement to the repository object that defines, implements, tests, and evidences it.
An editable source states intent; a generated contract prevents consumers from carrying a second copy.
Committed evidence establishes only the scope named in its row and does not replace the external raw and merged inputs.

| scientific claim | editable source | generated contract | implementation | source-contract test | committed evidence | manuscript consequence |
|---|---|---|---|---|---|---|
| Proton-proton collisions at 13.6 TeV | three nominal cards in `generation/cards/`; `config/tune_difference_allowlist_v1.json` | `generation/registries/GeneratedTuneSettingRegistry.h` | `generation/producer/heavyflavourcorrelations_status.cpp` records and checks effective settings | `tests/test_registry.py`; `tests/test_systematics_variation_cards.py` | `docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md`; `AnalysisScripts/anchors/closure_v3_verdicts/MANIFEST.md` | State pp at 13.6 TeV; do not inherit the historical 14 TeV label. |
| PYTHIA 8.317 and ROOT 6.30.01 | `config/dependencies.conf` | none; both are runtime assertions rather than generated headers | `setupEnv.sh`; `tools/environment_verdict.sh` | `tests/test_pythia_runtime_contract.py`; `tests/test_environment_verdict.py` | `results/validation/plotting/hf_run3_v1_kinematics_20260817/RUN_RECORD.md`; closure logs under `AnalysisScripts/anchors/closure_v3_verdicts/` | Quote both pins with every accepted result; an off-pin render is diagnostic. |
| Forced hard-heavy sample with `HardQCD:hardccbar`, `HardQCD:hardbbbar`, and `pTHatMin = 2.0 GeV` | nominal cards; common values in `config/tune_difference_allowlist_v1.json` | `generation/registries/GeneratedTuneSettingRegistry.h` | producer requires exactly one signed selected-hard pair in every successful event | `tests/test_heavy_flavour_utils.cpp`; `tests/test_registry.py` | `results/validation/generator/PTHAT_MULTIPLICITY_SCAN_8317.md`; campaign authorization | Call this a forced hard-heavy sample, never minimum bias. |
| Species roles and heavy-flavour signs follow signed quark content | `config/heavy_flavour_species_v1.json`; `config/heavy_flavour_pair_registry_v1.json` | `AnalysisScripts/GeneratedPairRegistry.h`; `AnalysisScripts/GeneratedSpeciesOrdinals.h` | `generation/producer/HeavyFlavourUtils.h`; reduction registry lookup | `tests/test_registry.py`; `tests/test_heavy_sign_production_convention.py` | central and block `per_species.csv` products under `AnalysisScripts/anchors/merged_*_dedup/` | OS and SS mean opposite and equal heavy-flavour sign, not electric charge. |
| Trigger: final direct-primary central ground state, `pT > 1.0 GeV/c`, `|eta| <= 4`; associate: the same status/state rules, `pT > 0.15 GeV/c`, `|eta| <= 4` | species registry and constants in `generation/producer/HeavyFlavourUtils.h` | pair-file metadata fields in `AnalysisScripts/GeneratedPairObjectContract.h` | `EligibleBase` in `analysis/status_analysis_THnSparse_qq.C` | `tests/test_pair_contract_schema_prefix.py`; `tests/test_heavy_flavour_utils.cpp` | v3 closure logs and the three extraction-anchor manifests | Describe status 81--89 as direct primary, not prompt. |
| Trigger ancestry must resolve to the selected hard process; associate origin is unrestricted and recorded in six categories | origin rules in `generation/producer/HeavyFlavourUtils.h`; `AnalysisScripts/AssociateOriginCategoryContract.h` | none; the shared category header is compiled directly by producer-adjacent and reduction code | producer origin graph and reduction trigger-only origin cut | `tests/test_associate_origin_category_contract.py`; `tests/test_final_origin_closure.py` | `results/a2/20260813/results/A2_DELTA_RESULT.md`; origin-resolved extraction anchors | Do not impose a prompt or selected-hard associate requirement in prose. |
| Self-pairs and pairs sharing the same selected hard parton are excluded | `generation/producer/HeavyFlavourUtils.h` | pair identity and selected-hard indices in the raw/pair contracts | pair loop in `analysis/status_analysis_THnSparse_qq.C` | `tests/test_observable_contract.py`; `tests/test_heavy_flavour_utils.cpp` | v3 closure and extraction anchors | The conditional yield never counts one carrier twice. |
| `OS`, `SS`, and `OS-SS` are registry-selected ordered conditional pairs; the SS factor is exactly 1 | pair registry; plotting configurations | `AnalysisScripts/GeneratedPairRegistry.h`; pair metadata `same_sign_pair_factor` | `ResolveConfiguredPairFromRegistry` and `calculateOneYield` in the ROOT plotter | `tests/test_plot_reference_multiplicity_contract.py`; `tests/test_observable_contract.py` | three-tune plotting run record and central tables | Write `(OS-SS)/N_trig`; never use the legacy one-half factor. |
| Trigger normalization comes only from a dedicated trigger count | `config/pair_file_object_contract_v1.json` | `AnalysisScripts/GeneratedPairObjectContract.h` requires additive `hTrKinematics` and `hFlavourClosureSummary` | the balancing plotter projects `hTrKinematics` and requires matching OS/SS denominators; the closure diagnostic uses the summary's trigger bin; pair projections supply numerators only | `tests/test_pair_object_contract.py`; `tests/test_plot_reference_multiplicity_contract.py` | plotting run record; ten-block uncertainty logs | Do not normalize a yield by a trigger projection from `hCorrelations`. |
| The stored angular axis is `-pi/2 <= Delta phi < 3pi/2`; the reported integrated yield covers that full axis | pair-object configuration | generated pair-object contract identifies `hCorrelations` but declares no regional boundary | `MakeCorrelation` in the reduction and full-histogram `Integral()` in `calculateOneYield` | `tests/test_statistical_robustness.py`; `tests/test_pair_object_contract.py` | ROOT plotting run record | Near-side and away-side may describe features of the distribution, but no near-side or away-side integrated yield is currently defined or evidenced. |
| Event activity counts final charged non-heavy particles with `pT > 0.15 GeV/c` and `|eta| <= 1`; eleven percentile windows are resolved independently per tune | `config/multiplicity_percentile_classes_v2.json`; multiplicity utility | generated class labels and v2 receipt schema | producer counter; ROOT per-tune threshold resolution and partition validation | `tests/test_multiplicity_inset_boundary_source.py`; `tests/test_plot_reference_multiplicity_contract.py`; `tests/test_harvest_class_axis.py`; `tests/test_supervisor_decisions.py` | tune-level merged `summed MULTIPLICITY`; v2 plotting boundary receipt | Use `c1` through `c11` as equal-fraction activity classes. Do not require common absolute `N_ch` thresholds. |
| Central values use the complete pooled union; uncertainty is the standard error across ten disjoint equal-exposure block estimators | `config/statistical_robustness_v1.json`; `docs/STATISTICS.md` | pair-object additive/identity scopes in `AnalysisScripts/GeneratedPairObjectContract.h` | manifest merge, ROOT block estimator, and extraction block combiners | `tests/test_statistical_robustness.py`; `tests/test_pair_object_contract.py`; `tests/test_decompose_exit_status.py` | three central plus thirty block extraction products; v3 closure logs | Do not call the central value a mean of blocks; form nonlinear ratios inside each block. |
| A species/reference-meson ratio divides two signed balancing yields selected by the pair registry | pair registry `reference_meson_pdg` fields | `AnalysisScripts/GeneratedPairRegistry.h` and pair metadata | ROOT reference selection and within-block ratio calculation | `tests/test_plot_reference_multiplicity_contract.py`; `tests/test_baryon_meson_render_contract.py` | integrated-row fixtures and three-tune result tables | Call it a balancing-yield ratio. It is not an inclusive baryon/meson production ratio. |
| Tune differences compare the complete MONASH, JUNCTIONS, and CLOSEPACKING bundles | three nominal cards; `config/tune_difference_allowlist_v1.json` | `generation/registries/GeneratedTuneSettingRegistry.h` | producer tune ordinal and three-tune plotting configuration | `tests/test_three_tune_plot_config.py`; `tests/test_registry.py` | `docs/THREE_TUNE_CENTRAL_TABLE.md`; three extraction-anchor manifests | Attribute differences to bundles, not isolated colour-reconnection, junction, or close-packing mechanisms. |
| Systematic campaigns cover scale, PDF, generation-threshold, activity-window, and origin variations; every class-dependent combination must be regenerated on the tune-local axes and detector response remains absent | `config/systematics_variations_v1.json`; `config/a2_variations_v1.json`; `docs/SYSTEMATICS.md` | generated variation cards and harvest configurations | separate variation campaigns and combination scripts | `tests/test_systematics_variation_cards.py`; `tests/test_combine_per_class.py`; `tests/test_combine_derived.py`; `tests/test_systematics_delta.py` | historical records under `results/systematics/`; new v2 receipts pending | The former common-axis S5 zero-migration result is superseded; combined verdicts remain blocked until regeneration. |

## Scientific release blockers from the contract audit

The matrix exposes four disagreements or missing contracts that documentation must not present as settled.

### Regional integration

No editable configuration, generated contract, test, or accepted evidence defines near-side and away-side integration boundaries.
`analysis/status_analysis_THnSparse_qq.C` books the full angular axis and `plotting/improvedPlotting_THnSparse.C` integrates the full histogram.
The dated 2026-08-21 owner ruling selects that full axis as the currently
supported integrated observable. This amendment does not alter earlier frozen
preregistrations. A manuscript may report the distribution and full-axis
integral; regional integrals require a later signed group decision, a new
reviewed contract, and regenerated evidence.

### Derived systematic errors

The dated 2026-08-21 correction applies the documented independent nominal and
variation SEMs in `extraction/combine_derived.py` and regenerates
`results/systematics/20260820/verdict.json` as schema v2. Four two-sigma
classifications change. The remaining S4 and hang-selection blockers still
prohibit a final derived-systematic significance claim.

### Pair-schema sidecar

The 2026-08-21 remediation makes `analysis/run_status_analysis.sh` derive the sidecar schema from the producer declaration and checks that declaration against `config/pair_file_object_contract_v1.json`.
The pair-directory validator now reports the schema common to all 300 files, and `tools/validate_analysis_outputs.py` requires it to match the sidecar.
This closes the source-level disagreement for new reductions; existing external job sidecars still require revalidation or regeneration before they can supply that evidence.

### Systematic configuration derivation

`tools/make_harvest_configs.py --check` now accepts all seven committed systematic plotting configurations.
Campaign storage routes come from their active selectors, and all configurations copy the evidence-derived common labels from the central template, including `59.8` rather than the rejected `59.9` spelling.
The retained results remain evidence of recorded campaigns only: configuration agreement does not rerun the external harvest or make its historical renders current.

The accepted ROOT-derived figure bytes, final receipts, and external central and ten-block inputs are also absent from this checkout.
That external-data boundary blocks publication closure without changing any numerical result here.

## Physics limitations and literature context

This work defines a generator-level heavy-flavour correlation, not a detector-level measurement.
The forced hard-pair sample, stable heavy hadrons, broad `|eta| <= 4` pair acceptance, and low associate threshold limit direct comparisons.
The nominal cards and `analysis/status_analysis_THnSparse_qq.C` define these limits.

The quoted sigma values are per-cell and uncorrected across 72 comparisons.
The artifact `results/systematics/20260819/tune_separation.json` contains six observables with twelve cells each.
No global significance or trial correction follows from those values.

The repository has not measured cross-class or cross-observable covariance.
Trend and cell estimates must therefore remain distinct claims.
The files `results/systematics/20260819/ratio_trend.json` and `results/systematics/20260819/tune_separation.json` report those estimates separately.

The final uncertainty calculation combines systematic sources in quadrature.
The repository has not tested their independence.
The artifact `results/systematics/20260820/verdict.json` records the per-source terms and their quadrature totals.

The OS-minus-SS construction follows the logic of identified-particle correlation studies that compare unlike-sign and like-sign pairs.
The hard heavy-flavour trigger and forced generator sample make this observable different from an experimental balance function.
[Graczykowski and Janik](https://doi.org/10.1016/j.nuclphysa.2014.03.004) provide the nearby identified-particle correlation context.

Colour-reconnection models with junction topologies provide context for the compared tune configurations.
They do not identify the cause of any difference measured here.
[Christiansen and Skands](https://doi.org/10.1007/JHEP08(2015)003) describe that model context.
The repository bibliography, `references/References.bib`, records both references.
