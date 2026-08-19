# Merge checklist — what is gated on the merge, and how each item is verified

**Written 2026-08-18.** These items have been accumulating in owner briefs, where
they are invisible to anyone reading the repository. They are collected here so
the merge session has one list.

> **Writing this list is not executing it.** Nothing below has been done, and
> nothing below may be done without the owner's explicit authorization. The
> merge itself remains prohibited until §F is satisfied.

---

## A. Apply the class-label corrections to the committed configurations

**What:** `tools/apply_class_labels.py` regenerates the multiplicity-class legend
labels from `config/multiplicity_class_boundaries_v1.json`. The committed configs
still carry the hand-rounded **59.9** where the artifact says **59.8** (E9).

**Current drift**, measured 2026-08-18:

| configuration | stale labels |
|---|---|
| `configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse_complete_root.json` | 20 |
| `configuration_multiplicity_HF_RUN3_V1_MONASH_THnSparse_complete_root.json` | 4 |

**Verify:** `python3 tools/apply_class_labels.py` then `--check` exits 0 — status
captured **directly**, never through a pipe (`tests/test_generator_check_exit_status.py`) —
and no `59.9` remains in either file.

> ✅ **BLOCKER RESOLVED 2026-08-18** (`d63f52e`). Each generated configuration now
> declares `label_owner`, and each generator touches only its own: `--check`
> reports **exactly 24 real drifts, zero false**. Both generators share one
> formatting primitive (`tools/class_label_format.py`). **Item B is unfrozen and
> now reads: wire BOTH checks** — `apply_class_labels --check` and
> `make_variant_configs --check`.
>
> The original text is kept below because the collision is the reason the
> ownership declaration exists.
>
> ~~**BLOCKER for A and B — the two generators collide, found 2026-08-18.**~~
> `apply_class_labels.py` globs **every** `plotting/configuration_*.json`, which
> now includes the variant configurations owned by
> `tools/make_variant_configs.py`. It reports **20 further "drifts"** in
> `…_VEXTREMES.json` and, run without `--check`, would **overwrite**
> `lowest #it{N}_{ch} class, 88.2-100.0%` with a bare `88.2-100.0%` — destroying
> the derived rank wording that exists specifically to disarm the
> top-percentile inversion.
>
> **Total reported drift is therefore 44, of which only 24 are the real E9
> corrections.** Reconcile ownership before running either generator in anger:
> either `apply_class_labels.py` skips configurations carrying
> `axis_declaration` (the marker of a generated variant), or the variant
> generator becomes the sole writer of those files. **Do not wire B until this
> is settled** — it would fail the suite on drift that is not drift.

## B. Wire `apply_class_labels --check` into the suite

**What:** the generator is `--check`-able but is not in `tools/run_tests.sh`.
Confirmed 2026-08-18: no reference in `run_tests.sh`, `Makefile`, or any test.

**Why it is merge-gated:** wiring it while the committed configs still carry the
stale labels turns the suite red on a known, deliberate difference. It lands
**with** A, in the same commit, never alone.

**Verify:** a new `tests/test_class_labels_current.py` (or equivalent) runs
`--check`, the suite count rises by one, and a deliberate hand-edit of a label
fails it — **mutation-checked**, per the convention in `COMPONENTS.md` §9.

## C. Update the polish-canvas committed reference

**What:** the committed byte-reproducible reference predates the polish. Both
shas are recorded in `GOLDEN_OUTPUTS.md`.

| | sha256 |
|---|---|
| old (pre-polish reference) | `545499157bf7d4a2…` |
| new (re-rendered at merge, 2026-08-19) | `8776a1fff6a425a2…` |

> ✅ **DONE AT MERGE.** Re-rendered on the pinned stack from the corrected
> configuration, target `thnsparse-complete-root`, selector
> `config/dataset_selector_hf_run3_v1.json`. The receipt is self-consistent and
> both shas it claims were recomputed from the files they name:
> `plotter_source_sha256` `684555300d2144ba…` and `configuration_sha256`
> `22caef48362e92a7…`, `completion_status = PASS`.
>
> **The label correction moved no number.** All 132 `UNCERTAINTY_MATRIX` rows
> were compared before and after across nine fields — yields, SEMs, reference
> yields, trigger counts, block counts, coverage and statuses — with **zero
> disagreements**. The two logs print at different precision, because the
> current plotter emits 17 significant figures where the 2026-08-17 one emitted
> six, so the comparison is at the precision the less precise log records. The
> PNG changes because the legend text is drawn on it, and only for that reason.

**Verify:** re-render from merged `main` on the pinned stack, record the new PNG
sha beside the old one, and confirm the receipt's `completion_status = PASS`
with its `plotter_source_sha256` and `configuration_sha256` recomputed from the
files they name.

## D. ✅ CLOSED 2026-08-18 — the exact 17-digit V-EXTREMES vs V-FULL assertion

**What:** V-FULL's current log records ROOT's default **6** significant figures,
because it was rendered before the macro began printing at 17. The
V-EXTREMES-vs-V-FULL identity is therefore exact only *via* the closure-run leg;
against V-FULL itself it is exact only to the digits its log preserves
(`GOLDEN_OUTPUTS.md` §9.5.2).

**Closed early.** The styling mandate re-rendered V-FULL on 2026-08-18, and that
render logs 17 significant figures. The direct assertion was run against it and
reports **IDENTICAL on all 24 drawn points by exact string equality**
(`GOLDEN_OUTPUTS.md` §9.6.1).

> ✅ **ACTUALLY CLOSED AT MERGE.** The paragraph above described the data, not
> the tool. `tools/assert_variant_identity.py` still ran this leg through a
> rounded comparison, so the assertion in the repository was the weaker one even
> though the log had carried 17 digits since the re-render. The leg now uses the
> exact comparison and the rounded helper is deleted. All three legs report
> exact string equality: 24, 24 and 12 points.

**Verify:** `python3 tools/assert_variant_identity.py` against the NEW V-FULL log
reports `IDENTICAL` on all 24 drawn points by **exact string equality**, not by
the rounded comparison.

## E. Record the variant family as committed references

**What:** V-EXTREMES and V-INTEGRATED are owner-evaluation artifacts today, not
committed references.

**Point at the STYLED set** (`GOLDEN_OUTPUTS.md` §9.6): V-FULL `0cf807b6…`,
V-EXTREMES `63906e84…`, V-INTEGRATED `88fdb628…`.

**Verify:** digests in `GOLDEN_OUTPUTS.md` §9.5/§9.6 with regeneration recipes naming
`THNSPARSE_COMPLETE_ROOT_CONFIG` and routing through
`tools/render_balancing_variant.sh`; dispositions in `FIGURE_INVENTORY.md`
promoted from *awaiting owner sign-off* to *committed reference*; both receipts
`PASS`.

> **REFERENT CHANGED 2026-08-18 — this item now carries more than three digests.**
> The `FIGURE_INVENTORY.md` dispositions this item points at stopped being
> *pending* on 2026-08-18 (`f043909`): the styled family is now the **stated
> basis of four closures**, so recording it as a committed reference is what
> makes those closures citable rather than a separate tidying step.
>
> | closure | rests on |
> |---|---|
> | **REGENERATE** §3.3 integrated charm/beauty (items 4, 6) | **V-INTEGRATED** `88fdb628…` |
> | **OWNER-DECIDE** items 5, 7 (per-flavour multiplicity canvases) | **V-FULL** `0cf807b6…` |
> | **OWNER-DECIDE** item 9 (`globalCanvasYieldsPDF_215`) | **V-FULL** `0cf807b6…` |
>
> **TWO MORE FIGURES EXIST SINCE 2026-08-18, both PROPOSALS.** Neither is a
> committed reference and neither may be treated as one without owner sign-off,
> but both are now referents this item has to name:
>
> | figure | artifact | state |
> |---|---|---|
> | baryon/meson ratio per class | PNG `4d38492f…`, receipt PASS (`GOLDEN_OUTPUTS.md` §9.8) | **SIGNED OFF** as the family's fourth member; proposal until merge. Closes `FIGURE_INVENTORY.md` §3.3 and OWNER-DECIDE item 10 |
> | angular correlations, MONASH | `7238982c…` / `b426fd7f…` (§9.11) | **final** — legend fixed by measurement; §3.2 closed |
> | figure 4 | `85a2488a…` (§9.13.4) | **final** — byte-identical across renders #5, #6 and #7 |
> | the 30 species panels | §9.13.4 set | **final** — caption above the frame, pixel checker 30/30 |
>
> The correlations run also proved, byte-identically, that its extra pair
> registrations moved nothing in the balancing family, so the two configurations
> can coexist at merge without a re-verification.
>
> **Two consequences for the merge session.** (1) Items 5, 7 and 9 are superseded
> on **content**, but the manuscript still includes two per-flavour files where
> V-FULL is one canvas — the §4.1 editorial change (two `\includegraphics` lines
> and their captions replaced by one) travels **with** this item. (2) **Item 10 is
> NOT covered by the family** and must not be swept in with 5, 7 and 9: it draws
> the baryon/meson ratio, which no canvas in the family draws. It is the same
> content as the open `FIGURE_INVENTORY.md` §3.3b and is ruled with that, not here.

## F. Merge preconditions — all three, before anything above

1. **Owner's explicit authorization to merge.** Standing sign-off on figures is
   not authorization to merge.
2. **`Literature/References.bib` settled BY THE OWNER.** The main worktree holds
   uncommitted bibliography work that the merge would rewrite. It is the owner's
   file and the owner's call; no session resolves it on their behalf.
3. **Harvest state checked for collisions.** The systematics-harvest session owns
   its worktree, its condor clusters and its merges. Confirm none is mid-flight
   against the same paths before touching `main`.

## G. Queued, NOT merge-gated — post-harvest

**`merging/merge_root_files.sh:27`** — `project_base` derived as
`${HADRONIZATION_BASE:-${script_dir}}`, the **third instance** of the restructure
family in which a script infers its base from its own location and gets it wrong
once the tree moves.

**Deliberately not merge-gated:** the merge pipeline is live in another session
and this file is on its path. Touching it now would be changing a script under a
running job. **Queue it for after the harvest completes.**
