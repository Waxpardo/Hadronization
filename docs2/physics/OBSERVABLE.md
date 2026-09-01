# The observable

The per-trigger balancing yield:

```
Y_bal = (N_OS - N_SS) / N_trig
```

and its angular form `B(Δφ) = (1/N_trig)(dN_OS/dΔφ - dN_SS/dΔφ)`.

## Opposite sign means opposite heavy-flavour sign

`OS` and `SS` compare **signed quark content**, not electric charge:
`q_b = n_b - n_b̄`. B⁺ carries `q_b = -1` and Λ_b⁰ carries `q_b = +1`, so they
form an opposite-sign pair. The pair registry, not the plotter, decides which
file is the OS partner of which trigger
(`config/heavy_flavour_pair_registry_v1.json`).

## The same-sign factor is one

The merged pair file records `same_sign_pair_factor` as **1.0**
(`analysis/status_analysis_THnSparse_qq.C:1317`), and the statistics contract
carries the same value (`config/statistical_robustness_v1.json`,
`contracts.same_sign_pair_factor`). Write `(OS−SS)/N_trig`. The legacy one-half
factor belongs to the `legacy-regression` target and to nothing on the paper
path.

## The trigger denominator is a dedicated count

`calculateOneYield` normalises each angular spectrum by the integral of its own
`hTrKinematics` projection, never by a trigger projection of `hCorrelations`
(`plotting/improvedPlotting_THnSparse.C:4061-4062`; the projection is
`GetTriggerPtHistograms` at `:1238-1291`, which projects axis 2 of
`hTrKinematics` at `:1287`).

It then refuses when the two denominators disagree. The OS and SS denominators
must match to a relative tolerance of `1e-10`, and a difference throws
`OS/SS trigger denominators differ` with both values printed
(`plotting/improvedPlotting_THnSparse.C:4069-4076`).
A zero denominator returns `NaN` with a warning rather than a silent division
(`plotting/improvedPlotting_THnSparse.C:4063-4068`).

The contract that makes this checkable: `contracts/GeneratedPairObjectContract.h`
**requires** additive `hTrKinematics` and **permits** conditional
`hFlavourClosureSummary`, whose absence is not an error. The summary is written
only when `trigger.weightedTriggers > 0`, so requiring it would fail every rare
species (`config/pair_file_object_contract_v1.json`, the
`hFlavourClosureSummary` row).

## Trigger and associate selections

Both must be final direct-primary central ground states — PYTHIA status 81–89
(`generation/producer/HeavyFlavourUtils.h:480-481`, applied at `:489-493`) — and both are cut on:

| | pT | \|η\| |
|---|---|---|
| trigger | `> 1.0` GeV/c, exclusive | `<= 4.0`, inclusive |
| associate | `> 0.15` GeV/c, exclusive | `<= 4.0`, inclusive |

The constants are named, never written as literals: `kCentralPtMinTrigger`,
`kCentralPtMinAssociate`, `kCentralEtaAbsMax`
(`generation/producer/HeavyFlavourUtils.h:477-479`), applied by
`IsCentralKinematic` (`:483-487`). The merged pair file records all three as
`trigger_pt_min_exclusive`, `associate_pt_min_exclusive` and
`eta_abs_max_inclusive` (`analysis/status_analysis_THnSparse_qq.C:1314-1316`).

## Ancestry is asymmetric, and that asymmetry is the observable

The **trigger** must resolve to the selected hard process: the reduction skips
any trigger whose origin is not `Origin::kSelectedHard`
(`analysis/status_analysis_THnSparse_qq.C:993`). The **associate** carries no
such requirement; its origin is recorded in six categories instead
(`contracts/AssociateOriginCategoryContract.h`).

This is not a convention that could go the other way. If both sides needed
resolved ancestry, the same-sign term would disappear by construction and there
would be nothing to subtract. Do not write a prompt or selected-hard associate
requirement into prose.

## Two exclusions inside the pair loop

Both live in the reduction, not in the producer:

- **Self-pairs**, by stored-particle identity rather than by species: the loop
  skips when the associate's `heavyIndex` equals the trigger's
  (`analysis/status_analysis_THnSparse_qq.C:1081-1083`).
- **Pairs sharing one selected hard parton**: the loop counts
  `sameHardConstituentPairs`, logs the first twenty with both PDGs and the
  shared hard index, and continues (`:1107-1121`).

No driver under `tests/` pins those two predicates. The nearest gate is
`tests/test_pthat_sensitivity.py:549-554`, which asserts that a nonzero
`same_hard_pairs` diagnostic is reported as a finding.

## Full angular axis only

The stored axis is `-π/2 <= Δφ < 3π/2` and the reported integrated yield covers
that full axis: `calculateOneYield` integrates the whole histogram
(`plotting/improvedPlotting_THnSparse.C:4083-4087`).
The owner ruling of 2026-08-21
selects the full axis as the supported integrated observable
(`docs/PHYSICS.md:282-288`).

No editable configuration, generated contract, test or accepted artifact defines
near-side or away-side boundaries. Near-side and away-side may describe features
of the distribution. **No near-side or away-side integrated yield is defined or
evidenced**, and a future regional observable needs a new signed decision and a
new contract.
