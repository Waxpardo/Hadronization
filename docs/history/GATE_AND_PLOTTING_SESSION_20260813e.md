# The A2 gate, and the paper figure layer — 2026-08-13 (fifth session)

**Three commits, `3f987e1..556ae12`. Suite 37/37 → 39/39**, two tests added,
none removed or skipped.

**The A2 jobs never started**, so this was Task 0 followed by Task 2. No A2
number exists and none was invented.

---

## 0. STATE

| | open 13:53 | close 14:12 |
|---|---|---|
| `stbc-i3` | up, same boot | unchanged, **no reboot** |
| A2 jobs (5478114, 5478127) | **301 Idle** | **301 Idle** |
| merge | alive, validator `slot_389`-ish | alive, 6h48m, `JUNCTIONS/slot_545` |

The merge is advancing steadily (~4 slots/min) and was otherwise left alone.

**One operational note:** `condor_history` is slow enough to blow a 240 s SSH
timeout. `condor_q … -af JobStatus | sort | uniq -c` gives the same answer in a
second and is what the run record now recommends.

---

## 1. TASK 0 — the consumption gate, mechanized

**The problem, stated plainly.** The pre-registration makes the regression check
a gate on consuming the permissive output. Until now that gate lived in a
paragraph. **A paragraph does not stop a script**, and 300 well-formed output
directories protected by prose is precisely the shape of accident this project
keeps writing error-record entries about.

**`analysis/a2_block_shift.py` now refuses to run** unless a sentinel records a
PASSED regression **for the exact variation sha** that produced the output. It
fires **before any input file is opened**, so a missing CSV can never be what
stops you first. There is deliberately **no `--force` and no `--skip-gate`**; the
sentinel path is redirectable only so the gate itself can be tested.

**A sentinel that records FAIL, or a different sha, is treated as worse than a
missing one** — it means somebody already has an answer and it is not the answer
this analyzer needs. *A regression pass certifies one specific macro, not the
idea of a macro.*

**`tools/a2_record_regression.py` is the only thing that can produce a
sentinel, and it cannot be used to assert a pass** — it performs the
object-by-object comparison itself and writes the verdict it measured. **There
is no `--verdict` flag.** It also encodes what "identical" means here: the macro
embeds `analysis_macro_sha256` derived from its own bytes, so it cannot
reproduce that string by construction. That field is named, counted, and
**anything else differing is a FAIL**.

**`tools/a2_quarantine_outputs.py` handles the failure branch physically rather
than by warning.** It moves the 300 permissive slot directories into a dated
quarantine tree with a manifest. It **moves, never deletes** — they are the
evidence for whatever the variation got wrong, the same reason the replicating
extractor was archived rather than removed. It **refuses to run when the
regression PASSED**, because quarantining a valid measurement is its own kind of
damage, and it is a dry run unless given `--apply`.

**`tests/test_a2_regression_gate.py`** has five independent refusal paths
(absent, FAIL verdict, wrong sha, malformed, missing key) **plus the negative
control that stops them being vacuous**: a valid sentinel must get *past* the
gate and then fail later on the missing data, with a different message. A gate
that refuses everything would pass the first four checks and be useless.

---

## 2. TASK 2 — the paper figure layer

Two figures, both pure functions of committed tables and the source, both
regenerating **byte-identically**.

| figure | sha256 | source |
|---|---|---|
| `fig1_species_decomposition.svg` | `d8d3f37b…327083` | `anchors/merged_monash_dedup`, central + ten blocks |
| `fig2_m7_inclusive_shift.svg` | `ad92ae69…f85724` | `anchors/{m7_blocks,m7b_blocks}` via `aggregate_m7.py` |

Recipes **R13**/**R13b**, digests in `GOLDEN_OUTPUTS.md` §2.12.

**Two decisions worth recording.**

- **The numbers are recomputed, not transcribed.** Fig 1 rebuilds the block
  fractions from the per-species anchors; fig 2 *shells out to the committed
  `aggregate_m7.py`* rather than re-implementing the aggregation. A second
  implementation could disagree with the recipe the Golden Outputs pin, and the
  figure would then show numbers no recipe reproduces.
- **Hand-emitted SVG, no dependencies.** Matplotlib is not installed here, but
  it would have been the wrong choice anyway: its bytes move with its version,
  freetype and the installed fonts, so a **pinned digest would fail on another
  machine for reasons unrelated to the physics**. `svgkit.py` routes every
  coordinate through one fixed-precision formatter.

**Fig 2 was rebuilt after the first version was drawn.** Charm CR (~0.55 %) and
beauty (~0.014 %) differ by ~40×, so on a shared linear axis the beauty bars
were sub-pixel — **the figure was hiding the exact comparison it exists to
make.** It now has independent per-sector axes, with the range printed in each
panel title and a "different scales" warning between them.

**Fig 1 is MONASH-only because only MONASH is merged**, but the layout already
reserves the other two: bars are grouped with one slot per tune, and the legend
lists JUNCTIONS and CLOSEPACKING greyed as *not yet merged*. They become bars
with **no layout change**.

**`tests/test_paper_figures.py`** runs the generator twice and requires
byte-identical output, recomputes the structural percentages from the anchors
and requires the figure to display them, and asserts the two labels that must
never be dropped — fig 1's **SELECTION-not-partition** caveat and fig 2's
**INCLUSIVE** banner. Both mistakes have already happened once in this project.

### The figure deliberately not drawn

The **OS−SS observable versus multiplicity class** has no committed table — it
is what the A2 jobs produce. `--figure ossvsmult` **fails closed** (R13b).
**A figure with invented data is worse than a missing figure**, because a figure
travels further than its caption.

---

## 3. NOT DELIVERED

- **No A2 result.** The regression gate is unsatisfied and no job has run. The
  gate now enforces that rather than trusting the next reader.
- **The three-tune table** remains blocked on the merge; untouched.
- The legacy `plotting/` tree was read and left alone as reference (A6).

---

## 4. FOR THE NEXT SESSION

1. `condor_q 5478114 5478127 -af JobStatus | sort | uniq -c`. **Not
   `condor_history`** — it is slow enough to time out an SSH call.
2. When the regression job lands, run **`tools/a2_record_regression.py`**. It
   writes the sentinel; nothing else can. If it reports FAIL, run
   **`tools/a2_quarantine_outputs.py --apply`** before anything else.
3. Then the analyzer runs, or refuses — either way you cannot get a number out
   of unvalidated output by accident any more.
4. Adding JUNCTIONS/CLOSEPACKING to fig 1 needs **no layout work**: commit their
   per-species anchors, extend the two dicts in `figure_species`, re-run, and
   **re-record the digest** in §2.12 — a figure whose table legitimately moved is
   supposed to move.
