# Proposal — excited-state recording, ground-state mapping, and the observable's definition

**Written 2026-08-08. Nothing implemented.** Responds to the physics review and
to the category measurement made in answer to it.

**Status of numbers:** every count below is measured, with its method beside it.
**The category fractions carry no block SEM yet and must not be quoted
paper-facing.** The population counts (219/50/152/…) are exact reads of a
produced file and are not statistical.

---

## 0. Two corrections before the design

### 0a. Do NOT extend `FindGroundState` in place — it would destroy the instrument

The review proposed extending `Hadronization::FindGroundState` to resolve
`B* -> B`, `Σ_b* -> Σ_b` and so on. **That specific move is unsafe, for a
reason stronger than the validator it trips.**

`FindGroundState` is not only a lookup. Its result *defines* the category axis:

```
heavyflavourcorrelations_status.cpp:1186   const bool centralGroundState = FindGroundState(id) != nullptr;
heavyflavourcorrelations_status.cpp:1191   heavyStateCategory.push_back(ClassifyHeavyStateDetailed(centralGroundState, ...))
HeavyFlavourUtils.h:355                    if (central) return HeavyStateCategory::kCentralGround;
```

**If `FindGroundState` resolved excited states, every excited state would return
`central = true` and land in `kCentralGround`. Categories 4 and 5 would empty
into category 0 — deleting exactly the decomposition that revealed the
problem.** The measurement and the proposed fix would annihilate each other.

It also breaks a deliberate contract: `Validation/AuditSpeciesRegistry.C:101-110`
iterates 26 named excited states (`413, 423, 433, 513, 523, 533, 543, 4114,
4224, 4334, 5114, 5224, 5334` and conjugates) and raises
`SPECIES_REGISTRY_ERROR` **if any of them resolves**. That validator exists to
assert the registry holds ground states only.

**Proposal: `FindGroundState` keeps its exact current meaning — strict registry
membership.** Add a *separate* resolver, `ResolveToGroundState(pdg, convention)`,
returning the mapped ground state or `nullptr`. Nothing that currently calls
`FindGroundState` changes behaviour. The 15 call sites stay correct as written.

### 0b. The gate is CPU-bound, not latency-bound — a load-bearing number was wrong

**Reported here because it invalidates a premise used in B10 and in the Phase 4
checklist, both of which this proposal's cost estimates touch.**

The detached P=1 reference completed:

```
P1_TIME wall=4156.96 user=3612.88 sys=205.17 maxrssKB=451480 cpupct=91%
```

`/data/alice/ipardoza/poolsweep_run01/p1_time.txt`, unmodified gate,
`--report` omitted, uncontended.

| | recorded in B10 | measured now |
|---|---|---|
| wall @ 300 dirs | 4354 s | **4156.96 s** (95.5 %, agrees) |
| CPU | ~165–220 s | **3818.05 s** |
| **CPU/wall** | **0.050** | **0.919** |

**Wall agrees to 4.5 %. CPU disagrees by a factor of ~23.** Since the work is
the same and the wall is the same, **the 0.050 figure was wrong at its origin** —
it came from a mid-run sample (`165 s CPU at t=3269 s`) that evidently did not
capture the ROOT children the gate spawns at `validate_analysis_outputs.py:506`.

**My own pre-registered prediction was wrong in both directions** (I predicted
wall well under 4354 s and CPU ~165–220 s as the invariant). The pre-registration
did its job: it made the error visible instead of absorbable.

**This is the second time a validation-class stage predicted at CPU/wall 0.050
measured CPU-bound** — `validate_pair_directory.sh` came in at 0.982. **Both
0.050 claims trace to the same origin and neither survived measurement.**

**Consequence for the pool remedy:** it still works, but *not for the stated
reason*. "Latency-bound, so more readers hide the wait" is false. The gate is
300 independent CPU-bound directory validations — the **same** shape as the
merge, not the opposite one. The Phase 4 checklist's fan-out table says the
gate and merge fan out for opposite reasons; **that table needs correcting, and
the correction simplifies it — both fan out for the same reason.**

---

## 1. What is actually in the data — measured, exact

From `heavy_stability_audit` in
`/data/alice/ipardoza/hadronization_production/HF_PT2_INT/raw/JUNCTIONS/hf_JUNCTIONS_job001.root`:

| quantity | count |
|---|---|
| total signed heavy states in PYTHIA's table | **219** |
| **`final_may_decay != 0`** | **0** — stabilisation verified on produced data |
| in the ground-state registry (`central_registry == 1`) | **50** — matches `kGroundStates` exactly |
| open-heavy (`q_c` or `q_b` != 0) | 202 |
| hidden-heavy (J/ψ, Υ, …) | 17 |
| **open-heavy but NOT in the registry** | **152** |
| — vector mesons (`spin_type == 3`) | 42 |
| — baryons | 82 |
| — charm-tagged / beauty-tagged | 96 / 92 (overlap 36 = B_c family) |

**152 open-heavy species are produced, stable, and invisible to every yield the
analysis reports.** That is the population behind the category-4 and category-5
weight.

**The pair-count rule, confirmed exactly:** `config/pair_registry_definition_v1.json`
gives 6 central triggers per sector and "all signed states" as associates,
sector-matched. `6 x 24 charm + 6 x 26 beauty = 300`. Every downstream shape
number scales off this identity.

---

## 2. The two mapping tables — derived at initialisation, never hardcoded

Both are built once at producer start-up by walking PYTHIA's own tables, and
**written into `heavy_stability_audit` beside `original_may_decay` /
`final_may_decay`**, so the mapping is hashed into `upstream_stability_sha256`
and carried into all 33 promoted directories. A reader can then verify which
mapping produced any figure.

**New branches:** `diquark_parent_pdg`, `decay_parent_pdg`,
`decay_parent_branching`, `mapping_rule_version`.

| | rule | source |
|---|---|---|
| **Diquark-structure parent** | same valence quark content, same light-diquark spin, lowest mass | quark content + `spin_type` from `ParticleData` |
| **Decay parent** | heavy-flavour daughter of the dominant decay channel | `ParticleDataEntry` channel list + branching ratios |

`Σ_b* -> Σ_b` / `Σ_b* -> Λ_b` is where they differ; `B* -> B`, `D* -> D`
coincide under both.

**Record `decay_parent_branching` alongside**, exactly as the review asks, so
"dominant" is visible where it is 100 % (`B* -> B γ`) and where it is not.

**One assumption to verify before implementing, flagged rather than assumed:**
this requires PYTHIA to retain decay-channel tables after
`particleData.mayDecay(id, false)`. `mayDecay` gates *execution*, not the table,
so channels should remain readable — **but I have not tested it**, and the whole
decay-parent map depends on it. **First implementation step is a five-line probe
printing channel counts for `513` after stabilisation.** If channels are gone,
the decay-parent map must instead be derived before the stabilisation pass.

---

## 3. Default convention, and the wording

**Default: diquark-structure.** The paper is about hadronisation mechanisms —
what fraction of beauty hadronises into a spin-1 light-diquark baryon — and
grouping `Σ_b*` with `Σ_b` measures the diquark channel that the junction
picture actually predicts.

**But it inverts the reader's default**, so it must be stated, not implied.
Proposed text:

> Because all heavy hadrons are kept stable, yields are grouped by
> **light-diquark structure** rather than by decay: `Σ_b^*` is counted with
> `Σ_b`, both carrying a spin-1 light diquark. This differs from an
> experimentally reconstructed yield, in which `Σ_b^*` feeds `Λ_b`. Vector
> mesons are unaffected — `B^*` is counted with `B` under either convention.
> The alternative grouping is available in the released data and is recorded
> per species in the production provenance.

**Stability is a physics choice and belongs in the text as one.** It is what
makes both conventions available as downstream sums: because nothing decays,
`Σ_b*` remains a distinct species in the record, so "Λ_b including `Σ_b*`
feed-down" is a sum over species already present. **Enabling strong decays would
merge the populations irreversibly and insert a decay layer exactly where origin
resolution has its largest unquantified tune-dependent failure mode.**

---

## 3b. STAGING — decided 2026-08-09. Stage-1 is analysis-side and gates nothing upstream

**This supersedes the "one change" framing below.** §4's Option A/B costing
stands as analysis of the *Δφ registration* question, which is now **stage-2**.

### Stage-1 — pre-resubmission, ANALYSIS-SIDE ONLY

**Contents:** the closure **species axis** plus the two **mapping tables**, as
**versioned analysis artifacts**.

**What stage-1 does NOT touch:** no tune card, no producer, no registry, no
generated header. **The pair count stays 300.** The five sibling literals in
`validate_pair_block_closure.sh:67` survive untouched. `upstream_executable_sha256`
stays at `e54b27bb9e3f…`.

**The §0a/§4B eligibility conflict is DISSOLVED in stage-1 — by construction,
not by fixing it.** No excited associate enters the pair registry in stage 1, so
`EligibleBase`'s `central && FindGroundState` gate is never asked to admit one.
`FindGroundState` stays strict, the category axis stays intact, and
`AuditSpeciesRegistry.C:101-110` stays true. **The conflict returns, live, in
stage-2.**

**Therefore stage-1 does not gate generation.** It gates *analysis*, and it can
be implemented in parallel with any authorized production run.

### Stage-2 — DEFERRED

**Contents:** Δφ registration of the excited families (§4 Option B) and
producer-side mapping branches in the `heavy_stability_audit` tree.

> **RULE, RECORDED: stage-2 producer changes ride a future campaign generation
> in full, never mid-campaign. No schema drift inside a campaign.**

A campaign whose early jobs write one schema and whose late jobs write another
is not a dataset; it is two datasets with one name, and every provenance hash in
the chain would be arguing with itself.

### Stage-1 design answers — written as requirements

**(F3) Closure-only virtual-trigger validation — REQUIRED before the
observable-definition sentence is written.**

Run `B*` and `Σ_b*` as **closure triggers from the raw record** and compare the
compensation decomposition against ground-state triggers. Purpose: **bound the
trigger-side completeness bias** — the part of the excluded-fraction problem
that affects the *trigger* leg rather than the associate leg.

**Why measured rather than argued:** the natural argument is "the trigger's own
channel doesn't matter, only the compensating flavour does". **Junction
topologies are exactly where that fails** — a junction baryon's compensation is
shared across three strings rather than balanced against one partner, so the
trigger's own species can correlate with how its compensation is distributed.
**That is the mechanism the paper is about, so it is the last place to accept an
argument in lieu of a number.**

**(F4) Decay-parent map — a PYTHIA-linked probe, hashed, validated, never
hand-written.**

- Derive against the **pinned 8.317 install**, via a small linked probe run —
  **not** from tables typed into a header.
- **Output: a versioned, hashed JSON artifact.**
- **Validated at analysis time against each raw file's `heavy_stability_audit`
  tree** — species-set match — and **fails closed** on mismatch.
- **The diquark-parent map derives from the stability tree alone** (quark
  content + `spin_type`), so it needs no probe.
- **Open dependency, unchanged from §2:** the probe must confirm PYTHIA retains
  decay-channel tables after `mayDecay(id,false)`. **Untested. First step.**

**(F5) Supersession policy — re-analysing an already-promoted campaign.**

- **Schema-tagged output directories**, so a re-analysis lands beside its
  predecessor rather than over it.
- **Provenance distinguishes supersession from coexistence** — a reader must be
  able to tell "this replaces that" from "these are two valid views".
- **Write-once guards untouched.** **Nothing is deleted.**

**(F5-DRAFT) Supersession policy — DESIGN FOR OWNER REVIEW, no code written.**

**The problem.** Stage-1 re-analyses HF_PT2_INT, which is **already promoted**.
Its 33 merged directories, their sidecars and their closure receipts exist and
are write-once. A second analysis pass produces a second set of the same
objects. **Nothing in the current layout can express "these two are both valid
views of one campaign" or "this one replaces that one" — and the distinction
matters, because one of them is a reason to keep both and the other is a reason
to stop using one.**

**Proposed shape, in four parts:**

**1. Schema-tagged output directories.** Analysis output roots carry their
schema version in the path — `…/analysis_v2/…` beside `…/analysis_v3/…` rather
than one overwriting the other. **A re-analysis lands beside its predecessor,
never on it.** This falls out of the existing write-once guards rather than
fighting them: `merge_one()` already refuses to promote onto an existing
directory, so a same-path re-analysis is already impossible — the tag is what
makes it *legible* instead of merely blocked.

**2. Provenance distinguishes supersession from coexistence.** A new field in
the merged provenance sidecar, `relation_to_prior`, with exactly three values:

| value | meaning | consumer behaviour |
|---|---|---|
| `independent` | first analysis of this campaign at this schema | normal |
| `coexists_with:<schema>` | both views valid; they answer different questions | **both quotable**, must be labelled |
| `supersedes:<schema>` | this replaces that one; the prior is retained but wrong | **prior not quotable** |

**The value is recorded by the run that creates it, not inferred later.** A
consumer that finds two views and no relation field must **fail**, not guess —
guessing is how one silently becomes canonical.

**3. Write-once guards untouched, nothing deleted.** No promoted directory is
removed, rewritten, or relabelled, **including one marked superseded.** A
superseded view is the evidence for why the current one exists; deleting it
destroys the audit trail at exactly the moment it becomes interesting. This is
the retain-your-outputs rule applied to promoted data.

**4. Stage-1's own case, stated concretely.** Stage-1 adds a species axis to
`hFlavourClosure` and changes no physics. **The honest relation is
`coexists_with`, not `supersedes`** — the v2 output remains a correct answer to
the question it was asked. Calling it superseded would imply the earlier
measurements were wrong, and **Measurements 1–3 and the closure results stand.**

**APPROVED 2026-08-09 with one added requirement — coexistence must be
LEGIBLE.** The owner ratified the `coexists_with` framing for stage-1 and
attached a condition that is now part of the policy, not an aspiration:

> **v3 outputs carry schema tags and provenance to the same raw manifest, and
> every merge and plot consumer FAILS CLOSED on a v2/v3 mix. Nothing may
> silently combine them.**

**Why fail-closed rather than a warning.** Two coexisting views of one campaign
answer different questions; a consumer that reads both and averages them is
producing a number that answers neither. **A warning is a thing an operator
scrolls past** — and the whole reason coexistence is permitted here is that
neither view is wrong, which is exactly the condition under which a silent mix
looks plausible.

**Three concrete obligations this creates:**

1. **Every v3 output directory records its schema tag AND the sha256 of the raw
   manifest it derives from.** Same manifest ⇒ same campaign ⇒ legitimately
   comparable. Different manifest ⇒ they are not two views of one thing and the
   coexistence question does not arise.
2. **Merge consumers refuse a mixed input set.** `merge_one()` already refuses
   to promote onto an existing directory; the new refusal is one level up —
   **a merge whose inputs carry two schema tags fails before it starts**, rather
   than producing a directory that is half one thing and half another.
3. **Plot consumers refuse a mixed input set**, and say which tags they found.
   A figure silently built from mixed schemas is the failure mode with no
   downstream check at all — nothing validates a PDF.

**Not yet designed:** where the schema tag physically lives (directory name,
provenance field, or both) and whether the raw-manifest sha256 belongs beside
it. **That is output-layout, which stays unwritten until the layout itself is
approved.**

**Open questions for the owner, not decided here:**

- **Does `relation_to_prior` belong in the merged provenance sidecar or in a
  campaign-level manifest?** Sidecar is per-directory and self-contained;
  campaign-level is one place to read but adds a cross-directory dependency —
  which is exactly what B10's audit went to some trouble to establish does not
  currently exist.
- **Who may set `supersedes`?** If any re-analysis can declare its predecessor
  superseded, the flag is worth little. It probably needs to be an owner act
  recorded in-tree, not a runtime default.
- **What happens to the closure receipts** of a superseded view — retained
  as-is, or annotated? Annotating means writing to promoted data, which the
  rules forbid.

**No output-layout code will be written until this is approved.**

**(F6) The species axis carries a fail-closed unmapped guard.**

**Any sector-charged PDG outside the ordinal table fails the run.** **No silent
overflow bin.** An overflow bin is how 152 species became invisible in the first
place; the replacement must not reintroduce the same failure mode with a
friendlier name.

### Paper-facing note — OWNER-SIDE

**The Δφ observables remain ground-state-defined through resubmission.** Stage-1
adds yields and fractions over the full species set; it does **not** redefine
the correlation observable.

**The observable-definition sentence must say so explicitly, with the F3 result
as its support.** Without F3, that sentence is an assertion; with it, it is a
bounded claim.

---

## 4. Two implementation shapes — costed. **Recommendation: B** *(this is now STAGE-2)*

**The review's instinct is right, and the arithmetic is decisive.**

### Option A — register every excited state as an associate

Applying the `bc_policy` (B_c to beauty): charm associates `24 -> 84`, beauty
`26 -> 118`.

**New pair count = `6 x 84 + 6 x 118` = 1212 files — 4.04x.**

Everything output-fixed scales by 4.04x:

| | now | Option A |
|---|---|---|
| pair files | 300 | **1212** |
| the two directory validations per `merge_one` | 1278 s (79 % of the 1613 s window) | **~5163 s** |
| a central `merge_one` window | 1613 s | **~5482 s** |
| merge phase, 33 directories | 4 h 25 m | **~17 h** |
| `object_content_sumw2_closure_checks` | 6 x 300 = 1800 | 6 x 1212 = **7272** |

Peak RSS stays ~flat (files are processed one at a time), but **all five
deferred literals in `validate_pair_block_closure.sh:67` break**, and the merge
CPU projection must be retaken.

### Option B — species-aware closure axis + four registered species

Widen `hFlavourClosure` to carry species (or add a species axis), giving the
**full 219-species decomposition with no new pair files**, and register only the
four families wanted in the Δφ observable: `B*`, `D*`, `Σ_b*`, `Σ_c*`
(signed: 4 + 4 + 6 + 6 = 20; charm +10, beauty +10).

**New pair count = `6 x 34 + 6 x 36` = 420 files — 1.40x.**

| | Option A | **Option B** |
|---|---|---|
| pair files | 1212 (4.04x) | **420 (1.40x)** |
| merge phase | ~17 h | **~6 h** |
| yields/fractions for all 219 species | via 1212 pair files | **via the closure axis, free** |
| Δφ correlations for `B*/D*/Σ*` | yes | **yes** |
| Δφ for the other 148 species | yes | no — **and nobody has asked for it** |

**Recommendation: Option B.** It buys the entire yield-and-fraction correction —
which is the physics problem — at 1.40x rather than 4.04x, and it keeps Δφ for
precisely the states the observable needs. Option A pays a 4x tax across every
downstream stage to obtain per-species Δφ for 148 states with no stated use.

**The cost of B that A avoids:** `hFlavourClosure` gains a species axis, so its
`THnSparse` bin count rises. Given the measured chunking behaviour this is the
one place B could surprise us — **the axis should be indexed by a compact
species ordinal (0–218), not by PDG code**, or the sparse becomes needlessly
wide.

---

## 5. What re-runs, and what it costs

**No regeneration.** The raw files retain everything
(`heavyflavourcorrelations_status.cpp:1186-1193` tags rather than filters;
confirmed by 152 non-registry species present in the audit tree and by
categories 4/5 carrying weight).

1. **Producer** — mapping tables only, no event-loop change. But
   `GeneratedHeavyFlavourRegistry.h` and the producer translation unit change,
   so **`upstream_executable_sha256` moves off `e54b27bb9e3f…`**. That breaks
   provenance comparability with HF_PT2_INT and **must be stated plainly** — it
   is not a silent change.
2. **Analysis stage** — re-run the 300-job shape (cluster `5323114`). Same
   inputs, same job count.
3. **Merge** — 33 directories at 420 pair files: **~6 h** under B, from the
   measured 4 h 25 m x 1.40. Fan-outable per directory.
4. **Gate** — re-runs ahead of the analysis. Now known CPU-bound at 0.919, wall
   ~4157 s at 300 directories.

**Estimate under B: one analysis campaign plus ~6 h of merge — well inside a
day of wall-clock, no generation.**

---

## 6. Effect on the three pairwise contrasts

**Every yield-based contrast must be retaken.** The baryon fraction and any
species ratio currently count directly-produced ground states only, which is
33–49 % of compensating beauty and tune-dependent. **These are not corrections
to the published numbers; they change what the numbers mean.**

- **Retake:** inclusive baryon fraction, `Σ_b/Λ_b`, and every species ratio.
- **Unaffected:** the three merge measurements (RSS, wall-clock, closure) —
  they are pipeline properties, not physics. **But measurement 2 and the merge
  CPU projection are taken at 300 pair files and must be rescaled to 420.**
- **Unaffected:** seed ledger, manifest, campaign shape.

**The baryon fraction must state what it is a fraction of.** With the closure
axis it becomes a defensible fraction over the full charm or beauty sector —
all 219 species — rather than "within the 12 registered trigger species".

---

## 7. The optional-trigger question — subsidiary, and the answer is yes

**With species-aware closure and recorded mappings, "which species can be a
trigger" becomes configuration rather than structure.** `centralEligible` is
already the precedent: `GeneratedHeavyFlavourRegistry.h` carries six states with
`centralEligible = false` — `±5212` (Σ_b⁰) and `±5312`/`±5322` (Ξ_b′) — that are
produced, stored and analysed but excluded from central results, with per-state
reasons in `config/heavy_flavour_species_v1.json`.

**A second axis is needed, not a reuse of that one.** `centralEligible` answers
"may this be quoted"; the new one answers "is this a trigger". They are
independent — Σ_b⁰ should be *measured as a trigger* and *not quoted*.
**Proposal: add `triggerEligible`, default to the current 12, and keep
`centralEligible` for publication.**

**Record, per the review:** Σ_b⁰'s exclusion is a **publication** exclusion, not
a physics one. It should be measured and merely not quoted. **Whatever the paper
calls "Σ_b" must read `Σ_b^±`.** The recorded reason — PDG 2025 assigning no
official MCID to 5312/5322 and treating Σ_b⁰ as an unmeasured model prediction —
says nothing about whether PYTHIA produced it. **An isospin triplet split across
an eligibility flag needs its rationale in `docs/DESIGN_AND_RATIONALE.md`, not
only in a JSON field.**

---

## 7b. Amendments — gaps stated, NOT resolved (added 2026-08-09)

### (a) ELIGIBILITY GAP — §0a and §4B currently conflict. Owner question

**Option B cannot work as written, and the conflict is internal to this
document.**

`EligibleBase` (`analysis/status_analysis_THnSparse_qq.C:687-692`):

```cpp
return isFinal && central && Hadronization::FindGroundState(pdg) &&
       Hadronization::IsDirectPrimaryStatus(status) &&
       Hadronization::IsCentralKinematic(pt, eta, trigger);
```

Three facts that do not fit together:

1. Eligibility requires **both** `central` (the raw branch) **and**
   `FindGroundState(pdg)`.
2. **`heavyCentral` is 0 for every excited state in all existing raw** — the
   producer sets it from `FindGroundState` (`heavyflavourcorrelations_status.cpp:1186`).
3. **§0a of this proposal correctly freezes `FindGroundState`**, because
   extending it would collapse categories 4 and 5 into `kCentralGround` and
   destroy the instrument that measured the problem. And
   `Validation/AuditSpeciesRegistry.C:101-110` **asserts** that `413, 423, 433,
   513, 523, 533, 543, 4114, 4224, 4334, 5114, 5224, 5334` and conjugates never
   resolve — **four of Option B's registered families are on that list.**

**So Option B's excited associates cannot pass eligibility through the
ground-state registry, and the registry is the one thing §0a says must not
move.**

**Candidate shape, not a decision:** a **separate associate-membership set**,
distinct from the ground-state registry, with **excited associates not gated on
`heavyCentral`**. `EligibleBase` would then test membership-for-role rather than
membership-in-registry. That keeps `FindGroundState` strict, keeps the category
axis intact, and keeps `AuditSpeciesRegistry`'s assertion true.

**Open owner question. Not resolved here.** It touches a validator and the
analysis eligibility contract, which is above this document's remit.

### (b) CONTRACT TRANSITION — a registry change rejects all existing raw

`ValidateRawInputs` pins `species_registry_sha256` and its siblings to
**compiled constants**. **Any registry change therefore makes the new analysis
reject every existing raw file**, including all of HF_PT2_INT.

**Two options, both owner decisions:**

| | cost | risk |
|---|---|---|
| **Versioned acceptance** — accept the old hash alongside the new, with a recorded rationale | cheap | a validator that accepts two contracts is a validator that can accept the wrong one; the rationale must be in-tree, not in a commit message |
| **Regenerate the 10 % campaign** at the new registry | **~56 CPU-h** | none to correctness; it is simply the honest option |

**This is the standing argument for implementing before full production.** Doing
it after means regenerating the full campaign (562.5 CPU-h) instead of the 10 %
one, a **10x** difference — or living with versioned acceptance permanently.

### (c) MECHANISM NOTE — the tune-dependence is NOT meson-vector parameters

**Verified 2026-08-09:** `StringFlav:mesonCvector` and `StringFlav:mesonBvector`
appear **nowhere in the tree** — not in any tune card, not in
`config/tune_difference_allowlist_v1.json`, and not in any of B5's measured
pairwise difference lists. **No arm sets either; all three inherit the PYTHIA
default.**

B5's measured MONASH ↔ CLOSEPACKING list (15 keys excluding `Random:seed`) is
`ClosePacking:*` (5), `ColourReconnection:*` (5),
`StringFragmentation:doStrangeJunctions`, `BeamRemnants:remnantMode`,
`MultipartonInteractions:pT0Ref`, `StringZ:useOldAExtra`. **No meson-vector
key, and no `StringFlav` key at all in that contrast.**

**So the excluded fraction's tune-dependence flows through the diquark/junction
parameters and the per-tune baryon fractions they produce — not through the
vector-to-pseudoscalar ratio.** The vector share of compensating beauty still
*differs* across tunes (65.2 % / 48.2 % / 47.8 %) — **but at a fixed
vector:pseudoscalar ratio, because the baryon fraction differs and mesons are
the remainder.** That is a consequence of the baryon side, not an independent
meson effect, and it should be stated that way or a reader will look for a
meson-vector parameter that does not exist.

**B_c completeness note.** B_c (`±541`) is **beauty-sector by registry**, carries
**both `q_c` and `q_b`**, and **legitimately enters both sector closures** — that
is a property of the state, not a bookkeeping choice, and a completeness table
must not treat its appearance in two sums as double-counting. Measured
2026-08-08: **95.6–97.7 % of B_c-containing events are beauty-hard**; **267 /
647 / 734 events per 10⁶** across MONASH / JUNCTIONS / CLOSEPACKING, a **~2.7x
tune spread that is itself an unexplained hadronisation effect.** Per-class B_c
is not viable in combined production, which is why **G2 declares it a
multiplicity-integrated / top-class-only observable**
(`RELEASE_BLOCKERS.md`, G2).

### (d) REGISTERED-FAMILY SCOPE — three more holes, and the B_c context

**Option B registers four families (`B*`, `D*`, `Σ_b*`, `Σ_c*`). Three
strange/charmed-beauty vectors sit outside it, each a Δφ feed-down hole for its
own ground state's associates:**

| state | PDG | hole | incremental pair-count cost |
|---|---|---|---|
| `D_s*` | ±433 | `D_s` associates | charm associates +2 → **+12 pairs** |
| `B_s*` | ±533 | `B_s` associates | beauty associates +2 → **+12 pairs** |
| `B_c*` | ±543 | `B_c` associates | beauty associates +2 → **+12 pairs** |

*Cost basis: pairs = `6 x N_charm + 6 x N_beauty`, verified exactly at
`6 x 24 + 6 x 26 = 300`. Adding all three takes Option B from 420 to **456
pairs** (1.52x baseline rather than 1.40x).*

**Owner question: include all three, some, or none?** They are cheap
individually and the holes are real but narrow — each affects only its own
ground state's associate spectrum.

**B_c context, measured 2026-08-08 (10 jobs/tune, 10⁶ events each):**

- **95.6–97.7 % of B_c-containing events are beauty-hard** (MONASH 97.38 %,
  JUNCTIONS 97.68 %, CLOSEPACKING 95.64 %) — shower `g -> cc̄` in a beauty event
  outweighs shower `g -> bb̄` in a charm event by ~30:1 to 40:1.
- **Rare: 267 / 647 / 734 events per 10⁶**, a ~2.7x spread across tunes that is
  itself an unexplained hadronisation effect.
- **Beauty-sector by registry**, carries both `q_c` and `q_b`, and **enters both
  sector closures legitimately** — that is a property of the state, not a
  bookkeeping choice.
- **Consequence for the shape decision:** a bb̄-only arm carries nearly all B_c
  statistics, and per-event-class B_c physics is identical under either
  production shape.

### (e) PARKED CARD TEXT — to land with the provenance break

**No card is edited until the registry change breaks provenance anyway.** Reason:
`effective_card_bytes` (`tools/campaign.py`) hashes raw card bytes without
stripping comments, so even a comment-only edit moves `effective_card_sha256`.

**Corrections to apply, all verified:**

1. **Per-tune `pT0Ref`.** All four cards carry an identical pasted sentence
   asserting 2.28 GeV. Correct for **MONASH** and **JUNCTIONS_MATCHED** (both
   inherit from `Tune:pp = 14`); **wrong for JUNCTIONS (2.15)** and
   **CLOSEPACKING (2.194)**. Each card should state its own value.
2. **Energy scaling.** Add: `pT0Ref` is defined at `ecmRef` and scales as
   `(sqrt(s)/ecmRef)^ecmPow`. **Verified from produced `effective_settings`:**
   `ecmPow = 0.215`, `ecmRef = 7000`, `eCM = 13600`, factor **1.153494**;
   effective screening scales **2.630 / 2.480 / 2.531**, margins over the 2.0
   threshold **0.630 / 0.480 / 0.531**.
3. **`Main:numberOfEvents`** is renderer-overridden in production
   (`effective_card_bytes` substitutes it) — annotate so the card value is not
   read as the production value.
4. **JUNCTIONS_MATCHED is not producible.** `TuneOrdinal`
   (`generation/producer/HeavyFlavourUtils.h:396-401`) throws for it, at
   `heavyflavourcorrelations_status.cpp:888`, inside the event loop — so it
   fails on the first successful event, not at startup.

**PROVENANCE-BREAK CHECKLIST — all four must move in the same change:**

- [ ] card comment corrections applied
- [ ] `effective_card_sha256` recomputed — **it moves**
- [ ] rendered production submit rows updated (`tools/render_production_submit.py:230,243`)
- [ ] the `effective_card_sha256` field in `tools/statistical_robustness.py:567`
- [ ] the recorded per-tune comparison at `tools/evaluate_pthat_sensitivity.py:419`
      (`sha256(card)` vs `campaign["card_sha256"][tune]`)
- [ ] `upstream_executable_sha256` moves off `e54b27bb9e3f…` — **state plainly**,
      it breaks comparability with HF_PT2_INT

---

## 8. Open questions for the owner

1. **Option B confirmed?** It is my recommendation and it matches the review's
   instinct, but it forecloses per-species Δφ for 148 states.
2. **`upstream_executable_sha256` moving off `e54b27bb…`** breaks comparability
   with HF_PT2_INT. Accept, or carry both?
3. **The species-axis width** on `hFlavourClosure` is the one place B could cost
   more than projected. Worth a bin-count estimate before committing.
4. **B13 and the five literals** now sit in front of this: the pair count is
   changing from 300 to 420, so the literals break as a certainty rather than a
   hypothesis.
