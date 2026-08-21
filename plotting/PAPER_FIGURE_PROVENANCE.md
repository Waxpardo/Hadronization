# Paper figure provenance

The current machine-readable authority is
`results/provenance/figure_acceptance_manifest_v1.json`. It records P1-P8 as
eight candidates and zero accepted figures. Older run records name external
current-campaign bytes, but this checkout lacks them. The plotting runner
disables its final sidecar recorder, and the uncertainty audit remains open.
Do not copy any entry below into a manuscript as an accepted scientific figure.

## Historical draft mapping

This maps the current working draft at
`Paper/Heavy_flavour_hadronisation_model_paper/Results.tex` to reproducible
generators. The paper directory is intentionally untracked in the main
Hadronization checkout, so the plotting branch does not overwrite it. Copy a
figure only after the corresponding Nikhef run and visual QA pass.

This table is a provisional legacy-draft map, not the final publication
index or an acceptance record. Its complete-root rows refer to the metadata-free
`21_06_2026` regression, whose full uncertainty coverage fails. The final
index must replace each input with the raw-v5 campaign, sealed central/block
manifest hashes, exact config/command, generated checksum, and reviewed paper
copy. An unresolved row blocks promotion.

| Draft result | Generator and config | Current mapped input (legacy until replaced) | Generated output | Paper copy |
|---|---|---|---|---|
| Charm angular correlations | `improvedPlotting_THnSparse.C`, full config, `draw_correlation_plots=true` | MONASH complete-root D+/D- and Lambda-c/D- OS/SS pairs | `plotting/Plots/THnSparse/Correlations/CHARMCorrelations_MONASH_PDF.pdf` | `figures/AngularCorrelations/CharmCorrelations_MONASH_PDF.pdf` |
| Beauty angular correlations | `improvedPlotting_THnSparse.C`, full config, `draw_correlation_plots=true` | MONASH complete-root B+/B- and Lambda-b/B- OS/SS pairs | `plotting/Plots/THnSparse/Correlations/BEAUTYCorrelations_MONASH_PDF.pdf` | `figures/AngularCorrelations/BeautyCorrelations_MONASH_PDF.pdf` |
| Integrated charm balancing yields | `improvedPlotting_THnSparse.C`, full config | all three complete-root tunes plus ten subsamples | `plotting/Plots/THnSparse/global_balancing_plots_integrated_charm_PDF.pdf` | `figures/YieldsBalancing/global_balancing_plots_integrated_charm_PDF.pdf` |
| Integrated beauty balancing yields | `improvedPlotting_THnSparse.C`, full config | all three complete-root tunes plus ten subsamples | `plotting/Plots/THnSparse/global_balancing_plots_integrated_beauty_PDF.pdf` | `figures/YieldsBalancing/global_balancing_plots_integrated_beauty_PDF.pdf` |
| Combined multiplicity-dependent beauty/charm yields | `improvedPlotting_THnSparse.C`, full config | all three complete-root tunes plus ten subsamples | `plotting/Plots/THnSparse/global_balancing_plots_multiplicity_PDF.pdf` | no current exact `includegraphics` match; select this combined canvas explicitly before copying |
| Multiplicity-dependent beauty/charm baryon/reference-meson balancing-yield ratios | `improvedPlotting_THnSparse.C`, full config | all three complete-root tunes plus ten subsamples | `plotting/Plots/THnSparse/global_balancing_baryon_over_meson_ratio_multiplicity_PDF.pdf` | `figures/BaryonMesonRelativeYieldsBalancing/global_balancing_baryon_over_meson_ratio_multiplicity_PDF.pdf` |
| Shared charged-multiplicity spectrum | `Plot_InclusiveKinematicSpectra_Raw.C` via `run_paper_plots.sh multiplicity-spectrum` | eventual sealed canonical raw manifest selected by `config/dataset_selector.json`; the current legacy selector is publication-ineligible and is rejected by this target | `plotting/Plots/KinematicSpectra/Multiplicity/MultiplicitySpectrum_Shared_shape.{pdf,png}` | `figures/Kinematic Plots/MultiplicitySpectrum_Shared_shape.png` |

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
correlation panels use central complete-root values with a per-`Delta phi`
bin SEM from the ten disjoint blocks. OS-minus-SS is formed inside each block
before calculating its SEM, preserving OS/SS covariance; native ROOT
projection errors are not used for those paper bars.

None of the regenerated full THnSparse canvases is ready for paper promotion.
The exhaustive real-input audit found 610 incomplete ten-subsample coverage
cases (540 beauty and 70 charm). The smoke output contains only the universally
supported `1-10%` activity class and is validation-only. The full config stays
strict and fails rather than emitting partial or placeholder errors. See
the dated private historical summary retained outside the PUBLIC export; its external
`final_thnsparse_subsample_coverage.json` artifact is not present in this
checkout, so new checksum-bound production coverage evidence is required
before copying these outputs.

The untracked draft needs a separate paper-only edit after figure promotion:

- `Results.tex:72` describes the beauty panel as charm with a D+ trigger; it
  should say beauty with B+ and Lambda-b triggers.
- `Results.tex:82` proposes a D0 trigger, while the current Paul-compatible
  full configuration uses a signed D+ trigger. This is a scientific mismatch,
  not a label-only edit, and must be resolved before the caption or
  configuration is changed.
- `Results.tex:93`, `:106`, `:127`, and `:140` still call CLOSEPACKING purple
  and JUNCTIONS red. They must use the canonical mapping above and state the
  ten-subsample SEM.
- `Results.tex:153` likewise gives stale red/purple colours and should identify
  the lower panels as numerator-tune/MONASH ratios with quadrature-propagated
  independent-tune uncertainties.
- `Results.tex:148` describes Lambda-c+/D0, whereas the configured quantity is
  the anti-Lambda-c balancing yield divided by the D- reference balancing
  yield for a D+ trigger. The final text must use the exact signed
  baryon/reference-meson balancing-yield definition.

The draft model section also remains blocked: `Model.tex:51` assigns the same
`pT >= 0.15 GeV/c` cut to every particle instead of strict trigger
`pT > 1 GeV/c` and associate `pT > 0.15 GeV/c`; `Model.tex:53` and `:129`
mislabel the status-81--89 charged multiplicity as prompt; and
`Model.tex:80--103` quote legacy 100-million-event yields without a sealed
canonical manifest. These protected paper files must be corrected only after
the final dataset and figures are frozen.

`Observables.tex:8--16` still defines a generic electric-charge
`C_{+-}-C_{++}` construction rather than the implemented signed-heavy-flavour
observable. The final methods text must define identified signed
trigger/associate channels, ordered trigger-conditional pairs with self-pairs
excluded, per-trigger normalization, the direct-primary role selections,
full-`Delta phi` OS-minus-SS integration, and the generated-registry
baryon/reference-meson balancing-yield ratio. `Observables.tex:22` currently
claims that charge, baryon number, charm, and beauty are all investigated
without identifying the actual channels. `Results.tex:159` onward is still
placeholder/legacy thesis interpretation. None of that prose is eligible for
publication until it is reconciled with the final sealed analysis.

The tune interpretation also needs substantive revision. `Model.tex:58`
implies that the configurations differ only through hadronisation, colour
reconnection, and dense-string effects, but the checked effective-setting
allowlist includes MPI `pT0Ref`, beam-remnant, `StringZ`, `StringPT`, and
`StringFlav` differences. `Observables.tex:20` suggests that close packing
changes the heavy-quark production probability even though the common
HardQCD process is held fixed; the implemented comparison primarily tests
hadronisation and species redistribution within different tune bundles.
`Results.tex:162--178` makes strong causal claims from legacy outputs, and its
`probQQ1toQQ0join` account is not consistent with the checked tune cards
(JUNCTIONS explicitly uses `0.0275,0.0275,0.0275,0.0275`,
CLOSEPACKING `0.5,0.7,0.9,1.0`, and MONASH the PYTHIA default). Final causal
language must be rederived from the Gate-B effective-settings evidence and
must not attribute a multi-parameter tune difference to one switch.

The draft also cannot pass a journal build/editorial gate in its present
protected state: `Results.tex:50`, `:73`, `:94`, `:107`, `:128`, `:141`, and
`:154` all reuse `\label{fig:placeholder}`; several captions begin with
`COMMENTS:`; line 159 says `UNDER CONSTRUCTION`; line 163 contains `[check]`;
and informal drafting phrases such as “zoom in a lot” and “improvements
ongoing” remain. The final paper-only pass must give every figure a unique
semantic label, remove drafting annotations, build without duplicate-label
warnings, and render-review every page.

These lines are intentionally not changed by the plotting commit because the
entire paper directory is untracked user work in the local main checkout.
