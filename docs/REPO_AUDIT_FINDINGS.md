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

## 2. RENAME CANDIDATES — ruled and acted on 2026-08-20

> **This section's original reasoning is superseded, and the record of what
> happened is `RENAMES.md` §8.** It said renaming belongs to the export. It does
> not: the documentation rewrite happens here first and will author documents
> that cite paths, so the paths have to be final before the prose is written.
>
> **R5 executed. R1 attempted, measured and BLOCKED** — it cannot move without
> changing files whose digests two owner grants and three receipts pin. **R2
> refused**, **R3 and R4 declined.** The pin inventory that decided all five is
> `docs/RENAME_PATH_PINS.md`.

The candidates as first recorded, with the evidence behind each ruling:

| # | path | why the name misleads | note |
|---|---|---|---|
| **R1** | `AnalysisScripts/` | holds **no analysis scripts**. Its contents are frozen artifacts, generated headers and `anchors/`. The one-pass analysis lives in `analysis/` | `RENAMES.md` §2 struck `→ artifacts/` under override D4, because moving it meant touching 63 paths across 138 occurrences. **The export rewrites paths anyway**, so D4's reason does not carry over |
| **R2** | `plotting/improvedPlotting_THnSparse.C` | "improved" names a comparison with a predecessor that is now in `attic/` | COMPONENTS Q5 already rules **rename after the figure set freezes, with a re-render** |
| **R3** | `plotting/FinalAnalysis/` | "Final" describes neither the stage nor the product; it is one directory of two macros already scheduled for retirement | COMPONENTS Q2 rules **leave as scheduled** and prices the naming cost deliberately |
| **R4** | `analysis/status_analysis_qq.C` vs `analysis/status_analysis_THnSparse_qq.C` | two names one token apart, on different chains — the first is superseded and its only consumer sits in `attic/split_chain/` | the same file is an **OWNER** row in the manifest |
| **R5** | `AnalysisScripts/anchors/merged_monash_replicated/` | holds the **replicated** (pre-E5) extraction, while `merged_monash_dedup/central/` holds the corrected one. "central" means the merge product in one name and the E5 state in the other | both are PUBLIC and a reader meets them side by side |

**R1 is the only one that changes how the published tree reads at a glance**,
and it is the only one whose blocking reason expires at export.

---

## 3. THE OWNER RULINGS — 2026-08-20

**All eight OWNER questions are closed and every one went INTERNAL.** No row in
`docs/REPO_AUDIT.csv` carries `class=OWNER` any more; each `why` records the
ruling and its date.

| ruled | files |
|---|---|
| `AnalysisScripts/decay_parent_map_v1.json` | 1 |
| `Literature/pveen_…msc_thesis.pdf` | 1 |
| `Paper/Tables/generated_heavy_flavor_summary.tex` | 1 |
| `analysis/status_analysis_qq.C` | 1 |
| `attic/plotting/improvedPlotting.C` | 1 |
| `attic/split_chain/**` | 18 |
| `docs/writing_standard/STANDARD.md`, `ste-rules.md` | 2 |

**Two consequences the rulings carry with them.** The writing standard does not
travel, so `tools/prose_check.py` and `tests/test_prose_check_ing_start.py`
leave with the rules they enforce. And `README.md` §6 no longer promises that
the split chain remains available: **the published repository must not offer
code it does not ship.** That sentence is deleted.

## 4. TWO STRUCTURAL NOTES FOR THE EXPORT SESSION

**4.1 A tool and its test leave together, or the suite names a missing file.**
`tools/checkout_advance_guard.py` and `tools/install_checkout_guard_hook.sh`
read as cluster operations, and a test in `tests/` exercises each. They stay
PUBLIC: the invariant they protect applies to any cluster the chain runs on,
and **dropping a tool while keeping its test turns `make check` red in the
exported tree**.

`tools/prose_check.py` went the other way on 2026-08-20, and the pairing is why
`tests/test_prose_check_ing_start.py` went with it. The owner ruled that the
writing standard does not travel. A checker without its rules is not a contract
a reader can act on. A test naming an absent tool is worse than no test.
**The rule this settles: a tool and the test that pins it always share a
class.** `tests/test_public_never_cites_internal.py` enforces half of it
mechanically. A PUBLIC test that names an INTERNAL tool becomes a recorded
reference, and it fails until someone records or removes it.

**4.2 Live configuration carries cluster-absolute paths.**
`config/dataset_selector.json` names `/data/alice/ipardoza` on 57 lines and
cites `docs/history/CAMPAIGN_SEAL_SESSION_20260817c.md`, which is INTERNAL.
`docs/GOLDEN_OUTPUTS.md` names the same volume on 16 lines. **Both are PUBLIC files.** They point at
paths a reader cannot reach and at a document the export does not carry. The
manifest marks them `needs-rewrite`. The rewrite is a later phase; this note
records why they are on the list.

---

## 5. THE PUBLIC-CITES-INTERNAL LEDGER

`docs/REPO_AUDIT_CITATIONS.tsv` records **181 references from 57 PUBLIC files
to INTERNAL paths**, and `tests/test_public_never_cites_internal.py` fails on
any reference the ledger does not already hold.

**The ledger is a worklist, not an exemption.** It keys on citing file, cited
file and matched token with an exact count, so one reference more or one fewer
breaks the comparison in either direction. A file that already carries recorded
references gets no allowance for a new one.

**The check found two class errors that the per-path pass missed.** The
manifest now carries both corrections:

| path | was | is | why the citation exposed it |
|---|---|---|---|
| `docs/PRODUCTION_SHAPE_DECISION.md` | INTERNAL | **PUBLIC** | its own opening says no number in it is a paper number, and §4.19 **THE RULING** then fixes the published multiplicity axis. `config/multiplicity_class_boundaries_v1.json` names it as `"ruling"`, and two live plotting headers cite it as the authority |
| `attic/count_events/CountEvents/generated_heavy_flavor_summary.C` | PUBLIC | **INTERNAL** | it hard-codes `Paper/Tables/generated_heavy_flavor_summary.tex`, and its whole justification was that the table is published. The owner ruled that table INTERNAL on the same day |

**The audit's own machinery is INTERNAL for the same reason.**
`tools/repo_audit.py`, `tests/test_repo_audit_manifest.py`,
`tests/test_public_never_cites_internal.py`, `docs/REPO_AUDIT.csv`,
`docs/REPO_AUDIT_CITATIONS.tsv` and `tools/repo_audit_rulings.json` exist to
decide what the export carries. A tool that names every excluded path
publishes the exclusion list along with itself.

> **One document is PUBLIC on a reason worth stating plainly.**
> `docs/SYSTEMATICS_HARVEST_RUN_RECORD.md` is 3200 lines of session log, and it
> is PUBLIC only because three of its sections are load-bearing for published
> results: `docs/SYSTEMATICS.md` cites §15 and §20 as the record behind
> per-class numbers, and both `systematics_results_20260820/VERDICT.md` and
> `COMBINED_SYSTEMATICS.md` cite **§25 as the pre-declaration of the S4
> subset** — the evidence that S4's scope was fixed before its run.
>
> **That is a thin reason to publish 3200 lines.** Sections 11 to 13 coordinate
> two executors, §19 and §27 are handoffs, and §7 lists decisions for the
> owner. The document is a session record with three pre-registrations buried
> in it. **The clean resolution is to lift §15, §20 and §25 into a
> pre-registration document and rule the remainder INTERNAL**, which would drop
> ten recorded citations at once. That is a content change, so this session
> records it rather than doing it.
