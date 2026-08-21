# Map v1.1 — the conjugation fix: pre-registered diff scope

**Committed BEFORE the builder change exists.** The built diff must match these
counts exactly; a mismatch in either direction is a failure, not a surprise.

Fixes `docs/MAP_V1_CONJUGATION_BUG.md`, confirmed by the owner. Lands **first,
as its own reviewable change**, before any split work (Task 3 / map v2).

---

## 1. THE FIX, AND WHY IT IS BUILDER-LEVEL

**The probe is not re-run.** `f4_probe.out` records what PYTHIA *reports*, and
PYTHIA reports one decay table per particle — `particleDataEntryPtr(-413)`
returns the `+413` entry. **That record is correct as a record.** Conjugation is
*interpretation*, so it belongs in the builder, and the retained probe output
stays the untouched raw material.

For an antiparticle parent, each product id is negated **iff the species has a
distinct antiparticle**. Self-conjugate products are left alone: gauge bosons
(21, 22, 23, 25), PYTHIA internal/string codes (81–100), and flavourless neutral
mesons — π⁰ 111, η 221, η′ 331, ρ⁰ 113, ω 223, φ 333, J/ψ 443 — identified by
equal quark digits rather than by a hand-written list.

---

## 2. THE PREDICTED DIFF — TWO COUNTS, NOT ONE

Conflating these would hide the interesting one.

| # | quantity | **prediction** |
|---|---|---|
| **D1** | **ARTIFACT rows changed** — antiparticle parents with ≥1 non-self-conjugate product | **101 of 101** |
| **D2** | **TABLE-AFFECTING rows** — the in-table heavy daughter changes identity | **60** |
| **D3** | antiparticle rows that remain **terminal** (quark-level products: 81, 1, −2, 4 …) | **41** |
| **D4** | antiparticle rows whose heavy daughter is itself **self-conjugate** (in-table, no flip) | **0** |
| **D5** | **PARTICLE rows changed** | **0** — conjugation must not be applied to positive parents |

**D2 + D3 = 101 exactly**, a clean partition of the antiparticle rows: every one
either flips its heavy daughter or has no in-table daughter at all. **D4 = 0
means no hidden-heavy (cc̄/bb̄) state sits on a chain**, so nothing is ambiguous.

**Only D2's 60 rows move weight between bins.** D1's larger count is artifact
hygiene — the stored products become right even where the chain outcome was
already unaffected.

Spot-check of the first table-affecting rows, daughter pdg before → after:

```
B*_1c-      513 -> -513      D*_1s-      433 -> -433
B*_1sbar0   523 -> -523      D*_1bar0    413 -> -413
B*_1-       513 -> -513      D*_1-       423 -> -423
```

---

## 3. FAIL-CLOSED CHECKS

| # | check |
|---|---|
| **I1 involution** | conjugating an antiparticle row must yield **exactly** the conjugated products of its particle row: `conj(products(−p)) == conj_ids(products(+p))`. Applied to all 101 pairs. **Permanent** — runs on every future map build |
| **I2 heavy-quark sign** | the C2 check that caught the bug must now **PASS on every row**, not merely on split rows |
| **I3 totals** | total weight preserved **exactly** (129,883,844) — this is a redistribution |
| **I4 particle rows untouched** | D5 = 0, asserted rather than assumed |

## 4. THE POSITIVE CHECK

The v1.1 regenerated experiment-comparable table must reproduce the
**independently computed** conjugation-fixed table in
`docs/MAP_V1_CONJUGATION_BUG.md` §3 **exactly**:

| | required |
|---|---|
| D⁰ | 36,539,688 (**28.133 %**) |
| D̄⁰ | 36,437,040 (28.054 %) |
| **D⁰/D̄⁰** | **1.00** |
| **D_s⁺/D_s⁻** | **1.00** |
| **B⁰/B̄⁰** | **1.00** |
| total | **129,883,844** |

That table was computed in the previous session by a **separate** code path
(a direct conjugation-aware walk), so agreement is a genuine two-implementation
check rather than a restatement.

## 5. THE NEW ADVISORY, AND WHY IT IS NOT A GATE

A **particle/antiparticle ratio report on every species-level table**, flagging
ratios beyond **~10 %** for investigation. **Advisory: it does not fail.**

**A hard gate at 1.00 would be wrong physics.** Real ~2 % baryon asymmetries
exist in the JUNCTIONS sample, and a check that refused them would be refusing a
result. The 4.49× that hid here for a generation is two orders of magnitude
beyond anything physical — a 10 % flag catches that class without touching real
asymmetry.

---

## 6. SUPERSESSION, NOT ERASURE

v1's artifact and every recorded v1 number stay in place with **dated
annotations** beside them. **`Paper/**` is owner-only**: any location quoting
45.95 % will be **flagged, not edited**.
