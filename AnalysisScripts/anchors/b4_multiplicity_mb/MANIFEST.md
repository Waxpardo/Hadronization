# Anchor `b4_multiplicity_mb` — per-tune minimum-bias N_ch

**The evidence behind the multiplicity class definition**, and behind figure 3.
Committed 2026-08-13 so the paper-facing translation table can be **recomputed**
rather than transcribed. It previously existed only at
`/data/alice/ipardoza/b4_mapping/out/`, off the repo.

| file | what |
|---|---|
| `nch_mb_<TUNE>.root` | the MB N_ch histogram, `hNch_mb_<TUNE>`, 400 unit bins on `[-0.5, 399.5]` |
| `nch_mb_<TUNE>.csv` | the same, dumped to text so no ROOT is needed downstream |
| `dump_nch.C` | the dumper, committed because the CSVs are derived |
| `run_meta.txt` | the original run's provenance |

| tune | MB events |
|---|---|
| MONASH | **172,429** |
| JUNCTIONS | 170,389 |
| CLOSEPACKING | 170,261 |

MONASH's 172,429 is the count `docs/PRODUCTION_SHAPE_DECISION.md` cites for the
boundary derivation, which is how the right artifact was identified.

## Provenance

```
B4_SOURCE_COMMIT   884f76e2a0c835f048cf66b336c3a07ed48f9059
B4_MACRO_SHA256    3be7a09422e734ec68ae7d2fab279b2d055158b0a2dd29f201bbe13192192cf1
B4_NIKHEF_CHECKOUT e6429b779d62dba4ec0fb65628470a041ee6a5e9
200,000 events requested per run, 6 runs (mb and hard per tune)
```

Only the **mb** histograms are committed here; the `hard` ones are not used by
the class definition, which is anchored on minimum bias by the ruling.

## ⚠ The half-integer trap, which bit twice

The axis is `[-0.5, 399.5]`, so **bin 1 is N_ch = 0 and its low edge is −0.5**.

**Dump by bin CENTRE, never by low edge.** Labelling by low edge and rounding
turns N_ch = 0 into "−1", which silently moves **872 MONASH events** (0.51 %)
out of the first class — the recomputed c1 then reads 0.51 % against the
published 0.00 %, and every other class is unaffected, so it looks like a
one-row disagreement rather than a labelling bug. `dump_nch.C` uses
`GetBinCenter` and refuses outright if under/overflow is non-empty.

This is the **same trap the boundary derivation already recorded once**:
`FindBin(2.5)` returns the bin *above* a half-integer edge, which produced an
off-by-one that was caught before that table was published. Half-integer edges
are the point of the design — no integer N_ch is ambiguous — and they are also
where the mistakes live.

## Recompute the published translation table

```bash
plotting/paper/make_paper_figures.py --figure multiplicity
```

`boundary_percentiles()` computes, per tune, the fraction of the MB sample
**strictly below** each boundary. It reproduces the paper-facing table in
`PRODUCTION_SHAPE_DECISION.md` to **< 0.01 pp on all 11 classes**, and the
maximum residual to **2.91 pp** exactly. Pinned by
`tests/test_paper_figures.py`.

---

## ➕ 2026-08-17 — the Nikhef `b4_mapping/` copy, and why it is NOT copied here

The scratch reconciliation found
`/data/alice/ipardoza/b4_mapping/macro/CalibrateMultiplicityAgainstMinBias.C`
matching no tracked content, and it was briefly anchored here on that basis.
**That was wrong and is corrected.** It differs from the tracked
`Validation/CalibrateMultiplicityAgainstMinBias.C` by **exactly one line**:

```
-#include "../generation/producer/HeavyFlavourUtils.h"   (tracked, post-restructure)
+#include "../SimulationScripts/HeavyFlavourUtils.h"     (deployed, pre-restructure)
```

The 2026-08-12 restructure moved `SimulationScripts/` to `generation/producer/`
and updated the include. The b4 run predates it (2026-08-09), so the scratch copy
is simply the **pre-restructure form of a tracked file**. Copying it here would
put a second, older copy of a tracked macro under a second path, where the two
can drift. **Archived in place with the diff recorded** —
`docs/SCRATCH_RECONCILIATION.md` §4.3.

### What that copy DOES establish

**The macro is not unrun.** `b4_mapping/logs/` holds six completed runs —
`{mb,hard} x {MONASH,JUNCTIONS,CLOSEPACKING}` — each ending

```
B4_RUN_EXIT=0 tune=<tune> arm=<arm> utc=2026-08-09T0x:xx:xxZ
```

with six `nch_*.root` outputs in `b4_mapping/out/`. The MONASH mb run carries the
counter verdict and the numbers **51.201** (|eta|<4) and **12.948** (|eta|<1)
that `ValidationReports/NCH_DECAY_POLICY_BIAS_8317.md` reports as agreeing to
1.1 % per unit eta — the measured input S4 needs.

**`STATE.md`'s "WRITTEN — UNRUN — AVAILABLE" table therefore lists this macro
wrongly**, and that is recorded rather than silently fixed, because the run
predates the entry and the entry has been read by other sessions since.
