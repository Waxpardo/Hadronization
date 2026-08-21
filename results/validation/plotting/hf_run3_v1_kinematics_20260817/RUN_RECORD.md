# Run record — charged-multiplicity spectrum and inclusive pT/η/φ, HF_RUN3_V1

**Rendered 2026-08-17** from the sealed, publication-authorized HF_RUN3_V1
freeze, on the pinned generator/analysis stack.

| | |
|---|---|
| macro | `plotting/Plot_InclusiveKinematicSpectra_Raw.C` |
| targets | `run_paper_plots.sh multiplicity-spectrum`, `… kinematic-spectra` |
| dataset selector | `config/dataset_selector_hf_run3_v1.json` — `canonical`, `publication_eligible: true` |
| authorization | `docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md` |
| freeze | `campaigns/HF_RUN3_V1/freeze/`, manifest sha256 `fcd96eaebd4dc11f071a2c8db8849f6a4cc19b764622a796664e524b27d0fc80` |
| ROOT | **6.30/01** (`v6-30-01-alice5-2`, CVMFS), the pinned analysis version |
| raw input | `/data/alice/ipardoza/hadronization_production/HF_RUN3_V1/raw` |
| contract line | `tunes=3 jobs_per_tune=1000 events_per_job=100000 events_per_tune=100000000 rows=3000 blocks=10 validation_log=absent shape=derived` |

---

## 1. THE TWO SELECTIONS, VERBATIM FROM THE FILLING CODE

**These are for the captions. They are read from source, not inherited from the
previous figure's label.**

### 1.1 The multiplicity counter — what `hMULTIPLICITY` holds

`generation/producer/heavyflavourcorrelations_status.cpp:1058` calls
`CountsNchPrimaryChargedV1`, defined at
`generation/producer/HeavyFlavourUtils.h:539`:

```
isFinal && isCharged && !hasHeavyConstituent &&
    IsMultiplicityKinematic(pt, eta, kMultiplicityEtaCentral)
```

and `IsMultiplicityKinematic` (`:533`) is
`pt > kMultiplicityPtMin && std::abs(eta) <= etaMax`, with
`kMultiplicityPtMin = 0.15` and `kMultiplicityEtaCentral = 1.0`.

> **Caption wording:** primary charged particles, **pT > 0.15 GeV/c**,
> **|η| ≤ 1.0**, **heavy-flavour excluded**.
>
> Three details a shorter label loses. The η cut is **inclusive** (`≤`, not `<`).
> Heavy flavour is **excluded** — `!hasHeavyConstituent`, the same "heavy EXCL."
> convention the b4 calibration logs carry. And the branch names itself
> `multiplicity_primary_charged_eta10_v1`, which is the identifier to quote if
> the definition is ever questioned.

### 1.2 The associate acceptance already applied to the pT/η/φ spectra

`plotting/Plot_InclusiveKinematicSpectra_Raw.C::PassCanonicalInclusiveSelection`:

```
isFinal && central && IsDirectPrimaryStatus(status) &&
    IsCentralKinematic(pt, eta, /*trigger=*/false)
```

with `IsCentralKinematic(pt, eta, false)` = `pt > 0.15 && |eta| <= 4.0`
(`HeavyFlavourUtils.h:467`) and `IsDirectPrimaryStatus` =
`status > 0 && 81 <= |status| <= 89` (`:472`).

> **Caption wording:** inclusive spectra of **direct primary hadronisation
> products** (status 81–89), **pT > 0.15 GeV/c**, **|η| ≤ 4.0**.
>
> **The spectra are not unrestricted.** The associate acceptance is already
> applied, so the pT histogram *begins* at 0.15 and the η histogram spans exactly
> ±4. A caption must present those as the spectrum's **domain**, not as cuts
> overlaid on an inclusive distribution — and the trigger threshold
> (**pT > 1 GeV/c**) is the one that sits properly inside the drawn range.
>
> **Status 81–89 is to be described as direct primary hadronisation products.**
> `plotting/PAPER_FIGURE_PROVENANCE.md` records that `Model.tex:53` and `:129`
> mislabel this same range; the figures must not inherit that.

## 2. THE CLASS-BOUNDARY CLOSED LOOP — re-verified this session

Boundaries from `config/multiplicity_class_boundaries_v1.json`; percentile
labels recomputed from `AnalysisScripts/anchors/b4_multiplicity_mb/nch_mb_MONASH.csv`
(172 429 events) as the fraction strictly below, in the receipt's top-percentile
convention; compared against
`docs/plotting_validation/hf_run3_v1_threetune_20260816/multiplicity_boundary_receipt_v1_polished.json`.

| class | boundary N_ch | recomputed MB % | frozen receipt % | \|Δ\| | threshold |
|---|---|---|---|---|---|
| c1 | −0.5 | 100.000000 | 100.000 | 0.000000 | 0 |
| c2 | 2.5 | 88.196881 | 88.197 | 0.000119 | 2 |
| c3 | 3.5 | 80.597231 | 80.597 | 0.000231 | 3 |
| c4 | 5.5 | 65.937284 | 65.937 | 0.000284 | 5 |
| c5 | 6.5 | 59.849561 | 59.850 | 0.000439 | 6 |
| c6 | 8.5 | 50.307663 | 50.308 | 0.000337 | 8 |
| c7 | 10.5 | 43.030465 | 43.030 | 0.000465 | 10 |
| c8 | 13.5 | 34.613667 | 34.614 | 0.000333 | 13 |
| c9 | 17.5 | 26.153953 | 26.154 | 0.000047 | 17 |
| c10 | 23.5 | 17.123570 | 17.124 | 0.000430 | 23 |
| c11 | 32.5 | 8.422017 | 8.422 | 0.000017 | 32 |

**Worst |Δ| = 0.000465, tolerance 0.0005 — PASS on all eleven.** The residual is
the receipt's own three-decimal storage, not a disagreement. The percentiles are
MB *translations* of absolute boundaries, which is why they are not round
numbers.

> **The same arithmetic exposed a transcription error elsewhere.** c5's boundary
> is 59.849561 %, which rounds to **59.8**; the plotting configs' hand-written
> legend label says **59.9**, having rounded the receipt's 3-decimal 59.850 a
> second time. See the canvas-polish proposal.

## 3. ENERGY LABEL

`Plot_InclusiveKinematicSpectra_Raw.C:825` returns `pp, #sqrt{s} = 13.6 TeV`.
**No plotting source in the repository contains a "14 TeV" string**; the 14 on
the superseded PNG exists only as pixels and predates the current generator.
