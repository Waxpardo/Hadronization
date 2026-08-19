# A2: the tie-break check runs, and it breaks the magnitude — 2026-08-13 (fourteenth session)

**Suite 43/43 → 44/44.** Wall clock 20:15–21:45 CEST. `stbc-i3` up 21 h 11 m at
session start — no reboot, so the merge that had been running since 07:24 was
the same process throughout. **The Condor pool had re-filled to ~74 000 idle
jobs** (it was drained last session); the 300-job campaign still completed in
**13 minutes**.

---

## THE RESULT — the shape survives, the magnitude does not

The pre-registration picks the winner of a contested hard index by **smallest**
`heavyIndex`. Δ exceeded the negligible threshold, so the robustness clause
fires: run the opposite direction.

> **The multiplicity dependence is REAL and survives the flip. Its SIZE does
> not: the largest-index arm is 2.0–5.5× larger in all ten CR classes, at
> 2.7–21.6 σ.**

**Shape (each arm normalised to its own M1) — robust:**

| tune | arm | M1 | M2 | M3 | M4 | M5 | rise |
|---|---|---|---|---|---|---|---|
| JUNCTIONS | smallest | 1.00 | 3.54 | 4.49 | 5.17 | 9.68 | **9.7×** |
| JUNCTIONS | largest | 1.00 | 2.71 | 3.95 | 5.92 | 5.37 | **5.9×** |
| CLOSEPACKING | smallest | 1.00 | 2.24 | 3.72 | 6.27 | 4.29 | **6.3×** |
| CLOSEPACKING | largest | 1.00 | 2.68 | 4.17 | 4.71 | 6.08 | **6.1×** |

**Magnitude — not robust.** JUNCTIONS integrated 0.0194 → **0.0583** (13.2 σ);
CLOSEPACKING 0.0192 → **0.0795** (21.6 σ). Full per-class table, both arms, with
the significance of every difference:
`docs/a2_results_20260813/A2_TIEBREAK_ROBUSTNESS.md`.

### The cause, and it falsifies a pre-registered assumption

**Both arms restore an identical number of rows** — JUNCTIONS 12 016 charm +
178 beauty, CLOSEPACKING 12 114 + 173, MONASH 60 + 2, the same in both. The rule
restores one winner per contested index, so flipping the direction changes
*which* row wins, never *how many*.

> **The entire 2–5.5× difference is therefore how often the winner survives the
> trigger selection.** `heavyIndex` correlates with trigger survival.

The pre-registration chose smallest-index precisely because it believed
otherwise — *"deliberately uncorrelated with pT so the tie-break cannot inflate
the measured shift"* — and called the winner choice *"a sub-leading ambiguity
inside the bracket"*. It is the **dominant** uncertainty on the magnitude,
larger than every block SEM in the measurement.

The pre-registration is **annotated, not edited**: the registered text stands
verbatim with a marked post-hoc block beside it. Writing the reasoning down in
advance is what made it checkable.

### What this retires

- **"No class exceeds 0.07 %"** — RETIRED. Seven of ten CR classes exceed it
  under the other direction; CLOSEPACKING M5 reaches **0.229 %**.
- **"Integrated understates JUNCTIONS' top class by 3.6×"** — amended to 2.6×
  (2.9× CLOSEPACKING). The per-class requirement is unchanged and stronger.
- **MONASH's exact zero** — *explained, not contradicted*. Same 62 restorations,
  different winners, Δ = 0.0006 ± 0.0002 %. Byte-level: the smallest arm's
  `permissive_MONASH.csv` was **sha-identical to its baseline**, which is why Δ
  was exactly 0; the largest arm's differs. **This independently confirms last
  session's claim that the zero was an exposure statement, not a mechanism one.**

**The systematic to quote is the envelope over both directions, per class.**

---

## THE GATE (Task 2's precondition) — a named set, per owner ruling

`EXPECTED_VARIATION_SHA256` becomes `config/a2_variations_v1.json`. The gate now
requires **three** things to agree: the sentinel records a PASS, its sha is
**registered**, and the caller **names** the variation and that name resolves to
the same sha.

> The third requirement is the one that earns its keep. With a *set* rather than
> a single pin, a sentinel left over from the smallest-index arm is still
> registered — so membership alone would wave through a largest-index
> measurement certified by the wrong regression, **and the output would look
> perfect**.

No `--force`, no `--skip-gate`; `--variation` is required. Each arm carries its
**own** sentinel file rather than sharing a path — the name check would catch a
shared-path mixup, but a design whose safe outcome depends on a later check
firing is worse than one where the arms never share a file.

`tests/test_a2_regression_gate.py`: 5 refusal paths → 9, including the
registered-but-WRONG case and a control proving the largest arm passes with its
own sentinel (without which check 6 could be satisfied by a gate that simply
always rejects that name).

**The refactor was verified not to touch the physics**: the smallest arm was
re-run through the new analyzer and reproduces last session's numbers exactly.

---

## Task 1 — the .gitignore sweep: CLEAN, and the guard now exists

Every top-level directory compared against `git ls-files`. **Nothing untracked
that should be tracked; zero findings.** The only ignored files anywhere are
build artifacts (`*_C.so`, `*_C.d`, `*.pcm`), `__pycache__`, and one `.DS_Store`.

**One methodological correction worth keeping.** `git ls-files --others
--ignored --exclude-standard` does **not descend into a wholly-ignored
directory** — it reports the directory only with `--directory`. So the natural
sweep command is blind to exactly the failure mode being swept for. The sweep
was redone by testing **every directory** against `git check-ignore` directly.

`campaigns/` is ignored and lowercase — the same shape as the `/Analysis/` trap
— but holds **zero files** and is a generated output root. Not a finding.

`tests/test_no_source_directory_is_ignored.py`, three checks that fire at
different stages: (A) a directory holding tracked files must not be ignored;
(B) no ignore rule may match a real directory **only under case-folding** — the
trap itself, caught before a file goes missing, and filesystem-independent so it
fails on Linux too; (C) an ignored directory must not hold source unless
declared, catching a directory swallowed whole where A is blind.

**Verified by reintroducing `/Analysis/`:** check B fires and names the rule and
the directory. **Checks A and D still PASS with the bug present** — because the
files are tracked now, git stops applying the rule to them. That is exactly why
the original was invisible, and it is why B is the check that matters.

---

## Task 3 — no tune became harvestable, and this is measured, not assumed

An empty `condor_q` was not treated as evidence. The filesystem says:

| tune | central | blocks | harvestable? |
|---|---|---|---|
| MONASH | ✅ promoted | **10/10** | **already done** — closure PASSED 2100/1500, errors 0; `MONASH_CENTRAL_TABLE.md` §0 is the table of record |
| JUNCTIONS | ✅ promoted | **3/10** | no |
| CLOSEPACKING | not merged | 0/10 | no |

**The merge is alive and progressing** (driver PID `430646`, 13 h 41 m, child at
99.6 % CPU). It **restarted at 07:24** as `merge_v4` and `merge_one` re-validates
every existing directory before doing new work, so it is currently re-walking
MONASH from the top. Measured rates this session:

| phase | measured |
|---|---|
| MONASH central re-validation (1000 inputs) | **77 min** (20:07 → 21:24) |
| a block re-validation (100 inputs) | **~7 min** |
| a fresh block merge (from `merge_v3`) | 28–64 min |

Remaining before JUNCTIONS is at 10/10: 8 MONASH blocks, JUNCTIONS central
(~77 min), 3 JUNCTIONS block re-validations, then **7 fresh block merges** →
**~6–9 hours**, i.e. ~04:00–07:00 on 2026-08-14. Its closure is then a further
~15 h (MONASH's took 14 h 49 m). **Driving a per-tune closure this session was
not possible**, and nothing was waited on in hope.

### Flagged, not acted on

`combined_root_subSamples_JUNCTIONS/combined_root_4.partial.l6K9h4` holds **all
304 files** (written Aug 12 22:40) but was never promoted — `merge_v3` died
between writing and validation. `merge_one` keys off the *final* directory name,
so it will stage a **new** partial and redo that block, leaving the orphan on
disk. **Not touched**: the brief says do not intervene in the merge, and
promoting a directory by hand would bypass the validation that promotion exists
to enforce.

---

## Two defects found and fixed on the way

**1. The tracked submit generator reproduced an already-solved failure.**
`tools/a2_make_subs.py` was committed from the remote copy dated 13:41, which
**predates** the provenance fix made at ~17:27 the same day. Its first submit
died on ExitCode 3: *"analysis worker tree is not a git checkout and no deploy
commit was injected."* `--deploy-commit` is now **required**, not defaulted — an
archived tree has no `.git`, so provenance there is injected rather than
discovered, and omitting it should be a usage error at generation time rather
than a held cluster. This is the *second* time this exact corollary has bitten.

**2. `tools/a2_record_regression.py` imported the constant the gate redesign
removed.** It now resolves the sha **from the registry by name**, so the recorder
cannot mint a sentinel for a macro nobody registered, and it records the
variation name alongside the sha.

---

## Next session

1. **The merge**, which should have JUNCTIONS at 10/10 by early morning. Then
   its closure (~15 h) and `harvest_tune.py`. CLOSEPACKING follows.
2. **Whether the envelope is an extremum.** Smallest and largest bracket the
   `heavyIndex` ordering, but a random-winner rule could sit outside it. Two
   directions are not a distribution, and §6 of the robustness document says so.
3. **Why** later-indexed heavy quarks survive the trigger selection more often.
   Measured here, unexplained; it would need `heavyIndex` against pT and
   ancestry.
