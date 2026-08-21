# M7 beauty — pre-registration

**Written and committed BEFORE the macro was deployed or any job submitted.**
Recorded so the result is scored against a statement that could not have been
tuned to it.

Closes the gap named in the dated private generational handoff, Sections 2.2 and 6.2: the
unresolved-origin systematic exists for **charm only**, because
`Validation/MeasureUnresolvedSystematic.C` cut on `heavyQc`. The paper's
beauty-baryon story therefore carries no equivalent systematic.

---

## 1. WHAT IS BEING MEASURED

Identical question, other sector. Per tune: the rate at which beauty candidates
are dropped as `kUnresolved`, the baryon fraction of the dropped sample against
the kept one, and the relative shift in the measured baryon fraction that
dropping them causes. The shift is the systematic to quote.

Sector selection is now an argument, default `"c"`. Beauty uses `heavyQb` and
`heavyOriginB` — **verified to exist as tree branches**, and the same pair the
production analysis reads (`analysis/status_analysis_THnSparse_qq.C:410-412`).

---

## 2. THE PRE-REGISTRATION — STRUCTURE ONLY

**Per the recorded authorization, no numeric prediction is made.** Charm's
values are not a prior for beauty: the sectors differ in production
cross-section, in hadronisation, and in how often ancestry is ambiguous. Stating
a number would be inventing one.

**Registered expectations, all structural:**

| # | expectation | reasoning |
|---|---|---|
| **B1** | **unresolved RATE: JUNCTIONS and CLOSEPACKING ≫ MONASH** | colour reconnection rearranges colour flow, so ancestry is ambiguous far more often in the CR tunes. This is the mechanism, and it is sector-independent |
| **B2** | **relative SHIFT: JUNCTIONS and CLOSEPACKING ≫ MONASH** | follows from B1 given B3 |
| **B3** | **the unresolved sample is baryon-ENRICHED in all three tunes** (enrichment > 1) | charm showed 1.45–1.53× with little tune dependence; the enrichment mechanism is not charm-specific |
| **B4** | **beauty resolved_n ≪ charm resolved_n**, so per-block counts are smaller and **block SEMs are relatively larger** | beauty production cross-section is far below charm at this energy |

**"≫" is deliberately not given a threshold.** For charm the CR/MONASH rate
ratio was ~13.6×; requiring a specific factor for beauty would smuggle in the
numeric prediction the authorization excludes.

### What would count as a finding rather than a failure

**If MONASH ≫ CR, that is a finding — it gets reported, not rationalised.** It
would say the CR-driven ambiguity mechanism does not carry from charm to beauty,
which is itself worth the paper knowing. The same applies to B3 failing: a
baryon-*depleted* unresolved sample would invert the sign of the systematic.

**No result here is a reason to re-run with different cuts.** The cuts are the
production cuts.

---

## 3. SIZING, WITH ITS n

| | |
|---|---|
| charm anchor | **3.32 s/file, n=1**, 284,680 kB maxRSS |
| beauty expectation | **comparable per file** — same tree, same four `TTree::Draw` calls, same file. Not obviously faster despite lower beauty multiplicity, because the cost is dominated by the scan, not the selected count |
| per job | 300 files ⇒ **~17 min**, n=1 basis |
| total | 10 jobs ⇒ **~2.8 h CPU**; wall much shorter if slots are free |

**Sizing quotes n=1 and is not a band.** Per the standing rule, it revises on
record at n ≥ 10 — the ten block jobs will themselves supply that n.

---

## 4. POSITIVE CHECKS THAT MUST PASS BEFORE ANY NUMBER IS BELIEVED

`rc=0` is not evidence. Six invocation failures in this project's history were
all of the "looked fine, wasn't" kind.

| # | check | why it is the right check |
|---|---|---|
| **P1** | **charm regression:** the parametrised macro at `sector="c"` reproduces the **frozen** charm-only macro's output on the same file, field for field | proves the parametrisation changed nothing for charm. This is the strongest single check available, because the old program still exists to compare against |
| **P2** | **aggregator regression:** the modified `extraction/aggregate_m7.py` reproduces the **published charm table** from the existing block logs — 0.0847 / 1.1530 / 1.1355 % and shifts 0.0451 / 0.5497 / 0.5125 % | proves the `sector` handling did not disturb charm |
| **P3** | **beauty is non-empty and distinct:** `resolved_n > 0` for all three tunes, and beauty counts differ from charm counts on the same file | a sector argument that silently fell through to charm would otherwise publish charm numbers under a beauty label |
| **P4** | **per-block cross-check:** the counts macro and the percentage macro agree on one file per tune per block, or the block aborts | the existing M7 mechanism, unchanged |
| **P5** | **n=10 or nothing:** the aggregator fail-closes below ten blocks | a partial set gives a SEM over the wrong n |

**P1 and P2 are regressions against programs that already exist. P3 is the one
that catches the specific failure this change could introduce.**

---

## 5. EXECUTION CONSTRAINTS

- **The frozen checkout is not touched.** The gate (cluster `5399423`) pins it
  and `make can-advance` refuses; that is correct. Macros deploy to scratch
  under `/data/alice/ipardoza/m7b_runs/`, read-only against the checkout.
- **`Requirements = (Machine != "wn-sate-072.nikhef.nl")` is retained**, keeping
  these jobs off the gate's node — the reason charm M7 ran concurrently with the
  gate without incident.
- **No seeds are burned.** This reads existing raw files.
