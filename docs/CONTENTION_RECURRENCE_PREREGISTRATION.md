# Pre-registration — the closure/merge collision will recur on CLOSEPACKING

> ## ⛔ SUPERSEDED 2026-08-12 — NEVER SCORED
>
> Registered while the JUNCTIONS central merge was running. It predicted a
> **scheduling** effect, gated no number, and the pivot to freeze ended
> operational forecasting. **Marked, not deleted: a prediction registered in
> advance is a record even when it is never scored.**

**Written 2026-08-12 11:40 CEST, while the JUNCTIONS central merge is still
running and the JUNCTIONS chain has NOT fired.** Registered in advance so the
65–77 h band's eventual score can cite a cause that was documented before the
evidence arrived, rather than one fitted to it afterwards.

Loose band, **structure-only**. This predicts a *scheduling* effect, not physics.
Nothing here gates any number, and per the owner's ruling **nothing is
intervened on** — the collision costs wall clock, not correctness.

---

## 1. THE STRUCTURE THAT MAKES IT RECUR

Each tune's chain fires that tune's closure the moment that tune's inputs are
complete. The merge, meanwhile, moves straight on to the next tune's central.
**So every tune boundary is a collision point, by construction:**

| tune boundary | merge is doing | a chain is doing | observed |
|---|---|---|---|
| MONASH → JUNCTIONS | JUNCTIONS **central** | **MONASH closure** | **happened** (§2) |
| JUNCTIONS → CLOSEPACKING | CLOSEPACKING **central** | **JUNCTIONS closure** | **predicted** (§3) |

Both are CPU-bound on the same node. This is a design property of the pipeline,
not a fault in it, and it is queued for the restructure phase.

## 2. THE OBSERVED CASE — the reference measurement

| | |
|---|---|
| MONASH central, **uncontended by any closure** | **4.07 h** |
| JUNCTIONS central start | 02:43:32 |
| MONASH closure start | **02:55:57** (12 min later) |
| JUNCTIONS central at 11:33 | 8.83 h elapsed, contract rank **71/300** (~57 % byte-weighted) |
| implied JUNCTIONS central total | ~15.5 h ⇒ **~3.8× MONASH central** |

**The reference is not clean, and that is why the band below is loose.** Blocks
7 and 10 ran 7925 s and 8004 s against a ~2800 s norm **with no closure running
at all**, so this node carries contention from at least one other source. A
factor measured here is our collision *plus* whatever else the node is doing.

## 3. THE PREDICTION

**Observable:** wall-clock duration of the **CLOSEPACKING central** merge leg,
from promoted-directory mtimes (method of `MERGE_V3_BAND_VALIDATION.md` §3).

**Reference:** MONASH central, **4.07 h**.

| | |
|---|---|
| **P1 (primary)** | CLOSEPACKING central ≥ **2×** MONASH central (**≥ 8.1 h**) |
| **P2 (loose band)** | CLOSEPACKING central falls in **2–6×** ⇒ **8.1–24.4 h** |
| **P3 (corroborating)** | JUNCTIONS central, when it completes, lands in the same 2–6× band |

**Direction is the claim; the factor is not.** A pre-registration that only
predicted "slower" would be nearly unfalsifiable, so P1 commits to a floor.

## 4. APPLICABILITY CONDITION — check this BEFORE scoring

**The test applies only if JUNCTIONS closure is actually running concurrently
for ≥ 50 % of the CLOSEPACKING central leg.** Verify from the closure process's
own start and end, not from the assumption that the chain fired on time.

> **If the overlap is under 50 %, the test is VOID — not passed and not failed.**
> Record it as void and say why. The most likely way this happens is the
> JUNCTIONS chain aborting (`TUNE_CHAIN_ABORTED`) so that no closure ever runs
> against the CLOSEPACKING merge.

## 5. WHAT FALSIFIES IT

**P1 is falsified if CLOSEPACKING central completes in < 8.1 h while the
applicability condition holds.** That would mean the MONASH→JUNCTIONS slowdown
was driven by something other than our own collision — most plausibly the other
user's load — and the contention story in `MERGE_V3_BAND_VALIDATION.md` §5 would
need withdrawing, not softening.

**P2 is falsified high** if it exceeds 6×, which would say the collision cost is
worse than the observed case and that the two-sided band in §5 was still too
optimistic.

## 6. WHEN IT IS SCORED

At CLOSEPACKING central promotion — **before** the full merge completes, since
this is a per-leg observable. Score it in the same pass that scores the 65–77 h
band, and state the applicability check explicitly either way.

**No projection of the merge's completion is offered here, and this
pre-registration must not be used to build one.** The ordered-unit-cost rule
stands: per-leg factors do not compose into a finish time.
