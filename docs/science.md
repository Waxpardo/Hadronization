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

The selected-state registry in [study.json](../config/study.json) contains signed PDG identities, heavy valence, electric charge and structural eligibility. The generated [C++ contract](../pipeline/generate/study_contract.hpp) binds those exact bytes. Version 2.2 products use [analysis.json](../config/analysis.json); the current complete fine-species construction uses [analysis-all-origin.json](../config/analysis-all-origin.json) and its independently pinned [heavy catalog](../config/heavy-catalog.json).

The default displayed triggers are D0 (421), Lambda_c+ (4122), B+ (521) and Lambda_b0 (5122). D+ (411) can replace D0 through `--charm-trigger 411`. The matching presentation configuration is `config/plot-dplus.json`.

A paper trigger is a final hadron of one of the registered signed trigger identities, with finite nonnegative pT and |eta| <= 4. The default selection includes all production origins. The query retains selected-hard ancestry and the direct-state predicate for a separate control selection. Both modes retain trigger denominators even when no associate qualifies.

The complete fine-species query retains every catalogued final heavy hadron independently in its kinematic sparse, including excited, hidden-heavy, multiply-heavy and mixed charm–beauty states. It retains pairs between registered triggers and every final heavy associate within |eta| <= 4, excluding self-pairs. It does not extend the trigger set. Exact support retains nonfinal event-record history separately; those copies do not add to final-particle yields. Associate origins include selected-hard associates, showers, multiple parton interactions, other resolved origins and unresolved origins when the heavy-flavour sign applies.

The selected-hard associate category describes the associate's own origin; it does not assert a shared root with the trigger. The version 2.5 diagnostic receipt labels pair-origin counts by the selected trigger population. Its closure rows retain the separate analyzed-closure population and do not measure closure for every all-origin trigger. Matched and rejected root indices remain event-local exact-support fields.

The published pair observables select 202 signed open-heavy states with direct-hadronization status codes 81–89. Each state remains a separate identity. The broader 219-state catalog also retains hidden-heavy states, which have no OS or SS heavy-flavour sign. These are PYTHIA species identities; inclusion does not assert experimental observation. A catalog label does not establish that a species occurred. The fine inventory reports observed, final, direct-selection and pair counts by signed identity, tune and original block.

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

The public table and plot label is **Charged primaries**. In this study that label means final charged particles without charm or beauty constituents, finite kinematics, pT > 0.15 GeV/c and |eta| <= 4. The corresponding event field is `a15_eta4`; `a15_eta1` uses |eta| <= 1. This is the study's generator-level definition and is not a claim of equivalence to an experimental primary-particle definition.

This threshold belongs to the activity definition. It does not apply to inclusive heavy-particle pairs or signed heavy-hadron spectra. The display label does not change retained values or their technical identities.

The generator disabled all heavy-hadron decays, including strong and electromagnetic decays. The runtime also used `ParticleDecays:limitTau0 = on` and `ParticleDecays:tau0Max = 0.01 mm`. Light strong/electromagnetic resonance daughters and charged leptons can contribute, while heavy-hadron daughters are absent. The predicate is therefore not a stored-event ancestry veto. Plots and tables use the compact label **Charged primaries**; this methods section specifies its full generator-level definition and limitations.

## Associate-state interpretations

The published identity recipe maps each of 202 signed open-heavy states to itself. Each state keeps its own OS and SS primitives. The estimator recomputes the pooled center, every K=10 delete-one value, covariance, validity mask and meson reference. It carries each trigger denominator once. Ratios, normalized spectra and errors are never added after estimation.

A separate supported recipe groups 82 signed saved states into 42 signed family destinations. It sums block-level OS and SS primitives before normalization, then recomputes all estimates and covariance. It does not describe the published result.

Grouped membership follows configured PYTHIA 8.317 decay endpoints. Unit endpoint probability in that configuration is not a measured physical branching fraction. States outside a recipe remain in the fine collection. Version 2.2 remains compatible with its matching versioned products and input contract.

The activity axis stores integers from 0 through 4095. Each integer occupies one regular bin. Values outside the supported domain fail the scientific contract rather than silently extending the axis.

## Multiplicity classes

The default percentile intervals are 0–1%, 1–10%, 10–20%, through 90–100%. A separate integrated class covers 0–100%. Each tune resolves its own integer boundaries from its weighted activity distribution.

For percentile p, the threshold is the first ascending integer whose cumulative weight reaches (100-p)/100 of the total. A threshold integer belongs to the lower-activity class. The higher-activity class starts at the next integer.

For [p_low, p_high], the integer lower bound is threshold(p_high)+1, except that p_high = 100 gives zero. The upper bound is threshold(p_low), except that p_low = 0 gives 4095. Discrete ties can produce unequal event fractions or empty classes.

Every aggregate activity bin must be nonnegative and the total must be positive. The implementation can retain signed event weights under these constraints. Reduction recalculates boundaries after each source-block deletion. A changed or statistically unresolved boundary withholds affected class uncertainty without deleting a valid pooled center.

## Observables

### Identified balancing species

The numerical request contains 84 signed charm states and 118 signed beauty states. The trigger's heavy-flavour sign selects the opposite-sign identity and its same-sign conjugate. Each charge and excitation remains separate.

Each hadron contributes one count, including multiply-heavy states. These species yields are not weighted heavy-quark-charge closure sums. The sector rule assigns states with net beauty to beauty, including Bc. Charm observables exclude states with beauty constituents.

The paired overview selects seven charm and eight beauty ground-state identities per trigger. These comprise ground-state mesons, Lambda and Sigma states. Separate single-trigger figures select 28 charm and 43 beauty ground, star and prime identities. The display omits higher orbital and mass-labelled states, but the numerical ROOT retains them.

Figures show mesons before baryons. Each displayed ground state precedes its star and prime partners of the same charge. Short ticks delimit species bins, and labels sit at bin centers.

Ds and Xi add strange meson and baryon comparisons. Sigma adds direct heavy-baryon production beyond Lambda. Heavy-hadron decays remain disabled, so Sigma particles do not feed down into the saved Lambda category.

Each numerical ROOT file records its selected interpretation. The renderer checks the recipe hash before it labels individual states. A new [reduction](workflow.md#numerical-reduction) can select another compatible recipe from the existing merged query.

### Definitions

Let w_e denote event weight. Let T_t denote the weighted number of eligible triggers of species t in the selected class. Let N_OS and N_SS denote weighted ordered-pair counts with the requested associates. A trigger contributes to T_t even when both pair counts are zero.

For azimuthal bin b, let delta_b denote its width in radians. The identified pair observables are bin-averaged densities:

$$C_{OS,b}=\frac{N_{OS,b}}{T_t\,\delta_b},\qquad C_{SS,b}=\frac{N_{SS,b}}{T_t\,\delta_b}.$$

The identified correlation difference is

$$C_{net,b}=\frac{N_{OS,b}-N_{SS,b}}{T_t\,\delta_b}=C_{OS,b}-C_{SS,b}.$$

Each lower correlation panel subtracts the two identified-pair densities directly above it. The trigger, associate species, selections, angular bins and trigger denominator stay the same. The default columns use D0, Lambda_c, B+ and Lambda_b triggers with their conjugate associates. The same-sign curve uses the corresponding unconjugated associate.

The default figures multiply Lambda_c correlation values and errors by 10, and Lambda_b values and errors by 5, for visibility. Each affected panel labels this display factor. OS, SS and their difference share the same factor. Numerical ROOT values and exports retain the physical densities.

Each density uses its own stored bin width. The estimator applies this division to the pooled result and every deletion. Joint covariance therefore includes the width factors on both axes. A sum of densities times their bin widths gives the integrated yield for the same associate domain.

The numerical quantity `dphi_density_per_trigger` has units `per_trigger_per_radian`. Formula contract `projection_formulas_v4` identifies this convention and the complete selected-state pair domain. Archives with `projection_formulas_v3` retain their narrower pair selection. The reader retains the earlier `dphi_per_trigger` quantity with units `per_trigger_per_bin`. The renderer labels each convention from the numerical archive and rejects mixed conventions within a panel.

The integrated balancing yield for an opposite-sign species a is

$$B_{t,a}=\frac{N(t,a)-N(t,\bar a)}{T_t}.$$

The partner bar denotes the conjugate signed PDG identity. There is no half-weight on the same-sign term. Integration covers the complete supported azimuthal interval. Activity-dependent balancing applies the same formula within each tune-local class.

The baryon-to-meson observable divides two balancing yields with the same trigger. The canonical Lambda tuples `(trigger, baryon, reference)` are `(421, -4122, -421)` and `(521, 5122, -521)`. The D+ selection changes the first tuple to `(411, -4122, -411)`.

The published request keeps Sigma, Xi, primed Xi and starred Xi identities separate. A grouped alternative can combine configured saved states only through a distinct recipe and reduction.

Selected charm baryon-to-meson ratios use the same D0 reference. Selected beauty baryon-to-meson ratios use the same charged B reference. This common denominator supports comparisons between baryon species. It does not isolate a strangeness mechanism.

Additional figures compare meson and Lambda triggers in separate columns for each selected baryon species. The signed registry sets the numerator and reference identities. For example, the Xi_b0 tuples are `(521, 5232, -521)` and `(5122, -5232, 521)`. The latter contains an antibaryon numerator because the Lambda_b trigger contains a beauty quark.

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

## Comparison between trigger species

The supplementary trigger comparison divides the baryon-trigger balancing yield by the meson-trigger yield, within each tune:

$$R_a=\frac{(N_{\mathrm{OS}}-N_{\mathrm{SS}})_{B,a}/T_B}{(N_{\mathrm{OS}}-N_{\mathrm{SS}})_{M,a'}/T_M}.$$

Here $B$ and $M$ denote the baryon and meson trigger samples. The charm panel compares $\Lambda_c^+$ with $D^0$ for the same signed associate, so $a'=a$. The beauty panel compares $\Lambda_b^0$ with $B^+$. These triggers contain opposite heavy-flavour signs, so the beauty panel compares the charge-conjugate associates used in the integrated figures. Its upper species label belongs to the numerator; its lower label belongs to the denominator.

A value above one means a larger balancing yield per baryon trigger for the indicated associate. A raw net-count ratio also contains the trigger-population ratio and therefore answers a different question. Neither comparison isolates a causal fragmentation mechanism.

The center uses pooled counts. Each uncertainty deletes the same original block from both trigger samples and recomputes the complete ratio. The numerical companion retains all deletion values and the joint covariance across associates. Independent tune families contribute separate covariance blocks. A zero or unresolved surviving denominator withholds the affected result or uncertainty. Negative valid centers remain signed.

The shipped recipe selects inclusive pair pT and the integrated multiplicity class. The command currently requires ten original blocks with unit event weights. Its ROOT companion binds the parent numerical archive, signed recipe and native statistics source. The figure renderer verifies these bindings before drawing the stored values.

## Definition authority

[physics.hpp](../pipeline/generate/physics.hpp) implements raw particle and ancestry rules. [model.py](../pipeline/query/model.py) validates downstream selections and the signed registry. [native_engine.cpp](../pipeline/reduce/native_engine.cpp) and [statistics.hpp](../pipeline/reduce/statistics.hpp) evaluate observables and covariance.

The numerical archive records the resolved model, source identities, class boundaries and estimator policy. The renderer consumes that archive. Presentation configuration controls layout, display selection and labelled scale factors. It does not change the estimator or its stored statistical uncertainty.

The fixed raw compatibility contract contains selection and statistical labels that do not configure downstream reduction. Use `config/analysis-all-origin.json` for current query construction. Use `config/analysis-individual-species.json` for the published numerical interpretation. Each analysis version has its own checksum identity. A change to checksum-bound raw metadata does not change the scientific meaning of existing data.
