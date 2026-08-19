# N_ch calibration under stock PYTHIA 8.317

**Date:** 2026-08-01
**Supersedes:** `NCH_CALIBRATION_20260730.md` (PYTHIA 8.315, ALICE CVMFS build)
**Purpose:** re-establish that `NCH_PRIMARY_CHARGED_ETA10_V1` reproduces the
published minimum-bias reference after the generator moved from the ALICE
CVMFS PYTHIA 8.315 package to a stock upstream 8.317 build.

## Why this had to be redone

8.316 changed defaults and code that plausibly move charged multiplicity:

- `StringFragmentation:stopMass` default 1.0 -> 0.8 GeV;
- trial-hadron generation in `StringFragmentation::kinematicsHadronTmp` fixed
  for the close-packing and thermal string-breaking frameworks;
- `StringFragmentation:eJunctionCutoff` / `mJunctionCutoff` introduced.

The calibration is a Gate-A gate, so it cannot be assumed to carry over.

## Environment

| | |
|---|---|
| PYTHIA | 8.317, stock upstream, `sha256 1ae551d1…45adf`, built `-std=c++20` |
| ROOT | 6.30.01 (ALICE CVMFS, unchanged) |
| Command | `root -l -b -q 'Validation/CalibrateMultiplicityAgainstMinBias.C(20000,false,10.0,false)'` |
| Sample | `SoftQCD:inelastic`, 13.6 TeV, tau0Max 10 mm, heavy decays enabled |
| Events | 20000 generated, 17312 INEL>0 accepted |

Invocation is byte-identical to the Gate-A entry in
`tools/run_publication_gate_a.py`.

## Result

```
counter                                    <N_ch>   dN_ch/deta
|eta|<0.5, pT>0     , heavy incl.           6.968        6.968
|eta|<0.5, pT>0.15  , heavy incl.           6.386        6.386
|eta|<0.5, pT>0.15  , heavy EXCL.           6.386        6.386
|eta|<1.0, pT>0.15  , heavy EXCL.          12.939        6.470
|eta|<4.0, pT>0.15  , heavy EXCL.          51.244        6.405
```

**VERDICT: PASS.** The counter reproduces the minimum-bias reference.

## Comparison against 8.315

| | 8.315 | 8.317 | shift |
|---|---|---|---|
| dN_ch/deta, MB convention | 7.007 | 6.968 | −0.039 (−0.56 %) |
| ALICE 13 TeV, INEL>0, pT->0 | 6.94 ± 0.10 | | |

Both versions sit inside the reference band, and 8.317 sits marginally closer
to the central value.

**The shift is not resolvable at this exposure, and must not be reported as a
physics effect.** The macro quotes no statistical uncertainty. For ~17 k
INEL>0 events drawn from a broad multiplicity distribution the standard error
on `<N_ch>` is of order 0.05, i.e. comparable to the 0.04 shift itself. This
run establishes only that 8.317 remains consistent with the reference — it does
**not** measure whether the 8.316 `stopMass` change moved the multiplicity. A
dedicated high-statistics comparison at fixed seed would be required for that,
and is not needed for Gate A.

## Scope

- Only the minimum-bias arm was rerun, matching the Gate-A protocol. The
  hard-sample and pTHat-scan numbers in `NCH_CALIBRATION_20260730.md` were
  measured under 8.315 and are **not** revalidated here.
- The pTHat-scan figures quoted in the project handoff (dN_ch/deta of
  4.31 / 4.55 / 6.05 / 9.74 at pTHatMin 0.5 / 1.0 / 2.0 / 4.0) therefore remain
  8.315 measurements and should be re-measured before they appear in the paper
  alongside 8.317 production.
