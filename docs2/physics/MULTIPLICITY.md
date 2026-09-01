# Event activity — the counter and the classes

## The counter

The event-activity classifier counts **final charged non-heavy primaries** with
`pT > 0.15` GeV/c and `|η| <= 1`. One predicate carries all five conditions:

```
CountsNchPrimaryChargedV1(isFinal, isCharged, hasHeavyConstituent, pt, eta, etaMax)
  = isFinal && isCharged && !hasHeavyConstituent && IsMultiplicityKinematic(pt, eta, etaMax)
```

(`generation/producer/HeavyFlavourUtils.h:557-562`). The constants are named:
`kMultiplicityPtMin = 0.15`, `kMultiplicityEtaCentral = 1.0` (`:523-524`). The
producer fills the counter at
`generation/producer/heavyflavourcorrelations_status.cpp:1058-1063` and writes
it as `multiplicity_primary_charged_eta10_v1` (`:713-714`).

A second, wider counter at `kMultiplicityEtaWide = 4.0`
(`generation/producer/HeavyFlavourUtils.h:525`) is written as
`multiplicity_primary_charged_eta40_v1`
(`generation/producer/heavyflavourcorrelations_status.cpp:715-716`). **It
does not define the classes.**
`config/multiplicity_percentile_classes_v2.json` names
`multiplicity_primary_charged_eta10_v1` as its counter.

**The figure captions must state |η| ≤ 1.** The observable's own acceptance is
`|η| ≤ 4`; the classifier's is `|η| ≤ 1`. They are different windows and a
caption that quotes the wrong one is a defect the project has already met.

## Heavy-flavour hadrons are excluded, for two reasons

Both are recorded at the counting site
(`generation/producer/heavyflavourcorrelations_status.cpp:1026-1030` and
`generation/producer/HeavyFlavourUtils.h:515-521`):

1. They are final here **only because their decays were disabled**. An
   experiment would count their daughters instead.
2. Including them would correlate the event-activity classifier with the
   heavy-flavour observable it classifies.

Weak-decay products need no ancestry traversal to exclude, because the
production policy already makes `isFinal()` mean "primary" for light hadrons
(`generation/producer/HeavyFlavourUtils.h:508-513`).

## Eleven classes, resolved per tune

`config/multiplicity_percentile_classes_v2.json` declares eleven top-percentile
windows, `c1` (90–100 %) through `c11` (0–1 %), each with its bin name `M90_100`
… `M0_1`.

**Every tune resolves these percentile edges independently from its own merged
`summed MULTIPLICITY` histogram.** No minimum-bias tune and no common absolute
`N_ch` boundary defines another tune's classes
(`config/multiplicity_percentile_classes_v2.json`, `definition`; receipt
`boundary_source.mode` is `per_tune`,
`plotting/improvedPlotting_THnSparse.C:2765-2766`; histogram
`summed MULTIPLICITY` at `:2767`). Absolute `N_ch` thresholds are therefore
allowed to differ between tunes, and they do.

The tie rule: a threshold integer belongs to the **lower**-activity class, and
the adjacent higher-activity class starts at the threshold plus one
(`config/multiplicity_percentile_classes_v2.json`, `tie_rule`; the same rule as
a receipt literal at `plotting/improvedPlotting_THnSparse.C:2758-2760`).

Class bounds are inclusive integer `N_ch`, and the integrated 0–100 %
observable is deliberately outside the mutually exclusive partition
(`plotting/improvedPlotting_THnSparse.C:2761-2763`).

Use `c1` through `c11` as equal-fraction activity classes. Do not require common
absolute thresholds.

### Which fields of the class contract are load-bearing

`classes` and `counter` are read. Four fields are narrative provenance with no
consumer anywhere in the tree: `historical_contract.merge_commit`,
`historical_contract.implementation`, `counter` as a cross-check, and
`tie_rule`. Two of them exist a SECOND time as C++ string literals in the
boundary receipt — `tie_rule` at
`plotting/improvedPlotting_THnSparse.C:2758-2760` and the PR-13 merge commit at
`:2769` — and nothing compares the two copies. Treat the JSON strings as
the statement of record and the C++ literals as what a run actually writes.

`historical_contract.implementation` reads
PlottingScripts/improvedPlotting_THnSparse.C, written here without a code span
because nothing in this repository resolves it. **That path is the upstream
PR-13 tree, not this repository**, where there is no `PlottingScripts/`
directory; the workflow lives at `plotting/improvedPlotting_THnSparse.C`. The
sibling `github_pr` and `merge_commit` fields make the upstream intent clear,
and `tests/test_multiplicity_inset_boundary_source.py:28` checks `github_pr`
alone.

**The retired recipe is not a reproduction of these classes.** Summing the
MONASH minimum-bias CSV under `evidence/b4_multiplicity_mb/` reproduces the
retired common-axis calibration, not the current tune-local thresholds. The
current thresholds need the external per-tune merged inputs and are bound to the
v2 boundary receipts (ledger DA1-041).

## The decay-policy mismatch, disclosed (ruling R42)

The counter counts prompt charged particles under the heavy-hadrons-stable
policy. The experimental primary definition counts heavy-decay daughters,
because open-heavy hadrons have `cτ₀ < 1 cm`.

A paired minimum-bias measurement on PYTHIA 8.317 puts the undercount at
**0.767 %**: (7.040 − 6.986) / 7.040, over 172,825 and 172,429 accepted INEL>0
events (`results/validation/generator/NCH_DECAY_POLICY_BIAS_8317.md:47-58`;
REPORTED from that record, not re-run here).

Three caveats travel with the number, and all three belong in the disclosure:

- **The 0.767 % is minimum bias.** Nobody has measured the magnitude on the
  forced hard-heavy sample. It is unmeasured, not small.
- **The classes stay internally consistent**, because the percentile axis is
  built from the same counter for all three tunes.
- **Ruling R42 keeps the mismatch as measured and discloses it.** Properly
  defined and disclosed, this is not incorrect physics.

### The validation campaign, noted and not scheduled

Ruling R42 records a post-paper validation campaign. Nobody has scheduled it.

The design note recorded with the ruling matters, because the obvious approach
does not work: a full 3,000-job re-production with decays on cannot be paired
event by event against the production sample, since PYTHIA's single RNG stream
means "same seeds" stops guaranteeing pairing after the first event.

The design that does work is a **paired two-pass** run: generate under the
production policy, count `N_ch`, then decay the stabilised hadrons in the *same*
event with PYTHIA's `moreDecays()` and count again. One campaign, paired per
event, measures both the forced-sample bias and the per-class migration on the
tune-local axis exactly. It could ride a future campaign as a cheap extra
counter.

A minimum-bias arm — anchoring this axis to the experimental MB convention — is
a separate and secondary question, already partly covered by the B4 calibration.
