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
implementation is that formula exactly (`extraction/harvest_class_axis.py:114-121`).
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
`tools/statistical_robustness.py:606-615` pins that exact string.

Ruling R39 supersedes the field's content. The field is **not** edited here,
because its tool is inside the paused module and the two must move together in
one edit (ledger DA1-A104). Recording the approval on this page and in
[../systematics/REACTIVATION.md](../systematics/REACTIVATION.md) does not touch
the paused module (ruling R31). The field flips on the reactivation checklist.

Read the ruling, not the field, for the scheme's status.

### Four things a reader should not have to re-derive

Session PHYS-1 measured these at HEAD, under brief item 3.

**1. What the field governs.** Its own rationale scopes it to the fixed-`N_ch`
cross-check: `fixed_nch_rationale` (`config/statistical_robustness_v1.json:5`)
calls them "Predeclared coarse absolute-activity intervals for a tune-to-tune
cross-check" and says *those boundaries* cannot support a publication claim
until the reviewer accepts them. The three intervals are `fixed_nch_selections`
— 0–19, 20–39, 40–79. The tool's own refusal message says the same, naming the
`fixed-Nch` review status. **But `validate_spec` gates the whole specification
on the field**, not the fixed-`N_ch` block alone, so operationally it governs
everything that function validates. The scope in the prose and the scope in the
code are not the same, and that gap is the reason this section exists.

**2. Which of the paper's numbers depend on it: none.**
`tools/statistical_robustness.py` is invoked by no `Makefile` target, no
`hadronization` subcommand and no pipeline script — the tool that reads the
field never runs on the deliverable path. The uncertainty the paper publishes is
computed by `extraction/harvest_class_axis.py:114-121`, which reads this
contract not at all. The ten blocks the figures rest on are built by
`merging/merge_root_files.sh:300-304` and
`tools/build_canonical_manifest.py:293-296`. The pending item covers a
descriptive cross-check whose own `description`
(`config/statistical_robustness_v1.json:6`) says it "deliberately defines no
publication pass threshold", and whose `fixed_nch_selections` carry no published
number.

**3. The R31 boundary, checked literally, and the coupling that decides it.**
The paused list names `tools/statistical_robustness.py` and four `config/`
artifacts — `config/systematics_*.json`, `config/verdict_v3.json`,
`config/a2_variations_v1.json`, `config/accepted_measurements_v1.json`.
`config/statistical_robustness_v1.json` **is not on that list**
([../systematics/STATUS.md](../systematics/STATUS.md) `:16-24`). No test pins its
sha256 either. So the file is not literally frozen and not literally paused.

It still cannot move alone. `validate_spec` refuses any value other than the
pending string, and `tests/test_statistical_robustness.py:164` calls
`validate_spec` on the real file — so changing the field turns the suite red
unless the tool changes with it, and the tool **is** on the paused list. That is
a measured result, not a reading: flipping the field in memory and calling
`validate_spec` raises `ValueError: statistical-robustness fixed-Nch review
status/rationale is absent`. R39 anticipated exactly this and ruled the two
"are updated together on the systematics reactivation checklist".

**4. `hf_final_scientific_review_v1` does not exist.** The rationale at
`config/statistical_robustness_v1.json:5` says the boundaries need the reviewer
to accept them "in `hf_final_scientific_review_v1`". No artifact of that name
exists in this repository, under any extension, and the identifier appears
nowhere outside the sentence that invokes it. The contract points at a review
record that was never created. That does not block the paper — by point 2
nothing published depends on it — but a reader who goes looking for the record
should be told it is not there.
