# Figure inventory — every plot the paper ever carried, with one disposition

**Census taken 2026-08-17.** Sources: the manuscript's own `\includegraphics`
list (the authoritative target), the `Paper/**/figures/` tree, and
`plotting/PAPER_FIGURE_PROVENANCE.md` (review finding **A6**).

**The principle:** every figure gets exactly one disposition. No figure reaches
the manuscript from the dead dataset, and no old figure disappears without a
recorded reason.

This document is a historical source ledger, not an accepted result set.
`results/figures/main/` is the canonical destination for accepted ROOT-derived scientific bytes.
Acceptance requires exact dataset and configuration binding, trigger normalization from `hTrKinematics`, ten-block uncertainties, receipts, and visual review.
This inventory contains no complete accepted byte set.
The publication export excludes AI-assisted explanatory SVGs from this inventory.
Tune panels compare the complete MONASH, JUNCTIONS, and CLOSEPACKING bundles.

> `Paper/**` is **read-only** in this work. Nothing below edits the manuscript.
> Rows marked **⚑ owner** need a paper-side decision and name their replacement.

---

## Current acceptance audit — 2026-08-21

`results/provenance/figure_acceptance_manifest_v1.json` supersedes the
acceptance language in this historical ledger. It records eight candidates,
zero accepted roles, and no accepted output bytes. Later sections that call a
render `FINAL`, `CLOSED`, or `SIGNED OFF` describe a historical external run and
its then-recorded digest. They do not establish current acceptance because the
bytes, source logs, input hashes, and final receipts are absent here.

The audit covered all locally visible render sets:

| set | complete set identity | current disposition |
|---|---|---|
| tracked plotting validation | 5 PNGs; sorted path-and-hash ledger `9331b95a52f123f97f56d306c62a7a82683dd96a61d74533693acdf79878b8f1` | validation only |
| ignored historical paper | 148 render files; ledger `d4e360a8c971647e7f45b68e540fdc9dcdbadde6eb24e1ddcb736f2d3402ccba` | historical; every file retains its disposition below |
| ignored historical plotting output | 267 PNG/PDF/generated-C representations across 89 stems; ledger `064e2660af157006f1a8501741fac15f4f35afcf4a98b75de1fe981c011c1f9a` | untracked and not authoritative |
| external campaign and deploy storage | selector and run-record paths on `stbc-i3.nikhef.nl` | unavailable; the 2026-08-21 read-only probe returned `No route to host` |
| retained run records | the three dated records under `results/validation/plotting/` | provenance evidence, not accepted bytes |

Direct visual inspection rejects every locally available P1-P8 role file. The
old P1 states 14 TeV and an absolute-pseudorapidity limit of 4; the ignored
plotting copy is a visible no-input placeholder. The old correlation PDFs lack
the current uncertainty and physics annotation and retain ROOT statistics-box
or legend collisions. The old yield PDFs use obsolete classes or tune styling.
The old baryon/meson ratio is not the signed registry ratio. The audit
reconstructed no point from a screenshot or illustration.

The current candidate mapping is:

| role | candidate | acceptance result |
|---|---|---|
| P1 | current 13.6 TeV shared raw spectrum | blocked: final bytes, input ledger, and receipt absent |
| P2/P3 | current MONASH charm/beauty correlation canvases | blocked: final bytes, numerical bins, block coverage, and receipts absent |
| P4/P6 | `V-INTEGRATED` | blocked: final bytes and receipts absent; retained fixture lacks integer closure rows |
| P5/P7 | `V-FULL` and `V-EXTREMES` | blocked: bytes and exact-identity logs absent; presentation choice remains owner/journal work |
| P8 | signed `V-BARYONMESON` | blocked: signed-off candidate bytes and receipt absent; uncertainty closure remains provisional |

The three explanatory graphics excluded by the publication architecture were
not inspected as candidates, changed, renamed, polished, or promoted.

---

## 0. COUNTS

| disposition | count | meaning |
|---|---|---|
| **REGENERATE** | **8** | the manuscript needs it; rebuild from merged v3 |
| **BUILD** | **2 families** (32 files) | the kinematic panels, promoted by the addendum |
| **OWNER-DECIDE** ⚑ | **4** | genuinely ambiguous; the question is stated |
| **SUPERSEDED** | **6** | role served by a named new-era figure |
| **RETIRE** ⚑ | **106** | observable or claim is gone |
| total catalogued | **148** | 146 under `figures/` + 2 at the paper root |

**Manuscript reality check: 10 active `\includegraphics`, 1 commented out. All
10 resolve to files that exist.** Nothing in the draft is a broken reference
today — the problem is that the files are from the dead dataset, not that they
are missing.

---

## 1. WHAT THE MANUSCRIPT ACTUALLY INCLUDES

| # | manuscript site | figure | disposition |
|---|---|---|---|
| 1 | `Model.tex:130` | `Kinematic Plots/MultiplicitySpectrum_Shared_shape.png` | **REGENERATE** — §3.1, figure 4 |
| 2 | `Results.tex:48` | `AngularCorrelations/CharmCorrelations_MONASH_PDF.pdf` | **REGENERATE** — §3.2 |
| 3 | `Results.tex:71` | `AngularCorrelations/BeautyCorrelations_MONASH_PDF.pdf` | **REGENERATE** — §3.2 |
| 4 | `Results.tex:92` | `YieldsBalancing/global_balancing_plots_integrated_charm_PDF.pdf` | **REGENERATE** — §3.3 |
| 5 | `Results.tex:105` | `YieldsBalancing/global_balancing_plots_multiplicity_charm_PDF.pdf` | **OWNER-DECIDE** ⚑ — §4.1 |
| 6 | `Results.tex:126` | `YieldsBalancing/global_balancing_plots_integrated_beauty_PDF.pdf` | **REGENERATE** — §3.3 |
| 7 | `Results.tex:139` | `YieldsBalancing/global_balancing_plots_multiplicity_beauty_PDF.pdf` | **OWNER-DECIDE** ⚑ — §4.1 |
| 8 | `Results.tex:152` | `BaryonMesonRelativeYieldsBalancing/global_balancing_baryon_over_meson_ratio_multiplicity_PDF.pdf` | **REGENERATE** — §3.3 |
| 9 | `Results.tex:170` | `YieldsBalancing/globalCanvasYieldsPDF_215.pdf` | **OWNER-DECIDE** ⚑ — §4.2 |
| 10 | `Results.tex:182` | `BaryonMesonRelativeYieldsBalancing/globalCanvasRelativeYieldsPDF_215.pdf` | **OWNER-DECIDE** ⚑ — §4.2 |
| — | `Introduction.tex:20` **(commented out)** | `Introduction-figures/runningCouplingQCD.png` | **RETIRE** ⚑ — §5.4 |

---

## 2. E5 EXPOSURE — the per-figure check, done before plotting

The rule: `hTrKinematics` and the closure objects are **trigger-owned** and
replicated 24×/26× across pair files; `summed MULTIPLICITY` is replicated
**300×**. Anything SUMMED across pair files must dedup by trigger or read one
file per trigger. `hCorrelations`/`hAsKinematics` are per-pair and safe.

| figure family | object read | summed across pair files? | verdict |
|---|---|---|---|
| **figure 4**, multiplicity spectrum | `hMULTIPLICITY` from **raw** files | no — one histogram per *raw* file, summed over raw files | ✅ **E5-SAFE by construction.** Raw files are disjoint event sets; there is no trigger dimension to replicate |
| **kinematic spectra** pT/η/φ | `heavyPt`/`heavyEta`/`heavyPhi` from the **raw** `tree` | no — raw heavy-hadron vectors | ✅ **E5-SAFE by construction.** This is why the addendum rules out pair files |
| **angular correlations** | `hCorrelations` | per-pair | ✅ **SAFE** — per-pair object, stated safe by the standing rule |
| **balancing yields** (integrated + multiplicity) | THnSparse pair projections | **TO VERIFY** | ⚠ **NOT YET CHECKED** — see §6.1. These are the rows that could inherit E5, and the check is a precondition for regenerating them |

> **The two safe families are safe for a structural reason, not by inspection of
> a number:** the raw tree has one entry per heavy hadron per event and no
> trigger axis, so the 24×/26× replication cannot arise. That is why the
> addendum's "raw vectors, not pair files" ruling is the right one and is
> restated in each row below.

---

## 3. REGENERATE — recipe per figure

### 3.1 Figure 4 — shared charged-multiplicity spectrum ✅ RENDERED 2026-08-18

| | |
|---|---|
| paper copy | `figures/Kinematic Plots/MultiplicitySpectrum_Shared_shape.png` |
| macro | `plotting/Plot_InclusiveKinematicSpectra_Raw.C`, entry `Plot_InclusiveMultiplicitySpectrum_Raw` |
| runner | `plotting/run_paper_plots.sh multiplicity-spectrum` |
| input | **raw** `RootFiles/HF`, three tunes, object `hMULTIPLICITY` |
| E5 | ✅ safe — §2 |
| ROOT | must be the **pinned 6.30/01 on Nikhef**, not local 6.38.04 |
| status | B6 defect **FIXED** (§6.2); closed loop re-verified 2026-08-18, worst \|Δ\| = 0.000465 against tolerance 0.0005, **PASS on all eleven**; **E10 fixed and confirmed on the render**; digests in `GOLDEN_OUTPUTS.md` §9.2 |

#### Disposition after the 2026-08-18 render

| | |
|---|---|
| sha256 (png) | `c9683cee4ff85fe51d0e51b45058ba12caf4d3c8ffd3d3c406bd3715f20d42a8` — **CURRENT** |
| supersession chain | `4d7ab97e…` (wrong η caption) → `7385fbdf…` (E10 fixed, 0-dp inset) → `c9683cee…` (1-dp inset) |
| caption verified | by opening the PNG **and** by extracting every text primitive from the ROOT-generated `.C` |
| inset precision | ✅ **1 dp**: `59.8-65.9%` and `50.3-59.8%` are distinct, so E9's correction is visible on the figure it corrects |
| closed loop | worst \|Δ\| = **0.000465** against 0.0005, **PASS ×11** |
| byte stability | the PNG is **byte-identical across three later passes**, including the species-caption re-renders that rewrite the shared stem |
| **remaining before quotation** | none on this axis. `%g` renders `\|η\| ≤ 1` rather than `1.0` — an owner call on the trailing decimal, governed family-wide by `AcceptanceNumber` |

### 3.1d ✅ THE CAPTION DEFECT IS CLOSED — render #7, 2026-08-18

The last open item in the figure family. `GOLDEN_OUTPUTS.md` §9.13 carries the
digests, the battery and both placement rules.

**The defect.** The acceptance caption sat at one position inside the frame on
all 30 panels. On the low-statistics pT panels the spectrum falls into that
corner. Dense-spectrum mode removed the markers and left the error bars, and the
bars are tall where the counts are small.

**What did not work.** An anchor ladder that searched inside the frame reached 28
of 30. Two panels, pT Λ̄c⁻ and pT Σ̄b⁰, have no clear baseline anywhere inside the
frame. The other option lowered the y-axis. It would have needed 5.69 extra
decades under pT Σ̄b⁰, and a negative minimum on the linear η panels.

**What works.** The caption sits above the frame, in a top margin enlarged from
0.13 to 0.28. It cannot meet the data at any statistics. All 30 captions now sit
at one position, where the ladder gave three.

| check | result |
|---|---|
| pixel checker, all 30 panels | **clean=30, struck=0** |
| render guard, all 30 panels | `caption_bottom=0.738 frame_top=0.72 boxes_clear=1 status=ABOVE_FRAME` |
| per-tune counts, manifest, boundaries | **unchanged** |
| closed loop, re-derived | worst \|Δ\| **0.000465**, **11/11 PASS** |
| text primitives | **30/30** on √s, status, pT and η; 0 *prompt*; 0/30 routing identifiers |
| φ flatness | 0.01000 per tune, scatter 4.0–4.4 % |
| eyes-on | pT Σ̄b⁰, η D⁺, φ B⁺ — caption legible, legend clear, domains exact |

**Cost, stated plainly.** The frame loses 20.5 % of its height, from 0.730 of the
canvas to 0.580. Every panel pays it. Nothing else changed. The macro stretched
no axis, dropped no error bar, and kept the caption's full wording.

### 3.1c ⚑ THE STYLED RE-RENDER — landed 2026-08-18, three findings open

Render #4 applied the §9.6 tune palette and the owner's transparent inset to this
whole family. **Digests, per-tune counts and the full account are in
`GOLDEN_OUTPUTS.md` §9.7.**

**Every number held.** Selected particles per tune, files, tree entries, the
freeze manifest and the boundaries artifact are all **identical to render #3**;
the closed loop was re-derived independently and still gives worst |Δ| =
**0.000465**, **PASS ×11**. The mechanical panel battery is **30/30** on √s,
status window, pT and η, with **0** occurrences of *prompt* and **0/30** routing
identifiers.

**What eyes-on found that the mechanical checks could not:**

| # | finding | scope |
|---|---|---|
| 1 | **markers saturate figure 4** — ~170 bins each drawing a marker, so the tunes become solid ribbons with no line visible and MONASH largely occluded behind CLOSEPACKING | figure 4 |
| 2 | **caption struck by data** on the 4 pT panels for Λc⁺, Λ̄c⁻, Σb⁰, Σ̄b⁰ — a **regression**, the added markers eat the ~0.05 NDC clearance `f5d93b1` established | 4 / 30 panels |
| 3 | the transparent inset **worked as intended** — main spectra now visibly cross its top-right corner — and exposed **two pre-existing** collisions inside it (subtitle struck by the inset's own frame; `0.0-8.4%` struck by the inset's own curve), both dating to `272dd01` | figure 4 |

**All three are presentation rulings and none was improvised.** In particular no
sparse-marker scheme was invented for finding 1. **Figure 4 and the four struck
panels are not to be quoted until ruled on**; the other 26 panels are clear.

> ### ✅ ACTED ON — render #5, 2026-08-18 (`GOLDEN_OUTPUTS.md` §9.10)
>
> The owner ruled dense-spectrum mode and the three inset fixes; both were
> previewed locally on render #4's real generated `.C` before the pass was spent.
>
> | finding | outcome |
> |---|---|
> | 1 marker ribbons | ✅ **closed.** Lines only; the tune marker survives on the legend and nowhere else, confirmed in the generated bytes |
> | 3 inset collisions (×3) | ✅ **all closed.** Frame clear of the spectra, subtitle clear of the frame, `0.0-8.4%` clear of its own curve |
> | 2 caption struck on 4 panels | ⚑ **improved, NOT closed.** Counts down 25–77%, but the four lowest-statistics pT panels are still struck — by **error bars** now that the markers are gone |
>
> **Figure 4 is clear and quotable on this axis.** The four struck panels are not,
> and the remaining options all cost something a session should not spend
> unasked: move the block, shorten the caption, or drop the error bars. The last
> would trade uncertainty information for text room. **Owner call.**
>
> > ### ✅ THIS ROW IS HISTORY — the caption defect closed on 2026-08-18
> >
> > The owner ruled the block moved. Render #7 closed finding 2. The caption now
> > sits above the frame, and the pixel checker reports 30 clean and 0 struck.
> > Read §3.1d for the outcome. Nothing in this row is outstanding.

### 3.1b The 30 per-species pT/η/φ panels ✅ CAPTIONED 2026-08-18

Rendered in the same invocation (`kinematic-spectra` draws figure 4 *and* the 30
panels from one pass); digests in `GOLDEN_OUTPUTS.md` §9.4.5.

| check | result |
|---|---|
| positive entries in every histogram | **31 / 31** ✅ |
| η domain exactly ±4, φ exactly ±π | ✅ all ten species |
| species labels in physics notation | **30 / 30** ✅ |
| carries `13.6 TeV` | **30 / 30** ✅ |
| states its own acceptance (status 81–89, pT > 0.15, \|η\| ≤ 4) | **30 / 30** ✅ |
| says *prompt* anywhere | **0** ✅ |
| legible — block clear of legend and data | ✅ eyes-on pT / η / φ |

**Disposition: CAPTIONED.** The panels drew exactly one text primitive — their
species title — because `DrawSimulationInfoBlock` had a single call site in the
multiplicity branch. They now carry:

```
PYTHIA 8
pp, #sqrt{s} = 13.6 TeV
direct primary hadronisation products (status 81-89)
#it{p}_{T} > 0.15 GeV/#it{c}, |#eta| #leq 4
```

Every constant derives from the symbol the filling predicate evaluates, after
`5f3f381` refactored `IsCentralKinematic` and `IsDirectPrimaryStatus` off their
literals — see E10's refinement, *same value is not same symbol*.

> **Both checks were needed, and the second caught what the first could not.**
> The text-primitive extraction confirmed 30/30 carried the block while it was
> still colliding with the legend on every panel and sitting on the data on the
> log-y ones. **Presence and legibility are different checks.**

#### The label audit — done against the data, not the old figure

| label | old PNG | current macro | verdict |
|---|---|---|---|
| **√s** | `14 TeV` | `Plot_InclusiveKinematicSpectra_Raw.C:825` returns `pp, #sqrt{s} = 13.6 TeV` | ✅ **already correct in code.** The 14 is baked into the stale PNG only. **Where the 14 came from: not from this macro at all** — no other plotting source contains a `14 TeV` string, so it predates the current generator and survives purely as a raster |
| **counter** | "charged multiplicity" | read from the filling code | ⚠ **the drawn label must be made specific — see below** |
| **boundaries** | per-tune quantiles | committed artifact | ✅ fixed, §6.2 |

**What the merged MULTIPLICITY histogram actually holds**, read from the filling
code rather than assumed — `heavyflavourcorrelations_status.cpp:1058` calls
`CountsNchPrimaryChargedV1`, defined at `HeavyFlavourUtils.h:539`:

```
isFinal && isCharged && !hasHeavyConstituent && pT > 0.15 && |eta| <= 1.0
```

with `kMultiplicityPtMin = 0.15`, `kMultiplicityEtaCentral = 1.0`. The branch
names itself `multiplicity_primary_charged_eta10_v1`.

> **Two details the drawn label must not omit.** The cut is `|η| ≤ 1.0`,
> **inclusive**, not `< 1`. And heavy-flavour is **excluded** —
> `!hasHeavyConstituent` — which is the same "heavy EXCL." convention the b4
> calibration logs record. A label reading only "charged multiplicity" is
> compatible with several different counters; the caption must say
> **primary charged, |η| ≤ 1, pT > 0.15 GeV/c, heavy-flavour excluded**.

> **The brief named `Plot_MultiplicityDistribution_PercentileBoundaries.C` as the
> base. That is the wrong macro for this figure, and the distinction matters.**
> The manuscript includes `MultiplicitySpectrum_Shared_shape.png`, which is the
> `multiplicity-spectrum` target of `Plot_InclusiveKinematicSpectra_Raw.C` — the
> one target whose description mentions the **MONASH inset** the brief asks about.
> The boundaries macro produces the flavour-split
> `MultiplicityDistributionPercentileBoundaries_*` PDFs, which the manuscript does
> **not** include (§5.1). Both were examined; the findings differ per macro and
> are recorded separately in §6.2.

### 3.1b ✅ RENDERED 2026-08-17 — the three-tune multiplicity canvas

Rendered on Nikhef, **pinned ROOT 6.30/01**, from the sealed `canonical` dataset,
config `configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse_complete_root.json`,
target `thnsparse-complete-root`. Output
`global_balancing_plots_multiplicity_HF_RUN3_V1_THREETUNE_{PDF,PNG,MACRO.C}` plus
`multiplicity_boundary_receipt_v1.json`, `tune_count=3 status=PASS`.

**SUPERSEDED 2026-08-19 by the label correction.** The committed reference is
now `8776a1fff6a425a2…`, re-rendered on the pinned stack from the corrected
configuration (`22caef48362e92a7…`). The class labels below read `59.8-65.9%`
and `50.3-59.8%` where they read `59.9` before, which is what
`config/multiplicity_class_boundaries_v1.json` says. **No number moved**: all
132 `UNCERTAINTY_MATRIX` rows agree across nine fields, zero disagreements. The
paragraph below describes the superseded `545499157bf7d4a2…` render and is kept
because the determinism result it records still stands.

**Determinism — the strong result.** The PNG is
`545499157bf7d4a2…`, **byte-identical to the committed
`…THREETUNE_POLISHED_PNG.png`** from the 2026-08-16 run. Reproduced across a
different session, a different deploy tree, and the dataset's promotion from
`canonical_candidate` to `canonical`. The boundary receipt differs in exactly
**two leaves**: one embedded deploy path and the `payload_sha256` that covers it.
Every physics quantity is identical.

**Ten-subsample coverage is complete.** Every `UNCERTAINTY_MATRIX` row reports
`finite_yields=10 … status=PASS`. This answers the standing concern from
`PAPER_FIGURE_PROVENANCE.md` — the **610 incomplete coverage cases** were a
property of the legacy dataset, not of merged v3.

**The class axis is live and correct in the figure.** The legend reads
`88.2-100.0%, 80.6-88.2%, 65.9-80.6%, 59.9-65.9%, 50.3-59.9%, 43.0-50.3%,
34.6-43.0%, 26.2-34.6%, 17.1-26.2%, 8.4-17.1%, 0.0-8.4%` and the internal bin
names are `hDPhic1_MB88p197_100 … hDPhic10_MB8p422_17p124` — the artifact's
MB percentiles, matching the independent closed-loop recomputation to the digit.

#### ⚠ Visual review — sound numbers, NOT publication-presentable ⚑

**Looked at, as the contract requires.** Tune styling is canonical (MONASH
black, JUNCTIONS blue, CLOSEPACKING magenta), the ratio panels are present, and
the physics reads correctly — the Λ_b and Λ_c ratios rise well above unity for
both CR tunes (JUNCTIONS/MONASH Λ_b reaching ≈ 2.3) while the meson ratios sit
at or below 1. **That is the baryon enhancement the paper is about, and it is
visible.**

Four presentation defects, all of which are also in the committed reference:

| # | defect |
|---|---|
| 1 | **Species labels are raw identifiers** — `Lambda_b`, `Lambda_c(+)-bar`, `B-`, `D-`. A paper figure needs `Λ_b`, `Λ̄_c⁻`, `B⁻`, `D⁻` |
| 2 | **The x-axis is two categorical points per panel**, with each class drawn as a horizontal rule spanning the full category width. It reads as a stack of lines rather than a comparison |
| 3 | **No x-axis title, no √s label**, and the class legend appears only in the top-left panel |
| 4 | **The y-axis says `yield`** — it is the per-trigger balancing yield, and should say so |

**⚑ Owner:** these are presentation, not correctness. The numbers are sealed,
reproducible and cross-checked; the canvas needs a styling pass before it goes
in the manuscript.

### 3.2 Angular correlations, charm and beauty

| | |
|---|---|
| macro | `plotting/improvedPlotting_THnSparse.C`, full config, `draw_correlation_plots=true` |
| input | MONASH complete-root pairs — D+/D− and Λc/D− (charm), B+/B− and Λb/B− (beauty) |
| E5 | ✅ safe — `hCorrelations` is per-pair |
| errors | per-Δφ-bin SEM from the ten disjoint blocks; **OS−SS formed inside each block before the SEM**, preserving OS/SS covariance. Native ROOT projection errors are not used |
| cross-check | none of the published tables carries Δφ shapes; no mandatory table cross-check |

### 3.2a ASSESSED 2026-08-18 — renderable from existing products, but NOT a flag flip

**Assessed before rendering, as instructed, and the assessment changed the answer.**
The disposition asks whether this is a render of existing merged products through
existing macros. It is — with one substantive caveat that must be ruled on first.

**What is already in place, and needs nothing built:**

| | |
|---|---|
| the canvas | **hard-coded in the macro**, not authored in configuration — pads at fixed NDC (`improvedPlotting_THnSparse.C:3310-3313`), log-y, via `createMiniPad` |
| the output stem | `Form("%sCorrelations_MONASH", FLAVOUR)` (`:4177`) → `CharmCorrelations_MONASH`, `BeautyCorrelations_MONASH` — **exactly the manuscript's two filenames** |
| the output directory | `plotting/Plots/THnSparse/Correlations`, fresh — no collision with any signed-off artifact |
| staging + receipt | **automatic.** `writeCanvasToFiles` always stages (`:1321`) and promotion happens only after the boundary receipt passes (`:5349`) |
| the MONASH label | **honest by construction** — the draw is gated on `TUNE == "MONASH"` (`:3587`) |
| the four input pairs | **all present** in `complete_root_HF_RUN3_V1_MONASH`: `BplusBminus`, `LbbarBminus`, `DplusDminus`, `LambdacplusDminus` |

**The caveat, and it is not cosmetic.** The draw is additionally gated on the OS
file being one of those four (`:3588-3591`) **and** on an integrated multiplicity
bin (`IsIntegratedMultiplicityBin`, `:3586`). Against the HF_RUN3_V1 configuration:

| gate | status |
|---|---|
| integrated multiplicity bin | ✅ V-INTEGRATED has one; V-FULL and V-EXTREMES do **not** |
| `DplusDminus`, `BplusBminus` (the **meson** channels) | ✅ registered |
| `LambdacplusDminus`, `LbbarBminus` (the **baryon** channels) | ❌ **NOT registered** |

HF_RUN3_V1 registers the **opposite pair direction** for the baryon channels —
`DplusLambdacplusbar` (D⁺ trigger, Λ̄c associate) and `BplusLb` — whereas the
correlation canvas wants Λc⁺ and Λ̄b as the **trigger** against a D⁻ / B⁻
associate. §3.2's own input line says so: *"D+/D− and **Λc/D−**"*.

> **So a flag flip alone yields a HALF-EMPTY figure.** The canvas has a meson pad
> and a baryon pad per flavour; with only the meson pairs registered, both
> `pCharmBaryon` and `pBeautyBaryon` would draw nothing, and the render would
> look successful.

**The delta this needs — named so the owner can rule in one line:** register
`LambdacplusDminus` and `LbbarBminus` as analysed correlations on a
V-INTEGRATED-derived configuration. **No new extraction and no new physics
computation** — the files exist and the macro already processes this shape — so
this does **not** meet the session's STOP criterion. But it **changes the
analysed pair set**, which feeds `ResolveReferenceAssociateSelection` and hence
the reference associate underpinning the block uncertainties. That is more than
a style adaptation, and it is why this was assessed and reported rather than
rendered unasked.

---

### 3.3 Balancing yields — integrated charm/beauty, and the baryon/meson ratio

| | |
|---|---|
| macro | `plotting/improvedPlotting_THnSparse.C`, full config |
| input | all three complete-root tunes plus ten subsamples |
| E5 | ⚠ **check first — §6.1** |
| **mandatory cross-check** | the quantities overlap `docs/THREE_TUNE_CENTRAL_TABLE.md` and `MONASH_CENTRAL_TABLE.md`. The drawn integrated values must reproduce the published fractions; **A2's per-class systematic** (`results/a2/20260813/results/`) applies to the multiplicity-differential panels and must be quoted per class, never integrated |
| known blocker | `PAPER_FIGURE_PROVENANCE.md` records **610 incomplete ten-subsample coverage cases** (540 beauty, 70 charm) in the last exhaustive audit. **That audit must be re-run against merged v3 and come back clean before any of these is promoted.** The full config fails closed rather than emitting partial errors, so this surfaces as a hard failure, not a silent gap |

### 3.3a ✅ CLOSED 2026-08-18 — integrated charm/beauty, closed on V-INTEGRATED

**Items 4 and 6 close together on one artifact**, because one artifact carries
both flavours.

| | |
|---|---|
| artifact | `global_balancing_plots_multiplicity_HF_RUN3_V1_THREETUNE_VINTEGRATED_POLISH_PROPOSAL_PNG.png` |
| sha256 (PNG — the byte anchor, §9.4.3) | `88fdb62845ccbcb623bf908a0ff0eedc8a822194a3c05dfbb5483882da1d4990` |
| receipt | PASS, plotter `003a39e3997b943f…`, promoted only after the gate |
| pre-registration | `docs/V_INTEGRATED_PREREGISTRATION.md` — the estimator was fixed before it was measured |
| closure | integer-exact on all twelve keys, no tolerance |

**The coverage claim, stated explicitly for owner verification.** V-INTEGRATED's
twelve keys are **four associate species × three tunes**, and the four species
span both flavours: **charm** D⁻ and Λ̄c (item 4), **beauty** B⁻ and Λ_b⁰
(item 6). The canvas draws five beauty and five charm mini-canvases — one per
tune plus the two tune ratios per flavour.

**Eyes on, 2026-08-18, as a check distinct from the digest.** Both flavours are
drawn and labelled in physics notation; tune identity is correct and matches the
mandate (MONASH black/circle, JUNCTIONS blue/square, CLOSEPACKING purple/triangle,
all solid); the axis declaration reads `multiplicity integrated, 0.0-100.0%`;
the y-axis says **balancing yield per trigger**, not "yield". The physics reads:
Λ_b/MONASH ratios ≈ 1.7 (CLOSEPACKING) and ≈ 1.9 (JUNCTIONS) against B⁻ ratios
≈ 0.74–0.76 — baryon enhancement above unity, mesons below.

> **Two honest caveats, neither a coverage gap.** (1) **Packaging**: this is one
> canvas; the manuscript names two files — the same editorial change §4.1 needs.
> (2) Each point is still drawn as a **horizontal rule spanning its category
> width** (§3.1b presentation defect 2), which is a live characteristic of this
> canvas family, not of the integration.

### 3.3b ⚠ OPEN 2026-08-18 — baryon/meson ratio: the path is live, the configuration does not exist

**Reported rather than rendered, and the reason is specific.** The instruction
was to render through the existing `drawBalancingBaryonMesonRatioPlots` path with
the style header applied. **That path is live and reachable** — dispatched on
`draw_function_to_use` (`improvedPlotting_THnSparse.C:5288`), and it would inherit
staging and the receipt gate automatically like every other canvas.

**What blocks it is that no HF_RUN3_V1 configuration declares such a canvas.**
Measured across every configuration in `plotting/`:

| configuration | baryon/meson canvases |
|---|---|
| all six `HF_RUN3_V1_*` (incl. the styled family) | **0** |
| `configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json` | 4 — but **validation-only**, ruled unusable for the manuscript in §4.1 |
| excluded legacy plotting configuration | 12 — but **two-tune** |

> **The two live call sites at `:5363-5364` are inside a commented-out block**
> headed *"TODO: only for simple tests, remove"*. There is no standalone entry
> point; configuration is the only route.

**The physics is available** — the ratio needs Λ̄c/D⁻ and Λ_b/B⁻, and all four
are registered — so this is **not** blocked on data or on extraction.

**It is blocked on presentation, which is an owner call.** Building the
configuration is not style application; it is authoring a new figure's
presentation, and every comparable canvas family here was pre-registered and
signed off before it was rendered. Concretely, none of these is derivable from an
existing HF_RUN3_V1 artifact:

1. **the y-axis range, and linear vs log** — the legacy ratio panels are linear
   `0.0–1.0` while every HF_RUN3_V1 yield panel is log `0.01–0.42`; a ratio that
   reaches ≈ 1.9 (§3.3a) does not fit `0–1`;
2. **the panel layout for three tunes** — the legacy layout is two-tune;
3. **the Σ panels are available in beauty and NOT in charm** — an asymmetry that
   has to be ruled on rather than papered over. The legacy config's `lambda_sigma`
   canvases need Σ_c *and* Σ_b. Measured against the freeze's MONASH complete-root
   set (304 files):

   | | in the config's short trigger form | verdict |
   |---|---|---|
   | Σ_b | `BplusSigmabzero.root`, `BplusSigmabzerobar.root` | ✅ **buildable** against the B⁺ trigger |
   | Σ_c | D⁺-triggered short forms are only D∓, D⁰(bar), Λc⁺(bar) — **no `DplusSigmac*`** | ❌ not against the D⁺ trigger |

   Σ_c pairs *do* exist in the freeze (36 files) but only under **D⁰ / D̄⁰**
   triggers in the long `pair_charm_trig_*_assoc_*` form, so using them would mean
   changing the charm trigger — a different figure, not a styling choice.

   > **Correction, same session:** an earlier draft of this section said the Σ
   > panels "cannot be built at all". **That is wrong** — Σ_b is directly
   > available, and the real constraint is charm-side and trigger-shaped. The
   > owner's options are therefore *beauty-only Σ*, *drop Σ*, or *change the charm
   > trigger*, which is a wider decision space than "drop half the legacy canvas".

   Separately, **none of these Σ pairs is currently registered** in any
   HF_RUN3_V1 correlation set, so any of them entails the same
   analysed-pair-set change flagged for the angular correlations in §3.2a.

**Recommended minimal delta, if the owner wants it rendered:** derive a
`V-BARYONMESON` configuration in `tools/make_variant_configs.py` (generated, never
hand-written) from the existing base, changing only `draw_function_to_use`,
`baryons_to_plot_in_baryon/meson_ratio`, the y-axis title, and writing to its own
`plotting/Plots/VariantBaryonMeson` so no signed-off artifact is touched —
**leaving the y-range, the log/linear choice and the Σ question to be ruled
first.** Per §9.4.3a this should be previewed against the generated `.C` before a
render pass is spent.

---

## 4. OWNER-DECIDE ⚑ — the questions, stated

### 4.1 Two multiplicity panels, or one combined canvas?

`Results.tex:105` and `:139` include **separate** charm and beauty
multiplicity-dependent canvases. **The current workflow produces one combined
canvas** (`global_balancing_plots_multiplicity_PDF.pdf`); there is no current
generator output with the two draft names.

**✅ RULED 2026-08-20 — move the manuscript to the single combined canvas.**

**The manuscript edit:** the two `\includegraphics` lines at `Results.tex:105`
and `:139`, and their two captions, are replaced by one of each, pointing at
`global_balancing_plots_multiplicity_PDF.pdf`. **Not executed here** — `Paper/**`
is read-only in this work, and this is recorded as the ruling the manuscript
session applies.

**The reasoning.** The combined canvas is the output the pipeline actually
produces and has already validated: its three-tune render came back
**byte-identical** on an independent re-render, in a different session and a
different deploy tree (private supervisor change record, Section 9.3). The alternative
adds a configuration variant whose only purpose is to match a draft layout, and
every new render owes its own receipt, determinism check and visual review. The
manuscript edit is two lines; the plotting change is a new artifact with a new
provenance chain.

**No configuration change is needed, and that was checked rather than assumed.**
Every selected multiplicity configuration in `plotting/` emits one canvas.
The excluded legacy two-tune configuration and
`configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse_complete_root.json:1661`
each carry a single `write_name` of the form
`global_balancing_plots_multiplicity*`, and no per-flavour variant exists
anywhere in the directory.

**This must not be resolved silently** — the reduced smoke output *does* produce
similarly-named files and is **validation-only**; substituting it would put a
one-activity-class plot where the paper claims a full multiplicity dependence.

### 4.2 The two `_215` global canvases

`Results.tex:170` and `:182` include `globalCanvasYieldsPDF_215.pdf` and
`globalCanvasRelativeYieldsPDF_215.pdf`, which are **legacy
`Balancing_and_Sampling` products**. No current generator emits them.

**✅ RULED 2026-08-20 — DROP both. §3.3 carries the content.**

**The manuscript edit:** the two `\includegraphics` lines at `Results.tex:170`
and `:182` and their captions come out. **Not executed here** — recorded as the
ruling the manuscript session applies.

**The reasoning.** The replacement already exists and already carries the same
content in current form: the per-flavour balancing-yield canvases of §3.3. The
alternative pays for a new generator, written against merged v3, to reproduce a
summary view of numbers the paper shows elsewhere.

**The legacy files cannot be refreshed, so "keep" never meant "re-run".** Their
inputs are gone: the v2 plotting configuration points at
`AnalyzedData/complete_root_21_06_2026` and
`AnalyzedData/SUBSAMPLES_700/combined_root_subSamples`, and **both are absent
locally and on Nikhef**, measured 2026-08-13 in the private plotting-delta record.
The private branch-state record classifies the whole family as permanently not regenerable.

**One consequence travels with this ruling.** Dropping these two figures ends the
manuscript's only dependence on `Balancing_and_Sampling`, which is what makes
the historical double-counting caveat out of scope — see the private repository
census, Section 5, where that conditional is recorded.

---

## 5. SUPERSEDED and RETIRE

> ### ✅ RULED 2026-08-20 — §5.1 and §5.2 are ACCEPTED as a block; §5.3 goes back to the owner
>
> **§5.1, the six supersessions: ACCEPTED.** Each names a specific current
> replacement, so the disposition is checkable rather than a judgement.
>
> **§5.2, the ten AVFD `.eps` files: ACCEPTED.** This is a factual claim, not a
> judgement — they belong to a chiral-magnetic-effect analysis, no
> `\includegraphics` names them, and no observable in this paper corresponds to
> them.
>
> **§5.3, the ninety-five superseded exploratory plots: NOT accepted as a
> block.** These are the retirements that could be wrong, because each retires a
> figure on the grounds that a superseding view exists. §5.3a puts the nine
> families to the owner, one line each.
>
> **§5.4 is ruled separately** — drop the line.

### 5.3a THE NINE FAMILIES — one line each, for the owner to answer

**Answer each row `retire` or `keep`.** The reason column is what the census
recorded; the question column is the only thing at issue. Nothing here is
executed against `Paper/**`.

| # | family | count | why it was retired | the question |
|---|---|---|---|---|
| **F1** | `Iñaki plots/MinimumBiasSingleParticleSpectra_*` | 18 | minimum-bias single-species spectra from the **pre-v3 dataset**; the role passes to the §7 inclusive panels | §7 is **blocked** behind the freeze contract (§6.3b). Retire now and carry a gap until §7 lands, or keep until it does? |
| **F2** | `Iñaki plots/SingleParticleSpectra_*` | 18 | as F1, non-MB variant | same question as F1, and the same answer should serve both |
| **F3** | `Iñaki plots/Ratio_*_MONASH_vs_JUNCTIONS_*` | 30 | **two-tune** ratios in 20 %-wide multiplicity slices; the analysis is now three-tune and the axis is the 11-class common-absolute partition | Both grounds are structural and neither can be repaired. Retire? |
| **F4** | `Iñaki plots/SpeciesResolvedSpectraCompareTunes_*_{0_20…80_100}` | 10 | same two-tune / wrong-axis grounds as F3 | Retire with F3, or is the species-resolved view wanted rebuilt on the current axis? |
| **F5** | `Iñaki plots/Ratio_{Lambdac_over_Dplus,Lambdab_over_Bplus}_vsMult` | 2 | superseded by the §3.3 baryon/meson ratio canvas, which uses the signed registry definition | The replacement exists and is current. Retire? |
| **F6** | `AngularCorrelations/` legacy — `c1x2_DPhi_214`, `c2x3_DPhi_Mult_214`, and two `c_correlations_OS_SS *.root for [0.000000, 100.000000]_PDF.pdf` | 4 | pre-THnSparse numbered-canvas products, replaced by §3.2; the two long names also embed a `.root` name and a float range | Retire? The filenames alone disqualify the last two from publication |
| **F7** | `YieldsBalancing/PDF_cYields_Error_YieldsTree_*_215` + `balancing-yield.png` | 5 | legacy `YieldsTree` era | Retires with the `_215` ruling in §4.2. Confirm? |
| **F8** | `BaryonMesonRelativeYieldsBalancing/PDF_cRelYields_Error_YieldsTree_*_215` + `balancing-baron-meson-ratio.png` | 7 | legacy `YieldsTree` era; the filename also misspells "baryon" | Retires with F7. Confirm? |
| **F9** | paper root `Trigger_phi_{CHARM,BEAUTY}_shape.pdf` | 2 | the φ role is **promoted** to a validation panel and rebuilt (§7), so superseded rather than dropped | §7 is blocked. Same timing question as F1 |

**Total 96 across the nine rows against §5.3's stated 95.** The one-file
difference is `balancing-baron-meson-ratio.png`, which §5.3 counts inside F8's
seven and the family table also lists at the paper root. **Flagged, not
silently reconciled** — the census owns the count and this table quotes it.

> **Three of the nine turn on one timing question, not on the figures.** F1, F2
> and F9 are retired in favour of the §7 kinematic panels, and §7 cannot be built
> until the freeze contract is amended (§6.3b). Answering "retire" for those
> three accepts a gap in the paper until §7 lands. **That is a scheduling
> decision about §6.3b, and answering it there answers these three.**


### 5.1 SUPERSEDED (6) — the role is served by a named new-era figure

| file(s) | superseded by |
|---|---|
| `figures/MultiplicityDistributionPercentileBoundaries_{CHARM,BEAUTY}_counts.pdf` | **figure 4** (`MultiplicitySpectrum_Shared_shape`) — one ROOT-derived shared event spectrum replaces the flavour-duplicated pair and carries the common class axis |
| the same two files duplicated inside `figures/Iñaki plots/` | as above — they are byte-duplicates of the top-level pair |
| `Iñaki plots/MinimumBiasSpeciesResolvedSpectraCompareTunes_{Charm,Beauty}_27-03-2026.png` | the accepted ROOT-derived inclusive species-kinematics family in §3.1b |

### 5.2 RETIRE — a different paper's figures (10) ⚑

`figures/` top level holds ten `.eps` files that belong to a **chiral-magnetic-effect /
AVFD analysis**, not this one: `BFieldVsCentrality`, `BFieldVsTime`,
`centrality40To50AVFDCME`, `centrality40To50AVFDLCC`,
`centralityDependenceAVFD-PbPb`, `centralityDependenceAVFD-XeXe`,
`cmeResultsVsModelsPbPb5TeV`, `deltaDeltaAVFD`, `deltaGammaAVFD`, `modelResult`.

**Reason:** template leftovers. Never referenced by any `\includegraphics`, and
no observable in this paper corresponds to them. **No replacement needed.**

### 5.3 RETIRE — superseded exploratory plots (95) ⚑

| family | count | one-line reason |
|---|---|---|
| `Iñaki plots/MinimumBiasSingleParticleSpectra_*` | 18 | minimum-bias single-species spectra from the **pre-v3 dataset**; the role passes to the §7 inclusive panels, built from raw v3 with audited labels |
| `Iñaki plots/SingleParticleSpectra_*` | 18 | as above, non-MB variant |
| `Iñaki plots/Ratio_*_MONASH_vs_JUNCTIONS_*` | 30 | **two-tune** ratios in 20%-wide multiplicity slices. Retired on two counts: the analysis is now **three**-tune, and the class axis is the committed 11-class common-absolute partition, not 20% slices |
| `Iñaki plots/SpeciesResolvedSpectraCompareTunes_*_{0_20…80_100}` | 10 | same two-tune / wrong-axis reasons |
| `Iñaki plots/Ratio_{Lambdac_over_Dplus,Lambdab_over_Bplus}_vsMult` | 2 | superseded by the baryon/meson ratio canvas of §3.3, which uses the signed registry definition |
| `AngularCorrelations/` legacy (`c1x2_DPhi_214`, `c2x3_DPhi_Mult_214`, and the two `c_correlations_OS_SS *.root for [0.000000, 100.000000]_PDF.pdf`) | 4 | old numbered-canvas products of the pre-THnSparse stack; replaced by §3.2. The two long filenames also embed a `.root` name and a float range — not publishable identifiers |
| `YieldsBalancing/PDF_cYields_Error_YieldsTree_*_215` + `balancing-yield.png` | 5 | legacy `YieldsTree` era |
| `BaryonMesonRelativeYieldsBalancing/PDF_cRelYields_Error_YieldsTree_*_215` + `balancing-baron-meson-ratio.png` | 7 | legacy `YieldsTree` era (filename also misspells "baryon") |
| paper root `Trigger_phi_{CHARM,BEAUTY}_shape.pdf` | 2 | **see §7** — the φ role is promoted to a validation panel and rebuilt, so these are superseded rather than merely dropped |

### 5.4 RETIRE ⚑ — `runningCouplingQCD.png`

Already commented out at `Introduction.tex:20`.

**✅ RULED 2026-08-20 — DROP the line.** Nothing in the current analysis depends
on it, and the line is already commented out, so this finishes a decision that
was left half-made rather than reversing one. If the introduction later wants a
running-coupling illustration, that is a writing decision taken while writing the
introduction, with a current source and its attribution — not a figure-inventory
row. **Not executed here**; recorded as the ruling the manuscript session
applies.

---

## 6. THE TWO FINDINGS THAT BLOCK WORK

### 6.1 ✅ RESOLVED 2026-08-17 — the balancing-yield family is E5-SAFE

**Verdict: safe, and safe for a structural reason that is worth stating exactly,
because the object involved IS the replicated one.**

The balancing yield is a per-trigger-normalised ratio
(`calculateOneYield`, `improvedPlotting_THnSparse.C:3005`):

| part | object | E5 status of the object |
|---|---|---|
| numerator | `hCorrelations` Δφ integral | per-pair — never replicated |
| denominator | `nTriggers = hTrPt->Integral()`, from **`hTrKinematics`** | **trigger-owned, replicated 24×/26× across pair files** |

So the safety cannot be "it does not touch the replicated object" — it does. The
safety is that **it is read once per pair file and never summed across them**:

1. Each configured pair names exactly **one** OS file and **one** SS file
   (`pair.OS`, `pair.SS`), opened per pair for the central (`:1912`) and for each
   block (`:1966`).
2. The **only** two histogram `Add()` calls in the macro are
   `hCorr->Add(hDPhiSS, -1.)` and `hSub->Add(hDPhiSS, -1.0)` — OS minus SS
   **within one pair**. There is no cross-pair-file summation anywhere.
3. A **uniqueness guard throws** on a configuration that would create one
   (`:614`): `osFiles.insert(...)`, `ssFiles.insert(...)`,
   `osAssociates.insert(...)` → `"Duplicate configured pair identity"`.
4. The multiplicity read (`:1866`) dedups by path (`visitedCentral`) and captures
   an **identity**, not a sum.

Numerator and denominator therefore come from the same single file, and the ratio
is "pairs of this channel per trigger" — the intended observable. **Point 3 is
what makes this structural rather than incidental:** the replication could only
arise from a configuration naming a pair file twice, and that configuration is
refused.

### 6.1b ⚠ The old check that WAS pending

§3.3's figures read THnSparse pair projections. Whether any of their inputs is
**summed across pair files** has not been established, and the brief's rule makes
that the deciding question. **This is a precondition, not a formality:** the
closure objects and `hTrKinematics` are trigger-owned, and a summed
trigger-owned object inherits the 24×/26× replication that produced **E5**.

**The check to run:** for each drawn quantity in `improvedPlotting_THnSparse.C`,
determine whether the projection sums over pair files, and if so whether it
dedups by trigger. Record the outcome in this row before regenerating.

### 6.2 ⛔ The B6 boundary-artifact update did NOT reach the figure-4 macro

**This is the answer to the brief's "verify that update is complete before
running, including the inset/marker source". It is not complete.**

| macro | boundary source | B6 status |
|---|---|---|
| `Plot_MultiplicityDistribution_PercentileBoundaries.C` | `HadronizationMultiplicity::LoadCommonBoundaries(...)` — the committed artifact | ✅ **updated**, and its own comment says it must not recompute this tune's quantiles "which would now disagree with the frozen receipt by construction" |
| `Plot_InclusiveKinematicSpectra_Raw.C` **(the figure-4 macro)** | `CalculateMultiplicityThreshold(hist, p)` — a running-integral **quantile of the passed histogram** | ⛔ **NOT updated.** The file contains **zero references** to the artifact |

**Why this is worse than a stale number.** `config/multiplicity_class_boundaries_v1.json`
states the axis is **common absolute** N_ch boundaries whose labels are
percentiles of the **MONASH minimum-bias** distribution, recomputed from the
committed MB anchor. The inset instead takes quantiles of the **MONASH
production** histogram — and the production campaign is **HardQCD with
pTHat > 2**, not minimum bias. So the inset would draw boundaries from one
distribution and label them with percentiles that are defined on a different one.

The artifact anticipates exactly this: *"THIS FILE IS THE ONE DEFINITION OF THE
AXIS… Neither may carry a literal copy — two definitions drift, and the axis is
the thing every per-multiplicity number is conditioned on."* The inset is a third
consumer that never read it.

**Disposition: fix before rendering.** The inset must resolve
`config/multiplicity_class_boundaries_v1.json` and label from the recomputed
MB percentiles, matching `tools/class_label_format.py`. **Figure 4 is not rendered until then** — rendering it
first would produce precisely the "per-tune quantiles" figure the brief forbids.

### 6.3b ✅ FIXED 2026-08-17 — the freeze contract now describes the seal

**Resolved.** `Plot_InclusiveKinematicSpectra_Raw.C` derives the campaign shape
from the manifest instead of hardcoding one campaign's arithmetic, and the
required-artifact set is narrowed to what a sealed freeze actually contains. On
the real HF_RUN3_V1 freeze it now reports:

```
CANONICAL_FREEZE_CONTRACT manifest_sha256=fcd96eae… tunes=3 jobs_per_tune=1000
  events_per_job=100000 events_per_tune=100000000 rows=3000 blocks=10
  validation_log=absent shape=derived
```

`events_per_tune` reaches exactly the 100 M the retired rule demanded — as
1000 × 100 000 rather than 100 × 1 000 000. **The path taken was NARROWED, not
aggregated**; the reasoning and the nine negative tests are in
`tests/test_canonical_freeze_contract.py` and the commit message. No
campaign-level receipt was synthesised.

*Superseded description of the defect, kept because the reasoning is the record:*

### 6.3b-history ⛔ the freeze contract's producer and consumer disagreed

**The owner gate in §6.3 is now OPEN** — HF_RUN3_V1 was sealed and promoted to
`canonical` / `publication_eligible: true`. Rendering figure 4 then failed at the
*next* gate, and that one is a defect rather than a policy:

```
ERROR: cannot open file for SHA-256: .../freeze/canonical_raw_validation_receipt.json
```

**`Plot_InclusiveKinematicSpectra_Raw.C` requires a five-artifact sealed freeze.
`tools/build_canonical_manifest.py` produces three of them.** The mismatch is
threefold and none of it is fixable by running something:

| # | required by the macro | produced by the repo |
|---|---|---|
| 1 | `canonical_manifest.jsonl`, `freeze_summary.json`, `canonical_raw_validation_receipt.json`, `freeze_seal.json` | only the manifest, the ten block files and the seal. **`freeze_summary.json` and the validation receipt are written nowhere in the repository except test fixtures** |
| 2 | `seal.state == "SEALED"`, `seal.validation_receipt_path`, `seal.validation_receipt_sha256` | the builder's seal has **none of these fields** |
| 3 | shape: first-stage → `jobs_per_tune == 100` **and** `successful_events_per_job == 1000000`; superseding → ≥ 110 jobs **and a union of ≥ 2 source freezes** | **HF_RUN3_V1 is 1000 jobs × 100 000 events.** It fits neither: it is not 100 jobs, and a single campaign is not a multi-source union |

> **The shape rule is the deep one.** 100 jobs × 1 M events and 1000 jobs × 100 k
> events are **the same 100 M per tune**, differently decomposed. The contract
> checks the decomposition, and it was written for
> `campaigns/HF_100M_primaryGround_ccbb_v1` — the only entry in `campaigns/` —
> and never updated for the physics campaign.

**Deliberately not worked around.** Producing the two missing artifacts by hand
would mean writing `successful_events_per_job: 1000000` (false — it is 100 000)
and `state: "PASS"` on a validation receipt for an exhaustive raw validation that
was never run. That is fabricated evidence, and it is the exact failure mode the
rest of this project's machinery exists to prevent.

**This blocks only the raw-reading macro** — figure 4 and the §7 kinematic
panels. `improvedPlotting_THnSparse.C` reads merged products and **does not
consume the freeze at all**, so the five THnSparse rows are unaffected.

### 6.3 ✅ OWNER GATE — CLEARED 2026-08-17

**Both raw-reading figure families — figure 4 and the §7 kinematic panels — are
blocked behind the same gate, and the gate is correct.** Reached by attempting
the render on Nikhef with pinned ROOT 6.30/01; the macro refused:

```
ERROR: selector mode requires a consistent status/publication-eligibility pair
```

`Plot_InclusiveKinematicSpectra_Raw.C::ResolveDatasetInputMode` admits exactly
two states, and `canonical_candidate` is deliberately neither:

| status | publication_eligible | admitted as |
|---|---|---|
| `canonical` | `true` | canonical-manifest mode |
| `legacy*` | `false` | legacy diagnostic |
| **`canonical_candidate`** | **`false`** | **refused — this is HF_RUN3_V1** |

**Two owner prerequisites, in order:**

1. **The canonical manifest does not exist.** `campaigns/HF_RUN3_V1/freeze/`
   is absent entirely. Building it (`make manifest CAMPAIGN=HF_RUN3_V1`) *seals
   the campaign*, which is a dataset decision, not a plotting one.
2. **The dataset must be promoted** from `canonical_candidate` to `canonical`
   with `publication_eligible: true` and a `publication_authorization` plus its
   sha256, in `config/dataset_selector_hf_run3_v1.json`.

> **This was not worked around, and should not be.** The gate exists so a figure
> cannot reach the manuscript from an unauthorized dataset — the same principle
> as this inventory's own rule about the dead dataset, pointing the other way.
> Everything upstream of it is done: the macro is fixed, compiles on pinned
> ROOT 6.30/01, the raw data is present (1000 files × 3 tunes), and the label
> and boundary audits are complete and verified against the frozen receipt.
> **The render is one owner action away.**

A prepublication scratch deploy of the fixed macro is staged at
`/data/alice/ipardoza/figure_deploy_20260817` (source only, ~1 MB; the frozen
checkout was not written).

---

## 7. BUILD — the kinematic panels (addendum)

**Source ruling: raw heavy-hadron vectors, NOT merged pair files.** Stated
reason, per the addendum and confirmed in §2: `hTrKinematics` is E5-replicated
24×/26×, and pair-file associates are **pair-weighted, not inclusive** — an
inclusive spectrum built from them would be weighted by how often each hadron
happened to be paired.

| | |
|---|---|
| macro | `plotting/Plot_InclusiveKinematicSpectra_Raw.C`, entry `Plot_InclusiveKinematicSpectra_Raw` |
| runner | `plotting/run_paper_plots.sh kinematic-spectra` |
| input | raw `RootFiles/HF` `tree`, branches `heavyPdg/heavyPt/heavyEta/heavyPhi/heavyIsFinal/heavyCentral` |
| subset | **100 files/tune** pre-stated; revise with a one-line argument if the spectra are not smooth |
| content | per-species inclusive spectra, **three tunes overlaid**, unit-normalized |
| markers | acceptance cuts drawn: trigger pT > 1, associate pT > 0.15, \|η\| ≤ 4 |
| predecessor | the 30 existing `figures/Kinematic Plots/Inclusive_{pT,eta,phi}_<species>_shape.pdf` — **reused and audited, not rewritten** |
| status | ⛔ **same gate as figure 4 — §6.3.** Identical macro, identical resolver |

**Proposed panel set** (the addendum invites a proposal): the ten species the
existing files already cover — `D+`, `D−`, `B+`, `B−`, `Λc+`, `Λ̄c−`, `Λb`,
`Λ̄b`, `Σb0`, `Σ̄b0` — which is exactly the paper's quoted trigger set plus the
Σb pair the Σb ordering work needs.

**φ is the validation panel and its verdict is a finding, not a style note.** It
must be flat; a non-flat φ spectrum is reported as a result. The caption material
must say it is shown as an isotropy check.

### 7.1 Predecessor audit, 2026-08-17 — read from code, and it changes the plan

The species list (`Plot_InclusiveKinematicSpectra_Raw.C:793`) is exactly the ten
the 30 existing panels cover, with correct antiparticle labels:
`D±`, `B±`, `Λc+/Λ̄c−`, `Λb/Λ̄b`, `Σb0/Σ̄b0`. **That is the proposed paper set**;
the addendum's minimum (D and B mesons, Λc, Λb) is a subset of it.

**The selection actually applied** — `PassCanonicalInclusiveSelection` (`:260`):

```
isFinal && central && IsDirectPrimaryStatus(status) && IsCentralKinematic(pt, eta, /*trigger=*/false)
```

with `IsCentralKinematic(pt, eta, false)` = `pt > 0.15 && |eta| <= 4.0` and
`IsDirectPrimaryStatus` = `status > 0 && 81 <= |status| <= 89`.

> ### ⚠ Two consequences the addendum's marker plan has to absorb
>
> **1. The spectra are not fully inclusive — the associate acceptance is already
> applied.** The pT histogram *begins* at 0.15 and the η histogram spans exactly
> ±4. So "draw associate pT > 0.15 and |η| ≤ 4 as markers" would place markers on
> the frame edges, where the data stops because of that very cut. Drawn that way
> a reader would read them as cuts sitting *inside* an inclusive distribution,
> which is the opposite of the truth. **Caption them as the spectrum's domain,
> not as a selection overlaid on it.**
>
> **The trigger marker is the informative one.** `pT > 1` sits properly inside
> the drawn range, so the reader can see what fraction of each species passes the
> trigger threshold. That marker earns its place; the other two do not.
>
> **2. `status 81–89` is a real selection and must not be called "prompt".**
> `PAPER_FIGURE_PROVENANCE.md` already records that `Model.tex:53` and `:129`
> mislabel this same status range as prompt. The panels inherit the range, so
> they would inherit the mislabel. The correct phrasing is **direct primary
> hadronisation products**.

**Still blocked on §6.3b** — same macro, same freeze contract.

---

## 8. WHAT THIS INVENTORY DOES NOT DO

It does not edit `Paper/**`. Every ⚑ row is a paper decision, and the manuscript
still points at dead-dataset files until the owner acts on §4 and §5. The
regeneration recipes are recorded so the remainder is mechanical.

---

## The balancing-yield variant family ⚖ THREE VARIANTS, UNDER OWNER EVALUATION

**No down-selection.** Three views of one observable, all developed to
publication standard. Which one (or which combination) the paper carries is an
owner and journal decision, not an engineering one.

| | V-FULL | V-EXTREMES | V-INTEGRATED |
|---|---|---|---|
| shows | all 11 N_ch classes | lowest + highest only | one integrated point |
| x axis | associate species | associate species | associate species |
| configured axis | 11 | **11** | **11 + integrated** |
| declares coverage on the figure | not needed | ✅ | ✅ |
| PNG | `0cf807b6…` | `63906e84…` | `88fdb628…` |
| receipt | PASS | PASS | PASS |
| status | ✅ **committed reference** | ✅ **committed reference** | ✅ **committed reference** |

> **PROMOTED AT MERGE, and the digests moved with the promotion.** The row above
> named the PRE-STYLING renders. The styled family superseded them on
> 2026-08-18 and is what the four closures below rest on, so the reference
> digests are now the styled ones (`GOLDEN_OUTPUTS.md` §9.6):
>
> | variant | before styling | committed reference |
> |---|---|---|
> | V-FULL | `f2973994e803b138…` | `0cf807b6750894c9…` |
> | V-EXTREMES | `7b65ecd5f032939a…` | `63906e847f243c79…` |
> | V-INTEGRATED | `f5e146e8baa379f8…` | `88fdb62845ccbcb6…` |
>
> **Styling moved no number**, asserted rather than assumed: 24 points against
> the pre-styling closure run and 24 against the styled V-FULL, both IDENTICAL
> by exact 17-digit string equality (§9.6.1).
>
> **The receipts pin plotter `003a39e3997b943f…`, which is commit `d63f52e`**,
> and two later commits changed the plotter — `1ff4b23` (baryon/meson) and
> `9b3e328` (correlation legend). Neither moved this family: the correlations
> run rendered the balancing canvas **byte-identically** at `88fdb628…`
> (`GOLDEN_OUTPUTS.md` §9.11). The reference is therefore reproducible from the
> branch tip, and that is measured rather than asserted.

**Every variant configures the whole axis.** The two filtered figures restrict
only what is *drawn*, via `bins_to_ignore`. Deleting a class from
`histograms_to_analyse` is still refused by the axis contract, and that refusal
is deliberate: a figure showing two of eleven classes with nothing saying so is
the silent re-binning the B6 family exists to prevent. Each filtered figure
therefore carries a self-declaration derived from the boundary artifact.

**Numerically these are the same measurement.** V-EXTREMES reproduces V-FULL's
c1 and c11 points and V-INTEGRATED reproduces the closure run's integrated
points, exactly, with no tolerance — `GOLDEN_OUTPUTS.md` §9.5.2.

**V-INTEGRATED is a new paper-facing quantity** and is pre-registered:
`docs/V_INTEGRATED_PREREGISTRATION.md` carries the definition, the unit-weight
ruling, the INTEGER-EXACT closure on all twelve keys, and the value table with
block SEMs at dof = 9.

> **RESOLVED 2026-08-18 — legend amendment.** ROOT auto-scaled these legends by
> row count, so one entry filled the box. `kBalancingLegendTextSize = 0.017` is
> now explicit at all four legend sites, measured as the centre of the
> [0.016, 0.018] plateau that reproduces V-FULL's legend byte-for-byte. Both
> filtered variants were re-rendered; **both PNGs changed** (V-EXTREMES' 2-entry
> legend had also been auto-scaled) and **all identity assertions still report
> IDENTICAL**, so no number moved. Superseded artifacts archived, not deleted —
> `GOLDEN_OUTPUTS.md` §9.5.0.
>
> **Remaining judgement for the owner:** one constant matching the eleven-entry
> panels necessarily makes the two- and one-entry legends small. They are legible
> at full resolution, and each filtered figure repeats the same information in
> its self-declaration line at a larger size — but if the owner prefers the
> filtered legends larger, that is a second constant and a second decision.

---

## Capability audit vs `main` — 2026-08-18

**Question asked: is there any plot `main` can produce that this branch cannot?**
**Answer: no, with one file to rule on.**

Read-only enumeration of `main @ 11884cf`:

| | count |
|---|---|
| `.C` files on main | 97 |
| of those, ROOT `SaveSource` artifacts under `Plots/` (outputs, not capability) | 48 |
| **source macros (actual capability)** | **49** |
| mapped to a branch counterpart by basename | **43** |
| no counterpart, but a recorded disposition | **5** |
| **no counterpart AND no disposition** | **1** ⚑ |

The 43 counterparts live in `plotting/` (16), `docs/history/studies/` (14),
`attic/` (9), `analysis/` (3) and `merging/` (1) — the restructure moved them,
it did not drop them.

Five have dispositions in the private removals log and repository census:
`count_events_bb_cc.C`, `reproduceCanvasPadError.C`, `ListHistos.C`,
`PlottingWizard.C`, `combinedCanvasPlots.C`.

### ⚑ The one finding, reported and NOT dispositioned here

**`Other/B_Balancing_GeneralPlotting_BEFORE_DOCUMENTATION.C`** has no branch
counterpart and no disposition in any record.

Measured, so the owner can rule with the facts:

- 3076 lines, against 2217 for `PlottingScripts/B_Balancing_GeneralPlotting.C`;
- **it defines no function the documented version lacks** — the extra ~993 lines
  are pre-documentation bulk, not additional capability;
- the documented version **is** preserved privately on this branch,
  byte-identical (sha `c41b52dc5440…` on both).

**No capability is therefore lost**, but the file itself has never been ruled on.
Writing a disposition for it is the owner's call, not this session's.

> ### ✅ RETIRED 2026-08-18 — owner ruling, re-issued on corrected evidence
>
> **`Other/B_Balancing_GeneralPlotting_BEFORE_DOCUMENTATION.C` is RETIRED.**
> The first issue of this ruling cited "no unique function", which this session
> disproved, so the retirement was held rather than recorded against a claim that
> had just failed. The owner re-issued it on the corrected facts, and those are
> what is recorded here:
>
> | evidence | value |
> |---|---|
> | line count against the documented version | **3076 vs 2217** |
> | unique function | **one** — `configureInputBeautyAndCharm`, lines **1557–1650** |
> | is it reachable? | **no.** All **four** call sites — 3017, 3033, 3046, 3058 — are **commented out**. It is dead code in its own file |
> | what it implements | the **superseded two-tune positional convention**: charm and beauty matched by position in a list ordered `{charm_monash, charm_junctions, beauty_monash, beauty_junctions}` |
> | documented version preserved | **byte-identical** in the private archive, sha `c41b52dc5440…` on both main@`11884cf` and this branch |
>
> **No reachable capability is unique to the retired file.** The one function the
> documented version lacks cannot be called from anywhere, and the convention it
> encodes was replaced by three tunes and an explicit registry.
>
> **Why the correction was worth the delay.** "No unique function" and "one
> unique function, dead in its own file" support the same disposition, but only
> the second is true, and a retirement is permanent and cites its evidence. The
> record now says what is actually the case.

### Open dispositions

| disposition | status |
|---|---|
| **REGENERATE** §3.1 figure 4 | ✅ **FINAL 2026-08-18, render #7** — `85a2488a…`, byte-identical across renders #5, #6 and #7; `GOLDEN_OUTPUTS.md` §9.13.4 |
| **REGENERATE** §3.1b the 30 species panels | ✅ **FINAL 2026-08-18, render #7 — 30/30 CLEAN** — caption moved above the frame; pixel checker `clean=30 struck=0`, render guard `ABOVE_FRAME` on all 30; digests §9.13.4 |
| **REGENERATE** §3.2 angular correlations (charm, beauty) | ✅ **CLOSED AND FINAL 2026-08-18** — legend defect fixed by measurement; `BEAUTYCorrelations_MONASH` `7238982c…`, `CHARMCorrelations_MONASH` `b426fd7f…`; balancing canvas still byte-identical `88fdb628…`, `GOLDEN_OUTPUTS.md` §9.11 |
| **REGENERATE** §3.3 balancing yields, integrated charm/beauty | ✅ **CLOSED 2026-08-18** — V-INTEGRATED, PNG `88fdb62845ccbcb623bf908a0ff0eedc8a822194a3c05dfbb5483882da1d4990`; coverage claim in §3.3a |
| **REGENERATE** §3.3 baryon/meson ratio | ✅ **SIGNED OFF 2026-08-18** — owner accepted `4d38492f…` as the fourth member of the balancing family; proposal until merge; `GOLDEN_OUTPUTS.md` §9.8 |
| **BUILD** the kinematic panel families | ✅ CLOSED — §9.4.5 |

### The four OWNER-DECIDE items — ruled 2026-08-18 under the owner's coverage test

The owner's ruling: any item whose content the styled balancing family **fully
covers** becomes SUPERSEDED by that family, with the coverage claim stated
explicitly for verification; any item not fully covered comes back described.

**The family's composition, which every claim below is measured against.** All
three variants draw the same ten mini-canvases — five beauty, five charm:
`{MONASH, JUNCTIONS, CLOSEPACKING}` plus `JUNCTIONS/MONASH` and
`CLOSEPACKING/MONASH` tune ratios, per flavour. Every one is
`drawBalancingPlots` or `drawBalancingPlotsTUNERatios`; **none is
`drawBalancingBaryonMesonRatioPlots`**. That last fact decides item 10.

| # | figure | ruling |
|---|---|---|
| 5 | `global_balancing_plots_multiplicity_charm_PDF.pdf` | **SUPERSEDED** by V-FULL |
| 7 | `global_balancing_plots_multiplicity_beauty_PDF.pdf` | **SUPERSEDED** by V-FULL |
| 9 | `globalCanvasYieldsPDF_215.pdf` | **SUPERSEDED** by V-FULL |
| 10 | `globalCanvasRelativeYieldsPDF_215.pdf` | ✅ **SUPERSEDED** — the signed-off baryon/meson figure of §9.8 draws the quantity the family lacked |

**Items 5 and 7 — the coverage claim, stated for verification.** V-FULL
(`0cf807b6750894c949eacf97c93c407aa65cddaa064d549a9e45c7bca738a3f2`) draws the
balancing yield across all eleven multiplicity classes, per tune, for both
flavours. Its five **charm** mini-canvases carry exactly what item 5 names and
its five **beauty** mini-canvases exactly what item 7 names.

> **The claim is about CONTENT, and one difference is packaging, not coverage.**
> The manuscript includes two files; V-FULL is one canvas holding both flavours.
> Superseding these two therefore still requires the §4.1 editorial change —
> two `\includegraphics` lines and their captions replaced by one. **What §4.1
> asked (a config change to emit two panels, or a manuscript change to take one
> canvas) is answered here as: take the one canvas.**

**Item 9 — the coverage claim.** The private legacy macro's `c2x3_yields`
canvas is "balancing yields for
beauty and charm on a 2x3 canvas": beauty and charm as the two **columns**, one
**row per tune**, and a tune-ratio **mini-pad** beneath each column
(`c20mini_yields`, `c21mini_yields`). V-FULL has that same structure — flavour
columns, a panel per tune, tune-ratio panels — built on three tunes where the
legacy canvas had two, on the committed eleven-class axis. **Content fully
covered, and extended.**

**Item 10 — NOT covered, returned with its description.**

> **One line, as ruled:** a 2×2 composite of the **baryon/meson relative**
> balancing yields — Λ_b/B and Λ_c/D — for beauty and charm, each panel carrying
> a ratio mini-pad beneath it (`c2x2_relYields`, same macro, line 1423, whose own
> comment reads "the global relative yield canvas for the baryon/meson ratios").

**Why it was not covered, and what changed.** The quantity it draws is the
baryon/meson ratio, and no canvas in the styled family drew that quantity — the
ten mini-canvases are yields and tune ratios. **Item 10 and REGENERATE §3.3
baryon/meson are the same content**, and they were to be ruled together.

> **Both now rest on one artifact.** The baryon/meson figure was built on
> 2026-08-18 (`GOLDEN_OUTPUTS.md` §9.8, PNG `4d38492f…`, receipt PASS) and draws
> exactly the missing quantity, per multiplicity class, for both flavours.
> **Item 10 and §3.3 therefore close together on owner sign-off of that figure**,
> or come back together if it is refused.

> **capability audit vs main @ `11884cf`: 49 macros: 48 mapped, 1 retired by
> owner ruling.**
>
> **RE-ISSUED 2026-08-18.** The previous form of this line carried an exception
> because the retirement behind it had been stopped on an evidentiary error. The
> ruling was re-issued on corrected evidence and executed above, so the audit
> closes with no exception: every one of the 49 source macros on main is either
> mapped to a branch counterpart, carries a recorded disposition, or is retired.
