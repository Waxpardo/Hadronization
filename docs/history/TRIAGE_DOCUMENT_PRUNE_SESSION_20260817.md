# Triage pass: document, prune, rename — 2026-08-17 (twenty-first session)

**Suite 46/46 before and after, ROOT present. Every cheap `GOLDEN_OUTPUTS`
recipe re-run and matching. `tools/docs_check.sh` clean.**

> **Headline: 219 executables walked, 213 documented, 6 removed, 0 renamed —
> and the zero is the finding.** A third of this repository's code has a
> filename that is load-bearing provenance, so the naming rule needed extending
> before it could be applied. The one name that violates the convention is the
> one name that cannot be changed without invalidating a receipt for a figure
> rendered yesterday. It is priced and deferred rather than performed.

---

## 0. Status at start — one line each, no intervention

- **Merge tail:** at last record (2026-08-16 22:35 CEST) merge `315689` alive
  inside its own JUNCTIONS closure, supervisor `316182` at 0 restarts, EOL
  watcher armed and correctly unfired; projected JUNCTIONS ≈ 03:30 and
  CLOSEPACKING ≈ 18:30 today. **Not checked this session, by instruction** — no
  Nikhef work, the consolidation gate owns it.
- **Systematics queue:** A2 pair-level delivered with its tie-break robustness
  check; A9 deliberately unsubmitted behind it; advisory step 2 open. **A
  concurrent session pre-registered a six-source systematics program during
  this session** — see §6.

---

## 1. What the pass did

| | |
|---|---|
| tracked executables walked | **219** |
| documented in `docs/COMPONENTS.md` | **213** |
| removed from `HEAD` | **6** (`docs/REMOVALS.md`) |
| renamed | **0** (`RENAMES.md` §7) |
| marked UNSURE | **6**, all location or disposition, none an existence question |
| untracked build products swept | 8 `__pycache__` trees, 6 `_C.so`/`_C.d`, 5 `.pcm`, 1 `.DS_Store` |

**`docs/COMPONENTS.md` is the deliverable** — one navigable map organised by
pipeline stage (generation → analysis → merging → extraction → plotting, plus
validation, contracts, tools, tests, attic), with the schema the brief set:
purpose, in → out, the connection map, *why it exists*, status. No orphan docs;
it is wired into `README.md` §7 beside `GOLDEN_OUTPUTS.md` and `ERROR_RECORD.md`.

---

## 2. The naming rule had to be extended before it could be applied

The brief exempts artifacts from renaming *because they appear in recorded
provenance*. **Measured, the same argument covers 67 of 219 executables:**

| | count |
|---|---|
| named inside a `GOLDEN_OUTPUTS.md` recipe, a run record, an anchor `MANIFEST.md`, a signed `config/*.json`, `REPRODUCIBILITY.md`, `Paper/**` or the `Makefile` | **67** |
| rename-eligible | **134** (51 of them `tests/`) |

**Not one of the eligible 134 carries a banned qualifier or a non-functional
name.** `tests/` is `test_<subject>.py`, `plotting/` is `Plot_<What>_<How>.C`,
`Validation/` is `Validate*`/`Audit*`/`Test*`, `tools/` is verb-first where it is
a tool and noun-first only where it is a library or a reporter. The tree was
already conventionally named, and the pass says so rather than manufacturing
churn.

One clarification folded into the rule: **`build_decay_parent_map_v2.py`'s `_v2`
names the artifact's version, not the code's.** v1.1 and v2 are separate
published maps with separate recipes and both builders are live.

### 2.1 The exception, priced

**`plotting/improvedPlotting_THnSparse.C`** violates the rule and is in the
frozen group. Renaming it forces a byte change — ROOT ties the entry-point
function to the basename, and the macro embeds its own filename at `:385` and
`:1334` — and `tools/statistical_robustness.py:669` checks **every**
`multiplicity_boundary_receipt_v1.json` against `sha256` of that file. The
shipped three-tune canvas records `6dace202…`.

**Changing the bytes does not re-pin a digest; it invalidates committed receipts
for a figure rendered on 2026-08-16.** Two further pins move with it
(`config/multiplicity_class_boundaries_v1.json`, the three-tune run record), and
the figure set is not frozen because the merge is still inside its closure pass.

**Recommendation:** rename to `Plot_PairBalancing_THnSparse.C` in a dedicated
commit *after* the campaign is recorded COMPLETE, re-rendering so the receipt is
regenerated rather than patched. Owner's call — `COMPONENTS.md` §11 Q5.

---

## 3. What writing the entries found

**The method earned its keep four times.** Each of these would have been taken
by a sweep keyed on reference counts, and each has a live reason to exist that
only appeared when the entry was written.

1. **`attic/count_events/CountEvents/generated_heavy_flavor_summary.C` is
   measurement-provenance, in `attic/`.** It generated
   `Paper/Tables/generated_heavy_flavor_summary.tex` — **published right now** —
   and `docs/A9_PAPER_TABLE_REGENERATION.md` cites it as the record of what was
   counted. A9 is open. Kept; §11 Q3 asks whether it should leave `attic/`.
2. **`attic/plotting/improvedPlotting.C` has a standing keep-argument.**
   `POST_SUBMISSION.md` correction 1, written after reading the code, records
   that it consumes `complete_root` — the same merge product the live path uses
   — making it a cross-check, not a superseded predecessor.
3. **Census D6 was wrong, and one `shasum` closed it.**
   `B_Balancing_GeneralPlotting.C` was flagged as "a byte-level duplicate
   question". **The two files differ**: 2217 vs 3051 lines, `c41b52dc…` vs
   `d6e6b74d…`, different headers, different stated purpose. The attic copy
   carries the author's 30-line explanatory header the other replaced with a
   TODO. **D6 is withdrawn as a question**; both files stay.
4. **`attic/split_chain/` (18 files) is kept by an owner statement**, not by
   inertia: `README.md` §6 says it remains available for reference samples.

**Two stale instructions fixed while there:** `plotting/FinalAnalysis/README.md`
and `plotting/PtMultiplicity/README.md` both told the reader to run
`plotting/ListHistos.C`, a path that stopped existing at the 2026-08-12
restructure. Now `rootls -l`, which ships with ROOT.

**Census Q5 closed:** `tools/docs_check.sh` stays — it is in `make docs-check`,
it is part of this session's gate, and it costs nothing.

---

## 4. The gate — every condition, measured

**Suite 46/46, `ROOT: /opt/homebrew/bin/root`.** Run before the pass and again
after, including after the concurrent session's changes landed.

| recipe | positive check | result |
|---|---|---|
| R1 `make registry` | no `STALE` | 50 signed states, 300 signed pairs |
| R2 | absence of `SPECIES_ORDINALS_STALE` | `species=202 digest=646f310f78126267` |
| R3 | absence of stale marker | `PAIR_OBJECT_CONTRACT_CURRENT objects=66` |
| R4 `make cards`/`cards-current` | exit 0 | `CARD_CONFIG_CURRENT` |
| **R5** | `map_sha256=dd502a10c5932fff`, `I1=PASS I2=PASS`, `rows_changed=101 table_affecting=60` | **all matched; output byte-identical to G6 `ed148156…`** |
| **R6** | `sha256=c9593c9c0a7c4ec2`, `split=2`, two `SPLIT` lines | **all matched; byte-identical to G7 `58081aa2…`** |
| R7 | `TOTAL 1298655240 INVARIANCE CONSERVED`, D⁰ 25.2435 | matched (D̄⁰ 25.1707) |
| R8 / R8b | `at_risk_pct=12.8396`; `postsplit_residual_pct=0.0018 residual_species=2` | matched |
| R9 / R9b | §2.8 / §2.7 reproduced | integer counts exact, both sectors |
| R10 / R10b | 30 of 88; 0 of 88 at σ̂ = 4.3990 | `flagged=30`; `flagged=0 sigma^=4.3990` |
| R12 | `charm 24x, beauty 26x`; 87 invert, 8 bracketed | matched, total `53,662,413.8 .. 53,662,827.8` |
| R13 | three digests of §2.12, `FIGURES_DONE` | **all three matched** (`316a7d99…`, `ffec6a3d…`, `e687b953…`) |
| R13b | refuses, `NOT AVAILABLE` | refused |
| **R14** | stdout sha256 `a46a7f6b96f66817…fc930d` | **exact match on committed anchors** |
| `tools/docs_check.sh` | advisory listing, rc=0 | clean |

**R11 (`make test`) and R15 are covered above and by the suite.** Not run:
recipes requiring Nikhef inputs (G1's fixture, N6) — out of scope by instruction.

> **G6 and G7 regenerating byte-identical is the strongest single result here.**
> It is the difference between "the file still has the right bytes" and "the file
> is still derivable from its inputs", and only the second is a freeze contract.

---

## 5. `docs/history/**` — the recommendation, not an action

**Nothing was touched.** Sizes, for the owner's ruling:

| directory | files | size |
|---|---|---|
| `handoffs/` | 49 | 728 K |
| `studies/` | 30 | 692 K |
| `audits/` | 5 | 576 K |
| `agent_instructions/` | 1 | 128 K |
| `plotting_validation/` | 2 | 24 K |
| `cleanups/`, `transcripts/` | 2 | 24 K |
| **total** | **111** | **2.3 M** |

**Recommendation: publish it, unedited, with one added `README.md`.** 2.3 MB of
text is nothing beside 276 GB of raw files that are not published either way, and
the directory is the evidence for the project's central claim — that every
mistake which reached a number is recorded with who caught it and what now
prevents it. A reader who meets `ERROR_RECORD.md` E1, E4, E5 or E7 and wants the
session that found it should be able to reach it. The one file to look at
deliberately before publishing is `agent_instructions/` (128 K): it is working
instructions for an AI agent, not physics, and it is the only item whose absence
would cost a reader nothing. **The append-only rule stands either way** — this is
a publish/withhold decision, not a prune.

---

## 6. A concurrent session shared this worktree, and the index collided

**Recorded because it changed where six commits' worth of work landed, and
because the fix is a working practice rather than a patch.**

At 10:58–11:00 another session working in the same checkout implemented the
card-variant mechanism (`tools/campaign.py`, `generation/submit/runCondorJob.sh`,
`tools/render_production_submit.py`) and committed
`fc59491 "Pre-register the six-source systematics program, before any job"`.

**`git commit` swept this pass's staged `git rm`s into that commit.** The six
deletions are therefore in a commit whose message describes only the systematics
pre-registration, and the manifest explaining them is in the commit after.

**Nothing is lost and the tree is correct** — the files are removed,
`git log --follow` reaches every one, and `docs/REMOVALS.md` §1 carries a banner
pointing at `fc59491`. **History was deliberately not rewritten**: rebasing
shared history under a live worker trades a cosmetic problem for a real one.

Its in-flight working-tree changes were **left untouched and excluded from this
session's commit by explicit pathspec**. One of them is worth flagging to its
owner as a genuine find: `runCondorJob.sh`'s `project_base` derivation was
broken by the 2026-08-12 restructure and had gone unnoticed for five days
because the Nikhef checkout is still pre-restructure — **no production job has
ever been launched from the restructured layout**, and the first one would have
been a systematics variation.

> **The practice:** a staged index is shared mutable state between sessions in
> one worktree. Stage and commit in one step, or use separate worktrees.

---

## 7. Boundaries

No `Paper/**`. No `docs/history/**` edits — one file added, this record. No
Nikhef work, no pinfile, no checkout advance, no intervention in the merge. No
committed artifact, anchor or manifest renamed or rewritten. `STATE.md`
untouched: nothing here changes where the project stands.

## 8. For the next session

1. **The deep-documentation session is unblocked** — `docs/COMPONENTS.md` is the
   map it extends.
2. **Six UNSURE questions want rulings** (`COMPONENTS.md` §11). Q5 (the plotter
   rename) and Q4 (whether `plotting_documentation.md`'s 485 lines were ever
   folded into `plotting/README.md`, as plan D5 ruled) are the two with
   substance behind them.
3. **`docs/REPO_FILE_CENSUS.md` is now superseded as a worklist** by
   `COMPONENTS.md`. It stays as the dated snapshot it is; it should not be
   updated, and it should not be used again as an index — it was written against
   374 files at `9426f38` and the tree is 617.
