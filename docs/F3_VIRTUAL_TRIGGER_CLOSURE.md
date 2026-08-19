# F3 — closure-only virtual-trigger validation: feasibility settled, run specified

**Required before the observable-definition sentence is written**
(`docs/REGISTRY_AND_MAPPING_PROPOSAL.md:213`). This session establishes that F3
**can** be run and specifies exactly how. **Step 1 (the commensurability gate) is COMPLETE and PASSED — `EXACT`, §4b.**
The comparison table (step 2) is not produced; see §5.

---

## 1. THE PRECONDITION HOLDS — the excited states are in the raw record

Measured on `hf_MONASH_job000.root` (**100,000 events**, schema
`hf_primary_ground_raw_v7`), counting events containing at least one such state:

| state | PDG | events / 100k | fraction |
|---|---|---|---|
| B*⁰ | 513 | **6,889** | 6.9 % |
| B*⁺ | 523 | **6,977** | 7.0 % |
| B*_s⁰ | 533 | 1,780 | 1.8 % |
| Σ_b*⁺ | 5224 | **83** | 0.083 % |
| Σ_b*⁰ | 5214 | **91** | 0.091 % |
| Σ_b*⁻ | 5114 | **83** | 0.083 % |
| Ξ_b*⁰ | 5324 | 15 | 0.015 % |
| Ξ_b*⁻ | 5314 | 14 | 0.014 % |

**F3 is feasible.** The raw record retains the excited states, so no re-generation
is needed — this runs against **already-promoted raw data**.

**Statistics at full HF_RUN3_V1 scale** (100 M events per tune):

- **B\***: ~6.9 M events per tune. Ample; block-level spread over ten blocks is
  computable with room to spare.
- **Σ_b\***: ~83 k events per charge state per tune, ~257 k summed over the three.
  Workable, and **block-level spread is computable** (~25 k per block summed).
  Per-charge-state per-block (~8 k) is thinner but not empty.

**Σ_b\* is the interesting one and the statistically limited one**, which is the
same shape as B6's residual. Expect the beauty-baryon channel to set the bound.

---

## 2. THE BLOCKER — there is no virtual-trigger path, by design

`analysis/status_analysis_THnSparse_qq.C` **cannot** do this:

```
:772-774   const char* selectionMode = "central_primary_ground_v1", ...
           if (std::string(selectionMode) != "central_primary_ground_v1") { ...refuse... }
```

The mode is **hard-refused**, and a grep for `virtual`, `closure_only`,
`closureTrigger` or `excited` in that macro returns **nothing**. Triggers come
from the pair registry's `definition.triggerPdg` (`:862,:872-874`) and are gated
by `EligibleBase(triggerPdg, heavyStatus, …)` (`:988`) — the ground-state
selector. **B\* and Σ_b\* are not in the 300-pair registry and cannot be made
triggers by configuration.**

> **This is correct behaviour, not a defect.** Every promoted directory records
> `analysis_macro_sha256`, and the 3000-directory v3 campaign is pinned to that
> hash. **Adding a selection mode to the production macro would invalidate the
> provenance of the campaign now being gated.** F3 must run **scratch-side**,
> which is what the brief specifies.

---

## 3. THE RUN, SPECIFIED

A scratch macro (not `AnalysisScripts/**`, not promoted) that:

1. **Reads the raw tree directly** — `tree`, schema `hf_primary_ground_raw_v7`,
   branches `heavyPdg` / `heavyStatus` / kinematics, plus
   `heavy_stability_audit` for the species set.
2. **Selects B\* and Σ_b\* as closure-only triggers** — no ground-state
   eligibility gate, no pair-registry lookup.
3. **Computes the compensation decomposition** for each, **by the same rule the
   production macro applies to ground-state triggers**, so the two are
   commensurable. *This is the part that must be read out of the production
   macro rather than re-invented — the comparison is worthless if the two sides
   decompose differently.*
4. **Emits the comparison table** — virtual-trigger decomposition against
   ground-state-trigger decomposition, **with block-level spread** over the ten
   deterministic blocks where computable.
5. **Asserts the macro sha** of whatever production code it mirrors (per the
   graduated convention: comparability assertions pin the program, never the
   checkout).
6. Scratch-deploy, retention unconditional.

**Inputs:** promoted raw under
`/data/alice/ipardoza/hadronization_production/HF_RUN3_V1/raw/`. Read-only.

---

## 4. PRE-REGISTRATION — recorded now, before any number exists

| outcome | reading |
|---|---|
| **Agreement within errors** | The trigger-side completeness bias is bounded and small. **One sentence closes the referee question**, with F3 as its support. |
| **Disagreement** | **A physics finding for the owner — not a problem to fix.** The trigger's own species correlates with how its compensation is distributed, which is exactly what junction topologies would do (`REGISTRY_AND_MAPPING_PROPOSAL.md:221-226`), and it is the mechanism the paper is about. |

**Neither outcome is a failure.** F3 exists because the natural argument — *"the
trigger's own channel doesn't matter, only the compensating flavour does"* — is
precisely the argument junction topologies break, and this is the last place to
accept an argument in place of a number.

**My prediction, recorded: agreement for B\*, and Σ_b\* too statistically thin at
block level to distinguish.** Basis: B* is a spin excitation of the same quark
content and its compensation should be indistinguishable from B's; Σ_b* yields
(~83 k/tune) are three orders below B*'s and the block-level spread will
dominate. **This prediction is n=0 — it rests on no measurement at all.**

---

## 4b. THE COMMENSURABILITY GATE — design, and why it is not a reimplementation

**The requirement** (owner ruling): a scratch closure run with **ground-state
triggers only** must reproduce the production `hFlavourClosure` decomposition
**bin-for-bin on the same input file**, before any virtual-trigger number exists.

**The obvious implementation is the wrong one.** Reimplementing the closure loop
scratch-side and comparing tests a reimplementation I would have had to get right
by hand — and that reimplementation is precisely the artifact most likely to be
subtly wrong. `EligibleBase` (`:725`) and `SectorCharge` (`:732`) live *inside*
the production macro and would have to be duplicated; only
`IsCentralKinematic`/`WrapDeltaPhi` come from the shared
`generation/producer/HeavyFlavourUtils.h`.

**So the gate runs the production macro itself**, unmodified, from the frozen
checkout, on one promoted raw file, with the same invocation the production
runner uses (`run_status_analysis.sh:268-270`, event filter `0,-1`), and compares
against the promoted directory.

**What that buys over reimplementation:**

- The closure loop is byte-identical to production **by construction**.
- It validates the **scratch harness** — invocation, environment, ROOT build,
  output layout — which reimplementation leaves untested and which is a real
  source of spurious disagreement.
- It establishes a **verified baseline**, so step 2 becomes a **minimal,
  reviewable diff** from a known-exact starting point rather than a fresh
  artifact whose agreement with production is assumed.

**The comparison is strict:** every filled bin of `hFlavourClosure` in **both
directions** (scratch→promoted and promoted→scratch, so a bin filled in only one
is caught), across **all 300 pair files**, with `max_abs_diff` reported. Verdict
is `EXACT` only on zero mismatches, zero missing objects, zero dimension
mismatches, and a non-zero pair count.

**The macro sha is asserted against the value the promoted directory records**
(`analysis_macro_sha256`), per the standing convention that assertions pin the
program rather than the environment. A mismatch aborts before any run.

**Cluster `5400225`**, submitted with `Requirements = (Machine !=
"wn-sate-072.nikhef.nl")` to keep it off the node running the 3000-directory
gate.

### First attempt failed on the provenance environment — my invocation, again

Cluster `5400225` ran and died in **10.66 s**:

```
ONE_PASS_ANALYSIS_ERROR missing required analysis provenance HADRONIZATION_ANALYSIS_COMMIT
```

**The macro sha assertion passed** — the scratch macro *was* the one that produced
the promoted directory. What I omitted was the **nine provenance variables**
`run_status_analysis.sh:136-145` exports before invoking it. The macro fails
closed without them, which is correct.

**The fix takes each from the promoted directory's own
`analysis_job_metadata.json`** rather than hand-writing them — `repository_commit`,
`analysis_macro_sha256`, `analysis_profile`, `raw_sha256` (twice), `campaign`,
`tune`, `logical_id`, `raw_validation_evidence_mode`,
`raw_validation_receipt_sha256`. **Deriving them from the metadata makes the
scratch run provably configured identically to the run that produced the output
it is compared against**; hand-writing them would reintroduce exactly the
divergence this gate exists to exclude.

**Resubmitted as cluster `5400242`.**

> **This is the third invocation-argument failure of the arc** (the gate's
> `--production-root`, the 10/25 pin assertion, now this). Each was caught in
> seconds by a fail-closed check rather than by a wrong number surviving into a
> result — which is the system working — but the pattern is mine and it is
> consistent: **I get the design right and the invocation wrong.**

### ✅ RESULT — the gate PASSES, and it passes exactly

Cluster **`5400242`**, `wn-lot-038`. Scratch analysis `rc=0`, **300/300** files,
wall **19.63 s**, maxRSS 910,680 kB.

```
CMP_SUMMARY pairs=300 filled_bins=1476268 bin_mismatches=0 obj_missing=0
            dim_mismatch=0 max_abs_diff=0 worst=
CMP_VERDICT EXACT
```

**1,476,268 filled bins compared in both directions across all 300 pair files.
Zero mismatches. `max_abs_diff` is exactly 0 — not small, zero.**

**F3 step 1 is complete.** The scratch harness reproduces promoted output
**bit-identically**, so:

- the invocation, environment, ROOT build and output layout are all validated;
- the closure loop is byte-identical to production **by construction**;
- **a verified baseline now exists**, and step 2 is a minimal, reviewable diff
  from it rather than a fresh artifact whose commensurability is assumed.

**No virtual-trigger number is blocked on commensurability any more.** What
remains for step 2 is the trigger-set change itself and the comparison table.

**A mismatch would have been an item-STOP** — it would mean the scratch harness cannot
reproduce promoted output at all, and no virtual-trigger number could be trusted
until it does.

---

## 5. WHY THE TABLE IS NOT IN THIS FILE

The deliverable is a physics comparison whose value is entirely in being
commensurable with the production decomposition. Producing it requires reading
the compensation rule out of the production macro and reimplementing it
faithfully scratch-side — and **a number produced by a hastily-mirrored rule
would be worse than no number**, because it would look like a measurement and
would be cited as one.

**Feasibility is settled, statistics are quantified, the blocker is identified
with `file:line`, and the run is specified.** The remaining work is the scratch
macro and one run against already-promoted data. **Nothing about it is blocked
on the gate or the merge** — it can run in parallel whenever someone has the
context to do the decomposition rule justice.


---

## 6. STEP 2 — built, running end to end, and stopped one line short

**Status: the harness works; the virtual triggers do not yet fire.** Recorded at
the exact stopping point so a successor resumes with a one-line change.

### What works

`f3_runs/f3_virtual.diff` — **111 added, 6 removed**, generated by a committed
script (`make_f3_patch.py`) so the diff is reproducible rather than hand-edited.
Final run (`5400819`): `rc=0`, **301 files** (300 pairs + `f3_virtual_triggers.root`),
one `ONE_PASS_ANALYSIS_SUMMARY`, ground-state sum rules all **1**, and the new
`F3_VIRTUAL_CLOSURE` lines emit for all twelve virtual PDGs.

### What does not

```
F3_VIRTUAL_CLOSURE pdg=513  weighted_triggers=0 full_phase_space=0 in_acceptance=0
F3_VIRTUAL_CLOSURE pdg=5224 weighted_triggers=0 full_phase_space=0 in_acceptance=0
   ... all twelve identical ...
```

**Every virtual trigger has `weighted_triggers = 0`. None was ever selected.**

### The cause, and it is a one-line fix

`EligibleBase` (`:725-730`) tests

```cpp
isFinal && central && FindGroundState(pdg) && IsDirectPrimaryStatus(status)
        && IsCentralKinematic(pt, eta, trigger)
```

and edit C relaxed `isFinal` and `FindGroundState(pdg)` while **keeping
`(*heavyCentral)[triggerIndex]`**. But the producer sets

```cpp
generation/producer/heavyflavourcorrelations_status.cpp:1186-1187
  const bool centralGroundState = FindGroundState(id) != nullptr;
  heavyCentral.push_back(centralGroundState ? 1 : 0);
```

> **`heavyCentral` *is* `FindGroundState(pdg)`, precomputed.** Dropping one while
> keeping the other relaxes nothing: B* and Σ_b* have no ground-state entry, so
> `heavyCentral == 0` and they are rejected exactly as before.

**The fix:** for virtual PDGs, drop `heavyCentral` as well, leaving
`IsDirectPrimaryStatus(status) && IsCentralKinematic(pt, eta, true)`. Note that
`IsCentralKinematic` is the **kinematic acceptance** and is a genuinely different
condition — it stays.

**Then re-run and read `F3_VIRTUAL_CLOSURE`:** `full_phase_space ≈ 1` means edit
D's descendant exclusion is right and the table can be built; **`≈ 0` means it is
wrong and no table should be produced.**

**One harness nit for the successor:** the run's success check asserts
`files == 300`, but the correct count is now **301** — edit E adds
`f3_virtual_triggers.root`. The last run reported `ABORT` on that alone despite
being otherwise clean.


---

## 7. ✅ F3 COMPLETE — the table, under the ruled predicate

**Owner ruling applied.** The predicate is
`isFinal ∧ IsDirectPrimaryStatus ∧ IsCentralKinematic ∧ sectorCharge ≠ 0`;
only the central/ground-state legs are dropped, and **the descendant walk is
removed**. Diff `f3_runs/f3_virtual.diff`, **79 added / 6 removed**, three edits
(B, C, E) down from five. Run `5401169`, `rc=0`, 301 files, one summary.

### 7a. The rationale I gave for the descendant walk was wrong

I argued that `B* → B γ` at ~100 % would put the daughter B into its own parent's
compensation sum at −1. **In this record that cannot happen: heavy-flavour decays
are disabled, so every heavy hadron is final and none has daughters.** Verified
on the input before rebuilding — of **11,440** events containing B*/Σ_b*:

| check | events |
|---|---|
| any with `isFinal == 0` | **0** |
| any with a daughter link | **0** |
| any with sector charge `qb == 0` | **0** |

The producer says so directly: heavy hadrons *"are final only because their
decays were disabled"* (`heavyflavourcorrelations_status.cpp:1026-1029`). The
real hazard is non-final event-record **copies**, and **keeping `isFinal`
eliminates those** — which is exactly why the ruled predicate retains it.

### 7b. The sum rule — pre-registration met exactly

**Pre-registered: full-phase-space closure = 1 exactly for every
virtual-trigger species. Any deviation is an item-STOP.**

**All twelve give exactly 1.** Every ground-state trigger in the same run also
closes at exactly 1 (0 exceptions). **No item-STOP.** The record's copy structure
contains nothing unmodelled.

### 7c. THE TABLE — trigger-side completeness, virtual vs ground state

`in_acceptance` is the fraction of a trigger's flavour compensation that falls
inside acceptance: the trigger-side completeness the referee question is about.

| virtual trigger | n | in-acceptance | | ground-state counterpart | in-acceptance |
|---|---|---|---|---|---|
| B*⁰ (513) | 3107 | 0.8632 | | B⁰ (511) | 0.8725 |
| B̄*⁰ (−513) | 3108 | 0.8610 | | B̄⁰ (−511) | 0.8809 |
| B*⁺ (523) | 3165 | 0.8727 | | B⁺ (521) | 0.8636 |
| B*⁻ (−523) | 3160 | 0.8690 | | B⁻ (−521) | 0.8575 |
| B*_s⁰ (533) | 707 | 0.8642 | | *(no B_s trigger in the registry)* | — |
| B̄*_s⁰ (−533) | 671 | 0.8703 | | — | — |
| Σ_b*⁺ (5224) | 32 | 0.8750 | | Λ_b (5122) | 0.8692 |
| Σ̄_b*⁻ (−5224) | 29 | 0.8966 | | Λ̄_b (−5122) | 0.8680 |
| Σ_b*⁰ (5214) | 36 | 0.8056 | | — | — |
| Σ̄_b*⁰ (−5214) | 39 | 0.8462 | | — | — |
| Σ_b*⁻ (5114) | 34 | 0.9412 | | — | — |
| Σ̄_b*⁺ (−5114) | 23 | 0.9130 | | — | — |

**Grouped:**

| | mean | range | spread |
|---|---|---|---|
| ground-state beauty mesons | **0.8686** | 0.8575–0.8809 | 0.0234 |
| virtual B* (non-strange) | **0.8665** | 0.8610–0.8727 | 0.0117 |
| **difference** | **−0.0022 (−0.25 %)** | | |
| ground-state Λ_b | **0.8686** | 0.8680–0.8692 | 0.0012 |
| virtual Σ_b* | **0.8796** | 0.8056–0.9412 | 0.1356 |
| **difference** | **+0.0110** | | |

### 7d. The reading: AGREEMENT within errors

- **B\* against B: −0.25 %.** The difference between the virtual and
  ground-state means is **an order of magnitude smaller than the ground states'
  own charge-state spread** (0.0022 against 0.0234). There is no trigger-side
  effect visible at B* statistics.
- **Σ_b\* against Λ_b: +0.011, and not resolvable.** With n = 23–39 per charge
  state the approximate counting σ is **0.052–0.068**; the observed half-range is
  **0.068**. The scatter is what statistics alone predicts. **Statistically
  indistinguishable.**

**⇒ The pre-registered "agreement" branch. The one-sentence trigger-side answer
is supported:** the compensation decomposition does not depend measurably on
whether the trigger is a ground state or an excited state of the same flavour, at
the statistics available.

**My own prediction — "agreement for B*, Σ_b* too thin at block level to
distinguish" — HITS on both halves.**

### 7e. What this does NOT establish

- **Block-level spread is not computable here.** One file is one number per
  species; the ten deterministic blocks do not exist until the merge lands. The
  σ quoted above is an **approximate counting** estimate on a weighted sum, not a
  block SEM, and is labelled as such.
- **One file, MONASH only, 100 k events.** The B* conclusion is solid at ~3 k
  triggers per charge state; **the Σ_b\* conclusion is a non-observation at
  n ≈ 30**, not a measurement of agreement. At full statistics Σ_b* reaches
  ~257 k, where the same comparison would actually constrain something.
- **Junction topologies are not separated out.** The mechanism that motivated F3
  (`REGISTRY_AND_MAPPING_PROPOSAL.md:221-226`) predicts a trigger-species
  correlation specifically through junction compensation. This table is
  inclusive; it does not isolate that channel.

**To the owner with the table. No interpretation beyond it.**

---

## 8. THE DECOMPOSITION COMPARISON — owner completeness item

**Required for filing:** the archived document must carry the per-category
decomposition comparison, not only the acceptance fractions. Built from the
**retained closure objects** of run `5401169` — **no new run**.

Sources: `f3_runs/step2/out/f3_virtual_triggers.root` (12 virtual triggers) and
the retained pair files, one per distinct ground-state trigger. Restricted on the
ground side to the **six beauty triggers** (511, ±; 521, ±; 5122, ±), so the
comparison is like-for-like against the all-beauty virtual set.

### Per-category — the `heavyStateCategory` axis

| cat | name | virtual % | ground % | diff (pp) |
|---|---|---|---|---|
| 0 | kCentralGround | 33.1562 | 33.8618 | **−0.7057** |
| 1 | kHiddenHeavy | 0 | 0 | 0 |
| 2 | kMultiplyHeavy | 0 | 0 | 0 |
| 3 | kOtherNoncentral | 0 | 0 | 0 |
| 4 | kExcludedVector | 65.8299 | 65.0812 | **+0.7488** |
| 5 | kExcludedExcited | 1.0139 | 1.0570 | −0.0431 |

### Baryon / meson — the species axis, grouped by the ordinal table

Grouped by the ordinal artifact's own `is_baryon` / `is_meson` columns, so the
grouping is the same table the extraction layer uses.

| kind | virtual % | ground % | diff (pp) |
|---|---|---|---|
| baryon | 4.8242 | 5.0585 | **−0.2343** |
| meson | 95.1758 | 94.9415 | +0.2343 |
| other | 0 | 0 | 0 |

Weighted totals: virtual **12,230**, ground **5,298**.

### Reading — consistent within counting statistics

Treating the weighted totals as effective counts:

| quantity | difference | combined σ | pulls |
|---|---|---|---|
| kCentralGround share | −0.706 pp | 0.777 pp | **0.91 σ** |
| baryon share | −0.234 pp | 0.358 pp | **0.65 σ** |

**Both under 1 σ.** The compensation decomposition under virtual triggers is the
same as under ground-state triggers, in category composition and in baryon
fraction, to the precision one file supports.

> **This strengthens §7d and does not extend it.** The acceptance fractions said
> *how much* compensation is captured; this says *what kind*. Both agree, and
> both are bounded by the same single-file statistics — **the baryon share is the
> observable the paper is about, and 0.36 pp is the resolution here, not a
> measurement of equality to better than that.**

**The limits of §7e apply unchanged**, in particular: this is inclusive over
junction and non-junction topologies and **does not test the mechanism**.
