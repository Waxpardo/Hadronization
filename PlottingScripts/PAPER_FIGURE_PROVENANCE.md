# Paper figure provenance

This maps the current working draft at
`Paper/Heavy_flavour_hadronisation_model_paper/Results.tex` to reproducible
generators. The paper directory is intentionally untracked in the main
Hadronization checkout, so the plotting branch does not overwrite it. Copy a
figure only after the corresponding Nikhef run and visual QA pass.

| Draft result | Generator and config | Canonical input | Generated output | Paper copy |
|---|---|---|---|---|
| Charm angular correlations | `improvedPlotting_THnSparse.C`, full config, `draw_correlation_plots=true` | MONASH complete-root D+/D- and Lambda-c/D- OS/SS pairs | `PlottingScripts/Plots/THnSparse/Correlations/CHARMCorrelations_MONASH_PDF.pdf` | `figures/AngularCorrelations/CharmCorrelations_MONASH_PDF.pdf` |
| Beauty angular correlations | `improvedPlotting_THnSparse.C`, full config, `draw_correlation_plots=true` | MONASH complete-root B+/B- and Lambda-b/B- OS/SS pairs | `PlottingScripts/Plots/THnSparse/Correlations/BEAUTYCorrelations_MONASH_PDF.pdf` | `figures/AngularCorrelations/BeautyCorrelations_MONASH_PDF.pdf` |
| Integrated charm balancing yields | `improvedPlotting_THnSparse.C`, full config | all three complete-root tunes plus ten subsamples | `PlottingScripts/Plots/THnSparse/global_balancing_plots_integrated_charm_PDF.pdf` | `figures/YieldsBalancing/global_balancing_plots_integrated_charm_PDF.pdf` |
| Integrated beauty balancing yields | `improvedPlotting_THnSparse.C`, full config | all three complete-root tunes plus ten subsamples | `PlottingScripts/Plots/THnSparse/global_balancing_plots_integrated_beauty_PDF.pdf` | `figures/YieldsBalancing/global_balancing_plots_integrated_beauty_PDF.pdf` |
| Combined multiplicity-dependent beauty/charm yields | `improvedPlotting_THnSparse.C`, full config | all three complete-root tunes plus ten subsamples | `PlottingScripts/Plots/THnSparse/global_balancing_plots_multiplicity_PDF.pdf` | no current exact `includegraphics` match; select this combined canvas explicitly before copying |
| Multiplicity-dependent beauty/charm baryon-to-meson ratios | `improvedPlotting_THnSparse.C`, full config | all three complete-root tunes plus ten subsamples | `PlottingScripts/Plots/THnSparse/global_balancing_baryon_over_meson_ratio_multiplicity_PDF.pdf` | `figures/BaryonMesonRelativeYieldsBalancing/global_balancing_baryon_over_meson_ratio_multiplicity_PDF.pdf` |
| Shared charged-multiplicity spectrum | `Plot_InclusiveKinematicSpectra_Raw.C` via `run_paper_plots.sh multiplicity-spectrum` | `RootFiles/HF/{MONASH,JUNCTIONS,CLOSEPACKING}` | `PlottingScripts/Plots/KinematicSpectra/Multiplicity/MultiplicitySpectrum_Shared_shape.{pdf,png}` | `figures/Kinematic Plots/MultiplicitySpectrum_Shared_shape.png` |

The draft also includes the following files whose provenance is not the current
paper runner:

- `figures/YieldsBalancing/global_balancing_plots_multiplicity_{charm,beauty}_PDF.pdf`
  have no matching current output names. The full workflow now produces one
  combined canvas, while the reduced smoke output remains validation-only;
  neither should replace the two draft files silently.
- `figures/YieldsBalancing/globalCanvasYieldsPDF_215.pdf` and
  `figures/BaryonMesonRelativeYieldsBalancing/globalCanvasRelativeYieldsPDF_215.pdf`
  are legacy `Balancing_and_Sampling` products.
- The draft's two charm/beauty multiplicity-boundary PDFs are older
  flavour-duplicated copies; the current workflow produces one shared event
  multiplicity spectrum.

Paper captions for regenerated tune plots should state: MONASH
black/circle/solid, JUNCTIONS blue/square/dashed, CLOSEPACKING
magenta/triangle/line-style 7; vertical bars are the SEM from ten disjoint
subsamples. Tune-ratio curves inherit the numerator tune style. Angular
correlation panels are drawn as central-value histogram lines and do not show
the subsample SEM.

None of the regenerated full THnSparse canvases is ready for paper promotion.
The exhaustive real-input audit found 610 incomplete ten-subsample coverage
cases (540 beauty and 70 charm). The smoke output contains only the universally
supported `1-10%` activity class and is validation-only. The full config stays
strict and fails rather than emitting partial or placeholder errors. See
`PlottingScripts/validation/final_thnsparse_subsample_coverage.json`; new or
repartitioned production coverage is required before copying these outputs.

The untracked draft needs a separate paper-only edit after figure promotion:

- `Results.tex:72` describes the beauty panel as charm with a D+ trigger; it
  should say beauty with B+ and Lambda-b triggers.
- `Results.tex:93`, `:106`, `:127`, and `:140` still call CLOSEPACKING purple
  and JUNCTIONS red. They must use the canonical mapping above and state the
  ten-subsample SEM.
- `Results.tex:153` likewise gives stale red/purple colours and should identify
  the lower panels as numerator-tune/MONASH ratios with quadrature-propagated
  independent-tune uncertainties.

These lines are intentionally not changed by the plotting commit because the
entire paper directory is untracked user work in the local main checkout.
