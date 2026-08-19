# `Model.tex` rewrite pack — evidence for the owner's B1 edit

**The paper is untouchable and untouched.** This is the material the owner needs
to rewrite `Model.tex` §Multiplicity classes (`:108-126`) and the threshold line
at `:39`. Every number carries its provenance and its method.

**Scope.** Three of the paper's statements are contradicted by production, all
recorded as blockers: **C1** (`:39`, the threshold), **C3** (`:126`, the density
deficit) and **C8** (`:126`, the per-tune offset). **The class list itself at
`:111-124` is correct and needs no change** — verified this generation against
the memo's boundary set.

---

## 1. What the paper currently says, and the three defects

`Model.tex:39` states `PhaseSpace:pTHatMin = 1.`

`Model.tex:126` states, in part: percentiles *"computed within the
hard-heavy-flavour sample itself and … not equivalent to experimental
minimum-bias multiplicity classes: at identical counter settings this sample has
a mean charged-particle density about 36 % below minimum bias, a consequence of
generating with a hard-process threshold p_T^hat > 1 GeV"*.

| # | defect | evidence |
|---|---|---|
| **C1** | threshold is **2.0**, not 1.0 | all four production cards, `SimulationScripts/pythiasettings_Hard_Low_ccbb_{MONASH,JUNCTIONS,CLOSEPACKING,JUNCTIONS_MATCHED}.cmnd:47/68/84/87` → `PhaseSpace:pTHatMin = 2.` **Verified directly this session** |
| **C3** | **36 % is wrong twice** | it is a PYTHIA **8.315** measurement, and it is at the **wrong threshold**. On **8.317**: **−28.6 %** at pTHatMin 1.0, **−4.16 %** at 2.0. `ValidationReports/PTHAT_MULTIPLICITY_SCAN_8317.md:78` states outright that the paper's number is wrong |
| **C8** | the sample-vs-MB offset is quoted as one number | it is a **per-tune** quantity, because percentiles are computed within each tune's own sample. **Only MONASH is measured** (−4.16 % at 2.0). **JUNCTIONS and CLOSEPACKING are unmeasured** |

> **C8 is not dischargeable from this pack.** Two of three tunes have no measured
> offset. The replacement language below is written so it does not assert one.

---

## 2. The settled convention — what replaces the per-tune percentile reading

**Ruling** (`docs/PRODUCTION_SHAPE_DECISION.md:421-424`):

> Adopt **common absolute N_ch boundaries** — one set, shared by all three tunes
> and both sectors. **Labels are defined as percentiles of the MONASH MB
> distribution.** The per-tune MB-percentile translations are **published** as a
> table.

**The reason is physics, not convenience.** Per-tune percentile classes fold each
tune's *activity distribution* into the class *definition*, confounding "how the
tune hadronises at fixed activity" with "how the tune distributes activity" —
the two things this study exists to separate.

**The paper's own class list is unchanged and correct:**
`0–1 %, 1–10 %, 10–20 %, 20–30 %, 30–40 %, 40–50 %, 50–60 %, 60–70 %, 70–80 %,
80–90 %, 90–100 %` — eleven classes, matching the eleven boundaries below
(ten closed intervals plus the open top bin).

---

## 3. The boundary set

Derived from MONASH MB, 172,429 events. **Half-integer edges** so no integer
N_ch is ambiguous about its class.

| class | target %ile | realised %ile | ± stat | **boundary** |
|---|---|---|---|---|
| c1 | 0.000 | 0.000 | — | **−0.5** |
| c2 | 9.091 | 11.803 | 0.078 | **2.5** |
| c3 | 18.182 | 19.403 | 0.095 | **3.5** |
| c4 | 27.273 | 34.063 | 0.114 | **5.5** |
| c5 | 36.364 | 40.150 | 0.118 | **6.5** |
| c6 | 45.455 | 49.692 | 0.120 | **8.5** |
| c7 | 54.545 | 56.970 | 0.119 | **10.5** |
| c8 | 63.636 | 65.386 | 0.115 | **13.5** |
| c9 | 72.727 | 73.846 | 0.106 | **17.5** |
| c10 | 81.818 | 82.876 | 0.091 | **23.5** |
| c11 | 90.909 | 91.578 | 0.067 | **32.5** |

**Realised percentiles overshoot their targets**, by up to 6.8 pp at c4, because
N_ch is discrete and no integer sits at the target. **The realised value is the
one that means anything;** the target is only how the boundary was chosen.

---

## 4. The paper-facing translation table

Where each common boundary sits in **each tune's own MB distribution** — the
residual the ruling requires be published.

| class | boundary | MONASH | JUNCTIONS | CLOSEPACKING | spread (pp) |
|---|---|---|---|---|---|
| c1 | −0.5 | 0.00 % | 0.00 % | 0.00 % | 0.00 |
| c2 | 2.5 | 11.80 % | 11.22 % | 11.86 % | 0.64 |
| c3 | 3.5 | 19.40 % | 18.04 % | 19.09 % | 1.36 |
| c4 | 5.5 | 34.06 % | 31.49 % | 33.06 % | 2.57 |
| c5 | 6.5 | 40.15 % | 37.24 % | 38.93 % | **2.91** |
| c6 | 8.5 | 49.69 % | 46.79 % | 48.37 % | 2.90 |
| c7 | 10.5 | 56.97 % | 54.18 % | 55.79 % | 2.79 |
| c8 | 13.5 | 65.39 % | 63.08 % | 64.62 % | 2.31 |
| c9 | 17.5 | 73.85 % | 72.11 % | 73.67 % | 1.73 |
| c10 | 23.5 | 82.88 % | 81.73 % | 83.26 % | 1.53 |
| c11 | 32.5 | 91.58 % | 90.84 % | 92.10 % | 1.26 |

**Maximum residual: 2.91 pp**, at c5. Every class is inside 3 pp.

> ### THE WARNING THAT MUST TRAVEL WITH THIS NUMBER
> **2.91 pp is NOT "the ±3 pp criterion passing".** B4's pre-registered gate
> asked whether **per-tune** boundaries land at the same MB percentile. **They do
> not — 5 of 11 fell outside ±3 pp**, and that failure is what caused the
> convention to change. The 2.91 pp is a **different quantity**: how far a
> **common** boundary's meaning drifts between tunes. **It is the published
> residual, not a passed gate.** Quoting it as the latter would misrepresent the
> result.

### The reproduction check — two independent computations, verified

Per the standing rule that a number going into a paper is computed two ways, the
MONASH column of §4 and the realised-percentile column of §3 are **the same
quantity** reached by different routes. All eleven agree:

| class | §3 realised | §4 MONASH | agree |
|---|---|---|---|
| c1 | 0.000 | 0.00 | ✓ |
| c2 | 11.803 | 11.80 | ✓ |
| c3 | 19.403 | 19.40 | ✓ |
| c4 | 34.063 | 34.06 | ✓ |
| c5 | 40.150 | 40.15 | ✓ |
| c6 | 49.692 | 49.69 | ✓ |
| c7 | 56.970 | 56.97 | ✓ |
| c8 | 65.386 | 65.39 | ✓ |
| c9 | 73.846 | 73.85 | ✓ |
| c10 | 82.876 | 82.88 | ✓ |
| c11 | 91.578 | 91.58 | ✓ |

**This check has already earned its place.** It is what caught the `FindBin`
off-by-one on a half-integer edge, when MONASH c2 was read as 19.40 % — c3's
value — against the boundary table's 11.803 %. **Only having both tables
exposed it.**

---

## 5. The screening scales, for the threshold sentence

The MPI regularisation scale is `pT0(s) = pT0Ref x (sqrt(s)/ecmRef)^ecmPow`.
All three tunes carry `ecmPow = 0.215`, `ecmRef = 7000` GeV,
`Beams:eCM = 13600` GeV ⇒ factor **1.153494**
(`docs/REGISTRY_AND_MAPPING_PROPOSAL.md:626-628`, verified from produced
`effective_settings`).

| tune | `pT0Ref` (card) | **effective pT0** | margin over 2.0 |
|---|---|---|---|
| MONASH | 2.28 (inherited, `Tune:pp = 14`) | **2.630** | 0.630 |
| JUNCTIONS | 2.15 | **2.480** | 0.480 |
| CLOSEPACKING | 2.194 | **2.531** | 0.531 |

**Why this matters to the sentence.** The paper's reasoning is that
`pTHatMin` lies *below* the MPI regularisation scale. **That remains true** —
2.0 sits below all three effective scales — **but the card values alone
understate the distance**, because comparing `pTHatMin = 2.0` against the
*unscaled* `pT0Ref` ignores the 1.153 energy scaling
(`docs/DESIGN_AND_RATIONALE.md:472`). The qualitative argument survives; the
arithmetic behind it should be the scaled column.

---

## 6. Suggested replacement language

**Offered as a starting point for the owner's edit, not as a patch.** The paper
is untouched.

### For `:39`

> `PhaseSpace:pTHatMin = 2.`

### For `:126`

> The 0–1 % class corresponds to the highest-multiplicity events, while the
> 90–100 % class corresponds to the lowest-multiplicity events. Class boundaries
> are defined as **common absolute values of N_ch**, shared by all three tunes
> and both flavour sectors, and are labelled by their percentile in the MONASH
> minimum-bias distribution. A common boundary does not sit at exactly the same
> percentile in every tune; the residual is at most **2.91 percentage points**
> across the three tunes and is published in Table X. Defining classes this way
> conditions every tune on an identical event selection, so that differences
> between tunes reflect how they hadronise at fixed activity rather than how
> they distribute activity.
>
> These percentiles are computed within the hard-heavy-flavour sample and are
> therefore not identical to experimental minimum-bias multiplicity classes. At
> identical counter settings and the production threshold
> `p_T^hat > 2` GeV, the MONASH sample's mean charged-particle density is
> **4.16 % below** minimum bias. Comparisons with multiplicity-dependent
> measurements should be read as qualitative trends rather than as matched event
> classes.

**Two deliberate choices in that draft, both of which the owner should confirm:**

1. **"the MONASH sample's"**, not "this sample's". C8 is only measured for
   MONASH. Writing it unqualified would assert an unmeasured number for two
   tunes. If the owner wants the general statement, JUNCTIONS and CLOSEPACKING
   need measuring first — the method is `Validation/CalibrateMultiplicityAgainstMinBias.C`
   and it is cheap.
2. **The 36 % figure is dropped entirely** rather than corrected in place,
   because it was wrong on two independent axes (PYTHIA 8.315, threshold 1.0).
   Note in passing that at 1.0 on 8.317 the deficit is **−28.6 %**, not 36 % —
   so even the old threshold's number was version-stale.

---

## 7. Provenance of every number here

| number | source | measured by |
|---|---|---|
| `pTHatMin = 2.` | production cards | **verified directly this session** |
| class list `0–1 … 90–100` | `Model.tex:111-124` | **read directly, matches the 11 boundaries** |
| boundary set, realised percentiles | `docs/PRODUCTION_SHAPE_DECISION.md` §5c | prior generation, 172,429 MONASH MB events |
| translation table, 2.91 pp | same memo, §5c | prior generation |
| reproduction check | **computed here** from the two tables | **this session** |
| −4.16 % at 2.0, −28.6 % at 1.0 | `RELEASE_BLOCKERS.md` C3, `ValidationReports/PTHAT_MULTIPLICITY_SCAN_8317.md` | prior generation, cluster 5319322 |
| ecmPow scales 2.630 / 2.480 / 2.531 | `docs/DESIGN_AND_RATIONALE.md:468-470`, `REGISTRY_AND_MAPPING_PROPOSAL.md:626-628` | prior generation, from produced `effective_settings` |

**I did not re-measure the multiplicity offsets or the screening scales.** They
are cited to their records. The two things verified from source this session are
the production threshold and the reproduction check.

---

# ADDENDUM — M2: the `probQQ1toQQ0join` mechanism claim is dead

**Added 2026-08-09. Owner ruling recorded; `Paper/**` untouched.**
Full working: `docs/M2_PROBQQ1TOQQ0JOIN.md`.

## 8. The finding, from the pinned 8.317 source

**`probQQ1toQQ0join` is indexed by the heavier of the two quarks being joined
*into the diquark* — not by the heaviest quark in the baryon.**

```
Pythia8/src/FragmentationFlavZpT.cc:52    pvec("StringFlav:probQQ1toQQ0join")   // read once
                                  :54      probQQ1join[i] = 3.*p[i] / (1. + 3.*p[i]);
                                  :523   int StringFlav::makeDiquark(int id1, int id2, int idHad)
                                  :526     int idMax = max( abs(id1), abs(id2));
                                  :536     } else if (idMin != idMax) {
                                  :537       if (rndmPtr->flat() > probQQ1join[min(idMax,5) - 2]) spin = 0;
```

Index map: **0 = u/d, 1 = s, 2 = c, 3 = b.**

## 9. Why the mechanism claim is dead

**Λ_c is `c + (ud)`; Λ_b is `b + (ud)`. The diquark is `(ud)` in both, so
`idMax = 2` and both consume index 0.** The heavy quark sits at the *other*
string end and is **never an argument to `makeDiquark`**.

> **The charm and beauty entries of `probQQ1toQQ0join` are never consulted when
> forming a Λ_c or Λ_b with a light diquark.** They are reachable only for
> **doubly-heavy diquarks**. A paragraph that explains an observed charm/beauty
> difference by appealing to those entries is explaining it by a mechanism that
> does not fire.

**RULED DISPOSITION:** the mechanism claim is **dropped from the manuscript's
reasoning**. The observed charm/beauty difference is **stated as observed**, with
no `probQQ1toQQ0join` explanation attached.

## 10. The one channel that survives — speculative only

Junction and non-junction fragmentation **consume the same entry rule** — both
call the same `makeDiquark`. What differs is *which two quarks are offered*:

| path | call site | joined quarks |
|---|---|---|
| non-junction break | `FragmentationSystems.cc:337` | the two ends at the break |
| **junction** | **`StringFragmentation.cc:2399`** — `makeDiquark(idMin, idMid)` | **remnant flavours of the two lowest-momentum legs** |

Legs are ordered by momentum in the junction rest frame
(`StringFragmentation.cc:2112-2117`); `idMin`/`idMid` are the **remnants left
after fragmenting** those two legs (`:2344`, `:2347`).

**So a heavy quark can end up inside the diquark — but only in a junction
topology, and only if it survives as the remnant end of one of the two
lower-momentum legs.**

> **⚠ NO RATE IS ASSERTED.** Reading the code establishes that the path
> **exists**. It says nothing about how often it is taken, and nothing in this
> repository measures it. **If this channel appears in the manuscript at all it
> must be explicitly speculative** — as a possible mechanism worth investigating,
> never as an explanation of the observed difference.

## 11. One further branch, for completeness

`FragmentationFlavZpT.cc:532-534` — when `idHad` is a proton or neutron and the
pair is `(ud)`, spin is 0 with probability 0.75 by SU(6), **bypassing
`probQQ1join` entirely**. The junction call passes `idHad = 0`, so junction
fragmentation never takes this branch; the beam-remnant calls
(`BeamParticle.cc:870,1402,1890`) do pass a beam id and can.

## 12. Provenance

Source read at `/data/alice/ipardoza/pythia_stock_8317/pythia8317/src/` — **the
pinned install the producer links against**, not a distribution copy.
`probQQ1toQQ0join` appears in exactly three places in `FragmentationFlavZpT.cc`:
read `:52`, transformed `:54`, consumed `:537`. The **scalar** `probQQ1toQQ0`
(no `join`) is a different parameter and is not what this addendum concerns.
