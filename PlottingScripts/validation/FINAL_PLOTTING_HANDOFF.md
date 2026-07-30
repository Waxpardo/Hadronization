# Final paper plotting handoff

Date: 2026-07-29

> Historical regression handoff. This report describes the metadata-free
> `complete_root_21_06_2026` production and the plotting-only branch before
> the raw-v5 publication pipeline. Preserve its measured coverage/SEM values
> as regression evidence, but do not treat its “canonical” wording as a
> raw-v5 publication claim. The active contracts and next actions are in
> `REPRODUCIBILITY.md` and
> `ValidationReports/PREPRODUCTION_GATE_REPORT_20260730.md`.

The historical machine artifacts named below
(`final_thnsparse_input_validation.json`,
`final_thnsparse_subsample_coverage.json`, and
`final_smoke_uncertainty_validation.json`) were retained outside this Git
checkout and are not available as repository evidence. Consequently, their
numerical summaries are a dated handoff record, not independently
reproducible proof. The publication pipeline must regenerate checksum-bound
equivalents from the final sealed raw-v5 dataset before any result is
promoted.

## Outcome

The plotting code, configuration portability, style mapping, input provenance,
strict uncertainty checks, and reduced validation path have been repaired and
tested. The full paper THnSparse workflow is **blocked by real production
coverage**, not by error-bar rendering on `main`.

The exhaustive full-config audit found 610 observables with fewer than ten
finite subsample values:

- beauty: 540 failures;
- charm: 70 failures;
- ordinary yield: 342 failures;
- baryon/meson ratio: 268 failures.

Only 468 of the 1,152 emitted yield/ratio statistics had `n=10`. The code
therefore rejects the full run. No full THnSparse figure was promoted into the
paper and the feature branch must not be merged as a claim that final figures
are reproducible from this production.

The reduced smoke selection is a validation-only result. It uses the one class
(`1-10%`) that has ten finite subsamples across every reduced tune/pair and
successfully exercises all four drawing paths.

## Repository and Paul status

- Local dirty paper checkout was left on `main` at
  `39c9cf22a723d623cc88ea683a5ea771ee98ea1c`.
- Canonical Nikhef `main` was fast-forwarded without rewriting history to
  `11884cf1ad3613e8e6997bbff32d48a3e7d89570` before validation.
- Work was isolated on `codex/final-paper-plotting-20260729`.
- `/data/alice/ipardoza/Hadronization-main` was not modified and remains the
  deterministic-seed feature checkout at
  `758a53696805231205c6adb027ff4c8cbdf12386`.
- Paul's post-rebase commit
  `10a6f098f80730374d9f827bfdf3ae97a928a030` is an ancestor of
  `11884cf1ad3613e8e6997bbff32d48a3e7d89570`; no change to Paul's branch is
  required.

## Inputs and structural validation

Audited legacy central inputs:

```text
AnalyzedData/complete_root_21_06_2026_MONASH
AnalyzedData/complete_root_21_06_2026_JUNCTIONS
AnalyzedData/complete_root_21_06_2026_CLOSEPACKING
```

Audited legacy subsample inputs:

```text
AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_MONASH
AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_JUNCTIONS
AnalyzedData/SUBSAMPLES_700/combined_root_subSamples_CLOSEPACKING
```

The unavailable external `final_thnsparse_input_validation.json` was reported
to record a passing Nikhef validation with ROOT 6.30/01:

- 56 central ROOT pair files for every tune;
- 10 subsamples for every tune and 56 ROOT pair files in every subsample;
- all configured OS/SS files exist;
- every checked file contains `summed MULTIPLICITY` (`TH1D`) plus
  `hTrKinematics`, `hAsKinematics`, and `hCorrelations` (`THnSparseD`);
- manifests are disjoint and their union covers job IDs 0--99 exactly once for
  every tune;
- all tunes have the same file inventory and schema;
- 72 representative comparisons (six final pairs, four objects, three tunes)
  show exact central-versus-ten-subsample entry/integral agreement within the
  ROOT merge tolerance.

This proves that the source partitions and merged ROOT objects are consistent.
It does not imply that every normalized per-bin yield is populated in all ten
partitions.

## Subsample coverage findings

The unavailable external machine record was named
`final_thnsparse_subsample_coverage.json`. The handoff reports that, across
every tune and associate in a trigger group, the bins with complete
yield/ratio coverage were:

| Flavour | Trigger group | Bins supported for every tune and associate |
|---|---|---|
| Beauty | `B^{+}` | integrated `00-100`, `1-10` |
| Beauty | `Lambda_b-bar` | none |
| Charm | `D^{+}` | integrated and `90-100` through `1-10`; not `0-1` |
| Charm | `Lambda_c(+)` | integrated, `30-40`, `20-30`, `1-10` |

The failures are dominated by zero trigger normalization inside individual
disjoint ten-job partitions. The audit log contains 1,781 such warnings. This
cannot be repaired by changing a marker style or error propagation formula.
Using fewer finite partitions, substituting zero error, or inserting `1e-10`
would violate the requested prescription.

## Uncertainty implementation and passing smoke evidence

`improvedPlotting_THnSparse.C` now:

- takes central values from complete-root files;
- uses sample standard deviation with `N-1`, divided by `sqrt(N)`;
- requires `N=10` finite yields for a paper error;
- forms baryon/meson ratios inside each subsample;
- combines independent tune errors in quadrature;
- uses the matching associate uncertainty in tune double ratios;
- applied identical cuts, OS/SS normalization, and the then-legacy same-sign
  factor 0.5 to central and subsample calculations. The raw-v5 ordered
  conditional central estimator now uses `same_sign_pair_factor = 1.0`; this
  historical smoke result cannot validate that corrected central definition;
- rejects non-finite denominators, non-finite errors, negative errors, and zero
  errors on non-degenerate final points;
- supports an explicit non-drawing `subsample_coverage_audit` mode;
- frees ROOT input objects and files between pairs so the exhaustive audit
  remains memory-bounded;
- initializes every optional mini pad to `nullptr` and checks it during global
  composition.

The handoff reports that the verbose reduced smoke log passed
`validate_subsample_log.py`; its external
`final_smoke_uncertainty_validation.json` is not present in this checkout:

- 30 records total (15 yield and 15 ratio);
- every record has `n=10`;
- every non-degenerate `stdError` is finite and positive;
- minimum positive SEM: `0.000233038`;
- maximum SEM: `164.482`;
- no missing files/objects, placeholder `1e-10`, NaN/infinity, or zero trigger
  normalization in the computed `1-10%` selection.

Representative SEMs:

| Flavour | Tune | Yield SEM | Baryon/meson SEM |
|---|---:|---:|---:|
| Beauty | MONASH | 150.576 | 0.000906502 |
| Beauty | JUNCTIONS | 118.932 | 0.00406401 |
| Beauty | CLOSEPACKING | 151.022 | 0.00365437 |
| Charm | MONASH | 164.482 | 0.000666226 |
| Charm | JUNCTIONS | 119.056 | 0.00105581 |
| Charm | CLOSEPACKING | 111.063 | 0.00106779 |

## Style and visual QA

`TunePlotStyle.h` remains the single source of truth:

- MONASH: black, marker 20, solid;
- JUNCTIONS: blue+1, marker 21, dashed;
- CLOSEPACKING: magenta+1, marker 22, line style 7.

The current THnSparse and three paper kinematic/multiplicity macros compile
successfully when loaded in separate ROOT batch processes. Tune-ratio curves
use the numerator tune style; legends use line-and-marker entries.

Both reduced PDFs were rendered to PNG for inspection. The ratio canvas shows
the correct tune colours/markers and visible point errors. The yield global
canvas has effectively empty/clipped pads because its multi-bin layout was
reduced to one supported class. This is acceptable only as smoke validation
and is another reason not to promote it into the paper.

## Generated artifact policy

The exact 78 stale tracked THnSparse/THnSparseCompleteRoot artifacts are listed
in `removed_tracked_plot_inventory.txt` and removed from version control.
`PlottingScripts/Plots/` is ignored. Successful validation outputs remain
generated files on Nikhef; no failed or validation-only plot is committed as a
paper result.

`PAPER_FIGURE_PROVENANCE.md` maps current `Results.tex` includes to generators
and identifies stale/legacy figures. The untracked paper directory was not
changed. In particular, no stale paper copy was overwritten with a smoke
figure.

## Commands run

```bash
./PlottingScripts/run_paper_plots.sh validate-inputs
./PlottingScripts/run_paper_plots.sh thnsparse-complete-root
THNSPARSE_COMPLETE_ROOT_CONFIG=/tmp/hadronization-smoke-verbose.json \
  ./PlottingScripts/run_paper_plots.sh thnsparse-complete-root
./PlottingScripts/validate_subsample_log.py \
  logs/final_paper_plots_thnsparse_complete_root_verbose.log \
  --json-output \
  PlottingScripts/validation/final_smoke_uncertainty_validation.json
THNSPARSE_CONFIG=/tmp/hadronization-full-coverage-audit.json \
  ./PlottingScripts/run_paper_plots.sh thnsparse
./PlottingScripts/summarize_subsample_coverage.py \
  logs/final_thnsparse_full_coverage_audit.log \
  --json-output \
  PlottingScripts/validation/final_thnsparse_subsample_coverage.json
```

The initial exact `smoke` command also completed the multiplicity-boundary and
raw kinematic stages (100 files and 100,000,000 entries per tune) before the
then-strict THnSparse stage exposed incomplete subsample coverage. The full
paper `all` target was not rerun after the exhaustive audit because its strict
THnSparse stage is proven to fail, and its earlier stages would only repeat the
same 300-million-entry raw scan.

Static validation included separate ROOT batch compilation of:

```text
PlottingScripts/improvedPlotting_THnSparse.C
PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C
PlottingScripts/Plot_KinematicSpectra_THnSparse.C
PlottingScripts/Plot_MultiplicityDistribution_PercentileBoundaries.C
```

Both JSON files pass `jq`; their activity classes remain ordered
`90-100, 80-90, ..., 1-10, 0-1`; shell/Python syntax checks and
`git diff --check` pass.

## Required next action

Produce the immutable raw-v5 equal-statistics campaign and its sealed
canonical/block manifests so every final plotted pair/bin has ten finite
trigger normalizations. Repartitioning this old production alone cannot
supply the corrected selector, stability, origin, species, and ordered-pair
contracts. After the new campaign passes Gates A--E:

1. rerun `validate-inputs`;
2. rerun `audit-subsamples` and require zero failures;
3. remove the smoke-only coverage exclusions;
4. run `smoke`, `thnsparse`, `multiplicity-spectrum`, and `all`;
5. validate the full verbose log;
6. render/inspect every final PDF/PNG;
7. copy only provenance-matched figures into the separate paper worktree;
8. then merge and fast-forward local and canonical Nikhef `main`.
