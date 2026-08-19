# Publication polish: the canvas becomes readable — 2026-08-16 (twentieth session)

**Suite 46/46 throughout. Wall clock 21:19–22:35 CEST.** `stbc-i3` up
**3 d 22 h**, boot 2026-08-12 23:06:56 — **no reboot**.

> **Headline: the three-tune canvas is publication-quality. Six defects fixed,
> three of them named in the run record and three found only by rendering and
> looking. No number moved, and that is measured: 220 bin contents and 220 bin
> errors identical pre- and post-polish. Two design decisions are rendered and
> proposed rather than chosen silently.**

---

## 1. The merge has not completed — no STATE.md change

`CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=CLOSEPACKING` is **absent**; only
`tune=MONASH` is present. Merge `315689` alive, on its **JUNCTIONS** closure
(worker `544364`, ~100 ticks/s — 100 % of a core). Supervisor `316182` alive at
**0 restarts**; EOL watcher `2566164` alive and correctly **not** fired.

**So the completion branch of the brief did not apply**, the campaign is **not**
recorded COMPLETE, and no pinfile or checkout was touched. Rough ETA from the
MONASH pass (14 h 51 m) and CPU consumed: **JUNCTIONS ≈ 03:30, CLOSEPACKING
≈ 18:30 on Aug 17**.

## 2. The canvas — six changes, all presentation

`docs/plotting_validation/hf_run3_v1_threetune_20260816/RUN_RECORD.md` appendix
carries the full table. In brief:

**The three named in the run record.**

1. **Every panel names its tune.** `canvas_title` per canvas. **No drawing-code
   change was needed** — `canvas_title` was already plumbed to `SetTitle` and was
   empty in every canvas, which is precisely *why* the panels were anonymous.
2. **One legend, four columns**, instead of eleven rows repeated in all ten
   panels. The eleven classes are the same series everywhere.
3. **Ratio panels 0.6–2.5, linear, measured not defaulted.** The 88 drawn ratio
   bins span **0.6605–2.2837**, median 0.9561; the old 0.2–5.0 log axis spent
   **61 %** of its range on nothing.

**The three that only looking found** — and two of them only became visible once
the first three were fixed:

4. **Titles were drawn on the frame line with ticks cutting the lettering.**
   ROOT places the title at the top of the *pad* while the frame is inset by the
   margins, so a title needs top-margin room: 0.03 (~12 px of a 387 px pad) → 0.10.
5. **The log y-axis carried exactly one label.** A log range inside one decade
   gets one labelled tick from ROOT, so the yield panels showed only `10⁻¹` —
   shape readable, values not. `SetMoreLogLabels()` now labels 2–5 ×10⁻² and ×10⁻¹.
   **This is the single biggest legibility gain of the session.**
6. **MONASH's Λ_b sat on the axis floor** at 0.013; the six yield panels span
   0.0180–0.2087, so the floor moved to 0.010.

**Drawing-code changes: two, neither touching analysis, selection or binning.**
An optional `legend_columns` field — parsed with `.value(..., 1)` so
configurations written before it exists still parse — applied at the four legend
sites, and `SetMoreLogLabels()` at the four axis setups.

## 3. The cross-check: no number moved

**Measured, not asserted.** The canvas macro ROOT writes contains every drawn
bin, so the pre- and post-polish macros are directly comparable:

```
10 panels, same set
220 bin contents and 220 bin errors compared
RESULT: IDENTICAL — no number moved
```

On the SVG side, fig 1's **42 cells — every mean and every SEM in both panels —**
still match `docs/THREE_TUNE_CENTRAL_TABLE.md` exactly: **0 mismatches**, before
and after.

**Byte-determinism:** the canvas is identical across **three** independent runs,
and the two receipts compared field-for-field differ in **no field**. All three
SVGs are byte-identical across two runs. (An earlier receipt digest belongs to
the *pre-fix configuration*, not to an irreproducible run — checked rather than
assumed.)

## 4. The SVG fresh-eyes pass found two more

- **fig 2**: value labels drawn **through** the upper error-bar caps in the
  beauty panel, where the SEM is a sixth of the bar height. Labels now anchor
  above the error bar. *(Flagged in the previous session's report and not fixed
  then; fixed now.)*
- **fig 1**: the legend header `tune` sat 7 px under the *CentralGround* axis
  label and read as part of the axis row. Dropped clear.
- **fig 3**: clean, unchanged.

Digests updated in `GOLDEN_OUTPUTS.md` §2.12 — fig 1 `316a7d99…`, fig 2
`ffec6a3d…`, fig 3 `e687b953…` unchanged.

## 5. Two design decisions, rendered and proposed — NOT applied

> ### ✅ RULED 2026-08-17 — **both REJECTED**, the shipped layout is unchanged
> Variant A rejected: near-unity ratios label badly on log, so ratio panels stay
> **linear**. Variant B rejected: **the paper's central comparison is
> ratio-vs-ratio**, so the two ratio panels stay **grouped** and adjacent —
> a firmer reason than the "readability preference" this record offered below.
> Renders renamed `REJECTED_variant{A,B}_*.png`; the rulings and their reasoning
> live in the run record §P4. **Nothing below is rewritten.**

Both are owner-visible per the brief, and both renders are committed beside the
run record.

- **`PROPOSAL_variantA_log_ratio_panels.png`** — ratio panels on log.
  **Recommendation: keep linear.** Log labels a near-unity axis as
  `6×10⁻¹, 7×10⁻¹, 8×10⁻¹, 9×10⁻¹, 1, 2` — scientific notation for numbers
  around one, harder to read than `0.6, 0.8 … 2.4`. Log would earn its place if
  the spread were wider than the measured 0.66–2.28.
- **`PROPOSAL_variantB_monash_first_ordering.png`** — MONASH on top with each CR
  tune's ratio row directly beneath the tune it divides, rather than the
  CLOSEPACKING/JUNCTIONS/MONASH/ratios stack inherited from the v2 layout.
  **No recommendation**: it is a readability preference and pairing each
  numerator with its own ratio row is a real argument on the other side.

## 6. Provenance of the shipped canvas

| | |
|---|---|
| ROOT | `v6-30-01-alice5-2`, `root-config --version` = **6.30.01** — on pin |
| configuration | sha256 `6f5b4c85…` (generated; `--check` asserted by the suite) |
| plotter source | sha256 `6dace202…` |
| receipt | `payload_sha256` `5eecd9ed…`, `tune_count=3 status=PASS` |
| canvas | sha256 `54549915…` |

**The receipt guard behaved correctly throughout** and was worked with, not
around: each configuration or plotter change moves a pinned sha, so every render
started from a clean output directory and the superseded outputs were archived
under `plot_archive/` rather than deleted.

## 7. Boundaries

No number changed. No `Paper/**`, no disk cleanup, no new figures beyond the
certain set, no pinfile, no checkout advance. `STATE.md` untouched — the merge
has not completed.

## 8. For the next session

1. **The gate is CLOSED** until `tune=CLOSEPACKING` appears (≈ 18:30 Aug 17) and
   the merge exits; then verify the EOL watcher stopped the supervisor and
   record the campaign COMPLETE.
2. **The two design proposals in §5** want an owner ruling.
3. **The I2 flags** remain the one open item on the FINAL table.
