# A2: the guard removed, the campaign re-run, and Δ measured — 2026-08-13 (thirteenth session)

**Suite 42/42 → 43/43.** Wall clock 18:43–19:40 CEST. `stbc-i3` up 19 h 37 m,
load ~2.5 — the pool that was jammed at 88 k idle last session had drained, and
the full re-run took **19 minutes**.

---

## THE RESULT

Δ(m) = [Y_perm(m) − Y_base(m)] / Y_base(m), formed inside each block, averaged
over ten blocks (`slot % 10`, dof 9). 100 slots × 3 tunes, 10 M events per tune.
**Per cent:**

| class | N_ch | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|---|
| M1 | 1–9 | 0.0000 | 0.0072 ± 0.0010 | 0.0098 ± 0.0008 |
| M2 | 10–19 | 0.0000 | 0.0255 ± 0.0012 | 0.0220 ± 0.0026 |
| M3 | 20–29 | 0.0000 | 0.0323 ± 0.0060 | 0.0365 ± 0.0046 |
| M4 | 30–39 | 0.0000 | 0.0372 ± 0.0045 | 0.0614 ± 0.0095 |
| M5 | ≥ 40 | 0.0000 | **0.0697 ± 0.0124** | 0.0420 ± 0.0135 |
| **int.** | | **0.0000** | **0.0194 ± 0.0014** | **0.0192 ± 0.0007** |

> **VERDICT: MONASH negligible. Both CR tunes MUST BE QUOTED PER MULTIPLICITY
> CLASS.** Small — nothing exceeds **0.07 %** — but **not flat**: JUNCTIONS
> rises monotonically by **9.7×** across the classes, at up to 5.6 σ.

**The flat outcome the pre-registration named in advance as a legitimate result
did not occur.** A2's concern is therefore **confirmed, not retired**: the
integrated 0.019 % understates JUNCTIONS' highest-activity class by 3.6×.

Full table, the pre-registration scored verbatim (all four expectations, all
four positive checks), and the provenance block:
`docs/a2_results_20260813/A2_DELTA_RESULT.md`, with the analyzer's own output
preserved beside it.

### MONASH's exact zero was checked, not assumed

An exact zero with zero variance is the shape of a plumbing failure, so it was
tested three ways: the two arms' CSVs share a **sha256**, zero of 150 000 rows
differ, and a permissive slot that restored two rows compares
**content-identical** to its baseline slot across all 300 pair files. Then the
wiring: the mutated `heavyOriginC` **is** read downstream at the trigger
selection, which tests `triggerOrigin != Origin::kSelectedHard` — exactly the
value the restoration writes.

**So the zero is an EXPOSURE statement, not a mechanism one.** MONASH restored
62 rows in 10 M events, and each must still pass central + ground-state +
acceptance + pT > 1 before it can add a pair. It should not be read as "the
effect does not exist in MONASH".

---

## THE GUARD (Task 1) — removed, replaced, and the removal verified

The throw is gone. The count is emitted with `contested_seen_charm/beauty`
beside it, so a legitimate zero says *contested rows existed and were declined
for the pre-registered reasons* rather than *the branch never ran*. The
did-it-work assertion moved to `check_campaign_restoration()` in
`analysis/a2_block_shift.py`, where zero across the whole sample is still a
defect. Recorded as **ERROR_RECORD E7**, with the principle stated:

> Provenance answers *"did the right code run"* — per job, by identity, already
> there as `analysis_macro_sha256`. Physics answers *"how much did it find"*,
> and its answer includes zero. **One check must not answer both.**

**The removal is verified, not asserted.** The MONASH re-run promotes **100 of
100**, including the 49 zero-restoration jobs the old guard discarded, and the
restored totals are **identical** to the superseded run — charm 60, beauty 2.
That is the proof the diff is guard-only and never entered a calculation.
`contested_seen` = 124 against 62 restored, so 62 contested rows were declined
by the eligibility filters — the signal the new field exists to make visible.

`tests/test_a2_campaign_restoration.py` holds four cases apart, including the
negative control that a campaign with zero-restoration jobs still passes — a
check that refused whenever it saw a zero job would reproduce the bias.

---

## Task 2 — which path, and why

**Path 2, the full re-run**, not the contingency. The pool had drained (load
2.5, 3 slots matching immediately) and 300 jobs completed in 19 minutes, so
there was no reason to take the two-sha shortcut. **The campaign carries one
sha**, `a4df31e6…`.

Regression first, on one job, exactly as instructed: **PASS** — 300 files, 300
diffs, every one the single allowed `analysis_macro_sha256` field, zero
unexpected.

**Nothing was deleted.** The superseded run is preserved whole at
`a2_runs/permissive_guarded_22120383` (251 promoted slots) and
`a2_runs/regression_guarded_22120383`; the held-job evidence stays at
`a2_runs/held_evidence_20260813`; the pre-patch macro and submit files are kept
beside their replacements. Only the 49 stale **queue entries** of the superseded
cluster were removed, after their outputs and hold reasons were already captured.

---

## Two defects found on the way, both mine, both caught before they mattered

**1. The extraction driver silently kept only the last slot.**
`a2_pair_yield.C`'s `append` argument **defaults to false**, so driving it in a
loop truncates and rewrites the header every call. The CSV would have looked
perfectly well-formed and contained one slot. Caught by noticing the file was
0 bytes when it should have been growing. The driver now passes `append`
explicitly and **asserts** what the bug destroyed: exactly one header line, and
one distinct slot value per requested slot.

**2. The gated analyzer was never in the repository.** `.gitignore`'s
`/Analysis/` rule matched the **source** directory on a case-insensitive
filesystem (`core.ignorecase=true`), and git applies ignore rules only to
untracked paths — so the files added before the restructure kept working and the
trap stayed invisible. `analysis/a2_block_shift.py`, the gated analyzer the
whole A2 pre-registration hangs on, and `analysis/a2_pair_yield.C` had **never
been committed**. Nothing generates a directory by that name; the rule was
stale. Removing it reveals exactly those two files and nothing else.

---

## NOT DONE — the tie-break robustness check, and why it was not improvised

Δ exceeds the negligible threshold, so re-running with the **largest**
`heavyIndex` winner instead of the smallest is warranted, to show the
multiplicity trend is not an artefact of the tie-break direction.

**It was not started, deliberately.** It needs a decision I should not make at
the end of a session:

> `analysis/a2_block_shift.py` pins **one** `EXPECTED_VARIATION_SHA256` and its
> gate comment says, correctly, that there is *"deliberately no `--force` and no
> `--skip-gate`"*. A second legitimate variation needs the gate to know about
> **two** admissible shas. The right shape is a frozen named **set** of
> variations, each still requiring its own PASS sentinel — not an override flag,
> which is what an end-of-session rush would have produced.

The magnitude bracket (drop-all versus keep-one) does not depend on the
tie-break direction; the **shape** is what the check would confirm. Until it is
run, the multiplicity dependence is reported as measured under one tie-break
direction, and `A2_DELTA_RESULT.md` says so.

---

## Task 4 — the verdict, and the M7 distinction

**The systematic must be quoted per multiplicity class for the CR tunes and is
negligible for MONASH.** `STATE.md` row 8 and `docs/M7_UNRESOLVED_SYSTEMATIC.md`
now carry it, together with the exposure comparison that settles the
relationship between the two documents:

| | pair-level restorations / M events | inclusive unresolved rate |
|---|---|---|
| MONASH | 6.2 | reference |
| JUNCTIONS | 1 219.4 | — |
| CLOSEPACKING | 1 228.7 | — |
| **CR / MONASH** | **≈ 197×** | **13.6×** |

**A restoration count is not Δ**, and both documents say so in those words. But
the *tune dependence* is like-for-like, and it is an order of magnitude larger
at pair level. **The inclusive diagnostic was never a proxy for the pair-level
systematic** — they do not even scale together across tunes, which is exactly
what review finding A2 claimed.

---

## Next session

1. **The tie-break robustness check**, starting with the gate-design decision
   above. Everything else for it is in place.
2. JUNCTIONS blocks were 4/10 at session start; the two-tune plotting figure
   unblocks when the merge finishes.
3. CLOSEPACKING remains unmerged, so the three-tune harvest is still out.
