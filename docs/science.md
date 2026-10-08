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

The selected-state registry in [study.json](../config/study.json) contains signed PDG identities, heavy valence, electric charge and structural eligibility. The generated [C++ contract](../pipeline/generate/study_contract.hpp) binds those exact bytes. Historical products use [analysis.json](../config/analysis.json); the current complete fine-species construction uses [analysis-all-origin.json](../config/analysis-all-origin.json) and its independently pinned [heavy catalog](../config/heavy-catalog.json).

The default displayed triggers are D0 (421), Lambda_c+ (4122), B+ (521) and Lambda_b0 (5122). D+ (411) can replace D0 through `--charm-trigger 411`. The matching presentation configuration is `config/plot-dplus.json`.

A paper trigger is a final hadron of one of the registered signed trigger identities, with finite nonnegative pT and |eta| <= 4. The default selection includes all production origins. The query retains selected-hard ancestry and the direct-state predicate for a separate control selection. Both modes retain trigger denominators even when no associate qualifies.

The complete fine-species query retains every catalogued final heavy hadron independently in its kinematic sparse, including excited, hidden-heavy, multiply-heavy and mixed charm–beauty states. It retains pairs between registered triggers and every final heavy associate within |eta| <= 4, excluding self-pairs. It does not extend the trigger set. Exact support retains nonfinal event-record history separately; those copies do not add to final-particle yields. Associate origins include selected-hard associates, showers, multiple parton interactions, other resolved origins and unresolved origins when the heavy-flavour sign applies.

The selected-hard associate category describes the associate's own origin; it does not assert a shared root with the trigger. The version 2.5 diagnostic receipt labels pair-origin counts by the selected trigger population. Its closure rows retain the separate historical analyzed-closure population and do not measure closure for every all-origin trigger. Matched and rejected root indices remain event-local exact-support fields.

The published pair observables select configured signed family members with direct-hadronization status codes 81–89 from the broader retained domain. This includes Sigma_b0 (5212), Xi_b'- (5312), Xi_b'0 (5322) and their antiparticles. These are PYTHIA species identities; inclusion does not assert experimental observation. A catalog label does not establish that a species occurred. The fine inventory reports observed, final, direct-selection and pair counts by signed identity, tune and original block.

The query and independent exact-row reader check filled weighted content, including sparse flow bins.

Define q_c = n_c - n_anticharm and q_b = n_b - n_antibeauty. Opposite-sign pairs have a negative product of the relevant heavy-flavour signs. Same-sign pairs have a positive product. Neutral particles participate through heavy valence, not electric charge.

The generic query retains zero-net-flavour associates with sign 0 and inapplicable origin. They contribute to neither OS nor SS. A multiply-heavy hadron is one associate, not a constituent-weighted pair count.

For example, B+ (521) contains an antibeauty quark. Positive-PDG Lambda_b0 (5122) contains a beauty quark. These form an opposite-heavy-flavour-sign channel. A plot label must not replace the signed registry identity.

## Pair selection

The default `inclusive` profile imposes no fixed final-hadron pT floor. Particle pT must be finite and nonnegative. Both particles must have |eta| <= 4. There is no event-wise comparison between trigger and associate pT.

An optional rectangular profile specifies two finite, nonnegative minima. The trigger minimum must be greater than or equal to the associate minimum. Each cut uses `pT >= minimum`. Each minimum must coincide with a regular query-bin lower edge. High-pT overflow remains included.

The model accepts equal minima. A pair with associate pT above trigger pT can pass. The model refuses a non-null `relative_pt` field. It also refuses strict thresholds and off-edge minima for this sparse projection route.

The azimuthal coordinate is trigger phi minus associate phi. The implementation wraps it into [-pi/2, 3pi/2). The query uses 100 equal bins. The lower endpoint is inclusive and the upper endpoint is exclusive.

## Charged primaries (study definition)

The public table and plot label is **Charged primaries**. In this study that label means final charged particles without charm or beauty constituents, finite kinematics, pT > 0.15 GeV/c and |eta| <= 4. The corresponding unchanged event field is `a15_eta4`; `a15_eta1` uses |eta| <= 1. This is the study's generator-level definition and is not a claim of equivalence to an experimental primary-particle definition.

This threshold belongs to the activity definition. It does not apply to inclusive heavy-particle pairs or signed heavy-hadron spectra. The display label does not change retained values or their technical identities.

The generator disabled all heavy-hadron decays, including strong and electromagnetic decays. The runtime also used `ParticleDecays:limitTau0 = on` and `ParticleDecays:tau0Max = 0.01 mm`. Light strong/electromagnetic resonance daughters and charged leptons can contribute, while heavy-hadron daughters are absent. The predicate is therefore not a stored-event ancestry veto. Plots and tables use the compact label **Charged primaries**; this methods section specifies its full generator-level definition and limitations.

## Saved-state associate families

The grouped observable sums additive OS and SS pair primitives for saved generator states at their saved kinematics. It then recomputes the pooled center, every K=10 delete-one value, covariance, validity mask and grouped meson reference. The estimator carries each trigger denominator once. Ratios, normalized spectra and errors are never added after estimation.

The default map has 82 signed members. Particle and antiparticle groups remain separate, as do Sigma and Lambda families. Xi-prime and Xi-star saved states contribute to their signed Xi-family destinations while remaining separate in fine storage. A separately pinned downstream recipe reuses the fine THnSparse. That recipe defines a distinct interpretation. The individual-state recipe instead preserves every eligible species as its own destination.

Membership follows the configured PYTHIA 8.317 decay endpoints; unit endpoint probability in that configuration is not a measured physical branching fraction. States outside a recipe remain in the fine collection and do not enter that grouped observable. Version 2.4 products retain their original trigger-selection identity. They do not represent all-origin results.

The activity axis stores integers from 0 through 4095. Each integer occupies one regular bin. Values outside the supported domain fail the scientific contract rather than silently extending the axis.

## Multiplicity classes

The default percentile intervals are 0–1%, 1–10%, 10–20%, through 90–100%. A separate integrated class covers 0–100%. Each tune resolves its own integer boundaries from its weighted activity distribution.

For percentile p, the threshold is the first ascending integer whose cumulative weight reaches (100-p)/100 of the total. A threshold integer belongs to the lower-activity class. The higher-activity class starts at the next integer.

For [p_low, p_high], the integer lower bound is threshold(p_high)+1, except that p_high = 100 gives zero. The upper bound is threshold(p_low), except that p_low = 0 gives 4095. Discrete ties can produce unequal event fractions or empty classes.

Every aggregate activity bin must be nonnegative and the total must be positive. The implementation can retain signed event weights under these constraints. Reduction recalculates boundaries after each source-block deletion. A changed or statistically unresolved boundary withholds affected class uncertainty without deleting a valid pooled center.

## Observables

### Identified balancing species

The default grouping request has 10 charm and 11 beauty signed associate destinations for each heavy-flavour sign. Integrated and activity-dependent balancing use the same destinations. The [pinned default recipe](../config/associate-family-runtime-all-heavy.json) specifies membership. Fine storage retains its 82 signed members and every other catalogued species separately.

| Sector | Mesons | Baryons |
| --- | --- | --- |
| Charm | D0, D+, Ds+ | Lambda_c+, Sigma_c++, Sigma_c+, Sigma_c0, Xi_c+, Xi_c0, Omega_c0 |
| Beauty | B+, B0, Bs0, Bc+ | Lambda_b0, Sigma_b+, Sigma_b0, Sigma_b-, Xi_b0, Xi_b-, Omega_b- |

The table names particle families. The trigger's heavy-flavour sign determines the opposite-sign particle or antiparticle. The estimator subtracts its same-sign conjugate.

Each charge state remains a separate category. Saved excited states join only their configured signed destination; Xi-prime and Xi-star join the corresponding Xi charge state in the default recipe. Their fine signed identities remain separate. Distinct Sigma or Xi charges are not summed together. The numerical ROOT retains their joint jackknife covariance.

Figures show mesons before baryons. Baryon groups follow the order Lambda, Sigma, Xi, then Omega. Each family follows a fixed destination order. Short ticks delimit species bins, and labels sit at bin centers.

Ds and Xi add strange meson and baryon comparisons. Sigma adds direct heavy-baryon production beyond Lambda. Heavy-hadron decays remain disabled, so Sigma particles do not feed down into the saved Lambda category.

Each numerical ROOT file records its own selected species. The renderer retains that selection. A new [reduction](workflow.md#numerical-reduction) can select these categories from the existing merged query without rebuilding it.

### Definitions

Let w_e denote event weight. Let T_t denote the weighted number of eligible triggers of species t in the selected class. Let N_OS and N_SS denote weighted ordered-pair counts with the requested associates. A trigger contributes to T_t even when both pair counts are zero.

For azimuthal bin b, let delta_b denote its width in radians. The identified pair observables are bin-averaged densities:

$$C_{OS,b}=\frac{N_{OS,b}}{T_t\,\delta_b},\qquad C_{SS,b}=\frac{N_{SS,b}}{T_t\,\delta_b}.$$

The sign-summed correlation difference is

$$C_{net,b}=\frac{N^{all}_{OS,b}-N^{all}_{SS,b}}{T_t\,\delta_b}.$$

Here, “all” means all selected registered associates in the selected heavy-flavour sector. It does not mean all generated particles. The default lower correlation panel uses this sign-summed difference. It is not a ratio of OS minus SS to OS plus SS.

Each density uses its own stored bin width. The estimator applies this division to the pooled result and every deletion. Joint covariance therefore includes the width factors on both axes. A sum of densities times their bin widths gives the integrated yield for the same associate domain.

The numerical quantity `dphi_density_per_trigger` has units `per_trigger_per_radian`. Formula contract `projection_formulas_v4` identifies this convention and the complete selected-state pair domain. Archives with `projection_formulas_v3` retain their narrower pair selection. The reader retains the earlier `dphi_per_trigger` quantity with units `per_trigger_per_bin`. The renderer labels each convention from the numerical archive and rejects mixed conventions within a panel.

The integrated balancing yield for an opposite-sign species a is

$$B_{t,a}=\frac{N(t,a)-N(t,\bar a)}{T_t}.$$

The partner bar denotes the conjugate signed PDG identity. There is no half-weight on the same-sign term. Integration covers the complete supported azimuthal interval. Activity-dependent balancing applies the same formula within each tune-local class.

The baryon-to-meson observable divides two balancing yields with the same trigger. The canonical Lambda tuples `(trigger, baryon, reference)` are `(421, -4122, -421)` and `(521, 5122, -521)`. The D+ selection changes the first tuple to `(411, -4122, -411)`.

The numerical request includes each selected Sigma and grouped Xi charge state. Primed Xi members contribute through their assigned destination in a grouped interpretation. The individual-state interpretation keeps primed and starred partners separate.

All charm baryons use the same D0 reference. All beauty baryons use the same charged B reference. This common denominator supports comparisons between baryon species. It does not isolate a strangeness mechanism.

Additional figures compare meson and Lambda triggers in separate columns for each baryon species. The signed registry sets the numerator and reference identities. For example, the Xi_b0 tuples are `(521, 5232, -521)` and `(5122, -5232, 521)`. The latter contains an antibaryon numerator because the Lambda_b trigger contains a beauty quark.

Each ratio cancels its common trigger denominator algebraically. The estimator still requires that denominator to exist. Joint deletion factors preserve the numerator-reference covariance and the covariance between ratios.

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

The fixed raw compatibility contract contains selection and statistical labels that do not configure downstream reduction. Use `config/analysis-all-origin.json` and the numerical request for current construction and default grouped results; historical analysis versions retain their own checksum identities. A change to checksum-bound raw metadata does not change the scientific meaning of existing data.
