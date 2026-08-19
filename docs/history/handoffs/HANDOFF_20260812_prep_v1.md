# HANDOFF prep_v1 — the freeze contract is written; the restructure plan needs ONE approval pass

**Side workstream, branch `restructure-prep`, off `physics-focus` at `9426f38`.**
**Not a main-line handoff. It takes no `vNN` number** — the main line is at v47
and this document does not sit in that chain.

**Five documents added. Nothing else changed. No file was moved, renamed or
deleted; no `.gitignore` was touched; no pipeline was run; nothing was written
to Nikhef.**

---

## 0. STATE

| | |
|---|---|
| **Branch** | `restructure-prep`, new, from `physics-focus` `9426f38` |
| **Worktree** | `/Users/wax/Documents/Research/Projects/Hadronization-restructure-prep` (new; `physics-focus`'s own worktree untouched) |
| **Suite** | **30 / 30**, `ROOT: /opt/homebrew/bin/root` — a genuinely green run, not the ROOT-absent false green |
| **Code changed** | **none.** The suite was run to confirm that, not to certify anything |
| **Main line** | not touched. No watcher, sampler, chain or PID was read, listed or signalled |
| **Nikhef** | four bounded foreground `ssh` calls, **stat-only** — `find -maxdepth 1 -printf`, three `du -s`, one `df`. No contents read, nothing checksummed, no process left behind |

---

## 1. WHAT IS DONE

### `docs/GOLDEN_OUTPUTS.md` — the freeze contract, and the spine per the pivot

35 frozen artifacts with **full file sha256** computed this session, each with a
**regeneration recipe and a named positive check** — never `rc=0`. Eleven
recipes (R1–R11), a digest manifest (§7) usable directly with `shasum -c` after
path substitution, and **§5: the seven things that cannot be regenerated, with
reasons.**

Three points worth carrying:

- **The record's `dd502a10…` is the *internal* `map_sha256`, not the file's
  sha256.** A reviewer who runs `sha256sum decay_parent_map_v1_1.json`, gets
  `ed148156…`, and reports a discrepancy has found nothing. Both digests are now
  stated side by side.
- **Byte-level regeneration of the maps is claimable, not merely hoped for.**
  Both builders end `json.dumps(payload, indent=2, sort_keys=True)` with **no
  timestamp, host, path or PRNG** in the payload — verified by reading the
  construction. The one residual dependency is CPython's float repr.
- **The gate is quoted from your directive, not extended.** G-1 suite green,
  G-2 digests. Everything else in the document is labelled method.

### `docs/REPO_FILE_CENSUS.md` — 374 tracked files classified

**~232 KEEP, ~118 HISTORY, 13 deletion-candidates, 11 UNKNOWN. Zero deletions
executed.**

**The census's most important entry is a refusal to classify.** The six
`Validation/` macros with no invoker and no recorded run are marked **KEEP —
explicitly NOT deletion-candidates**. Three bear on open blockers (C8, B3), and
they are the same shape as M7: a macro written to answer a referee, never run,
so the question stayed open. A dead-file sweep that deletes an unrun measurement
deletes the answer to a referee.

### `docs/RESTRUCTURE_PLAN.md` — rewritten to the pivot, for one approval pass

30 top-level items → 18. Every top-level item mapped; 27 draft renames;
`attic/` for dead code, `docs/history/` for evidence. **§8 is a decision sheet:
ten decisions, each with a recommended default, so approval can be "defaults
except N".** Added per your directive: the three entry documents (§6, with
`STATE.md` drafted in full) and the small-N smoke path (§7).

### `docs/NIKHEF_DISK_INVENTORY.md` — metadata only

Everything under `/data/alice/ipardoza` classified keep / move / archive /
UNKNOWN, with sizes and mtimes, plus the target single-root layout.

---

## 2. THE THREE THINGS I WOULD WANT YOU TO READ FIRST

### 2.1 `tools/extract_species_decomposition.py` defaults to the **defective** decay map

`:54` sets `DECAY_MAP = AnalysisScripts/decay_parent_map_v1.json` and `:203`
makes it the `--decay-map` default. **v1 is the map that does not conjugate
antiparticle decays — E1, 17.8 pp on D⁰.**

**No existing check catches it.** `load_decay_grouping` fails closed on a digest
mismatch, but it compares `ordinal_table_digest_fnv1a64`, which is
**`646f310f78126267` in v1, v1.1 and v2 alike**. The invariance check passes too,
because conjugation errors conserve the total exactly — **E1's own stated reason
every aggregate check missed it the first time.**

**Bounded honestly:** `per_species.csv` and `per_category.csv` are
map-independent, so nothing committed is wrong. The live pipeline is safe —
`tools/pipeline/tune_extract.sh` passes `--decay-map …_v1_1.json` explicitly.
**The hazard is an interactive or reviewer invocation**, which would regenerate
the 45.95 % table with every check green.

**Not fixed here** — docs-only branch, and the fix carries a decision: should the
digest check also pin the map *schema* (`hf_decay_parent_map_v1` vs `_v1_1` vs
`_v2`)? That is yours, not mine.

### 2.2 `m7_runs/` is 840 KB on Nikhef and holds the only copy of the charm-M7 block logs

The **beauty** M7 logs were anchored into the repository. The **charm** ones were
not — so `docs/M7_UNRESOLVED_SYSTEMATIC.md`'s table currently rests on prose plus
the beauty run's P2 regression check.

**840 KB, one `scp`, closes the gap, independent of everything else.** It is the
cheapest item in this entire handoff and the only one that is both cheap and
irreversible if the scratch is ever cleared.

### 2.3 The disk is not shaped the way the plan assumed

- **`b-hadron-fractions/` is 1.2 TB** — the largest item under your data
  directory, more than half the measured total, and **a different project**, on
  a filesystem at **97 % (1.1 T free)**.
- **`Hadronization/` — the frozen checkout — is 445 GB**, of which **409 GB is
  `RootFiles/`** and **≈423 GB is gitignored working data living inside a git
  checkout**. `.git` is another 23 GB.

**Consequence:** "advance the checkout" is a ref update on a 23 GB object store;
"move the checkout" is 445 GB across NFS. Any consolidation plan that treats
relocating it as routine has mispriced it by four orders of magnitude.

---

## 3. WHAT IS UNKNOWN, AND WHY

| # | UNKNOWN | why I did not resolve it |
|---|---|---|
| **U1** | **`hadronization_analysis/` size** | walking it means `readdir` on ~3000 `per_job` slot directories, which stamps atimes under `relatime` — **corrupting the live merge's frontier probe and reporting my own walk as merge progress.** Deliberate omission, not an oversight |
| **U2** | **Is there a repo-local aggregator for the Σ_b block logs?** | ten logs are anchored and `SIGMA_B_ORDERING_AND_ADJUDICATION.md` quotes numbers from them, but I found no tool in `tools/` that consumes them the way `aggregate_m7.py` consumes the M7b logs. It may be an arithmetic derivation in a doc I did not locate. **UNKNOWN, not "missing"** |
| **U3** | **Which of the 63 hardcoded repo-relative paths fail loudly vs quietly** | I found **one** confirmed quiet failure (below) by reading. Establishing the rest means running the tools, which is a verification job — out of scope by your directive |
| **U4** | **Are the paper figures digest-pinned anywhere?** | `PAPER_FIGURE_PROVENANCE.md` exists; whether any figure *output* carries a recorded digest, I could not establish. If not, the freeze contract has a hole on the figure side |
| **U5** | **Is the split bb/cc/qq chain still needed?** | `README.txt` says it "remains available for independent reference samples"; nothing calls it. An explicit statement of intent, so I refused to call it dead |
| **U6** | **`ATTENTION.txt`'s factor of two** | records that double-counting is *not* implemented from 23 Dec onwards and results "will have to be divided by 2 manually", ending *"remains to be checked"*. **Nothing in the tree says it was.** A physics question |

**The one confirmed quiet failure (U3):**
`extract_species_decomposition.py:278` guards its decay-map read with
`if args.decay_map.exists():`. **A moved map makes the file not exist, the branch
is skipped, `decay_verdict` stays `"SKIPPED"`, and the tool exits 0 having
silently dropped the entire experiment-comparable convention.** An `rc=0` with a
missing output — the project's named recurring mode, waiting at repository scale.

---

## 4. QUESTIONS ONLY YOU CAN ANSWER

**The ten restructure decisions are `RESTRUCTURE_PLAN.md` §8, each with a
recommended default.** The two that actually change the shape:

| # | question |
|---|---|
| **D4** | **Move the golden artifacts to `artifacts/`?** Default **yes** — it is the clearest legibility win. **Overriding it to "leave them in `AnalysisScripts/`" removes the single largest risk in the plan** and is the right call if the one-session budget looks tight |
| **D2** | **The split bb/cc/qq chain → `attic/`?** Default yes. Override if the paper needs a reference sample from it |

**Outside the restructure:**

| # | question |
|---|---|
| **Q1** | `ATTENTION.txt`'s unchecked factor of two (U6) — does it touch anything published? |
| **Q2** | Should `tools/extract_species_decomposition.py`'s default map be changed, and should the digest check pin the map schema? (§2.1) |
| **Q3** | Copy `m7_runs/` into the repo as anchors before anything else moves? (§2.2) |
| **Q4** | `b-hadron-fractions/` at 1.2 TB — archivable? Worth more free space than everything else here combined |

---

## 5. FILES READY FOR THE DOCS-ONLY MERGE

All five are **new files**. **No existing file was modified.** Merging this
branch into `physics-focus` cannot change any tracked path, tool, contract or
artifact.

```
docs/GOLDEN_OUTPUTS.md
docs/REPO_FILE_CENSUS.md
docs/RESTRUCTURE_PLAN.md
docs/NIKHEF_DISK_INVENTORY.md
docs/handoffs/HANDOFF_20260812_prep_v1.md
```

**Verify before merging** — one command, and it should print exactly these five
paths with `A` status and nothing else:

```bash
git diff --name-status physics-focus...restructure-prep
```

---

## 6. FOR THE MAIN LINE — errors found in main-line documents, recorded not fixed

Per the isolation contract I did not edit these. Each is verified, not suspected.

| # | document | what is wrong |
|---|---|---|
| **M1** | `README.md` §Tests | says `tests/` holds **24** files of which **21** are `test_*.py` and "the other three are `.cpp`". Measured: **35 files, 30 `.py`, 5 `.cpp`**, suite **30/30**. Also points at `Makefile:117` for the glob; the Makefile delegates to `tools/run_tests.sh`, and **`run_tests.sh:38`** globs |
| **M2** | `README.md` §Tests | claims *"The Python tests are standard-library only and run anywhere, including with no ROOT installed."* `tools/run_tests.sh:6-7,32-34` says five tests **compile or run a ROOT macro and raise rather than skip**, and prints *"this is NOT a green run"*. **The README creates exactly the false-green the script was written to prevent.** Worth fixing before the external review regardless of any restructure |
| **M3** | `AnalysisScripts/anchors/MANIFEST.md` §3 | lists Task 2 outputs as "in flight this session; anchor them when harvested". They **are** anchored — `anchors/sigmab_raw/` holds all ten block logs |

---

## 7. COLD-READ SELF-REVIEW

Read back as someone who had not written it.

**Traps I think are handled:** that the record's `dd502a10…` is not a file
sha256 (a reviewer would otherwise report a false discrepancy);
that "superseded" is not "deletable" for `decay_parent_map_v1.json` and
`per_observable.csv`, which are the *evidence* for E1; that the six unrun
`Validation/` macros look exactly like dead files and are not; that a
`*.partial.*` cleanup sweep on `hadronization_merged/` would delete a **running
merge's output** — one such directory had an mtime minutes old when I walked it;
that `git mv` preserves every byte and still breaks every recipe naming a
directory, which is why the suite sits beside the digests in the gate.

**What I could not do, and you should know:**

1. **I verified no recipe.** Every "VERIFIED-BY-RECORD" tag cites *someone
   else's* run, and I tagged nothing VERIFIED myself. Running them was excluded
   by the brief, and I chose to keep the tag honest rather than quietly
   broaden it. **The map rebuilds (R5, R6) are pure Python over committed inputs
   and take seconds — they are the cheapest thing the next session can do to
   turn two DETERMINISTIC-BY-CONSTRUCTION claims into measurements.**
2. **The census's read-pattern sweep was not run** — deliberately. Its value is
   that it runs immediately before a deletion, not five sessions earlier. **No
   DEL? entry may be acted on without it.**
3. **`hadronization_analysis/` has no size** (U1), and that is the correct
   trade.
4. **I did not examine `Paper/`.** Out of scope by instruction, so the freeze
   contract says nothing about the paper's own artifacts.
5. **The plan's §6 entry documents are outlines, not documents.** `STATE.md` is
   drafted in full and the other two are structured; writing them is the
   restructure session's job per your directive.

**On the pivot:** it arrived mid-session, after `GOLDEN_OUTPUTS.md` and the
census were written and while the disk walk was running. I rewrote
`RESTRUCTURE_PLAN.md` completely against it — removing the phased-rollout and
extra-gate proposal I had drafted, which your ruling forbids — and revised
`GOLDEN_OUTPUTS.md` §1 to quote your gate rather than the five-condition version
I had written. **The census I left as it was: it makes no process proposal, only
a classification.**
