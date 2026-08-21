# Charged multiplicity of the hard sample vs pTHatMin, on PYTHIA 8.317

**Date:** 2026-08-03
**Supersedes:** the pTHat scan figures in `NCH_CALIBRATION_20260730.md`, which
were measured on 8.315 and are **not** valid for 8.317 production.
**Question answered:** are the percentile multiplicity classes computed inside
the hard-heavy-flavour sample comparable to experimental minimum-bias
multiplicity classes?

**Answer: no, not at the production threshold.**

## Method

`Validation/CalibrateMultiplicityAgainstMinBias.C`, 20 000 events per point,
13.6 TeV, `tau0Max = 10 mm`, heavy decays enabled. The minimum-bias reference
uses `SoftQCD:inelastic`; the hard points use `HardQCD:hardccbar` +
`HardQCD:hardbbbar` at the stated `PhaseSpace:pTHatMin`. The counter is the
same in every case, so any difference is a property of the sample, not of the
counter.

Invocation is byte-identical to the one that produced the Gate-A calibration.

## Result

`dN_ch/deta`, MB convention (`|eta| < 0.5`, `pT -> 0`, heavy inclusive):

| sample | 8.317 | vs MB | 8.315 (superseded) |
|---|---|---|---|
| minimum bias (`SoftQCD:inelastic`) | **6.968** | — | 7.007 |
| hard, `pTHatMin = 0.5` | 4.613 | −33.8 % | 4.31 |
| hard, `pTHatMin = 1.0` **(production)** | **4.973** | **−28.6 %** | 4.55 |
| hard, `pTHatMin = 2.0` | 6.678 | −4.2 % | 6.05 |
| hard, `pTHatMin = 4.0` | 10.492 | +50.6 % | 9.74 |

ALICE 13 TeV INEL>0, `pT -> 0`: 6.94 ± 0.10. The minimum-bias reference
reproduces it, so the counter is sound and the deficit below is physical.

## What this means

**At the production threshold the hard sample is not minimum-bias-like.** Its
charged multiplicity sits 28.6 % below minimum bias. Percentiles computed
*within* that sample therefore slice a distribution whose mean is nearly a
third lower than the one an experiment slices. A "0–10 % multiplicity class"
in this sample is not the same object as a "0–10 % multiplicity class" in
data, and must not be presented, plotted, or compared as if it were.

The cause is the generator threshold sitting below the multiparton-interaction
regularisation scale (`MultipartonInteractions:pT0Ref = 2.28` for Monash).
Requiring a hard process softer than the MPI cutoff selects events with
suppressed underlying-event activity, so the sample ends up *quieter* than
minimum bias despite containing a hard scattering.

**At `pTHatMin = 2.0` the sample is within 4.2 % of minimum bias.** That is the
actionable part: raising the threshold to 2.0 -- above `pT0Ref` -- would make
the multiplicity classes defensible, at the cost of cutting low-pT charm, which
is where most charm is. That is a physics trade-off, not a technical one, and
belongs to whoever decides the paper's scope.

## The paper's current number is wrong

`Model.tex` states the sample is "about 36 % below minimum bias". That is the
8.315 figure (4.55 / 7.007 = −35 %). On 8.317 it is **−28.6 %**. If the
sentence survives, the number must change.

## The 8.315 → 8.317 shift is real, and only in the hard sample

Every hard point moved up by 7–10 % while the minimum-bias reference moved down
by 0.6 %:

| | 8.315 | 8.317 | shift |
|---|---|---|---|
| MB | 7.007 | 6.968 | −0.6 % |
| hard 0.5 | 4.31 | 4.613 | +7.0 % |
| hard 1.0 | 4.55 | 4.973 | +9.3 % |
| hard 2.0 | 6.05 | 6.678 | +10.4 % |
| hard 4.0 | 9.74 | 10.492 | +7.7 % |

This is not statistics. At 20 000 events the standard error on `<N_ch>` is of
order 0.04, so the +0.42 at `pTHatMin = 1.0` is roughly ten standard errors.
The minimum-bias shift, by contrast, is within its own uncertainty and must
still not be reported as a physics effect.

A change confined to the hard sample points at the 8.316
`StringFragmentation:stopMass` default (1.0 → 0.8), which acts on
fragmentation of the harder strings a hard process produces. That attribution
is a hypothesis, not a measurement -- it has not been tested by varying
`stopMass` directly.

**Consequence: every pTHat-dependent number measured on 8.315 is superseded.**
None may appear in the paper alongside 8.317 production.

## Reproduce

```bash
source ./setupEnv.sh
root -l -b -q 'Validation/CalibrateMultiplicityAgainstMinBias.C(20000,false,10.0,false)'
for P in 0.5 1.0 2.0 4.0; do
  root -l -b -q "Validation/CalibrateMultiplicityAgainstMinBias.C(20000,true,10.0,false,$P)"
done
```

Roughly four minutes total on a Nikhef login node.

## Limits

- 20 000 events per point. Enough to establish the deficit (which is tens of
  standard errors) but not for a precision statement about any single point.
- MONASH only. The threshold's effect on the CR tunes is not measured here;
  their MPI scales differ (`pT0Ref` 2.15 and 2.194), so their crossing points
  will differ too.
- This measures *what the sample is*. It does not answer whether the physics
  conclusion is robust to the threshold, which is a separate comparison of the
  balancing observables at different `pTHatMin` values.

---

## Decision, 2026-08-03

**`PhaseSpace:pTHatMin` is set to 2.0 GeV in all tune cards.**

Event-activity classification is central to this study, so the sample has to be
one whose percentiles mean what an experiment's percentiles mean. At 1.0 GeV it
is not: 28.6 % below minimum bias. At 2.0 GeV it is within 4.2 %.

**There is no statistics cost. It was measured, and the yield goes up.**

The obvious worry -- charm falls steeply in pT, so a higher threshold throws
charm away -- does not apply here, because the analysis already requires
trigger `pT > 1 GeV/c`. At `pTHatMin = 1.0` a large fraction of the charm
produced sits below that cut and never becomes a trigger. Raising the
threshold produces harder charm, more of which passes.

MONASH, 100 000 events each, hard-origin triggers with `pT > 1 GeV/c`,
`|eta| <= 4`:

| | pTHatMin 1.0 | pTHatMin 2.0 | change |
|---|---|---|---|
| charm triggers per event | 0.9900 | 1.1963 | **+20.8 %** |
| beauty triggers per event | 0.1262 | 0.2121 | **+68.1 %** |
| charm baryon triggers | 4 609 | 5 603 | +21.6 % |

Beauty gains more because it needs more energy to produce, so it benefits more
from a harder subprocess.

The generated cross section at 2.0 is of course smaller, but this is a
generator study with a chosen number of events, not a luminosity-limited
measurement, so that does not enter. At fixed event count the higher threshold
gives both interpretable multiplicity classes and more usable triggers.

Consequences:

- Every production generated before this date used `pTHatMin = 1.0` and is
  superseded. It is different physics, not a different exposure.
- `Model.tex` must state 2.0 GeV, and the sentence about the sample being
  "about 36 % below minimum bias" should be removed rather than corrected --
  at 2.0 GeV the sample is close to minimum bias and the caveat no longer
  applies.
- The tune cards changed, so `config/tune_difference_allowlist_v1.json`,
  `generation/registries/GeneratedTuneSettingRegistry.h` and the allowlist checksum
  in `config/statistical_robustness_v1.json` were regenerated with them.
