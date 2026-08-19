# V-INTEGRATED — pre-registration of the multiplicity-integrated balancing yield

**Written 2026-08-18, before the observable is built.** A new paper-facing
quantity is registered before it is measured, so the method cannot be chosen
after seeing the numbers.

---

## 1. THE OBSERVABLE

The multiplicity-integrated balancing yield per trigger, one point per associate
species per tune.

**It is a ratio, and the order of operations is the whole definition:**

```
Y_int  =  ( Σ_c N_OS,c  −  Σ_c N_SS,c )  /  Σ_c N_trig,c
```

Counts are integrated across the eleven multiplicity classes **first**, and the
ratio is formed **once**.

> **NEVER the mean of per-class ratios.** `⟨(N_OS,c − N_SS,c)/N_trig,c⟩_c` is a
> different estimator: it weights every class equally regardless of how many
> triggers it holds, so the low-activity classes — which hold most of the
> minimum-bias sample and the fewest triggers — would dominate a quantity that
> is supposed to be trigger-normalised. The two agree only if the per-trigger
> yield is independent of multiplicity, which is precisely the thing the
> multiplicity-differential canvas exists to test.

The existing per-class yield is `calculateOneYield`
(`plotting/improvedPlotting_THnSparse.C`), which normalises each ΔΦ spectrum by
its own trigger count and integrates the difference. It already enforces
`N_trig,OS == N_trig,SS`, so the denominator is unambiguous. V-INTEGRATED sums
the numerator and denominator histograms across the eleven classes and makes
**one** such call.

## 2. THE WEIGHTING QUESTION, SETTLED BEFORE ANY TOLERANCE WAS CHOSEN

The closure below is only meaningful if the counts are integers. They are filled
through a weighted path:

```
analysis/status_analysis_THnSparse_qq.C
  :1009   trigger.histogram->Fill(triggerValues, eventWeight);
  :1143   pair.associate->Fill(associateValues, eventWeight);
  :1144   pair.correlation->Fill(correlationValues, eventWeight);
```

and `eventWeight` is `pythia.info.weight()`
(`generation/producer/heavyflavourcorrelations_status.cpp:891`).

**So weighting enters the code path.** Measured rather than assumed, on the
sealed campaign:

| sample | entries | weights ≠ 1.0 | min | max |
|---|---|---|---|---|
| MONASH jobs 1, 250, 500, 750 | 400 000 | **0** | 1 | 1 |
| JUNCTIONS jobs 1, 250, 500, 750 | 400 000 | **0** | 1 | 1 |
| CLOSEPACKING jobs 1, 250, 500, 750 | 400 000 | **0** | 1 | 1 |
| **total** | **1 200 000** | **0** | **1** | **1** |

Comparison against `==` on the exact double, not a tolerance. `sum == entries`
held exactly for every file. This is consistent with the campaign's independent
report of `selected particles=39421891  selected weighted sum=3.94219e+07`.

> **RULING FOR THIS CAMPAIGN: the counts are unweighted.** `pTHatMin` restricts
> phase space; it does not weight events. Histogram contents are therefore exact
> integers held in doubles, and integer summation in double precision is exact
> below 2⁵³ — far above any count here. **Integer-exact closure is available and
> is what will be asserted. No tolerance is introduced.**
>
> **This is contingent on the data, not on the code.** The code path would carry
> a non-unit weight if one ever appeared, and the closure would then be a
> float comparison with no principled tolerance. The assertion therefore carries
> an explicit **unit-weight precondition**: if any bin content is non-integral,
> the closure **fails loudly** rather than being relaxed. A future weighted
> campaign must come back to the owner, not be given an epsilon.

## 3. THE CLOSURE, ASSERTED BEFORE ANY STATISTICS

The eleven classes tile the minimum-bias sample contiguously over 0–100 % with
no gap and no overlap (verified: `c1[88.197,100.000] … c11[0.000,8.422]`).
Integrated therefore **is** the full sample, which makes the closure exact
rather than approximate:

> **Per species, per tune:** the sum over the eleven classes of the OS−SS counts
> must equal the counts obtained by projecting the same THnSparse over the full
> multiplicity range, **as integers**. Likewise for the trigger denominator.

The two sides are computed by different routes — eleven restricted projections
summed, against one unrestricted projection — so agreement is a real check on
the class definitions tiling the axis, not an identity.

**Failure is not a tolerance question.** A mismatch means the classes do not
tile the sample (a dropped class, a `bins_to_ignore` entry, an off-by-one on a
boundary bin), and the correct response is to fix the axis, not to widen an
epsilon.

## 4. THE STATISTICS — identical to every published number

No new estimator. The procedure already used for every per-class point
(`calculateSubsampleStatistics`, `plotting/improvedPlotting_THnSparse.C:2920`):

| step | rule |
|---|---|
| blocks | ten, by `canonical_slot % 10` |
| per block | the integrated yield is formed **nonlinearly inside the block** — sum that block's counts across classes, then one ratio |
| central value | the same construction on the full sample |
| spread | `stdDev` with **dof = n − 1 = 9** |
| quoted error | `SEM = stdDev / √n` |

> The per-block quantity is a ratio, so it must be formed **inside** each block
> and never as a ratio of block means. This is the same discipline the per-class
> points already follow; V-INTEGRATED introduces no exception.

## 5. WHAT IS NOT YET DONE

At the time of writing: the observable is **specified and unblocked** —
the weighting question is settled, the closure rule is fixed, and the statistics
are inherited rather than invented — but **not implemented**. The yield loop
must gain the cross-class summation, and the closure must be asserted in code
before any V-INTEGRATED number is quoted or rendered.

**No V-INTEGRATED value appears anywhere in this repository yet, and none may be
quoted until the closure above has run and passed.**

---

## 6. RESULT — measured 2026-08-18, closure first

Run: `THNSPARSE_COMPLETE_ROOT_CONFIG=plotting/configuration_multiplicity_HF_RUN3_V1_VINTEGRATED_CLOSURE.json`
`bash plotting/run_paper_plots.sh thnsparse-complete-root`, wrapper PID 3204957
on `stbc-i3`, gate PASSED, receipt `cd4f2024…` `completion_status = PASS`.

### 6.1 The closure — INTEGER-EXACT on all twelve keys

Eleven restricted projections summed, against one unrestricted projection.
Compared with `==` on the exact double; no tolerance applied anywhere.

| tune | trigger | associate | Σ classes (OS−SS) | integrated (OS−SS) | exact |
|---|---|---|---|---|---|
| CLOSEPACKING | `B^{+}` | `B-` | 86,326 | 86,326 | **YES** |
| CLOSEPACKING | `D^{+}` | `D-` | 2,068,234 | 2,068,234 | **YES** |
| CLOSEPACKING | `B^{+}` | `Lambda_b` | 33,618 | 33,618 | **YES** |
| CLOSEPACKING | `D^{+}` | `Lambda_c(+)-bar` | 247,478 | 247,478 | **YES** |
| JUNCTIONS | `B^{+}` | `B-` | 89,974 | 89,974 | **YES** |
| JUNCTIONS | `D^{+}` | `D-` | 2,039,059 | 2,039,059 | **YES** |
| JUNCTIONS | `B^{+}` | `Lambda_b` | 37,648 | 37,648 | **YES** |
| JUNCTIONS | `D^{+}` | `Lambda_c(+)-bar` | 281,536 | 281,536 | **YES** |
| MONASH | `B^{+}` | `B-` | 165,827 | 165,827 | **YES** |
| MONASH | `D^{+}` | `D-` | 2,641,798 | 2,641,798 | **YES** |
| MONASH | `B^{+}` | `Lambda_b` | 27,702 | 27,702 | **YES** |
| MONASH | `D^{+}` | `Lambda_c(+)-bar` | 258,519 | 258,519 | **YES** |

`V_INTEGRATED_CLOSURE=EXACT keys=12`, eleven classes per key. The
unit-weight precondition (`RequireIntegralPairCount`) was evaluated on every
count of every bin and **never fired**, so the integrality the exact
comparison depends on held throughout.

### 6.2 The values, with block SEMs

Ten blocks by `canonical_slot % 10`; the integrated ratio is formed inside
each block and the spread taken across blocks at **dof = 9**,
`SEM = stdDev/√n`. Every point reports `finite_yields=10` and `status=PASS`.

| tune | trigger | associate | blocks | integrated yield | block SEM | rel. |
|---|---|---|---|---|---|---|
| MONASH | `B^{+}` | `B-` | 10 | 0.11625153 | 0.00026825 | 0.23% |
| JUNCTIONS | `B^{+}` | `B-` | 10 | 0.08730330 | 0.00034704 | 0.40% |
| CLOSEPACKING | `B^{+}` | `B-` | 10 | 0.08549668 | 0.00023313 | 0.27% |
| MONASH | `D^{+}` | `D-` | 10 | 0.19344596 | 0.00012215 | 0.06% |
| JUNCTIONS | `D^{+}` | `D-` | 10 | 0.17397377 | 0.00012989 | 0.07% |
| CLOSEPACKING | `D^{+}` | `D-` | 10 | 0.17347720 | 0.00009871 | 0.06% |
| MONASH | `B^{+}` | `Lambda_b` | 10 | 0.01942024 | 0.00009650 | 0.50% |
| JUNCTIONS | `B^{+}` | `Lambda_b` | 10 | 0.03653050 | 0.00030652 | 0.84% |
| CLOSEPACKING | `B^{+}` | `Lambda_b` | 10 | 0.03329504 | 0.00022179 | 0.67% |
| MONASH | `D^{+}` | `Lambda_c(+)-bar` | 10 | 0.01893008 | 0.00005393 | 0.28% |
| JUNCTIONS | `D^{+}` | `Lambda_c(+)-bar` | 10 | 0.02402082 | 0.00002956 | 0.12% |
| CLOSEPACKING | `D^{+}` | `Lambda_c(+)-bar` | 10 | 0.02075770 | 0.00003961 | 0.19% |

**Independent confirmation that the ratio is formed once, from the counts.**
Taking §6.1's own integers for MONASH B⁺→B⁻:

```
165827 / 1426450 = 0.11625153352728802     (closure counts, by hand)
                   0.11625153352728805     (macro central_yield)
```

Agreement to fifteen significant figures, the last digit being
floating-point summation order. The macro's yield **is**
(ΣN_OS − ΣN_SS)/ΣN_trig, computed once — not an average of per-class ratios,
which for this point would have been a different number entirely.

### 6.3 ⚠ BLOCKER — the standalone variant figures are refused by the axis contract

The **quantity** is measured and closed. The **standalone figures** for
V-INTEGRATED and V-EXTREMES are not renderable as configured, and the reason is
a guard that should not be weakened to get past it.

| config | bins | outcome |
|---|---|---|
| `…_VINTEGRATED_CLOSURE` | 11 classes **+** integrated | ✅ rendered, gate PASSED |
| `…_VINTEGRATED` | integrated only | ❌ *"Configured multiplicity class count (1) does not match the 11 classes defined in `multiplicity_class_boundaries_v1.json`; refusing to truncate or pad the axis"* |
| `…_VEXTREMES` | c1 + c11 | ❌ *"multiplicity-percentile classes have a gap or overlap"* |

`CommonMultiplicityBoundaries.h:111` requires the configured class count to equal
the artifact's, and `MultiplicityBoundaryUtils.h:337` requires the configured
percentile classes to tile without gap. **Both new variants violate these by
construction** — V-EXTREMES shows 2 of 11, V-INTEGRATED merges 11 into 1.

> **This is the B6 family working as designed.** The axis artifact is THE
> definition and no consumer may present a different axis. A figure showing two
> of eleven classes, with nothing on it saying so, is exactly the silent
> re-binning the guard exists to prevent.

**The resolution is a display filter, not a relaxed guard.** The axis must stay
whole — all eleven classes configured and validated — while the canvas chooses
which of them to *draw*. That separation does not exist today: `bins_to_ignore`
is honoured only by the baryon/meson-ratio canvases (`:4763`, `:5003`), not by
the balancing canvases, which draw every configured bin.

**Not attempted this session.** Adding a draw-selection mechanism to a
publication-facing canvas is a design change, and the alternative — deleting
classes from the config until the guard stops complaining — is precisely what
the guard is protecting against. It goes to the owner.

**What exists meanwhile:** `VariantIntegratedClosure` is a rendered, gate-PASSED
canvas carrying all eleven classes **and** the integrated point together, with
the full polish (species notation, per-panel √s, `balancing yield per trigger`
y-title, 1-dp class labels) and a legend entry `multiplicity integrated,
0.0-100.0%` whose span is derived from the artifact. It is the integrated
observable in context, and it is the artifact to look at while the display
filter is decided.
