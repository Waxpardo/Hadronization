# Deferred work — the post-paper list

This is what the deep repository audit found, judged, and decided not to do
before the paper. It is published because a repository that shows its deferred
work is easier to trust than one that does not.

**The load-bearing measurement.** The audit carries 391 rows. **138** are
deferred by judgement. (A further 38 are dormant behind ruling R31 and are
merged into the same `DEFER` state in disposition v5, giving 176 there; they
are described separately below, because "we decided not to" and "the module is
switched off" are different facts.) Of those, **87 are LATENT** and **51 are COSMETIC**, and **none is
`BLOCKS_PAPER`**. Every row the audit marked as blocking the paper was routed
to a session and closed; nothing on the paper path is hiding here. WRAP
re-measured this against `DA1_DISPOSITION_20260830_v4.csv` rather than
repeating it.

Deferred is not a synonym for unimportant. It means the row was read, its cost
and its risk were judged, and the judgement was that the paper does not depend
on it.

## How the rows group

Grouped by the tracked directory each row's `where` names, which is objective
and re-derivable:

| area | rows | LATENT | COSMETIC | what the group is |
|---|---:|---:|---:|---|
| `generation/` | 36 | 22 | 14 | producer and submission machinery; the campaigns are complete, so these are read-and-improve items, not run blockers |
| `config/` | 35 | 21 | 14 | schema and contract hygiene: keys described imprecisely, fields no consumer reads, comments that restate a constant |
| `tools/` | 14 | 9 | 5 | generator and helper scripts, including suite-reporting cosmetics |
| `merging/` | 11 | 6 | 5 | **merge semantics** — see below |
| `Validation/` | 9 | 8 | 1 | validation macros off the paper path; none produces a delivered number |
| `contracts/` | 9 | 7 | 2 | **contract prose hygiene** — see below |
| `analysis/` | 8 | 3 | 5 | reduction-stage comments and naming |
| `plotting/` | 4 | 3 | 1 | **the plotting layer's recorded items** — see below |
| `extraction/` | 4 | 4 | 0 | extraction-stage helpers |
| `tests/` | 2 | 1 | 1 | companion checks that fire only outside the paper sequence |
| `evidence/` | 2 | 2 | 0 | historical driver scripts, evidence-only |
| other | 4 | 1 | 3 | `Makefile` and top-level items |
| **total** | **138** | **87** | **51** | |

## The five themes worth naming

### Merge semantics (11 rows, `merging/`)

The supervised merge is wired and used (ruling R25), and the merged products
behind every figure are accepted. What is deferred is the *description* of what
the merge guarantees at its edges: which object classes are summed and which
are taken from the first input, and what a partial input set does. Closing it
means reading `merging/MergeAnalysisObjects.C` against the supervisor and
writing the semantics down once, with a test that fails if they change. It is a
day of reading, and no delivered number depends on it, because every merged
product in the campaign was produced from a complete input set and the closure
checks passed on the result.

### The decay-map build chain (9 rows)

Nine rows name a decay map or its builder. The maps in `contracts/` are
generated, committed, and consumed by `#include`; the rows concern the
reproducibility of the *build*, not the correctness of the committed bytes —
which the suite already checks by digest. Closing it means making the builder
re-runnable from a clean checkout and proving the output is byte-identical to
what is committed.

### The plotting layer's recorded items (4 rows, plus two named debts)

The two named debts are recorded in the macro's own style map at
`plotting/improvedPlotting_THnSparse.C:1701-1744` and described in
[../pipeline/STYLE.md](../pipeline/STYLE.md):

1. **The four near-duplicate template sites** at `:5260`, `:5568`, `:5879` and
   `:6200`. Each of the four draw functions carries its own copy of the title,
   legend and style block. They are near-duplicates, and a change to one is a
   change that has to be made four times. Closing it means extracting one
   template and proving the rendered bytes do not move.
2. **`MultiplicityClassLineStyle` matches a prefix nothing emits.** The
   function at `:4023` tests for the prefix `hDPhic`, while every tracked
   configuration emits `hDPhiM<lo>_<hi>`, so it returns style 1 for every bin
   it ever sees. It is dead in effect, not in form. Verified across all five
   V-configurations: zero objects carry the `hDPhic` prefix. The class
   line-style ladder that actually runs lives in `plotting/TunePlotStyle.h`.

Neither moves a number. Both were left because the figures were certified and
the plotting layer was closed by owner directive.

### Contract prose hygiene (9 rows, `contracts/`, and ~19 rows of comment prose overall)

Generated headers and contract JSON whose surrounding prose describes the field
loosely, or describes a rule the file no longer implements. The bytes are
right; the sentences beside them are imprecise. This is the same class of
defect as the line-anchor work, and it is worth doing for the same reason: a
reader who cannot trust the prose has to read the code, which is the cost the
documentation exists to remove.

### The systematics reactivation set (38 rows, `SYS-DORMANT`)

Ruling **R31** paused systematics development and left the module intact and
toggleable. Thirty-eight rows are dormant behind that pause: 21 LATENT, 11
COSMETIC, 3 `BLOCKS_STAGE` and 3 `BLOCKS_PAPER`.

**The three `BLOCKS_PAPER` rows block the systematics stage, not this paper.**
They are `DA1-029` (the overlay renderer), `finding 29`
(`extraction/write_tune_separation.py:89-92`) and `DA1-034`
(`tools/a2_record_regression.py`). Each blocks a claim the paper does not make,
because the paper reports statistical uncertainties only. That the paper says
so is itself an open question, and it is recorded as such in
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) item 1 — the register a reader should
follow from here.

The work list for the session that switches the module back on is
[../systematics/REACTIVATION.md](../systematics/REACTIVATION.md); the reason
for the pause is [../systematics/STATUS.md](../systematics/STATUS.md).

## Two items deferred by WRAP itself

- **The R30 gate classification is stale.** The bench document
  `R30_GATE_CLASSIFICATION_20260829_v3.md` classifies **91** drivers; the suite
  now has **97**. Seven drivers in the tree are unclassified, and one
  classified driver (`test_manuscript_release_blockers`) no longer exists —
  ruling R38 retired the manuscript gate. WRAP re-measured the twelve
  gate-cost corrections the audit rows `DA1-043` and `DA1-052` name, and
  those are now closed; bringing the document to 97 rows is post-paper.
- **The fifteen anchors WRAP found beyond ARCH-1's enumeration** are repaired,
  but the sweep that found them covered citations into the compiled plotting
  sources only. The same bare-anchor idiom exists elsewhere in the tree and has
  not been swept. Ruling R49 makes the convention binding going forward; a
  full retrospective sweep is post-paper.
