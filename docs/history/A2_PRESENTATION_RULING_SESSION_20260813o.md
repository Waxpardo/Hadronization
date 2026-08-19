# A2: the presentation ruling applied; JUNCTIONS not yet harvestable — 2026-08-13 (fifteenth session)

**Suite 44/44, unchanged.** Wall clock 21:48–22:00 CEST — a short session,
because the one thing that could have made it long was not ready. `stbc-i3` up
**22 h 41 m**, no reboot; the merge driver `430646` is the same process
throughout, now 14 h 33 m old.

---

## Task 1 — the presentation ruling, applied

**Quote the LARGEST-index arm, per multiplicity class.** Per cent, block SEMs:

| tune | M1 | M2 | M3 | M4 | M5 |
|---|---|---|---|---|---|
| MONASH | 0.0004 | 0.0011 | −0.0003 | 0.0017 | 0.0037 — **negligible** |
| **JUNCTIONS** | 0.0255 | 0.0691 | 0.1007 | **0.1509** | 0.1369 |
| **CLOSEPACKING** | 0.0377 | 0.1012 | 0.1571 | 0.1777 | **0.2293** |

Four things changed in how this is written down, in every document that carries
it (`STATE.md` row 8, `M7_UNRESOLVED_SYSTEMATIC.md`,
`A2_PAIR_UNRESOLVED_RUN_RECORD.md`, `A2_DELTA_RESULT.md`,
`A2_TIEBREAK_ROBUSTNESS.md` §4, and the pre-registration annotation):

1. **The shape leads.** The 5.9–9.7× rise across classes holds under *both*
   rules, and that is what makes per-class quoting mandatory rather than
   stylistic — an integrated number is wrong about the shape whichever rule is
   chosen. It is stated before any magnitude.
2. **The smallest-index arm is the cross-check**, whose job is to establish
   **rule dependence** (2.0–5.5×, all ten CR classes, 2.7–21.6 σ). It is not a
   lower bound.
3. **"Envelope" is gone.** The wording is now *"the larger of two extremal
   orderings of `heavyIndex`"*, and every document states explicitly that
   **neither ordering bounds the space of resolutions**: a pT-ordered rule would
   give more, which is exactly why the pre-registration rejected it as inflating
   the shift by construction. That rejection **still stands** — what was
   falsified is the claim that `heavyIndex` avoids the problem, not the claim
   that pT ordering has it.
4. **The falsified assumption is recorded as a METHOD FINDING**, promoted to its
   own section rather than left as a scoring footnote. The pre-registration
   chose smallest-index on an explicit reasoned argument; identical restoration
   counts with 2–5× different Δ falsify it. **The registered text stays
   unedited**; the marked annotation beside it carries the correction.

> The transferable form: **a tie-break defended as neutral is an empirical claim
> about the data, and it is cheap to check by running the other direction.**
> Within a single arm the choice is invisible.

**Out of scope, per the brief and not pursued:** a physics-motivated tie-break
(momentum matching or similar). It would be a better method, not a better bound,
and the worst-class value is 0.229 %.

---

## Task 2 — the probe-method addition

`docs/PROGRESS_PROBE_METHOD.md` gains **correction 6**, beside the atime
lessons, because it is the same failure on a different tool:

> `git ls-files --others --ignored --exclude-standard` does not descend into a
> **wholly-ignored** directory. So the natural sweep command is blind to
> precisely the failure mode it would be reached for, and — like correction 3 —
> it fails as a **quiet, well-formed, reassuring answer** rather than an error.
> Test directories directly with `git check-ignore -v`.

With the corollary that makes the trap durable: git applies ignore rules **only
to untracked paths**, so once any file in the directory is committed the rule
stops applying and every symptom disappears, while **the trap stays armed for
the next new file**. This is documented against the evidence from the guard
test — when the original defect was reinstated, the tracked-file check *passed*
and only the case-collision check fired.

---

## Task 3 — JUNCTIONS is NOT harvestable. Nothing was manufactured.

Read from the filesystem, not from `condor_q` (my queue is empty, which means
only that the A2 campaigns are done):

| tune | central | blocks promoted | harvestable |
|---|---|---|---|
| MONASH | ✅ | **10/10** | already harvested (previous session) |
| JUNCTIONS | ✅ | **3/10** | **no** |
| CLOSEPACKING | ✗ absent | 0/10 | no — and out of scope |

The merge is alive and progressing, but is still re-validating **MONASH block 4
of 10** — it restarted at 07:24 as `merge_v4`, and `merge_one` re-validates every
existing directory before doing new work. Four phases complete in v4 after
14 h 33 m. Remaining before JUNCTIONS reaches 10/10: 7 MONASH blocks, JUNCTIONS
central (~77 min), 3 JUNCTIONS re-validations, then **7 fresh block merges** →
still **~6–9 h**, unchanged from last session's estimate because only 12 minutes
of wall clock have passed. Closure is a further ~15 h after that.

**The orphaned `combined_root_4.partial.l6K9h4` was not touched.** It still holds
all 304 files. Promoting it by hand would bypass the validation that promotion
exists to enforce.

> One counting note worth keeping: `ls combined_root_[0-9]*` **matches the
> partial too** (`4.partial.l6K9h4` satisfies `[0-9]*`) and reports 4 promoted
> blocks where there are 3. Count with an exact-name test per block.

---

## Next session

1. **JUNCTIONS** when the merge reaches 10/10 — closure directly, then
   `harvest_tune.py`.
2. Nothing else is pending on A2. Task 1 closed it.
