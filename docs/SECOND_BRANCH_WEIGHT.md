# The second-branch number — how much weight the dominant-only mapping puts at risk

**Status: MEASURED. The decision rule fires the "more" branch, by an order of
magnitude. The BR-split option goes to the owner; the convention is NOT changed
here.**

Answers the gap recorded in the dated private generational handoff, Sections 2.3 and 6.3:
the experiment-comparable grouping chains each species through its **dominant**
decay channel only, so a 60/40 species is assigned **whole** to its 60 %
descendant. That approximation was recorded but never quantified. It is now.

---

## 1. VERDICT

| | |
|---|---|
| **Weight at risk from dominant-only mapping** | **12.84 % of total** |
| Decision-rule threshold (v40 §2.3) | ~1 % |
| **Result** | **≈ 13× over threshold — produce the distribution, put BR-split to the owner** |
| Convention changed? | **No.** Not a unilateral call |

**This is an upper bound, not a point estimate.** See §4 — it is the honest
statement of what the artifact can support, and the reason the next step is a
map v2 rather than a convention switch.

---

## 2. THE TWO DEFINITIONS, BECAUSE THE SOURCES DISAGREED

The first-session brief and v40 §2.3 specify **different quantities**. Neither
was assumed; both are reported.

| | definition | result |
|---|---|---|
| **(A) brief** | Σ *w* × (1 − BR_dominant) over mapped species — *expected* misassigned weight | **12.8400 %** |
| **(B) v40 §2.3** | Σ *w* over species whose dominant branch < 80 % — weight *exposed* to a substantial second branch | **35.7910 %** |

**The discrepancy does not change the decision: both are far above ~1 %.** (A)
is the tighter and more directly meaningful figure and is what §1 quotes; (B) is
the broader exposure measure. Reported per the standing rule that where the
brief and v40 disagree on a fact, the discrepancy is measured rather than
resolved by preference.

### A third figure, computed and found not to matter

The reader's chain walk is **recursive**
(`extraction/extract_species_decomposition.py:159-168`): a species may hop through
several decays before reaching a ground state, and the probability the whole
chain is right is the **product** of BRs along the hops taken, not the first BR
alone. So (A) understates multi-hop chains by construction.

| | result |
|---|---|
| **(C) Σ *w* × (1 − Π BR over hops taken)** | **12.8451 %** |

**(C) − (A) = 0.005 percentage points.** The refinement is real but numerically
negligible here, because chains are overwhelmingly one hop:

| chain length | weight | share of total |
|---|---|---|
| 1 hop | 62,587,124 | 48.1870 % |
| 2 hops | 4,080 | 0.0031 % |
| 3 hops (max) | 8,298 | 0.0064 % |

**The brief's single-hop formula is adequate for this map.** Recorded because it
was checked, not because it changed anything.

---

## 3. WHERE THE RISK SITS — IT IS FOUR SPECIES

Total weight 129,883,844; **62,599,502 (48.20 %) is actually reassigned** (≥1
hop). Everything else is already a ground state and maps to itself.

| species | hops | Π BR | weight | misassigned | % of total |
|---|---|---|---|---|---|
| D*0 | 1 | 0.6190 | 11,602,248 | 4,420,456.5 | 3.4034 |
| D*bar0 | 1 | 0.6190 | 11,550,648 | 4,400,796.9 | 3.3883 |
| D*+ | 1 | 0.6770 | 11,621,688 | 3,753,805.2 | 2.8901 |
| D*- | 1 | 0.6770 | 11,588,016 | 3,742,929.2 | 2.8818 |
| D*_s- | 1 | 0.9420 | 2,550,456 | 147,926.4 | 0.1139 |
| D*_s+ | 1 | 0.9420 | 2,549,160 | 147,851.3 | 0.1138 |
| Xi*_c+ | 1 | 0.5000 | 32,208 | 16,104 | 0.0124 |
| Xi*_c0 | 1 | 0.5000 | 30,840 | 15,420 | 0.0119 |
| B*_c+ | 3 | 0.2020 | 4,610 | 3,678.8 | 0.0028 |

> **The four D* charge states carry 97.81 % of the entire effect**
> (16,317,988 of 16,683,667). This is not a diffuse approximation error spread
> over 202 species — it is the D* → D system and essentially nothing else.

That concentration is what makes a BR-split tractable: **splitting four species
correctly captures ~98 % of the correction.**

---

## 4. WHY THIS IS AN UPPER BOUND, AND WHAT THE NEXT STEP ACTUALLY IS

(1 − BR_dominant) is the probability the species decayed through a
**non-dominant** channel. It is **not** the probability the species landed in
the **wrong bin**, because a non-dominant channel may terminate at the *same*
ground state.

The excluded historical v1 map records **only** the dominant channel — the per-species
fields are exactly `channels`, `dominant_branching_ratio`, `dominant_products`,
`name`, `ordinal`, `pdg`, `status`. **There are no subdominant products in the
artifact**, so where the other 12.84 % goes cannot be computed from this file.

The physics says most of it genuinely does move: D*+ → D⁰π⁺ (dominant) versus
D*+ → D⁺π⁰ / D⁺γ land on **different** ground states. So the true misassignment
is expected to be a large fraction of 12.84 %, but **that is an expectation, not
a measurement, and it is not quoted as one.**

**The next step is therefore a map v2, not a convention switch:** re-probe with
`tools/f4_probe.cc` retaining **all** channels and their products, then compute
the true bin-to-bin migration. That is a bounded job — the F4 probe already
walks all 202 species and the gate `READABLE_AFTER_DISABLE` already established
the channels survive stabilisation.

---

## 5. OPTIONS FOR THE OWNER

The convention is **not** changed here. Three options, with costs:

| option | what it means | cost | effect on the paper |
|---|---|---|---|
| **1. Quote and keep** | keep dominant-only; state 12.84 % as a bounded systematic on the experiment-comparable convention | **zero** — the number exists | honest, but a 12.8 % bound is large to leave standing |
| **2. Map v2, then BR-split** | probe all channels, split each species across its channels by BR | one probe run + reader change + closure re-check | removes the approximation; ~98 % of it is four species |
| **3. Map v2, quantify only** | probe all channels, measure true migration, then decide | one probe run, no reader change | converts the upper bound into the real number first |

**Recommendation: option 3, then decide.** It is the cheapest thing that
replaces a bound with a measurement, it cannot destabilise the reader (no
grouping changes), and option 2 remains open afterwards with better information.
Option 1 stays defensible only if the true migration turns out to be small,
which §4 argues against.

**This affects the experiment-comparable convention only.** The
diquark-structure grouping — the standing default under
`docs/EXTRACTION_CONVENTIONS.md` — does not chain through decays and is
untouched.

---

## 6. METHOD AND INVOCATION MANIFEST

Positive checks first, per the standing rule that `rc=0` is not evidence.

| | |
|---|---|
| weights | `stbc:/data/alice/ipardoza/f3_runs/extraction_dual/per_species.csv`, 91 filled ordinals |
| **positive check 1** | weights sum to **129,883,844 exactly**, matching `docs/EXTRACTION_CONVENTIONS.md` §2 |
| map | excluded historical v1 map, `map_sha256 = e343fd8872f974…`, file sha256 `a67e8ae5f853689c010e991859242a77b913787dd30ab3d4c1b68bc05758c00c` |
| ordinal table | `AnalysisScripts/species_ordinals_v2.json`; digest equality asserted as the reader asserts it |
| chain walk | reimplemented mirroring `extraction/extract_species_decomposition.py:153-176` |
| **positive check 2** | the reimplementation reproduces the published table **exactly** — D⁰ 59,678,352 (45.9475 %), D⁺ 13,331,304, B⁰ 5,042,102. **Numbers were not read out until this passed** |

> **ANNOTATION 2026-08-11.** Positive check 2 above was run against map **v1**,
> which is now known not to conjugate antiparticle decays
> (`docs/MAP_V1_CONJUGATION_BUG.md`). The check was sound — it proved the
> reimplementation agreed with the reader — but **both were consuming the same
> defective artifact. A reimplementation check proves agreement, not
> correctness.**
>
> **The number in this document is UNCHANGED and has been re-verified against
> the corrected map v1.1:** 12.8400 % (A), **12.8451 % (C)**, 35.7910 % (B),
> the same contributors, and the same 97.81 % D\* concentration. It survives
> because it is computed from branching-ratio **fractions**, not from daughter
> identity — D\*⁻ still splits 0.677/0.323 whichever bin it feeds.
>
> `extraction/second_branch_weight.py` now defaults to v1.1 and its published-table
> constants are the corrected ones; pointing it at v1 fail-closes loudly.
| scope | MONASH, the four anchor directories — the same weights the published convention table rests on. **Not three-tune.** Re-running on the merged output will change the weights and should change the number a little; the D* concentration is structural and should not move much |

**This is a reader-side calculation, not a new measurement** — no jobs, no seeds,
no cluster time.
