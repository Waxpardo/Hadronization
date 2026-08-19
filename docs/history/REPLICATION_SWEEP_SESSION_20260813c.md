# The replication-inflation sweep — 2026-08-13 (third session that day)

**The harvest was blocked again, and for a reason worth writing down: the merge
never got past its own validation preamble.** So the session did Task 3 in full,
which turned out to be the one that mattered — three recorded findings collapsed
into a single arithmetic mistake.

**One commit, `3f6f523..645154f`. Suite 37/37.** No tune advanced.

---

## 0. STATE AT OPEN

| | |
|---|---|
| wall clock | **2026-08-13 12:45 CEST** |
| `stbc-i3` uptime | **13:40** — same boot as the previous two sessions, **no new reboot** |
| merge | **ALIVE**, restarted 07:24, **still inside `validate_analysis_outputs.py`** |
| promotions | **0 new** (15 of 33 carried from the killed v3 run) |

**A connectivity note worth keeping.** The direct `stbc` alias failed on
*banner exchange* while `login.nikhef.nl` was fine and `stbc-i3` answered ping
and ssh from inside Nikhef. It was a transient ProxyJump failure and cleared on
retry (3/3). **A failed hop is not a dead node** — check the jump host and the
target separately before concluding anything.

---

## 1. THE MERGE — a restart cost nobody had measured

The validation preamble has now run **5 h 40 m** and is not close to done.

**The position probe that works.** `validate_analysis_outputs.py` forks
`validate_pair_directory.sh` **per job slot**, so the child's argv names the
current slot. That is the real progress metric — `rchar` on the parent is frozen
by construction, and `rchar` on the worker is inflated ~4× by ROOT's
basket-level re-reads (368 GB read against 88 GB of data), so it cannot be read
as a fraction of the job.

| time | slot |
|---|---|
| 12:48:56 | `JUNCTIONS/slot_243` |
| 12:52:30 | `JUNCTIONS/slot_254` |
| 13:04:41 | `JUNCTIONS/slot_306` |

**≈ 4.3 slots/min recent, 3.8 slots/min lifetime.** Manifest order is
MONASH-first, so position ≈ **1306 of 3000**; **~1700 slots ≈ 7 h remain**, ending
**~19:40–20:30 CEST**. The rate has degraded from the early run — the node now
carries **15 users at load 4.2**, where it was quiet at 07:24.

> **This ~13 h preamble is paid on EVERY restart.** `merge_root_files.sh:81-84`
> runs the validator unconditionally and rewrites its report; a valid report from
> a previous run is not consulted. Combined with the reboot cadence (Jul 8 /
> Jul 16 / Aug 12 at ~23:0x), a restart is far from free even though the merge
> itself resumes per directory. **Not changed here** — the checkout is frozen and
> the merge is reading it live — but it is the single cheapest thing to fix once
> the checkout can move.

### Revised completion estimate, including a phase nobody has costed

| phase | estimate |
|---|---|
| validation preamble | ends **~20:00 Aug 13** |
| re-validate the 15 promoted legs | ~2 h |
| **18 remaining merge legs** at ~2.68 h/leg | **~48 h** → **~22:00 Aug 15** |
| **the merge's own closure, all three tunes** | **~45 h** → **~19:00 Aug 17** |

**The closure phase is the new number.** `merge_root_files.sh:202-224` runs
closure for all three tunes *after* all merging, and MONASH's own closure took
**~14.9 h** (inputs complete 02:55:57, outputs written 17:47 on Aug 12). Three
of those is ~45 h. **The previously circulated "~2026-08-15" is the end of
*merging*, not the end of the run.**

One consolation: in this arrangement closure no longer overlaps merging, so the
self-contention that caused the band MISS does not recur.

---

## 2. E6 — three findings, one arithmetic mistake

**Task 3 delivered in full.** The unification is recorded as `ERROR_RECORD.md`
**E6**.

Multiplying every count by **R** leaves fractions and fractional deviations
**exactly** unchanged but scales a binomial pull by **√R**. Measured **5.03×**
(replicated blocks 4.800 ± 0.519, deduplicated 0.955 ± 0.096); predicted
**√24.2 = 4.92**.

| recorded as | recorded cause | actual cause |
|---|---|---|
| **E4** — anchor "bin-inconsistent", 30 of 88 at \|z\| > 4 | a corrupt/unprovenanced extraction | real 1/10 subsets give **32–40**; the anchor's 30 is **below** the range |
| **I2's 353 flags in 880** | a "misspecified null" | √R. Deduplicated, I2 gives **0 in 10** |
| **"~4.75× overdispersion from event clustering"** | pair counts are event-clustered | **there is no overdispersion**; blocks sit at 0.955 ± 0.096 |

### The evidence was already on the page

`MONASH_CENTRAL_TABLE.md` §3 records "observed block scatter ÷ binomial σ —
**median 5.06, mean 5.00**", which is √R to two figures, and directly beneath it
"**high vs low count: 4.99 vs 5.06 — flat**".

**That flatness is the tell.** A uniform multiplicative factor is
magnitude-independent; event clustering is not — it scales with how many pairs
an event contributes and would vary across species populations by construction.
The measurement said *constant* and the prose read it as *a property of pair
counting*. **A mechanism that explains your artifact is not evidence for the
mechanism.**

### Withdrawn, and what does not move

- ⛔ **"Poisson/binomial errors on these fractions are ~5× too small"** —
  withdrawn. True only of replicated data. On deduplicated output those errors
  are **correct as computed**.
- ⛔ **"I2 will flag on every tune"** — withdrawn with it.
- ✅ **No published number moves.** The quoted uncertainties are **empirical
  block SEMs**, which measure dispersion instead of assuming it — correct under
  the replication and correct without it. The re-extracted table confirms it:
  SEMs unchanged to four decimals.
- ✅ **The E4 quarantine still stands** on non-statistical grounds: the anchor is
  unprovenanced, and its result was contradicted by traceable data.

### It closes yesterday's open question

I left E4 with a hypothesis — "a significance computed on replicated counts is
inflated ~5×, which would turn a ~1.5 σ fluctuation into a 7.4 σ claim… that is
a hypothesis, not a finding". **7.4 ÷ 5.03 = 1.47.** Reached independently.
**E4 and E5 are one defect seen twice**, and the "may be" is now "is".

---

## 3. Σ_b — what stands and what is now unresolved

Per owner ruling, recorded at the head of
`SIGMA_B_ORDERING_AND_ADJUDICATION.md`:

- ✅ **R1 (spin-sorted) and R2 (forward growth) STAND** — measured on **raw
  generator records**, no analysis chain. The physics conclusion is unaffected.
- ⛔ **The charge-ordering question is UNRESOLVED.** *Both* readings used to
  settle it are null after deflation: the anchor's **−7.2 σ MISS → −1.43 σ** and
  the merged central's **+5.1 σ HIT → +1.01 σ**. The Task 1 retraction stands,
  but because **neither dataset resolves the ordering** — not because the merged
  central confirmed the prediction.
- ✅ **Σ*_b +3.2 σ at 1000 files** is raw-count and unaffected.
- **No further investigation.**

---

## 4. THE SWEEP — annotated, and cleared

One pass over every tracked `.md` outside `docs/history/`. **Annotated beside
the original, never rewritten, never re-derived:**
`SIGMA_B_ORDERING_AND_ADJUDICATION` (six values),
`B_BARYON_ADVISORY_DIAGNOSTIC` §3 (the whole σ column),
`ERROR_RECORD` E4, `anchors/extraction_dual/MANIFEST`, and
`MONASH_CENTRAL_TABLE` §3 (the withdrawal).

**Recorded as CLEARED, so nobody re-opens them:**
`PRODUCTION_SHAPE_DECISION` and `RELEASE_BLOCKERS` (⟨N_ch⟩ from six 200 k-event
generator runs — no extraction, no replication), R1/R2/R3-at-400-files, Σ*_b at
1000 files, and **every block SEM in the project**.

---

## 5. NOT DELIVERED

- **No tune was harvested.** JUNCTIONS is still central + blocks 1–3;
  CLOSEPACKING still has nothing. **No closure verdict is possible for either.**
- **The three-tune table does not exist**, for the third session running. MONASH's
  re-extracted values remain authoritative and were reused, not re-run.
- **The b-baryon asymmetry advisory table** needs three tunes. Not produced.
- **Idle-waiting was declined**, per the brief.

---

## 6. FOR THE NEXT SESSION

1. **Time and uptime first**, then the **slot probe**, not `rchar`:
   `pgrep -P <validator-pid> -a` names the job slot it is on. 3000 slots total,
   MONASH first.
2. **Do not restart the merge unless it is actually dead** — the ~13 h
   validation preamble is the price, and it is paid in full every time.
3. **Closure comes free with the merge** for all three tunes, with the stronger
   `expected_central_events=100000000`. Budget **~15 h per tune** and read the
   verdicts from
   `hadronization_analysis/HF_RUN3_V1/validation/pair_block_closure_*.log`
   against the 2100/1500 pre-registration. The schema argument (A4) is
   local-only; verify by reading the emitted `analysis_schema`.
4. **Extraction is safe by construction** — `bash tune_extract.sh TUNE`. Confirm
   the manifest header shows `map_v2_sha` and `registry_sha`, and that each
   directory logs `charm [24]x, beauty [26]x`.
5. **Realistic completion is ~2026-08-17**, not the 15th, once the closure phase
   is counted.
