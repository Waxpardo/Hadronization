# Map v2 — species-level splits: the misassignment falls to 0.0018 %

**Built on v1.1, never on v1.** Pre-registration:
`docs/MAP_V2_PREREGISTRATION.md` (structure predicted before the probe existed).
Conjugation fix it stands on: `docs/MAP_V1_1_PREREGISTRATION.md`.

| artifact | sha256 |
|---|---|
| `AnalysisScripts/decay_parent_map_v2.json` | `c9593c9c0a7c4ec2…` |
| base `decay_parent_map_v1_1.json` | `dd502a10c5932fff…` |

---

## 1. THE NUMBER

| | value |
|---|---|
| channel-level upper bound (**v1 history, superseded as the quoted figure**) | **12.8451 %** |
| **species-level, before any split** | **5.7737 %** |
| **species-level, after the two splits** | **0.0018 %** |

**Two distinct effects, and the larger one is not the split:**

- **7.0714 pp evaporated on species-level accounting alone** — channels that
  land on the *same* ground state were never a misassignment. No split needed;
  the 12.84 % was simply the wrong question asked of the artifact.
- **5.7719 pp removed by splitting two species.**

**C6 (residual < 1 %): PASS by a factor of ~550.** The threshold never had to be
lowered. All that remains is **B_c±**, 1,173 + 1,164 weight, 0.0009 % each.

> **The 12.84 % survives as history, not as the quoted number.** It was an
> honest upper bound on a question the artifact could not then answer
> (`docs/SECOND_BRANCH_WEIGHT.md` §4 said so), and species-level accounting is
> what answers it. **Quote 0.0018 %.**

---

## 2. THE SPLITS — EXACTLY TWO

| species | branches | fractions |
|---|---|---|
| **D\*+** | D⁰, D⁺ | **0.6770 / 0.3230** |
| **D\*-** | **D̄⁰, D⁻** | **0.6770 / 0.3230** |

D*⁻'s bins are **conjugated**, which is only correct because v1.1 landed first.
Everything else stays dominant-only, including B_c± at 0.0031 % — far below the
0.1 % threshold, and the only reassigned species whose PYTHIA table is irregular
(85 channels summing to 1.021, 23 of them daughterless).

## 3. THE TABLE UNDER v2

MONASH anchor, total 129,883,844, **invariance conserved**:

| observable | weight | share % |
|---|---|---|
| **D⁰** | 32,785,882.8 | **25.2425** |
| **D̄⁰** | 32,694,110.8 | **25.1718** |
| **D⁺** | 17,085,109.2 | **13.1541** |
| **D⁻** | 17,053,065.2 | **13.1295** |
| D_s⁺ | 5,491,128 | 4.2277 |
| D_s⁻ | 5,485,224 | 4.2232 |
| B̄⁰ | 2,991,690 | 2.3034 |
| B⁰ | 2,986,568 | 2.2994 |

**The split moves ~2.9 pp from each D⁰ state into the corresponding D±**, which
is the physical content of D\*+ → D⁺π⁰/D⁺γ finally being counted. Charge ratios
stay at unity.

### For reference, the three tables side by side (D⁰ share)

| map | D⁰ | D̄⁰ | D⁰/D̄⁰ |
|---|---|---|---|
| v1 (**defective**) | 45.9475 % | 10.2387 % | **4.49** |
| v1.1 (conjugation fixed) | 28.1326 % | 28.0536 % | 1.003 |
| **v2 (splits)** | **25.2425 %** | **25.1718 %** | **1.003** |

---

## 4. CHECKS

| # | check | result |
|---|---|---|
| **C1** | split fractions sum to exactly 1 — **exact rational arithmetic**, not tolerance | **PASS** |
| **C2 / I2** | heavy-quark sign preserved on every product | **PASS** |
| **C3** | totals preserved — 129,883,844 | **PASS** |
| **C4** | diquark-structure convention **byte-identical** | **PASS, measured** — 67,969,216 / 60,600,180 / 1,314,400 / 48 reproduced exactly from the category column, which never consults the map |
| **C5** | v2 **dominant-only** reproduces **v1.1** exactly (re-pointed from v1 by owner ruling) | **PASS, byte-identical** |
| **C6** | residual species-level misassignment < 1 % | **PASS** — 0.0018 % |
| **C7** | extended probe reproduces v1's `F4_SPECIES`/`F4_GATE` lines | **PASS** (previous session) |
| **guard** | building v2 on the defective v1 is refused | **PASS** — verified by attempting it |

**C1 uses `fraction_exact` rationals carried in the artifact**, so "sums to 1" is
a real equality rather than a float comparison. **C3 uses a relative tolerance**
because fractional splits introduce float summation — exact equality there would
fail on representation, not on a leak, and 1e-6 still catches any real loss by
six orders of magnitude.

---

## 5. SCORED AGAINST THE PRE-REGISTRATION — 2 HIT, 3 MISSED, ONE CAUSE

| # | registered | actual | |
|---|---|---|---|
| **V1** | species-level ≈ **5.83 %** | **5.7737 %** | **MISS**, low by 0.052 pp |
| **V2** | D\*± carries ≈ **99.1 %** of V1 | **99.97 %** | **MISS**, high |
| **V3** | D\*± splits ≈ 0.677 / 0.323 | **0.6770 / 0.3230** | **HIT, exact** |
| **V4** | exactly **2** species split at 0.1 % | **2** | **HIT** |
| **V5** | residual ≈ **0.054 %** | **0.0018 %** | **MISS**, 30× low |

**All three misses have a single cause, and it is instructive.** I applied the
convergence insight — "all channels land on the same ground state, so it
evaporates" — to D\*⁰ and D\*_s, and then assumed the remaining small species
would *keep* their non-dominant weight. **They do not.** Ξ*_c is the same
pattern I had already identified:

```
F4_CHANNEL pdg=4324 idx=0 br=0.5 products=4232:111     Xi*_c+ -> Xi_c+ pi0
F4_CHANNEL pdg=4324 idx=1 br=0.5 products=4232:22      Xi*_c+ -> Xi_c+ gamma
```

**π⁰ and γ, both landing on Ξ_c⁺ — exactly D\*⁰'s structure.** All four Ξ*_c
states collapse to a single branch at fraction 1.000. Having found the mechanism,
I failed to check where else it applied. **The predictions erred in the safe
direction — the real answer is better than registered — but the reasoning gap
was mine, not the data's.**

---

## 6. WHAT THE ADVISORY SAYS NOW

Particle/antiparticle flags: **15 under v1 → 7 under v1.1 and v2**, and the
4.49×, 2.74× and 5.39× are gone. What remains:

| pair | ratio | weight |
|---|---|---|
| Λ_b⁰ / Λ̄_b⁰ | **1.111** | 279,370 vs 251,498 |
| Ξ_b⁻ / Ξ̄_b⁺, Ξ_b⁰ / Ξ̄_b⁰ | 1.115 / 1.116 | ~37,000 |
| Ω_c⁰ / Ω̄_c⁰ | 1.169 | 7,464 vs 6,384 |
| Ω_b⁻ / Ω̄_b⁺ | 1.486 | 1,352 vs 910 |
| Ξ_cc⁺⁺ (4434), Ω_bc (5342) | antiparticle bin **empty** | 48 and 26 |

> **These are flagged, not judged.** The brief anticipated ~2 % baryon
> asymmetries in the CR samples; **Λ_c is 1.026 (2.6 %) and consistent with
> that, but the b-baryons sit near 11 %, five times larger.** Whether
> baryon-number transport accounts for that is **a physics question and the
> owner's to answer** — the advisory exists to surface it, and a hard gate would
> have refused it as a bug. The two empty bins carry 48 and 26 weight; at those
> counts an empty conjugate bin is a statistics artefact.

**This is MONASH anchor data (four directories), not three tunes.** The merged
output will change every weight here; the structure should not.
