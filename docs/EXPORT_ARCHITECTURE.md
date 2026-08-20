# Public repository architecture — INTERNAL

This file specifies a future fresh-history export. It moves nothing and edits
no existing path.

This inventory uses commit `dacd1e4`. At that commit,
`docs/REPO_AUDIT.csv` has 807 tracked rows: 605 PUBLIC and 202 INTERNAL, with
zero PENDING.

## 1. Proposed reader tree

The owner's first requirement is a single reader-facing home for figures and
results. The clean product would have this shape:

```text
README.md
docs/
  PHYSICS.md
  PIPELINE.md
  STATISTICS.md
  SYSTEMATICS.md
  RESULTS.md
  REPRODUCIBILITY.md
  COMPONENTS.md
  TERMS.md
  [dated records and machinery documents]
results/
  figures/
  a2/
    20260813/
  systematics/
    20260817/
    20260819/
    20260820/
  validation/
    generator/
    plotting/
code/
  generation/
  analysis/
  extraction/
  merging/
  plotting/
  validation/
  tools/
AnalysisScripts/                 # immutable exception; never renamed
config/
tests/
references/
Makefile
setupEnv.sh
```

| Directory | What a reader finds there |
|---|---|
| `docs/` | The nine-document spine, dated registrations and run records, and the two machinery documents that must retain identity. |
| `results/figures/` | The three final paper figures, with no generators or rejected variants mixed in. |
| `results/a2/` | The A2 measured outputs, robustness tables, and regression sentinels grouped by measurement date. |
| `results/systematics/` | Machine-readable deltas, combinations, verdicts, and their dated rendered tables. |
| `results/validation/generator/` | Generator and event-activity validation measurements now under `ValidationReports/`. |
| `results/validation/plotting/` | Figure receipts, rendered validation canvases, and deliberately rejected variants. |
| `code/` | The executable generation-to-plotting chain, validation code, and operational tools, if every stage can move safely. |
| `AnalysisScripts/` | Frozen generated contracts, decay maps, and committed anchors under the historical name that the repository cannot change. |
| `config/` | Signed scientific contracts, selectors, registries, and local-environment templates. |
| `tests/` | Contract tests grouped separately from the executable stages they check. |
| `references/` | The PUBLIC bibliography; the INTERNAL thesis PDF is not copied. |
| repository root | The front door and the minimum build and environment entrypoints. |

This tree does **not** claim that the owner's result-location requirement is
already satisfiable. The central and block tables under
`AnalysisScripts/anchors/` are result evidence, and their directory cannot
move. Part 3 states the surviving layout without hiding that exception.

## 2. Feasibility proof

### Counting rule

The path-edit denominator is the 605 PUBLIC rows in the audit, not every file in
the private tree. INTERNAL rows are never copied and therefore cannot require
an export edit.

Each table cell below is `files / edit sites`. An edit site is a literal
repository-relative path, a quoted path segment, or a repository-root
derivation whose depth changes under the proposed move. Generated audit files
are INTERNAL and are outside the count.

Classification is strict:

1. **Resolvers** use copied paths for execution, generation, navigation, or
   current source links. The exporter may edit them.

2. **Records** state input or output locations used by completed runs. The
   exporter keeps them byte-identical and deliberately stale.

3. **Frozen files** have bytes pinned by another artifact. The exporter may
   relocate them byte-for-byte but never edit them.

A frozen mention does not automatically block a move. It blocks only when the
mention is a current resolver and the move requires changing those bytes.

### Results, evidence, documentation, and references

| Proposed mapping | PUBLIC rows moved | Resolver | Record | Frozen | Verdict and named cost |
|---|---:|---:|---:|---:|---|
| `plotting/paper/figures/` → `results/figures/` | 3 | 6 / 22 | 0 / 0 | 0 / 0 | **Feasible with a named cost.** Edit the generator default, test, and live documentation. Copy all three digest-pinned SVGs without changing bytes. |
| `docs/a2_results_20260813/` → `results/a2/20260813/` | 13 | 4 / 7 | 4 / 5 | 1 / 2 | **Feasible with a named cost.** Edit four live indexes. Leave the registered paths in the pinned systematics registration and all result records unchanged. |
| PUBLIC row under `docs/a2_evidence_20260813/` → `results/a2/20260813/evidence/` | 1 | 0 / 0 | 0 / 0 | 0 / 0 | **Feasible.** Nothing resolves the exported sentinel by its current directory. Two INTERNAL siblings are not copied. |
| `docs/a2_regression_pass_*.json` → `results/a2/20260813/sentinels/` | 2 | 2 / 4 | 1 / 1 | 0 / 0 | **Feasible with a named cost.** Update the analyzer and recorder; preserve the result record's historical path. |
| `docs/systematics_results_20260817/` → `results/systematics/20260817/` | 1 | 2 / 3 | 0 / 0 | 0 / 0 | **Feasible.** Update the systematics spine source and its contract test. |
| `docs/systematics_results_20260819/` → `results/systematics/20260819/` | 9 | 2 / 28 | 1 / 9 | 0 / 0 | **Feasible with a named cost.** Edit `SYSTEMATICS.md` and 20 path sites in `GOLDEN_OUTPUTS.md`; preserve the harvest record. Five moved data files keep their pinned digests. |
| `docs/systematics_results_20260820/` → `results/systematics/20260820/` | 15 | 2 / 16 | 1 / 2 | 0 / 0 | **Feasible with a named cost.** Edit `SYSTEMATICS.md` and ten path sites in `GOLDEN_OUTPUTS.md`; preserve the harvest record. Six moved data files keep their pinned digests. |
| `docs/plotting_validation/` → `results/validation/plotting/` | 11 | 5 / 7 | 1 / 1 | 0 / 0 | **Feasible with a named cost.** Edit five live consumers, including two sites in `GOLDEN_OUTPUTS.md`. Receipts and canvases move byte-for-byte. |
| PUBLIC `ValidationReports/` rows → `results/validation/generator/` | 5 | 29 / 39 | 2 / 3 | 5 / 6 | **Feasible with a named cost.** Edit the 29 live consumers. The six frozen provenance mentions remain stale, and the one INTERNAL report is not copied. |
| root `REPRODUCIBILITY.md` → `docs/REPRODUCIBILITY.md` | 1 | 7 / 19 | 2 / 2 | 0 / 0 | **Feasible with a named cost.** Update seven live links and preserve two run-record citations. This move is already required by the nine-document plan. |
| PUBLIC `Literature/References.bib` → `references/References.bib` | 1 | 1 / 1 | 0 / 0 | 0 / 0 | **Feasible.** One live source citation changes; the INTERNAL PDF is not copied. |

These mappings place 60 PUBLIC rows under `results/`, one under `references/`,
and the root reproducibility document under `docs/`.

`Paper/Tables/generated_heavy_flavor_summary.tex` has no move. The audit marks
it INTERNAL, so the export does not copy it or create an empty tables directory.

### Code consolidation

The proposed `code/` directory is an atomic reader feature. If the exporter
moved only the unblocked stage, it would split the chain between two naming
systems and make the tree harder to read.

| Proposed mapping | Resolver | Record | Frozen | Verdict and exact blocker |
|---|---:|---:|---:|---|
| `generation/` → `code/generation/` | 68 / 140 | 6 / 10 | 8 / 13 | **Frozen.** `AnalysisScripts/AssociateOriginCategoryContract.h` resolves `../generation/producer/HeavyFlavourUtils.h`; the established `AnalysisScripts/` freeze forbids changing it. Pinned plotting headers and the pinned reduction macro also resolve generation paths. |
| `analysis/` → `code/analysis/` | 34 / 86 | 5 / 9 | 2 / 2 | **Frozen.** `extraction/extract_species_decomposition.py` names the reduction macro and is pinned by all three deduplicated-anchor manifests. `plotting/improvedPlotting_THnSparse.C` also names it and is pinned by the polished plotting receipt. |
| `extraction/` → `code/extraction/` | 44 / 127 | 6 / 15 | 13 / 25 | **Frozen.** `decompose_with_block_sems.py` must change its repository-root derivation and self path, but its digest is pinned in `THREE_TUNE_CENTRAL_TABLE.md`. `extract_species_decomposition.py` has the same problem and is pinned by the three deduplicated-anchor manifests. |
| `merging/` → `code/merging/` | 16 / 47 | 1 / 8 | 0 / 0 | **Feasible with a named cost.** Sixteen resolver files require 47 edits; the eight run-record sites remain stale. It is not selected because a lone nested stage would defeat the `code/` grouping. |
| `plotting/` → `code/plotting/` | 84 / 359 | 7 / 32 | 10 / 31 | **Frozen.** The boundary contract names both plotting consumers and is pinned in three receipts. The plotter and two live configurations also contain current output paths while their bytes are pinned. |
| `Validation/` → `code/validation/` | 55 / 139 | 9 / 24 | 4 / 5 | **Frozen.** `CalibrateBothCountersAgainstMinBias.C` carries a live invocation path and its full digest is pinned in `SYSTEMATICS_HARVEST_RUN_RECORD.md`. The other frozen sites are historical anchor records and stay unchanged. |
| `tools/` → `code/tools/` | 138 / 350 | 5 / 31 | 14 / 27 | **Frozen.** Frozen generated headers name their generators under `tools/`; four self-path-bearing tools are pinned in `SCRATCH_RECONCILIATION.md`; the pinned reduction macro and plotter also name current tool paths. |

### Exact pinned files

The following artifacts decide the refused moves:

| Path-bearing pinned file | Pinning artifact |
|---|---|
| `AnalysisScripts/` as a namespace | `config/multiplicity_class_boundaries_v1.json` names `AnalysisScripts/anchors/b4_multiplicity_mb`; digest `3b0554fe…` is pinned by the MONASH receipt, the three-tune receipt, and the polished three-tune receipt. This proof is accepted as given and is not reopened here. |
| `analysis/status_analysis_THnSparse_qq.C` and `Validation/CalibrateBothCountersAgainstMinBias.C` | Their full SHA-256 values are recorded in `docs/SYSTEMATICS_HARVEST_RUN_RECORD.md`. |
| `extraction/decompose_with_block_sems.py` | Its digest `f05a011fbc1d6d10…` is recorded in `docs/THREE_TUNE_CENTRAL_TABLE.md`. |
| `extraction/extract_species_decomposition.py` | Digest `4cd8b6fa84935296…` is recorded in each deduplicated-tune anchor manifest and in the central and harvest records. |
| `plotting/improvedPlotting_THnSparse.C` | The polished three-tune boundary receipt stores its full `plotter_source_sha256`. |
| `plotting/CommonMultiplicityBoundaries.h` and `plotting/MultiplicityBoundaryUtils.h` | The plotting boundary receipts store their full source digests. |
| `plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse_complete_root.json` | The polished plotting receipt stores its full `configuration_sha256`. |
| `plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json` | `config/statistical_robustness_v1.json` stores its full digest. |
| `plotting/configuration_multiplicity_HF_RUN3_V1_MONASH_THnSparse_complete_root.json` | `docs/nikhef_consolidation_20260820/resolver_pin_check_20260820.tsv` records its full digest and the ruling that it was not edited. |
| `tools/archive_breach_partials.sh`, `tools/checkout_advance_guard.py`, `tools/install_checkout_guard_hook.sh`, and `tools/queue_probe.py` | `docs/SCRATCH_RECONCILIATION.md` records their tracked digests against deployed copies. |
| `docs/SYSTEMATICS_PREREGISTRATION.md` | Fourteen selector rows pin the registration digest. Its old result paths are records and remain stale. |
| The three multiplicity-boundary receipts | Their payloads and source bindings are checked by `tools/statistical_robustness.py`; the polished receipt is also pinned in `GOLDEN_OUTPUTS.md`. |

Digest pins cover several moved result objects. They do not block relocation
because the export copies their bytes unchanged:

- the three paper SVGs, pinned in `GOLDEN_OUTPUTS.md`;

- five 2026-08-19 and six 2026-08-20 systematics data files, pinned in
  `GOLDEN_OUTPUTS.md`;

- the MONASH, three-tune, and polished three-tune canvases, pinned by
  `GOLDEN_OUTPUTS.md` or their run record; and

- the plotting receipts named above.

### `GOLDEN_OUTPUTS.md`

`GOLDEN_OUTPUTS.md` is a resolver contract, not a pinned file.

An independent scan finds exactly 32 directed-result path mentions:

| Current prefix | Mentions |
|---|---:|
| `docs/systematics_results_20260819/` | 16 |
| `systematics_results_20260819/` | 4 |
| `systematics_results_20260820/` | 10 |
| `docs/plotting_validation/` | 2 |
| **Total** | **32** |

The check computed the current file digest in memory, then searched every other
tracked file for the full value and its first sixteen hexadecimal characters.
Both searches returned zero hits. This plan deliberately does not record that
digest, because doing so would create the pin it is proving absent.

The file is therefore editable. The result objects it pins remain
byte-identical while their registered paths change.

## 3. Layout that survives the verdicts

The reachable layout is:

```text
README.md
docs/                              # spine, dated records, machinery
results/
  figures/                         # 3 final SVGs
  a2/20260813/                     # results, evidence, sentinels
  systematics/{20260817,20260819,20260820}/
  validation/{generator,plotting}/
AnalysisScripts/                   # frozen name and frozen location
generation/                        # stage directories stay at root
analysis/
extraction/
merging/
plotting/
Validation/
tools/
config/
tests/
references/
Makefile
setupEnv.sh
```

The proposed `code/` directory does not survive. Six digest barriers block
stage moves. A lone `merging/` move would create two code layouts.

The result consolidation survives only for the 60 movable PUBLIC rows. It does
not absorb `AnalysisScripts/anchors/`. The owner's requirement that *all*
figures and results occupy one directory is therefore **frozen and not fully
reachable**.

The public documentation must use this sentence:

> `AnalysisScripts/` retains its historical name because the signed
> multiplicity-boundary contract and three plotting receipts freeze its anchor
> path; treat it as immutable published artifacts, not the active analysis
> stage.

The design includes no alias, duplicate, symbolic link, or generated forwarding
directory. Any such device would work around the refused rename.

### Surviving path map

The later exporter applies these mappings in longest-prefix order:

| Source PUBLIC path | Export path |
|---|---|
| `plotting/paper/figures/*` | `results/figures/*` |
| `docs/a2_results_20260813/*` | `results/a2/20260813/results/*` |
| PUBLIC `docs/a2_evidence_20260813/*` | `results/a2/20260813/evidence/*` |
| `docs/a2_regression_pass_*.json` | `results/a2/20260813/sentinels/<basename>` |
| `docs/systematics_results_20260817/*` | `results/systematics/20260817/*` |
| `docs/systematics_results_20260819/*` | `results/systematics/20260819/*` |
| `docs/systematics_results_20260820/*` | `results/systematics/20260820/*` |
| `docs/plotting_validation/*` | `results/validation/plotting/*` |
| PUBLIC `ValidationReports/*` | `results/validation/generator/*` |
| `Literature/References.bib` | `references/References.bib` |
| `REPRODUCIBILITY.md` | `docs/REPRODUCIBILITY.md` |
| every other PUBLIC path | unchanged |

## 4. Export procedure specification

A later session implements this procedure. This session does not create the
tool or an export tree.

### Inputs and refusal conditions

1. Require a clean tracked source tree and record the source commit.

2. Run `python3 tools/repo_audit.py --check` and refuse PENDING or stale rows.

3. Read `docs/REPO_AUDIT.csv` with a CSV parser. Do not parse it with shell
   field splitting.

4. Intersect the audit with `git ls-files`. Refuse a missing audit row, an
   audited path that is not tracked, or a class outside PUBLIC and INTERNAL.

5. Select only rows whose class is PUBLIC.

6. Apply the Part 3 map in longest-prefix order. Refuse a destination collision,
   a path outside the staging root, or two sources mapping to one destination.

### Copy and edit rules

1. Build into a new temporary directory on the destination filesystem.

2. Copy each selected source to its mapped destination and record source path,
   destination path, source class, source digest, and destination digest.

3. Copy every record and frozen file byte-for-byte. Refuse any digest change.

4. Apply only a versioned, explicit replacement table to resolver files. A
   replacement must name the source file, old token, new token, and expected
   occurrence count.

5. Refuse if an expected resolver token is absent or occurs too many times.

6. Update all 32 result-path sites in `GOLDEN_OUTPUTS.md`. Preserve every digest
   value for the moved objects.

7. Re-run resolver-specific contract tests in the staged tree. Do not call a
   stale record a failed link.

### Idempotence proof

The exporter never edits an existing export in place. It produces a new staging
tree, then writes a sorted manifest of destination path and SHA-256.

Run it twice from the same source commit and compare the two manifests with
`cmp`. Equality proves path and byte idempotence. Only after equality passes may
the later session atomically replace its chosen destination.

### Ghost check and INTERNAL exclusion proof

Use four sets in the proof:

| Set | Meaning |
|---|---|
| `P` | Selected PUBLIC source paths |
| `I` | INTERNAL source paths |
| `M(P)` | Mapped PUBLIC destinations |
| `A` | Regular files in the staged tree |

The exporter must prove:

```text
P intersect I = empty
copied_sources = P
A = M(P)
copied_sources intersect I = empty
```

The proof is made from sorted manifests with `comm`; counts alone are not
sufficient. This catches an omitted PUBLIC file, an extra file, a collision,
and any copied INTERNAL source.

The fresh-history ghost check then runs after the single initial commit:

```bash
test -z "$(git -C "$EXPORT" ls-files -- 'docs/history')"
test "$(git -C "$EXPORT" rev-list --count HEAD)" = 1
```

The same absence check runs for every INTERNAL path from the source audit. A
content search for old path strings is **not** a ghost check: records retain old
paths deliberately.

## 5. Effect on the documentation plan

Only the surviving path map matters. Frozen code moves create no documentation
update because they do not occur.

| Spine document | `DOC_PLAN.md` outline sections that need revised source or output paths |
|---|---|
| `README.md` | Results in one page; Repository map and evidence model; Fast path from committed evidence; Verification and expected outputs; Data availability, citation, and license; Documentation and evidence index. |
| `docs/PHYSICS.md` | Scientific question and scope; Interpretation of tune differences; Physics limitations and literature context. The last row changes `Literature/References.bib` to `references/References.bib`. |
| `docs/PIPELINE.md` | Dataflow and sources of truth; Extraction and result products; Systematic variation processing; Plotting and figure production; Promotion, failure, and schema evolution. |
| `docs/STATISTICS.md` | Quantities and units; Pooled central estimators; Nonlinear observables and covariance; Differences between independent campaigns; Systematic delta estimators; Trend summaries and fit diagnostics; Closure and integrity checks; Combination, reporting, and inferential limits. |
| `docs/SYSTEMATICS.md` | Scope, status, and notation; S1; S2; S3; S5; S6; Source selection and combination; Effect on tune separations and trend; Coverage limits and evidence index. |
| `docs/RESULTS.md` | Scope and claim hierarchy; Multiplicity dependence of balancing yields; Baryon-to-meson ratio trend; Tune separations; Result after systematic uncertainties; Auxiliary validation results; Published figures and machine-readable tables; Limits on interpretation. |
| `docs/REPRODUCIBILITY.md` | What reproducible means here; Reproduce from committed evidence; Gates, receipts, and expected verdicts; Storage and data availability. Its own destination also changes from the root to `docs/`. |
| `docs/COMPONENTS.md` | Extraction and statistics components; Plotting components; Validation components; Diagnostic and non-entrypoint components; Entrypoint index. These rows must name the new output locations while leaving code paths unchanged. |
| `docs/TERMS.md` | None. No ruled identifier or term changes under the surviving map. |

Part 2 of `DOC_PLAN.md` also needs mechanical path updates for every relocated
PUBLIC evidence row after the corresponding spine destination lands. Its
dispositions, gap list, and writing order do not change.
