# Decay-parent map v2 (BR-split) — pre-registration

**Committed BEFORE the channel probe was written, compiled or run.** The
prediction below is falsifiable by the probe's own output.

Owner ruling being executed: the second-branch number came out **12.84 %**
(upper bound, `docs/SECOND_BRANCH_WEIGHT.md`), the decision rule fired, and the
ruling is **build map v2 with fractional splits; do not switch conventions.**

---

## 1. ⚠ A DISCREPANCY WITH THE TASK BRIEF, MEASURED AND REPORTED

The brief specifies Task 3 as *"local-repo, analysis-side; nothing touches the
Nikhef tree."* **The task cannot be completed under that constraint, and this is
a fact about the artifact, not a preference.**

`decay_parent_map_v1.json` records **only the dominant channel** — the complete
per-species field set is `channels`, `dominant_branching_ratio`,
`dominant_products`, `name`, `ordinal`, `pdg`, `status`. The retained probe
output `f4_runs/f4_probe.out` is the same: `f4_probe.cc:111` emits `dominant_br`
and `dominant_products` and nothing else. **202 species, 202 dominant channels,
zero subdominant products anywhere in the repository or the retained artifacts.**

`D*0` is recorded as `channels=2` — the *count* survives, the second channel's
products do not. **A fractional split needs the products the map does not
carry.** `docs/SECOND_BRANCH_WEIGHT.md` §4 said exactly this and named the fix.

**Resolution taken:** re-probe with an extended `f4_probe`, compiled and run
**in scratch on Nikhef**, reading the frozen checkout and PYTHIA install and
writing only to `/data/alice/ipardoza/f4b_runs/`. **The Nikhef tree is read,
never written** — the same pattern M7 beauty used. The alternative, hand-entering
branching ratios from memory, is unverifiable and is not done.

**BR provenance:** PYTHIA 8.317 `particleData`, the pinned install — **the same
source as v1**, so v2 is comparable to v1 by construction. The brief asks for
PDG-pinned values with edition and date; **PYTHIA's table is not the PDG's**,
and I have no offline PDG edition to pin. **This is flagged for the owner as an
open provenance decision** (§4). It does not block the arithmetic, and switching
source later changes the numbers but not the method.

---

## 2. THE SPECIES-LEVEL POINT, AND WHY MOST OF THE 12.84 % SHOULD EVAPORATE

The 12.84 % is **channel-level**: it counts all weight that did not take the
dominant *channel*. But the convention assigns to a **species**, so two channels
landing on the same ground state are **not** a misassignment.

**Prediction, from the decay structure, to be confirmed or refuted by the probe:**

| species | v1 channel-level | predicted species-level | why |
|---|---|---|---|
| **D\*0, D\*bar0** | **6.7917 pp** | **0** | both channels (D⁰π⁰, D⁰γ) land on **D⁰** |
| **D\*_s+, D\*_s-** | **0.2277 pp** | **0** | both channels (D_s γ, D_s π⁰) land on **D_s** |
| **D\*+, D\*-** | **5.7719 pp** | **5.7719 pp** | D⁰π⁺ vs D⁺π⁰/D⁺γ — genuinely **different** ground states |
| everything else | 0.0538 pp | ~0.0538 pp | small, mixed |

### Registered numbers

| # | quantity | prediction |
|---|---|---|
| **V1** | **species-level misassignment** | **≈ 5.83 %** (12.8451 − 6.7917 − 0.2277) |
| **V2** | fraction of V1 carried by **D\*± alone** | **≈ 99.1 %** (5.7719 / 5.8257) |
| **V3** | species split into ≈ 2/3 D⁰ : 1/3 D± for D\*± | D⁰ ≈ 0.677, D± ≈ 0.323 |
| **V4** | species needing a split at a **0.1 %** threshold | **exactly 2**: D\*+ and D\*− |
| **V5** | **residual after splitting those two** | **≈ 0.054 %**, comfortably under the ~1 % requirement |

**If the probe shows D\*0 has a channel that does not terminate at D⁰, V1
through V5 all fail together and the prediction was wrong.** That is the point
of writing it down first.

---

## 3. FAIL-CLOSED CHECKS, ALL MANDATORY

| # | check |
|---|---|
| **C1** | per-species split fractions sum to **exactly 1** (exact comparison, not a tolerance) |
| **C2** | every split product carries the **parent's heavy-quark sign** — a c̄ parent may not feed a c daughter |
| **C3** | total weight **preserved exactly** under v2 regrouping, as v1's invariance check does |
| **C4** | the **diquark-structure convention is byte-identical** — it does not consult the map at all, so any change is a bug |
| **C5** | ~~the v2 reader in **dominant-only mode reproduces the v1 experiment-comparable table exactly** — D⁰ 59,678,352 / 45.9475 %, D⁺ 13,331,304, B⁰ 5,042,102, total 129,883,844~~ **RE-POINTED 2026-08-11, see below** |

> **C5 IS RE-POINTED TO v1.1 (owner ruling, 2026-08-11).** Passing against v1
> would require reproducing the conjugation defect deliberately
> (`docs/MAP_V1_CONJUGATION_BUG.md`). **C5 now reads: v2 in dominant-only mode
> must reproduce the v1.1 table exactly** — **D⁰ 36,539,688 / 28.1326 %**,
> D̄⁰ 36,437,040, D⁺ 13,331,304, D_s⁺ 5,491,128, B⁰ 2,986,568, total
> 129,883,844, map v1.1 sha256 `dd502a10c5932fff…`.
>
> **The BR-source question in §4 is also ruled: PYTHIA 8.317's own probed decay
> table, version-pinned — NOT PDG.** The convention encodes what *this
> generator* would have decayed these states into; PDG values would mix
> conventions. PDG remains an advisory cross-check only.
| **C6** | **residual misassignment < ~1 %**; if not, lower the split threshold until it is. **If it cannot be reached, STOP and report** rather than tuning to fit |
| **C7** | the extended probe reproduces v1's `F4_SPECIES` lines **byte-identically**, so the same output can still rebuild v1 |

**C5 and C7 are regressions against artifacts that already exist.** C7 is the one
that proves the probe was extended rather than changed.

---

## 4. OPEN FOR THE OWNER

1. **BR provenance: PYTHIA 8.317 vs PDG.** v2 uses PYTHIA, matching v1 and
   matching the generator whose events supply the weights. The brief asked for
   PDG. **These are different numbers**, and for an *experiment-comparable*
   convention there is an argument for PDG. Not decided unilaterally; the
   artifact records its source explicitly either way.
2. Whether the ~0.05 % residual is quoted as a systematic or simply noted.
