# The paper figure layer

**Every paper figure is generated from committed tables by script. There are no
hand steps, and there is no figure whose numbers exist only inside the figure.**

```bash
plotting/paper/make_paper_figures.py            # both figures
plotting/paper/make_paper_figures.py --figure species
```

Digests and recipes: `docs/GOLDEN_OUTPUTS.md` §2.12 (recipes R13, R13b).
Self-check: `tests/test_paper_figures.py`, in `make check`.

## Why this is not built on `plotting/`

The existing tree is kept as **reference, not as a base**. It is ROOT-macro
based, written against the **v2** pair schema, and points at a legacy dataset —
review finding **A6**. Its input contract is not the one the paper's numbers now
come from. This layer reads the committed anchors and CSVs that the paper
actually quotes, and has **no ROOT and no matplotlib dependency**.

## Why hand-emitted SVG

Because the digests are pinned. Matplotlib's output bytes move with its own
version, with freetype, and with which fonts are installed, so a pinned digest
would fail on a different machine for reasons that have nothing to do with the
physics. `svgkit.py` has no dependencies and routes every coordinate through one
fixed-precision formatter, so **the bytes are a pure function of the input
numbers and the source**. Determinism is checked by regenerating and comparing,
not asserted.

It is not a plotting library and should not become one. It draws what these
figures need.

## The figures

| file | what | source |
|---|---|---|
| `fig1_species_decomposition.svg` | species decomposition by tune, **both conventions** | `anchors/merged_monash_dedup`, central + ten blocks |
| `fig2_m7_inclusive_shift.svg` | M7 **inclusive** unresolved-origin shift, per tune, both sectors | `anchors/{m7_blocks,m7b_blocks}` via `aggregate_m7.py` |
| `fig3_multiplicity_classes.svg` | the multiplicity class definition: common absolute N_ch bins, tune-dependent percentile labels | `anchors/b4_multiplicity_mb` |

**Fig 1 is MONASH-only because only MONASH is merged.** The layout already
reserves the other two tunes: bars are grouped per category with one slot per
tune, and the legend lists JUNCTIONS and CLOSEPACKING greyed as *not yet
merged*. When their anchors land, they become bars — **no layout change**.

**Fig 2 has all three tunes already**, since M7 ran at full scale.

**Fig 3 is a Methods figure and is complete.** It recomputes the paper-facing
percentile translation table from the committed MB samples rather than
displaying it, and reproduces the published values to < 0.01 pp on all eleven
classes with the maximum residual at 2.91 pp exactly.

## Three labels that must never be dropped

Each is asserted by the test, because a figure travels further than its caption
and every one of these mistakes has already been made once in this project.

- **Fig 1 panel B is a SELECTION, not a partition.** Its rows are the largest
  reconstructable observables; they do not sum to 100 %, and a reader who sums
  them and finds less has not found missing weight.
- **Fig 2 is INCLUSIVE level.** It is *not* a bound on the pair observable's
  systematic (review finding A2), and it says so on its face.
- **Fig 3's residual is not the ±3 pp criterion passing.** That criterion asked
  whether *per-tune* boundaries coincide — they do not. The residual is how far
  a *common* boundary's meaning drifts between tunes. The figure says so.

## The figure that is deliberately absent

The **OS−SS observable versus multiplicity class** has no committed table. It is
what the A2 jobs produce (`docs/A2_PAIR_UNRESOLVED_RUN_RECORD.md`).
`--figure ossvsmult` **fails closed** rather than drawing a placeholder.

## Adding a tune

Nothing in the figure code needs to change. Commit the tune's per-species
anchors alongside `merged_monash_dedup` and extend the `structure`/`experiment`
dicts in `figure_species` to load them; `TUNE_ORDER` and the colour map already
carry all three. Then re-run, and **re-record the digest in §2.12** — a figure
whose underlying table legitimately moved is supposed to move.
