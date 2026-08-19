# HANDOFF prep_v3 — MONASH absorbed, N7 closed, and one ruling collides with the freeze contract

**Read `prep_v1` then `prep_v2`. This is the delta.** Branch `restructure-prep`,
still **additive only** — seven documents, no tracked file outside `docs/`
touched, nothing moved, renamed or deleted, nothing written to Nikhef.

**The execution window is open: `b74e588` is committed, precondition 1 is met,
and the brief executes as written with no amendments.** Two things still gate
it: the §8 ruling and the 13 deletion-candidates.

---

## 1. THE ONE THING THAT NEEDS A DECISION

### The JUNCTIONS I2 recalibration lands on the function the pinned E4 test uses

**`tools/decompose_with_block_sems.py:84` is `from compare_subset_parent import
compare`.** I2 and the pinned E4 regression call **the same function**. The
standing ruling retires the binomial null "for pair counts" — and the E4
anchor-vs-parent case **is** pair counts.

**Sized rather than asserted.** `38bf707` puts the overdispersion factor at
**~4.75 in variance, σ inflated ~2.2×**. E4's set is 30 of 88 bins at |z| > 4,
largest z = +11.0 (Σ̄_b⁻) and +11.6 (Ξ*_c⁺). Under a 2.2× wider σ those two land
near **z ≈ 5.0 and 5.3 — still flagged** — while the bulk between 4 and 6 falls
below threshold. **The 30-bin set shrinks, and "30 of 88" is quoted in
`ERROR_RECORD.md` E4, `MERGED_CONVENTION_TABLES.md` §5 and
`anchors/extraction_dual/MANIFEST.md`.**

| reading of "minimal" | consequence |
|---|---|
| **(a) add the MAD null as a mode**, leave `compare()`'s binomial default | I2 gets the new null; the pinned test stays green; nothing published moves. **One commit + suite, exactly as ruled** |
| **(b) replace the null inside `compare()`** | the E4 reference set must be re-derived and re-pinned in the same commit, and three documents' quoted number changes. **Not one commit + suite** |

> **(a) satisfies the ruling as written. I flag it because (b) is the easier
> edit** — and it would rewrite the audit trail of a published error as a side
> effect, silently, since the test would simply be updated to whatever the new
> null produced. **The two are not the same change and the difference is not
> visible from the ruling's wording.**

**This does not touch the MONASH numbers.** `MONASH_CENTRAL_TABLE.md` §3 records
I3 exact and the SEMs unaffected; the misspecified null is a flagging
instrument, not an input. Full analysis: `GOLDEN_OUTPUTS.md` §2.11a; risk row
R8 in the plan.

---

## 2. WHAT WAS ABSORBED

| landed | where it went in my documents |
|---|---|
| `docs/MONASH_CENTRAL_TABLE.md` (`38bf707`) | new **`GOLDEN_OUTPUTS.md` §2.9b** — closure verdict, both convention tables with block SEMs, provenance, and the cross-check against the independent merged rebuild (they agree exactly). Added to `STATE.md`'s **FROZEN** list |
| **the overdispersion note** | **it is not a separate file** — it is **§3 of `MONASH_CENTRAL_TABLE.md`**. Recorded as such in the plan's §1.1a so nobody hunts for a file that does not exist |
| `anchors/m7_blocks/` — 10 charm logs (`b74e588`) | **G36–G45**, digests computed and frozen; **N7 CLOSED**. Added to the §7 digest manifest |
| `docs/MERGE_V3_BAND_VALIDATION.md` (`df078ad`, modified) | active `docs/`; the headroom line (1040 G avail) noted |

**No new rename rows were needed.** Every item lands inside a directory §5
already routes — which is what absorbing them "like everything else" means.

**N7's row in `GOLDEN_OUTPUTS.md` §5 is struck through, not deleted.** A gap
that was closed is part of the provenance story, and a reader arriving from an
older handoff needs to find its resolution rather than its absence.

---

## 3. THE TWO PAPER-FACING LABELS

Carried into **`GOLDEN_OUTPUTS.md` §2.9b** (prominently, in a callout beside the
tables) and into the **`STATE.md` draft** in `RESTRUCTURE_PLAN.md` §6.3:

- **`kMultiplyHeavy = 0` is BY CONSTRUCTION.** Doubly-heavy states are not
  missing from the sample; they are **not this observable's business**. **B_c is
  the separate top-class observable.** `0.0000 ± 0.0000` is not a measured zero
  and not a bug.
- **The experiment-comparable table is a SELECTION, not a partition.** Its eight
  species do not sum to 100 % and are not meant to; the diquark-structure table
  beside it **is** a partition and sums to 100.0000 %.

### 3.1 One precision note on the first label

**`MONASH_CENTRAL_TABLE.md` §4a prints `kMultiplyHeavy 0.0000`. The merged
rebuild in `MERGED_CONVENTION_TABLES.md` §1 prints the same share with a
weight of `192`** out of 1,298,655,240 — i.e. 1.5 × 10⁻⁵ %, which rounds to
0.0000.

**The label is right and I am not disputing it.** But a careful reader who
consults both documents finds "zero by construction" beside a non-zero integer,
and the two look like they disagree. **The fix is a footnote, not a change of
label:** *"0.0000 % — 192 entries of 1,298,655,240; doubly-heavy states are
classified out of this observable by construction, and B_c is the separate
top-class observable."* That states the structural claim and the residual at
once, and it is the version that survives a referee reading both tables.

**Where it should go:** `MONASH_CENTRAL_TABLE.md` §4a, at the point of use.
**Main line's file, not mine — recorded here rather than edited.**

### 3.2 The SELECTION label is present but not prominent

`MONASH_CENTRAL_TABLE.md` §4b already ends with *"These eight are a selection,
not a partition; they do not sum to 100 %."* — **as a trailing sentence after
the table.** The ruling asks for both labels stated prominently. **Suggest
promoting it to a callout above the table**, where a reader meets it before
adding the column up rather than after.

---

## 4. STILL STALE, AND THE RESTRUCTURE WILL CARRY IT FORWARD

**`AnalysisScripts/anchors/MANIFEST.md` §3** — the gap list a reviewer reads to
check provenance — is now stale in two ways:

1. it still lists Task 2 (`sigmab_runs/`) as *"in flight this session; anchor
   them when harvested"*, while `anchors/sigmab_raw/` holds all ten block logs
   (this was **M3** in prep_v1 and is unchanged);
2. it predates the charm-M7 anchoring in `b74e588`.

**One edit, while the file is already being moved** (plan §9, R7). A stale gap
list reads to a reviewer as a missing anchor.

---

## 5. STATUS

| | |
|---|---|
| branch | `restructure-prep`, seven documents, additive only |
| suite | **30/30, ROOT present** — no code changed on this branch |
| execution window | **open**; blocked only on the §8 ruling and the 13 deletion-candidates |
| open questions | Q1 (`ATTENTION.txt`'s unchecked factor of two), Q2 (are the paper figures digest-pinned?), U2 (Σ_b aggregator), U3 (loud vs quiet path failures — one confirmed quiet) |

Files for the docs-only merge:

```
docs/GOLDEN_OUTPUTS.md
docs/REPO_FILE_CENSUS.md
docs/RESTRUCTURE_PLAN.md
docs/NIKHEF_DISK_INVENTORY.md
docs/handoffs/HANDOFF_20260812_prep_v1.md
docs/handoffs/HANDOFF_20260812_prep_v2.md
docs/handoffs/HANDOFF_20260812_prep_v3.md
```

---

## 6. COLD-READ SELF-REVIEW

**The R8 flag is the one thing in this handoff that would have been expensive to
miss**, and it was found by reading `decompose_with_block_sems.py:84` rather
than by reasoning about the ruling — the import is the whole finding. **I have
not run either null**, so the "σ inflated ~2.2×" figure is arithmetic on
`38bf707`'s own stated factor of 4.75, not a measurement. **If the executing
session wants the real post-recalibration count on the E4 case, that is one
command and it should be run before choosing (a) or (b), not after.**

**On §3.1:** I am flagging a footnote on a label the owner just issued, which
risks reading as pushback. It is not — the label is structurally correct and the
192 entries do round to 0.0000. **The problem is only that two committed
documents will print "zero by construction" and "192" for the same quantity, and
a referee reading both has no way to reconcile them without asking.** That is
the class of thing this project's error record exists to catch early.

**What I still have not done, unchanged from prep_v1:** verified no recipe. The
R5/R6 gate at the restructure session will be the first execution of the map
recipes against these digests since 2026-08-11.
