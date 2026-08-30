# Sample counting

What the generated-sample table counts, and why (ruling R37, owner decision O2).

`tools/count_generated_sample.C` produces the table from the current campaign's
raw trees. `tools/read_merged_event_counts.C` supplies N_ev.
`tests/test_count_generated_sample.py` asserts every number against three
hand-computed events.

## What is counted

**Species yields.** An exact signed-PDG match over the `heavyPdg` branch,
filtered on `heavyIsFinal`. Eight rows: B⁺, B⁻, Λ_b, Λ̄_b, D⁺, D⁻, Λ_c⁺, Λ̄_c⁻
(±521, ±5122, ±411, ±4122).

**Content sums.** `sum(heavyNc + heavyNcbar)` and `sum(heavyNb + heavyNbbar)`,
over the same `heavyIsFinal` filter. These count heavy QUARKS bound inside final
heavy hadrons, not hadrons. A hidden-heavy state contributes 2: a J/ψ carries one
c and one c̄. Such a state appears in the content sum and in none of the eight
species rows.

**N_ev.** Both `TParameter<Long64_t>` counters of the merged analysis file,
asserted equal. `source_input_events` is `chain.GetEntries()`; `input_events` is
`selectedEvents`
(`analysis/status_analysis_THnSparse_qq.C:1329-1332`, VERIFIED by reading). They
differ only under the event-modulo filter, which this campaign disables. A tool
that read one alone would be right by accident, so this one reads both and
refuses a number when they disagree.

## What is not counted, and why

**Not `final_heavy_qc_sum` / `final_heavy_qb_sum`.** These are net-valence
conservation checksums: `qc() { return nc - ncbar; }` and
`qb() { return nb - nbbar; }` (`generation/producer/HeavyFlavourUtils.h:344-345`,
VERIFIED). The producer requires them to be zero in a good event —
`heavyFlavourConservationOk = finalHeavyQcSum == 0 && finalHeavyQbSum == 0`
(`generation/producer/heavyflavourcorrelations_status.cpp:1369-1370`, VERIFIED).
A table built on them reports zero and looks like a sample with no heavy flavour
in it.

**No kinematic acceptance.** The producer stores every particle that satisfies
`isHadron && hasHeavyConstituent`, with no `isFinal` gate and no cut at storage
(`heavyflavourcorrelations_status.cpp:1071`, VERIFIED). The count applies
`heavyIsFinal` and nothing else. The old Overleaf table's `acc` population was
pT ≥ 0.15 and |η| ≤ 4. That is a different quantity, so the superscript does not
survive (owner decision O2).

## The decay policy

`StabilizeHeavyHadrons` walks the whole PYTHIA particle table. For every hadron
carrying a charm or beauty quark it calls
`pythia.particleData.mayDecay(id, false)`. It then re-reads each
id and throws `"heavy hadron remained decay-enabled"` if one is still enabled
(`heavyflavourcorrelations_status.cpp:360-421`, VERIFIED). The policy is
programmatic and fail-closed: it reads the particle table, and no card lists the
ids.

Two consequences follow, and both are structural rather than cuts:

- No B → D feed-down exists in the sample. Prompt charm is structural.
- The count takes the quantum numbers at hadronization, before weak decays move
  them. The balancing observable uses that same quantity.

## The N_ch disclosure (ruling R42)

The multiplicity counter counts prompt charged particles under the
heavy-hadrons-stable policy. The experimental primary definition counts
heavy-decay daughters, because open-heavy hadrons have cτ₀ < 1 cm. A paired
minimum-bias measurement on PYTHIA 8.317 puts the undercount at **0.767 %**:
(7.040 − 6.986) / 7.040
(`results/validation/generator/NCH_DECAY_POLICY_BIAS_8317.md:54-59`, VERIFIED by
reading). This session did not re-run that measurement, so the number is
REPORTED from the record.

Three caveats travel with that number:

- The 0.767 % holds for minimum bias. Nobody has measured the magnitude on the
  forced hard-heavy sample.
- The percentile classes stay internally consistent, because the percentile axis
  is built from the same counter for all three tunes.
- Ruling R42 keeps the mismatch as measured and discloses it. The ruling notes a
  paired two-pass validation campaign for after the paper. Nobody has scheduled
  it.
