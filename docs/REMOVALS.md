# Removals — what left `HEAD`, and why

**Opened 2026-08-17 by the triage pass, against `d5f96d3`.** Companion to
[`RENAMES.md`](../RENAMES.md) (what moved) and
[`COMPONENTS.md`](COMPONENTS.md) (what stayed, and why).

**Git history is the archive.** Every file below is reachable with
`git log --follow -- <path>` and restorable with `git show <commit>:<path>`.
Nothing here was deleted to save space; each was deleted because **no defensible
answer to "why does this exist?" survived being written down**. That is the
whole test, and files that passed it are documented in `COMPONENTS.md` instead.

> **What this document is NOT.** It is not a licence to sweep. The same pass
> examined 219 tracked code files and removed six. Four candidates that a
> mechanical dead-code sweep would have taken were **kept** because writing the
> entry surfaced a live consumer — they are recorded in §2, because a near-miss
> is the part of a deletion record that teaches something.

---

## 1. REMOVED — six files, 2026-08-17

All six lived in `attic/`, whose contents the revised deletion policy releases
from `HEAD`. All six were authored 2026-02 and never modified since; their only
subsequent commit is the 2026-08-12 restructure move that put them in `attic/`.

| # | file | lines | why it went |
|---|---|---|---|
| **R1** | `attic/plotting/PlottingWizard.C` | 209 | A general-purpose plot driver ("Harry Plotter") from the pre-THnSparse era. No entry point, no recipe, no recorded run, and no document claims it as current. Every published figure comes from `run_paper_plots.sh` or `plotting/paper/make_paper_figures.py`, neither of which reaches it |
| **R2** | `attic/plotting/combinedCanvasPlots.C` | 1562 | Combined separate plots onto shared axes to de-crowd them. That job is now done inside `improvedPlotting_THnSparse.C`'s configured canvas blocks and, for the paper figures, by `plotting/paper/svgkit.py`. No consumer, no recipe |
| **R3** | `attic/plotting/ListHistos.C` | 39 | An interactive "list the histograms in this file" helper. **`rootls -l` ships with ROOT and does exactly this.** It was still recommended by `plotting/FinalAnalysis/README.md` and `plotting/PtMultiplicity/README.md` — at `plotting/ListHistos.C`, a path that stopped existing at the 2026-08-12 restructure, so the advice was already broken. Both READMEs now say `rootls` |
| **R4** | `attic/reproduceCanvasPadError.C` | 128 | A scratch reproduction of a ROOT canvas/pad error. The bug it reproduces is not recorded as open anywhere — not in `ERROR_RECORD.md`, not in `RELEASE_BLOCKERS.md`. A reproduction with no open defect is a note about a fixed problem, and git history is where notes about fixed problems live |
| **R5** | `attic/count_events/CountEvents/count_events.sh` | 34 | Driver for R6 |
| **R6** | `attic/count_events/CountEvents/count_events_bb_cc.C` | 110 | Counted events in the split bb/cc ROOT files by opening each and reading `tree`. **Superseded by `tools/campaign_status.py`**, which reconstructs the same accounting from the receipts the worker wrote, without opening a physics file — and which therefore cannot disagree with what actually ran |

> ### ⚠ WHERE THESE SIX DELETIONS ACTUALLY LANDED — read before `git log`
>
> **They are in `fc59491`, "Pre-register the six-source systematics program,
> before any job" — a commit about something else entirely.**
>
> The triage pass staged the six `git rm`s and then wrote this manifest. While
> it was writing, a **concurrent session working in the same worktree committed**,
> and `git commit` swept the staged index — including these deletions — into its
> own commit. The systematics pre-registration and six unrelated deletions are
> therefore one commit, and its message describes only the former.
>
> **Nothing was lost and nothing is wrong in the tree**: the six files are
> removed, the reference updates and this manifest are in the *following*
> commit, and `git log --follow` still reaches every deleted file. **History was
> deliberately not rewritten** — another session was actively working in this
> worktree, and rebasing shared history under a live worker trades a cosmetic
> problem for a real one.
>
> **The lesson is operational, not physical:** a staged index is shared mutable
> state between concurrent sessions in one worktree. Stage and commit in one
> step, or work in separate worktrees.

### 1.1 References updated in the same commit

Removing a file whose name survives in prose leaves a reader chasing it. Four
documents named these six and all four were corrected — in the commit carrying
this manifest, which is the one immediately after the deletions for the reason
given above:

| document | change |
|---|---|
| `plotting/README.md` §Legacy plotting | the three removed plotting macros dropped from the legacy list, with a pointer here; the survivors given their real `attic/` paths |
| `POST_SUBMISSION.md` §Chain map | the "not in the live chain" list amended, and the reason `improvedPlotting.C` was **kept** stated inline |
| `plotting/FinalAnalysis/README.md` §Practical Checks | `ListHistos.C` → `rootls -l` |
| `plotting/PtMultiplicity/README.md` §Practical Checks | `ListHistos.C` → `rootls -l` |

`docs/REPO_FILE_CENSUS.md` and `docs/RESTRUCTURE_PLAN.md` also name them. **Both
were deliberately left unedited**: they are dated documents recording what was
true when they were written, and the census is explicitly a snapshot against
`9426f38`. Editing them would falsify a record to tidy a cross-reference.

---

## 2. THE NEAR-MISSES — kept, and the reason each was kept

**These four are the point of doing this by hand.** Every one sits in `attic/`
or looks superseded, has no code-level consumer, and would be taken by a sweep
keyed on reference counts. Each has a live reason to exist that only appeared
when the entry was written.

| file | what a sweep would see | why it stayed |
|---|---|---|
| `attic/count_events/CountEvents/generated_heavy_flavor_summary.C` | in `attic/`, zero code references, last touched 2026-02 | **It generated a table that is published right now.** `Paper/Tables/generated_heavy_flavor_summary.tex` is its output, and `docs/A9_PAPER_TABLE_REGENERATION.md` cites it as the record of *what was counted*. A9 is an **open** item (`STATE.md` PENDING 7b). This is measurement-provenance sitting in a directory named for dead code |
| `attic/plotting/improvedPlotting.C` | superseded by `improvedPlotting_THnSparse.C`, in no entry point | **`POST_SUBMISSION.md` §Chain map correction 1 argues it must be kept**, from having read it: it reads `complete_root`, *the same merge product the live path consumes*, which makes it an independent cross-check rather than a predecessor. A standing recorded argument beats a reference count |
| `attic/plotting/B_Balancing_GeneralPlotting.C` | flagged in the census as a **byte-level duplicate** of the `Balancing_and_Sampling/` copy — the classic safe deletion | **The premise is false and was measured false.** The two files differ: 2217 lines vs 3051, different headers, different stated purpose. `sha256` `c41b52dc…` vs `d6e6b74d…`. The attic copy carries the original author's long explanatory header, which the other copy dropped. Deleting a "duplicate" that is not one destroys the only copy of that text — see §3 |
| `attic/split_chain/**` (18 files) | nothing calls it; no entry point since 2026-05 | **`README.md` §6 states it "remains available for independent reference samples and comparisons to older productions".** That is an owner statement of intent in a committed, current document. It is kept as one block and documented as one block in `COMPONENTS.md` |

---

## 3. CENSUS CORRECTION — D6 was never a duplicate

`docs/REPO_FILE_CENSUS.md` §4 records `B_Balancing_GeneralPlotting.C` as **"a
byte-level duplicate question"** and asks the owner to "keep one, and say
which"; `docs/RESTRUCTURE_PLAN.md` D6 rules "keep the `Balancing_and_Sampling/`
copy". **Both rest on a premise nobody measured, and it is wrong.**

```
c41b52dc…  attic/plotting/B_Balancing_GeneralPlotting.C                    2217 lines
d6e6b74d…  docs/history/studies/Balancing_and_Sampling/…GeneralPlotting.C  3051 lines
```

They are two generations of one macro, not two copies of one file. The attic
copy documents the vector-assembly procedure and the sub-sampling error estimate
in a 30-line header; the history copy replaced that header with
`// TODO: cut irrelevant parts from code`.

**Neither the census nor the plan is edited** — they are dated records. The
correction lives here and in `COMPONENTS.md`, and **D6 is withdrawn as a
question**: there is nothing to choose between, and both files stay.

> **The general lesson, which is the same one `ERROR_RECORD.md` E1 records in a
> different place:** *"duplicate" is a claim about bytes, and a claim about bytes
> is cheap to check and expensive to assume.* The census was right to flag it and
> right not to act on it; one `shasum` closed it.

---

## 4. WHAT WAS DELIBERATELY NOT REMOVED

Stated so a later sweep does not re-open settled ground.

1. **`docs/history/**`** — append-only by standing rule; out of scope for
   removal. Its publication disposition is a flagged owner decision, sized in
   the session record.
2. **`Paper/**`** — owner's.
3. **Committed anchors and their manifests** — `AnalysisScripts/anchors/**` is
   the provenance chain for every published number, and C7 depends on the probe
   anchors being byte-identical. Treated as binary.
4. **The error record** — `docs/ERROR_RECORD.md`, including every artifact it
   is *about*. `decay_parent_map_v1.json` (G5) and `per_observable.csv` (G13)
   are both marked *history — never delete*: they are the evidence for E1.
5. **The six written-unrun `Validation/` macros** — `STATE.md` lists them as a
   category of their own. Three bear on open blockers. A sweep that deletes an
   unrun measurement deletes the answer to a referee.
6. **`attic/plotting/configuration_{pT,pseudorapidity,rapidity}.json`** — data,
   not code, and the only readable record of the v2-era single-axis plot
   configurations. `STATE.md` establishes that the figures they configured are
   **permanently not regenerable** (their input dataset is gone), which makes
   the configuration the record rather than a recipe.
