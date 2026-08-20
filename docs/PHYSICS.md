# Physics observable

## Scientific question and scope

The study measures which heavy hadrons carry compensating charm or beauty around a hard heavy-flavour trigger.
It resolves species, relative azimuth, and multiplicity class for 300 signed trigger-associate combinations.
The pair registry, `config/heavy_flavour_pair_registry_v1.json`, defines those combinations.

The published quantities are angular correlations, integrated balancing yields, yield ratios, and species decompositions.
The artifacts `docs/systematics_results_20260819/tune_separation.json` and `docs/systematics_results_20260819/ratio_trend.json` contain the derived observables.

## Collision system and PYTHIA comparison

All samples simulate proton-proton collisions at 13.6 TeV with PYTHIA 8.317.
The dependency configuration, `config/dependencies.conf`, pins the PYTHIA and ROOT versions.

Each nominal card enables `HardQCD:hardccbar` and `HardQCD:hardbbbar` with `PhaseSpace:pTHatMin = 2.0`.
PYTHIA therefore constructs a hard charm or beauty pair in every successful event.
The producer, `generation/producer/heavyflavourcorrelations_status.cpp`, stops if a successful event lacks exactly one signed hard pair.

PYTHIA forces the sample; the analysis does not filter it from minimum bias.
It is therefore not a minimum-bias sample.
The three nominal cards under `generation/cards/` define the MONASH, JUNCTIONS, and CLOSEPACKING samples.

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

Uncorrelated combinatorial associates populate both sign counters equally in expectation.
The subtraction cancels this contribution.
The analysis therefore need not identify which heavy hadron is the trigger's true heavy balancing partner.
The reduction macro supplies the two sign counters used by this cancellation.

A yield ratio divides one balancing yield by another.
It does not change either yield's OS-minus-SS definition.
The derived-combination code, `extraction/combine_derived.py`, keeps that distinction explicit.

## Event activity and multiplicity classes

The event-activity counter counts charged primaries with `pT > 0.15 GeV/c` in `|eta| < 1`.
It excludes heavy hadrons because their disabled decays make them artificial final particles and create an autocorrelation.
The producer counter in `generation/producer/HeavyFlavourUtils.h` defines this quantity.

Eleven common, absolute classes use half-integer boundaries.
Each integer `N_ch` therefore belongs to exactly one class.
The artifact `config/multiplicity_class_boundaries_v1.json` is the single class definition.

| multiplicity class | integer `N_ch` | MONASH minimum-bias top-percentile label |
|---|---:|---:|
| `c1` | 0--2 | 88.197--100.000% |
| `c2` | 3 | 80.597--88.197% |
| `c3` | 4--5 | 65.937--80.597% |
| `c4` | 6 | 59.850--65.937% |
| `c5` | 7--8 | 50.308--59.850% |
| `c6` | 9--10 | 43.030--50.308% |
| `c7` | 11--13 | 34.614--43.030% |
| `c8` | 14--17 | 26.154--34.614% |
| `c9` | 18--23 | 17.124--26.154% |
| `c10` | 24--32 | 8.422--17.124% |
| `c11` | 33 and above | 0.000--8.422% |

Class `c1` is the lowest multiplicity class, while `c11` is the highest.
Top-percentile labels count from the most active end, so their numerical direction is opposite to the class order.
The boundary artifact and minimum-bias distribution establish this direction.

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

## Physics limitations and literature context

This work defines a generator-level heavy-flavour correlation, not a detector-level measurement.
The forced hard-pair sample, stable heavy hadrons, broad `|eta| <= 4` pair acceptance, and low associate threshold limit direct comparisons.
The nominal cards and `analysis/status_analysis_THnSparse_qq.C` define these limits.

The quoted sigma values are per-cell and uncorrected across 72 comparisons.
The artifact `docs/systematics_results_20260819/tune_separation.json` contains six observables with twelve cells each.
No global significance or trial correction follows from those values.

The repository has not measured cross-class or cross-observable covariance.
Trend and cell estimates must therefore remain distinct claims.
The files `docs/systematics_results_20260819/ratio_trend.json` and `docs/systematics_results_20260819/tune_separation.json` report those estimates separately.

The final uncertainty calculation combines systematic sources in quadrature.
The repository has not tested their independence.
The artifact `docs/systematics_results_20260820/verdict.json` records the per-source terms and their quadrature totals.

The OS-minus-SS construction follows the logic of identified-particle correlation studies that compare unlike-sign and like-sign pairs.
The hard heavy-flavour trigger and forced generator sample make this observable different from an experimental balance function.
[Graczykowski and Janik](https://doi.org/10.1016/j.nuclphysa.2014.03.004) provide the nearby identified-particle correlation context.

Colour-reconnection models with junction topologies provide context for the compared tune configurations.
They do not identify the cause of any difference measured here.
[Christiansen and Skands](https://doi.org/10.1007/JHEP08(2015)003) describe that model context.
The repository bibliography, `Literature/References.bib`, records both references.
