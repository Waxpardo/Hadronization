# Systematics reactivation checklist

Ruling R31 pauses systematics development. The module stays in the tree and its
tests stay green. A later session must be
able to finish it without touching the rest of the pipeline. This file is that
session's work list.

Nothing here is a defect in the paper path. The paper's figures carry ten-block
statistical uncertainties (ruling R39). The DA-1 deep audit found every row
below and
dispositioned it SYS-DORMANT, because ruling R31 pauses its subject.

**Do not gold-plate a paused module.** Work this list when the module is
switched on, not before.

## Scope boundary

These files are not edited while the pause holds:

`tools/systematics_*.py`, `tools/statistical_robustness.py`, `tools/a2_*.py`,
`tools/assert_systematics_envelope.py`,
`plotting/render_systematics_overlay.py`,
`extraction/write_verdict.py`, `extraction/combine_per_class.py`,
`extraction/combine_derived.py`, `extraction/write_tune_separation.py`,
`extraction/write_per_class_report.py`,
`extraction/write_combination_report.py`,
`analysis/a2_*`, `config/systematics_*.json`, `config/verdict_v3.json`,
`config/a2_variations_v1.json`, `config/accepted_measurements_v1.json`,
`tools/evaluate_pthat_sensitivity.py`.

`docs/SYSTEMATICS_PREREGISTRATION.md` stays byte-identical
(sha256 `a42ef9915cf555d637f66f56aef1f120113aaa27e0a6d9a9b3dfe1e5f72d2826`,
pinned fourteen times across eight selector files).

## The 37 dormant rows

### Contracts and declared keys

| id | where | subject |
|---|---|---|
| DA1-019 | `config/statistical_robustness_v1.json:16` | a non-constraining field reads as a contract |
| DA1-A096 | `config/statistical_robustness_v1.json:171-176` | declared key with no consumer |
| DA1-A103 | `config/statistical_robustness_v1.json:3` | an unenforced freeze |
| DA1-A105 | `config/statistical_robustness_v1.json:5` | stale citation |
| DA1-A109 | `config/statistical_robustness_v1.json:49`, `extraction/combine_per_class.py:173` | one constant, two copies |
| DA1-A106 | `config/systematic_variation_settings_v1.json:11, :17, :23` | declared keys with no consumer |
| DA1-A107 | `config/systematics_variations_v1.json:15, :25, :35, :45, :55, :65, :75` | declared values nothing validates |
| DA1-A108 | `config/systematics_sources_v1.json:5` | incomplete consumer record |
| DA1-A110 | `config/verdict_v3.json:56-61` | declared keys with no consumer |
| DA1-A112 | `config/systematics_envelope_v1.json:35, :50, :4, :32, :51, :52` | citations that do not resolve |
| DA1-A115 | `config/a2_variations_v1.json:7, :14, :24` | pins nothing can verify |
| DA1-A139 | `config/pthat_sensitivity_v1.json` (six ranges) | declared keys with no consumer |
| DA1-A140 | `config/pthat_sensitivity_v1.json:18, 34, 61-63, 70, 86, 116` | declared keys with no consumer |

### Gates and generators

| id | where | subject |
|---|---|---|
| DA1-A097 | `config/systematics_envelope_v1.json:6-15` | a gate that protects nothing |
| DA1-A098 | `tools/systematics_envelope.py:437, :594` | the consumer writes an undeclared key |
| DA1-A049 | `tools/add_variation_selector_rows.py:44` | the generator emits a row its consumer refuses |
| DA1-A050 | `tools/add_variation_selector_rows.py:107` | the generator cannot reproduce its own artifact |
| DA1-A051 | `tools/add_variation_selector_rows.py:58` | stale line citation |
| DA1-A128 | `tools/systematics_request.py:122-126` | a silent fallback in the preflight's verified flag |
| DA1-A077 | `Validation/PTHatSensitivity.C:152-165` | an unprotected duplicate of the contract |
| DA1-A147 | `tests/test_environment_verdict.py:99` | asymmetric contract derivation |
| DA1-B007 | `tests/test_systematics_variation_cards.py:83 vs :84, :93, :96` | the comment contradicts the code |
| DA1-A113 | `extraction/systematics_delta.py:203` | the document overstates the gate |
| DA1-B071 | `docs/SYSTEMATICS_PREREGISTRATION.md:492-493`, `Validation/CalibrateMultiplicityAgainstMinBias.C` | the documented cut boundary is strict where the code is inclusive |

### Overlays and report writers

| id | where | subject |
|---|---|---|
| DA1-029 | `plotting/render_systematics_overlay.py:117-173, :273-335`; `hadronization:419-430` | the nominal log is not bound to the envelope |
| D7 | `extraction/write_tune_separation.py:59-92`; `write_per_class_report.py`; `write_combination_report.py` | each raises `KeyError` on an `MB` component against an eleven-class render |
| finding 29 | `extraction/write_tune_separation.py:89-92` | tune-separation wording |
| DA1-033 | `extraction/write_combination_report.py:70-73, :104-105` | stale systematic scope and cardinality |

### The A2 arm

| id | where | subject |
|---|---|---|
| DA1-034 | `tools/a2_record_regression.py:30-119, :156-169` | a vacuous pass and an asymmetric comparison |
| DA1-B094 | `analysis/a2_block_shift.py:350-359` | silently variable dof in the headline SEM |
| DA1-B095 | `analysis/a2_block_shift.py:383, :388-390` | the pre-registered STOP condition is printed, not enforced |
| DA1-B096 | `analysis/a2_pair_yield.C:29-35, :93` | a missing include; the file cannot compile |
| DA1-B097 | `analysis/a2_pair_yield.C:82-83` | the axis is selected by position with no identity check |
| DA1-B098 | `analysis/a2_pair_yield.C:66-81, :109-110`; `tools/a2_extract_yields.sh:44-45, :57-64` | unequal file coverage between the two arms is not detected |
| DA1-B100 | `analysis/a2_pair_yield.C:40-41`; `analysis/a2_block_shift.py:352-353` | an event class is silently outside the partition |

## Rows that ride the module

These are not systematics defects. Each one waits because its repair lands
inside
the paused files.

**D1, D2, D11 — the boundary-receipt digest canonicalizer.** Two Python
validators, `extraction/write_verdict.py:163` and
`tools/statistical_robustness.py:1438`, reparse and re-serialize a receipt body
before digesting it. The C++ writer emitted the non-shortest double text
`0.8935862999999999` (= 0.8935863). The canonicalization renormalized it, so the
validator refused a receipt whose own digest is self-consistent. Ruling R30 puts
the repair in the gate, not in the data.

One canonicalizer closes all three. It must:

1. Parse with `parse_float` and `parse_int` as `str`.
2. Drop `payload_sha256`.
3. Re-serialize compact and key-sorted, with the writer's number tokens
   verbatim.
4. Pass `ensure_ascii=False`. This is D11: `json.dumps` defaults to
   `ensure_ascii=True` and emits `\uXXXX` where nlohmann's `dump()` emits raw
   UTF-8. It is inert today, because 52 tracked JSON contracts carry zero
   non-ASCII bytes.

The TS-1 fixture is
`be7071d34f9f7dc1323e4934474d676ff3772fd6aeb46f0b83ba211f2b7d3963`.

**D8 — accepted-root pins and `--require-pinned-or-current`.** Hiding one
variation `measurement_receipt.json` from the current commit root leaves
`tools/systematics_request.py:107-131` printing `verified=False` and
`SYSTEMATICS_PREFLIGHT_ONLY status=PASS` with exit 0. Assert that every
`accepted_roots` entry has `source == current_commit_root` before extraction; a
`--require-current-root` option moves the gate into source.

**D10 — `created_utc` and byte reproducibility.**
`extraction/write_verdict.py:963`
stamps a timestamp, so two runs on identical inputs give different
`verdict_v3.json` digests. A changed digest after a rerun is not a changed
result. Record this beside the command that orders the rerun.

**DA1-A129 — validator path coupling.**
`tools/statistical_robustness.py:1404-1413`
compares a contract value against a hardcoded constant. This blocked a pin move
for the paused envelope; it is BLOCKS_STAGE and is the first row to clear when
the module reopens.

**DA1-A104 with ruling R39 — `scientific_review_status`.** The pooled-central /
ten-block / SEM-dof-9 / nonlinear-inside-blocks scheme carries the paper's
uncertainties. R39 approves it (supervisor decision relayed by the owner,
2026-08-30). Update the contract's `scientific_review_status` field
(`config/statistical_robustness_v1.json:4`) and the paused tool that pins its
exact string (`tools/statistical_robustness.py:606-612`) TOGETHER, in one edit,
on this checklist. The gate fires on sound data today, which ruling R30
classifies as a defect in the gate. This record and its docs2 counterpart do not
touch the paused module.

**DA1-B002 — the card pTHat rationale.** Not a systematics defect, blocked by
one. The three published cards carry a comment asserting
`MultipartonInteractions:pT0Ref` is 2.28 GeV uniformly and arguing that a
threshold below pT0Ref selects suppressed underlying activity. The cards
override pT0Ref per tune: MONASH 2.28, JUNCTIONS 2.15, CLOSEPACKING 2.194. Each
card sets `PhaseSpace:pTHatMin = 2.`, which is below all three. The argument
therefore does not separate 2.0 from 1.0 for any tune. The real basis is
empirical and already in the card: at 1.0 the sample sits
29 % below minimum bias, at 2.0 within 4.2 %.

The repair is comments only and changes no value.

Why it waits: `tools/make_systematic_cards.py:151` writes each nominal card's
sha256 into all 21 generated variation cards. A comment edit therefore makes
every one of them stale and turns `tests/test_systematics_variation_cards.py`
red. Session CON-1 measured this and stopped rather than re-pin. Regenerate
those 21 cards here in one command, where the module is open anyway.

## The R32 record

Ruling R32 removed the JUNCTIONS_MATCHED fourth tune. Its card and eight of the
nine references left the tree in session CON-1.

`docs/SYSTEMATICS_PREREGISTRATION.md:123` KEEPS its sentence verbatim:

> a limit on interpretation, and `JUNCTIONS_MATCHED` exists to address it.

That sentence is a frozen record of the plan, and a pre-registration edited
after the fact is not one. Eight selector files pin the file's digest fourteen
times, so the annotation goes here instead (owner decision O5 default).

The limit itself still stands. `tools/validate_tune_cards.py` states it where
the removed check used to sit: JUNCTIONS retunes the Lund and diquark parameters
away from Monash. A MONASH/JUNCTIONS difference in a baryon observable therefore
cannot on its own establish junction formation. The paper states that limit
rather than isolating it.
