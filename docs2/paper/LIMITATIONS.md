# What the paper may claim without systematic uncertainties

Session PHYS-1 wrote this page under brief item 2. It is the paper-facing
statement of a limit that until now existed only as an internal note about a
paused module. It is a **framing** page: it introduces no measurement and asks
for none.

Chosen as a new page rather than a section of [CLAIM_MAP.md](CLAIM_MAP.md)
because the claim map is one row per claim, and this is a statement about the
whole result set. The claim map links here instead.

## 1. The plain statement

**No systematic uncertainty is evaluated for any number in this paper.** Every
uncertainty on every figure and table is the ten-block statistical uncertainty:
pooled central value, ten file blocks assigned by `canonical_slot % 10`,
standard error across the blocks on nine degrees of freedom, nonlinear
quantities formed inside each block
([../physics/STATISTICS.md](../physics/STATISTICS.md); the implementation is
`extraction/harvest_class_axis.py:114-121`).

The cause is a decision, not an oversight. Ruling **R31** paused systematics
development; the module stays intact and toggleable and is not on the paper's
critical path ([../systematics/STATUS.md](../systematics/STATUS.md)).

## 2. The programme that would have bounded them

Six sources are defined in `docs/SYSTEMATICS.md`. That document carries a
banner at its head (`:9-29`) recording that rulings R9 and R11 are not folded
into its prose and that **the executable contract is authoritative**. The
contract is `config/systematics_sources_v1.json`, and the statuses below are
read from it, not from the prose.

| source | varied choice | status in the contract |
|---|---|---|
| S1a | `SigmaProcess:renormMultFac` | `included: true` |
| S1b | `SigmaProcess:factorMultFac` | `included: true` |
| S2 | `PDF:pSet`, NNPDF2.3 LO to CTEQ6L1 | `included: true` |
| S3 | `PhaseSpace:pTHatMin`, 2.0 to 1.0 and 4.0 | `included: true`, but **one-sided**: the `HF_SYS_PTHAT_4` arm only, the `HF_SYS_PTHAT_1` arm excluded under R9 |
| S4 | event-activity counter window, `\|eta\| <= 1` to `\|eta\| <= 4` | `declared_absent`: "registers S4 and DELIBERATELY does not launch it. No campaign, no receipt, and no term." |
| S5 | decay-daughter bias in class assignment | `included: false` under R11, `exclusion_reason` "unresolved; re-derivation on the percentile axis pending" |
| S6 | duplicate hard-carrier ordering | `declared_absent` from the class totals: it lives on the `M1`–`M5` partition and "is NEVER summed into a `c1..c11` total" |

Four variation campaigns for S1a, S1b, S2 and S3 were launched and hold
campaign ordinals (`config/campaign_ordinals_v1.json`;
[../systematics/STATUS.md](../systematics/STATUS.md)). **Their results are not
usable for this paper**: they were produced on the retired common absolute
multiplicity axis, and both retired trees — the ones dated 2026-08-19 and
2026-08-20 — carry `"current_or_publication_use": "PROHIBITED"`. Re-derivation
on the percentile axis is the pending work
([../systematics/REACTIVATION.md](../systematics/REACTIVATION.md)).

So the honest description is not "systematics were never started". It is: the
programme was designed and partly run, its results were invalidated by an axis
change, and the re-derivation is deferred under R31.

## 3. The cancellation argument, and its exact limits

The argument is that a *differential* comparison between the three tunes is
insensitive to much of what a single-tune measurement would have to bound. It
holds, and its scope is measurable from the cards themselves.

**What the three tunes share, byte-for-byte.** Taking the settings common to
`generation/cards/pythiasettings_Hard_Low_ccbb_MONASH.cmnd`,
`…_JUNCTIONS.cmnd` and `…_CLOSEPACKING.cmnd`:

- the beam configuration — `Beams:eCM = 13600`, `Beams:idA = 2212`,
  `Beams:idB = 2212`;
- the hard process — `HardQCD:hardccbar = on`, `HardQCD:hardbbbar = on`;
- **the generation cut** — `PhaseSpace:pTHatMin = 2.`;
- **the decay policy** — `ParticleDecays:limitTau0 = on`,
  `ParticleDecays:tau0Max = 0.01`;
- the base tune `Tune:pp = 14`, before the per-tune overrides.

They also share the generator and runtime pins, PYTHIA 8.317 and ROOT 6.30.01
([CAMPAIGN_TRUTH.md](CAMPAIGN_TRUTH.md) `:22`), the event-activity counter
`multiplicity_primary_charged_eta10_v1`, the percentile class *rule*, and the
whole reduction and analysis chain
(`config/multiplicity_percentile_classes_v2.json`, `counter` and `definition`).

**What therefore cancels to first order.** A variation applied to any of the
shared inputs moves all three tunes in the same direction. In a tune-to-tune
difference or ratio the common part cancels, and what survives is the
*difference in response* between tunes — a second-order quantity. This covers
S1a, S1b, S2 and S3 in their entirety, because scale choices, the parton
distribution and `pTHatMin` are all common inputs.

**What does not cancel, and why.** Three things, and none of them is a detail.

1. **The tune parameters themselves.** The cards differ in exactly the
   hadronization and colour-reconnection settings under study, including the
   baryon-production knobs `StringFlav:probQQtoQ` (0.078 in JUNCTIONS, 0.081 in
   CLOSEPACKING) and `StringFlav:probQQ1toQQ0join`. This is not a systematic
   that failed to cancel; it is the measurement. The contract says so itself:
   `config/systematics_sources_v1.json`, `declared_absent`, records
   `tune_bundle_spread` with the reason "The spread between tune bundles is the
   measurement, not a systematic uncertainty. Folding it into a band would
   destroy the quantity the paper reports."
2. **The class definition's mapping to absolute activity.** The percentile rule
   is shared, but `config/multiplicity_percentile_classes_v2.json`, `definition`
   states that "Every tune resolves these percentile edges independently from
   its own merged summed MULTIPLICITY histogram; no minimum-bias tune and no
   common absolute `N_ch` boundary defines another tune's classes." The tunes
   also set different underlying-event activity: `MultipartonInteractions:pT0Ref`
   is 2.28 in MONASH, 2.15 in JUNCTIONS and 2.194 in CLOSEPACKING. So a given
   percentile class is a different absolute-`N_ch` selection in each tune by
   construction, and a variation of the class definition does **not** cancel
   between tunes. This is the S4 and S5 territory, and both are absent.
3. **Any effect whose response depends on the hadronization settings.** The
   cancellation is first-order. Where a shared input couples to the parameters
   being varied — and baryon production is precisely such a place — the residual
   is not obviously small, and nothing here bounds it.

## 4. The three variations a referee will ask for

For each: what the repository holds, and what it does not.

**`pTHatMin`.** The repository holds a scan at
`results/validation/generator/PTHAT_MULTIPLICITY_SCAN_8317.md`: four thresholds
at 20,000 events per point on PYTHIA 8.317, reporting `dN_ch/deta` of 4.613,
4.973, 6.678 and 10.492 at 0.5, 1.0, 2.0 and 4.0 against a minimum-bias
reference of 6.968 (`:27-36`). **It is measured on charged multiplicity, not on
the balancing observable.** It justified the production threshold; it is not a
systematic on any published number. The S3 campaign that would be is one-sided
and on a retired axis (§2).

**The class-boundary definition.** S4 was registered and deliberately not
launched; S5 is excluded pending re-derivation (§2). Related and separate,
ruling **R42** records that the `N_ch` decay-policy mismatch "stays as measured
and is disclosed", with a validation campaign noted for after the paper
([../decisions/RULINGS.md](../decisions/RULINGS.md)); the measurement is
`results/validation/generator/NCH_DECAY_POLICY_BIAS_8317.md`. The repository
therefore holds a *characterisation* of this effect and no *systematic* on it.

**The decay policy.** Shared across the three tunes as `tau0Max = 0.01`
(§3), so it is a common input and cancels to first order in the tune
comparison. It does not cancel in any absolute statement about a single tune.
S5 is the source that would have bounded it, and it is excluded.

## 5. What a reader may conclude

**Supported.** Comparative statements between the three tunes — that a
balancing yield, or a baryon-to-meson balancing ratio, is higher or lower in one
tune than another, and how that difference varies with event activity — with the
uncertainty stated as the ten-block statistical error. These are the comparisons
the analysis was built for, and they are the ones the shared configuration of §3
protects.

**Supported with care.** Statements about the *size* of a tune-to-tune
difference. The cancellation of §3 is first-order; a difference small compared
with its own statistical error is not made significant by the argument, and a
difference that depends on the class definition inherits the non-cancellation of
§3.2.

**Not supported.** Any absolute statement about a single tune quoted with an
uncertainty, as if that uncertainty were complete — it is statistical only.
Any comparison with experimental data that treats the quoted error as a total.
Any statement that the systematic uncertainties are small, negligible, or
bounded: none was evaluated, and this page makes no such claim.

**A separate limit, stated elsewhere.** Attempt attrition and whether the
discarded jobs can bias the observable are treated in
[../physics/DISCARD_BIAS.md](../physics/DISCARD_BIAS.md), which is an
unratified draft. That is a different question from systematics and is not
covered by anything on this page.

## 6. Status

This page records a limit; it does not decide how the manuscript words it.
Under ruling R38 no session edits `paper/`, and
[../decisions/OPEN_QUESTIONS.md](../decisions/OPEN_QUESTIONS.md) item 1 names
the owner, with the supervisor, as the decision's owner.
