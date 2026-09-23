# Scientific definitions

[Documentation index](../README.md#documentation)

## Sample and interpretation

[The campaign record](../data/campaign.json) defines pp collisions at sqrt(s) = 13.6 TeV with PYTHIA 8.317. The tune cards enable `HardQCD:hardccbar` and `HardQCD:hardbbbar`. They set `PhaseSpace:pTHatMin = 2.` GeV and disable heavy-hadron decays through generator configuration.

The pTHat threshold constrains hard partonic production. It is not a final-hadron pT threshold. The generator requires the selected heavy hard pair and records origin information. The resulting sample deliberately favors heavy-flavour production.

MONASH, JUNCTIONS and CLOSEPACKING are complete tune bundles. Their parameters change together. The comparison therefore describes conditional generator behavior in this sample. It does not isolate a single parameter or establish predictive coverage, precision ranking or agreement with experimental data.

The output is at generator level. There is no detector response, efficiency correction or systematic-uncertainty calculation. The activity classes are generator multiplicity percentiles, not experimental centrality.

## Sample accounting

[The raw manifest](../data/raw_manifest.jsonl) records 3,000 accepted sources. Each source contains 100,000 successful events. Each tune has 1,000 sources and 100 million successful events.

[The attempt ledger](../data/attempts.csv) records 3,127 job attempts. It identifies 3,000 accepted attempts and 127 discarded attempts. The accounting code preserves evidence-status categories. It does not identify every discarded attempt as the same generator failure.

Job attempts and generator event trials are different counts. The verified inventory does not contain event-trial totals across all submitted attempts. Numerical accounting marks those totals `UNAVAILABLE`. It does not infer them from successful events or job counts.

Each source has a tune, logical job ID, attempt ID and original block. Block membership is `block = (logical_id % 10) + 1`. Ten original blocks each contain 10 million successful events per tune. Query sharding and physical merging do not change these blocks.

## Particle identities and origins

The selected-state registry in [study.json](../config/study.json) contains signed PDG identities, heavy valence, electric charge and structural eligibility. The generated [C++ contract](../pipeline/generate/study_contract.hpp) binds those exact bytes. The active downstream model is [analysis.json](../config/analysis.json).

The default displayed triggers are D0 (421), Lambda_c+ (4122), B+ (521) and Lambda_b0 (5122). D+ (411) can replace D0 through `--charm-trigger 411`. The matching presentation configuration is `config/plot-dplus.json`.

A structural trigger must be final, selected and directly produced with absolute PYTHIA status from 81 through 89. It must carry one unit of the relevant heavy flavour. Its ancestry must identify one selected hard-process root. Separate trigger rows retain eligible triggers with no qualifying associate.

Associates use configured signed species in the same heavy-flavour sector. They must satisfy final-state and direct-hadronization conditions. The pair query also applies the registry's structural eligibility. It excludes self-pairs. Associate origins include selected-hard companions, showers, multiple parton interactions, other resolved origins and unresolved origins.

The six signed states with absolute PDG 5212, 5312 or 5322 are ineligible for central pair analysis. The query retains selected heavy kinematics independently of that pair exclusion. The data model also retains natural heavy states for constituent and closure accounting.

Define q_c = n_c - n_anticharm and q_b = n_b - n_antibeauty. Opposite-sign pairs have a negative product of the relevant heavy-flavour signs. Same-sign pairs have a positive product. Neutral particles participate through heavy valence, not electric charge.

For example, B+ (521) contains an antibeauty quark. Positive-PDG Lambda_b0 (5122) contains a beauty quark. These form an opposite-heavy-flavour-sign channel. A plot label must not replace the signed registry identity.

## Pair selection

The default `inclusive` profile imposes no fixed final-hadron pT floor. Particle pT must be finite and nonnegative. Both particles must have |eta| <= 4. There is no event-wise comparison between trigger and associate pT.

An optional rectangular profile specifies two finite, nonnegative minima. The trigger minimum must be greater than or equal to the associate minimum. Each cut uses `pT >= minimum`. Each minimum must coincide with a regular query-bin lower edge. High-pT overflow remains included.

The model accepts equal minima. A pair with associate pT above trigger pT can pass. The model refuses a non-null `relative_pt` field. It also refuses strict thresholds and off-edge minima for this sparse projection route.

The azimuthal coordinate is trigger phi minus associate phi. The implementation wraps it into [-pi/2, 3pi/2). The query uses 100 equal bins. The lower endpoint is inclusive and the upper endpoint is exclusive.

## Charged-light activity

Nominal activity counts final charged particles without charm or beauty constituents. It requires finite kinematics, pT > 0.15 GeV/c and |eta| <= 4. The corresponding event field is `a15_eta4`. The alternate `a15_eta1` field uses |eta| <= 1.

This threshold belongs to the activity definition. It does not apply to inclusive heavy-particle pairs or signed heavy-hadron spectra. The count is a charged-light final-particle activity measure. It does not implement a separate experimental primary-particle classification with explicit weak-daughter removal.

The activity axis stores integers from 0 through 4095. Each integer occupies one regular bin. Values outside the supported domain fail the scientific contract rather than silently extending the axis.

## Multiplicity classes

The default percentile intervals are 0–1%, 1–10%, 10–20%, through 90–100%. A separate integrated class covers 0–100%. Each tune resolves its own integer boundaries from its weighted activity distribution.

For percentile p, the threshold is the first ascending integer whose cumulative weight reaches (100-p)/100 of the total. A threshold integer belongs to the lower-activity class. The higher-activity class starts at the next integer.

For [p_low, p_high], the integer lower bound is threshold(p_high)+1, except that p_high = 100 gives zero. The upper bound is threshold(p_low), except that p_low = 0 gives 4095. Discrete ties can produce unequal event fractions or empty classes.

Every aggregate activity bin must be nonnegative and the total must be positive. The implementation can retain signed event weights under these constraints. Reduction recalculates boundaries after each source-block deletion. A changed or statistically unresolved boundary withholds affected class uncertainty without deleting a valid pooled center.

## Observables

### Identified balancing species

The default numerical request selects nine associate species per trigger. Integrated and activity-dependent balancing use the same selection.

| Sector | Mesons | Baryons |
| --- | --- | --- |
| Charm | D0, D+, Ds+ | Lambda_c+, Sigma_c+, Sigma_c0, Sigma_c++, Xi_c+, Xi_c0 |
| Beauty | B+, B0, Bs0, Bc+ | Lambda_b0, Sigma_b+, Sigma_b-, Xi_b0, Xi_b- |

The table names particle families. The trigger's heavy-flavour sign determines the opposite-sign particle or antiparticle. The estimator subtracts its same-sign conjugate.

Each charge state remains a separate category. The figures do not sum Sigma or Xi charge states. The numerical ROOT retains their joint jackknife covariance.

Figures show mesons before baryons. Baryon groups follow the order Lambda, Sigma, then Xi. Mass sets the order within each group. Short ticks delimit species bins, and labels sit at bin centers.

Ds and Xi add strange meson and baryon comparisons. Sigma adds direct heavy-baryon production beyond Lambda. Heavy-hadron decays remain disabled, so Sigma particles do not feed down into the saved Lambda category.

Each numerical ROOT file records its own selected species. The renderer retains that selection. A new [reduction](workflow.md#numerical-reduction) can select these categories from the existing merged query without rebuilding it.

### Definitions

Let w_e denote event weight. Let T_t denote the weighted number of eligible triggers of species t in the selected class. Let N_OS and N_SS denote weighted ordered-pair counts with the requested associates. A trigger contributes to T_t even when both pair counts are zero.

For azimuthal bin b, let delta_b denote its width in radians. The identified pair observables are bin-averaged densities:

$$C_{OS,b}=\frac{N_{OS,b}}{T_t\,\delta_b},\qquad C_{SS,b}=\frac{N_{SS,b}}{T_t\,\delta_b}.$$

The sign-summed correlation difference is

$$C_{net,b}=\frac{N^{all}_{OS,b}-N^{all}_{SS,b}}{T_t\,\delta_b}.$$

Here, “all” means all structurally eligible registered associates in the selected heavy-flavour sector. It does not mean all generated particles. The default lower correlation panel uses this sign-summed difference. It is not a ratio of OS minus SS to OS plus SS.

Each density uses its own stored bin width. The estimator applies this division to the pooled result and every deletion. Joint covariance therefore includes the width factors on both axes. A sum of densities times their bin widths gives the integrated yield for the same associate domain.

The numerical quantity `dphi_density_per_trigger` has units `per_trigger_per_radian`. Formula contract `projection_formulas_v3` identifies this convention and the eligible central pair domain. The reader retains the earlier `dphi_per_trigger` quantity with units `per_trigger_per_bin`. The renderer labels each convention from the numerical archive and rejects mixed conventions within a panel.

The integrated balancing yield for an opposite-sign species a is

$$B_{t,a}=\frac{N(t,a)-N(t,\bar a)}{T_t}.$$

The partner bar denotes the conjugate signed PDG identity. There is no half-weight on the same-sign term. Integration covers the complete supported azimuthal interval. Activity-dependent balancing applies the same formula within each tune-local class.

The baryon-to-meson observable divides two balancing yields with the same trigger. The default signed tuples `(trigger, baryon, reference)` are `(421, -4122, -421)` and `(521, 5122, -521)`. The D+ selection changes the charm tuple to `(411, -4122, -411)`.

A tune comparison divides the complete observable by the corresponding reference-tune observable. MONASH is the default reference. Shared references create covariance between ratios.

The multiplicity distribution divides each weighted activity-bin count by the total event weight. Signed heavy-hadron spectra divide each weighted species-bin count by the selected same-species total. These two histogram families report probabilities per bin. They do not divide by bin width.

Signed spectra select final registered direct-hadronization states with |eta| <= 4 and no fixed pT floor. They include all origins. The pT denominator includes overflow. Eta and phi use inclusive physical endpoints in the last regular bin.

Natural-heavy accounting has no kinematic acceptance cut. It counts final stored heavy hadrons and their charm and beauty constituents. Hidden heavy flavour contributes both constituents. Raw counts have no sampling error attached. Per-successful-event yields use the statistical estimator below.

## Jackknife and covariance

The authoritative estimator uses ten original source blocks per tune. It first pools additive counts and weights across the complete selected sample. It evaluates each nonlinear observable from these pooled primitives. The reported center is not the mean of block estimates or a bias-corrected jackknife center.

For tune f and omitted block k, let theta_(f,-k) denote the recomputed estimator. Other tunes remain at their complete-sample values. Each deletion recomputes affected class boundaries, trigger denominators, signed differences and ratios.

Let the mean of the ten deletions in family f be bar(theta)_f. The covariance is

$$C_{ij}=\sum_f\frac{9}{10}\sum_{k=1}^{10}
(\theta_{f,-k,i}-\bar\theta_{f,i})
(\theta_{f,-k,j}-\bar\theta_{f,j}).$$

The standard error is sqrt(C_ii). A single-tune observable has one deletion family. A ratio of two independent tunes has two families. The implementation sums their covariance contributions. It does not pair equal-numbered blocks across tunes or treat thirty blocks as one family.

The archive stores joint deletion factors with point keys and validity masks. Each valid factor is sqrt(9/10) times its centered deletion. Their Gram matrix recovers covariance across bins, signs, species, classes and shared references. Consumers must align tune-family identities and point keys before combining factors.

A denominator must pass numerical existence checks. Denominators that survive algebraic cancellation also undergo statistical-resolution and deletion-sign checks. The statistical screen uses a two-sided t quantile of 2.2621571628540993 for nine degrees of freedom. Algebraically cancelled denominators still require numerical existence.

A finite negative center can be valid. A missing uncertainty is not zero. Exact zero dispersion is valid only after all prerequisites pass. The archive distinguishes materialization, center validity, uncertainty validity and covariance validity. See [status semantics](data-model.md#status-semantics).

This block jackknife estimates finite-sample variability under the original block design. It does not measure model uncertainty. There is no production switch to ordinary subsampling in the public CLI.

## Definition authority

[physics.hpp](../pipeline/generate/physics.hpp) implements raw particle and ancestry rules. [model.py](../pipeline/query/model.py) validates downstream selections and the signed registry. [native_engine.cpp](../pipeline/reduce/native_engine.cpp) and [statistics.hpp](../pipeline/reduce/statistics.hpp) evaluate observables and covariance.

The numerical archive records the resolved model, source identities, class boundaries and estimator policy. The renderer consumes that archive. Presentation configuration controls layout and display selection, not formulas or statistical errors.

The fixed raw compatibility contract contains selection and statistical labels that do not configure downstream reduction. Use `config/analysis.json` and the numerical request for the active pair, activity and jackknife definitions. A change to checksum-bound raw metadata does not change the scientific meaning of existing data.
