# Figures — G1 to G9 and T1

One row per deliverable: what produces it, what it writes, and the name the
manuscript expects. The byte-exact delivery names and their Overleaf paths are
in [../paper/DELIVERABLES.md](../paper/DELIVERABLES.md).

| id | content | producer | output stem |
|---|---|---|---|
| G1 | N_ch spectrum, three tunes, tunes/MONASH ratio pad, MONASH percentile inset | `DrawMultiplicityOverlayWithRatio` (`plotting/Plot_InclusiveKinematicSpectra_Raw.C:1795`; ratio pad `:1815`; inset `:1670`, `:1865`), reached by target `multiplicity-spectrum` | `MultiplicitySpectrum_Shared_shape` (`:2192`) |
| G2 | MONASH charm angular correlations, 2×2 pads | the hard-coded canvas of V-CORRELATIONS (`plotting/improvedPlotting_THnSparse.C:4299-4301`) | `CHARMCorrelations_MONASH` |
| G3 | MONASH beauty angular correlations, 2×2 pads | the same canvas, `FLAVOUR = BEAUTY` | `BEAUTYCorrelations_MONASH` |
| G4 | integrated charm balancing yields | V-INTEGRATED global | `global_balancing_plots_integrated_charm` |
| G5 | charm balancing yields on classes 0–1 % and 90–100 % | V-EXTREMES global | `global_balancing_plots_multiplicity_charm` |
| G6 | integrated beauty balancing yields | V-INTEGRATED global | `global_balancing_plots_integrated_beauty` |
| G7 | beauty balancing yields on classes 0–1 % and 90–100 % | V-EXTREMES global | `global_balancing_plots_multiplicity_beauty` |
| G8 | baryon/meson balancing-yield ratio against multiplicity | V-BARYONMESON global | `global_balancing_baryon_over_meson_ratio_multiplicity` |
| G9 | kinematic spectra, ten species × {pT, η, φ} | target `kinematic-spectra` (`plotting/Plot_InclusiveKinematicSpectra_Raw.C:2196-2221`) | `Inclusive_pT_<species>_shape`, `Inclusive_eta_<species>_shape`, `Inclusive_phi_<species>_shape` |
| T1 | generated-sample table | `tools/count_generated_sample.C` and `tools/read_merged_event_counts.C` | a JSON of counts and a TeX table body |

## The `_PDF` suffix is the writer's, not the manuscript's

`writeCanvasToFiles` writes three files per canvas and appends a format tag to
each stem: `<stem>_PDF.pdf`, `<stem>_PNG.png`, `<stem>_MACRO.C`
(`plotting/improvedPlotting_THnSparse.C:1329-1331`). Every balancing
delivery name in the manuscript therefore carries `_PDF` before its extension.
G1 is the exception: `paper/Model.tex:128` includes the `.png`.

## G9's ten species

`Species()` (`plotting/Plot_InclusiveKinematicSpectra_Raw.C:849-862`) returns, in
order: `Bplus`, `Bminus`, `Lambdab`, `Lambdabbar`, `Sigmabzero`,
`Sigmabzerobar`, `Dplus`, `Dminus`, `Lambdacplus`, `Lambdacplusbar`. Three
observables each gives thirty G9 stems.

## Two hazards that cost a render

**Silent overwrite.** Promotion is `::rename` (`plotting/StagedOutputs.h:123`).
A second render of the same stem replaces the first without a record. Render
each stem once per session and enumerate the delivery directory afterwards.

**A refused y-window.** The generator sets hard y-limits per trigger column and
`SetPlotPointOrThrow` (`plotting/improvedPlotting_THnSparse.C:2972`) aborts the
render when a class leaves the window rather than clipping it. That refusal is correct and it is not repairable at render
time: widening the range is a generator edit and a fresh configuration version,
then a re-render (finding F63).
