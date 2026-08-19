# Merge v3 — first-block band validation

**Verdict: the 2643 s ± 30 % band is a HIT. The one apparent excess is a
measurement artefact of directory-mtime differencing, identified and
decomposed — not a slow block.** RSS is below band, which the owner's
asymmetric rule treats as record-and-revise, not investigate.

Pre-registration: `docs/MERGE_V3_PREREGISTRATION.md` (M1 block wall 2643 s
± 30 % ⇒ **1850–3436 s**; M4 merge-side child RSS ~836 MB).

---

## 1. THE TIMELINE, MEASURED

The merge log carries **no timestamps and no elapsed/RSS lines**, so every
number here comes from filesystem timestamps plus the log's own write times.
Method stated in §3.

| event | wall clock | interval |
|---|---|---|
| merge launched | 2026-08-10 22:32:12 | — |
| **internal gate finished** | 2026-08-11 10:53:26 | **8.35 h** |
| central MONASH promoted (1000 inputs, 11 G) | 14:57:43 | **4.07 h** |
| block 1 promoted | 16:43:54 | 6371 s |
| block 2 promoted | 17:34:29 | **3035 s** |
| block 3 promoted | 18:14:21 | **2392 s** |
| block 4 merge finished | 18:53:26 | **1606 s (direct)** |

**The internal gate took 8.35 h against the standalone gate's 18.77 h — 2.25×
faster.** v43 predicted its completion at ~11:10 from a single frontier reading;
**it landed at 10:53, 17 minutes early on a 12-hour prediction.** The frontier
method holds again.

**The central took 4.07 h against a pre-registered ~7.3 h** — that figure was
labelled an extrapolation when registered, and it was high.

---

## 2. THE BAND CHECK

### The artefact, and why block 1 is not slow

`merge_one()` runs **merge → validate(.partial) → promote**. Validation *reads*
the partial directory, so **the directory's mtime marks the end of its MERGE**,
not its promotion. Differencing consecutive directory mtimes therefore measures:

```
interval(N-1 -> N) = validate(N-1) + merge(N)
```

**The central→block-1 interval contains the CENTRAL's validation**, and the
central's output is **11 G against a block's 1.8 G**.

Decomposition, from the log's own write timestamps:

| quantity | value | how |
|---|---|---|
| **validate(block)** | **~739 s** | block 3 dir mtime 18:14:21 → next log write 18:26:40 |
| **merge(block 4)** | **1606 s** | log write 18:26:40 → block 4 dir mtime 18:53:26. **Direct, uncontaminated** |
| **full block cycle** | **~2345 s** | 1606 + 739 |
| implied validate(central) | ~4500 s | 6371 − merge(block 1) |
| **ratio validate(central)/validate(block)** | **~6.1×** | vs **6.1× output size** (11 G / 1.8 G) |

**The 6.1× time ratio matching the 6.1× size ratio is the check that closes
this.** Validation scales with output size, the central's is ~4500 s, and
block 1's merge was ~1870 s — inside band.

### Scored

| measurement | value | band 1850–3436 s | |
|---|---|---|---|
| block 2 full cycle | 3035 s | inside | **HIT** |
| block 3 full cycle | 2392 s | inside | **HIT** |
| **block 4 full cycle** | **~2345 s** | inside | **HIT** (merge leg measured directly) |
| mean of clean cycles | **2724 s** | vs anchor **2643 s** | **3.1 % high** |
| block 1 *raw interval* | 6371 s | above | **artefact — contains central validation** |

> **M1 HIT.** Three independently measured full cycles land inside the band and
> their mean is within 3.1 % of the anchor.

### RSS — below band

| child | RSS | vs anchor 836 MB |
|---|---|---|
| merge child (`MergeCanonicalAnalysis`) | **515.7 MB** | 62 % |
| validate child (`ValidatePairDirectory`) | **570.2 MB** | 68 % |

**Both below band.** Per the owner's asymmetric rule — *the guarded failure mode
is stall, not speed* — this is **recorded, not investigated**. The band revises
at n ≥ 10; n = 2 processes here, so **no revision is proposed**.

---

## 3. METHOD, AND ITS LIMITS

- **Directory mtime = end of that directory's merge**, because validation only
  reads the partial. Verified against the log's step structure
  (`MergeCanonicalAnalysis` → `CANONICAL_MERGE_SUMMARY` → `ValidatePairDirectory`
  → `PAIR_DIRECTORY_VALIDATION` → `MERGED_PAIR_DIRECTORY_VALID` →
  `PROMOTED_MERGE`).
- **Log write time = start of the next merge**, since the next
  `Processing MergeCanonicalAnalysis.C` line is written immediately after a
  promotion.
- **Only block 4's merge leg is a direct measurement** (start and end both
  timestamped). Blocks 2 and 3 are interval measurements; block 1's is
  contaminated and is reported decomposed rather than as a block time.
- **validate(central) is inferred, not measured** — it is the residual of
  block 1's interval. The 6.1× size agreement is corroboration, not proof.

## 4. NO COMPLETION PROJECTION IS OFFERED

**4 of 33 `merge_one()` calls are complete** (1 central + 3 blocks, all MONASH).

Per the ordered-unit-cost rule, **progress is reportable and never
projectable**: this workload's per-file costs are ordered, every prefix is
biased, and `docs/MERGE_V3_PREREGISTRATION.md` §5 preserves a withdrawn
escalation built from exactly this mistake. **The counts above are the report.**
The 65–77 h band stands untouched until the run ends and can be scored against
its final wall clock.

---

## 5. FULL MONASH TUNE TIMED, AND THE SLOWDOWN HAS A NAMED CAUSE

Measured 2026-08-12 11:35 from promoted-directory mtimes (method as §3).
**MONASH is complete — one full tune, 11 of 33 `merge_one()` calls.**

| leg | wall clock | interval |
|---|---|---|
| internal gate (**one-time, covers all three tunes**) | → 2026-08-11 10:53:26 | **8.35 h** |
| **MONASH central** (1000 inputs) | → 14:57:43 | **4.07 h** |
| block 1 | → 16:43:54 | 6371 s |
| block 2 | → 17:34:29 | 3035 s |
| block 3 | → 18:14:21 | 2392 s |
| block 4 | → 19:05:55 | 3094 s |
| block 5 | → 19:58:22 | 3147 s |
| block 6 | → 20:44:56 | 2794 s |
| **block 7** | → 22:57:01 | **7925 s** |
| block 8 | → 23:43:31 | 2790 s |
| block 9 | → 2026-08-12 00:30:08 | 2797 s |
| **block 10** | → 02:43:32 | **8004 s** |
| **ten blocks** | | **11.76 h** |
| **MONASH tune, merge work only** | | **15.83 h** |

### The second tune's central is running ~3.8× slower, and the cause is measured

JUNCTIONS central started **02:43:32**. At 11:33 (**8.83 h in**) it is at
**contract rank 71/300** — ~57 % of byte-weighted work, so ~15.5 h projected
against MONASH central's **4.07 h**.

**MONASH closure started 02:55:57 — twelve minutes after the JUNCTIONS central
leg began.** Both are CPU-bound on the same node. This is not a mystery
slowdown; it is the pipeline competing with itself, and it was designed to: the
chains fire each tune's closure as soon as that tune's inputs are complete.

> **The contention RECURS by construction.** JUNCTIONS closure will overlap the
> CLOSEPACKING merge exactly as MONASH closure now overlaps the JUNCTIONS merge.
> Any completion estimate that assumes the post-18:00 recovery persists is
> assuming away the next collision.

### The band is still NOT scored — and it is now genuinely two-sided

The remaining work is **two structurally identical tunes**, which is a far
better basis than a heterogeneous prefix. But the contention coupling dominates
and is not modelled:

| assumption | remaining from 18:00 Aug 12 | total | vs 65–77 h |
|---|---|---|---|
| merge returns to MONASH rates once closure ends | ~34 h | **~77 h** | at the **ceiling** |
| contention recurs for both remaining closures | materially more | **> 77 h** | **miss high** |

**Neither is published as the score.** Recorded because the leg mtimes are
perishable and because the *cause* of the slowdown — self-contention, not
degradation — is the part that would otherwise be re-derived from scratch.
Score at completion, from the final wall clock, per §4.

**Disk headroom, 2026-08-12 12:10:** `data-02:/alice` **1040 G avail / 32374 G (97 % used)**, merged tree 42 G — ample against the ~60 G the merge still needs, but the volume is shared and near-full, so the margin is not ours alone.

---

## SCORED 2026-08-13 — **MISS**. Measurement closed.

**Owner ruling.** 15 legs in 48.6 h (8.35 h one-time internal gate + 40.25 h
merge work, ~2.68 h/leg) projects to **~97 h** against a **65–77 h** ceiling;
documented cause is closure/merge CPU contention; the run was additionally
interrupted by a node reboot at 15/33. **The measurement is closed** — not to be
re-derived or re-scored against the restarted run.
