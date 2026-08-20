# Path pins — what a rename has to move, and what it must not touch

**Written 2026-08-20 on branch `renames`, against `9a99b42`.** The inventory the
rename pass was built on. `RENAMES.md` §8 records what the pass executed.

**A path lives in more than prose.** It lives in `#include` lines, in Python
constants, in JSON fields, in shell drivers, and — the category that decides
everything below — inside artifacts whose **sha256 someone else recorded**.

---

## 1. THE RULE THIS INVENTORY EXISTS TO ENFORCE

> **A file whose digest is pinned elsewhere cannot be edited by a bulk rewrite.**
> Editing it does not update the pin. It invalidates it.

`RENAMES.md` §5.1 records the first time this happened: the 2026-08-12 bulk
rewrite changed `"category_source"` inside `species_ordinals_v2.json` and moved
G1's digest. A recorded digest caught it.

**Three kinds of pin, and only two of them are recoverable:**

| kind | example | on a content change |
|---|---|---|
| **generated** | `GeneratedSpeciesOrdinals.h`, the three paper SVGs | regenerate, re-pin. **Recoverable** |
| **recorded in prose** | `docs/MONASH_CENTRAL_TABLE.md` naming the extractor's sha | the record goes stale; a reader cannot verify. **Costly** |
| **machine-checked** | `statistical_robustness.py` comparing a receipt field to a live file | **a passing check starts failing. Not recoverable without a re-render** |

---

## 2. MACHINE-CHECKED PINS — the blocking set

Each of these compares a **committed digest** against a **live file** at run
time. Changing the file's bytes breaks the comparison.

| checker | what it pins | pinned file |
|---|---|---|
| `tools/statistical_robustness.py:668` | `receipt["plotter_source_sha256"]` | `plotting/improvedPlotting_THnSparse.C` |
| `tools/statistical_robustness.py:666` | `receipt["configuration_sha256"]` | `plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse_complete_root.json` |
| `tools/statistical_robustness.py:670` | `receipt["boundary_utility_sha256"]` | `plotting/MultiplicityBoundaryUtils.h` |
| `tools/statistical_robustness.py:672` | `receipt["common_boundary_utility_sha256"]` | `plotting/CommonMultiplicityBoundaries.h` |
| `tools/make_harvest_plot_configs.py:25` | `FROZEN_BOUNDARY_SHA` | `config/multiplicity_class_boundaries_v1.json` |
| `tests/test_dataset_selector_row_agreement.py:88` | every row's `publication_authorization_sha256` | `docs/SYSTEMATICS_PREREGISTRATION.md` (14 rows), `docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md` |

**The last one is in the contract suite**, and it is the one that stopped the
R1 attempt within a single run of `tools/run_tests.sh`.

---

## 3. FROZEN ARTIFACTS — pinned, and not regenerable here

| artifact | pinned by | what its path field records |
|---|---|---|
| `docs/plotting_validation/*/multiplicity_boundary_receipt_v1*.json` (3) | the polished one in `docs/GOLDEN_OUTPUTS.md`; all three by `statistical_robustness.py` | `boundary_source/derived_from` names where the minimum-bias data sat **when the figure was drawn** |
| `docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md` | `config/dataset_selector.json`, `config/dataset_selector_hf_run3_v1.json`, `docs/GOLDEN_OUTPUTS.md` | an owner grant. Its digest exists so the grant cannot change after the fact |
| `docs/SYSTEMATICS_PREREGISTRATION.md` | 14 selector rows | a pre-registration. Same reason |
| anchor data under `anchors/**` (`.csv`, `.log`, `.out`, `.root`) | `docs/GOLDEN_OUTPUTS.md` G-rows | nothing — **no anchor data file contains a path**, so a directory rename leaves every digest intact |

> **That last row is why R5 was safe and R1 was not.** R5 moved four CSVs and
> edited twelve documents. **Not one of the twelve has a pinned digest, and a
> `git mv` does not change content**, so G14 `74ecfb6e…` and G15 `f162686c…`
> still hold after the move.

---

## 4. RECOVERABLE PINS — generated artifacts

Regenerate, then re-pin. Never hand-edit.

| artifact | generator |
|---|---|
| `AnalysisScripts/GeneratedSpeciesOrdinals.h` (**G2**) | `tools/generate_species_ordinals_header.py` |
| `AnalysisScripts/Generated{PairRegistry,PairObjectContract}.h` | `tools/generate_registry_artifacts.py`, `tools/generate_pair_object_contract.py` |
| `plotting/paper/figures/fig{1,2,3}*.svg` | `plotting/paper/make_paper_figures.py` |
| `plotting/GeneratedClassLabelPrecision.h` | `tools/apply_class_labels.py` |

**The three SVGs stamp their source anchor paths into the drawing**, so a rename
of an anchor directory changes the figure bytes. `tests/test_paper_figures.py`
regenerates and compares, which is what proves such a change is the rename and
nothing else.

---

## 5. ORDINARY PINS — rewrite these, they carry no digest

Measured for `AnalysisScripts` across the tracked tree:

| category | files | occurrences |
|---|---|---|
| C++ `#include` and string literals | 17 | 32 |
| Python path constants | 19 | 33 |
| shell drivers | 4 | 5 |
| test constants | 15 | 24 |
| JSON fields | 20 | 20 |
| prose | 41 | 169 |
| **rewrite total** | **116** | **283** |
| `docs/history/**` — archaeology, never rewritten | 27 | 200 |
| audit artifacts — regenerated from `tools/repo_audit_rulings.json` | 3 | 259 |

**`RENAMES.md` §2 priced this row at 63 files and 138 occurrences on
2026-08-12.** The tree has roughly doubled since. The count is measured here,
not carried forward.

---

## 6. PATHS THAT ARE NOT REPOSITORY PATHS

Two categories look like path pins and are not. Neither may be rewritten.

- **`docs/nikhef_cleanup_20260820/removal_manifest_20260820.tsv`** — 31 lines
  containing `AnalysisScripts`, all of the form
  `nikhef_stale_fullprod_20260730/untracked_source/AnalysisScripts/…`. These name
  directories **deleted from `/data/alice/ipardoza`**. A rewrite would falsify the record of
  what the cleanup deleted.
- **`AnalysisScripts/anchors/e5fix_drivers/{run_extract.sh,verify_e5.py}`** —
  recorded invocations. They record the command that produced a committed
  anchor, against the paths that existed when it ran.
