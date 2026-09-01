# Style — the five configurations, the generator's seams, and the recorded debt

Ruling R45 made one session responsible for the figure style. Ruling R46 fixed
how a figure identifies itself. This page states where each style decision
lives, so a reader who wants to change one knows which file to open. Every
anchor was read at HEAD `6729b3f`.

The rule that governs the whole layer: **the generator owns the decision, the
macro owns the drawing.** A wording, a window or a switch is a constant in
`tools/make_variant_configs.py`; the macro reads it out of the generated JSON.
Editing a rendered configuration by hand puts it out of step with its
generator, and `python3 tools/make_variant_configs.py --check` then fails.

## The five generated configurations

`tools/make_variant_configs.py` writes five documents and nothing else writes
them. `--check` reports `VARIANT_CONFIGS_CURRENT files=5`, and it passes at
this HEAD.

| configuration | panels | global canvas write name | output directory |
|---|---:|---|---|
| `…_VINTEGRATED.json` | 16 | `global_balancing_plots_integrated_beauty`, `…_charm` | `plotting/Plots/VariantIntegrated` |
| `…_VEXTREMES.json` | 16 | `global_balancing_plots_multiplicity_beauty`, `…_charm` | `plotting/Plots/VariantExtremes` |
| `…_VBARYONMESON.json` | 4 | `global_balancing_baryon_over_meson_ratio_multiplicity` | `plotting/Plots/VariantBaryonMeson` |
| `…_VCORRELATIONS.json` | 10 | `…_VCORRELATIONS_POLISH_PROPOSAL` | `plotting/Plots/VariantCorrelations` |
| `…_VINTEGRATED_CLOSURE.json` | 10 | `…_VINTEGRATED_CLOSURE_POLISH_PROPOSAL` | `plotting/Plots/VariantIntegratedClosure` |

The delivery names of the five composites are pinned by
`tests/test_delivery_names.py`, which compares strings from the generated JSON
and never the filesystem. G1, G2, G3, G9 and T1 sit outside that gate; see
[../paper/DELIVERABLES.md](../paper/DELIVERABLES.md).

## The generator's four seams

**`ASSOCIATE_SETS`** (`tools/make_variant_configs.py:264-275`) carries two
named associate sets, `legacy` and `legacy_sigma`, with
`DEFAULT_ASSOCIATE_SET = "legacy"`. A wider set emits a new configuration
version rather than overwriting the paper's. `CLOSURE_ASSOCIATE_SET = None`
(`:294`) holds the closure configuration on the base four series — B⁺→B⁻,
B⁺→Λ_b, D⁺→D⁻, D⁺→Λ̄_c⁺ — with the reason written beside it (`:277-293`):
a widened closure derives 48 identities and a 576-row render, a shape no
accepted log carries, and the 144/132 contract stops being checkable.

**`RATIO_PANEL_Y_TITLE = "ratio to MONASH"`** (`:607`) is the one place every
balancing ratio panel's y title is written. The reason is measured, not
stylistic: the previous 29-to-37-character wording renders complete only to
about 18 px against a 33 px metric (`:594-606`). The panels the constant
reaches are named by the macro's own dispatch keys in
`RATIO_PANEL_DRAW_FUNCTIONS` (`:613-616`), never by matching title text.

**`DRAW_CANVAS_TITLES = False`** (`:641`) is ruling R46's switch. FIG-1C built
it so the decision is one constant, and R46 flipped that constant rather than
deleting the five title sites. The macro defaults the key to `true` when it is
absent (`plotting/improvedPlotting_THnSparse.C:3203`), so the frozen base and
the four hand-maintained configurations parse and render unchanged. A `false`
value hands the empty string to the four template sites
(`:5260`, `:5568`, `:5879`, `:6200`) and to the correlation title (`:5007`).

**The nine y windows** (`:686-913`) are per trigger column, because
baryon-trigger yields differ in magnitude from meson-trigger yields. Each
window is stated with the measured envelope it must hold and the source that
measured it. `COLUMN_WINDOW_GUARDS` (`:919-950`) pairs every window with its
envelope, and the loop at `:952-956` raises before any document is built when a
window does not contain its own envelope. That guard exists because
`SetPlotPointOrThrow` (`plotting/improvedPlotting_THnSparse.C:3760`) refuses a
point outside the configured axis rather than cropping it, so a bad window
stops a render at the deployment instead of quietly clipping a paper figure.

## The macro's style pass

The macro carries its own map of where each style decision lives
(`plotting/improvedPlotting_THnSparse.C:1701-1744`). Measured at this HEAD:

| decision | where it is made |
|---|---|
| text sizes | `kPublicationLabelFraction` / `kPublicationTitleFraction`, applied by the one pass at `:6586` |
| titles | the generator's constants, parsed at `:3472` |
| axis offsets | chosen in `ApplyPublicationAxisStyle` (`:1759`) |
| legend rectangles | parsed at `:3495`, built per draw function, first at `:5317` |
| dashed reference at 1 | `:1552` |
| panel titles on or off | `draw_canvas_titles`, parsed at `:3203` |

Ruling R46's identification scheme, as the macro implements it: the generator
and beam energy go to the information block, drawn by `DrawInformationBlock`
(`:2137-2167`); the trigger, or the flavour on the baryon/meson and closure
canvases, goes to a column header (`DrawColumnHeaders`); the tune goes to an
in-frame row label (`DrawPanelLabel`); and the conventions the panels share go
to one canvas legend, top right and outside every pad (`DrawCanvasLegend`).
The caption carries the rest.

**`panel_label` is not emitted by every configuration, and that is correct.**
`apply_panel_labels` (`tools/make_variant_configs.py:2045-2063`) derives the row
label from the panel's own tune list, and a row that does not vary by tune takes
no label. V-BARYONMESON declares four `panel_label` keys and none of them is
non-empty, so its render prints zero `PANEL_LABEL` lines while the other four
configurations print exactly as many as they declare. A gate that asks for at
least one label on every configuration is wrong; a gate that counts each
configuration's own declared labels is right (RUN-N4b report, finding 1).

## Two pieces of recorded debt

Both are stated in the macro itself and neither is repaired. They are
post-paper work.

**Four near-duplicate draw functions.** `drawBalancingPlots` (`:5199`),
`drawBalancingPlotsTUNERatios` (`:5506`),
`drawBalancingBaryonMesonRatioPlots` (`:5811`) and
`drawBalancingBaryonMesonRatioPlotsTUNERatios` (`:6129`) each carry their own
copy of the title, legend and style block — the four template sites at `:5260`,
`:5568`, `:5879` and `:6200`. A style change therefore has to be made four
times, and the render dispatches to them by name at `:6542`, `:6546`, `:6550`
and `:6554`.

**A line-style ladder that never runs.** `MultiplicityClassLineStyle`
(`:4023-4039`) matches an object name against the prefix `hDPhic` and falls
through to `return 1`. Every tracked configuration names its bins
`hDPhiM<lo>_<hi>` — measured across all five V-configurations, zero objects
carry the `hDPhic` prefix — so the function returns 1 for every bin it ever
sees and both extreme classes draw solid. `plotting/TunePlotStyle.h:52-59`
records the same fact and states why it is not repaired: giving eleven line
styles to every canvas that draws eleven classes is a change no checklist item
asks for. Class identity on the extremes canvases is carried by marker fill
instead (`plotting/TunePlotStyle.h:38-50`).
