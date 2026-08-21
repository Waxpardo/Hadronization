# ⛔ STOP — the v1 decay-parent map does not conjugate antiparticle decays

**Found by check C2 of the map-v2 build, which the owner specified.** The check
fired on the first split it attempted and refused to build the artifact.

**Nothing has been changed. The convention has not been switched, the v1 map is
untouched, and no corrected table has been adopted.** This document reports the
defect, proves it, quantifies it, and lists the options. **The decision is the
owner's**, and one of the owner's own pre-specified checks (C5) cannot be
satisfied at the same time as correctness — see §5.

---

## 1. THE DEFECT

PYTHIA stores one decay table per particle and derives the antiparticle by
conjugation. `particleDataEntryPtr(-413)` returns **the same entry** as `+413`,
so the probe reads **unconjugated** products for every negative PDG id:

```
F4_CHANNEL pdg=-413 idx=0 br=0.677 products=421:211      <- D0 pi+ , the D*+ decay
F4_CHANNEL pdg= 413 idx=0 br=0.677 products=421:211
```

`f4_probe.cc` recorded them verbatim and the excluded historical v1 map carries them
verbatim:

```
-413  D*-      dominant_products = [421, 211]     should be [-421, -211]
-423  D*bar0   dominant_products = [421, 111]     should be [-421,  111]
```

**So the map sends D\*⁻ and D̄\*⁰ to D⁰ instead of D̄⁰.** The reader is not at
fault — `load_decay_grouping` faithfully follows the products it is given. The
artifact is wrong.

**This is not confined to charm.** Every negative-id parent in the map inherits
the same defect.

---

## 2. THE PROOF, WHICH IS ARITHMETIC AND NOT INFERENCE

The published v1 experiment-comparable table has

| | weight |
|---|---|
| D⁰ | 59,678,352 (45.947 %) |
| D̄⁰ | 13,298,376 (10.239 %) |
| **difference** | **46,379,976** |
| **sum of D\*0 + D̄\*0 + D\*+ + D\*−** | **46,362,600** |
| **residual** | **17,376 — 0.04 % of the difference** |

**The entire D⁰/D̄⁰ asymmetry in the published table is the four D\* states being
funnelled into D⁰.**

### The physics check, which is decisive

Prompt charm in pp at 13.6 TeV is produced **essentially charge-symmetrically**.
A 4.5× excess of D⁰ over D̄⁰ is not a physical result. Re-running the identical
chain walk with conjugation applied:

| ratio | v1 as published | conjugation-fixed |
|---|---|---|
| **D⁰ / D̄⁰** | **4.49** | **1.00** |
| **D_s⁺ / D_s⁻** | 2.74 | **1.00** |
| **B⁰ / B̄⁰** | 5.39 | **1.00** |
| D⁺ / D⁻ | 1.00 | 1.00 |

**Every charge ratio goes to unity.** A bug fix does not restore charge symmetry
across three independent species families by accident.

---

## 3. THE MAGNITUDE

Total weight is **preserved exactly** (129,883,844) under both — this is a
redistribution between bins, not a loss, so the invariance check in the reader
could never have caught it.

| observable | v1 as published | % | conjugation-fixed | % |
|---|---|---|---|---|
| **D⁰** | 59,678,352 | **45.947** | 36,539,688 | **28.133** |
| **D̄⁰** | 13,298,376 | **10.239** | 36,437,040 | **28.054** |
| D⁺ | 13,331,304 | 10.264 | 13,331,304 | 10.264 |
| D⁻ | 13,310,136 | 10.248 | 13,310,136 | 10.248 |
| **D_s⁺** | 8,041,584 | 6.191 | 5,491,128 | 4.228 |
| **D_s⁻** | 2,934,768 | 2.260 | 5,485,224 | 4.223 |
| **B⁰** | 5,042,102 | 3.882 | 2,986,568 | 2.299 |
| **B⁺** | 5,027,152 | 3.870 | 2,978,248 | 2.293 |
| **B̄⁰** | 936,156 | 0.721 | 2,991,690 | 2.303 |

> **D⁰ moves by 17.8 percentage points.** This is the single largest number in
> the experiment-comparable table and the one most likely to be quoted.

---

## 4. WHAT IS AND IS NOT AFFECTED

**Affected:**

- `docs/EXTRACTION_CONVENTIONS.md` §2, the experiment-comparable tables —
  **specifically the charge-separated rows**. The charm/beauty ground-state
  ROLL-UP (89.24 % / 10.76 %) is **unaffected**, because conjugation moves
  weight between charge states within the same sector.
- Anything downstream that consumes the experiment-comparable convention
  per-species. Nothing has yet.

**NOT affected — checked, not assumed:**

- **The diquark-structure convention.** It does not consult the map at all
  (check C4). Byte-identical.
- **The 12.84 % second-branch number** (`docs/SECOND_BRANCH_WEIGHT.md`). It is
  computed from branching-ratio *fractions*, not daughter identity: D\*⁻ still
  splits 0.677/0.323 whichever daughter it points at. **The number, the D\*
  concentration (97.81 %) and the upper-bound argument all stand.**
- **M7 charm and M7 beauty.** No decay map involved.
- **The gate, the merge, the closure counts.** No decay map involved.
- **The species ordinal table**, which distinguishes D⁰ (104) from D̄⁰ (97)
  correctly. The ordinals were never the problem.

---

## 5. WHY THIS BLOCKS A PRE-SPECIFIED CHECK, AND SO NEEDS A RULING

The owner's check **C5** requires: *the v2 reader in dominant-only mode
reproduces the v1 experiment-comparable table exactly.*

**C5 and correctness are now mutually exclusive.** A v2 map that conjugates
correctly will **not** reproduce v1's table, because v1's table is wrong. To
pass C5 as written, v2 would have to reproduce the defect deliberately.

**I have not chosen between them.** The v2 build **refuses to complete** rather
than pick — `tools/build_decay_parent_map_v2.py` raises `FAIL-CLOSED C2` and
writes no artifact.

### Options

| option | what it means | cost |
|---|---|---|
| **1. Fix conjugation in v2, retire C5** | v2 is correct; C5 is replaced by "reproduces v1 exactly **except** the conjugation correction, itemised" | rebuild v2, re-issue the experiment-comparable table, update `EXTRACTION_CONVENTIONS.md` §2 |
| **2. Fix v1 as its own change first, then build v2 on top** | separates the bug fix from the BR-split, so each is reviewable alone | one extra artifact revision; C5 then passes against the *fixed* v1 |
| **3. Reproduce the defect in v2 to satisfy C5** | **not recommended** — knowingly publishes a 17.8 pp error | none now, all of it later |

**Recommendation: option 2.** The conjugation fix and the BR-split are
independent defects with independent evidence, and merging them into one commit
makes both harder to review and impossible to revert separately. It also lets
C5 survive as a real check rather than being retired.

---

## 6. HOW IT SURVIVED UNTIL NOW

Worth recording, because the same blind spot could hide the next one.

- **The reader's invariance check cannot see it.** It asserts that regrouping
  conserves total weight. Conjugation errors move weight *between* bins and
  conserve the total exactly, so the check passes.
- **The v1 self-check compares against `hFlavourClosure`'s six-bin projection**,
  which is the *structural* convention — the one that does not use the map.
- **The predecessor's re-derivation check reproduced the table exactly** — and
  correctly so. It verified that the reimplementation matched the reader. **Both
  were faithfully consuming the same wrong artifact.** A reimplementation check
  proves agreement, not correctness.
- **The only thing that could catch it was a check on the physics**, and C2 —
  "every split product carries the parent's heavy-quark sign" — is exactly that.
  **The owner specified it, and it fired on the first split it examined.**
