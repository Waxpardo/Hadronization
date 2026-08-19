# HANDOFF prep_v2 — the owner's rulings, folded in; the disk plan is now a map, not a move

**Read `HANDOFF_20260812_prep_v1.md` first. This is the delta.**
Side workstream, branch `restructure-prep`. **Still additive only** — six
documents now, no existing tracked file modified, nothing moved, renamed or
deleted, nothing written to Nikhef.

**Seven rulings landed after prep_v1 was committed. Four of them closed
questions prep_v1 had to leave open; one reshaped the disk plan entirely.**

---

## 1. WHAT EACH RULING CHANGED

| ruling | what moved in the documents |
|---|---|
| **Contention pre-registration: superseded-mark in the restructure pass, never scored** | new step **F-b** in the execution order (`RESTRUCTURE_PLAN.md` §1.2, §4.1); census now classifies the doc **KEEP — mark superseded**, explicitly *not* delete; `STATE.md` draft lists it under NOT PLANNED with the reason |
| **`extract_species_decomposition.py`: v1 default is a reproduction hazard — remove the default, make `--decay-map` required. One line + suite** | new step **F-a**; `GOLDEN_OUTPUTS.md` F1 now carries the ruling instead of "the owner's call"; census row updated |
| **Charm M7 logs: main line `scp`s after the MONASH harvest, sha beside the beauty anchors** | `GOLDEN_OUTPUTS.md` §2.7 and **N7** are now **ASSIGNED** — the only row on the not-regenerable table with a scheduled closure |
| **R5/R6 run during the acceptance gate — they *are* the gate for the maps** | new `GOLDEN_OUTPUTS.md` §1.1; execution step 7 states the three expected lines verbatim. **This is what promotes G6/G7 from DETERMINISTIC-BY-CONSTRUCTION to measured** |
| **Consolidation reshaped: no physical checkout move, mapping-based code/data separation, big trees stay, `b-hadron-fractions` out of scope** | `RESTRUCTURE_PLAN.md` §10 **rewritten**; `NIKHEF_DISK_INVENTORY.md` gains §7 and a header warning that §2/§3's "MOVE" tags predate the ruling |
| **Unrun `Validation/` macros stay; `STATE.md` lists them written-unrun-available** | new fourth category in the `STATE.md` draft, with all six and the blocker each bears on; they are **out of** NOT PLANNED, where prep_v1 had wrongly filed them |
| **Restructure executes after the MONASH harvest; §8 and the 13 deletion-candidates are being ruled next** | `RESTRUCTURE_PLAN.md` §1.1 carries the window and the approval status; §8 and the census totals say *with the owner* |

---

## 2. THE DISK RESHAPE IS THE BIG ONE

**The inventory's job was to price the move. The price is what killed it.**

Relocating the frozen checkout means **445 GB across NFS on a volume at 97 %** —
of which **423 GB is gitignored working data that was never in the repository**
and **25 MB is source**. The checkout is **0.006 % code by volume.**

**So the consolidation is now a document.** `RESTRUCTURE_PLAN.md` §10.2 is a
role → path table saying which path is code, which is data, which is archive and
which is out of scope. It buys the same legibility for zero bytes moved.

**What is physically left: under 1 GB** — the ~70 loose top-level files into
`scratch/misc/`, `scratch/deploys/` and `archive/bundles/`. Two things must not
be swept up in that: the **seven scratch-deployed copies of committed tools**
(the deploy pattern is deliberate — the frozen checkout is read, never written)
and **`producer_e54b27bb_HF_PT2.bak`**, the backup of the binary whose sha is
contract C-3.

---

## 3. ONE PIECE OF ENGINEERING INFORMATION ON THE RULED FIX

**The ruling on F-a is right and I am not re-litigating it.** One thing the
executing session should see before it opens the file, because it is four lines
of context away from the edit:

`:203` is the ruled change — `default=DECAY_MAP` → `required=True`, and the help
string still says `decay_parent_map_v1.json`, so it goes too. **That closes the
hazard named: silently using v1.**

`:278` is `if args.decay_map.exists():`. **With the argument required, a
mistyped or stale path still takes the false branch** — `decay_verdict` stays
`"SKIPPED"`, the experiment-comparable convention is silently absent, and the
tool exits **0**. Same function, already open in the editor; making the call
unconditional turns a silent skip into a fail-closed read.

**Flagged, not mandated. Executor's call, and no ceremony either way.**

---

## 4. WHAT IS ASSIGNED TO WHOM NOW

| item | owner |
|---|---|
| `scp` of `m7_runs/` after the MONASH harvest, sha recorded | **main line** |
| one `df` on the merge target volume (~60 GB remaining), one line recorded | **main line** |
| ruling on §8's ten decisions and the 13 deletion-candidates | **owner, next** |
| F-a, F-b, `git mv`, entry documents, the gate | **restructure session**, after the MONASH harvest |
| everything in this branch | **done** |

**On the `df`:** not run here — it is assigned, and it is a live-pipeline
observation. **A prior, so that check is a confirmation rather than a
discovery:** `df -h /data/alice` during this session's metadata walk returned
**32 T, 31 T used, 1.1 T available, 97 %**. That is comfortable against ~60 GB —
but the reading is hours old on a shared filesystem with another user active,
which is exactly why a fresh one was asked for.

---

## 5. WHAT IS STILL OPEN

Two questions, both untouched by the rulings, both stated in
`RESTRUCTURE_PLAN.md` §8.1:

| # | question |
|---|---|
| **Q1** | `Balancing_and_Sampling/ATTENTION.txt` — double-counting is *not* implemented from 23 Dec onwards, results "will have to be divided by 2 manually", ending *"remains to be checked"*. **Nothing in the tree says it was.** A physics question, separate from the restructure |
| **Q2** | **Are the paper figures digest-pinned anywhere?** If not, the freeze contract has a hole on the figure side that `GOLDEN_OUTPUTS.md` cannot close by itself |

Plus the two UNKNOWNs the rulings did not reach: **U2** (is there a repo-local
aggregator for the Σ_b block logs?) and **U3** (which of the 63 hardcoded paths
fail loudly vs quietly — one confirmed quiet, §3 above).

---

## 6. FILES FOR THE DOCS-ONLY MERGE — now six

```
docs/GOLDEN_OUTPUTS.md
docs/REPO_FILE_CENSUS.md
docs/RESTRUCTURE_PLAN.md
docs/NIKHEF_DISK_INVENTORY.md
docs/handoffs/HANDOFF_20260812_prep_v1.md
docs/handoffs/HANDOFF_20260812_prep_v2.md
```

`git diff --name-status physics-focus...restructure-prep` must print exactly
these six with `A` and nothing else.

**Suite: 30/30, `ROOT` present.** No code changed on this branch.

---

## 7. COLD-READ SELF-REVIEW

**On prep_v1's one substantive error:** I filed the six unrun `Validation/`
macros under **NOT PLANNED** in the `STATE.md` draft while simultaneously arguing
in the census that they are the most valuable files in that directory and must
not be deleted. **Those two positions do not sit together** — "not planned"
invites exactly the sweep the census warns against. The ruling supplies the
category that was missing (*written — unrun — available*) and the draft now
carries it. **The census was right and my own draft contradicted it; the
contradiction was mine to catch and I did not.**

**On the disk section:** prep_v1 proposed physically relocating everything into
a `hadronization/` root, and did so **in the same document that reported the 445
GB and the 97 % full volume**. The measurements that refute the proposal were
already in my own text. **I gathered the number that killed the plan and then
did not apply it to the plan** — the ruling did. `NIKHEF_DISK_INVENTORY.md`'s
superseded "MOVE" tags are left in place rather than rewritten, because the
record of what was proposed before the pricing is the useful part.

**Unchanged from prep_v1, and still true:** I verified no recipe. Every
VERIFIED-BY-RECORD tag cites someone else's run. The R5/R6 ruling means the
restructure session's gate will be the first time the map recipes are actually
executed against these digests — which is the right place for it, and it is
worth knowing that **nobody has run them since 2026-08-11.**
