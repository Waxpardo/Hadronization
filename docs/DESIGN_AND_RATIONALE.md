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

This document owns *why*. For which document owns which area -- the physics
contract, cluster operations, machine setup, a subsystem's own mechanics --
see the ownership table in the top-level `README.md`. Sections 3.12 and 3.13
exist because that rule failed: a threshold change and a validator contract
were both live in code with no design entry at all.

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

**Why — corrected 2026-08-08. The original justification was overstated.** It
read: "Charm and beauty triggers must see the *same* underlying event
population, otherwise a charm-vs-beauty comparison confounds hadronisation
differences with sample differences." **That is not what the combined run
buys.**

**The two populations are disjoint by construction.** Every selected event is
charm-hard *or* beauty-hard — `121/122` against `123/124`, mutually exclusive,
and the producer aborts if the process code and the reconstructed hard pair
disagree. Interleaving them in one run does not give charm and beauty triggers a
shared underlying event; it gives them **adjacent entries in one file**. **The
marginal distributions would be identical if the two channels were generated in
separate runs from the same card with the same seeds** — nothing about the
mixture is a shared-population property.

**The real benefits are operational, and they are real:**

- one campaign, one seed ledger, one canonical manifest, one effective-settings
  audit, one provenance chain — rather than two of each to keep in step;
- a **naturally pooled N_ch composition**: the activity axis is built from the
  combined sample, so charm-hard and beauty-hard events are classified on one
  set of percentile boundaries without an extra reconciliation step.

**The mixture allocates statistics by cross-section, and it is not free.**
Measured over `process_counts`, 10 jobs per tune (1,000,000 events each),
`TChain` + weighted `Draw`, 2026-08-08:

| tune | charm | beauty | cc̄ : bb̄ | beauty fraction |
|---|---|---|---|---|
| MONASH | 864,887 | 135,113 | 6.401 : 1 | 13.51 % |
| JUNCTIONS | 864,539 | 135,461 | 6.382 : 1 | 13.55 % |
| CLOSEPACKING | 864,632 | 135,368 | 6.387 : 1 | 13.54 % |

**Tune-independent, as it must be** — the hard cross-sections do not depend on
hadronisation parameters. **So ~86.5 % of the CPU produces charm events and
13.5 % produces beauty**, and the beauty observables are correspondingly the
statistics-limited ones.

**No observable in the analysis depends on the mixture ratio.** Every yield,
fraction and correlation is normalised within its own trigger species, and the
per-sector closure sum rules are per-trigger. The ratio sets **how much
statistics each sector receives**, not what any number means.

**This makes the combined-vs-split question a resource decision, not a physics
one** — see `docs/PRODUCTION_SHAPE_DECISION.md`, which is open.

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

**Evidence.** `generation/producer/HeavyFlavourUtils.h:MatchHeavyOriginGraph`.
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
`|eta| <= 1`. A second counter at `|eta| <= 4` is stored as a cross-check.

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

**Evidence.** `Validation/CalibrateMultiplicityAgainstMinBias.C`, run by hand
(the Gate-A runner that used to invoke it was deleted with the gate layer; see
Section 4). Measured on PYTHIA 8.315 at 13.6 TeV, INEL>0:

| configuration | dN_ch/deta, \|eta\|<0.5, pT->0 |
|---|---|
| minimum bias, experimental decay convention | **7.007** |
| minimum bias, exact production decay policy | 6.914 |
| HardQCD ccbar+bbbar, pTHatMin = 1 GeV | 4.558 |

The published reference is ALICE, Phys. Lett. B 753 (2016) 319: 6.94 +- 0.10 at
13 TeV, INEL>0. The counter reproduces it to better than 1%.

**These numbers predate two changes and have not been re-measured.** They are
from PYTHIA 8.315, and production is now pinned to 8.317
(`config/dependencies.conf:36`); and the `pTHatMin = 1 GeV` row no longer
describes production, which runs at 2.0. The card comments record 8.317
measurements of dN_ch/deta = 4.973 at pTHatMin 1.0 against 6.968 for minimum
bias (`generation/cards/pythiasettings_Hard_Low_ccbb_MONASH.cmnd:33`). The
minimum-bias rows are threshold-independent and stand.

**One consequence that must be stated in the paper.** The production decay
policy costs ~~1.3%~~, because the experimental primary definition counts
charm/beauty decay daughters (open-heavy hadrons have `c*tau0 < 1 cm`) and we
disable those decays.

> ### ✏ RE-MEASURED 2026-08-17 — it is **0.767 %** on the production generator
>
> **The 1.3 % above is a PYTHIA 8.315 number** — 7.007 under the experimental
> convention against 6.914 under the production policy, i.e. **1.327 %**, from
> `results/validation/generator/NCH_CALIBRATION_20260730.md`. It is **kept visible rather
> than overwritten**, because it is the value every document written before today
> quotes.
>
> **On 8.317, which is what production runs, the bias is 0.767 %:** `dN_ch/deta`
> **7.040** under the experimental convention against **6.986** under the exact
> production policy. 200 000 events per arm, both arms **paired on the macro's
> fixed seed** so the shared event content cancels.
> `results/validation/generator/NCH_DECAY_POLICY_BIAS_8317.md`.
>
> Both arms rose from 8.315 (7.007 → 7.040 and 6.914 → 6.986), but the
> production-policy arm rose four times as much, which is what shrank the gap by
> 42 %.
>
> **The sentence above is the one this section says the paper must state, so the
> number the paper states must be 0.77 %.** `Model.tex` is **not** edited here —
> that is owner-side and belongs on the paper checklist, the same disposition
> `PTHAT_MULTIPLICITY_SCAN_8317.md` reached for the "36 % below minimum bias"
> claim it superseded.
>
> **Why it was re-measured rather than carried forward:** this number is the sole
> input to systematic source S5 (`docs/SYSTEMATICS.md` §2), whose null holds only
> while the bias stays below the margin separating a class boundary from the
> nearest integer. On the 8.315 value that margin was a factor of **1.16**. On the
> re-measured value it is **2.01**.

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

#### Quoting rule for sparse classes — zero-yield blocks are expected

**Recorded 2026-08-09, from the measured per-class projection
(`docs/PRODUCTION_SHAPE_DECISION.md` §4).** In the sparsest quoted cells —
**MONASH `Σ_b^±` in classes 1–5, at 20–37 mean entries per block at 1000 jobs**
— Poisson fluctuation means **some blocks will contain zero entries even at full
production.** That is a property of the statistics, not a failure of the run.

**Three rules follow, and they are not optional:**

1. **A zero-yield block is a valid finite estimate of zero, not a missing
   datum.** It enters the block mean and the SEM like any other block.
   **Discarding empty blocks biases the mean upward** and is the specific error
   this rule exists to prevent.
2. **Ratios in sparse classes use the never-zero meson control as the
   denominator.** The B-meson control carries ≥1467 entries per block in every
   class of every tune, so a within-block ratio is always defined. **Do not form
   a ratio whose denominator can be zero** — that is what the within-block
   convention above would otherwise produce.
3. **Per-class error bars in the marginal classes are shown, never smoothed.**
   MONASH classes 1–5 are marginal by construction; an error bar that looks
   embarrassing there is the honest output.

**Scope.** These apply to per-class quoting. Multiplicity-integrated quantities
are unaffected — which is why **B_c is declared a multiplicity-integrated /
top-class-only observable** by this scope ruling.

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

### 3.11 Canonical job size: 100,000 successes, 1000 jobs per tune

**Choice.** The canonical production job generates 100,000 successes, and each
tune contributes 1000 canonical jobs (candidate slots 1000/2000/2000). Total
exposure per tune is unchanged: 1000 x 100,000 is exactly the 100 x 1,000,000
it replaces.

**Why.** PYTHIA 8.315 contains an unbounded accept-reject loop in
`StringZ::zLund`, reached from `JunctionSplitting::splitJunGluons`, that is
entered only under the junction tunes (`ColourReconnection:mode = 1`,
`allowDoubleJunRem = off`, `BeamRemnants:remnantMode = 1`). A job that enters it
never terminates and never exits, so it is invisible to `on_exit_hold`. The
measured rate is approximately 1.1 hangs per million events in JUNCTIONS and
CLOSEPACKING, and zero in MONASH.

Because job survival is `exp(-N p)`, the job size is now a **statistical and
throughput parameter**, not just an operational one:

| successes/job | jobs surviving | CPU wasted |
|---|---|---|
| 1,000,000 | 33% | ~50% |
| 100,000 | 90% | ~5% |

Shrinking the job by ten and multiplying the job count by ten leaves the physics
sample identical while cutting wasted CPU by roughly an order of magnitude.

**2026-08-21 retraction of the unbiasedness claim.** Whole-job discard prevents
truncated files from entering the sample, but it does not prove that completion
is independent of event content. The final campaign recorded 0/1000 hangs for
MONASH, 63/1063 for JUNCTIONS, and 64/1064 for CLOSEPACKING. The hang is in
`JunctionSplitting`, plausibly correlated with the topologies being measured.
Fresh-seed rate stability does not distinguish an independent failure from a
content-triggered mechanism with a stable probability. The external attempt
ledger and a preregistered observable-level bias study are required; until
then, all retained comparisons are conditioned on job completion and remain
publication-blocked. Selection by pre-assigned logical ID still prevents the
separate first-to-finish bias, but it does not close this hang-selection risk.

**Bit-layout headroom.** The `EventId` layout
`[campaign:16][tune:2][logical:14][attempt:12][local-success:20]`
(`generation/producer/HeavyFlavourUtils.h:403-419`) already accommodates this,
and more safely than before: 1000 jobs/tune uses a small part of the 14-bit
logical field, and 100,000 successes/job uses 10% of the 20-bit local-success
field, which at 1,000,000 sat at 95% of its 1,048,575 capacity.

**The 2-bit tune field is not a constraint on this study.** Two bits hold
ordinals 0-3, i.e. exactly four configurations, and the study defines four. It
would bind only on a *fifth* arm. Widening it is cheap in principle -- the
campaign field is 16 bits against an ordinal that is currently 1, so two bits
could move from `campaign` to `tune` -- but it changes the meaning of every
stored `event_id` and therefore requires a raw-schema bump, which supersedes
all existing production. **That is far cheaper before the full campaign than
after it**, so if a fifth configuration is ever wanted, decide it before
`make submit-full`, not later.

**Production runs three tunes; `JUNCTIONS_MATCHED` is not one of them.** It
exists as a card so that `make cards` can verify its fragmentation values
really are the Monash defaults (`tools/validate_tune_cards.py:58-71`) -- that
check is its entire purpose. Consistent with that, `TuneOrdinal`
(`HeavyFlavourUtils.h:396-401`) maps only the three published tunes and throws
for anything else, so a `JUNCTIONS_MATCHED` production job would fail at its
first event rather than silently produce data nothing downstream can merge.
The producer's accepted-tune list (`heavyflavourcorrelations_status.cpp:124`)
does include it, so the two lists disagree by design: the card is validated,
the tune is not producible. Do not "fix" that by adding it to `TuneOrdinal`
without first deciding to run it.

**Evidence.** `tools/validate_analysis_outputs.py:105-118` enforces the merge
shape -- equal exposure across tunes, at least ten jobs per tune, divisible by
ten -- and `merge_root_files.sh:59-68` re-derives the same shape from the
manifest. Note what it does *not* enforce: there is no minimum-jobs constant.
Jobs per tune is a campaign parameter, and the earlier floor of 100 was removed
in `1f411cf` precisely because it hardcoded one campaign shape and rejected
every other. `results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md` carries the
hang stack traces, rate measurement and upstream status.

(The two tests this paragraph used to cite, `test_canonical_merge_contract.py`
and `test_superseding_canonical_expansion.py`, were deleted with the gate
layer. They are not coming back; the checks that survived are the two above,
which run inside the pipeline rather than as a separate approval step.)

**Known limitation.** The 2x over-submission for JUNCTIONS and CLOSEPACKING was
sized for 1,000,000-event jobs, where two-thirds of jobs were lost. At 100,000
successes roughly 90% survive, so 2000 candidates for 1000 keeps is now far more
headroom than needed. It is retained because it is harmless and preserves the
existing contract shape, but it could be trimmed.

### 3.12 Generator threshold: `PhaseSpace:pTHatMin = 2.0`

**Choice.** 2.0 GeV, declared once in the `common_required_card_values` block
of `config/tune_difference_allowlist_v1.json:53` and propagated to all four
cards by `make set-pthat`. Changed from 1.0 on 2026-08-03.

**Why.** Event-activity classification is central to the study, and at 1.0 the
percentile classes were not the classes an experiment slices.
`MultipartonInteractions:pT0Ref` is 2.28 GeV for Monash. A threshold below it
asks for the hardest interaction in the event to be *softer* than the MPI
screening scale, which preferentially selects events with suppressed
underlying activity. The hard sample then has *lower* multiplicity than
minimum bias, which is the opposite of the naive expectation and is what made
the effect look mysterious before the mechanism was identified.

**Evidence.** `results/validation/generator/PTHAT_MULTIPLICITY_SCAN_8317.md`, measured on
PYTHIA 8.317. `dN_ch/deta`, minimum-bias convention (`|eta| < 0.5`, `pT -> 0`):

| `pTHatMin` | dN_ch/deta | vs minimum bias |
|---|---|---|
| 0.5 | 4.613 | −33.8 % |
| 1.0 | 4.973 | −28.6 % |
| **2.0 (production)** | **6.678** | **−4.2 %** |
| 4.0 | 10.492 | +50.6 % |

**Energy scaling — the card value is not the working point.** `pT0Ref` is
defined at a reference energy and scales with collision energy:

```
pT0(s) = pT0Ref x (sqrt(s) / ecmRef) ^ ecmPow
```

**Verified from produced metadata, not from defaults** — the `effective_settings`
tree of one raw file per tune, HF_PT2_INT, 2026-08-08. All three production
tunes carry `ecmPow = 0.215`, `ecmRef = 7000` GeV, `Beams:eCM = 13600` GeV, so
the common factor is `(13600/7000)^0.215 = 1.153494`:

| tune | `pT0Ref` (card) | effective `pT0` at 13.6 TeV | margin over the 2.0 threshold |
|---|---|---|---|
| MONASH | 2.28 (inherited, `Tune:pp = 14`) | **2.630** | **0.630** |
| JUNCTIONS | 2.15 | **2.480** | **0.480** |
| CLOSEPACKING | 2.194 | **2.531** | **0.531** |

**Card-value arithmetic understates the distances.** Comparing `pTHatMin = 2.0`
against the raw card numbers (2.28 / 2.15 / 2.194) suggests margins of
0.28 / 0.15 / 0.194; the true separations at 13.6 TeV are **more than twice
that**. The threshold sits comfortably below the screening scale for every tune,
and **JUNCTIONS is the tightest arm** either way.

**This does not settle the working point — it only removes an arithmetic
error.** The central event-activity axis is the one common set of absolute
boundaries in `config/multiplicity_class_boundaries_v1.json`. The MONASH
minimum-bias distribution supplies its percentile labels. The documentation
uses per-tune minimum-bias translations only as residual diagnostics; they do
not redefine the classes.

**Card text pending.** Three of the four cards carry a pasted sentence asserting
`pT0Ref` is 2.28 GeV, which is correct only for MONASH and JUNCTIONS_MATCHED
(both inherit it) and wrong for JUNCTIONS (2.15) and CLOSEPACKING (2.194). The
corrected per-card text is **parked** in a private registry-and-mapping proposal
rather than applied, because a card
edit — even comment-only — changes `effective_card_sha256`, which is recorded
per job in produced provenance. It lands with the registry change's provenance
break, so continuity breaks once rather than twice.

At 2.0 the MONASH hard sample is close to its minimum-bias activity reference.
That observation motivated the working point but does not define the common
absolute classes. Note the older -36 % figure quoted before this change was a
PYTHIA 8.315 measurement; on 8.317 the same configuration gives -28.6 %.

**These numbers are MONASH only, and that is a live limitation, not a
footnote.** `results/validation/generator/PTHAT_MULTIPLICITY_SCAN_8317.md:108-110` states
it: the threshold's effect on the two colour-reconnection tunes was not
measured, and their MPI screening scales differ --
`MultipartonInteractions:pT0Ref` is 2.28 for MONASH but 2.15 for JUNCTIONS and
2.194 for CLOSEPACKING (measured, `Validation/AuditTuneSettings.C` on HF_PT2).
`pTHatMin = 2.0` sits below all three, so the qualitative argument holds for
every tune; the -4.2 % magnitude does not transfer, and the crossing points
differ.

**Why this matters beyond tidiness.** Event activity is classified by common
absolute `N_ch` intervals across all three tunes. A tune-dependent offset from
minimum bias therefore changes the residual percentile translation, not the
selected integer interval. The committed MONASH, JUNCTIONS, and CLOSEPACKING
minimum-bias distributions quantify that residual. They do not turn the
central axis into per-tune quantiles.

**It does not cost trigger statistics**, contrary to the obvious worry. The
analysis already requires trigger `pT > 1 GeV`, and at 1.0 much of the charm
produced falls below that and never becomes a trigger. Measured on 100k MONASH
events, moving 1.0 -> 2.0: charm triggers per event 0.990 -> 1.196 (+21 %),
beauty 0.126 -> 0.212 (+68 %). The generated cross section is smaller, but
this is a generator study with a chosen event count, so that does not enter.

**Consequence.** All production at 1.0 is superseded, and the provenance chain
detects it mechanically rather than by convention: raw files embed the
tune-difference allowlist checksum they were produced under, so a 1.0 file
validated against the current allowlist fails with
`RAW_VALIDATION_ERROR tune-difference allowlist checksum mismatch`.

### 3.13 Contracts that live inside validators

Some design choices are enforced by a validator rather than stated as a
setting. They are listed here because a reader will not find them by reading
the cards or the config, and because this document's own rule (no design
choice may exist only in code) applies to them.

**The pair-file object set is generated, not restated.** Since
`config/pair_file_object_contract_v1.json` and its generated header
`AnalysisScripts/GeneratedPairObjectContract.h`, there is exactly one
definition of what a pair file contains. Before that there were three
hand-maintained copies, and they had drifted:

| Site | Held | Missing |
|---|---|---|
| `Validation/ValidatePairDirectory.C` | 58 names | -- |
| `Validation/ValidatePairBlockClosure.C:266-268` | 4 sparse names | `hFlavourClosure` |
| `plotting/Validate_THnSparse_Production.C:45-47` | 4 names | `hFlavourClosure`, `hCorrelationsByOrigin` |

The copy that drifted was the closure's, so **the ten-block closure silently
skipped `hFlavourClosure`**. The omission is visible in the closure's own
success line: `object_content_sumw2_closure_checks=1500` over 300 pair files is
five objects per file -- one `summed MULTIPLICITY` plus four sparses -- where
the contract says six. All three sites now filter the generated header.

The contract carries four axes, and their independence is the point.
`presence` (required / conditional) is *not* the same question as `closure`
(checked / exempt): an object can be always written yet unsuitable for a
sum-check, or suitable in principle yet written conditionally. Collapsing the
two is what produced the drift. Every `closure: exempt` row carries a
`closure_reason` stating why, so the reasoning sits at the point of use rather
than in a commit message.

**The one deliberate exception.** The contract requires `hFlavourClosure` and
`centralEligible` in every one of the 300 pair files, and *permits but does
not require* `hFlavourClosureSummary`. The asymmetry is physical, not
cosmetic: the summary is written only when `trigger.weightedTriggers > 0`, so
requiring it would fail any rare species that produced no triggers in a given
job -- a correctness bug that would look like a validation failure. Requiring
the other two is what makes a missing closure observable a hard error instead
of a silently absent histogram.

The flavour closure is a property of the **trigger**, not of the
trigger-associate pair, so it is duplicated across every pair file sharing a
trigger.

> **CORRECTED 2026-08-13 — this paragraph was wrong twice.**
> Private error-ledger entry E5.
>
> 1. **The factor was not 18.** Measured from the committed 300-pair registry:
>    **24× for every charm trigger** (D⁺ included) and **26× for every beauty
>    trigger**. The 18 was stale.
> 2. **It was not "a storage wart, not a correctness problem."** It became a
>    correctness problem the moment `extract_species_decomposition.py` summed
>    all 300 files: the published decomposition counted every trigger's closure
>    24 or 26 times. Because the factor **differs by sector**, it does not
>    cancel in any cross-sector quantity — the charm : beauty split was biased
>    by 0.7448 pp and the total inflated 24.2×.
>
> **The layout reasoning was sound** — moving the histograms would still break
> the plotting layer. What was unsound was concluding that a known duplication
> therefore needed no consumer-side rule. That rule now exists:
> `deduplicate_by_trigger()` sums each trigger once and fails closed if two
> copies of one trigger disagree.

This contract is why the first analysis attempt failed with 900
`unexpected object hFlavourClosure` errors per job: the objects were being
written before the validator was taught to expect them.

**The campaign shape is asserted in two shell validators.**
`Validation/validate_pair_directory.sh:35-38` requires the exact strings
`trigger_histogram_digest_groups=12`, `trigger_histogram_identity_comparisons=288`,
`multiplicity_histogram_digest_groups=1` and
`multiplicity_histogram_identity_comparisons=299`;
`Validation/validate_pair_block_closure.sh:41` requires
`central_pair_files=300 block_pair_files=3000` and the accompanying check
counts. These encode 300 pair files per job and ten blocks. They are correct
for the current generated pair registry (300 signed pairs) and would need
updating in lockstep with it -- they are *not* derived from
`AnalysisScripts/GeneratedPairRegistry.h`, they are literals.

**Final-plot provenance is switched off, not removed.**
`plotting/run_paper_plots.sh:162-165` sets `plot_provenance_tool=""`
because the tool it invoked was part of the gate layer. The per-target blocks
that used to populate it are left in place and are inert. This was chosen over
deleting them so the plotting targets themselves stayed untouched during the
purge; it means roughly sixty lines of the runner are dead and should not be
mistaken for a broken feature.

### 3.14 Campaign ordinals: unique where it matters, distinct by convention

**Choice.** Campaign ordinals must be unique among campaigns whose events could
appear in **the same merge**. Merges never span campaigns, so the historical
reuse of ordinal 1 by `HF_PT2`, `HF_SMOKE2` and `PTHAT2` is **harmless and is
not a defect to migrate**. New campaigns nonetheless take an unused ordinal, to
keep event IDs globally distinguishable — stricter than the invariant requires,
and it costs nothing. `HF_RUN3_V1` is ordinal **3**.

**Why.** The ordinal is packed into every event ID. The property that actually
matters is that two *different* campaigns' events can never be confused **inside
one merged dataset**, and since a merge is always built from a single campaign's
manifest, uniqueness across every campaign ever run is not required for
correctness. Writing this down settles a question that previously existed only
as a shared assumption, and it is the difference between a one-line fix and a
migration: an invariant of "globally unique" would declare three existing
campaigns non-compliant and demand their event IDs be rewritten, for no gain.

That ambiguity is what made a "derive the ordinal from disk and refuse to reuse
one" fix look attractive for `make submit-full`. It was rejected on two grounds:
it enforces the stricter convention as though it were the real invariant, and it
cannot see the whole history anyway — `HF_SMOKE` has no `attempt_metadata`, so a
disk-derived view would report its ordinal as free and hand it out again.
**A derivation that is silently incomplete is worse than an explicit demand.**

**Consequence.** The `Makefile` carries no `ORDINAL` default. All three submit
targets depend on `require-ordinal`, which refuses and names the ordinals
already in use. The Phase 4 checklist item "campaign registered with ordinal"
therefore cannot be satisfied by a default; it must be an explicit, verified
value.

**Evidence.** `Makefile` `require-ordinal`; the campaign records for the
ordinals measured on disk; `tools/resubmit_held.py` `campaign_ordinal_on_disk()`
for the narrower case where derivation *is* correct — a retry completing jobs
within one campaign, where the ordinal must match by construction.

---

### 3.15 Variation weights: OFF

**Choice.** PYTHIA's automated variation weights (`UncertaintyBands:*`) are
**not enabled**. Owner-signed 2026-08-09 (gate F1).

**Why — the decisive reason first.** **The three arms *are* the variation.**
MONASH, JUNCTIONS and CLOSEPACKING differ in exactly the hadronisation
parameters this study is about, and they are already handled the only way such
parameters can be: **separate runs.** PYTHIA's automated machinery reweights
parton-shower emissions and PDF members — it cannot reweight hadronisation,
because changing `StringFlav:probQQtoQ` or a colour-reconnection mode changes
*which hadrons form*, so there is no fixed configuration to reweight. **Enabling
weights would therefore buy shower and PDF systematics only, which are not the
paper's subject.**

*Scope note, kept honest:* the repo-side half of that claim is verified — no
hadronisation-variation weighting exists anywhere in this tree. The
PYTHIA-API half is argued from how the machinery works, **not tested against
8.317.**

**What it would have cost.** `event_weight` is a scalar `double`
(`generation/producer/heavyflavourcorrelations_status.cpp:709`), and
`sum_weights` / `sum_weights2` are scalar doubles (`:849-850`, `:1402-1403`,
`:1622-1623`). **`Validation/ValidateRawOutput.C:976` pins the schema as
`{"event_weight", "Double_t", 1}` — a declared contract asserting exactly one
double per event** — and `:466-467` reads the sums through `ReadScalar`.
**Turning weights on makes all three quantities vectors, breaking a declared
contract and touching 18 consumer files.** Raw grows from **88.0 MiB/job**
(~264 GB at 3000 jobs) by **~+18 %** at N≈20 weights, to ~312 GB; CPU overhead
**10–30 %**, an estimate rather than a measurement.

**The consequence, stated rather than hidden.** Automated PYTHIA variation
weights remain off, but separate single-setting campaigns measured scale and
PDF effects. `config/systematics_variations_v1.json` registers them, and
`results/systematics/20260820/` retains their results. This checkout lacks the
external variation manifests and raw unions, so it cannot recount the campaign
file totals.

## 4. Rebuilding the study from scratch

```bash
source ./setupEnv.sh   # resolves config/dependencies.conf, asserts versions
make doctor            # what does and does not resolve on this machine
make build             # build the producer
make check             # doctor + cards + cards-current + registry + all source-contract tests
```

Dependency locations and pinned versions live in `config/dependencies.conf`,
never in `setupEnv.sh`. On a machine where the defaults do not apply, copy
`config/dependencies.local.conf.example` to `config/dependencies.local.conf`
(untracked) and override only what differs; an exported environment variable
beats both. ROOT is the pinned ALICE CVMFS package; PYTHIA 8.317 is a stock
upstream build and is therefore version-asserted at setup rather than
identified by its path.

The ordered gate runners A-E were deleted with the publication-gate layer.
What replaced them is not a weaker version of the same thing but a smaller
one: `make check` is fail-closed and runs on every machine, and the
per-artifact validators (`Validation/ValidateRawOutput.C` before any raw file
is promoted, `Validation/ValidatePairDirectory.C` before any analysis
directory is promoted) run inside the pipeline rather than as a separate
approval step.

Two things the gates ran that `make check` does not, because they need ROOT
and real data: the N_ch calibration (Section 3.5,
`Validation/CalibrateMultiplicityAgainstMinBias.C`) and the primary-charged
definition proof (Section 3.6, `Validation/TestPrimaryChargedDefinition.C`).
Both are now run by hand. **If you change the multiplicity definition or the
decay policy, run them; nothing will remind you.**

The stage order still holds and is still worth respecting: build, then a smoke
campaign, then manifest, then analysis, then merge, then plots, then full
production. Evidence from an earlier commit cannot be cited as a pass for a
later one -- the raw files embed the commit and the card checksum, so this is
enforced mechanically rather than by convention.

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
| pair analysis schema | **`paul_pair_objects_primary_ground_v3`** |

> **CORRECTED 2026-08-13 — this row read `..._v2`** while the current campaign,
> the v3 merge and the recorded closure (2100 content / 1500 invariant) are all
> **v3** (review finding B2). The stale row mattered: a reader taking this table
> as the schema of record would have concluded that a v2 dataset was correct,
> which is precisely the state `README.md` says must be treated as failure.
> `Validation/validate_pair_block_closure.sh` now takes the required schema as
> an argument rather than reading it from the data (finding A4).

Any change to a physics definition bumps the raw schema. Older raw files then
become historical evidence and cannot satisfy a gate.

---

## 6. Known limitations, stated deliberately

These must remain visible in the paper. Do not quietly resolve them.

1. **`pTHatMin` is a sample-defining systematic, not a small correction.**
   Section 3.12 records the rationale for 2.0 GeV. Separate 1.0 and 4.0 GeV
   campaigns now measure the balance-observable response on the common class
   axis, and `results/systematics/20260820/per_class_deltas_seven.json` records
   the large two-sided shifts. The current per-cell budget includes S3
   provisionally. The raw
   unions and manifests remain external, so this checkout cannot independently
   recount them or reinterpret the threshold as a conventional perturbative
   uncertainty.

   A previous version of this list carried a limitation reading "the hard
   sample sits ~36 % below minimum bias ... not yet understood". It is deleted
   rather than corrected. The effect was real but is a property of a threshold
   the study no longer uses, and the mechanism is now understood and documented
   in Section 3.12 -- it was never a mystery, it was pTHatMin sitting below
   `pT0Ref`. The 36 % figure was also a PYTHIA 8.315 measurement; on 8.317 the
   same configuration gives 28.6 %
   (`results/validation/generator/PTHAT_MULTIPLICITY_SCAN_8317.md:62`).

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
