# Deliverables — the byte-exact name manifest

**Ruling R38.** The paper lives in Overleaf. The repository's obligation ends at
producing every figure and result ready for the owner to drop in: correct
content, correct statistics, and byte-exact filenames. No repository gate builds
or validates the manuscript.

## The pin these names come from

The names below are read from the 2026-08-30 `paper/` snapshot, which is a
**pin, not a live document** (finding F62). Its digests, verified by
`shasum -a 256` at HEAD `f44e038`:

| file | sha256 |
|---|---|
| `paper/Results.tex` | `1d88f96dd775ac572649a1486029603b47c06e6c01b5d0bf0ab6e06fa800e000` |
| `paper/Model.tex` | `db96a959921ea33c3246dcaec89ac2240396214de43087d6211f13305e7538e5` |

The live Overleaf document may have moved since. The handoff package therefore
carries this manifest as an **owner-facing checklist against Overleaf**, not as
a gate.

## The manifest

| id | Overleaf path | producer name | source |
|---|---|---|---|
| G1 | `figures/Kinematic Plots/MultiplicitySpectrum_Shared_shape.png` | stem `MultiplicitySpectrum_Shared_shape` | `paper/Model.tex:128` |
| G2 | `figures/AngularCorrelations/CharmCorrelations_MONASH_PDF.pdf` | `CHARMCorrelations_MONASH_PDF.pdf` | `paper/Results.tex:48` |
| G3 | `figures/AngularCorrelations/BeautyCorrelations_MONASH_PDF.pdf` | `BEAUTYCorrelations_MONASH_PDF.pdf` | `paper/Results.tex:71` |
| G4 | `figures/YieldsBalancing/global_balancing_plots_integrated_charm_PDF.pdf` | `global_balancing_plots_integrated_charm` | `paper/Results.tex:92` |
| G5 | `figures/YieldsBalancing/global_balancing_plots_multiplicity_charm_PDF.pdf` | `global_balancing_plots_multiplicity_charm` | `paper/Results.tex:105` |
| G6 | `figures/YieldsBalancing/global_balancing_plots_integrated_beauty_PDF.pdf` | `global_balancing_plots_integrated_beauty` | `paper/Results.tex:126` |
| G7 | `figures/YieldsBalancing/global_balancing_plots_multiplicity_beauty_PDF.pdf` | `global_balancing_plots_multiplicity_beauty` | `paper/Results.tex:139` |
| G8 | `figures/BaryonMesonRelativeYieldsBalancing/global_balancing_baryon_over_meson_ratio_multiplicity_PDF.pdf` | `global_balancing_baryon_over_meson_ratio_multiplicity` | `paper/Results.tex:152` |
| G9 | `figures/Kinematic Plots/` | thirty stems: `Inclusive_{pT,eta,phi}_<species>_shape` | ten species × three observables |

G1 is delivered as a **`.png`**. Every balancing figure is delivered as a
**`.pdf`** and carries the writer's `_PDF` tag before the extension
(`plotting/improvedPlotting_THnSparse.C:1328-1330`).

## The G2 / G3 rename rule

The correlation canvas builds its stem from the flavour token, which is
upper case in the macro:
`Form("%sCorrelations_MONASH", FLAVOUR)`
(`plotting/improvedPlotting_THnSparse.C:4241`). The render therefore writes
`CHARMCorrelations_MONASH_PDF.pdf` and `BEAUTYCorrelations_MONASH_PDF.pdf`,
while the manuscript includes `Charm…` and `Beauty…`.

**The rename is a handoff step, not a render step.** Rename `CHARM` → `Charm`
and `BEAUTY` → `Beauty`; change nothing else in either name.

## The five names a gate does pin

`tests/test_delivery_names.py` compares strings from the generated JSON, never
the filesystem, and pins exactly five composite names:

```
global_balancing_plots_integrated_beauty     (VINTEGRATED)
global_balancing_plots_integrated_charm      (VINTEGRATED)
global_balancing_plots_multiplicity_beauty   (VEXTREMES)
global_balancing_plots_multiplicity_charm    (VEXTREMES)
global_balancing_baryon_over_meson_ratio_multiplicity  (VBARYONMESON)
```

**Why it compares strings and not files** (finding F58): an earlier form listed
the delivery directory and compared it with `git ls-files`. No figure is
tracked and `plotting/Plots` is git-ignored, so both sides were empty and the
check passed vacuously on every commit
(`tests/test_delivery_names.py:8-13`). A name the generator has not yet
written is not evidence that the name is right.

G1, G2, G3, G9 and T1 are outside that gate: G1 and G9 come from stems in
`plotting/Plot_InclusiveKinematicSpectra_Raw.C`, G2 and G3 from the hard-coded
correlation canvas, and T1 from `tools/count_generated_sample.C`. Check those
five by enumerating the delivery directory after the render.

## Two figures in the snapshot that this manifest does not produce

`paper/Results.tex:170` and `:182` include `globalCanvasYieldsPDF_215.pdf` and
`globalCanvasRelativeYieldsPDF_215.pdf`. These are thesis figures. No G-row
produces them, and no repository target names them. They are an Overleaf-side
editorial matter for the owner, listed here so nobody hunts for a producer that
does not exist.
