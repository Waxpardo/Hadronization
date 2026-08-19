# Figure census and regeneration — 2026-08-17 (evening)

**Suite 49/49 → 50/50 (one new contract test). Wall clock 20:21–21:3x CEST.**
Local `physics-focus` `c532a1d` → `3929faf`; Nikhef checkout unmoved at
`8650a047` (no advance work, as briefed). Retry clusters `5526031`–`5526033`
running, 0 held.

> **Headline: the census is complete — 148 figures, one disposition each — and
> the figure-4 work found a real defect and fixed it. The B6 boundary-artifact
> update had reached the boundaries macro but NOT the macro that makes the
> manuscript's figure, which was drawing production-sample quantiles under
> minimum-bias labels. Fixed, and verified as a closed loop against the frozen
> receipt to better than the receipt's own rounding. The render is blocked one
> owner action away, at a gate that is working correctly.**

---

## 1. The census — `docs/FIGURE_INVENTORY.md`

| disposition | count |
|---|---|
| REGENERATE | 8 |
| BUILD (kinematic panels) | 2 families, 32 files |
| OWNER-DECIDE ⚑ | 4 |
| SUPERSEDED | 6 |
| RETIRE ⚑ | 106 |
| **total** | **148** |

**The manuscript includes 10 figures and all 10 resolve to files that exist.**
Nothing in the draft is a broken reference; the problem is that the files come
from the dead dataset.

**The largest single retire block is not this paper's work at all.** Ten `.eps`
files in `figures/` — `BFieldVsTime`, `deltaGammaAVFD`, `cmeResultsVsModelsPbPb5TeV`
and seven more — belong to a **chiral-magnetic-effect / AVFD analysis**. They are
template leftovers, referenced by nothing. The other 95 retirements are
exploratory plots that are **two-tune** (the analysis is now three) or binned in
**20 % multiplicity slices** (the axis is now the committed 11-class
common-absolute partition), so they cannot be updated — only replaced.

## 2. ⛔ The B6 update had not reached the figure-4 macro

**This is the session's most valuable finding, and it is exactly what the brief
asked to verify before running.**

| macro | boundary source | B6 |
|---|---|---|
| `Plot_MultiplicityDistribution_PercentileBoundaries.C` | `LoadCommonBoundaries(...)` — the artifact | ✅ updated |
| `Plot_InclusiveKinematicSpectra_Raw.C` — **the manuscript's figure** | `CalculateMultiplicityThreshold(hist, p)` — a quantile of the drawn histogram | ⛔ **not updated; zero references to the artifact** |

**Wrong on two independent counts, not one.** The histogram it quantised is the
**production** sample — HardQCD, `pTHatMin = 2` — while the percentile labels are
defined on the **MONASH minimum-bias** distribution. Boundaries from one
distribution drawn under labels from another. And
`config/multiplicity_class_boundaries_v1.json` says in its own text that it is
the one definition and that no consumer may carry a copy, *"because two
definitions drift, and the axis is the thing every per-multiplicity number is
conditioned on."* This macro was a third consumer that never read it.

### 2.1 The fix, and the closed loop that proves it

Boundaries now come from the artifact; labels are **recomputed** from the
committed MB anchor by the same rule as `make_paper_figures.py`.

**Verified against the frozen three-tune receipt — all eleven boundaries:**

```
 boundary   recomputed %    frozen receipt %   Δ
    -0.5      100.0000          100.000        0.000000
     2.5       88.1969           88.197        0.000119
     3.5       80.5972           80.597        0.000231
     5.5       65.9373           65.937        0.000284
     6.5       59.8496           59.850        0.000439
     8.5       50.3077           50.308        0.000337
    10.5       43.0305           43.030        0.000465
    13.5       34.6137           34.614        0.000333
    17.5       26.1540           26.154        0.000047
    23.5       17.1236           17.124        0.000430
    32.5        8.4220            8.422        0.000017
```

**The residual is the receipt's own three-decimal rounding.** The percentiles are
not round numbers precisely because they are MB *translations* of absolute
boundaries — which is what makes this a real check rather than a tautology.

### 2.2 The test, and two structural facts it had to learn

`tests/test_multiplicity_inset_boundary_source.py` pins the loop and fails
against the pre-fix macro. Writing it surfaced two things a formula alone would
have got wrong, and both are now asserted rather than skipped:

1. **The receipt carries one more row than the artifact has boundaries** — the
   open-ended top class is stored as percentile `0.0` with the overflow sentinel
   `4095`. The test asserts the eleven recomputed values are a subset and that
   the single uncovered row *is* that sentinel, so a boundary that quietly
   failed to match cannot hide in the count.
2. **The lowest boundary clamps.** `-0.5` has formal inclusive upper `-1`; N_ch
   cannot be negative, so the receipt stores `0`. Asserted explicitly.

> **A smaller lesson, my own.** The first two versions of the test failed against
> the *fixed* macro, because the assertions matched the comment that documents
> the removal. Tests about code must read code: the checks now strip `//`
> comments first. A test that cannot tell an explanation from the defect it
> explains would have blocked every future correct edit.

## 3. The label audit — done against the data

| label | verdict |
|---|---|
| **√s** | ✅ **the code is already right**: the macro emits `13.6 TeV`. No plotting source anywhere contains a `14 TeV` string — **the 14 exists only as pixels in the stale PNG**, predating the current generator |
| **counter** | ⚠ needs to be made specific in the caption |

Read from the filling code, not assumed —
`heavyflavourcorrelations_status.cpp:1058` → `HeavyFlavourUtils.h:539`:

```
isFinal && isCharged && !hasHeavyConstituent && pT > 0.15 && |eta| <= 1.0
```

**Two details the old label omits.** The η cut is **inclusive** (`≤`, not `<`),
and **heavy flavour is excluded** — the same "heavy EXCL." convention the b4
calibration logs carry. "Charged multiplicity" alone is compatible with several
different counters, so the caption must say **primary charged, |η| ≤ 1,
pT > 0.15 GeV/c, heavy-flavour excluded.**

## 4. ⛔ The render is blocked at an owner gate, and the gate is right

Attempted on Nikhef with **pinned ROOT 6.30/01**. The macro compiled and then
refused:

```
ERROR: selector mode requires a consistent status/publication-eligibility pair
```

`ResolveDatasetInputMode` admits `canonical`+eligible or `legacy`+ineligible.
**HF_RUN3_V1 is `canonical_candidate` + ineligible, which is deliberately
neither.** Two owner prerequisites:

1. **The canonical manifest does not exist** — `campaigns/HF_RUN3_V1/freeze/` is
   absent. Building it *seals the campaign*, a dataset decision.
2. **The selector must be promoted** to `canonical` / `publication_eligible:
   true` with an authorization and its sha256.

> **Not worked around, and it should not be.** The gate exists so a figure cannot
> reach the manuscript from an unauthorized dataset — the same principle as this
> census's rule about the dead dataset, pointing the other way. Everything
> upstream is done: macro fixed, compiles on pinned ROOT, raw data present
> (1000 files × 3 tunes), audits complete and verified.

**The same gate covers the §7 kinematic panels** — same macro, same resolver — so
the addendum's build is blocked identically, not separately.

## 5. E5 exposure, per figure

| family | verdict |
|---|---|
| figure 4 | ✅ **safe by construction** — `hMULTIPLICITY` per **raw** file; raw files are disjoint event sets with no trigger axis, so the 24×/26× replication cannot arise |
| kinematic panels | ✅ **safe by construction** — raw heavy-hadron vectors. This is why the addendum's "raw, not pair files" ruling is the right one |
| angular correlations | ✅ safe — `hCorrelations` is per-pair |
| balancing yields | ⚠ **not yet checked** — the one family that could inherit E5; recorded as a precondition in the inventory §6.1 |

## 6. Boundaries respected

`Paper/**` **read-only** — read for the include list, never written; every dead
figure is flagged with its named replacement. No systematics harvest. No advance
work; the Nikhef checkout stayed at `8650a047`. Deploy `72ca4e39` untouched. The
frozen checkout was not written: the fixed macro went to a **source-only scratch
deploy** at `/data/alice/ipardoza/figure_deploy_20260817` (~1 MB).

## 7. For the next session

1. **The two owner prerequisites in §4** gate every raw-read figure. Nothing else
   blocks figure 4 or the kinematic panels.
2. **The balancing-yield E5 check** (§5) is the precondition for the three
   THnSparse regenerations, and `PAPER_FIGURE_PROVENANCE.md`'s **610 incomplete
   subsample-coverage cases** must be re-audited clean against merged v3 first.
3. **Four owner decisions** are waiting in the inventory §4 and §5.4: two
   multiplicity panels vs one combined canvas, the two legacy `_215` canvases,
   and the commented-out introduction figure.
