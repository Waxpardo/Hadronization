# B6 — status after the G2 scoping remediation

> **CLOSED 2026-08-09 by owner ruling.** Struck from G1; `RELEASE_BLOCKERS.md`
> §B6 carries the closure text. B6 closes on the residual being **characterised
> and attributed** — six `LbbarBcminus` failures in `M0_1`, coverage complete
> and yield genuinely zero at 10M events, with `BplusBcminus` passing in the
> same bin — **not** on the audit being made to pass. The check stays strict;
> `positive_required` is not weakened.
>
> **Follow-up recorded, not deferred:** re-run both targets against HF_RUN3_V1
> (**10×** larger — 100M events per tune against 10M) after its v3 analysis
> converges and merges.
> Still failing there ⇒ back to the owner as a physics-scope decision.

**The text below is as written before that ruling, and is left intact.**

**B6 is NOT closed.** It is one characterised step away, and the remaining step
is a physics-scope question rather than an engineering one.

---

## What B6 was blocked on, and what unblocked it

For six generations B6 could not run **at all**: no `hf_pt2_int` dataset existed
in either selector, so `run_paper_plots.sh`'s `thnsparse` and `audit-subsamples`
targets had no dataset to resolve. **That is fixed** — the entry is added, it
validates on Nikhef (`DATASET_SELECTOR_VALID active=hf_pt2_int_candidate
status=canonical_candidate blocks=10`), and both targets now execute end to end
over HF_PT2_INT.

---

## The G2 scoping remediation — the mechanism works

**First run, before scoping:** 54 failures, `beauty_failures=54 charm_failures=0`,
across two pairs.

**Second run, after encoding G2's B_c scope:**

```
SUBSAMPLE_COVERAGE_AUDIT_SUMMARY beauty_failures=6 charm_failures=0 total_failures=6
```

| | before | after |
|---|---|---|
| total failures | **54** | **6** |
| `BplusBcminus.root` | 14 | **0 — gone** |
| `LbbarBcminus.root` | 40 | **6** |
| bins affected | all classes | **only `hDPhiM0_1`** |
| charm | 0 | 0 |

**48 of 54 cleared, and exactly the out-of-scope ones.** Every surviving failure
sits in `M0_1` — **the top class, which G2 explicitly retains**. The mechanism
did precisely what it was built to do.

**The message fix also works.** All six report
`yield zero in all blocks (coverage complete)`, not the old
`technical coverage incomplete`, so a reader is no longer sent looking for absent
blocks that were all present.

---

## PRE-REGISTRATION MISSED — recorded as such

**I pre-registered that the audit would pass**, on the reasoning that all 54
prior failures were B_c pairs and descoping them clears the set. **It did not
pass: 6 remain.** The reasoning was right about *which* failures descoping
removes and wrong that descoping removes *all* of them — because G2 keeps the
top class, and one pair is empty even there.

---

## The residual, characterised

**All six are `Λ̄_b × B_c⁻` in the top multiplicity class, at 10 M events.**

The discriminating observation: **`BplusBcminus` now passes at both `M00_100`
and `M0_1`.** So B_c *is* populated in the top class for a B⁺ trigger. What is
empty is specifically the combination of a **beauty-baryon trigger** with a
**B_c associate** — doubly rare, and rare in a way that is about statistics
rather than about the scope declaration.

**That argues the residual resolves with statistics**, unlike the original 54:

| | original 54 | residual 6 |
|---|---|---|
| cause | observable outside G2's declared scope | pair too rare at 10 M events |
| fixed by statistics? | **no** — empty at any campaign size, which is why G2 declared the scope | **plausibly yes** — HF_RUN3_V1 is **100 M events per tune, 10×** |
| evidence | every class of both B_c pairs empty | the sibling B_c pair populates the same bin |

---

## What is needed to close B6

**Re-run both targets against HF_RUN3_V1 once its v3 analysis converges and
merges.** That is 10× the statistics on exactly the observable in question.

**Two outcomes, and both are informative:**

- **Green** ⇒ close B6, and the residual is confirmed as a statistics floor of
  the validation campaign.
- **Still failing on `Λ̄_b × B_c⁻` in `M0_1`** ⇒ that is a **physics-scope
  finding**, not an engineering one: it would mean G2's top-class retention does
  not hold for beauty-baryon triggers, and the scope for that pair should be
  integrated-only. **That is an owner decision and must not be taken by
  weakening `positive_required`.**

**Do not relax the check in either case.** It is correctly reporting that this
dataset cannot support the observable.

---

## The scoping mechanism, for the record

There was **no per-observable bin scoping in the plotting configuration at
all**. `subsample_error_bins_to_exclude` matches on bin name alone, so it
descopes a bin for *every* observable, and the audit target deliberately zeroes
it (`run_paper_plots.sh:366`) so the scan sees everything. Neither can express
"this pair, these bins".

**Added:** optional per-pair `multiplicity_scope` in the correlation entry.
Empty means all bins, so every pre-existing pair is unchanged. It is honoured
**even under `SUBSAMPLE_COVERAGE_AUDIT`** — unlike the global list — because an
undeclared bin is not an observable the analysis claims, so its emptiness is not
a coverage result.

**Exactly two rows carry a scope**, `BplusBcminus.root` and
`LbbarBcminus.root`, set to `["M00_100", "M0_1"]`.

> ### THE INDEX INVERSION — record it, it will bite otherwise
> **`M0_1` is the top class: 0–1 % is the HIGHEST-multiplicity class**
> (`Model.tex:126`), and it is where B_c lives.
>
> **But the shape memo's `c1…c11` indexing runs the opposite way to the
> percentile labels:**
>
> | memo | percentile label | multiplicity |
> |---|---|---|
> | **c11** | **`M0_1`** | **highest** |
> | c1 | `M90_100` | lowest |
>
> A reader who maps "c1 = first = top" gets the scope exactly backwards and
> descopes the only bin B_c populates. The mapping is mirrored in a comment in
> the plotting configuration itself.

**Runner:** `plotting/run_paper_plots.sh`, targets `audit-subsamples` and
`thnsparse`, with `DATASET_SELECTOR=config/dataset_selector_hf_pt2_int.json`.
**`USE_DATASET_SELECTOR` must not be set** — the runner tests it against the
literal string `"true"` and the default is already true; setting it to `1`
silently skips selector resolution entirely.
