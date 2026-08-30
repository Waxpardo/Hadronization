# Campaign truth — what actually ran

Owner decision O1. Every number here is read from its artifact, not from prose.
Where the paper text disagrees with a value below, the difference is an owner
decision and is never resolved silently (ruling R34).

## Beam, tune base, processes, threshold

All three nominal cards under `generation/cards/` set the same four values:

| setting | value | site |
|---|---|---|
| `Beams:eCM` | `13600` — pp at **13.6 TeV** | `…MONASH.cmnd:17`, `…JUNCTIONS.cmnd:17`, `…CLOSEPACKING.cmnd:17` |
| `Tune:pp` | `14` (Monash) | each card `:20` |
| `HardQCD:hardccbar` | `on` | MONASH `:24`, JUNCTIONS `:45`, CLOSEPACKING `:61` |
| `HardQCD:hardbbbar` | `on` | MONASH `:25`, JUNCTIONS `:46`, CLOSEPACKING `:62` |
| `PhaseSpace:pTHatMin` | `2.` | MONASH `:47`, JUNCTIONS `:68`, CLOSEPACKING `:84` |

**The sample is forced, not filtered.** Every statement about minimum-bias
event activity must name the forcing. Call it a forced hard-heavy sample.

Runtime pins: PYTHIA **8.317** and ROOT **6.30.01**
(`config/dependencies.conf:36`, `:47`).

## `pT0Ref` is per tune, and only two cards set it

| tune | `MultipartonInteractions:pT0Ref` | how |
|---|---|---|
| MONASH | **2.28** | not set in the card; inherited from `Tune:pp = 14` |
| JUNCTIONS | **2.15** | `…JUNCTIONS.cmnd:30` |
| CLOSEPACKING | **2.194** | `…CLOSEPACKING.cmnd:31` |

`python3 tools/validate_tune_cards.py` prints
`MultipartonInteractions:pT0Ref MONASH=<PYTHIA_DEFAULT> JUNCTIONS=2.15
CLOSEPACKING=2.194` — the sentinel is what "the card does not set it" looks
like on stdout.

**The cards' own rationale comment is stale on this point** (ledger DA1-B002).
Each card asserts `pT0Ref is 2.28 GeV` and argues that a threshold below
`pT0Ref` selects events with suppressed underlying activity
(`…MONASH.cmnd:29-31`). That argument does not separate 2.0 from 1.0 for any
tune, because `pTHatMin = 2.0` is below all three `pT0Ref` values. The comment
repair waits for the systematics reactivation, because
`tools/make_systematic_cards.py:148-151` writes each nominal card's sha256 into all
21 generated variation cards, so editing a comment turns
`tests/test_systematics_variation_cards.py` red. Session CON-1 measured this
and stopped rather than re-pin.

**The real basis for 2.0 is empirical, and it is measured.**
`results/validation/generator/PTHAT_MULTIPLICITY_SCAN_8317.md:26-33`,
20,000 events per point on PYTHIA 8.317:

| sample | `dN_ch/dη` | against minimum bias |
|---|---|---|
| minimum bias (`SoftQCD:inelastic`) | 6.968 | — |
| hard, `pTHatMin = 1.0` | 4.973 | **−28.6 %** |
| hard, `pTHatMin = 2.0` | 6.678 | **−4.2 %** |
| hard, `pTHatMin = 4.0` | 10.492 | +50.6 % |

At 1.0 the percentile classes would slice a distribution whose mean is nearly a
third below the one an experiment slices. At 2.0 they mean what they say. The
minimum-bias reference reproduces ALICE 13 TeV INEL>0 (6.94 ± 0.10), so the
counter is sound and the deficit is physical (`:34-36`).

The choice costs no trigger statistics: moving 1.0 → 2.0 **raised** charm
triggers per event from 0.990 to 1.196 and beauty from 0.126 to 0.212, because
the analysis requires trigger `pT > 1` GeV and much of the charm produced below
2.0 never becomes a trigger (`…MONASH.cmnd:39-45`).

## Job layout

**1,000 canonical slots per tune × 100,000 successful events per job × 3
tunes.** Smaller jobs limit the work lost to a generator hang
(`docs/REPRODUCIBILITY.md:131`). `HF_RUN3_V1` holds campaign ordinal 3
(`config/campaign_ordinals_v1.json`, the ordinal-3 row).

## Hang disclosure (ruling R41)

Recorded attempt attrition, per tune
(`config/cr_holdout_policy_v1.json`, `observations`):

| tune | discarded | attempts | rate |
|---|---|---|---|
| MONASH | 0 | 1,000 | 0.00 % |
| JUNCTIONS | 63 | 1,063 | 5.93 % |
| CLOSEPACKING | 64 | 1,064 | 6.02 % |
| **all three** | **127** | **3,127** | **4.06 %** |

Every hang is in PYTHIA's `JunctionSplitting`: an unbounded accept-reject loop
in `splitJunGluons`, reached because the two junction tunes set
`ColourReconnection:allowDoubleJunRem = off`, which removes the cheap removal
path for a connected double-junction system
(`results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md:100-111`). That
is a deliberate physics setting from the QCD-CR tune, not a configuration
error. MONASH sets none of the three implicated settings and hung 0 of 3 in
that study; the two junction tunes hung 4 of 6.

Completed files are conditioned only on **zero hang-triggering events**: a
failed attempt promotes no ROOT file, a missing logical slot is regenerated
under a new deterministic seed, and only promoted complete outputs named by the
sealed canonical manifest enter reduction
(`config/cr_holdout_policy_v1.json`, `handling`).

The attrition is **disclosed as measured and is not corrected away or converted
into an event weight** (same field). The hang hits dense-junction topologies —
exactly the configurations under study — which is why the discard rate must be
reported rather than corrected (`docs/GOLDEN_OUTPUTS.md:1053`, row N5).

Ruling R41 accepts these rates. Whether the disclosure reads "unmeasured" or
"bounded, negligible" is the owner's editorial call in Overleaf; the architect's
completed-file conditioning bound is on record if the stronger wording is
wanted.

## Trigger and associate scope (ruling R40)

**Triggers** are the lightest meson **and** the lightest baryon per flavour:
B⁺ and Λ̄_b for beauty, D⁺ and Λ_c⁺ for charm. Each per-flavour balancing figure
carries two trigger columns, meson trigger left and baryon trigger right.

**Associates** default to the legacy set: beauty B⁻, B̄⁰, B̄_s⁰, B_c⁻, Λ_b;
charm D⁻, D̄⁰, Λ̄_c⁺. The generator carries an associate-set switch whose default
emits the paper configurations; any other value emits a new configuration
version.

**No cross-flavour observable.** There is no charm-to-beauty ratio. The
per-flavour figures stand side by side.

Each trigger group's legacy associate set contains its own reference meson
(Λ̄_b → B⁻, Λ_c⁺ → D⁻), so the exactly-one-reference resolution invariant holds
per column.

## The kinematic cuts

Trigger `pT > 1.0` GeV/c and associate `pT > 0.15` GeV/c, both **exclusive**;
`|η| <= 4.0`, **inclusive**, for both. The constants are named in
`generation/producer/HeavyFlavourUtils.h:477-479` and are written into every
merged pair file as `trigger_pt_min_exclusive`, `associate_pt_min_exclusive`
and `eta_abs_max_inclusive`
(`analysis/status_analysis_THnSparse_qq.C:1314-1316`).

The event-activity counter uses a **different and narrower** window, `|η| <= 1`.
See [../physics/MULTIPLICITY.md](../physics/MULTIPLICITY.md).
