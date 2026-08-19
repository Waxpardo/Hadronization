# Three closures launched, three tunes extracted, the table staged — 2026-08-15 (seventeenth session)

**Suite 45/45** (44 + one added). Wall clock 22:06–22:45 CEST. `stbc-i3` up
**2 d 22 h 59 m**, boot 2026-08-12 23:07 — no reboot since. Merge PID `315689`
alive at **1 d 07 h 24 m**, supervisor `316182` alive, both untouched.

> **Headline: the closures for JUNCTIONS and CLOSEPACKING are running in
> parallel and will not land in this window (~12–15 h, ETA midday 2026-08-16).
> Everything that does not need them is finished** — both tunes extracted,
> integrity run, both conventions tabled, the b-baryon advisory computed. **The
> harvest is staged in `docs/THREE_TUNE_CENTRAL_TABLE.md`, marked ⛔ PROVISIONAL
> throughout. No number was promoted.**

---

## 1. Task 0 — the supervisor cannot tell completion from death. Answer recorded, guard installed.

**Read from `tools/merge_supervisor.sh` directly.** It detects the merge by
process presence — `merge_pid()` is `pgrep -f "merge_root_files.sh ${FREEZE}"`
— and **nothing downstream of that distinguishes an exit 0 from a crash.** On
absence it runs the five pre-checks and restarts if they pass.

**On a cleanly completed merge every one of those pre-checks passes**: the
checkout is tracked-clean, HEAD is at `43e35be8`, the reflog is unmoved, the
manifest sha matches, CVMFS python3 executes. **So it would restart a finished
merge into another 12 h 42 m preamble, up to `MAX_RESTARTS=6`.** Its
fail-closed design is right for deaths and simply has no concept of completion.

**The brief's condition — stop it when the merge exits cleanly, not before — is
not something this session could execute**, because the merge has ~45 h of
sequential closure left and is still guarding it. So the condition was
installed rather than performed: `tools/supervisor_eol_watch.sh`, deployed to
`a2_tools/` (sha `ac847c09…`, **byte-identical to the committed copy**), running
as **PID 2566164**.

**Its trigger is race-free, and that was the design point.** A poll that waits
for the merge to disappear has to beat the supervisor's 120 s poll — winnable
but a race. Instead it watches for `CANONICAL_PAIR_BLOCK_CLOSURE_PASS
tune=CLOSEPACKING`, which is **the last statement in `merge_root_files.sh`**
(its closure loop runs MONASH, JUNCTIONS, CLOSEPACKING and the file ends there).
Once that line is printed the merge has done all its work, so stopping the
supervisor is correct whether the merge then exits 0 or is killed.

**If the merge disappears WITHOUT that marker it does nothing at all** and says
so in its log — that is the death case the supervisor exists for, and it is left
alone.

**Six controls verified before launch**, in the shadow of last session's two
self-match traps:

| control | result |
|---|---|
| newest-log resolution | `merge_v6.log` — the live one |
| marker absent in **every** merge log now | 0 hits (and 0 for any tune) |
| `is_sup(316182)` | TRUE — would signal |
| `is_sup(315689)`, the merge | FALSE — correctly refuses a non-supervisor |
| merge alive | yes |
| supervisor restarts so far | **0** — a clean negative control since Aug 14 14:42 |

It identifies its target by **explicit PID plus a re-read of `/proc/PID/cmdline`**
(PID reuse), never by a pattern scan that could match its own command line.

## 2. Task 1 — both closures launched, in parallel, in 4 minutes

Not waiting for the merge's own sequential pass, per the brief. The **strong
invocation**, matching the merge's rather than the chains' `-1`:

```
Validation/validate_pair_block_closure.sh \
  complete_root_HF_RUN3_V1_<TUNE> \
  SUBSAMPLES_HF_RUN3_V1/combined_root_subSamples_<TUNE> \
  100000000
```

against the **frozen checkout's** wrapper (`/data/alice/ipardoza/Hadronization`,
still `43e35be8`, tracked-clean).

| tune | wrapper PID | ROOT worker | log |
|---|---|---|---|
| **JUNCTIONS** | **2563461** | 2563693 | `closure_runs/closure_HF_RUN3_V1_JUNCTIONS_20260815_220840.log` |
| **CLOSEPACKING** | **2563536** | 2563740 | `closure_runs/closure_HF_RUN3_V1_CLOSEPACKING_20260815_220842.log` |

Plus the merge's own MONASH pass (PID 2539259, started 21:48). **Three closures
on the node, load ~6–9, all three reading steadily** — 33 MB/min each against a
~29 GB workload, so **ETA ~12:45–13:15 CEST 2026-08-16**. Measured on the worker
by `rchar` and open-fd position, never atime.

**The stale `combined_root_4.partial.l6K9h4` cannot be touched by any of this,
and that was checked rather than assumed:** `ValidatePairBlockClosure.C:239`
builds block paths as `base + "/combined_root_" + to_string(block)` for
`block = 1..10`, so the partial is unreachable by name. Its mtime is unchanged
at Aug 12 22:52.

**A waiter records each verdict when it lands** (`closure_runs/closure_waiter.sh`,
PID 2572403). The launches are detached, so no shell holds their exit status;
the waiter writes the exit time and the `PAIR_BLOCK_CLOSURE` summary line, or
records that no summary line was reached. **It does not rule on the verdict** —
that is `harvest_tune.py --stage closure`.

### On A4's missing argument

`docs/PER_TUNE_PROCESSING_PREREGISTRATION.md` step 1 calls the expected-schema
argument mandatory. **It does not exist on Nikhef** — the frozen wrapper takes
`CENTRAL BLOCK_BASE [EXPECTED_CENTRAL_EVENTS]`, and A4's fix is local-only
because the checkout cannot advance while the merge reads it. **Verification is
therefore by reading the emitted `analysis_schema=` value against the
pre-registration, and it was checked that way deliberately.** That is precisely
the enforcement `extraction/pipeline/harvest_tune.py`'s `closure_verdict()` was
written to provide, as its own docstring records.

*(A small correction for future briefs: the harvest driver is at
`extraction/pipeline/harvest_tune.py`, not `tools/`.)*

## 3. Task 2 — 22 directories extracted, integrity run, everything PROVISIONAL

`docs/THREE_TUNE_CENTRAL_TABLE.md` holds the tables. Summary of what was
established:

**The instrument is the MONASH instrument.** All four artefact shas — extractor
`4cd8b6fa…`, ordinals `ccec0dbc…`, registry `ea9b0232…`, map v2 `58081aa2…` —
are identical to `MONASH_CENTRAL_TABLE.md` §0's provenance, and the extraction
went through `run_extract.sh` with `--registry` present.

**Two controls on it, both passed:**

1. **MONASH re-run reproduces its committed table to the last digit** —
   structural and experiment-comparable, I3 exact at 53,662,416, I2 0 flags. So
   MONASH's column is *reused* with its reuse corroborated, not assumed.
2. **JUNCTIONS central re-extracted byte-identical** to the independent
   2026-08-13 extraction (`cmp` clean on both CSVs), two days apart into a
   different run root.

**Every directory reports the deduplication:** all 22 carry
`beauty [26]x, charm [24]x` and `SELF_CHECK AGREE worst_relative=0.000e+00` —
the sum rule at 1e-9, met exactly.

**Per-event plausibility on all 33 counts:** MONASH 0.5366, JUNCTIONS 0.4631,
CLOSEPACKING 0.4668, every block within 0.0005 of its central. Nothing within an
order of magnitude of the replicated 12.9866.

**I3 exact for all three tunes**, bin by bin.

### I2 flagged, for the first time since the recalibration — 4 flags, both reported

The pre-registration says *"any flag at all is notable; two or more is a
finding."* **Neither tune was downgraded with `--i2-advisory`; the tool exits 4
for both and that is what is recorded.**

**JUNCTIONS, 3 flags — all in a category MONASH could not test.** Every flag is
a doubly-heavy baryon in `kMultiplyHeavy`. MONASH holds **8 entries in 3
ordinals** there and contributes **0 of its 88 testable bins**; JUNCTIONS holds
**20,935 in 29** and contributes **12 of 116**. All three flags land in that
12-bin subset — probability **(12/116)³ ≈ 1.1 × 10⁻³** if flags fell uniformly.
And that subset's dispersion is genuinely different: observed block scatter ÷
binomial σ is **1.60** for kMultiplyHeavy against **0.98–1.11** for the other
three categories, while I2's MAD null estimates **one** pooled σ̂ of 1.12.
Rescaled to their own subpopulation the flags are **|z| ≈ 2.5–2.7**.

> **Stated with its limit, because this project has made the opposite mistake.**
> That a pooled single-σ̂ null is misspecified for a subpopulation is *measured*.
> **Why** kMultiplyHeavy is overdispersed is not: event-clustered doubly-heavy
> production is the natural reading, but with 12 species and 10 blocks each
> ratio carries ~24 % uncertainty and the low/high split is 2 species against
> 10 — **too thin to claim magnitude dependence.** E6 is the standing warning
> against reading a scale factor as physics, and it applies here.

**CLOSEPACKING, 1 flag, and a different shape.** Σ*_c⁺ (`kExcludedExcited`,
308,901 entries, 0.66 % of total) reads 2.3 % low in block_2 at z = −4.28.
**Isolated in both directions:** its conjugate in the same block is +1.16, the
block's total sits mid-pack among the ten, and the next largest pull anywhere in
block_2 is +2.54. Setting kMultiplyHeavy aside, this is **1 flag in ~2,960
comparisons against ~0.19 expected (p ≈ 0.17)**. **E4's defect was 30 of 88 bins
displaced together; one isolated bin does not resemble it.**

**Materiality — jackknifed.** Dropping the flagged blocks moves no structural
row by more than **1.19 SEM** or **0.0056 pp**. Real enough to report, too small
to matter to the table.

### The sanity read the brief asked for — and the category split understates it

**Baryon share of total pair weight: MONASH 4.6093 ± 0.0028 → JUNCTIONS
16.5586 ± 0.0041.** More than tripled.

kCentralGround rises 52.4959 → 58.2318, a net **+5.74 pp** — but that net figure
is two much larger opposing moves, because **kCentralGround holds both baryons
and mesons**:

| component (% of total) | MONASH | JUNCTIONS | Δ |
|---|---|---|---|
| kCentralGround / **baryon** | 3.5997 | 14.7313 | **+11.13** |
| kCentralGround / meson | 48.8962 | 43.5006 | −5.40 |
| kExcludedVector / meson | 46.4946 | 39.9409 | −6.55 |
| kExcludedExcited / **baryon** | 1.0095 | 1.7821 | +0.77 |

**Baryons gain +11.95 pp and mesons lose exactly that.** The
kCentralGround/kExcludedVector shift is real, but the mechanism is only legible
once kCentralGround is split. **The tune-bundle confound stands unchanged** — 28
allowed differences across nine families, only 8 of them CR — so none of this is
attributable to junction formation alone.

## 4. The b-baryon advisory reverses its own pre-registration

Step 2 of the ladder in `docs/B_BARYON_ADVISORY_DIAGNOSTIC.md` §2, which that
document records as blocked on exactly this output. Loose pre-registration:
**CR ≥ MONASH**. Result: **0 of 13 weighted b-baryon species, in both CR tunes.**

**MONASH — the tune with no CR and no junctions — carries the asymmetry**
(Σ_b 1.59–1.64, Ξ'_b 1.76–1.78, tens of SEM from unity). **Both CR tunes are
consistent with symmetric** (0.98–1.05), on 10–20× the statistics.

That document had already noted the asymmetry "does not require the junction
transport mechanism". With three tunes it is sharper: **the CR tunes wash it
out.** The confound applies with full force — "the CR *tunes* do not show it" is
established; "CR removes it" is not.

**Advisory only, gates nothing, and PROVISIONAL until both closures return.**

## 5. What was committed

| | |
|---|---|
| `docs/THREE_TUNE_CENTRAL_TABLE.md` | the staged harvest, ⛔ PROVISIONAL throughout |
| `extraction/three_tune_table.py` | both conventions on a **common row set** — each tune's own top-8 differs, so three top-8 lists are not comparable |
| `extraction/bbaryon_tune_advisory.py` | the per-tune advisory, raw weights, no map |
| `tools/supervisor_eol_watch.sh` | Task 0's guard, sha-identical to the deployed copy |
| `tests/test_three_tune_tables.py` | **45th test** — both new tools pinned against the committed MONASH anchor |

The test pins two things that are easy to "fix" into errors: that the structural
table **is** a partition summing to 100 %, that the experiment-comparable table
**is not** and must not be normalised into one, and that the advisory's exit
status stays 0 even on MONASH's 1.59 ratios.

## 6. Boundaries respected

Merge and supervisor untouched. Checkout unmoved at `43e35be8`, tracked-clean,
pin intact. The stale partial untouched. No pinfile removal, no checkout
advance, no `Paper/**`, no disk cleanup. The merge's redundant closure passes
were left running as harmless confirmation.

## 7. For the next session

1. **The verdicts.** `closure_runs/verdict_line_{JUNCTIONS,CLOSEPACKING}.txt` and
   `closure_waiter.log` will hold them. Run
   `extraction/pipeline/harvest_tune.py <TUNE> --stage closure --closure-log <log>`
   — do not eyeball the counts. **A FAIL stops that tune**, reported verbatim.
2. **Both PASS → promote `THREE_TUNE_CENTRAL_TABLE.md`**: strike the ⛔, mark the
   two columns FINAL. No number needs recomputing; they are measured and staged.
3. **The owner's ruling on the I2 flags** (§3). The numbers do not move, but
   "two or more is a finding" is a standing commitment and this is the first
   time it has fired. A category-aware null is the obvious follow-up and is
   **not** a change to make quietly.
4. **The supervisor's end of life is handled** — but if the node reboots, the
   watcher and both closures die with it and **the closures have no supervisor**.
   The merge does. Relaunch them by hand from §2's invocation.
