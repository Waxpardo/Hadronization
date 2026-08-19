# Restructure session — 2026-08-12

**One session, on `physics-focus`. Mechanical: every decision was ruled by the
owner in advance and none was reopened.** The record of what was done; the
approved plan is `docs/RESTRUCTURE_PLAN.md`, the executed table is
[`RENAMES.md`](../../RENAMES.md).

**This file ends the handoff chain for the restructure.** It is not a handoff and
takes no `vNN`.

---

## 1. PRECONDITIONS, VERIFIED BEFORE ANYTHING MOVED

| # | condition | observed |
|---|---|---|
| 1 | `physics-focus` at `b74e588` or later, clean | **`b74e588`**, clean, suite **30/30** |
| 2 | `restructure-prep` additive only | **exactly seven `A` lines, zero non-`A`** — verified before merging, merged as `003da54` |
| 3 | live pipeline untouched | **nothing on Nikhef was contacted.** No ssh, no remote read, no job touched. Everything below is local to this repository |

---

## 2. WHAT MOVED

**186 paths by `git mv`, history preserved throughout. One deletion.**

| destination | count |
|---|---|
| `docs/history/` (handoffs, audits, cleanups, agent instructions, studies) | 87 |
| `plotting/` (was `PlottingScripts/`) | 34 |
| `generation/{producer,cards,registries,submit}` | 16 |
| `attic/{split_chain,plotting,count_events}` | 30 |
| `extraction/` | 8 |
| `analysis/` | 6 |
| `merging/` | 4 |
| **deleted** | **1** (`README.txt`, its unique sentence folded into `README.md`) |

**Top level: 30 items → 23.** Not the 18 the plan projected, because two owner
overrides kept `AnalysisScripts/` and `Validation/` under their existing names
and `attic/` is new. **Both overrides were correct** — see §4.

---

## 3. THE THREE STRUCK ROWS

| struck | override | effect |
|---|---|---|
| `AnalysisScripts/*.json` + `anchors/` → `artifacts/` | **D4** | 63 distinct repo-relative paths across 138 occurrences were left untouched, including every golden-output generator and every regeneration recipe |
| `AnalysisScripts/Generated*.h` → `analysis/contracts/` | **D4** | same reason — these are golden outputs G2–G4 |
| `Validation/` → `validation/` | **D10** | a case-only rename is a macOS/NFS corruption, not a cleanup |

---

## 4. WHAT THE MOVES BROKE — three findings

### 4.1 A frozen artifact was almost silently changed, and the digest caught it

The bulk path rewrite changed `"category_source"` inside
`AnalysisScripts/species_ordinals_v2.json` from `SimulationScripts/…` to the new
producer path. **G1's digest moved from `ccec0dbc…` to `60a2c6f2…`.**

That field is a **provenance record of where the classifier lived when the table
was built** — not a live path — and the artifact is frozen. Reverted; G1 is
byte-identical. `tools/GenerateSpeciesOrdinals.C` still emits the original
string, so a future regeneration still reproduces `ccec0dbc…`.

> **The rewrite was correct 119 times out of 120, and wrong in the one file
> where being wrong would have invalidated every downstream digest.** The
> recorded digest is what noticed. **This is the strongest argument in the
> session for why the freeze contract was written before the restructure and
> not after.**

### 4.2 The D4 override created three `../` includes

Moving the reduction and merge macros while their contract headers stayed in
`AnalysisScripts/` turned three sibling includes into `../AnalysisScripts/`
includes (`analysis/status_analysis_THnSparse_qq.C`,
`merging/MergeCanonicalAnalysis.C`). **A cost of the override, not a defect** —
and a much smaller cost than moving 63 paths.

### 4.3 One pinned checksum was legitimately re-pinned

`config/statistical_robustness_v1.json`'s `boundary_configuration_sha256`
(`6c1f33b7…` → `6bfeb9a6…`), because the rename changed `write_path` values
inside the plotting configuration it pins. **The pin exists to notice exactly
that**, so it was updated in the same commit as the rename that caused it.

---

## 5. NON-RENAME CHANGES — all ruled in advance

| # | change |
|---|---|
| **F-a** | `extraction/extract_species_decomposition.py` — `--decay-map` **required, no default**. Verified: the tool now exits non-zero with *"the following arguments are required: --decay-map"*. `extraction/pipeline/tune_extract.sh` already passed it explicitly, so the live chain is unaffected |
| **F-b** | `docs/CONTENTION_RECURRENCE_PREREGISTRATION.md` — SUPERSEDED mark, never scored, marked not deleted |
| **F-c** | the approved `kMultiplyHeavy` footnote at point of use, in `MERGED_CONVENTION_TABLES.md` §1 and `MONASH_CENTRAL_TABLE.md` §4a |
| **F-d** | the **SELECTION, not a partition** caveat promoted **above** four experiment-comparable tables |
| **F-e** | `anchors/MANIFEST.md` §3 gap list corrected — Σ_b and charm-M7 logs both anchored |
| — | `README.md` rewritten as a rebuild guide, with its false "tests run anywhere without ROOT" claim corrected |
| — | `ARCHITECTURE.md`, `STATE.md`, `RENAMES.md` written |

---

## 6. THE GATE — verbatim

**The owner's gate, unextended: suite green + derived artifacts regenerate to
recorded digests. Nothing else was added.**

### 6.1 Suite

```
make check
  ROOT: /opt/homebrew/bin/root
  30/30 passed
rc=0
```

**`ROOT:` present, so this is a real green** and not the smaller-denominator
pass a machine without ROOT reports.

### 6.2 R5 — decay-parent map v1.1

```
DECAY_PARENT_MAP species=202 with_dominant_channel=202 pythia=8.317 \
  gate=READABLE_AFTER_DISABLE map_sha256=dd502a10c5932fff
CONJUGATION artifact_rows_changed=101 table_affecting_rows=60 \
  involution_pairs=101 I1=PASS I2=PASS
```

### 6.3 R6 — decay-parent map v2

```
MAP_V2_BUILT species=202 split=2 threshold=0.1% sha256=c9593c9c0a7c4ec2
  SPLIT D*-        Dbar0=0.6770 D-=0.3230
  SPLIT D*+        D0=0.6770 D+=0.3230
```

### 6.4 Byte identity — regenerated vs committed vs recorded

| artifact | regenerated | committed | recorded in `GOLDEN_OUTPUTS.md` | |
|---|---|---|---|---|
| map v1.1 | `ed148156…` | `ed148156…` | `ed148156…` | **MATCH** |
| map v2 | `58081aa2…` | `58081aa2…` | `58081aa2…` | **MATCH** |

> **The first attempt at this check was wrong and reported a false pass.** A
> `set -- $p` inside a `for` loop does not word-split under zsh, so `shasum`
> read empty stdin and printed `e3b0c442…` — the hash of nothing — **for both
> rows, identically, which is exactly what a passing comparison looks like.**
> Redone in Python against the recorded digests. **A check that cannot fail is
> not a check** (`ERROR_RECORD.md` E2, in a new place).

### 6.5 Other pure-Python recipes over committed inputs

| recipe | output | expected |
|---|---|---|
| **R9b** charm M7 | unresolved_n 168,003 / 2,317,799 / 2,271,517; enrichment 1.53× / 1.48× / 1.45× | reproduces `M7_UNRESOLVED_SYSTEMATIC.md` |
| **R9** beauty M7 | unresolved_n 3,170 / 28,315 / 27,184; enrichment 2.23× / 1.14× / 1.15× | reproduces `M7_BEAUTY_UNRESOLVED_SYSTEMATIC.md` |
| **R10** compare_subset_parent | `SUBSET_PARENT_COMPARE flagged=30 tested=88 scale=9.9986` | the pinned **30 of 88** E4 reference set |
| **R8** second_branch_weight | `SECOND_BRANCH_DONE at_risk_pct=12.8396` | `GOLDEN_OUTPUTS.md` §2.6 merged (C) |
| **R7** apply_decay_map v2 | `TOTAL 1298655240 INVARIANCE CONSERVED`; D⁰ 25.2435, D̄⁰ 25.1707, D⁺ 13.1408, D⁻ 13.1129, B⁺ 2.3035, B⁻ 2.3024 | `GOLDEN_OUTPUTS.md` §2.5 |

**R7's `ADVISORY_FLAGGED 11`** are the particle/antiparticle ratio advisories on
the doubly-heavy and B_c bins — tens of entries against 10⁹. **Advisory by
design, not a gate**: a hard gate at ratio 1.00 would refuse real physics. They
are the same rare states the `kMultiplyHeavy` footnote is about.

**GATE: PASS.**

---

## 7. WHAT THIS SESSION DID NOT DO

- **Nothing on Nikhef.** The merge and the JUNCTIONS/CLOSEPACKING chains ran
  untouched throughout; no remote command was issued.
- **Nothing in `Paper/**`.**
- **No physics analysis, and no verification beyond the gate above.**
- **The `compare()` null-mode work and the E4 annotations** — those are the
  JUNCTIONS harvest session's first item, and it runs on this layout.
- **No read-pattern sweep**, because nothing was deleted except `README.txt`:
  everything dead went to `attic/`, which loses nothing.

---

## 8. FOR THE REVIEW

**The external review candidate is this session's final commit.** The three
documents a reviewer should open first, in order:

1. [`ARCHITECTURE.md`](../../ARCHITECTURE.md) — what is measured and how, no
   ROOT or PYTHIA assumed;
2. [`STATE.md`](../../STATE.md) — frozen / pending / written-unrun-available /
   not planned;
3. [`docs/GOLDEN_OUTPUTS.md`](../GOLDEN_OUTPUTS.md) — every published number,
   its digest, its recipe, and the seven things that cannot be regenerated.

**Two open questions are nobody's task yet** and are stated in `STATE.md`: the
unchecked double-counting factor in `ATTENTION.txt`, and whether any paper
*figure output* is digest-pinned anywhere.
