# Data layout — `/data/alice/ipardoza`, and where everything actually is

**Consolidated 2026-08-17, Consolidation A.** This is the answer to *"which path
is code and which is data, and where do I find X?"*

**The consolidation is a mapping, not a migration.** The owner ruled on
2026-08-12 that big trees stay where they are: advancing the checkout is a ref
update on a 23 GB object store, but *moving* it is 445 GB across a 98 %-full NFS
volume. A table that says which path holds what costs nothing and buys the same
legibility. See `docs/NIKHEF_DISK_INVENTORY.md` §7 for the ruling and why the
price is what killed the move.

**What physically moved: 79 loose top-level files, ~1 GB, all verified.**
Everything else is documented in place.

---

## 1. THE ONE RULE

> **`hadronization/` holds things that are finished. Everything else at the top
> level is either live, frozen as evidence, or not this project.**

A directory outside `hadronization/` is there for a reason, and §4 gives the
reason for each one.

---

## 2. THE CONSOLIDATED ROOT — `/data/alice/ipardoza/hadronization/`

```
hadronization/
├── MANIFEST_20260817.sha256          79 files, post-move
├── MANIFEST_premove_20260817.sha256  82 files, pre-move — the before/after pair
├── archive/
│   ├── bundles/          17  git bundles used to ship commits to Nikhef
│   ├── outputs/          10  run outputs and logs
│   ├── binaries/          1  producer_e54b27bb_HF_PT2.bak
│   └── gate_artifacts/    1  checkout_pin.refreshed
└── scratch/
    ├── deploys/           7  deployed copies of committed tools
    ├── misc/             29  investigation scripts and their .sub files
    └── a2/               14  the A2 variation generation set
```

**Every move is sha256-verified.** `MANIFEST_premove_20260817.sha256` was taken
before anything moved, `MANIFEST_20260817.sha256` after. All **82 of 82** files
hash identically across the pair: zero lost, zero altered. The three files in the
pre-move manifest that are not in the post-move one are the live systematics
bundles, deliberately left at the top level (§4.1).

### 2.1 Two things in here that must not be "cleaned up"

- **`scratch/deploys/`** — this deploy pattern is *deliberate*. The frozen
  checkout is read and never written, so tools are deployed to scratch with
  their sha recorded. **Do not consolidate these back into the checkout.** All
  seven are sha-verified against tracked content in
  `docs/SCRATCH_RECONCILIATION.md` §2.1 and §3.
- **`archive/binaries/producer_e54b27bb_HF_PT2.bak`** — the producer binary whose
  sha `e54b27bb9e3f…` is contract **C-3**. A backup of a pinned binary is
  evidence.

---

## 3. PATH TRANSLATION TABLE

Docs written before 2026-08-17 cite the old paths. Both forms are given so an
older document remains followable.

| cited as (old) | now at |
|---|---|
| `/data/alice/ipardoza/*.bundle` | `hadronization/archive/bundles/` |
| `/data/alice/ipardoza/systematics_20260817{,b,c}.bundle` | **unchanged** — live, see §4.1 |
| `/data/alice/ipardoza/extract_species_decomposition.py` | `hadronization/scratch/deploys/` |
| `…/tune_chain.sh`, `…/tune_extract.sh` | `hadronization/scratch/deploys/` |
| `…/queue_probe.py`, `…/checkout_advance_guard.py` | `hadronization/scratch/deploys/` |
| `…/install_checkout_guard_hook.sh`, `…/archive_breach_partials.sh` | `hadronization/scratch/deploys/` |
| `…/a2_make_subs.py`, `…/a2_make_largest_index_variation.py` | `hadronization/scratch/a2/` |
| `…/a2_*.sub`, `…/a2_*_submit.log`, `…/a2_*.pre_guard_removal` | `hadronization/scratch/a2/` |
| `…/status_analysis_THnSparse_qq_A2.C` | `hadronization/scratch/a2/` |
| `…/patch_variation.py` | `hadronization/scratch/a2/` |
| `…/scaling_*.sh`, `…/proj6iii*.sh`, `…/pool*.sh` | `hadronization/scratch/misc/` |
| `…/f3_gate.sh`, `…/f3_step2.sh`, `…/run_gate.sh` | `hadronization/scratch/misc/` |
| `…/validate_one.sh`, `…/validate_34.sh`, `…/verify_merge.sh` | `hadronization/scratch/misc/` |
| `…/rerun_closure.sh`, `…/run_closures.sh`, `…/diag_closure.sh` | `hadronization/scratch/misc/` |
| `…/run_merge_instrumented.sh`, `…/summarize_merge.py`, `…/rss_curve.sh` | `hadronization/scratch/misc/` |
| `…/chain_path_proof.sh` | `hadronization/scratch/misc/` |
| `…/*.sub` (non-A2) | `hadronization/scratch/misc/` |
| `…/hf_pt2_int_cpu.txt` | `hadronization/archive/outputs/` |
| `…/bimodality*`, `…/condor_*`, `…/compile_hf.log`, `…/merge_launch.out` | `hadronization/archive/outputs/` |
| `…/FlavourClosure_Dplus.png`, `…/tune_runs_three_driver.log` | `hadronization/archive/outputs/` |
| `…/producer_e54b27bb_HF_PT2.bak` | `hadronization/archive/binaries/` |
| `…/checkout_pin.refreshed` | `hadronization/archive/gate_artifacts/` |

> **`hf_pt2_int_cpu.txt` is not junk.** It is the basis of the **562.5
> CPU-hours** figure in `REPRODUCIBILITY.md` §6.

---

## 4. DOCUMENTED IN PLACE — nothing moved

### 4.1 LIVE — do not touch until the systematics campaigns are harvested

| path | role |
|---|---|
| `systematics_deploy/Hadronization` | ⛔ the pinned deploy at `72ca4e39`. Every in-flight job verifies this commit at startup and refuses a tree with tracked modifications |
| `systematics_deploy/nch_recal_8317/` | the 8.317 decay-policy re-measurement log |
| `systematics_regression/` | the nominal-reproduction gate's evidence, deliberately outside the production root so it can never be merged |
| `hadronization_production/HF_SYS_*` | live production output, growing toward ≈ 193 G |
| `systematics_20260817{,b,c}.bundle` | left at top level: archivable only **after** convergence |

### 4.2 FROZEN — evidence that reading or moving would damage

| path | why |
|---|---|
| `merge_runs/` | **N2** — the merge timing evidence *is* the filesystem mtimes. Clearing or rewriting them destroys the only basis for scoring the 65–77 h band |
| `archive/` | the 34 breach partials — *moved, never deleted*, with a committed manifest. **Distinct from `hadronization/archive/`**, and not merged into it for exactly that reason |
| `a2_runs/` | holds `held_evidence_20260813/` and `permissive_guarded_22120383/` — the **E7** evidence `config/a2_variations_v1.json` points at by sha |
| `quarantine/`, `seed_ledger_archive/` | as named |
| `Hadronization-full-production/campaigns/*/seed_ledger.jsonl` | 3557 burned seeds; nothing re-derives historical seeds |

### 4.3 BIG — stay put by ruling

| path | size | role |
|---|---|---|
| `Hadronization/` | **445 G** | the analysis checkout. 423 G of that is gitignored working data (`RootFiles/` 409 G); `.git/` alone is 23 G |
| `hadronization_production/` | **495 G** | raw campaign output, of which **195 G is `HF_SYS_*`** (see below) |
| `hadronization_analysis/` | **94 G** | per-job analysis output |
| `hadronization_merged/` | **88 G** | the merged central and subsample sets behind every current number |
| `a2_runs/` | **25 G** | see §4.2 — frozen |
| `Hadronization-full-production/` | 5.6 G | holds the seed ledgers |
| `pythia_stock_8317/` | 317 M | the pinned generator — `REPRODUCIBILITY.md` §4's biggest portability weakness |

> ### `hadronization_analysis/` finally has a size: 94 G
>
> The 2026-08-12 inventory recorded, as a deliberate choice rather than an
> oversight, that this tree had **no size**: walking it meant `readdir` on ~3000
> live slot directories, which would have stamped fresh atimes under `relatime`,
> corrupting the merge's frontier probe and reporting the walk itself as merge
> progress (`PROGRESS_PROBE_METHOD.md` §4). **The merge completed 2026-08-17
> 16:16 CEST, so the walk is now safe, and it was done.** This closes the one
> acknowledged gap in that inventory.

**The `HF_SYS_*` breakdown, measured 2026-08-17 18:5x** — seven campaigns, all
still writing:

| campaign | size | | campaign | size |
|---|---|---|---|---|
| `HF_SYS_MUR_UP` | 28 G | | `HF_SYS_PDF_CTEQ6L1` | 28 G |
| `HF_SYS_MUR_DOWN` | 27 G | | `HF_SYS_PTHAT_1` | 25 G |
| `HF_SYS_MUF_UP` | 29 G | | `HF_SYS_PTHAT_4` | 32 G |
| `HF_SYS_MUF_DOWN` | 26 G | | **total** | **195 G** |

**Costed in advance at ≈ 193 G.** The measurement lands within 1 % of the
pre-registered estimate.

### 4.4 NOT THIS PROJECT

`b-hadron-fractions/` (1.2 T, **out of scope by ruling — untouched**), `HRP/`,
`HRP_clean/`, `Axions/`, `EDMs/`, `.vscodium-server/`,
`Hadronization-Tune-Integration/`.

---

## 5. THE FILESYSTEM, AND THE HEADROOM

| measured | value |
|---|---|
| filesystem | `data-02:/alice`, 32 T |
| **2026-08-12** | 1.1 T available, 97 % used |
| **2026-08-17 12:0x** | 995 G available, 97 % used |
| **2026-08-17 18:3x** | 805 G available, 98 % used |
| **2026-08-17 18:5x** | **788 G available, 98 % used** |

**The systematics campaigns are consuming headroom in real time** — roughly
190 G between the morning and evening readings of the same day, against the
≈ 193 G the program was costed at. That is the campaign landing as predicted,
not a leak.

> **The consolidation did not free space and was never going to.** It moved
> ~1 GB of loose files into a legible structure. The space question on this
> volume is `b-hadron-fractions/` at 1.2 T, and that is not this project's
> decision.
