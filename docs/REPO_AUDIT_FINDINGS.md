# Repository audit — findings beyond the manifest

**Written 2026-08-20 on branch `repo-audit`, against `1c9076b`.** Companion to
[`docs/REPO_AUDIT.csv`](REPO_AUDIT.csv), which carries the per-path rulings.

**This session deleted nothing, moved nothing and renamed nothing.** Everything
below is a finding. Two sections state work for the export session. This
session executes neither.

---

## 1. THE UNTRACKED WORKING TREE

The primary checkout carries eight untracked top-level paths. **None of them is
source code that a fresh clone fails to receive.** That is the opposite of what the
question anticipated. The evidence follows.

### 1.1 `PlottingScripts/` — build residue of a rename, not lost code

**`PlottingScripts/` was renamed to `plotting/` on 2026-08-12.** `RENAMES.md:30`
records the move: 34 tracked files, by `git mv`, with history preserved. The
directory that remains in the working tree holds what `git mv` never touched,
because none of it was ever tracked.

| extension | count | what it is |
|---|---|---|
| `.png`, `.pdf` | 89 + 89 | rendered figure output under `Plots/` |
| `.C` | 89 | **ROOT canvas dumps**, all 89 under `Plots/`, from `TCanvas::SaveAs` |
| `.so`, `.d`, `.pcm` | 13 + 13 + 13 | ROOT ACLiC build products |
| `.DS_Store` | 10 | Finder metadata |

**316 files, 7.7 MB, and not one source macro, header or configuration.** The
`.C` files are the trap in this census: they carry a source extension and they
are canvas serialisations, every one of them under `Plots/`. `.gitignore`
already ignores `*_C.so`, `*_C.d`, `*.pcm` and `plotting/**/Plots/`.

**So the 27 references are not references to live code.** Every one resolves to
a path the restructure moved, and git tracks every current path:

| verdict | files | what the reference is |
|---|---|---|
| **historical** | **25** | session records, handoffs, prior audits, the rename log and the change report — documents whose subject *is* the pre-restructure layout |
| **stale name** | **2** | a live claim written against the old path |

**The two stale names are both in PUBLIC documents and both are marked
`needs-rewrite` in the manifest:**

| file | line | says | current path |
|---|---|---|---|
| `docs/COMPONENTS.md` | 550 | `PlottingScripts/improvedPlotting_THnSparse.C` | `plotting/improvedPlotting_THnSparse.C` |
| `docs/FIGURE_INVENTORY.md` | 999 | `PlottingScripts/B_Balancing_GeneralPlotting.C` | `attic/plotting/B_Balancing_GeneralPlotting.C` |

`RELEASE_BLOCKERS.md:1848` and `POST_SUBMISSION.md:385` also name "four
`PlottingScripts` sites" for the hard-coded three-tune triple. **The blocker's
substance is live and its path name is stale.** Seven tracked files under
`plotting/` hard-code the triple:

```
plotting/Plot_InclusiveKinematicSpectra_Raw.C:875, :2542
plotting/PtMultiplicity/Plot_HF_SpeciesResolvedPtSpectra_vsMultiplicity_subsamples.C:581, :1654
plotting/TunePlotStyle.h:14
plotting/Validate_THnSparse_Production.C:47
plotting/make_hf_run3_v1_three_tune_config.py:42
plotting/paper/make_paper_figures.py
plotting/README.md:200
```

Both documents are INTERNAL, so neither stale name reaches the export. **The
blocker itself should be re-pointed at `plotting/` before anyone counts four
sites and finds seven.**

> ### The verdict, stated as the question asked for it
>
> **The references are stale, and no live code exists that a fresh clone fails
> to receive.** The reconstructability claim holds. What sits in the working
> tree is 7.7 MB of regenerable build output and rendered figures that survived
> a `git mv` because git never tracked them.

### 1.2 The other seven untracked paths

| path | size | what it is | disposition |
|---|---|---|---|
| `Sources/` | **389 MB**, 33 files | third-party PDFs — published papers, textbooks and reviews | **must never be tracked.** Copyrighted works by other authors. `.gitignore` does not currently name it |
| `PUBLICATION_READY_CODING_AGENT_INSTRUCTIONS.md` | 96 KB | agent working instructions | a tracked copy is at `docs/history/agent_instructions/`, and **the two differ by digest** — the working copy has drifted |
| `LEARNING_ROADMAP.md` | 45 KB | personal study plan | not project record; leave untracked |
| `LEARNING_ROADMAP.md.bak-20260731` | 36 KB | its dated backup | same |
| `graphify-out/` | 5.1 MB, 93 files | output of an external graphing tool | regenerable tool output |
| `global_balancing_plots.ps` | 89,180 B | ROOT PostScript of the balancing canvases | regenerable |
| `ROOT::Append` | 89,167 B | **the same PostScript, written to a file literally named `ROOT::Append`** | an accident, not a file |

**`ROOT::Append` deserves one line of its own.** Its DSC header reads
`%%Title: ROOT::Append: global_balancing_plots`, `%%Creator: ROOT Version
6.38.04`, dated 2026-08-18. ROOT read a `SaveAs` argument as a filename rather
than as the append directive. It then wrote the canvas twice: once correctly,
once under the option's own name. **The ROOT version that wrote it is
6.38.04, which is the off-pin Homebrew build behind review finding A7**
(`docs/ERROR_RECORD.md`), not the pinned 6.30/01.

> **`.gitignore` covers five of these seven by pattern and does not name
> `Sources/`, `graphify-out/`, `ROOT::Append` or the two roadmap files.** Adding
> `Sources/` is the one that matters: 389 MB of other people's copyrighted PDFs
> is one `git add -A` away from the object store, and
> `docs/PUBLICATION_EXPORT_EXCLUSIONS.md` already argues at length why a blob
> that reaches history cannot be retracted.

---

## 2. RENAME CANDIDATES — none executed

**Renaming belongs to the export**, which builds a new tree and therefore pays
none of the path-rewrite cost that struck three rows from the restructure plan.

| # | path | why the name misleads | note |
|---|---|---|---|
| **R1** | `AnalysisScripts/` | holds **no analysis scripts**. Its contents are frozen artifacts, generated headers and `anchors/`. The one-pass analysis lives in `analysis/` | `RENAMES.md` §2 struck `→ artifacts/` under override D4, because moving it meant touching 63 paths across 138 occurrences. **The export rewrites paths anyway**, so D4's reason does not carry over |
| **R2** | `plotting/improvedPlotting_THnSparse.C` | "improved" names a comparison with a predecessor that is now in `attic/` | COMPONENTS Q5 already rules **rename after the figure set freezes, with a re-render** |
| **R3** | `plotting/FinalAnalysis/` | "Final" describes neither the stage nor the product; it is one directory of two macros already scheduled for retirement | COMPONENTS Q2 rules **leave as scheduled** and prices the naming cost deliberately |
| **R4** | `analysis/status_analysis_qq.C` vs `analysis/status_analysis_THnSparse_qq.C` | two names one token apart, on different chains — the first is superseded and its only consumer sits in `attic/split_chain/` | the same file is an **OWNER** row in the manifest |
| **R5** | `AnalysisScripts/anchors/merged_monash_central/` | holds the **replicated** (pre-E5) extraction, while `merged_monash_dedup/central/` holds the corrected one. "central" means the merge product in one name and the E5 state in the other | both are PUBLIC and a reader meets them side by side |

**R1 is the only one that changes how the published tree reads at a glance**,
and it is the only one whose blocking reason expires at export.

---

## 3. WHAT THE MANIFEST FOUND THAT THE RULE DID NOT SETTLE

Eight questions, 25 files, listed in `docs/REPO_AUDIT.csv` as `class=OWNER`.
Each row states its question in the `why` column. The session report collects
them rather than restating them here.

## 4. TWO STRUCTURAL NOTES FOR THE EXPORT SESSION

**4.1 The PUBLIC test suite pins three tools that read as internal.**
`tools/checkout_advance_guard.py`, `tools/install_checkout_guard_hook.sh` and
`tools/prose_check.py` are cluster-checkout and house-style tooling. A test in `tests/` exercises each one, and the brief rules tests PUBLIC. **Excluding any
of them turns `make check` red in the exported tree**, so all three are PUBLIC
in the manifest. The alternative — dropping their tests — shrinks the
denominator, which is the failure `tools/run_tests.sh:36-40` exists to prevent.

**4.2 Live configuration carries cluster-absolute paths.**
`config/dataset_selector.json` names `/data/alice/ipardoza` on 57 lines and
cites `docs/history/CAMPAIGN_SEAL_SESSION_20260817c.md`, which is INTERNAL.
`docs/GOLDEN_OUTPUTS.md` names the same volume on 16 lines. **Both are PUBLIC files.** They point at
paths a reader cannot reach and at a document the export does not carry. The
manifest marks them `needs-rewrite`. The rewrite is a later phase; this note
records why they are on the list.
