# Design and rationale

This is the authoritative explanation of **what this repository does, why every
choice was made, and what evidence backs it**. It is written so that someone
with no prior contact with the project can rebuild the study independently and
check our conclusions.

`REPRODUCIBILITY.md` tells you which commands to run. This document tells you
why those are the right commands. Where the two disagree, this document states
the intent and `REPRODUCIBILITY.md` states the mechanics; fix whichever is
stale.

**Rule for maintainers:** no design choice may exist only in code. If you change
a physics definition, a threshold, a schema, or a selection, you change the
corresponding row of Section 3 in the same commit, and you cite the test or
measurement that justifies it.

---

## 1. The physics question

Charm and beauty are produced almost exclusively in pairs, in a hard partonic
scattering that is calculable in perturbative QCD. The quantum numbers are
therefore fixed *before* hadronisation. What is not calculable is which hadrons
those quarks end up in, and where those hadrons go in phase space. That is a
non-perturbative question, and different hadronisation models answer it
differently.

The observable exploits this. Select a heavy-flavour hadron whose heavy quark
can be traced back to the selected hard scattering. Then ask: **which hadron
carries the compensating anti-flavour, and where is it?**

Concretely we measure, per trigger, the difference between opposite-sign and
same-sign correlations in relative azimuth:

```
Y = Integral dDeltaPhi [ (1/N_trig) dN_OS/dDeltaPhi  -  (1/N_trig) dN_SS/dDeltaPhi ]
```

The subtraction removes combinatorial background from additional heavy-flavour
production, leaving the part correlated with the trigger's own flavour.

The discriminating question is **whether the balancing partner of a heavy-flavour
baryon is itself a baryon or a meson**, because junction topologies and
conventional diquark fragmentation predict different answers.

### What this observable is not

- It is **not** an experimental, decay-inclusive yield. It is a model-level
  primary-hadron observable.
- It is **not** a measurement of electric-charge or baryon-number compensation.
  Those are balanced predominantly by *light* hadrons. See Section 3.9.
- The multiplicity classes are **not** comparable to experimental multiplicity
  classes. See Section 3.5.

---

## 2. Sign conventions, stated once

Heavy flavour is signed by **quark content**, not by electric charge and not by
particle/antiparticle naming:

```
q_c = n_c - n_cbar        q_b = n_b - n_bbar
```

This matters and is easy to get wrong. `B+` (`521`, u b-bar) has `q_b = -1`.
`Lambda_b0` (`5122`, udb) has `q_b = +1`. They are therefore an *opposite-sign*
pair, which is why the registry maps `5122 -> 521` as its reference meson. The
same holds for `D+` (`411`, `q_c = +1`) and `Lambda_c+` (`4122`, `q_c = +1`),
whose opposite-sign partner is `D-`.

Defining OS/SS on quark content rather than electric charge is what makes the
observable a *flavour* balance function. Do not "simplify" this.

---

## 3. Design decisions

Each row: the choice, why it is physically motivated, and the evidence.

### 3.1 Collision energy: 13.6 TeV

**Choice.** `Beams:eCM = 13600` in all three tune cards.

**Why.** This is LHC Run 3. The previous value, 14 TeV, is the design energy at
which no measurement exists, which made any comparison to data impossible and
used the CLOSEPACKING tune away from the 13 TeV data it was tuned against.

**Evidence.** `config/tune_difference_allowlist_v1.json` pins the required
value and `tools/validate_tune_cards.py` fails the build if a card disagrees.
Changing the card alone is rejected.

### 3.2 One combined producer, both heavy flavours in one run

**Choice.** `HardQCD:hardccbar = on` and `HardQCD:hardbbbar = on` in a single
producer, one raw dataset per tune.

**Why.** Charm and beauty triggers must see the *same* underlying event
population, otherwise a charm-vs-beauty comparison confounds hadronisation
differences with sample differences. A single selected hard event ordinarily
belongs to one channel or the other; the mixed sample simply contains both
populations.

**Evidence.** The producer verifies that the PYTHIA process code and the
reconstructed hard pair agree (`121/122 -> charm`, `123/124 -> beauty`) and
aborts the job on any disagreement, rather than trusting the code mapping.

### 3.3 Trigger requires hard origin; associate does not

**Choice.** The trigger's heavy quark must be ancestry-matched to the selected
hard-subprocess quark. The associate may have any origin: hard, shower, MPI,
other, or unresolved.

**Why.** This asymmetry is deliberate and is the single most important
selection in the analysis. Same-sign associates arise from *additional* heavy
flavour in the event. Requiring both particles to match the one selected hard
pair would remove the same-sign term by construction and destroy the
subtraction.

**Evidence.** `SimulationScripts/HeavyFlavourUtils.h:MatchHeavyOriginGraph`.
The traversal refuses to tie-break: ambiguous lineages return `kAmbiguous` and
are counted as unresolved rather than assigned. `Validation/AuditOriginResolution.C`
and `Validation/ListUnresolvedOrigins.C` report unresolved rates per tune,
because unresolved fractions are tune-dependent and a permissive tie-break
would bias exactly the comparison being made.

### 3.4 One hard quark enters at most one final hadron

**Choice.** If several final hadrons independently claim the same selected hard
quark, **all** of them are demoted to unresolved.

**Why.** PYTHIA can assign one fragmenting string or junction mother range to
several final hadrons. Independent ancestry walks then each look unique while
claiming the same physical quark. That is not distinguishable from the event
record, so choosing one arbitrarily would invent information.

**Evidence.** `EnforceUniqueFinalHardCarrier` and
`RejectFinalMultiHeavyCarrier`; `Validation/TestHardCarrierUniqueness.C`. The
raw validator independently requires that no duplicate survives.

### 3.5 Event activity: `NCH_PRIMARY_CHARGED_ETA10_V1`

**Choice.** Final, charged, non-heavy-flavour particles, `pT > 0.15 GeV/c`,
`|eta| < 1`. A second counter at `|eta| < 4` is stored as a cross-check.

**Why.** The previous definition counted only particles carrying PYTHIA
hadronisation status 81--89, discarding every pion from rho, K*, Delta or omega
decay. It was not a charged-particle multiplicity, and the paper could not
honestly connect it to measured multiplicity dependence.

Charge and heavy content come from PYTHIA `ParticleData`, never from
hand-written PDG digit arithmetic, so species the conventional primary
definition includes (`Sigma+-`, `Xi-`, `Omega-`) are counted rather than
silently dropped. Heavy-flavour hadrons are excluded because their decays are
disabled here, so they are final only as an artefact of the production policy,
and an experiment would count their decay daughters instead; excluding them
also removes the autocorrelation that would otherwise exist between the
event-activity classifier and the observable it classifies.

**Evidence.** `Validation/CalibrateMultiplicityAgainstMinBias.C`, run
permanently as part of Gate A and fail-closed. Measured at 13.6 TeV, INEL>0:

| configuration | dN_ch/deta, \|eta\|<0.5, pT->0 |
|---|---|
| minimum bias, experimental decay convention | **7.007** |
| minimum bias, exact production decay policy | 6.914 |
| HardQCD ccbar+bbbar, pTHatMin = 1 GeV | 4.558 |

The published reference is ALICE, Phys. Lett. B 753 (2016) 319: 6.94 +- 0.10 at
13 TeV, INEL>0. The counter reproduces it to better than 1%.

**Two consequences that must be stated in the paper.** The production decay
policy costs 1.3%, because the experimental primary definition counts
charm/beauty decay daughters (open-heavy hadrons have `c*tau0 < 1 cm`) and we
disable those decays. And the hard-heavy sample sits ~36% *below* minimum bias
at identical counter settings — see Section 6.

### 3.6 Decay policy: heavy stable, light per the 1 cm/c convention

**Choice.** Every hadron containing charm or beauty has `mayDecay = false` set
programmatically after reading the card. Light hadrons follow
`ParticleDecays:limitTau0 = on`, `tau0Max = 0.01 mm`.

**Why.** The observable is about hadrons made *directly* in hadronisation, so
the heavy states must survive to be counted. For light flavour, the card value
is exactly equivalent to the conventional experimental primary definition
(`c*tau0 > 1 cm`), because **no light hadron has `0.01 mm < c*tau0 < 10 mm`**.
That equivalence is what lets the paper quote the standard 1 cm/c definition.
Consequently `isFinal()` already means "primary" for light hadrons, and no
ancestry traversal is needed to exclude weak-decay products.

**Evidence.** `Validation/TestPrimaryChargedDefinition.C` enumerates the entire
installed `ParticleData` table and asserts the empty-window claim, rather than
trusting documentation. It also recounts both multiplicity windows from live
events, proving the stored pilot record is complete. Initialization fails if
any recognized heavy hadron remains decay-enabled, checked both before and
after `pythia.init()`.

### 3.7 Role-dependent acceptance

**Choice.** Trigger `pT > 1 GeV/c`; associate `pT > 0.15 GeV/c`; both
`|eta| <= 4`.

**Why.** The trigger threshold selects a well-defined, reasonably hard object
whose ancestry is meaningful. The associate threshold is kept low because the
compensating hadron is often soft and cutting it away would bias the balance
integral toward zero.

**Caveat.** `|eta| <= 4` is far wider than any single experiment and is a
model-level choice. It must be stated, not buried.

### 3.8 Statistics: ten disjoint blocks

**Choice.** Ten equal, disjoint, shuffled blocks. Uncertainties are the
standard error across block estimates. Ratios are formed **within** each block
before averaging.

**Why.** Forming ratios within blocks is what makes the numerator/denominator
correlation cancel correctly; taking a ratio of averages would misstate the
uncertainty on a nonlinear quantity.

**Known limitation.** Ten blocks gives roughly 24% uncertainty *on the
uncertainty* (chi-square with 9 degrees of freedom). If a conclusion depends on
an error bar rather than a central value, increase the block count.

### 3.9 Auxiliary light-hadron compensation grid (raw-v7)

**Choice.** Per event, net electric charge (in units of e/3) and net baryon
number of final light primaries, accumulated on a fixed 16 phi x 8 eta grid
over `|eta| <= 4`.

**Why.** Electric charge and baryon number are conserved too, but their
balancing partners are overwhelmingly *light* hadrons, which the heavy-hadron
collection does not store. The grid is trigger-agnostic: any Delta-phi or
Delta-eta profile relative to any trigger is recovered by rotating and shifting
cell indices at analysis time, so no future trigger definition is foreclosed.
Storing it now is cheap; regenerating 3e8 events later is not.

**Cost, measured not estimated.** 57 bytes/event compressed, i.e. 17.1 GB at
3e8 events, which is 6.4% of the 892 bytes/event raw total.

**Status: auxiliary.** This is not part of the central selector. It must not be
presented as a charge or baryon-number balance function without a dedicated
analysis and its own validation.

### 3.10 Tunes are configuration bundles, not single switches

**Choice.** MONASH, JUNCTIONS and CLOSEPACKING are compared as complete
bundles, and an allowlist declares exactly which settings may differ.

**Why.** MONASH and JUNCTIONS differ in 13 settings; MONASH and CLOSEPACKING in
about 20, including `StringZ:aLund` (0.36 vs 0.68), `bLund` (0.56 vs 0.98) and
`MultipartonInteractions:pT0Ref`. **No observed difference may be attributed to
junctions, close packing, or diquark production alone.** Use "difference
between the full configurations", followed by physically cautious
interpretation.

**Evidence.** `tools/validate_tune_cards.py` emits the machine-generated
difference table and fails on any setting differing outside the allowlist, and
on unknown or misspelled settings.

---

## 4. Rebuilding the study from scratch

```bash
source ./setupEnv.sh                 # pins ROOT 6.30/01 and PYTHIA 8.315 from CVMFS
make -C SimulationScripts            # build the producer
./run_publication_gate_a.sh <outdir> # static, unit and calibration validation
```

Gate A includes the N_ch calibration (Section 3.5) and the primary-charged
definition proof (Section 3.6), so a broken classifier blocks the gate.

The gates are ordered and each is fail-closed: A static/unit, B deterministic
tune pilots, C failure and workflow validation, D end-to-end analysis smoke
test, E full campaign. Do not skip forward; evidence from an earlier commit
cannot be cited as a pass for a later one.

---

## 5. Contract versions

| Contract | Version |
|---|---|
| raw schema | `hf_primary_ground_raw_v7` |
| central selector | `hard_trigger_primary_ground__primary_ground_associate_v1` |
| origin algorithm | `signed_heavy_constituent_complete_mothers_unique_v4` |
| multiplicity definition | `primary_charged_light_hadron_level_v1` |
| central multiplicity | `NCH_PRIMARY_CHARGED_ETA10_V1` |
| cross-check multiplicity | `NCH_PRIMARY_CHARGED_ETA40_V1` |
| light compensation grid | `light_compensation_grid_v1` |
| heavy-stability audit | `heavy_stability_audit_v2` |
| effective settings | `effective_pythia_settings_exhaustive_v2` |
| tune allowlist | `pythia_tune_difference_allowlist_v2` |
| pair analysis schema | `paul_pair_objects_primary_ground_v2` |

Any change to a physics definition bumps the raw schema. Older raw files then
become historical evidence and cannot satisfy a gate.

---

## 6. Known limitations, stated deliberately

These must remain visible in the paper. Do not quietly resolve them.

1. **The hard sample has lower multiplicity than minimum bias.** Measured
   ~36% lower at identical counter settings (Section 3.5). Requiring a hard
   process normally *raises* activity, so this is not yet understood.
   `PhaseSpace:pTHatMin = 1` sits below `MultipartonInteractions:pT0Ref = 2.15`,
   i.e. inside the regulated low-pT regime. **The percentile classes must not
   be used in a published figure, and must not be described as comparable to
   experimental multiplicity classes, until the pTHat sensitivity study
   (0.5 / 1.0 / 2.0 GeV) explains it.**

2. **`pTHatMin` sensitivity is unmeasured.** It is a generator-level cut that
   defines the sample. It must be reported, and the pilots must be run.

3. **Ground-state restriction and closure.** With decays disabled, excited
   states (D*, Sigma_c, Sigma_b, Xi_c) never feed down, so a ground-state-only
   balance integral does **not** satisfy the sum rule. The agreed direction is
   to define the balance on the complete open heavy flavour, with the
   ground-state set as a labelled subset, since the producer already verifies
   `sum q_c = sum q_b = 0` event by event. Until that lands, any ground-state
   integral must be labelled as a subset, not as closure.

4. **Six species are review-blocked.** `+-5212`, `+-5312`, `+-5322` are kept as
   operational PYTHIA entries but excluded from central results: PDG 2025
   assigns no MCID to 5312/5322 and treats Sigma_b0 as an unmeasured model
   prediction.

5. **Ten blocks means a noisy error bar** (Section 3.8).

6. **`|eta| <= 4` acceptance** is model-level and not experimentally
   accessible (Section 3.7).
