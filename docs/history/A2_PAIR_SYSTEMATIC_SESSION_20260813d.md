# A2 — the pair-level unresolved systematic: built and submitted, not measured

**2026-08-13 (fourth session that day).** **Two commits, `7148cc2..e9b6733`,
suite 37/37.**

**No number was produced, and the reason is scheduling, not physics.** The
measurement is pre-registered, the variation is built and deployed, and 301
Condor jobs are queued. The pool held **~87,400 idle jobs against ~4,800
running**, and every one of the 301 was still `Idle` at session end.

---

## 0. STATE AT OPEN AND CLOSE

| | open 13:27 | close 13:49 |
|---|---|---|
| `stbc-i3` uptime | 14:20, same boot | unchanged, **no reboot** |
| merge | alive, validator 6h03m, `JUNCTIONS/slot_389` | alive, 6h24m, `slot_464` |
| promotions | 0 | 0 |

The merge is advancing at ~4.2 slots/min, consistent with the previous session's
measurement. **Checked twice and otherwise left alone**, as instructed.

---

## 1. THE FINDING THAT MADE THE SESSION POSSIBLE

Origin resolution happens in the **producer**, not the analysis. The obvious
reading is that varying the rule means regenerating the entire campaign — which
would be weeks.

**It does not.** The producer snapshots `originalMatchedHard` *before*
`EnforceUniqueFinalHardCarrier` and writes it into `heavyRejectedHard{C,B}` for
exactly the rows it demotes
(`generation/producer/heavyflavourcorrelations_status.cpp:1215-1239`). **The raw
record states, per hadron, which hard quark it contested** — precisely and only
what a permissive tie-break needs.

So the measurement is a **re-analysis of existing raw files**: 300 jobs, no
regeneration, and the baseline is the committed `per_job` output, not re-run.

---

## 2. WHAT WAS PRE-REGISTERED (committed `6a56572`, before anything was built)

`docs/A2_PAIR_UNRESOLVED_PREREGISTRATION.md`. The parts that constrain the
result:

- **The rule.** Group demoted rows by the hard index they contested; restore
  **exactly one** per group. Restricted to `|sectorCharge| == 1`, because
  `RejectFinalMultiHeavyCarrier` rejects multi-heavy carriers for an
  **independent** reason and restoring those would measure a different variation
  than the one declared.
- **The winner is the smallest `heavyIndex`, deliberately not the highest pT.**
  A pT-ordered tie-break preferentially restores hadrons that pass the trigger pT
  cut, which would inflate the measured shift *by construction*.
- **Scope.** Slots 000–099 × 3 tunes; blocks by `canonical_slot % 10`, matching
  the project's canonical FILE/JOB blocking; SEM dof 9.
- **Expectations, stated so they can be wrong:** Δ ≥ 0 (the rule can only add
  triggers, so a negative Δ beyond 2 SEM is a STOP, not a result); Δ at or below
  the inclusive unresolved rate (~0.09 % MONASH, ~1.2 % CR); CR ≫ MONASH;
  and **Δ rising with multiplicity**, since duplicate-carrier claims come from
  dense-string configurations. **A flat Δ is called out in advance as a real
  outcome that would retire A2's concern.**
- **Three verdict thresholds** — negligible / quotable as one number / must be
  quoted per class — fixed before measuring, with the falsification statement
  for each.

---

## 3. THE VARIATION, AS BUILT

121 lines against the **frozen production macro** `a101a0a1`, all gated on
`HF_A2_PERMISSIVE=1`.

**It was built from the frozen macro, not the local repo copy**, which differs;
building from the wrong base would have confounded the origin-rule change with
unrelated drift. The scratch tree is `git archive` of the **production commit**
`61fe978f`, not HEAD `43e35be8` — the two turn out to be identical across the
relevant directories, which is only knowable because it was checked.

**Every insertion is anchored on a verbatim string and the patch aborts if an
anchor is not found exactly once.** That check paid immediately: the branch
declaration block appears **twice** — once in the contract validator (`tree->`)
and once in the event loop (`chain.`) — and the first attempt matched both and
refused. *A patch that silently no-ops is how a "variation" becomes a re-run of
the baseline.*

**Two self-checks are built in, both able to fail:**

- The rule restores exactly one row per contested index, so **hard-carrier
  uniqueness is preserved** and the production `throw` on
  `sameHardConstituentPairs` remains a **live** check against the variation
  rather than being disabled by it.
- A `throw` if **nothing** was restored — a silent zero would make every
  measured shift trivially zero and look like a clean null.

---

## 4. SUBMISSION, AND ONE JUDGEMENT CALL

| | |
|---|---|
| **regression** | cluster **`5478114`** — 1 job, rule **OFF** |
| **permissive** | cluster **`5478127`** — 300 jobs, rule **ON** |

Ids taken from the `condor_submit` output captured with `tee`, never recovered
by `tail`.

**The 300 were submitted alongside the regression rather than after it.** The
pre-registration makes the regression a gate, and serializing would have been
the letter of it — but with ~87,400 jobs already queued ahead, serializing would
have guaranteed that nothing ran at all. **Queuing is not using.** The gate is
preserved as a rule on *consumption*: **no permissive output may be used until
the regression passes.** Recorded here and in the run record so the next session
inherits the constraint rather than the convenience.

**On byte-identity.** The macro embeds `analysis_macro_sha256` from the
environment (`:1258`), so a modified macro **cannot** be literally byte-identical
to the baseline. The regression check is therefore: **every object identical
except that one named string.** A single explainable metadata difference — not a
tolerance and not a waiver.

---

## 5. WHAT WAS NOT DELIVERED

- **No measured shift, per class or otherwise.** The regression gate is
  unsatisfied and no job has run.
- **The analysis tooling has never seen real variation output.**
  `analysis/a2_pair_yield.C` and `analysis/a2_block_shift.py` are written,
  syntax- and CLI-checked only. `a2_pair_yield.C` deliberately does **not** know
  OS from SS — the signed registry join happens in Python and fails closed on an
  unknown filename — so a mislabelled file cannot be silently absorbed into a
  difference.
- **The three-tune harvest** remains blocked on the merge and was not touched.

---

## 6. FOR THE NEXT SESSION

1. `condor_q 5478114 5478127`. `max_retries = 0` with `on_exit_hold` on non-zero
   exit, so **held jobs mean a real failure**, not a retry-able blip.
2. **Regression first, always.** Compare
   `a2_runs/regression/MONASH/slot_000` against `per_job/MONASH/slot_000`
   expecting exactly one difference (`analysis_macro_sha256`). If anything else
   differs, **stop** — nothing downstream is usable.
3. Confirm `A2_PERMISSIVE restored_charm=… restored_beauty=…` is non-zero in the
   job logs and record the counts per tune. That is pre-registered positive
   check 2, and it is the difference between a real null and an inert variation.
4. Then `a2_pair_yield.C` over baseline and permissive slots, then
   `a2_block_shift.py`, and record the verdict it prints — the thresholds are
   already fixed, so the verdict is mechanical.
5. Full detail, including everything needed to resume without this session:
   `docs/A2_PAIR_UNRESOLVED_RUN_RECORD.md`.
