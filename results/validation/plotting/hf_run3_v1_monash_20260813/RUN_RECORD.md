# The first v3 plotting run — MONASH, HF_RUN3_V1, 2026-08-13

**This is the recipe, not a digest.** Per `docs/GOLDEN_OUTPUTS.md` §0.3,
ROOT-generated figures are contracted on **pinned inputs + pinned ROOT + the
recorded command**, not on a byte digest. The receipt beside this file *is*
digest-contracted — it carries its own `payload_sha256`, and the stack refuses to
overwrite a differing one.

## The command

```
DATASET_SELECTOR=config/dataset_selector_hf_run3_v1.json \
THNSPARSE_COMPLETE_ROOT_CONFIG=plotting/configuration_multiplicity_HF_RUN3_V1_MONASH_THnSparse_complete_root.json \
bash plotting/run_paper_plots.sh thnsparse-complete-root
```

Exit 0. 2,102 log lines.

## Where and with what

| | |
|---|---|
| host | `stbc-i3.nikhef.nl`, from a checkout rsynced to `/data/alice/ipardoza/hadronization_v3_plotting_run` |
| repository state | branch `physics-focus`, commit `47d6396` plus this record |
| ROOT | **6.30/02**, `/cvmfs/sft.cern.ch/lcg/views/LCG_105/x86_64-el9-gcc13-opt` |
| when | 2026-08-13, ~16:45–17:15 CEST |
| plotting configuration | sha256 `966ba46cbc560a138f0cc7d020ac3963c194c8e35791e47c9c2522b3f9df5038` |
| class-boundary artifact | sha256 `3b0554fe6c291a26ba03b0524975892754e9a0e75896b203c24d05e853d195b5` |
| central inputs | `/data/alice/ipardoza/hadronization_merged/complete_root_HF_RUN3_V1_MONASH/` — 8 pair files read, 8 validated |
| block inputs | `…/SUBSAMPLES_HF_RUN3_V1/combined_root_subSamples_MONASH/combined_root_{1..10}` — 80 files validated |

> **ROOT differs from the anchor's pin.** `MONASH_CENTRAL_TABLE.md` was produced
> under the ALICE build **6.30/01**; this ran under LCG **6.30/02**. Same minor
> version, different build. Recorded rather than smoothed over.

## What the axis did

```
MULTIPLICITY_COMMON_BOUNDARIES artifact=…/config/multiplicity_class_boundaries_v1.json
  artifact_sha256=3b0554fe… classes=11 tunes_compared=1 reference_tune=MONASH
  identical_across_tunes=PASS
```

Every emitted boundary equals the committed artifact:

| percentile key | emitted N_ch | artifact says |
|---|---|---|
| 100 | 0 | c1 lower edge −0.5 → first N_ch is 0 |
| 88.197 | 2 | c2 lower edge 2.5 → c1 ends at 2 |
| 80.597 | 3 | c3 lower edge 3.5 |
| 65.937 | 5 | c4 lower edge 5.5 |
| 59.850 | 6 | c5 lower edge 6.5 |
| 50.308 | 8 | c6 lower edge 8.5 |
| 43.030 | 10 | c7 lower edge 10.5 |
| 34.614 | 13 | c8 lower edge 13.5 |
| 26.154 | 17 | c9 lower edge 17.5 |
| 17.124 | 23 | c10 lower edge 23.5 |
| 8.422 | 32 | c11 lower edge 32.5 |
| 0 | 4095 | axis top; the ruled top class is open-ended |

`partition: coverage PASS, disjointness PASS, achieved_weighted_fraction 1.0`
exactly, with underflow and overflow exactly 0.

**A one-tune run satisfies the cross-tune assertion vacuously**, so it was also
run over **MONASH + JUNCTIONS** central inputs:
`tunes_compared=2 … identical_across_tunes=PASS`, with all twelve
`MULTIPLICITY_BOUNDARY` lines agreeing tune for tune. That is the demonstration;
the one-tune figure is the deliverable.

## Cross-checks against committed MONASH anchors

| quantity | this run | committed anchor | |
|---|---|---|---|
| pair registry sha256 | `ea9b0232c1be8415…ddee23` | `MONASH_CENTRAL_TABLE.md` §Provenance, same value | **match** |
| events | `regular_bin_integral` = 100,000,000 | "100 M events" | **match** |
| observable | `hMULTIPLICITY` titled `NCH_PRIMARY_CHARGED_ETA10_V1`, 4096 bins, −0.5…4095.5 | artifact's `multiplicity_primary_charged_eta10_v1` | **same definition** |

## ⚠ An open number, flagged rather than explained

The receipt publishes each class's realised fraction **in the campaign**. Against
the MONASH-**MB** label widths they are:

| class | N_ch | MB label width | campaign fraction | residual |
|---|---|---|---|---|
| c1 | 0–2 | 11.803 % | 11.776 % | −0.03 pp |
| c2 | 3 | 7.600 % | 7.801 % | +0.20 |
| c3 | 4–5 | 14.660 % | 15.283 % | +0.62 |
| c4 | 6 | 6.087 % | 6.493 % | +0.41 |
| c5 | 7–8 | 9.542 % | 10.837 % | +1.30 |
| c6 | 9–10 | 7.278 % | 8.732 % | +1.45 |
| c7 | 11–13 | 8.416 % | 10.051 % | +1.64 |
| c8 | 14–17 | 8.460 % | 9.223 % | +0.76 |
| c9 | 18–23 | 9.030 % | 8.569 % | −0.46 |
| c10 | 24–32 | 8.702 % | 6.764 % | −1.94 |
| c11 | ≥33 | 8.422 % | 4.472 % | **−3.95** |

A residual is **expected and is the point** — the labels are MB percentiles and
the campaign is heavy-flavour triggered, which is exactly why the ruling
publishes the per-sample fraction instead of hiding it inside the class
definition.

**What is not explained is the SIGN.** A heavy-flavour-triggered sample would
naively sit *above* minimum bias at high activity, and this one sits well below
it: the top class holds 4.47 % of campaign events against an 8.42 % MB label.
The observable is identical (`NCH_PRIMARY_CHARGED_ETA10_V1` in both), so this is
a property of the two samples, not of two definitions. `b4_multiplicity_mb`'s
`run_meta.txt` shows both an `mb` and a `hard` run per tune, but **only the `mb`
CSVs were kept**, so the comparison that would settle this is not available in
the repository.

> **This does not affect B6.** The boundaries are absolute, identical across
> tunes, and equal to the artifact. It affects how the label is *read*, and it
> should be resolved before any per-class number is written into the manuscript.

## The figure

`global_balancing_plots_multiplicity_HF_RUN3_V1_MONASH_PNG.png`, beauty (left)
and charm (right), eleven activity classes as series against associate species.

**It was looked at, and it is correct but weak as a figure.** The dependence is
real and monotonic in charm mesons — D⁻ balance rises 0.1889 → 0.2087 (+10.5 %)
from the lowest-activity class to the highest — and roughly flat in beauty
(B⁻ 0.1140 → 0.1180, +3.5 %). On `drawBalancingPlots`' layout, which puts
*species* on x and classes in the legend, a 10 % trend across eleven overlaid
series is nearly unreadable however the y-range is set; the range here was
already tightened from the inherited `(1e-4, 0.8)`, which had collapsed all
eleven into a single line.

**Recommendation, not a change:** the multiplicity dependence wants activity on
the x-axis, or a ratio to the integrated class. That is figure design and was
left for whoever owns the paper figure.

> The first attempt at this run reproduced the v2 canvas faithfully and drew
> **one** class, because every canvas in the reduced v2 configuration lists ten
> of the eleven classes in `bins_to_ignore`. That was caught by looking at the
> rendered output, not by any check in the stack.
