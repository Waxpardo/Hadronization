# N_ch calibration against a minimum-bias reference — 2026-07-30

Macro: `Validation/CalibrateMultiplicityAgainstMinBias.C`
Generator: PYTHIA 8.315, pp at 13.6 TeV, INEL>0 (>=1 charged particle, |eta|<1).
Reference: ALICE, Phys. Lett. B 753 (2016) 319, pp 13 TeV, INEL>0,
dN_ch/deta(|eta|<0.5) = 6.94 +- 0.10; ~7.0-7.1 expected at 13.6 TeV.

| configuration | dN_ch/deta, \|eta\|<0.5, pT->0 |
|---|---|
| MB, experimental decay convention (tau0Max = 10 mm, heavy decays on) | 7.007 |
| MB, exact production policy (tau0Max = 0.01 mm, heavy decays off) | 6.914 |
| HardQCD ccbar+bbbar, pTHatMin = 1 GeV, production policy | 4.558 |

In the actual central window (|eta| < 1, pT > 0.15, heavy flavour excluded):
minimum bias 6.416, hard-heavy sample 4.133.

## Conclusions

1. `NCH_PRIMARY_CHARGED_*_V1` reproduces the published minimum-bias reference
   to better than 1%. It is not defective and requires no change.
2. The production decay policy costs 1.3%. This is the bias from disabling
   heavy-hadron decays, whose daughters the experimental primary definition
   counts because open-heavy hadrons have c*tau0 < 1 cm. Small, bounded, and
   now quantified; it must be stated in the paper.
3. The pT > 0.15 GeV/c threshold costs ~8% relative to the pT -> 0
   extrapolation used by the reference.
4. OPEN ISSUE: the hard-heavy sample sits ~36% BELOW minimum bias at identical
   counter settings. Requiring a hard process normally raises activity, so this
   needs explanation before the multiplicity classes can be interpreted.
   `PhaseSpace:pTHatMin = 1` is below `MultipartonInteractions:pT0Ref = 2.15`,
   i.e. inside the regulated low-pT regime. This must be resolved by the
   pTHat sensitivity study (0.5 / 1.0 / 2.0 GeV) before the classes are used
   in any published figure, and the paper must not describe these percentile
   classes as comparable to experimental multiplicity classes.
