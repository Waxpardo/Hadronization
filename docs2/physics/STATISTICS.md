# Statistics — the ten-block scheme

**Ruling R39 approves this scheme.** The pooled-central / ten-block /
SEM-on-nine-degrees-of-freedom / nonlinear-inside-blocks prescription carries the
paper's uncertainties (supervisor decision relayed by the owner, 2026-08-30).
The paper's figures carry statistical uncertainties only; systematics are paused
under ruling R31.

Do not change any rule on this page without an owner ruling.

## The four rules

**1. The blocks are file blocks, not event blocks.** Assignment is
`canonical_slot % 10`, giving ten blocks of equal exposure
(`config/statistical_robustness_v1.json`,
`method.primary_partition.name = canonical_slot_modulo_10`; the same value is
stored in the manifest, `tools/build_canonical_manifest.py:281-287`).

**2. The central value is pooled.** It is the full union of the
manifest-derived, equal-N canonical files per tune
(`method.central_estimator`). **It is not the mean of the ten per-block
ratios**, and calling it one is a misstatement of the method.

**3. The uncertainty is the standard error across the ten blocks, on nine
degrees of freedom.** The contract writes it as
`sqrt(sum((x_k-mean(x))^2)/(K*(K-1)))`
(`config/statistical_robustness_v1.json`, `method.block_standard_error`) and the
implementation is that formula exactly (`extraction/harvest_class_axis.py:113-119`).
With `K = 10` the denominator is `10 × 9`.

**4. Nonlinear quantities are formed inside each block, before the standard
error is taken.** Two named rules, both in the contract:

- `os_ss_rule`: `form_OS_per_trigger_minus_SS_per_trigger_inside_every_resample`
- `ratio_rule`:
  `form_baryon_balancing_yield_over_reference_meson_balancing_yield_inside_every_resample`

Linear error propagation on pooled numerator and denominator gives a different
answer, and `tests/test_observable_contract.py:45-54` asserts that the two
differ — so the distinction is not academic.

## What the block partition is not

`root_sumw2_role` is `retained_for_input_validation_only_not_used_as_block_covariance`.
The ROOT `Sumw2` array validates inputs; it is never the uncertainty.

An alternative partition exists in the contract
(`method.alternative_partition`: the largest equal-exposure modulo partition not
exceeding 20), together with a delete-one-file jackknife
(`method.file_jackknife`, `N` replicates). Neither carries a published number.
The primary ten-block partition does.

## Fail-closed conditions

Four conditions are `technical_failure` rather than a value
(`config/statistical_robustness_v1.json`, `method`): a zero trigger denominator,
a zero reference-meson yield denominator, a non-finite value, and sparse
underflow or overflow (`integration.sparse_underflow_overflow_policy`).

A negative `OS−SS` yield is **not** a failure: the rule is
`retain_and_report`. Suppressing it would bias the mean.

## The contract's own review-status field

`config/statistical_robustness_v1.json:4` still reads
`"scientific_review_status": "PENDING_FINAL_PHYSICS_STATISTICS_REVIEW"`, and
`tools/statistical_robustness.py:606-614` pins that exact string.

Ruling R39 supersedes the field's content. The field is **not** edited here,
because its tool is inside the paused module and the two must move together in
one edit (ledger DA1-A104). Recording the approval on this page and in
[../systematics/REACTIVATION.md](../systematics/REACTIVATION.md) does not touch
the paused module (ruling R31). The field flips on the reactivation checklist.

Read the ruling, not the field, for the scheme's status.
