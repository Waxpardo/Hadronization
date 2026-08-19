# The full-scale v3 merge — pre-registration

`merge_root_files.sh`, unmodified, consuming the gate's report. **GO is in force
conditional on the gate returning PASS.** Recorded before launch.

> ## ⚠ ANNOTATION 2026-08-11 — READ THIS BEFORE ACTING ON §5
>
> **§5 below still carries, in bold, "⛔ THE MERGE MUST NOT BE LAUNCHED ON THIS
> PLAN". That escalation is WITHDRAWN IN FULL** eighty lines further down, in
> the n=300 correction. **The settled number is 65–77 h against the 96 h
> ceiling: it FITS, with 19–31 h of margin.**
>
> **The gate returned `status=PASS directories=3000 missing=0`, and the merge
> launched 2026-08-10 22:32 CEST.**
>
> The withdrawn conclusion is left in place on purpose, because the error is the
> lesson: it was built from a **prefix** of an ordered workload, and every prefix
> of this workload over-estimates monotonically — the per-file mean falls
> 35.9 → 8.8 s across a single block. **But a cold reader grepping this file for
> a blocker meets the retracted one first, and two sessions running have come
> close to acting on it.**
>
> **Rule: in this file, check for a withdrawal before acting on any escalation.**

---

## 1. THE SHAPE — 33 merges, and 30 of them are the same size

From `merge_root_files.sh:186-195`, per tune: one **central** over
`canonical_inputs_per_tune`, then ten **blocks** over
`canonical_inputs_per_block` (`:51`, `= inputs/10`).

| | count | inputs each |
|---|---|---|
| centrals | **3** (one per tune) | **1000** |
| blocks | **30** (ten per tune) | **100** |
| **total `merge_one()` calls** | **33** | |

**The 100-input block is the most-repeated operation in the merge**, and the v3
scaling curve stopped at 50. That is why the anchor exists.

---

## 2. THE BASIS, AND ITS WEAKNESS STATED

v3 measured, `per-elementary = wall / (300 × (N−1))`:

| N | wall | per-elem | n | host |
|---|---|---|---|---|
| 10 | 45.01 s | 16.67 ms | **n=1** | login |
| 25 | 135.10 s | 18.76 ms | **n=1** | login |
| 50 | 1591.88 s | **108.29 ms** | **n=1** | batch |

**Every point is n=1.** Under the standing early-sample caveat these bands quote
that, and they are wide because of it. The 10/25 re-run (`5399189`) is
**indicative-only** — node isolation was not guaranteed — and does not narrow
them.

**The extrapolation is not monotone, and v2 is the reason to doubt it.** v2's
per-elementary *fell* from 50 to 100 inputs — 306.0 → 217.2 ms, a ratio of
**0.71**. The step is a transition, not an exponent (v8 §2a). So a v3 block at
100 inputs may cost *less* per elementary merge than the 50-input point, not
more. **Three scenarios, carried rather than collapsed:**

| scenario | per-elem @100 | block wall | central wall @1000 |
|---|---|---|---|
| v2-like recovery (×0.71) | 70 ms | **34.6 min** | 5.83 h |
| flat at the 50 value | 108.29 ms | **53.6 min** | 9.02 h |
| continued rise | 150 ms | **74.2 min** | 12.49 h |

---

## 3. PRE-REGISTRATION

| # | prediction |
|---|---|
| **M1** | **Block (N=100) wall in 2100–4500 s** (35–75 min). Point estimate **~3200 s** at the flat rate; the anchor tests exactly this. |
| **M2** | **Central (N=1000) wall in 5.5–13 h.** Point estimate **~9 h**. |
| **M3** | **The 32 h per-process ceiling is not approached.** It would need **384.4 ms** per elementary merge at N=1000; the largest v3 value measured is **108.29 ms**. **Headroom 3.55×.** Comfortable is the expected answer and this is the number. |
| **M4** | **Merge-side child RSS ~760 MiB at N=100 and ~1.2 GiB at N=1000.** *Growth, not flatness* — see below. |
| **M5** | **Total merge wall 56–109 h** — the 33 merges (35–76 h) **plus the gate, which the script runs itself** (21–33 h). See §3b. At the flat rate ~**80 h**. |
| **M6** | Closure counts **2100 / 1500**, per `docs/CLOSURE_V3_PREREGISTRATION.md`. |

### 3b. ⚠ THE MERGE RUNS THE GATE ITSELF — and that may breach the retirement ceiling

**`merge_root_files.sh:80-83` runs `validate_analysis_outputs.py` as its first
step**, writing to `${analysis_root}/validation/analysis_output_manifest_validation.json`.
This is B10's point restated (`RELEASE_BLOCKERS.md:742-746`): the serial
checksum gate is on the merge path, not merely near it.

**Three consequences, none of them optional:**

1. **The standalone gate run (`5399180`) is a precondition check, not a
   substitute.** It writes to `gate_runs/gate_3000_report.json` — a *different
   path* — so the merge will not find it and will not skip its own. **The gate
   cost is paid twice: once to earn GO, once inside the merge.**
2. **That duplication is deliberate and worth its price.** Discovering a gate
   failure after 35–76 h of merging would be far more expensive than the
   21–33 h spent proving it first. But it should be *named* as a cost, not
   absorbed silently.
3. **The total may not fit.** Workers advertise `MaxJobRetirementTime = 345600`
   — **4 days = 96 h**. The merge's expected total is **56–109 h**. The optimistic
   and central cases fit; **the pessimistic case does not**, and the central
   case (~80 h) leaves only ~16 h of margin against an extrapolation whose every
   point is n=1.

> **This is an owner decision, not a successor's improvisation.** The options
> are visible — accept the risk, split the merge across invocations, or shorten
> the path — but two of those touch the production script, which is unmodified
> by standing rule. **Flagged before launch rather than discovered at hour 96.**
> The 100-input anchor is the cheapest thing that narrows the band, which is a
> second reason to have run it.

### Why M4 says growth rather than flatness

Measured v3 RSS: **470.2 MiB @10, 535.9 @25, 657.0 @50.** Fitting a power law
across the decade, `RSS ∝ N^a` gives **a = 0.208** — strongly sub-linear but not
flat. Extrapolated: **759 MiB @100, 1226 MiB @1000.**

**The mechanism argues for saturation below that.** What grows is the union of
*filled* `THnSparse` bins across merged inputs. As inputs accumulate, new files
increasingly fill bins that are already occupied, so the union grows toward the
support of the distribution rather than with N. **So the power-law figure is an
upper bound**, and the true N=1000 value should land under 1.2 GiB — plausibly
near 0.9–1.0 GiB. Either way it is comfortable against a batch node, and
`request_memory = 8GB` carries ≥6× headroom on the worst case.

**This is the merge-side figure, and it is not the gate's.** The gate's
`ValidatePairDirectory` measures **442.3 MiB ± 0.9 %** and is a different
program; conflating them was an error already recorded once and is not repeated
here.

---

## 4. LAUNCH CONDITIONS

- **Gate PASS is a precondition.** `status=PASS directories=3000 missing=0`.
  Any failure ⇒ item-STOP, failing directories enumerated, **the merge does not
  run.**
- Detached, PIDs and sentinel recorded, **outputs and logs retained
  unconditionally**.
- **The checkout stays frozen while it runs.** The guard and hook enforce this
  on their own — the merge's jobs are in flight and pin the commit. Noted, not
  fought.
- **If a `merge_one()` fails: item-STOP with that directory's stage retained.**
  Promoted inputs are untouched by design — `merge_one()` reads them and writes
  elsewhere.

---

## 5. ACTUALS — ⚠ THE ANCHOR INVERTS M3, AND THE MERGE DOES NOT FIT

**Status: projection at n=21 of 300, anchor `5399458` still running.** Recorded
now because the consequence is an owner decision, not because the number is
final.

The rate is **flat**, which is why n=21 is being acted on: deltas over the last
21 files have mean **35.9 s** and median **36.0 s**, against 35.0 s at n=3.
**It is not accelerating** — and the 50-input run did (11.8–14.7 s/file opening,
5.31 s/file final average). Under the standing caveat, n ≥ 10 revises the band
on record, so:

| | registered | **projected (n=21)** | |
|---|---|---|---|
| **M1** block wall @100 | 2100–4500 s | **~10,757 s ≈ 3.0 h** | **MISS, high by 2.4×** |
| per-elementary @100 | — | **362.2 ms** | vs 108.29 ms at N=50 |

### The 50→100 step goes the opposite way from v2

| N | v3 per-elem | v2 per-elem | v3/v2 |
|---|---|---|---|
| 50 | 108.29 ms | 306.0 ms | **0.354** |
| 100 | **362.2 ms** | 217.2 ms | **1.668** |

**v3 rises by 3.34× across 50→100; v2 *fell* by 0.71.** The v3/v2 ratio
**crosses over between 50 and 100 inputs** — v3 is cheaper at 50 and **more
expensive at 100**.

> **This does not breach the standing merge-strategy escalation**, which is
> `ratio ≥ 10` — 1.67 is far below it. **It breaks something else: the wall-clock
> budget.** Two different criteria, and last session's "no escalation" verdict
> remains true on its own terms while ceasing to be reassuring.

### M3 inverts: the 32 h per-process ceiling is now marginal

| | registered | **projected** |
|---|---|---|
| central wall @1000 (flat per-elem) | ~9 h | **30.15 h** |
| headroom vs 32 h ceiling | **3.55×** | **1.06×** |

**M3 said "the ceiling is not approached." It is now approached to within 6 %** —
and that assumes per-elementary stays *flat* from 100 to 1000, which is the one
thing the 50→100 step says it does not do. **If the rise continues at all, the
worst central breaches the per-process ceiling.**

### The total does not fit, by more than 2×

```
30 blocks  × 2.99 h =  89.6 h
 3 centrals × 30.15 h =  90.5 h
                        ------
 merges                 180.1 h
 + gate (run internally)  21-33 h
                        ------
 TOTAL                  201-213 h      against a 96 h site ceiling
```

> ## ⛔ THE MERGE MUST NOT BE LAUNCHED ON THIS PLAN
>
> Not "it is tight". **Roughly 2.1–2.2× over the ceiling**, with a per-process
> ceiling that is simultaneously marginal. §1's flag was that ~80 h left ~16 h of
> margin; the anchor says the real figure is ~200 h.
>
> **This is an owner decision with the numbers, and the options all touch things
> a successor may not touch alone:** split the merge across invocations, skip the
> internally-run gate, reduce block count, or change the merge strategy. **M6's
> closure counts and the gate's PASS are unaffected — this is purely a
> wall-clock feasibility finding.**

**Confirm against the anchor's final `SCALE` line before acting.** If the run
accelerates in its second half after all, these numbers fall and the conclusion
softens — but 21 flat files is not what acceleration looks like.

### CORRECTION at n=95 — the escalation stands, my magnitudes were too pessimistic

The n=21 figures above came from an early window and **overstated the cost by
~29 %**. At **n=95 of 300**, measured over the whole run rather than a window:

| | n=21 (published) | **n=95 (corrected)** |
|---|---|---|
| mean s/file | 35.9 | **25.5** |
| block wall @100 | ~10,757 s (2.99 h) | **~7,637 s (2.12 h)** |
| per-elementary @100 | 362.2 ms | **257.1 ms** |
| central @1000 (flat) | 30.15 h | **21.41 h** |
| headroom vs 32 h | 1.06× | **1.49×** |
| merge total + gate | 201–213 h | **149–161 h** |

**The per-file rate is not monotone and never was.** Quartile means across the
95 files: **36.0, 15.4, 10.3, 38.7 s.** It is *variable* — fast in the middle,
slow at both ends — not a cold-cache warmup that decays. Any window, early or
late, misprojects; only the running total is honest.

**What survives unchanged:**

- **M1 still misses high** — 7,637 s against a 2100–4500 s band, by 1.7× rather
  than 2.4×.
- **M3 is still inverted** — 1.49× headroom against a registered 3.55×, and the
  1.49× assumes per-elementary goes flat from 100 to 1000, which the 50→100
  step (still a **2.37× rise**) says it does not.
- **The merge still does not fit** — **149–161 h against a 96 h ceiling, ~1.6×
  over.** The decision is unchanged; only its size is.

**What was wrong:** the "2.1–2.2× over" and "headroom 1.06×" figures reported
before this correction. They were drawn from a 21-file early window, which is
the same error the standing caveat names — and this time it ran *pessimistic*,
which is the direction that manufactures false alarms rather than false comfort.
**The caveat should say "any small window", not "early samples".**

### FINAL — the anchor completed, and BOTH my escalations were WRONG

```
SCALE tune=MONASH inputs=100 rc=0 time_v=[2643.18 2530.70 33.24 836384] RETAINED
300/300 pair files, 20:42:30 → 21:26:34
```

| | registered | n=21 (my alarm) | n=95 (my correction) | **FINAL** | |
|---|---|---|---|---|---|
| **M1** block @100 | 2100–4500 s | 10,757 | 7,637 | **2643.18 s** | **HIT** |
| per-elem @100 | — | 362.2 ms | 257.1 ms | **88.99 ms** | |
| 50→100 factor | — | "3.34× rise" | "2.37× rise" | **0.82 — a FALL** | |
| v3/v2 @100 | — | "1.668, crossover" | — | **0.410, no crossover** | |
| **M3** central @1000 | 3.55× headroom | 1.06× | 1.49× | **4.32×** | **HOLDS** |
| **M5** total | 56–109 h | 201–213 h | 149–161 h | **65–77 h** | **FITS** |
| **M4** RSS @100 | ~760 MiB | — | — | **816.8 MiB** | ~7 % high |

**M1, M3, M4 and M5 all hold. There is no ceiling problem. The merge fits with
19–31 h of margin.** §5's escalation above is **withdrawn in full** — it is left
in place because the error is the lesson.

**Every claim I made from partial data was false:** per-elementary does not rise
across 50→100, it **falls** (0.82), the same direction v2 went (0.71); the v3/v2
ratio does not cross over, it stays at **0.410**; M3 does not invert, it comes in
**better than registered**.

### Why partial projections failed so badly here

The per-file cost is **extremely front-loaded**. Running mean by file count:

| n | mean s/file | implied 300-file wall |
|---|---|---|
| 21 | 35.9 | 10,757 s |
| 95 | 25.5 | 7,637 s |
| 255 | 10.1 | 3,039 s |
| **300 (actual)** | **8.8** | **2,643 s** |

Files 96–255 averaged **~1.1 s** against the first 95's **25.5 s** — a ~24×
spread *within one run*. The pair files are written in a deterministic order and
differ enormously in content, so the expensive ones come first. **No partial
window is representative, and the error is systematically pessimistic** — every
projection over-estimated, monotonically, until the run was essentially over.

> **The standing caveat, corrected again and now with a mechanism:** it is not
> "early samples run slow" and not merely "any small window". It is that **this
> workload's unit cost is ordered, not random**, so a prefix is a biased sample
> by construction. **For any `merge_one()`-shaped measurement, only the final
> `SCALE` line counts.** Report progress if asked; do not project from it, and
> above all do not escalate from it.

---

## 6. RESUME PROTOCOL — read from the script, before launch

**Required pre-flight.** A ~3-day single job will meet a node reboot, an
eviction, or a network blip sooner or later. This is what
`merge_root_files.sh` does on re-run, read from the source rather than assumed.

### It is safely resumable, and it is fail-closed

`merge_one()` opens with an existence check (`:94-106`):

| state of `final_directory` | behaviour |
|---|---|
| **exists and validates** — `validate_pair_directory.sh` (with `expected_inputs` **and** `manifest_sha`) **and** `merged_pair_provenance.py validate` both pass | prints **`VALIDATED_EXISTING_MERGE`**, `return 0`. **Skipped. This is the resume path.** |
| **exists and fails either check** | `ERROR: existing merge directory is stale/invalid; refusing overwrite`, `return 4` |
| **absent** | merges into `mktemp -d "${final_directory}.partial.XXXXXX"` |

**`set -euo pipefail` (`:2`)**, and the driver loop (`:186-196`) does not test
`merge_one`'s status — so **any non-zero return aborts the whole run**. Failures
propagate; they are not skipped. Return codes: **4** stale/invalid or bad
manifest, **5** merge failed (non-zero status, or `CANONICAL_MERGE_SUMMARY` not
exactly once, or `CANONICAL_MERGE_ERROR`/segv/JIT-error in the log), **6** final
directory appeared before promotion.

**Promotion is atomic and doubly validated** (`:167-183`): validate stage → write
provenance → validate stage again → validate provenance → assert final still
absent → `mv` → `PROMOTED_MERGE`.

**Every failure path retains its stage.** `ERROR: … retained stage ${stage}`.

### So the resume procedure is: re-run the same command. Nothing else.

Completed directories are skipped by validation, not by a marker file, so a
half-written directory cannot be mistaken for a finished one.

### Three consequences worth knowing before hour 50

1. **Every resume pays the internal gate again.** `:80-83` runs
   `validate_analysis_outputs.py` unconditionally at the top, before any
   `merge_one`. **A resume therefore costs 21–33 h before it reaches the first
   unmerged directory.** This is the single most important resume fact.
2. **Abandoned stages accumulate.** `mktemp -d` makes a *new* stage each run; the
   interrupted one is never cleaned. They land beside the final directories in
   `hadronization_merged/`, **not** in the gate's `per_job` scan root, so they do
   **not** block the gate — but they consume disk (below).
3. **A corrupt directory stops everything, by design.** Return 4 refuses to
   overwrite. That is correct — but it means a single bad directory blocks the
   run until a human looks at it. **That is an item-STOP, not a script edit.**

### Disk budget

Measured merged output scales close to linearly in inputs — **943 MB @50,
1.8 GB @100** (1.91× for a doubling), so the sparse content is **not** saturated
at 100.

| | count | each | total |
|---|---|---|---|
| blocks @100 | 30 | 1.8 GB | **54 GB** |
| centrals @1000 | 3 | 10–18 GB | **30–54 GB** |
| | | **total** | **84–108 GB** |

`/data/alice` holds **1.1 TB free at 97 % used**. 108 GB is ~10 % of free space —
**fits**, but the filesystem has moved from 1.6 TB free to 1.1 TB since
`docs/WORKSPACE.md` recorded it, so check `df` before launching. Each abandoned
stage from an interruption adds up to another central's worth.

### Invocation target

Prior campaigns wrote to **`/data/alice/ipardoza/hadronization_merged/`**
(`complete_root_HF_PT2_*`, `SUBSAMPLES_HF_PT2_INT`), **not** the checkout's
`AnalyzedData/` — which holds thesis-era output and must not receive ~100 GB
inside a git checkout. Use `hadronization_merged` with tag `HF_RUN3_V1`.
