# The two grouping conventions — first side-by-side

> ## ⚠ SUPERSEDED BY MERGED DATA — 2026-08-12
>
> **Every table in this document was computed from the anchor extraction, which
> is now quarantined for the baryon sector** (`docs/ERROR_RECORD.md` E4).
> **`docs/MERGED_CONVENTION_TABLES.md` rebuilds all of them from the merged
> MONASH central (1000 inputs) and is the current record.**
>
> **The headline numbers did not move** — every meson-dominated share shifts by
> ≤ 0.017 pp and the structural split is unchanged to 0.008 pp. That is the
> expected result and is exactly why the anchor defect stayed invisible: the
> affected sector carries ~2 % of weight against charm mesons' ~90 %.
>
> **Quote the merged tables.** These are kept as the historical record.

`extraction/extract_species_decomposition.py` now produces **both** groupings from the
same 202-bin species projection. This is the first time they have been put beside
each other, and the comparison is the paper's central figure taking shape.

**Source: the anchor's 100-input merged directory. MONASH only. No SEMs — one
directory is one number per bin, and the ten blocks per tune do not exist until
the merge lands.** Marked as such throughout.

---

## 1. THE TWO CONVENTIONS

| | groups by | comes from | answers |
|---|---|---|---|
| **structural** | diquark structure — what the species *is* | the ordinal table's `category` column (`ClassifyHeavyStateDetailed`) | "how much compensation sits in states the central-ground selector excludes?" |
| **experiment-comparable** | the observable it *feeds* | F4's `decay_parent_map_v1.json`, chained to the terminal heavy descendant | "how much compensation would a detector actually reconstruct, and as what?" |

---

## 2. SIDE BY SIDE

Total weight **129,883,844** under both — **identical, exactly.**

### Structural

| category | weight | share |
|---|---|---|
| kCentralGround | 67,969,216 | **52.3308 %** |
| kExcludedVector | 60,600,180 | **46.6572 %** |
| kExcludedExcited | 1,314,400 | 1.0120 % |
| kMultiplyHeavy | 48 | 0.0000 % |
| kHiddenHeavy, kOtherNoncentral | 0 | 0 |

### Experiment-comparable, rolled up

> **⚠ This table is a SELECTION, not a partition.** These species do not sum to
> 100 % and are not meant to: each row is an observable a detector reconstructs,
> and the rows are the largest of them, not a complete decomposition. The
> diquark-structure table **is** a partition and does sum to 100 %.

| group | weight | share |
|---|---|---|
| charm ground states | 115,906,584 | **89.2386 %** |
| beauty ground states | 13,977,186 | **10.7613 %** |
| UNMAPPED (quark-level channel) | 74 | **0.0001 %** |

### Experiment-comparable, top observables

> **⚠ This table is a SELECTION, not a partition.** These species do not sum to
> 100 % and are not meant to: each row is an observable a detector reconstructs,
> and the rows are the largest of them, not a complete decomposition. The
> diquark-structure table **is** a partition and does sum to 100 %.

> ## ⚠ SUPERSEDED 2026-08-11 — the table below was computed with map **v1**, which did not conjugate antiparticle decays
>
> v1 stored PYTHIA's **unconjugated** products for antiparticle parents, so
> **D\*⁻ and D̄\*⁰ fed D⁰ instead of D̄⁰**. The 4.49× D⁰/D̄⁰ asymmetry below is
> that defect, not physics. Diagnosis and proof:
> **`docs/MAP_V1_CONJUGATION_BUG.md`**; fix and verification:
> **`docs/MAP_V1_1_PREREGISTRATION.md`**.
>
> **The v1 numbers are left in place deliberately** — supersession, not erasure.
> **Do not quote them.** The current table is the v1.1 one immediately below.
>
> **The roll-up above (89.24 % / 10.76 %) is UNAFFECTED**: conjugation moves
> weight between charge states *within* a sector, never across sectors.

**v1 (SUPERSEDED — do not quote):**

| observable | weight | share |
|---|---|---|
| D⁰ | 59,678,352 | **45.9475 %** |
| D⁺ | 13,331,304 | 10.2640 % |
| D⁻ | 13,310,136 | 10.2477 % |
| D̄⁰ | 13,298,376 | 10.2387 % |
| D_s⁺ | 8,041,584 | 6.1914 % |
| B⁰ | 5,042,102 | 3.8820 % |
| B⁺ | 5,027,152 | 3.8705 % |
| D_s⁻ | 2,934,768 | 2.2595 % |

**v1.1 (CURRENT), map sha256 `dd502a10c5932fff…`, MONASH anchor, total 129,883,844:**

| observable | weight | share |
|---|---|---|
| **D⁰** | **36,539,688** | **28.1326 %** |
| **D̄⁰** | **36,437,040** | **28.0536 %** |
| D⁺ | 13,331,304 | 10.2640 % |
| D⁻ | 13,310,136 | 10.2477 % |
| **D_s⁺** | **5,491,128** | **4.2277 %** |
| **D_s⁻** | **5,485,224** | **4.2232 %** |
| B̄⁰ | 2,991,690 | 2.3034 % |
| B⁰ | 2,986,568 | 2.2994 % |
| B⁻ | 2,984,670 | 2.2980 % |

**Every particle/antiparticle ratio is now 1.00 to within 0.3 %** — D⁰/D̄⁰,
D_s⁺/D_s⁻ and B⁰/B̄⁰ all move from 4.49 / 2.74 / 5.39 to unity, which is what
charge-symmetric prompt production requires.

---

## 3. WHAT THE COMPARISON SAYS

**Under the structural convention, 46.7 % of the compensation sits in
`kExcludedVector`** — states the central-ground selector excludes. Read
structurally, nearly half the compensating flavour is in a category the analysis
does not count, and that is precisely the excluded-fraction problem the
observable-definition sentence exists to address.

**Under the experiment-comparable convention that weight is not lost — it is
reassigned to the ground states those vectors decay into.** D*⁰ → D⁰ and its
relatives are why **D⁰ alone carries 45.9 %**. The picture becomes 89 % charm
ground states against 11 % beauty ground states, and there is no large "excluded"
residual, because a detector reconstructing D⁰ is already counting the vectors'
decay products.

> **The two conventions are not competing answers; they answer different
> questions.** The structural one says what the generator made. The
> experiment-comparable one says what an experiment would see. **The
> excluded-fraction problem is severe in the first framing and largely dissolves
> in the second** — and which framing the paper's observable definition adopts is
> the decision this table exists to inform.

> ## ✅ RULED 2026-08-20 — THE PAPER QUOTES BOTH, AND EXPERIMENT-COMPARABLE IS PRIMARY
>
> **The observable definition adopts the experiment-comparable convention.** The
> diquark-structure partition is quoted beside it, as the mechanism-level
> decomposition that explains the primary number.
>
> **The reasoning.** The experiment-comparable convention is the number a
> measurement can confront. That is what makes this work a **proposed
> observable** rather than a model-internal comparison between three tunes — a
> quantity nobody can measure cannot be a proposal, however clean its
> decomposition. The diquark-structure partition answers a different and
> necessary question, *what the generator made*, and it is what turns the primary
> number from a result into an explanation. Neither is dropped, and the order is
> the claim.
>
> **What follows from the order.** The excluded-fraction problem is severe in the
> structural framing and largely dissolves in the experiment-comparable one,
> because the vectors' weight is reassigned to the ground states they decay into
> rather than left in a category the analysis does not count. Making the
> experiment-comparable table primary therefore means the paper's headline
> quantity does **not** carry a large unexplained residual — and the structural
> table, quoted beside it, is where that residual is shown and accounted for.
>
> **What travels with the ruling.** The primary number now depends on
> decay-parent map **v2**, and inherits its provenance: residual misassignment
> **0.0018 %** (`docs/MAP_V2_RESULT.md` §1), built on the v1.1 conjugation fix.
> **The experiment-comparable table is a SELECTION, not a partition** — it sums
> to ~91 % deliberately, and must never be normalised.

---

## 4. THE INVARIANCE CHECK

**Both groupings must sum to the ungrouped species total, exactly.** Regrouping
moves weight between bins; it cannot create or destroy it, so any deviation is a
bug by construction and the reader **item-STOPs** rather than warning.

```
INVARIANCE CONSERVED (both groupings sum exactly to the ungrouped species total)
```

The first convention additionally carries its original cross-check — species
summed into six categories reproducing `hFlavourClosure`'s own 6-bin projection
at `worst_relative = 0.000e+00`.

---

## 5. UNMAPPED, AND WHY IT IS REPORTED RATHER THAN ABSORBED

**54 of the 202 species cannot be chained to an observable ground state**, because
PYTHIA parametrises the weak decays of baryons it has no exclusive table for at
the **quark level** — the dominant channel of the doubly-heavy states is literally
`[-2, 1, 4, 81]`, ū d c plus a string placeholder. There is no hadron-level
daughter to follow.

**They are reported as `UNMAPPED`, never folded into a ground-state bin.**
Silently reallocating them is exactly the invisible-reassignment failure the
no-overflow-bin rule exists to prevent.

**Their weight is 74 of 129,883,844 — 0.000057 %.** The concern is real in
principle and immaterial in practice, and both halves of that belong in the
record.

---

## 6. LIMITS

- **MONASH only, one directory, 100 inputs.** The merge provides three tunes at
  1000 inputs.
- **No SEMs.** Ten blocks per tune are required and do not exist yet; `--blocks`
  refuses rather than fabricating them.
- **The chaining follows the DOMINANT channel only.** A species with a
  60/40 split is assigned entirely to its 60 % descendant. For a full treatment
  the weight should be split by branching ratio — the map carries the BRs, so
  this is a reader change, not a new measurement.

  **NOW QUANTIFIED: the weight at risk is 12.84 % of the total** (an upper
  bound), against the ~1 % threshold that would have let dominant-only stand.
  **97.81 % of the effect is the four D\* charge states.** The measurement, why
  it is a bound rather than a point estimate, and the options are in
  **`docs/SECOND_BRANCH_WEIGHT.md`**. **The convention is unchanged pending the
  owner's decision.**
